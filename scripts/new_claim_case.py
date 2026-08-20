#!/usr/bin/env python3
"""Create an empty, local workspace for preparing a health-insurance claim."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import NoReturn


CASE_DIRECTORIES = (
    "input",
    "output/REVIEW_ONLY",
    "output/SUBMIT",
    "output/CANDIDATE_UPLOADS",
    "review/renders",
)

GITIGNORE = """# Claim documents can contain sensitive personal and medical data.
input/**
!input/**/
!input/**/.gitkeep

output/**
!output/**/
!output/**/.gitkeep

review/**
!review/**/
!review/**/.gitkeep

claim-manifest.json
submission-receipt.md

# Also protect evidence copied into any additional private source directory.
*.pdf
*.png
*.jpg
*.jpeg
*.tif
*.tiff
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a private, empty claim-packet workspace."
    )
    parser.add_argument("case_dir", metavar="CASE_DIR", help="new case directory")
    parser.add_argument(
        "--force-empty",
        action="store_true",
        help=(
            "allow an already existing empty directory; this never deletes or "
            "overwrites files"
        ),
    )
    return parser.parse_args()


def fail(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    args = parse_args()
    case_dir = Path(args.case_dir).expanduser()
    template = (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "claim-manifest.example.json"
    )

    if not template.is_file():
        fail(f"manifest template is missing: {template}")

    if case_dir.is_symlink():
        fail(f"CASE_DIR must not be a symbolic link: {case_dir}")

    if case_dir.exists():
        if not case_dir.is_dir():
            fail(f"CASE_DIR exists and is not a directory: {case_dir}")
        if any(case_dir.iterdir()):
            fail(
                f"CASE_DIR is not empty: {case_dir}. Nothing was removed or "
                "overwritten. Choose a new or empty directory."
            )
        if not args.force_empty:
            fail(
                f"CASE_DIR already exists: {case_dir}. Use --force-empty only "
                "after confirming that it is empty."
            )
    else:
        case_dir.mkdir(parents=True)

    case_dir.chmod(0o700)

    for relative_path in CASE_DIRECTORIES:
        private_directory = case_dir / relative_path
        private_directory.mkdir(parents=True, exist_ok=False)
    for private_directory in (
        case_dir,
        *(path for path in case_dir.rglob("*") if path.is_dir()),
    ):
        private_directory.chmod(0o700)

    manifest_path = case_dir / "claim-manifest.json"
    ignore_path = case_dir / ".gitignore"
    shutil.copy2(template, manifest_path)
    ignore_path.write_text(GITIGNORE, encoding="utf-8")
    manifest_path.chmod(0o600)
    ignore_path.chmod(0o600)

    resolved_case_dir = case_dir.resolve()
    print(f"Created claim case: {resolved_case_dir}")
    print("Next steps:")
    print("1. Put document copies in input/; keep originals unchanged.")
    print("2. Complete claim-manifest.json and check every document.")
    print("3. Keep drafts in output/REVIEW_ONLY/ and final files in output/SUBMIT/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
