"""Local English / romanised-Nepali -> statute-Nepali query expansion.

Statutes are only in Nepali, so an English question needs translating
before BM25 can match anything. The LLM query analysis does that when it's
available; this glossary (data/glossary.json, built by
scripts/build_glossary.py) does it instantly and offline, so search stays
good when the LLM is rate-limited or not configured.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

GLOSSARY_PATH = Path(__file__).parent / "data" / "glossary.json"
_WORD = re.compile(r"[a-z]+")


def _norm_en(w: str) -> str:
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def _key(phrase: str) -> tuple[str, ...]:
    return tuple(_norm_en(w) for w in _WORD.findall(phrase.lower()))


@lru_cache(maxsize=1)
def _index() -> tuple[dict[tuple[str, ...], list[str]], int]:
    if not GLOSSARY_PATH.exists():
        return {}, 0
    data = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
    idx: dict[tuple[str, ...], list[str]] = {}
    for entries in data.get("areas", {}).values():
        for e in entries:
            ne = [t for t in e.get("ne", []) if t][:3]
            for phrase in e.get("en", []) + e.get("roman", []):
                k = _key(phrase)
                if not k or (len(k) == 1 and len(k[0]) <= 2):
                    continue
                bucket = idx.setdefault(k, [])
                for t in ne:
                    if t not in bucket:
                        bucket.append(t)
    longest = max((len(k) for k in idx), default=0)
    return idx, longest


def expand(text: str, max_terms: int = 14) -> list[str]:
    """Nepali statute terms for the English/romanised phrases in `text`,
    longest phrase match first."""
    idx, longest = _index()
    if not idx:
        return []
    words = [_norm_en(w) for w in _WORD.findall(text.lower())]
    out: list[str] = []
    i = 0
    while i < len(words):
        for n in range(min(longest, len(words) - i), 0, -1):
            terms = idx.get(tuple(words[i:i + n]))
            if terms:
                for t in terms:
                    if t not in out:
                        out.append(t)
                i += n
                break
        else:
            i += 1
    return out[:max_terms]


def size() -> int:
    return len(_index()[0])
