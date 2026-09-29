"""Pydantic models for the contract-audit API. Kept beside the feature (not in
app/schemas.py) so this work doesn't collide with other sessions' schema edits."""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

Status = Literal["ok", "issue", "warning", "missing", "info"]
Severity = Literal["issue", "warning", "info"]
Basis = Literal["statutory", "best_practice"]


class Bilingual(BaseModel):
    en: str = Field("", max_length=2000)
    ne: str = Field("", max_length=2000)


class ProvisionOut(BaseModel):
    law_title_ne: str = Field(..., max_length=300)
    section: str = Field(..., max_length=40)
    slug: str = Field(..., max_length=80)
    citation: str = Field("", max_length=400)
    citation_en: str = Field("", max_length=400)
    url: Optional[str] = Field(None, max_length=1200)
    status: Optional[str] = Field(None, max_length=40)


class FindingOut(BaseModel):
    check_id: str = Field(..., max_length=80)
    status: Status
    severity: Severity
    basis: Basis
    title: Bilingual
    recommendation: Bilingual
    clause_id: Optional[str] = Field(None, max_length=40)
    clause_label: Optional[str] = Field(None, max_length=80)
    quote: Optional[str] = Field(None, max_length=600)
    facts: dict[str, Any] = Field(default_factory=dict)
    not_stated: bool = False
    provision: ProvisionOut


class ExtractedFactOut(BaseModel):
    name: str = Field(..., max_length=80)
    value: Any = None
    clause_id: Optional[str] = Field(None, max_length=40)


class AuditResult(BaseModel):
    contract_type: str = Field(..., max_length=40)
    contract_type_title: Bilingual
    detected_by: Literal["user", "keywords", "llm"]
    language: Literal["en", "ne"] = "en"
    document_language: str = Field("en", max_length=8)
    filename: Optional[str] = Field(None, max_length=300)
    clause_count: int = 0
    truncated: bool = False
    summary: dict[str, int] = Field(default_factory=dict)
    checks_run: int = 0
    checks_not_applicable: int = 0
    findings: list[FindingOut] = Field(default_factory=list, max_length=200)
    extracted_facts: list[ExtractedFactOut] = Field(default_factory=list, max_length=200)
    disclaimer: Bilingual
    prompt_version: str = Field("", max_length=60)
    # set only when the caller passed a matter_id they own and the file was saved
    saved_file_id: Optional[str] = Field(None, max_length=80)
    saved_to_matter: bool = False


class ReportRequest(BaseModel):
    audit: AuditResult
    language: Literal["en", "ne"] = "en"


class ChecklistCheckOut(BaseModel):
    id: str
    title: Bilingual
    severity: Severity
    basis: Basis
    recommendation: Bilingual
    provision: ProvisionOut
    extract: list[str]


class NotEnforcedOut(BaseModel):
    id: str
    title: Bilingual
    reason: str


class ChecklistTypeOut(BaseModel):
    contract_type: str
    title: Bilingual
    checks: list[ChecklistCheckOut]
    not_enforced: list[NotEnforcedOut]
