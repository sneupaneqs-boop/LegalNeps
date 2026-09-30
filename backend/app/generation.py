"""Question understanding -> retrieval -> grounded answer.

1. analyze_query: a fast LLM call turns a lay question (English, Nepali or
   romanised Nepali) into formal Nepali legal search phrases plus likely
   statute titles - statutes are only in Nepali, so this is what lets an
   English question find "मुलुकी देवानी संहिता, २०७४ दफा ..." at all.
2. retrieval: BM25 over every phrasing, fused, laws and precedents fetched
   separately so a precedent can back up the statute.
3. generate: the stronger model answers ONLY from the numbered passages and
   cites them [1], [2] ... ; the API returns the same numbered sources with
   links to the official PDF page / nkp.gov.np decision.
Without any LLM key the app still works: raw query search + extractive answer.
"""
from __future__ import annotations

import hashlib
import logging
import re
import time
from pathlib import Path
from collections import OrderedDict
from threading import Lock

from . import claim_checks, config, glossary, llm, playbooks, prompt_guard, structured, supa, tiers, translit
from .playbook_matcher import match_scored as match_playbook_scored
from .playbook_matcher import strong_match as strong_playbook_match
from .retrieval import get_index
from .text_norm import detect_language, fold, guess_language, tokenize

log = logging.getLogger(__name__)

# S13: bump when ANSWER_SYSTEM's wording changes materially, so llm_usage
# rows say which prompt version produced an answer.
ANSWER_PROMPT_VERSION = "answer_v2_structured"

DISCLAIMER_EN = (
    "This is general legal information, not a substitute for advice from a "
    "licensed Nepali advocate. For anything urgent or high-stakes, please consult a lawyer."
)
DISCLAIMER_NE = (
    "यो सामान्य कानुनी जानकारी मात्र हो, इजाजतपत्रप्राप्त अधिवक्ताको सल्लाहको विकल्प होइन। "
    "जरुरी वा महत्वपूर्ण विषयमा कृपया वकिलसँग सम्पर्क गर्नुहोस्।"
)

ANALYZE_SYSTEM = """You turn a person's question into search queries for a corpus of ONLY official \
Nepali-language statutes (Constitution, Acts/ऐन, Codes/संहिता, Rules/नियमावली, Orders) and Supreme \
Court precedents, all in formal legal Nepali. The person may write English, Devanagari, or ROMANISED \
Nepali ("mero ghar bhada", "talab dinna"): read romanised Nepali as Nepali, then search in Devanagari.

Classify first; plan the search only for legal questions. Return JSON with exactly these keys:
- "intent": "legal" (any law/rights/legal problem/procedure, even vague or emotional), "greeting", \
"thanks", "smalltalk", "off_topic" (clearly not law), "unclear" (legal-ish but too vague to search).
- "reply": for non-legal intents, a short warm reply in the reply language (ONE clarifying question \
for unclear); "" for legal.
- "question": for legal, the message as one complete self-contained question, resolving follow-ups \
from the earlier conversation; else "".
- "reply_language": "ne" if the person wrote Nepali (Devanagari or romanised), else "en".
- "concern": one sentence on the real underlying legal concern, in the reply language.
- "area": short English legal area (e.g. "labour - overtime").
- "queries_ne": 4-6 short Devanagari phrases (2-6 words) in the STATUTORY vocabulary the law text \
itself uses, not everyday speech: wage/salary -> पारिश्रमिक; working hours -> कार्य घण्टा, अतिरिक्त \
समय; deposit/bail -> धरौटी, जमानत; property partition -> अंशबण्डा, अंशियार; heirs -> हकवाला; \
FIR -> जाहेरी दरखास्त; insider trading -> भित्री कारोबार; divorce -> सम्बन्ध विच्छेद; landlord/tenant \
-> घरधनी, बहालवाला, घर बहाल; limitation -> हदम्याद; rape -> जबरजस्ती करणी; cheating -> ठगी. Name \
the specific provision topic, not just the area. Never copy romanised words into queries_ne.
- "queries_en": 1-2 short English phrases.
- "laws": up to 3 governing Acts by their EXACT published title with year, e.g. "श्रम ऐन, २०७४", \
"मुलुकी देवानी संहिता, २०७४", "मुलुकी अपराध संहिता, २०७४", "मुलुकी फौजदारी कार्यविधि संहिता, २०७४", \
"वैदेशिक रोजगार ऐन, २०६४", "घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६", "धितोपत्र सम्बन्धी ऐन, २०६३", \
"कम्पनी ऐन, २०६३", "सूचनाको हक सम्बन्धी ऐन, २०६४", "उपभोक्ता संरक्षण ऐन, २०७५", "विद्युतीय \
(इलेक्ट्रोनिक) कारोबार ऐन, २०६३", "बैङ्किङ्ग कसूर तथा सजाय ऐन, २०६४", "मालपोत ऐन, २०३४". Omit \
if unsure; never invent a title.
- "wants_precedent": true if court interpretation would help, else false.

Examples (message -> area; queries_ne; laws):
1. "boss le din ko 12 ghanta kaam garauchha, overtime ko paisa pani dinna" -> labour hours; \
["कार्य घण्टा", "अतिरिक्त समयको पारिश्रमिक", "साप्ताहिक कार्य घण्टा"]; ["श्रम ऐन, २०७४"]
2. "manpower le thagyo, visa aayena, 3 lakh liyo" -> foreign-employment fraud; ["वैदेशिक रोजगारको \
नाममा ठगी", "रकम फिर्ता क्षतिपूर्ति", "म्यानपावर इजाजतपत्र"]; ["वैदेशिक रोजगार ऐन, २०६४"]
3. "sasu-sasura le sampatti ma haq chhaina bhanchhan, shreeman gujrey" -> widow's property; \
["विधवाको अंश", "अपुताली हकवाला", "अंशबण्डा"]; ["मुलुकी देवानी संहिता, २०७४"]
4. "police le jaheri lina maandaina" -> FIR refused; ["जाहेरी दरखास्त दर्ता", "प्रहरीले जाहेरी \
नलिएमा", "सरकारी वकिलको कार्यालयमा उजुरी"]; ["मुलुकी फौजदारी कार्यविधि संहिता, २०७४"]
5. "company le byaj sahit dharauti jafat garyo" -> deposit forfeiture; ["धरौटी जफत", "ब्याज सहित \
रकम फिर्ता", "सम्झौता उल्लङ्घन क्षतिपूर्ति"]; ["मुलुकी देवानी संहिता, २०७४"]
6. "kampani ko bhitri suchana bata share kinbech garda ke sajaya?" -> insider trading; \
["भित्री कारोबार", "धितोपत्र कारोबार सजाय"]; ["धितोपत्र सम्बन्धी ऐन, २०६३"]
7. "cheque bounce bhayo, sathi le paisa dinna" -> dishonoured cheque; ["चेक अनादर", "चेकको रकम \
भुक्तानी", "बैङ्किङ्ग कसूर सजाय"]; ["बैङ्किङ्ग कसूर तथा सजाय ऐन, २०६४"]"""

# V3: the answer is one JSON object of quoted, checkable sentences (see structured.py);
# the old free-prose prompt measured 40% unsupported legal claims (V1 review).
# V3.2 token diet: only the worked example in the reply language is sent (rules are shared).
_ANSWER_SYSTEMS = {lang: structured.system_prompt(lang) + "\n\n" + prompt_guard.UNTRUSTED_TEXT_NOTICE
                   for lang in ("en", "ne")}
ANSWER_SYSTEM = _ANSWER_SYSTEMS["en"]  # kept name: the English variant (both are hashed into the fingerprint)
ANALYZE_SYSTEM += "\n\n" + prompt_guard.UNTRUSTED_TEXT_NOTICE


def answer_system(lang: str) -> str:
    return _ANSWER_SYSTEMS["ne" if lang == "ne" else "en"]


class _LRU:
    def __init__(self, size: int):
        self.size, self.data, self.lock = size, OrderedDict(), Lock()

    def get(self, key):
        with self.lock:
            if key in self.data:
                self.data.move_to_end(key)
                return self.data[key]
        return None

    def put(self, key, value):
        with self.lock:
            self.data[key] = value
            self.data.move_to_end(key)
            while len(self.data) > self.size:
                self.data.popitem(last=False)


_analysis_cache = _LRU(2048)
_answer_cache = _LRU(config.ANSWER_CACHE_SIZE)


_WS = re.compile(r"\s+")


def _cache_key(message: str, lang: str) -> str:
    return lang + "|" + _WS.sub(" ", fold(message)).strip()


def _answer_cache_key(message: str, lang: str) -> str:
    # corpus_version prefix: an answer cached before the corpus changed must
    # never be served after (docs/PROGRESS.md known issue #5). Only the
    # answer cache needs this - analyze_query()'s output doesn't depend on
    # corpus content, and coupling its cache key to get_index() would force
    # the (slow, one-time) index build for every call site, including ones
    # that never touch retrieval.
    return PIPELINE_VERSION + "|" + get_index().digest + "|" + _cache_key(message, lang)


# Bump whenever answer construction changes (retrieval filters, pinned
# playbook provisions, verifier), so answers cached by an older pipeline -
# including the persistent Supabase answer_cache - are never served again.
# The fingerprint below also retires them automatically when the prompts,
# the romanised lexicon or any playbook file changes.
PIPELINE_VERSION = "p10"  # p9: structured JSON answers + quote verifier (V3); p10: V3.2 claim checks, gap filter, token diet


def _pipeline_fingerprint() -> str:
    h = hashlib.sha256()
    h.update(ANALYZE_SYSTEM.encode())
    h.update(_ANSWER_SYSTEMS["en"].encode())
    h.update(_ANSWER_SYSTEMS["ne"].encode())
    here = Path(__file__).parent
    for f in [here / "translit.py", here / "verifier.py", here / "structured.py", here / "text_norm.py",
              here / "claim_checks.py", here / "situation_guards.py",
              *sorted((here / "data" / "playbooks").glob("*.yaml"))]:
        if f.exists():
            h.update(f.name.encode())
            h.update(f.read_bytes())
    return h.hexdigest()[:8]


PIPELINE_VERSION = f"{PIPELINE_VERSION}-{_pipeline_fingerprint()}"


GREETING_RE = re.compile(
    r"^\s*(hi+|hello|hey|namaste|namaskar|good (morning|afternoon|evening)|नमस्ते|नमस्कार|हेलो|हाई)\W*$", re.I)
THANKS_RE = re.compile(r"^\s*(thanks?( you)?|thank u|ok(ay)?|dhanyabad|dhanyawad|धन्यवाद|ठिक छ|हुन्छ)\W*$", re.I)
# chit-chat about the assistant itself, not a legal question - short enough
# that false-positiving on a real legal message is very unlikely
SMALLTALK_RE = re.compile(
    r"^\s*(who are you|what('?s| is) your name|what can you do|how (are|do) you (work|help)|"
    r"are you (a )?(robot|bot|ai|human)|तिमी को हौ|तिमीलाई कस्तो छ|तिमी के गर्न सक्छौ|"
    r"तिमी को हौस्|तिम्रो नाम के हो)\W*$", re.I)
# a handful of unambiguous non-legal topics; deliberately narrow (a false
# positive here sends a real legal question a canned "I can't help" reply,
# which is worse than the false negative of just asking the LLM instead)
OFF_TOPIC_HINT_RE = re.compile(
    r"^\s*(what'?s? the weather( \w+)*|tell me a joke|sing (a|me a) song|recommend a movie|"
    r"मौसम कस्तो छ|एउटा जोक सुनाऊ|गीत गाऊ)\W*[?.!]*\s*$", re.I)

CANNED = {
    ("greeting", "en"): "Hello! I'm Kanooni Sathi. Tell me about your legal question or situation — "
                        "a landlord issue, family matter, work problem, a police case, anything — and I'll "
                        "explain what Nepali law says, with the exact sections.",
    ("greeting", "ne"): "नमस्ते! म कानूनी साथी हुँ। तपाईंको कानुनी प्रश्न वा समस्या बताउनुहोस् — घरबहाल, पारिवारिक, "
                        "कामकाज, प्रहरी मुद्दा, जुनसुकै — म नेपाली कानूनले के भन्छ, दफासहित बुझाउँछु।",
    ("thanks", "en"): "You're welcome! Ask me anything else about Nepali law whenever you need.",
    ("thanks", "ne"): "स्वागत छ! नेपाली कानूनबारे अरू केही जान्न परे जुनसुकै बेला सोध्नुहोस्।",
    ("off_topic", "en"): "I can only help with questions about Nepali law — your rights, procedures, "
                         "penalties, family, property, work and so on. What legal question can I help with?",
    ("off_topic", "ne"): "म नेपाली कानूनसम्बन्धी प्रश्नमा मात्र सहयोग गर्न सक्छु — हक-अधिकार, प्रक्रिया, सजाय, "
                         "परिवार, सम्पत्ति, रोजगारी आदि। तपाईंको कानुनी प्रश्न के हो?",
    ("unclear", "en"): "I'd like to help. Could you tell me a little more — what happened, who is involved, "
                       "and what you want to achieve?",
    ("unclear", "ne"): "म सहयोग गर्न चाहन्छु। अलि विस्तारमा बताउनुहोस् — के भयो, को-को संलग्न छन्, र तपाईं के चाहनुहुन्छ?",
}


def _history_text(history: list[dict] | None, limit: int = 4) -> str:
    if not history:
        return ""
    turns = history[-limit:]
    return "\n".join(f"{'Person' if t.get('role') == 'user' else 'Assistant'}: {(t.get('text') or '')[:500]}"
                     for t in turns)


def quick_intent(message: str) -> str | None:
    """Obvious non-legal messages, recognised without any LLM."""
    if GREETING_RE.match(message):
        return "greeting"
    if THANKS_RE.match(message):
        return "thanks"
    if SMALLTALK_RE.match(message):
        return "smalltalk"
    if OFF_TOPIC_HINT_RE.match(message):
        return "off_topic"
    return None


def _is_devanagari(message: str) -> bool:
    """Script check on the message itself. NOT the language hint: the hint is
    "ne" for romanised Nepali too (guess_language), and romanised Nepali is
    exactly what the statute index cannot read."""
    return detect_language(message) == "ne"


def _expansion_precise(message: str) -> bool:
    """The glossary's word-for-word expansion is trustworthy: it found
    something, and every hit is a multi-word phrase or a long distinctive word
    (short single words like "pani", "kaam", "paisa" are ambiguous)."""
    hits = glossary.expand_hits(message)
    return bool(hits) and len(hits) <= 6 and all(len(k) > 1 or len(k[0]) >= 6 for k, _ in hits)


def confidence(message: str, lang: str) -> float:
    """How sure we are this message can be searched well WITHOUT an LLM
    rewriting it. Devanagari questions already use the statutes' own script, so
    the raw text plus glossary/lexicon expansion is enough (the LLM would only
    polish phrasing). Anything typed in Latin script (English or romanised
    Nepali) needs the rewrite unless a curated playbook matches on an exact
    phrase AND the glossary expansion is high-precision - a loose glossary hit
    count is not evidence of understanding ("paisa pani" -> land units + water).
    quick_intent() has already filtered greetings/thanks/smalltalk.
    `lang` is kept for API compatibility; the decision is made on the script.
    """
    if _is_devanagari(message):
        return 0.9
    if strong_playbook_match(message) and _expansion_precise(message):
        return 0.9
    return 0.3 if (glossary.expand(message) or translit.expand(message)) else 0.0


CONFIDENCE_THRESHOLD = 0.6


def _skip_llm(message: str, lang_hint: str, history: list[dict] | None) -> bool:
    """The one rule for "answer this question without the query-rewrite call"
    - shared by analyze_needs_llm() and analyze_query() so they cannot drift.
    Follow-ups always need the LLM (history resolves "what about daughters?")."""
    return not history and confidence(message, lang_hint) >= CONFIDENCE_THRESHOLD


def analyze_needs_llm(message: str, lang_hint: str, history: list[dict] | None = None) -> bool:
    """Whether analyze_query() will reach a provider for this message."""
    if quick_intent(message) is not None or not llm.available():
        return False
    return not _skip_llm(message, lang_hint, history)


def analyze_query(message: str, lang_hint: str, history: list[dict] | None = None) -> dict:
    hist = _history_text(history)
    key = _cache_key(message + "\x00" + hist, lang_hint)
    cached = _analysis_cache.get(key)
    if cached is not None:
        return cached
    base = {"intent": quick_intent(message) or "legal", "reply": "", "question": "",
            "reply_language": lang_hint, "concern": "", "area": "", "queries_ne": [],
            "queries_en": [], "laws": [], "wants_precedent": True, "llm": False}
    if base["intent"] != "legal" or not llm.available():
        return base
    if _skip_llm(message, lang_hint, history):
        # skip the LLM call: build_queries() already searches the raw
        # Devanagari message plus glossary/lexicon expansion, so a confident
        # message searches just as well without an LLM-rewritten query set.
        out = {**base, "question": message}
        _analysis_cache.put(key, out)
        return out
    try:
        prompt = (f"Earlier conversation:\n{hist}\n\n" if hist else "") + \
            f"Latest message: {prompt_guard.wrap_user_text(message)}"
        raw = llm.complete(ANALYZE_SYSTEM, prompt, fast=True, json_mode=True,
                           max_tokens=700, temperature=0.1)
        data = llm.parse_json(raw)
        out = {**base, **{k: data.get(k, base[k]) for k in base if k != "llm"}, "llm": True}
        for k in ("queries_ne", "queries_en", "laws"):
            out[k] = [str(x) for x in (out[k] or []) if str(x).strip()][:6]
        if out["intent"] not in ("legal", "greeting", "thanks", "smalltalk", "off_topic", "unclear"):
            out["intent"] = "legal"
        if out["reply_language"] not in ("en", "ne"):
            out["reply_language"] = lang_hint
        if lang_hint in ("en", "ne") and lang_hint != detect_language(message):
            out["reply_language"] = lang_hint  # explicit UI choice wins
        _analysis_cache.put(key, out)
        return out
    except Exception as e:  # noqa: BLE001
        log.warning("query analysis failed: %s", str(e)[:200])
        return base


def build_queries(message: str, analysis: dict) -> list[tuple[str, float]]:
    """Weighted query set. Sources, best first: the LLM's Nepali legal
    phrasings; the curated romanised-Nepali lexicon (translit.py: precise,
    corpus-validated Devanagari terms); the word-for-word glossary (broader
    but noisier); the raw message (Devanagari messages search directly, Latin
    ones mostly match English-heavy noise like forms and dictionaries, so they
    count less once anything better exists). With an LLM rewrite the local
    expansions are supporting evidence; without one they are the query."""
    is_ne = detect_language(message) == "ne"
    llm_q = analysis.get("queries_ne") or []
    expansion = glossary.expand(message)
    lex = translit.match(message)
    lex_terms = translit.expand(message)
    queries: list[tuple[str, float]] = [
        (message, 1.0 if is_ne else (0.35 if (expansion or llm_q or lex_terms) else 1.0))]
    fixed = respell_devanagari(message) if is_ne else message
    if fixed != message:
        queries.append((fixed, 1.0))
    queries += [(q, 1.0) for q in llm_q]
    queries += [(q, 0.4) for q in analysis.get("queries_en", [])]
    if lex_terms:
        queries.append((" ".join(lex_terms), 0.6 if llm_q else 1.0))
        # one query per concept so a multi-topic message searches each topic,
        # not only the passages that mention all of them
        queries += [(" ".join(e.terms), 0.3 if llm_q else 0.5) for e in lex if e.strong]
    if expansion:
        queries.append((" ".join(expansion), 0.7 if llm_q else (0.5 if lex_terms else 1.0)))
        queries += [(t, 0.25) for t in expansion[:6]]
    return queries


# Tax/fiscal/insolvency statutes mention deposits, wages, payments and
# notices in passing, so on keyword overlap alone they outrank the law that
# actually governs a tenancy or employment question. Demote them unless the
# question itself is about tax/fiscal matters.
_FISCAL_DOC = re.compile(r"(आयकर|आर्थिक ऐन|आर्थिक कार्यविधि|मूल्य अभिवृद्धि कर|भन्सार|अन्तःशुल्क|राजस्व|"
                         r"विनियोजन|दामासाही|बजेट|कर सम्बन्धी)")
_FISCAL_QUERY = re.compile(
    r"(\btax|\bvat\b|\btds\b|income tax|customs|excise|revenue|budget|insolven|bankrupt|"
    r"आयकर|भ्याट|कर\b|करको|कर तिर|भन्सार|अन्तःशुल्क|राजस्व|बजेट|दामासाही|टीडीएस|अग्रिम कर)", re.I)
_YEAR_TAIL = re.compile(r"([०-९0-9]{4})\s*$")
_ANNUAL_ACT = re.compile(r"(आर्थिक ऐन|विनियोजन ऐन|राष्ट्र ऋण|ऋण तथा जमानत)")
# regulator directives/circulars (NRB, SEBON, Company Registrar) only answer
# banking, securities and company-filing questions; elsewhere they crowd out
# the governing statute
_REGULATOR_DOC = re.compile(r"^reg-(nrb|sebon|ocr)-")
_REGULATOR_QUERY = re.compile(
    r"(\bbank|\bbfi\b|\bnrb\b|rastra bank|loan|interest rate|foreign exchange|forex|remittance|kyc|\baml\b|"
    r"microfinance|cooperative|securit|share|\bipo\b|sebon|broker|mutual fund|debenture|stock|"
    r"company regist|annual return|\bocr\b|"
    # romanised + English retail-banking words (a message typed in Latin script never contains the Devanagari)
    r"\bbaink|\bbyank|\batm\b|debit card|credit card|minimum balance|penal (?:interest|rate|byaj)|base rate|mobile banking|"
    r"finance compan|laghubitta|\bkarja|\bbyaj|\bhundi\b|videshi mudra|remit|"
    r"बैंक|बैङ्क|राष्ट्र बैंक|ऋण|कर्जा|ब्याज|विदेशी विनिमय|विदेशी मुद्रा|सटही|रेमिट|विप्रेषण|लघुवित्त|वित्तीय संस्था|सहकारी|"
    r"एटीएम|डेबिट कार्ड|क्रेडिट कार्ड|न्यूनतम मौज्दात|पेनाल|आधार दर|हुण्डी|"
    r"धितोपत्र|शेयर|सेयर|आईपीओ|ब्रोकर|दलाल|डिबेन्चर|म्युचुअल|कम्पनी रजिस्ट्रार|वार्षिक विवरण)", re.I)
# A question a retail-banking regulator (NRB) directive answers: it names a bank / financial institution / card
# AND something a bank does to a customer (a loan, interest, a charge, an account balance, a complaint,
# remittance...), or is one of the unmistakable banking phrases on its own. Then the NRB Unified Directive
# passages are searched for explicitly (they rank below the Acts on generic overlap) and private-lender
# Civil Code rules are kept out. "cheque" and "jamanat" are deliberately not service words: a bounced-cheque
# or bail question that mentions a bank is a statute question.
_BANK_ACTOR = re.compile(
    r"(\bbank|\bbfi\b|\bnrb\b|rastra bank|\bbaink|\bbyank|finance compan|laghubitta|microfinance|\batm\b|"
    r"debit card|credit card|बैंक|बैङ्क|वित्तीय संस्था|लघुवित्त|फाइनान्स|एटीएम|डेबिट कार्ड|क्रेडिट कार्ड)", re.I)
_BANK_SERVICE = re.compile(
    r"(loan|karja|\brin\b|कर्जा|ऋण|byaj|interest|ब्याज|penal|पेनाल|charge|\bfees?\b|shulka|शुल्क|"
    r"account|\bkhata|खाता|balance|mauj?dat|मौज्दात|fixed deposit|savings|निक्षेप|complain|gunaso|गुनासो|"
    r"\bkaa?t(?:yo|eko|era|ti|a[yi]e|ayo|e)\b|कट्टा|remit|विप्रेषण|forex|exchange|सटही|kyc|\bcard|कार्ड|mobile banking|"
    r"statement|locker|emi\b|kisti|किस्ता|late payment|delay|hidden|service)", re.I)
_BANK_STANDALONE = re.compile(
    r"(minimum balance|penal interest|penal rate|base rate|foreign exchange|forex|remittance|\bhundi\b|"
    r"न्यूनतम मौज्दात|पेनाल ब्याज|आधार दर|विदेशी विनिमय|विप्रेषण|हुण्डी)", re.I)
# a question about a loan between private people: the Civil Code's private-creditor rules DO apply
_PRIVATE_LENDER = re.compile(
    r"(\bsahu|sahuji|moneylender|money lender|byajwala|sudkhor|\bfriend\b|\bsathi|\budhar|\budhaar|sapati|"
    r"relative|neighbou?r|साहु|सापटी|उधारो|साथी|छिमेकी|नातेदार)", re.I)
_CIVIL_CODE = "मुलुकी देवानी संहिता"
_PRIVATE_CREDIT_HEADING = re.compile(r"(साहू|ऋणी|ब्याज|साँवा|सावाँ)")
# the retail-customer directive shard: commercial banks / development banks / finance companies ("क, ख, ग");
# "घ" is the microfinance shard, so it is preferred only when the question is about microfinance
_NRB_RETAIL_SHARD = "परिपत्र नं. १० (क, ख, ग)"
_NRB_MICRO_SHARD = "परिपत्र नं. ६ (घ)"
_MICRO_QUERY = re.compile(r"(microfinance|laghubitta|लघुवित्त)", re.I)
_BANK_DOC = re.compile(r"(बैङ्क|बैंक|वित्तीय|निक्षेप)")  # a banking statute may lead the list; any other Act follows the directives


# Devanagari spelling slips that the index cannot read: a nasal written as a half consonant before a sibilant
# (अन्श for अंश). A respelling is accepted only when every token of it is an index word and the original is not.
_NASAL_RESPELL = (("न्श", "ंश"), ("न्स", "ंस"), ("म्श", "ंश"), ("म्स", "ंस"))
_DEV_WORD = re.compile(r"[\u0900-\u0963\u0966-\u097f]+")


def respell_devanagari(text: str) -> str:
    """`text` with known Devanagari spelling slips corrected (unchanged when nothing needs it)."""
    if not text or not re.search(r"[\u0900-\u097f]", text):
        return text
    vocab = getattr(get_index(), "vocab", None)
    if not vocab:
        return text

    def known(word: str) -> bool:
        return all(t in vocab for t in tokenize(word))

    def fix(m: re.Match) -> str:
        word = m.group(0)
        if known(word):
            return word
        for a, b in _NASAL_RESPELL:
            if a in word and known(word.replace(a, b)):
                return word.replace(a, b)
        return word

    return _DEV_WORD.sub(fix, text)
# the same rule for the other regulators: each only answers its own field
_AUTHORITY_DOMAIN = {
    "ppmo": re.compile(r"(procure|tender|bid\b|bidding|contractor|e-gp|खरिद|बोलपत्र|टेन्डर|ठेक्का|निर्माण व्यवसायी|ई-जीपी)", re.I),
    "nia": re.compile(r"(insur|reinsur|policy ?holder|premium|claim|बीमा|बिमा|प्रिमियम|दाबी भुक्तानी|पुनर्बीमा)", re.I),
    "moless": re.compile(r"(labou?r|employ|worker|wage|salary|overtime|social security|\bssf\b|child labou?r|workplace|"
                         r"foreign employment|manpower|talab|श्रम|कामदार|मजदुर|रोजगार|तलब|पारिश्रमिक|ज्याला|ओभरटाइम|"
                         r"सामाजिक सुरक्षा|बालश्रम|कार्यस्थल|वैदेशिक रोजगार|म्यानपावर)", re.I),
}
_AUTHORITY_ID = re.compile(r"^reg-(ppmo|nia|moless)-")
_NKP_YEAR = re.compile(r"ने\.?\s?का\.?\s?प\.?\s*([०-९0-9]{4})")


def _is_fiscal_query(message: str, analysis: dict) -> bool:
    text = " ".join([message, analysis.get("question") or "", analysis.get("area") or ""])
    return bool(_FISCAL_QUERY.search(text))


def _is_regulator_query(message: str, analysis: dict) -> bool:
    text = " ".join([message, analysis.get("question") or "", analysis.get("area") or ""])
    return bool(_REGULATOR_QUERY.search(text))


def _is_bank_query(text: str) -> bool:
    """A retail-banking question (see _BANK_ACTOR/_BANK_SERVICE): NRB directives are the governing text."""
    return bool(_BANK_STANDALONE.search(text) or (_BANK_ACTOR.search(text) and _BANK_SERVICE.search(text)))


def _bs_year(pattern: re.Pattern, text: str) -> int | None:
    m = pattern.search(text or "")
    return int(m.group(1).translate(_DEV)) if m else None


def mark_stale_precedents(laws: list[dict], precedents: list[dict]) -> list[dict]:
    """A precedent decided before the statute now governing the topic was
    enacted interprets older law. Flag it (it stays visible, labelled) and
    rank it after current-law precedents; the verifier refuses to let it be
    the only support for a quantified rule."""
    # annual Finance/Appropriation Acts are re-enacted every year, so their
    # year says nothing about when the underlying law last changed
    law_years = [y for y in (_bs_year(_YEAR_TAIL, s.get("doc_title_ne") or "") for s in laws[:4]
                             if not _ANNUAL_ACT.search(s.get("doc_title_ne") or "")) if y]
    governing = max(law_years) if law_years else None
    out = []
    for p in precedents:
        year = _bs_year(_NKP_YEAR, p.get("source_ne") or "")
        stale = bool(governing and year and year < governing)
        out.append({**p, "stale": stale, "decided_bs": year, "governing_law_bs": governing if stale else None})
    return sorted(out, key=lambda p: p["stale"])  # stable: current-law precedents first


def pinned_provisions(playbook: dict | None) -> list[dict]:
    """The curated playbook's own provisions, fetched as full corpus entries
    - hand-verified to govern this exact situation, so they lead the evidence."""
    if not playbook:
        return []
    idx = get_index()
    out = []
    for p in playbook.get("provisions", []):
        if not (p.get("slug") and p.get("section")):
            continue
        entry = playbooks.lookup_entry(idx, {"law_title_ne": p.get("law_title_ne") or "", "section": p["section"],
                                             "entry_title_contains": p.get("entry_title_contains"),
                                             "contains": p.get("contains")}) if p.get("law_title_ne") else None
        if entry is None:
            entry = idx.section(p["slug"], p["section"])
        if entry:
            entry = {k: v for k, v in entry.items() if k not in ("prev", "next")}
            out.append({**entry, "score": 1.0, "pinned": True})
    return out


# ---- relevance gate for a curated playbook's pins ---------------------------------------------------------
# A playbook is matched from keywords, which are loose: one shared word can pin a plan for a different
# situation, and its provisions then displace the law that governs. A pin is therefore trusted only when
#  (a) an exact keyword phrase of the plan is in the question, or the romanised-Nepali lexicon independently
#      names a statute the plan's provisions come from (a trusted match), or
#  (b) retrieval independently agrees: one of the plan's own provisions (or a neighbouring section of the
#      same document) is among the top PIN_SUPPORT_DEPTH passages the QUESTION retrieves without the plan's help.
# Otherwise the plan is dropped (pins, action-plan card and guide), and retrieval stands on its own.
PIN_SUPPORT_DEPTH = 20
PIN_NEIGHBOUR = 2
PIN_RESERVED_FOR_RETRIEVAL = 3  # of the top_k statute slots, at least this many stay with retrieval
PIN_MIN_SLOTS = 3
_SEC_NUM_ASCII = re.compile(r"^\s*(\d+)")


def _sec_number(section) -> int | None:
    m = _SEC_NUM_ASCII.match(str(section or ""))
    return int(m.group(1)) if m else None


def _ref_supported_by(ref: dict, s: dict) -> bool:
    """`s` (a retrieved passage) is the plan's provision `ref` or a neighbouring section of the same document."""
    if (s.get("doc_title_ne") or "") != (ref.get("law_title_ne") or ""):
        return False
    if ref.get("entry_title_contains"):
        return ref["entry_title_contains"] in (s.get("title_ne") or "")
    a, b = _sec_number(ref.get("section")), _sec_number(s.get("section"))
    if a is None or b is None:
        return str(ref.get("section") or "") == str(s.get("section") or "")
    return abs(a - b) <= PIN_NEIGHBOUR


def playbook_support(playbook: dict | None, retrieved: list[dict], depth: int = PIN_SUPPORT_DEPTH) -> int:
    """How many of the top `depth` retrieved passages back one of the plan's provisions."""
    if not playbook:
        return 0
    refs = playbook.get("provisions", [])
    return sum(1 for s in retrieved[:depth] if any(_ref_supported_by(r, s) for r in refs))


def search(message: str, analysis: dict, top_k: int | None = None, precedent_k: int | None = None,
           playbook: dict | None = None) -> list[dict]:
    return search_with_playbook(message, analysis, top_k, precedent_k, playbook)[0]


def search_with_playbook(message: str, analysis: dict, top_k: int | None = None, precedent_k: int | None = None,
                         playbook: dict | None = None) -> tuple[list[dict], dict | None]:
    """Retrieval for one question -> (sources, the playbook that survived the relevance gate or None).
    Callers that show the plan (card, guide) must use the returned playbook, not the one they passed in."""
    idx = get_index()
    top_k = top_k or config.TOP_K
    precedent_k = config.PRECEDENT_K if precedent_k is None else precedent_k
    queries = build_queries(message, analysis)
    # only a confidently matched plan may steer retrieval (title boost) before the gate has looked at it
    trusted = bool(playbook and playbook.get("_trusted"))
    boost = (list(analysis.get("laws", [])) + translit.laws(message)
             + ([p.get("law_title_ne") for p in playbook.get("provisions", [])] if trusted else []))
    depth = max(top_k + 6, PIN_SUPPORT_DEPTH) if playbook else top_k + 6
    laws = idx.search(queries, top_k=depth, boost_titles=[b for b in boost if b], category="law")
    if not _is_fiscal_query(message, analysis):
        on_domain = [s for s in laws if not _FISCAL_DOC.search(s.get("doc_title_ne") or "")
                     and not s["id"].startswith("reg-ird-")]
        laws = on_domain or laws
    if not _is_regulator_query(message, analysis):
        on_domain = [s for s in laws if not _REGULATOR_DOC.match(s["id"])]
        laws = on_domain or laws
    q_text = " ".join([message, analysis.get("question") or "", analysis.get("area") or ""])
    on_domain = [s for s in laws if not (m := _AUTHORITY_ID.match(s["id"]))
                 or _AUTHORITY_DOMAIN[m.group(1)].search(q_text)]
    laws = on_domain or laws

    bank = _is_bank_query(q_text)
    if bank and not _PRIVATE_LENDER.search(q_text):
        # a bank's loan/charge is governed by the BFI Act and NRB directives, not by the Civil Code's rules
        # between private lender and borrower (10% cap, interest-in-writing...)
        on_domain = [s for s in laws if not ((s.get("doc_title_ne") or "").startswith(_CIVIL_CODE)
                                             and _PRIVATE_CREDIT_HEADING.search(s.get("title_ne") or ""))]
        laws = on_domain or laws

    if playbook and not trusted and not playbook_support(playbook, laws):
        log.info("playbook %s dropped: none of its provisions is among the top %d retrieved for the question",
                 playbook.get("id"), PIN_SUPPORT_DEPTH)
        playbook = None
    pinned = pinned_provisions(playbook)
    retrieved_ids = [s["id"] for s in laws]
    # pins the question's own retrieval also found lead; the rest keep the editor's order
    # a plan with many provisions must not fill the whole list: keep room for what retrieval found. Which pins
    # stay: the ones the question's own retrieval also found first, then the editor's order; the survivors keep
    # the editor's order (first provision = most important)
    keep = max(PIN_MIN_SLOTS, top_k - PIN_RESERVED_FOR_RETRIEVAL)
    if len(pinned) > keep:
        ranked = sorted(range(len(pinned)),
                        key=lambda i: (pinned[i]["id"] not in retrieved_ids, i))[:keep]
        pinned = [pinned[i] for i in sorted(ranked)]
    seen = {p["id"] for p in pinned}
    # sections the curated plan marks as misleading for this situation
    # (e.g. deposit recovery vs. the tenant's early-departure notice rule)
    excluded = {(x.get("law_title_ne"), str(x.get("section"))) for x in (playbook or {}).get("exclude_provisions", [])}
    rest = [s for s in laws if s["id"] not in seen
            and (s.get("doc_title_ne"), str(s.get("section") or "")) not in excluded]
    if bank:
        # NRB directives rank below the Acts on generic overlap, so a banking question that names its
        # governing directive would otherwise never see it: search the directive shards explicitly and
        # put their best passages right behind the leading statute
        reg = [s for s in _nrb_directive_hits(idx, queries, q_text, boost) if s["id"] not in seen]
        reg_ids = {s["id"] for s in reg}
        lead = [s for s in rest[:1] if s["id"] not in reg_ids and _BANK_DOC.search(s.get("doc_title_ne") or "")]
        rest = lead + reg + [s for s in rest if s["id"] not in reg_ids and s not in lead]
    laws = (pinned + rest)[:max(top_k, len(pinned))]
    precedents = []
    if precedent_k and analysis.get("wants_precedent", True):
        precedents = idx.search(queries, top_k=precedent_k + 2, category="precedent", per_doc_cap=1)
        precedents = mark_stale_precedents(laws, precedents)[:precedent_k]
    # interleave so the strongest statute passages lead, precedents follow
    return laws + precedents, playbook


NRB_ROUTE_MAX = 3


def _nrb_directive_hits(idx, queries, q_text: str, boost: list) -> list[dict]:
    """The best NRB directive passages for a banking question, from the customer-facing shard first."""
    shard = _NRB_MICRO_SHARD if _MICRO_QUERY.search(q_text) else _NRB_RETAIL_SHARD
    try:
        hits = idx.search(queries, top_k=NRB_ROUTE_MAX * 3, boost_titles=[b for b in boost if b] + [shard],
                          category="law", doc_type="directive", per_doc_cap=NRB_ROUTE_MAX)
    except Exception as e:  # noqa: BLE001 - routing is an extra; never break retrieval
        log.warning("regulator routing failed: %s", str(e)[:200])
        return []
    hits = [s for s in hits if s["id"].startswith("reg-nrb-")]
    return hits[:NRB_ROUTE_MAX]


_SENT_SPLIT = re.compile(r"(?<=[।?!])\s+|\n+|(?=\([क-ह०-९0-9]{1,3}\)\s)")


def focus(text: str, query_terms: set[str], limit: int = 700) -> str:
    """The part of a passage that matters for this question: the heading line
    plus the run of sentences around the best-matching one, within `limit`
    chars. Keeps prompts small - Nepali is token-heavy and free tiers cap
    tokens per minute - without dropping the relevant clause."""
    text = text.strip()
    if len(text) <= limit:
        return text
    parts = [p.strip() for p in _SENT_SPLIT.split(text) if p and p.strip()]
    if not parts:
        return text[:limit]
    head = parts[0][:160]
    scores = [len(query_terms & set(tokenize(p))) for p in parts]
    best = max(range(len(parts)), key=lambda i: (scores[i], -i))
    lo = hi = best
    size = len(parts[best])
    while True:  # grow the window toward whichever neighbour matches more
        cand = []
        if lo - 1 > 0:
            cand.append((scores[lo - 1], lo - 1))
        if hi + 1 < len(parts):
            cand.append((scores[hi + 1], hi + 1))
        if not cand:
            break
        _, j = max(cand)
        if size + len(parts[j]) + 1 > limit - len(head):
            break
        size += len(parts[j]) + 1
        lo, hi = min(lo, j), max(hi, j)
    body = " ".join(parts[lo:hi + 1])[: limit - len(head)]
    prefix = "" if lo == 0 else head + " … "
    return prefix + body + (" …" if hi < len(parts) - 1 else "")


def _passage(i: int, s: dict, lang: str, terms: set[str] | None = None, tail: bool = False) -> str:
    """One numbered passage for the prompt, in ONE language (V3.2 token diet): the English translation when
    the person asks in English and the passage has one, else the Nepali text. Precedents get a shorter window
    (their opening is the court header; the holding is what the focus window finds)."""
    title = s.get("title_ne") or s.get("title_en") or ""
    cite = s.get("source_ne") if lang == "ne" else (s.get("source_en") or s.get("source_ne"))
    limit = config.PRECEDENT_PASSAGE_CHARS if (tail or s.get("category") == "precedent") else config.PASSAGE_CHARS
    if lang == "en" and s.get("text_en"):
        body = f"[English translation]: {focus(s['text_en'], terms or set(), limit)}"
    else:
        body = focus(s.get("text_ne") or "", terms or set(), limit)
    kind = "Supreme Court precedent" if s.get("category") == "precedent" else "Statute"
    if s.get("stale"):
        kind += (f", OLDER LAW: decided in BS {s.get('decided_bs')}, before the governing Act of BS "
                 f"{s.get('governing_law_bs')} - historical context only, never state its rule as current law")
    elif s.get("pinned"):
        kind += ", verified as governing this situation"
    status = s.get("status")
    if s.get("category") != "precedent" and status and status != "in_force":
        kind += f", status: {status}"
    return f"[{i}] ({kind}) {cite}\nTitle: {title}\n{body}"


def prompt_source_numbers(sources: list[dict], playbook: dict | None = None) -> list[int]:
    """1-based numbers of the sources SENT to the model (all of `sources` stay citable and verifiable; a
    source the model never sees cannot be cited, and the numbers are the original ones). With a curated
    playbook pin the pinned provisions are the governing law: only PROMPT_EXTRA_LAWS_WITH_PIN other statutes
    ride along; without one, the top PROMPT_MAX_LAWS. At most PROMPT_MAX_PRECEDENTS precedents (current-law
    ones first: retrieval already sorts them)."""
    pinned = [i for i, s in enumerate(sources, 1) if s.get("pinned")]
    laws = [i for i, s in enumerate(sources, 1) if s.get("category") != "precedent"]
    precs = [i for i, s in enumerate(sources, 1) if s.get("category") == "precedent"]
    if pinned:
        rest = [i for i in laws if i not in pinned][:config.PROMPT_EXTRA_LAWS_WITH_PIN]
        keep = set(pinned) | set(rest)
    else:
        keep = set(laws[:config.PROMPT_MAX_LAWS])
    keep |= set(precs[:config.PROMPT_MAX_PRECEDENTS])
    return sorted(keep)


def answer_max_tokens(lang: str, n_sources: int) -> int:
    """Output budget for the answer JSON. Groq/Gemini free tiers count the requested output against the
    per-minute token limit (and Groq's qwen refuses 6000), so ask for what the answer can need: Nepali is
    ~2.5x the tokens of English; a small source set cannot support a long answer."""
    if lang == "ne":
        return max(1200, min(config.ANSWER_MAX_TOKENS_NE, config.ANSWER_TOKENS_BASE_NE + config.ANSWER_TOKENS_PER_SOURCE_NE * n_sources))
    return max(800, min(config.ANSWER_MAX_TOKENS_EN, config.ANSWER_TOKENS_BASE_EN + config.ANSWER_TOKENS_PER_SOURCE_EN * n_sources))


def _terms(message: str, analysis: dict) -> set[str]:
    words = [message] + list(analysis.get("queries_ne") or []) + glossary.expand(message)
    return set(tokenize(" ".join(words)))


_BRACKET = re.compile(r"\[([^\[\]\d०-९][^\[\]]{2,160}?)\]")
_SEC_NUM = re.compile(r"(?:Section|Article|Rule|दफा|धारा|नियम)\s*([0-9०-९]+)", re.I)


_DEV = str.maketrans("०१२३४५६७८९", "0123456789")


def normalize_citations(answer: str, sources: list[dict]) -> str:
    """Models sometimes cite as "[Muluki Civil Code 2074, Section 400]"
    instead of "[3]"; map those to the numbered source when the section
    and law match one, so every citation is clickable."""
    def fix(m):
        inner = m.group(1)
        sec = _SEC_NUM.search(inner)
        if not sec:
            return m.group(0)
        num = sec.group(1).translate(str.maketrans("०१२३४५६७८९", "0123456789"))
        words = set(re.findall(r"[a-z]{4,}|[ऀ-ॿ]{3,}", inner.lower()))
        for i, s in enumerate(sources, 1):
            cite = f"{s.get('source_en') or ''} {s.get('source_ne') or ''}"
            if (s.get("section") or "").split(" ")[0] == num and \
                    words & set(re.findall(r"[a-z]{4,}|[ऀ-ॿ]{3,}", cite.lower())):
                return f"({inner}) [{i}]"
        return m.group(0)
    # gpt-oss writes 【4】 / 【4†source】; some models use Devanagari digits [४]
    answer = re.sub(r"【\s*(\d{1,2})\s*(?:†[^】]*)?】", r"[\1]", answer)
    answer = re.sub(r"\[([०-९]{1,2})\]", lambda m: f"[{m.group(1).translate(_DEV)}]", answer)
    return _BRACKET.sub(fix, answer)


UNVERIFIED_HEADER = {
    "en": "I could not verify a written summary against the official sources, so here are the most relevant "
          "provisions themselves:",
    "ne": "लिखित सारांशलाई आधिकारिक स्रोतसँग पुष्टि गर्न सकिएन, त्यसैले सबैभन्दा सान्दर्भिक प्रावधानहरू नै यहाँ दिइएको छ:",
}


def _extractive(sources: list[dict], lang: str, header: str | None = None) -> str:
    header = header or ("Here are the most relevant official provisions I found (AI summary unavailable right now):"
                        if lang == "en" else "सबैभन्दा सान्दर्भिक आधिकारिक कानुनी प्रावधानहरू (AI सारांश अहिले उपलब्ध छैन):")
    lines = [header]
    for i, s in enumerate(sources[:5], 1):
        cite = s.get("source_en") if lang == "en" and s.get("source_en") else s.get("source_ne")
        text = (s.get("text_en") if lang == "en" and s.get("text_en") else s.get("text_ne")) or ""
        lines.append(f"\n**[{i}] {cite}**\n{text[:700]}")
    lines.append("\n" + (DISCLAIMER_EN if lang == "en" else DISCLAIMER_NE))
    return "\n".join(lines)


PLAYBOOK_LOOSE_MIN_SCORE = 1.0


def _playbook_id_for(text: str) -> str | None:
    """A playbook id for `text`, or None. The keyword matcher alone is loose:
    a single shared word ("boss", "sasu", "police") can half-match a playbook
    for a different situation, and a wrong pin puts the wrong law at the top
    of the answer. So a match is trusted when (a) an exact keyword phrase is in
    the text, or (b) the lexicon knows which statutes the message is about and
    the playbook's own provisions come from one of them, or (c) with no lexicon
    signal, the keyword score is high (>= 3).

    Whatever passes here is still only a candidate: `search_with_playbook` drops a
    non-strong candidate that the question's own retrieval does not corroborate
    (see PIN_SUPPORT_DEPTH)."""
    return _playbook_pick(text)[0]


def _playbook_pick(text: str) -> tuple[str | None, bool]:
    """(playbook id or None, trusted). Trusted = an exact keyword phrase of the plan is in `text`, or the lexicon
    independently names a statute the plan's provisions come from. A match on loose keyword overlap alone (no
    lexicon signal) is not trusted: search_with_playbook keeps it only if retrieval corroborates it."""
    strong = strong_playbook_match(text)
    if strong:
        return strong, True
    got = match_playbook_scored(text)
    if not got:
        return None, False
    pid, score = got
    lex_laws = translit.laws(text)
    if lex_laws:
        try:
            pb_laws = {p.get("law_title_ne") for p in playbooks.get_playbook(pid).get("provisions", [])}
        except playbooks.UnresolvedProvision:
            return None, False
        return (pid, True) if pb_laws & set(lex_laws) else (None, False)
    return (pid if score >= PLAYBOOK_LOOSE_MIN_SCORE else None), False


def _match_playbook(message: str, analysis: dict) -> dict | None:
    """The curated action plan for this situation, when the keyword matcher
    is confident. Tries the raw message, then the LLM's standalone rewrite
    (which resolves follow-ups like "what about my deposit?"). The result carries
    `_trusted` (exact keyword phrase, or the lexicon agrees on the statute); a plan
    that is not trusted must be corroborated by retrieval before it is used
    (search_with_playbook)."""
    for text in (message, respell_devanagari(message), analysis.get("question") or ""):
        if text:
            pid, trusted = _playbook_pick(text)
            if pid:
                try:
                    pb = playbooks.get_playbook(pid)
                except playbooks.UnresolvedProvision as e:
                    # corpus drift: answer without the playbook rather than fail the chat
                    log.warning("playbook %s unresolved: %s", pid, e)
                    return None
                if pb is not None:
                    pb["_trusted"] = trusted
                return pb
    return None


def _playbook_card(playbook: dict | None) -> dict | None:
    if not playbook:
        return None
    return {"id": playbook["id"], "issue": playbook["issue"], "fact_questions": playbook.get("fact_questions", []),
            "forum": playbook.get("forum"), "limitation": playbook.get("limitation", {}).get("note")}


def _playbook_guide(playbook: dict | None, lang: str) -> str:
    """Editor-written steps/evidence from the curated plan: guidance for the
    answer's structure, not a citable source."""
    if not playbook:
        return ""
    key = "ne" if lang == "ne" else "en"
    steps = "\n".join(f"- {s.get(key) or s.get('en')}" for s in playbook.get("next_steps", []))
    evidence = "\n".join(f"- {s.get(key) or s.get('en')}" for s in playbook.get("evidence", []))
    forum = (playbook.get("forum") or {}).get(key) or ""
    return (f"Curated action plan for this situation (editorial guidance, not a source: use it only for "
            f"\"procedure\"/\"advice\" sentences with no cites, no numbers and no legal-rule wording):\n"
            f"Where to go: {forum}\nNext steps:\n{steps}\nEvidence to collect:\n{evidence}\n\n")


def _guidance_terms_text(playbook: dict | None) -> str:
    """Every step/forum/evidence line of the plan in both languages: the only
    place an uncited procedure sentence may come from."""
    if not playbook:
        return ""
    bits = [(playbook.get("forum") or {}).get(k) or "" for k in ("en", "ne")]
    for key in ("next_steps", "evidence"):
        for s in playbook.get(key, []):
            bits += [s.get("en") or "", s.get("ne") or ""]
    return " ".join(bits)


_EMPTY_TAIL = re.compile(r"(\n\s*(\*\*[^*\n]+\*\*|#{1,6}[^\n]*)\s*:?\s*)+\s*$")
_DHARA = re.compile(r"धारा(\s*[०-९0-9])")


def tidy_answer(answer: str, sources: list[dict]) -> str:
    """Drop a trailing heading with nothing under it (a cut-off stream) and
    fix "धारा" (constitutional article) used for a statute's "दफा" when no
    cited source is the Constitution."""
    answer = _EMPTY_TAIL.sub("", answer.rstrip()).rstrip()
    if not any(s.get("doc_type") == "constitution" for s in sources):
        answer = _DHARA.sub(r"दफा\1", answer)
    return answer


def _prompt(message: str, analysis: dict, sources: list[dict], lang: str, history: list[dict] | None,
            playbook: dict | None = None) -> str:
    terms = _terms(analysis.get("question") or message, analysis)
    shown = prompt_source_numbers(sources, playbook)
    # the leading statutes (and every pinned one) get the full window; lower-ranked ones a shorter window
    full = {i for i in shown if sources[i - 1].get("pinned")} | set(
        [i for i in shown if sources[i - 1].get("category") != "precedent"][:config.PROMPT_FULL_WINDOW_LAWS])
    context = "\n\n".join(_passage(i, sources[i - 1], lang, terms, tail=i not in full) for i in shown)
    hist = _history_text(history, limit=4)
    return (
        f"Official sources:\n{context}\n\n"
        + _playbook_guide(playbook, lang)
        + (f"Earlier conversation (context only):\n{hist}\n\n" if hist else "")
        + f"Person's concern (as understood): {analysis.get('concern') or '-'}\n"
        f"Person's message: {prompt_guard.wrap_user_text(message)}\n\n"
        f"{'Reply in English.' if lang == 'en' else 'Reply in Nepali (Devanagari).'} "
        f"Return only the JSON object described in the instructions."
    )


def check_context(message: str, analysis: dict, sources: list[dict], playbook: dict | None) -> claim_checks.CheckContext:
    """What the V3.2 sentence checks may know: the user's question (+ the model's standalone rewrite), its
    stemmed topic terms and the retrieved statutes' section titles (for the precedent topic gate), and the
    matched playbook's text (the only place an uncited office/forum may come from)."""
    q = analysis.get("question") or message
    return claim_checks.CheckContext(
        question=" ".join(x for x in (message, analysis.get("question")) if x),
        topic_terms=frozenset(_terms(q, analysis)),
        law_terms=claim_checks.law_topic_terms(sources),
        guidance=_guidance_terms_text(playbook))


def run(message: str, language: str = "auto", history: list[dict] | None = None, tier: str = "free"):
    """The whole pipeline as events: ("meta", {language, sources, analysis}),
    then ("status", ...)? ("delta", text)* ("replace", full_text)? while the answer is written, then
    ("done", {...}). The concatenated deltas (or the last `replace` text plus any deltas after it) always
    equal done["answer"].
    Non-legal messages (greetings, thanks, off-topic, too vague) get a direct
    reply and no sources; legal ones get a grounded, cited answer, or the
    matching provisions if no model responds in time.

    `tier` (S13): "free" uses the existing multi-provider free chain
    (llm.stream, unchanged); "haiku"/"sonnet" bills a specific Anthropic
    model directly (llm.paid_complete) for a paid-plan user - no streaming
    mid-generation (the Anthropic SDK call is synchronous), but the "done"
    event's `usage` lets the caller log a real cost per query. A cache hit
    never re-runs the LLM regardless of tier, so it carries no usage."""
    lang_hint = guess_language(message) if language == "auto" else language
    ckey = _answer_cache_key(message + " \u2016 " + _history_text(history), language)
    cached = _answer_cache.get(ckey)
    if cached is None and not history:
        # L2: persistent cache, survives restarts/redeploys (in-memory L1
        # above doesn't). Skipped for follow-ups - the key already includes
        # history, so this would almost never hit anyway, and it's not worth
        # a network round trip for messages that are cheap to just answer.
        remote = supa.cache_get(ckey, get_index().digest)
        if remote is not None:
            cached = remote
            _answer_cache.put(ckey, remote)  # warm L1 for this process too
    if cached is not None:
        yield "meta", {"language": cached["language"], "sources": cached["sources"],
                       "analysis": cached.get("analysis"), "playbook": cached.get("playbook")}
        yield "done", {"answer": cached["answer"], "llm_used": cached["llm_used"], "cached": True, "llm_calls": 0,
                       "verification": cached.get("verification")}
        return

    # llm_calls counts pipeline stages that reached a provider (analyze,
    # answer), not per-provider/key retries inside llm.complete/stream.
    llm_calls = 1 if analyze_needs_llm(message, lang_hint, history) else 0
    analysis = analyze_query(message, lang_hint, history)
    lang = language if language in ("en", "ne") else lang_hint  # script/word-based, not the model's guess
    meta_analysis = {k: analysis.get(k) for k in ("concern", "area", "queries_ne", "laws", "intent")}
    playbook = _match_playbook(message, analysis)
    if playbook and analysis.get("intent") in ("unclear", "off_topic"):
        analysis["intent"] = "legal"  # a curated action plan matched: that's a legal question we can answer

    if analysis.get("intent", "legal") != "legal":
        reply = (analysis.get("reply") or "").strip()
        if not reply or (lang == "en") == bool(re.search(r"[\u0900-\u097f]", reply)):
            # the model replied in the other language: use our own wording instead
            reply = CANNED.get((analysis["intent"], lang)) or CANNED[("unclear", lang)]
        yield "meta", {"language": lang, "sources": [], "analysis": meta_analysis}
        yield "done", {"answer": reply, "llm_used": analysis.get("llm", False), "cached": False, "llm_calls": llm_calls}
        return

    query = analysis.get("question") or message
    sources = search(query, analysis, playbook=playbook)
    if playbook and not any(s.get("pinned") for s in sources):
        playbook = None  # the relevance gate (search_with_playbook) dropped the plan: no card, no guide
    playbook_card = _playbook_card(playbook)
    yield "meta", {"language": lang, "sources": sources, "analysis": meta_analysis, "playbook": playbook_card}

    if not sources:
        yield "done", {"answer": CANNED[("unclear", lang)], "llm_used": False, "cached": False, "llm_calls": llm_calls}
        return
    if not llm.available():
        yield "done", {"answer": _extractive(sources, lang), "llm_used": False, "cached": False, "llm_calls": llm_calls}
        return

    llm_calls += 1
    # Generate-then-verify, progressively: the model's JSON is streamed and every sentence is checked the
    # moment it is complete; only sentences that pass are emitted (as `delta`). At the end the full
    # finalisation runs (fallback / entailment / gaps / disclaimer); whatever it adds is appended as more
    # deltas, and if it changes text that was already shown a `replace` event carries the final text.
    yield "status", {"stage": "checking sources"}
    prompt_text = _prompt(message, analysis, sources, lang, history, playbook)
    ctx = check_context(message, analysis, sources, playbook)
    if config.STREAM_VERIFIED:
        result, usage, streamed = yield from _stream_generate(prompt_text, sources, lang, tier, playbook, ctx=ctx)
    else:
        (result, usage), streamed = _generate_verified(prompt_text, sources, lang, tier, playbook, ctx=ctx), ""
    verification = None
    if result is None:
        answer, llm_used = _extractive(sources, lang), False
    elif result["answer"] is None:
        # nothing (or too little) survived verification: give the provisions themselves, and say so
        answer, llm_used, verification = _extractive(sources, lang, UNVERIFIED_HEADER[lang]), False, result["verification"]
    else:
        answer, llm_used, verification = tidy_answer(result["answer"], sources), True, result["verification"]
    if not streamed:
        yield from _simulate_stream(answer)
    elif answer.startswith(streamed):
        yield from _simulate_stream(answer[len(streamed):])  # gaps / follow-ups / disclaimer (or nothing)
    else:
        yield "replace", answer  # finalisation changed text already shown: `answer` is authoritative
    if llm_used:
        payload = {"answer": answer, "language": lang, "sources": sources, "llm_used": True,
                   "analysis": meta_analysis, "playbook": playbook_card, "verification": verification}
        _answer_cache.put(ckey, payload)
        if not history:
            supa.cache_put(ckey, get_index().digest, lang, message, payload)
    yield "done", {"answer": answer, "llm_used": llm_used, "cached": False, "llm_calls": llm_calls,
                   "tier": tier, "usage": usage, "prompt_version": ANSWER_PROMPT_VERSION,
                   "flagged_injection": prompt_guard.looks_like_injection(message),
                   "verification": verification}


def _simulate_stream(answer: str):
    pieces = list(structured.chunks(answer, 40))
    delay = min(config.STREAM_CHUNK_DELAY_S, 1.5 / max(1, len(pieces)))
    for piece in pieces:
        yield "delta", piece
        if delay > 0:
            time.sleep(delay)


def _generate_verified(prompt_text: str, sources: list[dict], lang: str, tier: str, playbook: dict | None, *,
                       raw: str | None = None, cut_off: bool = False, usage: dict | None = None,
                       budget_s: float | None = None, ctx: claim_checks.CheckContext | None = None):
    """(structured.build() result | None if no model answered, usage). Never raises. With `raw` (a reply that
    was already streamed) no generation call is made: it is only finalised (repair / verify / entailment)."""
    # Devanagari costs ~3x the tokens of English, and JSON adds keys and quotes
    max_tokens = answer_max_tokens(lang, len(prompt_source_numbers(sources, playbook)))
    system = answer_system(lang)
    paid = tier != "free"
    budget = budget_s if budget_s is not None else config.ANSWER_JSON_BUDGET_S
    model = tiers.model_for_tier(tier) if paid else None
    haiku = tiers.model_for_tier("haiku")

    def add_usage(u: dict):
        nonlocal usage
        usage = {k: (usage or {}).get(k, 0) + u.get(k, 0) for k in ("input_tokens", "output_tokens")}

    def paid_call(system, user, **kw):
        text, u = llm.paid_complete(kw.pop("model", model), system, user, max_tokens=kw.get("max_tokens", max_tokens),
                                    temperature=kw.get("temperature", 0.2), budget_s=kw.get("budget_s"))
        add_usage(u)
        return text

    if raw is None:
        try:
            if paid:
                raw = paid_call(system, prompt_text, budget_s=budget)
            else:
                raw = llm.complete(system, prompt_text, json_mode=True, max_tokens=max_tokens,
                                   budget_s=budget, call_timeout_s=config.ANSWER_JSON_CALL_TIMEOUT_S)
            cut_off = llm.was_cut_off()
        except Exception as e:  # noqa: BLE001
            log.warning("answer generation failed: %s", str(e)[:200])
            return None, usage

    def repair(bad: str) -> str:
        if paid:
            return paid_call(structured.REPAIR_SYSTEM, bad[:16000], model=haiku, budget_s=25)
        return llm.complete(structured.REPAIR_SYSTEM, bad[:16000], fast=True, json_mode=True,
                            max_tokens=max_tokens, budget_s=20, temperature=0.0)

    entail = None
    if config.ENTAILMENT_CHECK or paid:  # ONE extra fast-tier call over a compact payload (see structured.entail_payload)
        call = (lambda system, user, **kw: paid_call(system, user, model=haiku, max_tokens=kw.get("max_tokens", 300),
                                                     temperature=0.0, budget_s=20)) if paid else llm.complete
        question = ctx.question if ctx is not None else ""
        entail = lambda doc: structured.entailment_filter(  # noqa: E731
            doc, call, question=question, drop_partial=config.ENTAILMENT_DROP_PARTIAL)
    disclaimer = DISCLAIMER_EN if lang == "en" else DISCLAIMER_NE
    try:
        return structured.build(raw, sources, lang, guidance=_guidance_terms_text(playbook), disclaimer=disclaimer,
                                cut_off=cut_off, repair=repair, entail=entail, ctx=ctx), usage
    except Exception:  # noqa: BLE001 - a verifier bug must degrade to the extractive answer, not a 500
        log.exception("structured answer build failed")
        return None, usage


_DHARA_PIECE = re.compile(r"धारा(\s*[०-९0-9])")


def _tidy_piece(piece: str, sources: list[dict]) -> str:
    """The per-piece part of tidy_answer (the constitutional "धारा" fix), so streamed text equals tidied text."""
    if any(s.get("doc_type") == "constitution" for s in sources):
        return piece
    return _DHARA_PIECE.sub(r"दफा\1", piece)


def _stream_generate(prompt_text: str, sources: list[dict], lang: str, tier: str, playbook: dict | None, *,
                     ctx: claim_checks.CheckContext | None = None):
    """Stream the model's JSON, verifying every sentence as it completes. A generator: yields ("delta", text)
    for verified text and returns (result, usage, streamed_text) where `result` is the authoritative
    structured.build() of the whole reply (or of the non-streamed fallback) and `streamed_text` is exactly
    what was emitted. Never raises."""
    paid = tier != "free"
    max_tokens = answer_max_tokens(lang, len(prompt_source_numbers(sources, playbook)))
    system = answer_system(lang)
    budget = config.ANSWER_JSON_BUDGET_S
    started = time.time()
    sv = structured.StreamVerifier(sources, _guidance_terms_text(playbook), config.STREAM_MIN_RULES, ctx=ctx)
    info: dict = {}
    parts: list[str] = []
    streamed = ""
    err: Exception | None = None
    cut_off = False
    src = None
    try:
        if paid:
            src = llm.paid_stream(tiers.model_for_tier(tier), system, prompt_text, max_tokens=max_tokens,
                                  budget_s=budget, info=info)
        else:
            src = llm.stream_json(system, prompt_text, max_tokens=max_tokens, budget_s=budget, info=info)
        for delta in src:
            parts.append(delta)
            text = sv.feed(delta)
            if text:
                text = _tidy_piece(text, sources)
                streamed += text
                yield "delta", text
            if time.time() - started > budget:
                cut_off = True  # out of time: what is complete so far is finalised, the rest dropped
                break
    except Exception as e:  # noqa: BLE001 - provider failure before or mid-stream
        err = e
        log.warning("streamed answer failed after %d chars: %s", sum(map(len, parts)), str(e)[:200])
    finally:
        if src is not None:
            src.close()
    usage = info.get("usage")
    raw = "".join(parts)
    if not raw.strip():
        # nothing streamed (no streaming provider, or it never started): the V3 non-streamed call
        result, usage = _generate_verified(prompt_text, sources, lang, tier, playbook, usage=usage, ctx=ctx,
                                           budget_s=max(15.0, budget - (time.time() - started)))
        return result, usage, streamed
    cut_off = cut_off or err is not None or llm.was_cut_off(info.get("finish") or "")
    result, usage = _generate_verified(prompt_text, sources, lang, tier, playbook, raw=raw, cut_off=cut_off, usage=usage,
                                       ctx=ctx)
    if err is not None and (result is None or result.get("answer") is None):
        left = budget - (time.time() - started)
        if left > 12:  # the partial reply was not enough: one non-streamed attempt (the replace path swaps it in)
            fb, usage = _generate_verified(prompt_text, sources, lang, tier, playbook, usage=usage, budget_s=left, ctx=ctx)
            if fb is not None and fb.get("answer") is not None:
                result = fb
    return result, usage, streamed


def stream_answer(message: str, language: str = "auto", history: list[dict] | None = None, tier: str = "free"):
    yield from run(message, language, history, tier=tier)


def answer_question(message: str, language: str = "auto", history: list[dict] | None = None,
                    tier: str = "free") -> dict:
    result: dict = {"answer": "", "sources": [], "llm_used": False}
    for kind, data in run(message, language, history, tier=tier):
        if kind == "meta":
            result.update(language=data["language"], sources=data["sources"], analysis=data["analysis"],
                          playbook=data.get("playbook"))
        elif kind == "done":
            result.update(answer=data["answer"], llm_used=data["llm_used"], cached=data.get("cached", False),
                          llm_calls=data.get("llm_calls", 0), tier=data.get("tier", "free"),
                          usage=data.get("usage"), prompt_version=data.get("prompt_version"),
                          flagged_injection=data.get("flagged_injection", False),
                          verification=data.get("verification"))
    return result
