from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户消息")


class ChatResponse(BaseModel):
    answer: str


class HealthResponse(BaseModel):
    status: str
