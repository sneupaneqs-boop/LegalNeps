"""S10: LLM-assisted free-text fill for drafting templates, plus saving a
draft with version history. Two halves:

1. `app.drafting.ai_fill` unit tests, with `llm.complete` monkeypatched
   (no real LLM provider key exists in this build environment - same
   limitation noted throughout PROGRESS.md since S3).
2. `app.supa` draft_* unit tests. Supabase isn't configured in this
   environment either (`supa.available()` is False), so these exercise the
   documented "fails open to None/[] " behavior rather than a live
   round-trip - same honesty as S5's saved_research tests. The *schema*
   itself (drafts + draft_versions tables, RLS policies) was applied to and
   verified against the real LegalNeps Supabase project directly through
   the Supabase MCP tools this session, outside pytest's reach.

API-level tests hit the real corpus (requires_corpus) and monkeypatch
supa's user/quota/draft functions the same way tests/test_api.py's
saved_research tests do.
"""
import pytest

from app import llm, supa
from app.drafting import ai_fill
from app.retrieval import CORPUS_DIR

requires_corpus = pytest.mark.skipif(
    not (CORPUS_DIR / "manifest.json").exists(), reason="built corpus shards not present"
)


# ------------------------------------------------------------- ai_fill -----

def test_ai_fill_expands_hint_via_llm(monkeypatch):
    captured = {}

    def fake_complete(system, user, **kwargs):
        captured["system"] = system
        captured["user"] = user
        captured["kwargs"] = kwargs
        return "  विस्तारित पाठ यहाँ छ।  "

    monkeypatch.setattr(llm, "complete", fake_complete)
    text = ai_fill.fill("nda", "confidential_info_description", "ग्राहक सूची", "ne")
    assert text == "विस्तारित पाठ यहाँ छ।"
    assert captured["kwargs"]["fast"] is True  # tiered: cheap model, not the answer tier
    assert "ग्राहक सूची" in captured["user"]


def test_ai_fill_includes_other_answers_as_context(monkeypatch):
    captured = {}
    monkeypatch.setattr(llm, "complete", lambda system, user, **kw: captured.setdefault("user", user) or "ok")
    ai_fill.fill(
        "nda", "confidential_info_description", "मूल्य निर्धारण रणनीति", "ne",
        other_answers={"party_a_name": "अ कम्पनी", "duration_years": 5},
    )
    assert "अ कम्पनी" in captured["user"]


def test_ai_fill_unknown_template_raises():
    with pytest.raises(ai_fill.UnknownField):
        ai_fill.fill("not_a_template", "some_field", "hint", "ne")


def test_ai_fill_unknown_field_raises():
    with pytest.raises(ai_fill.UnknownField):
        ai_fill.fill("nda", "not_a_field", "hint", "ne")


def test_ai_fill_rejects_non_textarea_field():
    # party_a_name is a plain "text" field - AI fill is for free-text only
    with pytest.raises(ai_fill.UnknownField):
        ai_fill.fill("nda", "party_a_name", "hint", "ne")


def test_ai_fill_invalid_language_raises():
    with pytest.raises(ValueError):
        ai_fill.fill("nda", "confidential_info_description", "hint", "fr")


def test_ai_fill_propagates_llm_unavailable(monkeypatch):
    def raise_unavailable(*a, **kw):
        raise llm.LLMUnavailable("no provider configured")

    monkeypatch.setattr(llm, "complete", raise_unavailable)
    with pytest.raises(llm.LLMUnavailable):
        ai_fill.fill("nda", "confidential_info_description", "hint", "ne")


# ------------------------------------------------------- supa draft_* ------

def test_draft_functions_fail_open_without_supabase_configured():
    assert supa.available() is False  # no SUPABASE_URL in this build environment
    assert supa.draft_create("u1", "nda", "ne", {}) is None
    assert supa.draft_update("u1", "d1", "ne", {}) is None
    assert supa.draft_list("u1") == []
    assert supa.draft_get("u1", "d1") is None
    assert supa.draft_versions_list("u1", "d1") is None
    supa.draft_delete("u1", "d1")  # no-op, must not raise


# --------------------------------------------------------------- API ------

@requires_corpus
def test_ai_fill_endpoint_requires_auth_and_is_metered(monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app

    monkeypatch.setattr(supa, "get_user", lambda token: {"id": "user-1"} if token == "good" else None)
    monkeypatch.setattr(llm, "complete", lambda system, user, **kw: "विस्तारित पाठ")

    with TestClient(app) as c:
        assert c.post(
            "/api/drafting/templates/nda/ai-fill",
            json={"field_id": "confidential_info_description", "hint": "ग्राहक सूची", "language": "ne"},
        ).status_code == 401

        calls = {"n": 0}

        def fake_quota(user_id, daily_limit=None):
            calls["n"] += 1
            return (calls["n"] <= 1), calls["n"]

        monkeypatch.setattr(supa, "check_and_increment_quota", fake_quota)

        r = c.post(
            "/api/drafting/templates/nda/ai-fill",
            json={"field_id": "confidential_info_description", "hint": "ग्राहक सूची", "language": "ne"},
            headers={"Authorization": "Bearer good"},
        )
        assert r.status_code == 200
        assert r.json()["text"] == "विस्तारित पाठ"

        # second call: fake_quota now denies -> 429, proving AI fill is metered
        r = c.post(
            "/api/drafting/templates/nda/ai-fill",
            json={"field_id": "confidential_info_description", "hint": "अर्को", "language": "ne"},
            headers={"Authorization": "Bearer good"},
        )
        assert r.status_code == 429


@requires_corpus
def test_ai_fill_endpoint_bad_field(monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app

    monkeypatch.setattr(supa, "get_user", lambda token: {"id": "user-1"} if token == "good" else None)
    monkeypatch.setattr(supa, "check_and_increment_quota", lambda user_id, daily_limit=None: (True, 1))

    with TestClient(app) as c:
        r = c.post(
            "/api/drafting/templates/nda/ai-fill",
            json={"field_id": "not_a_field", "hint": "x", "language": "ne"},
            headers={"Authorization": "Bearer good"},
        )
        assert r.status_code == 400


@requires_corpus
def test_drafts_crud_and_version_history_api(monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app

    monkeypatch.setattr(supa, "get_user", lambda token: {"id": "user-1"} if token == "good" else None)

    drafts: dict[str, dict] = {}
    versions: dict[str, list[dict]] = {}

    def fake_create(user_id, template_id, language, answers, title=None):
        row = {
            "id": "draft-1", "template_id": template_id, "title": title, "language": language,
            "answers": answers, "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z",
        }
        drafts[row["id"]] = row
        versions[row["id"]] = [{"id": "v1", "version_number": 1, "language": language, "answers": answers,
                                 "created_at": "2026-01-01T00:00:00Z"}]
        return row

    def fake_update(user_id, draft_id, language, answers, title=None):
        if draft_id not in drafts:
            return None
        row = dict(drafts[draft_id], language=language, answers=answers, updated_at="2026-01-02T00:00:00Z")
        if title is not None:
            row["title"] = title
        drafts[draft_id] = row
        next_n = len(versions[draft_id]) + 1
        versions[draft_id].append({"id": f"v{next_n}", "version_number": next_n, "language": language,
                                    "answers": answers, "created_at": "2026-01-02T00:00:00Z"})
        return row

    monkeypatch.setattr(supa, "draft_create", fake_create)
    monkeypatch.setattr(supa, "draft_update", fake_update)
    monkeypatch.setattr(supa, "draft_list", lambda user_id: list(drafts.values()))
    monkeypatch.setattr(supa, "draft_get", lambda user_id, draft_id: drafts.get(draft_id))
    monkeypatch.setattr(supa, "draft_delete", lambda user_id, draft_id: drafts.pop(draft_id, None))
    monkeypatch.setattr(supa, "draft_versions_list", lambda user_id, draft_id: list(reversed(versions.get(draft_id, []))))

    headers = {"Authorization": "Bearer good"}
    with TestClient(app) as c:
        assert c.get("/api/drafting/drafts").status_code == 401

        body = {"template_id": "nda", "language": "ne", "answers": {"party_a_name": "अ"}, "title": "मेरो NDA"}
        r = c.post("/api/drafting/drafts", json=body, headers=headers)
        assert r.status_code == 201
        draft_id = r.json()["id"]

        assert c.post("/api/drafting/drafts",
                       json={"template_id": "does-not-exist", "language": "ne", "answers": {}},
                       headers=headers).status_code == 404

        r = c.get("/api/drafting/drafts", headers=headers)
        assert r.status_code == 200 and len(r.json()) == 1

        r = c.get(f"/api/drafting/drafts/{draft_id}", headers=headers)
        assert r.status_code == 200 and r.json()["answers"]["party_a_name"] == "अ"

        r = c.put(f"/api/drafting/drafts/{draft_id}",
                   json={"template_id": "nda", "language": "ne", "answers": {"party_a_name": "अ", "party_b_name": "ब"}},
                   headers=headers)
        assert r.status_code == 200
        assert r.json()["answers"]["party_b_name"] == "ब"

        r = c.get(f"/api/drafting/drafts/{draft_id}/versions", headers=headers)
        assert r.status_code == 200
        version_numbers = [v["version_number"] for v in r.json()]
        assert version_numbers == [2, 1]  # newest first

        assert c.delete(f"/api/drafting/drafts/{draft_id}", headers=headers).status_code == 204
        assert c.get("/api/drafting/drafts", headers=headers).json() == []
