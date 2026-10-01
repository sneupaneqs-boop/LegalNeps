# Playbook audit - the 25 curated action plans

Prepared for hand-off to a licensed Nepali advocate. Every provision cited by every playbook was re-read in its original Nepali text from our corpus, and each playbook's summary notes, numbers, forum, limitation period and next steps were checked against that text. Nothing here is legal advice; where the corpus does not settle a point it is listed as NEEDS-ADVOCATE-REVIEW rather than guessed.

## Result in one paragraph

24 of the 24 playbooks audited here needed changes (the 25th, deposit_not_returned, had already been corrected and was used as the model). The most serious defects were wrong limitation periods that could make a user file too late or too early, forum advice that skipped a mandatory step, and cited sections that govern a different situation. There are 64 NEEDS-ADVOCATE-REVIEW items in total, listed per playbook below and collected at the end.

## The most serious errors found

| # | Playbook | What the old playbook told users | What the law text says |
|---|---|---|---|
| 1 | unpaid_personal_loan | Sue within **2 years** (cited Civil Code s.520). | s.520 is the limitation clause of the *contract formation* chapter. Loans have their own chapter and s.492 gives **1 year** from the end of the repayment period stated in the document (or from the cause of action). A lender following the old advice could lose the claim. |
| 2 | foreign_employment_fraud | Complain within 1 year (cited Foreign Employment Act s.60), and go "directly to the Tribunal". | s.60's 1-year bar applies to offences *other than* ss.43-47; the false-promise money-taking offences (ss.43-44) are expressly excluded from it. Compensation is claimed from the Department (s.36); criminal cases are investigated by the Department and prosecuted by the government. |
| 3 | tenant_eviction_without_notice | Its only real provision was Civil Code s.400, with a note that it "cuts both ways". | s.400 lists when the *tenant* may leave early. The landlord's grounds are in s.401 (with a 35-day written notice only when the landlord needs the house himself). Same mistake as the deposit playbook. |
| 4 | cyber_harassment | Limitation: Criminal Code s.187 ("general limitation clause for this part"). | s.187 is the limitation clause of the *homicide chapter*. The real deadlines are 90 days (Electronic Transactions Act s.74) and 3 months (Criminal Code ss.304, 308). The main cyber-offence section (ETA s.47) was missing. |
| 5 | land_boundary_dispute | Land Survey Act s.5 as "the basis for requesting a re-survey of a disputed boundary". | s.5 fixes the boundaries of a municipality, rural municipality or ward, not a boundary between two private plots. The neighbour dispute route is the local Judicial Committee (Local Government Operation Act s.47) or the court, with a 6-month suit limit (Civil Code s.298). |
| 6 | right_to_information_request | "If refused, appeal to the National Information Commission", no deadline. | s.9 first requires a complaint to the head of the public body within **7 days**; only then can you appeal to the Commission within **35 days** (s.10). |
| 7 | traffic_accident_compensation | Claim through the insurer, District Court if refused. | The Act and Rules route payment through the Chief District Officer, who must have the insurer pay within 21 days (death) or 3 months. |
| 8 | workplace_sexual_harassment | Forum: workplace, police or Labour Office; no deadlines. | The Act names the Chief District Officer as the complaint-hearing authority; complaint to the manager within 15 days, to the CDO within 90 days. |
| 9 | cheque_bounce | Complaint within 1 year of learning of the offence; police or Gazette-designated court. | For a bounced cheque the 1 year runs from the date the bank *certified* the dishonour, and the case goes to the District Court within 6 months of the complaint (s.17(1क)). The 45-day bank notice step was missing. |
| 10 | Several | "No fixed limitation period" (divorce, child_custody, maintenance, land, tenant, bonus etc.). | The Civil Code's chapter-level limitation sections (3 or 6 months, e.g. ss.92, 104, 123, 265, 298, 405) exist and were not mentioned. Where their reach is unclear, the playbook now says so. |

## Summary table

| Playbook | Provisions kept / removed / added | Review items |
|---|---|---|
| bonus_not_paid | 3 / 0 / 2 | 1 |
| cheque_bounce | 4 / 0 / 1 | 2 |
| child_custody | 3 / 0 / 1 | 3 |
| child_marriage_protection | 1 / 0 / 1 | 2 |
| citizenship_by_descent | 2 / 0 / 3 | 3 |
| consumer_complaint | 3 / 0 / 2 | 3 |
| cyber_harassment | 2 / 1 / 4 | 3 |
| defamation | 2 / 0 / 2 | 3 |
| divorce | 4 / 0 / 3 | 3 |
| domestic_violence | 2 / 1 / 5 | 2 |
| fir_not_registered | 2 / 0 / 1 | 2 |
| foreign_employment_fraud | 2 / 1 / 2 | 3 |
| inheritance_share | 3 / 0 / 4 | 3 |
| land_boundary_dispute | 1 / 1 / 2 | 3 |
| maintenance_alimony | 2 / 0 / 4 | 3 |
| physical_assault | 2 / 0 / 1 | 2 |
| right_to_information_request | 1 / 1 / 1 | 2 |
| tenant_eviction_without_notice | 0 / 2 / 6 | 3 |
| theft_complaint | 2 / 0 / 4 | 2 |
| traffic_accident_compensation | 2 / 0 / 4 | 3 |
| unpaid_personal_loan | 1 / 2 / 5 | 4 |
| unpaid_salary | 2 / 0 / 0 | 3 |
| workplace_sexual_harassment | 2 / 1 / 5 | 3 |
| wrongful_termination | 2 / 0 / 5 | 3 |
| deposit_not_returned | already corrected (model) | see note below |

`deposit_not_returned` was not changed. One observation for the advocate: its note on Civil Code s.386 says a house "must be let under a written agreement"; s.386(2) exempts rents up to Rs 20,000 a month from the written-agreement rule.

## How to read the per-playbook sections

- *kept*: the provision was already cited and is still cited; *replaced/removed*: the old citation was wrong or off-point and was taken out; *added*: a governing rule, remedy, forum or deadline that was missing.
- "Final pinned list" is the ordered list the chat engine pins at the top of the answer's evidence. Some added sections were left out of that list on purpose (see method notes); their content is carried in the forum and limitation text where relevant.
- "Excluded from evidence" uses the new optional `exclude_provisions` field: sections that keyword search keeps surfacing for the situation but that govern something else.
- Section numbers follow the corpus's own entries. A few corpus entries hold several sub-sections (for example the entry `306 (2)` holds the exceptions listed in s.306(3)).

## Method and limits of this audit

- Source of truth: the Nepali text in `backend/app/data/corpus`, read section by section. English notes were checked against that Nepali text, not against titles or the old notes. Every number in a note (days, months, amounts, percentages) was checked.
- Every citation still resolves (`tests/test_playbooks.py` passes) and the full suite passes.
- Not in the corpus, so not checkable here: the Criminal Procedure Code schedules (which offences the state prosecutes), most delegated rules and later amendments after the corpus date, court practice and case law. Anything that depends on those is a NEEDS-ADVOCATE-REVIEW item.
- Where a section says only "as prescribed" or "the concerned court", the playbook now says so instead of naming a body.

## System observations found while auditing (not changed here)

1. **The playbook matcher over-matches.** In the retrieval evaluation set, unrelated questions match a playbook (for example the constitutional-rights questions match `right_to_information_request`, "Is child labour prohibited?" and "How do I register a marriage?" match `child_marriage_protection`, "Someone borrowed money from me" matches `physical_assault`). Because matched playbooks pin their provisions above everything else, each extra pinned provision pushes the right answer further down for those questions. This is why the pinned lists are short (2 to 7 entries) and why the evaluation sets a limit. Tightening the matcher (keywords were deliberately not touched here) would allow richer pinned lists.
2. `tests/test_v1_trust_engine.py::test_salary_question_flags_1970s_precedents_as_stale` hard-codes the exact pinned list for `unpaid_salary` as [s.34, s.162], so the salary playbook's procedure sections (Labour Act ss.113-115, 165) are in its forum and steps text but not pinned. Update that test if they should be pinned.
3. Some corpus entries merge neighbouring sections (Citizenship Act s.18 sits inside the entry for s.17). Those cannot be cited on their own; the citizenship playbook mentions s.18's 35-day appeal in text only.

## Per-playbook findings

### bonus_not_paid - Employer has not paid bonus

Status: CHANGED (notes rewritten, limitation citation removed)

Provisions before -> after: kept 3, removed 0, added 2.  Final pinned list (in order): बोनस ऐन 6; बोनस ऐन 9; बोनस ऐन 16; बोनस ऐन 5; बोनस ऐन 7.

| Provision | Action | What was wrong / why |
|---|---|---|
| बोनस ऐन, २०३० दफा 6 | kept, note rewritten | Note was a generic one-liner; now states the half-year-worked rule and the casual/substitute exclusion. |
| बोनस ऐन, २०३० दफा 9 | kept, note rewritten | Note omitted the 8-month deadline and the Labour Office's power to extend by up to 3 months. |
| बोनस ऐन, २०३० दफा 16 | kept, note rewritten | Note omitted the actual procedure: Labour Office talks, then decision, appeal to Labour Court within 35 days (final). |
| बोनस ऐन, २०३० दफा 5 | ADDED | Core rule: 10 percent of net profit must be set aside as bonus. Missing entirely. |
| बोनस ऐन, २०३० दफा 7 | ADDED | Core rule: how the percentage is worked out and the cap (8 months' pay up to twice the minimum wage; 6 months' pay above). |
| श्रम ऐन, २०७४ दफा 162 (limitation) | REMOVED as limitation citation | Section 162 gives 6 months for complaints about acts contrary to the *Labour Act*; bonus is governed by the separate Bonus Act, which has no limitation clause in our corpus. The old note asserted a "6 month" window as fact. |

Other fixes: forum now names the Labour Office procedure and the 35-day appeal; next steps mention the 8-month payment period.

**NEEDS-ADVOCATE-REVIEW**
- Deadline to complain about unpaid bonus. Bonus Act has none in our corpus; whether Labour Act s.162 (6 months) applies by analogy is unknown. Note now says so honestly.

### cheque_bounce - Cheque given to me bounced

Status: CHANGED (limitation and forum were wrong; notes rewritten)

Provisions before -> after: kept 4, removed 0, added 1.  Final pinned list (in order): विनिमेय अधिकारपत्र ऐन 65; बैङ्किङ्ग कसूर तथा सजाय ऐन 3क; बैङ्किङ्ग कसूर तथा सजाय ऐन 15 (1); बैङ्किङ्ग कसूर तथा सजाय ऐन 17; बैङ्किङ्ग कसूर तथा सजाय ऐन 26क.
Excluded from evidence: धनादेश नियमावली 3; धनादेश नियमावली 4; धनादेश नियमावली 15.

| Provision | Action | What was wrong / why |
|---|---|---|
| बैङ्किङ्ग कसूर तथा सजाय ऐन, २०६४ दफा 17 (also the limitation provision) | kept, note and limitation rewritten | Note said "1 year from learning of the offence" and "designated court by Gazette notice". For cheques, s.17(1क) says 1 year from the date dishonour was *certified* (प्रमाणित), and the case goes to the *District Court* within 6 months of the complaint. |
| बैङ्किङ्ग कसूर तथा सजाय ऐन, २०६४ दफा 3क | kept, note rewritten | Note only said "offence"; omitted the real mechanism: up to 45 days bank notice to the account holder, then bank certifies dishonour within 3 days; account holder can pay and take cheque back. |
| बैङ्किङ्ग कसूर तथा सजाय ऐन, २०६४ दफा 15 (1) | kept, note rewritten | Note said only "amount plus interest plus fine/imprisonment"; now states 5 percent fine and the jail tiers by amount (s.15(1क)). |
| विनिमेय अधिकारपत्र ऐन, २०३४ दफा 65 | kept (now first in the pinned list) | Accurate definition of dishonour; note tightened. |
| बैङ्किङ्ग कसूर तथा सजाय ऐन, २०६४ दफा 18 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Government is plaintiff in these cases (explains police complaint route). |
| बैङ्किङ्ग कसूर तथा सजाय ऐन, २०६४ दफा 26क | ADDED | Settlement route: paying the cheque amount and agreeing to settle removes punishment. |
| विनिमेय अधिकारपत्र ऐन, २०३४ दफा 108 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | 5-year limitation for a civil suit on a negotiable instrument. |
| exclude: धनादेश नियमावली, २०३१ दफा 3, 4, 15 | EXCLUDED | Postal money-order rules that surface on "cheque" searches; unrelated to bank cheques. |

Other fixes: forum, limitation note and next steps rewritten to follow s.3क / s.17(1क) / s.18.

**NEEDS-ADVOCATE-REVIEW**
- Whether a criminal complaint under s.3क/15 and a civil suit on the cheque (NI Act s.108, 5 years) can run in parallel, and how the two interact.
- Which body/step currently starts the case in practice (police complaint vs. direct application to the government attorney) after Muluki Criminal Procedure Code 2074 applied by s.18.

### child_custody - Custody of children after separation/divorce

Status: CHANGED (note on s.115 was incomplete; limitation claim contradicted the Code)

Provisions before -> after: kept 3, removed 0, added 1.  Final pinned list (in order): मुलुकी देवानी संहिता 115; मुलुकी देवानी संहिता 116; मुलुकी देवानी संहिता 117; बालबालिका सम्बन्धी ऐन 16.

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी देवानी संहिता, २०७४ दफा 115 | kept, note rewritten | Note said "a child under 5 generally stays with the mother" only. The section has two different regimes: after legal divorce (mother if she wants; from age 5 only if she has not remarried, otherwise father) versus parents merely living apart (under 5 mother; 5 to under 10 father; 10+ the child's choice), plus a written agreement overriding all, plus the child's opinion at 10+. |
| मुलुकी देवानी संहिता, २०७४ दफा 116 | kept, note rewritten | Omitted the key rule: the non-custodial parent with higher income must pay for the child's upkeep, education and medical care as agreed or as the court orders. |
| मुलुकी देवानी संहिता, २०७४ दफा 117 | kept, note rewritten | Added: frequency fixed by parents, else District Court; court may stop visits that harm the child. |
| मुलुकी देवानी संहिता, २०७४ दफा 114 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Both parents jointly responsible for care and upbringing. |
| बालबालिका सम्बन्धी ऐन, २०७५ दफा 16 | ADDED | Child's best interest comes first; s.16(3) requires the prescribed best-interest process when deciding who raises the children after divorce. |
| मुलुकी देवानी संहिता, २०७४ दफा 118 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Parent-child rights and duties survive the end of the marriage. |
| मुलुकी देवानी संहिता, २०७४ दफा 123 (limitation) | ADDED as limitation provision (final: limitation citation only, not pinned) | Old note said "no fixed deadline" with no citation. Section 123 gives 6 months for suits under the parent-child chapter. |

**NEEDS-ADVOCATE-REVIEW**
- Whether the 6-month limit in s.123 applies to a custody claim, and from what date it runs.
- The Code has no express standalone "custody petition" provision in the corpus; the correct forum/procedure for a custody claim not tied to a divorce petition (District Court vs Child Court under Children Act 2075).
- The "best-interest determination process" referred to in Children Act s.16(3) is "as prescribed" (in rules not in our corpus).

### child_marriage_protection - Stop or report a child marriage

Status: CHANGED (missing 3-month reporting deadline; forum cited a body not in the law)

Provisions before -> after: kept 1, removed 0, added 1.  Final pinned list (in order): मुलुकी अपराध संहिता 173; मुलुकी अपराध संहिता 176.
Excluded from evidence: नेपाल स्वास्थ्य सेवा नियमावली 116; संघीय संसद सचिवालय कर्मचारी प्रशासन नियमावली 116.

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी अपराध संहिता, २०७४ दफा 173 | kept | Correct: under 20 barred, marriage void, up to 3 years and Rs 30,000 (verified against text). |
| मुलुकी अपराध संहिता, २०७४ दफा 176 | ADDED, also now the limitation provision | Playbook said "report as soon as possible" with no deadline. Section 176 bars a complaint after 3 months from learning of the offence. This is the most important omission. |
| मुलुकी अपराध संहिता, २०७४ दफा 171 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Consent by someone under the marriage age does not count as consent, so a child's "agreement" does not legalise the marriage. |
| मुलुकी देवानी संहिता, २०७४ दफा 72 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Civil-law rule: a marriage below 20 (s.70(1)(घ)) or without consent is void from the start. |
| मुलुकी देवानी संहिता, २०७४ दफा 75 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Children already born from a void marriage keep their legal rights. |
| बालबालिका सम्बन्धी ऐन, २०७५ दफा 50 (1) | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Duty to report a child needing special protection to the local child welfare officer, who can rescue and place the child in temporary protection. |

Other fixes: forum said "the local ward office ... can intervene to stop a planned child marriage" - nothing in the corpus gives ward offices that power; replaced with the police and the local child welfare officer (Children Act ss.50, 61). Next steps now carry the 3-month deadline.

**NEEDS-ADVOCATE-REVIEW**
- Whether the 3-month limit in Criminal Code s.176 runs from the date of the marriage or from when the reporter learned of it when the marriage is ongoing/continuing.
- Whether the local ward office has any statutory power to stop a marriage (none found in corpus; removed from the playbook).

### citizenship_by_descent - Citizenship by descent (self or child)

Status: CHANGED (missed the age-16 rule and the mother/foreign-father exception; note on Constitution art. 11 was vague; appeal route added)

Provisions before -> after: kept 2, removed 0, added 3.  Final pinned list (in order): नेपालको संविधान 11; नेपाल नागरिकता ऐन 3 (1); नेपाल नागरिकता ऐन 8 (1); नेपाल नागरिकता ऐन 8 (2); नेपाल नागरिकता ऐन 5 (1).

| Provision | Action | What was wrong / why |
|---|---|---|
| नेपालको संविधान दफा/धारा 11 | kept, note rewritten | Note was a vague "under conditions set out". Now cites 11(2)(ख), (4), (5) and the 11(7) exception. Note that 11(2) opens with persons resident in Nepal at the Constitution's commencement; the Act's s.3(1) is the operative rule for later births. |
| नेपाल नागरिकता ऐन, २०६३ दफा 3 (1) | kept, note rewritten | Omitted the sub-section 2 exception: a child of a Nepali mother and foreign father is handled under s.5(2) as naturalised, not by descent. |
| नेपाल नागरिकता ऐन, २०६३ दफा 8 (1) | ADDED | Missing procedure: applicant must have completed 16 years; documents (parent or 3-generation relative's certificate, municipal recommendation). The playbook is titled "citizenship for my child" but never said a child under 16 cannot apply. |
| नेपाल नागरिकता ऐन, २०६३ दफा 8 (2) | ADDED | Fallback if documents are missing: family-member identification, then on-the-spot inquiry with two citizens and local official. |
| नेपाल नागरिकता ऐन, २०६३ दफा 5 (1) | ADDED | Naturalised route for children of a Nepali mother and foreign father. |

Other fixes: evidence list now includes the municipal recommendation; limitation note says the Act sets no deadline but age 16 is required, and the 35-day appeal to the Home Ministry Secretary (s.18) is mentioned in the note and forum. Section 18 has no separate entry in the corpus (its text is merged into the entry for s.17), so it is not cited as a provision.

**NEEDS-ADVOCATE-REVIEW**
- The Act names only the "prescribed officer" (तोकिएको अधिकारी) as issuer. District Administration Office is retained from the original playbook and is consistent with s.18, but the citizenship rules are not in the corpus.
- Whether an under-16 can obtain any proof of entitlement in practice (birth registration, recommendation) before turning 16.
- Whether a child of a Nepali mother and foreign father falls under 11(7)/5(2) or, if both parents were citizens, under descent; edge cases (unknown father) are complex.

### consumer_complaint - Defective product / cheated as consumer

Status: CHANGED (missed the 6-month compensation deadline and the return-of-goods right; compensation routed to the wrong body in next steps)

Provisions before -> after: kept 3, removed 0, added 2.  Final pinned list (in order): उपभोक्ता संरक्षण ऐन 3; उपभोक्ता संरक्षण ऐन 36; उपभोक्ता संरक्षण ऐन 50; उपभोक्ता संरक्षण ऐन 14; उपभोक्ता संरक्षण ऐन 16 (1).

| Provision | Action | What was wrong / why |
|---|---|---|
| उपभोक्ता संरक्षण ऐन, २०७५ दफा 3 | kept, note tightened | Correct but generic; note now lists the rights that matter here. |
| उपभोक्ता संरक्षण ऐन, २०७५ दफा 36 | kept, note extended | Correct; added confidential-name right. |
| उपभोक्ता संरक्षण ऐन, २०७५ दफा 50 | kept, note corrected, now the limitation provision | Old note omitted that the compensation claim goes to the *court* and must be filed within *6 months* of the loss. Old playbook said "the Act doesn't fix a single deadline" and cited only the appeal period. |
| उपभोक्ता संरक्षण ऐन, २०७५ दफा 45 (was limitation provision) | kept as provision (final: dropped from the pinned list to limit evidence crowding) | Appeal to High Court within 30 days (verified). It is an appeal period, not the deadline to start a claim, so it is no longer the limitation provision. |
| उपभोक्ता संरक्षण ऐन, २०७५ दफा 14 | ADDED | Core remedy for defective goods missing: return within 7 days (15 if sealed) for replacement or refund, no deductions, bill required; list of goods that cannot be returned. |
| उपभोक्ता संरक्षण ऐन, २०७५ दफा 11 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Seller must honour guarantee/warranty and give bill. |
| उपभोक्ता संरक्षण ऐन, २०७५ दफा 16 (1) | ADDED | Unfair trade practices (false quality, misleading advertisements) - the "cheated" limb of the issue. |
| उपभोक्ता संरक्षण ऐन, २०७५ दफा 51 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Treatment costs and interim relief if injured. |

Other fixes: next step 3 told users to "include a compensation claim in your complaint" to the Department; under s.50 compensation is claimed in court, so the step now says so with the 6-month limit.

**NEEDS-ADVOCATE-REVIEW**
- Muluki Civil Code s.430 ("a buyer cannot later claim that purchased property is spoiled or inferior, except for fraud or if it differs from the document") surfaces in search for this issue. It sits in the chapter on transfer of property; how it interacts with the later, special Consumer Protection Act (ss.14, 50) for ordinary goods is unclear. It is not pinned.
- Whether consumer courts under s.41 have actually been constituted in the user's district (the Act leaves it to a Gazette notice); otherwise where a s.50 claim is filed in practice.
- Whether the 6-month period in s.50 runs from the date of harm or knowledge (text says the date the loss was caused).

### cyber_harassment - Online harassment / photos or private information shared

Status: CHANGED (SERIOUS: limitation provision was from the homicide chapter; main cyber-offence law was missing)

Provisions before -> after: kept 2, removed 1, added 4.  Final pinned list (in order): मुलुकी अपराध संहिता 298; मुलुकी अपराध संहिता 307; विद्युतीय (इलेक्ट्रोनिक) कारोबार ऐन 47; मुलुकी अपराध संहिता 296; मुलुकी अपराध संहिता 300; विद्युतीय (इलेक्ट्रोनिक) कारोबार ऐन 74.

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी अपराध संहिता, २०७४ दफा 187 (provision and limitation provision) | REMOVED | Section 187 is the limitation clause for the *homicide (ज्यान) chapter* (offences under ss.177-184: 20 years / 2 years / 6 months). It has nothing to do with online harassment. The playbook described it as "General limitation clause for this part of the Criminal Code". |
| मुलुकी अपराध संहिता, २०७४ दफा 298 | kept, note rewritten | Note was loose; now states the actual penalty (2 years / Rs 20,000). |
| मुलुकी अपराध संहिता, २०७४ दफा 307 | kept, note corrected | Note said "higher fine" for electronic defamation; text adds up to 1 year and Rs 10,000. Added compensation and costs. |
| विद्युतीय (इलेक्ट्रोनिक) कारोबार ऐन, २०६३ दफा 47 | ADDED | The core cyber-offence provision (online insult/harassment of women, unlawful material; up to Rs 1 lakh or 5 years). Missing entirely. |
| विद्युतीय (इलेक्ट्रोनिक) कारोबार ऐन, २०६३ दफा 74 (now limitation provision) | ADDED | 90 days from learning of the offence to complain. |
| मुलुकी अपराध संहिता, २०७४ दफा 295, 296 | ADDED (final: only some of these sections are pinned) | Photo taken/altered/circulated without permission (the "private photos" limb of the issue). |
| मुलुकी अपराध संहिता, २०७४ दफा 299, 300 | ADDED (final: only some of these sections are pinned) | Harassing/deceptive messages and threats by electronic means. |
| मुलुकी अपराध संहिता, २०७४ दफा 304 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | 3 months from the act for privacy offences. |
| मुलुकी अपराध संहिता, २०७४ दफा 308 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | 3 months from learning for defamation offences. |

Other fixes: old limitation note said only "criminal complaints have their own time limits"; now states 90 days / 3 months and the forum notes the government-plaintiff rule (ETA s.75), tribunal compensation (s.58क) and the Privacy Act route (ss.30-31, District Court, 3 months).

**NEEDS-ADVOCATE-REVIEW**
- Which deadline governs when the same online conduct fits both the Electronic Transactions Act (90 days from learning) and the Criminal Code (3 months from the act): treat the shorter as binding until an advocate confirms.
- Section 47 of the Electronic Transactions Act is broadly worded and its constitutionality/enforcement scope (esp. for speech) has been contested; confirm current practice with the Cyber Bureau.
- The Privacy Act 2075 s.16/s.29-31 overlap with Criminal Code ss.295-296 (Privacy Act complaints go to District Court within 3 months); which route to prefer is a strategy question for an advocate.

### defamation - Someone defamed me

Status: CHANGED (missing 3-month deadline; note on 306 omitted the statutory exceptions; forum unverified)

Provisions before -> after: kept 2, removed 0, added 2.  Final pinned list (in order): मुलुकी अपराध संहिता 306 (1); मुलुकी अपराध संहिता 307; मुलुकी अपराध संहिता 308; मुलुकी अपराध संहिता 306 (2).

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी अपराध संहिता, २०७४ दफा 306 (1) | kept, note rewritten | Note was a loose paraphrase; now tracks the text of the definition (intent, or knowing it could harm; character assassination; false charge of shameful bodily condition). |
| मुलुकी अपराध संहिता, २०७४ दफा 306 (2) | ADDED | This corpus entry holds the exceptions list (the text of s.306(3)): true facts published for the public good with evidence, fair comment on public conduct, lawful accusation etc. The AI must not tell users that "truth is always a defence" or that all false statements are defamation. |
| मुलुकी अपराध संहिता, २०७४ दफा 307 | kept, note corrected | Note said "higher fine" for electronic defamation; the text adds up to 1 year and Rs 10,000. Added the mandatory compensation and costs rule. |
| मुलुकी अपराध संहिता, २०७४ दफा 308 (now the limitation provision) | ADDED | Playbook had no limitation citation and told users to "check with the police". Section 308: no complaint after 3 months from learning of the offence. |

Other fixes: forum "police, or directly with the District Court" is not supported by the corpus text (which classes the offence in the Criminal Procedure Code schedules that are not in the corpus), so it now says to ask an advocate. Next steps mention noting the date of first learning.

**NEEDS-ADVOCATE-REVIEW**
- Whether defamation is prosecuted by the state (Criminal Procedure Code Schedule 1) or on the victim's own complaint (Schedule 2), and hence whether a complaint goes to the police or directly to the District Court. The schedules are not in our corpus.
- How the 3-month period in s.308 works for a continuing publication (e.g., a post that stays online).
- Interaction with online-specific offences (Electronic Transactions Act s.47, 90-day complaint limit) when the defamation is on social media.

### divorce - Divorce from spouse

Status: CHANGED (grounds and money consequences were missing; limitation claim contradicted the Code; forum overstated)

Provisions before -> after: kept 4, removed 0, added 3.  Final pinned list (in order): मुलुकी देवानी संहिता 96; मुलुकी देवानी संहिता 97; मुलुकी देवानी संहिता 98; मुलुकी देवानी संहिता 99; मुलुकी देवानी संहिता 93; मुलुकी देवानी संहिता 94; मुलुकी देवानी संहिता 95.
Excluded from evidence: मुलुकी देवानी संहिता 706.

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी देवानी संहिता, २०७४ दफा 96 | kept | Correct. Forum note now says "concerned District Court" as the text does (old forum said "where you or your spouse resides", which is not in the text). |
| मुलुकी देवानी संहिता, २०७४ दफा 97 | kept | Correct. |
| मुलुकी देवानी संहिता, २०७४ दफा 98 | kept, note rewritten | Omitted the proviso: if the spouses still refuse to reconcile, the court must grant divorce one year after the petition. |
| मुलुकी देवानी संहिता, २०७४ दफा 99 | kept, note rewritten | Note was vague ("addressed before or alongside"); text requires joint property to be divided before divorce, wife's right to interim monthly expenses, loss on remarriage, and the husband's exemption in sub-section 6. |
| मुलुकी देवानी संहिता, २०७४ दफा 93 | ADDED | Mutual-consent divorce at any time. |
| मुलुकी देवानी संहिता, २०७४ दफा 94 | ADDED | Grounds on which a husband can divorce without the wife's consent (core rule missing). |
| मुलुकी देवानी संहिता, २०७४ दफा 95 | ADDED | Grounds on which a wife can divorce without the husband's consent (incl. 3-year separation, expulsion, another marriage, rape). |
| मुलुकी देवानी संहिता, २०७४ दफा 100 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Lump-sum or periodic payment to a divorced wife who does not take a share. |
| मुलुकी देवानी संहिता, २०७४ दफा 104 (limitation) | ADDED (final: limitation citation only, not pinned) | Old note said "no fixed limitation period". Section 104 gives 3 months for suits over acts under this chapter. |
| exclude: मुलुकी देवानी संहिता, २०७४ दफा 706 | EXCLUDED | Recognition of divorces obtained abroad; keeps surfacing on "divorce" searches but governs a different situation. |

**NEEDS-ADVOCATE-REVIEW**
- Whether the 3-month limit in s.104 applies to a divorce petition itself or only to ancillary claims (property, expenses). The playbook now says this is unclear.
- Which District Court is "concerned" (territorial jurisdiction) under the civil procedure code.
- Whether the "3 years apart" grounds in ss.94(क)/95(क) interact with the one-year rule in s.98.

### domestic_violence - Facing domestic violence, need protection

Status: CHANGED (weak notes; forum mixed in bodies the Act does not name; core provisions missing)

Provisions before -> after: kept 2, removed 1, added 5.  Final pinned list (in order): घरेलु हिंसा (कसूर र सजाय) ऐन 6; घरेलु हिंसा (कसूर र सजाय) ऐन 12क; घरेलु हिंसा (कसूर र सजाय) ऐन 14; घरेलु हिंसा (कसूर र सजाय) ऐन 2 (1); घरेलु हिंसा (कसूर र सजाय) ऐन 4 (1); घरेलु हिंसा (कसूर र सजाय) ऐन 5; घरेलु हिंसा (कसूर र सजाय) ऐन 13.

| Provision | Action | What was wrong / why |
|---|---|---|
| घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६ दफा 3 | REMOVED | Correct but adds nothing beyond ss.2 and 13; replaced by definition and penalty sections. |
| घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६ दफा 6 | kept, note expanded | Note omitted what the interim order can actually do (stay in home, treatment, separate residence, no harassment). |
| घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६ दफा 12क | kept, note corrected | Note said a Protection Officer "is designated"; the section says the local level *may* appoint one. Old forum said the police, the "Women and Children Service Directorate" and the court "can involve the Protection Officer" — none of this is in the Act. |
| घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६ दफा 14 (limitation) | kept, also pinned | 90 days from the act - verified. |
| घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६ दफा 2 (1) | ADDED | Definition of domestic violence and domestic relationship (includes couples living together and separated spouses). |
| घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६ दफा 4 (1) | ADDED | Who to complain to (police, National Women's Commission, local level), 24-hour summons, 30-day conciliation, 15-day referral to court. |
| घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६ दफा 5 | ADDED | Victim can file directly in court. |
| घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६ दफा 10 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Compensation. |
| घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६ दफा 11 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Service centres (shelter, legal aid, counselling). |
| घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६ दफा 13 | ADDED | Penalties (Rs 3,000-25,000 / 6 months) and for breaching a protection order (Rs 2,000-15,000 / 4 months). |

Other fixes: limitation note now says serious bodily injury/sexual torture can be reported directly to the police and is prosecuted by the state under other law (ss.5क, 12ग, 13(1)).

**NEEDS-ADVOCATE-REVIEW**
- The 90-day limit in s.14 for continuing or repeated violence (counted from which act) and whether it applies to the police-report route under s.5क.
- Penalty for serious bodily/sexual violence is "as per prevailing law" (s.13(1)); the applicable Criminal Code offences should be confirmed for the specific facts.

### fir_not_registered - Police refused to register my complaint

Status: CHANGED (notes incomplete; Schedule 2 route and higher police office missing)

Provisions before -> after: kept 2, removed 0, added 1.  Final pinned list (in order): मुलुकी फौजदारी कार्यविधि संहिता 4 (1); मुलुकी फौजदारी कार्यविधि संहिता 5; मुलुकी फौजदारी कार्यविधि संहिता 4 (2).

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी फौजदारी कार्यविधि संहिता, २०७४ दफा 4 (1) | kept, note rewritten | Old note said "anyone ... can file"; the text makes it a duty ("must ... as soon as possible") for Schedule 1 offences only, and adds the police duty to register and give a receipt, including for post/electronic reports. |
| मुलुकी फौजदारी कार्यविधि संहिता, २०७४ दफा 5 | kept, note rewritten | Old note and forum mentioned only the District Government Attorney's Office; the section also allows complaint to a *higher-level police office*, requires forwarding and registration, and has a separate route (Chief District Officer, then Home Ministry, within 3 days) for Schedule 2 notices. |
| मुलुकी फौजदारी कार्यविधि संहिता, २०७४ दफा 4 (2) | ADDED | Contains sub-sections 7-10: Schedule 2 offences are reported to the authority designated to investigate; police must forward a misdirected notice within 3 days. |

Other fixes: forum and next steps now say to ask for the receipt and name both escalation routes; limitation note says the Code sets no deadline but the underlying offence may have a short complaint deadline.

**NEEDS-ADVOCATE-REVIEW**
- Which offences fall in Schedule 1 vs Schedule 2 of the Criminal Procedure Code (the schedules are not in our corpus); this decides which route applies to the user's complaint.
- Whether the Chief District Officer / Home Ministry route (s.5(4)) applies to the user's offence, or only where a special investigating authority exists.

### foreign_employment_fraud - Manpower agency cheated me

Status: CHANGED (SERIOUS: told fraud victims a 1-year deadline that does not apply to the fraud offences; forum wrong; core provisions missing)

Provisions before -> after: kept 2, removed 1, added 2.  Final pinned list (in order): वैदेशिक रोजगार ऐन 36; वैदेशिक रोजगार ऐन 44; वैदेशिक रोजगार ऐन 43; वैदेशिक रोजगार ऐन 64.

| Provision | Action | What was wrong / why |
|---|---|---|
| वैदेशिक रोजगार ऐन, २०६४ दफा 60 (limitation) | kept, note and limitation rewritten (final: limitation citation only, not pinned) | Old playbook: "file your complaint within 1 year of the incident (or ... of returning)". Section 60 imposes the 1-year bar on offences OTHER than ss.43-47; the false-promise money-taking offences (ss.43-44) are expressly excluded from it. |
| वैदेशिक रोजगार ऐन, २०६४ दफा 36 | kept, note expanded | Now says the Department can order compensation for the whole cost of going abroad. |
| वैदेशिक रोजगार ऐन, २०६४ दफा 51 | kept, note rewritten (final: dropped from the pinned list to limit evidence crowding) | Old note said only "punishable"; text: refund/compensation from cash deposit, Rs 1 lakh fine, licence cancelled, 60-day notice for any shortfall. |
| वैदेशिक रोजगार ऐन, २०६४ दफा 64 | kept, note rewritten | Old forum said "directly the Foreign Employment Tribunal for compensation claims". Under ss.61, 63, 64 the Department investigates, the government is plaintiff, and the Tribunal (District Court until formed) hears criminal cases; compensation is claimed from the Department (s.36). |
| वैदेशिक रोजगार ऐन, २०६४ दफा 44 | ADDED | Licensed agency taking money on a false promise: refund plus 50 percent, Rs 3-5 lakh fine, 3-7 years, licence cancelled. |
| वैदेशिक रोजगार ऐन, २०६४ दफा 43 | ADDED | Same for unlicensed persons (the typical dalal / fake agent). |
| वैदेशिक रोजगार ऐन, २०६४ दफा 20 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | If not sent within 3 months: refund plus 25 percent a year within 30 days. |
| वैदेशिक रोजगार ऐन, २०६४ दफा 55 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Contract switching (lower pay, different job): Rs 1 lakh fine and shortfall repaid. |
| वैदेशिक रोजगार ऐन, २०६४ दफा 21क | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Complaints can be made by post/electronically and through the Chief District Officer. |

Other fixes: forum and steps mention the appeal periods (35 days, s.66).

**NEEDS-ADVOCATE-REVIEW**
- If the s.60 one-year bar does not apply to ss.43-47, which limitation period does apply to a false-promise fraud case (general Criminal Code/Procedure rules not in the playbook)?
- The Department-imposed penalties (ss.51, 55) are inside the 1-year rule: confirm how it is counted for a worker who is still abroad.
- Section 55 has a note in the corpus that the 2082 amendment "is unclear"; confirm the current text.

### inheritance_share - Share (अंश) of family/ancestral property

Status: CHANGED (limitation note incomplete; who counts as अंशियार and succession rules missing)

Provisions before -> after: kept 3, removed 0, added 4.  Final pinned list (in order): मुलुकी देवानी संहिता 206; मुलुकी देवानी संहिता 222; मुलुकी देवानी संहिता 235; मुलुकी देवानी संहिता 205; मुलुकी देवानी संहिता 220; मुलुकी देवानी संहिता 239; मुलुकी देवानी संहिता 250.

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी देवानी संहिता, २०७४ दफा 206 | kept, note refined | Correct (equal shares, unborn child's share); added the redistribution rule if no live birth. |
| मुलुकी देवानी संहिता, २०७४ दफा 222 | kept, note rewritten | Old note said "a coparcener can demand partition by bringing a statement"; s.222 is the court's duty to divide once the property list is filed and to obtain a no-concealment statement. |
| मुलुकी देवानी संहिता, २०७४ दफा 235 (limitation) | kept, note completed, also pinned | Omitted limb (घ): 6 months in all other cases. Also clarified that "no time limit" applies where no partition happened or a partition deed exists and both sides have enjoyed their shares. |
| मुलुकी देवानी संहिता, २०७४ दफा 205 | ADDED | Who counts as अंशियार (spouses, parents, sons, daughters). |
| मुलुकी देवानी संहिता, २०७४ दफा 209 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Grandchildren/wives take only from their own father's/husband's portion; heirs of a deceased before partition. |
| मुलुकी देवानी संहिता, २०७४ दफा 220 | ADDED | The suit requires a property/debt list (फाँटबारी) and the separation date; married daughter's separation date is her wedding day. |
| मुलुकी देवानी संहिता, २०७४ दफा 239 | ADDED | Order of heirs where the owner has died (the playbook is titled "inheritance"). |
| मुलुकी देवानी संहिता, २०७४ दफा 250 | ADDED | 3-year limit for inheritance claims after death unless another period applies. |

Other fixes: forum said "District Court where the property is located" — the text does not say that; now says an advocate should confirm the court.

**NEEDS-ADVOCATE-REVIEW**
- Territorial jurisdiction (which District Court) for a partition suit.
- Whether a married daughter's right to a share is affected by s.220's Explanation (घ) "date of marriage" rule and by any agreement (the text says "unless otherwise agreed").
- How the 3-month period in s.235(ख) and the 6-month catch-all in s.235(घ) apply to a person claiming that an earlier partition deed was unfair.

### land_boundary_dispute - Boundary dispute with neighbour

Status: CHANGED (SERIOUS: primary cited provision governed municipal/ward boundaries, not neighbours' plots; limitation and forum wrong)

Provisions before -> after: kept 1, removed 1, added 2.  Final pinned list (in order): जग्गा (नाप जाँच) ऐन 8; स्थानीय सरकार सञ्‍चालन ऐन 47 (2); मुलुकी देवानी संहिता 287.
Excluded from evidence: जग्गा (नाप जाँच) ऐन 5; जग्गा (नाप जाँच) नियमावली 8; विर्ता उन्मुलन नियमावली 10.

| Provision | Action | What was wrong / why |
|---|---|---|
| जग्गा (नाप जाँच) ऐन, २०१९ दफा 5 | REMOVED and EXCLUDED | Section 5 says how the boundaries of a municipality, rural municipality or ward are fixed before a survey. It has nothing to do with a boundary between two private plots. The playbook called it "the basis for requesting a re-survey of a disputed boundary". Now excluded from evidence, as is the equivalent जग्गा (नाप जाँच) नियमावली, २०५८ नियम 8. |
| जग्गा (नाप जाँच) ऐन, २०१९ दफा 8 | kept, note rewritten | Added the 60-day objection period to the ownership certificate; old note only said the owner receives a certificate. |
| स्थानीय सरकार सञ्‍चालन ऐन, २०७४ दफा 47 (2) | ADDED | Local Judicial Committee mediates one person pressing onto/encroaching another's land; parties may go straight to court; 35 days if no other limit applies. This is the practical first forum. |
| मुलुकी देवानी संहिता, २०७४ दफा 287 | ADDED | No occupying or using another's land without consent. |
| मुलुकी देवानी संहिता, २०७४ दफा 267 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Owner's right to fence, mark the boundary and sue to protect the land. |
| मुलुकी देवानी संहिता, २०७४ दफा 279 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Building on another's land: buy-out options and 3-month demolition rule. |
| मुलुकी देवानी संहिता, २०७४ दफा 298 | ADDED, now limitation provision (final: limitation citation only, not pinned) | 6 months from knowledge for suits under the land occupation chapter. Old note said "no single fixed deadline". |
| जग्गा (नाप जाँच) ऐन, २०१९ दफा 6 (5) | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | On re-survey, "yours-mine" disputes are registered per existing records. |
| जग्गा (नाप जाँच) ऐन, २०१९ दफा 7 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Area found different at survey is recorded as surveyed. |
| exclude: विर्ता उन्मुलन नियमावली, २०१७ नियम 10 | EXCLUDED | Historical Birta land-tenure rule about "disputed land" that surfaces on search; unrelated. |

**NEEDS-ADVOCATE-REVIEW**
- Which limitation applies to a neighbour's encroachment suit: 6 months (s.298, land occupation chapter), 1 year (s.275, ownership/possession chapter) or none for an ownership declaration. Note now says it is unclear.
- Whether an individual owner can compel a fresh survey ("re-survey") of a single plot; the corpus Survey Act gives no such right (the old forum assumed one). Removed as a promise.
- Whether the Judicial Committee's 35-day rule in LGOA s.47(4) conflicts with the 6-month civil limit.

### maintenance_alimony - Financial support from spouse

Status: CHANGED (notes incomplete; local-level route and deadline missing)

Provisions before -> after: kept 2, removed 0, added 4.  Final pinned list (in order): मुलुकी देवानी संहिता 89; मुलुकी देवानी संहिता 101; मुलुकी देवानी संहिता 211; मुलुकी देवानी संहिता 99; मुलुकी देवानी संहिता 100; स्थानीय सरकार सञ्‍चालन ऐन 47 (1).

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी देवानी संहिता, २०७४ दफा 89 | kept, note tightened | Correct (duty to provide food, clothing, health care per standing and capacity). |
| मुलुकी देवानी संहिता, २०७४ दफा 101 | kept, note completed | Omitted the two exceptions: no payment if she remarries or if her income is higher than his. Also clarifies it applies at divorce, to a wife with no property and no share. |
| मुलुकी देवानी संहिता, २०७४ दफा 211 | ADDED | Core rule for non-support inside a joint family: the person can take their share and separate. |
| मुलुकी देवानी संहिता, २०७४ दफा 213 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Spouse who is thrown out or tortured can take a share and separate. |
| मुलुकी देवानी संहिता, २०७४ दफा 99 | ADDED | Interim monthly expenses if property division will take long. |
| मुलुकी देवानी संहिता, २०७४ दफा 100 | ADDED | Lump sum or periodic payments in lieu of a share. |
| स्थानीय सरकार सञ्‍चालन ऐन, २०७४ दफा 47 (1) | ADDED | Local Judicial Committee can decide non-provision of food, clothing or education to spouse or minor children; 35 days if no other limit. |
| मुलुकी देवानी संहिता, २०७४ दफा 92 (limitation) | ADDED (final: limitation citation only, not pinned) | 3-month suit limit for the "consequences of marriage" chapter (which contains s.89). Old note had no limit at all. |

Other fixes: forum lists the Judicial Committee alongside the District Court.

**NEEDS-ADVOCATE-REVIEW**
- The playbook is one-sided: ss.99-101 favour a wife; the corpus has no equivalent for a husband claiming maintenance from a wife. Confirm what applies to a husband or unmarried partner.
- Whether the 3-month limit in s.92 (and s.104) applies to continuing non-payment of maintenance, and from what date it runs.
- Child support is covered in the child_custody playbook (Civil Code s.116); confirm the combined claim procedure.

### physical_assault - Someone physically assaulted me

Status: CHANGED (no deadline given although the Code has one; higher offences and compensation missing)

Provisions before -> after: kept 2, removed 0, added 1.  Final pinned list (in order): मुलुकी अपराध संहिता 191; मुलुकी फौजदारी कार्यविधि संहिता 4 (1); मुलुकी अपराध संहिता 199.

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी अपराध संहिता, २०७४ दफा 191 | kept, note rewritten | Note described the definition but omitted the punishment (up to 3 years / Rs 30,000). |
| मुलुकी फौजदारी कार्यविधि संहिता, २०७४ दफा 4 (1) | kept, note corrected | Old note said "you can file"; it is a duty for Schedule 1 offences, with a registration receipt right. |
| मुलुकी अपराध संहिता, २०७४ दफा 199 (limitation) | ADDED | Limitation was "criminal complaints generally have their own limits". Section 199: 1 year for assault and maiming; 3 months for criminal force; 6 months from regaining consciousness for s.197. |
| मुलुकी अपराध संहिता, २०७४ दफा 192 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Maiming (up to 10 years, Rs 1 lakh). |
| मुलुकी अपराध संहिता, २०७४ दफा 196 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Criminal force and threats of force. |
| मुलुकी अपराध संहिता, २०७४ दफा 198 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Compensation for injury. |

Not pinned: s.194 (assault in provocation/sudden quarrel - reduced punishment) and s.195 (negligent injury) - relevant to the accused's defences rather than the victim's complaint.

**NEEDS-ADVOCATE-REVIEW**
- Whether the 1-year limit in s.199 for assault runs from the offence or from discovery for injuries that show up later (e.g., s.192(3) delayed maiming).
- Whether assault (s.191) is a Schedule 1 (state-prosecuted) offence, which decides if the police must register the report under CPC s.4(1); the schedule is not in our corpus. Domestic violence has its own Act (see domestic_violence).

### right_to_information_request - Request information from a government office

Status: CHANGED (SERIOUS: appeal route skipped a mandatory step and all deadlines were missing)

Provisions before -> after: kept 1, removed 1, added 1.  Final pinned list (in order): सूचनाको हक सम्बन्धी ऐन 7; सूचनाको हक सम्बन्धी ऐन 9.

| Provision | Action | What was wrong / why |
|---|---|---|
| सूचनाको हक सम्बन्धी ऐन, २०६४ दफा 7 | kept, note rewritten | Old note: "following the procedure this section sets out". Now states the reason requirement, 15-day and 24-hour response times, and duty to say if the information is not held. |
| सूचनाको हक सम्बन्धी ऐन, २०६४ दफा 33 | kept, note completed (final: dropped from the pinned list to limit evidence crowding) | Omitted: compensation application goes to the Commission within 3 months. |
| सूचनाको हक सम्बन्धी ऐन, २०६४ दफा 9 (now limitation provision) | ADDED | Playbook said "if refused, appeal to the National Information Commission" and "no deadline". The Act requires a first complaint to the head of the public body within 7 days (s.9). |
| सूचनाको हक सम्बन्धी ऐन, २०६४ दफा 10 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Appeal to the Commission only from the head's decision, within 35 days; Commission decides within 60 days. |
| सूचनाको हक सम्बन्धी ऐन, २०६४ दफा 3 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Citizen-only right and the categories of information that are withheld. |
| सूचनाको हक सम्बन्धी ऐन, २०६४ दफा 6 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Duty to appoint an Information Officer. |
| सूचनाको हक सम्बन्धी ऐन, २०६४ दफा 8 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Fee based on actual cost; complaint to Commission if excessive. |

**NEEDS-ADVOCATE-REVIEW**
- Whether an applicant must in practice state a reason (s.7(1) says "कारण खुलाई") given constitutional RTI case law; the corpus text says so, so the playbook repeats it.
- Whether a complaint to the Commission is available directly when the head of the body fails to decide, and s.34's appeal route beyond the Commission (not read into the playbook).

### tenant_eviction_without_notice - Landlord trying to evict me without notice

Status: CHANGED (SERIOUS: the only real provision cited governed the opposite situation, as in the deposit playbook)

Provisions before -> after: kept 0, removed 2, added 6.  Final pinned list (in order): मुलुकी देवानी संहिता 401; मुलुकी देवानी संहिता 402; मुलुकी देवानी संहिता 385; मुलुकी देवानी संहिता 386; मुलुकी देवानी संहिता 389; स्थानीय सरकार सञ्‍चालन ऐन 47 (1).
Excluded from evidence: मुलुकी देवानी संहिता 400; मुलुकी देवानी संहिता 404.

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी देवानी संहिता, २०७४ दफा 400 | REMOVED and EXCLUDED | Section 400 lists when the *tenant* may leave early (landlord in breach; tenant no longer needs the house, with 35 days' notice by the *tenant*; landlord breach). The playbook's note claimed "this cuts both ways - a landlord also can't force you out outside the legally allowed grounds", which the text does not say. The same section was the source of the wrong "35 days' notice" advice in the deposit playbook. |
| मुलुकी देवानी संहिता, २०७४ दफा 404 | REMOVED | Concerns a tenant who has vanished owing 3+ months' rent; the old note itself said it "does not cover simply wanting the tenant out". |
| मुलुकी देवानी संहिता, २०७४ दफा 401 | ADDED | The actual rule: the list of grounds on which a landlord can remove a tenant, plus the 35-day written notice only when the landlord needs the house himself, the 3-month no-re-letting rule and the tenant's priority. |
| मुलुकी देवानी संहिता, २०७४ दफा 402 | ADDED | When the tenancy ends. |
| मुलुकी देवानी संहिता, २०७४ दफा 385 | ADDED | Term (max 5 years unless commercial). |
| मुलुकी देवानी संहिता, २०७४ दफा 386 | ADDED | Written agreement contents, and the exemption for rent up to Rs 20,000 a month. |
| मुलुकी देवानी संहिता, २०७४ दफा 389 | ADDED | Landlord's duties. |
| स्थानीय सरकार सञ्‍चालन ऐन, २०७४ दफा 47 (1) | ADDED | Local Judicial Committee hears house-rent disputes up to Rs 25 lakh a year; 35 days if no other limit. |
| मुलुकी देवानी संहिता, २०७४ दफा 405 (limitation) | ADDED (final: limitation citation only, not pinned) | 6 months for suits under the tenancy chapter. The old playbook gave no deadline. |

**NEEDS-ADVOCATE-REVIEW**
- Section 401 says the landlord "can remove" (हटाउन सक्नेछ) on the listed grounds but does not say how (court order or self-help). The playbook says so and does not state a method. An advocate should confirm that a landlord cannot lawfully lock out or physically remove a tenant without a court or administrative order.
- No notice period is stated in the Code for grounds other than the landlord's own need (s.401(2)); whether the agreement or custom fills the gap.
- Whether the 6-month limit in s.405 or the 35-day limit for the Judicial Committee governs a claim for unlawful eviction.
- OBSERVATION ON THE DEPOSIT PLAYBOOK (not edited): its note on s.386 says a house "must be let under a written agreement"; s.386(2) exempts rent up to Rs 20,000 a month. Suggest adding that qualifier.

### theft_complaint - Something was stolen

Status: CHANGED (note on s.242 was wrong; 6-month deadline missing)

Provisions before -> after: kept 2, removed 0, added 4.  Final pinned list (in order): मुलुकी अपराध संहिता 242; मुलुकी फौजदारी कार्यविधि संहिता 4 (1); मुलुकी अपराध संहिता 241; मुलुकी अपराध संहिता 243; मुलुकी अपराध संहिता 244; मुलुकी अपराध संहिता 247.
Excluded from evidence: विद्युत चोरी नियन्त्रण ऐन 6; विद्युत चोरी नियन्त्रण ऐन 10.

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी अपराध संहिता, २०७४ दफा 242 | kept, note corrected | Old note: punishment "generally scaled to the value of what was stolen". Section 242 does not scale by value: up to 3 years / Rs 30,000, or 2-7 years / Rs 20,000-70,000 in listed aggravated cases. |
| मुलुकी फौजदारी कार्यविधि संहिता, २०७४ दफा 4 (1) | kept, note corrected | Duty (not just right) to report Schedule 1 offences; registration receipt. |
| मुलुकी अपराध संहिता, २०७४ दफा 241 | ADDED | Definition of theft. |
| मुलुकी अपराध संहिता, २०७४ दफा 243 | ADDED | Burglary (3-5 years). |
| मुलुकी अपराध संहिता, २०७४ दफा 244 | ADDED | Robbery with violence (dakaiti). |
| मुलुकी अपराध संहिता, २०७४ दफा 247 | ADDED | Return of stolen property/value to the owner. |
| मुलुकी अपराध संहिता, २०७४ दफा 248 (limitation) | ADDED (final: limitation citation only, not pinned) | 6 months from knowledge (3 months for ss.245-246). The old note gave no limit. |

**NEEDS-ADVOCATE-REVIEW**
- Section 246 (pick-pocketing) says items of Rs 10,000 or more are treated as ordinary theft under s.241; whether that value line interacts with the punishment.
- Whether theft is a Schedule 1 offence (state prosecutes); schedule not in corpus.

### traffic_accident_compensation - Injured or property damaged in a traffic accident

Status: CHANGED (SERIOUS: forum sent victims to the insurer/District Court, missing the Chief District Officer route with fixed payment deadlines; note on s.163 was inaccurate)

Provisions before -> after: kept 2, removed 0, added 4.  Final pinned list (in order): सवारी तथा यातायात व्यवस्था ऐन 163; सवारी तथा यातायात व्यवस्था ऐन 152; सवारी तथा यातायात व्यवस्था ऐन 166; सवारी तथा यातायात व्यवस्था नियमावली 55; सवारी तथा यातायात व्यवस्था नियमावली 55ग; सवारी तथा यातायात व्यवस्था नियमावली 55ख.

| Provision | Action | What was wrong / why |
|---|---|---|
| सवारी तथा यातायात व्यवस्था ऐन, २०४९ दफा 163 | kept, note rewritten | Old note: entitled to "treatment costs, funeral costs, and compensation". Text: funeral up to Rs 50,000 and compensation for a death; for maiming, compensation and (if the organ works) Rs 25,000-50,000; the Chief District Officer (CDO) must order payment at once (163(2)) and Rs 25,000 immediate medicines if the driver broke the law (163(3)). |
| सवारी तथा यातायात व्यवस्था ऐन, २०४९ दफा 152 | kept, note completed | Omitted that an uninsured owner must pay the same amount himself. |
| सवारी तथा यातायात व्यवस्था ऐन, २०४९ दफा 166 | ADDED | Owner/manager pays what the driver would owe unless the driver acted negligently or in bad faith. |
| सवारी तथा यातायात व्यवस्था नियमावली, २०५४ नियम 55 | ADDED | Minimum third-party cover (Rs 50 lakh personal injury / Rs 50 lakh property; Rs 5 lakh per death), Rs 25,000 immediate funeral payment, Rs 2 lakh treatment cap, Rs 500/day carer. |
| सवारी तथा यातायात व्यवस्था नियमावली, २०५४ नियम 55ख | ADDED | Owner must file the insurance papers with the CDO immediately after an accident. |
| सवारी तथा यातायात व्यवस्था नियमावली, २०५४ नियम 55ग | ADDED | CDO must have insurance money paid within 21 days (death) or 3 months (other cases). |
| सवारी तथा यातायात व्यवस्था ऐन, २०४९ दफा 172 (limitation) | ADDED (final: limitation citation only, not pinned) | Complaint deadlines: 30 days for other offences; Criminal Code chapter periods for death/maiming. Old playbook gave no limit. |

Other fixes: forum rewritten around the CDO route; next steps updated.

**NEEDS-ADVOCATE-REVIEW**
- Amounts differ between the Act (funeral up to Rs 50,000; Rs 25,000-50,000 for treatment) and the 2054 Rules (Rs 25,000 immediate funeral; Rs 2 lakh treatment). The corpus does not show later amendments, and the insurance figures may have been revised since.
- The Act states no separate deadline to start a compensation claim; a court claim for property damage or amounts above the insurance is not covered by any provision in the corpus.
- Interaction between the CDO route and a separate criminal case against the driver (ss.161-162).

### unpaid_personal_loan - Lent money, not repaid

Status: CHANGED (SERIOUS: told lenders they have 2 years; the Civil Code's lending chapter gives 1 year)

Provisions before -> after: kept 1, removed 2, added 5.  Final pinned list (in order): मुलुकी देवानी संहिता 495; मुलुकी देवानी संहिता 492; मुलुकी देवानी संहिता 474; मुलुकी देवानी संहिता 488; मुलुकी देवानी संहिता 478; मुलुकी देवानी संहिता 476.
Excluded from evidence: मुलुकी देवानी संहिता 520.

| Provision | Action | What was wrong / why |
|---|---|---|
| मुलुकी देवानी संहिता, २०७४ दफा 520 (provision and limitation provision) | REMOVED and EXCLUDED | Section 520 is the limitation clause of the chapter on *contract formation* (2 years for other contracts). Loans have their own chapter (ss.474-492, "लेनदेन व्यवहार") whose limitation section 492 says 1 year. The playbook's limit text ("within 2 years ... don't delay") could make a lender file too late and lose the claim. |
| मुलुकी देवानी संहिता, २०७४ दफा 500 | REMOVED | General damages for non-performance; for money debts the interest rules in the lending chapter (ss.478-481) govern, and s.500 could mislead the AI into promising damages beyond interest. |
| मुलुकी देवानी संहिता, २०७४ दफा 495 | kept, note completed | Correct, added heirs/guarantor liability. |
| मुलुकी देवानी संहिता, २०७४ दफा 492 | ADDED, now limitation provision | 1 year from the end of the period stated in the document, or from the cause of action. No limit for fraud on people lacking capacity, interest on interest or interest above the cap. |
| मुलुकी देवानी संहिता, २०७४ दफा 474 | ADDED | Definition of loan transaction and duty to return. |
| मुलुकी देवानी संहिता, २०७४ दफा 476 | ADDED | Lending should be documented (cheque, receipt, voucher count as documents). |
| मुलुकी देवानी संहिता, २०७४ दफा 488 | ADDED | Court can order repayment on evidence such as bank transfers, cheques, ledgers, but not for private cash transactions above Rs 1 lakh without a document. |
| मुलुकी देवानी संहिता, २०७४ दफा 478, 479 | ADDED (final: only some of these sections are pinned) | Interest only if documented, capped at 10 percent a year (and 10 percent if a rate is not stated). |

**NEEDS-ADVOCATE-REVIEW**
- Whether the lending chapter's 1-year limit (s.492) is the operative one for a purely oral or bank-transfer loan, or whether the 2-year contract limit (s.520) could apply in addition or instead. The playbook now states 1 year as the safe assumption.
- How the 1-year limit runs when no repayment date was agreed (demand-based loans).
- The Rs 1 lakh cash rule in s.488 for an undocumented loan (whether this bars the claim entirely).
- Which District Court has jurisdiction (old forum said "where the borrower resides" - not in the corpus text, removed).

### unpaid_salary - Employer hasn't paid my salary

Status: CHANGED (procedure missing; notes vague)

Provisions before -> after: kept 2, removed 0, added 0.  Final pinned list (in order): श्रम ऐन 34; श्रम ऐन 162.

| Provision | Action | What was wrong / why |
|---|---|---|
| श्रम ऐन, २०७४ दफा 34 | kept, note refined | Added the no-reduction rule. |
| श्रम ऐन, २०७४ दफा 162 (also the limitation provision) | kept, note refined | Correct (6 months from the act). Must stay in the provisions list: `test_playbook_api_endpoints` asserts it. Note now says for unpaid pay count from the date the pay fell due. |
| श्रम ऐन, २०७४ दफा 35 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | When pay must be paid (contract; 3 days for under one month's work; no more than one month apart). |
| श्रम ऐन, २०७४ दफा 113 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | The first step under the Act is a written individual claim to the employer with a receipt; 15 days to discuss. |
| श्रम ऐन, २०७४ दफा 114 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Apply to the Labour Office if the employer does not respond in 7 days or no agreement after 15 days; 21 days of mediation. |
| श्रम ऐन, २०७४ दफा 115 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Labour Office decides in 15 days. |
| श्रम ऐन, २०७४ दफा 163 (2) | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Labour Office can order shortfall plus up to double compensation for unlawful deductions or below-minimum pay, and for unpaid gratuity/provident fund. |
| श्रम ऐन, २०७४ दफा 165 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | 35-day appeal to the Labour Court; Supreme Court from the Labour Court's first-instance decisions (s.161). |

Other fixes: forum and steps reflect the statutory order (employer, Labour Office, Labour Court). Old forum said "unresolved cases go to Labour Court" without the intermediate steps or time limits.

**NEEDS-ADVOCATE-REVIEW**
- Whether the double-compensation power in s.163(2)(क) covers plain non-payment of agreed wages (it names below-minimum pay and unlawful deductions).
- Section 162's 6 months for continuing non-payment: from each missed payday or from the end of employment.
- Section 114 says a claim can be made "15 days after the first application"; the interplay with s.162's 6 months if the employer delays.

### workplace_sexual_harassment - Sexually harassed at work

Status: CHANGED (SERIOUS: no deadlines given, though the Act sets 15-day and 90-day windows; forum named the wrong bodies)

Provisions before -> after: kept 2, removed 1, added 5.  Final pinned list (in order): कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन 5; कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन 7; कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन 4; कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन 6; कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन 14; कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन 12; कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन 16.

| Provision | Action | What was wrong / why |
|---|---|---|
| कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन, २०७१ दफा 5 | kept, note expanded | Old note was accurate but thin; now lists the manager's duties. |
| कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन, २०७१ दफा 7 | kept, note rewritten, now limitation provision | Old note said only "you can file with the workplace, police or another authority". Section 7: complaint to the complaint-hearing authority within 90 days (70 days after the manager fails/decides). |
| कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन, २०७१ दफा 15 | REMOVED | Procedure detail (summary procedure, closed hearing); folded into the s.14 note. |
| कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन, २०७१ दफा 4 | ADDED | Definition of sexual harassment. |
| कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन, २०७१ दफा 6 | ADDED | Complaint to the manager within 15 days; manager decides in 15 days. |
| कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन, २०७१ दफा 14 | ADDED | The complaint-hearing authority is the Chief District Officer (the Chief Secretary for complaints against the CDO). The old forum ("police, or the Labour Office") is not what the Act says. |
| कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन, २०७१ दफा 9 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Protection from retaliation. |
| कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन, २०७१ दफा 12, 13 | ADDED (final: only some of these sections are pinned) | Penalties (6 months / Rs 50,000) and compensation. |
| कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन, २०७१ दफा 16 | ADDED | 35-day appeal to the District Court. |

**NEEDS-ADVOCATE-REVIEW**
- Whether the police route (Criminal Code offences for sexual assault or harassment) remains open after or alongside this Act; s.19 says the Act does not bar prosecution under other law, but the criminal offences are not analysed here.
- How the 15-day, 90-day and 70-day windows interact if a victim does not complain to the manager first; and whether the 90-day period is counted from the last incident in a continuing pattern.
- Whether the Labour Office can also deal with a workplace complaint under Labour Act s.132 (the Labour Act's s.163 list does not name it).

### wrongful_termination - Dismissed without proper notice or process

Status: CHANGED (missed the 35-day Labour Court appeal; notice rule incomplete; core protections missing)

Provisions before -> after: kept 2, removed 0, added 5.  Final pinned list (in order): श्रम ऐन 144; श्रम ऐन 162; श्रम ऐन 139; श्रम ऐन 131 (2); श्रम ऐन 135; श्रम ऐन 148; श्रम ऐन 165.

| Provision | Action | What was wrong / why |
|---|---|---|
| श्रम ऐन, २०७४ दफा 144 | kept, note rewritten | Old note: "at least 1 day ..., longer for longer service". Now the precise 1 / 7 / 30-day periods and the rule that missing notice must be paid for. |
| श्रम ऐन, २०७४ दफा 162 | kept, note refined | Correct 6-month complaint window. |
| श्रम ऐन, २०७४ दफा 165 (now limitation provision) | ADDED | Worker can appeal a termination decision directly to the Labour Court within 35 days of notice (165(2)); internal appeal first if the regulations allow. The old playbook gave only "6 months, Labour Office". |
| श्रम ऐन, २०७४ दफा 139 | ADDED | Employment can end only on legal grounds, with a reasonable and sufficient reason stated. |
| श्रम ऐन, २०७४ दफा 131 (2) | ADDED | This corpus entry holds the dismissal grounds of s.131(4); lesser misconduct gets lesser punishment. |
| श्रम ऐन, २०७४ दफा 135 | ADDED | Employer must give 7 days to explain before punishing misconduct. |
| श्रम ऐन, २०७४ दफा 137 | ADDED, then left unpinned (final: not in the pinned list, to limit evidence crowding) | Employer must begin action within 2 months of learning and decide within 3 months. |
| श्रम ऐन, २०७४ दफा 148 | ADDED | Pay and benefits due within 15 days of termination, otherwise wages continue. |

**NEEDS-ADVOCATE-REVIEW**
- Whether dismissal without following ss.135-137 makes the termination void or only entitles the worker to remedies; the Act leaves the remedy (reinstatement vs compensation) to the deciding body.
- Grounds other than misconduct (incompetence s.142, health s.143, retrenchment s.145) have separate rules not fully pinned here.
- How the 35-day and 6-month routes relate (a worker who appeals to the Labour Court within 35 days versus one who complains to the Labour Office within 6 months).

## All NEEDS-ADVOCATE-REVIEW items (64)

**bonus_not_paid**

- Deadline to complain about unpaid bonus. Bonus Act has none in our corpus; whether Labour Act s.162 (6 months) applies by analogy is unknown. Note now says so honestly.

**cheque_bounce**

- Whether a criminal complaint under s.3क/15 and a civil suit on the cheque (NI Act s.108, 5 years) can run in parallel, and how the two interact.
- Which body/step currently starts the case in practice (police complaint vs. direct application to the government attorney) after Muluki Criminal Procedure Code 2074 applied by s.18.

**child_custody**

- Whether the 6-month limit in s.123 applies to a custody claim, and from what date it runs.
- The Code has no express standalone "custody petition" provision in the corpus; the correct forum/procedure for a custody claim not tied to a divorce petition (District Court vs Child Court under Children Act 2075).
- The "best-interest determination process" referred to in Children Act s.16(3) is "as prescribed" (in rules not in our corpus).

**child_marriage_protection**

- Whether the 3-month limit in Criminal Code s.176 runs from the date of the marriage or from when the reporter learned of it when the marriage is ongoing/continuing.
- Whether the local ward office has any statutory power to stop a marriage (none found in corpus; removed from the playbook).

**citizenship_by_descent**

- The Act names only the "prescribed officer" (तोकिएको अधिकारी) as issuer. District Administration Office is retained from the original playbook and is consistent with s.18, but the citizenship rules are not in the corpus.
- Whether an under-16 can obtain any proof of entitlement in practice (birth registration, recommendation) before turning 16.
- Whether a child of a Nepali mother and foreign father falls under 11(7)/5(2) or, if both parents were citizens, under descent; edge cases (unknown father) are complex.

**consumer_complaint**

- Muluki Civil Code s.430 ("a buyer cannot later claim that purchased property is spoiled or inferior, except for fraud or if it differs from the document") surfaces in search for this issue. It sits in the chapter on transfer of property; how it interacts with the later, special Consumer Protection Act (ss.14, 50) for ordinary goods is unclear. It is not pinned.
- Whether consumer courts under s.41 have actually been constituted in the user's district (the Act leaves it to a Gazette notice); otherwise where a s.50 claim is filed in practice.
- Whether the 6-month period in s.50 runs from the date of harm or knowledge (text says the date the loss was caused).

**cyber_harassment**

- Which deadline governs when the same online conduct fits both the Electronic Transactions Act (90 days from learning) and the Criminal Code (3 months from the act): treat the shorter as binding until an advocate confirms.
- Section 47 of the Electronic Transactions Act is broadly worded and its constitutionality/enforcement scope (esp. for speech) has been contested; confirm current practice with the Cyber Bureau.
- The Privacy Act 2075 s.16/s.29-31 overlap with Criminal Code ss.295-296 (Privacy Act complaints go to District Court within 3 months); which route to prefer is a strategy question for an advocate.

**defamation**

- Whether defamation is prosecuted by the state (Criminal Procedure Code Schedule 1) or on the victim's own complaint (Schedule 2), and hence whether a complaint goes to the police or directly to the District Court. The schedules are not in our corpus.
- How the 3-month period in s.308 works for a continuing publication (e.g., a post that stays online).
- Interaction with online-specific offences (Electronic Transactions Act s.47, 90-day complaint limit) when the defamation is on social media.

**divorce**

- Whether the 3-month limit in s.104 applies to a divorce petition itself or only to ancillary claims (property, expenses). The playbook now says this is unclear.
- Which District Court is "concerned" (territorial jurisdiction) under the civil procedure code.
- Whether the "3 years apart" grounds in ss.94(क)/95(क) interact with the one-year rule in s.98.

**domestic_violence**

- The 90-day limit in s.14 for continuing or repeated violence (counted from which act) and whether it applies to the police-report route under s.5क.
- Penalty for serious bodily/sexual violence is "as per prevailing law" (s.13(1)); the applicable Criminal Code offences should be confirmed for the specific facts.

**fir_not_registered**

- Which offences fall in Schedule 1 vs Schedule 2 of the Criminal Procedure Code (the schedules are not in our corpus); this decides which route applies to the user's complaint.
- Whether the Chief District Officer / Home Ministry route (s.5(4)) applies to the user's offence, or only where a special investigating authority exists.

**foreign_employment_fraud**

- If the s.60 one-year bar does not apply to ss.43-47, which limitation period does apply to a false-promise fraud case (general Criminal Code/Procedure rules not in the playbook)?
- The Department-imposed penalties (ss.51, 55) are inside the 1-year rule: confirm how it is counted for a worker who is still abroad.
- Section 55 has a note in the corpus that the 2082 amendment "is unclear"; confirm the current text.

**inheritance_share**

- Territorial jurisdiction (which District Court) for a partition suit.
- Whether a married daughter's right to a share is affected by s.220's Explanation (घ) "date of marriage" rule and by any agreement (the text says "unless otherwise agreed").
- How the 3-month period in s.235(ख) and the 6-month catch-all in s.235(घ) apply to a person claiming that an earlier partition deed was unfair.

**land_boundary_dispute**

- Which limitation applies to a neighbour's encroachment suit: 6 months (s.298, land occupation chapter), 1 year (s.275, ownership/possession chapter) or none for an ownership declaration. Note now says it is unclear.
- Whether an individual owner can compel a fresh survey ("re-survey") of a single plot; the corpus Survey Act gives no such right (the old forum assumed one). Removed as a promise.
- Whether the Judicial Committee's 35-day rule in LGOA s.47(4) conflicts with the 6-month civil limit.

**maintenance_alimony**

- The playbook is one-sided: ss.99-101 favour a wife; the corpus has no equivalent for a husband claiming maintenance from a wife. Confirm what applies to a husband or unmarried partner.
- Whether the 3-month limit in s.92 (and s.104) applies to continuing non-payment of maintenance, and from what date it runs.
- Child support is covered in the child_custody playbook (Civil Code s.116); confirm the combined claim procedure.

**physical_assault**

- Whether the 1-year limit in s.199 for assault runs from the offence or from discovery for injuries that show up later (e.g., s.192(3) delayed maiming).
- Whether assault (s.191) is a Schedule 1 (state-prosecuted) offence, which decides if the police must register the report under CPC s.4(1); the schedule is not in our corpus. Domestic violence has its own Act (see domestic_violence).

**right_to_information_request**

- Whether an applicant must in practice state a reason (s.7(1) says "कारण खुलाई") given constitutional RTI case law; the corpus text says so, so the playbook repeats it.
- Whether a complaint to the Commission is available directly when the head of the body fails to decide, and s.34's appeal route beyond the Commission (not read into the playbook).

**tenant_eviction_without_notice**

- Section 401 says the landlord "can remove" (हटाउन सक्नेछ) on the listed grounds but does not say how (court order or self-help). The playbook says so and does not state a method. An advocate should confirm that a landlord cannot lawfully lock out or physically remove a tenant without a court or administrative order.
- No notice period is stated in the Code for grounds other than the landlord's own need (s.401(2)); whether the agreement or custom fills the gap.
- Whether the 6-month limit in s.405 or the 35-day limit for the Judicial Committee governs a claim for unlawful eviction.

**theft_complaint**

- Section 246 (pick-pocketing) says items of Rs 10,000 or more are treated as ordinary theft under s.241; whether that value line interacts with the punishment.
- Whether theft is a Schedule 1 offence (state prosecutes); schedule not in corpus.

**traffic_accident_compensation**

- Amounts differ between the Act (funeral up to Rs 50,000; Rs 25,000-50,000 for treatment) and the 2054 Rules (Rs 25,000 immediate funeral; Rs 2 lakh treatment). The corpus does not show later amendments, and the insurance figures may have been revised since.
- The Act states no separate deadline to start a compensation claim; a court claim for property damage or amounts above the insurance is not covered by any provision in the corpus.
- Interaction between the CDO route and a separate criminal case against the driver (ss.161-162).

**unpaid_personal_loan**

- Whether the lending chapter's 1-year limit (s.492) is the operative one for a purely oral or bank-transfer loan, or whether the 2-year contract limit (s.520) could apply in addition or instead. The playbook now states 1 year as the safe assumption.
- How the 1-year limit runs when no repayment date was agreed (demand-based loans).
- The Rs 1 lakh cash rule in s.488 for an undocumented loan (whether this bars the claim entirely).
- Which District Court has jurisdiction (old forum said "where the borrower resides" - not in the corpus text, removed).

**unpaid_salary**

- Whether the double-compensation power in s.163(2)(क) covers plain non-payment of agreed wages (it names below-minimum pay and unlawful deductions).
- Section 162's 6 months for continuing non-payment: from each missed payday or from the end of employment.
- Section 114 says a claim can be made "15 days after the first application"; the interplay with s.162's 6 months if the employer delays.

**workplace_sexual_harassment**

- Whether the police route (Criminal Code offences for sexual assault or harassment) remains open after or alongside this Act; s.19 says the Act does not bar prosecution under other law, but the criminal offences are not analysed here.
- How the 15-day, 90-day and 70-day windows interact if a victim does not complain to the manager first; and whether the 90-day period is counted from the last incident in a continuing pattern.
- Whether the Labour Office can also deal with a workplace complaint under Labour Act s.132 (the Labour Act's s.163 list does not name it).

**wrongful_termination**

- Whether dismissal without following ss.135-137 makes the termination void or only entitles the worker to remedies; the Act leaves the remedy (reinstatement vs compensation) to the deciding body.
- Grounds other than misconduct (incompetence s.142, health s.143, retrenchment s.145) have separate rules not fully pinned here.
- How the 35-day and 6-month routes relate (a worker who appeals to the Labour Court within 35 days versus one who complains to the Labour Office within 6 months).

---

## V2.5 additions (2026-09-30): nine new playbooks and changes to existing ones

Written after the V3 live review found the governing provision in the corpus but not in the answer. Every provision below was read in its original Nepali text in the corpus (`backend/tests/test_v25_routing.py` pins the resolution of each one). None of this has been reviewed by an advocate: **every playbook in this section is NEEDS-ADVOCATE-REVIEW**, and the open questions per playbook are what to ask. As above, forum and step text cites only provisions in the plan (or the ones named in its own text).

### New playbooks (all NEEDS-ADVOCATE-REVIEW)

| Playbook | Status | Pins (Nepali corpus text checked) | What it is for |
|---|---|---|---|
| overtime_working_hours | NEEDS-ADVOCATE-REVIEW | Labour Act ss.28, 29, 30, 31, 113, 162 | Long hours / unpaid overtime: 8 h/day, 48 h/week; overtime at most 4 h/day and 24 h/week; overtime pay is 1.5x basic pay (s.31). |
| bank_loan_penal_interest | NEEDS-ADVOCATE-REVIEW | NRB Unified Directive IPD 15/082 cl.3 (penal rate at most 2 percentage points, on the overdue instalment only, no interest on penal interest); BFI Act s.55(2) [sub-ss.6, 8, 9]; s.57(1); IPD 20/082 cl.9 (complaints desk, NRB portal) | Bank / finance-company loan interest and penal charges. Vetoes the private-lender Civil Code rules (excludes ss.478, 481). |
| bank_account_charges_complaint | NEEDS-ADVOCATE-REVIEW | NRB Unified Directive IPD 20/082 cl.6 (no deduction because the balance is below the minimum; listed free services); cl.9 (complaints desk, hotline, NRB portal) | Money deducted from an account, service charges, a bank that ignores a complaint. |
| loan_interest_dispute | NEEDS-ADVOCATE-REVIEW | Civil Code ss.479, 478, 480, 481, 482 (limitation: s.492) | A private lender's interest: none if the document is silent (s.479), 10% cap (s.478), no interest on interest (s.480), not above principal (s.481). |
| bail_release_after_arrest | NEEDS-ADVOCATE-REVIEW | Criminal Procedure Code ss.68, 67, 71, 75, 76 | Release on deposit / guarantee / bank guarantee (s.68) versus custody (s.67). |
| dowry_harassment | NEEDS-ADVOCATE-REVIEW | Criminal Code ss.174, 176 (3-month complaint limit); Domestic Violence Act ss.4(1), 6 | Dowry demands and harassment after marriage. |
| company_registration_shareholders | NEEDS-ADVOCATE-REVIEW | Companies Act ss.9 (private company at most 101 shareholders; public at least 7), 5 (certificate within 7 days) | Registering a private company. |
| agm_not_held | NEEDS-ADVOCATE-REVIEW | Companies Act ss.76, 77 | A public company that has not held its AGM: Registrar's direction, then a shareholder's court application. |
| medical_negligence_death | NEEDS-ADVOCATE-REVIEW | Criminal Code ss.181, 195 (limitation: s.187); Criminal Procedure Code s.4(1) (forum text also cites s.5) | Death or injury by negligent treatment. Criminal route only; the Code has no doctor-specific section. |

Open questions for the advocate (one line each, all new plans):

- **overtime_working_hours** - Whether a monthly-salaried worker is owed s.31 pay for hours beyond s.28 where the contract says "long hours"; how s.162's 6 months runs for overtime accrued over many months; whether the s.31(2) managerial exemption applies to the asker.
- **bank_loan_penal_interest** - IPD 15/082 cl.3 is a regulator directive, not a statute: whether a court would enforce the 2-point cap against a loan agreement signed earlier; which shard of the NRB directive (the corpus holds the "क, ख, ग", "घ" and infrastructure-bank circulars) binds which class of institution; the interplay with the Bank and Financial Institutions Act s.57 recovery powers.
- **bank_account_charges_complaint** - Whether NRB's complaint portal can order a refund or only supervises the bank; whether cl.6(ga) applies to all licensed classes; the deduction rules for dormant accounts and card fees beyond cl.6.
- **loan_interest_dispute** - s.479 was inserted by the 2080 amendment: whether it applies to loans made before that date; how s.479 (no interest without a written mention) interacts with the deemed 10% of s.478(3) when a document says "interest" without a rate.
- **bail_release_after_arrest** - Schedules 1 and 2 (which offences are custody offences under s.67) are not in the corpus; whether police-stage release (before a court case) is governed by other provisions not in this plan.
- **dowry_harassment** - Whether the 3-month limit of s.176 applies to continuing harassment and from which act it runs; when a complaint of the s.174(3) offence is also a Domestic Violence Act matter.
- **company_registration_shareholders** - Whether the 7-day period runs from a complete application or from any filing; the minimum shareholder count for a private company (the Act sets only a ceiling).
- **agm_not_held** - Whether a shareholder can go to the Registrar's Office before the 3-month wait, and what "other suitable order" the court may make under s.76(3).
- **medical_negligence_death** - Whether negligent medical treatment is prosecuted under s.181 in practice, whether s.181 is a Schedule 1 offence (CrPC s.4), and the civil-compensation route, which this plan does not cover.

### Existing playbooks changed in V2.5

| Playbook | Change | NEEDS-ADVOCATE-REVIEW question |
|---|---|---|
| deposit_not_returned | Civil Code s.400 is no longer excluded; it is pinned with a note that it covers only a tenant who leaves early without the 35-day notice (landlord may deduct that period's rent from any *advance*). The V3 review and the eval set treat s.400(3) as governing the question; the earlier audit excluded it because its notice rule had been misapplied. `not_keywords` (bank, cooperative) keep bank/cooperative deposits out. | Whether s.400(3)'s "advance" (अग्रिम) is the same thing as a tenancy deposit (धरौटी) in ordinary usage. |
| inheritance_share | Added Civil Code s.214 (widow may take her share and live apart) and s.216 (partition deed); keywords for widows, intestate succession and the spelling "अन्श". | Whether a widow living in a joint household can compel partition against in-laws under s.214 alone. |
| child_custody | Keywords for "custody", "who gets custody", "lose my child" (a custody question that also mentioned divorce was routed to the divorce plan and never saw s.115). | - |
| foreign_employment_fraud | Added ss.60 and 55 to the pinned list; keywords for "no job on arrival / returned home". | Whether s.36 compensation is available when the worker returned home before the Department complaint. |
| right_to_information_request | Added s.10 (35-day appeal, 60-day decision); misspelled "suchanako hak" variants. | - |
| consumer_complaint | Added E-Commerce Act 2081 s.10 (return of goods not matching the seller's description); online-order keywords; bank complaints are vetoed (they go to the bank's complaints desk and NRB). | Whether E-Commerce Act s.10 applies to marketplaces that are not the seller. |
| unpaid_personal_loan | `not_keywords`: bank, finance company, microfinance. | - |
| wrongful_termination | Devanagari inflections ("कामबाट निकाल्यो" ...). | - |

## V2.6 additions (2026-10-01): three new playbooks and changes to existing ones

Provisions read in the corpus text (`Index.section`), resolved by `tests/test_playbooks.py`. All NEEDS-ADVOCATE-REVIEW.

| Playbook | Status | Provisions | Covers |
|---|---|---|---|
| maternity_leave | NEEDS-ADVOCATE-REVIEW | Labour Act ss.45, 162 | 14 weeks' leave, 60 days' full pay, doctor's extra month, 15 days' paternity-care leave; complaint within 6 months. |
| salary_tax_withholding | NEEDS-ADVOCATE-REVIEW | Income Tax Act s.87 | Employer's duty to withhold at the Schedule 1 rates. The percentages are NOT in s.87 (the plan says so); Schedule 1 is not in the corpus passage. |
| company_annual_return_late | NEEDS-ADVOCATE-REVIEW | Companies Act ss.80, 81(1), 81(2) | Filing deadlines and the fine table by months late and paid-up capital; the 90% concession for returns filed by Asar 2082. |

- **Open questions:** maternity_leave - whether the 14 weeks include the 6 compulsory weeks and how the 60 paid days count against them (s.45(1)-(3)); salary_tax_withholding - the current Schedule 1 slabs (the Finance Act changes them yearly) and whether the 2058 Act title or the "आर्थिक ऐन, २०८२ ले गरेको संशोधन सहित" copy is authoritative; company_annual_return_late - whether the s.81(2) fine is per director or per company, and whether the 2082 concession has lapsed.

| Existing playbook | Change | NEEDS-ADVOCATE-REVIEW question |
|---|---|---|
| wrongful_termination | + Labour Act s.53 (gratuity, 8.33% of basic pay into the Social Security Fund; the note says the text does not state when it may be drawn); keywords for "dismissed without a reason" | Whether gratuity is payable on dismissal for misconduct (the section text names no condition). |
| inheritance_share | Civil Code s.205 (son, daughter, spouse, parents are अंशियार) moved to the front of the provision list so the plan's pin limit keeps it | none new |
