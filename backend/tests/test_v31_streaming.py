"""V3.1: progressive streaming with per-sentence verification. The provider stream is faked (no network):
sentences are verified the moment they complete, removed ones never reach a delta, and the final `done.answer`
is exactly the text the reader ends up with (deltas, or the last `replace` plus later deltas)."""
import json
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from app import config, generation, llm, structured
from test_v3_structured import (GOOD, LABOUR, QUOTE_EN, QUOTE_NE, RENT, RENT_QUOTE, S, doc_of,  # noqa: F401
                                pipeline)

THREE = {"blocks": [{"heading": "Key rules", "sentences": [
    S("Under the Labour Act, 2074, Section 162, a worker can file a complaint within 6 months.", "deadline", (1, QUOTE_EN)),
    S("A landlord must sign a written agreement under Muluki Civil Code, 2074, Section 386.", "rule", (2, RENT_QUOTE)),
    S("A worker aggrieved by an act contrary to the Act may file a complaint under Section 162.", "rule", (1, QUOTE_EN))]}],
    "gaps": [], "follow_up_questions": []}
RAW = json.dumps(GOOD, ensure_ascii=False)
RAW_ASCII = json.dumps(GOOD, ensure_ascii=True)


def split_random(text, rng, lo=1, hi=17):
    i, out = 0, []
    while i < len(text):
        n = rng.randint(lo, hi)
        out.append(text[i:i + n])
        i += n
    return out


def fake_stream(text, chunk=10, delay=0.0, fail_after=None, finish="stop", marks=None):
    def gen(system, user, *, max_tokens=0, budget_s=None, info=None, **kw):
        if marks is not None:
            marks["start"] = time.perf_counter()
        if info is not None:
            info["finish"] = finish
        for i in range(0, len(text), chunk):
            if fail_after is not None and i >= fail_after:
                raise RuntimeError("provider died mid-stream")
            if delay:
                time.sleep(delay)
            yield text[i:i + chunk]
        if marks is not None:
            marks["end"] = time.perf_counter()
    return gen


def visible(events):
    """What the frontend ends up showing: deltas append, `replace` swaps."""
    text = ""
    for k, d in events:
        if k == "delta":
            text += d
        elif k == "replace":
            text = d
    return text


def run_events(lang="en", msg="My employer has not paid my salary for 4 months. What can I do?"):
    events = list(generation.run(msg, lang))
    return events, next(d for k, d in events if k == "done")


# ------------------------------------------------------------- incremental parser

def _sentences_of(doc):
    return [s["text"] for b in doc["blocks"] for s in b["sentences"]]


@pytest.mark.parametrize("raw", [RAW, RAW_ASCII], ids=["utf8", "escaped"])
def test_incremental_parser_matches_full_parse_for_any_chunking(raw):
    want = _sentences_of(GOOD)
    for seed in range(40):
        p = structured.IncrementalDoc()
        got = []
        for piece in split_random(raw, random.Random(seed)):
            got += [(b, h, s["text"]) for b, h, s in p.feed(piece)]
        assert [t for _, _, t in got] == want
        assert [b for b, _, _ in got] == [0, 1, 1, 1] and [h for _, h, _ in got] == ["", "Key rules", "Key rules", "Key rules"]
        assert p.closed


def test_incremental_parser_one_char_at_a_time_and_split_escapes():
    p = structured.IncrementalDoc()
    got = []
    for ch in RAW_ASCII:  # splits every \uXXXX escape, every key and every quote
        got += p.feed(ch)
    assert [s["text"] for _, _, s in got] == _sentences_of(GOOD)


def test_incremental_parser_devanagari_and_escaped_quotes():
    doc = {"blocks": [{"heading": "मुख्य नियम", "sentences": [
        S("श्रमिकले \"उजुरी\" दिन सक्छ \\ यो।", "rule", (1, QUOTE_NE)), S("दोस्रो वाक्य।", "empathy")]}]}
    for raw in (json.dumps(doc, ensure_ascii=False), json.dumps(doc, ensure_ascii=True)):
        for seed in range(20):
            p = structured.IncrementalDoc()
            got = []
            for piece in split_random(raw, random.Random(seed), 1, 5):
                got += p.feed(piece)
            assert [(h, s["text"]) for _, h, s in got] == [("मुख्य नियम", d["text"]) for d in doc["blocks"][0]["sentences"]]
            assert got[0][2]["cites"][0]["quote"] == QUOTE_NE


def test_incremental_parser_cut_off_mid_sentence_and_prose_prefix():
    cut = RAW[:RAW.index("The employer must also") + 30]
    p = structured.IncrementalDoc()
    got = p.feed("```json\n" + cut)
    assert [s["text"] for _, _, s in got] == _sentences_of(GOOD)[:3] and not p.closed


def test_incremental_parser_never_rescans_consumed_text(monkeypatch):
    positions = []

    class Spy:
        def __init__(self, rx):
            self.rx = rx

        def search(self, t, i):
            positions.append(i)
            return self.rx.search(t, i)

    monkeypatch.setattr(structured, "_STRUCT", Spy(structured._STRUCT))
    monkeypatch.setattr(structured, "_STR_SPECIAL", Spy(structured._STR_SPECIAL))
    big = json.dumps({"blocks": [{"heading": "H", "sentences": [S(f"Sentence number {i}.", "advice") for i in range(400)]}]})
    p = structured.IncrementalDoc()
    n = 0
    for piece in split_random(big, random.Random(1), 5, 30):
        n += len(p.feed(piece))
    assert n == 400
    assert positions == sorted(positions)                      # the scan position only ever moves forward
    assert len(positions) < 3 * len(big) / 8                   # ~ one search per token, not per re-parse


# ------------------------------------------------------------- pipeline

def test_first_delta_arrives_before_the_model_finishes_and_timing(pipeline, monkeypatch):
    """Simulated provider at 40 ms per ~3-char token: time to first verified text vs the whole answer."""
    marks: dict = {}
    monkeypatch.setattr(llm, "stream_json", fake_stream(RAW, chunk=3, delay=0.04, marks=marks))
    times = {"first": None}
    events = []
    t0 = time.perf_counter()
    for kind, data in generation.run("My employer has not paid my salary for 4 months. What can I do?", "en"):
        events.append((kind, data))
        if kind == "delta" and times["first"] is None:
            times["first"] = time.perf_counter()
    total = time.perf_counter() - t0
    first = times["first"] - t0
    model_total = marks["end"] - marks["start"]
    print(f"\nSTREAM TIMING first_verified_text={first:.2f}s model_finished={model_total:.2f}s "
          f"done={total:.2f}s (non-streamed V3 would show text at ~{model_total:.2f}s)")
    assert times["first"] < marks["end"]                       # first delta before the provider stopped
    assert first < 0.85 * model_total
    kinds = [k for k, _ in events]
    assert kinds[:2] == ["meta", "status"] and kinds[-1] == "done" and "replace" not in kinds
    done = events[-1][1]
    assert visible(events) == done["answer"] and done["llm_used"] is True
    assert "15 days" not in "".join(d for k, d in events if k == "delta")


def test_timing_with_release_after_the_first_rule(pipeline, monkeypatch):
    monkeypatch.setattr(config, "STREAM_MIN_RULES", 1)
    marks: dict = {}
    monkeypatch.setattr(llm, "stream_json", fake_stream(RAW, chunk=3, delay=0.04, marks=marks))
    t0, first = time.perf_counter(), None
    for kind, _ in generation.run("My employer has not paid my salary for 4 months. What can I do?", "en"):
        if kind == "delta" and first is None:
            first = time.perf_counter() - t0
    model_total = marks["end"] - marks["start"]
    print(f"\nSTREAM TIMING (min_rules=1) first_verified_text={first:.2f}s model_finished={model_total:.2f}s")
    assert first < 0.5 * model_total


def test_deltas_are_verified_sentences_then_tail_and_answer_equals_visible(pipeline, monkeypatch):
    monkeypatch.setattr(llm, "stream_json", fake_stream(RAW, chunk=7))
    events, done = run_events()
    deltas = [d for k, d in events if k == "delta"]
    assert "replace" not in [k for k, _ in events]
    assert "".join(deltas) == done["answer"] == visible(events)
    assert "15 days" not in done["answer"] and "[2]" in done["answer"]
    assert done["answer"].startswith("I understand your salary has not been paid.")
    assert "What the sources don't cover" in "".join(deltas[-8:]) and done["answer"].endswith("consult a lawyer.")
    v = done["verification"]
    assert v["removed"]["count"] == 1 and v["claims"] == v["supported"] == 2
    assert pipeline["calls"] == []                             # no non-streamed generation call was needed
    # exactly what structured.render would produce for the verified doc
    doc, _ = structured.parse_answer(RAW)
    from app import verifier
    good, _ = verifier.verify_structured(doc, [LABOUR, RENT])
    assert done["answer"] == generation.tidy_answer(structured.render(
        {**good, "gaps": doc["gaps"], "follow_up_questions": []}, "en", generation.DISCLAIMER_EN), [LABOUR, RENT])


def test_nothing_is_shown_until_two_rules_verified(pipeline, monkeypatch):
    doc = {"blocks": [
        {"heading": "", "sentences": [S("I understand.", "empathy")]},
        {"heading": "Rules", "sentences": [
            S("Under the Labour Act, 2074, Section 162, a worker can file a complaint within 6 months.", "deadline", (1, QUOTE_EN)),
            S("A landlord must sign a written agreement under Muluki Civil Code, 2074, Section 386.", "rule", (2, RENT_QUOTE))]}]}
    monkeypatch.setattr(llm, "stream_json", fake_stream(json.dumps(doc), chunk=5))
    events, done = run_events()
    first_delta = next(d for k, d in events if k == "delta")
    assert "I understand." in first_delta and "Section 162" in first_delta and "[1]" in first_delta   # released together
    assert visible(events) == done["answer"]


def test_document_level_failure_before_release_shows_only_the_extractive_answer(pipeline, monkeypatch):
    doc = doc_of(S("A worker can file a complaint within 6 months under Section 162.", "deadline", (1, QUOTE_EN)),
                 S("The employer will be jailed for 5 years.", "penalty"))
    monkeypatch.setattr(llm, "stream_json", fake_stream(json.dumps(doc), chunk=9))
    events, done = run_events()
    deltas = "".join(d for k, d in events if k == "delta")
    assert "replace" not in [k for k, _ in events]
    assert done["llm_used"] is False and done["answer"].startswith(generation.UNVERIFIED_HEADER["en"])
    assert deltas == done["answer"] and "6 months" not in deltas.split("**[1]")[0]   # held sentence never leaked early


def test_document_level_failure_after_release_uses_replace(pipeline, monkeypatch):
    monkeypatch.setattr(config, "STREAM_MIN_RULES", 1)
    doc = doc_of(S("Under the Labour Act, 2074, Section 162, a worker can file a complaint within 6 months.", "deadline", (1, QUOTE_EN)),
                 S("The employer will be jailed for 5 years.", "penalty"))
    monkeypatch.setattr(llm, "stream_json", fake_stream(json.dumps(doc), chunk=9))
    events, done = run_events()
    kinds = [k for k, _ in events]
    assert kinds.index("delta") < kinds.index("replace") < kinds.index("done")
    assert done["llm_used"] is False and done["answer"].startswith(generation.UNVERIFIED_HEADER["en"])
    assert visible(events) == done["answer"]
    assert "jailed" not in visible(events) and "jailed" not in "".join(d for k, d in events if k == "delta")


def test_entailment_removal_of_streamed_sentence_uses_replace(pipeline, monkeypatch):
    monkeypatch.setattr(config, "ENTAILMENT_CHECK", True)
    monkeypatch.setattr(llm, "stream_json", fake_stream(json.dumps(THREE), chunk=11))
    pipeline["reply"] = json.dumps({"results": [{"id": 0, "verdict": "no"}, {"id": 1, "verdict": "yes"}, {"id": 2, "verdict": "partial"}]})
    events, done = run_events()
    kinds = [k for k, _ in events]
    assert "replace" in kinds and kinds.index("delta") < kinds.index("replace")
    streamed = "".join(d for k, d in events if k == "delta")
    gone = "can file a complaint within 6 months"
    assert gone in streamed                                     # it WAS shown once...
    assert gone not in done["answer"] and "written agreement" in done["answer"]   # ...and is gone at the end
    assert visible(events) == done["answer"]
    assert done["verification"]["removed"]["by_reason"].get("not_entailed") == 1


def test_removed_sentences_never_appear_in_any_delta(pipeline, monkeypatch):
    bad = [S("The employer must also pay 15 days' wages.", "rule", (1, QUOTE_EN)),                 # number
           S("The Labour Court can jail the employer.", "penalty"),                                 # uncited
           S("A worker may complain within six months.", "rule", (1, "invented quote that is not in the passage at all"))]
    good = [S("Under the Labour Act, 2074, Section 162, a worker can file a complaint within 6 months.", "deadline", (1, QUOTE_EN)),
            S("A landlord must sign a written agreement under Muluki Civil Code, 2074, Section 386.", "rule", (2, RENT_QUOTE))]
    doc = {"blocks": [{"heading": "A", "sentences": [bad[0], good[0], bad[1]]}, {"heading": "B", "sentences": [bad[2]]},
                      {"heading": "C", "sentences": [good[1]]}], "gaps": [], "follow_up_questions": []}
    monkeypatch.setattr(llm, "stream_json", fake_stream(json.dumps(doc), chunk=6))
    events, done = run_events()
    text = "".join(d for k, d in events if k == "delta")
    for s in bad:
        assert s["text"] not in text and s["text"] not in done["answer"]
    assert "**B**" not in text and "**A**" in text and "**C**" in text     # a block with nothing left has no heading
    assert done["verification"]["removed"]["count"] == 3 and done["verification"]["removed"]["blocks_dropped"] == 1
    assert visible(events) == done["answer"]


def test_cut_off_stream_shows_only_complete_sentences(pipeline, monkeypatch):
    cut = RAW[:RAW.index("The employer must also") + 25]
    monkeypatch.setattr(llm, "stream_json", fake_stream(cut, chunk=8, finish="length"))
    events, done = run_events()
    assert "The employer must also" not in visible(events) and "written agreement" in visible(events)
    assert done["llm_used"] is True and done["verification"]["truncated"] is True
    assert visible(events) == done["answer"] and "replace" not in [k for k, _ in events]


def test_error_mid_stream_after_enough_sentences_keeps_what_was_verified(pipeline, monkeypatch):
    monkeypatch.setattr(llm, "stream_json", fake_stream(RAW, chunk=8, fail_after=RAW.index("The employer must also") + 10))
    events, done = run_events()
    assert done["llm_used"] is True and done["verification"]["truncated"] is True
    assert "written agreement" in done["answer"] and visible(events) == done["answer"]
    assert pipeline["calls"] == []


def test_error_mid_stream_too_early_falls_back_to_the_non_streamed_call(pipeline, monkeypatch):
    monkeypatch.setattr(llm, "stream_json", fake_stream(RAW, chunk=8, fail_after=RAW.index("Key rules")))
    pipeline["reply"] = RAW
    events, done = run_events()
    assert done["llm_used"] is True and "written agreement" in done["answer"] and "Section 162" in done["answer"]
    assert len(pipeline["calls"]) == 1 and visible(events) == done["answer"]
    assert done["verification"]["truncated"] is False           # the fallback's reply is complete


def test_error_after_shown_text_then_fallback_swaps_via_replace(pipeline, monkeypatch):
    monkeypatch.setattr(config, "STREAM_MIN_RULES", 1)
    first = doc_of(S("Under the Labour Act, 2074, Section 162, a worker can file a complaint within 6 months.", "deadline", (1, QUOTE_EN)))
    raw = json.dumps(first)
    monkeypatch.setattr(llm, "stream_json", fake_stream(raw, chunk=8, fail_after=len(raw) - 6))
    pipeline["reply"] = RAW                                    # fallback answer differs from what was streamed
    events, done = run_events()
    assert "replace" in [k for k, _ in events] and visible(events) == done["answer"]
    assert "written agreement" in done["answer"]


def test_no_streaming_provider_uses_the_non_streamed_path(pipeline, monkeypatch):
    def none(*a, **k):
        raise llm.LLMUnavailable("no streaming provider")
        yield  # pragma: no cover

    monkeypatch.setattr(llm, "stream_json", none)
    pipeline["reply"] = RAW
    events, done = run_events()
    assert done["llm_used"] is True and visible(events) == done["answer"] and len(pipeline["calls"]) == 1
    assert "replace" not in [k for k, _ in events]


def test_stream_verified_flag_off_restores_v3(pipeline, monkeypatch):
    monkeypatch.setattr(config, "STREAM_VERIFIED", False)
    monkeypatch.setattr(llm, "stream_json", lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not stream")))
    pipeline["reply"] = RAW
    events, done = run_events()
    assert visible(events) == done["answer"] and done["llm_used"] is True


def test_unparseable_stream_gets_repair_then_extractive(pipeline, monkeypatch):
    monkeypatch.setattr(llm, "stream_json", fake_stream("this is prose, not json", chunk=4))
    pipeline["reply"] = "still not json"
    events, done = run_events()
    assert done["llm_used"] is False and done["answer"].startswith(generation.UNVERIFIED_HEADER["en"])
    assert visible(events) == done["answer"] and len(pipeline["calls"]) == 1


def test_nepali_answer_streams_with_escaped_unicode_split_anywhere(pipeline, monkeypatch):
    ne = {"blocks": [
        {"heading": "", "sentences": [S("तलब नपाएको कुराले तपाईंलाई चिन्ता भएको मैले बुझें।", "empathy")]},
        {"heading": "मुख्य नियम", "sentences": [
            S("श्रम ऐन, २०७४ को दफा १६२ अनुसार श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)),
            S("मुलुकी देवानी संहिता, २०७४ को दफा ३८६ अनुसार बहालमा लिने व्यक्तिसँग लिखित सम्झौता गर्नु पर्छ।", "rule", (2, RENT_QUOTE)),
            S("श्रमिकले ३५ दिनभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE))]}],
        "gaps": ["मैले पाएका स्रोतहरूले उजुरी सुन्ने निकाय समेटेका छैनन्।"], "follow_up_questions": []}
    raw = json.dumps(ne, ensure_ascii=True)
    rng = random.Random(3)
    pieces = split_random(raw, rng, 1, 9)

    def gen(system, user, *, info=None, **kw):
        info["finish"] = "stop"
        yield from pieces

    monkeypatch.setattr(llm, "stream_json", gen)
    events, done = run_events("ne", "मेरो तलब ६ महिनादेखि आएको छैन")
    assert visible(events) == done["answer"] and done["llm_used"] is True
    assert "३५ दिन" not in done["answer"] and "दफा १६२" in done["answer"] and "दफा ३८६" in done["answer"]
    assert done["answer"].startswith("तलब नपाएको") and "**मुख्य नियम**\n- " in done["answer"]


def test_paid_tier_streams_and_reports_usage_and_runs_entailment_last(pipeline, monkeypatch):
    calls = []

    def paid_stream(model, system, user, *, max_tokens, budget_s=None, info=None, **kw):
        calls.append(model)
        info["usage"] = {"input_tokens": 100, "output_tokens": 50}
        info["finish"] = "end_turn"
        for i in range(0, len(RAW), 9):
            yield RAW[i:i + 9]

    def paid_complete(model, system, user, **kw):
        calls.append(("entail", model))
        return json.dumps({"results": [{"id": 0, "verdict": "yes"}, {"id": 1, "verdict": "yes"}]}), \
            {"input_tokens": 10, "output_tokens": 5}

    monkeypatch.setattr(llm, "paid_stream", paid_stream)
    monkeypatch.setattr(llm, "paid_complete", paid_complete)
    events = list(generation.run("My employer has not paid my salary for 4 months. What can I do?", "en", tier="haiku"))
    done = events[-1][1]
    assert done["usage"] == {"input_tokens": 110, "output_tokens": 55}
    assert visible(events) == done["answer"] and "replace" not in [k for k, _ in events]
    assert calls[0] == generation.tiers.model_for_tier("haiku") and calls[-1][0] == "entail"


def test_cache_hit_still_has_no_streaming_events(pipeline, monkeypatch):
    monkeypatch.setattr(llm, "stream_json", fake_stream(RAW, chunk=12))
    _, first = run_events()
    events, second = run_events()
    assert second["cached"] is True and [k for k, _ in events] == ["meta", "done"] and second["answer"] == first["answer"]


def test_non_stream_chat_endpoint_ignores_progressive_events(pipeline, monkeypatch):
    monkeypatch.setattr(llm, "stream_json", fake_stream(RAW, chunk=12))
    res = generation.answer_question("My employer has not paid my salary for 4 months. What can I do?", "en")
    assert res["llm_used"] is True and "written agreement" in res["answer"] and "15 days" not in res["answer"]


def test_stream_endpoint_forwards_replace(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from app import retrieval, supa
    from app.main import app
    from fixtures import ENTRIES

    monkeypatch.setattr(retrieval, "CACHE_DIR", tmp_path)
    idx = retrieval.Index([dict(e) for e in ENTRIES], "v31-test")
    monkeypatch.setattr(retrieval, "_index", idx)
    monkeypatch.setattr(generation, "get_index", lambda: idx)
    supa._ip_hits.clear()

    def fake_run(message, language="auto", history=None, tier="free"):
        yield "meta", {"language": "en", "sources": [], "analysis": {}}
        yield "status", {"stage": "checking sources"}
        yield "delta", "draft"
        yield "replace", "final"
        yield "done", {"answer": "final", "llm_used": True, "cached": False, "llm_calls": 1}

    monkeypatch.setattr("app.routes.chat.stream_answer", fake_run)
    with TestClient(app) as c:
        r = c.post("/api/chat/stream", json={"message": "hello there", "language": "en"})
    events = [json.loads(l) for l in r.text.splitlines() if l.strip()]
    assert [e["type"] for e in events] == ["meta", "status", "delta", "replace", "done"]
    assert events[3]["text"] == "final" and events[4]["answer"] == "final"


# ------------------------------------------------------------- llm.stream_json over a real (local) SSE endpoint

class _SSE(BaseHTTPRequestHandler):
    seen: list = []

    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.seen.append(body)
        if "response_format" in body:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"response_format is not supported with stream"}}')
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        for piece in ['{"blocks":[', '{"heading":"x","sentences":[]}', "]}"]:
            self.wfile.write(f"data: {json.dumps({'choices': [{'delta': {'content': piece}}]})}\n\n".encode())
        self.wfile.write(b'data: {"choices":[{"delta":{},"finish_reason":"length"}]}\n\n')
        self.wfile.write(b"data: [DONE]\n\n")


def test_stream_json_retries_without_response_format_and_reports_finish(monkeypatch):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _SSE)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    monkeypatch.setattr(config, "OPENAI_BASE_URL", f"http://127.0.0.1:{srv.server_port}/v1")
    monkeypatch.setattr(config, "OPENAI_MODELS", ["auto"])
    llm._cooldown.clear()
    llm._no_json_stream.clear()
    _SSE.seen.clear()
    info: dict = {}
    try:
        out = "".join(llm.stream_json("sys", "hi", info=info))
    finally:
        srv.shutdown()
        llm._no_json_stream.clear()
    assert json.loads(out) == {"blocks": [{"heading": "x", "sentences": []}]}
    assert info["finish"] == "length" and llm.was_cut_off(info["finish"])
    assert "response_format" in _SSE.seen[0] and "response_format" not in _SSE.seen[1]


def test_stream_json_without_any_provider_raises_quickly(monkeypatch):
    monkeypatch.setattr(config, "OPENAI_BASE_URL", "")
    monkeypatch.setattr(config, "DIRECT_PROVIDERS", {})
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    with pytest.raises(llm.LLMUnavailable):
        list(llm.stream_json("s", "u"))
