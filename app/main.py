# Day04 — FastAPI 应用入口
# Day08 — 重构：路由拆分到 app/api/，注册 upload 路由
# Day14 — 中间件、全局异常、OpenAPI 元数据
#
# 功能：创建 FastAPI 实例，挂载各 API 路由模块
# 逻辑：main.py 只做组装，不包含业务逻辑
# 启动：python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import agent, chat, health, rag, upload
from app.core.exceptions import AppError
from app.core.logger import logger
from app.core.middleware import RequestLoggingMiddleware

app = FastAPI(
    title="AI Project Assistant",
    version="0.3-alpha",
    description=(
        "企业知识库 Agent API（Sprint 3）。"
        "支持 PDF 上传、纯 LLM 对话、RAG 问答、Agent 规划与工具调用。"
    ),
)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(rag.router)
app.include_router(agent.router)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    if exc.status_code >= 500:
        logger.error("AppError: %s", exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误"})
