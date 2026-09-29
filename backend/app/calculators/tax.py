"""Income tax for resident individuals / couples and tax deducted at source (TDS),
read from the Income Tax Act, 2058 (आयकर ऐन, २०५८) as it stands in the corpus
(Schedule 1 as amended by the Finance Act, 2083, and ss. 88, 88क, 89).

What this is and is not: a slab calculator on a *taxable income you supply*
(after the deductions and exemptions you are entitled to under the Act - e.g.
your own provident fund contribution - which are not modelled here) plus the
schedule's own reliefs (insurance premium, remote-area allowance, disability,
women's rebate). The Schedule words the first 1% slab for "employment taxable
income" and exempts sole proprietors, pension income and contributors to a
retirement fund / Social Security Fund from it; those are the `first_slab_exempt`
switch. Individuals and couples use the same slabs in this text.
Every rate below is quoted from a section listed in SOURCES.
"""
from __future__ import annotations

from .sources import Source, cite

ITA = "आयकर ऐन, २०५८"

S_SLAB_A = Source("slab_1pct", ITA, "1 (1)", "दश लाख रुपैयाँसम्म रोजगारीको करयोग्य आय भएमा एक प्रतिशत", "up to Rs 10,00,000: 1%")
S_SLAB_A_EXEMPT = Source("slab_1pct_exempt", ITA, "1 (1)", "यस खण्ड बमोजिमको कर लाग्ने छैन", "sole proprietors, pension income and retirement-fund / SSF contributors: no tax in the first slab")
S_SLAB_B = Source("slab_10pct", ITA, "1 (1)", "दश लाख रुपैयाँसम्म दश हजार रुपैयाँ र दश लाख रुपैयाँभन्दा बढी करयोग्य आयमा दश प्रतिशत", "Rs 10,00,000 to 15,00,000: 10% above the first Rs 10 lakh")
S_SLAB_C = Source("slab_20pct", ITA, "1 (1)", "पन्ध्र लाख रुपैयाँसम्म साठी हजार रुपैयाँ र पन्ध्र लाख रुपैयाँभन्दा बढी करयोग्य आयमा बिस प्रतिशत", "Rs 15,00,000 to 25,00,000: 20% above Rs 15 lakh")
S_SLAB_D = Source("slab_27pct", ITA, "1 (1)", "पच्चिस लाख रुपैयाँसम्म दुई लाख साठी हजार रुपैयाँ र पच्चिस लाख रुपैयाँभन्दा बढी करयोग्य आयमा सत्ताईस प्रतिशत", "over Rs 25,00,000: 27% above Rs 25 lakh")
S_SLAB_E = Source("slab_surcharge", ITA, "1 (1)", "चालिस लाख रुपैयाँभन्दा बढी करयोग्य आय भएमा बढि भए जति करयोग्य आयमा खण्ड (घ) बमोजिम लागेको करको दरमा थप दुई प्रतिशत विन्दुले अतिरिक्त कर", "over Rs 40,00,000: 2 percentage points more on the excess")
S_NONRES = Source("nonresident_25", ITA, "1 (3)", "गैरबासिन्दा प्राकृतिक व्यक्तिको कुनै आय वर्षको करयोग्य आयमा पच्चीस प्रतिशतका दरले कर लाग्नेछ", "non-resident individual: flat 25%")
S_INSURANCE = Source("relief_insurance", ITA, "1 (3)", "वार्षिक प्रिमियम वा चालिस हजार रुपैयाँमा जुन घटी हुन्छ", "life-insurance premium deduction: the lower of premium paid and Rs 40,000")
S_DISABLED = Source("relief_disability", ITA, "1 (3)", "रकमको पचास प्रतिशत थप रकम करयोग्य आयबाट घटाई", "person with disability: extra deduction of 50% of the first-slab amount")
S_WOMEN = Source("relief_women", ITA, "1 (3)", "दश प्रतिशत छुट हुनेछ", "woman earning only salary income: 10% rebate on the tax")
S_REMOTE = Source("relief_remote", ITA, "1 (2)", "बढीमा पचास हजार रुपैयाँसम्म करयोग्य आयबाट घटाई", "remote-area allowance: up to Rs 50,000 deducted")
S_SALARY_TDS = Source("tds_salary", ITA, "87", "अनुसूची–१ बमोजिमको दरले हुने कर कट्टी गर्नुपर्नेछ", "employer deducts tax on salary at the Schedule 1 rates")

# TDS (source phrase, rate, section label)
S_TDS_DEFAULT = Source("tds_default", ITA, "88 (1)", "कुल भुक्तानी रकमको पन्ध्र प्रतिशतका दरले कर कट्टी गर्नु पर्नेछ", "default TDS: 15% of the total payment (interest, natural resources, rent, royalty, service fee, commission, sales bonus, retirement payment and other returns)")
S_TDS_RETIRE = Source("tds_retirement_govt", ITA, "88 (1)", "लाभमा पाँच प्रतिशतका दरले", "retirement payment by the government / approved fund: 5% of the benefit")
S_TDS_AIRCRAFT = Source("tds_aircraft", ITA, "88 (1)", "वायुयानको लिज (पट्टा) बापतको रकम भुक्तानी गर्दादश प्रतिशतका दरले", "aircraft lease: 10%")
S_TDS_VAT_SERVICE = Source("tds_vat_service", ITA, "88 (1)", "सेवा शुल्कमा भुक्तानी रकमको एक दशमलब पाँच प्रतिशतका दरले", "service fee to a VAT-registered provider: 1.5%")
S_TDS_RENT = Source("tds_rent", ITA, "88 (1)", "भाडा भुक्तानी गरेकोमा दश प्रतिशतका दरले", "rent from Nepal: 10%")
S_TDS_VEHICLE = Source("tds_vehicle_rent", ITA, "88 (1)", "एक दशमलब पाँच प्रतिशतले करकट्टी", "vehicle rent to a VAT-registered vehicle-rental business: 1.5%")
S_TDS_MUTUAL = Source("tds_mutual_fund", ITA, "88 (1)", "प्राकृतिक व्यक्तिलाई बितरण गरिने प्रतिफल रकम भुक्तानीमा पाँच प्रतिशतका दरले", "mutual fund distribution to an individual: 5%")
S_TDS_ROYALTY = Source("tds_literary_royalty", ITA, "88 (2)", "साहित्यिक लेख वा रचना बापत बासिन्दा व्यक्तिलाई रोयल्टी रकम भुक्तानी गर्दा भुक्तानी रकमको एक दशमलब पाँच प्रतिशतका दरले", "royalty for literary writing: 1.5%")
S_TDS_AGENT = Source("tds_insurance_agent", ITA, "88 (2)", "बीमा अभिकर्तालाई भुक्तानी गरेको सेवा शुल्क वा कमिशनमा बिस प्रतिशतका दरले", "commission to a resident individual insurance agent: 20%")
S_TDS_DIVIDEND = Source("tds_dividend", ITA, "88 (2)", "लाभांश भुक्तानी गरेकोमा भुक्तानी रकमको पाँच", "dividend: 5%")
S_TDS_INV_INSURANCE = Source("tds_investment_insurance", ITA, "88 (3)", "लगानी बीमाको लाभ भुक्तानी गर्दाभुक्तानी रकमको पाँच प्रतिशत", "investment-insurance benefit: 5%")
S_TDS_UNAPPROVED = Source("tds_unapproved_fund", ITA, "88 (3)", "स्वीकृति नलिएको अवकाश कोषबाट लाभ भुक्तानी गर्दालाभ रकमको पाँच प्रतिशत", "benefit from an unapproved retirement fund: 5%")
S_TDS_BANK_INTEREST = Source("tds_bank_interest", ITA, "88 (3)", "छ प्रतिशतका दरले करकट्टी गर्नुपर्नेछ", "interest to an individual from a bank, finance company, co-operative or listed company (not business income): 6%")
S_TDS_WINDFALL = Source("tds_windfall", ITA, "88क", "आकस्मिक लाभ बापतको भुक्तानीमा पच्चीस प्रतिशतका दरले करकट्टी गर्नुपर्नेछ", "windfall gain: 25%")
S_TDS_CONTRACT = Source("tds_contract", ITA, "89", "पचास हजार रूपैयाँभन्दा बढीको रकम भुक्तानी दिँदा भुक्तानीको कुल रकममा एक दशमलब पाँच प्रतिशतका दरले करकट्टी गर्नुपर्नेछ", "contract payment over Rs 50,000: 1.5%")

SOURCES = [v for v in list(globals().values()) if isinstance(v, Source)]

FIRST_SLAB_LIMIT = 1_000_000.0
SECOND_SLAB_LIMIT = 1_500_000.0
THIRD_SLAB_LIMIT = 2_500_000.0
SURCHARGE_FROM = 4_000_000.0
RATES = {"first": 1.0, "second": 10.0, "third": 20.0, "fourth": 27.0, "surcharge_points": 2.0}
NONRESIDENT_RATE = 25.0
INSURANCE_CAP = 40_000.0
REMOTE_CAP = 50_000.0
DISABILITY_PCT_OF_FIRST_SLAB = 50.0
WOMEN_REBATE_PCT = 10.0
CONTRACT_THRESHOLD = 50_000.0

_MAX_INCOME = 1e12


def _slabs(first_rate: float) -> list[tuple[float, float, float]]:
    """(from, to, rate%) - the last bracket is open-ended; the surcharge splits the top one."""
    return [
        (0.0, FIRST_SLAB_LIMIT, first_rate),
        (FIRST_SLAB_LIMIT, SECOND_SLAB_LIMIT, RATES["second"]),
        (SECOND_SLAB_LIMIT, THIRD_SLAB_LIMIT, RATES["third"]),
        (THIRD_SLAB_LIMIT, SURCHARGE_FROM, RATES["fourth"]),
        (SURCHARGE_FROM, float("inf"), RATES["fourth"] + RATES["surcharge_points"]),
    ]


def income_tax(taxable_income: float, resident: bool = True, first_slab_exempt: bool = False,
               insurance_premium: float = 0.0, remote_allowance: float = 0.0, disabled: bool = False,
               woman_salary_only: bool = False) -> dict:
    """Annual income tax on `taxable_income` (NPR) for a resident individual or
    couple (Schedule 1(1)) or a non-resident individual (25% flat, 1(8))."""
    if not (0 <= taxable_income <= _MAX_INCOME):
        raise ValueError("taxable_income must be between 0 and 1,000,000,000,000")
    for name, v in (("insurance_premium", insurance_premium), ("remote_allowance", remote_allowance)):
        if not (0 <= v <= _MAX_INCOME):
            raise ValueError(f"{name} must be between 0 and 1,000,000,000,000")

    if not resident:
        tax = taxable_income * NONRESIDENT_RATE / 100
        return {
            "resident": False,
            "taxable_income": round(taxable_income, 2),
            "tax_npr": round(tax, 2),
            "effective_rate_pct": round(tax / taxable_income * 100, 4) if taxable_income else 0.0,
            "slabs": [],
            "deductions": [],
            "provisions": [cite(S_NONRES)],
        }

    deductions = []
    base = taxable_income
    provisions = [cite(S_SLAB_A), cite(S_SLAB_B), cite(S_SLAB_C), cite(S_SLAB_D), cite(S_SLAB_E)]
    if first_slab_exempt:
        provisions.append(cite(S_SLAB_A_EXEMPT))
    if insurance_premium > 0:
        d = min(insurance_premium, INSURANCE_CAP)
        deductions.append({"id": "insurance", "amount": d})
        base -= d
        provisions.append(cite(S_INSURANCE))
    if remote_allowance > 0:
        d = min(remote_allowance, REMOTE_CAP)
        deductions.append({"id": "remote_area", "amount": d})
        base -= d
        provisions.append(cite(S_REMOTE))
    if disabled:
        d = FIRST_SLAB_LIMIT * DISABILITY_PCT_OF_FIRST_SLAB / 100
        deductions.append({"id": "disability", "amount": d})
        base -= d
        provisions.append(cite(S_DISABLED))
    base = max(base, 0.0)

    first_rate = 0.0 if first_slab_exempt else RATES["first"]
    slabs_out = []
    tax = 0.0
    for lo, hi, rate in _slabs(first_rate):
        if base <= lo:
            break
        part = min(base, hi) - lo
        t = part * rate / 100
        tax += t
        slabs_out.append({"from": lo, "to": None if hi == float("inf") else hi, "rate_pct": rate, "income_in_slab": round(part, 2), "tax": round(t, 2)})

    rebate = 0.0
    if woman_salary_only:
        rebate = tax * WOMEN_REBATE_PCT / 100
        tax -= rebate
        provisions.append(cite(S_WOMEN))
    return {
        "resident": True,
        "taxable_income": round(taxable_income, 2),
        "income_after_deductions": round(base, 2),
        "tax_npr": round(tax, 2),
        "effective_rate_pct": round(tax / taxable_income * 100, 4) if taxable_income else 0.0,
        "slabs": slabs_out,
        "deductions": deductions,
        "rebate_npr": round(rebate, 2),
        "first_slab_exempt": first_slab_exempt,
        "note": {
            "en": "An estimate on the taxable income you enter. Deductions and exemptions other than those listed here are not modelled. The Schedule words the 1% slab for employment income and exempts sole proprietors, pension income and retirement fund / SSF contributors from it. Individuals and couples use the same slabs in this text.",
            "ne": "तपाईंले दिएको करयोग्य आयमा आधारित अनुमान हो। यहाँ उल्लिखित बाहेकका कटौती तथा छुट समावेश छैनन्। अनुसूचीले १% को पहिलो तह रोजगारीको आयका लागि लेखेको छ र एकलौटी फर्म, निवृत्तभरण आय तथा निवृत्तभरण कोष/सामाजिक सुरक्षा कोषमा योगदान गर्नेलाई छुट दिएको छ। यस पाठमा व्यक्ति र दम्पतीको तह उही छ।",
        },
        "provisions": provisions,
    }


TDS_TYPES: dict[str, dict] = {
    "default": {"rate": 15.0, "source": S_TDS_DEFAULT, "name": {"en": "Default: interest, rent-type returns, royalty, service fee, commission, sales bonus, other returns", "ne": "सामान्य: ब्याज, प्राकृतिक स्रोत, रोयल्टी, सेवा शुल्क, कमिशन, बिक्री बोनस, अन्य प्रतिफल"}},
    "retirement_government": {"rate": 5.0, "source": S_TDS_RETIRE, "name": {"en": "Retirement payment by the government or an approved fund", "ne": "नेपाल सरकार वा स्वीकृत अवकाश कोषबाट अवकाश भुक्तानी"}},
    "aircraft_lease": {"rate": 10.0, "source": S_TDS_AIRCRAFT, "name": {"en": "Aircraft lease", "ne": "वायुयानको लिज (पट्टा)"}},
    "service_fee_vat_registered": {"rate": 1.5, "source": S_TDS_VAT_SERVICE, "name": {"en": "Service fee to a VAT-registered provider", "ne": "मूल्य अभिवृद्धि करमा दर्ता भएको सेवाप्रदायकलाई सेवा शुल्क"}},
    "rent": {"rate": 10.0, "source": S_TDS_RENT, "name": {"en": "Rent", "ne": "भाडा"}},
    "vehicle_rent_vat_registered": {"rate": 1.5, "source": S_TDS_VEHICLE, "name": {"en": "Vehicle rent to a VAT-registered vehicle-rental business", "ne": "मूल्य अभिवृद्धि करमा दर्ता सवारी भाडाको व्यवसायलाई भाडा"}},
    "mutual_fund_individual": {"rate": 5.0, "source": S_TDS_MUTUAL, "name": {"en": "Mutual fund distribution to an individual", "ne": "सामूहिक लगानी कोषबाट प्राकृतिक व्यक्तिलाई वितरण"}},
    "literary_royalty": {"rate": 1.5, "source": S_TDS_ROYALTY, "name": {"en": "Royalty for literary writing", "ne": "साहित्यिक लेख वा रचना बापत रोयल्टी"}},
    "insurance_agent_commission": {"rate": 20.0, "source": S_TDS_AGENT, "name": {"en": "Commission to an individual insurance agent", "ne": "बीमा अभिकर्ताको सेवा शुल्क वा कमिशन"}},
    "dividend": {"rate": 5.0, "source": S_TDS_DIVIDEND, "name": {"en": "Dividend", "ne": "लाभांश"}},
    "investment_insurance_benefit": {"rate": 5.0, "source": S_TDS_INV_INSURANCE, "name": {"en": "Investment-insurance benefit", "ne": "लगानी बीमाको लाभ"}},
    "unapproved_retirement_fund": {"rate": 5.0, "source": S_TDS_UNAPPROVED, "name": {"en": "Benefit from an unapproved retirement fund", "ne": "स्वीकृति नलिएको अवकाश कोषबाट लाभ"}},
    "bank_interest_individual": {"rate": 6.0, "source": S_TDS_BANK_INTEREST, "name": {"en": "Interest to an individual (deposit, debenture, bond) not related to a business", "ne": "प्राकृतिक व्यक्तिलाई निक्षेप, ऋणपत्र, डिवेञ्चर वा बण्डको ब्याज"}},
    "windfall_gain": {"rate": 25.0, "source": S_TDS_WINDFALL, "name": {"en": "Windfall gain (prize, lottery)", "ne": "आकस्मिक लाभ"}},
    "contract": {"rate": 1.5, "source": S_TDS_CONTRACT, "name": {"en": "Contract payment over Rs 50,000", "ne": "ठेक्का वा करारको भुक्तानी (रु. ५०,००० भन्दा बढी)"}},
}


def tds_types() -> list[dict]:
    return [{"id": k, "rate_pct": v["rate"], "name": v["name"], "provision": cite(v["source"])} for k, v in TDS_TYPES.items()]


def tds(payment_type: str, amount: float, aggregated_amount: float | None = None) -> dict:
    """Tax to deduct at source on a payment of `amount` (NPR). For a contract the
    Rs 50,000 test uses `aggregated_amount` (this payment plus other payments under
    the same contract in the previous 10 days, s. 89(2)); default = `amount`."""
    spec = TDS_TYPES.get(payment_type)
    if spec is None:
        raise ValueError(f"payment_type must be one of: {', '.join(TDS_TYPES)}")
    if not (0 < amount <= _MAX_INCOME):
        raise ValueError("amount must be positive and at most 1,000,000,000,000")
    rate = spec["rate"]
    applies = True
    reason = None
    if payment_type == "contract":
        agg = amount if aggregated_amount is None else aggregated_amount
        if not (0 < agg <= _MAX_INCOME):
            raise ValueError("aggregated_amount must be positive and at most 1,000,000,000,000")
        if agg <= CONTRACT_THRESHOLD:
            applies = False
            reason = {"en": "Payments up to Rs 50,000 (counting the previous 10 days under the same contract) are not subject to this deduction.", "ne": "रु. ५०,००० सम्मको भुक्तानी (सोही करार अन्तर्गत विगतका १० दिनको समेत जोडी) मा कर कट्टी लाग्दैन।"}
    tds_amount = round(amount * rate / 100, 2) if applies else 0.0
    return {
        "payment_type": payment_type,
        "name": spec["name"],
        "amount": round(amount, 2),
        "rate_pct": rate if applies else 0.0,
        "tds_npr": tds_amount,
        "net_payable_npr": round(amount - tds_amount, 2),
        "applies": applies,
        "reason": reason,
        "note": {"en": "Salary is taxed through the income-tax slabs (s. 87). Some payments (e.g. dividends, rent to a non-business individual) are final withholding under s. 92 - check the Act.", "ne": "तलबमा आयकरको तह अनुसार कर कट्टी हुन्छ (दफा ८७)। केही भुक्तानी (जस्तै लाभांश) दफा ९२ अनुसार अन्तिम रूपमा कट्टी हुन्छन् - ऐन हेर्नुहोस्।"},
        "provisions": [cite(spec["source"])],
    }
