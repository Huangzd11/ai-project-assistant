# Day15 — Agent 工具定义
#
# 功能：封装 RAG 为 Agent 可调用的 Tool
# 逻辑：rag_query → rag_answer，并提供 OpenAI Function Calling schema

from app.rag.rag_pipeline import rag_answer

# @brief: rag_query 的 OpenAI Function Calling schema
RAG_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "rag_query",
        "description": "在企业知识库检索并回答，返回 answer 与 sources",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "检索问题"},
            },
            "required": ["question"],
        },
    },
}

# @brief: 企业知识库检索并回答
# @param: question: 检索问题
# @return: 检索结果
def rag_query(question: str) -> dict:
    return rag_answer(question)

# @brief: 工具名 → 处理函数映射（Day16 演进为注册表）
TOOL_HANDLERS = {
    "rag_query": rag_query,
}