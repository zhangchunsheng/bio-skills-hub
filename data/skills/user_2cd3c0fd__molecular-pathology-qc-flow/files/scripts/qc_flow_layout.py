#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分子病理质控流程图的自动布局、阶段泳道和页面尺寸计算。

说明：布局层不读取或写入文件，只根据已校验的流程数据返回几何结果。
Author: WangYunL
"""

from __future__ import annotations

import math
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any

from qc_flow_model import NODE_SIZES, TERMINAL_TYPES


@dataclass
class StageBand:
    """阶段泳道背景的几何和显示信息。"""

    cell_id: str
    label: str
    x: float
    y: float
    width: float
    height: float


@dataclass
class LayoutResult:
    """生成器和预览器共同使用的完整布局结果。"""

    node_geometry: dict[str, dict[str, float]]
    stage_bands: list[StageBand]
    source_note_geometry: dict[str, float] | None
    page_width: float
    page_height: float


def calculate_levels(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> dict[str, int]:
    """从开始节点广度优先计算层级；显式回环不会导致重复遍历。"""
    start_id = next(str(node["id"]) for node in nodes if node["type"] == "start")
    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        outgoing[str(edge["source"])].append(str(edge["target"]))

    levels = {start_id: 0}
    queue: deque[str] = deque([start_id])
    while queue:
        source = queue.popleft()
        for target in outgoing.get(source, []):
            if target not in levels:
                levels[target] = levels[source] + 1
                queue.append(target)
    return levels


def lane_sequence(count: int) -> list[int]:
    """生成从主通道向左右交替展开的通道序列。"""
    values: list[int] = []
    for index in range(count):
        if index == 0:
            values.append(0)
        elif index % 2 == 1:
            values.append(-((index + 1) // 2))
        else:
            values.append(index // 2)
    return values


def _node_size(node: dict[str, Any]) -> tuple[float, float]:
    """返回节点显式尺寸或类型默认尺寸。"""
    default_width, default_height = NODE_SIZES[str(node["type"])]
    return (
        float(node.get("width", default_width)),
        float(node.get("height", default_height)),
    )


def _flow_geometry(
    layout: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    """保持 1.0 主流程逻辑，解析显式坐标并自动补齐缺失坐标。"""
    center_x = float(layout.get("center_x", 550))
    start_y = float(layout.get("start_y", 70))
    level_gap = float(layout.get("level_gap", 145))
    max_width = max(_node_size(node)[0] for node in nodes)
    lane_gap = max(float(layout.get("lane_gap", 320)), max_width + 40)
    levels = calculate_levels(nodes, edges)

    nodes_by_level: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        node_id = str(node["id"])
        level = int(node.get("level", levels[node_id]))
        nodes_by_level[level].append(node)

    automatic_lanes: dict[str, int] = {}
    for level_nodes in nodes_by_level.values():
        for node, lane in zip(level_nodes, lane_sequence(len(level_nodes))):
            automatic_lanes[str(node["id"])] = lane

    geometry: dict[str, dict[str, float]] = {}
    for node in nodes:
        node_id = str(node["id"])
        width, height = _node_size(node)
        level = int(node.get("level", levels[node_id]))
        lane = int(node.get("lane", automatic_lanes[node_id]))
        geometry[node_id] = {
            "x": float(node.get("x", center_x + lane * lane_gap - width / 2)),
            "y": float(node.get("y", start_y + level * level_gap)),
            "width": width,
            "height": height,
        }
    return geometry


def _swimlane_geometry(
    diagram: dict[str, Any],
    layout: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, float]], list[StageBand]]:
    """按阶段生成横向泳道，并在每个阶段内按层级排布节点。"""
    margin = float(layout.get("margin", 40))
    stage_gap = float(layout.get("stage_gap", 24))
    start_y = float(layout.get("start_y", 40))
    level_gap = float(layout.get("level_gap", 145))
    center_x = float(layout.get("center_x", 550))
    max_width = max(_node_size(node)[0] for node in nodes)
    lane_gap = max(float(layout.get("lane_gap", 320)), max_width + 40)
    levels = calculate_levels(nodes, edges)

    stages = [str(stage) for stage in diagram.get("stages", [])]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        grouped[str(node.get("stage") or diagram.get("qc_stage") or "未确定")].append(
            node
        )
    for stage in grouped:
        if stage not in stages:
            stages.append(stage)

    geometry: dict[str, dict[str, float]] = {}
    bands: list[StageBand] = []
    stage_top = start_y

    for stage_index, stage in enumerate(stages, start=1):
        stage_nodes = grouped.get(stage, [])
        level_values = sorted(
            {
                int(node.get("level", levels[str(node["id"])]))
                for node in stage_nodes
            }
        )
        local_levels = {value: index for index, value in enumerate(level_values)}
        nodes_by_level: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for node in stage_nodes:
            global_level = int(node.get("level", levels[str(node["id"])]))
            nodes_by_level[local_levels[global_level]].append(node)

        max_bottom = stage_top + 110
        for local_level, level_nodes in sorted(nodes_by_level.items()):
            if all(str(node.get("type")) in TERMINAL_TYPES for node in level_nodes):
                if len(level_nodes) == 1:
                    automatic_lanes = [-1]
                else:
                    automatic_lanes = [
                        value
                        for pair_index in range(1, len(level_nodes) + 1)
                        for value in (-pair_index, pair_index)
                    ][: len(level_nodes)]
            else:
                automatic_lanes = lane_sequence(len(level_nodes))
            for node, automatic_lane in zip(level_nodes, automatic_lanes):
                node_id = str(node["id"])
                width, height = _node_size(node)
                lane = int(node.get("lane", automatic_lane))
                x = float(node.get("x", center_x + lane * lane_gap - width / 2))
                y = float(node.get("y", stage_top + 50 + local_level * level_gap))
                geometry[node_id] = {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                }
                max_bottom = max(max_bottom, y + height + 30)

        band_height = max(110.0, max_bottom - stage_top)
        bands.append(
            StageBand(
                cell_id=f"_stage_{stage_index}",
                label=stage,
                x=margin,
                y=stage_top,
                width=0,
                height=band_height,
            )
        )
        stage_top += band_height + stage_gap

    return geometry, bands


def _shift_inside_margin(
    geometry: dict[str, dict[str, float]], bands: list[StageBand], margin: float
) -> None:
    """当自动布局越过页面左上边界时整体平移，避免节点被裁切。"""
    if not geometry:
        return
    min_x = min(item["x"] for item in geometry.values())
    min_y = min(item["y"] for item in geometry.values())
    shift_x = max(0.0, margin - min_x)
    shift_y = max(0.0, margin - min_y)
    if shift_x == 0 and shift_y == 0:
        return
    for item in geometry.values():
        item["x"] += shift_x
        item["y"] += shift_y
    for band in bands:
        band.x += shift_x
        band.y += shift_y


def _round_page(value: float) -> float:
    """页面尺寸向上取整到 10，便于 Draw.io 网格对齐。"""
    return float(int(math.ceil(value / 10.0) * 10))


def resolve_layout(
    diagram: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> LayoutResult:
    """计算节点、泳道、来源说明和自适应页面尺寸。"""
    layout = diagram.get("layout")
    if not isinstance(layout, dict):
        layout = {}
    margin = float(layout.get("margin", 40))
    mode = str(layout.get("mode") or "flow")

    if mode == "swimlane":
        geometry, bands = _swimlane_geometry(diagram, layout, nodes, edges)
    else:
        geometry = _flow_geometry(layout, nodes, edges)
        bands = []

    _shift_inside_margin(geometry, bands, margin)
    max_right = max(item["x"] + item["width"] for item in geometry.values())
    max_bottom = max(item["y"] + item["height"] for item in geometry.values())
    if bands:
        max_bottom = max(max_bottom, max(band.y + band.height for band in bands))

    configured_width = float(layout.get("page_width", 1100))
    configured_height = float(layout.get("page_height", 1380))
    auto_size = bool(layout.get("auto_size", True))
    if auto_size:
        page_width = _round_page(max(configured_width, max_right + margin))
    else:
        page_width = configured_width

    for band in bands:
        band.x = margin
        band.width = max(100.0, page_width - 2 * margin)

    source_note_geometry: dict[str, float] | None = None
    if bool(layout.get("show_source_note", True)):
        source_count = len(diagram.get("sources") or [])
        note_height = max(72.0, 50.0 + source_count * 22.0)
        source_note_geometry = {
            "x": margin,
            "y": max_bottom + 40.0,
            "width": max(100.0, page_width - 2 * margin),
            "height": note_height,
        }
        max_bottom = source_note_geometry["y"] + source_note_geometry["height"]

    if auto_size:
        page_height = _round_page(max(configured_height, max_bottom + margin))
    else:
        page_height = configured_height

    return LayoutResult(
        node_geometry=geometry,
        stage_bands=bands,
        source_note_geometry=source_note_geometry,
        page_width=page_width,
        page_height=page_height,
    )
