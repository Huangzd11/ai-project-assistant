# Day04 — HTTP 聊天接口
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
from app.models import ChatRequest, ChatResponse, ModelInfo

router = APIRouter(tags=["chat"])


@router.get("/models", response_model=ModelInfo)
def models():
    """返回当前 LLM 提供方、模型名、API 地址。"""
    return ModelInfo(
        provider=PROVIDER,
        model=MODEL_NAME,
        base_url=OPENAI_BASE_URL,
    )


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """单轮对话：用户 message → LLM → answer。"""
    answer = chat(req.message)
    return ChatResponse(answer=answer)
