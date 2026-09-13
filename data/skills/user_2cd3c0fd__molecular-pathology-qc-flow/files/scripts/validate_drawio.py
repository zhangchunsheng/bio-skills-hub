#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校验 Draw.io 质控流程图的 XML、业务元数据、连线、分支和终点完备性。

说明：本脚本独立读取生成结果，不依赖生成器内存中的校验结论。
Author: WangYunL
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


TERMINAL_TYPES = {"positive", "pass", "negative", "invalid", "end"}


class DrawioValidationError(ValueError):
    """表示 Draw.io 文件不满足质控流程图结构约束。"""


def configure_console_encoding() -> None:
    """在 Windows 命令行中统一使用 UTF-8 输出中文。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _parse_json_attribute(
    value: str | None, field: str, errors: list[str], expected_type: type
) -> Any:
    """解析 Draw.io 中的 JSON 元数据属性，并把错误加入统一列表。"""
    if value is None:
        errors.append(f"{field} 缺失。")
        return expected_type()
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        errors.append(f"{field} 不是合法 JSON。")
        return expected_type()
    if not isinstance(parsed, expected_type):
        errors.append(f"{field} 类型不正确。")
        return expected_type()
    return parsed


def _reached_from(start_id: str, adjacency: dict[str, list[str]]) -> set[str]:
    """返回从指定节点可达的全部业务节点。"""
    reached: set[str] = set()
    queue: deque[str] = deque([start_id])
    while queue:
        current = queue.popleft()
        if current in reached:
            continue
        reached.add(current)
        for target in adjacency.get(current, []):
            if target not in reached:
                queue.append(target)
    return reached


def validate_drawio(path: Path) -> tuple[int, int, int]:
    """校验一个未压缩 Draw.io 文件并返回图页、业务节点和连线数量。"""
    raw = path.read_text(encoding="utf-8-sig")
    errors: list[str] = []
    if "\ufffd" in raw:
        errors.append("文件包含中文替换字符。")

    try:
        mxfile = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise DrawioValidationError(f"XML 解析失败：{exc}") from exc

    if mxfile.tag != "mxfile":
        errors.append(f"根节点应为 mxfile，实际为 {mxfile.tag}。")
    diagrams = mxfile.findall("diagram")
    if not diagrams:
        errors.append("文件中没有 diagram 图页。")

    total_vertices = 0
    total_edges = 0

    for page_index, diagram in enumerate(diagrams, start=1):
        page_name = diagram.get("name") or f"第 {page_index} 页"
        strict_v11 = diagram.get("data-schema-version") == "1.1"
        source_ids: set[str] = set()
        if strict_v11:
            for attribute in (
                "data-generator-version",
                "data-technology",
                "data-method",
                "data-project",
                "data-qc-stage",
            ):
                if not (diagram.get(attribute) or "").strip():
                    errors.append(f"{page_name} 缺少图页元数据 {attribute}。")
            sources = _parse_json_attribute(
                diagram.get("data-sources"),
                f"{page_name}.data-sources",
                errors,
                list,
            )
            if not sources:
                errors.append(f"{page_name}.data-sources 不能为空。")
            for source in sources:
                if isinstance(source, dict) and str(source.get("id") or "").strip():
                    source_ids.add(str(source["id"]).strip())
            _parse_json_attribute(
                diagram.get("data-measurements"),
                f"{page_name}.data-measurements",
                errors,
                list,
            )

        model_root = diagram.find("mxGraphModel/root")
        if model_root is None:
            errors.append(f"{page_name} 不是未压缩的 mxGraphModel 图页。")
            continue

        cells = model_root.findall("mxCell")
        cell_ids: set[str] = set()
        duplicate_ids: set[str] = set()
        vertices: dict[str, ET.Element] = {}
        edges: list[ET.Element] = []

        for cell in cells:
            cell_id = cell.get("id", "")
            if not cell_id:
                errors.append(f"{page_name} 存在缺少 ID 的 mxCell。")
                continue
            if cell_id in cell_ids:
                duplicate_ids.add(cell_id)
            cell_ids.add(cell_id)

            role = cell.get("data-role")
            is_business = role in (None, "business")
            if cell.get("vertex") == "1" and is_business:
                vertices[cell_id] = cell
            if cell.get("edge") == "1" and is_business:
                edges.append(cell)

        if duplicate_ids:
            errors.append(
                f"{page_name} 存在重复 ID：" + "、".join(sorted(duplicate_ids))
            )
        if not vertices:
            errors.append(f"{page_name} 没有业务节点。")

        total_vertices += len(vertices)
        total_edges += len(edges)
        incoming_count: dict[str, int] = defaultdict(int)
        outgoing: dict[str, list[ET.Element]] = defaultdict(list)
        adjacency: dict[str, list[str]] = defaultdict(list)
        reverse_adjacency: dict[str, list[str]] = defaultdict(list)

        for edge in edges:
            edge_id = edge.get("id", "")
            source = edge.get("source", "")
            target = edge.get("target", "")
            if source not in vertices:
                errors.append(
                    f"{page_name} 的连线 {edge_id} source 不存在：{source or '空'}"
                )
            if target not in vertices:
                errors.append(
                    f"{page_name} 的连线 {edge_id} target 不存在：{target or '空'}"
                )
            if strict_v11:
                branch = (edge.get("data-branch") or "").strip()
                if not branch:
                    errors.append(f"{page_name} 的连线 {edge_id} 缺少 data-branch。")
                refs = _parse_json_attribute(
                    edge.get("data-evidence-refs"),
                    f"{page_name}.{edge_id}.data-evidence-refs",
                    errors,
                    list,
                )
                if not refs:
                    errors.append(
                        f"{page_name} 的连线 {edge_id} 缺少有效证据引用。"
                    )
                missing_refs = sorted(
                    {str(ref) for ref in refs if str(ref) not in source_ids}
                )
                if missing_refs:
                    errors.append(
                        f"{page_name} 的连线 {edge_id} 引用不存在来源："
                        + "、".join(missing_refs)
                    )
            if source in vertices and target in vertices:
                outgoing[source].append(edge)
                incoming_count[target] += 1
                adjacency[source].append(target)
                reverse_adjacency[target].append(source)

        start_ids: list[str] = []
        terminal_ids: set[str] = set()
        for node_id, node in vertices.items():
            style = node.get("style", "")
            node_type = (node.get("data-node-type") or "").strip()
            is_decision = node_type == "decision" or "rhombus" in style
            if strict_v11:
                if not node_type:
                    errors.append(f"{page_name} 的节点 {node_id} 缺少 data-node-type。")
                if not (node.get("data-stage") or "").strip():
                    errors.append(f"{page_name} 的节点 {node_id} 缺少 data-stage。")
                refs = _parse_json_attribute(
                    node.get("data-evidence-refs"),
                    f"{page_name}.{node_id}.data-evidence-refs",
                    errors,
                    list,
                )
                if not refs:
                    errors.append(f"{page_name} 的节点 {node_id} 缺少有效证据引用。")
                missing_refs = sorted(
                    {str(ref) for ref in refs if str(ref) not in source_ids}
                )
                if missing_refs:
                    errors.append(
                        f"{page_name} 的节点 {node_id} 引用不存在来源："
                        + "、".join(missing_refs)
                    )
                if is_decision:
                    condition = _parse_json_attribute(
                        node.get("data-condition"),
                        f"{page_name}.{node_id}.data-condition",
                        errors,
                        dict,
                    )
                    if not condition.get("operator") or not condition.get("expression"):
                        errors.append(
                            f"{page_name} 的判断节点 {node_id} 缺少结构化条件。"
                        )

            if node_type == "start":
                start_ids.append(node_id)
            if node_type in TERMINAL_TYPES:
                terminal_ids.add(node_id)
                if strict_v11 and not (node.get("data-terminal-result") or "").strip():
                    errors.append(
                        f"{page_name} 的终点节点 {node_id} 缺少 data-terminal-result。"
                    )

            if is_decision:
                node_edges = outgoing.get(node_id, [])
                if len(node_edges) < 2:
                    errors.append(f"{page_name} 的判断节点 {node_id} 至少需要两个出口。")
                labels = [(edge.get("value") or "").strip() for edge in node_edges]
                if any(not label for label in labels):
                    errors.append(
                        f"{page_name} 的判断节点 {node_id} 存在无分支文字的出口。"
                    )
                if len(labels) != len(set(labels)):
                    errors.append(f"{page_name} 的判断节点 {node_id} 存在重复分支文字。")
                if strict_v11:
                    branches = [
                        (edge.get("data-branch") or "").strip()
                        for edge in node_edges
                    ]
                    if len(branches) != len(set(branches)):
                        errors.append(
                            f"{page_name} 的判断节点 {node_id} 存在重复 branch 语义。"
                        )

        if strict_v11:
            if len(start_ids) != 1:
                errors.append(
                    f"{page_name} 应有且只有一个 start 节点，实际为 {len(start_ids)} 个。"
                )
        else:
            start_ids = sorted(
                node_id for node_id in vertices if incoming_count.get(node_id, 0) == 0
            )
            terminal_ids = {
                node_id for node_id in vertices if not outgoing.get(node_id)
            }
            if len(start_ids) != 1:
                errors.append(
                    f"{page_name} 应只有一个无入口开始节点，实际为 {len(start_ids)} 个："
                    + "、".join(start_ids)
                )

        if not terminal_ids:
            errors.append(f"{page_name} 至少需要一个明确终点。")
        for terminal_id in sorted(terminal_ids):
            if outgoing.get(terminal_id):
                errors.append(f"{page_name} 的终点节点 {terminal_id} 不应再有出口。")

        if start_ids:
            start_id = start_ids[0]
            if incoming_count.get(start_id, 0):
                errors.append(f"{page_name} 的开始节点 {start_id} 不应有入口。")
            reached = _reached_from(start_id, adjacency)
            unreachable = sorted(set(vertices) - reached)
            if unreachable:
                errors.append(f"{page_name} 存在不可达节点：" + "、".join(unreachable))

        can_reach_terminal: set[str] = set()
        queue: deque[str] = deque(sorted(terminal_ids))
        while queue:
            current = queue.popleft()
            if current in can_reach_terminal:
                continue
            can_reach_terminal.add(current)
            for source in reverse_adjacency.get(current, []):
                if source not in can_reach_terminal:
                    queue.append(source)
        trapped = sorted(set(vertices) - can_reach_terminal)
        if trapped:
            errors.append(
                f"{page_name} 存在无法到达终点的节点（可能为无出口循环）："
                + "、".join(trapped)
            )

    if errors:
        detail = "\n".join(f"- {message}" for message in errors)
        raise DrawioValidationError("Draw.io 校验失败：\n" + detail)
    return len(diagrams), total_vertices, total_edges


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="校验分子病理质控 Draw.io 流程图。")
    parser.add_argument("drawio", type=Path, help="待校验的 .drawio 文件")
    return parser.parse_args()


def main() -> int:
    """执行独立结构校验。"""
    args = parse_args()
    try:
        page_count, vertex_count, edge_count = validate_drawio(args.drawio)
    except (OSError, DrawioValidationError) as exc:
        print(f"校验失败：{exc}", file=sys.stderr)
        return 1

    print(
        "校验通过："
        f"{args.drawio}；图页 {page_count} 个，业务节点 {vertex_count} 个，"
        f"连线 {edge_count} 条，未发现中文乱码。"
    )
    return 0


if __name__ == "__main__":
    configure_console_encoding()
    raise SystemExit(main())

