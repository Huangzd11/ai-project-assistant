# Day04 — 请求/响应数据契约（Pydantic）
# Day08 — 新增 UploadResponse
#
# 功能：定义 API 入参/出参结构，自动校验与生成 OpenAPI 文档
# 逻辑：FastAPI 通过 response_model 和请求体类型引用这些模型

from pydantic import BaseModel, Field


# @brief: POST /chat 请求体（Day04）
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户消息")


# @brief: POST /chat 响应体（Day04）
class ChatResponse(BaseModel):
    answer: str


# @brief: GET /health 响应体（Day04）
class HealthResponse(BaseModel):
    status: str


# @brief: GET /models 响应体（Day04）
class ModelInfo(BaseModel):
    provider: str
    model: str
    base_url: str


# @brief: POST /upload 响应体（Day08）
class UploadResponse(BaseModel):
    filename: str
    size: str
