"""Standard-format complaints and petitions: laws that create the right to
complain or claim but attach no schedule form. Each is laid out to ordinary
Nepali court / office conventions (and, for the court papers, follows the
layout of the nearest prescribed schedule) and is labelled "standard format"
with the provisions it rests on.
"""
from __future__ import annotations

from .dsl import F, SELECT
from .forms_common import (
    CDPC, DATE, DC_RULES, EVIDENCE, FEE_ITEMS, FEES, LAWYERS, WITNESSES, court_field, court_line, more_parties_field,
    numbered_items, pair_items, party_fields, party_line, standard,
)

LABOUR_ACT = "श्रम ऐन, २०७४"
FEA_ACT = "वैदेशिक रोजगार ऐन, २०६४"
NI_ACT = "विनिमेय अधिकारपत्र ऐन, २०३४"
CIVIL_CODE = "मुलुकी देवानी संहिता, २०७४"

# --------------------------------------------------------------------------
# श्रम उजुरी
# --------------------------------------------------------------------------

LABOUR_COMPLAINT = standard(
    id="labour_complaint",
    title_en="Labour complaint - श्रम उजुरी",
    title_ne="श्रम उजुरी (रोजगारदाता वा श्रमिकको कार्य विरुद्ध)",
    desc_en="A complaint that an employer, worker or office broke the Labour Act 2074 or its Rules, filed within six months of the act. Standard format - the Act names who may complain and when but attaches no form.",
    desc_ne="श्रम ऐन, २०७४ वा नियम विपरीत कार्य गरेको उजुरी (कार्य भए गरेको मितिले छ महिनाभित्र)। मानक ढाँचा — ऐनले उजुरी दिन सक्ने व्यक्ति र म्याद तोकेको छ तर ढाँचा तोकेको छैन।",
    category="office",
    basis_law=LABOUR_ACT,
    basis_note={
        "en": "Labour Act, 2074, s.162: a party harmed by an act contrary to the Act or its Rules (or a trade union with the harmed party's written "
              "consent) may complain to the deciding body within six months of the act. No schedule fixes a form, so this is a standard layout.",
        "ne": "श्रम ऐन, २०७४ को दफा १६२: ऐन वा नियम विपरीत कार्यबाट मर्का पर्ने पक्षले (वा निजको लिखित मञ्जुरीमा ट्रेड युनियनले) कार्य भए गरेको मितिले "
              "छ महिनाभित्र निर्णय गर्ने निकायमा उजुरी दिन सक्ने। ढाँचा कुनै अनुसूचीमा तोकिएको छैन, त्यसैले यो मानक ढाँचा हो।",
    },
    provisions=[{"law_title_ne": LABOUR_ACT, "section": "162"}, {"law_title_ne": LABOUR_ACT, "section": "164"}],
    keywords=("labour", "labor", "श्रम", "employer", "worker", "unpaid wages", "dismissal", "complaint", "उजुरी", "श्रम कार्यालय", "श्रम अदालत", "salary"),
    fields=[
        F("office", "Addressed to (labour office / Labour Court)", "श्री (श्रम कार्यालय / श्रम अदालत)", required=True),
        F("office_addr", "Office address", "कार्यालयको ठेगाना"),
        F("c_name", "Complainant: full name", "उजुरीकर्ताको पूरा नाम", required=True),
        F("c_addr", "Complainant: address", "उजुरीकर्ताको ठेगाना", required=True),
        F("c_phone", "Complainant: phone", "उजुरीकर्ताको फोन"),
        F("c_post", "Post / nature of work", "पद / कामको प्रकृति"),
        F("c_join", "Date of appointment", "नियुक्ति भएको मिति", "date"),
        F("c_pay", "Monthly pay (NPR)", "मासिक पारिश्रमिक (रु.)", "number"),
        F("e_name", "Employer / party complained against", "विपक्षी रोजगारदाता / व्यक्तिको नाम", required=True),
        F("e_addr", "Employer's address", "विपक्षीको ठेगाना", required=True),
        F("act_date", "Date the act complained of happened", "उजुरी गरिएको कार्य भए गरेको मिति", "date", required=True),
        F("facts", "What happened (one point per line)", "घटनाको विवरण (एक पङ्क्तिमा एक बुँदा)", "textarea", required=True),
        F("breach", "Provision(s) of the Labour Act / Rules breached", "उल्लङ्घन भएको ऐन/नियमको दफा"),
        F("relief", "Relief sought", "माग गरेको उपचार", "textarea", required=True),
        F("attachments", "Documents attached (one per line)", "संलग्न कागजात (एक पङ्क्तिमा एउटा)", "textarea"),
        DATE,
    ],
    body="""
@r मितिः {{ doc_date|bs|blank(6) }}
@l,+ श्री {{ office|blank(10) }}
@l {{ office_addr }}
@cbu,+ विषयः श्रम ऐन, २०७४ को दफा १६२ बमोजिम उजुरी ।
@j उपर्युक्त सम्बन्धमा म उजुरीकर्ता देहायको विवरण खुलाई विपक्षी उपर कानून बमोजिम कारबाही गरी पाउन यो उजुरी दिएको छु ।
@l १.|उजुरीकर्ताको विवरणः नाम, थर {{ c_name }}, ठेगाना {{ c_addr }}{% if c_phone %}, फोन {{ c_phone|nd }}{% endif %}{% if c_post %}, पद/काम {{ c_post }}{% endif %}{% if c_join %}, नियुक्ति मिति {{ c_join|bs }}{% endif %}{% if c_pay %}, मासिक पारिश्रमिक रु. {{ c_pay|nd }}{% endif %} ।
@l २.|विपक्षीको विवरणः {{ e_name }}, ठेगाना {{ e_addr }} ।
@l ३.|उजुरी गरिएको कार्य भए गरेको मितिः {{ act_date|bs }} । श्रम ऐन, २०७४ को दफा १६२ बमोजिम कार्य भए गरेको मितिले छ महिनाभित्र यो उजुरी दिइएको छ ।
@l ४.|घटनाको विवरणः
@j,>1,each=facts:1 ({{ ka }})|{{ item }}
@l ५.|ऐन/नियमको उल्लङ्घनः {{ breach|blank(8) }}
@l ६.|मागः {{ relief }}
@l ७.|संलग्न कागजातः
@l,>1,each=attachments:1 {{ n|nd }}.|{{ item }}
@j,+ माथि लेखिएको व्यहोरा ठीक साँचो हो, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
@r,+ उजुरीकर्ता
@r नामः {{ c_name }}
@r सहीः ………………………
""",
)

# --------------------------------------------------------------------------
# वैदेशिक रोजगार उजुरी
# --------------------------------------------------------------------------

FEA_COMPLAINT = standard(
    id="foreign_employment_complaint",
    title_en="Foreign-employment complaint - वैदेशिक रोजगार उजुरी",
    title_ne="वैदेशिक रोजगार सम्बन्धी उजुरी (विभाग / प्रमुख जिल्ला अधिकारी)",
    desc_en="A migrant worker's complaint against a recruitment agency or agent - fraud, unpaid fees, no job or a different job - to the Department of Foreign Employment or the Chief District Officer, with compensation claim. Standard format.",
    desc_ne="वैदेशिक रोजगार संस्था वा एजेन्ट विरुद्ध कामदारले वैदेशिक रोजगार विभाग वा प्रमुख जिल्ला अधिकारीलाई दिने उजुरी (ठगी, सेवा शुल्क, रोजगार नपाएको वा फरक रोजगार, क्षतिपूर्ति माग)। मानक ढाँचा।",
    category="office",
    basis_law=FEA_ACT,
    basis_note={
        "en": "Foreign Employment Act, 2064, s.21A (complaints may be lodged by post or electronically with the Department, or with the Chief District Officer), "
              "s.36 (worker may claim compensation from the Department if the agency gave no job on the contracted terms) and s.60 (one-year limitation). "
              "No schedule fixes a form, so this is a standard layout.",
        "ne": "वैदेशिक रोजगार ऐन, २०६४ को दफा २१क (विभाग समक्ष वा प्रमुख जिल्ला अधिकारी समक्ष हुलाक वा विद्युतीय माध्यमबाट उजुरी), दफा ३६ "
              "(सम्झौता बमोजिम रोजगार नपाएमा क्षतिपूर्तिको लागि विभागमा उजुरी) र दफा ६० (एक वर्षको हदम्याद)। ढाँचा कुनै अनुसूचीमा तोकिएको छैन, त्यसैले यो मानक ढाँचा हो।",
    },
    provisions=[{"law_title_ne": FEA_ACT, "section": "21क"}, {"law_title_ne": FEA_ACT, "section": "36"},
                {"law_title_ne": FEA_ACT, "section": "60"}],
    keywords=("foreign employment", "वैदेशिक रोजगार", "migrant worker", "recruitment agency", "manpower", "fraud", "ठगी", "abroad", "complaint", "उजुरी", "compensation", "क्षतिपूर्ति", "visa"),
    fields=[
        SELECT("to", "Complaint to", "उजुरी दिने निकाय", ["वैदेशिक रोजगार विभाग", "प्रमुख जिल्ला अधिकारी"]),
        F("to_office", "Office address (Department: Tahachal / CDO office district)", "कार्यालयको ठेगाना"),
        F("w_name", "Worker: full name", "कामदारको पूरा नाम", required=True),
        F("w_addr", "Worker: address", "कामदारको ठेगाना", required=True),
        F("w_phone", "Worker: phone", "फोन"), F("w_passport", "Passport no.", "राहदानी नं."),
        F("agency", "Recruitment agency / agent complained against", "उजुरी गरिएको वैदेशिक रोजगार संस्था / एजेन्ट", required=True),
        F("agency_addr", "Agency address and licence no.", "संस्थाको ठेगाना र इजाजतपत्र नं."),
        F("country", "Destination country", "गन्तव्य देश"), F("job", "Job promised", "प्रतिज्ञा गरिएको रोजगार"),
        F("paid", "Amount paid to the agency / agent (NPR)", "संस्था/एजेन्टलाई तिरेको रकम (रु.)", "number"),
        F("paid_date", "Date(s) paid", "रकम तिरेको मिति"),
        F("facts", "What happened (one point per line)", "घटनाको विवरण (एक पङ्क्तिमा एक बुँदा)", "textarea", required=True),
        F("relief", "Relief sought (refund, compensation, action against the agency)", "माग (रकम फिर्ता, क्षतिपूर्ति, संस्था उपर कारबाही)", "textarea", required=True),
        F("attachments", "Documents attached (receipts, contract, visa, messages) (one per line)", "संलग्न कागजात (रसिद, सम्झौता, भिसा, सन्देश) (एक पङ्क्तिमा एउटा)", "textarea"),
        DATE,
    ],
    body="""
@r मितिः {{ doc_date|bs|blank(6) }}
@l,+ श्री {{ to|default('वैदेशिक रोजगार विभाग / प्रमुख जिल्ला अधिकारी', true) }}
@l {{ to_office }}
@cbu,+ विषयः उजुरी सम्बन्धमा ।
@j उपर्युक्त सम्बन्धमा वैदेशिक रोजगार ऐन, २०६४ को दफा २१क बमोजिम देहायको विवरण खुलाई यो उजुरी दिएको छु ।
@l १.|उजुरीकर्ता (कामदार): {{ w_name }}, ठेगाना {{ w_addr }}{% if w_phone %}, फोन {{ w_phone|nd }}{% endif %}{% if w_passport %}, राहदानी नं. {{ w_passport|nd }}{% endif %} ।
@l २.|विपक्षी वैदेशिक रोजगार संस्था/एजेन्ट: {{ agency }}{% if agency_addr %}, {{ agency_addr }}{% endif %} ।
@l ३.|गन्तव्य देश {{ country|blank(6) }} र प्रतिज्ञा गरिएको रोजगार {{ job|blank(6) }}{% if paid %}; निज संस्था/एजेन्टलाई {{ paid_date|nd }} मा जम्मा रु. {{ paid|nd }} तिरेको{% endif %} ।
@l ४.|घटनाको विवरणः
@j,>1,each=facts:1 ({{ ka }})|{{ item }}
@l ५.|माग: {{ relief }}
@l ६.|संलग्न कागजातः
@l,>1,each=attachments:1 {{ n|nd }}.|{{ item }}
@j,+ माथि लेखिएको व्यहोरा ठीक साँचो हो, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
@r,+ उजुरीकर्ता
@r नामः {{ w_name }}
@r सहीः ………………………
""",
)

# --------------------------------------------------------------------------
# चेक अनादर - दाबी फिरादपत्र (plaint layout)
# --------------------------------------------------------------------------

_CHEQUE_NOTE = {
    "en": "The Negotiable Instruments Act, 2034 (s.16, s.43) makes the bank liable for a proper cheque drawn on sufficient funds and requires "
          "presentment for payment; a claim on a dishonoured cheque is an ordinary civil suit, so this follows the layout of the plaint "
          "(Schedule 1 of the Civil Procedure Code). No schedule fixes cheque-specific wording; the facts paragraphs are standard.",
    "ne": "विनिमेय अधिकारपत्र ऐन, २०३४ को दफा १६ ले पर्याप्त निक्षेप भएको चेकको भुक्तानी दिनु पर्ने बैङ्कको दायित्व र दफा ४३ ले भुक्तानीको लागि "
          "प्रस्तुत गर्नु पर्ने कुरा तोकेको छ; अनादर भएको चेकको दाबी सामान्य देवानी मुद्दा हो, त्यसैले यसमा फिरादपत्र (देवानी कार्यविधि संहिता, अनुसूची–१) को "
          "ढाँचा अपनाइएको छ। चेक सम्बन्धी विशेष शब्दावली कुनै अनुसूचीमा तोकिएको छैन; तथ्यका प्रकरण मानक हुन्।",
}

CHEQUE_CLAIM = standard(
    id="cheque_dishonour_claim",
    title_en="Claim on a dishonoured cheque (plaint layout) - चेक अनादर दाबी",
    title_ne="चेक अनादर भएकोले रकम भराई पाउँ भन्ने फिरादपत्र",
    desc_en="A civil plaint to recover the amount of a cheque that the bank dishonoured, in the layout of the prescribed plaint. Standard format - the cheque-specific paragraphs are not prescribed by a schedule.",
    desc_ne="बैङ्कले अनादर गरेको चेकको रकम भराई पाउन दिने देवानी फिरादपत्र (तोकिएको फिरादपत्रको ढाँचामा)। मानक ढाँचा — चेक सम्बन्धी प्रकरण अनुसूचीमा तोकिएको होइन।",
    category="court",
    basis_law=NI_ACT, basis_note=_CHEQUE_NOTE,
    provisions=[{"law_title_ne": NI_ACT, "section": "16"}, {"law_title_ne": NI_ACT, "section": "43"},
                {"law_title_ne": CDPC, "section": "95"}],
    keywords=("cheque", "check", "चेक", "dishonour", "bounced cheque", "अनादर", "bank", "बैङ्क", "recovery", "रकम असुली", "debt"),
    fields=[
        court_field(),
        *party_fields("pl", "Plaintiff (payee / holder)", "बादी (चेक पाउने)"), *party_fields("df", "Defendant (drawer)", "प्रतिबादी (चेक जारी गर्ने)"),
        F("cheque_no", "Cheque no.", "चेक नं.", required=True), F("bank", "Bank and branch on which it was drawn", "चेक भुक्तानी दिने बैङ्क र शाखा", required=True),
        F("cheque_date", "Date on the cheque", "चेकमा लेखिएको मिति", "date", required=True),
        F("amount", "Amount of the cheque (NPR)", "चेकको रकम (रु.)", "number", required=True),
        F("reason_for_cheque", "Why the cheque was given (debt / goods / loan)", "चेक दिनुको कारण (ऋण / सामान / कर्जा)", required=True),
        F("presented_date", "Date presented to the bank for payment", "भुक्तानीको लागि बैङ्कमा प्रस्तुत गरेको मिति", "date", required=True),
        F("dishonour_reason", "Bank's stated reason for dishonour", "बैङ्कले जनाएको अनादरको कारण (जस्तै: खातामा रकम अपुग)", required=True),
        F("notice_date", "Date you gave written demand to the defendant", "प्रतिबादीलाई लिखित माग गरेको मिति", "date"),
        F("other_claims", "Interest / other amounts claimed", "ब्याज / अन्य माग रकम"),
        F("juris", "Basis for the court's jurisdiction", "अधिकारक्षेत्रको आधार"),
        LAWYERS, FEES, EVIDENCE, WITNESSES, DATE,
    ],
    body="""
@r अदालत/कार्यालयले भर्ने
@r मुद्दा दर्ता नं.: ……………
@r दर्ता मिति: ……………
@c,+ """ + court_line() + """
@cbu फिरादपत्र
@c,+ """ + party_line("pl", "बादी") + """
@cb विरुद्ध
@c """ + party_line("df", "प्रतिबादी") + """
@cb मुद्दा :- चेक अनादर भएकोले रकम भराई पाउँ ।
@l,+ १.|म/हामी फिरादपत्रवाला निम्न प्रकरणहरूमा लेखिए बमोजिम फिराद गर्दछु/गर्दछौँ ।
@j,>1 (क)|प्रतिबादीले {{ reason_for_cheque }} बापत मलाई/हामीलाई मिति {{ cheque_date|bs }} को रु. {{ amount|nd }} को {{ bank }} बाट भुक्तानी हुने चेक नं. {{ cheque_no|nd }} लेखिदिएको हो ।
@j,>1 (ख)|उक्त चेक मैले/हामीले मिति {{ presented_date|bs|blank(6) }} मा भुक्तानीको लागि सम्बन्धित बैङ्कमा प्रस्तुत गर्दा {{ dishonour_reason }} भनी बैङ्कले चेक अनादर गरी फिर्ता दिएको हो ।
@j,>1 (ग)|{% if notice_date %}प्रतिबादीलाई मिति {{ notice_date|bs }} मा लिखित रूपमा रकम बुझाउन माग गर्दा पनि निजले रकम भुक्तानी गरेका छैनन् ।{% else %}प्रतिबादीले चेकको रकम आजसम्म भुक्तानी गरेका छैनन् ।{% endif %}
@j,>1 (घ)|विनिमेय अधिकारपत्र ऐन, २०३४ को दफा ४३ बमोजिम चेक भुक्तानीको लागि प्रस्तुत गरिएको हुँदा चेकको रकम रु. {{ amount|nd }}{% if other_claims %} तथा {{ other_claims }}{% endif %} प्रतिबादीबाट भराई पाउँ ।
@j २.|{{ juris|blank(10) }} बमोजिम यो मुद्दा यसै अदालत/कार्यालयको अधिकारक्षेत्रभित्र पर्दछ ।
@j ३.|फिराद गर्न कानून बमोजिम हदम्याद रहेको छ ।
@j ४.|प्रस्तुत विषयमा अन्यत्र फिराद गरेको छैन ।
@j ५.|प्रतिबादीलाई आफैँले/कानून व्यवसायी मार्फत/अदालतबाट म्याद तामेल गर्ने व्यवस्था गरी पाउँ ।
@l ६.|कानून व्यवसायी नियुक्त गरेको भए सोको विवरणः
""" + pair_items("lawyers", 3, "नाम", "प्रमाणपत्र नं", gap=10) + """
@l ७.|देहायको दस्तुर यसैसाथ बुझाउन ल्याएको छु/छौँ ।
""" + FEE_ITEMS + """
@l ८.|फिरादको दाबीलाई पुष्टि गर्ने प्रमाणः-
@l,>1 यस विषयमा देहायको प्रमाण सम्बन्धी कागजातको प्रतिलिपि संलग्न गरेको छु/छौँ ।
""" + numbered_items("evidence", 3) + """
@l ९.|साक्षीः
""" + numbered_items("witnesses", 3) + """
@l १०.|यसमा लेखिएको व्यहोरा ठीक साँचो छ, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
@r,+ ………………………
@ru फिरादपत्रवालाको दस्तखत र सङ्गठित संस्था भए संस्थाको छाप
@l,>1.5,+ {{ signoff(doc_date) }}
""",
)

# --------------------------------------------------------------------------
# सम्बन्ध विच्छेद निवेदन (निवेदनपत्र layout)
# --------------------------------------------------------------------------

_DIVORCE_NOTE = {
    "en": "Civil Code 2074 ss.93-95 give the grounds (mutual consent; by husband; by wife) and s.96 says the spouse who wants divorce petitions the "
          "District Court; s.99 requires the partition of property before divorce. The petition follows the general petition layout of the District Court "
          "Rules (Schedule 9, rule 106). No schedule fixes divorce-specific wording.",
    "ne": "मुलुकी देवानी संहिता, २०७४ को दफा ९३–९५ ले सम्बन्ध विच्छेदका आधार (दुवैको मञ्जुरी; पतिले; पत्नीले) र दफा ९६ ले सम्बन्ध विच्छेद गर्न चाहने पति वा पत्नीले "
          "जिल्ला अदालतमा निवेदन दिनु पर्ने तोकेको छ; दफा ९९ ले सम्बन्ध विच्छेद गर्नु अघि अंशबण्डा गर्नु पर्ने भनेको छ। निवेदन जिल्ला अदालत नियमावलीको "
          "सामान्य निवेदनपत्रको ढाँचा (अनुसूची–९, नियम १०६) मा तयार गरिएको छ। सम्बन्ध विच्छेद सम्बन्धी विशेष शब्दावली अनुसूचीमा तोकिएको छैन।",
}

DIVORCE_PETITION = standard(
    id="divorce_petition",
    title_en="Divorce petition to the District Court - सम्बन्ध विच्छेद निवेदन",
    title_ne="सम्बन्ध विच्छेदको निवेदन (जिल्ला अदालत)",
    desc_en="A petition for divorce (mutual consent, or by the husband or wife on the statutory grounds) in the general petition layout of the District Court Rules. Standard format for the divorce content.",
    desc_ne="सम्बन्ध विच्छेदको निवेदन (दुवैको मञ्जुरी वा पति/पत्नीले कानूनी आधारमा) — जिल्ला अदालत नियमावलीको निवेदनपत्रको ढाँचामा। सम्बन्ध विच्छेदको व्यहोरा मानक ढाँचाको हो।",
    category="court",
    basis_law=CIVIL_CODE, basis_note=_DIVORCE_NOTE,
    provisions=[{"law_title_ne": CIVIL_CODE, "section": "93"}, {"law_title_ne": CIVIL_CODE, "section": "94"},
                {"law_title_ne": CIVIL_CODE, "section": "95"}, {"law_title_ne": CIVIL_CODE, "section": "96"},
                {"law_title_ne": DC_RULES, "section": "106"}],
    keywords=("divorce", "सम्बन्ध विच्छेद", "separation", "marriage", "विवाह", "husband", "wife", "पति", "पत्नी", "family court", "अंशबण्डा"),
    fields=[
        F("court", "District Court (district name)", "जिल्ला अदालत (जिल्लाको नाम)", required=True),
        F("ap_line", "Petitioner: full name, address, age", "निवेदकको पूरा नाम, ठेगाना, उमेर", required=True),
        F("op_line", "Spouse (opposite party): full name, address", "विपक्षी (पति/पत्नी) को पूरा नाम, ठेगाना", required=True),
        SELECT("ground", "Ground", "सम्बन्ध विच्छेदको आधार", ["दुवैको मञ्जुरी (दफा ९३)", "पतिले (दफा ९४)", "पत्नीले (दफा ९५)"]),
        F("marriage_date", "Date of marriage", "विवाह भएको मिति", "date"),
        F("marriage_reg", "Marriage registration no. (if registered)", "विवाह दर्ता नं. (दर्ता भएको भए)"),
        F("children", "Children of the marriage (names, ages)", "सन्तान (नाम, उमेर)", "textarea"),
        F("grounds_detail", "Facts supporting the ground (one point per line)", "आधारलाई पुष्टि गर्ने तथ्य (एक पङ्क्तिमा एक बुँदा)", "textarea", required=True),
        F("partition", "Property partition / maintenance / custody arrangements", "अंशबण्डा / भरणपोषण / सन्तानको संरक्षण सम्बन्धी व्यवस्था", "textarea"),
        F("sign_name", "Petitioner's name (signature)", "निवेदकको नाम (दस्तखत)"),
        DATE,
    ],
    body="""
@cb {{ court|blank(10) }} जिल्ला अदालतमा चढाएको
@cb निवेदनपत्र
@c विषय सम्बन्ध विच्छेद गरी पाऊँ ।
@r,+ {{ ap_line|blank(25) }} निवेदक
@c विरूद्ध
@r {{ op_line|blank(25) }} विपक्षी
@l,+ म/हामी निम्न लिखित निवेदन गर्छु/गर्छौं :-
@j,>1 १.|{% if marriage_date %}हामीबीच मिति {{ marriage_date|bs }} मा विवाह भएको{% else %}हामीबीच विवाह भएको{% endif %}{% if marriage_reg %} (विवाह दर्ता नं. {{ marriage_reg|nd }}){% endif %} हो ।
@j,>1 २.|सम्बन्ध विच्छेदको आधार: {{ ground|default('मुलुकी देवानी संहिता, २०७४ को दफा ९३/९४/९५', true) }} ।
@j,>1,each=grounds_detail:1 {{ n|nd }}.|{{ item }}
@j,>1 ३.|सन्तानको विवरण: {{ children|blank(6) }}
@j,>1 ४.|अंशबण्डा / भरणपोषण / सन्तानको संरक्षण: {{ partition|blank(6) }}
@j,+ तसर्थ मुलुकी देवानी संहिता, २०७४ को दफा ९६ बमोजिम हामी पति पत्नीबीचको वैवाहिक सम्बन्ध विच्छेद गरी पाऊँ ।
@j यस निवेदनपत्रको व्यहोरा ठीक साँचो छ, झुट्टा व्यहोरा लेखिएको ठहरे कानून बमोजिम सजाय सहुँला बुझाउँला ।
@r,+ ………………………
@r निवेदक{% if sign_name %} : {{ sign_name }}{% endif %}
@l,>0.5,+ {{ signoff(doc_date) }}
""",
)

# --------------------------------------------------------------------------
# अंश दाबी फिरादपत्र (plaint layout)
# --------------------------------------------------------------------------

_PARTITION_NOTE = {
    "en": "Civil Code 2074 ss.205-211 say who is a co-parcener (अंशियार) and may claim a share; s.216 requires partition; s.217 lists what a partition "
          "deed must state. A partition claim is an ordinary civil suit, so this follows the plaint layout (Schedule 1 of the Civil Procedure Code); the claim "
          "paragraphs are standard, not prescribed.",
    "ne": "मुलुकी देवानी संहिता, २०७४ को दफा २०५–२११ ले अंशियार को हुन् र अंश दाबी गर्न सक्ने कुरा, दफा २१६ ले अंशबण्डा गर्नु पर्ने कुरा र दफा २१७ ले अंशबण्डाको "
          "लिखतमा खुलाउनु पर्ने कुरा तोकेको छ। अंश दाबी सामान्य देवानी मुद्दा हो, त्यसैले फिरादपत्र (देवानी कार्यविधि संहिता, अनुसूची–१) को ढाँचा अपनाइएको छ; "
          "दाबीका प्रकरण मानक हुन्, तोकिएका होइनन्।",
}

PARTITION_PLAINT = standard(
    id="partition_plaint",
    title_en="Partition (अंश) claim plaint - अंश दाबी फिरादपत्र",
    title_ne="अंश दाबी सम्बन्धी फिरादपत्र",
    desc_en="A plaint claiming a share of family property (अंश) and its partition, in the layout of the prescribed plaint. Standard format for the partition content.",
    desc_ne="पारिवारिक सम्पत्तिमा अंश दाबी र अंशबण्डा गरी पाउन दिने फिरादपत्र (तोकिएको फिरादपत्रको ढाँचामा)। अंशको व्यहोरा मानक ढाँचाको हो।",
    category="court",
    basis_law=CIVIL_CODE, basis_note=_PARTITION_NOTE,
    provisions=[{"law_title_ne": CIVIL_CODE, "section": "205"}, {"law_title_ne": CIVIL_CODE, "section": "211"},
                {"law_title_ne": CIVIL_CODE, "section": "216"}, {"law_title_ne": CDPC, "section": "95"}],
    keywords=("partition", "अंश", "अंशबण्डा", "inheritance", "share", "property", "family property", "co-parcener", "अंशियार", "plaint"),
    fields=[
        court_field(),
        *party_fields("pl", "Plaintiff", "बादी"), more_parties_field("pl_more", "plaintiff", "बादी"),
        *party_fields("df", "Defendant", "प्रतिबादी"), more_parties_field("df_more", "defendant", "प्रतिबादी"),
        F("relation", "Relationship between you and the defendant(s)", "बादी र प्रतिबादीबीचको नाता", required=True),
        F("property", "Property to be partitioned (one item per line: kitta no., area, location / other assets)", "अंशबण्डा हुनु पर्ने सम्पत्ति (एक पङ्क्तिमा एउटा: कित्ता नं., क्षेत्रफल, ठाउँ / अन्य)", "textarea", required=True),
        F("facts", "Why you are entitled and why partition was refused (one point per line)", "अंश पाउने आधार र अंश नदिएको कारण (एक पङ्क्तिमा एक बुँदा)", "textarea", required=True),
        F("share_claim", "Share claimed", "दाबी गरेको अंश"),
        F("juris", "Basis for the court's jurisdiction", "अधिकारक्षेत्रको आधार"),
        LAWYERS, FEES, EVIDENCE, WITNESSES, DATE,
    ],
    body="""
@r अदालत/कार्यालयले भर्ने
@r मुद्दा दर्ता नं.: ……………
@r दर्ता मिति: ……………
@c,+ """ + court_line() + """
@cbu फिरादपत्र
@c,+ """ + party_line("pl", "बादी") + """
@c,each=pl_more:0 {{ item }} **बादी**
@cb विरुद्ध
@c """ + party_line("df", "प्रतिबादी") + """
@c,each=df_more:0 {{ item }} **प्रतिबादी**
@cb मुद्दा :- अंश ।
@l,+ १.|म/हामी फिरादपत्रवाला निम्न प्रकरणहरूमा लेखिए बमोजिम फिराद गर्दछु/गर्दछौँ ।
@j,>1 (क)|प्रतिबादी मेरा/हाम्रा {{ relation|blank(6) }} हुन्, हामी अंशियार हौँ ।
@j,>1 (ख)|अंशबण्डा हुनु पर्ने सम्पत्तिको विवरण देहाय बमोजिम छः
@l,>2,each=property:1 {{ n|nd }}.|{{ item }}
@j,>1,each=facts:1 ({{ kaf(n + 2) }})|{{ item }}
@j,>1 उपर्युक्त सम्पत्तिमा मेरो/हाम्रो {{ share_claim|blank(6) }} अंश पुग्ने हुँदा मुलुकी देवानी संहिता, २०७४ को दफा २१६ बमोजिम अंशबण्डा गरी मेरो/हाम्रो अंश भाग छुट्याई पाऊँ ।
@j २.|{{ juris|blank(10) }} बमोजिम यो मुद्दा यसै अदालत/कार्यालयको अधिकारक्षेत्रभित्र पर्दछ ।
@j ३.|फिराद गर्न कानून बमोजिम हदम्याद रहेको छ ।
@j ४.|प्रस्तुत विषयमा अन्यत्र फिराद गरेको छैन ।
@j ५.|प्रतिबादीलाई आफैँले/कानून व्यवसायी मार्फत/अदालतबाट म्याद तामेल गर्ने व्यवस्था गरी पाउँ ।
@l ६.|कानून व्यवसायी नियुक्त गरेको भए सोको विवरणः
""" + pair_items("lawyers", 3, "नाम", "प्रमाणपत्र नं", gap=10) + """
@l ७.|देहायको दस्तुर यसैसाथ बुझाउन ल्याएको छु/छौँ ।
""" + FEE_ITEMS + """
@l ८.|फिरादको दाबीलाई पुष्टि गर्ने प्रमाणः-
@l,>1 यस विषयमा देहायको प्रमाण सम्बन्धी कागजातको प्रतिलिपि संलग्न गरेको छु/छौँ ।
""" + numbered_items("evidence", 3) + """
@l ९.|साक्षीः
""" + numbered_items("witnesses", 3) + """
@l १०.|यसमा लेखिएको व्यहोरा ठीक साँचो छ, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
@r,+ ………………………
@ru फिरादपत्रवालाको दस्तखत र सङ्गठित संस्था भए संस्थाको छाप
@l,>1.5,+ {{ signoff(doc_date) }}
""",
)

TEMPLATES = [LABOUR_COMPLAINT, FEA_COMPLAINT, CHEQUE_CLAIM, DIVORCE_PETITION, PARTITION_PLAINT]
