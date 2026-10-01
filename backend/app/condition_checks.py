"""V2.7: dropped-condition checks that read the FULL enclosing passage sentence.

The V3.2/V3.3 checks look at the clause a quote sits in. A quote is often the tail (or the head) of a longer statutory
sentence whose other half carries the condition:

    "... [सात दिनभित्र] बिक्रेता समक्ष फिर्ता गर्न चाहेमा  [सोही मूल्य बराबरको त्यस्तै अर्को वस्तु वा तिरेको रकम भुक्तानी लिन सक्नेछ]"
    "[उपदफा (३) बमोजिम सूचना दिएकोमा]  खातावालाले जुनसुकै बखत ... चेक फिर्ता लिन सक्नेछ"
    "... अंशियारहरूको मञ्जुरी बमोजिम  [र मञ्जुरी हुन नसकेमा गोला हाली]"

(the V3.3 set-B review: the seven days / the s.3क(3) notice / the lot-draw fallback were dropped by an answer sentence that
quoted only one half). `enclosing` splits the passage at "।" and at clause labels, finds the single sentence holding the
quote and returns the folded tokens BEFORE and AFTER it. Every check below is small and general: the passage sentence
says X (a time limit, a leading condition anchored by a cross-reference, an alternative branch, an authority qualifier on
the actor, a list of grounds named only by letter) and the answer sentence, which states the rest of it, carries nothing
of X. They fail open (return False / None) whenever the quote cannot be located inside one sentence.

Pure functions; verifier.check_structured_sentence wires them in. Every rule was written from the labelled live
sentences (tests/data/v27_reviewB_fixture.json) and is measured on all 196 labelled sentences (tests/test_v27_conditions.py).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import claim_checks as cc
from .claim_checks import _CITE_ANY, _clean, _folded, _qtok, _rx, qty_scan

# a passage sentence ends at "।", and a numbered "(२)" or lettered "(क)" item that starts a line is its own sentence
_SENT_BREAK = re.compile(r"(?<=[।?!])\s+|\n\s*(?=\(\s*(?:[०-९0-9]{1,2}[क-ह]?|[क-ह]{1,2})\s*\)\s)")


@dataclass
class Enclosing:
    pre: list[str]      # folded tokens of the passage sentence before the quote
    quote: list[str]
    post: list[str]     # ... after the quote

    @property
    def pre_text(self) -> str:
        return " ".join(self.pre)

    @property
    def post_text(self) -> str:
        return " ".join(self.post)


def enclosing(text: str, qtok: list[str]) -> Enclosing | None:
    """The passage sentence that contains the quote (folded tokens before / quote / after), or None when the quote is
    not found inside exactly ONE sentence (the same words twice, or a quote that spans sentences: fail open). A quote that
    is not word-for-word (a fused or split word the verifier accepted fuzzily) is located by its first and last words."""
    if len(qtok) < 3 or not text:
        return None
    n = len(qtok)
    pieces = [_qtok(p) for p in _SENT_BREAK.split(_clean(text))]
    found = None
    for toks in pieces:
        if len(toks) < n:
            continue
        for s in range(len(toks) - n + 1):
            if toks[s:s + n] == qtok:
                if found is not None:
                    return None
                found = Enclosing(toks[:s], toks[s:s + n], toks[s + n:])
                break
    if found is not None:
        return found
    # fuzzy: the one piece that holds >= 80% of the quote's words, anchored on the quote's first and last words
    q = set(qtok)
    scored = sorted(((len(q & set(t)) / len(q), i) for i, t in enumerate(pieces) if t), reverse=True)
    if not scored or scored[0][0] < 0.8 or (len(scored) > 1 and scored[0][0] - scored[1][0] < 0.15):
        return None
    toks = pieces[scored[0][1]]
    lead = set(qtok[:3])
    best, first = -1, None
    for k, t in enumerate(toks):
        if t in lead:
            score = len(q & set(toks[k:k + n + 2]))  # the window that holds most of the quote starts where it starts
            if score > best:
                best, first = score, k
    if first is None:
        return None
    last = next((k for k in range(min(len(toks) - 1, first + n + 1), first - 1, -1) if toks[k] in set(qtok[-3:])), None)
    if last is None:
        return None
    return Enclosing(toks[:first], toks[first:last + 1], toks[last + 1:])


# ---------------------------------------------------------------- 1. a time limit attached to the rule
_NE_DURATION = (r"(?:[०-९0-9]+|एक|दुई|तीन|चार|पाँच|छ|सात|आठ|नौ|दश|एघार|बाह्र|पन्ध्र|बीस|पच्चिस|तीस|पैँतीस|पैंतीस|पैतीस|साठी|नब्बे)"
                r"\s*(?:दिन|महिना|वर्ष|घण्टा|हप्ता)")
_TIME_LIMIT_PASSAGE = _rx(_NE_DURATION + r"\s*(?:भित्र|अगावै|अघि|नाघे|पछि|भन्दा)")
_TIME_WORDS_SENT = re.compile(
    r"\b(?:within|before|after|no later than|at least|deadline|time[- ]?limit|period|until|days?|weeks?|months?|years?|hours?)\b", re.I)
_TIME_WORDS_SENT_NE = _rx(r"भित्र|अगावै|अघि|म्याद|अवधि|दिन|हप्ता|महिना|वर्ष|घण्टा|पछि|सम्म")
_TIME_UNITS = {"day", "week", "month", "year", "hour"}


def time_limit_dropped(sentence: str, enc: Enclosing | None) -> bool:
    """The passage sentence bounds the rule by a time ("सात दिनभित्र", "पैँतीस दिन अगावै") and the answer sentence states the
    rule with no time word at all (b25: the 7-day return right was stated without the 7 days)."""
    if enc is None:
        return False
    around = " ".join(enc.pre[-25:] + enc.post[:25])
    if not _TIME_LIMIT_PASSAGE.search(around):
        return False
    body = _CITE_ANY.sub(" ", sentence)
    if {u for _, u in qty_scan(body)[0]} & _TIME_UNITS:
        return False
    return not (_TIME_WORDS_SENT.search(body) or _TIME_WORDS_SENT_NE.search(_folded(body)))


# ---------------------------------------------------------------- 2. a leading condition anchored by a cross-reference
_LEAD_COND_REF = _rx(
    r"(?:उपदफा|खण्ड|दफा|उपनियम)\s*\(?\s*[०-९0-9क-ह]{1,3}\s*\)?[^।]{0,90}?बमोजिम[^।]{0,90}?"
    r"(?:कोमा|गरेमा|भएमा|नभएमा|परेमा|लागेमा|सकेमा)\s*$")
_COND_IN_SENTENCE = re.compile(
    r"\b(?:if|when|where|once|after|upon|in case|in the event|provided|subject to|only if|only after|following|case of|"
    r"situation|ground|reason)\b", re.I)
_COND_IN_SENTENCE_NE = _rx(r"भएमा|गरेमा|दिएमा|कोमा|अवस्थामा|पछि|बमोजिम|उपदफा|खण्ड|यदि|भने|परेमा")


def leading_condition_dropped(sentence: str, enc: Enclosing | None) -> bool:
    """The words before the quote in its own passage sentence are a conditional clause tied to another sub-section / item
    by a cross-reference, and the answer sentence has no conditional wording and names no reference (b10 s.3क(6): the
    account holder may take the cheque back only where the s.3क(3) notice was given; b28 s.400(2): the 35-day notice is for
    the clause (ख) exit only)."""
    if enc is None or len(enc.pre) < 4:
        return False
    if not _LEAD_COND_REF.search(enc.pre_text):
        return False
    body = _CITE_ANY.sub(" ", sentence)
    return not (_COND_IN_SENTENCE.search(body) or _COND_IN_SENTENCE_NE.search(_folded(body)))


# ---------------------------------------------------------------- 3. an alternative branch after the quote
_BRANCH_PIVOT = _rx(r"(?<![ऀ-ॿ])(?:नभएमा|नभए|नसकेमा|नमिलेमा|नमानेमा|नभएकोमा|अन्यथा)(?![ऀ-ॿ])")
_BRANCH_EN = re.compile(
    r"\b(?:if not|otherwise|failing|in default|where there is no|where there is not|by lot|by draw|lot|draw|fall ?back|else|"
    r"if (?:they|the parties|there|consent)|unless)\b", re.I)
_BRANCH_NE = _rx(r"नभएमा|नभए|नसकेमा|अन्यथा|गोला|बाहेक|नगरेमा")
# the sentence states the first branch AS a condition ("सहमति भएकोमा सोही बमोजिम", "if they agree ...", "रहेछ भने"): not unconditional
_BRANCH_COND_EN = re.compile(r"\b(?:if|where|when|in case|provided|once|should)\b", re.I)
_BRANCH_COND_NE = _rx(r"कोमा|भएमा|गरेमा|भने|यदि|हुँदा|गर्दा")


def alternative_branch_dropped(sentence: str, enc: Enclosing | None) -> bool:
    """The passage sentence continues AFTER the quote with an alternative ("... मञ्जुरी बमोजिम र मञ्जुरी हुन नसकेमा गोला हाली") and
    the answer sentence states only the first branch with no hint of the other (b23 s.216(3))."""
    if enc is None or not enc.post:
        return False
    if not _BRANCH_PIVOT.search(enc.post_text):
        return False
    body = _CITE_ANY.sub(" ", sentence)
    return not (_BRANCH_EN.search(body) or _BRANCH_NE.search(_folded(body))
                or _BRANCH_COND_EN.search(body) or _BRANCH_COND_NE.search(_folded(body)))


# ---------------------------------------------------------------- 4. the actor has authority / access under the Act
_AUTHORITY_PRE = _rx(r"(?:यस ऐन|ऐन अन्तर्गत|नियम|यस नियम)[^।]{0,40}(?:प्रदान|बमोजिम|अन्तर्गत)[^।]{0,60}(?:अधिकार|अख्तियार|पहुँच)")
_UNIVERSAL_SUBJECT = re.compile(r"\b(?:any person|anyone|any one|everyone|whoever|any individual|a person who|one who)\b", re.I)
_UNIVERSAL_SUBJECT_NE = _rx(r"कुनै पनि व्यक्ति|कुनै व्यक्ति|कसैले|जोसुकै|सबै व्यक्ति")
_AUTH_IN_SENTENCE = re.compile(
    r"\b(?:authori[sz]ed|authority|empowered|power|powers|right conferred|under (?:the |this )?(?:act|rules?)|"
    r"by (?:the |this )?act|official|regulator|controller)\b", re.I)
_AUTH_IN_SENTENCE_NE = _rx(r"अधिकार|अख्तियार|बमोजिम|प्रदान|नियन्त्रक|पदाधिकारी")


def authority_qualifier_dropped(sentence: str, enc: Enclosing | None) -> bool:
    """The passage's actor is a person with ACCESS granted by this Act or its rules ("यस ऐन ... बमोजिम प्रदान गरिएको अधिकार प्रयोग
    गरी ... पहुँच प्राप्त गरेको कुनै व्यक्ति") and the answer sentence says "any person" with no word of that authority (b26:
    ETA s.48 is for those holding access under the Act, not for a blackmailer)."""
    if enc is None or len(enc.pre) < 3:
        return False
    if not _AUTHORITY_PRE.search(enc.pre_text):
        return False
    body = _CITE_ANY.sub(" ", sentence)
    if not (_UNIVERSAL_SUBJECT.search(body) or _UNIVERSAL_SUBJECT_NE.search(_folded(body))):
        return False
    return not (_AUTH_IN_SENTENCE.search(body) or _AUTH_IN_SENTENCE_NE.search(_folded(body)))


# ---------------------------------------------------------------- 5. grounds named only by letter
_LETTER_LIST = re.compile(r"खण्ड\s*\(\s*[क-ह]{1,2}\s*\)\s*,\s*\(\s*[क-ह]{1,2}\s*\)")  # raw text: folding drops the punctuation
_GROUND_SENT = re.compile(r"\bgrounds?\b", re.I)
_GROUND_SENT_NE = _rx(r"आधारमा|आधार")


def ground_named_from_letters(sentence: str, quote: str) -> bool:
    """The quote refers to its grounds only by LETTER ("दफा ९५ को खण्ड (ख), (ग), (घ), (ङ) वा (च) बमोजिमको आधारमा") and the sentence
    names a concrete ground: a list of letters cannot support which ground it is (b14 s.99(2): "remarriage")."""
    if not _LETTER_LIST.search(_clean(quote)):
        return False
    body = _CITE_ANY.sub(" ", sentence)
    return bool(_GROUND_SENT.search(body) or _GROUND_SENT_NE.search(_folded(body)))


# ---------------------------------------------------------------- the entry point
def condition_problem(sentence: str, quote: str, source_text: str, source_text_en: str = "") -> str | None:
    """Reason code of the first dropped-condition problem between the answer sentence and the passage sentence its quote
    is part of, else None."""
    qtok = _qtok(quote)
    enc = enclosing(source_text, qtok)
    if time_limit_dropped(sentence, enc):
        return "time_limit_dropped"
    if leading_condition_dropped(sentence, enc):
        return "leading_condition_dropped"
    if alternative_branch_dropped(sentence, enc):
        return "alternative_branch_dropped"
    if authority_qualifier_dropped(sentence, enc):
        return "authority_qualifier_dropped"
    if ground_named_from_letters(sentence, quote):
        return "ground_named_from_letters"
    return None
