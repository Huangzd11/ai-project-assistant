# Day15 — Agent HTTP 接口
#
# 功能：暴露 POST /agent 端点
# 逻辑：接收用户目标 → run_agent() → 返回答案、计划与来源

from fastapi import APIRouter

from app.agent.executor import run_agent
from app.core.logger import logger
from app.models import AgentPlanStep, AgentRequest, AgentResponse, RagSource

router = APIRouter(tags=["agent"])


# @brief: Agent 问答（Planner + Tool + 总结）
# @param: req: AgentRequest（message 字段）
# @return: AgentResponse（answer + plan + sources）
@router.post(
    "/agent",
    response_model=AgentResponse,
    summary="Agent 问答",
    description=(
        "企业 Agent：Planner 分解任务 → 调用工具（如 rag_query）→ 根据 Observation 生成回答。"
        "响应包含可观测的 plan 与 sources；纯闲聊时 plan 为空。"
    ),
)
def agent_endpoint(req: AgentRequest):
    logger.info("agent request  message=%s", req.message)
    result = run_agent(req.message)
    return AgentResponse(
        message=result["message"],
        answer=result["answer"],
        plan=[AgentPlanStep(**step) for step in result["plan"]],
        tool_calls=result["tool_calls"],
        sources=[RagSource(**item) for item in result["sources"]],
    )
