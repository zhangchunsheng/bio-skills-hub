---
name: scanpy
description: 标准单细胞 RNA-seq 分析流程。适用于质控、归一化、降维（PCA/UMAP/t-SNE）、聚类、差异表达、可视化，以及将 R 友好的单细胞格式（如 Seurat 或 SingleCellExperiment RDS 文件）转换为 h5ad 供 Scanpy 使用。最适合使用成熟工作流进行探索性 scRNA-seq 分析。深度学习模型请使用 scvi-tools；数据格式问题请使用 anndata。
license: BSD-3-Clause
metadata: {"version": "1.3", "skill-author": "K-Dense Inc."}
---

# Scanpy：单细胞分析

## 概述

Scanpy 是一个可扩展的 Python 工具包，用于分析单细胞 RNA-seq 数据，基于 AnnData 构建。应用此技能可完成完整的单细胞工作流，包括质控、归一化、降维、聚类、标志基因识别、可视化和轨迹分析。当前稳定版本：**scanpy 1.12.x**（2026 年 1 月）。

## 安装

需要 Python **3.12+**（scanpy 1.12 不再支持 Python ≤3.11）和 anndata **≥0.10**。

```bash
uv pip install "scanpy[leiden]"
```

`[leiden]` 扩展安装 `python-igraph` 和 `leidenalg`，这是 Leiden 聚类所需的。对于可复现的环境，固定版本：`uv pip install "scanpy[leiden]==1.12.1"`。

对于大型或超核数据集，许多函数支持 [Dask](https://docs.dask.org/) 数组（实验性）：

```bash
uv pip install "scanpy[leiden]" dask
```

请参阅 [Using dask with Scanpy](https://scanpy.scverse.org/en/stable/tutorials/experimental/dask.html) 教程。对于 GPU 加速的类 scanpy 操作，请使用独立的 [rapids-singlecell](https://rapids-singlecell.readthedocs.io/) 包。

如果输入是 R 原生单细胞对象（`.rds`、`.RData`、Seurat 或 SingleCellExperiment），请先使用 R 工具将其转换为 `.h5ad`，然后用 Scanpy 加载。阅读 `references/r_interop.md` 了解 macOS、Linux 和 Windows 上由 agent 运行的安装和转换说明。

有关 AnnData 结构和 I/O 的详细信息，请使用 **anndata** 技能。有关概率模型和批次校正，请使用 **scvi-tools**。

## 何时使用此技能

在以下情况下应使用此技能：
- 分析单细胞 RNA-seq 数据（.h5ad、10X、CSV 格式）
- 处理需要转换为 `.h5ad` 的 R 友好单细胞数据集（`.rds`、`.RData`、Seurat、SingleCellExperiment）
- 对 scRNA-seq 数据集进行质控
- 创建 UMAP、t-SNE 或 PCA 可视化
- 识别细胞聚类和寻找标志基因
- 基于基因表达注释细胞类型
- 进行轨迹推断或伪时间分析
- 生成出版质量的单细胞图表

## 脚本工具包（优先使用而非从头编写代码）

此技能在 `scripts/` 中为每个常见步骤提供了即用型 CLI 脚本。**请运行这些脚本而不是手动编写 scanpy 代码**——它们能根据扩展名处理文件加载、图形设置、合理的默认值、原始计数保留和进度日志记录。每个脚本读写 `.h5ad` 文件，因此可以串联使用，且每个脚本都有 `--help`。仅在脚本未覆盖的任务或需要不寻常的自定义时才编写 scanpy 代码。

所有脚本都使用共享的 `scripts/_common.py` 辅助模块（加载、保存、图形配置）——请将其与其他脚本放在一起。从技能目录运行或传递完整路径；图表默认保存到 `./figures/`。

| 脚本 | 用途 | 典型调用 |
|--------|---------|--------------|
| `run_pipeline.py` | **一条命令完成完整工作流**：加载 → QC → 归一化 → HVG → PCA →（批次校正）→ UMAP → Leiden → 标志基因 | `python scripts/run_pipeline.py raw.h5ad -o processed.h5ad` |
| `inspect_data.py` | 汇总未知数据集（形状、obs/var、层、已计算内容、原始 vs 归一化） | `python scripts/inspect_data.py data.h5ad` |
| `convert.py` | 加载任意格式（10x 目录/.h5、csv、loom、mtx）并写入 `.h5ad` | `python scripts/convert.py 10x_dir/ -o data.h5ad` |
| `qc_analysis.py` | QC 指标、前后对比图、过滤、可选 Scrublet 双峰检测 | `python scripts/qc_analysis.py raw.h5ad -o qc.h5ad --scrublet` |
| `preprocess.py` | 归一化、log1p、HVG、可选缩放/回归（保留 `counts` 层 + `raw`） | `python scripts/preprocess.py qc.h5ad -o norm.h5ad` |
| `reduce_dimensions.py` | PCA + 方差图、邻域、UMAP、可选 t-SNE | `python scripts/reduce_dimensions.py norm.h5ad -o red.h5ad` |
| `batch_correct.py` | 整合：harmony / bbknn / combat | `python scripts/batch_correct.py red.h5ad -o int.h5ad --method harmony --batch-key sample` |
| `cluster.py` | Leiden（或 louvain）在一种或多种分辨率下 | `python scripts/cluster.py red.h5ad -o clu.h5ad --resolution 0.3 0.6 1.0` |
| `find_markers.py` | `rank_genes_groups` + 每组 CSV + 标志基因图表 | `python scripts/find_markers.py clu.h5ad --groupby leiden -o clu.h5ad` |
| `annotate.py` | 从 JSON/CSV 映射聚类 → 细胞类型；可选标志基因参考点图 | `python scripts/annotate.py clu.h5ad -o ann.h5ad --mapping map.json` |
| `score_genes.py` | 对基因签名（JSON）和/或细胞周期阶段进行评分 | `python scripts/score_genes.py ann.h5ad -o scored.h5ad --gene-sets sigs.json` |
| `pseudobulk.py` | 按样本 × 细胞类型汇总计数 → 用于 pydeseq2 的矩阵 | `python scripts/pseudobulk.py ann.h5ad --by sample cell_type --out-prefix pb` |
| `subset.py` | 按 obs 值或基因列表子集化（可选清除旧嵌入） | `python scripts/subset.py ann.h5ad -o tcells.h5ad --obs cell_type --keep "T cells"` |
| `plot.py` | 从已处理对象生成 umap/tsne/pca/violin/dotplot/heatmap 等 | `python scripts/plot.py ann.h5ad --kind dotplot --genes CD3D CD14 --groupby cell_type` |

### 一键端到端运行

```bash
# 计数 → 聚类、标志基因注释的对象 + 图表 + 标志基因 CSV
python scripts/run_pipeline.py raw.h5ad -o processed.h5ad \
    --resolution 0.5 --n-top-genes 2000 --scrublet
# 多样本整合：
python scripts/run_pipeline.py raw.h5ad -o processed.h5ad --batch-key sample --batch-method harmony
# 通过 JSON 设置可复现参数（键名使用下划线镜像标志名）：
python scripts/run_pipeline.py raw.h5ad -o processed.h5ad --config params.json
```

### 逐步串联（需要在阶段之间检查/迭代时使用）

```bash
python scripts/qc_analysis.py        raw.h5ad  -o qc.h5ad   --scrublet
python scripts/preprocess.py         qc.h5ad   -o norm.h5ad --n-top-genes 2000
python scripts/reduce_dimensions.py  norm.h5ad -o red.h5ad  --n-pcs 40
python scripts/cluster.py            red.h5ad  -o clu.h5ad  --resolution 0.3 0.5 0.8
python scripts/find_markers.py       clu.h5ad  -o clu.h5ad  --groupby leiden --use-raw
# 检查 results/markers/*.csv，决定标签，编写映射 JSON，然后：
python scripts/annotate.py           clu.h5ad  -o ann.h5ad  --mapping celltypes.json
```

以下部分记录了每个脚本底层执行的 scanpy 调用——在需要超出脚本标志的自定义时阅读它们。

## 快速入门

### 基本导入与设置

```python
import scanpy as sc
import pandas as pd
import numpy as np

# 配置设置
sc.settings.verbosity = 3
sc.settings.set_figure_params(dpi=80, facecolor='white')
sc.settings.figdir = './figures/'
sc.settings.autosave = True  # 优先于每个图的 save=（在 scanpy 1.12 中已弃用）
```

### 加载数据

```python
# 从 10X Genomics
adata = sc.read_10x_mtx('path/to/data/')
adata = sc.read_10x_h5('path/to/data.h5')

# 从 h5ad（AnnData 格式）
adata = sc.read_h5ad('path/to/data.h5ad')

# 从 CSV
adata = sc.read_csv('path/to/data.csv')
```

对于 R 原生文件，不要尝试直接在 Python 中解析 Seurat `.rds`。请先进行转换：

```bash
# 参见 references/r_interop.md 了解安装 R 和转换包的信息。
Rscript convert_rds_to_h5ad.R input.rds output.h5ad
```

```python
adata = sc.read_h5ad('output.h5ad')
```

### 理解 AnnData 结构

AnnData 对象是 scanpy 的核心数据结构：

```python
adata.X          # 表达矩阵（细胞 × 基因）
adata.obs        # 细胞元数据（DataFrame）
adata.var        # 基因元数据（DataFrame）
adata.uns        # 非结构化注释（字典）
adata.obsm       # 多维细胞数据（PCA、UMAP）
adata.raw        # 原始数据备份

# 访问细胞和基因名称
adata.obs_names  # 细胞条形码
adata.var_names  # 基因名称
```

## 标准分析工作流

### 1. 质控

识别并过滤低质量细胞和基因：

```python
# 识别线粒体基因
adata.var['mt'] = adata.var_names.str.startswith('MT-')

# 计算 QC 指标
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)

# 可视化 QC 指标
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
             jitter=0.4, multi_panel=True)

# 过滤细胞和基因
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata = adata[adata.obs.pct_counts_mt < 5, :]  # 去除高 MT% 细胞
```

**双峰检测（可选，在归一化前对原始计数进行）：**

```python
sc.pp.scrublet(adata)  # 自 scanpy 1.10 以来的核心 API（原为 scanpy.external.pp）
adata = adata[~adata.obs['predicted_doublet'], :].copy()
```

**使用 QC 脚本进行自动化分析**（从技能目录运行或传递完整路径）：

```bash
python skills/scanpy/scripts/qc_analysis.py input_file.h5ad --output filtered.h5ad
```

### 2. 归一化与预处理

```python
# 归一化到每个细胞 10,000 计数
sc.pp.normalize_total(adata, target_sum=1e4)

# 对数变换
sc.pp.log1p(adata)

# 保存原始计数供后续使用
adata.raw = adata

# 识别高变基因
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.pl.highly_variable_genes(adata)

# 子集化为高变基因
adata = adata[:, adata.var.highly_variable]

# 回归掉不需要的变异
sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])

# 缩放数据
sc.pp.scale(adata, max_value=10)
```

### 3. 降维

```python
# PCA
sc.tl.pca(adata, svd_solver='arpack')
sc.pl.pca_variance_ratio(adata, log=True)  # 检查肘部图

# 计算邻域图
sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)

# UMAP 可视化
sc.tl.umap(adata)
sc.pl.umap(adata, color='leiden')

# 替代方案：t-SNE
sc.tl.tsne(adata)
```

### 4. 聚类

```python
# Leiden 聚类（推荐）
sc.tl.leiden(adata, resolution=0.5)
sc.pl.umap(adata, color='leiden', legend_loc='on data')

# 尝试多种分辨率以找到最佳粒度
for res in [0.3, 0.5, 0.8, 1.0]:
    sc.tl.leiden(adata, resolution=res, key_added=f'leiden_{res}')
```

### 5. 标志基因识别

使用 `rank_genes_groups` 仅用于**探索性聚类标志基因**。逐个细胞的统计检验会夸大 p 值，因为细胞不是独立观测值。对于条件或样本之间的严格差异表达，请先进行伪批量分析（见下文）并使用 **pydeseq2** 或类似工具。

```python
# 查找每个聚类的标志基因（探索性）
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')

# 可视化结果
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False)
sc.pl.rank_genes_groups_heatmap(adata, n_genes=10)
sc.pl.rank_genes_groups_dotplot(adata, n_genes=5)

# 以 DataFrame 获取结果
markers = sc.get.rank_genes_groups_df(adata, group='0')
```

### 6. 细胞类型注释

```python
# 定义已知细胞类型的标志基因
marker_genes = ['CD3D', 'CD14', 'MS4A1', 'NKG7', 'FCGR3A']

# 可视化标志基因
sc.pl.umap(adata, color=marker_genes, use_raw=True)
sc.pl.dotplot(adata, var_names=marker_genes, groupby='leiden')

# 手动注释
cluster_to_celltype = {
    '0': 'CD4 T 细胞',
    '1': 'CD14+ 单核细胞',
    '2': 'B 细胞',
    '3': 'CD8 T 细胞',
}
adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_to_celltype)

# 可视化注释类型
sc.pl.umap(adata, color='cell_type', legend_loc='on data')
```

### 7. 保存结果

```python
# 保存处理后的数据
adata.write('results/processed_data.h5ad')

# 导出元数据
adata.obs.to_csv('results/cell_metadata.csv')
adata.var.to_csv('results/gene_metadata.csv')
```

## 常见任务

### 创建出版质量图表

优先使用 `sc.settings.autosave` 和 `sc.settings.figdir` 保存图表。每个图的 `save=` 参数在 scanpy 1.12 中已弃用。

```python
# 设置高质量默认值
sc.settings.set_figure_params(dpi=300, frameon=False, figsize=(5, 5))
sc.settings.file_format_figs = 'pdf'
sc.settings.figdir = './figures/'
sc.settings.autosave = True

# 使用自定义样式的 UMAP（通过 autosave 保存为 figures/umap.pdf）
sc.pl.umap(adata, color='cell_type',
           palette='Set2',
           legend_loc='on data',
           legend_fontsize=12,
           legend_fontoutline=2,
           frameon=False)

# 标志基因热图
sc.pl.heatmap(adata, var_names=genes, groupby='cell_type',
              swap_axes=True, show_gene_labels=True)

# 点图
sc.pl.dotplot(adata, var_names=genes, groupby='cell_type')
```

参考 `references/plotting_guide.md` 获取全面的可视化示例。

### 轨迹推断

```python
# PAGA（基于分区的图抽象）
sc.tl.paga(adata, groups='leiden')
sc.pl.paga(adata, color='leiden')

# 扩散伪时间
adata.uns['iroot'] = np.flatnonzero(adata.obs['leiden'] == '0')[0]
sc.tl.dpt(adata)
sc.pl.umap(adata, color='dpt_pseudotime')
```

### 伪批量与条件间差异表达

按样本和细胞类型进行伪批量，然后运行适当的 DE（例如 pydeseq2），而不是逐个细胞的 `rank_genes_groups`：

```python
# 按样本和细胞类型聚合计数（scanpy 1.12 中兼容 dask）
pb = sc.get.aggregate(
    adata,
    by=['sample', 'cell_type'],
    func='sum',
    layer='counts',  # 如有原始计数层则使用
)
# 后续：导出 pb 并使用 pydeseq2 进行条件比较
```

对于聚类内的快速探索性比较，`rank_genes_groups` 是可接受的，但谨慎解释 p 值：

```python
adata_subset = adata[adata.obs['cell_type'] == 'T cells']
sc.tl.rank_genes_groups(adata_subset, groupby='condition',
                         groups=['treated'], reference='control')
sc.pl.rank_genes_groups(adata_subset, groups=['treated'])
```

### 基因集评分

```python
# 对细胞进行基因集表达评分
gene_set = ['CD3D', 'CD3E', 'CD3G']
sc.tl.score_genes(adata, gene_set, score_name='T_cell_score')
sc.pl.umap(adata, color='T_cell_score')
```

### 批次校正

```python
# ComBat 批次校正
sc.pp.combat(adata, key='batch')

# 替代方案：使用 Harmony 或 scVI（独立包）
```

## 关键参数调整

### 质控
- `min_genes`：每个细胞最少基因数（通常 200-500）
- `min_cells`：每个基因最少细胞数（通常 3-10）
- `pct_counts_mt`：线粒体阈值（通常 5-20%）

### 归一化
- `target_sum`：每个细胞的目标计数（默认 1e4）

### 特征选择
- `n_top_genes`：高变基因数（通常 2000-3000）
- `min_mean`、`max_mean`、`min_disp`：HVG 选择参数

### 降维
- `n_pcs`：主成分数量（检查方差比图）
- `n_neighbors`：邻域数量（通常 10-30）

### 聚类
- `resolution`：聚类粒度（0.4-1.2，越高聚类越多）

## 常见陷阱与最佳实践

1. **始终保存原始计数**：在过滤基因前执行 `adata.raw = adata`
2. **仔细检查 QC 图**：根据数据集质量调整阈值
3. **使用 Leiden 聚类**：`sc.tl.louvain` 在 scanpy 1.12 中已弃用
4. **尝试多种聚类分辨率**：找到最佳粒度
5. **验证细胞类型注释**：使用多个标志基因
6. **对基因表达图使用 `use_raw=True`**：显示来自 `.raw` 的归一化计数
7. **检查 PCA 方差比**：确定最佳 PC 数量
8. **保存中间结果**：长工作流可能中途失败
9. **DE 使用伪批量**：不要将 `rank_genes_groups` 的 p 值视为条件间的严格 DE
10. **通过设置保存图表**：使用 `sc.settings.autosave` 而非图表函数上已弃用的 `save=`
11. **在 Scanpy 之前转换 R 对象**：使用 R 包将 Seurat 或 SingleCellExperiment `.rds` 文件转换为 `.h5ad`，保留计数、元数据和基因标识符

## 捆绑资源

### scripts/（CLI 工具包）
一组可组合的 `.h5ad` 输入/`.h5ad` 输出脚本，覆盖整个工作流以及一条命令的端到端流程。请参阅上面的**脚本工具包**部分获取完整表格和串联示例。每个脚本都有 `--help`。文件：

- `_common.py` — 被其他脚本导入的共享加载/保存/图形辅助工具（非 CLI）
- `run_pipeline.py` — 一条命令的完整流水线（标志或 `--config` JSON）
- `inspect_data.py`、`convert.py` — 探索和加载/转换任意输入格式
- `qc_analysis.py`、`preprocess.py`、`reduce_dimensions.py`、`batch_correct.py`、`cluster.py` — 流水线步骤
- `find_markers.py`、`annotate.py`、`score_genes.py`、`pseudobulk.py` — 标志基因、注释、评分、DE 准备
- `subset.py`、`plot.py` — 按元数据/基因子集化；生成任意标准图表

**在从头编写 scanpy 代码之前，默认使用这些脚本。**

### references/standard_workflow.md
完整的逐步工作流，包含详细解释和代码示例，涵盖：
- 数据加载和设置
- 带可视化的质控
- 归一化和缩放
- 特征选择
- 降维（PCA、UMAP、t-SNE）
- 聚类（Leiden）
- 双峰检测（scrublet）和伪批量聚合
- 标志基因识别
- 细胞类型注释
- 轨迹推断
- 差异表达

在从头进行完整分析时阅读此参考。

### references/api_reference.md
按模块组织的 scanpy 函数快速参考指南：
- 读写数据（`sc.read_*`、`adata.write_*`）
- 预处理（`sc.pp.*`）
- 工具（`sc.tl.*`）
- 绘图（`sc.pl.*`）
- AnnData 结构和操作
- 设置和工具

用于快速查找函数签名和常用参数。

### references/plotting_guide.md
全面的可视化指南，包括：
- 质控图表
- 降维可视化
- 聚类可视化
- 标志基因图表（热图、点图、小提琴图）
- 轨迹和伪时间图
- 出版质量自定义
- 多面板图表
- 颜色主题和样式

在创建出版就绪的图表时查阅此指南。

### references/r_interop.md
Agent 运行手册，用于在 macOS、Linux 和 Windows 上安装 R、安装 CRAN/Bioconductor 转换包、检查 `.rds`/`.RData` 输入、将 Seurat 或 SingleCellExperiment 对象转换为 `.h5ad`，以及在 Scanpy 中验证结果。

### assets/analysis_template.py
完整的分析模板，提供从数据加载到细胞类型注释的完整工作流。复制并自定义此模板用于新分析：

```bash
cp assets/analysis_template.py my_analysis.py
# 编辑参数并运行
python my_analysis.py
```

该模板包含所有标准步骤以及可配置参数和有用的注释。

### assets/ JSON 模板
可直接编辑和传递的模板，无需从头编写配置/映射：
- `assets/pipeline_config.json` — `run_pipeline.py --config` 的参数集
- `assets/celltype_mapping.json` — 供 `annotate.py --mapping` 使用的聚类 → 细胞类型映射
- `assets/gene_signatures.json` — 供 `score_genes.py --gene-sets` 使用的基因集签名

## 附加资源

- **Scanpy 官方文档**：https://scanpy.scverse.org/en/stable/
- **Scanpy 教程**：https://scanpy.scverse.org/en/stable/tutorials/index.html
- **版本发布说明**：https://scanpy.scverse.org/en/stable/release-notes/index.html
- **scverse 生态系统**：https://scverse.org/（相关工具：squidpy、scvi-tools、cellrank）
- **R 互操作性**：https://www.bioconductor.org/packages/release/bioc/html/zellkonverter.html 和 https://mojaveazure.github.io/seurat-disk/
- **最佳实践**：Luecken & Theis (2019) "Current best practices in single-cell RNA-seq"

## 有效分析的技巧

1. **从模板开始**：使用 `assets/analysis_template.py` 作为起点
2. **先运行 QC 脚本**：使用 `scripts/qc_analysis.py` 进行初始过滤
3. **根据需要查阅参考**：将工作流和 API 参考加载到上下文中
4. **迭代聚类**：尝试多种分辨率和可视化方法
5. **进行生物学验证**：检查标志基因是否与预期细胞类型匹配
6. **记录参数**：记录 QC 阈值和分析设置
7. **保存检查点**：在关键步骤写入中间结果
