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

import difflib
import re
import unicodedata
from functools import lru_cache

from . import claim_checks, config, situation_guards
from .claim_checks import CheckContext
from .text_norm import DEV_DIGITS, DEVANAGARI_RE, TOKEN_RE, detect_language, fold, tokenize

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


# =========================================================================
# V3: structured (JSON) answers. The model proposes sentences, each with the
# verbatim passage span ("quote") it rests on; this code keeps only the
# sentences whose quote is really in the cited source and actually says what
# the sentence says. A sentence that fails is REMOVED, never marked.
# =========================================================================
KINDS = ("rule", "deadline", "penalty", "procedure", "advice", "empathy")
STRICT_KINDS = {"rule", "deadline", "penalty"}
MIN_QUOTE_TOKENS = 4
FUZZY_MIN_TOKENS = 6
FUZZY_RATIO = 0.9
LEX_MIN_RATIO = 0.3       # share of the sentence's content words found in its quote (calibrated, see docs/PROGRESS.md)
GUIDANCE_MIN_RATIO = 0.4  # uncited procedure text must come from the curated playbook this much
TRAILING_PROVISO = config.TRAILING_PROVISO_CHECK  # V3.2: a quote followed by a "तर, ..." proviso may not be stated with no exception wording

_PUA = re.compile(r"[-]")
_PUNCT = re.compile(r"[।॥|.,;:!?\"'“”‘’()\[\]{}<>«»–—\-‐/\\*_…•·~`^]")
_CITE_ANY = re.compile(r"[\[【]\s*[0-9०-९]{1,2}\s*(?:†[^】\]]*)?[\]】]")
_CLAUSE_REF = re.compile(r"\(\s*[0-9०-९]{1,2}\s*\)")
_SECTION_REF2 = re.compile(
    r"(?:\bSections?|\bRules?|\bArticles?|\bsub-?sections?|दफा|उपदफा|नियम|धारा|अनुच्छेद)\s*\(?\s*([0-9०-९]{1,3}[क-ह]?)", re.I)
_ANY_NUM = re.compile(r"[0-9]+(?:\.[0-9]+)?")
_THOUSANDS = re.compile(r"(?<=[0-9]),(?=[0-9]{3}(?![0-9]))")
_OLDER_LABEL = re.compile(
    r"(older law|earlier law|old law|previous law|previously|formerly|historical|no longer|repealed|superseded|"
    r"पुरानो|पहिलेको|अघिल्लो|खारेज|ऐतिहासिक)", re.I)
_ORDINANCE_LABEL = re.compile(r"(ordinance|अध्यादेश)", re.I)
_BAD_STATUS = {"bill", "repealed", "lapsed"}

_GENERIC_WORDS = (
    "act law legal section rule provision code article court person may must shall provide state states say says "
    "allow allowed require required nepal nepali under also other any such "
    "ऐन दफा उपदफा संहिता नियम कानुन कानून व्यक्ति बमोजिम सम्बन्धी अनुसार नेपाल अन्य कुनै"
)
_GENERIC = frozenset(tokenize(_GENERIC_WORDS))


def _qtokens(text: str) -> list[str]:
    """Quote tokens: NFC, PUA glyphs and punctuation/danda gone, digits ASCII, spelling variants folded."""
    text = _PUA.sub("", unicodedata.normalize("NFC", text or ""))
    return TOKEN_RE.findall(fold(_PUNCT.sub(" ", text)))


def _numbers_in(text: str) -> set[str]:
    body = _words_to_digits(_CITE_ANY.sub(" ", text or "")).translate(DEV_DIGITS)
    body = _THOUSANDS.sub("", body)
    return {_norm_num(n) for n in _ANY_NUM.findall(body)}


def _sentence_numbers(text: str) -> set[str]:
    """Numbers/quantities the sentence asserts. Section references and (1)-style
    clause markers are checked separately."""
    body = _CLAUSE_REF.sub(" ", _SECTION_REF2.sub(" ", _CITE_ANY.sub(" ", text)))
    return _numbers_in(body)


def _section_refs(text: str) -> set[str]:
    return {m.group(1).translate(DEV_DIGITS) for m in _SECTION_REF2.finditer(_CITE_ANY.sub(" ", text))}


def looks_rule_like(text: str) -> bool:
    """A sentence that states or implies law, whatever kind the model gave it."""
    body = _CITE_ANY.sub(" ", text)
    return bool(_RULE_WORDS.search(body) or _LAW_REF.search(body) or _sentence_numbers(body) or _section_refs(body))


class _View:
    """One source prepared for span matching."""
    __slots__ = ("src", "texts", "joined", "numbers", "ocr", "_layout")

    def __init__(self, src: dict):
        self.src = src
        self.texts = [t for t in (_qtokens(src.get("text_ne")), _qtokens(src.get("text_en"))) if t]
        self.joined = [" " + " ".join(t) + " " for t in self.texts]
        head = " ".join(str(src.get(k) or "") for k in ("source_ne", "source_en", "title_ne", "title_en"))
        self.numbers = {n for n in _numbers_in(head) if len(n) == 4}  # the law's own year, e.g. 2074
        # scanned (OCR'd) sources drop and garble words: only they get the lenient quote matching
        self.ocr = str(src.get("ocr") or "").lower() in ("true", "1", "yes")
        self._layout = None

    @property
    def layout(self) -> claim_checks.Layout:
        """Section headings / clause starts of the Nepali text (lazy: only sentences that pass the cheap checks)."""
        if self._layout is None:
            self._layout = claim_checks.Layout(str(self.src.get("text_ne") or ""), str(self.src.get("section") or ""))
        return self._layout


def _fuzzy_span(qtok: list[str], stok: list[str], strict: bool = False) -> bool:
    """>=90% of the quote's tokens found in one contiguous run of the source; every digit token must be exact.
    Lenient (OCR'd passages drop or garble words) unless `strict`: then every quote token must also line up
    with the same word of the passage or a one/two-character variant of it - a substituted or added word
    (नागरिकता for व्यक्तिगत घटना दर्ताको) is not noise."""
    n = len(qtok)
    if n < FUZZY_MIN_TOKENS or len(stok) < n // 2:
        return False
    lead = set(qtok[:3])
    digits = {t for t in qtok if t.isdigit()}
    tried = 0
    for i, t in enumerate(stok):
        if t not in lead:
            continue
        window = stok[max(0, i - 2): i + n + 2]
        if digits - set(window):
            continue
        blocks = difflib.SequenceMatcher(None, qtok, window, autojunk=False).get_matching_blocks()
        if sum(b.size for b in blocks) / n >= FUZZY_RATIO and (not strict or claim_checks.alignment_ok(qtok, window)):
            return True
        tried += 1
        if tried > 200:
            break
    return False


def quote_in_source(quote: str, view: _View) -> str | None:
    """None if the quote is a verbatim span of the source, else a reason code."""
    qtok = _qtokens(quote)
    if len(qtok) < MIN_QUOTE_TOKENS:
        return "quote_too_short"
    needle = " " + " ".join(qtok) + " "
    if any(needle in j for j in view.joined):
        return None
    if any(_fuzzy_span(qtok, t, strict=not view.ocr) for t in view.texts):
        return None
    return "quote_not_verbatim"


@lru_cache(maxsize=1)
def _bridge() -> tuple[dict[str, frozenset[str]], dict[str, frozenset[str]]]:
    """English content word <-> Nepali stems, from the local glossary, so an
    English sentence can be compared with the Nepali statute text it quotes."""
    from . import glossary
    idx, _ = glossary._index()
    en2ne: dict[str, set[str]] = {}
    ne2en: dict[str, set[str]] = {}
    for key, ne_terms in idx.items():
        ne_stems = {t for term in ne_terms for t in tokenize(term)}
        for w in key:
            stem = tokenize(w)
            if not stem or stem[0] in _GENERIC:
                continue
            for s in ne_stems:
                en2ne.setdefault(stem[0], set()).add(s)
                ne2en.setdefault(s, set()).add(stem[0])
    return ({k: frozenset(v) for k, v in en2ne.items()}, {k: frozenset(v) for k, v in ne2en.items()})


def _same(a: str, b: str) -> bool:
    return a == b or (len(a) >= 5 and len(b) >= 5 and a[:5] == b[:5])


def _in_terms(term: str, pool: set[str]) -> bool:
    return term in pool or (len(term) >= 5 and any(_same(term, p) for p in pool))


def lexical_support(sentence: str, quote: str) -> tuple[float, int, int]:
    """(share of the sentence's content words the quote supports, hits, words
    compared). Words in the other script than the quote are compared through
    the glossary; those it cannot translate are not counted either way."""
    terms = {t for t in tokenize(_CITE_ANY.sub(" ", sentence)) if not t.isdigit() and len(t) > 1 and t not in _GENERIC}
    pool = {t for t in tokenize(quote) if not t.isdigit()}
    quote_dev = detect_language(quote) == "ne"
    en2ne, ne2en = _bridge()
    hits = considered = 0
    for t in terms:
        if _in_terms(t, pool):
            hits += 1
            considered += 1
            continue
        t_dev = bool(DEVANAGARI_RE.match(t))
        if t_dev == quote_dev:
            considered += 1
            continue
        cands = (en2ne if quote_dev else ne2en).get(t) or frozenset()
        if cands:
            considered += 1
            if any(_in_terms(c, pool) for c in cands):
                hits += 1
    return (hits / considered if considered else 1.0), hits, considered


def _guidance_ok(text: str, guidance_terms: set[str]) -> bool:
    terms = {t for t in tokenize(text) if not t.isdigit() and len(t) > 1 and t not in _GENERIC}
    if not terms or not guidance_terms:
        return False
    return sum(_in_terms(t, guidance_terms) for t in terms) / len(terms) >= GUIDANCE_MIN_RATIO


def _cite_list(sent: dict) -> list[tuple[int, str]]:
    out = []
    for c in sent.get("cites") or []:
        if not isinstance(c, dict):
            continue
        try:
            n = int(re.sub(r"[^0-9]", "", str(c.get("n")).translate(DEV_DIGITS)) or 0)
        except ValueError:
            n = 0
        out.append((n, str(c.get("quote") or "")))
    return out


def _cite_conflicts(good: list[tuple[int, str]], fn) -> str | None:
    """A sentence rests on one or more quotes; it fails a per-quote check only when EVERY quote fails it (the
    best-supporting quote decides, as for lexical support). `fn(n, quote)` -> reason | None."""
    reasons = [fn(n, q) for n, q in good]
    return reasons[0] if reasons and all(reasons) else None


def check_structured_sentence(sent: dict, sources: list[dict], views: list[_View],
                              guidance_terms: set[str] | None = None,
                              ctx: CheckContext | None = None) -> tuple[str | None, list[dict]]:
    """(None, kept cites) if the sentence may be shown, else (reason code, []). `ctx` (V3.2) carries the user's
    question and the matched playbook's text; without it the checks that need them are skipped."""
    text = str(sent.get("text") or "").strip()
    kind = sent.get("kind") if sent.get("kind") in KINDS else "rule"
    if not text:
        return "empty", []
    body = _CITE_ANY.sub(" ", text)
    cites = _cite_list(sent)
    if not (kind in STRICT_KINDS or cites or looks_rule_like(body)):
        # empathy / advice / plain procedure with no number and no rule wording;
        # a procedure step must come from the curated playbook, not the model's memory
        if kind == "procedure" and not _guidance_ok(body, guidance_terms or set()):
            return "uncited_procedure", []
        # V3.2: whatever the kind, an uncited sentence may not name an office/forum or a filing document that
        # the matched playbook does not name (it would be a legal claim with no source)
        if ctx is not None and claim_checks.uncited_forum_claim(body, ctx.guidance):
            return "uncited_forum_claim", []
        return None, []
    if not cites:
        return "no_citation", []

    valid: list[tuple[int, str]] = []
    first_bad = "bad_citation"
    for n, quote in cites:
        if not 1 <= n <= len(sources):
            first_bad = "bad_citation"
            continue
        why = quote_in_source(quote, views[n - 1])
        if why:
            first_bad = why
            continue
        valid.append((n, quote))
    if not valid:
        return first_bad, []

    older = bool(_OLDER_LABEL.search(body))
    ordinance = bool(_ORDINANCE_LABEL.search(body))
    good = []
    for n, quote in valid:
        s = sources[n - 1]
        status = s.get("status")
        if (status in _BAD_STATUS or s.get("stale")) and not older:
            first_bad = "stale_or_repealed_source"
            continue
        if status == "ordinance" and not ordinance:
            first_bad = "ordinance_unlabelled"
            continue
        if s.get("off_topic") and not s.get("pinned"):  # V3.3: the topical-fit gate ruled this passage out for the question
            first_bad = "off_topic_source"
            continue
        good.append((n, quote))
    if not good:
        return first_bad, []

    if _COURT_CLAIM.search(body) and not any(sources[n - 1].get("category") == "precedent" for n, _ in good):
        return "court_claim_cites_statute", []

    quote_nums: set[str] = set()
    for _, q in good:
        quote_nums |= _numbers_in(q)
    pool = quote_nums | set().union(*(views[n - 1].numbers for n, _ in good))
    if not _sentence_numbers(body) <= pool:
        return "number_not_in_quote", []
    section_pool = set(quote_nums)
    for n, q in good:
        section_pool.add(((sources[n - 1].get("section") or "").translate(DEV_DIGITS).split(" ")[0]) or "-")
        # a merged chunk (rule 22 + rule 23) is filed under its first section: the quote's own heading is the
        # right one (V3.2), and section_under_other_heading below refuses the first section for it
        under = claim_checks.quote_section(_qtokens(q), views[n - 1].layout)
        if under:
            section_pool.add(under)
    if not _section_refs(body) <= section_pool:
        return "section_not_in_quote", []

    # ---- V3.2: what the numbers / sections / parties / conditions of the sentence are BOUND to
    role = claim_checks.number_role_conflict(body, [q for _, q in good])
    if role:
        return role, []
    reason = _cite_conflicts(good, lambda n, q: _section_under_other_heading(body, q, views[n - 1]))
    if reason:
        return reason, []
    if claim_checks.dangling_additive(body):
        return "dangling_additive_penalty", []
    reason = _cite_conflicts(good, lambda n, q: _scope_problem(body, q, views[n - 1]))
    if reason:
        return reason, []
    if _only_precedents(good, sources):
        reason = _precedent_problem(good, sources, ctx)
        if reason:
            return reason, []
    if ctx is not None:
        cited_text = [" ".join(str(sources[n - 1].get(k) or "") for k in ("text_ne", "text_en", "title_ne", "source_ne"))
                      + (" सर्वोच्च अदालत Supreme Court" if sources[n - 1].get("category") == "precedent" else "")
                      for n, _ in good]
        if claim_checks.forum_not_in_sources(body, cited_text, ctx.guidance):
            return "forum_not_in_source", []
        if claim_checks.invented_subject(body, ctx.question, cited_text):  # V3.3: the person's own brand as the actor
            return "invented_subject", []
        reason = _cite_conflicts(good, lambda n, q: _guard_hit(ctx, body, q, sources[n - 1]))
        if reason:
            return reason, []

    # V3.3 (after every older check, so their reasons keep priority): a clause that opens with a cross-reference or sits
    # under a conditional lead-in only applies in that scope
    reason = _cite_conflicts(good, lambda n, q: claim_checks.leading_scope_problem(body, _qtokens(q), views[n - 1].layout))
    if reason:
        return reason, []

    # the best-supporting of the cited quotes decides; words it cannot compare are not held against it
    ratio, hits, considered = max((lexical_support(body, q) for _, q in good), key=lambda r: (r[0], r[1]))
    if considered and (hits < 1 or ratio < LEX_MIN_RATIO):
        return "quote_unrelated", []
    return None, [{"n": n, "quote": q} for n, q in good]


def _section_under_other_heading(body: str, quote: str, view: _View) -> str | None:
    if claim_checks.section_mismatch(body, _qtokens(quote), view.layout):
        return "section_under_other_heading"
    return None


def _scope_problem(body: str, quote: str, view: _View) -> str | None:
    got = claim_checks.clause_context(_qtokens(quote), view.layout)
    if got is not None:
        upto, after = got
        reason = claim_checks.scope_conflict(body, upto)
        if reason:
            return reason
        if TRAILING_PROVISO and claim_checks.proviso_dropped(body, after):
            return "proviso_dropped"
    return None


def _only_precedents(good: list[tuple[int, str]], sources: list[dict]) -> bool:
    return all(sources[n - 1].get("category") == "precedent" for n, _ in good)


def _precedent_problem(good: list[tuple[int, str]], sources: list[dict], ctx: CheckContext | None) -> str | None:
    reasons = [claim_checks.precedent_problem(q, ctx) for _, q in good]
    return reasons[0] if reasons and all(reasons) else None


def _guard_hit(ctx: CheckContext, body: str, quote: str, source: dict) -> str | None:
    gid = situation_guards.violation(ctx.question, body, [quote], source)
    return f"wrong_law_guard:{gid}" if gid else None


def _clean_doc_sentence(s) -> dict | None:
    if not isinstance(s, dict) or not str(s.get("text") or "").strip():
        return None
    return {"text": _CITE_ANY.sub("", str(s["text"])).strip(), "kind": s.get("kind"), "cites": s.get("cites") or []}


def verify_sentence(raw, sources: list[dict], views: list[_View],
                    guidance_terms: set[str] | None = None, ctx: CheckContext | None = None,
                    dangling: bool = False, first_in_block: bool = False) -> tuple[dict | None, str | None]:
    """One sentence through the same checks verify_structured applies: (kept sentence, None) when it may be
    shown, (None, reason) when it is removed, (None, None) when it is empty/malformed (skipped, not counted).
    Shared with the streaming path so streamed and final text are decided by identical code."""
    s = _clean_doc_sentence(raw)
    if s is None:
        return None, None
    reason, cites = check_structured_sentence(s, sources, views, guidance_terms, ctx)
    if reason:
        return None, reason
    if cites and (dangling or first_in_block):
        # V3.3: a sentence that points back ("त्यसै गरी", "यसै संहिताको", "This power", "such leave", "तर ...") whose
        # antecedent was removed - or that opens its block with nothing before it - is dropped, never repaired: a tail
        # must not outlive its head
        if claim_checks.orphan_opener(s["text"]):
            return None, "orphan_connective"
    if dangling:  # the sentence before it (same block) was removed: a plain "And ..." must not dangle
        s["text"], _ = claim_checks.strip_leading_conjunction(s["text"])
    return {"text": s["text"], "kind": s["kind"] if s["kind"] in KINDS else "rule", "cites": cites}, None


def make_views(sources: list[dict]) -> list[_View]:
    return [_View(s) for s in sources]


def guidance_term_set(guidance: str) -> set[str]:
    return {t for t in tokenize(guidance) if not t.isdigit()}


def verify_structured(doc: dict, sources: list[dict], guidance: str = "",
                      ctx: CheckContext | None = None) -> tuple[dict, dict]:
    """(verified doc, report). Failing sentences are dropped; blocks left with
    nothing under their heading are dropped; the report keeps the legacy
    verification shape (supported == claims for what is rendered) plus `removed`
    (counts and reason codes only - never the removed text)."""
    views = [_View(s) for s in sources]
    guidance_terms = {t for t in tokenize(guidance) if not t.isdigit()}
    ctx = ctx if ctx is not None else CheckContext()
    if not ctx.guidance:
        ctx = CheckContext(question=ctx.question, topic_terms=ctx.topic_terms, guidance=guidance)
    reasons: dict[str, int] = {}
    kept_blocks, claims, dropped_blocks = [], 0, 0
    cited: set[int] = set()
    polisher = Polisher(views)
    for block in doc.get("blocks") or []:
        kept = []
        prev_removed = False
        for si, raw in enumerate(block.get("sentences") or []):
            k, reason = verify_sentence(raw, sources, views, guidance_terms, ctx, dangling=prev_removed,
                                        first_in_block=si == 0)
            if k is not None and not reason:
                reason = polisher.admit(k)
            prev_removed = bool(reason)
            if reason:
                reasons[reason] = reasons.get(reason, 0) + 1
                continue
            if k is None:
                continue
            kept.append(k)
            cites = k["cites"]
            if cites:
                claims += 1
                cited |= {c["n"] - 1 for c in cites}
        if kept:
            heading = str(block.get("heading") or "").strip()
            if kept_blocks and heading and kept_blocks[-1]["heading"] == heading:  # same heading twice in a row: one block
                kept_blocks[-1]["sentences"] += kept
            else:
                kept_blocks.append({"heading": heading, "sentences": kept})
        elif block.get("sentences"):
            dropped_blocks += 1
    report = {
        "claims": claims, "supported": claims, "unverified": [],
        "cited_laws": sum(sources[i].get("category") != "precedent" for i in cited),
        "cited_precedents": sum(sources[i].get("category") == "precedent" for i in cited),
        "removed": {"count": sum(reasons.values()), "reasons": sorted(reasons, key=lambda r: -reasons[r]),
                    "by_reason": reasons, "blocks_dropped": dropped_blocks},
    }
    return {**doc, "blocks": kept_blocks}, report


# ------------------------------------------------------------------ V3.3: duplicates and per-subsection cap
DUP_JACCARD = 0.8
SUBSECTION_CAP = 2     # sentences per (passage, sub-section)
SOURCE_CAP = 5         # sentences per passage


class Polisher:
    """Run on sentences that already passed every check, in answer order: drops a (near-)identical sentence
    (a11 repeated one 3x), more than SUBSECTION_CAP sentences from one sub-section of one passage and more than
    SOURCE_CAP from one passage. Shared by verify_structured and the streaming path, so both decide alike."""

    def __init__(self, views: list[_View]):
        self.views = views
        self._seen: list[frozenset] = []
        self._sub: dict[tuple, int] = {}
        self._src: dict[int, int] = {}

    @staticmethod
    def _key(text: str) -> frozenset:
        return frozenset(t for t in tokenize(_CITE_ANY.sub(" ", text)) if not t.isdigit() and t not in _GENERIC)

    def admit(self, k: dict) -> str | None:
        if not k.get("cites"):
            return None
        key = self._key(k["text"])
        if key:
            for old in self._seen:
                if len(key & old) / max(1, len(key | old)) >= DUP_JACCARD:
                    return "duplicate_sentence"
        buckets = []
        for c in k["cites"]:
            n = c["n"]
            sub = claim_checks.quote_subsection(_qtokens(c["quote"]), self.views[n - 1].layout)
            buckets.append((n, sub))
        if any(self._src.get(n, 0) >= SOURCE_CAP for n, _ in buckets) or \
                any(sub and self._sub.get((n, sub), 0) >= SUBSECTION_CAP for n, sub in buckets):
            return "section_cap"
        self._seen.append(key)
        for n, sub in buckets:
            self._src[n] = self._src.get(n, 0) + 1
            if sub:
                self._sub[(n, sub)] = self._sub.get((n, sub), 0) + 1
        return None
