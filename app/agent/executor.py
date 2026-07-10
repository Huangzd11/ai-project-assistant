# Day15 — Agent 执行器
# Day16 — Tool Registry
# Day17 — 接入 Short / Long Memory
# Day20 — Workflow 元数据
# Day21_2 — SSE 流式 run_agent_stream
# Day25 — 聚合 LLM usage 写入响应
#
# 功能：执行 Workflow 计划，调用 Tool，根据 Observation 与历史生成回答
# 逻辑：memory → build_workflow → registry.run → chat_messages → 写回 memory

import json
import time
from collections.abc import Iterator
from typing import Any

import app.agent.tools  # noqa: F401 — bootstrap 工具注册
from app.agent.memory import (
    build_system_with_facts,
    get_memory,
    maybe_extract_facts,
)
from app.agent.tools.registry import run as run_tool
from app.agent.workflow import build_workflow, workflow_to_dict
from app.core.config import AGENT_ANSWER_PROMPT, SYSTEM_PROMPT
from app.core.llm import chat_messages, chat_messages_stream
from app.core.logger import logger
from app.core.token_meter import UsageInfo


# @brief: 格式化持续时间
def _format_duration(seconds: float) -> str:
    if seconds >= 1:
        return f"{seconds:.1f}s"
    return f"{seconds * 1000:.0f}ms"


# @brief: 格式化工具结果
def _format_tool_result(result: dict) -> str:
    if result.get("summary"):
        return str(result["summary"])
    return str(result.get("data", result))


# @brief: 收集来源
def _collect_sources(results: list[dict]) -> list[dict]:
    merged: list[dict] = []
    seen: set[tuple] = set()
    for result in results:
        for item in result.get("sources") or []:
            key = (item.get("source"), item.get("page"))
            if key not in seen:
                seen.add(key)
                merged.append(item)
    return merged


# @brief: 格式化观察
def _format_observation(user_message: str, results: list[dict]) -> str:
    parts = [f"用户原始问题：{user_message}", ""]
    for index, result in enumerate(results, start=1):
        parts.append(f"[工具结果{index}]")
        parts.append(_format_tool_result(result))
        sources = result.get("sources") or []
        if sources:
            cites = ", ".join(f"{s['source']} p{s['page']}" for s in sources)
            parts.append(f"sources: {cites}")
        parts.append("")
    return "\n".join(parts).strip()


# @brief: 执行工具步骤
def _run_steps(steps: list[dict]) -> tuple[list[dict], list[dict]]:
    observations: list[dict] = []
    results: list[dict] = []
    for step in steps:
        tool_name = step["tool"]
        logger.info("agent tool  name=%s  args=%s", tool_name, step.get("args"))
        try:
            result = run_tool(tool_name, **step["args"])
        except KeyError:
            logger.error("agent tool not found  name=%s", tool_name)
            result = {
                "ok": False,
                "data": {},
                "summary": f"未知工具: {tool_name}",
                "sources": [],
            }
        observations.append({"tool": tool_name, "result": result})
        results.append(result)
    return observations, results


# @brief: 准备 Agent 运行上下文
def _prepare_run(
    user_message: str,
    session_id: str | None,
) -> dict[str, Any]:
    memory = get_memory(session_id) if session_id else None
    history = memory.get_messages() if memory else []
    facts = memory.get_facts() if memory else []

    if memory:
        logger.info(
            "agent memory  session=%s  history=%d  facts=%d",
            memory.session_id,
            len(history),
            len(facts),
        )

    decision = build_workflow(user_message)
    steps = decision.steps
    workflow = workflow_to_dict(decision)
    logger.info(
        "agent workflow  intent=%s  need_tool=%s  tools=%s",
        decision.intent.value,
        decision.need_tool,
        [step["tool"] for step in steps],
    )

    chat_system = build_system_with_facts(SYSTEM_PROMPT, facts)
    agent_system = build_system_with_facts(AGENT_ANSWER_PROMPT, facts)

    observations: list[dict] = []
    results: list[dict] = []
    sources: list[dict] = []

    if steps:
        observations, results = _run_steps(steps)
        user_content = _format_observation(user_message, results)
        system_prompt = agent_system
        sources = _collect_sources(results)
    else:
        user_content = user_message
        system_prompt = chat_system

    llm_messages = [*history, {"role": "user", "content": user_content}]

    return {
        "memory": memory,
        "workflow": workflow,
        "steps": steps,
        "observations": observations,
        "sources": sources,
        "llm_messages": llm_messages,
        "system_prompt": system_prompt,
    }


def _usage_dict(usage: UsageInfo | None) -> dict | None:
    return usage.to_dict() if usage else None


# @brief: 构建响应
def _build_response(
    user_message: str,
    answer: str,
    workflow: dict,
    steps: list[dict],
    observations: list[dict],
    sources: list[dict],
    session_id: str | None,
    memory_session_id: str | None,
    usage: UsageInfo | None = None,
) -> dict:
    return {
        "message": user_message,
        "answer": answer,
        "session_id": memory_session_id if memory_session_id else session_id,
        "workflow": workflow,
        "plan": steps,
        "tool_calls": [{"tool": item["tool"]} for item in observations],
        "sources": sources,
        "usage": _usage_dict(usage),
    }


# @brief: Agent 门面，Workflow → 执行工具 → 总结回答（支持 session 记忆）
def run_agent(user_message: str, session_id: str | None = None) -> dict:
    start = time.perf_counter()
    ctx = _prepare_run(user_message, session_id)
    memory = ctx["memory"]

    result = chat_messages(ctx["llm_messages"], system_prompt=ctx["system_prompt"])
    answer = result.content
    logger.info("agent done  duration=%s", _format_duration(time.perf_counter() - start))

    if memory:
        maybe_extract_facts(memory, user_message)
        memory.append("user", user_message)
        memory.append("assistant", answer)

    mem_sid = memory.session_id if memory else None
    return _build_response(
        user_message,
        answer,
        ctx["workflow"],
        ctx["steps"],
        ctx["observations"],
        ctx["sources"],
        session_id,
        mem_sid,
        usage=result.usage,
    )


# @brief: 格式化为 SSE data 行
def format_sse_event(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


# @brief: Agent 流式执行，yield SSE 事件 dict
def run_agent_stream(user_message: str, session_id: str | None = None) -> Iterator[dict]:
    start = time.perf_counter()
    ctx = _prepare_run(user_message, session_id)
    memory = ctx["memory"]

    yield {"type": "workflow", "workflow": ctx["workflow"]}
    yield {"type": "plan", "plan": ctx["steps"]}

    if ctx["observations"]:
        yield {
            "type": "tool_calls",
            "tool_calls": [{"tool": item["tool"]} for item in ctx["observations"]],
        }

    answer_parts: list[str] = []
    usage: UsageInfo | None = None
    for item in chat_messages_stream(ctx["llm_messages"], system_prompt=ctx["system_prompt"]):
        if isinstance(item, UsageInfo) or item is None:
            usage = item
            continue
        answer_parts.append(item)
        yield {"type": "token", "content": item}

    answer = "".join(answer_parts)
    logger.info("agent stream done  duration=%s", _format_duration(time.perf_counter() - start))

    if memory:
        maybe_extract_facts(memory, user_message)
        memory.append("user", user_message)
        memory.append("assistant", answer)

    usage_payload = _usage_dict(usage)
    if usage_payload:
        yield {"type": "usage", "usage": usage_payload}

    mem_sid = memory.session_id if memory else None
    yield {
        "type": "done",
        "message": user_message,
        "answer": answer,
        "session_id": mem_sid if mem_sid else session_id,
        "workflow": ctx["workflow"],
        "plan": ctx["steps"],
        "tool_calls": [{"tool": item["tool"]} for item in ctx["observations"]],
        "sources": ctx["sources"],
        "usage": usage_payload,
    }
