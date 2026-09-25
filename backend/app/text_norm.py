"""Normalisation + tokenisation shared by indexing and querying.

Nepali legal text is spelled inconsistently (नीति/निति, पूर्व/पुर्व,
सँग/संग, Devanagari vs ASCII digits, invisible ZWJ/ZWNJ), and meaning-bearing
stems carry postpositions (जग्गाको, जग्गालाई, जग्गामा). Both sides of the
search go through the same folding so those variants still match.
"""
from __future__ import annotations

import re
import unicodedata

DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
_FOLD = str.maketrans({
    "ी": "ि", "ू": "ु", "ँ": "ं", "ॉ": "ो", "़": None, "‌": None, "‍": None,
    "­": None, "ऋ": "रि",
})
TOKEN_RE = re.compile(r"[ऀ-ॣॱ-ॿ]+|[a-z0-9]+")
DEVANAGARI_RE = re.compile(r"[ऀ-ॿ]")

# postpositions / plural markers, longest first (after folding ी->ि, ू->ु)
NE_SUFFIXES = sorted([
    "हरुलाई", "हरुको", "हरुका", "हरुकि", "हरुले", "हरुमा", "हरुबाट", "हरुसंग", "हरु",
    "लाई", "द्वारा", "बाट", "देखि", "सम्म", "संग", "भन्दा", "प्रति", "तर्फ", "मार्फत",
    "भित्र", "बिच", "माथि", "मुनि", "पछि", "अघि",
    "को", "का", "कि", "ले", "मा",
], key=len, reverse=True)

NE_STOP = {
    "र", "वा", "तथा", "एवं", "छ", "हो", "छन्", "थियो", "भएको", "गरेको", "रहेको", "हुने", "गर्ने",
    "सो", "यो", "त्यो", "यस", "उक्त", "पनि", "नै", "भने", "भन्ने", "गरि", "हुन", "गर्न", "एक", "कुनै",
    "सबै", "आफ्नो", "तर", "जुन", "यि", "ति", "के", "कसरि", "किन", "कहाँ", "म", "मेरो", "हामि",
    "तपाई", "तपाईं", "भएमा", "गरेमा", "सक्ने", "पर्ने", "हुन्छ", "गर्छ", "छैन", "होइन", "लागि",
}
EN_STOP = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "are", "was", "be", "been",
    "it", "my", "me", "i", "we", "you", "your", "our", "can", "do", "does", "did", "what", "how",
    "when", "who", "which", "that", "this", "with", "by", "from", "at", "as", "if", "not", "no",
    "any", "will", "shall", "would", "should", "about", "under", "into", "there", "their", "they",
    "he", "she", "his", "her", "them", "have", "has", "had", "get", "got", "so", "am",
    "were", "being", "also", "than", "then", "its", "may", "must", "per", "all", "some",
}


# str.translate with a dict table is slow on long texts; chained replace does the
# same mapping ~10x faster, which matters when indexing on a small server
_REPLACEMENTS = [(chr(k), chr(v) if isinstance(v, int) else (v or ""))
                 for table in (DEV_DIGITS, _FOLD) for k, v in table.items()]


def fold(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    for a, b in _REPLACEMENTS:
        if a in text:
            text = text.replace(a, b)
    return text.lower()


def _stem_ne(tok: str) -> str:
    for suf in NE_SUFFIXES:
        if tok.endswith(suf) and len(tok) - len(suf) >= 2:
            if suf in ("का", "कि") and tok[-len(suf) - 1] == "ि":
                continue  # -िका is a noun ending (बालिका, पत्रिका, भूमिका), not a genitive
            return tok[: -len(suf)]
    return tok


def _stem_en(tok: str) -> str:
    if len(tok) <= 3 or tok.isdigit():
        return tok
    for suf, rep in (("ies", "y"), ("ing", ""), ("ed", ""), ("ment", ""), ("es", ""), ("s", "")):
        if tok.endswith(suf) and len(tok) - len(suf) >= 3:
            return tok[: -len(suf)] + rep
    return tok


def _term(tok: str) -> str:
    """Index term for one folded token ('' = drop it)."""
    if DEVANAGARI_RE.match(tok):
        if tok in NE_STOP:
            return ""
        s = _stem_ne(tok)
        return s if s and s not in NE_STOP else ""
    return "" if tok in EN_STOP else _stem_en(tok)


# Word -> term memo: the corpus has ~100k distinct words across millions of
# occurrences, so stemming each word once makes indexing ~5x faster.
_TERM_MEMO: dict[str, str] = {}


def tokenize(text: str) -> list[str]:
    memo = _TERM_MEMO
    out = []
    for tok in TOKEN_RE.findall(fold(text)):
        term = memo.get(tok)
        if term is None:
            term = _term(tok)
            if len(memo) < 1_000_000:
                memo[tok] = term
        if term:
            out.append(term)
    return out


def detect_language(text: str) -> str:
    dev = len(DEVANAGARI_RE.findall(text or ""))
    lat = len(re.findall(r"[A-Za-z]", text or ""))
    return "ne" if dev >= max(1, lat // 3) else "en"


# Common words of romanised Nepali ("malai police le pakreko cha") that are
# not English words, used to answer in Nepali when people type in Latin script.
ROMAN_NE = {
    "malai", "mero", "meri", "hamro", "timro", "tapai", "tapaai", "tapailai", "garne", "garnu", "garera",
    "gareko", "garyo", "garchu", "garchha", "garcha", "cha", "chha", "chaina", "chhaina", "ho", "hoina",
    "bhayo", "bhaye", "bhane", "bhanyo", "ke", "kasari", "kina", "kaha", "kati", "ma", "le", "lai", "ko",
    "ki", "ra", "pani", "sanga", "dekhi", "samma", "huncha", "hunchha", "parcha", "parchha", "diyena",
    "dinu", "dina", "linu", "lina", "sakchu", "sakincha", "gharbeti", "shreemati", "shrimati", "shriman",
    "shreeman", "shreemaan", "chora", "chori", "bau", "buwa", "aama", "didi", "bahini", "dai", "bhai",
    "paisa", "jagga", "ghar", "kaam", "talab", "adalat", "muddha", "mudda", "ujuri", "pakreko", "pakrau",
    "baru", "aba", "ani", "tara", "yo", "tyo", "yas", "ahile", "hijo", "bholi", "garnuparcha", "milcha",
    "milchha", "paincha", "paunchha", "paucha", "firta", "diyo", "diye", "chahiyo", "chahincha",
}


def guess_language(text: str) -> str:
    """Reply language for 'auto': Devanagari -> ne; Latin script counts as
    romanised Nepali when its words are mostly Nepali ones; else en."""
    if detect_language(text) == "ne":
        return "ne"
    words = re.findall(r"[a-z]+", (text or "").lower())
    if not words:
        return "en"
    ne_hits = sum(w in ROMAN_NE for w in words)
    en_hits = sum(w in EN_STOP for w in words)
    return "ne" if ne_hits >= 2 and ne_hits > en_hits else "en"
