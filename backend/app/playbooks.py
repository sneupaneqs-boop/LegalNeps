"""Action Plan engine (S6): loads YAML playbooks (issue -> fact questions ->
cited provisions -> evidence -> forum -> limitation period -> next steps ->
optional draft-template link) and resolves every provision reference
against the live corpus, so a playbook can never show a citation the corpus
doesn't actually have.

Playbook YAML shape (see app/data/playbooks/*.yaml for real examples):

    id: unpaid_salary
    area: employment
    issue: {en: "...", ne: "..."}
    fact_questions: [{en: "...", ne: "..."}, ...]
    provisions:
      - law_title_ne: "श्रम ऐन, २०७४"   # must match a doc_title_ne in the corpus
        section: "34"                  # must match that doc's section field
        note: {en: "...", ne: "..."}   # why this provision matters here
    evidence: [{en: "...", ne: "..."}, ...]
    forum: {en: "...", ne: "..."}
    limitation:
      note: {en: "...", ne: "..."}
      provision: {law_title_ne: "...", section: "..."}  # optional, cited limitation clause
    next_steps: [{en: "...", ne: "..."}, ...]
    template_link: null   # S9 adds real drafting-template ids here

Optional keys (V2.5):
    not_keywords: ["bank", "बैंक"]   # phrases that veto this plan for a message (a different situation)
    exclude_provisions: [{law_title_ne, section}]   # sections retrieval must not surface for this plan
A provision of a regulator directive (whose clause numbers repeat) is referenced by heading and text instead
of a section number:
      - law_title_ne: "<exact directive document title>"
        entry_title_contains: "१५/०८२ - कर्जाको ब्याजदर"   # phrase of the entry's heading
        contains: ["पेनाल ब्याजदर"]                          # phrase(s) that must occur in its text
"""
from __future__ import annotations

import copy
import re
from functools import lru_cache
from pathlib import Path

import yaml

from .retrieval import doc_slug, get_index

PLAYBOOKS_DIR = Path(__file__).parent / "data" / "playbooks"


class UnresolvedProvision(ValueError):
    """A playbook cites a law_title_ne/section that isn't in the corpus."""


def _load_yaml_files() -> list[dict]:
    out = []
    for path in sorted(PLAYBOOKS_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["_file"] = path.name
        out.append(data)
    return out


_WS = re.compile(r"\s+")
_PUA = re.compile("[-]")  # footnote glyphs the PDF extraction leaves inside words


def _norm(text: str) -> str:
    return _WS.sub(" ", _PUA.sub("", text or "")).strip()


def lookup_entry(idx, ref: dict) -> dict | None:
    """The corpus entry a provision reference points at, or None.

    Statutes: `section` (the entry's section label). Regulator directives repeat
    their clause numbers (every IPD directive has a clause "3"), so a reference
    may instead give `entry_title_contains` (a phrase of the entry's heading)
    and/or `contains` (phrases that must occur in its text); the first matching
    entry of the document is used."""
    slug = doc_slug(ref["law_title_ne"])
    if ref.get("entry_title_contains") or ref.get("contains"):
        want_title = ref.get("entry_title_contains")
        needles = [_norm(c) for c in ref.get("contains") or []]
        for i in idx._doc_index.get(slug) or []:
            e = idx.get(i)
            if want_title and want_title not in (e.get("title_ne") or ""):
                continue
            text = _norm(e.get("text_ne"))
            if all(n in text for n in needles):
                return {**e, "slug": slug, "status": e.get("status") or idx.status[i]}
        return None
    section = ref.get("section")
    return idx.section(slug, section) if section else None


def _resolve_provision(ref: dict) -> dict:
    """A cited provision, enriched with the corpus's own citation text/url/
    slug - or raises UnresolvedProvision if it doesn't exist. This is what
    both the API (so the UI always shows live corpus text) and the
    citation-integrity test rely on."""
    title = ref["law_title_ne"]
    section = ref.get("section")
    slug = doc_slug(title)
    idx = get_index()
    by_text = bool(ref.get("entry_title_contains") or ref.get("contains"))
    entry = lookup_entry(idx, ref)
    if by_text:
        if entry is None:
            raise UnresolvedProvision(f"{title!r} entry {ref.get('entry_title_contains')!r} / "
                                      f"{ref.get('contains')!r} not found in corpus (slug={slug})")
        section = entry.get("section")
    elif entry is None:
        doc = idx.doc(slug, include_bills=True)
        if doc is None or (section and not any(s["section"] == section for s in doc["sections"])):
            raise UnresolvedProvision(f"{title!r} दफा {section!r} not found in corpus (slug={slug})")
        entry = doc  # section-less reference (e.g. a whole short act)
    out = {
        "law_title_ne": title,
        "section": section,
        "slug": slug,
        "citation": entry.get("source_ne") or entry.get("doc_title_ne") or title,
        "url": entry.get("url"),
        "status": entry.get("status"),
        "note": ref.get("note") or {},
    }
    if by_text:  # kept so pinned_provisions() can fetch this exact entry again
        out["entry_title_contains"] = ref.get("entry_title_contains")
        out["contains"] = list(ref.get("contains") or [])
    return out


def _resolve_playbook(data: dict) -> dict:
    resolved = dict(data)
    resolved["provisions"] = [_resolve_provision(p) for p in data.get("provisions", [])]
    if data.get("limitation", {}).get("provision"):
        resolved["limitation"] = {**data["limitation"],
                                  "provision": _resolve_provision(data["limitation"]["provision"])}
    return resolved


def list_playbooks() -> list[dict]:
    """Summary list (no provision resolution - cheap, for GET /api/playbooks)."""
    return [{"id": p["id"], "area": p.get("area"), "issue": p["issue"]} for p in _load_yaml_files()]


def get_playbook(playbook_id: str) -> dict | None:
    # Cached: chat calls this on every playbook-matched question, and
    # re-parsing all 25 YAML files each time cost ~100ms. Playbooks are
    # static files and the index is loaded once per process.
    return copy.deepcopy(_get_playbook_cached(playbook_id))


@lru_cache(maxsize=64)
def _get_playbook_cached(playbook_id: str) -> dict | None:
    for data in _load_yaml_files():
        if data["id"] == playbook_id:
            return _resolve_playbook(data)
    return None


def resolve_provision(ref: dict) -> dict:
    """Public entry point for callers outside a playbook (S8's calculators)
    that need to cite a single corpus provision without going through a
    whole playbook - same UnresolvedProvision guarantee as playbook YAML."""
    return _resolve_provision(ref)


def all_playbooks_resolved() -> list[dict]:
    """Every playbook with every provision resolved - raises
    UnresolvedProvision on the first bad citation. Used by the citation
    integrity test and can be run standalone as a corpus-drift check."""
    return [_resolve_playbook(data) for data in _load_yaml_files()]
