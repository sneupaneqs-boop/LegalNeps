"""Split contract text into numbered clauses so findings can cite "Clause 7".

Recognised clause starts (only at the beginning of a line):

    1.  1)  1.1  1.1.2  1.1.  (ASCII or Devanagari digits: १.  १.१)
    Clause 3  Article 3  Section 3   (optionally followed by . : - or a title)
    दफा ३  दफा नं. ३  बुँदा ३  बुँदा नं. ३  धारा ३

Sub-items such as (a), (i), (क) stay inside their parent clause. Text before
the first clause is kept as a "preamble" clause. If fewer than two numbered
clauses are found the text is split on blank lines instead (ids P1, P2, ...).

Clause ids are normalised to ASCII digits ("3.2") so they can be quoted back
by the model and matched against; `label` keeps the document's own spelling.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .. import text_norm

_DIGIT = r"[0-9०-९]"
_NUM = rf"{_DIGIT}{{1,3}}(?:\.{_DIGIT}{{1,3}})*"

# "Clause 3", "Article 3.1", "Section 3", "दफा ३", "बुँदा नं. ३", "धारा ३"
_KEYWORD_RE = re.compile(
    rf"^\s*(?P<label>(?:clause|article|section|दफा|बुँदा|बुंदा|धारा)\s*(?:नं\.?|no\.?)?\s*(?P<num>{_NUM}))\s*(?:[.:)\-–—]|\s|$)",
    re.IGNORECASE,
)
# "1." "1)" "1.1" "1.1." "१." "१.१"  - a bare "3 items" is NOT a clause start:
# a plain number needs a trailing . or ), a dotted number (1.1) may be followed by space
_NUMBERED_RE = re.compile(
    rf"^\s*(?P<label>(?P<num>{_NUM}))(?P<sep>[.)]|(?=\s))\s*(?P<rest>\S.*)?$"
)
_PLAIN_INT_RE = re.compile(rf"^{_DIGIT}{{1,3}}$")

PREAMBLE_ID = "0"


@dataclass
class Clause:
    id: str          # normalised: "7", "3.2", "P4", "0" (preamble)
    label: str       # as written in the document: "7.", "Clause 7", "दफा ७"
    text: str        # full clause text incl. its heading line

    def to_dict(self) -> dict:
        return {"id": self.id, "label": self.label, "text": self.text}


def normalize_text(text: str) -> str:
    """NFC, drop zero-width joiners/format chars, unify newlines and spaces.
    Keeps Devanagari digits as written (the clause matcher understands both)."""
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x0c", "\n")
    text = re.sub("[\u200b\u200c\u200d\u00ad\ufeff]", "", text)  # ZWSP ZWNJ ZWJ soft-hyphen BOM
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _ascii(num: str) -> str:
    return num.translate(text_norm.DEV_DIGITS)


def _clause_start(line: str) -> tuple[str, str] | None:
    """(id, label) if `line` starts a clause, else None."""
    m = _KEYWORD_RE.match(line)
    if m:
        return _ascii(m.group("num")), m.group("label").strip()
    m = _NUMBERED_RE.match(line)
    if not m:
        return None
    num, sep, rest = m.group("num"), m.group("sep"), (m.group("rest") or "")
    if _PLAIN_INT_RE.match(num) and not sep.strip():
        return None  # "3 months" / "12 Main Road" - a bare number, not a heading
    return _ascii(num), num + (sep if sep.strip() else "")


def _paragraph_fallback(text: str) -> list[Clause]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paras) < 2:  # no blank lines at all: one paragraph per line
        paras = [p.strip() for p in text.split("\n") if p.strip()]
    return [Clause(id=f"P{i}", label=f"Paragraph {i}", text=p) for i, p in enumerate(paras, 1)]


def segment_clauses(text: str) -> list[Clause]:
    """Split `text` into clauses. Never returns an empty list for non-empty text."""
    text = normalize_text(text)
    if not text:
        return []
    starts: list[tuple[int, str, str]] = []  # (line index, id, label)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        hit = _clause_start(line)
        if hit:
            starts.append((i, hit[0], hit[1]))
    if len(starts) < 2:
        return _paragraph_fallback(text)

    clauses: list[Clause] = []
    if starts[0][0] > 0:
        pre = "\n".join(lines[: starts[0][0]]).strip()
        if pre:
            clauses.append(Clause(id=PREAMBLE_ID, label="Preamble", text=pre))
    seen: dict[str, int] = {}
    for k, (i, cid, label) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        body = "\n".join(lines[i:end]).strip()
        seen[cid] = seen.get(cid, 0) + 1
        uid = cid if seen[cid] == 1 else f"{cid}#{seen[cid]}"  # a schedule may restart numbering
        clauses.append(Clause(id=uid, label=label, text=body))
    return clauses


def clause_by_id(clauses: list[Clause], clause_id: str | None) -> Clause | None:
    if not clause_id:
        return None
    wanted = _normalise_id(clause_id)
    for c in clauses:
        if c.id.lower() == wanted:
            return c
    return None


def _normalise_id(raw: str) -> str:
    """Accept whatever the model echoes back: "Clause 7", "clause 7.", "7.",
    "दफा ७", "cl. 3.2"."""
    s = _ascii(str(raw)).strip().lower()
    s = re.sub(r"^(clause|article|section|cl\.?|दफा|बुँदा|बुंदा|धारा)\s*(no\.?|नं\.?)?\s*", "", s)
    s = s.strip(" .:)-–—")
    return s


def prompt_view(clauses: list[Clause], max_chars: int) -> tuple[str, bool]:
    """The document as `[Clause 7] text` blocks for the extraction prompt,
    capped at `max_chars`. Returns (text, truncated)."""
    parts, used, truncated = [], 0, False
    for c in clauses:
        block = f"[Clause {c.id}]\n{c.text}"
        if used + len(block) > max_chars:
            room = max_chars - used
            if room > 200:
                parts.append(block[:room] + " …")
            truncated = True
            break
        parts.append(block)
        used += len(block) + 2
    return "\n\n".join(parts), truncated
