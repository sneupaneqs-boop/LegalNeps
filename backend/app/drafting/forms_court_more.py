"""More court forms: the reply, appeal and power-of-attorney (वारिसनामा) of the
Civil Procedure Code schedules, the petition forms of the District Court and
High Court Rules, the mediation petitions of the Mediation Rules, plus
standard-format (non-schedule) court papers: settlement deed, Supreme Court
writ, divorce and partition plaints.

`official()` templates are read against the official PDF page named in
`source.url`; `standard()` ones say so in their `source.note`.
"""
from __future__ import annotations

from .dsl import F, SELECT
from .forms_common import (
    CASE_TITLE, CDPC, DATE, DC_RULES, EVIDENCE, FEE_ITEMS, FEES, HC_RULES, LAWYERS, MEDIATION_RULES, REG_DATE, REG_NO,
    SC_RULES, WITNESSES, court_field, court_line, more_parties_field, numbered_items, official, pair_items,
    party_fields, party_line, standard,
)

CIVIL = "court"

_SIGN_IN = "@r,+ ………………………"

# --------------------------------------------------------------------------
# प्रतिउत्तरपत्र - अनुसूची–९ (दफा १२०)
# --------------------------------------------------------------------------

REPLY = official(
    id="written_reply_civil",
    title_en="Written reply (civil suit) - प्रतिउत्तरपत्र",
    title_ne="प्रतिउत्तरपत्र (देवानी मुद्दा)",
    desc_en="The defendant's written reply to a plaint, in the exact form of Schedule 9 of the Civil Procedure Code.",
    desc_ne="मुलुकी देवानी कार्यविधि संहिताको अनुसूची–९ बमोजिम प्रतिबादीले फिरादपत्रमा दिने प्रतिउत्तरपत्रको ढाँचा।",
    category=CIVIL,
    law=CDPC, law_en="Muluki Civil Procedure Code, 2074", schedule="अनुसूची–९", relates_to="दफा १२०",
    page=141, form_title="प्रतिउत्तरपत्रको ढाँचा",
    keywords=("reply", "defence", "written statement", "प्रतिउत्तर", "जवाफ", "प्रतिबादी", "civil case"),
    provisions=[{"law_title_ne": CDPC, "section": "120"}],
    fields=[
        court_field(), REG_NO, REG_DATE,
        F("case_year", "Case year (B.S.)", "मुद्दाको साल"), F("case_no", "Civil case no. (दे.दा.नं.)", "दे.दा.नं."),
        *party_fields("df", "Defendant", "प्रतिबादी"), more_parties_field("df_more", "defendant", "प्रतिबादी"),
        *party_fields("pl", "Plaintiff", "बादी"), more_parties_field("pl_more", "plaintiff", "बादी"),
        CASE_TITLE,
        SELECT("served_by", "Summons received from", "म्याद प्राप्त गरेको माध्यम", ["बादी", "कानून व्यवसायी", "अदालत"]),
        F("summons_date", "Date summons received", "म्याद प्राप्त भएको मिति", "date"),
        F("facts", "Your version of the facts (one point per line)",
          "बादीले दाबी गरेका विषयमा यथार्थ व्यहोरा (एक पङ्क्तिमा एक बुँदा)", "textarea", required=True),
        SELECT("admit", "Claim admitted?", "फिराद दाबी स्वीकार", ["पूर्ण रूपमा", "आंशिक रूपमा", "गर्दिनँ"]),
        F("counterclaims", "Counter-claims (one per line)", "प्रतिदाबी (एक पङ्क्तिमा एउटा)", "textarea"),
        F("objection", "Objection: no standing / limitation / jurisdiction (grounds)",
          "हकदैया नभएको / हदम्याद नभएको / क्षेत्राधिकार नभएको जिकिर (आधार र कारण)", "textarea"),
        F("decision_view", "Should the court decide as claimed?", "फिराद दाबी अनुसार अदालतबाट निर्णय हुनु पर्ने हो होइन"),
        LAWYERS, FEES, EVIDENCE, WITNESSES, DATE,
    ],
    body="""
@r अदालत/कार्यालयले भर्ने
@r दर्ता नं.: {{ reg_no|blank(8) }}
@r दर्ता मिति: {{ reg_date|bs|blank(8) }}
@cb,+ """ + court_line() + """
@cbu,+ प्रतिउत्तरपत्र
@c,+ {{ case_year|nd|blank(8) }} सालको दे.दा.नं. {{ case_no|nd|blank(8) }}
@c,+ """ + party_line("df", "प्रतिबादी") + """
@c,each=df_more:0 {{ item }} **प्रतिबादी**
@cbu,+ विरुद्ध
@c """ + party_line("pl", "बादी") + """
@c,each=pl_more:0 {{ item }} **बादी**
@cb,+ मुद्दा :- {{ case_title|blank(10) }}
@j,+ उल्लिखित विपक्षी भएको उक्त मुद्दामा यस अदालतबाट मेरा/हाम्रा नाममा जारी भएको म्याद {{ served_by|default('बादी/कानून व्यवसायी/अदालत', true) }}बाट मिति {{ summons_date|bs|blank(6) }} मा प्राप्त भएकोले सो फिराद दाबीका सम्बन्धमा देहायको व्यहोराको प्रतिउत्तरपत्र लिई उपस्थित भएको छु/छौँ ।
@j १.|बादीले दाबी गरेका विषयहरूका सम्बन्धमा मेरो/हाम्रो भएको यथार्थ व्यहोरा निम्न प्रकरणहरूमा खुलाएको छु/छौँ ।
""" + numbered_items("facts", 5) + """
@j २.|फिराददाबी {% if not admit %}पूर्ण रूपमा वा आंशिक रूपमा स्वीकार गर्दछु/गर्दछौँ । गर्दिनँ/गर्दैनौ ।{% elif admit == 'गर्दिनँ' %}स्वीकार गर्दिनँ/गर्दैनौँ ।{% else %}{{ admit }} स्वीकार गर्दछु/गर्दछौँ ।{% endif %}
@j ३.|प्रतिदाबी कुनै भए उल्लेख गर्नेः
""" + numbered_items("counterclaims", 3) + """
@j ४.|फिराद दर्ता गर्ने हकदैया नभएको/नालेस गर्ने हदम्याद नभएको/अदालतको क्षेत्राधिकार नभएको जिकिर लिएको भए सोको आधार र कारण{% if objection %} : {{ objection }}{% endif %} ।
@j ५.|फिराद दाबी अनुसार अदालतबाट निर्णय हुनु पर्ने हो होइन{% if decision_view %} : {{ decision_view }}{% endif %} ।
@l ६.|कानून व्यवसायी नियुक्त गरेको भए सोको विवरणः
""" + pair_items("lawyers", 3, "नाम", "प्रमाणपत्र नं", gap=10) + """
@l ७.|देहायको दस्तुर यसैसाथ बुझाउन ल्याएको छु/छौँ ।
""" + FEE_ITEMS + """
@l ८.|प्रमाणः यस विषयमा देहायको प्रमाण सम्बन्धी कागजातको प्रतिलिपि संलग्न गरेको छु/छौँ ।
""" + numbered_items("evidence", 3) + """
@l ९.|साक्षी :–
""" + numbered_items("witnesses", 3) + """
@l १०.|यसमा लेखिएको व्यहोरा ठीक साँचो छ, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
""" + _SIGN_IN + """
@ru प्रतिउत्तरपत्रवालाको दस्तखत र सङ्गठित संस्था भए संस्थाको छाप
@l,>1.5,+ {{ signoff(doc_date) }}
@ji,+ द्रष्टव्य : सङ्गठित संस्थाको तर्फबाट प्रतिउत्तरपत्र दिँदा त्यस्तो संस्थाको नाम तथा ठेगाना र त्यस्तो संस्थाको तर्फबाट प्रतिउत्तरपत्र दिन अधिकार पाएको व्यक्तिको नाम थर र पद उल्लेख गर्नु पर्नेछ ।
""",
)

# --------------------------------------------------------------------------
# पुनरावेदनपत्र - अनुसूची–२१ (दफा २०८ को उपदफा (१))
# --------------------------------------------------------------------------

APPEAL = official(
    id="appeal_civil",
    title_en="Appeal (civil case) - पुनरावेदनपत्र",
    title_ne="पुनरावेदनपत्र (देवानी मुद्दा)",
    desc_en="Appeal against a District Court judgment in a civil case, in the exact form of Schedule 21 of the Civil Procedure Code.",
    desc_ne="मुलुकी देवानी कार्यविधि संहिताको अनुसूची–२१ बमोजिम फैसलामा चित्त नबुझी दिने पुनरावेदनपत्रको ढाँचा।",
    category=CIVIL,
    law=CDPC, law_en="Muluki Civil Procedure Code, 2074", schedule="अनुसूची–२१", relates_to="दफा २०८ को उपदफा (१)",
    page=157, form_title="पुनरावेदनपत्रको ढाँचा",
    keywords=("appeal", "पुनरावेदन", "फैसला", "high court", "उच्च अदालत", "civil"),
    provisions=[{"law_title_ne": CDPC, "section": "208"}],
    fields=[
        F("court", "Court appealed to (full name)", "पुनरावेदन दायर गरेको अदालत (पूरा नाम)",
          help_en="e.g. Patan High Court", help_ne="जस्तै: पाटन उच्च अदालत"),
        REG_NO, REG_DATE,
        F("ap_name", "Appellant: full name", "पुनरावेदकको पूरा नाम", required=True),
        F("ap_addr", "Appellant: address", "पुनरावेदकको ठेगाना (बस्ने)"),
        F("ap_age", "Appellant: age", "पुनरावेदकको उमेर (वर्ष)", "number"),
        F("ap_more", "Additional appellants (one per line)", "थप पुनरावेदक (एक पङ्क्तिमा एक जना)", "textarea"),
        SELECT("ap_role", "Appellant was", "पुनरावेदक (बादी/प्रतिबादी)", ["बादी", "प्रतिबादी"]),
        F("rs_name", "Respondent: full name", "प्रत्यर्थीको पूरा नाम", required=True),
        F("rs_addr", "Respondent: address", "प्रत्यर्थीको ठेगाना (बस्ने)"),
        F("rs_age", "Respondent: age", "प्रत्यर्थीको उमेर (वर्ष)", "number"),
        F("rs_more", "Additional respondents (one per line)", "थप प्रत्यर्थी (एक पङ्क्तिमा एक जना)", "textarea"),
        SELECT("rs_role", "Respondent was", "प्रत्यर्थी (बादी/प्रतिबादी)", ["बादी", "प्रतिबादी"]),
        CASE_TITLE,
        F("judge_court", "Judge and court that decided", "फैसला गर्ने न्यायाधीश र अदालत/कार्यालय"),
        F("judgment_date", "Date of judgment", "फैसला भएको मिति", "date"),
        F("file_no", "Judgment file (मिसिल) no.", "फैसलाको मिसिल नं."),
        F("notice_date", "Date notice of judgment received", "फैसला भएको सूचना पाएको मिति", "date"),
        F("case_summary", "1. Brief of the case", "१. मुद्दाको संक्षिप्त विवरण", "textarea"),
        F("judgment_summary", "2. Brief of the judgment", "२. फैसलाको संक्षिप्त विवरण", "textarea"),
        F("judgment_basis", "3. Grounds taken in the judgment", "३. फैसला गर्दा लिएका आधार", "textarea"),
        F("appeal_reasons", "4. Reasons for appeal / refuting the grounds (one per line)",
          "४. पुनरावेदन गर्नु पर्ने कारण र फैसलाका आधार खण्डनको व्यहोरा (एक पङ्क्तिमा एक बुँदा)", "textarea", required=True),
        F("appeal_claim", "5. Appeal claim and legal grounds", "५. पुनरावेदन जिकिर र त्यसलाई पुष्ट्याई गर्ने कानूनी आधार", "textarea"),
        F("appeal_fee", "6. Court fee and other fees for the appeal", "६. पुनरावेदन गर्दा लाग्ने अदालती शुल्क र अन्य दस्तुर"),
        F("other_matters", "7. Other necessary matters (one per line)", "७. अन्य आवश्यक कुराहरू (एक पङ्क्तिमा एउटा)", "textarea"),
        F("sign_name", "Appellant's name (signature block)", "पुनरावेदकको नाम (दस्तखत)"),
        DATE,
    ],
    body="""
@r अदालत/कार्यालयले भर्ने
@r दर्ता नं.: {{ reg_no|blank(8) }}
@r दर्ता मिति: {{ reg_date|bs|blank(8) }}
@cb,+ {{ court|blank(12) }} दायर गरेको
@cbu पुनरावेदन पत्र
@c,+ {{ ap_addr|blank(8) }} बस्ने वर्ष {{ ap_age|nd|blank(3) }} को {{ ap_name|blank(8) }} __पुनरावेदक__
@c,each=ap_more:0 {{ item }} __पुनरावेदक__
@c {{ ap_role|default('बादी/प्रतिबादी', true) }}
@cb,+ विरुद्ध
@c,+ {{ rs_addr|blank(8) }} बस्ने वर्ष {{ rs_age|nd|blank(3) }} को {{ rs_name|blank(8) }} __प्रत्यर्थी__
@c,each=rs_more:0 {{ item }} __प्रत्यर्थी__
@c {{ rs_role|default('बादी/प्रतिबादी', true) }}
@cb,+ मुद्दा {{ case_title|blank(10) }}
@c,+ फैसला गर्ने न्यायाधीश र अदालत/ कार्यालय{% if judge_court %} : {{ judge_court }}{% endif %}
@c फैसला भएको मितिः {{ judgment_date|bs }}
@c फैसलाको मिसिल नं.ः {{ file_no|nd }}
@j,+ म/हामी पक्ष रहेको उपर्युक्त मुद्दामा देहायका कुरामा देहाय बमोजिम हुने गरी उपर्युक्त न्यायाधीश र अदालत/कार्यालयबाट फैसला भएकोमा सो फैसलामा चित्त नबुझी फैसला भएको सूचना {{ notice_date|bs|blank(6) }} (मिति उल्लेख गर्ने) मा पाएकोले देहायको पुनरावेदन गर्दछु/गर्दछौँ ।
@l १.|मुद्दाको संक्षिप्त विवरणः {{ case_summary }}
@l २.|फैसलाको संक्षिप्त विवरणः {{ judgment_summary }}
@l ३.|फैसला गर्दा लिएका आधारः {{ judgment_basis }}
@l ४.|पुनरावेदन गर्नु पर्ने कारण र फैसलाका आधार खण्डनको व्यहोराः
""" + numbered_items("appeal_reasons", 3) + """
@l ५.|पुनरावेदन जिकिर र त्यसलाई पुष्ट्याई गर्ने कानूनी आधारः {{ appeal_claim }}
@l ६.|पुनरावेदन गर्दा लाग्ने अदालती शुल्क र अन्य दस्तुरः {{ appeal_fee|nd }}
@l ७.|अन्य आवश्यक कुराहरू कुनै भए सो :
""" + numbered_items("other_matters", 3) + """
@l ८.|पुनरावेदन साथ संलग्न गर्नु पर्ने लिखतहरू:
@l,>1 (क)|फैसलाको प्रतिलिपि,
@l,>1 (ख)|अदालती दस्तुर तथा अन्य दस्तुर,
@l,>1 (ग)|कुनै प्रमाण भए सो प्रमाणको प्रतिलिपि ।
@l ९.|यसमा लेखिएको व्यहोरा ठीक साँचो छ, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
""" + _SIGN_IN + """
@r पुनरावेदकको दस्तखत र सङ्गठित संस्था भए संस्थाको छाप : {{ sign_name }}
@r मिति : {{ doc_date|bs }}
@ji,+ द्रष्टव्य : सङ्गठित संस्थाको तर्फबाट पुनरावेदनपत्र दिँदा त्यस्तो संस्थाको नाम तथा ठेगाना र त्यस्तो संस्थाको तर्फबाट पुनरावेदन गर्ने अधिकार पाएको व्यक्तिको नाम थर र पद उल्लेख गर्नु पर्नेछ ।
""",
)

# --------------------------------------------------------------------------
# वारिसनामा - अनुसूची–१३ (दफा १४६ को उपदफा (१))
# --------------------------------------------------------------------------

WARISNAMA = official(
    id="warisnama_court",
    title_en="Court power of attorney (Warisnama) - वारिसनामा",
    title_ne="वारिसनामा (अदालतमा मुद्दाको वारिस नियुक्त गर्ने)",
    desc_en="Appoints a person to act for you in a court case (Schedule 13 of the Civil Procedure Code), with the representative's acceptance, thumbprints and three witnesses.",
    desc_ne="अदालतमा मुद्दाको काम गर्न वारिस नियुक्त गर्ने अनुसूची–१३ बमोजिमको वारिसनामा, वारिसको मञ्जुरी, ल्याप्चे सहीछाप र तीन साक्षीसहित।",
    category=CIVIL,
    law=CDPC, law_en="Muluki Civil Procedure Code, 2074", schedule="अनुसूची–१३", relates_to="दफा १४६ को उपदफा (१)",
    page=147, form_title="वारिसनामाको ढाँचा",
    keywords=("power of attorney", "warisnama", "वारिस", "वकालतनामा", "representative", "court"),
    provisions=[{"law_title_ne": CDPC, "section": "146"}],
    fields=[
        F("opp_addr", "Opposite party: address", "विपक्षीको ठेगाना (बस्ने)"),
        F("opp_name", "Opposite party: name", "विपक्षीको नाम", required=True),
        F("case_title", "Case (मुद्दा)", "मुद्दा", required=True),
        F("purpose", "Purpose / work to be done", "वारिसले गर्ने काम (प्रयोजन)", required=True),
        F("w_addr", "Representative: address", "वारिसको ठेगाना (बस्ने)"),
        F("w_age", "Representative: age", "वारिसको उमेर (वर्ष)", "number"),
        F("w_name", "Representative: full name", "वारिसको पूरा नाम", required=True),
        F("w_cit_no", "Representative: citizenship no.", "वारिसको नागरिकता नं."),
        F("w_cit_issue", "Citizenship issued (year, district)", "नागरिकता जारी भएको वर्ष र जिल्ला"),
        F("p_name", "Principal (you): full name", "वारिसनामा दिने (तपाईं)को पूरा नाम", required=True),
        F("p_addr", "Principal: full address", "वारिसनामा दिनेको पूरा ठेगाना"),
        F("org_note", "Organisation name and address (if an organised body)", "सङ्गठित संस्था भए संस्थाको नाम तथा ठेगाना"),
        F("date1", "Date of the warisnama", "वारिसनामा गरेको मिति", "date"),
        F("date2", "Date of the representative's acceptance", "वारिसले मञ्जुरी गरेको मिति", "date"),
        F("wit1", "Witness 1: ID no., issuing district, address, age, name", "साक्षी १: परिचयपत्र नं. र जारी जिल्ला, ठेगाना, उमेर, नाम"),
        F("wit2", "Witness 2 (same details)", "साक्षी २ (यही विवरण)"),
        F("wit3", "Witness 3 / scribe (name; licence no. if any)", "साक्षी ३ / लेखक (नाम; प्रमाणपत्र भए सो)"),
        F("written_at", "Place where written", "वारिसनामा लेखिएको ठाउँ"),
        F("date3", "Witness attestation date", "साक्षी प्रमाणित मिति", "date"),
    ],
    body="""
@j,+ {{ opp_addr|blank(6) }} बस्ने {{ opp_name|blank(6) }} सँगको {{ case_title|blank(8) }} मुद्दामा मेरो तर्फबाट {{ purpose|blank(8) }} (प्रयोजन खुलाउने) काम गर्नलाई {{ w_addr|blank(6) }} बस्ने वर्ष {{ w_age|nd|blank(3) }} को {{ w_name|blank(6) }} नागरिकता नं. {{ w_cit_no|blank(6) }}/(नागरिकता जारी भएको वर्ष र जिल्ला) {{ w_cit_issue|blank(6) }} लाई __वारिसनामा__ दिई वारिस नियुक्त गरेको छु । निज वारिस कानून बमोजिम वारिस हुन योग्य हुनुहुन्छ । मैले अदालतबाट कानून बमोजिम लागेको दण्ड, जरिबाना, अदालती शुल्क सरकारी बिगो वा कुनै दस्तुर तिर्न बाँकी रहेको छैन । माथि लेखिएको व्यहोरा साँचो छ, झुट्टा ठहरेमा यो __वारिसनामा__ बदर गरी कानून बमोजिम भएमा मेरो मञ्जुरी छ ।
@l,+ मिति {{ date1|bs|blank(6) }}
@thumbs
@table 8.5,7.5 none
| औँठाको छाप/सङ्गठित संस्था भए संस्थाको छाप | दा. वा. (दस्तखत)<br>पूरा नाम थर : {{ p_name|blank(6) }}<br>पूरा ठेगाना : {{ p_addr|blank(6) }}{% if org_note %}<br>{{ org_note }}{% endif %} |
@end
@j,+ माथि उल्लेख भए बमोजिम {{ w_addr|blank(6) }} बस्ने {{ w_age|nd|blank(3) }} वर्ष नागरिकता नं. {{ w_cit_no|blank(6) }} (जारी भएको वर्ष र जिल्ला, सङ्गठित संस्था भएमा त्यस्तो संस्थाको नाम तथा ठेगाना) {{ w_cit_issue|blank(6) }} को वारिस भै काम गर्न मलाई मञ्जुर छ । सो काम म इमान्दारीपूर्वक गर्नेछु । मैले अदालतबाट कानून बमोजिम लागेको दण्ड, जरिबाना, अदालती शुल्क, सरकारी बिगो वा कुनै दस्तुर बुझाउन बाँकी रहेको छैन । म वारिस हुन कानून बमोजिम योग्य रहेको छु ।
@l,+ मिति {{ date2|bs|blank(6) }}
@thumbs
@table 8.5,7.5 none
| औँठाको छाप | दा. वा. (दस्तखत)<br>पूरा नाम थर : {{ w_name|blank(6) }}<br>पूरा ठेगाना : {{ w_addr|blank(6) }} |
@end
@u,+ साक्षीहरू :
@j यो __वारिसनामा__ हाम्रो रोहबरमा लेखी सहीछाप भएको साँचो हो ।
@l (१)|नागरिकता/राहदानी वा सो सरहको अन्य विवरण, नम्बर र जारी जिल्ला {{ wit1|blank(10) }} को श्री
@l (२)|नागरिकता/राहदानी वा सो सरहको अन्य विवरण, नम्बर र जारी जिल्ला {{ wit2|blank(10) }} को श्री
@l (३)|नागरिकता/राहदानी वा सो सरहको अन्य विवरण, नम्बर र जारी जिल्ला {{ wit3|blank(10) }} लेखक श्री (प्रमाणपत्र भए सो खुलाउने)
@l,>1 यो __वारिसनामा__ {{ written_at|blank(10) }} मा लेखिएको हो ।
@l मिति: {{ date3|bs }}
""",
)


# --------------------------------------------------------------------------
# निवेदनपत्र (सामान्य) - जिल्ला अदालत नियमावली, अनुसूची–९ (नियम १०६)
# --------------------------------------------------------------------------

def _petition_fields(court_label_en: str, court_label_ne: str, opp: str = "विपक्षी") -> list:
    return [
        F("court", court_label_en, court_label_ne, help_en="Only the name, e.g. Kathmandu", help_ne="जस्तै: काठमाडौं"),
        F("subject", "Subject (विषय)", "विषय", required=True),
        F("case_ref", "Case no. (मुद्दा नं.), if any", "मुद्दा नं. (भए)"),
        F("ap_line", "Applicant(s): full name, address, age", "निवेदकको पूरा नाम, ठेगाना, उमेर", required=True,
          help_en="If several applicants, separate with ; and all must sign (thumbprint if unable to write).",
          help_ne="एकभन्दा बढी निवेदक भए ; ले छुट्याउनुहोस्; लेखपढ गर्न नजान्नेले ल्याप्चे सही गर्नुपर्छ।"),
        F("op_line", "Opposite party(ies): full name, address", f"{opp}को पूरा नाम, ठेगाना", required=True),
        F("points", "Statement of the matter (one paragraph per line)", "निवेदनको विषयको वर्णन (एक पङ्क्तिमा एक प्रकरण)",
          "textarea", required=True,
          help_en="Number the paragraphs in order; the last two should state the law under which relief is claimed and the truth of the facts.",
          help_ne="प्रकरण सिलसिला मिलाई लेख्नुहोस्; अन्तिम दुई प्रकरणमा कुन कानून अन्तर्गत माग गरिएको हो र यथार्थताको उल्लेख गर्नुहोस्।"),
        F("prayer", "Relief prayed for (the 'तसर्थ ... गरिपाऊँ' part)", "माग गरिएको उपचार (तसर्थ ... गरिपाऊँ)", "textarea"),
        F("applicant_sign", "Applicant's name and place (signature block)", "निवेदकको नाम र ठेगाना (दस्तखत)"),
        DATE,
    ]


def _points_and_prayer(prayer: str, undertaking: str, extra: str = "") -> str:
    """The numbered paragraphs, the 'तसर्थ ... गरिपाउँ' prayer and the truth undertaking.
    The fixed wording differs slightly between schedules (गरिपाउँ / गरिपाऊँ, झुट्टा / झूठा), so
    each form passes its own transcription."""
    return (
        "@l,>1,each=points:2 {{ n|nd }}.|{{ item }}\n"
        "@j,+ {% if prayer %}तसर्थ यस विषयमा कानून बमोजिम {{ prayer }} गरिपाऊँ ।"
        "{% else %}" + prayer + "{% endif %}\n"
        "@j " + undertaking + extra + "\n"
    )


_DC_PRAYER = "तसर्थ यो यस विषयमा फलाना कानूनबमोजिम यो यस्तो गरिपाउँ वा यो यस्तो कुराका यो यसलाई आदेश गरिपाउँ।"
_DC_UNDERTAKING = "यस निवेदनपत्रको व्यहोरा ठीक साँचो छ, झुट्टा व्यहोरा लेखिएको ठहरे कानूनबमोजिम सजाय सहुँला बुझाउँला।"
_DC2_PRAYER = "तसर्थ यो यस विषयमा फलाना कानूनबमोजिम यो यस्तो गरिपाउँ वा यो यस्तो कुराको यो यसलाई आदेश गरिपाउँ ।"
_HC_PRAYER = "तसर्थ यो यस विषयमा फलाना कानून बमोजिम यो यस्तो गरिपाऊँ वा यो यस्तो कुराको यो यसलाई आदेश गरिपाऊँ।"
_HC_UNDERTAKING = "यस निवेदनपत्रको व्यहोरा ठीक साँचो छ, झूठा व्यहोरा लेखिएको ठहरे कानून बमोजिम सजाय सहुँला बुझाउँला ।"
_HC2_PRAYER = "तसर्थ यो विषयमा फलाना कानून बमोजिम यो यस्तो गरिपाऊँ वा यो यस्तो कुराको यो यसलाई आदेश गरिपाऊँ ।"
_HC2_UNDERTAKING = "यस निवेदनपत्रको व्यहोरा ठीक साँचो छ, झूठा व्यहोरा लेखेको ठहरे कानून बमोजिम सजाय सहुँला बुझाउँला ।"


DC_APPLICATION = official(
    id="application_district_court",
    title_en="General petition to a District Court - निवेदनपत्र",
    title_ne="जिल्ला अदालतमा दिने निवेदनपत्र (सामान्य)",
    desc_en="The general petition (निवेदनपत्र) any party files in a District Court, in the exact form of Schedule 9 of the District Court Rules.",
    desc_ne="जिल्ला अदालत नियमावलीको अनुसूची–९ (नियम १०६) बमोजिम जिल्ला अदालतमा दिने सामान्य निवेदनपत्रको ढाँचा।",
    category=CIVIL,
    law=DC_RULES, law_en="District Court Rules, 2075", schedule="अनुसूची–९", relates_to="नियम १०६", page=79,
    form_title="निवेदनपत्रको ढाँचा",
    keywords=("application", "petition", "निवेदन", "district court", "जिल्ला अदालत", "general application"),
    provisions=[{"law_title_ne": DC_RULES, "section": "106"}],
    fields=_petition_fields("District Court (district name)", "जिल्ला अदालत (जिल्लाको नाम)"),
    body="""
@cb,+ {{ court|blank(10) }} जिल्ला अदालतमा चढाएको
@cb निवेदनपत्र
@c विषय {{ subject|blank(10) }}
@c मुद्दा नः {{ case_ref|nd }}
@r,+ {{ ap_line|blank(25) }} निवेदक
@c विरुद्ध
@r {{ op_line|blank(25) }} विपक्षी
@l,+ म/हामी निम्न लिखित निवेदन गर्छु/गर्छौं :-
""" + _points_and_prayer(_DC_PRAYER, _DC_UNDERTAKING) + """
@r,+ ………………………
@r निवेदक{% if applicant_sign %} : {{ applicant_sign }}{% endif %}
@l,>0.5,+ {{ signoff(doc_date) }}
""",
)

DC_HABEAS = official(
    id="petition_habeas_injunction_dc",
    title_en="Habeas corpus / injunction petition (District Court)",
    title_ne="बन्दी प्रत्यक्षीकरण / निषेधाज्ञाको निवेदनपत्र (जिल्ला अदालत)",
    desc_en="Petition for habeas corpus or a prohibitory order in a District Court, in the exact form of Schedule 2 of the District Court Rules.",
    desc_ne="जिल्ला अदालत नियमावलीको अनुसूची–२ (नियम ३७) बमोजिम बन्दी प्रत्यक्षीकरण/निषेधाज्ञाको निवेदनपत्रको ढाँचा।",
    category=CIVIL,
    law=DC_RULES, law_en="District Court Rules, 2075", schedule="अनुसूची–२", relates_to="नियम ३७", page=64,
    form_title="बन्दी प्रत्यक्षीकरण / निषेधाज्ञा निवेदनपत्रको ढाँचा",
    keywords=("habeas corpus", "बन्दी प्रत्यक्षीकरण", "निषेधाज्ञा", "injunction", "detention", "writ", "wrongful detention"),
    provisions=[{"law_title_ne": DC_RULES, "section": "37"}],
    fields=_petition_fields("District Court (district name)", "जिल्ला अदालत (जिल्लाको नाम)"),
    body="""
@c,+ {{ court|blank(10) }} जिल्ला अदालतमा चढाएको
@cb निवेदनपत्र
@c विषयः {{ subject|blank(10) }} ।
@r,+ {{ ap_line|blank(25) }} निवेदक
@c विरूद्ध
@r {{ op_line|blank(25) }} विपक्षी
@l,+ म / हामी निम्नलिखित निवेदन गर्छु / गर्छौं :
""" + _points_and_prayer(_DC2_PRAYER, _DC_UNDERTAKING, " निवेदनको कारवाहीका सम्बन्धमा अदालतलाई आवश्यक सहयोग गर्नेछु ।") + """
@r,+ निवेदक{% if applicant_sign %} : {{ applicant_sign }}{% endif %}
@l,>0.5,+ {{ signoff(doc_date) }}
""",
)

HC_PETITION = official(
    id="writ_petition_high_court",
    title_en="Writ / petition to a High Court - निवेदनपत्र (रिट)",
    title_ne="उच्च अदालतमा दिने निवेदनपत्र (रिट निवेदन)",
    desc_en="The petition form of the High Court Rules (Schedule 1, rule 48) - the prescribed form for a writ petition or any petition to a High Court.",
    desc_ne="उच्च अदालत नियमावलीको अनुसूची–१ (नियम ४८) बमोजिम उच्च अदालतमा दिने रिट/निवेदनपत्रको ढाँचा।",
    category=CIVIL,
    law=HC_RULES, law_en="High Court Rules, 2073", schedule="अनुसूची–१", relates_to="नियम ४८", page=83,
    form_title="निवेदनपत्रको ढाँचा",
    keywords=("writ", "रिट", "certiorari", "mandamus", "उत्प्रेषण", "परमादेश", "high court", "उच्च अदालत", "petition"),
    provisions=[{"law_title_ne": HC_RULES, "section": "48"}],
    fields=[F("bench", "Bench (इजलास)", "इजलास")] + _petition_fields("High Court (place, e.g. Patan)", "उच्च अदालत (स्थान, जस्तै: पाटन)"),
    body="""
@cb,+ {{ court|blank(6) }} उच्च अदालत {{ bench|blank(6) }} मा चढाएको
@cbu निवेदनपत्र
@c,+ विषयः {{ subject|blank(10) }}
@r,+ {{ ap_line|blank(25) }} निवेदक
@cbu विरुद्ध
@r {{ op_line|blank(25) }} विपक्षी
@l,+ म/हामी निम्नलिखित निवेदन गर्छु/गछौँः
""" + _points_and_prayer(_HC_PRAYER, _HC_UNDERTAKING) + """
@r,+ निवेदक
@r {{ applicant_sign|blank(8) }}
@l,>1,+ {{ signoff(doc_date) }}
""",
)

HC_RESPONSE = official(
    id="written_response_high_court",
    title_en="Written response to a High Court petition - लिखित जवाफ",
    title_ne="उच्च अदालतमा दिने लिखित जवाफ",
    desc_en="The opposite party's written response to a High Court petition, in the exact form of Schedule 2 of the High Court Rules.",
    desc_ne="उच्च अदालत नियमावलीको अनुसूची–२ (नियम ४८) बमोजिम विपक्षीले दिने लिखित जवाफको ढाँचा।",
    category=CIVIL,
    law=HC_RULES, law_en="High Court Rules, 2073", schedule="अनुसूची–२", relates_to="नियम ४८", page=85,
    form_title="लिखित जवाफको ढाँचा",
    keywords=("written response", "लिखित जवाफ", "writ reply", "high court"),
    provisions=[{"law_title_ne": HC_RULES, "section": "48"}],
    fields=[
        F("court", "High Court (place, e.g. Patan)", "उच्च अदालत (स्थान, जस्तै: पाटन)"),
        F("bench", "Bench (इजलास)", "इजलास"),
        F("subject", "Subject (विषय)", "विषय", required=True),
        F("rp_line", "Respondent (you): name, address", "लिखित जवाफ प्रस्तुतकर्ताको नाम, ठेगाना", required=True),
        F("pt_line", "Petitioner (the other side): name, address", "विपक्षी (निवेदक)को नाम, ठेगाना", required=True),
        F("points", "Statement (one paragraph per line)", "निवेदनको व्यहोरा (एक पङ्क्तिमा एक प्रकरण)", "textarea", required=True),
        F("prayer", "Relief prayed for", "माग गरिएको उपचार", "textarea"),
        F("rp_sign", "Respondent's name and address (signature block)", "प्रस्तुतकर्ताको नाम, ठेगाना (दस्तखत)"),
        DATE,
    ],
    body="""
@cb,+ {{ court|blank(8) }} उच्च अदालत {{ bench|blank(8) }} मा चढाएको
@cb लिखित जवाफ
@c,+ विषयः {{ subject|blank(10) }}
@r,+ {{ rp_line|blank(25) }} लिखित जवाफ प्रस्तुतकर्ता
@cu,+ विरुद्ध
@r,+ {{ pt_line|blank(25) }} विपक्षी
@l,+ म/हामी निम्न लिखित निवेदन गर्छु/गर्छौँः
""" + _points_and_prayer(_HC2_PRAYER, _HC2_UNDERTAKING) + """
@r,+ __लिखित जवाफ प्रस्तुतकर्ता__
@r {{ rp_sign|blank(8) }}
@l,>1,+ {{ signoff(doc_date) }}
""",
)

# --------------------------------------------------------------------------
# मेलमिलाप - मेलमिलाप सम्बन्धी नियमावली, २०७० (अनुसूची–५ र ११)
# --------------------------------------------------------------------------

MEDIATION_COURT = official(
    id="mediation_petition_court",
    title_en="Mediation petition for a case pending in court - मेलमिलाप निवेदन",
    title_ne="मुद्दा मेलमिलापद्वारा समाधान गर्न दिइने निवेदन (अदालतमा विचाराधीन मुद्दा)",
    desc_en="Asks the court to send a pending case to mediation - the exact form of Schedule 5 of the Mediation Rules.",
    desc_ne="मेलमिलाप सम्बन्धी नियमावलीको अनुसूची–५ (नियम १२ को उपनियम (१)) बमोजिम मुद्दा मेलमिलापद्वारा समाधान गर्न दिइने निवेदनको ढाँचा।",
    category=CIVIL,
    law=MEDIATION_RULES, law_en="Mediation Rules, 2070", schedule="अनुसूची–५", relates_to="नियम १२ को उपनियम (१)",
    page=32, form_title="मेलमिलापद्वारा मुद्दा समाधान गर्न दिइने निवेदनको ढाँचा",
    keywords=("mediation", "मेलमिलाप", "settle", "compromise", "court", "मुद्दा"),
    provisions=[{"law_title_ne": MEDIATION_RULES, "section": "12"}],
    fields=[
        F("to_court", "Addressed to (court / body)", "श्री (अदालत/निकाय)", required=True),
        F("to_addr", "Address", "ठेगाना"),
        F("p1", "Plaintiff / appellant / petitioner (name)", "वादी/पुनरावेदक/निवेदकको नाम", required=True),
        SELECT("p1_role", "First party is", "पहिलो पक्ष", ["वादी", "पुनरावेदक", "निवेदक"]),
        F("p2", "Defendant / respondent (name)", "प्रतिवादी/प्रत्यर्थीको नाम", required=True),
        SELECT("p2_role", "Second party is", "दोस्रो पक्ष", ["प्रतिवादी", "प्रत्यर्थी"]),
        F("case_kind", "Nature of the case (मुद्दा)", "मुद्दाको किसिम", required=True),
        F("court_name", "Court where pending", "मुद्दा विचाराधीन अदालत"),
        F("sign_name", "Applicant's name", "निवेदकको नाम"),
        DATE,
    ],
    body="""
@l श्री {{ to_court|blank(10) }}
@l,>0.5 {{ to_addr|blank(8) }}
@cu,+ विषय :—मेलमिलापद्वारा मुद्दा समाधान गरी पाउँ ।
@j,>0.5 {{ p1|blank(8) }} {{ p1_role|default('वादी/पुनरावेदक/निवेदक', true) }} र {{ p2|blank(8) }} {{ p2_role|default('प्रतिवादी/प्रत्यर्थी', true) }} भएको {{ case_kind|blank(8) }} मुद्दा त्यस {{ court_name|blank(8) }} मा कारवाही भइरहेकोमा सो मुद्दा मेलमिलापको प्रक्रियाद्वारा समाधान गर्ने मेरो/हाम्रो इच्छा भएकोले सो मुद्दा मेलमिलापको प्रक्रियाद्वारा समाधान गर्ने सम्बन्धमा आवश्यक व्यवस्था गरी पाउन यो निवेदन गरेको छु/छौँ ।
@j,>0.5 निवेदनमा लेखिएको व्यहोरा ठीक साँचो छ, झुट्टा ठहरे कानून बमोजिम सँहुला बुझाउँला ।
@l,>8,+ निवेदकको,–
@l,>8 सही :
@l,>8 नाम : {{ sign_name }}
@l,>8 मिति : {{ doc_date|bs }}
""",
)

MEDIATION_BODY = official(
    id="mediation_petition_dispute",
    title_en="Petition to a mediation body / local body to resolve a dispute",
    title_ne="मेलमिलापद्वारा विवाद समाधान गर्न दिइने निवेदन (संस्था/स्थानीय निकाय/समुदाय)",
    desc_en="Asks a mediation organisation, local body or community mediator to resolve a dispute by mediation - the exact form of Schedule 11 of the Mediation Rules.",
    desc_ne="मेलमिलाप सम्बन्धी नियमावलीको अनुसूची–११ बमोजिम मेलमिलाप संस्था, स्थानीय निकाय वा समुदायद्वारा विवाद समाधान गर्न दिइने निवेदनको ढाँचा।",
    category=CIVIL,
    law=MEDIATION_RULES, law_en="Mediation Rules, 2070", schedule="अनुसूची–११",
    relates_to="नियम २९ को उपनियम (१) र नियम ३८ को उपनियम (१)", page=38,
    form_title="मेलमिलाप सम्बन्धी कार्य गर्ने संस्था, स्थानीय निकाय वा समुदायद्वारा विवाद समाधान गर्न दिइने निवेदनको ढाँचा",
    keywords=("mediation", "मेलमिलाप", "dispute", "विवाद", "community mediation", "ward", "local body"),
    provisions=[{"law_title_ne": MEDIATION_RULES, "section": "29"}],
    fields=[
        F("to_body", "Addressed to (mediation body)", "श्री (मेलमिलाप गर्ने संस्था/निकाय)", required=True),
        F("to_addr", "Address", "ठेगाना"),
        F("org", "Organisation / body / office", "संस्था/निकाय/कार्यालय"),
        F("a_name", "Party 1: name, surname", "पक्ष (क): नाम थर", required=True),
        F("a_district", "Party 1: district", "जिल्ला"), F("a_local", "Party 1: municipality / rural municipality", "गा.वि.स./न.पा."),
        F("a_ward", "Party 1: ward no.", "वडा नं."), F("a_tole", "Party 1: village / tole", "गाउँ/टोल"),
        F("a_phone", "Party 1: phone", "टेलिफोन नं."), F("a_email", "Party 1: email", "इमेल"), F("a_fax", "Party 1: fax", "फ्याक्स"),
        F("b_name", "Party 2: name, surname", "पक्ष (ख): नाम थर", required=True),
        F("b_district", "Party 2: district", "जिल्ला"), F("b_local", "Party 2: municipality / rural municipality", "गा.वि.स./न.पा."),
        F("b_ward", "Party 2: ward no.", "वडा नं."), F("b_tole", "Party 2: village / tole", "गाउँ/टोल"),
        F("b_phone", "Party 2: phone", "टेलिफोन नं."), F("b_email", "Party 2: email", "इमेल"),
        F("dispute", "2. Brief description of the dispute", "२. विवादको संक्षिप्त विवरण", "textarea", required=True),
        F("witnesses", "3. Witnesses (one per line)", "३. साक्षीहरू (एक पङ्क्तिमा एक जना)", "textarea"),
        F("attachments", "4. Attached documents (one per line)", "४. संलग्न कागजातहरू (एक पङ्क्तिमा एउटा)", "textarea"),
        F("sign1", "Applicant 1 name", "निवेदक १ को नाम"), F("sign2", "Applicant 2 name", "निवेदक २ को नाम"),
    ],
    body="""
@l श्री {{ to_body|blank(8) }}
@l,>0.5 {{ to_addr|blank(8) }}
@cu,+ विषय : मेलमिलापद्वारा विवाद समाधान गरी पाउँ ।
@j,>0.5,+ मेरो/हाम्रो त्यस {{ org|blank(8) }} संस्था/निकाय/कार्यालयबाट देहायको विवाद मेलमिलापद्वारा समाधान गर्ने इच्छा भएकोले मेलमिलापद्वारा विवाद समाधान गरी पाउन यो निवेदन पेश गरेको छु/छौँ ।
@l,+ १.|विवादको पक्षको,–
@l,>1 (क)|नाम थर : {{ a_name|blank(8) }}
@l,>2 ठेगाना : जिल्ला {{ a_district|blank(6) }}   गा.वि.स./न.पा. {{ a_local|blank(6) }}   वडा नं. {{ a_ward|nd|blank(3) }}
@l,>2 गाउँ/टोल {{ a_tole|blank(6) }}   टेलिफोन नं. {{ a_phone|nd|blank(6) }}   इमेल {{ a_email|blank(6) }}
@l,>2 फ्याक्स {{ a_fax|nd|blank(6) }}
@l,>1 (ख)|नाम थर : {{ b_name|blank(8) }}
@l,>2 ठेगाना जिल्ला {{ b_district|blank(6) }}   गा.वि.स./न.पा. {{ b_local|blank(6) }}   वडा नं. {{ b_ward|nd|blank(3) }}
@l,>2 गाउँ/टोल {{ b_tole|blank(6) }}   टेलिफोन नं. {{ b_phone|nd|blank(6) }}   इमेल {{ b_email|blank(6) }}
@l,+ २.|विवादको संक्षिप्त विवरण : {{ dispute }}
@l ३.|साक्षीहरु
@l,>1,each=witnesses:2 {{ n|nd }}.|{{ item }}
@j,>1,+ यसमा लेखिएको व्यहोरा ठीक साँचो छ, झुट्टा ठहरेमा कानून बमोजिम सहुँला बुझाउँला ।
@l ४.|संलग्न कागजातहरु
@l,>1,each=attachments:2 {{ n|nd }}.|{{ item }}
@l,>8,+ निवेदकको,–
@l,>8 १. सही: {{ sign1 }}
@l,>9 नाम: {{ sign1 }}
@l,>8 २. सही: {{ sign2 }}
@l,>9 नाम: {{ sign2 }}
""",
)

# --------------------------------------------------------------------------
# standard formats - no schedule prescribes them
# --------------------------------------------------------------------------

_SETTLEMENT_NOTE = {
    "en": "The Civil Procedure Code, 2074, s.193 prescribes the procedure (joint petition, three-copy draft read out to the "
          "parties, signed and certified by the judge) but attaches no schedule form. This is a standard layout that "
          "carries every element s.193 requires.",
    "ne": "मुलुकी देवानी कार्यविधि संहिता, २०७४ को दफा १९३ ले मिलापत्रको प्रक्रिया (संयुक्त निवेदन, तीन प्रति मस्यौदा, "
          "पक्षहरूलाई सुनाई दुवै पक्षको सहीछाप र न्यायाधीशको प्रमाणीकरण) तोकेको छ तर कुनै अनुसूचीमा ढाँचा तोकेको छैन। "
          "यो दफा १९३ ले चाहेका सबै तत्त्व समेटिएको साधारण ढाँचा हो।",
}

SETTLEMENT = standard(
    id="settlement_milapatra",
    title_en="Settlement deed in a court case - मिलापत्र",
    title_ne="मिलापत्र (अदालतमा विचाराधीन मुद्दामा)",
    desc_en="A joint settlement (मिलापत्र) of a pending civil case, with both parties' terms, signatures, thumbprints and the judge's certification. Standard format - not a prescribed schedule.",
    desc_ne="अदालतमा विचाराधीन मुद्दामा पक्षहरूले गर्ने मिलापत्र (शर्त, दुवै पक्षको सहीछाप/ल्याप्चे र न्यायाधीशको प्रमाणीकरणसहित)। मानक ढाँचा — अनुसूचीमा तोकिएको होइन।",
    category=CIVIL,
    basis_law=CDPC, basis_note=_SETTLEMENT_NOTE,
    provisions=[{"law_title_ne": CDPC, "section": "193"}],
    keywords=("settlement", "compromise", "मिलापत्र", "मिलाप", "court", "मुद्दा"),
    fields=[
        court_field(), F("case_no", "Case number", "मुद्दा नं."), CASE_TITLE,
        *party_fields("pl", "Plaintiff", "बादी"), *party_fields("df", "Defendant", "प्रतिबादी"),
        F("terms", "Settlement terms (one per line)", "मिलापत्रका शर्तहरू (एक पङ्क्तिमा एउटा)", "textarea", required=True),
        F("pl_sign", "Plaintiff's name (signature)", "बादीको नाम (सहीछाप)"), F("df_sign", "Defendant's name (signature)", "प्रतिबादीको नाम (सहीछाप)"),
        DATE,
    ],
    body="""
@cb """ + court_line("चढाएको") + """
@cbu मिलापत्र
@c मुद्दा नं. {{ case_no|nd|blank(6) }}     मुद्दा : {{ case_title|blank(8) }}
@c,+ """ + party_line("pl", "बादी") + """
@cbu विरुद्ध
@c """ + party_line("df", "प्रतिबादी") + """
@j,+ उपर्युक्त मुद्दामा हामी बादी र प्रतिबादी दुवै पक्षले आपसमा मिलापत्र गर्न मञ्जुर भई अदालतले हाम्रो निवेदनको व्यहोरा, त्यसको मतलब र परिणाम सुनाएपछि पनि स्वेच्छाले देहाय बमोजिम मिलापत्र गरेका छौँ :
@j,>0.5,each=terms:3 {{ n|nd }}.|{{ item }}
@j,+ माथि लेखिए बमोजिम मिलापत्र गरेकोले यो मिलापत्र बमोजिमको काम नभएको भन्ने विषयमा बाहेक हामी दुवै पक्षले मिलापत्रमा चित्त बुझेन भनी कुनै उजुर गर्ने छैनौँ । यो मिलापत्रको व्यहोरा हामीलाई पढी बाँची सुनाइएको र ठीक साँचो हो, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
@table 8,8 none
| @b बादीको सहीछाप<br>नाम : {{ pl_sign|blank(6) }} | @b प्रतिबादीको सहीछाप<br>नाम : {{ df_sign|blank(6) }} |
@end
@table 8,8 none
| @b बादीको ल्याप्चे सहीछाप (दायाँ / बायाँ) | @b प्रतिबादीको ल्याप्चे सहीछाप (दायाँ / बायाँ) |
@end
@thumbs
@l,+ मेरो रोहबरमा माथि लेखिए बमोजिम पक्षहरूले मिलापत्र गरेको ठीक साँचो हो भनी प्रमाणीकरण गर्ने :
@l न्यायाधीशको दस्तखत : …………………………
@l नाम : ………………………… मिति : {{ doc_date|bs|blank(6) }}
@l अदालतको छाप
""",
)

SC_WRIT = standard(
    id="writ_petition_supreme_court",
    title_en="Writ petition to the Supreme Court - रिट निवेदन",
    title_ne="सर्वोच्च अदालतमा दिने रिट निवेदन (संविधानको धारा १३३ को उपधारा (२))",
    desc_en="A writ petition under Article 133(2) laid out to carry the contents Rule 40 of the Supreme Court Rules, 2074 requires. Standard format - the Rules list the contents but attach no schedule form.",
    desc_ne="संविधानको धारा १३३ को उपधारा (२) अन्तर्गतको रिट निवेदन; सर्वोच्च अदालत नियमावली, २०७४ को नियम ४० ले तोकेका कुरा समेटिएको मानक ढाँचा — अनुसूचीमा ढाँचा तोकिएको छैन।",
    category=CIVIL,
    basis_law=SC_RULES,
    basis_note={
        "en": "SC Rules, 2074, Rules 32 and 40 list what a writ petition must state (grounds, jurisdiction, right infringed, absence of "
              "alternative remedy, relief sought, grounds for relief) and Rule 43 requires a statement that no parallel proceeding was "
              "filed. No schedule gives a fixed form, so this is a standard layout.",
        "ne": "सर्वोच्च अदालत नियमावली, २०७४ को नियम ३२ र ४० ले रिट निवेदनमा खुलाउनु पर्ने कुरा (कारण/तथ्य, अधिकारक्षेत्र, हनन भएको हक, "
              "वैकल्पिक उपचारको अभाव, मागेको उपचार, उपचारका आधार) र नियम ४३ ले समानान्तर अधिकारक्षेत्रमा निवेदन नदिएको बेहोरा खुलाउन भनेको छ। "
              "निश्चित ढाँचा कुनै अनुसूचीमा छैन, त्यसैले यो मानक ढाँचा हो।",
    },
    provisions=[{"law_title_ne": SC_RULES, "section": "32"}, {"law_title_ne": SC_RULES, "section": "40 (1)"},
                {"law_title_ne": SC_RULES, "section": "43"}],
    keywords=("writ", "रिट", "supreme court", "सर्वोच्च", "certiorari", "mandamus", "habeas", "fundamental rights", "PIL", "public interest"),
    fields=[
        F("subject", "Subject (writ sought)", "विषय (उत्प्रेषण/परमादेश/बन्दीप्रत्यक्षीकरण/अधिकारपृच्छा/निषेधाज्ञा आदि)", required=True),
        F("ap_line", "Petitioner: name, address, age", "निवेदकको पूरा नाम, ठेगाना, उमेर", required=True),
        F("op_line", "Respondents (one per line: office / person, address)", "विपक्षी (एक पङ्क्तिमा एक: कार्यालय/व्यक्ति, ठेगाना)", "textarea", required=True),
        F("facts", "1. Reason for the petition and the facts (one paragraph per line)", "१. निवेदन दिनु पर्ने कारण र तथ्य (एक पङ्क्तिमा एक प्रकरण)", "textarea", required=True),
        F("jurisdiction", "2. Jurisdiction of the Court", "२. अधिकारक्षेत्र सम्बन्धी कुरा", "textarea"),
        F("right_infringed", "3. Which fundamental / legal right is infringed and how", "३. निवेदकको के कस्तो मौलिक वा कानूनी हक कसरी हनन भएको", "textarea", required=True),
        F("alt_remedy", "4. No alternative remedy / why it is inadequate", "४. अन्य वैकल्पिक उपचार नभएको वा उपचार अपर्याप्त/प्रभावहीन भएको", "textarea"),
        F("relief", "6. Relief sought", "६. निवेदकले मागेको उपचार", "textarea", required=True),
        F("grounds", "7. Grounds for the relief (one per line)", "७. उपचारका आधारहरू (एक पङ्क्तिमा एउटा)", "textarea"),
        SELECT("public_interest", "Petition on a matter of public right / concern?", "सार्वजनिक हक वा सरोकारको विवाद सम्बन्धी निवेदन हो?", ["हो", "होइन"]),
        F("attachments", "Attached documents (one per line)", "संलग्न कागजातहरू (एक पङ्क्तिमा एउटा)", "textarea"),
        F("sign_name", "Petitioner's name (signature)", "निवेदकको नाम (दस्तखत)"),
        DATE,
    ],
    body="""
@cb श्री सर्वोच्च अदालतमा चढाएको
@cbu रिट निवेदन
@c (संविधानको धारा १३३ को उपधारा (२) बमोजिम)
@c,+ विषयः {{ subject|blank(10) }}
@r,+ {{ ap_line|blank(25) }} निवेदक
@cbu विरुद्ध
@r,each=op_line:1 {{ item|blank(20) }} विपक्षी
@l,+ म/हामी निवेदकले निम्न निवेदन गर्दछु/गर्दछौँः
@j १.|निवेदन दिनु पर्ने कारण र सो सम्बन्धी तथ्य :
@j,>1,each=facts:1 ({{ ka }})|{{ item }}
@j २.|अधिकारक्षेत्र सम्बन्धी कुरा : {{ jurisdiction|blank(10) }}
@j ३.|निवेदकको के कस्तो मौलिक वा कानूनी हक कसरी हनन भएको छ : {{ right_infringed|blank(10) }}
@j ४.|अन्य वैकल्पिक उपचार नभएको वा वैकल्पिक उपचारको व्यवस्था भए पनि सो उपचार अपर्याप्त वा प्रभावहीन देखिएको पुष्ट्याइँ : {{ alt_remedy|blank(10) }}
@j ५.|यस निवेदनमा उल्लेख भएको विषयमा उच्च अदालत वा जिल्ला अदालतमा समेत समानान्तर अधिकारक्षेत्र प्रयोग गरी कुनै निवेदन दिएको वा कानूनी कारबाही चलाएको छैन भन्ने बेहोरा खुलाएको छु/छौँ ।
@j ६.|निवेदकले मागेको उपचार : {{ relief|blank(10) }}
@j ७.|उपचारका आधारहरू :
@j,>1,each=grounds:1 ({{ ka }})|{{ item }}
@j {% if public_interest == 'हो' %}८.{% endif %}|{% if public_interest == 'हो' %}यो निवेदन सार्वजनिक हक वा सरोकारको विवादमा समावेश भएको संवैधानिक वा कानूनी प्रश्नको निरूपणको लागि दिइएको हो; निवेदकको यसमा कुनै व्यक्तिगत फाइदा वा निजी स्वार्थ छैन भनी स्वघोषणा गर्दछु/गर्दछौँ ।{% endif %}
@j,+ तसर्थ माथि लेखिएका आधार र कारणबाट निवेदकले माग गरेको उपचार प्राप्त हुने गरी विपक्षीका नाउँमा उपयुक्त आदेश/परमादेश/उत्प्रेषण जारी गरिपाऊँ ।
@j यस निवेदनमा लेखिएको व्यहोरा ठीक साँचो छ, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
@u,+ संलग्न कागजातहरू :
@l,>1,each=attachments:1 {{ n|nd }}.|{{ item }}
@r,+ निवेदक{% if sign_name %} : {{ sign_name }}{% endif %}
@r ………………………
@l,>1,+ {{ signoff(doc_date) }}
""",
)

TEMPLATES = [REPLY, APPEAL, WARISNAMA, DC_APPLICATION, DC_HABEAS, HC_PETITION, HC_RESPONSE,
             MEDIATION_COURT, MEDIATION_BODY, SETTLEMENT, SC_WRIT]
