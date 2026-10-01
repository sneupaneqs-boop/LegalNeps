"""V2.7: what the NEW sentence checks (dropped-condition checks on the full enclosing passage sentence + the V2.7 rows of the
situation-guard table) do to the 196 human-labelled sentences of the three live reviews (review 1 = 77, review 2 = 70, set B
= 49), without any LLM and without the git-ignored reports (everything is in tests/data/*fixture.json).

A sentence is "newly removed" when it passes every V3.3 check (CONDITION_CHECKS=0, GUARDS_V27=0) and fails with the V2.7 checks on.
Over-removal = newly removed sentences labelled `supported` / all supported; catch = newly removed labelled unsupported or
wrong-law. Ablations switch one mechanism off at a time.

    DENSE_MODEL_DIR=... python eval/v27_sentences.py [--list]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import config, verifier  # noqa: E402
from app.claim_checks import CheckContext  # noqa: E402

DATA = ROOT / "tests" / "data"
FILES = (("v33_review_fixture.json", None), ("v27_reviewB_fixture.json", None))


def load_sentences() -> list[dict]:
    out = []
    for fname, _ in FILES:
        fx = json.loads((DATA / fname).read_text(encoding="utf-8"))
        for s in fx["sentences"]:
            s = dict(s)
            s["question"] = fx["answers"][s["answer"]]["question"]
            out.append(s)
    return out


def build(s: dict) -> tuple[dict, list[dict]]:
    n_max = max(c["n"] for c in s["cites"])
    sources = [{"id": f"pad{i}", "category": "law", "text_ne": "", "status": "in_force"} for i in range(n_max)]
    for c in s["cites"]:
        src = {k: v for k, v in c.items() if k not in ("n", "quote", "citation")}
        src["status"] = src.get("status") or "in_force"
        src["category"] = src.get("category") or "law"
        sources[c["n"] - 1] = src
    sent = {"text": s["sentence"], "kind": s.get("kind") or "rule", "cites": [{"n": c["n"], "quote": c["quote"]} for c in s["cites"]]}
    return sent, sources


def reason_for(s: dict) -> str | None:
    sent, sources = build(s)
    ctx = CheckContext(question=s["question"], guidance="")
    reason, _ = verifier.check_structured_sentence(sent, sources, verifier.make_views(sources), set(), ctx)
    return reason


def run(sentences: list[dict], cond: bool, guards: bool) -> dict[str, str | None]:
    config.CONDITION_CHECKS, config.GUARDS_V27 = cond, guards
    return {s["key"]: reason_for(s) for s in sentences}


def summarise(name: str, sentences, base, new) -> dict:
    newly = [s for s in sentences if base[s["key"]] is None and new[s["key"]] is not None]
    by_label = Counter(s["label"] for s in newly)
    tot = Counter(s["label"] for s in sentences if base[s["key"]] is None)
    sup = tot["supported"]
    row = {"mode": name, "newly_removed": len(newly), "supported_removed": by_label["supported"],
           "unsupported_caught": by_label["unsupported"], "wrong_law_caught": by_label["wrong-law"],
           "over_removal_%": round(100 * by_label["supported"] / max(1, sup), 1)}
    return row, newly


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    sentences = load_sentences()
    total = Counter(s["label"] for s in sentences)
    print("labelled sentences:", dict(total), "(", len(sentences), ")")
    base = run(sentences, False, False)
    kept_base = Counter(s["label"] for s in sentences if base[s["key"]] is None)
    print("pass the V3.3 checks (what a V3.3 answer would have shown), by label:", dict(kept_base))
    rows = []
    for name, cond, guards in (("V2.7 full", True, True), ("conditions only", True, False), ("guards only", False, True)):
        new = run(sentences, cond, guards)
        row, newly = summarise(name, sentences, base, new)
        rows.append(row)
        print(row)
        if args.list and name == "V2.7 full":
            for s in newly:
                print("   -", s["label"], new[s["key"]], "|", s["key"], "|", s["sentence"][:110])
    config.CONDITION_CHECKS = config.GUARDS_V27 = True


if __name__ == "__main__":
    main()
