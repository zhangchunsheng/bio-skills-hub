#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用招投标采购助手 —— 评分测算与检查清单生成器（仅标准库）

功能：
  1. 报价得分测算（低价优先法 / 基准价±偏差法）
  2. 多报价模拟排名
  3. 投标检查清单生成
  4. 招标文件关键数字粗提（parse）

合规声明：本脚本仅做合规投标辅助计算，不提供任何违法投标方案。
所有公式参数需用户显式提供，脚本不臆造法规。
"""
import argparse
import json
import re
import sys


def price_priority_score(quote, base, weight):
    """低价优先法：得分 = (基准价 / 报价) × 满分，封顶 weight。"""
    if quote <= 0:
        return 0.0
    score = (base / quote) * weight
    return round(min(score, weight), 2)


def benchmark_dev_score(quote, base, weight, dev_step, dev_cap):
    """基准价±偏差法：偏离% = (报价-基准)/基准×100；得分=满分-|偏离|×步长，封顶weight封底0。"""
    if base <= 0:
        return 0.0
    dev_pct = (quote - base) / base * 100.0
    score = weight - abs(dev_pct) * dev_step
    score = max(0.0, min(score, weight))
    if dev_cap is not None:
        score = max(0.0, min(score, dev_cap))
    return round(score, 2), round(dev_pct, 2)


def compute_base(quotes, base_type, composite_factor=0.95):
    valid = [q for q in quotes if q and q > 0]
    if not valid:
        return 0.0
    if base_type == "min":
        return min(valid)
    if base_type == "avg":
        return sum(valid) / len(valid)
    if base_type == "composite":
        return (sum(valid) / len(valid)) * composite_factor
    if base_type == "given":
        return 0.0  # 给定值场景由调用方直接传 base
    return sum(valid) / len(valid)


def simulate(quotes, method, weight, base_type, dev_step, dev_cap,
             composite_factor, tech_biz_scores=None):
    base = compute_base(quotes, base_type, composite_factor)
    rows = []
    for i, q in enumerate(quotes):
        if method == "price_priority":
            ps = price_priority_score(q, base, weight)
            dev = None
        else:
            ps, dev = benchmark_dev_score(q, base, weight, dev_step, dev_cap)
        tb = (tech_biz_scores or {}).get(i, 0.0)
        total = round(ps + tb, 2)
        rows.append({"idx": i, "quote": q, "price_score": ps,
                     "dev_pct": dev, "tech_biz": tb, "total": total})
    rows.sort(key=lambda r: r["total"], reverse=True)
    for rank, r in enumerate(rows, 1):
        r["rank"] = rank
    return base, rows


def gen_checklist(stars, formats, extra_notes):
    lines = ["# 投标检查清单（定制版）", ""]
    lines.append("> 投标前逐项勾选。带「★/必须/不可偏离」的条款为否决项，最先查。", )
    lines.append("")
    lines.append("## 一、资格与实质（否决级）")
    for i, s in enumerate(stars, 1):
        lines.append(f"- [ ] ★条款{i}：{s} —— 已逐条响应并承诺")
    lines.append("- [ ] 营业执照范围覆盖采购内容")
    lines.append("- [ ] 资质/证书在有效期内且名称一致")
    lines.append("- [ ] 报价 ≤ 最高限价（含分项限价）")
    lines.append("")
    lines.append("## 二、必交格式件")
    for i, f in enumerate(formats, 1):
        lines.append(f"- [ ] {f}（严格使用给定格式）")
    lines.append("")
    lines.append("## 三、签字盖章 / 封装 / 时效")
    lines.append("- [ ] 法定代表人或授权人签字齐全")
    lines.append("- [ ] 公章/法人章位置正确清晰")
    lines.append("- [ ] 正副本数量、密封标识正确")
    lines.append("- [ ] 保证金按时到账、凭证留存")
    lines.append("- [ ] 投标截止前送达/上传完成、回执保存")
    if extra_notes:
        lines.append("")
        lines.append("## 四、补充提醒")
        for n in extra_notes:
            lines.append(f"- {n}")
    return "\n".join(lines)


def parse_brief(text):
    """粗提关键数字：限价、保证金、日期。仅作提示，不准确。"""
    out = {}
    m = re.search(r"最高限价[^\d]{0,8}([\d,.]+)\s*(万|元)?", text)
    if m:
        out["最高限价(疑似)"] = m.group(1) + (m.group(2) or "")
    m = re.search(r"预算[^\d]{0,8}([\d,.]+)\s*(万|元)?", text)
    if m:
        out["预算(疑似)"] = m.group(1) + (m.group(2) or "")
    m = re.search(r"保证金[^\d]{0,8}([\d,.]+)\s*(万|元)?", text)
    if m:
        out["保证金(疑似)"] = m.group(1) + (m.group(2) or "")
    dates = re.findall(r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)", text)
    if dates:
        out["日期(疑似)"] = dates[:5]
    out["提示"] = "粗提结果仅供参考，以招标文件原文为准；建议人工核对。"
    return out


def main():
    ap = argparse.ArgumentParser(description="通用招投标采购助手 - 测算与清单")
    ap.add_argument("--mode", default="score",
                    choices=["score", "parse", "checklist"])
    ap.add_argument("--method", default="price_priority",
                    choices=["price_priority", "benchmark_dev"])
    ap.add_argument("--quote", type=float, help="你的报价（万元）")
    ap.add_argument("--ceiling", type=float, help="最高限价（万元）")
    ap.add_argument("--base-type", default="min",
                    choices=["min", "avg", "composite", "given"])
    ap.add_argument("--base", type=float, help="给定基准价（base-type=given 时用）")
    ap.add_argument("--price-weight", type=float, default=30, help="报价满分")
    ap.add_argument("--dev-step", type=float, default=0.5,
                    help="基准价±偏差法：每偏差1%扣分值")
    ap.add_argument("--dev-cap", type=float, default=None,
                    help="报价分下限封底（如 0）")
    ap.add_argument("--composite-factor", type=float, default=0.95)
    ap.add_argument("--others", default="",
                    help="其他报价，逗号分隔（模拟排名）")
    ap.add_argument("--tech-biz", default="",
                    help="各报价对应技术商务分，逗号分隔（与others对应）")
    ap.add_argument("--file", help="parse 模式输入文本文件")
    ap.add_argument("--stars", default="", help="★条款，竖线分隔")
    ap.add_argument("--formats", default="", help="必交格式件，竖线分隔")
    ap.add_argument("--notes", default="", help="补充提醒，竖线分隔")
    ap.add_argument("--out", help="输出文件路径（可选）")
    args = ap.parse_args()

    result = {}

    if args.mode == "parse":
        if not args.file:
            print("parse 模式需要 --file", file=sys.stderr)
            return 1
        text = open(args.file, encoding="utf-8").read()
        result = parse_brief(text)

    elif args.mode == "checklist":
        stars = [s for s in args.stars.split("|") if s.strip()]
        formats = [f for f in args.formats.split("|") if f.strip()]
        notes = [n for n in args.notes.split("|") if n.strip()]
        result = gen_checklist(stars, formats, notes)

    else:  # score
        if not args.quote:
            print("score 模式需要 --quote", file=sys.stderr)
            return 1
        others = [float(x) for x in args.others.split(",") if x.strip()]
        quotes = [args.quote] + others
        if args.base_type == "given":
            if not args.base:
                print("base-type=given 需要 --base", file=sys.stderr)
                return 1
            base = args.base
            quotes = [args.quote] + others
        else:
            base = compute_base(quotes, args.base_type, args.composite_factor)
        tb = {}
        if args.tech_biz:
            vals = [float(x) for x in args.tech_biz.split(",") if x.strip()]
            for i, v in enumerate(vals):
                tb[i] = v
        if len(quotes) > 1:
            base, rows = simulate(quotes, args.method, args.price_weight,
                                  args.base_type, args.dev_step, args.dev_cap,
                                  args.composite_factor, tb)
            result = {"基准价": round(base, 2), "你的报价": args.quote,
                      "排名模拟": rows}
        else:
            if args.method == "price_priority":
                ps = price_priority_score(args.quote, base, args.price_weight)
                result = {"基准价": round(base, 2), "你的报价": args.quote,
                          "报价得分": ps, "满分": args.price_weight}
            else:
                ps, dev = benchmark_dev_score(args.quote, base, args.price_weight,
                                             args.dev_step, args.dev_cap)
                result = {"基准价": round(base, 2), "你的报价": args.quote,
                          "偏离%": dev, "报价得分": ps, "满分": args.price_weight}

    out_text = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else result
    if args.out:
        open(args.out, "w", encoding="utf-8").write(out_text + "\n")
        print(f"已写入 {args.out}")
    else:
        print(out_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
