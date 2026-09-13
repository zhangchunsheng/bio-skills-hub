---
name: bio-single-cell-annotation-zh
description: 使用 CellTypist、SingleR、Azimuth 和 scPred 等基于参考数据集的自动化方法完成单细胞细胞类型注释，实现一致、可复现的细胞标签分配。当需要自动注释细胞类型时使用。
tool_type: mixed
primary_tool: CellTypist
---

## 版本兼容性

参考示例基于 pandas 2.2+、scanpy 1.10+、scikit-learn 1.4+ 编写。

使用前请确认已安装版本匹配。若版本不同：
- Python：`pip show <package>`，再用 `help(module.function)` 确认函数签名
- R：`packageVersion('<pkg>')`，再用 `?function_name` 确认参数

若出现 `ImportError`、`AttributeError` 或 `TypeError`，请先检查当前环境的实际 API 并调整代码，不要盲目重试。

# 自动化细胞类型注释

## CellTypist（Python）

**目标：** 使用预训练或自定义 CellTypist 模型自动注释细胞类型。

**方法：** 加载参考模型，通过多数投票实现簇级别的一致性预测，并将预测结果写入 AnnData。

**"帮我自动标注细胞类型"** → 将训练好的分类器应用于查询数据，基于与参考图谱的转录组相似性分配细胞类型身份。

**前提条件：** CellTypist 要求 `.X` 为 log1p-归一化数据（target_sum=1e4）。若 adata 已经过 `sc.pp.scale()` 处理，请从原始计数重新归一化。

```python
import celltypist
import scanpy as sc

adata = sc.read_h5ad('adata_processed.h5ad')

# 确认数据为 log1p-归一化（若不确定，从原始计数重新处理）
# sc.pp.normalize_total(adata, target_sum=1e4)
# sc.pp.log1p(adata)

# 列出可用模型
celltypist.models.models_description()

# 下载模型
celltypist.models.download_models(model='Immune_All_Low.pkl')

# 加载模型
model = celltypist.models.Model.load(model='Immune_All_Low.pkl')

# 检查基因重叠率（低于 30% 时预测质量显著下降）
overlap = adata.var_names.intersection(model.features)
print(f"基因重叠率：{len(overlap)} / {len(model.features)} ({len(overlap)/len(model.features)*100:.1f}%)")

# majority_voting=True 需要 neighbors graph（内部执行过聚类）
# 若尚未运行：sc.pp.neighbors(adata)
# 若已有 leiden 聚类，显式传入可避免重复计算
predictions = celltypist.annotate(adata, model=model, majority_voting=True,
                                   over_clustering='leiden')  # 已有聚类时传入

# 将预测结果写入 adata
adata = predictions.to_adata()

# 获取预测结果
adata.obs['cell_type_celltypist'] = adata.obs['majority_voting']
adata.obs['cell_type_confidence'] = adata.obs['conf_score']

# 可视化
sc.pl.umap(adata, color=['cell_type_celltypist', 'conf_score'])
```

## CellTypist 自定义模型

**目标：** 在参考数据集上训练自定义 CellTypist 模型，用于领域特异性注释。

**方法：** 对带标签的参考数据训练逻辑回归分类器并进行特征筛选，再应用于查询数据。

```python
# 训练自定义模型
# use_SGD=True 适合 >10 万细胞；小数据集去掉此参数以获得更高精度
new_model = celltypist.train(adata_reference, labels='cell_type', n_jobs=-1,
                              feature_selection=True, use_SGD=True)

# 保存模型
new_model.write('custom_model.pkl')

# 使用自定义模型
predictions = celltypist.annotate(adata_query, model='custom_model.pkl')
```

## SingleR（R）

**目标：** 通过将表达谱与精心策划的参考数据集进行相关性分析来注释细胞类型。

**方法：** 使用 SingleR 基于相关性的分配方法将每个细胞的表达与参考转录组进行比较，并对低置信度的标注进行剪枝处理。

**前提条件：** `as.SingleCellExperiment()` 默认使用 Seurat `RNA@data`（log-normalized），符合 SingleR 要求。

```r
library(SingleR)
library(celldex)
library(Seurat)
library(SingleCellExperiment)
library(BiocParallel)

seurat_obj <- readRDS('seurat_processed.rds')
sce <- as.SingleCellExperiment(seurat_obj)  # 使用 RNA@data（log-normalized）

# 加载参考数据集（多个可选）
ref <- celldex::HumanPrimaryCellAtlasData()
# 其他选项：
# ref <- celldex::BlueprintEncodeData()
# ref <- celldex::MonacoImmuneData()
# ref <- celldex::ImmGenData()  # 小鼠数据

# 运行 SingleR
# de.method 默认为 'classic'（原始论文方法，速度快）；
# 'wilcox' 更稳健但慢得多，适合对批量参考集有顾虑时使用
pred <- SingleR(test = sce, ref = ref, labels = ref$label.main,
                de.method = 'classic',
                BPPARAM = MulticoreParam(4))  # 多核加速

# 写入 Seurat 对象
seurat_obj$SingleR_labels <- pred$labels
seurat_obj$SingleR_pruned <- pred$pruned.labels  # NA 表示低质量标注

# 评估注释质量
plotScoreHeatmap(pred)
plotDeltaDistribution(pred)
```

## SingleR 细粒度标签

```r
# 使用精细粒度标签
pred_fine <- SingleR(test = sce, ref = ref, labels = ref$label.fine)

# 合并多个参考数据集（SingleR 2.x 语法）
ref1 <- celldex::BlueprintEncodeData()
ref2 <- celldex::MonacoImmuneData()
pred_combined <- SingleR(test = sce, ref = list(BP = ref1, Monaco = ref2),
                          labels = list(ref1$label.main, ref2$label.main))
```

## Azimuth（R/Seurat）

**目标：** 使用 Seurat 的 Azimuth 参考映射框架注释细胞类型。

**方法：** 将查询细胞映射到预构建的 Azimuth 参考图谱上，迁移细胞类型标签及置信度分数。

**前提条件：** Azimuth 需要 `RNA` assay 的 `counts` slot 含原始计数。

```r
library(Seurat)
library(Azimuth)

seurat_obj <- readRDS('seurat_processed.rds')

# 使用 PBMC 参考运行 Azimuth
seurat_obj <- RunAzimuth(seurat_obj, reference = 'pbmcref')

# 可用参考：pbmcref、bonemarrowref、lungref 等
# 不同参考的层级深度不同（l1/l2/l3），根据参考文档确认列名

# 获取预测结果
seurat_obj$azimuth_labels <- seurat_obj$predicted.celltype.l2
seurat_obj$azimuth_score <- seurat_obj$predicted.celltype.l2.score

# 可视化
DimPlot(seurat_obj, group.by = 'azimuth_labels', label = TRUE) + NoLegend()
FeaturePlot(seurat_obj, features = 'predicted.celltype.l2.score')
```

## scPred（R）

**目标：** 使用 scPred 训练并应用监督分类器进行细胞类型预测。

**方法：** 从带标签的参考数据中提取信息性 PCA 特征，训练 SVM/RF 分类器，再对查询数据进行细胞类型预测。

**前提条件：** `getFeatureSpace()` 需要参考数据已完成 PCA。

```r
library(scPred)
library(Seurat)

# 在参考数据上训练
reference <- readRDS('reference_seurat.rds')

# getFeatureSpace() 依赖 PCA，必须提前运行
reference <- FindVariableFeatures(reference)
reference <- ScaleData(reference)
reference <- RunPCA(reference)

reference <- getFeatureSpace(reference, 'cell_type')
reference <- trainModel(reference)

# 获取训练概率
get_probabilities(reference)
get_scpred(reference)

# 绘制模型性能
plot_probabilities(reference)

# 对查询数据进行预测
query <- readRDS('query_seurat.rds')
query <- scPredict(query, reference)

# 查看结果
query$scpred_prediction
query$scpred_max
```

## 注释置信度过滤

```python
# CellTypist：过滤低置信度细胞
# conf_score 阈值参考：CellTypist 作者建议以 majority_voting 输出为主，
# 辅以 conf_score 识别极低置信度（<0.3）的需人工核查细胞
high_conf = adata[adata.obs['conf_score'] > 0.5].copy()

# 标记不确定细胞
adata.obs['annotation_uncertain'] = adata.obs['conf_score'] < 0.3
```

```r
# SingleR：使用剪枝标签（pruned.labels 中 NA 为低质量标注）
seurat_obj$final_labels <- ifelse(is.na(pred$pruned.labels), 'Unknown', pred$pruned.labels)

# Azimuth：按分数过滤
# 阈值因参考集而异，建议先查看分数分布后决定截断点
hist(seurat_obj$predicted.celltype.l2.score, breaks = 50, main = 'Azimuth score 分布')
seurat_obj$high_conf_labels <- ifelse(seurat_obj$predicted.celltype.l2.score > 0.5,
                                       seurat_obj$predicted.celltype.l2, 'Low_confidence')
```

## 共识注释

**目标：** 将多种注释工具的预测结果整合为每个细胞的单一共识标签。

**方法：** 汇总 SingleR、Azimuth 和 CellTypist 的标签，通过多数投票确定最终标签，并标记方法间存在分歧的模糊细胞。

**重要：** 三个工具使用不同的命名规范（如 `"CD4+_T_cells"` vs `"CD4 T"` vs `"CD4+ T cells"`），必须先统一映射到共同词汇表，否则多数投票几乎永远返回 `'Ambiguous'`。

```r
# 第一步：建立标签映射表（根据实际输出调整）
label_map <- c(
    # CellTypist → 标准名
    'CD4+_T_cells'         = 'CD4 T',
    'CD8+_T_cells'         = 'CD8 T',
    'B_cells'              = 'B cell',
    'NK_cells'             = 'NK',
    'Classical_monocytes'  = 'Monocyte',
    # SingleR → 标准名
    'T_cells'              = 'CD4 T',   # 根据实际粒度调整
    'Monocyte'             = 'Monocyte',
    # Azimuth → 标准名（pbmcref l2 示例）
    'CD4 T'                = 'CD4 T',
    'CD8 TEM'              = 'CD8 T',
    'NK'                   = 'NK',
    'CD14 Mono'            = 'Monocyte'
)

harmonize <- function(labels, map) {
    mapped <- map[as.character(labels)]
    ifelse(is.na(mapped), as.character(labels), mapped)
}

# 第二步：统一标签后再做共识投票
annotations <- data.frame(
    SingleR   = harmonize(seurat_obj$SingleR_pruned,   label_map),
    Azimuth   = harmonize(seurat_obj$azimuth_labels,   label_map),
    CellTypist = harmonize(seurat_obj$cell_type_celltypist, label_map)
)

# 多数投票（处理 NA 和 Unknown）
get_consensus <- function(x) {
    x <- x[!is.na(x) & x != 'Unknown' & x != 'Low_confidence']
    if (length(x) == 0) return('Ambiguous')
    tbl <- table(x)
    if (max(tbl) >= 2) names(which.max(tbl)) else 'Ambiguous'
}
seurat_obj$consensus_label <- apply(annotations, 1, get_consensus)
```

## 注释方法比较

**目标：** 定量评估不同注释方法之间的一致性。

**方法：** 计算标签集之间的调整兰德指数（ARI）和归一化互信息（NMI），并构建混淆矩阵。

```python
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

# 使用正确的列名（与 CellTypist 部分一致）
ari = adjusted_rand_score(adata.obs['manual_annotation'], adata.obs['cell_type_celltypist'])
nmi = normalized_mutual_info_score(adata.obs['manual_annotation'], adata.obs['cell_type_celltypist'])

# 混淆矩阵
pd.crosstab(adata.obs['manual_annotation'], adata.obs['cell_type_celltypist'])
```

## 基于标志基因的验证

```r
# 使用已知标志基因验证预测结果
canonical_markers <- list(
    T_cell   = c('CD3D', 'CD3E', 'CD4', 'CD8A'),
    B_cell   = c('CD19', 'MS4A1', 'CD79A'),
    Monocyte = c('CD14', 'LYZ', 'S100A8'),
    NK       = c('NKG7', 'GNLY', 'KLRF1', 'KLRD1')
    # NCAM1（CD56）不具 NK 特异性，在 CD56+ T 细胞和 NKT 细胞上也有表达，不建议用于验证
)

# group.by 使用实际存在的注释列
DotPlot(seurat_obj, features = unlist(canonical_markers), group.by = 'consensus_label') +
    RotatedAxis()
```

## 相关 Skills

- single-cell/clustering — 基于标志基因的手动注释
- single-cell/cell-communication — 利用已注释细胞类型进行细胞通讯分析
- single-cell/trajectory-inference — 在已注释数据上进行轨迹推断
