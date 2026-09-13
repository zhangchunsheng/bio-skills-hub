"""风格漂移测试（v2.0.0）— 6 个用例。"""
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


def test_flatten_radar_length():
    """_flatten_radar 应展开成 12 维向量。"""
    import style_drift as sd
    radar = {
        "value_growth": {"value": 70, "growth": 30},
        "market_cap": {"large": 80, "mid": 20},
        "momentum": {"high": 30, "low": 70},
        "quality": {"high": 80, "low": 20},
        "concentration": {"high": 70, "low": 30},
        "turnover": {"high": 20, "low": 80},
    }
    vec = sd._flatten_radar(radar)
    assert len(vec) == 12


def test_euclidean_distance_zero_for_identical():
    """相同向量欧式距离 = 0。"""
    import style_drift as sd
    v = [1, 2, 3, 4]
    assert sd._euclidean(v, v) == 0.0


def test_record_style_creates_jsonl():
    """record_style 应追加一行到 JSONL。"""
    import style_drift as sd

    with _DirIsolation():
        sd.record_style("m1", {"value_growth": {"value": 70, "growth": 30}})
        import _common
        path = os.path.join(_common.DATA_DIR, "style_history", "m1.jsonl")
        assert os.path.exists(path)
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    assert len(lines) == 1


def test_get_history_returns_recent_first():
    """get_history 应返回最近 N 期。"""
    import style_drift as sd

    with _DirIsolation():
        sd.record_style("m1", {"value_growth": {"value": 50, "growth": 50}})
        sd.record_style("m1", {"value_growth": {"value": 70, "growth": 30}})
        history = sd.get_history("m1", limit=2)
    assert len(history) == 2


def test_detect_drift_when_style_changes():
    """风格从平衡(50/50)→价值(90/10)应检出漂移。"""
    import style_drift as sd

    with _DirIsolation():
        sd.record_style("m1", {
            "value_growth": {"value": 50, "growth": 50},
            "market_cap": {"large": 50, "mid": 50},
            "momentum": {"high": 50, "low": 50},
            "quality": {"high": 50, "low": 50},
            "concentration": {"high": 50, "low": 50},
            "turnover": {"high": 50, "low": 50},
        })
        sd.record_style("m1", {
            "value_growth": {"value": 90, "growth": 10},
            "market_cap": {"large": 90, "mid": 10},
            "momentum": {"high": 90, "low": 10},
            "quality": {"high": 90, "low": 10},
            "concentration": {"high": 90, "low": 10},
            "turnover": {"high": 10, "low": 90},
        })
        drift = sd.detect_drift("m1", threshold=15.0)
    assert drift is not None
    assert drift["drift_detected"] is True


def test_detect_drift_returns_none_for_stable():
    """风格稳定时返回 None。"""
    import style_drift as sd

    with _DirIsolation():
        radar = {
            "value_growth": {"value": 70, "growth": 30},
            "market_cap": {"large": 80, "mid": 20},
            "momentum": {"high": 30, "low": 70},
            "quality": {"high": 80, "low": 20},
            "concentration": {"high": 70, "low": 30},
            "turnover": {"high": 20, "low": 80},
        }
        sd.record_style("m1", radar)
        sd.record_style("m1", radar)
        drift = sd.detect_drift("m1", threshold=15.0)
    assert drift is None