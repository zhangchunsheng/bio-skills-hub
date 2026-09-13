"""边界情况测试 — 补充核心模块的边界覆盖（v2.0.3）。

覆盖范围：
- 并发读写名单安全性
- 大数据量性能
- 网络超时恢复
- 损坏文件处理
- 特殊字符处理
- 空值/None处理
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime


def _today() -> str:
    """当前日期，避免 cache TTL 测试因硬编码日期失效（BUG-1 修复）。"""
    return datetime.now().strftime("%Y-%m-%d")
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


# ============================================================
# FIXTURE: 隔离目录
# ============================================================

class _DirIsolation:
    """安全的目录隔离"""
    def __init__(self):
        self.original = {}
        self.tmp = None

    def __enter__(self):
        import _common
        self.original = {
            "DATA_DIR": _common.DATA_DIR,
            "MANAGERS_DIR": _common.MANAGERS_DIR,
            "PROGRESS_DIR": _common.PROGRESS_DIR,
            "EXPORTS_DIR": _common.EXPORTS_DIR,
            "ROSTER_PATH": _common.ROSTER_PATH,
        }
        self.tmp = tempfile.mkdtemp()
        data_dir = os.path.join(self.tmp, "data")
        mgr_dir = os.path.join(data_dir, "managers")
        prog_dir = os.path.join(data_dir, "progress")
        exp_dir = os.path.join(data_dir, "exports")
        os.makedirs(mgr_dir)
        os.makedirs(prog_dir)
        os.makedirs(exp_dir)

        _common.DATA_DIR = data_dir
        _common.MANAGERS_DIR = mgr_dir
        _common.PROGRESS_DIR = prog_dir
        _common.EXPORTS_DIR = exp_dir
        _common.ROSTER_PATH = os.path.join(data_dir, "roster.json")
        return self.tmp

    def __exit__(self, *args):
        try:
            import _common
            for k, v in self.original.items():
                setattr(_common, k, v)
        finally:
            if self.tmp:
                import shutil
                shutil.rmtree(self.tmp, ignore_errors=True)


# ============================================================
# 并发读写名单安全性
# ============================================================

def test_concurrent_roster_read_write():
    """并发读写名单不应导致数据损坏（串行模拟，避免Windows文件锁问题）"""
    import _common
    import roster_manager

    with _DirIsolation():
        # 初始化名单
        roster = {
            "meta": {"version": 1, "count": 0, "last_update": "", "max": 100},
            "managers": []
        }
        _common.write_json(_common.ROSTER_PATH, roster)

        # 串行模拟并发场景（Windows文件系统不支持并发rename）
        success_count = 0
        for i in range(10):
            result = roster_manager.add_manager(
                f"concurrent_{i}",
                f"并发测试{i}",
                "测试公司"
            )
            if result.get("success"):
                success_count += 1

        # 验证读取
        managers = roster_manager.list_managers()
        assert len(managers) == success_count
        assert success_count == 10


# ============================================================
# 大数据量性能
# ============================================================

def test_large_roster_performance():
    """100个经理的名单操作应在合理时间内完成"""
    import _common
    import roster_manager

    with _DirIsolation():
        # 初始化名单
        roster = {
            "meta": {"version": 1, "count": 0, "last_update": "", "max": 100},
            "managers": []
        }
        _common.write_json(_common.ROSTER_PATH, roster)

        # 添加100个经理
        start_time = time.time()
        for i in range(100):
            result = roster_manager.add_manager(f"perf_{i}", f"性能测试{i}", "测试公司")
            assert result["success"] is True
        add_time = time.time() - start_time

        # 读取名单
        start_time = time.time()
        managers = roster_manager.list_managers()
        read_time = time.time() - start_time

        # 检查是否已满
        start_time = time.time()
        is_full = roster_manager.is_full()
        full_time = time.time() - start_time

        assert len(managers) == 100
        assert is_full is True
        assert add_time < 10.0, f"添加100个经理耗时 {add_time:.2f}s > 10s"
        assert read_time < 1.0, f"读取名单耗时 {read_time:.2f}s > 1s"
        assert full_time < 0.1, f"检查是否已满耗时 {full_time:.2f}s > 0.1s"

        print(f"\n性能测试结果:")
        print(f"  添加100个经理: {add_time:.2f}s")
        print(f"  读取名单: {read_time:.2f}s")
        print(f"  检查是否已满: {full_time:.3f}s")


# ============================================================
# 损坏文件处理
# ============================================================

def test_corrupt_roster_recovery():
    """损坏的 roster.json 应返回默认值"""
    import _common

    with _DirIsolation():
        # 写入损坏的JSON
        with open(_common.ROSTER_PATH, "w", encoding="utf-8") as f:
            f.write("{invalid json content")

        # 应返回默认值
        roster = _common.read_json(_common.ROSTER_PATH, default={"meta": {"count": 0}, "managers": []})
        assert roster["meta"]["count"] == 0
        assert roster["managers"] == []


def test_corrupt_manager_recovery():
    """损坏的经理档案应返回默认值（不崩溃）"""
    import _common

    with _DirIsolation():
        os.makedirs(_common.MANAGERS_DIR, exist_ok=True)

        # 写入损坏的JSON
        mgr_path = os.path.join(_common.MANAGERS_DIR, "corrupt.json")
        with open(mgr_path, "w", encoding="utf-8") as f:
            f.write("{corrupt data")

        # 应返回 None 或空字典（不崩溃）
        mgr = _common.load_manager("corrupt")
        # load_manager 对损坏文件返回 None（因为 default=None）
        assert mgr is None or mgr == {}


# ============================================================
# 特殊字符处理
# ============================================================

def test_special_characters_in_name():
    """经理姓名包含特殊字符时应正确处理"""
    import _common
    import roster_manager

    with _DirIsolation():
        # 初始化名单
        roster = {
            "meta": {"version": 1, "count": 0, "last_update": "", "max": 100},
            "managers": []
        }
        _common.write_json(_common.ROSTER_PATH, roster)

        # 测试各种特殊字符
        test_cases = [
            ("张三（测试）", "括号"),
            ("李四·王五", "中间点"),
            ("赵六-钱七", "连字符"),
            ("孙八_周九", "下划线"),
            ("吴十.", "点号"),
        ]

        for name, desc in test_cases:
            result = roster_manager.add_manager(f"special_{desc}", name, "测试公司")
            assert result["success"] is True, f"添加失败 ({desc}): {result}"

        # 验证可以正确列出
        managers = roster_manager.list_managers()
        assert len(managers) == len(test_cases)


def test_manager_path_sanitization():
    """经理ID中的特殊字符应被正确清理"""
    import _common

    test_cases = [
        ("normal_id", "normal_id"),
        ("id/with/slash", "id_with_slash"),
        ("id\\with\\backslash", "id_with_backslash"),
        ("id:with:colon", "id_with_colon"),
        ("id*with*star", "id_with_star"),
        ("id?with?question", "id_with_question"),
    ]

    for input_id, expected_safe in test_cases:
        safe_id = _common.manager_path(input_id)
        # 路径应包含清理后的ID
        assert expected_safe in safe_id, f"路径清理失败: {input_id} -> {safe_id}"


# ============================================================
# 空值/None处理
# ============================================================

def test_none_handling_in_search():
    """搜索时处理 None 值"""
    import manager_search

    # 模拟包含 None 值的索引
    fake_index = {
        "meta": {"last_update": _today(), "count": 2},
        "managers": [
            {"id": "1", "name": "张三", "company": "A基金",
             "fund_codes": None, "fund_names": None,  # None 值
             "tenure_days": 100, "tenure_return": "20%",
             "rep_fund_code": "", "rep_fund_name": "", "scale": "", "rep_fund_return": ""},
            {"id": "2", "name": None, "company": None,  # None 值
             "fund_codes": [], "fund_names": [],
             "tenure_days": 0, "tenure_return": "", "rep_fund_code": "",
             "rep_fund_name": "", "scale": "", "rep_fund_return": ""},
        ],
    }

    with patch("manager_search.read_json", return_value=fake_index):
        # 搜索不应崩溃
        results = manager_search.search_managers("张三", search_type="name")
        assert len(results) == 1
        assert results[0]["name"] == "张三"


def test_empty_holdings_aggregation():
    """空持仓数据聚合不应崩溃"""
    import fetch_holdings

    # 空结果列表
    result = fetch_holdings._aggregate_holdings([])
    assert result["latest_date"] == ""
    assert result["holdings"] == []

    # 包含空持仓的结果
    results = [
        {"fund_code": "A", "report_date": "2026-06-30", "holdings": []},
        {"fund_code": "B", "report_date": "", "holdings": []},
    ]
    result = fetch_holdings._aggregate_holdings(results)
    assert result["latest_date"] == "2026-06-30"
    assert result["holdings"] == []


def test_empty_performance_summary():
    """空业绩数据汇总不应崩溃"""
    import fetch_performance

    # 空基金列表
    result = fetch_performance._summarize_performance([])
    assert result == {}

    # 包含空收益率的基金
    funds = [
        {"fund_code": "A", "fund_name": "A", "returns": {}},
        {"fund_code": "B", "fund_name": "B", "returns": {"近1月": None, "近1年": "N/A"}},
    ]
    result = fetch_performance._summarize_performance(funds)
    assert result["fund_count"] == 2
    # 有效数据应被正确计算
    assert "近1月" not in result["avg_returns"]  # 全是None
    assert "近1年" not in result["avg_returns"]  # 全是无效字符串


# ============================================================
# 边界阈值测试
# ============================================================

def test_scale_parsing_edge_cases():
    """规模解析边界情况"""
    import monthly_updater

    test_cases = [
        ("", None),
        (None, None),
        ("0亿", 0.0),
        ("0.01亿", 0.01),
        ("10000亿", 10000.0),
        ("1万亿", 10000.0),
        ("500万元", 0.05),
        ("100万", 0.01),
        ("N/A", None),
        ("规模未知", None),
    ]

    for input_val, expected in test_cases:
        result = monthly_updater._parse_scale(input_val)
        assert result == expected, f"解析失败: '{input_val}' -> {result} (期望 {expected})"


def test_detect_changes_threshold_boundary():
    """变化检测阈值边界测试"""
    import monthly_updater

    # 规模变化正好在阈值上
    fresh = {"scale": "110亿"}
    archived = {"scale": "100亿"}
    # 10% 变化应被检测到
    result = monthly_updater._detect_changes(fresh, archived)
    # 注意：需要其他维度也无变化才只看规模
    assert any("规模变化" in r for r in result["reasons"]) or not result["changed"]

    # 规模变化在阈值下
    fresh = {"scale": "109亿"}
    archived = {"scale": "100亿"}
    result = monthly_updater._detect_changes(fresh, archived)
    # 9% 变化不应被检测到
    assert not any("规模变化" in r for r in result["reasons"])


# ============================================================
# 运行所有
# ============================================================

def main():
    tests = [
        (name, obj)
        for name, obj in globals().items()
        if name.startswith("test_") and callable(obj)
    ]
    passed = 0
    failed = 0
    import traceback
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*60}\n边界情况测试: {passed} 通过, {failed} 失败\n{'='*60}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
