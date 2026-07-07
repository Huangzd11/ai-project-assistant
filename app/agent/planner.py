# Day15 — Agent 任务规划
#
# 功能：将用户目标分解为可执行的工具调用计划
# 逻辑：规则 + 关键词判断是否需要 rag_query（Day15 轻量 Planner）

import re

RAG_KEYWORDS = ("pdf", "总结", "文档", "知识库", "资料", "根据")


# @brief: 判断是否需要走知识库检索
# @param: message: 用户消息
# @return: 是否需要 RAG
def _needs_rag(message: str) -> bool:
    lower = message.lower()
    return any(keyword in lower for keyword in RAG_KEYWORDS)


# @brief: 从用户消息构造 RAG 检索问题
# @param: message: 用户消息
# @return: 检索问题文本
def _build_rag_question(message: str) -> str:
    match = re.search(r"([\w\-.]+\.pdf)", message, re.I)
    if match:
        return f"{match.group(1)} 的主要内容是什么？"
    return message


# @brief: 规划执行步骤
# @param: user_message: 用户目标
# @return: 计划步骤列表，每步含 tool / args / reason
def plan(user_message: str) -> list[dict]:
    if not _needs_rag(user_message):
        return []
    return [
        {
            "tool": "rag_query",
            "args": {"question": _build_rag_question(user_message)},
            "reason": "需要从知识库获取文档内容",
        }
    ]
