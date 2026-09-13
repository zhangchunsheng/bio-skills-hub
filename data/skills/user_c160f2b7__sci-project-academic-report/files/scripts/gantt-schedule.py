#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gantt-schedule.py — 课题进度甘特图生成器（文本版）
====================================================
用于"基于XXX技术对甘肃道地药材的鉴定与质量评价"类课题的进度计划。

功能：
  1. 按月输出文本甘特图（默认18个月，里程碑◆标记）
  2. 输出里程碑表与风险预警提示
  3. 支持 JSON 配置自定义阶段/时长/里程碑

用法：
  python3 gantt-schedule.py                  # 内置示例（18个月）
  python3 gantt-schedule.py -f schedule.json # 从 JSON 读取
  python3 gantt-schedule.py -m 24            # 自定义总月数

JSON 输入格式：
{
  "total_months": 18,
  "title": "基于DNA条形码技术对当归的鉴定与质量评价 进度计划",
  "phases": [
    {"name": "文献调研", "start": 1, "duration": 2},
    {"name": "方案审批", "start": 3, "duration": 1},
    {"name": "样品采集", "start": 4, "duration": 2, "milestone": 5},
    ...
  ],
  "milestones": [["M3 样品采集完成", 5], ...]
}
"""

import json
import argparse

DEFAULT_TITLE = "课题进度计划（甘特图风格）"

EXAMPLE = {
    "total_months": 18,
    "title": "基于DNA条形码技术对甘肃道地药材当归及其混伪品的鉴定与质量评价 —— 进度计划",
    "phases": [
        {"name": "文献调研", "start": 1, "duration": 2},
        {"name": "方案定稿+审批", "start": 3, "duration": 1, "milestone": 3},
        {"name": "样品采集（采收季）", "start": 4, "duration": 2, "milestone": 5},
        {"name": "方法建立与预实验", "start": 6, "duration": 3},
        {"name": "样品测定", "start": 9, "duration": 4},
        {"name": "数据分析", "start": 13, "duration": 2},
        {"name": "论文撰写", "start": 15, "duration": 2, "milestone": 16},
        {"name": "预答辩", "start": 17, "duration": 1, "milestone": 17},
        {"name": "修改定稿", "start": 18, "duration": 1},
        {"name": "正式答辩", "start": 18, "duration": 1, "milestone": 18},
    ],
    "milestones": [
        ["M3 样品采集完成（秋末采收前）", 5],
        ["M5 样品测定完成", 12],
        ["M8 预答辩通过", 17],
        ["M9 正式答辩通过", 18],
    ],
    "warnings": [
        "样品采集必须前置于方法建立之前（10月底采收季），错过需等一年",
        "HPLC/UPLC-MS 仪器共享需提前2周预约，批量测定与预实验错峰",
        "进口标准品/引物采购周期2-4周，建议提前备货",
        "方法学验证返工风险预留2-4周缓冲",
    ],
}


def parse_args():
    p = argparse.ArgumentParser(description="课题进度甘特图生成器（文本版）")
    p.add_argument("-f", "--file", help="JSON 配置文件（可选）")
    p.add_argument("-m", "--months", type=int, default=18, help="总月数（默认18）")
    return p.parse_args()


def load_config(path, months):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("total_months", months)
    data.setdefault("title", DEFAULT_TITLE)
    data.setdefault("milestones", [])
    data.setdefault("warnings", [])
    return data


def render_gantt(cfg):
    total = cfg["total_months"]
    name_width = max(len(p["name"]) for p in cfg["phases"]) + 1
    out = []
    out.append(f"# {cfg.get('title', DEFAULT_TITLE)}")
    out.append("")
    # 月份表头
    header_nums = "".join(f"{str(m):>3}" for m in range(1, total + 1))
    out.append(f"{'阶段':<{name_width}}  {header_nums}")
    for p in cfg["phases"]:
        start = p["start"]
        dur = p["duration"]
        cells = ["   " for _ in range(total)]
        for i in range(start - 1, min(start - 1 + dur, total)):
            cells[i] = " █ "
        line = "".join(cells)
        # 里程碑标记
        if p.get("milestone"):
            idx = p["milestone"] - 1
            line = line[:idx * 3] + " ◆ " + line[idx * 3 + 3:]
        out.append(f"{p['name']:<{name_width}}  {line}")
    out.append("")
    # 里程碑表
    out.append("## 关键里程碑")
    out.append("")
    out.append("| 里程碑 | 建议完成月份 |")
    out.append("|--------|--------------|")
    for name, m in cfg["milestones"]:
        out.append(f"| {name} | 第{m}月 |")
    out.append("")
    # 风险预警
    if cfg["warnings"]:
        out.append("## 风险预警与调整策略")
        out.append("")
        for i, w in enumerate(cfg["warnings"], 1):
            out.append(f"{i}. {w}")
        out.append("")
    return "\n".join(out)


def main():
    args = parse_args()
    cfg = load_config(args.file, args.months) if args.file else EXAMPLE
    print(render_gantt(cfg))


if __name__ == "__main__":
    main()
