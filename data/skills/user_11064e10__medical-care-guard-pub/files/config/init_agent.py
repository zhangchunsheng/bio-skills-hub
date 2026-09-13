# -*- coding: utf-8 -*-
# Copyright (c) Joyxj2devs Team. All rights reserved.
"""技能自检：确认知识服务通道可用、核心工具可调、离线兜底存在。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mcp_client  # noqa: E402

CHECKS = []


def _check(name: str, fn):
    try:
        ok, detail = fn()
    except Exception as exc:  # noqa: BLE001
        ok, detail = False, f"异常: {exc}"
    CHECKS.append((name, ok, detail))


def main() -> int:
    _check("知识库清单", lambda: (
        len(mcp_client.kb_list().get("documents", [])) >= 4,
        f"{len(mcp_client.kb_list().get('documents', []))} 篇语料",
    ))
    _check("政策问答", lambda: (
        bool(mcp_client.life_policy_ask("被裁员该不该签自愿离职").get("answer")),
        "检索通道正常",
    ))
    _check("补偿测算", lambda: (
        mcp_client.rights_calculate("severance", {
            "work_years": 6.25, "monthly_wage": 28000,
            "local_social_avg_wage": 12183, "termination_type": "negotiated",
        }).get("amount", 0) > 0,
        "N 值计算正常",
    ))
    _check("风险闸门", lambda: (
        mcp_client.risk_check({
            "city": "深圳", "neo_employment": True, "has_business_license": True,
        }).get("level") == "L2",
        "L2 红线可触发",
    ))
    _check("时间轴", lambda: (
        len(mcp_client.timeline_plan("unemployment", "2026-08-05").get("items", [])) >= 8,
        "时间轴节点齐备",
    ))
    _check("离线兜底", lambda: (
        (Path(__file__).resolve().parents[1] / "offline_workflows").exists(),
        "offline_workflows 存在",
    ))

    passed = sum(1 for _, ok, _ in CHECKS if ok)
    for name, ok, detail in CHECKS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} - {detail}")
    print(f"\n自检结果: {passed}/{len(CHECKS)} 通过")
    return 0 if passed == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
