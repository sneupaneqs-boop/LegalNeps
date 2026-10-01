"""V2.7: the 49 human-labelled sentences of the V3.3 live review (fresh set B, 2026-10-01) as a committed fixture
(tests/data/v27_reviewB_fixture.json), in the same shape as tests/data/v33_review_fixture.json (reviews 1 and 2), so the
V2.7 sentence checks (actor / population / regime guards, dropped conditions) can be tested and their over-removal
measured on all 196 labelled sentences without the eval/reports/ files.

    answer-review-v33-labels-20261001.json  (labels, one per kept sentence)  +
    answer-review-v33-answers30b-20261001.json (the live answers with each sentence's cited passages)

    DENSE_MODEL_DIR=<dir> python eval/build_reviewB_fixture.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.retrieval import get_index  # noqa: E402

R = ROOT / "eval" / "reports"
OUT = ROOT / "tests" / "data" / "v27_reviewB_fixture.json"
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

    labels = json.loads((R / "answer-review-v33-labels-20261001.json").read_text(encoding="utf-8"))
    answers = {a["id"]: a for a in json.loads((R / "answer-review-v33-answers30b-20261001.json").read_text(encoding="utf-8"))["answers"]}
    sentences, answer_meta = [], {}
    for s in labels["sentences"]:
        a = answers[s["answer"]]
        sent = next(x for x in a["sentences"] if x["text"].strip() == s["sentence"].strip())
        akey = f"r3:{s['answer']}"
        answer_meta.setdefault(akey, {"review": 3, "answer_id": s["answer"], "question": a["question"],
                                      "language": a.get("language"), "mode": a.get("mode")})
        cites = [{"n": c["n"], "quote": c["quote"], "citation": c.get("citation"), **resolve(c.get("passage") or {}, c.get("citation"))}
                 for c in sent["cites"]]
        sentences.append({"key": f"r3:{s['id']}", "answer": akey, "review": 3, "label": s["label"], "sentence": s["sentence"],
                          "kind": sent.get("kind"), "cites": cites, "borderline": bool(s.get("borderline")),
                          "tangential": bool(s.get("tangential")), "note": (s.get("note") or "")[:400]})
    OUT.write_text(json.dumps({"about": __doc__.strip().split("\n\n")[0], "answers": answer_meta, "sentences": sentences},
                              ensure_ascii=False), encoding="utf-8")
    print(f"{len(sentences)} sentences, {len(answer_meta)} answers -> {OUT}")


if __name__ == "__main__":
    main()
