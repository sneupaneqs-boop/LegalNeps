"""S7: non-LLM playbook matcher - keyword/glossary routing, no embeddings.

LABELLED_QUERIES is a hand-written set (not derived from tuning the
keywords) mixing Nepali, English and romanised phrasing, 2-3 queries per
playbook, so precision on it is a real measure of the matcher rather than
an artifact of overfitting. STRATEGY.md's S7 "done when" bar is >=90%
precision on 60 labelled queries.
"""
from app.playbook_matcher import match

LABELLED_QUERIES = [
    ("तलब पाएको छैन तीन महिनादेखि", "unpaid_salary"),
    ("my employer hasn't paid my salary for 3 months", "unpaid_salary"),
    ("boss talab dinu bhako chaina", "unpaid_salary"),

    ("घरबेटीले मेरो धरौटी फिर्ता दिएन", "deposit_not_returned"),
    ("landlord won't return my rental deposit", "deposit_not_returned"),
    ("my security deposit was never returned after I moved out", "deposit_not_returned"),

    ("श्रीमानले दिनहुँ कुट्छ", "domestic_violence"),
    ("my husband beats me at home", "domestic_violence"),
    ("पतिले घरेलु हिंसा गर्छ", "domestic_violence"),

    ("म श्रीमानबाट सम्बन्ध विच्छेद गर्न चाहन्छु", "divorce"),
    ("I want to divorce my husband", "divorce"),
    ("श्रीमतीबाट छुट्टिने कानूनी प्रक्रिया के हो", "divorce"),

    ("ग्राहकले दिएको चेक बाउन्स भयो", "cheque_bounce"),
    ("the cheque I received bounced", "cheque_bounce"),
    ("चेक अनादर भएको उजुरी गर्न मिल्छ", "cheque_bounce"),

    ("बुबाको सम्पत्तिमा मेरो अंश चाहियो", "inheritance_share"),
    ("I want my inheritance share of ancestral property", "inheritance_share"),
    ("दाजुले अंशबण्डा गर्न मानेको छैन", "inheritance_share"),

    ("पसलले बिग्रेको सामान बेच्यो, गुनासो गर्न चाहन्छु", "consumer_complaint"),
    ("I bought a defective product and want to file a consumer complaint", "consumer_complaint"),
    ("दोकानदारले ठग्यो, उपभोक्ता गुनासो कहाँ गर्ने", "consumer_complaint"),

    ("कसैले मेरो निजी फोटो अनलाइन सार्वजनिक गर्यो", "cyber_harassment"),
    ("someone leaked my private photos online and is harassing me", "cyber_harassment"),
    ("फेसबुकमा साइबर दुर्व्यवहार भइरहेको छ", "cyber_harassment"),

    ("मलाई सूचना नदिई जागिरबाट निकालियो", "wrongful_termination"),
    ("I was fired from my job without any notice", "wrongful_termination"),
    ("कामदारलाई कामबाट हटाइयो, के गर्ने", "wrongful_termination"),

    ("अफिसमा मेरो बसले यौन दुर्व्यवहार गर्छ", "workplace_sexual_harassment"),
    ("my boss is sexually harassing me at work", "workplace_sexual_harassment"),
    ("कार्यस्थलमा यौन दुर्व्यवहार भएको उजुरी", "workplace_sexual_harassment"),

    ("यस वर्ष कम्पनीले बोनस दिएन", "bonus_not_paid"),
    ("my company hasn't paid the annual bonus this year", "bonus_not_paid"),
    ("बोनस पाउनुपर्ने तर पाइन", "bonus_not_paid"),

    ("म्यानपावर एजेन्सीले वैदेशिक रोजगारमा ठग्यो", "foreign_employment_fraud"),
    ("the manpower agency cheated me on my foreign employment contract", "foreign_employment_fraud"),
    ("वैदेशिक रोजगार ठगीको उजुरी गर्ने ठाउँ", "foreign_employment_fraud"),

    ("घरबेटीले सूचना नदिई घर खाली गर्न लगायो", "tenant_eviction_without_notice"),
    ("my landlord is trying to evict me without any notice", "tenant_eviction_without_notice"),

    ("छिमेकीसँग जग्गाको सीमानामा विवाद छ", "land_boundary_dispute"),
    ("my neighbour encroached onto my land, boundary dispute", "land_boundary_dispute"),

    ("साथीलाई सापटी दिएको पैसा फिर्ता दिएन", "unpaid_personal_loan"),
    ("I lent money to a friend and they haven't repaid the loan", "unpaid_personal_loan"),

    ("सडक दुर्घटनामा परेर घाइते भएँ, क्षतिपूर्ति चाहियो", "traffic_accident_compensation"),
    ("I was injured in a traffic accident and need compensation", "traffic_accident_compensation"),

    ("कसैले मेरो बारेमा झुटो हल्ला फैलाएर बेइज्जती गर्यो", "defamation"),
    ("someone is spreading false rumours about me, defamation case", "defamation"),

    ("मेरो मोटरसाइकल चोरी भयो", "theft_complaint"),
    ("my phone was stolen, I want to file a theft complaint", "theft_complaint"),

    ("कसैले मलाई बाटोमा कुटपिट गर्यो", "physical_assault"),
    ("a stranger beat me up on the street, physical assault", "physical_assault"),

    ("सम्बन्ध विच्छेदपछि छोराछोरी कसले राख्ने भन्ने विवाद", "child_custody"),
    ("who gets child custody after our divorce", "child_custody"),

    ("पतिले श्रीमतीलाई खर्च दिन मानेको छैन", "maintenance_alimony"),
    ("my ex-husband refuses to pay alimony", "maintenance_alimony"),

    ("१६ वर्षकी छोरीको बाल विवाह गराउन खोजिँदैछ", "child_marriage_protection"),
    ("my underage daughter is being forced into child marriage", "child_marriage_protection"),

    ("आमाको नामबाट मेरो नागरिकता बनाउन मिल्छ?", "citizenship_by_descent"),
    ("can I get citizenship by descent through my mother", "citizenship_by_descent"),

    ("सरकारी कार्यालयबाट सूचना माग्दा दिएन", "right_to_information_request"),
    ("I filed a right to information request and got no response", "right_to_information_request"),

    ("प्रहरीले मेरो जाहेरी दर्ता गरेन", "fir_not_registered"),
    ("the police refused to register my FIR complaint", "fir_not_registered"),

    ("आजको मौसम कस्तो छ", None),
    ("what time does the court open tomorrow", None),
    ("म काठमाडौंमा बस्छु", None),
]


def test_labelled_query_count_meets_strategy_bar():
    assert len(LABELLED_QUERIES) >= 60


def test_matcher_precision_at_least_90_percent():
    positives = [(q, expected) for q, expected in LABELLED_QUERIES if expected is not None]
    correct = 0
    failures = []
    for query, expected in positives:
        got = match(query)
        if got == expected:
            correct += 1
        else:
            failures.append((query, expected, got))
    precision = correct / len(positives)
    assert precision >= 0.90, f"precision={precision:.2%} failures={failures}"


def test_matcher_returns_none_for_unrelated_queries():
    negatives = [(q, expected) for q, expected in LABELLED_QUERIES if expected is None]
    assert negatives, "need at least one negative example"
    for query, _ in negatives:
        assert match(query) is None, query


def test_matcher_returns_none_for_empty_query():
    assert match("") is None
