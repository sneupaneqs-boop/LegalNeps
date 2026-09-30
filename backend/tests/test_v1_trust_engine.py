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
    assert [r["source_ne"] for r in res if r.get("pinned")] == ["श्रम ऐन, २०७४, दफा 34", "श्रम ऐन, २०७४, दफा 162"]
    old = [r for r in res if r["category"] == "precedent" and (r.get("decided_bs") or 9999) < 2074]
    assert old and all(r["stale"] for r in old)


@requires_corpus
def test_tax_question_keeps_tax_acts():
    res = generation.search("What is the TDS rate on rent under the Income Tax Act?", dict(RAW))
    assert any("आयकर" in (r.get("doc_title_ne") or "") for r in res)


@requires_corpus
def test_run_emits_playbook_card_and_verification(monkeypatch):
    monkeypatch.setattr(llm, "available", lambda: True)
    monkeypatch.setattr(generation, "analyze_query", lambda m, l, h=None: {**RAW, "intent": "legal", "llm": False})
    answer = ("I understand your salary has not been paid, and that four months without income is very hard. "
              "Keep your appointment letter, pay slips and any messages from your employer safe. "
              "Under the Labour Act, 2074, Section 162, you can "
              "complain to the Labour Office within 6 months [2]. You must file within 35 days [2].\n\n**Precedent**")
    monkeypatch.setattr(llm, "stream", lambda system, user, **kw: iter([answer]))
    monkeypatch.setattr(generation.supa, "cache_get", lambda *a: None)
    monkeypatch.setattr(generation.supa, "cache_put", lambda *a: None)
    events = list(generation.run("My employer has not paid my salary for 4 months. What can I do?", "en"))
    meta = next(d for k, d in events if k == "meta")
    done = next(d for k, d in events if k == "done")
    assert meta["playbook"]["id"] == "unpaid_salary"
    assert done["verification"]["supported"] == 1
    assert done["verification"]["unverified"][0]["reason"] == "number_not_in_source"
    assert not done["answer"].rstrip().endswith("**Precedent**")


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
    q = "घरबेटीले deposit फिर्ता दिएन, के गर्ने?"
    res = generation.search(q, dict(RAW), playbook=generation._match_playbook(q, dict(RAW)))
    assert not any(r.get("source_ne") == "मुलुकी देवानी संहिता, २०७४, दफा 400" for r in res)


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
