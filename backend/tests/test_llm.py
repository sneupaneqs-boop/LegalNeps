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
        self.wfile.write(json.dumps({"choices": [{"message": {"content": f"ok:{body['model']}"}}]}).encode())


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
