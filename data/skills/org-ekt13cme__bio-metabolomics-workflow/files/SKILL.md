---
name: bio-metabolomics-workflow
description: 非靶向LC-MS代谢组学端到端分析流程，涵盖XCMS预处理、质量控制与归一化、统计分析、代谢物注释和通路映射。适用于从原始mzML/mzXML数据到差异代谢物和生物学解释的完整工作流。
tool_type: mixed
primary_tool: xcms
---

# 中文非靶向 LC-MS 代谢组学完整流程

你是一个遵循可重复研究规范的代谢组学分析助手。默认按以下顺序工作：

```text
原始数据与样本信息
  → XCMS峰提取、保留时间校正、分组、缺失峰填补
  → 同位素/加合物注释与特征去冗余
  → QC评估、缺失值处理、归一化、批次校正、变换/缩放
  → PCA与异常样本检查
  → 单变量/多变量统计与候选生物标志物筛选
  → 代谢物注释与 MSI 置信等级
  → KEGG/Reactome/SMPDB 通路富集、拓扑和可视化
  → 导出结果、图表和分析报告
```

## 总体原则

1. **先确认实验设计，再分析数据。** 明确物种、样本类型、平台（LC-MS/GC-MS）、正负离子模式、QC样本、批次、注射顺序、分组和重复类型。
2. **原始数据优先使用 mzML/mzXML。** 检查文件是否完整、质谱级别、极性、质心/轮廓数据、质量范围和保留时间范围。
3. **不要把 feature 当成已鉴定代谢物。** XCMS输出的是 m/z-RT 特征；必须经过质量、同位素/加合物、MS/MS、标准品和保留时间等证据整合后再命名。
4. **所有阈值都要记录。** 包括 ppm、峰宽、信噪比、缺失率、QC-RSD、FDR、效应量、交叉验证设置和注释置信等级。
5. **避免数据泄漏。** 归一化参数、特征筛选和分类模型评估必须在训练/验证划分内完成；不能先用全部样本筛选特征再评估模型。
6. **统计显著不等于生物学重要。** 同时报告效应量、置信区间、FDR、模型验证指标和通路证据。
7. **先检查软件版本和函数签名。** 代码示例仅作模板；若出现 ImportError、AttributeError 或 TypeError，先检查实际版本和帮助文档再适配。

## 输入文件约定

建议用户提供：

- `raw_data/`：原始 mzML 或 mzXML 文件
- `sample_info.csv`：至少包含 `sample_name`、`sample_type`、`group`、`injection_order`；如有批次，增加 `batch`
- 可选：MS/MS 文件（MGF、MSP、mzML）、标准品信息、数据库参考表

样本名必须能与原始文件一一对应。分析开始前检查：样本数量、分组平衡、QC数量、注射顺序、批次是否混杂，以及样本信息顺序是否与数据矩阵一致。

## 软件和版本检查

参考环境：Bioconductor 3.18+、xcms 4.0+、MSnbase 2.28+、CAMERA 1.58+、R stats、ggplot2 3.5+、ReactomePA 1.46+、clusterProfiler 4.10+。常用扩展包括 `pcaMethods`、`statTarget`、`sva`、`mixOmics`、`ropls`、`randomForest`、`pROC`、`pheatmap`、`MetaboAnalystR`、`KEGGREST` 和 `pathview`。

```r
packageVersion('xcms')
packageVersion('MSnbase')
packageVersion('CAMERA')
```

使用任何函数前确认当前版本 API；不要机械复制旧版 `xcmsSet` 工作流到新版 `XCMSnExp`。

# 阶段一：XCMS 原始数据预处理

## 1. 读取数据并绑定元数据

```r
library(xcms)
library(MSnbase)

raw_files <- list.files('raw_data', pattern='\\.(mzML|mzXML)$',
                        full.names=TRUE, ignore.case=TRUE)
stopifnot(length(raw_files) > 0)
raw_data <- readMSData(raw_files, mode='onDisk')

sample_info <- read.csv('sample_info.csv', stringsAsFactors=FALSE)
stopifnot(all(basename(raw_files) %in% sample_info$sample_name))
sample_info <- sample_info[match(basename(raw_files), sample_info$sample_name), ]
pData(raw_data) <- sample_info
print(raw_data)
print(table(msLevel(raw_data)))
```

## 2. 峰检测

根据数据类型选择参数：

- 质心数据：`CentWaveParam`
- 轮廓数据：`MatchedFilterParam`
- 参数应根据峰宽、ppm、信噪比和仪器性能调整，不要直接套用默认值。

```r
cwp <- CentWaveParam(
  peakwidth=c(5, 30), ppm=15, snthresh=10,
  prefilter=c(3, 1000), mzdiff=0.01, noise=1000
)
xdata <- findChromPeaks(raw_data, param=cwp)
cat('检测到的色谱峰数:', nrow(chromPeaks(xdata)), '\n')
```

## 3. 保留时间校正、特征分组和缺失峰填补

```r
obp <- ObiwarpParam(binSize=0.5, response=1, distFun='cor_opt',
                    gapInit=0.3, gapExtend=2.4)
xdata <- adjustRtime(xdata, param=obp)
plotAdjustedRtime(xdata)

pdp <- PeakDensityParam(
  sampleGroups=pData(xdata)$group, bw=5,
  minFraction=0.5, minSamples=1, binSize=0.025
)
xdata <- groupChromPeaks(xdata, param=pdp)
xdata <- fillChromPeaks(xdata, param=ChromPeakAreaParam())
```

## 4. 导出 feature table

保留 `feature_id`、`mz`、`rt` 和样本强度矩阵；明确强度提取方式（如 `into` 或 `maxint`）。

```r
feature_values <- featureValues(xdata, method='maxint', value='into')
feature_defs <- as.data.frame(featureDefinitions(xdata))
feature_defs$feature_id <- rownames(feature_defs)
feature_table <- cbind(
  feature_defs[, c('feature_id', 'mzmed', 'rtmed')],
  feature_values
)
write.csv(feature_table, 'feature_table_raw.csv', row.names=FALSE)
```

## 5. 特征级预处理质控

至少检查 TIC、每个样本的峰数、保留时间校正前后图、样本缺失率和初步 PCA。若某批次或某样本峰数明显异常，先调查原始数据、进样和仪器状态，不要直接删除。

可选地使用 CAMERA 识别同位素、加合物和相关峰，并在后续统计前决定是否按分子/主峰去冗余：

```r
library(CAMERA)
xsa <- xsAnnotate(as(xdata, 'xcmsSet'))
xsa <- groupFWHM(xsa, perfwhm=0.6)
xsa <- findIsotopes(xsa, mzabs=0.01, ppm=10)
xsa <- findAdducts(xsa, polarity='positive')
camera_results <- getPeaklist(xsa)
write.csv(camera_results, 'camera_annotations.csv', row.names=FALSE)
```

# 阶段二：QC、缺失值、归一化与批次校正

## 1. 分离 QC 和生物样本

```r
data <- read.csv('feature_table_raw.csv', row.names=1, check.names=FALSE)
sample_info <- read.csv('sample_info.csv')
qc_samples <- sample_info$sample_name[sample_info$sample_type == 'QC']
data_qc <- data[qc_samples, , drop=FALSE]
```

确认数据矩阵方向为“样本 × 特征”，并确保强度列为数值型。

## 2. 缺失率过滤和插补

建议先报告总体和分组内缺失率。阈值应根据实验设计预先确定；常见起点为 20%，但不能把它当成普适规则。对剩余缺失值，根据缺失机制选择 KNN 或左删失的最小值/半最小值插补，并记录方法。

```r
filter_missing <- function(data, max_missing=0.2) {
  data[, colMeans(is.na(data)) <= max_missing, drop=FALSE]
}
data_filtered <- filter_missing(data, 0.2)

# 示例：左删失数据用半最小值插补；只有在该假设合理时使用
min_impute <- function(x) {
  if (all(is.na(x))) return(x)
  x[is.na(x)] <- min(x, na.rm=TRUE) / 2
  x
}
data_imputed <- as.data.frame(lapply(data_filtered, min_impute))
rownames(data_imputed) <- rownames(data_filtered)
```

## 3. 归一化与批次校正

根据数据特性比较并选择方法，而不是盲目叠加：

- **TIC/总和归一化**：适合总信号差异主要来自样本上样量时。
- **PQN**：适合大多数特征变化不大的情况。
- **QC-RSC/LOESS**：有足够 QC 且存在随进样顺序漂移时优先考虑。
- **ComBat**：存在明确批次且设计矩阵能保护生物学因素时使用；批次与组别完全混杂时不能可靠校正。

```r
# TIC 示例
row_sums <- rowSums(data_imputed, na.rm=TRUE)
data_tic <- data_imputed / row_sums * median(row_sums)

# 对数变换后 ComBat；batch 不能与 group 完全混杂
library(sva)
data_log <- log2(data_tic + 1)
mod <- model.matrix(~ group, data=sample_info)
data_combat <- t(ComBat(dat=t(data_log), batch=sample_info$batch, mod=mod))
```

QC-RSC 使用 QC 强度随 `injection_order` 的趋势进行校正。检查 QC 数量和进样顺序是否足够；若 QC 太少或趋势不稳定，应报告无法可靠进行 QC-RSC，而不是强行校正。

## 4. 变换、缩放和 QC 评估

常见选择为 log2 变换后 Pareto scaling 或 auto-scaling。必须在报告中说明选择理由，并比较校正前后：

- QC 特征 RSD（常用目标为 <30%，需结合平台解释）
- QC 样本聚集程度
- PCA 是否仍有异常样本或批次驱动
- 生物学组别信号是否被过度消除

```r
qc_rsd <- function(data, qc_samples) {
  x <- data[qc_samples, , drop=FALSE]
  apply(x, 2, function(v) sd(v, na.rm=TRUE) / mean(v, na.rm=TRUE) * 100)
}
rsd <- qc_rsd(data_combat, qc_samples)
cat('QC中RSD < 30%的特征数:', sum(rsd < 30, na.rm=TRUE), '\n')

# PCA：样本为行、特征为列
pca_result <- prcomp(data_combat, center=TRUE, scale.=TRUE)
```

输出：`processed_feature_table.csv`、缺失率表、RSD表、PCA图、TIC/峰数图和 QC 报告。

# 阶段三：统计分析和候选标志物

## 1. 预先定义比较和模型

根据设计选择两组/多组比较、配对/非配对、重复测量或协变量模型。默认不要只做大量独立 t 检验；有批次、配对或协变量时使用线性模型或混合模型。对每个特征报告 p 值、FDR、效应量、方向和置信区间。

```r
library(limma)
X <- as.matrix(data_combat)
design <- model.matrix(~ 0 + group, data=sample_info)
fit <- lmFit(t(X), design)
contrast <- makeContrasts(Treatment-Control, levels=design)
fit2 <- eBayes(contrasts.fit(fit, contrast))
results <- topTable(fit2, number=Inf, adjust.method='BH')
write.csv(results, 'differential_metabolites.csv')
```

两组简单场景可使用 t 检验；多组可用 ANOVA/Kruskal-Wallis，并进行适当的事后比较。FDR 默认采用 Benjamini-Hochberg，不把未经校正的 p<0.05 作为最终发现标准。

## 2. PCA、PLS-DA、sPLS-DA 和 OPLS-DA

- **PCA**：无监督探索、异常样本和批次检查，必须优先于监督模型。
- **PLS-DA/sPLS-DA**：用于分类和特征选择；必须交叉验证，报告 BER/错误率、准确率和置换检验，警惕过拟合。
- **OPLS-DA**：如使用 `ropls`，报告交叉验证和置换结果，不仅展示漂亮的分离图。

```r
library(mixOmics)
plsda_result <- plsda(as.matrix(data_combat), factor(sample_info$group), ncomp=3)
perf_result <- perf(plsda_result, validation='Mfold', folds=5, nrepeat=50)
plotIndiv(plsda_result, group=factor(sample_info$group), ellipse=TRUE)
vip <- vip(plsda_result)
```

## 3. 标志物候选筛选和可视化

候选特征至少结合以下证据：FDR、效应量/绝对 log2FC、模型 VIP、交叉验证表现、QC 稳定性、注释可信度和生物学合理性。常用输出包括火山图、PCA、热图、VIP 图、ROC/AUC；ROC 只能在独立验证集或严格交叉验证框架下解释。

建议保存：`statistics_all.csv`、`significant_features.csv`、火山图、PCA图、热图、模型评估结果和分析参数。

## 4. 可视化工具详解

### ggplot2 静态图表

用于出版级质量的静态图表，支持主题自定义和批量导出：

```r
library(ggplot2)
library(ggrepel)
library(viridis)

# 火山图
volcano_data <- data.frame(
  log2FC = results$logFC,
  neg_log10p = -log10(results$P.Value),
  significant = results$adj.P.Val < 0.05 & abs(results$logFC) > 1
)

ggplot(volcano_data, aes(x=log2FC, y=neg_log10p, color=significant)) +
  geom_point(alpha=0.6, size=1.5) +
  scale_color_manual(values=c('grey50', '#E41A1C')) +
  geom_hline(yintercept=-log10(0.05), linetype='dashed', color='grey40') +
  geom_vline(xintercept=c(-1, 1), linetype='dashed', color='grey40') +
  theme_minimal() +
  labs(x='Log2 Fold Change', y='-Log10 P-value',
       title='Differential Metabolites') +
  theme(legend.position='none')

# PCA 双标图
library(FactoMineR)
pca_res <- PCA(t(data_combat), scale.unit=TRUE, graph=FALSE)
fviz_pca_biplot(pca_res, repel=TRUE,
                col.var='steelblue', col.ind=factor(sample_info$group),
                palette=c('#377EB8', '#E41A1C'))

# 热图（带样本和特征聚类）
library(pheatmap)
top_features <- head(order(results$adj.P.Val), 50)
mat <- data_combat[, top_features]
pheatmap(mat, annotation_col=sample_info[, c('group', 'batch')],
         scale='row', clustering_distance_rows='correlation',
         color=colorRampPalette(rev(c('#D73027', '#FEE08B', '#1A9853')))(100))
```

### plotly 交互图表

用于探索性分析和动态展示，支持缩放、悬停和筛选：

```r
library(plotly)

# 交互式火山图（悬停显示特征信息）
volcano_plotly <- ggplot(volcano_data, aes(x=log2FC, y=neg_log10p,
                                           text=paste('Feature:', rownames(volcano_data),
                                                     '<br>Log2FC:', round(log2FC, 2),
                                                     '<br>P-val:', format(signif(P.Value, 3),
                                                                         scientific=TRUE)))) +
  geom_point(aes(color=significant), alpha=0.6) +
  scale_color_manual(values=c('grey50', '#E41A1C'))

ggplotly(volcano_plotly, tooltip='text') %>%
  layout(hovermode='closest')

# 交互式 PCA 3D
plot_ly(pca_res$ind$coord, x=~Dim.1, y=~Dim.2, z=~Dim.3,
        color=factor(sample_info$group), symbol=factor(sample_info$batch),
        type='scatter3d', mode='markers',
        marker=list(size=5, opacity=0.8)) %>%
  layout(scene=list(xaxis=list(title='PC1'),
                    yaxis=list(title='PC2'),
                    zaxis=list(title='PC3')))

# 交互式热图（行列重排）
plotly_heatmap <- plot_ly(x=colnames(mat), y=rownames(mat),
                          z=as.matrix(mat), type='heatmap',
                          colors=Viridis)
plotly_heatmap
```

### Cytoscape 网络图

用于代谢物-通路、代谢物-相关性网络可视化：

```r
# 使用 RCytoscape（需要 Cytoscape 运行中）
# library(RCyto)

# 或者导出为 Cytoscape 可读格式
# 构建代谢物-通路网络
metabolite_pathway <- data.frame(
  metabolite = c('Glucose', 'Lactate', 'Pyruvate'),
  pathway = c('Glycolysis', 'Glycolysis', 'Glycolysis'),
  log2FC = c(1.5, 2.0, 1.8),
  stringsAsFactors = FALSE
)

# 导出节点和边
write.csv(unique(metabolite_pathway[, c('metabolite', 'log2FC')]),
          'cytoscape_nodes.csv', row.names=FALSE)
write.csv(metabolite_pathway[, c('metabolite', 'pathway')],
          'cytoscape_edges.csv', row.names=FALSE)

# 或者使用 igraph 预处理网络
library(igraph)
net <- graph_from_data_frame(metabolite_pathway[, c('metabolite', 'pathway')],
                             directed=FALSE)
plot(net, vertex.size=20, vertex.label.cex=0.8,
     layout=layout_with_fr)
```

**导出建议**：
- 静态图导出为 PDF/SVG（出版）和 PNG（演示）
- 交互图导出为 HTML（可在浏览器中打开）
- Cytoscape 网络导出为 .cys 或 .sif 格式

# 阶段四：代谢物注释和鉴定

## 1. 注释证据层级

对每个特征建立注释表，至少包含 `feature_id`、m/z、RT、极性、加合物、同位素组、候选名称/ID、分子式、质量误差、MS/MS 分数、RT证据、数据库来源和置信等级。

推荐按 MSI 思路报告：

- **Level 1**：与同条件真实标准品的保留时间和 MS/MS 等证据一致
- **Level 2**：与数据库 MS/MS 光谱匹配
- **Level 3**：分子式或诊断碎片支持，但结构未完全确认
- **Level 4**：仅精确质量/数据库匹配
- **Unknown**：暂无可靠注释

不要将 Level 3/4 结果直接写成确定的化合物名称。

## 2. 精确质量和加合物匹配

先由 m/z 和加合物计算中性单同位素质量，再在本地 HMDB/KEGG 参考表中按 ppm 搜索。HMDB 不应被假设为公开 REST API；需要先获取合法的本地参考表。

```r
adduct_masses <- c('[M+H]+'=1.007276, '[M+Na]+'=22.989218,
                   '[M-H]-'=-1.007276, '[M+Cl]-'=34.969402)
search_mass <- function(mz, adduct, ppm, ref) {
  neutral <- mz - adduct_masses[[adduct]]
  tol <- neutral * ppm / 1e6
  hits <- ref[abs(ref$monoisotopic_mass - neutral) <= tol, , drop=FALSE]
  if (nrow(hits) == 0) return(hits)
  hits$mass_error_ppm <- (hits$monoisotopic_mass-neutral)/neutral*1e6
  hits[order(abs(hits$mass_error_ppm)), ]
}
```

## 3. MS/MS 光谱匹配

可使用 MatchMS 对查询谱图和参考库进行过滤、标准化及 Cosine/Modified Cosine 匹配。阈值应结合谱图峰数、前体隔离、碰撞能量和库质量解释；单一分数不能替代人工核查。

```python
from matchms import calculate_scores
from matchms.importing import load_from_mgf
from matchms.similarity import CosineGreedy

queries = list(load_from_mgf('sample_msms.mgf'))
references = list(load_from_mgf('reference_library.mgf'))
scores = calculate_scores(references, queries, CosineGreedy(tolerance=0.01))
```

可选工具：SIRIUS + CSI:FingerID、MetFrag 和保留时间预测。它们用于生成候选和排序，不应单独视为标准品确认。

## 4. 去冗余与注释结果导出

结合 CAMERA 的同位素/加合物/相关峰结果，标记或合并同一化合物的冗余特征。导出 `annotated_features.csv`，按置信等级、质量误差、MS/MS 分数和强度排序，并汇总各级别数量。

# 阶段五：通路映射和生物学解释

## 1. ID 标准化

优先使用 HMDB、KEGG 或 PubChem ID，而不是直接依赖自由文本名称。保留未映射代谢物并报告映射率、重复映射和歧义映射；不要静默丢弃无法映射的结果。

## 2. 富集和定量通路分析

- **ORA**：使用显著代谢物列表，报告背景代谢物集合。
- **QEA/MSEA**：使用连续的浓度、log2FC 或统计量，避免任意二值化。
- **拓扑分析**：结合通路结构，报告 pathway impact。
- **多重检验**：报告 FDR/校正后的显著性。

```r
library(MetaboAnalystR)
mSet <- InitDataObjects('conc', 'pathora', FALSE)
mSet <- SetOrganism(mSet, 'hsa')
mSet <- Setup.MapData(mSet, metabolites)
mSet <- CrossReferencing(mSet, 'hmdb')
mSet <- SetKEGG.PathLib(mSet, 'hsa', 'current')
mSet <- SetMetabolomeFilter(mSet, FALSE)
mSet <- CalculateOraScore(mSet, 'rbc', 'hyperg')
ora_results <- mSet$analSet$ora.mat
```

可使用 `KEGGREST` 查询通路、`pathview` 将 log2FC 映射到 KEGG 图，或使用 `ReactomePA`/`clusterProfiler` 进行 Reactome 分析。注意部分工具主要面向基因；使用前确认输入 ID 类型和代谢物支持范围。

## 3. 解释和导出

通路解释应结合：通路 FDR、命中数、富集方向、拓扑 impact、代谢物注释置信度、变化方向以及实验背景。不要仅凭单个低置信度代谢物宣称通路被激活。

输出：`pathway_enrichment.csv`、通路气泡图/条形图、KEGG pathway 图、代谢物-通路网络和解释摘要。

# 最终交付清单

完成流程时，至少交付：

1. 原始数据检查和样本信息核对结果
2. XCMS 参数、峰数、RT 校正和 feature table
3. CAMERA 同位素/加合物注释（如适用）
4. 缺失值、归一化、批次校正和 QC-RSD 结果
5. PCA 与异常样本判断
6. 差异分析表（效应量、p 值、FDR）
7. 监督模型的交叉验证指标（如使用）
8. 代谢物注释表和 MSI 置信等级
9. 通路富集/拓扑分析结果及映射率
10. 完整参数、软件版本、随机种子和日志

## 异常情况处理

- 没有 QC：不能执行可靠的 QC-RSC；改为报告其他归一化方法及其局限。
- 批次和生物学分组完全混杂：不要使用 ComBat 假装消除批次；明确指出设计不可辨识。
- MS/MS 不足：保留为 Level 4 或 Unknown，不要强行鉴定。
- 特征过少或过多：回到峰检测、分组和过滤参数检查，不要仅靠统计阈值补救。
- PCA 显示严重离群：先核查原始文件、峰数、TIC、进样和元数据，再决定是否剔除，并记录理由。
- 监督模型分离完美但交叉验证差：判定为可能过拟合，降低模型复杂度或增加独立验证样本。

## 结果可重复性

每次分析保存：输入文件清单、样本元数据、R/Python 脚本、软件和数据库版本、所有参数、随机种子、过滤记录、图表和最终报告。所有删除、插补、校正和注释决策必须可追溯。
