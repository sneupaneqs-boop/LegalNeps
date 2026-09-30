"""Warm/cold memory and search latency of the production retrieval path.

    python3 eval/measure_resources.py warm [--queries 60]   # fresh process: load, serve queries, report RSS + p50/p95
    python3 eval/measure_resources.py cold                  # wipe the index cache, rebuild, report peak RSS

Latency is `generation.search()` in raw mode (playbook matching included), i.e. what a chat
request spends in retrieval; the LLM is not involved. RSS is measured with psutil in the
same process after the queries ran (the number Render's 512MB limit sees).
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))


def rss_mb() -> float:
    import psutil
    return psutil.Process().memory_info().rss / 2**20


def warm(n: int) -> dict:
    t0 = time.time()
    from app.generation import _match_playbook, search
    from app.retrieval import get_index
    idx = get_index()
    load_s = time.time() - t0
    qs = []
    for name in ("questions.jsonl", "questions_realworld.jsonl", "questions_heldout.jsonl"):
        qs += [json.loads(l)["q"] for l in open(os.path.join(HERE, name), encoding="utf-8")
               if l.strip() and not l.lstrip().startswith("#")]
    qs = qs[:n]
    rss_loaded = rss_mb()
    an = {"queries_ne": [], "queries_en": [], "laws": [], "wants_precedent": True}
    for q in qs:  # first pass: brings caches/allocations to steady state
        search(q, an, top_k=8, precedent_k=3, playbook=_match_playbook(q, an))
    lat = []
    for q in qs:  # second pass = the warm figure (dense query-embedding cache is disabled for it below)
        try:
            from app import dense
            dense.clear_query_cache()
        except ImportError:
            pass
        t = time.perf_counter()
        search(q, an, top_k=8, precedent_k=3, playbook=_match_playbook(q, an))
        lat.append((time.perf_counter() - t) * 1000)
    lat.sort()
    d = getattr(idx, "dense", None)
    return {"passages": len(idx), "load_s": round(load_s, 1), "rss_after_load_mb": round(rss_loaded),
            "rss_warm_mb": round(rss_mb()), "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024),
            "n": len(lat), "p50_ms": round(statistics.median(lat)), "p95_ms": round(lat[int(len(lat) * 0.95) - 1]),
            "dense": bool(d is not None and getattr(d, "ready", False))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["warm", "cold", "_cold_child"])
    ap.add_argument("--queries", type=int, default=60)
    a = ap.parse_args()
    if a.mode == "warm":
        print(json.dumps(warm(a.queries)))
    elif a.mode == "cold":
        from app.retrieval import CACHE_DIR
        shutil.rmtree(CACHE_DIR, ignore_errors=True)
        out = subprocess.run([sys.executable, __file__, "_cold_child"], capture_output=True, text=True)
        print(out.stdout.strip() or out.stderr[-500:])
    else:
        t = time.time()
        from app.retrieval import get_index
        idx = get_index()
        try:
            from app.dense import warm_up
            warm_up(idx)
        except ImportError:
            pass
        print(json.dumps({"cold_build_s": round(time.time() - t, 1),
                          "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)}))


if __name__ == "__main__":
    main()
