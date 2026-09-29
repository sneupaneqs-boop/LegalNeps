"""Loads and validates the contract checklists in data/contract_checklists/*.yaml.

Same idea as playbooks.py: curated YAML, every cited provision resolved
against the live corpus through playbooks.resolve_provision(), so an audit can
never show a citation the corpus doesn't have. A check whose number could not
be confirmed in the cited section's corpus text is marked `verified: false`
in the YAML and is never run or shown as a finding (see `excluded_checks`).

YAML shape (see the five files for real examples):

    id: employment
    title: {en, ne}
    keywords: [...]                    # contract-type classification
    facts:                             # what the LLM must extract
      probation_months: {type: number, description: "..."}
    checks:
      - id: probation_max
        title: {en, ne}
        extract: [probation_months]    # facts this check needs
        when: {...}                    # optional guard (rule DSL)
        rule: {field: probation_months, max: 6}    # rules.py DSL
        if_missing: ok | missing | skip            # fact not found (default missing)
        severity: issue | warning | info
        basis: statutory | best_practice
        recommendation: {en, ne}
        provision: {law_title_ne, section}
        verify: ["छ महिना"]            # substrings the corpus text must contain
        verified: true
"""
from __future__ import annotations

import copy
import logging
from functools import lru_cache
from pathlib import Path

import yaml

from ..playbooks import UnresolvedProvision, resolve_provision
from ..retrieval import get_index
from . import rules

log = logging.getLogger(__name__)

CHECKLIST_DIR = Path(__file__).resolve().parent.parent / "data" / "contract_checklists"
CONTRACT_TYPES = ("employment", "rent_lease", "service_agreement", "nda", "sale_or_loan")
SEVERITIES = ("issue", "warning", "info")
BASES = ("statutory", "best_practice")
IF_MISSING = ("ok", "missing", "skip")
FACT_TYPES = ("boolean", "number", "string")


class ChecklistError(ValueError):
    """A checklist YAML is malformed (caught by the test-suite, not at request time)."""


def _bilingual(obj, where: str) -> None:
    if not isinstance(obj, dict) or not (obj.get("en") or "").strip() or not (obj.get("ne") or "").strip():
        raise ChecklistError(f"{where}: needs non-empty en and ne text")


def _validate(data: dict, path: str) -> None:
    if data.get("id") not in CONTRACT_TYPES:
        raise ChecklistError(f"{path}: id {data.get('id')!r} is not one of {CONTRACT_TYPES}")
    _bilingual(data.get("title"), f"{path} title")
    if not data.get("keywords"):
        raise ChecklistError(f"{path}: needs classification keywords")
    facts = data.get("facts") or {}
    for name, spec in facts.items():
        if spec.get("type") not in FACT_TYPES or not spec.get("description"):
            raise ChecklistError(f"{path}: fact {name!r} needs a type in {FACT_TYPES} and a description")
    seen: set[str] = set()
    for chk in data.get("checks") or []:
        cid = chk.get("id")
        where = f"{path} check {cid!r}"
        if not cid or cid in seen:
            raise ChecklistError(f"{where}: missing or duplicate id")
        seen.add(cid)
        _bilingual(chk.get("title"), f"{where} title")
        if chk.get("severity") not in SEVERITIES:
            raise ChecklistError(f"{where}: severity must be one of {SEVERITIES}")
        if chk.get("basis") not in BASES:
            raise ChecklistError(f"{where}: basis must be one of {BASES}")
        prov = chk.get("provision") or {}
        if not prov.get("law_title_ne") or not prov.get("section"):
            raise ChecklistError(f"{where}: needs provision {{law_title_ne, section}}")
        if not isinstance(chk.get("verified"), bool):
            raise ChecklistError(f"{where}: verified must be true or false")
        if not chk["verified"]:
            if not chk.get("unverified_reason"):
                raise ChecklistError(f"{where}: an unverified check must say why (unverified_reason)")
            continue
        _bilingual(chk.get("recommendation"), f"{where} recommendation")
        if chk.get("if_missing", "missing") not in IF_MISSING:
            raise ChecklistError(f"{where}: if_missing must be one of {IF_MISSING}")
        if not chk.get("verify"):
            raise ChecklistError(f"{where}: a verified check needs `verify` substrings from the corpus text")
        try:
            rules.validate(chk.get("rule"), set(facts))
            if chk.get("when"):
                rules.validate(chk["when"], set(facts))
        except rules.RuleError as exc:
            raise ChecklistError(f"{where}: {exc}") from exc
        needed = rules.fields_in(chk["rule"]) | rules.fields_in(chk.get("when") or {})
        missing = needed - set(chk.get("extract") or [])
        if missing:
            raise ChecklistError(f"{where}: rule reads {sorted(missing)} but `extract` doesn't list them")


@lru_cache(maxsize=1)
def _load_all() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in sorted(CHECKLIST_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        _validate(data, path.name)
        if path.stem != data["id"]:
            raise ChecklistError(f"{path.name}: file name must match id {data['id']!r}")
        out[data["id"]] = data
    return out


def contract_types() -> list[str]:
    return [t for t in CONTRACT_TYPES if t in _load_all()]


def get_raw(contract_type: str) -> dict | None:
    return _load_all().get(contract_type)


def _resolve(ref: dict) -> dict:
    p = resolve_provision({"law_title_ne": ref["law_title_ne"], "section": ref["section"]})
    entry = get_index().section(p["slug"], p["section"]) or {}
    out = {k: p[k] for k in ("law_title_ne", "section", "slug", "citation", "url", "status")}
    out["citation_en"] = entry.get("source_en") or p["citation"]
    return out


@lru_cache(maxsize=None)
def _resolved_cached(contract_type: str) -> dict | None:
    raw = _load_all().get(contract_type)
    if raw is None:
        return None
    data = copy.deepcopy(raw)
    active, excluded = [], []
    for chk in data["checks"]:
        if not chk["verified"]:
            excluded.append({"id": chk["id"], "title": chk["title"], "reason": chk["unverified_reason"],
                              "provision": chk["provision"]})
            continue
        try:
            chk["provision_resolved"] = _resolve(chk["provision"])
        except UnresolvedProvision as exc:
            # A corpus change dropped a cited section: never show a citation
            # the corpus can't back. tests/test_documents_audit.py fails hard
            # on this; at request time we degrade by dropping the check.
            log.error("contract checklist %s/%s: %s - check disabled", contract_type, chk["id"], exc)
            excluded.append({"id": chk["id"], "title": chk["title"], "reason": f"citation unresolved: {exc}",
                              "provision": chk["provision"]})
            continue
        chk.setdefault("if_missing", "missing")
        active.append(chk)
    data["checks"] = active
    data["excluded_checks"] = excluded
    return data


def get_checklist(contract_type: str) -> dict | None:
    """The type's checklist with only verified checks, each carrying
    `provision_resolved`, plus `excluded_checks` (unverified / unresolved).
    Returns a deep copy - callers may mutate it."""
    data = _resolved_cached(contract_type)
    return copy.deepcopy(data) if data else None


def assert_integrity() -> None:
    """Raise UnresolvedProvision for any cited provision (verified or not)
    the corpus lacks. Used by the citation-integrity test."""
    for raw in _load_all().values():
        for chk in raw["checks"]:
            _resolve(chk["provision"])


def public_listing() -> list[dict]:
    """GET /api/documents/checklists: what we check and why, for transparency."""
    out = []
    for ctype in contract_types():
        cl = _resolved_cached(ctype)
        out.append({
            "contract_type": ctype,
            "title": cl["title"],
            "checks": [
                {
                    "id": c["id"], "title": c["title"], "severity": c["severity"], "basis": c["basis"],
                    "recommendation": c["recommendation"], "provision": c["provision_resolved"],
                    "extract": c["extract"],
                }
                for c in cl["checks"]
            ],
            "not_enforced": cl["excluded_checks"],
        })
    return out
