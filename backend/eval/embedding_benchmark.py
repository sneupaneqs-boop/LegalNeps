"""S4: does adding embeddings to the BM25 ranking actually help? Per
STRATEGY.md, ship the hybrid only if it wins on this eval - so this script
measures it rather than assuming it.

Scope: this environment has no hosted-embedding API key, so only the local
arm (multilingual-e5-small, ONNX int8, ~118MB) is benchmarked; the "hosted
API for queries" arm from STRATEGY is untested here (see docs/PROGRESS.md).

Method: for each of the 150 eval questions, take BM25's own top-50 law
candidates (raw query, no LLM) - the same pool build_queries()/search()
already produce - and re-rank that pool three ways: BM25 alone (the
existing raw-mode ranking, recomputed here for a like-for-like top-8/MRR
number), e5 cosine similarity alone, and a weighted fusion of both. Testing
within BM25's own candidate pool (rather than a full second full-corpus ANN
search) keeps the compute bounded while still answering the real question:
does semantic similarity reorder these candidates toward the right one more
often than lexical BM25 does alone?

    python3 eval/embedding_benchmark.py --model-dir /tmp/e5small
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from app.generation import search as bm25_search  # noqa: E402
from app.retrieval import get_index  # noqa: E402

_RAW_ANALYSIS = {"queries_ne": [], "queries_en": [], "laws": [], "wants_precedent": False}


def load_questions():
    return [json.loads(l) for l in open(os.path.join(HERE, "questions.jsonl"), encoding="utf-8") if l.strip()]


class E5Small:
    def __init__(self, model_dir: str):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        self.tok = Tokenizer.from_file(os.path.join(model_dir, "tokenizer.json"))
        self.tok.enable_truncation(max_length=256)
        self.sess = ort.InferenceSession(os.path.join(model_dir, "model.onnx"),
                                          providers=["CPUExecutionProvider"])

    def embed(self, texts: list[str], prefix: str, batch_size: int = 16) -> np.ndarray:
        out = []
        for i in range(0, len(texts), batch_size):
            batch = [prefix + t for t in texts[i:i + batch_size]]
            encs = self.tok.encode_batch(batch)
            maxlen = max(len(e.ids) for e in encs)
            ids = np.zeros((len(encs), maxlen), dtype=np.int64)
            mask = np.zeros((len(encs), maxlen), dtype=np.int64)
            for j, e in enumerate(encs):
                ids[j, :len(e.ids)] = e.ids
                mask[j, :len(e.ids)] = e.attention_mask
            tt = np.zeros_like(ids)
            hidden = self.sess.run(None, {"input_ids": ids, "attention_mask": mask, "token_type_ids": tt})[0]
            m = mask[:, :, None].astype(np.float32)
            pooled = (hidden * m).sum(1) / np.clip(m.sum(1), 1e-9, None)
            norm = pooled / np.clip(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9, None)
            out.append(norm)
        return np.concatenate(out, axis=0)


def _first_hit(ranked_ids, id_to_entry, expect):
    for rank, doc_id in enumerate(ranked_ids, 1):
        title = id_to_entry[doc_id].get("doc_title_ne") or ""
        if any(x in title for x in expect):
            return rank
    return None


def summarize(name, per_question_ranks, k=8):
    ranks = [r for r in per_question_ranks if r is not None]
    n = len(per_question_ranks)
    return {
        "mode": name,
        "hit@k": round(sum(1 for r in ranks if r) / n, 3) if n else 0,
        "hit@3": round(sum(1 for r in ranks if r and r <= 3) / n, 3) if n else 0,
        "MRR": round(sum(1 / r for r in ranks if r) / n, 3) if n else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", required=True, help="dir with model.onnx + tokenizer.json")
    ap.add_argument("--pool-k", type=int, default=50)
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--alpha", type=float, default=0.5, help="fusion weight on cosine (0-1)")
    args = ap.parse_args()

    idx = get_index()
    qs = load_questions()
    titles = {e.get("doc_title_ne") or "" for e in idx.entries
              if e.get("doc_type") in ("act", "rule", "constitution", "order", "directive")}
    covered = [q for q in qs if any(any(x in t for x in q["expect"]) for t in titles)]
    print(f"{len(covered)}/{len(qs)} questions have their expected law in the corpus")

    print("running BM25 to build per-question candidate pools...")
    pools = []  # list of (question, [(id, bm25_rrf_score, entry), ...])
    all_entries: dict[str, dict] = {}
    for q in covered:
        hits = bm25_search(q["q"], _RAW_ANALYSIS, top_k=args.pool_k, precedent_k=0)
        pool = [(h["id"], h.get("rrf", 0.0), h) for h in hits]
        for doc_id, _, e in pool:
            all_entries[doc_id] = e
        pools.append((q, pool))
    print(f"candidate pool: {len(all_entries)} unique passages across {len(pools)} questions")

    print(f"loading e5-small from {args.model_dir} ...")
    model = E5Small(args.model_dir)

    print("embedding candidate passages...")
    pool_ids = list(all_entries)
    pool_texts = [(all_entries[i].get("title_ne") or "") + " " + (all_entries[i].get("text_ne") or "")[:500]
                  for i in pool_ids]
    pool_vecs = model.embed(pool_texts, prefix="passage: ")
    id_to_vec = dict(zip(pool_ids, pool_vecs))

    print("embedding queries...")
    query_vecs = model.embed([q["q"] for q, _ in pools], prefix="query: ")

    alphas = sorted({0.0, 0.3, args.alpha, 0.7, 1.0})
    ranks_by_alpha = {a: [] for a in alphas}
    bm25_ranks = []
    for (q, pool), qvec in zip(pools, query_vecs):
        pool_ids_q = [pid for pid, _, _ in pool]
        bm25_scores = {pid: s for pid, s, _ in pool}
        cos = {pid: float(np.dot(qvec, id_to_vec[pid])) for pid in pool_ids_q}
        # normalize each score list to [0,1] within this question's pool so
        # the two very different-scaled scores (BM25 rrf vs cosine) fuse fairly
        def norm(d):
            vals = list(d.values())
            lo, hi = min(vals), max(vals)
            return {k: (v - lo) / (hi - lo) if hi > lo else 0.0 for k, v in d.items()}
        bm25_n, cos_n = norm(bm25_scores), norm(cos)

        bm25_order = sorted(pool_ids_q, key=lambda i: -bm25_scores[i])[:args.top_k]
        bm25_ranks.append(_first_hit(bm25_order, all_entries, q["expect"]))
        for a in alphas:
            fused = {pid: (1 - a) * bm25_n[pid] + a * cos_n[pid] for pid in pool_ids_q}
            order = sorted(pool_ids_q, key=lambda i: -fused[i])[:args.top_k]
            ranks_by_alpha[a].append(_first_hit(order, all_entries, q["expect"]))

    results = [summarize("bm25 only (alpha=0)", bm25_ranks, args.top_k)]
    for a in alphas:
        if a == 0.0:
            continue
        label = "e5-small only (alpha=1)" if a == 1.0 else f"hybrid alpha={a}"
        results.append(summarize(label, ranks_by_alpha[a], args.top_k))
    print(json.dumps(results, indent=1))
    return results


if __name__ == "__main__":
    main()
