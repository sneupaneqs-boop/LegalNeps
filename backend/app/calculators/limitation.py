"""Limitation-period (हदम्याद) checker (S8).

मुलुकी देवानी कार्यविधि संहिता दफा ४९ says the limitation period for any
claim is whatever period *that claim's own governing law* sets, and only
falls back to "from the date the cause of action arose" when no specific
law sets one - there is no single general limitation period in Nepali law.
So this is a lookup table of specific, cited claim types (reusing the same
citations S6/S7 already verified against the corpus for the matching
playbooks), not one formula - each entry's provision is re-resolved against
the live corpus here too, so a corpus change that breaks a citation breaks
this calculator's tests as loudly as it breaks the playbook's.
"""
from __future__ import annotations

import calendar
import dataclasses
import datetime

from ..playbooks import resolve_provision


@dataclasses.dataclass(frozen=True)
class LimitationRule:
    claim_type: str
    period_value: int
    period_unit: str  # "days" | "months" | "years"
    note: dict
    provision: dict  # {law_title_ne, section}


RULES: dict[str, LimitationRule] = {
    "contract_civil_claim": LimitationRule(
        claim_type="contract_civil_claim",
        period_value=2, period_unit="years",
        note={
            "en": "Most civil claims arising from a contract (e.g. an unpaid personal loan) must be filed within 2 years of when the cause of action arose.",
            "ne": "करारबाट उत्पन्न अधिकांश देवानी दाबी (जस्तै तिरेको ऋण नफिर्ता भएको) दाबी गर्नुपर्ने कारण उत्पन्न भएको मितिले २ वर्षभित्र दायर गर्नुपर्छ।",
        },
        provision={"law_title_ne": "मुलुकी देवानी संहिता, २०७४", "section": "520"},
    ),
    "partition_disagreement": LimitationRule(
        claim_type="partition_disagreement",
        period_value=3, period_unit="months",
        note={
            "en": "If a property partition (अंशबण्डा) already happened and you disagree with it, you must claim within 3 months of that partition.",
            "ne": "अंशबण्डा भइसकेको र त्यसमा असहमत भए बण्डा भएको मितिले ३ महिनाभित्र दाबी गर्नुपर्छ।",
        },
        provision={"law_title_ne": "मुलुकी देवानी संहिता, २०७४", "section": "235"},
    ),
    "labour_dispute_complaint": LimitationRule(
        claim_type="labour_dispute_complaint",
        period_value=6, period_unit="months",
        note={
            "en": "A labour complaint (unpaid wages, wrongful termination, bonus, etc.) must be filed within 6 months of the act complained of.",
            "ne": "श्रम सम्बन्धी उजुरी (तलब नपाएको, गलत तरिकाले हटाइएको, बोनस आदि) सो कार्य भएको मितिले ६ महिनाभित्र दिनुपर्छ।",
        },
        provision={"law_title_ne": "श्रम ऐन, २०७४", "section": "162"},
    ),
    "foreign_employment_complaint": LimitationRule(
        claim_type="foreign_employment_complaint",
        period_value=1, period_unit="years",
        note={
            "en": "A foreign-employment complaint must be filed within 1 year of the incident, or within 1 year of returning to Nepal if you were abroad.",
            "ne": "वैदेशिक रोजगार सम्बन्धी उजुरी घटना भएको मितिले (वा विदेशमा हुनुभएको भए नेपाल फर्किएको मितिले) १ वर्षभित्र दिनुपर्छ।",
        },
        provision={"law_title_ne": "वैदेशिक रोजगार ऐन, २०६४", "section": "60"},
    ),
    "cheque_dishonour_complaint": LimitationRule(
        claim_type="cheque_dishonour_complaint",
        period_value=1, period_unit="years",
        note={
            "en": "A dishonoured-cheque complaint must be filed within 1 year of learning the cheque bounced.",
            "ne": "चेक अनादर भएको उजुरी सो कुरा थाहा पाएको मितिले १ वर्षभित्र दिनुपर्छ।",
        },
        provision={"law_title_ne": "बैङ्किङ्ग कसूर तथा सजाय ऐन, २०६४", "section": "17"},
    ),
}


class UnknownClaimType(ValueError):
    pass


def _add_period(d: datetime.date, value: int, unit: str) -> datetime.date:
    if unit == "days":
        return d + datetime.timedelta(days=value)
    months = value if unit == "months" else value * 12
    total_month_index = d.month - 1 + months
    year = d.year + total_month_index // 12
    month = total_month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def list_claim_types() -> list[str]:
    return sorted(RULES)


def check(claim_type: str, trigger_date: datetime.date, today: datetime.date | None = None) -> dict:
    """Deadline + days remaining for `claim_type`, whose limitation clock
    started on `trigger_date`. Raises UnknownClaimType for an unlisted claim
    and UnresolvedProvision (via resolve_provision) if the corpus no longer
    carries the cited section."""
    rule = RULES.get(claim_type)
    if rule is None:
        raise UnknownClaimType(f"{claim_type!r} is not a known claim type; see list_claim_types()")
    today = today or datetime.date.today()
    deadline = _add_period(trigger_date, rule.period_value, rule.period_unit)
    return {
        "claim_type": rule.claim_type,
        "trigger_date": trigger_date.isoformat(),
        "deadline": deadline.isoformat(),
        "days_remaining": (deadline - today).days,
        "is_time_barred": today > deadline,
        "note": rule.note,
        "provision": resolve_provision(rule.provision),
    }
