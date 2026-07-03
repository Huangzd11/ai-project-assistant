from fastapi import FastAPI

from llm import chat
from models import ChatRequest, ChatResponse, HealthResponse

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello AI"}


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="OK")


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    answer = chat(req.message)
    return ChatResponse(answer=answer)