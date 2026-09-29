"""Supabase integration: auth-token verification, persistent answer cache,
per-user daily quota, and saved research. Talks to Supabase's REST/Auth API
directly over httpx (already a dependency, see llm.py) rather than the
supabase-py SDK, to avoid pulling in a heavy dependency tree.

The backend always uses SUPABASE_SERVICE_ROLE_KEY, which bypasses RLS - the
backend has already verified the caller's identity itself (get_user), so
every query below explicitly filters by that verified user_id. RLS on these
tables is defense-in-depth for direct client access (e.g. a leaked anon
key), not something the backend depends on.
"""
from __future__ import annotations

import logging
import threading
import time

import httpx

from . import config

log = logging.getLogger(__name__)


def available() -> bool:
    return bool(config.SUPABASE_URL and config.SUPABASE_SERVICE_ROLE_KEY)


_client: httpx.Client | None = None
_client_lock = threading.Lock()


def _http() -> httpx.Client:
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = httpx.Client(
                    base_url=config.SUPABASE_URL,
                    headers={
                        "apikey": config.SUPABASE_SERVICE_ROLE_KEY,
                        "Authorization": f"Bearer {config.SUPABASE_SERVICE_ROLE_KEY}",
                    },
                    timeout=8.0,
                )
    return _client


# ---------------------------------------------------------------- auth
def get_user(access_token: str) -> dict | None:
    """Validate a Supabase access token (from the frontend's Authorization
    header) and return {id, email}, or None if it's missing/invalid/expired.
    A network round-trip to Supabase's own /auth/v1/user, rather than local
    JWT verification - simpler and avoids getting the signing-algorithm/key
    rotation details wrong."""
    if not available() or not access_token:
        return None
    try:
        r = _http().get("/auth/v1/user", headers={"Authorization": f"Bearer {access_token}"})
        if r.status_code != 200:
            return None
        data = r.json()
        return {"id": data["id"], "email": data.get("email")}
    except Exception as e:  # noqa: BLE001
        log.warning("supabase get_user failed: %s", str(e)[:200])
        return None


# ---------------------------------------------------------------- quota
def check_and_increment_quota(user_id: str, daily_limit: int | None = None) -> tuple[bool, int]:
    """Atomic check-and-increment via the increment_usage() RPC (avoids a
    read-then-write race between two concurrent requests). Fails open
    (allowed=True) if Supabase is unreachable - a quota outage shouldn't take
    the whole app down."""
    if not available():
        return True, 0
    if daily_limit is None:
        daily_limit = config.DAILY_QUOTA_FREE  # read at call time, not import time
    try:
        r = _http().post("/rest/v1/rpc/increment_usage",
                         json={"p_user_id": user_id, "p_daily_limit": daily_limit})
        r.raise_for_status()
        row = r.json()[0]
        return bool(row["allowed"]), int(row["request_count"])
    except Exception as e:  # noqa: BLE001
        log.warning("supabase quota check failed: %s", str(e)[:200])
        return True, 0


# ---------------------------------------------------------------- answer cache
def cache_get(cache_key: str, corpus_version: str) -> dict | None:
    """None on a miss OR if the cached row is from a stale corpus_version -
    the whole point of storing corpus_version is to invalidate old answers
    when the underlying law text changes (docs/PROGRESS.md known issue #5)."""
    if not available():
        return None
    try:
        r = _http().get("/rest/v1/answer_cache", params={
            "cache_key": f"eq.{cache_key}", "select": "answer,corpus_version", "limit": "1",
        })
        r.raise_for_status()
        rows = r.json()
        if not rows or rows[0]["corpus_version"] != corpus_version:
            return None
        return rows[0]["answer"]
    except Exception as e:  # noqa: BLE001
        log.warning("supabase cache_get failed: %s", str(e)[:200])
        return None


def cache_put(cache_key: str, corpus_version: str, language: str, question: str, answer: dict) -> None:
    if not available():
        return
    try:
        r = _http().post("/rest/v1/answer_cache", headers={"Prefer": "resolution=merge-duplicates"}, json={
            "cache_key": cache_key, "corpus_version": corpus_version, "language": language,
            "question": question[:2000], "answer": answer,
        })
        r.raise_for_status()
    except Exception as e:  # noqa: BLE001
        log.warning("supabase cache_put failed: %s", str(e)[:200])


# ---------------------------------------------------------------- saved research
def saved_research_create(user_id: str, question: str, answer: dict, language: str) -> dict | None:
    if not available():
        return None
    r = _http().post("/rest/v1/saved_research", headers={"Prefer": "return=representation"}, json={
        "user_id": user_id, "question": question[:2000], "answer": answer, "language": language,
    })
    r.raise_for_status()
    return r.json()[0]


def saved_research_list(user_id: str) -> list[dict]:
    if not available():
        return []
    r = _http().get("/rest/v1/saved_research", params={
        "user_id": f"eq.{user_id}", "select": "id,question,answer,language,created_at",
        "order": "created_at.desc", "limit": "200",
    })
    r.raise_for_status()
    return r.json()


def saved_research_delete(user_id: str, research_id: str) -> None:
    if not available():
        return
    r = _http().delete("/rest/v1/saved_research", params={"id": f"eq.{research_id}", "user_id": f"eq.{user_id}"})
    r.raise_for_status()


# ---------------------------------------------------------------- drafts (S10)
# A draft's `answers`/`language` always reflect its latest saved state;
# every save also writes an immutable snapshot to draft_versions, so a user
# can see (and in future, restore) how a draft looked before.
def draft_create(user_id: str, template_id: str, language: str, answers: dict, title: str | None = None) -> dict | None:
    if not available():
        return None
    r = _http().post("/rest/v1/drafts", headers={"Prefer": "return=representation"}, json={
        "user_id": user_id, "template_id": template_id, "language": language, "answers": answers,
        "title": (title or "")[:200] or None,
    })
    r.raise_for_status()
    draft = r.json()[0]
    _draft_version_insert(user_id, draft["id"], 1, language, answers)
    return draft


def draft_update(user_id: str, draft_id: str, language: str, answers: dict, title: str | None = None) -> dict | None:
    """Overwrites the draft's current state and appends a new version
    snapshot; returns None if the draft doesn't exist (or isn't the
    caller's)."""
    if not available():
        return None
    versions = draft_versions_list(user_id, draft_id)
    if versions is None:
        return None
    next_version = (versions[0]["version_number"] + 1) if versions else 1
    patch: dict = {"language": language, "answers": answers, "updated_at": "now()"}
    if title is not None:
        patch["title"] = title[:200] or None
    r = _http().patch(
        "/rest/v1/drafts", params={"id": f"eq.{draft_id}", "user_id": f"eq.{user_id}"},
        headers={"Prefer": "return=representation"}, json=patch,
    )
    r.raise_for_status()
    rows = r.json()
    if not rows:
        return None
    _draft_version_insert(user_id, draft_id, next_version, language, answers)
    return rows[0]


def _draft_version_insert(user_id: str, draft_id: str, version_number: int, language: str, answers: dict) -> None:
    r = _http().post("/rest/v1/draft_versions", json={
        "user_id": user_id, "draft_id": draft_id, "version_number": version_number,
        "language": language, "answers": answers,
    })
    r.raise_for_status()


def draft_list(user_id: str) -> list[dict]:
    if not available():
        return []
    r = _http().get("/rest/v1/drafts", params={
        "user_id": f"eq.{user_id}",
        "select": "id,template_id,title,language,answers,created_at,updated_at",
        "order": "updated_at.desc", "limit": "200",
    })
    r.raise_for_status()
    return r.json()


def draft_get(user_id: str, draft_id: str) -> dict | None:
    if not available():
        return None
    r = _http().get("/rest/v1/drafts", params={"id": f"eq.{draft_id}", "user_id": f"eq.{user_id}", "select": "*"})
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def draft_delete(user_id: str, draft_id: str) -> None:
    if not available():
        return
    r = _http().delete("/rest/v1/drafts", params={"id": f"eq.{draft_id}", "user_id": f"eq.{user_id}"})
    r.raise_for_status()


def draft_versions_list(user_id: str, draft_id: str) -> list[dict] | None:
    """Newest first, or None if Supabase is unavailable (distinct from `[]`,
    a draft that genuinely has no versions yet)."""
    if not available():
        return None
    r = _http().get("/rest/v1/draft_versions", params={
        "draft_id": f"eq.{draft_id}", "user_id": f"eq.{user_id}",
        "select": "id,version_number,language,answers,created_at",
        "order": "version_number.desc",
    })
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------- matters (S11)
# A matter groups a client's facts/notes/tasks/files/saved-research/drafts
# under one roof. Every sub-resource carries its own user_id (not just
# matter_id) so RLS can check ownership directly on that row without a
# join - same reasoning as draft_versions in S10.
def matter_create(user_id: str, client_name: str, facts: str | None = None) -> dict | None:
    if not available():
        return None
    r = _http().post("/rest/v1/matters", headers={"Prefer": "return=representation"}, json={
        "user_id": user_id, "client_name": client_name[:200], "facts": facts,
    })
    r.raise_for_status()
    return r.json()[0]


def matter_list(user_id: str) -> list[dict]:
    if not available():
        return []
    r = _http().get("/rest/v1/matters", params={
        "user_id": f"eq.{user_id}",
        "select": "id,client_name,facts,status,created_at,updated_at",
        "order": "updated_at.desc", "limit": "200",
    })
    r.raise_for_status()
    return r.json()


def matter_get(user_id: str, matter_id: str) -> dict | None:
    if not available():
        return None
    r = _http().get("/rest/v1/matters", params={"id": f"eq.{matter_id}", "user_id": f"eq.{user_id}", "select": "*"})
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def matter_update(user_id: str, matter_id: str, client_name: str | None = None,
                   facts: str | None = None, status: str | None = None) -> dict | None:
    if not available():
        return None
    patch: dict = {"updated_at": "now()"}
    if client_name is not None:
        patch["client_name"] = client_name[:200]
    if facts is not None:
        patch["facts"] = facts
    if status is not None:
        patch["status"] = status
    r = _http().patch(
        "/rest/v1/matters", params={"id": f"eq.{matter_id}", "user_id": f"eq.{user_id}"},
        headers={"Prefer": "return=representation"}, json=patch,
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def matter_delete(user_id: str, matter_id: str) -> None:
    if not available():
        return
    r = _http().delete("/rest/v1/matters", params={"id": f"eq.{matter_id}", "user_id": f"eq.{user_id}"})
    r.raise_for_status()


def matter_note_create(user_id: str, matter_id: str, body: str) -> dict | None:
    if not available():
        return None
    r = _http().post("/rest/v1/matter_notes", headers={"Prefer": "return=representation"}, json={
        "user_id": user_id, "matter_id": matter_id, "body": body[:10000],
    })
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def matter_note_list(user_id: str, matter_id: str) -> list[dict]:
    if not available():
        return []
    r = _http().get("/rest/v1/matter_notes", params={
        "user_id": f"eq.{user_id}", "matter_id": f"eq.{matter_id}",
        "select": "id,body,created_at", "order": "created_at.desc",
    })
    r.raise_for_status()
    return r.json()


def matter_note_delete(user_id: str, matter_id: str, note_id: str) -> None:
    if not available():
        return
    r = _http().delete("/rest/v1/matter_notes", params={
        "id": f"eq.{note_id}", "matter_id": f"eq.{matter_id}", "user_id": f"eq.{user_id}",
    })
    r.raise_for_status()


def matter_task_create(user_id: str, matter_id: str, title: str, due_date: str | None = None) -> dict | None:
    if not available():
        return None
    r = _http().post("/rest/v1/matter_tasks", headers={"Prefer": "return=representation"}, json={
        "user_id": user_id, "matter_id": matter_id, "title": title[:500], "due_date": due_date,
    })
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def matter_task_list(user_id: str, matter_id: str) -> list[dict]:
    if not available():
        return []
    r = _http().get("/rest/v1/matter_tasks", params={
        "user_id": f"eq.{user_id}", "matter_id": f"eq.{matter_id}",
        "select": "id,title,done,due_date,created_at,updated_at", "order": "created_at.desc",
    })
    r.raise_for_status()
    return r.json()


def matter_task_update(user_id: str, matter_id: str, task_id: str, title: str | None = None,
                        done: bool | None = None, due_date: str | None = None) -> dict | None:
    if not available():
        return None
    patch: dict = {"updated_at": "now()"}
    if title is not None:
        patch["title"] = title[:500]
    if done is not None:
        patch["done"] = done
    if due_date is not None:
        patch["due_date"] = due_date
    r = _http().patch(
        "/rest/v1/matter_tasks",
        params={"id": f"eq.{task_id}", "matter_id": f"eq.{matter_id}", "user_id": f"eq.{user_id}"},
        headers={"Prefer": "return=representation"}, json=patch,
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def matter_task_delete(user_id: str, matter_id: str, task_id: str) -> None:
    if not available():
        return
    r = _http().delete("/rest/v1/matter_tasks", params={
        "id": f"eq.{task_id}", "matter_id": f"eq.{matter_id}", "user_id": f"eq.{user_id}",
    })
    r.raise_for_status()


# ---------------------------------------------------------------- matter files (S11)
# Files live in the private "matter-files" Supabase Storage bucket, under
# {user_id}/{matter_id}/{filename} - storage.objects RLS policies check
# that path prefix directly, so a signed URL only ever unlocks the
# requesting user's own folder even if the id leaks.
MATTER_FILES_BUCKET = "matter-files"


def matter_file_create(user_id: str, matter_id: str, filename: str, content: bytes, content_type: str) -> dict | None:
    """Uploads the bytes to Storage, then records the metadata row. Storage
    upload happens first so a failed metadata insert never leaves an
    orphaned DB row pointing at nothing."""
    if not available():
        return None
    storage_path = f"{user_id}/{matter_id}/{filename}"
    upload = _http().post(
        f"/storage/v1/object/{MATTER_FILES_BUCKET}/{storage_path}",
        headers={"Content-Type": content_type or "application/octet-stream"},
        content=content,
    )
    upload.raise_for_status()
    r = _http().post("/rest/v1/matter_files", headers={"Prefer": "return=representation"}, json={
        "user_id": user_id, "matter_id": matter_id, "storage_path": storage_path,
        "filename": filename, "content_type": content_type, "size_bytes": len(content),
    })
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def matter_file_list(user_id: str, matter_id: str) -> list[dict]:
    if not available():
        return []
    r = _http().get("/rest/v1/matter_files", params={
        "user_id": f"eq.{user_id}", "matter_id": f"eq.{matter_id}",
        "select": "id,filename,content_type,size_bytes,storage_path,created_at", "order": "created_at.desc",
    })
    r.raise_for_status()
    return r.json()


def matter_file_signed_url(user_id: str, matter_id: str, file_id: str, expires_in: int = 300) -> str | None:
    """A time-limited download URL for one file, or None if it doesn't
    exist / isn't the caller's."""
    if not available():
        return None
    rows_resp = _http().get("/rest/v1/matter_files", params={
        "id": f"eq.{file_id}", "matter_id": f"eq.{matter_id}", "user_id": f"eq.{user_id}", "select": "storage_path",
    })
    rows_resp.raise_for_status()
    rows = rows_resp.json()
    if not rows:
        return None
    storage_path = rows[0]["storage_path"]
    signed = _http().post(
        f"/storage/v1/object/sign/{MATTER_FILES_BUCKET}/{storage_path}", json={"expiresIn": expires_in},
    )
    signed.raise_for_status()
    return config.SUPABASE_URL + "/storage/v1" + signed.json()["signedURL"]


def matter_file_delete(user_id: str, matter_id: str, file_id: str) -> None:
    if not available():
        return
    rows_resp = _http().get("/rest/v1/matter_files", params={
        "id": f"eq.{file_id}", "matter_id": f"eq.{matter_id}", "user_id": f"eq.{user_id}", "select": "storage_path",
    })
    rows_resp.raise_for_status()
    rows = rows_resp.json()
    if not rows:
        return
    _http().delete(f"/storage/v1/object/{MATTER_FILES_BUCKET}/{rows[0]['storage_path']}")
    _http().delete("/rest/v1/matter_files", params={
        "id": f"eq.{file_id}", "matter_id": f"eq.{matter_id}", "user_id": f"eq.{user_id}",
    })


# ---------------------------------------------------------------- compliance radar (S12)
def company_profile_get(user_id: str) -> dict | None:
    if not available():
        return None
    r = _http().get("/rest/v1/company_profiles", params={"user_id": f"eq.{user_id}", "select": "*"})
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def company_profile_upsert(user_id: str, company_name: str, entity_type: str, pan_vat_registered: bool,
                            has_employees: bool, reminder_email: str | None = None) -> dict | None:
    """One profile per user - create it if missing, otherwise overwrite it."""
    if not available():
        return None
    body = {
        "user_id": user_id, "company_name": company_name[:200], "entity_type": entity_type,
        "pan_vat_registered": pan_vat_registered, "has_employees": has_employees,
        "reminder_email": reminder_email, "updated_at": "now()",
    }
    r = _http().post(
        "/rest/v1/company_profiles",
        params={"on_conflict": "user_id"},
        headers={"Prefer": "return=representation,resolution=merge-duplicates"},
        json=body,
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def obligations_list() -> list[dict]:
    """The full seeded obligation catalogue - public reference data, not
    scoped to any user."""
    if not available():
        return []
    r = _http().get("/rest/v1/obligations", params={"select": "*", "order": "category,id"})
    r.raise_for_status()
    return r.json()


def all_company_profiles() -> list[dict]:
    """Used only by the reminder job (backend/scripts/send_compliance_reminders.py),
    which runs with the service-role key outside any single user's request."""
    if not available():
        return []
    r = _http().get("/rest/v1/company_profiles", params={"select": "*"})
    r.raise_for_status()
    return r.json()


def reminder_already_sent(user_id: str, obligation_id: str, period: str) -> bool:
    if not available():
        return False
    r = _http().get("/rest/v1/obligation_reminders_sent", params={
        "user_id": f"eq.{user_id}", "obligation_id": f"eq.{obligation_id}", "period": f"eq.{period}",
        "select": "id", "limit": "1",
    })
    r.raise_for_status()
    return bool(r.json())


def reminder_record_sent(user_id: str, obligation_id: str, period: str, due_date_bs: str, due_date_ad: str) -> None:
    if not available():
        return
    r = _http().post("/rest/v1/obligation_reminders_sent", json={
        "user_id": user_id, "obligation_id": obligation_id, "period": period,
        "due_date_bs": due_date_bs, "due_date_ad": due_date_ad,
    })
    r.raise_for_status()


# ---------------------------------------------------------------- IP rate limit
# In-memory sliding window, per process. Good enough for a single-instance
# free-tier deploy; would need a shared store (e.g. this same Postgres) to
# be correct across multiple backend instances.
_ip_hits: dict[str, list[float]] = {}
_ip_lock = threading.Lock()


def check_ip_rate_limit(ip: str, per_hour: int | None = None) -> bool:
    """True if this IP is still under its hourly budget (and records the hit)."""
    if per_hour is None:
        per_hour = config.IP_RATE_LIMIT_PER_HOUR  # read at call time, not import time
    now = time.time()
    cutoff = now - 3600
    with _ip_lock:
        hits = [t for t in _ip_hits.get(ip, []) if t > cutoff]
        if len(hits) >= per_hour:
            _ip_hits[ip] = hits
            return False
        hits.append(now)
        _ip_hits[ip] = hits
        return True
