"""Court fee (अदालती शुल्क) calculator (S8).

मुलुकी देवानी कार्यविधि संहिता, २०७४ दफा ६९ sets a marginal-bracket schedule
on the claim's disclosed value (बिगो): a flat Rs 500 base for the first
Rs 25,000, then a shrinking percentage on each further bracket - the same
shape as an income-tax schedule, so it's computed the same way (each
bracket's rate applies only to the slice of value that falls inside it).
दफा ७३ adds a flat 15% surcharge on appeal, computed on the fee for the
value actually being appealed. दफा ९७ is a separate, always-flat Rs 200
filing fee (फिराद दस्तुर) charged on every plaint regardless of value -
it is not part of the दफा ६९ schedule.
"""
from __future__ import annotations

from ..playbooks import resolve_provision

FILING_FEE_PROVISION = {"law_title_ne": "मुलुकी देवानी कार्यविधि संहिता, २०७४", "section": "97"}
COURT_FEE_PROVISION = {"law_title_ne": "मुलुकी देवानी कार्यविधि संहिता, २०७४", "section": "69"}
APPEAL_FEE_PROVISION = {"law_title_ne": "मुलुकी देवानी कार्यविधि संहिता, २०७४", "section": "73"}

FILING_FEE_NPR = 200.0
APPEAL_SURCHARGE_RATE = 0.15

# (bracket lower bound, bracket upper bound, marginal rate on the slice within it)
_BRACKETS: list[tuple[float, float, float]] = [
    (0, 25_000, 0.0),  # covered by the flat base fee instead of a rate
    (25_000, 50_000, 0.05),
    (50_000, 100_000, 0.035),
    (100_000, 500_000, 0.02),
    (500_000, 2_500_000, 0.015),
    (2_500_000, float("inf"), 0.01),
]
_BASE_FEE = 500.0  # flat fee for the first Rs 25,000 of claim value


def court_fee(claim_value: float) -> float:
    """The दफा ६९ अदालती शुल्क for a claim of this disclosed value."""
    if claim_value <= 0:
        raise ValueError("claim_value must be positive")
    fee = _BASE_FEE
    for lower, upper, rate in _BRACKETS[1:]:
        if claim_value <= lower:
            break
        fee += (min(claim_value, upper) - lower) * rate
    return round(fee, 2)


def appeal_fee(disputed_value: float) -> float:
    """The दफा ७३ additional appeal fee for appealing a claim of this
    (portion of the) disputed value."""
    return round(court_fee(disputed_value) * APPEAL_SURCHARGE_RATE, 2)


def estimate(claim_value: float) -> dict:
    """Filing fee + court fee for filing a plaint over `claim_value`, each
    with its own cited provision."""
    return {
        "claim_value": claim_value,
        "filing_fee_npr": FILING_FEE_NPR,
        "filing_fee_provision": resolve_provision(FILING_FEE_PROVISION),
        "court_fee_npr": court_fee(claim_value),
        "court_fee_provision": resolve_provision(COURT_FEE_PROVISION),
        "total_npr": round(FILING_FEE_NPR + court_fee(claim_value), 2),
    }


def estimate_appeal(disputed_value: float) -> dict:
    return {
        "disputed_value": disputed_value,
        "appeal_fee_npr": appeal_fee(disputed_value),
        "provision": resolve_provision(APPEAL_FEE_PROVISION),
    }
