from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Turn(BaseModel):
    role: Literal["user", "bot"]
    text: str = Field(..., max_length=6000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    language: Optional[Literal["en", "ne", "auto"]] = "auto"
    # earlier turns, oldest first, so follow-ups ("what about daughters?") make sense
    history: List[Turn] = Field(default_factory=list, max_length=20)


class Source(BaseModel):
    n: int
    id: str
    category: str
    doc_type: Optional[str] = None
    topic: str
    title: str
    citation: str
    snippet: str
    score: float
    url: Optional[str] = None


class Analysis(BaseModel):
    intent: Optional[str] = None
    concern: Optional[str] = None
    area: Optional[str] = None
    queries_ne: List[str] = []
    laws: List[str] = []


class ChatResponse(BaseModel):
    answer: str
    language: Literal["en", "ne"]
    sources: List[Source]
    llm_used: bool
    analysis: Optional[Analysis] = None
    cached: bool = False


class SearchResponse(BaseModel):
    query: str
    results: List[Source]
