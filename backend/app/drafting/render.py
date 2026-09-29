"""Questionnaire answers -> rendered DOCX / PDF (S9).

Each template's blocks are Jinja source strings (see registry.py / dsl.py);
this module fills in the questionnaire answers plus always-available context
values (today's date in BS, via S8's date calculator), resolves the block list
into plain layout structures (`RPara` / `RTable`), and hands them to the DOCX
writer (`docx_out`) or the PDF writer (`pdf_out`).
"""
from __future__ import annotations

import dataclasses
import datetime

from jinja2 import Environment, StrictUndefined
from jinja2.exceptions import TemplateError, UndefinedError

from ..calculators.dates import ad_to_bs
from ..playbooks import resolve_provision
from . import nepali
from .inline import strip_inline
from .fields import PageBreak, Paragraph, RepeatRow, Table, TemplateSpec
from .registry import TEMPLATES

FORMATS = ("docx", "pdf")


class UnknownTemplate(ValueError):
    pass


class MissingField(ValueError):
    pass


# ------------------------------------------------------------ resolved layout

@dataclasses.dataclass
class RPara:
    text: str
    bold: bool = False
    align: str = "left"
    underline: bool = False
    italic: bool = False
    indent: float = 0.0
    hanging: float = 0.0
    label: str | None = None
    size: float | None = None
    space_before: float | None = None
    space_after: float | None = None
    keep_next: bool = False
    page_break_before: bool = False


@dataclasses.dataclass
class RCell:
    text: str
    bold: bool = False
    align: str = "left"
    underline: bool = False
    italic: bool = False
    valign: str = "top"


@dataclasses.dataclass
class RTable:
    rows: list
    widths: list
    borders: str = "none"
    row_height: float | None = None
    align: str = "left"
    space_after: float | None = None
    size: float | None = None


@dataclasses.dataclass
class RBreak:
    pass


# ------------------------------------------------------------------- jinja

def _make_env() -> Environment:
    env = Environment(undefined=StrictUndefined, autoescape=False)
    env.filters["blank"] = nepali.blank
    env.filters["nd"] = nepali.nd
    env.filters["bs"] = nepali.bs_numeric
    env.filters["ad"] = nepali.ad_numeric
    env.globals["signoff"] = nepali.signoff
    env.globals["bs"] = nepali.bs_numeric
    env.globals["ka"] = nepali.ka
    env.globals["kaf"] = nepali.ka
    env.globals["opts"] = nepali.opts
    return env


_JINJA_ENV = _make_env()


# ------------------------------------------------------------ catalogue API

def list_templates() -> list[dict]:
    return [_summary(t) for t in TEMPLATES.values()]


def _source_out(spec: TemplateSpec) -> dict | None:
    if not spec.source:
        return None
    s = dict(spec.source)
    s.setdefault("law_title_ne", "")
    return s


def _summary(t: TemplateSpec) -> dict:
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "category": t.category,
        "kind": t.kind,
        "source": _source_out(t),
        "languages": list(t.languages),
        "keywords": list(t.keywords),
    }


def get_template(template_id: str) -> TemplateSpec:
    spec = TEMPLATES.get(template_id)
    if spec is None:
        raise UnknownTemplate(f"{template_id!r} is not a known drafting template")
    return spec


def get_template_detail(template_id: str) -> dict:
    spec = get_template(template_id)
    out = _summary(spec)
    out.update({
        "fields": [
            {"id": f.id, "label": f.label, "type": f.type, "required": f.required, "help": f.help,
             "options": f.options, "default": f.default}
            for f in spec.fields
        ],
        "provisions": [resolve_provision(p) for p in spec.provisions],
        "formats": list(FORMATS),
    })
    return out


# ---------------------------------------------------------------- rendering

def _build_context(spec: TemplateSpec, answers: dict) -> dict:
    ctx: dict = {}
    for f in spec.fields:
        value = answers.get(f.id, f.default)
        if f.required and (value is None or value == ""):
            raise MissingField(f"{f.id!r} is required for template {spec.id!r}")
        ctx[f.id] = value if value is not None else ""
    today = datetime.date.today()
    ctx["today_ad"] = today.isoformat()
    ctx["today_bs"] = str(ad_to_bs(today))
    ctx["today_bs_ne"] = nepali.bs_numeric(today)
    return ctx


def _effective_language(spec: TemplateSpec, language: str) -> str:
    if language not in ("en", "ne"):
        raise ValueError("language must be 'en' or 'ne'")
    # prescribed forms exist only in Nepali: an English request falls back to it
    return language if language in spec.languages else spec.languages[0]


def _render(source: str, ctx: dict, template_id: str) -> str:
    try:
        return _JINJA_ENV.from_string(source).render(**ctx)
    except UndefinedError as exc:
        raise MissingField(str(exc)) from exc
    except TemplateError as exc:  # pragma: no cover - malformed template source, not user input
        raise ValueError(f"template {template_id!r} block failed to render: {exc}") from exc


def _items(field_value, min_items: int) -> list[str]:
    lines = [ln.strip() for ln in str(field_value or "").splitlines() if ln.strip()]
    while len(lines) < min_items:
        lines.append("")
    return lines


def render_blocks(template_id: str, answers: dict, language: str) -> list:
    """The template resolved against `answers`: a list of RPara / RTable / RBreak."""
    spec = get_template(template_id)
    language = _effective_language(spec, language)
    ctx = _build_context(spec, answers)
    out: list = []
    for block in spec.paragraphs:
        if isinstance(block, PageBreak):
            out.append(RBreak())
        elif isinstance(block, Paragraph):
            source = block.text.get(language)
            if not source:
                continue
            if block.each:
                for n, item in enumerate(_items(ctx.get(block.each), block.min_items), 1):
                    sub = dict(ctx, item=item, n=n, ka=nepali.ka(n), ka_next=nepali.ka(n + 1))
                    text = _render(source, sub, template_id).strip()
                    label = _render(block.label, sub, template_id).strip() if block.label else None
                    if text or label:
                        out.append(_para(block, text, label, first=(n == 1)))
            else:
                text = _render(source, ctx, template_id).strip()
                label = _render(block.label, ctx, template_id).strip() if block.label else None
                if text or label:
                    out.append(_para(block, text, label, first=True))
        elif isinstance(block, Table):
            if block.lang and block.lang != language:
                continue
            rows = []
            for row in block.rows:
                if isinstance(row, RepeatRow):
                    contexts = [dict(ctx, item=it, n=n, ka=nepali.ka(n))
                                for n, it in enumerate(_items(ctx.get(row.each), row.min_items), 1)]
                    cell_rows = [(row.cells, c) for c in contexts]
                else:
                    cell_rows = [(row, ctx)]
                for cells, sub in cell_rows:
                    rrow = []
                    for cell in cells:
                        src = cell.text.get(language)
                        text = _render(src, sub, template_id).strip() if src else ""
                        rrow.append(nepali_cell(cell, text))
                    rows.append(rrow)
            out.append(RTable(rows=rows, widths=list(block.widths), borders=block.borders,
                              row_height=block.row_height, align=block.align, space_after=block.space_after,
                              size=block.size))
    return out


def nepali_cell(cell, text: str) -> RCell:
    return RCell(text=text, bold=cell.bold, align=cell.align, underline=cell.underline,
                 italic=cell.italic, valign=cell.valign)


def _para(block: Paragraph, text: str, label: str | None, first: bool) -> RPara:
    return RPara(
        text=text, bold=block.bold, align=block.align, underline=block.underline, italic=block.italic,
        indent=block.indent, hanging=block.hanging if label else 0.0, label=label, size=block.size,
        space_before=block.space_before, space_after=block.space_after, keep_next=block.keep_next,
        page_break_before=block.page_break_before and first,
    )


def render_paragraphs(template_id: str, answers: dict, language: str) -> list[tuple[str, bool, str]]:
    """[(text, bold, align), ...] for every non-empty paragraph of
    `template_id` rendered in `language` ("en" or "ne"). Table cell text is
    included (row by row) so callers can search the full rendered text."""
    out: list[tuple[str, bool, str]] = []
    for b in render_blocks(template_id, answers, language):
        if isinstance(b, RPara):
            out.append((strip_inline((b.label + " " if b.label else "") + b.text), b.bold, b.align))
        elif isinstance(b, RTable):
            for row in b.rows:
                for c in row:
                    if c.text:
                        out.append((strip_inline(c.text), c.bold, c.align))
    return out


def render_docx(template_id: str, answers: dict, language: str = "ne") -> bytes:
    from .docx_out import build_docx

    spec = get_template(template_id)
    blocks = render_blocks(template_id, answers, language)
    return build_docx(spec, blocks)


def render_pdf(template_id: str, answers: dict, language: str = "ne") -> bytes:
    from .pdf_out import build_pdf

    spec = get_template(template_id)
    blocks = render_blocks(template_id, answers, language)
    return build_pdf(spec, blocks, _effective_language(spec, language))


def render_file(template_id: str, answers: dict, language: str = "ne", fmt: str = "docx") -> tuple[bytes, str, str]:
    """(bytes, media_type, extension) for `fmt` in FORMATS."""
    if fmt == "docx":
        return (
            render_docx(template_id, answers, language),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "docx",
        )
    if fmt == "pdf":
        return render_pdf(template_id, answers, language), "application/pdf", "pdf"
    raise ValueError(f"format must be one of {FORMATS}")
