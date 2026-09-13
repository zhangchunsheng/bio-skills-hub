#!/usr/bin/env python3
"""
wechat-suite 部署脚本
把本 skill 内置的 skills/ 目录下所有含 SKILL.md 的 skill 复制到用户的 skills 目录。
按每个 skill 自身 frontmatter 的 name 作为落盘目录名（正确处理嵌套 skill，如 xiaohu-wechat-cover）。
"""
import os
import re
import sys
import shutil
from pathlib import Path

HOME = Path.home()
CANDIDATES = [
    HOME / ".workbuddy" / "skills",
    HOME / ".codebuddy" / "skills",
]

SELF_DIR = Path(__file__).resolve().parent
SOURCE_DIR = SELF_DIR.parent / "skills"


def find_target() -> Path:
    for c in CANDIDATES:
        if c.exists():
            return c
    target = CANDIDATES[0]
    target.mkdir(parents=True, exist_ok=True)
    return target


def skill_name_from_frontmatter(skill_md: Path) -> str:
    try:
        text = skill_md.read_text(encoding="utf-8")
    except Exception:
        return None
    m = re.search(r'^name:\s*(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip().strip('"').strip("'")
    return None


def main():
    if not SOURCE_DIR.exists():
        print(f"❌ 找不到内置 skills 目录: {SOURCE_DIR}")
        sys.exit(1)

    target = find_target()
    print(f"📦 目标 skills 目录: {target}\n")

    # 递归找出所有含 SKILL.md 的目录
    skill_dirs = sorted({p.parent for p in SOURCE_DIR.rglob("SKILL.md")})
    if not skill_dirs:
        print("⚠️  内置 skills 目录为空，没有可部署的 skill。")
        sys.exit(1)

    ok, skip, fail = 0, 0, 0
    for d in skill_dirs:
        name = skill_name_from_frontmatter(d / "SKILL.md") or d.name
        dest = target / name
        if dest.exists():
            print(f"⏭️  已存在，跳过: {name}")
            skip += 1
            continue
        try:
            shutil.copytree(d, dest)
            print(f"✅ 已部署: {name}")
            ok += 1
        except Exception as e:
            print(f"❌ 部署失败: {name} — {e}")
            fail += 1

    print(f"\n完成：成功 {ok} 个，跳过 {skip} 个，失败 {fail} 个")
    print("重启 WorkBuddy 后，全部公众号写作 skill 即可在列表中看到并直接使用。")


if __name__ == "__main__":
    main()
