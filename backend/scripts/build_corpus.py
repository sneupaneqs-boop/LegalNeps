"""
Builds the app's searchable corpus from government sources only:

  - sources/processed/law_docs.jsonl  (lawcommission.gov.np PDFs, section chunks)
  - sources/nkp/cases.jsonl           (Supreme Court precedents, nkp.gov.np)
  - backend/app/data/corpus.json      (hand-verified bilingual entries extracted
                                       earlier from lawcommission.gov.np PDFs;
                                       illustrative non-government demo entries
                                       are dropped)

Output: backend/app/data/corpus/*.jsonl.gz shards (each < 40 MB so they fit
in git), plus manifest.json with counts. Document titles are translated to
English once via Gemini (cached in sources/processed/title_en.json) when
GEMINI_API_KEY is set; otherwise English titles are left empty.

    python3 backend/scripts/build_corpus.py
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "backend"))
from app.doc_meta import classify_status, extract_doc_meta  # noqa: E402

LAW_DOCS = os.path.join(ROOT, "sources", "processed", "law_docs.jsonl")
NKP_CASES = os.path.join(ROOT, "sources", "nkp", "cases.jsonl")
CURATED = os.path.join(ROOT, "backend", "app", "data", "corpus.json")
OUT_DIR = os.path.join(ROOT, "backend", "app", "data", "corpus")
TITLE_CACHE = os.path.join(ROOT, "sources", "processed", "title_en.json")
SHARD_BYTES = 38 * 1024 * 1024

GOV_HOSTS = ("lawcommission.gov.np", "giwmscdnone.gov.np", "nkp.gov.np", "supremecourt.gov.np")
DROP_CURATED_PREFIXES = ("civil-", "precedent-")  # illustrative, not from an official source

DOC_TYPE_EN = {
    "constitution": "Constitution", "act": "Act", "rule": "Regulation", "order": "Formation Order",
    "directive": "Directive/Procedure", "gazette": "Gazette", "amendment": "Amendment",
    "treaty": "Treaty", "precedent": "Supreme Court precedent", "other": "Law Commission publication",
}
DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def _is_gov(url: str | None) -> bool:
    return bool(url) and any(h in url for h in GOV_HOSTS)


def _doc_type(rec: dict) -> str:
    t = rec.get("title") or ""
    if "संविधान" in t and "संशोधन" not in t[:12]:
        return "constitution"
    if re.search(r"नियमावली|नियमहरू|नियमहरु", t):
        return "rule"
    if re.search(r"संहिता|ऐन|अध्यादेश|विधेयक", t):
        return "act"
    if "आदेश" in t:
        return "order"
    if re.search(r"निर्देशिका|कार्यविधि|मापदण्ड", t):
        return "directive"
    if re.search(r"सन्धि|महासन्धि|प्रोटोकल|सम्झौता", t):
        return "treaty"
    return rec.get("category") or "other"


def _title_from_text(doc: dict) -> str | None:
    """First substantial Devanagari line of the document (its printed title)."""
    for ch in doc.get("chunks", [])[:2]:
        for line in ch["text"].split("\n"):
            line = line.strip(" -–:")
            if 8 <= len(line) <= 90 and re.search(r"[\u0900-\u097F]{3}", line) and not re.match(r"^[०-९0-9(]", line):
                return line
    return None


def translate_titles(titles: list[str]) -> dict[str, str]:
    cache = json.load(open(TITLE_CACHE, encoding="utf-8")) if os.path.exists(TITLE_CACHE) else {}
    todo = [t for t in dict.fromkeys(titles) if t and t not in cache]
    key = os.environ.get("GEMINI_API_KEY")
    if not todo or not key:
        return cache
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    models = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"]
    for i in range(0, len(todo), 60):
        batch = todo[i:i + 60]
        prompt = (
            "Translate these official Nepali legal document titles to their standard English "
            "titles as used by the Nepal Law Commission (e.g. 'मुलुकी देवानी संहिता, २०७४' -> "
            "'The Muluki Civil Code, 2074'). Keep Bikram Sambat years as Western digits. "
            "Return a JSON object mapping each input title exactly to its English title.\n\n"
            + json.dumps(batch, ensure_ascii=False)
        )
        for m in models:
            try:
                r = client.models.generate_content(
                    model=m, contents=prompt,
                    config=types.GenerateContentConfig(temperature=0, response_mime_type="application/json"),
                )
                out = json.loads(r.text)
                cache.update({k: v for k, v in out.items() if isinstance(v, str)})
                break
            except Exception as e:  # noqa: BLE001
                print(f"[titles] {m} failed: {str(e)[:120]}", file=sys.stderr)
                time.sleep(4)
        with open(TITLE_CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=0)
        print(f"[titles] {min(i + 60, len(todo))}/{len(todo)}", file=sys.stderr)
    return cache


def law_entries(title_en: dict[str, str]) -> list[dict]:
    out = []
    if not os.path.exists(LAW_DOCS):
        return out
    seen_titles: dict[str, str] = {}
    for line in open(LAW_DOCS, encoding="utf-8"):
        doc = json.loads(line)
        if doc.get("error") or not doc.get("chunks") or not _is_gov(doc.get("url")):
            continue
        title = (doc.get("title") or "").strip()
        if not title or title in ("डाउनलोड", "Download", "यहाँ क्लिक गर्नुहोस्"):
            title = _title_from_text(doc) or os.path.splitext(os.path.basename(doc["local_path"]))[0].replace("_", " ")
        # the same act is often linked from several listing pages with
        # different files; keep the first (listing tables come first)
        norm = re.sub(r"\s+", " ", title)
        if norm in seen_titles and seen_titles[norm] != doc["sha256"]:
            continue
        seen_titles[norm] = doc["sha256"]
        dtype = _doc_type(doc)
        t_en = title_en.get(title, "")
        short = doc["sha256"][:10]
        # status/dates come from the first chunk (header + preamble); every
        # chunk of the document carries the same doc-level metadata
        doc_meta = extract_doc_meta(doc["chunks"][0]["text"]) if doc["chunks"] else {}
        status = classify_status(title, doc_meta)
        for i, ch in enumerate(doc["chunks"]):
            sec = ch.get("section")
            head = ch.get("heading") or ""
            label_ne = {"constitution": "धारा", "rule": "नियम"}.get(dtype, "दफा")
            label_en = {"constitution": "Article", "rule": "Rule"}.get(dtype, "Section")
            is_num = bool(sec) and bool(re.match(r"^\d", sec))
            source_ne = f"{title}" + (f", {label_ne} {sec}" if is_num else "")
            source_en = (t_en or title) + (f", {label_en} {sec}" if is_num else "")
            out.append({
                "id": f"law-{short}-{i}",
                "category": "law",
                "doc_type": dtype,
                "topic": DOC_TYPE_EN.get(dtype, "Law"),
                "doc_title_ne": title,
                "doc_title_en": t_en,
                "section": sec,
                "title_ne": f"{head} ({title})" if head else title,
                "title_en": t_en,
                "text_ne": ch["text"],
                "text_en": "",
                "source_ne": source_ne,
                "source_en": source_en,
                "url": doc["url"] + (f"#page={ch['page']}" if ch.get("page") else ""),
                "doc_id": short,
                "provision_id": f"{short}:{sec}" if sec else short,
                "status": status,
                "enacted_bs": doc_meta.get("enacted_bs"),
                "amended_by": doc_meta.get("amended_by") or [],
                "consolidated_upto": doc_meta.get("consolidated_upto"),
            })
    return out


def precedent_entries() -> list[dict]:
    out = []
    if not os.path.exists(NKP_CASES):
        return out
    latest: dict[int, dict] = {}
    for line in open(NKP_CASES, encoding="utf-8"):
        c = json.loads(line)
        latest[c["nkp_id"]] = c  # re-fetched records supersede older ones
    for c in latest.values():
        body = c.get("headnote") or ""
        if len(body) < 40:
            body = c.get("conclusion") or ""
        if len(body) < 40:
            body = c.get("body_excerpt") or ""
        if len(body) < 40:
            continue
        laws = "; ".join(c.get("related_laws") or [])
        text = body + (f"\nसम्बद्ध कानून: {laws}" if laws else "")
        cite_ne = "ने.का.प. " + " ".join(x for x in [
            c.get("year") or "", f"अंक {c['issue']}" if c.get("issue") else "",
            f"नि.नं. {c['decision_no']}" if c.get("decision_no") else "",
        ] if x)
        dn = (c.get("decision_no") or "").translate(DEV_DIGITS)
        yr = (c.get("year") or "").translate(DEV_DIGITS)
        out.append({
            "id": f"nkp-{c['nkp_id']}",
            "category": "precedent",
            "doc_type": "precedent",
            "topic": c.get("subject") or "Supreme Court precedent",
            "doc_title_ne": c["title"],
            "doc_title_en": "",
            "section": None,
            "title_ne": f"{c['title']} ({c.get('bench') or 'सर्वोच्च अदालत'})",
            "title_en": f"Supreme Court of Nepal, Decision No. {dn} (NKP {yr})",
            "text_ne": text,
            "text_en": "",
            "source_ne": cite_ne,
            "source_en": f"Nepal Kanoon Patrika {yr}, Decision No. {dn}",
            "url": c["url"],
            "year": yr,
            "decided_on": c.get("decided_on"),
        })
    return out


def curated_entries() -> list[dict]:
    out = []
    for e in json.load(open(CURATED, encoding="utf-8")):
        if e["id"].startswith(DROP_CURATED_PREFIXES):
            continue
        e = dict(e)
        e.setdefault("doc_type", "constitution" if e["id"].startswith("constitution") else "other")
        e.setdefault("url", "https://lawcommission.gov.np/")
        e.setdefault("section", None)
        # hand-verified entries are almost all real, in-force provisions, but
        # a few (e.g. the 2083 finance bills in sources/*.pdf) are drafts
        # ingested for reference before passage - curated entries have no
        # doc_title_ne/preamble to run classify_status() on, so catch "विधेयक"
        # in any title/citation field the entry carries (it may only be in
        # source_ne, not title_ne - e.g. title_ne "राष्ट्र ऋण उठाउन सक्ने" vs.
        # source_ne "राष्ट्र ऋण उठाउने विधेयक, २०८३" for the same entry)
        names = (e.get("doc_title_ne"), e.get("title_ne"), e.get("source_ne"))
        e.setdefault("status", "bill" if any(n and "विधेयक" in n for n in names) else "in_force")
        e["curated"] = True
        out.append(e)
    return out


def merge_constitution_translations(curated: list[dict], laws: list[dict]) -> list[dict]:
    """Earlier hand-verified constitution-art-N entries carry English
    translations; attach them to the matching official chunk (first chunk
    of that Article) instead of keeping near-duplicate entries."""
    first_chunk: dict[str, dict] = {}
    for e in laws:
        if e["doc_type"] == "constitution" and e.get("section") and e["doc_title_ne"].startswith("नेपालको संविधान"):
            art = e["section"].split()[0]
            first_chunk.setdefault(art, e)
    kept, seen_text = [], set()
    for c in curated:
        key = re.sub(r"\s+", " ", c.get("text_ne", ""))[:200]
        if key in seen_text:
            continue  # exact duplicate curated entry
        seen_text.add(key)
        m = re.match(r"constitution-art-(\d+)$", c["id"]) or re.match(r"constitution-art-(\d+)-\d+$", c["id"])
        target = first_chunk.get(m.group(1)) if m else None
        if target is not None and c.get("text_en"):
            if not target.get("text_en"):
                target["text_en"] = c["text_en"]
                target["title_en"] = c.get("title_en") or target.get("title_en")
                target["source_en"] = c.get("source_en") or target["source_en"]
            continue
        kept.append(c)
    return kept


def write_shards(entries: list[dict]):
    os.makedirs(OUT_DIR, exist_ok=True)
    for f in os.listdir(OUT_DIR):
        if f.endswith(".jsonl.gz"):
            os.remove(os.path.join(OUT_DIR, f))
    shard, size, n = [], 0, 0
    files = []

    def flush():
        nonlocal shard, size, n
        if not shard:
            return
        name = f"part-{n:03d}.jsonl.gz"
        with gzip.open(os.path.join(OUT_DIR, name), "wt", encoding="utf-8", compresslevel=9) as f:
            f.writelines(shard)
        files.append(name)
        shard, size, n = [], 0, n + 1

    for e in entries:
        line = json.dumps(e, ensure_ascii=False) + "\n"
        shard.append(line)
        size += len(line.encode("utf-8")) // 4  # ~4x gzip ratio on Devanagari
        if size >= SHARD_BYTES:
            flush()
    flush()
    return files


def main():
    law_titles = []
    if os.path.exists(LAW_DOCS):
        for line in open(LAW_DOCS, encoding="utf-8"):
            d = json.loads(line)
            if d.get("title"):
                law_titles.append(d["title"].strip())
    title_en = translate_titles(law_titles)

    curated = curated_entries()
    laws = law_entries(title_en)
    curated = merge_constitution_translations(curated, laws)
    precedents = precedent_entries()
    entries = curated + laws + precedents
    files = write_shards(entries)
    digest = hashlib.sha256("".join(e["id"] for e in entries).encode()).hexdigest()[:16]
    manifest = {
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "counts": {"curated": len(curated), "law_chunks": len(laws), "precedents": len(precedents),
                   "total": len(entries), "law_documents": len({e["doc_title_ne"] for e in laws})},
        "files": files,
        "digest": digest,
    }
    with open(os.path.join(OUT_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
