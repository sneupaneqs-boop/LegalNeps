"""BS <-> AD date conversion (S8).

Nepal's Bikram Sambat calendar has variable month lengths defined by an
official almanac table, not a fixed rule - so this wraps the `nepali_datetime`
package (a maintained BS calendar table) rather than reimplementing that
table by hand, which would be an easy place to get quietly wrong.
"""
from __future__ import annotations

import datetime

import nepali_datetime

SUPPORTED_BS_MIN = nepali_datetime.date.min
SUPPORTED_BS_MAX = nepali_datetime.date.max


class UnsupportedDate(ValueError):
    """Outside the BS calendar table this build ships with."""


def bs_to_ad(year: int, month: int, day: int) -> datetime.date:
    try:
        return nepali_datetime.date(year, month, day).to_datetime_date()
    except (ValueError, OverflowError) as exc:
        raise UnsupportedDate(
            f"{year}-{month:02d}-{day:02d} B.S. is outside the supported range "
            f"({SUPPORTED_BS_MIN}..{SUPPORTED_BS_MAX} B.S.)"
        ) from exc


def ad_to_bs(date: datetime.date) -> nepali_datetime.date:
    try:
        return nepali_datetime.date.from_datetime_date(date)
    except (ValueError, OverflowError) as exc:
        raise UnsupportedDate(f"{date.isoformat()} A.D. is outside the supported BS range") from exc
