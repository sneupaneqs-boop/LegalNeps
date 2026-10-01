"""V2.7: verified keyword -> SECTION routes (section_routes.py, data/section_routes.yaml) and the lexicon rows added with them.
Every case below is one of the 14 governing-section misses of the V3.3 live review (set B, 2026-10-01); the questions and gold
sections live in eval/questions_sections_b.jsonl (TUNING data - burned, never a held-out set)."""
import os
import sys

import pytest

from app import generation, section_routes, translit
from app.retrieval import CORPUS_DIR, doc_slug, get_index

EVAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval")
sys.path.insert(0, EVAL)
import run_eval  # noqa: E402

requires_corpus = pytest.mark.skipif(not (CORPUS_DIR / "manifest.json").exists(), reason="corpus shards not present")
RAW = {"queries_ne": [], "queries_en": [], "laws": [], "wants_precedent": True}
B = {q["id"]: q for q in run_eval.load(run_eval.set_path("sections_b"))}


@requires_corpus
def test_every_route_provision_resolves_and_is_in_force():
    idx = get_index()
    assert len(section_routes.load_routes()) >= 14
    for r in section_routes.load_routes():
        assert r.provisions, r.id
        for ref in list(r.provisions) + list(r.suppress):
            e = idx.section(doc_slug(ref["law_title_ne"]), str(ref["section"]))
            if ref in r.suppress and e is None:  # a suppressed section may be a chunk label; the base number must exist
                continue
            assert e is not None, (r.id, ref)
            assert e.get("status") in ("in_force", None), (r.id, ref, e.get("status"))


@requires_corpus
def test_sections_b_gold_sections_are_in_the_corpus():
    from casecheck import DocResolver, verify_case
    idx = get_index()
    res = DocResolver(idx)
    for q in B.values():
        assert verify_case(q, idx, res) == [], q["id"]


@requires_corpus
@pytest.mark.parametrize("qid", sorted(B))
def test_governing_section_is_in_the_top_8_for_each_set_b_miss(qid):
    q = B[qid]
    pb = generation._match_playbook(q["q"], dict(RAW))
    res = generation.search(q["q"], dict(RAW), top_k=8, precedent_k=3, playbook=pb)
    laws = [r for r in res if r.get("category") == "law"]
    rank = run_eval._first_section_hit(laws, q["sections"])
    assert rank is not None and rank <= 8, (qid, [r.get("source_ne") for r in laws])


@requires_corpus
def test_routes_lead_the_list_and_are_marked_routed_and_pinned():
    q = B["b11"]["q"]  # overtime rate -> Labour Act s.31 is first (the plan pins ss.28-31 in order)
    res = generation.search(q, dict(RAW), top_k=8, playbook=generation._match_playbook(q, dict(RAW)))
    assert res[0]["section"] == "31" and res[0]["routed"] and res[0]["pinned"]
    assert sum(1 for r in res if r["section"] == "31" and "श्रम" in r["doc_title_ne"]) == 1  # promoted, not repeated


@requires_corpus
def test_edited_photo_route_suppresses_criminal_code_s298():
    q = B["b15"]["q"]
    res = generation.search(q, dict(RAW), top_k=8, playbook=generation._match_playbook(q, dict(RAW)))
    assert not any(str(r.get("section") or "").split(" ")[0] == "298" and "अपराध संहिता" in (r.get("doc_title_ne") or "") for r in res)
    assert [r["section"] for r in res if "गोपनीयता" in (r.get("doc_title_ne") or "")][:2] == ["16", "29"]


@requires_corpus
def test_two_issue_question_gets_both_routes():
    # b03: unpaid wages AND "the company will not let me leave": Labour Act ss.35, 148 (wages) and s.141 (resignation)
    q = B["b03"]["q"]
    got = {r.id for r in section_routes.matching_routes(q)}
    assert got == {"unpaid_wages", "resignation_not_allowed"}
    res = generation.search(q, dict(RAW), top_k=8, playbook=generation._match_playbook(q, dict(RAW)))
    secs = {r["section"] for r in res if r.get("doc_title_ne") == "श्रम ऐन, २०७४"}
    assert {"35", "141", "148"} <= secs


@pytest.mark.parametrize("text,route", [
    ("मेरो नाममा रहेको जग्गा दाजुले नक्कली सहीछाप गरेर बेचिदियो", "forged_document"),
    ("Someone forged my signature on a sale deed", "forged_document"),
    ("jali sahi garera lalpurja bechyo", "forged_document"),
    ("facebook ma mero photo edit garera failaidiyo", "edited_photo_privacy"),
    ("Someone is blackmailing me with my private photos", "blackmail_extortion"),
    ("probation period ma nikalyo", "probation_termination"),
    ("Can I sell my ancestral property without my brothers' consent?", "ancestral_property_sale"),
])
def test_route_keywords_match_english_roman_and_devanagari(text, route):
    assert route in {r.id for r in section_routes.matching_routes(text)}


@pytest.mark.parametrize("text", [
    "How do I register a company in Nepal?",
    "My landlord refuses to return the deposit",
    "The product was fake, I bought it from a shop",          # no 'online' / order word: no counterfeit-goods route
    "fake id banayera badnam gariraheko chha",                 # fake ACCOUNT, not a fake product
    "I signed the contract but the other side has not paid",   # a signature without a forgery word
    "chori ko muddha ma jamanat paincha?",                     # theft but neither punishment nor limitation asked
])
def test_routes_do_not_fire_on_nearby_but_different_questions(text):
    assert section_routes.matching_routes(text) == []


def test_latin_alternatives_are_spelling_tolerant_but_short_words_are_exact():
    assert {r.id for r in section_routes.matching_routes("nakali sahi garera jagga bechyo")} == {"forged_document"}
    assert section_routes.matching_routes("vat registration") and not section_routes.matching_routes("what is vatsal")


@requires_corpus
def test_new_lexicon_rows_name_the_governing_law():
    assert "वैयक्तिक गोपनीयता सम्बन्धी ऐन, २०७५" in translit.laws("my private photo was leaked")
    assert "श्रम ऐन, २०७४" in translit.laws_ne("तीन महिनादेखि तलब आएको छैन")
    assert "मुलुकी अपराध संहिता, २०७४" in translit.laws_ne("दाजुले नक्कली सहीछाप गरेर जग्गा बेचिदियो")
    assert "मुलुकी देवानी संहिता, २०७४" in translit.laws("Can I cancel a signed rental agreement?")
