#!/usr/bin/env python3
"""Score a structured risk register without inventing residual-risk reductions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_THRESHOLDS = [
    {"max": 4, "level": "低"},
    {"max": 9, "level": "中"},
    {"max": 16, "level": "高"},
    {"max": 25, "level": "极高"},
]
VALID_EVIDENCE = {"verified", "partial", "self_declared", "conflicting", "missing"}


def impact_value(block: dict[str, Any], matrix: dict[str, Any], warnings: list[str], risk_id: str) -> float | None:
    impacts = block.get("impacts")
    if not isinstance(impacts, dict) or not impacts:
        warnings.append(f"{risk_id}: 缺少影响维度")
        return None
    values: list[tuple[str, float]] = []
    for name, raw in impacts.items():
        try:
            value = float(raw)
        except (TypeError, ValueError):
            warnings.append(f"{risk_id}: 影响维度 {name} 不是数字")
            continue
        values.append((str(name), value))
    if not values:
        return None

    method = matrix.get("impact_method", "max")
    if method == "max":
        return max(value for _, value in values)
    if method == "weighted_average":
        weights = matrix.get("impact_weights")
        if not isinstance(weights, dict) or not weights:
            warnings.append(f"{risk_id}: 选择加权影响但未提供 impact_weights")
            return None
        total_weight = 0.0
        weighted = 0.0
        for name, value in values:
            try:
                weight = float(weights.get(name, 0))
            except (TypeError, ValueError):
                warnings.append(f"{risk_id}: 影响权重 {name} 不是数字")
                return None
            total_weight += weight
            weighted += value * weight
        if total_weight <= 0:
            warnings.append(f"{risk_id}: 影响权重总和必须大于 0")
            return None
        return weighted / total_weight
    warnings.append(f"{risk_id}: 未知 impact_method={method}")
    return None


def level_for(score: float | None, matrix: dict[str, Any]) -> str | None:
    if score is None:
        return None
    thresholds = matrix.get("thresholds", DEFAULT_THRESHOLDS)
    if isinstance(thresholds, dict):
        thresholds = [
            {"max": thresholds.get("low", 4), "level": "低"},
            {"max": thresholds.get("medium", 9), "level": "中"},
            {"max": thresholds.get("high", 16), "level": "高"},
            {"max": thresholds.get("critical", 25), "level": "极高"},
        ]
    try:
        ordered = sorted(thresholds, key=lambda item: float(item["max"]))
        for item in ordered:
            if score <= float(item["max"]):
                return str(item["level"])
    except (KeyError, TypeError, ValueError):
        return "分级配置错误"
    return "超出量表"


def score_block(
    block: Any,
    matrix: dict[str, Any],
    warnings: list[str],
    risk_id: str,
    label: str,
) -> tuple[float | None, float | None, float | None]:
    if not isinstance(block, dict):
        warnings.append(f"{risk_id}: 缺少{label}风险评价")
        return None, None, None
    try:
        likelihood = float(block["likelihood"])
    except (KeyError, TypeError, ValueError):
        warnings.append(f"{risk_id}: {label}风险缺少有效 likelihood")
        return None, None, None
    impact = impact_value(block, matrix, warnings, risk_id)
    if impact is None:
        return likelihood, None, None

    max_likelihood = float(matrix.get("likelihood_max", 5))
    max_impact = float(matrix.get("impact_max", 5))
    if not (1 <= likelihood <= max_likelihood):
        warnings.append(f"{risk_id}: {label}可能性 {likelihood:g} 超出 1—{max_likelihood:g}")
        return likelihood, impact, None
    if not (1 <= impact <= max_impact):
        warnings.append(f"{risk_id}: {label}影响 {impact:g} 超出 1—{max_impact:g}")
        return likelihood, impact, None
    return likelihood, impact, likelihood * impact


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    matrix = data.get("matrix") if isinstance(data.get("matrix"), dict) else {}
    warnings: list[str] = []
    if not matrix.get("scale_source"):
        warnings.append("矩阵未提供 scale_source；当前阈值只能视为分析假设")
    if "thresholds" not in matrix:
        warnings.append("未提供 thresholds；使用示例阈值 1—4/5—9/10—16/17—25")

    results: list[dict[str, Any]] = []
    risks = data.get("risks")
    if not isinstance(risks, list):
        raise ValueError("risks 必须是数组")

    for index, risk in enumerate(risks, 1):
        if not isinstance(risk, dict):
            warnings.append(f"第 {index} 项风险不是对象")
            continue
        risk_id = str(risk.get("id") or f"R{index}")
        evidence = str(risk.get("evidence_status") or "missing")
        if evidence not in VALID_EVIDENCE:
            warnings.append(f"{risk_id}: 未知 evidence_status={evidence}")

        il, ii, inherent_score = score_block(
            risk.get("inherent"), matrix, warnings, risk_id, "固有"
        )
        residual = risk.get("residual")
        if residual is None:
            rl = ri = residual_score = None
            warnings.append(f"{risk_id}: 未提供剩余风险；未根据控制描述自动折减")
        else:
            rl, ri, residual_score = score_block(
                residual, matrix, warnings, risk_id, "剩余"
            )
            if evidence in {"self_declared", "conflicting", "missing"}:
                warnings.append(
                    f"{risk_id}: 已给出剩余风险，但控制证据状态为 {evidence}，需保守复核"
                )

        critical = bool(risk.get("critical_trigger"))
        results.append(
            {
                "id": risk_id,
                "title": str(risk.get("title") or "未命名风险"),
                "category": str(risk.get("category") or "未分类"),
                "inherent_likelihood": il,
                "inherent_impact": ii,
                "inherent_score": inherent_score,
                "inherent_level": "红线/极高" if critical else level_for(inherent_score, matrix),
                "residual_likelihood": rl,
                "residual_impact": ri,
                "residual_score": residual_score,
                "residual_level": (
                    "红线/不可接受"
                    if critical
                    else level_for(residual_score, matrix)
                ),
                "critical_trigger": critical,
                "evidence_status": evidence,
                "owner": risk.get("owner"),
                "due_date": risk.get("due_date"),
            }
        )

    def sort_key(item: dict[str, Any]) -> tuple[int, float, float]:
        residual_score = item["residual_score"]
        inherent_score = item["inherent_score"]
        return (
            1 if item["critical_trigger"] else 0,
            float(residual_score if residual_score is not None else -1),
            float(inherent_score if inherent_score is not None else -1),
        )

    results.sort(key=sort_key, reverse=True)
    return {
        "assessment": data.get("assessment", {}),
        "matrix": matrix,
        "results": results,
        "warnings": warnings,
        "notice": "分值仅用于同一口径下排序；不得跨风险相加或平均，也不代表概率或金额。",
    }


def markdown(result: dict[str, Any]) -> str:
    lines = [
        "# 风险评分结果",
        "",
        result["notice"],
        "",
        "| 排名 | ID | 风险 | 固有风险 | 剩余风险 | 红线 | 证据状态 | 责任人 | 日期 |",
        "|---:|---|---|---|---|---|---|---|---|",
    ]
    for rank, item in enumerate(result["results"], 1):
        inherent = (
            "未评"
            if item["inherent_score"] is None
            else f'{item["inherent_score"]:g} / {item["inherent_level"]}'
        )
        residual = (
            "无法确定"
            if item["residual_score"] is None
            else f'{item["residual_score"]:g} / {item["residual_level"]}'
        )
        lines.append(
            f'| {rank} | {item["id"]} | {item["title"]} | {inherent} | '
            f'{residual} | {"是" if item["critical_trigger"] else "否"} | '
            f'{item["evidence_status"]} | {item["owner"] or "待定"} | '
            f'{item["due_date"] or "待定"} |'
        )
    if result["warnings"]:
        lines.extend(["", "## 警告", ""])
        lines.extend(f"- {warning}" for warning in result["warnings"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON 风险清单")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = evaluate(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    rendered = (
        json.dumps(result, ensure_ascii=False, indent=2)
        if args.format == "json"
        else markdown(result)
    )
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="" if rendered.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
