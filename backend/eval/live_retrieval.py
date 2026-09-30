"""Retrieval metrics through the DEPLOYED pipeline (LLM query rewrite included).

run_eval.py's retrieval mode can only exercise the LLM-free path in a sandbox
without provider keys. This posts each question to the live /api/chat and
scores the statute sources it returns with the same hit rule (expected law
title substring, rank among statute sources). Prints aggregates only - the
held-out set must not be inspected per question.

    python eval/live_retrieval.py --set heldout [--api URL] [--k 8] [--sleep 4]
"""
import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_eval import load, set_path  # noqa: E402


def ask(api: str, q: str) -> dict:
    req = urllib.request.Request(f"{api}/api/chat", data=json.dumps({"message": q}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--set", default="heldout")
    p.add_argument("--api", default="https://kanooni-sathi-api.onrender.com")
    p.add_argument("--k", type=int, default=8)
    p.add_argument("--sleep", type=float, default=4.0)
    args = p.parse_args()

    # English answers carry English citations; map each law's slug back to
    # its Nepali title from the local index (same corpus digest as prod)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app.retrieval import get_index
    idx = get_index()
    title_of = dict(zip(idx.slug, idx.doc_title))

    rows = []
    for q in load(set_path(args.set)):
        for attempt in range(3):
            try:
                d = ask(args.api, q["q"])
                break
            except Exception as e:  # noqa: BLE001 - cold start / rate limit: retry
                if attempt == 2:
                    print("failed:", str(e)[:80], file=sys.stderr)
                    d = {"sources": [], "analysis": {}}
                time.sleep(20)
        laws = [s for s in d.get("sources", []) if s.get("category", "law") == "law"][:args.k]
        titles = [title_of.get(s.get("slug") or "", "") or s.get("citation") or "" for s in laws]
        rank = next((i for i, t in enumerate(titles, 1) if any(x in t for x in q["expect"])), None)
        rows.append({"lang": q.get("lang"), "rank": rank, "llm": bool((d.get("analysis") or {}).get("queries_ne"))})
        time.sleep(args.sleep)

    n = len(rows)
    hit = lambda k: sum(1 for r in rows if r["rank"] and r["rank"] <= k) / n  # noqa: E731
    mrr = sum(1 / r["rank"] for r in rows if r["rank"]) / n
    print(json.dumps({"set": args.set, "n": n, f"hit@{args.k}": round(hit(args.k), 3), "hit@3": round(hit(3), 3),
                      "MRR": round(mrr, 3), "llm_rewrite_used": sum(r["llm"] for r in rows),
                      "by_lang": {lang: round(sum(1 for r in rows if r["lang"] == lang and r["rank"] and r["rank"] <= args.k)
                                               / max(1, sum(1 for r in rows if r["lang"] == lang)), 3)
                                  for lang in sorted({r["lang"] for r in rows})}}, indent=1))


if __name__ == "__main__":
    main()
