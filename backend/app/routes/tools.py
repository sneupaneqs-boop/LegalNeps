"""Legal tools API (S8 follow-up): the limitation-period catalog and deadline
calculator, labour entitlements, interest, tax, court fees and date tools.

Every endpoint is a public, unauthenticated GET that does a small deterministic
calculation, so every input is bounded: numbers by Query ge/gt/le, dates by a
strict YYYY-MM-DD pattern plus the supported Bikram Sambat range (BS 1975-2100),
and unknown ids by an allow-list. Domain problems (a date outside the calendar
table, end before start, ...) come back as 400 with a plain message; malformed
or out-of-bound parameters as FastAPI's usual 422.

Every result carries `provisions` (or `provision`): the corpus sections each
number was read from, resolved by app.playbooks.resolve_provision.
"""
from __future__ import annotations

import asyncio
import datetime
import functools
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query

from ..calculators import age as age_calc
from ..calculators import court_fee as court_fee_calc
from ..calculators import datetools as datetools_calc
from ..calculators import dates as date_calc
from ..calculators import interest as interest_calc
from ..calculators import labour_rights as labour_rights_calc
from ..calculators import limitation as limitation_calc
from ..calculators import tax as tax_calc

router = APIRouter(tags=["tools"])

MAX_MONEY = 1_000_000_000_000.0

Money = Annotated[float, Query(gt=0, le=MAX_MONEY)]
MoneyOrZero = Annotated[float, Query(ge=0, le=MAX_MONEY)]
DateParam = Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$", max_length=10)]
Calendar = Annotated[Literal["ad", "bs"], Query()]


def _bad(exc: Exception) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


def _date(value: str, calendar: str) -> datetime.date:
    """An AD (ISO) or BS ('YYYY-MM-DD' read as a BS date) date inside the supported range."""
    try:
        if calendar == "bs":
            y, m, d = (int(p) for p in value.split("-"))
            return date_calc.bs_to_ad(y, m, d)
        return date_calc.check_ad_supported(datetime.date.fromisoformat(value))
    except date_calc.UnsupportedDate as exc:
        raise _bad(exc)
    except ValueError as exc:
        raise _bad(ValueError(f"{value!r} is not a valid {calendar.upper()} date ({exc})"))


async def _run(fn, *args, **kwargs):
    """Run a calculation off the event loop; ValueError -> 400."""
    try:
        return await asyncio.to_thread(functools.partial(fn, *args, **kwargs))
    except date_calc.UnsupportedDate as exc:
        raise _bad(exc)
    except ValueError as exc:
        raise _bad(exc)


# ------------------------------------------------------------------------ limitation ---

@functools.lru_cache(maxsize=1)
def _catalog() -> dict:
    return limitation_calc.catalog()


@router.get("/calculators/limitation/catalog")
async def limitation_catalog() -> dict:
    """Every limitation-period entry (about 230), grouped by category, each with its
    period, what starts the clock, notes and a resolved citation."""
    return await asyncio.to_thread(_catalog)


@router.get("/calculators/limitation/deadline")
async def limitation_deadline(
    claim_id: Annotated[str, Query(min_length=1, max_length=100, pattern=r"^[a-z0-9_]+$")],
    trigger_date: DateParam,
    calendar: Calendar = "ad",
    long_stop_date: DateParam | None = None,
    as_of: DateParam | None = None,
) -> dict:
    """Deadline for any catalog entry with a fixed period. `trigger_date` is when the
    clock starts (AD, or BS with calendar=bs); `long_stop_date` is the start of the
    outer limit some entries have (e.g. the date an instrument was passed); `as_of`
    replaces today's date."""
    trigger = _date(trigger_date, calendar)
    long_stop = _date(long_stop_date, calendar) if long_stop_date else None
    today = _date(as_of, calendar) if as_of else None
    try:
        await asyncio.to_thread(limitation_calc.get_entry, claim_id)  # 404 for an id that is not in the catalog
    except limitation_calc.UnknownClaimType as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return await _run(limitation_calc.check, claim_id, trigger, today=today, long_stop_trigger_date=long_stop)


# ------------------------------------------------------------------------------ labour ---

@router.get("/calculators/labour/hours")
async def labour_hours_limits() -> dict:
    """Normal working hours, the rest break and overtime ceilings (Labour Act ss. 28, 30, 31)."""
    return await _run(labour_rights_calc.working_hours_limits)


@router.get("/calculators/labour/hours/check")
async def labour_hours_check(
    hours_per_day: Annotated[float, Query(gt=0, le=24)],
    hours_per_week: Annotated[float | None, Query(gt=0, le=168)] = None,
    overtime_per_day: Annotated[float | None, Query(ge=0, le=24)] = None,
    overtime_per_week: Annotated[float | None, Query(ge=0, le=168)] = None,
) -> dict:
    return await _run(labour_rights_calc.check_hours, hours_per_day, hours_per_week, overtime_per_day, overtime_per_week)


@router.get("/calculators/labour/overtime")
async def labour_overtime(
    overtime_hours: Annotated[float, Query(gt=0, le=168)],
    period: Annotated[Literal["day", "week"], Query()] = "day",
    basic_hourly_pay: Annotated[float | None, Query(gt=0, le=MAX_MONEY)] = None,
    basic_monthly_pay: Annotated[float | None, Query(gt=0, le=MAX_MONEY)] = None,
    paid_days_per_month: Annotated[float | None, Query(gt=0, le=31)] = None,
) -> dict:
    """Overtime pay at 1.5x basic pay (s. 31). Give the hourly basic pay, or the monthly
    basic pay with the paid days per month you use."""
    return await _run(
        labour_rights_calc.overtime_pay, overtime_hours, period, basic_hourly_pay, basic_monthly_pay, paid_days_per_month
    )


@router.get("/calculators/labour/leave")
async def labour_leave() -> dict:
    """The Act's leave entitlements (weekly, public, home, sick, maternity, paternity, mourning)."""
    return await _run(labour_rights_calc.leave_entitlements)


@router.get("/calculators/labour/leave/accrual")
async def labour_leave_accrual(
    days_worked: Annotated[float, Query(ge=0, le=40000)],
    months_worked_in_year: Annotated[float | None, Query(ge=0, le=1200)] = None,
) -> dict:
    return await _run(labour_rights_calc.leave_accrual, days_worked, months_worked_in_year)


@router.get("/calculators/labour/leave/encashment")
async def labour_leave_encashment(
    home_leave_days: Annotated[float, Query(ge=0, le=100000)],
    sick_leave_days: Annotated[float, Query(ge=0, le=100000)],
    daily_basic_pay: Money,
) -> dict:
    return await _run(labour_rights_calc.leave_encashment, home_leave_days, sick_leave_days, daily_basic_pay)


@router.get("/calculators/labour/maternity")
async def labour_maternity(
    expected_delivery: DateParam,
    calendar: Calendar = "ad",
    leave_start: DateParam | None = None,
    extra_month_recommended: bool = False,
) -> dict:
    """Maternity leave dates from the expected delivery date (s. 45)."""
    edd = _date(expected_delivery, calendar)
    start = _date(leave_start, calendar) if leave_start else None
    return await _run(labour_rights_calc.maternity_leave, edd, start, extra_month_recommended)


@router.get("/calculators/labour/festival-allowance")
async def labour_festival_allowance(
    basic_monthly_pay: Money,
    months_of_service: Annotated[float, Query(ge=0, le=1200)] = 12,
) -> dict:
    return await _run(labour_rights_calc.festival_allowance, basic_monthly_pay, months_of_service)


@router.get("/calculators/labour/fund-contributions")
async def labour_fund_contributions(
    basic_monthly_pay: Money,
    months: Annotated[float, Query(gt=0, le=1200)] = 1,
) -> dict:
    """Provident fund and gratuity contributions on basic pay (ss. 52, 53)."""
    return await _run(labour_rights_calc.fund_contributions, basic_monthly_pay, months)


@router.get("/calculators/labour/notice-tiers")
async def labour_notice_tiers() -> dict:
    return await _run(labour_rights_calc.notice_tiers)


# ---------------------------------------------------------------------------- interest ---

@router.get("/calculators/interest/rules")
async def interest_rules() -> dict:
    """The lawful maximum interest on a private loan and the rules around it (Civil Code ss. 478-481)."""
    return await _run(interest_calc.max_lawful_rate)


@router.get("/calculators/interest/simple")
async def interest_simple(
    principal: Money,
    start_date: DateParam,
    end_date: DateParam,
    calendar: Calendar = "ad",
    rate: Annotated[float | None, Query(ge=0, le=1000)] = None,
    interest_stated: bool = True,
) -> dict:
    """Simple interest with the 10% a year legal cap. `rate` is the yearly rate written in
    the loan instrument (omit it if interest is payable but no rate is written);
    `interest_stated=false` means the instrument does not mention interest."""
    start = _date(start_date, calendar)
    end = _date(end_date, calendar)
    return await _run(interest_calc.simple_interest, principal, start, end, rate, interest_stated)


# ------------------------------------------------------------------------------- tax ---

@router.get("/calculators/tax/income")
async def tax_income(
    taxable_income: MoneyOrZero,
    resident: bool = True,
    first_slab_exempt: bool = False,
    insurance_premium: MoneyOrZero = 0,
    remote_allowance: MoneyOrZero = 0,
    disabled: bool = False,
    woman_salary_only: bool = False,
) -> dict:
    """Annual income tax for a resident individual/couple (Income Tax Act Schedule 1) or a non-resident."""
    return await _run(
        tax_calc.income_tax, taxable_income, resident, first_slab_exempt, insurance_premium, remote_allowance, disabled,
        woman_salary_only,
    )


@router.get("/calculators/tax/tds-types")
async def tax_tds_types() -> list[dict]:
    return await _run(tax_calc.tds_types)


@router.get("/calculators/tax/tds")
async def tax_tds(
    payment_type: Annotated[str, Query(min_length=1, max_length=60, pattern=r"^[a-z0-9_]+$")],
    amount: Money,
    aggregated_amount: Annotated[float | None, Query(gt=0, le=MAX_MONEY)] = None,
) -> dict:
    return await _run(tax_calc.tds, payment_type, amount, aggregated_amount)


# ----------------------------------------------------------------------------- court fee ---

@router.get("/calculators/court-fee/flat-types")
async def court_fee_flat_types() -> list[dict]:
    return await _run(court_fee_calc.flat_fee_types)


@router.get("/calculators/court-fee/flat")
async def court_fee_flat(case_type: Annotated[str, Query(min_length=1, max_length=60, pattern=r"^[a-z0-9_]+$")]) -> dict:
    return await _run(court_fee_calc.flat_fee, case_type)


@router.get("/calculators/court-fee/review")
async def court_fee_review(contested_value: Money) -> dict:
    return await _run(court_fee_calc.review_fee, contested_value)


@router.get("/calculators/court-fee/settlement")
async def court_fee_settlement(fee_paid: Money, before_evidence: bool = True) -> dict:
    return await _run(court_fee_calc.settlement_fee, fee_paid, before_evidence)


# ---------------------------------------------------------------------------------- dates ---

@router.get("/calculators/date/add")
async def date_add(
    date: DateParam,
    calendar: Calendar = "bs",
    years: Annotated[int, Query(ge=-300, le=300)] = 0,
    months: Annotated[int, Query(ge=-3600, le=3600)] = 0,
    days: Annotated[int, Query(ge=-110000, le=110000)] = 0,
) -> dict:
    """Add (or subtract) years, months and days to a date. Years and months are BS calendar
    months (a year is 12 of them, clipped to the end of a shorter month); they are applied
    first, then the days."""
    start = _date(date, calendar)
    return await _run(datetools_calc.add_to_date, start, years, months, days)


@router.get("/calculators/date/difference")
async def date_difference(start: DateParam, end: DateParam, calendar: Calendar = "bs") -> dict:
    """Years, months and days between two dates on the BS calendar, and the exact number of days."""
    a = _date(start, calendar)
    b = _date(end, calendar)
    return await _run(datetools_calc.difference, a, b)


@router.get("/calculators/date/age")
async def date_age(birth_date: DateParam, calendar: Calendar = "bs", as_of: DateParam | None = None) -> dict:
    """Age on a date (default today) and when the person reaches 10, 18 and 20 (capacity,
    majority / consent age, marriage age)."""
    birth = _date(birth_date, calendar)
    on = _date(as_of, calendar) if as_of else datetime.date.today()
    return await _run(age_calc.age_on, birth, on)


@router.get("/calculators/date/age-markers")
async def date_age_markers() -> list[dict]:
    return await _run(age_calc.markers_table)
