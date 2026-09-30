"""Dense (semantic, cross-lingual) retrieval, fused with BM25 inside retrieval.Index.search.

Encoder: intfloat/multilingual-e5-small (Xenova's int8 ONNX export) run with onnxruntime;
text is tokenised with sentencepiece (same segmentation as the HF tokenizer, at ~60MB instead
of the ~280MB the `tokenizers` package needs for this 250k-piece vocabulary). To fit Render's
512MB the model's 250k-row word-embedding table is pruned to the ~91k pieces that are
Devanagari / ASCII (`prepare_model`), which is done once at build time.

Corpus vectors (one 384-d int8 vector + float16 scale per passage) are computed offline by
scripts/build_dense.py and committed as app/data/dense/vectors.npz, keyed by passage id AND
the corpus digest. At runtime:

  * artifact absent / unreadable / wrong model  -> BM25-only, never an error
  * digest differs from the loaded corpus       -> vectors are reused for ids that still
    exist, the rest simply have no dense signal (logged with the count)
  * model files absent                          -> BM25-only

Search is a brute-force chunked int8 x float32 product over all passages (~70k x 384 =
28M multiply-adds, tens of ms) - no ANN index needed at this scale.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import urllib.request
from pathlib import Path

import numpy as np

log = logging.getLogger("kanooni.dense")

DATA_DIR = Path(__file__).parent / "data"
VECTORS_PATH = Path(os.environ.get("DENSE_VECTORS", DATA_DIR / "dense" / "vectors.npz"))
MODEL_DIR = Path(os.environ.get("DENSE_MODEL_DIR", DATA_DIR / "dense_model"))

MODEL_NAME = "multilingual-e5-small-int8-pruned"
DIM = 384
MAX_TOKENS = 256          # passages are truncated to this many tokens when embedded
QUERY_MAX_TOKENS = 128
QUERY_PREFIX, PASSAGE_PREFIX = "query: ", "passage: "
ARTIFACT_VERSION = 1

# Files fetched at build time (never committed). Pinned to a commit so builds are reproducible.
_HF = "https://huggingface.co/{repo}/resolve/{rev}/{path}"
MODEL_FILES = {
    "model_quantized.onnx": ("Xenova/multilingual-e5-small", "761b726dd34fb83930e26aab4e9ac3899aa1fa78", "onnx/model_quantized.onnx"),
    "spm.model": ("intfloat/multilingual-e5-small", "614241f622f53c4eeff9890bdc4f31cfecc418b3", "onnx/sentencepiece.bpe.model"),
}
ENCODER_FILE, KEEP_FILE, SPM_FILE = "encoder.onnx", "keep_ids.npy", "spm.model"

_KEEP_CHARS = ("ऀ-ॿ‌‍▁ -~–—‘’“”"
               "•° ।॥")


def enabled() -> bool:
    return os.environ.get("DENSE", "1").lower() not in ("0", "false", "off", "no")


# ---------------------------------------------------------------------------
# passage text (what gets embedded)
# ---------------------------------------------------------------------------
def passage_text(e: dict) -> str:
    """Document title + section heading + body, Nepali first, English title/heading when the
    passage carries them (lets English queries land on a Nepali provision)."""
    doc_ne, doc_en = (e.get("doc_title_ne") or "")[:110], (e.get("doc_title_en") or "")[:90]
    t_ne, t_en = (e.get("title_ne") or "")[:110], (e.get("title_en") or "")[:90]
    head = doc_ne + (f" ({doc_en})" if doc_en and doc_en != doc_ne else "")
    if t_ne and t_ne != doc_ne:
        head += " | " + t_ne + (f" ({t_en})" if t_en and t_en != t_ne else "")
    body = " ".join((e.get("text_ne") or e.get("text_en") or "").split())
    return f"{head}. {body[:900]}"


# ---------------------------------------------------------------------------
# model preparation (build time)
# ---------------------------------------------------------------------------
def model_ready(model_dir: Path = MODEL_DIR) -> bool:
    return all((model_dir / f).exists() for f in (ENCODER_FILE, KEEP_FILE, SPM_FILE))


def _download(url: str, dest: Path):
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    tmp.replace(dest)


def prepare_model(model_dir: Path = MODEL_DIR, force: bool = False) -> Path:
    """Download the int8 ONNX encoder + sentencepiece model and prune the embedding table.
    Needs the `onnx` and `sentencepiece` packages (both in requirements.txt; onnx is only
    imported here, never on the request path)."""
    model_dir.mkdir(parents=True, exist_ok=True)
    if model_ready(model_dir) and not force:
        return model_dir
    import onnx
    import sentencepiece as spm
    from onnx import numpy_helper

    for name, (repo, rev, path) in MODEL_FILES.items():
        if force or not (model_dir / name).exists():
            log.info("downloading %s", name)
            _download(_HF.format(repo=repo, rev=rev, path=path), model_dir / name)
    sp = spm.SentencePieceProcessor(model_file=str(model_dir / SPM_FILE))
    import re
    ok = re.compile(f"^[{_KEEP_CHARS}]+$")
    n_sp = sp.get_piece_size()
    # model ids: 0 <s>, 1 <pad>, 2 </s>, 3 <unk>, then spm id + 1
    keep = [0, 1, 2, 3] + [i + 1 for i in range(3, n_sp) if ok.match(sp.id_to_piece(i))]
    keep_arr = np.array(sorted(set(keep)), dtype=np.int64)

    m = onnx.load(str(model_dir / "model_quantized.onnx"))
    target = "embeddings.word_embeddings.weight_quantized"
    for init in m.graph.initializer:
        if init.name == target:
            w = numpy_helper.to_array(init)
            init.CopyFrom(numpy_helper.from_array(np.ascontiguousarray(w[keep_arr]), name=target))
            break
    else:
        raise RuntimeError("word-embedding initializer not found in the ONNX graph")
    tmp = model_dir / (ENCODER_FILE + ".part")
    onnx.save(m, str(tmp))
    np.save(model_dir / KEEP_FILE, keep_arr)
    tmp.replace(model_dir / ENCODER_FILE)
    (model_dir / "model_quantized.onnx").unlink(missing_ok=True)  # the 118MB original is no longer needed
    return model_dir


# ---------------------------------------------------------------------------
# encoder (runtime + build)
# ---------------------------------------------------------------------------
class Encoder:
    def __init__(self, model_dir: Path = MODEL_DIR, threads: int | None = None):
        import onnxruntime as ort
        import sentencepiece as spm

        self.sp = spm.SentencePieceProcessor(model_file=str(model_dir / SPM_FILE))
        keep = np.load(model_dir / KEEP_FILE)
        self.remap = np.full(self.sp.get_piece_size() + 1, 3, dtype=np.int64)  # unknown -> <unk>
        self.remap[keep] = np.arange(len(keep))
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads or int(os.environ.get("DENSE_THREADS", "2"))
        so.inter_op_num_threads = 1
        so.enable_cpu_mem_arena = False   # keeps RSS flat across differently-sized batches
        so.enable_mem_pattern = False
        so.add_session_config_entry("session.disable_prepacking", "1")  # ~13MB less RSS for ~20% slower GEMMs
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.sess = ort.InferenceSession(str(model_dir / ENCODER_FILE), so, providers=["CPUExecutionProvider"])

    def _ids(self, text: str, max_tokens: int) -> list[int]:
        raw = self.sp.encode(text)[: max_tokens - 2]
        # sentencepiece ids -> HF XLM-R ids: <s>=0, </s>=2, pieces shifted by one, unk=3
        return [0] + [3 if i == 0 else i + 1 for i in raw] + [2]

    def encode(self, texts: list[str], prefix: str, max_tokens: int = MAX_TOKENS, batch: int = 32) -> np.ndarray:
        """L2-normalised float32 embeddings, shape (len(texts), DIM). Batches are length-sorted."""
        if not texts:
            return np.zeros((0, DIM), dtype=np.float32)
        seqs = [self._ids(prefix + t, max_tokens) for t in texts]
        order = np.argsort([len(s) for s in seqs])
        out = np.zeros((len(texts), DIM), dtype=np.float32)
        for a in range(0, len(order), batch):
            idx = order[a:a + batch]
            width = max(len(seqs[i]) for i in idx)
            ids = np.full((len(idx), width), 1, dtype=np.int64)       # <pad>
            mask = np.zeros((len(idx), width), dtype=np.int64)
            for r, i in enumerate(idx):
                ids[r, :len(seqs[i])] = seqs[i]
                mask[r, :len(seqs[i])] = 1
            ids = self.remap[ids]
            hidden = self.sess.run(None, {"input_ids": ids, "attention_mask": mask,
                                          "token_type_ids": np.zeros_like(ids)})[0]
            m = mask[:, :, None].astype(np.float32)
            pooled = (hidden * m).sum(1) / np.maximum(m.sum(1), 1.0)
            out[idx] = pooled / np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9)
        return out


# ---------------------------------------------------------------------------
# vector store
# ---------------------------------------------------------------------------
def quantize(vecs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """float32 (n, DIM) -> int8 + per-vector float16 scale (cos ~ (q . x) * scale)."""
    amax = np.maximum(np.abs(vecs).max(axis=1), 1e-9)
    scale = (amax / 127.0).astype(np.float16)
    q = np.clip(np.rint(vecs / scale.astype(np.float32)[:, None]), -127, 127).astype(np.int8)
    return q, scale


def save_vectors(path: Path, ids: list[str], q: np.ndarray, scale: np.ndarray, digest: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = json.dumps({"version": ARTIFACT_VERSION, "model": MODEL_NAME, "digest": digest, "dim": DIM,
                       "n": len(ids), "max_tokens": MAX_TOKENS})
    tmp = path.with_name(path.name + ".tmp.npz")
    np.savez_compressed(tmp, ids=np.array(ids), q=q, scale=scale, meta=np.array(meta))
    tmp.replace(path)


class VectorStore:
    """int8 vectors aligned to an Index's row order. `have[i]` is False for rows with no vector."""

    def __init__(self, q: np.ndarray, scale: np.ndarray, have: np.ndarray, info: dict):
        self.q, self.scale, self.have, self.info = q, scale, have, info

    @classmethod
    def load(cls, path: Path, ids: list[str], digest: str) -> "VectorStore | None":
        """Vectors for `ids` (the loaded corpus's passage ids, in row order), or None when there
        is no usable artifact. Never raises."""
        try:
            if not Path(path).exists():
                log.warning("dense: no vector artifact at %s - BM25 only", path)
                return None
            z = np.load(path, allow_pickle=False)
            meta = json.loads(str(z["meta"]))
            if meta.get("model") != MODEL_NAME or meta.get("dim") != DIM or meta.get("version") != ARTIFACT_VERSION:
                log.warning("dense: vector artifact is for another model/version (%s) - BM25 only", meta.get("model"))
                return None
            a_ids, q, scale = z["ids"], z["q"], z["scale"]
            if not (len(a_ids) == len(q) == len(scale)) or q.ndim != 2 or q.shape[1] != DIM:
                log.warning("dense: vector artifact is internally inconsistent - BM25 only")
                return None
            n = len(ids)
            same_order = len(a_ids) == n and bool(np.array_equal(a_ids, np.asarray(ids)))
            if same_order:
                have = np.ones(n, dtype=bool)
                store = cls(q, scale.astype(np.float32), have, {**meta, "missing": 0, "exact": True})
                if meta.get("digest") != digest:
                    log.warning("dense: corpus digest differs (%s vs %s) but ids align", meta.get("digest"), digest)
                return store
            pos = {pid: j for j, pid in enumerate(a_ids.tolist())}
            src = np.array([pos.get(pid, -1) for pid in ids], dtype=np.int64)
            have = src >= 0
            aligned = np.zeros((n, DIM), dtype=np.int8)
            aligned[have] = q[src[have]]
            sc = np.zeros(n, dtype=np.float32)
            sc[have] = scale[src[have]].astype(np.float32)
            missing = int((~have).sum())
            log.warning("dense: corpus digest %s != vectors %s; reused %d vectors, %d passages have no vector",
                        digest, meta.get("digest"), int(have.sum()), missing)
            return cls(aligned, sc, have, {**meta, "missing": missing, "exact": False})
        except Exception as e:  # noqa: BLE001 - a broken artifact must never take search down
            log.warning("dense: could not load vectors (%s) - BM25 only", e)
            return None

    def scores(self, qvecs: np.ndarray, chunk: int = 4096) -> np.ndarray:
        """(n_passages, n_queries) cosine similarities; -1 where a passage has no vector."""
        n = self.q.shape[0]
        qt = np.ascontiguousarray(qvecs.T.astype(np.float32))
        out = np.empty((n, qt.shape[1]), dtype=np.float32)
        for a in range(0, n, chunk):
            b = min(a + chunk, n)
            out[a:b] = (self.q[a:b].astype(np.float32) @ qt) * self.scale[a:b, None]
        out[~self.have] = -1.0
        return out


# ---------------------------------------------------------------------------
# query side
# ---------------------------------------------------------------------------
class Dense:
    """Query encoder + vector store for one Index."""

    def __init__(self, encoder: Encoder, store: VectorStore):
        self.encoder, self.store = encoder, store
        self.ready = True
        self._cache: dict[str, np.ndarray] = {}
        self._lock = threading.Lock()

    def encode_queries(self, texts: list[str]) -> np.ndarray:
        got = {t: self._cache[t] for t in texts if t in self._cache}
        todo = [t for t in dict.fromkeys(texts) if t not in got]
        if todo:
            with self._lock:
                vecs = self.encoder.encode(todo, QUERY_PREFIX, max_tokens=QUERY_MAX_TOKENS)
            got.update(zip(todo, vecs))
            if len(self._cache) > 512:
                self._cache.clear()
            self._cache.update(zip(todo, vecs))
        return np.stack([got[t] for t in texts])

    def scores(self, texts: list[str]) -> np.ndarray:
        return self.store.scores(self.encode_queries(texts))

    def clear_cache(self):
        self._cache.clear()


def load_dense(ids: list[str], digest: str) -> Dense | None:
    """Best-effort: a Dense for this corpus, or None (BM25-only). Never raises."""
    if not enabled():
        return None
    try:
        if not model_ready():
            log.warning("dense: model files missing in %s (run scripts/prebuild_index.py) - BM25 only", MODEL_DIR)
            return None
        store = VectorStore.load(VECTORS_PATH, ids, digest)
        if store is None:
            return None
        d = Dense(Encoder(), store)
        _release_heap()
        return d
    except Exception as e:  # noqa: BLE001
        log.warning("dense: disabled (%s)", e)
        return None


def _release_heap():
    """Hand freed load-time buffers (npz decompression, model bytes) back to the OS."""
    try:
        import ctypes
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:  # noqa: BLE001 - non-glibc platform
        pass


def warm_up(idx=None):
    """Load everything and run one query through it (used by scripts/prebuild_index.py)."""
    from .retrieval import get_index
    idx = idx or get_index()
    d = idx.dense
    if d is not None:
        d.encode_queries(["warm-up"])
    return d


def clear_query_cache():
    from . import retrieval
    idx = retrieval._index
    if idx is not None and idx.dense is not None:
        idx.dense.clear_cache()
