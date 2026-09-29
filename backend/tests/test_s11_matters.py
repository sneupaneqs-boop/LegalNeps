"""S11: Matter workspace lite - matters, notes, tasks, files.

Supabase isn't configured in this build environment (`supa.available()` is
False, same as every prior session's tests), so these exercise the API
layer against a monkeypatched `supa` store - same pattern
tests/test_api.py and tests/test_s10_ai_and_save.py already use.

The "Done when" bar (CRUD + RLS tests: user B can't see user A's matter) is
proven two ways: here, at the API layer, every note/task/file route 404s
when the matter isn't the caller's (app-layer ownership check, needed
because the backend talks to Supabase with the service-role key, which
bypasses RLS); and separately, live against the real Supabase project with
two real auth users and their own JWTs, exercised outside pytest's reach -
see docs/PROGRESS.md's S11 entry for that result.
"""
import io

import pytest

from app import supa
from app.retrieval import CORPUS_DIR

requires_corpus = pytest.mark.skipif(
    not (CORPUS_DIR / "manifest.json").exists(), reason="built corpus shards not present"
)


def test_matter_functions_fail_open_without_supabase_configured():
    assert supa.available() is False
    assert supa.matter_create("u1", "client") is None
    assert supa.matter_list("u1") == []
    assert supa.matter_get("u1", "m1") is None
    assert supa.matter_update("u1", "m1", client_name="x") is None
    supa.matter_delete("u1", "m1")  # no-op, must not raise
    assert supa.matter_note_create("u1", "m1", "note") is None
    assert supa.matter_note_list("u1", "m1") == []
    assert supa.matter_task_create("u1", "m1", "task") is None
    assert supa.matter_task_list("u1", "m1") == []
    assert supa.matter_task_update("u1", "m1", "t1", done=True) is None
    assert supa.matter_file_create("u1", "m1", "a.txt", b"x", "text/plain") is None
    assert supa.matter_file_list("u1", "m1") == []
    assert supa.matter_file_signed_url("u1", "m1", "f1") is None


class FakeMattersStore:
    """In-memory stand-in for supa.py's matters/notes/tasks/files functions,
    keyed by (user_id, id) like real RLS-scoped rows would be - a lookup
    with the wrong user_id simply finds nothing, the same shape as a real
    postgrest query filtered by user_id."""

    def __init__(self):
        self.matters: dict[str, dict] = {}
        self.notes: dict[str, dict] = {}
        self.tasks: dict[str, dict] = {}
        self.files: dict[str, dict] = {}
        self._n = 0

    def _id(self, prefix: str) -> str:
        self._n += 1
        return f"{prefix}{self._n}"

    def matter_create(self, user_id, client_name, facts=None):
        row = {"id": self._id("m"), "user_id": user_id, "client_name": client_name, "facts": facts,
               "status": "open", "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z"}
        self.matters[row["id"]] = row
        return dict(row)

    def matter_list(self, user_id):
        return [dict(m) for m in self.matters.values() if m["user_id"] == user_id]

    def matter_get(self, user_id, matter_id):
        m = self.matters.get(matter_id)
        return dict(m) if m and m["user_id"] == user_id else None

    def matter_update(self, user_id, matter_id, client_name=None, facts=None, status=None):
        m = self.matter_get(user_id, matter_id)
        if m is None:
            return None
        if client_name is not None:
            m["client_name"] = client_name
        if facts is not None:
            m["facts"] = facts
        if status is not None:
            m["status"] = status
        self.matters[matter_id] = m
        return dict(m)

    def matter_delete(self, user_id, matter_id):
        m = self.matter_get(user_id, matter_id)
        if m:
            del self.matters[matter_id]

    def matter_note_create(self, user_id, matter_id, body):
        row = {"id": self._id("n"), "user_id": user_id, "matter_id": matter_id, "body": body,
               "created_at": "2026-01-01T00:00:00Z"}
        self.notes[row["id"]] = row
        return dict(row)

    def matter_note_list(self, user_id, matter_id):
        return [dict(n) for n in self.notes.values() if n["user_id"] == user_id and n["matter_id"] == matter_id]

    def matter_note_delete(self, user_id, matter_id, note_id):
        n = self.notes.get(note_id)
        if n and n["user_id"] == user_id and n["matter_id"] == matter_id:
            del self.notes[note_id]

    def matter_task_create(self, user_id, matter_id, title, due_date=None):
        row = {"id": self._id("t"), "user_id": user_id, "matter_id": matter_id, "title": title, "done": False,
               "due_date": due_date, "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z"}
        self.tasks[row["id"]] = row
        return dict(row)

    def matter_task_list(self, user_id, matter_id):
        return [dict(t) for t in self.tasks.values() if t["user_id"] == user_id and t["matter_id"] == matter_id]

    def matter_task_update(self, user_id, matter_id, task_id, title=None, done=None, due_date=None):
        t = self.tasks.get(task_id)
        if not (t and t["user_id"] == user_id and t["matter_id"] == matter_id):
            return None
        if title is not None:
            t["title"] = title
        if done is not None:
            t["done"] = done
        if due_date is not None:
            t["due_date"] = due_date
        return dict(t)

    def matter_task_delete(self, user_id, matter_id, task_id):
        t = self.tasks.get(task_id)
        if t and t["user_id"] == user_id and t["matter_id"] == matter_id:
            del self.tasks[task_id]

    def matter_file_create(self, user_id, matter_id, filename, content, content_type):
        row = {"id": self._id("f"), "user_id": user_id, "matter_id": matter_id, "filename": filename,
               "content_type": content_type, "size_bytes": len(content), "created_at": "2026-01-01T00:00:00Z"}
        self.files[row["id"]] = row
        return dict(row)

    def matter_file_list(self, user_id, matter_id):
        return [dict(f) for f in self.files.values() if f["user_id"] == user_id and f["matter_id"] == matter_id]

    def matter_file_signed_url(self, user_id, matter_id, file_id):
        f = self.files.get(file_id)
        if not (f and f["user_id"] == user_id and f["matter_id"] == matter_id):
            return None
        return f"https://example.supabase.co/storage/v1/object/sign/matter-files/{user_id}/{matter_id}/{f['filename']}"

    def matter_file_delete(self, user_id, matter_id, file_id):
        f = self.files.get(file_id)
        if f and f["user_id"] == user_id and f["matter_id"] == matter_id:
            del self.files[file_id]


@pytest.fixture()
def matters_client(monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app

    monkeypatch.setattr(supa, "get_user", lambda token: {"id": "user-a"} if token == "a" else
                        ({"id": "user-b"} if token == "b" else None))
    store = FakeMattersStore()
    for fn in ["matter_create", "matter_list", "matter_get", "matter_update", "matter_delete",
               "matter_note_create", "matter_note_list", "matter_note_delete",
               "matter_task_create", "matter_task_list", "matter_task_update", "matter_task_delete",
               "matter_file_create", "matter_file_list", "matter_file_signed_url", "matter_file_delete"]:
        monkeypatch.setattr(supa, fn, getattr(store, fn))
    with TestClient(app) as c:
        yield c, store


def test_matters_require_auth(matters_client):
    c, _ = matters_client
    assert c.get("/api/matters").status_code == 401
    assert c.post("/api/matters", json={"client_name": "x"}).status_code == 401


def test_matter_crud_roundtrip(matters_client):
    c, _ = matters_client
    headers = {"Authorization": "Bearer a"}

    r = c.post("/api/matters", json={"client_name": "Ram Shrestha", "facts": "wage dispute"}, headers=headers)
    assert r.status_code == 201
    matter_id = r.json()["id"]
    assert r.json()["status"] == "open"

    r = c.get("/api/matters", headers=headers)
    assert r.status_code == 200 and len(r.json()) == 1

    r = c.get(f"/api/matters/{matter_id}", headers=headers)
    assert r.status_code == 200 and r.json()["client_name"] == "Ram Shrestha"

    r = c.put(f"/api/matters/{matter_id}", json={"status": "closed"}, headers=headers)
    assert r.status_code == 200 and r.json()["status"] == "closed"

    assert c.delete(f"/api/matters/{matter_id}", headers=headers).status_code == 204
    assert c.get("/api/matters", headers=headers).json() == []


def test_matter_notes_and_tasks_crud(matters_client):
    c, _ = matters_client
    headers = {"Authorization": "Bearer a"}
    matter_id = c.post("/api/matters", json={"client_name": "x"}, headers=headers).json()["id"]

    r = c.post(f"/api/matters/{matter_id}/notes", json={"body": "client called"}, headers=headers)
    assert r.status_code == 201
    note_id = r.json()["id"]
    assert c.get(f"/api/matters/{matter_id}/notes", headers=headers).json()[0]["body"] == "client called"
    assert c.delete(f"/api/matters/{matter_id}/notes/{note_id}", headers=headers).status_code == 204

    r = c.post(f"/api/matters/{matter_id}/tasks", json={"title": "file complaint"}, headers=headers)
    assert r.status_code == 201
    task_id = r.json()["id"]
    assert r.json()["done"] is False

    r = c.put(f"/api/matters/{matter_id}/tasks/{task_id}", json={"done": True}, headers=headers)
    assert r.status_code == 200 and r.json()["done"] is True

    assert c.delete(f"/api/matters/{matter_id}/tasks/{task_id}", headers=headers).status_code == 204


def test_matter_file_upload_list_download_delete(matters_client):
    c, _ = matters_client
    headers = {"Authorization": "Bearer a"}
    matter_id = c.post("/api/matters", json={"client_name": "x"}, headers=headers).json()["id"]

    r = c.post(
        f"/api/matters/{matter_id}/files", headers=headers,
        files={"file": ("evidence.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")},
    )
    assert r.status_code == 201
    file_id = r.json()["id"]
    assert r.json()["filename"] == "evidence.pdf"

    assert len(c.get(f"/api/matters/{matter_id}/files", headers=headers).json()) == 1

    r = c.get(f"/api/matters/{matter_id}/files/{file_id}/download", headers=headers)
    assert r.status_code == 200 and r.json()["url"].startswith("https://")

    assert c.delete(f"/api/matters/{matter_id}/files/{file_id}", headers=headers).status_code == 204
    assert c.get(f"/api/matters/{matter_id}/files", headers=headers).json() == []


def test_user_b_cannot_see_user_a_matter_or_its_subresources(matters_client):
    """The API-layer proof: every sub-resource route 404s for a matter that
    isn't the caller's, exactly like a nonexistent matter would - a
    stranger's matter ID and a made-up one are indistinguishable."""
    c, _ = matters_client
    a = {"Authorization": "Bearer a"}
    b = {"Authorization": "Bearer b"}

    matter_id = c.post("/api/matters", json={"client_name": "A's client", "facts": "secret"}, headers=a).json()["id"]

    assert c.get(f"/api/matters/{matter_id}", headers=b).status_code == 404
    assert c.put(f"/api/matters/{matter_id}", json={"status": "closed"}, headers=b).status_code == 404
    assert matter_id not in [m["id"] for m in c.get("/api/matters", headers=b).json()]

    assert c.post(f"/api/matters/{matter_id}/notes", json={"body": "snooping"}, headers=b).status_code == 404
    assert c.get(f"/api/matters/{matter_id}/notes", headers=b).status_code == 404
    assert c.post(f"/api/matters/{matter_id}/tasks", json={"title": "snooping"}, headers=b).status_code == 404
    assert c.get(f"/api/matters/{matter_id}/tasks", headers=b).status_code == 404
    r = c.post(f"/api/matters/{matter_id}/files", headers=b,
               files={"file": ("x.txt", io.BytesIO(b"x"), "text/plain")})
    assert r.status_code == 404
    assert c.get(f"/api/matters/{matter_id}/files", headers=b).status_code == 404

    # user A still sees everything intact
    assert c.get(f"/api/matters/{matter_id}", headers=a).status_code == 200


def test_matter_not_found_for_unknown_id(matters_client):
    c, _ = matters_client
    headers = {"Authorization": "Bearer a"}
    assert c.get("/api/matters/does-not-exist", headers=headers).status_code == 404
    assert c.delete("/api/matters/does-not-exist", headers=headers).status_code == 204  # delete is idempotent
