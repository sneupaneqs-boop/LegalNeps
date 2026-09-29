"""BS <-> AD date conversion and Bikram Sambat date arithmetic (S8).

Nepal's Bikram Sambat calendar has variable month lengths defined by an
official almanac table, not a fixed rule - so this wraps the `nepali_datetime`
package (a maintained BS calendar table) rather than reimplementing that
table by hand, which would be an easy place to get quietly wrong.

The arithmetic helpers (add days/months/years, difference, age) work on the BS
calendar because that is how Nepali law counts time: the Muluki Civil Procedure
Code s. 62 says a limitation given in months is counted by sankranti (BS
calendar months) however many days each month has, and a year is 12 such
months. So "6 months from 15 Baisakh" is 15 Kartik, never "6 x 30 days".
"""
from __future__ import annotations

import dataclasses
import datetime

import nepali_datetime

SUPPORTED_BS_MIN = nepali_datetime.date.min
SUPPORTED_BS_MAX = nepali_datetime.date.max
SUPPORTED_AD_MIN = SUPPORTED_BS_MIN.to_datetime_date()
SUPPORTED_AD_MAX = SUPPORTED_BS_MAX.to_datetime_date()


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


def check_ad_supported(date: datetime.date) -> datetime.date:
    """Raise UnsupportedDate unless `date` lies inside the BS calendar table."""
    if not (SUPPORTED_AD_MIN <= date <= SUPPORTED_AD_MAX):
        raise UnsupportedDate(
            f"{date.isoformat()} A.D. is outside the supported range "
            f"({SUPPORTED_AD_MIN.isoformat()}..{SUPPORTED_AD_MAX.isoformat()} A.D.)"
        )
    return date


def bs_month_length(year: int, month: int) -> int:
    """Number of days in a BS month (29-32; varies by year)."""
    if not (SUPPORTED_BS_MIN.year <= year <= SUPPORTED_BS_MAX.year) or not (1 <= month <= 12):
        raise UnsupportedDate(f"{year}-{month:02d} B.S. is outside the supported range")
    for day in (32, 31, 30, 29):
        try:
            nepali_datetime.date(year, month, day)
            return day
        except ValueError:
            continue
    raise UnsupportedDate(f"{year}-{month:02d} B.S. is outside the supported range")  # pragma: no cover


def bs_to_iso(bs) -> str:
    return f"{bs.year:04d}-{bs.month:02d}-{bs.day:02d}"


def add_days(date: datetime.date, days: int) -> datetime.date:
    """`date` plus (or minus) whole days, kept inside the supported range."""
    try:
        result = date + datetime.timedelta(days=days)
    except OverflowError as exc:
        raise UnsupportedDate("date is outside the supported range") from exc
    return check_ad_supported(result)


def add_bs_months(date: datetime.date, months: int) -> datetime.date:
    """`date` plus N BS calendar months (negative subtracts). The BS day-of-month
    is kept; if the target month is shorter the date is clipped to that month's
    last day (31 Shrawan + 1 month -> 30 or 31 Bhadra as the calendar says)."""
    bs = ad_to_bs(date)
    index = bs.year * 12 + (bs.month - 1) + months
    year, month0 = divmod(index, 12)
    month = month0 + 1
    day = min(bs.day, bs_month_length(year, month))
    return bs_to_ad(year, month, day)


def add_bs_years(date: datetime.date, years: int) -> datetime.date:
    """`date` plus N BS years (12 BS months each), clipped like add_bs_months."""
    return add_bs_months(date, years * 12)


def add_period(date: datetime.date, value: int, unit: str) -> datetime.date:
    """Add a limitation-style period. days -> calendar days, months -> BS months,
    years -> 12 BS months each (Muluki Civil Procedure Code s. 62)."""
    if unit == "days":
        return add_days(date, value)
    if unit == "months":
        return add_bs_months(date, value)
    if unit == "years":
        return add_bs_years(date, value)
    raise ValueError(f"unit must be days, months or years, not {unit!r}")


@dataclasses.dataclass(frozen=True)
class BsDiff:
    """Calendar difference between two dates, counted on the BS calendar."""

    years: int
    months: int
    days: int
    total_days: int
    negative: bool  # True when the second date is before the first


def bs_difference(start: datetime.date, end: datetime.date) -> BsDiff:
    """Whole BS years, months and days from `start` to `end` (order-independent;
    `negative` says whether `end` < `start`), plus the exact number of days.

    Months are the largest whole number of BS months that can be added to the
    earlier date without passing the later one (using the same end-of-month
    clipping as add_bs_months), and the days are what is left over, so adding the
    result back always reproduces the later date."""
    total = (end - start).days
    negative = total < 0
    first, second = (end, start) if negative else (start, end)
    a, b = ad_to_bs(first), ad_to_bs(second)
    months = (b.year - a.year) * 12 + (b.month - a.month)
    if add_bs_months(first, months) > second:
        months -= 1
    shifted = add_bs_months(first, months)
    years, months = divmod(months, 12)
    return BsDiff(years=years, months=months, days=(second - shifted).days, total_days=abs(total), negative=negative)
