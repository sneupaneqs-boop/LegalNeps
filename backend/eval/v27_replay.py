"""V2.7 offline replay of the 30 set-B answers (and the 30 answers30 ones): which MODE would the pipeline now choose?

For each question: the offline analysis (no LLM rewrite), the current retrieval (V2.7 routes + playbook pins), the V3.3
topical-fit gate with the V2.7 non-substantive filter and STRICT (direct) fit, then the decision `generation.run` takes
before calling a model:

    abstain     fewer than FIT_MIN_ONTOPIC on-topic statutes, or no directly-fitting statute, and no pinned/routed section
    ask model   otherwise: stays "structured" when the live answer was structured and at least MIN_VERIFIED_RULES labelled
                rule sentences survive the V2.7 sentence checks (sentence_replay.py numbers), else "fallback"

The sentence part needs the labelled fixtures (tests/data/v27_reviewB_fixture.json, v33_review_fixture.json) and is
reported by `eval/v27_sentences.py`. Run:

    DENSE_MODEL_DIR=... python eval/v27_replay.py [--set answers30b|answers30]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

from app import config, fit_reply, generation as g, structured  # noqa: E402
from app.retrieval import get_index  # noqa: E402

R = ROOT / "eval" / "reports"
SETS = {"answers30b": ("answer-review-v33-answers30b-20261001.json", "b"), "answers30": ("answer-review-v32-answers30-20260930.json", "a")}


_BY_TEXT: dict[str, int] = {}


def _live_passages(answer: dict) -> list[dict]:
    """The passages the LIVE answer cited or listed (an offline run has no LLM query rewrite, so its retrieval differs from
    the live one: these are added as extra candidates, after the retrieved ones, as the V3.3 replay did)."""
    idx = get_index()
    if not _BY_TEXT:
        for i, e in enumerate(idx.iter_entries()):
            t = (e.get("text_ne") or "").strip()
            if t:
                _BY_TEXT.setdefault(t, i)
    out = []
    for sent in answer.get("sentences") or []:
        for c in sent.get("cites") or []:
            i = _BY_TEXT.get(((c.get("passage") or {}).get("text_ne") or "").strip())
            if i is not None:
                out.append(idx.get(i))
    for _, head in re.findall(r"\*\*\[(\d+)\]\s*([^*]+)\*\*", answer.get("answer") or ""):
        for e in idx.iter_entries():  # linear scan, only for the (few) fallback answers
            if head.strip() in (e.get("source_ne"), e.get("source_en")):
                out.append(e)
                break
    return out


def decide(question: str, answer: dict | None = None) -> dict:
    an = g.analyze_query(question, "auto")
    pb = g._match_playbook(question, an)
    sources = g.search(an.get("question") or question, an, playbook=pb)
    if answer is not None:
        have = {s["id"] for s in sources}
        sources = sources + [dict(e) for e in _live_passages(answer) if e["id"] not in have and not have.add(e["id"])]
    if pb and not any(s.get("pinned") and (not s.get("routed") or s.get("plan_pin")) for s in sources):
        pb = None
    fit_reply.relabel_subsections(sources)
    rep = g.apply_topical_gate(question, an, sources, pb)
    pinned = any(s.get("pinned") for s in sources)
    on = fit_reply.on_topic_laws(sources)
    direct = fit_reply.direct_laws(sources)
    if rep is not None and not pinned and (len(on) < config.FIT_MIN_ONTOPIC or (config.FIT_ABSTAIN_STRICT and not direct)):
        mode = "abstain"
    else:
        mode = "ask_model"
    return {"mode": mode, "sources": sources, "playbook": pb, "on_topic": len(on), "direct": len(direct), "pinned": pinned,
            "failed": [(s["id"], s.get("off_topic_why")) for s in sources if s.get("off_topic")]}


def rules_left(answer_id: str) -> int | None:
    """Labelled rule/deadline/penalty sentences of a set-B answer that still pass every check (V3.3 + V2.7); None when the
    answer has no labelled sentences (not structured)."""
    import v27_sentences as vs
    sents = [x for x in vs.load_sentences() if x["answer"] == f"r3:{answer_id}"]
    if not sents:
        return None
    vs.config.CONDITION_CHECKS = vs.config.GUARDS_V27 = True
    kept = [x for x in sents if vs.reason_for(x) is None]
    return sum(1 for x in kept if (x.get("kind") or "rule") in ("rule", "deadline", "penalty")), len(kept), len(sents)


def fallback_text(d: dict, lang: str) -> str:
    return fit_reply.extractive_answer(d["sources"], lang, "DISCLAIMER", None, d["playbook"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="answers30b")
    ap.add_argument("--show", action="store_true", help="print the fallback / abstain text of every non-structured outcome")
    args = ap.parse_args()
    fname, _ = SETS[args.set]
    answers = json.loads((R / fname).read_text(encoding="utf-8"))["answers"]
    get_index()
    tally: dict[str, list[str]] = {}
    for a in answers:
        d = decide(a["question"], a)
        live = a["mode"]
        lang = "en" if a.get("language") == "en" else "ne"
        if d["mode"] == "abstain":
            new = "abstain"
        elif live == "structured":
            new = "structured"
            if args.set == "answers30b":
                left = rules_left(a["id"])
                if left is not None and left[0] < structured.MIN_VERIFIED_RULES:
                    new = "fallback"  # too few verified rules survive the V2.7 sentence checks
        else:
            # a fallback / no-LLM answer stays a fallback, but may now be an abstain (no direct fit among the shown)
            txt = fallback_text(d, lang)
            new = "abstain" if txt.startswith(("मैले खोजेका", "I couldn't find")) else "fallback"
        tally.setdefault(f"{live}->{new}", []).append(a["id"])
        print(f"{a['id']} live={live:<19} v27={new:<10} on_topic={d['on_topic']} direct={d['direct']} pinned={d['pinned']} | {a['question'][:60]}")
        if args.show and new != "structured":
            print("    " + fallback_text(d, lang)[:900].replace("\n", "\n    "))
    print()
    for k, v in sorted(tally.items()):
        print(f"{k:<32} {len(v)}  {' '.join(v)}")


if __name__ == "__main__":
    main()
