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
"""
from __future__ import annotations

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


def _resolve_provision(ref: dict) -> dict:
    """A cited provision, enriched with the corpus's own citation text/url/
    slug - or raises UnresolvedProvision if it doesn't exist. This is what
    both the API (so the UI always shows live corpus text) and the
    citation-integrity test rely on."""
    title = ref["law_title_ne"]
    section = ref.get("section")
    slug = doc_slug(title)
    idx = get_index()
    entry = idx.section(slug, section) if section else None
    if entry is None:
        doc = idx.doc(slug, include_bills=True)
        if doc is None or (section and not any(s["section"] == section for s in doc["sections"])):
            raise UnresolvedProvision(f"{title!r} दफा {section!r} not found in corpus (slug={slug})")
        entry = doc  # section-less reference (e.g. a whole short act)
    return {
        "law_title_ne": title,
        "section": section,
        "slug": slug,
        "citation": entry.get("source_ne") or entry.get("doc_title_ne") or title,
        "url": entry.get("url"),
        "status": entry.get("status"),
        "note": ref.get("note") or {},
    }


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
    for data in _load_yaml_files():
        if data["id"] == playbook_id:
            return _resolve_playbook(data)
    return None


def all_playbooks_resolved() -> list[dict]:
    """Every playbook with every provision resolved - raises
    UnresolvedProvision on the first bad citation. Used by the citation
    integrity test and can be run standalone as a corpus-drift check."""
    return [_resolve_playbook(data) for data in _load_yaml_files()]
