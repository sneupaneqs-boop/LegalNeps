"""V2: query understanding for romanised Nepali.

Root cause of the production bug ("boss le din ko 12 ghanta kaam garauchha,
overtime ko paisa pani dinna" -> queries_ne [] and 7 sources from the
Workplace Sexual Harassment Act): guess_language() calls romanised Nepali
"ne", confidence() trusted that hint (0.9), and even for English it counted
loose glossary hits (0.3 each). Either way analyze_query() skipped the LLM
rewrite. These tests pin the fixed rule and the offline LLM path."""
import json

import pytest

from app import config, generation, llm
from app.text_norm import guess_language

BOSS = "boss le din ko 12 ghanta kaam garauchha, overtime ko paisa pani dinna"
MANPOWER = "manpower le thagyo. Malaysia pathaidinchhu bhanera 3 lakh liyo, 8 mahina bhayo visa aayena"

# a realistic fast-tier reply for BOSS (what ANALYZE_SYSTEM asks for)
LLM_REPLY = json.dumps({
    "intent": "legal",
    "reply": "",
    "question": "My employer makes me work 12 hours a day and refuses to pay overtime. Is that legal?",
    "reply_language": "ne",
    "concern": "Employer requires 12-hour days and does not pay overtime.",
    "area": "labour - hours and overtime",
    "queries_ne": ["कार्य घण्टा दैनिक आठ घण्टा", "अतिरिक्त समयको पारिश्रमिक", "साप्ताहिक कार्य घण्टा",
                   "पारिश्रमिक दर"],
    "queries_en": ["working hours overtime pay"],
    "laws": ["श्रम ऐन, २०७४"],
    "wants_precedent": False,
})


@pytest.fixture()
def llm_on(monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "fake-key-for-test")
    generation._analysis_cache.data.clear()
    yield
    generation._analysis_cache.data.clear()


@pytest.fixture()
def calls(monkeypatch, llm_on):
    """Replace llm.complete with a recorder that returns LLM_REPLY."""
    seen = []

    def fake(system, user, **kw):
        seen.append({"system": system, "user": user, **kw})
        return LLM_REPLY

    monkeypatch.setattr(llm, "complete", fake)
    return seen


# ---------------------------------------------------------------- the bug
def test_root_cause_language_hint_calls_romanised_nepali_ne():
    """The hint is 'ne' for romanised Nepali, so it can never be used as a
    'the index can read this' signal."""
    assert guess_language(BOSS) == "ne"
    assert not generation._is_devanagari(BOSS)


def test_boss_overtime_message_is_not_confident_and_needs_the_llm(llm_on):
    assert generation.confidence(BOSS, "ne") < generation.CONFIDENCE_THRESHOLD
    assert generation.confidence(BOSS, "en") < generation.CONFIDENCE_THRESHOLD
    assert generation.analyze_needs_llm(BOSS, "ne", None) is True


def test_the_wrong_playbook_is_not_a_confident_match():
    """The half-match on "boss" must not pin the Workplace Sexual Harassment
    provisions. (V2.5: the overtime / working-hours plan now exists, so the
    message is matched to it on its own exact phrases - the LLM rewrite is
    still needed because the glossary expansion of this message is not precise.)"""
    assert generation.strong_playbook_match(BOSS) == "overtime_working_hours"
    assert generation._playbook_id_for(BOSS) == "overtime_working_hours"
    assert generation._playbook_id_for(BOSS) != "workplace_sexual_harassment"


def test_glossary_no_longer_treats_paisa_pani_as_land_units_and_water():
    hits = {k for k, _ in generation.glossary.expand_hits(BOSS)}
    assert ("paisa",) not in hits and ("pani",) not in hits


# ------------------------------------------------- skip rule / sync rule
def test_devanagari_first_turn_keeps_the_llm_free_fast_path(llm_on, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("no LLM call expected")

    monkeypatch.setattr(llm, "complete", boom)
    q = "घरबेटीले धरौटी फिर्ता दिएन, म के गर्न सक्छु?"
    assert generation.analyze_needs_llm(q, "ne", None) is False
    out = generation.analyze_query(q, "ne")
    assert out["llm"] is False and out["intent"] == "legal" and out["question"] == q


def test_latin_message_with_exact_playbook_phrase_and_precise_expansion_skips(llm_on, monkeypatch):
    monkeypatch.setattr(llm, "complete", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no call")))
    q = "My landlord won't return my security deposit"
    assert generation.confidence(q, "en") >= generation.CONFIDENCE_THRESHOLD
    assert generation.analyze_needs_llm(q, "en", None) is False
    assert generation.analyze_query(q, "en")["llm"] is False


@pytest.mark.parametrize("msg,lang", [
    (BOSS, "ne"), (MANPOWER, "ne"), ("What is the official language of Nepal?", "en"),
    ("My landlord won't return my security deposit", "en"),
    ("घरबेटीले धरौटी फिर्ता दिएन, म के गर्न सक्छु?", "ne"),
    ("gharbeti le deposit firta dinna", "ne"),
    ("namaste", "ne"),
])
def test_analyze_needs_llm_matches_what_analyze_query_actually_does(calls, msg, lang):
    predicted = generation.analyze_needs_llm(msg, lang, None)
    generation._analysis_cache.data.clear()
    generation.analyze_query(msg, lang)
    assert predicted == (len(calls) == 1)


def test_followups_always_use_the_llm(calls):
    hist = [{"role": "user", "text": "घरबेटीले धरौटी फिर्ता दिएन"}, {"role": "bot", "text": "..."}]
    assert generation.analyze_needs_llm("अंश पनि पाइन्छ?", "ne", hist) is True
    generation.analyze_query("अंश पनि पाइन्छ?", "ne", hist)
    assert len(calls) == 1


# ------------------------------------------------------------ the LLM path
def test_romanised_message_uses_the_llm_analysis(calls):
    out = generation.analyze_query(BOSS, "ne")
    assert len(calls) == 1
    assert calls[0]["fast"] is True and calls[0]["json_mode"] is True
    assert BOSS in calls[0]["user"]
    assert out["llm"] is True and out["intent"] == "legal"
    assert out["queries_ne"][0] == "कार्य घण्टा दैनिक आठ घण्टा"
    assert out["laws"] == ["श्रम ऐन, २०७४"]
    assert out["question"].startswith("My employer makes me work 12 hours")


def test_build_queries_with_llm_analysis_orders_and_weights(calls):
    analysis = generation.analyze_query(BOSS, "ne")
    queries = generation.build_queries(BOSS, analysis)
    weights = dict(queries)
    texts = [q for q, _ in queries]

    # raw romanised message is demoted once anything better exists
    assert queries[0] == (BOSS, 0.35)
    # the LLM's statutory phrasings come next, at full weight, in order
    assert queries[1:5] == [(q, 1.0) for q in analysis["queries_ne"]]
    assert (analysis["queries_en"][0], 0.4) in queries
    # the lexicon supports the LLM (0.6 combined, 0.3 per concept), glossary at 0.7
    lex_terms = generation.translit.expand(BOSS)
    assert "अतिरिक्त समय" in lex_terms and "कार्य घण्टा" in lex_terms
    assert weights[" ".join(lex_terms)] == 0.6
    assert all(w == 1.0 for q, w in queries if q in analysis["queries_ne"])
    assert max(w for q, w in queries if q not in analysis["queries_ne"]) < 1.0
    # nothing is duplicated as a query text with conflicting weights
    assert len(texts) == len(set(texts))
    # the wrong land-unit / water expansion is gone
    assert not any("रोपनी" in t or "पानी" in t for t in texts)


def test_build_queries_boosts_the_llm_named_law(calls, monkeypatch):
    """search() boosts titles from analysis['laws'] plus the lexicon's laws."""
    seen = {}

    class FakeIdx:
        digest = "x"

        def section(self, *a):
            return None

        def search(self, queries, top_k=8, boost_titles=(), category=None, **kw):
            seen.setdefault(category, {"queries": queries, "boost": list(boost_titles)})
            return []

    monkeypatch.setattr(generation, "get_index", lambda: FakeIdx())
    analysis = generation.analyze_query(BOSS, "ne")
    generation.search(BOSS, analysis, playbook=None)
    assert "श्रम ऐन, २०७४" in seen["law"]["boost"]
    assert seen["law"]["queries"][1][0] == "कार्य घण्टा दैनिक आठ घण्टा"


# ------------------------------------------------- graceful degradation
@pytest.mark.parametrize("exc", [TimeoutError("slow"), llm.LLMUnavailable("budget exhausted"),
                                 ValueError("bad")])
def test_failed_or_slow_llm_falls_back_to_the_deterministic_path(llm_on, monkeypatch, exc):
    def broken(*a, **k):
        raise exc

    monkeypatch.setattr(llm, "complete", broken)
    out = generation.analyze_query(BOSS, "ne")
    assert out["llm"] is False and out["intent"] == "legal" and out["queries_ne"] == []
    queries = generation.build_queries(BOSS, out)
    # no LLM: the lexicon expansion is the primary query, raw message is demoted
    assert queries[0] == (BOSS, 0.35)
    lex = " ".join(generation.translit.expand(BOSS))
    assert (lex, 1.0) in queries
    assert "अतिरिक्त समय" in lex


def test_unparseable_llm_json_falls_back_too(llm_on, monkeypatch):
    monkeypatch.setattr(llm, "complete", lambda *a, **k: "not json at all")
    out = generation.analyze_query(BOSS, "ne")
    assert out["llm"] is False and out["queries_ne"] == []


def test_no_llm_configured_never_calls_a_provider(monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GROQ_API_KEY"):
        monkeypatch.setattr(config, name, "", raising=False)
    generation._analysis_cache.data.clear()
    monkeypatch.setattr(llm, "complete", lambda *a, **k: (_ for _ in ()).throw(AssertionError("called")))
    if llm.available():
        pytest.skip("a provider is configured in this environment")
    assert generation.analyze_needs_llm(BOSS, "ne", None) is False
    out = generation.analyze_query(BOSS, "ne")
    assert out["llm"] is False
    assert any("अतिरिक्त समय" in q for q, _ in generation.build_queries(BOSS, out))


def test_analyze_call_is_bounded_by_the_fast_tier_budget():
    """The rewrite is one fast-tier JSON call inside config.ANALYZE_BUDGET_S
    (default 8s across all providers); slower than that raises and falls back."""
    assert 0 < config.ANALYZE_BUDGET_S <= 10


def test_prompt_lists_statutory_vocabulary_and_examples():
    p = generation.ANALYZE_SYSTEM
    for term in ("पारिश्रमिक", "कार्य घण्टा", "अतिरिक्त समय", "अंशबण्डा", "हकवाला", "जाहेरी दरखास्त",
                 "धरौटी जफत", "भित्री कारोबार"):
        assert term in p
    assert p.count('" -> ') >= 6            # worked examples
    assert "ROMANISED" in p
    assert len(p) < 5000                    # token cost matters on the free tier
