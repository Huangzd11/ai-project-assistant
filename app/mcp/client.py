# Day18 — MCP Client 封装
#
# 功能：通过 stdio 连接 MCP Server，列出并调用外部 Tool
# 逻辑：connect → list_tools / call_tool → close

from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.core.logger import logger

# @brief: MCP Client，使用 stdio 与独立 Server 进程通信。
class MCPClient:

    # @brief: 初始化 MCP Client
    # @param: command: 命令
    # @param: args: 参数
    def __init__(self, command: str, args: list[str]):
        self._params = StdioServerParameters(command=command, args=args)
        self._session: ClientSession | None = None
        self._stdio_ctx = None

    # @brief: 检查 MCP Client 是否连接
    # @return: 是否连接
    @property
    def connected(self) -> bool:
        return self._session is not None

    # @brief: 连接 MCP Server
    # @return: None
    async def connect(self) -> None:
        if self.connected:
            return
        self._stdio_ctx = stdio_client(self._params)
        read, write = await self._stdio_ctx.__aenter__()
        self._session = ClientSession(read, write)
        await self._session.__aenter__()
        await self._session.initialize()

    # @brief: 列出 MCP Server 提供的工具
    # @return: 工具列表
    async def list_tools(self) -> list[Any]:
        if not self._session:
            raise RuntimeError("MCP Client 未连接，请先调用 connect()")
        result = await self._session.list_tools()
        return list(result.tools)

    # @brief: 调用 MCP Server 提供的工具
    # @param: name: 工具名称
    # @param: arguments: 工具参数
    # @return: 工具调用结果
    async def call_tool(self, name: str, arguments: dict) -> dict:
        if not self._session:
            raise RuntimeError("MCP Client 未连接，请先调用 connect()")
        result = await self._session.call_tool(name, arguments)
        content = []
        for item in result.content:
            if hasattr(item, "model_dump"):
                content.append(item.model_dump())
            else:
                content.append({"type": getattr(item, "type", "text"), "text": str(item)})
        return {
            "tool": name,
            "arguments": arguments,
            "isError": bool(getattr(result, "isError", False)),
            "content": content,
        }

    # @brief: 关闭 MCP Client
    # @return: None
    async def close(self) -> None:
        if self._session:
            try:
                await self._session.__aexit__(None, None, None)
            except (RuntimeError, Exception) as exc:
                logger.warning("mcp session close skipped  error=%s", exc)
            finally:
                self._session = None
        if self._stdio_ctx:
            try:
                await self._stdio_ctx.__aexit__(None, None, None)
            except (RuntimeError, Exception) as exc:
                logger.warning("mcp stdio close skipped  error=%s", exc)
            finally:
                self._stdio_ctx = None

# @brief: 将 MCP 返回转为 LLM 可读的 summary 文本
# @param: result: MCP 返回结果
# @return: summary 文本
def format_mcp_summary(result: dict) -> str:
    """将 MCP 返回转为 LLM 可读的 summary 文本。"""
    if result.get("isError"):
        return f"MCP 工具执行失败: {result.get('content')}"
    parts: list[str] = []
    for item in result.get("content") or []:
        if isinstance(item, dict) and item.get("text"):
            parts.append(str(item["text"]))
        else:
            parts.append(str(item))
    return "\n".join(parts) if parts else str(result)
