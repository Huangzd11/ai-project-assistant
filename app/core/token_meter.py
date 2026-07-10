# Day25 — Token 用量计量
#
# 功能：从 LLM usage 构建 UsageInfo，写日志，支持请求级累加

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.core.config import MODEL_NAME
from app.core.logger import logger
from app.core.pricing import estimate_cost, load_pricing

# @brief: 用量信息
# @param: prompt_tokens: 提示词 Token 数
# @param: completion_tokens: 完成 Token 数
# @param: total_tokens: 总 Token 数
# @param: cost_usd: 成本（美元）
# @param: model: 模型名
# @param: currency: 货币
@dataclass
class UsageInfo:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    model: str
    currency: str = "USD"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

# @brief: 构建用量信息
# @param: prompt_tokens: 提示词 Token 数
# @param: completion_tokens: 完成 Token 数
# @param: model: 模型名
# @param: log: 是否记录日志
# @return: UsageInfo
def build_usage(
    prompt_tokens: int,
    completion_tokens: int,
    model: str | None = None,
    *,
    log: bool = True,
) -> UsageInfo:
    resolved = model or MODEL_NAME
    total = prompt_tokens + completion_tokens
    cost = estimate_cost(prompt_tokens, completion_tokens, model=resolved)
    currency = load_pricing().currency
    usage = UsageInfo(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total,
        cost_usd=cost,
        model=resolved,
        currency=currency,
    )
    if log:
        logger.info(
            "event=llm_usage  model=%s  prompt_tokens=%d  completion_tokens=%d  "
            "total_tokens=%d  cost_usd=%.6f",
            usage.model,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
            usage.cost_usd,
        )
    return usage

# @brief: 从 OpenAI 兼容 usage 对象构建 UsageInfo
# @param: raw: OpenAI 兼容 usage 对象
# @param: model: 模型名
# @param: log: 是否记录日志
# @return: UsageInfo | None
def usage_from_openai(raw: Any, model: str | None = None, *, log: bool = True) -> UsageInfo | None:
    """解析 OpenAI 兼容 usage 对象；缺失时返回 None。"""
    if raw is None:
        return None
    try:
        if isinstance(raw, dict):
            prompt = int(raw.get("prompt_tokens") or 0)
            completion = int(raw.get("completion_tokens") or 0)
            total = int(raw.get("total_tokens") or 0)
        else:
            prompt = int(getattr(raw, "prompt_tokens", 0) or 0)
            completion = int(getattr(raw, "completion_tokens", 0) or 0)
            total = int(getattr(raw, "total_tokens", 0) or 0)
    except (AttributeError, TypeError, ValueError):
        logger.warning("event=usage_parse_failed")
        return None

    if total <= 0 and prompt <= 0 and completion <= 0:
        return None
    if total <= 0:
        total = prompt + completion

    usage = build_usage(prompt, completion, model=model, log=log)
    # 若 API 给了 total，以 API 为准（通常等于 prompt+completion）
    if total != usage.total_tokens:
        usage.total_tokens = total
    return usage

# @brief: 合并用量信息
# @param: parts: 用量信息列表
# @return: UsageInfo | None
def merge_usage(*parts: UsageInfo | None) -> UsageInfo | None:
    items = [p for p in parts if p is not None]
    if not items:
        return None
    prompt = sum(i.prompt_tokens for i in items)
    completion = sum(i.completion_tokens for i in items)
    model = items[-1].model
    return build_usage(prompt, completion, model=model, log=False)
