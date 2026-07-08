# Day18 — MCP Tool 桥接到 Agent Registry
# Day19 — Filesystem 自然语言路由 + read_file / list_directory 显式调用
#
# 功能：将 MCP Server 暴露的工具动态注册为 mcp_* 内置工具
# 逻辑：register_mcp_tools → registry.register

from typing import Any

import re

from app.agent.tools.registry import get, list_names, register
from app.core.logger import logger
from app.mcp.client import MCPClient, format_mcp_summary
from app.mcp.runtime import run_on_background

_client: MCPClient | None = None
_registered = False


def _run_async(coro):
    return run_on_background(coro)

# @brief: 获取 MCP Client
# @return: MCP Client
def get_mcp_client() -> MCPClient | None:
    return _client

# @brief: 检查 MCP 是否启用
# @return: 是否启用
def is_mcp_enabled() -> bool:
    return _client is not None and _client.connected


# @brief: 创建同步 run 函数，供 registry 调用 MCP Tool
def _make_mcp_runner(client: MCPClient, tool_name: str):
    def run(**kwargs) -> dict:
        try:
            result = _run_async(client.call_tool(tool_name, kwargs))
            summary = format_mcp_summary(result)
            return {
                "ok": not result.get("isError", False),
                "data": result,
                "summary": summary,
                "sources": [],
            }
        except Exception as exc:
            logger.error("mcp tool failed  name=%s  error=%s", tool_name, exc)
            return {
                "ok": False,
                "data": {},
                "summary": f"MCP 工具 {tool_name} 调用失败: {exc}",
                "sources": [],
            }

    return run

# @brief: 将 MCP Tool 转换为 Tool Registry 可用的 schema
# @param: tool: MCP Tool
# @param: registry_name: 工具注册名称
# @return: schema
def _tool_schema(tool: Any, registry_name: str) -> dict:
    input_schema = tool.inputSchema
    if hasattr(input_schema, "model_dump"):
        parameters = input_schema.model_dump()
    elif isinstance(input_schema, dict):
        parameters = input_schema
    else:
        parameters = {"type": "object", "properties": {}}
    return {
        "type": "function",
        "function": {
            "name": registry_name,
            "description": tool.description or f"MCP tool: {tool.name}",
            "parameters": parameters,
        },
    }

# @brief: 将 MCP Server 工具注册进 Tool Registry
# @param: client: MCP Client
# @return: 注册的工具数量
async def register_mcp_tools(client: MCPClient) -> int:
    global _client, _registered
    _client = client
    tools = await client.list_tools()
    count = 0
    for tool in tools:
        registry_name = f"mcp_{tool.name}"
        if registry_name in list_names():
            logger.info("mcp tool skip  name=%s (already registered)", registry_name)
            continue
        register(
            {
                "name": registry_name,
                "description": tool.description or f"MCP tool: {tool.name}",
                "schema": _tool_schema(tool, registry_name),
                "run": _make_mcp_runner(client, tool.name),
            }
        )
        count += 1
        logger.info("mcp tool registered  name=%s", registry_name)
    _registered = count > 0
    return count

# @brief: 列出所有 MCP Tool 名称
# @return: MCP Tool 名称列表
def list_mcp_tool_names() -> list[str]:
    return [name for name in list_names() if name.startswith("mcp_")]

# @brief: 文件读取关键词
# @return: 文件读取关键词列表
FILE_READ_KEYWORDS = ("看看", "查看", "读取", "打开", "读一下", "写了什么", "内容是什么")
# @brief: 文件列表关键词
# @return: 文件列表关键词列表
FILE_LIST_KEYWORDS = ("列出", "目录", "有哪些", "列表", "文件列表")
# @brief: 文件路径模式
# @return: 文件路径模式
FILE_PATH_PATTERN = re.compile(
    r"([\w./\\-]+\.(?:md|txt|py|json|yml|yaml|toml))",
    re.I,
)

# @brief: 提取文件路径
# @param: message: 用户消息
# @return: 文件路径
def _extract_file_path(message: str) -> str | None:
    match = FILE_PATH_PATTERN.search(message)
    if match:
        return match.group(1).replace("\\", "/")
    if re.search(r"readme", message, re.I):
        return "README.md"
    return None

# @brief: 检查是否为文件列表意图
# @param: message: 用户消息
# @return: 是否为文件列表意图
def _is_list_directory_intent(message: str) -> bool:
    return any(keyword in message for keyword in FILE_LIST_KEYWORDS)

# @brief: 提取目录路径
# @param: message: 用户消息
# @return: 目录路径
def _extract_directory_path(message: str) -> str | None:
    lower = message.lower()
    if "docs" in lower and _is_list_directory_intent(message):
        return "docs"
    match = re.search(r"([\w./-]+)/?\s*(?:目录|文件夹)", message)
    if match:
        return match.group(1).replace("\\", "/").rstrip("/")
    return None

# @brief: 检查是否为文件系统意图
# @param: user_message: 用户消息
# @return: 是否为文件系统意图
def match_filesystem_intent(user_message: str) -> bool:
    """检测文件/目录语义（不依赖 MCP 是否在线）。"""
    if _extract_pdf_path(user_message):
        return False
    if _is_list_directory_intent(user_message) and _extract_directory_path(user_message):
        return True
    path = _extract_file_path(user_message)
    has_read_intent = path is not None or any(
        keyword in user_message for keyword in FILE_READ_KEYWORDS
    )
    if has_read_intent and re.search(r"readme|\.md|\.txt|\.py|文件", user_message, re.I):
        return True
    return False

# @brief: 检查是否为 MCP 显式意图
# @param: user_message: 用户消息
# @return: 是否为 MCP 显式意图
def match_mcp_explicit_intent(user_message: str) -> bool:
    """检测显式 mcp 命令（不依赖 MCP 是否在线）。"""
    return bool(re.search(r"mcp\s+[\w-]+", user_message.strip(), re.I))

# @brief: 计划文件系统步骤
# @param: user_message: 用户消息
# @return: 文件系统步骤
def plan_filesystem_step(user_message: str) -> dict | None:
    """自然语言文件/目录意图 → Filesystem MCP 工具。"""
    if not match_filesystem_intent(user_message):
        return None
    if not is_mcp_enabled():
        return None

    tools = set(list_mcp_tool_names())
    if "mcp_read_file" not in tools and "mcp_list_directory" not in tools:
        return None

    if _is_list_directory_intent(user_message) and "mcp_list_directory" in tools:
        dir_path = _extract_directory_path(user_message)
        if dir_path:
            return {
                "tool": "mcp_list_directory",
                "args": {"path": dir_path},
                "reason": f"列出目录 {dir_path}",
            }

    path = _extract_file_path(user_message)
    has_read_intent = path is not None or any(
        keyword in user_message for keyword in FILE_READ_KEYWORDS
    )
    if has_read_intent and re.search(r"readme|\.md|\.txt|\.py|文件", user_message, re.I):
        if not path and re.search(r"readme", user_message, re.I):
            path = "README.md"
        if path and "mcp_read_file" in tools:
            return {
                "tool": "mcp_read_file",
                "args": {"path": path},
                "reason": f"读取文件 {path}",
            }

    return None

# @brief: 提取 PDF 路径
# @param: message: 用户消息
# @return: PDF 路径
def _extract_pdf_path(message: str) -> str | None:
    match = re.search(r"([\w\-.]+\.pdf)", message, re.I)
    return match.group(1) if match else None

# @brief: 解析用户消息中的 MCP 显式调用，如「mcp read_file README.md」
# @param: user_message: 用户消息
# @return: MCP 步骤
def plan_mcp_step(user_message: str) -> dict | None:
    if "mcp" not in user_message.lower():
        return None
    mcp_tools = list_mcp_tool_names()
    if not mcp_tools:
        return None

    match = re.search(r"mcp\s+([\w-]+)(?:\s+(.*))?$", user_message.strip(), re.I)
    if not match:
        return None

    sub = match.group(1).lower().replace("-", "_")
    rest = (match.group(2) or "").strip()
    registry_name = f"mcp_{sub}"
    if registry_name not in mcp_tools:
        registry_name = f"mcp_{match.group(1)}"
    if registry_name not in mcp_tools:
        return None

    spec = get(registry_name)
    schema = spec["schema"]["function"]["parameters"]
    properties = schema.get("properties") or {}
    required = schema.get("required") or []

    args: dict = {}
    if "path" in properties and rest:
        args["path"] = rest
    elif "path" in required:
        args["path"] = rest or "README.md"
    elif required:
        key = required[0]
        if key in properties:
            args[key] = rest or "hello"
    elif rest:
        first_key = next(iter(properties), "message")
        args[first_key] = rest
    elif "message" in properties:
        args["message"] = "hello"

    return {
        "tool": registry_name,
        "args": args,
        "reason": f"调用 MCP 工具 {registry_name}",
    }
