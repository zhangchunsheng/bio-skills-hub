#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医疗净化工程物料与 BOM 管控 · 文档生成器

从一份 JSON 项目简述生成 2 类交付物（markdown）：
  1. BOM 编制表（含 备料量 = 净用量 ×(1+损耗率) 自动计算）
  2. 量差分析表（节点 12：实际用量 vs BOM 备料量，分因量差）

全程脱敏：不要求也不保留真实供应商名/合同价/内部额度；档次用
「国产一线/二线/进口高端」等通用口径。

用法：
  python generate.py --demo                  # 生成示例到 ./output_demo
  python generate.py --spec s.json --out out # 从 spec 生成
  python generate.py --validate s.json       # 仅校验 spec 合法性

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
    if "bom" not in spec and "variance" not in spec:
        errs.append("⚠️ 至少需要包含 bom（BOM编制表）或 variance（量差分析表）之一，当前两个都没有")
    if "bom" in spec:
        bom = spec["bom"]
        if not isinstance(bom, dict):
            errs.append("❌ bom 段必须是 JSON 对象")
        else:
            for i, r in enumerate(bom.get("rows", [])):
                prefix = f"bom.rows[{i}]（{r.get('name', '未命名')}）"
                if not r.get("name"):
                    errs.append(f"❌ {prefix} 缺少 name（材料/设备名称）")
                if not r.get("trade"):
                    errs.append(f"❌ {prefix} 缺少 trade（专业，如：暖通/装饰/电气/医气/给排水/医疗设备）")
                # net_qty
                try:
                    q = float(r.get("net_qty", 0) or 0)
                    if q < 0:
                        errs.append(f"⚠️ {prefix} net_qty={q} 为负数，净用量不能为负")
                except (TypeError, ValueError):
                    errs.append(f"❌ {prefix} net_qty 不是有效数字（当前值：{r.get('net_qty', '')}），请填数字如 3000 或 2")
                # loss_rate
                try:
                    lr = float(r.get("loss_rate", 0) or 0)
                    if lr < 0:
                        errs.append(f"⚠️ {prefix} loss_rate={lr} 为负数，损耗率不能为负（0=无损耗, 0.03=3%）")
                    elif lr > 1.0:
                        errs.append(f"💡 {prefix} loss_rate={lr} 大于 1.0。你填的是百分比吗？如果是 3% 应该填 0.03 而不是 3")
                except (TypeError, ValueError):
                    errs.append(f"❌ {prefix} loss_rate 不是有效数字（当前值：{r.get('loss_rate', '')}），请填小数如 0.03 表示 3%")
                # supply
                valid_supply = ("甲供", "乙供", "甲指乙供")
                s = r.get("supply")
                if s is not None and s not in valid_supply:
                    errs.append(f"⚠️ {prefix} supply=\"{s}\" 不在允许值内（应为：甲供 / 乙供 / 甲指乙供），将按原样输出不做修正")
    if "variance" in spec:
        var = spec["variance"]
        if not isinstance(var, dict):
            errs.append("❌ variance 段必须是 JSON 对象")
        else:
            for i, r in enumerate(var.get("rows", [])):
                prefix = f"variance.rows[{i}]（{r.get('name', '未命名')}）"
                for k in ("bom_qty", "actual_qty"):
                    try:
                        v = float(r.get(k, 0) or 0)
                        if v < 0:
                            errs.append(f"⚠️ {prefix} {k}={v} 为负数")
                    except (TypeError, ValueError):
                        errs.append(f"❌ {prefix} {k} 不是有效数字（当前值：{r.get(k, '')}），BOM备料量和实际用量须是数字")
                c = r.get("cause")
                if c is not None and c not in ("设计", "施工", "供应"):
                    errs.append(f"⚠️ {prefix} cause=\"{c}\" 不在标准分类内（设计/施工/供应），将原样输出；如需自定义可在备注栏补充")
    return errs


# ---------------------------------------------------------------------------
# 渲染
# ---------------------------------------------------------------------------
def _num(x, nd=2):
    try:
        return f"{float(x):,.{nd}f}"
    except (TypeError, ValueError):
        return str(x)


def render_bom(project, bom):
    version = bom.get("version", "V2施工图")
    lines = ["# BOM 编制表（医疗净化工程 · 含损耗/备料/甲供乙供/编码）", "",
             "> 由 cleanroom-material-bom 技能生成（脱敏）", "",
             f"## 版本信息", "| 项 | 内容 |", "|----|------|",
             f"| BOM 版本 | {version} |",
             f"| 项目（脱敏） | {project.get('name','—')} |",
             f"| 项目编号 | {project.get('code','—')} |",
             f"| 编制日期 | {bom.get('date', date.today().isoformat())} |", ""]
    lines += ["## BOM 明细",
              "| 专业 | 编码 | 名称 | 规格 | 单位 | 净用量 | 损耗率 | 备料量 | 供应方式 | 关键路径 | 锁单时机 | 备注 |",
              "|------|------|------|------|------|--------|--------|--------|---------|---------|---------|------|"]
    summary = {}
    for r in bom.get("rows", []):
        trade = r.get("trade", "—")
        net = float(r.get("net_qty", 0) or 0)
        loss = float(r.get("loss_rate", 0) or 0)
        prep = net * (1 + loss)
        summary.setdefault(trade, {"n": 0, "prep": 0.0})
        summary[trade]["n"] += 1
        summary[trade]["prep"] += prep
        lines.append(
            f"| {trade} | {r.get('code','')} | {r.get('name','')} | {r.get('spec','')} | "
            f"{r.get('unit','')} | {_num(net)} | {loss*100:.1f}% | {_num(prep)} | "
            f"{r.get('supply','')} | {r.get('flag','')} | {r.get('lock','')} | {r.get('note','')} |")
    lines.append("")
    lines.append("## 汇总（按专业备料量合计）")
    lines.append("| 专业 | 条目数 | 备料量合计 | 备注 |")
    lines.append("|------|--------|-----------|------|")
    tot_n = tot_prep = 0.0
    for trade, s in summary.items():
        lines.append(f"| {trade} | {s['n']} | {_num(s['prep'])} | |")
        tot_n += s["n"]; tot_prep += s["prep"]
    lines.append(f"| **合计** | {tot_n} | **{_num(tot_prep)}** | |")
    lines.append("")
    lines.append("> 备料量 = 净用量 ×(1+损耗率)（工艺余量未单列时计入 0）。损耗率取自损耗率经验区间表。")
    return "\n".join(lines) + "\n"


def render_variance(project, var):
    lines = ["# 量差分析表（医疗净化工程 · 节点 12 结算量差）", "",
             "> 由 cleanroom-material-bom 技能生成（脱敏）", "",
             f"## 项目（脱敏）：{project.get('name','—')} ｜ 编号：{project.get('code','—')}", "",
             "## 量差明细",
             "| 专业 | 名称 | 单位 | BOM备料量 | 实际用量 | 量差 | 量差率 | 成因分类 |",
             "|------|------|------|----------|---------|------|--------|---------|"]
    tot_bom = tot_act = 0.0
    for r in var.get("rows", []):
        bom_q = float(r.get("bom_qty", 0) or 0)
        act_q = float(r.get("actual_qty", 0) or 0)
        diff = act_q - bom_q
        rate = (diff / bom_q * 100) if bom_q else 0.0
        tot_bom += bom_q; tot_act += act_q
        lines.append(
            f"| {r.get('trade','—')} | {r.get('name','')} | {r.get('unit','')} | "
            f"{_num(bom_q)} | {_num(act_q)} | {_num(diff)} | {rate:+.1f}% | {r.get('cause','')} |")
    lines.append(f"| **合计** | | | **{_num(tot_bom)}** | **{_num(tot_act)}** | "
                 f"**{_num(tot_act-tot_bom)}** | | |")
    lines.append("")
    lines.append("## 分析结论")
    lines.append("- 量差 = 实际用量 − BOM 备料量；按 设计/施工/供应 三分因归类。")
    lines.append("- 施工量差（损耗/浪费/丢失）应回灌校准「损耗率经验区间表」。")
    lines.append("- 设计量差（变更）须有节点 10 的签证/补充协议支撑。")
    lines.append("- 供应量差（短装/超装）关联节点 7 到货验收记录。")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def _write_file(path, content):
    """安全写入文件，带权限异常兜底。"""
    try:
        dirn = os.path.dirname(path)
        if dirn:
            os.makedirs(dirn, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path
    except PermissionError:
        print(f"  ⚠️ 无法写入 {path}：没有写入权限，请检查文件夹是否只读或被其他程序占用")
        return None
    except OSError as e:
        print(f"  ⚠️ 写入 {path} 失败：{e}")
        return None


def generate(spec, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    project = spec.get("project", {})
    files = {}
    if "bom" in spec:
        p = os.path.join(out_dir, "BOM编制表.md")
        result = _write_file(p, render_bom(project, spec["bom"]))
        if result:
            files["BOM编制表"] = result
    if "variance" in spec:
        p = os.path.join(out_dir, "量差分析表.md")
        result = _write_file(p, render_variance(project, spec["variance"]))
        if result:
            files["量差分析表"] = result

    if not files:
        print("  ❌ 所有文档均未能成功写入，请检查输出目录权限")

    return files


DEMO = {
    "project": {"name": "某三甲医院洁净手术部项目", "code": "PRJ-DEMO", "date": "2026-07-12"},
    "bom": {"version": "V2施工图", "date": "2026-07-12",
        "rows": [
            {"trade": "暖通", "code": "HVAC-01", "name": "净化空调机组", "spec": "MAU+AHU",
             "unit": "台", "net_qty": 2, "loss_rate": 0, "supply": "乙供",
             "flag": "长交期/大金额", "lock": "投标后即锁", "note": "非标定制"},
            {"trade": "电气", "code": "ELE-12", "name": "阻燃线缆", "spec": "WDZ-YJY",
             "unit": "米", "net_qty": 3000, "loss_rate": 0.03, "supply": "乙供",
             "flag": "", "lock": "", "note": "按回路长度+损耗"},
            {"trade": "医气", "code": "MGS-03", "name": "脱脂紫铜管", "spec": "Φ22",
             "unit": "米", "net_qty": 800, "loss_rate": 0.03, "supply": "甲供",
             "flag": "影响验收", "lock": "开工前", "note": "与装饰开孔位提前拉通"},
        ]},
    "variance": {"rows": [
        {"trade": "电气", "name": "阻燃线缆", "unit": "米",
         "bom_qty": 3090, "actual_qty": 3250, "cause": "施工"},
        {"trade": "医气", "name": "脱脂紫铜管", "unit": "米",
         "bom_qty": 824, "actual_qty": 800, "cause": "设计"},
    ]},
}


def main():
    ap = argparse.ArgumentParser(
        description="医疗净化工程物料与 BOM 管控 · 文档生成器（v1.1 — 友好提示版）",
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
            print("\n💡 提示：示例中的损耗率为占位符（0），实际使用时请按项目经验区间填入")
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
