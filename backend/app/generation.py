from typing import List, Literal

from . import config

DISCLAIMER_EN = (
    "This is general legal information, not a substitute for advice from a "
    "licensed Nepali advocate. For anything urgent or high-stakes, please "
    "consult a lawyer."
)
DISCLAIMER_NE = (
    "यो सामान्य कानुनी जानकारी मात्र हो, इजाजतपत्रप्राप्त अधिवक्ताको सल्लाहको विकल्प होइन। "
    "जरुरी वा महत्वपूर्ण विषयमा कृपया वकिलसँग सम्पर्क गर्नुहोस्।"
)

SYSTEM_PROMPT = """You are Kanooni Sathi ("Legal Friend"), a warm, patient bilingual \
(English/Nepali) legal-information assistant focused on Nepali law, primarily civil \
law for this prototype.

How to behave:
- First understand the person's real underlying concern, not just the literal words \
they typed. People often describe a life situation (a fight with a landlord, an \
abusive marriage, a business partner who won't pay) rather than a legal term. \
Restate their concern briefly in plain language before answering, so they feel heard.
- Answer using ONLY the "Retrieved context" passages given to you below as your legal \
grounding. Do not invent section numbers, case names, or citations that are not in \
the retrieved context. If the retrieved context does not cover the question, say so \
honestly and give only general, cautious guidance.
- Explain things the way a knowledgeable friend would to someone with no legal \
training: short sentences, no unexplained jargon, concrete next steps (e.g. which \
office or court to approach) when the context supports it.
- Reply in the SAME language as requested (English or Nepali). If Nepali, write in \
natural Nepali (Devanagari), not machine-translated-sounding text.
- Always end with one short empathetic line and the standard disclaimer that this is \
general information, not a substitute for a licensed advocate.
- Never claim certainty about the outcome of a specific case. Encourage the person to \
consult a lawyer for anything urgent, high-stakes, or fact-sensitive.
"""


def _format_context(sources: List[dict], lang: Literal["en", "ne"]) -> str:
    blocks = []
    for s in sources:
        title = s["title_en"] if lang == "en" else s["title_ne"]
        text = s["text_en"] if lang == "en" else s["text_ne"]
        citation = s["source_en"] if lang == "en" else s["source_ne"]
        blocks.append(f"[{s['id']}] {title}\nCitation: {citation}\n{text}")
    return "\n\n".join(blocks)


def _extractive_fallback(message: str, sources: List[dict], lang: Literal["en", "ne"]) -> str:
    """Used when no ANTHROPIC_API_KEY is configured, so the app still works."""
    lines = []
    header = (
        "I couldn't reach the AI model, so here are the most relevant passages I found:"
        if lang == "en"
        else "AI मोडेलसँग जडान हुन सकेन, तर सबैभन्दा मिल्दो जानकारी यहाँ छ:"
    )
    lines.append(header)
    for s in sources:
        title = s["title_en"] if lang == "en" else s["title_ne"]
        text = s["text_en"] if lang == "en" else s["text_ne"]
        citation = s["source_en"] if lang == "en" else s["source_ne"]
        lines.append(f"\n**{title}** ({citation})\n{text}")
    lines.append("\n" + (DISCLAIMER_EN if lang == "en" else DISCLAIMER_NE))
    return "\n".join(lines)


def generate_answer(message: str, sources: List[dict], lang: Literal["en", "ne"]) -> tuple[str, bool]:
    if not config.ANTHROPIC_API_KEY:
        return _extractive_fallback(message, sources, lang), False

    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    context = _format_context(sources, lang)
    lang_instruction = "Reply in English." if lang == "en" else "Reply in Nepali (Devanagari script)."

    user_content = (
        f"Retrieved context:\n{context}\n\n"
        f"Person's message: {message}\n\n"
        f"{lang_instruction}"
    )

    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    answer = "".join(block.text for block in response.content if block.type == "text")
    return answer, True
