# Day15 — Agent HTTP 接口
# Day17 — 支持 session_id 多轮记忆
#
# 功能：暴露 POST /agent 端点
# 逻辑：接收用户目标 → run_agent() → 返回答案、计划与来源

from fastapi import APIRouter

from app.agent.executor import run_agent
from app.core.logger import logger
from app.models import AgentPlanStep, AgentRequest, AgentResponse, AgentWorkflowInfo, RagSource

router = APIRouter(tags=["agent"])


@router.post(
    "/agent",
    response_model=AgentResponse,
    summary="Agent 问答",
    description=(
        "企业 Agent：Planner 分解任务 → 调用工具 → 根据 Observation 生成回答。"
        "传入 session_id 可启用 Short Memory 多轮对话；相同 session_id 共享上下文。"
    ),
)
def agent_endpoint(req: AgentRequest):
    logger.info("agent request  message=%s  session_id=%s", req.message, req.session_id)
    result = run_agent(req.message, session_id=req.session_id)
    workflow = result.get("workflow")
    return AgentResponse(
        message=result["message"],
        answer=result["answer"],
        session_id=result.get("session_id"),
        workflow=AgentWorkflowInfo(**workflow) if workflow else None,
        plan=[AgentPlanStep(**step) for step in result["plan"]],
        tool_calls=result["tool_calls"],
        sources=[RagSource(**item) for item in result["sources"]],
    )
