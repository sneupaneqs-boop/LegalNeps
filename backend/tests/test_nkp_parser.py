from scrape_nkp import parse

HTML = """<html><body>
<h1 class="post-title"><a>निर्णय नं. ११५१६ - सम्पत्ति शुद्धीकरण</a></h1>
<div id="decision_summary">भाग: ६७ साल: २०८२ महिना: चैत्र अंक: १२</div>
<div id="faisala_detail ">
<p>सर्वोच्च अदालत, संयुक्त इजलास</p>
<p>माननीय न्यायाधीश श्री हरिप्रसाद फुयाल</p>
<p>फैसला मिति : २०८०।११।०२</p>
<p>मुद्दाः सम्पत्ति शुद्धीकरण</p>
<p>पुनरावेदक / प्रतिवादी : क</p>
<p>विरूद्ध</p>
<p>प्रत्यर्थी / वादी : विभागको तर्फबाट अनुसन्धान अधिकृत</p>
<p>सम्पत्ति शुद्धीकरणको कसुर हुनका लागि सम्बद्ध कसुर हुनुपर्ने ।</p>
<p>(प्रकरण नं.२)</p>
<p>पुनरावेदक / प्रतिवादीका तर्फबाट :</p>
<p>अवलम्बित नजिर :</p>
<p>ने.का.प.२०७२, अङ्क ५, नि.नं.९४०६</p>
<p>सम्बद्ध कानून :</p>
<p>सम्पत्ति शुद्धीकरण (मनी लाउन्डरिङ) निवारण ऐन, २०६४</p>
<p>फैसला</p>
<p>... यो सजाय ठहर्छ ।</p>
</div></body></html>"""


def test_parse_extracts_headnote_and_metadata():
    rec = parse(HTML, 10612)
    assert rec["decision_no"] == "११५१६"
    assert rec["subject"] == "सम्पत्ति शुद्धीकरण"
    assert rec["year"] == "२०८२" and rec["issue"] == "१२"
    assert rec["headnote"].startswith("सम्पत्ति शुद्धीकरणको कसुर")
    assert "प्रकरण नं.२" in rec["headnote"]
    # the party line mentioning "तर्फबाट" must not end the headnote early
    assert "अनुसन्धान अधिकृत" not in rec["headnote"]
    assert rec["related_laws"] == ["सम्पत्ति शुद्धीकरण (मनी लाउन्डरिङ) निवारण ऐन, २०६४"]
    assert rec["cited_precedents"] == ["ने.का.प.२०७२, अङ्क ५, नि.नं.९४०६"]
    assert "ठहर्छ" in rec["conclusion"]


def test_parse_returns_none_for_non_decision_pages():
    assert parse("<html><body><h1>404</h1></body></html>", 1) is None
