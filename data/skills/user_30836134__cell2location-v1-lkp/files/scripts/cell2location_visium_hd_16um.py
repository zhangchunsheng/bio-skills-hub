#!/usr/bin/env python3

# Author: LKP <kunpeng.liao@abiosciences.com>
# Date:   2026-08-18

# -*- coding: utf-8 -*-
"""
Cell2location Visium HD 16um 空间反卷积分析 - 最终优化版

使用方法:
    python cell2location_visium_hd_16um.py

环境要求:
    - Python 3.8+
    - cell2location >= 0.3.0
    - scanpy, anndata, pandas, numpy, matplotlib
    - PyTorch with CUDA (推荐)
"""

import os
import sys
import numpy as np
import pandas as pd

# ========== 配置区域（请根据实际数据修改） ==========
USER_DATA_DIR      = "your/data/directory"          # TODO: 修改为你的数据根目录
SC_FILENAME        = "scRNA.h5ad"                    # TODO: 单细胞 h5ad 文件名
SPATIAL_SUBDIR     = "binned_outputs/square_016um"   # 空间数据子目录
CELL_TYPE_COL      = "cell_type"                     # TODO: 修改为你的细胞类型列名
OUTPUT_DIR         = "cell2location_16um_results"    # 输出目录
# =====================================================
import scanpy as sc
import anndata
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.io import mmread
from datetime import datetime

# cell2location导入
import cell2location
from cell2location.utils.filtering import filter_genes
from cell2location.models import RegressionModel
from cell2location.models import Cell2location
import torch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# =============================================================================
# 配置参数 - 根据您的数据修改这些路径
# =============================================================================

# 输入数据路径
SC_DATA_DIR = "I:/TRAE skill 数据分析/测试数据/scRNA-seq data"
SPATIAL_DATA_DIR = "os.path.join(USER_DATA_DIR, SPATIAL_SUBDIR)"

# 输出目录
OUTPUT_DIR = OUTPUT_DIR

# 分析参数
N_SPOTS_SAMPLE = 10000          # 空间数据采样数
REFERENCE_EPOCHS = 250          # 参考模型训练轮数
SPATIAL_EPOCHS = 1000           # 空间模型训练轮数
N_CELLS_PER_LOCATION = 8        # 16um分辨率每个spot的预期细胞数

# =============================================================================
# 主分析流程
# =============================================================================

def main():
    """主分析函数"""
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 80)
    print("Cell2location Visium HD 16um 空间反卷积分析")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # -------------------------------------------------------------------------
    # 步骤1: 检查计算资源
    # -------------------------------------------------------------------------
    print("\n【步骤1/7】检查计算资源...")
    if torch.cuda.is_available():
        device = 'cuda'
        gpu_name = torch.cuda.get_device_name(0)
        print(f"   ✓ GPU可用: {gpu_name}")
        print(f"   ✓ CUDA版本: {torch.version.cuda}")
    else:
        device = 'cpu'
        print("   ⚠ GPU不可用，使用CPU计算（速度较慢）")
    
    # -------------------------------------------------------------------------
    # 步骤2: 读取单细胞参考数据
    # -------------------------------------------------------------------------
    print("\n【步骤2/7】读取单细胞参考数据...")
    
    # 检查导出文件是否存在
    export_files = ['sc_counts.mtx', 'sc_genes.txt', 'sc_cells.txt', 'sc_meta.csv']
    files_exist = all(os.path.exists(f) for f in export_files)
    
    if files_exist:
        print("   读取已导出的单细胞数据...")
        counts_matrix = mmread("sc_counts.mtx").T.tocsr()
        genes = pd.read_csv("sc_genes.txt", header=None)[0].tolist()
        cells = pd.read_csv("sc_cells.txt", header=None)[0].tolist()
        meta_df = pd.read_csv("sc_meta.csv")
        
        adata_ref = anndata.AnnData(
            X=counts_matrix,
            obs=pd.DataFrame({'cell_type': meta_df['cell_type'].values}, index=cells),
            var=pd.DataFrame(index=genes)
        )
    else:
        # 从RDS文件读取（需要rpy2或提前导出）
        print("   错误: 未找到导出的单细胞数据文件")
        print("   请先运行R脚本导出数据:")
        print("   - sc_counts.mtx")
        print("   - sc_genes.txt")
        print("   - sc_cells.txt")
        print("   - sc_meta.csv")
        sys.exit(1)
    
    adata_ref.obs['cell_type'] = adata_ref.obs['cell_type'].astype('category')
    print(f"   ✓ 参考数据: {adata_ref.n_obs} cells, {adata_ref.n_vars} genes")
    print(f"   ✓ 细胞类型: {len(adata_ref.obs['cell_type'].cat.categories)} 种")
    
    # -------------------------------------------------------------------------
    # 步骤3: 读取空间转录组数据
    # -------------------------------------------------------------------------
    print("\n【步骤3/7】读取空间转录组数据 (16um)...")
    
    spatial_h5 = os.path.join(SPATIAL_DATA_DIR, "filtered_feature_bc_matrix.h5")
    if not os.path.exists(spatial_h5):
        print(f"   错误: 找不到空间数据文件: {spatial_h5}")
        sys.exit(1)
    
    adata_vis = sc.read_10x_h5(spatial_h5)
    print(f"   ✓ 空间数据: {adata_vis.n_obs} spots, {adata_vis.n_vars} genes")
    
    # 读取空间坐标
    coords_file = os.path.join(SPATIAL_DATA_DIR, "spatial/tissue_positions.parquet")
    if os.path.exists(coords_file):
        coords_df = pd.read_parquet(coords_file)
        coords_df = coords_df.set_index('barcode')
        common_barcodes = list(set(adata_vis.obs_names) & set(coords_df.index))
        coords_df = coords_df.loc[common_barcodes].reindex(adata_vis.obs_names)
        
        adata_vis.obs['array_row'] = coords_df['array_row'].values
        adata_vis.obs['array_col'] = coords_df['array_col'].values
        adata_vis.obsm['spatial'] = coords_df[['pxl_col_in_fullres', 'pxl_row_in_fullres']].values
        print(f"   ✓ 空间坐标: {len(coords_df)} spots")
    else:
        print("   ⚠ 警告: 未找到空间坐标文件")
    
    # -------------------------------------------------------------------------
    # 步骤4: 数据预处理
    # -------------------------------------------------------------------------
    print("\n【步骤4/7】数据预处理...")
    
    # 采样spots以减少计算量
    if adata_vis.n_obs > N_SPOTS_SAMPLE:
        print(f"   采样 {N_SPOTS_SAMPLE} 个spots...")
        sc.pp.subsample(adata_vis, n_obs=N_SPOTS_SAMPLE, random_state=42)
        print(f"   - 采样后: {adata_vis.n_obs} spots")
    
    # 找到共同基因
    intersect = np.intersect1d(adata_vis.var_names, adata_ref.var_names)
    print(f"   - 共同基因: {len(intersect)}")
    
    if len(intersect) < 100:
        print("   错误: 共同基因太少，请检查数据")
        sys.exit(1)
    
    adata_ref = adata_ref[:, intersect].copy()
    adata_vis = adata_vis[:, intersect].copy()
    
    # -------------------------------------------------------------------------
    # 步骤5: 训练参考签名模型
    # -------------------------------------------------------------------------
    print("\n【步骤5/7】训练参考签名模型...")
    print(f"   训练轮数: {REFERENCE_EPOCHS}")
    print("   预计时间: 5-15分钟...")
    
    # 筛选基因
    selected = filter_genes(
        adata_ref,
        cell_count_cutoff=5,
        cell_percentage_cutoff2=0.03,
        nonz_mean_cutoff=1.12
    )
    adata_ref = adata_ref[:, selected].copy()
    print(f"   - 选择基因: {adata_ref.n_vars}")
    
    # 准备参考数据
    RegressionModel.setup_anndata(adata_ref, labels_key='cell_type')
    
    # 训练参考模型
    mod = RegressionModel(adata_ref)
    mod.train(max_epochs=REFERENCE_EPOCHS, accelerator=device)
    
    # 导出参考签名
    adata_ref = mod.export_posterior(adata_ref, sample_kwargs={'num_samples': 1000})
    ref_sig = adata_ref.varm['means_per_cluster_mu_fg']
    
    print(f"   ✓ 签名矩阵: {ref_sig.shape[0]} genes x {ref_sig.shape[1]} cell types")
    
    # -------------------------------------------------------------------------
    # 步骤6: 运行空间反卷积
    # -------------------------------------------------------------------------
    print("\n【步骤6/7】运行空间反卷积...")
    print(f"   训练轮数: {SPATIAL_EPOCHS}")
    print("   预计时间: 20-40分钟，请耐心等待...")
    print(f"   开始时间: {datetime.now().strftime('%H:%M:%S')}")
    
    adata_vis = adata_vis[:, adata_ref.var_names].copy()
    Cell2location.setup_anndata(adata_vis)
    
    mod_spatial = Cell2location(
        adata_vis,
        cell_state_df=ref_sig,
        N_cells_per_location=N_CELLS_PER_LOCATION,
        detection_alpha=20,
    )
    
    mod_spatial.train(max_epochs=SPATIAL_EPOCHS, accelerator=device)
    adata_vis = mod_spatial.export_posterior(adata_vis, sample_kwargs={'num_samples': 1000})
    
    print(f"   结束时间: {datetime.now().strftime('%H:%M:%S')}")
    print("   ✓ 反卷积完成")
    
    # -------------------------------------------------------------------------
    # 步骤7: 提取和保存结果
    # -------------------------------------------------------------------------
    print("\n【步骤7/7】提取和保存结果...")
    
    # 提取细胞类型丰度
    abundances = adata_vis.obsm['q05_cell_abundance_w_sf']
    cell_types = adata_ref.obs['cell_type'].cat.categories
    
    # 转换为比例
    abundances_np = abundances.values if hasattr(abundances, 'values') else abundances
    proportions_np = abundances_np / abundances_np.sum(axis=1, keepdims=True)
    
    # 保存到AnnData
    adata_vis.obsm['cell_type_proportions'] = proportions_np
    adata_vis.obs['dominant_cell_type'] = cell_types[proportions_np.argmax(axis=1)]
    
    # 保存比例矩阵
    prop_df = pd.DataFrame(
        proportions_np,
        index=adata_vis.obs_names,
        columns=cell_types
    )
    prop_df.to_csv(f"{OUTPUT_DIR}/cell2location_cell_type_proportions_16um.csv")
    
    # 保存AnnData对象
    adata_vis.write_h5ad(f"{OUTPUT_DIR}/spatial_pancreas_cell2location_16um.h5ad")
    print("   ✓ 结果已保存")
    
    # 生成可视化
    print("\n生成可视化...")
    generate_visualizations(adata_vis, prop_df, OUTPUT_DIR)
    
    # 生成统计摘要
    generate_statistics(adata_vis, prop_df, OUTPUT_DIR)
    
    # 清理临时文件
    for temp_file in export_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"   清理: {temp_file}")
    
    print("\n" + "=" * 80)
    print("Cell2location 分析完成!")
    print("=" * 80)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n输出文件:")
    print(f"  📊 {OUTPUT_DIR}/cell2location_cell_type_proportions_16um.csv")
    print(f"  📦 {OUTPUT_DIR}/spatial_pancreas_cell2location_16um.h5ad")
    print(f"  🖼️  {OUTPUT_DIR}/cell2location_top4_cell_types_16um.png")
    print(f"  🖼️  {OUTPUT_DIR}/cell2location_dominant_cell_types_16um.png")
    print(f"  🖼️  {OUTPUT_DIR}/cell2location_all_cell_types_combined.png")
    print(f"  🖼️  {OUTPUT_DIR}/cell2location_mean_proportions_barplot.png")
    print(f"  🖼️  {OUTPUT_DIR}/cell2location_cell_type_proportions_boxplot.png")
    print(f"  🖼️  {OUTPUT_DIR}/cell2location_cell_type_correlation_heatmap.png")
    print(f"  📝 {OUTPUT_DIR}/cell2location_statistics_16um.txt")


def generate_visualizations(adata_vis, prop_df, output_dir):
    """生成可视化图表"""
    
    mean_props = prop_df.mean().sort_values(ascending=False)
    top4_cell_types = mean_props.head(4).index.tolist()
    cell_types = prop_df.columns.tolist()
    
    print(f"   前4种细胞类型: {top4_cell_types}")
    
    # 1. 前4种细胞类型热图
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    axes = axes.flatten()
    
    for idx, ct in enumerate(top4_cell_types):
        adata_vis.obs[f'{ct}_proportion'] = prop_df[ct].values
        sc.pl.spatial(
            adata_vis,
            color=f'{ct}_proportion',
            ax=axes[idx],
            show=False,
            title=f'{ct} (mean: {mean_props[ct]:.3f})',
            cmap='Reds',
            vmin=0,
            vmax=prop_df[ct].quantile(0.95),
            spot_size=50
        )
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cell2location_top4_cell_types_16um.png', dpi=150, bbox_inches='tight')
    plt.savefig(f'{output_dir}/cell2location_top4_cell_types_16um.pdf', bbox_inches='tight')
    plt.close()
    
    # 2. 所有细胞类型综合图
    n_cols = 5
    n_rows = (len(cell_types) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 4*n_rows))
    axes = axes.flatten()
    
    for idx, ct in enumerate(cell_types):
        if idx < len(axes):
            ax = axes[idx]
            scatter = ax.scatter(
                adata_vis.obsm['spatial'][:, 0],
                adata_vis.obsm['spatial'][:, 1],
                c=prop_df[ct],
                cmap='Reds',
                s=5,
                alpha=0.8,
                vmin=0,
                vmax=prop_df[ct].quantile(0.95)
            )
            ax.set_title(f'{ct}\n(mean: {mean_props[ct]:.3f})', fontsize=9, fontweight='bold')
            ax.set_aspect('equal')
            ax.axis('off')
            plt.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)
    
    for idx in range(len(cell_types), len(axes)):
        axes[idx].axis('off')
    
    plt.suptitle('Cell2location 16um: All Cell Types', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cell2location_all_cell_types_combined.png', dpi=150, bbox_inches='tight')
    plt.savefig(f'{output_dir}/cell2location_all_cell_types_combined.pdf', bbox_inches='tight')
    plt.close()
    
    # 3. 主要细胞类型分布图
    fig, ax = plt.subplots(figsize=(14, 12))
    dominant_types = prop_df.idxmax(axis=1)
    adata_vis.obs['dominant_cell_type'] = dominant_types.astype('category')
    
    sc.pl.spatial(
        adata_vis,
        color='dominant_cell_type',
        ax=ax,
        show=False,
        title='Dominant Cell Types (cell2location 16um)',
        spot_size=50
    )
    plt.savefig(f'{output_dir}/cell2location_dominant_cell_types_16um.png', dpi=150, bbox_inches='tight')
    plt.savefig(f'{output_dir}/cell2location_dominant_cell_types_16um.pdf', bbox_inches='tight')
    plt.close()
    
    # 4. 平均比例条形图
    fig, ax = plt.subplots(figsize=(12, 8))
    mean_props_sorted = mean_props.sort_values(ascending=True)
    colors_bar = plt.cm.Reds(np.linspace(0.3, 1, len(mean_props_sorted)))
    
    bars = ax.barh(range(len(mean_props_sorted)), mean_props_sorted.values, color=colors_bar)
    ax.set_yticks(range(len(mean_props_sorted)))
    ax.set_yticklabels(mean_props_sorted.index)
    ax.set_xlabel('Mean Proportion', fontsize=12)
    ax.set_title('Cell2location 16um: Mean Cell Type Proportions', fontsize=14, fontweight='bold')
    
    for i, (bar, val) in enumerate(zip(bars, mean_props_sorted.values)):
        ax.text(val + 0.005, i, f'{val:.3f} ({val*100:.1f}%)', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cell2location_mean_proportions_barplot.png', dpi=150, bbox_inches='tight')
    plt.savefig(f'{output_dir}/cell2location_mean_proportions_barplot.pdf', bbox_inches='tight')
    plt.close()
    
    # 5. 箱线图
    fig, ax = plt.subplots(figsize=(14, 8))
    prop_melted = prop_df.melt(var_name='Cell Type', value_name='Proportion')
    prop_melted = prop_melted[prop_melted['Proportion'] > 0]
    
    mean_order = prop_df.mean().sort_values(ascending=False).index.tolist()
    prop_melted['Cell Type'] = pd.Categorical(prop_melted['Cell Type'], categories=mean_order, ordered=True)
    prop_melted = prop_melted.sort_values('Cell Type')
    
    sns.boxplot(data=prop_melted, x='Cell Type', y='Proportion', ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_title('Cell2location 16um: Cell Type Proportions Distribution', fontsize=14, fontweight='bold')
    ax.set_ylabel('Proportion')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cell2location_cell_type_proportions_boxplot.png', dpi=150, bbox_inches='tight')
    plt.savefig(f'{output_dir}/cell2location_cell_type_proportions_boxplot.pdf', bbox_inches='tight')
    plt.close()
    
    # 6. 相关性热图
    fig, ax = plt.subplots(figsize=(12, 10))
    corr_matrix = prop_df.corr()
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, ax=ax, cbar_kws={'label': 'Correlation'})
    ax.set_title('Cell2location 16um: Cell Type Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cell2location_cell_type_correlation_heatmap.png', dpi=150, bbox_inches='tight')
    plt.savefig(f'{output_dir}/cell2location_cell_type_correlation_heatmap.pdf', bbox_inches='tight')
    plt.close()
    
    # 7. 单独细胞类型热图（14个）
    for ct in cell_types:
        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(
            adata_vis.obsm['spatial'][:, 0],
            adata_vis.obsm['spatial'][:, 1],
            c=prop_df[ct],
            cmap='Reds',
            s=8,
            alpha=0.8,
            vmin=0,
            vmax=prop_df[ct].quantile(0.95)
        )
        ax.set_title(f'{ct} (cell2location 16um)\nmean: {mean_props[ct]:.3f}', 
                    fontsize=12, fontweight='bold')
        ax.set_aspect('equal')
        ax.axis('off')
        plt.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04, label='Proportion')
        plt.tight_layout()
        
        safe_name = ct.replace(' ', '.').replace('/', '.')
        plt.savefig(f'{output_dir}/cell2location_heatmap_{safe_name}_no_bg.png', dpi=150, bbox_inches='tight')
        plt.savefig(f'{output_dir}/cell2location_heatmap_{safe_name}_no_bg.pdf', bbox_inches='tight')
        plt.close()
    
    print("   ✓ 可视化已保存")


def generate_statistics(adata_vis, prop_df, output_dir):
    """生成统计摘要"""
    
    mean_props = prop_df.mean().sort_values(ascending=False)
    dominant_counts = adata_vis.obs['dominant_cell_type'].value_counts()
    
    print("\n" + "=" * 80)
    print("统计摘要")
    print("=" * 80)
    
    print("\n各细胞类型平均比例:")
    for ct in mean_props.index:
        print(f"  - {ct}: {mean_props[ct]:.4f} ({mean_props[ct]*100:.2f}%)")
    
    print("\n各细胞类型作为主要类型的Spot数:")
    for ct in dominant_counts.index:
        pct = dominant_counts[ct] / len(adata_vis) * 100
        print(f"  - {ct}: {dominant_counts[ct]} spots ({pct:.1f}%)")
    
    # 保存统计结果
    with open(f'{output_dir}/cell2location_statistics_16um.txt', 'w') as f:
        f.write("=== Cell2location16um反卷积结果统计 ===\n\n")
        f.write(f"分析日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"样本: Visium HD 16um\n")
        f.write(f"Spots: {adata_vis.n_obs}\n")
        f.write(f"细胞类型: {len(prop_df.columns)}\n\n")
        
        f.write("各细胞类型平均比例:\n")
        for ct in mean_props.index:
            f.write(f"  - {ct}: {mean_props[ct]:.4f} ({mean_props[ct]*100:.2f}%)\n")
        
        f.write("\n各细胞类型作为主要类型的Spot数:\n")
        for ct in dominant_counts.index:
            pct = dominant_counts[ct] / len(adata_vis) * 100
            f.write(f"  - {ct}: {dominant_counts[ct]} spots ({pct:.1f}%)\n")
    
    print("\n   ✓ 统计结果已保存")


if __name__ == "__main__":
    main()
