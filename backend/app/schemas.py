from typing import List, Literal, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    language: Optional[Literal["en", "ne", "auto"]] = "auto"


class Source(BaseModel):
    id: str
    category: str
    topic: str
    title: str
    citation: str
    snippet: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    language: Literal["en", "ne"]
    sources: List[Source]
    llm_used: bool
