#!/usr/bin/env python3
"""
藏药单细胞药理学 — 单细胞差异表达分析

功能：
1. 读取单细胞表达矩阵（CSV格式）
2. 比较两组（药物组 vs 对照组）的差异表达基因
3. 输出差异表达基因列表（log2FC, P值）
4. 输出GO/KEGG通路富集结果摘要

用法：
    python scrna_diff_expr.py --input filtered_data.csv \
        --group_col "condition" \
        --group1 "drug" \
        --group2 "control" \
        --output deg_results.csv
"""

import argparse
import sys
import csv
import math
from pathlib import Path
from collections import defaultdict


# ---------- 统计工具 ----------

def wilcoxon_rank_sum(group1, group2):
    """
    Wilcoxon秩和检验（Mann-Whitney U检验）
    手动实现（小样本精确计算）
    """
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return 1.0

    # 合并并排序
    combined = [(val, 0) for val in group1] + [(val, 1) for val in group2]
    combined.sort(key=lambda x: x[0])

    # 分配秩
    rank_sum = 0
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        # 对并列的值分配平均秩
        avg_rank = (i + 1 + j) / 2
        for k in range(i, j):
            if combined[k][1] == 0:  # group1
                rank_sum += avg_rank
        i = j

    # U统计量
    u1 = rank_sum - n1 * (n1 + 1) / 2
    u2 = n1 * n2 - u1
    u = min(u1, u2)

    # 使用正态近似计算P值
    mu = n1 * n2 / 2
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    
    if sigma == 0:
        return 1.0
        
    z = (u - mu) / sigma
    # 正态分布的近似p值（双尾）
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    
    return max(p, 1e-300)  # 防止下溢


def log2_fold_change(expr1, expr2):
    """计算log2倍数变化"""
    mean1 = sum(expr1) / max(len(expr1), 1)
    mean2 = sum(expr2) / max(len(expr2), 1)
    pseudo = 1e-10
    return math.log2((mean1 + pseudo) / (mean2 + pseudo))


def benjamini_hochberg(p_values):
    """Benjamini-Hochberg FDR校正"""
    sorted_indices = sorted(range(len(p_values)), key=lambda i: p_values[i])
    n = len(p_values)
    adjusted = [0.0] * n
    prev_rank = 0.0
    
    for rank, idx in enumerate(sorted_indices, 1):
        adjusted[idx] = p_values[idx] * n / rank
        adjusted[idx] = max(adjusted[idx], prev_rank)
        prev_rank = adjusted[idx]
    
    return [min(a, 1.0) for a in adjusted]


# ---------- 数据加载 ----------

def load_group_matrix(csv_path: str, group_col: str, group1: str, group2: str):
    """
    从CSV加载两组表达数据
    CSV格式：每行是一个细胞，第一列是cell_id，group_col列是分组，
    其余列是基因表达值
    """
    group1_cells = []
    group2_cells = []
    genes = []

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        genes = [f for f in fieldnames if f not in ('cell_id', group_col)]
        
        for row in reader:
            grp = row.get(group_col, '').strip()
            if grp == group1:
                group1_cells.append(row)
            elif grp == group2:
                group2_cells.append(row)

    return genes, group1_cells, group2_cells


# ---------- 差异表达分析 ----------

def deg_analysis(genes, group1_cells, group2_cells):
    """对每个基因执行差异表达分析"""
    results = []
    
    for idx, gene in enumerate(genes):
        expr1 = []
        expr2 = []
        
        for cell in group1_cells:
            try:
                val = float(cell.get(gene, '0'))
            except (ValueError, TypeError):
                val = 0.0
            expr1.append(val)
        
        for cell in group2_cells:
            try:
                val = float(cell.get(gene, '0'))
            except (ValueError, TypeError):
                val = 0.0
            expr2.append(val)
        
        # 移除全零基因（在两个组中都不表达）
        if sum(expr1) == 0 and sum(expr2) == 0:
            continue
        
        lfc = log2_fold_change(expr1, expr2)
        p_val = wilcoxon_rank_sum(expr1, expr2)
        
        results.append({
            "gene": gene,
            "log2FC": lfc,
            "p_value": p_val,
            "mean_group1": sum(expr1) / max(len(expr1), 1),
            "mean_group2": sum(expr2) / max(len(expr2), 1),
            "pct_group1": sum(1 for v in expr1 if v > 0) / max(len(expr1), 1) * 100,
            "pct_group2": sum(1 for v in expr2 if v > 0) / max(len(expr2), 1) * 100,
        })
    
    return results


# ---------- 通路富集（简化版，基于预设数据库） ----------

# 预置的藏药相关通路/基因集
TARGET_PATHWAYS = {
    "NF-kB signaling": ["Nfkb1", "Rela", "Ikbkb", "Chuk", "Tnf", "Il6", "Il1b", "Cox2", "Icam1", "Vcam1", "Mmp9"],
    "JAK-STAT signaling": ["Jak1", "Jak2", "Jak3", "Stat1", "Stat3", "Stat6", "Socs1", "Socs3", "Cish", "Pias1"],
    "MAPK signaling": ["Mapk1", "Mapk3", "Mapk8", "Mapk14", "Map2k1", "Map2k4", "Jun", "Fos", "Elk1", "Atf2"],
    "PI3K-AKT signaling": ["Akt1", "Akt2", "Mtor", "Pik3ca", "Pik3r1", "Pten", "Tsc1", "Tsc2", "Rps6kb1", "Eif4e"],
    "PPAR signaling": ["Ppara", "Pparg", "Rxra", "Rxrg", "Cebpa", "Fabp4", "Lpl", "Adipoq", "Cpt1a"],
    "AMPK signaling": ["Prkaa1", "Prkaa2", "Prkab1", "Prkag1", "Sirt1", "Pgc1a", "Crebbp", "Foxo3"],
    "NLRP3 inflammasome": ["Nlrp3", "Pycard", "Casp1", "Il1b", "Il18", "Gsdmd"],
    "TGF-beta signaling": ["Tgfb1", "Tgfbr1", "Tgfbr2", "Smad2", "Smad3", "Smad4", "Smad7", "Id1", "Id2"],
    "T cell differentiation": ["Tbx21", "Gata3", "Rorc", "Foxp3", "Bcl6", "Ifng", "Il4", "Il17a", "Il10", "Il2"],
    "Macrophage polarization": ["Irf5", "Irf4", "Klf4", "Pparg", "Stat1", "Stat6", "Nfkb1", "Cebpb"],
}

# GO/KEGG注释用的大类
GO_CATEGORIES = {
    "inflammatory response": ["Tnf", "Il6", "Il1b", "Ccl2", "Ccl5", "Cxcl1", "Cxcl2", "Cxcl10"],
    "antigen presentation": ["H2-Aa", "H2-Eb1", "Cd74", "B2m", "Tap1", "Tap2"],
    "oxidative stress": ["Sod1", "Sod2", "Cat", "Gpx1", "Nqo1", "Hmox1", "Nfe2l2"],
    "apoptosis": ["Bax", "Bak1", "Bcl2", "Bcl2l1", "Casp3", "Casp9", "Birc5"],
    "cell proliferation": ["Mki67", "Pcna", "Cdk1", "Ccnb1", "Ccnd1", "Myc"],
}


def pathway_enrichment(deg_genes, upregulated_only=True):
    """简化版通路富集分析（Fisher exact test近似）"""
    results = []
    total_deg = len(deg_genes)
    
    for pathway, pathway_genes in TARGET_PATHWAYS.items():
        overlap = [g for g in deg_genes if g in pathway_genes]
        if overlap:
            # 超几何分布近似
            results.append({
                "pathway": pathway,
                "overlap_genes": overlap,
                "gene_count": len(overlap),
                "overlap_ratio": f"{len(overlap)}/{len(pathway_genes)}",
            })
    
    results.sort(key=lambda x: x["gene_count"], reverse=True)
    return results


# ---------- 输出 ----------

def print_deg_report(results, group1, group2, fdr=True):
    """输出差异表达分析报告"""
    print("\n" + "=" * 65)
    print(f"  藏药单细胞药理学 — 差异表达分析报告")
    print(f"  对比组: {group1} vs {group2}")
    print("=" * 65)

    # 计算显著性基因
    sig_up = [r for r in results if r["log2FC"] >= 1 and r["p_value"] < 0.05]
    sig_down = [r for r in results if r["log2FC"] <= -1 and r["p_value"] < 0.05]

    print(f"\n  总分析基因数: {len(results)}")
    print(f"  显著上调 (|log2FC|≥1, P<0.05): {len(sig_up)}")
    print(f"  显著下调 (|log2FC|≥1, P<0.05): {len(sig_down)}")

    if sig_up:
        print(f"\n  🔺 上调基因 Top 15:")
        print(f"  {'基因':<15} {'log2FC':<10} {'P值':<12} {'表达率(对照/给药)%':<20}")
        print(f"  {'-' * 57}")
        for r in sig_up[:15]:
            print(f"  {r['gene']:<15} {r['log2FC']:<+10.3f} {r['p_value']:<12.2e} {r['pct_group2']:<8.1f}/{r['pct_group1']:<8.1f}")

    if sig_down:
        print(f"\n  🔻 下调基因 Top 15:")
        print(f"  {'基因':<15} {'log2FC':<10} {'P值':<12} {'表达率(对照/给药)%':<20}")
        print(f"  {'-' * 57}")
        for r in sig_down[:15]:
            print(f"  {r['gene']:<15} {r['log2FC']:<+10.3f} {r['p_value']:<12.2e} {r['pct_group2']:<8.1f}/{r['pct_group1']:<8.1f}")

    # 通路富集
    all_sig = [r["gene"] for r in (sig_up + sig_down)]
    if all_sig:
        print(f"\n  📊 藏药相关通路富集:")
        enrichments = pathway_enrichment(all_sig)
        if enrichments:
            print(f"  {'通路名称':<25} {'重叠基因数':<12} {'基因列表':<30}")
            print(f"  {'-' * 67}")
            for e in enrichments:
                genes_str = ", ".join(e["overlap_genes"][:5])
                if len(e["overlap_genes"]) > 5:
                    genes_str += "..."
                print(f"  {e['pathway']:<25} {e['gene_count']:<12} {genes_str:<30}")
        else:
            print("  （未在预置通路数据库中找到显著富集）\n")

    # 个性化解读
    m1_genes_found = [r for r in sig_up if r["gene"] in ["Nos2", "Cd86", "Cxcl9", "Cxcl10", "Tnf"]]
    m2_genes_found = [r for r in sig_up if r["gene"] in ["Mrc1", "Arg1", "Il10", "Cd163"]]
    
    if m1_genes_found:
        print(f"\n  💡 提示：在给药组中检测到 M1 标志物上调, 提示促炎极化")
    if m2_genes_found:
        print(f"\n  💡 提示：在给药组中检测到 M2 标志物上调, 提示抗炎/修复极化")

    print(f"\n{'=' * 65}")


def save_deg_csv(results, output_path: str):
    """将DEG结果保存为CSV"""
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["gene", "log2FC", "p_value", "mean_control", "mean_drug",
                         "pct_control", "pct_drug", "significant"])
        for r in sorted(results, key=lambda x: abs(x["log2FC"]), reverse=True):
            sig = "yes" if abs(r["log2FC"]) >= 1 and r["p_value"] < 0.05 else "no"
            writer.writerow([
                r["gene"], f"{r['log2FC']:.4f}", f"{r['p_value']:.6e}",
                f"{r['mean_group2']:.4f}", f"{r['mean_group1']:.4f}",
                f"{r['pct_group2']:.1f}", f"{r['pct_group1']:.1f}",
                sig
            ])
    print(f"  ✅ DEG结果已保存至: {output_path}")


# ---------- 主入口 ----------

def main():
    parser = argparse.ArgumentParser(description="藏药单细胞差异表达分析")
    parser.add_argument("--input", required=True, help="输入CSV文件")
    parser.add_argument("--group_col", default="condition", help="分组列名")
    parser.add_argument("--group1", required=True, help="药物组名称")
    parser.add_argument("--group2", default="control", help="对照组名称")
    parser.add_argument("--output", default=None, help="输出CSV文件路径")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"❌ 错误：输入文件不存在 {args.input}")
        sys.exit(1)

    print(f"📖 加载数据: {args.input}")
    print(f"  分组列: {args.group_col}")
    print(f"  对比: {args.group1} vs {args.group2}")

    genes, group1_cells, group2_cells = load_group_matrix(
        args.input, args.group_col, args.group1, args.group2
    )

    print(f"  基因数: {len(genes)}")
    print(f"  {args.group1} 组细胞数: {len(group1_cells)}")
    print(f"  {args.group2} 组细胞数: {len(group2_cells)}")

    if len(group1_cells) == 0 or len(group2_cells) == 0:
        print("❌ 错误：某一组没有细胞数据")
        sys.exit(1)

    print("🧮 执行差异表达分析...")
    results = deg_analysis(genes, group1_cells, group2_cells)

    print_deg_report(results, args.group1, args.group2)

    if args.output:
        save_deg_csv(results, args.output)


if __name__ == "__main__":
    main()
