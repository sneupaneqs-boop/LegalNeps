"""
Scrapes primary regulatory texts (acts, regulations, directives, circulars)
from Nepali regulators' websites so Kanooni Sathi can answer questions from
CAs, accountants and SME owners about NRB / IRD / SEBON / OCR / insurance /
labour rules.  Step 1 of a two-step pipeline:

    1. scrape_regulators.py   discover + download documents  -> sources/regulators/<authority>/
    2. ingest_regulators.py   extract text, chunk, write     -> backend/app/data/corpus/part-002.jsonl.gz

    python3 backend/scripts/scrape_regulators.py --authority nrb
    python3 backend/scripts/scrape_regulators.py --authority all --max-pages 5
    python3 backend/scripts/scrape_regulators.py --authority ird --list-only
    python3 backend/scripts/scrape_regulators.py stats

Design (same conventions as scrape_lawcommission.py):
- Polite: honours robots.txt, <= 1 request/second per host, descriptive
  User-Agent, retries with exponential backoff on 5xx / dropped connections.
- Idempotent + resumable: every discovered document is appended to
  sources/regulators/<authority>/manifest.jsonl (keyed by URL); a re-run
  skips anything already downloaded and re-fetches only missing files.
- Plain HTTP only (scrapling's Fetcher); none of these sites needs a browser.
- One function per authority (scrape_nrb, scrape_ird, ...); each yields
  document records and lets the shared machinery download them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.robotparser
from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator
from urllib.parse import unquote, urljoin, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_ROOT = os.path.join(ROOT, "sources", "regulators")

USER_AGENT = "KanooniSathiBot/1.0 (legal research; contact s.neupaneqs@gmail.com)"
MIN_INTERVAL = 1.1  # seconds between requests to the same host
DOC_EXT = (".pdf", ".doc", ".docx")
MAX_DOWNLOAD_MB = 60


# --------------------------------------------------------------------------
# polite HTTP client
# --------------------------------------------------------------------------
class Client:
    """Rate-limited, robots-aware, retrying fetcher built on scrapling.Fetcher."""

    def __init__(self, min_interval: float = MIN_INTERVAL, retries: int = 4, timeout: int = 45):
        from scrapling.fetchers import Fetcher

        self._fetcher = Fetcher
        self.min_interval = min_interval
        self.retries = retries
        self.timeout = timeout
        self._last: dict[str, float] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self._lock = threading.Lock()
        self.stats = {"requests": 0, "retries": 0, "failures": 0, "robots_blocked": 0}

    def _wait(self, host: str):
        with self._lock:
            now = time.time()
            wait = self._last.get(host, 0) + self.min_interval - now
            if wait > 0:
                time.sleep(wait)
            self._last[host] = time.time()

    def _raw_get(self, url: str):
        """One rate-limited request with retry on 5xx/network errors. Returns
        the scrapling response, or None after exhausting retries."""
        host = urlparse(url).netloc
        for attempt in range(self.retries):
            self._wait(host)
            self.stats["requests"] += 1
            try:
                r = self._fetcher.get(
                    url, headers={"User-Agent": USER_AGENT}, timeout=self.timeout,
                    stealthy_headers=False, follow_redirects=True,
                )
            except Exception as e:  # noqa: BLE001 - connection reset etc.
                print(f"   [http] {type(e).__name__} {url[:90]} (attempt {attempt + 1})", file=sys.stderr)
                r = None
            if r is not None and r.status < 500:
                return r
            if r is not None:
                print(f"   [http] {r.status} {url[:90]} (attempt {attempt + 1})", file=sys.stderr)
            self.stats["retries"] += 1
            time.sleep(min(30, 2 ** (attempt + 1)))
        self.stats["failures"] += 1
        return None

    def allowed(self, url: str) -> bool:
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            r = self._raw_get(base + "/robots.txt")
            if r is not None and r.status == 200:
                rp.parse(r.body.decode("utf-8", "replace").splitlines())
                self._robots[base] = rp
            else:
                self._robots[base] = None  # no robots.txt (404) or unreachable: allow
        rp = self._robots[base]
        ok = rp is None or rp.can_fetch(USER_AGENT, url)
        if not ok:
            self.stats["robots_blocked"] += 1
        return ok

    def get(self, url: str):
        """Fetch a page/file if robots allows. Returns response (any status < 500) or None."""
        if not self.allowed(url):
            print(f"   [robots] disallowed: {url}", file=sys.stderr)
            return None
        return self._raw_get(url)

    def html(self, url: str, patient: bool = False):
        """Fetch a page; `patient` re-tries a few times after a pause, for listing
        pages where one flaky response would otherwise truncate a whole crawl."""
        for attempt in range(3 if patient else 1):
            r = self.get(url)
            if r is not None and r.status == 200:
                return r
            if r is not None and r.status < 500:
                return None  # 404 etc: retrying will not help
            time.sleep(10)
        print(f"   [warn] gave up on {url}", file=sys.stderr)
        return None


# --------------------------------------------------------------------------
# manifest + downloads
# --------------------------------------------------------------------------
def _slug(s: str, n: int = 60) -> str:
    s = re.sub(r"[^\wऀ-ॿ]+", "-", s.strip(), flags=re.UNICODE).strip("-")
    return s[:n] or "doc"


def _clean(s: str | None) -> str:
    return " ".join((s or "").split())


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class Store:
    """sources/regulators/<authority>/{files/,manifest.jsonl}"""
    authority: str
    root: str = OUT_ROOT
    records: dict[str, dict] = field(default_factory=dict)  # url -> record

    def __post_init__(self):
        self.dir = os.path.join(self.root, self.authority)
        self.files_dir = os.path.join(self.dir, "files")
        self.manifest = os.path.join(self.dir, "manifest.jsonl")
        if os.path.exists(self.manifest):
            for line in open(self.manifest, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    self.records[r["url"]] = r

    def has_file(self, url: str) -> bool:
        r = self.records.get(url)
        return bool(r and r.get("local_path") and os.path.exists(os.path.join(ROOT, r["local_path"])))

    def save(self, rec: dict):
        self.records[rec["url"]] = rec
        os.makedirs(self.dir, exist_ok=True)
        with open(self.manifest, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def compact(self):
        """Rewrite the manifest keeping only the latest record per URL."""
        tmp = self.manifest + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for r in self.records.values():
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        os.replace(tmp, self.manifest)


def _save_file(store: Store, doc: dict, url: str, body: bytes) -> dict | None:
    ext = os.path.splitext(urlparse(url).path)[1].lower()
    if body[:5] == b"%PDF-":
        ext = ".pdf"
    elif ext not in DOC_EXT:
        return None
    sha = hashlib.sha256(body).hexdigest()
    base = unquote(os.path.basename(urlparse(url).path)) or doc["title"]
    name = f"{sha[:10]}-{_slug(re.sub(r'[.](pdf|docx?)$', '', base, flags=re.I), 50)}{ext}"
    path = os.path.join(store.files_dir, name)
    os.makedirs(store.files_dir, exist_ok=True)
    with open(path, "wb") as f:
        f.write(body)
    rec = {
        **doc, "url": url, "authority": store.authority, "sha256": sha, "size": len(body),
        "local_path": os.path.relpath(path, ROOT), "fetched_at": _now(),
    }
    store.save(rec)
    return rec


def download(client: Client, store: Store, doc: dict, follow: bool = True) -> list[dict]:
    """Download doc['url'] into the store (skipped when already present) and
    record it. Many CMSs serve the file straight from the post URL; others
    serve an HTML page linking to the attachment(s), which are followed one
    level deep. `doc` needs url + title, and may carry page_url/published/kind/doc_type.
    Returns the manifest records for the file(s) obtained."""
    url = doc["url"]
    if store.has_file(url):
        return [store.records[url]]
    r = client.get(url)
    if r is None or r.status != 200 or not r.body:
        print(f"   [skip] {url[:100]} -> {getattr(r, 'status', 'no response')}", file=sys.stderr)
        return []
    body = r.body
    if len(body) > MAX_DOWNLOAD_MB * 1024 * 1024:
        print(f"   [skip] too large ({len(body) >> 20}MB): {url[:100]}", file=sys.stderr)
        return []
    rec = _save_file(store, doc, url, body)
    if rec:
        return [rec]
    if not follow:
        return []
    out = []
    for u, text in _links(r, url):
        if _is_doc_url(u) and urlparse(u).netloc == urlparse(url).netloc and u not in store.records:
            sub = {**doc, "url": u, "page_url": url}
            if text and text.lower() not in ("download", "डाउनलोड", "pdf") and text not in doc["title"]:
                sub["title"] = f"{doc['title']} - {text}"
            out += download(client, store, sub, follow=False)
        elif u in store.records:
            out.append(store.records[u])
    if not out:
        print(f"   [skip] no document at {url[:100]}", file=sys.stderr)
    return out


def _links(page, base: str) -> Iterator[tuple[str, str]]:
    for a in page.css("a"):
        h = a.attrib.get("href")
        if not h or h.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        yield urljoin(base, h), _clean(a.get_all_text())


def _is_doc_url(u: str) -> bool:
    return urlparse(u).path.lower().endswith(DOC_EXT)


# --------------------------------------------------------------------------
# authority scrapers - each yields {"url","title","page_url","published","kind","doc_type"}
# --------------------------------------------------------------------------
AUTHORITIES: dict[str, Callable] = {}


def authority(name: str):
    def deco(fn):
        AUTHORITIES[name] = fn
        return fn
    return deco


# --- date helpers ----------------------------------------------------------
_DEV = str.maketrans("०१२३४५६७८९", "0123456789")
_BS_MONTHS = ["बैशाख", "जेठ", "असार", "साउन", "भदौ", "असोज", "कात्तिक", "मंसिर", "पौष", "माघ", "फागुन", "चैत"]
_BS_ALIASES = {"वैशाख": "बैशाख", "बैसाख": "बैशाख", "श्रावण": "साउन", "भाद्र": "भदौ", "आश्विन": "असोज", "असौज": "असोज",
               "कार्तिक": "कात्तिक", "मङ्सिर": "मंसिर", "मंसीर": "मंसिर", "मङ्गसिर": "मंसिर", "पुष": "पौष",
               "पुस": "पौष", "फाल्गुन": "फागुन", "चैत्र": "चैत", "साऊन": "साउन", "भदाै": "भदौ", "असाेज": "असोज"}


def bs_key(s: str | None) -> tuple[int, int, int] | None:
    """'१३ असोज, २०८३' or '2083-06-13' -> (2083, 6, 13) for ordering; None if unparseable."""
    if not s:
        return None
    t = s.translate(_DEV)
    m = re.search(r"(20\d\d)[-/.।](\d{1,2})[-/.।](\d{1,2})", t)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    m = re.search(r"(\d{1,2})\s+([^\d\s,]+)[,\s]+(20\d\d)", t)
    if m:
        mon = _BS_ALIASES.get(m.group(2), m.group(2))
        if mon in _BS_MONTHS:
            return int(m.group(3)), _BS_MONTHS.index(mon) + 1, int(m.group(1))
    return None


def fiscal_year_bs(key: tuple[int, int, int] | None) -> str | None:
    """Nepali fiscal year runs from Shrawan (month 4): (2083, 6, 13) -> '2083/84'."""
    if not key:
        return None
    y = key[0] if key[1] >= 4 else key[0] - 1
    return f"{y}/{str(y + 1)[-2:]}"


# --- generic GIWMS CMS (ird.gov.np, ocr.gov.np, nia.gov.np ...) ------------------
_GIWMS_ITEM = re.compile(r'href="(?:https?://[^/"]+)?(/content/(\d+)/[^"\s]*?)(?:%0A[^"]*)?"[^>]*>\s*([^<]{3,}?)\s*</a>')
_GIWMS_DATE = re.compile(r'post__date">\s*<p>\s*<i[^>]*></i>\s*([^<]+)')
_GIWMS_PDF = re.compile(r"""var\s+pdf\s*=\s*['"]([^'"]+)['"]""")


def giwms_listing(client: Client, base: str, path: str, max_pages: int = 30, stop_before_bs: tuple | None = None) -> Iterator[dict]:
    """Iterate a GIWMS category listing (?page=N). Only the main list is read
    (not the header ticker or the 'related' block). Stops at max_pages, an
    empty page, or - listings are newest-first - once items get older than
    `stop_before_bs`."""
    seen: set[str] = set()
    for pg in range(1, max_pages + 1):
        url = f"{base}{path}" + (f"?page={pg}" if pg > 1 else "")
        r = client.html(url, patient=True)
        if r is None:
            break
        h = re.sub(r"\s+", " ", r.html_content)
        start = h.find("category__title")
        if start < 0:
            start = 0
        end = h.find("category__title", start + 20)
        region = h[start: end if end > 0 else len(h)]
        n_new, older = 0, 0
        if not _GIWMS_DATE.search(region) and not any(True for _ in _GIWMS_ITEM.finditer(region)):
            region = h  # table-style layouts (lawcommission rules): no dated cards, read every content link
        for m in _GIWMS_ITEM.finditer(region):
            cid = m.group(2)
            d = _GIWMS_DATE.search(region[m.end(): m.end() + 700])
            if cid in seen:
                continue
            seen.add(cid)
            n_new += 1
            # some sites (ocr.gov.np) list items without a date: fall back to a BS date in the title
            pub = d.group(1).strip() if d else ""
            if not pub:
                tm = re.search(r"20[78]\d\s*[/।.\-]\s*\d{1,2}\s*[/।.\-]\s*\d{1,2}|\d{1,2}\s*[/।.\-]\s*\d{1,2}\s*[/।.\-]\s*20[78]\d", m.group(3).translate(_DEV))
                pub = tm.group(0) if tm else ""
            if stop_before_bs and (bs_key(pub) or (9999, 0, 0)) < stop_before_bs:
                older += 1
                continue
            yield {"url": f"{base}{m.group(1)}", "title": _clean(m.group(3)), "published": pub, "page_url": url}
        if n_new == 0 or (stop_before_bs and older == n_new):
            break


def giwms_files(client: Client, page_url: str) -> list[str]:
    """Attachment URLs of a GIWMS content page: the `var pdf = '...'` viewer
    variable plus any directly linked documents."""
    r = client.html(page_url)
    if r is None:
        return []
    h = r.html_content
    out = [u for u in _GIWMS_PDF.findall(h) if u.lower().split("?")[0].endswith(DOC_EXT)]
    for u, _t in _links(r, page_url):
        if _is_doc_url(u) and ("giwmscdnone" in u or urlparse(u).netloc == urlparse(page_url).netloc):
            out.append(u)
    return list(dict.fromkeys(out))


# --- shared selection helpers -----------------------------------------------
# titles that are never legal text: tenders, vacancies, press, auctions, results...
NOISE_TITLE = re.compile(
    r"लिलाम|प्रवेश\s*नि[षे]*ेध|बोलपत्र|tender|प्रेस\s*विज्ञप्ति|press release|विज्ञापन|पाठ्यक्रम|नतिजा|"
    r"कर्मचारी सेवा|सूचना अधिकारी|बिदा|विजेता|दरभाउपत्र|शिलबन्दी|खरिद सम्बन्धी|फोटो|गुनासो|वार्षिक प्रतिवेदन|"
    r"annual report|newsletter|सार्वजनिक बिदा|विद्युतिय सेवा प्राप्त|अन्तरक्रिया|तालिम|कार्यक्रम तालिका|"
    r"goaml सेवा|शोक|श्रद्धाञ्जली|रिक्त|अन्तर्वार्ता|दैवी प्रकोप|राहत कोष",
    re.I,
)


def series_key(title: str) -> str:
    """Title with amendment parentheticals, digits and punctuation removed, so
    'X ऐन, २०५८ (आर्थिक ऐन, २०८२ सहित)' and '... २०८१ सहित' fall in one series."""
    t = re.sub(r"\([^)]*\)", " ", title or "")
    t = re.sub(r"[०-९0-9]+", " ", t)
    t = re.sub(r"[\W_]+", " ", t, flags=re.UNICODE)
    return " ".join(t.split()).lower()


def pub_sort_key(published: str | None) -> tuple[int, int, int]:
    """Comparable (year, month, day) for an AD ('July 22, 2025', '2025-07-22') or BS
    ('१३ असोज, २०८३') date; BS is mapped roughly onto AD. Only used to order
    documents of the same source, so the approximation is harmless."""
    ad = _ad_date(published)
    if ad:
        return ad.tm_year, ad.tm_mon, ad.tm_mday
    bs = bs_key(published)
    if bs:
        return bs[0] - (57 if bs[1] <= 8 else 56), (bs[1] + 2) % 12 + 1, bs[2]
    return (0, 0, 0)


def newest_per_series(docs: list[dict]) -> list[dict]:
    """Keep the newest document of each title series (dated docs win; ties keep
    the first, and listings are newest-first on all these sites)."""
    best: dict[str, dict] = {}
    for d in docs:
        k = series_key(d["title"])
        cur = best.get(k)
        if cur is None or pub_sort_key(d.get("published")) > pub_sort_key(cur.get("published")):
            best[k] = d
    return [d for d in docs if best.get(series_key(d["title"])) is d]


def _ad_date(s: str | None):
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            return time.strptime((s or "").strip(), fmt)
        except ValueError:
            pass
    return None


CURRENT_FY_START_AD = time.strptime("2025-07-16", "%Y-%m-%d")  # 1 Shrawan 2082 = start of previous FY


# --------------------------------------------------------------------------
# Nepal Rastra Bank  (www.nrb.org.np, WordPress; posts serve the PDF directly)
# --------------------------------------------------------------------------
NRB = "https://www.nrb.org.np"
# (label, listing url, kind, doc_type, only-newer-than-previous-FY?, max_pages, latest_per_series)
NRB_LISTINGS = [
    ("acts", f"{NRB}/category/acts/?department=lgd", "act", "act", False, 3, True),
    ("rules-bylaws", f"{NRB}/category/rules-by-laws/?department=lgd", "regulation", "rule", False, 8, True),
    ("bfr-circulars-2083-84", f"{NRB}/category/circulars/2083-84/?department=bfr", "circular", "directive", False, 6, False),
    ("bfr-circulars-2082-83", f"{NRB}/category/circulars/2082-83/?department=bfr", "circular", "directive", False, 8, False),
    ("guidelines-manuals", f"{NRB}/category/manual-guidelines/?department=ofg", "guideline", "directive", False, 3, False),
    ("psd-circulars", f"{NRB}/category/circulars/?department=psd", "circular", "directive", True, 4, False),
    ("psd-guidelines", f"{NRB}/category/policies-guidelines/?department=psd", "guideline", "directive", False, 2, False),
    ("fxm-circulars", f"{NRB}/category/fxm-circulars/%e0%a4%b5%e0%a4%bf%e0%a4%a6%e0%a5%87%e0%a4%b6%e0%a5%80-%e0%a4%b5%e0%a4%bf%e0%a4%a8%e0%a4%bf%e0%a4%ae%e0%a4%af-%e0%a4%b5%e0%a5%8d%e0%a4%af%e0%a4%b5%e0%a4%b8%e0%a5%8d%e0%a4%a5%e0%a4%be%e0%a4%aa%e0%a4%a8/?department=fxm",
     "circular", "directive", True, 4, False),
]
_NRB_ITEM = re.compile(
    r'<span class="text-primary">\s*<a href="([^"]+)"[^>]*>([^<]+)</a>.*?<span class="mr-3 text-muted">([^<]*)</span>', re.S)
# NRB skip: repealed 2012 NRB Act, HR bylaws
NRB_SKIP = re.compile(
    r"ऐन,\s*२०१२|ऐन,\s*2012|विधेयक|संशोधन र एकीकरण गर्न|कर्मचारी सेवा|खरिद|खर्च व्यवस्था|अख्तियार|प्रकाशन निर्देशिका|उच्च अध्ययन|"
    r"बैठक|कार्य व्यवस्था|Board of Directors|Seal|सूचना तथा स[ंञ्]*चार|कागजात धुल्याउने|सट्टा भर्ना|नोट धुल्याउने|"
    r"नोट छपाई|टकमरी|टकमारी|अनुसन्धान|Upabhokta|RSRF|BOP Manual")
# FIU-Nepal hosts AML/CFT directives of NRB departments and of other regulators (incl. ICAN)
NRB_FIU_SITEMAP = f"{NRB}/fiu-sitemap.xml"
NRB_FIU_RE = re.compile(r"directive|guidelines?$|guidelines-updated|निर्देशिका|निर्देशन")
NRB_FIU_SKIP = re.compile(r"report|newsletter|training|invitation|faqs?$|typolog|egmont|fatf|methodology|booklet|strategic|assessment|follow-up")


def _nrb_listing_pages(client: Client, url: str, max_pages: int):
    """Yield (href, title, date_str) over a paginated NRB category listing."""
    base, _, query = url.partition("?")
    for pg in range(1, max_pages + 1):
        u = url if pg == 1 else (base.rstrip("/") + f"/page/{pg}/" + (f"?{query}" if query else ""))
        r = client.html(u, patient=True)
        if r is None:
            return
        found = 0
        for m in _NRB_ITEM.finditer(r.html_content):
            found += 1
            yield m.group(1), _clean(m.group(2)), _clean(m.group(3))
        if not found:
            return


@authority("nrb")
def scrape_nrb(client: Client, opts) -> Iterator[dict]:
    seen = set()
    for label, url, kind, dtype, recent_only, maxp, latest in NRB_LISTINGS:
        docs = []
        for href, title, date in _nrb_listing_pages(client, url, min(maxp, opts.max_pages or maxp)):
            if href in seen or NOISE_TITLE.search(title) or NRB_SKIP.search(title):
                continue
            ad = _ad_date(date)
            if recent_only and ad and ad < CURRENT_FY_START_AD:
                continue
            seen.add(href)
            docs.append({"url": href, "title": title, "published": date, "page_url": url,
                         "kind": kind, "doc_type": dtype, "source_list": label})
        yield from (newest_per_series(docs) if latest else docs)
    # FIU-Nepal AML/CFT directives hosted on nrb.org.np
    r = client.get(NRB_FIU_SITEMAP)
    if r is not None and r.status == 200:
        for loc, lastmod in re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", r.body.decode("utf-8", "replace")):
            slug = unquote(loc.rstrip("/").rsplit("/", 1)[-1]).lower()
            if NRB_FIU_RE.search(slug) and not NRB_FIU_SKIP.search(slug) and loc not in seen:
                seen.add(loc)
                yield {"url": loc, "title": slug.replace("-", " "), "published": lastmod[:10], "page_url": NRB_FIU_SITEMAP,
                       "kind": "directive", "doc_type": "directive", "source_list": "fiu-aml-cft"}


# --------------------------------------------------------------------------
# Inland Revenue Department  (ird.gov.np, GIWMS CMS; PDFs at giwmscdnone.gov.np)
# --------------------------------------------------------------------------
IRD = "https://ird.gov.np"
# (category, kind, doc_type, selection mode, only recent fiscal years)
IRD_CATEGORIES = [
    ("incometaxact", "act", "act", "latest", False),
    ("valueaddedtaxact", "act", "act", "latest", False),
    ("exciseact", "act", "act", "latest", False),
    ("financeact", "act", "act", "finance", False),
    ("incometaxrules", "regulation", "rule", "latest", False),
    ("valueaddedtaxrules", "regulation", "rule", "latest", False),
    ("exciserules", "regulation", "rule", "latest", False),
    ("directives", "directive", "directive", "series", False),
    ("procedure", "directive", "directive", "series", False),
    ("vat-2", "directive", "directive", "series", False),
    ("incometax-2", "directive", "directive", "series", False),
    ("excise-1", "directive", "directive", "series", False),
    ("others-1", "directive", "directive", "series", False),
    ("taxrateincentives", "circular", "directive", "all", True),
]


# per-chapter uploads of the 2077 income-tax directive; the 5th-amendment (2081) consolidated text supersedes them
IRD_SUPERSEDED = re.compile(r"परिच्छेद|आयकर निर्देशिका\s*,?\s*२०६६\s*\(?\s*(?:तेस्रो|चौथो)")


@authority("ird")
def scrape_ird(client: Client, opts) -> Iterator[dict]:
    seen = set()
    for cat, kind, dtype, mode, fy_only in IRD_CATEGORIES:
        stop = (2082, 4, 1) if fy_only else None  # tax-rate notices: FY 2082/83 onwards only
        items = [d for d in giwms_listing(client, IRD, f"/category/{cat}/", max_pages=opts.max_pages or 12, stop_before_bs=stop)
                 if d["url"] not in seen and not NOISE_TITLE.search(d["title"])]
        items = [d for d in items if "विधेयक" not in d["title"] and "bill" not in d["title"].lower()
                 and not IRD_SUPERSEDED.search(d["title"])]
        if mode == "latest":
            items = items[:1]  # consolidated act/rules: newest listed version only
        elif mode == "finance":
            items = items[:3]  # last three Finance (Economic) Acts carry the yearly rate changes
        elif mode == "series":
            items = newest_per_series(items)
        for d in items:
            seen.add(d["url"])
            yield {**d, "kind": kind, "doc_type": dtype, "source_list": cat}


# --------------------------------------------------------------------------
# SEBON  (www.sebon.gov.np; listing tables: title | English pdf | Nepali pdf)
# --------------------------------------------------------------------------
SEBON = "https://www.sebon.gov.np"
SEBON_LISTS = [
    ("acts", "act", "act", 3), ("regulations", "regulation", "rule", 6), ("bylaws", "regulation", "rule", 4),
    ("guidelines", "guideline", "directive", 5), ("circulars", "circular", "directive", 6),
]
_SEBON_ROW = re.compile(r"<tr><td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>", re.S)
_HREF = re.compile(r'href="([^"]+)"')
_UPLOAD_DATE = re.compile(r"/uploads/(20\d\d)/(\d\d)/(\d\d)/")


@authority("sebon")
def scrape_sebon(client: Client, opts) -> Iterator[dict]:
    seen = set()
    for name, kind, dtype, maxp in SEBON_LISTS:
        for pg in range(1, min(maxp, opts.max_pages or maxp) + 1):
            r = client.html(f"{SEBON}/{name}" + (f"?page={pg}" if pg > 1 else ""), patient=True)
            if r is None:
                break
            rows = _SEBON_ROW.findall(re.sub(r"\s+", " ", r.html_content))
            if not rows:
                break
            for title_h, en_h, ne_h in rows:
                title = _clean(re.sub(r"<[^>]+>", " ", title_h))
                if NOISE_TITLE.search(title) or "मस्यौदा" in title or "draft" in title.lower():
                    continue  # consultation drafts are not law
                for lang, cell in (("ne", ne_h), ("en", en_h)):
                    m = _HREF.search(cell)
                    if not m or not m.group(1).lower().endswith(".pdf"):
                        continue
                    u = urljoin(SEBON + "/", m.group(1))
                    if u in seen:
                        continue
                    seen.add(u)
                    dm = _UPLOAD_DATE.search(u)
                    yield {"url": u, "title": title + (" (English)" if lang == "en" else ""),
                           "published": "-".join(dm.groups()) if dm else "", "page_url": f"{SEBON}/{name}",
                           "kind": kind, "doc_type": dtype, "lang": lang, "source_list": name}


# --------------------------------------------------------------------------
# Office of the Company Registrar  (ocr.gov.np, GIWMS CMS)
# --------------------------------------------------------------------------
OCR = "https://ocr.gov.np"


@authority("ocr")
def scrape_ocr(client: Client, opts) -> Iterator[dict]:
    seen = set()
    for cat in ("act-rules", "notices", "other-downloads"):
        for d in giwms_listing(client, OCR, f"/category/{cat}", max_pages=opts.max_pages or 6):
            if d["url"] in seen or NOISE_TITLE.search(d["title"]):
                continue
            seen.add(d["url"])
            is_dir = bool(re.search(r"निर्देशिका|निर्देशन|कार्यविधि|मापदण्ड|ढाँचा", d["title"]))
            yield {**d, "kind": "directive" if is_dir else "notice", "doc_type": "directive", "source_list": cat}


# --------------------------------------------------------------------------
# Law Commission gap check  (www.lawcommission.gov.np, GIWMS table layout)
# --------------------------------------------------------------------------
LAWCOMMISSION = "https://www.lawcommission.gov.np"
# current-law indexes: category id -> (kind, doc_type)
LC_CATEGORIES = {"1757": ("act", "act"), "1811": ("regulation", "rule"), "2163": ("act", "act")}
_TABLE_ROW = re.compile(r"<tr><td>\s*\d+\s*</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>\s*<a href=\"([^\"]+)\"", re.S)
_DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def giwms_table(client: Client, base: str, path: str, max_pages: int = 40) -> Iterator[dict]:
    """Rows of a GIWMS table listing: | # | title | published | pdf link | ... |"""
    seen = set()
    for pg in range(1, max_pages + 1):
        url = f"{base}{path}" + (f"?page={pg}" if pg > 1 else "")
        r = client.html(url, patient=True)
        if r is None:
            break
        rows = _TABLE_ROW.findall(re.sub(r"\s+", " ", r.html_content))
        new = 0
        for title_h, pub_h, href in rows:
            u = urljoin(base + "/", href.replace(" ", "%20"))
            if u in seen:
                continue
            seen.add(u)
            new += 1
            yield {"url": u, "title": _clean(re.sub(r"<[^>]+>", " ", title_h)),
                   "published": _clean(re.sub(r"<[^>]+>", " ", pub_h)), "page_url": url}
        if not new:
            break


def title_key(title: str) -> str:
    """Spelling/digit-insensitive identity of a law title (years are part of the identity)."""
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    from app.text_norm import fold

    return re.sub(r"[\W_]+", "", fold((title or "").translate(_DEV_DIGITS)), flags=re.UNICODE)


_existing_titles: dict[str, str] | None = None


def existing_corpus_titles() -> dict[str, str]:
    """title_key -> doc_title_ne for every law document in the pre-existing corpus shards
    (shards written by ingest_regulators.py, `reg-` ids, are excluded)."""
    global _existing_titles
    if _existing_titles is None:
        import glob
        import gzip

        out: dict[str, str] = {}
        for path in sorted(glob.glob(os.path.join(ROOT, "backend", "app", "data", "corpus", "part-*.jsonl.gz"))):
            with gzip.open(path, "rt", encoding="utf-8") as f:
                for line in f:
                    if '"category": "law"' not in line[:400] or '"id": "reg-' in line[:60]:
                        continue
                    t = json.loads(line).get("doc_title_ne") or ""
                    if t:
                        out.setdefault(title_key(t), t)
        _existing_titles = out
    return _existing_titles


def in_corpus(title: str, threshold: float = 0.88) -> bool:
    """True when a law of this title (same year, near-identical spelling: 'ज्येष्ठ'/'जेष्ठ',
    'निर्वाचन'/'निर्वाचन' ...) is already in the corpus."""
    import difflib

    k = title_key(title)
    have = existing_corpus_titles()
    if k in have:
        return True
    year = re.findall(r"20\d\d", (title or "").translate(_DEV_DIGITS))
    for e in have:
        if year and year[-1] not in e:
            continue
        if (len(e) > 14 and (k in e or e in k) and abs(len(e) - len(k)) < 20) or \
                difflib.SequenceMatcher(None, k, e).ratio() >= threshold:
            return True
    return False


_LC_INDEX_ROW = re.compile(
    r'<td[^>]*>\s*[०-९0-9]+\.?\s*</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>\s*(?:<a[^>]*href="([^"]+)"[^>]*>)?', re.S)


def _similar(a: str, b: str, threshold: float = 0.85) -> bool:
    import difflib

    return difflib.SequenceMatcher(None, title_key(a), title_key(b)).ratio() >= threshold


@authority("lawcommission-gap")
def scrape_lawcommission_gap(client: Client, opts) -> Iterator[dict]:
    """Compare the Law Commission's current-acts index (alphabetical index page: ~350
    acts) and its recent acts/rules listings with the corpus; yield those not in it.
    The alphabetical index links each act to its volume category, whose listing
    carries the PDF, so missing titles are resolved there."""
    seen: set[str] = set()

    def fresh(d, kind, dtype, src):
        if d["url"] in seen or "विधेयक" in d["title"] or in_corpus(d["title"]):
            return None
        seen.add(d["url"])
        return {**d, "kind": kind, "doc_type": dtype, "source_list": src}

    # 1. alphabetical index -> missing titles -> volume categories
    r = client.html(f"{LAWCOMMISSION}/pages/alphabetical-index-of-acts/", patient=True)
    missing: dict[str, list[str]] = {}
    if r is not None:
        for name_h, href in _LC_INDEX_ROW.findall(re.sub(r"\s+", " ", r.html_content)):
            name = _clean(re.sub(r"<[^>]+>", " ", name_h))
            if name and href and "/category/" in href and not in_corpus(name):
                missing.setdefault(href, []).append(name)
    for href, names in missing.items():
        cat = "/" + href.split("gov.np/", 1)[-1].strip("/")
        rows = list(giwms_table(client, LAWCOMMISSION, cat, max_pages=30)) or \
            [{**d, "url": d["url"]} for d in giwms_listing(client, LAWCOMMISSION, cat, max_pages=30)]
        for name in names:
            hit = next((d for d in rows if _similar(d["title"], name)), None)
            if hit is None:
                print(f"   [gap] {name}: not found in {cat}", file=sys.stderr)
                continue
            if (x := fresh({**hit, "title": hit["title"]}, "act", "act", "alphabetical-index")):
                yield x
    # 2. newest acts/rules listings (may post-date the index page)
    for d in giwms_listing(client, LAWCOMMISSION, "/category/1757", max_pages=opts.max_pages or 40):
        if (x := fresh(d, "act", "act", "category-1757")):
            yield x
    for cid, (kind, dtype) in (("1811", ("regulation", "rule")), ("2163", ("act", "act"))):
        for d in giwms_table(client, LAWCOMMISSION, f"/category/{cid}", max_pages=opts.max_pages or 10):
            if d["url"].lower().endswith(DOC_EXT) and (x := fresh(d, kind, dtype, f"category-{cid}")):
                yield x


# --------------------------------------------------------------------------
# Tier-2 sites on the same GIWMS CMS: NIA, MoLESS, PPMO (+ Nepal Gazette, best effort)
# --------------------------------------------------------------------------
_LEGAL_CAT = re.compile(r"ऐन|नियम|निर्देशिका|कार्यविधि|मापदण्ड|परिपत्र|कानून|निर्देशन|पीपीए|\bacts?\b|regulation|directive|circular|guideline|bylaw|law", re.I)


def _giwms_site(client: Client, base: str, opts, kind_by_title=None, only: tuple[str, ...] | None = None) -> Iterator[dict]:
    """Discover legal-text categories from a GIWMS site's home page and crawl them."""
    home = client.html(base + "/", patient=True)
    if home is None:
        print(f"   [unreachable] {base} - skipped", file=sys.stderr)
        return
    cats: dict[str, str] = {}
    for u, text in _links(home, base + "/"):
        m = re.match(re.escape(base) + r"(/category/[^/?#\s]+)", u.strip())
        if m and text and _LEGAL_CAT.search(text) and (not only or any(o in m.group(1) for o in only)):
            cats.setdefault(m.group(1), text)
    seen = set()
    for cat, label in cats.items():
        for d in giwms_listing(client, base, cat, max_pages=opts.max_pages or 6):
            if d["url"] in seen or NOISE_TITLE.search(d["title"]):
                continue
            seen.add(d["url"])
            t = d["title"]
            if re.search(r"नियमावली|विनियमावली|नियमहरू|regulations?\b|rules?\b", t, re.I):
                kind, dtype = "regulation", "rule"
            elif re.search(r"ऐन\b|\bact\b", t, re.I) and "निर्देशिका" not in t:
                kind, dtype = "act", "act"
            else:
                kind, dtype = "directive", "directive"
            yield {**d, "kind": kind, "doc_type": dtype, "source_list": label}


def _first_reachable(client: Client, bases: tuple[str, ...]) -> str:
    """The first base URL whose home page answers (a site can serve one scheme/host
    spelling and reset the others). Falls back to the first candidate."""
    for b in bases:
        if client.html(b + "/", patient=False) is not None:
            return b
    return bases[0]


# NIA is not a GIWMS site: /law/<slug> pages are tables (title | "Updated At" date | PDF link(s)).
# (slug, kind, doc_type)
NIA_LAW_PAGES = [
    ("insurance-act", "act", "act"), ("insurance-regulation", "regulation", "rule"),
    ("insurance-board-by-laws", "regulation", "rule"), ("directive", "directive", "directive"),
    ("circular", "circular", "directive"), ("risk-based-capital", "directive", "directive"),
    ("agent", "directive", "directive"), ("aml", "directive", "directive"),
]


def nia_rows(html: str) -> Iterator[dict]:
    """(title, ISO date, pdf url) rows of one NIA /law/ page. Only the main table is read - the
    page also carries a sidebar of the latest notices, which are not legal texts."""
    start = html.find('<table class="table table-main"')
    if start < 0:
        return
    region = html[start: html.find("</table>", start)]
    for tr in region.split("<tr")[1:]:
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        pdfs = re.findall(r'href="([^"]+\.pdf)"', tr, re.I)
        if len(tds) < 2 or not pdfs:
            continue
        title = _clean(re.sub(r"<[^>]+>", " ", tds[0]))
        try:
            date = time.strftime("%Y-%m-%d", time.strptime(_clean(re.sub(r"<[^>]+>", " ", tds[1])), "%d %b %Y"))
        except ValueError:
            date = ""
        for u in dict.fromkeys(pdfs):
            yield {"title": title, "published": date, "url": u}


@authority("nia")
def scrape_nia(client: Client, opts) -> Iterator[dict]:
    """Nepal Insurance Authority (nia.gov.np; formerly Beema Samiti). Its HTTPS endpoint resets
    the connection from the build sandbox (proxy 502 / tunnel closed); the plain-HTTP site
    answers, so both are tried (public documents only, nothing is submitted). Acts, regulations,
    bylaws, directives, circulars, RBC and agent/AML rules, from the site's /law/ tables."""
    base = _first_reachable(client, ("http://nia.gov.np", "https://nia.gov.np"))
    seen: set[str] = set()
    for slug, kind, dtype in NIA_LAW_PAGES:
        page_url = f"{base}/law/{slug}"
        r = client.html(page_url, patient=True)
        if r is None:
            continue
        for d in nia_rows(r.html_content):
            if d["url"] in seen or NOISE_TITLE.search(d["title"]):
                continue
            seen.add(d["url"])
            lang = "en" if re.search(r"\(English\)|english", d["title"], re.I) else "ne"
            yield {**d, "kind": kind, "doc_type": dtype, "source_list": slug, "page_url": page_url, "lang": lang}


@authority("moless")
def scrape_moless(client: Client, opts) -> Iterator[dict]:
    """Ministry of Labour, Employment and Social Security: the bare host moless.gov.np returns
    502 from the sandbox, https://www.moless.gov.np answers."""
    yield from _giwms_site(client, _first_reachable(client, ("https://www.moless.gov.np", "https://moless.gov.np")), opts)


@authority("ppmo")
def scrape_ppmo(client: Client, opts) -> Iterator[dict]:
    """Public Procurement Monitoring Office: PPA/PPR texts, directives and criteria."""
    yield from _giwms_site(client, "https://www.ppmo.gov.np", opts, only=("acts-regulations", "directory-and-criteria", "1157"))


@authority("gazette")
def scrape_gazette(client: Client, opts) -> Iterator[dict]:
    """Nepal Gazette (rajpatra.dop.gov.np). Not reachable from the build sandbox; the
    Law Commission index already carries the consolidated statutes the Gazette prints."""
    if client.html("https://rajpatra.dop.gov.np/", patient=False) is None:
        print("   [unreachable] rajpatra.dop.gov.np - skipped", file=sys.stderr)
    return
    yield  # pragma: no cover  (generator marker)


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------
AUTHORITY_NAMES = {
    "nrb": "Nepal Rastra Bank", "ird": "Inland Revenue Department", "sebon": "Securities Board of Nepal",
    "ocr": "Office of the Company Registrar", "nia": "Nepal Insurance Authority",
    "moless": "Ministry of Labour, Employment and Social Security", "ppmo": "Public Procurement Monitoring Office",
    "gazette": "Nepal Gazette", "lawcommission-gap": "Nepal Law Commission",
}
GIWMS_FILE_AUTHORITIES = {"ird", "ocr", "nia", "moless", "ppmo", "lawcommission-gap"}


def run_authority(name: str, client: Client, opts) -> dict:
    fn = AUTHORITIES[name]
    store = Store(name)
    n = {"listed": 0, "downloaded": 0, "cached": 0, "failed": 0, "already_in_corpus": 0}
    for doc in fn(client, opts):
        # statutes the Law Commission pass already delivered (IRD's consolidated
        # tax acts are kept: they carry later Finance-Act amendments)
        if doc["kind"] == "act" and name not in ("ird", "lawcommission-gap") and not opts.no_skip_existing and in_corpus(doc["title"]):
            n["already_in_corpus"] += 1
            continue
        n["listed"] += 1
        if opts.limit and n["listed"] > opts.limit:
            break
        if opts.list_only:
            print(f"[{name}] {doc.get('published', '')[:12]:12} {doc['title'][:100]} <{doc['url'][-60:]}>")
            continue
        doc["authority_name"] = AUTHORITY_NAMES.get(name, name)
        if name in GIWMS_FILE_AUTHORITIES and "/content/" in doc["url"]:
            recs = []
            cached = 0
            for f in giwms_files(client, doc["url"]):
                if store.has_file(f):
                    recs.append(store.records[f])
                    cached += 1
                else:
                    recs += download(client, store, {**doc, "url": f, "page_url": doc["url"]}, follow=False)
            if recs and cached == len(recs):
                n["cached"] += 1
                continue
        else:
            if store.has_file(doc["url"]):
                n["cached"] += 1
                continue
            recs = download(client, store, doc)
        if recs:
            n["downloaded"] += len(recs)
            print(f"[{name}] + {doc['title'][:80]}  ({sum(r['size'] for r in recs) >> 10} KB)")
        else:
            n["failed"] += 1
    return n


def cmd_stats():
    for name in sorted(os.listdir(OUT_ROOT)) if os.path.isdir(OUT_ROOT) else []:
        if not os.path.isdir(os.path.join(OUT_ROOT, name)):
            continue
        s = Store(name)
        have = [r for r in s.records.values() if s.has_file(r["url"])]
        print(f"{name:12} {len(have):4} files  {sum(r['size'] for r in have) / 1e6:7.1f} MB")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", nargs="?", default="scrape", choices=["scrape", "stats"])
    ap.add_argument("--authority", default="all", help="one of %s, or 'all' (default)" % ", ".join(sorted(AUTHORITIES)))
    ap.add_argument("--max-pages", type=int, default=0, help="cap listing pages per category (0 = per-source default)")
    ap.add_argument("--limit", type=int, default=0, help="stop after N documents per authority")
    ap.add_argument("--list-only", action="store_true", help="print what would be fetched, download nothing")
    ap.add_argument("--no-skip-existing", action="store_true", help="also fetch acts whose title is already in the corpus")
    ap.add_argument("--delay", type=float, default=MIN_INTERVAL, help="min seconds between requests to one host")
    opts = ap.parse_args(argv)
    if opts.command == "stats":
        return cmd_stats()
    names = sorted(AUTHORITIES) if opts.authority == "all" else [a.strip() for a in opts.authority.split(",")]
    for a in names:
        if a not in AUTHORITIES:
            ap.error(f"unknown authority {a!r}; choose from {sorted(AUTHORITIES)}")
    client = Client(min_interval=max(opts.delay, 1.0))  # never faster than 1 req/s/host
    for a in names:
        print(f"== {a}", file=sys.stderr)
        res = run_authority(a, client, opts)
        print(f"== {a}: {res}   http={client.stats}", file=sys.stderr)
        if not opts.list_only and os.path.exists(Store(a).manifest):
            Store(a).compact()  # one record per URL (the log is append-only while running)


if __name__ == "__main__":
    main()
