"""S3: LLM-free hot path - confidence-gated skip of analyze_query()'s LLM
call, and the expanded non-legal intent regex it relies on."""
import pytest

from app import config, generation, llm


def test_quick_intent_catches_smalltalk_and_off_topic():
    assert generation.quick_intent("who are you?") == "smalltalk"
    assert generation.quick_intent("what can you do") == "smalltalk"
    assert generation.quick_intent("तिमी को हौ") == "smalltalk"
    assert generation.quick_intent("what's the weather today?") == "off_topic"
    assert generation.quick_intent("मौसम कस्तो छ?") == "off_topic"
    # still catches the pre-existing cases
    assert generation.quick_intent("namaste") == "greeting"
    assert generation.quick_intent("dhanyabad") == "thanks"
    # a real legal question must never be caught by these
    assert generation.quick_intent("My landlord won't return my deposit") is None
    assert generation.quick_intent("घरबेटीले धरौटी फिर्ता दिएन") is None


def test_confidence_high_for_nepali_and_glossary_matched_english():
    assert generation.confidence("घरबेटीले धरौटी फिर्ता दिएन, म के गर्न सक्छु?", "ne") >= generation.CONFIDENCE_THRESHOLD
    assert generation.confidence("My landlord won't return my security deposit", "en") >= generation.CONFIDENCE_THRESHOLD


def test_confidence_low_for_english_with_no_glossary_hits():
    assert generation.confidence("What is the official language of Nepal?", "en") < generation.CONFIDENCE_THRESHOLD


@pytest.fixture()
def llm_available(monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "fake-key-for-test")
    generation._analysis_cache.data.clear()


def _explode(*a, **kw):
    raise AssertionError("llm.complete should not have been called for a confident, no-history message")


def test_confident_first_turn_skips_the_llm_call(llm_available, monkeypatch):
    monkeypatch.setattr(llm, "complete", _explode)
    out = generation.analyze_query("My landlord won't return my security deposit", "en", history=None)
    assert out["intent"] == "legal"
    assert out["llm"] is False
    assert out["question"] == "My landlord won't return my security deposit"
    assert generation.analyze_needs_llm("My landlord won't return my security deposit", "en", None) is False


def test_low_confidence_message_still_calls_the_llm(llm_available, monkeypatch):
    called = {"n": 0}

    def fake_complete(*a, **kw):
        called["n"] += 1
        return '{"intent":"legal","queries_ne":["भाषा"]}'

    monkeypatch.setattr(llm, "complete", fake_complete)
    out = generation.analyze_query("What is the official language of Nepal?", "en", history=None)
    assert called["n"] == 1
    assert out["llm"] is True
    assert generation.analyze_needs_llm("What is the official language of Nepal?", "en", None) is True


def test_followups_always_use_the_llm_even_if_confident(llm_available, monkeypatch):
    called = {"n": 0}

    def fake_complete(*a, **kw):
        called["n"] += 1
        return '{"intent":"legal","question":"resolved"}'

    monkeypatch.setattr(llm, "complete", fake_complete)
    history = [{"role": "user", "text": "मेरो घरबेटीले धरौटी फिर्ता दिएन"}, {"role": "bot", "text": "..."}]
    generation.analyze_query("अंश पनि पाइन्छ?", "ne", history=history)
    assert called["n"] == 1
    assert generation.analyze_needs_llm("अंश पनि पाइन्छ?", "ne", history) is True
