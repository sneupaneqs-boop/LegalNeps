import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from app import config, llm

MODE = {"value": "ok"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        mode = MODE["value"]
        if mode == "hang":
            time.sleep(8)
        if mode == "400-effort" and "reasoning_effort" in body:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"Request contains an invalid argument."}}')
            return
        if mode == "429-key1" and self.headers.get("Authorization") == "Bearer key1":
            self.send_response(429)
            self.end_headers()
            self.wfile.write(b'{"error":"rate limit"}')
            return
        if mode == "429":
            self.send_response(429)
            self.end_headers()
            self.wfile.write(b'{"error":"rate limit"}')
            return
        if body.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for piece in ["Hello ", "from ", body["model"]]:
                chunk = {"choices": [{"delta": {"content": piece}}]}
                self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
                self.wfile.flush()
            self.wfile.write(b"data: [DONE]\n\n")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        content = f"ok:{body['model']}"
        if mode == "parts":
            content = [{"type": "text", "text": "ok:"}, {"type": "text", "text": body["model"]}]
        self.wfile.write(json.dumps({"choices": [{"message": {"content": content}}]}).encode())


@pytest.fixture()
def gateway(monkeypatch):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    monkeypatch.setattr(config, "OPENAI_BASE_URL", f"http://127.0.0.1:{srv.server_port}/v1")
    monkeypatch.setattr(config, "OPENAI_MODELS", ["auto"])
    monkeypatch.setattr(config, "OPENAI_FAST_MODELS", ["auto/fast"])
    llm._cooldown.clear()
    MODE["value"] = "ok"
    yield
    srv.shutdown()


def test_openai_compatible_gateway_uses_fast_tier_for_analysis(gateway):
    assert llm.available()
    assert llm.complete("sys", "hi", fast=True) == "ok:auto/fast"
    assert llm.complete("sys", "hi") == "ok:auto"


def test_streaming_through_gateway(gateway):
    assert "".join(llm.stream("sys", "hi")) == "Hello from auto"


def test_hanging_provider_is_cut_off_by_budget(gateway, monkeypatch):
    MODE["value"] = "hang"
    t = time.time()
    with pytest.raises(llm.LLMUnavailable):
        llm.complete("sys", "hi", fast=True, budget_s=3)
    assert time.time() - t < 5


def test_rate_limited_model_cools_down(gateway):
    MODE["value"] = "429"
    with pytest.raises(llm.LLMUnavailable):
        llm.complete("sys", "hi", budget_s=5)
    assert llm._cooldown.get("openai:auto", 0) > time.time()


def test_stream_gives_up_when_nothing_starts(gateway, monkeypatch):
    MODE["value"] = "hang"
    monkeypatch.setattr(config, "FIRST_TOKEN_BUDGET_S", 3)
    t = time.time()
    with pytest.raises(llm.LLMUnavailable):
        list(llm.stream("sys", "hi"))
    assert time.time() - t < 6


def test_content_as_list_of_parts_and_reasoning_hint(gateway):
    MODE["value"] = "parts"
    assert llm.complete("sys", "hi", fast=True) == "ok:auto/fast"
    body = llm._openai_payload("gemini/gemini-3.1-flash-lite", "s", "u", True, 10, 0, fast=True)
    assert body["reasoning_effort"] == "none" and body["response_format"]["type"] == "json_object"
    assert llm._openai_payload("groq/openai/gpt-oss-120b", "s", "u", False, 10, 0)["reasoning_effort"] == "low"
    assert "reasoning_effort" not in llm._openai_payload("mistral/mistral-small-latest", "s", "u", False, 10, 0)


def test_stream_skips_model_that_only_thinks(gateway, monkeypatch):
    # "hang" sleeps before sending anything; with a short per-model window the
    # stream must give up on it quickly rather than wait for the full budget
    MODE["value"] = "hang"
    monkeypatch.setattr(config, "MODEL_FIRST_TOKEN_S", 2)
    monkeypatch.setattr(config, "FIRST_TOKEN_BUDGET_S", 20)
    monkeypatch.setattr(config, "LLM_CALL_TIMEOUT_S", 3)
    t = time.time()
    with pytest.raises(llm.LLMUnavailable):
        list(llm.stream("sys", "hi"))
    assert time.time() - t < 10


def test_model_rejecting_reasoning_effort_is_retried_without_it(gateway, monkeypatch):
    seen = []
    orig = llm._openai_payload

    def spy(model, *a, **k):
        body = orig(model, *a, **k)
        seen.append("reasoning_effort" in body)
        return body
    monkeypatch.setattr(llm, "_openai_payload", spy)
    monkeypatch.setattr(config, "OPENAI_FAST_MODELS", ["gemini/gemini-3.5-flash-lite"])
    MODE["value"] = "400-effort"
    assert llm.complete("sys", "hi", fast=True) == "ok:gemini/gemini-3.5-flash-lite"
    assert seen == [True, False]


def test_direct_providers_rotate_keys_and_skip_unconfigured(gateway, monkeypatch):
    base = config.OPENAI_BASE_URL
    monkeypatch.setattr(config, "OPENAI_BASE_URL", "")
    monkeypatch.setattr(config, "DIRECT_PROVIDERS", {"groq": (base, ["key1", "key2"])})
    monkeypatch.setattr(config, "OPENAI_MODELS", ["openrouter/x:free", "groq/openai/gpt-oss-120b"])
    MODE["value"] = "429-key1"
    # openrouter has no key -> skipped; provider prefix stripped for the direct API;
    # key1 rate-limited -> key2 answers, and key1 stays cooled for the next call
    for _ in range(3):
        assert llm.complete("sys", "hi") == "ok:openai/gpt-oss-120b"
    assert [t.key for t in llm._targets(["groq/openai/gpt-oss-120b"])] == ["key2"]


def test_gateway_chain_not_clobbered_by_gemini_chain(gateway, monkeypatch):
    # regression: both chains used to share one closure variable, so the
    # gateway was sent the Gemini SDK model names
    monkeypatch.setattr(config, "GEMINI_API_KEY", "x")
    monkeypatch.setattr(config, "GEMINI_FAST_MODELS", ["gemini-lite"])
    assert llm.complete("sys", "hi", fast=True) == "ok:auto/fast"
