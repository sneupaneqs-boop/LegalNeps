"""Labour Act, 2074 (श्रम ऐन, २०७४) calculators (S8): gratuity, termination
notice/pay-in-lieu, and retrenchment (कटौती) severance compensation.
"""
from __future__ import annotations

from ..playbooks import resolve_provision

GRATUITY_PROVISION = {"law_title_ne": "श्रम ऐन, २०७४", "section": "53"}
NOTICE_PROVISION = {"law_title_ne": "श्रम ऐन, २०७४", "section": "144"}
SEVERANCE_PROVISION = {"law_title_ne": "श्रम ऐन, २०७४", "section": "145 (2)"}

GRATUITY_RATE = 0.0833  # दफा ५३(१): 8.33% of basic monthly remuneration, per month of service


def gratuity(basic_monthly_pay: float, months_of_service: float) -> dict:
    """दफा ५३: उपदान accrues at 8.33% of basic monthly pay for every month
    worked, deposited into the Social Security Fund."""
    if basic_monthly_pay <= 0:
        raise ValueError("basic_monthly_pay must be positive")
    if months_of_service < 0:
        raise ValueError("months_of_service cannot be negative")
    amount = round(basic_monthly_pay * GRATUITY_RATE * months_of_service, 2)
    return {"amount_npr": amount, "provision": resolve_provision(GRATUITY_PROVISION)}


def notice_period_days(service_days: int) -> int:
    """दफा १४४(१): minimum notice before ending an employment relationship
    (either side), tiered by how long the worker has been employed."""
    if service_days < 0:
        raise ValueError("service_days cannot be negative")
    if service_days <= 28:  # up to 4 weeks
        return 1
    if service_days <= 365:  # 4 weeks to 1 year
        return 7
    return 30  # more than 1 year


def notice(service_days: int, daily_wage: float) -> dict:
    """दफा १४४: the notice period owed, and the pay-in-lieu (दफा १४४(२)/(३))
    if the employer skips giving that notice."""
    if daily_wage <= 0:
        raise ValueError("daily_wage must be positive")
    days = notice_period_days(service_days)
    return {
        "notice_period_days": days,
        "pay_in_lieu_npr": round(days * daily_wage, 2),
        "provision": resolve_provision(NOTICE_PROVISION),
    }


def severance(basic_monthly_pay: float, years_of_service: float) -> dict:
    """दफा १४५(७): one month's basic pay per completed year of service as
    a lump-sum retrenchment (कटौती) compensation, pro-rated (दामासाहीले) for
    a partial year - both cases reduce to basic_monthly_pay * years."""
    if basic_monthly_pay <= 0:
        raise ValueError("basic_monthly_pay must be positive")
    if years_of_service < 0:
        raise ValueError("years_of_service cannot be negative")
    amount = round(basic_monthly_pay * years_of_service, 2)
    return {"amount_npr": amount, "provision": resolve_provision(SEVERANCE_PROVISION)}
