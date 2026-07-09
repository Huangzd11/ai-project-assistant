# Day04 — FastAPI 应用入口
# Day08 — 重构：路由拆分到 app/api/，注册 upload 路由
# Day14 — 中间件、全局异常、OpenAPI 元数据
# Day18/19 — MCP Client 启动引导
# Day24 — Request ID、分级日志落盘
#
# 功能：创建 FastAPI 实例，挂载各 API 路由模块
# 逻辑：main.py 只做组装，不包含业务逻辑
# 启动：python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import agent, chat, health, mcp, rag, upload
from app.core.config import APP_VERSION
from app.core.exceptions import AppError
from app.core.logger import logger
from app.core.middleware import RequestIdMiddleware, RequestLoggingMiddleware
from app.core.request_context import get_request_id
from app.mcp import bootstrap_mcp, shutdown_mcp


def _error_content(detail: str) -> dict:
    content = {"detail": detail}
    rid = get_request_id()
    if rid != "-":
        content["request_id"] = rid
    return content


def _error_headers() -> dict[str, str]:
    rid = get_request_id()
    if rid == "-":
        return {}
    return {"X-Request-ID": rid}


# @brief: 生命周期管理
# @param: _app: FastAPI
# @return: None
@asynccontextmanager
async def lifespan(_app: FastAPI):
    await bootstrap_mcp()
    yield
    await shutdown_mcp()


app = FastAPI(
    title="AI Project Assistant",
    version=APP_VERSION,
    description=(
        "企业 AI Agent API（v0.4.0-beta）。"
        "Workflow 意图路由、Tool Registry、会话 Memory、Docker Compose、"
        "Nginx 反代、结构化日志、企业 RAG。"
    ),
    lifespan=lifespan,
)

# Starlette：后添加的中间件在外层先执行 → CORS → RequestId → RequestLogging
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @brief: 注册路由
# @return: None
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(rag.router)
app.include_router(agent.router)
app.include_router(mcp.router)


# @brief: 处理 AppError
# @param: request: 请求
# @param: exc: AppError
# @return: JSONResponse
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    if exc.status_code >= 500:
        logger.error(
            "event=app_error  path=%s  status=%d  detail=%s",
            request.url.path,
            exc.status_code,
            exc.detail,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_content(exc.detail),
        headers=_error_headers(),
    )


# @brief: 处理未捕获的异常
# @param: request: 请求
# @param: exc: Exception
# @return: JSONResponse
@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "event=unhandled_error  path=%s  error=%s",
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=500,
        content=_error_content("服务器内部错误"),
        headers=_error_headers(),
    )
