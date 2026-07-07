# Day18 — MCP Tool 桥接到 Agent Registry
#
# 功能：将 MCP Server 暴露的工具动态注册为 mcp_* 内置工具
# 逻辑：register_mcp_tools → registry.register

from typing import Any

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


# @brief: 解析用户消息中的 MCP 显式调用，如「mcp echo hello」
def plan_mcp_step(user_message: str) -> dict | None:
    import re

    if "mcp" not in user_message.lower():
        return None
    mcp_tools = list_mcp_tool_names()
    if not mcp_tools:
        return None

    match = re.search(r"mcp\s+(\w+)(?:\s+(.*))?$", user_message.strip(), re.I)
    if not match:
        return None

    sub = match.group(1).lower()
    rest = (match.group(2) or "").strip()
    registry_name = f"mcp_{sub}"
    if registry_name not in mcp_tools:
        return None

    spec = get(registry_name)
    schema = spec["schema"]["function"]["parameters"]
    properties = schema.get("properties") or {}
    required = schema.get("required") or []

    args: dict = {}
    if required:
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
