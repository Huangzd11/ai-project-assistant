# Day18 — MCP 包入口与启动引导

import asyncio

from app.core.config import MCP_ENABLED, MCP_SERVER_ARGS, MCP_SERVER_COMMAND
from app.core.logger import logger
from app.mcp.bridge import get_mcp_client, register_mcp_tools
from app.mcp.client import MCPClient
from app.mcp.runtime import run_on_background, stop_background_loop

__all__ = ["bootstrap_mcp", "shutdown_mcp", "get_mcp_client"]


def _parse_args(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


async def _bootstrap_inner() -> int:
    command = MCP_SERVER_COMMAND
    args = _parse_args(MCP_SERVER_ARGS)
    client = MCPClient(command=command, args=args)
    try:
        await client.connect()
        count = await register_mcp_tools(client)
        logger.info("mcp bootstrap ok  tools=%d  command=%s %s", count, command, args)
        return count
    except Exception as exc:
        logger.error("mcp bootstrap failed  error=%s", exc)
        await client.close()
        return 0


async def bootstrap_mcp() -> int:
    """连接 MCP Server 并注册工具；MCP_ENABLED=false 时跳过。"""
    if not MCP_ENABLED:
        logger.info("mcp bootstrap skipped  MCP_ENABLED=false")
        return 0
    return await asyncio.to_thread(run_on_background, _bootstrap_inner())


async def shutdown_mcp() -> None:
    client = get_mcp_client()

    async def _close() -> None:
        if client and client.connected:
            await client.close()
            logger.info("mcp client closed")

    if client and client.connected:
        await asyncio.to_thread(run_on_background, _close())
    stop_background_loop()


def bootstrap_mcp_sync() -> int:
    """供脚本或测试使用的同步入口。"""
    if not MCP_ENABLED:
        return 0
    return run_on_background(_bootstrap_inner())
