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

import logging
import re
from collections import OrderedDict
from threading import Lock

from . import config, glossary, llm, playbooks, prompt_guard, supa, tiers, verifier
from .playbook_matcher import match as match_playbook
from .retrieval import get_index
from .text_norm import detect_language, fold, guess_language, tokenize

log = logging.getLogger(__name__)

# S13: bump when ANSWER_SYSTEM's wording changes materially, so llm_usage
# rows say which prompt version produced an answer.
ANSWER_PROMPT_VERSION = "answer_v1"

DISCLAIMER_EN = (
    "This is general legal information, not a substitute for advice from a "
    "licensed Nepali advocate. For anything urgent or high-stakes, please consult a lawyer."
)
DISCLAIMER_NE = (
    "यो सामान्य कानुनी जानकारी मात्र हो, इजाजतपत्रप्राप्त अधिवक्ताको सल्लाहको विकल्प होइन। "
    "जरुरी वा महत्वपूर्ण विषयमा कृपया वकिलसँग सम्पर्क गर्नुहोस्।"
)

ANALYZE_SYSTEM = """You are a Nepali legal research assistant. Convert a person's question into \
search queries for a corpus that contains ONLY official Nepali-language statutes (Constitution, \
Acts/ऐन, Codes/संहिता, Regulations/नियमावली, Orders) and Supreme Court precedents (नेपाल कानून \
पत्रिका), all written in formal legal Nepali.

People type anything: greetings, thanks, follow-ups to the earlier conversation, vague or \
off-topic messages. Classify first, then (for legal questions) plan the search.

Return JSON with exactly these keys:
- "intent": one of "legal" (asks about law, rights, a legal problem or procedure - even vaguely \
or emotionally described), "greeting", "thanks", "smalltalk" (chit-chat, questions about you), \
"off_topic" (clearly not about law), "unclear" (legal-ish but too vague to search, e.g. "help me").
- "reply": for any intent other than "legal", a short warm reply in the reply language: answer \
the greeting/thanks/smalltalk briefly, say you help with Nepali law for off_topic, or ask ONE \
specific clarifying question for unclear. Empty string for "legal".
- "question": for "legal", the person's question rewritten as a complete, self-contained question \
(resolve follow-ups like "what about daughters?" using the earlier conversation); else "".
- "reply_language": "ne" if the person wrote in Nepali (Devanagari or romanised Nepali like \
"mero ghar"), else "en".
- "concern": one sentence restating the person's real underlying legal concern, in the reply language.
- "area": short legal area in English (e.g. "family law - divorce", "landlord-tenant", "criminal - assault").
- "queries_ne": 4-6 short Nepali search phrases (2-7 words each) using the exact formal vocabulary \
Nepali statutes use (e.g. landlord/tenant -> "घर बहाल", "बहालवाला", "घरधनी"; deposit -> "धरौटी"; \
divorce -> "सम्बन्ध विच्छेद"; property share -> "अंश"; limitation period -> "हदम्याद"; \
rape -> "जबरजस्ती करणी"; cheating -> "ठगी"; wage -> "पारिश्रमिक"). Include the specific \
provision topic, not just the area.
- "queries_en": 1-2 short English phrases.
- "laws": up to 4 exact Nepali titles of the statutes most likely to govern this \
(e.g. "मुलुकी देवानी संहिता, २०७४", "मुलुकी अपराध संहिता, २०७४", "नेपालको संविधान", \
"श्रम ऐन, २०७४", "उपभोक्ता संरक्षण ऐन, २०७५", "घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६").
- "wants_precedent": true if court interpretation/precedent would help answer, else false."""

ANSWER_SYSTEM = """You are Kanooni Sathi ("Legal Friend"), a warm, precise bilingual \
(English/Nepali) legal-information assistant for Nepal.

Grounding rules (strict):
- Use ONLY the numbered passages in "Official sources". They are verbatim extracts from Nepal Law \
Commission publications and Supreme Court (Nepal Kanoon Patrika) decisions, in Nepali.
- Cite every legal statement with the passage NUMBER ONLY in square brackets, placed at the end of \
the sentence: e.g. "...must give 35 days' notice (Muluki Civil Code 2074, Section 400) [3]." Name the \
law and section in the sentence text, never inside the brackets - brackets contain only digits like \
[3] or [1][4]. Never invent a law, section, number, deadline, fine or case that is not in the passages.
- If the passages don't cover the question, say so plainly, share only what they do support, and \
suggest what to ask a lawyer or which office to approach.
- Passages may contain small OCR/typing glitches; read through them, but don't quote garbled words.
- Passages marked "verified as governing this situation" are the core law for this question: build \
the answer on them first. Passages marked "OLDER LAW" may only be mentioned as history - never \
present their deadlines, amounts or procedures as the current rule. Never present a passage whose \
status is "bill" or "repealed" as current law.
- Every number you state (days, months, years, rupees, percentages, section numbers) must appear in \
the passage you cite for it. If you are not sure of a number, don't state it.
- Don't state a legal remedy, offence or procedure that no passage mentions (e.g. don't suggest a \
criminal complaint unless a passage makes the act an offence).
- In Nepali, statute sections are "दफा" and regulation provisions are "नियम"; only the Constitution \
uses "धारा".

How to answer:
- Start with one short sentence showing you understood the real concern.
- Then give the direct answer, followed by the key rules (short bullet points), concrete next \
steps (which office/court, documents, time limits - only if in the passages), and a relevant \
Supreme Court precedent if one is provided.
- Plain language, short sentences, no unexplained jargon. When answering in English, translate \
the Nepali provisions faithfully.
- Reply entirely in the requested language (Nepali in natural Devanagari).
- End with one empathetic line and the disclaimer that this is general information, not a \
substitute for a licensed advocate."""

ANSWER_SYSTEM += "\n\n" + prompt_guard.UNTRUSTED_TEXT_NOTICE
ANALYZE_SYSTEM += "\n\n" + prompt_guard.UNTRUSTED_TEXT_NOTICE


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
PIPELINE_VERSION = "p2"


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


def confidence(message: str, lang: str) -> float:
    """How sure we are this message is a legal question we can search well
    without an LLM rewriting it - i.e. it already contains vocabulary our
    statute-Nepali index matches (directly, since statutes are in Nepali, or
    via the glossary's English/romanised -> Nepali expansion). Used to skip
    analyze_query's LLM call for the common case; low-confidence messages
    still get the full LLM analysis. quick_intent() has already filtered out
    greetings/thanks/smalltalk/obvious-off-topic before this is called, so a
    Nepali-script message reaching here is almost always a real legal
    question - the LLM's main value for it is polishing search phrasing, not
    deciding whether to search at all.
    """
    if lang == "ne":
        return 0.9
    expansion = glossary.expand(message)
    return min(1.0, 0.3 * len(expansion)) if expansion else 0.0


CONFIDENCE_THRESHOLD = 0.6


def analyze_needs_llm(message: str, lang_hint: str, history: list[dict] | None = None) -> bool:
    """Whether analyze_query() will reach a provider for this message - kept
    in sync with analyze_query()'s own short-circuits so run()'s llm_calls
    count stays accurate without duplicating the decision logic."""
    if quick_intent(message) is not None or not llm.available():
        return False
    if not history and confidence(message, lang_hint) >= CONFIDENCE_THRESHOLD:
        return False
    return True


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
    if not history and confidence(message, lang_hint) >= CONFIDENCE_THRESHOLD:
        # skip the LLM call: build_queries() already does glossary expansion
        # and searches the raw Nepali message directly, so a confident
        # message searches just as well without an LLM-rewritten query set.
        # Follow-ups always go through the LLM (needs history to resolve
        # "what about daughters?" into a standalone question).
        out = {**base, "question": message}
        _analysis_cache.put(key, out)
        return out
    try:
        prompt = (f"Earlier conversation:\n{hist}\n\n" if hist else "") + \
            f"Latest message: {prompt_guard.wrap_user_text(message)}"
        raw = llm.complete(ANALYZE_SYSTEM, prompt, fast=True, json_mode=True,
                           max_tokens=1000, temperature=0.1)
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
    """Weighted query set: the LLM's Nepali legal phrasings carry most
    weight; glossary expansion translates English/romanised words locally;
    the raw message counts less when it isn't Nepali (English words mostly
    match English-heavy noise like forms and dictionaries)."""
    is_ne = detect_language(message) == "ne"
    expansion = glossary.expand(message)
    queries: list[tuple[str, float]] = [(message, 1.0 if is_ne else (0.35 if (expansion or analysis.get("queries_ne")) else 1.0))]
    queries += [(q, 1.0) for q in analysis.get("queries_ne", [])]
    queries += [(q, 0.4) for q in analysis.get("queries_en", [])]
    if expansion:
        queries.append((" ".join(expansion), 1.0 if not analysis.get("queries_ne") else 0.7))
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
_NKP_YEAR = re.compile(r"ने\.?\s?का\.?\s?प\.?\s*([०-९0-9]{4})")


def _is_fiscal_query(message: str, analysis: dict) -> bool:
    text = " ".join([message, analysis.get("question") or "", analysis.get("area") or ""])
    return bool(_FISCAL_QUERY.search(text))


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
        entry = idx.section(p["slug"], p["section"])
        if entry:
            entry = {k: v for k, v in entry.items() if k not in ("prev", "next")}
            out.append({**entry, "score": 1.0, "pinned": True})
    return out


def search(message: str, analysis: dict, top_k: int | None = None, precedent_k: int | None = None,
           playbook: dict | None = None) -> list[dict]:
    idx = get_index()
    top_k = top_k or config.TOP_K
    precedent_k = config.PRECEDENT_K if precedent_k is None else precedent_k
    queries = build_queries(message, analysis)
    pinned = pinned_provisions(playbook)
    boost = list(analysis.get("laws", [])) + [p.get("law_title_ne") for p in (playbook or {}).get("provisions", [])]
    laws = idx.search(queries, top_k=top_k + 6, boost_titles=[b for b in boost if b], category="law")
    if not _is_fiscal_query(message, analysis):
        on_domain = [s for s in laws if not _FISCAL_DOC.search(s.get("doc_title_ne") or "")]
        laws = on_domain or laws
    seen = {p["id"] for p in pinned}
    laws = pinned + [s for s in laws if s["id"] not in seen]
    laws = laws[:max(top_k, len(pinned))]
    precedents = []
    if precedent_k and analysis.get("wants_precedent", True):
        precedents = idx.search(queries, top_k=precedent_k + 2, category="precedent", per_doc_cap=1)
        precedents = mark_stale_precedents(laws, precedents)[:precedent_k]
    # interleave so the strongest statute passages lead, precedents follow
    return laws + precedents


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


def _passage(i: int, s: dict, lang: str, terms: set[str] | None = None) -> str:
    title = s.get("title_ne") or s.get("title_en") or ""
    cite = s.get("source_ne") if lang == "ne" else (s.get("source_en") or s.get("source_ne"))
    body = focus(s.get("text_ne") or "", terms or set(), config.PASSAGE_CHARS)
    if s.get("text_en"):
        body += f"\n[English translation]: {focus(s['text_en'], terms or set(), config.PASSAGE_CHARS)}"
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


def _extractive(sources: list[dict], lang: str) -> str:
    header = ("Here are the most relevant official provisions I found (AI summary unavailable right now):"
              if lang == "en" else "सबैभन्दा सान्दर्भिक आधिकारिक कानुनी प्रावधानहरू (AI सारांश अहिले उपलब्ध छैन):")
    lines = [header]
    for i, s in enumerate(sources[:5], 1):
        cite = s.get("source_en") if lang == "en" and s.get("source_en") else s.get("source_ne")
        text = (s.get("text_en") if lang == "en" and s.get("text_en") else s.get("text_ne")) or ""
        lines.append(f"\n**[{i}] {cite}**\n{text[:700]}")
    lines.append("\n" + (DISCLAIMER_EN if lang == "en" else DISCLAIMER_NE))
    return "\n".join(lines)


def _match_playbook(message: str, analysis: dict) -> dict | None:
    """The curated action plan for this situation, when the keyword matcher
    is confident. Tries the raw message, then the LLM's standalone rewrite
    (which resolves follow-ups like "what about my deposit?")."""
    for text in (message, analysis.get("question") or ""):
        if text:
            pid = match_playbook(text)
            if pid:
                try:
                    return playbooks.get_playbook(pid)
                except playbooks.UnresolvedProvision as e:
                    # corpus drift: answer without the playbook rather than fail the chat
                    log.warning("playbook %s unresolved: %s", pid, e)
                    return None
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
    return (f"Curated action plan for this situation (editorial guidance - use it to structure next steps "
            f"and evidence; do NOT cite it, cite only the numbered passages):\n"
            f"Where to go: {forum}\nNext steps:\n{steps}\nEvidence to collect:\n{evidence}\n\n")


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
    context = "\n\n".join(_passage(i, s, lang, terms) for i, s in enumerate(sources, 1))
    hist = _history_text(history, limit=4)
    return (
        f"Official sources:\n{context}\n\n"
        + _playbook_guide(playbook, lang)
        + (f"Earlier conversation (context only):\n{hist}\n\n" if hist else "")
        + f"Person's concern (as understood): {analysis.get('concern') or '-'}\n"
        f"Person's message: {prompt_guard.wrap_user_text(message)}\n\n"
        f"{'Reply in English.' if lang == 'en' else 'Reply in Nepali (Devanagari).'}"
    )


def run(message: str, language: str = "auto", history: list[dict] | None = None, tier: str = "free"):
    """The whole pipeline as events: ("meta", {language, sources, analysis}),
    then ("delta", text)* while the answer is written, then ("done", {...}).
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
    ckey = _answer_cache_key(message + "\x00" + _history_text(history), language)
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
    playbook_card = _playbook_card(playbook)

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
    yield "meta", {"language": lang, "sources": sources, "analysis": meta_analysis, "playbook": playbook_card}

    if not sources:
        yield "done", {"answer": CANNED[("unclear", lang)], "llm_used": False, "cached": False, "llm_calls": llm_calls}
        return
    if not llm.available():
        yield "done", {"answer": _extractive(sources, lang), "llm_used": False, "cached": False, "llm_calls": llm_calls}
        return

    llm_calls += 1
    parts: list[str] = []
    usage: dict | None = None
    prompt_text = _prompt(message, analysis, sources, lang, history, playbook)
    # Devanagari costs ~3x the tokens of English for the same content; the
    # old flat 1800 cut Nepali answers off mid-section.
    max_tokens = 3000 if lang == "ne" else 1800
    try:
        if tier == "free":
            for piece in llm.stream(ANSWER_SYSTEM, prompt_text, max_tokens=max_tokens):
                parts.append(piece)
                yield "delta", piece
        else:
            model = tiers.model_for_tier(tier)
            text, usage = llm.paid_complete(model, ANSWER_SYSTEM, prompt_text, max_tokens=max_tokens)
            parts.append(text)
            yield "delta", text
        answer = tidy_answer(normalize_citations("".join(parts), sources), sources)
        llm_used = True
    except Exception as e:  # noqa: BLE001
        log.warning("answer generation failed: %s", str(e)[:200])
        answer = "".join(parts) or _extractive(sources, lang)
        llm_used = bool(parts)
    if llm_used and len(answer.strip()) < 200:
        # the model's stream stopped after a sentence or two: still give the
        # person the provisions that answer their question, and don't cache it
        answer = answer.rstrip() + "\n\n" + _extractive(sources, lang)
        llm_used = False
    verification = None
    if llm_used:
        answer, verification = verifier.verify(answer, sources, lang)
        payload = {"answer": answer, "language": lang, "sources": sources, "llm_used": True,
                   "analysis": meta_analysis, "playbook": playbook_card, "verification": verification}
        _answer_cache.put(ckey, payload)
        if not history:
            supa.cache_put(ckey, get_index().digest, lang, message, payload)
    yield "done", {"answer": answer, "llm_used": llm_used, "cached": False, "llm_calls": llm_calls,
                   "tier": tier, "usage": usage, "prompt_version": ANSWER_PROMPT_VERSION,
                   "flagged_injection": prompt_guard.looks_like_injection(message),
                   "verification": verification}


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
