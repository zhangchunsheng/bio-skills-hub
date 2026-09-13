"""风险指标测试（v2.0.0）— 6 个用例。"""
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


def test_max_drawdown_basic():
    """最大回撤估算。"""
    import risk_metrics as rm
    # 适中下跌 → 回撤 = 累计跌幅（限幅 -50%）
    returns = {"近1月": "-2", "近3月": "-5", "近6月": "-8", "近1年": "-12"}
    dd = rm._max_drawdown_estimate(returns)
    assert dd is not None
    assert dd < 0  # 负数表示回撤
    assert -50 < dd <= 0


def test_max_drawdown_recovery():
    """先跌后涨 → 回撤幅度小于累计跌幅。"""
    import risk_metrics as rm
    returns = {"近1月": "10", "近3月": "-15", "近6月": "-20", "近1年": "5"}
    dd = rm._max_drawdown_estimate(returns)
    assert dd is not None
    assert dd <= -15  # 最大回撤至少 -15%


def test_volatility_estimate_basic():
    """波动率估算（年化）。"""
    import risk_metrics as rm
    returns = {"近1月": "5", "近3月": "-3", "近6月": "8"}
    vol = rm._volatility_estimate(returns)
    assert vol is not None
    assert vol > 0


def test_downside_volatility_only_negative():
    """下行波动率只算负区间月化收益（v2.1：由滚动收益反推不重叠区间）。"""
    import risk_metrics as rm
    # 单调向上的正收益序列 → 所有区间收益为正 → 下行=0
    assert rm._downside_volatility({"近1月": "5", "近3月": "15", "近6月": "30"}) == 0.0
    # 近 30-90 天区间下跌（1.08/0.95-1… 用 F30=0.95, F90=0.90 构造负区间）→ 应>0
    assert rm._downside_volatility({"近1月": "-5", "近3月": "-10", "近6月": "8"}) > 0


def test_compute_risk_metrics_with_full_data():
    """完整数据应算出所有指标。"""
    import risk_metrics as rm
    mgr = {
        "performance": {"summary": {"avg_returns": {
            "近1月": "3", "近3月": "-5", "近6月": "10", "近1年": "15", "近3年": "30",
        }}},
    }
    metrics = rm.compute_risk_metrics(mgr)
    assert metrics["max_drawdown_pct"] is not None
    assert metrics["annual_volatility_pct"] > 0
    assert "sharpe_ratio" in metrics
    assert "calmar_ratio" in metrics
    assert "risk_level" in metrics


def test_save_risk_metrics_writes_to_manager():
    """save_risk_metrics 应写到 manager.json 的 risk_metrics 字段。"""
    import risk_metrics as rm

    with _DirIsolation():
        import _common
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试",
            "performance": {"summary": {"avg_returns": {"近1年": "10.0", "近6月": "5.0"}}},
        })
        result = rm.evaluate_manager("m1")
        metrics = {k: v for k, v in result.items() if k not in ("manager_id", "name")}
        rm.save_risk_metrics("m1", metrics)
        saved = _common.load_manager("m1")
    assert "risk_metrics" in saved
    assert saved["risk_metrics"]["max_drawdown_pct"] is not None