# Day13 — RAG Pipeline（检索增强生成）
#
# 功能：Question → Search → Prompt → LLM → Answer + sources
# 逻辑：
#   format_context    — 检索结果 → Prompt 参考资料
#   build_rag_prompt  — 拼接 user prompt
#   extract_sources   — 提取去重来源
#   rag_answer        — 门面函数
#
# 详见 docs/Day13.md

from app.core.config import RAG_SYSTEM_PROMPT, SEARCH_TOP_K
from app.core.llm import chat
from app.rag.vector_store import search


# @brief: 将检索结果格式化为 LLM 可读的参考资料
# @param: chunks: search() 返回的 results 列表
# @return: 格式化后的参考文本
def format_context(chunks: list[dict]) -> str:
    parts = []
    for i, item in enumerate(chunks, start=1):
        parts.append(f"[参考{i}] 来源：{item['source']} 第{item['page']}页")
        parts.append(item["content"])
        parts.append("")
    return "\n".join(parts).strip()


# @brief: 组装 RAG user prompt（参考资料 + 用户问题）
# @param: question: 用户问题
# @param: chunks: 检索到的 chunk 列表
# @return: 完整 user 消息文本
def build_rag_prompt(question: str, chunks: list[dict]) -> str:
    context = format_context(chunks)
    return f"参考资料：\n{context}\n\n用户问题：{question}"


# @brief: 从检索结果提取去重来源（按 source+page，保留最高 score）
# @param: chunks: 检索结果列表
# @return: sources 列表
def extract_sources(chunks: list[dict]) -> list[dict]:
    best: dict[tuple, dict] = {}
    for item in chunks:
        key = (item["source"], item["page"])
        source_item = {
            "source": item["source"],
            "page": item["page"],
            "chunk": item["chunk"],
            "score": item["score"],
        }
        if key not in best or source_item["score"] > best[key]["score"]:
            best[key] = source_item
    return sorted(best.values(), key=lambda x: x["score"], reverse=True)


# @brief: RAG 问答门面，检索 → Prompt → LLM → 带来源的回答
# @param: question: 用户问题
# @param: top_k: 检索条数，默认 SEARCH_TOP_K
# @return: { question, answer, sources }
def rag_answer(question: str, top_k: int = SEARCH_TOP_K) -> dict:
    retrieval = search(question, top_k=top_k)
    chunks = retrieval["results"]

    if not chunks:
        return {
            "question": question,
            "answer": "知识库中未找到相关内容。",
            "sources": [],
        }

    prompt = build_rag_prompt(question, chunks)
    answer = chat(prompt, system_prompt=RAG_SYSTEM_PROMPT)
    return {
        "question": question,
        "answer": answer,
        "sources": extract_sources(chunks),
    }
