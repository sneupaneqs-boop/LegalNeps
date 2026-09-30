"""
Pure text functions for the OCR pipeline (ocr_regulators.py): cleaning of raw
Tesseract output and the quality gate. No tesseract / PDF / corpus access here,
so they are unit-tested directly (tests/test_ocr_clean.py).

  clean_page(text)                 broken matras, stray symbols, page numbers, whitespace
  strip_running_headers(pages)     drop header/footer lines repeated on many pages
  normalise_digits(text)           Devanagari digits in Nepali lines, ASCII in English lines
  token_stats(text, ne, en)        share of Devanagari / Latin word tokens that are real words
  structural_share(text)           vocabulary-free Devanagari validity (matra placement)
  page_verdict(text, ne, en)       keep / drop a page (with the reason)
  document_verdict(pages, ...)     keep / drop a document from its page verdicts

`ne` / `en` are sets of folded (app.text_norm.fold) known words: the Nepali set is
built from the clean text already in the corpus, the English set likewise.
"""
from __future__ import annotations

import re
import sys
import os
import unicodedata

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ""))
from app.text_norm import fold  # noqa: E402

# --- character classes ------------------------------------------------------
DEV_DIGITS = "०१२३४५६७८९"
_TO_DEV = str.maketrans("0123456789", DEV_DIGITS)
_TO_ASCII = str.maketrans(DEV_DIGITS, "0123456789")

VOWEL_SIGN = "ा-ौॕ-ॗॢॣऺऻॎ"  # dependent vowel signs
SIGN_CLASS = f"[{VOWEL_SIGN}]"
MARK = "ऀ-ः़्"                       # candrabindu, anusvara, visarga, nukta, halant
DEV = "ऀ-ॿ"
DEV_WORD_RE = re.compile(r"[ऀ-ॣॱ-ॿ]{2,}")
LATIN_WORD_RE = re.compile(r"[A-Za-z]{3,}")

_CONTROL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f�﻿​‌‍­⁠]")
_STRAY_SYMBOLS = re.compile(r"[~^`_¢£¥©®§¬°¿¡¦¤¶·•●○■□▪▫◆◇♦★☆►▶◄◀¨´¸¯±×÷µ¹²³ªº«»\\]")
_PAGE_NUMBER = re.compile(
    r"^\W*(?:(?:page|pg|पृष्ठ|पेज)\W*)?[0-9०-९]{1,4}(?:\s*(?:of|/|मध्ये)\s*[0-9०-९]{1,4})?\W*$", re.I)
_LINE_ALNUM = re.compile(r"[A-Za-z0-9ऀ-ॿ]")


def clean_page(text: str) -> str:
    """Clean one page of raw OCR output. Idempotent."""
    text = unicodedata.normalize("NFC", text or "")
    text = _CONTROL.sub("", text)
    text = _STRAY_SYMBOLS.sub(" ", text)
    text = text.replace(" ", "\n").replace("\r", "\n")
    lines = []
    for raw in text.split("\n"):
        line = _fix_devanagari(raw)
        line = re.sub(r"[ \t ]+", " ", line).strip()
        if not line:
            lines.append("")
            continue
        if _PAGE_NUMBER.match(line) or _is_noise_line(line):
            continue
        lines.append(line)
    out = "\n".join(lines)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


def _fix_devanagari(line: str) -> str:
    """Repair the matra damage OCR leaves behind."""
    if not re.search(f"[{DEV}]", line):
        return line
    # independent vowel + its own sign = the long vowel OCR split in two
    line = line.replace("अा", "आ").replace("अो", "ओ").replace("अौ", "औ").replace("एे", "ऐ")
    # a run of vowel signs on one consonant is a misread: keep the first (a nasal mark may follow)
    line = re.sub(f"({SIGN_CLASS})(?:{SIGN_CLASS})+", r"\1", line)
    # repeated marks: "््", "ंं", "ःः"
    line = re.sub(r"([ऀ-ः़्])\1+", r"\1", line)
    # a vowel sign / halant / nasal mark with no consonant before it (start of word) is orphaned
    line = re.sub(f"(?<![{DEV}])[{VOWEL_SIGN}़्ऀ-ः]+", "", line)
    # a mark straight after a digit or a danda also has nothing to attach to
    line = re.sub(f"(?<=[0-9०-९।॥])[{VOWEL_SIGN}़्]+", "", line)
    # danda read as a bar / capital i / lowercase L after Devanagari
    line = re.sub(rf"(?<=[{DEV}])\s+[|Il]\s*$", " ।", line)
    line = re.sub(rf"(?<=[{DEV}])\s*\|\s*\|", " ॥", line)
    line = re.sub(rf"(?<=[{DEV}])\s*\|(?=\s|$)", " ।", line)
    line = re.sub(r"।{2,}", "।", line)
    return line


def _is_noise_line(line: str) -> bool:
    """A line that is mostly punctuation / isolated marks (table rules, scan edges)."""
    visible = re.sub(r"\s", "", line)
    if not visible:
        return True
    alnum = len(_LINE_ALNUM.findall(visible))
    if alnum == 0:
        return True
    if len(visible) >= 4 and alnum / len(visible) < 0.4:
        return True
    # one or two stray glyphs on a line of their own (not a number or a real letter pair)
    if len(visible) <= 2 and not re.search(r"[0-9०-९]", visible) and not re.search(r"[A-Za-zक-ह]{2}", visible):
        return True
    return False


# --- running headers / footers ----------------------------------------------
def _header_key(line: str) -> str:
    k = fold(line)
    k = re.sub(r"[0-9]+", "", k)
    return re.sub(r"[^a-zऀ-ॿ]", "", k)


def strip_running_headers(pages: list[str], edge: int = 4, share: float = 0.4, min_pages: int = 4) -> list[str]:
    """Remove lines that head or foot many pages (letterheads, 'Page x of y' variants,
    repeated document titles). Compared after dropping digits, so a changing page
    number does not hide the repetition. Only the first/last `edge` lines of a page
    are considered, and only in documents of at least `min_pages` pages."""
    if len(pages) < min_pages:
        return pages
    split = [p.split("\n") for p in pages]
    counts: dict[str, int] = {}
    for lines in split:
        seen = set()
        body = [l for l in lines if l.strip()]
        for l in body[:edge] + body[-edge:]:
            k = _header_key(l)
            if len(k) >= 4 and k not in seen:
                seen.add(k)
                counts[k] = counts.get(k, 0) + 1
    repeated = {k for k, n in counts.items() if n / len(pages) >= share}
    if not repeated:
        return pages
    out = []
    for lines in split:
        idx = [i for i, l in enumerate(lines) if l.strip()]
        edge_idx = set(idx[:edge] + idx[-edge:])
        kept = [l for i, l in enumerate(lines) if not (i in edge_idx and _header_key(l) in repeated)]
        out.append(re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip())
    return out


# --- digits -----------------------------------------------------------------
def _latin_dominant(line: str) -> bool:
    lat = len(re.findall(r"[A-Za-z]", line))
    dev = len(re.findall(f"[{DEV}]", line)) - len(re.findall(r"[०-९]", line))
    return lat > dev


def normalise_digits(text: str) -> str:
    """Same convention as the existing corpus: Nepali running text carries Devanagari
    digits, English text ASCII digits. Decided per line; digits glued to Latin letters
    ('CAMIS2', 'COVID-19', 'A4') are left alone."""
    out = []
    for line in text.split("\n"):
        if _latin_dominant(line):
            out.append(line.translate(_TO_ASCII))
            continue

        def conv(m: re.Match) -> str:
            s, e = m.span()
            before = line[max(0, s - 2):s]
            after = line[e:e + 1]
            if re.search(r"[A-Za-z][-–]?$", before) or re.match(r"[A-Za-z]", after):
                return m.group(0)
            return m.group(0).translate(_TO_DEV)

        out.append(re.sub(r"[0-9]+", conv, line))
    return "\n".join(out)


# --- quality ------------------------------------------------------------------
def token_stats(text: str, ne: set[str], en: set[str]) -> dict:
    """Word-token counts and how many are known words. Nepali tokens are compared after
    `fold` (so नीति/निति, व/ब and halant variants agree); Latin tokens are lowercased."""
    ne_words = DEV_WORD_RE.findall(fold(text))
    en_words = [w.lower() for w in LATIN_WORD_RE.findall(text)]
    ne_ok = sum(w in ne for w in ne_words)
    en_ok = sum(w in en for w in en_words)
    total = len(ne_words) + len(en_words)
    return {
        "ne_words": len(ne_words), "ne_valid": ne_ok, "en_words": len(en_words), "en_valid": en_ok,
        "words": total, "valid": ne_ok + en_ok,
        "rate": (ne_ok + en_ok) / total if total else 0.0,
    }


_VOWEL_SIGN_RE = re.compile(SIGN_CLASS)


def structural_share(text: str) -> float | None:
    """Vocabulary-free check of Devanagari words: share of words whose combining marks
    sit where Devanagari allows them (no mark at word start, no two vowel signs on one
    consonant, no sign after a halant, no doubled marks). None when too little text."""
    words = DEV_WORD_RE.findall(text)
    if len(words) < 10:
        return None

    def ok(w: str) -> bool:
        if re.match(f"[{VOWEL_SIGN}़्ऀ-ः]", w):
            return False
        if re.search(f"{SIGN_CLASS}{SIGN_CLASS}|्{SIGN_CLASS}|््|[ऀ-ः]{{2}}", w):
            return False
        if re.search("्[ऀ-ः]", w):
            return False
        return True

    return sum(ok(w) for w in words) / len(words)


def page_verdict(text: str, ne: set[str], en: set[str], min_words: int = 8, min_rate: float = 0.55,
                 min_structural: float = 0.9) -> tuple[bool, str, dict]:
    """(keep, reason, stats) for one cleaned page."""
    st = token_stats(text, ne, en)
    st["structural"] = structural_share(text)
    if st["words"] < min_words:
        return False, "too_short", st
    if st["rate"] < min_rate:
        return False, f"garbled (valid words {st['rate']:.0%})", st
    if st["structural"] is not None and st["structural"] < min_structural:
        return False, f"broken matras ({st['structural']:.0%} well-formed words)", st
    return True, "ok", st


def document_verdict(pages: list[str], ne: set[str], en: set[str], min_page_share: float = 0.6,
                     min_rate: float = 0.6, **kw) -> dict:
    """Judge every page; a document survives when enough of its words sit on kept pages
    and the kept pages are clean overall. Returns {keep, reason, pages: [kept text or ''],
    dropped_pages: [(page_no, reason)], rate, kept_share}."""
    kept, dropped, words_all, words_kept, valid_kept = [], [], 0, 0, 0
    for i, p in enumerate(pages, 1):
        ok, why, st = page_verdict(p, ne, en, **kw)
        words_all += st["words"]
        if ok:
            kept.append(p)
            words_kept += st["words"]
            valid_kept += st["valid"]
        else:
            kept.append("")
            if st["words"] > 0 or why != "too_short":
                dropped.append((i, why))
    rate = valid_kept / words_kept if words_kept else 0.0
    share = words_kept / words_all if words_all else 0.0
    keep, reason = True, "ok"
    if not words_kept:
        keep, reason = False, "no readable page"
    elif share < min_page_share:
        keep, reason = False, f"only {share:.0%} of the text is on readable pages"
    elif rate < min_rate:
        keep, reason = False, f"valid words {rate:.0%}"
    return {"keep": keep, "reason": reason, "pages": kept, "dropped_pages": dropped,
            "rate": round(rate, 3), "kept_share": round(share, 3)}


# --- Latin noise inside Nepali lines -----------------------------------------------
# stamps, logos and seals come out of Tesseract as short lowercase Latin nonsense ("wear", "geet", "poe")
# in the middle of a Devanagari line; real English inside Nepali text is capitalised or an acronym, or a
# common loan word
_LOWER_LATIN = re.compile(r"(?<![A-Za-z0-9@./:_-])[a-z]{2,6}(?![A-Za-z0-9@./:_-])")
SAFE_LATIN = {"online", "email", "web", "app", "apps", "sms", "pdf", "url", "www", "gov", "np", "org", "com", "login",
              "mobile", "user", "wallet", "data", "file", "link", "bank", "fund", "cash", "card", "swift", "iban"}


def drop_latin_noise(text: str, en: set[str]) -> str:
    """In Devanagari-dominant lines, drop short all-lowercase Latin tokens that are not known English words."""
    out = []
    for line in text.split("\n"):
        if not re.search("[\u0915-\u0939]", line) or _latin_dominant(line):
            out.append(line)
            continue
        kept = _LOWER_LATIN.sub(lambda m: m.group(0) if (m.group(0) in en or m.group(0) in SAFE_LATIN) else "", line)
        out.append(re.sub(r"[ \t]{2,}", " ", kept).strip())
    return "\n".join(out)


_NUMERIC_TOKEN = re.compile(r"^[0-9०-९.,:;/()\-–|%]+$")


def numeric_share(text: str) -> float:
    """Share of whitespace-separated tokens that are only digits/separators - a scanned
    tariff or rate table (HS codes, column after column of figures) rather than prose."""
    toks = text.split()
    return sum(bool(_NUMERIC_TOKEN.match(t)) for t in toks) / len(toks) if toks else 0.0


def is_table_noise(text: str, min_tokens: int = 20, max_numeric: float = 0.55) -> bool:
    """A chunk that is mostly figures: OCR'd code lists carry no searchable meaning and
    only add tokens (and mis-read digits) to the index."""
    return len(text.split()) >= min_tokens and numeric_share(text) > max_numeric


def clean_document(raw_pages: list[str], en: set[str] | None = None) -> list[str]:
    """clean_page on each page, then drop running headers/footers, Latin noise (when the English
    word set is given) and normalise digits."""
    pages = strip_running_headers([clean_page(p) for p in raw_pages])
    if en is not None:
        pages = [drop_latin_noise(p, en) for p in pages]
    return [normalise_digits(p) for p in pages]
