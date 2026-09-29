"""Government-office forms.

Official (transcribed from a schedule of the rules named in `source`):
  * RTI appeal to the National Information Commission (सूचनाको हक नियमावली, अनुसूची)
  * Consumer complaint (उपभोक्ता संरक्षण नियमावली, अनुसूची–९)
  * Domestic-violence complaint (घरेलु हिंसा नियमावली, अनुसूची–१)
  * Notices of birth / death / marriage / divorce / migration to the local
    registrar (व्यक्तिगत घटना दर्ता नियमावली, अनुसूची–२ देखि ६)

Standard (no schedule prescribes the form; laid out to Nepali office-letter
convention and labelled as such): RTI request, labour complaint,
foreign-employment complaint.
"""
from __future__ import annotations

from .dsl import F, SELECT
from .forms_common import CONSUMER_RULES, DV_RULES, RTI_RULES, official, standard

OFFICE = "office"
NOTICES = "notices"

RTI_ACT = "सूचनाको हक सम्बन्धी ऐन, २०६४"
CONSUMER_ACT = "उपभोक्ता संरक्षण ऐन, २०७५"
LABOUR_ACT = "श्रम ऐन, २०७४"
FEA_ACT = "वैदेशिक रोजगार ऐन, २०६४"
NI_ACT = "विनिमेय अधिकारपत्र ऐन, २०३४"

_DATE = F("doc_date", "Date", "मिति", "date",
          help_en="Picked as A.D., printed in B.S.", help_ne="ए.डी. मा चयन गर्नुहोस्; बि.सं. मा छापिन्छ")

# --------------------------------------------------------------------------
# सूचनाको हक - पुनरावेदन (आयोगमा)
# --------------------------------------------------------------------------

RTI_APPEAL = official(
    id="rti_appeal_commission",
    title_en="RTI appeal to the National Information Commission - पुनरावेदन",
    title_ne="सूचनाको हक: राष्ट्रिय सूचना आयोगमा पुनरावेदन",
    desc_en="Appeal (within 35 days) when a public body's head refuses information - the exact schedule form of the Right to Information Rules.",
    desc_ne="सार्वजनिक निकायको प्रमुखले सूचना दिन नमिल्ने गरी निर्णय गरेमा ३५ दिनभित्र आयोगमा दिने पुनरावेदन — सूचनाको हक सम्बन्धी नियमावलीको अनुसूची बमोजिमको ढाँचा।",
    category=OFFICE,
    law=RTI_RULES, law_en="Right to Information Rules, 2065", schedule="अनुसूची", relates_to="नियम ५ को उपनियम (१)",
    page=13, form_title="श्री राष्ट्रिय सूचना आयोगमा दिएको पुनरावेदन",
    keywords=("RTI", "right to information", "सूचनाको हक", "appeal", "पुनरावेदन", "information commission", "आयोग", "complaint"),
    provisions=[{"law_title_ne": RTI_ACT, "section": "10"}, {"law_title_ne": RTI_RULES, "section": "5"}],
    heading=False,
    fields=[
        F("via_office", "Filed through (office)", "मार्फत् (कार्यालय)"),
        F("appellant", "Appellant: name and address", "पुनरावेदकको नाम र ठेगाना", required=True),
        F("respondent", "Respondent: public body", "प्रत्यर्थी (सार्वजनिक निकाय)", required=True),
        F("subject", "Subject", "विषय", required=True),
        F("body_name", "Public body (name)", "सार्वजनिक निकायको नाम"),
        F("head", "Head of the public body", "प्रमुखको नाम"),
        F("decision_date", "Date of the head's decision", "निर्णय गरेको मिति", "date"),
        F("info", "Information requested", "माग गरेको सूचनाको विषय", required=True),
        F("grounds", "Grounds and reasons (one per line)", "आधार र कारण (एक पङ्क्तिमा एउटा)", "textarea", required=True),
        F("attachments", "Other attachments (one per line)", "अन्य संलग्न कागजात (एक पङ्क्तिमा एउटा)", "textarea"),
        F("sign_name", "Appellant's name (signature)", "पुनरावेदकको नाम (सही)"),
        _DATE,
    ],
    body="""
@cb श्री राष्ट्रिय सूचना आयोगमा दिएको
@cbu पुनरावेदन
@l,+ मार्फत् {{ via_office|blank(12) }} कार्यालय
@r {{ appellant|blank(20) }} पुनरावेदक
@cu विरुद्ध
@r {{ respondent|blank(20) }} प्रत्यर्थी
@c विपक्षी
@c,+ विषयः {{ subject|blank(12) }}
@j,+ {{ body_name|blank(10) }} सार्वजनिक निकायको प्रमुख श्री {{ head|blank(10) }} ले मिति {{ decision_date|bs|blank(6) }} मा मलाई/हामीलाई {{ info|blank(8) }} विषयको सूचना दिन नमिल्ने गरी निर्णय गरेकोमा देहायको आधार र कारणबाट मलाई/ हामीलाई सो निर्णयमा चित्त नबुझेको हुँदा ऐनको म्याद पैंतीस दिनभित्र यो पुनरावेदन गर्दछु/गर्दछौँ।
@l,>1,each=grounds:4 ({{ ka }})|{{ item }}
@l माथि लेखिएको व्यहोरा ठीक साँचो हो, झुट्ठा ठहरे कानून बमोजिम सहुँला बुझाउँला।
@u,+ संलग्न कागजात
@l,>1 (क)|सार्वजनिक निकायको प्रमुखले गरेको निर्णयको प्रतिलिपि।
@l,>1,each=attachments:2 ({{ ka_next }})|{{ item }}
@r,+ पुनरावेदकको सही{% if sign_name %} : {{ sign_name }}{% endif %}
@l {{ signoff(doc_date, 'संवत्') }}
""",
)

# --------------------------------------------------------------------------
# सूचना माग निवेदन (standard)
# --------------------------------------------------------------------------

RTI_REQUEST = standard(
    id="rti_request",
    title_en="RTI request to a public body - सूचना माग निवेदन",
    title_ne="सूचनाको हक: सूचना माग गर्ने निवेदन",
    desc_en="A written request to a public body's information officer under Section 7 of the Right to Information Act. Standard format - the Act asks for a written application stating the reason but attaches no form.",
    desc_ne="सूचनाको हक सम्बन्धी ऐन, २०६४ को दफा ७ बमोजिम सार्वजनिक निकायको सूचना अधिकारीलाई दिने सूचना माग निवेदन। मानक ढाँचा — ऐनले कारण खुलाई लिखित निवेदन दिन भनेको छ तर अनुसूचीमा ढाँचा तोकेको छैन।",
    category=OFFICE,
    basis_law=RTI_ACT,
    basis_note={
        "en": "RTI Act, 2064, s.7(1): a Nepali citizen applies in writing to the information officer stating why the information is needed; "
              "s.7(2): the officer must give it at once, or within 15 days; Rules 4: fee Rs 5 per page, first 10 pages free.",
        "ne": "सूचनाको हक सम्बन्धी ऐन, २०६४ को दफा ७(१): नेपाली नागरिकले कारण खुलाई सूचना अधिकारी समक्ष निवेदन दिनु पर्ने; दफा ७(२): "
              "तत्काल वा १५ दिनभित्र सूचना दिनु पर्ने; नियमावली नियम ४: प्रति पृष्ठ रु ५, दश पृष्ठसम्म निःशुल्क।",
    },
    provisions=[{"law_title_ne": RTI_ACT, "section": "7"}, {"law_title_ne": RTI_RULES, "section": "4"}],
    keywords=("RTI", "right to information", "सूचनाको हक", "information request", "सूचना माग", "public body", "सूचना अधिकारी"),
    fields=[
        F("office", "Public body / office", "सार्वजनिक निकाय / कार्यालय", required=True),
        F("info", "Information you want (describe precisely)", "माग गरेको सूचनाको विवरण", "textarea", required=True),
        F("period", "Period the information relates to", "सूचनासँग सम्बन्धित अवधि"),
        F("reason", "Why you need it (required by s.7(1))", "सूचना प्राप्त गर्नु पर्ने कारण", "textarea", required=True),
        SELECT("form", "Form you want it in", "सूचना प्राप्त गर्न चाहेको स्वरूप", ["प्रतिलिपि (फोटोकपी)", "अध्ययन/अवलोकन", "विद्युतीय माध्यम (इमेल/सीडी)"]),
        F("applicant", "Your full name", "निवेदकको पूरा नाम", required=True),
        F("citizenship_no", "Citizenship no.", "नागरिकता नं."),
        F("address", "Address", "ठेगाना", required=True),
        F("contact", "Phone / email", "फोन / इमेल"),
        _DATE,
    ],
    body="""
@r मितिः {{ doc_date|bs|blank(6) }}
@l,+ श्री सूचना अधिकारी ज्यू,
@l {{ office|blank(12) }}
@cbu,+ विषयः सूचना उपलब्ध गराई दिने बारे ।
@j उपर्युक्त सम्बन्धमा सूचनाको हक सम्बन्धी ऐन, २०६४ को दफा ७ बमोजिम देहायको सूचना प्राप्त गर्न यो निवेदन दिएको छु ।
@j १.|माग गरेको सूचनाको विवरणः {{ info }}
@j २.|सूचनासँग सम्बन्धित अवधिः {{ period|blank(8) }}
@j ३.|सूचना प्राप्त गर्नु पर्ने कारणः {{ reason }}
@j ४.|सूचना प्राप्त गर्न चाहेको स्वरूपः {{ form|blank(8) }}
@j ५.|सूचनाको हक सम्बन्धी नियमावली, २०६५ को नियम ४ बमोजिम लाग्ने दस्तुर बुझाउन म तयार छु ।
@j माथि लेखिएको व्यहोरा ठीक साँचो हो, झुट्ठा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
@r,+ निवेदक
@r नामः {{ applicant }}
@r नागरिकता नं.: {{ citizenship_no|nd|blank(6) }}
@r ठेगानाः {{ address }}
@r सम्पर्कः {{ contact|nd|blank(6) }}
@r सही: ………………………
""",
    body_en="""
@r Date: {{ doc_date|bs|blank(6) }}
@l,+ To: The Information Officer,
@l {{ office|blank(12) }}
@cbu,+ Subject: Request for information under the Right to Information Act, 2064
@j Under Section 7 of the Right to Information Act, 2064 I request the following information:
@j 1.|Information requested: {{ info }}
@j 2.|Period the information relates to: {{ period|blank(8) }}
@j 3.|Why I need the information (Section 7(1)): {{ reason }}
@j 4.|Form in which I want it: {{ form|blank(8) }}
@j 5.|I am ready to pay the fee under Rule 4 of the Right to Information Rules, 2065 (Rs 5 per page; up to 10 pages free).
@j The statements above are true; if found false I will be liable under law.
@r,+ Applicant
@r Name: {{ applicant }}
@r Citizenship no.: {{ citizenship_no|blank(6) }}
@r Address: {{ address }}
@r Contact: {{ contact|blank(6) }}
@r Signature: ………………………
@i,+ (English text is an unofficial convenience rendering; the Act prescribes no form.)
""",
)

# --------------------------------------------------------------------------
# उपभोक्ता उजुरी - अनुसूची–९ (नियम २९ को उपनियम (१) र नियम ३० को उपनियम (४))
# --------------------------------------------------------------------------

_CONSUMER_NE = """
@l श्री केन्द्रीय बजार अनुगमन समिति/
@l वाणिज्य, आपूर्ति तथा उपभोक्ता हित संरक्षण विभाग/
@l निरीक्षण अधिकृत ।
@j,+ {{ seller_district|blank(6) }} जिल्ला, {{ seller_local|blank(6) }} नगरपालिका/गाउँपालिका वडा नं. {{ seller_ward|nd|blank(4) }} टोलः {{ seller_tole|blank(6) }} मार्ग {{ seller_road|blank(6) }} स्थित {{ seller_kind|default('वस्तु उत्पादक/ वितरक/विक्रेता/सेवा प्रदायक', true) }} श्री {{ seller_name|blank(8) }} (व्यक्ति वा संस्थाको नाम) ले उपभोक्ता संरक्षण ऐन,२०७५ तथा उपभोक्ता संरक्षण नियमावली, २०७६ विपरीत हुने गरी देहाय बमोजिमको कार्य गरेको हुनाले निजलाई कानून बमोजिम कारबाही हुनको लागि यो उजुरी गरेको/लेखाई दिएको छु । उजुरीमा उल्लेख गरेको व्यहोरा मैले जाने बुझेसम्म साँचो छ ।
@l १.|उजुरी कर्ताको नाम, थरः {{ complainant_name }}
@l २.|ठेगाना र सम्पर्क नम्बरः {{ complainant_address }}, {{ complainant_phone|nd }}
@l ३.|उजुरीको संक्षिप्त व्यहोराः
@l,>1 (वस्तु विक्रेता वा सेवा प्रदायकले गरेको त्रुटि वा काम कारवाहीबाट उपभोक्तालाई भएको/हुन सक्ने हानी, नोक्सानी वा क्षतिको संक्षिप्त विवरण उल्लेख गर्ने)
@j,>1 {{ product_or_service }}{% if purchase_date %} (किनेको मिति: {{ purchase_date|bs }}){% endif %}{% if amount_involved %} रु. {{ amount_involved|nd }} तिरेको{% endif %}। {{ complaint_details }}{% if relief_sought %} माग: {{ relief_sought }}{% endif %}
@table 8,8 none
| उजुरी दर्ता मितिः {{ reg_date|bs }} | उजुरीकर्ताको दस्तखतः |
@end
@l ४.|मौखिक वा कुनै माध्यमबाट उजुरी प्राप्त भएको भए सो टिपोट गर्नेको नाम, थर र दस्तखतः
@l ५.|उजुरी प्राप्त भएको व्यहोरा प्रमाणित गर्ने अधिकारीको नाम, थर, दर्जा र प्रमाणित गरेको मितिः
@l,>1 मौखिक उजुरीकर्ताको दस्तखत (उपलब्ध भएमा).......
"""

_CONSUMER_EN = """
@l To: Central Market Monitoring Committee /
@l Department of Commerce, Supplies and Consumer Protection /
@l Inspection Officer
@j,+ I hereby lodge this complaint against {{ seller_name|blank(8) }} ({{ seller_kind|default('producer / distributor / seller / service provider', true) }}), located at {{ seller_tole|blank(6) }}, ward {{ seller_ward|blank(3) }}, {{ seller_local|blank(6) }}, {{ seller_district|blank(6) }} district, for acting contrary to the Consumer Protection Act, 2075 and the Consumer Protection Rules, 2076, so that action may be taken under law. What is stated here is true to the best of my knowledge.
@l 1.|Complainant's name: {{ complainant_name }}
@l 2.|Address and contact number: {{ complainant_address }}, {{ complainant_phone }}
@l 3.|Brief description of the complaint (the fault or conduct of the seller / service provider and the harm, loss or damage caused or likely to be caused to the consumer):
@j,>1 {{ product_or_service }}{% if purchase_date %} (purchased on {{ purchase_date }}){% endif %}{% if amount_involved %}, NPR {{ amount_involved }} paid{% endif %}. {{ complaint_details }}{% if relief_sought %} Relief sought: {{ relief_sought }}{% endif %}
@l,+ Date of registration of the complaint: {{ reg_date|blank(6) }}
@r Complainant's signature: ....................
@l 4.|If received orally or by another means, name, surname and signature of the person noting it down:
@l 5.|Name, surname, rank and date of certification of the officer certifying the complaint received:
@l,>1 Signature of the oral complainant (if available): .......
@i,+ (English text is an unofficial convenience rendering of the prescribed Nepali form.)
"""

CONSUMER_COMPLAINT = official(
    id="consumer_complaint",
    title_en="Consumer complaint (prescribed form) - उपभोक्ता उजुरी",
    title_ne="उपभोक्ता उजुरी (तोकिएको ढाँचा)",
    desc_en="A complaint about a defective product, unfair trade practice or poor service, in the exact form of Schedule 9 of the Consumer Protection Rules, 2076 (the English text is an unofficial rendering).",
    desc_ne="बिग्रेको सामान, अनुचित व्यापारिक क्रियाकलाप वा सेवाको गुनासो — उपभोक्ता संरक्षण नियमावली, २०७६ को अनुसूची–९ बमोजिमको उजुरीको ढाँचा।",
    category=OFFICE,
    law=CONSUMER_RULES, law_en="Consumer Protection Rules, 2076", schedule="अनुसूची–९",
    relates_to="नियम २९ को उपनियम (१) र नियम ३० को उपनियम (४)", page=30, form_title="उजुरीको ढाँचा",
    keywords=("consumer", "उपभोक्ता", "complaint", "उजुरी", "defective", "बिग्रेको", "refund", "shop", "पसल", "market monitoring"),
    provisions=[{"law_title_ne": CONSUMER_ACT, "section": "3"}, {"law_title_ne": CONSUMER_ACT, "section": "36"},
                {"law_title_ne": CONSUMER_ACT, "section": "50"}, {"law_title_ne": CONSUMER_RULES, "section": "29"}],
    fields=[
        F("complainant_name", "Your full name", "तपाईंको पूरा नाम", required=True),
        F("complainant_address", "Your address", "तपाईंको ठेगाना", required=True),
        F("complainant_phone", "Your phone number", "तपाईंको फोन नम्बर", required=True),
        F("seller_name", "Seller / business name", "पसल / व्यवसायको नाम", required=True),
        F("seller_address", "Seller's address (one line; or fill the boxes below)", "पसलको ठेगाना (एक लाइनमा; वा तलका खण्ड भर्नुहोस्)", required=True),
        F("seller_district", "Seller: district", "जिल्ला"), F("seller_local", "Seller: municipality / rural municipality", "नगरपालिका/गाउँपालिका"),
        F("seller_ward", "Seller: ward no.", "वडा नं."), F("seller_tole", "Seller: tole", "टोल"), F("seller_road", "Seller: road", "मार्ग"),
        SELECT("seller_kind", "Seller is a", "वस्तु उत्पादक/वितरक/विक्रेता/सेवा प्रदायक",
               ["वस्तु उत्पादक", "वितरक", "विक्रेता", "सेवा प्रदायक"]),
        F("product_or_service", "Product or service involved", "सम्बन्धित वस्तु वा सेवा", required=True),
        F("purchase_date", "Date of purchase", "किनेको मिति", "date", required=True),
        F("amount_involved", "Amount paid (NPR)", "तिरेको रकम (रु.)", "number", required=True),
        F("complaint_details", "What went wrong", "के समस्या भयो", "textarea", required=True),
        F("relief_sought", "What you want done about it", "के समाधान चाहनुहुन्छ", "textarea", required=True),
        F("reg_date", "Complaint registration date (office fills)", "उजुरी दर्ता मिति (कार्यालयले भर्ने)", "date"),
    ],
    body=_CONSUMER_NE, body_en=_CONSUMER_EN,
)

# --------------------------------------------------------------------------
# घरेलु हिंसा उजुरी - अनुसूची–१ (नियम ३ को उपनियम (१) र (२))
# --------------------------------------------------------------------------

DV_COMPLAINT = official(
    id="domestic_violence_complaint",
    title_en="Domestic-violence complaint - घरेलु हिंसा उजुरी",
    title_ne="घरेलु हिंसा सम्बन्धी उजुरी",
    desc_en="Complaint by a victim (or someone on their behalf) of domestic violence, in the exact form of Schedule 1 of the Domestic Violence Rules, 2067.",
    desc_ne="घरेलु हिंसा (कसूर र सजाय) नियमावली, २०६७ को अनुसूची–१ (नियम ३) बमोजिम घरेलु हिंसाको उजुरीको ढाँचा।",
    category=OFFICE,
    law=DV_RULES, law_en="Domestic Violence (Offence and Punishment) Rules, 2067", schedule="अनुसूची–१",
    relates_to="नियम ३ को उपनियम (१) र (२)", page=9, form_title="उजुरीको ढाँचा",
    keywords=("domestic violence", "घरेलु हिंसा", "abuse", "complaint", "उजुरी", "victim", "पीडित", "women", "violence"),
    provisions=[{"law_title_ne": "घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६", "section": "12ग"}, {"law_title_ne": DV_RULES, "section": "3"}],
    fields=[
        F("to_office", "Submitted to (office / body)", "श्री ... मा चढाएको (कार्यालय/निकाय)", required=True),
        F("v_district", "Complainant: district", "उजुरवालाको जिल्ला"), F("v_local", "Complainant: गा.वि.स./न.पा.", "गा.वि.स./न.पा."),
        F("v_ward", "Complainant: ward no.", "वडा नं."), F("v_tole", "Complainant: tole / address", "टोल / ठेगाना"),
        F("v_age", "Complainant: age", "उमेर", "number"), F("v_name", "Complainant: full name", "उजुरवालाको पूरा नाम", required=True),
        F("o_district", "Person complained against: district", "विपक्षीको जिल्ला"), F("o_local", "Person complained against: गा.वि.स./न.पा.", "गा.वि.स./न.पा."),
        F("o_ward", "Person complained against: ward no.", "वडा नं."), F("o_tole", "Person complained against: tole / address", "टोल / ठेगाना"),
        F("o_age", "Person complained against: age", "उमेर", "number"), F("o_name", "Person complained against: full name", "विपक्षीको पूरा नाम", required=True),
        F("place", "1(a). Place where the violence happened / is happening", "१(क). घरेलु हिंसा भएको भइरहेको वा हुन लागेको ठाउँ"),
        F("when", "1(b). Date", "१(ख). मिति", "date"), F("time", "1(c). Time", "१(ग). समय"),
        SELECT("physical", "2(a). Physical abuse", "२(क). शारीरिक यातना", ["छ", "छैन"]),
        SELECT("mental", "2(b). Mental abuse", "२(ख). मानसिक यातना", ["छ", "छैन"]),
        SELECT("sexual", "2(c). Sexual abuse", "२(ग). यौनजन्य यातना", ["छ", "छैन"]),
        SELECT("economic", "2(d). Economic abuse", "२(घ). आर्थिक यातना", ["छ", "छैन"]),
        F("other_kind", "2(e). Other", "२(ङ). अन्य"),
        F("effect", "3. Effect on the victim", "३. घरेलु हिंसाबाट पीडितलाई पर्न गएको असर", "textarea", required=True),
        F("others", "4. Other persons who saw or know of it (one per line: name, address)", "४. उजुरीवाला बाहेक घरेलु हिंसा भएको देख्ने वा थाहा पाउने अन्य व्यक्ति (नाम, ठेगाना) (एक पङ्क्तिमा एक जना)", "textarea"),
        F("evidence", "5. Any evidence", "५. कुनै सबुत प्रमाण भए सो कुरा", "textarea"),
        F("other_body", "6. If complained to another body: its name and the date", "६. अन्य उजुरी सुन्ने निकायमा उजुरी गरेको भए सो निकायको नाम र उजुरी गरेको मिति"),
        F("sign_name", "Name (signature block)", "नाम"), F("sign_addr", "Address (signature block)", "ठेगाना"),
        F("sign_date", "Date", "मिति", "date"),
    ],
    body="""
@c श्री {{ to_office|blank(12) }} मा चढाएको
@c,+ उजुरी
@j,+ जिल्ला {{ v_district|blank(8) }} गा.वि.स./न.पा {{ v_local|blank(6) }} वडा नं. {{ v_ward|nd|blank(4) }} {{ v_tole|blank(8) }} वस्ने वर्ष {{ v_age|nd|blank(4) }} को {{ v_name|blank(10) }} ले मलाई/ जिल्ला {{ o_district|blank(8) }} गा.वि.स./न.पा. {{ o_local|blank(6) }} वडा नं. {{ o_ward|nd|blank(4) }} {{ o_tole|blank(8) }} वस्ने वर्ष {{ o_age|nd|blank(4) }} को {{ o_name|blank(10) }} लाई घरेलु हिंसा सम्बन्धी कसूर गरेकोले आवश्यक कानूनी कारबाहीको लागि देहायको विवरण खुलाई यो उजुरी गरेको छु ।
@l १.|घरेलु हिंसा भएको भैरहेको वा हुन लागेकोः
@l,>1 (क)|ठाउँः {{ place }}
@l,>1 (ख)|मितिः {{ when|bs }}
@l,>1 (ग)|समयः {{ time|nd }}
@l २.|घरेलु हिंसाको प्रकृतिः
@l,>1 (क)|शारीरिक यातना {{ physical }}
@l,>1 (ख)|मानसिक यातना {{ mental }}
@l,>1 (ग)|यौनजन्य यातना {{ sexual }}
@l,>1 (घ)|आर्थिक यातना {{ economic }}
@l,>1 (ङ)|अन्य {{ other_kind }}
@l ३.|घरेलु हिंसाबाट पीडितलाई पर्न गएको असरः {{ effect }}
@l ४.|उजुरीवाला बाहेक घरेलु हिंसा भएको देख्ने वा थाहा पाउने अन्य व्यक्ति भए निजको नाम, ठेगानाः
@l,>1,each=others:3 ({{ ka }})|{{ item }}
@l ५.|कुनै सबुत प्रमाण भए सो कुराः- {{ evidence }}
@l ६.|अन्य उजुरी सुन्ने निकायमा उजुरी गरेको भए सो निकायको नाम र उजुरी गरेको मितिः {{ other_body }}
@l ७.|माथि लेखिएको व्यहोरा ठीक साँचो छ, झुट्टा ठहरे कानून बमोजिम सहने बुझाउने छु ।
@l,>1,+ उजुरी दिनेको,
@l,>1 दस्तखतः
@l,>1 नामः {{ sign_name }}
@l,>1 ठेगानाः {{ sign_addr }}
@l,>1 मितिः {{ sign_date|bs }}
""",
)

TEMPLATES = [RTI_APPEAL, RTI_REQUEST, CONSUMER_COMPLAINT, DV_COMPLAINT]
