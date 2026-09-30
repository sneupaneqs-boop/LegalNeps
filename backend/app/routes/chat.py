import asyncio
import datetime
import json
import logging
import time

from typing import Annotated

from fastapi import APIRouter, Depends, File, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import Response, StreamingResponse
from starlette.concurrency import iterate_in_threadpool

from .. import compliance, llm, playbooks, prompt_guard, supa, tiers
from ..calculators import court_fee as court_fee_calc
from ..calculators import dates as date_calc
from ..calculators import labour as labour_calc
from ..calculators import limitation as limitation_calc
from ..drafting import ai_fill as drafting_ai_fill
from ..drafting import render as drafting_render
from ..generation import answer_question, stream_answer
from ..playbook_matcher import match as match_playbook
from ..retrieval import corpus_stats, doc_slug, get_index
from ..schemas import (AiFillRequest, AiFillResponse, BsDate, ChatRequest, ChatResponse, CompanyProfileIn,
                        CompanyProfileOut, CourtFeeAppealResponse, CourtFeeEstimateResponse, DateConversionResponse,
                        DraftingTemplateDetail, DraftingTemplateSummary, DraftRequest, DraftVersionOut,
                        GratuityResponse, LawDoc, LawSection, LimitationCheckResponse, LlmUsageOut,
                        MatterFileDownload, MatterFileOut, MatterIn, MatterNoteIn, MatterNoteOut, MatterOut,
                        MatterTaskIn, MatterTaskOut, MatterTaskUpdateIn, MatterUpdateIn, NoticeResponse,
                        ObligationDue, Playbook, PlaybookMatchResponse, PlaybookSummary, SavedDraftIn, SavedDraftOut,
                        SavedResearchIn, SavedResearchOut, SearchResponse, SeveranceResponse, Source,
                        UpcomingObligationsResponse)

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


async def _enforce_limits(request: Request, user: dict | None) -> str:
    """Rate-limits by IP always, and by the user's own daily quota (S13:
    plan-based - tiers.daily_quota_for()) when signed in. Returns the
    caller's plan ("free" for anonymous callers), so the route can pick an
    LLM tier from the same lookup instead of fetching it twice."""
    ip = _client_ip(request)
    if not await asyncio.to_thread(supa.check_ip_rate_limit, ip):
        raise HTTPException(status_code=429, detail="too many requests from this address, try again later")
    if user is None:
        return "free"
    plan = await asyncio.to_thread(supa.profile_get_plan, user["id"])
    allowed, _ = await asyncio.to_thread(supa.check_and_increment_quota, user["id"], tiers.daily_quota_for(plan))
    if not allowed:
        raise HTTPException(status_code=429, detail="daily answer limit reached")
    return plan


def _log_request(endpoint: str, started: float, *, llm_used: bool, cached: bool, llm_calls: int,
                 language: str | None, tier: str = "free") -> None:
    # One structured line per request: what it cost (llm_calls, latency) and
    # whether it hit no provider at all (cache) or several (retries/fallback).
    reqlog.info(json.dumps({
        "endpoint": endpoint,
        "llm_calls": llm_calls,
        "tier": tier,
        "latency_ms": int((time.time() - started) * 1000),
        "cache_hit": cached,
        "llm_used": llm_used,
        "language": language,
    }, ensure_ascii=False))


def _record_llm_usage_sync(user: dict | None, endpoint: str, result: dict) -> None:
    """S13: writes one llm_usage row per real (non-cached, non-free-tier)
    generation, with an estimated cost from real token counts. Free-tier
    and cached answers aren't billed to a specific model, so they're not
    logged here - request-level telemetry for those already goes through
    _log_request(). Blocking (httpx sync client, same as the rest of
    supa.py) - callers on the event loop must run it via asyncio.to_thread."""
    tier = result.get("tier", "free")
    if user is None or tier == "free" or result.get("cached"):
        return
    usage = result.get("usage") or {}
    cost = tiers.estimate_cost_usd(tier, usage.get("input_tokens"), usage.get("output_tokens"))
    supa.llm_usage_record(
        user["id"], endpoint, tier, "anthropic", tiers.model_for_tier(tier),
        result.get("prompt_version") or "unknown", usage.get("input_tokens"), usage.get("output_tokens"),
        cost, result.get("flagged_injection", False),
    )


async def _log_llm_usage(user: dict | None, endpoint: str, result: dict) -> None:
    await asyncio.to_thread(_record_llm_usage_sync, user, endpoint, result)


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
        pinned=bool(hit.get("pinned")), stale=bool(hit.get("stale")),
        decided_bs=hit.get("decided_bs"), governing_law_bs=hit.get("governing_law_bs"),
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request, authorization: str | None = Header(None)) -> ChatResponse:
    # LLM + search calls are blocking; keep the event loop free for other requests.
    user = await _current_user(authorization)
    plan = await _enforce_limits(request, user)
    tier = tiers.select_tier(plan, "chat")
    started = time.time()
    history = [t.model_dump() for t in payload.history]
    result = await asyncio.to_thread(answer_question, payload.message, payload.language or "auto", history, tier)
    lang = result["language"]
    _log_request("/api/chat", started, llm_used=result["llm_used"], cached=result.get("cached", False),
                 llm_calls=result.get("llm_calls", 0), language=lang, tier=tier)
    await _log_llm_usage(user, "/api/chat", result)
    return ChatResponse(
        answer=result["answer"],
        language=lang,
        sources=[_to_source(i, h, lang) for i, h in enumerate(result["sources"], 1)],
        llm_used=result["llm_used"],
        analysis=result.get("analysis"),
        cached=result.get("cached", False),
        playbook=result.get("playbook"),
        verification=result.get("verification"),
    )


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest, request: Request,
                      authorization: str | None = Header(None)) -> StreamingResponse:
    """NDJSON stream: {"type":"meta", sources...} then {"type":"delta","text"}* then {"type":"done"}.
    Sources arrive before the model starts writing, so the UI can show them immediately."""
    user = await _current_user(authorization)
    plan = await _enforce_limits(request, user)
    tier = tiers.select_tier(plan, "chat")
    started = time.time()
    history = [t.model_dump() for t in payload.history]

    def events():
        lang = "en"
        try:
            for kind, data in stream_answer(payload.message, payload.language or "auto", history, tier):
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
                                 language=lang, tier=tier)
                    _record_llm_usage_sync(user, "/api/chat/stream", data)
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

# NaN / Infinity parse as floats but cannot be serialised to JSON (the response 500'd);
# reject them (and absurdly large values) as 422 like the tools endpoints do.
Finite = Annotated[float, Query(allow_inf_nan=False, ge=-1e12, le=1e12)]


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
async def estimate_court_fee(claim_value: Finite) -> CourtFeeEstimateResponse:
    try:
        result = await asyncio.to_thread(court_fee_calc.estimate, claim_value)
    except ValueError as exc:
        raise _bad_input(exc)
    return CourtFeeEstimateResponse(**result)


@router.get("/calculators/court-fee/appeal", response_model=CourtFeeAppealResponse)
async def estimate_appeal_fee(disputed_value: Finite) -> CourtFeeAppealResponse:
    try:
        result = await asyncio.to_thread(court_fee_calc.estimate_appeal, disputed_value)
    except ValueError as exc:
        raise _bad_input(exc)
    return CourtFeeAppealResponse(**result)


@router.get("/calculators/labour/gratuity", response_model=GratuityResponse)
async def calc_gratuity(basic_monthly_pay: Finite, months_of_service: Finite) -> GratuityResponse:
    try:
        result = await asyncio.to_thread(labour_calc.gratuity, basic_monthly_pay, months_of_service)
    except ValueError as exc:
        raise _bad_input(exc)
    return GratuityResponse(**result)


@router.get("/calculators/labour/notice", response_model=NoticeResponse)
async def calc_notice(service_days: int, daily_wage: Finite) -> NoticeResponse:
    try:
        result = await asyncio.to_thread(labour_calc.notice, service_days, daily_wage)
    except ValueError as exc:
        raise _bad_input(exc)
    return NoticeResponse(**result)


@router.get("/calculators/labour/severance", response_model=SeveranceResponse)
async def calc_severance(basic_monthly_pay: Finite, years_of_service: Finite) -> SeveranceResponse:
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
    """The drafted document as DOCX (default) or PDF (`format: "pdf"`)."""
    try:
        data, media_type, ext = await asyncio.to_thread(
            drafting_render.render_file, template_id, payload.answers, payload.language, payload.format
        )
    except drafting_render.UnknownTemplate:
        raise HTTPException(status_code=404, detail="drafting template not found")
    except (drafting_render.MissingField, ValueError) as exc:
        raise _bad_input(exc)
    return Response(
        content=data,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{template_id}.{ext}"'},
    )


# --------------------------------------------------------- S10: AI fill + save ---

@router.post("/drafting/templates/{template_id}/ai-fill", response_model=AiFillResponse)
async def ai_fill_field(template_id: str, payload: AiFillRequest, user: dict = Depends(_require_user)) -> AiFillResponse:
    """Expands a free-text field's short hint via the LLM. Signed-in only,
    metered against the caller's plan-based daily quota, and (S13) billed to
    Sonnet 5.5 for any paid plan - "drafting" per STRATEGY's tier-routing
    rule - with the real cost logged to llm_usage; free-plan users keep
    using the free chain, same as before S13."""
    plan = await asyncio.to_thread(supa.profile_get_plan, user["id"])
    allowed, _ = await asyncio.to_thread(supa.check_and_increment_quota, user["id"], tiers.daily_quota_for(plan))
    if not allowed:
        raise HTTPException(status_code=429, detail="daily AI-fill limit reached")
    tier = tiers.select_tier(plan, "draft")
    flagged = prompt_guard.looks_like_injection(payload.hint)
    try:
        if tier == "free":
            text = await asyncio.to_thread(
                drafting_ai_fill.fill, template_id, payload.field_id, payload.hint, payload.language, payload.other_answers
            )
        else:
            text, usage = await asyncio.to_thread(
                drafting_ai_fill.fill_paid, template_id, payload.field_id, payload.hint, payload.language,
                payload.other_answers, tier,
            )
            cost = tiers.estimate_cost_usd(tier, usage.get("input_tokens"), usage.get("output_tokens"))
            await asyncio.to_thread(
                supa.llm_usage_record, user["id"], "/api/drafting/ai-fill", tier, "anthropic",
                tiers.model_for_tier(tier), drafting_ai_fill.PROMPT_VERSION,
                usage.get("input_tokens"), usage.get("output_tokens"), cost, flagged,
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


# --------------------------------------------------------------- S11: matters ---
# The backend talks to Supabase with the service-role key, which bypasses
# RLS - so unlike a direct client, ownership here is enforced in this route
# layer, not just by the database. Every note/task/file endpoint below
# first confirms the matter belongs to the caller (404, not 403, so a
# stranger's matter ID looks identical to a nonexistent one) before
# touching anything scoped to it.
async def _require_matter(matter_id: str, user: dict) -> dict:
    matter = await asyncio.to_thread(supa.matter_get, user["id"], matter_id)
    if matter is None:
        raise HTTPException(status_code=404, detail="matter not found")
    return matter


@router.post("/matters", response_model=MatterOut, status_code=201)
async def create_matter(payload: MatterIn, user: dict = Depends(_require_user)) -> MatterOut:
    row = await asyncio.to_thread(supa.matter_create, user["id"], payload.client_name, payload.facts)
    if row is None:
        raise HTTPException(status_code=503, detail="matters are unavailable right now")
    return MatterOut(**row)


@router.get("/matters", response_model=list[MatterOut])
async def list_matters(user: dict = Depends(_require_user)) -> list[MatterOut]:
    rows = await asyncio.to_thread(supa.matter_list, user["id"])
    return [MatterOut(**r) for r in rows]


@router.get("/matters/{matter_id}", response_model=MatterOut)
async def get_matter(matter_id: str, user: dict = Depends(_require_user)) -> MatterOut:
    return MatterOut(**await _require_matter(matter_id, user))


@router.put("/matters/{matter_id}", response_model=MatterOut)
async def update_matter(matter_id: str, payload: MatterUpdateIn, user: dict = Depends(_require_user)) -> MatterOut:
    await _require_matter(matter_id, user)
    row = await asyncio.to_thread(
        supa.matter_update, user["id"], matter_id, payload.client_name, payload.facts, payload.status
    )
    if row is None:
        raise HTTPException(status_code=404, detail="matter not found")
    return MatterOut(**row)


@router.delete("/matters/{matter_id}", status_code=204)
async def delete_matter(matter_id: str, user: dict = Depends(_require_user)) -> None:
    await asyncio.to_thread(supa.matter_delete, user["id"], matter_id)


@router.post("/matters/{matter_id}/notes", response_model=MatterNoteOut, status_code=201)
async def create_matter_note(matter_id: str, payload: MatterNoteIn, user: dict = Depends(_require_user)) -> MatterNoteOut:
    await _require_matter(matter_id, user)
    row = await asyncio.to_thread(supa.matter_note_create, user["id"], matter_id, payload.body)
    if row is None:
        raise HTTPException(status_code=503, detail="matters are unavailable right now")
    return MatterNoteOut(**row)


@router.get("/matters/{matter_id}/notes", response_model=list[MatterNoteOut])
async def list_matter_notes(matter_id: str, user: dict = Depends(_require_user)) -> list[MatterNoteOut]:
    await _require_matter(matter_id, user)
    rows = await asyncio.to_thread(supa.matter_note_list, user["id"], matter_id)
    return [MatterNoteOut(**r) for r in rows]


@router.delete("/matters/{matter_id}/notes/{note_id}", status_code=204)
async def delete_matter_note(matter_id: str, note_id: str, user: dict = Depends(_require_user)) -> None:
    await _require_matter(matter_id, user)
    await asyncio.to_thread(supa.matter_note_delete, user["id"], matter_id, note_id)


@router.post("/matters/{matter_id}/tasks", response_model=MatterTaskOut, status_code=201)
async def create_matter_task(matter_id: str, payload: MatterTaskIn, user: dict = Depends(_require_user)) -> MatterTaskOut:
    await _require_matter(matter_id, user)
    row = await asyncio.to_thread(supa.matter_task_create, user["id"], matter_id, payload.title, payload.due_date)
    if row is None:
        raise HTTPException(status_code=503, detail="matters are unavailable right now")
    return MatterTaskOut(**row)


@router.get("/matters/{matter_id}/tasks", response_model=list[MatterTaskOut])
async def list_matter_tasks(matter_id: str, user: dict = Depends(_require_user)) -> list[MatterTaskOut]:
    await _require_matter(matter_id, user)
    rows = await asyncio.to_thread(supa.matter_task_list, user["id"], matter_id)
    return [MatterTaskOut(**r) for r in rows]


@router.put("/matters/{matter_id}/tasks/{task_id}", response_model=MatterTaskOut)
async def update_matter_task(matter_id: str, task_id: str, payload: MatterTaskUpdateIn,
                              user: dict = Depends(_require_user)) -> MatterTaskOut:
    await _require_matter(matter_id, user)
    row = await asyncio.to_thread(
        supa.matter_task_update, user["id"], matter_id, task_id, payload.title, payload.done, payload.due_date
    )
    if row is None:
        raise HTTPException(status_code=404, detail="task not found")
    return MatterTaskOut(**row)


@router.delete("/matters/{matter_id}/tasks/{task_id}", status_code=204)
async def delete_matter_task(matter_id: str, task_id: str, user: dict = Depends(_require_user)) -> None:
    await _require_matter(matter_id, user)
    await asyncio.to_thread(supa.matter_task_delete, user["id"], matter_id, task_id)


@router.post("/matters/{matter_id}/files", response_model=MatterFileOut, status_code=201)
async def upload_matter_file(matter_id: str, file: UploadFile = File(...),
                              user: dict = Depends(_require_user)) -> MatterFileOut:
    await _require_matter(matter_id, user)
    # S14: read in bounded chunks rather than file.read() - an oversized
    # upload used to be buffered in full (spooled to disk past Starlette's
    # threshold, but still fully consumed) before this check ever ran,
    # so a large-enough request body was itself a resource-exhaustion path
    # independent of the 20MB limit it was meant to enforce.
    max_bytes = 20 * 1024 * 1024
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(status_code=413, detail="file too large (20MB limit)")
        chunks.append(chunk)
    content = b"".join(chunks)
    row = await asyncio.to_thread(
        supa.matter_file_create, user["id"], matter_id, file.filename or "upload",
        content, file.content_type or "application/octet-stream",
    )
    if row is None:
        raise HTTPException(status_code=503, detail="matters are unavailable right now")
    return MatterFileOut(**row)


@router.get("/matters/{matter_id}/files", response_model=list[MatterFileOut])
async def list_matter_files(matter_id: str, user: dict = Depends(_require_user)) -> list[MatterFileOut]:
    await _require_matter(matter_id, user)
    rows = await asyncio.to_thread(supa.matter_file_list, user["id"], matter_id)
    return [MatterFileOut(**r) for r in rows]


@router.get("/matters/{matter_id}/files/{file_id}/download", response_model=MatterFileDownload)
async def download_matter_file(matter_id: str, file_id: str, user: dict = Depends(_require_user)) -> MatterFileDownload:
    await _require_matter(matter_id, user)
    url = await asyncio.to_thread(supa.matter_file_signed_url, user["id"], matter_id, file_id)
    if url is None:
        raise HTTPException(status_code=404, detail="file not found")
    return MatterFileDownload(url=url)


@router.delete("/matters/{matter_id}/files/{file_id}", status_code=204)
async def delete_matter_file(matter_id: str, file_id: str, user: dict = Depends(_require_user)) -> None:
    await _require_matter(matter_id, user)
    await asyncio.to_thread(supa.matter_file_delete, user["id"], matter_id, file_id)


# ---------------------------------------------------------------- S12: compliance radar
@router.put("/company-profile")
async def put_company_profile(payload: CompanyProfileIn, user: dict = Depends(_require_user)) -> CompanyProfileOut:
    profile = await asyncio.to_thread(
        supa.company_profile_upsert, user["id"], payload.company_name, payload.entity_type,
        payload.pan_vat_registered, payload.has_employees, payload.reminder_email,
    )
    if profile is None:
        raise HTTPException(status_code=503, detail="not configured")
    return profile


@router.get("/company-profile")
async def get_company_profile(user: dict = Depends(_require_user)) -> CompanyProfileOut:
    profile = await asyncio.to_thread(supa.company_profile_get, user["id"])
    if profile is None:
        raise HTTPException(status_code=404, detail="no company profile - create one with PUT /company-profile")
    return profile


@router.get("/obligations/upcoming")
async def upcoming_obligations(within_days: int = Query(60, ge=1, le=365),
                                user: dict = Depends(_require_user)) -> UpcomingObligationsResponse:
    profile = await asyncio.to_thread(supa.company_profile_get, user["id"])
    if profile is None:
        raise HTTPException(status_code=404, detail="no company profile - create one with PUT /company-profile")
    all_obligations = await asyncio.to_thread(supa.obligations_list)
    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=within_days)
    due: list[ObligationDue] = []
    for ob in all_obligations:
        if not compliance.applies_to(ob["applies_if"], profile):
            continue
        result = compliance.next_due(ob, today)
        if result is None:
            continue
        period, due_bs = result
        due_ad = date_calc.bs_to_ad(due_bs.year, due_bs.month, due_bs.day)
        if due_ad > horizon:
            continue
        due.append(ObligationDue(
            id=ob["id"], title_en=ob["title_en"], title_ne=ob["title_ne"], category=ob["category"],
            frequency=ob["frequency"], citation=ob["citation"], source_url=ob.get("source_url"),
            period=period, due_date_bs=str(due_bs), due_date_ad=due_ad.isoformat(),
            days_remaining=(due_ad - today).days,
        ))
    due.sort(key=lambda o: o.due_date_ad)
    return UpcomingObligationsResponse(company_name=profile["company_name"], obligations=due)


# ---------------------------------------------------------------- S13: AI gateway v2
@router.get("/llm-usage")
async def list_llm_usage(limit: int = Query(100, ge=1, le=500),
                          user: dict = Depends(_require_user)) -> list[LlmUsageOut]:
    """Cost-per-query visibility (STRATEGY's S13 "done when" bar): every
    paid-tier (haiku/sonnet) call this user triggered, with its real token
    counts and estimated USD cost. Free-tier calls aren't billed to a
    specific model, so they never appear here (see _record_llm_usage_sync)."""
    rows = await asyncio.to_thread(supa.llm_usage_list, user["id"], limit)
    return [LlmUsageOut(**row) for row in rows]
