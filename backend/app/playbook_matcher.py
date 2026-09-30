"""Non-LLM query -> playbook routing (S7).

Scores each playbook's `keywords` list against the user's query using plain
substring/token overlap - no embeddings, no LLM call. English or romanised
queries are widened first via glossary.expand() (S3) so they can still hit a
playbook's Nepali keywords. Returns the best playbook id only when the match
is confident and unambiguous; otherwise returns None so the caller falls
back to the LLM pipeline or a normal search.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from . import glossary
from .playbooks import _load_yaml_files

_WORD = re.compile(r"[a-z]+|[ऀ-ॿ]+")


def _tokens(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


@dataclass
class Match:
    playbook_id: str
    score: float


def _keyword_weight(keyword: str) -> float:
    """Longer, more specific phrases count for more than a bare one-word
    keyword, so a generic word can't single-handedly win a match."""
    n_words = len(_tokens(keyword))
    return 1.0 if n_words <= 1 else float(n_words)


@lru_cache(maxsize=1)
def _playbook_keywords() -> tuple[tuple[str, list[str]], ...]:
    return tuple((data["id"], data.get("keywords") or []) for data in _load_yaml_files())


def _query_tokens(query: str) -> set[str]:
    toks = _tokens(query)
    for term in glossary.expand(query):
        toks |= _tokens(term)
    return toks


# Function words carry no topic signal; counting them let "right to
# information" half-match "fundamental rights under the constitution".
_STOP = {"a", "an", "the", "to", "of", "in", "on", "for", "and", "or", "is", "are", "my", "me", "i",
         "from", "with", "by", "not", "no", "be", "it", "at", "as", "your", "their", "has", "have",
         "को", "का", "की", "मा", "ले", "लाई", "र", "छ", "छैन", "भएको", "गर्ने", "दिने", "पनि", "तथा"}


_GENERIC = {"हक", "अधिकार", "right", "rights", "law", "laws", "कानून", "कानुन", "ऐन", "act", "legal",
            "court", "अदालत", "case", "मुद्दा", "नेपाल", "nepal", "सरकारी", "government", "office", "कार्यालय"}


def _keyword_hit_fraction(kw: str, kw_tokens: set[str], q_tokens: set[str], q_lower: str) -> float:
    """1.0 for an exact phrase hit, else the fraction of the keyword's own
    words that appear anywhere in the query - so a query that only echoes
    part of a multi-word keyword still contributes partial credit instead
    of an all-or-nothing miss."""
    if kw.lower() in q_lower:
        return 1.0
    content = kw_tokens - _STOP
    if not content:
        return 0.0
    shared = content & q_tokens
    if len(shared) < len(content) and not (shared - _GENERIC):
        # a partial match made only of generic legal words ("हक" = right,
        # "law", "court") is not evidence of any specific situation
        return 0.0
    return len(shared) / len(content)


def score_playbooks(query: str) -> list[Match]:
    """Every playbook with a non-zero score, highest first."""
    q_tokens = _query_tokens(query)
    q_lower = query.lower()
    scores: dict[str, float] = {}
    for playbook_id, keywords in _playbook_keywords():
        # exact phrase hits add up; partial hits count once (the best one),
        # so many variants sharing one word ("श्रीमानले कुटपिट", "पतिले कुटपिट")
        # can't pile up credit from that single word
        total, best_partial = 0.0, 0.0
        for kw in keywords:
            kw_tokens = _tokens(kw)
            fraction = _keyword_hit_fraction(kw, kw_tokens, q_tokens, q_lower)
            if fraction >= 1.0:
                total += _keyword_weight(kw)
            elif fraction >= 0.5:
                best_partial = max(best_partial, _keyword_weight(kw) * fraction)
        total += best_partial
        if total > 0:
            scores[playbook_id] = total
    return sorted((Match(pid, s) for pid, s in scores.items()), key=lambda m: -m.score)


def match(query: str, min_score: float = 1.0, min_margin: float = 0.5) -> str | None:
    """Best playbook id for `query`, or None if no confident, unambiguous
    match exists. A match is confident when its score clears `min_score`
    and unambiguous when it beats the runner-up by `min_margin`."""
    ranked = score_playbooks(query)
    if not ranked:
        return None
    best = ranked[0]
    if best.score < min_score:
        return None
    if len(ranked) > 1 and (best.score - ranked[1].score) < min_margin:
        return None
    return best.playbook_id


def _reset_cache_for_tests() -> None:
    _playbook_keywords.cache_clear()
