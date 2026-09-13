#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把未压缩 Draw.io 流程图渲染为 SVG 或 PNG 结构预览。

说明：预览用于检查节点、泳道、文字和分支位置，不等同于 diagrams.net 桌面端渲染。
Author: WangYunL
"""

from __future__ import annotations

import argparse
import html
import math
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


BR_PATTERN = re.compile(r"<br\s*/?>", re.IGNORECASE)
TAG_PATTERN = re.compile(r"<[^>]+>")
FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/simsun.ttc"),
)


class PreviewRenderError(ValueError):
    """表示 Draw.io 预览无法解析或渲染。"""


@dataclass
class PreviewCell:
    """预览器使用的最小 mxCell 结构。"""

    cell_id: str
    value: str
    style: dict[str, str]
    role: str
    node_type: str
    x: float
    y: float
    width: float
    height: float
    source: str = ""
    target: str = ""


@dataclass
class PreviewPage:
    """单个 Draw.io 图页的页面和单元格数据。"""

    name: str
    width: float
    height: float
    vertices: list[PreviewCell]
    edges: list[PreviewCell]


def configure_console_encoding() -> None:
    """在 Windows 命令行中统一使用 UTF-8 输出中文。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _style_map(style: str) -> dict[str, str]:
    """把 Draw.io 分号样式拆成键值字典，并保留图形关键字。"""
    result: dict[str, str] = {}
    for part in style.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            key, value = part.split("=", 1)
            result[key] = value
        else:
            result[part] = "1"
    return result


def _plain_text(value: str) -> str:
    """把 Draw.io HTML 标签转换为预览器可绘制的纯文本。"""
    text = html.unescape(value or "")
    text = BR_PATTERN.sub("\n", text)
    text = TAG_PATTERN.sub("", text)
    text = html.unescape(text)
    return text.replace("✅", "✓").replace("⚪", "○").replace("❌", "×")


def _geometry(cell: ET.Element) -> tuple[float, float, float, float]:
    """读取 mxGeometry；连线没有绝对尺寸时返回零。"""
    geometry = cell.find("mxGeometry")
    if geometry is None:
        return 0.0, 0.0, 0.0, 0.0
    return tuple(
        float(geometry.get(field, "0")) for field in ("x", "y", "width", "height")
    )


def parse_drawio(path: Path) -> PreviewPage:
    """读取未压缩 Draw.io 的第一个图页。"""
    raw = path.read_text(encoding="utf-8-sig")
    if "\ufffd" in raw:
        raise PreviewRenderError("Draw.io 文件包含中文替换字符。")
    try:
        mxfile = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise PreviewRenderError(f"XML 解析失败：{exc}") from exc
    diagram = mxfile.find("diagram")
    if diagram is None:
        raise PreviewRenderError("Draw.io 文件没有 diagram 图页。")
    model = diagram.find("mxGraphModel")
    root = diagram.find("mxGraphModel/root")
    if model is None or root is None:
        raise PreviewRenderError("仅支持未压缩的 mxGraphModel 图页。")

    width = float(model.get("pageWidth", "1100"))
    height = float(model.get("pageHeight", "1380"))
    vertices: list[PreviewCell] = []
    edges: list[PreviewCell] = []
    for cell in root.findall("mxCell"):
        x, y, cell_width, cell_height = _geometry(cell)
        preview_cell = PreviewCell(
            cell_id=cell.get("id", ""),
            value=_plain_text(cell.get("value", "")),
            style=_style_map(cell.get("style", "")),
            role=cell.get("data-role") or "business",
            node_type=cell.get("data-node-type") or "",
            x=x,
            y=y,
            width=cell_width,
            height=cell_height,
            source=cell.get("source", ""),
            target=cell.get("target", ""),
        )
        if cell.get("vertex") == "1":
            vertices.append(preview_cell)
        elif cell.get("edge") == "1" and preview_cell.role == "business":
            edges.append(preview_cell)
    return PreviewPage(
        name=diagram.get("name") or "质控流程图",
        width=width,
        height=height,
        vertices=vertices,
        edges=edges,
    )


def _display_width(character: str) -> int:
    """估算单个字符的显示宽度，中文和全角字符按两个单位计算。"""
    return 2 if unicodedata.east_asian_width(character) in {"W", "F", "A"} else 1


def _wrap_text(text: str, max_units: int) -> list[str]:
    """按估算显示宽度换行，并保留输入中的显式换行。"""
    lines: list[str] = []
    for source_line in text.splitlines() or [""]:
        current = ""
        current_width = 0
        for character in source_line:
            width = _display_width(character)
            if current and current_width + width > max_units:
                lines.append(current)
                current = character
                current_width = width
            else:
                current += character
                current_width += width
        lines.append(current)
    return lines or [""]


def _colors(cell: PreviewCell) -> tuple[str, str]:
    """返回节点填充色和边框色。"""
    return (
        cell.style.get("fillColor", "#ffffff"),
        cell.style.get("strokeColor", "#666666"),
    )


def _connection_points(
    source: PreviewCell, target: PreviewCell
) -> tuple[tuple[float, float], tuple[float, float], list[tuple[float, float]]]:
    """根据节点相对位置生成简化正交连线。"""
    source_center = (source.x + source.width / 2, source.y + source.height / 2)
    target_center = (target.x + target.width / 2, target.y + target.height / 2)
    dx = target_center[0] - source_center[0]
    dy = target_center[1] - source_center[1]
    if abs(dx) > abs(dy):
        if dx >= 0:
            start = (source.x + source.width, source_center[1])
            end = (target.x, target_center[1])
        else:
            start = (source.x, source_center[1])
            end = (target.x + target.width, target_center[1])
        middle_x = (start[0] + end[0]) / 2
        points = [start, (middle_x, start[1]), (middle_x, end[1]), end]
    else:
        if dy >= 0:
            start = (source_center[0], source.y + source.height)
            end = (target_center[0], target.y)
        else:
            start = (source_center[0], source.y)
            end = (target_center[0], target.y + target.height)
        middle_y = (start[1] + end[1]) / 2
        points = [start, (start[0], middle_y), (end[0], middle_y), end]
    return start, end, points


def _arrow_points(
    previous: tuple[float, float], end: tuple[float, float], size: float = 8
) -> list[tuple[float, float]]:
    """计算连线末端箭头三角形。"""
    angle = math.atan2(end[1] - previous[1], end[0] - previous[0])
    return [
        end,
        (
            end[0] - size * math.cos(angle - math.pi / 6),
            end[1] - size * math.sin(angle - math.pi / 6),
        ),
        (
            end[0] - size * math.cos(angle + math.pi / 6),
            end[1] - size * math.sin(angle + math.pi / 6),
        ),
    ]


def _svg_text(
    parent: ET.Element,
    cell: PreviewCell,
    *,
    align_left: bool = False,
    font_size: float = 14,
) -> None:
    """在 SVG 中加入经过宽度估算的多行文本。"""
    max_units = max(8, int((cell.width - 16) / (font_size * 0.55)))
    lines = _wrap_text(cell.value, max_units)
    line_height = font_size * 1.35
    if align_left:
        x = cell.x + 12
        y = cell.y + 20
        anchor = "start"
    else:
        x = cell.x + cell.width / 2
        y = cell.y + cell.height / 2 - (len(lines) - 1) * line_height / 2 + 5
        anchor = "middle"
    text_element = ET.SubElement(
        parent,
        "text",
        {
            "x": f"{x:.1f}",
            "y": f"{y:.1f}",
            "text-anchor": anchor,
            "font-family": "Microsoft YaHei, SimHei, sans-serif",
            "font-size": f"{font_size:.1f}",
            "fill": cell.style.get("fontColor", "#222222"),
        },
    )
    for index, line in enumerate(lines):
        tspan = ET.SubElement(
            text_element,
            "tspan",
            {
                "x": f"{x:.1f}",
                "dy": "0" if index == 0 else f"{line_height:.1f}",
            },
        )
        tspan.text = line


def render_svg(page: PreviewPage, output: Path) -> None:
    """使用标准库输出可缩放的 SVG 结构预览。"""
    svg = ET.Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": f"{page.width:.0f}",
            "height": f"{page.height:.0f}",
            "viewBox": f"0 0 {page.width:.0f} {page.height:.0f}",
        },
    )
    ET.SubElement(
        svg,
        "rect",
        {"x": "0", "y": "0", "width": "100%", "height": "100%", "fill": "#ffffff"},
    )
    vertices_by_id = {cell.cell_id: cell for cell in page.vertices}

    for cell in page.vertices:
        if cell.role != "stage":
            continue
        fill, stroke = _colors(cell)
        ET.SubElement(
            svg,
            "rect",
            {
                "x": f"{cell.x:.1f}",
                "y": f"{cell.y:.1f}",
                "width": f"{cell.width:.1f}",
                "height": f"{cell.height:.1f}",
                "rx": "10",
                "fill": fill,
                "fill-opacity": "0.55",
                "stroke": stroke,
                "stroke-width": "1",
            },
        )
        _svg_text(svg, cell, align_left=True, font_size=13)

    for edge in page.edges:
        source = vertices_by_id.get(edge.source)
        target = vertices_by_id.get(edge.target)
        if source is None or target is None:
            continue
        _, end, points = _connection_points(source, target)
        path_data = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points)
        ET.SubElement(
            svg,
            "path",
            {"d": path_data, "fill": "none", "stroke": "#555555", "stroke-width": "1.5"},
        )
        arrow = _arrow_points(points[-2], end)
        ET.SubElement(
            svg,
            "polygon",
            {"points": " ".join(f"{x:.1f},{y:.1f}" for x, y in arrow), "fill": "#555555"},
        )
        if edge.value:
            label_cell = PreviewCell(
                cell_id=edge.cell_id,
                value=edge.value,
                style={"fontColor": "#444444"},
                role="edge-label",
                node_type="",
                x=(points[1][0] + points[2][0]) / 2 - 80,
                y=(points[1][1] + points[2][1]) / 2 - 12,
                width=160,
                height=24,
            )
            ET.SubElement(
                svg,
                "rect",
                {
                    "x": f"{label_cell.x:.1f}",
                    "y": f"{label_cell.y:.1f}",
                    "width": f"{label_cell.width:.1f}",
                    "height": f"{label_cell.height:.1f}",
                    "fill": "#ffffff",
                    "fill-opacity": "0.9",
                },
            )
            _svg_text(svg, label_cell, font_size=11)

    for cell in page.vertices:
        if cell.role in {"stage", "metadata"}:
            continue
        fill, stroke = _colors(cell)
        if cell.node_type == "decision" or "rhombus" in cell.style:
            points = [
                (cell.x + cell.width / 2, cell.y),
                (cell.x + cell.width, cell.y + cell.height / 2),
                (cell.x + cell.width / 2, cell.y + cell.height),
                (cell.x, cell.y + cell.height / 2),
            ]
            ET.SubElement(
                svg,
                "polygon",
                {
                    "points": " ".join(f"{x:.1f},{y:.1f}" for x, y in points),
                    "fill": fill,
                    "stroke": stroke,
                    "stroke-width": "1.5",
                },
            )
        else:
            ET.SubElement(
                svg,
                "rect",
                {
                    "x": f"{cell.x:.1f}",
                    "y": f"{cell.y:.1f}",
                    "width": f"{cell.width:.1f}",
                    "height": f"{cell.height:.1f}",
                    "rx": "12",
                    "fill": fill,
                    "stroke": stroke,
                    "stroke-width": "1.5",
                },
            )
        _svg_text(svg, cell)

    for cell in page.vertices:
        if cell.role != "metadata":
            continue
        fill, stroke = _colors(cell)
        ET.SubElement(
            svg,
            "rect",
            {
                "x": f"{cell.x:.1f}",
                "y": f"{cell.y:.1f}",
                "width": f"{cell.width:.1f}",
                "height": f"{cell.height:.1f}",
                "rx": "8",
                "fill": fill,
                "stroke": stroke,
                "stroke-width": "1",
            },
        )
        _svg_text(svg, cell, align_left=True, font_size=11)

    tree = ET.ElementTree(svg)
    ET.indent(tree, space="  ")
    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding="utf-8", xml_declaration=True)


def _load_font(size: int) -> Any:
    """优先加载 Windows 中文字体，找不到时退回 Pillow 默认字体。"""
    from PIL import ImageFont

    for path in FONT_CANDIDATES:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _scaled_points(points: list[tuple[float, float]], scale: float) -> list[tuple[int, int]]:
    """把页面坐标转换为 PNG 像素坐标。"""
    return [(round(x * scale), round(y * scale)) for x, y in points]


def _draw_png_text(
    draw: Any,
    cell: PreviewCell,
    scale: float,
    *,
    align_left: bool = False,
    font_size: int = 14,
) -> None:
    """在 PNG 上绘制支持中文的多行文本。"""
    font = _load_font(max(9, round(font_size * scale)))
    max_units = max(8, int((cell.width - 16) / (font_size * 0.55)))
    lines = _wrap_text(cell.value, max_units)
    spacing = max(2, round(4 * scale))
    text = "\n".join(lines)
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    if align_left:
        position = (round((cell.x + 12) * scale), round((cell.y + 10) * scale))
        align = "left"
    else:
        position = (
            round((cell.x + cell.width / 2) * scale - text_width / 2),
            round((cell.y + cell.height / 2) * scale - text_height / 2),
        )
        align = "center"
    draw.multiline_text(position, text, fill="#222222", font=font, spacing=spacing, align=align)


def render_png(page: PreviewPage, output: Path, scale: float) -> None:
    """使用 Pillow 输出带中文字体的 PNG 结构预览。"""
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise PreviewRenderError("生成 PNG 需要 Pillow；可改用 .svg 输出。") from exc

    image = Image.new(
        "RGB", (round(page.width * scale), round(page.height * scale)), "#ffffff"
    )
    draw = ImageDraw.Draw(image)
    vertices_by_id = {cell.cell_id: cell for cell in page.vertices}

    for cell in page.vertices:
        if cell.role != "stage":
            continue
        fill, stroke = _colors(cell)
        box = (
            round(cell.x * scale),
            round(cell.y * scale),
            round((cell.x + cell.width) * scale),
            round((cell.y + cell.height) * scale),
        )
        draw.rounded_rectangle(box, radius=round(10 * scale), fill=fill, outline=stroke, width=max(1, round(scale)))
        _draw_png_text(draw, cell, scale, align_left=True, font_size=13)

    for edge in page.edges:
        source = vertices_by_id.get(edge.source)
        target = vertices_by_id.get(edge.target)
        if source is None or target is None:
            continue
        _, end, points = _connection_points(source, target)
        draw.line(_scaled_points(points, scale), fill="#555555", width=max(1, round(2 * scale)))
        draw.polygon(_scaled_points(_arrow_points(points[-2], end), scale), fill="#555555")
        if edge.value:
            label_cell = PreviewCell(
                cell_id=edge.cell_id,
                value=edge.value,
                style={},
                role="edge-label",
                node_type="",
                x=(points[1][0] + points[2][0]) / 2 - 80,
                y=(points[1][1] + points[2][1]) / 2 - 12,
                width=160,
                height=24,
            )
            label_box = (
                round(label_cell.x * scale),
                round(label_cell.y * scale),
                round((label_cell.x + label_cell.width) * scale),
                round((label_cell.y + label_cell.height) * scale),
            )
            draw.rectangle(label_box, fill="#ffffff")
            _draw_png_text(draw, label_cell, scale, font_size=11)

    for cell in page.vertices:
        if cell.role in {"stage", "metadata"}:
            continue
        fill, stroke = _colors(cell)
        if cell.node_type == "decision" or "rhombus" in cell.style:
            points = [
                (cell.x + cell.width / 2, cell.y),
                (cell.x + cell.width, cell.y + cell.height / 2),
                (cell.x + cell.width / 2, cell.y + cell.height),
                (cell.x, cell.y + cell.height / 2),
            ]
            draw.polygon(_scaled_points(points, scale), fill=fill, outline=stroke)
        else:
            box = (
                round(cell.x * scale),
                round(cell.y * scale),
                round((cell.x + cell.width) * scale),
                round((cell.y + cell.height) * scale),
            )
            draw.rounded_rectangle(box, radius=round(12 * scale), fill=fill, outline=stroke, width=max(1, round(2 * scale)))
        _draw_png_text(draw, cell, scale)

    for cell in page.vertices:
        if cell.role != "metadata":
            continue
        fill, stroke = _colors(cell)
        box = (
            round(cell.x * scale),
            round(cell.y * scale),
            round((cell.x + cell.width) * scale),
            round((cell.y + cell.height) * scale),
        )
        draw.rounded_rectangle(box, radius=round(8 * scale), fill=fill, outline=stroke, width=max(1, round(scale)))
        _draw_png_text(draw, cell, scale, align_left=True, font_size=11)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="生成 Draw.io 流程图结构预览。")
    parser.add_argument("drawio", type=Path, help="未压缩 .drawio 文件")
    parser.add_argument("--output", required=True, type=Path, help="输出 .svg 或 .png")
    parser.add_argument("--scale", type=float, default=1.25, help="PNG 输出缩放倍数")
    return parser.parse_args()


def main() -> int:
    """执行结构预览渲染。"""
    args = parse_args()
    if args.output.suffix.lower() not in {".svg", ".png"}:
        print("预览失败：输出扩展名必须是 .svg 或 .png。", file=sys.stderr)
        return 2
    if args.scale <= 0:
        print("预览失败：--scale 必须大于 0。", file=sys.stderr)
        return 2
    try:
        page = parse_drawio(args.drawio)
        if args.output.suffix.lower() == ".svg":
            render_svg(page, args.output)
        else:
            render_png(page, args.output, args.scale)
    except (OSError, PreviewRenderError) as exc:
        print(f"预览失败：{exc}", file=sys.stderr)
        return 1
    print(
        f"结构预览生成成功：{args.output}；该文件不等同于 diagrams.net 桌面端渲染结果。"
    )
    return 0


if __name__ == "__main__":
    configure_console_encoding()
    raise SystemExit(main())
