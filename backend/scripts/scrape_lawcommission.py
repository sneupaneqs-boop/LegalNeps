"""
Crawls lawcommission.gov.np (and, optionally, other Nepali legal-source
domains such as supremecourt.gov.np for precedents) and downloads every law,
rule/regulation, and other legal document it can find as a PDF/DOC/DOCX,
building a resumable manifest of what was found and fetched.

This is step 1 of a two-step pipeline:

    1. scrape_lawcommission.py   crawl + download raw documents -> sources/lawcommission/
    2. ingest_scraped.py         turn downloaded PDFs into corpus.json entries

Usage
-----
    python3 scripts/scrape_lawcommission.py crawl
    python3 scripts/scrape_lawcommission.py crawl --max-pages 5000 --delay 1.5
    python3 scripts/scrape_lawcommission.py ocr
    python3 scripts/scrape_lawcommission.py stats

Design notes
------------
- Polite by default: reads robots.txt, honors Crawl-delay, rate-limits
  requests, identifies itself with a real User-Agent + contact string.
- Resumable: every downloaded document is appended to a JSONL manifest
  immediately, keyed by URL. Re-running `crawl` skips URLs already present,
  so a killed/interrupted run can just be restarted.
- Domain-scoped BFS crawl (not a fixed sitemap) because government CMS
  navigation/URLs change over time and this way new sections get picked up
  automatically, at the cost of some noise (filtered by extension + link
  text heuristics).
- OCR step is separate and optional: most lawcommission.gov.np PDFs already
  carry a (possibly legacy-font-encoded, see README) text layer, so we only
  force OCR on documents that look like flat scanned images (no extractable
  text at all). It shells out to `ocrmypdf` if installed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.robotparser
from dataclasses import dataclass, field
from typing import Iterable
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OUT_DIR = os.path.join(ROOT, "sources", "lawcommission")
DEFAULT_MANIFEST = os.path.join(DEFAULT_OUT_DIR, "manifest.jsonl")

USER_AGENT = (
    "KanooniSathiBot/1.0 (+https://github.com/; legal-research corpus builder; "
    "contact: s.neupaneqs@gmail.com)"
)

DOC_EXTENSIONS = {".pdf", ".doc", ".docx"}

# Nepali/English keyword -> category tag, checked against link text and URL path.
CATEGORY_KEYWORDS = [
    ("constitution", ["संविधान", "constitution"]),
    ("act", ["ऐन", "act", "विधेयक", "bill"]),
    ("rule", ["नियमावली", "नियम", "regulation", "rule"]),
    ("order", ["आदेश", "order", "गठन आदेश"]),
    ("directive", ["निर्देशिका", "directive", "guideline", "कार्यविधि", "procedure"]),
    ("gazette", ["राजपत्र", "gazette"]),
    ("amendment", ["संशोधन", "amendment"]),
    ("treaty", ["सन्धि", "treaty", "convention"]),
    ("precedent", ["नेकाप", "nkp", "फैसला", "judgment", "judgement", "precedent", "मुद्दा"]),
]

SKIP_URL_PATTERNS = re.compile(
    r"(\.(jpg|jpeg|png|gif|svg|css|js|ico|woff2?|ttf|mp4|zip)(\?|$))|"
    r"(/user/login)|(/search\?)|(mailto:)|(tel:)|(javascript:)",
    re.IGNORECASE,
)


def classify(text: str) -> str:
    t = text.lower()
    for tag, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw.lower() in t:
                return tag
    return "other"


def _truncate_utf8_bytes(s: str, max_bytes: int) -> str:
    """Truncate to a byte budget without splitting a multi-byte character
    (Devanagari is 3 bytes/char in UTF-8, so a naive char-count limit can
    still overflow the filesystem's byte-based filename limit)."""
    b = s.encode("utf-8")
    if len(b) <= max_bytes:
        return s
    return b[:max_bytes].decode("utf-8", errors="ignore")


def safe_filename(url: str, title: str) -> str:
    ext = os.path.splitext(urlparse(url).path)[1].lower() or ".pdf"
    base = re.sub(r"[^\wऀ-ॿ\-.]+", "_", title.strip(), flags=re.UNICODE).strip("_")
    if not base:
        base = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    # keep total filename (base + ext) well under the common 255-byte limit
    base = _truncate_utf8_bytes(base, 200 - len(ext.encode("utf-8")))
    return f"{base}{ext}"


@dataclass
class Crawler:
    seeds: list[str]
    allowed_domains: set[str]
    out_dir: str = DEFAULT_OUT_DIR
    manifest_path: str = DEFAULT_MANIFEST
    delay: float = 1.0
    doc_delay: float = 0.5
    max_pages: int = 20000
    timeout: int = 30
    session: requests.Session = field(default_factory=requests.Session)
    seen_urls: set[str] = field(default_factory=set)
    seen_doc_urls: set[str] = field(default_factory=set)
    robots: dict[str, urllib.robotparser.RobotFileParser] = field(default_factory=dict)
    page_delay_by_origin: dict[str, float] = field(default_factory=dict)
    stats: dict[str, int] = field(default_factory=lambda: {"pages": 0, "docs_found": 0, "docs_downloaded": 0, "docs_skipped": 0, "errors": 0})

    def __post_init__(self):
        self.session.headers.update({"User-Agent": USER_AGENT})
        os.makedirs(self.out_dir, exist_ok=True)
        self._load_manifest()

    def _load_manifest(self):
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                        self.seen_doc_urls.add(rec["url"])
                    except (json.JSONDecodeError, KeyError):
                        continue
        else:
            os.makedirs(os.path.dirname(self.manifest_path), exist_ok=True)
            open(self.manifest_path, "a", encoding="utf-8").close()

    def _append_manifest(self, record: dict):
        with open(self.manifest_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _robots_allows(self, url: str) -> bool:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        rp = self.robots.get(origin)
        if rp is None:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(urljoin(origin, "/robots.txt"))
            try:
                rp.read()
            except Exception:  # noqa: BLE001
                rp = None  # treat unreadable robots.txt as "allow"
            self.robots[origin] = rp
        if rp is None:
            return True
        if origin not in self.page_delay_by_origin:
            try:
                cd = rp.crawl_delay(USER_AGENT)
            except Exception:  # noqa: BLE001
                cd = None
            self.page_delay_by_origin[origin] = max(self.delay, float(cd)) if cd else self.delay
        try:
            return rp.can_fetch(USER_AGENT, url)
        except Exception:  # noqa: BLE001
            return True

    def _page_delay_for(self, url: str) -> float:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        return self.page_delay_by_origin.get(origin, self.delay)

    def _is_doc_link(self, url: str) -> bool:
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        return ext in DOC_EXTENSIONS

    def _infer_title(self, a_tag, url: str) -> str:
        """Icon-only PDF links (common on the category tables) carry no anchor
        text; fall back to a sibling data-title in the same table row, then
        to the row's first non-numeric cell, then to the URL's own filename
        (uploaded PDFs are typically named after the document in Nepali)."""
        text = a_tag.get_text(strip=True)
        if text:
            return text
        row = a_tag.find_parent("tr")
        if row is not None:
            sib = row.find(attrs={"data-title": True})
            if sib and sib.get("data-title"):
                return sib["data-title"]
            for td in row.find_all("td"):
                t = td.get_text(strip=True)
                if t and not t.isdigit():
                    return t
        base = os.path.splitext(os.path.basename(urlparse(url).path))[0]
        return unquote(base)

    def _in_scope(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        if parsed.netloc not in self.allowed_domains:
            return False
        if SKIP_URL_PATTERNS.search(url):
            return False
        return True

    @staticmethod
    def _priority(url: str) -> int:
        """Listing pages (category tables, index pages, pagination) link
        directly to every Act/Rule PDF, so drain them before the thousands of
        individual /content/ news/detail pages."""
        path = urlparse(url).path
        if path.startswith("/category/") or path.startswith("/pages/") or path in ("", "/"):
            return 0
        if path.startswith("/content/"):
            return 2
        return 1

    def _state_path(self) -> str:
        return os.path.join(os.path.dirname(self.manifest_path), "crawl_state.json")

    def _save_state(self, heap: list):
        tmp = self._state_path() + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"visited": sorted(self.seen_urls), "queue": [u for _, _, u in heap]}, f, ensure_ascii=False)
        os.replace(tmp, self._state_path())

    def crawl(self):
        import heapq
        heap: list = []
        self._enqueued: set[str] = set()
        seq = 0

        def push(u: str):
            nonlocal seq
            if u in self._enqueued or u in self.seen_urls:
                return
            self._enqueued.add(u)
            heapq.heappush(heap, (self._priority(u), seq, u))
            seq += 1

        self._push = push
        if os.path.exists(self._state_path()):
            with open(self._state_path(), "r", encoding="utf-8") as f:
                state = json.load(f)
            self.seen_urls.update(state.get("visited", []))
            for u in state.get("queue", []):
                push(u)
            print(f"[crawl] resumed: visited={len(self.seen_urls)} queue={len(heap)}", file=sys.stderr)
        for s in self.seeds:
            push(s)

        while heap and self.stats["pages"] < self.max_pages:
            _, _, url = heapq.heappop(heap)
            try:
                self._crawl_one(url, len(heap))
            except Exception as e:  # noqa: BLE001 - a single bad page must never kill the crawl
                self.stats["errors"] += 1
                print(f"[crawl] unexpected error: {e}", file=sys.stderr)
            if self.stats["pages"] % 10 == 0:
                self._save_state(heap)

        self._save_state(heap)
        print(f"[crawl] done: {self.stats}", file=sys.stderr)

    def _crawl_one(self, url: str, queue_len: int):
        if url in self.seen_urls or not self._in_scope(url):
            return
        self.seen_urls.add(url)

        if self._is_doc_link(url):
            self._safe_handle_doc(url, link_text=os.path.basename(urlparse(url).path))
            return

        if not self._robots_allows(url):
            return

        html = self._fetch_page(url)
        self.stats["pages"] += 1
        if html is None:
            return

        soup = BeautifulSoup(html, "html.parser")
        self._current_page = url
        page_hosts = {urlparse(s).netloc for s in self.seeds}
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith("#"):
                continue
            abs_url = urljoin(url, href)
            abs_url = abs_url.split("#")[0]
            if not self._in_scope(abs_url):
                continue
            if self._is_doc_link(abs_url):
                self._safe_handle_doc(abs_url, link_text=self._infer_title(a, abs_url))
            elif urlparse(abs_url).netloc in page_hosts:
                self._push(abs_url)

        if self.stats["pages"] % 10 == 0:
            print(
                f"[crawl] pages={self.stats['pages']} docs_found={self.stats['docs_found']} "
                f"downloaded={self.stats['docs_downloaded']} skipped={self.stats['docs_skipped']} "
                f"queue={queue_len}",
                file=sys.stderr,
            )
        time.sleep(self._page_delay_for(url))

    def _fetch_page(self, url: str) -> str | None:
        for attempt, wait in enumerate((15, 45, 120, None)):
            try:
                r = self.session.get(url, timeout=self.timeout)
                if r.status_code == 404:
                    return None
                r.raise_for_status()
                ctype = r.headers.get("Content-Type", "")
                if "text/html" not in ctype:
                    return None
                return r.text
            except requests.RequestException as e:
                print(f"[crawl] fetch failed {url} (attempt {attempt + 1}): {e}", file=sys.stderr)
                if wait is None:
                    self.stats["errors"] += 1
                    return None
                time.sleep(wait)  # the government server sheds load with 503s; back off
        return None

    def _safe_handle_doc(self, url: str, link_text: str):
        try:
            self._handle_doc(url, link_text)
        except Exception as e:  # noqa: BLE001 - one bad document must never kill the crawl
            self.stats["errors"] += 1
            print(f"[download] unexpected error for {url}: {e}", file=sys.stderr)

    def _handle_doc(self, url: str, link_text: str):
        self.stats["docs_found"] += 1
        if url in self.seen_doc_urls:
            self.stats["docs_skipped"] += 1
            return
        if not self._robots_allows(url):
            self.stats["docs_skipped"] += 1
            return

        category = classify(f"{link_text} {url}")
        fname = safe_filename(url, link_text or url)
        dest_dir = os.path.join(self.out_dir, category)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, fname)

        # avoid overwriting a different doc that hashed to the same filename
        n = 1
        base, ext = os.path.splitext(dest_path)
        while os.path.exists(dest_path):
            dest_path = f"{base}__{n}{ext}"
            n += 1

        try:
            r = self.session.get(url, timeout=self.timeout, stream=True)
            r.raise_for_status()
            sha256 = hashlib.sha256()
            size = 0
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 16):
                    if not chunk:
                        continue
                    f.write(chunk)
                    sha256.update(chunk)
                    size += len(chunk)
        except requests.RequestException as e:
            self.stats["errors"] += 1
            print(f"[download] failed {url}: {e}", file=sys.stderr)
            if os.path.exists(dest_path):
                os.remove(dest_path)
            return

        record = {
            "url": url,
            "title": link_text,
            "category": category,
            "source_page": getattr(self, "_current_page", None),
            "local_path": os.path.relpath(dest_path, ROOT),
            "sha256": sha256.hexdigest(),
            "size_bytes": size,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self._append_manifest(record)
        self.seen_doc_urls.add(url)
        self.stats["docs_downloaded"] += 1
        time.sleep(self.doc_delay)


def cmd_crawl(args):
    domains = {urlparse(u).netloc for u in args.seed}
    domains |= set(args.extra_domain or [])
    crawler = Crawler(
        seeds=args.seed,
        allowed_domains=domains,
        out_dir=args.out_dir,
        manifest_path=args.manifest,
        delay=args.delay,
        doc_delay=args.doc_delay,
        max_pages=args.max_pages,
    )
    crawler.crawl()


def _extractable_text_fraction(pdf_path: str) -> float:
    """Rough heuristic: fraction of sampled pages that yield >20 chars of text."""
    try:
        from pypdf import PdfReader
    except Exception:  # noqa: BLE001 - broken/missing pypdf install
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except Exception:  # noqa: BLE001
            return 1.0  # can't check; assume fine, skip OCR
    try:
        reader = PdfReader(pdf_path)
    except Exception:  # noqa: BLE001
        return 1.0
    pages = reader.pages
    if not pages:
        return 1.0
    sample = pages[:: max(1, len(pages) // 10)][:10] or pages[:1]
    with_text = 0
    for p in sample:
        try:
            if len((p.extract_text() or "").strip()) > 20:
                with_text += 1
        except Exception:  # noqa: BLE001
            pass
    return with_text / len(sample)


def cmd_ocr(args):
    if subprocess.run(["which", "ocrmypdf"], capture_output=True).returncode != 0:
        print("ocrmypdf not found on PATH. Install it (apt install ocrmypdf tesseract-ocr-nep) "
              "to enable this step.", file=sys.stderr)
        sys.exit(1)

    records = []
    with open(args.manifest, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    for rec in records:
        path = os.path.join(ROOT, rec["local_path"])
        if not path.lower().endswith(".pdf") or not os.path.exists(path):
            continue
        if rec.get("ocr_done"):
            continue
        frac = _extractable_text_fraction(path)
        if frac >= 0.3:
            continue  # already has a usable text layer on most sampled pages
        ocr_path = path.replace(".pdf", ".ocr.pdf")
        print(f"[ocr] {rec['local_path']} (text_fraction={frac:.2f})")
        result = subprocess.run(
            ["ocrmypdf", "--language", "nep+eng", "--force-ocr", "--optimize", "1",
             path, ocr_path],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"[ocr] FAILED {rec['local_path']}: {result.stderr[-500:]}", file=sys.stderr)
            continue
        rec["ocr_done"] = True
        rec["ocr_path"] = os.path.relpath(ocr_path, ROOT)

    with open(args.manifest, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("[ocr] done")


def cmd_stats(args):
    if not os.path.exists(args.manifest):
        print("No manifest yet.")
        return
    by_category: dict[str, int] = {}
    total = 0
    with open(args.manifest, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            by_category[rec["category"]] = by_category.get(rec["category"], 0) + 1
            total += 1
    print(f"Total documents: {total}")
    for cat, n in sorted(by_category.items(), key=lambda kv: -kv[1]):
        print(f"  {cat:12s} {n}")


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    pc = sub.add_parser("crawl", help="crawl + download documents")
    pc.add_argument("--seed", nargs="+", default=[
        "https://lawcommission.gov.np/",
    ])
    pc.add_argument("--extra-domain", nargs="*", default=["giwmscdnone.gov.np"],
                     help="additional netlocs to allow (PDFs are hosted on the CDN "
                          "domain by default; add supremecourt.gov.np for precedents)")
    pc.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    pc.add_argument("--manifest", default=DEFAULT_MANIFEST)
    pc.add_argument("--delay", type=float, default=2.0,
                     help="seconds between HTML page requests (raised to robots.txt's "
                          "Crawl-delay automatically if it's higher)")
    pc.add_argument("--doc-delay", type=float, default=0.5,
                     help="seconds between binary document downloads")
    pc.add_argument("--max-pages", type=int, default=20000)
    pc.set_defaults(func=cmd_crawl)

    po = sub.add_parser("ocr", help="OCR documents with no usable text layer (needs ocrmypdf)")
    po.add_argument("--manifest", default=DEFAULT_MANIFEST)
    po.set_defaults(func=cmd_ocr)

    ps = sub.add_parser("stats", help="print manifest stats")
    ps.add_argument("--manifest", default=DEFAULT_MANIFEST)
    ps.set_defaults(func=cmd_stats)

    return p


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
