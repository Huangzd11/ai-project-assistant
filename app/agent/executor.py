# Day15 — Agent 执行器
# Day16 — Tool Registry
# Day17 — 接入 Short / Long Memory
# Day20 — Workflow 元数据
#
# 功能：执行 Workflow 计划，调用 Tool，根据 Observation 与历史生成回答
# 逻辑：memory → build_workflow → registry.run → chat_messages → 写回 memory

import time

import app.agent.tools  # noqa: F401 — bootstrap 工具注册
from app.agent.memory import (
    build_system_with_facts,
    get_memory,
    maybe_extract_facts,
)
from app.agent.tools.registry import run as run_tool
from app.agent.workflow import build_workflow, workflow_to_dict
from app.core.config import AGENT_ANSWER_PROMPT, SYSTEM_PROMPT
from app.core.llm import chat_messages
from app.core.logger import logger


# @brief: 格式化持续时间
# @param: seconds: 持续时间
# @return: 格式化后的持续时间
def _format_duration(seconds: float) -> str:
    if seconds >= 1:
        return f"{seconds:.1f}s"
    return f"{seconds * 1000:.0f}ms"

# @brief: 格式化工具结果
# @param: result: 工具结果
# @return: 格式化后的工具结果
def _format_tool_result(result: dict) -> str:
    if result.get("summary"):
        return str(result["summary"])
    return str(result.get("data", result))

# @brief: 收集来源
# @param: results: 工具结果列表
# @return: 来源列表
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
# @param: user_message: 用户消息
# @param: results: 工具结果列表
# @return: 格式化后的观察
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

# @brief: 调用 LLM
# @param: history: 历史消息
# @param: user_content: 用户内容
# @param: system_prompt: 系统提示词
# @return: 回答
def _call_llm(
    history: list[dict],
    user_content: str,
    system_prompt: str,
) -> str:
    messages = [*history, {"role": "user", "content": user_content}]
    return chat_messages(messages, system_prompt=system_prompt)

# @brief: 构建响应
# @param: user_message: 用户消息
# @param: answer: 回答
# @param: workflow: 工作流
# @param: steps: 步骤
# @param: observations: 观察
# @param: sources: 来源
# @param: session_id: 会话 ID
# @param: memory_session_id: 记忆会话 ID
# @return: 响应
def _build_response(
    user_message: str,
    answer: str,
    workflow: dict,
    steps: list[dict],
    observations: list[dict],
    sources: list[dict],
    session_id: str | None,
    memory_session_id: str | None,
) -> dict:
    return {
        "message": user_message,
        "answer": answer,
        "session_id": memory_session_id if memory_session_id else session_id,
        "workflow": workflow,
        "plan": steps,
        "tool_calls": [{"tool": item["tool"]} for item in observations],
        "sources": sources,
    }


# @brief: Agent 门面，Workflow → 执行工具 → 总结回答（支持 session 记忆）
def run_agent(user_message: str, session_id: str | None = None) -> dict:
    start = time.perf_counter()
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

    if not steps:
        answer = _call_llm(history, user_message, chat_system)
        logger.info("agent direct  duration=%s", _format_duration(time.perf_counter() - start))
        observations: list[dict] = []
        sources: list[dict] = []
    else:
        observations = []
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

        prompt = _format_observation(user_message, results)
        answer = _call_llm(history, prompt, agent_system)
        sources = _collect_sources(results)
        logger.info(
            "agent done  duration=%s  sources=%d",
            _format_duration(time.perf_counter() - start),
            len(sources),
        )

    if memory:
        maybe_extract_facts(memory, user_message)
        memory.append("user", user_message)
        memory.append("assistant", answer)

    mem_sid = memory.session_id if memory else None
    return _build_response(
        user_message,
        answer,
        workflow,
        steps,
        observations,
        sources,
        session_id,
        mem_sid,
    )
