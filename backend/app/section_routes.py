"""V2.7: verified keyword -> SECTION routes.

A playbook pins the governing sections of one situation it was written for, and the matcher picks ONE playbook,
so a question with two issues (unpaid wages AND "the company won't let me resign"), a situation with no playbook
(a forged signature on a land sale, an edited photo) or a plan the relevance gate dropped (b03) never saw the
section that governs it. The V3.3 set-B review found ~14 such misses with the governing section in the corpus.

A route is a small, auditable DATA row (`data/section_routes.yaml`):

    - id: ...
      all:   [[alt, alt, ...], [alt, ...]]   # EVERY group must have an alternative present in the message
      not:   [alt, ...]                      # none of these may be present (a different situation)
      provisions: [{law_title_ne, section}]  # statute sections that govern it (verified against the corpus by a test)
      suppress:   [{law_title_ne, section}]  # sections known to be the WRONG law for this situation
      source: where the row came from; status NEEDS-ADVOCATE-REVIEW (docs/PLAYBOOK_AUDIT.md)

An alternative is a Devanagari substring, or a Latin word / phrase matched word by word with spelling tolerance
(translit.canon: nakali = nakkali; a Latin word of >= 4 letters may carry a suffix: bechne ~ bech). Routed
sections are put right behind the playbook's pins (never ahead of them) and are marked `routed` + `pinned`: the
topical-fit gate never fails them, because a person verified them against the corpus text. This is NOT legal
judgement about the facts: it only guarantees that the section the situation is *about* is in front of the model.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from . import translit
from .playbooks import lookup_entry
from .retrieval import doc_slug

log = logging.getLogger("kanooni.routes")

ROUTES_PATH = Path(__file__).parent / "data" / "section_routes.yaml"
ROUTE_MAX = 3  # at most this many routed sections that no playbook pins are added to one question
ROUTE_SCAN = 8  # routes are read until this many sections are collected (the caller applies ROUTE_MAX / the room left)

_PUA = re.compile("[-]")
_LATIN_TOK = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Alt:
    dev: str | None                       # Devanagari substring
    words: tuple[str, ...] = ()           # Latin words (canonical form) in order


@dataclass(frozen=True)
class Route:
    id: str
    groups: tuple[tuple[Alt, ...], ...]
    nots: tuple[Alt, ...]
    provisions: tuple[dict, ...]
    suppress: tuple[dict, ...]
    source: str = ""


def _alt(raw: str) -> Alt:
    raw = unicodedata.normalize("NFC", str(raw)).strip().lower()
    if re.search(r"[ऀ-ॿ]", raw):
        return Alt(dev=" ".join(raw.split()))
    return Alt(dev=None, words=tuple(c for c in (translit.canon(w) for w in _LATIN_TOK.findall(raw)) if c))


@lru_cache(maxsize=1)
def load_routes() -> tuple[Route, ...]:
    try:
        rows = yaml.safe_load(ROUTES_PATH.read_text(encoding="utf-8")) or []
    except Exception as e:  # noqa: BLE001 - routing is an extra; never break retrieval
        log.warning("section routes unavailable: %s", e)
        return ()
    out = []
    for r in rows:
        out.append(Route(
            id=r["id"],
            groups=tuple(tuple(_alt(a) for a in g) for g in r["all"]),
            nots=tuple(_alt(a) for a in r.get("not") or []),
            provisions=tuple(r.get("provisions") or []),
            suppress=tuple(r.get("suppress") or []),
            source=r.get("source", "")))
    return tuple(out)


def _normalise(text: str) -> tuple[str, list[str]]:
    t = unicodedata.normalize("NFC", _PUA.sub("", text or "")).lower()
    dev = " ".join(t.split())
    latin = [c for c in (translit.canon(w) for w in _LATIN_TOK.findall(t)) if c]
    return dev, latin


def _present(alt: Alt, dev: str, latin: list[str]) -> bool:
    if alt.dev is not None:
        return alt.dev in dev
    if not alt.words:
        return False
    n = len(alt.words)
    for i in range(len(latin) - n + 1):
        ok = True
        for a, m in zip(alt.words, latin[i:i + n]):
            # an exact (canonical) word, or - for a stem of >= 4 letters - the same word with a suffix glued on
            if not (m == a or (len(a) >= 4 and m.startswith(a))):
                ok = False
                break
        if ok:
            return True
    return False


def matching_routes(text: str) -> list[Route]:
    dev, latin = _normalise(text)
    out = []
    for r in load_routes():
        if any(_present(a, dev, latin) for a in r.nots):
            continue
        if all(any(_present(a, dev, latin) for a in g) for g in r.groups):
            out.append(r)
    return out


def routed_entries(text: str, limit: int = ROUTE_SCAN, skip_ids: set[str] | None = None, idx=None) -> tuple[list[dict], list[dict]]:
    """(corpus entries of the routed sections, in route order and capped at `limit`, `suppress` references of the
    routes that fired). `skip_ids`: passages already in the list (pins) are not repeated and do not use the cap."""
    from .retrieval import get_index
    idx = idx or get_index()
    skip = set(skip_ids or ())
    entries: list[dict] = []
    suppress: list[dict] = []
    for r in matching_routes(text):
        suppress += list(r.suppress)
        for ref in r.provisions:
            if len(entries) >= limit:
                break
            e = lookup_entry(idx, {"law_title_ne": ref["law_title_ne"], "section": str(ref["section"])})
            if e is None:
                log.warning("route %s: %s s.%s not found", r.id, ref["law_title_ne"], ref["section"])
                continue
            if e["id"] in skip or any(x["id"] == e["id"] for x in entries):
                continue
            e = {k: v for k, v in e.items() if k not in ("prev", "next")}
            entries.append({**e, "score": 1.0, "pinned": True, "routed": True, "route": r.id})
    return entries, suppress


def is_suppressed(entry: dict, suppress: list[dict]) -> bool:
    return any((entry.get("doc_title_ne") or "") == s["law_title_ne"]
               and str(entry.get("section") or "").split(" ")[0] == str(s["section"]).split(" ")[0]
               for s in suppress)
