"""monthly_updater._post_update_hooks 集成测试（v2.0.0）。"""
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


def test_post_update_hooks_writes_all_fields():
    """_post_update_hooks 应写 capability_scores/attribution/risk_metrics/speech_fingerprint。"""
    import monthly_updater as mu
    import _common

    with _DirIsolation():
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试经理", "company": "X",
            "strategy_texts": ["我看好消费板块，ROE 较高，估值合理，分红稳定。"],
            "viewpoint_human": "我当前重仓持有白酒龙头。",
            "bio": "我是测试经理，擅长消费领域。",
            "top_holdings": [
                {"code": "600519", "name": "贵州茅台", "total_ratio": 10.0},
                {"code": "000858", "name": "五粮液", "total_ratio": 8.0},
            ],
            "performance": {"summary": {"avg_returns": {
                "近1月": "3", "近3月": "-5", "近6月": "10", "近1年": "15", "近3年": "30",
            }}},
            "style_code": "VALUE-HIGH_POS-SECTOR_CONCENTRATED-LOW_TURNOVER-A_SHARE",
            "industry_preference": ["消费"],
        })
        mu._post_update_hooks("m1")
        saved = _common.load_manager("m1")
        assert "capability_scores" in saved
        assert "attribution" in saved
        assert "risk_metrics" in saved
        assert "speech_fingerprint" in saved
        assert saved["capability_scores"]["composite"] > 0

        assert os.path.exists(os.path.join(_common.DATA_DIR, "track_records", "m1.jsonl"))
        assert os.path.exists(os.path.join(_common.DATA_DIR, "viewpoints_history", "m1.jsonl"))
        assert os.path.exists(os.path.join(_common.DATA_DIR, "style_history", "m1.jsonl"))


def test_post_update_hooks_does_not_crash_on_empty_manager():
    """经理档案缺失字段时不应崩溃。"""
    import monthly_updater as mu
    import _common

    with _DirIsolation():
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试", "company": "X",
        })
        mu._post_update_hooks("m1")
        saved = _common.load_manager("m1")
        assert saved is not None
