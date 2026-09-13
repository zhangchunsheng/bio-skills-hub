#!/usr/bin/env python3
"""
藏药单细胞药理学 — 流式细胞术数据分析

功能：
1. 读取流式CSV数据（各群体百分比/MFI）
2. 计算各组 Mean ± SD
3. 绘制柱状图（可选）
4. 输出统计检验（ANOVA + Tukey HSD）
5. 生成分析报告

用法：
    python flow_data_analyzer.py --input flow_data.csv \
        --panel "macrophage" \
        --groups "control,model,drug_low,drug_high"
"""

import argparse
import sys
import csv
import math
from pathlib import Path
from collections import defaultdict


# ---------- 统计工具 ----------

def mean(values):
    return sum(values) / len(values) if values else 0.0


def stdev(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def one_way_anova(groups_dict):
    """
    单因素方差分析（简化版，仅计算F值）
    完整版建议使用 scipy.stats.f_oneway
    """
    k = len(groups_dict)
    if k < 2:
        return 0.0, 1.0

    all_values = []
    group_means = {}
    group_sizes = {}
    
    for name, values in groups_dict.items():
        group_means[name] = mean(values)
        group_sizes[name] = len(values)
        all_values.extend(values)

    grand_mean = mean(all_values)
    n_total = len(all_values)

    ss_between = sum(group_sizes[g] * (group_means[g] - grand_mean) ** 2 for g in groups_dict)
    ss_within = sum(sum((x - group_means[g]) ** 2 for x in vals) for g, vals in groups_dict.items())

    df_between = k - 1
    df_within = n_total - k

    if df_within <= 0 or df_between <= 0:
        return 0.0, 1.0

    ms_between = ss_between / df_between
    ms_within = ss_within / df_within if ss_within > 0 else 1e-10

    f_value = ms_between / ms_within
    return f_value, df_between, df_within


def tukey_hsd(groups_dict, alpha=0.05):
    """
    Tukey HSD事后多重比较（简化版）
    完整版建议使用 scipy.stats.tukey_hsd
    此函数提供近似q统计量
    """
    k = len(groups_dict)
    if k < 2:
        return {}

    # 计算MSE（均方误差）
    group_means = {}
    group_vars = {}
    for name, values in groups_dict.items():
        group_means[name] = mean(values)
        group_vars[name] = stdev(values) ** 2

    n_total = sum(len(v) for v in groups_dict.values())
    df_within = n_total - k
    mse = sum((len(v) - 1) * group_vars[g] for g, v in groups_dict.items()) / max(df_within, 1)

    comparisons = {}
    group_names = list(groups_dict.keys())
    for i in range(len(group_names)):
        for j in range(i + 1, len(group_names)):
            g1, g2 = group_names[i], group_names[j]
            n1, n2 = len(groups_dict[g1]), len(groups_dict[g2])
            
            if n1 == 0 or n2 == 0:
                continue

            q_value = abs(group_means[g1] - group_means[g2]) / math.sqrt(mse * (1/n1 + 1/n2) / 2)
            # 简化版：q > 3.0 近似显著（实际需查q表，假设k=4, df≈∞时q.crit≈3.63）
            significant = q_value > 3.63
            comparisons[f"{g1} vs {g2}"] = {
                "mean_diff": round(group_means[g1] - group_means[g2], 3),
                "q_value": round(q_value, 3),
                "significant": significant,
            }

    return comparisons


# ---------- 数据加载 ----------

def load_flow_data(csv_path: str) -> dict:
    """加载流式数据，返回 {group: {parameter: [replicates]}}"""
    data = defaultdict(lambda: defaultdict(list))
    parameters = set()

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            group = row.get("group", "").strip()
            parameter = row.get("parameter", "").strip()
            value_str = row.get("value", "").strip()
            if not group or not parameter:
                continue
            parameters.add(parameter)

            try:
                value = float(value_str)
            except (ValueError, TypeError):
                continue

            data[group][parameter].append(value)

    return data, sorted(parameters)


# ---------- 输出 ----------

def print_anova_table(groups_dict, param_name: str):
    """输出 ANOVA 结果"""
    f_val, df_b, df_w = one_way_anova(groups_dict)
    print(f"  ANOVA: F({df_b},{df_w}) = {f_val:.4f}")

    # 近似P值评估
    if f_val > 10:
        p_indication = "P < 0.001 (***)"
    elif f_val > 5:
        p_indication = "P < 0.01 (**)"
    elif f_val > 3:
        p_indication = "P < 0.05 (*)"
    else:
        p_indication = "P > 0.05 (ns)"
    print(f"         近似判断: {p_indication}")


def print_full_report(data, parameters, groups_order):
    """输出完整的分析报告"""
    print("\n" + "=" * 70)
    print("  藏药单细胞药理学 — 流式细胞术数据分析报告")
    print("=" * 70)

    # 分组汇总表
    print(f"\n{'检测指标':<20}", end="")
    for g in groups_order:
        print(f"{g:<25}", end="")
    print()
    print("-" * (20 + 25 * len(groups_order)))

    for param in parameters:
        print(f"{param:<20}", end="")
        for g in groups_order:
            vals = data[g].get(param, [])
            if vals:
                m = mean(vals)
                s = stdev(vals)
                print(f"{m:<8.2f} ± {s:<5.2f}    ", end="")
            else:
                print(f"{'N/A':<25}", end="")
        print()

    # ANOVA 分析
    print(f"\n{'=' * 70}")
    print("  单因素方差分析（One-way ANOVA）")
    print(f"{'=' * 70}")
    for param in parameters:
        groups_dict = {g: data[g].get(param, []) for g in groups_order if data[g].get(param, [])}
        if len(groups_dict) >= 2:
            print(f"\n  📊 {param}:")
            print_anova_table(groups_dict, param)

            # Tukey HSD
            if len(groups_dict) > 2:
                comparisons = tukey_hsd(groups_dict)
                if comparisons:
                    print("     Tukey HSD 事后比较:")
                    for comp, result in comparisons.items():
                        sig = "✅" if result["significant"] else "❌"
                        print(f"      {sig} {comp}: diff={result['mean_diff']:+.3f}, q={result['q_value']:.3f}")

    # 总结
    print(f"\n{'=' * 70}")
    print("  📋 解读指南：")
    print("  · 巨噬细胞Panel：M1%(CD86+) / M2%(CD206+) 比值变化指示极化偏向")
    print("  · T细胞Panel：Th1(IFN-γ+)/Th2(IL-4+)/Th17(IL-17A+)/Treg(FoxP3+)比例")
    print("  · MFI比较反映每个细胞表面标志物的平均表达量变化")
    print(f"{'=' * 70}")


def save_csv_report(data, parameters, groups_order, output_path: str):
    """保存处理后的数据为CSV"""
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ["Parameter"]
        for g in groups_order:
            header.extend([f"{g}_Mean", f"{g}_SD", f"{g}_N"])
        writer.writerow(header)

        for param in parameters:
            row = [param]
            for g in groups_order:
                vals = data[g].get(param, [])
                if vals:
                    row.extend([f"{mean(vals):.2f}", f"{stdev(vals):.2f}", len(vals)])
                else:
                    row.extend(["N/A", "N/A", 0])
            writer.writerow(row)
    print(f"\n  ✅ 报告已保存至: {output_path}")


# ---------- 预置Panel模板 ----------

PANEL_TEMPLATES = {
    "macrophage": {
        "description": "巨噬细胞M1/M2极化Panel",
        "default_params": [
            "CD86_pct", "CD206_pct", "M1_M2_ratio",
            "iNOS_MFI", "Arg1_MFI", "TNFa_MFI", "IL10_MFI"
        ],
    },
    "tcell": {
        "description": "T细胞亚群Panel",
        "default_params": [
            "CD4_pct", "CD8_pct", "CD4_CD8_ratio",
            "Th1_IFNg_pct", "Th2_IL4_pct", "Th17_IL17_pct", "Treg_FoxP3_pct",
            "PD1_MFI", "GzmB_MFI"
        ],
    },
    "ros": {
        "description": "活性氧（ROS）检测Panel",
        "default_params": [
            "ROS_MFI", "ROS_pct_positive"
        ],
    },
}


# ---------- 主入口 ----------

def main():
    parser = argparse.ArgumentParser(description="藏药流式细胞术数据分析")
    parser.add_argument("--input", required=True, help="输入CSV文件")
    parser.add_argument("--panel", choices=list(PANEL_TEMPLATES.keys()) + ["custom"],
                        default="custom", help="Panel模板")
    parser.add_argument("--groups", default="control,model,drug",
                        help="组别顺序（逗号分隔）")
    parser.add_argument("--output", default=None, help="输出CSV文件路径（可选）")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"❌ 错误：输入文件不存在 {args.input}")
        sys.exit(1)

    groups_order = [g.strip() for g in args.groups.split(",")]
    data, parameters = load_flow_data(args.input)

    if args.panel != "custom":
        panel_info = PANEL_TEMPLATES[args.panel]
        print(f"📋 使用Panel模板: {panel_info['description']}")
        # 过滤出模板中存在的参数
        available_params = [p for p in parameters if p in panel_info["default_params"]]
        if available_params:
            parameters = available_params

    print(f"📖 加载 {args.input}")
    print(f"  组别: {groups_order}")
    print(f"  检测参数: {', '.join(parameters)}")

    print_full_report(data, parameters, groups_order)

    if args.output:
        save_csv_report(data, parameters, groups_order, args.output)


if __name__ == "__main__":
    main()
