#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为缺少项目专用阈值定义的查询构建安全质控流程。

说明：只生成通用门控和待确认条件，不从项目名称或报告模板猜测阈值。
Author: WangYunL
"""

from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import date
from typing import Any


def _diagram_id(technology: str, project: str) -> str:
    """生成稳定且满足契约的流程 ID。"""
    digest = hashlib.sha256(f"{technology}|{project}".encode("utf-8")).hexdigest()[:12]
    return f"query_qc_{digest}"


def _query_source(technology: str, project: str) -> dict[str, Any]:
    """声明用户查询只确认技术与项目名称，不确认阈值。"""
    return {
        "id": "query_scope",
        "type": "user-confirmed",
        "title": f"用户查询：{technology} / {project}",
        "version": "本次查询",
        "last_verified": date.today().isoformat(),
        "path": f"interactive-query/{technology}/{project}",
        "scope_note": "仅确认查询的技术和项目名称，不代表试剂、平台、阈值或判读算法已确认",
        "evidence_status": "confirmed",
    }


def _sources(
    technology: str,
    project: str,
    project_entry: dict[str, Any] | None,
    technology_entry: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """组合查询来源、项目资料和一条通用技术来源。"""
    sources = [_query_source(technology, project)]
    for source in (project_entry or {}).get("qc_sources") or []:
        if isinstance(source, dict):
            sources.append(deepcopy(source))
    technical_sources = (technology_entry or {}).get("sources") or []
    if technical_sources:
        source = technical_sources[0]
        if isinstance(source, dict) and source.get("url"):
            sources.append(
                {
                    "id": "technology_reference",
                    "type": "official-technical-document",
                    "title": str(source.get("title") or f"{technology} 通用技术资料"),
                    "version": "网页版本",
                    "last_verified": str(source.get("last_verified") or date.today().isoformat()),
                    "url": str(source["url"]),
                    "scope_note": "仅支持通用技术原理和质控维度，不提供项目专用阈值",
                    "evidence_status": "confirmed",
                }
            )
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in sources:
        source_id = str(source.get("id") or "")
        if source_id and source_id not in seen:
            unique.append(source)
            seen.add(source_id)
    return unique


def build_safe_project_spec(
    technology: str,
    project: str,
    project_entry: dict[str, Any] | None = None,
    technology_entry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """生成可验证、可画图且不会虚构阈值的 v1.1 流程。"""
    entry = project_entry or {}
    delivery_name = str(entry.get("delivery_name") or f"{project}下机质控")
    method = str(entry.get("qc_method") or "具体 PCR 方法、试剂和平台待确认")
    qc_stage = str(entry.get("qc_stage") or "下机质控")
    sources = _sources(technology, project, project_entry, technology_entry)
    evidence_refs = [source["id"] for source in sources]
    stages = ["资料门控", "批次质控", "样本质控", "目标判读", "结果复核"]

    def condition(expression: str) -> dict[str, Any]:
        return {
            "operator": "CUSTOM",
            "expression": expression,
            "missing_policy": "manual_review",
        }

    nodes = [
        {
            "id": "start",
            "type": "start",
            "label": f"{technology} {project}<br>下机数据",
            "stage": "资料门控",
            "description": "开始项目下机质控",
            "evidence_refs": evidence_refs,
        },
        {
            "id": "documents_ready",
            "type": "decision",
            "label": "试剂 / 平台 / 软件 / SOP<br>版本是否完整且匹配？",
            "stage": "资料门控",
            "condition": condition("依据当前匹配版本的试剂 IFU、平台、软件和实验室 SOP 确认"),
            "evidence_refs": evidence_refs,
        },
        {
            "id": "manual_review",
            "type": "end",
            "label": "⚠ 暂停自动判读<br>补齐资料并人工复核",
            "stage": "结果复核",
            "terminal_result": "manual_review",
            "evidence_refs": evidence_refs,
        },
        {
            "id": "run_controls",
            "type": "decision",
            "label": "本批次全部对照<br>是否满足项目规则？",
            "stage": "批次质控",
            "condition": condition("阳性、阴性、空白、提取等对照依据当前 SOP/IFU 判定"),
            "evidence_refs": evidence_refs,
        },
        {
            "id": "batch_invalid",
            "type": "invalid",
            "label": "❌ 批次无效<br>排查后重复实验",
            "stage": "批次质控",
            "terminal_result": "invalid",
            "evidence_refs": evidence_refs,
        },
        {
            "id": "sample_valid",
            "type": "decision",
            "label": "样本内参与有效性指标<br>是否满足项目规则？",
            "stage": "样本质控",
            "condition": condition("依据核酸类型、内参、抑制和样本质量规则判定"),
            "evidence_refs": evidence_refs,
        },
        {
            "id": "sample_invalid",
            "type": "invalid",
            "label": "❌ 样本结果无效<br>按 SOP 复检 / 重提",
            "stage": "样本质控",
            "terminal_result": "invalid",
            "evidence_refs": evidence_refs,
        },
        {
            "id": "target_signal",
            "type": "decision",
            "label": "目标曲线 / 信号<br>是否满足对应位点规则？",
            "stage": "目标判读",
            "condition": condition("逐反应管、位点和通道应用匹配版本的判读规则"),
            "evidence_refs": evidence_refs,
        },
        {
            "id": "mapping_consistent",
            "type": "decision",
            "label": "位点、管号 / 通道、结果枚举<br>是否与项目范围一致？",
            "stage": "结果复核",
            "condition": condition("核对项目位点表、管号/通道映射和报告范围"),
            "evidence_refs": evidence_refs,
        },
        {
            "id": "qc_pass",
            "type": "pass",
            "label": "✅ 质控通过<br>进入位点结果人工复核",
            "stage": "结果复核",
            "terminal_result": "pass",
            "evidence_refs": evidence_refs,
        },
        {
            "id": "negative_supported",
            "type": "decision",
            "label": "无目标信号时<br>能否支持未检出结论？",
            "stage": "目标判读",
            "condition": condition("确认对照、内参和项目有效性规则均支持未检出结论"),
            "evidence_refs": evidence_refs,
        },
        {
            "id": "negative_result",
            "type": "negative",
            "label": "⚪ 质控有效的未检出候选<br>进入人工复核",
            "stage": "结果复核",
            "terminal_result": "negative",
            "evidence_refs": evidence_refs,
        },
    ]
    edges = [
        {"id": "e1", "source": "start", "target": "documents_ready", "label": "", "branch": "next"},
        {"id": "e2", "source": "documents_ready", "target": "run_controls", "label": "是", "branch": "yes"},
        {"id": "e3", "source": "documents_ready", "target": "manual_review", "label": "否", "branch": "no"},
        {"id": "e4", "source": "run_controls", "target": "sample_valid", "label": "是", "branch": "yes"},
        {"id": "e5", "source": "run_controls", "target": "batch_invalid", "label": "否", "branch": "no"},
        {"id": "e6", "source": "sample_valid", "target": "target_signal", "label": "是", "branch": "yes"},
        {"id": "e7", "source": "sample_valid", "target": "sample_invalid", "label": "否", "branch": "no"},
        {"id": "e8", "source": "target_signal", "target": "mapping_consistent", "label": "是", "branch": "yes"},
        {"id": "e9", "source": "target_signal", "target": "negative_supported", "label": "否", "branch": "no"},
        {"id": "e10", "source": "mapping_consistent", "target": "qc_pass", "label": "是", "branch": "yes"},
        {"id": "e11", "source": "mapping_consistent", "target": "manual_review", "label": "否", "branch": "no"},
        {"id": "e12", "source": "negative_supported", "target": "negative_result", "label": "是", "branch": "yes"},
        {"id": "e13", "source": "negative_supported", "target": "manual_review", "label": "否", "branch": "no"},
    ]
    for edge in edges:
        edge["evidence_refs"] = list(evidence_refs)

    return {
        "$schema": "../references/qc-flow.schema.json",
        "schema_version": "1.1",
        "diagram": {
            "name": delivery_name,
            "id": _diagram_id(technology, project),
            "technology": technology,
            "method": method,
            "project": project,
            "qc_stage": qc_stage,
            "stages": stages,
            "sources": sources,
            "layout": {
                "mode": "swimlane",
                "page_width": 1680,
                "page_height": 1260,
                "auto_size": True,
                "show_source_note": True,
                "margin": 40,
                "stage_gap": 20,
            },
        },
        "measurements": [],
        "nodes": nodes,
        "edges": edges,
    }

