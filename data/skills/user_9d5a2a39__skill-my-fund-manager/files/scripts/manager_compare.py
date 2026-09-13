#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""基金经理对比工具（v2.0 新增）。

对比 2-4 个基金经理的：
    - 风格 DNA（持仓集中度、行业偏好、规模风格）
    - 业绩（最近1月/3月/6月/1年/3年/今年来）
    - 重仓股重叠度
    - 风险指标（最大回撤/夏普）
    - 管理规模 / 资历

使用：
    from manager_compare import compare_managers
    result = compare_managers(["1", "2", "3"])
    print(result["summary"])

CLI:
    python manager_compare.py 30189741 30189744
"""
from __future__ import annotations

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def _load_manager_data(manager_id: str) -> Dict | None:
    """加载经理的档案数据。"""
    import _common
    safe_id = manager_id
    path = _common.manager_path(safe_id)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def compare_managers(manager_ids: List[str]) -> Dict[str, Any]:
    """对比多个基金经理。

    Args:
        manager_ids: 经理 ID 列表（2-4 个）

    Returns:
        dict: 包含每个经理的画像 + 对比总结
    """
    if not 2 <= len(manager_ids) <= 4:
        return {
            "available": False,
            "reason": f"对比需要 2-4 个经理，当前 {len(manager_ids)} 个",
        }

    managers = {}
    missing = []
    for mid in manager_ids:
        data = _load_manager_data(mid)
        if data is None:
            missing.append(mid)
            continue
        managers[mid] = data

    if not managers:
        return {
            "available": False,
            "reason": f"所有经理数据缺失：{missing}",
        }

    # 提取每个经理的关键指标
    profiles = {}
    for mid, data in managers.items():
        profiles[mid] = {
            "name": data.get("name", mid),
            "company": data.get("company", ""),
            "type": data.get("manager_type", "公募"),
            "scale": data.get("scale", "N/A"),
            "tenure_return": data.get("tenure_return", "N/A"),
            "fund_count": data.get("fund_count", 0),
            "status": data.get("status", "active"),
            "last_refresh": data.get("last_refresh", ""),
            "performance": data.get("performance", {}),
            "holdings": data.get("holdings", []),
            "style_dna": data.get("style_dna", {}),
        }

    # 业绩对比
    performance_comparison = _compare_performance(profiles)
    # 重仓股重叠
    holdings_overlap = _compare_holdings(profiles)
    # 风格 DNA 对比
    style_comparison = _compare_style(profiles)

    # 生成总结
    summary = _generate_summary(profiles, performance_comparison, holdings_overlap, style_comparison)

    return {
        "available": True,
        "manager_count": len(managers),
        "missing_ids": missing,
        "profiles": profiles,
        "performance_comparison": performance_comparison,
        "holdings_overlap": holdings_overlap,
        "style_comparison": style_comparison,
        "summary": summary,
        "compared_at": datetime.now().isoformat(timespec="seconds"),
    }


def _compare_performance(profiles: Dict) -> Dict:
    """对比业绩数据。"""
    periods = ["1m", "3m", "6m", "1y", "3y", "ytd"]
    comparison = {}

    for period in periods:
        comparison[period] = {}
        values = []
        for mid, prof in profiles.items():
            perf = prof.get("performance", {}) or {}
            val = perf.get(period)
            if val is not None:
                try:
                    num = float(str(val).replace("%", ""))
                    comparison[period][mid] = val
                    values.append((mid, num))
                except (ValueError, TypeError):
                    comparison[period][mid] = "N/A"
            else:
                comparison[period][mid] = "N/A"

        if values:
            best = max(values, key=lambda x: x[1])
            worst = min(values, key=lambda x: x[1])
            comparison[period]["_best"] = best[0]
            comparison[period]["_worst"] = worst[0]
        else:
            comparison[period]["_best"] = None
            comparison[period]["_worst"] = None

    return comparison


def _compare_holdings(profiles: Dict) -> Dict:
    """分析重仓股重叠。"""
    all_holdings = {}  # stock_code → [(manager_id, weight)]

    for mid, prof in profiles.items():
        holdings = prof.get("holdings", []) or []
        for h in holdings:
            if isinstance(h, dict):
                code = h.get("code") or h.get("stock_code") or h.get("name")
                weight = h.get("weight") or h.get("ratio") or 0
            elif isinstance(h, (list, tuple)) and len(h) >= 2:
                code, weight = h[0], h[1]
            else:
                continue

            if code:
                if code not in all_holdings:
                    all_holdings[code] = []
                all_holdings[code].append((mid, weight))

    overlap = {code: holders for code, holders in all_holdings.items() if len(holders) >= 2}
    only_each = {code: holders for code, holders in all_holdings.items() if len(holders) == 1}

    return {
        "total_unique_stocks": len(all_holdings),
        "overlap_count": len(overlap),
        "overlap_stocks": {
            code: [{"manager_id": mid, "weight": w} for mid, w in holders]
            for code, holders in sorted(overlap.items(), key=lambda x: -len(x[1]))[:10]
        },
        "common_consensus": len(overlap) > 0,
    }


def _compare_style(profiles: Dict) -> Dict:
    """对比投资风格 DNA。"""
    comparison = {}
    style_keys = ["concentration", "industry_preference", "market_cap_pref", "turnover"]

    for key in style_keys:
        comparison[key] = {}
        for mid, prof in profiles.items():
            dna = prof.get("style_dna", {}) or {}
            val = dna.get(key)
            comparison[key][mid] = val if val is not None else "N/A"

    return comparison


def _generate_summary(profiles: Dict, perf: Dict, overlap: Dict, style: Dict) -> str:
    """生成自然语言总结。"""
    parts = []

    n = len(profiles)
    names = [p["name"] for p in profiles.values()]
    parts.append(f"对比了 {n} 位基金经理：{' / '.join(names)}")

    # 业绩亮点（取最近 1y 期）
    if "1y" in perf and perf["1y"].get("_best"):
        best = profiles[perf["1y"]["_best"]]["name"]
        parts.append(f"近 1 年业绩最佳：{best}")

    # 重仓股共识
    if overlap["overlap_count"] > 0:
        parts.append(f"重仓股共识：{overlap['overlap_count']} 只股票被 ≥2 人持有（说明投资风格相似）")
    else:
        parts.append("重仓股无共识（投资风格可能差异大）")

    return "；".join(parts)


def format_text(result: Dict) -> str:
    """格式化为可读文本。"""
    lines = ["📊 基金经理对比报告", "=" * 60]
    if not result.get("available"):
        lines.append(f"❌ {result.get('reason', '对比不可用')}")
        return "\n".join(lines)

    lines.append(f"对比 {result['manager_count']} 位经理")
    lines.append(f"缺失: {', '.join(result.get('missing_ids', [])) or '无'}")
    lines.append(f"时间: {result['compared_at']}")
    lines.append("")

    # 个人信息
    lines.append("👤 经理画像：")
    for mid, prof in result["profiles"].items():
        lines.append(
            f"  - {prof['name']} ({prof['company'] or '未填'})\n"
            f"    类型: {prof['type']} | 规模: {prof['scale']} | 任期收益: {prof['tenure_return']}\n"
            f"    产品数: {prof['fund_count']} | 状态: {prof['status']}"
        )
    lines.append("")

    # 业绩对比
    lines.append("📈 业绩对比：")
    for period, data in result["performance_comparison"].items():
        parts = [f"  {period}:"] + [f"  {prof_data}" for _, prof_data in [(k, v) for k, v in data.items() if not k.startswith("_")]]
        lines.append("    ".join(parts))
        if data.get("_best"):
            lines.append(f"    → 最佳: {data['_best']} | 最差: {data['_worst']}")
    lines.append("")

    # 重仓股
    lines.append("🏢 重仓股重叠：")
    lines.append(f"  共 {result['holdings_overlap']['total_unique_stocks']} 只不重复股票")
    lines.append(f"  其中 {result['holdings_overlap']['overlap_count']} 只被 ≥2 人持有")
    for code, holders in list(result["holdings_overlap"]["overlap_stocks"].items())[:5]:
        names = [result["profiles"][h["manager_id"]]["name"] for h in holders]
        lines.append(f"    {code} → {', '.join(names)}")
    lines.append("")

    # 总结
    lines.append("📝 总结：")
    lines.append(f"  {result['summary']}")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="基金经理对比工具（v2.0）")
    parser.add_argument("manager_ids", nargs="+", help="经理 ID（2-4 个）")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    result = compare_managers(args.manager_ids)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
