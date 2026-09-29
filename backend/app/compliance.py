"""S12: Compliance Radar lite - due-date math for the seeded obligations.

Nepal's fiscal year runs Shrawan 1 to Ashad-end (BS months 4..3 of the next
year), so "FY end year" below means the BS year whose Ashad marks that
year's fiscal year-end - e.g. FY 2081/82 ends in Ashad 2082, so its
fy_end_year is 2082.

Month-end arithmetic goes through `nepali_datetime.date.fromordinal`, not
`date - timedelta`: subtracting a timedelta from this library's BS date does
NOT roll over into the previous month (date(2082,3,1) - 1 day comes back as
the non-existent "2082-03-32" instead of normalizing), so ordinal round-trips
are the only safe way to walk BS dates by a day count.
"""
from __future__ import annotations

import datetime

import nepali_datetime

from .calculators.dates import ad_to_bs, bs_to_ad


def _bs_date(year: int, month: int, day: int) -> nepali_datetime.date:
    return nepali_datetime.date(year, month, day)


def bs_month_end(year: int, month: int) -> nepali_datetime.date:
    """The last day of the given BS year/month."""
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
    first_of_next = _bs_date(next_year, next_month, 1)
    return nepali_datetime.date.fromordinal(first_of_next.toordinal() - 1)


def add_bs_days(d: nepali_datetime.date, days: int) -> nepali_datetime.date:
    return nepali_datetime.date.fromordinal(d.toordinal() + days)


def add_bs_months(year: int, month: int, n: int) -> tuple[int, int]:
    total = (year * 12 + (month - 1)) + n
    return total // 12, total % 12 + 1


def due_date_for_month_end_rule(bs_year: int, bs_month: int, days: int) -> nepali_datetime.date:
    """"days_after_bs_month_end": due `days` after the end of BS bs_year/bs_month
    (the obligation period itself, e.g. the VAT return for Shrawan)."""
    return add_bs_days(bs_month_end(bs_year, bs_month), days)


def due_date_for_fy_end_rule(fy_end_year: int, months: int) -> nepali_datetime.date:
    """"months_after_bs_fy_end": due at the end of the BS month `months` after
    Ashad-end of the fiscal year ending in `fy_end_year`."""
    y, m = add_bs_months(fy_end_year, 3, months)
    return bs_month_end(y, m)


def _due_date_ad(due_rule: dict, period_year: int, period_month: int | None) -> nepali_datetime.date:
    rtype = due_rule["type"]
    if rtype == "days_after_bs_month_end":
        return due_date_for_month_end_rule(period_year, period_month, due_rule["days"])
    if rtype == "months_after_bs_fy_end":
        return due_date_for_fy_end_rule(period_year, due_rule["months"])
    raise ValueError(f"unknown due_rule type: {rtype}")


def applies_to(applies_if: dict, profile: dict) -> bool:
    if applies_if.get("pan_vat_registered") and not profile.get("pan_vat_registered"):
        return False
    if applies_if.get("has_employees") and not profile.get("has_employees"):
        return False
    entity_types = applies_if.get("entity_type_in")
    if entity_types and profile.get("entity_type") not in entity_types:
        return False
    return True


def next_due(obligation: dict, today_ad: datetime.date) -> tuple[str, nepali_datetime.date] | None:
    """The obligation's next unpassed due date on/after `today_ad`, as
    (period, bs_due_date), or None if the due_rule type is unrecognized.
    Checks a small window of neighbouring periods (BS month/year can shift
    relative to the AD "today" depending on where in the month we are) and
    returns the earliest due date that hasn't passed yet."""
    today_bs = ad_to_bs(today_ad)
    frequency = obligation["frequency"]
    rule = obligation["due_rule"]
    candidates: list[tuple[str, nepali_datetime.date]] = []
    if frequency == "monthly":
        for offset in (-1, 0, 1):
            y, m = add_bs_months(today_bs.year, today_bs.month, offset)
            due = _due_date_ad(rule, y, m)
            candidates.append((f"{y:04d}-{m:02d}", due))
    else:  # annual
        for fy_end_year in (today_bs.year - 1, today_bs.year, today_bs.year + 1):
            due = _due_date_ad(rule, fy_end_year, None)
            candidates.append((str(fy_end_year), due))
    upcoming = [(period, due) for period, due in candidates if bs_to_ad(due.year, due.month, due.day) >= today_ad]
    if not upcoming:
        return None
    return min(upcoming, key=lambda pair: pair[1].toordinal())
