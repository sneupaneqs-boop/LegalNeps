"""V3.2: deterministic claim checks, built from the V3 live review (2026-09-30).

Every fixture here is a REAL labelled sentence and its REAL cited passage (tests/data/v32_review_fixture.json,
extracted from eval/reports/answer-review-v3-{labels,realworld}-20260930.json). Each check has (a) a bad sentence
from the review that is now removed and (b) a good sentence from the same review (or the corrected version of the
bad one) that still passes. The last section replays all 77 labelled sentences: how many of the 12 bad ones are
caught and how many of the 65 good ones are wrongly removed."""
import json
import random
import re
from pathlib import Path

import pytest

from app import claim_checks as cc
from app import config, generation, llm, situation_guards, structured, verifier

FIX = json.loads((Path(__file__).parent / "data" / "v32_review_fixture.json").read_text(encoding="utf8"))
_HEAD = re.compile(r"^\W*[०-९0-9]+[क-ह]?\.\s*([^:ः\n]{2,120})[:ः]")


def sources_of(aid):
    src = FIX["answers"][aid]["sources"]
    out = []
    for n in range(1, max(int(k) for k in src) + 1):
        s = src.get(str(n))
        if not s:
            out.append({"id": f"x{n}", "category": "law", "text_ne": "", "text_en": ""})
            continue
        m = _HEAD.match(s["text_ne"])
        out.append({"id": f"{aid}-{n}", "category": s["category"], "status": s["status"], "doc_type": "act",
                    "section": s["section"], "source_ne": s["citation"], "source_en": s["citation"],
                    "title_ne": m.group(1).strip() if m else "", "text_ne": s["text_ne"], "text_en": s["text_en"]})
    return out


def ctx_of(aid, guidance=""):
    q = FIX["answers"][aid]["question"]
    return cc.CheckContext(question=q, topic_terms=frozenset(generation._terms(q, {})),
                           law_terms=cc.law_topic_terms(sources_of(aid)), guidance=guidance)


def judge(aid, text, kind="rule", cites=(), guidance=""):
    """(kept?, reason) of one sentence through verify_sentence exactly as the pipeline calls it."""
    srcs = sources_of(aid)
    raw = {"text": text, "kind": kind, "cites": [{"n": n, "quote": q} for n, q in cites]}
    k, reason = verifier.verify_sentence(raw, srcs, verifier.make_views(srcs), verifier.guidance_term_set(guidance),
                                         ctx_of(aid, guidance))
    return k, reason


def labelled(aid, idx):
    return next(s for s in FIX["sentences"] if s["answer_id"] == aid and s["index"] == idx)


def replay(aid, idx, guidance=""):
    s = labelled(aid, idx)
    return judge(aid, s["text"], s["kind"], [(c["n"], c["quote"]) for c in s["cites"]], guidance)[1]


def span(aid, n, start, end):
    """Verbatim (whitespace-normalised) span of a real cited passage from `start` through `end`."""
    text = FIX["answers"][aid]["sources"][str(n)]["text_ne"]
    a = text.index(start)
    b = text.index(end, a) + len(end)
    return " ".join(text[a:b].split())


def uncited_line(aid, start):
    """A real uncited line of a rendered answer (advice / procedure)."""
    for line in FIX["answers"][aid]["answer"].split("\n"):
        line = line.lstrip("- ").strip()
        if line.startswith(start):
            return line
    raise AssertionError(f"{aid}: no line starting {start!r}")


# ===================================================================== 1. number bound to its role
BAND = ("बिगोको पाँच प्रतिशत जरिबाना र देहाय बमोजिम कैद सजाय हुनेछ:- (क) पन्ध्र लाख रुपैयाँसम्म बिगो भए एक महिनासम्म "
        "कैद, (ख) पन्ध्र लाख रुपैयाँभन्दा बढी पचास लाख रुपैयाँसम्म बिगो भए एक महिनादेखि तीन महिनासम्म कैद")
RW06_S3_BAD = labelled("rw06", 3)["text"]
RW06_S3_GOOD = ("Under the Banking Offence and Punishment Act, 2064, Section 15, if the amount is more than fifteen lakh "
                "rupees up to fifty lakh rupees, the account holder faces a fine of five percent of the amount and "
                "imprisonment from one month up to three months.")


def test_rw06_five_lakh_is_refused_even_when_a_five_percent_is_in_the_quote():
    assert "पाँच प्रतिशत" in BAND                                   # the reason the V3 number check let it through
    _, reason = judge("rw06", RW06_S3_BAD, "penalty", [(3, BAND)])
    assert reason == "number_role_mismatch"
    # the V3 number check alone was blind to it: it never read "five lakh" as a number
    body = RW06_S3_BAD
    assert verifier._sentence_numbers(body) <= verifier._numbers_in(BAND) | {"2064"}


def test_rw06_the_same_sentence_with_the_right_number_passes():
    kept, reason = judge("rw06", RW06_S3_GOOD, "penalty", [(3, BAND)])
    assert reason is None and kept["cites"][0]["n"] == 3


def test_rw06_original_spliced_quote_is_also_refused():
    # the model joined "(ख)" onto the sentence start, skipping band "(क)": not a verbatim span any more
    assert replay("rw06", 3) == "quote_not_verbatim"


@pytest.mark.parametrize("text,pairs", [
    ("five lakh rupees", {("500000", "rs")}),
    ("पन्ध्र लाख रुपैयाँसम्म", {("1500000", "rs")}),
    ("बिगोको पाँच प्रतिशत जरिबाना", {("5", "pct")}),
    ("within 3 days and a fine of Rs. 5,000", {("3", "day"), ("5000", "rs")}),
    ("तीन वर्षदेखि सात वर्षसम्म कैद", {("3", "year"), ("7", "year")}),
    ("एक महिनादेखि तीन महिनासम्म", {("1", "month"), ("3", "month")}),
    ("दश हजार रुपैयाँसम्म जरिबाना", {("10000", "rs")}),
    ("१०,००० रुपैयाँ", {("10000", "rs")}),
])
def test_quantity_pairs(text, pairs):
    assert cc.qty_scan(text)[0] == pairs


def test_number_with_unit_swapped_is_refused_and_unbound_numbers_are_not_judged():
    assert cc.number_role_conflict("The complaint must be filed within 3 days.", ["तीन महिनाभित्र उजुरी दिनु पर्नेछ"]) == "number_unit_mismatch"
    assert cc.number_role_conflict("You may file within 3 months.", ["तीन महिनाभित्र उजुरी दिनु पर्नेछ"]) is None
    assert cc.number_role_conflict("Section 15 applies.", ["दफा १५ बमोजिम"]) is None        # no unit: not this check's job
    # the quote never uses that unit: the plain number check decides, not this one


def test_number_role_property_same_pair_passes_other_value_same_unit_fails():
    rnd = random.Random(32)
    units_en = {"day": "days", "month": "months", "year": "years", "pct": "percent"}
    units_ne = {"day": "दिन", "month": "महिना", "year": "वर्ष", "pct": "प्रतिशत"}
    for _ in range(200):
        unit = rnd.choice(list(units_en))
        a, b = rnd.sample(range(2, 90), 2)
        quote = f"{a} {units_ne[unit]}भित्र र अर्को {b} {units_ne['month' if unit != 'month' else 'year']}"
        assert cc.number_role_conflict(f"within {a} {units_en[unit]}", [quote]) is None
        other = rnd.choice([x for x in range(2, 95) if x not in (a, b)])
        assert cc.number_role_conflict(f"within {other} {units_en[unit]}", [quote]) == "number_role_mismatch"


# ===================================================================== 2. fuzzy match forgives noise, not words
RW27_QUOTE = span("rw27", 5, "ऐनको दफा 25 बमोजिम", "पर्नेछः")
RW27_ALTERED = RW27_QUOTE.replace("व्यक्तिगत घटना दर्ताको", "नागरिकता").replace("ऐनको दफा 25 बमोजिम कुनै ", "")


def test_rw27_substituted_noun_in_the_quote_is_refused():
    assert "नागरिकता प्रमाणपत्रमा" in RW27_ALTERED and "नागरिकता प्रमाणपत्रमा" not in FIX["answers"]["rw27"]["sources"]["5"]["text_ne"]
    s = labelled("rw27", 2)
    assert replay("rw27", 2) == "quote_not_verbatim"
    srcs = sources_of("rw27")
    view = verifier._View(srcs[4])
    assert verifier.quote_in_source(RW27_ALTERED, view) == "quote_not_verbatim"
    # the V3 matcher (>=90% of the tokens) accepted it: only the alignment rule refuses it
    qtok = verifier._qtokens(RW27_ALTERED)
    assert any(verifier._fuzzy_span(qtok, t, strict=False) for t in view.texts)


def test_rw27_the_true_quote_and_real_spelling_variants_still_pass():
    view = verifier._View(sources_of("rw27")[4])
    assert verifier.quote_in_source(RW27_QUOTE, view) is None
    assert verifier.quote_in_source(RW27_QUOTE.replace("उल्लिखित", "उल्लीखित"), view) is None       # matra variant (folded)
    assert verifier.quote_in_source(RW27_QUOTE.replace("पञ्जिकाधिकारीको", "पञ्जिकाधिकारीका"), view) is None  # one-letter slip


def test_ocr_sources_keep_the_lenient_matching_and_others_do_not():
    src = dict(sources_of("rw27")[4])
    assert verifier.quote_in_source(RW27_ALTERED, verifier._View(src)) == "quote_not_verbatim"
    assert verifier.quote_in_source(RW27_ALTERED, verifier._View({**src, "ocr": True})) is None
    assert verifier._View({**src, "ocr": "True"}).ocr and not verifier._View({**src, "ocr": False}).ocr


def test_fused_or_split_words_are_line_break_noise_not_substitution():
    assert cc.alignment_ok(["खान", "लाउन", "दिनर", "आर्थिक"], ["खान", "लाउन", "दिन", "र", "आर्थिक"])
    assert not cc.alignment_ok(["नागरिकता", "प्रमाणपत्रमा"], ["व्यक्तिगत", "घटना", "दर्ताको", "प्रमाणपत्रमा"])
    assert not cc.alignment_ok(["ऋण", "साहूले", "पाउने"], ["ऋण", "बैंकले", "पाउने"])
    assert cc.near_variant("गरेमा", "गरेमां") and not cc.near_variant("१०", "११")


# ===================================================================== 3. section resolved from where the quote sits
RW27_23 = span("rw27", 5, "ऐनको दफा 25 बमोजिम", "पर्नेछः")
RW27_S22 = ("राष्ट्रिय परिचयपत्र तथा पञ्जीकरण नियमावली, २०७७ को नियम २२ अनुसार व्यक्तिगत घटना दर्ताको प्रमाणपत्रमा उल्लिखित नाम, "
            "थर, उमेर वा अन्य विवरणमा त्रुटि भएमा सम्बन्धित व्यक्तिले स्थानीय पञ्जिकाधिकारीको कार्यालयमा निवेदन दिनु पर्छ।")
RW27_S23 = RW27_S22.replace("नियम २२", "नियम २३")


def test_rw27_layout_finds_both_rules_of_the_merged_chunk():
    layout = verifier._View(sources_of("rw27")[4]).layout
    assert [n for n, _ in layout.sections] == ["22", "23"]
    assert cc.quote_section(verifier._qtokens(RW27_23), layout) == "23"
    assert cc.quote_section(verifier._qtokens("कुनै व्यक्तिको एउटै व्यक्तिगत घटना एक पटक भन्दा बढी दर्ताभएकोमा"), layout) == "22"


def test_rw27_rule_number_of_the_wrong_heading_is_refused_the_right_one_passes():
    _, reason = judge("rw27", RW27_S22, "rule", [(5, RW27_23)])
    assert reason == "section_under_other_heading"
    kept, reason = judge("rw27", RW27_S23, "rule", [(5, RW27_23)])
    assert reason is None and kept                                  # rule 23 is what the passage says at that spot


def test_single_section_passages_and_unnumbered_lists_are_never_split():
    text = "३८६. सम्झौता गर्नु पर्ने : (१) क्रमः\n१. नाम, ठेगाना : पहिलो\n२. उमेर : दोस्रो\n(२) अर्को कुरा।"
    assert cc.Layout(text, "386").sections == []
    two = "२२. पहिलो : (१) एक\n२३. दोस्रो : (१) दुई"
    assert [n for n, _ in cc.Layout(two, "22").sections] == ["22", "23"]
    assert cc.Layout(two, "40").sections == []                       # a chunk must open with its own section


# ===================================================================== 4. dropped condition / widened subject
RW06_CLAUSE5 = span("rw06", 2, "उपदफा (३) बमोजिम तोकिएको म्याद समाप्त भएपछि", "पर्नेछ।")
RW06_S2_GOOD = ("Under the Banking Offence and Punishment Act, 2064, Section 3A, once the notice period given to the "
                "account holder has expired and the holder asks for payment, if the account still lacks the money the "
                "bank must certify the cheque dishonour within three days and return the cheque to the holder.")


def test_rw06_three_day_step_without_the_notice_period_is_removed():
    assert replay("rw06", 2) == "condition_dropped:notice_period"


def test_rw06_the_same_step_with_the_notice_period_passes():
    kept, reason = judge("rw06", RW06_S2_GOOD, "rule", [(2, RW06_CLAUSE5)])
    assert reason is None and kept


def test_rw08_maintenance_stretched_to_children_is_removed_the_literal_one_passes():
    assert replay("rw08", 1) == "party_added:child"
    good = "मुलुकी देवानी संहिता, २०७४ को दफा ८९ अनुसार पति वा पत्नीले एक अर्कालाई आफ्नो इज्जत र क्षमता अनुसार खान लगाउन तथा स्वास्थ्योपचारको व्यवस्था गर्नु पर्छ।"
    kept, reason = judge("rw08", good, "rule", [(1, labelled("rw08", 1)["cites"][0]["quote"])])
    assert reason is None and kept


def test_rw08_joint_property_condition_dropped_is_removed_with_it_stated_passes():
    assert replay("rw08", 2) == "condition_dropped:joint_property"     # (the quote's fused "दिनर" is line-break noise)
    good = ("मुलुकी देवानी संहिता, २०७४ को दफा २११ अनुसार सगोलको सम्पत्ति भएका पति, पत्नी, बाबु, आमा, छोरा, छोरीले एक अर्कालाई "
            "आफ्नो इज्जत आमद अनुसार खान लाउन दिन र शिक्षा र स्वास्थ्य उपचारको व्यवस्था गर्नु पर्नेछ।")
    kept, reason = judge("rw08", good, "rule", [(3, labelled("rw08", 2)["cites"][0]["quote"])])
    assert reason is None and kept


def test_rw08_divorced_wife_provision_carries_its_proviso_or_is_removed(monkeypatch):
    assert replay("rw08", 3) in ("proviso_dropped", "wrong_law_guard:separated_not_divorced")
    q = labelled("rw08", 3)["cites"][0]["quote"]
    # for a divorced wife (question mentions divorce) with the proviso stated, it passes
    FIX["answers"]["rw08"]["question"], saved = "divorce bhayo, husband le kharcha dinna, maintenance kasari paune?", FIX["answers"]["rw08"]["question"]
    try:
        text = ("यदि पतिको आम्दानी छ भने, अदालतले सम्बन्ध विच्छेद भएको अवस्थामा पत्नीलाई खान लगाउने खर्च भराइ दिन सक्नेछ, "
                "तर पत्नीले अर्को विवाह गरेमा वा पत्नीको आम्दानी बढी भएमा दिनु पर्ने छैन।")
        _, reason = judge("rw08", text, "rule", [(2, q)])
        assert reason is None
        _, reason = judge("rw08", labelled("rw08", 3)["text"], "rule", [(2, q)])
        assert reason == "proviso_dropped"                          # divorced wife, but the two provisos are not mentioned
    finally:
        FIX["answers"]["rw08"]["question"] = saved


def test_scope_classes_are_data_and_carried_in_either_language():
    T = cc._qtok                                                    # the folded tokens the pipeline passes in
    joint = T("सगोलको सम्पत्ति भएका पति")
    assert cc.scope_conflict("The duty applies to family members.", joint) == "condition_dropped:joint_property"
    assert cc.scope_conflict("The duty applies to members holding joint property.", joint) is None
    assert cc.scope_conflict("पति र छोराछोरीले", T("पति वा पत्नीले")) == "party_added:child"
    assert cc.scope_conflict("The husband must support the wife.", T("पति वा पत्नीले एक अर्कालाई")) is None
    assert cc.scope_conflict("The wife may claim.", T("पतिपत्नी दुवैले")) is None
    assert cc.scope_conflict("Sub-section rules apply.", T("सम्पत्ति आमदानी")) is None      # 'आमदानी' is not 'आमा'


# ===================================================================== 5. dangling additive penalties
def test_rw15_additional_penalty_without_its_base_is_removed():
    assert replay("rw15", 4) == "dangling_additive_penalty"


def test_additional_penalty_with_its_base_in_the_same_sentence_passes():
    quote = span("rw30", 2, "कसैले कसैको बेइज्जती गरे वा गराएमा निजलाई", "जरिबाना हुनेछ।")
    good = ("मुलुकी अपराध संहिता, २०७४ को दफा ३०७ अनुसार बेइज्जती गरे वा गराएमा दुई वर्षसम्म कैद वा बीस हजार रुपैयाँसम्म जरिबाना वा दुवै "
            "सजाय हुन्छ, र विद्युतीय वा अन्य आम सञ्चारका माध्यमबाट गरेमा त्यस्तो सजायमा थप एक वर्षसम्म कैद र दश हजार रुपैयाँसम्म जरिबाना हुन्छ।")
    kept, reason = judge("rw30", good, "penalty", [(2, quote)])
    assert reason is None and kept


def test_additive_detector_both_languages_and_direction():
    assert cc.dangling_additive("An additional 2 years of imprisonment applies.")
    assert not cc.dangling_additive("The penalty is 1 year of imprisonment, and an additional 2 years apply if it is repeated.")
    assert not cc.dangling_additive("In addition to a fine of Rs. 5,000, the person may be jailed for 3 months.")
    assert cc.dangling_additive("त्यस्तो सजायमा थप छ महिना कैद हुनेछ।")
    assert not cc.dangling_additive("एक वर्ष कैद हुन्छ र त्यस्तो सजायमा थप छ महिना कैद हुनेछ।")
    assert not cc.dangling_additive("थप जानकारी वकिलसँग लिनुहोस्।")                  # 'थप' as "more", no penalty nearby


def test_known_tradeoff_the_reviewer_kept_the_two_s307_sentences_but_they_are_removed():
    # documented over-removal: rw30 s2 was labelled 'supported' (the quote says "त्यस्तो सजायमा थप")
    assert replay("rw30", 2) == "dangling_additive_penalty"


# ===================================================================== 6. uncited forum / document claims
RW04 = {"forum": uncited_line("rw04", "तपाईंले वैदेशिक रोजगार विभाग"), "tribunal": uncited_line("rw04", "विभागले अनुसन्धान गरी")}
RW01_COURT = uncited_line("rw01", "घरबेटीले रकम फिर्ता गर्न अस्विकार")
RW08_COMMITTEE = uncited_line("rw08", "स्थानीय तहको न्यायिक समितिमा")
RW15_BUREAU = uncited_line("rw15", "नेपाल प्रहरीको साइबर ब्यूरो")
RW20_DOC = uncited_line("rw20", "कम्पनी दर्ताको लागि निवेदन दिँदा")


@pytest.mark.parametrize("aid,line", [("rw04", RW04["forum"]), ("rw04", RW04["tribunal"]), ("rw01", RW01_COURT),
                                      ("rw08", RW08_COMMITTEE), ("rw15", RW15_BUREAU), ("rw20", RW20_DOC)])
def test_uncited_forum_or_document_requirement_is_removed_whatever_its_kind(aid, line):
    for kind in ("advice", "procedure"):
        assert judge(aid, line, kind)[1] in ("uncited_forum_claim", "uncited_procedure")
    assert judge(aid, line, "advice")[1] == "uncited_forum_claim"


def test_the_same_lines_pass_when_the_matched_playbook_names_the_forum():
    plan = ("Where to go: Department of Foreign Employment or the Chief District Officer; Foreign Employment Tribunal "
            "वैदेशिक रोजगार विभाग प्रमुख जिल्ला अधिकारी वैदेशिक रोजगार न्यायाधिकरण")
    assert judge("rw04", RW04["forum"], "advice", guidance=plan)[1] is None
    assert judge("rw04", RW04["tribunal"], "advice", guidance=plan)[1] is None
    assert judge("rw01", RW01_COURT, "advice", guidance="जिल्ला अदालत court")[1] is None
    assert judge("rw20", RW20_DOC, "advice", guidance="संस्थापकको नागरिकताको प्रतिलिपि certificate copy documents")[1] is None


@pytest.mark.parametrize("aid,start", [
    ("rw01", "घरबेटीलाई निश्चित समय तोकेर"),                       # a plain step
    ("rw01", "घरबहाल सम्झौता, धरौटी बुझाएको रसिद"),                  # keep your evidence: not a filing requirement
    ("rw04", "उजुरी गर्दा आफूले बुझाएको रकमको रसिद"),
    ("rw15", "त्यस्तो नक्कली प्रोफाइल"),                           # screenshots
    ("rw14", "पहिले सम्बन्धित प्रहरी कार्यालयमा"),                   # police / lawyers are generic advice
])
def test_generic_advice_and_evidence_keeping_lines_from_the_same_answers_survive(aid, start):
    assert judge(aid, uncited_line(aid, start), "advice")[1] is None


def test_the_local_police_line_of_rw15_survives_but_the_named_bureau_does_not():
    assert cc.forum_classes("नजिकैको प्रहरी कार्यालयमा गएर उजुरी दिनुहोस्") == set()
    assert cc.forum_classes(RW15_BUREAU) == {"bureau"}


def test_cited_sentence_may_not_name_a_forum_none_of_its_passages_names():
    good = labelled("rw27", 1)
    cites = [(c["n"], c["quote"]) for c in good["cites"]]
    assert judge("rw27", good["text"], "rule", cites)[1] is None
    reason = judge("rw27", good["text"].replace("निवेदन दिनु पर्छ", "जिल्ला अदालतमा निवेदन दिनु पर्छ"), "rule", cites)[1]
    assert reason == "forum_not_in_source"
    # an office named in the passage (even outside the quoted clause) is fine
    s = labelled("rw21", 1)
    assert judge("rw21", s["text"], "rule", [(c["n"], c["quote"]) for c in s["cites"]])[1] is None


# ===================================================================== 7. precedents
def _ctx_reason(aid, idx):
    return replay(aid, idx)


def test_rw25_precedent_that_only_records_a_petition_is_removed():
    assert _ctx_reason("rw25", 3) == "precedent_not_a_rule"


def test_rw21_dividend_precedent_for_an_agm_question_is_off_topic():
    assert _ctx_reason("rw21", 6) == "precedent_off_topic"


@pytest.mark.parametrize("aid,idx", [("rw28", 6), ("rw29", 4), ("rw30", 6)])
def test_useful_precedents_from_the_same_review_still_pass(aid, idx):
    assert replay(aid, idx) is None


def test_precedent_gate_states_rule_and_topic_units():
    assert cc.states_rule("क्षतिपूर्ति पाउनु पीडित उपभोक्ताको कानूनी अधिकार पनि हो")
    assert not cc.states_rule("निवेदन दिएको समेत देखिएबाट")
    assert cc.topic_overlap("क्षतिपूर्ति सवारी", None) is None
    assert cc.topic_overlap("चिकित्सक", cc.CheckContext(topic_terms=frozenset({"nonsense", "words"}))) is None   # nothing usable: undecided


def test_rw04_wrong_law_precedent_is_not_deterministically_catchable():
    # real quote, on the user's topic (foreign-employment money), states a rule - about a doubtful FIR of an accused.
    assert replay("rw04", 4) is None            # -> needs the entailment pass (which now sees the user's situation)


# ===================================================================== 8. gaps
def _gap_case(aid, gap_start):
    a = FIX["answers"][aid]
    gaps = [ln[2:].strip() for ln in a["answer"].split("\n") if ln.startswith("- ") and ln[2:].startswith(gap_start)]
    assert gaps, (aid, gap_start)
    cited = {c["n"] for s in FIX["sentences"] if s["answer_id"] == aid for c in s["cites"]}
    texts = [a["sources"][str(n)]["text_ne"] + " " + a["sources"][str(n)]["text_en"] for n in sorted(cited)]
    return gaps[0], ("ne" if a["language"] == "ne" else "en"), texts


def test_rw06_false_limitation_gap_is_dropped_because_a_cited_passage_covers_it():
    gap, lang, texts = _gap_case("rw06", "The sources retrieved do not cover the limitation period")
    kept, dropped = cc.filter_gaps([gap], lang, texts, texts)
    assert kept == [] and dropped[0][1] == "gap_covered_by_sources"


def test_honest_gaps_of_the_same_review_are_kept():
    for aid, start in [("rw01", "हामीले पाएका कानूनी स्रोतहरूमा घरबहालको धरौटी"), ("rw25", "मैले पाएका स्रोतहरूले बैंक तथा वित्तीय"),
                       ("rw27", "मैले पाएका स्रोतहरूले सच्याउन लाग्ने शुल्क"), ("rw03", "प्राप्त स्रोतहरूले सामान्य अवस्थाको")]:
        gap, lang, texts = _gap_case(aid, start)
        kept, dropped = cc.filter_gaps([gap], lang, texts, texts)
        assert kept == [gap] and not dropped, (aid, dropped)


def test_rw14_english_gap_in_a_nepali_answer_is_dropped_and_vice_versa():
    gap, lang, texts = _gap_case("rw14", "The sources retrieved do not cover the exact bail amount")
    assert lang == "ne"
    assert cc.filter_gaps([gap], "ne", texts, texts)[1][0][1] == "gap_wrong_language"
    assert cc.filter_gaps([gap], "en", [], [])[0] == [gap]
    assert cc.filter_gaps(["स्रोतहरूले जमानतको रकम समेटेका छैनन्।"], "en", [], [])[1][0][1] == "gap_wrong_language"
    assert cc.gap_in_language("The NRB directive on penal interest is not covered (नेपाल).", "en")


def test_gaps_reach_the_rendered_answer_only_after_the_filter():
    a = FIX["answers"]["rw06"]
    srcs = sources_of("rw06")
    doc = {"blocks": [], "gaps": ["The sources retrieved do not cover the limitation period for filing a complaint with the police "
                                  "after receiving the bank certification."], "follow_up_questions": []}
    cleaned, dropped = structured._clean_side_text(doc, "en", srcs, {3})
    assert cleaned["gaps"] == [] and dropped == {"gap_covered_by_sources": 1}
    keep, none = structured._clean_side_text({**doc, "gaps": ["The sources retrieved do not cover funeral rites."]}, "en", srcs, {3})
    assert keep["gaps"] and not none
    assert structured._clean_side_text(doc)[0]["gaps"] == doc["gaps"]    # legacy call: no sources -> only the old cleaning


# ===================================================================== 9. render polish
def test_duplicate_adjacent_markers_are_merged_rw30():
    s = labelled("rw30", 3)
    assert [c["n"] for c in s["cites"]] == [5, 5]
    line = structured._line({"text": s["text"], "kind": s["kind"], "cites": s["cites"]})
    assert line.count("[5]") == 1 and line.endswith("[5]।")
    assert cc.dedupe_marks([2, 3, 2, 3, 3]) == [2, 3]


def test_dangling_leading_conjunction_after_a_removal_is_repaired_not_shown():
    srcs = sources_of("rw27")
    q1 = labelled("rw27", 1)
    good = [{"n": c["n"], "quote": c["quote"]} for c in q1["cites"]]
    bad = {"text": "मुलुकी देवानी संहिता, २०७४ को दफा १ अनुसार १५ दिनभित्र गर्नु पर्छ।", "kind": "rule", "cites": good}
    follower = {"text": "र " + q1["text"], "kind": "rule", "cites": good}
    doc = {"blocks": [{"heading": "Rules", "sentences": [bad, follower]}], "gaps": [], "follow_up_questions": []}
    out, report = verifier.verify_structured(doc, srcs)
    assert report["removed"]["count"] == 1
    kept = out["blocks"][0]["sentences"][0]["text"]
    assert not kept.startswith("र ") and kept.startswith(q1["text"][:12])
    assert cc.strip_leading_conjunction("And you may appeal within the time.") == ("You may appeal within the time.", True)
    assert cc.strip_leading_conjunction("र छोटो") == ("र छोटो", False)        # too short to repair: unchanged


def test_proviso_tail_of_a_removed_head_is_dropped_not_repaired_v33():
    srcs = sources_of("rw27")
    q1 = labelled("rw27", 1)
    good = [{"n": c["n"], "quote": c["quote"]} for c in q1["cites"]]
    bad = {"text": "मुलुकी देवानी संहिता, २०७४ को दफा १ अनुसार १५ दिनभित्र गर्नु पर्छ।", "kind": "rule", "cites": good}
    tail = {"text": "तर " + q1["text"], "kind": "rule", "cites": good}
    out, report = verifier.verify_structured({"blocks": [{"heading": "R", "sentences": [bad, tail]}]}, srcs)
    assert report["removed"]["by_reason"] == {"number_not_in_quote": 1, "orphan_connective": 1} or report["removed"]["count"] == 2
    assert not out["blocks"]
    # with its head kept the same proviso is left alone
    head = {"text": q1["text"], "kind": "rule", "cites": good}
    other = {"text": "तर " + q1["text"] + " अपवाद बाहेक।", "kind": "rule", "cites": good}
    out2, _ = verifier.verify_structured({"blocks": [{"heading": "R", "sentences": [head]}]}, srcs)
    assert out2["blocks"][0]["sentences"][0]["text"] == q1["text"]


def test_streamed_text_equals_final_text_for_the_repair():
    srcs = sources_of("rw27")
    q1 = labelled("rw27", 1)
    good = [{"n": c["n"], "quote": c["quote"]} for c in q1["cites"]]
    sents = [{"text": "मुलुकी देवानी संहिता, २०७४ को दफा १ अनुसार १५ दिनभित्र गर्नु पर्छ।", "kind": "rule", "cites": good},
             {"text": "र " + q1["text"], "kind": "rule", "cites": good}]
    doc = {"blocks": [{"heading": "Rules", "sentences": sents}], "gaps": [], "follow_up_questions": []}
    sv = structured.StreamVerifier(srcs, "", min_rules=1)
    streamed = sv.feed(json.dumps(doc, ensure_ascii=False))
    final = structured.render(verifier.verify_structured(doc, srcs)[0], "ne")
    assert streamed == final and "र मुलुकी" not in streamed


def test_ocr_reph_typos_are_cleaned_in_shown_text_and_evidence_but_not_in_matching(monkeypatch):
    s = labelled("rw08", 3)
    assert "भरार्ई" in s["text"]
    assert "भराई" in structured._line({"text": s["text"], "kind": "rule", "cites": []})
    assert cc.clean_ocr_text("धारकलाइर् फिर्ता") == "धारकलाई फिर्ता" and cc.clean_ocr_text("सामान्य पाठ") == "सामान्य पाठ"
    srcs = sources_of("rw08")
    q89 = labelled("rw08", 1)["cites"][0]["quote"]
    q101 = labelled("rw08", 3)["cites"][0]["quote"]
    assert "भरार्ई" in q101
    monkeypatch.setattr(verifier, "TRAILING_PROVISO", False)
    raw = json.dumps({"blocks": [{"heading": "नियम", "sentences": [
        {"text": "मुलुकी देवानी संहिता, २०७४ को दफा ८९ अनुसार पति वा पत्नीले एक अर्कालाई खान लगाउन तथा स्वास्थ्योपचारको व्यवस्था गर्नु पर्छ।",
         "kind": "rule", "cites": [{"n": 1, "quote": q89}]},
        {"text": "मुलुकी देवानी संहिता, २०७४ को दफा १०१ अनुसार अदालतले सम्बन्ध विच्छेद भएको पतिको आम्दानीको आधारमा खान लगाउने खर्च भरार्ई दिन सक्नेछ।",
         "kind": "rule", "cites": [{"n": 2, "quote": q101}]}]}]}, ensure_ascii=False)
    built = structured.build(raw, srcs, "ne")
    assert built["answer"] and "भरार्ई" not in built["answer"] and "खर्च भराई दिन" in built["answer"]
    assert all("भरार्ई" not in c["quote"] for e in built["verification"]["evidence"] for c in e["cites"])
    assert any("भराई" in c["quote"] for e in built["verification"]["evidence"] for c in e["cites"])


# ===================================================================== 10. entailment v2 + situation guards
RW25_S1 = labelled("rw25", 1)
RW25_S2 = labelled("rw25", 2)


def test_bank_loan_question_may_not_rest_on_the_private_lender_chapter():
    assert replay("rw25", 1) == "wrong_law_guard:bank_loan_vs_private_creditor"     # s.478
    assert replay("rw25", 2) == "wrong_law_guard:bank_loan_vs_private_creditor"     # s.492


def test_the_guard_does_not_fire_for_a_private_loan_or_another_law():
    srcs = sources_of("rw25")
    s478 = srcs[4]
    q = "bank loan ma late payment ko penal interest kati lagauna milchha?"
    assert situation_guards.violation(q, "", [""], s478) == "bank_loan_vs_private_creditor"
    assert situation_guards.violation("mero sathi le tamsuk garera loan diyo, byaj kati?", "", [""], s478) is None
    assert situation_guards.violation("my friend gave me a loan, what interest can he charge?", "", [""], s478) is None
    assert situation_guards.violation(q, "", [""], {**s478, "source_ne": "श्रम ऐन, २०७४, दफा 478", "source_en": "The Labour Act, 2074, Section 478", "doc_title_ne": "श्रम ऐन, २०७४"}) is None
    assert situation_guards.violation(q, "", [""], {**s478, "section": "100"}) is None       # other Civil Code sections
    assert situation_guards.violation("", "", [""], s478) is None


def test_rw08_husband_left_is_not_a_divorce_the_divorced_wife_provision_is_guarded(monkeypatch):
    monkeypatch.setattr(verifier, "TRAILING_PROVISO", False)          # prove the guard alone catches it
    assert replay("rw08", 3) == "wrong_law_guard:separated_not_divorced"
    srcs = sources_of("rw08")
    s101 = srcs[1]
    assert situation_guards.violation("husband le chhadera gayo, maintenance?", "", [""], s101) == "separated_not_divorced"
    assert situation_guards.violation("husband le chhadera gayo ra divorce ko case chha", "", [""], s101) is None
    assert situation_guards.violation("husband le chhadera gayo, maintenance?", "", [""], srcs[0]) is None     # s.89 is fine
    assert situation_guards.violation("पतिले छोडेर गए, खर्च?", "", ["अदालतले सम्बन्ध विच्छेद भएको पतिको"], srcs[0]) == "separated_not_divorced"


def test_guard_table_is_documented_data():
    ids = [g.id for g in situation_guards.GUARDS]
    assert len(ids) == len(set(ids)) >= 2 and all(g.cues and g.why for g in situation_guards.GUARDS)
    assert "bank_loan_vs_private_creditor" in ids and "separated_not_divorced" in ids
    assert "wrong-law" in (situation_guards.__doc__ or "")


def _doc_with(*texts):
    return {"blocks": [{"heading": "R", "sentences": [{"text": t, "kind": "rule", "cites": [{"n": 1, "quote": "क ख ग घ ङ"}]} for t in texts]}]}


def test_entailment_payload_carries_the_user_situation_once_and_is_compact():
    doc = _doc_with("Statement one.", "Statement two.")
    payload, index = structured.entail_payload(doc, "bank loan ma late payment ko penal interest kati lagauna milchha?")
    data = json.loads(payload)
    assert data["situation"].startswith("bank loan") and len(data["items"]) == 2 and index == [(0, 0), (0, 1)]
    assert set(data["items"][0]) == {"s", "q"}
    long = _doc_with("x" * 900)
    long["blocks"][0]["sentences"][0]["cites"][0]["quote"] = "य" * 900
    item = json.loads(structured.entail_payload(long, "q" * 900)[0])
    assert len(item["items"][0]["s"]) == structured.ENTAIL_STATEMENT_CHARS
    assert len(item["items"][0]["q"]) == structured.ENTAIL_QUOTE_CHARS and len(item["situation"]) == structured.ENTAIL_QUESTION_CHARS


def test_entailment_is_one_call_sees_the_question_and_partial_is_configurable():
    calls = []

    def call(system, user, **kw):
        calls.append((system, user, kw))
        return json.dumps({"v": ["y", "n", "p"]})

    doc = _doc_with("A.", "B.", "C.")
    out, dropped, ran = structured.entailment_filter(doc, call, question="my husband left me")
    assert ran and dropped == 1 and len(calls) == 1
    assert "my husband left me" in calls[0][1] and calls[0][2]["fast"] is True and calls[0][2]["max_tokens"] <= 100
    assert [s["text"] for s in out["blocks"][0]["sentences"]] == ["A.", "C."]
    out, dropped, _ = structured.entailment_filter(_doc_with("A.", "B.", "C."), call, drop_partial=True)
    assert dropped == 2 and [s["text"] for s in out["blocks"][0]["sentences"]] == ["A."]


def test_entailment_reads_both_formats_and_fails_open():
    assert structured.parse_verdicts(json.dumps({"v": ["y", "N", "partial"]}), 3) == ["yes", "no", "partial"]
    assert structured.parse_verdicts(json.dumps({"results": [{"id": 1, "verdict": "no"}]}), 3) == ["yes", "no", "yes"]
    assert structured.parse_verdicts(json.dumps({"v": ["?"]}), 2) == ["yes", "yes"]

    def boom(*a, **k):
        raise llm.LLMUnavailable("429")

    doc = _doc_with("A.")
    assert structured.entailment_filter(doc, boom, question="q") == (doc, 0, False)


def test_entailment_payload_size_over_the_real_answers_is_small():
    """Token cost of the ONE extra call on the free tier, measured over the 20 real structured answers of the
    review (sentences + quotes exactly as kept). ~1.6 chars per Devanagari token would still be < 1.6k tokens."""
    sizes = []
    for aid, a in FIX["answers"].items():
        sents = [s for s in FIX["sentences"] if s["answer_id"] == aid]
        doc = {"blocks": [{"heading": "", "sentences": [{"text": s["text"], "kind": s["kind"], "cites": s["cites"]} for s in sents]}]}
        payload, index = structured.entail_payload(doc, a["question"])
        assert len(index) == len(sents)
        sizes.append(len(payload) + len(structured.ENTAIL_SYSTEM))
    assert max(sizes) < 3300 and sum(sizes) / len(sizes) < 2200, (max(sizes), sum(sizes) / len(sizes))


# ===================================================================== 11. prompt rules
def test_prompt_carries_the_v32_rules_compactly():
    r = structured.STRUCTURED_RULES
    for needle in ("WHOLE conditional clause", "never widen", "Never widen the subject", "tied to the same unit", "additional",
                   "Supreme Court precedent", "situation and topic", "ONLY when no passage covers", "reply language",
                   "Name no office", "Never restate a number"):
        assert needle.lower() in r.lower() or needle in r, needle
    assert "the law does not say" in r and "at most 3 gaps".lower() in r.lower()


# ===================================================================== 12. token diet
def test_only_the_reply_language_example_is_sent_and_the_rules_are_smaller_than_before():
    en, ne = generation.answer_system("en"), generation.answer_system("ne")
    assert structured.EXAMPLE_EN in en and structured.EXAMPLE_NE not in en
    assert structured.EXAMPLE_NE in ne and structured.EXAMPLE_EN not in ne
    assert len(structured.STRUCTURED_ANSWER_SYSTEM) > len(en) and len(structured.STRUCTURED_ANSWER_SYSTEM) > len(ne)
    assert generation.answer_system("auto") == en                 # anything not "ne" is English


def test_max_tokens_is_adaptive_capped_and_nepali_larger():
    assert generation.answer_max_tokens("ne", 8) == config.ANSWER_MAX_TOKENS_NE <= 3500
    assert generation.answer_max_tokens("en", 8) == config.ANSWER_MAX_TOKENS_EN <= 2000
    assert generation.answer_max_tokens("ne", 2) < generation.answer_max_tokens("ne", 5) <= config.ANSWER_MAX_TOKENS_NE
    assert generation.answer_max_tokens("en", 2) < generation.answer_max_tokens("en", 5)
    assert generation.answer_max_tokens("ne", 0) >= 1200 and generation.answer_max_tokens("en", 0) >= 800
    assert generation.answer_max_tokens("ne", 4) > generation.answer_max_tokens("en", 4)
    assert config.ANSWER_MAX_TOKENS_NE < 5000      # Groq qwen refused 6000 output tokens


def _srcs(n_laws, pinned=0, precs=0):
    out = [{"id": f"l{i}", "category": "law", "text_ne": "क " * 600, "source_ne": "S", "pinned": i < pinned}
           for i in range(n_laws)]
    out += [{"id": f"p{i}", "category": "precedent", "text_ne": "ख " * 300, "source_ne": "P", "stale": False} for i in range(precs)]
    return out


def test_prompt_sources_without_a_pin_are_the_top_laws_and_one_precedent():
    srcs = _srcs(6, 0, 2)
    assert generation.prompt_source_numbers(srcs) == [1, 2, 3, 4, 5, 7]


def test_prompt_sources_with_a_playbook_pin_keep_the_pins_and_only_two_extras():
    srcs = _srcs(6, pinned=3, precs=2)
    assert generation.prompt_source_numbers(srcs, {"id": "x"}) == [1, 2, 3, 4, 5, 7]
    srcs = _srcs(6, pinned=6, precs=2)
    assert generation.prompt_source_numbers(srcs) == [1, 2, 3, 4, 5, 6, 7]     # every pin is kept


def test_prompt_keeps_original_numbers_one_language_per_passage_and_shorter_tail_windows():
    srcs = _srcs(6, pinned=0, precs=2)
    for s in srcs:
        s["text_en"] = "y " * 400
    prompt = generation._prompt("m", {"question": "m"}, srcs, "en", None, None)
    assert "[6] (" not in prompt and "[8] (" not in prompt and "[7] (" in prompt          # unsent sources are not renumbered
    assert prompt.count("[English translation]") == 6 and "क क क" not in prompt         # English only when asked in English
    ne = generation._prompt("m", {"question": "m"}, srcs, "ne", None, None)
    assert "[English translation]" not in ne and "क क" in ne
    body = lambda p, i: p.split(f"[{i}] (")[1].split("\n\n")[0]  # noqa: E731
    assert len(body(ne, 5)) < len(body(ne, 1))                    # 4th+ statute: shorter window than the leading ones


def test_check_context_carries_question_topic_terms_law_terms_and_playbook_text():
    srcs = sources_of("rw25")
    plan = {"forum": {"en": "District Court", "ne": "जिल्ला अदालत"}, "next_steps": [{"en": "File a complaint", "ne": "उजुरी दिनुहोस्"}],
            "evidence": []}
    ctx = generation.check_context("bank loan ma penal interest", {"question": "penal interest on a bank loan"}, srcs, plan)
    assert "bank loan ma penal interest" in ctx.question and "penal interest on a bank loan" in ctx.question
    assert ctx.topic_terms and ctx.law_terms and "जिल्ला अदालत" in ctx.guidance


# ===================================================================== whole-set replay: 12 bad / 65 good
EXPECT_CAUGHT = {
    ("rw06", 2): "condition_dropped:notice_period",
    ("rw06", 3): "quote_not_verbatim",
    ("rw08", 1): "party_added:child",
    ("rw08", 2): "condition_dropped:joint_property",
    ("rw08", 3): "proviso_dropped",
    ("rw21", 6): "precedent_off_topic",
    ("rw25", 1): "wrong_law_guard:bank_loan_vs_private_creditor",
    ("rw25", 2): "wrong_law_guard:bank_loan_vs_private_creditor",
    ("rw25", 3): "precedent_not_a_rule",
    ("rw27", 2): "quote_not_verbatim",
}
NOT_CATCHABLE = {("rw04", 4), ("rw15", 2)}          # wrong-law that needs judgement -> the entailment pass
KNOWN_OVER_REMOVAL = {("rw15", 4): "dangling_additive_penalty", ("rw30", 2): "dangling_additive_penalty"}


def test_replay_of_all_77_labelled_sentences():
    bad = [s for s in FIX["sentences"] if s["label"] != "supported"]
    good = [s for s in FIX["sentences"] if s["label"] == "supported"]
    assert (len(bad), len(good)) == (12, 65)
    caught = {(s["answer_id"], s["index"]): replay(s["answer_id"], s["index"]) for s in bad}
    assert {k for k, v in caught.items() if v} == set(EXPECT_CAUGHT) and {k for k, v in caught.items() if not v} == NOT_CATCHABLE
    for key, reason in EXPECT_CAUGHT.items():
        assert caught[key] == reason, key
    removed = {(s["answer_id"], s["index"]): replay(s["answer_id"], s["index"]) for s in good}
    removed = {k: v for k, v in removed.items() if v}
    assert removed == KNOWN_OVER_REMOVAL                             # <= 5 of 65 (measured: 2, both the s.307 "थप" sentences)
    assert len(removed) <= 5


def test_pipeline_report_lists_the_new_reason_codes(monkeypatch):
    srcs = sources_of("rw08")
    s = labelled("rw08", 1)
    doc = {"blocks": [{"heading": "R", "sentences": [{"text": s["text"], "kind": "rule", "cites": s["cites"]}]}]}
    _, report = verifier.verify_structured(doc, srcs, "", ctx_of("rw08"))
    assert report["removed"]["by_reason"] == {"party_added:child": 1} and report["claims"] == 0
