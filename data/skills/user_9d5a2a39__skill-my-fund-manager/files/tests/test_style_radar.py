"""风格雷达测试（v2.0.0）— 8 个用例。"""
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


def test_value_growth_extreme_value():
    """策略文本全关键词价值 → 价值分高。"""
    import style_radar as sr
    mgr = {"strategy_texts": ["估值低估值价值安全边际现金流分红股息PBPE"]}
    score = sr._value_growth_score(mgr)
    assert score["value"] >= 90
    assert score["growth"] <= 10


def test_value_growth_extreme_growth():
    """策略文本全关键词成长。"""
    import style_radar as sr
    mgr = {"strategy_texts": ["成长增速赛道创新渗透率景气增长空间"]}
    score = sr._value_growth_score(mgr)
    assert score["growth"] >= 90


def test_market_cap_basic():
    """持仓代码前缀判断大盘vs中小盘。"""
    import style_radar as sr
    holdings = [
        {"code": "600519", "total_ratio": 10.0},  # 6开头 → 大盘
        {"code": "000858", "total_ratio": 8.0},   # 0开头 → 中盘
        {"code": "300750", "total_ratio": 5.0},   # 3开头 → 中盘
    ]
    mgr = {"top_holdings": holdings}
    score = sr._market_cap_score(mgr)
    # large=10, mid=13, total=23 → large=43.5, mid=56.5
    assert 40 < score["large"] < 50
    assert 50 < score["mid"] < 60


def test_concentration_high():
    """前10>60% → 高集中。"""
    import style_radar as sr
    holdings = [{"total_ratio": 7.0}] * 10  # 合计70%
    mgr = {"top_holdings": holdings}
    score = sr._concentration_score(mgr)
    assert score["high"] >= 70


def test_turnover_from_style_code():
    """LOW_TURNOVER → 低换手。"""
    import style_radar as sr
    mgr = {"style_code": "GROWTH-MED_POS-SECTOR_CONCENTRATED-LOW_TURNOVER-HK_STOCK"}
    score = sr._turnover_score(mgr)
    assert score["low"] >= 70


def test_compute_radar_returns_6_dims():
    """compute_radar 应返回 6 维 + computed_at。"""
    import style_radar as sr
    mgr = {
        "strategy_texts": ["估值低估值价值ROE质量"],
        "top_holdings": [{"code": "600519", "total_ratio": 8.0}] * 5,
        "style_code": "VALUE-HIGH_POS-SECTOR_CONCENTRATED-LOW_TURNOVER-A_SHARE",
        "industry_preference": ["消费", "金融"],
    }
    radar = sr.compute_radar(mgr)
    assert "value_growth" in radar
    assert "market_cap" in radar
    assert "momentum" in radar
    assert "quality" in radar
    assert "concentration" in radar
    assert "turnover" in radar
    assert "computed_at" in radar


def test_render_ascii_radar():
    """render_ascii_radar 应生成文本。"""
    import style_radar as sr
    radar = {
        "value_growth": {"value": 70, "growth": 30},
        "market_cap": {"large": 80, "mid": 20},
        "momentum": {"high": 30, "low": 70},
        "quality": {"high": 80, "low": 20},
        "concentration": {"high": 70, "low": 30},
        "turnover": {"high": 20, "low": 80},
    }
    text = sr.render_ascii_radar(radar, "测试经理")
    assert "测试经理" in text
    assert "价值/成长" in text
    assert "集中度" in text


def test_save_radar_writes_to_manager():
    """save_radar 应写到 manager.json。"""
    import style_radar as sr

    with _DirIsolation():
        import _common
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试", "strategy_texts": ["价值估值"],
            "top_holdings": [{"code": "600519", "total_ratio": 10.0}],
        })
        result = sr.evaluate_manager("m1")
        sr.save_radar("m1", result["style_radar"])
        saved = _common.load_manager("m1")
    assert "style_radar" in saved
    assert saved["style_radar"]["value_growth"]["value"] >= 50