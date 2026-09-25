import asyncio

from fastapi import APIRouter, Query

from ..generation import answer_question
from ..retrieval import corpus_stats, get_index
from ..schemas import ChatRequest, ChatResponse, SearchResponse, Source

router = APIRouter()


def _to_source(n: int, hit: dict, lang: str) -> Source:
    en = lang == "en"
    title = (hit.get("title_en") if en and hit.get("title_en") else hit.get("title_ne")) or hit.get("title_en") or ""
    citation = (hit.get("source_en") if en and hit.get("source_en") else hit.get("source_ne")) or ""
    text = (hit.get("text_en") if en and hit.get("text_en") else hit.get("text_ne")) or hit.get("text_en") or ""
    return Source(
        n=n, id=hit["id"], category=hit.get("category", "law"), doc_type=hit.get("doc_type"),
        topic=hit.get("topic") or "", title=title, citation=citation,
        snippet=" ".join(text.split())[:280], score=round(float(hit.get("score", 0.0)), 4),
        url=hit.get("url"),
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    # LLM + search calls are blocking; keep the event loop free for other requests.
    result = await asyncio.to_thread(answer_question, payload.message, payload.language or "auto")
    lang = result["language"]
    return ChatResponse(
        answer=result["answer"],
        language=lang,
        sources=[_to_source(i, h, lang) for i, h in enumerate(result["sources"], 1)],
        llm_used=result["llm_used"],
        analysis=result.get("analysis"),
        cached=result.get("cached", False),
    )


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, max_length=500),
    category: str | None = Query(None, pattern="^(law|precedent)$"),
    k: int = Query(10, ge=1, le=50),
    lang: str = Query("ne", pattern="^(en|ne)$"),
) -> SearchResponse:
    hits = await asyncio.to_thread(lambda: get_index().search([q], top_k=k, category=category))
    return SearchResponse(query=q, results=[_to_source(i, h, lang) for i, h in enumerate(hits, 1)])


@router.get("/stats")
async def stats() -> dict:
    return await asyncio.to_thread(corpus_stats)
