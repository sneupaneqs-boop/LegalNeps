from app import config, supa


def test_unavailable_when_not_configured(monkeypatch):
    monkeypatch.setattr(config, "SUPABASE_URL", "")
    monkeypatch.setattr(config, "SUPABASE_SERVICE_ROLE_KEY", "")
    assert supa.available() is False
    assert supa.get_user("sometoken") is None
    assert supa.cache_get("key", "digest") is None
    allowed, count = supa.check_and_increment_quota("user-1")
    assert allowed is True and count == 0  # fails open, never blocks when unconfigured


def test_ip_rate_limit_blocks_after_the_hourly_budget(monkeypatch):
    supa._ip_hits.clear()
    ip = "203.0.113.5"
    for _ in range(3):
        assert supa.check_ip_rate_limit(ip, per_hour=3) is True
    assert supa.check_ip_rate_limit(ip, per_hour=3) is False


def test_ip_rate_limit_is_per_ip(monkeypatch):
    supa._ip_hits.clear()
    for _ in range(2):
        assert supa.check_ip_rate_limit("203.0.113.10", per_hour=2) is True
    assert supa.check_ip_rate_limit("203.0.113.10", per_hour=2) is False
    # a different IP has its own, untouched budget
    assert supa.check_ip_rate_limit("203.0.113.11", per_hour=2) is True


def test_ip_rate_limit_window_expires(monkeypatch):
    supa._ip_hits.clear()
    ip = "203.0.113.20"
    t = [1000.0]
    monkeypatch.setattr(supa.time, "time", lambda: t[0])
    assert supa.check_ip_rate_limit(ip, per_hour=1) is True
    assert supa.check_ip_rate_limit(ip, per_hour=1) is False
    t[0] += 3601  # an hour and one second later, the old hit has aged out
    assert supa.check_ip_rate_limit(ip, per_hour=1) is True
