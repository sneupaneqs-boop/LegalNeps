"""
Scrapes Supreme Court of Nepal precedents from the official Nepal Kanoon
Patrika site (nkp.gov.np). Every decision lives at /full_detail/<id> as
Unicode HTML, so no OCR/LLM is needed: we parse the headnote (the court's
own summary of the legal principle, marked "(प्रकरण नं.N)"), metadata, the
laws it applied and the precedents it relied on.

    python3 backend/scripts/scrape_nkp.py                 # ids 1..11000
    python3 backend/scripts/scrape_nkp.py --start 9000 --end 9100

Output: sources/nkp/cases.jsonl (one JSON object per decision; resumable,
already-fetched ids are skipped on re-run).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "sources", "nkp")
OUT_PATH = os.path.join(OUT_DIR, "cases.jsonl")
BASE = "https://nkp.gov.np/full_detail/{}"
USER_AGENT = "KanooniSathiBot/1.0 (legal-research corpus builder; contact: s.neupaneqs@gmail.com)"

COUNSEL_RE = re.compile(r"^[^:ः]{0,40}तर्फबाट\s*[:ः]?\s*|^आदेश$|^फैसला$")
PARTY_RE = re.compile(r"^(पुनरावेदक|प्रत्यर्थी|निवेदक|विपक्षी|वादी|प्रतिवादी|रिट निवेदक|उजुरवाला|अपीलाण्ट|रेस्पोण्डेण्ट)")
PRAKARAN_RE = re.compile(r"^\(?\s*प्रकरण\s*नं")

_write_lock = threading.Lock()


def _lines(el) -> list[str]:
    return [l.strip() for l in el.get_text("\n", strip=True).split("\n") if l.strip()]


def _section_after(lines: list[str], label: str, stop_labels: tuple[str, ...]) -> list[str]:
    out, on = [], False
    for l in lines:
        if l.startswith(label):
            on = True
            rest = l[len(label):].strip(" :ः")
            if rest:
                out.append(rest)
            continue
        if on:
            if any(l.startswith(s) for s in stop_labels) or COUNSEL_RE.search(l):
                break
            out.append(l)
    return out


def parse(html: str, case_id: int) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1", class_="post-title")
    body = soup.find(id=lambda v: v and v.strip() == "faisala_detail")
    if not h1 or not body:
        return None
    title = h1.get_text(" ", strip=True)
    summary = soup.find(id="decision_summary")
    meta_text = summary.get_text(" ", strip=True) if summary else ""

    def meta(label):
        m = re.search(label + r"\s*:?\s*([^\s|]+)", meta_text)
        return m.group(1) if m else None

    lines = _lines(body)

    # Headnote = lines between the party block and the counsel block,
    # i.e. the court's own summarised holdings, each ending "(प्रकरण नं.N)".
    end = next((i for i, l in enumerate(lines[:80]) if COUNSEL_RE.search(l)), None)
    headnote_lines: list[str] = []
    if end is not None:
        start = 0
        for i in range(end):
            l = lines[i]
            if l.startswith("मुद्दा") or PARTY_RE.match(l) or l in ("विरुद्ध", "विरूद्ध"):
                start = i + 1
        headnote_lines = lines[start:end]
    headnote = " ".join(headnote_lines)
    headnote = re.sub(r"\s*\(\s*प्रकरण\s*नं\.?\s*([०-९0-9,\s]+)\)", r" (प्रकरण नं.\1)\n", headnote).strip()

    subject = next((l.split(":", 1)[-1].split("ः", 1)[-1].strip() for l in lines[:40] if l.startswith("मुद्दा")), "")
    bench = next((l for l in lines[:6] if "इजलास" in l or "बेञ्च" in l), "")
    judges = [l.replace("माननीय", "").strip() for l in lines[:12] if "न्यायाधीश" in l]
    decided = next((l.split(":", 1)[-1].strip() for l in lines[:12] if "फैसला मिति" in l or "आदेश मिति" in l), "")
    laws = _section_after(lines, "सम्बद्ध कानून", ("सुरू", "फैसला", "आदेश", "अवलम्बित"))
    cited = _section_after(lines, "अवलम्बित नजिर", ("सम्बद्ध", "सुरू", "फैसला", "आदेश"))

    # Tail of the judgment usually holds the operative conclusion ("ठहर्छ").
    full = "\n".join(lines)
    concl_idx = max(full.rfind("ठहर्छ"), full.rfind("ठहर्‍याई"), full.rfind("ठहर गर्छ"))
    conclusion = full[max(0, concl_idx - 900): concl_idx + 120].strip() if concl_idx > 0 else ""

    # Older decisions have no headnote: keep the opening of the judgment
    # (facts + issue) so they're still searchable.
    body_start = (end + 1) if end is not None else 0
    body_lines = [l for l in lines[body_start:] if not COUNSEL_RE.search(l) and not PARTY_RE.match(l)]
    body_excerpt = " ".join(body_lines)[:1600]

    m = re.search(r"निर्णय नं\.?\s*([०-९0-9]+)", title)
    return {
        "nkp_id": case_id,
        "url": BASE.format(case_id),
        "title": title,
        "decision_no": m.group(1) if m else None,
        "subject": subject,
        "volume": meta("भाग"),
        "year": meta("साल"),
        "month": meta("महिना"),
        "issue": meta("अंक"),
        "decided_on": decided,
        "bench": bench,
        "judges": judges[:5],
        "headnote": headnote,
        "related_laws": laws[:10],
        "cited_precedents": cited[:10],
        "conclusion": conclusion,
        "body_excerpt": body_excerpt,
        "full_text_chars": len(full),
    }


def fetch(session: requests.Session, case_id: int, retries: int = 4) -> str | None:
    for attempt in range(retries):
        try:
            r = session.get(BASE.format(case_id), timeout=40, allow_redirects=False)
            if r.status_code in (301, 302, 404):
                return None
            r.raise_for_status()
            r.encoding = "utf-8"
            return r.text
        except requests.RequestException as e:
            wait = 2 ** attempt * 2
            print(f"[nkp] {case_id} attempt {attempt+1} failed: {e}; retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=11000)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--delay", type=float, default=0.5, help="per-worker delay between requests")
    ap.add_argument("--refetch-thin", action="store_true", help="re-fetch decisions stored without any summary")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    done: set[int] = set()
    if os.path.exists(OUT_PATH):
        for line in open(OUT_PATH, encoding="utf-8"):
            try:
                done.add(json.loads(line)["nkp_id"])
            except Exception:  # noqa: BLE001
                pass
    missing_path = os.path.join(OUT_DIR, "missing_ids.json")
    missing: set[int] = set(json.load(open(missing_path))) if os.path.exists(missing_path) else set()

    if args.refetch_thin:
        # re-fetch decisions stored without a headnote/conclusion so the new
        # body_excerpt field gets filled; the corpus builder keeps the last copy
        thin = set()
        for line in open(OUT_PATH, encoding="utf-8"):
            c = json.loads(line)
            if len(c.get("headnote") or "") < 40 and len(c.get("conclusion") or "") < 40 and not c.get("body_excerpt"):
                thin.add(c["nkp_id"])
        done -= thin
        print(f"[nkp] re-fetching {len(thin)} decisions without a summary", file=sys.stderr)
    todo = [i for i in range(args.start, args.end + 1) if i not in done and i not in missing]
    print(f"[nkp] {len(done)} already fetched, {len(todo)} to go", file=sys.stderr)
    stats = {"ok": 0, "missing": 0, "parse_fail": 0}

    local = threading.local()

    def work(case_id: int):
        if not hasattr(local, "s"):
            local.s = requests.Session()
            local.s.headers["User-Agent"] = USER_AGENT
        html = fetch(local.s, case_id)
        time.sleep(args.delay)
        if html is None:
            stats["missing"] += 1
            missing.add(case_id)
            return
        try:
            rec = parse(html, case_id)
        except Exception as e:  # noqa: BLE001
            print(f"[nkp] parse error {case_id}: {e}", file=sys.stderr)
            rec = None
        if not rec:
            stats["parse_fail"] += 1
            return
        with _write_lock:
            with open(OUT_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            stats["ok"] += 1
            if stats["ok"] % 200 == 0:
                print(f"[nkp] {stats}", file=sys.stderr)
                json.dump(sorted(missing), open(missing_path, "w"))

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, todo))
    json.dump(sorted(missing), open(missing_path, "w"))
    print(f"[nkp] done {stats}", file=sys.stderr)


if __name__ == "__main__":
    main()
