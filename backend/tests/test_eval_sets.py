"""V1: the real-world and held-out eval sets, the `--set` flag of eval/run_eval.py,
and the corpus check that every case's governing provisions really exist."""
import json
import os
import re
import sys

import pytest

from app.retrieval import CORPUS_DIR

EVAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval")
sys.path.insert(0, EVAL)

import run_eval  # noqa: E402

requires_corpus = pytest.mark.skipif(
    not (CORPUS_DIR / "manifest.json").exists(), reason="built corpus shards not present"
)


def _lines(name):
    with open(os.path.join(EVAL, name), encoding="utf-8") as f:
        return f.read().splitlines()


def _norm(q):
    return re.sub(r"\s+", " ", q).strip().lower()


DEFAULT = run_eval.load(os.path.join(EVAL, "questions.jsonl"))
REALWORLD = run_eval.load(os.path.join(EVAL, "questions_realworld.jsonl"))
HELDOUT = run_eval.load(os.path.join(EVAL, "questions_heldout.jsonl"))


def test_default_set_is_unchanged():
    assert run_eval.SETS["default"] == "questions.jsonl"
    assert run_eval.set_path(None).endswith("questions.jsonl")
    assert len(DEFAULT) == 150
    assert all({"q", "expect", "area"} <= set(q) for q in DEFAULT)


def test_load_skips_comment_and_blank_lines(tmp_path):
    p = tmp_path / "x.jsonl"
    p.write_text('# comment\n\n{"q": "a", "expect": ["b"], "area": "c"}\n  # indented comment\n', encoding="utf-8")
    assert run_eval.load(str(p)) == [{"q": "a", "expect": ["b"], "area": "c"}]


def test_set_sizes_and_schema():
    assert len(REALWORLD) == 30
    assert len(HELDOUT) == 50
    for rows in (REALWORLD, HELDOUT):
        assert len({r["id"] for r in rows}) == len(rows)
        for r in rows:
            assert {"id", "q", "lang", "area", "expect", "sections", "why"} <= set(r), r["q"]
            assert r["lang"] in ("en", "ne", "roman")
            assert r["expect"] and all(isinstance(x, str) and x for x in r["expect"])
            assert r["why"].strip()
            assert r["sections"]
            for s in r["sections"]:
                assert s["doc"] and s["contains"]
                assert bool(s.get("section")) != bool(s.get("title_contains")), "exactly one of section/title_contains"


def test_the_two_audited_failures_are_first_and_verbatim():
    assert REALWORLD[0]["q"] == "घरबेटीले deposit फिर्ता दिएन, के गर्ने?"
    assert REALWORLD[1]["q"] == "My employer has not paid my salary for 4 months. What can I do?"


def test_heldout_is_disjoint_and_marked_do_not_tune():
    seen = {_norm(q["q"]) for q in DEFAULT}
    for r in REALWORLD:
        assert _norm(r["q"]) not in seen, r["q"]
        seen.add(_norm(r["q"]))
    for r in HELDOUT:
        assert _norm(r["q"]) not in seen, r["q"]
    header = "\n".join(l for l in _lines("questions_heldout.jsonl") if l.startswith("#"))
    assert "DO NOT USE FOR TUNING" in header
    assert _lines("questions_heldout.jsonl")[0].startswith("# HELD-OUT SET")


def test_heldout_language_mix_and_domain_spread():
    non_en = sum(1 for r in HELDOUT if r["lang"] != "en")
    assert 0.35 <= non_en / len(HELDOUT) <= 0.45  # ~40% Nepali / romanised
    areas = {r["area"] for r in HELDOUT}
    assert len(areas) >= 20


def test_realworld_covers_the_requested_domains():
    text = " ".join(r["area"] for r in REALWORLD)
    for needle in ("tenancy", "labour", "foreign employment", "cheque", "loans", "custody", "partition", "inheritance",
                   "land", "police", "bail", "cyber", "domestic violence", "consumer", "RTI", "company", "tax",
                   "banking", "securities", "citizenship", "traffic", "medical", "defamation", "maintenance"):
        assert needle in text, needle


def test_set_flag_parses_and_dispatches(monkeypatch):
    seen = {}
    monkeypatch.setattr(run_eval, "cmd_retrieval", lambda a: seen.update(set=a.set, k=a.k))
    monkeypatch.setattr(sys, "argv", ["run_eval.py", "retrieval", "--set", "heldout"])
    run_eval.main()
    assert seen == {"set": "heldout", "k": 8}
    monkeypatch.setattr(sys, "argv", ["run_eval.py", "retrieval"])
    run_eval.main()
    assert seen["set"] == "default"
    monkeypatch.setattr(sys, "argv", ["run_eval.py", "retrieval", "--set", "bogus"])
    with pytest.raises(SystemExit):
        run_eval.main()


def test_first_section_hit_ranking():
    sections = [
        {"doc": "श्रम ऐन, २०७४", "section": "162", "contains": ["x"]},
        {"doc": "परिपत्र नं. १०", "title_contains": "गुनासो सुनवाई", "contains": ["x"]},
    ]
    results = [
        {"doc_title_ne": "श्रम ऐन, २०७४", "section": "34"},
        {"doc_title_ne": "श्रम ऐन, २०७४", "section": "162"},
        {"doc_title_ne": "परिपत्र नं. १० (क, ख, ग): एकीकृत निर्देशन", "section": "9 (1)", "title_ne": "x - गुनासो सुनवाई सम्बन्धी"},
    ]
    assert run_eval._first_section_hit(results, sections) == 2
    assert run_eval._first_section_hit(results[2:], sections) == 1
    assert run_eval._first_section_hit(results[:1], sections) is None
    assert run_eval._first_section_hit(results, None) is None


@requires_corpus
@pytest.mark.parametrize("name", ["realworld", "heldout"])
def test_every_governing_provision_exists_in_the_corpus(name):
    """Each case's `sections` must resolve in the real corpus and contain the quoted phrase."""
    from casecheck import DocResolver, verify_case
    from app.retrieval import get_index
    idx = get_index()
    resolver = DocResolver(idx)
    failures = {}
    for q in run_eval.load(run_eval.set_path(name)):
        problems = verify_case(q, idx, resolver)
        if problems:
            failures[q["id"]] = problems
    assert not failures, json.dumps(failures, ensure_ascii=False, indent=1)
