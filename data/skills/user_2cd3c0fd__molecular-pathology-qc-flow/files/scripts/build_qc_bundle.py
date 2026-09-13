#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一条命令生成分子病理质控说明、Draw.io、结构预览和交付清单。

说明：输出目录必须不存在，避免覆盖用户已有文件；所有内容先在临时目录完成并验证。
Author: WangYunL
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from generate_drawio import build_drawio
from qc_flow_model import (
    SpecValidationError,
    configure_console_encoding,
    load_spec,
    normalize_spec,
    validate_spec,
)
from query_knowledge import DEFAULT_INDEX, load_index, search_index
from render_drawio_preview import parse_drawio, render_png, render_svg
from validate_drawio import DrawioValidationError, validate_drawio


BUNDLE_VERSION = "1.2"
INVALID_FILENAME_PATTERN = re.compile(r"[<>:\"/\\|?*\x00-\x1f]")
BR_PATTERN = re.compile(r"<br\s*/?>", re.IGNORECASE)
TAG_PATTERN = re.compile(r"<[^>]+>")


class BundleBuildError(ValueError):
    """表示质控交付包无法安全生成。"""


def safe_filename(value: str) -> str:
    """把图页名称转换为 Windows 可用且可读的文件名。"""
    normalized = INVALID_FILENAME_PATTERN.sub("_", value).strip().rstrip(". ")
    normalized = re.sub(r"\s+", "_", normalized)
    if not normalized:
        raise BundleBuildError("无法从图页名称生成有效文件名，请使用 --base-name。")
    return normalized[:100].rstrip(". ")


def plain_text(value: Any) -> str:
    """把节点 HTML 换行转换为说明文档中的纯文本。"""
    text = html.unescape(str(value or ""))
    text = BR_PATTERN.sub(" / ", text)
    text = TAG_PATTERN.sub("", text)
    return html.unescape(text).strip()


def markdown_cell(value: Any) -> str:
    """转义 Markdown 表格中的换行和竖线。"""
    return plain_text(value).replace("|", "\\|").replace("\r", " ").replace("\n", " / ")


def source_location(source: dict[str, Any]) -> str:
    """返回来源 URL 或本地路径。"""
    return str(source.get("url") or source.get("path") or "未提供")


def find_knowledge_entries(
    diagram: dict[str, Any], index_path: Path
) -> list[dict[str, Any]]:
    """按技术和项目查找用于说明“是什么”的知识条目。"""
    query = " ".join(
        value
        for value in (
            str(diagram.get("technology") or "").strip(),
            str(diagram.get("project") or "").strip(),
        )
        if value and value not in {"未确定", "通用模板"}
    )
    if not query:
        return []
    index = load_index(index_path)
    results = search_index(index, query, limit=5)
    selected: list[dict[str, Any]] = []
    seen_kinds: set[str] = set()
    for entry in results:
        kind = str(entry.get("kind") or "")
        if kind in seen_kinds and len(selected) >= 2:
            continue
        selected.append(entry)
        seen_kinds.add(kind)
        if len(selected) == 2:
            break
    return selected


def unresolved_items(
    diagram: dict[str, Any], nodes: list[dict[str, Any]]
) -> list[str]:
    """收集需要实验室资料确认的字段，不把缺失项静默隐藏。"""
    items: list[str] = []
    method = str(diagram.get("method") or "").strip()
    if not method or "未确定" in method or "待确认" in method:
        items.append("具体方法、试剂或平台仍需确认。")
    for source in diagram.get("sources") or []:
        if not isinstance(source, dict):
            continue
        source_id = str(source.get("id") or "来源")
        version = str(source.get("version") or "")
        status = str(source.get("evidence_status") or "")
        if "未提供" in version or "未确定" in version:
            items.append(f"来源 {source_id} 的版本尚未提供。")
        if status in {"unknown", "conflict", "inferred"}:
            items.append(f"来源 {source_id} 的证据状态为 {status}，需复核。")
    for node in nodes:
        condition = node.get("condition")
        if isinstance(condition, dict) and condition.get("operator") == "CUSTOM":
            items.append(
                f"判断节点 {node.get('id')} 使用 CUSTOM 条件，需依据匹配 SOP/IFU 确认："
                f"{plain_text(condition.get('expression'))}"
            )
    unique_items: list[str] = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)
    return unique_items


def build_markdown_report(
    spec: dict[str, Any],
    diagram: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    knowledge_entries: list[dict[str, Any]],
    drawio_counts: tuple[int, int, int],
    preview_names: list[str],
) -> str:
    """生成技术说明、质控节点表、来源和验证结果。"""
    lines = [
        f"# {diagram['name']}质控说明",
        "",
        "作者：WangYunL  ",
        f"生成日期：{date.today().isoformat()}  ",
        f"数据契约：{spec.get('schema_version', '1.0')}  ",
        "",
        "## 一、项目概况",
        "",
        "| 字段 | 内容 |",
        "| --- | --- |",
        f"| 技术 | {markdown_cell(diagram.get('technology'))} |",
        f"| 方法 | {markdown_cell(diagram.get('method'))} |",
        f"| 项目 | {markdown_cell(diagram.get('project'))} |",
        f"| 质控范围 | {markdown_cell(diagram.get('qc_stage'))} |",
        f"| 阶段 | {'、'.join(markdown_cell(item) for item in diagram.get('stages') or [])} |",
        "",
        "## 二、技术与项目说明",
        "",
    ]
    if knowledge_entries:
        for entry in knowledge_entries:
            lines.extend(
                [
                    f"### {entry.get('name')}（{entry.get('kind')}）",
                    "",
                    f"- 是什么：{entry.get('summary')}",
                    f"- 原理：{entry.get('principle')}",
                    f"- 常见方法：{'、'.join(entry.get('methods') or ['未确定'])}",
                    f"- 适用边界：{entry.get('scope_note')}",
                    "",
                ]
            )
    else:
        lines.extend(["内置知识索引没有匹配条目，需要依据用户资料补充技术说明。", ""])

    lines.extend(
        [
            "## 三、指标",
            "",
            "| ID | 指标 | 单位 | 说明 | 证据 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    measurements = spec.get("measurements") or []
    if measurements:
        for measurement in measurements:
            lines.append(
                "| {id} | {name} | {unit} | {description} | {refs} |".format(
                    id=markdown_cell(measurement.get("id")),
                    name=markdown_cell(measurement.get("name")),
                    unit=markdown_cell(measurement.get("unit")),
                    description=markdown_cell(measurement.get("description")),
                    refs="、".join(measurement.get("evidence_refs") or []),
                )
            )
    else:
        lines.append("| - | 未定义结构化指标 | - | 根据当前流程补充 | - |")

    lines.extend(
        [
            "",
            "## 四、质控节点",
            "",
            "| 序号 | ID | 阶段 | 类型 | 节点内容 | 判断条件 | 空值策略 | 终点语义 | 证据 |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for index, node in enumerate(nodes, start=1):
        condition = node.get("condition") if isinstance(node.get("condition"), dict) else {}
        lines.append(
            "| {index} | {id} | {stage} | {type} | {label} | {condition} | {missing} | {terminal} | {refs} |".format(
                index=index,
                id=markdown_cell(node.get("id")),
                stage=markdown_cell(node.get("stage")),
                type=markdown_cell(node.get("type")),
                label=markdown_cell(node.get("label")),
                condition=markdown_cell(condition.get("expression") or "-"),
                missing=markdown_cell(condition.get("missing_policy") or "-"),
                terminal=markdown_cell(node.get("terminal_result") or "-"),
                refs="、".join(node.get("evidence_refs") or []),
            )
        )

    lines.extend(
        [
            "",
            "## 五、分支关系",
            "",
            "| ID | 起点 | 终点 | 分支文字 | 分支语义 | 证据 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for edge in edges:
        lines.append(
            "| {id} | {source} | {target} | {label} | {branch} | {refs} |".format(
                id=markdown_cell(edge.get("id")),
                source=markdown_cell(edge.get("source")),
                target=markdown_cell(edge.get("target")),
                label=markdown_cell(edge.get("label") or "-"),
                branch=markdown_cell(edge.get("branch") or "next"),
                refs="、".join(edge.get("evidence_refs") or []),
            )
        )

    lines.extend(
        [
            "",
            "## 六、来源与适用范围",
            "",
            "| ID | 标题 | 版本 | 状态 | 位置 | 适用范围 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for source in diagram.get("sources") or []:
        lines.append(
            "| {id} | {title} | {version} | {status} | {location} | {scope} |".format(
                id=markdown_cell(source.get("id")),
                title=markdown_cell(source.get("title")),
                version=markdown_cell(source.get("version")),
                status=markdown_cell(source.get("evidence_status")),
                location=markdown_cell(source_location(source)),
                scope=markdown_cell(source.get("scope_note")),
            )
        )

    unresolved = unresolved_items(diagram, nodes)
    lines.extend(["", "## 七、待确认项", ""])
    if unresolved:
        lines.extend(f"- {item}" for item in unresolved)
    else:
        lines.append("- 当前结构化流程未发现自动识别的待确认项；仍需由实验室负责人确认适用范围。")

    page_count, vertex_count, edge_count = drawio_counts
    lines.extend(
        [
            "",
            "## 八、生成与验证结果",
            "",
            f"- 质控 JSON 语义校验：通过",
            f"- Draw.io 独立校验：通过（图页 {page_count}、业务节点 {vertex_count}、连线 {edge_count}）",
            f"- 结构预览：{'、'.join(preview_names) if preview_names else '未生成'}",
            "- 结构预览不等同于 diagrams.net 桌面端真实渲染验收。",
            "- 本说明不能替代临床诊断、病理判读或实验室现行 SOP。",
            "",
        ]
    )
    return "\n".join(lines)


def file_digest(path: Path) -> str:
    """计算交付文件 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(
    input_path: Path,
    diagram: dict[str, Any],
    files: list[tuple[str, Path]],
    drawio_counts: tuple[int, int, int],
) -> dict[str, Any]:
    """构建不包含自身哈希的交付清单。"""
    return {
        "bundle_version": BUNDLE_VERSION,
        "generated_on": date.today().isoformat(),
        "author": "WangYunL",
        "input": {
            "path": str(input_path.resolve()),
            "sha256": file_digest(input_path),
        },
        "diagram": {
            "name": diagram.get("name"),
            "technology": diagram.get("technology"),
            "method": diagram.get("method"),
            "project": diagram.get("project"),
            "qc_stage": diagram.get("qc_stage"),
        },
        "validation": {
            "spec": "passed",
            "drawio": "passed",
            "pages": drawio_counts[0],
            "business_nodes": drawio_counts[1],
            "edges": drawio_counts[2],
        },
        "files": [
            {
                "role": role,
                "name": path.name,
                "size": path.stat().st_size,
                "sha256": file_digest(path),
            }
            for role, path in files
        ],
        "boundary": "结构预览不等同于 diagrams.net 桌面端真实渲染；阈值仅在来源适用范围内有效。",
    }


def build_bundle(
    input_path: Path,
    output_dir: Path,
    base_name: str | None,
    preview: str,
    index_path: Path,
) -> list[Path]:
    """在临时目录完成全部生成和复验，再复制到一个全新的输出目录。"""
    if output_dir.exists():
        raise BundleBuildError(f"输出目录已存在，已停止以避免覆盖：{output_dir}")

    spec = normalize_spec(load_spec(input_path))
    diagram, nodes, edges = validate_spec(spec)
    stem = safe_filename(base_name or str(diagram["name"]))
    report_name = f"{date.today().isoformat()}-{stem}-质控说明.md"
    knowledge_entries = find_knowledge_entries(diagram, index_path)

    with TemporaryDirectory(prefix="molecular-qc-bundle-") as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        spec_path = staging / f"{stem}_质控定义.json"
        drawio_path = staging / f"{stem}.drawio"
        spec_path.write_text(
            json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        tree = build_drawio(
            diagram,
            nodes,
            edges,
            schema_version=str(spec.get("schema_version") or "1.0"),
            measurements=spec.get("measurements") or [],
        )
        tree.write(drawio_path, encoding="utf-8", xml_declaration=True)
        drawio_counts = validate_drawio(drawio_path)

        generated_files: list[tuple[str, Path]] = [
            ("spec", spec_path),
            ("drawio", drawio_path),
        ]
        preview_names: list[str] = []
        page = parse_drawio(drawio_path)
        if preview in {"svg", "both"}:
            svg_path = staging / f"{stem}_结构预览.svg"
            render_svg(page, svg_path)
            generated_files.append(("preview-svg", svg_path))
            preview_names.append(svg_path.name)
        if preview in {"png", "both"}:
            png_path = staging / f"{stem}_结构预览.png"
            render_png(page, png_path, 1.25)
            generated_files.append(("preview-png", png_path))
            preview_names.append(png_path.name)

        report_path = staging / report_name
        report_path.write_text(
            build_markdown_report(
                spec,
                diagram,
                nodes,
                edges,
                knowledge_entries,
                drawio_counts,
                preview_names,
            ),
            encoding="utf-8",
        )
        generated_files.append(("qc-report", report_path))

        manifest_path = staging / f"{stem}_交付清单.json"
        manifest_path.write_text(
            json.dumps(
                build_manifest(input_path, diagram, generated_files, drawio_counts),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        shutil.copytree(staging, output_dir)

    return sorted(output_dir.iterdir(), key=lambda path: path.name)


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="从一个质控 JSON 一次性生成说明、Draw.io、预览和交付清单。"
    )
    parser.add_argument("--input", required=True, type=Path, help="输入质控 JSON")
    parser.add_argument(
        "--output-dir", required=True, type=Path, help="必须不存在的新输出目录"
    )
    parser.add_argument("--base-name", help="输出文件基础名称，默认使用 diagram.name")
    parser.add_argument(
        "--preview",
        choices=("none", "svg", "png", "both"),
        default="svg",
        help="结构预览格式，默认 svg",
    )
    parser.add_argument(
        "--index", type=Path, default=DEFAULT_INDEX, help="技术项目知识索引"
    )
    return parser.parse_args()


def main() -> int:
    """执行一键交付包生成。"""
    args = parse_args()
    try:
        files = build_bundle(
            args.input,
            args.output_dir,
            args.base_name,
            args.preview,
            args.index,
        )
    except (
        OSError,
        SpecValidationError,
        DrawioValidationError,
        BundleBuildError,
        ValueError,
    ) as exc:
        print(f"交付包生成失败：{exc}", file=sys.stderr)
        return 1

    print(f"交付包生成成功：{args.output_dir}")
    for path in files:
        print(f"- {path.name}")
    return 0


if __name__ == "__main__":
    configure_console_encoding()
    raise SystemExit(main())

