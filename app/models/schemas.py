# Day04 — 请求/响应数据契约（Pydantic）
# Day08 — 新增 UploadResponse
# Day14 — Field 描述与 OpenAPI 示例
#
# 功能：定义 API 入参/出参结构，自动校验与生成 OpenAPI 文档
# 逻辑：FastAPI 通过 response_model 和请求体类型引用这些模型

from pydantic import BaseModel, ConfigDict, Field


# @brief: POST /chat 请求体（Day04）
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户消息", examples=["什么是 RAG？"])


# @brief: POST /chat 响应体（Day04）
class ChatResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"answer": "RAG（Retrieval-Augmented Generation）是检索增强生成..."}]}
    )

    answer: str = Field(..., description="模型生成的回答")


# @brief: GET /health 响应体（Day04）
class HealthResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{"status": "OK"}]})

    status: str = Field(..., description="服务状态，正常时为 OK")


# @brief: GET /models 响应体（Day04）
class ModelInfo(BaseModel):
    provider: str = Field(..., description="模型提供方")
    model: str = Field(..., description="当前模型名称")
    base_url: str = Field(..., description="API 基础地址")


# @brief: POST /upload 响应体（Day08）
class UploadResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"filename": "linux.pdf", "size": "8MB"}]}
    )

    filename: str = Field(..., description="保存后的文件名")
    size: str = Field(..., description="人类可读文件大小")


# @brief: RAG 来源条目（Day13）
class RagSource(BaseModel):
    source: str = Field(..., description="文档名")
    page: int = Field(..., description="页码")
    chunk: int = Field(..., description="chunk 编号")
    score: float = Field(..., description="检索相似度（越高越相关）")


# @brief: POST /rag 请求体（Day13）
class RagRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="用户问题",
        examples=["如何开启 telnet？"],
    )


# @brief: POST /rag 响应体（Day13）
class RagResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "question": "如何开启 telnet？",
                    "answer": "根据《test.pdf》第1页：ASR1803开启telnetd……",
                    "sources": [
                        {
                            "source": "test.pdf",
                            "page": 1,
                            "chunk": 1,
                            "score": 0.72,
                        }
                    ],
                }
            ]
        }
    )

    question: str = Field(..., description="用户问题")
    answer: str = Field(..., description="LLM 生成的回答（含引用句式）")
    sources: list[RagSource] = Field(
        default_factory=list,
        description="引用来源列表；无命中时为空数组",
    )
