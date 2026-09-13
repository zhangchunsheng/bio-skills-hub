"""能力评分测试（v2.0.0）— 8 个用例。"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class _DirIsolation:
    def __enter__(self):
        import _common
        self.original = {k: getattr(_common, k) for k in
                         ("DATA_DIR", "MANAGERS_DIR", "PROGRESS_DIR", "EXPORTS_DIR", "ROSTER_PATH")}
        self.tmp = tempfile.mkdtemp()
        _common.DATA_DIR = os.path.join(self.tmp, "data")
        _common.MANAGERS_DIR = os.path.join(_common.DATA_DIR, "managers")
        _common.PROGRESS_DIR = os.path.join(_common.DATA_DIR, "progress")
        _common.EXPORTS_DIR = os.path.join(_common.DATA_DIR, "exports")
        _common.ROSTER_PATH = os.path.join(_common.DATA_DIR, "roster.json")
        for p in (_common.MANAGERS_DIR, _common.PROGRESS_DIR, _common.EXPORTS_DIR):
            os.makedirs(p, exist_ok=True)
        return self

    def __exit__(self, *args):
        import _common
        for k, v in self.original.items():
            setattr(_common, k, v)
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)


def test_parse_return_basic():
    """解析 'XX%' 字符串。"""
    import capability_score as cs
    assert cs._parse_return("12.34%") == 12.34
    assert cs._parse_return("-5.6%") == -5.6
    assert cs._parse_return("100") == 100.0
    assert cs._parse_return("") is None
    assert cs._parse_return(None) is None


def test_score_stock_picking_high_return():
    """高收益 + 集中持仓应得高分。"""
    import capability_score as cs
    mgr = {
        "performance": {"summary": {"avg_returns": {"近1年": "30.0"}}},
        "top_holdings": [{"total_ratio": 8.0}] * 10,  # 前10合计80%
    }
    score = cs._score_stock_picking(mgr)
    assert score >= 90  # 高收益 + 集中


def test_score_stock_picking_low_return():
    """低收益应得低分。"""
    import capability_score as cs
    mgr = {
        "performance": {"summary": {"avg_returns": {"近1年": "-25.0"}}},
        "top_holdings": [],
    }
    score = cs._score_stock_picking(mgr)
    assert score <= 20


def test_score_timing_short_term_outperforms():
    """短期(6m*2 > 1y) 跑赢 → 高分。"""
    import capability_score as cs
    mgr = {
        "performance": {"summary": {"avg_returns": {"近6月": "15.0", "近1年": "10.0"}}},
    }
    score = cs._score_timing(mgr)
    # 6m*2 - 1y = 30 - 10 = 20 → 加分
    assert score >= 60


def test_score_risk_control_no_data():
    """无业绩数据时风控分中性。"""
    import capability_score as cs
    mgr = {"performance": {"summary": {"avg_returns": {}}}}
    score = cs._score_risk_control(mgr)
    assert score == 50.0


def test_score_stability_with_3y_data():
    """有 3y 数据时稳定分应非中性。"""
    import capability_score as cs
    mgr = {
        "performance": {"summary": {"avg_returns": {"近1年": "15.0", "近3年": "30.0"}}},
    }
    score = cs._score_stability(mgr)
    # annualized=10, excess=8, vol_proxy=5, sharpe=1.6 → score≈70
    assert 50 < score <= 100


def test_compute_scores_returns_all_dimensions():
    """compute_scores 应返回 4 维 + composite + weights。"""
    import capability_score as cs
    mgr = {
        "performance": {"summary": {"avg_returns": {"近1年": "10.0", "近6月": "5.0", "近3年": "20.0"}}},
        "top_holdings": [{"total_ratio": 5.0}] * 8,
    }
    result = cs.compute_scores(mgr)
    assert "选股" in result
    assert "择时" in result
    assert "风控" in result
    assert "稳定" in result
    assert "composite" in result
    assert result["composite"] > 0
    # 权重总和 1
    assert abs(sum(result["weights"].values()) - 1.0) < 0.001


def test_save_scores_writes_to_manager():
    """save_scores 应写到 manager.json 的 capability_scores 字段。"""
    import capability_score as cs

    with _DirIsolation():
        mgr = {
            "id": "m1", "name": "测试经理", "company": "X",
            "performance": {"summary": {"avg_returns": {"近1年": "10.0"}}},
        }
        import _common
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), mgr)
        result = cs.evaluate_manager("m1")
        scores = {k: v for k, v in result.items() if k not in ("manager_id", "name", "company")}
        cs.save_scores("m1", scores)
        saved = _common.load_manager("m1")
    assert "capability_scores" in saved
    assert saved["capability_scores"]["composite"] > 0