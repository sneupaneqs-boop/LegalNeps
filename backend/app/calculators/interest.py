"""Interest on private loans under the Muluki Civil Code, 2074, chapter 15
(लेनदेन व्यवहार): the lawful maximum and a simple-interest calculator.

The rules, all from the Code's own text (see SOURCES):
- s. 479: no interest at all unless the loan instrument says interest is payable;
- s. 478(1)-(3): interest as written in the instrument, but never more than 10%
  a year of the principal; if the instrument says interest is payable but gives
  no rate, 10% a year;
- s. 480: no interest on interest (compound interest is void: it is set against
  the principal, or refunded if the principal is paid);
- s. 481: total interest can never exceed the principal;
- s. 492(1): a claim about interest above 10% or interest on interest has no
  limitation period.

The Code says nothing about how to count the days, so this tool counts actual
days / 365 and says so in the result.
"""
from __future__ import annotations

import datetime

from . import dates
from .sources import Source, cite

CIV = "मुलुकी देवानी संहिता, २०७४"

S_CAP = Source("interest_cap", CIV, "478", "वार्षिक दश प्रतिशतभन्दा बढी", "interest can never exceed 10% a year of the principal")
S_DEFAULT = Source("interest_default", CIV, "478", "साँवा रकमको वार्षिक दश प्रतिशतका दरले", "no rate stated: 10% a year")
S_NOT_STATED = Source("interest_not_stated", CIV, "479", "ब्याज लिने दिने कुरा उल्लेख नभएमा साहूले ऋणीबाट ब्याज लिन पाउने छैन", "no interest unless the instrument mentions it")
S_NO_COMPOUND = Source("interest_no_compound", CIV, "480", "ब्याजको ब्याज लिन पाउने छैन", "no interest on interest")
S_PRINCIPAL_CAP = Source("interest_principal_cap", CIV, "481", "साँवाभन्दा बढी ब्याज लिन पाउने छैन", "total interest can not exceed the principal")
S_TERM = Source("interest_ghar_sar_term", CIV, "484", "बढीमा दश वर्षको हुनेछ", "a ghar-sar instrument runs at most 10 years")
S_NO_LIMIT = Source("interest_no_limitation", CIV, "492", "ब्याजमा दश प्रतिशतभन्दा बढी लिएको", "no limitation for claims about interest above 10% or interest on interest")

SOURCES = [v for v in list(globals().values()) if isinstance(v, Source)]

MAX_ANNUAL_RATE_PCT = 10.0
DAYS_IN_YEAR = 365


def max_lawful_rate() -> dict:
    return {
        "max_annual_rate_pct": MAX_ANNUAL_RATE_PCT,
        "default_rate_pct": MAX_ANNUAL_RATE_PCT,
        "rules": [
            {"en": "Interest is only payable if the loan instrument says so (s. 479).", "ne": "लिखतमा ब्याज लिने दिने कुरा उल्लेख नभए ब्याज पाइँदैन (दफा ४७९)।"},
            {"en": "Never more than 10% a year of the principal (s. 478(2)); if no rate is written, 10% (s. 478(3)).", "ne": "साँवाको वार्षिक १०% भन्दा बढी हुँदैन (दफा ४७८(२)); दर नलेखिएमा १०% (दफा ४७८(३))।"},
            {"en": "No interest on interest (s. 480).", "ne": "ब्याजको ब्याज लिन पाइँदैन (दफा ४८०)।"},
            {"en": "Total interest can never exceed the principal (s. 481).", "ne": "साँवाभन्दा बढी ब्याज लिन पाइँदैन (दफा ४८१)।"},
        ],
        "provisions": [cite(S_CAP), cite(S_DEFAULT), cite(S_NOT_STATED), cite(S_NO_COMPOUND), cite(S_PRINCIPAL_CAP)],
    }


def simple_interest(principal: float, start: datetime.date, end: datetime.date, agreed_rate_pct: float | None = None,
                    interest_stated_in_instrument: bool = True) -> dict:
    """Interest on a private loan from `start` to `end`, with the lawful cap applied.

    agreed_rate_pct: the yearly rate written in the instrument; None means the
    instrument says interest is payable but names no rate (10% applies)."""
    if not (principal > 0):
        raise ValueError("principal must be positive")
    if agreed_rate_pct is not None and not (0 <= agreed_rate_pct <= 1000):
        raise ValueError("agreed_rate_pct must be between 0 and 1000")
    dates.check_ad_supported(start)
    dates.check_ad_supported(end)
    if end < start:
        raise ValueError("end date cannot be before the start date")
    days = (end - start).days
    years = days / DAYS_IN_YEAR

    provisions = [cite(S_CAP)]
    if not interest_stated_in_instrument:
        rate = 0.0
        basis = {"en": "The instrument does not mention interest, so none is payable (s. 479).", "ne": "लिखतमा ब्याज उल्लेख नभएकाले ब्याज पाइँदैन (दफा ४७९)।"}
        provisions = [cite(S_NOT_STATED)]
    elif agreed_rate_pct is None:
        rate = MAX_ANNUAL_RATE_PCT
        basis = {"en": "No rate is written, so 10% a year applies (s. 478(3)).", "ne": "दर नलेखिएकाले वार्षिक १०% लाग्छ (दफा ४७८(३))।"}
        provisions = [cite(S_DEFAULT)]
    else:
        rate = min(agreed_rate_pct, MAX_ANNUAL_RATE_PCT)
        if agreed_rate_pct > MAX_ANNUAL_RATE_PCT:
            basis = {"en": f"The agreed {agreed_rate_pct:g}% is above the 10% legal maximum, so 10% is used (s. 478(2)).", "ne": f"तोकिएको {agreed_rate_pct:g}% कानूनी सीमा १०% भन्दा बढी भएकाले १०% प्रयोग भएको छ (दफा ४७८(२))।"}
        else:
            basis = {"en": "Agreed rate, within the 10% legal maximum.", "ne": "तोकिएको दर, कानूनी सीमा १०% भित्र।"}

    uncapped = principal * rate / 100 * years
    capped = min(uncapped, principal)
    principal_capped = capped < uncapped
    if principal_capped:
        provisions.append(cite(S_PRINCIPAL_CAP))
    at_agreed = None
    excess = None
    if interest_stated_in_instrument and agreed_rate_pct is not None and agreed_rate_pct > MAX_ANNUAL_RATE_PCT:
        at_agreed = round(principal * agreed_rate_pct / 100 * years, 2)
        excess = round(at_agreed - uncapped, 2)
        provisions.append(cite(S_NO_LIMIT))
    return {
        "principal": round(principal, 2),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "start_date_bs": dates.bs_to_iso(dates.ad_to_bs(start)),
        "end_date_bs": dates.bs_to_iso(dates.ad_to_bs(end)),
        "days": days,
        "years": round(years, 6),
        "rate_applied_pct": rate,
        "interest_npr": round(capped, 2),
        "total_due_npr": round(principal + capped, 2),
        "capped_by_principal": principal_capped,
        "interest_at_agreed_rate_npr": at_agreed,
        "excess_over_legal_max_npr": excess,
        "rate_basis": basis,
        "day_count": {"en": "Actual days / 365 (a convention of this tool; the Code does not prescribe one). Simple interest only - no interest on interest (s. 480).", "ne": "वास्तविक दिन / ३६५ (यस उपकरणको तरिका; संहिताले तोकेको छैन)। साधारण ब्याज मात्र - ब्याजको ब्याज हुँदैन (दफा ४८०)।"},
        "provisions": provisions,
    }
