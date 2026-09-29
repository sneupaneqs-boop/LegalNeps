"""Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.

The real model isn't available in unit tests (and must never be called), so
`RegexReader` plays its role: given the extraction prompt the audit engine
builds, it reads the `[Clause id]` blocks out of that prompt and answers with
the JSON contract the engine demands ({"facts": {name: {"value", "clause"}}}).
Every value comes from the contract text via a regex - nothing is hard-coded
per contract - and the clause id is the one the engine put in the prompt.

What this proves: segmentation -> prompt -> JSON validation -> deterministic
rules -> cited findings works end to end, and that seeded defects are caught.
What it does NOT prove: how accurately a real model extracts facts. Seeded
recall below therefore measures the pipeline and the rules, not the model.
"""
from __future__ import annotations

import json
import re

from app.text_norm import DEV_DIGITS

# --------------------------------------------------------------------------
# contracts: (id, contract_type, text, seeded_defect_check_ids)
# --------------------------------------------------------------------------

EMPLOYMENT_1 = """EMPLOYMENT AGREEMENT

This Employment Agreement is made between Himal Traders Pvt. Ltd. (the "Employer") and Sita Sharma (the "Employee").

1. Position and duties
The Employee is appointed as Accountant on a regular employment basis and shall carry out bookkeeping and reporting duties.

2. Remuneration
The Employee shall receive a monthly salary of NPR 45,000 plus allowances. Salary is paid monthly.

3. Probation
The Employee shall serve a probation period of 8 months from the start date.

4. Working hours
Normal working hours are 8 hours per day and 54 hours per week.

5. Overtime
Overtime is limited to 3 hours per day and 15 hours per week and is paid at 1.25 times the basic hourly pay.

6. Leave
The Employee is entitled to 7 days of paid sick leave per year.

7. Insurance
The Employer shall provide medical insurance of NPR 100,000 per year and accident insurance of NPR 700,000.

8. Confidentiality
The Employee shall keep the Employer's business information confidential.
"""
EMPLOYMENT_1_SEEDS = {"probation_max", "weekly_hours_max", "overtime_rate_min", "termination_clause_present",
                      "sick_leave_min"}

EMPLOYMENT_2 = """EMPLOYMENT CONTRACT

Between Kathmandu Software Solutions Pvt. Ltd. (the "Employer") and Ramesh Thapa (the "Employee").

Clause 1. Appointment
The Employee is appointed as Software Engineer on a regular employment basis.

Clause 2. Working time
Normal working hours are 8 hours per day and 48 hours per week. There is a probation period of 6 months.

Clause 3. Pay
Salary is paid every 2 months. The Employer may deduct a fine from the salary for late arrival.

Clause 4. Termination
Either party may terminate this contract. The Employer shall give 15 days' written notice of termination.

Clause 5. Insurance
The Employer provides accident insurance of NPR 500,000 for the Employee.

Clause 6. Sick leave
The Employee gets 12 days of paid sick leave per year.
"""
EMPLOYMENT_2_SEEDS = {"remuneration_stated", "salary_interval_max", "no_penalty_deduction",
                      "termination_notice_min", "accident_insurance_min"}

RENT_1 = """HOUSE RENT AGREEMENT

This agreement is made between Hari Adhikari (the "Landlord", citizenship no. 27-01-70-01234, Lalitpur) and Maya Gurung (the "Tenant", citizenship no. 12-02-74-00456, Pokhara).

1. Property
The Landlord rents to the Tenant a residential flat on the second floor at Kupondole, Lalitpur, kitta number 431.

2. Term
The term of this tenancy is 7 years starting on 1 Baisakh 2083.

3. Rent
The Tenant shall pay a monthly rent of NPR 30,000. Rent is paid by the 7th of each month by bank transfer.

4. Utilities and tax
The Tenant pays the electricity and water bills. The Landlord pays the house-rent tax.

5. Security deposit
The Tenant has paid a security deposit of NPR 200,000 to the Landlord.

6. Sub-letting
The Tenant may not sub-let any part of the flat.

7. Ending the tenancy
The Tenant may vacate the flat with 35 days' notice. The Landlord shall give 15 days' written notice if the Landlord needs the flat back for own use.
"""
RENT_1_SEEDS = {"deposit_return_terms", "residential_term_max", "landlord_notice_min", "witnesses"}

RENT_2 = """घर बहाल सम्झौता

घरधनी राम श्रेष्ठ (नागरिकता नं. ११-०१-७०-०१२३४) र बहालवाला सीता राई (नागरिकता नं. २२-०३-७१-०५६७८) बीच यो सम्झौता भएको छ।

१. घरको विवरण
काठमाडौं, बानेश्वरमा रहेको कित्ता नम्बर ५२१ को जग्गामा बनेको आवासीय घर बहालमा दिइएको छ।

२. अवधि
बहालको अवधि ३ वर्ष हुनेछ।

३. बहाल बुझाउने तरिका
बहाल प्रत्येक महिनाको ७ गतेभित्र बैंक मार्फत बुझाउनुपर्नेछ।

४. कर तथा पुनः बहाल
घर बहाल कर घरधनीले बुझाउनेछ। बहालमा लिनेले घर अन्य व्यक्तिलाई बहालमा दिन पाउने छैन।

५. साक्षी
साक्षी १: गोपाल केसी। साक्षी २: कमला पौडेल।
"""
RENT_2_SEEDS = {"monthly_rent_stated", "utilities_responsibility", "vacate_and_eviction_terms"}

SERVICE_1 = """SERVICE AGREEMENT

This Service Agreement is made between Everest Retail Pvt. Ltd. (the "Client") and Digital Craft Consultancy (the "Service Provider"). The Client is represented by its Director, an authorised signatory.

1. Scope of services
The Service Provider shall design and maintain the Client's website as set out in Schedule A (the scope of services).

2. Fees
The Client shall pay a fee of NPR 250,000, payable in two instalments.

3. Liability
The Service Provider is liable for direct damages caused by its breach, capped at the total fee.

4. Non-competition
The Service Provider shall not provide similar services to any competitor of the Client. This non-compete applies after this agreement ends.

5. Governing law
This agreement is governed by the laws of Nepal.
"""
SERVICE_1_SEEDS = {"dispute_resolution", "noncompete_has_duration", "termination_terms", "force_majeure"}

SERVICE_2 = """CONSULTANCY SERVICES AGREEMENT

Between Sunrise Foods Pvt. Ltd. (the "Client") and Anil Karki (the "Consultant"). Signed for the Client by its authorised signatory.

1. Services
The Consultant shall provide marketing advice as needed.

2. Fees and payment
The Consultant is paid a fee of NPR 80,000 on completion.

3. Termination
Either party may terminate this agreement by giving 30 days' written notice.

4. Force majeure
Neither party shall be responsible for delay caused by force majeure events.

5. Disputes
Disputes shall be settled by arbitration in Kathmandu under the Arbitration Act, 2055.
"""
SERVICE_2_SEEDS = {"scope_defined", "governing_law", "damages_clause"}

NDA_1 = """NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement is made between Alpha Tech Pvt. Ltd. (the "Disclosing Party") and Beta Solutions Pvt. Ltd. (the "Receiving Party").

1. Obligation
The Receiving Party shall keep all information received from the Disclosing Party confidential and not disclose it to anyone.

2. Term
The confidentiality obligation continues for 3 years after this agreement ends.

3. Permitted disclosure
The Receiving Party may disclose information where required by law or a court order.

4. Remedies
The Disclosing Party may seek an injunction and damages for any breach.

5. Non-compete
The Receiving Party shall not engage in a competing business.

6. Governing law
This agreement is governed by the laws of Nepal.
"""
NDA_1_SEEDS = {"confidential_info_defined", "dispute_resolution", "noncompete_has_duration"}

NDA_2 = """CONFIDENTIALITY AGREEMENT

Between Green Valley Hydropower and Snow Consulting.

1. Definition
"Confidential Information" means all non-public technical and commercial information disclosed by one party (the Disclosing Party) to the other (the Receiving Party), excluding information that is public.

2. Permitted disclosure
Disclosure required by law or a court order is permitted.

3. Dispute resolution
Any dispute shall be referred to arbitration in Kathmandu.
"""
NDA_2_SEEDS = {"duration_stated", "remedies_clause", "governing_law"}

LOAN_1 = """LOAN AGREEMENT

This Loan Agreement is made between Prakash Rana (the "Lender") and Sunil Bista (the "Borrower").

1. Loan
The Lender lends NPR 500,000 to the Borrower.

2. Interest
The Borrower shall pay interest at 3% per month. Unpaid interest is compounded monthly.

3. Security
The Borrower gives a mortgage over land at Bhaktapur as collateral.

4. Receipts
The Lender shall issue a receipt for every payment.

5. Governing law and disputes
This agreement is governed by the laws of Nepal. Disputes shall be resolved in the courts of Kathmandu district.
"""
LOAN_1_SEEDS = {"interest_cap", "no_compound_interest", "collateral_release"}

SALE_1 = """AGREEMENT FOR SALE OF GOODS

Between Bharat Suppliers (the "Seller") and Nepal Bakery Pvt. Ltd. (the "Buyer").

1. Goods
The Seller shall sell 500 sacks of Brand-X wheat flour, 50 kg each, as described in the goods specification.

2. Warranty
The Seller warrants that the flour is fresh and fit for human consumption.

3. Governing law
This agreement is governed by the laws of Nepal.
"""
SALE_1_SEEDS = {"price_stated", "delivery_terms", "dispute_resolution"}

CONTRACTS = [
    ("employment_1", "employment", EMPLOYMENT_1, EMPLOYMENT_1_SEEDS),
    ("employment_2", "employment", EMPLOYMENT_2, EMPLOYMENT_2_SEEDS),
    ("rent_1", "rent_lease", RENT_1, RENT_1_SEEDS),
    ("rent_2_nepali", "rent_lease", RENT_2, RENT_2_SEEDS),
    ("service_1", "service_agreement", SERVICE_1, SERVICE_1_SEEDS),
    ("service_2", "service_agreement", SERVICE_2, SERVICE_2_SEEDS),
    ("nda_1", "nda", NDA_1, NDA_1_SEEDS),
    ("nda_2", "nda", NDA_2, NDA_2_SEEDS),
    ("loan_1", "sale_or_loan", LOAN_1, LOAN_1_SEEDS),
    ("sale_1", "sale_or_loan", SALE_1, SALE_1_SEEDS),
]


# --------------------------------------------------------------------------
# the stand-in reader
# --------------------------------------------------------------------------

def _n(text: str) -> str:
    return text.translate(DEV_DIGITS)


def _num(m, group=1) -> float:
    return float(m.group(group).replace(",", ""))


def _search(pattern):
    rx = re.compile(pattern, re.I | re.S)
    return lambda t: rx.search(_n(t))


def _has(pattern, *, absent=None):
    rx = re.compile(pattern, re.I | re.S)
    ab = re.compile(absent, re.I | re.S) if absent else None
    return lambda t: (True if rx.search(_n(t)) and not (ab and ab.search(_n(t))) else None)


def _val(pattern, conv=None, *, need=None, forbid=None):
    rx = re.compile(pattern, re.I | re.S)
    need_rx = re.compile(need, re.I | re.S) if need else None
    forbid_rx = re.compile(forbid, re.I | re.S) if forbid else None

    def fn(t):
        t = _n(t)
        if need_rx and not need_rx.search(t):
            return None
        if forbid_rx and forbid_rx.search(t):
            return None
        m = rx.search(t)
        if not m:
            return None
        return conv(m) if conv else _num(m)
    return fn


def _term_years(t):
    t = _n(t)
    m = re.search(r"(?:term of this tenancy is|term of|अवधि)\D{0,12}?(\d+(?:\.\d+)?)\s*(years?|months?|वर्ष|महिना)", t, re.I)
    if not m:
        return None
    n = float(m.group(1))
    return n / 12 if m.group(2).lower().startswith(("month", "महिना")) else n


def _interest(t):
    t = _n(t)
    m = re.search(r"interest at (\d+(?:\.\d+)?)%\s*(per annum|per year|per month|a month)", t, re.I)
    if not m:
        return None
    n = float(m.group(1))
    return n * 12 if "month" in m.group(2).lower() else n


def _payment_interval(t):
    t = _n(t)
    if re.search(r"salary is paid monthly", t, re.I):
        return 1.0
    m = re.search(r"salary is paid every (\d+) months?", t, re.I)
    return float(m.group(1)) if m else None


# fact -> reader(clause_text) -> value | None ; first clause with a non-None wins
READERS = {
    # -- employment
    "states_remuneration": _has(r"monthly salary of|remuneration of"),
    "states_employment_type": _has(r"regular employment|fixed-term|casual employment|part-time"),
    "states_position_and_duties": _has(r"is appointed as"),
    "probation_months": _val(r"probation period of (\d+(?:\.\d+)?) months?"),
    "daily_working_hours": _val(r"(\d+(?:\.\d+)?) hours per day", forbid=r"overtime"),
    "weekly_working_hours": _val(r"(\d+(?:\.\d+)?) hours per week", forbid=r"overtime"),
    "overtime_pay_multiplier": _val(r"(\d+(?:\.\d+)?) times", need=r"overtime"),
    "overtime_daily_hours": _val(r"limited to (\d+(?:\.\d+)?) hours per day", need=r"overtime"),
    "overtime_weekly_hours": _val(r"(\d+(?:\.\d+)?) hours per week", need=r"overtime"),
    "salary_payment_interval_months": _payment_interval,
    "has_termination_clause": _has(r"\bterminat|\bresign"),
    "employer_notice_days": _val(r"Employer shall give (\d+) days'? (?:written )?notice"),
    "allows_penalty_salary_deduction": _has(r"deduct\w* a? ?(?:fine|penalty)|fine from the salary"),
    "gratuity_percent": _val(r"gratuity of (\d+(?:\.\d+)?)%"),
    "medical_insurance_amount_npr": _val(r"medical insurance of NPR ([\d,]+)"),
    "accident_insurance_amount_npr": _val(r"accident insurance of NPR ([\d,]+)"),
    "sick_leave_days_per_year": _val(r"(\d+) days of paid sick leave"),
    # -- rent (English + Nepali phrasings)
    "has_party_identity_details": _has(r"citizenship no|नागरिकता नं"),
    "has_property_description": _has(r"kitta number|कित्ता नम्बर"),
    "monthly_rent_npr": _val(r"monthly rent of NPR ([\d,]+)|मासिक बहाल रु\.? ?([\d,]+)",
                              conv=lambda m: float((m.group(1) or m.group(2)).replace(",", ""))),
    "has_rent_payment_schedule": _has(r"rent is paid by|बहाल बुझाउने तरिका|बहाल प्रत्येक महिना"),
    "lease_term_years": _term_years,
    "is_commercial_use": lambda t: (True if re.search(r"\b(shop|office|commercial)\b|व्यापारिक", t, re.I)
                                     else (False if re.search(r"residential|आवासीय", t, re.I) else None)),
    "has_utilities_clause": _has(r"electricity|बिजुली|खानेपानी"),
    "has_tax_clause": _has(r"house-rent tax|घर बहाल कर"),
    "has_vacate_and_eviction_terms": _has(r"vacate|evict|घर छाड्"),
    "landlord_notice_days": _val(r"Landlord shall give (\d+) days'? (?:written )?notice"),
    "has_sublet_clause": _has(r"sub-?let|अन्य व्यक्तिलाई बहालमा दिन"),
    "has_two_witnesses": _has(r"witness 1.*witness 2|साक्षी 1.*साक्षी 2|two witnesses"),
    "security_deposit_npr": _val(r"security deposit of NPR ([\d,]+)|धरौटी रु\.? ?([\d,]+)",
                                  conv=lambda m: float((m.group(1) or m.group(2)).replace(",", ""))),
    "has_deposit_return_terms": _has(r"deposit (?:shall be|will be|is) (?:refunded|returned)|धरौटी फिर्ता"),
    # -- service / nda
    "has_scope_of_services": _has(r"scope of services|scope of work|shall (?:design|develop|deliver)", absent=r"as needed"),
    "has_fee_and_payment_terms": _has(r"fee of NPR|is paid a fee"),
    "has_damages_or_liability_clause": _has(r"liable|liability|damages"),
    "governing_law": _val(r"governed by the laws of ([A-Za-z ]+?)\.", conv=lambda m: m.group(1).strip()),
    "dispute_resolution": _val(r"(arbitration|courts? of [A-Za-z ]+?)[ .]", conv=lambda m: m.group(1), need=r"dispute"),
    "has_noncompete_clause": _has(r"non-?compet|competing business|competitor"),
    "noncompete_duration_months": _val(r"for (\d+) months", need=r"non-?compet|competit"),
    "has_force_majeure_clause": _has(r"force majeure"),
    "states_signatory_authority": _has(r"authori[sz]ed signatory"),
    "has_confidential_info_definition": _has(r"\"Confidential Information\" means"),
    "confidentiality_duration_years": _val(r"continues for (\d+) years"),
    "has_legal_disclosure_exception": _has(r"required by law|court order"),
    "has_remedies_clause": _has(r"injunction|remed"),
    # -- sale / loan
    "is_sale": _has(r"\bsell\b|purchase price|\bbuyer\b"),
    "is_loan": _has(r"\blends?\b|\bborrower\b"),
    "has_goods_description": _has(r"sacks? of|as described in the goods specification"),
    "has_price_stated": _has(r"purchase price of NPR|price of NPR"),
    "has_delivery_terms": _has(r"deliver"),
    "has_quality_warranty_terms": _has(r"warrant"),
    "interest_rate_percent_per_year": _interest,
    "lender_is_licensed_financial_institution": _has(r"licensed (?:bank|financial institution)"),
    "has_compound_interest": _has(r"compound|interest on interest"),
    "has_receipt_clause": _has(r"receipt"),
    "has_collateral": _has(r"collateral|mortgage|pledge"),
    "has_collateral_release_terms": _has(r"collateral shall be (?:returned|released)|released on repayment"),
}
BOOLEAN_FACTS_DEFAULT_FALSE = True


class RegexReader:
    """Callable with the signature of llm.complete (system, user, **kw) -> str."""

    def __init__(self, break_first: int = 0):
        self.calls = 0
        self.prompts: list[str] = []
        self.break_first = break_first  # answer garbage this many times before answering properly

    def __call__(self, system, user, **kwargs):
        self.calls += 1
        self.prompts.append(user)
        if self.calls <= self.break_first:
            return "Sure! Here is the analysis you asked for: (no JSON)"
        requested = re.findall(r"^- (\w+) \((number|boolean|string)\):", user, re.M)
        blocks = re.findall(r"\[Clause ([^\]]+)\]\n(.*?)(?=\n\n\[Clause |\n<<<end_user_text>>>)", user, re.S)
        facts = {}
        for name, ftype in requested:
            reader = READERS.get(name)
            value, clause = None, None
            if reader:
                for cid, body in blocks:
                    v = reader(body)
                    if v is not None:
                        value, clause = v, cid
                        break
            if value is None and ftype == "boolean":
                value = False
            facts[name] = {"value": value, "clause": clause}
        return json.dumps({"facts": facts})
