"""S8: BS<->AD dates, limitation-period checker, court fee, and Labour Act
gratuity/notice/severance calculators. Table-driven per STRATEGY's "done
when" bar for this session.

Limitation/court-fee/labour tests marked `requires_corpus` hit the real
built corpus (via app.playbooks.resolve_provision), same reasoning as
tests/test_playbooks.py: a calculator citing a section the corpus can't
find should fail loudly, not silently.
"""
import datetime

import pytest

from app.calculators import court_fee, dates, labour, limitation
from app.retrieval import CORPUS_DIR

requires_corpus = pytest.mark.skipif(
    not (CORPUS_DIR / "manifest.json").exists(), reason="built corpus shards not present"
)


# ---------------------------------------------------------------- dates ----

BS_AD_PAIRS = [
    (2081, 1, 1, datetime.date(2024, 4, 13)),
    (2080, 1, 1, datetime.date(2023, 4, 14)),
    (2075, 1, 1, datetime.date(2018, 4, 14)),
    (2079, 9, 15, datetime.date(2022, 12, 30)),
]


@pytest.mark.parametrize("by, bm, bd, ad", BS_AD_PAIRS)
def test_bs_to_ad(by, bm, bd, ad):
    assert dates.bs_to_ad(by, bm, bd) == ad


@pytest.mark.parametrize("by, bm, bd, ad", BS_AD_PAIRS)
def test_ad_to_bs_roundtrip(by, bm, bd, ad):
    bs = dates.ad_to_bs(ad)
    assert (bs.year, bs.month, bs.day) == (by, bm, bd)


def test_bs_to_ad_rejects_impossible_date():
    with pytest.raises(dates.UnsupportedDate):
        dates.bs_to_ad(2081, 13, 1)


def test_ad_to_bs_rejects_out_of_range():
    with pytest.raises(dates.UnsupportedDate):
        dates.ad_to_bs(datetime.date(1800, 1, 1))


# ------------------------------------------------------------ limitation ----

LIMITATION_CASES = [
    # claim_type, trigger_date, today, expect_time_barred
    ("contract_civil_claim", datetime.date(2023, 1, 1), datetime.date(2024, 6, 1), False),
    ("contract_civil_claim", datetime.date(2020, 1, 1), datetime.date(2024, 6, 1), True),
    ("partition_disagreement", datetime.date(2026, 1, 1), datetime.date(2026, 2, 1), False),
    ("partition_disagreement", datetime.date(2026, 1, 1), datetime.date(2026, 5, 1), True),
    ("labour_dispute_complaint", datetime.date(2026, 1, 1), datetime.date(2026, 3, 1), False),
    ("labour_dispute_complaint", datetime.date(2026, 1, 1), datetime.date(2026, 9, 1), True),
    ("foreign_employment_complaint", datetime.date(2025, 1, 1), datetime.date(2025, 6, 1), False),
    ("foreign_employment_complaint", datetime.date(2023, 1, 1), datetime.date(2025, 6, 1), True),
    ("cheque_dishonour_complaint", datetime.date(2025, 1, 1), datetime.date(2025, 6, 1), False),
    ("cheque_dishonour_complaint", datetime.date(2023, 1, 1), datetime.date(2025, 6, 1), True),
]


@requires_corpus
@pytest.mark.parametrize("claim_type, trigger, today, expect_barred", LIMITATION_CASES)
def test_limitation_check(claim_type, trigger, today, expect_barred):
    result = limitation.check(claim_type, trigger, today=today)
    assert result["is_time_barred"] is expect_barred
    assert result["provision"]["citation"]


@requires_corpus
def test_limitation_unknown_claim_type_raises():
    with pytest.raises(limitation.UnknownClaimType):
        limitation.check("not_a_real_claim", datetime.date.today())


def test_limitation_deadline_math_months():
    # Months are Bikram Sambat months (Civil Procedure Code s. 62): 2026-01-31 AD is 2082-10-17 B.S.,
    # so 6 months on is 2083-04-17 B.S. = 2026-08-02 AD (no corpus needed for the date math itself)
    from app.calculators.limitation import _add_period
    assert _add_period(datetime.date(2026, 1, 31), 6, "months") == datetime.date(2026, 8, 2)


def test_limitation_deadline_math_clips_short_month():
    from app.calculators.limitation import _add_period
    # 31 Bhadra 2081 B.S. + 1 month: Ashwin 2081 has only 30 days, so it lands on 30 Ashwin, not an invalid 31
    start = dates.bs_to_ad(2081, 5, 31)
    end = _add_period(start, 1, "months")
    assert (dates.ad_to_bs(end).year, dates.ad_to_bs(end).month, dates.ad_to_bs(end).day) == (2081, 6, 30)


# ------------------------------------------------------------- court fee ----

COURT_FEE_CASES = [
    (10_000, 500.0),
    (25_000, 500.0),
    (50_000, 1750.0),
    (100_000, 3500.0),
    (500_000, 11500.0),
    (2_500_000, 41500.0),
    (3_500_000, 51500.0),
]


@pytest.mark.parametrize("claim_value, expected_fee", COURT_FEE_CASES)
def test_court_fee_brackets(claim_value, expected_fee):
    assert court_fee.court_fee(claim_value) == expected_fee


def test_court_fee_rejects_non_positive_value():
    with pytest.raises(ValueError):
        court_fee.court_fee(0)


def test_appeal_fee_is_15_percent_of_court_fee():
    assert court_fee.appeal_fee(50_000) == pytest.approx(1750.0 * 0.15)


@requires_corpus
def test_court_fee_estimate_includes_citations():
    result = court_fee.estimate(50_000)
    assert result["filing_fee_npr"] == 200.0
    assert result["court_fee_npr"] == 1750.0
    assert result["total_npr"] == 1950.0
    assert result["filing_fee_provision"]["citation"]
    assert result["court_fee_provision"]["citation"]


@requires_corpus
def test_court_fee_estimate_appeal():
    result = court_fee.estimate_appeal(50_000)
    assert result["appeal_fee_npr"] == pytest.approx(1750.0 * 0.15)
    assert result["provision"]["citation"]


# -------------------------------------------------------------- labour -----

GRATUITY_CASES = [
    (30_000, 12, round(30_000 * 0.0833 * 12, 2)),
    (50_000, 6, round(50_000 * 0.0833 * 6, 2)),
    (20_000, 0, 0.0),
]


@requires_corpus
@pytest.mark.parametrize("basic_pay, months, expected", GRATUITY_CASES)
def test_gratuity(basic_pay, months, expected):
    result = labour.gratuity(basic_pay, months)
    assert result["amount_npr"] == expected
    assert result["provision"]["citation"]


NOTICE_CASES = [
    (10, 1),     # <= 4 weeks
    (28, 1),
    (29, 7),     # 4 weeks to 1 year
    (365, 7),
    (366, 30),   # > 1 year
    (3000, 30),
]


@pytest.mark.parametrize("service_days, expected_days", NOTICE_CASES)
def test_notice_period_days(service_days, expected_days):
    assert labour.notice_period_days(service_days) == expected_days


@requires_corpus
def test_notice_pay_in_lieu():
    result = labour.notice(400, daily_wage=1000.0)
    assert result["notice_period_days"] == 30
    assert result["pay_in_lieu_npr"] == 30_000.0
    assert result["provision"]["citation"]


SEVERANCE_CASES = [
    (30_000, 5, 150_000.0),
    (40_000, 0.5, 20_000.0),
    (25_000, 0, 0.0),
]


@requires_corpus
@pytest.mark.parametrize("basic_pay, years, expected", SEVERANCE_CASES)
def test_severance(basic_pay, years, expected):
    result = labour.severance(basic_pay, years)
    assert result["amount_npr"] == expected
    assert result["provision"]["citation"]


def test_labour_calculators_reject_invalid_inputs():
    with pytest.raises(ValueError):
        labour.gratuity(-1, 5)
    with pytest.raises(ValueError):
        labour.notice(5, daily_wage=0)
    with pytest.raises(ValueError):
        labour.severance(10_000, -1)


# --------------------------------------------------------------- API -------

@requires_corpus
def test_calculator_api_endpoints():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        r = c.get("/api/calculators/date/bs-to-ad", params={"year": 2081, "month": 1, "day": 1})
        assert r.status_code == 200
        assert r.json()["ad"] == "2024-04-13"

        r = c.get("/api/calculators/date/ad-to-bs", params={"date": "2024-04-13"})
        assert r.status_code == 200
        assert r.json()["bs"] == {"year": 2081, "month": 1, "day": 1}

        assert c.get("/api/calculators/date/bs-to-ad", params={"year": 2081, "month": 13, "day": 1}).status_code == 400

        r = c.get("/api/calculators/limitation/claim-types")
        assert r.status_code == 200
        assert "contract_civil_claim" in r.json()

        r = c.get("/api/calculators/limitation",
                   params={"claim_type": "contract_civil_claim", "trigger_date": "2023-01-01"})
        assert r.status_code == 200
        assert r.json()["deadline"] == "2025-01-01"

        assert c.get("/api/calculators/limitation",
                      params={"claim_type": "nonsense", "trigger_date": "2023-01-01"}).status_code == 400

        r = c.get("/api/calculators/court-fee", params={"claim_value": 50_000})
        assert r.status_code == 200
        assert r.json()["total_npr"] == 1950.0

        r = c.get("/api/calculators/labour/gratuity", params={"basic_monthly_pay": 30_000, "months_of_service": 12})
        assert r.status_code == 200
        assert r.json()["amount_npr"] == round(30_000 * 0.0833 * 12, 2)

        r = c.get("/api/calculators/labour/notice", params={"service_days": 400, "daily_wage": 1000})
        assert r.status_code == 200
        assert r.json()["notice_period_days"] == 30

        r = c.get("/api/calculators/labour/severance", params={"basic_monthly_pay": 30_000, "years_of_service": 5})
        assert r.status_code == 200
        assert r.json()["amount_npr"] == 150_000.0


@requires_corpus
def test_calculator_api_rejects_nan_and_infinity_instead_of_500():
    """Regression (prod audit): nan/inf/1e999 parsed as floats, the result could not be
    serialised to JSON and the endpoints answered 500."""
    from fastapi.testclient import TestClient

    from app.main import app

    cases = [
        ("/api/calculators/court-fee", {"claim_value": "{}"}),
        ("/api/calculators/court-fee/appeal", {"disputed_value": "{}"}),
        ("/api/calculators/labour/gratuity", {"basic_monthly_pay": "{}", "months_of_service": 12}),
        ("/api/calculators/labour/gratuity", {"basic_monthly_pay": 30_000, "months_of_service": "{}"}),
        ("/api/calculators/labour/notice", {"service_days": 400, "daily_wage": "{}"}),
        ("/api/calculators/labour/severance", {"basic_monthly_pay": "{}", "years_of_service": 5}),
        ("/api/calculators/labour/severance", {"basic_monthly_pay": 30_000, "years_of_service": "{}"}),
    ]
    with TestClient(app, raise_server_exceptions=False) as c:
        for path, params in cases:
            for bad in ("nan", "inf", "-inf", "1e999"):
                q = {k: (bad if v == "{}" else v) for k, v in params.items()}
                r = c.get(path, params=q)
                assert 400 <= r.status_code < 500, (path, q, r.status_code)
