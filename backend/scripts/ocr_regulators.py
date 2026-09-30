"""
OCR pass for the regulator documents ingest_regulators.py had to skip as scanned
images ("needs OCR" in sources/regulators/ingest_report.json), using Tesseract
(no API, no cost) - and its own shard, backend/app/data/corpus/part-003.jsonl.gz, so
part-002 (the text-layer regulator shard) is never touched. Sources that were
unreachable when part-002 was built (NIA, MoLESS: NEW_AUTHORITIES) are ingested into
the same shard - their text-layer documents as they are, their scanned ones via OCR.
Only OCR'd chunks carry `"ocr": true`.

    python3 backend/scripts/scrape_regulators.py ...                # the PDFs must be on disk (files/)
    python3 backend/scripts/ocr_regulators.py targets               # list what needs OCR (from the report)
    python3 backend/scripts/ocr_regulators.py ocr [--workers 4]     # render 300 dpi + tesseract nep+eng, cached per page
    python3 backend/scripts/ocr_regulators.py ingest [--dry-run]    # clean, quality-gate, chunk -> part-003 + manifest

System deps (scripts only, NOT production): tesseract-ocr tesseract-ocr-nep tesseract-ocr-eng.

Chunking, entry schema, status rules, dedupe against the existing corpus and edition
handling are ingest_regulators.py's (imported, not re-implemented); every entry gets
`"ocr": true`. Cleaning and the quality gate are the pure functions in ocr_clean.py.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ingest_regulators as I  # noqa: E402
import ocr_clean as C  # noqa: E402
import scrape_regulators as S  # noqa: E402
from app.text_norm import fold  # noqa: E402

ROOT = I.ROOT
OCR_DIR = os.path.join(ROOT, "sources", "processed", "ocr_tesseract")
VOCAB_PATH = os.path.join(ROOT, "sources", "processed", "ocr_vocab.json")
SHARD_NAME = "part-003.jsonl.gz"
DPI = 300
LANG = "nep+eng"
REPORT_PATH = os.path.join(I.REG_ROOT, "ocr_report.json")


# --------------------------------------------------------------------------
# what needs OCR
# --------------------------------------------------------------------------
def needs_ocr_records() -> list[dict]:
    """Manifest records whose title is in ingest_report.json's skipped.needs_ocr
    (matched on '[authority] cleaned title'), de-duplicated by sha256. Works when the
    PDFs are gone: only the manifests + the report are needed."""
    rep = json.load(open(I.FLAT_REPORT, encoding="utf-8"))
    wanted = set(rep["skipped"]["needs_ocr"])
    by_title: dict[str, list[dict]] = {}
    seen: set[str] = set()
    for auth in I.AUTHORITY_ORDER:
        mp = os.path.join(I.REG_ROOT, auth, "manifest.jsonl")
        if not os.path.exists(mp):
            continue
        latest: dict[str, dict] = {}
        for line in open(mp, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                latest[r["url"]] = r
        for r in latest.values():
            if r["sha256"] in seen:
                continue
            seen.add(r["sha256"])
            by_title.setdefault(f"[{r['authority']}] {I.clean_title(r['title'])}", []).append(r)
    out = []
    for t in wanted:
        out += by_title.get(t, [])
    return sorted(out, key=lambda r: (I.AUTHORITY_ORDER.index(r["authority"]), r["title"]))


NEW_AUTHORITIES = ["nia", "moless", "gazette"]

# A regulator's own housekeeping (bylaws on purchasing/finance, staffing, appointments, awards, call
# centres, work plans) and the MoLESS all-in-one compilation (960 passages that repeat its separate
# directives): they add tokens without answering a CA/SME/lawyer question. Same idea as
# ingest_regulators.LOW_VALUE_TITLE, extended to the sources that file did not see.
LOW_VALUE_EXTRA = re.compile(
    r"Purchase Bylaw|Financial Bylaw|आन्तरिक व्यवस्थापन निर्देशिका|आन्तरिक कार्यसञ्चालन|पदपूर्ति|नियुक्ति सम्बन्धी|"
    r"कार्यकारी निर्देशक|आचारसंहिता|पुरस्कार|सम्मान|छात्रवृत्ति|कल सेन्टर|सूचना प्रविधिको प्रयोग|कार्ययोजना|"
    r"एकीकृत संगालो|MISCELLANEOUS|कोषको रकम बाणिज्य बैंक|"
    # IRD's how-to-fill-the-online-forms manual (a 2078 user guide, not a legal instrument)
    r"विवरण भर्ने निर्देशिका|"
    # foreign-employment programme administration, outside what a CA/SME/lawyer asks
    r"घरेलु कामदार", re.I)
# NIA publishes its English-titled copies of instruments the corpus already holds in Nepali
# (title regex, Nepali title as it is in the corpus)
EN_ALIASES = [(re.compile(r"^Insurance Act,? (?:with .*)?2079", re.I), "बीमा ऐन २०७९"),
              (re.compile(r"^Insurance Regulation,? ?2081", re.I), "बीमा नियमावली, २०८१")]
# MoLESS instruments about employment relations / workplace rules (the rest is foreign-employment programme administration)
LABOUR_CORE = re.compile(r"सामाजिक सुरक्षा योजना|श्रम अडिट|रोजगारदाता र श्रमिकको सूचीकरण|तापस्तर|व्यवसायजन्य सुरक्षा|ठगीका उजुरी|"
                         r"बालश्रम|ध्वनी र प्रकाश|श्रम इजाजत")


def series_key(title: str) -> str:
    """scrape_regulators.series_key plus the wording that only marks an edition or a language
    ('with Second Amendment', '(Nepali)', '-Registered', plural 'Regulations')."""
    t = re.sub(r"\bwith\b.*?\bamendments?\b|\bnepali\b|\benglish\b|\bregistered\b|\bammendment\b", " ", title or "", flags=re.I)
    t = re.sub(r"\b(act|regulation|guideline|directive|bylaw)s\b", r"\1", t, flags=re.I)
    return S.series_key(t)


def title_year(title: str) -> int:
    """Newest 4-digit year in the title, on the AD scale (a BS year, 2040 or later, minus 57), so
    'Directive, 2026' and 'Directive, 2025 (2082)' order correctly. Editions of one series compare on it."""
    years = [int(y) for y in re.findall(r"(?<!\d)((?:19|20)\d\d)(?!\d)", (title or "").translate(C._TO_ASCII))]
    years = [y - 57 if y >= 2040 else y for y in years]
    return max(years) if years else 0


def new_authority_records() -> list[dict]:
    """Manifest records of the sources first reachable after part-002 was built, whose files are on disk."""
    out, seen = [], set()
    for auth in NEW_AUTHORITIES:
        mp = os.path.join(I.REG_ROOT, auth, "manifest.jsonl")
        if not os.path.exists(mp):
            continue
        latest: dict[str, dict] = {}
        for line in open(mp, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                latest[r["url"]] = r
        for r in latest.values():
            if r["sha256"] not in seen and r["local_path"].lower().endswith(".pdf") \
                    and os.path.exists(os.path.join(ROOT, r["local_path"])):
                seen.add(r["sha256"])
                out.append(r)
    return out


def classify_new(recs: list[dict], workers: int = 3) -> list[tuple[dict, dict]]:
    """(record, assessed text-layer extraction) for the new-authority PDFs; `ex["needs_ocr"]`
    marks the scanned ones. Cached per sha (ingest_regulators.extract_one)."""
    if not recs:
        return []
    I.ensure_vocab()
    I.ensure_glyph_reference()
    I.X._vocab = None
    I.X._glyph_ref = None
    with ProcessPoolExecutor(workers) as pool:
        exs = [I.assess(ex) for ex in pool.map(I.extract_one, recs, chunksize=2)]
    return list(zip(recs, exs))


def all_ocr_records() -> list[dict]:
    """Everything to OCR: the report's needs-OCR list plus scanned/garbled new-authority PDFs."""
    recs = needs_ocr_records()
    recs += [r for r, ex in classify_new(new_authority_records()) if ex.get("needs_ocr") and not ex.get("error")]
    return recs


# --------------------------------------------------------------------------
# OCR (tesseract, page by page, cached)
# --------------------------------------------------------------------------
_doc_cache: dict = {}


def _tesseract(png: bytes) -> str:
    env = {**os.environ, "OMP_THREAD_LIMIT": "1"}
    try:
        r = subprocess.run(["tesseract", "stdin", "stdout", "-l", LANG, "--dpi", str(DPI)],
                           input=png, capture_output=True, timeout=600, env=env)
        return r.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return ""


def binarise(pix, window: int = 51, offset: int = 18) -> bytes:
    """Adaptive (local-mean) threshold of a grayscale pixmap -> PNG bytes."""
    import numpy as np
    import pymupdf
    from scipy.ndimage import uniform_filter

    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(np.float32)
    b = ((a > uniform_filter(a, size=window) - offset) * 255).astype(np.uint8)
    return pymupdf.Pixmap(pymupdf.csGRAY, pix.width, pix.height, b.tobytes(), False).tobytes("png")


def _ocr_page(task: tuple[str, str, int]) -> tuple[str, int, str]:
    """Render page `pno` (0-based) of `path` at 300 dpi grayscale and run tesseract."""
    import pymupdf

    sha, path, pno = task
    out = os.path.join(OCR_DIR, sha, f"p{pno + 1:04d}.txt")
    if os.path.exists(out):
        return sha, pno, "cached"
    doc = _doc_cache.get(path)
    if doc is None:
        _doc_cache.clear()
        doc = _doc_cache[path] = pymupdf.open(path)
    pix = doc[pno].get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
    text = _tesseract(pix.tobytes("png"))
    if len(re.sub(r"\s", "", text)) < 30:
        # photographed / shadowed pages defeat Tesseract's own binarisation: retry on a
        # locally thresholded copy (only pages that came back (nearly) empty)
        alt = _tesseract(binarise(pix))
        if len(re.sub(r"\s", "", alt)) > len(re.sub(r"\s", "", text)):
            text = alt
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, out)
    return sha, pno, "ok"


def page_count(path: str) -> int:
    import pymupdf

    with pymupdf.open(path) as d:
        return d.page_count


def run_ocr(recs: list[dict], workers: int) -> None:
    tasks, meta = [], {}
    for r in recs:
        path = os.path.join(ROOT, r["local_path"])
        if not os.path.exists(path):
            print(f"[ocr] missing file (re-download it): {r['title'][:60]}", file=sys.stderr)
            continue
        n = page_count(path)
        meta[r["sha256"]] = n
        os.makedirs(os.path.join(OCR_DIR, r["sha256"]), exist_ok=True)
        for p in range(n):
            if not os.path.exists(os.path.join(OCR_DIR, r["sha256"], f"p{p + 1:04d}.txt")):
                tasks.append((r["sha256"], path, p))
    # keep one document's pages together so a worker reuses its open PDF
    tasks.sort(key=lambda t: (t[1], t[2]))
    total = len(tasks)
    print(f"[ocr] {len(meta)} documents, {sum(meta.values())} pages, {total} still to do", file=sys.stderr)
    t0, done = time.time(), 0
    with ProcessPoolExecutor(workers) as pool:
        for _sha, _p, _st in pool.map(_ocr_page, tasks, chunksize=4):
            done += 1
            if done % 25 == 0 or done == total:
                el = time.time() - t0
                print(f"[ocr] {done}/{total} pages, {el:.0f}s, eta {el / done * (total - done):.0f}s", file=sys.stderr, flush=True)
    for sha, n in meta.items():
        json.dump({"n_pages": n, "dpi": DPI, "lang": LANG}, open(os.path.join(OCR_DIR, sha, "meta.json"), "w"))


def load_raw_pages(sha: str) -> list[str] | None:
    d = os.path.join(OCR_DIR, sha)
    mp = os.path.join(d, "meta.json")
    if not os.path.exists(mp):
        return None
    n = json.load(open(mp))["n_pages"]
    pages = []
    for p in range(n):
        f = os.path.join(d, f"p{p + 1:04d}.txt")
        pages.append(open(f, encoding="utf-8").read() if os.path.exists(f) else "")
    return pages


# --------------------------------------------------------------------------
# vocabularies for the quality gate: real words seen in the existing corpus
# --------------------------------------------------------------------------
def build_vocabs(min_count: int = 3) -> tuple[set[str], set[str]]:
    """Nepali: folded Devanagari words seen >= min_count times in the corpus' clean text
    layers (laws, precedents, text-layer regulator documents; part-003 itself excluded).
    English: Latin words seen >= min_count times in the corpus' English text + the
    extractor's function-word list. Cached."""
    if os.path.exists(VOCAB_PATH):
        d = json.load(open(VOCAB_PATH, encoding="utf-8"))
        return set(d["ne"]), set(d["en"])
    ne_c: Counter = Counter()
    en_c: Counter = Counter()
    manifest = json.load(open(os.path.join(I.CORPUS_DIR, "manifest.json"), encoding="utf-8"))
    for name in manifest["files"]:
        if name == SHARD_NAME:
            continue
        with gzip.open(os.path.join(I.CORPUS_DIR, name), "rt", encoding="utf-8") as f:
            for line in f:
                e = json.loads(line)
                if e.get("ocr"):
                    continue
                ne_c.update(C.DEV_WORD_RE.findall(fold(" ".join([e.get("doc_title_ne") or "", e.get("text_ne") or ""]))))
                en_c.update(w.lower() for w in C.LATIN_WORD_RE.findall(" ".join([e.get("text_en") or "", e.get("doc_title_en") or ""])))
    ne = {w for w, n in ne_c.items() if n >= min_count}
    en = {w for w, n in en_c.items() if n >= min_count} | {w for w in I.X.EN_FUNCTION_WORDS if len(w) >= 3}
    os.makedirs(os.path.dirname(VOCAB_PATH), exist_ok=True)
    json.dump({"ne": sorted(ne), "en": sorted(en)}, open(VOCAB_PATH, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[ocr] vocabularies: {len(ne)} Nepali, {len(en)} English words", file=sys.stderr)
    return ne, en


# --------------------------------------------------------------------------
# ingest
# --------------------------------------------------------------------------
def _existing_docs() -> list[dict]:
    """Documents part-002 already carries (from yesterday's ingest report): used to
    recognise instruments whose text layer is already in the corpus."""
    rep = json.load(open(I.FLAT_REPORT, encoding="utf-8"))
    return rep.get("documents", [])


def make_ex(pages: list[str]) -> dict:
    joined = "".join(pages)
    dev = len(re.findall(r"[ऀ-ॿ]", joined))
    lat = len(re.findall(r"[A-Za-z]", joined))
    return {"pages": pages, "devanagari_share": round(dev / max(1, dev + lat), 3), "n_pages": len(pages)}


def write_ocr_shard(entries: list[dict]) -> int:
    path = os.path.join(I.CORPUS_DIR, SHARD_NAME)
    with gzip.open(path, "wt", encoding="utf-8", compresslevel=9) as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return os.path.getsize(path)


def cmd_ingest(args) -> None:
    I.ensure_vocab()
    I.X._vocab = None
    ne, en = build_vocabs()
    recs = [(r, None) for r in needs_ocr_records()]           # scanned: pages come from the OCR cache
    new = classify_new(new_authority_records())                 # NIA / MoLESS: text layer or scanned
    recs += [(r, None if ex.get("needs_ocr") else ex) for r, ex in new if not ex.get("error")]
    new_errors = [f"[{r['authority']}] {r['title']}: {ex['error']}" for r, ex in new if ex.get("error")]
    from app.retrieval import _text_key

    # every other shard (a re-run must not see its own previous output as "already in the corpus")
    existing_keys: set[int] = set()
    m = json.load(open(os.path.join(I.CORPUS_DIR, "manifest.json"), encoding="utf-8"))
    for name in m["files"]:
        if name == SHARD_NAME:
            continue
        with gzip.open(os.path.join(I.CORPUS_DIR, name), "rt", encoding="utf-8") as f:
            for line in f:
                existing_keys.add(_text_key(json.loads(line)))

    skipped: dict[str, list[str]] = {}
    per_authority: dict[str, dict] = {}

    def tally(auth, key, n=1):
        per_authority.setdefault(auth, Counter())[key] += n

    exclude = re.compile(args.exclude) if args.exclude else None
    held_years: dict[tuple, int] = {}   # (authority, series) -> year of the edition the corpus already holds
    candidates = []
    doc_reports = []
    for rec, text_ex in recs:
        auth = rec["authority"]
        title = I.clean_title(rec["title"])
        tag = f"[{auth}] {title}"
        if text_ex is None:
            tally(auth, "needs_ocr")
            raw = load_raw_pages(rec["sha256"])
            if raw is None:
                skipped.setdefault("not_ocrd", []).append(tag)
                continue
            pages = C.clean_document(raw, en)
            verdict = C.document_verdict(pages, ne, en)
            doc_reports.append({"authority": auth, "title": title, "sha": rec["sha256"][:10], "pages": len(pages),
                                "rate": verdict["rate"], "kept_share": verdict["kept_share"], "keep": verdict["keep"],
                                "reason": verdict["reason"], "dropped_pages": verdict["dropped_pages"]})
            if not verdict["keep"]:
                skipped.setdefault("dropped_quality", []).append(f"{tag}: {verdict['reason']}")
                tally(auth, "dropped_quality")
                continue
            tally(auth, "ocr_ok")
            kept = [p for p in verdict["pages"] if p]  # unreadable pages are left out, not fed to the chunker
            ex = make_ex(kept)
            ex["ocr"] = True
        else:
            tally(auth, "text_layer")
            ex = text_ex
            ex["ocr"] = False
        if (exclude and exclude.search(title)) or I.LOW_VALUE_TITLE.search(title) or LOW_VALUE_EXTRA.search(title):
            skipped.setdefault("low_value", []).append(tag)
            tally(auth, "dropped_low_value")
        elif any(rx.search(title) and S.in_corpus(ne_title) for rx, ne_title in EN_ALIASES):
            skipped.setdefault("duplicate_of_corpus", []).append(f"{tag} (English title of an instrument already in the corpus)")
            tally(auth, "dropped_duplicate")
            held_years[(auth, series_key(title))] = max(title_year(title), held_years.get((auth, series_key(title)), 0))
        elif I.superseded(rec, title):
            skipped.setdefault("superseded", []).append(tag)
            tally(auth, "dropped_superseded")
        elif rec.get("doc_type") in ("act", "rule") and rec["authority"] != "ird" and (
                S.in_corpus(title) or S.in_corpus(re.sub(r"\([^)]*\)", " ", title))):
            skipped.setdefault("duplicate_of_corpus", []).append(f"{tag} (title already in corpus)")
            tally(auth, "dropped_duplicate")
        else:
            candidates.append((rec, ex, title))

    # editions: of the OCR'd editions of one instrument keep the newest consolidated one, and
    # none at all when part-002 already carries a consolidated text-layer edition of that series
    groups: dict[tuple, list] = {}
    for c in candidates:
        if c[0].get("kind") in ("act", "regulation", "directive", "guideline"):
            groups.setdefault((c[0]["authority"], series_key(c[2])), []).append(c)
        elif c[0].get("kind") == "circular" and I.CONSOLIDATED_ISSUE.search(c[2]):
            key = " ".join(re.sub(r"[०-९0-9/–\-]+", " ", c[2]).split())
            groups.setdefault((c[0]["authority"], "issue:" + key), []).append(c)
    have: dict[tuple, dict] = {}
    for d in _existing_docs():
        if d.get("kind") in ("act", "regulation", "directive", "guideline"):
            have.setdefault((d["authority"], series_key(d["title"])), d)
    drop = set()
    for key, g in groups.items():
        held = held_years.get(key, 0)
        if held:  # the corpus holds a newer edition of this instrument: these are repealed/older texts
            for c in [c for c in g if title_year(c[2]) < held]:
                drop.add(id(c))
                skipped.setdefault("older_edition", []).append(f"[{c[0]['authority']}] {c[2]} (corpus has the {held} edition)")
                tally(c[0]["authority"], "dropped_edition")
            g = [c for c in g if id(c) not in drop]
            if not g:
                continue
        if key in have and not I.AMENDING_ONLY.search(have[key]["title"]):
            for c in g:
                drop.add(id(c))
                skipped.setdefault("older_or_dup_edition_in_part002", []).append(f"[{c[0]['authority']}] {c[2]} (have: {have[key]['title'][:60]})")
                tally(c[0]["authority"], "dropped_edition")
            continue

        def rank(c):
            amending_only = bool(I.AMENDING_ONLY.search(c[2])) and "सहित" not in c[2]
            return (not amending_only, title_year(c[2]), c[0].get("lang") != "en", S.pub_sort_key(c[0].get("published")))

        best = max(g, key=rank)
        for c in g:
            if c is not best:
                drop.add(id(c))
                skipped.setdefault("older_edition", []).append(f"[{c[0]['authority']}] {c[2]}")
                tally(c[0]["authority"], "dropped_edition")
    # an ordinance (अध्यादेश) lapses into the Act that replaces it: keep the Act only
    act_titles = {c[2] for c in candidates if id(c) not in drop}
    for c in candidates:
        if id(c) not in drop and "अध्यादेश" in c[2] and c[2].replace("अध्यादेश", "ऐन") in act_titles:
            drop.add(id(c))
            skipped.setdefault("superseded", []).append(f"[{c[0]['authority']}] {c[2]} (replaced by the Act)")
            tally(c[0]["authority"], "dropped_superseded")
    candidates = [c for c in candidates if id(c) not in drop]

    entries: list[dict] = []
    per_doc = []
    seen_keys: set[int] = set()
    nepali_done: set[str] = set()
    for rec, ex, title in sorted(candidates, key=lambda c: c[0].get("lang") == "en"):
        if rec.get("lang") == "en" and title in nepali_done:
            skipped.setdefault("translation_of_ingested_original", []).append(f"[{rec['authority']}] {title}")
            tally(rec["authority"], "dropped_translation")
            continue
        es, st = I.build_entries(rec, ex, existing_keys, seen_keys)
        if ex.get("ocr"):
            tables = [e for e in es if C.is_table_noise(e["text_ne"] or e["text_en"])]
            if tables:
                es = [e for e in es if e not in tables]
                tally(rec["authority"], "table_chunks_dropped", len(tables))
        if not es:
            skipped.setdefault("duplicate_or_empty", []).append(f"[{rec['authority']}] {title}")
            tally(rec["authority"], "dropped_duplicate")
            continue
        if ex.get("ocr"):
            for e in es:
                e["ocr"] = True
        entries += es
        if rec.get("lang") != "en":
            nepali_done.add(title)
        per_doc.append({"authority": rec["authority"], "title": title, "kind": rec.get("kind"), "chunks": len(es),
                        "status": st["status"], "lang": st["lang"], "sha": rec["sha256"][:10], "published": rec.get("published")})
        tally(rec["authority"], "chunks", len(es))
        tally(rec["authority"], "documents_ingested")

    if args.profile == "core":
        def core(d):
            return (d["status"] == "in_force" or d["kind"] in ("act", "regulation", "circular")
                    or d["authority"] in I.CORE_AUTHORITIES or bool(d["authority"] == "moless" and LABOUR_CORE.search(d["title"])))
        dropped = [d for d in per_doc if not core(d)]
        skipped["profile_core_dropped"] = [f"[{d['authority']}] {d['title']} ({d['chunks']} chunks)" for d in dropped]
        gone = {d["sha"] for d in dropped}
        for d in dropped:
            tally(d["authority"], "chunks", -d["chunks"])
            tally(d["authority"], "documents_ingested", -1)
            tally(d["authority"], "dropped_profile")
        entries = [e for e in entries if e["doc_id"] not in gone]
        per_doc = [d for d in per_doc if d["sha"] not in gone]

    if args.max_chunks and len(entries) > args.max_chunks:
        rank = lambda d: (d["status"] == "in_force", d["kind"] in ("act", "regulation"), d["authority"] in ("ird", "nrb", "sebon", "ocr"), -d["chunks"])  # noqa: E731
        keep, total = set(), 0
        for d in sorted(per_doc, key=rank, reverse=True):
            if total + d["chunks"] <= args.max_chunks:
                keep.add(d["sha"])
                total += d["chunks"]
        entries = [e for e in entries if e["doc_id"] in keep]
        per_doc = [d for d in per_doc if d["sha"] in keep]

    if new_errors:
        skipped["extract_error"] = new_errors
    report = {"by_authority": {a: dict(c) for a, c in per_authority.items()}, "total_chunks": len(entries),
              "total_documents": len(per_doc), "skipped": skipped, "documents": per_doc, "ocr_quality": doc_reports}
    print(json.dumps({"by_authority": report["by_authority"], "total_chunks": len(entries), "total_documents": len(per_doc)},
                     ensure_ascii=False, indent=1))
    for k, v in skipped.items():
        print(f"[ocr-ingest] {k}: {len(v)}")
    if args.dry_run:
        if args.report_out:
            with open(args.report_out, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=1)
        return
    size = write_ocr_shard(entries)
    m = I.update_manifest(entries, shard=SHARD_NAME, count_keys=("regulator2_chunks", "regulator2_documents"))
    ocr_es = [e for e in entries if e.get("ocr")]
    m["counts"]["ocr_chunks"] = len(ocr_es)
    m["counts"]["ocr_documents"] = len({e["doc_id"] for e in ocr_es})
    with open(os.path.join(I.CORPUS_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
    report["shard_bytes"] = size
    report["manifest_counts"] = m["counts"]
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"[ocr-ingest] wrote {SHARD_NAME}: {len(entries)} chunks / {len(per_doc)} docs, {size / 1e6:.1f} MB; digest {m['digest']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["targets", "ocr", "ingest"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--exclude", default="", help="regex on document title: leave matching documents out")
    ap.add_argument("--profile", choices=["core", "full"], default="core")
    ap.add_argument("--max-chunks", type=int, default=0)
    ap.add_argument("--report-out", default="", help="with --dry-run: write the full report JSON here")
    args = ap.parse_args()
    if args.command == "targets":
        for r in all_ocr_records():
            have = os.path.exists(os.path.join(ROOT, r["local_path"]))
            print(f"{r['authority']:8} {r['size'] >> 10:6} KB {'on disk' if have else 'MISSING'}  {r['title'][:80]}")
    elif args.command == "ocr":
        run_ocr(all_ocr_records(), args.workers)
    else:
        cmd_ingest(args)


if __name__ == "__main__":
    main()
