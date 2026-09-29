"""LLM-assisted drafting for free-text fields (S10).

Only `textarea` fields go through the LLM - short single-line fields
(names, dates, amounts) are exactly the kind of thing a user just types, and
running them through a model would add latency and hallucination risk for
no benefit. The LLM only expands the user's own short hint into fuller
legal-notice-style prose in the target language; it never invents statute
citations or facts not implied by the hint - those come from the template's
own (corpus-verified) paragraphs, never from this free-text fill.

Tiered per STRATEGY's S10 requirement: uses the `fast` (cheap/low-latency)
model tier, since expanding one field's text is a bounded, low-stakes task,
not the kind of long-form reasoning the answer tier is for.
"""
from __future__ import annotations

from .. import llm, prompt_guard, tiers
from .fields import TemplateSpec
from .registry import TEMPLATES

# S13: bump when _SYSTEM's wording changes materially.
PROMPT_VERSION = "ai_fill_v1"

_SYSTEM = {
    "en": (
        "You help a layperson draft one section of a legal document in Nepal. "
        "Expand their short note into 2-4 clear, formal sentences in English "
        "suitable for the document section described. Stick to what they told "
        "you - do not invent names, dates, amounts, or legal citations that "
        "were not given to you. Output only the expanded text, no preamble."
    ),
    "ne": (
        "तपाईं नेपालमा कानूनी कागजातको एउटा खण्ड मस्यौदा गर्न सामान्य प्रयोगकर्तालाई "
        "सहयोग गर्नुहुन्छ। दिइएको छोटो टिप्पणीलाई वर्णन गरिएको खण्डका लागि उपयुक्त "
        "२-४ स्पष्ट, औपचारिक नेपाली वाक्यमा विस्तार गर्नुहोस्। दिइएको जानकारीमै सीमित "
        "रहनुहोस् - नदिइएको नाम, मिति, रकम, वा कानूनी दफा नबनाउनुहोस्। विस्तारित पाठ "
        "मात्र दिनुहोस्, कुनै भूमिका नलेख्नुहोस्।"
    ),
}


class UnknownField(ValueError):
    pass


def _get_field(spec: TemplateSpec, field_id: str):
    for f in spec.fields:
        if f.id == field_id:
            return f
    raise UnknownField(f"{field_id!r} is not a field of template {spec.id!r}")


def _build(template_id: str, field_id: str, hint: str, language: str, other_answers: dict | None) -> tuple[str, str]:
    """Returns (system, user) for the given field, or raises ValueError /
    UnknownField. `hint` is wrapped as untrusted user text (S13) - it's the
    one place free-form user input enters this prompt."""
    if language not in ("en", "ne"):
        raise ValueError("language must be 'en' or 'ne'")
    spec = TEMPLATES.get(template_id)
    if spec is None:
        raise UnknownField(f"{template_id!r} is not a known drafting template")
    field = _get_field(spec, field_id)
    if field.type != "textarea":
        raise UnknownField(f"{field_id!r} is not a free-text field; AI fill is only for textarea fields")

    label = field.label.get(language, field.label.get("en", field_id))
    context_lines = []
    if other_answers:
        for f in spec.fields:
            if f.id in other_answers and other_answers[f.id] and f.type != "textarea":
                context_lines.append(f"{f.label.get(language, f.id)}: {other_answers[f.id]}")
    context_block = ("\n".join(context_lines) + "\n\n") if context_lines else ""
    wrapped_hint = prompt_guard.wrap_user_text(hint)

    user = (
        f"{context_block}Document section: {label}\nUser's note: {wrapped_hint}"
        if language == "en"
        else f"{context_block}कागजातको खण्डः {label}\nप्रयोगकर्ताको टिप्पणीः {wrapped_hint}"
    )
    system = _SYSTEM[language] + "\n\n" + prompt_guard.UNTRUSTED_TEXT_NOTICE
    return system, user


def fill(template_id: str, field_id: str, hint: str, language: str = "ne", other_answers: dict | None = None) -> str:
    """Expand `hint` into fuller prose for `field_id` of `template_id`, in
    `language`, via the free chain. Raises UnknownField for a bad field id,
    llm.LLMUnavailable if no provider answers in time - callers should fall
    back to using `hint` verbatim on that error, not fail the whole draft."""
    system, user = _build(template_id, field_id, hint, language, other_answers)
    text = llm.complete(system, user, fast=True, max_tokens=400, temperature=0.3)
    return text.strip()


def fill_paid(template_id: str, field_id: str, hint: str, language: str, other_answers: dict | None,
              tier: str) -> tuple[str, dict]:
    """S13: same expansion, billed to a specific paid-tier model
    (tiers.select_tier(plan, "draft") picks "sonnet" for any paid plan).
    Returns (text, usage) so the caller can log a real cost per query."""
    system, user = _build(template_id, field_id, hint, language, other_answers)
    model = tiers.model_for_tier(tier)
    text, usage = llm.paid_complete(model, system, user, max_tokens=800, temperature=0.3)
    return text.strip(), usage
