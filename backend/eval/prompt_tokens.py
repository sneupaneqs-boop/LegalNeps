"""Size of the structured-answer request (V3.2 token diet): system prompt + user prompt (sources) + the
max_tokens asked for, over the 30 real-world questions of the V3 live review, retrieved offline (BM25, no query
rewrite) exactly like the live path.

    python eval/prompt_tokens.py [--tokenizer PATH/tokenizer.json] [--out eval/reports/prompt-tokens-<label>.json]
                                 [--label before|after]

Tokens are counted with a real subword tokenizer when --tokenizer (a HuggingFace tokenizer.json, e.g. the
multilingual-e5 one used by the dense retriever) is given - an XLM-R style vocabulary, so a PROXY for the
Groq/Gemini tokenizers (their Devanagari counts differ, typically higher) - else with a documented estimate:
Devanagari chars / 1.6 + other chars / 4. Compare runs of the same tokenizer only. The point is the ratio
between before and after, and that the request stays well under the free-tier per-minute limits.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from app import config, generation  # noqa: E402
from app.retrieval import get_index  # noqa: E402

REPORTS = HERE / "reports"
_DEV = re.compile(r"[ऀ-ॿ]")


def make_counter(path: str | None):
    if path:
        from tokenizers import Tokenizer
        tk = Tokenizer.from_file(path)
        return lambda text: len(tk.encode(text).ids), f"tokenizers:{Path(path).parent.name}"
    return (lambda text: round(len(_DEV.findall(text)) / 1.6 + (len(text) - len(_DEV.findall(text))) / 4)), "estimate"


def request_parts(question: str):
    """(system, user prompt, max_tokens, sources sent, sources retrieved, lang) as the live pipeline builds them."""
    lang = generation.guess_language(question)
    analysis = generation.analyze_query(question, lang)  # no LLM offline: the base analysis
    lang = analysis.get("reply_language") or lang
    playbook = generation._match_playbook(question, analysis)
    sources = generation.search(analysis.get("question") or question, analysis, playbook=playbook)
    system = generation.answer_system(lang) if hasattr(generation, "answer_system") else generation.ANSWER_SYSTEM
    prompt = generation._prompt(question, analysis, sources, lang, None, playbook)
    if hasattr(generation, "answer_max_tokens"):
        shown = len(generation.prompt_source_numbers(sources, playbook)) if hasattr(generation, "prompt_source_numbers") else len(sources)
        max_tokens = generation.answer_max_tokens(lang, shown)
    else:
        max_tokens = config.ANSWER_MAX_TOKENS_NE if lang == "ne" else config.ANSWER_MAX_TOKENS_EN
    sent = len(re.findall(r"^\[\d+\] \(", prompt, re.M))
    return system, prompt, max_tokens, sent, len(sources), lang, playbook


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer")
    ap.add_argument("--label", default="run")
    ap.add_argument("--out")
    ap.add_argument("--reviewed", default=str(REPORTS / "answer-review-v3-realworld-20260930.json"))
    args = ap.parse_args()
    count, how = make_counter(args.tokenizer)
    get_index()
    questions = [a["question"] for a in json.load(open(args.reviewed, encoding="utf8"))["answers"]]
    rows = []
    for q in questions:
        system, prompt, max_tokens, sent, retrieved, lang, playbook = request_parts(q)
        s_tok, p_tok = count(system), count(prompt)
        rows.append({"question": q, "lang": lang, "playbook": playbook and playbook["id"], "sources_retrieved": retrieved,
                     "sources_sent": sent, "system_chars": len(system), "system_tokens": s_tok,
                     "prompt_chars": len(prompt), "prompt_tokens": p_tok, "input_tokens": s_tok + p_tok,
                     "max_tokens": max_tokens, "request_budget_tokens": s_tok + p_tok + max_tokens})
    def col(k, sel=lambda r: True):
        v = [r[k] for r in rows if sel(r)]
        return {"n": len(v), "mean": round(statistics.mean(v)) if v else 0, "max": max(v) if v else 0}
    summary = {"counted_with": how, "label": args.label, "n": len(rows)}
    for k in ("system_tokens", "prompt_tokens", "input_tokens", "max_tokens", "request_budget_tokens", "sources_sent"):
        summary[k] = {"all": col(k), "ne": col(k, lambda r: r["lang"] == "ne"), "en": col(k, lambda r: r["lang"] == "en")}
    out = {"summary": summary, "rows": rows}
    path = Path(args.out) if args.out else REPORTS / f"prompt-tokens-{args.label}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("wrote", path)


if __name__ == "__main__":
    main()
