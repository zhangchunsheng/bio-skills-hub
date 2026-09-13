---
name: fastCNV
description: >
  使用 fastCNV 进行单细胞 RNA-seq 和空间转录组学（ST）数据的拷贝数变异（CNV）检测。
  fastCNV 是基于 SeuratObject 的 R 包，支持 scRNA-seq、Visium 和 Visium HD 数据，
  可快速检测、可视化和分析 CNV，计算 cnv_fraction，构建亚克隆树。
  提供一站式 fastCNV() 和 fastCNV_10XHD() 函数，自动完成从计数聚合到热图绘制的全流程。
author: LKP <kunpeng.liao@abiosciences.com>
platform: github
source: https://github.com/must-bioinfo/fastCNV
tags: [scRNA-seq, CNV, copy-number, spatial-transcriptomics, Visium, Visium-HD, Seurat, R, tumor]
version: 1.1.10
generated: 2026-08-02T00:00:00+08:00
---

# fastCNV — 快速单细胞与空间转录组 CNV 检测工具

## 概述

**fastCNV** 是一个 R 包，用于在单细胞 RNA-seq（scRNA-seq）或空间转录组学（ST）数据中检测、可视化和分析推定的拷贝数变异（CNV），包括 Visium HD 数据。基于 `SeuratObject` 构建，可轻松集成到 scRNA-seq 或 ST 分析流程中。

核心特性：
- **多数据类型支持**：scRNA-seq、Visium、Visium HD
- **一站式工作流**：`fastCNV()` 自动完成计数聚合、CNV 计算、聚类和热图绘制
- **亚克隆分析**：基于 CNV 分数构建亚克隆聚类和进化树
- **多样本处理**：支持跨样本构建池化参考
- **快速运行**：约 4,000 个细胞仅需约 1 分钟，Visium HD（16µm，约 150,000 个 spot）约 40 分钟

---

## 适用场景

当用户需要执行以下任务时使用此 Skill：

- 从 scRNA-seq 或空间转录组数据检测拷贝数变异（CNV）
- 区分肿瘤细胞与正常细胞（基于 CNV fraction）
- 在 Visium 或 Visium HD 空间数据上进行 CNV 分析
- 构建 CNV 亚克隆聚类和亚克隆进化树
- 基于 Seurat 对象进行 CNV 热图可视化

---

## 安装

### 从 GitHub 安装

```r
# 安装 fastCNV
remotes::install_github("must-bioinfo/fastCNV")

# 安装示例数据包（可选，用于教程）
remotes::install_github("must-bioinfo/fastCNVdata")
```

### 系统要求

- R >= 3.5.0
- 依赖包：Seurat, SeuratObject, SeuratWrappers, Banksy, biomaRt, ComplexHeatmap, circlize, dplyr, ggplot2, ggtree, FNN, ape, phangorn 等
- **仅支持人类数据**（小鼠数据支持开发中）
- Visium HD 16µm：约 64 GB RAM；8µm：最高约 200 GB RAM

---

## 数据准备

fastCNV 基于 **Seurat 对象** 工作，要求：

1. **Seurat 对象**：包含表达矩阵的 Seurat 或 Seurat v5 对象
2. **参考注释**（推荐）：`metadata` 中有一列标识正常/健康细胞（如免疫细胞、正常上皮等）
3. **Visium HD**：默认使用 `Spatial.016um` assay

### 注释格式

参考注释可以是任意类型的标注，只需指定 `referenceVar`（metadata 列名）和 `referenceLabel`（参考标签值）。

```r
# 查看可用注释
unique(seuratObj[["annot"]])
```

---

## 完整工作流

### 1. 单样本 scRNA-seq 分析

```r
library(fastCNV)

# 运行完整 CNV 分析
seuratObj <- fastCNV(
    seuratObj = scColon1,
    sampleName = "scColon1",
    referenceVar = "annot",
    referenceLabel = c("TNKILC", "Myeloid", "B", "Mast", "Plasma"),
    printPlot = TRUE
)
```

此调用自动执行：
- `prepareCountsForCNVAnalysis`：聚类并聚合为 metaspot
- `CNVAnalysis`：计算 CNV 基因组分数
- `CNVPerChromosomeArm`：按染色体臂计算 CNV
- `CNVCluster`：层次聚类生成 cnv_clusters
- `plotCNVResults`：生成 CNV 热图

### 2. 多样本分析（池化参考）

```r
# 多样本同时分析，自动构建跨样本池化参考
samples <- fastCNV(
    seuratObj = c(sample1, sample2, sample3),
    sampleName = c("sample1", "sample2", "sample3"),
    referenceVar = "Annotations",
    referenceLabel = c("Healthy1", "Healthy2", "Healthy3")
)
```

> 当提供多个样本时，fastCNV 会**跨所有样本构建池化参考**，因此一个样本中的健康组织可用作所有样本的参考。

### 3. Visium HD 分析

```r
# 运行 Visium HD CNV 分析
seuratHD <- fastCNV_10XHD(
    seuratObjHD = visiumHD_obj,
    sampleName = "HD_sample",
    referenceVar = "annotation",
    referenceLabel = "Normal",
    assay = "Spatial.016um"   # 默认 16µm bin
)
```

---

## 主函数 API

### `fastCNV()` — scRNA-seq / Visium 一站式分析

```r
fastCNV(
    seuratObj,                    # Seurat 对象或列表
    sampleName,                   # 样本名称
    referenceVar = NULL,          # 参考注释列名
    referenceLabel = NULL,        # 参考标签值
    assay = NULL,                 # 使用的 assay
    prepareCounts = "default",    # 计数聚合：TRUE/FALSE/"default"（< 60,000 细胞时自动执行）
    aggregFactor = 15000,         # 每 spot 目标计数
    clusterResolution = 0.8,      # Seurat 聚类分辨率
    pooledReference = TRUE,       # 跨样本池化参考
    scaleOnReferenceLabel = TRUE, # 基于参考缩放结果
    thresholdPercentile = 0.01,   # 分位数阈值（背景噪声控制）
    windowSize = 150,             # 基因组窗口大小
    windowStep = 10,              # 窗口步长
    topNGenes = 7000,             # 保留的高表达基因数
    getCNVPerChromosomeArm = TRUE,# 计算染色体臂级 CNV
    getCNVClusters = TRUE,        # 执行 CNV 聚类
    k_clusters = NULL,            # 指定聚类数（NULL 则自动 elbow 法）
    mergeCNV = TRUE,              # 合并高相关 CNV 簇
    mergeThreshold = 0.98,        # 合并阈值（相关性）
    doPlot = TRUE,                # 生成热图
    denoise = TRUE,               # 使用去噪数据
    savePath = ".",               # 保存路径
    outputType = "png",           # 输出格式："png" 或 "pdf"
    clustersVar = "cnv_clusters", # 聚类列名
    referencePalette = "default", # 参考注释配色
    clusters_palette = "default"  # 聚类配色
)
```

### `fastCNV_10XHD()` — Visium HD 分析

```r
fastCNV_10XHD(
    seuratObjHD,                  # Visium HD Seurat 对象或列表
    sampleName,                   # 样本名称
    referenceVar = NULL,          # 参考注释列名
    referenceLabel = NULL,        # 参考标签值
    assay = "Spatial.016um",      # 使用的 assay（默认 16µm）
    pooledReference = TRUE,
    scaleOnReferenceLabel = TRUE,
    thresholdPercentile = 0.01,
    windowSize = 150,
    windowStep = 10,
    topNGenes = 7000,
    getCNVPerChromosomeArm = TRUE,
    getCNVClusters = TRUE,
    k_clusters = NULL,
    h_clusters = NULL,
    mergeCNV = TRUE,
    mergeThreshold = 0.98,
    doPlot = TRUE,
    denoise = TRUE,
    raster_resize_mat = TRUE,     # 是否将矩阵调整为与光栅图像相同的维度
    savePath = ".",
    outputType = "png"
)
```

---

## 内部函数 API

| 函数 | 说明 |
|---|---|
| `prepareCountsForCNVAnalysis()` | 聚类并聚合计数为 metaspot（适用于低计数 Visium 样本） |
| `CNVAnalysis()` | 核心 CNV 计算，生成基因组分数 assay 和 `cnv_fraction` |
| `CNVCalling()` | 单样本 CNV 调用 |
| `CNVCallingList()` | 多样本 CNV 调用（池化参考） |
| `CNVPerChromosomeArm()` | 按染色体臂计算 CNV，存入 metadata |
| `CNVCluster()` | 基于 CNV 分数矩阵进行层次聚类 |
| `mergeCNVClusters()` | 合并高相关性 CNV 簇 |
| `plotCNVResults()` | 绘制 CNV 热图（scRNA-seq / Visium） |
| `plotCNVResultsHD()` | 绘制 Visium HD CNV 热图 |
| `CNVTree()` / `buildCNVTree()` | 构建 CNV 亚克隆进化树 |
| `plotCNVTree()` | 绘制亚克隆树 |
| `annotateCNVTree()` | 注释亚克隆树 |
| `getGenes()` | 获取基因元数据（默认 Ensembl v113） |

---

## 输出说明

运行 `fastCNV()` 后，Seurat 对象中新增：

### Metadata 列
- **`cnv_fraction`**：每个细胞/spot 的 CNV 分数（0 = 正常，高值 = 大量 CNV）
- **`cnv_clusters`**：基于 CNV 的亚克隆聚类标签
- **`cnv_per_chromosome_arm`**（如启用）：按染色体臂的 CNV 分数

### Assays
- **`rawGenomicScores`**：原始基因组窗口分数
- **`genomicScores`**：处理后的基因组分数（含去噪、缩放）

### 图形输出
- CNV 热图（PNG/PDF），保存至 `savePath`
- 可通过 Seurat 标准绘图函数可视化 `cnv_fraction` 和 `cnv_clusters`

```r
# 使用 Seurat 绘图
Seurat::DimPlot(seuratObj, group.by = "cnv_clusters")
FeaturePlot(seuratObj, features = "cnv_fraction")

# 空间可视化（Visium）
SpatialFeaturePlot(seuratObj, features = "cnv_fraction")
```

---

## 关键参数说明

| 参数 | 默认值 | 说明 |
|---|---|---|
| `prepareCounts` | `"default"` | 计数聚合；`"default"` 表示 < 60,000 细胞时自动执行 |
| `aggregFactor` | `15000` | 每 metaspot 目标计数；低于 1000 则不执行聚合 |
| `windowSize` | `150` | 基因组窗口大小（基因数） |
| `windowStep` | `10` | 窗口步长 |
| `topNGenes` | `7000` | 保留的高表达基因数 |
| `thresholdPercentile` | `0.01` | 分位数阈值；值越大背景噪声越多 |
| `mergeThreshold` | `0.98` | CNV 簇合并的相关性阈值 |
| `denoise` | `TRUE` | 热图使用去噪数据 |
| `scaleOnReferenceLabel` | `TRUE` | 基于参考缩放结果 |

---

## 可视化能力

### CNV 热图
使用 **ComplexHeatmap** 生成，可自定义：
- `referencePalette`：参考注释颜色
- `clusters_palette`：聚类颜色
- `splitPlotOnVar`：按 metadata 列分割热图

### 亚克隆树
基于 CNV 簇构建亚克隆进化树：
```r
tree <- CNVTree(seuratObj)
plotCNVTree(tree)
```

### CNV fraction 可视化
```r
# UMAP 上的 cnv_fraction
FeaturePlot(seuratObj, features = "cnv_fraction")

# 空间 cnv_fraction（Visium）
SpatialFeaturePlot(seuratObj, features = "cnv_fraction")

# 亚克隆聚类
DimPlot(seuratObj, group.by = "cnv_clusters")
```

---

## 故障排除

### 常见问题

1. **内存不足（Visium HD）**
   - 使用 16µm bin（约需 64 GB RAM）
   - 8µm bin 可能需要高达 200 GB RAM

2. **没有健康参考**
   - fastCNV 可以**无参考运行**，但**强烈建议使用健康参考**
   - 可从公共数据库下载相同器官、相同技术的健康样本作为参考

3. **低计数 Visium 样本**
   - `prepareCountsForCNVAnalysis()` 会聚合相邻 spot 直到达到阈值（通常 3-4 个 spot）
   - 调整 `aggregFactor` 控制目标计数

4. **强制包含特定基因/区域**
   - 使用 `genesToForce = c("FOXP3", "MUC16")`
   - 使用 `chrArmsToForce = c("8p", "3q")`
   - 使用 `regionToForce = c("chr", start, end)`

5. **热图渲染缓慢**
   - 设置 `raster_resize_mat = FALSE`（HD）作为后备方案

---

## 性能参考

| 数据类型 | 规模 | 运行时间 | 内存 |
|---|---|---|---|
| scRNA-seq | ~4,000 细胞 | ~1 分钟 | 中等 |
| Visium HD (16µm) | ~150,000 spots | ~40 分钟 | ~64 GB RAM |
| Visium HD (8µm) | ~600,000 spots | 更长 | 最高 ~200 GB RAM |

---

## 引用

```bibtex
@article{cabrejas2025fastcnv,
  title   = {fastCNV: Fast and accurate copy number variation prediction from High-Definition Spatial Transcriptomics and scRNA-Seq Data},
  author  = {Cabrejas, G. and Groeneveld, C. and others},
  journal = {bioRxiv},
  year    = {2025},
  doi     = {10.1101/2025.10.22.683855}
}
```

---

## 许可证

GPL-3 License

---

## 资源链接

- **源码仓库**：[github.com/must-bioinfo/fastCNV](https://github.com/must-bioinfo/fastCNV)
- **官方文档**：[must-bioinfo.github.io/fastCNV](https://must-bioinfo.github.io/fastCNV)
- **教程**：[must-bioinfo.github.io/fastCNV/articles/index.html](https://must-bioinfo.github.io/fastCNV/articles/index.html)
- **示例数据包**：[github.com/must-bioinfo/fastCNVdata](https://github.com/must-bioinfo/fastCNVdata)
- **论文**：[bioRxiv 2025.10.22.683855](https://doi.org/10.1101/2025.10.22.683855)

---

## 完整可运行脚本

以下脚本均为最小可运行示例，复制到 `.R` 文件中即可执行（需要先安装 `fastCNV` 及示例数据）。

### 脚本 1 — 单样本 scRNA-seq CNV 分析

```r
#!/usr/bin/env Rscript
# 01_single_sample_scrnaseq.R
# fastCNV 单样本 scRNA-seq CNV 分析（最小可运行示例）。
#
# 该脚本使用 fastCNV::fastCNV() 一站式函数自动执行：
#   1. prepareCountsForCNVAnalysis：聚类并聚合为 metaspot
#   2. CNVAnalysis：计算 CNV 基因组分数
#   3. CNVPerChromosomeArm：按染色体臂计算 CNV
#   4. CNVCluster：层次聚类生成 cnv_clusters
#   5. plotCNVResults：生成 CNV 热图

library(fastCNV)
library(Seurat)

# 运行 fastCNV 一站式分析
# 输入：Seurat 对象（scColon1 为内置示例）
#   - metadata 中需有 referenceVar 列，标识正常/健康细胞
#   - referenceLabel 为该列中作为参考的标签值向量
seuratObj <- fastCNV(
    seuratObj    = scColon1,
    sampleName   = "scColon1",
    referenceVar = "annot",
    referenceLabel = c("TNKILC", "Myeloid", "B", "Mast", "Plasma"),
    printPlot    = TRUE
)

# 查看结果
cat("=== Tumor/Normal 分布（按 cnv_fraction）===\n")
print(summary(seuratObj$cnv_fraction))

cat("\n=== CNV 亚克隆聚类分布 ===\n")
print(table(seuratObj$cnv_clusters))

# 可视化（UMAP 上的 cnv_fraction 与 cnv_clusters）
if (!exists("DimPlot")) DimPlot <- Seurat::DimPlot
if (!exists("FeaturePlot")) FeaturePlot <- Seurat::FeaturePlot

p1 <- FeaturePlot(seuratObj, features = "cnv_fraction") +
      ggplot2::ggtitle("cnv_fraction")
p2 <- DimPlot(seuratObj, group.by = "cnv_clusters") +
      ggplot2::ggtitle("cnv_clusters")
print(p1)
print(p2)

# 保存分析结果
saveRDS(seuratObj, file = "seuratObj_fastCNV.rds")
cat("\n[OK] Seurat 对象已保存 -> seuratObj_fastCNV.rds\n")
```

### 脚本 2 — 多样本池化参考分析

```r
#!/usr/bin/env Rscript
# 02_multi_sample_pooled.R
# fastCNV 多样本同时分析，自动构建跨样本池化参考。
#
# 当提供多个样本时，fastCNV 会跨所有样本构建池化参考，
# 因此一个样本中的健康组织可用作所有样本的参考。

library(fastCNV)
library(Seurat)

# 假设已有 3 个 Seurat 对象
# 若无现成数据可使用 fastCNVdata 包中的示例：
#   remotes::install_github("must-bioinfo/fastCNVdata")

# 方式一：直接传入向量形式的样本列表
samples <- fastCNV(
    seuratObj    = c(sample1, sample2, sample3),
    sampleName   = c("sample1", "sample2", "sample3"),
    referenceVar = "Annotations",
    referenceLabel = c("Healthy1", "Healthy2", "Healthy3")
)

# 方式二：使用 Seurat 合并后再分析
# merged <- merge(sample1, y = c(sample2, sample3),
#                 add.cell.ids = c("S1","S2","S3"), project = "merged")
# samples <- fastCNV(
#     seuratObj      = merged,
#     sampleName     = "merged",
#     referenceVar   = "Annotations",
#     referenceLabel = c("Healthy1", "Healthy2", "Healthy3"),
#     pooledReference = TRUE
# )

cat("=== 多样本池化分析完成 ===\n")
cat(sprintf("样本数: %d\n", length(unique(samples$orig.ident))))
cat("\n各样本 Tumor/Normal 分布：\n")
print(table(samples$orig.ident, samples$cnv_clusters))

# 跨样本可视化（Split By Sample）
p <- Seurat::DimPlot(
    samples,
    group.by = "cnv_clusters",
    split.by = "orig.ident",
    ncol = 3
) + ggplot2::ggtitle("CNV clusters by sample")
print(p)

# 保存
saveRDS(samples, file = "multi_sample_fastCNV.rds")
cat("\n[OK] 合并结果已保存 -> multi_sample_fastCNV.rds\n")
```

### 脚本 3 — Visium HD 空间转录组 CNV 分析

```r
#!/usr/bin/env Rscript
# 03_visium_hd_analysis.R
# fastCNV Visium HD 空间转录组 CNV 分析。
#
# 使用 fastCNV::fastCNV_10XHD() 一站式函数，
# 默认基于 Spatial.016um assay（约 64 GB RAM）；
# 8µm bin 可能需要高达 200 GB RAM。

library(fastCNV)
library(Seurat)

# 加载 Visium HD Seurat 对象
# （通过 Seurat::Load10X_Spatial_VHD 加载）
# visiumHD_obj <- Load10X_Spatial_VHD(
#     data.dir = "path/to/visium_hd_outs",
#     bin.size = c("008um", "016um")
# )

# 必备预处理：NormalizeData + FindSpatiallyVariableFeatures
# （fastCNV 内部会调用，此处仅展示完整流程起点）
visiumHD_obj <- NormalizeData(visiumHD_obj, verbose = FALSE)
visiumHD_obj <- FindSpatiallyVariableFeatures(
    visiumHD_obj,
    assay = "Spatial.016um",
    verbose = FALSE
)

# 运行 fastCNV_10XHD
seuratHD <- fastCNV_10XHD(
    seuratObjHD    = visiumHD_obj,
    sampleName     = "HD_sample",
    referenceVar   = "annotation",
    referenceLabel = "Normal",
    assay          = "Spatial.016um",    # 默认 16µm bin
    pooledReference = TRUE,
    raster_resize_mat = TRUE             # 将矩阵调整为与光栅图像同维度
)

cat("=== Visium HD CNV 分析完成 ===\n")
cat("\nCNV fraction 分布：\n")
print(summary(seuratHD$cnv_fraction))

cat("\n亚克隆聚类分布：\n")
print(table(seuratHD$cnv_clusters))

# 空间可视化
p1 <- Seurat::SpatialFeaturePlot(
    seuratHD, features = "cnv_fraction"
) + ggplot2::ggtitle("cnv_fraction (spatial)")

p2 <- Seurat::SpatialDimPlot(
    seuratHD, group.by = "cnv_clusters"
) + ggplot2::ggtitle("cnv_clusters (spatial)")

print(p1)
print(p2)

# 保存
saveRDS(seuratHD, file = "visiumHD_fastCNV.rds")
cat("\n[OK] Visium HD 结果已保存 -> visiumHD_fastCNV.rds\n")
```

### 脚本 4 — CNV 亚克隆树构建与可视化

```r
#!/usr/bin/env Rscript
# 04_cnv_tree_visualization.R
# fastCNV 亚克隆树构建与可视化。
#
# 基于 CNV 分数矩阵构建亚克隆进化树，
# 用于揭示肿瘤内异质性与克隆演化关系。

library(fastCNV)
library(Seurat)

# 加载 fastCNV 已完成分析的 Seurat 对象
# （例如由 01/02/03 脚本输出）
seuratObj <- readRDS("seuratObj_fastCNV.rds")

# 1. 构建亚克隆进化树
cat("[Step 1] 构建 CNV 亚克隆树...\n")
tree <- CNVTree(seuratObj)

# 2. 绘制亚克隆树
cat("[Step 2] 绘制亚克隆树...\n")
plotCNVTree(tree)

# 3. 注释亚克隆树（添加细胞类型/分组信息）
cat("[Step 3] 注释亚克隆树...\n")
# annotateCNVTree(tree, ...)

# 4. UMAP 上叠加 cnv_fraction 着色
p_umap <- Seurat::FeaturePlot(
    seuratObj, features = "cnv_fraction",
    cols = c("lightgrey", "firebrick"),
    order = TRUE
) + ggplot2::ggtitle("cnv_fraction on UMAP")
print(p_umap)

# 5. UMAP 上叠加亚克隆聚类
p_cluster <- Seurat::DimPlot(
    seuratObj, group.by = "cnv_clusters", label = TRUE
) + ggplot2::ggtitle("CNV subclones")
print(p_cluster)

# 6. 导出亚克隆统计
subclone_stats <- table(seuratObj$cnv_clusters)
write.csv(
    as.data.frame(subclone_stats),
    file = "cnv_subclone_stats.csv",
    row.names = FALSE
)

cat("\n=== 亚克隆统计 ===\n")
print(subclone_stats)

cat("\n[OK] 亚克隆树分析与可视化完成 -> cnv_subclone_stats.csv\n")
```
