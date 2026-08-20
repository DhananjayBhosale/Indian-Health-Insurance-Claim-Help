# Contributing

Contributions should make claim preparation safer, clearer, or easier to verify.

## Good contributions

- Corrections backed by a current official insurer, TPA, policy, form, or portal source.
- Tests for a real document-matching, reconciliation, privacy, or output-integrity failure.
- Small usability improvements that preserve original evidence and claimant control.
- Product or UIN updates that clearly record the source and date checked.

Do not submit real claimant PDFs, screenshots, identifiers, diagnoses, policy numbers, bank details, manifests, or portal confirmations. Use synthetic fixtures only.

## Before opening a pull request

Run from the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
codex-validate-skill .
```

Keep changes focused. Explain the user-visible problem, the official authority when applicable, and the verification performed. One maintainer can merge a change after the checks pass; no formal approval ceremony is required.
