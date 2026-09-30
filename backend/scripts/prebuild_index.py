"""Build the BM25 index and fetch/warm the dense query encoder at deploy BUILD time.

Render's free instance loses its disk on every wake, so without this the
index is rebuilt from the corpus shards on each cold start (~17s locally,
~45s on Render's CPU, 312MB peak RSS). Loading the prebuilt cache instead
takes ~0.7s and 168MB. Render build command:

    cd backend && pip install -r requirements.txt && python scripts/prebuild_index.py

Hybrid retrieval (app/dense.py): this also downloads the multilingual-e5-small int8
ONNX encoder (~118MB) + its sentencepiece model, prunes the embedding table to the
Devanagari/ASCII vocabulary (~54MB), and loads it once as a smoke test. The corpus
vectors themselves are the committed file app/data/dense/vectors.npz. A failure in the
dense part never fails the build: the service then runs BM25-only (and logs why).
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import dense  # noqa: E402
from app.retrieval import get_index  # noqa: E402

if dense.enabled():
    t = time.time()
    try:
        dense.prepare_model()
        print(f"dense encoder ready in {dense.MODEL_DIR} ({time.time() - t:.1f}s)")
    except Exception as e:  # noqa: BLE001 - offline build etc.: BM25-only is a valid deployment
        print(f"WARNING: dense encoder not prepared, service will be BM25-only: {e}")

t = time.time()
idx = get_index()
print(f"index ready: {len(idx)} passages, digest {idx.digest}, {time.time() - t:.1f}s")
if dense.enabled():
    d = dense.warm_up(idx)
    if d is None:
        print("WARNING: dense retrieval unavailable (no vectors or model) - BM25 only")
    else:
        i = d.store.info
        print(f"dense ready: {int(d.store.have.sum())}/{len(idx)} passages have vectors "
              f"({'exact' if i.get('exact') else str(i.get('missing')) + ' missing, digest ' + str(i.get('digest'))})")
