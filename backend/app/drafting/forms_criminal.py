"""Criminal-procedure forms transcribed from the schedules of the
मुलुकी फौजदारी कार्यविधि संहिता, २०७४ (Criminal Procedure Code, 2074):

  अनुसूची–५   जाहेरी दरखास्तको ढाँचा           (दफा ४)
  अनुसूची–२१  उजुरीको ढाँचा                     (दफा ५३)
  अनुसूची–४२  प्रतिउत्तरपत्रको ढाँचा            (दफा १२२)
  अनुसूची–४५  पुनरावेदनपत्रको ढाँचा            (दफा १३६)
  अनुसूची–४६  प्रतिवादको ढाँचा                  (दफा १४०)

Each was read from the page image of the official PDF (the Law Commission
copy's text layer is scrambled), so `source.page` is the page to open.
"""
from __future__ import annotations

from .dsl import F, SELECT
from .forms_common import CRPC, official

POLICE = "police"
COURT = "police"  # criminal-procedure forms sit with the FIR under "Police & criminal"

_SIGN_NOTE = "@l,>0 "

# --------------------------------------------------------------------------
# जाहेरी दरखास्त - अनुसूची–५ (दफा ४ को उपदफा (१) र (७))
# --------------------------------------------------------------------------

FIR = official(
    id="fir_jaheri_darkhast",
    title_en="First information report (FIR) to the police - जाहेरी दरखास्त",
    title_ne="जाहेरी दरखास्त (प्रहरी कार्यालयमा)",
    desc_en="Report a crime to the police in the exact form of Schedule 5 of the Criminal Procedure Code: informant, offence, offender, incident details and evidence.",
    desc_ne="मुलुकी फौजदारी कार्यविधि संहिताको अनुसूची–५ बमोजिम कसूरको जाहेरी दरखास्त वा सूचना दिने ढाँचा।",
    category=POLICE,
    law=CRPC, law_en="Muluki Criminal Procedure Code, 2074", schedule="अनुसूची–५", relates_to="दफा ४ को उपदफा (१) र (७)",
    page=146, form_title="जाहेरी दरखास्तको ढाँचा",
    keywords=("FIR", "first information report", "police complaint", "जाहेरी", "दरखास्त", "प्रहरी", "crime", "report to police", "उजुरी"),
    provisions=[{"law_title_ne": CRPC, "section": "4"}],
    fields=[
        F("police_office", "Police office it is submitted to", "श्री ... (प्रहरी कार्यालय) मा पेश गरेको", required=True),
        F("police_addr", "Police office: name and address", "प्रहरी कार्यालयको नाम र ठेगाना"),
        F("reg_no", "Registration no. (police fill)", "दर्ता नं. (प्रहरीले भर्ने)"),
        F("reg_date", "Registration date (police fill)", "दर्ता मिति (प्रहरीले भर्ने)", "date"),
        F("informant", "1. Your name, surname, address (with tole) and phone", "१. जाहेरी दरखास्त वा सूचना दिने व्यक्तिको नाम, थर र ठेगाना (टोल सहित) फोन नम्बर", required=True),
        F("subject", "2. Which law / offence is the report about", "२. कुन कानून वा मुद्दाबारे दरखास्त वा सूचना गरेको हो", required=True),
        F("offender", "3. Offender's name, surname and address (with tole)", "३. कसूर गर्ने व्यक्तिको नाम, थर र ठेगाना (टोल सहित)"),
        F("offender_parents", "4. Offender's father / mother", "४. कसूर गर्ने व्यक्तिको बाबु/आमाको नाम"),
        F("offender_look", "5. Offender's appearance and other identifying details", "५. कसूर गर्ने व्यक्तिको हुलिया र परिचय खुल्ने अन्य विवरण", "textarea"),
        F("place_time", "6(a). Place, date and time the offence happened / is happening / is about to happen",
          "६(क). कसूर भएको वा भइरहेको वा हुन लागेको स्थान, ठाउँ, मिति र समय", "textarea"),
        F("incident", "6(b). Details of the incident", "६(ख). कसूरसँग सम्बन्धित घटनाको विवरण", "textarea", required=True),
        F("nature", "6(c). Nature of the offence and other related details", "६(ग). कसूरको प्रकृति र कसूरसँग सम्बन्धित अन्य विवरण", "textarea"),
        F("evidence", "6(d). Evidence", "६(घ). कसूरसँग सम्बन्धित सबुद प्रमाण", "textarea"),
        F("other", "6(e). Other details", "६(ङ). कसूरसँग सम्बन्धित अन्य विवरण", "textarea"),
        F("sign_date", "Date", "मिति", "date"),
    ],
    body="""
@table 9,6.5 none
| श्री {{ police_office|blank(10) }} मा पेश गरेको | प्रहरी कार्यालयले भर्ने |
| (प्रहरी कार्यालयको नाम र ठेगाना){% if police_addr %} : {{ police_addr }}{% endif %} | दर्ता नं:- {{ reg_no|nd }} |
| | दर्ता मितिः- {{ reg_date|bs }} |
@end
@l,+ १.|जाहेरी दरखास्त वा सूचना दिने व्यक्तिको नाम, थर र ठेगाना (टोल सहित) फोन नम्बरः- {{ informant|nd }}
@l २.|कुन कानून वा मुद्दाबारे दरखास्त वा सूचना गरेको होः- {{ subject }}
@l ३.|कसूर गर्ने व्यक्तिको नाम, थर र ठेगाना (टोल सहित):- {{ offender }}
@l ४.|कसूर गर्ने व्यक्तिको बाबु/आमाको नामः- {{ offender_parents }}
@l ५.|कसूर गर्ने व्यक्तिको हुलिया र परिचय खुल्ने अन्य विवरण :- {{ offender_look }}
@l ६.|कसूर सम्बन्धी विवरणः
@l,>1 (क)|कसूर भएको वा भइरहेको वा हुन लागेको स्थान, ठाउँ, मिति र समय, {{ place_time }}
@l,>1 (ख)|कसूरसँग सम्बन्धित घटनाको विवरण, {{ incident }}
@l,>1 (ग)|कसूरको प्रकृति र कसूरसँग सम्बन्धित अन्य विवरण, {{ nature }}
@l,>1 (घ)|कसूरसँग सम्बन्धित सबुद प्रमाण, {{ evidence }}
@l,>1 (ङ)|कसूरसँग सम्बन्धित अन्य विवरण । {{ other }}
@j ७.|यो दरखास्तको व्यहोरा ठीक साँचो छ, झुट्टा व्यहोरा लेखेको ठहरे कानून बमोजिम सहुँला बुझाउँला ।
@j,>1 प्रहरीद्वारा अनुसन्धान हुँदा वा अदालतमा मुद्दा चल्दाको बखत उपस्थित हुनु पर्ने जनाउ पाए सो बमोजिम उपस्थित हुनेछु।
@l,>8,+ जाहेरी वा सूचना दिने व्यक्तिकोः
@l,>10 सहीः-
@l,>10 मितिः {{ sign_date|bs }}
""",
)

# --------------------------------------------------------------------------
# उजुरी - अनुसूची–२१ (दफा ५३ को उपदफा (२))
# --------------------------------------------------------------------------

_PARTY_COMPLAINANT = [
    F("court", "Court (name)", "अदालत (नाम)"),
    F("reg_no", "Registration no. (court fills)", "दर्ता नं. (अदालतले भर्ने)"),
    F("reg_date", "Registration date (court fills)", "दर्ता मिति (अदालतले भर्ने)", "date"),
]

COMPLAINT = official(
    id="criminal_complaint_ujuri",
    title_en="Criminal complaint to the court - उजुरीपत्र",
    title_ne="उजुरीपत्र (फौजदारी मुद्दा, अदालतमा)",
    desc_en="A private complaint filed directly in court against an offender, in the exact form of Schedule 21 of the Criminal Procedure Code.",
    desc_ne="मुलुकी फौजदारी कार्यविधि संहिताको अनुसूची–२१ बमोजिम अदालतमा दिने उजुरीको ढाँचा।",
    category=COURT,
    law=CRPC, law_en="Muluki Criminal Procedure Code, 2074", schedule="अनुसूची–२१", relates_to="दफा ५३ को उपदफा (२)",
    page=174, form_title="उजुरीको ढाँचा",
    keywords=("complaint", "उजुरी", "criminal case", "फौजदारी", "private prosecution", "court"),
    provisions=[{"law_title_ne": CRPC, "section": "53 (1)"}],
    fields=[
        *_PARTY_COMPLAINANT,
        F("court_name", "Court complaint is filed in (name)", "उजुरी दायर गर्ने अदालत (नाम)", required=True),
        F("chapter", "Chapter (परिच्छेद)", "परिच्छेद"), F("section", "Section (दफा)", "दफा"),
        F("case_year", "Year of criminal case (B.S.)", "फौ.मि. को साल"), F("case_no", "Criminal case no.", "फौ.मि. नं."),
        F("c_addr", "Complainant: address", "उजुरवालाको ठेगाना (बस्ने)"), F("c_age", "Complainant: age", "उजुरवालाको उमेर", "number"),
        F("c_name", "Complainant: full name", "उजुरवालाको पूरा नाम", required=True),
        F("o_addr", "Offender: address", "कसूरदारको ठेगाना (बस्ने)"), F("o_age", "Offender: age", "कसूरदारको उमेर", "number"),
        F("o_name", "Offender: full name", "कसूरदारको पूरा नाम", required=True),
        F("case_title", "Case (मुद्दा)", "मुद्दा", required=True),
        F("offence", "1. Details of the offence", "१. कसूरको विवरण", "textarea", required=True),
        F("charge", "2. Charge against the offender", "२. कसूरदार उपर लगाएको अभियोग"),
        F("law", "3. Relevant law", "३. सम्बन्धित कानून"),
        F("punishment", "4. Punishment the offender should get", "४. कसूरदारलाई हुनु पर्ने सजाय"),
        F("loss", "5. Loss suffered and amount to be recovered from the offender", "५. कसूरबाट हुन गएको क्षति र कसूरदारबाट भराउनु पर्ने रकम"),
        F("admitted", "6. If the accused admitted the offence: details and remission for it", "६. अभियुक्तले कसूर स्वीकार गरेको भए सो सम्बन्धी विवरण र सो बापत पाउने सजाय छुट"),
        F("other", "7. Other necessary matters", "७. अन्य आवश्यक कुराहरू"),
        F("witnesses", "Witnesses (one per line: full name, age, address)", "साक्षी (एक पङ्क्तिमा: पूरा नाम, उमेर, ठेगाना)", "textarea"),
        F("documents", "Documents (one per line)", "लिखत (एक पङ्क्तिमा एउटा)", "textarea"),
        F("exhibits", "Exhibits (दसी) (one per line)", "दसी (एक पङ्क्तिमा एउटा)", "textarea"),
        F("c_birthplace", "Complainant: born at", "उजुरवाला जन्म भै (ठाउँ)"), F("c_dwell", "Complainant: residing at", "बस्ने ठाउँ"),
        SELECT("c_rel", "Complainant is child / spouse of", "छोरा/छोरी/पत्नी", ["छोरा", "छोरी", "पत्नी"]),
        F("c_parent", "Name of father / husband", "बाबु/पतिको नाम"),
        F("sign_date", "Date", "मिति", "date"),
    ],
    body="""
@l,>9,+ अदालतले भर्ने {{ court|blank(6) }}
@l,>9 दर्ता नं. {{ reg_no|nd|blank(8) }}
@l,>9 दर्ता मिति {{ reg_date|bs|blank(8) }}
@j,+ {{ court_name|blank(8) }} मा मुलुकी फौजदारी कार्यविधि (संहिता) ऐन, २०७४ को परिच्छेद {{ chapter|nd|blank(6) }} को दफा {{ section|nd|blank(6) }} अन्तर्गत दायर गरेको
@cu,+ उजुरीपत्र
@j,+ {{ case_year|nd|blank(8) }} सालको फौ.मि. नं. {{ case_no|nd|blank(12) }} बस्ने {{ c_addr|blank(6) }} वर्ष {{ c_age|nd|blank(4) }} को {{ c_name|blank(8) }} उजुरवाला ।
@cu,+ विरुद्ध
@c {{ o_addr|blank(6) }} बस्ने वर्ष {{ o_age|nd|blank(4) }} को {{ o_name|blank(8) }} कसूरदार
@c,+ मुद्दा {{ case_title|blank(8) }}
@j,>0.7,+ उपर्युक्त कसूरदारले गरेको कसूरको व्यहोरा निम्न लिखित छ । निज उपर मुद्दाको कारबाही गर्न सादर अनुरोध गर्छु ।
@l,+ १.|कसूरको विवरण {{ offence }}
@l २.|कसूरदार उपर लगाएको अभियोग {{ charge }}
@l ३.|सम्बन्धित कानून {{ law }}
@l ४.|कसूरदारलाई हुनु पर्ने सजाय {{ punishment }}
@l ५.|कसूरबाट हुन गएको क्षति र कसुरदारबाट भराउनु पर्ने रकम {{ loss|nd }}
@j ६.|अभियुक्तले कसूर स्वीकार गरेको भए सो सम्बन्धी विवरण र सो बापत पाउने सजाय छुट {{ admitted }}
@l ७.|अन्य आवश्यक कुराहरु {{ other }}
@u,+ प्रमाण
@u साक्षी
@l,each=witnesses:2 ({{ n|nd }})|{{ item }}
@r (साक्षीहरुको पूरा नाम, उमेर र ठेगाना)
@u,+ लिखत
@l,each=documents:2 {{ n|nd }}.|{{ item }}
@u,+ दसी
@l,each=exhibits:2 {{ n|nd }}.|{{ item }}
@cu,+ उजुरवाला
@c {{ c_birthplace|blank(8) }} जन्म भै {{ c_dwell|blank(6) }} बस्ने
@c {{ c_rel|default('छोरा/छोरी/पत्नी', true) }} {{ c_parent|blank(8) }} {{ c_age|nd|blank(4) }} वर्षको
@c {{ c_name|blank(12) }}
@l,+ मिति {{ sign_date|bs|blank(8) }}
""",
)

# --------------------------------------------------------------------------
# प्रतिउत्तरपत्र - अनुसूची–४२ (दफा १२२ को उपदफा (८))
# --------------------------------------------------------------------------

CRIMINAL_REPLY = official(
    id="criminal_written_reply",
    title_en="Accused's written reply - प्रतिउत्तरपत्र (criminal case)",
    title_ne="प्रतिउत्तरपत्र (फौजदारी मुद्दा, अभियुक्तको)",
    desc_en="The accused's written reply to a charge sheet or complaint, in the exact form of Schedule 42 of the Criminal Procedure Code.",
    desc_ne="मुलुकी फौजदारी कार्यविधि संहिताको अनुसूची–४२ बमोजिम अभियुक्तले दिने प्रतिउत्तरपत्रको ढाँचा।",
    category=COURT,
    law=CRPC, law_en="Muluki Criminal Procedure Code, 2074", schedule="अनुसूची–४२", relates_to="दफा १२२ को उपदफा (८)",
    page=196, form_title="प्रतिउत्तरपत्रको ढाँचा",
    keywords=("reply", "defence", "accused", "प्रतिउत्तर", "अभियुक्त", "criminal", "फौजदारी"),
    provisions=[{"law_title_ne": CRPC, "section": "122"}],
    fields=[
        F("reg_no", "Registration no. (court fills)", "दर्ता नं. (अदालतले भर्ने)"),
        F("reg_date", "Registration date (court fills)", "दर्ता मिति (अदालतले भर्ने)", "date"),
        F("filed_at", "Filed at (court)", "मा दाखिल गरेको (अदालत)", required=True),
        F("case_year", "Case year (B.S.)", "साल"), F("case_no", "Criminal case no. (फौ.मि.नं.)", "फौ.मि.नं."),
        F("a_addr", "Accused: address", "अभियुक्तको ठेगाना (बस्ने)"), F("a_age", "Accused: age", "अभियुक्तको उमेर", "number"),
        F("a_name", "Accused: full name", "अभियुक्तको पूरा नाम", required=True),
        F("c_addr", "Complainant: address", "उजुरवालाको ठेगाना (बस्ने)"), F("c_age", "Complainant: age", "उजुरवालाको उमेर", "number"),
        F("c_name", "Complainant: full name (or Nepal Government)", "उजुरवालाको नाम (वा नेपाल सरकार)", required=True),
        F("case_title", "Case (मुद्दा)", "मुद्दा", required=True),
        F("points", "Your response to the allegation (one point per line)", "अभियोगका सम्बन्धमा मेरो व्यहोरा (एक पङ्क्तिमा एक बुँदा)", "textarea", required=True),
        F("witnesses", "Witnesses (one per line: full name, age, address)", "साक्षी (एक पङ्क्तिमा: पूरा नाम, उमेर, ठेगाना)", "textarea"),
        F("documents", "Documents (one per line)", "लिखत (एक पङ्क्तिमा एउटा)", "textarea"),
        F("a_birthplace", "Accused: born at", "अभियुक्त जन्म भै (ठाउँ)"), F("a_dwell", "Accused: residing at", "बस्ने ठाउँ"),
        SELECT("a_rel", "Accused is child / spouse of", "छोरा/छोरी/पत्नी", ["छोरा", "छोरी", "पत्नी"]),
        F("a_parent", "Name of father / husband", "बाबु/पतिको नाम"),
        F("sign_date", "Date", "मिति", "date"),
    ],
    body="""
@l,>8 अदालतले भर्ने
@l,>8 दर्ता नं. {{ reg_no|nd|blank(8) }}
@l,>8 दर्ता मितिः {{ reg_date|bs|blank(8) }}
@c,>4 {{ filed_at|blank(10) }} मा दाखिल गरेको
@cbu,+ प्रतिउत्तरपत्रको ढाँचा
@j,+ {{ case_year|nd|blank(8) }} साल को फौ.मि.नं. {{ case_no|nd|blank(10) }} बस्ने {{ a_addr|blank(6) }} वर्ष {{ a_age|nd|blank(6) }} को {{ a_name|blank(10) }} अभियुक्त ।
@c,+ विरुद्ध
@j,+ {{ c_name|blank(10) }} बस्ने {{ c_addr|blank(6) }} वर्ष {{ c_age|nd|blank(6) }} को उजुरवाला
@c,+ मुद्दा {{ case_title|blank(10) }}
@j,>0.7,+ उपर्युक्त उजुरवालाले मलाई लगाएको अभियोगका सम्बन्धमा मेरो व्यहोरा निम्नलिखित छ ।
@l,>1,each=points:3 {{ n|nd }}.|{{ item|blank(10) }}
@cu,+ प्रमाण
@u साक्षी
@l,each=witnesses:3 {{ n|nd }}.|{{ item|blank(10) }}{% if n == 1 %} साक्षीहरुको पूरा नाम, उमेर र ठेगाना{% endif %}
@u,+ लिखत
@l,each=documents:2 {{ n|nd }}.|{{ item|blank(10) }}
@l,+ {{ a_birthplace|blank(10) }} जन्म भै {{ a_dwell|blank(20) }}
@l बस्ने {{ a_dwell|blank(10) }} को {{ a_rel|default('छोरा/छोरी/पत्नी', true) }} {{ a_parent|blank(10) }}
@l वर्षको {{ a_age|nd|blank(10) }}
@l मिति {{ sign_date|bs|blank(10) }}      अभियुक्तको सहीछाप
""",
)

# --------------------------------------------------------------------------
# पुनरावेदनपत्र - अनुसूची–४५ (दफा १३६ को उपदफा (१))
# --------------------------------------------------------------------------

CRIMINAL_APPEAL = official(
    id="criminal_appeal",
    title_en="Appeal in a criminal case - पुनरावेदनपत्र",
    title_ne="पुनरावेदनपत्र (फौजदारी मुद्दा)",
    desc_en="Appeal by a convicted person against a criminal judgment, in the exact form of Schedule 45 of the Criminal Procedure Code.",
    desc_ne="मुलुकी फौजदारी कार्यविधि संहिताको अनुसूची–४५ बमोजिम फौजदारी मुद्दाको फैसलामा चित्त नबुझी दिने पुनरावेदनपत्रको ढाँचा।",
    category=COURT,
    law=CRPC, law_en="Muluki Criminal Procedure Code, 2074", schedule="अनुसूची–४५", relates_to="दफा १३६ को उपदफा (१)",
    page=201, form_title="पुनरावेदनपत्रको ढाँचा",
    keywords=("appeal", "पुनरावेदन", "criminal", "फौजदारी", "sentence", "conviction", "सजाय"),
    provisions=[{"law_title_ne": CRPC, "section": "136"}],
    fields=[
        F("reg_no", "Registration no. (court fills)", "दर्ता नं. (अदालतले भर्ने)"),
        F("reg_date", "Registration date (court fills)", "दर्ता मिति (अदालतले भर्ने)", "date"),
        F("filed_at", "Appeal filed at (court)", "मा दिएको (अदालत)", required=True),
        F("appeal_year", "Year (B.S.)", "साल"), F("appeal_no", "Appeal no.", "पुनरावेदन नं."),
        F("ap_addr", "Appellant: address", "पुनरावेदकको ठेगाना (बस्ने)"), F("ap_name", "Appellant: full name", "पुनरावेदकको पूरा नाम", required=True),
        SELECT("ap_role", "Appellant was", "पुनरावेदक (उजुरवाला/अभियुक्त)", ["उजुरवाला", "अभियुक्त"]),
        F("rs_addr", "Respondent: address", "प्रत्यर्थीको ठेगाना (बस्ने)"), F("rs_name", "Respondent: full name", "प्रत्यर्थीको पूरा नाम", required=True),
        SELECT("rs_role", "Respondent was", "प्रत्यर्थी (उजुरवाला/अभियुक्त)", ["प्रत्यर्थी", "उजुरवाला", "अभियुक्त"]),
        F("case_title", "Case (मुद्दा)", "मुद्दा", required=True),
        F("deciding_court", "Court whose judgment is appealed", "फैसला गर्ने अदालत"),
        F("decision_date", "Date of the judgment", "फैसला भएको मिति", "date"),
        F("sentence", "Sentence imposed on you", "गरिएको सजाय (कैद/जरिबाना)"),
        F("points", "Grounds of appeal (one per line)", "पुनरावेदनको व्यहोरा (एक पङ्क्तिमा एक बुँदा)", "textarea", required=True),
        F("sign_date", "Date", "मिति", "date"), F("sign_name", "Appellant's name", "पुनरावेदकको नाम"), F("sign_addr", "Appellant's address", "पुनरावेदकको ठेगाना"),
    ],
    body="""
@l,>9 अदालतले भर्ने
@l,>10 दर्ता नं. {{ reg_no|nd|blank(8) }}
@l,>10 दर्ता मितिः {{ reg_date|bs|blank(8) }}
@c,>4 {{ filed_at|blank(10) }} मा दिएको
@cu पुनरावेदनपत्र
@r पहिला
@l {{ appeal_year|nd|blank(8) }} सालको {{ appeal_no|nd|blank(12) }} पुनरावेदन नं.
@r दोश्रो
@l {{ ap_addr|blank(8) }} बस्ने {{ ap_name|blank(12) }} पुनरावेदक
@l,>1 {{ ap_role|default('उजुरवाला। अभियुक्त', true) }}
@cbu,+ विरुद्ध
@c {{ rs_addr|blank(10) }} बस्ने {{ rs_name|blank(10) }} {{ rs_role|default('प्रत्यर्थी/उजुरवाला/अभियुक्त', true) }}
@c,+ मुद्दा {{ case_title|blank(10) }}
@j,>3,+ {{ deciding_court|blank(10) }} ले {{ decision_date|bs|blank(10) }} उपरोक्त मुद्दामा म/हामीहरुलाई {{ sentence|blank(10) }} सजाय गरी बिगो वा क्षतिपूर्ति भराउने गरी फैसला गरेकोले फैसला बमोजिम भएको सजाय भोगी/सो बापत धरौट/जमानत दिई चित्त नबुझेको कुरामा पुनरावेदन दिन आएको छु/छौँ मेरो/हाम्रो व्यहोरा निम्नलिखित छः-
@l,>1,each=points:4 {{ n|nd }}.|{{ item|blank(10) }}
@l,+ मिति {{ sign_date|bs|blank(10) }}        पुनरावेदकको सहीछाप
@l,>9 नामः {{ sign_name }}
@l,>9 ठेगानाः {{ sign_addr }}
""",
)

TEMPLATES = [FIR, COMPLAINT, CRIMINAL_REPLY, CRIMINAL_APPEAL]
