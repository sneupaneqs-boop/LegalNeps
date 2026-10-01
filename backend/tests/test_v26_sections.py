"""V2.6: section-level retrieval - Devanagari concept lexicon, specialist-regime prior, heading boost, sections12 set."""
import os
import sys

import pytest

from app import generation, retrieval, translit
from app.retrieval import CORPUS_DIR, get_index
from app.text_norm import tokenize

EVAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval")
sys.path.insert(0, EVAL)
import run_eval  # noqa: E402

requires_corpus = pytest.mark.skipif(not (CORPUS_DIR / "manifest.json").exists(), reason="corpus shards not present")
RAW = {"queries_ne": [], "queries_en": [], "laws": [], "wants_precedent": True}


@requires_corpus
def test_ne_lexicon_targets_are_index_words_and_laws_are_titles():
    idx = get_index()
    df = idx.W.tocsc()
    titles = set(idx.doc_title)
    assert len(translit.NE_ENTRIES) >= 15
    for e in translit.NE_ENTRIES:
        for law in e.laws:
            assert law in titles, law
        for term in e.terms:
            toks = tokenize(term)
            assert toks, term
            for t in toks:
                col = idx.vocab.get(t)
                assert col is not None and df.indptr[col + 1] - df.indptr[col] >= 2, (term, t)


@pytest.mark.parametrize("text,term", [
    ("घरबेटीले भाडा नतिरेको भन्दै एक्कासी कोठा खाली गर्न लगायो", "बहालमा लिने व्यक्तिलाई हटाउन सक्ने"),
    ("तलबबाट कर कटौती कति प्रतिशत हुन्छ", "रोजगारदाताबाट कर कट्टी"),
    ("मोटरसाइकलले हिर्काएर भाग्यो, बुबा घाइते हुनुभयो", "सवारी दुर्घटना"),
    ("किनेको मोबाइल एक महिनामै बिग्रियो, पसलेले फिर्ता लिँदैन", "वस्तु फिर्ता"),
    ("कम्पनीले कारण नदेखाई जागिरबाट निकाल्यो", "उपदान"),
])
def test_devanagari_everyday_wording_maps_to_statute_terms(text, term):
    assert term in translit.expand_ne(text)


def test_ne_lexicon_ignores_latin_and_unrelated_text():
    assert translit.match_ne("What is the official language of Nepal?") == []
    assert translit.match_ne("मेरो नाम राम हो") == []
    assert translit.match("घरबेटीले धरौटी फिर्ता दिएन") == []  # the Latin lexicon stays untouched


def test_regime_cues_and_inactive_set():
    names = [r[0] for r in retrieval.REGIMES]
    off = retrieval._inactive_regimes("तलबबाट कर कटौती")
    assert names.index("military") + 1 in off and names.index("postal") + 1 in off
    on = retrieval._inactive_regimes("सैनिकको तलब")
    assert names.index("military") + 1 not in on


@requires_corpus
def test_every_regime_matches_corpus_titles():
    """The regimes are derived from the corpus's own titles: each must actually occur in it."""
    idx = get_index()
    assert idx.aux is not None
    counts = {k: 0 for k in range(1, len(retrieval.REGIMES) + 1)}
    for r in idx.aux["regime"]:
        if r:
            counts[int(r)] += 1
    assert all(c > 0 for c in counts.values()), counts
    # the civil code's hire-purchase chapter is found by its opening words, the rest of the Code is general law
    sec = idx.section(retrieval.doc_slug("मुलुकी देवानी संहिता, २०७४"), "633")
    row = idx.ids.index(sec["id"])
    assert idx.aux["regime"][row] == [r[0] for r in retrieval.REGIMES].index("hire_purchase") + 1
    row401 = idx.ids.index(idx.section(retrieval.doc_slug("मुलुकी देवानी संहिता, २०७४"), "401")["id"])
    assert idx.aux["regime"][row401] == 0


@requires_corpus
def test_regime_demotion_and_heading_boost_can_be_switched_off(monkeypatch):
    idx = get_index()
    q = ["तलबबाट कर कटौती कति प्रतिशत हुन्छ"]
    on = [r["id"] for r in idx.search(q, top_k=8, category="law")]
    monkeypatch.setitem(retrieval.SEARCH, "regime_demote", 1.0)
    monkeypatch.setitem(retrieval.SEARCH, "heading_boost", 0)
    off = [r["id"] for r in idx.search(q, top_k=8, category="law")]
    assert on and off


@requires_corpus
def test_sections12_is_marked_tuning_data_and_verified():
    path = run_eval.set_path("sections12")
    head = "\n".join(l for l in open(path, encoding="utf-8") if l.startswith("#"))
    assert "TUNING DATA" in head
    rows = run_eval.load(path)
    assert len(rows) == 12
    from casecheck import DocResolver, verify_case
    idx = get_index()
    resolver = DocResolver(idx)
    for r in rows:
        assert not verify_case(r, idx, resolver), r["id"]


def test_any_subsection_matches_a_chunk_of_the_section():
    sections = [{"doc": "मुलुकी अपराध संहिता", "section": "219 (2)", "any_subsection": True}]
    res = [{"doc_title_ne": "मुलुकी अपराध संहिता, २०७४", "section": "7"},
           {"doc_title_ne": "मुलुकी अपराध संहिता, २०७४", "section": "219 (3)"}]
    assert run_eval._first_section_hit(res, sections) == 2
    assert run_eval._first_section_hit(res, [{**sections[0], "any_subsection": False}]) is None


@requires_corpus
def test_sections12_section_hit_at_8():
    """The governing section of at least 10 of the 12 missed questions is in the top 8 on the raw production path."""
    rows = run_eval.load(run_eval.set_path("sections12"))
    hits = 0
    for q in rows:
        res = generation.search(q["q"], RAW, top_k=8, precedent_k=0, playbook=generation._match_playbook(q["q"], RAW))
        hits += bool(run_eval._first_section_hit([r for r in res if r.get("category") == "law"], q["sections"]))
    assert hits >= 10, hits
