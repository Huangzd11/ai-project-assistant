# Day15 — Agent 执行器
# Day16 — 改用 Tool Registry，统一 Observation 格式
#
# 功能：执行 Planner 计划，调用 Tool，根据 Observation 生成最终回答
# 逻辑：plan → registry.run → format observation → llm.chat → AgentResult

import time

import app.agent.tools  # noqa: F401 — bootstrap 工具注册
from app.agent.planner import plan
from app.agent.tools.registry import run as run_tool
from app.core.config import AGENT_ANSWER_PROMPT
from app.core.llm import chat
from app.core.logger import logger


# @brief: 格式化耗时
# @param: seconds: 秒
# @return: 人类可读耗时
def _format_duration(seconds: float) -> str:
    if seconds >= 1:
        return f"{seconds:.1f}s"
    return f"{seconds * 1000:.0f}ms"


# @brief: 将单条工具结果格式化为文本
# @param: result: 工具 Observation
# @return: 文本摘要
def _format_tool_result(result: dict) -> str:
    if result.get("summary"):
        return str(result["summary"])
    return str(result.get("data", result))


# @brief: 从多条工具结果聚合 sources
# @param: results: 工具 Observation 列表
# @return: 去重后的 sources
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


# @brief: 将工具返回格式化为 LLM 可读的 Observation 文本
# @param: user_message: 用户原始消息
# @param: results: 各工具返回结果列表
# @return: 拼接后的 prompt 文本
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


# @brief: Agent 门面，规划 → 执行工具 → 总结回答
# @param: user_message: 用户目标
# @return: { message, answer, plan, tool_calls, sources }
def run_agent(user_message: str) -> dict:
    start = time.perf_counter()
    steps = plan(user_message)
    logger.info(
        "agent plan  steps=%d  tools=%s",
        len(steps),
        [step["tool"] for step in steps],
    )

    if not steps:
        answer = chat(user_message)
        logger.info("agent direct  duration=%s", _format_duration(time.perf_counter() - start))
        return {
            "message": user_message,
            "answer": answer,
            "plan": [],
            "tool_calls": [],
            "sources": [],
        }

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

    prompt = _format_observation(user_message, results)
    answer = chat(prompt, system_prompt=AGENT_ANSWER_PROMPT)
    sources = _collect_sources(results)

    logger.info(
        "agent done  duration=%s  sources=%d",
        _format_duration(time.perf_counter() - start),
        len(sources),
    )
    return {
        "message": user_message,
        "answer": answer,
        "plan": steps,
        "tool_calls": [{"tool": item["tool"]} for item in observations],
        "sources": sources,
    }
