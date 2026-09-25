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


def fold(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    return text.translate(DEV_DIGITS).translate(_FOLD).lower()


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


def tokenize(text: str) -> list[str]:
    out = []
    for tok in TOKEN_RE.findall(fold(text)):
        if DEVANAGARI_RE.match(tok):
            if tok in NE_STOP:
                continue
            s = _stem_ne(tok)
            if s and s not in NE_STOP:
                out.append(s)
        else:
            if tok in EN_STOP:
                continue
            out.append(_stem_en(tok))
    return out


def detect_language(text: str) -> str:
    dev = len(DEVANAGARI_RE.findall(text or ""))
    lat = len(re.findall(r"[A-Za-z]", text or ""))
    return "ne" if dev >= max(1, lat // 3) else "en"
