import pytest

from app import retrieval
from fixtures import ENTRIES


@pytest.fixture(scope="module")
def idx(tmp_path_factory):
    retrieval.CACHE_DIR = tmp_path_factory.mktemp("cache")
    return retrieval.Index([dict(e) for e in ENTRIES], "test-digest")


def test_nepali_query_finds_the_right_section(idx):
    hits = idx.search(["घरबहाल धरौटी फिर्ता"], top_k=3)
    assert hits[0]["id"] == "law-civ-400"


def test_inflected_query_still_matches(idx):
    hits = idx.search(["बाल विवाहको सजायलाई"], top_k=2)
    assert hits[0]["id"] == "law-crim-173"


def test_duplicate_text_from_other_document_is_collapsed(idx):
    ids = [h["id"] for h in idx.search(["बाल विवाह कैद"], top_k=5)]
    assert "law-crim-173" in ids and "law-crim-173-dup" not in ids


def test_category_filter_and_fusion_across_queries(idx):
    prec = idx.search(["सम्बन्ध विच्छेद अंश"], top_k=3, category="precedent")
    assert [h["id"] for h in prec] == ["nkp-1"]
    laws = idx.search(["divorce", "सम्बन्ध विच्छेद अंश"], top_k=3, category="law")
    assert laws[0]["id"] == "law-civ-99"


def test_english_text_is_searchable_when_present(idx):
    assert idx.search(["citizenship by descent"], top_k=1)[0]["id"] == "law-const-11"


def test_title_boost_prefers_named_statute(idx):
    hits = idx.search(["कैद"], top_k=3, boost_titles=["मुलुकी अपराध संहिता, २०७४"])
    assert hits[0]["doc_title_ne"] == "मुलुकी अपराध संहिता, २०७४"


def test_unknown_terms_return_nothing(idx):
    assert idx.search(["zzzqqq"], top_k=3) == []


def test_cache_roundtrip(idx):
    again = retrieval.Index([dict(e) for e in ENTRIES], "test-digest")
    assert again.W.shape == idx.W.shape and again.vocab == idx.vocab


def test_draft_bills_are_excluded_from_default_search(idx):
    ids = [h["id"] for h in idx.search(["बाल विवाह कैद सजाय"], top_k=10)]
    assert "law-bill-1" not in ids
    ids = [h["id"] for h in idx.search(["बाल विवाह कैद सजाय"], top_k=10, include_bills=True)]
    assert "law-bill-1" in ids
