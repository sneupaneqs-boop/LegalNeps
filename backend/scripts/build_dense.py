"""Regenerate the corpus vectors (app/data/dense/vectors.npz) after a corpus change.

    cd backend && python scripts/build_dense.py [--workers 4]

Embeds every passage (doc title + section heading + body, see app.dense.passage_text) with the
int8 multilingual-e5-small encoder and stores int8 vectors + float16 scales keyed by passage id
and the corpus digest. ~73k passages take ~25-50 minutes on 4 CPU cores; a checkpoint is kept
next to the output so an interrupted run resumes. Needs `pip install -r requirements-scripts.txt`
(onnx, sentencepiece, onnxruntime). Commit the resulting file (~30MB).

The vectors are only useful for the exact model in app.dense (MODEL_NAME); changing the model,
MAX_TOKENS or passage_text requires a rebuild AND bumping dense.ARTIFACT_VERSION.
"""
import argparse
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402

from app import dense  # noqa: E402
from app.retrieval import corpus_source  # noqa: E402

_enc = None


def _init():
    global _enc
    _enc = dense.Encoder(threads=1)


def _work(job):
    lo, texts = job
    return lo, _enc.encode(texts, dense.PASSAGE_PREFIX, batch=16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--limit", type=int, default=0, help="only the first N passages (smoke test; do not commit)")
    ap.add_argument("--out", type=Path, default=dense.VECTORS_PATH)
    ap.add_argument("--chunk", type=int, default=128)
    a = ap.parse_args()

    dense.prepare_model()
    entries, digest = corpus_source()
    ids, texts = [], []
    for e in entries:
        ids.append(e["id"])
        texts.append(dense.passage_text(e))
        if a.limit and len(ids) >= a.limit:
            break
    n = len(ids)
    dup = n - len(set(ids))
    print(f"{n} passages, digest {digest}" + (f", WARNING {dup} duplicate ids" if dup else ""), flush=True)

    a.out.parent.mkdir(parents=True, exist_ok=True)
    ckpt = a.out.with_name(a.out.name + ".partial.npz")
    vecs = np.zeros((n, dense.DIM), dtype=np.float32)
    done = np.zeros(n, dtype=bool)
    if ckpt.exists():
        z = np.load(ckpt)
        if z["done"].shape[0] == n and str(z["digest"]) == digest:
            vecs, done = z["vecs"].astype(np.float32), z["done"]
            print(f"resuming: {int(done.sum())} already embedded", flush=True)
    order = np.argsort([len(t) for t in texts], kind="stable")
    order = order[~done[order]]
    jobs = [(order[i:i + a.chunk], [texts[j] for j in order[i:i + a.chunk]]) for i in range(0, len(order), a.chunk)]

    t0, last = time.time(), time.time()
    with mp.get_context("spawn").Pool(a.workers, initializer=_init) as pool:
        for k, (idx, v) in enumerate(pool.imap_unordered(_work, jobs), 1):
            vecs[idx] = v
            done[idx] = True
            if time.time() - last > 240:
                np.savez(ckpt, vecs=vecs.astype(np.float16), done=done, digest=np.array(digest))
                last = time.time()
                rate = (int(done.sum()) - (n - len(order))) / (time.time() - t0)
                print(f"  {int(done.sum())}/{n}  {rate:.1f}/s", flush=True)
    assert done.all()
    q, scale = dense.quantize(vecs)
    dense.save_vectors(a.out, ids, q, scale, digest)
    ckpt.unlink(missing_ok=True)
    print(f"wrote {a.out} ({a.out.stat().st_size / 2**20:.1f} MB) in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
