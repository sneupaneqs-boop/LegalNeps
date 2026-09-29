"""Civil-court forms transcribed from the schedules (अनुसूची) of the
मुलुकी देवानी कार्यविधि संहिता, २०७४ (Civil Procedure Code, 2074).

Every form below was read against the schedule in the official Law
Commission PDF (see `source.url`, with the page): same heading lines and
order, same fixed wording, same numbered items; the blanks are the fields.
Layout follows the printed page: centred titles, a right-aligned "court fills
this in" block, centred party lines, right-aligned signature line.
"""
from __future__ import annotations

from .dsl import F, SELECT
from .forms_common import (
    CASE_TITLE as _CASE_TITLE, DATE as _DATE, EVIDENCE as _EVIDENCE, FEE_ITEMS, FEES as _FEES,
    LAWYERS as _LAWYERS, REG_DATE as _REG_DATE, REG_NO as _REG_NO, WITNESSES as _WITNESSES,
    CDPC, court_field, court_line, more_parties_field, numbered_items, official, pair_items,
    party_fields, party_line,
)

CIVIL = "court"

# --------------------------------------------------------------------------
# फिरादपत्र - अनुसूची–१ (दफा ९५)
# --------------------------------------------------------------------------

PLAINT = official(
    id="plaint_civil",
    title_en="Plaint (civil suit) - फिरादपत्र",
    title_ne="फिरादपत्र (देवानी मुद्दा)",
    desc_en="The prescribed plaint for a civil suit in a District Court, in the exact form of Schedule 1 of the Civil Procedure Code.",
    desc_ne="मुलुकी देवानी कार्यविधि संहिताको अनुसूची–१ बमोजिमको जिल्ला अदालतमा दिने फिरादपत्रको ढाँचा।",
    category=CIVIL,
    law=CDPC, law_en="Muluki Civil Procedure Code, 2074", schedule="अनुसूची–१", relates_to="दफा ९५",
    page=128, form_title="फिरादपत्रको ढाँचा",
    keywords=("plaint", "suit", "फिराद", "दाबी", "नालिस", "civil case", "court", "अदालत", "मुद्दा दर्ता"),
    provisions=[{"law_title_ne": CDPC, "section": "95"}],
    fields=[
        court_field(), _REG_NO, _REG_DATE,
        *party_fields("pl", "Plaintiff", "बादी"), more_parties_field("pl_more", "plaintiff", "बादी"),
        *party_fields("df", "Defendant", "प्रतिबादी"), more_parties_field("df_more", "defendant", "प्रतिबादी"),
        _CASE_TITLE,
        F("claims", "Facts, grounds and claim (one point per line -> (क) (ख) (ग) ...)",
          "फिरादको विषयवस्तु, दाबी गर्ने आधार र फिराद दाबी (एक पङ्क्तिमा एक बुँदा -> (क) (ख) (ग) ...)", "textarea",
          required=True),
        F("juris_law", "Act giving the court jurisdiction (name)", "अधिकारक्षेत्र दिने ऐनको नाम"),
        F("juris_year", "Act year (B.S.)", "ऐनको साल"),
        F("juris_section", "Section", "दफा"),
        F("limitation", "Limitation period basis", "हदम्याद (कुन कानून/दफा बमोजिम)"),
        SELECT("other_suit", "Suit filed elsewhere on this matter?", "प्रस्तुत विषयमा अन्यत्र फिराद", ["छ", "छैन"]),
        SELECT("service", "Service of summons on defendant", "म्याद तामेल गर्ने तरिका",
               ["आफैँले", "कानून व्यवसायी मार्फत", "अदालतबाट"]),
        _LAWYERS, _FEES, _EVIDENCE, _WITNESSES, _DATE,
    ],
    body="""
@r अदालत/कार्यालयले भर्ने
@r मुद्दा दर्ता नं.: {{ reg_no|blank(8) }}
@r दर्ता मिति: {{ reg_date|bs|blank(8) }}
@c,+ """ + court_line() + """
@cbu फिरादपत्र
@c,+ """ + party_line("pl", "बादी") + """
@c,each=pl_more:0 {{ item }} **बादी**
@cb विरुद्ध
@c """ + party_line("df", "प्रतिबादी") + """
@c,each=df_more:0 {{ item }} **प्रतिबादी**
@cb मुद्दा :- {{ case_title|blank(10) }}
@l,+ १.|म/हामी फिरादपत्रवाला निम्न प्रकरणहरूमा लेखिए बमोजिम फिराद गर्दछु/गर्दछौँ ।
""" + numbered_items("claims", 5) + """
@l २.|{{ juris_law|blank(6) }} ऐन {{ juris_year|blank(4) }} को दफा {{ juris_section|blank(4) }} बमोजिम यो मुद्दा यसै अदालत/कार्यालयको अधिकारक्षेत्रभित्र पर्दछ ।
@l ३.|फिराद गर्न {{ limitation|blank(6) }} कानून बमोजिम हदम्याद रहेको छ ।
@l ४.|प्रस्तुत विषयमा अन्यत्र फिराद गरेको {{ other_suit|default('छ/छैन', true) }} ।
@l ५.|प्रतिबादीलाई {{ service|default('आफैँले/कानून व्यवसायी मार्फत/अदालतबाट', true) }} म्याद तामेल गर्ने व्यवस्था गरी पाउँ ।
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
@ji,+ द्रष्टव्य : सङ्गठित संस्थाको तर्फबाट फिरादपत्र दिँदा त्यस्तो संस्थाको नाम तथा ठेगाना र त्यस्तो संस्थाको तर्फबाट फिरादपत्र दिन अधिकार पाएको व्यक्तिको नाम थर र पद उल्लेख गर्नु पर्नेछ ।
""",
)

TEMPLATES = [PLAINT]
