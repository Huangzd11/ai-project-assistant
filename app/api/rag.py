# Day13 — RAG 知识库问答接口
# Day14 — 引用来源日志、Swagger 描述完善
#
# 功能：暴露 POST /rag 端点
# 逻辑：接收问题 → rag_answer() → 返回答案与来源

from fastapi import APIRouter

from app.core.logger import logger
from app.models import RagRequest, RagResponse, RagSource
from app.rag.rag_pipeline import rag_answer

router = APIRouter(tags=["rag"])


# @brief: 知识库 RAG 问答
# @param: req: RagRequest（question 字段）
# @return: RagResponse（answer + sources）
@router.post(
    "/rag",
    response_model=RagResponse,
    summary="知识库问答",
    description=(
        "企业知识库 RAG 问答：检索 Top-K 片段 → 拼接 Prompt → LLM 生成带引用的回答。"
        "响应始终包含 sources 数组；无命中时 sources 为空。"
        "前端展示格式建议：`{source}  Page {page}`。"
    ),
)
def rag_endpoint(req: RagRequest):
    logger.info("rag request  question=%s", req.question)
    result = rag_answer(req.question)
    sources = [RagSource(**s) for s in result["sources"]]
    return RagResponse(
        question=result["question"],
        answer=result["answer"],
        sources=sources,
    )
