"""Build the BM25 search index at deploy BUILD time, not on first request.

Render's free instance loses its disk on every wake, so without this the
index is rebuilt from the corpus shards on each cold start (~17s locally,
~45s on Render's CPU, 312MB peak RSS). Loading the prebuilt cache instead
takes ~0.7s and 168MB. Render build command:

    cd backend && pip install -r requirements.txt && python scripts/prebuild_index.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieval import get_index  # noqa: E402

t = time.time()
idx = get_index()
print(f"index ready: {len(idx)} passages, digest {idx.digest}, {time.time() - t:.1f}s")
