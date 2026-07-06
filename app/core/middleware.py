# Day14 — 请求日志中间件
#
# 功能：记录每个 HTTP 请求的方法、路径、耗时与状态码
# 逻辑：BaseHTTPMiddleware 包裹 call_next，perf_counter 计时

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import logger


def _format_duration(seconds: float) -> str:
    if seconds >= 1:
        return f"{seconds:.1f}s"
    return f"{seconds * 1000:.0f}ms"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        logger.info(
            "%s %s  duration=%s  status=%d",
            request.method,
            request.url.path,
            _format_duration(elapsed),
            response.status_code,
        )
        return response
