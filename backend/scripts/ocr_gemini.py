"""
OCR for documents extract_laws.py flagged `needs_ocr` (scanned PDFs, or
text layers that aren't real Nepali). Pages are rendered to images and
transcribed by Gemini vision a few at a time; results are cached per PDF
sha256 in sources/processed/ocr/<sha>.json and picked up automatically by
extract_laws.py on its next run.

    GEMINI_API_KEY=... python3 backend/scripts/ocr_gemini.py [--max-docs N]

Paced for free-tier limits and rotates models on 429/503. Resumable.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(ROOT, "sources", "processed", "law_docs.jsonl")
OCR_DIR = os.path.join(ROOT, "sources", "processed", "ocr")
MODELS = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.1-flash-lite", "gemini-3.5-flash-lite"]
PAGES_PER_CALL = 3

PROMPT = """Transcribe these scanned pages of an official Nepali legal document exactly, in \
Unicode (Devanagari for Nepali, Latin for English). Keep section/rule numbers, headings, \
sub-clauses (क) (ख) and line order. Do not translate, summarise or add anything. Skip page \
headers/footers and page numbers. Separate pages with a line "=== PAGE ===". If a page is blank, \
output "=== PAGE ===" followed by nothing."""


def render(doc, pno: int) -> bytes:
    import pymupdf

    pix = doc[pno].get_pixmap(dpi=150, colorspace=pymupdf.csGRAY)
    return pix.tobytes("jpeg", jpg_quality=80)


def transcribe(client, images: list[bytes], cooldown: dict) -> str | None:
    from google.genai import types

    parts = [types.Part.from_bytes(data=img, mime_type="image/jpeg") for img in images] + [PROMPT]
    for model in MODELS:
        if cooldown.get(model, 0) > time.time():
            continue
        try:
            r = client.models.generate_content(
                model=model, contents=parts,
                config=types.GenerateContentConfig(temperature=0, max_output_tokens=16000),
            )
            return r.text or ""
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            wait = 65 if ("429" in msg or "RESOURCE_EXHAUSTED" in msg) else 25
            cooldown[model] = time.time() + (3600 if "PerDay" in msg else wait)
            print(f"[ocr] {model}: {msg[:90]}", file=sys.stderr)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-docs", type=int, default=0)
    ap.add_argument("--max-pages", type=int, default=120, help="skip very long scans")
    args = ap.parse_args()

    import pymupdf
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    os.makedirs(OCR_DIR, exist_ok=True)
    cooldown: dict[str, float] = {}
    todo = [json.loads(l) for l in open(DOCS, encoding="utf-8")]
    todo = [d for d in todo if d.get("needs_ocr") and not os.path.exists(os.path.join(OCR_DIR, d["sha256"] + ".json"))]
    if args.max_docs:
        todo = todo[: args.max_docs]
    print(f"[ocr] {len(todo)} documents to transcribe", file=sys.stderr)

    for d in todo:
        path = os.path.join(ROOT, d["local_path"])
        doc = pymupdf.open(path)
        if len(doc) > args.max_pages:
            print(f"[ocr] skip {d.get('title')}: {len(doc)} pages", file=sys.stderr)
            continue
        partial = os.path.join(OCR_DIR, d["sha256"] + ".partial.json")
        pages: list[str] = json.load(open(partial, encoding="utf-8")) if os.path.exists(partial) else []
        start = len(pages)
        while start < len(doc):
            idx = list(range(start, min(start + PAGES_PER_CALL, len(doc))))
            text = None
            for _ in range(20):
                text = transcribe(client, [render(doc, i) for i in idx], cooldown)
                if text is not None:
                    break
                time.sleep(max(5, min(cooldown.values(), default=time.time() + 10) - time.time()))
            if text is None:
                print(f"[ocr] giving up on {d.get('title')} at page {start + 1}", file=sys.stderr)
                break
            got = [p.strip() for p in text.split("=== PAGE ===")]
            if got and not got[0]:
                got = got[1:]  # output usually starts with the marker
            if len(got) < len(idx):
                got += [""] * (len(idx) - len(got))
            elif len(got) > len(idx):
                got = got[: len(idx) - 1] + ["\n".join(got[len(idx) - 1:])]
            pages.extend(got)
            json.dump(pages, open(partial, "w", encoding="utf-8"), ensure_ascii=False)
            start += len(idx)
            time.sleep(4.5)  # ~13 requests/minute across the rotation
        if len(pages) >= len(doc):
            with open(os.path.join(OCR_DIR, d["sha256"] + ".json"), "w", encoding="utf-8") as f:
                json.dump({"title": d.get("title"), "pages": pages, "model_ocr": True}, f, ensure_ascii=False)
            os.remove(partial)
            print(f"[ocr] done {d.get('title')} ({len(pages)} pages)", file=sys.stderr)


if __name__ == "__main__":
    main()
