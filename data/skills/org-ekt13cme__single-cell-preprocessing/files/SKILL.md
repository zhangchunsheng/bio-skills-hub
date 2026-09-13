---
name: bio-single-cell-preprocessing-zh
description: 使用 Seurat（R）和 Scanpy（Python）完成单细胞 RNA 测序质量控制、过滤、标准化和特征选择；覆盖按样本 QC、双细胞与环境 RNA 处理及可复现输出。
tool_type: mixed
primary_tool: Seurat
---

# 单细胞 RNA 测序预处理

## 适用场景

当用户提出“预处理我的 scRNA-seq 数据”时，完成从原始计数矩阵到适合降维和聚类的数据准备：数据检查、QC、过滤、可选的空液滴/环境 RNA/双细胞处理、标准化、高变基因选择与缩放。

- Scanpy：`calculate_qc_metrics()` -> 过滤 -> 保存计数层 -> `normalize_total()` + `log1p()` -> HVG -> 回归（可选）-> 缩放。
- Seurat：QC -> 过滤 -> `NormalizeData()` -> `FindVariableFeatures()` -> `ScaleData()`；或在 QC 后选择 `SCTransform()` 流程。

不要把不同样本、组织或实验方案的固定阈值当成普适规则。必须先按样本/批次检查 QC 分布，再记录并应用最终阈值。

## 版本兼容性

参考示例基于 ggplot2 3.5+、matplotlib 3.8+、numpy 1.26+、scanpy 1.10+ 和近期 Seurat 版本编写。

- Python：运行 `pip show <package>`，再用 `help(module.function)` 确认函数签名。
- R：运行 `packageVersion('<pkg>')`，再用 `?function_name` 确认参数。
- 若出现 `ImportError`、`AttributeError` 或 `TypeError`，先检查当前环境 API 并调整代码，不要盲目重试。

## 预处理原则与顺序

1. 确认输入是原始、未对数化的整数 UMI 计数；去重基因名称并确认细胞条形码唯一。
2. 按样本或批次独立计算并可视化 QC；不要先合并所有样本再用单一全局阈值。
3. 若有原始 droplets，先进行空液滴识别；环境 RNA 校正应在下游表达分析前完成。
4. 在常规 QC 过滤后进行双细胞检测；高基因数仅是筛查线索，不可替代双细胞算法。
5. 过滤后立即保存原始计数到专用层/assay，再进行标准化与高变基因选择。
6. 在同一 assay 或矩阵上选择一条规范化路线：LogNormalize 工作流或 SCTransform 工作流，不要串行混用。

## 物种和基因命名适配

线粒体基因模式取决于特征命名，不应硬编码为一种写法。

| 数据 | 常见模式 | 建议 |
|------|----------|------|
| 人类 gene symbol | `^MT-` | 先检查 `MT-` 基因是否存在 |
| 小鼠 gene symbol | `^mt-` | 常见于 Mouse Genome Informatics 格式 |
| Ensembl ID 或其他物种 | 无可靠前缀 | 用注释表生成线粒体基因布尔向量 |

应在运行前执行类似 `adata.var_names[:5]` 或 `head(rownames(seurat_obj))` 的检查。若样本存在人-鼠混样、移植模型或多物种实验，还应在 QC 前依据基因注释检查物种来源与交叉物种污染。

---

## Scanpy（Python）

### 必需导入

```python
import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt
```

### 读取与输入检查

```python
adata = sc.read_10x_mtx('filtered_feature_bc_matrix/', var_names='gene_symbols')
adata.var_names_make_unique()

# 原始 UMI 计数通常应为非负整数；不要把已 log1p 的矩阵再次标准化
if adata.X.min() < 0:
    raise ValueError('表达矩阵包含负值；请确认输入是否为原始计数。')

print(f'输入：{adata.n_obs} 个细胞，{adata.n_vars} 个基因')
```

### 计算与可视化 QC 指标

```python
# 按数据物种和特征命名选择模式：人类通常为 MT-，小鼠通常为 mt-
mt_pattern = 'MT-'  # 小鼠 gene symbol 数据改为 'mt-'
adata.var['mt'] = adata.var_names.str.startswith(mt_pattern)

sc.pp.calculate_qc_metrics(
    adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True
)

# 新增关键指标：n_genes_by_counts、total_counts、pct_counts_mt
sc.pl.violin(
    adata,
    ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
    jitter=0.4,
    multi_panel=True,
)
sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts')
```

若 `adata.obs` 中有样本列，例如 `sample`，应按样本检查分布，而不是依据合并后的总体分布确定阈值：

```python
sc.pl.violin(
    adata,
    ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
    groupby='sample',
    multi_panel=True,
)
```

### 选择 QC 阈值

下列数值只是 droplet-based scRNA-seq 的起始参考，不是默认应直接使用的过滤规则：

| 指标 | 常用起始范围 | 解释 |
|------|--------------|------|
| 最低检测基因数 | 200-500 | 过滤空液滴和低 RNA 细胞 |
| 最高检测基因数 | 2,500-5,000 | 仅用于标记潜在双细胞 |
| 线粒体比例上限 | 5-20% | 过滤受损细胞，需按组织调整 |
| 基因最少检出细胞数 | 3-10 | 过滤极低检出率基因 |

优先在每个样本中使用 QC 图、分位数或 MAD（median absolute deviation）识别离群值。snRNA-seq 通常具有更少的基因和更低的线粒体比例；高代谢组织、肿瘤或应激样本可能天然具有更高的线粒体比例。对这些数据不应机械套用阈值。

```python
# 示例：使用每个细胞至少 200 个基因和低于 20% mt 作为待审查的起始条件
n_cells_before = adata.n_obs
sc.pp.filter_cells(adata, min_genes=200)
adata = adata[adata.obs['pct_counts_mt'] < 20, :].copy()
sc.pp.filter_genes(adata, min_cells=3)
print(f'过滤前：{n_cells_before}；过滤后：{adata.n_obs} 个细胞，{adata.n_vars} 个基因')
```

### 空液滴、环境 RNA 与双细胞（可选但建议评估）

- **空液滴：** 若输入来自 `raw_feature_bc_matrix` 而非上游已过滤矩阵，可在 R 中用 DropletUtils 的 EmptyDrops，或使用相应平台的细胞调用结果；应在常规 QC 之前完成。
- **环境 RNA：** 若发现广泛而低水平的非预期标记表达，可评估 SoupX、CellBender 或 DecontX；校正方法与参数必须记录，并在下游 marker 解释中说明。
- **双细胞：** 在常规 QC 后、聚类解释前，用 Scrublet（Python）等方法检测。高 `n_genes_by_counts` 只能发现一部分双细胞，不能作为唯一判据。

```python
# Scrublet 为独立包；应在每个样本/文库内运行，并结合预期双细胞率解释。
# import scrublet as scr
# scrub = scr.Scrublet(adata.layers['counts'])
# scores, calls = scrub.scrub_doublets()
# adata.obs['doublet_score'] = scores
# adata.obs['predicted_doublet'] = calls
# adata = adata[~adata.obs['predicted_doublet']].copy()
```

### 保存原始计数与两种 HVG 路线

`layers['counts']` 用于保存过滤后的原始计数，供计数模型和 `seurat_v3` HVG 使用。`adata.raw` 通常应在 `normalize_total()` 和 `log1p()` 后、HVG 子集化前保存，以便后续绘图和差异表达使用完整的已标准化基因集。

#### 路线 A：对数标准化数据上的 HVG

```python
# 过滤后、标准化前保存原始计数
adata.layers['counts'] = adata.X.copy()

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata.copy()

# 默认 flavor 适用于当前已 log1p 的 adata.X
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.pl.highly_variable_genes(adata)

adata = adata[:, adata.var['highly_variable']].copy()
# 若要回归，先回归再缩放；默认不回归，除非有明确技术混杂证据。
sc.pp.scale(adata, max_value=10)
```

#### 路线 B：原始计数上的 Seurat v3 HVG

```python
# 过滤后、标准化前保存原始计数
adata.layers['counts'] = adata.X.copy()

# seurat_v3 在原始计数层上选择 HVG
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=2000,
    flavor='seurat_v3',
    layer='counts',
)

# 仍对 adata.X 执行标准化，供 PCA/邻居图等下游分析使用
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata.copy()

adata = adata[:, adata.var['highly_variable']].copy()
sc.pp.scale(adata, max_value=10)
```

不要在没有 `counts` layer 的情况下指定 `layer='counts'`。不要将未标准化计数赋给 `adata.raw` 后又将其当作对数标准化表达使用。

### 回归与缩放

```python
# 仅在确认技术协变量掩盖目标信号时使用；回归必须发生在缩放前。
# sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])
# sc.pp.scale(adata, max_value=10)
```

回归 `total_counts` 或 `pct_counts_mt` 可能同时移除真实生物学变异，例如细胞周期、代谢状态或受损细胞群。默认不回归；若使用，比较回归前后结果并记录理由。大型数据集上 `regress_out()` 和 `scale()` 可能显著增加内存占用；应先子集到 HVG，仅缩放必要特征，并避免不必要的稠密化。

### 完整 Scanpy 流程：原始计数 Seurat v3 HVG

```python
import scanpy as sc

adata = sc.read_10x_mtx('filtered_feature_bc_matrix/', var_names='gene_symbols')
adata.var_names_make_unique()

# 人类通常使用 MT-；小鼠 gene symbol 通常改用 mt-
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)

# 阈值必须在查看每个样本 QC 分布后确定
n_cells_before = adata.n_obs
sc.pp.filter_cells(adata, min_genes=200)
adata = adata[adata.obs['pct_counts_mt'] < 20, :].copy()
sc.pp.filter_genes(adata, min_cells=3)
print(f'保留 {adata.n_obs}/{n_cells_before} 个细胞')

# 保存过滤后的原始计数，供 seurat_v3 HVG 和后续计数方法使用
adata.layers['counts'] = adata.X.copy()
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor='seurat_v3', layer='counts')

# 标准化表达用于下游降维；raw 保留完整的 log-normalized 基因集
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata.copy()

adata = adata[:, adata.var['highly_variable']].copy()
sc.pp.scale(adata, max_value=10)
```

---

## Seurat（R）

### 必需加载的包

```r
library(Seurat)
library(ggplot2)
```

### QC 指标、物种适配与按样本可视化

```r
# 人类 gene symbol 通常为 ^MT-；小鼠 gene symbol 常为 ^mt-
mt_pattern <- '^MT-'
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = mt_pattern)

VlnPlot(seurat_obj, features = c('nFeature_RNA', 'nCount_RNA', 'percent.mt'), ncol = 3)
plot1 <- FeatureScatter(seurat_obj, feature1 = 'nCount_RNA', feature2 = 'percent.mt')
plot2 <- FeatureScatter(seurat_obj, feature1 = 'nCount_RNA', feature2 = 'nFeature_RNA')
plot1 + plot2

# 若元数据有样本列，应先按 orig.ident 或相应列比较 QC 分布
# VlnPlot(seurat_obj, features = c('nFeature_RNA', 'nCount_RNA', 'percent.mt'), group.by = 'orig.ident', ncol = 3)
```

对 Ensembl ID 或其他物种，不应假设线粒体前缀。应从可靠注释表建立线粒体基因集合，再用 `PercentageFeatureSet(..., features = mt_features)` 计算比例。

### 过滤与双细胞处理

```r
# 起始示例，不是固定通用规则；先按样本 QC 图调整阈值
n_cells_before <- ncol(seurat_obj)
seurat_obj <- subset(
    seurat_obj,
    subset = nFeature_RNA > 200 & nFeature_RNA < 5000 & percent.mt < 20
)
cat('过滤前：', n_cells_before, '；过滤后：', ncol(seurat_obj), '个细胞\n')
```

- 原始 droplets 的空液滴识别可使用 DropletUtils::EmptyDrops，并应在创建最终 Seurat 对象前完成。
- 环境 RNA 可评估 SoupX 或 DecontX；保留校正前后信息，避免将校正造成的变化误解为生物学效应。
- 双细胞应在每个文库中用 scDblFinder 或 DoubletFinder 等方法检测；高 `nFeature_RNA` 只能作为候选提示，不应单独决定删除。

### 路线 A：LogNormalize 工作流

```r
# 该流程与 SCTransform 二选一；不要在同一 RNA assay 上串行混用两套步骤。
seurat_obj <- NormalizeData(
    seurat_obj,
    normalization.method = 'LogNormalize',
    scale.factor = 10000
)
seurat_obj <- FindVariableFeatures(
    seurat_obj,
    selection.method = 'vst',
    nfeatures = 2000
)

# 默认不回归技术协变量；如需回归，在 ScaleData 中一次性完成。
seurat_obj <- ScaleData(seurat_obj, features = VariableFeatures(seurat_obj))
```

```r
# 若确有技术混杂的诊断证据，可改用：
# seurat_obj <- ScaleData(
#     seurat_obj,
#     features = VariableFeatures(seurat_obj),
#     vars.to.regress = c('percent.mt', 'nCount_RNA')
# )
```

回归可能删除真实的细胞周期、代谢或应激信号。使用前应比较回归前后 PCA/聚类，并记录理由与协变量。

### 路线 B：SCTransform 工作流

```r
# 选择 SCTransform 后，不需要再对同一 SCT assay 调用 NormalizeData、
# FindVariableFeatures 或 ScaleData。是否回归 percent.mt 需要根据诊断结果决定。
seurat_obj <- SCTransform(
    seurat_obj,
    vars.to.regress = NULL,
    verbose = FALSE
)
```

```r
# 仅在有明确技术混杂证据时：
# seurat_obj <- SCTransform(seurat_obj, vars.to.regress = 'percent.mt', verbose = FALSE)
```

SCTransform 并非所有数据的唯一首选。应基于数据规模、批次整合方案、下游统计方法和团队既有分析规范，在 LogNormalize 与 SCTransform 间选择一种路线并保持一致。

### 可视化高变特征

```r
# 仅用于 LogNormalize 路线
# top10 <- head(VariableFeatures(seurat_obj), 10)
# plot1 <- VariableFeaturePlot(seurat_obj)
# LabelPoints(plot = plot1, points = top10, repel = TRUE)
```

对大型对象，优先仅对高变特征缩放；避免不必要地缩放所有基因，以降低内存与计算成本。

---

## 可复现性与输出检查清单

完成预处理时，必须保存或报告：

- 输入来源、基因命名体系、物种，以及是否为原始整数计数。
- 每个样本/批次在过滤前后的细胞数、基因数、删除比例及最终阈值。
- 空液滴、环境 RNA、双细胞检测是否执行，所用工具、版本、参数和删除规则。
- 标准化路线、HVG 方法与数量、是否回归协变量及其理由。
- 软件版本、随机种子（对含随机步骤的方法）和完整运行脚本。
- 过滤后的原始计数、标准化对象和 QC 图；例如保存为 `.h5ad` 或 `.rds`。

在开始 PCA、邻居图、UMAP、聚类或 marker 分析前，确认：

1. 每个样本均保留合理数量的细胞，且没有样本被意外完全过滤。
2. QC 指标没有显示未处理的极端离群群体。
3. 双细胞候选率与平台、装载量和预期双细胞率基本一致。
4. `counts` layer（Scanpy）或原始 RNA assay（Seurat）仍可用于需要原始计数的下游方法。
5. HVG、缩放矩阵和 `raw`/assay 的数据语义与下游函数要求一致。

## 方法对比

| 步骤 | Scanpy | Seurat LogNormalize | Seurat SCTransform |
|------|--------|---------------------|--------------------|
| 原始计数保存 | `layers['counts']` | RNA assay counts slot | RNA assay counts slot |
| 标准化 | `normalize_total` + `log1p` | `NormalizeData` | `SCTransform` |
| HVG | `highly_variable_genes` | `FindVariableFeatures` | 内置 |
| 缩放 | `scale` | `ScaleData` | 内置 |
| 回归 | 可选 `regress_out`，后接 `scale` | `ScaleData(vars.to.regress)` | `SCTransform(vars.to.regress)` |

## 相关技能

- `data-io`：在预处理前加载和检查数据。
- `clustering`：在预处理后运行 PCA、邻居图和聚类。
- `markers-annotation`：聚类后寻找标记基因并进行细胞注释。
