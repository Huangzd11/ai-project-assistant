# Day15 — Agent 执行器
#
# 功能：执行 Planner 计划，调用 Tool，根据 Observation 生成最终回答
# 逻辑：plan → TOOL_HANDLERS → format observation → llm.chat → AgentResult

import time

from app.agent.planner import plan
from app.agent.tools import TOOL_HANDLERS
from app.core.config import AGENT_ANSWER_PROMPT
from app.core.llm import chat
from app.core.logger import logger

# @brief: 格式化时间
# @param: seconds: 时间（秒）
# @return: 格式化后的时间
def _format_duration(seconds: float) -> str:
    if seconds >= 1:
        return f"{seconds:.1f}s"
    return f"{seconds * 1000:.0f}ms"


# @brief: 将工具返回格式化为 LLM 可读的 Observation 文本
# @param: user_message: 用户原始消息
# @param: results: 各工具返回结果列表
# @return: 拼接后的 prompt 文本
def _format_observation(user_message: str, results: list[dict]) -> str:
    parts = [f"用户原始问题：{user_message}", ""]
    for index, result in enumerate(results, start=1):
        parts.append(f"[工具结果{index}]")
        parts.append(f"answer: {result.get('answer', '')}")
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
        handler = TOOL_HANDLERS[tool_name]
        result = handler(**step["args"])
        observations.append({"tool": tool_name, "result": result})
        results.append(result)

    prompt = _format_observation(user_message, results)
    answer = chat(prompt, system_prompt=AGENT_ANSWER_PROMPT)
    sources = results[-1].get("sources", []) if results else []

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
