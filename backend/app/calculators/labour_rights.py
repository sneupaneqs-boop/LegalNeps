"""Labour Act, 2074 (श्रम ऐन, २०७४) entitlements: working hours and overtime,
leave, festival allowance, provident fund and gratuity contributions, and the
notice tiers. Everything here is read from the Act's own text - see SOURCES.

Deterministic and bounded: inputs are validated, no external calls. The Act
leaves one thing to other rules that we deliberately do NOT invent: how an
hourly rate is derived from monthly pay. So overtime takes an hourly basic pay,
or a monthly basic pay plus the number of paid days per month *you* state (the
8-hour working day is s. 28(1)).
"""
from __future__ import annotations

import datetime

from . import dates
from .sources import Source, cite

LAB = "श्रम ऐन, २०७४"

S_DAY_HOURS = Source("work_8h_day", LAB, "28", "प्रतिदिन आठ घण्टा", "normal working day: 8 hours")
S_WEEK_HOURS = Source("work_48h_week", LAB, "28", "अठ्चालीस घण्टा", "normal working week: 48 hours")
S_BREAK = Source("work_break", LAB, "28", "लगातार पाँच घण्टा काम गरेपछि आधा घण्टा विश्रामको समय", "30 minute rest after 5 continuous hours")
S_OT_DAY = Source("ot_4h_day", LAB, "30", "प्रतिदिन चार घण्टा", "overtime limit: 4 hours a day")
S_OT_WEEK = Source("ot_24h_week", LAB, "30", "चौबीस घण्टा", "overtime limit: 24 hours a week")
S_OT_RATE = Source("ot_rate", LAB, "31", "डेढी", "overtime is paid at one and a half times (1.5x) the basic pay")
S_FESTIVAL = Source("festival", LAB, "37", "एक महिनाको आधारभूत पारिश्रमिक बराबरको रकम", "festival allowance: one month's basic pay a year")
S_FESTIVAL_PRORATA = Source("festival_prorata", LAB, "37", "सेवा अवधिको अनुपातमा", "less than a year's service: in proportion to the service period")
S_WEEKLY = Source("leave_weekly", LAB, "40", "एक दिन साप्ताहिक बिदा", "one paid weekly day off")
S_PUBLIC = Source("leave_public", LAB, "41", "तेह्र दिन", "13 paid public holidays (14 for women)")
S_PUBLIC_W = Source("leave_public_women", LAB, "41", "चौध दिन", "14 paid public holidays for women workers")
S_SUBSTITUTE = Source("leave_substitute", LAB, "42", "एक्काईस दिनभित्र", "substitute leave within 21 days")
S_HOME = Source("leave_home", LAB, "43", "बीस दिनको एक दिनको दरले", "home leave: 1 day for every 20 days worked")
S_SICK = Source("leave_sick", LAB, "44", "बाह्र दिन", "sick leave: 12 days a year, paid")
S_SICK_CERT = Source("leave_sick_cert", LAB, "44", "लगातार तीन दिनभन्दा बढी", "medical certificate for more than 3 continuous days")
S_MATERNITY = Source("leave_maternity", LAB, "45", "चौध हप्ताको प्रसूति बिदा", "maternity leave: 14 weeks")
S_MAT_BEFORE = Source("leave_maternity_before", LAB, "45", "कम्तीमा दुई हप्ता अगाडिदेखि", "must start at least 2 weeks before the expected delivery")
S_MAT_AFTER = Source("leave_maternity_after", LAB, "45", "कम्तीमा छ हप्तासम्म", "must stay on leave at least 6 weeks after delivery")
S_MAT_PAID = Source("leave_maternity_paid", LAB, "45", "साठी दिनको पूरा पारिश्रमिक", "60 days of maternity leave on full pay")
S_MAT_EXTRA = Source("leave_maternity_extra", LAB, "45", "थप एक महिनासम्मको वेतलबी बिदा", "one more month unpaid leave on a doctor's recommendation")
S_MAT_STILLBIRTH = Source("leave_maternity_stillbirth", LAB, "45", "सात महिना वा सोभन्दा बढी गर्भ", "stillbirth or miscarriage from 7 months: same leave as childbirth")
S_PATERNITY = Source("leave_paternity", LAB, "45", "१५ दिन प्रसूति स्याहार बिदा", "paternity (childbirth care) leave: 15 days, paid")
S_MOURNING = Source("leave_mourning", LAB, "48", "तेह्र दिन किरिया बिदा", "mourning (kriya) leave: 13 days, full pay")
S_CARRY_HOME = Source("leave_carry_home", LAB, "49", "घर बिदा नब्बे दिनसम्म", "home leave can accumulate to 90 days")
S_CARRY_SICK = Source("leave_carry_sick", LAB, "49", "बिरामी बिदा पैँतालीस दिनसम्म", "sick leave can accumulate to 45 days")
S_ENCASH = Source("leave_encash", LAB, "49", "आधारभूत पारिश्रमिकको दरले", "unused accumulated leave is paid at the basic pay rate")
S_PF_EMPLOYEE = Source("pf_employee", LAB, "52", "आधारभूत पारिश्रमिकबाट दश प्रतिशत रकम कट्टा गरी", "employee provident fund: 10% of basic pay")
S_PF_EMPLOYER = Source("pf_employer", LAB, "52", "शतप्रतिशत रकम थप गरी", "employer adds 100% of that (matches it)")
S_GRATUITY = Source("gratuity", LAB, "53", "आठ दशमलव तेत्तीस प्रतिशत", "gratuity: 8.33% of basic pay every month")
S_NOTICE_1 = Source("notice_4w", LAB, "144", "चार हप्तासम्मको रोजगारीको हकमा कम्तीमा एक दिन अगावै", "up to 4 weeks' service: 1 day's notice")
S_NOTICE_7 = Source("notice_1y", LAB, "144", "चार हप्तादेखि एक वर्षसम्मको रोजगारीको हकमा कम्तीमा सात दिन अगावै", "4 weeks to 1 year: 7 days' notice")
S_NOTICE_30 = Source("notice_over_1y", LAB, "144", "एक वर्षभन्दा बढी अवधिको रोजगारीको हकमा कम्तीमा तीस दिन अगावै", "over 1 year: 30 days' notice")

SOURCES = [v for v in list(globals().values()) if isinstance(v, Source)]

DAY_HOURS = 8
WEEK_HOURS = 48
BREAK_AFTER_HOURS = 5
BREAK_MINUTES = 30
OT_MAX_DAY = 4
OT_MAX_WEEK = 24
OT_RATE = 1.5
FESTIVAL_MONTHS = 1
PF_EMPLOYEE_PCT = 10.0
PF_EMPLOYER_PCT = 10.0  # "add 100% of" the employee's 10%
GRATUITY_PCT = 8.33
HOME_LEAVE_DAYS_PER = 20
SICK_LEAVE_DAYS = 12
HOME_LEAVE_CAP = 90
SICK_LEAVE_CAP = 45
MATERNITY_WEEKS = 14
MATERNITY_PAID_DAYS = 60
MATERNITY_MIN_BEFORE_WEEKS = 2
MATERNITY_MIN_AFTER_WEEKS = 6
MATERNITY_EXTRA_MONTH_DAYS = 30  # "one month"; counted as a BS month when dated
PATERNITY_DAYS = 15
MOURNING_DAYS = 13
PUBLIC_HOLIDAYS = 13
PUBLIC_HOLIDAYS_WOMEN = 14


def _money(x: float) -> float:
    return round(x + 0.0, 2)


def _positive(name: str, v: float) -> None:
    if not (v > 0):
        raise ValueError(f"{name} must be positive")


def _non_negative(name: str, v: float) -> None:
    if not (v >= 0):
        raise ValueError(f"{name} cannot be negative")


# ------------------------------------------------------------------ hours & overtime ---

def working_hours_limits() -> dict:
    """The statutory hour limits, as a table."""
    return {
        "normal_day_hours": DAY_HOURS,
        "normal_week_hours": WEEK_HOURS,
        "rest_break": {"after_continuous_hours": BREAK_AFTER_HOURS, "minutes": BREAK_MINUTES},
        "overtime_max_per_day": OT_MAX_DAY,
        "overtime_max_per_week": OT_MAX_WEEK,
        "overtime_rate_multiple": OT_RATE,
        "provisions": [cite(S_DAY_HOURS), cite(S_OT_DAY)],
        "provisions_overtime_pay": [cite(S_OT_RATE)],
    }


def check_hours(hours_per_day: float, hours_per_week: float | None = None, overtime_per_day: float | None = None,
                overtime_per_week: float | None = None) -> dict:
    """Compare a schedule against the limits (s. 28, s. 30)."""
    _positive("hours_per_day", hours_per_day)
    issues = []
    if hours_per_day > DAY_HOURS:
        issues.append({"code": "day_over_8", "limit": DAY_HOURS, "actual": hours_per_day})
    if hours_per_week is not None:
        _positive("hours_per_week", hours_per_week)
        if hours_per_week > WEEK_HOURS:
            issues.append({"code": "week_over_48", "limit": WEEK_HOURS, "actual": hours_per_week})
    if overtime_per_day is not None:
        _non_negative("overtime_per_day", overtime_per_day)
        if overtime_per_day > OT_MAX_DAY:
            issues.append({"code": "overtime_day_over_4", "limit": OT_MAX_DAY, "actual": overtime_per_day})
    if overtime_per_week is not None:
        _non_negative("overtime_per_week", overtime_per_week)
        if overtime_per_week > OT_MAX_WEEK:
            issues.append({"code": "overtime_week_over_24", "limit": OT_MAX_WEEK, "actual": overtime_per_week})
    return {
        "within_limits": not issues,
        "issues": issues,
        "break_needed": hours_per_day > BREAK_AFTER_HOURS,
        "break_minutes": BREAK_MINUTES if hours_per_day > BREAK_AFTER_HOURS else 0,
        "provisions": [cite(S_DAY_HOURS), cite(S_BREAK), cite(S_OT_DAY)],
    }


def overtime_pay(overtime_hours: float, period: str = "day", basic_hourly_pay: float | None = None,
                 basic_monthly_pay: float | None = None, paid_days_per_month: float | None = None) -> dict:
    """Overtime pay at 1.5x the regular hourly basic pay (s. 31), and whether the
    hours are within the 4-a-day / 24-a-week ceiling (s. 30)."""
    _positive("overtime_hours", overtime_hours)
    if period not in ("day", "week"):
        raise ValueError("period must be 'day' or 'week'")
    if basic_hourly_pay is not None:
        _positive("basic_hourly_pay", basic_hourly_pay)
        hourly = float(basic_hourly_pay)
        basis = {"en": "Hourly basic pay as entered.", "ne": "दिइएको प्रति घण्टा आधारभूत पारिश्रमिक।"}
    elif basic_monthly_pay is not None and paid_days_per_month is not None:
        _positive("basic_monthly_pay", basic_monthly_pay)
        _positive("paid_days_per_month", paid_days_per_month)
        hourly = basic_monthly_pay / (paid_days_per_month * DAY_HOURS)
        basis = {
            "en": f"Hourly basic pay = monthly basic pay / ({paid_days_per_month:g} paid days x {DAY_HOURS} hours). The Act does not fix the number of days; this uses the number you entered.",
            "ne": f"प्रति घण्टा आधारभूत पारिश्रमिक = मासिक आधारभूत पारिश्रमिक / ({paid_days_per_month:g} दिन x {DAY_HOURS} घण्टा)। ऐनले दिन संख्या तोकेको छैन; तपाईंले दिएको संख्या प्रयोग भएको छ।",
        }
    else:
        raise ValueError("give basic_hourly_pay, or basic_monthly_pay together with paid_days_per_month")
    rate = hourly * OT_RATE
    limit = OT_MAX_DAY if period == "day" else OT_MAX_WEEK
    return {
        "hourly_basic_pay": round(hourly, 4),
        "overtime_rate_per_hour": round(rate, 4),
        "overtime_pay_npr": _money(rate * overtime_hours),
        "rate_multiple": OT_RATE,
        "hours": overtime_hours,
        "period": period,
        "legal_limit_hours": limit,
        "within_legal_limit": overtime_hours <= limit,
        "hourly_basis": basis,
        "provisions": [cite(S_OT_RATE), cite(S_OT_DAY if period == "day" else S_OT_WEEK)],
    }


# ------------------------------------------------------------------------------- leave ---

def leave_entitlements() -> dict:
    """Every leave entitlement in the Act, as a table (each row cites its section)."""
    def row(id_, days, unit, paid, name_en, name_ne, source, extra=None):
        d = {"id": id_, "days": days, "unit": unit, "paid": paid, "name": {"en": name_en, "ne": name_ne}, "provision": cite(source)}
        if extra:
            d["note"] = extra
        return d

    return {
        "entitlements": [
            row("weekly", 1, "day per week", True, "Weekly day off", "साप्ताहिक बिदा", S_WEEKLY),
            row("public", PUBLIC_HOLIDAYS, "days per year", True, "Public holidays (women: 14)", "सार्वजनिक बिदा (महिला: १४)", S_PUBLIC,
                {"en": "14 days for women workers (including International Women's Day).", "ne": "महिला श्रमिकलाई अन्तर्राष्ट्रिय श्रमिक महिला दिवस सहित १४ दिन।"}),
            row("substitute", 21, "days to give it", True, "Substitute leave for working a weekly/public holiday", "साप्ताहिक/सार्वजनिक बिदामा काम गरेको सट्टा बिदा", S_SUBSTITUTE,
                {"en": "Must be given within 21 days of the work.", "ne": "काम गरेको २१ दिनभित्र दिनुपर्छ।"}),
            row("home", 1, "day per 20 days worked", True, "Home (annual) leave", "घर बिदा", S_HOME),
            row("sick", SICK_LEAVE_DAYS, "days per year", True, "Sick leave", "बिरामी बिदा", S_SICK,
                {"en": "Proportional if you worked a year or less; a doctor's certificate is needed beyond 3 continuous days.", "ne": "एक वर्ष वा कम काम गरेकोमा अनुपातमा; लगातार ३ दिनभन्दा बढीमा चिकित्सकको प्रमाणपत्र चाहिन्छ।"}),
            row("maternity", MATERNITY_WEEKS * 7, "days (14 weeks)", "60 days full pay, the rest unpaid", "Maternity leave", "प्रसूति बिदा", S_MATERNITY,
                {"en": "At least 2 weeks before the expected delivery and 6 weeks after are compulsory.", "ne": "प्रसूतिको सम्भावित मितिभन्दा कम्तीमा २ हप्ता अगाडि र प्रसूतिपछि कम्तीमा ६ हप्ता अनिवार्य बिदा बस्नुपर्छ।"}),
            row("paternity", PATERNITY_DAYS, "days", True, "Paternity (childbirth care) leave", "प्रसूति स्याहार बिदा (पुरुष श्रमिक)", S_PATERNITY),
            row("mourning", MOURNING_DAYS, "days", True, "Mourning (kriya) leave", "किरिया बिदा", S_MOURNING),
        ],
        "accumulation": {
            "home_leave_cap_days": HOME_LEAVE_CAP,
            "sick_leave_cap_days": SICK_LEAVE_CAP,
            "provisions": [cite(S_CARRY_HOME), cite(S_CARRY_SICK)],
        },
    }


def leave_accrual(days_worked: float, months_worked_in_year: float | None = None) -> dict:
    """Home leave earned (1 per 20 days worked, s. 43) and the sick-leave
    entitlement for the year (12 days, proportional for a part-year, s. 44)."""
    _non_negative("days_worked", days_worked)
    home = days_worked / HOME_LEAVE_DAYS_PER
    out = {
        "home_leave_days": round(home, 2),
        "home_leave_whole_days": int(home),
        "home_leave_cap_days": HOME_LEAVE_CAP,
        "home_leave_over_cap_days": round(max(0.0, home - HOME_LEAVE_CAP), 2),
        "provisions": [cite(S_HOME), cite(S_CARRY_HOME)],
    }
    if months_worked_in_year is not None:
        _non_negative("months_worked_in_year", months_worked_in_year)
        m = min(months_worked_in_year, 12.0)
        out["sick_leave_days"] = round(SICK_LEAVE_DAYS * m / 12, 2)
        out["sick_leave_cap_days"] = SICK_LEAVE_CAP
        out["provisions"] += [cite(S_SICK), cite(S_CARRY_SICK)]
    return out


def leave_encashment(home_leave_days: float, sick_leave_days: float, daily_basic_pay: float) -> dict:
    """Pay for accumulated leave when service ends (s. 49(2)), at the last basic
    pay rate. Home leave is counted up to the 90-day cap and sick leave up to the
    45-day cap (the excess over a cap is paid out at each year's end, s. 49(3))."""
    _non_negative("home_leave_days", home_leave_days)
    _non_negative("sick_leave_days", sick_leave_days)
    _positive("daily_basic_pay", daily_basic_pay)
    home = min(home_leave_days, HOME_LEAVE_CAP)
    sick = min(sick_leave_days, SICK_LEAVE_CAP)
    return {
        "home_leave_days_counted": home,
        "sick_leave_days_counted": sick,
        "amount_npr": _money((home + sick) * daily_basic_pay),
        "provisions": [cite(S_ENCASH), cite(S_CARRY_HOME), cite(S_CARRY_SICK)],
    }


def maternity_leave(expected_delivery: datetime.date, leave_start: datetime.date | None = None,
                    extra_month_recommended: bool = False) -> dict:
    """Dates for maternity leave from the expected delivery date (s. 45): 14 weeks
    in total, on leave from at least 2 weeks before the expected date to at
    least 6 weeks after delivery, the first 60 days on full pay."""
    dates.check_ad_supported(expected_delivery)
    latest_start = dates.add_days(expected_delivery, -MATERNITY_MIN_BEFORE_WEEKS * 7)
    min_end = dates.add_days(expected_delivery, MATERNITY_MIN_AFTER_WEEKS * 7)
    start = leave_start or latest_start
    dates.check_ad_supported(start)
    total_days = MATERNITY_WEEKS * 7
    end = dates.add_days(start, total_days - 1)  # 14 weeks counted with the start day included
    paid_until = dates.add_days(start, MATERNITY_PAID_DAYS - 1)
    warnings = []
    if start > latest_start:
        warnings.append("start_after_latest_start")
    if end < min_end:
        warnings.append("ends_before_six_weeks_after_expected_delivery")
    result = {
        "expected_delivery": expected_delivery.isoformat(),
        "latest_start": latest_start.isoformat(),
        "minimum_leave_until": min_end.isoformat(),
        "leave_start": start.isoformat(),
        "leave_end": end.isoformat(),
        "leave_end_bs": dates.bs_to_iso(dates.ad_to_bs(end)),
        "leave_start_bs": dates.bs_to_iso(dates.ad_to_bs(start)),
        "total_days": total_days,
        "full_pay_days": MATERNITY_PAID_DAYS,
        "full_pay_until": paid_until.isoformat(),
        "unpaid_days": total_days - MATERNITY_PAID_DAYS,
        "paternity_days": PATERNITY_DAYS,
        "warnings": warnings,
        "extra_unpaid_month": None,
        "provisions": [cite(S_MATERNITY), cite(S_MAT_BEFORE), cite(S_MAT_AFTER), cite(S_MAT_PAID), cite(S_PATERNITY)],
    }
    if extra_month_recommended:
        extra_end = dates.add_bs_months(dates.add_days(end, 1), 1)
        extra_end = dates.add_days(extra_end, -1)
        result["extra_unpaid_month"] = {"from": dates.add_days(end, 1).isoformat(), "to": extra_end.isoformat()}
        result["provisions"].append(cite(S_MAT_EXTRA))
    return result


# --------------------------------------------------------------- pay-related amounts ---

def festival_allowance(basic_monthly_pay: float, months_of_service: float = 12) -> dict:
    """Festival allowance (चाडपर्व खर्च, s. 37): one month's basic pay a year;
    in proportion to service if under a year by the payment date."""
    _positive("basic_monthly_pay", basic_monthly_pay)
    _non_negative("months_of_service", months_of_service)
    fraction = min(months_of_service, 12.0) / 12.0
    return {
        "amount_npr": _money(basic_monthly_pay * FESTIVAL_MONTHS * fraction),
        "fraction_of_year": round(fraction, 4),
        "payable_at": {"en": "Dashain, unless you ask in writing to be paid at another main festival of your own religion or culture (once a financial year).", "ne": "लिखित अनुरोध नगरेमा प्रत्येक वर्षको बडादशैंमा।"},
        "provisions": [cite(S_FESTIVAL), cite(S_FESTIVAL_PRORATA)],
    }


def fund_contributions(basic_monthly_pay: float, months: float = 1) -> dict:
    """Monthly provident fund (10% from the worker + 10% matched by the employer,
    s. 52) and gratuity (8.33% by the employer, s. 53) on basic pay."""
    _positive("basic_monthly_pay", basic_monthly_pay)
    _positive("months", months)
    pf_emp = basic_monthly_pay * PF_EMPLOYEE_PCT / 100
    pf_er = basic_monthly_pay * PF_EMPLOYER_PCT / 100
    grat = basic_monthly_pay * GRATUITY_PCT / 100
    m = months
    return {
        "months": months,
        "monthly": {
            "employee_pf_npr": _money(pf_emp),
            "employer_pf_npr": _money(pf_er),
            "employer_gratuity_npr": _money(grat),
            "total_deposit_npr": _money(pf_emp + pf_er + grat),
            "employer_cost_npr": _money(pf_er + grat),
        },
        "period_total": {
            "employee_pf_npr": _money(pf_emp * m),
            "employer_pf_npr": _money(pf_er * m),
            "employer_gratuity_npr": _money(grat * m),
            "total_deposit_npr": _money((pf_emp + pf_er + grat) * m),
            "employer_cost_npr": _money((pf_er + grat) * m),
        },
        "rates_pct": {"employee_pf": PF_EMPLOYEE_PCT, "employer_pf": PF_EMPLOYER_PCT, "gratuity": GRATUITY_PCT},
        "note": {
            "en": "These are the Labour Act rates on basic pay, deposited in the Social Security Fund (or, until it operates for the employer, as the Rules say). The Social Security Act leaves the fund's own contribution rate to a gazette notice that is not in the corpus.",
            "ne": "यी श्रम ऐनका आधारभूत पारिश्रमिकमा लाग्ने दर हुन्, जुन सामाजिक सुरक्षा कोषमा जम्मा हुन्छन्। योगदानमा आधारित सामाजिक सुरक्षा ऐनले कोषको आफ्नै योगदान दर नेपाल राजपत्रको सूचनाबाट तोक्ने भनेको छ, जुन यहाँ उपलब्ध छैन।",
        },
        "provisions": [cite(S_PF_EMPLOYEE), cite(S_PF_EMPLOYER), cite(S_GRATUITY)],
    }


def notice_tiers() -> dict:
    """The minimum notice before ending employment, by length of service (s. 144)."""
    return {
        "tiers": [
            {"service": {"en": "up to 4 weeks", "ne": "चार हप्तासम्म"}, "notice_days": 1, "provision": cite(S_NOTICE_1)},
            {"service": {"en": "4 weeks to 1 year", "ne": "चार हप्तादेखि एक वर्षसम्म"}, "notice_days": 7, "provision": cite(S_NOTICE_7)},
            {"service": {"en": "more than 1 year", "ne": "एक वर्षभन्दा बढी"}, "notice_days": 30, "provision": cite(S_NOTICE_30)},
        ],
        "note": {
            "en": "Applies to either side ending the employment, except a dismissal for misconduct. If the employer skips it, the pay for the notice period is due (s. 144(2)).",
            "ne": "खराब आचरणमा कारबाही भई रोजगारी अन्त्य भएकोमा बाहेक रोजगारदाता वा श्रमिक जसले अन्त्य गरे पनि लागू हुन्छ। रोजगारदाताले सूचना नदिए सो अवधिको पारिश्रमिक दिनुपर्छ।",
        },
    }
