# Day18 — MCP 调试接口
#
# 功能：查看 MCP 连接状态与已注册工具

from fastapi import APIRouter

from app.agent.tools.registry import get, list_names
from app.mcp.bridge import is_mcp_enabled, list_mcp_tool_names

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("/status")
def mcp_status():
    names = list_mcp_tool_names()
    return {
        "enabled": is_mcp_enabled(),
        "tool_count": len(names),
        "tools": [
            {
                "name": name,
                "description": get(name)["description"],
            }
            for name in names
        ],
    }


@router.get("/tools")
def mcp_tools():
    return {"tools": mcp_status()["tools"], "all_registry_mcp": list_mcp_tool_names()}
