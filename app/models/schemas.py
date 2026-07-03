from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户消息")


class ChatResponse(BaseModel):
    answer: str


class HealthResponse(BaseModel):
    status: str


class ModelInfo(BaseModel):
    provider: str
    model: str
    base_url: str


class UploadResponse(BaseModel):
    filename: str
    size: str
