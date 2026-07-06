# Day14 — 统一业务异常
#
# 功能：将 LLM / 服务等错误映射为友好 HTTP 响应
# 逻辑：main.py 注册 exception_handler，按 status_code 返回 detail

class AppError(Exception):
    """应用层可预期异常基类。"""

    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class LLMUnavailableError(AppError):
    """LLM 服务不可达或调用失败。"""

    def __init__(self, detail: str = "LLM 服务不可用，请检查 Ollama"):
        super().__init__(detail, status_code=503)


class LLMTimeoutError(AppError):
    """LLM 请求超时。"""

    def __init__(self, detail: str = "LLM 请求超时"):
        super().__init__(detail, status_code=504)
