"""A tiny line-oriented markup for writing prescribed forms compactly, so the
template source reads like the official schedule it transcribes.

    @cbu फिरादपत्र                  centred, bold, underlined paragraph
    @r अदालतले भर्ने                right-aligned
    @l>8 दर्ता नं. {{ reg|blank }}  left-aligned, indented 8 cm (a "court fills this" box)
    @l १.|म/हामी ... गर्दछु ।       numbered item: label "१." hangs, text wraps under itself
    @l,>1 ({{ ka }})|{{ item }}     (with ,each=claims:3 -> one paragraph per line of `claims`, >= 3)
    @j तपाईंले ...                  justified
    plain text                      left-aligned paragraph

Flags (comma separated, or run together when single letters):
  c r l j      alignment                     b u i    bold / underline / italic
  ^            keep with next                +        12pt space before
  >N           left indent N cm              hN       hanging indent N cm for a label (default 1.0)
  sN           font size N pt                aN       space after N pt
  pb           page break before             each=FIELD:MIN   repeat per line of a textarea answer

Blocks:
    @table 8,8 none [h=2] [align=right] [size=9]   widths in cm; borders none|all; h = height of the last row
    | @r cell one | @b cell two |             one row per line, cells split on `|`;  <br> = line break
    @rows FIELD:MIN                           (before a row) repeat that row per line of a textarea answer
    @end
    @thumbs [align=left] [label=...]        the दायाँ / बायाँ thumbprint table (label = caption, last on the line)
    @pagebreak
Inline (inside any text): **bold** and __underline__.
Lines starting with `#` are comments; blank lines are ignored.
"""
from __future__ import annotations

import re

from .fields import Cell, Field, PageBreak, Paragraph, RepeatRow, Table

_LETTERS = set("crljbui^+")


def _split_top(s: str, sep: str) -> list[str]:
    """Split on `sep` ignoring separators inside {{ }} / {% %}."""
    out, cur, i, depth = [], [], 0, 0
    while i < len(s):
        two = s[i:i + 2]
        if two in ("{{", "{%"):
            depth += 1
            cur.append(two)
            i += 2
            continue
        if two in ("}}", "%}"):
            depth = max(0, depth - 1)
            cur.append(two)
            i += 2
            continue
        if s[i] == sep and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(s[i])
        i += 1
    out.append("".join(cur))
    return out


def _flags(tok: str) -> dict:
    kw: dict = {}
    for part in tok.split(","):
        part = part.strip()
        if not part:
            continue
        if part.startswith("each="):
            name, _, mn = part[5:].partition(":")
            kw["each"] = name
            kw["min_items"] = int(mn) if mn else 0
        elif part == "pb":
            kw["page_break_before"] = True
        elif part.startswith(">"):
            kw["indent"] = float(part[1:])
        elif part[0] == "h" and re.fullmatch(r"h[\d.]+", part):
            kw["hanging"] = float(part[1:])
        elif part[0] == "s" and re.fullmatch(r"s[\d.]+", part):
            kw["size"] = float(part[1:])
        elif part[0] == "a" and re.fullmatch(r"a[\d.]+", part):
            kw["space_after"] = float(part[1:])
        elif set(part) <= _LETTERS:
            for ch in part:
                if ch == "c":
                    kw["align"] = "center"
                elif ch == "r":
                    kw["align"] = "right"
                elif ch == "l":
                    kw["align"] = "left"
                elif ch == "j":
                    kw["align"] = "justify"
                elif ch == "b":
                    kw["bold"] = True
                elif ch == "u":
                    kw["underline"] = True
                elif ch == "i":
                    kw["italic"] = True
                elif ch == "^":
                    kw["keep_next"] = True
                elif ch == "+":
                    kw["space_before"] = 12.0
        else:
            raise ValueError(f"unknown drafting-markup flag {part!r}")
    return kw


def _split_flags(line: str) -> tuple[dict, str]:
    """`@flags rest` -> (flags, rest); a line without a leading @ has no flags."""
    if not line.startswith("@"):
        return {}, line
    tok, _, rest = line[1:].partition(" ")
    return _flags(tok), rest


def _label_split(text: str) -> tuple[str | None, str]:
    parts = _split_top(text, "|")
    if len(parts) > 1:
        head = parts[0]
        stripped = re.sub(r"\{\{.*?\}\}|\{%.*?%\}", "X", head)
        if len(stripped) <= 14 and " " not in stripped and stripped:
            return head, "|".join(parts[1:]).lstrip(" ")
    return None, text


def _paragraph(line: str, lang: str) -> Paragraph:
    kw, text = _split_flags(line)
    label, text = _label_split(text)
    if label is not None and "hanging" not in kw:
        kw["hanging"] = 1.0
    return Paragraph({lang: text}, label=label, **kw)


def _cell(raw: str, lang: str) -> Cell:
    raw = raw.strip()
    kw, text = _split_flags(raw)
    if "align" not in kw:
        kw["align"] = "left"
    kw.pop("size", None)
    for k in ("indent", "hanging", "space_after", "space_before", "keep_next", "page_break_before",
              "each", "min_items"):
        kw.pop(k, None)
    valign = "top"
    if kw.pop("bold", False):
        kw["bold"] = True
    return Cell({lang: text.replace("<br>", "\n")}, valign=valign, **kw)


def thumbs_table(lang: str = "ne", align: str = "left", label: str | None = None) -> list:
    """The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a
    bordered दायाँ / बायाँ two-box table with a tall empty row for the prints."""
    default = "Thumbprints" if lang == "en" else "ल्याप्चे सहीछाप"
    caption = Paragraph({lang: label or default}, bold=True, keep_next=True, space_before=6, align=align)
    right, left = ("Right", "Left") if lang == "en" else ("दायाँ", "बायाँ")
    table = Table(
        rows=[
            [Cell({lang: right}, align="center", bold=True), Cell({lang: left}, align="center", bold=True)],
            [Cell({lang: ""}), Cell({lang: ""})],
        ],
        widths=[3.4, 3.4],
        borders="all",
        row_height=2.4,  # applies to the last (print) row; the header row stays compact
        align=align,
        lang=lang,
    )
    return [caption, table]


def doc(src: str, lang: str = "ne") -> list:
    """Parse the markup above into a block list for `TemplateSpec.paragraphs`."""
    blocks: list = []
    lines = src.strip("\n").split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        line = line.strip()
        if line.startswith("@pagebreak"):
            blocks.append(PageBreak())
        elif line.startswith("@thumbs"):
            align, label = "left", None
            m = re.search(r"align=(\w+)", line)
            if m:
                align = m.group(1)
            m = re.search(r"label=(.*)$", line)
            if m:
                label = m.group(1).strip()
            blocks.extend(thumbs_table(lang, align, label))
        elif line.startswith("@table"):
            args = line.split()[1:]
            widths = [float(x) for x in args[0].split(",")]
            borders, height, align, tsize = "none", None, "left", None
            for a in args[1:]:
                if a in ("none", "all"):
                    borders = a
                elif a.startswith("h="):
                    height = float(a[2:])
                elif a.startswith("align="):
                    align = a[6:]
                elif a.startswith("size="):
                    tsize = float(a[5:])
            rows = []
            pending = None  # (field, min) set by an `@rows FIELD:MIN` line for the next row
            while i < len(lines) and not lines[i].strip().startswith("@end"):
                row = lines[i].strip()
                i += 1
                if not row or row.startswith("#"):
                    continue
                if row.startswith("@rows"):
                    name, _, mn = row.split()[1].partition(":")
                    pending = (name, int(mn or 0))
                    continue
                if not row.startswith("|"):
                    raise ValueError(f"table row must start with '|': {row!r}")
                cells = _split_top(row, "|")[1:-1] if row.endswith("|") else _split_top(row, "|")[1:]
                parsed = [_cell(c, lang) for c in cells]
                rows.append(RepeatRow(parsed, *pending) if pending else parsed)
                pending = None
            i += 1  # @end
            blocks.append(Table(rows=rows, widths=widths, borders=borders, row_height=height, align=align, size=tsize, lang=lang))
        else:
            blocks.append(_paragraph(line, lang))
    return blocks


def F(id: str, en: str, ne: str, type: str = "text", required: bool = False,
      help_en: str | None = None, help_ne: str | None = None, default=None,
      options: list | None = None) -> Field:
    """Compact Field builder; fields on prescribed forms are optional by
    default because an unfilled blank is printed as a dotted line."""
    help_ = {"en": help_en, "ne": help_ne} if (help_en or help_ne) else None
    if help_ and not help_["en"]:
        help_["en"] = help_["ne"]
    if help_ and not help_["ne"]:
        help_["ne"] = help_["en"]
    return Field(id, {"en": en, "ne": ne}, type, required, help_, default, options)


def SELECT(id: str, en: str, ne: str, choices: list[str], required: bool = False,
           help_en: str | None = None, help_ne: str | None = None) -> Field:
    """A select field whose options are Nepali words shown in both languages."""
    opts = [{"value": c, "label": {"en": c, "ne": c}} for c in choices]
    return F(id, en, ne, "select", required, help_en, help_ne, None, opts)
