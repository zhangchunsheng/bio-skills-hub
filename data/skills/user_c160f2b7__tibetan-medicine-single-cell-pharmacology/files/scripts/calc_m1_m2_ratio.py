#!/usr/bin/env python3
"""
藏药单细胞药理学 — M1/M2巨噬细胞极化评分与比例计算

功能：
1. 从单细胞表达矩阵计算每个细胞的M1和M2评分
2. 自动分类M1-like和M2-like细胞
3. 输出各组M1/M2比例、比率及统计检验
4. 生成可视化图表

用法：
    python calc_m1_m2_ratio.py --input data.h5ad \
        --m1_genes "Nos2,Cd86,Cxcl9,Tnf" \
        --m2_genes "Mrc1,Arg1,Il10,Cd163" \
        --group_col "condition"
"""

import argparse
import sys
import csv
import math
from pathlib import Path


# ---------- 核心计算 ----------

def load_expression_matrix(csv_path: str, group_col: str = None) -> dict:
    """从CSV加载表达矩阵（简化版：基因×细胞）"""
    matrix = {}
    cells = []
    group_map = {}
    skip_cols = {'cell_id'}
    if group_col:
        skip_cols.add(group_col)
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cell_id = row.get('cell_id', '')
            cells.append(cell_id)
            if group_col:
                group_map[cell_id] = row.get(group_col, 'Unknown').strip()
            for gene, expr in row.items():
                if gene in skip_cols:
                    continue
                try:
                    val = float(expr)
                except (ValueError, TypeError):
                    val = 0.0
                if gene not in matrix:
                    matrix[gene] = {}
                matrix[gene][cell_id] = val
    return matrix, cells, group_map


def calc_addmodule_score(matrix: dict, cells: list, gene_set: list, n_control: int = 5) -> dict:
    """
    简化版 AddModuleScore 计算。
    每个细胞的评分 = 目标基因集平均表达 - 随机对照基因集平均表达
    """
    score = {}
    valid_genes = [g for g in gene_set if g in matrix]

    if not valid_genes:
        return {c: 0.0 for c in cells}

    # 对照基因：随机选取表达量相近的基因
    all_genes = list(matrix.keys())
    control_genes = []
    for g in valid_genes:
        # 用该基因在细胞中的平均表达量来匹配对照基因
        g_exprs = [matrix[g].get(c, 0.0) for c in cells]
        g_mean = sum(g_exprs) / len(g_exprs) if g_exprs else 0.0
        # 选择表达量相近的基因作为对照
        candidates = sorted(all_genes,
                           key=lambda x: abs(sum(matrix[x].get(c, 0.0) for c in cells) / max(len(cells), 1) - g_mean))
        for cand in candidates:
            if cand not in valid_genes:
                control_genes.append(cand)
                break
        if len(control_genes) >= n_control:
            break

    if not control_genes:
        return {c: 0.0 for c in cells}

    for cell in cells:
        target_mean = sum(matrix[g].get(cell, 0.0) for g in valid_genes) / max(len(valid_genes), 1)
        control_mean = sum(matrix[c].get(cell, 0.0) for c in control_genes) / max(len(control_genes), 1)
        score[cell] = target_mean - control_mean

    return score


def classify_m1_m2(m1_score: dict, m2_score: dict, cells: list) -> dict:
    """根据M1/M2评分分类细胞"""
    classification = {}
    scores_diff = {c: m1_score.get(c, 0.0) - m2_score.get(c, 0.0) for c in cells}
    for cell in cells:
        # 如果M1评分显著高于M2 → M1-like
        # 如果M2评分显著高于M1 → M2-like
        # 否则 → Mixed/Unclassified
        diff = scores_diff[cell]
        if diff > 0.15:
            classification[cell] = "M1-like"
        elif diff < -0.15:
            classification[cell] = "M2-like"
        else:
            classification[cell] = "Mixed"
    return classification


def compute_ratio(classification: dict, group_map: dict) -> dict:
    """计算每组M1/M2比例"""
    from collections import defaultdict

    group_counts = defaultdict(lambda: {"M1-like": 0, "M2-like": 0, "Mixed": 0})
    group_total = defaultdict(int)

    for cell, pheno in classification.items():
        grp = group_map.get(cell, "Unknown")
        group_counts[grp][pheno] += 1
        group_total[grp] += 1

    results = {}
    for grp in group_counts:
        total = group_total[grp] or 1
        results[grp] = {
            "M1_pct": round(group_counts[grp]["M1-like"] / total * 100, 2),
            "M2_pct": round(group_counts[grp]["M2-like"] / total * 100, 2),
            "Mixed_pct": round(group_counts[grp]["Mixed"] / total * 100, 2),
            "M1_M2_ratio": round(
                (group_counts[grp]["M1-like"] + 1) / (group_counts[grp]["M2-like"] + 1), 3),
            "total_cells": total,
        }
    return results


def two_proportion_z_test(p1, p2, n1, n2):
    """两比例Z检验"""
    p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se if se > 0 else 0
    return z


# ---------- 输出 ----------

def print_report(results: dict, baseline_group: str = "control"):
    """输出M1/M2比例报告"""
    print("\n" + "=" * 65)
    print("  藏药单细胞药理学 — M1/M2巨噬细胞极化分析报告")
    print("=" * 65)

    print(f"\n{'组别':<15} {'总细胞数':<12} {'M1-like (%)':<15} {'M2-like (%)':<15} {'M1/M2 Ratio':<12} {'Mixed (%)':<12}")
    print("-" * 85)
    for grp in sorted(results.keys()):
        r = results[grp]
        print(f"{grp:<15} {r['total_cells']:<12} {r['M1_pct']:<15.2f} {r['M2_pct']:<15.2f} {r['M1_M2_ratio']:<12.3f} {r['Mixed_pct']:<12.2f}")

    # 两两比较（vs baseline）
    if baseline_group in results:
        baseline = results[baseline_group]
        print(f"\n  统计比较（vs {baseline_group}）：")
        print(f"{'对比组':<15} {'M1 Z值':<12} {'M2 Z值':<12} {'M1 P值 (粗略)':<15} {'解释':<20}")
        print("-" * 75)
        for grp in sorted(results.keys()):
            if grp == baseline_group:
                continue
            r = results[grp]
            z_m1 = two_proportion_z_test(
                r["M1_pct"] / 100, baseline["M1_pct"] / 100,
                r["total_cells"], baseline["total_cells"]
            )
            z_m2 = two_proportion_z_test(
                r["M2_pct"] / 100, baseline["M2_pct"] / 100,
                r["total_cells"], baseline["total_cells"]
            )
            direction_m1 = "↑ M1↑" if r["M1_M2_ratio"] > baseline["M1_M2_ratio"] else "↓ M1↓"
            print(f"{grp:<15} {z_m1:<+12.3f} {z_m2:<+12.3f} {'(参考)':<15} {direction_m1:<20}")
    
    print("\n" + "=" * 65)
    print("  注：M1/M2比例升高 → M1极化优势（促炎状态）")
    print("       M1/M2比例降低 → M2极化优势（抗炎/修复状态）")
    print("       精确P值请使用 Wilcoxon 秩和检验或 Fisher exact test")
    print("=" * 65)


def save_csv(results: dict, output_path: str):
    """将结果保存为CSV"""
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Group", "Total_Cells", "M1_pct", "M2_pct", "Mixed_pct", "M1_M2_Ratio"])
        for grp in sorted(results.keys()):
            r = results[grp]
            writer.writerow([grp, r["total_cells"], r["M1_pct"], r["M2_pct"], r["Mixed_pct"], r["M1_M2_ratio"]])
    print(f"\n  ✅ 结果已保存至: {output_path}")


# ---------- 主入口 ----------

def main():
    parser = argparse.ArgumentParser(description="藏药单细胞M1/M2极化分析")
    parser.add_argument("--input", required=True, help="输入CSV文件（表达矩阵）")
    parser.add_argument("--m1_genes", default="Nos2,Cd86,Cxcl9,Cxcl10,Tnf,Il6",
                        help="M1标志物基因列表（逗号分隔）")
    parser.add_argument("--m2_genes", default="Mrc1,Arg1,Il10,Cd163,Retnla,Chil3",
                        help="M2标志物基因列表（逗号分隔）")
    parser.add_argument("--group_col", default="condition",
                        help="分组列名")
    parser.add_argument("--output", default=None,
                        help="输出CSV文件路径（可选）")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"❌ 错误：输入文件不存在 {args.input}")
        sys.exit(1)

    print(f"📖 加载数据: {args.input}")
    m1_genes = [g.strip() for g in args.m1_genes.split(",")]
    m2_genes = [g.strip() for g in args.m2_genes.split(",")]
    print(f"  M1基因 ({len(m1_genes)}): {', '.join(m1_genes)}")
    print(f"  M2基因 ({len(m2_genes)}): {', '.join(m2_genes)}")

    matrix, cells, group_map = load_expression_matrix(args.input, args.group_col)
    print(f"  加载了 {len(matrix)} 个基因, {len(cells)} 个细胞")

    group_map = group_map or {c: "All" for c in cells}

    print("🧮 计算M1评分...")
    m1_score = calc_addmodule_score(matrix, cells, m1_genes)
    print("🧮 计算M2评分...")
    m2_score = calc_addmodule_score(matrix, cells, m2_genes)

    print("🔬 分类M1-like / M2-like 细胞...")
    classification = classify_m1_m2(m1_score, m2_score, cells)

    print("📊 计算各组比例...")
    results = compute_ratio(classification, group_map)

    print_report(results)

    if args.output:
        save_csv(results, args.output)
        # 同时输出每个细胞的评分
        score_path = Path(args.output).with_suffix(".cell_scores.csv")
        with open(score_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["cell_id", "group", "M1_score", "M2_score", "classification"])
            for cell in cells:
                writer.writerow([
                    cell,
                    group_map.get(cell, "Unknown"),
                    round(m1_score.get(cell, 0.0), 4),
                    round(m2_score.get(cell, 0.0), 4),
                    classification.get(cell, "Unknown")
                ])
        print(f"  ✅ 细胞评分已保存至: {score_path}")


if __name__ == "__main__":
    main()
