"""Questionnaire field + document paragraph shapes shared by every drafting
template (S9)."""
from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class Field:
    id: str
    label: dict  # {"en": "...", "ne": "..."}
    type: str  # "text" | "textarea" | "number" | "date"
    required: bool = True
    help: dict | None = None  # {"en": "...", "ne": "..."}
    default: object = None


@dataclasses.dataclass(frozen=True)
class Paragraph:
    """One paragraph of the generated document. `text` holds a Jinja source
    string per language - empty/missing for a language means the paragraph
    is skipped when drafting in that language."""
    text: dict  # {"en": "jinja source", "ne": "jinja source"}
    bold: bool = False
    align: str = "left"  # "left" | "center" | "right"


@dataclasses.dataclass(frozen=True)
class TemplateSpec:
    id: str
    title: dict  # {"en": "...", "ne": "..."}
    description: dict
    fields: list[Field]
    paragraphs: list[Paragraph]
    provisions: list[dict] = dataclasses.field(default_factory=list)  # [{law_title_ne, section}]
