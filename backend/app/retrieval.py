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
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sqlite3
import threading
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np
from scipy import sparse

from .text_norm import detect_language, fold, tokenize  # noqa: F401  (re-exported)

DATA_DIR = Path(__file__).parent / "data"
CORPUS_DIR = DATA_DIR / "corpus"
LEGACY_CORPUS = DATA_DIR / "corpus.json"
CACHE_DIR = DATA_DIR / "index_cache"

K1, B = 1.4, 0.72
AUTHORITY = {
    "constitution": 1.18, "act": 1.12, "rule": 1.04, "precedent": 1.05, "order": 0.97,
    "directive": 0.97, "treaty": 0.95, "amendment": 1.0, "gazette": 0.95, "other": 0.7,
}
RRF_K = 60

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
        self._local = threading.local()
        if not self._load_cache():
            self._build(entries)

    # -- storage --------------------------------------------------------
    def _paths(self):
        base = CACHE_DIR / self.digest
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
        rows: list[int] = []
        cols: list[int] = []
        vals: list[int] = []
        lengths: list[int] = []
        prior, keys, ids, cats, dtypes, titles = [], [], [], [], [], []
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
            dtypes.append(e.get("doc_type") or "")
            titles.append(e.get("doc_title_ne") or e.get("title_ne") or e["id"])
            batch.append((i + 1, json.dumps(e, ensure_ascii=False)))
            if len(batch) >= 2000:
                con.executemany("INSERT INTO p VALUES (?, ?)", batch)
                batch = []
        if batch:
            con.executemany("INSERT INTO p VALUES (?, ?)", batch)
        con.commit()
        con.close()

        n = len(ids)
        lengths_a = np.array(lengths, dtype=np.float32)
        tf = sparse.coo_matrix(
            (np.array(vals, dtype=np.float32), (np.array(rows, dtype=np.int32), np.array(cols, dtype=np.int32))),
            shape=(n, len(vocab)),
        )
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

        tmp_db.replace(dbpath)
        try:
            sparse.save_npz(mpath, self.W)
            vpath.write_text(json.dumps(vocab, ensure_ascii=False), encoding="utf-8")
            np.savez(metapath, prior=self.prior, text_key=self.text_key, ids=np.array(ids),
                     category=np.array(cats), doc_type=np.array(dtypes), doc_title=np.array(titles))
        except OSError:
            pass  # read-only deploy: in-memory index still works for this process

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
    ) -> list[dict]:
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
            doc_key = self.doc_title[i]
            cap = 1 if self.doc_type[i] == "other" else per_doc_cap  # reports/dictionaries: one passage
            if per_doc[doc_key] >= cap:
                continue
            key = int(self.text_key[i])
            if key in seen_text:
                continue  # same provision published in two documents
            seen_text.add(key)
            per_doc[doc_key] += 1
            results.append({**self.get(i), "score": float(best_raw[i]), "rrf": float(fused[i])})
        return results


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
                _index = Index(entries, digest)
    return _index


def retrieve(query: str, lang: str = "auto", top_k: int = 4) -> list[dict]:
    """Backwards-compatible single-query search."""
    return get_index().search([query], top_k=top_k)


def corpus_stats() -> dict:
    idx = get_index()
    by: dict[str, int] = defaultdict(int)
    for t, c in zip(idx.doc_type, idx.category):
        by[t or c] += 1
    docs = len({t for t, c in zip(idx.doc_title, idx.category) if c == "law"})
    return {"entries": len(idx), "by_type": dict(by), "law_documents": docs,
            "vocab": len(idx.vocab), "digest": idx.digest}
