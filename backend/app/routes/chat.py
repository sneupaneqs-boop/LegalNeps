import asyncio
import datetime
import json
import logging
import time

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import Response, StreamingResponse
from starlette.concurrency import iterate_in_threadpool

from .. import llm, playbooks, supa
from ..calculators import court_fee as court_fee_calc
from ..calculators import dates as date_calc
from ..calculators import labour as labour_calc
from ..calculators import limitation as limitation_calc
from ..drafting import ai_fill as drafting_ai_fill
from ..drafting import render as drafting_render
from ..generation import answer_question, stream_answer
from ..playbook_matcher import match as match_playbook
from ..retrieval import corpus_stats, doc_slug, get_index
from ..schemas import (AiFillRequest, AiFillResponse, BsDate, ChatRequest, ChatResponse, CourtFeeAppealResponse,
                        CourtFeeEstimateResponse, DateConversionResponse, DraftingTemplateDetail,
                        DraftingTemplateSummary, DraftRequest, DraftVersionOut, GratuityResponse, LawDoc,
                        LawSection, LimitationCheckResponse, NoticeResponse, Playbook, PlaybookMatchResponse,
                        PlaybookSummary, SavedDraftIn, SavedDraftOut, SavedResearchIn, SavedResearchOut,
                        SearchResponse, SeveranceResponse, Source)

router = APIRouter()
reqlog = logging.getLogger("kanooni.request")


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _current_user(authorization: str | None = Header(None)) -> dict | None:
    """None for an anonymous caller - most endpoints work without an account.
    Only /api/research requires one (see require_user)."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization[7:].strip()
    return await asyncio.to_thread(supa.get_user, token)


async def _require_user(authorization: str | None = Header(None)) -> dict:
    user = await _current_user(authorization)
    if user is None:
        raise HTTPException(status_code=401, detail="sign in required")
    return user


async def _enforce_limits(request: Request, user: dict | None) -> None:
    ip = _client_ip(request)
    if not await asyncio.to_thread(supa.check_ip_rate_limit, ip):
        raise HTTPException(status_code=429, detail="too many requests from this address, try again later")
    if user is not None:
        allowed, _ = await asyncio.to_thread(supa.check_and_increment_quota, user["id"])
        if not allowed:
            raise HTTPException(status_code=429, detail="daily answer limit reached")


def _log_request(endpoint: str, started: float, *, llm_used: bool, cached: bool, llm_calls: int,
                 language: str | None) -> None:
    # One structured line per request: what it cost (llm_calls, latency) and
    # whether it hit no provider at all (cache) or several (retries/fallback).
    reqlog.info(json.dumps({
        "endpoint": endpoint,
        "llm_calls": llm_calls,
        "tier": "free",  # only tier that exists until S13's paid AI gateway
        "latency_ms": int((time.time() - started) * 1000),
        "cache_hit": cached,
        "llm_used": llm_used,
        "language": language,
    }, ensure_ascii=False))


def _to_source(n: int, hit: dict, lang: str) -> Source:
    en = lang == "en"
    title = (hit.get("title_en") if en and hit.get("title_en") else hit.get("title_ne")) or hit.get("title_en") or ""
    citation = (hit.get("source_en") if en and hit.get("source_en") else hit.get("source_ne")) or ""
    text = (hit.get("text_en") if en and hit.get("text_en") else hit.get("text_ne")) or hit.get("text_en") or ""
    category = hit.get("category", "law")
    doc_title = hit.get("doc_title_ne") or hit.get("title_ne") or ""
    return Source(
        n=n, id=hit["id"], category=category, doc_type=hit.get("doc_type"),
        topic=hit.get("topic") or "", title=title, citation=citation,
        snippet=" ".join(text.split())[:280], score=round(float(hit.get("score", 0.0)), 4),
        url=hit.get("url"),
        slug=doc_slug(doc_title) if category == "law" and doc_title else None,
        section=hit.get("section"), status=hit.get("status"),
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request, authorization: str | None = Header(None)) -> ChatResponse:
    # LLM + search calls are blocking; keep the event loop free for other requests.
    user = await _current_user(authorization)
    await _enforce_limits(request, user)
    started = time.time()
    history = [t.model_dump() for t in payload.history]
    result = await asyncio.to_thread(answer_question, payload.message, payload.language or "auto", history)
    lang = result["language"]
    _log_request("/api/chat", started, llm_used=result["llm_used"], cached=result.get("cached", False),
                 llm_calls=result.get("llm_calls", 0), language=lang)
    return ChatResponse(
        answer=result["answer"],
        language=lang,
        sources=[_to_source(i, h, lang) for i, h in enumerate(result["sources"], 1)],
        llm_used=result["llm_used"],
        analysis=result.get("analysis"),
        cached=result.get("cached", False),
    )


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest, request: Request,
                      authorization: str | None = Header(None)) -> StreamingResponse:
    """NDJSON stream: {"type":"meta", sources...} then {"type":"delta","text"}* then {"type":"done"}.
    Sources arrive before the model starts writing, so the UI can show them immediately."""
    user = await _current_user(authorization)
    await _enforce_limits(request, user)
    started = time.time()
    history = [t.model_dump() for t in payload.history]

    def events():
        lang = "en"
        try:
            for kind, data in stream_answer(payload.message, payload.language or "auto", history):
                if kind == "meta":
                    lang = data["language"]
                    data = {**data, "sources": [_to_source(i, h, lang).model_dump()
                                                for i, h in enumerate(data["sources"], 1)]}
                    yield json.dumps({"type": "meta", **data}, ensure_ascii=False) + "\n"
                elif kind == "delta":
                    yield json.dumps({"type": "delta", "text": data}, ensure_ascii=False) + "\n"
                else:
                    _log_request("/api/chat/stream", started, llm_used=data.get("llm_used", False),
                                 cached=data.get("cached", False), llm_calls=data.get("llm_calls", 0),
                                 language=lang)
                    yield json.dumps({"type": "done", **data}, ensure_ascii=False) + "\n"
        except Exception:  # noqa: BLE001 - never leave the client hanging
            yield json.dumps({"type": "error"}) + "\n"

    return StreamingResponse(iterate_in_threadpool(events()), media_type="application/x-ndjson",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, max_length=500),
    category: str | None = Query(None, pattern="^(law|precedent)$"),
    doc_type: str | None = Query(None, max_length=40),
    status: str | None = Query(None, pattern="^(in_force|bill|unknown)$"),
    k: int = Query(10, ge=1, le=50),
    lang: str = Query("ne", pattern="^(en|ne)$"),
) -> SearchResponse:
    hits = await asyncio.to_thread(
        lambda: get_index().search([q], top_k=k, category=category, doc_type=doc_type, status=status)
    )
    return SearchResponse(query=q, results=[_to_source(i, h, lang) for i, h in enumerate(hits, 1)])


@router.get("/law/{slug}", response_model=LawDoc)
async def law_doc(slug: str) -> LawDoc:
    d = await asyncio.to_thread(get_index().doc, slug, include_bills=True)
    if d is None:
        raise HTTPException(status_code=404, detail="document not found")
    return LawDoc(**d)


@router.get("/law/{slug}/{section}", response_model=LawSection)
async def law_section(slug: str, section: str) -> LawSection:
    s = await asyncio.to_thread(get_index().section, slug, section)
    if s is None:
        raise HTTPException(status_code=404, detail="section not found")
    return LawSection(**s)


@router.get("/stats")
async def stats() -> dict:
    return await asyncio.to_thread(corpus_stats)


@router.post("/research", response_model=SavedResearchOut, status_code=201)
async def save_research(payload: SavedResearchIn, user: dict = Depends(_require_user)) -> SavedResearchOut:
    row = await asyncio.to_thread(
        supa.saved_research_create, user["id"], payload.question, payload.answer.model_dump(), payload.language
    )
    if row is None:
        raise HTTPException(status_code=503, detail="saved research is unavailable right now")
    return SavedResearchOut(**row)


@router.get("/research", response_model=list[SavedResearchOut])
async def list_research(user: dict = Depends(_require_user)) -> list[SavedResearchOut]:
    rows = await asyncio.to_thread(supa.saved_research_list, user["id"])
    return [SavedResearchOut(**r) for r in rows]


@router.delete("/research/{research_id}", status_code=204)
async def delete_research(research_id: str, user: dict = Depends(_require_user)) -> None:
    await asyncio.to_thread(supa.saved_research_delete, user["id"], research_id)


@router.get("/playbooks", response_model=list[PlaybookSummary])
async def list_playbooks() -> list[PlaybookSummary]:
    rows = await asyncio.to_thread(playbooks.list_playbooks)
    return [PlaybookSummary(**r) for r in rows]


@router.get("/playbooks/match", response_model=PlaybookMatchResponse)
async def match_playbooks(q: str = Query(..., min_length=1)) -> PlaybookMatchResponse:
    """Non-LLM keyword+glossary routing (S7): a confident hit lets the UI
    jump straight to an Action Plan without any LLM call; None means fall
    back to the normal chat/search flow."""
    playbook_id = await asyncio.to_thread(match_playbook, q)
    return PlaybookMatchResponse(playbook_id=playbook_id)


@router.get("/playbooks/{playbook_id}", response_model=Playbook)
async def get_playbook(playbook_id: str) -> Playbook:
    pb = await asyncio.to_thread(playbooks.get_playbook, playbook_id)
    if pb is None:
        raise HTTPException(status_code=404, detail="playbook not found")
    return Playbook(**{k: v for k, v in pb.items() if k != "_file"})


# --------------------------------------------------------------- S8: calculators ---

def _bad_input(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@router.get("/calculators/date/bs-to-ad", response_model=DateConversionResponse)
async def bs_to_ad(year: int, month: int, day: int) -> DateConversionResponse:
    try:
        ad = await asyncio.to_thread(date_calc.bs_to_ad, year, month, day)
    except date_calc.UnsupportedDate as exc:
        raise _bad_input(exc)
    return DateConversionResponse(bs=BsDate(year=year, month=month, day=day), ad=ad.isoformat())


@router.get("/calculators/date/ad-to-bs", response_model=DateConversionResponse)
async def ad_to_bs(date: str) -> DateConversionResponse:
    try:
        ad_date = datetime.date.fromisoformat(date)
        bs = await asyncio.to_thread(date_calc.ad_to_bs, ad_date)
    except (ValueError, date_calc.UnsupportedDate) as exc:
        raise _bad_input(exc)
    return DateConversionResponse(bs=BsDate(year=bs.year, month=bs.month, day=bs.day), ad=ad_date.isoformat())


@router.get("/calculators/limitation/claim-types", response_model=list[str])
async def limitation_claim_types() -> list[str]:
    return await asyncio.to_thread(limitation_calc.list_claim_types)


@router.get("/calculators/limitation", response_model=LimitationCheckResponse)
async def check_limitation(claim_type: str, trigger_date: str) -> LimitationCheckResponse:
    try:
        trigger = datetime.date.fromisoformat(trigger_date)
        result = await asyncio.to_thread(limitation_calc.check, claim_type, trigger)
    except (ValueError, limitation_calc.UnknownClaimType) as exc:
        raise _bad_input(exc)
    return LimitationCheckResponse(**result)


@router.get("/calculators/court-fee", response_model=CourtFeeEstimateResponse)
async def estimate_court_fee(claim_value: float) -> CourtFeeEstimateResponse:
    try:
        result = await asyncio.to_thread(court_fee_calc.estimate, claim_value)
    except ValueError as exc:
        raise _bad_input(exc)
    return CourtFeeEstimateResponse(**result)


@router.get("/calculators/court-fee/appeal", response_model=CourtFeeAppealResponse)
async def estimate_appeal_fee(disputed_value: float) -> CourtFeeAppealResponse:
    try:
        result = await asyncio.to_thread(court_fee_calc.estimate_appeal, disputed_value)
    except ValueError as exc:
        raise _bad_input(exc)
    return CourtFeeAppealResponse(**result)


@router.get("/calculators/labour/gratuity", response_model=GratuityResponse)
async def calc_gratuity(basic_monthly_pay: float, months_of_service: float) -> GratuityResponse:
    try:
        result = await asyncio.to_thread(labour_calc.gratuity, basic_monthly_pay, months_of_service)
    except ValueError as exc:
        raise _bad_input(exc)
    return GratuityResponse(**result)


@router.get("/calculators/labour/notice", response_model=NoticeResponse)
async def calc_notice(service_days: int, daily_wage: float) -> NoticeResponse:
    try:
        result = await asyncio.to_thread(labour_calc.notice, service_days, daily_wage)
    except ValueError as exc:
        raise _bad_input(exc)
    return NoticeResponse(**result)


@router.get("/calculators/labour/severance", response_model=SeveranceResponse)
async def calc_severance(basic_monthly_pay: float, years_of_service: float) -> SeveranceResponse:
    try:
        result = await asyncio.to_thread(labour_calc.severance, basic_monthly_pay, years_of_service)
    except ValueError as exc:
        raise _bad_input(exc)
    return SeveranceResponse(**result)


# ------------------------------------------------------------------ S9: drafting ---

@router.get("/drafting/templates", response_model=list[DraftingTemplateSummary])
async def list_drafting_templates() -> list[DraftingTemplateSummary]:
    rows = await asyncio.to_thread(drafting_render.list_templates)
    return [DraftingTemplateSummary(**r) for r in rows]


@router.get("/drafting/templates/{template_id}", response_model=DraftingTemplateDetail)
async def get_drafting_template(template_id: str) -> DraftingTemplateDetail:
    try:
        detail = await asyncio.to_thread(drafting_render.get_template_detail, template_id)
    except drafting_render.UnknownTemplate:
        raise HTTPException(status_code=404, detail="drafting template not found")
    return DraftingTemplateDetail(**detail)


@router.post("/drafting/templates/{template_id}/draft")
async def draft_document(template_id: str, payload: DraftRequest) -> Response:
    try:
        docx_bytes = await asyncio.to_thread(
            drafting_render.render_docx, template_id, payload.answers, payload.language
        )
    except drafting_render.UnknownTemplate:
        raise HTTPException(status_code=404, detail="drafting template not found")
    except (drafting_render.MissingField, ValueError) as exc:
        raise _bad_input(exc)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{template_id}.docx"'},
    )


# --------------------------------------------------------- S10: AI fill + save ---

@router.post("/drafting/templates/{template_id}/ai-fill", response_model=AiFillResponse)
async def ai_fill_field(template_id: str, payload: AiFillRequest, user: dict = Depends(_require_user)) -> AiFillResponse:
    """Expands a free-text field's short hint via the LLM. Signed-in only,
    and metered against the same daily quota as chat answers (S13 gives
    this its own cost-tracked ledger; until then, one shared per-user
    budget is enough to stop runaway use)."""
    allowed, _ = await asyncio.to_thread(supa.check_and_increment_quota, user["id"])
    if not allowed:
        raise HTTPException(status_code=429, detail="daily AI-fill limit reached")
    try:
        text = await asyncio.to_thread(
            drafting_ai_fill.fill, template_id, payload.field_id, payload.hint, payload.language, payload.other_answers
        )
    except drafting_ai_fill.UnknownField as exc:
        raise _bad_input(exc)
    except ValueError as exc:
        raise _bad_input(exc)
    except llm.LLMUnavailable:
        raise HTTPException(status_code=503, detail="AI fill is temporarily unavailable, try again shortly")
    return AiFillResponse(text=text)


@router.post("/drafting/drafts", response_model=SavedDraftOut, status_code=201)
async def create_draft(payload: SavedDraftIn, user: dict = Depends(_require_user)) -> SavedDraftOut:
    try:
        drafting_render.get_template(payload.template_id)
    except drafting_render.UnknownTemplate:
        raise HTTPException(status_code=404, detail="drafting template not found")
    row = await asyncio.to_thread(
        supa.draft_create, user["id"], payload.template_id, payload.language, payload.answers, payload.title
    )
    if row is None:
        raise HTTPException(status_code=503, detail="saving drafts is unavailable right now")
    return SavedDraftOut(**row)


@router.get("/drafting/drafts", response_model=list[SavedDraftOut])
async def list_drafts(user: dict = Depends(_require_user)) -> list[SavedDraftOut]:
    rows = await asyncio.to_thread(supa.draft_list, user["id"])
    return [SavedDraftOut(**r) for r in rows]


@router.get("/drafting/drafts/{draft_id}", response_model=SavedDraftOut)
async def get_draft(draft_id: str, user: dict = Depends(_require_user)) -> SavedDraftOut:
    row = await asyncio.to_thread(supa.draft_get, user["id"], draft_id)
    if row is None:
        raise HTTPException(status_code=404, detail="draft not found")
    return SavedDraftOut(**row)


@router.put("/drafting/drafts/{draft_id}", response_model=SavedDraftOut)
async def update_draft(draft_id: str, payload: SavedDraftIn, user: dict = Depends(_require_user)) -> SavedDraftOut:
    row = await asyncio.to_thread(
        supa.draft_update, user["id"], draft_id, payload.language, payload.answers, payload.title
    )
    if row is None:
        raise HTTPException(status_code=404, detail="draft not found")
    return SavedDraftOut(**row)


@router.delete("/drafting/drafts/{draft_id}", status_code=204)
async def delete_draft(draft_id: str, user: dict = Depends(_require_user)) -> None:
    await asyncio.to_thread(supa.draft_delete, user["id"], draft_id)


@router.get("/drafting/drafts/{draft_id}/versions", response_model=list[DraftVersionOut])
async def list_draft_versions(draft_id: str, user: dict = Depends(_require_user)) -> list[DraftVersionOut]:
    versions = await asyncio.to_thread(supa.draft_versions_list, user["id"], draft_id)
    return [DraftVersionOut(**v) for v in (versions or [])]
