"""
Evaluation harness for Kanooni Sathi.

    python3 eval/run_eval.py retrieval            # hand-written questions, raw + LLM-rewritten queries
    python3 eval/run_eval.py synth-gen --n 200    # generate questions from random real provisions
    python3 eval/run_eval.py synth                # retrieval on the synthetic set (known gold chunk)
    python3 eval/run_eval.py e2e --n 20           # full answers, auto-checks + LLM judge

Retrieval "hit" = one of the top-k statute passages comes from an expected
law (title substring). A question whose expected law isn't in the corpus at
all is reported separately as a coverage gap, not a ranking failure.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from app import llm  # noqa: E402
from app.generation import analyze_query, answer_question, search  # noqa: E402
from app.retrieval import get_index  # noqa: E402
from app.text_norm import detect_language  # noqa: E402

REPORTS = os.path.join(HERE, "reports")
SYNTH = os.path.join(HERE, "synth.jsonl")


def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def _save(name, data):
    os.makedirs(REPORTS, exist_ok=True)
    path = os.path.join(REPORTS, f"{name}-{time.strftime('%Y%m%d-%H%M%S')}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return path


def _first_hit(results, expect):
    for rank, r in enumerate(results, 1):
        title = r.get("doc_title_ne") or r.get("title_ne") or ""
        if any(x in title for x in expect):
            return rank
    return None


def cmd_retrieval(args):
    idx = get_index()
    titles = {e.get("doc_title_ne") or "" for e in idx.entries
              if e.get("doc_type") in ("act", "rule", "constitution", "order", "directive")}
    qs = load(os.path.join(HERE, "questions.jsonl"))
    modes = ["raw"] + (["llm"] if llm.available() and not args.raw_only else [])
    rows = []

    def run(q):
        out = {"q": q["q"], "area": q["area"], "expect": q["expect"]}
        out["in_corpus"] = any(any(x in t for x in q["expect"]) for t in titles)
        for mode in modes:
            t = time.time()
            if mode == "raw":
                analysis = {"queries_ne": [], "queries_en": [], "laws": [], "wants_precedent": True}
            else:
                analysis = analyze_query(q["q"], detect_language(q["q"]))
            res = search(q["q"], analysis, top_k=args.k, precedent_k=3)
            laws = [r for r in res if r.get("category") == "law"]
            out[mode] = {
                "rank": _first_hit(laws, q["expect"]),
                "precedents": sum(1 for r in res if r.get("category") == "precedent"),
                "top": [r.get("source_ne") for r in laws[:3]],
                "ms": int((time.time() - t) * 1000),
                "queries": analysis.get("queries_ne", [])[:4],
            }
        return out

    with ThreadPoolExecutor(args.workers) as ex:
        rows = list(ex.map(run, qs))

    summary = {}
    covered = [r for r in rows if r["in_corpus"]]
    for mode in modes:
        ranks = [r[mode]["rank"] for r in covered]
        summary[mode] = {
            "hit@k (covered)": round(sum(1 for x in ranks if x) / max(1, len(covered)), 3),
            "hit@3 (covered)": round(sum(1 for x in ranks if x and x <= 3) / max(1, len(covered)), 3),
            "MRR": round(sum(1 / x for x in ranks if x) / max(1, len(covered)), 3),
            "median_ms": statistics.median(r[mode]["ms"] for r in rows),
            "with_precedent": round(sum(1 for r in rows if r[mode]["precedents"]) / len(rows), 3),
        }
    summary["questions"] = len(rows)
    summary["coverage_gaps"] = sorted({"/".join(r["expect"]) for r in rows if not r["in_corpus"]})
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    worst_mode = modes[-1]
    misses = [r for r in covered if not r[worst_mode]["rank"]]
    print(f"\nMisses in '{worst_mode}' mode ({len(misses)}):")
    for r in misses:
        print(" -", r["q"][:70], "| expect", r["expect"], "| got", [t[:40] for t in r[worst_mode]["top"] if t])
    print("report:", _save("retrieval", {"summary": summary, "rows": rows}))


GEN_SYSTEM = """You write realistic evaluation questions for a Nepali legal Q&A assistant. \
For each numbered official legal passage, write TWO questions that a real person with this \
problem would ask WITHOUT quoting the law or naming section numbers: one in plain English, one \
in everyday Nepali (Devanagari). The passage must contain the answer. Return JSON: \
{"items": [{"n": <passage number>, "en": "...", "ne": "..."}]}. Skip passages that are purely \
procedural boilerplate (titles, commencement, definitions lists, schedules) by omitting them."""


def cmd_synth_gen(args):
    idx = get_index()
    rng = random.Random(args.seed)
    pool = [e for e in idx.entries
            if len(e.get("text_ne") or "") > 250
            and (e.get("category") == "precedent" or (e.get("section") and e.get("doc_type") in
                 ("act", "constitution", "rule")))]
    sample = rng.sample(pool, min(args.n, len(pool)))
    out = []
    for i in range(0, len(sample), 8):
        batch = sample[i:i + 8]
        passages = "\n\n".join(f"[{j}] {e.get('source_ne')}\n{e['text_ne'][:1500]}" for j, e in enumerate(batch, 1))
        try:
            data = llm.parse_json(llm.complete(GEN_SYSTEM, passages, json_mode=True, max_tokens=3000, temperature=0.6))
        except Exception as ex:  # noqa: BLE001
            print("gen failed:", str(ex)[:120])
            continue
        for it in data.get("items", []):
            try:
                e = batch[int(it["n"]) - 1]
            except (KeyError, ValueError, IndexError):
                continue
            for lang in ("en", "ne"):
                if it.get(lang):
                    out.append({"q": it[lang], "lang": lang, "gold_id": e["id"],
                                "gold_doc": e.get("doc_title_ne"), "category": e.get("category")})
        print(f"generated {len(out)} questions from {i + len(batch)} passages")
    with open(SYNTH, "w", encoding="utf-8") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")


def cmd_synth(args):
    get_index()
    qs = load(SYNTH)
    if args.limit:
        qs = qs[: args.limit]
    use_llm = llm.available() and not args.raw_only

    def run(q):
        analysis = analyze_query(q["q"], q["lang"]) if use_llm else {"queries_ne": [], "queries_en": [], "laws": []}
        res = search(q["q"], analysis, top_k=args.k, precedent_k=5)
        ids = [r["id"] for r in res]
        docs = [r.get("doc_title_ne") for r in res]
        return {**q, "chunk_hit": q["gold_id"] in ids, "doc_hit": q["gold_doc"] in docs,
                "rank": ids.index(q["gold_id"]) + 1 if q["gold_id"] in ids else None}

    with ThreadPoolExecutor(args.workers) as ex:
        rows = list(ex.map(run, qs))
    summary = {}
    for key, sel in {"all": rows,
                     "en": [r for r in rows if r["lang"] == "en"],
                     "ne": [r for r in rows if r["lang"] == "ne"],
                     "law": [r for r in rows if r["category"] == "law"],
                     "precedent": [r for r in rows if r["category"] == "precedent"]}.items():
        if sel:
            summary[key] = {"n": len(sel),
                            "exact_passage@k": round(sum(r["chunk_hit"] for r in sel) / len(sel), 3),
                            "right_document@k": round(sum(r["doc_hit"] for r in sel) / len(sel), 3),
                            "MRR": round(sum(1 / r["rank"] for r in sel if r["rank"]) / len(sel), 3)}
    summary["mode"] = "llm" if use_llm else "raw"
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("report:", _save("synth", {"summary": summary, "rows": rows}))


JUDGE_SYSTEM = """You grade answers from a Nepali legal-information assistant. You get the \
question, the numbered official passages the assistant was given, and its answer. Return JSON: \
{"grounded": 1-5 (every legal claim supported by a cited passage; 5 = fully), \
"relevant": 1-5 (addresses the person's actual problem), \
"helpful": 1-5 (clear, actionable, plain language), \
"hallucination": true/false (states a law, section, number, deadline or penalty NOT in the passages), \
"notes": "one sentence"}"""


def cmd_e2e(args):
    get_index()
    qs = load(os.path.join(HERE, "questions.jsonl"))
    rng = random.Random(args.seed)
    qs = rng.sample(qs, min(args.n, len(qs)))
    rows = []
    for q in qs:
        t = time.time()
        r = answer_question(q["q"])
        ms = int((time.time() - t) * 1000)
        ans = r["answer"]
        n_src = len(r["sources"])
        cited = {int(x) for x in re.findall(r"\[(\d{1,2})\]", ans.translate(str.maketrans("०१२३४५६७८९", "0123456789")))}
        want_lang = detect_language(q["q"]) if not re.search(r"\b(mero|garne|chha|ke|ko)\b", q["q"]) else "ne"
        checks = {
            "llm_used": r["llm_used"],
            "has_citation": bool(cited),
            "citations_valid": all(1 <= c <= n_src for c in cited),
            "language_ok": r["language"] == want_lang,
            "disclaimer": bool(re.search(r"advocate|lawyer|वकिल|अधिवक्ता|कानून व्यवसायी", ans)),
        }
        judge = {}
        if llm.available():
            ctx = "\n\n".join(f"[{i}] {s.get('source_ne')}\n{(s.get('text_ne') or '')[:1200]}"
                              for i, s in enumerate(r["sources"], 1))
            try:
                judge = llm.parse_json(llm.complete(
                    JUDGE_SYSTEM, f"Question: {q['q']}\n\nPassages:\n{ctx}\n\nAnswer:\n{ans}",
                    fast=True, json_mode=True, max_tokens=400, temperature=0))
            except Exception as ex:  # noqa: BLE001
                judge = {"error": str(ex)[:120]}
        rows.append({"q": q["q"], "ms": ms, "checks": checks, "judge": judge, "answer": ans[:1500],
                     "sources": [s.get("source_ne") for s in r["sources"]]})
        print(f"{ms:6d}ms {json.dumps(checks)} {json.dumps({k: judge.get(k) for k in ('grounded', 'relevant', 'helpful', 'hallucination')})} | {q['q'][:60]}")

    def avg(key):
        vals = [r["judge"].get(key) for r in rows if isinstance(r["judge"].get(key), (int, float))]
        return round(sum(vals) / len(vals), 2) if vals else None

    summary = {
        "n": len(rows),
        "median_ms": statistics.median(r["ms"] for r in rows),
        **{k: round(sum(1 for r in rows if r["checks"][k]) / len(rows), 3) for k in rows[0]["checks"]},
        "grounded": avg("grounded"), "relevant": avg("relevant"), "helpful": avg("helpful"),
        "hallucination_rate": round(sum(1 for r in rows if r["judge"].get("hallucination") is True) / len(rows), 3),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("report:", _save("e2e", {"summary": summary, "rows": rows}))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("retrieval"); p.add_argument("--k", type=int, default=8); p.add_argument("--workers", type=int, default=4); p.add_argument("--raw-only", action="store_true")
    p = sub.add_parser("synth-gen"); p.add_argument("--n", type=int, default=120); p.add_argument("--seed", type=int, default=7)
    p = sub.add_parser("synth"); p.add_argument("--k", type=int, default=8); p.add_argument("--workers", type=int, default=4); p.add_argument("--limit", type=int, default=0); p.add_argument("--raw-only", action="store_true")
    p = sub.add_parser("e2e"); p.add_argument("--n", type=int, default=15); p.add_argument("--seed", type=int, default=3)
    args = ap.parse_args()
    {"retrieval": cmd_retrieval, "synth-gen": cmd_synth_gen, "synth": cmd_synth, "e2e": cmd_e2e}[args.cmd](args)


if __name__ == "__main__":
    main()
