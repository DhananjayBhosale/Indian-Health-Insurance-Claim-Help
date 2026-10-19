# Local setup

Use this when the skill runs on your own computer (for example with Codex or Claude Code) instead of a chat website.

## Install

You need Python 3.11 or newer.

```bash
git clone https://github.com/DhananjayBhosale/Indian-Health-Insurance-Claim-Help.git
cd Indian-Health-Insurance-Claim-Help
python3 -m pip install -r requirements.txt
```

For page-by-page visual checks, also install Poppler: `brew install poppler` on macOS, or `sudo apt-get install poppler-utils` on Ubuntu/Debian.

Names or descriptions in an Indian script (Devanagari, Tamil, Bengali, and others) appear on the review cover only when a matching font is installed, such as Noto Sans Devanagari; macOS and Windows already have them. Set `CLAIM_COVER_FONT_DIR` to a folder of `.ttf` fonts to use other ones. For correctly joined letters, also run `python3 -m pip install uharfbuzz`. Upload files are not affected.

Codex users can install the repository at `~/.codex/skills/indian-health-insurance-claim-help` and invoke `$indian-health-insurance-claim-help`. Other assistants can read `SKILL.md` directly.

## Ask your assistant

Give the assistant access to this folder and to a private folder with the claim documents, then ask:

```text
Read SKILL.md and audit my Indian health-insurance reimbursement documents.
First show me missing evidence and the bill-by-bill reconciliation.
Then create separate hospitalization, pre-hospitalization, and
post-hospitalization PDF candidates. Do not upload anything.
```

## Run the helpers yourself

From the repository root:

```bash
python3 scripts/new_claim_case.py /absolute/path/to/private-case
python3 scripts/claim_packet.py audit --manifest /absolute/path/to/private-case/claim-manifest.json --output-dir /absolute/path/to/private-case/output
python3 scripts/claim_packet.py build --manifest /absolute/path/to/private-case/claim-manifest.json --output-dir /absolute/path/to/private-case/output
scripts/render_packet.sh /absolute/path/to/file.pdf /absolute/path/to/renders
```

Add `--draft` to `build` to get a review-only packet listing what is still missing. Use a new output directory for each build.

Keep claim folders outside this repository.

## Build the claude.ai skill ZIP

The release workflow attaches this ZIP to every GitHub release. To build it yourself from the last commit:

```bash
git archive --format=zip --prefix=indian-health-insurance-claim-help/ -o indian-health-insurance-claim-help.zip HEAD SKILL.md GUIDE.md LICENSE requirements.txt agents assets references scripts
```

The top folder inside the ZIP must be named `indian-health-insurance-claim-help`, matching the skill name. GitHub's green "Code > Download ZIP" button produces a different folder name, which claude.ai rejects.
