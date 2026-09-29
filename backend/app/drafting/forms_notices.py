"""Notices to the local registrar of vital events, transcribed from the
schedules of the जन्म, मृत्यु तथा अन्य व्यक्तिगत घटना (दर्ता गर्ने) नियमावली, २०३४
(Births, Deaths and Other Personal Events (Registration) Rules):

  अनुसूची–२  जन्मको सूचना फाराम          अनुसूची–५  सम्बन्ध विच्छेदको सूचना फाराम
  अनुसूची–३  मृत्युको सूचना फाराम         अनुसूची–६  बसाइँ सराईको लगत हस्तान्तरण फाराम
  अनुसूची–४  विवाहको सूचना फाराम

plus standard-format complaints that have no schedule: labour complaint,
foreign-employment complaint and a dishonoured-cheque claim.

The forms are field-heavy: check-boxes are printed as ☐ / ☒ from select
fields, the informant's thumbprint boxes (दायाँ / बायाँ) and the marriage
photo boxes are real tables.
"""
from __future__ import annotations

from .dsl import F, SELECT
from .forms_common import PERSONAL_EVENTS_RULES, official

NOTICES = "notices"
OFFICE = "office"
COURT = "court"

_OFFICE_FIELDS = [
    F("o_ward", "Registrar's office: ward no.", "स्थानीय पञ्जीकाधिकारीको कार्यालय: वडा नं."),
    F("o_local", "Municipality / rural municipality", "गा.पा./न.पा."),
    F("o_district", "District", "जिल्ला"), F("o_province", "Province", "प्रदेश"),
]

_HEADER = """
@i (सूचकले भर्ने)
@l श्री स्थानीय पञ्जीकाधिकारीज्यू,
@l वडा नं. {{ o_ward|nd|blank(4) }} , {{ o_local|blank(8) }} गा. पा. / न.पा.
@l {{ o_district|blank(8) }} जिल्ला, {{ o_province|blank(8) }} प्रदेश
@l,+ महोदय,
"""

_SEX = ["पुरुष", "महिला", "अन्य"]


def _name3(prefix: str, en: str, ne: str, required: bool = False) -> list:
    return [
        F(f"{prefix}_first", f"{en}: first name", f"{ne}: पहिलो नाम", required=required),
        F(f"{prefix}_mid", f"{en}: middle name", f"{ne}: बीचको नाम"),
        F(f"{prefix}_last", f"{en}: surname", f"{ne}: थर", required=required),
        F(f"{prefix}_en", f"{en}: full name in English", f"{ne}: अङ्ग्रेजीमा पूरा नाम"),
    ]


def _name3_lines(prefix: str, indent: float = 0) -> str:
    return (
        f"@l,>{indent} पहिलो नाम {{{{ {prefix}_first|blank(4) }}}}   बीचको नाम {{{{ {prefix}_mid|blank(4) }}}}   थर {{{{ {prefix}_last|blank(4) }}}}\n"
        f"@l,>{indent} First Name / Middle Name / Surname : {{{{ {prefix}_en|blank(8) }}}}\n"
    )


def _addr(prefix: str, en: str, ne: str) -> list:
    return [
        F(f"{prefix}_prov", f"{en}: province", f"{ne}: प्रदेश"), F(f"{prefix}_local", f"{en}: municipality / rural municipality", f"{ne}: गा.पा./न.पा."),
        F(f"{prefix}_ward", f"{en}: ward no.", f"{ne}: वडा नं."), F(f"{prefix}_road", f"{en}: road", f"{ne}: सडक/मार्ग"),
        F(f"{prefix}_tole", f"{en}: village / tole", f"{ne}: गाउँ/टोल"), F(f"{prefix}_house", f"{en}: house no.", f"{ne}: घर नं."),
    ]


def _addr_lines(prefix: str, indent: float = 0) -> str:
    return (
        f"@l,>{indent} प्रदेश {{{{ {prefix}_prov|blank(4) }}}}   गा.पा./न.पा. {{{{ {prefix}_local|blank(4) }}}}   वडा नं. {{{{ {prefix}_ward|nd|blank(3) }}}}\n"
        f"@l,>{indent} सडक/मार्ग {{{{ {prefix}_road|blank(4) }}}}   गाउँ/टोल {{{{ {prefix}_tole|blank(4) }}}}   घर नं. {{{{ {prefix}_house|nd|blank(3) }}}}\n"
    )


_INFORMANT_FIELDS = [
    *_name3("inf", "Informant", "सूचक", required=True),
    F("inf_rel", "Informant's relation to the person", "सँगको नाता"),
    F("inf_cit", "Informant's citizenship certificate / ID no.", "नागरिकता प्रमाणपत्र नं./ परिचय पत्र नं."),
    F("inf_passport", "If a foreigner: passport no. and issuing country", "विदेशी भएमा राहदानी नं. र जारी गर्ने देश"),
    F("form_date", "Date the form was filled", "फाराम भरेको मिति", "date"),
]


def _informant_block(who: str) -> str:
    return (
        "@l,+ यसमा लेखिएको विवरण साँचो हो। झुट्ठा ठहरे कानून बमोजिम सहुँला बुझाउँला भनी सहीछाप गर्ने सूचकको विवरण :\n"
        + _name3_lines("inf")
        + f"@l {who}सँगको नाता {{{{ inf_rel|blank(6) }}}}\n"
        "@l नागरिकता प्रमाणपत्र नं./ परिचय पत्र नं. {{ inf_cit|nd|blank(6) }}\n"
        "@l विदेशी भएमा राहदानी नं. र जारी गर्ने देशको नाम {{ inf_passport|blank(6) }}\n"
        "@l फाराम भरेको मिति (साल-महिना-गते) {{ form_date|bs|blank(6) }}\n"
    )


_REGISTRAR_BLOCK = """
@l,+ (स्थानीय पञ्जीकाधिकारीले भर्ने)
@l स्थानीय पञ्जीकाधिकारीको नाम ……………………
@l कर्मचारी सङ्केत नं./ परिचय नं. ……………………
@l फाराम दर्ता नं. ……………………
@l फाराम दर्ता मिति ……………………
@l परिवारको लगत नं. ……………………
@l कार्यालय (गाउँपालिका/नगरपालिका/वडा नं.) ……………………
"""


# --------------------------------------------------------------------------
# जन्मको सूचना फाराम - अनुसूची–२
# --------------------------------------------------------------------------

BIRTH = official(
    id="birth_registration_notice",
    title_en="Birth registration notice - जन्मको सूचना फाराम",
    title_ne="जन्म दर्ता: जन्मको सूचना फाराम",
    desc_en="Notice of a birth to the local registrar (ward office), in the exact form of Schedule 2 of the Personal Events Registration Rules.",
    desc_ne="स्थानीय पञ्जीकाधिकारी (वडा कार्यालय) लाई दिने जन्मको सूचना फाराम — जन्म, मृत्यु तथा अन्य व्यक्तिगत घटना (दर्ता गर्ने) नियमावलीको अनुसूची–२।",
    category=NOTICES,
    law=PERSONAL_EVENTS_RULES, law_en="Births, Deaths and other Personal Events (Registration) Rules, 2034", schedule="अनुसूची–२",
    relates_to="नियम ५", page=9, form_title="जन्मको सूचना फाराम",
    keywords=("birth", "जन्म", "registration", "दर्ता", "newborn", "birth certificate", "जन्म दर्ता", "ward office", "वडा"),
    fields=_OFFICE_FIELDS + [
        *_name3("c", "Child", "शिशु", required=True),
        F("c_bs", "Date of birth", "जन्म मिति", "date", required=True),
        SELECT("c_place", "Place of birth", "शिशु जन्मेको ठाउँ", ["घर", "स्वास्थ्य संस्था", "अस्पताल", "अन्य"]),
        SELECT("c_sex", "Sex", "लिङ्ग", _SEX),
        *_addr("cb", "Birthplace", "जन्मेको ठेगाना"),
        F("c_abroad_ne", "If born abroad: address (in Nepali)", "विदेशमा जन्मेको भए ठेगाना (नेपालीमा: देश, प्रदेश, स्थानीय ठेगाना)"),
        F("c_abroad_en", "If born abroad: address (in English)", "विदेशमा जन्मेको भए ठेगाना (In English)"),
        SELECT("c_kind", "Type of birth", "जन्मको किसिम", ["एकल", "जुम्ल्याहा", "तिम्ल्याहा वा सो भन्दा बढी"]),
        F("c_weight", "Birth weight (grams)", "शिशु जन्मदाको तौल (ग्राममा)", "number"),
        SELECT("c_helper", "Who assisted at birth", "शिशु जन्मदा मद्दत गर्ने व्यक्ति",
               ["डाक्टर", "नर्स/अनमी", "परम्परागत सुडिनी", "तालिम प्राप्त सुडिनी", "घरपरिवारका सदस्य", "अन्य"]),
        F("c_helper_other", "Helper (if other)", "अन्य भए खुलाउने"),
        F("c_disability", "Disability (if any)", "अपाङ्गता (भएमा खुलाउने)"),
        *_name3("gf", "Grandfather", "बाजे"),
        *_name3("fa", "Father", "बाबु"), *_name3("mo", "Mother", "आमा"),
        *_addr("fa", "Father", "बाबुको स्थायी ठेगाना"), *_addr("mo", "Mother", "आमाको स्थायी ठेगाना"),
        F("fa_id", "Father: ID / citizenship no.", "बाबु: परिचय पत्र नं./नागरिकता नं."), F("mo_id", "Mother: ID / citizenship no.", "आमा: परिचय पत्र नं./नागरिकता नं."),
        F("fa_passport", "Father: passport no. and country", "बाबु: विदेशी भए राहदानी नं. र देश"), F("mo_passport", "Mother: passport no. and country", "आमा: विदेशी भए राहदानी नं. र देश"),
        F("marriage_no", "Marriage registration no.", "विवाह दर्ता नं."), F("marriage_date", "Date of marriage", "विवाह भएको मिति", "date"),
        F("fa_bs", "Father: date of birth", "बाबु: जन्म मिति", "date"), F("mo_bs", "Mother: date of birth", "आमा: जन्म मिति", "date"),
        F("fa_edu", "Father: education", "बाबु: शैक्षिक स्तर"), F("mo_edu", "Mother: education", "आमा: शैक्षिक स्तर"),
        F("fa_job", "Father: occupation", "बाबु: पेशा"), F("mo_job", "Mother: occupation", "आमा: पेशा"),
        F("fa_religion", "Father: religion", "बाबु: धर्म"), F("mo_religion", "Mother: religion", "आमा: धर्म"),
        F("fa_caste", "Father: caste / ethnicity", "बाबु: जातजाति"), F("mo_caste", "Mother: caste / ethnicity", "आमा: जातजाति"),
        *_INFORMANT_FIELDS,
    ],
    body=_HEADER + """
@j निम्न लिखित विवरण खुलाई नवजात शिशु जन्मको सूचना दिन आएको छु । कानून अनुसार जन्म दर्ता गरी पाऊँ ।
@b,+ १. नवजात शिशुको विवरण
""" + _name3_lines("c", 0.5) + """
@l,>0.5 जन्म मिति: वि.सं. मा (साल-महिना-गते) {{ c_bs|bs|blank(4) }}   ई.सं. मा (गते-महिना-साल) {{ c_bs|ad|blank(4) }}
@l,>0.5 शिशु जन्मेको ठाउँ: {{ opts(c_place, ['घर', 'स्वास्थ्य संस्था', 'अस्पताल', 'अन्य']) }}
@l,>0.5 लिङ्ग: {{ opts(c_sex, ['पुरुष', 'महिला', 'अन्य']) }}
@l,>0.5 शिशु जन्मेको ठेगाना
""" + _addr_lines("cb", 1) + """
@l,>0.5 विदेशमा जन्मेको भएमा ठेगाना (नेपालीमा: देश, प्रदेश, स्थानीय ठेगाना): {{ c_abroad_ne|blank(8) }}
@l,>0.5 विदेशमा जन्मेको भएमा ठेगाना (In English: District, Province/State, Local Address): {{ c_abroad_en|blank(8) }}
@l,>0.5 जन्मको किसिम: {{ opts(c_kind, ['एकल', 'जुम्ल्याहा', 'तिम्ल्याहा वा सो भन्दा बढी']) }}
@l,>0.5 शिशु जन्मदाको तौल: ग्राममा {{ c_weight|nd|blank(4) }}   {{ opts('', ['थाहा नभएको (तौल नलिएको)']) }}
@l,>0.5 शिशु जन्मदा मद्दत गर्ने व्यक्ति: {{ opts(c_helper, ['डाक्टर', 'नर्स/अनमी', 'परम्परागत सुडिनी', 'तालिम प्राप्त सुडिनी', 'घरपरिवारका सदस्य', 'अन्य']) }}{% if c_helper == 'अन्य' %} खुलाउने {{ c_helper_other|blank(6) }}{% endif %}
@l,>0.5 अपाङ्गता (भएमा खुलाउने) {{ c_disability|blank(6) }}
@b,+ २. नवजात शिशुको बाजेको विवरण
""" + _name3_lines("gf", 0.5) + """
@b,+ ३. नवजात शिशुको बाबु आमाको विवरण
@l,>0.5 बाबुको नाम: पहिलो नाम {{ fa_first|blank(4) }}   बीचको नाम {{ fa_mid|blank(4) }}   थर {{ fa_last|blank(4) }}
@l,>0.5 Father's Name: First Name / Middle Name / Surname : {{ fa_en|blank(8) }}
@l,>0.5 आमाको नाम: पहिलो नाम {{ mo_first|blank(4) }}   बीचको नाम {{ mo_mid|blank(4) }}   थर {{ mo_last|blank(4) }}
@l,>0.5 Mother's Name: First Name / Middle Name / Surname : {{ mo_en|blank(8) }}
@table 4.6,5.6,5.6 all
| @b स्थायी ठेगाना | @b बाबुको विवरण | @b आमाको विवरण |
| प्रदेश | {{ fa_prov }} | {{ mo_prov }} |
| गा.पा./न.पा. | {{ fa_local }} | {{ mo_local }} |
| वडा नं. | {{ fa_ward|nd }} | {{ mo_ward|nd }} |
| सडक/मार्ग | {{ fa_road }} | {{ mo_road }} |
| गाउँ / टोल | {{ fa_tole }} | {{ mo_tole }} |
| घर नं. | {{ fa_house|nd }} | {{ mo_house|nd }} |
| परिचय पत्र नं./ नागरिकता नं. | {{ fa_id|nd }} | {{ mo_id|nd }} |
| विदेशी भएमा पासपोर्ट नं. र देशको नाम | {{ fa_passport|nd }} | {{ mo_passport|nd }} |
| विवाह दर्ता नं. | {{ marriage_no|nd }} | {{ marriage_no|nd }} |
| विवाह भएको मिति<br>वि.सं. मा (साल-महिना-गते):<br>ई.सं. मा (गते-महिना-साल): | {{ marriage_date|bs }}<br>{{ marriage_date|ad }} | {{ marriage_date|bs }}<br>{{ marriage_date|ad }} |
| जन्म मिति<br>वि.सं. मा (साल-महिना-गते):<br>ई.सं. मा (गते-महिना-साल): | {{ fa_bs|bs }}<br>{{ fa_bs|ad }} | {{ mo_bs|bs }}<br>{{ mo_bs|ad }} |
| शैक्षिक स्तर | {{ fa_edu }} | {{ mo_edu }} |
| पेशा | {{ fa_job }} | {{ mo_job }} |
| धर्म | {{ fa_religion }} | {{ mo_religion }} |
| जातजाति | {{ fa_caste }} | {{ mo_caste }} |
@end
""" + _informant_block("नवजात शिशु") + """
@thumbs label=बाबुको सहीछाप
@thumbs label=आमाको सहीछाप
""" + _REGISTRAR_BLOCK + """
@b,+ संलग्न गर्नुपर्ने कागजात
@l १.|बाबु वा आमाको नागरिकताको प्रतिलिपि;
@l २.|स्वास्थ्य संस्था/अस्पतालमा जन्म भएको भए उक्त संस्थाबाट जारी जन्म प्रतिवेदन;
@l ३.|घरमा जन्म भएको भए पछिल्लो खोप दिएको प्रमाण;
@l ४.|अस्पताल वा खोपको प्रमाण नभएमा जन्म दर्ता गर्नुपर्ने व्यक्ति स्वयंलाई उपस्थित गराउने वा सम्बन्धित वडाबाट जन्म दर्ता गर्नु पर्ने व्यक्तिको जन्म प्रमाणित गरेको कागज;
@l ५.|विदेशी भएमा बाबु, आमाको राहदानी प्रमाणपत्रको प्रतिलिपि तथा सम्बन्धित स्थानीय तहको वडामा बसोबास रहेको प्रमाण;
@l ६.|भारतीय भएमा भारतीय नागरिक भनी पहिचान खुल्ने प्रमाण;
@l ७.|बाबु बेपत्ता वा ठेगाना थाहा नभएको भए सो सम्बन्धमा प्रहरीको पत्र ।
""",
)

# --------------------------------------------------------------------------
# मृत्युको सूचना फाराम - अनुसूची–३
# --------------------------------------------------------------------------

DEATH = official(
    id="death_registration_notice",
    title_en="Death registration notice - मृत्युको सूचना फाराम",
    title_ne="मृत्यु दर्ता: मृत्युको सूचना फाराम",
    desc_en="Notice of a death to the local registrar (ward office), in the exact form of Schedule 3 of the Personal Events Registration Rules.",
    desc_ne="स्थानीय पञ्जीकाधिकारी (वडा कार्यालय) लाई दिने मृत्युको सूचना फाराम — जन्म, मृत्यु तथा अन्य व्यक्तिगत घटना (दर्ता गर्ने) नियमावलीको अनुसूची–३।",
    category=NOTICES,
    law=PERSONAL_EVENTS_RULES, law_en="Births, Deaths and other Personal Events (Registration) Rules, 2034", schedule="अनुसूची–३",
    relates_to="नियम ५", page=14, form_title="मृत्युको सूचना फाराम",
    keywords=("death", "मृत्यु", "registration", "दर्ता", "death certificate", "मृत्यु दर्ता", "ward office", "deceased"),
    fields=_OFFICE_FIELDS + [
        *_name3("d", "Deceased", "मृतक", required=True),
        F("d_id", "Deceased: ID no.", "परिचय पत्र नं."), SELECT("d_sex", "Sex", "लिङ्ग", _SEX),
        F("d_bs", "Date of birth", "जन्म मिति", "date"), F("d_death", "Date of death", "मृत्यु भएको मिति", "date", required=True),
        SELECT("d_place", "Place of death", "मृत्यु भएको स्थान", ["घर", "अस्पताल", "अन्य"]),
        SELECT("d_cert", "Death certified by a physician?", "मृत्यु चिकित्सकबाट प्रमाणित", ["छ", "छैन"]),
        F("d_cause", "Cause of death stated in the certificate", "यदि छ भने प्रमाणपत्रमा उल्लेख मृत्युको कारण"),
        F("d_death_addr", "Address where death occurred (country and local address if abroad)", "मृत्यु भएको ठेगाना (विदेशमा भएमा देश र स्थानीय ठेगाना)"),
        *_addr("da", "Deceased", "मृतकको ठेगाना"),
        F("d_cit", "Citizenship certificate no. / issuing district / issue date / ID no.", "नागरिकता प्रमाणपत्र नं./ जारी गर्ने जिल्ला/जारी मिति/परिचयपत्र नं."),
        F("d_passport", "If a foreigner: passport no., issuing country and date", "विदेशी भएमा राहदानी नं., जारी गर्ने देश र जारी मिति"),
        SELECT("d_marital", "Marital status before death", "पूर्व वैवाहिक स्थिति", ["विवाहित", "अविवाहित", "विधुवा/विदुर", "पारपाचुके", "छुट्टिएर बसेको"]),
        F("d_edu", "Education", "शैक्षिक स्तर"), F("d_job", "Occupation", "पेशा"), F("d_religion", "Religion", "धर्म"), F("d_caste", "Caste / ethnicity", "जातजाति"),
        *_name3("gf", "Grandfather", "बाजे"), *_name3("fa", "Father", "बाबु"), *_name3("mo", "Mother", "आमा"),
        F("spouses", "4. If married: names of spouse(s), incl. deceased (one per line: Nepali | English)",
          "४. मृतक विवाहित भएमा पति/पत्नीको नाम (मृत्यु भएकाको समेत) (एक पङ्क्तिमा: देवनागरी | English)", "textarea"),
        *_INFORMANT_FIELDS,
    ],
    body=_HEADER + """
@j निम्न लिखित विवरण खुलाई मृतकको सूचना दिन आएको छु । कानून अनुसार मृत्यु दर्ता गरी पाऊँ ।
@b,+ १. मृतकको विवरण
""" + _name3_lines("d", 0.5) + """
@l,>0.5 परिचय पत्र नं. {{ d_id|nd|blank(6) }}
@l,>0.5 लिङ्ग: {{ opts(d_sex, ['पुरुष', 'महिला', 'अन्य']) }}
@l,>0.5 जन्म मिति: वि.सं. मा (साल-महिना-गते) {{ d_bs|bs|blank(4) }}   ई.सं. मा (गते-महिना-साल) {{ d_bs|ad|blank(4) }}
@l,>0.5 मृत्यु भएको: वि.सं. मा (साल-महिना-गते) {{ d_death|bs|blank(4) }}   ई.सं. मा (गते-महिना-साल) {{ d_death|ad|blank(4) }}
@l,>0.5 मृत्यु भएको स्थान: {{ opts(d_place, ['घर', 'अस्पताल', 'अन्य']) }}
@l,>0.5 मृत्यु चिकित्सकबाट प्रमाणित {{ opts(d_cert, ['छ', 'छैन']) }}
@l,>0.5 यदि छ भने प्रमाणपत्रमा उल्लेख मृत्युको कारण {{ d_cause|blank(6) }}
@l,>0.5 मृत्यु भएको ठेगाना (विदेशमा भएमा देश र स्थानीय ठेगाना) {{ d_death_addr|blank(6) }}
@b,+ २. मृतकको ठेगाना
""" + _addr_lines("da", 0.5) + """
@b,+ ३. मृतकको अन्य विवरण
@l,>0.5 नागरिकता प्रमाणपत्र नं./ जारी गर्ने जिल्ला/जारी मिति/परिचयपत्र नं. {{ d_cit|nd|blank(6) }}
@l,>0.5 विदेशी भएमा राहदानी नं., जारी गर्ने देश र जारी मिति {{ d_passport|blank(6) }}
@l,>0.5 पूर्व वैवाहिक स्थिति: {{ opts(d_marital, ['विवाहित', 'अविवाहित', 'विधुवा/विदुर', 'पारपाचुके', 'छुट्टिएर बसेको']) }}
@l,>0.5 शैक्षिक स्तर {{ d_edu|blank(4) }}   पेशा {{ d_job|blank(4) }}   धर्म {{ d_religion|blank(4) }}   जातजाति {{ d_caste|blank(4) }}
@l,>0.5 बाजेको पहिलो नाम {{ gf_first|blank(3) }}   बीचको नाम {{ gf_mid|blank(3) }}   थर {{ gf_last|blank(3) }}
@l,>0.5 Grand Father's First Name / Middle Name / Surname : {{ gf_en|blank(8) }}
@l,>0.5 बाबुको पहिलो नाम {{ fa_first|blank(3) }}   बीचको नाम {{ fa_mid|blank(3) }}   थर {{ fa_last|blank(3) }}
@l,>0.5 Father's First Name / Middle Name / Surname : {{ fa_en|blank(8) }}
@l,>0.5 आमाको पहिलो नाम {{ mo_first|blank(3) }}   बीचको नाम {{ mo_mid|blank(3) }}   थर {{ mo_last|blank(3) }}
@l,>0.5 Mother's First Name / Middle Name / Surname : {{ mo_en|blank(8) }}
@b,+ ४. मृतक विवाहित भएमा
@l,>0.5 पति/पत्नी को नाम उल्लेख गर्ने । (मृत्यु भएकाको समेत)
@table 1.5,7,7 all
| @b क्र.सं. | @b नाम (देवनागरीमा) | @b Name (In English) |
@rows spouses:2
| {{ n|nd }} | {{ (item.split('|') + ['', ''])[0]|trim }} | {{ (item.split('|') + ['', ''])[1]|trim }} |
@end
@b,+ ५. सूचकको विवरण
""" + _informant_block("मृतक") + """
@l,+ सूचकको सहीछाप
@thumbs
@l,+ स्थानीय पञ्जीकाधिकारीले भर्ने :-
@b संलग्न गर्नुपर्ने कागजातहरू
@l १.|मृतकको नागरिकता प्रमाणपत्रको प्रतिलिपि (नागरिकता बनेको भएमा)
@l २.|सूचकको नागरिकता प्रमाणपत्रको प्रतिलिपि
@l ३.|विदेशी भएमा सूचक र मृतकको राहदानी, प्रवेशाज्ञा तथा निज त्यस वडामा बसोबास गरिरहेको प्रमाण
""" + _REGISTRAR_BLOCK,
)

# --------------------------------------------------------------------------
# विवाहको सूचना फाराम - अनुसूची–४
# --------------------------------------------------------------------------

MARRIAGE = official(
    id="marriage_registration_notice",
    title_en="Marriage registration notice - विवाहको सूचना फाराम",
    title_ne="विवाह दर्ता: विवाहको सूचना फाराम",
    desc_en="Notice of a marriage to the local registrar (ward office), in the exact form of Schedule 4 of the Personal Events Registration Rules, with photo boxes and both spouses' thumbprint boxes.",
    desc_ne="स्थानीय पञ्जीकाधिकारी (वडा कार्यालय) लाई दिने विवाहको सूचना फाराम — जन्म, मृत्यु तथा अन्य व्यक्तिगत घटना (दर्ता गर्ने) नियमावलीको अनुसूची–४; फोटो र ल्याप्चे सहीछापका बाकससहित।",
    category=NOTICES,
    law=PERSONAL_EVENTS_RULES, law_en="Births, Deaths and other Personal Events (Registration) Rules, 2034", schedule="अनुसूची–४",
    relates_to="नियम ५", page=18, form_title="विवाहको सूचना फाराम",
    keywords=("marriage", "विवाह", "registration", "दर्ता", "marriage certificate", "विवाह दर्ता", "wedding", "ward office"),
    fields=_OFFICE_FIELDS + [
        SELECT("m_kind", "Kind of marriage", "विवाहको किसिम", ["सामाजिक परम्परा अनुसार", "विवाह दर्ता ऐन, २०२८ अनुसार", "मुलुकी देवानी (संहिता) ऐन, २०७४ अनुसार"]),
        F("m_bs", "Date of marriage", "विवाह भएको मिति", "date", required=True),
        *_addr("mp", "Place of marriage", "विवाह सम्पन्न भएको स्थान"),
        F("m_abroad_ne", "If married abroad: address (Nepali)", "विदेशमा विवाह भएमा (नेपालीमा: देश, प्रदेश, स्थानीय ठेगाना)"),
        F("m_abroad_en", "If married abroad: address (English)", "विदेशमा विवाह भएमा ठेगाना (In English)"),
        *_name3("g", "Groom", "दुलाहा", required=True), *_name3("b", "Bride", "दुलही", required=True),
        F("g_bs", "Groom: date of birth", "दुलाहा: जन्म मिति", "date"), F("b_bs", "Bride: date of birth", "दुलही: जन्म मिति", "date"),
        F("g_marital", "Groom: previous marital status", "दुलाहा: पूर्व वैवाहिक स्थिति"), F("b_marital", "Bride: previous marital status", "दुलही: पूर्व वैवाहिक स्थिति"),
        F("g_cit", "Groom: citizenship / birth reg. no.", "दुलाहा: नागरिकता प्रमाण पत्र नं./जन्म दर्ता नं."), F("b_cit", "Bride: citizenship / birth reg. no.", "दुलही: नागरिकता प्रमाण पत्र नं./जन्म दर्ता नं."),
        F("g_reg", "Groom: earlier marriage registration no. and body", "दुलाहा: दर्ता विवाह भएको भए दर्ता नं. र निकाय"), F("b_reg", "Bride: earlier marriage registration no. and body", "दुलही: दर्ता विवाह भएको भए दर्ता नं. र निकाय"),
        F("g_addr", "Groom: permanent address (Nepali)", "दुलाहा: स्थायी ठेगाना (नेपालीमा)"), F("b_addr", "Bride: permanent address (Nepali)", "दुलही: स्थायी ठेगाना (नेपालीमा)"),
        F("g_addr_en", "Groom: permanent address (English)", "दुलाहा: स्थायी ठेगाना (In English)"), F("b_addr_en", "Bride: permanent address (English)", "दुलही: स्थायी ठेगाना (In English)"),
        F("g_passport", "Groom: if foreign: passport, country, issue date", "दुलाहा: विदेशी भए राहदानी नं., देश र जारी मिति"), F("b_passport", "Bride: if foreign: passport, country, issue date", "दुलही: विदेशी भए राहदानी नं., देश र जारी मिति"),
        F("g_edu", "Groom: education", "दुलाहा: शैक्षिक स्तर"), F("b_edu", "Bride: education", "दुलही: शैक्षिक स्तर"),
        F("g_job", "Groom: occupation", "दुलाहा: पेशा"), F("b_job", "Bride: occupation", "दुलही: पेशा"),
        F("g_religion", "Groom: religion", "दुलाहा: धर्म"), F("b_religion", "Bride: religion", "दुलही: धर्म"),
        F("g_caste", "Groom: caste / ethnicity", "दुलाहा: जातजाति"), F("b_caste", "Bride: caste / ethnicity", "दुलही: जातजाति"),
        F("g_gf", "Groom: grandfather's name", "दुलाहा: बाजेको नाम"), F("b_gf", "Bride: grandfather's name", "दुलही: बाजेको नाम"),
        F("g_fa", "Groom: father's name", "दुलाहा: बाबुको नाम"), F("b_fa", "Bride: father's name", "दुलही: बाबुको नाम"),
        F("g_mo", "Groom: mother's name", "दुलाहा: आमाको नाम"), F("b_mo", "Bride: mother's name", "दुलही: आमाको नाम"),
        F("other_informant", "If the informant is someone other than the couple (authorised): name, address, ID", "दम्पत्ती बाहेक अरु सूचक भएमा (अधिकृतनामा दिएको अवस्थामा): नाम, ठेगाना, परिचयपत्र नं."),
        F("form_date", "Date the form was filled", "फाराम भरेको मिति", "date"),
    ],
    body="""
@table 3.2,3.2 all h=2.6 align=right
| @c दुलाहाको<br>फोटो | @c दुलहीको<br>फोटो |
@end
""" + _HEADER + """
@j निम्न लिखित विवरण खुलाई विवाहको सूचना दिन आएको छु । कानून अनुसार विवाह दर्ता गरी पाऊँ ।
@b,+ १. विवाहको विवरण
@l,>0.5 विवाहको किसिमः {{ opts(m_kind, ['सामाजिक परम्परा अनुसार', 'विवाह दर्ता ऐन, २०२८ अनुसार', 'मुलुकी देवानी (संहिता) ऐन, २०७४ अनुसार']) }}
@l,>0.5 विवाह भएको मितिः वि.सं. मा (साल-महिना-गते) {{ m_bs|bs|blank(4) }}   ई.सं. मा (गते-महिना-साल) {{ m_bs|ad|blank(4) }}
@bu,>0.5 विवाह सम्पन्न भएको स्थान
""" + _addr_lines("mp", 0.5) + """
@l,>0.5 विदेशमा विवाह भएमा (नेपालीमा: देश, प्रदेश, स्थानीय ठेगाना) {{ m_abroad_ne|blank(6) }}
@l,>0.5 विदेशमा विवाह भएमा ठेगाना (In English: District, Province/State, Local Address) {{ m_abroad_en|blank(6) }}
@b,+ २. दुलहा दुलहीको विवरण
@table 4.6,5.6,5.6 all
| | @b दुलहाको विवरण | @b दुलहीको विवरण |
| @b नाम (नेपालीमा) | | |
| पहिलो नाम | {{ g_first }} | {{ b_first }} |
| बीचको नाम | {{ g_mid }} | {{ b_mid }} |
| थर | {{ g_last }} | {{ b_last }} |
| @b Name (In English) | {{ g_en }} | {{ b_en }} |
| जन्म मिति<br>वि.सं. मा (साल-महिना-गते)<br>ई.सं. मा (गते-महिना-साल) | {{ g_bs|bs }}<br>{{ g_bs|ad }} | {{ b_bs|bs }}<br>{{ b_bs|ad }} |
| पूर्व वैवाहिक स्थिति | {{ g_marital }} | {{ b_marital }} |
| नागरिकता प्रमाण पत्र नं./ जन्म दर्ता नं. | {{ g_cit|nd }} | {{ b_cit|nd }} |
| दर्ता विवाह भएको भए:<br>दर्ता नं.<br>निकाय: | {{ g_reg|nd }} | {{ b_reg|nd }} |
| स्थायी ठेगाना (नेपालीमा) | {{ g_addr }} | {{ b_addr }} |
| स्थायी ठेगाना (In English) | {{ g_addr_en }} | {{ b_addr_en }} |
| विदेशी भएमा राहदानी नं., देश र जारी मिति | {{ g_passport }} | {{ b_passport }} |
| शैक्षिक स्तर | {{ g_edu }} | {{ b_edu }} |
| पेशा | {{ g_job }} | {{ b_job }} |
| धर्म | {{ g_religion }} | {{ b_religion }} |
| जातजाति | {{ g_caste }} | {{ b_caste }} |
| बाजेको नाम | {{ g_gf }} | {{ b_gf }} |
| बाबुको नाम | {{ g_fa }} | {{ b_fa }} |
| आमाको नाम | {{ g_mo }} | {{ b_mo }} |
@end
@b,+ ३. सूचकको विवरण
@j यसमा लेखिएको विवरण साँचो हो। झुट्ठा ठहरे कानून बमोजिम सहुँला बुझाउँला भनी सहीछाप गर्ने सूचकको विवरण :
@l,+ दुलाहाको सहीछाप : ……………………          दुलहीको सहीछाप : ……………………
@thumbs label=दुलाहाको ल्याप्चे सहीछाप
@thumbs label=दुलहीको ल्याप्चे सहीछाप
@l,+ दम्पत्ती बाहेक अरु सूचक भएमा (अधिकृतनामा दिएको अवस्थामा): {{ other_informant|blank(8) }}
@l फाराम भरेको मिति (साल-महिना-गते) {{ form_date|bs|blank(6) }}
""" + _REGISTRAR_BLOCK + """
@b,+ संलग्न गर्नुपर्ने कागजातहरू:
@l १.|दुलाहादुलहीको नागरिकता प्रमाण-पत्रको प्रतिलिपि;
@l २.|कुनै एक जना विदेशमा रहेमा विदेश स्थित नेपाली राजदुतावासबाट प्रमाणित अधिकृत वारेसनामा;
@l ३.|दुलाहा वा दुलही नभएमा अदालतबाट भएको नाता कायमको कागज;
@l ४.|दुवै जनाको हालै खिचेको अटो साईजको फोटो ।
""",
)

# --------------------------------------------------------------------------
# सम्बन्ध विच्छेदको सूचना फाराम - अनुसूची–५
# --------------------------------------------------------------------------

DIVORCE_NOTICE = official(
    id="divorce_registration_notice",
    title_en="Divorce registration notice - सम्बन्ध विच्छेदको सूचना फाराम",
    title_ne="सम्बन्ध विच्छेद दर्ता: सम्बन्ध विच्छेदको सूचना फाराम",
    desc_en="Notice of a court-decreed divorce to the local registrar, in the exact form of Schedule 5 of the Personal Events Registration Rules.",
    desc_ne="अदालतबाट भएको सम्बन्ध विच्छेद दर्ता गर्न स्थानीय पञ्जीकाधिकारीलाई दिने सूचना फाराम — जन्म, मृत्यु तथा अन्य व्यक्तिगत घटना (दर्ता गर्ने) नियमावलीको अनुसूची–५।",
    category=NOTICES,
    law=PERSONAL_EVENTS_RULES, law_en="Births, Deaths and other Personal Events (Registration) Rules, 2034", schedule="अनुसूची–५",
    relates_to="नियम ५", page=24, form_title="सम्बन्ध विच्छेदको सूचना फाराम",
    keywords=("divorce", "सम्बन्ध विच्छेद", "registration", "दर्ता", "separation", "decree", "ward office"),
    fields=_OFFICE_FIELDS + [
        SELECT("court_kind", "Court that decided the divorce", "अदालतको किसिम", ["जिल्ला अदालत", "उच्च अदालत", "सर्वोच्च अदालत"]),
        F("court_addr", "Court's address (province, municipality, ward)", "अदालतको ठेगाना (प्रदेश, गा.पा./न.पा., वडा)"),
        F("decision_no", "Court decision number", "अदालतको निर्णय नम्बर"),
        F("foreign_court", "If a foreign court: name, country and local address (Nepali)", "विदेशी अदालत भएमा अदालतको नाम, देश र स्थानीय ठेगाना (नेपालीमा)"),
        F("foreign_court_en", "If a foreign court: name, country, province/state, local address (English)", "विदेशी अदालत भएमा (In English)"),
        F("decision_date", "Date of the court decision", "अदालतको निर्णय मिति", "date", required=True),
        F("marriage_no", "Marriage registration no.", "विवाह दर्ता नं."),
        *_name3("h", "Husband", "पति", required=True), *_name3("w", "Wife", "पत्नी", required=True),
        F("h_bs", "Husband: date of birth", "पतिको जन्म मिति", "date"), F("w_bs", "Wife: date of birth", "पत्नीको जन्म मिति", "date"),
        F("h_cit", "Husband: birth reg. / citizenship no.", "पति: जन्म दर्ता नं/ नागरिकता प्रमाण पत्र नं."), F("w_cit", "Wife: birth reg. / citizenship no.", "पत्नी: जन्म दर्ता नं/ नागरिकता प्रमाण पत्र नं."),
        F("h_passport", "Husband: if foreign: passport, country, date", "पति: विदेशी भए पासपोर्ट नं., देश र जारी मिति"), F("w_passport", "Wife: if foreign: passport, country, date", "पत्नी: विदेशी भए पासपोर्ट नं., देश र जारी मिति"),
        F("h_addr", "Husband: address before divorce", "पति: सम्बन्ध विच्छेद हुनु अगाडिको ठेगाना"), F("w_addr", "Wife: address before divorce", "पत्नी: सम्बन्ध विच्छेद हुनु अगाडिको ठेगाना"),
        F("h_edu", "Husband: education", "पति: शैक्षिक स्तर"), F("w_edu", "Wife: education", "पत्नी: शैक्षिक स्तर"),
        F("h_job", "Husband: occupation", "पति: पेशा"), F("w_job", "Wife: occupation", "पत्नी: पेशा"),
        F("h_religion", "Husband: religion", "पति: धर्म"), F("w_religion", "Wife: religion", "पत्नी: धर्म"),
        F("h_caste", "Husband: caste / ethnicity", "पति: जातजाति"), F("w_caste", "Wife: caste / ethnicity", "पत्नी: जातजाति"),
        F("h_gf", "Husband: grandfather", "पति: बाजेको नाम थर"), F("w_gf", "Wife: grandfather", "पत्नी: बाजेको नाम थर"),
        F("h_fa", "Husband: father", "पति: बाबुको नाम थर"), F("w_fa", "Wife: father", "पत्नी: बाबुको नाम थर"),
        F("h_mo", "Husband: mother", "पति: आमाको नाम थर"), F("w_mo", "Wife: mother", "पत्नी: आमाको नाम थर"),
        F("marriage_date", "Date of marriage", "विवाह भएको मिति", "date"),
        F("children", "Number of children from the marriage", "वैवाहिक सम्बन्धबाट पाएको सन्तान सङ्ख्या", "number"),
        *_INFORMANT_FIELDS[:-1],
        F("inf_addr", "Informant's address", "सूचकको ठेगाना"),
        F("form_date", "Date the form was filled", "फाराम भरेको मिति", "date"),
    ],
    body=_HEADER + """
@j निम्न लिखित विवरण खुलाई सम्बन्ध विच्छेदको सूचना दिन आएको छु । कानून अनुसार सम्बन्ध विच्छेदको दर्ता गरी पाऊँ ।
@b,+ १. सम्बन्ध विच्छेद सम्बन्धी विवरण
@l,>0.5 (क)|सम्बन्ध विच्छेदको निर्णय गर्ने अदालतको किसिमः {{ opts(court_kind, ['जिल्ला अदालत', 'उच्च अदालत', 'सर्वोच्च अदालत']) }}
@l,>1.5 अदालतको ठेगानाः {{ court_addr|blank(6) }}
@l,>1.5 अदालतको निर्णय नम्बर : {{ decision_no|nd|blank(6) }}
@l,>0.5 (ख)|विदेशी अदालत भएमा : अदालतको नाम, देश र स्थानीय ठेगाना (नेपालीमा) : {{ foreign_court|blank(6) }}
@l,>1.5 Country, Province/State, Local Address (In English) : {{ foreign_court_en|blank(6) }}
@l,>0.5 (ग)|अदालतको निर्णय मिति : वि.सं. मा (साल-महिना-गते) {{ decision_date|bs|blank(4) }}   ई.स. मा (गते-महिना-साल) {{ decision_date|ad|blank(4) }}
@l,>0.5 (घ)|विवाह दर्ता नं. : {{ marriage_no|nd|blank(6) }}
@b,+ २. पति पत्नीको विवरण
@table 4.6,5.6,5.6 all
| | @b पतिको विवरण | @b पत्नीको विवरण |
| @b पूरा नाम (नेपाली) | | |
| पहिलो नाम | {{ h_first }} | {{ w_first }} |
| बीचको नाम | {{ h_mid }} | {{ w_mid }} |
| थर | {{ h_last }} | {{ w_last }} |
| Full Name (In English) | {{ h_en }} | {{ w_en }} |
| जन्म मिति<br>वि.सं. मा (साल-महिना-गते)<br>ई.सं. मा (गते-महिना-साल) | {{ h_bs|bs }}<br>{{ h_bs|ad }} | {{ w_bs|bs }}<br>{{ w_bs|ad }} |
| जन्म दर्ता नं/ नागरिकता प्रमाण पत्र नं. | {{ h_cit|nd }} | {{ w_cit|nd }} |
| विदेशी नागरिक भएमा पासपोर्ट नं., देश र जारी मिति | {{ h_passport }} | {{ w_passport }} |
| सम्बन्ध विच्छेद हुनु अगाडिको ठेगाना | {{ h_addr }} | {{ w_addr }} |
| शैक्षिक स्तर | {{ h_edu }} | {{ w_edu }} |
| पेशा | {{ h_job }} | {{ w_job }} |
| धर्म | {{ h_religion }} | {{ w_religion }} |
| जातजाति | {{ h_caste }} | {{ w_caste }} |
| बाजेको नाम थर (नेपाली) | {{ h_gf }} | {{ w_gf }} |
| बाबुको नाम थर (नेपाली) | {{ h_fa }} | {{ w_fa }} |
| आमाको नाम थर (नेपाली) | {{ h_mo }} | {{ w_mo }} |
@end
@l,+ विवाह भएको मिति: वि.सं. मा (साल-महिना-गते) {{ marriage_date|bs|blank(4) }}   ई.सं. मा (गते-महिना-साल) {{ marriage_date|ad|blank(4) }}
@l वैवाहिक सम्बन्धबाट पाएको सन्तान सङ्ख्या {{ children|nd|blank(3) }}
@b,+ ३. सूचकको विवरण
@j यसमा लेखिएको विवरण साँचो हो। झुट्ठा ठहरे कानून बमोजिम सहुँला बुझाउँला भनी सहीछाप गर्ने सूचकको विवरण :
""" + _name3_lines("inf") + """
@l ठेगाना: {{ inf_addr|blank(6) }}
@l नागरिकता प्रमाणपत्र नं./ परिचय पत्र नं. {{ inf_cit|nd|blank(6) }}
@l विदेशी भएमा राहदानी नं. र जारी गर्ने देशको नाम {{ inf_passport|blank(6) }}
@l फाराम भरेको मिति (साल-महिना-गते) {{ form_date|bs|blank(6) }}
@l,+ सूचकको सहीछाप
@thumbs
""" + _REGISTRAR_BLOCK + """
@b,+ संलग्न गर्नुपर्ने कागजात :
@l १.|सूचकको नागरिकता प्रमाणपत्रको प्रतिलिपि
@l २.|अदालतबाट सम्बन्ध विच्छेद भएको फैसलाको प्रतिलिपि
""",
)

# --------------------------------------------------------------------------
# बसाइँ सराईको लगत हस्तान्तरण फाराम - अनुसूची–६
# --------------------------------------------------------------------------

MIGRATION = official(
    id="migration_registration_notice",
    title_en="Migration (change of residence) notice - बसाइँ सराईको सूचना",
    title_ne="बसाइँ सराई दर्ता: बसाइँ सराईको लगत हस्तान्तरण फाराम",
    desc_en="Notice of a family's change of residence to the local registrar, in the exact form of Schedule 6 of the Personal Events Registration Rules, with the table of migrating family members.",
    desc_ne="बसाइँ सराईको सूचना स्थानीय पञ्जीकाधिकारीलाई दिने फाराम — जन्म, मृत्यु तथा अन्य व्यक्तिगत घटना (दर्ता गर्ने) नियमावलीको अनुसूची–६; बसाइँ सर्ने परिवारका सदस्यको तालिकासहित।",
    category=NOTICES,
    law=PERSONAL_EVENTS_RULES, law_en="Births, Deaths and other Personal Events (Registration) Rules, 2034", schedule="अनुसूची–६",
    relates_to="नियम ५", page=30, form_title="बसाइँ सराईको लगत हस्तान्तरण फाराम",
    keywords=("migration", "बसाइँ सराइ", "बसाई सराई", "change of address", "moving", "relocation", "registration", "ward office", "transfer"),
    fields=_OFFICE_FIELDS + [
        SELECT("i_title", "Informant", "सूचक श्री/श्रीमती/सुश्री", ["श्री", "श्रीमती", "सुश्री"]),
        F("i_name", "Informant's full name", "सूचकको पूरा नाम", required=True),
        F("i_bs", "Informant's date of birth", "सूचकको जन्म मिति", "date"),
        F("i_cit", "Citizenship certificate no.", "ना.प्र.नं"),
        *_addr("cur", "Present address", "हालको ठेगाना"), F("cur_prov_en", "Present: province (English)", "हाल: प्रदेश (In English)"),
        F("cur_dist", "Present: district", "हाल: जिल्ला"),
        *_addr("new", "Migrated address", "सरी जाने ठेगाना"), F("new_prov_en", "New: province (English)", "सरी जाने: प्रदेश (In English)"),
        F("new_dist", "New: district", "सरी जाने: जिल्ला"),
        F("mig_date", "Date of migration", "बसाइँ सराईको मिति", "date", required=True),
        SELECT("reason", "Reason for migrating", "बसाइँ सराईको कारण", ["नोकरी", "व्यापार व्यावसाय", "घरबास", "अध्ययन/शिक्षा", "अन्य"]),
        F("reason_other", "Reason (if other)", "अन्य (खुलाउने)"),
        F("members", "2. Family members (one per line: full name | birth reg. no. | date of birth | sex | citizenship no. | issue date | issue district | relation to informant | migrating yes/no)",
          "२. बसाइँ सराई गर्ने परिवारका सदस्यहरूको विवरण (एक पङ्क्तिमा एक जना: पुरा नाम थर | जन्म दर्ता नं. | जन्म मिति | लिङ्ग | नागरिकता नं. | जारी मिति | जारी जिल्ला | सूचकसँगको नाता | सरी जाने/नजाने)", "textarea"),
        F("form_date", "Date the form was filled", "फाराम भरेको मिति", "date"),
        F("family_total", "Number of family members", "परिवार सदस्य संख्या (जना)", "number"),
        F("family_moving", "Number migrating", "बसाइँ सरी जाने सदस्य (जना)", "number"),
    ],
    body="""
@i (सूचकले भर्ने)
@l श्री स्थानीय पञ्जिकाधिकारीज्यू,
@l वडा नं. {{ o_ward|nd|blank(4) }} , {{ o_local|blank(8) }} गा. पा./ न.पा.
@l {{ o_district|blank(8) }} जिल्ला, {{ o_province|blank(8) }} प्रदेश
@l,+ महोदय,
@j म सूचक {{ i_title|default('श्री/श्रीमती/सुश्री', true) }} {{ i_name|blank(8) }} , जन्म मिति {{ i_bs|bs|blank(6) }} , ना.प्र.नं {{ i_cit|nd|blank(6) }} भएको व्यक्ति निम्न लिखित विवरण खुलाई बसाइँ सराईको सूचना दिन आएको छु । कानून अनुसार बसाइँ सराई दर्ता गरी पाऊँ ।
@b,+ १. बसाइँ सराई विवरण
@table 4.6,5.6,5.6 all
| @b विवरण | @b हालको ठेगाना (Present Address) | @b सरी जाने ठेगाना (Migrated Address) |
| प्रदेश | {{ cur_prov }} / {{ cur_prov_en }} | {{ new_prov }} / {{ new_prov_en }} |
| जिल्ला (District) | {{ cur_dist }} | {{ new_dist }} |
| गाउँपालिका/नगरपालिका (Rural/Municipality) | {{ cur_local }} | {{ new_local }} |
| वडा नं (Ward No) | {{ cur_ward|nd }} | {{ new_ward|nd }} |
| गाउँ /टोल (Village/Tole) | {{ cur_tole }} | {{ new_tole }} |
| सडक/मार्ग (Road/Street) | {{ cur_road }} | {{ new_road }} |
| घर नं. (House No.) | {{ cur_house|nd }} | {{ new_house|nd }} |
@end
@l,+ बसाइँ सराईको मिति वि.सं. मा (साल-महिना-गते) {{ mig_date|bs|blank(4) }}   ई.सं. मा (गते-महिना-साल) {{ mig_date|ad|blank(4) }}
@l बसाइँ सराईको कारणः {{ opts(reason, ['नोकरी', 'व्यापार व्यावसाय', 'घरबास', 'अध्ययन/शिक्षा', 'अन्य']) }}{% if reason == 'अन्य' %} (खुलाउने {{ reason_other|blank(6) }}){% endif %}
@b,+ २. बसाइँ सराई गर्ने परिवारका सदस्यहरुको विवरण
@table 0.9,2.6,1.9,1.7,1.2,1.9,1.4,1.5,1.5,1.4 all size=8.5
| @b क्र.सं.<br>(SN) | @b पुरा नाम थर<br>(Full Name) | @b जन्म दर्ता नं.<br>(Birth Reg. No.) | @b जन्म मिति<br>(साल-महिना-गते) | @b लिङ्ग<br>(Sex) | @b नागरिकता प्रमाणपत्र नं.<br>(Citizenship No.) | @b जारी मिति<br>(Issue Date) | @b जारी गर्ने जिल्ला<br>(Issue District) | @b सूचकसँगको नाता<br>(Relation) | @b बसाइँ सरी जाने/नजाने |
@end
@table 0.9,2.6,1.9,1.7,1.2,1.9,1.4,1.5,1.5,1.4 all size=8.5
@rows members:3
| {{ n|nd }} | {{ (item.split('|') + [''] * 9)[0]|trim }} | {{ (item.split('|') + [''] * 9)[1]|trim }} | {{ (item.split('|') + [''] * 9)[2]|trim }} | {{ (item.split('|') + [''] * 9)[3]|trim }} | {{ (item.split('|') + [''] * 9)[4]|trim }} | {{ (item.split('|') + [''] * 9)[5]|trim }} | {{ (item.split('|') + [''] * 9)[6]|trim }} | {{ (item.split('|') + [''] * 9)[7]|trim }} | {{ (item.split('|') + [''] * 9)[8]|trim }} |
@end
@l,+ यसमा लेखिएको विवरण साँचो हो। झुट्ठा ठहरे कानून बमोजिम सहुँला बुझाउँला भनी सहीछाप गर्ने सूचकको विवरण :
@l फाराम भरेको मिति (साल-महिना-गते): {{ form_date|bs|blank(6) }}
@l,+ स्थानीय पञ्जिकाधिकारीले भर्ने :
@j श्री स्थानीय पञ्जिकाधिकारी ज्यू, वडा नं {{ new_ward|nd|blank(3) }} , {{ new_local|blank(6) }} गा. पा./ न.पा. {{ new_dist|blank(6) }} जिल्ला {{ new_prov|blank(6) }} प्रदेश जन्म, मृत्यु तथा अन्य व्यक्तिगत घटना (दर्ता गर्ने) नियमावली २०३४ को नियम ५ बमोजिम {{ family_total|nd|blank(3) }} जना परिवार सदस्य मध्ये {{ family_moving|nd|blank(3) }} जना सदस्यहरू बसाइँ सरी त्यस स्थानमा जानको लागि निवेदन प्राप्त भएकोले सम्पूर्ण सदस्यहरुको यस अघि घटेका व्यक्तिगत घटना दर्ता गरी, सूचना फारामको सक्कल प्रति यसै साथ संलग्न राखी लगत हस्तान्तरण गरिएकोले तहाँ बसाइँ सराइँ दर्ता गरिदिनुहुन अनुरोध छ ।
@l स्थानीय पञ्जिकाधिकारीको हस्ताक्षर:
@l स्थानीय पञ्जिकाधिकारीको नाम:
@l,+ सूचकको सहीछाप
@thumbs
@l कर्मचारी सङ्केत नं./परिचय नं.: ……………………
@l फारम दर्ता नं. : ……………………
""",
)

TEMPLATES = [BIRTH, DEATH, MARRIAGE, DIVORCE_NOTICE, MIGRATION]
