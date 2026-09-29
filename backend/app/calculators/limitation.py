"""Limitation-period (हदम्याद) database and deadline checker (S8, extended).

Nepali law has no single general limitation period: each chapter of the Civil
and Criminal Codes ends with its own हदम्याद section and many special Acts
carry another (मुलुकी देवानी कार्यविधि संहिता दफा ४८-४९: whatever period the
claim's own law sets, from the date that law says, otherwise from the date the
cause of action arose). So this is a data file of cited entries -
`backend/app/data/limitation_periods.yaml` - not a formula.

Guarantees:
- every entry's citation is re-resolved against the live corpus when the
  catalog is built (UnresolvedProvision on a bad one), and
- `verify_entry()` re-reads the cited section's text and checks that the
  verbatim `period_phrase_ne` is in it and that the number/unit inside the
  phrase equal the entry's stated period; tests run it over every entry, so a
  corpus change or a typo fails loudly.

Deadline arithmetic follows Civil Procedure Code s. 62: days are calendar days
counted from the day after the trigger, months are Bikram Sambat calendar
months (not 30-day blocks) and a year is 12 such months (see dates.add_period).
"""
from __future__ import annotations

import datetime
import functools
import re
import unicodedata
from pathlib import Path
from typing import Any

import yaml

from ..playbooks import UnresolvedProvision, resolve_provision
from . import dates

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "limitation_periods.yaml"

UNIT_WORDS = {
    "days": ("days", "दिन"),
    "months": ("months", "महिना"),
    "years": ("years", "वर्ष"),
}


class UnknownClaimType(ValueError):
    pass


class NotComputable(UnknownClaimType):
    """The entry states no plain period (no limitation / a special rule), so
    there is no deadline to compute. Subclasses UnknownClaimType so the legacy
    route turns it into a 400 with the message."""


# --------------------------------------------------------------------------- loading ---

@functools.lru_cache(maxsize=1)
def _raw() -> dict:
    with DATA_FILE.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def raw_entries() -> list[dict]:
    return _raw()["entries"]


@functools.lru_cache(maxsize=1)
def _by_id() -> dict[str, dict]:
    entries = _raw()["entries"]
    by_id = {e["id"]: e for e in entries}
    if len(by_id) != len(entries):  # pragma: no cover - guarded by a test as well
        raise ValueError("duplicate limitation entry ids in limitation_periods.yaml")
    return by_id


def get_entry(claim_type: str) -> dict:
    entry = _by_id().get(claim_type)
    if entry is None:
        raise UnknownClaimType(f"{claim_type!r} is not a known claim type; see list_claim_types()")
    return entry


def general_rules() -> list[dict]:
    """The Codes' general rules about limitation (what it is, when it starts, how it is counted, ...)."""
    return _raw().get("general_rules", [])


def is_computable(entry: dict) -> bool:
    return entry["period"]["kind"] == "fixed"


def list_claim_types() -> list[str]:
    """Ids of every entry that has a plain period a deadline can be computed for."""
    return sorted(e["id"] for e in raw_entries() if is_computable(e))


# ------------------------------------------------------------------- period wording ---

_DEVANAGARI = str.maketrans("0123456789", "०१२३४५६७८९")


def ne_digits(n: int | str) -> str:
    return str(n).translate(_DEVANAGARI)


def period_text(period: dict) -> dict:
    """Human wording of a period in both languages ("6 months" / "६ महिना")."""
    kind = period["kind"]
    if kind == "fixed":
        v, unit = period["value"], period["unit"]
        en_unit, ne_unit = UNIT_WORDS[unit]
        if v == 1:
            en_unit = en_unit[:-1]
        return {"en": f"{v} {en_unit}", "ne": f"{ne_digits(v)} {ne_unit}"}
    if kind == "none":
        return {"en": "No limitation", "ne": "हदम्याद लाग्दैन"}
    text = period.get("text") or {}
    return {"en": text.get("en", "Special rule"), "ne": text.get("ne", "विशेष व्यवस्था")}


def _legacy_note(entry: dict) -> dict:
    """The old {en, ne} note the first version's API returned."""
    notes = entry.get("notes")
    if notes:
        return {"en": notes["en"], "ne": notes["ne"]}
    pt = period_text(entry["period"])
    start = entry.get("start", {})
    return {
        "en": f"{entry['name']['en']}: {pt['en']} from {start.get('en', 'the trigger date')}.",
        "ne": f"{entry['name']['ne']}: {start.get('ne', 'सुरु मिति')} {pt['ne']}।",
    }


# ---------------------------------------------------------------------- the catalog ---

@functools.lru_cache(maxsize=1)
def _resolved_citations() -> dict[str, dict | None]:
    """Resolve every entry's citation once. None marks a citation the corpus
    no longer carries (the tests fail on it; the API degrades instead of 500)."""
    out: dict[str, dict | None] = {}
    for e in raw_entries():
        try:
            out[e["id"]] = resolve_provision({"law_title_ne": e["citation"]["law_title_ne"], "section": e["citation"]["section"]})
        except UnresolvedProvision:
            out[e["id"]] = None
    return out


def resolved_citation(entry: dict) -> dict | None:
    return _resolved_citations().get(entry["id"])


def entry_view(entry: dict) -> dict:
    """The public JSON shape of one entry (also what the catalog lists)."""
    laws = _raw().get("laws", {})
    cit = entry["citation"]
    resolved = resolved_citation(entry)
    period = dict(entry["period"])
    period["text"] = period_text(entry["period"])
    view: dict[str, Any] = {
        "id": entry["id"],
        "category": entry["category"],
        "name": entry["name"],
        "period": period,
        "start": entry.get("start"),
        "applies_to": entry.get("applies_to"),
        "notes": entry.get("notes"),
        "long_stop": entry.get("long_stop"),
        "keywords": entry.get("keywords", []),
        "needs_review": bool(entry.get("needs_review")),
        "computable": is_computable(entry),
        "citation": {
            "law_title_ne": cit["law_title_ne"],
            "law_en": laws.get(cit["law_title_ne"], {}).get("en"),
            "section": cit["section"],
            "clause": cit.get("clause"),
            "slug": resolved["slug"] if resolved else None,
            "citation": resolved["citation"] if resolved else None,
            "url": resolved["url"] if resolved else None,
            "resolved": resolved is not None,
        },
    }
    if entry["period"]["kind"] == "fixed" and entry.get("long_stop"):
        ls = dict(entry["long_stop"])
        ls["text"] = period_text({"kind": "fixed", "value": ls["value"], "unit": ls["unit"]})
        view["long_stop"] = ls
    return view


def catalog() -> dict:
    """Every entry, grouped by category (categories in the file's order)."""
    entries = [entry_view(e) for e in raw_entries()]
    groups = []
    for cat in _raw()["categories"]:
        members = [e for e in entries if e["category"] == cat["id"]]
        if members:
            groups.append({"id": cat["id"], "name": cat["name"], "entries": members})
    return {
        "total": len(entries),
        "categories": groups,
        "general_rules": [
            {"id": r["id"], "text": r["text"], "citation": _rule_citation(r)} for r in general_rules()
        ],
    }


def _rule_citation(rule: dict) -> dict | None:
    try:
        return resolve_provision(rule["citation"])
    except UnresolvedProvision:
        return None


def verify_rule(rule: dict) -> list[str]:
    """Problems with one general rule's citation (the phrase must be in the cited section)."""
    cit = rule["citation"]
    text = section_text(cit["law_title_ne"], cit["section"])
    if text is None:
        return [f"{rule['id']}: {cit['law_title_ne']} {cit['section']} not found in the corpus"]
    if normalise_text(rule["phrase_ne"]) not in normalise_text(text):
        return [f"{rule['id']}: phrase {rule['phrase_ne']!r} not in {cit['law_title_ne']} {cit['section']}"]
    return []


# --------------------------------------------------------------------- the deadline ---

def _add_period(d: datetime.date, value: int, unit: str) -> datetime.date:
    """Add a period to an (AD) date, counting months/years on the BS calendar."""
    return dates.add_period(d, value, unit)


def _bs_dict(d: datetime.date) -> dict:
    bs = dates.ad_to_bs(d)
    return {"year": bs.year, "month": bs.month, "day": bs.day, "iso": dates.bs_to_iso(bs)}


def check(
    claim_type: str,
    trigger_date: datetime.date,
    today: datetime.date | None = None,
    long_stop_trigger_date: datetime.date | None = None,
) -> dict:
    """Deadline + days remaining for `claim_type`, whose limitation clock
    started on `trigger_date`. Raises UnknownClaimType for an unlisted claim
    (and NotComputable for one with no plain period), and UnresolvedProvision
    (via resolve_provision) if the corpus no longer carries the cited section.

    Entries that also have an outer limit ("no later than 6 months after the
    instrument was passed") take it as `long_stop_trigger_date`; the earlier of
    the two deadlines then governs."""
    entry = get_entry(claim_type)
    if not is_computable(entry):
        raise NotComputable(
            f"{claim_type!r} has no fixed period to compute ({period_text(entry['period'])['en']}); "
            "read the cited section."
        )
    dates.check_ad_supported(trigger_date)
    today = today or datetime.date.today()
    period = entry["period"]
    start = trigger_date
    offset = entry.get("start", {}).get("offset_days")
    if offset:
        start = dates.add_days(trigger_date, offset)
    deadline = _add_period(start, period["value"], period["unit"])

    long_stop = entry.get("long_stop")
    long_stop_deadline = None
    if long_stop and long_stop_trigger_date is not None:
        dates.check_ad_supported(long_stop_trigger_date)
        long_stop_deadline = _add_period(long_stop_trigger_date, long_stop["value"], long_stop["unit"])
    governing = min(deadline, long_stop_deadline) if long_stop_deadline else deadline

    return {
        "claim_type": entry["id"],
        "trigger_date": trigger_date.isoformat(),
        "deadline": governing.isoformat(),
        "days_remaining": (governing - today).days,
        "is_time_barred": today > governing,
        "note": _legacy_note(entry),
        "provision": resolve_provision({"law_title_ne": entry["citation"]["law_title_ne"], "section": entry["citation"]["section"]}),
        # richer fields (the legacy response model ignores these)
        "name": entry["name"],
        "category": entry["category"],
        "period": {**entry["period"], "text": period_text(period)},
        "start": entry.get("start"),
        "trigger_date_bs": _bs_dict(trigger_date),
        "deadline_bs": _bs_dict(governing),
        "period_deadline": deadline.isoformat(),
        "long_stop": (
            {"deadline": long_stop_deadline.isoformat(), "deadline_bs": _bs_dict(long_stop_deadline)}
            if long_stop_deadline else None
        ),
        "needs_review": bool(entry.get("needs_review")),
        "clause": entry["citation"].get("clause"),
        "counting_note": {
            "en": "Days are calendar days counted from the day after the start; months and years are Bikram Sambat months (Civil Procedure Code s. 62).",
            "ne": "दिन हदम्याद प्रारम्भ भएको भोलिपल्टदेखि गनिन्छ; महिना र वर्ष वि.सं. महिना अनुसार गनिन्छ (देवानी कार्यविधि संहिता दफा ६२)।",
        },
    }


# ------------------------------------------------------------- text verification ---

_ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍﻿­"), None)
_DIGITS_TO_ASCII = str.maketrans("०१२३४५६७८९", "0123456789")

# Nepali number words as spelled in the corpus (spelling varies between acts).
NUMBER_WORDS: dict[str, int] = {
    "एक": 1, "दुई": 2, "तीन": 3, "चार": 4, "पाँच": 5, "पांच": 5, "छ": 6, "सात": 7, "आठ": 8, "नौ": 9,
    "दश": 10, "दस": 10, "पन्ध्र": 15, "बीस": 20, "बिस": 20, "तीस": 30, "तिस": 30,
    "पैँतीस": 35, "पैंतीस": 35, "पैतीस": 35, "पैतिस": 35, "पैंतिस": 35,
    "साठी": 60, "साठि": 60, "सत्तरी": 70, "नब्बे": 90,
}
_UNIT_PREFIX = {"दिन": "days", "महिना": "months", "वर्ष": "years"}


def normalise_text(text: str) -> str:
    """Comparison form of a corpus text/phrase: NFC, no zero-width marks, Devanagari
    digits -> ASCII, and ALL whitespace removed (line breaks fall inside words in
    the scanned sources)."""
    text = unicodedata.normalize("NFC", text).translate(_ZERO_WIDTH).translate(_DIGITS_TO_ASCII)
    text = re.sub(r"[\ue000-\uf8ff]", "", text)  # private-use glyphs left by the PDF conversion
    return re.sub(r"\s+", "", text)


def parse_period_phrase(phrase: str) -> tuple[int, str] | None:
    """(value, unit) of the number+unit at the start of a phrase like
    'छ महिनाभित्र' or '9० दिनभित्र', or None if it does not start with one."""
    p = normalise_text(phrase)
    m = re.match(r"(\d+)(दिन|महिना|वर्ष)", p)
    if m:
        return int(m.group(1)), _UNIT_PREFIX[m.group(2)]
    for word in sorted(NUMBER_WORDS, key=len, reverse=True):
        if p.startswith(word):
            rest = p[len(word):]
            for prefix, unit in _UNIT_PREFIX.items():
                if rest.startswith(prefix):
                    return NUMBER_WORDS[word], unit
    return None


def section_text(law_title_ne: str, section: str) -> str | None:
    from ..retrieval import doc_slug, get_index

    entry = get_index().section(doc_slug(law_title_ne), section)
    return (entry or {}).get("text_ne")


def verify_entry(entry: dict) -> list[str]:
    """Problems (empty when fine) with one entry's citation and stated period:
    the section must exist, the verbatim phrase must be in its text and, for a
    fixed period, the number and unit in the phrase must equal the entry's."""
    problems: list[str] = []
    cit = entry["citation"]
    text = section_text(cit["law_title_ne"], cit["section"])
    if text is None:
        return [f"{entry['id']}: {cit['law_title_ne']} {cit['section']} not found in the corpus"]
    haystack = normalise_text(text)
    checks = [(entry.get("period_phrase_ne"), entry["period"])]
    if entry.get("long_stop"):
        ls = entry["long_stop"]
        checks.append((ls.get("period_phrase_ne"), {"kind": "fixed", "value": ls["value"], "unit": ls["unit"]}))
    for phrase, period in checks:
        if not phrase:
            problems.append(f"{entry['id']}: missing period_phrase_ne")
            continue
        if normalise_text(phrase) not in haystack:
            problems.append(f"{entry['id']}: phrase {phrase!r} not in {cit['law_title_ne']} {cit['section']}")
            continue
        if period["kind"] == "fixed":
            parsed = parse_period_phrase(phrase)
            if parsed != (period["value"], period["unit"]):
                problems.append(f"{entry['id']}: phrase {phrase!r} reads as {parsed}, entry says {(period['value'], period['unit'])}")
    return problems
