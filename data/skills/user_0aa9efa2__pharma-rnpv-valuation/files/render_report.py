#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
priced-in JSON -> Markdown 报告渲染器
=====================================
从 [ticker]_implied.json (符合 output_schema.json 契约) 渲染
人类可读的 Markdown 报告。JSON 是真值源,MD 是呈现。

用法:
    python render_report.py <json_file> [-o <output.md>]

默认输出: 与 JSON 同名 _rendered.md
"""
import json
import sys
import os


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def pct(x, d=2):
    """小数 -> 百分比字符串"""
    return f"{x*100:.{d}f}%"


def render(d):
    m = d["metadata"]
    L = []
    L.append(f"# {m['name']}（{m['ticker']}）priced-in 重审报告")
    L.append("")
    L.append(f"> **分析日期**：{m['date']} | **当前价**：{m['current_price']} | **市值**：{m['market_cap_yi']}亿 | **货币**：{m['currency']} | **方法**：{m['method']}")
    if m.get("framework_migration"):
        L.append(f"> **框架迁移**：{m['framework_migration']}")
    L.append("")
    L.append("---")
    L.append("")

    # 一、执行摘要
    v = d["verdict"]
    L.append("## 一、执行摘要")
    L.append("")
    L.append(f"- **综合判断**：{v['judgment']}")
    L.append(f"- **理由**：{v['rationale']}")
    L.append(f"- **稳健性**：{v['robustness']}")
    L.append("")

    # 二、T1 基线
    b = d["baseline"]
    L.append("## 二、T1 基线（三源交叉）")
    L.append("")
    L.append(f"- PE(TTM)：{b['pe_ttm']} | 当前PE（市值/FY25归母）：{b['pe_current']}")
    f = b["financials"]
    L.append(f"- FY25 归母：{f['fy25_net_income_yi']}亿（+{pct(f['fy25_ni_yoy'], 1)}）| EPS {f['fy25_eps']} | 来源：{f['source']}")
    L.append("- 远期共识：")
    for c in b["consensus"]:
        L.append(f"  - {c['year']}：EPS {c['eps']} / NI {c['net_income_yi']}亿 / PE@当前 {c['pe_at_current']} | {c['source']}")
    cs = b["capital_structure"]
    L.append(f"- 资本结构：净负债 {cs['net_debt_yi']}亿 / FCF {cs['fcf_yi']}亿 / ROE {pct(cs['roe'], 1)}")
    cp_pos = b.get("cycle_position")
    if cp_pos:
        L.append(f"- **周期位置**：{cp_pos['current']} | {cp_pos['rationale']}")
    sc = b.get("s_curve")
    if sc:
        pen = f"（渗透率/份额 {sc['penetration_rate']}%）" if sc.get("penetration_rate") is not None else ""
        conf = f" [置信度:{sc.get('confidence','中')}]" if sc.get("confidence") else ""
        L.append(f"- **S 曲线位置**：{sc['position']}{pen}{conf}")
        L.append(f"  - 调整后现实锚：{pct(sc['adjusted_anchor'][0])} - {pct(sc['adjusted_anchor'][1])}（source of truth，覆盖默认 12-18%）")
        L.append(f"  - λ 期权：{sc['lambda_option']}")
        segs = sc.get("segments")
        if segs:
            L.append(f"  - **conglomerate SOTP 分部**：")
            for s in segs:
                sw = f"（渗透率 {s['penetration_rate']}%）" if s.get("penetration_rate") is not None else ""
                L.append(f"    - {s['segment']}：{s['position']}{sw} | 锚 {pct(s['adjusted_anchor'][0])}-{pct(s['adjusted_anchor'][1])} | weight {s['weight']} | λ {s.get('lambda_option','-')}")
        L.append(f"  - 理由：{sc['rationale']}")
    L.append("")

    # 三、严格的计算过程（核心）
    cp = d["calculation_process"]
    L.append("## 三、严格的计算过程（⭐ 核心）")
    L.append("")
    L.append(f"**方法**：{cp['method']}")
    L.append("")
    L.append(f"**公式**：")
    L.append(f"```")
    L.append(cp["formula"]["expression"])
    L.append(f"```")
    L.append(f"**公式解释**：{cp['formula']['explanation']}")
    p = cp["parameters"]
    L.append(f"**参数**：IRR = {pct(p['irr'])} | 期限 {p['horizon_years']} 年 | FV 因子 = {p['fv_factor']}")
    L.append(f"**算术纪律**：{cp['arithmetic_discipline']}")
    L.append(f"**计算脚本**：`{cp['calc_script']}`（所有 CAGR 由代码算得，可复现）")
    L.append("")

    for step in cp["steps"]:
        L.append(f"### 读数 {step['reading']}：{step['label']}")
        L.append(f"- 退出 PE：{step['exit_pe']} | 理由：{step['pe_rationale']}")
        L.append(f"- 净利_10y：{step['ni_10y_yi']}亿")
        L.append("- 基准净利拆解（区间制）：")
        for bc in step["base_cases"]:
            L.append(f"  - from {bc['base']} {bc['base_ni_yi']}亿 -> 隐含 CAGR **{pct(bc['implied_cagr'])}** | {bc['source']} | {bc['interpretation']}")
        L.append(f"- **核心 CAGR：{pct(step['core_cagr'])}**（from {step['core_base']}）")
        L.append("")

    L.append("### 敏感性分析")
    L.append("")
    for s in cp["sensitivity"]:
        axis = s.get("axis", "")
        axis_vals = s.get("axis_values", [])
        if axis and axis_vals and len(axis_vals) == len(s["results"]):
            pairs = " / ".join(f"{av}={pct(r)}" for av, r in zip(axis_vals, s["results"]))
            L.append(f"- {s['test']} [{axis}]: {pairs} -> {s['conclusion']}")
        else:
            results_str = " / ".join(pct(r) for r in s["results"])
            L.append(f"- {s['test']}：{results_str} -> {s['conclusion']}")
    L.append("")

    # 四、现实锚
    ra = d["reality_anchor"]
    L.append("## 四、现实锚对照")
    L.append("")
    L.append(f"- 现实可支撑 CAGR：{pct(ra['cagr_range'][0])} - {pct(ra['cagr_range'][1])}（中位 {pct(ra['midpoint'])}）")
    if b.get("s_curve"):
        L.append(f"  - **经 S 曲线调整**（{b['s_curve']['position']}）：= s_curve.adjusted_anchor（source of truth）")
    L.append(f"- 理由：{ra['rationale']}")
    L.append(f"- 隐含 vs 现实锚：**{ra['implied_vs_anchor']}**")
    if ra.get("anchor_uncertainty"):
        L.append(f"- 不确定性：{ra['anchor_uncertainty']}")
    L.append("")

    # 五、核心假设
    L.append("## 五、核心假设（当前价买入接受了什么）")
    L.append("")
    for a in d["core_assumptions"]:
        L.append(f"### {a['name']}")
        L.append(f"- 值：{a['value']}")
        L.append(f"- 来源：{a['source']} | 置信度：{a['confidence']} | T 级别：{a['t_level']}")
        if a.get("adjustment_rationale"):
            L.append(f"- 调整理由：{a['adjustment_rationale']}")
        L.append(f"- **若假设错了**：{a['if_wrong']}")
        L.append("")

    # 六、承担的风险
    L.append("## 六、承担的风险")
    L.append("")
    L.append("| 风险 | 概率 | 影响 | 什么被破坏 | 时间 | 缓解 |")
    L.append("|---|---|---|---|---|---|")
    for r in d["risks"]:
        L.append(f"| {r['name']} | {r['probability']} | {r['impact']} | {r['what_breaks']} | {r.get('timeline', '-')} | {r.get('mitigation', '-')} |")
    L.append("")

    # 七、操作信号
    os_ = d["operation_signal"]
    L.append("## 七、操作信号")
    L.append("")
    L.append(f"**行动**：{os_['action']}")
    L.append(f"- 当前价在 trigger 区间：{os_['current_price_in_trigger']} | trigger：{os_['trigger_zone'][0]} - {os_['trigger_zone'][1]}")
    if os_.get("price_to_cagr_map"):
        L.append("")
        L.append("| 价格 | 对应 CAGR | 定性 |")
        L.append("|---|---|---|")
        for pm in os_["price_to_cagr_map"]:
            L.append(f"| {pm['price']} | {pct(pm['cagr'])} | {pm['label']} |")
    L.append(f"\n**更优等待点**：{os_['better_entry'][0]} - {os_['better_entry'][1]}")
    L.append(f"\n**仓位建议**：{os_['position_advice']}")
    if os_.get("catalysts"):
        L.append("\n**催化剂**：")
        L.append("")
        L.append("| 时间 | 事件 | 影响 |")
        L.append("|---|---|---|")
        for c in os_["catalysts"]:
            L.append(f"| {c['date']} | {c['event']} | {c['impact']} |")
    L.append("")

    L.append("---")
    L.append("")
    L.append("> ⚠️ 本报告由 priced-in schema 渲染（JSON 真值源 + Markdown 呈现），仅供研究参考，不构成投资建议。reverse DCF 双读数对退出 PE / 基准净利 / 现实锚 CAGR 假设高度敏感。trigger 区间为 screen/重审触发器非精准买入点。投资决策请咨询持牌专业人士。")

    return "\n".join(L)


def main():
    if len(sys.argv) < 2:
        print("用法: python render_report.py <json_file> [-o <output.md>]")
        sys.exit(2)

    json_path = sys.argv[1]
    if not os.path.exists(json_path):
        print(f"[ERROR] 文件不存在: {json_path}")
        sys.exit(2)

    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        out_path = sys.argv[idx + 1]
    else:
        out_path = os.path.splitext(json_path)[0] + "_rendered.md"

    d = load_json(json_path)
    md = render(d)
    with open(out_path, encoding="utf-8", mode="w") as f:
        f.write(md)
    print(f"[OK] 报告已渲染: {out_path}")


if __name__ == "__main__":
    main()
