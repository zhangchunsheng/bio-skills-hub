---
name: "单细胞多组学分析"
description: "面向单细胞测序与多组学研究的规范化分析技能，支持 scRNA-seq、CITE-seq、scATAC-seq、TARGET-seq 和 Multiome 数据"
globs: ["*.h5ad", "*.h5", "*.fastq.gz", "*.bam", "*.mtx", "*.csv", "*.tsv"]
alwaysAllow: ["Bash", "Read", "Write"]
---

# 单细胞多组学分析技能

## 使用原则

1. 先确认物种、组织或细胞来源、测序平台、数据格式、样本分组和生物学重复数，再选择分析流程。
2. 先检查输入文件、矩阵层、细胞条形码、基因命名、样本信息和软件版本；不要假设数据一定是原始 counts。
3. 明确区分探索性细胞级分析和正式的样本级统计推断。
4. 所有阈值都应根据 QC 分布、实验平台和组织类型调整，不要机械套用固定参数。
5. 执行分析时记录参数、软件版本、参考数据库、随机种子和输出文件，保留原始对象与中间结果。
6. 自动细胞类型注释只能作为辅助结果，必须结合标记基因、表达分布和生物学背景人工复核。
7. 批次校正不得掩盖真实生物学差异；整合前后应分别检查批次混合度和生物学结构。

## 支持的数据类型

### 单模态数据
- scRNA-seq：10x Genomics、Smart-seq2、Drop-seq 等平台
- scATAC-seq：fragment 文件、peak-by-cell 矩阵和相关单细胞对象

### 多模态数据
- CITE-seq：RNA 与表面蛋白联合分析
- Multiome：RNA 与 ATAC 联合分析
- TARGET-seq：转录组与靶向基因型/突变检测联合分析

对于 FASTQ 或 BAM，若需要从原始测序数据开始，应先完成测序质控、比对或准比对、barcode/UMI 处理以及表达矩阵或 fragment 文件生成；本技能不能把文件扩展名本身视为已完成预处理。

## scRNA-seq 核心流程

### 1. 数据读取与质量控制

常见输入包括 10x Matrix Market、10x H5 和 AnnData。示例：

```python
import scanpy as sc

adata = sc.read_10x_mtx(
    "path/to/matrix",
    var_names="gene_symbols",
    cache=True
)
adata.var_names_make_unique()
```

QC 指标应写入 `adata.obs`，并使用 Scanpy 的 QC 函数计算：

```python
import numpy as np

# 人类通常为 MT-；小鼠常见为 mt-，应按物种确认
adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-")
adata.var["ribo"] = adata.var_names.str.upper().str.startswith(("RPS", "RPL"))

sc.pp.calculate_qc_metrics(
    adata,
    qc_vars=["mt", "ribo"],
    percent_top=None,
    log1p=False,
    inplace=True
)

# 仅作为起始示例，实际阈值应根据 QC 分布调整
adata = adata[
    (adata.obs["n_genes_by_counts"] >= 200) &
    (adata.obs["pct_counts_mt"] < 20),
    :
].copy()
sc.pp.filter_genes(adata, min_cells=3)
```

同时评估：低基因数、高线粒体比例、异常总 counts、核糖体比例、ambient RNA 和 doublet。可考虑 Scrublet、DoubletFinder、scDblFinder、SoupX 或 CellBender，但应结合预期 doublet rate 和实验设计解释结果。

### 2. 归一化与特征选择

```python
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=2000,
    flavor="seurat_v3"
)
```

如果使用 `seurat_v3` flavor，应确认输入层为原始 counts，并按 Scanpy 版本要求设置 `layer="counts"` 或相应参数。不要在已经 log-normalized 的数据上重复进行 counts 专用方法。

Seurat 示例：

```r
library(Seurat)
seurat_obj <- Read10X(data.dir = "path/to/matrix")
seurat_obj <- CreateSeuratObject(counts = seurat_obj)
seurat_obj <- NormalizeData(seurat_obj, normalization.method = "LogNormalize")
seurat_obj <- FindVariableFeatures(seurat_obj, selection.method = "vst", nfeatures = 2000)
```

### 3. 降维、邻居图与聚类

```python
sc.tl.pca(adata, svd_solver="arpack")
sc.pl.pca_variance_ratio(adata, log=True)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5)
sc.pl.umap(adata, color=["leiden"])
```

`n_neighbors`、`n_pcs` 和 `resolution` 仅为起始值，应结合 PCA 方差、邻居图稳定性、聚类稳定性和标记基因结果调整。Leiden 依赖相应的 Python 包和版本，应在实际环境中确认 API。

### 4. 细胞类型注释

可使用 CellMarker、PanglaoDB、Human Cell Atlas 等参考资源，或 CellTypist、scmap、scANVI、scCATCH、SingleR 等工具。

SingleR 为 R/Bioconductor 工具，示例：

```r
library(SingleR)
library(celldex)
ref <- HumanPrimaryCellAtlasData()
result <- SingleR(
  test = GetAssayData(seurat_obj, layer = "data"),
  ref = ref,
  labels = ref$label.main
)
seurat_obj$cell_type <- result$labels
```

自动注释必须使用与物种、组织和实验条件相匹配的参考集，并结合 marker expression 和 UMAP 分布复核。

### 5. 差异表达与样本级统计

探索性细胞级 marker 分析示例：

```python
sc.tl.rank_genes_groups(adata, groupby="leiden", method="wilcoxon")
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False)
```

正式的条件比较应优先以样本或生物学重复为统计单位进行 pseudobulk 分析，再使用 edgeR、DESeq2 或 limma-voom。不能把同一样本中的每个细胞直接当作独立生物学重复，否则会产生伪重复和夸大的显著性。

差异分析应报告效应量、置信区间或 FDR，并进行 Benjamini-Hochberg 多重检验校正。Wilcoxon、MAST 和 Kruskal-Wallis 等方法的选择应依据比较单位、设计和数据分布。

### 6. 批次效应与数据整合

可考虑 Harmony、BBKNN、Scanorama、Seurat anchors 或 scVI。使用前确认各工具版本和输入对象要求；整合后同时检查：

- 相同细胞类型是否在批次间合理混合
- 已知生物学差异是否仍然存在
- 稀有细胞群是否被错误合并
- 整合结果是否仅用于可视化/聚类，还是用于下游表达统计

正式差异表达通常应使用未被过度校正的 counts，并在模型中显式处理样本和批次因素。

## RNA velocity 与轨迹分析

RNA velocity 需要包含 spliced/unspliced 层或等价的剪接信息，普通表达矩阵通常不能直接用于 velocity。建议使用 velocyto 或其他工具生成所需层，再使用 scVelo：

```python
import scvelo as scv

scv.pp.filter_and_normalize(adata)
scv.pp.moments(adata, n_pcs=30, n_neighbors=30)
scv.tl.velocity(adata, mode="stochastic")
scv.tl.velocity_graph(adata)
scv.pl.velocity_embedding_stream(adata)
```

若采用 dynamical model，应在完成上述准备后运行 `scv.tl.recover_dynamics(adata)`，再推断 velocity 和 latent time。轨迹和伪时间是模型依赖的推断结果，不应直接解释为真实时间顺序或因果关系。

## scATAC-seq 与 Multiome

scATAC-seq 不应只套用 RNA 流程。至少应评估：

- fragment 数量
- TSS enrichment
- nucleosome signal
- transcription start site 相关质量
- FRiP/peak 相关指标
- doublet 与低质量细胞

常见工具包括 ArchR、Signac、SnapATAC2 和 MuData/Muon。典型步骤包括 TF-IDF、LSI 降维、邻居图、聚类、peak 分析、gene activity、motif enrichment 和差异可及性分析。

Multiome 可使用 Muon：

```python
import muon as mu

mdata = mu.read_10x_h5("multiome.h5")
rna = mdata.mod["rna"]
atac = mdata.mod["atac"]

# RNA 与 ATAC 应分别进行适配的 QC、归一化和降维
mu.pp.filter_vars(rna)
sc.pp.normalize_total(rna)
sc.pp.log1p(rna)
```

应明确说明 RNA 和 ATAC 的 QC、特征选择与降维方法不同，联合分析不能简单地对两个模态执行同一套参数。

## CITE-seq 与 TotalVI

TotalVI 需要 RNA counts 和蛋白表达矩阵，并应正确指定蛋白矩阵所在位置：

```python
import scvi

scvi.model.TOTALVI.setup_anndata(
    adata,
    protein_expression_obsm_key="protein_expression"
)
model = scvi.model.TOTALVI(adata)
model.train()
adata.obsm["X_totalVI"] = model.get_latent_representation()
```

在运行前确认 `adata.layers` 或 `adata.X` 为适合模型的 counts，蛋白矩阵已经正确导入，并检查 scvi-tools 版本对应的 API。TotalVI 的潜在表示可用于可视化、聚类和批次建模，但仍需进行生物学验证。

scVI 示例：

```python
scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="batch")
vae = scvi.model.SCVI(adata)
vae.train()
adata.obsm["X_scVI"] = vae.get_latent_representation()
```

## 高级分析

### 基因集富集

可使用 gseapy、clusterProfiler、GSEA 或 fgsea。应根据物种选择基因集，并明确输入的是 marker、差异基因还是排序后的全基因列表；不要只使用显著性而忽略效应量和背景基因集。

### 细胞间通讯

CellChat 主要在 R 中使用 Seurat 对象或表达矩阵。使用时需转换对象、设置细胞身份、选择物种数据库，并完成过表达基因、配体受体相互作用、通信概率和网络聚合等步骤。通讯推断是基于表达和先验数据库的统计推断，不等同于已验证的细胞间真实信号传递。

### 转录因子调控网络

SCENIC/pySCENIC 需要表达矩阵、物种匹配的 motif/注释数据库和足够的计算资源。典型流程包括基因过滤、共表达网络推断、motif 富集和 AUCell 活性评分。应明确使用 R 版 SCENIC 还是 Python 版 pySCENIC，不能混用对象和函数。

## 可视化

```python
sc.pl.umap(adata, color=["cell_type", "CD3D", "CD8A"])
sc.pl.violin(adata, ["n_genes_by_counts", "pct_counts_mt"], groupby="leiden")
sc.pl.matrixplot(adata, var_names=marker_genes, groupby="leiden")
sc.pl.dotplot(adata, var_names=marker_genes, groupby="leiden")
```

报告中可包含：QC 图、细胞类型 UMAP、marker 基因图、差异表达图、功能富集图、轨迹图、细胞通讯图和调控网络图。图表应标注样本数、细胞数、统计方法、阈值和 FDR。

## 实验设计与资源估计

- 细胞数量、测序深度和质量阈值应按平台、组织和目标细胞群确定。
- 正式比较建议至少有多个独立生物学重复；重复数不足时应明确统计局限。
- 100K 细胞的内存和计算时间高度依赖矩阵稀疏性、模态数和模型，不能保证固定为 32GB 或 2–24 小时；应在实际数据上进行资源评估。
- 原始 FASTQ、表达矩阵、fragment 文件、元数据、分析对象和参数日志应分层备份。

## 常见问题

1. 线粒体阈值：根据 QC 分布和组织类型选择，不要默认固定阈值。
2. Doublet：结合实验预期 doublet rate 和工具评分判断。
3. Ambient RNA：必要时使用 SoupX 或 CellBender，并比较校正前后结果。
4. 批次效应：同时检查批次混合与真实生物学信号，避免过度整合。
5. 低表达基因：按细胞数和目标分析调整过滤阈值。
6. 差异表达：优先样本级 pseudobulk，防止伪重复。
7. 版本兼容：执行代码前确认 Scanpy、Seurat、scvi-tools、scVelo、Muon 和相关包的版本。

## 分析报告结构

1. 摘要：数据概览、QC 结果和主要发现
2. 方法：输入数据、软件版本、参数、参考数据库和统计模型
3. 结果：细胞组成、聚类、注释、差异、轨迹和多组学结果
4. 质量与局限：过滤、批次、重复数、潜在混杂和模型限制
5. 讨论：生物学意义、可验证假设和后续实验

使用本技能时，应根据具体数据类型和研究目标选择工具，先验证输入和代码环境，再执行分析；输出结果时同时提供方法、关键参数、质量控制和统计局限。