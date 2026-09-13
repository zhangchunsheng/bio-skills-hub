#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据结构化分子病理质控 JSON 生成可编辑的 Draw.io 流程图。

说明：本文件只负责编排模型校验、布局和 XML 输出；各职责由独立模块实现。
Author: WangYunL
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

from qc_flow_layout import LayoutResult, resolve_layout
from qc_flow_model import (
    NODE_STYLES,
    SCHEMA_VERSION,
    SpecValidationError,
    configure_console_encoding,
    load_spec,
    normalize_spec,
    validate_spec,
)


GENERATOR_VERSION = "1.1"
HTML_TAG_PATTERN = re.compile(
    r"</?(?:br|b|strong|i|em|u|span|font|div)(?:\s+[^<>]*)?\s*/?>",
    re.IGNORECASE,
)
STAGE_STYLE = (
    "swimlane;horizontal=1;startSize=32;rounded=1;html=1;collapsible=0;"
    "container=0;pointerEvents=0;fillColor=#f8f9fa;strokeColor=#b8b8b8;"
    "fontStyle=1;fontColor=#555555;opacity=55;"
)
SOURCE_NOTE_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacing=10;"
    "fillColor=#f5f5f5;strokeColor=#999999;fontColor=#555555;fontSize=11;"
)


def format_number(value: float) -> str:
    """把整数坐标写成无小数形式。"""
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def normalize_html_label(value: str) -> str:
    """保留允许的 HTML 标签，并把字面小于号转换为 Draw.io 实体。"""
    tags: list[str] = []

    def reserve_tag(match: re.Match[str]) -> str:
        tags.append(match.group(0))
        return f"\ue000{len(tags) - 1}\ue001"

    normalized = HTML_TAG_PATTERN.sub(reserve_tag, value)
    normalized = normalized.replace("<", "&lt;")
    for index, tag in enumerate(tags):
        normalized = normalized.replace(f"\ue000{index}\ue001", tag)
    return normalized


def edge_style(
    source_geometry: dict[str, float], target_geometry: dict[str, float]
) -> str:
    """根据节点相对位置设置正交连线入口和出口。"""
    source_center_x = source_geometry["x"] + source_geometry["width"] / 2
    source_center_y = source_geometry["y"] + source_geometry["height"] / 2
    target_center_x = target_geometry["x"] + target_geometry["width"] / 2
    target_center_y = target_geometry["y"] + target_geometry["height"] / 2
    dx = target_center_x - source_center_x
    dy = target_center_y - source_center_y

    base = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;"
    if abs(dx) > abs(dy):
        if dx >= 0:
            return base + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
        return base + "exitX=0;exitY=0.5;entryX=1;entryY=0.5;"
    if dy >= 0:
        return base + "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"
    return base + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;"


def _json_attribute(value: Any) -> str:
    """把结构化元数据压缩为稳定的 UTF-8 JSON 属性值。"""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _source_note(diagram: dict[str, Any]) -> str:
    """生成图内可见的证据和适用范围说明。"""
    lines = ["<b>证据与适用范围</b>"]
    for source in diagram.get("sources") or []:
        if not isinstance(source, dict):
            continue
        source_id = str(source.get("id") or "来源")
        title = str(source.get("title") or "未命名来源")
        version = str(source.get("version") or "版本未提供")
        status = str(source.get("evidence_status") or "unknown")
        scope = str(source.get("scope_note") or "适用范围未提供")
        lines.append(f"[{source_id}] {title}（{version}，{status}）：{scope}")
    if len(lines) == 1:
        lines.append("未提供来源；图中阈值和结论均需人工确认。")
    return "<br>".join(lines)


def _add_geometry(
    cell: ET.Element, geometry: dict[str, float], relative: bool = False
) -> None:
    """给 mxCell 添加统一格式的 mxGeometry。"""
    attributes = {"as": "geometry"}
    if relative:
        attributes["relative"] = "1"
    else:
        attributes.update(
            {
                "x": format_number(geometry["x"]),
                "y": format_number(geometry["y"]),
                "width": format_number(geometry["width"]),
                "height": format_number(geometry["height"]),
            }
        )
    ET.SubElement(cell, "mxGeometry", attributes)


def build_drawio(
    diagram: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    schema_version: str = SCHEMA_VERSION,
    measurements: list[dict[str, Any]] | None = None,
) -> ET.ElementTree:
    """构建包含业务语义、来源元数据和可选阶段泳道的未压缩 XML。"""
    layout_result: LayoutResult = resolve_layout(diagram, nodes, edges)
    geometry = layout_result.node_geometry
    sources = diagram.get("sources") or []
    measurements = measurements or []

    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "agent": f"molecular-pathology-qc-flow/{GENERATOR_VERSION} Author WangYunL",
            "version": "24.7.17",
        },
    )
    diagram_element = ET.SubElement(
        mxfile,
        "diagram",
        {
            "name": str(diagram["name"]),
            "id": str(diagram["id"]),
            "data-schema-version": str(schema_version),
            "data-generator-version": GENERATOR_VERSION,
            "data-technology": str(diagram.get("technology") or "未确定"),
            "data-method": str(diagram.get("method") or "未确定"),
            "data-project": str(diagram.get("project") or "未确定"),
            "data-qc-stage": str(diagram.get("qc_stage") or "未确定"),
            "data-sources": _json_attribute(sources),
            "data-measurements": _json_attribute(measurements),
        },
    )
    model = ET.SubElement(
        diagram_element,
        "mxGraphModel",
        {
            "dx": "1422",
            "dy": "794",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": format_number(layout_result.page_width),
            "pageHeight": format_number(layout_result.page_height),
            "math": "0",
            "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    for stage in layout_result.stage_bands:
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": stage.cell_id,
                "value": normalize_html_label(stage.label),
                "style": STAGE_STYLE,
                "parent": "1",
                "vertex": "1",
                "data-role": "stage",
                "data-stage": stage.label,
            },
        )
        _add_geometry(
            cell,
            {
                "x": stage.x,
                "y": stage.y,
                "width": stage.width,
                "height": stage.height,
            },
        )

    for node in nodes:
        node_id = str(node["id"])
        node_type = str(node["type"])
        style = NODE_STYLES[node_type] + str(node.get("style", ""))
        attributes = {
            "id": node_id,
            "value": normalize_html_label(str(node["label"])),
            "style": style,
            "parent": "1",
            "vertex": "1",
            "data-role": "business",
            "data-node-type": node_type,
            "data-stage": str(node.get("stage") or diagram.get("qc_stage") or "未确定"),
            "data-evidence-refs": _json_attribute(node.get("evidence_refs") or []),
        }
        if isinstance(node.get("condition"), dict):
            attributes["data-condition"] = _json_attribute(node["condition"])
        if node.get("terminal_result"):
            attributes["data-terminal-result"] = str(node["terminal_result"])
        cell = ET.SubElement(root, "mxCell", attributes)
        _add_geometry(cell, geometry[node_id])

    for edge in edges:
        source = str(edge["source"])
        target = str(edge["target"])
        attributes = {
            "id": str(edge["id"]),
            "style": str(
                edge.get("style", edge_style(geometry[source], geometry[target]))
            ),
            "parent": "1",
            "source": source,
            "target": target,
            "edge": "1",
            "data-role": "business",
            "data-branch": str(edge.get("branch") or "next"),
            "data-evidence-refs": _json_attribute(edge.get("evidence_refs") or []),
        }
        label = str(edge.get("label", ""))
        if label:
            attributes["value"] = normalize_html_label(label)
        cell = ET.SubElement(root, "mxCell", attributes)
        _add_geometry(cell, {}, relative=True)

    if layout_result.source_note_geometry is not None:
        note_cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": "_meta_sources",
                "value": normalize_html_label(_source_note(diagram)),
                "style": SOURCE_NOTE_STYLE,
                "parent": "1",
                "vertex": "1",
                "data-role": "metadata",
            },
        )
        _add_geometry(note_cell, layout_result.source_note_geometry)

    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ")
    return tree


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="根据分子病理质控 JSON 生成可编辑的 Draw.io 流程图。"
    )
    parser.add_argument("--input", required=True, type=Path, help="输入 JSON 文件")
    parser.add_argument("--output", required=True, type=Path, help="输出 .drawio 文件")
    return parser.parse_args()


def main() -> int:
    """执行读取、校验、布局和生成流程。"""
    args = parse_args()
    if args.output.suffix.lower() != ".drawio":
        print("生成失败：输出文件扩展名必须是 .drawio。", file=sys.stderr)
        return 2

    try:
        spec = normalize_spec(load_spec(args.input))
        diagram, nodes, edges = validate_spec(spec)
        tree = build_drawio(
            diagram,
            nodes,
            edges,
            schema_version=str(spec.get("schema_version") or "1.0"),
            measurements=spec.get("measurements") or [],
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        tree.write(
            args.output,
            encoding="utf-8",
            xml_declaration=True,
            short_empty_elements=True,
        )
    except (OSError, SpecValidationError, ValueError) as exc:
        print(f"生成失败：{exc}", file=sys.stderr)
        return 1

    print(
        f"生成成功：{args.output}；业务节点 {len(nodes)} 个，连线 {len(edges)} 条。"
    )
    return 0


if __name__ == "__main__":
    configure_console_encoding()
    raise SystemExit(main())

