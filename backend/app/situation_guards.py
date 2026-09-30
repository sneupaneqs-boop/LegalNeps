"""V3.2: a small DATA table of wrong-law guards - (what the user's question says -> provision families that
must not be cited for it). Wrong-law (a verbatim, on-topic quote from a provision that governs somebody else's
situation) was 7 of the 12 bad sentences of the V3 live review and is what deterministic quote checks cannot
see. Two patterns from that review recur and are cheap and safe to encode:

  1. a BANK / NRB loan question answered from the Civil Code's private-lender chapter (s.474-492: साहू,
     "10% a year", "no limitation for excess interest"); the governing text is the NRB directive.
  2. a wife whose husband merely LEFT (no divorce) answered from the divorced-wife provisions (s.99-102).

A guard fires only when the question contains a cue and none of the `unless` cues; the check is on the CITED
SOURCE (law + section range) or, for provisions keyed on a party word, on the cited quote. This is not legal
judgement - it is a list of known mis-fires. Anything else that needs real judgement stays with the entailment
pass (structured.entailment_filter, which now sees the question). Add a row when a live review finds a new
recurring wrong-law pattern; every row needs a test in tests/test_v32_claim_checks.py built from the review.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .text_norm import DEV_DIGITS


@dataclass(frozen=True)
class Guard:
    id: str
    why: str
    cues: tuple[re.Pattern, ...]           # ALL must match the question
    unless: tuple[re.Pattern, ...]         # NONE may match the question
    law: re.Pattern | None = None          # forbidden source: law title matches...
    sections: tuple[tuple[int, int], ...] = ()   # ...and its section number is in one of these ranges
    quote: re.Pattern | None = None        # or: the cited quote/sentence matches (a party-keyed provision)


def _r(p: str) -> re.Pattern:
    return re.compile(p, re.I)


GUARDS: tuple[Guard, ...] = (
    Guard(
        id="bank_loan_vs_private_creditor",
        why="a bank/NRB loan is governed by the regulator's directive, not the Civil Code's private-lender chapter",
        cues=(_r(r"\bbank|\bbfi\b|\bnrb\b|rastra\s*bank|बैंक|बैङ्क|राष्ट्र बैंक|वित्तीय संस्था|finance compan"),
              _r(r"\bloan|\bkarja|\bkarza|\binterest|\bbyaj|penal|hartana|\bemi\b|installment|instalment|"
                 r"ऋण|कर्जा|ब्याज|हर्जना|किस्ता")),
        unless=(_r(r"tamsuk|तमसुक|साहू|\bsahu\b|shahu|moneylender|money lender|\bfriend\b|\bsathi\b|साथी|"
                   r"neighbou?r|relative"),),
        law=_r(r"मुलुकी देवानी संहिता(?!.*कार्यविधि)|Muluki Civil Code(?!.*Procedure)"),
        sections=((474, 492),),
        quote=_r(r"साहूले|साहू"),
    ),
    Guard(
        id="separated_not_divorced",
        why="s.99-102 (maintenance/one-time payment) are for a DIVORCED wife; a husband who merely left is not a divorce",
        cues=(_r(r"chhad(?:era|yo|eko|di)|छोडेर|छाडेर|छोडिदियो|छाडिदियो|छोडी|left (?:me|us|the house|home)|"
                 r"\bdeserted?\b|abandon|walked out|bhagera|\bseparated\b"),),
        unless=(_r(r"divorc|सम्बन्ध\s*विच्छेद|पारपाचुके|bichhed|vichhed|bicched|mukti"),),
        law=_r(r"मुलुकी देवानी संहिता(?!.*कार्यविधि)|Muluki Civil Code(?!.*Procedure)"),
        sections=((99, 102),),
        quote=_r(r"सम्बन्ध\s*विच्छेद\s*भएको"),
    ),
)


def _section_no(section: str) -> int:
    m = re.match(r"\s*([0-9]+)", (section or "").translate(DEV_DIGITS))
    return int(m.group(1)) if m else -1


def violation(question: str, sentence: str, quotes: list[str], source: dict) -> str | None:
    """The id of the guard that forbids citing `source` for this question, else None."""
    if not question:
        return None
    for g in GUARDS:
        if not all(c.search(question) for c in g.cues) or any(u.search(question) for u in g.unless):
            continue
        title = " ".join(str(source.get(k) or "") for k in ("doc_title_ne", "source_ne", "source_en", "title_ne"))
        if g.law and g.sections and g.law.search(title):
            n = _section_no(str(source.get("section") or ""))
            if any(lo <= n <= hi for lo, hi in g.sections):
                return g.id
        if g.quote and any(g.quote.search(q) for q in quotes):
            return g.id
    return None
