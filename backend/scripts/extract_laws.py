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
SECTION_RE = re.compile(
    r"(?m)^[ \t]*(?P<num>[०-९0-9]{1,3}(?:\.[क-ह])?)[.\)]\s{0,4}(?P<head>[^\n:ः।]{2,140}?)\s*[:ः]"
)
CHAPTER_RE = re.compile(r"(?m)^[ \t]*(परिच्छेद|भाग)\s*[-–—]?\s*([०-९0-9]{1,3})")

_mapper = None


def _get_mapper():
    global _mapper
    if _mapper is None:
        import npttf2utf
        from npttf2utf.base.fontmapper import FontMapper

        _mapper = FontMapper(os.path.join(os.path.dirname(npttf2utf.__file__), "map.json"))
    return _mapper


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


GLYPH_TABLES_PATH = os.path.join(OUT_DIR, "glyph_tables.json")
_glyph_tables: dict | None = None


def _font_family(basefont: str) -> str:
    return basefont.split("+", 1)[-1]


def load_glyph_tables() -> dict:
    global _glyph_tables
    if _glyph_tables is None:
        import devanagari_glyphs as G

        raw = json.load(open(GLYPH_TABLES_PATH, encoding="utf-8")) if os.path.exists(GLYPH_TABLES_PATH) else {}
        _glyph_tables = {fam: G.prepare(t) for fam, t in raw.items()}
    return _glyph_tables


def _embedded_font(doc, xref):
    import io

    from fontTools.ttLib import TTFont

    try:
        buf = doc.extract_font(xref)[3]
        return (TTFont(io.BytesIO(buf)), buf) if buf else (None, None)
    except Exception:  # noqa: BLE001
        return None, None


def _compatible(font, table: dict) -> bool:
    """The embedded (possibly subset) font must agree with the reference
    table on the Devanagari glyphs it maps in its own cmap."""
    order = font.getGlyphOrder()
    gid = {n: i for i, n in enumerate(order)}
    agree = total = 0
    for cp, name in (font.getBestCmap() or {}).items():
        if 0x0900 <= cp <= 0x097F and name in gid:
            total += 1
            agree += table["text"].get(gid[name]) == chr(cp)
    return total == 0 or agree / total >= 0.95


def font_plan(doc) -> dict[str, tuple]:
    """font name (as texttrace reports it) -> ("legacy", map) | ("glyph", table) | ("plain", None)."""
    tables = load_glyph_tables()
    plan: dict[str, tuple] = {}
    for pno in range(len(doc)):
        for xref, _ext, _typ, basefont, *_ in doc.get_page_fonts(pno):
            fam = _font_family(basefont)
            if fam in plan:
                continue
            m = legacy_map_name(fam)
            if m:
                plan[fam] = ("legacy", m)
            elif fam in tables:
                font, _ = _embedded_font(doc, xref)
                ok = font is None or _compatible(font, tables[fam])
                plan[fam] = ("glyph", tables[fam]) if ok else ("plain", None)
            else:
                plan[fam] = ("plain", None)
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
    return {
        "n_pages": len(pages),
        "pages": pages,
        "legacy_fraction": round(legacy / total, 3) if total else 0.0,
        "glyph_decoded_fonts": sorted(f for f, (k, _) in plan.items() if k == "glyph"),
        "empty_pages": empty,
        "needs_ocr": len(pages) > 0 and len(empty) / len(pages) > 0.5,
    }


def build_glyph_tables(records: list[dict], max_docs: int = 400) -> dict:
    """Scan PDFs for complete embedded Devanagari fonts (with GSUB) and build
    one GID->Unicode table per font family."""
    import pymupdf

    import devanagari_glyphs as G

    found: dict[str, dict] = {}
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
                fam = _font_family(basefont)
                if fam in found or legacy_map_name(fam):
                    continue
                font, buf = _embedded_font(doc, xref)
                if font is None or "GSUB" not in font:
                    continue
                cmap = font.getBestCmap() or {}
                if sum(1 for cp in cmap if 0x0900 <= cp <= 0x097F) < 60:
                    continue  # not a (complete) Devanagari font
                try:
                    found[fam] = G.build_glyph_table(buf)
                    print(f"[glyphs] table for {fam}: {len(found[fam]['text'])} glyphs", file=sys.stderr)
                except Exception as e:  # noqa: BLE001
                    print(f"[glyphs] failed for {fam}: {e}", file=sys.stderr)
    return found


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
        matches = list(SECTION_RE.finditer(full))
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
                head = m.group("head").strip()
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
    chunks = [] if ex["needs_ocr"] else chunk_document(ex["pages"], is_leg)
    return {
        "url": rec["url"],
        "sha256": rec["sha256"],
        "title": rec.get("title"),
        "category": rec["category"],
        "source_page": rec.get("source_page"),
        "local_path": rec["local_path"],
        "n_pages": ex["n_pages"],
        "legacy_fraction": ex["legacy_fraction"],
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
    args = ap.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    os.makedirs(OUT_DIR, exist_ok=True)
    done: dict[str, dict] = {}
    if os.path.exists(OUT_PATH) and not args.force:
        for line in open(OUT_PATH, encoding="utf-8"):
            r = json.loads(line)
            done[r["sha256"]] = r

    records, seen_sha = [], set(done)
    for line in open(MANIFEST, encoding="utf-8"):
        r = json.loads(line)
        if r["sha256"] in seen_sha:
            continue  # same file content already processed (dup links)
        seen_sha.add(r["sha256"])
        records.append(r)

    if args.rebuild_glyphs or not os.path.exists(GLYPH_TABLES_PATH):
        all_recs = [json.loads(l) for l in open(MANIFEST, encoding="utf-8")]
        tables = build_glyph_tables(all_recs)
        with open(GLYPH_TABLES_PATH, "w", encoding="utf-8") as f:
            json.dump({fam: {"text": {str(k): v for k, v in t["text"].items()}, "reph": t["reph"]}
                       for fam, t in tables.items()}, f, ensure_ascii=False)

    print(f"[extract] {len(done)} cached, {len(records)} new", file=sys.stderr)
    mode = "w" if args.force else "a"
    n = 0
    with open(OUT_PATH, mode, encoding="utf-8") as out, ProcessPoolExecutor(args.workers) as ex:
        for res in ex.map(process, records, chunksize=2):
            if res is None:
                continue
            out.write(json.dumps(res, ensure_ascii=False) + "\n")
            out.flush()
            n += 1
            if n % 25 == 0:
                print(f"[extract] {n}/{len(records)}", file=sys.stderr)
    print(f"[extract] done: {n} documents", file=sys.stderr)


if __name__ == "__main__":
    main()
