from fastapi import APIRouter

from app.core.config import MODEL_NAME, OPENAI_BASE_URL, PROVIDER
from app.core.llm import chat
from app.models import ChatRequest, ChatResponse, ModelInfo

router = APIRouter(tags=["chat"])


@router.get("/models", response_model=ModelInfo)
def models():
    return ModelInfo(
        provider=PROVIDER,
        model=MODEL_NAME,
        base_url=OPENAI_BASE_URL,
    )


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    answer = chat(req.message)
    return ChatResponse(answer=answer)
