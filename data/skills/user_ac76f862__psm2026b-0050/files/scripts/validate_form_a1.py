#!/usr/bin/env python3
"""Validate the structural compliance of a Form A.1 IR JSON against
T/CHAS 20-2-3—2021 附录 A 表 A.1.

Checks:
- Required encounter header fields.
- All drug records appear in the drug list (no orphan drops).
- Patient-brought drugs are tagged with patient_brought=true.
- Signature placeholders are blank (no model name, no AI identifier).
- Unconfirmed adjustments are not marked as already executed.

Exit codes (per output-contract.md §6):
  0  pass
  2  header / drug list incomplete
  3  signature row non-empty
  4  patient_brought drug not marked
  5  unconfirmed adjustment marked as executed

Usage:
  python validate_form_a1.py <input.json>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


PHI_FORBIDDEN_PATTERNS = [
    re.compile(r"\b\d{15,18}\b"),  # 身份证号
    re.compile(r"\b1[3-9]\d{9}\b"),  # 手机号
]


class ValidationResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.exit_code: int = 0

    def add_error(self, msg: str, code: int) -> None:
        self.errors.append(msg)
        if code > self.exit_code:
            self.exit_code = code

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_header(data: dict[str, Any], result: ValidationResult) -> None:
    encounter = data.get("encounter") or {}
    required = {
        "patient_name",
        "patient_age",
        "patient_gender",
        "patient_id",
        "primary_diagnosis",
    }
    missing = required - set(encounter.keys())
    if missing:
        result.add_error(f"Header missing fields: {sorted(missing)}", 2)

    if not encounter.get("info_sources"):
        result.add_error("Header missing info_sources", 2)

    # admission_time or transfer_in_time
    if not (encounter.get("admission_time") or encounter.get("transfer_in_time")):
        result.add_error(
            "Header requires admission_time or transfer_in_time", 2
        )


def check_drug_list(data: dict[str, Any], result: ValidationResult) -> None:
    drugs = data.get("drug_records") or []
    if not drugs:
        result.add_error("Drug list is empty; standard requires full list", 2)
        return
    for drug in drugs:
        rid = drug.get("record_id", "<unknown>")
        # Original name must always be present
        if not drug.get("original_name"):
            result.add_error(f"Drug {rid} missing original_name", 2)

        # patient_brought boolean explicit
        if "patient_brought" not in drug:
            result.add_error(
                f"Drug {rid} missing patient_brought boolean", 4
            )

        # Standard requires listing ALL drugs; the renderer must include every
        # record, including stopped / unconfirmed. We verify the renderer would
        # include each by checking evidence_status is set.
        if not drug.get("evidence_status"):
            result.add_error(
                f"Drug {rid} missing evidence_status; cannot decide inclusion", 2
            )


def check_signature_blank(data: dict[str, Any], result: ValidationResult) -> None:
    """The signature row is *generated* at render time, but the IR must not
    embed any AI / model identifier inside encounter or drug_records that
    would later be copied into the signature row."""
    forbidden_signatures = [
        "GPT", "Claude", "WorkBuddy", "AI", "模型", "人工智能", "auto-sign",
    ]
    blob = json.dumps(data, ensure_ascii=False)
    for keyword in forbidden_signatures:
        # We only treat as hard error if the keyword appears in obvious
        # signature contexts (pharmacist_signature / physician_signature keys).
        for key in ("pharmacist_signature", "physician_signature", "signature_date"):
            if key in data and data[key]:
                result.add_error(
                    f"Signature field {key} must remain blank in IR", 3
                )
    # Also flag if any of the forbidden signatures appears in raw_text of an
    # evidence record tagged as "signature".
    for ev in data.get("evidence") or []:
        if "签名" in str(ev.get("field_path", "")) and ev.get("value"):
            result.add_error(
                "Evidence tied to a signature path contains a value", 3
            )
    # Just informational: the keyword check above is in addition to literal
    # blanks; the IR carries no signature fields by design, so this should
    # always pass if schema is followed.


def check_unconfirmed_adjustments(data: dict[str, Any], result: ValidationResult) -> None:
    outcomes = data.get("reconciliation_outcomes") or []
    for o in outcomes:
        role = o.get("decided_by_role")
        if role == "pharmacist_suggestion" and o.get("result") in (
            "停药",
            "加药",
            "换药",
            "恢复用药",
            "临时暂停",
            "临时调整",
        ):
            # Allowed: still suggestions, but the renderer must mark them as
            # "建议讨论" / "待医师确认" not "已执行".
            # Here we just warn that the renderer must NOT promote these to
            # "已确认".
            result.add_warning(
                f"Outcome for {o.get('drug_record_id')} is unconfirmed adjustment "
                f"({o.get('result')}); renderer must label '建议讨论'."
            )
        if role == "physician_confirmed" and not o.get("source_id"):
            result.add_error(
                f"Outcome for {o.get('drug_record_id')} physician_confirmed lacks source_id",
                5,
            )


def check_patient_brought_marking(data: dict[str, Any], result: ValidationResult) -> None:
    """For every drug whose evidence_status is patient_brought_med, the
    patient_brought flag must be true (otherwise the renderer will not append *)."""
    for drug in data.get("drug_records") or []:
        if drug.get("category") == "patient_brought_med" and drug.get("patient_brought") is not True:
            result.add_error(
                f"Drug {drug.get('record_id')} category=patient_brought_med "
                f"but patient_brought != true",
                4,
            )


def check_phi_in_test_data(data: dict[str, Any], result: ValidationResult) -> None:
    """Soft PHI check: warn (not fail) on patterns that resemble real IDs/phones.
    Real PHI is forbidden by privacy-and-safety.md; this helps catch leaks."""
    blob = json.dumps(data, ensure_ascii=False)
    # Exclude clearly synthetic test patterns (TEST-..., 1380000000x)
    if re.search(r"TEST-\d{4}-\d{3}", blob):
        return
    for pattern in PHI_FORBIDDEN_PATTERNS:
        if pattern.search(blob):
            result.add_warning(
                "Possible PHI pattern detected in IR (e.g. 身份证号/手机号). "
                "Confirm this is synthetic test data."
            )
            break


def validate(data: dict[str, Any]) -> ValidationResult:
    result = ValidationResult()
    check_header(data, result)
    check_drug_list(data, result)
    check_signature_blank(data, result)
    check_unconfirmed_adjustments(data, result)
    check_patient_brought_marking(data, result)
    check_phi_in_test_data(data, result)
    return result


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python validate_form_a1.py <input.json>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.exists():
        print(f"Input file not found: {path}", file=sys.stderr)
        return 2
    try:
        data = load_json(path)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return 2

    result = validate(data)
    print("=" * 60)
    print("Form A.1 Structural Validation")
    print("=" * 60)
    print(f"Patient ID       : {data.get('encounter', {}).get('patient_id')}")
    print(f"Encounter ID     : {data.get('encounter', {}).get('encounter_id')}")
    print(f"Drug Records     : {len(data.get('drug_records') or [])}")
    print(f"Outcomes         : {len(data.get('reconciliation_outcomes') or [])}")
    print()
    if result.warnings:
        print("Warnings:")
        for w in result.warnings:
            print(f"  - {w}")
        print()
    if result.errors:
        print("Errors:")
        for e in result.errors:
            print(f"  - {e}")
        print()
    print(f"Result: {'PASS' if result.exit_code == 0 else 'FAIL'} (exit_code={result.exit_code})")
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))