"""业绩归因测试（v2.0.0）— 6 个用例。"""
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


def test_detect_industry_consumer():
    """识别消费行业。"""
    import performance_attribution as pa
    assert pa._detect_industry("贵州茅台") == "消费"
    assert pa._detect_industry("宁德时代") == "科技"  # 字典里


def test_detect_industry_unknown():
    """未知股票 → 其他。"""
    import performance_attribution as pa
    assert pa._detect_industry("XYZ公司") == "其他"


def test_attribute_performance_no_data():
    """无业绩数据时返回占位结果。"""
    import performance_attribution as pa
    mgr = {"top_holdings": [], "performance": {"summary": {"avg_returns": {}}}}
    result = pa.attribute_performance(mgr)
    assert result["total_return"] == 0.0
    assert "无业绩数据" in result["summary"]


def test_attribute_performance_positive():
    """正收益经理的归因分三项。"""
    import performance_attribution as pa
    mgr = {
        "performance": {"summary": {"avg_returns": {"近1年": "20.0"}}},
        "top_holdings": [
            {"name": "贵州茅台", "total_ratio": 8.0},  # 消费
            {"name": "腾讯控股", "total_ratio": 6.0},  # 科技
            {"name": "宁德时代", "total_ratio": 5.0},  # 科技
            {"name": "中国平安", "total_ratio": 4.0},  # 金融
        ],
    }
    result = pa.attribute_performance(mgr)
    assert result["total_return"] == 20.0
    # 归因三项应都已计算
    assert "industry_exposure" in result
    assert "stock_selection" in result
    assert "timing" in result
    assert isinstance(result["industry_exposure"], (int, float))


def test_attribute_performance_negative():
    """负收益经理归因。"""
    import performance_attribution as pa
    mgr = {
        "performance": {"summary": {"avg_returns": {"近1年": "-15.0"}}},
        "top_holdings": [
            {"name": "贵州茅台", "total_ratio": 10.0},
            {"name": "腾讯控股", "total_ratio": 8.0},
        ],
    }
    result = pa.attribute_performance(mgr)
    assert result["total_return"] == -15.0
    # summary 应是非空文本（含"最大贡献来自"）
    assert "最大贡献来自" in result["summary"]


def test_save_attribution_writes_to_manager():
    """save_attribution 应写到 manager.json 的 attribution 字段。"""
    import performance_attribution as pa

    with _DirIsolation():
        import _common
        _common.write_json(os.path.join(_common.MANAGERS_DIR, "m1.json"), {
            "id": "m1", "name": "测试",
            "performance": {"summary": {"avg_returns": {"近1年": "10.0"}}},
            "top_holdings": [{"name": "贵州茅台", "total_ratio": 5.0}],
        })
        result = pa.evaluate_manager("m1")
        attr = {k: v for k, v in result.items() if k not in ("manager_id", "name")}
        pa.save_attribution("m1", attr)
        saved = _common.load_manager("m1")
    assert "attribution" in saved
    assert saved["attribution"]["total_return"] == 10.0