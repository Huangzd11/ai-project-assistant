# Day16 — RAG 工具
#
# 功能：封装 rag_answer 为 Agent 可调用的 rag_query 工具
# 逻辑：run → rag_answer → 统一 Observation 格式


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


# @brief: 运行 RAG 工具
# @param: question: 检索问题
# @return: Observation（ok / data / summary / sources）
def run(question: str) -> dict:
    from app.rag.rag_pipeline import rag_answer

    result = rag_answer(question)
    return {
        "ok": True,
        "data": result,
        "summary": result["answer"],
        "sources": result.get("sources", []),
    }


SPEC = {
    "name": "rag_query",
    "description": "在企业知识库检索并回答，返回 answer 与 sources",
    "schema": RAG_TOOL_SCHEMA,
    "run": run,
}
