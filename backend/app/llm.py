"""Provider-agnostic LLM calls with tiered models, fallback and hard deadlines.

Providers are tried in order until one answers, each call bounded by a time
budget so a slow or rate-limited provider can never leave the UI "thinking":

1. OpenAI-compatible gateway (OPENAI_BASE_URL) - e.g. a self-hosted OmniRoute
   (http://localhost:20128/v1) that fans out over many providers' free tiers
   with its own fallback, or OpenRouter/Groq/any compatible API.
2. Gemini (GEMINI_API_KEY) - walks a chain of models; per-model cooldowns on
   429/503 because each model has its own (small, on free tier) quota.
3. Anthropic, 4. Groq.

Two tiers everywhere: `fast=True` (query understanding - cheap, low latency)
and the answer tier (stronger model, still cheapest that does the job).
"""
from __future__ import annotations

import json
import logging
import re
import threading
import time

from . import config

log = logging.getLogger(__name__)
_TRANSIENT = ("429", "RESOURCE_EXHAUSTED", "500", "502", "503", "504", "UNAVAILABLE", "DEADLINE",
              "timed out", "timeout", "overloaded", "Timeout")


class LLMUnavailable(RuntimeError):
    pass


def available() -> bool:
    return bool(config.OPENAI_BASE_URL or config.GEMINI_API_KEY or config.ANTHROPIC_API_KEY or config.GROQ_API_KEY)


_cooldown: dict[str, float] = {}  # "provider:model" -> unix time until which it's skipped
_no_thinking: set[str] = set()
_client_lock = threading.Lock()
_gemini_client = None
_http = None


def _cool(key: str, msg: str):
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "rate" in msg.lower():
        m = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+(?:\.\d+)?)s", msg)
        delay = float(m.group(1)) if m else 30.0
        if "PerDay" in msg:
            delay = max(delay, 3600.0)
        _cooldown[key] = time.time() + min(delay, 6 * 3600)
    else:
        _cooldown[key] = time.time() + 20  # overloaded / timed out: brief pause


def _ready(prefix: str, models: list[str]) -> list[str]:
    now = time.time()
    ok = [m for m in models if _cooldown.get(f"{prefix}:{m}", 0) <= now]
    return ok or models[-1:]  # everything cooling down: still try the last-resort model


# ---------------------------------------------------------------- OpenAI-compatible (OmniRoute etc.)
def _client_http():
    global _http
    if _http is None:
        with _client_lock:
            if _http is None:
                import httpx

                _http = httpx.Client(timeout=config.LLM_TIMEOUT_S)
    return _http


def _openai_payload(model, system, user, json_mode, max_tokens, temperature, stream=False, fast=False):
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": stream,
    }
    effort = _reasoning_effort(model)
    if effort:
        body["reasoning_effort"] = effort
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    return body


def _reasoning_effort(model: str) -> str | None:
    """Hidden "thinking" adds seconds (and can leak into the text); grounded
    answers from retrieved passages don't need it. Providers disagree on the
    allowed values, so set it per model family."""
    m = model.lower()
    if "gpt-oss" in m:
        return "low"  # gpt-oss rejects "none"
    if m.startswith(("gemini/", "gemini-")) or "qwen3" in m:
        return "none"
    return None


def _text_of(content) -> str:
    """Gateways return content as a string or as a list of typed parts."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(p.get("text", "") for p in content if isinstance(p, dict) and p.get("type", "text") == "text")
    return ""


def _openai_headers():
    h = {"Content-Type": "application/json"}
    if config.OPENAI_API_KEY:
        h["Authorization"] = f"Bearer {config.OPENAI_API_KEY}"
    return h


def _openai_complete(models, system, user, json_mode, max_tokens, temperature, deadline, fast=False) -> str:
    last = None
    for model in _ready("openai", models):
        left = deadline - time.time()
        if left < 2:
            break
        try:
            r = _client_http().post(
                f"{config.OPENAI_BASE_URL.rstrip('/')}/chat/completions",
                json=_openai_payload(model, system, user, json_mode, max_tokens, temperature, fast=fast),
                headers=_openai_headers(), timeout=min(left, config.LLM_CALL_TIMEOUT_S),
            )
            if r.status_code >= 400:
                raise LLMUnavailable(f"{r.status_code} {r.text[:200]}")
            text = _text_of(r.json()["choices"][0]["message"].get("content")).strip()
            if text:
                return text
            last = LLMUnavailable(f"{model}: empty response")
        except Exception as e:  # noqa: BLE001
            last = e
            log.warning("openai-compatible %s failed: %s", model, str(e)[:160])
            _cool(f"openai:{model}", str(e))
    raise LLMUnavailable(str(last)[:300] if last else "openai-compatible: no time left")


def _openai_stream(models, system, user, max_tokens, temperature, first_token_deadline):
    for model in _ready("openai", models):
        left = first_token_deadline - time.time()
        if left < 2:
            return
        # a model that keeps the stream alive with reasoning chunks but no text
        # must not eat the whole budget
        model_deadline = time.time() + min(left, config.MODEL_FIRST_TOKEN_S)
        emitted = False
        try:
            import httpx

            timeout = httpx.Timeout(config.LLM_TIMEOUT_S, connect=min(left, 10),
                                    read=min(left, config.MODEL_FIRST_TOKEN_S + 2))
            with _client_http().stream(
                "POST", f"{config.OPENAI_BASE_URL.rstrip('/')}/chat/completions",
                json=_openai_payload(model, system, user, False, max_tokens, temperature, stream=True),
                headers=_openai_headers(), timeout=timeout,
            ) as r:
                if r.status_code >= 400:
                    raise LLMUnavailable(f"{r.status_code} {r.read()[:200]!r}")
                for line in r.iter_lines():
                    if not emitted and time.time() > model_deadline:
                        raise LLMUnavailable(f"{model}: no answer text within {config.MODEL_FIRST_TOKEN_S}s")
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        delta = _text_of(json.loads(data)["choices"][0].get("delta", {}).get("content"))
                    except (ValueError, KeyError, IndexError):
                        continue
                    if delta:
                        emitted = True
                        yield delta
            if emitted:
                return
            log.warning("openai-compatible stream %s ended without text", model)
            _cool(f"openai:{model}", "empty")
        except Exception as e:  # noqa: BLE001
            if emitted:
                raise
            log.warning("openai-compatible stream %s failed: %s", model, str(e)[:160])
            _cool(f"openai:{model}", str(e))


# ---------------------------------------------------------------- Gemini
def _gemini():
    global _gemini_client
    if _gemini_client is None:
        with _client_lock:  # one shared client; a GC'd duplicate would close its pool mid-request
            if _gemini_client is None:
                from google import genai
                from google.genai import types

                _gemini_client = genai.Client(
                    api_key=config.GEMINI_API_KEY,
                    http_options=types.HttpOptions(timeout=config.LLM_TIMEOUT_S * 1000),
                )
    return _gemini_client


def _gemini_cfg(model, system, json_mode, max_tokens, temperature, timeout_s, thinking):
    from google.genai import types

    cfg = dict(system_instruction=system, max_output_tokens=max_tokens, temperature=temperature,
               http_options=types.HttpOptions(timeout=int(timeout_s * 1000)))
    if json_mode:
        cfg["response_mime_type"] = "application/json"
    if thinking is not None and "flash" in model and model not in _no_thinking:
        cfg["thinking_config"] = types.ThinkingConfig(thinking_budget=thinking)
    return cfg


def _gemini_complete(models, system, user, json_mode, max_tokens, temperature, deadline) -> str:
    from google.genai import types

    last = None
    for model in _ready("gemini", models):
        for _ in range(2):  # second pass only to retry without an unsupported thinking budget
            left = deadline - time.time()
            if left < 2:
                raise LLMUnavailable(str(last)[:300] if last else "gemini: no time left")
            cfg = _gemini_cfg(model, system, json_mode, max_tokens, temperature,
                              min(left, config.LLM_CALL_TIMEOUT_S), 0 if json_mode else 512)
            try:
                r = _gemini().models.generate_content(model=model, contents=user,
                                                      config=types.GenerateContentConfig(**cfg))
                text = (r.text or "").strip()
                if text:
                    return text
                last = LLMUnavailable(f"{model}: empty response")
                break
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                last = e
                if "thinking_config" in cfg and "INVALID_ARGUMENT" in msg and model not in _no_thinking:
                    _no_thinking.add(model)
                    continue
                log.warning("gemini %s failed: %s", model, msg[:140])
                if any(t in msg for t in _TRANSIENT):
                    _cool(f"gemini:{model}", msg)
                break
    raise LLMUnavailable(str(last)[:300] if last else "no gemini model available")


def _gemini_stream(system, user, max_tokens, temperature, first_token_deadline):
    from google.genai import types

    for model in _ready("gemini", config.GEMINI_MODELS):
        left = first_token_deadline - time.time()
        if left < 2:
            return
        cfg = _gemini_cfg(model, system, False, max_tokens, temperature, min(left, config.LLM_CALL_TIMEOUT_S), 512)
        model_deadline = time.time() + min(left, config.MODEL_FIRST_TOKEN_S)
        emitted = False
        try:
            for chunk in _gemini().models.generate_content_stream(
                    model=model, contents=user, config=types.GenerateContentConfig(**cfg)):
                if not emitted and time.time() > model_deadline:
                    raise LLMUnavailable(f"{model}: no answer text in time")
                text = chunk.text or ""
                if text:
                    emitted = True
                    yield text
            if emitted:
                return
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if emitted:
                raise
            if "INVALID_ARGUMENT" in msg:
                _no_thinking.add(model)
            log.warning("gemini stream %s failed: %s", model, msg[:140])
            if any(t in msg for t in _TRANSIENT):
                _cool(f"gemini:{model}", msg)


# ---------------------------------------------------------------- Anthropic / Groq
def _anthropic_complete(system, user, max_tokens, temperature, deadline) -> str:
    import anthropic

    left = deadline - time.time()
    if left < 2:
        raise LLMUnavailable("anthropic: no time left")
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY, timeout=min(left, config.LLM_CALL_TIMEOUT_S))
    r = client.messages.create(
        model=config.ANTHROPIC_MODEL, max_tokens=max_tokens, temperature=temperature,
        system=system, messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in r.content if b.type == "text").strip()


def _groq_complete(system, user, json_mode, max_tokens, temperature, deadline) -> str:
    from groq import Groq

    left = deadline - time.time()
    if left < 2:
        raise LLMUnavailable("groq: no time left")
    client = Groq(api_key=config.GROQ_API_KEY, timeout=min(left, config.LLM_CALL_TIMEOUT_S))
    kw = {"response_format": {"type": "json_object"}} if json_mode else {}
    r = client.chat.completions.create(
        model=config.GROQ_MODEL, max_tokens=max_tokens, temperature=temperature,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}], **kw,
    )
    return (r.choices[0].message.content or "").strip()


# ---------------------------------------------------------------- public API
def complete(system: str, user: str, *, fast: bool = False, json_mode: bool = False,
             max_tokens: int = 1400, temperature: float = 0.2, budget_s: float | None = None) -> str:
    """One completion within `budget_s` seconds across all providers, or LLMUnavailable."""
    budget = budget_s if budget_s is not None else (config.ANALYZE_BUDGET_S if fast else config.ANSWER_BUDGET_S)
    deadline = time.time() + budget
    errors = []
    attempts = []
    if config.OPENAI_BASE_URL:
        models = config.OPENAI_FAST_MODELS if fast else config.OPENAI_MODELS
        attempts.append(("openai", lambda: _openai_complete(models, system, user, json_mode, max_tokens, temperature, deadline, fast)))
    if config.GEMINI_API_KEY:
        models = config.GEMINI_FAST_MODELS if fast else config.GEMINI_MODELS
        attempts.append(("gemini", lambda: _gemini_complete(models, system, user, json_mode, max_tokens, temperature, deadline)))
    if config.ANTHROPIC_API_KEY:
        attempts.append(("anthropic", lambda: _anthropic_complete(system, user, max_tokens, temperature, deadline)))
    if config.GROQ_API_KEY:
        attempts.append(("groq", lambda: _groq_complete(system, user, json_mode, max_tokens, temperature, deadline)))
    for name, fn in attempts:
        if deadline - time.time() < 2:
            errors.append("time budget exhausted")
            break
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {str(e)[:200]}")
    raise LLMUnavailable("; ".join(errors) or "no LLM provider configured")


def stream(system: str, user: str, *, max_tokens: int = 1800, temperature: float = 0.2):
    """Yield answer text incrementally. A provider/model is only abandoned
    before it has emitted anything; if none starts within the first-token
    budget, raise LLMUnavailable so the caller can answer extractively."""
    first_token_deadline = time.time() + config.FIRST_TOKEN_BUDGET_S
    if config.OPENAI_BASE_URL:
        emitted = False
        for piece in _openai_stream(config.OPENAI_MODELS, system, user, max_tokens, temperature, first_token_deadline):
            emitted = True
            yield piece
        if emitted:
            return
    if config.GEMINI_API_KEY:
        emitted = False
        for piece in _gemini_stream(system, user, max_tokens, temperature, first_token_deadline):
            emitted = True
            yield piece
        if emitted:
            return
    left = first_token_deadline - time.time()
    if (config.ANTHROPIC_API_KEY or config.GROQ_API_KEY) and left > 3:
        yield complete(system, user, max_tokens=max_tokens, temperature=temperature, budget_s=left)
        return
    raise LLMUnavailable("no model started answering within the time budget")


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
