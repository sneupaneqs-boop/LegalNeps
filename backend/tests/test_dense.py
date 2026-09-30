"""Dense retrieval: vector store (digest mismatch, missing file, id alignment), fusion ordering,
and that every filter still applies after fusion. No model files needed: the query side is a fake
that returns fixed cosine columns."""
import logging

import numpy as np
import pytest

from app import dense, retrieval
from fixtures import ENTRIES

DIM = dense.DIM


class FakeDense:
    """Stands in for dense.Dense: `wanted` maps query text -> {passage id: cosine}; others get 0.1."""
    ready = True

    def __init__(self, idx, wanted, boom=False):
        self.idx, self.wanted, self.boom = idx, wanted, boom

    def scores(self, texts):
        if self.boom:
            raise RuntimeError("encoder exploded")
        out = np.full((len(self.idx), len(texts)), 0.1, dtype=np.float32)
        pos = {pid: i for i, pid in enumerate(self.idx.ids)}
        for j, t in enumerate(texts):
            for pid, c in self.wanted.get(t, {}).items():
                out[pos[pid], j] = c
        return out

    def clear_cache(self):
        pass


@pytest.fixture(scope="module")
def idx(tmp_path_factory):
    original = retrieval.CACHE_DIR
    retrieval.CACHE_DIR = tmp_path_factory.mktemp("cache")
    try:
        yield retrieval.Index([dict(e) for e in ENTRIES], "test-digest")
    finally:
        retrieval.CACHE_DIR = original


@pytest.fixture
def hybrid(idx):
    """Attach a fake dense, restore afterwards."""
    def attach(wanted, boom=False):
        idx.dense = FakeDense(idx, wanted, boom)
        return idx
    yield attach
    idx.dense = None


# -- fusion ordering ------------------------------------------------------------------
def test_dense_finds_what_bm25_cannot(idx, hybrid):
    q = "zzzqqq"  # no lexical match at all
    assert idx.search([q], top_k=3, mode="bm25") == []
    hybrid({q: {"law-civ-400": 0.9}})
    hits = idx.search([q], top_k=3)
    assert hits[0]["id"] == "law-civ-400"
    assert hits[0]["score"] == 0.0 and hits[0]["dense"] == pytest.approx(0.9)


def test_agreement_beats_either_signal_alone(idx, hybrid):
    q = "बाल विवाह कैद"  # BM25: law-crim-173 first
    hybrid({q: {"law-civ-400": 0.95, "law-crim-173": 0.9}})
    hits = idx.search([q], top_k=3)
    assert hits[0]["id"] == "law-crim-173"  # #1 lexically, #2 semantically
    assert idx.search([q], top_k=3, mode="dense")[0]["id"] == "law-civ-400"
    assert idx.search([q], top_k=3, mode="bm25")[0]["id"] == "law-crim-173"


def test_dense_weight_shifts_the_order(idx, hybrid, monkeypatch):
    q = "बाल विवाह कैद"
    hybrid({q: {"law-civ-400": 0.95}})
    monkeypatch.setitem(retrieval.HYBRID, "dense_depth", 1)  # only the dense #1 is fused (7-passage toy corpus)
    monkeypatch.setitem(retrieval.HYBRID, "dense_weight", 5.0)
    assert idx.search([q], top_k=3)[0]["id"] == "law-civ-400"
    monkeypatch.setitem(retrieval.HYBRID, "dense_weight", 0.0)
    assert idx.search([q], top_k=3)[0]["id"] == "law-crim-173"


def test_light_glossary_terms_skip_the_dense_side(idx, hybrid):
    hybrid({"zzzqqq": {"law-civ-99": 0.9}, "tenant": {"law-civ-400": 0.99}})
    hits = idx.search([("zzzqqq", 1.0), ("tenant", 0.25)], top_k=5)  # 0.25 < dense_min_w: "tenant" is not encoded
    assert hits[0]["id"] == "law-civ-99"
    assert all(h["dense"] < 0.95 for h in hits if h["id"] == "law-civ-400")


def test_first_query_is_primary_even_with_low_bm25_weight(idx, hybrid):
    hybrid({"my message": {"law-civ-400": 0.9}})
    hits = idx.search([("my message", 0.35)], top_k=3)
    assert hits[0]["id"] == "law-civ-400"


# -- filters still apply after fusion ------------------------------------------------------
def test_category_filter_after_fusion(idx, hybrid):
    q = "zzzqqq"
    hybrid({q: {"nkp-1": 0.99, "law-civ-99": 0.8}})
    assert [h["id"] for h in idx.search([q], top_k=2, category="law")][0] == "law-civ-99"
    assert [h["id"] for h in idx.search([q], top_k=2, category="precedent")] == ["nkp-1"]


def test_bills_never_surface_by_default_even_if_dense_top(idx, hybrid):
    q = "zzzqqq"
    hybrid({q: {"law-bill-1": 0.99, "law-civ-99": 0.3}})
    ids = [h["id"] for h in idx.search([q], top_k=5)]
    assert "law-bill-1" not in ids
    assert idx.search([q], top_k=1, include_bills=True)[0]["id"] == "law-bill-1"


def test_doc_type_and_status_filters_after_fusion(idx, hybrid):
    q = "zzzqqq"
    hybrid({q: {"law-const-11": 0.99, "law-civ-99": 0.9}})
    assert idx.search([q], top_k=1, doc_type="act")[0]["id"] == "law-civ-99"
    assert all(h["status"] == "in_force" for h in idx.search([q], top_k=3, status="in_force"))


def test_duplicate_text_is_collapsed_after_fusion(idx, hybrid):
    q = "zzzqqq"
    hybrid({q: {"law-crim-173-dup": 0.99, "law-crim-173": 0.98}})
    ids = [h["id"] for h in idx.search([q], top_k=5)]
    assert ("law-crim-173" in ids) != ("law-crim-173-dup" in ids)  # exactly one of the two copies


def test_per_doc_cap_after_fusion(idx, hybrid):
    q = "zzzqqq"
    hybrid({q: {"law-civ-99": 0.99, "law-civ-400": 0.98, "law-crim-173": 0.97}})
    ids = [h["id"] for h in idx.search([q], top_k=3, per_doc_cap=1)]
    assert len([i for i in ids if i.startswith("law-civ")]) == 1


# -- degradation ------------------------------------------------------------------------------
def test_encoder_failure_falls_back_to_bm25(idx, hybrid):
    hybrid({}, boom=True)
    hits = idx.search(["बाल विवाहको सजायलाई"], top_k=2)
    assert hits[0]["id"] == "law-crim-173" and "dense" not in hits[0]


def test_no_dense_is_plain_bm25(idx):
    idx.dense = None
    hits = idx.search(["घरबहाल धरौटी फिर्ता"], top_k=3)
    assert hits[0]["id"] == "law-civ-400" and "dense" not in hits[0]
    assert idx.search(["घरबहाल धरौटी फिर्ता"], top_k=3, mode="dense")[0]["id"] == "law-civ-400"


# -- vector store -----------------------------------------------------------------------------------
def _vectors(n, seed=0):
    v = np.random.default_rng(seed).normal(size=(n, DIM)).astype(np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def _write(path, ids, vecs, digest="d1"):
    q, s = dense.quantize(vecs)
    dense.save_vectors(path, ids, q, s, digest)


def test_quantize_roundtrip_keeps_cosine():
    v = _vectors(20)
    q, s = dense.quantize(v)
    back = q.astype(np.float32) * s.astype(np.float32)[:, None]
    assert np.abs((back * v).sum(1) - 1).max() < 0.01


def test_store_exact_match(tmp_path):
    ids, v = [f"p{i}" for i in range(10)], _vectors(10)
    _write(tmp_path / "v.npz", ids, v, "d1")
    st = dense.VectorStore.load(tmp_path / "v.npz", ids, "d1")
    assert st.info["exact"] and st.info["missing"] == 0 and st.have.all()
    sc = st.scores(v[[3]])
    assert int(sc[:, 0].argmax()) == 3 and sc[3, 0] == pytest.approx(1.0, abs=0.01)


def test_store_digest_mismatch_reuses_surviving_ids(tmp_path, caplog):
    ids, v = [f"p{i}" for i in range(10)], _vectors(10)
    _write(tmp_path / "v.npz", ids, v, "old")
    # new corpus: p2 and p5 removed, p10/p11 added, order changed
    new_ids = ["p9", "p0", "p10", "p1", "p3", "p4", "p6", "p7", "p8", "p11"]
    with caplog.at_level(logging.WARNING, logger="kanooni.dense"):
        st = dense.VectorStore.load(tmp_path / "v.npz", new_ids, "new")
    assert st is not None and not st.info["exact"] and st.info["missing"] == 2
    assert "2 passages have no vector" in caplog.text
    assert st.have.tolist() == [True, True, False, True, True, True, True, True, True, False]
    # ids stay aligned: querying with p6's vector finds p6's new row
    sc = st.scores(v[[6]])[:, 0]
    assert new_ids[int(sc.argmax())] == "p6"
    assert sc[2] == -1.0 and sc[9] == -1.0  # passages without vectors never rank


def test_store_same_ids_other_digest_is_used_but_flagged(tmp_path, caplog):
    ids, v = [f"p{i}" for i in range(5)], _vectors(5)
    _write(tmp_path / "v.npz", ids, v, "old")
    with caplog.at_level(logging.WARNING, logger="kanooni.dense"):
        st = dense.VectorStore.load(tmp_path / "v.npz", ids, "new")
    assert st.have.all() and "digest differs" in caplog.text


def test_store_missing_file_is_none(tmp_path):
    assert dense.VectorStore.load(tmp_path / "nope.npz", ["a"], "d") is None


def test_store_corrupt_or_foreign_artifact_is_none(tmp_path):
    (tmp_path / "bad.npz").write_bytes(b"not a zip")
    assert dense.VectorStore.load(tmp_path / "bad.npz", ["a"], "d") is None
    np.savez(tmp_path / "foreign.npz", ids=np.array(["a"]), q=np.zeros((1, DIM), np.int8),
             scale=np.ones(1, np.float16), meta=np.array('{"model": "other", "dim": 384, "version": 1}'))
    assert dense.VectorStore.load(tmp_path / "foreign.npz", ["a"], "d") is None


def test_load_dense_without_artifact_or_model_is_bm25_only(tmp_path, monkeypatch):
    monkeypatch.setattr(dense, "VECTORS_PATH", tmp_path / "missing.npz")
    monkeypatch.setattr(dense, "MODEL_DIR", tmp_path / "no-model")
    assert dense.load_dense(["a"], "d") is None


def test_dense_env_switch(monkeypatch):
    monkeypatch.setenv("DENSE", "0")
    assert dense.load_dense(["a"], "d") is None


def test_passage_text_carries_titles():
    t = dense.passage_text(ENTRIES[0])
    assert ENTRIES[0]["doc_title_ne"] in t and ENTRIES[0]["title_ne"] in t and "Muluki Civil Code" in t
