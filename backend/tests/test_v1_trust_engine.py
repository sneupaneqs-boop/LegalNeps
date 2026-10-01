"""V1: trust engine - deterministic citation verifier, status on every source,
playbook-first retrieval, fiscal-domain filter, stale-precedent flagging."""
import pytest

from app import generation, llm, verifier
from app.retrieval import CORPUS_DIR

requires_corpus = pytest.mark.skipif(
    not (CORPUS_DIR / "manifest.json").exists(), reason="built corpus shards not present"
)

LABOUR = {"category": "law", "doc_type": "act", "section": "162", "source_en": "The Labour Act, 2074, Section 162",
          "source_ne": "श्रम ऐन, २०७४, दफा 162",
          "text_ne": "१६२. उजुरी दिन सक्ने: यो ऐन विपरीत कार्यबाट मर्का परेको श्रमिकले सो कार्य भएको मितिले ६ महिनाभित्र उजुरी दिन सक्नेछ।"}
OLD_CASE = {"category": "precedent", "source_ne": "ने.का.प. २०२७ अंक १ नि.नं. ५५०",
            "text_ne": "तलब दाबी ३५ दिनभित्र गर्नुपर्ने।", "stale": True}
CONSTITUTION = {"category": "law", "doc_type": "constitution", "section": "18", "source_ne": "नेपालको संविधान, धारा 18",
                "text_ne": "१८. समानताको हक"}


# ------------------------------------------------------------- verifier ----

def test_supported_claim_with_matching_number_passes():
    ans = "You can complain to the Labour Office within 6 months under the Labour Act, 2074, Section 162 [1]."
    out, rep = verifier.verify(ans, [LABOUR])
    assert rep["claims"] == 1 and rep["supported"] == 1 and rep["unverified"] == []
    assert "⚠" not in out


def test_devanagari_number_matches_ascii_claim():
    ans = "श्रम ऐन, २०७४ को दफा १६२ अनुसार ६ महिनाभित्र उजुरी दिन सकिन्छ [1]।"
    _, rep = verifier.verify(ans, [LABOUR], "ne")
    assert rep["supported"] == 1


def test_wrong_number_is_flagged():
    ans = "You must file within 35 days under the Labour Act, 2074 [1]."
    out, rep = verifier.verify(ans, [LABOUR])
    assert rep["unverified"][0]["reason"] == "number_not_in_source"
    assert "not verified" in out


def test_uncited_legal_claim_is_flagged():
    ans = "Consider filing a criminal complaint for wage theft under the Labour Act."
    out, rep = verifier.verify(ans, [LABOUR])
    assert rep["unverified"][0]["reason"] == "no_citation"
    assert "⚠" in out


def test_citation_out_of_range_is_flagged():
    _, rep = verifier.verify("The Labour Act, 2074 gives this right [7].", [LABOUR])
    assert rep["unverified"][0]["reason"] == "bad_citation"


def test_number_supported_only_by_stale_precedent_is_flagged():
    ans = "A salary claim must be filed within 35 days according to the Supreme Court [2]."
    _, rep = verifier.verify(ans, [LABOUR, OLD_CASE])
    assert rep["unverified"][0]["reason"] == "stale_authority"


def test_section_not_in_cited_source_is_flagged():
    ans = "Under the Labour Act, 2074, Section 99, you may complain [1]."
    _, rep = verifier.verify(ans, [LABOUR])
    assert rep["unverified"][0]["reason"] == "section_not_in_source"


def test_non_legal_sentences_are_not_counted():
    ans = "I understand you are worried about this.\n\nPlease keep copies of your letters."
    out, rep = verifier.verify(ans, [LABOUR])
    assert rep["claims"] == 0 and out == ans


def test_report_counts_cited_laws_and_precedents():
    ans = ("You can complain within 6 months under the Labour Act, Section 162 [1]. "
           "The Supreme Court has discussed salary claims in an older case [2].")
    _, rep = verifier.verify(ans, [LABOUR, OLD_CASE])
    assert rep["cited_laws"] == 1 and rep["cited_precedents"] == 1


# ---------------------------------------------------------- tidy_answer ----

def test_trailing_empty_heading_is_removed():
    ans = "Answer text [1].\n\n**संबन्धित सर्वोच्च अदालतको निर्णय**\n"
    assert generation.tidy_answer(ans, [LABOUR]).endswith("[1].")


def test_dhara_becomes_dafa_for_statutes_only():
    assert "दफा ४००" in generation.tidy_answer("मुलुकी देवानी संहिता, धारा ४०० अनुसार [1]", [LABOUR])
    assert "धारा १८" in generation.tidy_answer("संविधानको धारा १८ अनुसार [1]", [CONSTITUTION])


# ------------------------------------------------------ stale precedents ---

def test_precedent_older_than_governing_act_is_stale():
    laws = [{"doc_title_ne": "श्रम ऐन, २०७४"}]
    precs = [{"source_ne": "ने.का.प. २०२७ अंक १ नि.नं. ५५०"}, {"source_ne": "ने.का.प. २०८० अंक ३ नि.नं. ११०००"}]
    out = generation.mark_stale_precedents(laws, precs)
    assert [p["stale"] for p in out] == [False, True]  # current-law precedent sorted first
    assert out[1]["decided_bs"] == 2027 and out[1]["governing_law_bs"] == 2074


def test_annual_finance_act_does_not_make_precedents_stale():
    laws = [{"doc_title_ne": "आर्थिक ऐन, २०८२"}, {"doc_title_ne": "आयकर ऐन, २०५८"}]
    out = generation.mark_stale_precedents(laws, [{"source_ne": "ने.का.प. २०७८ अंक १२ नि.नं. १०८०५"}])
    assert out[0]["stale"] is False


# ------------------------------------------------------- live retrieval ----

RAW = {"queries_ne": [], "queries_en": [], "laws": [], "wants_precedent": True}


@requires_corpus
def test_every_search_result_has_a_status():
    res = generation.search("employer not paying salary", dict(RAW))
    assert res and all(r.get("status") for r in res)


@requires_corpus
def test_deposit_question_pins_civil_code_and_drops_tax_acts():
    q = "घरबेटीले deposit फिर्ता दिएन, के गर्ने?"
    pb = generation._match_playbook(q, dict(RAW))
    assert pb and pb["id"] == "deposit_not_returned"
    res = generation.search(q, dict(RAW), playbook=pb)
    assert res[0]["pinned"] and "मुलुकी देवानी संहिता" in res[0]["source_ne"]
    laws = [r for r in res if r["category"] == "law"]
    assert not any("आयकर" in (r.get("doc_title_ne") or "") for r in laws)


@requires_corpus
def test_salary_question_flags_1970s_precedents_as_stale():
    q = "My employer has not paid my salary for 4 months. What can I do?"
    pb = generation._match_playbook(q, dict(RAW))
    res = generation.search(q, dict(RAW), playbook=pb)
    # V2.7: the unpaid-wages route puts Labour Act ss.35 and 148 in front of the plan's own pins (s.34, s.162)
    assert [r["source_ne"] for r in res if r.get("pinned")] == [
        "श्रम ऐन, २०७४, दफा 35", "श्रम ऐन, २०७४, दफा 148", "श्रम ऐन, २०७४, दफा 34", "श्रम ऐन, २०७४, दफा 162"]
    old = [r for r in res if r["category"] == "precedent" and (r.get("decided_bs") or 9999) < 2074]
    assert old and all(r["stale"] for r in old)


@requires_corpus
def test_tax_question_keeps_tax_acts():
    res = generation.search("What is the TDS rate on rent under the Income Tax Act?", dict(RAW))
    assert any("आयकर" in (r.get("doc_title_ne") or "") for r in res)


@requires_corpus
def test_run_emits_playbook_card_and_verification(monkeypatch):
    # migrated in V3: the answer is now one JSON object whose sentences carry verbatim quotes; the invented
    # "35 days" is REMOVED (it used to be shown with a warning mark) and `unverified` is always empty
    import json
    from app import config
    monkeypatch.setattr(llm, "available", lambda: True)
    monkeypatch.setattr(config, "STREAM_CHUNK_DELAY_S", 0)
    monkeypatch.setattr(generation, "analyze_query", lambda m, l, h=None: {**RAW, "intent": "legal", "llm": False})
    q1 = "प्रत्येक श्रमिकले काम शुरु गरेको मितिदेखि पारिश्रमिक तथा सुविधा पाउनेछ"
    q2 = "श्रमिकले पाउने पारिश्रमिक तथा सुविधा यो ऐन तथा यस ऐन अन्तर्गत बनेको नियममा तोकिएभन्दा कम नहुने गरी रोजगार सम्झौतामा उल्लेख भए बमोजिम हुनेछ"
    q3 = "कुनै व्यक्ति, रोजगारदाता, श्रमिक वा पदाधिकारीले यो ऐन वा यस ऐन अन्तर्गत बनेको नियम विपरीत कार्यगरेमा"
    reply = {"blocks": [
        {"heading": "", "sentences": [{"text": "I understand that four months without income is very hard.", "kind": "empathy", "cites": []}]},
        {"heading": "Key rules", "sentences": [
            {"text": "Under the Labour Act, 2074, Section 34, a worker gets wages and benefits from the day work starts.",
             "kind": "rule", "cites": [{"n": 3, "quote": q1}]},   # V2.7: routed ss.35, 148 are [1], [2]; s.34 is [3]
            {"text": "A worker's wages cannot be lower than the Act or the employment contract provides.",
             "kind": "rule", "cites": [{"n": 3, "quote": q2}]},
            {"text": "You must file within 35 days.", "kind": "deadline", "cites": [{"n": 4, "quote": q3}]}]},
    ], "gaps": [], "follow_up_questions": []}
    monkeypatch.setattr(llm, "complete", lambda system, user, **kw: json.dumps(reply, ensure_ascii=False))
    monkeypatch.setattr(generation.supa, "cache_get", lambda *a: None)
    monkeypatch.setattr(generation.supa, "cache_put", lambda *a: None)
    events = list(generation.run("My employer has not paid my salary for 4 months. What can I do?", "en"))
    meta = next(d for k, d in events if k == "meta")
    done = next(d for k, d in events if k == "done")
    assert meta["playbook"]["id"] == "unpaid_salary"
    assert done["verification"]["supported"] == done["verification"]["claims"] == 2
    assert done["verification"]["unverified"] == []
    # the invented deadline, and the empathy line that restates the user's own "four months" (a number
    # with no quote behind it is never rendered, whatever kind the model gave it)
    assert set(done["verification"]["removed"]["reasons"]) == {"number_not_in_quote", "no_citation"}
    assert "35 days" not in done["answer"] and "Section 34" in done["answer"]


def test_number_words_in_statute_match_digits_in_claim():
    src = {**LABOUR, "text_ne": "सो कार्यभए गरेको मितिले छ\nमहिनाभित्र उजुरी दिन सक्नेछ।"}
    _, rep = verifier.verify("You can complain within 6 months under Section 162 [1].", [src])
    assert rep["supported"] == 1
    _, rep = verifier.verify("You can complain within six months under Section 162 [1].", [src])
    assert rep["supported"] == 1


def test_nepali_verb_chha_is_not_read_as_six():
    src = {**LABOUR, "text_ne": "यो अधिकार छ।"}
    _, rep = verifier.verify("You must complain within 6 months [1].", [src])
    assert rep["unverified"][0]["reason"] == "number_not_in_source"


def test_restated_user_fact_is_not_a_legal_claim():
    _, rep = verifier.verify("I understand four months without income is very hard for you.", [LABOUR])
    assert rep["claims"] == 0


def test_supreme_court_claim_citing_only_a_statute_is_flagged():
    ans = "सुप्रीम कोर्टले लिखित प्रमाणको महत्त्वलाई जोड दिएको छ [1]।"
    _, rep = verifier.verify(ans, [LABOUR], "ne")
    assert rep["unverified"][0]["reason"] == "court_claim_cites_statute"


@requires_corpus
def test_playbook_excluded_provision_never_reaches_the_evidence():
    # V2.5: s.400 is no longer excluded from the deposit plan (the V3 review found s.400(3) - deduction of the
    # rent for a missing notice from the ADVANCE - governs the question); the exclude_provisions mechanism itself
    # is exercised by the bank plan, which keeps the private-creditor cap of s.478 out of a bank-loan answer
    q = "bank loan ma late payment ko penal interest kati lagauna milchha?"
    pb = generation._match_playbook(q, dict(RAW))
    assert pb and pb["id"] == "bank_loan_penal_interest" and pb["exclude_provisions"]
    res = generation.search(q, dict(RAW), playbook=pb)
    assert not any(r.get("source_ne") == "मुलुकी देवानी संहिता, २०७४, दफा 478" for r in res)
    dq = "घरबेटीले deposit फिर्ता दिएन, के गर्ने?"
    dpb = generation._match_playbook(dq, dict(RAW))
    assert not dpb.get("exclude_provisions")
    assert any(p["section"] == "400" for p in dpb["provisions"])


def test_old_ordinances_are_lapsed_and_recent_ones_temporary():
    from app.retrieval import _current_bs_year, _temporal_status
    y = _current_bs_year()
    assert _temporal_status("रेल्वे अध्यादेश, २०७८", "act", "in_force") == ("act", "lapsed")
    assert _temporal_status(f"कुनै अध्यादेश, {y}", "act", "in_force") == ("act", "ordinance")
    assert _temporal_status("संविधान सभा सदस्य निर्वाचन अध्यादेश, २०७०", "constitution", "in_force") == ("act", "lapsed")
    assert _temporal_status("मध्यस्थता ऐन, २०५५ को संशोधन सम्बन्धी अध्ययन", "act", "unknown") == ("other", "unknown")
    assert _temporal_status("श्रम ऐन, २०७४", "act", "in_force") == ("act", "in_force")


@requires_corpus
def test_lapsed_ordinances_never_returned_by_default():
    from app.retrieval import get_index
    res = get_index().search(["रेल्वे अध्यादेश"], top_k=20, category="law")
    assert not any(r.get("status") == "lapsed" for r in res)


def test_regulator_directives_only_surface_for_banking_securities_company_questions():
    from app.generation import _is_regulator_query, _REGULATOR_DOC
    assert _REGULATOR_DOC.match("reg-nrb-3d2ed04c46-0") and _REGULATOR_DOC.match("reg-sebon-x-1")
    assert not _REGULATOR_DOC.match("reg-lawcommission-8dc8911ba9-0")  # gap-filled acts are ordinary law
    assert _is_regulator_query("बैंकले ब्याज दर कति लिन पाउँछ?", {})
    assert _is_regulator_query("How do I apply for an IPO?", {})
    assert not _is_regulator_query("घरबेटीले धरौटी फिर्ता गरेन", {})
    assert not _is_regulator_query("My employer has not paid my salary", {})


@pytest.mark.parametrize("query,expected", [
    ("मेरो श्रीमानले मलाई कुटपिट गर्छ, के गर्ने?", "domestic_violence"),
    ("my husband hits me every night", "domestic_violence"),
    ("छिमेकीले कुटपिट गर्यो", "physical_assault"),  # not domestic: shared word alone mustn't win
    ("manpower le thagyo", "foreign_employment_fraud"),
])
def test_playbook_matcher_real_phrasings(query, expected):
    from app.playbook_matcher import _reset_cache_for_tests, match
    _reset_cache_for_tests()
    assert match(query) == expected


def test_procurement_insurance_labour_regulator_passages_stay_in_their_field(monkeypatch):
    from app import generation
    hits = [{"id": "reg-ppmo-a-1", "doc_title_ne": "ई-खरिद निर्देशिका"}, {"id": "reg-nia-b-1", "doc_title_ne": "बीमा निर्देशन"},
            {"id": "reg-moless-c-1", "doc_title_ne": "श्रम अडिट मापदण्ड"}, {"id": "law-x-1", "doc_title_ne": "मुलुकी देवानी संहिता, २०७४"}]

    class _Idx:
        def search(self, *a, **kw):
            return [dict(h) for h in hits] if kw.get("category") == "law" else []

    monkeypatch.setattr(generation, "get_index", lambda: _Idx())
    ids = lambda q: [s["id"] for s in generation.search(q, {}, top_k=8, precedent_k=0)]
    assert ids("घरबेटीले धरौटी फिर्ता गरेन") == ["law-x-1"]
    assert "reg-nia-b-1" in ids("बीमा दाबी भुक्तानी भएन") and "reg-ppmo-a-1" not in ids("बीमा दाबी भुक्तानी भएन")
    assert "reg-moless-c-1" in ids("company le talab diyena")
    assert "reg-ppmo-a-1" in ids("बोलपत्र रद्द भयो")


def test_pipeline_version_tracks_prompts_lexicon_and_playbooks(tmp_path, monkeypatch):
    # a stale answer_cache row survived a prompt/lexicon change once: the
    # romanised "boss ... overtime" question kept its pre-fix answer
    from app import generation
    base = generation._pipeline_fingerprint()
    assert generation.PIPELINE_VERSION.endswith("-" + base)
    monkeypatch.setattr(generation, "ANALYZE_SYSTEM", generation.ANALYZE_SYSTEM + " ")
    assert generation._pipeline_fingerprint() != base


@pytest.mark.parametrize("words,expected", [
    ("अठ्चालीस घण्टा", "48 "), ("अठचालीस घण्टा", "48 "), ("पच्चीस दिन", "25 "), ("पच्चिस दिन", "25 "),
    ("सन्तानब्बे दिन", "97 "), ("दश प्रतिशत", "10 "), ("पैँतीस दिन", "35 "),
])
def test_nepali_number_words_before_units(words, expected):
    from app.verifier import _words_to_digits
    assert _words_to_digits(words).startswith(expected)


def test_number_word_alone_is_not_converted():
    from app.verifier import _words_to_digits
    assert _words_to_digits("यो कानून हो र यो छ ।") == "यो कानून हो र यो छ ।"


@pytest.mark.parametrize("text", ["पच्चीस लाख रुपैयाँ", "२५ लाख", "25 lakh", "2,500,000"])
def test_lakh_and_crore_amounts_match_digits(text):
    from app.verifier import _haystack_numbers
    assert "2500000" in _haystack_numbers({"text_ne": text})


def test_labour_act_hours_claim_verified_against_spelled_out_statute():
    from app.verifier import verify
    src = [{"n": 1, "category": "law", "section": "28", "doc_title_ne": "श्रम ऐन, २०७४",
            "text_ne": "२८. काम गर्नेसमयः (१) रोजगारदाताले श्रमिकलाई प्रतिदिन आठ घण्टा र एक हप्तामा "
                       "अठ्चालीस घण्टाभन्दा बढी समय हुने गरी काममा लगाउन पाइने छैन।"}]
    ok = "प्रतिदिन अधिकतम ८ घण्टा (हप्तामा ४८ घण्टा) भन्दा बढी काममा लगाउन पाइँदैन [1]।"
    bad = "प्रतिदिन १० घण्टा भन्दा बढी काममा लगाउन पाइँदैन [1]।"
    assert verify(ok, src, "ne")[1]["unverified"] == []
    assert verify(bad, src, "ne")[1]["unverified"][0]["reason"] == "number_not_in_source"
