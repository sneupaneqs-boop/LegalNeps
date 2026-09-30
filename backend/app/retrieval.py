"""BM25 search over the government-sourced corpus (laws + precedents).

The corpus ships as gzip JSONL shards (backend/app/data/corpus/). On first
start they're compiled into an on-disk cache keyed by the corpus digest:
the BM25 weight matrix (.npz), vocabulary, compact per-passage metadata, and
a SQLite store holding the full passages. Only the matrix and metadata live
in memory; passage text is read from SQLite for the handful of results
returned, so memory stays small even with hundreds of thousands of passages.

Ranking = BM25 over folded/stemmed tokens (text_norm), fused across several
weighted query phrasings (reciprocal rank fusion), times an authority prior
(constitution/acts above reports, commencement clauses down-weighted), with a
per-document cap and duplicate-text collapsing.

Hybrid: when the dense encoder + corpus vectors are available (app/dense.py), each query's
semantic ranking (multilingual-e5-small cosine over every passage) is fused with its BM25
ranking, by reciprocal rank, before the boosts and filters run. Without them (no vectors, no
model files, DENSE=0) search is BM25-only, exactly as before.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import logging
import os
import re
import sqlite3
import threading
from array import array
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np
from scipy import sparse

from .doc_meta import classify_status, extract_doc_meta
from .text_norm import detect_language, fold, tokenize  # noqa: F401  (re-exported)

DATA_DIR = Path(__file__).parent / "data"
CORPUS_DIR = DATA_DIR / "corpus"
LEGACY_CORPUS = DATA_DIR / "corpus.json"
CACHE_DIR = DATA_DIR / "index_cache"

# bump when tokenisation/weighting changes so stale on-disk caches are rebuilt
INDEX_VERSION = 5
K1, B = 1.4, 0.72
AUTHORITY = {
    "constitution": 1.18, "act": 1.12, "rule": 1.04, "precedent": 1.05, "order": 0.97,
    "directive": 0.97, "treaty": 0.95, "amendment": 1.0, "gazette": 0.95, "other": 0.7,
}
RRF_K = 60
# Hybrid fusion knobs (tuned on the default + realworld eval sets only - never on heldout)
HYBRID = {
    "dense_weight": 1.5,    # weight of a query's dense ranking relative to its BM25 ranking
    "dense_rrf_k": 100,     # RRF constant for the dense ranking (flatter than BM25's: cosines are compressed)
    "dense_depth": 100,     # passages taken from each dense ranking
    "dense_min_w": 0.3,     # queries lighter than this (single glossary terms) skip the dense side
    "primary_floor": 0.0,   # dense weight of the first query (the user's message) is at least this
    "solo": 0.6,            # dense-only candidates (absent from every BM25 top-`gate_depth`) count this fraction
    "gate_depth": 300,
    "prior_pow": 0.5,       # dense ranking score = cosine * prior**prior_pow (0 = pure cosine)
}
# "hybrid" (default), "bm25" or "dense" - the last two exist for eval/ablation (RETRIEVAL_MODE env)
DEFAULT_MODE = os.environ.get("RETRIEVAL_MODE", "hybrid")

_LOW_VALUE_HEADINGS = ("संक्षिप्त नाम र प्रारम्भ", "सङ्क्षिप्त नाम र प्रारम्भ", "संक्षिप्त नाम", "खारेजी र बचाउ", "खारेजी")
_LOW_VALUE_DOCS = ("वार्षिक प्रतिवेदन", "annual report", "विषय-सूची", "सूचनाको हक बमोजिम सार्वजनिक")


def _prior(e: dict) -> float:
    """Authority of the source x usefulness of this particular passage."""
    kind = e.get("doc_type") or ("precedent" if e.get("category") == "precedent" else "other")
    p = AUTHORITY.get(kind, 1.0)
    if e.get("curated"):
        p *= 1.08
    heading = e.get("title_ne") or ""
    if any(heading.startswith(h) for h in _LOW_VALUE_HEADINGS):
        p *= 0.5  # "short title and commencement" / repeal clauses rarely answer anything
    doc = (e.get("doc_title_ne") or "").lower()
    if any(d in doc for d in _LOW_VALUE_DOCS):
        p *= 0.45  # the Commission's own annual reports mention every topic in passing
    return p


def _entry_status(e: dict, doc_status_cache: dict[str, str]) -> str:
    status = e.get("status")
    if status:
        return status
    if e.get("category") != "law":
        return "in_force"  # precedents etc. aren't subject to bill/enactment status
    # curated entries (backend/app/data/corpus.json) have no doc_title_ne and
    # no preamble/header to run extract_doc_meta on - they're one hand-picked
    # section each - so a "विधेयक" (bill) title can only be caught by name,
    # and it may only appear in the citation, not the (possibly untitled)
    # section heading - e.g. title_ne "राष्ट्र ऋण उठाउन सक्ने" vs. source_ne
    # "राष्ट्र ऋण उठाउने विधेयक, २०८३" for the same entry - so check all of them
    title = e.get("doc_title_ne") or ""
    if e.get("curated"):
        names = (e.get("doc_title_ne"), e.get("title_ne"), e.get("source_ne"))
        return "bill" if any(n and "विधेयक" in n for n in names) else "in_force"
    cached = doc_status_cache.get(title)
    if cached is None:
        meta = extract_doc_meta(e.get("text_ne") or "")
        cached = doc_status_cache[title] = classify_status(title, meta)
    return cached


_ORDINANCE = re.compile(r"अध्यादेश")
_STUDY = re.compile(r"(अध्ययन|प्रतिवेदन|आवश्यकता)$|सम्बन्धी अध्ययन")
_TITLE_YEAR = re.compile(r"([०-९0-9]{4})\s*$")
_DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def _current_bs_year() -> int:
    try:
        import nepali_datetime
        return nepali_datetime.date.today().year
    except Exception:  # noqa: BLE001
        import datetime
        return datetime.date.today().year + 57  # BS runs ~56.7 years ahead of AD


def _temporal_status(title: str, doc_type: str, status: str) -> tuple[str, str]:
    """Corrects status/type the source metadata gets wrong for law that isn't
    permanent. An अध्यादेश (ordinance) is temporary: under the Constitution
    it lapses 60 days after the House next meets unless Parliament replaces
    it, so one from before last year is certainly no longer law. Law
    Commission studies/reports filed under a statute category aren't law."""
    if _STUDY.search(title) and doc_type in ("constitution", "act", "rule"):
        return "other", "unknown"
    if _ORDINANCE.search(title) and doc_type in ("act", "constitution", "rule", "order"):
        m = _TITLE_YEAR.search(title)
        year = int(m.group(1).translate(_DEV_DIGITS)) if m else None
        if year is not None and year < _current_bs_year() - 1:
            return "act", "lapsed"
        return "act", "ordinance"  # recent or undated: temporary, may or may not still apply
    return doc_type, status


def doc_slug(title: str) -> str:
    """Stable, URL-safe id for a document's law-browser page, derived from
    its title rather than a per-entry field - works uniformly whether or not
    the entry carries S2's doc_id (scraped law_entries() only; curated
    entries in corpus.json never do)."""
    return hashlib.blake2b(title.encode("utf-8"), digest_size=6).hexdigest()


def _text_key(e: dict) -> int:
    key = fold(e.get("text_ne") or e.get("text_en") or "")[:160]
    return int.from_bytes(hashlib.blake2b(key.encode("utf-8"), digest_size=8).digest(), "little", signed=True)


def _index_text(e: dict) -> str:
    parts = [
        e.get("doc_title_ne") or "", e.get("doc_title_en") or "",
        e.get("title_ne") or "", e.get("title_en") or "", e.get("title_ne") or "",
        e.get("topic") or "", e.get("text_ne") or "", e.get("text_en") or "",
        e.get("source_ne") or "", e.get("source_en") or "",
    ]
    return "\n".join(parts)


def corpus_source() -> tuple[Iterable[dict], str]:
    manifest = CORPUS_DIR / "manifest.json"
    if manifest.exists():
        m = json.loads(manifest.read_text(encoding="utf-8"))

        def stream():
            for name in m["files"]:
                with gzip.open(CORPUS_DIR / name, "rt", encoding="utf-8") as f:
                    for line in f:
                        yield json.loads(line)
        return stream(), m["digest"]
    entries = json.loads(LEGACY_CORPUS.read_text(encoding="utf-8"))
    return entries, "legacy-%d" % len(entries)


class Index:
    def __init__(self, entries: Iterable[dict], digest: str):
        self.digest = digest
        self.dense = None  # app.dense.Dense once attach_dense() ran and found vectors + model
        self._local = threading.local()
        if not self._load_cache():
            self._build(entries)

    # -- storage --------------------------------------------------------
    def _paths(self):
        base = CACHE_DIR / f"{self.digest}-v{INDEX_VERSION}"
        return (Path(f"{base}.npz"), Path(f"{base}.vocab.json"), Path(f"{base}.meta.npz"), Path(f"{base}.sqlite"))

    def _db(self) -> sqlite3.Connection:
        con = getattr(self._local, "con", None)
        if con is None:
            con = sqlite3.connect(f"file:{self._paths()[3]}?mode=ro", uri=True, check_same_thread=False)
            self._local.con = con
        return con

    def _load_cache(self) -> bool:
        mpath, vpath, metapath, dbpath = self._paths()
        if not all(p.exists() for p in (mpath, vpath, metapath, dbpath)):
            return False
        try:
            self.W = sparse.load_npz(mpath).tocsc()
            self.vocab = json.loads(vpath.read_text(encoding="utf-8"))
            meta = np.load(metapath, allow_pickle=False)
            self.prior = meta["prior"]
            self.text_key = meta["text_key"]
            self.ids = meta["ids"].tolist()
            self.category = meta["category"].tolist()
            self.doc_type = meta["doc_type"].tolist()
            self.doc_title = meta["doc_title"].tolist()
            self.status = meta["status"].tolist()
            self.slug = meta["slug"].tolist()
            return self.W.shape[0] == len(self.ids)
        except Exception:  # noqa: BLE001 - stale/corrupt cache: rebuild
            return False

    def _build(self, entries: Iterable[dict]):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        mpath, vpath, metapath, dbpath = self._paths()
        tmp_db = Path(f"{dbpath}.tmp")
        if tmp_db.exists():
            tmp_db.unlink()
        con = sqlite3.connect(tmp_db)
        con.execute("CREATE TABLE p (rowid INTEGER PRIMARY KEY, doc TEXT NOT NULL)")

        vocab: dict[str, int] = {}
        # compact C arrays: millions of Python ints in lists would double peak memory
        rows, cols, vals, lengths = array("i"), array("i"), array("f"), array("i")
        prior, keys, ids, cats, dtypes, titles, statuses, slugs = [], [], [], [], [], [], [], []
        # corpus shards built before doc-level status existed carry no
        # "status" field; compute it lazily from each doc's first chunk (its
        # header/preamble) the same way build_corpus.py does, so bills are
        # still excluded without a full corpus rebuild. law_entries() writes
        # a document's chunks consecutively, so the first entry seen for a
        # given title is always that document's first chunk.
        doc_status_cache: dict[str, str] = {}
        batch = []
        for i, e in enumerate(entries):
            counts: dict[int, int] = defaultdict(int)
            toks = tokenize(_index_text(e))
            lengths.append(len(toks))
            for t in toks:
                j = vocab.get(t)
                if j is None:
                    j = vocab[t] = len(vocab)
                counts[j] += 1
            rows.extend([i] * len(counts))
            cols.extend(counts.keys())
            vals.extend(counts.values())
            prior.append(_prior(e))
            keys.append(_text_key(e))
            ids.append(e["id"])
            cats.append(e.get("category") or "law")
            title = e.get("doc_title_ne") or e.get("title_ne") or e["id"]
            dtype, status = _temporal_status(title, e.get("doc_type") or "", _entry_status(e, doc_status_cache))
            if status != e.get("status") or dtype != e.get("doc_type"):
                e = {**e, "doc_type": dtype, "status": status}  # stored row matches the index
            dtypes.append(dtype)
            titles.append(title)
            statuses.append(status)
            slugs.append(doc_slug(titles[-1]))
            batch.append((i + 1, json.dumps(e, ensure_ascii=False)))
            if len(batch) >= 2000:
                con.executemany("INSERT INTO p VALUES (?, ?)", batch)
                batch = []
        if batch:
            con.executemany("INSERT INTO p VALUES (?, ?)", batch)
        con.commit()
        con.close()

        n = len(ids)
        lengths_a = np.frombuffer(lengths, dtype=np.int32).astype(np.float32)
        tf = sparse.coo_matrix(
            (np.frombuffer(vals, dtype=np.float32), (np.frombuffer(rows, dtype=np.int32),
                                                     np.frombuffer(cols, dtype=np.int32))),
            shape=(n, len(vocab)),
        )
        del rows, cols, vals
        df = np.bincount(tf.col, minlength=len(vocab)).astype(np.float32)
        idf = np.log(1 + (n - df + 0.5) / (df + 0.5)).astype(np.float32)
        avgdl = float(lengths_a.mean()) if n else 1.0
        # floor at half the average length so a 20-word clause that happens to
        # contain one query term doesn't outrank a substantive provision
        dl = np.maximum(lengths_a, 0.5 * avgdl)
        norm = K1 * (1 - B + B * dl / max(avgdl, 1e-6))
        w = tf.data * (K1 + 1) / (tf.data + norm[tf.row]) * idf[tf.col]
        self.W = sparse.csc_matrix((w.astype(np.float32), (tf.row, tf.col)), shape=tf.shape)
        self.vocab = vocab
        self.prior = np.array(prior, dtype=np.float32)
        self.text_key = np.array(keys, dtype=np.int64)
        self.ids, self.category, self.doc_type, self.doc_title = ids, cats, dtypes, titles
        self.status = statuses
        self.slug = slugs

        tmp_db.replace(dbpath)
        try:
            sparse.save_npz(mpath, self.W, compressed=False)
            vpath.write_text(json.dumps(vocab, ensure_ascii=False), encoding="utf-8")
            np.savez(metapath, prior=self.prior, text_key=self.text_key, ids=np.array(ids),
                     category=np.array(cats), doc_type=np.array(dtypes), doc_title=np.array(titles),
                     status=np.array(statuses), slug=np.array(slugs))
        except OSError:
            pass  # read-only deploy: in-memory index still works for this process

    def attach_dense(self):
        """Load the query encoder + corpus vectors if available (best-effort, never raises)."""
        from . import dense
        self.dense = dense.load_dense(self.ids, self.digest)
        return self.dense

    # -- access -----------------------------------------------------------
    def __len__(self) -> int:
        return len(self.ids)

    def get(self, i: int) -> dict:
        row = self._db().execute("SELECT doc FROM p WHERE rowid = ?", (int(i) + 1,)).fetchone()
        return json.loads(row[0])

    def iter_entries(self) -> Iterator[dict]:
        for (doc,) in self._db().execute("SELECT doc FROM p ORDER BY rowid"):
            yield json.loads(doc)

    @property
    def entries(self) -> list[dict]:
        """All passages (loads everything - for scripts/evals, not requests)."""
        return list(self.iter_entries())

    # -- law browser --------------------------------------------------------
    @property
    def _doc_index(self) -> dict[str, list[int]]:
        """slug -> row indices, in corpus order (which is section order for
        scraped law_entries()), law entries only. Built once per process from
        the parallel arrays already in memory; not persisted."""
        cached = getattr(self, "_doc_index_cache", None)
        if cached is None:
            cached = defaultdict(list)
            for i, (slug, cat) in enumerate(zip(self.slug, self.category)):
                if cat == "law":
                    cached[slug].append(i)
            self._doc_index_cache = cached
        return cached

    def doc(self, slug: str, include_bills: bool = True) -> dict | None:
        """Doc-level metadata plus its ordered section list, for /law/[doc]."""
        rows = self._doc_index.get(slug)
        if not rows:
            return None
        status = self.status[rows[0]]
        if not include_bills and status == "bill":
            return None
        first = self.get(rows[0])
        # pre-S2 corpus shards (built before status/enacted_bs/amended_by
        # existed) carry status only via the in-memory fallback (self.status,
        # computed in _build()); the stored row itself has no enacted_bs/
        # amended_by at all. Backfill them here the same way, so the law
        # browser shows real dates instead of blanks without a corpus rebuild.
        if "enacted_bs" not in first and not first.get("curated"):
            first = {**first, **extract_doc_meta(first.get("text_ne") or "")}
        sections = []
        for i in rows:
            e = self.get(i)
            sections.append({
                "id": e["id"], "section": e.get("section"),
                "title_ne": e.get("title_ne"), "title_en": e.get("title_en"),
                "snippet": " ".join((e.get("text_ne") or "").split())[:160],
            })
        return {
            "slug": slug, "doc_title_ne": first.get("doc_title_ne") or first.get("title_ne"),
            "doc_title_en": first.get("doc_title_en"), "doc_type": first.get("doc_type"),
            "status": first.get("status") or status, "enacted_bs": first.get("enacted_bs"),
            "amended_by": first.get("amended_by") or [], "consolidated_upto": first.get("consolidated_upto"),
            "url": first.get("url"), "sections": sections,
        }

    def _section_positions(self, slug: str) -> dict[str, int]:
        """section label -> position within the doc's rows, built once per
        document (pinned playbook provisions look sections up on every chat)."""
        cache = self.__dict__.setdefault("_section_pos_cache", {})
        pos = cache.get(slug)
        if pos is None:
            pos = {}
            for k, i in enumerate(self._doc_index.get(slug, [])):
                pos.setdefault(self.get(i).get("section") or "", k)
            cache[slug] = pos
        return pos

    def section(self, slug: str, section: str) -> dict | None:
        """One section's full entry plus neighbouring sections, for
        /law/[doc]/[section]."""
        rows = self._doc_index.get(slug)
        if not rows:
            return None
        pos = self._section_positions(slug).get(section)
        if pos is None:
            return None
        entry = self.get(rows[pos])
        if not entry.get("status"):
            # pre-S2 corpus rows have no stored status; fall back to the
            # computed array (same backfill doc() already does)
            entry = {**entry, "status": self.status[rows[pos]]}
        prev_row = self.get(rows[pos - 1]) if pos > 0 else None
        next_row = self.get(rows[pos + 1]) if pos + 1 < len(rows) else None
        return {
            **entry, "slug": slug,
            "prev": {"section": prev_row.get("section"), "title_ne": prev_row.get("title_ne")} if prev_row else None,
            "next": {"section": next_row.get("section"), "title_ne": next_row.get("title_ne")} if next_row else None,
        }

    # -- querying -----------------------------------------------------------
    def bm25(self, query: str) -> np.ndarray:
        ids = [self.vocab[t] for t in dict.fromkeys(tokenize(query)) if t in self.vocab]
        if not ids:
            return np.zeros(len(self), dtype=np.float32)
        return np.asarray(self.W[:, ids].sum(axis=1)).ravel()

    def search(
        self,
        queries: Iterable[str | tuple[str, float]],
        top_k: int = 8,
        boost_titles: Iterable[str] = (),
        category: str | None = None,
        per_doc_cap: int = 3,
        include_bills: bool = False,
        doc_type: str | None = None,
        status: str | None = None,
        mode: str | None = None,
    ) -> list[dict]:
        """`mode`: "hybrid" (BM25 + dense when available), "bm25" or "dense" (ablations);
        None = DEFAULT_MODE. The first query is taken to be the user's own message."""
        mode = mode or DEFAULT_MODE
        weighted: dict[str, float] = {}
        for q in queries:
            text, w = (q, 1.0) if isinstance(q, str) else q
            text = text.strip()
            if text:
                weighted[text] = max(w, weighted.get(text, 0.0))
        if not weighted:
            return []
        n = len(self)
        fused = np.zeros(n, dtype=np.float32)
        best_raw = np.zeros(n, dtype=np.float32)
        use_bm25 = mode != "dense" or self.dense is None
        bm_best = np.full(n, 10**6, dtype=np.int32)  # best BM25 rank of each passage over the queries
        if use_bm25:
            for q, w in weighted.items():
                s = self.bm25(q) * self.prior
                if not s.any():
                    continue
                best_raw = np.maximum(best_raw, s)
                top = np.argpartition(-s, min(300, n - 1))[:300]
                top = top[np.argsort(-s[top])]
                for rank, i in enumerate(top):
                    if s[i] <= 0:
                        break
                    fused[i] += w / (RRF_K + rank)
                    if rank < bm_best[i]:
                        bm_best[i] = rank
        best_cos = None
        if mode != "bm25" and self.dense is not None:
            best_cos = self._fuse_dense(fused, weighted, bm_best)

        boost_toks = [set(tokenize(t)) for t in boost_titles if t]
        if boost_toks:
            for i in np.nonzero(fused)[0]:
                title_toks = _title_tokens(self.doc_title[i])
                if any(bt and len(bt & title_toks) / len(bt) >= 0.6 for bt in boost_toks):
                    fused[i] *= 1.35

        order = np.argsort(-fused)
        results, per_doc, seen_text = [], defaultdict(int), set()
        for i in order:
            if fused[i] <= 0 or len(results) >= top_k:
                break
            if category and self.category[i] != category:
                continue
            if doc_type and self.doc_type[i] != doc_type:
                continue
            if status:
                if self.status[i] != status:
                    continue
            elif not include_bills and self.status[i] in ("bill", "lapsed"):
                continue  # never cite a draft bill or a lapsed ordinance by default
            doc_key = self.doc_title[i]
            cap = 1 if self.doc_type[i] == "other" else per_doc_cap  # reports/dictionaries: one passage
            if per_doc[doc_key] >= cap:
                continue
            key = int(self.text_key[i])
            if key in seen_text:
                continue  # same provision published in two documents
            seen_text.add(key)
            per_doc[doc_key] += 1
            entry = self.get(i)
            if not entry.get("status"):
                # older shards store no status; the index computed it at build time
                entry["status"] = self.status[i]
            hit = {**entry, "score": float(best_raw[i]), "rrf": float(fused[i])}
            if best_cos is not None:
                hit["dense"] = round(float(best_cos[i]), 4)
            results.append(hit)
        return results

    def _fuse_dense(self, fused: np.ndarray, weighted: dict[str, float], bm_best: np.ndarray) -> np.ndarray | None:
        """Adds each eligible query's dense (cosine) ranking to `fused` in place, by reciprocal
        rank. Returns each passage's best cosine over the queries, or None if encoding failed
        (search then degrades to BM25 alone)."""
        h = HYBRID
        items = []
        for k, (q, w) in enumerate(weighted.items()):
            dw = max(w, h["primary_floor"]) if k == 0 else w
            if dw >= h["dense_min_w"]:
                items.append((q, dw))
        if not items:
            return None
        try:
            cos = self.dense.scores([q for q, _ in items])  # (n, m)
        except Exception as e:  # noqa: BLE001 - a broken encoder must not break search
            logging.getLogger("kanooni.dense").warning("dense query failed, BM25 only: %s", e)
            return None
        n = len(self)
        depth = min(h["dense_depth"], n - 1)
        prior = self.prior ** h["prior_pow"] if h["prior_pow"] else None
        for j, (_, dw) in enumerate(items):
            s = cos[:, j] if prior is None else cos[:, j] * prior
            top = np.argpartition(-s, depth)[:depth]
            top = top[np.argsort(-s[top])]
            gate = np.where(bm_best[top] < h["gate_depth"], 1.0, h["solo"]).astype(np.float32)
            fused[top] += h["dense_weight"] * dw * gate / (h["dense_rrf_k"] + np.arange(len(top), dtype=np.float32))
        return cos.max(axis=1)


@lru_cache(maxsize=20000)
def _title_tokens(title: str) -> frozenset:
    return frozenset(tokenize(title))


_index: Index | None = None
_lock = threading.Lock()


def get_index() -> Index:
    global _index
    if _index is None:
        with _lock:
            if _index is None:
                entries, digest = corpus_source()
                idx = Index(entries, digest)
                idx.attach_dense()
                _index = idx
    return _index


def index_ready() -> bool:
    return _index is not None


def retrieve(query: str, lang: str = "auto", top_k: int = 4) -> list[dict]:
    """Backwards-compatible single-query search."""
    return get_index().search([query], top_k=top_k)


def corpus_stats() -> dict:
    idx = get_index()
    by: dict[str, int] = defaultdict(int)
    for t, c in zip(idx.doc_type, idx.category):
        by[t or c] += 1
    by_status: dict[str, int] = defaultdict(int)
    for s, c in zip(idx.status, idx.category):
        if c == "law":
            by_status[s] += 1
    docs = len({t for t, c in zip(idx.doc_title, idx.category) if c == "law"})
    return {"entries": len(idx), "by_type": dict(by), "by_status": dict(by_status), "law_documents": docs,
            "vocab": len(idx.vocab), "digest": idx.digest, "corpus_version": idx.digest}
