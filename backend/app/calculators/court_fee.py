"""Court fee (अदालती शुल्क) calculator (S8).

मुलुकी देवानी कार्यविधि संहिता, २०७४ दफा ६९ sets a marginal-bracket schedule
on the claim's disclosed value (बिगो): a flat Rs 500 base for the first
Rs 25,000, then a shrinking percentage on each further bracket - the same
shape as an income-tax schedule, so it's computed the same way (each
bracket's rate applies only to the slice of value that falls inside it).
दफा ७३ adds a flat 15% surcharge on appeal, computed on the fee for the
value actually being appealed. दफा ९७ is a separate, always-flat Rs 200
filing fee (फिराद दस्तुर) charged on every plaint regardless of value -
it is not part of the दफा ६९ schedule.
"""
from __future__ import annotations

from ..playbooks import resolve_provision
from .sources import Source, cite

FILING_FEE_PROVISION = {"law_title_ne": "मुलुकी देवानी कार्यविधि संहिता, २०७४", "section": "97"}
COURT_FEE_PROVISION = {"law_title_ne": "मुलुकी देवानी कार्यविधि संहिता, २०७४", "section": "69"}
APPEAL_FEE_PROVISION = {"law_title_ne": "मुलुकी देवानी कार्यविधि संहिता, २०७४", "section": "73"}

FILING_FEE_NPR = 200.0
APPEAL_SURCHARGE_RATE = 0.15

# (bracket lower bound, bracket upper bound, marginal rate on the slice within it)
_BRACKETS: list[tuple[float, float, float]] = [
    (0, 25_000, 0.0),  # covered by the flat base fee instead of a rate
    (25_000, 50_000, 0.05),
    (50_000, 100_000, 0.035),
    (100_000, 500_000, 0.02),
    (500_000, 2_500_000, 0.015),
    (2_500_000, float("inf"), 0.01),
]
_BASE_FEE = 500.0  # flat fee for the first Rs 25,000 of claim value


# Where each number below is read from (verified against the corpus text by the tests).
_CPC = "मुलुकी देवानी कार्यविधि संहिता, २०७४"
SOURCES = [
    Source("fee_base", _CPC, "69", "पहिलो पच्चीस हजार रुपैयाँसम्मको लागि पाँच सय रुपैयाँ", "first Rs 25,000: Rs 500"),
    Source("fee_5pct", _CPC, "69", "दोस्रो पच्चीस हजारसम्मको लागि सयकडा पाँचका दरले", "next Rs 25,000: 5%"),
    Source("fee_3_5pct", _CPC, "69", "तेस्रो पचास हजार रुपैयाँसम्मको लागि सयकडा तीन दशमलब पाँचका दरले", "next Rs 50,000: 3.5%"),
    Source("fee_2pct", _CPC, "69", "चौथो चार लाख रुपैयाँसम्मको लागि सयकडा दुईका दरले", "next Rs 4,00,000: 2%"),
    Source("fee_1_5pct", _CPC, "69", "पाँचौं बीस लाख रुपैयाँसम्मको लागि सयकडा एक दशमलब पाँचका दरले", "next Rs 20,00,000: 1.5%"),
    Source("fee_1pct", _CPC, "69", "पच्चीस लाख रुपैयाँभन्दा माथि जतिसुकै भएपनि बढी अङ्क जतिको लागि सयकडा एकका दरले", "above Rs 25,00,000: 1%"),
    Source("filing_fee", _CPC, "97", "दुई सय रुपैयाँ फिराद दस्तुर", "plaint filing fee Rs 200"),
    Source("appeal_15pct", _CPC, "73", "सयकडा पन्ध्रको दरले थप अदालती शुल्क", "appeal: 15% of the plaint fee on the value appealed"),
    Source("review_10pct", _CPC, "74", "थप दश प्रतिशतका दरले अदालती शुल्क", "review / retrial: 10% of the plaint fee on the value contested"),
    Source("flat_500", _CPC, "70", "एकमुष्ट पाँच सय रुपैयाँ अदालती शुल्क लाग्नेछ", "flat Rs 500 for the listed subjects"),
    Source("flat_1000", _CPC, "70", "एक हजार रुपैयाँ अदालती शुल्क लाग्नेछ", "flat Rs 1,000 for share determination / setting aside a document"),
    Source("flat_2500", _CPC, "70", "एकमुष्ट दुई हजार पाँच सय रुपैयाँ अदालती शुल्क लाग्नेछ", "flat Rs 2,500 for other contract disputes with no stated amount"),
    Source("flat_other", _CPC, "71", "मूल्य वा बिगो नखुलेको अन्य जुनसुकै मुद्दामा दफा ७० को अधीनमा रही एक हजार रुपैयाँ अदालती शुल्क लाग्नेछ", "other suits with no stated value: Rs 1,000"),
    Source("settle_25", _CPC, "82", "प्रमाण बुझ्नु अघि भए पच्चीस प्रतिशत", "settlement before evidence is heard at first instance: 25% of the fee kept"),
    Source("settle_50", _CPC, "82", "आधा अदालती शुल्क लिई बाँकी अदालती शुल्क", "settlement later: half the fee kept, the rest refunded"),
]


def court_fee(claim_value: float) -> float:
    """The दफा ६९ अदालती शुल्क for a claim of this disclosed value."""
    if claim_value <= 0:
        raise ValueError("claim_value must be positive")
    fee = _BASE_FEE
    for lower, upper, rate in _BRACKETS[1:]:
        if claim_value <= lower:
            break
        fee += (min(claim_value, upper) - lower) * rate
    return round(fee, 2)


def appeal_fee(disputed_value: float) -> float:
    """The दफा ७३ additional appeal fee for appealing a claim of this
    (portion of the) disputed value."""
    return round(court_fee(disputed_value) * APPEAL_SURCHARGE_RATE, 2)


def estimate(claim_value: float) -> dict:
    """Filing fee + court fee for filing a plaint over `claim_value`, each
    with its own cited provision."""
    return {
        "claim_value": claim_value,
        "filing_fee_npr": FILING_FEE_NPR,
        "filing_fee_provision": resolve_provision(FILING_FEE_PROVISION),
        "court_fee_npr": court_fee(claim_value),
        "court_fee_provision": resolve_provision(COURT_FEE_PROVISION),
        "total_npr": round(FILING_FEE_NPR + court_fee(claim_value), 2),
    }


def estimate_appeal(disputed_value: float) -> dict:
    return {
        "disputed_value": disputed_value,
        "appeal_fee_npr": appeal_fee(disputed_value),
        "provision": resolve_provision(APPEAL_FEE_PROVISION),
    }


# ------------------------------------------------------------- other fee types (s. 70, 71, 74, 82) ---

_SRC = {s.id: s for s in SOURCES}

# case type -> (flat fee NPR, source id, English name, Nepali name)
FLAT_FEE_CASE_TYPES: dict[str, tuple[float, str, str, str]] = {
    "land_registration_or_mutation": (500.0, "flat_500", "Land registration, mutation, or cancelling one", "जग्गाको दर्ता, नामसारी वा त्यस्तो दर्ता/नामसारी बदर"),
    "receipt_or_acquittance": (500.0, "flat_500", "Claim for a receipt or acquittance", "रसिद तथा भरपाईको दाबी"),
    "demand_deed_or_note": (500.0, "flat_500", "Demand for a deed, promissory note, surety bond or acknowledgement", "लिखत, भाखापत्र, जमानीपत्र, कबुलियत भरपाई आदि फट्टाको माग दाबी"),
    "eviction": (500.0, "flat_500", "Eviction from, or right to stay in, a house or land", "घर वा जग्गामा बसेकोलाई उठाउने वा उठ्न नपर्ने माग दाबी"),
    "water_channel": (500.0, "flat_500", "Dam, channel or water-turn dispute", "बाँध, पैनी वा कुलो वा पानीको रोलक्रम सम्बन्धी दाबी"),
    "window_door_passage": (500.0, "flat_500", "Passage, window, door or drain opening/closing", "निकास, झ्याल, ढोका वा कौशी सम्बन्धी माग दाबी"),
    "injunction": (500.0, "flat_500", "Injunction or mandatory order (or setting one aside)", "निषेधाज्ञा वा आदेशात्मक आदेश जारीको माग दाबी वा बदर"),
    "capacity_determination": (500.0, "flat_500", "Determining full / semi / lack of legal capacity", "पूर्ण सक्षमता, अर्ध सक्षमता वा असक्षमता निर्धारण"),
    "divorce": (500.0, "flat_500", "Divorce", "सम्बन्ध विच्छेद"),
    "kinship": (500.0, "flat_500", "Establishing a family relationship", "नाता कायम"),
    "declaration_of_death": (500.0, "flat_500", "Judicial declaration of death (or setting it aside)", "मृत्युको न्यायिक घोषणा वा सोको बदर/संशोधन"),
    "insolvency": (500.0, "flat_500", "Starting or not starting insolvency proceedings", "दामासाहीको कारबाही प्रारम्भ गर्ने वा नगर्ने माग दाबी"),
    "guthi_manager": (500.0, "flat_500", "Appointing or removing a guthi manager", "गुठी सञ्चालक नियुक्ति वा बदर"),
    "guardian": (500.0, "flat_500", "Appointing or removing a guardian", "संरक्षक नियुक्ति वा बदर"),
    "curator": (500.0, "flat_500", "Appointing or removing a curator (माथवर)", "माथवरको नियुक्ति वा बदर"),
    "usufruct": (500.0, "flat_500", "Usufruct claim (if a value is stated, the value-based fee applies instead)", "फलोपभोगको दाबी वा बदर (मूल्य उल्लेख भएमा मूल्यका आधारमा)"),
    "easement": (500.0, "flat_500", "Easement claim or cancellation", "सुविधाभारको दाबी वा बदर"),
    "partition_share": (1000.0, "flat_1000", "Partition: fixing or giving a share in inheritable property", "अंश लाग्ने सम्पत्तिमा अंशको भाग यकिन गर्ने वा दिलाई दिने"),
    "set_aside_document": (1000.0, "flat_1000", "Setting aside a document or paper", "लिखत वा कागज बदर"),
    "contract_no_amount": (2500.0, "flat_2500", "Any other contract dispute where no amount is stated", "बिगो नखुलेको अन्य कुनै करारका सम्बन्धमा विवाद"),
    "other_no_value": (1000.0, "flat_other", "Any other suit where no value or amount is stated", "मूल्य वा बिगो नखुलेको अन्य मुद्दा"),
}


def flat_fee_types() -> list[dict]:
    return [
        {"id": k, "fee_npr": v[0], "name": {"en": v[2], "ne": v[3]}, "provision": cite(_SRC[v[1]])}
        for k, v in FLAT_FEE_CASE_TYPES.items()
    ]


def flat_fee(case_type: str) -> dict:
    """The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2))."""
    spec = FLAT_FEE_CASE_TYPES.get(case_type)
    if spec is None:
        raise ValueError(f"case_type must be one of: {', '.join(FLAT_FEE_CASE_TYPES)}")
    amount, src_id, en, ne = spec
    return {
        "case_type": case_type,
        "name": {"en": en, "ne": ne},
        "court_fee_npr": amount,
        "filing_fee_npr": FILING_FEE_NPR,
        "total_npr": round(amount + FILING_FEE_NPR, 2),
        "filing_fee_provision": cite(_SRC["filing_fee"]),
        "provision": cite(_SRC[src_id]),
    }


REVIEW_SURCHARGE_RATE = 0.10
SETTLEMENT_RETAINED_BEFORE_EVIDENCE = 0.25
SETTLEMENT_RETAINED_LATER = 0.50


def review_fee(contested_value: float) -> dict:
    """s. 74: when a review / retrial of a case is granted, an extra 10% of the
    plaint fee on the value contested."""
    base = court_fee(contested_value)
    return {
        "contested_value": contested_value,
        "review_fee_npr": round(base * REVIEW_SURCHARGE_RATE, 2),
        "provision": cite(_SRC["review_10pct"]),
    }


def settlement_fee(fee_paid: float, before_evidence_at_first_instance: bool) -> dict:
    """s. 82(1): on a settlement (मिलापत्र) of a fully paid case, the court keeps
    25% of the fee if it is before evidence is heard at first instance, otherwise
    half, and refunds the rest."""
    if fee_paid <= 0:
        raise ValueError("fee_paid must be positive")
    share = SETTLEMENT_RETAINED_BEFORE_EVIDENCE if before_evidence_at_first_instance else SETTLEMENT_RETAINED_LATER
    kept = round(fee_paid * share, 2)
    return {
        "fee_paid_npr": round(fee_paid, 2),
        "retained_npr": kept,
        "refunded_npr": round(fee_paid - kept, 2),
        "retained_share": share,
        "provision": cite(_SRC["settle_25" if before_evidence_at_first_instance else "settle_50"]),
    }
