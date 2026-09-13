"""
测试数据清理工具
清理名单中的测试数据，释放名额给真实经理。
支持预览模式和实际清理模式。
"""

import os
import re
import sys

# 确保能 import 同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _common
from _common import read_json, write_json, log, ROSTER_PATH, MANAGERS_DIR

# 测试数据模式（正则表达式）
TEST_PATTERNS = [
    r'^M\d+$',           # M0, M1, ..., M94
    r'^甲$',             # 甲
    r'^乙$',             # 乙
    r'^存在经理$',        # 存在经理
    r'^第\d+个经理$',     # 第101个经理
    r'^测试经理$',        # 测试经理
    r'^某私募经理$',      # 某私募经理（测试用）
]


def is_test_manager(name):
    """判断是否为测试数据"""
    for pattern in TEST_PATTERNS:
        if re.match(pattern, name):
            return True
    return False


def preview_cleanup():
    """预览清理结果（不实际删除）"""
    roster = read_json(ROSTER_PATH, default={"meta": {"count": 0}, "managers": []})
    managers = roster.get("managers", [])

    if not managers:
        print("📋 名单为空，无需清理")
        return []

    test_managers = []
    real_managers = []

    for m in managers:
        if is_test_manager(m["name"]):
            test_managers.append(m)
        else:
            real_managers.append(m)

    print("=" * 60)
    print("📊 名单数据分析")
    print("=" * 60)
    print(f"总人数：{len(managers)}")
    print(f"真实经理：{len(real_managers)} 人")
    print(f"测试数据：{len(test_managers)} 人")
    print(f"释放名额：{len(test_managers)} 个")
    print()

    if test_managers:
        print("🗑️  将清理的测试数据：")
        print("-" * 60)
        for m in test_managers[:20]:  # 只显示前20个
            print(f"  - {m['name']} (ID: {m['id']}, 添加: {m.get('add_date', 'N/A')})")
        if len(test_managers) > 20:
            print(f"  ... 还有 {len(test_managers) - 20} 个")
        print()

    if real_managers:
        print("✅ 保留的真实经理：")
        print("-" * 60)
        for m in real_managers:
            print(f"  - {m['name']} ({m.get('company', 'N/A')})")
        print()

    return test_managers


def cleanup_test_data(dry_run=True):
    """
    清理测试数据

    Args:
        dry_run: True=仅预览，False=实际清理

    Returns:
        清理的测试数据列表
    """
    roster = read_json(ROSTER_PATH, default={"meta": {"count": 0}, "managers": []})
    managers = roster.get("managers", [])

    if not managers:
        log.info("名单为空，无需清理")
        return []

    test_managers = []
    real_managers = []

    for m in managers:
        if is_test_manager(m["name"]):
            test_managers.append(m)
        else:
            real_managers.append(m)

    if not test_managers:
        log.info("未发现测试数据")
        return []

    if dry_run:
        log.info(f"[预览] 发现 {len(test_managers)} 个测试数据，使用 --execute 实际清理")
        return test_managers

    # 实际清理
    log.info(f"开始清理 {len(test_managers)} 个测试数据...")

    # 1. 更新名单
    roster["managers"] = real_managers
    roster["meta"]["count"] = len(real_managers)
    write_json(ROSTER_PATH, roster)
    log.info(f"名单已更新：{len(real_managers)} 人")

    # 2. 删除测试经理的档案文件
    deleted_files = 0
    for m in test_managers:
        mgr_id = m["id"]
        safe_id = re.sub(r"[^\w\-]", "_", str(mgr_id))
        mgr_path = os.path.join(MANAGERS_DIR, f"{safe_id}.json")
        if os.path.exists(mgr_path):
            os.remove(mgr_path)
            deleted_files += 1

    log.info(f"已删除 {deleted_files} 个测试档案文件")

    print()
    print("=" * 60)
    print("✅ 清理完成！")
    print("=" * 60)
    print(f"清理测试数据：{len(test_managers)} 个")
    print(f"保留真实经理：{len(real_managers)} 个")
    print(f"删除档案文件：{deleted_files} 个")
    print(f"当前名额使用：{len(real_managers)}/100")
    print()

    return test_managers


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="清理名单中的测试数据")
    parser.add_argument("--execute", action="store_true", help="实际执行清理（默认仅预览）")
    parser.add_argument("--force", action="store_true", help="跳过确认提示")

    args = parser.parse_args()

    # 预览
    test_data = preview_cleanup()

    if not test_data:
        sys.exit(0)

    if not args.execute:
        print("\n💡 提示：添加 --execute 参数实际执行清理")
        print("   python scripts/cleanup_test_data.py --execute")
        sys.exit(0)

    # 确认
    if not args.force:
        print("\n⚠️  警告：此操作不可逆！")
        confirm = input("确认清理？(y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            sys.exit(0)

    # 执行清理
    cleanup_test_data(dry_run=False)
