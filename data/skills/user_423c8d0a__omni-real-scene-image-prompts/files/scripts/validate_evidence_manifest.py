#!/usr/bin/env python3
"""Validate evidence provenance, freshness, scale boundaries, and truth mode."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


REALITY_MODES = {"A", "B", "C"}
SOURCE_TYPES = {
    "user_asset",
    "satellite",
    "orthophoto",
    "street_view",
    "ground_photo",
    "site_camera",
    "map",
    "poi",
    "transit",
    "statistics",
    "industry_reference",
}
GROUND_TYPES = {"user_asset", "street_view", "ground_photo", "site_camera"}
REMOTE_TYPES = {"satellite", "orthophoto"}
MACRO_TYPES = {"satellite", "orthophoto", "map", "poi", "transit"}
SENSITIVE_LEVELS = {"ground", "store", "people", "interior", "text", "operation"}
CLAIM_LEVELS = {"macro", "ground", "store", "people", "interior", "text", "operation", "original"}
CLAIM_STATUSES = {"observed", "inferred", "original"}
CONFIDENCE_VALUES = {"high", "medium", "low"}
KNOWN_COORDINATE_SYSTEMS = {"WGS84", "CGCS2000", "GCJ-02", "BD-09", "LOCAL", "UNKNOWN", "N/A"}

SOURCE_REQUIRED_FIELDS = (
    "id",
    "source_type",
    "source_name",
    "capture_date",
    "access_date",
    "geographic_precision",
    "coordinate_system",
    "spatial_resolution",
    "license_or_permission",
    "supported_claims",
    "unsupported_claims",
    "confidence",
)

CLAIM_REQUIRED_FIELDS = (
    "id",
    "statement",
    "claim_level",
    "status",
    "source_ids",
    "current_state",
)


def normalized(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def parse_iso_date(value: Any) -> date | None:
    text = normalized(value)
    if not text or text.lower() in {"unknown", "n/a", "none"}:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


def months_old(capture: date, as_of: date) -> float:
    return max(0, (as_of - capture).days) / 30.4375


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("manifest root must be a JSON object")
    return data


def as_string_list(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    if not all(isinstance(item, str) and item.strip() for item in value):
        return None
    return [item.strip() for item in value]


def audit(manifest: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []

    for field in ("version", "reality_mode", "target_scope", "as_of_date", "sources", "claims"):
        if field not in manifest:
            errors.append(f"missing root field: {field}")

    mode = normalized(manifest.get("reality_mode")).upper()
    if mode and mode not in REALITY_MODES:
        errors.append("reality_mode must be A, B, or C")

    as_of = parse_iso_date(manifest.get("as_of_date"))
    if as_of is None:
        errors.append("as_of_date must be YYYY-MM-DD")
        as_of = date.today()

    sources_value = manifest.get("sources", [])
    if not isinstance(sources_value, list):
        errors.append("sources must be a list")
        sources_value = []
    claims_value = manifest.get("claims", [])
    if not isinstance(claims_value, list):
        errors.append("claims must be a list")
        claims_value = []

    sources: list[dict[str, Any]] = []
    source_ids: set[str] = set()
    source_by_id: dict[str, dict[str, Any]] = {}
    coordinate_systems: set[str] = set()

    for index, source in enumerate(sources_value, start=1):
        if not isinstance(source, dict):
            errors.append(f"source #{index} must be an object")
            continue
        sources.append(source)
        for field in SOURCE_REQUIRED_FIELDS:
            if field not in source:
                errors.append(f"source #{index} missing field: {field}")

        source_id = normalized(source.get("id"))
        if not source_id:
            errors.append(f"source #{index} id must be non-empty")
        elif source_id in source_ids:
            errors.append(f"duplicate source id: {source_id}")
        else:
            source_ids.add(source_id)
            source_by_id[source_id] = source

        source_type = normalized(source.get("source_type"))
        if source_type not in SOURCE_TYPES:
            errors.append(f"source {source_id or index} has unsupported source_type: {source_type}")

        confidence = normalized(source.get("confidence")).lower()
        if confidence not in CONFIDENCE_VALUES:
            errors.append(f"source {source_id or index} confidence must be high, medium, or low")

        coordinate = normalized(source.get("coordinate_system")).upper()
        if coordinate:
            coordinate_systems.add(coordinate)
            if coordinate not in KNOWN_COORDINATE_SYSTEMS:
                warnings.append(f"source {source_id or index} uses custom coordinate system '{coordinate}'")

        supported = as_string_list(source.get("supported_claims"))
        unsupported = as_string_list(source.get("unsupported_claims"))
        if supported is None:
            errors.append(f"source {source_id or index} supported_claims must be a non-empty string list")
            supported = []
        if unsupported is None:
            errors.append(f"source {source_id or index} unsupported_claims must be a non-empty string list")
            unsupported = []

        if source_type in REMOTE_TYPES:
            unsupported_text = " ".join(unsupported)
            for token in ("门头", "人物", "室内", "经营"):
                if token not in unsupported_text:
                    errors.append(
                        f"remote source {source_id or index} must explicitly list '{token}' as unsupported"
                    )

        capture_raw = source.get("capture_date")
        capture = parse_iso_date(capture_raw)
        if normalized(capture_raw) and capture is None and normalized(capture_raw).lower() not in {"unknown", "n/a"}:
            errors.append(f"source {source_id or index} capture_date must be YYYY-MM-DD or 'unknown'")
        access_raw = source.get("access_date")
        access = parse_iso_date(access_raw)
        if normalized(access_raw) and access is None:
            errors.append(f"source {source_id or index} access_date must be YYYY-MM-DD")
        if capture and capture > as_of:
            errors.append(f"source {source_id or index} capture_date is after as_of_date")
        if access and access > as_of:
            errors.append(f"source {source_id or index} access_date is after as_of_date")

        permission = normalized(source.get("license_or_permission")).lower()
        if mode in {"A", "B"} and permission in {"", "unknown", "unclear", "none"}:
            errors.append(f"source {source_id or index} lacks a usable license_or_permission for mode {mode}")

        if source_type in {"site_camera", "user_asset"} and permission in {"public", "publicly visible"}:
            warnings.append(
                f"source {source_id or index} is {source_type}; public visibility alone may not establish reuse permission"
            )

    effective_coordinates = {item for item in coordinate_systems if item not in {"UNKNOWN", "N/A", "LOCAL"}}
    if len(effective_coordinates) > 1 and not normalized(manifest.get("coordinate_transform_note")):
        errors.append(
            "multiple coordinate systems detected; coordinate_transform_note is required: "
            + ", ".join(sorted(effective_coordinates))
        )

    claims: list[dict[str, Any]] = []
    claim_ids: set[str] = set()
    current_claim_count = 0
    for index, claim in enumerate(claims_value, start=1):
        if not isinstance(claim, dict):
            errors.append(f"claim #{index} must be an object")
            continue
        claims.append(claim)
        for field in CLAIM_REQUIRED_FIELDS:
            if field not in claim:
                errors.append(f"claim #{index} missing field: {field}")

        claim_id = normalized(claim.get("id"))
        if not claim_id:
            errors.append(f"claim #{index} id must be non-empty")
        elif claim_id in claim_ids:
            errors.append(f"duplicate claim id: {claim_id}")
        else:
            claim_ids.add(claim_id)

        level = normalized(claim.get("claim_level")).lower()
        status = normalized(claim.get("status")).lower()
        if level not in CLAIM_LEVELS:
            errors.append(f"claim {claim_id or index} has unsupported claim_level: {level}")
        if status not in CLAIM_STATUSES:
            errors.append(f"claim {claim_id or index} status must be observed, inferred, or original")

        ids_value = claim.get("source_ids")
        if not isinstance(ids_value, list) or not all(isinstance(item, str) for item in ids_value):
            errors.append(f"claim {claim_id or index} source_ids must be a string list")
            ids_value = []
        referenced = [item.strip() for item in ids_value if item.strip()]
        missing = [item for item in referenced if item not in source_ids]
        if missing:
            errors.append(f"claim {claim_id or index} references unknown source ids: {', '.join(missing)}")

        current_state = claim.get("current_state")
        if not isinstance(current_state, bool):
            errors.append(f"claim {claim_id or index} current_state must be boolean")
            current_state = False
        if current_state:
            current_claim_count += 1

        if status in {"observed", "inferred"} and not referenced:
            errors.append(f"claim {claim_id or index} status={status} requires source_ids")
        if status == "original" and referenced:
            warnings.append(f"claim {claim_id or index} is original but still references sources; verify wording")
        if status == "original" and current_state:
            errors.append(f"claim {claim_id or index} cannot be both original and current_state=true")

        ref_types = {normalized(source_by_id[item].get("source_type")) for item in referenced if item in source_by_id}
        if level in SENSITIVE_LEVELS and ref_types and ref_types.issubset(REMOTE_TYPES):
            errors.append(
                f"claim {claim_id or index} at level '{level}' is supported only by satellite/orthophoto"
            )

        if current_state and referenced:
            recent = False
            dated = False
            for source_id in referenced:
                source = source_by_id.get(source_id)
                if not source:
                    continue
                capture = parse_iso_date(source.get("capture_date"))
                if capture:
                    dated = True
                    if months_old(capture, as_of) <= 36:
                        recent = True
            if not dated:
                warnings.append(f"current-state claim {claim_id or index} has no dated evidence")
            elif not recent:
                warnings.append(f"current-state claim {claim_id or index} relies only on evidence older than 36 months")

    source_type_set = {normalized(source.get("source_type")) for source in sources}
    target_scope = normalized(manifest.get("target_scope")).lower()

    if mode == "A":
        if target_scope != "exact_location":
            errors.append("mode A requires target_scope='exact_location'")
        if not (source_type_set & GROUND_TYPES):
            errors.append("mode A requires at least one authorized ground/user source")
        if not (source_type_set & MACRO_TYPES):
            errors.append("mode A requires at least one macro location source")
        if not any(
            normalized(claim.get("claim_level")).lower() in {"store", "interior", "text"}
            and normalized(claim.get("status")).lower() == "observed"
            for claim in claims
        ):
            errors.append("mode A requires at least one observed store/interior/text claim")

    if mode == "B":
        if not (source_type_set & MACRO_TYPES):
            errors.append("mode B requires at least one macro source")
        if not (source_type_set & GROUND_TYPES):
            errors.append("mode B requires at least one ground/user source for store-level logic")

    if mode == "C" and not sources:
        # Allowed: concept mode can operate without external evidence.
        pass

    metrics = {
        "reality_mode": mode,
        "source_count": len(sources),
        "claim_count": len(claims),
        "current_claim_count": current_claim_count,
        "source_types": sorted(source_type_set),
        "coordinate_systems": sorted(coordinate_systems),
    }
    return errors, warnings, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="UTF-8 JSON evidence manifest")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    try:
        manifest = load_manifest(args.manifest)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: cannot load manifest: {exc}")
        return 1

    errors, warnings, metrics = audit(manifest)
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARN: {item}")
    print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))

    if errors or (args.strict and warnings):
        print(f"FAIL: errors={len(errors)} warnings={len(warnings)} strict={args.strict}")
        return 1
    print(f"PASS: errors=0 warnings={len(warnings)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
