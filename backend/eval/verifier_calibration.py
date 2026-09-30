"""Calibrate the deterministic checks of the V3 verifier on the 119 human-labelled claims of the V1 review.

For each labelled claim, the passage it cites (full text from the corpus, looked up by source id) is treated
as the quote source and the *best-matching span* of it (<= 40 words, most overlap with the claim, preferring
spans that contain the claim's numbers) is used as the quote - i.e. the most favourable quote a model could
have picked - then each check is asked whether it would still remove the claim. Reported per check and
combined, per bad-claim type. A claim with no citation is removed by the "no_citation" rule.

    python eval/verifier_calibration.py [--write eval/reports/verifier-calibration-YYYYMMDD.json]

Not measured here (needs the live pipeline): whether the model's real quotes are verbatim, and whether the
wrong-law claims still get a real quote. See docs/PROGRESS.md (V3).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import verifier  # noqa: E402
from app.retrieval import corpus_source  # noqa: E402
from app.text_norm import DEV_DIGITS, tokenize  # noqa: E402

REVIEW = ROOT / "eval" / "reports" / "live-review-20260930.json"
BAD = {"unsupported", "wrong-law", "hallucinated-number-or-section"}
_BRACKET = re.compile(r"\[[^\]]*\]")
_CITE = re.compile(r"\[(\d{1,2})(?::[^\]]*)?\]")
_SHORT_REF = re.compile(r"\b([sr])\.\s*(?=[0-9])", re.I)


def load_passages(ids: set[str]) -> dict[str, dict]:
    found: dict[str, dict] = {}
    entries, _ = corpus_source()
    for e in entries:
        if e.get("id") in ids:
            found[e["id"]] = e
            if len(found) == len(ids):
                break
    return found


def clean_claim(claim: str) -> str:
    text = _SHORT_REF.sub(lambda m: "Section " if m.group(1).lower() == "s" else "Rule ", claim)
    return _BRACKET.sub(" ", text).strip()


def best_quote(claim: str, src: dict, max_words: int = 40) -> str:
    """The span of the passage most favourable to the claim."""
    want = set(tokenize(claim))
    nums = verifier._sentence_numbers(claim)
    best, best_score = "", -1.0
    for field in ("text_ne", "text_en"):
        text = src.get(field) or ""
        words = text.split()
        if not words:
            continue
        step = 8
        for start in range(0, max(1, len(words)), step):
            span = " ".join(words[start:start + max_words])
            toks = set(tokenize(span))
            score = len(want & toks) + 2 * len(nums & verifier._numbers_in(span))
            if score > best_score:
                best, best_score = span, score
        # lexical overlap is script-sensitive: also try the bridge-aware score for the other script
    if best_score <= 0:  # nothing overlaps directly (English claim vs Nepali text): score through the bridge
        for field in ("text_ne", "text_en"):
            words = (src.get(field) or "").split()
            for start in range(0, max(1, len(words)), 8):
                span = " ".join(words[start:start + max_words])
                score = verifier.lexical_support(claim, span)[1] + 2 * len(nums & verifier._numbers_in(span))
                if score > best_score:
                    best, best_score = span, score
    return best


def evaluate(review_path: Path = REVIEW) -> dict:
    data = json.loads(review_path.read_text(encoding="utf-8"))
    ids = {s["id"] for a in data["answers"] for s in a["sources"]}
    passages = load_passages(ids)
    rows = []
    for a in data["answers"]:
        sources = []
        for s in a["sources"]:
            full = passages.get(s["id"], {})
            sources.append({**full, "category": s.get("category"), "status": s.get("status"),
                            "stale": s.get("stale"), "section": s.get("section") or full.get("section"),
                            "source_ne": full.get("source_ne") or s.get("citation"), "id": s["id"]})
        views = [verifier._View(s) for s in sources]
        for c in a["review"]["claims"]:
            claim = c["claim"]
            ns = [int(n) for n in _CITE.findall(claim)]
            ns = [n for n in ns if 1 <= n <= len(sources)]
            text = clean_claim(claim)
            cites = [{"n": n, "quote": best_quote(text, sources[n - 1])} for n in ns]
            good = [n for n in ns if not (sources[n - 1].get("status") in verifier._BAD_STATUS
                                          or sources[n - 1].get("stale"))]
            sentence = {"text": text, "kind": "rule", "cites": cites}
            reason, _ = verifier.check_structured_sentence(sentence, sources, views)
            quote_nums = set().union(*(verifier._numbers_in(q["quote"]) for q in cites)) if cites else set()
            pool = quote_nums | set().union(*(views[n - 1].numbers for n in ns)) if ns else set()
            lex = [verifier.lexical_support(text, q["quote"]) for q in cites]
            flags = {
                "no_citation": not ns,
                "number": bool(ns) and not verifier._sentence_numbers(text) <= pool,
                "section": bool(ns) and not verifier._section_refs(text) <= (
                    quote_nums | {(sources[n - 1].get("section") or "").translate(DEV_DIGITS).split(" ")[0] for n in ns}),
                "status": bool(ns) and not good and not verifier._OLDER_LABEL.search(text),
                "court": bool(ns) and bool(verifier._COURT_CLAIM.search(text))
                and not any(sources[n - 1].get("category") == "precedent" for n in ns),
                "lexical": bool(lex) and max(l[2] and (l[1] < 1 or l[0] < verifier.LEX_MIN_RATIO) for l in lex),
            }
            rows.append({"id": a["id"], "claim": claim, "label": c["label"], "lang": a["answer_language"],
                         "cited": bool(ns), "flags": flags, "removed": bool(reason), "reason": reason,
                         "lex": [round(l[0], 2) for l in lex],
                         "verifier_flagged": c.get("verifier_flagged")})
    summary = summarise(rows)
    summary["lexical_threshold_sweep"] = lexical_sweep(data, passages)
    summary["synthetic_mutations"] = mutation_tests(data, passages)
    return {"rows": rows, "summary": summary}


def _sources_of(a: dict, passages: dict) -> list[dict]:
    return [{**passages.get(s["id"], {}), "category": s.get("category"), "status": s.get("status"),
             "stale": s.get("stale"), "section": s.get("section") or passages.get(s["id"], {}).get("section"),
             "id": s["id"]} for s in a["sources"]]


def lexical_sweep(data: dict, passages: dict, seed: int = 7) -> list[dict]:
    """How well 'sentence vs quote word overlap' separates a claim's own passage from an unrelated one.
    Both quotes are the best-matching span of their passage, i.e. the unrelated quote is chosen as
    favourably to the sentence as possible - the hardest case for an overlap test."""
    import random
    rng = random.Random(seed)
    pool = [(a["id"], s) for a in data["answers"] for s in _sources_of(a, passages) if s.get("text_ne")]
    own, other = [], []
    for a in data["answers"]:
        sources = _sources_of(a, passages)
        for c in a["review"]["claims"]:
            n = [int(x) for x in _CITE.findall(c["claim"]) if 1 <= int(x) <= len(sources)]
            if not n or c["label"] in BAD:
                continue
            text = clean_claim(c["claim"])
            own.append(verifier.lexical_support(text, best_quote(text, sources[n[0] - 1])))
            for _ in range(3):
                aid, src = rng.choice(pool)
                while aid == a["id"]:
                    aid, src = rng.choice(pool)
                other.append(verifier.lexical_support(text, best_quote(text, src)))
    out = []
    for thr in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
        rej = lambda x: bool(x[2]) and (x[1] < 1 or x[0] < thr)  # noqa: E731
        out.append({"threshold": thr, "own_passage_wrongly_rejected": round(sum(map(rej, own)) / len(own), 3),
                    "unrelated_passage_rejected": round(sum(map(rej, other)) / len(other), 3),
                    "n_own": len(own), "n_unrelated": len(other)})
    return out


def mutation_tests(data: dict, passages: dict) -> dict:
    """Take supported cited claims that state a number and change it (or a section): does the check remove it?"""
    total = caught = sec_total = sec_caught = 0
    for a in data["answers"]:
        sources = _sources_of(a, passages)
        views = [verifier._View(s) for s in sources]
        for c in a["review"]["claims"]:
            n = [int(x) for x in _CITE.findall(c["claim"]) if 1 <= int(x) <= len(sources)]
            text = clean_claim(c["claim"])
            if not n or c["label"] in BAD:
                continue
            quote = best_quote(text, sources[n[0] - 1])
            base = {"text": text, "kind": "rule", "cites": [{"n": n[0], "quote": quote}]}
            ok = verifier.check_structured_sentence(base, sources, views)[0] is None
            nums = sorted(verifier._sentence_numbers(text))
            if ok and nums:
                mut = re.sub(r"\b" + re.escape(nums[0]) + r"\b", str(int(float(nums[0])) + 17), text.translate(DEV_DIGITS), count=1)
                if mut != text.translate(DEV_DIGITS):  # the number was written in digits, so it could be changed
                    total += 1
                    caught += verifier.check_structured_sentence({**base, "text": mut}, sources, views)[0] is not None
            secs = sorted(verifier._section_refs(text))
            if ok and secs:
                mut = re.sub(r"\b" + re.escape(secs[0]) + r"\b", "999", text.translate(DEV_DIGITS), count=1)
                sec_total += mut != text.translate(DEV_DIGITS)
                sec_caught += mut != text.translate(DEV_DIGITS) and verifier.check_structured_sentence({**base, "text": mut}, sources, views)[0] is not None
    return {"number_mutations": total, "number_mutations_removed": caught,
            "section_mutations": sec_total, "section_mutations_removed": sec_caught}


def prf(rows: list[dict], pred) -> dict:
    tp = sum(1 for r in rows if r["label"] in BAD and pred(r))
    fp = sum(1 for r in rows if r["label"] not in BAD and pred(r))
    fn = sum(1 for r in rows if r["label"] in BAD and not pred(r))
    p = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": round(p, 3), "recall": round(rec, 3),
            "f1": round(2 * p * rec / (p + rec), 3) if p + rec else 0.0}


def summarise(rows: list[dict]) -> dict:
    out: dict = {"claims": len(rows), "bad": sum(r["label"] in BAD for r in rows),
                 "good": sum(r["label"] not in BAD for r in rows), "by_check": {}, "by_type": {}}
    for name in ("no_citation", "number", "section", "status", "court", "lexical"):
        out["by_check"][name] = prf(rows, lambda r, n=name: r["flags"][n])
    out["combined"] = prf(rows, lambda r: r["removed"])
    out["combined_excluding_no_citation"] = prf(rows, lambda r: r["removed"] and r["reason"] != "no_citation")
    cited = [r for r in rows if r["cited"]]
    out["cited_claims_only"] = {"n": len(cited), "bad": sum(r["label"] in BAD for r in cited),
                                "content_checks": prf(cited, lambda r: r["removed"])}
    out["old_verifier"] = prf(rows, lambda r: bool(r["verifier_flagged"]))
    for label in sorted(BAD):
        sub = [r for r in rows if r["label"] == label]
        out["by_type"][label] = {
            "n": len(sub), "removed": sum(r["removed"] for r in sub),
            "recall": round(sum(r["removed"] for r in sub) / len(sub), 3) if sub else 0.0,
            "old_verifier_recall": round(sum(bool(r["verifier_flagged"]) for r in sub) / len(sub), 3) if sub else 0.0,
            "by_reason": {k: sum(r["reason"] == k for r in sub) for k in sorted({r["reason"] for r in sub if r["reason"]})},
        }
    good = [r for r in rows if r["label"] not in BAD]
    out["good_wrongly_removed"] = {"n": sum(r["removed"] for r in good), "of": len(good),
                                   "by_reason": {k: sum(r["reason"] == k for r in good)
                                                 for k in sorted({r["reason"] for r in good if r["reason"]})}}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", help="write the full report (rows + summary) here")
    args = ap.parse_args()
    res = evaluate()
    print(json.dumps(res["summary"], ensure_ascii=False, indent=1))
    if args.write:
        Path(args.write).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
