# Evidence and ordering checklist

Use this as a common baseline. The exact policy, current claim form, insurer/TPA request, and live portal override it.

## 1. Administrative and payment identity

Check whether the current claim route requires:

- claimant-completed, dated, and signed Claim Form Part A;
- hospital-completed, signed, and sealed Part B or equivalent;
- claim intimation/registration reference;
- covering letter or schedule of expenses when the current route requests one;
- policy schedule, health card, or current coverage proof;
- patient photo ID and policyholder/proposer KYC or CKYC;
- PAN or other threshold-specific KYC;
- NEFT form and personalized cancelled cheque, bank passbook first page, or accepted bank statement;
- other-insurer settlement advice and certified copies when originals were submitted elsewhere;
- original/photocopy classification and a truthful photocopy reason when the portal asks for it.

Never fill a hospital-only declaration or missing clinical fact. A typed form entry must come from a confirmed source. Adding a signature requires the signer's explicit approval.
Never write, stamp, or annotate an original or its scan merely because another insurer's special route asks for such wording. Do so only when the exact current route requires it and the claimant authorizes it; keep the untouched source separately.

## 2. Hospitalization or day-care core

Common evidence includes:

- first consultation and admission advice;
- treating doctor's diagnosis/onset certificate or physician statement when required;
- discharge/day-care/transfer summary;
- final hospital bill and detailed itemized breakup;
- deposit, final-payment, refund, and other payment receipts;
- inpatient prescriptions and pharmacy bills;
- investigation requests and complete reports;
- consultation notes, indoor case papers, nursing charts, or treatment records when required;
- hospital registration/facility proof for a non-network hospital when required.

For surgery or an implant, check for operation notes/surgeon certificate, implant invoice, payment receipt, sticker/barcode/serial label, and relevant pre-operative records.

## 3. Pre- and post-hospitalization expense chains

Create one expense record for each financial event. Link all evidence to that expense ID.

Match using the visible insured-patient name, provider, service date, invoice/receipt number, item or test description, and amount. A filename or nearby page order is not enough. When more than one bill could match, keep the evidence unlinked and ask the claimant to point to the exact source file/page; do not choose silently. The audit should identify the financial event and say exactly which role is missing.

| Expense | Required chain |
|---|---|
| Consultation | Consultation note or prescription -> itemized bill -> payment proof |
| Diagnostic test | Doctor advice/referral -> complete report/result -> itemized bill -> payment proof |
| Medicine | Matching prescription -> itemized pharmacy bill -> payment proof |
| Ambulance | Medical/route support when the policy requires it -> invoice -> payment proof |
| Implant | Clinical/operative context -> invoice -> payment proof -> implant identity label |

The same page may satisfy more than one evidence role, such as a paid invoice satisfying both `invoice` and `payment_proof`. Do not count it twice.

For each chain, visually confirm:

- the insured patient's name;
- the same illness/treatment and hospitalization episode;
- practitioner/provider identity;
- date within the policy's configured window;
- prescription/advice before the service or medicine;
- bill/invoice number and item description;
- paid status and payment receipt;
- report continuity and all substantive pages;
- no unsupported mixed invoice lines included in the requested amount.

## 4. Conditional branches

Ask explicitly; do not infer these from filenames:

- Accident/medico-legal: first consultation, incident statement, MLC/accident register, FIR/police papers, intoxication history or test when asked.
- Death: death summary/certificate, nominee identity and bank proof, legal-heir/succession/NOC documents as required.
- Maternity/newborn: obstetric history, sonography, birth papers, and policy-specific records.
- Other insurer/co-pay/deductible: settlement letter, certified document copies, and a clear allocation of gross, other-insurer-paid, claimant-paid, excluded, and requested amounts.
- Non-network hospital: registration number/certificate and facility/bed information when requested.
- Late filing: a claimant-approved factual explanation only. Never manufacture a reason.
- Physical-only evidence: retain imaging films, wet-signed originals, and any item the insurer says cannot be replaced by a scan.

## 5. Bill-by-bill reconciliation

Use decimal arithmetic. Keep at least these fields:

| Field | Purpose |
|---|---|
| Expense ID | Stable link between evidence pages and the amount |
| Phase | Hospitalization, pre, post, or other |
| Date | Service/invoice date |
| Issuer | Hospital, doctor, pharmacy, or diagnostic center |
| Invoice number | Duplicate-event check and claim-form bill register |
| Description | What was supplied or performed |
| Billed amount | Gross supported invoice amount |
| Claimed amount | Amount requested once |
| Not-claimed reason | Unsupported line, deductible, co-pay, other insurer, unrelated item, or claimant choice |

Require all of the following:

- `sum(expense.claim_amount) == case.claimed_amount`;
- each expense is counted once, even when it has multiple receipts/pages;
- hospitalization, pre, post, and other subtotals independently match the claim form/portal;
- every partial claim has an explicit, truthful reason for the difference;
- repeated issuer + invoice number + date + amount combinations are investigated;
- claim form, bill register, cover/index, upload inventory, and portal breakdown use the same final figures.

## 6. Recommended document order

Keep the canonical master order in the manifest. A useful default is:

1. Claim form and claim reference.
2. Identity/KYC and bank proof.
3. Policy/health card evidence required for this route.
4. Hospital Part B and non-network registration, if applicable.
5. Admission advice and hospitalization clinical records.
6. Discharge summary, operation/implant evidence, final bill/breakup, and payment receipts.
7. Pre-hospitalization chains in chronological order.
8. Post-hospitalization chains in chronological order.
9. Conditional records and insurer correspondence.

Within each phase, keep each prescription/advice -> report/service -> bill -> receipt chain contiguous. Keep multi-page reports together.

Upload bundles must follow the live portal categories. A common fallback split is:

- `01-claim-form-bank`
- `02-hospitalization-core`
- `03-hospital-bills-receipts`
- `04-pre-hospitalization`
- `05-post-hospitalization`
- `06-conditional-other`

This phase-based fallback avoids uploading the same prescription/report/bill in both a document-type pack and a phase pack. If the live portal instead has document-type slots, replace these IDs with an explicit portal mapping. Do not add an audit cover to a portal category unless current instructions ask for one. Do not split a substantive report or expense chain merely to hit an arbitrary target; split on document boundaries and verify the actual portal limit first.
