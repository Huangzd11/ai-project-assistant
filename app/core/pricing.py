# Day25 — 模型单价加载与成本估算
#
# 功能：从 config/pricing.yaml 读取单价，估算单次请求 cost_usd
# 逻辑：Cost = prompt/1M × P_in + completion/1M × P_out

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from app.core.config import MODEL_NAME

# @brief: 模型单价
@dataclass(frozen=True)
class ModelRates:
    input_per_1m_usd: float
    output_per_1m_usd: float

# @brief: 单价配置
@dataclass(frozen=True)
class PricingConfig:
    default_model: str
    fx_cny_per_usd: float
    currency: str
    models: dict[str, ModelRates]

# @brief: 单价文件路径
def _pricing_path() -> Path:
    override = os.getenv("PRICING_FILE", "").strip()
    if override:
        return Path(override)
    root = Path(__file__).resolve().parent.parent.parent
    return root / "config" / "pricing.yaml"

# @brief: 加载单价配置
@lru_cache(maxsize=1)
def load_pricing() -> PricingConfig:
    path = _pricing_path()
    if not path.is_file():
        return PricingConfig(
            default_model=MODEL_NAME,
            fx_cny_per_usd=7.2,
            currency=os.getenv("COST_CURRENCY", "USD"),
            models={
                MODEL_NAME: ModelRates(0.0, 0.0),
                "qwen-plus": ModelRates(0.11, 0.28),
            },
        )

    with path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    models: dict[str, ModelRates] = {}
    for name, rates in (raw.get("models") or {}).items():
        if not isinstance(rates, dict):
            continue
        models[str(name)] = ModelRates(
            input_per_1m_usd=float(rates.get("input_per_1m_usd", 0.0)),
            output_per_1m_usd=float(rates.get("output_per_1m_usd", 0.0)),
        )

    return PricingConfig(
        default_model=str(raw.get("default_model", MODEL_NAME)),
        fx_cny_per_usd=float(raw.get("fx_cny_per_usd", 7.2)),
        currency=os.getenv("COST_CURRENCY", str(raw.get("currency", "USD"))),
        models=models,
    )

# @brief: 获取模型单价
def get_rates(model: str | None = None) -> tuple[str, ModelRates]:
    cfg = load_pricing()
    name = model or MODEL_NAME
    if name in cfg.models:
        return name, cfg.models[name]
    if cfg.default_model in cfg.models:
        return cfg.default_model, cfg.models[cfg.default_model]
    return name, ModelRates(0.0, 0.0)

# @brief: 估算单次请求成本
def estimate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str | None = None,
) -> float:
    _, rates = get_rates(model)
    cost = (
        prompt_tokens / 1_000_000 * rates.input_per_1m_usd
        + completion_tokens / 1_000_000 * rates.output_per_1m_usd
    )
    return round(cost, 6)

# @brief: 估算每日成本
def estimate_daily_cost(
    users: int,
    queries_per_user: int,
    avg_total_tokens: int,
    input_ratio: float = 0.67,
    model: str | None = None,
) -> dict:
    """AI PM 规模化粗算：users × qpu × (in×P_in + out×P_out)。"""
    ratio = min(max(input_ratio, 0.0), 1.0)
    prompt = int(avg_total_tokens * ratio)
    completion = max(avg_total_tokens - prompt, 0)
    daily_prompt = users * queries_per_user * prompt
    daily_completion = users * queries_per_user * completion
    daily_cost = estimate_cost(daily_prompt, daily_completion, model=model)
    resolved_model, _ = get_rates(model)
    cfg = load_pricing()
    return {
        "users": users,
        "queries_per_user": queries_per_user,
        "avg_total_tokens": avg_total_tokens,
        "input_ratio": ratio,
        "model": resolved_model,
        "daily_prompt_tokens": daily_prompt,
        "daily_completion_tokens": daily_completion,
        "daily_cost_usd": daily_cost,
        "monthly_cost_usd": round(daily_cost * 30, 4),
        "currency": cfg.currency,
        "formula": "daily = users * qpu * (prompt*P_in + completion*P_out) / 1M",
    }
