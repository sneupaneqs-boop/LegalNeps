"""Questionnaire field + document block shapes shared by every drafting
template (S9, extended for prescribed-format layout).

A template is a list of *blocks*: `Paragraph` (one paragraph, optionally
aligned / indented / underlined / repeated per line of a textarea answer) and
`Table` (borderless layout tables such as the two-column "court fills this in"
header, or bordered tables such as the thumbprint boxes). Text is Jinja source,
one per language; a language with no text for a block skips the block.
"""
from __future__ import annotations

import dataclasses

ALIGNS = ("left", "center", "right", "justify")

# Template categories (drives the grouping in the UI).
CATEGORIES = ("court", "police", "office", "deeds", "notices")

# "official": transcribed from a schedule (अनुसूची) prescribed by a statute or
# rules, and `source` names it.  "standard": no schedule prescribes a form -
# laid out to ordinary Nepali court / office letter conventions, and labelled
# as such everywhere it is shown.
KINDS = ("official", "standard")


@dataclasses.dataclass(frozen=True)
class Field:
    id: str
    label: dict  # {"en": "...", "ne": "..."}
    type: str  # "text" | "textarea" | "number" | "date" | "select"
    required: bool = True
    help: dict | None = None  # {"en": "...", "ne": "..."}
    default: object = None
    # for type == "select": [{"value": "छोरा", "label": {"en": .., "ne": ..}}, ...]
    options: list | None = None


@dataclasses.dataclass(frozen=True)
class Paragraph:
    """One paragraph of the generated document. `text` holds a Jinja source
    string per language - empty/missing for a language means the paragraph
    is skipped when drafting in that language."""
    text: dict  # {"en": "jinja source", "ne": "jinja source"}
    bold: bool = False
    align: str = "left"  # see ALIGNS
    underline: bool = False
    italic: bool = False
    indent: float = 0.0  # cm from the left margin
    hanging: float = 0.0  # cm; with `label` the number/letter hangs in the margin
    label: str | None = None  # Jinja source of a hanging label ("१.", "(क)")
    size: float | None = None  # pt (None = template default)
    space_before: float | None = None  # pt
    space_after: float | None = None  # pt
    keep_next: bool = False
    page_break_before: bool = False
    # repeat this paragraph once per non-empty line of answers[each]; the
    # Jinja context gains `item`, `n` (1-based) and `ka` ((क), (ख) ... letter).
    # At least `min_items` paragraphs are always produced (blank items are
    # rendered with dotted blanks, like the official form's empty (क)(ख)(ग)).
    each: str | None = None
    min_items: int = 0


@dataclasses.dataclass(frozen=True)
class Cell:
    text: dict  # Jinja source per language
    bold: bool = False
    align: str = "left"
    underline: bool = False
    italic: bool = False
    valign: str = "top"  # top | center | bottom


@dataclasses.dataclass(frozen=True)
class RepeatRow:
    """A table row repeated once per non-empty line of the textarea answer
    `each` (at least `min_items` rows). Cell text may use `item`, `n`, `ka`."""
    cells: list  # list[Cell]
    each: str
    min_items: int = 0


@dataclasses.dataclass(frozen=True)
class Table:
    rows: list  # list[list[Cell]]
    widths: list  # column widths in cm
    borders: str = "none"  # "none" | "all"
    row_height: float | None = None  # cm minimum
    align: str = "left"  # table position: left | center | right
    space_after: float | None = None
    size: float | None = None  # font size (pt) for every cell; None = document default
    lang: str | None = None  # render only when drafting in this language (None = every language)


@dataclasses.dataclass(frozen=True)
class PageBreak:
    pass


@dataclasses.dataclass(frozen=True)
class TemplateSpec:
    id: str
    title: dict  # {"en": "...", "ne": "..."}
    description: dict
    fields: list[Field]
    paragraphs: list  # blocks: Paragraph | Table | PageBreak
    provisions: list[dict] = dataclasses.field(default_factory=list)  # [{law_title_ne, section}]
    category: str = "notices"
    kind: str = "standard"
    # For kind == "official": {"law_title_ne", "schedule", "relates_to", "url", "page"}.
    # For kind == "standard" with a legal basis: {"law_title_ne", "relates_to", "note"}.
    source: dict | None = None
    languages: tuple = ("en", "ne")
    font_size: float = 12.0
    keywords: tuple = ()  # extra search terms (both scripts)
