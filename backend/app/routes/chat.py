from fastapi import APIRouter

from .. import config
from ..generation import generate_answer
from ..retrieval import detect_language, retrieve
from ..schemas import ChatRequest, ChatResponse, Source

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    lang = detect_language(payload.message) if payload.language == "auto" else payload.language

    hits = retrieve(payload.message, lang, top_k=config.TOP_K)
    answer, llm_used = generate_answer(payload.message, hits, lang)

    sources = [
        Source(
            id=hit["id"],
            category=hit["category"],
            topic=hit["topic"],
            title=hit["title_en"] if lang == "en" else hit["title_ne"],
            citation=hit["source_en"] if lang == "en" else hit["source_ne"],
            snippet=(hit["text_en"] if lang == "en" else hit["text_ne"])[:220],
            score=hit["score"],
        )
        for hit in hits
    ]

    return ChatResponse(answer=answer, language=lang, sources=sources, llm_used=llm_used)
