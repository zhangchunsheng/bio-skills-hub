"""
缓存清理工具
清理 Python 字节码、pytest 缓存等临时文件。
定期运行可保持项目目录干净。
"""

import os
import sys
import shutil
from pathlib import Path

# 项目根目录
SKILL_ROOT = Path(__file__).parent.parent

# 需要清理的目录模式
CACHE_DIRS = [
    "__pycache__",
    ".pytest_cache",
    ".cache",
    "htmlcov",
]

# 需要清理的文件扩展名
CACHE_EXTENSIONS = [
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".egg-info",
]


def find_and_remove_dirs(root, patterns):
    """查找并删除匹配的目录"""
    removed = []
    for dirpath, dirnames, filenames in os.walk(root):
        for dirname in dirnames:
            if dirname in patterns:
                full_path = os.path.join(dirpath, dirname)
                try:
                    shutil.rmtree(full_path)
                    removed.append(full_path)
                except Exception as e:
                    print(f"  ⚠️ 无法删除 {full_path}: {e}")
    return removed


def find_and_remove_files(root, extensions):
    """查找并删除匹配的文件"""
    removed = []
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                full_path = os.path.join(dirpath, filename)
                try:
                    os.remove(full_path)
                    removed.append(full_path)
                except Exception as e:
                    print(f"  ⚠️ 无法删除 {full_path}: {e}")
    return removed


def cleanup_cache(dry_run=False):
    """清理缓存文件"""
    print("=" * 60)
    print("🧹 缓存清理工具")
    print("=" * 60)
    print(f"项目目录: {SKILL_ROOT}")
    print()

    if dry_run:
        print("📋 预览模式（不实际删除）")
        print()

    # 查找并删除目录
    print("🔍 查找缓存目录...")
    dirs_to_remove = []
    for dirpath, dirnames, filenames in os.walk(SKILL_ROOT):
        for dirname in dirnames:
            if dirname in CACHE_DIRS:
                full_path = os.path.join(dirpath, dirname)
                dirs_to_remove.append(full_path)

    if dirs_to_remove:
        print(f"  找到 {len(dirs_to_remove)} 个缓存目录:")
        for d in dirs_to_remove:
            print(f"    - {os.path.relpath(d, SKILL_ROOT)}")
        if not dry_run:
            for d in dirs_to_remove:
                try:
                    shutil.rmtree(d)
                    print(f"    ✅ 已删除: {os.path.relpath(d, SKILL_ROOT)}")
                except Exception as e:
                    print(f"    ❌ 删除失败: {e}")
    else:
        print("  ✅ 未找到缓存目录")

    print()

    # 查找并删除文件
    print("🔍 查找缓存文件...")
    files_to_remove = []
    for dirpath, dirnames, filenames in os.walk(SKILL_ROOT):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in CACHE_EXTENSIONS):
                full_path = os.path.join(dirpath, filename)
                files_to_remove.append(full_path)

    if files_to_remove:
        print(f"  找到 {len(files_to_remove)} 个缓存文件:")
        for f in files_to_remove[:10]:  # 只显示前10个
            print(f"    - {os.path.relpath(f, SKILL_ROOT)}")
        if len(files_to_remove) > 10:
            print(f"    ... 还有 {len(files_to_remove) - 10} 个")
        if not dry_run:
            for f in files_to_remove:
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"    ❌ 删除失败: {e}")
            print(f"    ✅ 已删除 {len(files_to_remove)} 个文件")
    else:
        print("  ✅ 未找到缓存文件")

    print()

    # 统计结果
    total_removed = len(dirs_to_remove) + len(files_to_remove)
    if dry_run:
        print(f"📊 预览完成: 发现 {total_removed} 个可清理项")
        print(f"   使用 --execute 参数实际执行清理")
    else:
        print(f"✅ 清理完成: 删除 {total_removed} 个缓存项")

    return total_removed


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="清理项目缓存文件")
    parser.add_argument("--execute", action="store_true", help="实际执行清理（默认仅预览）")
    parser.add_argument("--quiet", action="store_true", help="静默模式")

    args = parser.parse_args()

    if args.quiet:
        # 静默模式，直接清理
        cleanup_cache(dry_run=False)
    else:
        # 交互模式
        cleanup_cache(dry_run=not args.execute)
