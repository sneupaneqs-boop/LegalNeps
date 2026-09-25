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

from . import config, glossary, llm
from .retrieval import get_index
from .text_norm import detect_language, fold, tokenize

log = logging.getLogger(__name__)

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

Return JSON with exactly these keys:
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


def analyze_query(message: str, lang_hint: str) -> dict:
    key = _cache_key(message, lang_hint)
    cached = _analysis_cache.get(key)
    if cached is not None:
        return cached
    base = {"reply_language": lang_hint, "concern": "", "area": "", "queries_ne": [],
            "queries_en": [], "laws": [], "wants_precedent": True, "llm": False}
    if not llm.available():
        return base
    try:
        raw = llm.complete(ANALYZE_SYSTEM, f"Question: {message}", fast=True, json_mode=True,
                           max_tokens=1000, temperature=0.1)
        data = llm.parse_json(raw)
        out = {**base, **{k: data.get(k, base[k]) for k in base if k != "llm"}, "llm": True}
        for k in ("queries_ne", "queries_en", "laws"):
            out[k] = [str(x) for x in (out[k] or []) if str(x).strip()][:6]
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


def search(message: str, analysis: dict, top_k: int | None = None, precedent_k: int | None = None) -> list[dict]:
    idx = get_index()
    top_k = top_k or config.TOP_K
    precedent_k = config.PRECEDENT_K if precedent_k is None else precedent_k
    queries = build_queries(message, analysis)
    laws = idx.search(queries, top_k=top_k, boost_titles=analysis.get("laws", []), category="law")
    precedents = []
    if precedent_k and analysis.get("wants_precedent", True):
        precedents = idx.search(queries, top_k=precedent_k, category="precedent", per_doc_cap=1)
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
    return f"[{i}] ({kind}) {cite}\nTitle: {title}\n{body}"


def _terms(message: str, analysis: dict) -> set[str]:
    words = [message] + list(analysis.get("queries_ne") or []) + glossary.expand(message)
    return set(tokenize(" ".join(words)))


_BRACKET = re.compile(r"\[([^\[\]\d०-९][^\[\]]{2,160}?)\]")
_SEC_NUM = re.compile(r"(?:Section|Article|Rule|दफा|धारा|नियम)\s*([0-9०-९]+)", re.I)


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


def answer_question(message: str, language: str = "auto") -> dict:
    lang_hint = detect_language(message) if language == "auto" else language
    ckey = _cache_key(message, language)
    cached = _answer_cache.get(ckey)
    if cached is not None:
        return {**cached, "cached": True}

    analysis = analyze_query(message, lang_hint)
    lang = analysis.get("reply_language") or lang_hint
    if language in ("en", "ne"):
        lang = language
    sources = search(message, analysis)

    llm_used = False
    if not sources:
        answer = ("I couldn't find an official provision that matches this question. Could you describe "
                  "the situation in a bit more detail (who, what happened, where)?" if lang == "en" else
                  "यस प्रश्नसँग मिल्ने आधिकारिक कानुनी प्रावधान फेला परेन। कृपया अलि विस्तारमा बताउनुहोस् "
                  "(को, के भयो, कहाँ)?")
    elif llm.available():
        terms = _terms(message, analysis)
        context = "\n\n".join(_passage(i, s, lang, terms) for i, s in enumerate(sources, 1))
        user = (
            f"Official sources:\n{context}\n\n"
            f"Person's concern (as understood): {analysis.get('concern') or '-'}\n"
            f"Person's message: {message}\n\n"
            f"{'Reply in English.' if lang == 'en' else 'Reply in Nepali (Devanagari).'}"
        )
        try:
            answer = normalize_citations(llm.complete(ANSWER_SYSTEM, user, max_tokens=1800, temperature=0.2), sources)
            llm_used = True
        except Exception as e:  # noqa: BLE001
            log.warning("generation failed, using extractive fallback: %s", str(e)[:200])
            answer = _extractive(sources, lang)
    else:
        answer = _extractive(sources, lang)

    result = {"answer": answer, "language": lang, "sources": sources, "llm_used": llm_used,
              "analysis": {k: analysis.get(k) for k in ("concern", "area", "queries_ne", "laws")}}
    if llm_used:
        _answer_cache.put(ckey, result)
    return result


def stream_answer(message: str, language: str = "auto"):
    """Event generator for the streaming endpoint:
    ("meta", {...sources...}) -> ("delta", text)* -> ("done", {...})."""
    lang_hint = detect_language(message) if language == "auto" else language
    ckey = _cache_key(message, language)
    cached = _answer_cache.get(ckey)
    if cached is not None:
        yield "meta", {"language": cached["language"], "sources": cached["sources"], "analysis": cached.get("analysis")}
        yield "done", {"answer": cached["answer"], "llm_used": cached["llm_used"], "cached": True}
        return

    analysis = analyze_query(message, lang_hint)
    lang = language if language in ("en", "ne") else (analysis.get("reply_language") or lang_hint)
    sources = search(message, analysis)
    meta_analysis = {k: analysis.get(k) for k in ("concern", "area", "queries_ne", "laws")}
    yield "meta", {"language": lang, "sources": sources, "analysis": meta_analysis}

    if not sources or not llm.available():
        answer = answer_question(message, language)["answer"] if not sources else _extractive(sources, lang)
        yield "done", {"answer": answer, "llm_used": False, "cached": False}
        return

    terms = _terms(message, analysis)
    context = "\n\n".join(_passage(i, s, lang, terms) for i, s in enumerate(sources, 1))
    user = (
        f"Official sources:\n{context}\n\n"
        f"Person's concern (as understood): {analysis.get('concern') or '-'}\n"
        f"Person's message: {message}\n\n"
        f"{'Reply in English.' if lang == 'en' else 'Reply in Nepali (Devanagari).'}"
    )
    parts: list[str] = []
    try:
        for piece in llm.stream(ANSWER_SYSTEM, user):
            parts.append(piece)
            yield "delta", piece
        answer = normalize_citations("".join(parts), sources)
        llm_used = True
    except Exception as e:  # noqa: BLE001
        log.warning("streaming generation failed: %s", str(e)[:200])
        answer = "".join(parts) or _extractive(sources, lang)
        llm_used = bool(parts)
    result = {"answer": answer, "language": lang, "sources": sources, "llm_used": llm_used, "analysis": meta_analysis}
    if llm_used:
        _answer_cache.put(ckey, result)
    yield "done", {"answer": answer, "llm_used": llm_used, "cached": False}


# Backwards-compatible helper used by older callers/tests.
def generate_answer(message: str, sources: list[dict], lang: str) -> tuple[str, bool]:
    if not llm.available():
        return _extractive(sources, lang), False
    context = "\n\n".join(_passage(i, s, lang) for i, s in enumerate(sources, 1))
    user = f"Official sources:\n{context}\n\nPerson's message: {message}\n\n" + (
        "Reply in English." if lang == "en" else "Reply in Nepali (Devanagari).")
    try:
        return llm.complete(ANSWER_SYSTEM, user), True
    except Exception:  # noqa: BLE001
        return _extractive(sources, lang), False
