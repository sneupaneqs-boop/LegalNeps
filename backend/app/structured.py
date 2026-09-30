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
import re
import time

from . import llm, verifier

log = logging.getLogger(__name__)

MIN_VERIFIED_RULES = 2  # fewer verified rule/deadline/penalty sentences than this -> extractive fallback

STRUCTURED_ANSWER_SYSTEM = """You are Kanooni Sathi ("Legal Friend"), a warm, precise bilingual \
(English/Nepali) legal-information assistant for Nepal. Reply with ONE JSON object and nothing else. \
Code checks every sentence against the numbered passages in "Official sources" and DELETES any sentence \
whose quote is not really in the passage it cites, so write only what a passage lets you quote.

Schema:
{"blocks":[{"heading":"...","sentences":[{"text":"...","kind":"rule|deadline|penalty|procedure|advice|empathy",
"cites":[{"n":3,"quote":"..."}]}]}],
"gaps":["..."],"follow_up_questions":["..."]}

Rules:
- Sentence text is plain prose: no [n] markers, no markdown. Blocks in order: one with heading "" holding a \
single "empathy" sentence that shows you understood the real concern; then the direct answer, key rules, \
next steps, and a Supreme Court precedent if one is provided. Headings are short, in the reply language.
- kind "rule"/"deadline"/"penalty" = any statement of what the law says, requires, allows, punishes or \
how long it takes. EVERY such sentence needs "cites": one or more {"n": <passage number>, "quote": <a span \
copied CHARACTER FOR CHARACTER from that passage, 6-40 words>}. Copy from the Nepali text, or from the \
"[English translation]" when the passage has one and you answer in English. Never paraphrase, translate or \
join two spans in a quote. One sentence, one idea; cite the passage that says it.
- Every number (days, months, years, rupees, percentages) and every section number in a sentence must \
appear in its quote. Name the law and section in the sentence; if unsure of a number, leave it out.
- Nepali statute provisions are "दफा", regulation provisions "नियम"; only the Constitution has "धारा".
- Passages marked "verified as governing this situation" are the core law: build on them first. "OLDER \
LAW" passages only as history and say so in the sentence ("older law"); never state their rule as current. \
Never present a "bill", "repealed" or "lapsed" passage as law. A passage with status "ordinance" is \
temporary: say "ordinance" in the sentence and that it lapses unless Parliament replaces it.
- A statement about a Supreme Court decision must cite a Supreme Court precedent passage.
- The "Curated action plan" is guidance, not a source: use it only for sentences of kind "procedure" or \
"advice" (where to go, what to gather), with NO cites, NO numbers and no legal-rule wording (no must/shall/\
within/penalty/deadline). Everything else needs a quote.
- Do not state any remedy, offence, office or procedure that no passage mentions. If a passage does not \
cover something the person needs, put it in "gaps" as "The sources retrieved do not cover X" - never \
"the law does not say X". At most 3 short gaps; "follow_up_questions": at most 3 short questions that \
would sharpen the answer (no numbers or legal claims in them).
- Passages may contain OCR glitches: quote exactly what is printed anyway. Reply entirely in the requested \
language (Nepali in natural Devanagari). Keep the whole object under about 900 words.

Example 1 (English; passage [1] is Labour Act, 2074, section 162, English translation: "A worker \
aggrieved by an act contrary to this Act may file a complaint within six months from the date of the act."):
{"blocks":[{"heading":"","sentences":[{"text":"I understand your salary has not been paid and how stressful \
that is.","kind":"empathy","cites":[]}]},
{"heading":"Direct answer","sentences":[{"text":"Under the Labour Act, 2074, Section 162, you can file a \
complaint within 6 months of the act.","kind":"deadline","cites":[{"n":1,"quote":"may file a complaint \
within six months from the date of the act"}]}]},
{"heading":"Next steps","sentences":[{"text":"Gather your appointment letter and pay slips before you \
complain.","kind":"advice","cites":[]}]}],
"gaps":["The sources retrieved do not cover which office can order the unpaid wages to be paid."],
"follow_up_questions":["When was your last salary paid?"]}
(The claim "the Labour Office can order payment" was NOT written as a rule because no passage says it - it went \
into gaps.)

Example 2 (Nepali; passage [1] is मुलुकी देवानी संहिता, २०७४, दफा ३८६: "कुनै व्यक्तिले घर बहालमा दिँदा देहायका \
कुराहरू खुलाई बहालमा लिने व्यक्तिसँग लिखित सम्झौता गर्नु पर्नेछ"):
{"blocks":[{"heading":"","sentences":[{"text":"धरौटी फिर्ता नभएको कुराले तपाईंलाई चिन्ता भएको मैले बुझें।",\
"kind":"empathy","cites":[]}]},
{"heading":"मुख्य नियम","sentences":[{"text":"मुलुकी देवानी संहिता, २०७४ को दफा ३८६ अनुसार घर बहालमा दिँदा \
बहालमा लिने व्यक्तिसँग लिखित सम्झौता गर्नु पर्छ।","kind":"rule","cites":[{"n":1,"quote":"घर बहालमा दिँदा \
देहायका कुराहरू खुलाई बहालमा लिने व्यक्तिसँग लिखित सम्झौता गर्नु पर्नेछ"}]}]}],
"gaps":["मैले पाएका स्रोतहरूले धरौटी फिर्ता गर्ने म्याद समेटेका छैनन्।"],"follow_up_questions":[]}"""

REPAIR_SYSTEM = ("You repair broken JSON. The user message is a JSON object of a legal answer that failed to parse "
                 "(maybe cut off). Return ONLY the repaired, valid JSON object, keeping every complete sentence exactly "
                 "as written and dropping any half-written one. Do not add content.")

ENTAIL_SYSTEM = ("You check legal statements against quoted passage text. For each item decide whether the QUOTE "
                 "supports the STATEMENT: \"yes\" (the quote states or directly entails it), \"partial\" (the quote "
                 "supports only part of it) or \"no\" (the quote does not support it, contradicts it, or is about a "
                 "different rule). Judge only from the quote. Return JSON: "
                 "{\"results\":[{\"id\":0,\"verdict\":\"yes|no|partial\"}, ...]} with one entry per item.")

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


def parse_answer(raw: str, cut_off: bool = False) -> tuple[dict | None, bool]:
    """(doc, complete). complete=False when the object was cut off or broken and
    only its complete sentences were kept; doc None when nothing usable."""
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    try:
        doc = _norm_doc(llm.parse_json(text))
        if doc is not None:
            return doc, not cut_off
    except (ValueError, json.JSONDecodeError):
        pass
    doc = _norm_doc(_salvage(text))
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

    def __init__(self, sources: list[dict], guidance: str = "", min_rules: int = MIN_VERIFIED_RULES):
        self.sources = sources
        self.views = verifier.make_views(sources)
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
            k, reason = verifier.verify_sentence(norm, self.sources, self.views, self.terms)
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
    text = s["text"].strip()
    marks = "".join(f"[{c['n']}]" for c in s.get("cites") or [])
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


def _clean_side_text(doc: dict) -> dict:
    """Gaps and follow-up questions carry no legal claim: keep them short and number-free."""
    gaps = [g for g in doc.get("gaps", []) if len(g) <= 240 and not re.search(r"[0-9०-९]", g)][:3]
    asks = [q for q in doc.get("follow_up_questions", [])
            if len(q) <= 140 and "?" in q and not verifier.looks_rule_like(q)][:3]
    return {**doc, "gaps": gaps, "follow_up_questions": asks}


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
def entailment_filter(doc: dict, call=None) -> tuple[dict, int, bool]:
    """One cheap call over every cited sentence: drop those whose quote does NOT
    support them. (doc, removed_count, ran). Fails open: a provider error keeps
    the deterministic result. `call(system, user, **kw) -> str` is injectable."""
    call = call or llm.complete
    items, index = [], []
    for bi, b in enumerate(doc["blocks"]):
        for si, s in enumerate(b["sentences"]):
            if s.get("cites"):
                index.append((bi, si))
                items.append({"id": len(items), "statement": s["text"],
                              "quote": " … ".join(c["quote"] for c in s["cites"])})
    if not items:
        return doc, 0, False
    try:
        raw = call(ENTAIL_SYSTEM, json.dumps({"items": items}, ensure_ascii=False), fast=True, json_mode=True,
                   max_tokens=60 + 25 * len(items), temperature=0.0)
        results = llm.parse_json(raw).get("results") or []
        no = {int(r["id"]) for r in results if isinstance(r, dict) and str(r.get("verdict")).lower() == "no"}
    except Exception as e:  # noqa: BLE001
        log.warning("entailment check skipped: %s", str(e)[:160])
        return doc, 0, False
    drop = {index[i] for i in no if 0 <= i < len(index)}
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


def build(raw: str, sources: list[dict], lang: str, *, guidance: str = "", disclaimer: str = "",
          cut_off: bool = False, repair=None, entail=None) -> dict:
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
        return {"answer": None, "verification": empty, "doc": None, "truncated": True, "repaired": repaired}
    good, report = verifier.verify_structured(doc, sources, guidance)
    if entail is not None and verified_rule_count(good) >= 1:
        good, dropped, ran = entail(good)
        if dropped:
            report = _recount(good, sources, report, dropped, "not_entailed")
        report["entailment"] = "ran" if ran else "skipped"
    good = _clean_side_text({**good, "gaps": doc.get("gaps", []), "follow_up_questions": doc.get("follow_up_questions", [])})
    report = {**report, "mode": "structured", "truncated": not complete}
    if verified_rule_count(good) < MIN_VERIFIED_RULES:
        report["mode"] = "extractive_fallback"
        return {"answer": None, "verification": report, "doc": good, "truncated": not complete, "repaired": repaired}
    # what was rendered and the passage span each sentence rests on (public statute text, no user text)
    report["evidence"] = [{"text": s["text"], "kind": s["kind"], "cites": s["cites"]}
                          for b in good["blocks"] for s in b["sentences"] if s["cites"]]
    return {"answer": render(good, lang, disclaimer), "verification": report, "doc": good,
            "truncated": not complete, "repaired": repaired}
