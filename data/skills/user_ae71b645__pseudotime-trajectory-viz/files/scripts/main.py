#!/usr/bin/env python3
"""
伪时间轨迹可视化工具（Pseudotime Trajectory Visualization Tool）

对单细胞数据进行拟时序（pseudotime）分析，可视化细胞从干细胞
向成熟细胞分化的发育轨迹。

Author: OpenClaw
Date: 2026-02-06
"""

import argparse
import json
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

import anndata
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# 屏蔽警告信息，保持输出简洁
warnings.filterwarnings('ignore')

# 设置 matplotlib 默认参数，以满足出版级图像质量要求
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 9


def parse_arguments():
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description='可视化单细胞发育轨迹（拟时序 / pseudotime）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  %(prog)s --input data.h5ad --output ./results
  %(prog)s --input data.h5ad --start-cell-type progenitor --method diffusion
  %(prog)s --input data.h5ad --genes SOX2,OCT4,NANOG --plot-genes
        """
    )

    # 必填参数
    parser.add_argument('--input', '-i', type=str, required=True,
                        help='输入 AnnData（.h5ad）文件路径')
    parser.add_argument('--output', '-o', type=str, default='./trajectory_output',
                        help='结果输出目录（默认：./trajectory_output）')

    # Embedding 与方法选择
    parser.add_argument('--embedding', type=str, default='umap',
                        choices=['umap', 'tsne', 'pca', 'diffmap'],
                        help='用于可视化的 embedding（默认：umap）')
    parser.add_argument('--method', type=str, default='diffusion',
                        choices=['diffusion', 'paga'],
                        help='轨迹推断方法（默认：diffusion）。'
                             '注：本脚本目前只实现了 diffusion（DPT）和 paga 两种方法，'
                             '不支持 slingshot / palantir。')

    # 轨迹相关参数
    parser.add_argument('--start-cell', type=str, default=None,
                        help='轨迹起点的根细胞（root cell）ID')
    parser.add_argument('--start-cell-type', type=str, default=None,
                        help='作为轨迹起点的细胞类型')
    parser.add_argument('--n-lineages', type=int, default=None,
                        help='预期的谱系分支数量（不指定则自动检测）')

    # 数据字段 key
    parser.add_argument('--cluster-key', type=str, default='leiden',
                        help='AnnData obs 中用于细胞聚类的字段名（默认：leiden）')
    parser.add_argument('--cell-type-key', type=str, default='cell_type',
                        help='AnnData obs 中细胞类型标注的字段名（默认：cell_type）')

    # 基因表达绘图
    parser.add_argument('--genes', type=str, default=None,
                        help='沿拟时序绘制表达趋势的基因名（英文逗号分隔）')
    parser.add_argument('--plot-genes', action='store_true',
                        help='生成沿轨迹的基因表达热图')
    parser.add_argument('--plot-branch', action='store_true', default=True,
                        help='显示谱系分支概率（注：该参数目前未在脚本逻辑中实际使用，'
                             '是遗留的无效参数，见下方“已知问题”说明）')

    # 输出选项
    parser.add_argument('--format', type=str, default='png',
                        choices=['png', 'pdf', 'svg'],
                        help='输出图像格式（默认：png）')
    parser.add_argument('--dpi', type=int, default=300,
                        help='图像分辨率（默认：300）')

    # 分析参数
    parser.add_argument('--n-pcs', type=int, default=30,
                        help='用于分析的主成分数量（默认：30）')
    parser.add_argument('--n-neighbors', type=int, default=15,
                        help='构建邻接图时使用的邻居数量（默认：15）')
    parser.add_argument('--diffmap-components', type=int, default=5,
                        help='扩散图（diffusion map）成分数量（默认：5）')

    return parser.parse_args()


def load_data(input_path):
    """从文件加载 AnnData 对象。"""
    print(f"正在从 {input_path} 加载数据...")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"未找到输入文件：{input_path}")

    try:
        adata = sc.read_h5ad(input_path)
        print(f"已加载 {adata.n_obs} 个细胞，{adata.n_vars} 个基因")
        return adata
    except Exception as e:
        raise ValueError(f"加载 AnnData 文件出错：{e}")


def preprocess_data(adata, args):
    """为轨迹分析预处理数据。"""
    print("正在预处理数据...")

    # 检查所需的注释字段是否存在
    if args.cluster_key not in adata.obs.columns:
        print(f"警告：未找到聚类字段 '{args.cluster_key}'，将自动计算 Leiden 聚类...")
        if 'neighbors' not in adata.uns:
            sc.pp.neighbors(adata, n_neighbors=args.n_neighbors, n_pcs=args.n_pcs)
        sc.tl.leiden(adata, key_added=args.cluster_key)

    # 若指定的 embedding 不存在则计算
    embedding_key = f'X_{args.embedding}'
    if embedding_key not in adata.obsm.keys():
        print(f"正在计算 {args.embedding.upper()} embedding...")
        if 'neighbors' not in adata.uns:
            sc.pp.neighbors(adata, n_neighbors=args.n_neighbors, n_pcs=args.n_pcs)

        if args.embedding == 'umap':
            sc.tl.umap(adata)
        elif args.embedding == 'tsne':
            sc.tl.tsne(adata)
        elif args.embedding == 'diffmap':
            sc.tl.diffmap(adata, n_comps=args.diffmap_components)
        # 注：--embedding pca 依赖 adata.obsm['X_pca']，该字段通常由
        # sc.tl.pca 生成；若输入数据未预先计算 PCA，这里不会自动补算，
        # 后续绘图步骤在缺少 X_pca 时会报错。建议预处理阶段先运行 sc.tl.pca。

    # 若未计算高变基因则补算
    if 'highly_variable' not in adata.var.columns:
        print("正在计算高变基因（highly variable genes）...")
        sc.pp.highly_variable_genes(adata, n_top_genes=2000)

    return adata


def find_root_cell(adata, args):
    """确定轨迹推断所需的根细胞（root cell）。"""
    print("正在识别根细胞...")

    root_cell = None

    # 方式一：使用用户指定的细胞 ID
    if args.start_cell:
        if args.start_cell in adata.obs_names:
            root_cell = args.start_cell
            print(f"使用指定的根细胞：{root_cell}")
            return root_cell
        else:
            print(f"警告：未在数据中找到指定的起始细胞 '{args.start_cell}'")

    # 方式二：使用细胞类型注释
    if args.start_cell_type and args.cell_type_key in adata.obs.columns:
        cell_types = adata.obs[args.cell_type_key].values
        if args.start_cell_type in cell_types:
            # 在该细胞类型中，寻找干性标记基因表达量最高的细胞
            stem_markers = ['SOX2', 'POU5F1', 'NANOG', 'PROM1', 'THY1', 'KIT']
            available_markers = [g for g in stem_markers if g in adata.var_names]

            mask = cell_types == args.start_cell_type
            if available_markers:
                expr = adata[mask, available_markers].X.mean(axis=1)
                if hasattr(expr, 'A1'):
                    expr = expr.A1
                root_idx = np.where(mask)[0][np.argmax(expr)]
            else:
                root_idx = np.where(mask)[0][0]

            root_cell = adata.obs_names[root_idx]
            print(f"已从细胞类型 '{args.start_cell_type}' 中选出根细胞：{root_cell}")
            return root_cell
        else:
            print(f"警告：未找到细胞类型 '{args.start_cell_type}'")

    # 方式三：基于干性标记基因自动检测
    stem_markers = ['SOX2', 'POU5F1', 'OCT4', 'NANOG', 'PROM1', 'THY1', 'KIT', 'CD34']
    available_markers = [g for g in stem_markers if g in adata.var_names]

    if available_markers:
        print(f"使用以下干性标记基因寻找根细胞：{available_markers}")
        expr = adata[:, available_markers].X.mean(axis=1)
        if hasattr(expr, 'A1'):
            expr = expr.A1
        root_idx = np.argmax(expr)
        root_cell = adata.obs_names[root_idx]
        print(f"自动选定的根细胞：{root_cell}")
    else:
        # 兜底方案：使用第一个细胞
        root_cell = adata.obs_names[0]
        print(f"未找到任何标记基因，使用第一个细胞作为根细胞：{root_cell}")

    return root_cell


def compute_diffusion_pseudotime(adata, root_cell, args):
    """使用 scanpy 计算扩散拟时序（Diffusion Pseudotime，DPT）。"""
    print("正在计算扩散拟时序（DPT）...")

    # 计算扩散图（diffusion map）
    sc.tl.diffmap(adata, n_comps=args.diffmap_components)

    # 获取根细胞索引
    root_idx = np.where(adata.obs_names == root_cell)[0][0]
    adata.uns['iroot'] = root_idx

    # 计算 DPT
    sc.tl.dpt(adata, n_dcs=args.diffmap_components)

    # 获取拟时序值
    pseudotime = adata.obs['dpt_pseudotime'].values

    print(f"拟时序取值范围：{pseudotime.min():.3f} - {pseudotime.max():.3f}")

    # 基于聚类推断谱系
    n_lineages = args.n_lineages or min(3, adata.obs[args.cluster_key].nunique())

    # 基于终末分支的简化谱系分配
    lineage_assignments = assign_lineages(adata, n_lineages, args)
    adata.obs['lineage'] = lineage_assignments

    return adata


def assign_lineages(adata, n_lineages, args):
    """基于轨迹分支情况为细胞分配谱系。

    注：这是一种简化的谱系分配启发式方法，仅按拟时序值把
    [0, 1] 区间等分为 n_lineages 段区间，逐段贴上 lineage_i 标签，
    并不基于真正的分支拓扑结构（如 PAGA 连通图或扩散图上的
    分叉点）。对于存在多个真实分支的轨迹，这种按拟时序值分箱的方式
    可能会把不同分支上拟时序相近的细胞错误地划入同一谱系,
    也无法处理断裂（disconnected）的组成部分。如需更严谨的谱系
    分配，建议结合 PAGA 连通性或专门的谱系推断方法（如 Palantir）。
    """
    # 基于聚类和拟时序的简化谱系分配
    clusters = adata.obs[args.cluster_key].values
    pseudotime = adata.obs['dpt_pseudotime'].values

    # 找出终末簇（拟时序值较高的簇）
    cluster_pseudotime = {}
    for c in np.unique(clusters):
        mask = clusters == c
        cluster_pseudotime[c] = pseudotime[mask].mean()

    # 按拟时序值对簇排序
    sorted_clusters = sorted(cluster_pseudotime.items(), key=lambda x: x[1])

    # 分配谱系
    lineages = np.array(['lineage_1'] * adata.n_obs, dtype=object)

    if n_lineages > 1:
        # 简单启发式：按拟时序值把细胞分配到不同谱系区间
        pseudotime_bins = np.linspace(0, 1, n_lineages + 1)
        for i in range(n_lineages):
            mask = (pseudotime >= pseudotime_bins[i]) & (pseudotime < pseudotime_bins[i+1])
            lineages[mask] = f'lineage_{i+1}'

    return lineages


def compute_paga_trajectory(adata, root_cell, args):
    """使用 PAGA（Partition-based Graph Abstraction，基于分区的图抽象）计算轨迹。"""
    print("正在计算 PAGA 轨迹...")

    # 计算 PAGA
    sc.tl.paga(adata, groups=args.cluster_key)

    # 获取根簇（root cluster）
    root_idx = np.where(adata.obs_names == root_cell)[0][0]
    root_cluster = adata.obs[args.cluster_key].iloc[root_idx]

    # 修正说明：原版这里会调用 sc.tl.draw_graph(adata, init_pos=args.embedding)，
    # 但 init_pos 期望的是 'paga'、布尔值或某个真实存在的 .obsm 键
    # （如 'X_umap'），而不是裸的 embedding 名字（如 'umap'）。传入 'umap'
    # 会被当作真值，落入需要先调用 sc.pl.paga() 生成 adata.uns['paga']['pos']
    # 的分支，若未先绘图则直接报错；即便不报错，其计算结果
    # （adata.obsm['X_draw_graph_fa']）在后续绘图代码中也从未被使用。
    # 因此这是一处死代码 + 潜在崩溃点，已删除，不影响实际功能。

    # 基于 PAGA 距离估算拟时序
    paga_distances = adata.uns['paga']['connectivities'].toarray()

    # 简化拟时序：与根簇的距离
    cluster_order = list(adata.obs[args.cluster_key].unique())
    if root_cluster in cluster_order:
        root_idx_cluster = cluster_order.index(root_cluster)
    else:
        root_idx_cluster = 0

    # 基于簇分配拟时序
    cluster_pseudotime = {}
    for i, c in enumerate(cluster_order):
        # 用簇序号距离作为拟时序的代理指标
        cluster_pseudotime[c] = min(1.0, abs(i - root_idx_cluster) / max(1, len(cluster_order) - 1))

    pseudotime = np.array([cluster_pseudotime[c] for c in adata.obs[args.cluster_key]])
    pseudotime = pseudotime + np.random.normal(0, 0.05, len(pseudotime))  # 加入随机噪声
    pseudotime = np.clip(pseudotime, 0, 1)

    adata.obs['paga_pseudotime'] = pseudotime
    adata.obs['dpt_pseudotime'] = pseudotime  # 复用同一字段名以保持后续代码一致

    # 分配谱系
    n_lineages = args.n_lineages or min(3, len(cluster_order))
    lineage_assignments = assign_lineages(adata, n_lineages, args)
    adata.obs['lineage'] = lineage_assignments

    return adata


def plot_trajectory(adata, args, output_dir):
    """生成主轨迹可视化图。"""
    print("正在生成轨迹图...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    embedding_key = f'X_{args.embedding}'

    # 子图1：按拟时序着色的 embedding
    ax = axes[0, 0]
    sc.pl.embedding(
        adata, basis=args.embedding, color='dpt_pseudotime',
        ax=ax, show=False, color_map='viridis_r',
        title='拟时序轨迹'
    )

    # 子图2：按细胞簇着色的 embedding
    ax = axes[0, 1]
    sc.pl.embedding(
        adata, basis=args.embedding, color=args.cluster_key,
        ax=ax, show=False, legend_loc='on data',
        title='细胞簇'
    )

    # 子图3：按谱系着色的 embedding
    ax = axes[1, 0]
    sc.pl.embedding(
        adata, basis=args.embedding, color='lineage',
        ax=ax, show=False,
        title='谱系分配'
    )

    # 子图4：拟时序分布
    ax = axes[1, 1]
    pseudotime = adata.obs['dpt_pseudotime'].values
    for lineage in adata.obs['lineage'].unique():
        mask = adata.obs['lineage'] == lineage
        ax.hist(pseudotime[mask], bins=30, alpha=0.6, label=lineage, density=True)
    ax.set_xlabel('拟时序（Pseudotime）')
    ax.set_ylabel('密度')
    ax.set_title('各谱系拟时序分布')
    ax.legend()

    plt.tight_layout()
    output_path = os.path.join(output_dir, f'trajectory_plot.{args.format}')
    plt.savefig(output_path, dpi=args.dpi, bbox_inches='tight')
    plt.close()

    print(f"已保存：{output_path}")
    return output_path


def plot_paga_graph(adata, args, output_dir):
    """绘制 PAGA 图（若已计算）。"""
    if 'paga' not in adata.uns:
        return None

    print("正在生成 PAGA 图...")

    # 修正说明：原版调用 sc.pl.paga_compare(..., ax=axes[1], ...) 会报错——
    # paga_compare 内部会自建双子图（scatter + graph），不接受外部传入 ax，
    # 与其内部转发给 paga() 的 ax 参数冲突，导致 TypeError。
    # 这里改为绘制单张 PAGA 连通图，并用 embedding 上按簇着色的散点图作对照。
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 左图：PAGA 簇间连通图
    sc.pl.paga(adata, ax=axes[0], show=False,
               title='PAGA 图（簇间连通性）')

    # 右图：embedding 上按簇着色，便于与 PAGA 图对照
    sc.pl.embedding(
        adata, basis=args.embedding, color=args.cluster_key,
        ax=axes[1], show=False, legend_loc='on data',
        title='细胞簇（embedding 对照）'
    )

    plt.tight_layout()
    output_path = os.path.join(output_dir, f'paga_graph.{args.format}')
    plt.savefig(output_path, dpi=args.dpi, bbox_inches='tight')
    plt.close()

    print(f"已保存：{output_path}")
    return output_path


def plot_gene_expression(adata, genes, args, output_dir):
    """绘制基因沿拟时序的表达趋势。"""
    if not genes:
        return []

    print(f"正在为 {len(genes)} 个基因生成表达趋势图...")

    output_files = []

    # 创建基因趋势子目录
    gene_trends_dir = os.path.join(output_dir, 'gene_trends')
    os.makedirs(gene_trends_dir, exist_ok=True)

    # 筛选数据中实际存在的基因
    available_genes = [g for g in genes if g in adata.var_names]
    missing_genes = set(genes) - set(available_genes)
    if missing_genes:
        print(f"警告：数据中未找到以下基因：{missing_genes}")

    if not available_genes:
        print("没有可绘制的有效基因")
        return output_files

    # 逐个基因绘图
    for gene in available_genes:
        fig, ax = plt.subplots(figsize=(8, 5))

        pseudotime = adata.obs['dpt_pseudotime'].values
        expression = adata[:, gene].X.toarray().flatten() if hasattr(adata[:, gene].X, 'toarray') else adata[:, gene].X.flatten()

        # 散点图叠加趋势线
        for lineage in adata.obs['lineage'].unique():
            mask = adata.obs['lineage'] == lineage
            ax.scatter(pseudotime[mask], expression[mask], alpha=0.3, s=10, label=lineage)

            # 拟合平滑样条曲线
            if mask.sum() > 10:
                from scipy.interpolate import UnivariateSpline
                idx = np.argsort(pseudotime[mask])
                x = pseudotime[mask][idx]
                y = expression[mask][idx]
                try:
                    spline = UnivariateSpline(x, y, s=len(x))
                    x_smooth = np.linspace(x.min(), x.max(), 100)
                    ax.plot(x_smooth, spline(x_smooth), linewidth=2, label=f'{lineage} 趋势线')
                except:
                    pass

        ax.set_xlabel('拟时序（Pseudotime）')
        ax.set_ylabel(f'{gene} 表达量')
        ax.set_title(f'{gene} 沿轨迹的表达变化')
        ax.legend(loc='best')

        output_path = os.path.join(gene_trends_dir, f'{gene}_trend.{args.format}')
        plt.tight_layout()
        plt.savefig(output_path, dpi=args.dpi, bbox_inches='tight')
        plt.close()
        output_files.append(output_path)

    # 合并热图
    fig, ax = plt.subplots(figsize=(10, 8))

    # 准备热图数据
    expr_matrix = []
    gene_labels = []

    for gene in available_genes:
        expression = adata[:, gene].X.toarray().flatten() if hasattr(adata[:, gene].X, 'toarray') else adata[:, gene].X.flatten()
        expr_matrix.append(expression)
        gene_labels.append(gene)

    expr_matrix = np.array(expr_matrix)

    # 按拟时序值对细胞排序
    pseudotime = adata.obs['dpt_pseudotime'].values
    sort_idx = np.argsort(pseudotime)
    expr_matrix_sorted = expr_matrix[:, sort_idx]

    # 按基因做归一化（z-score）
    expr_matrix_norm = (expr_matrix_sorted - expr_matrix_sorted.mean(axis=1, keepdims=True)) / (
        expr_matrix_sorted.std(axis=1, keepdims=True) + 1e-8
    )

    # 绘制热图
    sns.heatmap(expr_matrix_norm, xticklabels=False, yticklabels=gene_labels,
                cmap='RdBu_r', center=0, ax=ax, cbar_kws={'label': 'Z-score'})
    ax.set_xlabel('细胞（按拟时序排序）')
    ax.set_title('沿拟时序的基因表达热图')

    output_path = os.path.join(output_dir, f'gene_expression_heatmap.{args.format}')
    plt.tight_layout()
    plt.savefig(output_path, dpi=args.dpi, bbox_inches='tight')
    plt.close()
    output_files.append(output_path)

    print(f"已保存 {len(output_files)} 张基因表达图")
    return output_files


def save_results(adata, args, output_dir, root_cell):
    """将分析结果保存到文件。"""
    print("正在保存结果...")

    # 保存拟时序数值
    results_df = pd.DataFrame({
        'cell_id': adata.obs_names,
        'cluster': adata.obs[args.cluster_key].values,
        'pseudotime': adata.obs['dpt_pseudotime'].values,
        'lineage': adata.obs['lineage'].values
    })

    if args.cell_type_key in adata.obs.columns:
        results_df['cell_type'] = adata.obs[args.cell_type_key].values

    results_path = os.path.join(output_dir, 'pseudotime_values.csv')
    results_df.to_csv(results_path, index=False)
    print(f"已保存：{results_path}")

    # 保存分析报告
    lineages = {}
    for lineage in adata.obs['lineage'].unique():
        mask = adata.obs['lineage'] == lineage
        lineages[lineage] = {
            'cell_count': int(mask.sum()),
            'mean_pseudotime': float(adata.obs['dpt_pseudotime'][mask].mean()),
            'clusters': list(adata.obs[args.cluster_key][mask].unique())
        }

    report = {
        'analysis_date': datetime.now().isoformat(),
        'method': args.method,
        'n_cells': adata.n_obs,
        'n_genes': adata.n_vars,
        'n_lineages': len(adata.obs['lineage'].unique()),
        'root_cell': root_cell,
        'pseudotime_range': [
            float(adata.obs['dpt_pseudotime'].min()),
            float(adata.obs['dpt_pseudotime'].max())
        ],
        'lineages': lineages,
        'parameters': {
            'embedding': args.embedding,
            'n_pcs': args.n_pcs,
            'n_neighbors': args.n_neighbors,
            'cluster_key': args.cluster_key
        }
    }

    report_path = os.path.join(output_dir, 'analysis_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"已保存：{report_path}")

    # 保存更新后的 AnnData 对象
    adata_path = os.path.join(output_dir, 'trajectory_data.h5ad')
    adata.write(adata_path)
    print(f"已保存：{adata_path}")

    return results_path, report_path, adata_path


def main():
    """主分析流程。"""
    args = parse_arguments()

    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    print(f"输出目录：{args.output}")

    try:
        # 加载数据
        adata = load_data(args.input)

        # 预处理
        adata = preprocess_data(adata, args)

        # 寻找根细胞
        root_cell = find_root_cell(adata, args)

        # 计算轨迹
        if args.method == 'diffusion':
            adata = compute_diffusion_pseudotime(adata, root_cell, args)
        elif args.method == 'paga':
            adata = compute_paga_trajectory(adata, root_cell, args)

        # 生成可视化图像
        plot_trajectory(adata, args, args.output)

        if args.method == 'paga':
            plot_paga_graph(adata, args, args.output)

        # 基因表达图
        if args.genes or args.plot_genes:
            gene_list = args.genes.split(',') if args.genes else []
            if not gene_list and args.plot_genes:
                # 使用高变基因
                if 'highly_variable' in adata.var.columns:
                    gene_list = adata.var_names[adata.var['highly_variable']][:20].tolist()
            plot_gene_expression(adata, gene_list, args, args.output)

        # 保存结果
        save_results(adata, args, args.output, root_cell)

        print("\n" + "="*50)
        print("分析完成！")
        print(f"结果已保存至：{args.output}")
        print("="*50)

        return 0

    except Exception as e:
        print(f"\n错误：{e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
