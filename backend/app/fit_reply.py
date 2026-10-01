"""V3.3: what the user sees when the topical-fit gate leaves too little to answer from.

  abstain_answer   "I couldn't find a provision that directly answers this in the sources" + at most FIT_RELATED_MAX
                   closest statute passages, each labelled "possibly related", + the curated plan's forum/steps
  extractive_answer the provisions themselves (fallback when no summary could be verified), filtered by the same gate
                   and followed by one plain sentence on whether they directly govern the question
  relabel_subsections  a citation label must not name a sub-section the passage does not start at

Pure functions over the source dicts `generation.apply_topical_gate` has marked (`off_topic`, `off_topic_why`,
`fit_score`).
"""
from __future__ import annotations

import re

from . import config
from .text_norm import DEV_DIGITS

ABSTAIN = {
    "en": {"lead": "I couldn't find a provision that directly answers this in the sources I searched, so I won't guess "
                   "at an answer.",
           "related": "Possibly related (I could not confirm these govern your situation)",
           "forum": "Where to go", "steps": "General next steps (from our action plan, not a legal source)"},
    "ne": {"lead": "मैले खोजेका स्रोतहरूमा तपाईंको प्रश्नको सिधै जवाफ दिने प्रावधान भेटिएन, त्यसैले अनुमान गरेर जवाफ दिइरहेको छैन।",
           "related": "सम्भावित रूपमा सम्बन्धित (तपाईंको अवस्थामा लागू हुन्छ भन्ने पुष्टि भएको छैन)",
           "forum": "कहाँ जाने", "steps": "सामान्य अर्को कदम (हाम्रो कार्ययोजनाबाट, कानुनी स्रोत होइन)"},
}
DIRECT_NOTE = {
    "en": "These provisions match the subject of your question, but I could not confirm that they directly govern your "
          "exact situation.",
    "ne": "यी प्रावधानहरू तपाईंको प्रश्नको विषयसँग मिल्छन्, तर तपाईंको ठ्याक्कै अवस्थामा सिधै लागू हुन्छन् भन्ने पुष्टि गर्न सकिएन।",
}
# V2.7: the "matches the subject" sentence is only printed when the shown provisions pass the STRICT fit check
# (topical_fit.direct_fit); otherwise the reader is told plainly that these are merely the closest found
PARTIAL_NOTE = {
    "en": "Only {nums} clearly match the subject of your question; the others are the closest I found and may not apply to "
          "your situation. I could not confirm that any of them directly governs your exact situation.",
    "ne": "{nums} मात्र तपाईंको प्रश्नको विषयसँग स्पष्ट रूपमा मिल्छन्; बाँकी मैले भेटेका सबैभन्दा नजिकका प्रावधान हुन् र तपाईंको "
          "अवस्थामा लागू नहुन सक्छन्। तपाईंको ठ्याक्कै अवस्थामा कुनै सिधै लागू हुन्छ भन्ने पुष्टि गर्न सकिएन।",
}
CLOSEST_NOTE = {
    "en": "These are the closest provisions I found. They may not apply to your situation, and I could not find one that "
          "clearly matches the subject of your question.",
    "ne": "यी मैले भेटेका सबैभन्दा नजिकका प्रावधान हुन्। तपाईंको अवस्थामा यी लागू नहुन सक्छन्, र तपाईंको प्रश्नको विषयसँग स्पष्ट "
          "रूपमा मिल्ने प्रावधान मैले भेटिनँ।",
}
_EXTRACTIVE_HEADER = {
    "en": "Here are the most relevant official provisions I found (AI summary unavailable right now):",
    "ne": "सबैभन्दा सान्दर्भिक आधिकारिक कानुनी प्रावधानहरू (AI सारांश अहिले उपलब्ध छैन):",
}


def on_topic_laws(sources: list[dict]) -> list[dict]:
    return [s for s in sources if s.get("category") != "precedent" and not s.get("off_topic")]


def gate_ran(sources: list[dict]) -> bool:
    return any("fit_score" in s for s in sources)


def direct_laws(sources: list[dict]) -> list[dict]:
    """On-topic statute passages that also pass the strict fit check (verified, or the law the question names, or a
    heading that covers its terms)."""
    return [s for s in on_topic_laws(sources) if s.get("fit_direct") or s.get("pinned")]


def related_candidates(sources: list[dict], limit: int | None = None) -> list[tuple[int, dict]]:
    """(number, source) of the closest statute passages the gate did not rule out by REGIME (a passage from the
    army / postal / hire-purchase chapter is known to be the wrong kind of law and is never offered as "related").
    Closest = lowest off-topic score, then retrieval rank; returned in source order."""
    limit = config.FIT_RELATED_MAX if limit is None else limit
    cand = [(i, s) for i, s in enumerate(sources, 1)
            if s.get("category") != "precedent"
            and not any(str(w).startswith(("specialist:", "non_substantive:")) for w in s.get("off_topic_why") or [])]
    cand.sort(key=lambda x: (x[1].get("fit_score", 0.0), x[0]))
    return sorted(cand[:limit])


def _excerpt(s: dict, lang: str, limit: int = 260) -> str:
    text = " ".join(str((s.get("text_en") if lang == "en" and s.get("text_en") else s.get("text_ne")) or "").split())
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + " …"


def _cite(s: dict, lang: str) -> str:
    return (s.get("source_en") if lang == "en" and s.get("source_en") else s.get("source_ne")) or ""


def abstain_answer(sources: list[dict], lang: str, disclaimer: str, playbook: dict | None = None) -> str:
    key = "en" if lang == "en" else "ne"
    t = ABSTAIN[key]
    parts = [t["lead"]]
    rel = related_candidates(sources)
    if rel:
        parts.append(f"**{t['related']}**\n" + "\n".join(f"- **[{k}] {_cite(s, lang)}**: {_excerpt(s, lang)}" for k, (_, s) in enumerate(rel, 1)))
    if playbook:
        forum = (playbook.get("forum") or {}).get(key) or (playbook.get("forum") or {}).get("en") or ""
        steps = [x for x in ((st.get(key) or st.get("en")) for st in playbook.get("next_steps", [])) if x]
        if forum:
            parts.append(f"**{t['forum']}**\n{forum}")
        if steps:
            parts.append(f"**{t['steps']}**\n" + "\n".join(f"- {x}" for x in steps))
    parts.append(disclaimer)
    return "\n\n".join(parts)


def extractive_answer(sources: list[dict], lang: str, disclaimer: str, header: str | None = None,
                      playbook: dict | None = None) -> str:
    """The provisions themselves. With the gate: only passages that passed it (V3.2 review: copyright, land
    acquisition and pesticide rules showed up here), at most 3, statutes first, then one plain sentence saying they
    match the subject but were not confirmed to govern the exact situation; nothing passing = the abstain reply.
    Without the gate (off / no model): the V3.2 list of the first 5."""
    key = "en" if lang == "en" else "ne"
    gated = gate_ran(sources)
    note = None
    if gated:
        if not on_topic_laws(sources):
            return abstain_answer(sources, lang, disclaimer, playbook)
        ok = [(i, s) for i, s in enumerate(sources, 1) if not s.get("off_topic")]
        laws = [x for x in ok if x[1].get("category") != "precedent"]
        precs = [x for x in ok if x[1].get("category") == "precedent"]
        if config.FIT_ABSTAIN_STRICT and not direct_laws(sources):
            # V3.3 live review: 4 of 11 fallbacks listed wholly unrelated provisions under "these match the subject"
            return abstain_answer(sources, lang, disclaimer, playbook)
        # directly fitting passages first (each group keeps retrieval order), then the rest; statutes before precedents
        laws = [x for x in laws if x[1].get("fit_direct") or x[1].get("pinned")] + \
               [x for x in laws if not (x[1].get("fit_direct") or x[1].get("pinned"))]
        shown = (laws + precs)[:3]
        n_direct = sum(1 for _, s in shown if s.get("fit_direct") or s.get("pinned"))
        if n_direct == len(shown):
            note = DIRECT_NOTE[key]
        elif n_direct:
            nums = ", ".join(f"[{k}]" for k, (_, s) in enumerate(shown, 1) if s.get("fit_direct") or s.get("pinned"))
            note = PARTIAL_NOTE[key].format(nums=nums)
        else:
            note = CLOSEST_NOTE[key]
    else:
        shown = list(enumerate(sources[:5], 1))
    lines = [header or _EXTRACTIVE_HEADER[key]]
    # the labels shown are 1..n in display order (the source list's own numbers skip the passages the gate removed)
    for k, (i, s) in enumerate(shown, 1):
        text = (s.get("text_en") if lang == "en" and s.get("text_en") else s.get("text_ne")) or ""
        lines.append(f"\n**[{k}] {_cite(s, lang)}**\n{text[:700]}")
    if note:
        lines.append("\n" + note)
    lines.append("\n" + disclaimer)
    return "\n".join(lines)


_SUB_LABEL = re.compile(r"\s*\(\s*([०-९0-9]{1,2})\s*\)\s*$")
_SUB_MARK = re.compile(r"^[ \t÷]*\(\s*([०-९0-9]{1,2})\s*\)", re.M)


def relabel_subsections(sources: list[dict]) -> None:
    """The corpus files a long section under its FIRST sub-section ("दफा 10 (1)") although the passage holds
    (1)-(3): a citation label must never name a sub-section the quote is not in (V3.2 review: a17, a20). A chunk
    that opens at sub-section k and holds up to m > k is labelled with the range it holds: "दफा 10 (1)-(3)"."""
    for s in sources:
        m = _SUB_LABEL.search(str(s.get("source_ne") or ""))
        if not m:
            continue
        k = int(m.group(1).translate(DEV_DIGITS))
        marks = [int(x.translate(DEV_DIGITS)) for x in _SUB_MARK.findall(str(s.get("text_ne") or ""))]
        top = max((x for x in marks if x < 40), default=k)
        if top > k:
            for key in ("source_ne", "source_en"):
                if s.get(key):
                    s[key] = _SUB_LABEL.sub(f" ({k})–({top})", str(s[key]))
