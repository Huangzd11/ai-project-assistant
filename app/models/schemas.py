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


# @brief: Token / 成本用量（Day25）
class UsageInfo(BaseModel):
    prompt_tokens: int = Field(..., description="Input / Prompt Tokens")
    completion_tokens: int = Field(..., description="Output / Completion Tokens")
    total_tokens: int = Field(..., description="合计 Tokens")
    cost_usd: float = Field(..., description="估算成本（美元）")
    model: str = Field(..., description="计费所用模型名")
    currency: str = Field(default="USD", description="货币单位")


# @brief: POST /chat 响应体（Day04）
class ChatResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "answer": "RAG（Retrieval-Augmented Generation）是检索增强生成...",
                    "usage": {
                        "prompt_tokens": 120,
                        "completion_tokens": 80,
                        "total_tokens": 200,
                        "cost_usd": 0.0004,
                        "model": "qwen-plus",
                        "currency": "USD",
                    },
                }
            ]
        }
    )

    answer: str = Field(..., description="模型生成的回答")
    usage: UsageInfo | None = Field(None, description="Token 与成本（Day25）")


# @brief: GET /health 响应体（Day04 / Day21 增加 version）
class HealthResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"status": "OK", "version": "1.0.0"}]}
    )

    status: str = Field(..., description="服务状态，正常时为 OK")
    version: str = Field(..., description="API 版本号")


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
    usage: UsageInfo | None = Field(None, description="Token 与成本（Day25）")


# @brief: Agent 计划步骤（Day15）
class AgentPlanStep(BaseModel):
    tool: str = Field(..., description="工具名称")
    args: dict = Field(default_factory=dict, description="工具参数")
    reason: str = Field(default="", description="规划原因")


# @brief: POST /agent 请求体（Day15）
class AgentRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="用户目标",
        examples=["总结一下 test.pdf"],
    )
    session_id: str | None = Field(
        None,
        description="会话 ID；相同 ID 共享 Short Memory，支持多轮对话",
        examples=["work-001"],
    )


# @brief: Agent 工作流决策（Day20）
class AgentWorkflowInfo(BaseModel):
    intent: str = Field(
        ...,
        description="意图：chat / rag / filesystem / calculator / weather / news / sports / pdf_read / mcp_explicit",
    )
    need_tool: bool = Field(..., description="是否调用了工具")
    route: str = Field(..., description="路由链路说明")
    reason: str = Field(..., description="决策原因")


# @brief: POST /agent 响应体（Day15）
class AgentResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "总结一下 test.pdf",
                    "answer": "test.pdf 主要介绍了……",
                    "session_id": "work-001",
                    "workflow": {
                        "intent": "rag",
                        "need_tool": True,
                        "route": "Question → RAG Search → Summary → Answer",
                        "reason": "知识库检索与总结",
                    },
                    "plan": [
                        {
                            "tool": "rag_query",
                            "args": {"question": "test.pdf 的主要内容是什么？"},
                            "reason": "需要从知识库获取文档内容",
                        }
                    ],
                    "tool_calls": [{"tool": "rag_query"}],
                    "sources": [
                        {
                            "source": "test.pdf",
                            "page": 1,
                            "chunk": 1,
                            "score": 0.72,
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 1450,
                        "completion_tokens": 632,
                        "total_tokens": 2082,
                        "cost_usd": 0.0038,
                        "model": "qwen-plus",
                        "currency": "USD",
                    },
                }
            ]
        }
    )

    message: str = Field(..., description="用户目标")
    answer: str = Field(..., description="Agent 最终回答")
    session_id: str | None = Field(None, description="会话 ID；与请求一致时用于多轮记忆")
    workflow: AgentWorkflowInfo | None = Field(None, description="工作流决策（Day20）")
    plan: list[AgentPlanStep] = Field(default_factory=list, description="规划步骤")
    tool_calls: list[dict] = Field(default_factory=list, description="实际调用的工具")
    sources: list[RagSource] = Field(
        default_factory=list,
        description="引用来源；无 RAG 命中时为空数组",
    )
    usage: UsageInfo | None = Field(None, description="Token 与成本（Day25）")


# @brief: GET /metrics/cost-estimate 响应（Day25）
class CostEstimateResponse(BaseModel):
    users: int
    queries_per_user: int
    avg_total_tokens: int
    input_ratio: float
    model: str
    daily_prompt_tokens: int
    daily_completion_tokens: int
    daily_cost_usd: float
    monthly_cost_usd: float
    currency: str = "USD"
    formula: str
