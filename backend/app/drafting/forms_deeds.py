"""Deeds (लिखत): standard formats for documents the Muluki Civil Code, 2074
requires in writing. No schedule prescribes the wording, so each is a
standard layout carrying the elements the Code lists (for example s.217 for a
partition deed and s.477 for a debt or sale instrument), with a signature
block, left/right thumbprint boxes and witnesses. Deeds that transfer
immovable property must be passed (पारित) at the competent office (s.464) -
each description says so.
"""
from __future__ import annotations

from .dsl import F, SELECT
from .forms_common import DATE, RELATIONS, standard

CIVIL_CODE = "मुलुकी देवानी संहिता, २०७४"
DEEDS = "deeds"


def person_fields(prefix: str, en: str, ne: str, required: bool = True) -> list:
    return [
        F(f"{prefix}_name", f"{en}: full name", f"{ne}: पूरा नाम", required=required),
        F(f"{prefix}_gf", f"{en}: grandfather's name", f"{ne}: बाजेको नाम"),
        F(f"{prefix}_father", f"{en}: father's (or spouse's) name", f"{ne}: बाबु (वा पति/पत्नी) को नाम"),
        SELECT(f"{prefix}_rel", f"{en}: relation to that person", f"{ne}: नाता", RELATIONS),
        F(f"{prefix}_age", f"{en}: age", f"{ne}: उमेर", "number"),
        F(f"{prefix}_addr", f"{en}: address (district, municipality/ward, tole)", f"{ne}: ठेगाना (जिल्ला, गा.पा./न.पा., वडा नं., टोल)", required=required),
        F(f"{prefix}_cit", f"{en}: citizenship certificate no.", f"{ne}: नागरिकता प्रमाणपत्र नं."),
    ]


def person_line(prefix: str) -> str:
    return (
        f"{{{{ {prefix}_addr|blank(6) }}}} बस्ने {{{{ {prefix}_gf|blank(4) }}}} को नाति {{{{ {prefix}_father|blank(4) }}}} को "
        f"{{{{ {prefix}_rel|default('छोरा/छोरी/पति/पत्नी', true) }}}} वर्ष {{{{ {prefix}_age|nd|blank(3) }}}} को **{{{{ {prefix}_name|blank(6) }}}}** "
        f"(नागरिकता प्रमाणपत्र नं. {{{{ {prefix}_cit|nd|blank(4) }}}})"
    )


_WITNESS_FIELDS = [
    F("wit1", "Witness 1: name, address, age", "साक्षी १: नाम, ठेगाना, उमेर"),
    F("wit2", "Witness 2: name, address, age", "साक्षी २: नाम, ठेगाना, उमेर"),
    F("place", "Place where the deed is written", "लिखत गरिएको ठाउँ"),
]

_SIGN_BLOCK = """
@l,+ साक्षीहरू :
@l १.|{{ wit1|blank(10) }}          सही : ………………
@l २.|{{ wit2|blank(10) }}          सही : ………………
"""


def _sig(role_ne: str, name_var: str) -> str:
    return (
        f"@l,+ {role_ne}को दस्तखत : ……………………          नाम : {{{{ {name_var}|blank(6) }}}}\n"
        f"@thumbs label={role_ne}को ल्याप्चे सहीछाप\n"
    )


# --------------------------------------------------------------------------
# शेषपछिको बकसपत्र (will)
# --------------------------------------------------------------------------

_WILL_NOTE = {
    "en": "Civil Code 2074 s.406(3)-(4): a gift that takes effect only after the giver's death is a शेषपछिको बकस (will-like gift); s.410: the giver may amend or cancel it "
          "in person before the competent officer; s.464(1)(g): a शेषपछिको बकसपत्र of immovable property must be passed (पारित) at the competent office or it has no legal effect.",
    "ne": "मुलुकी देवानी संहिता, २०७४ को दफा ४०६(३)–(४): दाताको मृत्यु पछि मात्र प्रभावकारी हुने बकस शेषपछिको बकस; दफा ४१०: दाताले सम्बन्धित अधिकारी समक्ष उपस्थित भई "
          "संशोधन वा रद्द गर्न सक्ने; दफा ४६४(१)(ग): अचल सम्पत्तिको शेषपछिको बकसपत्र सम्बन्धित कार्यालयबाट पारित गराउनु पर्ने, नगराएमा कानूनी मान्यता नपाउने।",
}

WILL = standard(
    id="will_sheshpachi_bakaspatra",
    title_en="Will (शेषपछिको बकसपत्र)",
    title_ne="शेषपछिको बकसपत्र",
    desc_en="A gift of property that takes effect only after your death (Nepali 'will'), with beneficiary, property, conditions, signature, thumbprints and witnesses. Standard format - must be passed at the land/registration office to be valid for immovable property.",
    desc_ne="दाताको मृत्यु पछि मात्र प्रभावकारी हुने बकसपत्र (लाभग्राही, सम्पत्ति, शर्त, दस्तखत, ल्याप्चे सहीछाप र साक्षीसहित)। मानक ढाँचा — अचल सम्पत्तिमा सम्बन्धित कार्यालयबाट पारित गराउनु पर्छ।",
    category=DEEDS,
    basis_law=CIVIL_CODE, basis_note=_WILL_NOTE,
    provisions=[{"law_title_ne": CIVIL_CODE, "section": "406"}, {"law_title_ne": CIVIL_CODE, "section": "410"},
                {"law_title_ne": CIVIL_CODE, "section": "464"}],
    keywords=("will", "बकसपत्र", "शेषपछि", "testament", "inheritance", "gift after death", "बकस", "succession", "अपुताली"),
    fields=[
        *person_fields("g", "Giver (you)", "बकस दिने (दाता)"),
        *person_fields("r", "Beneficiary", "बकस लिने (लाभग्राही)"),
        F("property", "Property given (one item per line: kitta no., area, location / description)", "बकस दिइने सम्पत्ति (एक पङ्क्तिमा एउटा: कित्ता नं., क्षेत्रफल, ठाउँ / विवरण)", "textarea", required=True),
        F("reason", "Reason for the gift (care, affection ...)", "बकस दिनुको कारण (पालनपोषण, माया-स्नेह आदि)"),
        F("conditions", "Conditions, if any (life interest, duties, others' shares)", "शर्त भए (जीवनकालको भोगाधिकार, दायित्व, अरूको अंश)", "textarea"),
        F("family", "Family members told / who consent (names)", "जानकारी दिइएका/मञ्जुर परिवारका सदस्य (नाम)", "textarea"),
        *_WITNESS_FIELDS, DATE,
    ],
    body="""
@cbu शेषपछिको बकसपत्र
@j,+ """ + person_line("g") + """ (यसपछि "बकस दिने" भनिएको) ले """ + person_line("r") + """ (यसपछि "बकस लिने" भनिएको) लाई लेखिदिएको शेषपछिको बकसपत्रको लिखत यस प्रकार छ :
@j १.|म बकस दिने आफ्नो पूर्ण होस हवासमा, कसैको दबाब वा प्रलोभन बेगर, आफ्नो हक र स्वामित्वको देहायको सम्पत्ति{% if reason %} {{ reason }} भएकोले{% endif %} मेरो मृत्यु पछि मात्र प्रभावकारी हुने गरी तपाईं बकस लिनेलाई शेषपछिको बकस गरिदिएको छु :
@l,>1,each=property:1 {{ n|nd }}.|{{ item }}
@j २.|मेरो जीवनकालमा उक्त सम्पत्तिमा मेरो पूर्ण भोगाधिकार कायम रहनेछ । मेरो मृत्यु पछि उक्त सम्पत्ति तपाईंले आफ्नो हक स्वामित्वमा लिई भोगचलन गर्न, नामसारी गराउन पाउनुहुनेछ ।
@j ३.|यो शेषपछिको बकसपत्र मैले जुनसुकै बखत सम्बन्धित अधिकारी समक्ष उपस्थित भई संशोधन वा रद्द गराउन सक्ने कुरा मलाई जानकारी छ ।
@j ४.|शर्त: {{ conditions|blank(10) }}
@j ५.|{% if family %}यो बकसपत्रको जानकारी मेरा परिवारका देहायका सदस्यहरूलाई गराइएको छ : {{ family }} ।{% else %}यो बकसपत्रको जानकारी मेरा परिवारका सदस्यहरूलाई गराइएको छ ।{% endif %}
@j ६.|यस लिखतमा लेखिएको व्यहोरा ठीक साँचो हो, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला । यो लिखत सम्बन्धित कार्यालयबाट पारित गराउन मञ्जुर छु ।
""" + _sig("बकस दिनेको", "g_name") + _SIGN_BLOCK + """
@l,+ लिखत गरेको ठाउँ : {{ place|blank(6) }}
@l {{ signoff(doc_date) }}
""",
)

# --------------------------------------------------------------------------
# अंशबण्डाको लिखत
# --------------------------------------------------------------------------

_PARTITION_DEED_NOTE = {
    "en": "Civil Code 2074 s.217 lists what a partition deed must state: (a) co-parceners' names, surnames, ages, addresses and parents'/grandparents' names; (b) the property each gets; "
          "(c) any debts each bears; (d) any co-parcener who will live with another; (e) that no property was hidden; (f) property that goes to one co-parcener after a parent's/spouse's "
          "death; (g) any share held in another's care; (h) other necessary matters. s.218 and s.464(1)(e): the deed must be passed (पारित).",
    "ne": "मुलुकी देवानी संहिता, २०७४ को दफा २१७ ले अंशबण्डाको लिखतमा (क) अंशियारहरूको नाम, थर, उमेर, ठेगाना तथा आमा, बाबु, बाजे, बजैको नाम, (ख) अंशियारले पाउने सम्पत्ति, "
          "(ग) अंशियारको नाममा ऋण धन, (घ) कुनै अंशियार अन्य अंशियारसँग बस्ने भए सो कुरा, (ङ) सम्पत्ति नलुकाएको कुरा, (च) शेषपछि कुनै अंशियारले मात्र पाउने सम्पत्ति, "
          "(छ) अंश कसैको जिम्मामा रहने भए सो कुरा, (ज) अन्य आवश्यक कुराहरू खुलाउनु पर्ने तोकेको छ। दफा २१८ र ४६४(१)(ङ): लिखत पारित गराउनु पर्ने।",
}

PARTITION_DEED = standard(
    id="partition_deed_anshabanda",
    title_en="Partition deed (अंशबण्डाको लिखत)",
    title_ne="अंशबण्डाको लिखत",
    desc_en="A deed dividing family property among the co-parceners, with every item Section 217 of the Civil Code requires. Standard format - must be passed at the competent office.",
    desc_ne="अंशियारहरूबीच पारिवारिक सम्पत्ति बण्डा गर्ने लिखत — देवानी संहिताको दफा २१७ ले खुलाउनु पर्ने भनेका सबै कुरासहित। मानक ढाँचा — सम्बन्धित कार्यालयबाट पारित गराउनु पर्छ।",
    category=DEEDS,
    basis_law=CIVIL_CODE, basis_note=_PARTITION_DEED_NOTE,
    provisions=[{"law_title_ne": CIVIL_CODE, "section": "216"}, {"law_title_ne": CIVIL_CODE, "section": "217"},
                {"law_title_ne": CIVIL_CODE, "section": "218"}, {"law_title_ne": CIVIL_CODE, "section": "464"}],
    keywords=("partition", "अंशबण्डा", "अंश", "family property", "division of property", "co-parcener", "अंशियार", "inheritance", "deed"),
    fields=[
        F("shares", "Co-parceners (one per line: name, surname, age, address, parents'/grandparents' names)", "अंशियारहरू (एक पङ्क्तिमा एक जना: नाम, थर, उमेर, ठेगाना, आमा/बाबु/बाजे/बजैको नाम)", "textarea", required=True),
        F("division", "Property each co-parcener gets (one line each: who — property)", "प्रत्येक अंशियारले पाउने सम्पत्ति (एक पङ्क्तिमा एउटा: को — सम्पत्ति)", "textarea", required=True),
        F("debts", "Debts each co-parcener bears", "अंशियारको नाममा रहेको ऋण धन", "textarea"),
        F("living_with", "Any co-parcener who will live with another", "कुनै अंशियार अन्य अंशियारसँग बस्ने भए सो कुरा"),
        F("after_death", "Property that one co-parcener alone gets after a parent's / spouse's death", "बाबु आमा वा पति पत्नीको शेषपछि कुनै अंशियारले मात्र पाउने सम्पत्ति"),
        F("in_care", "A co-parcener's share that stays in another's care", "कुनै अंशियारको अंश कसैको जिम्मामा रहने भए सो कुरा"),
        F("other", "Other necessary matters", "अन्य आवश्यक कुराहरू", "textarea"),
        F("signers", "Signatories (names, one per line)", "सहीछाप गर्ने अंशियारहरू (नाम, एक पङ्क्तिमा एक जना)", "textarea", required=True),
        *_WITNESS_FIELDS, DATE,
    ],
    body="""
@cbu अंशबण्डाको लिखत
@j,+ हामी देहायका अंशियारहरूले आपसमा अंशबण्डा गर्न मञ्जुर भई पारिवारिक सम्पत्तिको अंशबण्डा गरेको लिखत यस प्रकार छ :
@u,+ अंशियारहरूको विवरण
@l,>0.5,each=shares:2 {{ n|nd }}.|{{ item }}
@u,+ अंशबण्डाको व्यहोरा
@j १.|माथि उल्लिखित अंशियारहरूले बण्डा गर्नु पर्ने सम्पत्ति देहाय बमोजिम आपसमा बाँडफाँट गरी लिने गरी मञ्जुर गरेका छौँ :
@l,>1,each=division:2 ({{ ka }})|{{ item }}
@j २.|अंशियारको नाममा रहेको ऋण धन: {{ debts|blank(8) }}
@j ३.|बण्डा गर्दा कुनै अंशियार अन्य अंशियारसँग बस्ने भए सो कुरा: {{ living_with|blank(8) }}
@j ४.|बण्डा गर्नु पर्ने सम्पत्ति हामीमध्ये कसैले पनि नलुकाएको, नछिपाएको हो ।
@j ५.|बाबु आमा वा पति पत्नीको शेषपछि कुनै अंशियारले मात्र पाउने सम्पत्तिको विवरण: {{ after_death|blank(8) }}
@j ६.|कुनै अंशियारको अंश कसैको जिम्मामा रहने भए सो कुरा: {{ in_care|blank(8) }}
@j ७.|अन्य आवश्यक कुराहरू: {{ other|blank(8) }}
@j ८.|यस लिखतमा लेखिएको व्यहोरा ठीक साँचो हो, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला । यो लिखत सम्बन्धित कार्यालयबाट पारित गराउन हामी सबै मञ्जुर छौँ ।
@l,+ लिखतमा सहीछाप गर्ने अंशियारहरू :
@l,>0.5,each=signers:2 {{ n|nd }}.|{{ item }}          सही : ………………
@thumbs label=अंशियारहरूको ल्याप्चे सहीछाप (दायाँ / बायाँ) — प्रत्येकको अलग
""" + _SIGN_BLOCK + """
@l,+ लिखत गरेको ठाउँ : {{ place|blank(6) }}
@l {{ signoff(doc_date) }}
""",
)

# --------------------------------------------------------------------------
# घरजग्गा राजीनामा (sale deed of immovable property)
# --------------------------------------------------------------------------

_SALE_DEED_NOTE = {
    "en": "Civil Code 2074 s.464(1)(a): a deed transferring immovable property in any way must be passed at the competent office or has no legal effect; s.477 lists what any "
          "transaction deed must state (parties with parents'/grandparents' names, reason, amount, price, date and place, witnesses); s.432: immovable property cannot be transferred to a foreigner.",
    "ne": "मुलुकी देवानी संहिता, २०७४ को दफा ४६४(१)(क): अचल सम्पत्ति हस्तान्तरण गरेको लिखत सम्बन्धित कार्यालयबाट पारित गराउनु पर्ने, नगराएमा कानूनी मान्यता नपाउने; "
          "दफा ४७७: लिखतमा खुलाउनु पर्ने कुरा (पक्षको नाम थर उमेर ठेगाना, बाबु आमा बाजेको नाम, कारण, परिमाण, मूल्य, मिति, ठाउँ, साक्षी); दफा ४३२: विदेशीलाई अचल सम्पत्ति हस्तान्तरण गर्न नपाइने।",
}

SALE_DEED = standard(
    id="land_sale_deed_rajinama",
    title_en="Sale deed of land / house (राजीनामा)",
    title_ne="घर जग्गा राजीनामाको लिखत",
    desc_en="A deed transferring land or a house by sale (राजीनामा), with the price, receipt, warranties and the seller's consent to transfer at the land revenue office. Standard format - must be passed at the office.",
    desc_ne="घर जग्गा बिक्री गरी हस्तान्तरण गर्ने राजीनामाको लिखत — मूल्य, रकम बुझेको व्यहोरा, हकको आश्वासन र मालपोत कार्यालयबाट नामसारी गर्ने मञ्जुरीसहित। मानक ढाँचा — पारित गराउनु पर्छ।",
    category=DEEDS,
    basis_law=CIVIL_CODE, basis_note=_SALE_DEED_NOTE,
    provisions=[{"law_title_ne": CIVIL_CODE, "section": "464"}, {"law_title_ne": CIVIL_CODE, "section": "477"},
                {"law_title_ne": CIVIL_CODE, "section": "432"}],
    keywords=("sale deed", "राजीनामा", "land sale", "house sale", "जग्गा", "घर", "property transfer", "transfer of ownership", "malpot", "नामसारी", "रजिस्ट्रेशन"),
    fields=[
        *person_fields("s", "Seller", "राजीनामा लेखिदिने (बिक्रेता)"),
        *person_fields("b", "Buyer", "राजीनामा लिने (खरिदकर्ता)"),
        F("property", "Property sold (district, municipality/ward, kitta no., area, boundaries, house details)", "बिक्री गरिएको घर जग्गाको विवरण (जिल्ला, गा.पा./न.पा., वडा, कित्ता नं., क्षेत्रफल, चार किल्ला, घर)", "textarea", required=True),
        F("price", "Sale price (NPR)", "बिक्री मूल्य (रु.)", "number", required=True),
        F("price_words", "Price in words", "अक्षरेपी मूल्य"),
        F("payment", "How the price was paid (cash / bank cheque / instalments)", "मूल्य बुझाएको तरिका (नगद / बैङ्क चेक / किस्ता)"),
        F("reason", "Reason for sale", "बिक्री गर्नुको कारण"),
        *_WITNESS_FIELDS, DATE,
    ],
    body="""
@cbu घर जग्गा राजीनामाको लिखत
@j,+ """ + person_line("s") + """ (यसपछि "बिक्रेता" भनिएको) ले """ + person_line("b") + """ (यसपछि "खरिदकर्ता" भनिएको) लाई गरिदिएको राजीनामाको लिखत यस प्रकार छ :
@j १.|म बिक्रेतालाई {{ reason|default('घर व्यवहार चलाउन', true) }} आवश्यक परेकोले मेरो हक स्वामित्व र भोगचलनमा रहेको देहायको घर जग्गा तपाईं खरिदकर्तालाई रु. {{ price|nd|blank(6) }} ({{ price_words|blank(6) }}) मा बिक्री गर्न मञ्जुर भएँ :
@l,>1 {{ property }}
@j २.|उक्त मूल्य {{ payment|blank(6) }} मार्फत मैले तपाईंबाट पूरा बुझिलिएँ ।
@j ३.|उक्त घर जग्गा मेरो हक भोगको हुँदा अरू कसैको हक दाबी नलाग्ने, कुनै दोस्रो व्यक्तिलाई बिक्री, धितो, बन्धकी वा अन्य हस्तान्तरण नगरेको, र कुनै कर, तिरो वा सरकारी बाँकी नरहेको कुरा म ठहर गर्दछु ।
@j ४.|उक्त घर जग्गामा कसैको हक दाबी लागी तपाईंलाई हानि नोक्सानी भएमा त्यसको जिम्मेवारी म बिक्रेता स्वयंले लिनेछु ।
@j ५.|उक्त घर जग्गा तपाईंको नाममा नामसारी दाखिल खारेज गर्न मलाई मञ्जुर छ । यो लिखत सम्बन्धित कार्यालयबाट पारित गराउन मञ्जुर छु ।
@j ६.|यस लिखतमा लेखिएको व्यहोरा ठीक साँचो हो, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
""" + _sig("बिक्रेताको", "s_name") + _sig("खरिदकर्ताको", "b_name") + _SIGN_BLOCK + """
@l,+ लिखत गरेको ठाउँ : {{ place|blank(6) }}
@l {{ signoff(doc_date) }}
""",
)

# --------------------------------------------------------------------------
# ऋण लिखत (तमसुक)
# --------------------------------------------------------------------------

_LOAN_NOTE = {
    "en": "Civil Code 2074 s.476: no transaction without a written instrument; s.477: the instrument must state the parties (with parents'/grandparents' names), reason, amount, "
          "date of repayment, interest rate, that the creditor may recover from the debtor's property on default, place, witnesses and date; s.478: interest.",
    "ne": "मुलुकी देवानी संहिता, २०७४ को दफा ४७६: लिखत नगरी लेनदेन गर्न नहुने; दफा ४७७: लिखतमा पक्षको नाम थर उमेर ठेगाना (बाबु आमा बाजेको नाम), कारण, परिमाण, रकम बुझाउने मिति, "
          "ब्याजको दर, भाखा नाघे साहूले ऋणीको सम्पत्तिबाट असुल गर्न पाउने कुरा, ठाउँ, साक्षी र मिति खुलाउनु पर्ने; दफा ४७८: ब्याज।",
}

LOAN_DEED = standard(
    id="loan_deed_tamsuk",
    title_en="Loan deed (तमसुक)",
    title_ne="ऋण लिखत (तमसुक)",
    desc_en="A written loan agreement stating lender, borrower, amount, interest, repayment date, recovery on default, place, witnesses and date - every item Section 477 of the Civil Code requires. Standard format.",
    desc_ne="ऋण लेनदेनको लिखत — साहू, ऋणी, रकम, ब्याज, भाखा, भाखा नाघे असुली, ठाउँ, साक्षी र मिति (देवानी संहिताको दफा ४७७ ले खुलाउनु पर्ने भनेका सबै कुरा)। मानक ढाँचा।",
    category=DEEDS,
    basis_law=CIVIL_CODE, basis_note=_LOAN_NOTE,
    provisions=[{"law_title_ne": CIVIL_CODE, "section": "476"}, {"law_title_ne": CIVIL_CODE, "section": "477"},
                {"law_title_ne": CIVIL_CODE, "section": "478"}],
    keywords=("loan", "ऋण", "तमसुक", "debt", "lender", "borrower", "interest", "ब्याज", "साहू", "ऋणी", "IOU", "credit", "कर्जा"),
    fields=[
        *person_fields("l", "Lender (साहू)", "साहू (ऋण दिने)"),
        *person_fields("d", "Borrower (ऋणी)", "ऋणी (ऋण लिने)"),
        F("amount", "Loan amount (NPR)", "ऋण रकम (रु.)", "number", required=True),
        F("amount_words", "Amount in words", "अक्षरेपी रकम"),
        F("reason", "Reason for the loan", "ऋण लिनुको कारण", required=True),
        F("rate", "Interest rate (% per year); leave blank if interest-free", "ब्याजको दर (वार्षिक %); ब्याज नलाग्ने भए खाली"),
        F("due", "Repayment date", "रकम बुझाउने (भाखा) मिति", "date", required=True),
        F("security", "Security / collateral (if any)", "धितो / जमानत (भए)"),
        *_WITNESS_FIELDS, DATE,
    ],
    body="""
@cbu ऋण लिखत (तमसुक)
@j,+ """ + person_line("d") + """ (यसपछि "ऋणी" भनिएको) ले """ + person_line("l") + """ (यसपछि "साहू" भनिएको) लाई लेखिदिएको ऋण लिखतको व्यहोरा यस प्रकार छ :
@j १.|मलाई {{ reason|blank(8) }} को लागि रकम आवश्यक परेकोले मैले तपाईं साहूबाट आज नगद/बैङ्क मार्फत रु. {{ amount|nd|blank(6) }} ({{ amount_words|blank(6) }}) ऋण लिएको छु ।
@j २.|उक्त ऋण रकम मैले मिति {{ due|bs|blank(6) }} भित्र तपाईंलाई बुझाउनेछु ।
@j ३.|उक्त ऋणमा {% if rate %}वार्षिक {{ rate|nd }} प्रतिशतका दरले ब्याज तिर्नेछु{% else %}ब्याज लाग्ने छैन{% endif %} ।
@j ४.|{% if security %}उक्त ऋणको सुरक्षणको रूपमा {{ security }} धितो/जमानत राखेको छु ।{% else %}यो ऋणमा कुनै धितो राखिएको छैन ।{% endif %}
@j ५.|तोकिएको म्यादभित्र ऋण रकम नबुझाएमा वा यस लिखत बमोजिमको अन्य शर्त पूरा नगरेमा लेनदेन बमोजिमको रकम तपाईं साहूले मेरो सम्पत्तिबाट असुल गरी लिन पाउनुहुनेछ ।
@j ६.|यस लिखतमा लेखिएको व्यहोरा ठीक साँचो हो, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
""" + _sig("ऋणीको", "d_name") + """
@l,+ रकम बुझिलिने साहूको दस्तखत : ……………………          नाम : {{ l_name|blank(6) }}
""" + _SIGN_BLOCK + """
@l,+ लिखत गरेको ठाउँ : {{ place|blank(6) }}
@l {{ signoff(doc_date) }}
""",
)

# --------------------------------------------------------------------------
# दानपत्र / बकसपत्र (gift deed - effective now)
# --------------------------------------------------------------------------

_GIFT_NOTE = {
    "en": "Civil Code 2074 s.406: giving one's own property free of charge is a gift (दान); a gift out of affection or in return for care is a बकस; it may take effect at once, "
          "after a period, or after death. Immovable property must be passed at the competent office (s.464). Standard format.",
    "ne": "मुलुकी देवानी संहिता, २०७४ को दफा ४०६: आफ्नो हक स्वामित्वको सम्पत्ति निःशुल्क दिनु दान र पालनपोषण/माया स्नेह वापत दिनु बकस; दिनासाथ, निश्चित अवधि पछि वा मृत्यु पछि "
          "प्रभावकारी हुन सक्ने; अचल सम्पत्ति सम्बन्धित कार्यालयबाट पारित गराउनु पर्ने (दफा ४६४)। मानक ढाँचा।",
}

GIFT_DEED = standard(
    id="gift_deed_bakaspatra",
    title_en="Gift deed (दानपत्र / बकसपत्र)",
    title_ne="दानपत्र / बकसपत्र (दिनासाथ प्रभावकारी)",
    desc_en="A deed giving property free of charge that takes effect at once (a gift or 'बकस' out of affection or in return for care). Standard format - immovable property must be passed at the office.",
    desc_ne="निःशुल्क सम्पत्ति दिने दानपत्र/बकसपत्र (दिनासाथ प्रभावकारी; पालनपोषण वा माया स्नेह वापत)। मानक ढाँचा — अचल सम्पत्ति भए कार्यालयबाट पारित गराउनु पर्छ।",
    category=DEEDS,
    basis_law=CIVIL_CODE, basis_note=_GIFT_NOTE,
    provisions=[{"law_title_ne": CIVIL_CODE, "section": "406"}, {"law_title_ne": CIVIL_CODE, "section": "464"}],
    keywords=("gift", "दान", "बकस", "donation", "gift deed", "दानपत्र", "बकसपत्र", "transfer without payment"),
    fields=[
        *person_fields("g", "Giver", "दान/बकस दिने"), *person_fields("r", "Receiver", "दान/बकस लिने"),
        F("property", "Property given (kitta no., area, location / description)", "दिइएको सम्पत्ति (कित्ता नं., क्षेत्रफल, ठाउँ / विवरण)", "textarea", required=True),
        SELECT("kind", "Kind of gift", "दान वा बकस", ["दान", "बकस"]),
        F("reason", "Reason (care given, affection, purpose)", "कारण (पालनपोषण, माया स्नेह, प्रयोजन)"),
        *_WITNESS_FIELDS, DATE,
    ],
    body="""
@cbu {{ kind|default('दान/बकस', true) }}पत्रको लिखत
@j,+ """ + person_line("g") + """ (यसपछि "दिने" भनिएको) ले """ + person_line("r") + """ (यसपछि "लिने" भनिएको) लाई गरिदिएको {{ kind|default('दान/बकस', true) }}पत्रको लिखत यस प्रकार छ :
@j १.|म दिनेले आफ्नो हक र स्वामित्वको देहायको सम्पत्ति{% if reason %} {{ reason }} भएकोले{% endif %} तपाईं लिनेलाई निःशुल्क रूपमा यो लिखत गरेको दिनदेखि नै प्रभावकारी हुने गरी {{ kind|default('दान/बकस', true) }} दिएको छु :
@l,>1 {{ property }}
@j २.|उक्त सम्पत्तिमा अब मेरो कुनै हक, दाबी वा सरोकार रहने छैन । उक्त सम्पत्ति तपाईंले आफ्नो हक स्वामित्वमा लिई भोगचलन गर्न, नामसारी गराउन पाउनुहुनेछ ।
@j ३.|उक्त सम्पत्ति मेरो हक भोगको हो, अरू कसैलाई दान, बकस, बिक्री, धितो वा बन्धकी दिएको छैन । यो लिखत सम्बन्धित कार्यालयबाट पारित गराउन मञ्जुर छु ।
@j ४.|यस लिखतमा लेखिएको व्यहोरा ठीक साँचो हो, झुट्टा ठहरे कानून बमोजिम सहुँला बुझाउँला ।
""" + _sig("दिनेको", "g_name") + _SIGN_BLOCK + """
@l,+ लिखत गरेको ठाउँ : {{ place|blank(6) }}
@l {{ signoff(doc_date) }}
""",
)

TEMPLATES = [WILL, PARTITION_DEED, SALE_DEED, LOAN_DEED, GIFT_DEED]
