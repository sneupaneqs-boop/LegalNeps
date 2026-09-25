import json
import re
from functools import lru_cache
from pathlib import Path
from typing import List, Literal

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = Path(__file__).parent / "data" / "corpus.json"

DEVANAGARI_RE = re.compile(r"[ऀ-ॿ]")


def detect_language(text: str) -> Literal["en", "ne"]:
    return "ne" if DEVANAGARI_RE.search(text) else "en"


@lru_cache(maxsize=1)
def load_corpus() -> List[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _vectorizer_bundle(lang: str):
    corpus = load_corpus()
    field = "text_en" if lang == "en" else "text_ne"
    texts = [entry[field] for entry in corpus]
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix, corpus


def retrieve(query: str, lang: Literal["en", "ne"], top_k: int = 4) -> List[dict]:
    vectorizer, matrix, corpus = _vectorizer_bundle(lang)
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, matrix)[0]
    ranked = sorted(range(len(corpus)), key=lambda i: scores[i], reverse=True)

    results = []
    for i in ranked[:top_k]:
        if scores[i] <= 0:
            continue
        entry = corpus[i]
        results.append({**entry, "score": float(scores[i])})

    # Fall back to the top results even if none matched keywords, so the
    # assistant always has some grounding context to reason over.
    if not results:
        for i in ranked[:top_k]:
            entry = corpus[i]
            results.append({**entry, "score": float(scores[i])})

    return results
