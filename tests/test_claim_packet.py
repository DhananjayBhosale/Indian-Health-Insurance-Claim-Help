from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


SKILL_ROOT = Path(__file__).resolve().parents[1]
CLAIM_PACKET = SKILL_ROOT / "scripts" / "claim_packet.py"


class ClaimPacketCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.case_root = Path(self.temporary_directory.name)
        self.sources = self.case_root / "sources"
        self.sources.mkdir()
        self._create_source_set()

    def _pdf(self, name: str, label: str, pages: int = 1) -> Path:
        path = self.sources / name
        document = canvas.Canvas(str(path), pagesize=A4, invariant=1)
        for page_number in range(1, pages + 1):
            document.setFont("Helvetica-Bold", 14)
            document.drawString(72, 770, label)
            document.setFont("Helvetica", 10)
            document.drawString(72, 748, f"Synthetic source page {page_number} of {pages}")
            document.showPage()
        document.save()
        return path

    def _png(self, name: str, label: str) -> Path:
        path = self.sources / name
        image = Image.new("RGB", (900, 600), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((20, 20, 880, 580), outline="black", width=4)
        draw.text((55, 55), label, fill="black", font=ImageFont.load_default())
        image.save(path, format="PNG")
        return path

    @staticmethod
    def _sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _create_source_set(self) -> None:
        self._pdf("admin.pdf", "Claim form, patient identity, and bank proof")
        self._pdf("discharge.pdf", "Hospital discharge summary")
        self._pdf("hospital-bill.pdf", "Hospital final bill and paid receipt")
        self._pdf("pre-advice.pdf", "Pre-hospitalization diagnostic advice")
        self._png("pre-result.png", "Pre-hospitalization diagnostic report")
        self._pdf("pre-invoice.pdf", "Pre-hospitalization paid diagnostic invoice")
        self._pdf("post-prescription.pdf", "Post-hospitalization prescription")
        self._pdf("post-invoice.pdf", "Post-hospitalization paid medicine bill")

    def _document(
        self,
        *,
        document_id: str,
        path: str,
        phase: str,
        document_type: str,
        date: str,
        expense_ids: list[str],
        roles: list[str],
        packs: list[str],
        pages: str | None = None,
        decision: str = "include",
        exclusion_reason: str = "",
    ) -> dict[str, object]:
        source = self.case_root / path
        return {
            "id": document_id,
            "path": path,
            "expected_sha256": self._sha256(source),
            "decision": decision,
            "pages": pages,
            "phase": phase,
            "document_type": document_type,
            "date": date,
            "expense_ids": expense_ids,
            "evidence_roles": roles,
            "packs": packs,
            "original_status": "original",
            "exclusion_reason": exclusion_reason,
        }

    def _manifest(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "case": {
                "case_id": "synthetic-claim-001",
                "insurer": "Synthetic insurer",
                "product": "Synthetic indemnity health plan",
                "uin": "SYNHLIP00001V012026",
                "patient_name": "Synthetic Patient",
                "policy_reference": "POLICY-TEST-001",
                "claim_reference": "CLAIM-TEST-001",
                "main_claim_reference": "",
                "claim_type": "hospitalization_reimbursement",
                "claim_route": "combined_initial",
                "submission_channel": "online portal",
                "admission_date": "2026-08-10",
                "discharge_date": "2026-08-12",
                "claimed_amount": "180.00",
                "currency": "INR",
            },
            "verification": {
                "checked_on": "2026-08-19",
                "official_claim_form_url": "https://example.test/claim-form",
                "official_policy_url": "https://example.test/policy",
                "portal_rules_url": "https://example.test/upload-rules",
                "portal_rules_confirmed": True,
                "coverage_window": {
                    "pre_start": "2026-07-01",
                    "pre_end": "2026-08-09",
                    "post_start": "2026-08-13",
                    "post_end": "2026-10-31",
                    "authority": "Synthetic policy fixture",
                    "authority_url": "https://example.test/policy#coverage-window",
                },
                "filing_deadlines": {
                    "hospitalization_and_pre_due": "2099-01-01",
                    "post_due": "2099-02-01",
                    "authority": "Synthetic policy fixture",
                    "authority_url": "https://example.test/policy#filing-deadlines",
                },
                "portal": {
                    "rule_scope": "initial reimbursement upload for synthetic policy",
                    "accepted_file_types": ["pdf"],
                    "max_file_mb": "5",
                    "max_total_mb": "20",
                    "max_files": 4,
                    "authority_url": "https://example.test/upload-rules",
                },
            },
            "conditions": {
                "surgery": False,
                "implant": False,
                "accident": False,
                "death_claim": False,
                "non_network_hospital": False,
                "other_insurer_involved": False,
                "maternity": False,
                "ambulance_claimed": False,
            },
            "rules": {
                "source_roots": ["sources"],
                "required_case_roles": ["claim_form", "identity", "bank", "discharge"],
                "compatibility_target_mb": "5",
                "pack_definitions": [
                    {"id": "01-admin", "label": "Administrative", "max_file_mb": None},
                    {"id": "02-hospital", "label": "Hospitalization", "max_file_mb": None},
                    {"id": "03-pre", "label": "Pre-hospitalization", "max_file_mb": None},
                    {"id": "04-post", "label": "Post-hospitalization", "max_file_mb": None},
                ],
            },
            "expenses": [
                {
                    "id": "exp-hospital",
                    "phase": "hospitalization",
                    "kind": "hospital",
                    "date": "2026-08-12",
                    "issuer": "Synthetic Hospital",
                    "invoice_number": "HOSP-001",
                    "description": "Hospitalization bill",
                    "billed_amount": "100.00",
                    "claim_amount": "100.00",
                    "not_claimed_reason": "",
                },
                {
                    "id": "exp-pre",
                    "phase": "pre",
                    "kind": "diagnostic",
                    "date": "2026-08-05",
                    "issuer": "Synthetic Diagnostics",
                    "invoice_number": "PRE-001",
                    "description": "Lipid profile (cholesterol test)",
                    "billed_amount": "50.00",
                    "claim_amount": "50.00",
                    "not_claimed_reason": "",
                },
                {
                    "id": "exp-post",
                    "phase": "post",
                    "kind": "medicine",
                    "date": "2026-08-20",
                    "issuer": "Synthetic Pharmacy",
                    "invoice_number": "POST-001",
                    "description": "Prescribed medicine",
                    "billed_amount": "30.00",
                    "claim_amount": "30.00",
                    "not_claimed_reason": "",
                },
            ],
            "documents": [
                self._document(
                    document_id="doc-admin",
                    path="sources/admin.pdf",
                    phase="administrative",
                    document_type="Claim form, identity, and bank proof",
                    date="2026-08-20",
                    expense_ids=[],
                    roles=["claim_form", "identity", "bank"],
                    packs=["01-admin"],
                ),
                self._document(
                    document_id="doc-discharge",
                    path="sources/discharge.pdf",
                    phase="hospitalization",
                    document_type="Discharge summary",
                    date="2026-08-12",
                    expense_ids=[],
                    roles=["discharge"],
                    packs=["02-hospital"],
                ),
                self._document(
                    document_id="doc-hospital-bill",
                    path="sources/hospital-bill.pdf",
                    phase="hospitalization",
                    document_type="Final hospital bill and payment receipt",
                    date="2026-08-12",
                    expense_ids=["exp-hospital"],
                    roles=["invoice", "payment_proof"],
                    packs=["02-hospital"],
                ),
                self._document(
                    document_id="doc-pre-advice",
                    path="sources/pre-advice.pdf",
                    phase="pre",
                    document_type="Diagnostic advice",
                    date="2026-08-04",
                    expense_ids=["exp-pre"],
                    roles=["clinical_advice"],
                    packs=["03-pre"],
                ),
                self._document(
                    document_id="doc-pre-result",
                    path="sources/pre-result.png",
                    phase="pre",
                    document_type="Diagnostic report",
                    date="2026-08-05",
                    expense_ids=["exp-pre"],
                    roles=["clinical_result"],
                    packs=["03-pre"],
                ),
                self._document(
                    document_id="doc-pre-invoice",
                    path="sources/pre-invoice.pdf",
                    phase="pre",
                    document_type="Diagnostic invoice and payment receipt",
                    date="2026-08-05",
                    expense_ids=["exp-pre"],
                    roles=["invoice", "payment_proof"],
                    packs=["03-pre"],
                ),
                self._document(
                    document_id="doc-post-prescription",
                    path="sources/post-prescription.pdf",
                    phase="post",
                    document_type="Medicine prescription",
                    date="2026-08-18",
                    expense_ids=["exp-post"],
                    roles=["clinical_advice"],
                    packs=["04-post"],
                ),
                self._document(
                    document_id="doc-post-invoice",
                    path="sources/post-invoice.pdf",
                    phase="post",
                    document_type="Pharmacy invoice and payment receipt",
                    date="2026-08-20",
                    expense_ids=["exp-post"],
                    roles=["invoice", "payment_proof"],
                    packs=["04-post"],
                ),
            ],
        }

    def _write_manifest(self, manifest: dict[str, object], name: str = "manifest.json") -> Path:
        path = self.case_root / name
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return path

    def _run(self, command: str, manifest: Path, output_name: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(CLAIM_PACKET),
                command,
                "--manifest",
                str(manifest),
                "--output-dir",
                str(self.case_root / output_name),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def _assert_code(
        self, result: subprocess.CompletedProcess[str], expected: int
    ) -> None:
        self.assertEqual(
            result.returncode,
            expected,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def _report(self, output_name: str) -> dict[str, object]:
        return json.loads(
            (self.case_root / output_name / "claim-audit.json").read_text(encoding="utf-8")
        )

    def _attempt_report(self, output_name: str) -> dict[str, object]:
        return json.loads(
            (self.case_root / output_name / "claim-audit-attempt.json").read_text(
                encoding="utf-8"
            )
        )

    @staticmethod
    def _blocker_codes(report: dict[str, object]) -> set[str]:
        return {item["code"] for item in report["blockers"]}  # type: ignore[index]

    def test_successful_audit_and_build_create_clean_submit_packets(self) -> None:
        manifest_path = self._write_manifest(self._manifest())

        audit = self._run("audit", manifest_path, "successful-audit")
        self._assert_code(audit, 0)
        audit_report = self._report("successful-audit")
        self.assertEqual(audit_report["status"], "READY_WITH_WARNINGS")
        self.assertEqual(audit_report["blockers"], [])
        self.assertEqual(
            {item["code"] for item in audit_report["warnings"]},  # type: ignore[index]
            {"VISUAL_QA_PENDING"},
        )

        build = self._run("build", manifest_path, "successful-build")
        self._assert_code(build, 0)
        report = self._report("successful-build")
        self.assertEqual(report["status"], "READY_WITH_WARNINGS")
        self.assertEqual(report["blockers"], [])

        submit_dir = self.case_root / "successful-build" / "SUBMIT"
        expected_pages = {
            "01-admin.pdf": 1,
            "02-hospital.pdf": 2,
            "03-pre.pdf": 3,
            "04-post.pdf": 2,
        }
        self.assertEqual({path.name for path in submit_dir.glob("*.pdf")}, set(expected_pages))
        for name, page_count in expected_pages.items():
            reader = PdfReader(str(submit_dir / name), strict=False)
            self.assertEqual(len(reader.pages), page_count)
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
            self.assertNotIn("REVIEW ONLY", text)
            self.assertNotIn("Health reimbursement claim - review packet", text)
            self.assertNotIn("Claim packet audit", text)

        master_path = (
            self.case_root
            / "successful-build"
            / "REVIEW_ONLY"
            / "synthetic-claim-001-master-review.pdf"
        )
        master = PdfReader(str(master_path), strict=False)
        self.assertGreater(len(master.pages), sum(expected_pages.values()))
        self.assertIn("REVIEW ONLY", master.pages[0].extract_text() or "")

        for output in report["outputs"]:  # type: ignore[index]
            output_path = Path(output["path"])
            self.assertEqual(output["sha256"], self._sha256(output_path))
            self.assertEqual(output["bytes"], output_path.stat().st_size)
            self.assertEqual(output["pages"], len(PdfReader(str(output_path)).pages))

    def test_pre_and_post_expenses_require_complete_evidence_chains(self) -> None:
        for document_id, expense_id in (
            ("doc-pre-result", "exp-pre"),
            ("doc-post-prescription", "exp-post"),
        ):
            with self.subTest(document_id=document_id):
                manifest = self._manifest()
                manifest["documents"] = [  # type: ignore[index]
                    document
                    for document in manifest["documents"]  # type: ignore[index]
                    if document["id"] != document_id
                ]
                manifest_path = self._write_manifest(manifest, f"missing-{document_id}.json")
                result = self._run("audit", manifest_path, f"missing-{document_id}")
                self._assert_code(result, 2)
                report = self._report(f"missing-{document_id}")
                missing = [
                    item
                    for item in report["blockers"]  # type: ignore[index]
                    if item["code"] == "MISSING_EXPENSE_EVIDENCE"
                ]
                self.assertEqual([item["expense_id"] for item in missing], [expense_id])
                self.assertIn("provider", missing[0]["message"])
                self.assertIn("invoice", missing[0]["message"])
                self.assertIn("exact source file and page(s)", missing[0]["message"])
                expected_role = (
                    "complete report or result for Lipid profile (cholesterol test)"
                    if expense_id == "exp-pre"
                    else "doctor advice, prescription, or referral for Prescribed medicine"
                )
                self.assertIn(expected_role, missing[0]["message"])
                expense_report = next(
                    item for item in report["expenses"] if item["id"] == expense_id  # type: ignore[index]
                )
                self.assertTrue(expense_report["linked_evidence"])
                self.assertIn(expected_role, expense_report["missing_evidence"])
                if expense_id == "exp-pre":
                    linked_sources = {
                        (item["source"], item["pages"])
                        for item in expense_report["linked_evidence"]
                    }
                    self.assertIn(("sources/pre-invoice.pdf", "1"), linked_sources)
                    self.assertIn("invoice PRE-001", missing[0]["message"])

    def test_total_mismatch_is_a_blocker(self) -> None:
        manifest = self._manifest()
        manifest["case"]["claimed_amount"] = "180.01"  # type: ignore[index]
        manifest_path = self._write_manifest(manifest)

        result = self._run("audit", manifest_path, "total-mismatch")

        self._assert_code(result, 2)
        self.assertIn("CLAIM_TOTAL_MISMATCH", self._blocker_codes(self._report("total-mismatch")))

    def test_missing_diagnostic_bill_names_the_specific_test(self) -> None:
        manifest = self._manifest()
        manifest["documents"] = [  # type: ignore[index]
            document
            for document in manifest["documents"]  # type: ignore[index]
            if document["id"] != "doc-pre-invoice"
        ]
        manifest_path = self._write_manifest(manifest, "missing-lipid-bill.json")

        result = self._run("audit", manifest_path, "missing-lipid-bill")
        self._assert_code(result, 2)
        report = self._report("missing-lipid-bill")
        blocker = next(
            item
            for item in report["blockers"]  # type: ignore[index]
            if item["code"] == "MISSING_EXPENSE_EVIDENCE"
            and item.get("expense_id") == "exp-pre"
        )
        self.assertIn(
            "itemized bill or invoice for Lipid profile (cholesterol test)",
            blocker["message"],
        )
        self.assertIn(
            "payment receipt or other paid proof for Lipid profile (cholesterol test)",
            blocker["message"],
        )

    def test_duplicate_financial_event_is_a_blocker(self) -> None:
        manifest = self._manifest()
        duplicate = copy.deepcopy(manifest["expenses"][0])  # type: ignore[index]
        duplicate["id"] = "exp-hospital-copy"
        duplicate["phase"] = "post"
        manifest["expenses"].append(duplicate)  # type: ignore[index]
        manifest["case"]["claimed_amount"] = "280.00"  # type: ignore[index]
        hospital_bill = next(
            document
            for document in manifest["documents"]  # type: ignore[index]
            if document["id"] == "doc-hospital-bill"
        )
        hospital_bill["expense_ids"].append("exp-hospital-copy")
        manifest_path = self._write_manifest(manifest)

        result = self._run("audit", manifest_path, "duplicate-event")

        self._assert_code(result, 2)
        report = self._report("duplicate-event")
        duplicate_blockers = [
            item
            for item in report["blockers"]  # type: ignore[index]
            if item["code"] == "DUPLICATE_FINANCIAL_EVENT"
        ]
        self.assertEqual(len(duplicate_blockers), 1)
        self.assertEqual(duplicate_blockers[0]["expense_id"], "exp-hospital-copy")

    def test_every_referenced_source_page_needs_an_include_or_exclude_decision(self) -> None:
        source = self._pdf("admin-two-pages.pdf", "Administrative evidence", pages=2)
        manifest = self._manifest()
        admin = next(
            document
            for document in manifest["documents"]  # type: ignore[index]
            if document["id"] == "doc-admin"
        )
        admin["path"] = "sources/admin-two-pages.pdf"
        admin["expected_sha256"] = self._sha256(source)
        admin["pages"] = "1"
        (self.sources / "admin.pdf").unlink()
        manifest_path = self._write_manifest(manifest, "unaccounted.json")

        incomplete = self._run("audit", manifest_path, "unaccounted")
        self._assert_code(incomplete, 2)
        self.assertIn(
            "UNACCOUNTED_SOURCE_PAGES",
            self._blocker_codes(self._report("unaccounted")),
        )

        manifest["documents"].append(  # type: ignore[index]
            self._document(
                document_id="doc-admin-blank-reverse",
                path="sources/admin-two-pages.pdf",
                phase="administrative",
                document_type="Blank reverse page",
                date="",
                expense_ids=[],
                roles=[],
                packs=[],
                pages="2",
                decision="exclude",
                exclusion_reason="Blank reverse page; no claim evidence",
            )
        )
        complete_path = self._write_manifest(manifest, "accounted.json")
        complete = self._run("audit", complete_path, "accounted")
        self._assert_code(complete, 0)
        self.assertNotIn(
            "UNACCOUNTED_SOURCE_PAGES",
            self._blocker_codes(self._report("accounted")),
        )

    def test_encrypted_input_is_blocked_and_never_built(self) -> None:
        original = PdfReader(str(self.sources / "admin.pdf"), strict=False)
        encrypted = PdfWriter()
        for page in original.pages:
            encrypted.add_page(page)
        encrypted.encrypt("synthetic-password")
        encrypted_path = self.sources / "admin-encrypted.pdf"
        with encrypted_path.open("wb") as stream:
            encrypted.write(stream)

        manifest = self._manifest()
        admin = next(
            document
            for document in manifest["documents"]  # type: ignore[index]
            if document["id"] == "doc-admin"
        )
        admin["path"] = "sources/admin-encrypted.pdf"
        admin["expected_sha256"] = self._sha256(encrypted_path)
        (self.sources / "admin.pdf").unlink()
        manifest_path = self._write_manifest(manifest)

        result = self._run("build", manifest_path, "encrypted")

        self._assert_code(result, 2)
        report = self._report("encrypted")
        invalid = [
            item
            for item in report["blockers"]  # type: ignore[index]
            if item["code"] == "SOURCE_INVALID"
        ]
        self.assertEqual(len(invalid), 1)
        self.assertIn("encrypted/password-protected", invalid[0]["message"])
        self.assertFalse((self.case_root / "encrypted" / "SUBMIT").exists())
        self.assertFalse((self.case_root / "encrypted" / "REVIEW_ONLY").exists())

    def test_build_refuses_to_overwrite_any_existing_pdf(self) -> None:
        manifest_path = self._write_manifest(self._manifest())
        first = self._run("build", manifest_path, "non-overwrite")
        self._assert_code(first, 0)
        output_root = self.case_root / "non-overwrite"
        pdfs = sorted(output_root.rglob("*.pdf"))
        before = {path: self._sha256(path) for path in pdfs}
        audit_json_before = (output_root / "claim-audit.json").read_bytes()
        audit_markdown_before = (output_root / "claim-audit.md").read_bytes()

        second = self._run("build", manifest_path, "non-overwrite")

        self._assert_code(second, 2)
        self.assertIn(
            "OUTPUT_DIRECTORY_NOT_EMPTY",
            self._blocker_codes(self._attempt_report("non-overwrite")),
        )
        self.assertEqual(before, {path: self._sha256(path) for path in pdfs})
        self.assertEqual(audit_json_before, (output_root / "claim-audit.json").read_bytes())
        self.assertEqual(
            audit_markdown_before, (output_root / "claim-audit.md").read_bytes()
        )

    def test_audit_and_build_preserve_all_source_bytes_and_record_their_hashes(self) -> None:
        manifest = self._manifest()
        manifest_path = self._write_manifest(manifest)
        source_paths = sorted(self.sources.iterdir())
        before = {path: self._sha256(path) for path in source_paths}

        audit = self._run("audit", manifest_path, "hash-audit")
        self._assert_code(audit, 0)
        build = self._run("build", manifest_path, "hash-build")
        self._assert_code(build, 0)

        self.assertEqual(before, {path: self._sha256(path) for path in source_paths})
        report = self._report("hash-build")
        recorded = {
            str(self.case_root / document["source"]): document["sha256"]
            for document in report["documents"]  # type: ignore[index]
        }
        for path, digest in before.items():
            self.assertEqual(recorded[str(path)], digest)

    def test_interactive_form_is_copied_byte_for_byte_as_standalone(self) -> None:
        interactive_path = self.sources / "interactive-claim-form.pdf"
        document = canvas.Canvas(str(interactive_path), pagesize=A4, invariant=1)
        document.drawString(72, 770, "Synthetic interactive claim form")
        document.acroForm.textfield(
            name="synthetic_patient",
            value="Synthetic Patient",
            x=72,
            y=710,
            width=220,
            height=24,
        )
        document.showPage()
        document.save()

        manifest = self._manifest()
        admin = next(
            item
            for item in manifest["documents"]  # type: ignore[index]
            if item["id"] == "doc-admin"
        )
        admin["path"] = "sources/interactive-claim-form.pdf"
        admin["expected_sha256"] = self._sha256(interactive_path)
        admin["delivery_mode"] = "standalone"
        (self.sources / "admin.pdf").unlink()
        manifest_path = self._write_manifest(manifest)

        result = self._run("build", manifest_path, "standalone-form")

        self._assert_code(result, 0)
        copied = list((self.case_root / "standalone-form" / "SUBMIT").glob("*--original.pdf"))
        self.assertEqual(len(copied), 1)
        self.assertEqual(copied[0].read_bytes(), interactive_path.read_bytes())
        self.assertTrue(PdfReader(str(copied[0])).get_fields())
        report = self._report("standalone-form")
        standalone = [
            item
            for item in report["outputs"]  # type: ignore[index]
            if ":standalone:" in item["purpose"]
        ]
        self.assertEqual(len(standalone), 1)
        self.assertEqual(standalone[0]["sha256"], self._sha256(interactive_path))

    def test_interactive_form_requires_standalone_delivery(self) -> None:
        interactive_path = self.sources / "interactive-blocked.pdf"
        document = canvas.Canvas(str(interactive_path), pagesize=A4, invariant=1)
        document.acroForm.textfield(
            name="synthetic_field", x=72, y=710, width=220, height=24
        )
        document.showPage()
        document.save()
        manifest = self._manifest()
        admin = next(
            item
            for item in manifest["documents"]  # type: ignore[index]
            if item["id"] == "doc-admin"
        )
        admin["path"] = "sources/interactive-blocked.pdf"
        admin["expected_sha256"] = self._sha256(interactive_path)
        (self.sources / "admin.pdf").unlink()
        manifest_path = self._write_manifest(manifest)

        result = self._run("audit", manifest_path, "interactive-blocked")

        self._assert_code(result, 2)
        self.assertIn(
            "PROTECTED_PDF_STANDALONE",
            self._blocker_codes(self._report("interactive-blocked")),
        )

    def test_audit_refuses_symlink_report_without_touching_target(self) -> None:
        manifest_path = self._write_manifest(self._manifest())
        output = self.case_root / "symlink-output"
        output.mkdir()
        victim = self.case_root / "victim.txt"
        victim.write_text("preserve me", encoding="utf-8")
        try:
            (output / "claim-audit.json").symlink_to(victim)
        except (OSError, NotImplementedError):
            self.skipTest("symbolic links are unavailable")

        result = self._run("audit", manifest_path, "symlink-output")

        self._assert_code(result, 2)
        self.assertEqual(victim.read_text(encoding="utf-8"), "preserve me")
        self.assertIn("must not be a symbolic link", result.stderr)

    def test_output_must_stay_inside_private_manifest_directory(self) -> None:
        manifest_path = self._write_manifest(self._manifest())
        external_temporary = tempfile.TemporaryDirectory()
        self.addCleanup(external_temporary.cleanup)
        external = Path(external_temporary.name)
        external.chmod(0o755)
        marker = external / "preserve.txt"
        marker.write_text("preserve", encoding="utf-8")
        mode_before = external.stat().st_mode & 0o777

        result = subprocess.run(
            [
                sys.executable,
                str(CLAIM_PACKET),
                "audit",
                "--manifest",
                str(manifest_path),
                "--output-dir",
                str(external),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self._assert_code(result, 2)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("strict descendant", result.stderr)
        self.assertEqual(external.stat().st_mode & 0o777, mode_before)
        self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")
        self.assertFalse((external / "claim-audit.json").exists())

    def test_regular_file_output_root_is_refused_without_modification(self) -> None:
        manifest_path = self._write_manifest(self._manifest())
        output_file = self.case_root / "output-is-file"
        output_file.write_text("preserve", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(CLAIM_PACKET),
                "audit",
                "--manifest",
                str(manifest_path),
                "--output-dir",
                str(output_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self._assert_code(result, 2)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("not a directory", result.stderr)
        self.assertEqual(output_file.read_text(encoding="utf-8"), "preserve")

    def test_private_output_permissions(self) -> None:
        manifest_path = self._write_manifest(self._manifest())

        result = self._run("build", manifest_path, "private-modes")

        self._assert_code(result, 0)
        output = self.case_root / "private-modes"
        self.assertEqual(output.stat().st_mode & 0o777, 0o700)
        for directory in (output / "REVIEW_ONLY", output / "SUBMIT"):
            self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
        for path in output.rglob("*"):
            if path.is_file():
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_unverified_portal_builds_candidates_not_submit_files(self) -> None:
        manifest = self._manifest()
        manifest["verification"]["portal_rules_confirmed"] = False  # type: ignore[index]
        manifest_path = self._write_manifest(manifest)

        result = self._run("build", manifest_path, "unverified-portal")

        self._assert_code(result, 0)
        output = self.case_root / "unverified-portal"
        self.assertEqual(list((output / "SUBMIT").iterdir()), [])
        self.assertEqual(len(list((output / "CANDIDATE_UPLOADS").glob("*.pdf"))), 4)
        self.assertEqual(self._report("unverified-portal")["status"], "PORTAL_RULES_UNVERIFIED")

    def test_supported_input_file_cannot_be_left_out_of_manifest(self) -> None:
        manifest = self._manifest()
        self._pdf("forgotten-receipt.pdf", "Unmanifested synthetic receipt")
        manifest_path = self._write_manifest(manifest)

        result = self._run("audit", manifest_path, "unmanifested-source")

        self._assert_code(result, 2)
        self.assertIn(
            "UNMANIFESTED_SOURCE_FILE",
            self._blocker_codes(self._report("unmanifested-source")),
        )

    def test_source_roots_must_be_strictly_inside_private_case(self) -> None:
        unsafe_roots = ("/", ".", "..", str(self.case_root.parent))
        for index, unsafe_root in enumerate(unsafe_roots):
            with self.subTest(source_root=unsafe_root):
                manifest = self._manifest()
                manifest["rules"]["source_roots"] = [unsafe_root]  # type: ignore[index]
                manifest_path = self._write_manifest(manifest, f"unsafe-root-{index}.json")
                output_name = f"unsafe-root-{index}"

                result = self._run("audit", manifest_path, output_name)

                self._assert_code(result, 2)
                codes = self._blocker_codes(self._report(output_name))
                self.assertIn("SOURCE_ROOT_SCOPE", codes)
                self.assertIn("SOURCE_ROOTS_UNAVAILABLE", codes)

    def test_document_outside_source_roots_is_not_opened(self) -> None:
        external = self.case_root / "external"
        external.mkdir()
        original = PdfReader(str(self.sources / "admin.pdf"), strict=False)
        encrypted = PdfWriter()
        for page in original.pages:
            encrypted.add_page(page)
        encrypted.encrypt("must-not-be-opened")
        outside_path = external / "outside-encrypted.pdf"
        with outside_path.open("wb") as stream:
            encrypted.write(stream)
        manifest = self._manifest()
        admin = next(
            item
            for item in manifest["documents"]  # type: ignore[index]
            if item["id"] == "doc-admin"
        )
        admin["path"] = "external/outside-encrypted.pdf"
        admin["expected_sha256"] = self._sha256(outside_path)
        manifest_path = self._write_manifest(manifest)

        result = self._run("audit", manifest_path, "outside-root")

        self._assert_code(result, 2)
        codes = self._blocker_codes(self._report("outside-root"))
        self.assertIn("SOURCE_OUTSIDE_ROOTS", codes)
        self.assertNotIn("SOURCE_INVALID", codes)

    def test_empty_page_selection_cannot_satisfy_evidence_roles(self) -> None:
        manifest = self._manifest()
        manifest["documents"][0]["pages"] = []  # type: ignore[index]
        manifest_path = self._write_manifest(manifest)

        result = self._run("build", manifest_path, "empty-pages")

        self._assert_code(result, 2)
        self.assertIn("SOURCE_INVALID", self._blocker_codes(self._report("empty-pages")))
        self.assertFalse((self.case_root / "empty-pages" / "SUBMIT").exists())

    def test_pack_limit_cannot_override_stricter_portal_limit(self) -> None:
        manifest = self._manifest()
        manifest["verification"]["portal"]["max_file_mb"] = "0.001"  # type: ignore[index]
        for pack in manifest["rules"]["pack_definitions"]:  # type: ignore[index]
            pack["max_file_mb"] = "5"
        manifest_path = self._write_manifest(manifest)

        result = self._run("build", manifest_path, "stricter-portal-limit")

        self._assert_code(result, 2)
        self.assertIn(
            "UPLOAD_FILE_TOO_LARGE",
            self._blocker_codes(self._report("stricter-portal-limit")),
        )

    def test_extreme_decimal_is_reported_without_crashing(self) -> None:
        manifest = self._manifest()
        manifest["expenses"][0]["billed_amount"] = "1e999999"  # type: ignore[index]
        manifest["expenses"][0]["claim_amount"] = "1e999999"  # type: ignore[index]
        manifest["case"]["claimed_amount"] = "1e999999"  # type: ignore[index]
        manifest_path = self._write_manifest(manifest)

        result = self._run("audit", manifest_path, "extreme-decimal")

        self._assert_code(result, 2)
        self.assertNotIn("Traceback", result.stderr)
        codes = self._blocker_codes(self._report("extreme-decimal"))
        self.assertIn("EXPENSE_AMOUNT", codes)
        self.assertIn("CLAIM_TOTAL", codes)

    def test_every_conditional_branch_requires_an_explicit_boolean(self) -> None:
        cases = (("missing", None), ("string", "false"))
        for label, value in cases:
            with self.subTest(label=label):
                manifest = self._manifest()
                if value is None:
                    del manifest["conditions"]["accident"]  # type: ignore[index]
                    expected = "CONDITION_UNVERIFIED"
                else:
                    manifest["conditions"]["accident"] = value  # type: ignore[index]
                    expected = "CONDITION_TYPE"
                manifest_path = self._write_manifest(manifest, f"condition-{label}.json")

                result = self._run("audit", manifest_path, f"condition-{label}")

                self._assert_code(result, 2)
                self.assertIn(expected, self._blocker_codes(self._report(f"condition-{label}")))

    def test_required_case_roles_cannot_be_empty(self) -> None:
        manifest = self._manifest()
        manifest["rules"]["required_case_roles"] = []  # type: ignore[index]
        manifest_path = self._write_manifest(manifest)

        result = self._run("audit", manifest_path, "empty-case-roles")

        self._assert_code(result, 2)
        self.assertIn(
            "REQUIRED_CASE_ROLES",
            self._blocker_codes(self._report("empty-case-roles")),
        )

    def test_implant_expense_needs_linked_clinical_or_operation_record(self) -> None:
        implant_label = self._pdf("implant-label.pdf", "Synthetic implant identity label")
        manifest = self._manifest()
        manifest["conditions"]["implant"] = True  # type: ignore[index]
        manifest["expenses"].append(  # type: ignore[index]
            {
                "id": "exp-implant",
                "phase": "hospitalization",
                "kind": "implant",
                "date": "2026-08-11",
                "issuer": "Synthetic Implant Supplier",
                "invoice_number": "IMPLANT-001",
                "description": "Synthetic implant",
                "billed_amount": "20.00",
                "claim_amount": "20.00",
                "not_claimed_reason": "",
            }
        )
        manifest["case"]["claimed_amount"] = "200.00"  # type: ignore[index]
        hospital_bill = next(
            item
            for item in manifest["documents"]  # type: ignore[index]
            if item["id"] == "doc-hospital-bill"
        )
        hospital_bill["expense_ids"].append("exp-implant")
        manifest["documents"].append(  # type: ignore[index]
            self._document(
                document_id="doc-implant-label",
                path="sources/implant-label.pdf",
                phase="hospitalization",
                document_type="Implant identity label",
                date="2026-08-11",
                expense_ids=["exp-implant"],
                roles=["implant_identity"],
                packs=["02-hospital"],
            )
        )
        self.assertEqual(self._sha256(implant_label), manifest["documents"][-1]["expected_sha256"])  # type: ignore[index]
        manifest_path = self._write_manifest(manifest)

        result = self._run("audit", manifest_path, "implant-context")

        self._assert_code(result, 2)
        missing = [
            item
            for item in self._report("implant-context")["blockers"]  # type: ignore[index]
            if item["code"] == "MISSING_EXPENSE_EVIDENCE"
            and item.get("expense_id") == "exp-implant"
        ]
        self.assertTrue(any("clinical_record or operation_record" in item["message"] for item in missing))

    def test_confirmed_null_portal_limits_need_explicit_unpublished_status(self) -> None:
        manifest = self._manifest()
        portal = manifest["verification"]["portal"]  # type: ignore[index]
        portal["max_file_mb"] = None
        portal["max_total_mb"] = None
        portal["max_files"] = None
        manifest_path = self._write_manifest(manifest, "portal-null-unknown.json")

        unknown = self._run("audit", manifest_path, "portal-null-unknown")

        self._assert_code(unknown, 2)
        self.assertIn(
            "PORTAL_LIMIT_STATUS",
            self._blocker_codes(self._report("portal-null-unknown")),
        )

        portal["unpublished_rules"] = ["max_file_mb", "max_total_mb", "max_files"]
        recorded_path = self._write_manifest(manifest, "portal-null-recorded.json")
        recorded = self._run("audit", recorded_path, "portal-null-recorded")

        self._assert_code(recorded, 0)
        self.assertEqual(self._report("portal-null-recorded")["blockers"], [])

    def test_confirmed_portal_rules_require_the_exact_journey_scope(self) -> None:
        manifest = self._manifest()
        manifest["verification"]["portal"].pop("rule_scope")  # type: ignore[index]
        manifest_path = self._write_manifest(manifest)

        result = self._run("audit", manifest_path, "portal-scope-missing")

        self._assert_code(result, 2)
        report = self._report("portal-scope-missing")
        self.assertIn("PORTAL_RULE_SCOPE", self._blocker_codes(report))
        self.assertEqual(report["portal_rules"]["rule_scope"], "")

    def test_compatibility_warning_routes_clean_files_to_candidates(self) -> None:
        manifest = self._manifest()
        manifest["rules"]["compatibility_target_mb"] = "0.001"  # type: ignore[index]
        manifest_path = self._write_manifest(manifest)

        result = self._run("build", manifest_path, "compatibility-candidates")

        self._assert_code(result, 0)
        output = self.case_root / "compatibility-candidates"
        self.assertEqual(list((output / "SUBMIT").iterdir()), [])
        self.assertEqual(len(list((output / "CANDIDATE_UPLOADS").glob("*.pdf"))), 4)
        warnings = {
            item["code"] for item in self._report("compatibility-candidates")["warnings"]  # type: ignore[index]
        }
        self.assertIn("COMPATIBILITY_TARGET", warnings)

    def test_build_subdirectory_path_types_are_reported_without_traceback(self) -> None:
        manifest_path = self._write_manifest(self._manifest())
        for name in ("REVIEW_ONLY", "SUBMIT", "CANDIDATE_UPLOADS"):
            with self.subTest(name=name):
                output_name = f"path-type-{name.lower()}"
                output = self.case_root / output_name
                output.mkdir()
                (output / name).write_text("preserve", encoding="utf-8")

                result = self._run("build", manifest_path, output_name)

                self._assert_code(result, 2)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn(
                    "OUTPUT_PATH_TYPE", self._blocker_codes(self._report(output_name))
                )
                self.assertEqual((output / name).read_text(encoding="utf-8"), "preserve")

    def test_renamed_case_and_packs_cannot_accumulate_stale_outputs(self) -> None:
        manifest = self._manifest()
        manifest_path = self._write_manifest(manifest, "stale-first.json")
        first = self._run("build", manifest_path, "stale-build")
        self._assert_code(first, 0)
        output = self.case_root / "stale-build"
        old_pdfs = sorted(output.rglob("*.pdf"))
        old_hashes = {path: self._sha256(path) for path in old_pdfs}

        manifest["case"]["case_id"] = "synthetic-renamed-case"  # type: ignore[index]
        id_map = {
            "01-admin": "11-admin-renamed",
            "02-hospital": "12-hospital-renamed",
            "03-pre": "13-pre-renamed",
            "04-post": "14-post-renamed",
        }
        for pack in manifest["rules"]["pack_definitions"]:  # type: ignore[index]
            pack["id"] = id_map[pack["id"]]
        for document in manifest["documents"]:  # type: ignore[index]
            document["packs"] = [id_map[pack] for pack in document["packs"]]
        renamed_path = self._write_manifest(manifest, "stale-renamed.json")

        second = self._run("build", renamed_path, "stale-build")

        self._assert_code(second, 2)
        self.assertIn(
            "OUTPUT_DIRECTORY_NOT_EMPTY",
            self._blocker_codes(self._attempt_report("stale-build")),
        )
        self.assertEqual(old_hashes, {path: self._sha256(path) for path in old_pdfs})
        self.assertEqual(sorted(output.rglob("*.pdf")), old_pdfs)

    def test_audit_after_build_preserves_pdf_bound_inventory_report(self) -> None:
        manifest_path = self._write_manifest(self._manifest())
        first = self._run("build", manifest_path, "audit-after-build")
        self._assert_code(first, 0)
        output = self.case_root / "audit-after-build"
        canonical_json = (output / "claim-audit.json").read_bytes()
        canonical_markdown = (output / "claim-audit.md").read_bytes()

        later = self._run("audit", manifest_path, "audit-after-build")

        self._assert_code(later, 0)
        self.assertEqual(canonical_json, (output / "claim-audit.json").read_bytes())
        self.assertEqual(canonical_markdown, (output / "claim-audit.md").read_bytes())
        attempt = self._attempt_report("audit-after-build")
        self.assertEqual(attempt["outputs"], [])
        self.assertIn("claim-audit-attempt.md", later.stdout)

    def test_condition_flags_must_match_the_expense_ledger(self) -> None:
        cases = (
            ("ambulance-true-empty", "ambulance_claimed", True, None),
            ("ambulance-false-expense", "ambulance_claimed", False, "ambulance"),
            ("implant-false-expense", "implant", False, "implant"),
        )
        for label, flag, flag_value, expense_kind in cases:
            with self.subTest(label=label):
                manifest = self._manifest()
                manifest["conditions"][flag] = flag_value  # type: ignore[index]
                if expense_kind is not None:
                    manifest["expenses"].append(  # type: ignore[index]
                        {
                            "id": f"exp-{expense_kind}-conflict",
                            "phase": "hospitalization",
                            "kind": expense_kind,
                            "date": "2026-08-11",
                            "issuer": "Synthetic Service",
                            "invoice_number": f"{expense_kind.upper()}-CONFLICT",
                            "description": "Synthetic condition conflict",
                            "billed_amount": "10.00",
                            "claim_amount": "10.00",
                            "not_claimed_reason": "",
                        }
                    )
                    manifest["case"]["claimed_amount"] = "190.00"  # type: ignore[index]
                manifest_path = self._write_manifest(manifest, f"{label}.json")

                result = self._run("audit", manifest_path, label)

                self._assert_code(result, 2)
                self.assertIn(
                    "CONDITION_LEDGER_CONFLICT",
                    self._blocker_codes(self._report(label)),
                )

    def test_money_with_sub_paise_precision_is_rejected_not_rounded(self) -> None:
        cases = ("case", "expense")
        for label in cases:
            with self.subTest(label=label):
                manifest = self._manifest()
                if label == "case":
                    manifest["case"]["claimed_amount"] = "180.005"  # type: ignore[index]
                    expected = "CLAIM_TOTAL"
                else:
                    manifest["expenses"][0]["billed_amount"] = "100.005"  # type: ignore[index]
                    expected = "EXPENSE_AMOUNT"
                manifest_path = self._write_manifest(manifest, f"precision-{label}.json")

                result = self._run("audit", manifest_path, f"precision-{label}")

                self._assert_code(result, 2)
                self.assertIn(expected, self._blocker_codes(self._report(f"precision-{label}")))

    def test_dates_require_exact_extended_iso_format(self) -> None:
        manifest = self._manifest()
        manifest["expenses"][2]["date"] = "20260820"  # type: ignore[index]
        manifest_path = self._write_manifest(manifest)

        result = self._run("audit", manifest_path, "date-format")

        self._assert_code(result, 2)
        self.assertIn("EXPENSE_DATE", self._blocker_codes(self._report("date-format")))

    def test_partial_amounts_and_phase_subtotals_appear_in_review_artifacts(self) -> None:
        manifest = self._manifest()
        manifest["expenses"][0]["billed_amount"] = "120.00"  # type: ignore[index]
        manifest["expenses"][0]["not_claimed_reason"] = "Synthetic excluded line"  # type: ignore[index]
        manifest_path = self._write_manifest(manifest)

        result = self._run("build", manifest_path, "partial-review")

        self._assert_code(result, 0)
        output = self.case_root / "partial-review"
        markdown = (output / "claim-audit.md").read_text(encoding="utf-8")
        self.assertIn("Hospitalization subtotal: INR 100.00", markdown)
        self.assertIn("20.00", markdown)
        self.assertIn("Synthetic excluded line", markdown)
        master_path = next((output / "REVIEW_ONLY").glob("*.pdf"))
        master_text = "\n".join(
            page.extract_text() or "" for page in PdfReader(str(master_path)).pages
        )
        self.assertIn("Partial or excluded amounts", master_text)
        self.assertIn("Synthetic excluded line", master_text)
        self.assertIn("hospital-bill.pdf p.1", master_text)

    def test_help_works_without_loading_optional_pdf_dependencies(self) -> None:
        result = subprocess.run(
            [sys.executable, "-S", str(CLAIM_PACKET), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Audit or build", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
