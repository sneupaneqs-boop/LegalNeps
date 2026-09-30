"""V2.5: retrieval / playbook-routing fixes from the V3 live review.

Root causes covered: (1) a loosely matched playbook pinned provisions of an unrelated law (rw05, rw10, rw23,
rw24, rw25) - now vetoed (`not_keywords`), or dropped when retrieval does not corroborate it; (2) banking
questions never saw the NRB Unified Directive and got the private-creditor Civil Code rules instead; (3) recurring
situations had no playbook; (4) lexicon / spelling gaps. Real corpus, BM25 or hybrid - the assertions hold for both."""
import pytest

from app import generation, playbook_matcher, playbooks, translit
from app.retrieval import CORPUS_DIR, get_index

requires_corpus = pytest.mark.skipif(
    not (CORPUS_DIR / "manifest.json").exists(), reason="built corpus shards not present"
)
RAW = {"queries_ne": [], "queries_en": [], "laws": [], "wants_precedent": False}

BANK_LOAN = "bank loan ma late payment ko penal interest kati lagauna milchha?"
MIN_BALANCE = "bank le account ma minimum balance nabhayeko bhanera paisa katyo. yo milchha?"
BOSS = "boss le din ko 12 ghanta kaam garauchha, overtime ko paisa pani dinna. yo milchha?"
KUWAIT = "Kuwait pugda job chhaina, company le kaam nai dinna. ghar pharkiye. ticket ra agency ko kharcha kasari firta paune?"


def _pinned(res):
    return [r for r in res if r.get("pinned")]


# ------------------------------------------------------------ wrong pins ---

@requires_corpus
def test_private_lender_plan_is_vetoed_for_a_bank_loan_question():
    assert generation._playbook_id_for(BANK_LOAN) != "unpaid_personal_loan"
    assert generation._playbook_id_for(BANK_LOAN) == "bank_loan_penal_interest"
    # ...but a loan between people is still a private-lender question
    assert generation._playbook_id_for("my friend lent me money and now sahu le byaj magyo") != "bank_loan_penal_interest"


def test_not_keywords_veto_a_matched_playbook():
    ids = [m.playbook_id for m in playbook_matcher.score_playbooks("bank ma deposit rakheko, security deposit")]
    assert "deposit_not_returned" not in ids
    ids = [m.playbook_id for m in playbook_matcher.score_playbooks("landlord won't return my security deposit")]
    assert "deposit_not_returned" in ids


def test_keyword_words_scattered_over_a_message_count_half():
    """"ghar kharcha dinna" is not in a message about a job abroad whose words happen to include ghar, kharcha and
    dinna in three different sentences (V3 review rw05: the maintenance plan scored 8.0)."""
    ranked = playbook_matcher.score_playbooks(KUWAIT)
    assert not ranked or ranked[0].playbook_id != "maintenance_alimony"
    assert playbook_matcher.match("ghar kharcha dinna, 3 ota bachha chha") == "maintenance_alimony"


@requires_corpus
def test_unrelated_untrusted_playbook_is_dropped_by_the_relevance_gate():
    """foreign_employment_fraud offered for a bank-charge question: none of its provisions is retrieved, so it is
    dropped (pins, card and guide) instead of displacing the NRB directive."""
    pb = playbooks.get_playbook("foreign_employment_fraud")
    pb["_trusted"] = False
    res, kept = generation.search_with_playbook(MIN_BALANCE, dict(RAW), top_k=8, precedent_k=0, playbook=pb)
    assert kept is None and not _pinned(res)
    assert any(r["id"].startswith("reg-nrb-") for r in res)


@requires_corpus
def test_a_trusted_playbook_keeps_its_pins():
    pb = playbooks.get_playbook("foreign_employment_fraud")
    pb["_trusted"] = True
    res, kept = generation.search_with_playbook(MIN_BALANCE, dict(RAW), top_k=8, precedent_k=0, playbook=pb)
    assert kept is not None and _pinned(res)


@requires_corpus
def test_gate_keeps_a_plan_whose_own_provisions_are_retrieved():
    q = "My employer has not paid my salary for 4 months. What can I do?"
    pb = generation._match_playbook(q, dict(RAW))
    assert pb["id"] == "unpaid_salary"
    pb["_trusted"] = False  # force the retrieval check
    res, kept = generation.search_with_playbook(q, dict(RAW), top_k=8, precedent_k=0, playbook=pb)
    if generation.playbook_support(pb, [r for r in res if not r.get("pinned")]):
        assert kept is not None  # only asserted when retrieval corroborates (dense model present or not)


def test_playbook_support_counts_a_neighbouring_section_of_the_same_law():
    pb = {"provisions": [{"law_title_ne": "श्रम ऐन, २०७४", "section": "162"}]}
    hit = [{"doc_title_ne": "श्रम ऐन, २०७४", "section": "163 (2)", "title_ne": "x"}]
    miss = [{"doc_title_ne": "श्रम ऐन, २०७४", "section": "40", "title_ne": "x"},
            {"doc_title_ne": "अर्को ऐन", "section": "162", "title_ne": "x"}]
    assert generation.playbook_support(pb, hit) == 1
    assert generation.playbook_support(pb, miss) == 0
    assert generation.playbook_support(None, hit) == 0


@requires_corpus
def test_long_playbook_leaves_room_for_retrieval():
    q = "mero shreemanko mrityu bhayo. sasu-sasura le sampatti ma tero kei haq chhaina bhanchhan. hamro ek chhora chha."
    pb = generation._match_playbook(q, dict(RAW))
    assert pb and len(pb["provisions"]) > 5
    res, _ = generation.search_with_playbook(q, dict(RAW), top_k=8, precedent_k=0, playbook=pb)
    assert len(_pinned(res)) <= 8 - generation.PIN_RESERVED_FOR_RETRIEVAL
    assert len(res) == 8


# -------------------------------------------------- regulator routing ------

def test_bank_cue_needs_a_bank_and_a_service_or_a_standalone_phrase():
    for q in (BANK_LOAN, MIN_BALANCE, "बैंकले मेरो गुनासो सुन्दैन। कहाँ उजुरि गर्ने?",
              "credit card ko interest rate kati lagchha", "how do I send remittance from abroad",
              "forex kati dollar lina milchha", "atm bata paisa kataye"):
        assert generation._is_bank_query(q), q
    for q in ("landlord won't return my deposit", "cheque bounce bhayo", "my friend took 5 lakh from me",
              "public company ko AGM bolayeko chhaina", "police le arrest garyo"):
        assert not generation._is_bank_query(q), q


@requires_corpus
def test_bank_loan_question_surfaces_the_nrb_directive_and_not_the_private_creditor_cap():
    res, kept = generation.search_with_playbook(BANK_LOAN, dict(RAW), top_k=8, precedent_k=0,
                                                playbook=generation._match_playbook(BANK_LOAN, dict(RAW)))
    assert kept and kept["id"] == "bank_loan_penal_interest"
    assert any(r["id"].startswith("reg-nrb-") for r in res)
    penal = [r for r in res if "पेनाल ब्याजदर" in (r.get("text_ne") or "")]
    assert penal, "IPD 15/082 clause 3 (penal interest <= 2 percentage points) must be in the sources"
    assert not any((r.get("doc_title_ne") or "").startswith("मुलुकी देवानी संहिता") and r.get("section") in ("478", "481")
                   for r in res)


@requires_corpus
def test_minimum_balance_question_pins_the_account_charge_clause_first():
    pb = generation._match_playbook(MIN_BALANCE, dict(RAW))
    assert pb["id"] == "bank_account_charges_complaint"
    res, _ = generation.search_with_playbook(MIN_BALANCE, dict(RAW), top_k=8, precedent_k=0, playbook=pb)
    assert "न्यूनतम मौज्दात भन्दा कम" in _pinned(res)[0]["text_ne"]


@requires_corpus
def test_non_banking_question_gets_no_regulator_routing():
    res = generation.search("boss le talab dinna", dict(RAW), top_k=8, precedent_k=0)
    assert not any(r["id"].startswith("reg-nrb-") for r in res)


def test_regulator_cues_cover_english_romanised_and_devanagari():
    for q in ("penal interest on my loan", "minimum balance charge", "baink ko karja", "एटीएम कार्डको शुल्क",
              "न्यूनतम मौज्दात", "विप्रेषण रकम", "hundi"):
        assert generation._is_regulator_query(q, {}), q


# ------------------------------------------------------- new playbooks -----

@requires_corpus
def test_new_playbook_provisions_resolve_including_directive_entries():
    for pid in ("bank_loan_penal_interest", "bank_account_charges_complaint"):
        pb = playbooks.get_playbook(pid)
        directive = [p for p in pb["provisions"] if p.get("entry_title_contains")]
        assert directive, pid
        for p in directive:
            assert p["slug"] and p["citation"] and p["section"]
    idx = get_index()
    e = playbooks.lookup_entry(idx, {"law_title_ne": "परिपत्र नं. १० (क, ख, ग) २०८२/८३: एकीकृत निर्देशन, २०८२ जारी गरिएको सम्बन्धमा ।",
                                     "entry_title_contains": "१५/०८२ - कर्जाको ब्याजदर", "contains": ["पेनाल ब्याजदर"]})
    assert e and "२ प्रतिशत विन्दु" in e["text_ne"].replace("\n", " ")
    assert playbooks.lookup_entry(idx, {"law_title_ne": "श्रम ऐन, २०७४", "section": "28"})["section"] == "28"
    assert playbooks.lookup_entry(idx, {"law_title_ne": "श्रम ऐन, २०७४", "contains": ["यस्तो पाठ छैन"]}) is None


@pytest.mark.parametrize("query,expected", [
    (BOSS, "overtime_working_hours"),
    ("employer makes me work 10 hours a day, no overtime pay", "overtime_working_hours"),
    ("साहुले ब्याज मागेको छ तर लिखतमा ब्याज कतै लेखेकै छैन", "loan_interest_dispute"),
    (MIN_BALANCE, "bank_account_charges_complaint"),
    (BANK_LOAN, "bank_loan_penal_interest"),
    ("My wife wants a divorce, who gets custody of our daughter?", "child_custody"),
    ("mero dai lai police le arrest garyo. jamanat/dharauti rakhera kasari chhutaune?", "bail_release_after_arrest"),
    ("Shreemati lai sasu ra shreemanle dowry nadeko bhanera rojai sataunchhan", "dowry_harassment"),
    ("private company register garna kati jana shareholder chahinchha?", "company_registration_shareholders"),
    ("public company ko AGM 2 barsa dekhi bolayeko chhaina. shareholder le ke garna sakchha?", "agm_not_held"),
    ("doctor le galat operation garera bihari ko mrityu bho. ke garne?", "medical_negligence_death"),
    ("mero shreemanko mrityu bhayo. sasu-sasura le sampatti ma tero kei haq chhaina bhanchhan", "inheritance_share"),
])
def test_recurring_situations_route_to_their_playbook(query, expected):
    assert generation._playbook_id_for(query) == expected


@requires_corpus
@pytest.mark.parametrize("pid,must_cite", [
    ("overtime_working_hours", {"28", "31"}),
    ("bank_loan_penal_interest", {"55 (2)", "57 (1)"}),
    ("loan_interest_dispute", {"479", "478", "481"}),
    ("bail_release_after_arrest", {"67", "68"}),
    ("dowry_harassment", {"174", "176"}),
    ("company_registration_shareholders", {"9", "5"}),
    ("agm_not_held", {"76"}),
    ("medical_negligence_death", {"181"}),
    ("child_custody", {"115"}),
    ("inheritance_share", {"214", "239"}),
    ("deposit_not_returned", {"400"}),
    ("foreign_employment_fraud", {"36", "60"}),
    ("right_to_information_request", {"10"}),
])
def test_playbooks_cite_the_provisions_the_live_review_found_missing(pid, must_cite):
    got = {p["section"] for p in playbooks.get_playbook(pid)["provisions"]}
    assert must_cite <= got


def test_every_v25_playbook_is_flagged_for_advocate_review_in_the_audit():
    from pathlib import Path
    audit = (Path(__file__).resolve().parents[2] / "docs" / "PLAYBOOK_AUDIT.md").read_text(encoding="utf-8")
    for pid in ("overtime_working_hours", "bank_loan_penal_interest", "bank_account_charges_complaint",
                "loan_interest_dispute", "bail_release_after_arrest", "dowry_harassment",
                "company_registration_shareholders", "agm_not_held", "medical_negligence_death"):
        line = next((l for l in audit.splitlines() if pid in l), "")
        assert "NEEDS-ADVOCATE-REVIEW" in line, pid


# ------------------------------------------------- query-side fixes ---------

@pytest.mark.parametrize("text,expected", [
    ("bank le account ma minimum balance nabhayeko bhanera paisa katyo", "न्यूनतम मौज्दात"),
    ("bank loan ma penal interest", "पेनाल ब्याज"),
    ("bank ko gunaso sunena", "गुनासो सुनवाई"),
    ("boss le 12 ghanta kaam garauchha overtime dinna", "आठ घण्टा"),
    ("online order ma nakali aayo, return garna dinna", "वस्तु फिर्ता"),
    ("private company register garna", "प्राइभेट कम्पनी"),
    ("Kuwait pugda job chhaina ghar pharkiye", "स्वदेश"),
    ("wife wants divorce, who gets custody", "नाबालक"),
])
def test_v25_lexicon_entries_map_to_statutory_terms(text, expected):
    assert expected in translit.expand(text)


def test_bank_terms_carry_the_bfi_act_as_their_statute():
    assert translit._LAW["BFI"] in translit.laws("bank le account ma minimum balance nabhayeko")
    assert translit._LAW["ECOM"] in translit.laws("online order return garna dinna")


@requires_corpus
def test_devanagari_nasal_spelling_slip_is_corrected_only_when_the_index_knows_the_fix():
    assert generation.respell_devanagari("बुबाले अन्श दिनुभएन") == "बुबाले अंश दिनुभएन"
    assert generation.respell_devanagari("बुबाले अंश दिनुभएन") == "बुबाले अंश दिनुभएन"
    assert generation.respell_devanagari("plain english") == "plain english"
    queries = [q for q, _ in generation.build_queries("बुबाले अन्श दिनुभएन", dict(RAW))]
    assert "बुबाले अंश दिनुभएन" in queries
    pb = generation._match_playbook("बुबाले अन्श दिनुभएन, म छोरी हुँ", dict(RAW))
    assert pb and pb["id"] == "inheritance_share"


# ------------------------------------------------- run(): card follows the gate

def _run_with(monkeypatch, sources, msg):
    from app import llm
    monkeypatch.setattr(llm, "available", lambda: False)
    monkeypatch.setattr(generation, "analyze_query", lambda m, l, h=None: {
        **RAW, "intent": "legal", "llm": False, "question": m})
    monkeypatch.setattr(generation, "_match_playbook", lambda m, a: playbooks.get_playbook("unpaid_salary"))
    monkeypatch.setattr(generation, "search", lambda *a, **k: sources)
    monkeypatch.setattr(generation.supa, "cache_get", lambda *a: None)
    monkeypatch.setattr(generation.supa, "cache_put", lambda *a: None)
    generation._answer_cache.data.clear()
    return dict(generation.run(msg, "en"))


@requires_corpus
def test_run_shows_no_action_plan_card_when_the_gate_dropped_the_plan(monkeypatch):
    src = {"id": "x1", "category": "law", "source_ne": "श्रम ऐन, २०७४, दफा 162", "text_ne": "उजुरी",
           "status": "in_force", "doc_type": "act"}
    meta = _run_with(monkeypatch, [dict(src)], "v25 card gate dropped")["meta"]
    assert meta["playbook"] is None
    meta = _run_with(monkeypatch, [{**src, "pinned": True}], "v25 card gate kept")["meta"]
    assert meta["playbook"]["id"] == "unpaid_salary"
