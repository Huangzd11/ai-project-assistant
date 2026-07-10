#!/usr/bin/env python3
# Day25 — AI PM 日成本粗算脚本
#
# 示例：
#   python scripts/estimate_cost.py --users 1000 --qpu 20 --avg-tokens 3000

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.pricing import estimate_daily_cost  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="估算规模化日/月 LLM 成本")
    parser.add_argument("--users", type=int, default=1000)
    parser.add_argument("--qpu", type=int, default=20, help="每用户每日问答次数")
    parser.add_argument("--avg-tokens", type=int, default=3000)
    parser.add_argument("--input-ratio", type=float, default=0.67)
    parser.add_argument("--model", type=str, default=None)
    args = parser.parse_args()

    data = estimate_daily_cost(
        users=args.users,
        queries_per_user=args.qpu,
        avg_total_tokens=args.avg_tokens,
        input_ratio=args.input_ratio,
        model=args.model,
    )

    print("=== Day25 Cost Estimate ===")
    print(f"model:                 {data['model']}")
    print(f"users × qpu × tokens:  {data['users']} × {data['queries_per_user']} × {data['avg_total_tokens']}")
    print(f"daily prompt tokens:   {data['daily_prompt_tokens']:,}")
    print(f"daily completion:      {data['daily_completion_tokens']:,}")
    print(f"daily cost:            ${data['daily_cost_usd']:.4f}")
    print(f"monthly cost (~30d):   ${data['monthly_cost_usd']:.4f}")
    print(f"formula:               {data['formula']}")


if __name__ == "__main__":
    main()
