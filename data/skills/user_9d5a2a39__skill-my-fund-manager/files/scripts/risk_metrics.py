"""
风险调整收益指标（v2.0.0 新增）。

- 最大回撤估算
- 夏普比率
- Calmar 比率
- 索提诺比率（用下行波动率）

数据来源：managers/{id}.json 的 performance 字段（近1月/3月/6月/1年/3年/今年来）。
无 LLM 依赖，纯数学计算。
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Dict, Optional

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import _common
from _common import load_manager, save_manager, log


RISK_FREE_RATE = 2.0  # 无风险利率（%），可后续从国库券收益率动态取


def _parse(text) -> Optional[float]:
    if text is None:
        return None
    s = str(text).strip().replace("%", "").replace(",", "")
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _window_factors(returns: Dict) -> Dict[int, float]:
    """把滚动窗口收益解析为累计增长因子 {回溯天数: 1 + r/100}。
    近1月/3月/6月/1年都以今天为终点，是重叠窗口，不能直接累加。"""
    factors = {}
    for label, days in [("近1月", 30), ("近3月", 90), ("近6月", 180), ("近1年", 365)]:
        v = _parse(returns.get(label))
        if v is not None and v > -100:
            factors[days] = 1.0 + v / 100.0
    return factors


def _interval_monthly_returns(returns: Dict) -> list:
    """由滚动收益反推不重叠区间的月化收益序列。
    区间 [t1, t2]（t1<t2 天前）的区间收益 = F_t2/F_t1 - 1，
    再按 (30/区间天数) 幂次归一到月度，避免不同窗口量纲混算。"""
    factors = _window_factors(returns)
    checkpoints = sorted(factors)  # 短→长，均为"距今天数"
    intervals = []
    for t1, t2 in zip(checkpoints, checkpoints[1:]):
        ret = factors[t2] / factors[t1] - 1.0
        span_days = t2 - t1
        monthly = (1.0 + ret) ** (30.0 / span_days) - 1.0 if span_days > 0 else ret
        intervals.append(monthly)
    # 若只拿到单一窗口（如仅近1月），直接月化兜底，保证至少 1 个样本
    if not intervals and checkpoints:
        t = checkpoints[-1]
        intervals.append(factors[t] ** (30.0 / t) - 1.0)
    return intervals


def _max_drawdown_estimate(returns: Dict) -> Optional[float]:
    """
    简化最大回撤估算。
    v2.1 修复：近1月/3月/6月/1年是重叠滚动窗口，不能直接累加构造净值。
    改为由累计因子反推各检查点净值：以最长窗口起点为 100，
    NAV(-t) = 100 * F_long / F_t（F_t 为距今 t 天的累计增长因子）。
    检查点稀疏，真实回撤可能更深，结果仅作估算。

    返回值：负数（如 -15.3 表示最大回撤 15.3%），None 表示无法估算。
    限制：估算范围 [-50%, 0%]，避免过于悲观。
    """
    factors = _window_factors(returns)
    checkpoints = sorted(factors)
    if not checkpoints:
        return None

    # 构造净值序列（时间正序：最长窗口起点 → 今天）
    long_t = checkpoints[-1]
    f_long = factors[long_t]
    nav_series = [100.0]
    for t in reversed(checkpoints[:-1]):
        nav_series.append(100.0 * f_long / factors[t])
    nav_series.append(100.0 * f_long)
    if len(nav_series) < 2:
        return None

    # 算最大回撤
    peak = nav_series[0]
    max_dd = 0.0
    for nav in nav_series:
        peak = max(peak, nav)
        dd = (nav - peak) / peak * 100.0  # 负数
        max_dd = min(max_dd, dd)
    return round(max(-50.0, max_dd), 2)


def _volatility_estimate(returns: Dict) -> Optional[float]:
    """
    波动率近似（年化%）。
    v2.1 修复：不再把近1月/3月/6月 重叠窗口收益混作同维样本算标准差，
    改为反推不重叠区间的月化收益序列，再标准差×√12 年化。
    """
    intervals = _interval_monthly_returns(returns)
    if not intervals:
        return None
    if len(intervals) == 1:
        # 单样本：用绝对幅度作波动率近似（避免标准差恒 0）
        return round(abs(intervals[0]) * (12 ** 0.5), 2)
    mean = sum(intervals) / len(intervals)
    var = sum((v - mean) ** 2 for v in intervals) / len(intervals)
    std = var ** 0.5
    return round(std * (12 ** 0.5), 2)


def _downside_volatility(returns: Dict) -> Optional[float]:
    """下行波动率（仅算负月化收益的标准差，年化）。v2.1 同步改用区间月化收益。"""
    intervals = _interval_monthly_returns(returns)
    negatives = [v for v in intervals if v < 0]
    if not negatives:
        return 0.0
    if len(negatives) == 1:
        # 单个负样本：取其绝对值作为下行风险近似（×√12 年化）
        return round(abs(negatives[0]) * (12 ** 0.5), 2)
    mean = sum(negatives) / len(negatives)
    var = sum((v - mean) ** 2 for v in negatives) / len(negatives)
    std = var ** 0.5
    return round(std * (12 ** 0.5), 2)


def compute_risk_metrics(mgr: Dict) -> Dict:
    perf = mgr.get("performance", {}).get("summary", {}).get("avg_returns", {})
    one_y = _parse(perf.get("近1年"))

    max_dd = _max_drawdown_estimate(perf)
    vol = _volatility_estimate(perf)
    downside_vol = _downside_volatility(perf)

    metrics = {
        "max_drawdown_pct": max_dd,
        "annual_volatility_pct": vol,
        "downside_volatility_pct": downside_vol,
        "computed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    # 夏普 = (年化收益 - 无风险利率) / 年化波动率
    if one_y is not None and vol and vol > 0:
        sharpe = round((one_y - RISK_FREE_RATE) / vol, 3)
        metrics["sharpe_ratio"] = sharpe

    # Calmar = 年化收益 / |最大回撤|
    if one_y is not None and max_dd is not None and max_dd < 0:
        calmar = round(one_y / abs(max_dd), 3)
        metrics["calmar_ratio"] = calmar

    # Sortino = (年化收益 - 无风险利率) / 下行波动率
    if one_y is not None and downside_vol and downside_vol > 0:
        sortino = round((one_y - RISK_FREE_RATE) / downside_vol, 3)
        metrics["sortino_ratio"] = sortino

    # 风险等级定性
    if max_dd is None:
        metrics["risk_level"] = "未知"
    elif max_dd >= -10:
        metrics["risk_level"] = "低"
    elif max_dd >= -20:
        metrics["risk_level"] = "中"
    elif max_dd >= -30:
        metrics["risk_level"] = "高"
    else:
        metrics["risk_level"] = "极高"

    return metrics


def evaluate_manager(manager_id: str) -> Dict:
    mgr = load_manager(manager_id)
    if not mgr:
        return {"error": f"经理档案 {manager_id} 不存在"}
    metrics = compute_risk_metrics(mgr)
    return {
        "manager_id": manager_id,
        "name": mgr.get("name", ""),
        **metrics,
    }


def save_risk_metrics(manager_id: str, metrics: Dict) -> None:
    mgr = load_manager(manager_id) or {"id": manager_id}
    mgr["risk_metrics"] = metrics
    save_manager(manager_id, mgr)
    log.info(f"经理 {manager_id} 风险指标已写入档案")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="风险调整收益指标")
    parser.add_argument("manager_id")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    result = evaluate_manager(args.manager_id)
    if result.get("error"):
        print(result["error"])
        sys.exit(1)

    print(f"📉 {result['name']} 风险调整指标")
    print("=" * 50)
    print(f"  最大回撤估算：{result.get('max_drawdown_pct', 'N/A')}%")
    print(f"  年化波动率：{result.get('annual_volatility_pct', 'N/A')}%")
    print(f"  下行波动率：{result.get('downside_volatility_pct', 'N/A')}%")
    print(f"  夏普比率：{result.get('sharpe_ratio', 'N/A')}")
    print(f"  Calmar 比率：{result.get('calmar_ratio', 'N/A')}")
    print(f"  Sortino 比率：{result.get('sortino_ratio', 'N/A')}")
    print(f"  风险等级：{result.get('risk_level', 'N/A')}")

    if args.save:
        metrics = {k: v for k, v in result.items() if k not in ("manager_id", "name")}
        save_risk_metrics(args.manager_id, metrics)
        print(f"\n✅ 已写入 managers/{args.manager_id}.json")