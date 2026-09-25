from extract_laws import _join_zwnj_breaks, chunk_document, drop_redraw_passes

ACT = """मुलुकी देवानी संहिता, २०७४
प्रस्तावना: नागरिक कानूनलाई संशोधन र एकीकरण गर्न वाञ्छनीय भएकोले,

१. संक्षिप्त नाम र प्रारम्भ : (१) यस ऐनको नाम "मुलुकी देवानी संहिता, २०७४" रहेको छ।
(२) यो संहिता तुरुन्त प्रारम्भ हुनेछ।

२. परिभाषा : विषय वा प्रसङ्गले अर्को अर्थ नलागेमा यस संहितामा,
(क) "अदालत" भन्नाले जिल्ला अदालत सम्झनु पर्छ।

३. संहिताको अधीनमा रहने : नेपाल सरकारले यस संहिताको अधीनमा रही नियम बनाउन सक्नेछ।
"""


def test_legislation_is_split_on_section_headings():
    chunks = chunk_document([ACT], is_legislation=True)
    sections = [c["section"] for c in chunks if c["section"] != "प्रस्तावना"]
    assert sections == ["1", "2", "3"]
    heads = {c["section"]: c["heading"] for c in chunks}
    assert heads["1"] == "संक्षिप्त नाम र प्रारम्भ"
    assert heads["3"] == "संहिताको अधीनमा रहने"
    assert chunks[0]["section"] == "प्रस्तावना"


def test_long_sections_are_windowed_not_truncated():
    long_body = "१. लामो दफा : " + ("यो वाक्य हो। " * 400) + "\n\n२. अर्को : छोटो।\n\n३. तेस्रो : छोटो।"
    chunks = chunk_document([long_body], is_legislation=True)
    first = [c for c in chunks if c["section"].startswith("1")]
    assert len(first) > 1 and all(len(c["text"]) <= 2200 for c in first)


def test_non_legislation_uses_paragraph_windows_with_pages():
    pages = ["पहिलो अनुच्छेद। " * 50, "दोस्रो पृष्ठ। " * 50]
    chunks = chunk_document(pages, is_legislation=False)
    assert chunks and all(c["section"] is None for c in chunks)
    assert chunks[-1]["page"] == 2


def test_zwnj_breaks_rejoined_but_real_final_halant_kept():
    assert _join_zwnj_breaks("हेजिङ् ग नियमावली") == "हेजिङ्ग नियमावली"
    assert _join_zwnj_breaks("संघीय संसद् सचिवालय") == "संघीय संसद् सचिवालय"
    assert _join_zwnj_breaks("संवत् २०७४") == "संवत् २०७४"


def test_simulated_bold_redraw_passes_are_dropped():
    def ch(c, x, y=100.0):
        return (ord(c), 1, (x, y), (x, y - 8, x + 5, y))
    one_pass = [ch("a", 10), ch("b", 15), ch("c", 20)]
    redraw = one_pass + [ch("a", 10.3), ch("b", 15.3), ch("c", 20.3)]
    assert [c[0] for c in drop_redraw_passes(redraw, 10)] == [ord("a"), ord("b"), ord("c")]
    two_lines = one_pass + [ch("d", 10, 120), ch("e", 15, 120)]
    assert len(drop_redraw_passes(two_lines, 10)) == 5
