import pytest
from fastapi.testclient import TestClient

from app import generation, retrieval
from fixtures import ENTRIES


@pytest.fixture()
def client(monkeypatch, tmp_path):
    retrieval.CACHE_DIR = tmp_path
    idx = retrieval.Index([dict(e) for e in ENTRIES], "api-test")
    monkeypatch.setattr(retrieval, "_index", idx)
    monkeypatch.setattr(generation, "get_index", lambda: idx)
    from app.main import app
    with TestClient(app) as c:
        yield c


def test_chat_without_llm_returns_extractive_answer_with_numbered_official_sources(client):
    r = client.post("/api/chat", json={"message": "बाल विवाह गरेमा के सजाय हुन्छ?", "language": "auto"})
    assert r.status_code == 200
    body = r.json()
    assert body["language"] == "ne"
    assert body["llm_used"] is False
    assert body["sources"][0]["n"] == 1
    assert body["sources"][0]["citation"] == "मुलुकी अपराध संहिता, २०७४, दफा 173"
    assert body["sources"][0]["url"].startswith("https://")
    assert "[1]" in body["answer"]


def test_english_ui_gets_english_citations(client):
    r = client.post("/api/chat", json={"message": "citizenship by descent", "language": "en"})
    body = r.json()
    assert body["language"] == "en"
    assert body["sources"][0]["citation"] == "Constitution of Nepal, Article 11"


def test_search_endpoint_and_category_filter(client):
    r = client.get("/api/search", params={"q": "सम्बन्ध विच्छेद अंश", "category": "precedent"})
    assert r.status_code == 200
    assert [s["id"] for s in r.json()["results"]] == ["nkp-1"]


def test_search_doc_type_and_status_filters(client):
    r = client.get("/api/search", params={"q": "कैद", "category": "law", "doc_type": "act"})
    assert r.status_code == 200
    assert r.json()["results"]
    assert all(s["doc_type"] == "act" for s in r.json()["results"])
    # a draft bill only shows up when explicitly asked for by status
    r = client.get("/api/search", params={"q": "बाल विवाह", "status": "bill"})
    assert any(s["id"] == "law-bill-1" for s in r.json()["results"])


def test_validation(client):
    assert client.post("/api/chat", json={"message": ""}).status_code == 422
    assert client.post("/api/chat", json={"message": "x", "language": "fr"}).status_code == 422
    assert client.get("/api/search", params={"q": "x", "k": 500}).status_code == 422
    assert client.get("/api/search", params={"q": "x", "status": "repealed"}).status_code == 422


def test_law_browser_doc_and_section_endpoints(client):
    from app.retrieval import doc_slug

    slug = doc_slug("मुलुकी देवानी संहिता, २०७४")
    r = client.get(f"/api/law/{slug}")
    assert r.status_code == 200
    body = r.json()
    assert body["doc_title_ne"] == "मुलुकी देवानी संहिता, २०७४"
    assert [s["section"] for s in body["sections"]] == ["99", "400"]

    r = client.get(f"/api/law/{slug}/99")
    assert r.status_code == 200
    section = r.json()
    assert section["id"] == "law-civ-99"
    assert section["next"]["section"] == "400"
    assert section["prev"] is None

    assert client.get("/api/law/no-such-slug").status_code == 404
    assert client.get(f"/api/law/{slug}/no-such-section").status_code == 404


def test_stats(client):
    s = client.get("/api/stats").json()
    assert s["entries"] == len(ENTRIES) and s["by_type"]["precedent"] == 1
    assert s["corpus_version"] == "api-test"
    assert s["by_status"]["bill"] == 2


def test_text_citations_are_mapped_to_numbered_sources():
    from app.generation import normalize_citations
    sources = [dict(ENTRIES[1]), dict(ENTRIES[0])]
    out = normalize_citations("Give notice [Muluki Civil Code 2074, Section 400]. Divorce [Muluki Civil Code, Section 99].", sources)
    assert "[1]" in out and "[2]" in out
    assert normalize_citations("see [3]", sources) == "see [3]"
    assert normalize_citations("[Some Act, Section 7]", sources) == "[Some Act, Section 7]"


def test_streaming_endpoint_sends_sources_then_done(client):
    import json
    r = client.post("/api/chat/stream", json={"message": "बाल विवाह सजाय", "language": "ne"})
    assert r.status_code == 200
    events = [json.loads(l) for l in r.text.splitlines() if l.strip()]
    assert events[0]["type"] == "meta" and events[0]["sources"][0]["n"] == 1
    assert events[-1]["type"] == "done" and events[-1]["llm_used"] is False
    assert "[1]" in events[-1]["answer"]


def test_focus_keeps_heading_and_the_matching_clause():
    from app.generation import focus
    from app.text_norm import tokenize
    filler = " ".join(f"({i}) यो असम्बन्धित व्यवस्था हो।" for i in range(1, 40))
    text = "१७३. बाल विवाह गर्न नहुने : " + filler + " (४०) बाल विवाह गर्नेलाई तीन वर्षसम्म कैद हुनेछ। " + filler
    out = focus(text, set(tokenize("बाल विवाह कैद सजाय")), limit=300)
    assert len(out) <= 330
    assert out.startswith("१७३. बाल विवाह गर्न नहुने")
    assert "तीन वर्षसम्म कैद" in out
    assert focus("छोटो पाठ", set(), 300) == "छोटो पाठ"


def test_greetings_and_thanks_get_a_reply_not_law_passages(client):
    for msg, lang, needle in [("hi", "en", "Kanooni Sathi"), ("नमस्ते", "auto", "कानूनी साथी"), ("thank you", "en", "welcome")]:
        body = client.post("/api/chat", json={"message": msg, "language": lang}).json()
        assert body["sources"] == []
        assert needle in body["answer"]


def test_history_is_accepted_and_validated(client):
    hist = [{"role": "user", "text": "बाल विवाह"}, {"role": "bot", "text": "..."}]
    r = client.post("/api/chat", json={"message": "सजाय कति हो?", "history": hist})
    assert r.status_code == 200
    assert client.post("/api/chat", json={"message": "x", "history": [{"role": "system", "text": "y"}]}).status_code == 422
