"""OCR cleaning + quality-gate tests (ocr_clean.py, ocr_regulators.py helpers).
Pure functions: no tesseract, no PDFs, no corpus."""
import gzip
import hashlib
import json

import ingest_regulators as I
import ocr_clean as C
from app.text_norm import fold

NE = {fold(w) for w in "धितोपत्र बोर्डले संगठित संस्थाले कम्पनी दर्ता गर्नु पर्नेछ निर्देशन जारी गरेको सम्बन्धमा सूचना लगानी कर्ता".split()}
EN = {"the", "board", "shall", "issue", "directive", "securities", "and", "listed", "companies"}


# --- clean_page ---------------------------------------------------------------
def test_page_numbers_and_noise_lines_are_dropped():
    raw = "धितोपत्र बोर्डले निर्देशन जारी गरेको छ ।\n\n- 3 -\n७\nPage 4 of 12\n~~ __ ..\n|\nअर्को अनुच्छेद ।"
    out = C.clean_page(raw)
    assert out == "धितोपत्र बोर्डले निर्देशन जारी गरेको छ ।\n\nअर्को अनुच्छेद ।"


def test_stray_symbols_and_control_chars_removed():
    out = C.clean_page("कम्पनी\x0c दर्ता ¢ गर्नु ■ पर्नेछ� ।")
    assert out == "कम्पनी दर्ता गर्नु पर्नेछ ।"


def test_broken_matras_repaired():
    assert C.clean_page("संस्थााले गरेकोो") == "संस्थाले गरेको"      # repeated signs collapse
    assert C.clean_page("धितोपत्र ाानिर्देशन") == "धितोपत्र निर्देशन"  # orphan sign at word start
    assert C.clean_page("अाज अोटा") == "आज ओटा"                      # split independent vowels
    assert C.clean_page("गर्नु ््् पर्नेछ") == "गर्नु पर्नेछ"          # halant run + lone halants


def test_valid_nasal_marks_survive():
    assert C.clean_page("संस्थाहरूमा हुँदै भएकाः") == "संस्थाहरूमा हुँदै भएकाः"


def test_bar_read_as_danda():
    assert C.clean_page("जारी गरिएको छ |") == "जारी गरिएको छ ।"
    assert C.clean_page("Rule | Description") == "Rule | Description"  # a table bar between English words is kept


def test_clean_page_idempotent():
    raw = "सूचना\n\n३\nधितोपत्र बोर्डले ािनर्देशन जारी गरेको छ |\nPage 2"
    once = C.clean_page(raw)
    assert C.clean_page(once) == once


# --- running headers -----------------------------------------------------------
def test_running_headers_and_footers_stripped():
    pages = [f"नेपाल धितोपत्र बोर्ड\nसाल्ना बैठक {i}\nमुख्य पाठ नम्बर {'क' * i} यहाँ छ ।\nगोप्य दस्तावेज पृष्ठ {i}" for i in range(1, 6)]
    out = C.strip_running_headers(pages)
    assert all("नेपाल धितोपत्र बोर्ड" not in p and "गोप्य दस्तावेज" not in p for p in out)
    assert all("मुख्य पाठ" in p for p in out)


def test_header_stripping_leaves_short_documents_and_unique_lines_alone():
    pages = ["नेपाल धितोपत्र बोर्ड\nपाठ एक", "नेपाल धितोपत्र बोर्ड\nपाठ दुई"]
    assert C.strip_running_headers(pages) == pages
    many = [f"शीर्षक {chr(0x0915 + i)}{chr(0x0915 + i)}{chr(0x0915 + i)}\nपाठ" for i in range(6)]
    assert C.strip_running_headers(many) == many


# --- digits ------------------------------------------------------------------
def test_digits_devanagari_in_nepali_ascii_in_english():
    assert C.normalise_digits("दफा 12 को उपदफा (3) बमोजिम") == "दफा १२ को उपदफा (३) बमोजिम"
    assert C.normalise_digits("Section ५ of the Act, 2063") == "Section 5 of the Act, 2063"
    assert C.normalise_digits("मिति २०८३/05/09") == "मिति २०८३/०५/०९"


def test_digits_glued_to_latin_letters_kept():
    assert C.normalise_digits("कोभिड COVID-19 सम्बन्धमा CAMIS2 प्रणाली") == "कोभिड COVID-19 सम्बन्धमा CAMIS2 प्रणाली"


# --- quality gate --------------------------------------------------------------
GOOD = "धितोपत्र बोर्डले सूचना जारी गरेको छ । संगठित संस्थाले कम्पनी दर्ता गर्नु पर्नेछ । लगानी कर्ता सम्बन्धमा निर्देशन जारी गरेको ।"
GARBAGE = "ककखग घघङच छजझञ टठडढ णतथद धनपफ बभमय रलवश षसहक ककखग घघङच छजझञ टठडढ णतथद धनपफ बभमय रलवश"


def test_token_stats_counts_both_scripts():
    st = C.token_stats(GOOD + " The Board shall issue directive xqzv", NE, EN)
    assert st["ne_words"] > 10 and st["ne_valid"] >= 9
    assert st["en_words"] == 6 and st["en_valid"] == 5
    assert 0.6 < st["rate"] < 1


def test_token_stats_variant_spellings_count_as_valid():
    st = C.token_stats("सम्वन्धमा सुचना कम्पनि दर्ता गर्नु", NE, EN)  # ब/व, ी/ि variants fold together
    assert st["ne_valid"] >= 3


def test_structural_share_flags_broken_words():
    assert C.structural_share(GOOD) == 1.0
    broken = " ".join(["ािधितो", "गरेकोो", "ुसंस्था", "क्ा्", "ांबोर्ड", "संस्थाले", "गर्नु", "पर्नेछ", "बोर्डले", "सूचना"])
    assert C.structural_share(broken) < 0.6
    assert C.structural_share("थोरै शब्द") is None


def test_page_verdict_keeps_good_drops_garbage_and_short():
    assert C.page_verdict(GOOD, NE, EN)[:2] == (True, "ok")
    ok, why, _ = C.page_verdict(GARBAGE, NE, EN)
    assert not ok and why.startswith("garbled")
    ok, why, _ = C.page_verdict("सूचना जारी", NE, EN)
    assert not ok and why == "too_short"


def test_page_verdict_drops_broken_matras_even_with_valid_share():
    broken = GOOD + " " + " ".join(["ािक", "ुख", "ांग", "ीघ", "ूज"] * 4)
    ok, why, _ = C.page_verdict(broken, NE, EN, min_rate=0.3)
    assert not ok and why.startswith("broken matras")


def test_document_verdict_drops_mostly_garbage_documents():
    v = C.document_verdict([GOOD, GARBAGE, GARBAGE], NE, EN)
    assert not v["keep"] and "readable pages" in v["reason"]
    assert [p for p, _ in v["dropped_pages"]] == [2, 3]
    v = C.document_verdict([GOOD, GOOD, GARBAGE], NE, EN)
    assert v["keep"] and v["pages"][2] == "" and v["pages"][0] == GOOD and v["kept_share"] > 0.6
    v = C.document_verdict(["", ""], NE, EN)
    assert not v["keep"] and v["reason"] == "no readable page"


def test_clean_document_end_to_end():
    pages = [f"नेपाल धितोपत्र बोर्ड\n{GOOD} दफा {i} {'ख' * (i + 1)}\n{i}" for i in range(1, 6)]
    out = C.clean_document(pages)
    assert all("नेपाल धितोपत्र बोर्ड" not in p for p in out)
    assert out[0].endswith("दफा १ खख")


# --- manifest handling for a second shard (part-003) --------------------------
def _seed(tmp_path, monkeypatch):
    for name, ids in (("part-000.jsonl.gz", ["a-0", "a-1"]), ("part-002.jsonl.gz", ["reg-x-0"])):
        with gzip.open(tmp_path / name, "wt", encoding="utf-8") as f:
            f.writelines(json.dumps({"id": i}) + "\n" for i in ids)
    (tmp_path / "manifest.json").write_text(json.dumps({
        "built_at": "x", "counts": {"total": 3, "regulator_chunks": 1, "regulator_documents": 1},
        "files": ["part-000.jsonl.gz", "part-002.jsonl.gz"], "digest": "old"}))
    monkeypatch.setattr(I, "CORPUS_DIR", str(tmp_path))


def test_second_shard_registered_last_with_own_counters(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    es = [{"id": "reg-sebon-z-0", "doc_id": "z"}, {"id": "reg-sebon-z-1", "doc_id": "z"}]
    m = I.update_manifest(es, shard="part-003.jsonl.gz", count_keys=("ocr_chunks", "ocr_documents"))
    assert m["files"] == ["part-000.jsonl.gz", "part-002.jsonl.gz", "part-003.jsonl.gz"]
    assert m["digest"] == hashlib.sha256("a-0a-1reg-x-0reg-sebon-z-0reg-sebon-z-1".encode()).hexdigest()[:16]
    c = m["counts"]
    assert c["total"] == 5 and c["ocr_chunks"] == 2 and c["ocr_documents"] == 1 and c["regulator_chunks"] == 1
    m2 = I.update_manifest(es, shard="part-003.jsonl.gz", count_keys=("ocr_chunks", "ocr_documents"))  # idempotent
    assert m2["counts"]["total"] == 5 and m2["files"].count("part-003.jsonl.gz") == 1


def test_part002_rebuild_keeps_part003_after_it_in_the_digest(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    es3 = [{"id": "reg-sebon-z-0", "doc_id": "z"}]
    with gzip.open(tmp_path / "part-003.jsonl.gz", "wt", encoding="utf-8") as f:
        f.writelines(json.dumps(e) + "\n" for e in es3)
    I.update_manifest(es3, shard="part-003.jsonl.gz", count_keys=("ocr_chunks", "ocr_documents"))
    new2 = [{"id": "reg-x-0", "doc_id": "x"}, {"id": "reg-x-1", "doc_id": "x"}]
    m = I.update_manifest(new2)  # rebuilding part-002 must not move part-003 in front of it
    assert m["files"] == ["part-000.jsonl.gz", "part-002.jsonl.gz", "part-003.jsonl.gz"]
    assert m["digest"] == hashlib.sha256("a-0a-1reg-x-0reg-x-1reg-sebon-z-0".encode()).hexdigest()[:16]
    assert m["counts"]["total"] == 2 + 2 + 1


# --- Latin noise from stamps/seals ---------------------------------------------
def test_latin_noise_dropped_only_inside_nepali_lines():
    en = {"online", "the", "board"}
    line = "विशेष दर्ता खारेजी wear (दफा १३६क) सम्बन्धी geet सूचना"
    assert C.drop_latin_noise(line, en) == "विशेष दर्ता खारेजी (दफा १३६क) सम्बन्धी सूचना"
    # capitalised words, acronyms, known words and URLs stay; English lines are untouched
    keep = "कम्पनी CAMIS मार्फत online Dashboard हेर्नुहोस् https://camis.ocr.gov.np"
    assert C.drop_latin_noise(keep, en) == keep
    assert C.drop_latin_noise("xqz wear geet only english here", en) == "xqz wear geet only english here"
    assert C.clean_document(["कम्पनी poe दर्ता ere गर्नु"], en) == ["कम्पनी दर्ता गर्नु"]


# --- edition handling helpers (ocr_regulators) ---------------------------------
def test_title_year_puts_bs_and_ad_on_one_scale():
    import ocr_regulators as O

    assert O.title_year("Directive, 2026") > O.title_year("Directive, 2025 (2082)") > O.title_year("Directive, 2024 (2081)")
    assert O.title_year("बीमा नियमावली, २०८१") == 2024
    assert O.title_year("Insurance Act, 1992 (Nepali)") == 1992
    assert O.title_year("no year here") == 0


def test_series_key_ignores_edition_and_language_words():
    import ocr_regulators as O

    assert O.series_key("Insurance Act with Second Amendment, 2079 (Nepali)") == O.series_key("Insurance Act, 1992")
    assert O.series_key("Insurance Regulations 1969 with Amendments") == O.series_key("Insurance Regulation, 2081")
    assert O.series_key("Financial Bylaw-Registered, 2079") == O.series_key("Financial Bylaw, 2079")
    assert O.series_key("Insurance Act, 2079") != O.series_key("Insurance Regulation, 2081")


def test_nia_rows_parse_the_law_tables():
    import scrape_regulators as S2

    html = ('<div>sidebar <a href="http://nia.gov.np/uploads/notice/1.pdf">notice</a></div>'
            '<table class="table table-main"><tbody>'
            '<tr><td><span class="text-primary-main">Insurance Regulation, 2081</span></td><td> 10 Mar 2025 </td>'
            '<td><a href="http://nia.gov.np/Admin/images/Law/InsuranceRegulation/a.pdf">Download PDF</a></td></tr>'
            '<tr><td> रसुवा बाढी दाबी कार्यविधि, २०८३ </td><td>30 Sep 2026</td>'
            '<td><a href="http://nia.gov.np/Admin/images/Law/Directive/b.pdf">PDF</a></td></tr>'
            '<tr><td>no file</td><td>1 Jan 2020</td><td></td></tr></tbody></table>')
    rows = list(S2.nia_rows(html))
    assert [(r["title"], r["published"], r["url"].rsplit("/", 1)[1]) for r in rows] == [
        ("Insurance Regulation, 2081", "2025-03-10", "a.pdf"), ("रसुवा बाढी दाबी कार्यविधि, २०८३", "2026-09-30", "b.pdf")]
    assert list(S2.nia_rows("<html>no table</html>")) == []


def test_scanned_figure_tables_are_flagged_prose_is_not():
    table = "\n".join("४४०१.३१.०० ४४०१.३२.०० । ४४०१.२९.०० ४४०२.१०.०० ४४०२.२०.००" for _ in range(4))
    assert C.is_table_noise(table)
    assert not C.is_table_noise(GOOD * 3)
    rates = "आयकर दर १० % २० % ३० % ३६ % ३९ % वार्षिक आय रु ५,००,००० सम्म १ % सामाजिक सुरक्षा कर लाग्ने छ ।" * 2
    assert not C.is_table_noise(rates)
    assert not C.is_table_noise("१२ ३४")  # too short to judge
