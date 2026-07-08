# Day16 — Agent 任务规划
# Day20 — 委托 workflow 引擎
#
# 功能：将用户目标分解为可执行的工具调用计划
# 逻辑：plan() → build_workflow().steps

from app.agent.workflow import build_workflow


def plan(user_message: str) -> list[dict]:
    return build_workflow(user_message).steps
