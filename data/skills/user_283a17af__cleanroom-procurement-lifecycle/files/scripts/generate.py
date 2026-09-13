#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医疗净化采购全生命周期 · 文档生成器

从一份 JSON 项目简述生成 4 类交付物（markdown）：
  1. 采购申请单
  2. BOM 拆解表
  3. 供应商比价矩阵
  4. 成本估算框架

全程脱敏：不要求也不保留真实供应商名/合同价/内部额度；档次用
「国产一线/二线/进口高端」等通用口径。

用法：
  python generate.py --demo            # 生成示例到 ./output_demo
  python generate.py --spec s.json --out out_dir   # 从 spec 生成
  python generate.py --validate s.json # 仅校验 spec 合法性

仅依赖 Python 标准库。
"""

import argparse
import json
import os
import sys
from datetime import date


# ---------------------------------------------------------------------------
# 校验
# ---------------------------------------------------------------------------
def validate_spec(spec):
    """校验必需字段，返回错误信息列表（中文友好提示）。"""
    errs = []
    if not isinstance(spec, dict):
        return ["❌ spec 顶层必须是 JSON 对象（花括号 {} 包裹），请检查文件格式"]
    if "project" not in spec:
        errs.append("❌ 缺少 project 段，至少需要 {\"name\": \"项目名\", \"code\": \"编号\"}")
    else:
        p = spec["project"]
        if not p.get("name"):
            errs.append("⚠️ project.name 为空，建议填写脱敏项目名称（如「某三甲医院洁净手术部项目」）")
    if "application" in spec:
        app = spec["application"]
        if not isinstance(app, dict):
            errs.append("❌ application 段必须是 JSON 对象")
        else:
            for i, it in enumerate(app.get("items", [])):
                prefix = f"application.items[{i}]（{it.get('name', '未命名')}）"
                if not it.get("name"):
                    errs.append(f"❌ {prefix} 缺少 name（材料/设备名称）")
                if not it.get("unit"):
                    errs.append(f"❌ {prefix} 缺少 unit（单位，如：台/米/套/批）")
                try:
                    q = float(it.get("qty", 0) or 0)
                    if q < 0:
                        errs.append(f"⚠️ {prefix} qty={q} 为负数，数量不能为负")
                except (TypeError, ValueError):
                    errs.append(f"❌ {prefix} qty 不是有效数字（当前值：{it.get('qty', '')}），请填数字如 2 或 120")
                # 兼容英文字段名 price
                price_val = it.get("price", it.get("Price", it.get("PRICE", 0)))
                try:
                    float(price_val or 0)
                except (TypeError, ValueError):
                    errs.append(f"⚠️ {prefix} price 不是有效数字（当前值：{price_val}），金额填 0 或实际数均可")
    if "compare" in spec:
        cmp = spec["compare"]
        w = cmp.get("weights", {})
        if not w:
            errs.append("⚠️ compare.weights 为空，将使用默认权重生成比价矩阵")
        else:
            try:
                total = sum(float(v) for v in w.values())
            except (TypeError, ValueError):
                errs.append(f"❌ compare.weights 的值必须都是数字")
                total = 0
            if abs(total - 1.0) > 0.01 and abs(total - 100.0) > 1.0:
                errs.append(f"❌ compare.weights 权重之和应为 1.0（或 100），当前各权重加起来是 {total:.2f}。请检查是否漏了某个维度或小数点写错")
            elif abs(total - 100.0) <= 1.0:
                errs.append(f"💡 提示：你填的权重之和是 {total:.0f}（按百分制），程序会自动按比例折算成 1.0 使用")
            for s in cmp.get("suppliers", []):
                sname = s.get("name", f"供应商#{cmp.get('suppliers',[]).index(s)+1}")
                scores = s.get("scores", {})
                if not scores:
                    errs.append(f"⚠️ 供应商「{sname}」没有打分数据（scores 为空），比价时该项全按 0 分计算")
                else:
                    miss = [d for d in w if d not in scores]
                    if miss:
                        errs.append(f"⚠️ 供应商「{sname}」缺少以下维度的打分：{miss}。缺的维度按 0 分参与加权计算")
    if "cost" in spec:
        cost = spec["cost"]
        for i, r in enumerate(cost.get("rows", [])):
            trade = r.get("trade", f"专业#{i}")
            for k in ("device", "material", "install", "tax"):
                val = r.get(k, 0)
                try:
                    v = float(val or 0)
                    if v < 0:
                        errs.append(f"⚠️ cost.rows[{i}]({trade}).{k}={v} 为负数")
                except (TypeError, ValueError):
                    errs.append(f"❌ cost.rows[{i}]({trade}).{k} 不是有效数字（当前值：{val}），请填数字")
    return errs


# ---------------------------------------------------------------------------
# 渲染
# ---------------------------------------------------------------------------
def _money(x):
    try:
        return f"{float(x):,.2f}"
    except (TypeError, ValueError):
        return str(x)


def render_application(project, app):
    lines = ["# 采购申请单（医疗净化工程）", "",
             "> 由 cleanroom-procurement-lifecycle 技能生成（脱敏）", ""]
    lines += ["## 项目基本信息", "| 项 | 内容 |", "|----|------|",
              f"| 项目名称（脱敏） | {project.get('name','—')} |",
              f"| 项目编号 | {project.get('code','—')} |",
              f"| 申请日期 | {app.get('date', date.today().isoformat())} |",
              f"| 申请专业 | {app.get('trade','—')} |",
              f"| 采购方式 | {app.get('method','—')} |",
              f"| 进场节点 | {app.get('node','—')} |", ""]
    lines += ["## 采购明细",
              "| 序号 | 材料/设备名称 | 规格型号 | 单位 | 数量 | 品牌档 | 估算单价(元) | 估算金额(元) | 进场节点 | 用途说明 |",
              "|------|-------------|---------|------|------|--------|------------|------------|---------|---------|"]
    total = 0.0
    for i, it in enumerate(app.get("items", []), 1):
        qty = float(it.get("qty", 0) or 0)
        price = float(it.get("price", 0) or 0)
        amt = qty * price
        total += amt
        lines.append(
            f"| {i} | {it.get('name','')} | {it.get('spec','')} | {it.get('unit','')} | "
            f"{qty} | {it.get('tier','')} | {_money(price)} | {_money(amt)} | "
            f"{it.get('node','')} | {it.get('use','')} |")
    lines.append("")
    lines.append(f"**合计金额（元）**：{_money(total)}")
    lines.append("")
    lines.append("## 审批")
    lines.append("| 角色 | 签字 | 日期 |")
    lines.append("|------|------|------|")
    for role in ("申请人", "专业审核", "采购主管", "项目总"):
        lines.append(f"| {role} | | |")
    return "\n".join(lines) + "\n"


def render_bom(project, bom):
    lines = ["# BOM 拆解表（医疗净化工程 · 按专业）", "",
             "> 由 cleanroom-procurement-lifecycle 技能生成（脱敏）", "",
             "## BOM 明细",
             "| 专业 | 序号 | 设备/材料名称 | 规格 | 单位 | 数量 | 关键路径标记 | 建议锁单时机 | 备注 |",
             "|------|------|-------------|------|------|------|------------|------------|------|"]
    summary = {}
    for i, r in enumerate(bom.get("rows", []), 1):
        trade = r.get("trade", "—")
        summary.setdefault(trade, {"n": 0, "k": 0})
        summary[trade]["n"] += 1
        if r.get("flag"):
            summary[trade]["k"] += 1
        lines.append(
            f"| {trade} | {i} | {r.get('name','')} | {r.get('spec','')} | {r.get('unit','')} | "
            f"{r.get('qty','')} | {r.get('flag','')} | {r.get('lock','')} | {r.get('note','')} |")
    lines.append("")
    lines.append("## 汇总")
    lines.append("| 专业 | 条目数 | 关键路径项数 | 备注 |")
    lines.append("|------|--------|------------|------|")
    tot_n = tot_k = 0
    for trade, s in summary.items():
        lines.append(f"| {trade} | {s['n']} | {s['k']} | |")
        tot_n += s["n"]; tot_k += s["k"]
    lines.append(f"| **合计** | {tot_n} | {tot_k} | |")
    return "\n".join(lines) + "\n"


def render_compare(project, cmp):
    weights = cmp.get("weights", {})
    suppliers = cmp.get("suppliers", [])
    dims = list(weights.keys())
    lines = ["# 供应商比价矩阵（医疗净化工程）", "",
             "> 由 cleanroom-procurement-lifecycle 技能生成（脱敏）", "",
             "## 评估维度与权重"]
    lines.append("| 维度 | 权重 |")
    lines.append("|------|------|")
    for d, w in weights.items():
        lines.append(f"| {d} | {w*100:.0f}% |")
    lines.append("")
    lines.append("## 评分表（1–5 分，5 最优）")
    head = "| 维度(权重) | " + " | ".join(s.get("name", "?") for s in suppliers) + " |"
    lines.append(head)
    lines.append("|" + "---|" * (len(suppliers) + 1))
    totals = {s.get("name", "?"): 0.0 for s in suppliers}
    for d in dims:
        row = f"| {d}({weights[d]*100:.0f}%) |"
        for s in suppliers:
            sc = float(s.get("scores", {}).get(d, 0))
            row += f" {sc} |"
            totals[s.get("name", "?")] += sc * weights[d]
        lines.append(row)
    lines.append("| **加权总分** |" + " " +
                  " | ".join(f"**{t:.2f}**" for t in totals.values()) + " |")
    lines.append("")
    best = max(totals, key=totals.get) if totals else "—"
    lines.append("## 结论建议")
    lines.append(f"- 推荐定标：{best}（加权总分最高）")
    lines.append(f"- 各供应商总分：{ '；'.join(f'{k} {v:.2f}' for k,v in totals.items()) }")
    lines.append("- 风险与对冲：____________________")
    lines.append("- 谈判重点：____________________")
    return "\n".join(lines) + "\n"


def render_cost(project, cost):
    lines = ["# 成本估算框架（医疗净化工程 · 按专业）", "",
             "> 由 cleanroom-procurement-lifecycle 技能生成（脱敏）", "",
             "## 按专业分解",
             "| 专业 | 直接设备费 | 材料费 | 安装配合费 | 税费 | 小计 | 占预算比 |",
             "|------|-----------|--------|-----------|------|------|---------|"]
    grand = 0.0
    subtotals = []
    for r in cost.get("rows", []):
        d = float(r.get("device", 0) or 0)
        m = float(r.get("material", 0) or 0)
        ins = float(r.get("install", 0) or 0)
        t = float(r.get("tax", 0) or 0)
        sub = d + m + ins + t
        subtotals.append(sub)
        grand += sub
        lines.append(f"| {r.get('trade','—')} | {_money(d)} | {_money(m)} | {_money(ins)} | "
                     f"{_money(t)} | {_money(sub)} | |")
    lines.append(f"| **合计** | | | | | **{_money(grand)}** | 100% |")
    lines.append("")
    cont = float(cost.get("contingency_rate", 0) or 0)
    mgmt = float(cost.get("management", 0) or 0)
    cont_amt = grand * cont
    total_budget = grand + cont_amt + mgmt
    lines.append("## 费用附加项")
    lines.append("| 项 | 计算口径 | 金额 |")
    lines.append("|----|---------|------|")
    lines.append(f"| 不可预见费 | 合计的 {cont*100:.0f}% | {_money(cont_amt)} |")
    lines.append(f"| 管理费 | 公司管理费分摊 | {_money(mgmt)} |")
    lines.append(f"| **总预算** | | **{_money(total_budget)}** |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def _write_file(path, content):
    """安全写入文件，带权限异常兜底。"""
    try:
        # 确保目录存在
        dirn = os.path.dirname(path)
        if dirn:
            os.makedirs(dirn, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path
    except PermissionError:
        print(f"  ⚠️ 无法写入 {path}：没有写入权限，请检查文件夹是否只读或被占用")
        return None
    except OSError as e:
        print(f"  ⚠️ 写入 {path} 失败：{e}")
        return None


def generate(spec, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    project = spec.get("project", {})
    files = {}
    if "application" in spec:
        p = os.path.join(out_dir, "采购申请单.md")
        result = _write_file(p, render_application(project, spec["application"]))
        if result:
            files["采购申请单"] = result
    if "bom" in spec:
        p = os.path.join(out_dir, "BOM拆解表.md")
        result = _write_file(p, render_bom(project, spec["bom"]))
        if result:
            files["BOM拆解表"] = result
    if "compare" in spec:
        p = os.path.join(out_dir, "供应商比价矩阵.md")
        result = _write_file(p, render_compare(project, spec["compare"]))
        if result:
            files["供应商比价矩阵"] = result
    if "cost" in spec:
        p = os.path.join(out_dir, "成本估算框架.md")
        result = _write_file(p, render_cost(project, spec["cost"]))
        if result:
            files["成本估算框架"] = result

    # 如果全部写入失败，给明确提示
    if not files:
        print("  ❌ 所有文档均未能成功写入，请检查输出目录权限")

    return files


DEMO = {
    "project": {"name": "某三甲医院洁净手术部项目", "code": "PRJ-DEMO", "date": "2026-07-12"},
    "application": {
        "trade": "暖通", "method": "自采", "node": "主体施工第 6 周",
        "items": [
            {"name": "净化空调机组", "spec": "MAU+AHU 非标定制", "unit": "台", "qty": 2,
             "tier": "国产一线", "price": 0, "node": "第6周", "use": "关键路径-长交期"},
            {"name": "FFU 风机过滤单元", "spec": "H14", "unit": "台", "qty": 120,
             "tier": "国产一线", "price": 0, "node": "第8周", "use": ""},
        ],
    },
    "bom": {
        "rows": [
            {"trade": "暖通", "name": "净化空调机组", "spec": "MAU+AHU", "unit": "台", "qty": 2,
             "flag": "长交期/大金额/影响验收", "lock": "投标后即锁", "note": ""},
            {"trade": "医气", "name": "中心供氧管道", "spec": "脱脂紫铜管", "unit": "米", "qty": 800,
             "flag": "影响验收", "lock": "开工前", "note": "与装饰开孔位需提前拉通"},
        ],
    },
    "compare": {
        "weights": {"资质授权": 0.15, "单价": 0.25, "交期": 0.20, "质保": 0.15,
                    "验收风险": 0.10, "付款": 0.10, "本地服务": 0.05},
        "suppliers": [
            {"name": "供应商A", "tier": "国产一线",
             "scores": {"资质授权": 5, "单价": 4, "交期": 4, "质保": 4, "验收风险": 4, "付款": 3, "本地服务": 4}},
            {"name": "供应商B", "tier": "国产二线",
             "scores": {"资质授权": 4, "单价": 5, "交期": 3, "质保": 3, "验收风险": 3, "付款": 4, "本地服务": 3}},
            {"name": "供应商C", "tier": "进口高端",
             "scores": {"资质授权": 5, "单价": 2, "交期": 5, "质保": 5, "验收风险": 5, "付款": 2, "本地服务": 3}},
        ],
    },
    "cost": {
        "rows": [
            {"trade": "暖通", "device": 0, "material": 0, "install": 0, "tax": 0},
            {"trade": "装饰", "device": 0, "material": 0, "install": 0, "tax": 0},
            {"trade": "医疗设备", "device": 0, "material": 0, "install": 0, "tax": 0},
        ],
        "contingency_rate": 0.05, "management": 0,
    },
}


def main():
    ap = argparse.ArgumentParser(
        description="医疗净化采购文档生成器（v1.1 — 友好提示版）",
        epilog="示例：python generate.py --demo\n      python generate.py --spec 项目.json --out 输出目录",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", help="JSON 项目简述路径")
    ap.add_argument("--out", default="output", help="输出目录（默认：./output）")
    ap.add_argument("--demo", action="store_true", help="生成示例文档（无需 spec）")
    ap.add_argument("--validate", metavar="SPEC", help="仅校验 spec 合法性，不生成文档")
    args = ap.parse_args()

    # ---- 仅校验模式 ----
    if args.validate:
        try:
            with open(args.validate, encoding="utf-8") as f:
                spec = json.load(f)
        except FileNotFoundError:
            print(f"❌ 找不到文件：{args.validate}")
            print("   请检查文件路径是否正确，或文件是否已移动/删除")
            sys.exit(2)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 格式错误：{args.validate}")
            print(f"   第 {e.lineno} 行第 {e.colno} 列附近有语法错误：{e.msg}")
            print("   提示：检查是否缺少逗号、多了逗号、括号不匹配、或含有中文标点")
            sys.exit(2)
        except PermissionError:
            print(f"❌ 没有权限读取文件：{args.validate}")
            sys.exit(2)

        errs = validate_spec(spec)
        if errs:
            print(f"\n⚠️ 校验发现 {len(errs)} 个问题：\n")
            for e in errs:
                print(f"  {e}")
            print("\n💡 修复建议：逐条修改后重新运行 --validate 确认通过即可")
            sys.exit(1)
        else:
            print("✅ 校验通过！spec 格式合法，可以用 --spec 生成文档了。")
        return

    # ---- Demo 模式 ----
    if args.demo:
        try:
            files = generate(DEMO, args.out)
        except Exception as e:
            print(f"❌ 生成示例文档时出错：{e}")
            print("   这可能是程序内部错误，请联系技能维护者")
            sys.exit(3)
        if files:
            print(f"\n✅ 已生成 {len(files)} 份示例文档到 {args.out}/ ：")
            for k, v in files.items():
                print(f"  📄 {k} → {v}")
            print("\n💡 提示：示例中的金额为占位符（0），实际使用时请替换为真实数据")
        return

    # ---- 从 spec 生成模式 ----
    if args.spec:
        try:
            with open(args.spec, encoding="utf-8") as f:
                spec = json.load(f)
        except FileNotFoundError:
            print(f"❌ 找不到 spec 文件：{args.spec}")
            print("   请确认路径正确。当前工作目录：", os.getcwd())
            sys.exit(2)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 格式错误（{args.spec}）：第 {e.lineno} 行附近 — {e.msg}")
            print("   常见原因：末尾多余逗号、中文引号、注释语法等")
            sys.exit(2)
        except PermissionError:
            print(f"❌ 无权读取文件：{args.spec}")
            sys.exit(2)

        errs = validate_spec(spec)
        if errs:
            print(f"\n⚠️ spec 有 {len(errs)} 个问题，已中止生成：\n")
            for e in errs:
                print(f"  {e}")
            print("\n💡 建议先运行：python generate.py --validate " + args.spec)
            sys.exit(1)

        try:
            files = generate(spec, args.out)
        except Exception as e:
            print(f"❌ 生成文档时发生未预期错误：{e}")
            print("   请检查 spec 数据完整性后重试")
            sys.exit(3)

        if files:
            print(f"\n✅ 已生成 {len(files)} 份文档到 {args.out}/ ：")
            for k, v in files.items():
                print(f"  📄 {k} → {v}")
        else:
            print("\n⚠️ 没有任何文档被成功生成，请查看上方错误信息")
        return

    # ---- 无参数 → 显示帮助 ----
    ap.print_help()
    print("\n💡 快速开始：运行 python generate.py --demo 查看示例输出")


if __name__ == "__main__":
    main()
