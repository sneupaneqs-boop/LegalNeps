"""V3: generate-then-verify answers.

The model returns ONE JSON object (blocks of sentences, each with a kind and
the verbatim passage quote it rests on). Nothing is shown until verifier.py has
checked every sentence against the retrieved passages; sentences that fail are
deleted. This module owns the prompt, tolerant parsing (a cut-off object is
salvaged sentence by sentence), the optional LLM entailment pass, and rendering
of the surviving sentences into the markdown the UI already displays.
"""
from __future__ import annotations

import json
import logging
import os
import re
import time

from . import claim_checks, llm, verifier
from .claim_checks import CheckContext

log = logging.getLogger(__name__)

MIN_VERIFIED_RULES = 2  # fewer verified rule/deadline/penalty sentences than this -> extractive fallback

STRUCTURED_RULES = """You are Kanooni Sathi, a careful bilingual (English/Nepali) legal-information assistant \
for Nepal. Reply with ONE JSON object only. Code checks each sentence against the numbered passages and DELETES \
any whose quote is not verbatim in the passage it cites or that says more than its quote.

Schema: {"blocks":[{"heading":"","sentences":[{"text":"","kind":"rule|deadline|penalty|procedure|advice|empathy",\
"cites":[{"n":3,"quote":""}]}]}],"gaps":[""],"follow_up_questions":[""]}

Rules:
1. Blocks: heading "" with ONE empathy sentence; direct answer; key rules; next steps; a Supreme Court precedent \
ONLY if provided and its quote states a rule for this person's situation and topic. Short headings, reply \
language. Sentence text: plain prose, no [n], no markdown. Answer the asked quantity (how much/many/long) first; \
never restate a provision under a second heading; never open a sentence with a connective or demonstrative \
(But, Such, This, तर, त्यसै गरी).
2. rule/deadline/penalty = anything the law says, requires, allows, punishes or how long it takes. It needs \
cites: {"n": passage number, "quote": 6-40 words copied CHARACTER FOR CHARACTER from that one passage} (Nepali \
text, or the "[English translation]" if you answer in English). Never paraphrase, translate or join spans. One \
idea per sentence.
3. Quote the WHOLE conditional clause and copy its who/when/only-if words (सगोलको, सम्बन्ध विच्छेद भएको, notice \
period, उपदफा (N) बमोजिम, "तर" provisos). Never widen the subject (no children/relatives the quote does not \
name). If unsure, quote more or omit.
4. Every number, unit and section number must be in the quote, tied to the same unit ("पन्ध्र लाख" = fifteen \
lakh). Never restate a number from the person's message. An "additional/थप" penalty only with its base penalty \
in the same sentence.
5. Name law and section (दफा for Acts/Codes, नियम for Rules, धारा only for the Constitution). Passages "verified \
as governing" first. "OLDER LAW" only as history, say so. Never present a bill/repealed/lapsed passage as law; \
an "ordinance" is temporary - say so. "Supreme Court" only with a precedent passage.
6. The "Curated action plan" is guidance, not a source: only for procedure/advice sentences with NO cites, \
numbers or rule wording. Name no office, tribunal, court, department or required document that no passage or \
that plan names; an office/forum/document in advice needs a cite or the plan.
7. A passage about a different subject than the question (another regime, population or chapter) is not used: say \
"not covered". "gaps" ("The sources retrieved do not cover X", reply language) ONLY when no passage covers X; never "the law \
does not say". At most 3 gaps and 3 short follow_up_questions, no numbers.
8. Quote OCR glitches as printed. Reply entirely in the requested language (natural Devanagari for Nepali), \
under about 550 words."""

EXAMPLE_EN = """Example (passage [1] is Labour Act, 2074, section 162, English translation: "A worker aggrieved \
by an act contrary to this Act may file a complaint within six months from the date of the act."):
{"blocks":[{"heading":"","sentences":[{"text":"I understand how stressful unpaid salary is.","kind":"empathy",\
"cites":[]}]},{"heading":"Direct answer","sentences":[{"text":"Under the Labour Act, 2074, Section 162, you can \
file a complaint within 6 months of the act.","kind":"deadline","cites":[{"n":1,"quote":"may file a complaint \
within six months from the date of the act"}]}]},{"heading":"Next steps","sentences":[{"text":"Gather your \
appointment letter and pay slips.","kind":"advice","cites":[]}]}],"gaps":["The sources retrieved do not cover \
which office can order the wages to be paid."],"follow_up_questions":["When was your last salary paid?"]}"""

EXAMPLE_NE = """Example (passage [1] is मुलुकी देवानी संहिता, २०७४, दफा ३८६: "कुनै व्यक्तिले घर बहालमा दिँदा \
देहायका कुराहरू खुलाई बहालमा लिने व्यक्तिसँग लिखित सम्झौता गर्नु पर्नेछ"):
{"blocks":[{"heading":"","sentences":[{"text":"धरौटी फिर्ता नभएकोले तपाईंलाई चिन्ता भएको मैले बुझें।","kind":"empathy",\
"cites":[]}]},{"heading":"मुख्य नियम","sentences":[{"text":"मुलुकी देवानी संहिता, २०७४ को दफा ३८६ अनुसार घर \
बहालमा दिँदा बहालमा लिने व्यक्तिसँग लिखित सम्झौता गर्नु पर्छ।","kind":"rule","cites":[{"n":1,"quote":"घर बहालमा दिँदा \
देहायका कुराहरू खुलाई बहालमा लिने व्यक्तिसँग लिखित सम्झौता गर्नु पर्नेछ"}]}]}],"gaps":["मैले पाएका स्रोतहरूले धरौटी \
फिर्ता गर्ने म्याद समेटेका छैनन्।"],"follow_up_questions":[]}"""

# Only the example in the reply language is sent: the other one is ~250 tokens of dead weight per request
# (V3.2 token diet). STRUCTURED_ANSWER_SYSTEM (rules + both examples) is the full text, kept for fingerprints/tests.
STRUCTURED_ANSWER_SYSTEM = STRUCTURED_RULES + "\n\n" + EXAMPLE_EN + "\n\n" + EXAMPLE_NE


def system_prompt(lang: str) -> str:
    """The answer system prompt for a reply language: rules + the one worked example in that language."""
    return STRUCTURED_RULES + "\n\n" + (EXAMPLE_NE if lang == "ne" else EXAMPLE_EN)


REPAIR_SYSTEM = ("You repair broken JSON. The user message is a JSON object of a legal answer that failed to parse "
                 "(maybe cut off). Return ONLY the repaired, valid JSON object, keeping every complete sentence exactly "
                 "as written and dropping any half-written one. Do not add content.")

ENTAIL_SYSTEM = (
    "You check legal statements against the passage span each one quotes, for THIS person's situation "
    "(\"situation\"). Per item answer one letter: y = the quote states a rule that governs this situation and "
    "supports the exact statement (who, when, only-if, numbers); p = it supports only part of it, or drops a "
    "condition or party; n = it does not support it, contradicts it, or is a rule for another situation (another "
    "kind of lender or borrower, a divorced vs a merely separated spouse, another subject). Judge only from the "
    "quote. Return JSON {\"v\":[\"y\",\"n\",...]}, one letter per item, in order.")

HEADINGS = {
    "gaps": {"en": "What the sources don't cover", "ne": "स्रोतहरूले नसमेटेको कुरा"},
    "ask": {"en": "It would help to know", "ne": "थाहा भए अझ सहयोग हुन्छ"},
}


# ------------------------------------------------------------------ parsing
def _norm_sentence(s) -> dict | None:
    if not isinstance(s, dict) or not isinstance(s.get("text"), str) or not s["text"].strip():
        return None
    cites = []
    for c in s.get("cites") or []:
        if isinstance(c, dict):
            cites.append({"n": c.get("n"), "quote": c.get("quote") if isinstance(c.get("quote"), str) else ""})
    return {"text": s["text"].strip(), "kind": s.get("kind"), "cites": cites}


def _norm_doc(obj) -> dict | None:
    if not isinstance(obj, dict) or not isinstance(obj.get("blocks"), list):
        return None
    blocks = []
    for b in obj["blocks"]:
        if not isinstance(b, dict):
            continue
        sents = [x for x in (_norm_sentence(s) for s in b.get("sentences") or []) if x]
        if sents:
            blocks.append({"heading": str(b.get("heading") or "").strip(), "sentences": sents})
    strs = lambda v: [x.strip() for x in v if isinstance(x, str) and x.strip()] if isinstance(v, list) else []  # noqa: E731
    return {"blocks": blocks, "gaps": strs(obj.get("gaps")), "follow_up_questions": strs(obj.get("follow_up_questions"))}


_DEC = json.JSONDecoder()
_WS_COMMA = " \n\r\t,"


def _objects_from(text: str, pos: int) -> tuple[list[dict], bool, int]:
    """Complete {...} objects of the array whose items start at `pos`; whether
    the array closed; and where the unfinished item (if any) starts."""
    out = []
    while pos < len(text):
        while pos < len(text) and text[pos] in _WS_COMMA:
            pos += 1
        if pos >= len(text):
            break
        if text[pos] == "]":
            return out, True, pos
        if text[pos] != "{":
            break
        try:
            obj, end = _DEC.raw_decode(text, pos)
        except json.JSONDecodeError:
            return out, False, pos  # the half-written one: dropped
        out.append(obj)
        pos = end
    return out, False, len(text)


def _salvage(text: str) -> dict | None:
    """Every complete block, and every complete sentence of the block that was cut off."""
    m = re.search(r'"blocks"\s*:\s*\[', text)
    if not m:
        return None
    blocks, closed, rest = _objects_from(text, m.end())
    if not closed and rest < len(text):
        frag = text[rest:]  # the unfinished last block: keep its heading and complete sentences
        sm = re.search(r'"sentences"\s*:\s*\[', frag)
        if sm:
            hm = re.search(r'"heading"\s*:\s*"((?:[^"\\]|\\.)*)"', frag[:sm.start()])
            sents, _, _ = _objects_from(frag, sm.end())
            if sents:
                try:
                    heading = json.loads(f'"{hm.group(1)}"') if hm else ""
                except ValueError:
                    heading = ""
                blocks.append({"heading": heading, "sentences": sents})
    obj: dict = {"blocks": blocks}
    for key in ("gaps", "follow_up_questions"):
        km = re.search(rf'"{key}"\s*:\s*\[', text)
        if km:
            try:
                obj[key] = _DEC.raw_decode(text, km.end() - 1)[0]
            except json.JSONDecodeError:
                pass
    return obj


_SENT_START = re.compile(r'\{\s*"text"\s*:')
_HEADING_TOKEN = re.compile(r'"heading"\s*[:,]\s*(?:":"\s*,\s*)?:?\s*"((?:[^"\\]|\\.)*)"')


def _loose_blocks(text: str) -> list[dict]:
    """Free-tier models sometimes emit JSON-ish text whose structure is broken (keys turned into separate
    strings, "heading",":","..."), so nothing nests under "blocks". Their sentence objects are usually
    intact: find every {"text": ...} object wherever it sits, and give it the nearest heading before it."""
    found: list[tuple[int, str, dict]] = []
    for m in _SENT_START.finditer(text):
        try:
            obj, _ = _DEC.raw_decode(text, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("text"), str):
            heads = list(_HEADING_TOKEN.finditer(text[:m.start()]))
            try:
                heading = json.loads(f'"{heads[-1].group(1)}"') if heads else ""
            except ValueError:
                heading = ""
            found.append((m.start(), heading, obj))
    blocks: list[dict] = []
    for _, heading, obj in found:
        if blocks and blocks[-1]["heading"] == heading:
            blocks[-1]["sentences"].append(obj)
        else:
            blocks.append({"heading": heading, "sentences": [obj]})
    return blocks


def _n_sentences(doc: dict | None) -> int:
    return sum(len(b.get("sentences") or []) for b in (doc or {}).get("blocks", []))


def parse_answer(raw: str, cut_off: bool = False) -> tuple[dict | None, bool]:
    """(doc, complete). complete=False when the object was cut off or broken and
    only its complete sentences were kept; doc None when nothing usable."""
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    try:
        doc = _norm_doc(llm.parse_json(text))
        if doc is not None:
            # the lenient JSON parser can accept the first well-formed object of a broken reply: if the text
            # holds more sentence objects than the parsed document, recover them
            if len(_SENT_START.findall(text)) > _n_sentences(doc):
                loose = _norm_doc({"blocks": _loose_blocks(text), "gaps": doc.get("gaps", []),
                                   "follow_up_questions": doc.get("follow_up_questions", [])})
                if loose and _n_sentences(loose) > _n_sentences(doc):
                    return loose, False
            return doc, not cut_off
    except (ValueError, json.JSONDecodeError):
        pass
    doc = _norm_doc(_salvage(text))
    loose = _norm_doc({**(_salvage(text) or {}), "blocks": _loose_blocks(text)}) if _SENT_START.search(text) else None
    if loose and loose["blocks"] and _n_sentences(loose) > _n_sentences(doc):
        doc = loose  # the structure was broken but more intact sentences are recoverable
    return (doc, False) if doc and doc["blocks"] else (None, False)


# ------------------------------------------------- incremental (streaming) parsing
_STR_SPECIAL = re.compile(r'["\\]')
_STRUCT = re.compile(r'["{}\[\]:,]')


class _Frame:
    __slots__ = ("kind", "key", "cur", "awaiting", "start", "heading")

    def __init__(self, kind: str, key: str | None, start: int):
        self.kind, self.key, self.start = kind, key, start  # kind "{" | "["; key = the key in the parent that led here
        self.cur: str | None = None   # key whose value is being read (objects)
        self.awaiting = False         # after ':' until the value is consumed
        self.heading = ""             # block objects only


class IncrementalDoc:
    """Truly incremental reader of the growing answer JSON: feed() consumes only the NEW characters (one
    pass over the stream in total, no re-parsing) and returns each sentence object the moment its closing
    brace arrives, as (block_index, heading, raw sentence dict). String/escape state survives across feed()
    calls, so chunk boundaries may fall inside a key, a string, a \\uXXXX escape or between surrogates.
    Only sentences at blocks[].sentences[] are reported; anything else (gaps, questions, prose) is left to
    the authoritative parse at the end of the stream."""

    def __init__(self):
        self.text = ""
        self._i = 0
        self._in_str = False
        self._esc = False
        self._str_start = 0
        self._last_str: tuple[int, int] | None = None  # span (incl. quotes) of the last closed string
        self._stack: list[_Frame] = []
        self._blocks = -1
        self.closed = False  # the root object closed

    def _decode(self, span: tuple[int, int]) -> str:
        try:
            v = json.loads(self.text[span[0]:span[1]])
            return v if isinstance(v, str) else ""
        except ValueError:
            return ""

    def feed(self, delta: str) -> list[tuple[int, str, dict]]:
        out: list[tuple[int, str, dict]] = []
        if not delta or self.closed:
            return out
        self.text += delta
        t, n, i = self.text, len(self.text), self._i
        stack = self._stack
        while i < n:
            if self._in_str:
                if self._esc:  # previous chunk ended on a backslash: this char is escaped
                    self._esc = False
                    i += 1
                    continue
                m = _STR_SPECIAL.search(t, i)
                if not m:
                    i = n
                    break
                if m.group() == "\\":
                    if m.start() + 1 >= n:
                        self._esc = True
                        i = n
                        break
                    i = m.start() + 2
                    continue
                self._in_str = False
                self._last_str = (self._str_start, m.start() + 1)
                i = m.start() + 1
                top = stack[-1] if stack else None
                if top is not None and top.awaiting:  # a string VALUE
                    top.awaiting = False
                    if top.kind == "{" and top.cur == "heading" and len(stack) == 3:
                        top.heading = self._decode(self._last_str).strip()
                continue
            m = _STRUCT.search(t, i)
            if not m:
                i = n
                break
            c, at = m.group(), m.start()
            i = at + 1
            if c == '"':
                self._in_str, self._str_start = True, at
            elif c == ":":
                top = stack[-1] if stack else None
                if top is not None and top.kind == "{" and self._last_str:
                    top.cur, top.awaiting = self._decode(self._last_str), True
            elif c == ",":
                if stack:
                    stack[-1].awaiting = False
            elif c in "{[":
                top = stack[-1] if stack else None
                if top is None:
                    key = None
                elif top.kind == "{":
                    key = top.cur if top.awaiting else None
                else:
                    key = top.key
                if top is not None:
                    top.awaiting = False
                stack.append(_Frame(c, key, at))
                if len(stack) == 3 and c == "{" and stack[1].key == "blocks" and stack[1].kind == "[":
                    self._blocks += 1
            else:  # "}" or "]"
                if not stack:
                    continue
                fr = stack.pop()
                if fr.kind == "{" and len(stack) == 4 and stack[1].key == "blocks" and stack[3].key == "sentences" \
                        and stack[3].kind == "[" and stack[2].kind == "{":
                    try:
                        obj = json.loads(t[fr.start:at + 1])
                    except ValueError:
                        obj = None
                    if isinstance(obj, dict):
                        out.append((self._blocks, stack[2].heading, obj))
                if not stack:
                    self.closed = True
                    break
        self._i = i
        return out


class StreamVerifier:
    """Verify each sentence the moment it is complete and produce the markdown pieces `render` would produce
    for it. Removed sentences are counted and never returned. Nothing is released until `min_rules`
    rule/deadline/penalty sentences have verified (so a document that would fall back to the extractive answer
    is, in practice, never shown); the held pieces are then released together and later ones immediately."""

    def __init__(self, sources: list[dict], guidance: str = "", min_rules: int = MIN_VERIFIED_RULES,
                 ctx: CheckContext | None = None):
        self.sources = sources
        self.ctx = ctx if ctx is not None else CheckContext()
        if not self.ctx.guidance:
            self.ctx = CheckContext(question=self.ctx.question, topic_terms=self.ctx.topic_terms,
                                    law_terms=self.ctx.law_terms, guidance=guidance)
        self._last_block: int | None = None
        self._prev_removed = False
        self._pos = 0
        self.views = verifier.make_views(sources)
        self.polisher = verifier.Polisher(self.views)
        self.terms = verifier.guidance_term_set(guidance)
        self.min_rules = min_rules
        self.parser = IncrementalDoc()
        self.removed = 0
        self.verified = 0
        self.rules = 0
        self.released = False
        self._held: list[str] = []
        self._open_block: int | None = None
        self._open_heading = ""
        self._any = False
        self.first_verified_at: float | None = None  # perf_counter of the first surviving sentence (may be held)

    def _piece(self, block: int, heading: str, k: dict) -> str:
        line, empathy = _line(k), k.get("kind") == "empathy"
        if block != self._open_block and heading and heading == self._open_heading and self._any:
            self._open_block = block   # same heading as the block just shown: its bullets continue that block
            return "\n" + (line if empathy else f"- {line}")
        if block != self._open_block:
            self._open_block, self._open_heading = block, heading
            sep = "\n\n" if self._any else ""
            return sep + (f"**{heading}**\n{line if empathy else '- ' + line}" if heading else line)
        if self._open_heading:
            return "\n" + (line if empathy else f"- {line}")
        return " " + line

    def feed(self, delta: str) -> str:
        """New model text in; the text now safe to show (possibly ""), out."""
        out: list[str] = []
        for block, heading, raw in self.parser.feed(delta):
            norm = _norm_sentence(raw)
            if norm is None:
                continue
            if block != self._last_block:
                self._last_block, self._prev_removed, self._pos = block, False, 0
            k, reason = verifier.verify_sentence(norm, self.sources, self.views, self.terms, self.ctx,
                                                 dangling=self._prev_removed, first_in_block=self._pos == 0)
            self._pos += 1
            if k is not None and not reason:
                reason = self.polisher.admit(k)
            self._prev_removed = bool(reason)
            if reason:
                self.removed += 1
                continue
            if k is None:
                continue
            if self.first_verified_at is None:
                self.first_verified_at = time.perf_counter()
            self.verified += 1
            if k["cites"] and k["kind"] in verifier.STRICT_KINDS:
                self.rules += 1
            self._held.append(self._piece(block, heading, k))
            self._any = True
            if not self.released and self.rules >= self.min_rules:
                self.released = True
            if self.released:
                out.extend(self._held)
                self._held = []
        return "".join(out)


# ---------------------------------------------------------------- rendering
_TRAIL_PUNCT = re.compile(r"([.।!?]+)\s*$")


def _line(s: dict) -> str:
    text = claim_checks.clean_ocr_text(s["text"].strip())  # OCR typos copied from a scanned source are not shown
    marks = "".join(f"[{n}]" for n in claim_checks.dedupe_marks([c["n"] for c in s.get("cites") or []]))
    if not marks:
        return text
    m = _TRAIL_PUNCT.search(text)
    return f"{text[:m.start()]} {marks}{m.group(1)}" if m else f"{text} {marks}"


def render(doc: dict, lang: str, disclaimer: str = "") -> str:
    """Markdown in the shape the UI already shows: bold headings, bullets, inline [n]."""
    parts = []
    for b in doc.get("blocks") or []:
        lines = [(_line(s), s.get("kind")) for s in b["sentences"]]
        if b.get("heading"):
            parts.append(f"**{b['heading']}**\n" + "\n".join(
                t if k == "empathy" else f"- {t}" for t, k in lines))
        else:
            parts.append(" ".join(t for t, _ in lines))
    key = "ne" if lang == "ne" else "en"
    if doc.get("gaps"):
        parts.append(f"**{HEADINGS['gaps'][key]}**\n" + "\n".join(f"- {g}" for g in doc["gaps"]))
    if doc.get("follow_up_questions"):
        parts.append(f"**{HEADINGS['ask'][key]}**\n" + "\n".join(f"- {q}" for q in doc["follow_up_questions"]))
    if disclaimer:
        parts.append(disclaimer)
    return "\n\n".join(parts)


def _passage_text(src: dict) -> str:
    return " ".join(str(src.get(k) or "") for k in ("text_ne", "text_en", "title_ne"))


def _clean_side_text(doc: dict, lang: str = "", sources: list[dict] | None = None,
                     cited: set[int] | None = None) -> tuple[dict, dict[str, int]]:
    """Gaps and follow-up questions carry no legal claim: keep them short and number-free. With `sources`
    (V3.2) a gap that says the sources do not cover X is dropped when a passage the answer cites - or any
    retrieved passage - contains X's terms, and a gap not in the answer language is dropped.
    (doc, {reason: dropped count})."""
    gaps = [g for g in doc.get("gaps", []) if len(g) <= 240 and not re.search(r"[0-9०-९]", g)]
    dropped: dict[str, int] = {}
    if lang and sources is not None:
        cited_texts = [_passage_text(sources[i]) for i in sorted(cited or ()) if 0 <= i < len(sources)]
        gaps, why = claim_checks.filter_gaps(gaps, lang, cited_texts, [_passage_text(x) for x in sources])
        for _, reason in why:
            dropped[reason] = dropped.get(reason, 0) + 1
    asks = [q for q in doc.get("follow_up_questions", [])
            if len(q) <= 140 and "?" in q and not verifier.looks_rule_like(q)][:3]
    return {**doc, "gaps": gaps[:3], "follow_up_questions": asks}, dropped


def chunks(text: str, size: int = 40):
    """Word-boundary chunks of ~`size` chars (newlines kept) for simulated streaming."""
    buf = ""
    for piece in re.findall(r"\S+\s*|\s+", text):
        buf += piece
        if len(buf) >= size or "\n" in piece:
            yield buf
            buf = ""
    if buf:
        yield buf


# --------------------------------------------------------------- entailment
ENTAIL_STATEMENT_CHARS = 300   # compact payload: the statement and its quote are cut here (the verdict needs the
ENTAIL_QUOTE_CHARS = 320       # first clauses; the deterministic checks already proved the quote is real)
ENTAIL_QUESTION_CHARS = 300


def entail_payload(doc: dict, question: str = "") -> tuple[str, list[tuple[int, int]]]:
    """(compact JSON for the entailment call, [(block, sentence) per item]). One item per cited sentence:
    the statement and the quote(s) it rests on, plus the user's situation once."""
    items, index = [], []
    for bi, b in enumerate(doc["blocks"]):
        for si, s in enumerate(b["sentences"]):
            if s.get("cites"):
                index.append((bi, si))
                items.append({"s": s["text"][:ENTAIL_STATEMENT_CHARS],
                              "q": " … ".join(c["quote"] for c in s["cites"])[:ENTAIL_QUOTE_CHARS]})
    payload = {"situation": " ".join((question or "").split())[:ENTAIL_QUESTION_CHARS], "items": items}
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")), index


_VERDICT = {"y": "yes", "yes": "yes", "n": "no", "no": "no", "p": "partial", "partial": "partial"}


def parse_verdicts(raw: str, n: int) -> list[str]:
    """One verdict (yes/no/partial) per item from {"v":["y",...]} or the older {"results":[{"id","verdict"}]};
    anything missing or unreadable is "yes" (fail open)."""
    data = llm.parse_json(raw)
    out = ["yes"] * n
    if isinstance(data.get("v"), list):
        for i, v in enumerate(data["v"][:n]):
            out[i] = _VERDICT.get(str(v).strip().lower(), "yes")
    for r in data.get("results") or []:
        try:
            i = int(r["id"])
        except (KeyError, TypeError, ValueError):
            continue
        if 0 <= i < n:
            out[i] = _VERDICT.get(str(r.get("verdict")).strip().lower(), "yes")
    return out


def entailment_filter(doc: dict, call=None, question: str = "", drop_partial: bool = False) -> tuple[dict, int, bool]:
    """ONE cheap call over every cited sentence: drop those whose quote does NOT support them for this user's
    situation ("no"; also "partial" when drop_partial). (doc, removed_count, ran). Fails open: a provider error
    keeps the deterministic result. `call(system, user, **kw) -> str` is injectable."""
    call = call or llm.complete
    payload, index = entail_payload(doc, question)
    if not index:
        return doc, 0, False
    try:
        raw = call(ENTAIL_SYSTEM, payload, fast=True, json_mode=True, max_tokens=40 + 8 * len(index), temperature=0.0)
        verdicts = parse_verdicts(raw, len(index))
    except Exception as e:  # noqa: BLE001
        log.warning("entailment check skipped: %s", str(e)[:160])
        return doc, 0, False
    bad = {"no", "partial"} if drop_partial else {"no"}
    drop = {index[i] for i, v in enumerate(verdicts) if v in bad}
    blocks = []
    for bi, b in enumerate(doc["blocks"]):
        kept = [s for si, s in enumerate(b["sentences"]) if (bi, si) not in drop]
        if kept:
            blocks.append({**b, "sentences": kept})
    return {**doc, "blocks": blocks}, len(drop), True


def _recount(doc: dict, sources: list[dict], report: dict, removed_extra: int, reason: str) -> dict:
    cited = {c["n"] - 1 for b in doc["blocks"] for s in b["sentences"] for c in s["cites"]}
    claims = sum(1 for b in doc["blocks"] for s in b["sentences"] if s["cites"])
    rem = dict(report["removed"])
    rem["count"] += removed_extra
    if removed_extra:
        rem["by_reason"] = {**rem["by_reason"], reason: removed_extra}
        rem["reasons"] = sorted(rem["by_reason"], key=lambda r: -rem["by_reason"][r])
    return {**report, "claims": claims, "supported": claims, "removed": rem,
            "cited_laws": sum(sources[i].get("category") != "precedent" for i in cited),
            "cited_precedents": sum(sources[i].get("category") == "precedent" for i in cited)}


# ------------------------------------------------------------ orchestration
def verified_rule_count(doc: dict) -> int:
    return sum(1 for b in doc["blocks"] for s in b["sentences"]
               if s["cites"] and s["kind"] in verifier.STRICT_KINDS)


def _log_fallback(why: str, raw: str, doc: dict | None, report: dict, cut_off: bool, repaired: bool) -> None:
    """Why an answer fell back to the extractive provisions: structure counts only (no user text). Set
    DEBUG_ANSWERS=1 to also log the start of the raw model reply while diagnosing a provider."""
    sents = [s for b in (doc or {}).get("blocks", []) for s in b["sentences"]]
    log.info("answer fallback: why=%s raw_chars=%d cut_off=%s repaired=%s parsed_sentences=%d cited=%d removed=%s",
             why, len(raw or ""), cut_off, repaired, len(sents), sum(1 for s in sents if s["cites"]),
             (report.get("removed") or {}).get("by_reason"))
    if os.getenv("DEBUG_ANSWERS") == "1":
        log.info("answer fallback raw: %s", (raw or "")[:2000].replace("\n", " "))


def build(raw: str, sources: list[dict], lang: str, *, guidance: str = "", disclaimer: str = "",
          cut_off: bool = False, repair=None, entail=None, ctx: CheckContext | None = None) -> dict:
    """The model's raw reply -> {"answer": markdown | None, "verification": report, "doc": verified doc,
    "truncated": bool, "repaired": bool}. answer None means: fall back to the extractive provisions.
    `repair(raw) -> str` retries broken JSON once; `entail(doc) -> (doc, removed, ran)` is the optional LLM pass."""
    doc, complete = parse_answer(raw, cut_off)
    repaired = False
    if doc is None and repair is not None:
        try:
            doc, complete = parse_answer(repair(raw))
            repaired = True
        except Exception as e:  # noqa: BLE001
            log.warning("JSON repair failed: %s", str(e)[:160])
    empty = {"claims": 0, "supported": 0, "unverified": [], "cited_laws": 0, "cited_precedents": 0,
             "removed": {"count": 0, "reasons": ["unparseable"], "by_reason": {"unparseable": 1}, "blocks_dropped": 0},
             "mode": "extractive_fallback", "truncated": not complete}
    if doc is None:
        _log_fallback("unparseable", raw, None, empty, cut_off, repaired)
        return {"answer": None, "verification": empty, "doc": None, "truncated": True, "repaired": repaired}
    good, report = verifier.verify_structured(doc, sources, guidance, ctx)
    if entail is not None and verified_rule_count(good) >= 1:
        good, dropped, ran = entail(good)
        if dropped:
            report = _recount(good, sources, report, dropped, "not_entailed")
        report["entailment"] = "ran" if ran else "skipped"
    cited = {c["n"] - 1 for b in good["blocks"] for s in b["sentences"] for c in s["cites"]}
    good, gaps_dropped = _clean_side_text(
        {**good, "gaps": doc.get("gaps", []), "follow_up_questions": doc.get("follow_up_questions", [])},
        lang, sources, cited)
    # V3.3: an asked quantity (कति / how many / what penalty) that no kept sentence answers is said plainly
    if ctx is not None and claim_checks.asks_quantity(ctx.question) and good["gaps"] is not None:
        texts = [s["text"] for b in good["blocks"] for s in b["sentences"] if s["cites"]]
        if not claim_checks.has_figure(texts):
            gap = claim_checks.QUANTITY_GAP["ne" if lang == "ne" else "en"]
            good = {**good, "gaps": [gap] + [g for g in good["gaps"] if g != gap][:2]}
            report["quantity_gap"] = True
    report = {**report, "mode": "structured", "truncated": not complete}
    if gaps_dropped:
        report["gaps_removed"] = gaps_dropped
    if verified_rule_count(good) < MIN_VERIFIED_RULES:
        report["mode"] = "extractive_fallback"
        _log_fallback("too_few_verified", raw, doc, report, cut_off, repaired)
        return {"answer": None, "verification": report, "doc": good, "truncated": not complete, "repaired": repaired}
    # what was rendered and the passage span each sentence rests on (public statute text, no user text)
    views = verifier.make_views(sources)

    def locate(c):  # the sub-section that actually holds the quote (V3.3), e.g. "(2)"
        sub = claim_checks.quote_subsection(verifier._qtokens(c["quote"]), views[c["n"] - 1].layout)
        return {"sub_section": sub} if sub else {}

    report["evidence"] = [{"text": claim_checks.clean_ocr_text(s["text"]), "kind": s["kind"],
                           "cites": [{**c, "quote": claim_checks.clean_ocr_text(c["quote"]), **locate(c)} for c in s["cites"]]}
                          for b in good["blocks"] for s in b["sentences"] if s["cites"]]
    return {"answer": render(good, lang, disclaimer), "verification": report, "doc": good,
            "truncated": not complete, "repaired": repaired}
