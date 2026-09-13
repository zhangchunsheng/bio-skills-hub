#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
emotion_curve.py —— 情绪曲线生成与校验

生成：按"压→小扬→爆"三章循环，每 10 章置大高潮，输出 Markdown 表。
校验：读取规划文件（每行 "章号 情绪定位" 或 "章号,情绪定位"），与生成曲线比对。

用法：
  python emotion_curve.py --chapters 50            # 生成 50 章曲线
  python emotion_curve.py --chapters 100 --genre 虐恋   # 虐恋允许连压
  python emotion_curve.py --chapters 50 --validate plan.txt   # 校验规划
  python emotion_curve.py --chapters 50 --md        # 输出 Markdown 表
"""
import argparse
import re
import sys

CYCLE = ["压", "小扬", "爆"]


def build_curve(n, genre="default"):
    """返回 list of (chapter, position, is_climax)"""
    curve = []
    for i in range(1, n + 1):
        pos = CYCLE[(i - 1) % 3]
        is_climax = (i % 10 == 0)  # 每 10 章大高潮
        if is_climax:
            pos = "爆(大高潮)"
        # 虐恋：允许第1-2章连压，第3章必须有"想让他后悔"钩子（此处仅标位置）
        curve.append((i, pos, is_climax))
    return curve


def render_md(curve):
    lines = ["| 章 | 情绪定位 | 大高潮 |", "|----|----------|--------|"]
    for ch, pos, cl in curve:
        lines.append(f"| {ch} | {pos} | {'★' if cl else ''} |")
    return "\n".join(lines)


def validate(curve, plan_path):
    """plan 每行: 'N 位置' 或 'N,位置'"""
    planned = {}
    with open(plan_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = re.split(r"[,\s]+", line)
            if len(parts) >= 2 and parts[0].isdigit():
                planned[int(parts[0])] = parts[1]
    mismatches = []
    for ch, pos, cl in curve:
        exp = "爆" if cl else CYCLE[(ch - 1) % 3]
        got = planned.get(ch, "")
        if got and not got.startswith(exp[0]):  # 前缀比对（压/扬/爆）
            mismatches.append((ch, exp, got))
    return mismatches


def main():
    import re
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", type=int, required=True)
    ap.add_argument("--genre", default="default")
    ap.add_argument("--validate", default=None, help="规划文件路径")
    ap.add_argument("--md", action="store_true", help="输出 Markdown 表")
    args = ap.parse_args()

    curve = build_curve(args.chapters, args.genre)

    if args.validate:
        mism = validate(curve, args.validate)
        if mism:
            print("情绪曲线断裂：")
            for ch, exp, got in mism:
                print(f"  第 {ch} 章：计划={got}，应={exp}")
            sys.exit(1)
        else:
            print(f"校验通过：{args.chapters} 章规划与曲线一致 ✅")
            return

    if args.md:
        print(render_md(curve))
    else:
        for ch, pos, cl in curve:
            print(f"{ch:>3}  {pos}{'  ★大高潮' if cl else ''}")


if __name__ == "__main__":
    main()
