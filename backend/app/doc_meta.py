"""Doc-level status/date metadata shared by scripts/build_corpus.py (which
computes it once per document at build time) and retrieval.py (which
computes it lazily for any corpus shard built before this existed, so
bill-exclusion works without a full corpus rebuild).

Every official Nepali law PDF opens with a printed header block giving its
certification/gazette date and a numbered list of amending acts (each name
followed by its own BS date), before the "प्रस्तावना" (preamble) text
starts. Draft bills (विधेयक) never carry this header, which is what tells
them apart from enacted law - see docs/PROGRESS.md S2 notes for samples.
"""
from __future__ import annotations

import re

DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
_DATE_RE = re.compile(r"(\d{4})[।./](\d{1,2})[।./](\d{1,2})")
_ENACT_TRIGGER_RE = re.compile(r"प्रमाण|लाल\s?मोहर|राजपत्र|assent", re.I)
_AMEND_LABELS = ("संशोधन गर्ने ऐन", "संशोधन")
_STOP_MARKERS = ("प्रस्तावना", "संवत्", "सम्वत्")


def _bs_date(m: re.Match) -> str:
    y, mo, d = m.groups()
    return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"


def _find_enacted_date(head: str) -> str | None:
    """First BS date following a certification/gazette-date trigger word,
    within the printed header (first ~700 chars, before the preamble)."""
    for m in _ENACT_TRIGGER_RE.finditer(head):
        d = _DATE_RE.search(head, m.end())
        if d and d.start() - m.end() < 70:
            return _bs_date(d)
    return None


def extract_doc_meta(preamble_text: str) -> dict:
    """status/enacted_bs/amended_by/consolidated_upto for one document, from
    its first chunk's text (the header + preamble). `status` here is only
    in_force/unknown - a bill's "no header found" case is handled by
    classify_status(), which also knows the title; detecting a
    since-repealed act is out of scope (would need a cross-document repeal
    graph)."""
    western = (preamble_text or "").translate(DEV_DIGITS)
    enacted = _find_enacted_date(western[:700])
    amended_by: list[dict] = []
    for label in _AMEND_LABELS:
        idx = western.find(label)
        if idx < 0:
            continue
        stop = len(western)
        for marker in _STOP_MARKERS:
            j = western.find(marker, idx + len(label))
            if j >= 0:
                stop = min(stop, j)
        block = western[idx + len(label):stop]
        pos = 0
        for m in _DATE_RE.finditer(block):
            name = re.sub(r"\s+", " ", block[pos:m.start()]).strip("।.,–- ")
            name = re.sub(r"^\d+\.\s*", "", name)  # drop "1. " numbering
            if name and len(name) > 6:
                amended_by.append({"name": name, "date_bs": _bs_date(m)})
            pos = m.end()
        break
    consolidated_upto = max((a["date_bs"] for a in amended_by), default=enacted)
    return {"enacted_bs": enacted, "amended_by": amended_by, "consolidated_upto": consolidated_upto}


def classify_status(title: str, meta: dict) -> str:
    if "विधेयक" in (title or ""):
        # a promulgated act whose title still contains "विधेयक" (rare, but
        # possible for a renamed bill) is still in force
        return "in_force" if meta.get("enacted_bs") else "bill"
    return "in_force" if meta.get("enacted_bs") else "unknown"
