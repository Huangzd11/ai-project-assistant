# Day24 — 请求上下文（Request ID / Trace ID）
#
# 功能：contextvars 贯穿单次 HTTP 请求，日志 Filter 自动注入字段

import contextvars
import logging
import uuid

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")
trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")


def get_request_id() -> str:
    return request_id_var.get()


def get_trace_id() -> str:
    return trace_id_var.get()


def resolve_request_id(header_value: str | None) -> str:
    if header_value and header_value.strip():
        return header_value.strip()
    return str(uuid.uuid4())


def resolve_trace_id(header_value: str | None) -> str:
    if header_value and header_value.strip():
        return header_value.strip()
    return ""


class RequestContextFilter(logging.Filter):
    """为每条日志注入 request_id / trace_id 格式化字段。"""

    def filter(self, record: logging.LogRecord) -> bool:
        rid = get_request_id()
        record.request_id = f"request_id={rid}" if rid != "-" else "request_id=-"
        tid = get_trace_id()
        record.trace_id = f"trace_id={tid}" if tid else ""
        return True
