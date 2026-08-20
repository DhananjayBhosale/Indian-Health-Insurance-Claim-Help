# Indian Health Insurance Claim Help

Build clear, traceable PDF packets for Indian health-insurance reimbursement claims.

[![Tests](https://github.com/DhananjayBhosale/Indian-Health-Insurance-Claim-Help/actions/workflows/test.yml/badge.svg)](https://github.com/DhananjayBhosale/Indian-Health-Insurance-Claim-Help/actions/workflows/test.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-0f766e.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-0f766e.svg)](https://www.python.org/)

This Codex skill audits and assembles hospitalization, pre-hospitalization, and post-hospitalization evidence. It improves completeness, ordering, reconciliation, and upload readiness without changing the underlying medical or financial records.

> [!IMPORTANT]
> A well-prepared PDF cannot guarantee claim acceptance. The issued policy, treatment eligibility, exclusions, deadlines, originals, medical linkage, and insurer assessment still control the outcome.

## What it checks

- The exact insurer, product, UIN, TPA, policy window, filing deadline, and live submission route.
- Every expense against its prescription or advice, report or service record, itemized bill, and payment proof.
- Patient, provider, date, invoice, service description, amount, and page-level evidence links.
- Missing reports, bills, receipts, signatures, conditional documents, and unaccounted source pages.
- Duplicate expenses, unsupported lines, partial claims, phase subtotals, and final requested total.
- Portal file types, size limits, file-count limits, encryption, and page-by-page visual quality.

## Evidence matching

The skill creates one stable expense ID for each financial event. A bill and its payment receipt are evidence for one expense, not two separate expenses.

```text
Diagnostic test
doctor advice or referral -> complete report -> itemized bill -> payment proof

Medicine
matching prescription -> itemized pharmacy bill -> payment proof

Consultation
consultation note or prescription -> itemized bill -> payment proof
```

Missing-document messages use the visible service name and point back to the supplied file and page. For example:

```text
Lipid profile (cholesterol test)

Found:
- Doctor prescription: prescription.pdf, page 2
- Diagnostic report: lab-report.pdf, pages 1-2

Missing:
- Itemized bill or invoice for Lipid profile (cholesterol test)

Action:
Add the bill, or identify the exact source file and page if it was already supplied.
```

Ambiguous matches remain unresolved. The skill never chooses a bill from its filename alone and never invents a diagnosis, invoice, amount, signature, explanation, or paid status.

## Insurer coverage

The [official-source map](references/insurer-sources.md) routes the current IRDAI ordinary-general and standalone-health insurer rosters, including a detailed HDFC ERGO route. Kshema's current fixed hospital-cash products are intentionally routed outside this expense-indemnity workflow.

Insurer pages, product versions, and portal rules change. Always verify the exact issued policy and live claim journey before using a recorded rule.

## Install

Clone or download this repository into the Codex skills directory:

```bash
git clone https://github.com/DhananjayBhosale/Indian-Health-Insurance-Claim-Help.git \
  ~/.codex/skills/indian-health-insurance-claim-help

cd ~/.codex/skills/indian-health-insurance-claim-help
python3 -m pip install -r requirements.txt
```

Python 3.11 or newer is supported. Install Poppler for rendered visual QA:

```bash
# macOS
brew install poppler

# Ubuntu or Debian
sudo apt-get install poppler-utils
```

## Use with Codex

Attach or place the claim documents in a private local folder, then ask:

```text
Use $indian-health-insurance-claim-help to audit my reimbursement documents.
Create separate hospitalization, pre-hospitalization, and post-hospitalization
PDF packets. Do not upload anything. First show me missing evidence, the
bill-by-bill reconciliation, and the exact output inventory.
```

Codex will identify the exact policy route, create a private case manifest, reconcile the evidence, build review and upload candidates, and retain visual QA and claimant approval as human gates.

## Manual workflow

Run these commands from the repository root:

```bash
python3 scripts/new_claim_case.py /absolute/path/to/private-case

python3 scripts/claim_packet.py audit \
  --manifest /absolute/path/to/private-case/claim-manifest.json \
  --output-dir /absolute/path/to/private-case/output

python3 scripts/claim_packet.py build \
  --manifest /absolute/path/to/private-case/claim-manifest.json \
  --output-dir /absolute/path/to/private-case/output
```

Render every final PDF before upload:

```bash
scripts/render_packet.sh \
  /absolute/path/to/packet.pdf \
  /absolute/path/to/private-case/review/packet-pages
```

Read the [manifest guide](references/manifest.md), [document checklist](references/document-checklist.md), and [submission QA gates](references/qa-submission.md) before preparing a real claim.

## Outputs

| Output | Purpose |
|---|---|
| `REVIEW_ONLY/` | Master packet with generated index, reconciliation, and bookmarks. |
| `SUBMIT/` | Clean category PDFs after structural and recorded portal checks pass. Human visual QA is still required. |
| `CANDIDATE_UPLOADS/` | Clean PDFs with unresolved portal, authority, deadline, or material warnings. |
| `claim-audit.md` | Readable blockers, evidence matches, totals, exclusions, and inventory. |
| `claim-audit.json` | Machine-readable audit and output hashes. |

The builder preserves prior inventory-bearing reports when a rebuild is refused. Use a fresh output directory for every packet revision.

## Privacy and integrity

- Keep real claim workspaces outside this repository and outside Git.
- Process medical, identity, bank, and policy records locally unless the claimant authorizes a named external service.
- Preserve original files byte-for-byte and retain paper originals and physical imaging films.
- Use `delivery_mode: standalone` for digitally signed or interactive-form PDFs.
- Never upload or submit a claim without the claimant's explicit approval.
- Never treat `SUBMIT/` as insurer approval. Complete the private visual-QA and claimant-approval receipt first.

The included manifest and tests use synthetic data only.

## Development

```bash
python3 -m unittest discover -s tests -v
codex-validate-skill .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the focused contribution process and [SECURITY.md](SECURITY.md) for private vulnerability reporting.

## License

[MIT](LICENSE)
