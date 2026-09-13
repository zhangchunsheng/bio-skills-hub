"""季度调仓追踪测试（v2.0.0）— 6 个用例。"""
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


def test_holdings_dict_basic():
    """_holdings_dict 应映射 code → ratio。"""
    import turnover_tracker as tt
    holdings = [
        {"code": "600519", "total_ratio": 10.0},
        {"code": "000858", "total_ratio": 8.0},
    ]
    d = tt._holdings_dict(holdings)
    assert d["600519"] == 10.0
    assert d["000858"] == 8.0


def test_snapshot_creates_jsonl():
    """snapshot 应追加一行到 JSONL。"""
    import turnover_tracker as tt

    with _DirIsolation():
        import _common
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试",
            "top_holdings": [{"code": "600519", "total_ratio": 10.0}],
            "holdings_report_date": "2026-06-30",
        })
        tt.snapshot("m1")
        path = os.path.join(_common.DATA_DIR, "track_records", "m1.jsonl")
        assert os.path.exists(path)


def test_track_changes_first_run():
    """首次运行无上一期快照 → 返回 note。"""
    import turnover_tracker as tt

    with _DirIsolation():
        import _common
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试", "top_holdings": [],
        })
        changes = tt.track_changes("m1")
    assert "note" in changes
    assert changes["added"] == []


def test_track_changes_detects_added_removed():
    """能检出新增和退出。"""
    import turnover_tracker as tt

    with _DirIsolation():
        import _common
        # 上一期快照
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试",
            "top_holdings": [
                {"code": "600519", "total_ratio": 10.0},
                {"code": "000858", "total_ratio": 8.0},
                {"code": "300750", "total_ratio": 6.0},
            ],
        })
        tt.snapshot("m1")
        # 当前持仓变化（300750 退出，新增 600276）
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试",
            "top_holdings": [
                {"code": "600519", "total_ratio": 10.0},
                {"code": "000858", "total_ratio": 8.0},
                {"code": "600276", "total_ratio": 6.0},
            ],
        })
        changes = tt.track_changes("m1")
    assert "300750" in changes["removed"]
    assert "600276" in changes["added"]


def test_compute_turnover_rate_basic():
    """换手率 = (新增权重 + 退出权重) / 2。"""
    import turnover_tracker as tt

    with _DirIsolation():
        import _common
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试",
            "top_holdings": [
                {"code": "600519", "total_ratio": 10.0},
                {"code": "000858", "total_ratio": 8.0},
                {"code": "300750", "total_ratio": 6.0},
            ],
        })
        tt.snapshot("m1")
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试",
            "top_holdings": [
                {"code": "600519", "total_ratio": 10.0},
                {"code": "000858", "total_ratio": 8.0},
                {"code": "600276", "total_ratio": 6.0},
            ],
        })
        rate = tt.compute_turnover_rate("m1")
    # 退出 6% (300750) + 新增 6% (600276) / 2 = 6%
    assert rate == 6.0


def test_compute_turnover_no_history():
    """无历史时换手率 = None。"""
    import turnover_tracker as tt

    with _DirIsolation():
        import _common
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试", "top_holdings": [],
        })
        rate = tt.compute_turnover_rate("m1")
    assert rate is None