---
name: bio-pathway-gsea
description: 使用 clusterProfiler 的 gseGO 和 gseKEGG 进行基因集富集分析（GSEA）。适用于分析排序基因列表，在不设任意显著性阈值的情况下发现基因集的协同表达变化。
tool_type: R
primary_tool: clusterProfiler
---

# 基因集富集分析（GSEA）

## 版本兼容性

以下示例面向 DESeq2 1.42+ 与 clusterProfiler 4.6+；不同 Bioconductor 版本的参数和默认算法可能不同。

使用示例代码前，请先确认已安装包的版本是否兼容。若版本不同：

- 运行 `packageVersion('<pkg>')`，再运行 `?函数名` 确认参数和默认值。
- 若出现 `unused argument`、`could not find function` 或对象列名不存在等错误，请按已安装版本的实际 API 调整；不要机械地重复执行示例代码。
- 记录 R、Bioconductor、注释包、KEGG/MSigDB 数据版本和分析日期，以便复现。

## 物种适配

不同物种需使用对应的 OrgDb 注释包：

| 物种 | OrgDb 包 | KEGG 代码 |
|------|----------|-----------|
| 人类 | `org.Hs.eg.db` | `hsa` |
| 小鼠 | `org.Mm.eg.db` | `mmu` |
| 大鼠 | `org.Rn.eg.db` | `rno` |
| 斑马鱼 | `org.Dr.eg.db` | `dre` |
| 拟南芥 | `org.At.tair.db` | `ath` |
| 酵母 | `org.Sc.sgd.db` | `sce` |
| 果蝇 | `org.Dm.eg.db` | `dme` |

安装 OrgDb 包：
```r
# 从 Bioconductor 安装
if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("org.Mm.eg.db")  # 小鼠示例
```

## 核心概念

GSEA 使用按统计量排序的**全部基因**（如 log2FC 或带方向的 p 值），而不是只使用显著基因子集。它检测某个基因集的成员是否集中出现在排序列表的顶部或底部。

## 准备排序基因列表

**目标：** 创建可供 GSEA 使用的、已排序且带基因 ID 名称的统计量向量。

**方法：** 从差异表达结果中提取倍数变化或其他统计量，以基因 ID 作为名称，并按降序排序。

“对我的差异表达结果运行 GSEA”表示：按表达统计量对所有基因排序，并检验预定义基因集是否聚集于列表两端。

```r
library(clusterProfiler)
library(org.Hs.eg.db)

de_results <- read.csv('de_results.csv')

# 清洗排名向量：删除空 ID/非有限值，并让每个 ID 只保留绝对统计量最大的记录
clean_rank_vector <- function(score, gene_id) {
    rank_df <- data.frame(
        gene_id = as.character(gene_id),
        score = as.numeric(score),
        stringsAsFactors = FALSE
    )
    rank_df <- rank_df[
        !is.na(rank_df$gene_id) & rank_df$gene_id != "" & is.finite(rank_df$score),
    ]
    rank_df <- rank_df[order(abs(rank_df$score), decreasing = TRUE), ]
    rank_df <- rank_df[!duplicated(rank_df$gene_id), ]
    sort(setNames(rank_df$score, rank_df$gene_id), decreasing = TRUE)
}

# 命名向量：值为统计量，名称为基因 ID
# DESeq2 分析通常优先使用 Wald stat；这里只演示通用的 log2FoldChange
gene_list <- clean_rank_vector(de_results$log2FoldChange, de_results$gene_id)

stopifnot(
    length(gene_list) > 0,
    !anyDuplicated(names(gene_list)),
    all(is.finite(gene_list)),
    identical(gene_list, sort(gene_list, decreasing = TRUE))
)
```

## 为 GSEA 转换基因 ID

**目标：** 将基因符号映射为 Entrez ID，同时保留排序统计量。

**方法：** 使用 `bitr` 进行 ID 转换，然后用 Entrez ID 重新构建并排序命名向量。

```r
# 将基因符号转换为 Entrez ID；bitr 可能产生一对多和多对一映射
gene_ids <- bitr(
    names(gene_list),
    fromType = "SYMBOL",
    toType = "ENTREZID",
    OrgDb = org.Hs.eg.db
)

rank_df <- data.frame(
    SYMBOL = names(gene_list),
    score = as.numeric(gene_list),
    stringsAsFactors = FALSE
)
mapped <- merge(rank_df, gene_ids, by = "SYMBOL")
mapping_rate <- length(unique(mapped$SYMBOL)) / length(gene_list)

# 每个 Entrez ID 保留绝对统计量最大的记录，确保名称唯一
mapped <- mapped[order(abs(mapped$score), decreasing = TRUE), ]
mapped <- mapped[!duplicated(mapped$ENTREZID), ]
gene_list_entrez <- sort(
    setNames(mapped$score, mapped$ENTREZID),
    decreasing = TRUE
)

message(sprintf("成功映射 %.1f%% 的输入基因", 100 * mapping_rate))
stopifnot(length(gene_list_entrez) > 0, !anyDuplicated(names(gene_list_entrez)))
```

## 可选排序统计量

**目标：** 选择同时平衡效应大小与显著性的 GSEA 排序指标。

**方法：** DESeq2 结果通常优先使用带方向且已按标准误缩放的 Wald 统计量。原始 log2 倍数变化或带方向的 p 值（`-log10(p) * sign(FC)`）可作为备选，但后者容易放大极小 p 值并产生大量并列值。

```r
# 首选：DESeq2 Wald 统计量
gene_list <- clean_rank_vector(de_results$stat, de_results$gene_id)

# 备选：带方向的 p 值；限制 p 值下界，避免 p == 0 产生 Inf
safe_p <- pmax(de_results$pvalue, .Machine$double.xmin)
signed_p <- -log10(safe_p) * sign(de_results$log2FoldChange)
gene_list_signed_p <- clean_rank_vector(signed_p, de_results$gene_id)

# 并列统计量过多会导致并列基因的内部顺序任意，应报告并谨慎解释
tie_fraction <- 1 - length(unique(gene_list)) / length(gene_list)
message(sprintf("排名统计量并列比例：%.1f%%", 100 * tie_fraction))
```

## 使用 GO 进行 GSEA

**目标：** 在不设显著性筛选阈值的前提下，检测 GO 基因集中的协同表达变化。

**方法：** 对排序基因列表运行 `gseGO`，检验 GO 条目成员是否富集在列表顶部或底部。

```r
set.seed(20260806)
gse_go <- gseGO(
    geneList = gene_list_entrez,
    OrgDb = org.Hs.eg.db,
    ont = 'BP',                     # BP、MF、CC 或 ALL
    minGSSize = 10,
    maxGSSize = 500,
    pvalueCutoff = 0.05,
    verbose = FALSE,
    pAdjustMethod = 'BH'
)

# 转换为可读基因符号
gse_go <- setReadable(gse_go, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID')
```

## 使用 KEGG 进行 GSEA

**目标：** 识别在全部基因中具有协同表达变化的 KEGG 通路。

**方法：** 基于 KEGG 通路定义，对排序基因列表运行 `gseKEGG`。默认在线 KEGG 注释会随数据库更新而变化，因此应记录分析日期和数据库版本。

```r
set.seed(20260806)
gse_kegg <- gseKEGG(
    geneList = gene_list_entrez,
    organism = 'hsa',
    minGSSize = 10,
    maxGSSize = 500,
    pvalueCutoff = 0.05,
    verbose = FALSE
)

# 转换为可读基因符号
gse_kegg <- setReadable(gse_kegg, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID')
```

## 使用自定义基因集进行 GSEA

**目标：** 对用户提供或非标准的基因集集合运行 GSEA。

**方法：** 读取 GMT 文件，并通过通用 `GSEA` 函数传入 `TERM2GENE` 映射。

```r
# 读取 GMT（Gene Matrix Transposed）文件
gene_sets <- read.gmt('msigdb_hallmarks.gmt')

# TERM2GENE 的基因 ID 类型必须与 names(gene_list_entrez) 完全一致
set.seed(20260806)
gse_custom <- GSEA(
    geneList = gene_list_entrez,
    TERM2GENE = gene_sets,
    minGSSize = 10,
    maxGSSize = 500,
    pvalueCutoff = 0.05
)
```

## MSigDB 基因集

**目标：** 使用分子特征数据库（MSigDB）中整理的基因集运行 GSEA。

**方法：** 通过 `msigdbr` 获取基因集，整理为 `TERM2GENE` 数据框后运行 `GSEA`。

**版权提醒：** MSigDB 数据集使用需注明版权。在出版物或报告中使用时，应引用：
> Subramanian, A. et al. (2005). Gene set enrichment analysis: a knowledge-based approach to interpreting genome-wide expression profiles. Proc Natl Acad Sci USA 102, 15545-15550.

```r
# 使用 msigdbr 包获取 MSigDB 基因集
library(msigdbr)

# Hallmark 基因集；新版 msigdbr 使用 collection 和 ncbi_gene
hallmarks <- msigdbr(
    db_species = "HS",
    species = "Homo sapiens",
    collection = "H"
)
hallmarks_t2g <- hallmarks[, c("gs_name", "ncbi_gene")]

# 旧版 msigdbr 可能使用 category 和 entrez_gene，请先检查 packageVersion() 与 colnames()
set.seed(20260806)
gse_hallmark <- GSEA(
    geneList = gene_list_entrez,
    TERM2GENE = hallmarks_t2g,
    pvalueCutoff = 0.05
)

# 其他类别：C1（位置）、C2（整理）、C3（基序）、C5（GO）、C6（致癌）、C7（免疫）
```

## 理解结果

```r
# 查看结果
head(gse_go)
results <- as.data.frame(gse_go)

# 关键列：
# - NES：标准化富集分数；正值富集于排名顶部，负值富集于排名底部
# - pvalue：名义 p 值
# - p.adjust：FDR 校正后的 p 值
# - core_enrichment：前导边缘（leading edge）基因
```

## 解读 NES（标准化富集分数）

| NES | 解释 |
|-----|------|
| 正值（> 0） | 基因集富集于排序向量顶部 |
| 负值（< 0） | 基因集富集于排序向量底部 |
| `|NES| > 1.5` | 可作为效应强度的经验参考，不能替代 FDR 判断 |

顶部和底部对应哪个实验组，取决于差异分析的 contrast 定义与排名统计量方向；解释结果时必须明确写出比较方向。

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `geneList` | 必需 | 已命名、已排序的数值向量 |
| `OrgDb` | 必需 | 物种注释数据库（用于 `gseGO`） |
| `organism` | `hsa` | KEGG 物种代码（用于 `gseKEGG`） |
| `ont` | `BP` | 本体：BP、MF、CC、ALL |
| `minGSSize` | 10 | 基因集最小基因数（详见下方参数选择依据） |
| `maxGSSize` | 500 | 基因集最大基因数（详见下方参数选择依据） |
| `pvalueCutoff` | 0.05 | p 值阈值，可根据研究目的调整 |
| `pAdjustMethod` | `BH` | 多重检验校正方法（BH/Bonferroni/holm 等） |
| `nPerm` | 1000 | clusterProfiler 4.20.0 的默认置换次数；旧版可能不同 |
| `method` | `multilevel` | clusterProfiler 4.20.0 的默认 GSEA 方法；按已安装版本文档确认 |
| `eps` | `1e-10` | p 值计算下界（部分版本通过 `...` 传递） |

## 参数选择科学依据

**minGSSize（最小基因集大小）**
- **默认 10**：避免过于特异的基因集（假阳性）
- **研究特异性通路**：可提高至 15-20，确保信号生物学意义
- **小型或特异基因集**：仅在注释覆盖和研究问题确有依据时降至 5，并评估多重检验负担；样本量本身不是降低该阈值的理由

**maxGSSize（最大基因集大小）**
- **默认 500**：排除过于宽泛的基因集（如"代谢过程"）
- **细胞器/全局过程**：可提高至 800-1000
- **聚焦特定机制**：可降低至 200-300

**pvalueCutoff 与 pAdjustMethod**
- **BH（Benjamini-Hochberg）**：控制 FDR，适用于探索性分析
- **Bonferroni**：更保守，适用于验证性研究或小规模基因集
- **pvalueCutoff = 0.05**：常用阈值；如需尽量保留完整结果，可设为数值 `1`，再按 `p.adjust` 手动筛选，不要传入 `NULL`

## 导出结果

**目标：** 保存 GSEA 结果，并提取前导边缘基因以供后续分析。

**方法：** 将富集结果对象转为数据框后导出 CSV，并解析 `core_enrichment` 中的驱动基因。

```r
results_df <- as.data.frame(gse_go)
write.csv(results_df, 'gsea_go_results.csv', row.names = FALSE)

# 获取某个条目的前导边缘基因
leading_edge <- strsplit(results_df$core_enrichment[1], '/')[[1]]
```

## 注意事项

- **必须排序：** 基因列表必须按降序排序。
- **输入必须有效：** 删除 `NA`、`Inf`、空 ID，并确保基因 ID 唯一；报告 ID 映射率与排名 ties。
- **命名向量：** 名称为基因 ID，数值为统计量；`TERM2GENE` 必须使用相同 ID 类型。
- **避免任意阈值：** 使用所有具有有效统计量且能映射的检测基因，而非仅使用显著基因。
- **NES 方向依赖 contrast：** 正值表示排序顶部富集，不应脱离比较方向直接称为“上调”。
- **统计显著性：** `|NES|` 是效应强度参考，主要结合 `p.adjust`、基因集大小和生物学背景判断。
- **前导边缘：** `core_enrichment` 包含驱动富集信号的基因。
- **可复现性：** 设置随机种子，并记录软件、注释包和在线数据库版本或访问日期。

## 相关技能

- go-enrichment：GO 过度富集分析
- kegg-pathways：KEGG 过度富集分析
- enrichment-visualization：GSEA 曲线图、山脊图等可视化
