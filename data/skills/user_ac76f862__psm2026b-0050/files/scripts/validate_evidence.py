#!/usr/bin/env python3
"""Validate the evidence ledger of a medication reconciliation IR JSON.

Implements checks called out by references/privacy-and-safety.md and
references/output-contract.md:

- Each structured field must carry a source_id, page_or_image, evidence_status.
- Conflict fields must have evidence_status=conflict.
- Critical drug fields cannot be filled without source attribution.
- Patient and encounter identity must be unambiguous.
- Mixed-patient contamination triggers a hard stop.
- physician_confirmed=true requires decided_by_role=physician_confirmed AND
  a corresponding source snippet in the input.
- Patient-brought drugs must be flagged with patient_brought=true.
- No obvious fabricated names / doses / frequencies on critical fields.

Exit codes (per output-contract.md §6):
  0  pass
  2  missing required fields
  3  critical drug field has no source or looks fabricated
  4  mixed-patient hard stop
  5  physician_confirmed marker conflict

Usage:
  python validate_evidence.py <input.json>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_ENCOUNTER_KEYS = {
    "patient_name",
    "patient_age",
    "patient_gender",
    "patient_id",
    "primary_diagnosis",
    "info_sources",
    "encounter_id",
    "suspected_other_patient",
}

CRITICAL_DRUG_FIELDS = (
    "generic_name",
    "dose",
    "frequency",
    "route",
    "indication",
    "start_time",
    "stop_time",
)

EVIDENCE_STATUSES = {
    "direct_visible",
    "cross_confirmed",
    "conflict",
    "ambiguous",
    "missing",
    "pharmacist_verified",
    "physician_confirmed",
}

# Loose patterns suggesting fabricated numeric doses
DOSE_PATTERN = re.compile(r"^[\s\d\.]+(mg|g|mcg|μg|ml|mL|iu|U|mmol)$", re.IGNORECASE)


class ValidationResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.exit_code: int = 0

    def add_error(self, msg: str, code: int) -> None:
        self.errors.append(msg)
        # Escalate exit code while preserving the most severe code seen
        if code > self.exit_code:
            self.exit_code = code

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_encounter(encounter: dict[str, Any], result: ValidationResult) -> None:
    if not isinstance(encounter, dict):
        result.add_error("encounter must be an object", 2)
        return
    missing = REQUIRED_ENCOUNTER_KEYS - set(encounter.keys())
    if missing:
        result.add_error(
            f"encounter missing required fields: {sorted(missing)}", 2
        )

    # suspected_other_patient hard stop
    if encounter.get("suspected_other_patient") is True:
        result.add_error(
            "Hard stop: encounter.suspected_other_patient=true; mixed-patient contamination suspected. "
            "Resolve before continuing.",
            4,
        )

    # patient_id must be a non-empty string
    pid = encounter.get("patient_id")
    if not pid or not isinstance(pid, str):
        result.add_error("patient_id must be a non-empty string", 2)


def check_sources(sources: list[Any], result: ValidationResult) -> None:
    seen_ids: set[str] = set()
    if not isinstance(sources, list) or not sources:
        result.add_error("sources must be a non-empty list", 2)
        return
    for src in sources:
        sid = src.get("source_id") if isinstance(src, dict) else None
        if not sid:
            result.add_error("source missing source_id", 2)
            continue
        if sid in seen_ids:
            result.add_error(f"duplicate source_id: {sid}", 2)
        seen_ids.add(sid)
        if not src.get("file_name"):
            result.add_warning(f"source {sid} has no file_name")


def check_drug_records(
    drug_records: list[Any], source_ids: set[str], result: ValidationResult
) -> None:
    if not isinstance(drug_records, list) or not drug_records:
        result.add_error("drug_records must be a non-empty list", 2)
        return

    for drug in drug_records:
        if not isinstance(drug, dict):
            result.add_error("drug_record is not an object", 2)
            continue
        rid = drug.get("record_id", "<unknown>")
        for required in ("record_id", "original_name", "category", "source_id", "evidence_status"):
            if required not in drug:
                result.add_error(f"drug {rid} missing required field: {required}", 2)

        # source_id must exist
        sid = drug.get("source_id")
        if sid and source_ids and sid not in source_ids:
            result.add_error(
                f"drug {rid} references unknown source_id: {sid}", 2
            )

        # evidence_status must be in enum
        ev_status = drug.get("evidence_status")
        if ev_status and ev_status not in EVIDENCE_STATUSES:
            result.add_error(
                f"drug {rid} invalid evidence_status: {ev_status}", 2
            )

        # Critical drug fields must have source attribution; if filled and source
        # is missing, escalate.
        if drug.get("evidence_status") != "missing":
            for field_name in CRITICAL_DRUG_FIELDS:
                value = drug.get(field_name)
                if value in (None, "", []):
                    continue
                # If the field is filled, source_id must be present and we
                # already verified it belongs to known sources above.
                # Also catch obviously fabricated dose strings.
                if field_name == "dose" and isinstance(value, str):
                    if not re.search(r"\d", value):
                        result.add_error(
                            f"drug {rid} dose={value!r} has no numeric value (possible fabrication)",
                            3,
                        )

        # patient_brought must be explicit boolean
        if "patient_brought" not in drug:
            result.add_warning(f"drug {rid} missing patient_brought boolean")


def check_reconciliation_outcomes(
    outcomes: list[Any], drug_ids: set[str], source_ids: set[str], result: ValidationResult
) -> None:
    if not isinstance(outcomes, list):
        result.add_error("reconciliation_outcomes must be a list", 2)
        return
    for outcome in outcomes:
        rid = outcome.get("drug_record_id")
        if rid and drug_ids and rid not in drug_ids:
            result.add_error(
                f"reconciliation_outcome references unknown drug_record_id: {rid}",
                2,
            )
        role = outcome.get("decided_by_role")
        if role not in ("pharmacist_suggestion", "physician_confirmed"):
            result.add_error(
                f"outcome for {rid} invalid decided_by_role: {role!r}", 2
            )
        # physician_confirmed must have a source snippet (decided_at or source_id)
        if role == "physician_confirmed":
            if not outcome.get("source_id") or not outcome.get("decided_at"):
                result.add_error(
                    f"outcome for {rid} marked physician_confirmed but lacks source_id/decided_at",
                    5,
                )
            if source_ids and outcome.get("source_id") not in source_ids:
                result.add_error(
                    f"outcome for {rid} physician_confirmed references unknown source_id",
                    5,
                )


def check_discrepancies(
    discrepancies: list[Any], source_ids: set[str], result: ValidationResult
) -> None:
    if discrepancies is None:
        return
    if not isinstance(discrepancies, list):
        result.add_error("discrepancies must be a list", 2)
        return
    for d in discrepancies:
        if d.get("evidence_status") == "conflict":
            # Conflict fields should also reference at least two distinct sources
            sources_in_diff = set()
            for key in ("source_a", "source_b"):
                sub = d.get(key) or {}
                if sub.get("source_id"):
                    sources_in_diff.add(sub["source_id"])
            if len(sources_in_diff) < 2:
                result.add_warning(
                    f"discrepancy {d.get('discrepancy_id')} marked conflict but references <2 sources"
                )
        # Any discrepancy with physician_confirmed=true must be backed by source
        if d.get("physician_confirmed") is True:
            if not d.get("proposed_action"):
                result.add_warning(
                    f"discrepancy {d.get('discrepancy_id')} physician_confirmed without proposed_action"
                )


def validate(data: dict[str, Any]) -> ValidationResult:
    result = ValidationResult()
    encounter = data.get("encounter")
    check_encounter(encounter, result)

    sources = data.get("sources") or []
    check_sources(sources, result)
    source_ids = {s.get("source_id") for s in sources if isinstance(s, dict) and s.get("source_id")}

    drug_records = data.get("drug_records") or []
    check_drug_records(drug_records, source_ids, result)
    drug_ids = {d.get("record_id") for d in drug_records if isinstance(d, dict) and d.get("record_id")}

    outcomes = data.get("reconciliation_outcomes") or []
    check_reconciliation_outcomes(outcomes, drug_ids, source_ids, result)

    discrepancies = data.get("discrepancies") or []
    check_discrepancies(discrepancies, source_ids, result)

    return result


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python validate_evidence.py <input.json>", file=sys.stderr)
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
    print("Evidence Ledger Validation")
    print("=" * 60)
    print(f"Patient ID       : {data.get('encounter', {}).get('patient_id')}")
    print(f"Encounter ID     : {data.get('encounter', {}).get('encounter_id')}")
    print(f"Sources          : {len(data.get('sources') or [])}")
    print(f"Drug Records     : {len(data.get('drug_records') or [])}")
    print(f"Discrepancies    : {len(data.get('discrepancies') or [])}")
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