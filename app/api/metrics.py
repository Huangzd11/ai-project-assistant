# Day25 — Token / 成本估算 API（AI PM）
#
# 功能：规模化日成本粗算（1000 用户 × 20 次 × 3000 Token）

from fastapi import APIRouter, Query

from app.core.config import MODEL_NAME
from app.core.pricing import estimate_daily_cost
from app.models import CostEstimateResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get(
    "/cost-estimate",
    response_model=CostEstimateResponse,
    summary="日成本估算",
    description=(
        "AI PM 规模化粗算："
        "`daily = users × queries_per_user × (prompt×P_in + completion×P_out) / 1M`。"
        "默认 input_ratio=0.67（约 2/3 Input、1/3 Output）。"
    ),
)
def cost_estimate(
    users: int = Query(1000, ge=1, description="日活用户数"),
    queries_per_user: int = Query(20, ge=1, description="每用户每日问答次数"),
    avg_total_tokens: int = Query(3000, ge=1, description="平均每次总 Token"),
    input_ratio: float = Query(0.67, ge=0.0, le=1.0, description="Input 占比"),
    model: str | None = Query(None, description="模型名，默认当前 MODEL_NAME"),
):
    data = estimate_daily_cost(
        users=users,
        queries_per_user=queries_per_user,
        avg_total_tokens=avg_total_tokens,
        input_ratio=input_ratio,
        model=model or MODEL_NAME,
    )
    return CostEstimateResponse(**data)
