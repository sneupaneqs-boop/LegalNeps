"""BM25 search over the government-sourced corpus (laws + precedents).

The corpus is loaded from gzip JSONL shards (backend/app/data/corpus/), and
the BM25 term matrix is cached on disk keyed by the corpus digest, so
restarts are fast. Ranking = BM25 over folded/stemmed tokens (see
text_norm), fused across several query phrasings with reciprocal rank
fusion, times a small authority prior (constitution/acts above reports),
with a per-document cap so one long act can't crowd out everything else.
"""
from __future__ import annotations

import gzip
import json
import threading
from collections import defaultdict
from pathlib import Path
from typing import Iterable

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


def _index_text(e: dict) -> str:
    parts = [
        e.get("doc_title_ne") or "", e.get("doc_title_en") or "",
        e.get("title_ne") or "", e.get("title_en") or "", e.get("title_ne") or "",
        e.get("topic") or "", e.get("text_ne") or "", e.get("text_en") or "",
        e.get("source_ne") or "", e.get("source_en") or "",
    ]
    return "\n".join(parts)


def load_entries() -> tuple[list[dict], str]:
    manifest = CORPUS_DIR / "manifest.json"
    if manifest.exists():
        m = json.loads(manifest.read_text(encoding="utf-8"))
        entries: list[dict] = []
        for name in m["files"]:
            with gzip.open(CORPUS_DIR / name, "rt", encoding="utf-8") as f:
                entries.extend(json.loads(line) for line in f)
        return entries, m["digest"]
    entries = json.loads(LEGACY_CORPUS.read_text(encoding="utf-8"))
    return entries, "legacy-%d" % len(entries)


class Index:
    def __init__(self, entries: list[dict], digest: str):
        self.entries = entries
        self.digest = digest
        self.by_id = {e["id"]: i for i, e in enumerate(entries)}
        self.prior = np.array([_prior(e) for e in entries], dtype=np.float32)
        if not self._load_cache():
            self._build()
            self._save_cache()

    # -- building -----------------------------------------------------
    def _build(self):
        vocab: dict[str, int] = {}
        rows, cols, vals = [], [], []
        lengths = np.zeros(len(self.entries), dtype=np.float32)
        for i, e in enumerate(self.entries):
            counts: dict[int, int] = defaultdict(int)
            toks = tokenize(_index_text(e))
            lengths[i] = len(toks)
            for t in toks:
                j = vocab.get(t)
                if j is None:
                    j = vocab[t] = len(vocab)
                counts[j] += 1
            rows.extend([i] * len(counts))
            cols.extend(counts.keys())
            vals.extend(counts.values())
        n = len(self.entries)
        tf = sparse.csr_matrix(
            (np.array(vals, dtype=np.float32), (np.array(rows), np.array(cols))),
            shape=(n, len(vocab)),
        )
        df = np.bincount(tf.indices, minlength=len(vocab)).astype(np.float32)
        idf = np.log(1 + (n - df + 0.5) / (df + 0.5)).astype(np.float32)
        avgdl = float(lengths.mean()) if n else 1.0
        # floor at half the average length so a 20-word clause that happens to
        # contain one query term doesn't outrank a substantive provision
        dl = np.maximum(lengths, 0.5 * avgdl)
        norm = K1 * (1 - B + B * dl / max(avgdl, 1e-6))
        tf = tf.tocoo()
        w = tf.data * (K1 + 1) / (tf.data + norm[tf.row]) * idf[tf.col]
        self.W = sparse.csc_matrix((w.astype(np.float32), (tf.row, tf.col)), shape=tf.shape)
        self.vocab = vocab

    def _cache_paths(self):
        return CACHE_DIR / f"{self.digest}.npz", CACHE_DIR / f"{self.digest}.vocab.json"

    def _load_cache(self) -> bool:
        mpath, vpath = self._cache_paths()
        if not (mpath.exists() and vpath.exists()):
            return False
        try:
            self.W = sparse.load_npz(mpath).tocsc()
            self.vocab = json.loads(vpath.read_text(encoding="utf-8"))
            return self.W.shape[0] == len(self.entries)
        except Exception:  # noqa: BLE001 - stale/corrupt cache: rebuild
            return False

    def _save_cache(self):
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            mpath, vpath = self._cache_paths()
            sparse.save_npz(mpath, self.W)
            vpath.write_text(json.dumps(self.vocab, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass  # read-only deploys just rebuild on start

    # -- querying -----------------------------------------------------
    def bm25(self, query: str) -> np.ndarray:
        ids = [self.vocab[t] for t in dict.fromkeys(tokenize(query)) if t in self.vocab]
        if not ids:
            return np.zeros(len(self.entries), dtype=np.float32)
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
        fused = np.zeros(len(self.entries), dtype=np.float32)
        best_raw = np.zeros(len(self.entries), dtype=np.float32)
        for q, w in weighted.items():
            s = self.bm25(q) * self.prior
            if not s.any():
                continue
            best_raw = np.maximum(best_raw, s)
            top = np.argpartition(-s, min(300, len(s) - 1))[:300]
            top = top[np.argsort(-s[top])]
            for rank, i in enumerate(top):
                if s[i] <= 0:
                    break
                fused[i] += w / (RRF_K + rank)

        boost_toks = [set(tokenize(t)) for t in boost_titles if t]
        if boost_toks:
            cand = np.nonzero(fused)[0]
            for i in cand:
                title_toks = set(tokenize(self.entries[i].get("doc_title_ne") or self.entries[i].get("title_ne") or ""))
                if any(bt and len(bt & title_toks) / len(bt) >= 0.6 for bt in boost_toks):
                    fused[i] *= 1.35

        order = np.argsort(-fused)
        results, per_doc, seen_text = [], defaultdict(int), set()
        for i in order:
            if fused[i] <= 0 or len(results) >= top_k:
                break
            e = self.entries[i]
            if category and e.get("category") != category:
                continue
            doc_key = e.get("doc_title_ne") or e["id"]
            cap = 1 if e.get("doc_type") == "other" else per_doc_cap  # reports/dictionaries: one passage
            if per_doc[doc_key] >= cap:
                continue
            text_key = fold(e.get("text_ne") or e.get("text_en") or "")[:160]
            if text_key in seen_text:
                continue  # same provision published in two documents
            seen_text.add(text_key)
            per_doc[doc_key] += 1
            results.append({**e, "score": float(best_raw[i]), "rrf": float(fused[i])})
        return results


_index: Index | None = None
_lock = threading.Lock()


def get_index() -> Index:
    global _index
    if _index is None:
        with _lock:
            if _index is None:
                entries, digest = load_entries()
                _index = Index(entries, digest)
    return _index


def retrieve(query: str, lang: str = "auto", top_k: int = 4) -> list[dict]:
    """Backwards-compatible single-query search."""
    return get_index().search([query], top_k=top_k)


def corpus_stats() -> dict:
    idx = get_index()
    by = defaultdict(int)
    for e in idx.entries:
        by[e.get("doc_type") or e.get("category")] += 1
    docs = len({e.get("doc_title_ne") for e in idx.entries if e.get("category") == "law"})
    return {"entries": len(idx.entries), "by_type": dict(by), "law_documents": docs,
            "vocab": len(idx.vocab), "digest": idx.digest}

