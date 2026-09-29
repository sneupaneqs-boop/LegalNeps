"""Contract audit API: upload a contract -> cited legal audit.

    GET  /api/documents/checklists        public: every check we run and its citation
    POST /api/documents/audit             signed-in: multipart file -> audit JSON
    POST /api/documents/audit/report      signed-in: audit JSON -> DOCX report

The audit is stateless: the uploaded document is read in memory, audited and
dropped. It is stored only if the request carries a `matter_id` the caller
owns, and then through the same matter-file path as a manual upload.
"""
import asyncio
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from .. import llm, supa, tiers
from ..documents import audit as audit_engine
from ..documents import checklists, extract
from ..documents.models import AuditResult, ChecklistTypeOut, ReportRequest
from ..documents.report import render_report
from .chat import _require_matter, _require_user

router = APIRouter(prefix="/documents")
log = logging.getLogger("kanooni.documents")

MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # same cap as matter-file uploads


async def _read_capped(file: UploadFile) -> bytes:
    """Bounded chunked read (see routes/chat.py:upload_matter_file): an
    oversized upload is rejected as soon as it crosses the cap instead of
    being buffered whole first."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="file too large (20MB limit)")
        chunks.append(chunk)
    return b"".join(chunks)


def _error(status: int, code: str, message: str, message_ne: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"code": code, "message": message, "message_ne": message_ne})


@router.get("/checklists", response_model=list[ChecklistTypeOut])
async def list_checklists() -> list[ChecklistTypeOut]:
    """Public, for transparency: what each contract type is checked against
    and the corpus provision behind every check (plus what we chose NOT to
    enforce because its number could not be confirmed in the corpus)."""
    return await asyncio.to_thread(checklists.public_listing)


@router.post("/audit", response_model=AuditResult)
async def audit_document(
    file: UploadFile = File(...),
    contract_type: str | None = Form(None),
    language: str = Form("en"),
    matter_id: str | None = Form(None),
    user: dict = Depends(_require_user),
) -> AuditResult:
    """Signed-in only. Metered against the caller's plan-based daily quota
    exactly like AI-fill, and billed to Sonnet 5.5 (tiers.select_tier(plan,
    "draft")) on a paid plan with the real cost logged to llm_usage; the
    free plan uses the free provider chain."""
    if language not in ("en", "ne"):
        raise HTTPException(status_code=422, detail="language must be 'en' or 'ne'")
    valid_types = checklists.contract_types()
    if contract_type in ("", "auto"):
        contract_type = None
    if contract_type is not None and contract_type not in valid_types:
        raise HTTPException(status_code=422, detail=f"contract_type must be 'auto' or one of {valid_types}")
    if matter_id:
        await _require_matter(matter_id, user)  # 404 for a matter the caller doesn't own - before any work

    content = await _read_capped(file)

    # cheap, deterministic failures (wrong format, legacy font, scanned PDF)
    # come before the quota check so a rejected upload costs the user nothing
    try:
        doc = await asyncio.to_thread(extract.extract_text, file.filename or "", content)
    except extract.DocumentError as exc:
        raise _error(422, exc.code, exc.message_en, exc.message_ne)

    plan = await asyncio.to_thread(supa.profile_get_plan, user["id"])
    allowed, _ = await asyncio.to_thread(supa.check_and_increment_quota, user["id"], tiers.daily_quota_for(plan))
    if not allowed:
        raise HTTPException(status_code=429, detail="daily limit reached")
    tier = tiers.select_tier(plan, "draft")

    try:
        result, meta = await asyncio.to_thread(
            audit_engine.run_audit, doc.text, contract_type=contract_type, tier=tier, language=language,
            filename=file.filename,
        )
    except audit_engine.ContractTypeUnknown as exc:
        raise _error(422, "contract_type_unknown", str(exc),
                     "यो कुन प्रकारको सम्झौता हो पहिचान गर्न सकिएन - कृपया सम्झौताको प्रकार आफैँ छान्नुहोस्।")
    except audit_engine.UnsupportedContractType as exc:
        raise _error(422, "unsupported_contract_type", str(exc),
                     "यो प्रकारको सम्झौता अहिले परीक्षण गर्न मिल्दैन।")
    except audit_engine.ExtractionFailed as exc:
        raise _error(502, "extraction_failed", str(exc),
                     "एआई पाठकले प्रयोगयोग्य उत्तर दिन सकेन; कृपया फेरि प्रयास गर्नुहोस्।")
    except llm.LLMUnavailable:
        raise _error(503, "llm_unavailable", "The AI reader is temporarily unavailable, try again shortly.",
                     "एआई पाठक केही समयका लागि उपलब्ध छैन, केही बेरपछि फेरि प्रयास गर्नुहोस्।")

    if tier != "free":
        cost = tiers.estimate_cost_usd(tier, meta.input_tokens, meta.output_tokens)
        await asyncio.to_thread(
            supa.llm_usage_record, user["id"], "/api/documents/audit", tier, "anthropic",
            tiers.model_for_tier(tier), audit_engine.PROMPT_VERSION, meta.input_tokens, meta.output_tokens,
            cost, meta.flagged_injection,
        )

    out = AuditResult(**result)
    if matter_id:
        row = await asyncio.to_thread(
            supa.matter_file_create, user["id"], matter_id, file.filename or "contract", content,
            file.content_type or "application/octet-stream",
        )
        if row is not None:
            out.saved_to_matter = True
            out.saved_file_id = str(row.get("id")) if row.get("id") is not None else None
        else:
            log.warning("contract audit: matter %s could not store the file (supabase unavailable)", matter_id)
    return out


@router.post("/audit/report")
async def audit_report(payload: ReportRequest, user: dict = Depends(_require_user)) -> Response:
    """Render an audit (the JSON returned by /documents/audit) as a DOCX
    report. Signed-in; not metered - it makes no LLM call."""
    docx_bytes = await asyncio.to_thread(render_report, payload.audit.model_dump(), payload.language)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="contract-audit.docx"'},
    )
