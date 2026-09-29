"""S14: security + reliability.

Covers what's unit-testable from this sandbox (audit log wiring, the
request-body-size backstop, the chunked file-upload cap) - see
docs/PROGRESS.md's S14 entry for the parts that needed the live Supabase
project instead (the profiles.plan RLS escalation fix, verified live with
a role/JWT-claim simulation, not here) or a live Anthropic/frontend build
(not repeatable in pytest).
"""
import io

import pytest

from app import supa


class _FakeResponse:
    def __init__(self, json_data=None):
        self._json = json_data if json_data is not None else []

    def raise_for_status(self):
        pass

    def json(self):
        return self._json


class _FakeHttp:
    def __init__(self):
        self.calls = []

    def post(self, path, **kwargs):
        self.calls.append(("POST", path, kwargs.get("json")))
        return _FakeResponse()

    def delete(self, path, **kwargs):
        self.calls.append(("DELETE", path, kwargs.get("params")))
        return _FakeResponse()


def test_audit_log_fails_open_without_supabase_configured():
    assert supa.available() is False
    supa.audit_log("u1", "delete", "matter", "m1")  # must not raise


def test_matter_delete_writes_an_audit_log_entry(monkeypatch):
    fake = _FakeHttp()
    monkeypatch.setattr(supa, "available", lambda: True)
    monkeypatch.setattr(supa, "_http", lambda: fake)
    supa.matter_delete("user-a", "matter-1")
    kinds = [c[0] for c in fake.calls]
    assert kinds == ["DELETE", "POST"]
    _, path, body = fake.calls[1]
    assert path == "/rest/v1/audit_log"
    assert body == {"user_id": "user-a", "action": "delete", "target_type": "matter",
                    "target_id": "matter-1", "metadata": {}}


def test_draft_delete_writes_an_audit_log_entry(monkeypatch):
    fake = _FakeHttp()
    monkeypatch.setattr(supa, "available", lambda: True)
    monkeypatch.setattr(supa, "_http", lambda: fake)
    supa.draft_delete("user-a", "draft-1")
    kinds = [c[0] for c in fake.calls]
    assert kinds == ["DELETE", "POST"]
    assert fake.calls[1][1] == "/rest/v1/audit_log"


def test_audit_log_failure_does_not_raise(monkeypatch):
    class _RaisingHttp:
        def delete(self, *a, **kw):
            return _FakeResponse()

        def post(self, *a, **kw):
            raise RuntimeError("network down")

    monkeypatch.setattr(supa, "available", lambda: True)
    monkeypatch.setattr(supa, "_http", lambda: _RaisingHttp())
    supa.matter_delete("user-a", "matter-1")  # must not raise despite the audit write failing


# ---------------------------------------------------------- request size ---

@pytest.fixture()
def api_client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


def test_oversized_request_body_rejected(api_client):
    big = b"x" * (26 * 1024 * 1024)
    r = api_client.post("/api/chat", content=big, headers={"Content-Type": "application/json"})
    assert r.status_code == 413


def test_normal_sized_request_not_rejected_by_size_middleware(api_client):
    # Hits validation (empty message), not the size backstop - proves the
    # middleware doesn't false-positive on an ordinary request.
    r = api_client.post("/api/chat", json={"message": ""})
    assert r.status_code != 413


# --------------------------------------------------- matter file upload ----

def test_matter_file_upload_over_cap_is_rejected_without_buffering_whole_body(monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app

    monkeypatch.setattr(supa, "get_user", lambda token: {"id": "user-a"})
    monkeypatch.setattr(supa, "matter_get", lambda user_id, matter_id: {"id": matter_id, "user_id": user_id})

    def fail_if_called(*a, **kw):
        raise AssertionError("matter_file_create must not run for an over-cap upload")

    monkeypatch.setattr(supa, "matter_file_create", fail_if_called)

    oversized = io.BytesIO(b"x" * (21 * 1024 * 1024))
    with TestClient(app) as c:
        r = c.post(
            "/api/matters/m1/files", headers={"Authorization": "Bearer a"},
            files={"file": ("big.bin", oversized, "application/octet-stream")},
        )
    assert r.status_code == 413


def test_uploaded_filename_cannot_steer_the_storage_path(monkeypatch):
    fake = _FakeHttp()
    monkeypatch.setattr(supa, "available", lambda: True)
    monkeypatch.setattr(supa, "_http", lambda: fake)
    supa.matter_file_create("user-a", "matter-1", "../../user-b/matter-9/evil.pdf", b"%PDF", "application/pdf")
    upload_path = fake.calls[0][1]
    key = upload_path.split("/storage/v1/object/matter-files/", 1)[1]
    parts = key.split("/")
    assert parts[:2] == ["user-a", "matter-1"] and len(parts) == 3
    assert ".." not in key and "evil" not in key and parts[2].endswith(".pdf")
    row = fake.calls[1][2]
    assert row["filename"] == "evil.pdf" and row["storage_path"] == key


@pytest.mark.parametrize("name,expected", [
    ("a/b/c.docx", "c.docx"), ("..\\..\\x.pdf", "x.pdf"), (".hidden", "hidden"),
    ("सम्झौता पत्र.pdf", "सम्झौता पत्र.pdf"), ("a<script>.pdf", "a_script_.pdf"), ("", "file"),
])
def test_safe_filename(name, expected):
    assert supa.safe_filename(name) == expected


def test_answer_cache_strips_nul_characters_postgres_jsonb_rejects(monkeypatch):
    fake = _FakeHttp()
    monkeypatch.setattr(supa, "available", lambda: True)
    monkeypatch.setattr(supa, "_http", lambda: fake)
    supa.cache_put("k", "v", "ne", "q\x00", {"answer": "a\x00b", "sources": [{"text": "x\x00"}], "n": 1})
    body = fake.calls[0][2]
    assert body["question"] == "q" and body["answer"] == {"answer": "ab", "sources": [{"text": "x"}], "n": 1}
