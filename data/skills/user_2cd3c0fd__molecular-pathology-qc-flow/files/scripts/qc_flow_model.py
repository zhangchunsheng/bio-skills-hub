#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分子病理质控流程的数据读取、兼容转换和语义校验。

说明：模型层只负责数据契约和业务结构校验，不承担布局或 XML 持久化。
Author: WangYunL
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict, deque
from copy import deepcopy
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.1"
ID_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
RESERVED_ID_PREFIXES = ("_meta_", "_stage_")

NODE_STYLES = {
    "start": (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=50;"
        "fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;"
    ),
    "process": (
        "rounded=1;whiteSpace=wrap;html=1;"
        "fillColor=#dae8fc;strokeColor=#6c8ebf;"
    ),
    "decision": (
        "rhombus;whiteSpace=wrap;html=1;"
        "fillColor=#fff2cc;strokeColor=#d6b656;"
    ),
    "positive": (
        "rounded=1;whiteSpace=wrap;html=1;"
        "fillColor=#d5e8d4;strokeColor=#82b366;"
    ),
    "pass": (
        "rounded=1;whiteSpace=wrap;html=1;"
        "fillColor=#d5e8d4;strokeColor=#82b366;"
    ),
    "negative": (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=50;"
        "fillColor=#f5f5f5;strokeColor=#999999;"
    ),
    "invalid": (
        "rounded=1;whiteSpace=wrap;html=1;"
        "fillColor=#f8cecc;strokeColor=#b85450;"
    ),
    "warning": (
        "rounded=1;whiteSpace=wrap;html=1;"
        "fillColor=#ffe6cc;strokeColor=#d79b00;"
    ),
    "end": (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=50;"
        "fillColor=#f5f5f5;strokeColor=#999999;"
    ),
}

NODE_SIZES = {
    "start": (220.0, 48.0),
    "process": (280.0, 56.0),
    "decision": (240.0, 90.0),
    "positive": (220.0, 60.0),
    "pass": (220.0, 60.0),
    "negative": (220.0, 56.0),
    "invalid": (240.0, 64.0),
    "warning": (240.0, 64.0),
    "end": (220.0, 56.0),
}

TERMINAL_TYPES = {"positive", "pass", "negative", "invalid", "end"}
TERMINAL_RESULTS = {
    "positive",
    "negative",
    "pass",
    "invalid",
    "manual_review",
    "end",
}
CONDITION_OPERATORS = {
    "EQ",
    "NE",
    "LT",
    "LE",
    "GT",
    "GE",
    "BETWEEN_CLOSED",
    "BETWEEN_OPEN",
    "IN",
    "EXISTS",
    "MISSING",
    "CUSTOM",
}
BRANCH_TYPES = {
    "next",
    "yes",
    "no",
    "pass",
    "fail",
    "positive",
    "negative",
    "invalid",
    "manual_review",
    "repeat",
}
SOURCE_TYPES = {
    "user-file",
    "laboratory-sop",
    "validation-report",
    "manufacturer-ifu",
    "regulatory",
    "professional-guideline",
    "public-database",
    "official-technical-document",
    "user-confirmed",
}
EVIDENCE_STATUSES = {"confirmed", "inferred", "unknown", "conflict"}
MISSING_POLICIES = {
    "fail",
    "pass",
    "invalid",
    "next_branch",
    "manual_review",
    "not_applicable",
}


class SpecValidationError(ValueError):
    """表示质控 JSON 不满足生成约束。"""


def configure_console_encoding() -> None:
    """在 Windows 命令行中统一使用 UTF-8 输出中文。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def load_spec(path: Path) -> dict[str, Any]:
    """以 UTF-8 读取并解析质控 JSON。"""
    raw = path.read_text(encoding="utf-8-sig")
    if "\ufffd" in raw:
        raise SpecValidationError(f"输入文件包含中文替换字符：{path}")

    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SpecValidationError(
            f"JSON 解析失败：第 {exc.lineno} 行，第 {exc.colno} 列，{exc.msg}"
        ) from exc

    if not isinstance(value, dict):
        raise SpecValidationError("JSON 根节点必须是对象。")
    return value


def _legacy_source(diagram: dict[str, Any]) -> list[dict[str, Any]]:
    """把 1.0 的 diagram.source 转换为 1.1 生成器可读取的来源列表。"""
    source = diagram.get("source")
    if not isinstance(source, dict):
        return []
    title = str(source.get("name") or source.get("title") or "旧版来源").strip()
    return [
        {
            "id": "legacy_source",
            "type": "user-file",
            "title": title,
            "version": str(source.get("version") or "未提供"),
            "path": title,
            "last_verified": "未提供",
            "scope_note": str(source.get("scope_note") or "旧版输入未注明适用范围"),
            "evidence_status": "unknown",
        }
    ]


def _infer_branch(label: str, source_type: str) -> str:
    """为旧版连线补充兼容分支语义，不改变原显示文字。"""
    normalized = label.strip().lower()
    if source_type != "decision":
        return "next"
    if normalized.startswith("是") or normalized in {"yes", "y"}:
        return "yes"
    if normalized.startswith("否") or normalized in {"no", "n"}:
        return "no"
    if "阳性" in normalized:
        return "positive"
    if "阴性" in normalized or "未检出" in normalized:
        return "negative"
    if "无效" in normalized or "失败" in normalized:
        return "invalid"
    if "复" in normalized:
        return "repeat"
    return "next"


def normalize_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """复制并规范化输入；保留 1.0 输入兼容，不回写用户文件。"""
    normalized = deepcopy(spec)
    version = str(normalized.get("schema_version") or "1.0").strip()
    normalized["schema_version"] = version
    normalized.setdefault("measurements", [])

    diagram = normalized.get("diagram")
    if not isinstance(diagram, dict):
        return normalized

    sources = diagram.get("sources")
    if not isinstance(sources, list):
        sources = _legacy_source(diagram)
        diagram["sources"] = sources

    source_ids = [
        str(source.get("id", "")).strip()
        for source in sources
        if isinstance(source, dict) and str(source.get("id", "")).strip()
    ]
    default_source_refs = source_ids[:1]
    qc_stage = str(diagram.get("qc_stage") or "未确定")
    diagram.setdefault("method", "未确定")
    diagram.setdefault("technology", "未确定")
    diagram.setdefault("project", "未确定")
    diagram.setdefault("layout", {})

    nodes = normalized.get("nodes")
    if isinstance(nodes, list):
        for node in nodes:
            if not isinstance(node, dict):
                continue
            node.setdefault("stage", qc_stage)
            node.setdefault("evidence_refs", list(default_source_refs))
            if node.get("type") in TERMINAL_TYPES:
                node.setdefault(
                    "terminal_result",
                    {
                        "positive": "positive",
                        "pass": "pass",
                        "negative": "negative",
                        "invalid": "invalid",
                        "end": "end",
                    }.get(str(node.get("type")), "end"),
                )

    if not isinstance(diagram.get("stages"), list):
        stages: list[str] = []
        if isinstance(nodes, list):
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                stage = str(node.get("stage") or qc_stage).strip()
                if stage and stage not in stages:
                    stages.append(stage)
        diagram["stages"] = stages or [qc_stage]

    node_types = {
        str(node.get("id")): str(node.get("type"))
        for node in nodes or []
        if isinstance(node, dict)
    }
    edges = normalized.get("edges")
    if isinstance(edges, list):
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            source_type = node_types.get(str(edge.get("source")), "")
            edge.setdefault(
                "branch", _infer_branch(str(edge.get("label") or ""), source_type)
            )
            edge.setdefault("evidence_refs", list(default_source_refs))

    return normalized


def _check_identifier(value: str, field: str, errors: list[str]) -> None:
    """校验业务 ID，防止与生成器保留单元格冲突。"""
    if not value:
        errors.append(f"{field} 不能为空。")
    elif not ID_PATTERN.fullmatch(value):
        errors.append(f"{field} 只能使用英文字母、数字、下划线、点或连字符。")
    elif value.startswith(RESERVED_ID_PREFIXES):
        errors.append(f"{field} 使用了生成器保留前缀：{value}")


def _check_evidence_refs(
    refs: Any,
    field: str,
    source_ids: set[str],
    errors: list[str],
    required: bool,
) -> None:
    """校验证据引用是否为非空、去重且指向已声明来源。"""
    if not isinstance(refs, list):
        if required:
            errors.append(f"{field} 必须是非空数组。")
        return
    if required and not refs:
        errors.append(f"{field} 不能为空。")
    normalized_refs = [str(item).strip() for item in refs]
    if len(normalized_refs) != len(set(normalized_refs)):
        errors.append(f"{field} 存在重复来源引用。")
    missing = sorted({item for item in normalized_refs if item not in source_ids})
    if missing:
        errors.append(f"{field} 引用了不存在的来源：" + "、".join(missing))


def _validate_condition(
    condition: Any,
    prefix: str,
    measurement_ids: set[str],
    errors: list[str],
) -> None:
    """校验结构化判断条件及范围边界。"""
    if not isinstance(condition, dict):
        errors.append(f"{prefix}.condition 必须是对象。")
        return

    operator = str(condition.get("operator") or "").strip()
    expression = str(condition.get("expression") or "").strip()
    measurement = str(condition.get("measurement") or "").strip()
    missing_policy = str(condition.get("missing_policy") or "").strip()

    if operator not in CONDITION_OPERATORS:
        errors.append(f"{prefix}.condition.operator 不支持：{operator or '空'}")
    if not expression:
        errors.append(f"{prefix}.condition.expression 不能为空。")
    if missing_policy not in MISSING_POLICIES:
        errors.append(
            f"{prefix}.condition.missing_policy 不支持：{missing_policy or '空'}"
        )

    if operator != "CUSTOM":
        if not measurement:
            errors.append(f"{prefix}.condition.measurement 不能为空。")
        elif measurement not in measurement_ids:
            errors.append(
                f"{prefix}.condition.measurement 不存在：{measurement}"
            )

    if operator in {"EQ", "NE", "LT", "LE", "GT", "GE"} and "value" not in condition:
        errors.append(f"{prefix}.condition.value 不能为空。")
    if operator in {"BETWEEN_CLOSED", "BETWEEN_OPEN"}:
        lower = condition.get("lower")
        upper = condition.get("upper")
        if not isinstance(lower, (int, float)) or not isinstance(upper, (int, float)):
            errors.append(f"{prefix}.condition.lower 和 upper 必须是数字。")
        elif lower >= upper:
            errors.append(f"{prefix}.condition.lower 必须小于 upper。")
    if operator == "IN" and not isinstance(condition.get("value"), list):
        errors.append(f"{prefix}.condition.value 必须是数组。")


def validate_spec(
    spec: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """兼容规范化后，校验节点、证据、分支、可达性和终点完备性。"""
    normalized = normalize_spec(spec)
    version = str(normalized.get("schema_version") or "1.0")
    strict_v11 = version == SCHEMA_VERSION
    errors: list[str] = []
    diagram = normalized.get("diagram")
    nodes = normalized.get("nodes")
    edges = normalized.get("edges")
    measurements = normalized.get("measurements")

    if not isinstance(diagram, dict):
        errors.append("diagram 必须是对象。")
        diagram = {}
    if not isinstance(nodes, list) or not nodes:
        errors.append("nodes 必须是非空数组。")
        nodes = []
    if not isinstance(edges, list) or not edges:
        errors.append("edges 必须是非空数组。")
        edges = []
    if not isinstance(measurements, list):
        errors.append("measurements 必须是数组。")
        measurements = []

    if version not in {"1.0", SCHEMA_VERSION}:
        errors.append(f"schema_version 不支持：{version}")

    diagram_id = str(diagram.get("id") or "").strip()
    _check_identifier(diagram_id, "diagram.id", errors)
    if not str(diagram.get("name") or "").strip():
        errors.append("diagram.name 不能为空。")
    if strict_v11:
        for field in ("technology", "method", "project", "qc_stage"):
            if not str(diagram.get(field) or "").strip():
                errors.append(f"diagram.{field} 不能为空。")

    layout = diagram.get("layout")
    if strict_v11 and not isinstance(layout, dict):
        errors.append("diagram.layout 必须是对象。")
    elif isinstance(layout, dict):
        mode = str(layout.get("mode") or "flow")
        if mode not in {"flow", "swimlane"}:
            errors.append(f"diagram.layout.mode 不支持：{mode}")
        for field in ("page_width", "page_height"):
            if field in layout and (
                not isinstance(layout[field], (int, float)) or layout[field] < 400
            ):
                errors.append(f"diagram.layout.{field} 必须是大于等于 400 的数字。")

    stages_value = diagram.get("stages")
    stages = [str(item).strip() for item in stages_value or []]
    if strict_v11 and (not isinstance(stages_value, list) or not stages):
        errors.append("diagram.stages 必须是非空数组。")
    if len(stages) != len(set(stages)):
        errors.append("diagram.stages 存在重复阶段。")

    source_ids: set[str] = set()
    sources = diagram.get("sources")
    if strict_v11 and (not isinstance(sources, list) or not sources):
        errors.append("diagram.sources 必须是非空数组。")
        sources = []
    for index, source in enumerate(sources or []):
        prefix = f"diagram.sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{prefix} 必须是对象。")
            continue
        source_id = str(source.get("id") or "").strip()
        _check_identifier(source_id, f"{prefix}.id", errors)
        if source_id in source_ids:
            errors.append(f"来源 ID 重复：{source_id}")
        source_ids.add(source_id)
        if strict_v11:
            for field in ("title", "version", "last_verified", "scope_note"):
                if not str(source.get(field) or "").strip():
                    errors.append(f"{prefix}.{field} 不能为空。")
            source_type = str(source.get("type") or "").strip()
            if source_type not in SOURCE_TYPES:
                errors.append(f"{prefix}.type 不支持：{source_type or '空'}")
            evidence_status = str(source.get("evidence_status") or "").strip()
            if evidence_status not in EVIDENCE_STATUSES:
                errors.append(
                    f"{prefix}.evidence_status 不支持：{evidence_status or '空'}"
                )
            if not source.get("url") and not source.get("path"):
                errors.append(f"{prefix} 必须提供 url 或 path。")

    measurement_ids: set[str] = set()
    for index, measurement in enumerate(measurements):
        prefix = f"measurements[{index}]"
        if not isinstance(measurement, dict):
            errors.append(f"{prefix} 必须是对象。")
            continue
        measurement_id = str(measurement.get("id") or "").strip()
        _check_identifier(measurement_id, f"{prefix}.id", errors)
        if measurement_id in measurement_ids:
            errors.append(f"指标 ID 重复：{measurement_id}")
        measurement_ids.add(measurement_id)
        if strict_v11:
            for field in ("name", "unit", "description"):
                if not str(measurement.get(field) or "").strip():
                    errors.append(f"{prefix}.{field} 不能为空。")
            _check_evidence_refs(
                measurement.get("evidence_refs"),
                f"{prefix}.evidence_refs",
                source_ids,
                errors,
                required=True,
            )

    node_ids: set[str] = set()
    node_types: dict[str, str] = {}
    start_ids: list[str] = []
    terminal_ids: set[str] = set()

    for index, node in enumerate(nodes):
        prefix = f"nodes[{index}]"
        if not isinstance(node, dict):
            errors.append(f"{prefix} 必须是对象。")
            continue

        node_id = str(node.get("id") or "").strip()
        node_type = str(node.get("type") or "").strip()
        label = str(node.get("label") or "").strip()
        _check_identifier(node_id, f"{prefix}.id", errors)
        if node_id in node_ids:
            errors.append(f"节点 ID 重复：{node_id}")
        node_ids.add(node_id)
        node_types[node_id] = node_type

        if node_type not in NODE_STYLES:
            errors.append(f"{prefix}.type 不支持：{node_type or '空'}")
        elif node_type == "start":
            start_ids.append(node_id)
        elif node_type in TERMINAL_TYPES:
            terminal_ids.add(node_id)

        if not label:
            errors.append(f"{prefix}.label 不能为空。")
        elif "\ufffd" in label:
            errors.append(f"{prefix}.label 包含中文替换字符。")

        stage = str(node.get("stage") or "").strip()
        if strict_v11 and not stage:
            errors.append(f"{prefix}.stage 不能为空。")
        elif strict_v11 and stage not in stages:
            errors.append(f"{prefix}.stage 未在 diagram.stages 中声明：{stage}")

        for field in ("x", "y", "width", "height", "level", "lane"):
            if field in node and not isinstance(node[field], (int, float)):
                errors.append(f"{prefix}.{field} 必须是数字。")
        for field in ("width", "height"):
            if isinstance(node.get(field), (int, float)) and node[field] <= 0:
                errors.append(f"{prefix}.{field} 必须大于 0。")

        if strict_v11:
            _check_evidence_refs(
                node.get("evidence_refs"),
                f"{prefix}.evidence_refs",
                source_ids,
                errors,
                required=True,
            )
            if node_type == "decision":
                _validate_condition(
                    node.get("condition"), prefix, measurement_ids, errors
                )
            if node_type in TERMINAL_TYPES:
                result = str(node.get("terminal_result") or "").strip()
                if result not in TERMINAL_RESULTS:
                    errors.append(
                        f"{prefix}.terminal_result 不支持：{result or '空'}"
                    )

    if len(start_ids) != 1:
        errors.append(f"必须且只能有一个 start 节点，当前数量为 {len(start_ids)}。")
    if not terminal_ids:
        errors.append("至少需要一个明确的终点节点。")

    edge_ids: set[str] = set()
    outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    reverse_adjacency: dict[str, list[str]] = defaultdict(list)

    for index, edge in enumerate(edges):
        prefix = f"edges[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"{prefix} 必须是对象。")
            continue

        edge_id = str(edge.get("id") or "").strip()
        source = str(edge.get("source") or "").strip()
        target = str(edge.get("target") or "").strip()
        label = str(edge.get("label") or "").strip()
        _check_identifier(edge_id, f"{prefix}.id", errors)
        if edge_id in edge_ids:
            errors.append(f"连线 ID 重复：{edge_id}")
        elif edge_id in node_ids:
            errors.append(f"连线 ID 与节点 ID 冲突：{edge_id}")
        edge_ids.add(edge_id)

        if source not in node_ids:
            errors.append(f"{prefix}.source 指向不存在的节点：{source or '空'}")
        if target not in node_ids:
            errors.append(f"{prefix}.target 指向不存在的节点：{target or '空'}")
        if "\ufffd" in label:
            errors.append(f"{prefix}.label 包含中文替换字符。")

        branch = str(edge.get("branch") or "").strip()
        if strict_v11 and branch not in BRANCH_TYPES:
            errors.append(f"{prefix}.branch 不支持：{branch or '空'}")
        if strict_v11:
            _check_evidence_refs(
                edge.get("evidence_refs"),
                f"{prefix}.evidence_refs",
                source_ids,
                errors,
                required=True,
            )

        if source in node_ids and target in node_ids:
            outgoing[source].append(edge)
            incoming[target].append(edge)
            reverse_adjacency[target].append(source)

    for node_id, node_type in node_types.items():
        node_outgoing = outgoing.get(node_id, [])
        if node_type == "decision":
            if len(node_outgoing) < 2:
                errors.append(f"判断节点 {node_id} 至少需要两个出口。")
            labels = [str(edge.get("label") or "").strip() for edge in node_outgoing]
            if any(not label for label in labels):
                errors.append(f"判断节点 {node_id} 的所有出口都必须有分支文字。")
            if len(labels) != len(set(labels)):
                errors.append(f"判断节点 {node_id} 存在重复分支文字。")
            if strict_v11:
                branches = [
                    str(edge.get("branch") or "").strip() for edge in node_outgoing
                ]
                if len(branches) != len(set(branches)):
                    errors.append(f"判断节点 {node_id} 存在重复 branch 语义。")
        if node_type in TERMINAL_TYPES and node_outgoing:
            errors.append(f"终点节点 {node_id} 不应再有出口。")

    if start_ids:
        start_id = start_ids[0]
        if incoming.get(start_id):
            errors.append(f"开始节点 {start_id} 不应有入口。")

        reached: set[str] = set()
        queue: deque[str] = deque([start_id])
        while queue:
            current = queue.popleft()
            if current in reached:
                continue
            reached.add(current)
            for edge in outgoing.get(current, []):
                target = str(edge.get("target") or "")
                if target and target not in reached:
                    queue.append(target)
        unreachable = sorted(node_ids - reached)
        if unreachable:
            errors.append("以下节点无法从开始节点到达：" + "、".join(unreachable))

    can_reach_terminal: set[str] = set()
    terminal_queue: deque[str] = deque(sorted(terminal_ids))
    while terminal_queue:
        current = terminal_queue.popleft()
        if current in can_reach_terminal:
            continue
        can_reach_terminal.add(current)
        for source in reverse_adjacency.get(current, []):
            if source not in can_reach_terminal:
                terminal_queue.append(source)
    trapped = sorted(node_ids - can_reach_terminal)
    if trapped:
        errors.append(
            "以下节点无法到达任何终点（可能存在无出口循环）：" + "、".join(trapped)
        )

    if errors:
        detail = "\n".join(f"- {message}" for message in errors)
        raise SpecValidationError("质控 JSON 校验失败：\n" + detail)

    return diagram, nodes, edges
