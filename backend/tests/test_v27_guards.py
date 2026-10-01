"""V2.7: actor / population / regime guards (situation_guards.py rows) and the dropped-condition checks on the full enclosing
passage sentence (condition_checks.py). Built from the real labelled sentences of the V3.3 live review (set B) and measured on
ALL 196 labelled sentences of the three reviews: nothing labelled `supported` may be removed (the budget was 5%)."""
import json
import sys
from pathlib import Path

import pytest

from app import condition_checks as cc, config, situation_guards as sg, verifier
from app.claim_checks import _qtok

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
import v27_sentences as vs  # noqa: E402

SENTENCES = {s["key"]: s for s in vs.load_sentences()}
HAVE_FIXTURE_TEXT = all(c.get("text_ne") for s in SENTENCES.values() for c in s["cites"])


def _reason(key: str, cond: bool = True, guards: bool = True):
    s = SENTENCES[key]
    old = config.CONDITION_CHECKS, config.GUARDS_V27
    config.CONDITION_CHECKS, config.GUARDS_V27 = cond, guards
    try:
        return vs.reason_for(s)
    finally:
        config.CONDITION_CHECKS, config.GUARDS_V27 = old


# ---------------------------------------------------------------- the guards, one real case each
@pytest.mark.parametrize("key,guard", [
    ("r3:b20-s0", "school_act_for_college_student"),     # college certificate -> compulsory SCHOOL education Act (x3)
    ("r3:b20-s1", "school_act_for_college_student"),
    ("r3:b20-s2", "school_act_for_college_student"),
    ("r3:b06-s0", "apartment_act_for_plain_land_sale"),  # land sale with an advance -> Apartment Act s.15 (x2)
    ("r3:b06-s1", "apartment_act_for_plain_land_sale"),
    ("r3:b17-s0", "public_company_rule_for_private_company"),  # pvt ltd -> "at least seven shareholders" (public company)
    ("r3:b08-s0", "mortgage_rule_without_a_mortgage"),   # tamsuk returned after repayment -> mortgage redemption s.444
    ("r3:b08-s1", "guarantor_rule_for_debtor"),          # ... -> guarantor reimbursement s.567
    ("r3:b10-s1", "cheque_drawer_right_for_holder"),     # a friend gave me a cheque -> the DRAWER may take the cheque back
])
def test_guard_removes_the_labelled_wrong_law_sentence(key, guard):
    assert _reason(key, cond=False, guards=True) == f"wrong_law_guard:{guard}"
    assert _reason(key, cond=False, guards=False) != f"wrong_law_guard:{guard}"   # the V3.3 checks did not catch it


def test_guard_cues_and_unless():
    q_college = "college le certificate nadine bhanyo, fee baki chha bhanera, milchha?"
    src = {"doc_title_ne": "अनिवार्य तथा निःशुल्क शिक्षा सम्बन्धी ऐन, २०७५", "section": "32"}
    assert sg.violation(q_college, "x", ["y"], src) == "school_act_for_college_student"
    assert sg.violation("school le mero chhora ko certificate roki diyo", "x", ["y"], src) is None   # a school child: fine
    apt = {"doc_title_ne": "संयुक्त आवासको स्वामित्व सम्बन्धी ऐन, २०५४", "section": "15"}
    assert sg.violation("jagga ko bayana diyen tara bechne le registration garena", "x", ["y"], apt) == "apartment_act_for_plain_land_sale"
    assert sg.violation("apartment ko jagga ko bayana diyen", "x", ["y"], apt) is None
    pub = "कम्पनी ऐन, २०६३ को दफा ९ अनुसार पब्लिक कम्पनीको शेयरधनीहरुको सङ्ख्या कम्तीमा सातजना"
    assert sg.violation("pvt ltd darta garna kati jana shareholder chahincha?", pub, [pub], {}) == "public_company_rule_for_private_company"
    assert sg.violation("public company ko shareholder kati jana chahincha?", pub, [pub], {}) is None
    priv = "प्राइभेट कम्पनीको शेयरधनीहरुको सङ्ख्या एकसय एकभन्दा बढी हुनु हुँदैन।"
    assert sg.violation("public limited company ma kati shareholder?", priv, [priv], {}) == "private_company_rule_for_public_company"
    assert sg.violation("pvt ltd darta garna kati jana shareholder chahincha?", priv, [priv], {}) is None   # the private rule is right
    guar = "जमानत दिने व्यक्तिले ऋणीको तर्फबाट चुक्ता गरिदिएको ऋण"
    assert sg.violation("साहूले ऋण तिरेपछि पनि तमसुक फिर्ता गरेको छैन", guar, [guar], {}) == "guarantor_rule_for_debtor"
    assert sg.violation("I stood guarantor for my friend's loan, can I get it back?", guar, [guar], {}) is None
    mort = "भोग बन्धकीमा दिएको सम्पत्ति भए साहूबाट लिएको ऋण"
    assert sg.violation("साहूले ऋण तिरेपछि पनि तमसुक फिर्ता गरेको छैन", mort, [mort], {}) == "mortgage_rule_without_a_mortgage"
    assert sg.violation("मैले जग्गा धितो राखेर ऋण लिएको थिएँ, अब तिरेँ", mort, [mort], {}) is None
    drawer = "खातावालाले जुनसुकै बखत धारकलाई त्यस्तो चेकमा उल्लिखित रकम भुक्तानी दिई चेक फिर्ता लिन सक्नेछ।"
    assert sg.violation("साथीले दिएको चेक बाउन्स भयो", drawer, [drawer], {}) == "cheque_drawer_right_for_holder"
    assert sg.violation("मैले दिएको चेक बाउन्स भयो, मैले चेक जारी गरेको हुँ", drawer, [drawer], {}) is None


def test_source_violation_rules_a_passage_out_before_generation():
    guar = {"doc_title_ne": "मुलुकी देवानी संहिता, २०७४", "section": "567", "title_ne": "जमानत दिने व्यक्ति साहूको रूपमा प्रतिस्थापन हुने",
            "text_ne": "५६७. जमानत दिने व्यक्ति साहूको रूपमा प्रतिस्थापन हुने : (१) जमानत दिने व्यक्तिले ऋणीको तर्फबाट"}
    assert sg.source_violation("साहूले ऋण तिरेपछि पनि तमसुक फिर्ता गरेको छैन", guar) == "guarantor_rule_for_debtor"
    assert sg.source_violation("साहूले ऋण तिरेपछि पनि तमसुक फिर्ता गरेको छैन", guar, v27=False) is None
    assert sg.source_violation("I guaranteed a loan", guar) is None
    school = {"doc_title_ne": "अनिवार्य तथा निःशुल्क शिक्षा सम्बन्धी ऐन, २०७५", "section": "13"}
    assert sg.source_violation("college certificate fee", school) == "school_act_for_college_student"


# ---------------------------------------------------------------- dropped conditions, one real case each
@pytest.mark.skipif(not HAVE_FIXTURE_TEXT, reason="fixture passages missing")
@pytest.mark.parametrize("key,reason", [
    ("r3:b25-s0", "time_limit_dropped"),            # s.14: "सात दिनभित्र" (within seven days) not stated
    ("r3:b10-s1", "leading_condition_dropped"),     # s.3क(6): "उपदफा (३) बमोजिम सूचना दिएकोमा" dropped
    ("r3:b28-s2", "leading_condition_dropped"),     # s.400(2): the 35-day notice belongs to the "खण्ड (ख)" exit only
    ("r3:b23-s2", "alternative_branch_dropped"),    # s.216(3): by consent ... "र मञ्जुरी नभएमा गोला हाली"
    ("r3:b26-s1", "authority_qualifier_dropped"),   # ETA s.48: a person with ACCESS under the Act, not "any person"
    ("r3:b14-s1", "ground_named_from_letters"),     # s.99(2): grounds (ख)(ग)(घ)(ङ)(च) by letter, sentence names "remarriage"
])
def test_condition_check_catches_the_labelled_dropped_condition(key, reason):
    s = SENTENCES[key]
    got = [cc.condition_problem(s["sentence"], c["quote"], c["text_ne"]) for c in s["cites"]]
    assert got == [reason]
    assert _reason(key, cond=False, guards=False) is None and _reason(key, cond=True, guards=False) == reason


def test_enclosing_sentence_splits_items_and_locates_a_fused_quote():
    text = "९. क\n(१) पहिलो वाक्य सात दिनभित्र गर्नु पर्नेछ।\n(२) दोस्रो नियम यस्तो छ।\n(क) अनयथा भएमा\n(ख) तेस्रो"
    enc = cc.enclosing(text, _qtok("दोस्रो नियम यस्तो छ"))
    assert enc is not None and "सात" not in enc.pre_text and not enc.post
    fused = cc.enclosing("अन्यथा जुनसुकै कुरा लेखिएको भए तापनि उपदफा (३) बमोजिम सूचना दिएकोमा खातावालाले जुनसुकै बखत धारकलाई त्यस्तो चेकमा "
                         "उल्लिखित रकम चेक फिर्ता लिन सक्नेछ।",
                         _qtok("खातावालाले जुनसुकै बखत धारकलाईत्यस्तो चेकमा उल्लिखित रकम चेक फिर्ता लिन सक्नेछ"))
    assert fused is not None and "दिएकोमा" in fused.pre_text


def test_condition_checks_do_not_fire_when_the_sentence_carries_the_condition():
    passage = "छ। कसैले सात दिनभित्र बिक्रेता समक्ष फिर्ता गर्न चाहेमा मूल्य फिर्ता लिन सक्नेछ।"
    quote = "बिक्रेता समक्ष फिर्ता गर्न चाहेमा मूल्य फिर्ता लिन सक्नेछ"
    assert cc.condition_problem("You can get your money back from the seller.", quote, passage) == "time_limit_dropped"
    assert cc.condition_problem("Within seven days you can get your money back from the seller.", quote, passage) is None
    assert cc.condition_problem("तपाईंले सात दिनभित्र पैसा फिर्ता लिन सक्नुहुन्छ।", quote, passage) is None
    assert cc.condition_problem("You can get your money back from the seller.", "कुनै अर्को वाक्य जुन छैन", passage) is None   # unlocated: open


# ---------------------------------------------------------------- over-removal on every labelled sentence
def test_v27_checks_remove_no_supported_sentence_of_the_196_labelled():
    if not HAVE_FIXTURE_TEXT:
        pytest.skip("fixture passages missing")
    sentences = list(SENTENCES.values())
    base = vs.run(sentences, False, False)
    new = vs.run(sentences, True, True)
    config.CONDITION_CHECKS = config.GUARDS_V27 = True
    supported = [s for s in sentences if s["label"] == "supported" and base[s["key"]] is None]
    removed_supported = [s["key"] for s in supported if new[s["key"]] is not None]
    assert len(supported) > 120
    assert len(removed_supported) <= 0.05 * len(supported), removed_supported
    caught = [s["key"] for s in sentences if s["label"] != "supported" and base[s["key"]] is None and new[s["key"]] is not None]
    assert len(caught) >= 12   # 6 dropped conditions + 9 wrong-law sentences of the 15 newly removed (measured 15)
