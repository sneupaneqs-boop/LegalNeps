"""S9's first 6 drafting templates.

Every statute reference embedded in a paragraph's Nepali text below was
found with `idx.search()` and read in full with `idx.section()` against the
real corpus first (same discipline as S6/S7/S8's citation research) - the
section number quoted in the drafted document text and the `provisions`
list below always name the same corpus-verified dफा, so a corpus drift that
breaks a citation is caught by `tests/test_drafting.py`'s
`resolve_provision` check, not just by someone reading the generated DOCX.
"""
from __future__ import annotations

from .fields import Field, Paragraph, TemplateSpec

_SIGNATURE_BLOCK = Paragraph(
    text={
        "en": "\nSincerely,\n{{ sender_name }}\n{{ sender_address }}\nDate: {{ today_bs }} B.S. ({{ today_ad }} A.D.)",
        "ne": "\nभवदीय,\n{{ sender_name }}\n{{ sender_address }}\nमितिः {{ today_bs }} (अंग्रेजी मितिः {{ today_ad }})",
    }
)

LEGAL_NOTICE_SALARY = TemplateSpec(
    id="legal_notice_salary",
    title={"en": "Legal notice: unpaid salary", "ne": "कानूनी सूचना: तलब/पारिश्रमिक नपाएको"},
    description={
        "en": "A formal written notice demanding your employer pay wages owed, before you escalate to a complaint.",
        "ne": "रोजगारदातालाई बाँकी पारिश्रमिक भुक्तानी माग गर्ने औपचारिक लिखित सूचना, उजुरी दिनुअघि।",
    },
    fields=[
        Field("sender_name", {"en": "Your full name", "ne": "तपाईंको पूरा नाम"}, "text"),
        Field("sender_address", {"en": "Your address", "ne": "तपाईंको ठेगाना"}, "text"),
        Field("recipient_name", {"en": "Employer's name / company", "ne": "रोजगारदाताको नाम / कम्पनी"}, "text"),
        Field("recipient_address", {"en": "Employer's address", "ne": "रोजगारदाताको ठेगाना"}, "text"),
        Field("job_title", {"en": "Your job title", "ne": "तपाईंको पद"}, "text"),
        Field("unpaid_period", {"en": "Period the unpaid wages cover", "ne": "बाँकी पारिश्रमिकको अवधि"}, "text"),
        Field("unpaid_amount", {"en": "Unpaid amount (NPR)", "ne": "बाँकी रकम (रु.)"}, "number"),
        Field("demand_days", {"en": "Days given to pay", "ne": "भुक्तानीका लागि दिइने दिन"}, "number", default=15),
    ],
    paragraphs=[
        Paragraph({"en": "श्री {{ recipient_name }}", "ne": "श्री {{ recipient_name }}"}, bold=True),
        Paragraph({"en": "Address: {{ recipient_address }}", "ne": "ठेगानाः {{ recipient_address }}"}),
        Paragraph({"en": "Date: {{ today_bs }} B.S.", "ne": "मितिः {{ today_bs }}"}),
        Paragraph(
            {"en": "Subject: Legal notice demanding payment of unpaid salary",
             "ne": "विषयः पारिश्रमिक भुक्तानी गरिदिने सम्बन्धी कानूनी सूचना"},
            bold=True, align="center",
        ),
        Paragraph({
            "en": ("I, {{ sender_name }}, residing at {{ sender_address }}, have been employed by you as "
                   "{{ job_title }}. You have not paid my salary of NPR {{ unpaid_amount }} for the period "
                   "{{ unpaid_period }}. Under Section 35 of the Labour Act, 2074 (श्रम ऐन, २०७४, दफा ३५), the "
                   "gap between wage payments must not exceed one month, which you have violated."),
            "ne": ("उपरोक्त सम्बन्धमा, म {{ sender_name }}, ठेगाना {{ sender_address }}, हजुरको प्रतिष्ठानमा "
                   "{{ job_title }} पदमा कार्यरत रहेको छु। {{ unpaid_period }} अवधिको रु. {{ unpaid_amount }} "
                   "बराबरको पारिश्रमिक हजुरले हालसम्म भुक्तानी गर्नुभएको छैन। श्रम ऐन, २०७४ को दफा ३५ बमोजिम "
                   "पारिश्रमिक भुक्तानी गर्ने अवधिको अन्तर एक महिनाभन्दा बढी हुन नहुने व्यवस्था रहेकोमा सो "
                   "उल्लंघन भएको छ।"),
        }),
        Paragraph({
            "en": ("I therefore request you to pay the above unpaid salary within {{ demand_days }} days of "
                   "receiving this notice. If payment is not made within that period, I will file a complaint "
                   "with the competent authority under Section 162 of the Labour Act, 2074 (श्रम ऐन, २०७४, "
                   "दफा १६२) and pursue further legal action."),
            "ne": ("अतः यो सूचना प्राप्त भएको मितिले {{ demand_days }} दिनभित्र माथि उल्लिखित बाँकी पारिश्रमिक "
                   "भुक्तानी गरिदिनुहुन अनुरोध छ। तोकिएको अवधिभित्र भुक्तानी नगरेमा श्रम ऐन, २०७४ को दफा १६२ "
                   "बमोजिम सम्बन्धित निकायसमक्ष उजुरी दिई कानून बमोजिम अग्रसर हुनेछु।"),
        }),
        _SIGNATURE_BLOCK,
    ],
    provisions=[
        {"law_title_ne": "श्रम ऐन, २०७४", "section": "35"},
        {"law_title_ne": "श्रम ऐन, २०७४", "section": "162"},
    ],
)

LEGAL_NOTICE_DEPOSIT = TemplateSpec(
    id="legal_notice_deposit",
    title={"en": "Legal notice: rental deposit not returned",
           "ne": "कानूनी सूचना: घरबहाल धरौटी फिर्ता नपाएको"},
    description={
        "en": "A formal written notice demanding your landlord return your rental deposit.",
        "ne": "घरबेटीलाई धरौटी फिर्ता माग गर्ने औपचारिक लिखित सूचना।",
    },
    fields=[
        Field("sender_name", {"en": "Your full name", "ne": "तपाईंको पूरा नाम"}, "text"),
        Field("sender_address", {"en": "Your address", "ne": "तपाईंको ठेगाना"}, "text"),
        Field("recipient_name", {"en": "Landlord's name", "ne": "घरबेटीको नाम"}, "text"),
        Field("recipient_address", {"en": "Landlord's / house address", "ne": "घरबेटी / घरको ठेगाना"}, "text"),
        Field("deposit_amount", {"en": "Deposit amount (NPR)", "ne": "धरौटी रकम (रु.)"}, "number"),
        Field("vacate_date", {"en": "Date you vacated the house", "ne": "घर खाली गरेको मिति"}, "date"),
        Field("demand_days", {"en": "Days given to pay", "ne": "भुक्तानीका लागि दिइने दिन"}, "number", default=15),
    ],
    paragraphs=[
        Paragraph({"en": "श्री {{ recipient_name }}", "ne": "श्री {{ recipient_name }}"}, bold=True),
        Paragraph({"en": "Address: {{ recipient_address }}", "ne": "ठेगानाः {{ recipient_address }}"}),
        Paragraph({"en": "Date: {{ today_bs }} B.S.", "ne": "मितिः {{ today_bs }}"}),
        Paragraph(
            {"en": "Subject: Legal notice demanding return of rental deposit",
             "ne": "विषयः घरबहाल धरौटी फिर्ता गरिदिने सम्बन्धी कानूनी सूचना"},
            bold=True, align="center",
        ),
        Paragraph({
            "en": ("I, {{ sender_name }}, residing at {{ sender_address }}, had rented a house from you at "
                   "{{ recipient_address }} and vacated it on {{ vacate_date }}. Despite vacating, you have "
                   "not returned my deposit of NPR {{ deposit_amount }}. Under Sections 495 and 500 of the "
                   "National Civil Code, 2074 (मुलुकी देवानी संहिता, २०७४, दफा ४९५ र ५००), a person who has "
                   "taken on an obligation must fulfil it, and is liable to compensate for loss caused by "
                   "failing to do so."),
            "ne": ("उपरोक्त सम्बन्धमा, म {{ sender_name }}, ठेगाना {{ sender_address }}, हजुरको "
                   "{{ recipient_address }} स्थित घरमा बहालमा बसेको थिएँ र मिति {{ vacate_date }} मा घर खाली "
                   "गरिसकेको छु। घर खाली गरिसक्दा पनि हजुरले मेरो रु. {{ deposit_amount }} बराबरको धरौटी "
                   "फिर्ता गर्नुभएको छैन। मुलुकी देवानी संहिता, २०७४ को दफा ४९५ र ५०० बमोजिम दायित्व लिएको "
                   "व्यक्तिले सो पूरा गर्नुपर्ने र पूरा नगरे हानिको क्षतिपूर्ति व्यहोर्नुपर्ने व्यवस्था छ।"),
        }),
        Paragraph({
            "en": ("I therefore request you to return the above deposit within {{ demand_days }} days of "
                   "receiving this notice, failing which I will file a civil claim at the District Court."),
            "ne": ("अतः यो सूचना प्राप्त भएको मितिले {{ demand_days }} दिनभित्र माथि उल्लिखित धरौटी फिर्ता "
                   "गरिदिनुहुन अनुरोध छ, नगरेमा जिल्ला अदालतमा देवानी मुद्दा दायर गर्ने छु।"),
        }),
        _SIGNATURE_BLOCK,
    ],
    provisions=[
        {"law_title_ne": "मुलुकी देवानी संहिता, २०७४", "section": "495"},
        {"law_title_ne": "मुलुकी देवानी संहिता, २०७४", "section": "500"},
    ],
)

RENTAL_AGREEMENT = TemplateSpec(
    id="rental_agreement",
    title={"en": "Rental / tenancy agreement", "ne": "घरबहाल सम्झौता"},
    description={
        "en": "A written house-rental agreement covering everything Section 386 of the National Civil Code requires.",
        "ne": "मुलुकी देवानी संहिताको दफा ३८६ ले अनिवार्य गरेका सबै कुरा समेटिएको घरबहाल लिखित सम्झौता।",
    },
    fields=[
        Field("landlord_name", {"en": "Landlord's full name", "ne": "घरधनीको पूरा नाम"}, "text"),
        Field("landlord_address", {"en": "Landlord's address", "ne": "घरधनीको ठेगाना"}, "text"),
        Field("landlord_citizenship_no", {"en": "Landlord's citizenship number", "ne": "घरधनीको नागरिकता नम्बर"}, "text"),
        Field("tenant_name", {"en": "Tenant's full name", "ne": "बहालवालाको पूरा नाम"}, "text"),
        Field("tenant_address", {"en": "Tenant's permanent address", "ne": "बहालवालाको स्थायी ठेगाना"}, "text"),
        Field("tenant_citizenship_no", {"en": "Tenant's citizenship number", "ne": "बहालवालाको नागरिकता नम्बर"}, "text"),
        Field("house_location", {"en": "House location", "ne": "घर रहेको ठाउँ"}, "text"),
        Field("kitta_no", {"en": "Land parcel (kitta) number", "ne": "जग्गाको कित्ता नम्बर"}, "text"),
        Field("purpose", {"en": "Purpose of renting (e.g. residence, shop)", "ne": "बहालमा लिने प्रयोजन"}, "text"),
        Field("start_date", {"en": "Tenancy start date", "ne": "बहाल शुरु हुने मिति"}, "date"),
        Field("duration_months", {"en": "Duration (months)", "ne": "बहाल अवधि (महिना)"}, "number"),
        Field("monthly_rent", {"en": "Monthly rent (NPR)", "ne": "मासिक बहाल रकम (रु.)"}, "number"),
        Field("payment_terms", {"en": "When/how rent is paid", "ne": "बहाल बुझाउने समय र प्रक्रिया"}, "text"),
        Field("utility_responsibility", {"en": "Who pays electricity/water/etc.", "ne": "बिजुली/पानी आदि महसुल बुझाउने दायित्व"}, "text"),
        Field("sublet_allowed", {"en": "Subletting allowed? (yes/no)", "ne": "अरूलाई बहालमा दिन पाउने? (हो/होइन)"}, "text"),
        Field("other_terms", {"en": "Other terms (optional)", "ne": "अन्य आवश्यक कुराहरू (वैकल्पिक)"}, "textarea", required=False, default=""),
    ],
    paragraphs=[
        Paragraph({"en": "House Rental Agreement", "ne": "घरबहाल सम्झौता"}, bold=True, align="center"),
        Paragraph({
            "en": ("This agreement is made on {{ today_bs }} B.S. between {{ landlord_name }}, address "
                   "{{ landlord_address }}, citizenship no. {{ landlord_citizenship_no }} (\"Landlord\") and "
                   "{{ tenant_name }}, address {{ tenant_address }}, citizenship no. {{ tenant_citizenship_no }} "
                   "(\"Tenant\"), under Section 386 of the National Civil Code, 2074 (मुलुकी देवानी संहिता, "
                   "२०७४, दफा ३८६)."),
            "ne": ("यो सम्झौता मिति {{ today_bs }} मा {{ landlord_name }}, ठेगाना {{ landlord_address }}, "
                   "नागरिकता नं. {{ landlord_citizenship_no }} (\"घरधनी\") र {{ tenant_name }}, ठेगाना "
                   "{{ tenant_address }}, नागरिकता नं. {{ tenant_citizenship_no }} (\"बहालवाला\") बीच मुलुकी "
                   "देवानी संहिता, २०७४ को दफा ३८६ बमोजिम गरिएको छ।"),
        }),
        Paragraph({
            "en": "1. House location: {{ house_location }} (land parcel / kitta no. {{ kitta_no }})",
            "ne": "१. घर रहेको ठाउँः {{ house_location }} (जग्गाको कित्ता नं. {{ kitta_no }})",
        }),
        Paragraph({"en": "2. Purpose of tenancy: {{ purpose }}", "ne": "२. बहालमा लिने प्रयोजनः {{ purpose }}"}),
        Paragraph({"en": "3. Tenancy start date: {{ start_date }}", "ne": "३. बहाल शुरु हुने मितिः {{ start_date }}"}),
        Paragraph({"en": "4. Duration: {{ duration_months }} months", "ne": "४. बहाल कायम रहने अवधिः {{ duration_months }} महिना"}),
        Paragraph({"en": "5. Monthly rent: NPR {{ monthly_rent }}", "ne": "५. मासिक बहाल रकमः रु. {{ monthly_rent }}"}),
        Paragraph({"en": "6. Payment terms: {{ payment_terms }}", "ne": "६. बहाल बुझाउने समय र प्रक्रियाः {{ payment_terms }}"}),
        Paragraph({
            "en": "7. Utility bills (electricity, water, etc.): {{ utility_responsibility }}",
            "ne": "७. बिजुली, खानेपानी आदि महसुल बुझाउने दायित्वः {{ utility_responsibility }}",
        }),
        Paragraph({
            "en": "8. Subletting to a third party: {{ sublet_allowed }}",
            "ne": "८. अरू व्यक्तिलाई बहालमा दिन पाउने कुराः {{ sublet_allowed }}",
        }),
        Paragraph({"en": "9. Other terms: {{ other_terms }}", "ne": "९. अन्य आवश्यक कुराहरूः {{ other_terms }}"}),
        Paragraph({
            "en": ("Under Section 389 of the National Civil Code (मुलुकी देवानी संहिता, २०७४, दफा ३८९), the "
                   "Landlord must let the Tenant use the house as agreed, maintain water/electricity/drainage "
                   "where available, and protect the Tenant from disturbance by other occupants. Under Section "
                   "402 (दफा ४०२), this agreement ends when the Tenant vacates, the Landlord evicts the "
                   "Tenant, both parties agree to end it, or the tenancy period expires."),
            "ne": ("मुलुकी देवानी संहिता, २०७४ को दफा ३८९ बमोजिम घरधनीले सम्झौता बमोजिम घर उपयोग गर्न दिने, "
                   "उपलब्ध भएसम्म पानी/बिजुली/ढल निकासको व्यवस्था गर्ने, र बहालवालालाई अन्य व्यक्तिबाट हुने "
                   "हैरानीबाट रोक्ने दायित्व हुनेछ। दफा ४०२ बमोजिम बहालवाला घर छाडेमा, घरधनीले हटाएमा, आपसी "
                   "सहमतिमा रद्द गरेमा, वा अवधि समाप्त भएमा यो सम्झौता समाप्त भएको मानिनेछ।"),
        }),
        Paragraph({
            "en": "Both parties and at least two witnesses from each side sign below, and each party keeps one copy, per Section 386(3)-(4).",
            "ne": "दफा ३८६(३)-(४) बमोजिम दुवै पक्ष र प्रत्येक पक्षका कम्तीमा दुई-दुई जना साक्षीको सहीछाप गरी एक-एक प्रति दुवै पक्षले राख्नु पर्नेछ।",
        }),
        Paragraph({
            "en": "Landlord: {{ landlord_name }}   Signature: ____________\nTenant: {{ tenant_name }}   Signature: ____________\nWitness 1 (Landlord side): ____________\nWitness 2 (Landlord side): ____________\nWitness 1 (Tenant side): ____________\nWitness 2 (Tenant side): ____________",
            "ne": "घरधनीः {{ landlord_name }}   दस्तखतः ____________\nबहालवालाः {{ tenant_name }}   दस्तखतः ____________\nसाक्षी १ (घरधनी तर्फबाट): ____________\nसाक्षी २ (घरधनी तर्फबाट): ____________\nसाक्षी १ (बहालवाला तर्फबाट): ____________\nसाक्षी २ (बहालवाला तर्फबाट): ____________",
        }),
    ],
    provisions=[
        {"law_title_ne": "मुलुकी देवानी संहिता, २०७४", "section": "386"},
        {"law_title_ne": "मुलुकी देवानी संहिता, २०७४", "section": "389"},
        {"law_title_ne": "मुलुकी देवानी संहिता, २०७४", "section": "402"},
    ],
)

POWER_OF_ATTORNEY = TemplateSpec(
    id="power_of_attorney",
    title={"en": "Power of attorney (अख्तियारनामा)", "ne": "अख्तियारनामा"},
    description={
        "en": "Authorizes someone else to act as your representative for a specific purpose.",
        "ne": "निश्चित काम गर्न कसैलाई आफ्नो प्रतिनिधिको रूपमा अख्तियार दिने कागजात।",
    },
    fields=[
        Field("principal_name", {"en": "Your full name (the person giving authority)", "ne": "तपाईंको पूरा नाम (अख्तियार दिने व्यक्ति)"}, "text"),
        Field("principal_address", {"en": "Your address", "ne": "तपाईंको ठेगाना"}, "text"),
        Field("principal_citizenship_no", {"en": "Your citizenship number", "ne": "तपाईंको नागरिकता नम्बर"}, "text"),
        Field("agent_name", {"en": "Representative's (agent's) full name", "ne": "प्रतिनिधि (एजेन्ट) को पूरा नाम"}, "text"),
        Field("agent_address", {"en": "Representative's address", "ne": "प्रतिनिधिको ठेगाना"}, "text"),
        Field("agent_citizenship_no", {"en": "Representative's citizenship number", "ne": "प्रतिनिधिको नागरिकता नम्बर"}, "text"),
        Field("purpose_description", {"en": "What the representative is authorized to do", "ne": "प्रतिनिधिलाई दिइएको अख्तियारको विवरण"}, "textarea"),
        Field("valid_until", {"en": "Valid until (optional)", "ne": "मान्य रहने मिति (वैकल्पिक)"}, "date", required=False, default=""),
    ],
    paragraphs=[
        Paragraph({"en": "Power of Attorney", "ne": "अख्तियारनामा"}, bold=True, align="center"),
        Paragraph({
            "en": ("I, {{ principal_name }}, residing at {{ principal_address }}, citizenship no. "
                   "{{ principal_citizenship_no }}, hereby appoint {{ agent_name }}, residing at "
                   "{{ agent_address }}, citizenship no. {{ agent_citizenship_no }}, as my representative "
                   "(प्रतिनिधि), under Section 591 of the National Civil Code, 2074 (मुलुकी देवानी संहिता, "
                   "२०७४, दफा ५९१), to do the following on my behalf:"),
            "ne": ("म {{ principal_name }}, ठेगाना {{ principal_address }}, नागरिकता नं. "
                   "{{ principal_citizenship_no }}, ले मुलुकी देवानी संहिता, २०७४ को दफा ५९१ बमोजिम श्री "
                   "{{ agent_name }}, ठेगाना {{ agent_address }}, नागरिकता नं. {{ agent_citizenship_no }} "
                   "लाई मेरो प्रतिनिधि नियुक्त गरी देहायको काम गर्ने अख्तियार प्रदान गर्दछुः"),
        }),
        Paragraph({"en": "{{ purpose_description }}", "ne": "{{ purpose_description }}"}),
        Paragraph({
            "en": ("Under Section 592 of the National Civil Code (मुलुकी देवानी संहिता, २०७४, दफा ५९२), acts "
                   "done by my representative within this authority will be treated as done by me. "
                   "{% if valid_until %}This power of attorney is valid until {{ valid_until }}.{% endif %}"),
            "ne": ("मुलुकी देवानी संहिता, २०७४ को दफा ५९२ बमोजिम मेरो प्रतिनिधिले अख्तियारको सीमाभित्र रही गरेको "
                   "काम कारबाही मैले नै गरेको मानिनेछ। {% if valid_until %}यो अख्तियारनामा मिति "
                   "{{ valid_until }} सम्म मान्य रहनेछ।{% endif %}"),
        }),
        Paragraph({
            "en": "\nPrincipal: {{ principal_name }}   Signature: ____________\nRepresentative: {{ agent_name }}   Signature: ____________\nDate: {{ today_bs }} B.S. ({{ today_ad }} A.D.)\nWitness 1: ____________   Witness 2: ____________",
            "ne": "\nअख्तियार दिने: {{ principal_name }}   दस्तखतः ____________\nप्रतिनिधि: {{ agent_name }}   दस्तखतः ____________\nमितिः {{ today_bs }} (अंग्रेजी मितिः {{ today_ad }})\nसाक्षी १: ____________   साक्षी २: ____________",
        }),
    ],
    provisions=[
        {"law_title_ne": "मुलुकी देवानी संहिता, २०७४", "section": "591"},
        {"law_title_ne": "मुलुकी देवानी संहिता, २०७४", "section": "592"},
    ],
)

AFFIDAVIT = TemplateSpec(
    id="affidavit",
    title={"en": "Affidavit (सपथपत्र / स्वघोषणा-पत्र)", "ne": "सपथपत्र / स्वघोषणा-पत्र"},
    description={
        "en": "A general sworn written statement of facts, for use in support of another application or filing.",
        "ne": "अर्को निवेदन वा प्रक्रियाको समर्थनमा प्रयोग गरिने सामान्य लिखित सपथपत्र।",
    },
    fields=[
        Field("declarant_name", {"en": "Your full name", "ne": "तपाईंको पूरा नाम"}, "text"),
        Field("declarant_address", {"en": "Your address", "ne": "तपाईंको ठेगाना"}, "text"),
        Field("declarant_citizenship_no", {"en": "Your citizenship number", "ne": "तपाईंको नागरिकता नम्बर"}, "text"),
        Field("purpose_of_affidavit", {"en": "What this affidavit is for", "ne": "यो सपथपत्र केको लागि हो"}, "text"),
        Field("statement_text", {"en": "The facts you are declaring", "ne": "बयान गर्ने तथ्यहरू"}, "textarea"),
    ],
    paragraphs=[
        Paragraph({"en": "Affidavit", "ne": "सपथपत्र"}, bold=True, align="center"),
        Paragraph({
            "en": ("I, {{ declarant_name }}, residing at {{ declarant_address }}, citizenship no. "
                   "{{ declarant_citizenship_no }}, do hereby solemnly declare, for the purpose of "
                   "{{ purpose_of_affidavit }}, the following facts:"),
            "ne": ("म {{ declarant_name }}, ठेगाना {{ declarant_address }}, नागरिकता नं. "
                   "{{ declarant_citizenship_no }}, ले {{ purpose_of_affidavit }} प्रयोजनको लागि सत्य कुरा "
                   "गोप्य नराखी देहाय बमोजिम बयान गर्दछुः"),
        }),
        Paragraph({"en": "{{ statement_text }}", "ne": "{{ statement_text }}"}),
        Paragraph({
            "en": ("The above statement is true and correct to the best of my knowledge. If found false, "
                   "I am liable under prevailing law."),
            "ne": ("माथि लेखिएको व्यहोरा सत्य र ठिक छ, झुट्टा ठहरे प्रचलित कानून बमोजिम सहुँला बुझाउँला।"),
        }),
        Paragraph({
            "en": "\nDeclarant: {{ declarant_name }}   Signature: ____________\nDate: {{ today_bs }} B.S. ({{ today_ad }} A.D.)",
            "ne": "\nबयान गर्नेः {{ declarant_name }}   दस्तखतः ____________\nमितिः {{ today_bs }} (अंग्रेजी मितिः {{ today_ad }})",
        }),
    ],
    provisions=[],
)

CONSUMER_COMPLAINT = TemplateSpec(
    id="consumer_complaint",
    title={"en": "Consumer complaint letter", "ne": "उपभोक्ता गुनासो पत्र"},
    description={
        "en": "A written complaint to the consumer protection authority about a defective product or unfair trade practice.",
        "ne": "बिग्रेको सामान वा अनुचित व्यापारिक क्रियाकलापका बारे उपभोक्ता संरक्षण निकायलाई दिइने लिखित गुनासो।",
    },
    fields=[
        Field("complainant_name", {"en": "Your full name", "ne": "तपाईंको पूरा नाम"}, "text"),
        Field("complainant_address", {"en": "Your address", "ne": "तपाईंको ठेगाना"}, "text"),
        Field("complainant_phone", {"en": "Your phone number", "ne": "तपाईंको फोन नम्बर"}, "text"),
        Field("seller_name", {"en": "Seller / business name", "ne": "पसल / व्यवसायको नाम"}, "text"),
        Field("seller_address", {"en": "Seller's address", "ne": "पसलको ठेगाना"}, "text"),
        Field("product_or_service", {"en": "Product or service involved", "ne": "सम्बन्धित वस्तु वा सेवा"}, "text"),
        Field("purchase_date", {"en": "Date of purchase", "ne": "किनेको मिति"}, "date"),
        Field("amount_involved", {"en": "Amount paid (NPR)", "ne": "तिरेको रकम (रु.)"}, "number"),
        Field("complaint_details", {"en": "What went wrong", "ne": "के समस्या भयो"}, "textarea"),
        Field("relief_sought", {"en": "What you want done about it", "ne": "के समाधान चाहनुहुन्छ"}, "textarea"),
    ],
    paragraphs=[
        Paragraph({"en": "To: Department of Commerce, Supplies and Consumer Protection",
                    "ne": "श्री वाणिज्य, आपूर्ति तथा उपभोक्ता संरक्षण विभाग"}, bold=True),
        Paragraph({"en": "Date: {{ today_bs }} B.S.", "ne": "मितिः {{ today_bs }}"}),
        Paragraph({"en": "Subject: Consumer complaint", "ne": "विषयः उपभोक्ता गुनासो"}, bold=True, align="center"),
        Paragraph({
            "en": ("I, {{ complainant_name }}, address {{ complainant_address }}, phone "
                   "{{ complainant_phone }}, purchased {{ product_or_service }} from {{ seller_name }} "
                   "({{ seller_address }}) on {{ purchase_date }} for NPR {{ amount_involved }}. "
                   "{{ complaint_details }}"),
            "ne": ("म {{ complainant_name }}, ठेगाना {{ complainant_address }}, फोन {{ complainant_phone }}, "
                   "ले मिति {{ purchase_date }} मा {{ seller_name }} ({{ seller_address }}) बाट "
                   "{{ product_or_service }} रु. {{ amount_involved }} मा किनेको थिएँ। {{ complaint_details }}"),
        }),
        Paragraph({
            "en": ("Under Section 3 of the Consumer Protection Act, 2075 (उपभोक्ता संरक्षण ऐन, २०७५, दफा ३), "
                   "I am entitled to safe, quality goods and services and protection from unfair trade "
                   "practices. Under Section 36 (दफा ३६), I am filing this written complaint with your office, "
                   "and under Section 50 (दफा ५०), I am entitled to compensation for the loss this has caused "
                   "me."),
            "ne": ("उपभोक्ता संरक्षण ऐन, २०७५ को दफा ३ बमोजिम मलाई सुरक्षित र गुणस्तरीय वस्तु/सेवा तथा अनुचित "
                   "व्यापारिक क्रियाकलापबाट संरक्षण पाउने अधिकार छ। दफा ३६ बमोजिम यो लिखित उजुरी हजुरको "
                   "कार्यालयमा दिइरहेको छु, र दफा ५० बमोजिम यसबाट भएको हानिको क्षतिपूर्ति पाउने हकदार छु।"),
        }),
        Paragraph({"en": "What I am requesting: {{ relief_sought }}", "ne": "मेरो अनुरोधः {{ relief_sought }}"}),
        Paragraph({
            "en": "\nComplainant: {{ complainant_name }}   Signature: ____________\nDate: {{ today_bs }} B.S. ({{ today_ad }} A.D.)",
            "ne": "\nगुनासोकर्ताः {{ complainant_name }}   दस्तखतः ____________\nमितिः {{ today_bs }} (अंग्रेजी मितिः {{ today_ad }})",
        }),
    ],
    provisions=[
        {"law_title_ne": "उपभोक्ता संरक्षण ऐन, २०७५", "section": "3"},
        {"law_title_ne": "उपभोक्ता संरक्षण ऐन, २०७५", "section": "36"},
        {"law_title_ne": "उपभोक्ता संरक्षण ऐन, २०७५", "section": "50"},
    ],
)

TEMPLATES: dict[str, TemplateSpec] = {
    t.id: t for t in [
        LEGAL_NOTICE_SALARY,
        LEGAL_NOTICE_DEPOSIT,
        RENTAL_AGREEMENT,
        POWER_OF_ATTORNEY,
        AFFIDAVIT,
        CONSUMER_COMPLAINT,
    ]
}
