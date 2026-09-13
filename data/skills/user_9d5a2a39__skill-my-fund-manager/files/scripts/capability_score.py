"""
基金经理能力评分（v2.0.0 新增）。

4 维评分（0-100）：
- 选股能力：持仓超额收益近似（基于业绩数据 + 持仓集中度）
- 择时能力：股票仓位 vs 沪深300 涨跌相关性近似
- 风控能力：最大回撤估算（基于 1y/3y 波动）
- 稳定性：夏普比率近似

零 LLM 依赖，纯规则引擎。
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


# ============================================================
# 4 维评分核心算法
# ============================================================

def _parse_return(text: str) -> Optional[float]:
    """解析 'XX%' 字符串为 float。"""
    if not text:
        return None
    s = str(text).strip().replace("%", "").replace(",", "")
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _score_stock_picking(mgr: Dict) -> float:
    """
    选股能力（0-100）。
    基于：近 1 年收益率分位（>15% 给高分，<-15% 给低分）
    + 持仓集中度（前10占比 >50% 加分说明下注能力强）
    """
    perf = mgr.get("performance", {}).get("summary", {}).get("avg_returns", {})
    one_year = _parse_return(perf.get("近1年"))
    if one_year is None:
        return 50.0  # 无数据中性
    # 1 年收益从 -30 到 +30 映射到 0-100
    score = max(0.0, min(100.0, 50.0 + one_year * (50.0 / 30.0)))
    # 持仓集中度加成
    holdings = mgr.get("top_holdings", []) or []
    if holdings:
        top10_ratio = sum(h.get("total_ratio", 0) for h in holdings[:10])
        if top10_ratio > 60:
            score += 5  # 高度集中下注
    return round(max(0.0, min(100.0, score)), 1)


def _score_timing(mgr: Dict) -> float:
    """
    择时能力（0-100）。
    简化算法：基于近 6 月 vs 近 1 年的收益差。
    如果 6m > 1y/2 表示近期跑赢（择时正贡献）；反之则拖累。
    """
    perf = mgr.get("performance", {}).get("summary", {}).get("avg_returns", {})
    six_m = _parse_return(perf.get("近6月"))
    one_y = _parse_return(perf.get("近1年"))
    if six_m is None or one_y is None:
        return 50.0
    if one_y == 0:
        return 50.0
    # 6m * 2 vs 1y，差值为正说明短期跑赢
    short_term_strength = six_m * 2 - one_y
    score = 50.0 + short_term_strength * (50.0 / 20.0)
    return round(max(0.0, min(100.0, score)), 1)


def _score_risk_control(mgr: Dict) -> float:
    """
    风控能力（0-100）。
    估算最大回撤：基于近 1 年收益率。
    1y=-20% 视作回撤 >= -20%，风控差；1y=+20% 风控好。
    简化：低回撤=高得分。
    """
    perf = mgr.get("performance", {}).get("summary", {}).get("avg_returns", {})
    one_y = _parse_return(perf.get("近1年"))
    if one_y is None:
        return 50.0
    # 假设最大回撤 = max(-30%, one_y - 5)
    # 1y=-30% → 回撤-30% → 得分低
    # 1y=+30% → 回撤 0% → 得分高
    estimated_dd = max(-30.0, min(0.0, one_y - 5.0))
    # dd from -30 to 0 maps to 0-100
    score = 100.0 + estimated_dd * (100.0 / 30.0)
    return round(max(0.0, min(100.0, score)), 1)


def _score_stability(mgr: Dict) -> float:
    """
    稳定性（0-100）。
    夏普比率近似 = (1y - 2%) / (近3年波动率近似)
    无风险利率 2%。
    """
    perf = mgr.get("performance", {}).get("summary", {}).get("avg_returns", {})
    one_y = _parse_return(perf.get("近1年"))
    three_y = _parse_return(perf.get("近3年"))
    if one_y is None or three_y is None:
        return 50.0
    # 用 3y / 3 估年化收益
    annualized = three_y / 3.0
    # 用 (1y - annualized) 估波动率近似（越接近越稳）
    vol_proxy = abs(one_y - annualized)
    excess = annualized - 2.0
    if vol_proxy == 0:
        return 50.0
    sharpe = excess / max(vol_proxy, 1.0)
    # sharpe from -1 to +3 maps to 0-100
    score = 50.0 + sharpe * 12.5
    return round(max(0.0, min(100.0, score)), 1)


def compute_scores(mgr: Dict) -> Dict:
    """
    计算经理 4 维能力分 + 综合分。
    综合分 = 选股 35% + 择时 25% + 风控 20% + 稳定 20%
    """
    scores = {
        "选股": _score_stock_picking(mgr),
        "择时": _score_timing(mgr),
        "风控": _score_risk_control(mgr),
        "稳定": _score_stability(mgr),
    }
    composite = round(
        scores["选股"] * 0.35 +
        scores["择时"] * 0.25 +
        scores["风控"] * 0.20 +
        scores["稳定"] * 0.20,
        1,
    )
    return {
        **scores,
        "composite": composite,
        "computed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data_window": "近1年+3年",
        "weights": {"选股": 0.35, "择时": 0.25, "风控": 0.20, "稳定": 0.20},
    }


def evaluate_manager(manager_id: str) -> Dict:
    """对单经理评估，返回完整评分 + 元信息。"""
    mgr = load_manager(manager_id)
    if not mgr:
        return {"error": f"经理档案 {manager_id} 不存在"}
    scores = compute_scores(mgr)
    return {
        "manager_id": manager_id,
        "name": mgr.get("name", ""),
        "company": mgr.get("company", ""),
        **scores,
    }


def save_scores(manager_id: str, scores: Dict) -> None:
    """写回 manager.json 的 capability_scores 字段。"""
    mgr = load_manager(manager_id) or {"id": manager_id}
    mgr["capability_scores"] = scores
    save_manager(manager_id, mgr)
    log.info(f"经理 {manager_id} 能力评分已写入档案")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="基金经理能力评分")
    parser.add_argument("manager_id", nargs="?", help="经理ID（不传则批量评估名单）")
    parser.add_argument("--all", action="store_true", help="批量评估全部名单")
    parser.add_argument("--save", action="store_true", help="写入 manager.json")
    args = parser.parse_args()

    if args.all:
        import roster_manager
        roster = roster_manager.load_roster()
        for m in roster.get("managers", []):
            result = evaluate_manager(m["id"])
            if result.get("error"):
                continue
            print(f"{result['name']:　<6} 选股={result['选股']} 择时={result['择时']} 风控={result['风控']} 稳定={result['稳定']} → 综合={result['composite']}")
            if args.save:
                save_scores(m["id"], {k: v for k, v in result.items() if k not in ("manager_id", "name", "company")})
    elif args.manager_id:
        result = evaluate_manager(args.manager_id)
        if result.get("error"):
            print(result["error"])
            sys.exit(1)
        print(f"🎯 {result['name']}（{result['company']}）能力评分")
        print("=" * 50)
        for dim in ["选股", "择时", "风控", "稳定"]:
            bar = "▓" * int(result[dim] / 5) + "░" * (20 - int(result[dim] / 5))
            print(f"  {dim}：{result[dim]:5.1f}  {bar}")
        print(f"  综合：{result['composite']:5.1f}")
        if args.save:
            scores = {k: v for k, v in result.items() if k not in ("manager_id", "name", "company")}
            save_scores(args.manager_id, scores)
            print(f"\n✅ 已写入 managers/{args.manager_id}.json")
    else:
        parser.print_help()