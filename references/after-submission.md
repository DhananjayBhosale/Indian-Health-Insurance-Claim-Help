# Intimation, deductions, queries, rejection, and complaints

Last checked: 2026-10-19. Rules change; confirm against the current circulars below and the claimant's policy wording before relying on a date or limit.

Sources:

- [HMC] [Master Circular on Health Insurance Business, 29 May 2024](https://irdai.gov.in/document-detail?documentId=4942918)
- [PMC] [Master Circular on Protection of Policyholders' Interests, 5 September 2024](https://irdai.gov.in/document-detail?documentId=5625747)
- [IOR] [Insurance Ombudsman Rules 2017, as amended to 9 November 2023](https://cioins.co.in/OmbudsmanRules2017)

Pages that still say "30 days, or 45 with investigation" quote the repealed 2016 health and 2017 policyholder regulations. Do not use them.

## Intimation

- There is no single legal deadline. The PMC asks for intimation "at the earliest possible time"; the policy sets any period (often 24 hours after an emergency admission or 48 hours before a planned one).
- A claim must not be rejected or closed for late intimation or for missing documents (PMC Part B, Ch. V, 1(ii)). If the claimant has not intimated, ask them to do it now through the insurer's app, website, or toll-free number, and record the intimation number as `case.claim_reference`.
- Filing deadlines for the claim documents are still policy-specific. Use the earlier date when sources conflict. If a deadline has passed, any explanation must be the claimant's own facts; never write a reason for them.

## Cashless or reimbursement

- At a network hospital, cashless is usually simpler. The insurer must decide a cashless request within 1 hour and the final discharge authorization within 3 hours of the hospital's request (HMC 15(b) and 16; PMC Part B, Ch. V, 3(i)).
- If cashless is refused or only partly approved, ask for the decision in writing and keep it with the reimbursement claim.
- Pre- and post-hospitalization bills after a cashless stay are usually a separate reimbursement claim linked to the main claim number (`claim_route: supplementary_pre_post`, `main_claim_reference`).
- With more than one indemnity policy, the claimant chooses which policy to claim under first; that insurer coordinates any balance with the others (HMC 18).

## Expected deductions

The requested amount and the payable amount often differ. Never predict the payable amount; list the clauses that may apply so the claimant is not surprised:

- items the policy lists as non-payable (many consumables) unless an add-on covers them;
- room-rent or ICU limits. Above the limit, many policies cut related charges in proportion. IRDAI's 2020 product norms kept pharmacy, consumables, implants, medical devices, and diagnostics out of proportionate cuts; check whether the policy wording repeats this, because that circular has since been superseded;
- co-pay, deductible, and sub-limits such as a per-eye cataract limit;
- "reasonable and customary" charge limits, exclusions, and waiting periods.

## Answering a query

- List every point in the query. Reply once, covering all of them, quoting the claim number and query reference, before the stated deadline. Keep the reply and its acknowledgement.
- Records the hospital holds are for the insurer or TPA to collect (HMC 17(c)). If asked for one, say so politely and give the hospital's details, while still sending anything the claimant holds.
- If a requested document does not exist, say so factually. Never create one.
- Build any new upload set in a fresh output directory and record it in the submission receipt.

## Settlement

- A reimbursement claim must be settled within 15 days from submission of the claim (PMC Part B, Ch. V, 3(iii)(6)). If payment is late, the insurer must add interest at 2% above the bank rate, counted from the date it received the claim intimation until the date of payment, without being asked (PMC Part B, Ch. V, 2(ii)). Record the intimation, submission, and acknowledgement dates.

### Settlement check

When the settlement letter arrives, compare it with the bill ledger, one row per ledger line:

| Ledger line | Claimed | Approved | Deducted | Clause cited | Evidence |
| --- | --- | --- | --- | --- | --- |
| Pre: lipid profile, 2026-01-08 | ₹1,200 | ₹1,000 | ₹200 | "Section 4.2 sub-limit" | lab bill p.1, receipt p.1 |

- Totals: claimed minus approved must equal the total deducted. If the letter's figures do not add up, ask the insurer in writing to explain the difference.
- Interest: if payment came more than 15 days after submission, check that the letter adds interest from the intimation date; if not, ask for it (PMC Part B, Ch. V, 2(ii)).
- A deduction with no specific clause cited does not meet HMC 17(b). List it as a point for the grievance or complaint.
- Never tell the claimant what the insurer should have paid. Point out only what the letter leaves unexplained, and quote the policy text for each clause it cites.

## Rejection or partial payment

- A rejection must be approved by the insurer's Claims Review Committee (HMC 17(a)).
- The letter must give full reasons with reference to the specific policy terms (HMC 17(b)). If it does not, ask for them in writing.
- Neither late intimation nor missing documents is a valid reason to reject or close a claim (PMC Part B, Ch. V, 1(ii)).

## Complaint ladder

1. **Insurer.** Write to the insurer's grievance officer and keep the complaint number. The insurer must acknowledge it at once and resolve it within 14 days, giving reasons with reference to the policy terms (PMC Part B, Ch. VI, 2(i)).
2. **IRDAI Bima Bharosa.** Register at [bimabharosa.irdai.gov.in](https://bimabharosa.irdai.gov.in) or call 155255 or 1800 4254 732.
3. **Insurance Ombudsman.** Free. File online at [cioins.co.in](https://cioins.co.in/Complaint/Online) after the insurer rejects the written complaint, does not reply within one month, or replies unsatisfactorily. File within one year of that reply or of the one-month mark. Awards are capped at ₹50 lakh. The Ombudsman will not take a matter already before a court, consumer commission, or arbitrator (IOR 14 and 17).
4. **Consumer commission.** Generally within 2 years of the cause of action; the District Commission's ₹50 lakh limit counts the consideration paid (the premium), not the claim amount; how courts apply this to insurance is not settled, so check the current position before filing. Choose this or the Ombudsman, not both.

## Complaint letter outline

Use only facts the claimant confirms:

- policyholder, patient, policy number, and claim number;
- admission and discharge dates, hospital, amount claimed, amount paid, and the date of the insurer's letter;
- each disputed rejection or deduction, with the clause the insurer cited and why the claimant disagrees, referring to the attached evidence;
- the request: reconsider the claim, or explain each deduction with the specific clause;
- attachments: the insurer's letter, the ledger, and the relevant bills, reports, and receipts.

The claimant reviews, signs, and sends it.
