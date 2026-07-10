# Day15 — Agent HTTP 接口
# Day17 — 支持 session_id 多轮记忆
# Day21_2 — POST /agent/stream SSE 流式输出
# Day25 — 返回 usage
#
# 功能：暴露 POST /agent 端点
# 逻辑：接收用户目标 → run_agent() → 返回答案、计划与来源

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agent.executor import format_sse_event, run_agent, run_agent_stream
from app.core.logger import logger
from app.models import (
    AgentPlanStep,
    AgentRequest,
    AgentResponse,
    AgentWorkflowInfo,
    RagSource,
    UsageInfo,
)

router = APIRouter(tags=["agent"])


@router.post(
    "/agent",
    response_model=AgentResponse,
    summary="Agent 问答",
    description=(
        "企业 Agent：Planner 分解任务 → 调用工具 → 根据 Observation 生成回答。"
        "传入 session_id 可启用 Short Memory 多轮对话；相同 session_id 共享上下文。"
        "响应含 usage（prompt/completion/total tokens 与 cost_usd）。"
    ),
)
def agent_endpoint(req: AgentRequest):
    logger.info("agent request  message=%s  session_id=%s", req.message, req.session_id)
    result = run_agent(req.message, session_id=req.session_id)
    workflow = result.get("workflow")
    usage = UsageInfo(**result["usage"]) if result.get("usage") else None
    return AgentResponse(
        message=result["message"],
        answer=result["answer"],
        session_id=result.get("session_id"),
        workflow=AgentWorkflowInfo(**workflow) if workflow else None,
        plan=[AgentPlanStep(**step) for step in result["plan"]],
        tool_calls=result["tool_calls"],
        sources=[RagSource(**item) for item in result["sources"]],
        usage=usage,
    )


@router.post(
    "/agent/stream",
    summary="Agent 流式问答（SSE）",
    description=(
        "与 POST /agent 相同逻辑，但通过 Server-Sent Events 逐字返回 LLM 输出。"
        "事件类型：workflow → plan → tool_calls → token → usage → done。"
    ),
)
def agent_stream_endpoint(req: AgentRequest):
    logger.info("agent stream  message=%s  session_id=%s", req.message, req.session_id)

    def event_generator():
        try:
            for event in run_agent_stream(req.message, session_id=req.session_id):
                yield format_sse_event(event)
        except Exception as exc:
            logger.exception("event=agent_stream_error  error=%s", exc)
            yield format_sse_event({"type": "error", "detail": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
