#!/usr/bin/env python3
"""Structural checks for viral-structure-decoder reports."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED = [
    ("速览", re.compile(r"⚡|结构速览|DNA 速览|快速 DNA")),
    ("分类或培训", re.compile(r"分类|🔍|打钩|辨识|培训")),
    ("边界", re.compile(r"不代笔|不保证|版权|边界|学结构")),
]

REQUIRED_FULL = [
    ("钩子", re.compile(r"钩子|🎣")),
    ("DNA一句", re.compile(r"DNA一句|🧬")),
    ("五维或扫描", re.compile(r"五维扫描|钩子✓")),
    ("说服", re.compile(r"说服|技巧|🎯")),
    ("弱点", re.compile(r"弱点|🔧|若改")),
    ("表面或深层", re.compile(r"表面|深层|不要只学")),
    ("迁移或自检", re.compile(r"迁移度|发布前自检")),
    ("蓝图空槽", re.compile(r"___|空槽")),
]

FORBIDDEN = [
    ("保证爆款", re.compile(r"必爆|保证上热门|播放量肯定")),
    ("刷量教唆", re.compile(r"刷赞|买热评|控评水军")),
]


def strip_anti(text: str) -> str:
    return re.split(r"\n##\s*反例|\n##\s*常见翻车", text, maxsplit=1)[0]


def validate(text: str, mode: str) -> list[str]:
    errors: list[str] = []
    if not text.strip():
        return ["empty report"]
    body = strip_anti(text)
    for name, pat in REQUIRED:
        if mode == "train" and name == "速览":
            # train mode may skip full scan card
            if not re.search(r"⚡|结构速览|DNA|打钩", body):
                errors.append(f"missing: {name}")
            continue
        if not pat.search(body):
            errors.append(f"missing: {name}")
    if mode == "full":
        for name, pat in REQUIRED_FULL:
            if not pat.search(body):
                errors.append(f"missing: {name}")
    elif mode == "quick":
        if not re.search(r"钩子|🎣", body):
            errors.append("missing: 钩子")
        if not re.search(r"蓝图|___|空槽", body):
            errors.append("missing: 蓝图")
    elif mode == "train":
        if not re.search(r"打钩|辨识", body):
            errors.append("missing: 培训结构")
    for name, pat in FORBIDDEN:
        if pat.search(body):
            # allow in 反例 / 禁止 contexts already stripped; also allow 不保证爆款
            if name == "保证爆款" and re.search(r"不保证|禁止|勿|不要", body):
                # only flag assertive 必爆 without 不
                if re.search(r"(?<!不)必爆|(?<!不)保证上热门", body):
                    errors.append(f"forbidden: {name}")
            else:
                errors.append(f"forbidden: {name}")
    return errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("report", type=Path)
    p.add_argument("--mode", choices=("full", "quick", "train", "auto"), default="auto")
    args = p.parse_args()
    text = args.report.read_text(encoding="utf-8")
    mode = args.mode
    if mode == "auto":
        if re.search(r"培训|辨识题|新人五维", text[:500]):
            mode = "train"
        elif re.search(r"快速 DNA|DNA 速览|蓝图骨架", text[:400]):
            mode = "quick"
        else:
            mode = "full"
    errs = validate(text, mode)
    for e in errs:
        print(f"ERR: {e}")
    if errs:
        return 1
    print(f"OK mode={mode}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
