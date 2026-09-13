#!/usr/bin/env python3
"""Deterministically validate all PICOS elements."""

from __future__ import annotations

import json
import sys
from typing import Any

FIELDS = {
    "population": ("PICOS_P_MISSING", "研究对象（P）"),
    "intervention": ("PICOS_I_MISSING", "干预/暴露（I）"),
    "comparison": ("PICOS_C_MISSING", "对照（C）"),
    "outcome": ("PICOS_O_MISSING", "结局（O）"),
    "study_design": ("PICOS_S_MISSING", "研究设计（S）"),
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


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    missing = []
    for field, (code, label) in FIELDS.items():
        if empty(payload.get(field)):
            missing.append({"code": code, "label": label, "field": f"picos.{field}", "severity": "BLOCKER"})
    return {"valid": not missing, "status": "PASS" if not missing else "BLOCKED", "missing_items": missing}


if __name__ == "__main__":
    raw = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    report = validate(json.loads(raw))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["valid"] else 1)
