"""Nepali-script helpers for drafted documents: digits, alphabet labels and
B.S. date wording used at the foot of court forms ("इति सम्वत् ... शुभम् ।")."""
from __future__ import annotations

import datetime

from ..calculators.dates import ad_to_bs

_DIGITS = str.maketrans("0123456789", "०१२३४५६७८९")

# क ख ग घ ङ च छ ज झ ञ ट ठ ड ढ ण त थ द ध न प फ ब भ म  (the (क)(ख)(ग) item letters)
ALPHABET = list("कखगघङचछजझञटठडढणतथदधनपफबभम")

BS_MONTHS = ["बैशाख", "जेठ", "असार", "श्रावण", "भदौ", "असोज",
             "कार्तिक", "मंसिर", "पौष", "माघ", "फाल्गुन", "चैत्र"]
# court forms end "... गते रोज ५ शुभम् ।": the day of the week is a number, आइतबार (Sunday) = १ ... शनिबार = ७

DOTS = "…"


def nd(value) -> str:
    """ASCII digits -> Devanagari digits."""
    return str(value).translate(_DIGITS)


def ka(n: int) -> str:
    """1 -> क, 2 -> ख ... (falls back to क१ style past the alphabet)."""
    n0 = n - 1
    if 0 <= n0 < len(ALPHABET):
        return ALPHABET[n0]
    return ALPHABET[n0 % len(ALPHABET)] + nd(n0 // len(ALPHABET) + 1)


def blank(value, n: int = 10) -> str:
    """The value, or a dotted blank like the ones on the printed forms."""
    if value is None or str(value).strip() == "":
        return DOTS * n
    return str(value)


def _as_date(value) -> datetime.date | None:
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value).strip()[:10])
    except (ValueError, TypeError):
        return None


def bs_parts(value):
    """ISO A.D. date -> (year, month_name, day, weekday_no) in B.S., Nepali
    digits, or None when `value` is empty / not a date."""
    d = _as_date(value)
    if d is None:
        return None
    b = ad_to_bs(d)
    return nd(b.year), BS_MONTHS[b.month - 1], nd(b.day), nd((d.weekday() + 1) % 7 + 1)


def bs_numeric(value, fallback: str = "") -> str:
    """ISO A.D. date -> "२०८३।०६।१३" (B.S., the style used on court forms);
    non-date text is returned unchanged, empty gives `fallback`."""
    if value is None or str(value).strip() == "":
        return fallback
    d = _as_date(value)
    if d is None:
        return str(value)
    b = ad_to_bs(d)
    return nd(f"{b.year}।{b.month:02d}।{b.day:02d}")


def ad_numeric(value, fallback: str = "") -> str:
    """ISO A.D. date -> "१३-०९-२०२६" (गते-महिना-साल, the A.D. style on registration forms)."""
    d = _as_date(value)
    if d is None:
        return str(value) if value not in (None, "") else fallback
    return nd(f"{d.day:02d}-{d.month:02d}-{d.year}")


def opts(value, choices) -> str:
    """The printed check-box row of a form: the chosen option is ticked
    (☒), the others left as empty boxes (☐): '☐ पुरुष  ☒ महिला  ☐ अन्य'."""
    return "   ".join(("☒ " if str(value) == c else "☐ ") + c for c in choices)


def signoff(value, samvat: str = "सम्वत्") -> str:
    """The closing line of a court form. With a date it reads
    'इति सम्वत् २०८३ साल असोज महिना १३ गते रोज २ शुभम् ।', without one the
    blanks are left for hand-filling exactly as on the printed form.
    (`samvat` lets a form keep its own spelling, e.g. "संवत्".)"""
    p = bs_parts(value)
    y, m, d, wd = p if p else (DOTS * 6, DOTS * 6, DOTS * 4, DOTS * 3)
    return f"इति {samvat} {y} साल {m} महिना {d} गते रोज {wd} शुभम् ।"
