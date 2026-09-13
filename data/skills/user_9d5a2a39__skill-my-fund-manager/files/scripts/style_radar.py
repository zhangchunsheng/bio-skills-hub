"""
基金经理 6 维风格雷达（v2.0.0 新增）。

维度：价值vs成长 / 大盘vs中小盘 / 高动量vs低动量 / 质量 / 集中度 / 换手率
借鉴 wechat-analyzer.text_analyzer._analyze_big_five 关键词字典 + 计数模式。

零 LLM 依赖。
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Dict, List

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import _common
from _common import load_manager, save_manager, log


# 关键词字典
VALUE_KW = {"估值", "低估值", "价值", "安全边际", "现金流", "分红", "股息", "PB", "PE"}
GROWTH_KW = {"成长", "增速", "赛道", "创新", "渗透率", "景气", "增长", "空间"}
QUALITY_KW = {"ROE", "护城河", "龙头", "盈利", "毛利率", "净利率", "质量", "优秀"}
MOMENTUM_HIGH_KW = {"趋势", "突破", "加速", "上涨", "强势", "高弹性"}
MOMENTUM_LOW_KW = {"低波动", "防御", "稳健", "抗跌"}


def _count(text: str, keywords: set) -> int:
    if not text:
        return 0
    return sum(text.count(kw) for kw in keywords)


def _value_growth_score(mgr: Dict) -> Dict:
    """价值/成长倾向（0-100 + 50 = 平衡分）。"""
    text = " ".join(mgr.get("strategy_texts", []) or [])
    v = _count(text, VALUE_KW)
    g = _count(text, GROWTH_KW)
    total = v + g
    if total == 0:
        # 默认基于持仓判断（用行业偏好近似）
        ip = mgr.get("industry_preference", []) or []
        if any(i in ("消费", "金融", "能源") for i in ip):
            return {"value": 65, "growth": 35}
        return {"value": 50, "growth": 50}
    value_pct = round(v / total * 100, 1)
    growth_pct = round(g / total * 100, 1)
    return {"value": value_pct, "growth": growth_pct}


def _market_cap_score(mgr: Dict) -> Dict:
    """大盘/中小盘倾向。"""
    holdings = mgr.get("top_holdings", []) or []
    if not holdings:
        return {"large": 50, "mid": 50}
    # 简化：用股票代码前缀判断（6 开头沪市大盘，0/3 开头深市，8/4 开头北交所中小）
    large = 0
    mid = 0
    total_ratio = 0
    for h in holdings:
        code = h.get("code", "") or ""
        ratio = h.get("total_ratio", 0) or 0
        total_ratio += ratio
        if not code:
            continue
        # 简化启发式：A 股 6 开头 + 港股（5位）= 大盘；0/3 开头 = 中盘
        if code.startswith("6") or (len(code) == 5 and not code.startswith("8")):
            large += ratio
        elif code.startswith("0") or code.startswith("3"):
            mid += ratio
    if total_ratio == 0:
        return {"large": 50, "mid": 50}
    return {
        "large": round(large / total_ratio * 100, 1),
        "mid": round(mid / total_ratio * 100, 1),
    }


def _momentum_score(mgr: Dict) -> Dict:
    """高动量/低动量倾向。"""
    text = " ".join(mgr.get("strategy_texts", []) or [])
    high = _count(text, MOMENTUM_HIGH_KW)
    low = _count(text, MOMENTUM_LOW_KW)
    total = high + low
    if total == 0:
        return {"high": 40, "low": 60}  # 默认偏防御
    return {
        "high": round(high / total * 100, 1),
        "low": round(low / total * 100, 1),
    }


def _quality_score(mgr: Dict) -> Dict:
    """质量偏好（高/低，0-100）。"""
    text = " ".join(mgr.get("strategy_texts", []) or [])
    q = _count(text, QUALITY_KW)
    # 0 命中 → 50/50 中性
    if q == 0:
        return {"high": 50, "low": 50}
    # 关键词命中数 / 10 → 倾向高分（封顶 90）
    score = min(90, 50 + q * 8)
    return {"high": score, "low": 100 - score}


def _concentration_score(mgr: Dict) -> Dict:
    """持仓集中度（前10 大占比 → 高/低）。"""
    holdings = mgr.get("top_holdings", []) or []
    if not holdings:
        return {"high": 50, "low": 50}
    top10 = sum(h.get("total_ratio", 0) for h in holdings[:10])
    # top10 > 60% → 高集中
    if top10 > 60:
        score = 80
    elif top10 > 40:
        score = 60
    elif top10 > 20:
        score = 40
    else:
        score = 20
    return {"high": score, "low": 100 - score}


def _turnover_score(mgr: Dict) -> Dict:
    """
    换手率倾向。
    规则引擎无换手率数据，用 style_code 推断 + 持仓更新频率近似。
    """
    style_code = mgr.get("style_code", "") or ""
    if "LOW_TURNOVER" in style_code:
        return {"high": 20, "low": 80}
    if "HIGH_TURNOVER" in style_code:
        return {"high": 80, "low": 20}
    if "MED_TURNOVER" in style_code:
        return {"high": 50, "low": 50}
    return {"high": 40, "low": 60}  # 默认偏长期


def compute_radar(mgr: Dict) -> Dict:
    """计算 6 维风格雷达。"""
    radar = {
        "value_growth": _value_growth_score(mgr),
        "market_cap": _market_cap_score(mgr),
        "momentum": _momentum_score(mgr),
        "quality": _quality_score(mgr),
        "concentration": _concentration_score(mgr),
        "turnover": _turnover_score(mgr),
        "computed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    return radar


def render_ascii_radar(radar: Dict, name: str = "", width: int = 30) -> str:
    """6 维 ASCII 雷达图（条形图组合）。"""
    lines = [f"📊 {name} 风格雷达", "=" * (width + 20)]
    # 维度列表
    dims = [
        ("价值/成长", radar["value_growth"], ("价值", "成长")),
        ("大盘/中小盘", radar["market_cap"], ("大盘", "中小盘")),
        ("动量", radar["momentum"], ("高动量", "低动量")),
        ("质量", radar["quality"], ("高质量", "低质量")),
        ("集中度", radar["concentration"], ("高集中", "低集中")),
        ("换手率", radar["turnover"], ("高换手", "低换手")),
    ]
    for label, scores, (left, right) in dims:
        # 简化：用第一个 key 作 left，第二个作 right
        keys = list(scores.keys())
        left_val = scores[keys[0]]
        right_val = scores[keys[1]]
        left_bar = "▓" * int(left_val / 100 * 12)
        right_bar = "░" * int(right_val / 100 * 12)
        lines.append(f"  {label:　<10}  {keys[0]:　<6} {left_bar:<12} {left_val:5.1f}%  |  {right_val:5.1f}% {right_bar:<12} {keys[1]}")
    return "\n".join(lines)


def evaluate_manager(manager_id: str) -> Dict:
    mgr = load_manager(manager_id)
    if not mgr:
        return {"error": f"经理档案 {manager_id} 不存在"}
    radar = compute_radar(mgr)
    return {
        "manager_id": manager_id,
        "name": mgr.get("name", ""),
        "style_radar": radar,
    }


def save_radar(manager_id: str, radar: Dict) -> None:
    mgr = load_manager(manager_id) or {"id": manager_id}
    mgr["style_radar"] = radar
    save_manager(manager_id, mgr)
    log.info(f"经理 {manager_id} 风格雷达已写入档案")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="经理风格雷达")
    parser.add_argument("manager_id")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--no-render", action="store_true", help="只输出 JSON 不渲染雷达")
    args = parser.parse_args()

    result = evaluate_manager(args.manager_id)
    if result.get("error"):
        print(result["error"])
        sys.exit(1)

    if not args.no_render:
        print(render_ascii_radar(result["style_radar"], result["name"]))
        print()

    if args.save:
        save_radar(args.manager_id, result["style_radar"])
        print(f"✅ 已写入 managers/{args.manager_id}.json")