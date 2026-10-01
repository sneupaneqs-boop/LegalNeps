"""Assemble the 147 human-labelled sentences of the two live answer reviews into ONE committed fixture
(tests/data/v33_review_fixture.json), so the V3.3 topical-fit gate can be calibrated and tested without the
git-ignored eval/reports/ files:

  review 1 = answer-review-v3-labels-20260930.json       + answer-review-v3-realworld-20260930.json   (77 sentences)
  review 2 = answer-review-v32-labels-20260930.json      + answer-review-v32-answers30-20260930.json  (70 sentences, FRESH questions)

Per sentence: the question, the label, the sentence, its cites (n = the passage number the model saw = the rank
of that passage in the answer's source list) and the FULL cited passage (resolved to the corpus entry by text, so
its id, law title, section and heading are known). Per answer: `candidates`, the ids of the sources an OFFLINE
retrieval of the same question returns (no LLM query rewrite is available offline, so it approximates the live
source list; it is what the relative dense features are computed against).

    DENSE_MODEL_DIR=<main checkout>/backend/app/data/dense_model python eval/build_review_fixture.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import generation as g  # noqa: E402
from app.retrieval import get_index  # noqa: E402

R = ROOT / "eval" / "reports"
OUT = ROOT / "tests" / "data" / "v33_review_fixture.json"
FIELDS = ("id", "doc_title_ne", "doc_title_en", "title_ne", "title_en", "section", "category", "doc_type",
          "source_ne", "source_en", "text_ne", "text_en", "status")


def main() -> None:
    idx = get_index()
    by_text: dict[str, int] = {}
    for i, e in enumerate(idx.iter_entries()):
        t = (e.get("text_ne") or "").strip()
        if t:
            by_text.setdefault(t, i)

    def resolve(p: dict, citation: str) -> dict:
        i = by_text.get((p.get("text_ne") or "").strip())
        if i is None:
            return {"id": None, "text_ne": p.get("text_ne"), "text_en": p.get("text_en"), "doc_title_ne": citation}
        e = idx.get(i)
        return {k: e.get(k) for k in FIELDS}

    sentences, answers = [], {}
    for review, labels_f, answers_f in ((1, "answer-review-v3-labels-20260930.json", "answer-review-v3-realworld-20260930.json"),
                                        (2, "answer-review-v32-labels-20260930.json", "answer-review-v32-answers30-20260930.json")):
        labels = json.loads((R / labels_f).read_text(encoding="utf-8"))
        by_id = {a["id"]: a for a in json.loads((R / answers_f).read_text(encoding="utf-8"))["answers"]}
        for s in labels["sentences"]:
            a = by_id[s["answer_id"]]
            sent = next(x for x in a["sentences"] if x["text"].strip() == s["sentence"].strip())
            akey = f"r{review}:{s['answer_id']}"
            if akey not in answers:
                an = g.analyze_query(a["question"], "auto")
                pb = g._match_playbook(a["question"], an)
                cand = g.search(an.get("question") or a["question"], an, playbook=pb)
                answers[akey] = {"review": review, "answer_id": s["answer_id"], "question": a["question"],
                                 "language": a.get("language"), "playbook": pb and pb.get("id"),
                                 "candidates": [c["id"] for c in cand]}
            cites = []
            for c in sent["cites"]:
                cites.append({"n": c["n"], "quote": c["quote"], "citation": c.get("citation"),
                              **resolve(c.get("passage") or {}, c.get("citation"))})
            sentences.append({"key": f"r{review}:{s['answer_id']}:{s.get('id') or s.get('sentence_index')}",
                              "answer": akey, "review": review, "label": s["label"], "sentence": s["sentence"],
                              "kind": sent.get("kind"), "cites": cites,
                              "note": (s.get("evidence_and_note") or s.get("note") or "")[:400]})
    OUT.write_text(json.dumps({"about": __doc__.strip().split("\n\n")[0], "answers": answers, "sentences": sentences},
                              ensure_ascii=False), encoding="utf-8")
    print(f"{len(sentences)} sentences, {len(answers)} answers -> {OUT}")


if __name__ == "__main__":
    main()
