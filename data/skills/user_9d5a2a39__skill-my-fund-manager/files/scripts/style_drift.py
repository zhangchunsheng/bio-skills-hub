"""
风格漂移检测（v2.0.0 新增）。

每次 smart_update 自动追加 style_radar 到 data/style_history/{id}.jsonl，
跨期对比维度差异（Euclidean 距离），超过阈值报警。

零 LLM 依赖。
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import _common
from _common import load_manager, log

import style_radar as sr


def _history_dir() -> str:
    return os.path.join(_common.DATA_DIR, "style_history")


def _path(manager_id: str) -> str:
    return os.path.join(_history_dir(), f"{manager_id}.jsonl")


def record_style(manager_id: str, radar: Dict) -> None:
    """追加一期 style_radar 到 JSONL。"""
    os.makedirs(_history_dir(), exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "manager_id": manager_id,
        "radar": radar,
    }
    with open(_path(manager_id), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    log.info(f"经理 {manager_id} style_radar 已记录到 history")


def get_history(manager_id: str, limit: int = 8) -> List[Dict]:
    path = _path(manager_id)
    if not os.path.exists(path):
        return []
    lines = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return []
    recent = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            recent.append(json.loads(line))
        except json.JSONDecodeError:
            continue
        if len(recent) >= limit:
            break
    return list(reversed(recent))


def _flatten_radar(radar: Dict) -> List[float]:
    """把 6 维雷达展开成 12 维数值向量（每维 2 个分值）。"""
    vec = []
    for dim in ("value_growth", "market_cap", "momentum", "quality", "concentration", "turnover"):
        v = radar.get(dim, {})
        # 取前两个 key 作有序对
        keys = list(v.keys())[:2]
        for k in keys:
            vec.append(float(v.get(k, 50)))
    return vec


def _euclidean(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        return 0.0
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def detect_drift(manager_id: str, threshold: float = 15.0) -> Optional[Dict]:
    """
    漂移检测：对比最近 2 期 style_radar。
    threshold: Euclidean 距离阈值（默认 15.0）。
    """
    history = get_history(manager_id, limit=2)
    if len(history) < 2:
        return None
    latest, previous = history[-1], history[-2]
    vec_latest = _flatten_radar(latest["radar"])
    vec_previous = _flatten_radar(previous["radar"])
    distance = _euclidean(vec_latest, vec_previous)
    if distance >= threshold:
        return {
            "manager_id": manager_id,
            "drift_detected": True,
            "from_ts": previous["ts"],
            "to_ts": latest["ts"],
            "distance": round(distance, 2),
            "magnitude": "high" if distance >= threshold * 2 else "medium",
            "details": f"近 2 期风格雷达 Euclidean 距离 = {distance:.1f}（阈值 {threshold}）",
        }
    return None


def render_drift_report(manager_id: str) -> str:
    """渲染最近 4 期风格轨迹。"""
    history = get_history(manager_id, limit=4)
    if not history:
        return "（无风格历史，请先运行 style_radar.py）"
    lines = [f"📐 {manager_id} 风格漂移轨迹（最近 {len(history)} 期）："]
    for h in history:
        radar = h.get("radar", {})
        # 简化为 6 个特征值
        keys_summary = []
        for dim in ("value_growth", "market_cap", "momentum", "quality", "concentration", "turnover"):
            v = radar.get(dim, {})
            keys = list(v.keys())
            if len(keys) >= 2:
                ratio = v[keys[0]] / 100
                keys_summary.append(f"{keys[0][:1]}{ratio:.1f}")
        sig = "|".join(keys_summary)
        lines.append(f"  {h['ts']}  {sig}")
    # 漂移检测
    drift = detect_drift(manager_id)
    if drift:
        lines.append(f"\n⚠️  漂移预警：{drift['details']}（幅度={drift['magnitude']}）")
    else:
        lines.append("\n✅ 风格稳定")
    return "\n".join(lines)


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="风格漂移检测")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_record = sub.add_parser("record", help="记录当期雷达")
    p_record.add_argument("manager_id")

    p_drift = sub.add_parser("drift", help="检测漂移")
    p_drift.add_argument("manager_id")
    p_drift.add_argument("--threshold", type=float, default=15.0)

    p_report = sub.add_parser("report", help="渲染轨迹")
    p_report.add_argument("manager_id")

    args = parser.parse_args()

    if args.cmd == "record":
        mgr = _common.load_manager(args.manager_id)
        if not mgr:
            print(f"经理档案 {args.manager_id} 不存在")
            sys.exit(1)
        radar = sr.compute_radar(mgr)
        record_style(args.manager_id, radar)
        print(f"✅ 已记录 style_radar 到 history")
    elif args.cmd == "drift":
        d = detect_drift(args.manager_id, args.threshold)
        if d:
            print(f"⚠️  漂移检测：{d['details']}（幅度={d['magnitude']}）")
        else:
            print("✅ 无显著风格漂移")
    elif args.cmd == "report":
        print(render_drift_report(args.manager_id))