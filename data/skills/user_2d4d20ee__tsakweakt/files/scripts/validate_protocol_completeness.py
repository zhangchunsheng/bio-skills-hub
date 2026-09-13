#!/usr/bin/env python3
"""Validate normalized protocol components using protocol-completeness-v1."""

from __future__ import annotations

import json
import sys
from typing import Any

RULES = {
    "background_and_objective": ("BACKGROUND_OBJECTIVE_MISSING", "研究背景与目的"),
    "study_design": ("STUDY_DESIGN_MISSING", "研究设计类型"),
    "eligibility.inclusion": ("INCLUSION_CRITERIA_MISSING", "纳入标准"),
    "eligibility.exclusion": ("EXCLUSION_CRITERIA_MISSING", "排除标准"),
    "sample_size.basis": ("SAMPLE_SIZE_BASIS_MISSING", "样本量计算依据"),
    "outcomes.primary": ("PRIMARY_OUTCOME_MISSING", "主要终点指标"),
    "outcomes.secondary": ("SECONDARY_OUTCOME_MISSING", "次要终点指标"),
    "statistical_analysis": ("STATISTICAL_ANALYSIS_MISSING", "统计分析方法"),
    "references": ("REFERENCES_MISSING", "参考文献列表"),
}


def empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set)):
        return not value or all(empty(item) for item in value)
    if isinstance(value, dict):
        return not value or all(empty(item) for item in value.values())
    return False


def get_path(obj: dict[str, Any], path: str) -> Any:
    current: Any = obj
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    components = payload.get("components", payload)
    missing, present = [], []
    for field, (code, label) in RULES.items():
        if empty(get_path(components, field)):
            missing.append({"code": code, "label": label, "field": field, "severity": "BLOCKER"})
        else:
            present.append(label)
    picos = components.get("picos") or {}
    from validate_picos_completeness import validate as validate_picos
    picos_report = validate_picos(picos)
    missing.extend(picos_report["missing_items"])
    if picos_report["valid"]:
        present.append("PICOS各要素")
    warnings = payload.get("extraction_warnings", [])
    uncertain = any(
        (isinstance(item, str) and "EXTRACTION_UNCERTAIN" in item)
        or (isinstance(item, dict) and item.get("code") == "EXTRACTION_UNCERTAIN")
        for item in warnings
    )
    if uncertain:
        missing.append({"code": "EXTRACTION_UNCERTAIN", "label": "方案内容抽取不确定", "field": "document", "severity": "BLOCKER"})

    # Component-specific semantic minimums.
    basis = get_path(components, "sample_size.basis")
    if isinstance(basis, dict) and not any(not empty(basis.get(k)) for k in ("method", "formula", "parameters", "rationale")):
        missing.append({"code": "SAMPLE_SIZE_BASIS_INVALID", "label": "样本量计算依据", "field": "sample_size.basis", "severity": "BLOCKER"})
    references = components.get("references")
    if isinstance(references, list) and references and not any(not empty(item) for item in references):
        missing.append({"code": "REFERENCES_INVALID", "label": "参考文献列表", "field": "references", "severity": "BLOCKER"})

    # Deduplicate by code and field.
    missing = list({(item["code"], item["field"]): item for item in missing}.values())
    valid = not missing
    result_label = "完整性校验通过" if valid else "完整性校验不通过"
    popup_message = None if valid else "方案不完整，缺少：[" + "、".join(dict.fromkeys(item["label"] for item in missing)) + "]"
    return {
        "valid": valid,
        "status": "PASS" if valid else "FAIL",
        "validation_result": result_label,
        "branch": "S" if valid else "M",
        "rule_set": payload.get("rule_set", "protocol-completeness-v1"),
        "protocol_artifact_id": payload.get("protocol_artifact_id"),
        "present_items": present,
        "missing_items": missing,
        "warnings": warnings,
        "next_node": "0.2" if valid else "0.1",
        "next_task": "ASSESS_FEASIBILITY" if valid else "RETURN_FOR_REVISION",
        "popup_required": not valid,
        "message": result_label if valid else popup_message,
    }


if __name__ == "__main__":
    raw = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    report = validate(json.loads(raw))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["valid"] else 1)
