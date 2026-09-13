#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行分子病理质控 Skill 的可重复回归自检。

说明：所有测试产物写入 TemporaryDirectory，执行结束自动清理，不保留临时文件。
Author: WangYunL
"""

from __future__ import annotations

import json
import hashlib
import sys
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

from build_example_delivery import build_example_delivery
from build_qc_bundle import BundleBuildError, build_bundle
from generate_project_delivery import ProjectDeliveryError, generate_project_delivery
from generate_drawio import build_drawio
from migrate_qc_spec import migrate_legacy_spec
from qc_flow_layout import resolve_layout
from qc_flow_model import SpecValidationError, load_spec, normalize_spec, validate_spec
from query_knowledge import load_index, search_index
from render_drawio_preview import parse_drawio, render_png, render_svg
from render_qc_html import validate_qc_html
from validate_drawio import DrawioValidationError, validate_drawio
from windows_downloads import resolve_downloads_dir


SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS = SKILL_ROOT / "assets"
SCHEMA_PATH = SKILL_ROOT / "references" / "qc-flow.schema.json"
EXAMPLE_SPECS = (
    ASSETS / "BRAF-V600E下机质控.json",
    ASSETS / "NGS通用质控.json",
    ASSETS / "FISH-ALK通用质控.json",
    ASSETS / "Sanger通用质控.json",
)


class SelfCheckError(AssertionError):
    """表示一项回归自检未满足预期。"""


def _assert(condition: bool, message: str) -> None:
    """使用带中文原因的断言。"""
    if not condition:
        raise SelfCheckError(message)


def _expect_spec_error(spec: dict, message_fragment: str) -> None:
    """确认无效 JSON 被模型层拒绝，并包含预期错误信息。"""
    try:
        validate_spec(spec)
    except SpecValidationError as exc:
        _assert(message_fragment in str(exc), f"错误信息未包含：{message_fragment}")
        return
    raise SelfCheckError(f"无效质控 JSON 未被拒绝：{message_fragment}")


def _base_cycle_spec(with_terminal_exit: bool) -> dict:
    """构造用于循环与终点语义测试的最小 v1.1 流程。"""
    nodes = [
        {
            "id": "start",
            "type": "start",
            "label": "开始",
            "stage": "阶段",
            "evidence_refs": ["source"],
        },
        {
            "id": "decision",
            "type": "decision",
            "label": "是否通过？",
            "stage": "阶段",
            "condition": {
                "operator": "CUSTOM",
                "expression": "依据当前 SOP 判断",
                "missing_policy": "manual_review",
            },
            "evidence_refs": ["source"],
        },
        {
            "id": "repeat",
            "type": "process",
            "label": "复检处理",
            "stage": "阶段",
            "evidence_refs": ["source"],
        },
    ]
    edges = [
        {
            "id": "e1",
            "source": "start",
            "target": "decision",
            "label": "",
            "branch": "next",
            "evidence_refs": ["source"],
        },
        {
            "id": "e2",
            "source": "decision",
            "target": "repeat",
            "label": "否（复检）",
            "branch": "repeat",
            "evidence_refs": ["source"],
        },
        {
            "id": "e3",
            "source": "repeat",
            "target": "decision",
            "label": "复检后重判",
            "branch": "repeat",
            "evidence_refs": ["source"],
        },
    ]
    if with_terminal_exit:
        nodes.append(
            {
                "id": "pass",
                "type": "pass",
                "label": "通过",
                "stage": "阶段",
                "terminal_result": "pass",
                "evidence_refs": ["source"],
            }
        )
        edges.append(
            {
                "id": "e4",
                "source": "decision",
                "target": "pass",
                "label": "是（通过）",
                "branch": "pass",
                "evidence_refs": ["source"],
            }
        )
    return {
        "$schema": "../references/qc-flow.schema.json",
        "schema_version": "1.1",
        "diagram": {
            "name": "循环测试",
            "id": "cycle_test",
            "technology": "测试",
            "method": "测试",
            "project": "测试",
            "qc_stage": "阶段",
            "stages": ["阶段"],
            "sources": [
                {
                    "id": "source",
                    "type": "user-confirmed",
                    "title": "测试来源",
                    "version": "1",
                    "last_verified": "2026-08-27",
                    "path": "self-check",
                    "scope_note": "仅用于自检",
                    "evidence_status": "confirmed",
                }
            ],
            "layout": {
                "mode": "flow",
                "page_width": 400,
                "page_height": 400,
                "auto_size": True,
                "show_source_note": True,
            },
        },
        "measurements": [],
        "nodes": nodes,
        "edges": edges,
    }


def _validate_json_schema(specs: list[dict]) -> str:
    """安装 jsonschema 时执行标准 Schema 校验，否则由语义校验兜底。"""
    try:
        import jsonschema
    except ImportError:
        return "跳过（当前 Python 未安装 jsonschema，语义校验仍已执行）"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8-sig"))
    for spec in specs:
        jsonschema.validate(spec, schema)
    return "通过"


def run_checks() -> list[str]:
    """执行 Schema、生成、校验、布局、预览和查询回归。"""
    messages: list[str] = []
    specs = [load_spec(path) for path in EXAMPLE_SPECS]
    messages.append(f"示例 JSON 读取通过：{len(specs)} 个")
    messages.append(f"JSON Schema：{_validate_json_schema(specs)}")

    for path, spec in zip(EXAMPLE_SPECS, specs):
        diagram, nodes, edges = validate_spec(spec)
        _assert(diagram and nodes and edges, f"语义校验未返回完整数据：{path.name}")
    messages.append("PCR/NGS/FISH/Sanger 语义校验通过")

    braf = specs[0]
    expected_labels = {
        "start": "PCR 下机数据",
        "fam_direct": "FAM Ct ≤ 24？",
        "fam_gray": "FAM 有 Ct 且<br>24 < Ct < 35？",
        "vic_gray": "VIC Ct ≤ 20？",
        "delta_proc": "计算 ΔCt = FAM Ct − VIC Ct",
        "delta": "ΔCt ≤ 13？",
    }
    actual_labels = {node["id"]: node["label"] for node in braf["nodes"]}
    for node_id, label in expected_labels.items():
        _assert(actual_labels.get(node_id) == label, f"BRAF 节点文字变化：{node_id}")
    _assert(len(braf["nodes"]) == 11 and len(braf["edges"]) == 10, "BRAF 节点或连线数量变化")
    messages.append("BRAF 关键文字及 11 节点/10 连线基线通过")

    no_terminal = _base_cycle_spec(with_terminal_exit=False)
    _expect_spec_error(no_terminal, "至少需要一个明确的终点节点")
    cycle_with_exit = _base_cycle_spec(with_terminal_exit=True)
    validate_spec(cycle_with_exit)
    messages.append("无终点循环已拒绝；带终点出口的复检循环已接受")

    bad_evidence = deepcopy(cycle_with_exit)
    bad_evidence["nodes"][0]["evidence_refs"] = ["missing_source"]
    _expect_spec_error(bad_evidence, "引用了不存在的来源")
    duplicate_branch = deepcopy(cycle_with_exit)
    duplicate_branch["edges"][1]["label"] = "重复"
    duplicate_branch["edges"][3]["label"] = "重复"
    _expect_spec_error(duplicate_branch, "重复分支文字")
    messages.append("证据悬空引用和重复判断分支均已拒绝")

    expanded = deepcopy(cycle_with_exit)
    next(node for node in expanded["nodes"] if node["id"] == "pass").update(
        {"x": 1800, "y": 1200}
    )
    diagram, nodes, edges = validate_spec(expanded)
    layout = resolve_layout(diagram, nodes, edges)
    _assert(layout.page_width > 1800 and layout.page_height > 1200, "页面未按远端节点自动扩展")
    messages.append("页面宽高自适应通过")

    index = load_index()
    query_expectations = {
        "PCR BRAF": "project_braf_v600e",
        "EGFR": "project_egfr",
        "NGS Q30": "technology_ngs",
        "ALK FISH": "project_alk_fish",
        "Sanger 峰图": "technology_sanger",
        "ARMS-PCR": "method_arms_pcr",
        "ddPCR": "method_digital_pcr",
        "肺癌3+8": "project_lung_3_plus_8",
    }
    for query, expected_id in query_expectations.items():
        results = search_index(index, query, limit=3)
        _assert(results and results[0]["id"] == expected_id, f"知识查询首条不正确：{query}")
    messages.append("PCR/BRAF、肺癌3+8、ARMS、数字PCR、EGFR、NGS、FISH/ALK、Sanger 查询回归通过")

    with TemporaryDirectory(prefix="molecular-qc-self-check-") as temporary:
        temporary_path = Path(temporary)
        for index_number, raw_spec in enumerate(specs, start=1):
            spec = normalize_spec(raw_spec)
            diagram, nodes, edges = validate_spec(spec)
            tree = build_drawio(
                diagram,
                nodes,
                edges,
                schema_version=str(spec["schema_version"]),
                measurements=spec["measurements"],
            )
            drawio_path = temporary_path / f"example_{index_number}.drawio"
            tree.write(drawio_path, encoding="utf-8", xml_declaration=True)
            page_count, vertex_count, edge_count = validate_drawio(drawio_path)
            _assert(page_count == 1, "生成结果图页数量不正确")
            _assert(vertex_count == len(nodes) and edge_count == len(edges), "业务节点或连线计数不一致")
            preview_path = temporary_path / f"example_{index_number}.svg"
            render_svg(parse_drawio(drawio_path), preview_path)
            _assert(preview_path.exists() and preview_path.stat().st_size > 0, "SVG 预览生成失败")

        braf_drawio = temporary_path / "example_1.drawio"
        raw_xml = braf_drawio.read_text(encoding="utf-8")
        _assert("data-condition=" in raw_xml and "data-sources=" in raw_xml, "业务元数据未写入 Draw.io")
        _assert("24 &amp;lt; Ct &amp;lt; 35" in raw_xml, "字面小于号未安全编码")

        parsed = ET.parse(braf_drawio)
        first_edge = parsed.find(".//mxCell[@edge='1']")
        _assert(first_edge is not None, "测试图缺少连线")
        first_edge.attrib.pop("target", None)
        broken_path = temporary_path / "broken.drawio"
        parsed.write(broken_path, encoding="utf-8", xml_declaration=True)
        try:
            validate_drawio(broken_path)
        except DrawioValidationError:
            pass
        else:
            raise SelfCheckError("缺少 target 的 Draw.io 连线未被拒绝")

        ngs_drawio = temporary_path / "example_2.drawio"
        ngs_root = ET.parse(ngs_drawio).getroot()
        stage_cells = ngs_root.findall(".//mxCell[@data-role='stage']")
        _assert(len(stage_cells) == 5, "NGS 阶段泳道数量不正确")

        try:
            import PIL  # noqa: F401
        except ImportError:
            messages.append("PNG 预览：跳过（当前 Python 未安装 Pillow）")
        else:
            png_path = temporary_path / "braf.png"
            render_png(parse_drawio(braf_drawio), png_path, 1.0)
            _assert(png_path.exists() and png_path.stat().st_size > 0, "PNG 预览生成失败")
            messages.append("SVG/PNG 结构预览通过")

        bundle_dir = temporary_path / "single_bundle"
        bundle_files = build_bundle(
            EXAMPLE_SPECS[0], bundle_dir, None, "svg", SKILL_ROOT / "references" / "技术项目索引.json"
        )
        _assert(len(bundle_files) == 5, "单项目完整交付包文件数量不正确")
        manifest_path = next(path for path in bundle_files if path.name.endswith("_交付清单.json"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest["files"]:
            file_path = bundle_dir / item["name"]
            digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
            _assert(digest == item["sha256"], f"交付清单哈希不一致：{item['name']}")
        try:
            build_bundle(
                EXAMPLE_SPECS[0], bundle_dir, None, "svg", SKILL_ROOT / "references" / "技术项目索引.json"
            )
        except BundleBuildError:
            pass
        else:
            raise SelfCheckError("完整交付包生成器未拒绝覆盖现有目录")
        messages.append("单项目完整交付包、SHA-256 清单和防覆盖通过")

        examples_root = temporary_path / "example_delivery"
        example_entries = build_example_delivery(examples_root, "svg")
        _assert(
            {"BRAF-V600E", "NGS", "FISH-ALK", "Sanger"}.issubset(
                {path.name for path in example_entries}
            ),
            "四套示例交付目录不完整",
        )
        _assert((examples_root / "总交付清单.json").exists(), "总交付清单未生成")
        messages.append("四套示例完整交付回归通过")

        downloads = temporary_path / "Downloads"
        downloads.mkdir()
        _assert(resolve_downloads_dir(downloads) == downloads.resolve(), "下载目录覆盖解析失败")
        project_dir, project_files = generate_project_delivery(
            "PCR", "肺癌3+8", output_root=downloads
        )
        expected_project_names = {
            "肺癌3+8下机质控_流程图.drawio",
            "肺癌3+8下机质控配置方案.html",
        }
        _assert(
            {path.name for path in project_files} == expected_project_names,
            "肺癌3+8 默认交付文件名不正确",
        )
        _assert(len(list(project_dir.iterdir())) == 2, "默认项目目录不是严格两个文件")
        _assert(project_dir.relative_to(downloads).as_posix() == "PCR/肺癌3+8", "下载目录层级不正确")
        page_count, vertex_count, edge_count = validate_drawio(project_files[0])
        _assert(
            (page_count, vertex_count, edge_count) == (1, 12, 13),
            "肺癌3+8 Draw.io 结构计数不正确",
        )
        html_path = next(path for path in project_files if path.suffix == ".html")
        html_content = html_path.read_text(encoding="utf-8")
        validate_qc_html(html_content)
        for expected_text in ("肿瘤相关11基因", "AmoyDx", "待确认项", "CUSTOM"):
            _assert(expected_text in html_content, f"肺癌3+8 HTML 缺少：{expected_text}")
        try:
            generate_project_delivery("PCR", "肺癌3+8", output_root=downloads)
        except ProjectDeliveryError:
            pass
        else:
            raise SelfCheckError("项目交付生成器未拒绝覆盖现有目录")
        messages.append("默认下载/PCR/肺癌3+8 两文件交付、HTML、Draw.io 和防覆盖通过")

        online_downloads = temporary_path / "OnlineDownloads"
        online_downloads.mkdir()
        overlay_path = temporary_path / "online-evidence.json"
        overlay_path.write_text(
            json.dumps(
                {
                    "query": {"technology": "PCR", "project": "在线自检项目"},
                    "project_entry": {
                        "summary": "本次在线核对摘要",
                        "principle": "本次在线核对原理",
                        "qc_sources": [
                            {
                                "id": "online_source",
                                "type": "official-technical-document",
                                "title": "在线官方来源",
                                "version": "2026",
                                "last_verified": "2026-08-27",
                                "url": "https://example.org/official",
                                "scope_note": "仅用于在线覆盖自检",
                                "evidence_status": "confirmed",
                            }
                        ],
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        _, online_files = generate_project_delivery(
            "PCR",
            "在线自检项目",
            output_root=online_downloads,
            evidence_overlay=overlay_path,
        )
        online_html = next(path for path in online_files if path.suffix == ".html").read_text(
            encoding="utf-8"
        )
        _assert("本次在线核对摘要" in online_html and "在线官方来源" in online_html, "在线证据覆盖未进入 HTML")
        messages.append("本次在线证据覆盖合并通过")

        legacy = deepcopy(specs[0])
        legacy.pop("$schema", None)
        legacy["schema_version"] = "1.0"
        legacy_diagram = legacy["diagram"]
        legacy_diagram["source"] = {"name": "旧版 BRAF 图", "version": "1.0"}
        for field in ("sources", "method", "stages"):
            legacy_diagram.pop(field, None)
        legacy.pop("measurements", None)
        for node in legacy["nodes"]:
            for field in ("stage", "evidence_refs", "condition", "terminal_result"):
                node.pop(field, None)
        for edge in legacy["edges"]:
            for field in ("branch", "evidence_refs"):
                edge.pop(field, None)
        migrated, review = migrate_legacy_spec(
            legacy, EXAMPLE_SPECS[0], "2026-08-27"
        )
        validate_spec(migrated)
        _assert(migrated["schema_version"] == "1.1", "迁移结果版本不正确")
        _assert(
            all(
                node["condition"]["operator"] == "CUSTOM"
                for node in migrated["nodes"]
                if node["type"] == "decision"
            ),
            "旧版无结构条件时不应自动猜测数值运算符",
        )
        _assert(any("不会从节点文字推断数值阈值" in item for item in review), "迁移复核记录缺少阈值边界")
        messages.append("v1.0→v1.1 可审计迁移和不猜阈值边界通过")
    messages.append("Draw.io 元数据、泳道、HTML、悬空连线和独立校验通过")
    messages.append("TemporaryDirectory 已自动清理")
    return messages


def main() -> int:
    """执行自检并输出逐项结果。"""
    try:
        messages = run_checks()
    except (OSError, ValueError, SelfCheckError) as exc:
        print(f"自检失败：{exc}", file=sys.stderr)
        return 1
    for message in messages:
        print(f"[通过] {message}")
    print("全部回归自检通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
