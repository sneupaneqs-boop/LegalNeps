"""
Step 2 of the regulator pipeline: turns the documents downloaded by
scrape_regulators.py (sources/regulators/<authority>/manifest.jsonl + files/)
into corpus entries and writes ONE new shard,
backend/app/data/corpus/part-002.jsonl.gz, updating manifest.json.

    python3 backend/scripts/ingest_regulators.py            # extract (cached) + build shard + manifest
    python3 backend/scripts/ingest_regulators.py --dry-run  # report only, write nothing
    python3 backend/scripts/ingest_regulators.py --force    # re-extract every PDF

What it reuses (nothing is re-implemented):
  - extract_laws.extract_pdf / chunk_document / _windows / valid_word_rate: PDF text
    (Unicode, legacy Preeti/Kantipur fonts, glyph-decoded embedded fonts), section
    splitting, ~1,200-char paragraph windows, garbage-encoding detection.
  - devanagari_glyphs (via extract_laws): the embedded-font decoder. Its reference
    (sources/processed/glyph_reference.json) is built from a sample of Law Commission
    PDFs when missing; ne_vocab.json (the word list used to reject garbage encodings)
    is built from the Supreme Court precedents already in the corpus.
  - build_corpus conventions: same entry schema, `doc_id`/`provision_id`, digest =
    sha256 of all entry ids in shard order, first 16 hex chars.

Chunking: acts/regulations by दफा/नियम; directives/circulars by निर्देशन number and
numbered बुँदा (N।) when the text has them, otherwise ~1,200-char paragraph windows.
English-only text goes to text_en/title_en/source_en.

Dropped, and reported: scanned/garbled PDFs ("needs OCR"), .doc/.docx (no converter),
table-of-contents pages, chunks with <25% valid Nepali words, and exact duplicates of
text already in the corpus (or in an earlier regulator chunk).

`status`: "in_force" only where the document is demonstrably the current instrument -
the latest Unified Directive (2082) issue, instruments dated in the current fiscal year
(2083/84), the FY 2083/84 tax-rate notices and the Finance Act 2083; everything else
(older circulars, consolidated acts that a later amendment may have touched) is "unknown".

NOTE: build_corpus.py deletes every *.jsonl.gz in the corpus directory when it rebuilds;
re-run this script afterwards to restore part-002.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "backend"))

import extract_laws as X  # noqa: E402
import scrape_regulators as S  # noqa: E402
from app.doc_meta import classify_status, extract_doc_meta  # noqa: E402
from app.text_norm import fold  # noqa: E402

REG_ROOT = os.path.join(ROOT, "sources", "regulators")
CORPUS_DIR = os.path.join(ROOT, "backend", "app", "data", "corpus")
SHARD_NAME = "part-002.jsonl.gz"
SHARD_MAX_BYTES = 40 * 1024 * 1024
EXTRACT_DIR = os.path.join(ROOT, "sources", "processed", "regulators")
FLAT_REPORT = os.path.join(REG_ROOT, "ingest_report.json")

AUTHORITY_ORDER = ["nrb", "ird", "sebon", "ocr", "ppmo", "nia", "moless", "gazette", "lawcommission-gap"]
AUTH_EN = {
    "nrb": "Nepal Rastra Bank", "ird": "Inland Revenue Department", "sebon": "Securities Board of Nepal",
    "ocr": "Office of the Company Registrar", "nia": "Nepal Insurance Authority",
    "moless": "Ministry of Labour, Employment and Social Security", "ppmo": "Public Procurement Monitoring Office",
    "gazette": "Nepal Gazette", "lawcommission-gap": "Nepal Law Commission",
}
AUTH_SLUG = {"lawcommission-gap": "lawcommission"}
KIND_EN = {"act": "Act", "regulation": "Regulation", "directive": "Directive", "circular": "Circular",
           "guideline": "Guideline", "notice": "Notice"}
LABEL_NE = {"act": "दफा", "rule": "नियम", "directive": "बुँदा"}
LABEL_EN = {"act": "Section", "rule": "Rule", "directive": "Clause"}
MAX_CHUNK = 1400
DEV = str.maketrans("०१२३४५६७८९", "0123456789")
DEVRE = re.compile(r"[ऀ-ॿ]")
LATINRE = re.compile(r"[A-Za-z]")

# Left out by default: a regulator's own housekeeping rules (staff, procurement, finance
# administration) and English translations of Acts/Rules the Law Commission pass already
# carries in Nepali - they add tokens (and BM25 length statistics) without answering a
# CA/SME/lawyer question, and displaced core statutes in the retrieval eval.
LOW_VALUE_TITLE = re.compile(
    r"Procurement|खरिद\s*(?:नियमावली|विनियमावली|निर्देशिका)|आर्थिक प्रशासन|कर्मचारी|Staff|Service Bylaw|"
    r"Suggestion Form|अख्तियार|प्रकाशन निर्देशिका|"
    r"^Securities Act, 2063|Money\) Laundering Prevention Act, 2008|^Commodities Act|"  # English copies of Acts carried in Nepali
    r"^RTGS System Rules 2019$|Unofficial Tr|"
    # NRB's own central-bank operations (currency, open-market, government debt, RTGS liquidity),
    # not something a CA/SME/lawyer asks about
    r"नोट तथा सिक्का|खुला बजार|राष्ट्र\s?ऋण|अन्तर बैंक भुक्तानी|दैनिक तरलता|नगद सम्बन्धी|ऋणपत्रको प्राथमिक|सरकारी कारोवार|"
    r"कर्जा सूचना विनियमावली|वित्तिय मध्यस्थता", re.I)

# NRB circulars issued before a Unified Directive/Circular was (re)issued are folded into it
# ("...२०८२ माघ २ सम्म जारी भएका परिपत्र/निर्देशन समेतलाई समावेश गरी परिमार्जन गरिएको"), so the
# earlier amendments are superseded text. source_list prefix -> issue date (AD) of the
# consolidated instrument; anything older is dropped ("superseded").
INCORPORATED_BEFORE = {"bfr-circulars": (2026, 1, 16), "fxm-circulars": (2026, 4, 7)}

# The title of a *consolidated issue* ("एकीकृत निर्देशन, २०८२ जारी गरिएको सम्बन्धमा"), as opposed to a
# circular that amends the directive ("...जारी गरिएको एकीकृत निर्देशन, २०८२ मा संशोधन")
CONSOLIDATED_ISSUE = re.compile(r"एकीकृत\s*(?:निर्देशन|परिपत्र)\s*[-–,]*\s*[०-९0-9]{4}\s*जारी")

# "X (छैठौं संशोधन) नियमावली, २०८२": an instrument that only amends, as opposed to a consolidated text
AMENDING_ONLY = re.compile(r"\([^)]*संशोधन[^)]*\)\s*(?:नियमावली|विनियमावली|निर्देशिका|कार्यविधि|ऐन|निर्देशन)")

CORE_AUTHORITIES = {"ird", "sebon", "ocr", "ppmo", "lawcommission-gap"}
_AUTH_BY_EN = {v: k for k, v in AUTH_EN.items()}

# current fiscal year 2083/84 began 1 Shrawan 2083 (2026-07-17)
CURRENT_FY_BS = (2083, 4, 1)
CURRENT_FY_AD = (2026, 7, 16)


# --------------------------------------------------------------------------
# support files for extract_laws (glyph reference, vocabulary)
# --------------------------------------------------------------------------
def _iter_shard_lines(skip_reg: bool = True):
    manifest = os.path.join(CORPUS_DIR, "manifest.json")
    files = json.load(open(manifest, encoding="utf-8"))["files"] if os.path.exists(manifest) else []
    for name in files:
        if skip_reg and name == SHARD_NAME:
            continue
        with gzip.open(os.path.join(CORPUS_DIR, name), "rt", encoding="utf-8") as f:
            for line in f:
                yield line


def ensure_vocab() -> None:
    """ne_vocab.json = words seen >=2x in clean Unicode text (the Supreme Court
    precedents in the existing corpus) - what extract_laws.valid_word_rate needs."""
    if os.path.exists(X.VOCAB_PATH):
        return
    cnt: Counter = Counter()
    for line in _iter_shard_lines():
        if '"category": "precedent"' in line[:400]:
            e = json.loads(line)
            cnt.update(X._WORD_RE.findall(fold(" ".join([e.get("doc_title_ne") or "", e.get("text_ne") or ""]))))
    vocab = sorted(w for w, n in cnt.items() if n >= 2)
    os.makedirs(X.OUT_DIR, exist_ok=True)
    json.dump(vocab, open(X.VOCAB_PATH, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[ingest] vocabulary built from precedents: {len(vocab)} words", file=sys.stderr)


def ensure_glyph_reference(sample: int = 45) -> None:
    """Government PDFs set in an embedded Unicode font whose ToUnicode map is broken
    ("सेिामा" for "सेवामा") can only be read by matching glyph outlines against a
    reference built from complete Kalimati-style fonts. Those complete fonts live in
    Law Commission PDFs, so sample some once (resumable) and build the reference."""
    if os.path.exists(X.GLYPH_REF_PATH):
        return
    import scrape_regulators as S

    client, store, n = S.Client(), S.Store("_glyphref"), 0
    for d in S.giwms_listing(client, S.LAWCOMMISSION, "/category/1757", max_pages=8):
        if n >= sample:
            break
        for f in S.giwms_files(client, d["url"]):
            n += len(S.download(client, store, {"url": f, "title": d["title"], "page_url": d["url"]}, follow=False))
    ref = X.build_glyph_reference(list(store.records.values()))
    os.makedirs(X.OUT_DIR, exist_ok=True)
    json.dump(ref, open(X.GLYPH_REF_PATH, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[ingest] glyph reference: {len(ref['hash_text'])} outlines from {n} PDFs", file=sys.stderr)


# --------------------------------------------------------------------------
# extraction (cached per PDF sha256)
# --------------------------------------------------------------------------
def _cache_path(sha: str) -> str:
    return os.path.join(EXTRACT_DIR, sha + ".json")


def extract_one(rec: dict) -> dict:
    """Extract one PDF (cached). Returns the extract_laws.extract_pdf result plus the sha,
    or {"sha256", "error"}. Pages come from sources/processed/ocr/<sha>.json when an OCR
    pass (ocr_gemini.py) has produced them for a scanned file."""
    cp = _cache_path(rec["sha256"])
    if os.path.exists(cp):
        return json.load(open(cp, encoding="utf-8"))
    path = os.path.join(ROOT, rec["local_path"])
    out = {"sha256": rec["sha256"]}
    try:
        ex = X.extract_pdf(path)
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        return out
    ocr_path = os.path.join(X.OUT_DIR, "ocr", rec["sha256"] + ".json")
    if os.path.exists(ocr_path):
        ex["pages"] = [re.sub(r"</?(?:u|b|i|strong|em)>|\*\*", "", p) for p in json.load(open(ocr_path, encoding="utf-8"))["pages"]]
        ex["needs_ocr"] = False
    out.update({k: ex[k] for k in ("n_pages", "pages", "devanagari_share", "legacy_fraction", "empty_pages", "needs_ocr")})
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    json.dump(out, open(cp, "w", encoding="utf-8"), ensure_ascii=False)
    return out


def assess(ex: dict) -> dict:
    """Decide whether a text layer is usable. Nepali text is checked against the word list
    (garbage legacy encodings score far below real Nepali); English text is not.
    A glyph-decoded font may emit U+FFFD for its space glyph - that is repaired, not rejected."""
    if ex.get("error") or ex.get("needs_ocr"):
        return ex
    full = "\n".join(ex["pages"])
    if ex["devanagari_share"] >= 0.3:
        if "\ufffd" in full:
            fixed = full.replace("\ufffd", " ")
            if (X.valid_word_rate(fixed) or 0) >= 0.5:
                ex["pages"] = [p.replace("\ufffd", " ") for p in ex["pages"]]
                full = fixed
        quality = X.valid_word_rate(full)
        ex["quality"] = round(quality, 3) if quality is not None else None
        if (quality is not None and quality < 0.3) or full.count("\ufffd") > 0.05 * max(1, len(full)):
            ex["needs_ocr"] = True
    return ex


# --------------------------------------------------------------------------
# chunking
# --------------------------------------------------------------------------
UNIT_RE = re.compile(r"(?m)^[ \t]*(?P<unit>(?:इ\.?\s?प्रा\.?\s?)?निर्देशन\s*नं\.?\s*[०-९0-9]+\s*/\s*[०-९0-9]+)[ \t]*$")
CLAUSE_RE = re.compile(r"(?m)^[ \t]*(?P<num>[०-९0-9]{1,3})[.।][ \t]*(?P<head>[^\n]{2,200})")
_DANDA_NUM = re.compile(r"(?m)^([ \t-*]*[०-९0-9]{1,3})।")


def looks_toc(text: str) -> bool:
    """A contents page: many short lines ending in page numbers / dot leaders."""
    lines = [l for l in text.split("\n") if l.strip()]
    if len(lines) < 6:
        return False
    hits = sum(bool(re.search(r"(?:…|\.{3,})|\s[०-९0-9]{1,3}\s*$", l)) for l in lines)
    return hits / len(lines) > 0.5 or bool(re.search(r"विषय[\s\-–]*सू[चि]ी|table of contents", text[:200], re.I) and hits / len(lines) > 0.3)


def chunk_directive(pages: list[str]) -> list[dict]:
    """Split a directive/circular on its निर्देशन units and numbered बुँदा ('१३। ...:').
    Numbers must run 1,2,3... within a unit (a stray '2.' inside prose is body text)."""
    joined, starts, pos = [], [], 0
    for p in pages:
        starts.append(pos)
        joined.append(p)
        pos += len(p) + 2
    full = "\n\n".join(joined)

    def page_of(off: int) -> int:
        lo = 0
        for i, s in enumerate(starts):
            if s <= off:
                lo = i
            else:
                break
        return lo + 1

    events = sorted(
        [(m.start(), "unit", m) for m in UNIT_RE.finditer(full)] + [(m.start(), "clause", m) for m in CLAUSE_RE.finditer(full)],
        key=lambda t: t[0],
    )
    bounds: list[dict] = []
    cur, unit = 0, None
    for off, kind, m in events:
        if kind == "unit":
            unit = " ".join(m.group("unit").split())
            cur = 0
            bounds.append({"start": off, "unit": unit, "num": None, "head": None})
            continue
        n = int(m.group("num").translate(DEV))
        if n == cur + 1 or (n == 1 and (cur == 0 or cur >= 3)):
            head = re.sub(r"\s*[:ः–\-]+\s*$", "", m.group("head")).strip()
            cur = n
            bounds.append({"start": off, "unit": unit, "num": str(n), "head": head})
    clauses = [b for b in bounds if b["num"]]
    if len(clauses) < 3:
        return X.chunk_document(pages, False)
    out: list[dict] = []
    pre = full[: bounds[0]["start"]].strip()
    if len(pre) > 80:
        for w, off in X._windows(pre, 1500, 100):
            out.append({"section": None, "heading": "प्रस्तावना / प्रारम्भिक", "unit": None, "text": w, "page": page_of(off)})
    ends = [b["start"] for b in bounds[1:]] + [len(full)]
    for b, end in zip(bounds, ends):
        body = full[b["start"]:end].strip()
        if not body or (b["num"] is None and len(body) < 120):
            continue
        pieces = X._windows(body, 1800, 200, base=b["start"]) if len(body) > 2200 else [(body, b["start"])]
        for j, (piece, off) in enumerate(pieces):
            sec = b["num"] + (f" ({j + 1})" if len(pieces) > 1 else "") if b["num"] else None
            out.append({"section": sec, "heading": b["head"] or b["unit"], "unit": b["unit"], "text": piece, "page": page_of(off)})
    return out


def chunk_text(pages: list[str], doc_type: str) -> list[dict]:
    pages = [_DANDA_NUM.sub(r"\1.", p) if doc_type != "directive" else p for p in pages]  # "१।" -> "१." for the section regex
    if doc_type == "directive":
        chunks = chunk_directive(pages)
    else:
        chunks = X.chunk_document(pages, True)
    out: list[dict] = []
    for c in chunks:
        if len(c["text"]) > MAX_CHUNK:  # keep passages near the ~1,200-char window the rest of the corpus uses
            for j, (w, _off) in enumerate(X._windows(c["text"], 1200, 150)):
                sec = c.get("section")
                out.append({**c, "text": w, "section": (f"{sec} ({j + 1})" if sec and "(" not in sec else sec)})
        else:
            out.append(c)
    return [c for c in out if len(c["text"].strip()) >= 60 and not looks_toc(c["text"])]


def script_of(text: str) -> str:
    dev, lat = len(DEVRE.findall(text)), len(LATINRE.findall(text))
    return "en" if lat > 2 * dev else "ne"


# --------------------------------------------------------------------------
# entries
# --------------------------------------------------------------------------
def clean_title(t: str) -> str:
    t = re.sub(r"\s+", " ", t or "").strip(" -–:")
    return re.sub(r"\s*\(English\)$", "", t)


def english_title(pages: list[str], fallback: str) -> str:
    for line in (pages[0] if pages else "").split("\n"):
        line = line.strip()
        if 10 <= len(line) <= 120 and len(LATINRE.findall(line)) > 0.7 * len(line.replace(" ", "")):
            return line
    return fallback


def superseded(rec: dict, title: str) -> bool:
    """A circular folded into a later consolidated Unified Directive/Circular (not the
    consolidated issue itself)."""
    for prefix, cutoff in INCORPORATED_BEFORE.items():
        is_consolidated_issue = bool(CONSOLIDATED_ISSUE.search(title))
        if (rec.get("source_list") or "").startswith(prefix) and not is_consolidated_issue:
            if S.pub_sort_key(rec.get("published")) < cutoff:
                return True
    return False


def status_for(rec: dict, doc_type: str, meta: dict) -> str:
    title = rec["title"]
    pub = rec.get("published") or ""
    ad = re.match(r"(\d{4})-(\d\d)-(\d\d)", pub)
    bs = None
    try:
        import scrape_regulators as S

        bs = S.bs_key(pub)
        ad_t = S._ad_date(pub)
        ad_key = (ad_t.tm_year, ad_t.tm_mon, ad_t.tm_mday) if ad_t else (tuple(int(x) for x in ad.groups()) if ad else None)
    except Exception:  # noqa: BLE001
        ad_key = None
    in_current_fy = bool((bs and bs >= CURRENT_FY_BS) or (ad_key and ad_key >= CURRENT_FY_AD))
    if rec.get("authority") == "nrb" and CONSOLIDATED_ISSUE.search(title):
        # the consolidated Unified Directive/Circular issue of its class (Unified Directive 2082 for
        # A/B/C, D and infrastructure banks; Unified Circular 2082 for foreign exchange). Earlier
        # issues are dropped as older editions before this point, so what survives is the latest.
        return "in_force"
    if in_current_fy and rec.get("kind") in ("circular", "directive", "guideline"):
        return "in_force"
    if "आर्थिक ऐन, २०८३" in title and "जानकारी" not in title and "पुस्तिका" not in title:
        return "in_force"
    if "आ.व.२०८३।०८४" in title:  # IRD tax-rate notices for FY 2083/84
        return "in_force"
    if doc_type in ("act", "rule") and classify_status(title, meta) == "bill":
        return "bill"
    return "unknown"


def build_entries(rec: dict, ex: dict, existing_keys: set[int], seen_keys: set[int]) -> tuple[list[dict], dict]:
    """Corpus entries for one document + a small stats dict."""
    from app.retrieval import _text_key

    doc_type = rec.get("doc_type") or "directive"
    kind = rec.get("kind") or doc_type
    authority = rec["authority"]
    doc_lang = "en" if (ex.get("devanagari_share") or 0) < 0.3 else "ne"
    title = clean_title(rec["title"])
    title_is_latin = script_of(title) == "en"
    en_title = english_title(ex["pages"], title) if doc_lang == "en" or title_is_latin else ""
    if doc_lang == "en" and title_is_latin:
        en_title = title
    # doc_title_ne: the Nepali listing title; for documents that only have an English
    # title it carries that (retrieval groups/caps passages by doc_title_ne, the law
    # browser slugs it - empty would make every chunk its own "document")
    doc_title_ne = title
    doc_title_en = en_title if (doc_lang == "en" or title_is_latin) else ""
    chunks = chunk_text(ex["pages"], doc_type)
    short = rec["sha256"][:10]
    slug = AUTH_SLUG.get(authority, authority)
    meta = extract_doc_meta(chunks[0]["text"]) if chunks and doc_lang == "ne" else {}
    status = status_for({**rec, "title": title}, doc_type, meta)
    topic = f"{AUTH_EN[authority]} {KIND_EN.get(kind, kind).lower()}"
    entries, dup = [], 0
    for i, ch in enumerate(chunks):
        text = ch["text"].strip()
        # a Nepali document stays text_ne even where a table/acronym-heavy chunk is mostly Latin;
        # an English document goes to text_en unless the chunk itself is Nepali (e.g. a form)
        lang = "ne" if doc_lang == "ne" or script_of(text) == "ne" else "en"
        key = _text_key({"text_ne": text if lang == "ne" else "", "text_en": text if lang == "en" else ""})
        if key in existing_keys or key in seen_keys:
            dup += 1
            continue
        if lang == "ne" and (X.valid_word_rate(text) or 1.0) < 0.25:
            continue  # garbled chunk in an otherwise readable PDF
        seen_keys.add(key)
        sec, head, unit = ch.get("section"), ch.get("heading") or "", ch.get("unit")
        is_num = bool(sec) and bool(re.match(r"^\d", sec))
        label_ne, label_en = LABEL_NE[doc_type], LABEL_EN[doc_type]
        unit_bit = f", {unit}" if unit else ""
        ttl = f"{head} ({doc_title_ne})" if head and head != doc_title_ne else doc_title_ne
        if unit and head and head != unit:
            ttl = f"{unit} - {head} ({doc_title_ne})"
        e = {
            "id": f"reg-{slug}-{short}-{i}",
            "category": "law",
            "doc_type": doc_type,
            "topic": topic,
            "doc_title_ne": doc_title_ne,
            "doc_title_en": doc_title_en,
            "section": sec,
            "title_ne": ttl if lang == "ne" else (doc_title_ne if not title_is_latin else ""),
            "title_en": (f"{head} ({doc_title_en})" if head and lang == "en" and doc_title_en else doc_title_en) if lang == "en" else doc_title_en,
            "text_ne": text if lang == "ne" else "",
            "text_en": text if lang == "en" else "",
            "source_ne": f"{doc_title_ne}{unit_bit}" + (f", {label_ne} {sec}" if is_num else ""),
            "source_en": f"{AUTH_EN[authority]}: {doc_title_en or doc_title_ne}{unit_bit}" + (f", {label_en} {sec}" if is_num else ""),
            "url": rec["url"] + (f"#page={ch['page']}" if ch.get("page") else ""),
            "doc_id": short,
            "provision_id": f"{short}:{sec}" if sec else short,
            "status": status,
            "authority": AUTH_EN[authority],
            "published": rec.get("published") or "",
            "fetched_at": rec.get("fetched_at") or "",
        }
        entries.append(e)
    return entries, {"chunks": len(chunks), "dup": dup, "status": status, "lang": doc_lang}


# --------------------------------------------------------------------------
# manifest / shard
# --------------------------------------------------------------------------
def corpus_digest(extra_ids: list[str]) -> tuple[str, int]:
    """Digest exactly as build_corpus.main(): sha256("".join(ids in shard order))[:16]."""
    h = hashlib.sha256()
    n = 0
    manifest = json.load(open(os.path.join(CORPUS_DIR, "manifest.json"), encoding="utf-8"))
    for name in [f for f in manifest["files"] if f != SHARD_NAME]:
        with gzip.open(os.path.join(CORPUS_DIR, name), "rt", encoding="utf-8") as f:
            for line in f:
                h.update(json.loads(line)["id"].encode())
                n += 1
    for i in extra_ids:
        h.update(i.encode())
        n += 1
    return h.hexdigest()[:16], n


def write_shard(entries: list[dict]) -> int:
    path = os.path.join(CORPUS_DIR, SHARD_NAME)
    with gzip.open(path, "wt", encoding="utf-8", compresslevel=9) as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return os.path.getsize(path)


def update_manifest(entries: list[dict]) -> dict:
    mpath = os.path.join(CORPUS_DIR, "manifest.json")
    m = json.load(open(mpath, encoding="utf-8"))
    base = m.get("counts", {})
    prev_reg = base.get("regulator_chunks", 0)
    base_total = base["total"] - prev_reg
    if SHARD_NAME not in m["files"]:
        m["files"].append(SHARD_NAME)
    m["digest"], n = corpus_digest([e["id"] for e in entries])
    docs = {e["doc_id"] for e in entries}
    base["regulator_chunks"] = len(entries)
    base["regulator_documents"] = len(docs)
    base["total"] = base_total + len(entries)
    assert n == base["total"], (n, base["total"])
    m["counts"] = base
    m["built_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
    return m


# --------------------------------------------------------------------------
def load_records() -> list[dict]:
    recs, seen = [], set()
    for auth in AUTHORITY_ORDER:
        mp = os.path.join(REG_ROOT, auth, "manifest.jsonl")
        if not os.path.exists(mp):
            continue
        latest: dict[str, dict] = {}
        for line in open(mp, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                latest[r["url"]] = r
        for r in latest.values():
            if r["sha256"] in seen or not os.path.exists(os.path.join(ROOT, r["local_path"])):
                continue
            seen.add(r["sha256"])
            recs.append(r)
    return recs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="build and report, write nothing")
    ap.add_argument("--force", action="store_true", help="ignore the extraction cache")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--exclude", default="", help="regex on document title: leave matching documents out (extra size/memory trimming)")
    ap.add_argument("--profile", choices=["core", "full"], default="core",
                    help="core (default): statutes, in-force instruments and the IRD/SEBON/OCR directives; full: everything readable")
    ap.add_argument("--max-chunks", type=int, default=0, help="keep at most N chunks (drops lowest-priority documents first)")
    args = ap.parse_args()

    ensure_vocab()
    ensure_glyph_reference()
    X._vocab = None
    X._glyph_ref = None

    recs = load_records()
    skipped: dict[str, list[str]] = {"needs_ocr": [], "unsupported_format": [], "error": [], "empty": [], "duplicate_of_corpus": []}
    pdfs = []
    for r in recs:
        if not r["local_path"].lower().endswith(".pdf"):
            skipped["unsupported_format"].append(r["title"])
        else:
            pdfs.append(r)
    if args.force and os.path.isdir(EXTRACT_DIR):
        for f in os.listdir(EXTRACT_DIR):
            os.remove(os.path.join(EXTRACT_DIR, f))
    print(f"[ingest] {len(pdfs)} PDFs to extract ({len(skipped['unsupported_format'])} non-PDF skipped)", file=sys.stderr)
    t0 = time.time()
    with ProcessPoolExecutor(args.workers) as pool:
        extracted = [assess(ex) for ex in pool.map(extract_one, pdfs, chunksize=2)]
    print(f"[ingest] extraction done in {time.time() - t0:.0f}s", file=sys.stderr)

    from app.retrieval import _text_key

    existing_keys: set[int] = set()
    for line in _iter_shard_lines():
        e = json.loads(line)
        existing_keys.add(_text_key(e))
    seen_keys: set[int] = set()

    # phase 1: which documents are usable at all
    exclude = re.compile(args.exclude) if args.exclude else None
    candidates: list[tuple[dict, dict, str]] = []
    for rec, ex in zip(pdfs, extracted):
        title = clean_title(rec["title"])
        tag = f"[{rec['authority']}] {title}"
        if (exclude and exclude.search(title)) or LOW_VALUE_TITLE.search(title):
            skipped.setdefault("low_value", []).append(tag)
        elif superseded(rec, title):
            skipped.setdefault("superseded", []).append(tag)
        elif ex.get("error"):
            skipped["error"].append(f"{title}: {ex['error']}")
        elif ex.get("needs_ocr"):
            skipped["needs_ocr"].append(tag)
        elif rec.get("doc_type") in ("act", "rule") and rec["authority"] != "ird" and (
                S.in_corpus(title) or S.in_corpus(re.sub(r"\([^)]*\)", " ", title))):
            skipped["duplicate_of_corpus"].append(f"{tag} (title already in corpus)")
        else:
            candidates.append((rec, ex, title))

    # phase 2: of the readable editions of one instrument (same title series, often listed under
    # several categories) keep the newest consolidated one; a stand-alone amending instrument
    # ("X (छैठौं संशोधन) नियमावली") only survives when no consolidated text is readable
    groups: dict[tuple, list] = {}
    for c in candidates:
        if c[0].get("kind") in ("act", "regulation", "directive", "guideline"):
            groups.setdefault((c[0]["authority"], S.series_key(c[2])), []).append(c)
        elif c[0].get("kind") == "circular" and CONSOLIDATED_ISSUE.search(c[2]):
            # a consolidated issue: same class (क,ख,ग / घ / पूर्वाधार / forex) = same series across years
            key = " ".join(re.sub(r"[०-९0-9/–\-]+", " ", c[2]).split())
            groups.setdefault((c[0]["authority"], "issue:" + key), []).append(c)

    def edition_rank(c):
        rec, _ex, title = c
        amending_only = bool(AMENDING_ONLY.search(title)) and "सहित" not in title
        return (not amending_only, S.pub_sort_key(rec.get("published")))

    drop = set()
    for g in groups.values():
        best = max(g, key=edition_rank)
        for c in g:
            if c is not best:
                drop.add(id(c))
                skipped.setdefault("older_edition", []).append(f"[{c[0]['authority']}] {c[2]}")
    candidates = [c for c in candidates if id(c) not in drop]

    # phase 3: chunk. English translations go last and are kept only when the Nepali original was not ingested
    entries: list[dict] = []
    per_doc = []
    nepali_done: set[str] = set()
    for rec, ex, title in sorted(candidates, key=lambda c: c[0].get("lang") == "en"):
        if rec.get("lang") == "en" and title in nepali_done:
            skipped.setdefault("translation_of_ingested_original", []).append(f"[{rec['authority']}] {title}")
            continue
        es, st = build_entries(rec, ex, existing_keys, seen_keys)
        if not es:
            (skipped["duplicate_of_corpus"] if st["chunks"] and st["dup"] >= 0.5 * st["chunks"] else skipped["empty"]).append(f"[{rec['authority']}] {title}")
            continue
        entries += es
        if rec.get("lang") != "en":
            nepali_done.add(title)
        per_doc.append({"authority": rec["authority"], "title": title, "kind": rec.get("kind"), "chunks": len(es),
                        "status": st["status"], "lang": st["lang"], "sha": rec["sha256"][:10], "published": rec.get("published")})

    if args.profile == "core":
        # keep: statutes/regulations, instruments in force now, and the tax/company/securities
        # regulators' directives (the CA/SME core), plus NRB circulars issued since the current unified
        # directives (already filtered to those not folded into them). Dropped: NRB payment-system /
        # AML / cyber guidelines and manuals, mostly English-only, which are outside the CA/SME core.
        def core(d):
            return d["status"] == "in_force" or d["kind"] in ("act", "regulation", "circular") or d["authority"] in CORE_AUTHORITIES
        dropped = [d for d in per_doc if not core(d)]
        skipped["profile_core_dropped"] = [f"[{d['authority']}] {d['title']} ({d['chunks']} chunks)" for d in dropped]
        gone = {d["sha"] for d in dropped}
        entries = [e for e in entries if e["doc_id"] not in gone]
        per_doc = [d for d in per_doc if d["sha"] not in gone]

    if args.max_chunks and len(entries) > args.max_chunks:
        rank = lambda d: (  # noqa: E731 - lower = dropped first
            d["status"] == "in_force", d["kind"] in ("act", "regulation"), d["authority"] in ("ird", "nrb", "sebon", "ocr"), -d["chunks"])
        keep, total = set(), 0
        for d in sorted(per_doc, key=rank, reverse=True):
            if total + d["chunks"] <= args.max_chunks:
                keep.add(d["sha"])
                total += d["chunks"]
        entries = [e for e in entries if e["doc_id"] in keep]
        per_doc = [d for d in per_doc if d["sha"] in keep]

    by_auth: dict[str, dict] = {}
    for d in per_doc:
        a = by_auth.setdefault(d["authority"], {"documents": 0, "chunks": 0, "in_force_chunks": 0})
        a["documents"] += 1
        a["chunks"] += d["chunks"]
        a["in_force_chunks"] += d["chunks"] if d["status"] == "in_force" else 0
    report = {"by_authority": by_auth, "total_chunks": len(entries), "total_documents": len(per_doc),
              "skipped": {k: v for k, v in skipped.items()}, "documents": per_doc}
    print(json.dumps({k: report[k] for k in ("by_authority", "total_chunks", "total_documents")}, ensure_ascii=False, indent=1))
    for k, v in skipped.items():
        print(f"[ingest] skipped {k}: {len(v)}")
    if args.dry_run:
        return
    size = write_shard(entries)
    if size > SHARD_MAX_BYTES:
        raise SystemExit(f"shard is {size / 1e6:.1f} MB (> 40 MB): re-run with --max-chunks / --exclude")
    m = update_manifest(entries)
    report["shard_bytes"] = size
    report["manifest_counts"] = m["counts"]
    with open(FLAT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"[ingest] wrote {SHARD_NAME}: {len(entries)} chunks / {len(per_doc)} docs, {size / 1e6:.1f} MB; digest {m['digest']}")


if __name__ == "__main__":
    main()
