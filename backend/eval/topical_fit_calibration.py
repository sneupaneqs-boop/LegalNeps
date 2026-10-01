"""Calibrate and TEST the V3.3 topical-fit gate on the two human-labelled live reviews.

Protocol (docs/PROGRESS.md, V3.3):
  1. features for every labelled (question, cited passage) pair, offline (tests/data/v33_review_fixture.json;
     needs the dense model: DENSE_MODEL_DIR=<main checkout>/backend/app/data/dense_model);
  2. FIT weights + thresholds on review 1 ONLY (77 sentences: 4 statute wrong-law, 3 precedent wrong-law);
  3. TEST on review 2 (70 FRESH sentences, 24 wrong-law) with nothing re-fitted; per-feature ablation (each ablated
     model is refitted on review 1 and tested on review 2);
  4. only then refit on BOTH reviews for production (data/topical_fit.json); leave-one-answer-out CV over all 147
     is reported as the honest estimate for that model.

    python eval/topical_fit_calibration.py --stage r1     # design view: review 1 only (fit + leave-one-answer-out CV)
    python eval/topical_fit_calibration.py --stage test   # review 1 -> review 2 held-out numbers + ablation
    python eval/topical_fit_calibration.py --stage prod   # refit on both, write app/data/topical_fit.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import generation as g, topical_fit as tf  # noqa: E402
from app.retrieval import get_index  # noqa: E402

FIXTURE = ROOT / "tests" / "data" / "v33_review_fixture.json"
REPORT = ROOT / "eval" / "reports" / "topical-fit-calibration-20260930.json"
FEATCACHE = ROOT / "eval" / "reports" / "topical-fit-features.json"
MODEL_OUT = ROOT / "app" / "data" / "topical_fit.json"
R1MODEL = ROOT / "eval" / "reports" / "topical-fit-model-r1.json"  # fitted on review 1 only (the held-out model)
SIGN = {"rank": +1, "d_head": -1, "d_head_rel": -1, "d_pass_rel": -1, "q_cov_head": -1, "q_cov_body": -1,
        "h_unexpl": +1, "l_unexpl": +1}
MAX_OVER = 0.10        # over-removal budget on the fitting set supported sentences for the reported held-out test (acceptance limit: 15%)
PROD_MAX_OVER = 0.05   # budget used for the production refit (sensitivity of the held-out result to it is reported)
BAD_TOPIC = {"wrong-law"}


# ------------------------------------------------------------------ features
def build_features(force: bool = False) -> list[dict]:
    if FEATCACHE.exists() and not force:
        return json.loads(FEATCACHE.read_text(encoding="utf-8"))
    fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
    idx = get_index()
    assert idx.dense is not None, "set DENSE_MODEL_DIR to the dense model directory (main checkout)"
    rows_by_id = {pid: i for i, pid in enumerate(idx.ids)}
    per_answer: dict[str, dict] = {}
    for akey, a in fx["answers"].items():
        an = g.analyze_query(a["question"], "auto")
        pb = g._match_playbook(a["question"], an)
        guidance = g._guidance_terms_text(pb)
        prof = tf.make_profile(a["question"], an, guidance, g.build_queries(a["question"], an))
        cited = {c["id"]: c for s in fx["sentences"] if s["answer"] == akey for c in s["cites"] if c.get("id")}
        cands = [idx.get(rows_by_id[i]) for i in a["candidates"] if i in rows_by_id]
        ids = {c["id"] for c in cands}
        cands += [idx.get(rows_by_id[i]) for i in cited if i not in ids and i in rows_by_id]
        sc = tf.Scorer(prof, idx=idx, model={"dense": True}, use_dense=True)
        feats = sc.features(cands)
        per_answer[akey] = {c["id"]: f for c, f in zip(cands, feats)}
    out = []
    for s in fx["sentences"]:
        for c in s["cites"]:
            f = dict(per_answer[s["answer"]][c["id"]])
            f["rank"] = float(c["n"])
            f["specialist_all"] = f["specialist"]
            out.append({"key": s["key"], "answer": s["answer"], "review": s["review"], "label": s["label"],
                        "prec": c.get("category") == "precedent", "cite": c["id"], "n": c["n"], "f": f,
                        "head": c.get("title_ne"), "law": c.get("doc_title_ne")})
    FEATCACHE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


# ------------------------------------------------------------------ fitting
def _matrix(rows, names):
    X = np.array([[np.nan if r["f"].get(n) is None else r["f"][n] for n in names] for r in rows], dtype=float)
    return X


def _standardise(X, mu=None, sd=None):
    if mu is None:
        mu = np.nanmean(X, axis=0)
        sd = np.nanstd(X, axis=0)
        sd[sd < 1e-9] = 1.0
    Z = (X - mu) / sd
    Z[np.isnan(Z)] = 0.0
    return Z, mu, sd


def fit_weights(Z, y, sign, lam, iters=800, lr=0.1):
    """L2 logistic regression with balanced classes and prior sign constraints (projected gradient)."""
    n, k = Z.shape
    w = np.zeros(k)
    b = 0.0
    pos, neg = y.sum(), (1 - y).sum()
    sw = np.where(y == 1, 0.5 / max(pos, 1), 0.5 / max(neg, 1)) * n
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(Z @ w + b)))
        gw = Z.T @ (sw * (p - y)) / n + lam * w
        gb = (sw * (p - y)).sum() / n
        w -= lr * gw
        b -= lr * gb
        w = np.where(w * sign < 0, 0.0, w)
    return w, b


def choose_threshold(z, y, is_supported, max_over):
    """Lowest threshold (most removal) whose over-removal of supported sentences stays within budget."""
    sup = z[is_supported]
    if len(sup) == 0:
        return float(np.max(z))
    allowed = int(math.floor(max_over * len(sup)))
    srt = np.sort(sup)[::-1]  # highest supported scores first: the first `allowed` may be removed
    cut = srt[allowed] if allowed < len(srt) else srt[-1] - 1
    return float(cut)  # remove score > cut


def fit_variant(rows, names, lam, max_over=MAX_OVER):
    stat = [r for r in rows if not r["prec"]]
    X = _matrix(stat, names)
    Z, mu, sd = _standardise(X)
    y = np.array([1 if r["label"] in BAD_TOPIC else 0 for r in stat], dtype=float)
    sign = np.array([SIGN[n] for n in names], dtype=float)
    w, b = fit_weights(Z, y, sign, lam)
    z = Z @ w + b
    sup = np.array([r["label"] == "supported" for r in stat])
    thr = choose_threshold(z, y, sup, max_over)
    # precedents: body features only (a case title carries no topic); own threshold on the precedent rows
    prec = [r for r in rows if r["prec"]]
    thr_p = 1e9
    if prec:
        zp = np.array([_score_row(r, {"features": names, "w": w, "mean": mu, "std": sd, "b": b}, True) for r in prec])
        sup_p = np.array([r["label"] == "supported" for r in prec])
        thr_p = choose_threshold(zp, None, sup_p, max_over) if sup_p.any() else float(np.min(zp)) - 1
    return {"features": list(names), "w": [float(x) for x in w], "mean": [float(x) for x in mu],
            "std": [float(x) for x in sd], "b": float(b), "threshold": float(thr), "threshold_prec": float(thr_p),
            "lam": lam}


def _score_row(r, v, prec=False):
    return tf.score(r["f"], {**v, "features": v["features"], "w": list(v["w"]), "mean": list(v["mean"]),
                             "std": list(v["std"])}, prec)


def sentence_verdicts(rows, variant, sources):
    """Per sentence: removed? (every cited passage fails: low topical fit or a specialist marker)."""
    out = {}
    for r in rows:
        prec = r["prec"]
        z = _score_row(r, variant, prec)
        thr = variant["threshold_prec"] if prec else variant["threshold"]
        spec = [x for x in r["f"]["specialist_all"] if not prec and _fam_source(x) in sources]
        fail = z > thr or bool(spec)
        out[r["key"]] = out.get(r["key"], True) and fail
    return out


_FAMSRC = {f.id: f.source for f in tf.SPECIALIST}


def _fam_source(fid):
    return _FAMSRC[fid]


def evaluate(rows, variant, sources=("corpus", "review1")):
    v = sentence_verdicts(rows, variant, sources)
    lab = {}
    for r in rows:
        lab[r["key"]] = r["label"]
    res = {}
    for name, labels in (("wrong-law", {"wrong-law"}), ("unsupported", {"unsupported", "hallucinated-number-or-section"}),
                         ("supported", {"supported"})):
        ks = [k for k, l in lab.items() if l in labels]
        res[name] = {"n": len(ks), "removed": sum(v[k] for k in ks)}
    removed_bad = res["wrong-law"]["removed"] + res["unsupported"]["removed"]
    removed_all = removed_bad + res["supported"]["removed"]
    res["precision_bad"] = removed_bad / removed_all if removed_all else float("nan")
    res["recall_wrong_law"] = res["wrong-law"]["removed"] / res["wrong-law"]["n"] if res["wrong-law"]["n"] else float("nan")
    res["over_removal"] = res["supported"]["removed"] / res["supported"]["n"] if res["supported"]["n"] else float("nan")
    return res


def loao_cv_logloss(rows, names, lam):
    """Leave-one-answer-out log-loss of the statute model (to choose lambda)."""
    stat = [r for r in rows if not r["prec"]]
    answers = sorted({r["answer"] for r in stat})
    tot, n = 0.0, 0
    for a in answers:
        tr = [r for r in stat if r["answer"] != a]
        te = [r for r in stat if r["answer"] == a]
        X = _matrix(tr, names)
        Z, mu, sd = _standardise(X)
        y = np.array([1 if r["label"] in BAD_TOPIC else 0 for r in tr], dtype=float)
        sign = np.array([SIGN[nm] for nm in names], dtype=float)
        w, b = fit_weights(Z, y, sign, lam)
        Zt, _, _ = _standardise(_matrix(te, names), mu, sd)
        p = 1 / (1 + np.exp(-(Zt @ w + b)))
        yt = np.array([1 if r["label"] in BAD_TOPIC else 0 for r in te], dtype=float)
        tot += float(-(yt * np.log(p + 1e-9) + (1 - yt) * np.log(1 - p + 1e-9)).sum())
        n += len(te)
    return tot / max(n, 1)


def auc(pos, neg):
    if not len(pos) or not len(neg):
        return float("nan")
    return float(np.mean([(p > q) + 0.5 * (p == q) for p in pos for q in neg]))


def pick_lambda(rows, names):
    best = None
    for lam in (0.003, 0.01, 0.03, 0.1, 0.3, 1.0):
        ll = loao_cv_logloss(rows, names, lam)
        if best is None or ll < best[1]:
            best = (lam, ll)
    return best


ALL_NAMES = list(tf.FEATURES)
LEX_NAMES = [n for n in ALL_NAMES if n not in tf.DENSE_FEATURES]


def show(title, res):
    print(f"{title}: wrong-law removed {res['wrong-law']['removed']}/{res['wrong-law']['n']}, "
          f"unsupported removed {res['unsupported']['removed']}/{res['unsupported']['n']}, "
          f"supported removed {res['supported']['removed']}/{res['supported']['n']} "
          f"(over-removal {res['over_removal']:.1%}); precision(bad among removed)={res['precision_bad']:.2f} "
          f"recall(wrong-law)={res['recall_wrong_law']:.2f}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("r1", "test", "prod"), default="r1")
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    rows = build_features(args.rebuild)
    r1 = [r for r in rows if r["review"] == 1]
    r2 = [r for r in rows if r["review"] == 2]

    if args.stage == "r1":
        stat = [r for r in r1 if not r["prec"]]
        print("review 1:", len(r1), "cite rows;", sum(r["label"] == "wrong-law" for r in stat), "statute wrong-law,",
              sum(r["label"] == "wrong-law" for r in r1 if r["prec"]), "precedent wrong-law")
        for n in ALL_NAMES:
            pos = [r["f"].get(n) for r in stat if r["label"] == "wrong-law" and r["f"].get(n) is not None and not math.isnan(r["f"][n])]
            neg = [r["f"].get(n) for r in stat if r["label"] != "wrong-law" and r["f"].get(n) is not None and not math.isnan(r["f"][n])]
            a = auc(pos, neg)
            print(f"  {n:12s} AUC(off-topic higher)={a:.2f} (direction prior {'+' if SIGN[n] > 0 else '-'}) "
                  f"mean pos={np.mean(pos):.3f} neg={np.mean(neg):.3f}")
        for names, tag in ((ALL_NAMES, "dense+lexical"), (LEX_NAMES, "lexical only")):
            lam, ll = pick_lambda(r1, names)
            v = fit_variant(r1, names, lam)
            print(tag, "lambda", lam, "cv-logloss", round(ll, 3), "weights", dict(zip(names, np.round(v["w"], 2))), "thr", round(v["threshold"], 2), "thr_prec", round(v["threshold_prec"], 2))
            show("  R1 in-sample", evaluate(r1, v))
        return

    if args.stage == "test":
        report = {"protocol": "fit review 1 only; test review 2 with nothing re-fitted"}
        for names, tag in ((ALL_NAMES, "dense_lexical"), (LEX_NAMES, "lexical_only")):
            lam, _ = pick_lambda(r1, names)
            v = fit_variant(r1, names, lam)
            res1, res2 = evaluate(r1, v), evaluate(r2, v)
            print(f"=== {tag} (lambda {lam})")
            show("R1 (fit)", res1)
            show("R2 (TEST)", res2)
            report[tag] = {"variant": v, "review1": res1, "review2": res2, "ablation": {}}
            # per-feature ablation: refit on R1 without the feature, test on R2
            for drop in names:
                sub = [n for n in names if n != drop]
                l2, _ = pick_lambda(r1, sub)
                vv = fit_variant(r1, sub, l2)
                rr = evaluate(r2, vv)
                report[tag]["ablation"][f"-{drop}"] = rr
                show(f"  drop {drop:11s}", rr)
            for src, label in ((("corpus", "review1"), "specialist markers: corpus+review1 (held-out)"),
                               ((), "specialist markers OFF"),
                               (("corpus", "review1", "review2"), "specialist markers incl. review2 (in-sample on R2)")):
                rr = evaluate(r2, v, src)
                report[tag]["ablation"][label] = rr
                show(f"  {label}", rr)
            # sensitivity to the over-removal budget used when fitting the threshold on review 1
            report[tag]["budget_sensitivity"] = {}
            for bud in (0.10, 0.05, 0.03, 0.0):
                vb = fit_variant(r1, names, lam, max_over=bud)
                rb = evaluate(r2, vb)
                report[tag]["budget_sensitivity"][str(bud)] = rb
                show(f"  budget {bud:.0%}", rb)
            # each single feature alone (its own threshold from R1)
            for only in names:
                lam1 = 0.01
                vv = fit_variant(r1, [only], lam1)
                rr = evaluate(r2, vv, ())
                report[tag]["ablation"][f"only {only}"] = rr
                show(f"  only {only:11s}", rr)
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
        R1MODEL.write_text(json.dumps({"lexical": report["lexical_only"]["variant"], "dense": report["dense_lexical"]["variant"],
                                       "specialist_sources": ["corpus", "review1"]}, ensure_ascii=False, indent=1),
                           encoding="utf-8")
        print("wrote", REPORT, R1MODEL)
        return

    # prod: refit on both reviews
    allr = r1 + r2
    out = {"about": "V3.3 topical-fit gate; weights/threshold fitted by eval/topical_fit_calibration.py --stage prod on "
                    "reviews 1+2 (147 sentences). Held-out numbers (fit on review 1, test on review 2) are in "
                    "docs/PROGRESS.md V3.3 and eval/reports/topical-fit-calibration-20260930.json.",
           "specialist_sources": ["corpus", "review1", "review2"]}
    for names, tag in ((ALL_NAMES, "dense"), (LEX_NAMES, "lexical")):
        lam, ll = pick_lambda(allr, names)
        v = fit_variant(allr, names, lam, max_over=PROD_MAX_OVER)
        out[tag] = v
        show(f"prod {tag} (in-sample, both reviews)", evaluate(allr, v, ("corpus", "review1", "review2")))
        # leave-one-answer-out over both reviews (threshold re-chosen inside each fold)
        answers = sorted({r["answer"] for r in allr})
        folds = {}
        for a in answers:
            tr = [r for r in allr if r["answer"] != a]
            te = [r for r in allr if r["answer"] == a]
            l2, _ = pick_lambda(tr, names) if False else (lam, None)
            vv = fit_variant(tr, names, l2, max_over=PROD_MAX_OVER)
            sv = sentence_verdicts(te, vv, ("corpus", "review1", "review2"))
            for r in te:
                folds[r["key"]] = sv[r["key"]]
        lab = {r["key"]: r["label"] for r in allr}
        cv = {"wrong-law": [0, 0], "unsupported": [0, 0], "supported": [0, 0]}
        for k, removed in folds.items():
            name = "wrong-law" if lab[k] == "wrong-law" else ("supported" if lab[k] == "supported" else "unsupported")
            cv[name][1] += 1
            cv[name][0] += int(removed)
        print(f"  leave-one-answer-out over 147: {cv}")
        out[tag]["loao_cv"] = cv
    out["dense"]["features_note"] = "all features"
    MODEL_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", MODEL_OUT)


if __name__ == "__main__":
    main()
