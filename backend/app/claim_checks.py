"""V3.2: extra deterministic sentence checks built from the 12 labelled bad sentences of the V3 live review
(docs/PROGRESS.md, "V3.2"). Each check is a small, general rule about how a legal sentence can drift from its
quote - not a keyword blacklist tuned to those 12:

  number_role      a number is bound to its unit/head noun ("five lakh" != "पन्ध्र लाख" even if "पाँच" is
                   elsewhere in the quote)
  alignment        fuzzy quote matching forgives character noise, never a substituted word
  heading          a merged chunk (rule 22 + rule 23) is resolved by where the quote sits
  scope            a condition the quote's own clause carries (joint property, divorce, a notice period) or a
                   party the quote does not name (children) must not be dropped/added by the sentence
  additive         "additional penalty" without the base penalty
  forum            an office/tribunal/court or a filing-document requirement needs a quote or the playbook
  precedent        a precedent must state a rule on the user's topic
  gaps             "the sources do not cover X" lines are checked against the passages, in the answer language
  polish           duplicate [n][n], dangling leading conjunctions, OCR typos in shown text

Everything here is pure (no I/O). verifier.py wires the sentence checks in; structured.py the gap/render ones.
What still needs real legal judgement (a verbatim, on-topic quote from a provision that does not govern this
user's situation) is left to the entailment pass - see situation_guards.py for the small deterministic part.
"""
from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache

from .text_norm import DEV_DIGITS, DEVANAGARI_RE, TOKEN_RE, fold, tokenize

# ------------------------------------------------------------------ context


@dataclass
class CheckContext:
    """What the checks may know about the request. All optional: with none of it the checks that need it
    (precedent topic, situation guards, forum-in-guidance) are skipped or strict-by-default."""
    question: str = ""                       # the user's message (+ the model's standalone rewrite)
    topic_terms: frozenset = field(default_factory=frozenset)  # stemmed terms of the question + search phrases
    law_terms: frozenset = field(default_factory=frozenset)    # stemmed section titles of the retrieved statutes
    guidance: str = ""                       # raw text of the matched playbook's forum/steps/evidence


def _v():
    from . import verifier  # lazy: verifier imports this module
    return verifier


_CITE_ANY = re.compile(r"[\[【]\s*[0-9०-९]{1,2}\s*(?:†[^】\]]*)?[\]】]")
_PUA = re.compile(r"[-]")
_PUNCT = re.compile(r"[।॥|.,;:!?\"'“”‘’()\[\]{}<>«»–—\-‐/\\*_…•·~`^]")
_COMMA_DIGITS = re.compile(r"(?<=[0-9]),(?=[0-9])")


def _clean(text: str) -> str:
    return _PUA.sub("", unicodedata.normalize("NFC", text or ""))


def _folded(text: str) -> str:
    """Lower-cased, spelling-folded text with punctuation as single spaces (what the class patterns run on)."""
    return " ".join(fold(_PUNCT.sub(" ", _CITE_ANY.sub(" ", _clean(text)))).split())


def _rx(pattern: str) -> re.Pattern:
    return re.compile(fold(pattern))


# ============================================================ 1. number + role
_MULT = {"हजार": 1e3, "लाख": 1e5, "करोड": 1e7, "अर्ब": 1e9,
         "thousand": 1e3, "lakhs": 1e5, "lakh": 1e5, "lac": 1e5, "crores": 1e7, "crore": 1e7, "billion": 1e9}
_MULT_ALT = "|".join(sorted(_MULT, key=len, reverse=True))
_UNITS = (
    ("pct", re.compile(r"(?:%|per\s?cent|percent|प्रतिशत)", re.I)),
    ("day", re.compile(r"(?:days?(?![a-z])|दिन(?![ुेि]))", re.I)),
    ("month", re.compile(r"(?:months?(?![a-z])|महिना)", re.I)),
    ("year", re.compile(r"(?:years?(?![a-z])|वर्ष)", re.I)),
    ("week", re.compile(r"(?:weeks?(?![a-z])|हप्ता)", re.I)),
    ("hour", re.compile(r"(?:hours?(?![a-z])|घण्टा)", re.I)),
    ("rs", re.compile(r"(?:rupees?(?![a-z])|rs(?![a-z])|npr(?![a-z])|रुपैयाँ|रूपैयाँ|रुपियाँ|रुपैया|रूपैया|रु(?![ऀ-ॿ]))",
                      re.I)),
    ("person", re.compile(r"(?:persons?(?![a-z])|people(?![a-z])|जना)", re.I)),
    ("times", re.compile(r"(?:times(?![a-z])|गुणा)", re.I)),
)
_UNIT_LOOK = "|".join(f"(?:{u.pattern})" for _, u in _UNITS)
_EN_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "twenty-five": 25, "thirty": 30, "thirty-five": 35, "forty": 40,
    "forty-five": 45, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
}
_EN_NUM_RE = re.compile(r"(?<![a-z])(" + "|".join(sorted(_EN_NUM, key=len, reverse=True)) + r")(?=[\s-]*(?:" +
                        _MULT_ALT + "|" + _UNIT_LOOK + r"))", re.I)
_PAIR = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*[-–]?\s*(?:(" + _MULT_ALT + r")(?![a-z])\s*)?", re.I)
_RS_BEFORE = re.compile(r"(?:\brs\.?|\bnpr|रु\.?|रू\.?)\s*$", re.I)


@lru_cache(maxsize=1)
def _ne_num_re() -> re.Pattern:
    words = _v()._NE_WORDS
    return re.compile(r"(?<![ऀ-ॿ])(" + "|".join(sorted(map(re.escape, words), key=len, reverse=True)) +
                      r")\s*(?=(?:" + _MULT_ALT + "|" + _UNIT_LOOK + r"))")


def _fmt(v: float) -> str:
    return str(int(v)) if float(v) == int(v) else str(v)


def _prep_numbers(text: str) -> str:
    t = _CITE_ANY.sub(" ", _clean(text)).translate(DEV_DIGITS)
    t = _COMMA_DIGITS.sub("", t)
    words = _v()._NE_WORDS
    t = _ne_num_re().sub(lambda m: f"{words[m.group(1)]} ", t)
    return _EN_NUM_RE.sub(lambda m: _fmt(_EN_NUM[m.group(1).lower()]), t)


def qty_scan(text: str) -> tuple[set[tuple[str, str]], set[str]]:
    """({(value, unit)}, {numbers with no unit}). Units: pct day month year week hour rs person times. A
    lakh/crore/thousand with no currency word is money ("rs")."""
    t = _prep_numbers(text)
    pairs: set[tuple[str, str]] = set()
    loose: set[str] = set()
    for m in _PAIR.finditer(t):
        val = float(m.group(1))
        mult = m.group(2)
        if mult:
            val *= _MULT[mult.lower()]
        rest = t[m.end(): m.end() + 24]
        unit = next((name for name, rx in _UNITS if rx.match(rest)), None)
        if unit is None and (mult or _RS_BEFORE.search(t[: m.start()])):
            unit = "rs"
        if unit:
            pairs.add((_fmt(val), unit))
        else:
            loose.add(_fmt(val))
    return pairs, loose


def number_role_conflict(sentence: str, quotes: list[str]) -> str | None:
    """A reason code when a number of the sentence is bound to a unit/head noun the quote does not give it:
    the quote has the same unit with other values only ("five lakh" vs "पन्ध्र लाख"), or has that value only
    under a different unit ("3 days" vs "तीन महिना"). None otherwise (including when the quote never uses the
    unit: the plain number check covers that)."""
    sp, _ = qty_scan(sentence)
    if not sp:
        return None
    qp: set[tuple[str, str]] = set()
    qloose: set[str] = set()
    for q in quotes:
        p, l = qty_scan(q)
        qp |= p
        qloose |= l
    for value, unit in sp:
        same = {v for v, u in qp if u == unit}
        if same and value not in same:
            return "number_role_mismatch"
        if not same and value in {v for v, _ in qp} and value not in qloose:
            return "number_unit_mismatch"
    return None


# ============================================================ 2. fuzzy alignment
def _lev(a: str, b: str, cap: int = 3) -> int:
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def near_variant(a: str, b: str) -> bool:
    """Same word up to a character slip (matra/spelling/OCR): edit distance 1, or 2 for a word of 7+ letters.
    Digits never vary. Not a different word: नागरिकता vs व्यक्तिगत, or a dropped negation."""
    if a == b:
        return True
    if a.isdigit() or b.isdigit():
        return False
    d = _lev(a, b)
    return d <= 1 or (min(len(a), len(b)) >= 7 and d <= 2)


def alignment_ok(qtok: list[str], window: list[str]) -> bool:
    """Every token of the quote is in the passage window, or is a near variant of the token it lines up with.
    Passage words the quote skips (footnotes, page furniture) are fine; a word the quote adds or substitutes
    is not."""
    sm = difflib.SequenceMatcher(None, qtok, window, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("equal", "insert"):
            continue
        if tag == "delete":
            return False
        qseg, sseg = qtok[i1:i2], window[j1:j2]
        if len(qseg) == len(sseg):
            if not all(near_variant(q, s) for q, s in zip(qseg, sseg)):
                return False
        elif not (max(len(qseg), len(sseg)) <= 3 and near_variant("".join(qseg), "".join(sseg))):
            return False  # two words fused or one word split at a line break is fine; a different word is not
    return True


# ============================================================ 3+4. passage layout
_HEAD = re.compile(r"^[ \t÷]*([०-९0-9]{1,3}[क-ह]?)[ \t]*\.[ \t]+([^\n:ः]{2,200}?)[ \t]*[:ः]", re.M)
_CLAUSE_START = re.compile(r"^[ \t÷]*(?=\(\s*[०-९0-9]{1,2}[क-ह]?\s*\)|\(\s*[क-ह]{1,2}\s*\)|तर\s*[,:]|तर\s)", re.M)
_TOP_REF = re.compile(
    r"(?:(?<!उप)(?:दफा|नियम|धारा)|(?<!sub-)(?<!sub)\b(?:Section|Rule|Article)|अनुच्छेद)\s*\(?\s*([०-९0-9]{1,3}[क-ह]?)", re.I)


def _sec_key(s: str) -> tuple[int, str]:
    m = re.match(r"(\d+)(.*)", (s or "").translate(DEV_DIGITS).strip())
    return (int(m.group(1)), m.group(2)) if m else (-1, "")


def top_section_refs(sentence: str) -> set[str]:
    """Section/rule numbers a sentence names as ITS provision (not sub-section / clause numbers)."""
    return {m.group(1).translate(DEV_DIGITS) for m in _TOP_REF.finditer(_CITE_ANY.sub(" ", sentence))}


def _qtok(text: str) -> list[str]:
    return TOKEN_RE.findall(fold(_PUNCT.sub(" ", _clean(text))))


class Layout:
    """A passage split (a) at section headings ("२३. विवरण सच्याउने :") and (b) at clause starts ("(२)",
    "(क)", "तर,"), each piece as folded tokens. Built once per source."""
    __slots__ = ("sections", "clauses")

    def __init__(self, text: str, meta_section: str = ""):
        self.sections: list[tuple[str, list[str]]] = []
        self.clauses: list[list[str]] = []
        text = _clean(text)
        heads = self._headings(text, meta_section)
        if len(heads) >= 2:
            for i, (num, at) in enumerate(heads):
                end = heads[i + 1][1] if i + 1 < len(heads) else len(text)
                self.sections.append((num, _qtok(text[at:end])))
        cuts = sorted({0, *(m.start() for m in _CLAUSE_START.finditer(text)), *(h[1] for h in heads)})
        for i, at in enumerate(cuts):
            piece = _qtok(text[at: cuts[i + 1] if i + 1 < len(cuts) else len(text)])
            if piece:
                self.clauses.append(piece)

    @staticmethod
    def _headings(text: str, meta_section: str) -> list[tuple[str, int]]:
        found = [(m.group(1).translate(DEV_DIGITS), m.start(1)) for m in _HEAD.finditer(text)]
        if not found:
            return []
        meta = _sec_key(meta_section.split(" ")[0] if meta_section else "")
        first = _sec_key(found[0][0])
        if found[0][1] > 12 and first != meta:  # the chunk must open with its own section
            return []
        if meta[0] >= 0 and first != meta:
            return []
        out = [found[0]]
        for num, at in found[1:]:
            prev, cur = _sec_key(out[-1][0]), _sec_key(num)
            if (cur[0] > prev[0] and cur[0] - prev[0] <= 8) or (cur[0] == prev[0] and cur[1] > prev[1]):
                out.append((num, at))
        return out


def _locate(needle: list[str], pieces: list[list[str]]) -> int | None:
    n = " " + " ".join(needle) + " "
    hits = [i for i, p in enumerate(pieces) if n in " " + " ".join(p) + " "]
    return hits[0] if len(hits) == 1 else None


def quote_section(qtok: list[str], layout: Layout) -> str | None:
    """The heading number the quote sits under, when the passage holds several sections and the quote is
    clearly in one of them; None when unknown (fail open)."""
    if not layout.sections or len(qtok) < 4:
        return None
    hit = _locate(qtok, [t for _, t in layout.sections])
    if hit is not None:
        return layout.sections[hit][0]
    q = set(qtok)
    scores = [len(q & set(t)) / len(q) for _, t in layout.sections]
    best = max(range(len(scores)), key=scores.__getitem__)
    rest = sorted(scores)[:-1]
    if scores[best] >= 0.8 and scores[best] - (rest[-1] if rest else 0) >= 0.15:
        return layout.sections[best][0]
    return None


def section_mismatch(sentence: str, qtok: list[str], layout: Layout) -> bool:
    """The sentence names a section/rule that is another heading of the same passage than the one the quote
    sits under."""
    if not layout.sections:
        return False
    where = quote_section(qtok, layout)
    if where is None:
        return False
    heads = {n for n, _ in layout.sections}
    return any(ref in heads and ref != where for ref in top_section_refs(sentence))


def clause_context(qtok: list[str], layout: Layout) -> tuple[list[str], list[str]] | None:
    """(tokens of the clause up to the end of the quote, tokens of the clause after it) when the quote is
    inside one clause of the passage, else None."""
    if len(qtok) < 4 or not layout.clauses:
        return None
    needle = " ".join(qtok)
    hits = [(i, p) for i, p in enumerate(layout.clauses) if f" {needle} " in " " + " ".join(p) + " "]
    n = len(qtok)
    if len(hits) == 1:
        i, p = hits[0]
        for s in range(len(p) - n + 1):
            if p[s:s + n] == qtok:
                after = layout.clauses[i + 1] if i + 1 < len(layout.clauses) else []
                return p[: s + n], after
        return None
    if hits:
        return None
    # not verbatim (a fused word, a fuzzy-matched OCR quote): the clause that holds most of the quote's words
    q = set(qtok)
    scores = [len(q & set(p)) / len(q) for p in layout.clauses]
    i = max(range(len(scores)), key=scores.__getitem__)
    if scores[i] < 0.8:
        return None
    p = layout.clauses[i]
    first = next((k for k, t in enumerate(p) if t in set(qtok[:3])), None)
    if first is None:
        return None
    after = layout.clauses[i + 1] if i + 1 < len(layout.clauses) else []
    return p[: min(len(p), first + n + 2)], after


# ---- scope: conditions the clause carries that the sentence must keep
_SCOPE = {
    # class: (trigger in the quote's clause, "carried" in the sentence) - each (Nepali, English)
    "joint_property": ((r"सगोल", r"\bjoint|undivided|jointly|family propert|common propert"),
                       (r"सगोल", r"\bjoint|undivided|jointly|family propert|common propert")),
    "divorce": ((r"सम्बन्ध विच्छेद|सम्बन्धविच्छेद|पारपाचुके", r"divorc"),
                (r"सम्बन्ध विच्छेद|सम्बन्धविच्छेद|पारपाचुके|छुट्टिएको", r"divorc|separated legally")),
    "notice_period": ((r"म्याद (?:समाप्त|व्यतीत|दिइ|दिई|दिएर)",
                       r"period (?:has )?expire|expiry"),
                      (r"म्याद|सूचना|भएपछि|समाप्त|पछि",
                       r"expir|notice|after|once|period|deadline|following|elapse")),
}
_SCOPE_RX = {k: (_rx(t[0]), re.compile(t[1], re.I), _rx(c[0]), re.compile(c[1], re.I)) for k, (t, c) in _SCOPE.items()}
_PARTY = {
    "child": (r"(?<![ऀ-ॿ])(?:बच्चा|बालबालिका|छोरा|छोरी|सन्तान|नाबालक)", r"\b(?:child|children|kids?|son|sons|daughters?|minors?)\b"),
    "parent": (r"(?<![ऀ-ॿ])(?:बाबु|आमा|बुबा|बुवा|अभिभावक)", r"\b(?:parents?|father|mother)\b"),
    "husband": (r"(?<![ऀ-ॿ])(?:पति|श्रीमान)", r"\b(?:husband|spouse)s?\b"),
    "wife": (r"(?<![ऀ-ॿ])(?:पत्नी|श्रीमती|पतिपत्नी)", r"\b(?:wife|wives|spouse)s?\b"),
}
_PARTY_RX = {k: (_rx(a), re.compile(b, re.I)) for k, (a, b) in _PARTY.items()}
_PROVISO_CUE = (_rx(r"(?<![ऀ-ॿ])तर(?![ऀ-ॿ])|बाहेक|अपवाद"), re.compile(r"\b(?:unless|except|but|provided|however|other than|subject to|if she remarries)\b", re.I))


def _has(rx_pair, text_folded: str, text_raw: str) -> bool:
    return bool(rx_pair[0].search(text_folded) or rx_pair[1].search(text_raw))


def scope_conflict(sentence: str, ctx_tokens: list[str], after_tokens: list[str] | None = None) -> str | None:
    """`ctx_tokens`: the quote's clause up to the end of the quote (heading text + the words before the quote
    in its clause + the quote). A scoping condition it carries must be in the sentence; a family party the
    sentence names must be in it (the sentence may not widen who is bound or protected)."""
    clause_folded = " ".join(ctx_tokens)
    s_folded, s_raw = _folded(sentence), _CITE_ANY.sub(" ", sentence)
    for name, (trig_ne, trig_en, carry_ne, carry_en) in _SCOPE_RX.items():
        if trig_ne.search(clause_folded) and not (carry_ne.search(s_folded) or carry_en.search(s_raw)):
            return f"condition_dropped:{name}"
    for name, (ne, en) in _PARTY_RX.items():
        if (ne.search(s_folded) or en.search(s_raw)) and not (ne.search(clause_folded) or _party_generic(name, clause_folded)):
            return f"party_added:{name}"
    return None


def _party_generic(name: str, clause_folded: str) -> bool:
    """A quote that names 'the family/relatives' or the couple covers husband/wife."""
    if name in ("husband", "wife"):
        return bool(re.search(fold(r"पतिपत्नी|दम्पती|दम्पत्ति"), clause_folded))
    return False


def proviso_dropped(sentence: str, after_tokens: list[str]) -> bool:
    """The clause right after the quote is a proviso ("तर, (१) ... गरेमा ... पर्ने छैन") and the sentence
    carries no exception wording at all."""
    if not after_tokens or after_tokens[0] != fold("तर"):
        return False
    return not _has(_PROVISO_CUE, _folded(sentence), _CITE_ANY.sub(" ", sentence))


# ============================================================ 5. additive penalties
_ADD_NE = re.compile(r"(?<![ऀ-ॿ])थप(?![ऀ-ॿ])")
_PEN_NE = re.compile(r"सजाय|कैद|जरिबाना|दण्ड|दंड")
_ADD_EN = re.compile(r"\b(?:additional(?:ly)?|in addition|further (?:imprisonment|fine|penalty|punishment)|extra (?:penalty|fine|imprisonment)"
                     r"|on top of|added to)\b", re.I)
_PENALTY_UNITS = {"year", "month", "day", "rs", "pct"}


def _has_penalty_qty(text: str) -> bool:
    return bool({u for _, u in qty_scan(text)[0]} & _PENALTY_UNITS)


def dangling_additive(sentence: str) -> bool:
    """"Additional/थप" penalty whose base penalty is not stated in the sentence: it reads as the whole
    penalty. The base must appear (as an amount or period) before the additive wording ("in addition to X" is
    read the other way round)."""
    body = _CITE_ANY.sub(" ", _clean(sentence))
    for m in _ADD_NE.finditer(body):
        if _PEN_NE.search(body[max(0, m.start() - 25): m.end() + 40]):
            return not _has_penalty_qty(body[: m.start()])
    m = _ADD_EN.search(body)
    if not m:
        return False
    if re.match(r"in addition", m.group(0), re.I) and re.match(r"\s+to\b", body[m.end():], re.I):
        return not _has_penalty_qty(body[m.end():])
    return not _has_penalty_qty(body[: m.start()])


# ============================================================ 6. forums and document requirements
# (class, Nepali, English). Police and lawyers are deliberately absent: "go to the police / see a lawyer" is
# safe generic advice; a *named* body or forum is a legal claim.
_FORUMS = {
    "court": (r"अदालत|न्यायालय|इजलास", r"\bcourts?\b|\bjudges?\b"),
    "tribunal": (r"न्यायाधिकरण", r"tribunal"),
    "commission": (r"आयोग", r"commission"),
    "committee": (r"समिति", r"committee"),
    "department": (r"विभाग", r"department"),
    "cdo": (r"प्रमुख जिल्ला अधिकारी|जिल्ला प्रशासन", r"\bcdo\b|chief district officer|district administration"),
    "bureau": (r"ब्यूरो", r"bureau|cyber"),
    "office": (r"कार्यालय|रजिस्ट्रार", r"\boffices?\b|registrar"),
    "local": (r"वडा|गाउँपालिका|नगरपालिका|स्थानीय तह|स्थानीय अधिकारी", r"\bward\b|municipal|local level|local authority"),
    "authority": (r"प्राधिकरण|नियमनकारी|राष्ट्र बैंक|सेबोन", r"authority|regulator|rastra bank|\bnrb\b|\bsebon\b"),
}
_FORUM_RX = {k: (_rx(a), re.compile(b, re.I)) for k, (a, b) in _FORUMS.items()}
_POLICE_NE = _rx(r"प्रहरी\s*(?:कार्यालय|चौकी|स्टेशन)")
_POLICE_EN = re.compile(r"police\s*(?:station|office|post)", re.I)
_DOC_NE = _rx(r"प्रमाणपत्र|प्रतिलिपि|नागरिकता|रसिद|कागजात|सम्झौतापत्र|निस्सा|राहदानी|पासपोर्ट|तस्बिर")
_DOC_EN = re.compile(r"\b(?:certificates?|copy|copies|citizenship|receipts?|documents?|passport|photos?|identity card)\b", re.I)
_FILE_NE = _rx(r"संलग्न|पेश गर्न|बुझाउ|दिँदा|दिंदा|आवश्यक|चाहिन्छ|अनिवार्य|साथमा|तयार राख")
_FILE_EN = re.compile(r"\b(?:attach|submit|enclose|required|must (?:provide|bring)|need(?:s|ed)? to|bring|file with|ready)\b", re.I)
_KEEP_NE = _rx(r"सुरक्षित राख|संकलन|सङ्कलन|जम्मा गर्न|स्क्रिनसट|फोटो खिच|रेकर्डिङ")
_KEEP_EN = re.compile(r"\b(?:keep|save|preserve|collect|gather|screenshot|record)\b", re.I)


def forum_classes(text: str) -> set[str]:
    f = _POLICE_NE.sub(" ", _folded(text))
    raw = _POLICE_EN.sub(" ", _CITE_ANY.sub(" ", text))
    return {k for k, (ne, en) in _FORUM_RX.items() if ne.search(f) or en.search(raw)}


def document_requirement(text: str) -> bool:
    """A sentence that says which document a filing needs (as opposed to "keep your receipts")."""
    f, raw = _folded(text), _CITE_ANY.sub(" ", text)
    if not (_DOC_NE.search(f) or _DOC_EN.search(raw)):
        return False
    if not (_FILE_NE.search(f) or _FILE_EN.search(raw)):
        return False
    return not (_KEEP_NE.search(f) or _KEEP_EN.search(raw))


def uncited_forum_claim(text: str, guidance: str) -> bool:
    """An uncited sentence that names an office/forum or a filing document that the matched playbook does not
    name either. `guidance` is the playbook's raw text ("" when there is no playbook)."""
    forums = forum_classes(text)
    doc = document_requirement(text)
    if not forums and not doc:
        return False
    if not guidance:
        return True
    if forums - forum_classes(guidance):
        return True
    return bool(doc and not (_DOC_NE.search(_folded(guidance)) or _DOC_EN.search(guidance)))


def forum_not_in_sources(sentence: str, source_texts: list[str], guidance: str = "") -> str | None:
    """A cited sentence may not name an office/tribunal/court that NONE of the cited passages (nor the
    matched playbook) names: the quote is often one clause and the actor sits in the clause before it, so the
    whole passage is the unit, not the quote."""
    have = set(forum_classes(guidance)) if guidance else set()
    for t in source_texts:
        have |= forum_classes(t)
    missing = forum_classes(sentence) - have
    return sorted(missing)[0] if missing else None


# ============================================================ 7. precedents
_RULE_NE = _rx(r"पर्ने|पर्नेछ|पर्दछ|पर्छ|पर्दैन|हुने|हुँदैन|हुदैन|हुन्छ|नहुने|सक्ने|सक्दैन|नसक्ने|पाउने|नपाउने|पाउनु|ठहर|"
               r"अनिवार्य|बाध्य|विपरीत|मान्य|नमिल्ने|लाग्ने|लाग्दैन|उत्तरदायी|दायित्व|आवश्यक|अधिकार|हक")
_HISTORY_NE = _rx(r"निवेदन दिएको|फिराद|दायर|पेश गरेको|दर्ता भएको|देखिएबाट|देखिन्छ|देखियो|उल्लेख भएको|भनी लेखेको")
_RULE_EN = re.compile(r"\b(?:must|shall|may not|cannot|liable|entitled|required|invalid|illegal|held that|obliged)\b", re.I)
_TOPIC_GENERIC = frozenset(tokenize(
    "हक अधिकार कानुन कानून संविधान व्यक्ति समय शर्त प्रक्रिया गर्न सक्ने गर्ने पर्ने अदालत मुद्दा निर्णय सर्वोच्च "
    "दायित्व कर्तव्य प्रदत्त उपभोग पालना अनिवार्य विषय अवस्था कारण आधार सिद्धान्त व्यवस्था प्रावधान "
    "right law legal court case rule person"))


_TITLE_LAW = re.compile(r"\([^)]*\)\s*$")


def law_topic_terms(sources: list[dict]) -> frozenset:
    """Stemmed section titles of the retrieved STATUTES ("बेइज्जती गर्न नहुने", "साधारण सभा"): what the answer's
    law is about, so a precedent that shares those nouns counts as on topic even when the user's own wording
    (romanised, or a paraphrase) does not."""
    terms: set[str] = set()
    for s in sources:
        if s.get("category") == "precedent":
            continue
        title = _TITLE_LAW.sub("", str(s.get("title_ne") or "")).strip()
        terms |= set(tokenize(title))
    return frozenset(terms)


def states_rule(quote: str) -> bool:
    """The quote is a holding/rule (must, cannot, entitled...), not just a record of what was filed."""
    f, raw = _folded(quote), _CITE_ANY.sub(" ", quote)
    return bool(_RULE_NE.search(f) or _RULE_EN.search(raw))


def topic_overlap(text: str, ctx: CheckContext | None) -> bool | None:
    """Does `text` share a distinctive noun with the user's question? None when the question gives no usable
    terms (then the caller must not decide on it)."""
    if not ctx or not (ctx.topic_terms or ctx.law_terms):
        return None
    v = _v()
    en2ne, _ = v._bridge()
    generic = v._GENERIC | _TOPIC_GENERIC
    terms = {t for t in (set(ctx.topic_terms) | set(ctx.law_terms)) if t and not t.isdigit() and len(t) > 1 and t not in generic}
    usable = {t for t in terms if DEVANAGARI_RE.match(t) or t in en2ne}
    if not usable:
        return None
    pool = {t for t in tokenize(text) if t not in generic and not t.isdigit()}
    for t in usable:
        if v._in_terms(t, pool) or any(v._in_terms(c, pool) for c in en2ne.get(t, ())):
            return True
    return False


def precedent_problem(quote: str, ctx: CheckContext | None) -> str | None:
    if not states_rule(quote) and _HISTORY_NE.search(_folded(quote)):  # a record of what was filed / found
        return "precedent_not_a_rule"
    if topic_overlap(quote, ctx) is False:
        return "precedent_off_topic"
    return None


# ============================================================ 8. gaps
_GAP_BOILER = re.compile(
    r"(?:the )?sources? (?:retrieved )?(?:do|does|did) not (?:cover|mention|state|address|say|specify|include|contain|provide)|"
    r"(?:no|not) (?:source|passage)s?|"
    r"(?:प्राप्त |पाएका |मैले पाएका )?स्रोत(?:हरू|हरूले|हरुले|मा|ले)?|समेटेका छैनन्|समेटेको छैन|उल्लेख छैन|स्पष्ट|खुलाएका छैनन्|"
    r"छैनन्|छैन|मैले", re.I)


def _dev_share(text: str) -> float:
    dev = len(DEVANAGARI_RE.findall(text))
    lat = len(re.findall(r"[A-Za-z]", text))
    return dev / (dev + lat) if dev + lat else 0.5


def gap_in_language(gap: str, lang: str) -> bool:
    share = _dev_share(gap)
    return share >= 0.5 if lang == "ne" else share <= 0.3


def gap_is_false(gap: str, passages: list[str]) -> bool:
    """The gap says the sources do not cover X, but a passage the answer cites (or that was retrieved)
    contains X's distinctive terms. Cheap lexical test (with the glossary bridge for English gaps over Nepali
    passages): most of the gap's content words, and at least three, inside ONE passage."""
    body = _GAP_BOILER.sub(" ", gap)
    v = _v()
    for p in passages:
        ratio, hits, considered = v.lexical_support(body, p)
        if considered >= 3 and hits >= 3 and ratio >= 0.7:
            return True
    return False


def filter_gaps(gaps: list[str], lang: str, cited_passages: list[str], retrieved_passages: list[str]
                ) -> tuple[list[str], list[tuple[str, str]]]:
    """(kept gaps, [(dropped gap, reason)]). Cited passages are tested first, then everything retrieved."""
    kept, dropped = [], []
    seen_passages = cited_passages + [p for p in retrieved_passages if p not in cited_passages]
    for g in gaps:
        if not gap_in_language(g, lang):
            dropped.append((g, "gap_wrong_language"))
        elif gap_is_false(g, seen_passages):
            dropped.append((g, "gap_covered_by_sources"))
        else:
            kept.append(g)
    return kept, dropped


# ============================================================ 9. render polish
_LEAD_CONJ_NE = re.compile(r"^\s*(?:तर|र|तथा|अनि|अनी|साथै|त्यसैले|तसर्थ|अतः)\s*[,।]?\s+")
_LEAD_CONJ_EN = re.compile(r"^\s*(?:but|and|however|also|additionally|moreover|yet|so|therefore|thus|furthermore|"
                           r"in addition)\b[,\s]+", re.I)


def strip_leading_conjunction(text: str) -> tuple[str, bool]:
    """Remove a leading "But/And/तर/र" that joined the sentence to one that was removed. The statement
    itself is unchanged, so this is a repair, not a new claim."""
    for rx in (_LEAD_CONJ_NE, _LEAD_CONJ_EN):
        m = rx.match(text)
        if m and len(text) - m.end() >= 12:
            rest = text[m.end():].lstrip()
            return (rest[:1].upper() + rest[1:] if rx is _LEAD_CONJ_EN else rest), True
    return text, False


_OCR_IR = re.compile(r"[इई]र्|र्[इई]")


def clean_ocr_text(text: str) -> str:
    """OCR glitches the model copied from a scanned source into its own sentence: a reph misplaced around the
    vowel ("भरार्ई", "लाइर्") is the word ending -ई. Applied to shown text only, never to what is matched."""
    return _OCR_IR.sub("ई", text or "")


def dedupe_marks(numbers: list[int]) -> list[int]:
    """[5][5] -> [5]; order kept."""
    seen, out = set(), []
    for n in numbers:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out
