"""观点时序追踪测试（v2.0.0）— 10 个用例。"""
from __future__ import annotations

import json
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


def test_score_sentiment_positive():
    """纯积极 → +1.0。"""
    import viewpoint_tracker as vt
    s = vt._score_sentiment("看好 机会 增长 改善 受益 优势")
    assert s == 1.0


def test_score_sentiment_negative():
    """纯消极 → -1.0。"""
    import viewpoint_tracker as vt
    s = vt._score_sentiment("谨慎 风险 下行 回落 恶化 亏损")
    assert s == -1.0


def test_score_sentiment_neutral():
    """无关键词 → 0.0。"""
    import viewpoint_tracker as vt
    s = vt._score_sentiment("投资策略基于量化分析。")
    assert s == 0.0


def test_detect_stance_sector_bullish():
    """看好具体板块。"""
    import viewpoint_tracker as vt
    s = vt._detect_stance("我看好消费板块的机会，建议增持白酒")
    assert "消费" in s


def test_detect_stance_sector_bearish():
    """谨慎具体板块。"""
    import viewpoint_tracker as vt
    s = vt._detect_stance("我们对科技板块保持谨慎，注意风险")
    assert "科技" in s


def test_record_viewpoint_creates_jsonl():
    """record_viewpoint 应追加 JSONL 一行。"""
    import viewpoint_tracker as vt

    captured = {}
    with _DirIsolation():
        vt.record_viewpoint("m1", "2026-06-30", "我看好消费板块的机会", "季报")
        import _common
        captured["path"] = os.path.join(_common.DATA_DIR, "viewpoints_history", "m1.jsonl")
        captured["lines"] = open(captured["path"], "r", encoding="utf-8").readlines()
    lines = captured["lines"]
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["date"] == "2026-06-30"
    assert entry["stance"]  # 非空


def test_get_history_returns_recent_first():
    """get_history 应返回最近 N 期，正序。"""
    import viewpoint_tracker as vt

    with _DirIsolation():
        vt.record_viewpoint("m1", "2026-03-31", "Q1 观点", "季报")
        vt.record_viewpoint("m1", "2026-06-30", "Q2 观点", "季报")
        history = vt.get_history("m1", limit=2)
    assert len(history) == 2
    assert history[0]["date"] == "2026-03-31"
    assert history[1]["date"] == "2026-06-30"


def test_get_history_empty_when_no_file():
    """无文件 → 返回空 list。"""
    import viewpoint_tracker as vt
    with _DirIsolation():
        history = vt.get_history("nonexistent")
    assert history == []


def test_detect_drift_detects_stance_change():
    """立场从「中性」→「整体看多」应检出漂移。"""
    import viewpoint_tracker as vt

    with _DirIsolation():
        vt.record_viewpoint("m1", "2026-03-31", "中性观点无明显倾向", "季报")
        vt.record_viewpoint("m1", "2026-06-30", "我看好机会强劲增长优势", "季报")
        drift = vt.detect_drift("m1")
    assert drift is not None
    assert drift["stance_changed"] is True


def test_detect_drift_returns_none_for_stable():
    """立场稳定时返回 None。"""
    import viewpoint_tracker as vt

    with _DirIsolation():
        vt.record_viewpoint("m1", "2026-03-31", "看好机会增长", "季报")
        vt.record_viewpoint("m1", "2026-06-30", "看好机会增长", "季报")
        drift = vt.detect_drift("m1")
    # 立场相同 + sentiment_delta=0 → 无漂移
    assert drift is None