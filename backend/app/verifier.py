"""Deterministic citation verifier for generated answers.

The model writes the answer; plain code decides whether each legal claim is
backed by the passages we actually retrieved. No LLM judges its own output.

A sentence is a *legal claim* if it names a statute/section/precedent or
states a quantified rule (N days/months/years, a percentage, an amount). Each
legal claim must:
  1. cite at least one retrieved passage ([n] with 1 <= n <= len(sources));
  2. for every quantity it states, have that number in a cited passage
     (its text or citation string), Devanagari/ASCII digits normalized;
  3. for every section it names, cite a passage for that section or one
     whose text contains the number;
  4. not rest on a precedent flagged `stale` (decided before the statute
     now governing the topic) for a quantified rule.
Failing claims stay in the answer but are marked, and counted in the report.
"""
from __future__ import annotations

import re

from .text_norm import DEV_DIGITS

_CITE = re.compile(r"\[(\d{1,2})\]")
_SENT = re.compile(r"(?<=[.।!?])\s+(?=\S)|\n+")
_LAW_REF = re.compile(
    r"(ऐन|संहिता|नियमावली|दफा|धारा|नियम\s*[०-९0-9]|ने\.?\s?का\.?\s?प|नजिर|सर्वोच्च अदालत|सुप्रि?ी?म कोर्ट|"
    r"\bAct\b|\bCode\b|\bSection\b|\bRule\s*\d|\bArticle\b|\bRegulations?\b|precedent|Supreme Court)",
    re.I,
)
_UNIT = (r"(days?|months?|years?|weeks?|hours?|%|percent|per cent|rupees?|Rs\.?|NPR|"
         r"दिन|महिना|वर्ष|हप्ता|घण्टा|प्रतिशत|रुपैयाँ|रु\.?)")
_QTY = re.compile(r"([0-9०-९][0-9०-९,]*(?:\.[0-9०-९]+)?)\s*(?:-|–)?\s*" + _UNIT, re.I)
_QTY_PREFIX = re.compile(r"(?:Rs\.?|NPR|रु\.?)\s*([0-9०-९][0-9०-९,]*(?:\.[0-9०-९]+)?)", re.I)
_SECTION_REF = re.compile(r"(?:\bSection|\bRule|दफा|नियम)\s*([0-9०-९]{1,3}[क-ह]?)", re.I)
_NUM_IN_TEXT = re.compile(r"[0-9]+(?:\.[0-9]+)?")
# A bare quantity ("four months without pay") is often the user's own fact;
# it is only a legal claim when stated as a rule.
_RULE_WORDS = re.compile(
    r"(within|must|shall|required|entitled|deadline|limitation|at least|not less than|no later|"
    r"fine|penalt|imprison|compensat|notice period|"
    r"भित्र|पर्छ|पर्नेछ|पर्दछ|सक्नेछ|सकिन्छ|हदम्याद|जरिवाना|कैद|सजाय|क्षतिपूर्ति|कम्तीमा|भन्दा बढी|अनिवार्य)", re.I)
_HEADING = re.compile(r"^\s*(#{1,6}\s|\*\*[^*]+\*\*\s*:?\s*$)")

MARK = {"en": " *(⚠ not verified against the sources)*", "ne": " *(⚠ स्रोतसँग पुष्टि भएन)*"}

# Statutes usually spell periods out ("छ महिनाभित्र", "पैंतीस दिन"). Only a
# number word directly followed by a time unit is converted - "छ" alone is
# also the verb "is".
_NE_BASE = [
    "एक", "दुई", "तीन", "चार", "पाँच", "छ", "सात", "आठ", "नौ", "दस",
    "एघार", "बाह्र", "तेह्र", "चौध", "पन्ध्र", "सोह्र", "सत्र", "अठार", "उन्नाइस", "बीस",
    "एक्काइस", "बाइस", "तेइस", "चौबीस", "पच्चीस", "छब्बीस", "सत्ताइस", "अठ्ठाइस", "उनन्तीस", "तीस",
    "एकतीस", "बत्तीस", "तेत्तीस", "चौंतीस", "पैंतीस", "छत्तीस", "सैंतीस", "अठतीस", "उनन्चालीस", "चालीस",
    "एकचालीस", "बयालीस", "त्रिचालीस", "चवालीस", "पैंतालीस", "छयालीस", "सतचालीस", "अठचालीस", "उनन्चास", "पचास",
    "एकाउन्न", "बाउन्न", "त्रिपन्न", "चउन्न", "पचपन्न", "छपन्न", "सन्ताउन्न", "अन्ठाउन्न", "उनन्साठी", "साठी",
    "एकसट्ठी", "बयसट्ठी", "त्रिसट्ठी", "चौंसट्ठी", "पैंसट्ठी", "छयसट्ठी", "सतसट्ठी", "अठसट्ठी", "उनन्सत्तरी", "सत्तरी",
    "एकहत्तर", "बहत्तर", "त्रिहत्तर", "चौहत्तर", "पचहत्तर", "छयहत्तर", "सतहत्तर", "अठहत्तर", "उनासी", "असी",
    "एकासी", "बयासी", "त्रियासी", "चौरासी", "पचासी", "छयासी", "सतासी", "अठासी", "उनान्नब्बे", "नब्बे",
    "एकानब्बे", "बयानब्बे", "त्रियानब्बे", "चौरानब्बे", "पन्चानब्बे", "छयानब्बे", "सन्तानब्बे", "अन्ठानब्बे", "उनान्सय", "सय",
]
_NE_EXTRA = {"दश": 10, "पांच": 5, "अठाह्र": 18, "उन्नाईस": 19, "अठ्चालीस": 48, "अठ्तीस": 38, "असि": 80, "एक सय": 100}


def _ne_variants(word: str) -> set[str]:
    """Statutes and model output spell the same number several ways: long/short
    i (बीस/बिस), chandrabindu/anusvara (पाँच/पांच), with or without the
    half-t in अठ्/अठ."""
    out = {word}
    for a, b in (("ी", "ि"), ("ँ", "ं"), ("ं", "ँ"), ("अठ्", "अठ"), ("अठ", "अठ्")):
        out |= {w.replace(a, b) for w in out}
    return out


_NE_WORDS: dict[str, int] = {}
for _n, _w in enumerate(_NE_BASE, 1):
    for _v in _ne_variants(_w):
        _NE_WORDS.setdefault(_v, _n)
for _w, _n in _NE_EXTRA.items():
    for _v in _ne_variants(_w):
        _NE_WORDS.setdefault(_v, _n)
_EN_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "thirty-five": 35,
    "forty": 40, "forty-five": 45, "fifty": 50, "sixty": 60, "ninety": 90, "hundred": 100,
}
_NE_WORD_QTY = re.compile(r"(?<![ऀ-ॿ])(" + "|".join(sorted(_NE_WORDS, key=len, reverse=True)) +
                          r")\s*(?=(दिन|महिना|वर्ष|हप्ता|घण्टा|प्रतिशत|गुणा|लाख|हजार|करोड|रुपैयाँ|जना|वटा))")
_EN_WORD_QTY = re.compile(r"\b(" + "|".join(sorted(_EN_WORDS, key=len, reverse=True)) +
                          r")(?=\s*\(?\s*\d*\s*\)?\s*(days?|months?|years?|weeks?|hours?)\b)", re.I)


_MULTIPLIER = {"हजार": 1_000, "लाख": 100_000, "करोड": 10_000_000,
               "thousand": 1_000, "lakh": 100_000, "lakhs": 100_000, "crore": 10_000_000, "crores": 10_000_000}
_MULT_QTY = re.compile(r"([0-9०-९]+(?:[.,][0-9०-९]+)?)\s*(हजार|लाख|करोड|thousand|lakhs?|crores?)\b", re.I)


def _expand_multiplier(m: re.Match) -> str:
    n = float(m.group(1).translate(DEV_DIGITS).replace(",", ""))
    value = n * _MULTIPLIER[m.group(2).lower()]
    return str(int(value)) if value == int(value) else str(value)


def _words_to_digits(text: str) -> str:
    text = _NE_WORD_QTY.sub(lambda m: f"{_NE_WORDS[m.group(1)]} ", text)
    text = _EN_WORD_QTY.sub(lambda m: str(_EN_WORDS[m.group(1).lower()]), text)
    # "पच्चीस लाख" / "25 lakh" and "2,500,000" are the same amount
    return _MULT_QTY.sub(_expand_multiplier, text)


def _norm_num(s: str) -> str:
    s = s.translate(DEV_DIGITS).replace(",", "")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def _haystack_numbers(src: dict) -> set[str]:
    text = " ".join(str(src.get(k) or "") for k in ("text_ne", "text_en", "source_ne", "source_en",
                                                        "title_ne", "title_en", "section"))
    text = _words_to_digits(text)
    return {_norm_num(n) for n in _NUM_IN_TEXT.findall(text.translate(DEV_DIGITS).replace(",", ""))}


def _is_legal_claim(sentence: str) -> bool:
    if len(sentence) < 20 or _HEADING.match(sentence):
        return False
    s = _words_to_digits(sentence)
    if _LAW_REF.search(s):
        return True
    return bool((_QTY.search(s) or _QTY_PREFIX.search(s)) and _RULE_WORDS.search(s))


def _quantities(sentence: str) -> set[str]:
    body = _words_to_digits(_CITE.sub(" ", sentence))
    nums = {_norm_num(m.group(1)) for m in _QTY.finditer(body)}
    nums |= {_norm_num(m.group(1)) for m in _QTY_PREFIX.finditer(body)}
    return {n for n in nums if n}


def _sections(sentence: str) -> set[str]:
    return {m.group(1).translate(DEV_DIGITS) for m in _SECTION_REF.finditer(_CITE.sub(" ", sentence))}


_COURT_CLAIM = re.compile(r"(Supreme Court|सर्वोच्च अदालत|सुप्रिम कोर्ट|सुप्रीम कोर्ट|नजिर|precedent|ने\.?\s?का\.?\s?प)", re.I)


def check_sentence(sentence: str, sources: list[dict], numbers: list[set[str]]) -> str | None:
    """None if the claim is supported, else a short reason code."""
    cites = [int(c) for c in _CITE.findall(sentence)]
    if not cites:
        return "no_citation"
    if any(c < 1 or c > len(sources) for c in cites):
        return "bad_citation"
    cited = [c - 1 for c in cites]
    if _COURT_CLAIM.search(sentence) and not any(sources[i].get("category") == "precedent" for i in cited):
        return "court_claim_cites_statute"
    pool: set[str] = set().union(*(numbers[i] for i in cited))
    for q in _quantities(sentence):
        if q not in pool:
            return "number_not_in_source"
        fresh = set().union(*(numbers[i] for i in cited if not sources[i].get("stale")))
        if q not in fresh:
            return "stale_authority"
    for sec in _sections(sentence):
        if not any((sources[i].get("section") or "").translate(DEV_DIGITS).split(" ")[0] == sec
                   or sec in numbers[i] for i in cited):
            return "section_not_in_source"
    return None


def verify(answer: str, sources: list[dict], lang: str = "en") -> tuple[str, dict]:
    """Returns (answer with unsupported legal claims marked, report)."""
    numbers = [_haystack_numbers(s) for s in sources]
    report = {"claims": 0, "supported": 0, "unverified": [], "cited_laws": 0, "cited_precedents": 0}
    cited_ids: set[int] = set()
    out_lines = []
    for line in answer.split("\n"):
        pieces = _SENT.split(line)
        new_pieces = []
        for piece in pieces:
            if _is_legal_claim(piece):
                report["claims"] += 1
                reason = check_sentence(piece, sources, numbers)
                if reason is None:
                    report["supported"] += 1
                else:
                    report["unverified"].append({"text": piece.strip()[:240], "reason": reason})
                    piece = piece.rstrip() + MARK["ne" if lang == "ne" else "en"]
            for c in _CITE.findall(piece):
                if 1 <= int(c) <= len(sources):
                    cited_ids.add(int(c) - 1)
            new_pieces.append(piece)
        out_lines.append(" ".join(new_pieces))
    for i in cited_ids:
        if sources[i].get("category") == "precedent":
            report["cited_precedents"] += 1
        else:
            report["cited_laws"] += 1
    return "\n".join(out_lines), report
