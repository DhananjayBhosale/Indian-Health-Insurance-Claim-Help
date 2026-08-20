#!/usr/bin/env python3
"""Audit and build local PDF packets for hospitalization-linked health claims.

The manifest is authoritative. Source files are read-only; the program never
edits, deletes, decrypts, signs, annotates, or compresses them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable, NoReturn
from xml.sax.saxutils import escape

DEPENDENCY_ERROR: ModuleNotFoundError | None = None
try:
    from PIL import Image, ImageOps
    from pypdf import PdfReader, PdfWriter
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
except ModuleNotFoundError as exc:
    DEPENDENCY_ERROR = exc


SUPPORTED_SUFFIXES = {".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff"}
DOCUMENT_PHASES = {"administrative", "pre", "hospitalization", "post", "other"}
EXPENSE_PHASES = {"pre", "hospitalization", "post", "other"}
EXPENSE_KINDS = {
    "consultation",
    "diagnostic",
    "medicine",
    "hospital",
    "implant",
    "ambulance",
    "other",
}
EVIDENCE_ROLES = {
    "claim_form",
    "identity",
    "bank",
    "policy",
    "hospital_form",
    "hospital_registration",
    "discharge",
    "clinical_advice",
    "clinical_record",
    "clinical_result",
    "invoice",
    "payment_proof",
    "operation_record",
    "implant_identity",
    "accident_record",
    "death_record",
    "claimant_authority",
    "other_insurer_settlement",
    "maternity_record",
    "other",
}
DEFAULT_EXPENSE_ROLES = {
    "consultation": {"clinical_advice", "invoice", "payment_proof"},
    "diagnostic": {"clinical_advice", "clinical_result", "invoice", "payment_proof"},
    "medicine": {"clinical_advice", "invoice", "payment_proof"},
    "hospital": {"invoice", "payment_proof"},
    "implant": {"invoice", "payment_proof", "implant_identity"},
    "ambulance": {"invoice", "payment_proof"},
}
EVIDENCE_ROLE_LABELS = {
    "clinical_advice": "doctor advice, prescription, or referral",
    "clinical_record": "clinical or treatment record",
    "clinical_result": "complete diagnostic report or result",
    "invoice": "itemized bill or invoice",
    "payment_proof": "payment receipt or other paid proof",
    "operation_record": "operation note or surgeon record",
    "implant_identity": "implant sticker, barcode, or serial label",
}
CONDITION_ROLES = {
    "surgery": {"operation_record"},
    "implant": {"implant_identity"},
    "accident": {"accident_record"},
    "death_claim": {"death_record", "claimant_authority"},
    "non_network_hospital": {"hospital_registration"},
    "other_insurer_involved": {"other_insurer_settlement"},
    "maternity": {"maternity_record"},
}
CANONICAL_CONDITIONS = (*CONDITION_ROLES.keys(), "ambulance_claimed")
SUPPORTED_CLAIM_TYPES = {"hospitalization_reimbursement", "day_care_reimbursement"}


@dataclass
class SourceInfo:
    path: Path
    sha256: str
    page_count: int
    suffix: str
    digitally_signed: bool
    has_acroform: bool


@dataclass
class Selection:
    document: dict[str, Any]
    source: SourceInfo
    pages: list[int]  # zero-based
    manifest_path: str


def fail(message: str, code: int = 2) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit or build a private Indian health-claim PDF packet."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("audit", "build"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--manifest", required=True, type=Path)
        sub.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"manifest does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read manifest: {exc}")
    if not isinstance(payload, dict):
        fail("manifest root must be a JSON object")
    return payload


def prepare_output_dir(path: Path, case_root: Path) -> Path:
    expanded = path.expanduser()
    if expanded.is_symlink():
        fail(f"output directory must not be a symbolic link: {expanded}")
    resolved = expanded.resolve()
    resolved_case_root = case_root.resolve()
    if resolved == resolved_case_root or not resolved.is_relative_to(resolved_case_root):
        fail("output directory must be a strict descendant of the private manifest directory")
    if expanded.exists() and not expanded.is_dir():
        fail(f"output path exists and is not a directory: {expanded}")
    try:
        resolved.mkdir(parents=True, exist_ok=True)
        resolved.chmod(0o700)
    except OSError as exc:
        fail(f"cannot prepare output directory: {exc}")
    return resolved


def refuse_symlink(path: Path, purpose: str) -> None:
    """Refuse a path entry that could redirect a private output elsewhere."""
    if path.is_symlink():
        fail(f"{purpose} must not be a symbolic link: {path}")


def secure_replace(path: Path, payload: bytes) -> None:
    """Atomically replace a private report without following a target symlink."""
    refuse_symlink(path, "output file")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
        path.chmod(0o600)
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        temporary_path.unlink(missing_ok=True)
        raise


def secure_write_new(path: Path, payload: bytes) -> None:
    """Create a private output exactly once; never follow or replace a link."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    created = True
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        created = False
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        if created:
            path.unlink(missing_ok=True)
        raise


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pdf_has_applied_signature(reader: PdfReader) -> bool:
    try:
        fields = reader.get_fields() or {}
    except Exception:
        fields = {}
    for field in fields.values():
        if str(field.get("/FT", "")) == "/Sig" and field.get("/V") is not None:
            return True
    for page in reader.pages:
        try:
            annotations = page.get("/Annots") or []
            for reference in annotations:
                annotation = reference.get_object()
                parent = annotation.get("/Parent")
                effective = parent.get_object() if parent is not None else annotation
                if str(effective.get("/FT", "")) == "/Sig" and effective.get("/V") is not None:
                    return True
        except Exception:
            continue
    return False


def inspect_source(path: Path) -> SourceInfo:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"unsupported source type: {suffix or '(none)'}")
    digest = sha256_file(path)
    if suffix == ".pdf":
        reader = PdfReader(str(path), strict=False)
        if reader.is_encrypted:
            raise ValueError("encrypted/password-protected PDF; do not decrypt automatically")
        page_count = len(reader.pages)
        if page_count < 1:
            raise ValueError("PDF contains no pages")
        signed = pdf_has_applied_signature(reader)
        try:
            root = reader.trailer["/Root"]
            acroform = root.get("/AcroForm")
            acroform_object = acroform.get_object() if acroform is not None else None
            has_acroform = bool(
                acroform_object
                and (
                    acroform_object.get("/Fields")
                    or acroform_object.get("/XFA")
                )
            )
        except Exception:
            has_acroform = False
        return SourceInfo(path, digest, page_count, suffix, signed, has_acroform)

    with Image.open(path) as image:
        page_count = int(getattr(image, "n_frames", 1))
        if page_count < 1:
            raise ValueError("image contains no frames")
        image.seek(0)
        image.load()
    return SourceInfo(path, digest, page_count, suffix, False, False)


def parse_page_spec(spec: Any, page_count: int) -> list[int]:
    if spec is None or spec == "":
        return list(range(page_count))
    raw_items: list[Any]
    if isinstance(spec, int):
        raw_items = [spec]
    elif isinstance(spec, list):
        raw_items = spec
    elif isinstance(spec, str):
        raw_items = [item.strip() for item in spec.split(",") if item.strip()]
    else:
        raise ValueError("pages must be null, an integer, a list, or a range string")

    selected: list[int] = []
    for item in raw_items:
        if isinstance(item, int):
            numbers = [item]
        else:
            text = str(item).strip()
            match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", text)
            if match:
                start, end = int(match.group(1)), int(match.group(2))
                if end < start:
                    raise ValueError(f"descending page range is not allowed: {text}")
                numbers = list(range(start, end + 1))
            elif text.isdigit():
                numbers = [int(text)]
            else:
                raise ValueError(f"invalid page selection: {text!r}")
        for number in numbers:
            if number < 1 or number > page_count:
                raise ValueError(f"page {number} is outside 1-{page_count}")
            index = number - 1
            if index in selected:
                raise ValueError(f"page {number} is selected more than once")
            selected.append(index)
    if not selected:
        raise ValueError("page selection must include at least one page")
    return selected


def decimal_value(value: Any, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field} must be a decimal value") from None
    if not result.is_finite() or result < 0:
        raise ValueError(f"{field} must be a non-negative finite decimal")
    try:
        quantized = result.quantize(Decimal("0.01"))
    except InvalidOperation:
        raise ValueError(f"{field} is too large or precise to represent safely") from None
    if quantized != result:
        raise ValueError(f"{field} must not contain fractions smaller than 0.01")
    return quantized


def iso_date(value: Any, field: str) -> date | None:
    if value in (None, ""):
        return None
    text = str(value)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise ValueError(f"{field} must use YYYY-MM-DD")
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise ValueError(f"{field} must use YYYY-MM-DD") from None


def list_of_strings(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of strings")
    return value


def issue(report: dict[str, Any], level: str, code: str, message: str, **refs: Any) -> None:
    item = {"code": code, "message": message}
    item.update({key: value for key, value in refs.items() if value not in (None, "")})
    report["blockers" if level == "blocker" else "warnings"].append(item)


def issue_once(
    report: dict[str, Any], level: str, code: str, message: str, **refs: Any
) -> None:
    bucket = report["blockers" if level == "blocker" else "warnings"]
    if any(item.get("code") == code and item.get("message") == message for item in bucket):
        return
    issue(report, level, code, message, **refs)


def page_spec_text(pages: Iterable[int]) -> str:
    numbers = [number + 1 for number in pages]
    if not numbers:
        return ""
    ranges: list[str] = []
    start = previous = numbers[0]
    for number in numbers[1:]:
        if number == previous + 1:
            previous = number
            continue
        ranges.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = number
    ranges.append(str(start) if start == previous else f"{start}-{previous}")
    return ",".join(ranges)


def audit_manifest(
    manifest: dict[str, Any], manifest_path: Path
) -> tuple[dict[str, Any], list[Selection]]:
    report: dict[str, Any] = {
        "audit_schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_id": "unnamed-case",
        "status": "NOT_READY",
        "blockers": [],
        "warnings": [],
        "totals": {},
        "expenses": [],
        "documents": [],
        "outputs": [],
    }

    if manifest.get("schema_version") != 1:
        issue(report, "blocker", "SCHEMA_VERSION", "schema_version must equal 1")

    case = manifest.get("case")
    verification = manifest.get("verification")
    conditions = manifest.get("conditions")
    rules = manifest.get("rules")
    expenses = manifest.get("expenses")
    documents = manifest.get("documents")
    for name, value, expected in (
        ("case", case, dict),
        ("verification", verification, dict),
        ("conditions", conditions, dict),
        ("rules", rules, dict),
        ("expenses", expenses, list),
        ("documents", documents, list),
    ):
        if not isinstance(value, expected):
            issue(report, "blocker", "SCHEMA_SECTION", f"{name} must be a {expected.__name__}")

    case = case if isinstance(case, dict) else {}
    verification = verification if isinstance(verification, dict) else {}
    conditions = conditions if isinstance(conditions, dict) else {}
    rules = rules if isinstance(rules, dict) else {}
    expenses = expenses if isinstance(expenses, list) else []
    documents = documents if isinstance(documents, list) else []

    for condition in CANONICAL_CONDITIONS:
        if condition not in conditions:
            issue(
                report,
                "blocker",
                "CONDITION_UNVERIFIED",
                f"conditions.{condition} must be answered explicitly",
            )
        elif not isinstance(conditions[condition], bool):
            issue(
                report,
                "blocker",
                "CONDITION_TYPE",
                f"conditions.{condition} must be true or false",
            )

    case_id = str(case.get("case_id", "")).strip()
    if not case_id:
        issue(report, "blocker", "CASE_ID", "case.case_id is required")
        case_id = "unnamed-case"
    report["case_id"] = case_id

    for field in ("insurer", "product", "uin", "patient_name", "policy_reference"):
        if not str(case.get(field, "")).strip():
            issue(
                report,
                "blocker",
                "CASE_IDENTITY",
                f"case.{field} is required for a traceable hospitalization claim",
            )

    claim_type = str(case.get("claim_type", "")).strip()
    case["claim_type"] = claim_type
    if claim_type not in SUPPORTED_CLAIM_TYPES:
        issue(
            report,
            "blocker",
            "UNSUPPORTED_CLAIM_TYPE",
            "claim_type must be hospitalization_reimbursement or day_care_reimbursement",
        )
    claim_route = str(case.get("claim_route", "")).strip()
    case["claim_route"] = claim_route
    if not claim_route:
        issue(report, "warning", "CLAIM_ROUTE_UNVERIFIED", "case.claim_route is not recorded")
    if not str(case.get("submission_channel", "")).strip():
        issue(
            report,
            "warning",
            "SUBMISSION_CHANNEL_UNVERIFIED",
            "case.submission_channel is not recorded",
        )

    try:
        admission_date = iso_date(case.get("admission_date"), "case.admission_date")
        discharge_date = iso_date(case.get("discharge_date"), "case.discharge_date")
        if not admission_date or not discharge_date:
            issue(
                report,
                "blocker",
                "CASE_DATES",
                "admission and discharge dates are required",
            )
        if admission_date and discharge_date and discharge_date < admission_date:
            issue(report, "blocker", "CASE_DATES", "discharge date precedes admission date")
    except ValueError as exc:
        admission_date = discharge_date = None
        issue(report, "blocker", "CASE_DATES", str(exc))

    portal_confirmed = verification.get("portal_rules_confirmed") is True
    if not portal_confirmed:
        issue(
            report,
            "warning",
            "PORTAL_RULES_UNVERIFIED",
            "live portal file rules and categories are not confirmed",
        )

    portal = verification.get("portal")
    if not isinstance(portal, dict):
        portal = {}
        issue(report, "warning", "PORTAL_SCHEMA", "verification.portal is not recorded")
    portal_rule_scope = str(portal.get("rule_scope", "")).strip()
    if portal_confirmed and not portal_rule_scope:
        issue(
            report,
            "blocker",
            "PORTAL_RULE_SCOPE",
            "portal rules are marked confirmed but verification.portal.rule_scope does not identify the checked journey or screen",
        )
    accepted_types = portal.get("accepted_file_types")
    try:
        accepted_types_list = [
            item.strip().lower().lstrip(".")
            for item in list_of_strings(accepted_types, "accepted_file_types")
            if item.strip()
        ]
    except ValueError as exc:
        accepted_types_list = []
        issue(report, "blocker", "PORTAL_FILE_TYPES", str(exc))
    if portal_confirmed and not accepted_types_list:
        issue(
            report,
            "blocker",
            "PORTAL_FILE_TYPES",
            "portal rules are marked confirmed but no accepted file types are recorded",
        )
    if portal_confirmed and accepted_types_list and "pdf" not in accepted_types_list:
        issue(report, "blocker", "PDF_NOT_ACCEPTED", "confirmed portal does not list PDF as accepted")
    try:
        unpublished_rules = {
            item.strip()
            for item in list_of_strings(
                portal.get("unpublished_rules"), "portal.unpublished_rules"
            )
            if item.strip()
        }
    except ValueError as exc:
        unpublished_rules = set()
        issue(report, "blocker", "PORTAL_LIMIT_STATUS", str(exc))
    limit_fields = {"max_file_mb", "max_total_mb", "max_files"}
    unknown_unpublished = sorted(unpublished_rules - limit_fields)
    if unknown_unpublished:
        issue(
            report,
            "blocker",
            "PORTAL_LIMIT_STATUS",
            f"unknown unpublished portal rules: {', '.join(unknown_unpublished)}",
        )
    if portal_confirmed:
        for field in sorted(limit_fields):
            value = portal.get(field)
            marked_unpublished = field in unpublished_rules
            if value in (None, "") and not marked_unpublished:
                issue(
                    report,
                    "blocker",
                    "PORTAL_LIMIT_STATUS",
                    f"portal.{field} is null but not recorded in unpublished_rules",
                )
            if value not in (None, "") and marked_unpublished:
                issue(
                    report,
                    "blocker",
                    "PORTAL_LIMIT_STATUS",
                    f"portal.{field} has a value but is also marked unpublished",
                )

    report["portal_rules"] = {
        "confirmed": portal_confirmed,
        "rule_scope": portal_rule_scope,
        "accepted_file_types": accepted_types_list,
        "max_file_mb": portal.get("max_file_mb"),
        "max_total_mb": portal.get("max_total_mb"),
        "max_files": portal.get("max_files"),
        "unpublished_rules": sorted(unpublished_rules),
        "authority_url": str(portal.get("authority_url", "")).strip(),
    }

    for url_field in ("official_claim_form_url", "official_policy_url", "portal_rules_url"):
        if not str(verification.get(url_field, "")).strip():
            issue(report, "warning", "AUTHORITY_URL", f"verification.{url_field} is not recorded")

    try:
        checked_on = iso_date(verification.get("checked_on"), "verification.checked_on")
        if not checked_on:
            issue(
                report,
                "blocker",
                "VERIFICATION_DATE",
                "verification.checked_on is required",
            )
        elif checked_on > date.today():
            issue(
                report,
                "warning",
                "VERIFICATION_DATE",
                "verification.checked_on is in the future",
            )
    except ValueError as exc:
        issue(report, "blocker", "VERIFICATION_DATE", str(exc))

    coverage = verification.get("coverage_window")
    coverage = coverage if isinstance(coverage, dict) else {}
    coverage_dates: dict[str, date | None] = {}
    for key in ("pre_start", "pre_end", "post_start", "post_end"):
        try:
            coverage_dates[key] = iso_date(coverage.get(key), f"coverage_window.{key}")
        except ValueError as exc:
            coverage_dates[key] = None
            issue(report, "blocker", "COVERAGE_DATE", str(exc))
    if coverage_dates.get("pre_start") and coverage_dates.get("pre_end"):
        if coverage_dates["pre_end"] < coverage_dates["pre_start"]:  # type: ignore[operator]
            issue(report, "blocker", "COVERAGE_DATE", "pre coverage end precedes start")
    if coverage_dates.get("post_start") and coverage_dates.get("post_end"):
        if coverage_dates["post_end"] < coverage_dates["post_start"]:  # type: ignore[operator]
            issue(report, "blocker", "COVERAGE_DATE", "post coverage end precedes start")

    deadlines = verification.get("filing_deadlines")
    deadlines = deadlines if isinstance(deadlines, dict) else {}
    deadline_dates: dict[str, date | None] = {}
    for key in ("hospitalization_and_pre_due", "post_due"):
        try:
            due = iso_date(deadlines.get(key), f"filing_deadlines.{key}")
            deadline_dates[key] = due
            if due and due < date.today():
                issue(
                    report,
                    "warning",
                    "FILING_DATE_PASSED",
                    f"recorded {key} has passed; verify late-filing instructions without inventing a reason",
                )
        except ValueError as exc:
            deadline_dates[key] = None
            issue(report, "blocker", "FILING_DATE", str(exc))

    pack_definitions = rules.get("pack_definitions")
    if not isinstance(pack_definitions, list):
        pack_definitions = []
        issue(report, "blocker", "PACK_DEFINITIONS", "rules.pack_definitions must be a list")
    pack_map: dict[str, dict[str, Any]] = {}
    slug_to_pack: dict[str, str] = {}
    for entry in pack_definitions:
        if not isinstance(entry, dict) or not str(entry.get("id", "")).strip():
            issue(report, "blocker", "PACK_DEFINITION", "every pack definition needs an id")
            continue
        pack_id = str(entry["id"]).strip()
        entry["id"] = pack_id
        if pack_id in pack_map:
            issue(report, "blocker", "PACK_DEFINITION", f"duplicate pack definition: {pack_id}")
        if not str(entry.get("label", "")).strip():
            issue(report, "blocker", "PACK_DEFINITION", f"pack {pack_id} needs a label")
        pack_slug = slugify(pack_id)
        if pack_slug in slug_to_pack and slug_to_pack[pack_slug] != pack_id:
            issue(
                report,
                "blocker",
                "PACK_FILENAME_COLLISION",
                f"pack ids {slug_to_pack[pack_slug]!r} and {pack_id!r} map to the same filename",
            )
        slug_to_pack[pack_slug] = pack_id
        pack_map[pack_id] = entry

    expense_map: dict[str, dict[str, Any]] = {}
    expense_amounts: dict[str, tuple[Decimal, Decimal]] = {}
    duplicate_events: dict[tuple[str, str, str, str], tuple[str, str]] = {}
    total_claimed = Decimal("0.00")
    phases_total: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    if not expenses:
        issue(report, "blocker", "NO_EXPENSES", "at least one claimed expense is required")
    for index, raw_expense in enumerate(expenses, start=1):
        if not isinstance(raw_expense, dict):
            issue(report, "blocker", "EXPENSE_SCHEMA", f"expense {index} must be an object")
            continue
        expense = raw_expense
        expense_id = str(expense.get("id", "")).strip()
        if not expense_id:
            issue(report, "blocker", "EXPENSE_ID", f"expense {index} has no id")
            continue
        if expense_id in expense_map:
            issue(report, "blocker", "EXPENSE_ID", f"duplicate expense id: {expense_id}")
            continue
        expense["id"] = expense_id
        expense_map[expense_id] = expense
        phase = str(expense.get("phase", "")).strip()
        kind = str(expense.get("kind", "")).strip()
        expense["phase"] = phase
        expense["kind"] = kind
        if phase not in EXPENSE_PHASES:
            issue(report, "blocker", "EXPENSE_PHASE", f"invalid expense phase: {phase}", expense_id=expense_id)
        if kind not in EXPENSE_KINDS:
            issue(report, "blocker", "EXPENSE_KIND", f"invalid expense kind: {kind}", expense_id=expense_id)
        for field in ("issuer", "invoice_number", "description"):
            if not str(expense.get(field, "")).strip():
                issue(
                    report,
                    "blocker",
                    "EXPENSE_DETAIL",
                    f"expense {expense_id} requires {field}",
                    expense_id=expense_id,
                )
        try:
            billed = decimal_value(expense.get("billed_amount"), f"expense {expense_id} billed_amount")
            claimed = decimal_value(expense.get("claim_amount"), f"expense {expense_id} claim_amount")
            expense_amounts[expense_id] = (billed, claimed)
            total_claimed += claimed
            phases_total[phase] += claimed
            if claimed > billed:
                issue(report, "blocker", "CLAIM_EXCEEDS_BILL", "claim amount exceeds billed amount", expense_id=expense_id)
            if claimed < billed and not str(expense.get("not_claimed_reason", "")).strip():
                issue(
                    report,
                    "blocker",
                    "PARTIAL_CLAIM_REASON",
                    "billed and claimed amounts differ without a not_claimed_reason",
                    expense_id=expense_id,
                )
        except ValueError as exc:
            billed = claimed = Decimal("0.00")
            issue(report, "blocker", "EXPENSE_AMOUNT", str(exc), expense_id=expense_id)
        try:
            expense_date = iso_date(expense.get("date"), f"expense {expense_id} date")
            if not expense_date:
                issue(
                    report,
                    "blocker",
                    "EXPENSE_DATE",
                    "expense date is required",
                    expense_id=expense_id,
                )
        except ValueError as exc:
            expense_date = None
            issue(report, "blocker", "EXPENSE_DATE", str(exc), expense_id=expense_id)
        if phase == "pre" and expense_date:
            start, end = coverage_dates.get("pre_start"), coverage_dates.get("pre_end")
            if start and end and not (start <= expense_date <= end):
                issue(report, "warning", "OUTSIDE_CONFIGURED_WINDOW", "pre expense date is outside the configured policy window", expense_id=expense_id)
        if phase == "post" and expense_date:
            start, end = coverage_dates.get("post_start"), coverage_dates.get("post_end")
            if start and end and not (start <= expense_date <= end):
                issue(report, "warning", "OUTSIDE_CONFIGURED_WINDOW", "post expense date is outside the configured policy window", expense_id=expense_id)
        event_key = (
            str(expense.get("issuer", "")).strip().casefold(),
            str(expense.get("invoice_number", "")).strip().casefold(),
            str(expense.get("date", "")),
            str(billed),
        )
        if event_key in duplicate_events:
            previous_id, previous_phase = duplicate_events[event_key]
            issue(
                report,
                "blocker",
                "DUPLICATE_FINANCIAL_EVENT",
                f"possible duplicate of expense {previous_id} classified as {previous_phase}",
                expense_id=expense_id,
            )
        else:
            duplicate_events[event_key] = (expense_id, phase)
        report["expenses"].append(
            {
                "id": expense_id,
                "phase": phase,
                "kind": kind,
                "date": str(expense.get("date", "")),
                "issuer": str(expense.get("issuer", "")),
                "invoice_number": str(expense.get("invoice_number", "")),
                "description": str(expense.get("description", "")),
                "billed_amount": f"{billed:.2f}",
                "claim_amount": f"{claimed:.2f}",
                "not_claimed_amount": f"{(billed - claimed):.2f}",
                "not_claimed_reason": str(expense.get("not_claimed_reason", "")),
                "currency": str(case.get("currency", "INR")),
            }
        )

    try:
        case_claimed = decimal_value(case.get("claimed_amount"), "case.claimed_amount")
        if case_claimed != total_claimed:
            issue(
                report,
                "blocker",
                "CLAIM_TOTAL_MISMATCH",
                f"case total {case_claimed:.2f} does not equal expense total {total_claimed:.2f}",
            )
    except ValueError as exc:
        case_claimed = Decimal("0.00")
        issue(report, "blocker", "CLAIM_TOTAL", str(exc))
    report["totals"] = {
        "currency": str(case.get("currency", "INR")),
        "case_claimed_amount": f"{case_claimed:.2f}",
        "expense_claimed_amount": f"{total_claimed:.2f}",
        "by_phase": {key: f"{value:.2f}" for key, value in sorted(phases_total.items())},
    }

    has_pre = any(expense.get("phase") == "pre" for expense in expense_map.values())
    has_post = any(expense.get("phase") == "post" for expense in expense_map.values())
    if has_pre and not (coverage_dates.get("pre_start") and coverage_dates.get("pre_end")):
        issue(report, "blocker", "POLICY_WINDOW_UNVERIFIED", "pre-hospitalization coverage dates are not recorded")
    if has_post and not (coverage_dates.get("post_start") and coverage_dates.get("post_end")):
        issue(report, "blocker", "POLICY_WINDOW_UNVERIFIED", "post-hospitalization coverage dates are not recorded")
    if (
        has_pre
        or any(expense.get("phase") == "hospitalization" for expense in expense_map.values())
    ) and not deadline_dates.get("hospitalization_and_pre_due"):
        issue(
            report,
            "blocker",
            "FILING_DEADLINE_UNVERIFIED",
            "hospitalization/pre filing deadline is not recorded",
        )
    if has_post and not deadline_dates.get("post_due"):
        issue(report, "blocker", "FILING_DEADLINE_UNVERIFIED", "post filing deadline is not recorded")
    if (has_pre or has_post) and not str(coverage.get("authority_url", "")).strip():
        issue(report, "warning", "AUTHORITY_URL", "coverage-window authority URL is not recorded")
    if not str(deadlines.get("authority_url", "")).strip():
        issue(report, "warning", "AUTHORITY_URL", "filing-deadline authority URL is not recorded")
    if (has_pre or has_post) and claim_route == "supplementary_pre_post" and not str(case.get("main_claim_reference", "")).strip():
        issue(report, "blocker", "MAIN_CLAIM_REFERENCE", "supplementary pre/post route needs main_claim_reference")

    source_cache: dict[Path, SourceInfo] = {}
    selections: list[Selection] = []
    document_ids: set[str] = set()
    selected_by_source: dict[Path, list[tuple[str, str, set[int]]]] = defaultdict(list)
    hashes_to_paths: dict[str, set[Path]] = defaultdict(set)
    manifest_root = manifest_path.resolve().parent
    try:
        source_root_entries = [
            item.strip()
            for item in list_of_strings(rules.get("source_roots"), "source_roots")
            if item.strip()
        ]
    except ValueError as exc:
        source_root_entries = []
        issue(report, "blocker", "SOURCE_ROOTS", str(exc))
    if not source_root_entries:
        issue(
            report,
            "blocker",
            "SOURCE_ROOTS",
            "rules.source_roots must list every private input directory",
        )
    source_roots: list[Path] = []
    for raw_root in source_root_entries:
        candidate = Path(raw_root).expanduser()
        if not candidate.is_absolute():
            candidate = manifest_root / candidate
        if candidate.is_symlink():
            issue(
                report,
                "blocker",
                "SOURCE_ROOT_SYMLINK",
                "source root must not be a symbolic link",
            )
            continue
        resolved_root = candidate.resolve()
        if resolved_root == manifest_root or not resolved_root.is_relative_to(manifest_root):
            issue(
                report,
                "blocker",
                "SOURCE_ROOT_SCOPE",
                "source root must be a strict descendant of the private case directory",
            )
            continue
        if not resolved_root.is_dir():
            issue(
                report,
                "blocker",
                "SOURCE_ROOT_MISSING",
                f"source root is missing or not a directory: {raw_root}",
            )
            continue
        if resolved_root not in source_roots:
            source_roots.append(resolved_root)

    if not documents:
        issue(report, "blocker", "NO_DOCUMENTS", "at least one source document is required")
    for index, raw_document in enumerate(documents, start=1):
        if not isinstance(raw_document, dict):
            issue(report, "blocker", "DOCUMENT_SCHEMA", f"document {index} must be an object")
            continue
        document = raw_document
        document_id = str(document.get("id", "")).strip()
        if not document_id:
            issue(report, "blocker", "DOCUMENT_ID", f"document {index} has no id")
            continue
        if document_id in document_ids:
            issue(report, "blocker", "DOCUMENT_ID", f"duplicate document id: {document_id}")
            continue
        document["id"] = document_id
        document_ids.add(document_id)
        decision = str(document.get("decision", "")).strip()
        document["decision"] = decision
        included = decision == "include"
        if decision not in {"include", "exclude"}:
            issue(report, "blocker", "DOCUMENT_DECISION", "decision must be include or exclude", document_id=document_id)
        if decision == "exclude" and not str(document.get("exclusion_reason", "")).strip():
            issue(report, "blocker", "EXCLUSION_REASON", "excluded document needs a reason", document_id=document_id)
        phase = str(document.get("phase", "")).strip()
        document["phase"] = phase
        if phase not in DOCUMENT_PHASES:
            issue(report, "blocker", "DOCUMENT_PHASE", f"invalid document phase: {phase}", document_id=document_id)
        try:
            roles = [
                item.strip()
                for item in list_of_strings(document.get("evidence_roles"), "evidence_roles")
                if item.strip()
            ]
            document["evidence_roles"] = roles
            unknown_roles = sorted(set(roles) - EVIDENCE_ROLES)
            if unknown_roles:
                issue(report, "blocker", "EVIDENCE_ROLE", f"unknown roles: {', '.join(unknown_roles)}", document_id=document_id)
            if included and not roles:
                issue(report, "warning", "EVIDENCE_ROLE", "included document has no evidence roles", document_id=document_id)
        except ValueError as exc:
            roles = []
            issue(report, "blocker", "EVIDENCE_ROLE", str(exc), document_id=document_id)
        try:
            expense_ids = [
                item.strip()
                for item in list_of_strings(document.get("expense_ids"), "expense_ids")
                if item.strip()
            ]
            packs = [
                item.strip()
                for item in list_of_strings(document.get("packs"), "packs")
                if item.strip()
            ]
            document["expense_ids"] = expense_ids
            document["packs"] = packs
        except ValueError as exc:
            expense_ids = []
            packs = []
            issue(report, "blocker", "DOCUMENT_LIST", str(exc), document_id=document_id)
        for expense_id in expense_ids:
            if expense_id not in expense_map:
                issue(report, "blocker", "UNKNOWN_EXPENSE", f"unknown expense id: {expense_id}", document_id=document_id)
        for pack_id in packs:
            if pack_id not in pack_map:
                issue(report, "blocker", "UNKNOWN_PACK", f"pack is not defined: {pack_id}", document_id=document_id)
        if included and not packs:
            issue(report, "warning", "NO_SUBMIT_PACK", "included document appears only in the review master", document_id=document_id)
        if included and not str(document.get("document_type", "")).strip():
            issue(report, "blocker", "DOCUMENT_TYPE", "included document needs document_type", document_id=document_id)
        if included and not str(document.get("original_status", "")).strip():
            issue(report, "warning", "ORIGINAL_STATUS", "included document has no original_status", document_id=document_id)
        delivery_mode = str(document.get("delivery_mode", "assemble")).strip()
        document["delivery_mode"] = delivery_mode
        if delivery_mode not in {"assemble", "standalone"}:
            issue(
                report,
                "blocker",
                "DELIVERY_MODE",
                "delivery_mode must be assemble or standalone",
                document_id=document_id,
            )
        try:
            iso_date(document.get("date"), f"document {document_id} date")
        except ValueError as exc:
            issue(report, "blocker", "DOCUMENT_DATE", str(exc), document_id=document_id)

        raw_path = str(document.get("path", "")).strip()
        if not raw_path:
            issue(report, "blocker", "DOCUMENT_PATH", "document path is required", document_id=document_id)
            continue
        path = Path(raw_path).expanduser()
        if not path.is_absolute():
            path = manifest_root / path
        path = path.resolve()
        if not source_roots:
            issue(
                report,
                "blocker",
                "SOURCE_ROOTS_UNAVAILABLE",
                "document was not inspected because no valid source root is available",
                document_id=document_id,
            )
            continue
        if not any(path.is_relative_to(root) for root in source_roots):
            issue(
                report,
                "blocker",
                "SOURCE_OUTSIDE_ROOTS",
                "document path is outside rules.source_roots",
                document_id=document_id,
            )
            continue
        if not path.is_file():
            issue(
                report,
                "blocker" if included else "warning",
                "SOURCE_MISSING",
                "source file is missing",
                document_id=document_id,
            )
            continue
        try:
            source = source_cache.get(path)
            if source is None:
                source = inspect_source(path)
                source_cache[path] = source
            selected_pages = parse_page_spec(document.get("pages"), source.page_count)
        except Exception as exc:
            issue(
                report,
                "blocker" if included else "warning",
                "SOURCE_INVALID",
                str(exc),
                document_id=document_id,
            )
            continue
        if included and (source.digitally_signed or source.has_acroform) and delivery_mode != "standalone":
            protected_kind = "digitally signed" if source.digitally_signed else "interactive-form"
            issue(
                report,
                "blocker",
                "PROTECTED_PDF_STANDALONE",
                f"{protected_kind} PDF must use delivery_mode standalone so its original bytes are preserved",
                document_id=document_id,
            )
        if included and delivery_mode == "standalone":
            if source.suffix != ".pdf":
                issue(
                    report,
                    "blocker",
                    "STANDALONE_SOURCE_TYPE",
                    "standalone delivery currently supports PDF sources only",
                    document_id=document_id,
                )
            if selected_pages != list(range(source.page_count)):
                issue(
                    report,
                    "blocker",
                    "STANDALONE_PAGE_SELECTION",
                    "standalone delivery must preserve every source page",
                    document_id=document_id,
                )
            if len(packs) != 1:
                issue(
                    report,
                    "blocker",
                    "STANDALONE_PACK",
                    "standalone delivery must map to exactly one upload pack",
                    document_id=document_id,
                )
        expected_hash = str(document.get("expected_sha256", "")).strip().lower()
        if expected_hash and expected_hash != source.sha256:
            issue(report, "blocker", "HASH_MISMATCH", "source SHA-256 differs from expected_sha256", document_id=document_id)
        hashes_to_paths[source.sha256].add(path)
        selected_by_source[path].append((document_id, decision, set(selected_pages)))
        selection = Selection(document, source, selected_pages, raw_path)
        selections.append(selection)
        report["documents"].append(
            {
                "id": document_id,
                "decision": decision,
                "source": raw_path,
                "source_pages": page_spec_text(selected_pages),
                "page_count": len(selected_pages),
                "sha256": source.sha256,
                "phase": phase,
                "document_type": str(document.get("document_type", "")),
                "date": str(document.get("date", "")),
                "expense_ids": expense_ids,
                "evidence_roles": roles,
                "packs": packs,
                "delivery_mode": delivery_mode,
                "digitally_signed": source.digitally_signed,
                "interactive_form": source.has_acroform,
                "original_status": str(document.get("original_status", "")),
                "exclusion_reason": str(document.get("exclusion_reason", "")),
            }
        )

    manifested_paths = set(selected_by_source)
    for source_root in source_roots:
        for candidate in source_root.rglob("*"):
            if candidate.is_symlink():
                issue(
                    report,
                    "blocker",
                    "SOURCE_SYMLINK",
                    "source roots must contain copies, not symbolic links",
                )
                continue
            if not candidate.is_file() or candidate.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            resolved_candidate = candidate.resolve()
            if resolved_candidate not in manifested_paths:
                try:
                    display_path = str(candidate.relative_to(manifest_root))
                except ValueError:
                    display_path = candidate.name
                issue(
                    report,
                    "blocker",
                    "UNMANIFESTED_SOURCE_FILE",
                    f"supported input file has no include/exclude manifest row: {display_path}",
                )

    for digest, paths in hashes_to_paths.items():
        if len(paths) > 1:
            issue(report, "warning", "EXACT_FILE_DUPLICATE", f"same SHA-256 appears at {len(paths)} source paths: {digest[:12]}")

    for path, rows in selected_by_source.items():
        covered: set[int] = set()
        included_seen: set[int] = set()
        excluded_seen: set[int] = set()
        for document_id, decision, pages in rows:
            overlap = covered & pages
            if overlap:
                issue(
                    report,
                    "blocker",
                    "OVERLAPPING_SOURCE_PAGES",
                    f"source pages overlap another manifest row: {page_spec_text(sorted(overlap))}",
                    document_id=document_id,
                )
            covered |= pages
            if decision == "include":
                included_seen |= pages
            else:
                excluded_seen |= pages
        contradiction = included_seen & excluded_seen
        if contradiction:
            issue(report, "blocker", "INCLUDE_EXCLUDE_CONFLICT", f"source pages are both included and excluded: {page_spec_text(sorted(contradiction))}")
        page_count = source_cache[path].page_count
        unaccounted = set(range(page_count)) - covered
        if unaccounted:
            issue(
                report,
                "blocker",
                "UNACCOUNTED_SOURCE_PAGES",
                f"referenced source has pages with no include/exclude decision: {page_spec_text(sorted(unaccounted))}",
            )

    roles_by_expense: dict[str, set[str]] = defaultdict(set)
    evidence_by_expense: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_included_roles: set[str] = set()
    included_selections = [item for item in selections if item.document.get("decision") == "include"]
    if not included_selections:
        issue(report, "blocker", "NO_INCLUDED_DOCUMENTS", "no source documents are included")
    for selection in included_selections:
        roles = set(selection.document.get("evidence_roles") or [])
        all_included_roles |= roles
        for expense_id in selection.document.get("expense_ids") or []:
            linked_expense_id = str(expense_id)
            roles_by_expense[linked_expense_id] |= roles
            evidence_by_expense[linked_expense_id].append(
                {
                    "document_id": str(selection.document.get("id", "")),
                    "source": selection.manifest_path,
                    "pages": page_spec_text(selection.pages),
                    "document_type": str(selection.document.get("document_type", "")),
                    "evidence_roles": sorted(roles),
                }
            )

    expense_report_by_id = {
        str(item.get("id", "")): item for item in report.get("expenses", [])
    }

    for expense_id, expense in expense_map.items():
        kind = str(expense.get("kind", ""))
        if kind == "other":
            try:
                required = set(list_of_strings(expense.get("required_roles"), "required_roles"))
            except ValueError as exc:
                required = set()
                issue(report, "blocker", "EXPENSE_REQUIRED_ROLES", str(exc), expense_id=expense_id)
            if not required:
                issue(report, "warning", "EXPENSE_REQUIRED_ROLES", "other expense has no required_roles", expense_id=expense_id)
        else:
            required = DEFAULT_EXPENSE_ROLES.get(kind, set())
        missing = sorted(required - roles_by_expense.get(expense_id, set()))
        expense_report = expense_report_by_id.get(expense_id, {})
        expense_report["linked_evidence"] = evidence_by_expense.get(expense_id, [])
        expense_report["missing_evidence_roles"] = missing
        expense_report["missing_evidence"] = [
            expense_evidence_label(role, expense_report) for role in missing
        ]
        if missing:
            missing_labels = ", ".join(
                expense_evidence_label(role, expense_report) for role in missing
            )
            issue(
                report,
                "blocker",
                "MISSING_EXPENSE_EVIDENCE",
                f"{expense_match_reference(expense_report)}. Missing: {missing_labels}. "
                "Add the missing document, or identify the exact source file and page(s) already supplied so they can be linked to this expense.",
                expense_id=expense_id,
                missing_roles=missing,
            )
        if kind == "implant" and not (
            roles_by_expense.get(expense_id, set())
            & {"clinical_record", "operation_record"}
        ):
            issue(
                report,
                "blocker",
                "MISSING_EXPENSE_EVIDENCE",
                "implant expense needs linked clinical_record or operation_record evidence",
                expense_id=expense_id,
            )

    if any(expense.get("kind") == "hospital" for expense in expense_map.values()) and "discharge" not in all_included_roles:
        issue(report, "blocker", "DISCHARGE_REQUIRED", "hospital expense exists without discharge evidence")

    try:
        required_case_roles = {
            item.strip()
            for item in list_of_strings(rules.get("required_case_roles"), "required_case_roles")
            if item.strip()
        }
    except ValueError as exc:
        required_case_roles = set()
        issue(report, "blocker", "REQUIRED_CASE_ROLES", str(exc))
    if not required_case_roles:
        issue(
            report,
            "blocker",
            "REQUIRED_CASE_ROLES",
            "rules.required_case_roles must contain the roles from the verified live checklist",
        )
    unknown_required = sorted(required_case_roles - EVIDENCE_ROLES)
    if unknown_required:
        issue(report, "blocker", "REQUIRED_CASE_ROLES", f"unknown required roles: {', '.join(unknown_required)}")
    missing_case_roles = sorted(required_case_roles - all_included_roles)
    if missing_case_roles:
        issue(report, "blocker", "MISSING_CASE_EVIDENCE", f"missing required case roles: {', '.join(missing_case_roles)}")

    for condition, required in CONDITION_ROLES.items():
        if conditions.get(condition) is True:
            missing = sorted(required - all_included_roles)
            if missing:
                issue(
                    report,
                    "blocker",
                    "CONDITIONAL_EVIDENCE",
                    f"{condition} is true; missing evidence roles: {', '.join(missing)}",
                )
    if conditions.get("implant") is True and not (
        all_included_roles & {"clinical_record", "operation_record"}
    ):
        issue(
            report,
            "blocker",
            "CONDITIONAL_EVIDENCE",
            "implant is true; clinical_record or operation_record evidence is required",
        )
    if conditions.get("ambulance_claimed") is True and not any(
        expense.get("kind") == "ambulance" for expense in expense_map.values()
    ):
        issue(report, "blocker", "CONDITION_LEDGER_CONFLICT", "ambulance_claimed is true but no ambulance expense exists")
    if conditions.get("ambulance_claimed") is False and any(
        expense.get("kind") == "ambulance" for expense in expense_map.values()
    ):
        issue(report, "blocker", "CONDITION_LEDGER_CONFLICT", "ambulance expense exists but ambulance_claimed is false")
    if conditions.get("implant") is False and any(
        expense.get("kind") == "implant" for expense in expense_map.values()
    ):
        issue(report, "blocker", "CONDITION_LEDGER_CONFLICT", "implant expense exists but conditions.implant is false")

    assembled_packs: list[str] = []
    standalone_attachment_count = 0
    for selection in included_selections:
        if selection.document.get("delivery_mode") == "standalone":
            standalone_attachment_count += 1
            continue
        for pack_id in selection.document.get("packs") or []:
            if pack_id not in assembled_packs:
                assembled_packs.append(pack_id)
    attachment_count = len(assembled_packs) + standalone_attachment_count
    max_files = portal.get("max_files")
    if max_files not in (None, ""):
        try:
            maximum = int(max_files)
            if maximum < 1:
                raise ValueError
            if attachment_count > maximum:
                issue(
                    report,
                    "blocker",
                    "PORTAL_FILE_COUNT",
                    f"{attachment_count} upload files exceed confirmed maximum {maximum}",
                )
        except (TypeError, ValueError):
            issue(report, "blocker", "PORTAL_FILE_COUNT", "portal.max_files must be a positive integer or null")

    issue_once(
        report,
        "warning",
        "VISUAL_QA_PENDING",
        "page-by-page rendered visual inspection is still required",
    )
    report["status"] = determine_status(report, portal_confirmed)
    return report, selections


def determine_status(report: dict[str, Any], portal_confirmed: bool) -> str:
    if report["blockers"]:
        return "NOT_READY"
    if not portal_confirmed:
        return "PORTAL_RULES_UNVERIFIED"
    if report["warnings"]:
        return "READY_WITH_WARNINGS"
    return "READY"


def evidence_role_label(role: str) -> str:
    return EVIDENCE_ROLE_LABELS.get(role, role.replace("_", " "))


def expense_evidence_label(role: str, expense: dict[str, Any]) -> str:
    service = str(expense.get("description", "")).strip()
    if not service:
        return evidence_role_label(role)
    service_specific = {
        "clinical_advice": f"doctor advice, prescription, or referral for {service}",
        "clinical_result": f"complete report or result for {service}",
        "invoice": f"itemized bill or invoice for {service}",
        "payment_proof": f"payment receipt or other paid proof for {service}",
        "operation_record": f"operation note or surgeon record for {service}",
        "implant_identity": f"implant sticker, barcode, or serial label for {service}",
    }
    return service_specific.get(role, evidence_role_label(role))


def expense_match_reference(expense: dict[str, Any]) -> str:
    details = [
        f"{str(expense.get('kind', 'expense')).replace('_', ' ')} expense {expense.get('id', '')}",
        f"provider {expense.get('issuer', '')}",
        f"date {expense.get('date', '')}",
        f"invoice {expense.get('invoice_number', '')}",
        f"billed {expense.get('currency', 'INR')} {expense.get('billed_amount', '0.00')}",
    ]
    description = str(expense.get("description", "")).strip()
    if description:
        details.append(f"service {description}")
    return "; ".join(details)


def report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Claim packet audit",
        "",
        f"- Case ID: `{report['case_id']}`",
        f"- Status: **{report['status']}**",
        f"- Blockers: {len(report['blockers'])}",
        f"- Warnings: {len(report['warnings'])}",
        "",
        "## Blockers",
        "",
    ]
    if report["blockers"]:
        for item in report["blockers"]:
            reference = item.get("document_id") or item.get("expense_id")
            suffix = f" (`{reference}`)" if reference else ""
            lines.append(f"- `{item['code']}`{suffix}: {item['message']}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        for item in report["warnings"]:
            reference = item.get("document_id") or item.get("expense_id")
            suffix = f" (`{reference}`)" if reference else ""
            lines.append(f"- `{item['code']}`{suffix}: {item['message']}")
    else:
        lines.append("- None.")

    portal_rules = report.get("portal_rules", {})
    per_file_limit = (
        f"{portal_rules.get('max_file_mb')} MB"
        if portal_rules.get("max_file_mb") not in (None, "")
        else "Not published/recorded"
    )
    total_limit = (
        f"{portal_rules.get('max_total_mb')} MB"
        if portal_rules.get("max_total_mb") not in (None, "")
        else "Not published/recorded"
    )
    lines.extend(
        [
            "",
            "## Portal rule scope",
            "",
            f"- Confirmed: {'yes' if portal_rules.get('confirmed') else 'no'}",
            f"- Checked journey/screen: {portal_rules.get('rule_scope') or 'Not recorded'}",
            f"- Accepted file types: {', '.join(portal_rules.get('accepted_file_types', [])) or 'Not recorded'}",
            f"- Per-file limit: {per_file_limit}",
            f"- Total limit: {total_limit}",
            f"- File-count limit: {portal_rules.get('max_files') if portal_rules.get('max_files') not in (None, '') else 'Not published/recorded'}",
        ]
    )

    totals = report.get("totals", {})
    lines.extend(
        [
            "",
            "## Reconciliation",
            "",
            f"- Case requested: {totals.get('currency', 'INR')} {totals.get('case_claimed_amount', '0.00')}",
            f"- Expense ledger: {totals.get('currency', 'INR')} {totals.get('expense_claimed_amount', '0.00')}",
        ]
    )
    for phase, amount in totals.get("by_phase", {}).items():
        lines.append(f"- {phase.title()} subtotal: {totals.get('currency', 'INR')} {amount}")
    lines.extend(
        [
            "",
            "| Expense | Phase | Kind | Date | Issuer | Invoice | Billed | Requested | Not requested | Reason |",
            "|---|---|---|---|---|---|---:|---:|---:|---|",
        ]
    )
    for expense in report.get("expenses", []):
        lines.append(
            "| {id} | {phase} | {kind} | {date} | {issuer} | {invoice_number} | {billed_amount} | {claim_amount} | {not_claimed_amount} | {not_claimed_reason} |".format(
                **{key: str(value).replace("|", "\\|") for key, value in expense.items()}
            )
        )

    lines.extend(
        [
            "",
            "## Evidence matching",
            "",
            "Each source below is linked to the expense shown; missing items are blockers, not inferred matches.",
            "",
            "| Expense | Exact financial event | Linked source/pages | Missing evidence |",
            "|---|---|---|---|",
        ]
    )
    for expense in report.get("expenses", []):
        linked = "<br>".join(
            f"{item.get('document_id', '')}: {item.get('source', '')} p.{item.get('pages', '')} "
            f"({', '.join(item.get('evidence_roles', []))})"
            for item in expense.get("linked_evidence", [])
        ) or "None linked"
        missing = ", ".join(expense.get("missing_evidence", [])) or "None"
        identity = expense_match_reference(expense)
        values = {
            "id": str(expense.get("id", "")).replace("|", "\\|"),
            "identity": identity.replace("|", "\\|"),
            "linked": linked.replace("|", "\\|"),
            "missing": missing.replace("|", "\\|"),
        }
        lines.append(
            f"| {values['id']} | {values['identity']} | {values['linked']} | {values['missing']} |"
        )

    lines.extend(
        [
            "",
            "## Document ledger",
            "",
            "| Document | Decision | Source | Pages | Phase | Expense links | Roles | Packs | SHA-256 |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for document in report.get("documents", []):
        values = {key: str(value).replace("|", "\\|") for key, value in document.items()}
        roles = ", ".join(document.get("evidence_roles", []))
        expense_links = ", ".join(document.get("expense_ids", []))
        packs = ", ".join(document.get("packs", []))
        lines.append(
            f"| {values['id']} | {values['decision']} | {values['source']} | {values['source_pages']} | "
            f"{values['phase']} | {expense_links} | {roles} | {packs} | `{document['sha256']}` |"
        )

    lines.extend(
        [
            "",
            "## Output inventory",
            "",
            "| Purpose | File | Pages | Bytes | SHA-256 |",
            "|---|---|---:|---:|---|",
        ]
    )
    for output in report.get("outputs", []):
        lines.append(
            f"| {output['purpose']} | {output['path']} | {output['pages']} | {output['bytes']} | `{output['sha256']}` |"
        )
    if not report.get("outputs"):
        lines.append("| - | No PDF output built | - | - | - |")
    lines.extend(
        [
            "",
            "This audit is private claim-working material. Structural readiness does not guarantee reimbursement acceptance.",
            "",
        ]
    )
    return "\n".join(lines)


def write_reports(
    output_dir: Path, report: dict[str, Any], *, stem: str = "claim-audit"
) -> tuple[Path, Path]:
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    refuse_symlink(json_path, "audit JSON")
    refuse_symlink(md_path, "audit Markdown")
    secure_replace(
        json_path,
        (json.dumps(report, indent=2, ensure_ascii=True) + "\n").encode("utf-8"),
    )
    secure_replace(md_path, report_markdown(report).encode("utf-8"))
    return json_path, md_path


def slugify(value: str, fallback: str = "packet") -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-").lower()
    return text or fallback


def money(value: Any, currency: str = "INR") -> str:
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"))
        return f"{currency} {amount:,.2f}"
    except (InvalidOperation, ValueError):
        return f"{currency} 0.00"


def styled_paragraph(text: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(str(text)), style)


def invariant_canvas(*args: Any, **kwargs: Any) -> canvas.Canvas:
    kwargs["invariant"] = 1
    return canvas.Canvas(*args, **kwargs)


def make_cover_pdf(
    manifest: dict[str, Any],
    report: dict[str, Any],
    selections: list[Selection],
    cover_page_count: int,
) -> bytes:
    case = manifest.get("case", {})
    currency = str(case.get("currency", "INR"))
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ClaimTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#17324D"),
        alignment=0,
        spaceAfter=8,
    )
    heading = ParagraphStyle(
        "ClaimHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#17324D"),
        spaceBefore=8,
        spaceAfter=5,
    )
    body = ParagraphStyle(
        "ClaimBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1F2937"),
    )
    small = ParagraphStyle("ClaimSmall", parent=body, fontSize=7.1, leading=9)
    buffer = BytesIO()
    doc_template = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title=f"Claim review {case.get('case_id', '')}",
        author="Indian Health Insurance Claim Help skill",
    )
    story: list[Any] = [
        styled_paragraph("Health reimbursement claim - review packet", title),
        styled_paragraph(
            "REVIEW ONLY. This index is not insurer approval and is not included in clean upload bundles.",
            body,
        ),
        Spacer(1, 5),
    ]
    details = [
        ["Case ID", case.get("case_id", "")],
        ["Insurer", case.get("insurer", "")],
        ["Product / UIN", f"{case.get('product', '')} / {case.get('uin', '')}"],
        ["Patient", case.get("patient_name", "")],
        ["Claim route", f"{case.get('claim_type', '')} / {case.get('claim_route', '')}"],
        ["Admission / discharge", f"{case.get('admission_date', '')} / {case.get('discharge_date', '')}"],
        ["Requested", money(case.get("claimed_amount", "0"), currency)],
        ["Audit status", report.get("status", "NOT_READY")],
    ]
    detail_table = Table(
        [[styled_paragraph(left, small), styled_paragraph(right, small)] for left, right in details],
        colWidths=[42 * mm, 142 * mm],
    )
    detail_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF4F8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.extend([detail_table, styled_paragraph("Phase subtotals", heading)])
    phase_rows: list[list[Any]] = [
        [styled_paragraph("Phase", small), styled_paragraph("Requested", small)]
    ]
    for phase, amount in report.get("totals", {}).get("by_phase", {}).items():
        phase_rows.append(
            [styled_paragraph(str(phase).title(), small), styled_paragraph(money(amount, currency), small)]
        )
    phase_table = Table(phase_rows, colWidths=[92 * mm, 92 * mm], repeatRows=1)
    phase_table.setStyle(default_table_style())
    story.extend([phase_table, styled_paragraph("Expense reconciliation", heading)])
    expense_rows: list[list[Any]] = [
        [
            styled_paragraph("ID", small),
            styled_paragraph("Phase", small),
            styled_paragraph("Date", small),
            styled_paragraph("Invoice", small),
            styled_paragraph("Description", small),
            styled_paragraph("Billed", small),
            styled_paragraph("Requested", small),
        ]
    ]
    for expense in report.get("expenses", []):
        expense_rows.append(
            [
                styled_paragraph(expense["id"], small),
                styled_paragraph(expense["phase"], small),
                styled_paragraph(expense["date"], small),
                styled_paragraph(expense["invoice_number"], small),
                styled_paragraph(expense["description"], small),
                styled_paragraph(money(expense["billed_amount"], currency), small),
                styled_paragraph(money(expense["claim_amount"], currency), small),
            ]
        )
    expense_table = Table(
        expense_rows,
        colWidths=[19 * mm, 18 * mm, 22 * mm, 23 * mm, 54 * mm, 24 * mm, 24 * mm],
        repeatRows=1,
    )
    expense_table.setStyle(default_table_style())
    story.append(expense_table)
    partial_expenses = [
        item
        for item in report.get("expenses", [])
        if Decimal(str(item.get("not_claimed_amount", "0"))) > 0
    ]
    story.append(styled_paragraph("Partial or excluded amounts", heading))
    if partial_expenses:
        partial_rows: list[list[Any]] = [
            [
                styled_paragraph("Expense", small),
                styled_paragraph("Billed", small),
                styled_paragraph("Requested", small),
                styled_paragraph("Not requested", small),
                styled_paragraph("Reason", small),
            ]
        ]
        for expense in partial_expenses:
            partial_rows.append(
                [
                    styled_paragraph(expense["id"], small),
                    styled_paragraph(money(expense["billed_amount"], currency), small),
                    styled_paragraph(money(expense["claim_amount"], currency), small),
                    styled_paragraph(money(expense["not_claimed_amount"], currency), small),
                    styled_paragraph(expense["not_claimed_reason"], small),
                ]
            )
        partial_table = Table(
            partial_rows,
            colWidths=[34 * mm, 28 * mm, 28 * mm, 30 * mm, 64 * mm],
            repeatRows=1,
        )
        partial_table.setStyle(default_table_style())
        story.append(partial_table)
    else:
        story.append(styled_paragraph("No partial or excluded amounts are recorded.", small))
    story.append(styled_paragraph("Document page index", heading))

    included = [item for item in selections if item.document.get("decision") == "include"]
    packet_cursor = cover_page_count + 1
    index_rows: list[list[Any]] = [
        [
            styled_paragraph("No.", small),
            styled_paragraph("Phase", small),
            styled_paragraph("Document", small),
            styled_paragraph("Expense", small),
            styled_paragraph("Date", small),
            styled_paragraph("Source", small),
            styled_paragraph("Packet pages", small),
        ]
    ]
    packet_ranges: dict[str, str] = {}
    for number, selection in enumerate(included, start=1):
        start = packet_cursor
        end = start + len(selection.pages) - 1
        packet_cursor = end + 1
        packet_range = str(start) if start == end else f"{start}-{end}"
        packet_ranges[str(selection.document.get("id", ""))] = packet_range
        index_rows.append(
            [
                styled_paragraph(number, small),
                styled_paragraph(selection.document.get("phase", ""), small),
                styled_paragraph(selection.document.get("document_type", ""), small),
                styled_paragraph(
                    ", ".join(selection.document.get("expense_ids", []) or []) or "case-level",
                    small,
                ),
                styled_paragraph(selection.document.get("date", ""), small),
                styled_paragraph(
                    f"{selection.source.path.name} p.{page_spec_text(selection.pages)}",
                    small,
                ),
                styled_paragraph(packet_range, small),
            ]
        )
    for document_item in report.get("documents", []):
        if document_item.get("id") in packet_ranges:
            document_item["master_packet_pages"] = packet_ranges[document_item["id"]]
    index_table = Table(
        index_rows,
        colWidths=[8 * mm, 19 * mm, 45 * mm, 25 * mm, 20 * mm, 39 * mm, 28 * mm],
        repeatRows=1,
    )
    index_table.setStyle(default_table_style())
    story.append(index_table)

    excluded = [item for item in report.get("documents", []) if item.get("decision") == "exclude"]
    if excluded:
        story.append(styled_paragraph("Exclusion ledger", heading))
        excluded_rows: list[list[Any]] = [
            [styled_paragraph("Document", small), styled_paragraph("Source pages", small), styled_paragraph("Reason", small)]
        ]
        for item in excluded:
            excluded_rows.append(
                [
                    styled_paragraph(item["id"], small),
                    styled_paragraph(item["source_pages"], small),
                    styled_paragraph(item["exclusion_reason"], small),
                ]
            )
        excluded_table = Table(excluded_rows, colWidths=[45 * mm, 30 * mm, 109 * mm], repeatRows=1)
        excluded_table.setStyle(default_table_style())
        story.append(excluded_table)

    story.extend(
        [
            Spacer(1, 6),
            styled_paragraph(
                "Amounts are copied from the private manifest. A bill plus its payment receipt is one expense. "
                "Final submission still requires policy, portal, original-document, and page-by-page visual checks.",
                small,
            ),
        ]
    )
    doc_template.build(story, canvasmaker=invariant_canvas)
    return buffer.getvalue()


def default_table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6EFF5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17324D")),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
    )


def image_selection_pdf(selection: Selection) -> bytes:
    packet = BytesIO()
    pdf_canvas = canvas.Canvas(packet, pagesize=A4, invariant=1)
    page_width, page_height = A4
    margin = 12 * mm
    max_width = page_width - 2 * margin
    max_height = page_height - 2 * margin
    with Image.open(selection.source.path) as source:
        for frame_index in selection.pages:
            source.seek(frame_index)
            frame = ImageOps.exif_transpose(source.copy())
            if frame.mode in ("RGBA", "LA") or (frame.mode == "P" and "transparency" in frame.info):
                rgba = frame.convert("RGBA")
                background = Image.new("RGB", rgba.size, "white")
                background.paste(rgba, mask=rgba.getchannel("A"))
                frame = background
            elif frame.mode != "RGB":
                frame = frame.convert("RGB")
            width, height = frame.size
            scale = min(max_width / width, max_height / height, 1.0)
            draw_width, draw_height = width * scale, height * scale
            x = (page_width - draw_width) / 2
            y = (page_height - draw_height) / 2
            pdf_canvas.setFillColor(colors.white)
            pdf_canvas.rect(0, 0, page_width, page_height, fill=1, stroke=0)
            pdf_canvas.drawImage(
                ImageReader(frame),
                x,
                y,
                width=draw_width,
                height=draw_height,
                preserveAspectRatio=True,
                mask="auto",
            )
            pdf_canvas.showPage()
    pdf_canvas.save()
    return packet.getvalue()


def selection_pages(selection: Selection) -> list[Any]:
    if selection.source.suffix == ".pdf":
        reader = PdfReader(str(selection.source.path), strict=False)
        return [reader.pages[index] for index in selection.pages]
    reader = PdfReader(BytesIO(image_selection_pdf(selection)))
    return list(reader.pages)


def writer_bytes(writer: PdfWriter) -> bytes:
    packet = BytesIO()
    writer.write(packet)
    return packet.getvalue()


def verify_pdf_bytes(payload: bytes, expected_pages: int) -> tuple[int, str]:
    reader = PdfReader(BytesIO(payload), strict=False)
    if reader.is_encrypted:
        raise ValueError("generated PDF is unexpectedly encrypted")
    page_count = len(reader.pages)
    if page_count != expected_pages:
        raise ValueError(f"generated PDF has {page_count} pages; expected {expected_pages}")
    return page_count, hashlib.sha256(payload).hexdigest()


def positive_decimal_or_none(value: Any, field: str) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field} must be a positive number or null") from None
    if not result.is_finite() or result <= 0:
        raise ValueError(f"{field} must be a positive number or null")
    return result


BUILD_SUBDIRECTORY_NAMES = ("REVIEW_ONLY", "SUBMIT", "CANDIDATE_UPLOADS")


def packet_surface_has_entries(output_dir: Path) -> bool:
    """Return true when a prior packet or colliding build entry is present."""
    for name in BUILD_SUBDIRECTORY_NAMES:
        path = output_dir / name
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            return True
        if path.is_dir():
            try:
                if next(path.iterdir(), None) is not None:
                    return True
            except OSError:
                return True
    return False


def prepare_empty_build_subdirectories(
    output_dir: Path, report: dict[str, Any], *, create: bool
) -> bool:
    """Require a fresh build surface so stale claim PDFs cannot be mixed in."""
    paths = [output_dir / name for name in BUILD_SUBDIRECTORY_NAMES]
    for path in paths:
        if path.is_symlink():
            issue(
                report,
                "blocker",
                "OUTPUT_PATH_TYPE",
                f"build directory must not be a symbolic link: {path.name}",
            )
            continue
        if path.exists() and not path.is_dir():
            issue(
                report,
                "blocker",
                "OUTPUT_PATH_TYPE",
                f"build directory name is occupied by a non-directory: {path.name}",
            )
            continue
        if path.is_dir():
            try:
                if next(path.iterdir(), None) is not None:
                    issue(
                        report,
                        "blocker",
                        "OUTPUT_DIRECTORY_NOT_EMPTY",
                        f"{path.name} is not empty; use a fresh revision-specific output directory",
                    )
            except OSError as exc:
                issue(
                    report,
                    "blocker",
                    "OUTPUT_DIRECTORY_READ",
                    f"cannot inspect {path.name}: {exc}",
                )
    if report["blockers"] or not create:
        return not report["blockers"]
    for path in paths:
        try:
            path.mkdir(mode=0o700, parents=False, exist_ok=True)
            path.chmod(0o700)
        except OSError as exc:
            issue(
                report,
                "blocker",
                "OUTPUT_DIRECTORY_CREATE",
                f"cannot prepare {path.name}: {exc}",
            )
    return not report["blockers"]


def build_packets(
    manifest: dict[str, Any],
    report: dict[str, Any],
    selections: list[Selection],
    output_dir: Path,
) -> None:
    included = [item for item in selections if item.document.get("decision") == "include"]
    if not included:
        issue(report, "blocker", "NO_INCLUDED_DOCUMENTS", "no documents are included")
        report["status"] = "NOT_READY"
        return

    case = manifest.get("case", {})
    verification = manifest.get("verification", {})
    rules = manifest.get("rules", {})
    portal = verification.get("portal") if isinstance(verification.get("portal"), dict) else {}
    pack_definitions = {
        str(item.get("id")): item
        for item in rules.get("pack_definitions", [])
        if isinstance(item, dict) and item.get("id")
    }
    case_slug = slugify(str(case.get("case_id", "claim")), "claim")
    review_dir = output_dir / "REVIEW_ONLY"
    if not prepare_empty_build_subdirectories(output_dir, report, create=True):
        report["status"] = "NOT_READY"
        return

    assembled_included = [
        item for item in included if item.document.get("delivery_mode") != "standalone"
    ]
    standalone_included = [
        item for item in included if item.document.get("delivery_mode") == "standalone"
    ]
    pack_ids: list[str] = []
    for selection in assembled_included:
        for pack_id in selection.document.get("packs") or []:
            if pack_id not in pack_ids:
                pack_ids.append(str(pack_id))
    standalone_filenames: dict[str, tuple[str, str]] = {}
    for selection in standalone_included:
        document_id = str(selection.document.get("id"))
        pack_id = str((selection.document.get("packs") or [""])[0])
        id_digest = hashlib.sha256(document_id.encode("utf-8")).hexdigest()[:8]
        filename = (
            f"{slugify(pack_id)}--{slugify(document_id)}-{id_digest}--original.pdf"
        )
        if any(existing_filename == filename for _, existing_filename in standalone_filenames.values()):
            issue(
                report,
                "blocker",
                "STANDALONE_FILENAME_COLLISION",
                "standalone document filenames collide after normalization",
                document_id=document_id,
            )
        standalone_filenames[document_id] = (pack_id, filename)
    if report["blockers"]:
        report["status"] = "NOT_READY"
        return

    source_page_cache: dict[str, list[Any]] = {}
    for selection in included:
        document_id = str(selection.document.get("id"))
        try:
            source_page_cache[document_id] = selection_pages(selection)
        except Exception as exc:
            issue(
                report,
                "blocker",
                "SOURCE_READ_DURING_BUILD",
                f"cannot read source pages during build: {exc}",
                document_id=document_id,
            )
    if report["blockers"]:
        report["status"] = "NOT_READY"
        return

    pack_payloads: dict[str, tuple[bytes, int, str]] = {}
    for pack_id in pack_ids:
        writer = PdfWriter()
        expected_pages = 0
        for selection in assembled_included:
            if pack_id not in (selection.document.get("packs") or []):
                continue
            for page in source_page_cache[str(selection.document.get("id"))]:
                writer.add_page(page)
                expected_pages += 1
        if expected_pages == 0:
            issue(report, "blocker", "EMPTY_PACK", f"pack has no pages: {pack_id}")
            continue
        writer.add_metadata(
            {
                "/Title": pack_id,
                "/Author": "Indian Health Insurance Claim Help skill",
                "/Subject": "Clean source-evidence upload bundle",
            }
        )
        payload = writer_bytes(writer)
        try:
            page_count, digest = verify_pdf_bytes(payload, expected_pages)
            pack_payloads[pack_id] = (payload, page_count, digest)
        except ValueError as exc:
            issue(report, "blocker", "OUTPUT_VERIFY", f"{pack_id}: {exc}")

    standalone_payloads: dict[str, tuple[str, str, bytes, int, str]] = {}
    for selection in standalone_included:
        document_id = str(selection.document.get("id"))
        pack_id, filename = standalone_filenames[document_id]
        try:
            payload = selection.source.path.read_bytes()
            page_count, digest = verify_pdf_bytes(payload, selection.source.page_count)
            if digest != selection.source.sha256:
                raise ValueError("standalone source hash changed after audit")
            standalone_payloads[document_id] = (
                pack_id,
                filename,
                payload,
                page_count,
                digest,
            )
        except (OSError, ValueError) as exc:
            issue(
                report,
                "blocker",
                "OUTPUT_VERIFY",
                f"standalone {document_id}: {exc}",
                document_id=document_id,
            )

    try:
        portal_max = positive_decimal_or_none(portal.get("max_file_mb"), "portal.max_file_mb")
        total_max = positive_decimal_or_none(portal.get("max_total_mb"), "portal.max_total_mb")
        target = positive_decimal_or_none(rules.get("compatibility_target_mb"), "compatibility_target_mb")
    except ValueError as exc:
        issue(report, "blocker", "UPLOAD_LIMIT", str(exc))
        portal_max = total_max = target = None

    total_bytes = 0
    for pack_id, (payload, _pages, _digest) in pack_payloads.items():
        total_bytes += len(payload)
        definition = pack_definitions.get(pack_id, {})
        try:
            pack_max = positive_decimal_or_none(definition.get("max_file_mb"), f"pack {pack_id} max_file_mb")
        except ValueError as exc:
            pack_max = None
            issue(report, "blocker", "UPLOAD_LIMIT", str(exc))
        active_limits = [limit for limit in (pack_max, portal_max) if limit is not None]
        effective_max = min(active_limits) if active_limits else None
        if effective_max is not None and Decimal(len(payload)) > effective_max * Decimal(1_000_000):
            issue(
                report,
                "blocker",
                "UPLOAD_FILE_TOO_LARGE",
                f"{pack_id} is {len(payload)} bytes and exceeds the confirmed {effective_max} MB limit",
            )
        if target is not None and Decimal(len(payload)) > target * Decimal(1_000_000):
            issue(
                report,
                "warning",
                "COMPATIBILITY_TARGET",
                f"{pack_id} exceeds the non-authoritative {target} MB compatibility target",
            )
    for document_id, (
        pack_id,
        _filename,
        payload,
        _pages,
        _digest,
    ) in standalone_payloads.items():
        total_bytes += len(payload)
        definition = pack_definitions.get(pack_id, {})
        try:
            pack_max = positive_decimal_or_none(
                definition.get("max_file_mb"), f"pack {pack_id} max_file_mb"
            )
        except ValueError as exc:
            pack_max = None
            issue(report, "blocker", "UPLOAD_LIMIT", str(exc))
        active_limits = [limit for limit in (pack_max, portal_max) if limit is not None]
        effective_max = min(active_limits) if active_limits else None
        if effective_max is not None and Decimal(len(payload)) > effective_max * Decimal(1_000_000):
            issue(
                report,
                "blocker",
                "UPLOAD_FILE_TOO_LARGE",
                f"standalone {document_id} is {len(payload)} bytes and exceeds the confirmed {effective_max} MB limit",
                document_id=document_id,
            )
        if target is not None and Decimal(len(payload)) > target * Decimal(1_000_000):
            issue(
                report,
                "warning",
                "COMPATIBILITY_TARGET",
                f"standalone {document_id} exceeds the non-authoritative {target} MB compatibility target",
                document_id=document_id,
            )
    if total_max is not None and Decimal(total_bytes) > total_max * Decimal(1_000_000):
        issue(report, "blocker", "UPLOAD_TOTAL_TOO_LARGE", f"upload bundles total {total_bytes} bytes and exceed confirmed {total_max} MB limit")

    if report["blockers"]:
        report["status"] = "NOT_READY"
        return

    final_warning_codes = {item.get("code") for item in report.get("warnings", [])}
    clean_directory_name = (
        "SUBMIT"
        if verification.get("portal_rules_confirmed") is True
        and final_warning_codes <= {"VISUAL_QA_PENDING"}
        else "CANDIDATE_UPLOADS"
    )
    submit_dir = output_dir / clean_directory_name
    report["status"] = determine_status(
        report, verification.get("portal_rules_confirmed") is True
    )

    try:
        provisional = make_cover_pdf(manifest, report, selections, 0)
        cover_pages = len(PdfReader(BytesIO(provisional)).pages)
        cover_payload = provisional
        for _ in range(3):
            candidate = make_cover_pdf(manifest, report, selections, cover_pages)
            candidate_pages = len(PdfReader(BytesIO(candidate)).pages)
            cover_payload = candidate
            if candidate_pages == cover_pages:
                break
            cover_pages = candidate_pages

        master_writer = PdfWriter()
        cover_reader = PdfReader(BytesIO(cover_payload))
        for page in cover_reader.pages:
            master_writer.add_page(page)
        packet_cursor = cover_pages
        for selection in included:
            document_id = str(selection.document.get("id"))
            start_index = packet_cursor
            for page in source_page_cache[document_id]:
                master_writer.add_page(page)
                packet_cursor += 1
            title = str(
                selection.document.get("document_type")
                or selection.document.get("id")
            )
            master_writer.add_outline_item(title, start_index)
        master_writer.add_metadata(
            {
                "/Title": f"Claim review {case_slug}",
                "/Author": "Indian Health Insurance Claim Help skill",
                "/Subject": "Private reimbursement claim review packet",
            }
        )
        master_payload = writer_bytes(master_writer)
        master_page_count, master_hash = verify_pdf_bytes(master_payload, packet_cursor)
    except Exception as exc:
        issue(report, "blocker", "OUTPUT_VERIFY", f"review master: {exc}")
        report["status"] = "NOT_READY"
        return

    master_path = review_dir / f"{case_slug}-master-review.pdf"
    pack_paths = {
        pack_id: submit_dir / f"{slugify(pack_id)}.pdf" for pack_id in pack_ids
    }
    standalone_paths = {
        document_id: (pack_id, submit_dir / filename)
        for document_id, (pack_id, filename) in standalone_filenames.items()
    }
    planned_paths = [
        master_path,
        *pack_paths.values(),
        *(target for _, target in standalone_paths.values()),
    ]
    if len({str(path) for path in planned_paths}) != len(planned_paths):
        issue(
            report,
            "blocker",
            "OUTPUT_FILENAME_COLLISION",
            "two planned outputs resolve to the same filename",
        )
        report["status"] = "NOT_READY"
        return

    if not prepare_empty_build_subdirectories(output_dir, report, create=False):
        report["status"] = "NOT_READY"
        return

    changed_sources: list[str] = []
    for selection in included:
        try:
            if sha256_file(selection.source.path) != selection.source.sha256:
                changed_sources.append(str(selection.source.path))
        except OSError:
            changed_sources.append(str(selection.source.path))
    changed_sources = sorted(set(changed_sources))
    if changed_sources:
        issue(
            report,
            "blocker",
            "SOURCE_CHANGED_DURING_BUILD",
            "one or more source files changed while the packet was being built; rerun the audit",
        )
        report["status"] = "NOT_READY"
        return

    written: list[Path] = []
    pending_outputs: list[dict[str, Any]] = []
    try:
        secure_write_new(master_path, master_payload)
        written.append(master_path)
        pending_outputs.append(
            {
                "purpose": "review-only master",
                "path": str(master_path),
                "pages": master_page_count,
                "bytes": len(master_payload),
                "sha256": master_hash,
            }
        )
        for pack_id in pack_ids:
            payload, page_count, digest = pack_payloads[pack_id]
            target_path = pack_paths[pack_id]
            secure_write_new(target_path, payload)
            written.append(target_path)
            pending_outputs.append(
                {
                    "purpose": f"{clean_directory_name.lower()}:{pack_id}",
                    "path": str(target_path),
                    "pages": page_count,
                    "bytes": len(payload),
                    "sha256": digest,
                }
            )
        for document_id, (
            pack_id,
            _filename,
            payload,
            page_count,
            digest,
        ) in standalone_payloads.items():
            _mapped_pack_id, target_path = standalone_paths[document_id]
            secure_write_new(target_path, payload)
            written.append(target_path)
            pending_outputs.append(
                {
                    "purpose": (
                        f"{clean_directory_name.lower()}:standalone:{pack_id}:{document_id}"
                    ),
                    "path": str(target_path),
                    "pages": page_count,
                    "bytes": len(payload),
                    "sha256": digest,
                }
            )
    except OSError as exc:
        for path in written:
            path.unlink(missing_ok=True)
        issue(report, "blocker", "OUTPUT_WRITE", f"could not write complete output set: {exc}")
        report["status"] = "NOT_READY"
        return
    report["outputs"].extend(pending_outputs)
    report["status"] = determine_status(report, verification.get("portal_rules_confirmed") is True)


def main() -> int:
    args = parse_args()
    if DEPENDENCY_ERROR is not None:
        fail(
            "missing PDF runtime dependency "
            f"{DEPENDENCY_ERROR.name!r}. From the skill repository root, run: "
            "python3 -m pip install -r requirements.txt"
        )
    manifest_path = args.manifest.expanduser().resolve()
    manifest = load_manifest(manifest_path)
    output_dir = prepare_output_dir(args.output_dir, manifest_path.parent)
    canonical_json = output_dir / "claim-audit.json"
    canonical_markdown = output_dir / "claim-audit.md"
    refuse_symlink(canonical_json, "audit JSON")
    refuse_symlink(canonical_markdown, "audit Markdown")
    packet_entries_before_command = packet_surface_has_entries(output_dir)
    canonical_report_exists = canonical_json.exists() or canonical_markdown.exists()
    report, selections = audit_manifest(manifest, manifest_path)
    if args.command == "build" and not report["blockers"]:
        build_packets(manifest, report, selections, output_dir)
    report_stem = (
        "claim-audit-attempt"
        if packet_entries_before_command and canonical_report_exists
        else "claim-audit"
    )
    _json_path, markdown_path = write_reports(output_dir, report, stem=report_stem)
    print(f"Case: {report['case_id']}")
    print(f"Status: {report['status']}")
    print(f"Blockers: {len(report['blockers'])}; warnings: {len(report['warnings'])}")
    print(f"Audit: {markdown_path}")
    return 2 if report["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
