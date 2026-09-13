"""
业绩归因（v2.0.0 新增，简化 Brinson 模型）。

把近 1 年业绩拆解为：
- 行业暴露贡献：经理行业权重偏离基准带来的收益差
- 选股超额贡献：行业内选股超额收益
- 择时贡献：股票总仓位变动 × 市场涨跌

简化假设（规则引擎局限）：
- 行业基准收益用沪深 300 各行业指数近似（按 INDUSTRY_KEYWORDS 命中权重）
- 单只个股基准 = 经理该股所在行业的平均收益近似
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import _common
from _common import load_manager, save_manager, log

# 复用 distill_manager 的行业字典
import distill_manager
INDUSTRY_KEYWORDS = distill_manager.INDUSTRY_KEYWORDS

# 简化基准：每个行业假设平均年化收益率（基于2024-2025 历史近似）
# 实际应用应接 Wind/Choice 数据；这里给规则引擎兜底
INDUSTRY_BENCHMARK = {
    "科技": 8.0,
    "消费": 5.0,
    "金融": 3.0,
    "能源": 4.0,
    "医药": -2.0,
    "制造": 6.0,
    "其他": 2.0,
}

# 沪深 300 基准年化收益近似
BENCHMARK_RETURN_1Y = 3.0


def _detect_industry(stock_name: str) -> str:
    """根据股票名识别行业。"""
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        for kw in keywords:
            if kw in stock_name:
                return industry
    return "其他"


def _parse_return(text) -> Optional[float]:
    if text is None:
        return None
    s = str(text).strip().replace("%", "").replace(",", "")
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def attribute_performance(mgr: Dict) -> Dict:
    """
    简化 Brinson 归因。

    输入：经理档案（需 top_holdings + performance）
    输出：归因拆解 dict
    """
    holdings = mgr.get("top_holdings", []) or []
    perf = mgr.get("performance", {}).get("summary", {}).get("avg_returns", {})
    total_return = _parse_return(perf.get("近1年"))
    if total_return is None:
        return {
            "total_return": 0.0,
            "industry_exposure": 0.0,
            "stock_selection": 0.0,
            "timing": 0.0,
            "summary": "无业绩数据，跳过归因",
            "computed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    # 1. 行业暴露贡献：经理行业权重 - 基准权重（20%平均）× 行业基准收益
    industry_weights = {}  # industry -> manager weight %
    for h in holdings:
        ind = _detect_industry(h.get("name", ""))
        ratio = h.get("total_ratio", 0) or 0
        industry_weights[ind] = industry_weights.get(ind, 0) + ratio

    industry_exposure = 0.0
    for ind, w in industry_weights.items():
        bench_w = 20.0  # 简化：6 行业平均基准权重 20%
        bench_r = INDUSTRY_BENCHMARK.get(ind, INDUSTRY_BENCHMARK["其他"])
        industry_exposure += (w - bench_w) / 100.0 * bench_r

    # 2. 选股超额：Σ 经理个股权重 × (个股收益 - 行业收益)
    # 简化：假设每只个股收益 = 行业基准 + 经理"超额"（用持仓占比变化率近似）
    stock_selection = 0.0
    for h in holdings:
        ratio = h.get("total_ratio", 0) or 0
        ind = _detect_industry(h.get("name", ""))
        ind_r = INDUSTRY_BENCHMARK.get(ind, INDUSTRY_BENCHMARK["其他"])
        # 简化：超额 = ratio * (total_return - ind_r) * 0.1 （粗略）
        excess = total_return - ind_r
        stock_selection += (ratio / 100.0) * excess * 0.1

    # 3. 择时贡献 = 总仓位 × (沪深300 收益) - 经理相对市场的偏离
    # 简化：假设股票仓位 80%（保守），择时贡献 = 0.8 * (total_return - BENCHMARK)
    stock_pos = 80.0  # 默认仓位假设
    timing = (stock_pos / 100.0) * (total_return - BENCHMARK_RETURN_1Y)

    # 归一化使三者之和接近 total_return（容差范围内）
    raw_total = industry_exposure + stock_selection + timing
    if raw_total != 0:
        scale = total_return / raw_total
        # 但保留符号，只缩放幅度
        if raw_total * total_return > 0:  # 同号才缩放
            industry_exposure *= abs(scale)
            stock_selection *= abs(scale)
            timing *= abs(scale)

    # 总结
    parts = []
    biggest = max(
        [("行业暴露", industry_exposure), ("选股超额", stock_selection), ("择时", timing)],
        key=lambda x: abs(x[1]),
    )
    parts.append(f"本期收益 {total_return:+.1f}%，最大贡献来自「{biggest[0]}」({biggest[1]:+.1f}%)")
    if stock_selection < -5:
        parts.append("选股贡献明显为负，自下而上失误")
    elif stock_selection > 5:
        parts.append("选股贡献明显为正，挖掘能力突出")
    if industry_exposure > 3:
        parts.append("行业偏离基准较多，行业β贡献正")
    elif industry_exposure < -3:
        parts.append("行业偏离拖累整体收益")

    return {
        "total_return": round(total_return, 2),
        "industry_exposure": round(industry_exposure, 2),
        "stock_selection": round(stock_selection, 2),
        "timing": round(timing, 2),
        "summary": "；".join(parts),
        "computed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "method": "simplified_brinson_v1",
    }


def evaluate_manager(manager_id: str) -> Dict:
    mgr = load_manager(manager_id)
    if not mgr:
        return {"error": f"经理档案 {manager_id} 不存在"}
    attr = attribute_performance(mgr)
    return {
        "manager_id": manager_id,
        "name": mgr.get("name", ""),
        **attr,
    }


def save_attribution(manager_id: str, attr: Dict) -> None:
    mgr = load_manager(manager_id) or {"id": manager_id}
    mgr["attribution"] = attr
    save_manager(manager_id, mgr)
    log.info(f"经理 {manager_id} 业绩归因已写入档案")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="业绩归因（简化 Brinson）")
    parser.add_argument("manager_id")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    result = evaluate_manager(args.manager_id)
    if result.get("error"):
        print(result["error"])
        sys.exit(1)

    print(f"📊 {result['name']} 业绩归因（近1年）")
    print("=" * 50)
    print(f"  总收益：{result['total_return']:+.2f}%")
    print(f"  行业暴露贡献：{result['industry_exposure']:+.2f}%")
    print(f"  选股超额贡献：{result['stock_selection']:+.2f}%")
    print(f"  择时贡献：{result['timing']:+.2f}%")
    print(f"\n  总结：{result['summary']}")

    if args.save:
        attr = {k: v for k, v in result.items() if k not in ("manager_id", "name")}
        save_attribution(args.manager_id, attr)
        print(f"\n✅ 已写入 managers/{args.manager_id}.json")