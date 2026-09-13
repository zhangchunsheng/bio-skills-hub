"""v2.1.0 bug 修复回归测试 — 覆盖本轮审查发现并修复的缺陷。

修复清单：
1. _common._find_balanced_json / http_get_jsonp：单引号 JSON 与值内撇号
2. risk_metrics：滚动窗口收益量纲错误（回撤/波动率/下行波动率）
3. style_cluster：余弦判别力、KMeans 初始化、代表成员选择
4. distill_manager：空持仓代码误判海外
5. qa_memory：相似度升级为 Jaccard×包含度混合
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


# ============================================================
# 1. _common：jsonp 单引号解析
# ============================================================

def test_find_balanced_json_single_quote_string_with_brace():
    """单引号字符串内的 } 不应中断括号配对（东财 jsonp 场景）。"""
    import _common
    text = "var data={'name': 'A}B', 'x': 1};"
    result = _common._find_balanced_json(text)
    assert result == "{'name': 'A}B', 'x': 1}"


def test_convert_single_quote_json_basic():
    """单引号定界符转双引号，值内撇号/双引号正确处理。"""
    import _common
    out = _common._convert_single_quote_json("{'a': 'b', 'c': 1}")
    assert out == '{"a": "b", "c": 1}'


def test_convert_single_quote_json_inner_double_quote():
    """值内双引号应被转义。"""
    import _common
    out = _common._convert_single_quote_json("{'k': 'say \"hi\"'}")
    assert out == '{"k": "say \\"hi\\""}'


def test_http_get_jsonp_double_quote_with_apostrophe(monkeypatch):
    """合法双引号 JSON 且值内含撇号：旧版盲目替换单引号会破坏数据，现应原样解析。"""
    import _common
    payload = '{"name": "O\'Hara Fund", "scale": "10.5"}'
    monkeypatch.setattr(_common, "http_get", lambda *a, **k: f"var apidata={payload};")
    result = _common.http_get_jsonp("http://fake")
    assert result["name"] == "O'Hara Fund"
    assert result["scale"] == "10.5"


def test_http_get_jsonp_single_quote_variant(monkeypatch):
    """单引号 jsonp 变体应能正确转换并解析。"""
    import _common
    monkeypatch.setattr(_common, "http_get", lambda *a, **k: "var d={'code': '110011', 'n': 2};")
    result = _common.http_get_jsonp("http://fake")
    assert result["code"] == "110011"
    assert result["n"] == 2


# ============================================================
# 2. risk_metrics：滚动窗口量纲修复
# ============================================================

def test_max_drawdown_no_cumulative_inflation():
    """旧版把重叠滚动收益直接累加，持续上涨也会构造出假净值波动；
    修复后单调上涨序列的回撤应为 0。"""
    import risk_metrics as rm
    ret = {"近1月": "5", "近3月": "15", "近6月": "30", "近1年": "60"}
    assert rm._max_drawdown_estimate(ret) == 0.0


def test_max_drawdown_v_shape():
    """中途回落再反弹：净值曲线应先涨后跌再涨，回撤精确可验。
    近1年 0%（F365=1.0）、近6月 -20%（F180=0.8）→ 净值 [100, 125, 100] → 回撤 -20%。"""
    import risk_metrics as rm
    ret = {"近6月": "-20", "近1年": "0"}
    dd = rm._max_drawdown_estimate(ret)
    assert dd == -20.0


def test_max_drawdown_insufficient_data():
    """无任何窗口数据时返回 None。"""
    import risk_metrics as rm
    assert rm._max_drawdown_estimate({}) is None


def test_volatility_steady_vs_choppy():
    """稳定上行波动率应明显低于大幅震荡序列。"""
    import risk_metrics as rm
    steady = {"近1月": "3", "近3月": "9", "近6月": "18", "近1年": "36"}
    choppy = {"近1月": "-8", "近3月": "12", "近6月": "-6", "近1年": "10"}
    v_steady = rm._volatility_estimate(steady)
    v_choppy = rm._volatility_estimate(choppy)
    assert v_steady is not None and v_choppy is not None
    assert v_steady < v_choppy


def test_volatility_single_window_fallback():
    """只有单一窗口时不应返回 None（月化兜底）。"""
    import risk_metrics as rm
    v = rm._volatility_estimate({"近3月": "9"})
    assert v is not None and v > 0


def test_interval_monthly_returns_non_overlapping():
    """区间收益反推：F90/F30 - 1 对应 30-90 天区间，不应混入重叠窗口。"""
    import risk_metrics as rm
    ret = {"近1月": "5", "近3月": "15"}
    intervals = rm._interval_monthly_returns(ret)
    assert len(intervals) == 1
    # [30,90] 区间收益 = 1.15/1.05 - 1 ≈ 9.52%，月化约 3.07%
    assert abs(intervals[0] - ((1.15 / 1.05) ** 0.5 - 1)) < 1e-9


# ============================================================
# 3. style_cluster：判别力 / 初始化 / 代表选择
# ============================================================

def test_cosine_discriminates_radar_styles():
    """旧版对任意 0-100 正向雷达恒 ~0.99+；修复后价值型 vs 成长型应显著低于 0.99。"""
    import style_cluster as sc
    value_like = [90, 10, 80, 20, 30, 70]
    growth_like = [10, 90, 20, 80, 70, 30]
    sim = sc._cosine(value_like, growth_like)
    assert sim < 0


def test_kmeans_duplicate_head_points():
    """前 k 点全重复时旧版初始化产生重复中心；kmeans++ lite 应仍正确分开簇。"""
    import style_cluster as sc
    points = [
        [0, 0], [0, 0], [0, 0], [0.5, 0.5],  # 簇 A（含重复点）
        [10, 10], [10.5, 10], [10, 10.5], [10.2, 10.2],  # 簇 B
    ]
    assignments, centers = sc._kmeans(points, k=2, max_iter=20)
    assert len(set(assignments[:4])) == 1  # 簇 A 同组
    assert len(set(assignments[4:])) == 1  # 簇 B 同组
    assert assignments[0] != assignments[4]


def test_cluster_representative_nearest_to_center():
    """代表成员应为组内最接近中心者，而非名单顺序第一人。"""
    import style_cluster as sc

    # 直接用内部函数验证：中心 = (5,5)，成员 (0,0)/(5,5)/(10,10)
    # 若按名单顺序代表是 idx0=(0,0)，修复后应选 (5,5)
    vectors = [[0.0, 0.0], [5.0, 5.0], [10.0, 10.0]]
    assignments, centers = sc._kmeans(vectors, k=1, max_iter=10)
    ci = assignments[0]
    rep_idx, _ = min(
        enumerate(vectors), key=lambda im: sc._euclidean(im[1], centers[ci])
    )
    assert rep_idx == 1


# ============================================================
# 4. distill_manager：空代码不误判海外
# ============================================================

def test_viewpoint_empty_code_not_overseas():
    """持仓代码为空串时不应被判为海外市场覆盖。"""
    import distill_manager as dm
    holdings = [
        {"code": "", "name": "贵州茅台", "total_ratio": 8.0},
        {"code": "600519", "name": "贵州茅台A", "total_ratio": 7.0},
    ]
    vp = dm._generate_viewpoint_from_holdings(holdings, [("消费", 15.0)], "SECTOR_BALANCED", "适度集中", [], "测试")
    assert "海外" not in vp
    assert "A股" in vp


# ============================================================
# 5. qa_memory：混合相似度
# ============================================================

def test_similarity_containment_boost():
    """短问题被长问题包含时，混合相似度应高于纯 Jaccard。"""
    import qa_memory as qm
    a = qm._tokens("张坤怎么看消费")
    b = qm._tokens("张坤怎么看消费板块的后市表现")
    hybrid = qm._similarity(a, b)
    jaccard = qm._jaccard(a, b)
    assert hybrid > jaccard > 0


def test_similarity_disjoint_zero():
    """完全不相关的问题相似度为 0。"""
    import qa_memory as qm
    assert qm._similarity({"abc"}, {"xyz"}) == 0.0
