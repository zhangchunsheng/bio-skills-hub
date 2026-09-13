#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按“技术 + 项目”查询并默认写入 Windows 下载目录。

默认交付：<下载目录>/<技术>/<项目>/ 下仅生成 Draw.io 和 HTML 两个文件。
Author: WangYunL
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from generate_drawio import build_drawio
from project_spec_factory import build_safe_project_spec
from qc_flow_model import (
    SpecValidationError,
    configure_console_encoding,
    load_spec,
    normalize_spec,
    validate_spec,
)
from query_knowledge import DEFAULT_INDEX, load_index, normalize_text, search_index
from render_qc_html import HtmlValidationError, build_qc_html, validate_qc_html
from validate_drawio import DrawioValidationError, validate_drawio
from windows_downloads import DownloadsPathError, resolve_downloads_dir, safe_path_segment


SKILL_ROOT = Path(__file__).resolve().parent.parent
DELIVERY_VERSION = "1.2"


class ProjectDeliveryError(ValueError):
    """表示项目交付无法安全完成。"""


def _compact(value: Any) -> str:
    """生成用于名称和别名精确比较的规范值。"""
    return normalize_text(value).replace(" ", "")


def _exact_entry(index: dict[str, Any], query: str, kind: str) -> dict[str, Any] | None:
    """优先按名称或别名精确匹配指定类型的知识条目。"""
    expected = _compact(query)
    for entry in index.get("entries") or []:
        if not isinstance(entry, dict) or entry.get("kind") != kind:
            continue
        candidates = [entry.get("name"), *(entry.get("aliases") or [])]
        if any(_compact(candidate) == expected for candidate in candidates):
            return entry
    results = search_index(index, query, limit=10)
    return next((entry for entry in results if entry.get("kind") == kind), None)


def _merge_entry(
    base: dict[str, Any] | None, overlay: dict[str, Any] | None
) -> dict[str, Any] | None:
    """把本次在线核对结果合并到离线索引，不回写知识库。"""
    if not base and not overlay:
        return None
    merged = dict(base or {})
    for key, value in (overlay or {}).items():
        if key in {"sources", "qc_sources", "pending_items"} and isinstance(value, list):
            existing = list(merged.get(key) or [])
            for item in value:
                if item not in existing:
                    existing.append(item)
            merged[key] = existing
        elif key == "project_profile" and isinstance(value, dict):
            profile = dict(merged.get(key) or {})
            profile.update(value)
            merged[key] = profile
        else:
            merged[key] = value
    return merged


def _load_evidence_overlay(
    path: Path | None, technology: str, project: str
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """读取由在线检索形成的本次证据覆盖文件。"""
    if path is None:
        return None, None
    raw = path.read_text(encoding="utf-8-sig")
    if "\ufffd" in raw:
        raise ProjectDeliveryError(f"在线证据覆盖文件包含中文替换字符：{path}")
    try:
        overlay = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProjectDeliveryError(
            f"在线证据覆盖文件解析失败：第 {exc.lineno} 行，第 {exc.colno} 列。"
        ) from exc
    if not isinstance(overlay, dict):
        raise ProjectDeliveryError("在线证据覆盖文件根节点必须是对象。")
    query = overlay.get("query")
    if isinstance(query, dict):
        if _compact(query.get("technology")) != _compact(technology) or _compact(
            query.get("project")
        ) != _compact(project):
            raise ProjectDeliveryError("在线证据覆盖文件的技术或项目与本次查询不一致。")
    project_overlay = overlay.get("project_entry")
    technology_overlay = overlay.get("technology_entry")
    if project_overlay is not None and not isinstance(project_overlay, dict):
        raise ProjectDeliveryError("project_entry 必须是对象。")
    if technology_overlay is not None and not isinstance(technology_overlay, dict):
        raise ProjectDeliveryError("technology_entry 必须是对象。")
    return project_overlay, technology_overlay


def _resolve_spec(
    technology: str,
    project: str,
    spec_path: Path | None,
    project_entry: dict[str, Any] | None,
    technology_entry: dict[str, Any] | None,
) -> dict[str, Any]:
    """读取项目专用定义；不存在时生成不含猜测阈值的安全流程。"""
    if spec_path is not None:
        return normalize_spec(load_spec(spec_path))
    configured = (project_entry or {}).get("qc_spec_file")
    if configured:
        path = SKILL_ROOT / str(configured)
        if not path.exists():
            raise ProjectDeliveryError(f"知识索引声明的质控定义不存在：{path}")
        return normalize_spec(load_spec(path))
    return build_safe_project_spec(technology, project, project_entry, technology_entry)


def _output_names(diagram: dict[str, Any]) -> tuple[str, str]:
    """生成与 BRAF 样例一致的两个文件名。"""
    base = safe_path_segment(str(diagram.get("name") or "质控流程"), "流程名称").replace(" ", "_")
    return f"{base}_流程图.drawio", f"{base}配置方案.html"


def generate_project_delivery(
    technology: str,
    project: str,
    *,
    output_root: Path | None = None,
    index_path: Path = DEFAULT_INDEX,
    spec_path: Path | None = None,
    evidence_overlay: Path | None = None,
    overwrite: bool = False,
) -> tuple[Path, list[Path]]:
    """生成项目目录和两个文件，并返回最终路径。"""
    downloads = resolve_downloads_dir(output_root)
    technology_segment = safe_path_segment(technology, "技术")
    project_segment = safe_path_segment(project, "项目")
    target_dir = downloads / technology_segment / project_segment

    index = load_index(index_path)
    project_entry = _exact_entry(index, project, "project")
    technology_entry = _exact_entry(index, technology, "technology")
    project_overlay, technology_overlay = _load_evidence_overlay(
        evidence_overlay, technology, project
    )
    project_entry = _merge_entry(project_entry, project_overlay)
    technology_entry = _merge_entry(technology_entry, technology_overlay)
    spec = _resolve_spec(
        technology, project, spec_path, project_entry, technology_entry
    )
    diagram, nodes, edges = validate_spec(spec)
    if _compact(diagram.get("technology")) != _compact(technology):
        raise ProjectDeliveryError(
            f"质控定义技术为 {diagram.get('technology')}，与查询技术 {technology} 不一致。"
        )
    drawio_name, html_name = _output_names(diagram)

    if target_dir.exists() and not overwrite:
        raise ProjectDeliveryError(
            f"目标项目目录已存在，已停止以避免覆盖：{target_dir}；确认后可使用 --overwrite。"
        )
    if target_dir.exists() and not target_dir.is_dir():
        raise ProjectDeliveryError(f"目标项目路径不是目录：{target_dir}")

    with TemporaryDirectory(prefix="molecular-qc-project-") as temporary:
        staging = Path(temporary) / "delivery"
        staging.mkdir()
        drawio_path = staging / drawio_name
        html_path = staging / html_name
        tree = build_drawio(
            diagram,
            nodes,
            edges,
            schema_version=str(spec.get("schema_version") or "1.1"),
            measurements=spec.get("measurements") or [],
        )
        tree.getroot().set("data-generator", "molecular-pathology-qc-flow")
        tree.getroot().set("data-generator-version", DELIVERY_VERSION)
        tree.write(drawio_path, encoding="utf-8", xml_declaration=True)
        validate_drawio(drawio_path)

        html_content = build_qc_html(
            spec,
            diagram,
            nodes,
            edges,
            project_entry,
            technology_entry,
            drawio_name,
        )
        validate_qc_html(html_content)
        html_path.write_text(html_content, encoding="utf-8")
        if "\ufffd" in drawio_path.read_text(encoding="utf-8"):
            raise ProjectDeliveryError("Draw.io 包含中文替换字符。")

        target_dir.parent.mkdir(parents=True, exist_ok=True)
        if target_dir.exists():
            shutil.copy2(drawio_path, target_dir / drawio_name)
            shutil.copy2(html_path, target_dir / html_name)
        else:
            shutil.copytree(staging, target_dir)

    final_files = [target_dir / drawio_name, target_dir / html_name]
    return target_dir, final_files


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="查询分子病理技术和项目，并默认在 Windows 下载目录生成 Draw.io + HTML。"
    )
    parser.add_argument("--technology", required=True, help="技术，例如 PCR")
    parser.add_argument("--project", required=True, help="项目，例如 肺癌3+8")
    parser.add_argument("--output-root", type=Path, help="覆盖默认下载根目录，仅用于测试或显式指定")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX, help="技术项目知识索引")
    parser.add_argument("--spec", type=Path, help="可选项目专用质控 JSON")
    parser.add_argument(
        "--evidence-overlay",
        type=Path,
        help="本次在线检索形成的证据 JSON；只合并到本次 HTML/Draw.io，不回写知识索引",
    )
    parser.add_argument("--overwrite", action="store_true", help="仅覆盖同名交付文件，不删除目录中其他内容")
    return parser.parse_args()


def main() -> int:
    """执行项目查询和默认下载交付。"""
    args = parse_args()
    try:
        target_dir, files = generate_project_delivery(
            args.technology,
            args.project,
            output_root=args.output_root,
            index_path=args.index,
            spec_path=args.spec,
            evidence_overlay=args.evidence_overlay,
            overwrite=args.overwrite,
        )
    except (
        OSError,
        DownloadsPathError,
        SpecValidationError,
        DrawioValidationError,
        HtmlValidationError,
        ProjectDeliveryError,
        ValueError,
    ) as exc:
        print(f"项目交付生成失败：{exc}", file=sys.stderr)
        return 1
    print(f"默认下载目录识别/使用成功：{target_dir.parents[1]}")
    print(f"项目目录：{target_dir}")
    for path in files:
        print(f"- {path.name}")
    return 0


if __name__ == "__main__":
    configure_console_encoding()
    raise SystemExit(main())
