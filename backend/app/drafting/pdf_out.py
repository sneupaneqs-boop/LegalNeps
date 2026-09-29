"""Resolved layout blocks -> PDF, pure Python, no Word / LibreOffice needed.

PyMuPDF's `Story` lays out HTML with MuPDF's HarfBuzz shaper, so Devanagari
conjuncts, reph and matras come out correctly (a plain reportlab route cannot
shape Devanagari). The Noto Sans Devanagari TTFs bundled in `fonts/` (SIL OFL)
are embedded, so the output does not depend on fonts installed on the server.
Layout mirrors the DOCX: A4, same margins, alignment, indents, hanging labels,
tables and page breaks.
"""
from __future__ import annotations

import html
import io
import pathlib

import pymupdf

from .fields import TemplateSpec
from .inline import split_inline

FONT_DIR = pathlib.Path(__file__).parent / "fonts"

CM = 72.0 / 2.54
PAGE_W, PAGE_H = 595.28, 841.89  # A4 in pt
MARGIN = {"top": 2.5 * CM, "bottom": 2.5 * CM, "left": 2.7 * CM, "right": 2.3 * CM}
CONTENT_W = PAGE_W - MARGIN["left"] - MARGIN["right"]

_CSS = """
@font-face { font-family: 'NotoDeva'; src: url(NotoSansDevanagari-Regular.ttf); }
@font-face { font-family: 'NotoDeva'; font-weight: bold; src: url(NotoSansDevanagari-Bold.ttf); }
body { font-family: 'NotoDeva'; font-size: %(size)spt; line-height: 1.5; margin: 0; padding: 0; }
p { margin: 0; padding: 0; }
table { border-collapse: collapse; }
td { padding: 2pt 3pt; vertical-align: top; }
"""


def _txt(s: str) -> str:
    return html.escape(s).replace("\n", "<br>")


def _pstyle(p) -> str:
    st = [f"text-align:{p.align}"]
    before = p.space_before if p.space_before is not None else 0
    after = p.space_after if p.space_after is not None else 6
    st.append(f"margin-top:{before}pt")
    st.append(f"margin-bottom:{after}pt")
    if p.size:
        st.append(f"font-size:{p.size}pt")
    if p.page_break_before:
        st.append("page-break-before:always")
    return ";".join(st)


def _inline(text: str, bold: bool, underline: bool) -> str:
    pieces = []
    for seg, b, u in split_inline(text, bold, underline):
        out = _txt(seg)
        if u:
            out = f"<u>{out}</u>"
        if b:
            out = f"<b>{out}</b>"
        pieces.append(out)
    return "".join(pieces)


def _para_html(p) -> str:
    left = (p.indent or 0) * CM
    body = _inline(p.text, p.bold, p.underline) if p.text else "&nbsp;"
    if p.label:
        hang = max(p.hanging, 0.6) * CM
        label = _inline(p.label, p.bold, p.underline)
        text_w = max(CONTENT_W - left - hang, 40)
        before = p.space_before if p.space_before is not None else 0
        after = p.space_after if p.space_after is not None else 6
        # hanging label = a two-cell borderless table (MuPDF has no tab stops)
        return (
            f'<table style="margin-left:{left:.1f}pt;margin-top:{before}pt;margin-bottom:{after}pt;'
            f'width:{hang + text_w:.1f}pt"><tr>'
            f'<td style="width:{hang:.1f}pt;padding:0">{label}</td>'
            f'<td style="width:{text_w:.1f}pt;padding:0;text-align:{p.align}">{body}</td>'
            "</tr></table>"
        )
    style = _pstyle(p)
    if left:
        style += f";margin-left:{left:.1f}pt"
    return f'<p style="{style}">{body}</p>'


def _table_html(t) -> str:
    widths = [w * CM for w in t.widths]
    total = sum(widths)
    if total > CONTENT_W - 8:  # borders / cell padding add width in MuPDF: keep inside the margins
        widths = [w * (CONTENT_W - 8) / total for w in widths]
        total = sum(widths)
    if t.align == "right":
        margin = max(CONTENT_W - total - 3, 0)
    elif t.align == "center":
        margin = max((CONTENT_W - total) / 2, 0)
    else:
        margin = 0
    border = "border:0.75pt solid #000;" if t.borders == "all" else ""
    rows_html = []
    for r_idx, row in enumerate(t.rows):
        last = r_idx == len(t.rows) - 1
        height = f"height:{t.row_height * CM:.1f}pt;" if (t.row_height and last) else ""
        cells = []
        for c_idx, cell in enumerate(row):
            w = (widths[c_idx] if c_idx < len(widths) else 60) - 6.0  # td padding is 3pt each side
            cells.append(
                f'<td style="width:{w:.1f}pt;{height}{border}text-align:{cell.align}">'
                f"{_inline(cell.text, cell.bold, cell.underline) if cell.text else '&nbsp;'}</td>"
            )
        rows_html.append("<tr>" + "".join(cells) + "</tr>")
    fsize = f"font-size:{t.size}pt;" if t.size else ""
    return (
        f'<table style="{fsize}margin-left:{margin:.1f}pt;margin-bottom:4pt;width:{total:.1f}pt">'
        + "".join(rows_html) + "</table>"
    )


def build_html(blocks: list) -> str:
    from .render import RBreak, RPara, RTable

    parts = []
    pending_break = False
    for b in blocks:
        if isinstance(b, RBreak):
            pending_break = True
            continue
        if isinstance(b, RPara):
            if pending_break:
                b.page_break_before = True
                pending_break = False
            parts.append(_para_html(b))
        elif isinstance(b, RTable):
            parts.append(_table_html(b))
    return "<body>" + "".join(parts) + "</body>"


def build_pdf(spec: TemplateSpec, blocks: list, language: str = "ne") -> bytes:
    css = _CSS % {"size": max(spec.font_size - 0.5, 9)}
    story = pymupdf.Story(html=build_html(blocks), user_css=css, archive=pymupdf.Archive(str(FONT_DIR)))
    buf = io.BytesIO()
    writer = pymupdf.DocumentWriter(buf)
    mediabox = pymupdf.Rect(0, 0, PAGE_W, PAGE_H)
    where = pymupdf.Rect(MARGIN["left"], MARGIN["top"], PAGE_W - MARGIN["right"], PAGE_H - MARGIN["bottom"])
    more = 1
    while more:
        dev = writer.begin_page(mediabox)
        more, _ = story.place(where)
        story.draw(dev)
        writer.end_page()
    writer.close()
    data = buf.getvalue()
    # document metadata (title shows in the viewer's tab)
    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
        doc.set_metadata({
            "title": spec.title.get(language) or spec.title.get("ne") or spec.id,
            "author": "Kanooni Sathi",
            "producer": "Kanooni Sathi drafting",
        })
        out = doc.tobytes(garbage=3, deflate=True)
        doc.close()
        return out
    except Exception:  # noqa: BLE001 - metadata is cosmetic; never fail the export over it
        return data
