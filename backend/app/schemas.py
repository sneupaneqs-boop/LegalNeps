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
    slug: Optional[str] = None
    section: Optional[str] = None
    status: Optional[str] = None


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


class Amendment(BaseModel):
    name: str
    date_bs: str


class LawSectionSummary(BaseModel):
    id: str
    section: Optional[str] = None
    title_ne: Optional[str] = None
    title_en: Optional[str] = None
    snippet: str


class LawDoc(BaseModel):
    slug: str
    doc_title_ne: Optional[str] = None
    doc_title_en: Optional[str] = None
    doc_type: Optional[str] = None
    status: str
    enacted_bs: Optional[str] = None
    amended_by: List[Amendment] = []
    consolidated_upto: Optional[str] = None
    url: Optional[str] = None
    sections: List[LawSectionSummary]


class LawSectionNeighbour(BaseModel):
    section: Optional[str] = None
    title_ne: Optional[str] = None


class SavedResearchIn(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    answer: ChatResponse
    language: Literal["en", "ne"]


class SavedResearchOut(BaseModel):
    id: str
    question: str
    answer: dict
    language: str
    created_at: str


class LawSection(BaseModel):
    slug: str
    id: str
    section: Optional[str] = None
    title_ne: Optional[str] = None
    title_en: Optional[str] = None
    text_ne: Optional[str] = None
    text_en: Optional[str] = None
    source_ne: Optional[str] = None
    source_en: Optional[str] = None
    url: Optional[str] = None
    doc_title_ne: Optional[str] = None
    doc_title_en: Optional[str] = None
    doc_type: Optional[str] = None
    status: Optional[str] = None
    prev: Optional[LawSectionNeighbour] = None
    next: Optional[LawSectionNeighbour] = None
