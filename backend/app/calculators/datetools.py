"""BS date arithmetic tools: add years/months/days to a date, and the difference
between two dates. The counting convention is the one Nepali law itself uses for
limitation periods (Muluki Civil Procedure Code, 2074, s. 62): months are Bikram
Sambat calendar months however many days they have, and a year is 12 such months.
"""
from __future__ import annotations

import datetime

from . import dates
from .sources import Source, cite

S_COUNTING = Source(
    "counting_months",
    "मुलुकी देवानी कार्यविधि संहिता, २०७४",
    "62",
    "जति दिनको महिना भएपनि सक्रान्तिको हिसाबले जति महिना तोकिएको हो त्यति नै महिनाको हिसाबले गणना गर्नु पर्नेछ",
    "months are counted as Bikram Sambat calendar months, however many days each has",
)
S_COUNTING_YEAR = Source(
    "counting_year",
    "मुलुकी देवानी कार्यविधि संहिता, २०७४",
    "62",
    "बाह्र महिनाको अवधिलाई एक वर्ष मानी",
    "a year is 12 months",
)

SOURCES = [S_COUNTING, S_COUNTING_YEAR]

COUNTING_NOTE = {
    "en": "Months and years are Bikram Sambat calendar months (Civil Procedure Code s. 62), not 30-day blocks; a year is 12 of them. Years and months are applied first, then days.",
    "ne": "महिना र वर्ष वि.सं. महिना अनुसार गनिन्छ (देवानी कार्यविधि संहिता दफा ६२), ३० दिनको खण्डमा होइन; वर्ष १२ महिनाको। पहिले वर्ष र महिना, त्यसपछि दिन जोडिन्छ।",
}


def _pair(d: datetime.date) -> dict:
    return {"ad": d.isoformat(), "bs": dates.bs_to_iso(dates.ad_to_bs(d))}


def add_to_date(start: datetime.date, years: int = 0, months: int = 0, days: int = 0) -> dict:
    """`start` plus years, months (BS calendar) then days; negatives go back."""
    dates.check_ad_supported(start)
    moved = dates.add_bs_months(start, years * 12 + months)
    result = dates.add_days(moved, days)
    return {
        "start": start.isoformat(),
        "start_bs": _pair(start)["bs"],
        "result": result.isoformat(),
        "result_bs": _pair(result)["bs"],
        "added": {"years": years, "months": months, "days": days},
        "counting_note": COUNTING_NOTE,
        "provisions": [cite(S_COUNTING), cite(S_COUNTING_YEAR)],
    }


def difference(start: datetime.date, end: datetime.date) -> dict:
    """Whole BS years, months and days between two dates, plus the exact day count."""
    dates.check_ad_supported(start)
    dates.check_ad_supported(end)
    diff = dates.bs_difference(start, end)
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "start_bs": _pair(start)["bs"],
        "end_bs": _pair(end)["bs"],
        "years": diff.years,
        "months": diff.months,
        "days": diff.days,
        "total_days": diff.total_days,
        "end_is_before_start": diff.negative,
        "counting_note": COUNTING_NOTE,
        "provisions": [cite(S_COUNTING)],
    }
