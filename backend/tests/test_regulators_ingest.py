"""Chunking + schema tests for the regulator pipeline (ingest_regulators.py /
scrape_regulators.py). No network and no PDFs: page text is a small fixture."""
import gzip
import hashlib
import json

import ingest_regulators as I
import scrape_regulators as S

# Fixture: a Unified-Directive-style document (units restart clause numbering, headings end in ः)
DIRECTIVE = """नेपाल राष्ट्र बैंक
एकीकृत निर्देशन, २०८२

इ.प्रा.निर्देशन नं. १/०८२
१। न्यूनतम पुँजीकोष सम्बन्धी व्यवस्थाः
(१) वाणिज्य बैंकले कम्तीमा आठ अर्ब रुपैयाँ चुक्ता पुँजी कायम गर्नु पर्नेछ । यो व्यवस्था सबै इजाजतपत्रप्राप्त संस्थाका लागि लागू हुनेछ ।
२। पुँजीकोष अनुपात सम्बन्धी व्यवस्थाः
(१) संस्थाले जोखिम भारित सम्पत्तिको तुलनामा कम्तीमा ११ प्रतिशत कुल पुँजीकोष कायम गर्नु पर्नेछ । अनुपात त्रैमासिक रूपमा गणना गरिनेछ ।
३। लाभांश वितरण सम्बन्धी व्यवस्थाः
(१) संस्थाले पुँजीकोष कायम नगरी नगद लाभांश वितरण गर्न पाइने छैन । यसको अनुगमन नेपाल राष्ट्र बैंकले गर्नेछ ।

इ.प्रा.निर्देशन नं. २/०८२
१। कर्जा सीमा सम्बन्धी व्यवस्थाः
(१) एउटै ऋणी समूहलाई प्रदान गर्ने कर्जाको सीमा प्राथमिक पुँजीको पच्चीस प्रतिशतभन्दा बढी हुनु हुँदैन । सीमा नाघेमा नियमनकारी कारबाही हुनेछ ।
२। सञ्चालक समिति सम्बन्धी व्यवस्थाः
(१) संस्थाको सञ्चालक समितिले वर्षमा कम्तीमा बाह्र पटक बैठक बस्नु पर्नेछ । बैठकको माइन्युट राखिनेछ ।
"""

ACT = """कम्पनी दर्ता निर्देशिका
प्रस्तावना: कम्पनी दर्ता प्रक्रिया व्यवस्थित गर्न वाञ्छनीय भएकोले,

१। संक्षिप्त नाम र प्रारम्भ : यो निर्देशिका २०८२ सालदेखि लागू हुनेछ । यसलाई कम्पनी दर्ता निर्देशिका भनिनेछ ।

२। परिभाषा : विषय वा प्रसङ्गले अर्को अर्थ नलागेमा यस निर्देशिकामा कम्पनी भन्नाले कम्पनी ऐन बमोजिम दर्ता भएको कम्पनी सम्झनु पर्छ ।

३। वार्षिक विवरण : कम्पनीले प्रत्येक आर्थिक वर्षको वार्षिक विवरण कम्पनी रजिष्ट्रारको कार्यालयमा बुझाउनु पर्नेछ ।
"""

ENGLISH = """AML/CFT Guidance to Dealers in Precious Metals
This guidance explains the reporting obligations of dealers in precious metals and stones under the Assets (Money) Laundering Prevention Act. Reporting entities must identify beneficial owners and file threshold transaction reports with the Financial Intelligence Unit within the prescribed time.
Dealers must maintain records of customer due diligence for at least five years after the end of the business relationship. Failure to comply may result in penalties under the Act and the directives issued by the Inland Revenue Department as supervisor."""

TOC = "\n".join(f"{i}। विषय {i} ........ {i + 3}" for i in range(1, 12))

REC = {
    "url": "https://www.nrb.org.np/bfr/example/", "title": "परिपत्र नं. १ (क, ख, ग) २०८३/८४: एकीकृत निर्देशन, २०८२ मा संशोधन",
    "published": "August 27, 2026", "kind": "circular", "doc_type": "directive", "authority": "nrb",
    "sha256": "ab" * 32, "fetched_at": "2026-09-29T10:00:00Z",
}

REQUIRED = ["id", "category", "doc_type", "topic", "doc_title_ne", "doc_title_en", "section", "title_ne", "title_en",
            "text_ne", "text_en", "source_ne", "source_en", "url", "status", "authority", "published", "fetched_at"]


def _ex(text: str, dev: float = 1.0) -> dict:
    return {"pages": [text], "devanagari_share": dev}


# --- chunking -------------------------------------------------------------
def test_directive_is_split_per_unit_and_clause():
    chunks = I.chunk_text([DIRECTIVE], "directive")
    keyed = [(c["unit"], c["section"]) for c in chunks if c["section"]]
    assert keyed == [("इ.प्रा.निर्देशन नं. १/०८२", "1"), ("इ.प्रा.निर्देशन नं. १/०८२", "2"), ("इ.प्रा.निर्देशन नं. १/०८२", "3"),
                     ("इ.प्रा.निर्देशन नं. २/०८२", "1"), ("इ.प्रा.निर्देशन नं. २/०८२", "2")]
    cap = next(c for c in chunks if c["unit"].endswith("१/०८२") and c["section"] == "2")
    assert cap["heading"] == "पुँजीकोष अनुपात सम्बन्धी व्यवस्था"
    assert "११ प्रतिशत" in cap["text"] and "लाभांश" not in cap["text"]  # cut at the next clause


def test_directive_without_numbering_falls_back_to_paragraph_windows():
    text = "\n\n".join("यो एउटा परिपत्रको अनुच्छेद हो जसले संस्थाहरूलाई निर्देशन दिन्छ। " * 4 for _ in range(12))
    chunks = I.chunk_text([text], "directive")
    assert len(chunks) > 1 and all(c["section"] is None for c in chunks)
    assert all(len(c["text"]) <= 1250 for c in chunks)


def test_act_style_sections_with_danda_numbers():
    chunks = I.chunk_text([ACT], "act")
    assert [c["section"] for c in chunks if c["section"] != "प्रस्तावना"] == ["1", "2", "3"]


def test_table_of_contents_pages_are_dropped():
    assert I.looks_toc(TOC)
    assert not I.looks_toc(ACT)
    assert I.chunk_text([TOC], "directive") == []


def test_script_detection():
    assert I.script_of(ENGLISH) == "en" and I.script_of(ACT) == "ne"


# --- entries / schema -------------------------------------------------------
def test_nepali_directive_entries_match_schema():
    es, st = I.build_entries(REC, _ex(DIRECTIVE), set(), set())
    assert len(es) == 5 and st["dup"] == 0
    e = es[1]
    for k in REQUIRED:
        assert k in e, k
    assert e["id"] == f"reg-nrb-{'ab' * 5}-1"
    assert e["category"] == "law" and e["doc_type"] == "directive"
    assert e["authority"] == "Nepal Rastra Bank" and e["topic"] == "Nepal Rastra Bank circular"
    assert e["text_ne"] and e["text_en"] == ""
    assert e["section"] == "2"
    assert e["source_ne"].endswith("इ.प्रा.निर्देशन नं. १/०८२, बुँदा 2")
    assert e["source_en"].startswith("Nepal Rastra Bank: ") and e["source_en"].endswith("Clause 2")
    assert e["url"] == "https://www.nrb.org.np/bfr/example/#page=1"
    assert e["published"] == "August 27, 2026" and e["fetched_at"] == "2026-09-29T10:00:00Z"
    assert e["provision_id"] == f"{'ab' * 5}:2"
    json.dumps(e, ensure_ascii=False)  # serialisable


def test_status_is_never_guessed():
    # circular dated in the current fiscal year (2083/84) -> in_force
    assert I.build_entries(REC, _ex(DIRECTIVE), set(), set())[1]["status"] == "in_force"
    # last fiscal year's circular, and an undated act: unknown
    old = {**REC, "published": "March 17, 2026", "sha256": "cd" * 32}
    assert I.build_entries(old, _ex(DIRECTIVE), set(), set())[1]["status"] == "unknown"
    act = {**REC, "kind": "act", "doc_type": "act", "published": "", "title": "बैंकिङ्ग कसूर तथा सजाय ऐन, २०६४", "sha256": "ef" * 32}
    assert I.build_entries(act, _ex(ACT), set(), set())[1]["status"] == "unknown"


def test_english_documents_use_english_fields():
    rec = {**REC, "authority": "ird", "kind": "directive", "title": "AML-CFT Guidance to DPMS", "published": "१७ भदौ, २०८३",
           "sha256": "12" * 32}
    es, st = I.build_entries(rec, _ex(ENGLISH, dev=0.0), set(), set())
    assert st["lang"] == "en" and es
    e = es[0]
    assert e["text_en"] and e["text_ne"] == ""
    assert e["doc_title_en"] == "AML-CFT Guidance to DPMS" and e["title_en"]
    assert e["id"].startswith("reg-ird-")
    assert e["status"] == "in_force"  # BS date 2083-05-17 is inside FY 2083/84


def test_exact_duplicates_of_existing_text_are_dropped():
    from app.retrieval import _text_key

    first, _ = I.build_entries(REC, _ex(DIRECTIVE), set(), set())
    existing = {_text_key(first[0])}
    again, st = I.build_entries({**REC, "sha256": "99" * 32}, _ex(DIRECTIVE), existing, set())
    assert st["dup"] == 1 and len(again) == len(first) - 1


# --- manifest / digest ------------------------------------------------------
def _write_corpus(tmp_path, monkeypatch):
    part = [{"id": "law-x-0"}, {"id": "law-x-1"}]
    with gzip.open(tmp_path / "part-000.jsonl.gz", "wt", encoding="utf-8") as f:
        f.writelines(json.dumps(e) + "\n" for e in part)
    (tmp_path / "manifest.json").write_text(json.dumps({
        "built_at": "x", "counts": {"curated": 0, "law_chunks": 2, "precedents": 0, "total": 2, "law_documents": 1},
        "files": ["part-000.jsonl.gz"], "digest": "old"}))
    monkeypatch.setattr(I, "CORPUS_DIR", str(tmp_path))


def test_manifest_update_appends_shard_and_recomputes_digest_like_build_corpus(tmp_path, monkeypatch):
    _write_corpus(tmp_path, monkeypatch)
    es, _ = I.build_entries(REC, _ex(DIRECTIVE), set(), set())
    m = I.update_manifest(es)
    ids = ["law-x-0", "law-x-1"] + [e["id"] for e in es]
    assert m["files"] == ["part-000.jsonl.gz", "part-002.jsonl.gz"]
    assert m["digest"] == hashlib.sha256("".join(ids).encode()).hexdigest()[:16]  # build_corpus.main()'s formula
    assert m["counts"]["total"] == 2 + len(es) and m["counts"]["regulator_chunks"] == len(es)
    # idempotent: a second run replaces, not doubles
    m2 = I.update_manifest(es)
    assert m2["files"].count("part-002.jsonl.gz") == 1 and m2["counts"]["total"] == m["counts"]["total"]


def test_shard_roundtrip(tmp_path, monkeypatch):
    _write_corpus(tmp_path, monkeypatch)
    es, _ = I.build_entries(REC, _ex(DIRECTIVE), set(), set())
    size = I.write_shard(es)
    assert 0 < size < I.SHARD_MAX_BYTES
    back = [json.loads(l) for l in gzip.open(tmp_path / "part-002.jsonl.gz", "rt", encoding="utf-8")]
    assert back == es


# --- scraper helpers --------------------------------------------------------
def test_bs_dates_and_fiscal_year():
    assert S.bs_key("१३ असोज, २०८३") == (2083, 6, 13)
    assert S.fiscal_year_bs(S.bs_key("१३ असोज, २०८३")) == "2083/84"
    assert S.fiscal_year_bs(S.bs_key("२७ चैत, २०८२")) == "2082/83"
    assert S.bs_key("२०८२।१२।३०") == (2082, 12, 30)


def test_newest_per_series_keeps_latest_amendment():
    docs = [
        {"title": "आयकर नियमावली, २०५९ (सोह्रौं संशोधन सहित)", "published": "१८ पुष, २०८२"},
        {"title": "आयकर नियमावली, २०५९ (पन्ध्रौं संशोधन २०८१)", "published": "१ पुष, २०८१"},
        {"title": "अन्तःशुल्क नियमावली, २०५९", "published": "१८ पुष, २०८२"},
    ]
    kept = S.newest_per_series(docs)
    assert [d["title"] for d in kept] == [docs[0]["title"], docs[2]["title"]]


def test_noise_titles_are_filtered():
    assert S.NOISE_TITLE.search("ललितपुर जिल्ला अदालतबाट जारी भएको डाँक लिलामी सूचना")
    assert S.NOISE_TITLE.search("मसलन्द तथा कार्यालय सामाग्री खरिद सम्बन्धी बोलपत्र आव्हानको सूचना")
    assert not S.NOISE_TITLE.search("आयकर निर्देशिका, २०६६")
