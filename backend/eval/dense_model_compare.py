"""Which small multilingual encoder should the dense half use?  (default + realworld sets only)

Embedding all 73k passages per candidate model costs ~30 min of CPU each, so this compares them
on a candidate pool instead: for every question, the union of BM25's top-N law passages and the
shipped e5-small's top-N (N=30), re-ranked by each model's cosine alone. Hit@8 / MRR are doc-level
(an expected law's title on one of the first 8 re-ranked passages; no per-document cap).
The pool is built from BM25 + e5-small, so it slightly favours e5-small; a rival that still wins
here is clearly better.

    python3 eval/dense_model_compare.py pool                       # writes $DENSE_COMPARE_DIR/dense-pool.json
    python3 eval/dense_model_compare.py run e5-small|e5-base|minilm|labse   # embeds the pool with one model
    python3 eval/dense_model_compare.py report                     # table over the finished models

Models are fetched from the Hugging Face hub (Xenova ONNX int8 exports) into a temp dir.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

CACHE = os.environ.get("DENSE_COMPARE_DIR", "/tmp/dense-compare")
POOL = os.path.join(CACHE, "dense-pool.json")
N = 30
MODELS = {
    # name: (repo, onnx file, query prefix, passage prefix)
    "e5-small": ("Xenova/multilingual-e5-small", "onnx/model_quantized.onnx", "query: ", "passage: "),
    "e5-base": ("Xenova/multilingual-e5-base", "onnx/model_quantized.onnx", "query: ", "passage: "),
    "minilm": ("Xenova/paraphrase-multilingual-MiniLM-L12-v2", "onnx/model_quantized.onnx", "", ""),
    "labse": ("Xenova/LaBSE", "onnx/model_quantized.onnx", "", ""),
}


def _fetch(repo, path, dest):
    if not os.path.exists(dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        urllib.request.urlretrieve(f"https://huggingface.co/{repo}/resolve/main/{path}", dest)
    return dest


def build_pool():
    import run_eval as R
    from app import dense, retrieval
    idx = retrieval.get_index()
    qs = []
    for name in ("default", "realworld"):
        qs += [{**q, "set": name} for q in R.load(R.set_path(name))]
    passages: dict[str, str] = {}
    rows = []
    for q in qs:
        bm = idx.search([q["q"]], top_k=N, category="law", per_doc_cap=N, mode="bm25")
        de = idx.search([q["q"]], top_k=N, category="law", per_doc_cap=N, mode="dense")
        cand = {h["id"]: h for h in bm + de}
        for pid, h in cand.items():
            passages[pid] = dense.passage_text(h)
        rows.append({"q": q["q"], "set": q["set"], "expect": q["expect"], "lang": q.get("lang"),
                     "cands": [{"id": pid, "doc": h.get("doc_title_ne") or ""} for pid, h in cand.items()]})
    os.makedirs(os.path.dirname(POOL), exist_ok=True)
    json.dump({"rows": rows, "passages": passages}, open(POOL, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(rows)} questions, {len(passages)} unique passages -> {POOL}")


def embed_pool(name: str, threads: int = 4):
    import onnxruntime as ort
    from tokenizers import Tokenizer
    repo, onnx_path, qp, pp = MODELS[name]
    model = _fetch(repo, onnx_path, f"{CACHE}/{name}/model.onnx")
    tok = Tokenizer.from_file(_fetch(repo, "tokenizer.json", f"{CACHE}/{name}/tokenizer.json"))
    tok.enable_truncation(256)
    so = ort.SessionOptions()
    so.intra_op_num_threads = threads
    sess = ort.InferenceSession(model, so, providers=["CPUExecutionProvider"])
    wanted = {i.name for i in sess.get_inputs()}

    def enc(texts, prefix, batch=16):
        seqs = [tok.encode(prefix + t) for t in texts]
        order = np.argsort([len(s.ids) for s in seqs])
        res = [None] * len(texts)
        for a in range(0, len(order), batch):
            ix = order[a:a + batch]
            w = max(len(seqs[i].ids) for i in ix)
            ids = np.full((len(ix), w), tok.token_to_id("<pad>") or 0, dtype=np.int64)
            mask = np.zeros((len(ix), w), dtype=np.int64)
            for r, i in enumerate(ix):
                ids[r, :len(seqs[i].ids)] = seqs[i].ids
                mask[r, :len(seqs[i].ids)] = 1
            feed = {"input_ids": ids, "attention_mask": mask}
            if "token_type_ids" in wanted:
                feed["token_type_ids"] = np.zeros_like(ids)
            h = sess.run(None, feed)[0]
            m = mask[:, :, None].astype(np.float32)
            v = (h * m).sum(1) / np.maximum(m.sum(1), 1)
            v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)
            for r, i in enumerate(ix):
                res[i] = v[r]
        return np.stack(res)

    pool = json.load(open(POOL, encoding="utf-8"))
    ids = list(pool["passages"])
    t = time.time()
    pv = enc([pool["passages"][i] for i in ids], pp)
    qv = enc([r["q"] for r in pool["rows"]], qp)
    print(f"{name}: {len(ids)} passages + {len(qv)} queries in {time.time() - t:.0f}s")
    np.savez(os.path.join(CACHE, f"dense-pool-{name}.npz"), ids=np.array(ids), pv=pv.astype(np.float16), qv=qv)


def report():
    pool = json.load(open(POOL, encoding="utf-8"))
    out = {}
    for name in MODELS:
        p = os.path.join(CACHE, f"dense-pool-{name}.npz")
        if not os.path.exists(p):
            continue
        z = np.load(p)
        pos = {pid: j for j, pid in enumerate(z["ids"].tolist())}
        pv, qv = z["pv"].astype(np.float32), z["qv"]
        for split in ("default", "realworld"):
            hits, mrr, n = 0, 0.0, 0
            for r, q in zip(pool["rows"], qv):
                if r["set"] != split:
                    continue
                cs = r["cands"]
                sc = [float(pv[pos[c["id"]]] @ q) for c in cs]
                order = sorted(range(len(cs)), key=lambda i: -sc[i])
                rank, k = None, 0
                for i in order:
                    k += 1
                    if any(x in cs[i]["doc"] for x in r["expect"]):
                        rank = k
                        break
                n += 1
                if rank and rank <= 8:
                    hits += 1
                mrr += 1 / rank if rank else 0
            out.setdefault(name, {})[split] = (round(hits / n, 3), round(mrr / n, 3), n)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "pool":
        build_pool()
    elif cmd == "run":
        embed_pool(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 4)
    else:
        report()
