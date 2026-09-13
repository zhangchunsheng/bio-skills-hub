"""monthly_updater 更新检测逻辑测试。"""
from __future__ import annotations

import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from monthly_updater import _detect_changes, _parse_scale


def test_parse_scale_supports_common_units():
    assert _parse_scale("322.85亿元") == 322.85
    assert _parse_scale("1,234.5亿元") == 1234.5
    assert _parse_scale("5000万元") == 0.5
    assert _parse_scale("暂无数据") is None


def test_detect_changes_scale_threshold_is_inclusive():
    result = _detect_changes(
        {"scale": "110亿元"},
        {"scale": "100亿元"},
    )
    assert result["changed"] is True
    assert "scale_change" in result["details"]


def test_detect_changes_holdings_add_remove_and_ratio():
    old = {
        "top_holdings": [
            {"code": "A", "total_ratio": 10},
            {"code": "B", "total_ratio": 8},
        ]
    }
    added = _detect_changes(
        {"top_holdings": [{"code": "A", "total_ratio": 10}, {"code": "C", "total_ratio": 8}]},
        old,
    )
    assert added["changed"] is True
    assert added["details"]["holdings_change"]["added"] == ["C"]
    assert added["details"]["holdings_change"]["removed"] == ["B"]

    ratio = _detect_changes(
        {"top_holdings": [{"code": "A", "total_ratio": 13}, {"code": "B", "total_ratio": 8}]},
        old,
    )
    assert ratio["changed"] is True
    assert ratio["details"]["holdings_ratio_change"][0]["diff"] == 3


def test_detect_changes_report_and_performance_thresholds():
    old = {
        "holdings_report_date": "2026-03-31",
        "performance": {"summary": {"avg_returns": {"近1年": 10}}},
    }
    result = _detect_changes(
        {
            "holdings_report_date": "2026-06-30",
            "performance": {"summary": {"avg_returns": {"近1年": 15}}},
        },
        old,
    )
    assert result["changed"] is True
    assert "report_date_change" in result["details"]
    assert result["details"]["perf_change"]["diff"] == 5


def test_detect_changes_no_change_for_below_thresholds():
    result = _detect_changes(
        {
            "scale": "109亿元",
            "top_holdings": [{"code": "A", "total_ratio": 12.9}],
            "holdings_report_date": "2026-06-30",
            "performance": {"summary": {"avg_returns": {"近1年": 14.9}}},
        },
        {
            "scale": "100亿元",
            "top_holdings": [{"code": "A", "total_ratio": 10}],
            "holdings_report_date": "2026-06-30",
            "performance": {"summary": {"avg_returns": {"近1年": 10}}},
        },
    )
    assert result["changed"] is False
