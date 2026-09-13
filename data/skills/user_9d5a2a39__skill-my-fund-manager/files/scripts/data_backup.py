#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据备份与恢复工具（v2.0 新增）。

解决问题：
- 名单/档案/导出/进度等数据丢失
- 误删一个经理档案
- 设备迁移

使用：
    from data_backup import backup_all, restore_all
    backup_path = backup_all()  # → data/backups/skill_my_fund_manager_20260728_1200.zip
    restore_all(backup_path)    # 从备份恢复

CLI:
    python data_backup.py backup
    python data_backup.py restore data/backups/skill_my_fund_manager_20260728_1200.zip
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import zipfile
import argparse
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


# ============================================================
# 备份
# ============================================================

def backup_all(output_dir: str = None) -> str:
    """备份所有数据目录到 zip 文件。

    Args:
        output_dir: 输出目录（默认 data/backups/）

    Returns:
        str: 备份文件路径
    """
    import _common

    _common.ensure_dirs()

    if output_dir is None:
        output_dir = os.path.join(_common.DATA_DIR, "backups")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(output_dir, f"skill_backup_{timestamp}.zip")

    # 待备份目录：roster, managers, exports, change_log, progress
    backup_dirs = ["managers", "exports", "change_log", "progress"]
    backup_files = ["roster.json", "manager_index.json", "famous_managers_2025_2026.json"]

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        # 备份子目录
        for d in backup_dirs:
            full_dir = os.path.join(_common.DATA_DIR, d)
            if not os.path.isdir(full_dir):
                continue
            for f in os.listdir(full_dir):
                full = os.path.join(full_dir, f)
                if os.path.isfile(full):
                    zf.write(full, f"data/{d}/{f}")
                    print(f"  + {d}/{f}")

        # 备份顶层文件
        for f in backup_files:
            full = os.path.join(_common.DATA_DIR, f)
            if os.path.isfile(full):
                zf.write(full, f"data/{f}")
                print(f"  + {f}")

        # 添加 manifest
        manifest = {
            "backup_at": timestamp,
            "skill_name": "my-fund-manager",
            "skill_version": "2.0.2",
            "data_dirs_backed_up": backup_dirs,
            "data_files_backed_up": backup_files,
            "note": "解压到 data/ 目录覆盖即可恢复",
        }
        zf.writestr("MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    size = os.path.getsize(backup_path)
    print(f"\n✅ 备份完成: {backup_path} ({size/1024:.1f} KB)")
    return backup_path


# ============================================================
# 恢复
# ============================================================

def restore_all(backup_path: str, overwrite: bool = False) -> Dict:
    """从备份 zip 恢复所有数据。

    Args:
        backup_path: 备份 zip 路径
        overwrite: 是否覆盖现有数据（默认 False 安全模式）

    Returns:
        dict: 恢复结果
    """
    import _common
    p = Path(backup_path)
    if not p.exists():
        return {"success": False, "reason": f"备份文件不存在: {backup_path}"}

    _common.ensure_dirs()

    restored_files = 0
    skipped_files = 0

    with zipfile.ZipFile(backup_path, "r") as zf:
        names = zf.namelist()

        for name in names:
            if name == "MANIFEST.json":
                continue
            # 解压到 _common.DATA_DIR
            # zip 路径格式: "data/managers/xxx.json"
            if not name.startswith("data/"):
                continue
            rel_path = name[len("data/"):]
            target = _common.DATA_DIR + "/" + rel_path.replace("\\", "/")
            # 替换路径分隔符为本地系统的
            target = os.path.normpath(target)

            if os.path.exists(target) and not overwrite:
                skipped_files += 1
                continue

            # 确保父目录存在
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with zf.open(name) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
            restored_files += 1

    return {
        "success": True,
        "restored_files": restored_files,
        "skipped_files": skipped_files,
        "backup_path": backup_path,
    }


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="我的基金经理 - 数据备份与恢复")
    parser.add_argument("--action", choices=["backup", "restore", "list"], default="backup")
    parser.add_argument("path", nargs="?", help="restore 时为备份文件路径")

    args = parser.parse_args()

    if args.action == "backup":
        path = backup_all()
        print(f"备份文件：{path}")
    elif args.action == "restore":
        if not args.path:
            print("用法: data_backup.py restore <备份文件路径>")
            return 1
        result = restore_all(args.path, overwrite=True)
        if result["success"]:
            print(f"✅ 恢复完成：{result['restored_files']} 文件")
            if result["skipped_files"]:
                print(f"⚠️ 跳过：{result['skipped_files']} 文件已存在")
        else:
            print(f"❌ 失败：{result.get('reason', '未知错误')}")
    elif args.action == "list":
        import _common
        backup_dir = os.path.join(_common.DATA_DIR, "backups")
        if not os.path.isdir(backup_dir):
            print("📭 没有备份")
            return 0
        files = sorted(os.listdir(backup_dir), reverse=True)
        for f in files:
            if f.endswith(".zip"):
                full = os.path.join(backup_dir, f)
                print(f"  {f} ({os.path.getsize(full)/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
