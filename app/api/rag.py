# Day13 — RAG 知识库问答接口
#
# 功能：暴露 POST /rag 端点
# 逻辑：接收问题 → rag_answer() → 返回答案与来源

from fastapi import APIRouter

from app.models import RagRequest, RagResponse, RagSource
from app.rag.rag_pipeline import rag_answer

router = APIRouter(tags=["rag"])


# @brief: 知识库 RAG 问答
# @param: req: RagRequest（question 字段）
# @return: RagResponse（answer + sources）
@router.post("/rag", response_model=RagResponse)
def rag_endpoint(req: RagRequest):
    result = rag_answer(req.question)
    return RagResponse(
        question=result["question"],
        answer=result["answer"],
        sources=[RagSource(**s) for s in result["sources"]],
    )
