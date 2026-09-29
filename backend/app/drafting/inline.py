"""Inline emphasis inside a paragraph: **bold** and __underline__ (e.g. the
bold role word at the end of a party line: "... को राम श्रेष्ठ **बादी**")."""
from __future__ import annotations

import re

_TOKEN = re.compile(r"(\*\*|__)")


def split_inline(text: str, bold: bool = False, underline: bool = False) -> list[tuple[str, bool, bool]]:
    """[(segment, bold, underline), ...]; markers toggle the style and are dropped."""
    out: list[tuple[str, bool, bool]] = []
    b, u = bold, underline
    for part in _TOKEN.split(text):
        if part == "**":
            b = not b
        elif part == "__":
            u = not u
        elif part:
            out.append((part, b, u))
    return out or [("", bold, underline)]


def strip_inline(text: str) -> str:
    return _TOKEN.sub("", text)
