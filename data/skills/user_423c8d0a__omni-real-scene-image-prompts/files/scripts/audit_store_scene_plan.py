#!/usr/bin/env python3
"""Audit multi-store diversity, same-store continuity, scene swaps, or crowd swaps.

The script validates planning metadata only. It never calls an image model.
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


MODES = {"multi_store", "same_store", "scene_swap", "crowd_swap"}
TRUTH_MODES = {"A", "B", "C"}

COMMON_REQUIRED_FIELDS = (
    "id",
    "store_id",
    "truth_mode",
    "administrative_context",
    "urban_morphology",
    "micro_context",
    "land_use",
    "property_type",
    "building_period",
    "road_system",
    "store_category",
    "store_subtype",
    "geometry_signature",
    "price_band",
    "facade_structure",
    "materials_palette",
    "time_weather",
    "people_mobility",
    "operation_action",
    "camera_view",
    "storefront_text",
    "identity_signature",
)

DIVERSITY_AXES = (
    "administrative_context",
    "urban_morphology",
    "micro_context",
    "land_use",
    "property_type",
    "building_period",
    "road_system",
    "store_category",
    "store_subtype",
    "geometry_signature",
    "price_band",
    "facade_structure",
    "materials_palette",
    "time_weather",
    "people_mobility",
    "operation_action",
    "camera_view",
)

SAME_STORE_LOCK_FIELDS = (
    "store_id",
    "truth_mode",
    "administrative_context",
    "urban_morphology",
    "micro_context",
    "land_use",
    "property_type",
    "building_period",
    "road_system",
    "store_category",
    "store_subtype",
    "geometry_signature",
    "price_band",
    "facade_structure",
    "materials_palette",
    "storefront_text",
    "identity_signature",
)

SCENE_SWAP_IDENTITY_LOCK_FIELDS = (
    "store_id",
    "truth_mode",
    "store_category",
    "store_subtype",
    "price_band",
    "storefront_text",
    "identity_signature",
)

SCENE_SWAP_ENVIRONMENT_FIELDS = (
    "administrative_context",
    "urban_morphology",
    "micro_context",
    "land_use",
    "property_type",
    "building_period",
    "road_system",
    "time_weather",
    "people_mobility",
)

CROWD_SWAP_LOCK_FIELDS = (
    "store_id",
    "truth_mode",
    "administrative_context",
    "urban_morphology",
    "micro_context",
    "land_use",
    "property_type",
    "building_period",
    "road_system",
    "store_category",
    "store_subtype",
    "geometry_signature",
    "price_band",
    "facade_structure",
    "materials_palette",
    "time_weather",
    "camera_view",
    "storefront_text",
    "identity_signature",
)


def normalized(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split()).casefold()


def nonempty(value: Any) -> bool:
    return normalized(value) != ""


def load_plan(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        return {"mode": "multi_store", "scenes": data}
    if not isinstance(data, dict):
        raise ValueError("plan root must be a JSON object or scene list")
    return data


def pairwise_distance(a: dict[str, Any], b: dict[str, Any], fields: Iterable[str]) -> int:
    return sum(normalized(a.get(field)) != normalized(b.get(field)) for field in fields)


def duplicate_values(scenes: list[dict[str, Any]], field: str) -> list[str]:
    values = [normalized(scene.get(field)) for scene in scenes]
    return sorted(value for value, count in Counter(values).items() if value and count > 1)


def validate_common(scenes: list[Any], errors: list[str]) -> list[dict[str, Any]]:
    valid: list[dict[str, Any]] = []
    for index, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            errors.append(f"scene #{index} must be an object")
            continue
        valid.append(scene)
        for field in COMMON_REQUIRED_FIELDS:
            if not nonempty(scene.get(field)):
                errors.append(f"scene #{index} missing non-empty field: {field}")
        truth_mode = str(scene.get("truth_mode", "")).strip().upper()
        if truth_mode and truth_mode not in TRUTH_MODES:
            errors.append(f"scene #{index} truth_mode must be A, B, or C")

    duplicate_ids = duplicate_values(valid, "id")
    if duplicate_ids:
        errors.append("duplicate scene ids: " + ", ".join(duplicate_ids))
    return valid


def check_locked_fields(
    scenes: list[dict[str, Any]], fields: Iterable[str], label: str, errors: list[str]
) -> None:
    for field in fields:
        values = {normalized(scene.get(field)) for scene in scenes if nonempty(scene.get(field))}
        if len(values) != 1:
            errors.append(f"{label} drift in {field}: {sorted(values)}")


def audit_multi_store(
    plan: dict[str, Any], scenes: list[dict[str, Any]], errors: list[str], warnings: list[str]
) -> dict[str, Any]:
    repeated_store_ids = duplicate_values(scenes, "store_id")
    if repeated_store_ids:
        errors.append("multi_store repeats store_id: " + ", ".join(repeated_store_ids))

    requested = plan.get("pairwise_min_differences", 7)
    try:
        minimum = int(requested)
    except (TypeError, ValueError):
        errors.append("pairwise_min_differences must be an integer")
        minimum = 7
    if minimum < 5 or minimum > len(DIVERSITY_AXES):
        errors.append(f"pairwise_min_differences must be between 5 and {len(DIVERSITY_AXES)}")
        minimum = 7

    pair_distances: list[tuple[str, str, int]] = []
    for first, second in combinations(scenes, 2):
        distance = pairwise_distance(first, second, DIVERSITY_AXES)
        first_id = str(first.get("id", "?"))
        second_id = str(second.get("id", "?"))
        pair_distances.append((first_id, second_id, distance))
        if distance < minimum:
            errors.append(
                f"pairwise diversity too low: {first_id} vs {second_id} = "
                f"{distance}/{len(DIVERSITY_AXES)}, required >= {minimum}"
            )

    signatures = [tuple(normalized(scene.get(field)) for field in DIVERSITY_AXES) for scene in scenes]
    duplicate_signatures = sum(1 for count in Counter(signatures).values() if count > 1)
    if duplicate_signatures:
        errors.append(f"duplicate full scene signatures: {duplicate_signatures}")

    counts = {
        field: len({normalized(scene.get(field)) for scene in scenes if nonempty(scene.get(field))})
        for field in DIVERSITY_AXES
    }

    if len(scenes) >= 6:
        for field in (
            "micro_context",
            "property_type",
            "facade_structure",
            "materials_palette",
            "people_mobility",
            "camera_view",
        ):
            if counts[field] < 3:
                warnings.append(f"low batch coverage for {field}: {counts[field]} unique, expected >= 3")

        category_target = max(4, math.ceil(len(scenes) * 0.60))
        if counts["store_subtype"] < category_target:
            warnings.append(
                f"low store_subtype coverage: {counts['store_subtype']} unique, expected >= {category_target}"
            )

    for field in ("facade_structure", "materials_palette", "camera_view"):
        values = [normalized(scene.get(field)) for scene in scenes]
        if values:
            value, frequency = Counter(values).most_common(1)[0]
            if len(values) >= 6 and frequency > math.ceil(len(values) / 2):
                warnings.append(f"{field} dominated by '{value}' in {frequency}/{len(values)} scenes")

    if pair_distances:
        weakest = min(pair_distances, key=lambda item: item[2])
        return {
            "pairwise_required": minimum,
            "pairwise_min": weakest[2],
            "weakest_pair": [weakest[0], weakest[1]],
            "unique_counts": counts,
        }
    return {"pairwise_required": minimum, "pairwise_min": None, "weakest_pair": [], "unique_counts": counts}


def audit_same_store(
    scenes: list[dict[str, Any]], errors: list[str], warnings: list[str]
) -> dict[str, Any]:
    check_locked_fields(scenes, SAME_STORE_LOCK_FIELDS, "same_store identity/context", errors)
    view_count = len({normalized(scene.get("camera_view")) for scene in scenes})
    action_count = len({normalized(scene.get("operation_action")) for scene in scenes})
    people_count = len({normalized(scene.get("people_mobility")) for scene in scenes})
    if len(scenes) >= 2 and view_count < 2:
        errors.append("same_store requires at least 2 distinct camera_view values")
    if len(scenes) >= 2 and action_count < 2:
        errors.append("same_store requires at least 2 distinct operation_action values")
    if len(scenes) >= 6 and view_count < 4:
        warnings.append(f"six-image same_store set has only {view_count} distinct camera views")
    return {"view_count": view_count, "action_count": action_count, "people_count": people_count}


def audit_scene_swap(
    plan: dict[str, Any], scenes: list[dict[str, Any]], errors: list[str], warnings: list[str]
) -> dict[str, Any]:
    check_locked_fields(scenes, SCENE_SWAP_IDENTITY_LOCK_FIELDS, "scene_swap brand identity", errors)
    requested = plan.get("scene_swap_min_environment_differences", 5)
    try:
        minimum = int(requested)
    except (TypeError, ValueError):
        errors.append("scene_swap_min_environment_differences must be an integer")
        minimum = 5
    if minimum < 3 or minimum > len(SCENE_SWAP_ENVIRONMENT_FIELDS):
        errors.append(
            f"scene_swap_min_environment_differences must be between 3 and "
            f"{len(SCENE_SWAP_ENVIRONMENT_FIELDS)}"
        )
        minimum = 5

    distances: list[tuple[str, str, int]] = []
    for first, second in combinations(scenes, 2):
        distance = pairwise_distance(first, second, SCENE_SWAP_ENVIRONMENT_FIELDS)
        first_id = str(first.get("id", "?"))
        second_id = str(second.get("id", "?"))
        distances.append((first_id, second_id, distance))
        if distance < minimum:
            errors.append(
                f"scene_swap environment change too small: {first_id} vs {second_id} = "
                f"{distance}/{len(SCENE_SWAP_ENVIRONMENT_FIELDS)}, required >= {minimum}"
            )

    # Geometry/facade should normally adapt rather than remain cloned across all different properties.
    if len(scenes) >= 2:
        for field in ("geometry_signature", "facade_structure"):
            if len({normalized(scene.get(field)) for scene in scenes}) == 1:
                warnings.append(f"scene_swap keeps identical {field}; verify the store was not pasted onto new backgrounds")

    weakest = min(distances, key=lambda item: item[2]) if distances else None
    return {
        "environment_required": minimum,
        "environment_min": weakest[2] if weakest else None,
        "weakest_pair": [weakest[0], weakest[1]] if weakest else [],
    }


def audit_crowd_swap(
    scenes: list[dict[str, Any]], errors: list[str], warnings: list[str]
) -> dict[str, Any]:
    check_locked_fields(scenes, CROWD_SWAP_LOCK_FIELDS, "crowd_swap scene/camera", errors)
    people_values = [normalized(scene.get("people_mobility")) for scene in scenes]
    action_values = [normalized(scene.get("operation_action")) for scene in scenes]
    if len(set(people_values)) != len(people_values):
        errors.append("crowd_swap requires unique people_mobility for every scene")
    if len(set(action_values)) != len(action_values):
        errors.append("crowd_swap requires unique operation_action for every scene")
    for first, second in combinations(scenes, 2):
        # Both crowd logic and operation response must change.
        distance = pairwise_distance(first, second, ("people_mobility", "operation_action"))
        if distance < 2:
            errors.append(
                f"crowd_swap is only a cosmetic replacement: {first.get('id')} vs {second.get('id')} "
                "must differ in both people_mobility and operation_action"
            )
    if len(scenes) > 8:
        warnings.append("large crowd_swap set may become repetitive; review trip purpose and transport diversity")
    return {"people_variants": len(set(people_values)), "operation_variants": len(set(action_values))}


def audit(plan: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []

    mode = str(plan.get("mode", "multi_store")).strip()
    if mode not in MODES:
        errors.append("mode must be one of: " + ", ".join(sorted(MODES)))

    scenes_value = plan.get("scenes")
    if not isinstance(scenes_value, list) or not scenes_value:
        return ["scenes must be a non-empty list"], warnings, {}

    scenes = validate_common(scenes_value, errors)
    metrics: dict[str, Any] = {"mode": mode, "scene_count": len(scenes)}
    if not scenes:
        return errors, warnings, metrics

    if mode == "multi_store":
        metrics.update(audit_multi_store(plan, scenes, errors, warnings))
    elif mode == "same_store":
        metrics.update(audit_same_store(scenes, errors, warnings))
    elif mode == "scene_swap":
        metrics.update(audit_scene_swap(plan, scenes, errors, warnings))
    elif mode == "crowd_swap":
        metrics.update(audit_crowd_swap(scenes, errors, warnings))

    return errors, warnings, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="UTF-8 JSON scene plan")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
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
