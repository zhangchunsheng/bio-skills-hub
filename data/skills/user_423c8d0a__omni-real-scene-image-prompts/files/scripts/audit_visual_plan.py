#!/usr/bin/env python3
"""Audit universal visual plans for diversity and continuity.

Supported modes: batch, series, multiratio, same_subject, scene_swap, audience_swap.
The script validates planning metadata only and never calls an image model.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable


MODES = {"batch", "series", "multiratio", "same_subject", "scene_swap", "audience_swap"}
TRUTH_MODES = {"A", "B", "C", "D"}

REQUIRED_FIELDS = (
    "id",
    "series_id",
    "truth_mode",
    "domain",
    "audience",
    "content_objective",
    "platform",
    "aspect_ratio",
    "asset_role",
    "geography",
    "space_type",
    "time_weather",
    "subject_identity",
    "key_objects",
    "primary_action",
    "emotional_evidence",
    "camera_view",
    "composition",
    "focal_length",
    "lighting",
    "materials_palette",
    "text_strategy",
    "continuity_signature",
    "truth_boundary",
)

DIVERSITY_AXES = (
    "domain",
    "audience",
    "content_objective",
    "platform",
    "geography",
    "space_type",
    "time_weather",
    "subject_identity",
    "key_objects",
    "primary_action",
    "emotional_evidence",
    "camera_view",
    "composition",
    "focal_length",
    "lighting",
    "materials_palette",
    "text_strategy",
    "asset_role",
)

SERIES_LOCK_FIELDS = (
    "series_id",
    "truth_mode",
    "domain",
    "geography",
    "space_type",
    "subject_identity",
    "continuity_signature",
    "truth_boundary",
)

MULTIRATIO_LOCK_FIELDS = (
    "series_id",
    "truth_mode",
    "domain",
    "audience",
    "content_objective",
    "geography",
    "space_type",
    "time_weather",
    "subject_identity",
    "key_objects",
    "primary_action",
    "emotional_evidence",
    "lighting",
    "materials_palette",
    "continuity_signature",
    "truth_boundary",
)

SAME_SUBJECT_LOCK_FIELDS = (
    "series_id",
    "truth_mode",
    "subject_identity",
    "continuity_signature",
)

SCENE_SWAP_LOCK_FIELDS = (
    "series_id",
    "truth_mode",
    "domain",
    "subject_identity",
    "key_objects",
    "continuity_signature",
)

SCENE_SWAP_ENV_FIELDS = (
    "geography",
    "space_type",
    "time_weather",
    "audience",
    "primary_action",
    "camera_view",
    "lighting",
    "materials_palette",
)

AUDIENCE_SWAP_LOCK_FIELDS = (
    "series_id",
    "truth_mode",
    "domain",
    "geography",
    "space_type",
    "time_weather",
    "subject_identity",
    "key_objects",
    "camera_view",
    "lighting",
    "materials_palette",
    "continuity_signature",
)


def normalized(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return " | ".join(sorted(normalized(item) for item in value))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).casefold()
    return " ".join(str(value).strip().split()).casefold()


def nonempty(value: Any) -> bool:
    return normalized(value) != ""


def load_plan(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        return {"mode": "batch", "items": data}
    if not isinstance(data, dict):
        raise ValueError("plan root must be an object or list")
    return data


def pairwise_distance(a: dict[str, Any], b: dict[str, Any], fields: Iterable[str]) -> int:
    return sum(normalized(a.get(field)) != normalized(b.get(field)) for field in fields)


def duplicates(items: list[dict[str, Any]], field: str) -> list[str]:
    values = [normalized(item.get(field)) for item in items]
    return sorted(value for value, count in Counter(values).items() if value and count > 1)


def check_locked(items: list[dict[str, Any]], fields: Iterable[str], label: str, errors: list[str]) -> None:
    for field in fields:
        values = {normalized(item.get(field)) for item in items if nonempty(item.get(field))}
        if len(values) != 1:
            errors.append(f"{label} drift in {field}: {sorted(values)}")


def validate_common(raw_items: Any, errors: list[str]) -> list[dict[str, Any]]:
    if not isinstance(raw_items, list) or not raw_items:
        errors.append("items must be a non-empty list")
        return []
    items: list[dict[str, Any]] = []
    for index, item in enumerate(raw_items, start=1):
        if not isinstance(item, dict):
            errors.append(f"item #{index} must be an object")
            continue
        items.append(item)
        for field in REQUIRED_FIELDS:
            if not nonempty(item.get(field)):
                errors.append(f"item #{index} missing non-empty field: {field}")
        mode = str(item.get("truth_mode", "")).strip().upper()
        if mode and mode not in TRUTH_MODES:
            errors.append(f"item #{index} truth_mode must be A, B, C, or D")
        ratio = normalized(item.get("aspect_ratio"))
        if ratio and ":" not in ratio:
            errors.append(f"item #{index} aspect_ratio must look like W:H")
    duplicate_ids = duplicates(items, "id")
    if duplicate_ids:
        errors.append("duplicate ids: " + ", ".join(duplicate_ids))
    return items


def audit_batch(plan: dict[str, Any], items: list[dict[str, Any]], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    minimum = int(plan.get("pairwise_min_differences", 8))
    if minimum < 5 or minimum > len(DIVERSITY_AXES):
        errors.append(f"pairwise_min_differences must be 5..{len(DIVERSITY_AXES)}")
        minimum = 8
    distances: list[tuple[str, str, int]] = []
    for first, second in combinations(items, 2):
        distance = pairwise_distance(first, second, DIVERSITY_AXES)
        pair = (str(first.get("id")), str(second.get("id")), distance)
        distances.append(pair)
        if distance < minimum:
            errors.append(
                f"pairwise diversity too low: {pair[0]} vs {pair[1]} = {distance}/{len(DIVERSITY_AXES)}, required >= {minimum}"
            )
    signatures = [tuple(normalized(item.get(field)) for field in DIVERSITY_AXES) for item in items]
    if any(count > 1 for count in Counter(signatures).values()):
        errors.append("duplicate full visual signatures detected")

    counts = {
        field: len({normalized(item.get(field)) for item in items if nonempty(item.get(field))})
        for field in DIVERSITY_AXES
    }
    if len(items) >= 6:
        for field in ("space_type", "primary_action", "camera_view", "composition", "asset_role"):
            if counts[field] < 3:
                warnings.append(f"low batch coverage for {field}: {counts[field]} unique")
        for field in ("subject_identity", "camera_view", "lighting", "materials_palette"):
            values = [normalized(item.get(field)) for item in items]
            value, frequency = Counter(values).most_common(1)[0]
            if frequency > math.ceil(len(items) / 2):
                warnings.append(f"{field} dominated by '{value}' in {frequency}/{len(items)} items")
    weakest = min(distances, key=lambda row: row[2]) if distances else None
    return {
        "pairwise_required": minimum,
        "pairwise_min": weakest[2] if weakest else None,
        "weakest_pair": [weakest[0], weakest[1]] if weakest else [],
        "unique_counts": counts,
    }


def audit_series(items: list[dict[str, Any]], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    check_locked(items, SERIES_LOCK_FIELDS, "series identity", errors)
    roles = [normalized(item.get("asset_role")) for item in items]
    duplicate_roles = sorted(value for value, count in Counter(roles).items() if value and count > 1)
    if duplicate_roles:
        warnings.append("series repeats asset roles: " + ", ".join(duplicate_roles))
    view_count = len({normalized(item.get("camera_view")) for item in items})
    action_count = len({normalized(item.get("primary_action")) for item in items})
    if len(items) >= 2 and view_count < 2:
        errors.append("series requires at least two camera views")
    if len(items) >= 3 and action_count < 2:
        errors.append("series requires action progression")
    if len(items) >= 5 and len(set(roles)) < 4:
        warnings.append("five-image series should usually have at least four asset roles")
    return {"view_count": view_count, "action_count": action_count, "role_count": len(set(roles))}


def audit_multiratio(items: list[dict[str, Any]], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    check_locked(items, MULTIRATIO_LOCK_FIELDS, "multiratio identity", errors)
    ratios = [normalized(item.get("aspect_ratio")) for item in items]
    if len(set(ratios)) != len(ratios):
        errors.append("multiratio requires unique aspect_ratio values")
    composition_count = len({normalized(item.get("composition")) for item in items})
    if len(items) >= 2 and composition_count < 2:
        errors.append("multiratio versions must be recomposed, not identical crops")
    if len({normalized(item.get("text_strategy")) for item in items}) < 2:
        warnings.append("multiratio text strategies are identical; verify safe zones were recalculated")
    return {"ratios": ratios, "composition_count": composition_count}


def audit_same_subject(plan: dict[str, Any], items: list[dict[str, Any]], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    check_locked(items, SAME_SUBJECT_LOCK_FIELDS, "same_subject identity", errors)
    fields = ("geography", "space_type", "time_weather", "primary_action", "camera_view", "composition")
    minimum = int(plan.get("same_subject_min_differences", 3))
    distances = [pairwise_distance(a, b, fields) for a, b in combinations(items, 2)]
    if distances and min(distances) < minimum:
        errors.append(f"same_subject variants require at least {minimum} contextual differences")
    return {"pairwise_min_context_difference": min(distances) if distances else None}


def audit_scene_swap(plan: dict[str, Any], items: list[dict[str, Any]], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    check_locked(items, SCENE_SWAP_LOCK_FIELDS, "scene_swap subject", errors)
    minimum = int(plan.get("scene_swap_min_environment_differences", 4))
    distances = [pairwise_distance(a, b, SCENE_SWAP_ENV_FIELDS) for a, b in combinations(items, 2)]
    if distances and min(distances) < minimum:
        errors.append(f"scene_swap requires at least {minimum} environment differences")
    return {"pairwise_min_environment_difference": min(distances) if distances else None}


def audit_audience_swap(items: list[dict[str, Any]], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    check_locked(items, AUDIENCE_SWAP_LOCK_FIELDS, "audience_swap world", errors)
    audience_count = len({normalized(item.get("audience")) for item in items})
    action_count = len({normalized(item.get("primary_action")) for item in items})
    if audience_count < 2:
        errors.append("audience_swap requires at least two audiences")
    if action_count < 2:
        errors.append("audience_swap must recalculate actions, not only faces or clothes")
    return {"audience_count": audience_count, "action_count": action_count}


def audit(plan: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    mode = normalized(plan.get("mode")) or "batch"
    if mode not in MODES:
        errors.append(f"unsupported mode: {mode}; expected {sorted(MODES)}")
    items = validate_common(plan.get("items"), errors)
    metrics: dict[str, Any] = {"mode": mode, "item_count": len(items)}
    if not items:
        return errors, warnings, metrics
    if mode == "batch":
        metrics.update(audit_batch(plan, items, errors, warnings))
    elif mode == "series":
        metrics.update(audit_series(items, errors, warnings))
    elif mode == "multiratio":
        metrics.update(audit_multiratio(items, errors, warnings))
    elif mode == "same_subject":
        metrics.update(audit_same_subject(plan, items, errors, warnings))
    elif mode == "scene_swap":
        metrics.update(audit_scene_swap(plan, items, errors, warnings))
    elif mode == "audience_swap":
        metrics.update(audit_audience_swap(items, errors, warnings))
    return errors, warnings, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="UTF-8 JSON visual plan")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()
    try:
        plan = load_plan(args.plan)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: cannot load plan: {exc}")
        return 1
    errors, warnings, metrics = audit(plan)
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
