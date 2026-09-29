"""S13: plan-based tier routing and token-cost accounting.

STRATEGY.md §2's routing rule, encoded directly: free chain (existing
multi-provider fallback in llm.py) for free-plan users; Claude Haiku 4.5 for
a paid plan's structured chat answers; Claude Sonnet 5.5 only for a paid
plan's drafting/contract-review task. "Paid" here means any plan other than
"free" - the three paid tiers (individual/professional/firm) all route the
same way; they differ only in daily quota.
"""
from __future__ import annotations

from . import config

PLAN_DAILY_QUOTA = {
    "free": config.DAILY_QUOTA_FREE,
    "individual": config.DAILY_QUOTA_INDIVIDUAL,
    "professional": config.DAILY_QUOTA_PROFESSIONAL,
    "firm": config.DAILY_QUOTA_FIRM,
}

_MODEL_FOR_TIER = {"haiku": config.PAID_HAIKU_MODEL, "sonnet": config.PAID_SONNET_MODEL}


def daily_quota_for(plan: str) -> int:
    return PLAN_DAILY_QUOTA.get(plan, PLAN_DAILY_QUOTA["free"])


def select_tier(plan: str, task: str) -> str:
    """`task` is "chat" (structured Q&A) or "draft" (AI-fill / document
    drafting). Returns "free", "haiku", or "sonnet"."""
    if plan not in PLAN_DAILY_QUOTA or plan == "free":
        return "free"
    return "sonnet" if task == "draft" else "haiku"


def model_for_tier(tier: str) -> str | None:
    return _MODEL_FOR_TIER.get(tier)


def estimate_cost_usd(tier: str, input_tokens: int | None, output_tokens: int | None) -> float:
    model = model_for_tier(tier)
    pricing = config.MODEL_PRICING_PER_1M.get(model or "")
    if not pricing:
        return 0.0
    return round(((input_tokens or 0) * pricing["input"] + (output_tokens or 0) * pricing["output"]) / 1_000_000, 6)
