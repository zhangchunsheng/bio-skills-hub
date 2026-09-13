#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cleanroom-cost-settlement 程序化生成器
--------------------------------------
从一份 JSON 项目简述生成 4 类脱敏交付物：
  1. 结算资料策划清单  (plan)
  2. 量价核对表        (reconcile)
  3. 变更签证计价表    (variation)
  4. 成本数据库沉淀表  (database)

用法：
  python3 generate.py --demo --out output_demo
  python3 generate.py --spec my_project.json --out output
  python3 generate.py --validate my_project.json

全部金额/单价以区间或 0 占位输出，严格脱敏（不写真实成交价/商号/联系人）。
"""

import argparse
import json
import os
import sys


def load_spec(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate(spec):
    errors = []
    if "project" not in spec:
        errors.append("缺少 project 字段")
    if "reconcile" in spec:
        for i, r in enumerate(spec["reconcile"].get("rows", [])):
            for k in ("trade", "name", "unit", "actual_qty"):
                if k not in r:
                    errors.append(f"reconcile.rows[{i}] 缺字段 {k}")
    if "variation" in spec:
        for i, r in enumerate(spec["variation"].get("rows", [])):
            for k in ("no", "item", "qty", "unit"):
                if k not in r:
                    errors.append(f"variation.rows[{i}] 缺字段 {k}")
            basis = r.get("basis", "")
            if basis and basis not in ("合同单价", "类似单价", "市场价", "信息价", "组价"):
                errors.append(f"variation.rows[{i}] basis 不在允许口径: {basis}")
    if "database" in spec:
        for i, r in enumerate(spec["database"].get("rows", [])):
            for k in ("trade", "name", "unit"):
                if k not in r:
                    errors.append(f"database.rows[{i}] 缺字段 {k}")
    return errors


def gen_plan(spec):
    p = spec.get("project", {})
    return f"""# 结算资料策划清单

> 自动生成（脱敏示范）。提供部门均为通用部门名。

## 项目基本信息

| 项 | 内容 |
|----|------|
| 项目名称 | {p.get('name','某X级医院净化项目')} |
| 项目编号 | {p.get('code','PRJ-001')} |
| 清单编制日 | {p.get('date','YYYY-MM-DD')} |

## 资料需求清单（按类别 + 提供部门）

| # | 资料类别 | 具体资料 | 提供部门 | 状态 |
|---|---------|---------|---------|------|
| 1 | 合同类 | 施工合同及补充协议 | 成本部 | ☐ |
| 2 | 合同类 | 中标通知书 | 成本部 | ☐ |
| 3 | 图纸BOM类 | 施工图（三版） | 工程部/资料部门 | ☐ |
| 4 | 图纸BOM类 | BOM（三版及量差） | 成本部 | ☐ |
| 5 | 采购类 | 采购合同（含协议价） | 采购部 | ☐ |
| 6 | 采购类 | 到货签收/验收记录 | 采购部 | ☐ |
| 7 | 采购类 | 付款/质保金台账 | 采购部 | ☐ |
| 8 | 变更签证类 | 设计变更单（签字版） | 工程部 | ☐ |
| 9 | 变更签证类 | 现场签证单 | 工程部 | ☐ |
| 10 | 隐蔽验收类 | 隐蔽工程验收记录 | 工程部/资料部门 | ☐ |
| 11 | 检测类 | 检测报告（CMA/CNAS） | 资料部门 | ☐ |
| 12 | 竣工图类 | 竣工图（含变更标注） | 资料部门 | ☐ |
| 13 | 竣工图类 | 资料组卷目录 | 资料部门 | ☐ |

> 高风险缺项：隐蔽验收记录、变更签字版、合格证原件、检测报告——建议施工过程预归档。
"""


def gen_reconcile(spec):
    rows = spec.get("reconcile", {}).get("rows", [])
    lines = ["| # | 专业 | 名称 | 单位 | 合同量 | 设计量 | 清单量 | 实际量 | 量差 | 量差成因 | 合同单价(区间) |",
             "|---|------|------|------|-------|-------|-------|-------|------|---------|--------------|"]
    for i, r in enumerate(rows, 1):
        c = r.get("contract_qty", 0); d = r.get("design_qty", 0)
        b = r.get("boq_qty", 0); a = r.get("actual_qty", 0)
        diff = a - c
        lines.append(f"| {i} | {r.get('trade','')} | {r.get('name','')} | {r.get('unit','')} | "
                     f"{c} | {d} | {b} | {a} | {diff:+d} | {r.get('cause','')} | {r.get('contract_price',0)} |")
    return ("# 量价核对表\n\n> 自动生成（脱敏：单价为区间/0占位）。\n\n"
            "## 量价核对明细\n\n" + "\n".join(lines) +
            "\n\n> 量基准：BOM V3 净用量+签证；价基准：合同价/协议价；量差按 设计/施工/供应 三分因。\n")


def gen_variation(spec):
    rows = spec.get("variation", {}).get("rows", [])
    lines = ["| # | 签证号 | 项目 | 单位 | 量 | 单价(区间) | 计价口径 | 时效内 | 影像/验收 |",
             "|---|-------|------|------|---|-----------|---------|-------|----------|"]
    for i, r in enumerate(rows, 1):
        lines.append(f"| {i} | {r.get('no','')} | {r.get('item','')} | {r.get('unit','')} | "
                     f"{r.get('qty',0)} | {r.get('price',0)} | {r.get('basis','')} | "
                     f"{'是' if r.get('timely',True) else '否'} | {'是' if r.get('evidence',True) else '否'} |")
    return ("# 变更签证计价表\n\n> 自动生成（脱敏：单价为区间/0占位）。\n\n"
            "## 变更签证汇总\n\n" + "\n".join(lines) +
            "\n\n> 计价口径：合同单价 → 类似单价 → 市场价 → 信息价 → 组价。隐蔽项须有验收记录+影像。\n")


def gen_database(spec):
    rows = spec.get("database", {}).get("rows", [])
    lines = ["| 专业 | 材料/设备 | 单位 | 结算单价区间 | 档次 | 实际损耗率 |",
             "|------|----------|------|------------|------|-----------|"]
    for r in rows:
        loss = r.get("actual_loss", "")
        loss_s = f"{loss*100:.0f}%" if isinstance(loss, (int, float)) else str(loss)
        lines.append(f"| {r.get('trade','')} | {r.get('name','')} | {r.get('unit','')} | "
                     f"{r.get('settle_price_range','')} | {r.get('tier','')} | {loss_s} |")
    return ("# 成本数据库沉淀表\n\n> 自动生成（脱敏：单价/损耗为区间与档次）。\n\n"
            "## 结算单价区间（脱敏）\n\n" + "\n".join(lines) +
            "\n\n> 每项目回填即校准一次；单价/损耗脱敏为区间与档次，不承载商号与成交价。\n")


def gen_demo():
    return {
        "project": {"name": "某三甲医院洁净手术部项目", "code": "PRJ-001", "date": "2026-07-20"},
        "baseline": {"contract_price": 0, "target_cost": 0, "planned_margin": 0,
                     "trade_split": {"暖通": 0.30, "医疗设备": 0.25, "装饰": 0.18,
                                     "电气": 0.12, "给排水": 0.07, "医气": 0.08}},
        "reconcile": {"rows": [
            {"trade": "暖通", "name": "净化空调机组", "unit": "台", "contract_qty": 2,
             "design_qty": 2, "boq_qty": 2, "actual_qty": 2, "cause": "—", "contract_price": 0},
            {"trade": "电气", "name": "阻燃线缆", "unit": "米", "contract_qty": 3000,
             "design_qty": 3050, "boq_qty": 3000, "actual_qty": 3250, "cause": "施工损耗", "contract_price": 0},
        ]},
        "variation": {"rows": [
            {"no": "V-001", "item": "风管变更", "qty": 120, "unit": "㎡", "price": 0,
             "basis": "合同单价", "timely": True, "evidence": True},
            {"no": "V-002", "item": "增加风口", "qty": 8, "unit": "个", "price": 0,
             "basis": "类似单价", "timely": True, "evidence": True},
        ]},
        "database": {"rows": [
            {"trade": "电气", "name": "阻燃线缆", "unit": "米", "settle_price_range": "区间C–D",
             "tier": "国产一线/二线", "actual_loss": 0.04},
            {"trade": "装饰", "name": "装饰面板", "unit": "㎡", "settle_price_range": "区间E–F",
             "tier": "国产一线/二线", "actual_loss": 0.06},
        ]},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="生成脱敏示例")
    ap.add_argument("--spec", help="项目 JSON 路径")
    ap.add_argument("--out", default="output", help="输出目录")
    ap.add_argument("--validate", help="仅校验 spec 合法性")
    args = ap.parse_args()

    if args.validate:
        spec = load_spec(args.validate)
        errs = validate(spec)
        if errs:
            print("校验失败:")
            for e in errs:
                print("  -", e)
            sys.exit(1)
        print("校验通过")
        return

    spec = gen_demo() if args.demo else load_spec(args.spec)
    if not args.demo:
        errs = validate(spec)
        if errs:
            print("spec 校验失败，中止生成:")
            for e in errs:
                print("  -", e)
            sys.exit(1)

    os.makedirs(args.out, exist_ok=True)
    files = {
        "结算资料策划清单.md": gen_plan(spec),
        "量价核对表.md": gen_reconcile(spec),
        "变更签证计价表.md": gen_variation(spec),
        "成本数据库沉淀表.md": gen_database(spec),
    }
    for fn, content in files.items():
        with open(os.path.join(args.out, fn), "w", encoding="utf-8") as f:
            f.write(content)
    print(f"已生成 {len(files)} 个文件到 {args.out}/")


if __name__ == "__main__":
    main()
