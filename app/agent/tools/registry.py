# Day16 — Agent 工具注册表
#
# 功能：统一注册、查找、执行 Agent 工具
# 逻辑：register → get → run，Executor 只依赖本模块

from typing import Callable, TypedDict


class ToolSpec(TypedDict):
    name: str
    description: str
    schema: dict
    run: Callable[..., dict]


_TOOLS: dict[str, ToolSpec] = {}


# @brief: 注册工具
# @param: tool: 工具规格（name / description / schema / run）
# @return: None
def register(tool: ToolSpec) -> None:
    if tool["name"] in _TOOLS:
        raise ValueError(f"Tool {tool['name']} already registered")
    _TOOLS[tool["name"]] = tool


# @brief: 获取工具规格
# @param: name: 工具名
# @return: ToolSpec
def get(name: str) -> ToolSpec:
    if name not in _TOOLS:
        raise KeyError(f"Tool {name} not found")
    return _TOOLS[name]


# @brief: 运行工具
# @param: name: 工具名
# @param: kwargs: 工具关键字参数
# @return: 统一 Observation 格式 dict
def run(name: str, **kwargs) -> dict:
    return get(name)["run"](**kwargs)


# @brief: 获取所有已注册工具名
# @return: 工具名列表
def list_names() -> list[str]:
    return list(_TOOLS.keys())


# @brief: 获取所有工具的 OpenAI Function Calling schema
# @return: schema 列表
def get_schemas() -> list[dict]:
    return [tool["schema"] for tool in _TOOLS.values()]
