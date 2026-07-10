# Day04 — HTTP 聊天接口
# Day14 — Swagger 描述完善
# Day25 — 返回 usage
#
# 功能：暴露 /chat 与 /models 两个端点
# 逻辑：
#   1. 接收 Pydantic 校验后的 ChatRequest
#   2. 调用 core.llm.chat() 获取模型回答
#   3. 封装为 ChatResponse 返回
#   /models 返回当前环境变量中的模型配置信息

from fastapi import APIRouter

from app.core.config import MODEL_NAME, OPENAI_BASE_URL, PROVIDER
from app.core.llm import chat
from app.models import ChatRequest, ChatResponse, ModelInfo, UsageInfo

router = APIRouter(tags=["chat"])


# @brief: 返回当前 LLM 提供方、模型名、API 地址
# @return: ModelInfo
@router.get("/models", response_model=ModelInfo, summary="查询模型配置")
def models():
    return ModelInfo(
        provider=PROVIDER,
        model=MODEL_NAME,
        base_url=OPENAI_BASE_URL,
    )


# @brief: 单轮对话，用户 message → LLM → answer
# @param: req: ChatRequest（message 字段）
# @return: ChatResponse
@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="AI 聊天",
    description="纯 LLM 单轮对话，不走知识库检索。需要 Ollama 或云端 API 可用。",
)
def chat_endpoint(req: ChatRequest):
    result = chat(req.message)
    usage = UsageInfo(**result.usage.to_dict()) if result.usage else None
    return ChatResponse(answer=result.content, usage=usage)
