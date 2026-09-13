#!/usr/bin/env python3

# Author: LKP <kunpeng.liao@abiosciences.com>
# Date:   2026-08-18

# -*- coding: utf-8 -*-
"""
Cell2location 生成全套可视化图表（类似RCTD风格）

依赖：需先运行 cell2location 反卷积并保存结果 h5ad
"""

import os
import numpy as np
import pandas as pd
import scanpy as sc
import matplotlib.pyplot as plt

# ========== 配置区域（请根据实际数据修改） ==========
USER_DATA_DIR      = "your/data/directory"          # TODO: 修改为你的数据根目录
SPATIAL_SUBDIR     = "binned_outputs/square_016um"   # 空间数据子目录
OUTPUT_DIR         = "cell2location_16um_results"    # 反卷积结果目录
N_TOP_TYPES_PLOT   = 4                               # 可视化前 N 种细胞类型
# =====================================================
import seaborn as sns
from matplotlib.patches import Patch

work_dir = "os.path.join(USER_DATA_DIR, OUTPUT_DIR)"
os.chdir(work_dir)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("Cell2location 生成全套可视化图表")
print("=" * 70)

# 读取已保存的结果
print("\n读取已保存的结果...")
adata_vis = sc.read_h5ad("cell2location_16um_results/spatial_pancreas_cell2location_16um.h5ad")
prop_df = pd.read_csv("cell2location_16um_results/cell2location_cell_type_proportions_16um.csv", index_col=0)

# 添加比例列到AnnData
for ct in prop_df.columns:
    adata_vis.obs[f'{ct}_proportion'] = prop_df[ct].values

print(f"   ✓ 读取成功: {adata_vis.n_obs} spots, {len(prop_df.columns)} 细胞类型")

# 设置样式
plt.style.use('default')
sns.set_palette("husl")

# 1. 所有细胞类型的热图（类似rctd_all_cell_types_combined）
print("\n【1/8】生成所有细胞类型综合热图...")
fig, axes = plt.subplots(3, 5, figsize=(20, 12))
axes = axes.flatten()

cell_types = prop_df.columns.tolist()
for idx, ct in enumerate(cell_types):
    if idx < len(axes):
        ax = axes[idx]
        scatter = ax.scatter(
            adata_vis.obsm['spatial'][:, 0],
            adata_vis.obsm['spatial'][:, 1],
            c=prop_df[ct],
            cmap='Reds',
            s=3,
            alpha=0.8
        )
        ax.set_title(f'{ct}', fontsize=10, fontweight='bold')
        ax.set_aspect('equal')
        ax.axis('off')
        plt.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)

# 隐藏多余的子图
for idx in range(len(cell_types), len(axes)):
    axes[idx].axis('off')

plt.suptitle('Cell2location: All Cell Types Spatial Distribution (16um)', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('cell2location_16um_results/cell2location_all_cell_types_combined.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ 所有细胞类型综合热图已保存")

# 2. 前4种细胞类型对比图
print("\n【2/8】生成前4种细胞类型对比图...")
mean_props = prop_df.mean().sort_values(ascending=False)
top4_cell_types = mean_props.head(4).index.tolist()

fig, axes = plt.subplots(2, 2, figsize=(16, 14))
axes = axes.flatten()

for idx, ct in enumerate(top4_cell_types):
    ax = axes[idx]
    scatter = ax.scatter(
        adata_vis.obsm['spatial'][:, 0],
        adata_vis.obsm['spatial'][:, 1],
        c=prop_df[ct],
        cmap='Reds',
        s=5,
        alpha=0.8
    )
    ax.set_title(f'{ct} (mean: {mean_props[ct]:.3f})', fontsize=12, fontweight='bold')
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    ax.set_aspect('equal')
    ax.invert_yaxis()
    plt.colorbar(scatter, ax=ax, label='Proportion')

plt.suptitle('Cell2location: Top 4 Cell Types (16um)', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('cell2location_16um_results/cell2location_top4_cell_types_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ 前4种细胞类型对比图已保存")

# 3. 主要细胞类型分布图
print("\n【3/8】生成主要细胞类型分布图...")
dominant_types = prop_df.idxmax(axis=1)
unique_types = dominant_types.unique()
colors = plt.cm.tab20(np.linspace(0, 1, len(unique_types)))
color_map = dict(zip(unique_types, colors))

fig, ax = plt.subplots(figsize=(14, 12))
for cell_type in unique_types:
    mask = dominant_types == cell_type
    ax.scatter(
        adata_vis.obsm['spatial'][mask, 0],
        adata_vis.obsm['spatial'][mask, 1],
        c=[color_map[cell_type]],
        s=5,
        alpha=0.8,
        label=cell_type
    )

ax.set_title('Cell2location: Dominant Cell Types (16um)', fontsize=16, fontweight='bold')
ax.set_xlabel('X coordinate')
ax.set_ylabel('Y coordinate')
ax.set_aspect('equal')
ax.invert_yaxis()
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
plt.tight_layout()
plt.savefig('cell2location_16um_results/cell2location_dominant_cell_types_spatial.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ 主要细胞类型分布图已保存")

# 4. 细胞类型比例箱线图
print("\n【4/8】生成细胞类型比例箱线图...")
fig, ax = plt.subplots(figsize=(14, 8))

# 准备数据
prop_melted = prop_df.melt(var_name='Cell Type', value_name='Proportion')
prop_melted = prop_melted[prop_melted['Proportion'] > 0]  # 只显示非零值

# 按平均值排序
mean_order = prop_df.mean().sort_values(ascending=False).index.tolist()
prop_melted['Cell Type'] = pd.Categorical(prop_melted['Cell Type'], categories=mean_order, ordered=True)
prop_melted = prop_melted.sort_values('Cell Type')

sns.boxplot(data=prop_melted, x='Cell Type', y='Proportion', ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
ax.set_title('Cell2location: Cell Type Proportions Distribution (16um)', fontsize=14, fontweight='bold')
ax.set_ylabel('Proportion')
plt.tight_layout()
plt.savefig('cell2location_16um_results/cell2location_cell_type_proportions_boxplot.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ 细胞类型比例箱线图已保存")

# 5. 所有细胞类型的单独热图（类似rctd_heatmap_xxx_no_bg）
print("\n【5/8】生成各细胞类型单独热图...")

for ct in cell_types:
    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(
        adata_vis.obsm['spatial'][:, 0],
        adata_vis.obsm['spatial'][:, 1],
        c=prop_df[ct],
        cmap='Reds',
        s=8,
        alpha=0.8
    )
    ax.set_title(f'{ct} (cell2location 16um)', fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    ax.axis('off')
    plt.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04, label='Proportion')
    plt.tight_layout()
    plt.savefig(f'cell2location_16um_results/cell2location_heatmap_{ct.replace(" ", ".")}_no_bg.png', dpi=150, bbox_inches='tight')
    plt.close()

print(f"   ✓ {len(cell_types)}个细胞类型单独热图已保存")

# 6. 气泡图（类似rctd_all_cell_types_bubble）
print("\n【6/8】生成细胞类型气泡图...")
fig, ax = plt.subplots(figsize=(14, 10))

# 计算每个spot的主要细胞类型和比例
max_props = prop_df.max(axis=1)
max_types = prop_df.idxmax(axis=1)

# 创建气泡图
for idx, ct in enumerate(unique_types):
    mask = max_types == ct
    if mask.sum() > 0:
        ax.scatter(
            adata_vis.obsm['spatial'][mask, 0],
            adata_vis.obsm['spatial'][mask, 1],
            c=[color_map[ct]],
            s=max_props[mask] * 100,  # 气泡大小与比例成正比
            alpha=0.6,
            label=ct,
            edgecolors='black',
            linewidth=0.5
        )

ax.set_title('Cell2location: Cell Type Bubble Plot (16um)\nBubble size = proportion', fontsize=14, fontweight='bold')
ax.set_xlabel('X coordinate')
ax.set_ylabel('Y coordinate')
ax.set_aspect('equal')
ax.invert_yaxis()
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
plt.tight_layout()
plt.savefig('cell2location_16um_results/cell2location_all_cell_types_bubble.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ 细胞类型气泡图已保存")

# 7. 细胞类型平均比例条形图
print("\n【7/8】生成细胞类型平均比例条形图...")
fig, ax = plt.subplots(figsize=(12, 8))

mean_props_sorted = mean_props.sort_values(ascending=True)
colors_bar = plt.cm.Reds(np.linspace(0.3, 1, len(mean_props_sorted)))

bars = ax.barh(range(len(mean_props_sorted)), mean_props_sorted.values, color=colors_bar)
ax.set_yticks(range(len(mean_props_sorted)))
ax.set_yticklabels(mean_props_sorted.index)
ax.set_xlabel('Mean Proportion', fontsize=12)
ax.set_title('Cell2location: Mean Cell Type Proportions (16um)', fontsize=14, fontweight='bold')

# 添加数值标签
for i, (bar, val) in enumerate(zip(bars, mean_props_sorted.values)):
    ax.text(val + 0.005, i, f'{val:.3f}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('cell2location_16um_results/cell2location_mean_proportions_barplot.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ 细胞类型平均比例条形图已保存")

# 8. 细胞类型相关性热图
print("\n【8/8】生成细胞类型相关性热图...")
fig, ax = plt.subplots(figsize=(12, 10))

# 计算相关性矩阵
corr_matrix = prop_df.corr()

# 绘制热图
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, ax=ax, cbar_kws={'label': 'Correlation'})
ax.set_title('Cell2location: Cell Type Correlation Matrix (16um)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('cell2location_16um_results/cell2location_cell_type_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ 细胞类型相关性热图已保存")

# 统计摘要
print("\n" + "=" * 70)
print("统计摘要")
print("=" * 70)

print("\n各细胞类型平均比例（前10）:")
for ct in mean_props.head(10).index:
    print(f"  - {ct}: {mean_props[ct]:.3f}")

print("\n各细胞类型作为主要类型的Spot数（前10）:")
dominant_counts = dominant_types.value_counts()
for ct in dominant_counts.head(10).index:
    pct = dominant_counts[ct] / len(adata_vis) * 100
    print(f"  - {ct}: {dominant_counts[ct]} spots ({pct:.1f}%)")

print("\n" + "=" * 70)
print("Cell2location 全套可视化图表生成完成!")
print("=" * 70)
print("\n生成的图表:")
print("  🖼️  cell2location_all_cell_types_combined.png - 所有细胞类型综合热图")
print("  🖼️  cell2location_top4_cell_types_comparison.png - 前4种细胞类型对比")
print("  🖼️  cell2location_dominant_cell_types_spatial.png - 主要细胞类型空间分布")
print("  🖼️  cell2location_cell_type_proportions_boxplot.png - 细胞类型比例箱线图")
print("  🖼️  cell2location_heatmap_*.png - 各细胞类型单独热图(14个)")
print("  🖼️  cell2location_all_cell_types_bubble.png - 细胞类型气泡图")
print("  🖼️  cell2location_mean_proportions_barplot.png - 平均比例条形图")
print("  🖼️  cell2location_cell_type_correlation_heatmap.png - 细胞类型相关性热图")
