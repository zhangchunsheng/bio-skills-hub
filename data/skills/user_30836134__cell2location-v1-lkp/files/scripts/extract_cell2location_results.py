#!/usr/bin/env python3

# Author: LKP <kunpeng.liao@abiosciences.com>
# Date:   2026-08-18

# -*- coding: utf-8 -*-
"""
从cell2location模型中提取结果
"""

import os
import numpy as np
import pandas as pd
import scanpy as sc
import matplotlib.pyplot as plt

# ========== 配置区域（请根据实际数据修改） ==========
USER_DATA_DIR      = "your/data/directory"          # TODO: 修改为你的数据根目录
SPATIAL_SUBDIR     = "binned_outputs/square_016um"   # 空间数据子目录
OUTPUT_DIR         = "cell2location_16um_results"    # 输入/输出目录（与训练一致）
# =====================================================
import cell2location
from cell2location.models import Cell2location
import torch

# 设置工作目录
work_dir = "os.path.join(USER_DATA_DIR, OUTPUT_DIR)"
os.chdir(work_dir)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("Cell2location 提取结果")
print("=" * 70)

# 检查是否有保存的模型
print("\n检查保存的模型...")

# 读取空间数据
print("\n读取空间数据...")
spatial_dir = "os.path.join(USER_DATA_DIR, SPATIAL_SUBDIR)"
adata_vis = sc.read_10x_h5(os.path.join(spatial_dir, "filtered_feature_bc_matrix.h5"))

# 采样
if adata_vis.n_obs > 10000:
    sc.pp.subsample(adata_vis, n_obs=10000, random_state=42)

# 读取坐标
coords_file = os.path.join(spatial_dir, "spatial/tissue_positions.parquet")
if os.path.exists(coords_file):
    coords_df = pd.read_parquet(coords_file)
    coords_df = coords_df.set_index('barcode')
    coords_df = coords_df.reindex(adata_vis.obs_names)
    adata_vis.obs['array_row'] = coords_df['array_row'].values
    adata_vis.obs['array_col'] = coords_df['array_col'].values
    adata_vis.obsm['spatial'] = coords_df[['pxl_col_in_fullres', 'pxl_row_in_fullres']].values

print(f"   ✓ 空间数据: {adata_vis.n_obs} spots")

# 读取参考签名
print("\n读取参考签名...")
from scipy.io import mmread

counts_matrix = mmread("sc_counts.mtx").T.tocsr()
genes = pd.read_csv("sc_genes.txt", header=None)[0].tolist()
cells = pd.read_csv("sc_cells.txt", header=None)[0].tolist()
meta_df = pd.read_csv("sc_meta.csv")

adata_ref = sc.AnnData(
    X=counts_matrix,
    obs=pd.DataFrame({'cell_type': meta_df['cell_type'].values}, index=cells),
    var=pd.DataFrame(index=genes)
)
adata_ref.obs['cell_type'] = adata_ref.obs['cell_type'].astype('category')

# 找到共同基因
intersect = np.intersect1d(adata_vis.var_names, adata_ref.var_names)
adata_ref = adata_ref[:, intersect].copy()
adata_vis = adata_vis[:, intersect].copy()

# 选择基因
from cell2location.utils.filtering import filter_genes
selected = filter_genes(adata_ref, cell_count_cutoff=5, cell_percentage_cutoff2=0.03, nonz_mean_cutoff=1.12)
adata_ref = adata_ref[:, selected].copy()

# 训练参考模型获取签名
from cell2location.models import RegressionModel
RegressionModel.setup_anndata(adata_ref, labels_key='cell_type')
mod = RegressionModel(adata_ref)
mod.train(max_epochs=250, accelerator='cuda' if torch.cuda.is_available() else 'cpu')
adata_ref = mod.export_posterior(adata_ref, sample_kwargs={'num_samples': 1000})
ref_sig = adata_ref.varm['means_per_cluster_mu_fg']

print(f"   ✓ 参考签名: {ref_sig.shape}")

# 准备空间数据
adata_vis = adata_vis[:, adata_ref.var_names].copy()
Cell2location.setup_anndata(adata_vis)

# 创建模型并加载训练好的参数
print("\n加载训练好的模型...")
mod_spatial = Cell2location(
    adata_vis,
    cell_state_df=ref_sig,
    N_cells_per_location=8,
    detection_alpha=20,
)

# 由于我们已经训练过模型，直接从AnnData中提取结果
# 检查是否有保存的结果
if 'q05_cell_abundance_w_sf' in adata_vis.obsm:
    print("   ✓ 找到已保存的结果")
    abundances = adata_vis.obsm['q05_cell_abundance_w_sf']
else:
    print("   需要重新运行反卷积...")
    print("   这将需要约20-30分钟")
    mod_spatial.train(max_epochs=1000, accelerator='cuda' if torch.cuda.is_available() else 'cpu')
    adata_vis = mod_spatial.export_posterior(adata_vis, sample_kwargs={'num_samples': 1000})
    abundances = adata_vis.obsm['q05_cell_abundance_w_sf']

# 提取细胞类型
cell_types = adata_ref.obs['cell_type'].cat.categories

print(f"   ✓ 细胞类型: {len(cell_types)}")
print(f"   ✓ Spots: {abundances.shape[0]}")

# 计算比例
print("\n计算细胞类型比例...")
abundances_np = abundances.values if hasattr(abundances, 'values') else abundances
proportions_np = abundances_np / abundances_np.sum(axis=1, keepdims=True)

# 保存到AnnData
adata_vis.obsm['cell_type_proportions'] = proportions_np
adata_vis.obs['dominant_cell_type'] = cell_types[proportions_np.argmax(axis=1)]

# 保存结果
prop_df = pd.DataFrame(
    proportions_np,
    index=adata_vis.obs_names,
    columns=cell_types
)
prop_df.to_csv("cell2location_16um_results/cell2location_cell_type_proportions_16um.csv")
adata_vis.write_h5ad("cell2location_16um_results/spatial_pancreas_cell2location_16um.h5ad")
print("   ✓ 结果已保存")

# 生成可视化
print("\n生成可视化...")

mean_props = prop_df.mean().sort_values(ascending=False)
top4_cell_types = mean_props.head(4).index.tolist()
print(f"   前4种细胞类型: {top4_cell_types}")

# 前4种细胞类型热图
fig, axes = plt.subplots(2, 2, figsize=(16, 14))
axes = axes.flatten()

for idx, ct in enumerate(top4_cell_types):
    adata_vis.obs[f'{ct}_proportion'] = prop_df[ct].values
    sc.pl.spatial(
        adata_vis,
        color=f'{ct}_proportion',
        ax=axes[idx],
        show=False,
        title=f'{ct} (cell2location)',
        cmap='Reds',
        vmin=0,
        vmax=prop_df[ct].max()
    )

plt.tight_layout()
plt.savefig('cell2location_16um_results/cell2location_top4_cell_types_16um.png', dpi=150, bbox_inches='tight')
plt.close()

# 综合图
fig, ax = plt.subplots(figsize=(14, 12))
adata_vis.obs['dominant_cell_type'] = adata_vis.obs['dominant_cell_type'].astype('category')
sc.pl.spatial(
    adata_vis,
    color='dominant_cell_type',
    ax=ax,
    show=False,
    title='Dominant Cell Types (cell2location 16um)',
    size=1.5
)
plt.savefig('cell2location_16um_results/cell2location_dominant_cell_types_16um.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ 可视化已保存")

# 统计摘要
print("\n" + "=" * 70)
print("统计摘要")
print("=" * 70)

print("\n各细胞类型平均比例:")
for ct in mean_props.index:
    print(f"  - {ct}: {mean_props[ct]:.3f}")

print("\n各细胞类型作为主要类型的Spot数:")
dominant_counts = adata_vis.obs['dominant_cell_type'].value_counts()
for ct in dominant_counts.index:
    pct = dominant_counts[ct] / len(adata_vis) * 100
    print(f"  - {ct}: {dominant_counts[ct]} spots ({pct:.1f}%)")

# 保存统计结果
with open('cell2location_16um_results/cell2location_statistics_16um.txt', 'w') as f:
    f.write("=== Cell2location16um反卷积结果统计 ===\n\n")
    f.write(f"分析日期: {pd.Timestamp.now()}\n")
    f.write(f"样本: Visium HD 16um\n")
    f.write(f"Spots: {adata_vis.n_obs}\n")
    f.write(f"细胞类型: {len(cell_types)}\n\n")
    
    f.write("各细胞类型平均比例:\n")
    for ct in mean_props.index:
        f.write(f"  - {ct}: {mean_props[ct]:.3f}\n")
    
    f.write("\n各细胞类型作为主要类型的Spot数:\n")
    for ct in dominant_counts.index:
        pct = dominant_counts[ct] / len(adata_vis) * 100
        f.write(f"  - {ct}: {dominant_counts[ct]} spots ({pct:.1f}%)\n")

print("\n   ✓ 统计结果已保存")

# 清理临时文件
for temp_file in ['sc_counts.mtx', 'sc_genes.txt', 'sc_cells.txt', 'sc_meta.csv']:
    if os.path.exists(temp_file):
        os.remove(temp_file)

print("\n" + "=" * 70)
print("Cell2location 分析完成!")
print("=" * 70)
print("\n输出文件:")
print("  📊 cell2location_16um_results/cell2location_cell_type_proportions_16um.csv")
print("  📦 cell2location_16um_results/spatial_pancreas_cell2location_16um.h5ad")
print("  🖼️  cell2location_16um_results/cell2location_top4_cell_types_16um.png")
print("  🖼️  cell2location_16um_results/cell2location_dominant_cell_types_16um.png")
print("  📝 cell2location_16um_results/cell2location_statistics_16um.txt")
