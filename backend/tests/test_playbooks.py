"""S6: every playbook's cited provisions must actually exist in the corpus.
Uses the real built corpus (not fixtures) since that's what production
serves - a playbook citing a section our own retrieval index can't find
would silently cite nothing to the user."""
import pytest

from app import playbooks
from app.retrieval import CORPUS_DIR

requires_corpus = pytest.mark.skipif(
    not (CORPUS_DIR / "manifest.json").exists(), reason="built corpus shards not present"
)

EXPECTED_IDS = {
    "unpaid_salary", "deposit_not_returned", "domestic_violence", "divorce",
    "cheque_bounce", "inheritance_share", "consumer_complaint", "cyber_harassment",
}


def test_eight_playbooks_exist():
    ids = {p["id"] for p in playbooks.list_playbooks()}
    assert ids == EXPECTED_IDS


@requires_corpus
def test_every_cited_provision_resolves_in_the_real_corpus():
    # raises UnresolvedProvision on the first bad citation - a hard failure,
    # not a soft warning, per S6's "done when": no playbook may cite a
    # provision the corpus doesn't have.
    resolved = playbooks.all_playbooks_resolved()
    assert len(resolved) == 8
    for pb in resolved:
        assert pb["provisions"], f"{pb['id']} cites no provisions at all"
        for p in pb["provisions"]:
            assert p["citation"], f"{pb['id']}: provision resolved but has no citation text"


@requires_corpus
def test_every_playbook_renders_with_a_full_shape():
    for pb in playbooks.all_playbooks_resolved():
        assert pb["issue"]["en"] and pb["issue"]["ne"]
        assert len(pb["fact_questions"]) >= 2
        assert len(pb["evidence"]) >= 2
        assert pb["forum"]["en"] and pb["forum"]["ne"]
        assert pb["limitation"]["note"]["en"] and pb["limitation"]["note"]["ne"]
        assert len(pb["next_steps"]) >= 2


@requires_corpus
def test_bogus_provision_is_rejected_not_silently_dropped():
    from app.playbooks import UnresolvedProvision, _resolve_provision

    with pytest.raises(UnresolvedProvision):
        _resolve_provision({"law_title_ne": "यस्तो ऐन कहिल्यै थिएन", "section": "1"})
    with pytest.raises(UnresolvedProvision):
        _resolve_provision({"law_title_ne": "मुलुकी देवानी संहिता, २०७४", "section": "99999"})


def test_get_playbook_unknown_id_returns_none():
    assert playbooks.get_playbook("does-not-exist") is None


@requires_corpus
def test_playbook_api_endpoints():
    # against the real corpus (not the tiny test_api.py fixture, which
    # doesn't carry the statutes these playbooks actually cite) - safe to
    # hit get_index() directly since the CACHE_DIR leak that made this slow
    # is fixed (see test_retrieval.py's idx fixture).
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        r = c.get("/api/playbooks")
        assert r.status_code == 200
        ids = {p["id"] for p in r.json()}
        assert ids == EXPECTED_IDS

        r = c.get("/api/playbooks/unpaid_salary")
        assert r.status_code == 200
        body = r.json()
        assert body["issue"]["ne"]
        assert any(p["section"] == "162" for p in body["provisions"])

        assert c.get("/api/playbooks/does-not-exist").status_code == 404
