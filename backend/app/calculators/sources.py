"""Where every number in a calculator comes from.

Each calculator module lists its `SOURCES`: the corpus section a rule is read
from and a short verbatim phrase (as written in that section) that carries the
number. `verify_source()` re-reads the section and checks the phrase is there,
so a typo or a corpus change fails the tests instead of silently shipping a
wrong number. Results cite the section through `cite()` (which raises
UnresolvedProvision if the section is gone).
"""
from __future__ import annotations

import dataclasses

from ..playbooks import resolve_provision
from .limitation import normalise_text, section_text


@dataclasses.dataclass(frozen=True)
class Source:
    id: str
    law_title_ne: str
    section: str
    phrase_ne: str  # verbatim (whitespace-insensitive) text from the section that carries the number
    what: str  # what the number means, in plain English

    @property
    def ref(self) -> dict:
        return {"law_title_ne": self.law_title_ne, "section": self.section}


def cite(source: Source, note: dict | None = None) -> dict:
    """The resolved provision for a source, optionally with a per-use note."""
    ref = dict(source.ref)
    if note:
        ref["note"] = note
    return resolve_provision(ref)


def verify_source(source: Source) -> list[str]:
    """Problems (empty when fine) with one source."""
    text = section_text(source.law_title_ne, source.section)
    if text is None:
        return [f"{source.id}: {source.law_title_ne} {source.section} not found in the corpus"]
    if normalise_text(source.phrase_ne) not in normalise_text(text):
        return [f"{source.id}: phrase {source.phrase_ne!r} not found in {source.law_title_ne} {source.section}"]
    return []
