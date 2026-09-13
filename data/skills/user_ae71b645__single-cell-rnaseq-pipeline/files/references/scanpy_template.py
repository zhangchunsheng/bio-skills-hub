# Scanpy 模板参考

## 完整 Scanpy 工作流程示例

```python
# ============================================
# Complete Scanpy scRNA-seq Analysis Pipeline
# ============================================

import scanpy as sc
import pandas as pd
import numpy as np

# 1. Settings
sc.settings.verbosity = 3
sc.settings.set_figure_params(dpi=80)

# 2. Load Data (10x Genomics)
adata = sc.read_10x_mtx(
    "filtered_gene_bc_matrices/",
    var_names='gene_symbols',
    cache=True
)

# 3. QC
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
adata = adata[adata.obs.pct_counts_mt < 20, :]

# 4. Filter
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# 5. Normalize
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# 6. Scale and PCA
sc.pp.scale(adata)
sc.tl.pca(adata, svd_solver='arpack')

# 7. Neighborhood and Clustering
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.8)

# 8. Visualize
sc.pl.umap(adata, color=['leiden'])

# 9. Markers
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=25)
```

## 关键函数

| 函数 | 用途 |
|----------|---------|
| `sc.read_10x_mtx()` | 加载 10x Genomics 数据 |
| `sc.read_h5ad()` | 加载 H5AD 文件 |
| `sc.pp.filter_cells()` | 按基因计数过滤细胞 |
| `sc.pp.filter_genes()` | 按细胞计数过滤基因 |
| `sc.pp.calculate_qc_metrics()` | 计算质控统计量 |
| `sc.pp.normalize_total()` | 归一化至目标总和 |
| `sc.pp.log1p()` | 对数转换 |
| `sc.pp.highly_variable_genes()` | 寻找高变异基因（HVG） |
| `sc.pp.scale()` | Z 分数归一化 |
| `sc.tl.pca()` | 主成分分析（PCA） |
| `sc.pp.neighbors()` | 构建邻域图 |
| `sc.tl.umap()` | UMAP |
| `sc.tl.leiden()` | Leiden 聚类 |
| `sc.tl.rank_genes_groups()` | 寻找标志基因 |

## 常用参数

### 邻居数设置
```python
n_neighbors=10  # Dense data
n_neighbors=15  # Standard
n_neighbors=30  # Sparse data
```

### Leiden 分辨率
```python
resolution=0.4  # Coarse clusters
resolution=0.8  # Standard
resolution=1.5  # Fine clusters
```

### 高变异基因
```python
n_top_genes=1000  # Simple datasets
n_top_genes=2000  # Standard
n_top_genes=5000  # Complex datasets
```

## 可视化函数

```python
# UMAP
c.pl.umap(adata, color=['leiden', 'gene_name'])

# Violin plot
sc.pl.violin(adata, ['gene1', 'gene2'])

# Dot plot
sc.pl.dotplot(adata, var_names=['gene1', 'gene2'], groupby='leiden')

# Heatmap
sc.pl.heatmap(adata, var_names=['gene1', 'gene2'], groupby='leiden')

# Feature plot (on embedding)
sc.pl.embedding(adata, basis='umap', color='gene_name')
```
