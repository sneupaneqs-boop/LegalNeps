"""
Corpus verification for eval cases (V1).

Each case in questions_realworld.jsonl / questions_heldout.jsonl carries
`sections`: the provisions that govern the question, with `contains` phrases
copied from the corpus text. `verify_case` looks each provision up through the
same index the app serves (`Index.section(doc_slug(title), section)`, or an
entry title for regulator directives whose section numbers repeat) and checks
that the phrases really occur and that the passage is not repealed/lapsed/a bill.

    python3 eval/run_eval.py verify --set realworld
"""
from __future__ import annotations

import re

from app.retrieval import doc_slug

_WS = re.compile(r"\s+")
_PUA = re.compile("[-]")  # footnote glyphs the PDF extraction leaves inside words
BAD_STATUS = {"repealed", "lapsed", "bill"}


def norm(text: str) -> str:
    return _WS.sub(" ", _PUA.sub("", text or "")).strip()


class DocResolver:
    """Resolve a case's `doc` (exact title or unambiguous prefix) to a title in the index."""

    def __init__(self, idx):
        self.idx = idx
        self.by_title: dict[str, list[dict]] = {}
        for e in idx.iter_entries():
            if e.get("category") == "law" and e.get("doc_title_ne"):
                self.by_title.setdefault(e["doc_title_ne"], []).append(e)

    def title(self, doc: str) -> str | None:
        if doc in self.by_title:
            return doc
        c = sorted((t for t in self.by_title if t.startswith(doc)), key=len)
        return c[0] if c else None


def verify_case(case: dict, idx, resolver: DocResolver | None = None) -> list[str]:
    """Return a list of problems ([] = every cited provision found and confirmed)."""
    resolver = resolver or DocResolver(idx)
    problems: list[str] = []
    if not case.get("sections"):
        return ["no sections to verify"]
    for s in case["sections"]:
        title = resolver.title(s["doc"])
        if not title:
            problems.append(f"doc not in corpus: {s['doc']}")
            continue
        candidates: list[dict] = []
        if s.get("section"):
            e = idx.section(doc_slug(title), s["section"])
            if e is None:
                problems.append(f"section not found: {title} s.{s['section']}")
                continue
            candidates = [e]
        elif s.get("title_contains"):
            candidates = [e for e in resolver.by_title[title] if s["title_contains"] in (e.get("title_ne") or "")]
            if not candidates:
                problems.append(f"no entry titled *{s['title_contains']}* in {title}")
                continue
        else:
            problems.append(f"{s['doc']}: need section or title_contains")
            continue
        ok = False
        for e in candidates:
            text = norm(e.get("text_ne"))
            status = e.get("status")
            if all(norm(p) in text for p in s.get("contains", [])) and status not in BAD_STATUS:
                ok = True
                break
        if not ok:
            where = s.get("section") or s.get("title_contains")
            problems.append(f"text check failed: {title} [{where}] missing {s.get('contains')} (or repealed/lapsed)")
    return problems
