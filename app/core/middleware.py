# Day14 — 请求日志中间件
# Day24 — Request ID / Trace ID 中间件
#
# 功能：记录每个 HTTP 请求的方法、路径、耗时与状态码

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import logger
from app.core.request_context import (
    get_trace_id,
    request_id_var,
    resolve_request_id,
    resolve_trace_id,
    trace_id_var,
)


def _format_duration(seconds: float) -> str:
    if seconds >= 1:
        return f"{seconds:.1f}s"
    return f"{seconds * 1000:.0f}ms"


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = resolve_request_id(request.headers.get("X-Request-ID"))
        trace_id = resolve_trace_id(request.headers.get("X-Trace-ID"))
        rid_token = request_id_var.set(request_id)
        tid_token = trace_id_var.set(trace_id)
        request.state.request_id = request_id
        request.state.trace_id = trace_id
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            if trace_id:
                response.headers["X-Trace-ID"] = trace_id
            return response
        finally:
            request_id_var.reset(rid_token)
            trace_id_var.reset(tid_token)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        trace_part = f"  trace_id={get_trace_id()}" if get_trace_id() else ""
        logger.info(
            "method=%s  path=%s  duration=%s  status=%d%s",
            request.method,
            request.url.path,
            _format_duration(elapsed),
            response.status_code,
            trace_part,
        )
        return response
