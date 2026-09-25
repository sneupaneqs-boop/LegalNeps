"""
Step 2 of the scrape pipeline: turns documents downloaded by
scrape_lawcommission.py (recorded in sources/lawcommission/manifest.jsonl)
into bilingual corpus.json entries, the same way ingest_pdfs.py does for the
hand-picked seed PDFs — by having Gemini read each PDF *visually* (its
pages are rendered as images), which sidesteps the legacy, non-Unicode font
that corrupts naive text extraction from these documents. This works
equally well for genuinely scanned/image-only PDFs, so a separate OCR pass
is only needed if you want a searchable PDF file itself, not for this step.

Usage:
    GEMINI_API_KEY=... python3 scripts/ingest_scraped.py
    GEMINI_API_KEY=... python3 scripts/ingest_scraped.py --category act --limit 20
    GEMINI_API_KEY=... python3 scripts/ingest_scraped.py --resume-from sources/lawcommission/ingested.json

Progress is tracked in sources/lawcommission/ingested.json (list of manifest
URLs already processed) so the script is safe to stop and re-run; it will
skip anything already ingested and pick up where it left off.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from google import genai

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS_PATH = os.path.join(ROOT, "backend", "app", "data", "corpus.json")
MANIFEST_PATH = os.path.join(ROOT, "sources", "lawcommission", "manifest.jsonl")
INGESTED_PATH = os.path.join(ROOT, "sources", "lawcommission", "ingested.json")
MODEL = "gemini-3.1-flash-lite"

# manifest "category" tag -> corpus.json "category" field
CATEGORY_MAP = {
    "constitution": "law",
    "act": "law",
    "rule": "law",
    "order": "law",
    "directive": "law",
    "gazette": "law",
    "amendment": "law",
    "treaty": "law",
    "precedent": "precedent",
    "other": "law",
}

MAX_FILE_MB = 45  # Gemini file API practical limit for inline vision reading


def load_manifest():
    records = []
    if not os.path.exists(MANIFEST_PATH):
        return records
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_ingested() -> set[str]:
    if os.path.exists(INGESTED_PATH):
        with open(INGESTED_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_ingested(urls: set[str]):
    os.makedirs(os.path.dirname(INGESTED_PATH), exist_ok=True)
    with open(INGESTED_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(urls), f, ensure_ascii=False, indent=2)


def load_corpus():
    if not os.path.exists(CORPUS_PATH):
        return []
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_corpus(entries):
    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def slugify(text: str) -> str:
    import re
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return s[:60] or "doc"


def ask_json(client, file_ref, prompt: str, retries: int = 3):
    full_prompt = (
        prompt
        + "\n\nRespond with ONLY a JSON array (no markdown fences, no commentary). "
        "Each item must be a JSON object with exactly these string keys: "
        "id, topic, title_en, title_ne, text_en, text_ne, source_en, source_ne. "
        "If the document has no substantive legal content to extract (e.g. it is "
        "a blank cover page or duplicate), respond with an empty JSON array []."
    )
    last_err = None
    for attempt in range(retries):
        try:
            r = client.models.generate_content(
                model=MODEL,
                contents=[file_ref, full_prompt],
                config={"temperature": 0.1, "max_output_tokens": 8192},
            )
            text = (r.text or "").strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"    retry {attempt+1}/{retries} after error: {e}", file=sys.stderr)
            time.sleep(3)
    raise last_err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default=None, help="only ingest this manifest category (act, rule, ...)")
    ap.add_argument("--limit", type=int, default=None, help="max number of new documents to ingest this run")
    args = ap.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    client = genai.Client(api_key=api_key)

    records = load_manifest()
    if args.category:
        records = [r for r in records if r["category"] == args.category]
    ingested = load_ingested()
    corpus = load_corpus()
    existing_ids = {e["id"] for e in corpus}

    processed = 0
    for rec in records:
        if rec["url"] in ingested:
            continue
        if args.limit and processed >= args.limit:
            break

        path = os.path.join(ROOT, rec.get("ocr_path") or rec["local_path"])
        if not os.path.exists(path):
            print(f"SKIP missing file: {path}", file=sys.stderr)
            ingested.add(rec["url"])
            continue
        if os.path.getsize(path) > MAX_FILE_MB * 1024 * 1024:
            print(f"SKIP too large (>{MAX_FILE_MB}MB): {path}", file=sys.stderr)
            ingested.add(rec["url"])
            continue
        if not path.lower().endswith(".pdf"):
            print(f"SKIP non-PDF (add a converter first): {path}", file=sys.stderr)
            ingested.add(rec["url"])
            continue

        title = rec.get("title") or os.path.basename(path)
        print(f"-- [{rec['category']}] {title} ({rec['url']})")

        try:
            f = client.files.upload(file=path)
            while f.state.name == "PROCESSING":
                time.sleep(2)
                f = client.files.get(name=f.name)
            if f.state.name != "ACTIVE":
                raise RuntimeError(f"upload state {f.state}")

            corpus_category = CATEGORY_MAP.get(rec["category"], "law")
            prompt = (
                f"This PDF is a Nepali legal document titled '{title}' "
                f"(source: lawcommission.gov.np, category: {rec['category']}). "
                "Its embedded text layer may be garbled due to a legacy, non-Unicode "
                "font, or it may be a scanned image with no text layer at all - read "
                "the PDF VISUALLY page by page and transcribe correctly. "
                "Extract every substantively important provision/section (दफा/धारा) "
                "as a separate JSON object, skipping purely numeric schedules or "
                "blank/cover pages. For each: title_ne/title_en are the section "
                "heading, text_ne/text_en are its full text (accurate translation "
                f"between Nepali and English), source_en = '{title}' plus the "
                "section number/name, source_ne = the Nepali equivalent citation. "
                f"id should be like '{slugify(title)}-section-<N>'. "
                "If this is a court judgment/precedent instead of legislation, "
                "extract the case name, citation, and key legal holdings/ratio "
                "instead of sections."
            )
            entries = ask_json(client, f, prompt)
        except Exception as e:  # noqa: BLE001
            print(f"   FAILED: {e}", file=sys.stderr)
            continue  # leave out of `ingested` so it's retried next run

        added = 0
        for e in entries:
            e["category"] = corpus_category
            if e.get("id") in existing_ids or not e.get("id"):
                e["id"] = f"{slugify(title)}-{added}-{int(time.time())}"
            corpus.append(e)
            existing_ids.add(e["id"])
            added += 1
        print(f"   added {added} entries")

        ingested.add(rec["url"])
        processed += 1

        # persist incrementally so a crash/interrupt doesn't lose progress
        save_corpus(corpus)
        save_ingested(ingested)

    print(f"Done. Processed {processed} new documents this run. Corpus now has {len(corpus)} entries.")


if __name__ == "__main__":
    main()
