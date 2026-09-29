"""Legal tools: the limitation-period database, BS date arithmetic, the labour /
interest / tax / court-fee / age calculators and the /api/calculators/* tools API.

Table-driven. Tests marked `requires_corpus` hit the real built corpus (through
app.playbooks.resolve_provision / app.retrieval), like tests/test_calculators.py:
a calculator or limitation entry citing a section the corpus cannot find, or whose
stated number is not in that section's text, must fail loudly.
"""
import datetime
import re

import pytest
import yaml
from fastapi.testclient import TestClient

from app import retrieval
from app.calculators import age, court_fee, datetools, dates, interest, labour_rights, limitation, tax
from app.calculators.sources import verify_source
from app.retrieval import CORPUS_DIR

requires_corpus = pytest.mark.skipif(
    not (CORPUS_DIR / "manifest.json").exists(), reason="built corpus shards not present"
)

D = datetime.date
CIV = "मुलुकी देवानी संहिता, २०७४"
CRI = "मुलुकी अपराध संहिता, २०७४"


def bs(y, m, d):
    return dates.bs_to_ad(y, m, d)


def to_bs(d):
    b = dates.ad_to_bs(d)
    return (b.year, b.month, b.day)


# ================================================================ BS date arithmetic ====

ADD_MONTH_CASES = [
    # start (BS), months, expected (BS)
    ((2081, 1, 15), 6, (2081, 7, 15)),
    ((2081, 1, 15), 0, (2081, 1, 15)),
    ((2081, 1, 15), 12, (2082, 1, 15)),
    ((2081, 5, 31), 1, (2081, 6, 30)),  # Bhadra 31 -> Ashwin has 30 days
    ((2081, 2, 32), 1, (2081, 3, 31)),  # Jestha 32 -> Ashadh has 31
    ((2081, 10, 30), 1, (2081, 11, 29)),  # Magh 30 -> Falgun 2081 has 29
    ((2081, 12, 31), 1, (2082, 1, 31)),  # year rollover keeps the day
    ((2081, 12, 31), 12, (2082, 12, 30)),  # ... and clips against Chaitra 2082 (30 days)
    ((2081, 12, 31), 13, (2083, 1, 31)),
    ((2081, 3, 10), -3, (2080, 12, 10)),  # negative months go back
    ((2081, 1, 1), -1, (2080, 12, 1)),
    ((2080, 1, 15), 24, (2082, 1, 15)),
]


@pytest.mark.parametrize("start, months, expected", ADD_MONTH_CASES)
def test_add_bs_months(start, months, expected):
    assert to_bs(dates.add_bs_months(bs(*start), months)) == expected


def test_a_bs_month_is_not_thirty_days():
    start = bs(2081, 1, 1)
    end = dates.add_period(start, 6, "months")
    assert to_bs(end) == (2081, 7, 1)
    # Baisakh..Ashwin 2081 have 31+32+31+32+31+30 days, so "6 months" is 187 days here, never 180
    assert (end - start).days == 31 + 32 + 31 + 32 + 31 + 30 == 187


ADD_YEAR_CASES = [
    ((2081, 5, 31), 1, (2082, 5, 31)),
    ((2081, 12, 31), 1, (2082, 12, 30)),  # Chaitra 2082 is one day shorter
    ((2081, 1, 15), 2, (2083, 1, 15)),
    ((2081, 1, 15), -1, (2080, 1, 15)),
]


@pytest.mark.parametrize("start, years, expected", ADD_YEAR_CASES)
def test_add_bs_years(start, years, expected):
    assert to_bs(dates.add_bs_years(bs(*start), years)) == expected


def test_add_period_units():
    start = bs(2081, 1, 15)
    assert dates.add_period(start, 35, "days") == start + datetime.timedelta(days=35)
    assert to_bs(dates.add_period(start, 3, "months")) == (2081, 4, 15)
    assert to_bs(dates.add_period(start, 2, "years")) == (2083, 1, 15)
    with pytest.raises(ValueError):
        dates.add_period(start, 1, "fortnights")


def test_arithmetic_stops_at_the_end_of_the_calendar_table():
    with pytest.raises(dates.UnsupportedDate):
        dates.add_bs_years(bs(2100, 12, 30), 1)
    with pytest.raises(dates.UnsupportedDate):
        dates.add_days(dates.SUPPORTED_AD_MAX, 1)
    with pytest.raises(dates.UnsupportedDate):
        dates.add_bs_months(bs(1975, 1, 1), -1)
    with pytest.raises(dates.UnsupportedDate):
        dates.check_ad_supported(D(1900, 1, 1))
    with pytest.raises(dates.UnsupportedDate):
        dates.check_ad_supported(D(2050, 1, 1))


@pytest.mark.parametrize("year, month, length", [(2081, 1, 31), (2081, 2, 32), (2081, 9, 29), (2081, 11, 29), (2081, 12, 31),
                                                 (2082, 12, 30), (2100, 5, 30), (1975, 4, 32)])
def test_bs_month_length(year, month, length):
    assert dates.bs_month_length(year, month) == length


@pytest.mark.parametrize("year, month", [(2101, 1), (1974, 1), (2081, 0), (2081, 13)])
def test_bs_month_length_rejects_out_of_range(year, month):
    with pytest.raises(dates.UnsupportedDate):
        dates.bs_month_length(year, month)


DIFF_CASES = [
    # start, end (BS), years, months, days, total_days
    ((2081, 1, 1), (2081, 1, 1), 0, 0, 0, 0),
    ((2081, 1, 31), (2081, 2, 1), 0, 0, 1, 1),
    ((2081, 1, 15), (2081, 7, 15), 0, 6, 0, 187),
    ((2081, 1, 31), (2082, 3, 1), 1, 1, 1, 398),
    ((2081, 1, 1), (2082, 1, 1), 1, 0, 0, 366),  # 31+32+31+32+31+30+30+30+29+30+29+31
    ((2081, 1, 1), (2082, 3, 5), 1, 2, 4, 432),
]


@pytest.mark.parametrize("start, end, years, months, days, total", DIFF_CASES)
def test_bs_difference(start, end, years, months, days, total):
    diff = dates.bs_difference(bs(*start), bs(*end))
    assert (diff.years, diff.months, diff.days, diff.total_days) == (years, months, days, total)
    assert diff.negative is False


def test_bs_difference_is_order_independent_and_flags_direction():
    a, b = bs(2081, 1, 1), bs(2082, 3, 5)
    fwd, back = dates.bs_difference(a, b), dates.bs_difference(b, a)
    assert (fwd.years, fwd.months, fwd.days) == (back.years, back.months, back.days)
    assert fwd.negative is False and back.negative is True


def test_add_then_difference_round_trips():
    d = D(2000, 1, 1)
    while d < D(2040, 1, 1):
        for n in (1, 5, 11, 12, 30):
            shifted = dates.add_bs_months(d, n)
            diff = dates.bs_difference(d, shifted)
            assert diff.years * 12 + diff.months == n and diff.days == 0, (d, n)
        d += datetime.timedelta(days=37)


# ============================================================ limitation database ====

def test_yaml_structure():
    """Shape checks that need no corpus."""
    raw = limitation._raw()
    ids = [e["id"] for e in raw["entries"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    categories = {c["id"] for c in raw["categories"]}
    laws = raw["laws"]
    for e in raw["entries"]:
        assert re.fullmatch(r"[a-z0-9_]+", e["id"]), e["id"]
        assert e["category"] in categories, e["id"]
        assert e["name"]["en"].strip() and e["name"]["ne"].strip(), e["id"]
        assert e["citation"]["law_title_ne"] in laws and laws[e["citation"]["law_title_ne"]]["en"], e["id"]
        assert isinstance(e["citation"]["section"], str) and e["citation"]["section"], e["id"]
        assert e["period_phrase_ne"].strip(), e["id"]
        period = e["period"]
        assert period["kind"] in ("fixed", "none", "special"), e["id"]
        if period["kind"] == "fixed":
            assert isinstance(period["value"], int) and period["value"] > 0, e["id"]
            assert period["unit"] in ("days", "months", "years"), e["id"]
            assert e["start"]["kind"] in ("act", "knowledge", "cause", "other"), e["id"]
            assert e["start"]["en"].strip() and e["start"]["ne"].strip(), e["id"]
        if period["kind"] == "special":
            assert period["text"]["en"].strip() and period["text"]["ne"].strip(), e["id"]
        if e.get("long_stop"):
            assert period["kind"] == "fixed" and e["long_stop"]["unit"] in ("days", "months", "years")
        assert all(isinstance(k, str) for k in e.get("keywords", [])), e["id"]
    for rule in raw["general_rules"]:
        assert rule["text"]["en"].strip() and rule["text"]["ne"].strip() and rule["phrase_ne"].strip()


def test_database_breadth():
    entries = limitation.raw_entries()
    assert len(entries) >= 200
    by_law = {}
    for e in entries:
        by_law.setdefault(e["citation"]["law_title_ne"], []).append(e)
    assert len(by_law[CIV]) >= 60
    assert len(by_law[CRI]) >= 60
    assert len(by_law) >= 45  # the two Codes, two procedure Codes and the special Acts
    assert {c["id"] for c in limitation._raw()["categories"]} >= {"civil", "criminal", "family", "property", "labour", "consumer", "banking", "cyber"}
    kinds = {e["period"]["kind"] for e in entries}
    assert kinds == {"fixed", "none", "special"}


LEGACY = {
    "contract_civil_claim": (2, "years", CIV, "520"),
    "partition_disagreement": (3, "months", CIV, "235"),
    "labour_dispute_complaint": (6, "months", "श्रम ऐन, २०७४", "162"),
    "foreign_employment_complaint": (1, "years", "वैदेशिक रोजगार ऐन, २०६४", "60"),
    "cheque_dishonour_complaint": (1, "years", "बैङ्किङ्ग कसूर तथा सजाय ऐन, २०६४", "17"),
}


@pytest.mark.parametrize("claim_id, spec", list(LEGACY.items()))
def test_legacy_ids_still_resolve_with_their_old_periods(claim_id, spec):
    value, unit, law, section = spec
    entry = limitation.get_entry(claim_id)
    assert (entry["period"]["value"], entry["period"]["unit"]) == (value, unit)
    assert (entry["citation"]["law_title_ne"], entry["citation"]["section"]) == (law, section)
    assert claim_id in limitation.list_claim_types()


@requires_corpus
@pytest.mark.parametrize("entry", limitation.raw_entries(), ids=lambda e: e["id"])
def test_every_entry_citation_resolves_and_states_the_number_in_the_text(entry):
    """The citation-integrity test: the cited section exists, the verbatim phrase is in its text and the
    number+unit inside the phrase are the number+unit the entry states."""
    assert limitation.verify_entry(entry) == []


@requires_corpus
@pytest.mark.parametrize("rule", limitation.general_rules(), ids=lambda r: r["id"])
def test_general_rules_are_in_the_cited_sections(rule):
    assert limitation.verify_rule(rule) == []


@requires_corpus
def test_catalog_resolves_every_citation():
    cat = limitation.catalog()
    assert cat["total"] == len(limitation.raw_entries())
    assert sum(len(g["entries"]) for g in cat["categories"]) == cat["total"]
    for group in cat["categories"]:
        for e in group["entries"]:
            assert e["citation"]["resolved"] and e["citation"]["slug"], e["id"]
            assert e["period"]["text"]["en"] and e["period"]["text"]["ne"]
    assert all(r["citation"] for r in cat["general_rules"])


def _corpus_hadmyad_sections():
    entries, _digest = retrieval.corpus_source()
    return [
        (e.get("doc_title_ne"), e.get("section"))
        for e in entries
        if e.get("category") == "law" and "हदम्याद" in (e.get("title_ne") or "")
    ]


@requires_corpus
def test_every_hadmyad_section_of_the_codes_and_special_acts_is_in_the_database():
    """Completeness guard: each corpus section titled हदम्याद in the Civil/Criminal Codes, the two procedure
    Codes and every Act (not ordinance/bill/report) is cited by an entry or a general rule."""
    cited = {(e["citation"]["law_title_ne"], e["citation"]["section"]) for e in limitation.raw_entries()}
    cited |= {(r["citation"]["law_title_ne"], r["citation"]["section"]) for r in limitation.general_rules()}
    skip = ("अध्यादेश", "विधेयक", "प्रतिवेदन", "अध्ययन", "नियमावली")
    missing = []
    seen = 0
    for doc, section in _corpus_hadmyad_sections():
        if not doc or any(s in doc for s in skip):
            continue
        seen += 1
        if (doc, section) not in cited:
            missing.append((doc, section))
    assert seen >= 100
    assert not missing, missing


@requires_corpus
def test_civil_and_criminal_codes_are_fully_covered_by_period_entries():
    cited = {(e["citation"]["law_title_ne"], e["citation"]["section"]) for e in limitation.raw_entries()}
    for law in (CIV, CRI):
        sections = [s for d, s in _corpus_hadmyad_sections() if d == law]
        assert len(sections) >= 30
        assert [s for s in sections if (law, s) not in cited] == []


@requires_corpus
def test_verify_entry_catches_a_wrong_number_a_wrong_section_and_a_missing_phrase():
    good = limitation.get_entry("partition_disagreement")
    assert limitation.verify_entry(good) == []
    wrong_number = {**good, "period": {"kind": "fixed", "value": 4, "unit": "months"}}
    assert limitation.verify_entry(wrong_number)
    wrong_unit = {**good, "period": {"kind": "fixed", "value": 3, "unit": "years"}}
    assert limitation.verify_entry(wrong_unit)
    wrong_section = {**good, "citation": {**good["citation"], "section": "9999"}}
    assert limitation.verify_entry(wrong_section)
    other_text = {**good, "citation": {**good["citation"], "section": "84"}}  # a different chapter's हदम्याद
    assert limitation.verify_entry({**other_text, "period_phrase_ne": "एक वर्षभित्र"})
    no_phrase = {k: v for k, v in good.items() if k != "period_phrase_ne"}
    assert limitation.verify_entry(no_phrase)


PHRASE_CASES = [
    ("छ महिनाभित्र", 6, "months"),
    ("६ महिनाभित्र", 6, "months"),
    ("9० दिनभित्र", 90, "days"),
    ("नब्बे दिनभित्र", 90, "days"),
    ("पैँतीस दिनभित्र", 35, "days"),
    ("पैंतीस दिन भित्र", 35, "days"),
    ("पैतीस दिन", 35, "days"),
    ("तीन वर्ष नाघेपछि", 3, "years"),
    ("सत्तरी दिन", 70, "days"),
    ("साठी दिन", 60, "days"),
    ("८ महिनाभित्र", 8, "months"),
    ("बीस वर्ष", 20, "years"),
    ("तीस दिनको अवधिभित्र", 30, "days"),
    ("एक\nवर्षभित्र", 1, "years"),
    ("जहिलेसुकै", None, None),
]


@pytest.mark.parametrize("phrase, value, unit", PHRASE_CASES)
def test_parse_period_phrase(phrase, value, unit):
    parsed = limitation.parse_period_phrase(phrase)
    assert parsed == ((value, unit) if value is not None else None)


def test_normalise_text_ignores_whitespace_digits_and_private_use_glyphs():
    assert limitation.normalise_text("छ\n महिना​भित्र") == "छमहिनाभित्र"
    assert limitation.normalise_text("९०") == limitation.normalise_text("90") == "90"


PERIOD_TEXT_CASES = [
    ({"kind": "fixed", "value": 6, "unit": "months"}, "6 months", "६ महिना"),
    ({"kind": "fixed", "value": 1, "unit": "years"}, "1 year", "१ वर्ष"),
    ({"kind": "fixed", "value": 35, "unit": "days"}, "35 days", "३५ दिन"),
    ({"kind": "none"}, "No limitation", "हदम्याद लाग्दैन"),
]


@pytest.mark.parametrize("period, en, ne", PERIOD_TEXT_CASES)
def test_period_text(period, en, ne):
    assert limitation.period_text(period) == {"en": en, "ne": ne}


# ---- deadline computation ----------------------------------------------------------

DEADLINE_CASES = [
    # claim id, trigger (BS), expected deadline (BS)
    ("partition_disagreement", (2081, 1, 15), (2081, 4, 15)),
    ("labour_dispute_complaint", (2081, 1, 15), (2081, 7, 15)),
    ("contract_civil_claim", (2081, 5, 31), (2083, 5, 31)),
    ("cheque_dishonour_complaint", (2081, 12, 31), (2082, 12, 30)),  # clipped to the shorter Chaitra
    ("foreign_employment_complaint", (2081, 1, 1), (2082, 1, 1)),
    ("civil_29_other", (2081, 12, 31), (2082, 6, 31)),  # Ashwin 2082 has 31 days
    ("civil_29_other", (2081, 6, 30), (2081, 12, 30)),
    ("criminal_74_public_peace", (2081, 11, 29), (2082, 2, 29)),
]


@requires_corpus
@pytest.mark.parametrize("claim_id, trigger, expected", DEADLINE_CASES)
def test_deadline_is_counted_in_bs_months(claim_id, trigger, expected):
    result = limitation.check(claim_id, bs(*trigger), today=D(2024, 1, 1))
    assert to_bs(D.fromisoformat(result["deadline"])) == expected
    assert result["deadline_bs"]["iso"] == "%04d-%02d-%02d" % expected
    assert result["trigger_date_bs"]["iso"] == "%04d-%02d-%02d" % trigger
    assert result["provision"]["citation"]


@requires_corpus
def test_day_periods_are_calendar_days():
    start = bs(2081, 1, 15)
    for claim_id, days in (("domestic_violence_14", 90), ("cpc_205_civil_appeal", 30), ("labour_165_2_dismissal_appeal", 35)):
        result = limitation.check(claim_id, start, today=D(2024, 1, 1))
        assert D.fromisoformat(result["deadline"]) == start + datetime.timedelta(days=days), claim_id


@requires_corpus
def test_start_offset_days_are_added_before_the_period():
    # civil procedure s. 58(क): 7 days counted from the 15th day after a death
    start = bs(2081, 1, 15)
    result = limitation.check("cpc_58_a_bereavement", start, today=D(2024, 1, 1))
    assert D.fromisoformat(result["deadline"]) == start + datetime.timedelta(days=15 + 7)


@requires_corpus
def test_a_long_stop_can_bring_the_deadline_forward():
    # pre-emption: 35 days from knowing, but no later than 6 months after the instrument was passed
    knew = bs(2081, 1, 15)
    passed = bs(2080, 8, 1)
    plain = limitation.check("civil_462_a_preemption", knew, today=D(2024, 1, 1))
    capped = limitation.check("civil_462_a_preemption", knew, today=D(2024, 1, 1), long_stop_trigger_date=passed)
    assert D.fromisoformat(plain["deadline"]) == knew + datetime.timedelta(days=35)
    assert to_bs(D.fromisoformat(capped["long_stop"]["deadline"])) == (2081, 2, 1)
    assert D.fromisoformat(capped["deadline"]) == D.fromisoformat(capped["long_stop"]["deadline"]) < D.fromisoformat(plain["deadline"])
    # a long stop that falls after the ordinary deadline changes nothing
    late = limitation.check("civil_462_a_preemption", knew, today=D(2024, 1, 1), long_stop_trigger_date=bs(2081, 1, 1))
    assert late["deadline"] == plain["deadline"]


@requires_corpus
def test_time_barred_boundary_is_the_deadline_day_itself():
    trigger = bs(2081, 1, 15)
    deadline = limitation.check("partition_disagreement", trigger, today=D(2024, 1, 1))["deadline"]
    d = D.fromisoformat(deadline)
    on = limitation.check("partition_disagreement", trigger, today=d)
    after = limitation.check("partition_disagreement", trigger, today=d + datetime.timedelta(days=1))
    assert (on["is_time_barred"], on["days_remaining"]) == (False, 0)
    assert (after["is_time_barred"], after["days_remaining"]) == (True, -1)


@requires_corpus
@pytest.mark.parametrize("claim_id", ["civil_235_a_no_partition", "criminal_59_1_state_offences", "civil_235_c_hidden_property", "cpc_52_1_minor", "criminal_240_1_treatment_death"])
def test_entries_without_a_plain_period_have_no_deadline(claim_id):
    with pytest.raises(limitation.NotComputable):
        limitation.check(claim_id, D(2024, 1, 1))
    assert claim_id not in limitation.list_claim_types()
    assert issubclass(limitation.NotComputable, limitation.UnknownClaimType)


@requires_corpus
def test_unknown_claim_and_out_of_range_trigger():
    with pytest.raises(limitation.UnknownClaimType):
        limitation.get_entry("nope")
    with pytest.raises(dates.UnsupportedDate):
        limitation.check("partition_disagreement", D(1900, 1, 1))
    with pytest.raises(dates.UnsupportedDate):  # the deadline would fall after the end of the calendar table
        limitation.check("contract_civil_claim", bs(2100, 6, 1))


# ========================================================= calculators: sources ====

_SOURCE_MODULES = [labour_rights, interest, tax, court_fee, age, datetools]
_ALL_SOURCES = [(m.__name__.rsplit(".", 1)[-1], s) for m in _SOURCE_MODULES for s in m.SOURCES]


def test_source_registries_are_populated():
    counts = {m.__name__.rsplit(".", 1)[-1]: len(m.SOURCES) for m in _SOURCE_MODULES}
    assert all(n >= 2 for n in counts.values()), counts
    assert sum(counts.values()) >= 80
    assert counts['labour_rights'] >= 30 and counts['tax'] >= 25


@requires_corpus
@pytest.mark.parametrize("module, source", _ALL_SOURCES, ids=lambda x: x if isinstance(x, str) else x.id)
def test_every_calculator_number_is_in_the_section_it_cites(module, source):
    assert verify_source(source) == []


@requires_corpus
def test_verify_source_catches_a_number_that_is_not_in_the_section():
    good = labour_rights.S_OT_RATE
    assert verify_source(good) == []
    assert verify_source(type(good)("x", good.law_title_ne, good.section, "दोब्बर", "x"))
    assert verify_source(type(good)("x", good.law_title_ne, "99999", good.phrase_ne, "x"))


# ================================================== calculators: labour rights ====

OVERTIME_CASES = [
    # kwargs, expected hourly, rate, pay, within limit
    (dict(overtime_hours=2, period="day", basic_hourly_pay=100), 100.0, 150.0, 300.0, True),
    (dict(overtime_hours=4, period="day", basic_hourly_pay=100), 100.0, 150.0, 600.0, True),
    (dict(overtime_hours=5, period="day", basic_hourly_pay=100), 100.0, 150.0, 750.0, False),
    (dict(overtime_hours=24, period="week", basic_hourly_pay=80), 80.0, 120.0, 2880.0, True),
    (dict(overtime_hours=25, period="week", basic_hourly_pay=80), 80.0, 120.0, 3000.0, False),
    (dict(overtime_hours=3, period="day", basic_monthly_pay=26000, paid_days_per_month=26), 125.0, 187.5, 562.5, True),
    (dict(overtime_hours=1.5, period="day", basic_monthly_pay=24000, paid_days_per_month=30), 100.0, 150.0, 225.0, True),
]


@requires_corpus
@pytest.mark.parametrize("kwargs, hourly, rate, pay, within", OVERTIME_CASES)
def test_overtime_pay(kwargs, hourly, rate, pay, within):
    r = labour_rights.overtime_pay(**kwargs)
    assert r["hourly_basic_pay"] == pytest.approx(hourly)
    assert r["overtime_rate_per_hour"] == pytest.approx(rate)
    assert r["overtime_pay_npr"] == pytest.approx(pay)
    assert r["within_legal_limit"] is within
    assert r["rate_multiple"] == 1.5
    assert all(p["citation"] for p in r["provisions"])


@pytest.mark.parametrize("kwargs", [
    dict(overtime_hours=0, basic_hourly_pay=100),
    dict(overtime_hours=-1, basic_hourly_pay=100),
    dict(overtime_hours=2, basic_hourly_pay=0),
    dict(overtime_hours=2, basic_hourly_pay=-5),
    dict(overtime_hours=2),  # no pay information
    dict(overtime_hours=2, basic_monthly_pay=26000),  # monthly without paid days
    dict(overtime_hours=2, basic_monthly_pay=26000, paid_days_per_month=0),
    dict(overtime_hours=2, basic_hourly_pay=100, period="month"),
])
def test_overtime_pay_rejects_bad_input(kwargs):
    with pytest.raises(ValueError):
        labour_rights.overtime_pay(**kwargs)


HOURS_CASES = [
    (dict(hours_per_day=8), True, [], True),  # an 8-hour day runs past 5 continuous hours, so the 30-minute break is due
    (dict(hours_per_day=9), False, ["day_over_8"], True),
    (dict(hours_per_day=8, hours_per_week=48), True, [], True),
    (dict(hours_per_day=8, hours_per_week=49), False, ["week_over_48"], True),
    (dict(hours_per_day=8, overtime_per_day=4), True, [], True),
    (dict(hours_per_day=8, overtime_per_day=4.5), False, ["overtime_day_over_4"], True),
    (dict(hours_per_day=8, overtime_per_week=25), False, ["overtime_week_over_24"], True),
    (dict(hours_per_day=5), True, [], False),  # break is due only after MORE than 5 continuous hours
    (dict(hours_per_day=5.5), True, [], True),
    (dict(hours_per_day=12, hours_per_week=60, overtime_per_day=6, overtime_per_week=30), False,
     ["day_over_8", "week_over_48", "overtime_day_over_4", "overtime_week_over_24"], True),
]


@requires_corpus
@pytest.mark.parametrize("kwargs, ok, codes, break_needed", HOURS_CASES)
def test_check_hours(kwargs, ok, codes, break_needed):
    r = labour_rights.check_hours(**kwargs)
    assert r["within_limits"] is ok
    assert [i["code"] for i in r["issues"]] == codes
    assert r["break_needed"] is break_needed


@pytest.mark.parametrize("kwargs", [dict(hours_per_day=0), dict(hours_per_day=-1), dict(hours_per_day=8, overtime_per_day=-1),
                                     dict(hours_per_day=8, hours_per_week=0)])
def test_check_hours_rejects_bad_input(kwargs):
    with pytest.raises(ValueError):
        labour_rights.check_hours(**kwargs)


@requires_corpus
def test_working_hours_limits_table():
    t = labour_rights.working_hours_limits()
    assert (t["normal_day_hours"], t["normal_week_hours"], t["overtime_max_per_day"], t["overtime_max_per_week"]) == (8, 48, 4, 24)
    assert t["rest_break"] == {"after_continuous_hours": 5, "minutes": 30}


ACCRUAL_CASES = [
    # days worked, months in year, home days, whole, over cap, sick
    (0, 0, 0.0, 0, 0.0, 0.0),
    (19, 12, 0.95, 0, 0.0, 12.0),
    (20, 6, 1.0, 1, 0.0, 6.0),
    (219, 3, 10.95, 10, 0.0, 3.0),
    (1800, 12, 90.0, 90, 0.0, 12.0),
    (2000, 24, 100.0, 100, 10.0, 12.0),  # months beyond 12 count as a full year of sick leave
]


@requires_corpus
@pytest.mark.parametrize("days, months, home, whole, over, sick", ACCRUAL_CASES)
def test_leave_accrual(days, months, home, whole, over, sick):
    r = labour_rights.leave_accrual(days, months)
    assert r["home_leave_days"] == pytest.approx(home)
    assert r["home_leave_whole_days"] == whole
    assert r["home_leave_over_cap_days"] == pytest.approx(over)
    assert r["sick_leave_days"] == pytest.approx(sick)


def test_leave_accrual_without_months_has_no_sick_leave_figure_and_rejects_negatives():
    assert "sick_leave_days" not in labour_rights.leave_accrual(40)
    for bad in (dict(days_worked=-1), dict(days_worked=10, months_worked_in_year=-1)):
        with pytest.raises(ValueError):
            labour_rights.leave_accrual(**bad)


@requires_corpus
@pytest.mark.parametrize("home, sick, wage, amount", [(10, 5, 1000, 15000.0), (100, 50, 1000, 135000.0), (90, 45, 500.5, 67567.5), (0, 0, 800, 0.0)])
def test_leave_encashment_counts_up_to_the_caps(home, sick, wage, amount):
    assert labour_rights.leave_encashment(home, sick, wage)["amount_npr"] == pytest.approx(amount)


@pytest.mark.parametrize("args", [(-1, 0, 100), (0, -1, 100), (1, 1, 0), (1, 1, -5)])
def test_leave_encashment_rejects_bad_input(args):
    with pytest.raises(ValueError):
        labour_rights.leave_encashment(*args)


@requires_corpus
def test_leave_entitlements_table():
    t = labour_rights.leave_entitlements()
    rows = {r["id"]: r for r in t["entitlements"]}
    assert set(rows) == {"weekly", "public", "substitute", "home", "sick", "maternity", "paternity", "mourning"}
    assert rows["sick"]["days"] == 12 and rows["maternity"]["days"] == 98 and rows["paternity"]["days"] == 15 and rows["mourning"]["days"] == 13
    assert all(r["provision"]["citation"] for r in rows.values())
    assert (t["accumulation"]["home_leave_cap_days"], t["accumulation"]["sick_leave_cap_days"]) == (90, 45)


@requires_corpus
def test_maternity_leave_dates():
    r = labour_rights.maternity_leave(D(2026, 10, 1))
    assert r["latest_start"] == "2026-09-17"  # 2 weeks before
    assert r["minimum_leave_until"] == "2026-11-12"  # 6 weeks after
    assert r["leave_start"] == "2026-09-17" and r["leave_end"] == "2026-12-23"  # 14 weeks counted inclusively
    assert (D.fromisoformat(r["leave_end"]) - D.fromisoformat(r["leave_start"])).days + 1 == 98
    assert r["full_pay_days"] == 60 and r["full_pay_until"] == "2026-11-15" and r["unpaid_days"] == 38
    assert r["warnings"] == [] and r["extra_unpaid_month"] is None and r["paternity_days"] == 15
    assert r["leave_start_bs"] == "2083-06-01"


@requires_corpus
def test_maternity_leave_warnings_and_extra_month():
    late = labour_rights.maternity_leave(D(2026, 10, 1), leave_start=D(2026, 9, 25))
    assert "start_after_latest_start" in late["warnings"]
    short = labour_rights.maternity_leave(D(2026, 10, 1), leave_start=D(2026, 8, 1))
    assert "ends_before_six_weeks_after_expected_delivery" in short["warnings"]
    extra = labour_rights.maternity_leave(D(2026, 10, 1), extra_month_recommended=True)
    assert extra["extra_unpaid_month"]["from"] == "2026-12-24"
    assert D.fromisoformat(extra["extra_unpaid_month"]["to"]) > D(2026, 12, 24)
    with pytest.raises(dates.UnsupportedDate):
        labour_rights.maternity_leave(D(1900, 1, 1))


@requires_corpus
@pytest.mark.parametrize("pay, months, amount", [(30000, 12, 30000.0), (30000, 6, 15000.0), (30000, 18, 30000.0), (24000, 3, 6000.0), (30000, 0, 0.0)])
def test_festival_allowance(pay, months, amount):
    assert labour_rights.festival_allowance(pay, months)["amount_npr"] == pytest.approx(amount)


@pytest.mark.parametrize("args", [(0, 12), (-100, 12), (1000, -1)])
def test_festival_allowance_rejects_bad_input(args):
    with pytest.raises(ValueError):
        labour_rights.festival_allowance(*args)


@requires_corpus
def test_fund_contributions():
    r = labour_rights.fund_contributions(30000, 12)
    m = r["monthly"]
    assert (m["employee_pf_npr"], m["employer_pf_npr"], m["employer_gratuity_npr"]) == (3000.0, 3000.0, 2499.0)
    assert m["total_deposit_npr"] == 8499.0 and m["employer_cost_npr"] == 5499.0
    assert r["period_total"]["total_deposit_npr"] == 101988.0
    assert r["rates_pct"] == {"employee_pf": 10.0, "employer_pf": 10.0, "gratuity": 8.33}


@pytest.mark.parametrize("args", [(0, 1), (-5, 1), (1000, 0), (1000, -3)])
def test_fund_contributions_rejects_bad_input(args):
    with pytest.raises(ValueError):
        labour_rights.fund_contributions(*args)


@requires_corpus
def test_notice_tiers_agree_with_the_existing_notice_calculator():
    from app.calculators import labour
    tiers = labour_rights.notice_tiers()["tiers"]
    assert [t["notice_days"] for t in tiers] == [1, 7, 30]
    for service_days, expected in ((10, 1), (28, 1), (29, 7), (365, 7), (366, 30)):
        assert labour.notice_period_days(service_days) == expected


# ============================================================= calculators: interest ====

INTEREST_CASES = [
    # kwargs, days, rate applied, interest, capped by principal
    (dict(principal=100000, start=D(2024, 1, 1), end=D(2024, 12, 31), agreed_rate_pct=10), 365, 10.0, 10000.0, False),
    (dict(principal=100000, start=D(2024, 1, 1), end=D(2024, 12, 31), agreed_rate_pct=8), 365, 8.0, 8000.0, False),
    (dict(principal=100000, start=D(2024, 1, 1), end=D(2024, 12, 31), agreed_rate_pct=18), 365, 10.0, 10000.0, False),
    (dict(principal=100000, start=D(2024, 1, 1), end=D(2024, 12, 31), agreed_rate_pct=None), 365, 10.0, 10000.0, False),
    (dict(principal=100000, start=D(2024, 1, 1), end=D(2024, 12, 31), agreed_rate_pct=12, interest_stated_in_instrument=False), 365, 0.0, 0.0, False),
    (dict(principal=100000, start=D(2024, 1, 1), end=D(2024, 1, 1), agreed_rate_pct=10), 0, 10.0, 0.0, False),
    (dict(principal=100000, start=D(2024, 1, 1), end=D(2024, 12, 31), agreed_rate_pct=0), 365, 0.0, 0.0, False),
    (dict(principal=1000, start=D(2000, 1, 1), end=D(2020, 1, 1), agreed_rate_pct=10), 7305, 10.0, 1000.0, True),  # 20 years: capped at the principal
]


@requires_corpus
@pytest.mark.parametrize("kwargs, days, rate, amount, capped", INTEREST_CASES)
def test_simple_interest(kwargs, days, rate, amount, capped):
    r = interest.simple_interest(**kwargs)
    assert r["days"] == days
    assert r["rate_applied_pct"] == rate
    assert r["interest_npr"] == pytest.approx(amount)
    assert r["capped_by_principal"] is capped
    assert r["total_due_npr"] == pytest.approx(kwargs["principal"] + amount)
    assert all(p["citation"] for p in r["provisions"])


@requires_corpus
def test_simple_interest_reports_the_excess_over_the_legal_maximum():
    r = interest.simple_interest(100000, D(2024, 1, 1), D(2024, 12, 31), agreed_rate_pct=24)
    assert r["interest_at_agreed_rate_npr"] == pytest.approx(24000.0)
    assert r["excess_over_legal_max_npr"] == pytest.approx(14000.0)
    within = interest.simple_interest(100000, D(2024, 1, 1), D(2024, 12, 31), agreed_rate_pct=9)
    assert within["interest_at_agreed_rate_npr"] is None and within["excess_over_legal_max_npr"] is None


@pytest.mark.parametrize("kwargs", [
    dict(principal=0, start=D(2024, 1, 1), end=D(2024, 2, 1)),
    dict(principal=-100, start=D(2024, 1, 1), end=D(2024, 2, 1)),
    dict(principal=100, start=D(2024, 2, 1), end=D(2024, 1, 1)),
    dict(principal=100, start=D(2024, 1, 1), end=D(2024, 2, 1), agreed_rate_pct=-1),
    dict(principal=100, start=D(2024, 1, 1), end=D(2024, 2, 1), agreed_rate_pct=1001),
    dict(principal=100, start=D(1900, 1, 1), end=D(2024, 2, 1)),
])
def test_simple_interest_rejects_bad_input(kwargs):
    with pytest.raises(ValueError):
        interest.simple_interest(**kwargs)


@requires_corpus
def test_interest_rules_table():
    t = interest.max_lawful_rate()
    assert t["max_annual_rate_pct"] == 10.0 and t["default_rate_pct"] == 10.0
    assert len(t["rules"]) == 4 and all(p["citation"] for p in t["provisions"])


# ================================================================ calculators: tax ====

TAX_CASES = [
    # taxable income, expected annual tax
    (0, 0.0),
    (500_000, 5_000.0),
    (1_000_000, 10_000.0),
    (1_250_000, 35_000.0),
    (1_500_000, 60_000.0),
    (2_000_000, 160_000.0),
    (2_500_000, 260_000.0),
    (3_000_000, 395_000.0),
    (4_000_000, 665_000.0),
    (4_500_000, 810_000.0),
    (5_000_000, 955_000.0),
]


@requires_corpus
@pytest.mark.parametrize("income, expected", TAX_CASES)
def test_resident_income_tax_slabs(income, expected):
    r = tax.income_tax(income)
    assert r["tax_npr"] == pytest.approx(expected)
    assert sum(s["tax"] for s in r["slabs"]) == pytest.approx(expected)
    assert all(p["citation"] for p in r["provisions"])


@requires_corpus
def test_income_tax_first_slab_exemption_and_reliefs():
    assert tax.income_tax(1_500_000, first_slab_exempt=True)["tax_npr"] == pytest.approx(50_000.0)  # the first Rs 10 lakh is not taxed
    assert tax.income_tax(500_000, first_slab_exempt=True)["tax_npr"] == 0.0
    assert tax.income_tax(1_500_000, woman_salary_only=True)["tax_npr"] == pytest.approx(54_000.0)  # 10% off the tax
    assert tax.income_tax(1_500_000, insurance_premium=60_000)["tax_npr"] == pytest.approx(56_000.0)  # deduction capped at 40,000
    assert tax.income_tax(1_500_000, insurance_premium=25_000)["tax_npr"] == pytest.approx(10_000 + 475_000 * 0.10)
    assert tax.income_tax(1_500_000, remote_allowance=70_000)["tax_npr"] == pytest.approx(10_000 + 450_000 * 0.10)  # capped at 50,000
    assert tax.income_tax(1_500_000, disabled=True)["tax_npr"] == pytest.approx(10_000.0)  # extra deduction of Rs 5 lakh
    assert tax.income_tax(300_000, disabled=True)["tax_npr"] == 0.0  # deductions cannot make income negative
    r = tax.income_tax(1_500_000, insurance_premium=40_000, remote_allowance=50_000, disabled=True, woman_salary_only=True)
    assert r["income_after_deductions"] == 910_000.0 and r["tax_npr"] == pytest.approx(9_100.0 * 0.9)


@requires_corpus
def test_non_resident_pays_a_flat_25_percent():
    r = tax.income_tax(1_000_000, resident=False)
    assert r["tax_npr"] == 250_000.0 and r["effective_rate_pct"] == 25.0 and r["slabs"] == []
    assert tax.income_tax(0, resident=False)["tax_npr"] == 0.0


@pytest.mark.parametrize("kwargs", [dict(taxable_income=-1), dict(taxable_income=2e12), dict(taxable_income=100, insurance_premium=-1),
                                     dict(taxable_income=100, remote_allowance=-1)])
def test_income_tax_rejects_bad_input(kwargs):
    with pytest.raises(ValueError):
        tax.income_tax(**kwargs)


TDS_CASES = [
    ("default", 100_000, None, 15.0, 15_000.0, True),
    ("rent", 100_000, None, 10.0, 10_000.0, True),
    ("service_fee_vat_registered", 200_000, None, 1.5, 3_000.0, True),
    ("dividend", 50_000, None, 5.0, 2_500.0, True),
    ("bank_interest_individual", 10_000, None, 6.0, 600.0, True),
    ("insurance_agent_commission", 10_000, None, 20.0, 2_000.0, True),
    ("windfall_gain", 1_000_000, None, 25.0, 250_000.0, True),
    ("contract", 60_000, None, 1.5, 900.0, True),
    ("contract", 50_000, None, 0.0, 0.0, False),  # "more than Rs 50,000" - exactly 50,000 is out
    ("contract", 40_000, None, 0.0, 0.0, False),
    ("contract", 40_000, 60_000, 1.5, 600.0, True),  # aggregated with earlier payments under the same contract
]


@requires_corpus
@pytest.mark.parametrize("ptype, amount, aggregated, rate, tds_amount, applies", TDS_CASES)
def test_tds(ptype, amount, aggregated, rate, tds_amount, applies):
    r = tax.tds(ptype, amount, aggregated)
    assert (r["rate_pct"], r["tds_npr"], r["applies"]) == (rate, tds_amount, applies)
    assert r["net_payable_npr"] == pytest.approx(amount - tds_amount)
    assert r["provisions"][0]["citation"]


@pytest.mark.parametrize("args", [("nonsense", 100), ("rent", 0), ("rent", -5), ("rent", 2e12), ("contract", 100, 0)])
def test_tds_rejects_bad_input(args):
    with pytest.raises(ValueError):
        tax.tds(*args)


@requires_corpus
def test_tds_types_table():
    types = tax.tds_types()
    assert len(types) >= 14 and {t["id"] for t in types} == set(tax.TDS_TYPES)
    assert all(t["provision"]["citation"] and t["rate_pct"] > 0 for t in types)


# ================================================================ calculators: court fee ====

FLAT_FEE_CASES = [
    ("divorce", 500.0), ("land_registration_or_mutation", 500.0), ("kinship", 500.0), ("injunction", 500.0),
    ("declaration_of_death", 500.0), ("insolvency", 500.0), ("guardian", 500.0), ("easement", 500.0),
    ("partition_share", 1000.0), ("set_aside_document", 1000.0),
    ("contract_no_amount", 2500.0), ("other_no_value", 1000.0),
]


@requires_corpus
@pytest.mark.parametrize("case_type, fee", FLAT_FEE_CASES)
def test_flat_court_fees(case_type, fee):
    r = court_fee.flat_fee(case_type)
    assert r["court_fee_npr"] == fee and r["filing_fee_npr"] == 200.0 and r["total_npr"] == fee + 200.0
    assert r["provision"]["citation"] and r["filing_fee_provision"]["citation"]


@requires_corpus
def test_every_flat_fee_type_is_listed_and_cited():
    types = court_fee.flat_fee_types()
    assert len(types) == len(court_fee.FLAT_FEE_CASE_TYPES) >= 20
    assert all(t["provision"]["citation"] and t["fee_npr"] in (500.0, 1000.0, 2500.0) for t in types)


def test_flat_fee_rejects_an_unknown_case_type():
    with pytest.raises(ValueError):
        court_fee.flat_fee("whatever")


@requires_corpus
@pytest.mark.parametrize("value, fee", [(10_000, 0.0 + 50.0), (500_000, 1150.0), (2_500_000, 4150.0)])
def test_review_fee_is_ten_percent_of_the_plaint_fee(value, fee):
    # plaint fee on Rs 10,000 is the Rs 500 base -> 50; on 5,00,000 it is 11,500 -> 1,150; on 25,00,000 it is 41,500 -> 4,150
    assert court_fee.review_fee(value)["review_fee_npr"] == pytest.approx(fee)


@requires_corpus
@pytest.mark.parametrize("paid, before, kept, refunded", [(10_000, True, 2500.0, 7500.0), (10_000, False, 5000.0, 5000.0), (777.77, True, 194.44, 583.33)])
def test_settlement_fee(paid, before, kept, refunded):
    r = court_fee.settlement_fee(paid, before)
    assert (r["retained_npr"], r["refunded_npr"]) == (kept, refunded)
    assert r["provision"]["citation"]


def test_court_fee_extensions_reject_non_positive_values():
    with pytest.raises(ValueError):
        court_fee.review_fee(0)
    with pytest.raises(ValueError):
        court_fee.settlement_fee(0, True)
    with pytest.raises(ValueError):
        court_fee.settlement_fee(-10, False)


# =========================================================== calculators: date tools ====

ADD_TO_DATE_CASES = [
    # start (BS), years, months, days, expected (BS)
    ((2081, 1, 15), 0, 6, 0, (2081, 7, 15)),
    ((2081, 5, 31), 0, 1, 0, (2081, 6, 30)),
    ((2081, 1, 15), 1, 2, 3, (2082, 3, 18)),
    ((2081, 12, 31), 1, 0, 0, (2082, 12, 30)),
    ((2081, 3, 10), 0, -3, 0, (2080, 12, 10)),
    ((2081, 1, 31), 0, 1, 1, (2081, 2, 32)),  # the month is applied first (-> 31 Jestha), then one day (Jestha 2081 has 32 days)
    ((2081, 1, 1), 0, 0, 0, (2081, 1, 1)),
    ((2081, 1, 15), 0, 0, -15, (2080, 12, 30)),  # days go back across a month boundary (Chaitra 2080 has 30 days)
]


@requires_corpus
@pytest.mark.parametrize("start, years, months, days_, expected", ADD_TO_DATE_CASES)
def test_add_to_date(start, years, months, days_, expected):
    r = datetools.add_to_date(bs(*start), years, months, days_)
    assert r["result_bs"] == "%04d-%02d-%02d" % expected
    assert r["start_bs"] == "%04d-%02d-%02d" % start
    assert all(p["citation"] for p in r["provisions"])


@requires_corpus
def test_date_difference_tool():
    r = datetools.difference(bs(2081, 1, 31), bs(2082, 3, 1))
    assert (r["years"], r["months"], r["days"], r["total_days"], r["end_is_before_start"]) == (1, 1, 1, 398, False)
    back = datetools.difference(bs(2082, 3, 1), bs(2081, 1, 31))
    assert back["end_is_before_start"] is True and back["total_days"] == 398


def test_date_tools_reject_dates_outside_the_table():
    with pytest.raises(dates.UnsupportedDate):
        datetools.add_to_date(D(1900, 1, 1), 0, 1, 0)
    with pytest.raises(dates.UnsupportedDate):
        datetools.add_to_date(bs(2100, 12, 30), 0, 1, 0)
    with pytest.raises(dates.UnsupportedDate):
        datetools.difference(D(1900, 1, 1), D(2024, 1, 1))


# ==================================================================== calculators: age ====

AGE_CASES = [
    # birth (BS), as-of (BS), years, months, days
    ((2060, 5, 10), (2083, 6, 12), 23, 1, 2),
    ((2060, 5, 10), (2060, 5, 10), 0, 0, 0),
    ((2060, 5, 10), (2060, 5, 11), 0, 0, 1),
    ((2065, 1, 1), (2083, 1, 1), 18, 0, 0),  # exactly 18 on the anniversary
    ((2065, 1, 1), (2082, 12, 30), 17, 11, 29),  # the day before (Chaitra 2082 has 30 days)
    ((2070, 6, 15), (2083, 6, 14), 12, 11, 30),  # Bhadra 2083 has 31 days, so 15 Bhadra -> 14 Ashwin is 30 days
]


@requires_corpus
@pytest.mark.parametrize("birth, as_of, years, months, days", AGE_CASES)
def test_age_on(birth, as_of, years, months, days):
    r = age.age_on(bs(*birth), bs(*as_of))
    assert (r["years"], r["months"], r["days"]) == (years, months, days)
    assert r["birth_date_bs"] == "%04d-%02d-%02d" % birth
    assert len(r["thresholds"]) == 3


@requires_corpus
def test_age_thresholds_reached_and_dates():
    r = age.age_on(bs(2070, 1, 1), bs(2083, 1, 1))  # 13 years old
    by_years = {t["years"]: t for t in r["thresholds"]}
    assert by_years[10]["reached"] is True and by_years[10]["reached_on_bs"] == "2080-01-01"
    assert by_years[18]["reached"] is False and by_years[18]["reached_on_bs"] == "2088-01-01"
    assert by_years[20]["reached"] is False and by_years[20]["reached_on_bs"] == "2090-01-01"
    turned = age.age_on(bs(2060, 1, 1), bs(2080, 1, 1))  # exactly 20
    assert all(t["reached"] for t in turned["thresholds"])
    assert all(p["citation"] for t in turned["thresholds"] for p in t["provisions"])


@requires_corpus
def test_age_birthday_clips_at_the_end_of_a_shorter_month():
    # born on 32 Jestha 2081; Jestha 2082 has only 31 days, so the first birthday is 31 Jestha 2082
    r = age.age_on(bs(2081, 2, 32), bs(2082, 3, 1))
    assert (r["years"], r["months"], r["days"]) == (1, 0, 1)


def test_age_rejects_an_as_of_date_before_birth():
    with pytest.raises(ValueError):
        age.age_on(bs(2070, 1, 1), bs(2069, 12, 30))


@requires_corpus
def test_age_markers_table():
    assert [m["years"] for m in age.markers_table()] == [10, 18, 20]
    assert all(p["citation"] for m in age.markers_table() for p in m["provisions"])


# ========================================================================= tools API ====

@pytest.fixture(scope="module")
def api():
    from app.main import app
    with TestClient(app) as client:
        yield client


PREFIX = "/api/calculators"

OK_CASES = [
    # path, params, key that must be present in the JSON
    ("/limitation/deadline", dict(claim_id="labour_dispute_complaint", trigger_date="2081-01-15", calendar="bs", as_of="2081-02-01"), "deadline_bs"),
    ("/limitation/deadline", dict(claim_id="labour_dispute_complaint", trigger_date="2024-05-01"), "deadline"),
    ("/labour/hours", {}, "normal_day_hours"),
    ("/labour/hours/check", dict(hours_per_day=9, overtime_per_day=5), "issues"),
    ("/labour/overtime", dict(overtime_hours=3, basic_monthly_pay=26000, paid_days_per_month=26), "overtime_pay_npr"),
    ("/labour/overtime", dict(overtime_hours=3, period="week", basic_hourly_pay=100), "overtime_pay_npr"),
    ("/labour/leave", {}, "entitlements"),
    ("/labour/leave/accrual", dict(days_worked=400, months_worked_in_year=8), "home_leave_days"),
    ("/labour/leave/encashment", dict(home_leave_days=30, sick_leave_days=10, daily_basic_pay=900), "amount_npr"),
    ("/labour/maternity", dict(expected_delivery="2083-06-15", calendar="bs"), "leave_end"),
    ("/labour/maternity", dict(expected_delivery="2026-10-01", leave_start="2026-09-10", extra_month_recommended="true"), "extra_unpaid_month"),
    ("/labour/festival-allowance", dict(basic_monthly_pay=30000, months_of_service=6), "amount_npr"),
    ("/labour/fund-contributions", dict(basic_monthly_pay=30000, months=12), "period_total"),
    ("/labour/notice-tiers", {}, "tiers"),
    ("/interest/rules", {}, "max_annual_rate_pct"),
    ("/interest/simple", dict(principal=100000, start_date="2080-01-01", end_date="2081-01-01", calendar="bs", rate=24), "interest_npr"),
    ("/interest/simple", dict(principal=100000, start_date="2024-01-01", end_date="2024-07-01", interest_stated="false"), "interest_npr"),
    ("/tax/income", dict(taxable_income=1800000), "tax_npr"),
    ("/tax/income", dict(taxable_income=1800000, resident="false"), "tax_npr"),
    ("/tax/income", dict(taxable_income=900000, first_slab_exempt="true", woman_salary_only="true", disabled="true", insurance_premium=30000, remote_allowance=10000), "tax_npr"),
    ("/tax/tds", dict(payment_type="rent", amount=100000), "tds_npr"),
    ("/tax/tds", dict(payment_type="contract", amount=30000, aggregated_amount=70000), "tds_npr"),
    ("/court-fee/flat-types", {}, None),
    ("/tax/tds-types", {}, None),
    ("/court-fee/flat", dict(case_type="divorce"), "court_fee_npr"),
    ("/court-fee/review", dict(contested_value=500000), "review_fee_npr"),
    ("/court-fee/settlement", dict(fee_paid=10000, before_evidence="false"), "refunded_npr"),
    ("/date/add", dict(date="2081-01-15", months=6), "result_bs"),
    ("/date/add", dict(date="2024-04-27", calendar="ad", years=1, months=-2, days=10), "result"),
    ("/date/difference", dict(start="2081-01-01", end="2082-03-05"), "total_days"),
    ("/date/age", dict(birth_date="2060-05-10", as_of="2083-06-12"), "thresholds"),
    ("/date/age", dict(birth_date="2000-01-01", calendar="ad", as_of="2024-01-01"), "years"),
    ("/date/age-markers", {}, None),
]


@requires_corpus
@pytest.mark.parametrize("path, params, key", OK_CASES, ids=[f"{p}?{','.join(q)}" for p, q, _ in OK_CASES])
def test_tools_endpoint_ok(api, path, params, key):
    r = api.get(PREFIX + path, params=params)
    assert r.status_code == 200, r.text
    body = r.json()
    if key:
        assert key in body
    assert "citation" in r.text  # every result cites the section its numbers come from


@requires_corpus
def test_tools_endpoint_values(api):
    r = api.get(f"{PREFIX}/labour/overtime", params=dict(overtime_hours=3, basic_monthly_pay=26000, paid_days_per_month=26)).json()
    assert r["overtime_pay_npr"] == 562.5 and r["within_legal_limit"] is True
    r = api.get(f"{PREFIX}/tax/income", params=dict(taxable_income=3000000)).json()
    assert r["tax_npr"] == 395000.0
    r = api.get(f"{PREFIX}/date/add", params=dict(date="2081-05-31", months=1)).json()
    assert r["result_bs"] == "2081-06-30"
    r = api.get(f"{PREFIX}/date/difference", params=dict(start="2081-01-31", end="2082-03-01")).json()
    assert (r["years"], r["months"], r["days"], r["total_days"]) == (1, 1, 1, 398)
    r = api.get(f"{PREFIX}/interest/simple", params=dict(principal=100000, start_date="2024-01-01", end_date="2024-12-31", rate=24)).json()
    assert r["interest_npr"] == 10000.0 and r["excess_over_legal_max_npr"] == 14000.0


@requires_corpus
def test_limitation_deadline_endpoint_matches_the_calculator(api):
    r = api.get(f"{PREFIX}/limitation/deadline", params=dict(claim_id="cheque_dishonour_complaint", trigger_date="2081-12-31", calendar="bs", as_of="2082-01-01"))
    body = r.json()
    assert body["deadline_bs"]["iso"] == "2082-12-30"
    assert body["is_time_barred"] is False and body["provision"]["citation"] and body["needs_review"] is False
    assert body["period"]["text"]["en"] == "1 year"
    lst = api.get(f"{PREFIX}/limitation/deadline", params=dict(claim_id="civil_462_a_preemption", trigger_date="2081-01-15", calendar="bs",
                                                                 long_stop_date="2080-08-01", as_of="2081-01-20")).json()
    assert lst["long_stop"]["deadline_bs"]["iso"] == "2081-02-01"
    assert lst["deadline_bs"]["iso"] == "2081-02-01"


@requires_corpus
def test_limitation_catalog_endpoint(api):
    r = api.get(f"{PREFIX}/limitation/catalog")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 200
    ids = {e["id"] for g in body["categories"] for e in g["entries"]}
    assert set(LEGACY) <= ids
    assert {g["id"] for g in body["categories"]} >= {"civil", "criminal", "family", "labour"}
    sample = next(e for g in body["categories"] for e in g["entries"] if e["id"] == "partition_disagreement")
    assert sample["citation"]["law_title_ne"] == CIV and sample["citation"]["section"] == "235" and sample["citation"]["clause"] == "(ख)"
    assert sample["citation"]["resolved"] and sample["citation"]["slug"] and sample["period"]["text"]["en"] == "3 months"
    assert sample["start"]["ne"] and sample["computable"] is True
    assert len(body["general_rules"]) >= 10


@requires_corpus
def test_legacy_limitation_endpoints_keep_working(api):
    types = api.get(f"{PREFIX}/limitation/claim-types").json()
    assert set(LEGACY) <= set(types) and types == sorted(types)
    r = api.get(f"{PREFIX}/limitation", params=dict(claim_type="cheque_dishonour_complaint", trigger_date="2024-01-01"))
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"claim_type", "trigger_date", "deadline", "days_remaining", "is_time_barred", "note", "provision"}
    assert body["is_time_barred"] is True and body["note"]["en"] and body["note"]["ne"] and "दफा" in body["provision"]["citation"]
    assert api.get(f"{PREFIX}/limitation", params=dict(claim_type="civil_235_a_no_partition", trigger_date="2024-01-01")).status_code == 400
    assert api.get(f"{PREFIX}/limitation", params=dict(claim_type="zzz", trigger_date="2024-01-01")).status_code == 400


BAD_CASES = [
    # path, params, expected status
    # -- unbounded / non-positive numbers: rejected by Query bounds (422)
    ("/tax/income", dict(taxable_income=-1), 422),
    ("/tax/income", dict(taxable_income=1e13), 422),
    ("/tax/income", dict(taxable_income="abc"), 422),
    ("/tax/income", dict(taxable_income="nan"), 422),
    ("/tax/income", dict(taxable_income="inf"), 422),
    ("/tax/tds", dict(payment_type="rent", amount=0), 422),
    ("/tax/tds", dict(payment_type="rent", amount=1e13), 422),
    ("/labour/overtime", dict(overtime_hours=0, basic_hourly_pay=100), 422),
    ("/labour/overtime", dict(overtime_hours=169, basic_hourly_pay=100), 422),
    ("/labour/overtime", dict(overtime_hours=2, basic_hourly_pay=-1), 422),
    ("/labour/overtime", dict(overtime_hours=2, basic_monthly_pay=1000, paid_days_per_month=32), 422),
    ("/labour/overtime", dict(overtime_hours=2, basic_hourly_pay=100, period="year"), 422),
    ("/labour/hours/check", dict(hours_per_day=25), 422),
    ("/labour/hours/check", dict(hours_per_day=8, hours_per_week=169), 422),
    ("/labour/leave/accrual", dict(days_worked=-1), 422),
    ("/labour/leave/accrual", dict(days_worked=40001), 422),
    ("/labour/festival-allowance", dict(basic_monthly_pay=0), 422),
    ("/labour/festival-allowance", dict(basic_monthly_pay=100, months_of_service=1201), 422),
    ("/labour/fund-contributions", dict(basic_monthly_pay=100, months=0), 422),
    ("/labour/fund-contributions", dict(basic_monthly_pay=100, months=1201), 422),
    ("/interest/simple", dict(principal=0, start_date="2024-01-01", end_date="2024-02-01"), 422),
    ("/interest/simple", dict(principal=1e13, start_date="2024-01-01", end_date="2024-02-01"), 422),
    ("/interest/simple", dict(principal=100, start_date="2024-01-01", end_date="2024-02-01", rate=1001), 422),
    ("/court-fee/review", dict(contested_value=0), 422),
    ("/court-fee/settlement", dict(fee_paid=-5), 422),
    ("/date/add", dict(date="2081-01-15", years=301), 422),
    ("/date/add", dict(date="2081-01-15", months=-3601), 422),
    ("/date/add", dict(date="2081-01-15", days=110001), 422),
    # -- malformed dates / parameters (422)
    ("/date/age", dict(birth_date="2081-1-1"), 422),
    ("/date/age", dict(birth_date="20810101"), 422),
    ("/date/age", dict(birth_date="2081-01-01", calendar="julian"), 422),
    ("/date/difference", dict(start="2081-01-01"), 422),  # missing end
    ("/limitation/deadline", dict(claim_id="Bad Id!", trigger_date="2024-01-01"), 422),
    ("/limitation/deadline", dict(claim_id="x" * 101, trigger_date="2024-01-01"), 422),
    ("/limitation/deadline", dict(claim_id="partition_disagreement", trigger_date="tomorrow"), 422),
    ("/limitation/deadline", dict(claim_id="partition_disagreement"), 422),
    ("/tax/tds", dict(payment_type="rent; drop table", amount=10), 422),
    # -- well-formed but outside the supported calendar / impossible: 400 with a message
    ("/date/age", dict(birth_date="2081-13-01", calendar="bs"), 400),
    ("/date/age", dict(birth_date="2101-01-01", calendar="bs"), 400),
    ("/date/age", dict(birth_date="1974-12-30", calendar="bs"), 400),
    ("/date/age", dict(birth_date="2024-02-30", calendar="ad"), 400),
    ("/date/age", dict(birth_date="1900-01-01", calendar="ad"), 400),
    ("/date/age", dict(birth_date="2060-01-01", calendar="bs", as_of="2059-01-01"), 400),
    ("/date/add", dict(date="2100-12-30", years=5), 400),
    ("/date/add", dict(date="2081-01-01", years=-300), 400),
    ("/interest/simple", dict(principal=100, start_date="2024-02-01", end_date="2024-01-01"), 400),
    ("/interest/simple", dict(principal=100, start_date="1900-01-01", end_date="2024-01-01"), 400),
    ("/labour/overtime", dict(overtime_hours=2), 400),  # neither hourly nor monthly pay
    ("/labour/overtime", dict(overtime_hours=2, basic_monthly_pay=1000), 400),  # monthly pay without paid days
    ("/labour/maternity", dict(expected_delivery="2101-01-01", calendar="bs"), 400),
    ("/tax/tds", dict(payment_type="nonsense", amount=100), 400),
    ("/court-fee/flat", dict(case_type="nonsense"), 400),
    ("/limitation/deadline", dict(claim_id="civil_235_a_no_partition", trigger_date="2024-01-01"), 400),  # no period to compute
    ("/limitation/deadline", dict(claim_id="contract_civil_claim", trigger_date="2044-01-01"), 400),  # deadline beyond the table
    ("/limitation/deadline", dict(claim_id="contract_civil_claim", trigger_date="1900-01-01"), 400),
    ("/limitation/deadline", dict(claim_id="contract_civil_claim", trigger_date="2081-02-33", calendar="bs"), 400),
    # -- unknown id: 404
    ("/limitation/deadline", dict(claim_id="not_a_claim", trigger_date="2024-01-01"), 404),
]


@requires_corpus
@pytest.mark.parametrize("path, params, status", BAD_CASES, ids=[f"{i}:{p}" for i, (p, _q, _s) in enumerate(BAD_CASES)])
def test_tools_endpoint_rejects_bad_input(api, path, params, status):
    r = api.get(PREFIX + path, params=params)
    assert r.status_code == status, r.text
    if status in (400, 404):
        assert isinstance(r.json()["detail"], str) and r.json()["detail"]


def test_tools_router_is_mounted_by_main():
    from app.main import app
    paths = {getattr(r, "path", "") for r in app.routes}
    assert "/api/calculators/limitation/catalog" in paths
    assert "/api/calculators/limitation/deadline" in paths
    # and the older chat.py calculator routes are still there
    assert "/api/calculators/limitation" in paths and "/api/calculators/limitation/claim-types" in paths
    assert "/api/calculators/court-fee" in paths
