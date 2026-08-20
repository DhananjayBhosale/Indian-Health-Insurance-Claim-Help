from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfWriter


SKILL_ROOT = Path(__file__).resolve().parents[1]
NEW_CLAIM_CASE = SKILL_ROOT / "scripts" / "new_claim_case.py"
RENDER_PACKET = SKILL_ROOT / "scripts" / "render_packet.sh"
MANIFEST_TEMPLATE = SKILL_ROOT / "assets" / "claim-manifest.example.json"


class NewClaimCaseCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.test_root = Path(self.temporary_directory.name)

    def _run(
        self, case_dir: Path, *extra_arguments: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(NEW_CLAIM_CASE),
                str(case_dir),
                *extra_arguments,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def assertMode(self, path: Path, expected_mode: int) -> None:  # noqa: N802
        actual_mode = stat.S_IMODE(path.stat().st_mode)
        self.assertEqual(
            actual_mode,
            expected_mode,
            f"unexpected mode for {path}: {oct(actual_mode)}",
        )

    def test_new_case_creates_private_layout_and_copies_template(self) -> None:
        case_dir = self.test_root / "new-case"

        result = self._run(case_dir)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"Created claim case: {case_dir.resolve()}", result.stdout)

        private_directories = (
            case_dir,
            case_dir / "input",
            case_dir / "output",
            case_dir / "output" / "REVIEW_ONLY",
            case_dir / "output" / "SUBMIT",
            case_dir / "output" / "CANDIDATE_UPLOADS",
            case_dir / "review",
            case_dir / "review" / "renders",
        )
        for private_directory in private_directories:
            with self.subTest(path=private_directory):
                self.assertTrue(private_directory.is_dir())
                self.assertMode(private_directory, 0o700)

        manifest = case_dir / "claim-manifest.json"
        local_ignore = case_dir / ".gitignore"
        self.assertEqual(manifest.read_bytes(), MANIFEST_TEMPLATE.read_bytes())
        self.assertMode(manifest, 0o600)
        self.assertMode(local_ignore, 0o600)

        ignore_rules = local_ignore.read_text(encoding="utf-8")
        for private_path in (
            "input/**",
            "output/**",
            "review/**",
            "claim-manifest.json",
            "submission-receipt.md",
            "*.pdf",
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.tif",
            "*.tiff",
        ):
            with self.subTest(ignore_rule=private_path):
                self.assertIn(private_path, ignore_rules)
        self.assertIn("!input/**/.gitkeep", ignore_rules)
        self.assertIn("!output/**/.gitkeep", ignore_rules)
        self.assertIn("!review/**/.gitkeep", ignore_rules)

    def test_existing_nonempty_target_is_refused_without_removing_marker(self) -> None:
        case_dir = self.test_root / "nonempty-case"
        case_dir.mkdir()
        marker = case_dir / "keep-me.txt"
        marker_contents = b"synthetic marker; must remain unchanged\n"
        marker.write_bytes(marker_contents)

        for extra_arguments in ((), ("--force-empty",)):
            with self.subTest(extra_arguments=extra_arguments):
                result = self._run(case_dir, *extra_arguments)
                self.assertEqual(result.returncode, 2)
                self.assertIn("CASE_DIR is not empty", result.stderr)
                self.assertEqual(marker.read_bytes(), marker_contents)
                self.assertEqual(list(case_dir.iterdir()), [marker])

    def test_existing_empty_target_requires_force_empty_then_succeeds(self) -> None:
        case_dir = self.test_root / "empty-case"
        case_dir.mkdir()

        refused = self._run(case_dir)

        self.assertEqual(refused.returncode, 2)
        self.assertIn("CASE_DIR already exists", refused.stderr)
        self.assertEqual(list(case_dir.iterdir()), [])

        created = self._run(case_dir, "--force-empty")

        self.assertEqual(created.returncode, 0, created.stderr)
        self.assertTrue((case_dir / "claim-manifest.json").is_file())
        self.assertMode(case_dir, 0o700)

    def test_symlink_target_is_refused(self) -> None:
        actual_directory = self.test_root / "actual-case"
        actual_directory.mkdir()
        symlink_target = self.test_root / "linked-case"
        try:
            symlink_target.symlink_to(actual_directory, target_is_directory=True)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"directory symlinks are unavailable: {error}")

        result = self._run(symlink_target, "--force-empty")

        self.assertEqual(result.returncode, 2)
        self.assertIn("must not be a symbolic link", result.stderr)
        self.assertTrue(symlink_target.is_symlink())
        self.assertEqual(list(actual_directory.iterdir()), [])

    def test_renderer_creates_private_page_images(self) -> None:
        if not shutil.which("pdfinfo") or not shutil.which("pdftoppm"):
            self.skipTest("Poppler commands are unavailable")
        source = self.test_root / "synthetic.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=595, height=842)
        with source.open("wb") as stream:
            writer.write(stream)
        renders = self.test_root / "renders"

        result = subprocess.run(
            [str(RENDER_PACKET), str(source), str(renders)],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertMode(renders, 0o700)
        pages = list(renders.glob("page-*.png"))
        self.assertEqual(len(pages), 1)
        self.assertMode(pages[0], 0o600)

    def test_renderer_rejects_resolved_home_before_changing_its_mode(self) -> None:
        protected_home = self.test_root / "protected-home"
        protected_home.mkdir(mode=0o755)
        protected_home.chmod(0o755)
        source = self.test_root / "synthetic-home-check.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=595, height=842)
        with source.open("wb") as stream:
            writer.write(stream)
        aliased_home = protected_home / "."
        environment = dict(os.environ)
        environment["HOME"] = str(protected_home)

        result = subprocess.run(
            [str(RENDER_PACKET), str(source), str(aliased_home)],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to use HOME", result.stderr)
        self.assertMode(protected_home, 0o755)

    def test_renderer_failure_still_leaves_partial_page_private(self) -> None:
        fake_bin = self.test_root / "fake-bin"
        fake_bin.mkdir()
        fake_pdfinfo = fake_bin / "pdfinfo"
        fake_pdfinfo.write_text(
            "#!/usr/bin/env bash\nprintf 'Pages: 1\\nPage size: 595 x 842 pts\\nFile size: 10 bytes\\n'\n",
            encoding="utf-8",
        )
        fake_pdftoppm = fake_bin / "pdftoppm"
        fake_pdftoppm.write_text(
            "#!/usr/bin/env bash\nfor last_argument do :; done\nprintf x > \"${last_argument}-1.png\"\nexit 1\n",
            encoding="utf-8",
        )
        fake_pdfinfo.chmod(0o755)
        fake_pdftoppm.chmod(0o755)
        source = self.test_root / "synthetic-failure.pdf"
        source.write_bytes(b"%PDF-synthetic")
        renders = self.test_root / "failed-renders"
        environment = dict(os.environ)
        environment["PATH"] = f"{fake_bin}{os.pathsep}{environment['PATH']}"

        result = subprocess.run(
            [str(RENDER_PACKET), str(source), str(renders)],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

        self.assertEqual(result.returncode, 1)
        self.assertMode(renders, 0o700)
        partial = renders / "page-1.png"
        self.assertTrue(partial.is_file())
        self.assertMode(partial, 0o600)


if __name__ == "__main__":
    unittest.main()
