#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
experiment-budget.py — 科研实验试剂耗材预算计算器
==================================================
用于"基于XXX技术对甘肃道地药材的鉴定与质量评价"类课题的预算估算。

功能：
  1. 内置损耗率默认值（可覆盖）
  2. 按类别（试剂/耗材/标准品/其他）汇总
  3. 输出 Markdown 表格 + 汇总 + 预留不可预见费

用法：
  python3 experiment-budget.py                # 运行内置示例
  python3 experiment-budget.py -f budget.json # 从 JSON 文件读取

JSON 输入格式（items 数组）：
[
  {
    "category": "试剂",            # 试剂/耗材/标准品/其他
    "name": "甲醇（色谱纯）",
    "spec": "4L/瓶",
    "unit_price": 120,             # 单价（元）
    "quantity": 6,                 # 所需数量（按单价单位）
    "loss_rate": 0.10,             # 损耗率（可选，默认按类别）
    "purpose": "流动相/提取"
  },
  ...
]
"""

import json
import sys
import argparse

# 类别损耗率默认值
DEFAULT_LOSS = {
    "试剂": 0.10,
    "耗材": 0.10,
    "标准品": 0.05,
    "其他": 0.05,
}

CATEGORIES = ["试剂", "耗材", "标准品", "其他"]

EXAMPLE_ITEMS = [
    {"category": "试剂", "name": "甲醇（色谱纯）", "spec": "4L/瓶", "unit_price": 120, "quantity": 6, "purpose": "流动相/提取"},
    {"category": "试剂", "name": "乙腈（色谱纯）", "spec": "4L/瓶", "unit_price": 180, "quantity": 4, "purpose": "流动相"},
    {"category": "试剂", "name": "水合氯醛", "spec": "500g", "unit_price": 45, "quantity": 1, "purpose": "显微制片"},
    {"category": "耗材", "name": "C18色谱柱", "spec": "250×4.6mm,5μm", "unit_price": 3200, "quantity": 2, "loss_rate": 0.0, "purpose": "HPLC分离（备用1支）"},
    {"category": "耗材", "name": "进样瓶+盖垫", "spec": "100个/包", "unit_price": 120, "quantity": 5, "purpose": "HPLC进样"},
    {"category": "耗材", "name": "0.45μm滤膜", "spec": "50片/盒", "unit_price": 80, "quantity": 4, "purpose": "样品过滤"},
    {"category": "标准品", "name": "阿魏酸对照品", "spec": "20mg", "unit_price": 260, "quantity": 1, "purpose": "含量测定"},
    {"category": "标准品", "name": "当归对照药材", "spec": "1g/支", "unit_price": 60, "quantity": 3, "purpose": "薄层/对照"},
    {"category": "标准品", "name": "DNA测序服务", "spec": "样/次", "unit_price": 60, "quantity": 60, "purpose": "条形码测序"},
    {"category": "其他", "name": "样品采集差旅", "spec": "趟", "unit_price": 1500, "quantity": 2, "purpose": "岷县等道地产区采样"},
    {"category": "其他", "name": "冷链运输", "spec": "次", "unit_price": 500, "quantity": 2, "purpose": "鲜品/样本回运"},
]


def parse_args():
    p = argparse.ArgumentParser(description="科研实验试剂耗材预算计算器")
    p.add_argument("-f", "--file", help="JSON 输入文件（可选）")
    p.add_argument("-c", "--contingency", type=float, default=0.08,
                   help="不可预见费比例，默认 8%%")
    return p.parse_args()


def load_items(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get("items", [])


def compute(items):
    """返回每项明细(含小计) 与 分类汇总、总计。"""
    rows = []
    for it in items:
        unit_price = float(it["unit_price"])
        quantity = float(it["quantity"])
        cat = it.get("category", "其他")
        if cat not in CATEGORIES:
            cat = "其他"
        loss = it.get("loss_rate", DEFAULT_LOSS[cat])
        subtotal = round(unit_price * quantity * (1 + loss), 2)
        rows.append({
            "category": cat,
            "name": it["name"],
            "spec": it.get("spec", ""),
            "unit_price": unit_price,
            "quantity": quantity,
            "loss": loss,
            "subtotal": subtotal,
            "purpose": it.get("purpose", ""),
        })
    summary = {c: round(sum(r["subtotal"] for r in rows if r["category"] == c), 2)
               for c in CATEGORIES}
    total = round(sum(summary.values()), 2)
    return rows, summary, total


def render_markdown(rows, summary, total, contingency):
    out = []
    out.append("## 试剂耗材预算清单")
    out.append("")
    for cat in CATEGORIES:
        cat_rows = [r for r in rows if r["category"] == cat]
        if not cat_rows:
            continue
        out.append(f"### {cat}类")
        out.append("")
        out.append("| 序号 | 名称 | 规格 | 单价(元) | 数量 | 损耗率 | 小计(元) | 用途 |")
        out.append("|------|------|------|----------|------|--------|----------|------|")
        for i, r in enumerate(cat_rows, 1):
            loss_pct = f"{r['loss']*100:.0f}%" if r["loss"] else "0%"
            qty = int(r["quantity"]) if r["quantity"] == int(r["quantity"]) else r["quantity"]
            price = int(r["unit_price"]) if r["unit_price"] == int(r["unit_price"]) else r["unit_price"]
            out.append(f"| {i} | {r['name']} | {r['spec']} | {price} | {qty} | {loss_pct} | {r['subtotal']:.2f} | {r['purpose']} |")
        out.append("")
    out.append("### 汇总")
    out.append("")
    out.append("| 类别 | 小计(元) | 占比 |")
    out.append("|------|----------|------|")
    for cat in CATEGORIES:
        v = summary[cat]
        pct = f"{v/total*100:.1f}%" if total else "-"
        out.append(f"| {cat} | {v:.2f} | {pct} |")
    out.append(f"| **总计** | **{total:.2f}** | 100% |")
    out.append("")
    contingency_amt = round(total * contingency, 2)
    grand = round(total + contingency_amt, 2)
    out.append(f"> 不可预见费（{contingency*100:.0f}%）：{contingency_amt:.2f} 元；**预算总额：{grand:.2f} 元**")
    out.append("> 说明：单价为参考市场价，实际以当期采购合同为准。")
    return "\n".join(out)


def main():
    args = parse_args()
    items = load_items(args.file) if args.file else EXAMPLE_ITEMS
    rows, summary, total = compute(items)
    print(render_markdown(rows, summary, total, args.contingency))


if __name__ == "__main__":
    main()
