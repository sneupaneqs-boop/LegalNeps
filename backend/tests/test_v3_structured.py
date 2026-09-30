"""V3: generate-then-verify. The model's JSON answer is checked sentence by sentence against the retrieved
passages (verbatim quote, numbers, sections, lexical support, source status); failing sentences are removed.
No real LLM is called: llm.complete is mocked."""
import json
import random

import pytest

from app import config, generation, llm, structured, verifier

QUOTE_NE = "मर्का परेको श्रमिकले सो कार्य भएको मितिले ६ महिनाभित्र उजुरी दिन सक्नेछ"
LABOUR = {"id": "law-1", "category": "law", "doc_type": "act", "section": "162", "status": "in_force",
          "source_en": "The Labour Act, 2074, Section 162", "source_ne": "श्रम ऐन, २०७४, दफा 162",
          "text_ne": "१६२. उजुरी दिन सक्ने: यो ऐन विपरीत कार्यबाट " + QUOTE_NE + "। "
                     "उजुरी सुन्ने निकायले एक महिनाभित्र निर्णय गर्नु पर्नेछ।",
          "text_en": "162. Complaint: A worker aggrieved by an act contrary to this Act may file a complaint within "
                     "six months from the date of the act."}
QUOTE_EN = "may file a complaint within six months from the date of the act"
RENT = {"id": "law-2", "category": "law", "doc_type": "act", "section": "386", "status": "in_force",
        "source_ne": "मुलुकी देवानी संहिता, २०७४, दफा 386", "source_en": "Muluki Civil Code, 2074, Section 386",
        "text_ne": "३८६. बहालमा दिँदा सम्झौता गर्नु पर्ने : कुनै व्यक्तिले घर बहालमा दिँदा देहायका कुराहरू खुलाई "
                   "बहालमा लिने व्यक्तिसँग लिखित सम्झौता गर्नु पर्नेछ।"}
RENT_QUOTE = "घर बहालमा दिँदा देहायका कुराहरू खुलाई बहालमा लिने व्यक्तिसँग लिखित सम्झौता गर्नु पर्नेछ"
CASE = {"id": "case-1", "category": "precedent", "source_ne": "ने.का.प. २०८० अंक ३ नि.नं. ११०००",
        "text_ne": "श्रमिकको पारिश्रमिक दाबी गर्दा लिखित प्रमाण पेश गर्नु पर्ने व्यहोरा सर्वोच्च अदालतले ठहर गरेको छ।"}
CASE_QUOTE = "पारिश्रमिक दाबी गर्दा लिखित प्रमाण पेश गर्नु पर्ने व्यहोरा"


def S(text, kind="rule", *cites):
    return {"text": text, "kind": kind, "cites": [{"n": n, "quote": q} for n, q in cites]}


def doc_of(*sentences, heading="Rules"):
    return {"blocks": [{"heading": heading, "sentences": list(sentences)}], "gaps": [], "follow_up_questions": []}


def check(sentence, sources=None):
    sources = sources or [LABOUR]
    views = [verifier._View(s) for s in sources]
    return verifier.check_structured_sentence(sentence, sources, views)


# ----------------------------------------------------------- deterministic checks

def test_verbatim_nepali_quote_supports_a_nepali_sentence():
    reason, cites = check(S("श्रम ऐन, २०७४ को दफा १६२ अनुसार श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)))
    assert reason is None and cites[0]["n"] == 1


def test_english_sentence_with_english_translation_quote():
    reason, _ = check(S("Under the Labour Act, 2074, Section 162, a worker can file a complaint within 6 months.",
                        "deadline", (1, QUOTE_EN)))
    assert reason is None


def test_english_sentence_with_nepali_quote_is_bridged_through_the_glossary():
    reason, _ = check(S("A worker aggrieved by an act contrary to the Act can complain within 6 months.",
                        "deadline", (1, QUOTE_NE)))
    assert reason is None


def test_altered_quote_is_removed():
    altered = QUOTE_NE.replace("६ महिनाभित्र", "३५ दिनभित्र")
    reason, _ = check(S("श्रमिकले ३५ दिनभित्र उजुरी दिन सक्छ।", "deadline", (1, altered)))
    assert reason == "quote_not_verbatim"


def test_invented_quote_and_too_short_quote_are_removed():
    assert check(S("श्रमिकले उजुरी दिन सक्छ।", "rule", (1, "कर्मचारीले अदालतमा मुद्दा हाल्न सक्छ भन्ने कुरा")))[0] == "quote_not_verbatim"
    assert check(S("श्रमिकले उजुरी दिन सक्छ।", "rule", (1, "उजुरी दिन")))[0] == "quote_too_short"


def test_number_not_in_the_quote_is_removed():
    reason, _ = check(S("श्रमिकले ३० दिनभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)))
    assert reason == "number_not_in_quote"


def test_number_word_and_devanagari_digits_match():
    assert check(S("A worker may complain within six months.", "deadline", (1, QUOTE_EN)))[0] is None
    assert check(S("श्रमिकले छ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)))[0] is None


def test_section_must_be_the_cited_sources_or_in_the_quote():
    assert check(S("Under Section 99 a worker may complain within 6 months.", "rule", (1, QUOTE_NE)))[0] == "section_not_in_quote"
    assert check(S("Under Section 162 a worker may complain within 6 months.", "rule", (1, QUOTE_NE)))[0] is None
    with_ref = "कुनै श्रमिकले दफा १०५ बमोजिम गरेको कार्यविरुद्ध उजुरी दिन सक्छ"
    src = {**LABOUR, "text_ne": "१६२. " + with_ref + "।"}
    assert check(S("A worker may complain against acts under Section 105.", "rule", (1, with_ref)), [src])[0] is None


@pytest.mark.parametrize("status", ["repealed", "lapsed", "bill"])
def test_repealed_lapsed_or_bill_source_is_removed(status):
    src = {**LABOUR, "status": status}
    assert check(S("श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)), [src])[0] == "stale_or_repealed_source"


def test_older_law_may_be_cited_when_the_sentence_says_so():
    src = {**LABOUR, "status": "repealed"}
    assert check(S("Under the older law, since repealed, a worker could complain within 6 months.", "rule", (1, QUOTE_NE)), [src])[0] is None


def test_ordinance_must_be_labelled():
    src = {**LABOUR, "status": "ordinance"}
    assert check(S("श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)), [src])[0] == "ordinance_unlabelled"
    assert check(S("यो अध्यादेश अनुसार श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)), [src])[0] is None


def test_unrelated_real_quote_cannot_launder_a_claim():
    # the quote is genuine but says nothing about deposits
    assert check(S("घरधनीले धरौटी फिर्ता दिनु पर्छ।", "rule", (1, QUOTE_NE)))[0] == "quote_unrelated"
    assert check(S("The landlord must return the tenant's deposit.", "rule", (1, QUOTE_NE)))[0] == "quote_unrelated"


def test_supreme_court_claim_must_cite_a_precedent():
    s = "सर्वोच्च अदालतले श्रमिकले लिखित प्रमाण पेश गर्नु पर्ने ठहर गरेको छ।"
    assert check(S(s, "rule", (1, QUOTE_NE)))[0] == "court_claim_cites_statute"
    assert check(S(s, "rule", (2, CASE_QUOTE)), [LABOUR, CASE])[0] is None


def test_uncited_rule_wording_or_numbers_are_removed_whatever_the_kind():
    assert check(S("The employer must pay wages.", "advice"))[0] == "no_citation"
    assert check(S("Keep your documents for 30 days.", "empathy"))[0] == "no_citation"
    assert check(S("Consider a complaint under the Labour Act.", "procedure"))[0] == "no_citation"


def test_empathy_and_plain_advice_pass_uncited_but_uncited_procedure_needs_the_playbook():
    assert check(S("I understand how stressful this is.", "empathy"))[0] is None
    assert check(S("Keep your appointment letter and pay slips safe.", "advice"))[0] is None
    views = [verifier._View(LABOUR)]
    step = S("Go to the Labour Office in your district.", "procedure")
    assert verifier.check_structured_sentence(step, [LABOUR], views, set())[0] == "uncited_procedure"
    guide = {t for t in verifier.tokenize("Where to go: the Labour Office of your district")}
    assert verifier.check_structured_sentence(step, [LABOUR], views, guide)[0] is None


def test_bad_citation_number_is_removed():
    assert check(S("श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (5, QUOTE_NE)))[0] == "bad_citation"


def test_one_bad_cite_is_dropped_but_a_good_one_keeps_the_sentence():
    reason, cites = check(S("श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, "काल्पनिक वाक्यांश जो स्रोतमा छैन पक्कै"), (1, QUOTE_NE)))
    assert reason is None and len(cites) == 1 and cites[0]["quote"] == QUOTE_NE


def test_ocr_garbled_passage_still_matches_a_correct_quote_fuzzily():
    garbled = LABOUR["text_ne"].replace("श्रमिकले", "श्रमकिले")  # one OCR-garbled word in the span
    src = {**LABOUR, "text_ne": garbled}
    assert check(S("श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)), [src])[0] is None


def test_fuzzy_match_never_forgives_a_changed_number():
    src = {**LABOUR, "text_ne": LABOUR["text_ne"].replace("६ महिना", "६० महिना")}
    assert check(S("श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)), [src])[0] == "quote_not_verbatim"


def test_pua_glyphs_danda_punctuation_and_digit_script_are_normalised():
    src = {**LABOUR, "text_ne": "१६२. उजुरी: मर्का परेको श्रमिकले सो कार्य भएको मितिले 6 महिनाभित्र, उजुरी दिन सक्नेछ॥"}
    assert check(S("श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE + "।")), [src])[0] is None


def test_any_contiguous_slice_of_the_source_verifies_property():
    rng = random.Random(3)
    words = RENT["text_ne"].split()
    for _ in range(60):
        i = rng.randrange(0, len(words) - 6)
        j = rng.randrange(i + 5, min(len(words), i + 25) + 1)
        assert verifier.quote_in_source(" ".join(words[i:j]), verifier._View(RENT)) is None


def test_a_slice_with_one_word_swapped_never_verifies_property():
    rng = random.Random(5)
    words = LABOUR["text_ne"].split()
    view = verifier._View(LABOUR)
    for _ in range(40):
        i = rng.randrange(0, len(words) - 8)
        span = words[i:i + 6]
        span[rng.randrange(2, 4)] = "कल्पितशब्द"
        span2 = span[:3] + ["अर्कोकल्पित"] + span[3:]  # two foreign words in 7: below the 90% bar
        assert verifier.quote_in_source(" ".join(span2), view) == "quote_not_verbatim"


# -------------------------------------------------------------- whole document

def test_failing_sentences_are_removed_and_report_keeps_the_legacy_shape():
    doc = doc_of(
        S("श्रम ऐन, २०७४ को दफा १६२ अनुसार श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)),
        S("श्रमिकले ३५ दिनभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)),
        S("मालिकलाई ५ वर्ष जेल हुन्छ।", "penalty"),
    )
    out, rep = verifier.verify_structured(doc, [LABOUR])
    assert [s["text"][:6] for s in out["blocks"][0]["sentences"]] == ["श्रम ऐ"]
    assert rep["claims"] == rep["supported"] == 1 and rep["unverified"] == []
    assert rep["cited_laws"] == 1 and rep["cited_precedents"] == 0
    assert rep["removed"]["count"] == 2
    assert set(rep["removed"]["reasons"]) == {"number_not_in_quote", "no_citation"}
    assert "35" not in json.dumps(rep) and "३५" not in json.dumps(rep, ensure_ascii=False)  # no user text leaks


def test_heading_left_without_sentences_is_dropped():
    doc = {"blocks": [
        {"heading": "Good", "sentences": [S("A worker may complain within six months.", "deadline", (1, QUOTE_EN))]},
        {"heading": "Empty after checking", "sentences": [S("The employer will be jailed for 5 years.", "penalty")]},
    ]}
    out, rep = verifier.verify_structured(doc, [LABOUR])
    assert [b["heading"] for b in out["blocks"]] == ["Good"]
    assert rep["removed"]["blocks_dropped"] == 1
    assert "Empty after checking" not in structured.render(out, "en")


def test_render_makes_the_markdown_the_ui_already_shows():
    doc = {"blocks": [
        {"heading": "", "sentences": [S("I understand your worry.", "empathy")]},
        {"heading": "Key rules", "sentences": [S("A worker may complain within 6 months.", "deadline", (1, QUOTE_EN))]},
    ], "gaps": ["The sources retrieved do not cover the labour court."], "follow_up_questions": ["When was your last salary paid?"]}
    out, _ = verifier.verify_structured(doc, [LABOUR])
    md = structured.render(out, "en", "DISCLAIMER")
    assert md.startswith("I understand your worry.\n\n**Key rules**\n- A worker may complain within 6 months [1].")
    assert "**What the sources don't cover**\n- The sources retrieved do not cover the labour court." in md
    assert md.endswith("DISCLAIMER")


def test_gaps_with_numbers_and_questions_with_legal_claims_are_not_rendered():
    doc = {"blocks": [{"heading": "R", "sentences": [S("A worker may complain within six months.", "deadline", (1, QUOTE_EN)),
                                                      S("A worker may complain within 6 months of the act.", "deadline", (1, QUOTE_EN))]}],
           "gaps": ["The law gives 30 days for wages.", "The sources retrieved do not cover the labour court."],
           "follow_up_questions": ["You must file within 30 days, right?", "Did you sign a contract?"]}
    res = structured.build(json.dumps(doc), [LABOUR], "en")
    assert "30 days" not in res["answer"] and "must file" not in res["answer"]
    assert "labour court" in res["answer"] and "Did you sign a contract?" in res["answer"]


# ------------------------------------------------------------ parsing / salvage

FULL = {"blocks": [
    {"heading": "", "sentences": [S("I understand your worry.", "empathy")]},
    {"heading": "Rules", "sentences": [
        S("A worker may complain within 6 months.", "deadline", (1, QUOTE_EN)),
        S("A worker aggrieved by an act contrary to the Act can complain.", "rule", (1, "A worker aggrieved by an act contrary to this Act may file a complaint")),
        S("Second rule text that will be cut", "rule", (1, QUOTE_EN))]},
], "gaps": ["The sources retrieved do not cover the labour court."], "follow_up_questions": []}


def test_complete_json_parses_and_fenced_json_too():
    raw = json.dumps(FULL)
    assert structured.parse_answer(raw) == (structured._norm_doc(FULL), True)
    assert structured.parse_answer("```json\n" + raw + "\n```")[1] is True
    assert structured.parse_answer("Here you go: " + raw)[1] is True


def test_truncated_json_keeps_every_complete_sentence_and_drops_the_partial_one():
    raw = json.dumps(FULL, ensure_ascii=False)
    cut = raw[:raw.index("Second rule") + 12]  # mid-sentence inside the third sentence
    doc, complete = structured.parse_answer(cut)
    assert complete is False
    texts = [s["text"] for b in doc["blocks"] for s in b["sentences"]]
    assert texts == ["I understand your worry.", "A worker may complain within 6 months.",
                     "A worker aggrieved by an act contrary to the Act can complain."]


def test_truncation_between_blocks_and_inside_a_heading():
    raw = json.dumps(FULL, ensure_ascii=False)
    doc, complete = structured.parse_answer(raw[:raw.index('"heading": "Rules"') + 8])
    assert complete is False and [b["heading"] for b in doc["blocks"]] == [""]


def test_truncated_answer_renders_only_whole_sentences_and_is_flagged():
    raw = json.dumps(FULL, ensure_ascii=False)
    cut = raw[:raw.index("Second rule") + 12]
    res = structured.build(cut, [LABOUR], "en", cut_off=True)
    assert res["truncated"] is True and res["answer"]
    assert "Second rule" not in res["answer"]
    assert res["answer"].rstrip().endswith(("].", "."))
    assert res["verification"]["truncated"] is True


def test_cut_off_flag_alone_marks_a_parseable_answer_truncated():
    assert structured.parse_answer(json.dumps(FULL), cut_off=True)[1] is False


def test_garbage_is_unparseable_and_repair_gets_one_attempt():
    calls = []

    def repair(bad):
        calls.append(bad)
        return json.dumps(FULL)

    res = structured.build("Sorry, here is your answer in prose: workers may complain.", [LABOUR], "en", repair=repair)
    assert len(calls) == 1 and res["repaired"] is True and res["answer"]
    broken = structured.build("prose only", [LABOUR], "en", repair=lambda bad: "still not json")
    assert broken["answer"] is None and broken["verification"]["mode"] == "extractive_fallback"


def test_fewer_than_two_verified_rules_falls_back():
    doc = doc_of(S("A worker may complain within six months.", "deadline", (1, QUOTE_EN)),
                 S("The employer will be jailed for 5 years.", "penalty"))
    res = structured.build(json.dumps(doc), [LABOUR], "en")
    assert res["answer"] is None and res["verification"]["mode"] == "extractive_fallback"
    assert res["verification"]["removed"]["count"] == 1


def test_nepali_document_end_to_end():
    doc = {"blocks": [
        {"heading": "", "sentences": [S("तपाईंको चिन्ता मैले बुझें।", "empathy")]},
        {"heading": "मुख्य नियम", "sentences": [
            S("श्रम ऐन, २०७४ को दफा १६२ अनुसार श्रमिकले ६ महिनाभित्र उजुरी दिन सक्छ।", "deadline", (1, QUOTE_NE)),
            S("मुलुकी देवानी संहिता, २०७४ को दफा ३८६ अनुसार घर बहालमा दिँदा लिखित सम्झौता गर्नु पर्छ।", "rule", (2, RENT_QUOTE))]}],
        "gaps": ["मैले पाएका स्रोतहरूले धरौटी फिर्ता गर्ने म्याद समेटेका छैनन्।"], "follow_up_questions": []}
    res = structured.build(json.dumps(doc, ensure_ascii=False), [LABOUR, RENT], "ne", disclaimer=generation.DISCLAIMER_NE)
    md = res["answer"]
    assert "**मुख्य नियम**" in md and "[1]" in md and "[2]" in md and "**स्रोतहरूले नसमेटेको कुरा**" in md
    assert md.endswith(generation.DISCLAIMER_NE)
    assert res["verification"]["claims"] == 2 == res["verification"]["supported"]


# ------------------------------------------------------------------ entailment

def test_entailment_removes_no_and_keeps_yes_and_partial():
    doc = doc_of(S("A worker may complain within six months.", "deadline", (1, QUOTE_EN)),
                 S("A worker aggrieved by an act may file a complaint.", "rule", (1, "aggrieved by an act contrary to this Act may file a complaint")),
                 S("I understand.", "empathy"))
    asked = {}

    def call(system, user, **kw):
        asked["items"] = json.loads(user)["items"]
        return json.dumps({"results": [{"id": 0, "verdict": "yes"}, {"id": 1, "verdict": "no"}]})

    out, dropped, ran = structured.entailment_filter(doc, call)
    assert ran and dropped == 1 and len(asked["items"]) == 2  # empathy is not sent
    assert [s["text"] for s in out["blocks"][0]["sentences"]] == ["A worker may complain within six months.", "I understand."]


def test_entailment_fails_open():
    doc = doc_of(S("A worker may complain within six months.", "deadline", (1, QUOTE_EN)))

    def boom(*a, **k):
        raise llm.LLMUnavailable("quota")

    out, dropped, ran = structured.entailment_filter(doc, boom)
    assert out is doc and dropped == 0 and ran is False


def test_build_runs_entailment_only_when_given_and_recounts():
    good = doc_of(S("A worker may complain within six months.", "deadline", (1, QUOTE_EN)),
                  S("A worker aggrieved by an act may file a complaint.", "rule", (1, "aggrieved by an act contrary to this Act may file a complaint")),
                  S("A worker may also complain within 6 months of the act.", "rule", (1, QUOTE_EN)))
    entail = lambda d: structured.entailment_filter(d, lambda *a, **k: json.dumps({"results": [{"id": 2, "verdict": "no"}]}))  # noqa: E731
    res = structured.build(json.dumps(good), [LABOUR], "en", entail=entail)
    assert res["verification"]["claims"] == 2 and res["verification"]["removed"]["by_reason"] == {"not_entailed": 1}
    assert res["verification"]["entailment"] == "ran"
    assert "entailment" not in structured.build(json.dumps(good), [LABOUR], "en")["verification"]


# ------------------------------------------------------------------ streaming

def test_chunks_are_small_lossless_and_never_split_a_citation():
    text = "**Key rules**\n- A worker may complain within 6 months [12].\n- Another rule [3][4]. " * 5
    pieces = list(structured.chunks(text, 40))
    assert "".join(pieces) == text
    assert all(len(p) <= 60 for p in pieces)
    assert not any(p.rstrip().endswith("[") for p in pieces)


# ----------------------------------------------------------- pipeline (mocked LLM)

@pytest.fixture()
def pipeline(monkeypatch):
    monkeypatch.setattr(llm, "available", lambda: True)
    monkeypatch.setattr(config, "STREAM_CHUNK_DELAY_S", 0)
    monkeypatch.setattr(generation, "analyze_query", lambda m, l, h=None: {
        "queries_ne": [], "queries_en": [], "laws": [], "wants_precedent": True, "intent": "legal", "llm": False})
    monkeypatch.setattr(generation, "search", lambda *a, **k: [dict(LABOUR), dict(RENT)])
    monkeypatch.setattr(generation, "_match_playbook", lambda m, a: None)
    monkeypatch.setattr(generation, "get_index", lambda: type("I", (), {"digest": "t"})())
    monkeypatch.setattr(generation.supa, "cache_get", lambda *a: None)
    monkeypatch.setattr(generation.supa, "cache_put", lambda *a: None)
    generation._answer_cache.data.clear()
    seen = {"calls": []}

    def fake(system, user, **kw):
        seen["calls"].append((system, kw))
        return seen["reply"]

    monkeypatch.setattr(llm, "complete", fake)
    monkeypatch.setattr(llm, "was_cut_off", lambda reason=None: seen.get("cut", False))
    return seen


def _run(msg="My employer has not paid my salary for 4 months. What can I do?", lang="en"):
    events = list(generation.run(msg, lang))
    return events, {k: d for k, d in events if k in ("meta", "done", "status")}


GOOD = {"blocks": [
    {"heading": "", "sentences": [S("I understand your salary has not been paid.", "empathy")]},
    {"heading": "Key rules", "sentences": [
        S("Under the Labour Act, 2074, Section 162, a worker can file a complaint within 6 months.", "deadline", (1, QUOTE_EN)),
        S("A landlord must sign a written agreement under Muluki Civil Code, 2074, Section 386.", "rule", (2, RENT_QUOTE)),
        S("The employer must also pay 15 days' wages.", "rule", (1, QUOTE_EN))]}],
    "gaps": ["The sources retrieved do not cover which office orders payment."], "follow_up_questions": []}


def test_run_streams_status_then_verified_deltas_then_done(pipeline):
    pipeline["reply"] = json.dumps(GOOD)
    events, by = _run()
    kinds = [k for k, _ in events]
    assert kinds[0] == "meta" and kinds[1] == "status" and kinds[-1] == "done"
    assert by["status"] == {"stage": "checking sources"}
    deltas = [d for k, d in events if k == "delta"]
    assert len(deltas) > 3 and all(len(d) < 80 for d in deltas)
    done = by["done"]
    assert "".join(deltas) == done["answer"] and done["llm_used"] is True
    assert "15 days" not in done["answer"]                       # the invented number never reached the client
    assert "written agreement" in done["answer"] and "[2]" in done["answer"]
    v = done["verification"]
    assert v["claims"] == v["supported"] == 2 and v["unverified"] == [] and v["removed"]["count"] == 1
    assert done["prompt_version"] == generation.ANSWER_PROMPT_VERSION
    system, kw = pipeline["calls"][0]
    assert system == generation.ANSWER_SYSTEM and kw["json_mode"] is True and kw["max_tokens"] == config.ANSWER_MAX_TOKENS_EN


def test_nepali_gets_a_larger_token_budget(pipeline):
    pipeline["reply"] = json.dumps(GOOD)
    _run("मेरो तलब ६ महिनादेखि आएको छैन", "ne")
    assert pipeline["calls"][0][1]["max_tokens"] == config.ANSWER_MAX_TOKENS_NE > config.ANSWER_MAX_TOKENS_EN


def test_run_falls_back_to_the_provisions_when_too_little_survives(pipeline):
    pipeline["reply"] = json.dumps(doc_of(S("The employer will be jailed for 5 years.", "penalty")))
    events, by = _run()
    done = by["done"]
    assert done["llm_used"] is False and done["verification"]["mode"] == "extractive_fallback"
    assert done["answer"].startswith(generation.UNVERIFIED_HEADER["en"]) and "**[1]" in done["answer"]
    assert "jailed" not in done["answer"]
    assert generation._answer_cache.data == {}                    # fallbacks are never cached


def test_run_unparseable_json_gets_one_repair_then_falls_back(pipeline):
    pipeline["reply"] = "this is prose, not json"
    events, by = _run()
    assert by["done"]["llm_used"] is False and by["done"]["answer"].startswith(generation.UNVERIFIED_HEADER["en"])
    assert len(pipeline["calls"]) == 2                            # answer + exactly one repair


def test_run_truncated_json_is_salvaged_not_cut_mid_sentence(pipeline):
    raw = json.dumps(GOOD, ensure_ascii=False)
    pipeline["reply"] = raw[:raw.index("The employer must also") + 25]
    pipeline["cut"] = True
    _, by = _run()
    done = by["done"]
    assert done["llm_used"] is True and done["verification"]["truncated"] is True
    assert "The employer must also" not in done["answer"]
    assert "written agreement" in done["answer"]


def test_run_provider_failure_gives_the_extractive_answer(pipeline, monkeypatch):
    def boom(*a, **k):
        raise llm.LLMUnavailable("no provider")

    monkeypatch.setattr(llm, "complete", boom)
    _, by = _run()
    assert by["done"]["llm_used"] is False and "AI summary unavailable" in by["done"]["answer"]


def test_free_tier_skips_entailment_by_default_and_env_flag_enables_it(pipeline, monkeypatch):
    pipeline["reply"] = json.dumps(GOOD)
    _run()
    assert len(pipeline["calls"]) == 1
    monkeypatch.setattr(config, "ENTAILMENT_CHECK", True)
    generation._answer_cache.data.clear()
    _run()
    assert len(pipeline["calls"]) == 3                            # answer + entailment (answer call of run 1 counted)


def test_paid_tier_runs_entailment_on_the_paid_model(pipeline, monkeypatch):
    calls = []

    def paid(model, system, user, **kw):
        calls.append(model)
        if system == generation.ANSWER_SYSTEM:
            return json.dumps(GOOD), {"input_tokens": 100, "output_tokens": 50}
        return json.dumps({"results": [{"id": 0, "verdict": "yes"}]}), {"input_tokens": 10, "output_tokens": 5}

    monkeypatch.setattr(llm, "paid_complete", paid)
    events = list(generation.run("My employer has not paid my salary. What can I do?", "en", tier="haiku"))
    done = next(d for k, d in events if k == "done")
    assert len(calls) == 2 and done["usage"] == {"input_tokens": 110, "output_tokens": 55}
    assert done["verification"]["entailment"] == "ran"
    assert pipeline["calls"] == []                                # never touched the free chain


def test_verifier_crash_degrades_to_extractive(pipeline, monkeypatch):
    pipeline["reply"] = json.dumps(GOOD)
    monkeypatch.setattr(verifier, "verify_structured", lambda *a, **k: 1 / 0)
    _, by = _run()
    assert by["done"]["llm_used"] is False


# ---------------------------------------------------------- cache / versioning

def test_pipeline_version_and_fingerprint_cover_the_new_modules():
    import inspect
    assert generation.PIPELINE_VERSION.startswith("p9-")           # p8 cached prose answers can never be served
    src = inspect.getsource(generation._pipeline_fingerprint)
    assert "structured.py" in src and "verifier.py" in src and "text_norm.py" in src
    assert generation.ANSWER_SYSTEM.startswith(structured.STRUCTURED_ANSWER_SYSTEM[:40])


def test_old_prose_cache_entry_is_not_served(monkeypatch):
    monkeypatch.setattr(generation, "get_index", lambda: type("I", (), {"digest": "t"})())
    key = generation._answer_cache_key("q", "en")
    assert key.startswith(generation.PIPELINE_VERSION) and not key.startswith("p8")


# ------------------------------------------------------------------ llm hooks

def test_llm_cut_off_detection():
    assert llm.was_cut_off("length") and llm.was_cut_off("max_tokens") and llm.was_cut_off("FinishReason.MAX_TOKENS")
    assert not llm.was_cut_off("stop") and not llm.was_cut_off("end_turn") and not llm.was_cut_off(None)


def test_stream_endpoint_forwards_the_status_event(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from app import retrieval, supa
    from app.main import app
    from fixtures import ENTRIES

    monkeypatch.setattr(retrieval, "CACHE_DIR", tmp_path)
    idx = retrieval.Index([dict(e) for e in ENTRIES], "v3-test")
    monkeypatch.setattr(retrieval, "_index", idx)
    monkeypatch.setattr(generation, "get_index", lambda: idx)
    monkeypatch.setattr(config, "STREAM_CHUNK_DELAY_S", 0)
    supa._ip_hits.clear()

    def fake_run(message, language="auto", history=None, tier="free"):
        yield "meta", {"language": "en", "sources": [], "analysis": {}}
        yield "status", {"stage": "checking sources"}
        yield "delta", "hello"
        yield "done", {"answer": "hello", "llm_used": True, "cached": False, "llm_calls": 1}

    monkeypatch.setattr("app.routes.chat.stream_answer", fake_run)
    with TestClient(app) as c:
        r = c.post("/api/chat/stream", json={"message": "hello there", "language": "en"})
    events = [json.loads(l) for l in r.text.splitlines() if l.strip()]
    assert [e["type"] for e in events] == ["meta", "status", "delta", "done"]
    assert events[1]["stage"] == "checking sources"


# ------------------------------------------------------------- review tooling

def test_answer_review_rows_and_aggregate(pipeline):
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval"))
    import answer_review as ar

    pipeline["reply"] = json.dumps(GOOD)
    result = generation.answer_question("My employer has not paid my salary for 4 months. What can I do?", "en")
    body = {**result, "sources": [{"n": i, "id": s["id"], "citation": s["source_en"], "status": "in_force",
                                   "category": "law", "snippet": "snip"} for i, s in enumerate(result["sources"], 1)]}

    class NoCorpus(ar.Passages):
        def __init__(self):
            self.api, self.local, self._entries = "", {}, []

    row = ar.review_row({"id": "x1", "q": "salary"}, body, NoCorpus())
    assert row["mode"] == "structured" and row["truncated"] is False
    assert [s["cites"][0]["n"] for s in row["sentences"]] == [1, 2]
    assert row["sentences"][0]["cites"][0]["quote"] == QUOTE_EN
    assert row["sentences"][0]["cites"][0]["passage"]["where"] == "snippet"
    agg = ar.aggregate([row])
    assert agg["cited_sentences_kept"] == 2 and agg["sentences_removed"] == 1 and agg["fallback_rate"] == 0.0
    assert agg["removal_reasons"] == {"number_not_in_quote": 1}
    assert agg["uncited_numbers_in_rendered_sentences"] == 0
