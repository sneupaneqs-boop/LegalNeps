"""Collect answers from a running API for human / LLM review of the V3 generate-then-verify pipeline.

For each question of a set it calls POST {api}/api/chat and writes, per answer, the rendered answer, every
rendered cited sentence with the verbatim quote(s) it rests on, and the FULL text of each cited passage
(from the local corpus by source id; falls back to /api/law/{slug}/{section}, then to the snippet), plus
the verifier's own counts. The aggregate block is deterministic bookkeeping only (sentences kept/removed,
removal reasons, fallback and truncation rates) - it is NOT the unsupported-claim rate. That rate needs a
reviewer to read the sentences against the passages (see docs/PROGRESS.md, V3).

    python eval/answer_review.py --set realworld --limit 30 [--api URL] [--out FILE] [--sleep 4]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from run_eval import load, set_path  # noqa: E402

LIVE = "https://kanooni-sathi-api.onrender.com"
REPORTS = HERE / "reports"


def post(api: str, q: str, timeout: int = 180) -> dict:
    req = urllib.request.Request(f"{api}/api/chat", data=json.dumps({"message": q}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def get(api: str, path: str, timeout: int = 60) -> dict:
    with urllib.request.urlopen(f"{api}{path}", timeout=timeout) as r:
        return json.load(r)


class Passages:
    """Full text of cited sources: local corpus by id, else the API's section endpoint, else the snippet."""

    def __init__(self, api: str):
        self.api, self.local = api, {}
        try:
            from app.retrieval import corpus_source
            self._entries, _ = corpus_source()
        except Exception:  # noqa: BLE001 - no local corpus: use the API
            self._entries = []

    def preload(self, ids: set[str]) -> None:
        if not ids or not self._entries:
            return
        for e in self._entries:
            if e.get("id") in ids:
                self.local[e["id"]] = e
                if len(self.local) >= len(ids):
                    break

    def text(self, src: dict) -> dict:
        e = self.local.get(src.get("id"))
        if e:
            return {"where": "corpus", "text_ne": e.get("text_ne"), "text_en": e.get("text_en")}
        if src.get("slug") and src.get("section"):
            try:
                d = get(self.api, f"/api/law/{src['slug']}/{urllib.request.quote(str(src['section']))}")
                return {"where": "api", "text_ne": d.get("text_ne"), "text_en": d.get("text_en")}
            except Exception:  # noqa: BLE001
                pass
        return {"where": "snippet", "text_ne": src.get("snippet"), "text_en": None}


def review_row(q: dict, d: dict, passages: Passages) -> dict:
    v = d.get("verification") or {}
    sources = {s["n"]: s for s in d.get("sources", [])}
    sentences = []
    for ev in v.get("evidence") or []:
        cites = []
        for c in ev.get("cites", []):
            s = sources.get(c["n"], {})
            cites.append({"n": c["n"], "quote": c["quote"], "citation": s.get("citation"), "status": s.get("status"),
                          "category": s.get("category"), "passage": passages.text(s) if s else None})
        sentences.append({"text": ev["text"], "kind": ev.get("kind"), "cites": cites})
    return {"id": q.get("id"), "question": q["q"], "language": d.get("language"), "llm_used": d.get("llm_used"),
            "cached": d.get("cached"), "mode": v.get("mode") or ("legacy" if v else "none"),
            "truncated": v.get("truncated"), "answer": d.get("answer"), "sentences": sentences,
            "removed": v.get("removed"), "claims": v.get("claims"), "gaps_rendered": "**What the sources don't cover**" in (d.get("answer") or "")
            or "**स्रोतहरूले नसमेटेको कुरा**" in (d.get("answer") or ""),
            "review": {"sentences": [{"i": i, "label": None, "note": ""} for i in range(len(sentences))],
                       "labels": "supported | unsupported | wrong-law | hallucinated-number-or-section"}}


def aggregate(rows: list[dict]) -> dict:
    n = len(rows)
    reasons: dict[str, int] = {}
    for r in rows:
        for k, c in ((r.get("removed") or {}).get("by_reason") or {}).items():
            reasons[k] = reasons.get(k, 0) + c
    kept = sum(len(r["sentences"]) for r in rows)
    removed = sum((r.get("removed") or {}).get("count", 0) for r in rows)
    structured = [r for r in rows if r["mode"] == "structured"]
    return {
        "answers": n, "structured": len(structured),
        "fallback_rate": round(sum(r["mode"] == "extractive_fallback" for r in rows) / n, 3) if n else None,
        "no_llm_or_error": sum(r["mode"] in ("none",) for r in rows),
        "legacy_prose_answers": sum(r["mode"] == "legacy" for r in rows),
        "truncation_rate": round(sum(bool(r.get("truncated")) for r in rows) / n, 3) if n else None,
        "cited_sentences_kept": kept, "sentences_removed": removed,
        "removal_share": round(removed / (kept + removed), 3) if kept + removed else None,
        "removal_reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
        "avg_cited_sentences_per_structured_answer": round(kept / len(structured), 2) if structured else None,
        "answers_with_gaps_section": sum(r["gaps_rendered"] for r in rows),
        "uncited_numbers_in_rendered_sentences": sum(uncited_numbers(r) for r in rows),
    }


def uncited_numbers(r: dict) -> int:
    """Numbers in a rendered cited sentence that appear in none of its quotes (the '0 uncited numbers' target)."""
    from app import verifier
    bad = 0
    for s in r["sentences"]:
        pool = set()
        for c in s["cites"]:
            pool |= verifier._numbers_in(c["quote"])
            pool |= {n for n in verifier._numbers_in(c.get("citation") or "") if len(n) == 4}
        bad += len(verifier._sentence_numbers(s["text"]) - pool)
    return bad


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--set", default="realworld", choices=["realworld", "heldout", "default", "answers30", "answers30b", "answers30c"])
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--api", default=LIVE)
    p.add_argument("--out", help="output JSON (default eval/reports/answer-review-<set>-<time>.json)")
    p.add_argument("--sleep", type=float, default=4.0, help="seconds between calls (free-tier quotas)")
    args = p.parse_args()

    questions = load(set_path(args.set))[:args.limit]
    answers = []
    for q in questions:
        d = None
        for attempt in range(3):
            try:
                d = post(args.api, q["q"])
                break
            except Exception as e:  # noqa: BLE001 - cold start / rate limit: retry
                print(f"{q.get('id')}: attempt {attempt + 1} failed: {str(e)[:80]}", file=sys.stderr)
                time.sleep(20)
        answers.append((q, d))
        time.sleep(args.sleep)

    passages = Passages(args.api)
    passages.preload({s["id"] for _, d in answers if d for s in d.get("sources", []) if s.get("id")})
    rows = [review_row(q, d or {"sources": []}, passages) | ({"error": "no response"} if d is None else {})
            for q, d in answers]
    out = {"meta": {"date": time.strftime("%Y-%m-%d %H:%M:%S"), "api": args.api, "set": args.set, "n": len(rows),
                    "note": "aggregate is deterministic bookkeeping, not the unsupported-claim rate; label each "
                            "sentence against its full passage in review.sentences"},
           "aggregate": aggregate(rows), "answers": rows}
    path = Path(args.out) if args.out else REPORTS / f"answer-review-{args.set}-{time.strftime('%Y%m%d-%H%M%S')}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out["aggregate"], ensure_ascii=False, indent=1))
    print("wrote", path)


if __name__ == "__main__":
    main()
