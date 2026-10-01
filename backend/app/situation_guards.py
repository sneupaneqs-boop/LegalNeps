"""V3.2/V2.7: a small DATA table of wrong-law guards - (what the user's question says -> provision families that
must not be cited for it). Wrong-law (a verbatim, on-topic quote from a provision that governs somebody else's
situation) was 7 of the 12 bad sentences of the V3 live review and 10 of the 49 of the V3.3 set-B review, and is what
deterministic quote checks cannot see. Patterns from those reviews that recur and are cheap and safe to encode:

  1. a BANK / NRB loan question answered from the Civil Code's private-lender chapter (s.474-492)          [V3.2]
  2. a wife whose husband merely LEFT (no divorce) answered from the divorced-wife provisions (s.99-102)      [V3.2]
  3. POPULATION: a COLLEGE student answered from the compulsory SCHOOL-education Act (b20); a plain LAND sale from the
     apartment / condominium Act (b06)                                                                      [V2.7]
  4. REGIME: a PRIVATE company asked, a PUBLIC-company rule given (b17: "at least seven shareholders") and vice versa [V2.7]
  5. ACTOR: a guarantor's reimbursement right for a person who is the debtor; a mortgage-redemption rule for a person
     who only repaid a loan on a tamsuk (b08); the drawer's right to take a cheque back for the HOLDER (b10)  [V2.7]

A guard fires only when the question contains every cue and none of the `unless` cues; the check is on the CITED
SOURCE (law title, optionally a section range) or on the cited quote / the answer sentence for a provision keyed on a
party or regime word. This is not legal judgement - it is a list of known mis-fires. Anything else that needs real
judgement stays with the entailment pass. Add a row when a live review finds a new recurring wrong-law pattern; every row
needs a test (tests/test_v32_claim_checks.py for V3.2 rows, tests/test_v27_guards.py for V2.7 rows) built from the review.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .text_norm import DEV_DIGITS


@dataclass(frozen=True)
class Guard:
    id: str
    why: str
    cues: tuple[re.Pattern, ...]           # ALL must match the question
    unless: tuple[re.Pattern, ...]         # NONE may match the question
    law: re.Pattern | None = None          # forbidden source: law title matches...
    sections: tuple[tuple[int, int], ...] = ()   # ...and its section number is in one of these ranges
    whole_law: bool = False                # ...or, with no ranges, the whole law is forbidden for this question
    quote: re.Pattern | None = None        # or: the cited quote matches (a party- / regime-keyed provision)
    sentence: re.Pattern | None = None     # or: the answer sentence itself matches
    v27: bool = False                      # added in V2.7 (switch: config.GUARDS_V27, for ablations)


def _r(p: str) -> re.Pattern:
    return re.compile(p, re.I)


GUARDS: tuple[Guard, ...] = (
    Guard(
        id="bank_loan_vs_private_creditor",
        why="a bank/NRB loan is governed by the regulator's directive, not the Civil Code's private-lender chapter",
        cues=(_r(r"\bbank|\bbfi\b|\bnrb\b|rastra\s*bank|बैंक|बैङ्क|राष्ट्र बैंक|वित्तीय संस्था|finance compan"),
              _r(r"\bloan|\bkarja|\bkarza|\binterest|\bbyaj|penal|hartana|\bemi\b|installment|instalment|"
                 r"ऋण|कर्जा|ब्याज|हर्जना|किस्ता")),
        unless=(_r(r"tamsuk|तमसुक|साहू|\bsahu\b|shahu|moneylender|money lender|\bfriend\b|\bsathi\b|साथी|"
                   r"neighbou?r|relative"),),
        law=_r(r"मुलुकी देवानी संहिता(?!.*कार्यविधि)|Muluki Civil Code(?!.*Procedure)"),
        sections=((474, 492),),
        quote=_r(r"साहूले|साहू"),
    ),
    Guard(
        id="separated_not_divorced",
        why="s.99-102 (maintenance/one-time payment) are for a DIVORCED wife; a husband who merely left is not a divorce",
        cues=(_r(r"chhad(?:era|yo|eko|di)|छोडेर|छाडेर|छोडिदियो|छाडिदियो|छोडी|left (?:me|us|the house|home)|"
                 r"\bdeserted?\b|abandon|walked out|bhagera|\bseparated\b"),),
        unless=(_r(r"divorc|सम्बन्ध\s*विच्छेद|पारपाचुके|bichhed|vichhed|bicched|mukti"),),
        law=_r(r"मुलुकी देवानी संहिता(?!.*कार्यविधि)|Muluki Civil Code(?!.*Procedure)"),
        sections=((99, 102),),
        quote=_r(r"सम्बन्ध\s*विच्छेद\s*भएको"),
    ),
    # ---------------------------------------------------------------- V2.7: population
    Guard(
        id="school_act_for_college_student",
        why="the Compulsory and Free (basic school) Education Act governs children in school; a college / university student's "
            "withheld certificate is not its subject (V3.3 set B b20: a 15-day deadline and a head-teacher fine were invented from it)",
        cues=(_r(r"\bcollege|\bcolleges|कलेज|क्याम्पस|\bcampus|विश्वविद्यालय|\buniversit|\bbachelor|\bmasters?\b|\bplus ?two\b|\+2|"
                 r"\bbbs\b|\bbba\b|\bmbbs\b|\bmbs\b|डिग्री|\bdegree"),),
        unless=(_r(r"\bschool|विद्यालय|\bbasic education|आधारभूत|\bclass ?[1-8]\b|कक्षा\s*[१-८1-8]\b|\bprimary\b|बालबालिका|"
                   r"\bmy (?:son|daughter|child|children)\b|\bchhora|\bchhori|\bbachha"),),
        law=_r(r"अनिवार्य तथा निःशुल्क शिक्षा|Compulsory and Free (?:Basic )?Education"),
        whole_law=True, v27=True,
    ),
    Guard(
        id="apartment_act_for_plain_land_sale",
        why="the Apartment / Condominium Ownership Act governs apartment units and housing buildings; a plain land sale with an "
            "advance (bayana) is not its subject (V3.3 set B b06: s.15 founder-contract duties)",
        cues=(_r(r"जग्गा|\bjagga|\bland\b|\bplot\b|\bropani|कित्ता|लालपुर्जा|\blalpurja|घर ?जग्गा"),),
        unless=(_r(r"apartment|अपार्टमेन्ट|\bflat|फ्ल्याट|condomin|कण्डोमिनियम|संयुक्त आवास|joint housing|आवास इकाई|बहुतले|multi.?stor|"
                   r"housing (?:company|unit|project)|\bbuilder|\bdeveloper|भवन निर्माण"),),
        law=_r(r"संयुक्त आवासको स्वामित्व|Apartment Ownership|Condominium Ownership|Joint Housing"),
        whole_law=True, v27=True,
    ),
    # ---------------------------------------------------------------- V2.7: regime inside one law (Companies Act s.9)
    Guard(
        id="public_company_rule_for_private_company",
        why="the question is about a PRIVATE company; s.9(2) (at least seven shareholders) is the public-company rule - the same "
            "passage carries the private-company rule in s.9(1) (V3.3 set B b17)",
        cues=(_r(r"\bpvt\b|\bprivate (?:limited )?compan|\bprivate limited|\bprivate ltd|प्राइभेट|प्राइवेट|प्रा\.?\s?लि|\bprive\b|\bprayibhet"),),
        unless=(_r(r"\bpublic\b|पब्लिक|सार्वजनिक कम्पनी|\blisted\b|\bipo\b"),),
        sentence=_r(r"पब्लिक\s*कम्पनी|सार्वजनिक\s*कम्पनी|public (?:limited )?compan"),
        quote=_r(r"पब्लिक\s*कम्पनी|सार्वजनिक\s*कम्पनी|public (?:limited )?compan"), v27=True,
    ),
    Guard(
        id="private_company_rule_for_public_company",
        why="the question is about a PUBLIC company; a rule stated for a private company is not its rule",
        cues=(_r(r"\bpublic (?:limited )?compan|\bpublic ltd|पब्लिक कम्पनी|सार्वजनिक कम्पनी|\blisted compan"),),
        unless=(_r(r"\bpvt\b|\bprivate\b|प्राइभेट|प्राइवेट"),),
        sentence=_r(r"प्राइभेट\s*कम्पनी|प्राइवेट\s*कम्पनी|private (?:limited )?compan"),
        quote=_r(r"प्राइभेट\s*कम्पनी|प्राइवेट\s*कम्पनी|private (?:limited )?compan"), v27=True,
    ),
    # ---------------------------------------------------------------- V2.7: actor / regime of a Civil Code rule
    Guard(
        id="guarantor_rule_for_debtor",
        why="s.567 (the guarantor's right to be reimbursed by the debtor) is for the person who GUARANTEED a debt; a borrower who "
            "repaid the lender is not the guarantor (V3.3 set B b08)",
        cues=(_r(r"tamsuk|तमसुक|\bloan|\bkarja|\bkarza|\brin\b|ऋण|कर्जा|\blender|साहू|\bsahu|\bborrow|\bdebt"),),
        unless=(_r(r"guarant|surety|जमानी|जमानत|\bjamani|\bjamanat|\bbail\b"),),
        quote=_r(r"जमानत दिने व्यक्ति|जमानी|जमानतदार|guarantor"),
        sentence=_r(r"जमानत दिने व्यक्ति|जमानी|जमानतदार|guarantor"), v27=True,
    ),
    Guard(
        id="mortgage_rule_without_a_mortgage",
        why="the mortgage-redemption rules (भोग बन्धक / दृष्टिबन्धक, s.444) govern property given as security; a person who only "
            "repaid a loan on a tamsuk and wants the note back has not mortgaged anything (V3.3 set B b08)",
        cues=(_r(r"tamsuk|तमसुक|\bloan|\bkarja|\bkarza|ऋण|कर्जा|\blender|साहू|\bsahu|\bborrow|repaid|तिरे"),),
        unless=(_r(r"mortgag|धितो|बन्धक|\bbandhak|\bdhito|collateral|pledg|गहना|security|लालपुर्जा राख|जग्गा राख|land (?:as|kept)|"
                   r"lalpurja rakh"),),
        quote=_r(r"भोग\s*बन्धक|दृष्टि\s*बन्धक|बन्धकी"),
        sentence=_r(r"भोग\s*बन्धक|दृष्टि\s*बन्धक|बन्धकी|mortgag"), v27=True,
    ),
    Guard(
        id="cheque_drawer_right_for_holder",
        why="Banking Offences Act s.3क(6) lets the account holder (drawer) pay and take the cheque back where the s.3क(3) notice was "
            "given; a person who RECEIVED the cheque is the holder, and the sentence presents the drawer's option as a rule for them "
            "(V3.3 set B b10)",
        cues=(_r(r"cheque|\bchek\b|\bcheck bounce|चेक"),
              _r(r"दिएको चेक|दिएको\s+(?:\w+\s+){0,2}चेक|मलाई .{0,30}चेक|चेक पाएको|received (?:a|the|his|her) (?:cheque|check)|"
                 r"(?:gave|given|gives|handed) me (?:a|the)? ?(?:cheque|check)|cheque (?:given|issued) (?:to me|by)|\bdiyeko (?:cheque|chek)|"
                 r"cheque (?:diyo|diye)|(?:friend|client|customer|buyer|tenant)\w* (?:gave|issued|wrote)")),
        unless=(_r(r"मैले .{0,20}चेक (?:दिएँ|दिएको|जारी)|\bmy cheque|मेरो (?:खाताको )?चेक|\bi (?:issued|wrote|gave|signed) (?:a|the) (?:cheque|check)|"
                   r"\bmaile .{0,15}cheque"),),
        quote=_r(r"खातावालाले[^।]{0,90}चेक फिर्ता लिन|account holder[^.]{0,90}(?:take|get) (?:the )?cheque back"),
        sentence=_r(r"account ?holder[^.]{0,90}(?:take|get|withdraw) (?:the )?cheque back|खातावालाले[^।]{0,90}चेक फिर्ता लिन"), v27=True,
    ),
)


def _section_no(section: str) -> int:
    m = re.match(r"\s*([0-9]+)", (section or "").translate(DEV_DIGITS))
    return int(m.group(1)) if m else -1


def violation(question: str, sentence: str, quotes: list[str], source: dict, v27: bool = True) -> str | None:
    """The id of the guard that forbids citing `source` for this question, else None. `v27=False` skips the rows added in
    V2.7 (ablation)."""
    if not question:
        return None
    for g in GUARDS:
        if g.v27 and not v27:
            continue
        if not all(c.search(question) for c in g.cues) or any(u.search(question) for u in g.unless):
            continue
        title = " ".join(str(source.get(k) or "") for k in ("doc_title_ne", "doc_title_en", "source_ne", "source_en", "title_ne"))
        if g.law and g.law.search(title):
            if g.sections:
                n = _section_no(str(source.get("section") or ""))
                if any(lo <= n <= hi for lo, hi in g.sections):
                    return g.id
            elif g.whole_law:
                return g.id
        if g.quote and any(g.quote.search(q) for q in quotes):
            return g.id
        if g.sentence and g.sentence.search(sentence or ""):
            return g.id
    return None


def source_violation(question: str, source: dict, v27: bool = True) -> str | None:
    """The id of the guard that rules this PASSAGE out for the question (used before generation and for the extractive
    fallback, so the wrong-law passage is never offered as "the provisions that match your question"): its law (whole law
    or section range) is forbidden, or its law title / heading / opening names the regime or party the guard keys on (the
    heading "जमानत दिने व्यक्ति साहूको रूपमा प्रतिस्थापन हुने" for a borrower who repaid his lender)."""
    if not question:
        return None
    head = " ".join(str(source.get(k) or "") for k in ("title_ne", "title_en")) + " " + str(source.get("text_ne") or "")[:160]
    for g in GUARDS:
        if g.v27 and not v27:
            continue
        if not all(c.search(question) for c in g.cues) or any(u.search(question) for u in g.unless):
            continue
        title = " ".join(str(source.get(k) or "") for k in ("doc_title_ne", "doc_title_en", "source_ne", "source_en", "title_ne"))
        if g.law and g.law.search(title):
            if g.sections:
                n = _section_no(str(source.get("section") or ""))
                if any(lo <= n <= hi for lo, hi in g.sections):
                    return g.id
            elif g.whole_law:
                return g.id
        if g.quote and g.quote.search(head) and source.get("category") != "precedent":
            return g.id
    return None
