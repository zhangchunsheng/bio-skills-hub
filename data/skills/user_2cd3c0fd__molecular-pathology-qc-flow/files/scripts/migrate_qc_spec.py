#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把旧版 v1.0 质控 JSON 迁移为可审计的 v1.1 数据契约。

说明：迁移只保留或显式标记已有信息，不根据节点文字猜测结构化阈值。
Author: WangYunL
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from qc_flow_model import (
    BRANCH_TYPES,
    CONDITION_OPERATORS,
    ID_PATTERN,
    MISSING_POLICIES,
    SOURCE_TYPES,
    TERMINAL_TYPES,
    configure_console_encoding,
    load_spec,
    normalize_spec,
    validate_spec,
)


MIGRATION_VERSION = "1.2"
ALLOWED_LAYOUT_FIELDS = {
    "mode",
    "page_width",
    "page_height",
    "auto_size",
    "show_source_note",
    "center_x",
    "start_y",
    "level_gap",
    "lane_gap",
    "stage_gap",
    "margin",
}
ALLOWED_NODE_FIELDS = {
    "id",
    "type",
    "label",
    "stage",
    "description",
    "condition",
    "terminal_result",
    "evidence_refs",
    "x",
    "y",
    "width",
    "height",
    "level",
    "lane",
    "style",
}
ALLOWED_EDGE_FIELDS = {
    "id",
    "source",
    "target",
    "label",
    "branch",
    "evidence_refs",
    "style",
}
ALLOWED_CONDITION_FIELDS = {
    "measurement",
    "operator",
    "value",
    "lower",
    "upper",
    "unit",
    "expression",
    "missing_policy",
}
TERMINAL_RESULTS = {
    "positive": "positive",
    "pass": "pass",
    "negative": "negative",
    "invalid": "invalid",
    "end": "end",
}


class MigrationError(ValueError):
    """表示旧版质控定义无法安全迁移。"""


def _valid_identifier(value: Any) -> bool:
    """判断值是否可直接作为 v1.1 业务 ID。"""
    return bool(ID_PATTERN.fullmatch(str(value or "").strip()))


def _unique_identifier(value: Any, prefix: str, index: int, used: set[str]) -> str:
    """保留合法且唯一的旧 ID，否则生成可追溯的新 ID。"""
    candidate = str(value or "").strip()
    if not _valid_identifier(candidate) or candidate in used:
        candidate = f"{prefix}_{index}"
        suffix = index
        while candidate in used:
            suffix += 1
            candidate = f"{prefix}_{suffix}"
    used.add(candidate)
    return candidate


def _date_value(value: str) -> str:
    """校验命令行提供的来源核对日期。"""
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise MigrationError("--last-verified 必须使用 YYYY-MM-DD。") from exc


def _removed_fields(
    item: dict[str, Any], allowed: set[str], location: str, review: list[str]
) -> None:
    """把未进入新契约的字段完整记录到复核清单。"""
    removed = sorted(set(item) - allowed)
    if removed:
        review.append(
            f"{location} 未迁移字段：{'、'.join(removed)}；原因：v1.1 契约未定义，原文件仍保留。"
        )


def _source_candidates(diagram: dict[str, Any]) -> list[dict[str, Any]]:
    """统一读取旧版 source 或过渡期 sources。"""
    sources = diagram.get("sources")
    if isinstance(sources, list) and any(isinstance(item, dict) for item in sources):
        return [item for item in sources if isinstance(item, dict)]
    source = diagram.get("source")
    return [source] if isinstance(source, dict) else [{}]


def _migrate_sources(
    diagram: dict[str, Any], input_path: Path, last_verified: str, review: list[str]
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """迁移来源并返回旧来源 ID 到新来源 ID 的映射。"""
    migrated: list[dict[str, Any]] = []
    id_map: dict[str, str] = {}
    used_ids: set[str] = set()
    for index, source in enumerate(_source_candidates(diagram), start=1):
        old_id = str(source.get("id") or "").strip()
        new_id = _unique_identifier(old_id, "migration_source", index, used_ids)
        if old_id and old_id != new_id:
            review.append(f"来源 ID {old_id} 已映射为 {new_id}，原因：旧 ID 不合法或重复。")
        if old_id:
            id_map[old_id] = new_id

        source_type = str(source.get("type") or "user-file").strip()
        if source_type not in SOURCE_TYPES:
            review.append(f"来源 {new_id} 的 type={source_type} 不受支持，已标记为 user-file。")
            source_type = "user-file"
        evidence_status = str(source.get("evidence_status") or "unknown").strip()
        if evidence_status not in {"confirmed", "inferred", "unknown", "conflict"}:
            review.append(f"来源 {new_id} 的 evidence_status 不受支持，已标记为 unknown。")
            evidence_status = "unknown"

        migrated_source: dict[str, Any] = {
            "id": new_id,
            "type": source_type,
            "title": str(source.get("title") or source.get("name") or input_path.name),
            "version": str(source.get("version") or "未提供（需复核）"),
            "last_verified": last_verified,
            "scope_note": str(
                source.get("scope_note") or "由 v1.0 迁移，适用范围需结合原始资料复核"
            ),
            "evidence_status": evidence_status,
        }
        if source.get("url"):
            migrated_source["url"] = str(source["url"])
        else:
            migrated_source["path"] = str(source.get("path") or input_path.resolve())
        migrated.append(migrated_source)
        review.append(
            f"来源 {new_id} 的 last_verified 使用命令行确认日期 {last_verified}；这表示迁移核对日期，不代表内容已获实验室确认。"
        )
    return migrated, id_map


def _evidence_refs(
    raw_refs: Any, source_ids: set[str], source_id_map: dict[str, str], default_ref: str
) -> list[str]:
    """保留可解析的来源引用，缺失时绑定默认迁移来源。"""
    refs: list[str] = []
    if isinstance(raw_refs, list):
        for item in raw_refs:
            raw_id = str(item or "").strip()
            mapped = source_id_map.get(raw_id, raw_id)
            if mapped in source_ids and mapped not in refs:
                refs.append(mapped)
    return refs or [default_ref]


def _migrate_measurements(
    raw_measurements: Any,
    source_ids: set[str],
    source_id_map: dict[str, str],
    default_ref: str,
    review: list[str],
) -> list[dict[str, Any]]:
    """迁移可识别指标；非法 ID 不会被猜测替换。"""
    migrated: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    for index, measurement in enumerate(raw_measurements or [], start=1):
        if not isinstance(measurement, dict):
            review.append(f"measurements[{index - 1}] 不是对象，未迁移；原值保留在旧文件。")
            continue
        measurement_id = str(measurement.get("id") or "").strip()
        if not _valid_identifier(measurement_id) or measurement_id in used_ids:
            review.append(
                f"measurements[{index - 1}] 的 ID 无效或重复，未迁移；请人工分配业务 ID 后补入。"
            )
            continue
        used_ids.add(measurement_id)
        migrated.append(
            {
                "id": measurement_id,
                "name": str(measurement.get("name") or "未确定（需复核）"),
                "unit": str(measurement.get("unit") or "未确定（需复核）"),
                "description": str(
                    measurement.get("description") or "由 v1.0 迁移，定义需复核"
                ),
                "evidence_refs": _evidence_refs(
                    measurement.get("evidence_refs"),
                    source_ids,
                    source_id_map,
                    default_ref,
                ),
            }
        )
        _removed_fields(
            measurement,
            {"id", "name", "unit", "description", "evidence_refs"},
            f"measurement {measurement_id}",
            review,
        )
    return migrated


def _usable_condition(condition: dict[str, Any], measurement_ids: set[str]) -> bool:
    """判断旧条件是否能不改语义地进入 v1.1。"""
    operator = str(condition.get("operator") or "").strip()
    if operator not in CONDITION_OPERATORS:
        return False
    if not str(condition.get("expression") or "").strip():
        return False
    if str(condition.get("missing_policy") or "") not in MISSING_POLICIES:
        return False
    if operator != "CUSTOM" and str(condition.get("measurement") or "") not in measurement_ids:
        return False
    if operator in {"EQ", "NE", "LT", "LE", "GT", "GE"} and "value" not in condition:
        return False
    if operator in {"BETWEEN_CLOSED", "BETWEEN_OPEN"}:
        lower = condition.get("lower")
        upper = condition.get("upper")
        if not isinstance(lower, (int, float)) or not isinstance(upper, (int, float)) or lower >= upper:
            return False
    if operator == "IN" and not isinstance(condition.get("value"), list):
        return False
    return True


def _migrate_condition(
    node: dict[str, Any], measurement_ids: set[str], review: list[str]
) -> dict[str, Any]:
    """保留完整旧条件，否则降级为必须人工复核的 CUSTOM 条件。"""
    raw = node.get("condition")
    node_id = str(node.get("id") or "未命名")
    if isinstance(raw, dict) and _usable_condition(raw, measurement_ids):
        _removed_fields(raw, ALLOWED_CONDITION_FIELDS, f"节点 {node_id}.condition", review)
        return {key: deepcopy(value) for key, value in raw.items() if key in ALLOWED_CONDITION_FIELDS}
    expression = str(raw.get("expression") if isinstance(raw, dict) else "").strip()
    if not expression:
        expression = str(node.get("label") or "依据原流程判断").replace("<br>", " ")
    review.append(
        f"判断节点 {node_id} 未提供可直接验证的结构化条件，已改为 CUSTOM/manual_review；数值和单位未从节点文字猜测。"
    )
    return {
        "operator": "CUSTOM",
        "expression": f"{expression}（由迁移工具生成，需按原 SOP/IFU 复核）",
        "missing_policy": "manual_review",
    }


def migrate_legacy_spec(
    raw_spec: dict[str, Any], input_path: Path, last_verified: str
) -> tuple[dict[str, Any], list[str]]:
    """迁移 v1.0 数据并返回完整人工复核记录。"""
    version = str(raw_spec.get("schema_version") or "1.0").strip()
    if version != "1.0":
        raise MigrationError(f"仅支持从 v1.0 迁移，当前版本为 {version}。")
    normalized = normalize_spec(raw_spec)
    raw_diagram = raw_spec.get("diagram")
    if not isinstance(raw_diagram, dict):
        raise MigrationError("diagram 必须是对象。")

    review: list[str] = [
        "迁移不会修改旧文件，也不会从节点文字推断数值阈值。",
        "所有自动补充的字段必须由实验室负责人结合原 SOP、IFU 或验证报告复核。",
    ]
    sources, source_id_map = _migrate_sources(
        raw_diagram, input_path, _date_value(last_verified), review
    )
    source_ids = {item["id"] for item in sources}
    default_ref = sources[0]["id"]
    measurements = _migrate_measurements(
        raw_spec.get("measurements"), source_ids, source_id_map, default_ref, review
    )
    measurement_ids = {item["id"] for item in measurements}

    raw_nodes = normalized.get("nodes")
    if not isinstance(raw_nodes, list):
        raise MigrationError("nodes 必须是数组。")
    node_id_map: dict[str, str] = {}
    used_node_ids: set[str] = set()
    nodes: list[dict[str, Any]] = []
    for index, raw_node in enumerate(raw_nodes, start=1):
        if not isinstance(raw_node, dict):
            raise MigrationError(f"nodes[{index - 1}] 必须是对象。")
        node_type = str(raw_node.get("type") or "").strip()
        if node_type not in {
            "start", "process", "decision", "positive", "pass", "negative", "invalid", "warning", "end"
        }:
            raise MigrationError(f"nodes[{index - 1}].type 不支持：{node_type or '空'}")
        old_id = str(raw_node.get("id") or "").strip()
        new_id = _unique_identifier(old_id, "node", index, used_node_ids)
        if old_id:
            node_id_map[old_id] = new_id
        if old_id != new_id:
            review.append(f"节点 ID {old_id or '空'} 已映射为 {new_id}。")
        node = {
            key: deepcopy(value)
            for key, value in raw_node.items()
            if key in ALLOWED_NODE_FIELDS
            and key not in {"id", "condition", "terminal_result", "evidence_refs"}
        }
        node["id"] = new_id
        node["stage"] = str(raw_node.get("stage") or raw_diagram.get("qc_stage") or "未确定（需复核）")
        node["evidence_refs"] = _evidence_refs(
            raw_node.get("evidence_refs"), source_ids, source_id_map, default_ref
        )
        if node_type == "decision":
            node["condition"] = _migrate_condition(raw_node, measurement_ids, review)
        if node_type in TERMINAL_TYPES:
            node["terminal_result"] = str(
                raw_node.get("terminal_result") or TERMINAL_RESULTS.get(node_type, "end")
            )
            if not raw_node.get("terminal_result"):
                review.append(
                    f"终点节点 {new_id} 的 terminal_result 按节点类型 {node_type} 补为 {node['terminal_result']}。"
                )
        _removed_fields(raw_node, ALLOWED_NODE_FIELDS, f"节点 {new_id}", review)
        nodes.append(node)

    node_types = {node["id"]: node["type"] for node in nodes}
    raw_edges = normalized.get("edges")
    if not isinstance(raw_edges, list):
        raise MigrationError("edges 必须是数组。")
    used_edge_ids: set[str] = set()
    edges: list[dict[str, Any]] = []
    for index, raw_edge in enumerate(raw_edges, start=1):
        if not isinstance(raw_edge, dict):
            raise MigrationError(f"edges[{index - 1}] 必须是对象。")
        old_id = str(raw_edge.get("id") or "").strip()
        edge_id = _unique_identifier(old_id, "edge", index, used_edge_ids | used_node_ids)
        used_edge_ids.add(edge_id)
        if old_id != edge_id:
            review.append(f"连线 ID {old_id or '空'} 已映射为 {edge_id}。")
        old_source = str(raw_edge.get("source") or "")
        old_target = str(raw_edge.get("target") or "")
        source = node_id_map.get(old_source, old_source)
        target = node_id_map.get(old_target, old_target)
        edge = {
            key: deepcopy(value)
            for key, value in raw_edge.items()
            if key in ALLOWED_EDGE_FIELDS
            and key not in {"id", "source", "target", "branch", "evidence_refs"}
        }
        edge.update(
            {
                "id": edge_id,
                "source": source,
                "target": target,
                "branch": str(raw_edge.get("branch") or "next"),
                "evidence_refs": _evidence_refs(
                    raw_edge.get("evidence_refs"), source_ids, source_id_map, default_ref
                ),
            }
        )
        if edge["branch"] not in BRANCH_TYPES:
            edge["branch"] = "next"
            review.append(f"连线 {edge_id} 的旧 branch 不受支持，已标记为 next，需复核。")
        original_edges = raw_spec.get("edges")
        original_edge = (
            original_edges[index - 1]
            if isinstance(original_edges, list)
            and index <= len(original_edges)
            and isinstance(original_edges[index - 1], dict)
            else {}
        )
        if not original_edge.get("branch"):
            review.append(
                f"连线 {edge_id} 的 branch={edge['branch']} 由旧版分支文字兼容规则生成，需复核。"
            )
        _removed_fields(raw_edge, ALLOWED_EDGE_FIELDS, f"连线 {edge_id}", review)
        edges.append(edge)

    layout_source = raw_diagram.get("layout")
    layout_raw = layout_source if isinstance(layout_source, dict) else {}
    layout = {key: deepcopy(value) for key, value in layout_raw.items() if key in ALLOWED_LAYOUT_FIELDS}
    layout.setdefault("mode", "flow")
    layout.setdefault("auto_size", True)
    layout.setdefault("show_source_note", True)
    _removed_fields(layout_raw, ALLOWED_LAYOUT_FIELDS, "diagram.layout", review)

    stages: list[str] = []
    for node in nodes:
        stage = str(node["stage"])
        if stage not in stages:
            stages.append(stage)
    migrated = {
        "$schema": "../references/qc-flow.schema.json",
        "schema_version": "1.1",
        "diagram": {
            "name": str(raw_diagram.get("name") or input_path.stem),
            "id": str(raw_diagram.get("id") or "migrated_qc_flow"),
            "technology": str(raw_diagram.get("technology") or "未确定（需复核）"),
            "method": str(raw_diagram.get("method") or "未确定（需复核）"),
            "project": str(raw_diagram.get("project") or "未确定（需复核）"),
            "qc_stage": str(raw_diagram.get("qc_stage") or "未确定（需复核）"),
            "stages": stages,
            "sources": sources,
            "layout": layout,
        },
        "measurements": measurements,
        "nodes": nodes,
        "edges": edges,
    }
    if not _valid_identifier(migrated["diagram"]["id"]):
        review.append(
            f"diagram.id={migrated['diagram']['id']} 不合法，已映射为 migrated_qc_flow。"
        )
        migrated["diagram"]["id"] = "migrated_qc_flow"
    _removed_fields(
        raw_diagram,
        {
            "name", "id", "technology", "method", "project", "qc_stage", "stages", "source", "sources", "layout"
        },
        "diagram",
        review,
    )
    _removed_fields(raw_spec, {"$schema", "schema_version", "diagram", "measurements", "nodes", "edges"}, "顶层", review)
    validate_spec(migrated)
    return migrated, review


def build_review_report(
    input_path: Path, output_path: Path, review: list[str]
) -> str:
    """生成迁移执行和人工复核清单。"""
    lines = [
        f"# {output_path.stem}迁移复核清单",
        "",
        "作者：WangYunL  ",
        f"生成日期：{date.today().isoformat()}  ",
        f"迁移工具版本：{MIGRATION_VERSION}  ",
        "",
        "## 一、迁移对象",
        "",
        f"- 原文件：`{input_path.resolve()}`",
        f"- 新文件：`{output_path.resolve()}`",
        "- 原文件未修改，新文件采用 v1.1 契约。",
        "",
        "## 二、迁移记录",
        "",
    ]
    lines.extend(f"- {item}" for item in review)
    lines.extend(
        [
            "",
            "## 三、发布前人工复核",
            "",
            "- [ ] 技术、方法、项目和质控阶段与原 SOP 一致。",
            "- [ ] 所有 CUSTOM 条件已用匹配版本的 SOP/IFU 转为结构化条件，或确认继续人工判读。",
            "- [ ] 所有来源版本、核对日期、适用范围和证据状态准确。",
            "- [ ] 所有分支语义、终点语义和失败处置与原流程一致。",
            "- [ ] 在 diagrams.net 中完成真实渲染和人工连线检查。",
            "",
            "## 四、删除与覆盖说明",
            "",
            "迁移工具不删除或覆盖原文件。v1.1 不支持的字段仅不进入新文件，并已在“迁移记录”中逐项标记原因。",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="把 v1.0 质控 JSON 迁移为 v1.1，并生成复核清单。")
    parser.add_argument("--input", required=True, type=Path, help="v1.0 输入 JSON")
    parser.add_argument("--output", required=True, type=Path, help="必须不存在的 v1.1 输出 JSON")
    parser.add_argument("--last-verified", required=True, help="迁移时核对来源的日期，YYYY-MM-DD")
    parser.add_argument("--review-output", type=Path, help="复核清单路径，默认与输出文件同目录")
    return parser.parse_args()


def main() -> int:
    """执行安全迁移并写入两个全新文件。"""
    args = parse_args()
    review_output = args.review_output or (
        args.output.parent / f"{date.today().isoformat()}-{args.output.stem}-迁移复核清单.md"
    )
    try:
        if args.output.exists() or review_output.exists():
            raise MigrationError("输出 JSON 或复核清单已存在，已停止以避免覆盖。")
        if not args.output.parent.exists() or not review_output.parent.exists():
            raise MigrationError("输出文件的父目录必须已存在。")
        raw_spec = load_spec(args.input)
        migrated, review = migrate_legacy_spec(raw_spec, args.input, args.last_verified)
        with TemporaryDirectory(prefix="molecular-qc-migration-") as temporary:
            temporary_path = Path(temporary)
            json_path = temporary_path / "migrated.json"
            report_path = temporary_path / "review.md"
            json_path.write_text(
                json.dumps(migrated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            report_path.write_text(
                build_review_report(args.input, args.output, review), encoding="utf-8"
            )
            load_spec(json_path)
            shutil.copy2(json_path, args.output)
            shutil.copy2(report_path, review_output)
    except (OSError, MigrationError, ValueError) as exc:
        print(f"迁移失败：{exc}", file=sys.stderr)
        return 1
    print(f"迁移成功：{args.output}")
    print(f"复核清单：{review_output}")
    return 0


if __name__ == "__main__":
    configure_console_encoding()
    raise SystemExit(main())
