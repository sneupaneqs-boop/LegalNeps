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


def test_validation(client):
    assert client.post("/api/chat", json={"message": ""}).status_code == 422
    assert client.post("/api/chat", json={"message": "x", "language": "fr"}).status_code == 422
    assert client.get("/api/search", params={"q": "x", "k": 500}).status_code == 422


def test_stats(client):
    s = client.get("/api/stats").json()
    assert s["entries"] == len(ENTRIES) and s["by_type"]["precedent"] == 1
