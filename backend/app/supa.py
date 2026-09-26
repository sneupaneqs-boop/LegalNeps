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
