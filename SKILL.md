---
name: indian-health-insurance-claim-help
description: Audit, organize, and create PDF packets for hospitalization-linked Indian health-insurance indemnity reimbursement claims, including day-care and pre/post-hospitalization evidence. Use for claim-document preparation or QA; not for standalone OPD, fixed-benefit claims, eligibility decisions, or promising approval.
---

# Indian Health Insurance Claim Help

Prepare a truthful, readable, traceable evidence packet. Improve completeness and reviewer usability without implying that formatting can guarantee claim acceptance.

## Establish the authority first

Before arranging documents, confirm this is a hospitalization/day-care-linked indemnity reimbursement. Standalone OPD, fixed-benefit, cashless authorization, critical-illness lump-sum, and similar claim types need their own current product instructions instead of this default evidence model.

Identify the insurer, exact product name and UIN, policy/schedule, TPA, claim type, admission/discharge dates, main claim reference when applicable, and submission channel.

- Prefer the current policy wording, customer information sheet, live insurer/TPA portal, and current official claim form over generic guidance.
- Record official URLs, the date checked, exact portal screen/journey, documented upload categories, formats, and size limits in the manifest.
- Never hard-code a pre/post coverage window or filing deadline across products. If sources conflict, flag the conflict and use the safer earlier date while the claimant confirms.
- Read [references/insurer-sources.md](references/insurer-sources.md) when researching an insurer. It is a source map, not a substitute for the claimant's policy.

## Protect originals and private data

- Work locally unless the claimant explicitly authorizes another service. Medical, identity, bank, policy, and claim records are highly sensitive.
- Preserve every source byte-for-byte. Build only from copies and record SHA-256 hashes.
- Never invent, rewrite, hide, crop away, or "correct" medical or financial evidence.
- Never add insurer-specific wording, a stamp, or an annotation to source evidence unless the exact current route requires it and the claimant authorizes it; preserve the untouched source.
- Do not fill hospital-only fields, add a signature, create a factual explanation, or submit a claim without explicit authorization. Unknown facts stay unresolved.
- Keep highlights, annotations, and audit covers in `REVIEW_ONLY`; submit untouched evidence pages in `SUBMIT` unless the live insurer instructions require otherwise.

## Workflow

Run these helpers from the skill repository root with Python 3.11 or newer. If the PDF runtime is not installed, run `python3 -m pip install -r requirements.txt` first; install Poppler (`brew install poppler` on macOS or `sudo apt-get install poppler-utils` on Ubuntu/Debian) for rendered visual QA.

1. Create a private case workspace:

   ```bash
   python3 scripts/new_claim_case.py /absolute/path/to/private-case
   ```

2. Inventory every file and page. Classify by visible content, not filename. Render image-only scans and use OCR only to locate information; visually verify the original page.
3. Fill `claim-manifest.json`. Read [references/manifest.md](references/manifest.md) before editing it.
   Keep copied evidence under the private case directory and set `rules.source_roots` (normally `["input"]`) so every source file must be explicitly included or excluded.
   Use `delivery_mode: standalone` for a digitally signed or interactive-form PDF so the clean output remains byte-for-byte identical.
4. Reconcile every requested expense using [references/document-checklist.md](references/document-checklist.md). A bill and its receipt describe one expense, not two. Match prescription/advice, report, bill, and receipt to one stable expense ID using visible patient/provider, date, invoice number, item/service, and amount. Never guess from a filename alone. If a match is ambiguous, leave it unlinked and ask the claimant to identify the exact source file and page. If a required item is absent, name the expense and ask for that exact report, bill, or receipt.
5. Audit before building:

   ```bash
   python3 scripts/claim_packet.py audit \
     --manifest /absolute/path/to/private-case/claim-manifest.json \
     --output-dir /absolute/path/to/private-case/output
   ```

6. Resolve every blocker and every unexplained warning. Then build:

   ```bash
   python3 scripts/claim_packet.py build \
     --manifest /absolute/path/to/private-case/claim-manifest.json \
     --output-dir /absolute/path/to/private-case/output
   ```

   The master packet is for review. Clean category PDFs contain no generated cover. They go to `SUBMIT` only when recorded portal/policy gates have no unresolved warning other than visual QA; otherwise they go to `CANDIDATE_UPLOADS`.

7. Render and inspect every final page:

   ```bash
   scripts/render_packet.sh /absolute/path/to/file.pdf /absolute/path/to/renders
   ```

   The CLI deliberately retains `VISUAL_QA_PENDING`; it cannot see a rendered page as a human does. Record the completed page-by-page check and claimant approval in the private submission receipt before calling the packet ready to upload.

8. Apply the final gates in [references/qa-submission.md](references/qa-submission.md). Present the claimant with the bill ledger, exclusions, and exact upload inventory before any submission.

## Evidence rule for pre/post claims

For each requested expense, keep the evidence chain together:

- Consultation: clinical note or prescription -> bill -> payment proof.
- Diagnostic test: doctor advice/referral -> report/result -> bill -> payment proof.
- Medicine: matching prescription -> itemized pharmacy bill -> payment proof.
- Implant: clinical/operative context -> invoice -> payment proof -> label/sticker when required.

Tie every chain to the same insured patient, episode, diagnosis/treatment, and covered hospitalization. Exclude unsupported lines from the requested amount and disclose the reason in the manifest.

The audit's `Evidence matching` section shows, for every expense, the specific visible test/medicine/consultation description, exact provider/date/invoice/amount, every linked source file and page, and any missing evidence. It should say, for example, `itemized bill or invoice for Lipid profile (cholesterol test)`, not merely `invoice missing`. A diagnostic prescription without its report, a receipt without its itemized bill, or a bill without payment proof blocks readiness. A medicine prescription does not create a report requirement unless a diagnostic test is also being claimed.

## Ready-to-submit claim

Do not call a packet ready until:

- the exact policy/UIN and live submission route were checked;
- every claimed expense has the required evidence roles;
- the manifest total, claim form, bill register, and portal breakdown agree;
- every included source page appears exactly once in the master packet and every omission has a reason;
- the clean upload PDFs reopen, are unencrypted, fit the confirmed portal limits, and pass page-by-page visual review;
- originals and any physical-only evidence remain available; and
- the claimant has approved the final inventory and any form entries.

After submission, record the confirmation reference, timestamp, files uploaded, local unique-file count, portal-displayed document count, and follow-up instructions. Keep those counts separate because portals may generate their own document.
