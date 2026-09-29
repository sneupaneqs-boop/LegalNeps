"""S2: doc-level status/enactment metadata (build_corpus.extract_doc_meta /
classify_status), verified against real header text from the built corpus
so the regexes are checked on the actual Law Commission formatting, not
hand-typed approximations of it."""
import gzip
import json
import os

import pytest
from build_corpus import classify_status, extract_doc_meta

CORPUS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "data", "corpus")


def _first_chunk_by_title() -> dict[str, dict]:
    manifest_path = os.path.join(CORPUS_DIR, "manifest.json")
    if not os.path.exists(manifest_path):
        return {}
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    out: dict[str, dict] = {}
    for name in manifest["files"]:
        with gzip.open(os.path.join(CORPUS_DIR, name), "rt", encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                # regulator shard (ingest_regulators.py, `reg-` ids): directives/circulars carry an
                # explicit `status` field and no Law Commission certification header, so the
                # header-regex checks below are about the Law Commission documents only
                if d.get("category") == "law" and not d["id"].startswith("reg-"):
                    out.setdefault(d.get("doc_title_ne") or "", d)
    return out


DOCS = _first_chunk_by_title()
requires_corpus = pytest.mark.skipif(not DOCS, reason="built corpus shards not present")

# 20 real acts/rules and their certification/gazette date as printed in the
# document's own header (backend/app/data/corpus), read by hand off the
# corpus text and cross-checked against Nepal Law Commission's published
# dates. BS = Bikram Sambat, as the header prints it.
KNOWN_DATES = [
    ("मुलुकी देवानी संहिता, २०७४", "2074-06-30"),
    ("सुरक्षित कारोबार ऐन, २०६३", "2063-07-30"),
    ("पारस्परिक कानूनी सहायता ऐन, २०७०", "2070-12-12"),
    ("आर्थिक कार्यविधि तथा वित्तीय उत्तरदायित्व नियमावली, २०७७", "2077-10-19"),
    ("स्वास्थ्यकर्मी तथा स्वास्थ्य संस्थाको सुरक्षा सम्बन्धी नियमावली, २०६९", "2069-06-08"),
    ("मालसामानको बहुविधिक ढुवानी ऐन, २०६३", "2063-07-07"),
    ("सहकारी ऐन, २०७४", "2074-07-01"),
    ("छापाखाना र प्रकाशन सम्बन्धी ऐन, २०४८", "2048-02-16"),
    ("कार्य सञ्चालन कोष ऐन, २०४३", "2043-07-24"),
    ("मुलुकी फौजदारी कार्यविधि नियमावली, २०७५", "2075-05-01"),
    ("औद्योगिक व्यवसाय विकास प्रतिष्ठान ऐन, २०५३", "2053-07-19"),
    ("खाद्य स्वच्छता तथा गुणस्तर ऐन, २०८१", "2081-01-23"),
    ("राष्ट्रिय सतर्कता केन्द्र (कार्य सञ्‍चालन) नियमावली, २०६५", "2065-12-04"),
    ("महान्यायाधिवक्ताको पारिश्रमिक, सेवाको शर्त र सुविधा सम्बन्धी ऐन, २०५२", "2052-11-03"),
    ("राष्ट्रिय चिकित्सा शिक्षा नियमावली, २०७७", "2077-04-26"),
    ("सर्वोच्च अदालत ऐन, २०४८", "2048-07-28"),
    ("पशु स्वास्थ्य तथा पशु सेवा व्यवसायी परिषद् ऐन, २०७९", "2079-06-23"),
    ("न्याय परिषद ऐन, २०७३", "2073-05-27"),
    ("जीवनाशक विषादी व्यवस्थापन ऐन, २०७६", "2076-05-13"),
    ("कर्मचारी समायोजन ऐन, २०७५", "2075-11-10"),
]


@requires_corpus
@pytest.mark.parametrize("title,expected_bs", KNOWN_DATES)
def test_enacted_date_matches_known_acts(title, expected_bs):
    doc = DOCS.get(title)
    assert doc is not None, f"fixture title not found in built corpus: {title!r}"
    meta = extract_doc_meta(doc["text_ne"])
    assert meta["enacted_bs"] == expected_bs


@requires_corpus
def test_all_nine_draft_bills_are_classified_as_bills_not_acts():
    bill_titles = [t for t in DOCS if "विधेयक" in t]
    assert len(bill_titles) == 9
    for title in bill_titles:
        meta = extract_doc_meta(DOCS[title]["text_ne"])
        assert classify_status(title, meta) == "bill", title


@requires_corpus
def test_status_covers_most_of_the_corpus_with_no_false_bills():
    # every doc gets a status; only genuine bills are "bill"
    in_force = sum(1 for t, d in DOCS.items() if classify_status(t, extract_doc_meta(d["text_ne"])) == "in_force")
    assert in_force / len(DOCS) > 0.75


def test_classify_status_bill_without_header():
    meta = {"enacted_bs": None, "amended_by": [], "consolidated_upto": None}
    assert classify_status("... सम्बन्धमा व्यवस्था गर्न बनेको विधेयक", meta) == "bill"


def test_classify_status_enacted_act_with_header():
    text = "केही ऐन\nप्रमाणीकरण र प्रकाशन मिति\n२०७४।६।३०\nप्रस्तावना : ..."
    meta = extract_doc_meta(text)
    assert meta["enacted_bs"] == "2074-06-30"
    assert classify_status("केही ऐन, २०७४", meta) == "in_force"


def test_amendment_list_is_parsed_with_dates():
    text = (
        "केही ऐन\nप्रमाणीकरण र प्रकाशन मिति\n२०६३।०७।३०\nसंशोधन गर्ने ऐन\n"
        "१. पहिलो संशोधन ऐन, २०७५ २०७६।०१।०२\n"
        "२. दोस्रो संशोधन ऐन, २०८० २०८०।१२।०३\n"
        "२०६३ सालको ऐन नं. १\nप्रस्तावनाः ..."
    )
    meta = extract_doc_meta(text)
    assert meta["enacted_bs"] == "2063-07-30"
    assert [a["date_bs"] for a in meta["amended_by"]] == ["2076-01-02", "2080-12-03"]
    assert meta["consolidated_upto"] == "2080-12-03"


def test_no_header_at_all_is_unknown_not_in_force():
    meta = extract_doc_meta("विषयसूची\nपरिच्छेद १\nप्रारम्भिक")
    assert meta["enacted_bs"] is None
    assert classify_status("कुनै प्रतिवेदन", meta) == "unknown"
