#!/usr/bin/env python3
"""Lint universal Prompt-Only output structure and anchors."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(
    r"^【(?P<name>图\d+(?:｜[^】]+)?|场景\d+(?:｜[^】]+)?|主提示词|负面提示词|版式叠字提示词|文字定向编辑提示词|一致性锁定提示词)】$"
)
CONTAINER_RE = re.compile(r"^(?:图|场景)\d+")

PROHIBITED_META = (
    "以下是分析",
    "世界卡",
    "证据报告",
    "质检结论",
    "评分：",
    "我将",
    "我已经",
    "已为你生成",
    "调用图像",
    "调用工具",
    "下载地址",
    "sandbox:",
)

PROHIBITED_CLAIMS = (
    "保证治愈",
    "保证收益",
    "稳赚",
    "保过",
    "真实顾客证言",
    "真实新闻现场",
    "销量第一",
    "全网第一",
)

REQUIRED_ANCHORS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("use case", ("Use case", "用途")),
    ("content objective", ("Content objective", "内容目标")),
    ("reality mode", ("Reality mode", "真实性模式")),
    ("asset", ("Asset", "平台与画幅", "画幅与图位")),
    ("world context", ("World context", "世界语境", "地域与时间")),
    ("spatial logic", ("Spatial logic", "空间逻辑", "空间几何")),
    ("subject identity", ("Subject identity", "主体身份")),
    ("objects and process", ("Objects & process", "物体与流程", "道具与动作")),
    ("camera and composition", ("Camera & composition", "机位与构图", "摄影与构图")),
    ("lighting and materials", ("Lighting & materials", "光线与材质")),
    ("text and brand", ("Text & brand", "文字与品牌")),
    ("continuity", ("Continuity locks", "连续性锁", "一致性锁")),
    ("truth boundary", ("Truth boundary", "事实边界")),
)


def parse_sections(text: str) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    first_nonblank = next((line.strip() for line in lines if line.strip()), "")
    if not first_nonblank.startswith("【"):
        errors.append("output must begin with an allowed bracketed heading")

    groups: list[dict[str, Any]] = [{"name": "default", "sections": {}}]
    current = groups[0]
    current_section: str | None = None

    for line_number, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        match = HEADING_RE.match(stripped)
        if match:
            name = match.group("name")
            if CONTAINER_RE.match(name):
                if current["name"] == "default" and not current["sections"]:
                    current["name"] = name
                else:
                    current = {"name": name, "sections": {}}
                    groups.append(current)
                current_section = None
                continue
            if name in current["sections"]:
                errors.append(f"group {current['name']} repeats section: {name}")
            current["sections"][name] = []
            current_section = name
            continue
        if stripped.startswith("【") and stripped.endswith("】"):
            errors.append(f"line {line_number} unsupported heading: {stripped}")
            continue
        if stripped:
            if current_section is None:
                errors.append(f"line {line_number} has text outside an allowed section")
            else:
                current["sections"][current_section].append(raw)
        elif current_section is not None:
            current["sections"][current_section].append(raw)

    return [group for group in groups if group["sections"] or group["name"] != "default"], errors


def section_text(group: dict[str, Any], name: str) -> str:
    return "\n".join(group["sections"].get(name, [])).strip()


def chinese_in_quotes(text: str) -> int:
    segments = re.findall(r'["“]([^"”]+)["”]', text)
    return max((len(re.findall(r"[\u4e00-\u9fff]", segment)) for segment in segments), default=0)


def audit(text: str) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    for phrase in PROHIBITED_META:
        if phrase in text:
            errors.append(f"prohibited meta-output detected: {phrase}")
    for phrase in PROHIBITED_CLAIMS:
        if phrase in text:
            errors.append(f"prohibited claim detected: {phrase}")

    groups, parse_errors = parse_sections(text)
    errors.extend(parse_errors)
    if not groups:
        errors.append("no prompt groups found")
        return errors, warnings, {"group_count": 0}

    for group in groups:
        name = group["name"]
        main = section_text(group, "主提示词")
        negative = section_text(group, "负面提示词")
        overlay = section_text(group, "版式叠字提示词")
        text_edit = section_text(group, "文字定向编辑提示词")
        consistency = section_text(group, "一致性锁定提示词")
        if not main:
            errors.append(f"group {name} missing non-empty 主提示词")
            continue
        if not negative:
            errors.append(f"group {name} missing non-empty 负面提示词")
        elif len(negative) < 20:
            warnings.append(f"group {name} negative prompt is unusually short")

        for label, alternatives in REQUIRED_ANCHORS:
            if not any(alt.casefold() in main.casefold() for alt in alternatives):
                errors.append(f"group {name} main prompt missing anchor: {label}")

        if not re.search(r"(?:Reality mode|真实性模式)\s*[:：]?\s*(?:[ABCD]\b|[ABCD]\s*级)", main, re.IGNORECASE):
            errors.append(f"group {name} does not declare A/B/C/D reality mode")

        if "Truth boundary" in main or "事实边界" in main:
            recognized = (
                "同一授权",
                "同类原创场景",
                "原创真实感场景",
                "拟真虚构",
                "重建场景",
            )
            if not any(phrase in main for phrase in recognized):
                warnings.append(f"group {name} truth boundary is not a recognized statement")

        if chinese_in_quotes(main) > 6 and not (overlay or text_edit):
            warnings.append(f"group {name} has long quoted Chinese text but no overlay/edit prompt")

        social_signal = any(word in main for word in ("小红书", "抖音", "视频号", "公众号", "电商", "公开传播", "营销"))
        if social_signal and not any(word in main for word in ("Public-use note", "公开传播", "AI生成", "概念图")):
            warnings.append(f"group {name} appears public-facing but lacks public-use note")

        continuity_signal = any(word in main for word in ("同一人物", "同一产品", "同一空间", "系列", "多比例", "9:16", "3:4"))
        if continuity_signal and not consistency:
            warnings.append(f"group {name} appears to need continuity but lacks consistency lock prompt")

        if re.search(r"卫星.{0,16}(门头|人物|室内|顾客|营业|事故)", main):
            errors.append(f"group {name} may overclaim satellite-scale evidence")

    metrics = {
        "group_count": len(groups),
        "sections_per_group": {group["name"]: sorted(group["sections"]) for group in groups},
    }
    return errors, warnings, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt_file", type=Path, help="UTF-8 Prompt-Only output")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()
    try:
        text = args.prompt_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FAIL: cannot read prompt file: {exc}")
        return 1
    errors, warnings, metrics = audit(text)
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARN: {item}")
    print(metrics)
    if errors or (args.strict and warnings):
        print(f"FAIL: errors={len(errors)} warnings={len(warnings)} strict={args.strict}")
        return 1
    print(f"PASS: errors=0 warnings={len(warnings)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
