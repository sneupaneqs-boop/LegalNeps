"""
Turns the PDFs downloaded by scrape_lawcommission.py into clean, section-level
text chunks, with no LLM involved for the bulk of documents:

- Unicode (Kalimati/Kokila/Mangal...) spans are taken as-is.
- Legacy-font spans (Preeti, Kantipur, PCS Nepali, Sagarmatha, Fontasy
  Himali) are converted to Unicode with npttf2utf, span by span, using the
  font name PyMuPDF reports - so mixed documents convert correctly.
- Pages with no extractable text are flagged `needs_ocr` for the Gemini
  vision pass (ocr_gemini.py).

Acts/rules are split on their दफा/नियम headings ("१. संक्षिप्त नाम र
प्रारम्भः"), long sections are windowed; other documents (reports,
treaties) are split into ~1,200-character paragraph windows.

    python3 backend/scripts/extract_laws.py            # incremental
    python3 backend/scripts/extract_laws.py --force    # re-extract all

Output: sources/processed/law_docs.jsonl (one record per document with its
chunks). Cached by the PDF's sha256, so re-runs only process new files.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = os.path.join(ROOT, "sources", "lawcommission", "manifest.jsonl")
OUT_DIR = os.path.join(ROOT, "sources", "processed")
OUT_PATH = os.path.join(OUT_DIR, "law_docs.jsonl")

LEGACY_FONTS = [
    ("preeti", "Preeti"),
    ("kantipur", "Kantipur"),
    ("pcs", "PCS NEPALI"),
    ("sagarmatha", "Sagarmatha"),
    ("fontasy", "FONTASY_HIMALI_TT"),
]

DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
# Amended sections are flagged with a symbol-font glyph (private use area) or
# an asterisk-like mark before the number: "\uf0b9११. मृत्युकालीन घोषणाः".
_MARKS = "\ue000-\uf8ff*✲✳✱✻⊕†‡¤§"
SECTION_RE = re.compile(
    r"(?m)^[ \t" + _MARKS + r"]*(?P<num>[०-९0-9]{1,3}(?:\.?[क-ह])?)[.\)]\s{0,4}(?P<head>[^\n:ः।]{2,140}?)\s*[:ः]"
)
# Looser shapes seen in the gazette PDFs - heading wrapped onto a second line,
# or the dot after the number dropped ("३७ हदम्याद लागू हुनेः"). Too permissive
# on their own, so they only count when they fill an exact gap in the numbering.
# (a lookahead, so candidates can overlap and one can't swallow the next)
LOOSE_SECTION_RE = re.compile(
    r"(?m)^(?=[ \t" + _MARKS + r"]*(?P<num>[०-९0-9]{1,3})(?:[.\)]\s{0,4}|\s{1,3})"
    r"(?P<head>[^\n:ः।(\s][^\n:ः।]{1,140}?(?:\n[^\n:ः।]{1,100}?){0,2})\s*[:ः])"
)


def _section_no(num: str) -> int | None:
    m = re.match(r"\d+", num.translate(DEV_DIGITS))
    return int(m.group(0)) if m else None


def find_sections(full: str) -> list[re.Match]:
    """Section headings: every strict match, plus loose matches that supply
    exactly the missing number between two strict neighbours."""
    strict = list(SECTION_RE.finditer(full))
    taken = {m.start() for m in strict}
    extra = []
    for m in LOOSE_SECTION_RE.finditer(full):
        if m.start() in taken:
            continue
        n = _section_no(m.group("num"))
        prev = next((s for s in reversed(strict) if s.start() < m.start()), None)
        nxt = next((s for s in strict if s.start() > m.start()), None)
        if n is None or prev is None:
            continue
        pn = _section_no(prev.group("num"))
        nn = _section_no(nxt.group("num")) if nxt else None
        if pn is not None and n == pn + 1 and (nn is None or nn > n):
            extra.append(m)
    return sorted(strict + extra, key=lambda m: m.start())
CHAPTER_RE = re.compile(r"(?m)^[ \t]*(परिच्छेद|भाग)\s*[-–—]?\s*([०-९0-9]{1,3})")

_mapper = None


def _get_mapper():
    global _mapper
    if _mapper is None:
        import npttf2utf
        from npttf2utf.base.fontmapper import FontMapper

        _mapper = FontMapper(os.path.join(os.path.dirname(npttf2utf.__file__), "map.json"))
    return _mapper


COMMON_EN = set("""the of and to in is for on by with as at be or an are this that from it not
act acts rule rules regulation section sub clause chapter schedule article part name date no number
office government nepal ministry department court district supreme high law laws legal order notice
form application applicant signature address fee fees amount rs total year years month day details
and/or shall may must will per any all other such under above below following page table list report
policy plan national international committee board council authority member members chairman
secretary officer officers public private company bank tax income value added customs social
health education development management service services system information technology data
case registration letter reference autopsy police examination sheets floor plans elevations
drawings section cross longitudinal first middle last identity citizen citizenship passport
designation country nationality english nepali b.s. a.d.""".split())
EN_FUNCTION_WORDS = {"the", "of", "and", "to", "in", "for", "on", "with", "by", "is", "be", "or", "as",
                     "at", "from", "no", "a", "an", "are", "this", "that", "shall", "which", "name", "date"}
_PREETI_MARKS = set("]{}|;'/\\«»@)*!&^%$#+=[<>?`~\"")


def looks_preeti(text: str) -> bool:
    """Legacy-font text whose font isn't called Preeti (subset names like
    'F1', 'Arial' fallbacks): Latin letters, few real English words, and the
    punctuation Preeti uses for matras and digits (] f { ; / @ ) ...)."""
    letters = sum(c.isalpha() for c in text)
    if letters < 3 or re.search(r"[\u0900-\u097F]", text):
        return False
    words = re.findall(r"[A-Za-z]+", text)
    if words and sum(w.lower() in COMMON_EN for w in words) / len(words) > 0.2:
        return False
    marks = sum(c in _PREETI_MARKS for c in text)
    return marks / max(1, len(text.strip())) > 0.05


def legacy_map_name(font: str) -> str | None:
    f = font.lower().replace(" ", "").replace("_", "")
    for key, name in LEGACY_FONTS:
        if key in f:
            return name
    return None


def convert_legacy(text: str, map_name: str) -> str:
    try:
        return _get_mapper().map_to_unicode(
            text, from_font=map_name, unescape_html_input=False, escape_html_output=False
        )
    except Exception:  # noqa: BLE001
        return text


GLYPH_REF_PATH = os.path.join(OUT_DIR, "glyph_reference.json")
_glyph_ref: dict | None = None
_table_cache: dict[str, dict | None] = {}


def _font_family(basefont: str) -> str:
    return basefont.split("+", 1)[-1]


def load_glyph_reference() -> dict:
    global _glyph_ref
    if _glyph_ref is None:
        _glyph_ref = json.load(open(GLYPH_REF_PATH, encoding="utf-8")) if os.path.exists(GLYPH_REF_PATH) \
            else {"hash_text": {}, "reph_hashes": []}
    return _glyph_ref


def _font_bytes(doc, xref) -> bytes | None:
    try:
        return doc.extract_font(xref)[3] or None
    except Exception:  # noqa: BLE001
        return None


def font_plan(doc) -> dict[str, tuple]:
    """font name (as texttrace reports it) -> ("legacy", map) | ("glyph", table) | ("plain", None).
    Embedded Unicode Devanagari fonts are decoded from glyph outlines when
    they match the reference design (any build/subset of Kalimati etc.)."""
    import hashlib

    import devanagari_glyphs as G

    ref = load_glyph_reference()
    plan: dict[str, tuple] = {}
    merged: dict[str, dict] = {}
    for pno in range(len(doc)):
        for xref, _ext, _typ, basefont, *_ in doc.get_page_fonts(pno):
            fam = _font_family(basefont)
            m = legacy_map_name(fam)
            if m:
                plan[fam] = ("legacy", m)
                continue
            if not ref["hash_text"]:
                continue
            buf = _font_bytes(doc, xref)
            if not buf:
                continue
            key = hashlib.sha1(buf).hexdigest()
            if key not in _table_cache:
                _table_cache[key] = G.table_for_embedded(buf, ref)
            t = _table_cache[key]
            if t:
                agg = merged.setdefault(fam, {"text": {}, "reph_set": set()})
                agg["text"].update(t["text"])
                agg["reph_set"] |= t["reph_set"]
    for fam, agg in merged.items():
        if fam not in plan:
            plan[fam] = ("glyph", {"text": agg["text"], "reph": sorted(agg["reph_set"]), "reph_set": agg["reph_set"]})
    return plan


FINAL_HALANT_WORDS = {
    "संसद्", "परिषद्", "मन्त्रिपरिषद्", "संवत्", "अर्थात्", "पश्चात्", "विद्वान्", "श्रीमान्",
    "भगवान्", "महान्", "सम्यक्", "किञ्चित्", "जगत्", "विपद्", "सम्पद्", "आपद्", "कदाचित्",
    "यावत्", "तावत्", "सम्राट्", "विराट्", "उपनिषद्", "बुद्धिमान्", "वाक्", "धीमान्", "प्रत्युत्",
    "ईश्वर्", "भवत्", "किमर्थ्", "सत्", "असत्", "तत्", "यत्", "एतत्",
}
_HALANT_SPACE_RE = re.compile(r"(\S*[क-ह]्) (?=[क-ह])")


def _join_zwnj_breaks(text: str) -> str:
    """"हेजिङ्‌ग" typed with ZWNJ is often drawn with a space glyph; rejoin
    such halant+space+consonant breaks unless the left part is a real word
    that ends in a halant (संसद् सचिवालय)."""
    def fix(m):
        word = m.group(1)
        bare = re.sub(r"^[^ऀ-ॿ]+", "", word)
        return word + (" " if bare in FINAL_HALANT_WORDS else "")
    return _HALANT_SPACE_RE.sub(fix, text)


_BOILERPLATE_LINE_RE = re.compile(
    r"(?m)^\s*(?:www\.lawcommission\.gov\.np|[०-९0-9]{1,4}|[-–—]\s*[०-९0-9]{1,4}\s*[-–—])\s*$\n?"
)


def drop_redraw_passes(chars, size: float):
    """Simulated bold is often drawn as 2-4 passes of the same glyphs inside
    one span. Keep only the first pass on each line: a glyph whose origin
    jumps back left on the same baseline starts a redraw pass, and a line
    whose baseline was already emitted in this span is a redraw too."""
    kept = []
    line_y = last_x = None
    seen_lines: list[float] = []
    skipping = False
    for c in chars:
        x, y = c[2]
        if line_y is None or abs(y - line_y) > 0.3 * size:
            line_y, last_x = y, x  # new line
            skipping = any(abs(y - s) <= 0.3 * size for s in seen_lines)
            seen_lines.append(y)
            if not skipping:
                kept.append(c)
            continue
        if skipping:
            continue
        if c[1] >= 0 and x < last_x - 0.35 * size:
            skipping = True
            continue
        last_x = max(last_x, x)
        kept.append(c)
    return kept


def page_text(page, plan: dict) -> tuple[str, int, int]:
    """Returns (text, n_legacy_chars, n_total_chars) for one PDF page."""
    import devanagari_glyphs as G

    lines: list[str] = []
    cur = ""
    last_bbox = None
    recent: list[tuple[str, tuple]] = []
    legacy = total = 0
    zero_width_pending = False
    for sp in page.get_texttrace():
        if sp["type"] not in (0, 3):  # skip stroke/clip passes (fake-bold duplicates)
            continue
        chars = drop_redraw_passes(sp["chars"], sp.get("size") or 10)
        if not chars:
            continue
        raw = "".join(chr(c[0]) for c in chars if c[0] > 0)
        kind, arg = plan.get(sp["font"], plan.get(_font_family(sp["font"]), ("plain", None)))
        if kind == "glyph":
            t = G.decode_span(chars, arg)
            if t is None:
                t = raw
        elif kind == "legacy":
            legacy += len(raw)
            t = convert_legacy(raw, arg)
        elif looks_preeti(raw):
            legacy += len(raw)
            t = convert_legacy(raw, "Preeti")
        else:
            t = raw
        total += len(raw)
        if not t:
            continue
        if not t.strip() and kind == "plain" and cur.endswith("्"):
            # ZWJ/ZWNJ after a halant that Word rendered as a space in a
            # fallback font (e.g. "हेजिङ्‍ग"): not a word break.
            zero_width_pending = True
            continue
        if zero_width_pending:
            zero_width_pending = False
            if re.match(r"[क-ह]", t):
                cur += t
                last_bbox = tuple(sp["bbox"])
                continue
        bbox = tuple(sp["bbox"])
        if any(t == rt and abs(bbox[0] - rb[0]) < 2.5 and abs(bbox[1] - rb[1]) < 2.5 for rt, rb in recent):
            continue  # same text drawn twice at the same spot (simulated bold)
        recent = (recent + [(t, bbox)])[-8:]
        size = sp.get("size") or 10
        if last_bbox is not None:
            ymid, last_ymid = (bbox[1] + bbox[3]) / 2, (last_bbox[1] + last_bbox[3]) / 2
            if abs(ymid - last_ymid) > 0.6 * size:
                lines.append(cur)
                if bbox[1] - last_bbox[3] > 1.2 * size:
                    lines.append("")  # paragraph gap
                cur = ""
            elif bbox[0] - last_bbox[2] > 0.15 * size and cur and not cur.endswith(" ") and not t.startswith(" "):
                cur += " "
        cur += t
        last_bbox = bbox
    lines.append(cur)
    deduped: list[str] = []
    for ln in lines:
        key = ln.strip()
        if len(key) > 15 and key in (d.strip() for d in deduped[-4:]):
            continue  # line redrawn as a separate pass (simulated bold)
        deduped.append(ln)
    text = "\n".join(deduped)
    text = re.sub(r"(?:https?://)?www\.lawcommission\.gov\.np/?", "", text)
    text = _BOILERPLATE_LINE_RE.sub("", text)
    text = re.sub(r"(?:[।.·…_]\s?){4,}", " … ", text)  # table-of-contents leaders
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    text = _join_zwnj_breaks(text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip(), legacy, total


def extract_pdf(path: str) -> dict:
    import pymupdf

    doc = pymupdf.open(path)
    plan = font_plan(doc)
    pages, legacy, total, empty = [], 0, 0, []
    for i, p in enumerate(doc):
        t, lg, tt = page_text(p, plan)
        legacy += lg
        total += tt
        if len(t) < 40:
            empty.append(i + 1)
        pages.append(t)
    joined = "".join(pages)
    dev = len(re.findall(r"[\u0900-\u097F]", joined))
    lat = len(re.findall(r"[A-Za-z]", joined))
    dev_share = dev / max(1, dev + lat)
    latin_words = re.findall(r"[A-Za-z]+", joined)
    en_rate = sum(w.lower() in EN_FUNCTION_WORDS for w in latin_words) / max(1, len(latin_words))
    return {
        "n_pages": len(pages),
        "pages": pages,
        "devanagari_share": round(dev_share, 3),
        "legacy_fraction": round(legacy / total, 3) if total else 0.0,
        "glyph_decoded_fonts": sorted(f for f, (k, _) in plan.items() if k == "glyph"),
        "empty_pages": empty,
        # scanned (no text) or text layer that isn't Nepali at all (garbage encodings)
        "needs_ocr": len(pages) > 0 and (
            len(empty) / len(pages) > 0.5
            or (dev + lat > 500 and dev_share < 0.3 and en_rate < 0.08)  # neither Nepali nor English: garbage encoding
        ),
    }


def build_glyph_reference(records: list[dict], max_docs: int = 600) -> dict:
    """Merge outline->text references from every complete embedded
    Devanagari font (with GSUB) found in the downloaded PDFs."""
    import hashlib

    import pymupdf

    import devanagari_glyphs as G
    from fontTools.ttLib import TTFont
    import io

    ref = {"hash_text": {}, "reph_hashes": set()}
    seen: set[str] = set()
    for r in records[:max_docs]:
        path = os.path.join(ROOT, r["local_path"])
        if not path.lower().endswith(".pdf") or not os.path.exists(path):
            continue
        try:
            doc = pymupdf.open(path)
        except Exception:  # noqa: BLE001
            continue
        for pno in range(min(3, len(doc))):
            for xref, _ext, _typ, basefont, *_ in doc.get_page_fonts(pno):
                if legacy_map_name(_font_family(basefont)):
                    continue
                buf = _font_bytes(doc, xref)
                if not buf:
                    continue
                key = hashlib.sha1(buf).hexdigest()
                if key in seen:
                    continue
                seen.add(key)
                try:
                    font = TTFont(io.BytesIO(buf))
                except Exception:  # noqa: BLE001
                    continue
                if "cmap" not in font:
                    continue
                cmap = font.getBestCmap() or {}
                if "GSUB" not in font or "glyf" not in font or sum(1 for cp in cmap if 0x0900 <= cp <= 0x097F) < 60:
                    continue
                try:
                    one = G.build_reference(buf)
                except Exception as e:  # noqa: BLE001
                    print(f"[glyphs] {basefont}: {e}", file=sys.stderr)
                    continue
                before = len(ref["hash_text"])
                for h, t in one["hash_text"].items():
                    ref["hash_text"].setdefault(h, t)
                ref["reph_hashes"] |= set(one["reph_hashes"])
                print(f"[glyphs] reference from {basefont}: +{len(ref['hash_text']) - before} outlines", file=sys.stderr)
    ref["reph_hashes"] = sorted(ref["reph_hashes"])
    return ref


def _windows(text: str, size: int = 1200, overlap: int = 150, base: int = 0) -> list[tuple[str, int]]:
    """Paragraph-aligned windows of ~size chars. Returns (window, offset of
    its first character in the original text + base) so callers can map
    each window back to the page it starts on."""
    paras = [(m.start(), m.group(0).strip()) for m in re.finditer(r"\S(?:.|\n(?!\s*\n))*", text)]
    out: list[tuple[str, int]] = []
    cur, cur_start = "", 0
    for start, p in paras:
        if not p:
            continue
        if cur and len(cur) + len(p) + 1 <= size:
            cur = f"{cur}\n{p}"
            continue
        if cur:
            out.append((cur, cur_start))
        pos = start
        while len(p) > size:
            out.append((p[:size], pos))
            p, pos = p[size - overlap:], pos + size - overlap
        cur, cur_start = p, pos
    if cur:
        out.append((cur, cur_start))
    return [(w, o + base) for w, o in out]


def chunk_document(pages: list[str], is_legislation: bool) -> list[dict]:
    """Split into sections (legislation) or windows (everything else).
    Each chunk remembers the page it starts on."""
    joined, page_starts, pos = [], [], 0
    for p in pages:
        page_starts.append(pos)
        joined.append(p)
        pos += len(p) + 2
    full = "\n\n".join(joined)

    def page_of(offset: int) -> int:
        lo = 0
        for i, s in enumerate(page_starts):
            if s <= offset:
                lo = i
            else:
                break
        return lo + 1

    chunks: list[dict] = []
    if is_legislation:
        matches = find_sections(full)
        # require a plausible, mostly increasing section sequence
        if len(matches) >= 3:
            chapter = None
            chapter_marks = [(m.start(), m.group(0).strip()) for m in CHAPTER_RE.finditer(full)]
            bounds = [m.start() for m in matches] + [len(full)]
            pre = full[: matches[0].start()].strip()
            if len(pre) > 80:
                for w, _ in _windows(pre, 1500, 100):
                    chunks.append({"section": "प्रस्तावना", "heading": "प्रस्तावना / प्रारम्भिक", "text": w, "page": 1})
            for i, m in enumerate(matches):
                body = full[bounds[i]: bounds[i + 1]].strip()
                for cs, ct in chapter_marks:
                    if cs <= m.start():
                        chapter = ct
                num = m.group("num").translate(DEV_DIGITS)
                head = " ".join(re.sub("[\ue000-\uf8ff]", "", m.group("head")).split())
                pieces = _windows(body, 1800, 200, base=bounds[i]) if len(body) > 2200 else [(body, bounds[i])]
                for j, (piece, off) in enumerate(pieces):
                    chunks.append({
                        "section": num + (f" ({j + 1})" if len(pieces) > 1 else ""),
                        "heading": head,
                        "chapter": chapter,
                        "text": piece,
                        "page": page_of(off),
                    })
            return [c for c in chunks if len(c["text"]) > 30]

    for w, off in _windows(full, 1200, 150):
        chunks.append({"section": None, "heading": None, "text": w, "page": page_of(off)})
    return [c for c in chunks if len(c["text"]) > 30]


VOCAB_PATH = os.path.join(OUT_DIR, "ne_vocab.json")
NKP_CASES = os.path.join(ROOT, "sources", "nkp", "cases.jsonl")
_WORD_RE = re.compile(r"[\u0900-\u0963\u0971-\u097f]{2,}")
_vocab: set[str] | None = None


def build_vocab() -> set[str]:
    """Words seen >=2x in clean Unicode Supreme Court text (nkp.gov.np)."""
    import collections

    sys.path.insert(0, os.path.join(ROOT, "backend"))
    from app.text_norm import fold

    cnt = collections.Counter()
    if os.path.exists(NKP_CASES):
        for line in open(NKP_CASES, encoding="utf-8"):
            c = json.loads(line)
            cnt.update(_WORD_RE.findall(fold(" ".join([c.get("title", ""), c.get("headnote") or "", c.get("conclusion") or ""]))))
    return {w for w, n in cnt.items() if n >= 2}


def _get_vocab() -> set[str]:
    global _vocab
    if _vocab is None:
        _vocab = set(json.load(open(VOCAB_PATH, encoding="utf-8"))) if os.path.exists(VOCAB_PATH) else set()
    return _vocab


def valid_word_rate(text: str) -> float | None:
    """Share of Devanagari words that are real Nepali words; garbage
    encodings score far below real (even archaic) Nepali."""
    vocab = _get_vocab()
    if not vocab:
        return None
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    from app.text_norm import fold

    words = _WORD_RE.findall(fold(text))
    if len(words) < 20:
        return None
    return sum(w in vocab for w in words) / len(words)


LEGISLATION_CATS = {"act", "rule", "constitution", "order", "amendment", "directive"}


def process(rec: dict) -> dict | None:
    path = os.path.join(ROOT, rec["local_path"])
    if not path.lower().endswith(".pdf") or not os.path.exists(path):
        return None
    try:
        ex = extract_pdf(path)
    except Exception as e:  # noqa: BLE001
        return {"url": rec["url"], "sha256": rec["sha256"], "error": str(e)}
    is_leg = rec["category"] in LEGISLATION_CATS or bool(
        re.search(r"(ऐन|नियमावली|नियमहरु|नियमहरू|संहिता|आदेश|संविधान|अध्यादेश)", rec.get("title") or "")
    )
    ocr_path = os.path.join(OUT_DIR, "ocr", rec["sha256"] + ".json")
    if os.path.exists(ocr_path):
        ex["pages"] = [re.sub(r"</?(?:u|b|i|strong|em)>|\*\*", "", p)
                       for p in json.load(open(ocr_path, encoding="utf-8"))["pages"]]
        ex["needs_ocr"] = False
        ex["ocr"] = True
    full = "\n".join(ex["pages"])
    quality = valid_word_rate(full)
    garbled = full.count("\ufffd") > 0.05 * max(1, len(full))
    if (quality is not None and quality < 0.3) or garbled:
        ex["needs_ocr"] = True  # text layer is not real Nepali: send to OCR instead
    chunks = [] if ex["needs_ocr"] else chunk_document(ex["pages"], is_leg)
    chunks = [c for c in chunks if (valid_word_rate(c["text"]) or 1.0) >= 0.25]
    return {
        "url": rec["url"],
        "sha256": rec["sha256"],
        "title": rec.get("title"),
        "category": rec["category"],
        "source_page": rec.get("source_page"),
        "local_path": rec["local_path"],
        "n_pages": ex["n_pages"],
        "legacy_fraction": ex["legacy_fraction"],
        "devanagari_share": ex["devanagari_share"],
        "quality": round(quality, 3) if quality is not None else None,
        "empty_pages": ex["empty_pages"][:50],
        "needs_ocr": ex["needs_ocr"],
        "is_legislation": is_leg,
        "chunks": chunks,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--rebuild-glyphs", action="store_true")
    ap.add_argument("--rebuild-vocab", action="store_true")
    args = ap.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    os.makedirs(OUT_DIR, exist_ok=True)
    done: dict[str, dict] = {}
    if os.path.exists(OUT_PATH) and not args.force:
        for line in open(OUT_PATH, encoding="utf-8"):
            r = json.loads(line)
            if r.get("needs_ocr") and os.path.exists(os.path.join(OUT_DIR, "ocr", r["sha256"] + ".json")):
                continue  # OCR text has arrived since: re-process
            done[r["sha256"]] = r

    records, seen_sha = [], set(done)
    for line in open(MANIFEST, encoding="utf-8"):
        r = json.loads(line)
        if r["sha256"] in seen_sha:
            continue  # same file content already processed (dup links)
        seen_sha.add(r["sha256"])
        records.append(r)

    if args.rebuild_vocab or not os.path.exists(VOCAB_PATH):
        vocab = build_vocab()
        with open(VOCAB_PATH, "w", encoding="utf-8") as f:
            json.dump(sorted(vocab), f, ensure_ascii=False)
        print(f"[extract] vocabulary: {len(vocab)} words", file=sys.stderr)

    if args.rebuild_glyphs or not os.path.exists(GLYPH_REF_PATH):
        all_recs = [json.loads(l) for l in open(MANIFEST, encoding="utf-8")]
        ref = build_glyph_reference(all_recs)
        with open(GLYPH_REF_PATH, "w", encoding="utf-8") as f:
            json.dump(ref, f, ensure_ascii=False)

    print(f"[extract] {len(done)} cached, {len(records)} new", file=sys.stderr)
    n = 0
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as out, ProcessPoolExecutor(args.workers) as ex:
        for r in done.values():
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
        for res in ex.map(process, records, chunksize=2):
            if res is None:
                continue
            out.write(json.dumps(res, ensure_ascii=False) + "\n")
            out.flush()
            n += 1
            if n % 25 == 0:
                print(f"[extract] {n}/{len(records)}", file=sys.stderr)
    os.replace(tmp, OUT_PATH)
    print(f"[extract] done: {n} documents", file=sys.stderr)


if __name__ == "__main__":
    main()
