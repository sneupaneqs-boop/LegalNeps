"""V2.7: forms / schedules are not provisions, the strict ("direct") topical fit, the truthful fallback caveat, abstaining
when no passage fits directly, contiguous citation labels and the reply language - all built from the real cases of the V3.3
set-B live review (b01 b02 b03 b05 b16 b18 ...)."""
import json
from pathlib import Path

import pytest

from app import config, fit_reply, generation, topical_fit as tf
from app.retrieval import CORPUS_DIR, doc_slug, get_index
from app.text_norm import guess_language

requires_corpus = pytest.mark.skipif(not (CORPUS_DIR / "manifest.json").exists(), reason="corpus shards not present")
DATA = Path(__file__).parent / "data"
CRPC = "मुलुकी फौजदारी कार्यविधि संहिता, २०७४"


def _entry(title: str, section: str) -> dict:
    e = get_index().section(doc_slug(title), section)
    assert e is not None, (title, section)
    return e


# ---------------------------------------------------------------- forms and schedules
@requires_corpus
@pytest.mark.parametrize("title,section,why", [
    (CRPC, "5 (7)", "schedule_form"),                       # b01: the power-of-attorney form (अनुसूची-३६ वारेसनामाको ढाँचा)
    (CRPC, "5 (6)", None),                                  # b01: the bail-bond form (blanks, then अनुसूची-३२)
    ("हातहतियार खरखजाना नियमावली, २०२८", "5 (3)", None),  # b05: arms-licence form; schedule heading or blanks, either is a form
    ("मुलुकी देवानी कार्यविधि संहिता, २०७४", "9 (2)", None),  # b02: अनुसूची-५ receipt form
])
def test_forms_and_schedules_are_not_substantive(title, section, why):
    got = tf.non_substantive(_entry(title, section))
    assert got in ("schedule_form", "blank_form") and (why is None or got == why)


@requires_corpus
def test_real_provisions_are_never_flagged_as_forms():
    """Over-removal: the passages cited by ALL labelled supported sentences (reviews 1, 2 and B) stay substantive."""
    n = 0
    for fname in ("v33_review_fixture.json", "v27_reviewB_fixture.json"):
        for s in json.loads((DATA / fname).read_text(encoding="utf-8"))["sentences"]:
            if s["label"] != "supported":
                continue
            for c in s["cites"]:
                n += 1
                assert tf.non_substantive(c) is None, (s["key"], c.get("source_ne"))
    assert n > 100
    for title, sec in (("श्रम ऐन, २०७४", "31"), ("मुलुकी देवानी संहिता, २०७४", "389"), ("सवारी तथा यातायात व्यवस्था ऐन, २०४९", "163")):
        assert tf.non_substantive(_entry(title, sec)) is None


def test_constitution_schedules_and_precedents_are_exempt():
    assert tf.non_substantive({"doc_type": "constitution", "text_ne": "अनुसूची–६ (धारा ५७ को उपधारा (२) ...)"}) is None
    assert tf.non_substantive({"category": "precedent", "text_ne": "… … … … …"}) is None
    assert tf.non_substantive({"text_ne": "अनुसूची-६ (नियम ५ सँग सम्बन्धित) बसाइँ सराईको फाराम"}) == "schedule_form"


def test_a_question_that_asks_for_a_form_keeps_forms():
    assert tf.asks_for_form("वारेसनामाको ढाँचा कहाँ पाइन्छ? अनुसूची")
    assert tf.asks_for_form("Where can I get the application form?") and tf.asks_for_form("send me a sample draft")
    assert not tf.asks_for_form("मेरो नाममा रहेको जग्गा दाजुले नक्कली सहीछाप गरेर बेचिदियो")
    form = {"id": "f", "category": "law", "doc_title_ne": "मुलुकी फौजदारी कार्यविधि संहिता, २०७४", "section": "5 (7)",
            "text_ne": "अनुसूची-३६ (दफा ८९ को उपदफा (५) सँग सम्बन्धित) वारेसनामाको ढाँचा … बस्ने … सँगको"}
    for q, flagged in (("मेरो जग्गा नक्कली सहीछाप", True), ("वारेसनामाको ढाँचा चाहियो", False)):
        prof = tf.make_profile(q)
        v = tf.judge([form], tf.Scorer(prof))[0]
        assert ("non_substantive:schedule_form" in v.reasons) is flagged


@requires_corpus
def test_gate_marks_forms_off_topic_and_never_offers_them_as_related():
    q = "मेरो नाममा रहेको जग्गा दाजुले नक्कली सहीछाप गरेर बेचिदियो, के गर्ने?"
    srcs = [dict(_entry(CRPC, "5 (7)"), score=0.5), dict(_entry(CRPC, "5 (6)"), score=0.4)]
    an = {"queries_ne": [], "queries_en": [], "laws": [], "wants_precedent": True, "llm": False, "question": q}
    generation.apply_topical_gate(q, an, srcs, None)
    assert all(s["off_topic"] and any(w.startswith("non_substantive") for w in s["off_topic_why"]) for s in srcs)
    out = fit_reply.abstain_answer(srcs, "ne", "DISC")
    assert "वारेसनामाको ढाँचा" not in out and "**[" not in out   # nothing offered under "possibly related"


# ---------------------------------------------------------------- strict (direct) fit
def test_named_law_makes_a_passage_direct_and_exempts_it_from_the_weak_score():
    q = "bike le thokera bhagyo, hospital ko kharcha ko lagi kasari dabi garne?"
    prof = tf.make_profile(q)
    assert "सवारी तथा यातायात व्यवस्था ऐन" in prof.named_laws
    mv = {"id": "m", "category": "law", "doc_title_ne": "सवारी तथा यातायात व्यवस्था ऐन, २०४९", "title_ne": "क्षतिपूर्ति",
          "section": "163", "text_ne": "१६३. क्षतिपूर्ति दिनु पर्ने: सवारी दुर्घटना भएमा चालकले क्षतिपूर्ति दिनु पर्नेछ।"}
    other = dict(mv, id="o", doc_title_ne="विश्वविद्यालय ऐन, २०५०")
    v1, v2 = tf.judge([mv, other], tf.Scorer(prof), ranks=[8, 8])
    assert v1.direct and v1.direct_why == "named_law" and "low_topical_fit" not in v1.reasons
    assert not v2.direct


def test_the_company_in_my_salary_question_does_not_make_the_companies_act_direct():
    q = "तीन महिनादेखि तलब आएको छैन तर कम्पनीले जागिर छाड्न दिँदैन, के गर्ने?"
    prof = tf.make_profile(q)
    assert prof.named_laws == frozenset({"श्रम ऐन"})
    comp = {"id": "c", "category": "law", "doc_title_ne": "कम्पनी ऐन, २०६३", "title_ne": "वार्षिक साधारण सभा", "section": "76",
            "text_ne": "७६. वार्षिक साधारण सभा : कम्पनीको वार्षिक साधारण सभा हरेक वर्ष बस्नु पर्नेछ।"}
    assert not tf.judge([comp], tf.Scorer(prof))[0].direct


# ---------------------------------------------------------------- the fallback caveat is truthful
def _src(i, direct, off=False, pinned=False):
    return {"id": f"s{i}", "category": "law", "source_ne": f"A{i}", "source_en": f"A{i}", "text_ne": f"पाठ{i}", "fit_score": 0.0,
            "fit_direct": direct, **({"off_topic": True} if off else {}), **({"pinned": True} if pinned else {})}


def test_caveat_matches_what_is_shown():
    all_direct = [_src(1, True), _src(2, True)]
    assert fit_reply.DIRECT_NOTE["en"] in fit_reply.extractive_answer(all_direct, "en", "D")
    mixed = fit_reply.extractive_answer([_src(1, True), _src(2, False), _src(3, False)], "en", "D")
    assert "Only [1] clearly match" in mixed and "may not apply" in mixed and fit_reply.DIRECT_NOTE["en"] not in mixed
    mixed_ne = fit_reply.extractive_answer([_src(1, True), _src(2, False)], "ne", "D")
    assert "[1] मात्र" in mixed_ne and fit_reply.DIRECT_NOTE["ne"] not in mixed_ne


def test_no_direct_fit_abstains_instead_of_listing_unrelated_provisions(monkeypatch):
    srcs = [_src(1, False), _src(2, False), _src(3, False)]
    out = fit_reply.extractive_answer(srcs, "en", "D")                  # b03 / b05 / b16: nothing fits the subject
    assert out.startswith("I couldn't find a provision that directly answers this")
    assert "match the subject of your question" not in out
    monkeypatch.setattr(config, "FIT_ABSTAIN_STRICT", False)            # switch: the V3.3 list with the honest "closest" note
    out = fit_reply.extractive_answer(srcs, "ne", "D")
    assert fit_reply.CLOSEST_NOTE["ne"] in out and fit_reply.DIRECT_NOTE["ne"] not in out
    # a pinned (verified) provision always counts as direct
    assert not fit_reply.extractive_answer([_src(1, False, pinned=True)], "en", "D").startswith("I couldn't find")


def test_citation_labels_are_contiguous_after_display_order():
    srcs = [_src(1, True), _src(2, False, off=True), _src(3, True), _src(4, False, off=True), _src(5, False), _src(6, True)]
    srcs.append({"id": "p1", "category": "precedent", "source_ne": "P", "text_ne": "x", "fit_score": 0.0})
    ordered = fit_reply.order_for_display(srcs)
    assert [s["id"] for s in ordered] == ["s1", "s3", "s6", "s5", "p1", "s2", "s4"]   # direct, other on-topic, precedents, ruled out
    ordered[0]["pinned"] = False
    out = fit_reply.extractive_answer(ordered, "en", "D")
    assert "**[1] A1**" in out and "**[2] A3**" in out and "**[3] A6**" in out and "[4]" not in out and "[5]" not in out


def test_abstain_related_list_is_numbered_from_the_front():
    srcs = fit_reply.order_for_display([_src(1, False, off=True), _src(2, False, off=True), _src(3, False)])
    srcs[1]["off_topic_why"] = ["low_topical_fit"]
    out = fit_reply.abstain_answer(srcs, "en", "D")
    assert "**[1] A3**" in out


# ---------------------------------------------------------------- reply language
@pytest.mark.parametrize("text,want", [
    ("nagarikta harayo, pratilipi kasari line?", "ne"),                       # b18 was answered in English
    ("ghar dhani le bhada 3 mahina ko advance liyera pachi farkaudaina, ke garne?", "ne"),
    ("mero jagga ko lalpurja haraye, ke garne", "ne"),
    ("What is the notice period for rent in Nepal?", "en"),
    ("How do I get a duplicate citizenship certificate if lost?", "en"),
    ("Explain in English: nagarikta harayo, pratilipi kasari line?", "en"),   # the person asked for English
    ("timro answer in english please, mero ghar bhada badhyo", "en"),
    ("nepali ma bhana: what is the VAT rate", "ne"),
])
def test_reply_language_for_romanised_nepali_and_explicit_requests(text, want):
    assert guess_language(text) == want


def test_run_answers_a_romanised_question_in_nepali(monkeypatch):
    seen = {}
    monkeypatch.setattr(generation.llm, "available", lambda: False)
    monkeypatch.setattr(generation, "analyze_query", lambda m, l, h=None: seen.setdefault("lang", l) and
                        {"queries_ne": [], "queries_en": [], "laws": [], "wants_precedent": True, "intent": "legal", "llm": False})
    monkeypatch.setattr(generation, "search", lambda *a, **k: [])
    monkeypatch.setattr(generation, "_match_playbook", lambda m, a: None)
    monkeypatch.setattr(generation, "get_index", lambda: type("I", (), {"digest": "t"})())
    monkeypatch.setattr(generation.supa, "cache_get", lambda *a: None)
    generation._answer_cache.data.clear()
    events = list(generation.run("nagarikta harayo, pratilipi kasari line?", "auto"))
    assert next(d for k, d in events if k == "meta")["language"] == "ne"


# ---------------------------------------------------------------- the pre-generation decision (b03 as it was served live)
@requires_corpus
def test_run_abstains_when_no_retrieved_statute_fits_the_subject_and_does_not_call_the_model(monkeypatch):
    from app import llm
    q = "तीन महिनादेखि तलब आएको छैन तर कम्पनीले जागिर छाड्न दिँदैन, के गर्ने?"
    live = [dict(_entry("कम्पनी ऐन, २०६३", s), score=0.3) for s in ("76", "28", "53 (1)")]   # what V3.3 retrieved for b03
    monkeypatch.setattr(llm, "available", lambda: True)
    monkeypatch.setattr(config, "STREAM_CHUNK_DELAY_S", 0)
    monkeypatch.setattr(generation, "analyze_query", lambda m, l, h=None: {
        "queries_ne": [], "queries_en": [], "laws": [], "wants_precedent": True, "intent": "legal", "llm": False})
    monkeypatch.setattr(generation, "_match_playbook", lambda m, a: None)
    monkeypatch.setattr(generation, "search", lambda *a, **k: [dict(s) for s in live])
    monkeypatch.setattr(generation.supa, "cache_get", lambda *a: None)
    monkeypatch.setattr(llm, "complete", lambda *a, **k: pytest.fail("the model must not be called"))
    monkeypatch.setattr(llm, "stream_json", lambda *a, **k: pytest.fail("the model must not be called"))
    generation._answer_cache.data.clear()
    done = dict(generation.run(q, "ne"))["done"]
    assert done["verification"]["mode"] == "abstain" and done["llm_used"] is False
    assert done["answer"].startswith("मैले खोजेका स्रोतहरूमा तपाईंको प्रश्नको सिधै जवाफ दिने प्रावधान भेटिएन")
    assert "विषयसँग मिल्छन्" not in done["answer"]          # no false "these match the subject of your question"
