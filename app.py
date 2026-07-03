from fastapi import FastAPI

from config import MODEL_NAME, OPENAI_BASE_URL, PROVIDER
from llm import chat
from models import ChatRequest, ChatResponse, HealthResponse, ModelInfo

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello AI"}


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="OK")


@app.get("/models", response_model=ModelInfo)
def models():
    return ModelInfo(
        provider=PROVIDER,
        model=MODEL_NAME,
        base_url=OPENAI_BASE_URL,
    )


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    answer = chat(req.message)
    return ChatResponse(answer=answer)
