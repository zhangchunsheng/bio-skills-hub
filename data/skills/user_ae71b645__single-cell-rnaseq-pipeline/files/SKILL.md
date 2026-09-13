---
name: single-cell-rnaseq-pipeline
description: 为 Seurat 和 Scanpy 生成单细胞 RNA-seq 分析代码模板，支持质量控制、聚类、可视化和下游分析。当用户需要
  scRNA-seq 分析流程、预处理工作流或批次校正代码时触发。
version: "1.0.2"
category: Bioinfo
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
displayName: "单细胞测序流程"
slug: single-cell-rnaseq-pipeline
---

# 单细胞测序流程

## 概述

为 **Seurat (R)** 和 **Scanpy (Python)** 生成全面的单细胞 RNA-seq 分析代码模板。本技能提供开箱即用的代码框架，涵盖预处理、质量控制、归一化、聚类、标志基因识别、可视化，以及批次校正和轨迹推断等高级分析。

**技术难度**：高

## 使用场景

- 从原始计数矩阵构建 scRNA-seq 分析流程
- 需要标准化的质控和预处理工作流
- 跨多个样本/数据集进行批次校正
- 执行降维和聚类分析
- 识别细胞类型特异性标志基因
- 创建适合发表的可视化图表（UMAP、小提琴图、热图）
- 进行轨迹推断（伪时序分析）
- 比较不同条件下的细胞亚群

## 核心功能

### Seurat (R) 模板
1. **数据加载**：10x Genomics、H5AD、Cell Ranger 输出
2. **质控指标**：线粒体含量、基因计数、双细胞检测
3. **归一化**：对数归一化、SCTransform
4. **整合**：Harmony、RPCA、CCA 批次校正
5. **聚类**：带优化的图聚类
6. **可视化**：UMAP、t-SNE、特征图、点图
7. **标志分析**：Wilcoxon 检验、保守标志基因
8. **差异表达**：FindAllMarkers、FindConservedMarkers
9. **细胞类型注释**：基于参考的 SingleR/Azimuth 注释

### Scanpy (Python) 模板
1. **数据加载**：AnnData、10x、CSV、loom 文件
2. **质控工作流**：全面的过滤和指标
3. **归一化**：Log1p、scran、ComBat 批次校正
4. **整合**：scVI、Scanorama、BBKNN
5. **聚类**：分辨率扫描的 Leiden/Louvain
6. **可视化**：UMAP、PAGA、嵌入表示
7. **标志分析**：rank_genes_groups、过滤标志基因
8. **轨迹**：PAGA、扩散伪时序（DPT）
9. **CellChat/CellPhoneDB**：细胞间通信

## 使用方法

### 生成 Seurat 模板

```bash
python scripts/main.py --tool seurat --output seurat_analysis.R --species human
```

### 生成 Scanpy 模板

```bash
python scripts/main.py --tool scanpy --output scanpy_analysis.py --species mouse
```

### 同时生成两种模板

```bash
python scripts/main.py --tool both --output scrna_pipeline --species human --batch-correction harmony --trajectory true
```

### 命令行参数

| 参数 | 类型 | 是否必需 | 描述 |
|-----------|------|----------|-------------|
| --tool | string | 是 | 分析工具：`seurat`、`scanpy` 或 `both` |
| --output | string | 是 | 输出文件或目录路径 |
| --species | string | 否 | 物种：`human` 或 `mouse`（默认：human） |
| --batch-correction | string | 否 | 方法：`harmony`、`rpca`、`cca`、`scanorama`、`scvi` |
| --trajectory | bool | 否 | 包含轨迹分析（默认：false） |
| --cell-communication | bool | 否 | 包含细胞间通信（默认：false） |
| --de-analysis | bool | 否 | 包含差异表达分析（默认：false） |
| --spatial | bool | 否 | 包含空间转录组学（默认：false） |

## 输出结构

```
output/
├── seurat/
│   ├── 01_load_and_qc.R
│   ├── 02_normalize_integrate.R
│   ├── 03_cluster_annotate.R
│   ├── 04_visualize.R
│   └── 05_de_analysis.R (if --de-analysis)
├── scanpy/
│   ├── 01_load_qc.py
│   ├── 02_normalize_integrate.py
│   ├── 03_cluster_annotate.py
│   ├── 04_visualize.py
│   └── 05_trajectory.py (if --trajectory)
└── README.md
```

## 技术细节

### 支持的输入格式
- 10x Genomics Cell Ranger 输出（barcodes.tsv、features.tsv、matrix.mtx）
- H5AD（AnnData h5 格式）
- Seurat RDS 对象
- CSV/TSV 计数矩阵
- HDF5 文件

### 质控参数（默认）
| 指标 | Human | Mouse |
|--------|-------|-------|
| min_genes | 200 | 200 |
| max_genes | 25000 | 25000 |
| min_cells | 3 | 3 |
| max_mt_percent | 20% | 20% |
| doublet_threshold | Auto | Auto |

### 聚类分辨率指南
- **0.4-0.6**：主要细胞类型
- **0.8-1.2**：细胞亚型
- **1.5-2.0**：精细亚群

### 批次校正建议
| 场景 | Seurat | Scanpy |
|----------|--------|--------|
| 小批次（<5） | Harmony | Harmony |
| 大批次 | RPCA | Scanorama |
| 复杂变异 | CCA | scVI |

## 代码示例

### Seurat 快速入门

```r
# Load data
seurat_obj <- CreateSeuratObject(counts = raw_data, project = "Sample")

# QC
seurat_obj[["percent.mt"]] <- PercentageFeatureSet(seurat_obj, pattern = "^MT-")
seurat_obj <- subset(seurat_obj, subset = nFeature_RNA > 200 & percent.mt < 20)

# Normalize
seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj, selection.method = "vst", nfeatures = 2000)

# Scale and PCA
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj, features = VariableFeatures(object = seurat_obj))

# Cluster
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30)
seurat_obj <- FindClusters(seurat_obj, resolution = 1.0)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30)

# Visualize
DimPlot(seurat_obj, reduction = "umap", label = TRUE)
FeaturePlot(seurat_obj, features = c("CD3E", "CD14", "CD79A"))
```

### Scanpy 快速入门

```python
import scanpy as sc

# Load data
adata = sc.read_10x_mtx("filtered_gene_bc_matrices/")

# QC
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, inplace=True)
adata = adata[adata.obs.pct_counts_mt < 20, :]

# Normalize
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# PCA and UMAP
sc.pp.scale(adata)
sc.tl.pca(adata, svd_solver='arpack')
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=1.0)

# Visualize
sc.pl.umap(adata, color=['leiden', 'total_counts'])
sc.pl.dotplot(adata, var_names=['CD3E', 'CD14', 'CD79A'], groupby='leiden')
```

## 参考资料

- `references/seurat_template.R` - 完整 Seurat 分析模板
- `references/scanpy_template.py` - 完整 Scanpy 分析模板
- `references/batch_correction_guide.md` - 批次校正方法比较
- `requirements.txt` - Python 依赖项

## 依赖项

### Seurat (R)
```r
install.packages(c("Seurat", "SeuratObject", "tidyverse", "patchwork"))
# Optional
remotes::install_github("satijalab/seurat-wrappers")
remotes::install_github("immunogenomics/harmony")
BiocManager::install("SingleR")
```

### Scanpy (Python)
```bash
pip install scanpy leidenalg scvi-tools cellchatpy
```

## 测试

运行基本验证：
```bash
cd scripts
python test_main.py
```

## 错误处理

所有错误均返回语义化信息：

```json
{
  "status": "error",
  "error": {
    "type": "invalid_parameter",
    "message": "Unsupported batch correction method: 'xyz'",
    "suggestion": "Use one of: harmony, rpca, cca, scanorama, scvi"
  }
}
```

## 安全与合规

- 无外部 API 调用
- 所有代码模板均自包含
- 无硬编码凭证或路径
- 模板使用相对路径引用数据
- 默认参数保守，保障安全

## 引用

如在发表物中使用生成的模板：
- Seurat: Satija Lab, Nature Biotechnology 2015
- Scanpy: Wolf et al., Genome Biology 2018
- scVI: Lopez et al., Nature Methods 2018
- Harmony: Korsunsky et al., Nature Methods 2019

## 风险评估

| 风险指标 | 评估 | 级别 |
|----------------|------------|-------|
| 代码执行 | Python/R 脚本在本地执行 | 中 |
| 网络访问 | 无外部 API 调用 | 低 |
| 文件系统访问 | 读取输入文件，写入输出文件 | 中 |
| 指令篡改 | 标准提示指南 | 低 |
| 数据暴露 | 输出文件保存至工作区 | 低 |

## 安全检查清单

- [ ] 无硬编码凭证或 API 密钥
- [ ] 无未授权的文件系统访问（../）
- [ ] 输出不暴露敏感信息
- [ ] 已实施提示注入防护
- [ ] 输入文件路径已验证（无 ../ 遍历）
- [ ] 输出目录限制在工作区内
- [ ] 脚本在沙箱环境中执行
- [ ] 错误信息已净化（不暴露堆栈跟踪）
- [ ] 依赖项已审计
## 前置条件

```bash
# Python dependencies
pip install -r requirements.txt
```

## 评估标准

### 成功指标
- [ ] 成功执行主要功能
- [ ] 输出符合质量标准
- [ ] 优雅处理边缘情况
- [ ] 性能可接受

### 测试用例
1. **基本功能**：标准输入 → 预期输出
2. **边缘情况**：无效输入 → 优雅错误处理
3. **性能**：大型数据集 → 可接受的处理时间

## 生命周期状态

- **当前阶段**：草稿
- **Next Review Date**: 2026-03-06
- **已知问题**：无
- **计划改进**：
  - 性能优化
  - 支持更多功能
