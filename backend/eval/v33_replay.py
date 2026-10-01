"""Replay the 30 FRESH review-2 questions through the V3.3 gate OFFLINE and count how many answers would now
abstain, fall back to the (topical) extractive provisions, or stay structured, and what that does to the
labelled sentences.

Offline means: no LLM query rewrite (the live analysis is not stored), the retrieval of the current worktree
(the concurrent retrieval/playbook fixes are not in it), the candidate sources = offline retrieval + the passages
the live answer actually cited. The labelled sentences are the V3.2 answers' verified sentences; a sentence is
dropped when EVERY passage it cites fails the gate, an answer falls back when fewer than MIN_VERIFIED_RULES (2)
cited rule sentences remain. Polish rules (dedupe, orphan connectives) are not applied here.

    DENSE_MODEL_DIR=... python eval/v33_replay.py [--heldout]     # --heldout: review-1 model + corpus-only markers
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import config, fit_reply, generation as g, structured, topical_fit as tf  # noqa: E402
from app.retrieval import get_index  # noqa: E402

FIXTURE = ROOT / "tests" / "data" / "v33_review_fixture.json"
ANSWERS = ROOT / "eval" / "reports" / "answer-review-v32-answers30-20260930.json"
R1MODEL = ROOT / "eval" / "reports" / "topical-fit-model-r1.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--heldout", action="store_true")
    ap.add_argument("--min-ontopic", type=int, default=config.FIT_MIN_ONTOPIC)
    args = ap.parse_args()
    model = json.loads(R1MODEL.read_text()) if args.heldout else tf.load_model()
    fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
    ans = {a["id"]: a for a in json.loads(ANSWERS.read_text(encoding="utf-8"))["answers"]}
    idx = get_index()
    rows = {pid: i for i, pid in enumerate(idx.ids)}
    by_answer: dict[str, list[dict]] = {}
    for s in fx["sentences"]:
        if s["review"] == 2:
            by_answer.setdefault(s["answer"].split(":")[1], []).append(s)
    out = []
    tally = {"abstain": [], "fallback": [], "structured": []}
    lab_before, lab_after = {}, {}
    for aid, a in sorted(ans.items()):
        q = a["question"]
        an = g.analyze_query(q, "auto")
        pb = g._match_playbook(q, an)
        sources = g.search(an.get("question") or q, an, playbook=pb)
        if pb and not any(s.get("pinned") for s in sources):
            pb = None
        cited = {c["id"]: c for s in by_answer.get(aid, []) for c in s["cites"] if c.get("id")}
        have = {s["id"] for s in sources}
        extra = [idx.get(rows[i]) for i in cited if i not in have and i in rows]
        cands = sources + extra
        fit_reply.relabel_subsections(cands)
        prof = tf.make_profile(q, an, g._guidance_terms_text(pb), g.build_queries(an.get("question") or q, an))
        n_of = {c["id"]: c["n"] for c in cited.values()} if False else {}
        for s_ in by_answer.get(aid, []):
            for c in s_["cites"]:
                n_of[c["id"]] = c["n"]     # the live rank of a passage the answer cited
        ranks = [n_of.get(c["id"], k + 1) for k, c in enumerate(cands)]
        verdicts = tf.judge(cands, tf.Scorer(prof, model=model), model, ranks)
        flag = {}
        for s, v in zip(cands, verdicts):
            s["fit_score"] = round(v.score, 3)
            s.pop("off_topic", None)
            if not v.ok:
                s["off_topic"] = True
                s["off_topic_why"] = v.reasons
            flag[s["id"]] = not v.ok
        shown = g.prompt_source_numbers(sources, pb)
        laws_on = [s for s in cands[:len(sources)] if s.get("category") != "precedent" and not s.get("off_topic")]
        pinned = any(s.get("pinned") for s in sources)
        abstain = len(laws_on) < args.min_ontopic and not pinned
        sents = by_answer.get(aid, [])
        kept = [s for s in sents if not all(flag.get(c["id"], False) for c in s["cites"])]
        rules_left = sum(1 for s in kept if s["kind"] in ("rule", "deadline", "penalty"))
        for s in sents:
            lab_before[s["label"]] = lab_before.get(s["label"], 0) + 1
        for s in kept:
            lab_after[s["label"]] = lab_after.get(s["label"], 0) + 1
        live_mode = a["mode"]
        if abstain:
            mode = "abstain"
        elif live_mode == "structured" and rules_left >= structured.MIN_VERIFIED_RULES:
            mode = "structured"
        elif live_mode == "structured":
            mode = "fallback"       # too few verified rules survive the gate
        else:
            mode = "fallback"       # was already an extractive fallback / no-LLM answer (now topical)
        tally[mode].append(aid)
        out.append({"id": aid, "question": q[:70], "live_mode": live_mode, "v33_mode": mode,
                    "sources": len(sources), "on_topic_laws": len(laws_on), "pinned": pinned,
                    "sentences": len(sents), "kept_after_gate": len(kept), "rules_left": rules_left,
                    "failed": [{"id": s["id"], "why": s.get("off_topic_why")} for s in cands if s.get("off_topic")][:6]})
    for r in out:
        print(f"{r['id']} live={r['live_mode']:<19} v33={r['v33_mode']:<10} laws_on_topic={r['on_topic_laws']}/{r['sources']} "
              f"sentences {r['kept_after_gate']}/{r['sentences']} rules_left={r['rules_left']} | {r['question']}")
    print("\n", {k: (len(v), v) for k, v in tally.items()})
    print("labels before gate:", lab_before)
    print("labels after gate :", lab_after)
    bad = sum(v for k, v in lab_after.items() if k != "supported")
    tot = sum(lab_after.values())
    print(f"kept sentences after gate: {tot}, bad {bad} ({bad / max(tot, 1):.1%}) vs before "
          f"{sum(lab_before.values())}, bad {sum(v for k, v in lab_before.items() if k != 'supported')}")


if __name__ == "__main__":
    main()
