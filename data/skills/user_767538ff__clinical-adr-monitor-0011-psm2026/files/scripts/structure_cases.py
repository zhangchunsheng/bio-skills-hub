#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
structure_cases.py —— 药品不良反应病例结构化与汇总统计

用途：
  将自由导出的 ADR 监测 Excel/CSV 解析为结构化记录，并自动完成
  汇总统计（总例数、新的/严重例数及占比、按药品/SOC/关联性/转归分布等），
  输出 JSON 与可读摘要，供季度/年度汇总报告直接引用，避免手工加总数错。

用法：
  python structure_cases.py <输入文件.csv|.xlsx> [--out 结果.json] [--top 10]
                          [--map 原始列=标准列,原始列=标准列 ...]

标准列名（可经 --map 映射你的实际表头）：
  case_id   报告编号
  drug      药品（通用名）
  adr       不良反应名称
  soc       SOC / 系统器官分类
  seriousness  严重程度（含"严重"即判为严重）
  is_new    是否新的（含"新"即判为新的）
  causality 关联性评价（肯定/很可能/可能/可能无关/待评价/无法评价）
  outcome   转归（治愈/好转/未好转/后遗症/死亡）
  dept      科室
  age       年龄
  gender    性别

说明：
  - CSV 优先按 utf-8-sig 读取，失败回退 gbk（兼容国内导出）。
  - .xlsx 需要 openpyxl；若未安装，请将文件另存为 CSV 后重试。
  - 仅做结构化与统计，不判断医学结论；"新的/严重"判定基于列内关键字。
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict


# 常见中文表头 -> 标准列名（不区分大小写、忽略空格与标点）
HEADER_ALIASES = {
    "case_id": ["报告编号", "编号", "id", "病例编号", "reportid", "报告id"],
    "drug": ["药品", "药品名称", "通用名", "怀疑药品", "药物", "药名", "drug", "medication"],
    "adr": ["不良反应", "反应名称", "不良反应名称", "adr", "ae", "不良事件"],
    "soc": ["soc", "系统器官", "系统器官分类", "器官分类"],
    "seriousness": ["严重程度", "严重", "是否严重", "serious"],
    "is_new": ["是否新的", "新的", "isnew", "新的一般或新的严重"],
    "causality": ["关联性", "关联性评价", "因果", "因果关系", "causality"],
    "outcome": ["转归", "结果", "结局", "outcome", "预后"],
    "dept": ["科室", "部门", "dept", "department"],
    "age": ["年龄", "age"],
    "gender": ["性别", "gender", "sex"],
}


def detect_columns(headers):
    """将原始表头映射到标准列名。"""
    norm = {h.strip().lower().replace(" ", ""): h for h in headers if h}
    mapping = {}
    for std, aliases in HEADER_ALIASES.items():
        for a in aliases:
            key = a.lower().replace(" ", "")
            if key in norm:
                mapping[std] = norm[key]
                break
    return mapping


def read_rows(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        # 先试 utf-8-sig，再试 gbk
        for enc in ("utf-8-sig", "gbk", "utf-8"):
            try:
                with open(path, "r", encoding=enc, newline="") as f:
                    reader = csv.DictReader(f)
                    rows = [dict(r) for r in reader]
                    if rows:
                        return rows
            except (UnicodeDecodeError, UnicodeError):
                continue
        raise ValueError("无法以 utf-8/gbk 解码该 CSV，请检查文件编码。")
    elif ext in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            sys.stderr.write("读取 .xlsx 需要 openpyxl，请先安装或将文件另存为 CSV。\n")
            raise
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        ws = wb.active
        rows_iter = ws.iter_rows(values_only=True)
        try:
            headers = [str(h) if h is not None else "" for h in next(rows_iter)]
        except StopIteration:
            return []
        out = []
        for r in rows_iter:
            if all(c is None for c in r):
                continue
            out.append({headers[i]: ("" if i >= len(r) or r[i] is None else str(r[i]))
                        for i in range(len(headers))})
        return out
    else:
        raise ValueError("不支持的文件类型：%s（仅支持 .csv / .xlsx）" % ext)


def norm_val(row, col):
    if not col:
        return ""
    v = row.get(col, "")
    return (v or "").strip()


def is_serious(v):
    return "严重" in v


def is_new(v):
    return "新" in v  # 含"新"字即视为新的（含新的一般/新的严重）


def pct(n, total):
    return round(100.0 * n / total, 1) if total else 0.0


def analyze(rows, mapping):
    get = lambda row, std: norm_val(row, mapping.get(std, ""))
    total = len(rows)
    serious = sum(1 for r in rows if is_serious(get(r, "seriousness")))
    new = sum(1 for r in rows if is_new(get(r, "is_new")))
    new_serious = sum(1 for r in rows
                      if is_new(get(r, "is_new")) and is_serious(get(r, "seriousness")))

    by_drug = Counter(get(r, "drug") or "（未填）" for r in rows)
    by_adr = Counter(get(r, "adr") or "（未填）" for r in rows)
    by_soc = Counter(get(r, "soc") or "（未填）" for r in rows)
    by_causality = Counter(get(r, "causality") or "（未填）" for r in rows)
    by_outcome = Counter(get(r, "outcome") or "（未填）" for r in rows)
    by_dept = Counter(get(r, "dept") or "（未填）" for r in rows)

    deaths = sum(1 for r in rows if "死亡" in get(r, "outcome"))

    return {
        "total": total,
        "serious": serious,
        "serious_pct": pct(serious, total),
        "new": new,
        "new_pct": pct(new, total),
        "new_serious": new_serious,
        "deaths": deaths,
        "by_drug": by_drug.most_common(),
        "by_adr": by_adr.most_common(),
        "by_soc": by_soc.most_common(),
        "by_causality": by_causality.most_common(),
        "by_outcome": by_outcome.most_common(),
        "by_dept": by_dept.most_common(),
    }


def render_md(stats, top):
    lines = []
    lines.append("# ADR 汇总统计（自动生成）")
    lines.append("")
    lines.append(f"- 总例数：**{stats['total']}**")
    lines.append(f"- 严重不良反应：**{stats['serious']}** 例（占 {stats['serious_pct']}%）")
    lines.append(f"- 新的不良反应：**{stats['new']}** 例（占 {stats['new_pct']}%）")
    lines.append(f"- 新的严重：**{stats['new_serious']}** 例")
    lines.append(f"- 死亡：**{stats['deaths']}** 例")
    lines.append("")

    def table(title, counter, n=top):
        lines.append(f"## {title}")
        lines.append("| 项目 | 例数 | 占比 |")
        lines.append("|------|------|------|")
        for k, v in counter[:n]:
            lines.append(f"| {k} | {v} | {pct(v, stats['total'])}% |")
        lines.append("")

    table(f"按药品分布（Top {top}）", stats["by_drug"])
    table(f"按不良反应分布（Top {top}）", stats["by_adr"])
    table("按 SOC 分布", stats["by_soc"])
    table("按关联性评价分布", stats["by_causality"])
    table("按转归分布", stats["by_outcome"])
    table(f"按科室分布（Top {top}）", stats["by_dept"])
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="ADR 病例结构化与汇总统计")
    ap.add_argument("input", help="输入 .csv 或 .xlsx 文件")
    ap.add_argument("--out", help="输出 JSON 路径（可选）")
    ap.add_argument("--top", type=int, default=10, help="Top N 展示数量（默认 10）")
    ap.add_argument("--map", help="列映射，如 '药品名称=drug,反应=adr'")
    args = ap.parse_args()

    rows = read_rows(args.input)
    headers = list(rows[0].keys()) if rows else []
    mapping = detect_columns(headers)

    if args.map:
        for pair in args.map.split(","):
            if "=" not in pair:
                continue
            src, std = pair.split("=", 1)
            src, std = src.strip(), std.strip()
            if std in HEADER_ALIASES and src in headers:
                mapping[std] = src

    if not mapping:
        sys.stderr.write("未识别到任何标准列，请用 --map 指定，例如 --map 药品名称=drug,不良反应=adr\n")
        sys.stderr.write("识别到的表头：%s\n" % headers)
        sys.exit(2)

    stats = analyze(rows, mapping)
    print(render_md(stats, args.top))

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"mapping": mapping, "stats": stats}, f,
                      ensure_ascii=False, indent=2)
        print(f"\n[已写入 JSON：{args.out}]")


if __name__ == "__main__":
    main()
