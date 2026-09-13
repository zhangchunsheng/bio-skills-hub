#!/usr/bin/env python3
"""Validate universal R12 scene-world cards.

The validator checks planning consistency, not the final generated pixels.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


TRUTH_MODES = {"A", "B", "C", "D"}
REQUIRED_FIELDS = (
    "id",
    "truth_mode",
    "content_objective",
    "platform",
    "aspect_ratio",
    "asset_role",
    "domain",
    "audience",
    "world_context",
    "spatial_logic",
    "subject_identity",
    "key_objects",
    "primary_action",
    "people_relations",
    "camera",
    "lighting_materials",
    "text_strategy",
    "continuity",
    "truth_boundary",
)

HIGH_RISK_CLAIMS = (
    "保证治愈",
    "保证收益",
    "稳赚",
    "保过",
    "官方认证",
    "真实新闻现场",
    "真实顾客证言",
    "销量第一",
    "全网第一",
)


def nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple)):
        return len(value) > 0
    return True


def validate_card(card: Any, index: int) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    label = f"card #{index}"
    if not isinstance(card, dict):
        return [f"{label} must be an object"], warnings
    for field in REQUIRED_FIELDS:
        if not nonempty(card.get(field)):
            errors.append(f"{label} missing non-empty field: {field}")

    mode = str(card.get("truth_mode", "")).strip().upper()
    if mode and mode not in TRUTH_MODES:
        errors.append(f"{label} truth_mode must be A, B, C, or D")

    ratio = str(card.get("aspect_ratio", "")).strip()
    if ratio and not re.fullmatch(r"\d+(?:\.\d+)?:\d+(?:\.\d+)?", ratio):
        errors.append(f"{label} aspect_ratio must look like W:H")

    for field in ("world_context", "spatial_logic", "camera", "lighting_materials", "text_strategy", "continuity"):
        if field in card and not isinstance(card.get(field), dict):
            errors.append(f"{label} {field} must be an object")

    if "key_objects" in card and not isinstance(card.get("key_objects"), list):
        errors.append(f"{label} key_objects must be a list")

    boundary = str(card.get("truth_boundary", ""))
    if mode == "A":
        sources = card.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{label} mode A requires non-empty sources")
        permission = str(card.get("permission", "")).strip().lower()
        if permission not in {"authorized", "user_owned", "licensed"}:
            errors.append(f"{label} mode A requires authorized permission")
        if "同一" not in boundary and "授权" not in boundary:
            warnings.append(f"{label} mode A boundary should state same authorized subject/location")
    elif mode == "B":
        if "同类原创" not in boundary:
            warnings.append(f"{label} mode B boundary should say 同类原创")
    elif mode == "C":
        if "原创真实感" not in boundary and "原创概念" not in boundary:
            warnings.append(f"{label} mode C boundary should say 原创真实感/原创概念")
    elif mode == "D":
        if "拟真虚构" not in boundary and "重建" not in boundary:
            errors.append(f"{label} mode D boundary must state 拟真虚构 or 重建")

    camera = card.get("camera", {}) if isinstance(card.get("camera"), dict) else {}
    for field in ("location", "height", "distance", "angle", "focal_length", "composition"):
        if camera and not nonempty(camera.get(field)):
            errors.append(f"{label} camera missing {field}")

    spatial = card.get("spatial_logic", {}) if isinstance(card.get("spatial_logic"), dict) else {}
    if spatial and not nonempty(spatial.get("affordance_check")):
        warnings.append(f"{label} spatial_logic lacks affordance_check")

    text_strategy = card.get("text_strategy", {}) if isinstance(card.get("text_strategy"), dict) else {}
    p0 = str(text_strategy.get("p0_text", ""))
    overlay = str(text_strategy.get("render_strategy", ""))
    chinese_count = len(re.findall(r"[\u4e00-\u9fff]", p0))
    if chinese_count > 6 and overlay not in {"post_overlay", "two_stage", "edit_only"}:
        warnings.append(f"{label} has long P0 Chinese text without two-stage/post-overlay strategy")

    serialized = json.dumps(card, ensure_ascii=False)
    for phrase in HIGH_RISK_CLAIMS:
        if phrase in serialized:
            errors.append(f"{label} contains prohibited high-risk claim: {phrase}")

    if re.search(r"卫星.{0,16}(门头|人物|室内|顾客|营业|事故)", serialized):
        errors.append(f"{label} may overclaim satellite-scale evidence")

    public_use = bool(card.get("public_use", False))
    if public_use and not nonempty(card.get("public_use_note")):
        warnings.append(f"{label} public_use=true but public_use_note is empty")

    return errors, warnings


def load_cards(path: Path) -> list[Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("scenes"), list):
        return data["scenes"]
    if isinstance(data, dict):
        return [data]
    raise ValueError("JSON root must be an object, scene list, or {scenes:[...]} object")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene_world", type=Path, help="UTF-8 JSON scene world card")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()
    try:
        cards = load_cards(args.scene_world)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: cannot load scene world: {exc}")
        return 1
    errors: list[str] = []
    warnings: list[str] = []
    for index, card in enumerate(cards, start=1):
        card_errors, card_warnings = validate_card(card, index)
        errors.extend(card_errors)
        warnings.extend(card_warnings)
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARN: {item}")
    print(json.dumps({"scene_count": len(cards), "errors": len(errors), "warnings": len(warnings)}, ensure_ascii=False))
    if errors or (args.strict and warnings):
        print(f"FAIL: errors={len(errors)} warnings={len(warnings)} strict={args.strict}")
        return 1
    print(f"PASS: errors=0 warnings={len(warnings)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
