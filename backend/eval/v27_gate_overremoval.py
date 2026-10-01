"""V2.7: how many labelled `supported` sentences does the PASSAGE-level gate (V3.3 topical fit + V2.7 form filter + V2.7 source
guards) remove? A sentence is removed when EVERY passage it cites is ruled off-topic for its question (generation: off_topic_source).
Run with env FIT_FORM_FILTER=0 GUARDS_V27=0 for the V3.3 behaviour.

    DENSE_MODEL_DIR=... python eval/v27_gate_overremoval.py
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

import v27_sentences as vs  # noqa: E402
from app import config, generation as g, situation_guards, topical_fit as tf  # noqa: E402


def main() -> None:
    sents = vs.load_sentences()
    removed, total = Counter(), Counter()
    cache: dict[str, tuple] = {}
    for s in sents:
        q = s["question"]
        if q not in cache:
            an = g.analyze_query(q, "auto")
            cache[q] = (an, tf.Scorer(tf.make_profile(q, an, "", g.build_queries(q, an))))
        an, sc = cache[q]
        cands = []
        for c in s["cites"]:
            src = {k: v for k, v in c.items() if k not in ("n", "quote", "citation")}
            src["category"] = src.get("category") or "law"
            cands.append(src)
        verdicts = tf.judge(cands, sc, ranks=[c["n"] for c in s["cites"]])
        off = []
        for src, v in zip(cands, verdicts):
            bad = not v.ok
            if not bad and not src.get("pinned") and situation_guards.source_violation(q, src, v27=config.GUARDS_V27):
                bad = True
            off.append(bad)
        total[s["label"]] += 1
        if all(off):
            removed[s["label"]] += 1
    sup = total["supported"]
    print({"FIT_FORM_FILTER": config.FIT_FORM_FILTER, "GUARDS_V27": config.GUARDS_V27})
    print("labelled:", dict(total))
    print("removed by the passage gate:", dict(removed), f"-> supported removed {removed['supported']}/{sup} = {100 * removed['supported'] / sup:.1f}%")


if __name__ == "__main__":
    main()
