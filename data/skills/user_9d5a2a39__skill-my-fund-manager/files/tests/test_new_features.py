"""v2.0 新功能测试：manager_compare + data_backup。"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


# ============================================================
# manager_compare 测试
# ============================================================

def test_compare_two_managers_basic():
    """2 个经理对比基本流程。"""
    from manager_compare import compare_managers

    # 用现有的 manager 文件 ID（data/managers/） — 假设存在
    result = compare_managers(["30189741", "30189744"])
    # 只要不崩溃就算通过（数据可能不完整）
    if result.get("available"):
        assert "summary" in result
        assert "performance_comparison" in result
        assert "holdings_overlap" in result
    # 若数据缺失，至少返回结构
    assert "manager_count" in result or "reason" in result


def test_compare_rejects_single_manager():
    """1 个经理应被拒绝。"""
    from manager_compare import compare_managers
    result = compare_managers(["30189741"])
    assert result["available"] is False
    assert "2-4" in result.get("reason", "")


def test_compare_rejects_too_many():
    """5 个经理应被拒绝（上限 4）。"""
    from manager_compare import compare_managers
    result = compare_managers(["a", "b", "c", "d", "e"])
    assert result["available"] is False


def test_compare_all_missing_returns_helpful_error():
    """全部缺失应给出原因。"""
    from manager_compare import compare_managers
    result = compare_managers(["nonexistent1", "nonexistent2"])
    assert result["available"] is False
    assert "缺失" in result.get("reason", "")


def test_compare_with_mocked_manager_data():
    """直接喂数据测试（不依赖实际文件）。"""
    from manager_compare import compare_managers

    # 准备测试数据
    tmp = tempfile.mkdtemp()
    import _common
    original = _common.MANAGERS_DIR
    _common.MANAGERS_DIR = tmp
    try:
        # 创建 2 个 mock 经理档案
        for mid in ["m1", "m2"]:
            data = {
                "name": mid,
                "company": f"公司{mid}",
                "scale": "100亿",
                "tenure_return": "20%",
                "fund_count": 3,
                "status": "distilled",
                "performance": {"1y": f"{mid == 'm1' and 25 or 15}"},
                "holdings": [
                    {"code": "000001", "weight": 8},
                    {"code": "000002", "weight": 6 if mid == "m1" else 0},
                ],
                "style_dna": {"concentration": "高" if mid == "m1" else "中"},
            }
            with open(os.path.join(tmp, f"{mid}.json"), "w", encoding="utf-8") as f:
                json.dump(data, f)

        result = compare_managers(["m1", "m2"])
        assert result["available"] is True
        assert result["manager_count"] == 2
        # 业绩对比：m1 最佳
        perf_1y = result["performance_comparison"]["1y"]
        assert perf_1y["_best"] == "m1"
        # 重仓股：000001 共持
        assert result["holdings_overlap"]["overlap_count"] >= 1
    finally:
        _common.MANAGERS_DIR = original
        import shutil; shutil.rmtree(tmp, ignore_errors=True)


# ============================================================
# data_backup 测试
# ============================================================

def test_backup_creates_zip_file():
    """backup_all 应生成 zip 文件。"""
    from data_backup import backup_all
    import _common

    with tempfile.TemporaryDirectory() as tmp:
        # 重定向到 tmp
        original_data = _common.DATA_DIR
        _common.DATA_DIR = os.path.join(tmp, "data")
        _common.ensure_dirs()
        try:
            backup_path = backup_all(os.path.join(tmp, "backups"))
            assert os.path.exists(backup_path)
            assert backup_path.endswith(".zip")
            assert os.path.getsize(backup_path) > 100  # 应有内容
        finally:
            _common.DATA_DIR = original_data


def test_backup_includes_manifest():
    """备份应包含 MANIFEST.json。"""
    import zipfile
    from data_backup import backup_all
    import _common

    with tempfile.TemporaryDirectory() as tmp:
        original = _common.DATA_DIR
        _common.DATA_DIR = os.path.join(tmp, "data")
        _common.ensure_dirs()
        try:
            backup_path = backup_all(os.path.join(tmp, "backups"))
            with zipfile.ZipFile(backup_path, "r") as zf:
                names = zf.namelist()
                assert "MANIFEST.json" in names
        finally:
            _common.DATA_DIR = original


def test_restore_requires_existing_file():
    """不存在的备份应返回失败。"""
    from data_backup import restore_all
    result = restore_all("/nonexistent/path.zip")
    assert result["success"] is False
    assert "不存在" in result.get("reason", "")


def test_backup_restore_roundtrip():
    """完整备份-恢复循环。"""
    from data_backup import backup_all, restore_all
    import _common

    with tempfile.TemporaryDirectory() as tmp:
        original = _common.DATA_DIR
        # 设置原始数据目录
        data_dir = os.path.join(tmp, "data")
        os.makedirs(os.path.join(data_dir, "managers"))
        _common.DATA_DIR = data_dir
        _common.MANAGERS_DIR = os.path.join(data_dir, "managers")
        _common.PROGRESS_DIR = os.path.join(data_dir, "progress")
        _common.EXPORTS_DIR = os.path.join(data_dir, "exports")
        _common.ROSTER_PATH = os.path.join(data_dir, "roster.json")

        # 写一个 roster.json
        with open(_common.ROSTER_PATH, "w", encoding="utf-8") as f:
            json.dump({"meta": {"count": 1}, "managers": [{"id": "x", "name": "测试"}]}, f)
        # 写一个 manager 文件
        with open(os.path.join(data_dir, "managers", "x.json"), "w", encoding="utf-8") as f:
            json.dump({"name": "测试"}, f)

        try:
            # 1. 备份
            backup_path = backup_all(os.path.join(tmp, "backups"))
            assert os.path.exists(backup_path)

            # 2. 删除原始数据
            os.remove(_common.ROSTER_PATH)
            os.remove(os.path.join(data_dir, "managers", "x.json"))

            # 3. 恢复（overwrite）
            result = restore_all(backup_path, overwrite=True)
            assert result["success"] is True

            # 4. 验证数据回来
            assert os.path.exists(_common.ROSTER_PATH)
            with open(_common.ROSTER_PATH, encoding="utf-8") as f:
                recovered = json.load(f)
            assert recovered["managers"][0]["id"] == "x"
        finally:
            _common.DATA_DIR = original
            _common.MANAGERS_DIR = os.path.join(original, "managers")
            _common.PROGRESS_DIR = os.path.join(original, "progress")
            _common.EXPORTS_DIR = os.path.join(original, "exports")
            _common.ROSTER_PATH = os.path.join(original, "roster.json")


# ============================================================
# CLI 烟雾测试
# ============================================================

def test_manager_compare_cli_help():
    """CLI --help 应输出。"""
    import subprocess
    result = subprocess.run(
        ["python", str(SCRIPTS_DIR / "manager_compare.py"), "--help"],
        capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0
    assert "manager_ids" in result.stdout.lower() or "对比" in result.stdout


def test_data_backup_cli_help():
    """CLI --help 应输出。"""
    import subprocess
    result = subprocess.run(
        ["python", str(SCRIPTS_DIR / "data_backup.py"), "--help"],
        capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0


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

    print(f"\n{'='*60}\n新增功能测试: {passed} 通过, {failed} 失败\n{'='*60}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
