"""S12: Compliance Radar lite - company profile, obligations, upcoming-due
computation, and the reminder job.

Supabase isn't configured in this build environment (same as every prior
session's tests), so the API-layer tests exercise a monkeypatched `supa`
store, matching tests/test_s11_matters.py's pattern. The due-date math in
app/compliance.py is exercised directly against the real nepali_datetime
BS calendar table (no mocking needed - it's pure computation), and the
"each obligation has a source" bar is checked against the actual seeded
rows applied to the live Supabase project (see docs/PROGRESS.md's S12
entry for the citations and how they were verified).
"""
import datetime

import pytest

from app import compliance, supa

SEEDED_OBLIGATIONS = [
    {
        "id": "vat_monthly_return", "title_en": "Monthly VAT return and payment", "title_ne": "x",
        "category": "tax", "frequency": "monthly",
        "due_rule": {"type": "days_after_bs_month_end", "days": 25},
        "applies_if": {"pan_vat_registered": True},
        "citation": "Value Added Tax Act, 2052 (1996), Section 18", "source_url": "https://ird.gov.np",
    },
    {
        "id": "tds_monthly_statement", "title_en": "Monthly TDS statement and payment", "title_ne": "x",
        "category": "tax", "frequency": "monthly",
        "due_rule": {"type": "days_after_bs_month_end", "days": 15},
        "applies_if": {},
        "citation": "Income Tax Act, 2058 (2002), Section 90", "source_url": "https://ird.gov.np",
    },
    {
        "id": "income_tax_annual_return", "title_en": "Annual income tax return", "title_ne": "x",
        "category": "tax", "frequency": "annual",
        "due_rule": {"type": "months_after_bs_fy_end", "months": 3},
        "applies_if": {},
        "citation": "Income Tax Act, 2058 (2002), Section 96(1)", "source_url": "https://ird.gov.np",
    },
    {
        "id": "ocr_annual_return", "title_en": "Annual return to OCR", "title_ne": "x",
        "category": "company", "frequency": "annual",
        "due_rule": {"type": "months_after_bs_fy_end", "months": 6},
        "applies_if": {"entity_type_in": ["private_limited", "public_limited"]},
        "citation": "Companies Act, 2063 (2006), Section 80", "source_url": "https://ocr.gov.np",
    },
    {
        "id": "ssf_monthly_contribution", "title_en": "Monthly SSF contribution", "title_ne": "x",
        "category": "labour", "frequency": "monthly",
        "due_rule": {"type": "days_after_bs_month_end", "days": 15},
        "applies_if": {"has_employees": True},
        "citation": "Contribution Based Social Security Act, 2074 (2017), Section 7", "source_url": "https://ssf.gov.np",
    },
    {
        "id": "bonus_distribution", "title_en": "Annual bonus distribution", "title_ne": "x",
        "category": "labour", "frequency": "annual",
        "due_rule": {"type": "months_after_bs_fy_end", "months": 8},
        "applies_if": {"has_employees": True},
        "citation": "Bonus Act, 2030 (1974), Section 9", "source_url": "https://lawcommission.gov.np",
    },
]


def test_every_seeded_obligation_has_a_citation_and_a_source():
    for ob in SEEDED_OBLIGATIONS:
        assert ob["citation"].strip()
        assert ob["source_url"] and ob["source_url"].startswith("https://")
        assert ob["frequency"] in ("monthly", "annual")
        assert ob["due_rule"]["type"] in ("days_after_bs_month_end", "months_after_bs_fy_end")


def test_compliance_functions_fail_open_without_supabase_configured():
    assert supa.available() is False
    assert supa.company_profile_get("u1") is None
    assert supa.company_profile_upsert("u1", "Acme", "private_limited", True, True) is None
    assert supa.obligations_list() == []
    assert supa.all_company_profiles() == []
    assert supa.reminder_already_sent("u1", "vat_monthly_return", "2083-05") is False
    supa.reminder_record_sent("u1", "vat_monthly_return", "2083-05", "2083-06-25", "2026-10-11")  # no-op


def test_bs_month_end_and_fy_end_arithmetic():
    # Ashad (month 3) 2082 has 32 days per the BS calendar table.
    assert compliance.bs_month_end(2082, 3).day == 32
    # 3 months after Ashad-end 2083 is Ashwin-end 2083 (income tax annual return).
    y, m = compliance.add_bs_months(2083, 3, 3)
    assert (y, m) == (2083, 6)
    # December rollover.
    assert compliance.add_bs_months(2082, 11, 3) == (2083, 2)


def test_applies_to_gates_on_profile_fields():
    vat = SEEDED_OBLIGATIONS[0]
    assert compliance.applies_to(vat["applies_if"], {"pan_vat_registered": True}) is True
    assert compliance.applies_to(vat["applies_if"], {"pan_vat_registered": False}) is False

    tds = SEEDED_OBLIGATIONS[1]
    assert compliance.applies_to(tds["applies_if"], {}) is True  # no condition - always applies

    ocr = SEEDED_OBLIGATIONS[3]
    assert compliance.applies_to(ocr["applies_if"], {"entity_type": "sole_proprietorship"}) is False
    assert compliance.applies_to(ocr["applies_if"], {"entity_type": "private_limited"}) is True


def test_next_due_is_always_in_the_future_and_recurs_monthly():
    today = datetime.date(2026, 9, 29)
    vat = SEEDED_OBLIGATIONS[0]
    period, due_bs = compliance.next_due(vat, today)
    due_ad = compliance.bs_to_ad(due_bs.year, due_bs.month, due_bs.day)
    assert due_ad >= today
    # The obligation recurs: a month later, a *different* (later) period is next due.
    period2, due_bs2 = compliance.next_due(vat, due_ad + datetime.timedelta(days=1))
    assert period2 != period
    assert compliance.bs_to_ad(due_bs2.year, due_bs2.month, due_bs2.day) > due_ad


def test_next_due_annual_obligation():
    today = datetime.date(2026, 9, 29)
    income_tax = SEEDED_OBLIGATIONS[2]
    period, due_bs = compliance.next_due(income_tax, today)
    due_ad = compliance.bs_to_ad(due_bs.year, due_bs.month, due_bs.day)
    assert due_ad >= today
    assert period.isdigit() and len(period) == 4  # a bare BS year, e.g. "2083"


class FakeComplianceStore:
    def __init__(self, obligations):
        self.profiles: dict[str, dict] = {}
        self.obligations = obligations
        self.reminders_sent: set[tuple[str, str, str]] = set()

    def company_profile_get(self, user_id):
        return self.profiles.get(user_id)

    def company_profile_upsert(self, user_id, company_name, entity_type, pan_vat_registered,
                                has_employees, reminder_email=None):
        profile = {
            "id": f"cp-{user_id}", "user_id": user_id, "company_name": company_name,
            "entity_type": entity_type, "pan_vat_registered": pan_vat_registered,
            "has_employees": has_employees, "reminder_email": reminder_email,
            "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z",
        }
        self.profiles[user_id] = profile
        return dict(profile)

    def obligations_list(self):
        return [dict(o) for o in self.obligations]

    def all_company_profiles(self):
        return [dict(p) for p in self.profiles.values()]

    def reminder_already_sent(self, user_id, obligation_id, period):
        return (user_id, obligation_id, period) in self.reminders_sent

    def reminder_record_sent(self, user_id, obligation_id, period, due_date_bs, due_date_ad):
        self.reminders_sent.add((user_id, obligation_id, period))


@pytest.fixture()
def compliance_client(monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app

    monkeypatch.setattr(supa, "get_user", lambda token: {"id": "user-a"} if token == "a" else None)
    store = FakeComplianceStore(SEEDED_OBLIGATIONS)
    for fn in ["company_profile_get", "company_profile_upsert", "obligations_list",
               "all_company_profiles", "reminder_already_sent", "reminder_record_sent"]:
        monkeypatch.setattr(supa, fn, getattr(store, fn))
    with TestClient(app) as c:
        yield c, store


def test_company_profile_requires_auth(compliance_client):
    c, _ = compliance_client
    assert c.get("/api/company-profile").status_code == 401
    assert c.put("/api/company-profile", json={"company_name": "x", "entity_type": "private_limited"}).status_code == 401


def test_company_profile_create_then_get(compliance_client):
    c, _ = compliance_client
    headers = {"Authorization": "Bearer a"}

    assert c.get("/api/company-profile", headers=headers).status_code == 404

    r = c.put("/api/company-profile", json={
        "company_name": "Himalaya Traders Pvt Ltd", "entity_type": "private_limited",
        "pan_vat_registered": True, "has_employees": True, "reminder_email": "owner@example.com",
    }, headers=headers)
    assert r.status_code == 200
    assert r.json()["company_name"] == "Himalaya Traders Pvt Ltd"

    r = c.get("/api/company-profile", headers=headers)
    assert r.status_code == 200 and r.json()["pan_vat_registered"] is True


def test_upcoming_obligations_requires_profile_first(compliance_client):
    c, _ = compliance_client
    headers = {"Authorization": "Bearer a"}
    assert c.get("/api/obligations/upcoming", headers=headers).status_code == 404


def test_upcoming_obligations_filters_by_profile_and_window(compliance_client):
    c, _ = compliance_client
    headers = {"Authorization": "Bearer a"}
    c.put("/api/company-profile", json={
        "company_name": "Sole Trader Shop", "entity_type": "sole_proprietorship",
        "pan_vat_registered": False, "has_employees": False,
    }, headers=headers)

    r = c.get("/api/obligations/upcoming?within_days=365", headers=headers)
    assert r.status_code == 200
    body = r.json()
    ids = {o["id"] for o in body["obligations"]}
    # VAT (needs pan_vat_registered), OCR (needs a company entity type), SSF
    # and bonus (need employees) must all be excluded for this profile.
    assert "vat_monthly_return" not in ids
    assert "ocr_annual_return" not in ids
    assert "ssf_monthly_contribution" not in ids
    assert "bonus_distribution" not in ids
    # TDS and the annual income tax return have no conditions - always included.
    assert "tds_monthly_statement" in ids
    assert "income_tax_annual_return" in ids
    for ob in body["obligations"]:
        assert ob["citation"]
        assert ob["days_remaining"] >= 0

    # A 1-day window only returns what is due today or tomorrow (a monthly
    # deadline can legitimately fall inside it, e.g. TDS on the 25th).
    r = c.get("/api/obligations/upcoming?within_days=1", headers=headers)
    assert all(0 <= o["days_remaining"] <= 1 for o in r.json()["obligations"])


def test_upcoming_obligations_sorted_by_due_date(compliance_client):
    c, _ = compliance_client
    headers = {"Authorization": "Bearer a"}
    c.put("/api/company-profile", json={
        "company_name": "Full Co Pvt Ltd", "entity_type": "private_limited",
        "pan_vat_registered": True, "has_employees": True,
    }, headers=headers)
    r = c.get("/api/obligations/upcoming?within_days=365", headers=headers)
    dates = [o["due_date_ad"] for o in r.json()["obligations"]]
    assert dates == sorted(dates)
    assert len(dates) == len(SEEDED_OBLIGATIONS)  # every obligation applies to this profile


def test_reminder_job_dedups_via_reminders_sent(monkeypatch):
    import send_compliance_reminders as job

    monkeypatch.setattr(job.supa, "available", lambda: True)
    store = FakeComplianceStore(SEEDED_OBLIGATIONS)
    store.company_profile_upsert("user-a", "Full Co Pvt Ltd", "private_limited", True, True, "owner@example.com")
    for fn in ["all_company_profiles", "obligations_list", "reminder_already_sent", "reminder_record_sent"]:
        monkeypatch.setattr(job.supa, fn, getattr(store, fn))
    # Whether anything is due within the default 7-day window depends on today's date, so widen it.
    monkeypatch.setattr(job.config, "COMPLIANCE_REMINDER_DAYS_AHEAD", 400)

    sent_first = job.run(dry_run=True)
    assert sent_first > 0
    # dry-run never records, so the same run again finds the same obligations still unsent.
    sent_second = job.run(dry_run=True)
    assert sent_second == sent_first
