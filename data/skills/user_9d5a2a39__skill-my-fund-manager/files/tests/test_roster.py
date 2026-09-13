"""roster_manager.py 单元测试（v2.0 新增）。

覆盖：
- add_manager 去重、上限、自动类型判断
- remove_manager 删除名单 + 档案文件
- remove_manager_by_name 大小写不敏感
- is_in_roster / is_full
- update_status 状态机
- list_managers 摘要
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def _setup_isolated_dirs():
    """创建临时目录并返回 (DATA_DIR, MANAGERS_DIR)，调用 _setup 后应清理。"""
    tmp = tempfile.mkdtemp()
    data_dir = os.path.join(tmp, "data")
    managers_dir = os.path.join(data_dir, "managers")
    progress_dir = os.path.join(data_dir, "progress")
    exports_dir = os.path.join(data_dir, "exports")
    os.makedirs(managers_dir)
    os.makedirs(progress_dir)
    os.makedirs(exports_dir)
    return tmp, data_dir, managers_dir, progress_dir, exports_dir


def _restore_dirs(original):
    import _common
    _common.DATA_DIR = original["DATA_DIR"]
    _common.MANAGERS_DIR = original["MANAGERS_DIR"]
    _common.PROGRESS_DIR = original["PROGRESS_DIR"]
    _common.EXPORTS_DIR = original["EXPORTS_DIR"]
    _common.ROSTER_PATH = original["ROSTER_PATH"]


def _capture_dirs():
    """备份当前目录常量，方便测试结束后恢复。"""
    import _common
    return {
        "DATA_DIR": _common.DATA_DIR,
        "MANAGERS_DIR": _common.MANAGERS_DIR,
        "PROGRESS_DIR": _common.PROGRESS_DIR,
        "EXPORTS_DIR": _common.EXPORTS_DIR,
        "ROSTER_PATH": _common.ROSTER_PATH,
    }


def _switch_dirs(data_dir, managers_dir, progress_dir, exports_dir):
    import _common
    _common.DATA_DIR = data_dir
    _common.MANAGERS_DIR = managers_dir
    _common.PROGRESS_DIR = progress_dir
    _common.EXPORTS_DIR = exports_dir
    _common.ROSTER_PATH = os.path.join(data_dir, "roster.json")  # 修复 v2.0 测试 bug：v2.0 测试漏设 ROSTER_PATH


# ============================================================
# 基础 CRUD
# ============================================================

def test_add_manager_creates_entry():
    """add_manager 应写入名单。"""
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        result = roster_manager.add_manager("30189741", "张坤", "易方达基金", manager_type="公募")
        assert result["success"] is True
        assert "张坤" in result["message"]

        # roster.json 应包含该经理
        with open(os.path.join(d, "roster.json"), encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["managers"]) == 1
        assert data["managers"][0]["id"] == "30189741"
        assert data["managers"][0]["name"] == "张坤"
        assert data["managers"][0]["manager_type"] == "公募"
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


def test_add_manager_dedup():
    """重复添加同 ID 的经理应返回已存在提示。"""
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        roster_manager.add_manager("30189741", "张坤", "易方达基金")
        result = roster_manager.add_manager("30189741", "张坤", "易方达基金")
        assert result["success"] is False
        assert "已在名单中" in result["message"]
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


def test_add_manager_auto_detect_type():
    """未传 manager_type 应根据 ID 前缀自动判断。"""
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager

        # amac_ 前缀 → 私募
        r1 = roster_manager.add_manager("amac_12345", "某私募经理")
        assert r1["manager"]["manager_type"] == "私募"

        # 数字 ID → 公募
        r2 = roster_manager.add_manager("30189741", "公募经理")
        assert r2["manager"]["manager_type"] == "公募"
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


def test_add_manager_full_check():
    """名单上限 100 应被强制执行。"""
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        # 直接灌满 100 个
        with open(os.path.join(d, "roster.json"), "w", encoding="utf-8") as f:
            json.dump({
                "meta": {"version": 1, "count": 100, "max": 100},
                "managers": [
                    {"id": str(i), "name": f"M{i}"} for i in range(100)
                ],
            }, f)

        result = roster_manager.add_manager("99999", "第101个经理")
        assert result["success"] is False
        assert "已满" in result["message"]
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


# ============================================================
# 删除
# ============================================================

def test_remove_manager_deletes_profile_file():
    """删除名单时应同时删除档案文件。"""
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        from _common import save_manager

        roster_manager.add_manager("test_id", "测试", "测试公司")
        save_manager("test_id", {"name": "测试"})

        # 验证档案文件存在
        from _common import manager_path
        assert os.path.exists(manager_path("test_id"))

        # 删除
        result = roster_manager.remove_manager("test_id")
        assert result["success"] is True

        # 档案文件应被删除
        assert not os.path.exists(manager_path("test_id"))
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


def test_remove_manager_by_name_case_insensitive():
    """按姓名删除应大小写不敏感。"""
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        roster_manager.add_manager("100", "Buffett")
        result = roster_manager.remove_manager_by_name("BUFFETT")
        assert result["success"] is True
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


def test_remove_manager_by_name_not_found():
    """不存在的姓名应返回失败。"""
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        result = roster_manager.remove_manager_by_name("根本不存在的经理")
        assert result["success"] is False
        assert "未找到" in result["message"]
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


# ============================================================
# 列表/查询
# ============================================================

def test_list_managers_returns_summaries():
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        roster_manager.add_manager("1", "甲", "公司A")
        roster_manager.add_manager("2", "乙", "公司B", manager_type="私募")

        result = roster_manager.list_managers()
        assert len(result) == 2
        assert result[0]["name"] == "甲"
        assert result[1]["manager_type"] == "私募"
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


def test_is_in_roster_checks_by_id():
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        assert not roster_manager.is_in_roster("nonexistent")

        roster_manager.add_manager("exists_id", "存在经理")
        assert roster_manager.is_in_roster("exists_id")
        # int 自动转 str：is_in_roster 接受任意类型，转为 string 比较
        assert roster_manager.is_in_roster(30189741) is False  # 没有这个 ID
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


def test_is_full_basic():
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        assert not roster_manager.is_full()
        # 灌满
        for i in range(100):
            roster_manager.add_manager(str(i), f"M{i}")
        assert roster_manager.is_full()
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


# ============================================================
# 状态机
# ============================================================

def test_update_status_changes_status():
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        roster_manager.add_manager("1", "甲")

        result = roster_manager.update_status("1", "distilled")
        assert result["success"]

        roster = roster_manager.get_roster()
        target = next(m for m in roster["managers"] if m["id"] == "1")
        assert target["status"] == "distilled"
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


def test_update_status_invalid_value():
    """非法 status 应被拒绝。"""
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        roster_manager.add_manager("1", "甲")
        result = roster_manager.update_status("1", "hacker_value")
        # 应返回失败或被拒绝
        assert not result["success"] or "invalid" in str(result).lower() or "无效" in str(result)
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


def test_meta_count_keeps_in_sync():
    """meta.count 应与 managers 列表长度同步。"""
    tmp, d, m, p, e = _setup_isolated_dirs()
    orig = _capture_dirs()
    _switch_dirs(d, m, p, e)
    try:
        import roster_manager
        roster_manager.add_manager("1", "甲")
        roster_manager.add_manager("2", "乙")
        roster = roster_manager.get_roster()
        assert roster["meta"]["count"] == 2
        roster_manager.remove_manager("1")
        assert roster_manager.get_roster()["meta"]["count"] == 1
    finally:
        _restore_dirs(orig)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


# ============================================================
# 运行测试
# ============================================================

def main():
    tests = [
        (name, obj)
        for name, obj in globals().items()
        if name.startswith("test_") and callable(obj)
    ]
    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*60}\nroster_manager 测试: {passed} 通过, {failed} 失败\n{'='*60}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
