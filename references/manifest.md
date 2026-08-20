# Claim manifest

The manifest is the single source of truth for ordering, amount reconciliation, evidence links, exclusions, and upload bundles. It is private and must not be committed.

Start from [../assets/claim-manifest.example.json](../assets/claim-manifest.example.json). Paths are resolved relative to the manifest file.

Keep the CLI output directory inside that same private case directory, normally `<case>/output`. The helper refuses the case root itself and every external/broad output path before changing permissions or writing.

## Top-level sections

- `schema_version`: currently `1`.
- `case`: case ID, insurer/product/UIN, patient, policy/main-claim references, claim type/route, submission channel, dates, currency, and requested total.
- `verification`: official source URLs, TPA, checked date, covered pre/post date bounds, filing deadlines, accepted file types/limits, and whether live portal rules were confirmed.
- `conditions`: case-specific branches such as surgery, implant, accident, death, non-network hospital, other insurer, ambulance, or maternity.
- `rules`: private source roots, verified required roles, and upload limits.
- `expenses`: one row per financial event.
- `documents`: ordered source/page selections and their evidence links.

## Claim route and verification fields

Record enough detail to reproduce a readiness decision:

- `case.claim_type`: for this skill, normally `hospitalization_reimbursement` or `day_care_reimbursement`.
- `case.claim_route`: for example `main_with_pre_and_post`, `main_only`, or `supplementary_pre_post`.
- `case.main_claim_reference`: required when pre/post documents attach to an existing main claim.
- `case.submission_channel`: authenticated portal, TPA portal, app, email, branch, or courier route actually used.
- `verification.coverage_window`: exact `pre_start`, `pre_end`, `post_start`, and `post_end` dates plus the policy authority URL.
- `verification.filing_deadlines`: main/pre and post due dates plus the authority URL. These are different from the regulator's settlement turnaround time.
- `verification.portal`: exact rule scope, accepted file types, per-file limit, total limit, file-count limit, explicitly unpublished rules, and authority URL.

`verification.portal.rule_scope` names the exact journey or screen that was checked, for example `initial reimbursement upload`, `supplementary pre/post claim`, or `additional documents for claim ABC`. Do not copy a limit from an additional-document/query screen into the initial-claim route, or from an insurer portal into a TPA/app/email route. If `portal_rules_confirmed` is true, this scope must be non-empty.

Use `null` for a rule that is genuinely unavailable. When the live route was checked and a limit is genuinely not published, also list that field in `portal.unpublished_rules`; otherwise keep `portal_rules_confirmed` false. Do not turn an unknown rule into a guessed number.

## Money and dates

- Store money as quoted decimal strings, for example `"1250.50"`.
- Use ISO dates: `YYYY-MM-DD`.
- `case.claimed_amount` must equal the sum of `expenses[].claim_amount`.
- `claim_amount` cannot exceed `billed_amount`.
- If the two differ, explain the non-claimed portion in `not_claimed_reason`.

## Expense fields

Required fields are:

- `id`: unique stable ID such as `pre-diagnostic-001`.
- `phase`: `pre`, `hospitalization`, `post`, or `other`.
- `kind`: `consultation`, `diagnostic`, `medicine`, `hospital`, `implant`, `ambulance`, or `other`.
- `date`, `issuer`, `invoice_number`, and `description`. Make `description` the specific visible service or item, such as `Lipid profile (cholesterol test)`, rather than a generic `diagnostic test`. Do not infer a diagnosis or expand an abbreviation unless the supplied evidence supports it.
- `billed_amount`, `claim_amount`, and `not_claimed_reason`.

For `kind: other`, provide `required_roles` so the audit knows the evidence chain.

## Document fields

- `id`: unique page/document ID.
- `path`: PDF or JPG/JPEG/PNG/TIF/TIFF source path.
- `pages`: PDF page selection such as `"1-3,5"`; use `null` for all pages.
- `phase`: `administrative`, `pre`, `hospitalization`, `post`, or `other`.
- `document_type`: short human-readable classification.
- `date`: document/service date when applicable.
- `expense_ids`: expenses this evidence supports.
- `evidence_roles`: machine-checkable roles.
- `packs`: output upload categories. One document may appear in multiple packs when the portal requires it, while appearing once in the master.
- `delivery_mode`: `assemble` by default, or `standalone` for a digitally signed or interactive-form PDF that must be copied byte-for-byte. A standalone PDF must use all pages and map to exactly one pack.
- `decision`: `include` or `exclude`.
- `exclusion_reason`: mandatory when excluded.
- `original_status`: for example `scan_of_original`, `digital_original`, `certified_copy`, or `photocopy`.
- `expected_sha256`: optional pin. Once reviewed, set this to detect later source replacement.
- `notes`: concise factual caveats; do not paste unnecessary medical details.

Set `rules.source_roots` to every private input directory, normally `["input"]`. Each root must be a strict descendant of the manifest's private case directory. Every supported PDF/JPG/JPEG/PNG/TIF/TIFF file under those roots must have an explicit include or exclude row. This catches files that were copied into the case but accidentally left out of the manifest. Source files outside those roots are blocked and are not inspected.

## Evidence roles

Use only roles the audit can reason about:

- `claim_form`
- `identity`
- `bank`
- `policy`
- `hospital_form`
- `hospital_registration`
- `discharge`
- `clinical_advice`
- `clinical_record`
- `clinical_result`
- `invoice`
- `payment_proof`
- `operation_record`
- `implant_identity`
- `accident_record`
- `death_record`
- `claimant_authority`
- `other_insurer_settlement`
- `maternity_record`
- `other`

A paid itemized invoice can carry both `invoice` and `payment_proof`. A prescription for a diagnostic test can carry `clinical_advice`; the test report carries `clinical_result`.

All documents belonging to one financial event use the same `expense_ids` value. The audit then prints the provider, date, invoice number, amount, linked source file/page, and any missing evidence. Do not link ambiguous candidates merely to clear a blocker; ask the claimant to identify the exact bill, receipt, prescription, or report.

## Rules and status

Set `rules.required_case_roles` from the exact current checklist, not from guesswork. Define every pack in `rules.pack_definitions` with a stable ID, portal-facing label, and optional pack-specific limit. Every `documents[].packs` value must match one of these IDs.

Use `verification.portal.max_file_mb` or a pack-specific `max_file_mb` only when an official source or authenticated live portal confirms it for the recorded `rule_scope`. `compatibility_target_mb` is a non-authoritative warning target. Also record any confirmed total-size and upload-count limits and the screen to which they apply.

If `verification.portal_rules_confirmed` is false, the audit must remain `PORTAL_RULES_UNVERIFIED` even if the evidence packet builds. That output is suitable for review, not a ready-to-upload claim.

## Page coverage

- Select each included source page once in the master packet.
- If a large source scan contains multiple document types, create separate manifest document rows with non-overlapping page ranges.
- Exclude blank, duplicate, unrelated-person, unrelated-episode, and unsupported pages explicitly; never silently omit them.
- A digitally signed or interactive-form PDF must use `delivery_mode: standalone`. The builder copies that upload file byte-for-byte and uses a reserialized copy only inside the clearly marked review master.
