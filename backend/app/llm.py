"""Provider-agnostic LLM calls with model fallback.

Gemini is the primary provider: each call walks a chain of models and moves
on when one is rate-limited/unavailable, so a free-tier quota running out on
one model doesn't take the app down. Anthropic and Groq remain available as
alternative providers.
"""
from __future__ import annotations

import json
import logging
import re

from . import config

log = logging.getLogger(__name__)
_TRANSIENT = ("429", "RESOURCE_EXHAUSTED", "500", "502", "503", "504", "UNAVAILABLE", "DEADLINE", "timed out", "overloaded")


class LLMUnavailable(RuntimeError):
    pass


def available() -> bool:
    return bool(config.GEMINI_API_KEY or config.ANTHROPIC_API_KEY or config.GROQ_API_KEY)


_gemini_client = None
_no_thinking: set[str] = set()


def _gemini():
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        from google.genai import types

        _gemini_client = genai.Client(
            api_key=config.GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=config.LLM_TIMEOUT_S * 1000),
        )
    return _gemini_client


def _gemini_complete(models: list[str], system: str, user: str, json_mode: bool, max_tokens: int, temperature: float) -> str:
    from google.genai import types

    last = None
    for model in models:
        cfg = dict(
            system_instruction=system,
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        if json_mode:
            cfg["response_mime_type"] = "application/json"
        if "flash" in model and not model.startswith("gemini-2") and model not in _no_thinking:
            cfg["thinking_config"] = types.ThinkingConfig(thinking_budget=0 if json_mode else 512)
        for attempt in range(2):
            try:
                r = _gemini().models.generate_content(
                    model=model, contents=user, config=types.GenerateContentConfig(**cfg)
                )
                text = (r.text or "").strip()
                if text:
                    return text
                last = LLMUnavailable(f"{model}: empty response")
                break
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                last = e
                if "thinking_config" in cfg and ("thinking" in msg.lower() or "INVALID_ARGUMENT" in msg):
                    cfg.pop("thinking_config")  # model doesn't accept a thinking budget: retry without
                    _no_thinking.add(model)
                    continue
                if any(t in msg for t in _TRANSIENT):
                    # quota / overload: the next model in the chain is the fastest recovery
                    log.warning("gemini %s unavailable: %s", model, msg[:120])
                    break
                log.warning("gemini %s failed: %s", model, msg[:200])
                break
    raise LLMUnavailable(str(last)[:300] if last else "no gemini model available")


def _anthropic_complete(system: str, user: str, max_tokens: int, temperature: float) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY, timeout=config.LLM_TIMEOUT_S)
    r = client.messages.create(
        model=config.ANTHROPIC_MODEL, max_tokens=max_tokens, temperature=temperature,
        system=system, messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in r.content if b.type == "text").strip()


def _groq_complete(system: str, user: str, json_mode: bool, max_tokens: int, temperature: float) -> str:
    from groq import Groq

    client = Groq(api_key=config.GROQ_API_KEY, timeout=config.LLM_TIMEOUT_S)
    kw = {"response_format": {"type": "json_object"}} if json_mode else {}
    r = client.chat.completions.create(
        model=config.GROQ_MODEL, max_tokens=max_tokens, temperature=temperature,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}], **kw,
    )
    return (r.choices[0].message.content or "").strip()


def complete(system: str, user: str, *, fast: bool = False, json_mode: bool = False,
             max_tokens: int = 1400, temperature: float = 0.2) -> str:
    errors = []
    if config.GEMINI_API_KEY:
        models = config.GEMINI_FAST_MODELS if fast else config.GEMINI_MODELS
        try:
            return _gemini_complete(models, system, user, json_mode, max_tokens, temperature)
        except Exception as e:  # noqa: BLE001
            errors.append(f"gemini: {e}")
    if config.ANTHROPIC_API_KEY:
        try:
            return _anthropic_complete(system, user, max_tokens, temperature)
        except Exception as e:  # noqa: BLE001
            errors.append(f"anthropic: {e}")
    if config.GROQ_API_KEY:
        try:
            return _groq_complete(system, user, json_mode, max_tokens, temperature)
        except Exception as e:  # noqa: BLE001
            errors.append(f"groq: {e}")
    raise LLMUnavailable("; ".join(errors) or "no LLM provider configured")


def parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, flags=re.S)
        if m:
            return json.loads(m.group(0))
        raise
