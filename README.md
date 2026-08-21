# Indian Health Insurance Claim Help

Audit and assemble hospitalization, pre-hospitalization, and post-hospitalization claim PDFs without changing the original evidence.

[![Tests](https://github.com/DhananjayBhosale/Indian-Health-Insurance-Claim-Help/actions/workflows/test.yml/badge.svg)](https://github.com/DhananjayBhosale/Indian-Health-Insurance-Claim-Help/actions/workflows/test.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-0f766e.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-0f766e.svg)](https://www.python.org/)

Works with any capable AI model or assistant that can read local files and follow [`SKILL.md`](SKILL.md). No model-specific API is required.

> [!IMPORTANT]
> Better preparation improves completeness, not eligibility. The policy, deadlines, originals, treatment linkage, and insurer assessment still decide the claim.

## What it does

- Checks the exact insurer, product, UIN, TPA, policy window, deadline, and live submission route.
- Matches each prescription or advice, report, itemized bill, and payment receipt to one expense.
- Names the exact missing evidence and points to known source files and pages.
- Finds duplicate expenses, total mismatches, unsupported lines, missing pages, and portal-limit problems.
- Builds separate review and upload-ready PDF candidates while preserving source files and hashes.

## Quick start

```bash
git clone https://github.com/DhananjayBhosale/Indian-Health-Insurance-Claim-Help.git
cd Indian-Health-Insurance-Claim-Help
python3 -m pip install -r requirements.txt
```

Give your AI assistant access to this repository and a private folder containing the claim documents. Then ask:

```text
Read SKILL.md and audit my Indian health-insurance reimbursement documents.
First show me missing evidence and the bill-by-bill reconciliation.
Then create separate hospitalization, pre-hospitalization, and
post-hospitalization PDF candidates. Do not upload anything.
```

Codex users can install the repository at `~/.codex/skills/indian-health-insurance-claim-help` and invoke `$indian-health-insurance-claim-help`. Other assistants can read `SKILL.md` directly.

## Exact evidence matching

The audit uses the visible service name, not a generic error. For example:

```text
Lipid profile (cholesterol test)
Found: prescription.pdf page 2; lab-report.pdf pages 1-2
Missing: itemized bill for Lipid profile (cholesterol test)
Action: add the bill, or identify its exact file and page.
```

Ambiguous matches stay unresolved. The tool never invents a diagnosis, invoice, amount, signature, explanation, or paid status.

## Run manually

From the repository root:

```bash
python3 scripts/new_claim_case.py /absolute/path/to/private-case
python3 scripts/claim_packet.py audit --manifest /absolute/path/to/private-case/claim-manifest.json --output-dir /absolute/path/to/private-case/output
python3 scripts/claim_packet.py build --manifest /absolute/path/to/private-case/claim-manifest.json --output-dir /absolute/path/to/private-case/output
```

Install Poppler and run `scripts/render_packet.sh` for page-by-page visual QA before uploading any PDF.

## Outputs

- `REVIEW_ONLY/`: indexed master packet for human review.
- `SUBMIT/`: clean category PDFs after recorded checks pass.
- `CANDIDATE_UPLOADS/`: clean PDFs with unresolved policy, portal, deadline, or evidence warnings.
- `claim-audit.md`: readable evidence matches, blockers, totals, and output inventory.

Human visual review and claimant approval are always required before submission.

## Insurers and guidance

The [official-source map](references/insurer-sources.md) covers the current IRDAI ordinary-general and standalone-health insurer rosters, with a detailed HDFC ERGO route. Always verify the issued policy and live portal because product rules change.

- [Skill instructions](SKILL.md)
- [Document checklist](references/document-checklist.md)
- [Manifest guide](references/manifest.md)
- [Submission QA](references/qa-submission.md)

## Privacy

Keep real claim files outside Git. Processing is local by default. Preserve paper originals, signed files, imaging films, and untouched source documents. Never submit without the claimant's approval.

## Development

```bash
python3 -m unittest discover -s tests -v
codex-validate-skill .
```

[MIT License](LICENSE) | [Contributing](CONTRIBUTING.md) | [Security](SECURITY.md)
