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


class Bilingual(BaseModel):
    en: str
    ne: str


class PlaybookSummary(BaseModel):
    id: str
    area: Optional[str] = None
    issue: Bilingual


class ResolvedProvision(BaseModel):
    law_title_ne: str
    section: Optional[str] = None
    slug: str
    citation: str
    url: Optional[str] = None
    status: Optional[str] = None
    note: dict = {}


class PlaybookLimitation(BaseModel):
    note: Bilingual
    provision: Optional[ResolvedProvision] = None


class PlaybookMatchResponse(BaseModel):
    playbook_id: Optional[str] = None


class DraftingField(BaseModel):
    id: str
    label: Bilingual
    type: str
    required: bool = True
    help: Optional[Bilingual] = None


class DraftingTemplateSummary(BaseModel):
    id: str
    title: Bilingual
    description: Bilingual


class DraftingTemplateDetail(BaseModel):
    id: str
    title: Bilingual
    description: Bilingual
    fields: List[DraftingField]
    provisions: List[ResolvedProvision]


class DraftRequest(BaseModel):
    language: Literal["en", "ne"] = "ne"
    answers: dict = Field(default_factory=dict)


class AiFillRequest(BaseModel):
    field_id: str
    hint: str = Field(..., min_length=1, max_length=2000)
    language: Literal["en", "ne"] = "ne"
    other_answers: dict = Field(default_factory=dict)


class AiFillResponse(BaseModel):
    text: str


class SavedDraftIn(BaseModel):
    template_id: str
    language: Literal["en", "ne"] = "ne"
    answers: dict = Field(default_factory=dict)
    title: Optional[str] = None


class SavedDraftOut(BaseModel):
    id: str
    template_id: str
    title: Optional[str] = None
    language: str
    answers: dict
    created_at: str
    updated_at: str


class DraftVersionOut(BaseModel):
    id: str
    version_number: int
    language: str
    answers: dict
    created_at: str


class MatterIn(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=200)
    facts: Optional[str] = None


class MatterUpdateIn(BaseModel):
    client_name: Optional[str] = Field(None, min_length=1, max_length=200)
    facts: Optional[str] = None
    status: Optional[Literal["open", "closed"]] = None


class MatterOut(BaseModel):
    id: str
    client_name: str
    facts: Optional[str] = None
    status: str
    created_at: str
    updated_at: str


class MatterNoteIn(BaseModel):
    body: str = Field(..., min_length=1, max_length=10000)


class MatterNoteOut(BaseModel):
    id: str
    body: str
    created_at: str


class MatterTaskIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    due_date: Optional[str] = None


class MatterTaskUpdateIn(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    done: Optional[bool] = None
    due_date: Optional[str] = None


class MatterTaskOut(BaseModel):
    id: str
    title: str
    done: bool
    due_date: Optional[str] = None
    created_at: str
    updated_at: str


class MatterFileOut(BaseModel):
    id: str
    filename: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: str


class MatterFileDownload(BaseModel):
    url: str


class BsDate(BaseModel):
    year: int
    month: int
    day: int


class DateConversionResponse(BaseModel):
    bs: BsDate
    ad: str


class LimitationCheckResponse(BaseModel):
    claim_type: str
    trigger_date: str
    deadline: str
    days_remaining: int
    is_time_barred: bool
    note: Bilingual
    provision: ResolvedProvision


class CourtFeeEstimateResponse(BaseModel):
    claim_value: float
    filing_fee_npr: float
    filing_fee_provision: ResolvedProvision
    court_fee_npr: float
    court_fee_provision: ResolvedProvision
    total_npr: float


class CourtFeeAppealResponse(BaseModel):
    disputed_value: float
    appeal_fee_npr: float
    provision: ResolvedProvision


class GratuityResponse(BaseModel):
    amount_npr: float
    provision: ResolvedProvision


class NoticeResponse(BaseModel):
    notice_period_days: int
    pay_in_lieu_npr: float
    provision: ResolvedProvision


class SeveranceResponse(BaseModel):
    amount_npr: float
    provision: ResolvedProvision


class Playbook(BaseModel):
    id: str
    area: Optional[str] = None
    issue: Bilingual
    fact_questions: List[Bilingual]
    provisions: List[ResolvedProvision]
    evidence: List[Bilingual]
    forum: Bilingual
    limitation: PlaybookLimitation
    next_steps: List[Bilingual]
    template_link: Optional[str] = None
