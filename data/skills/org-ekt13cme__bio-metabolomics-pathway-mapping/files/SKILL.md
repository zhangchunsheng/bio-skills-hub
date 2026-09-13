---
name: bio-metabolomics-pathway-mapping
description: 使用 KEGG、MetaboAnalystR 和适合的 Reactome 工具进行代谢物通路映射、富集分析与拓扑分析。适用于解释代谢组学结果、评估通路改变并生成可复现的分析报告。
tool_type: r
primary_tool: MetaboAnalystR
---

# 代谢组学通路映射

当用户提出“将代谢物映射到通路”“进行代谢物通路富集”或“解释代谢组学通路变化”时，执行本 Skill。

## 工作原则

1. **先明确输入与问题**：确认物种、代谢物 ID 类型、输入是代谢物列表还是带方向的定量数据，以及用户需要 ORA、QEA、拓扑分析还是可视化。
2. **优先使用最简单的适用方法**：
   - 只有代谢物列表：使用过度富集分析（ORA）。
   - 有 fold change、log2FC 或统计量：使用定量富集分析（QEA）或基于排序的分析。
   - 需要考虑通路结构：在输入和 ID 映射可靠时再进行拓扑分析。
3. **不要混淆分子类型**：ReactomePA 的 `enrichPathway()` 主要接受 Entrez 基因 ID，不能把 Reactome 通路 ID 或 HMDB 代谢物 ID 直接作为 `gene` 输入。
4. **公开假设与不确定性**：若代谢物名称存在一对多映射、物种未确定、背景集合缺失或接口版本不明，必须说明影响并在必要时询问用户。
5. **定义并验证成功标准**：报告输入数、成功映射数、映射率、显著通路、FDR、通路影响值（如适用）以及使用的软件和数据库版本。

## 版本与可复现性

使用示例前，先检查实际安装版本和函数接口：

```r
packages <- c("MetaboAnalystR", "KEGGREST", "pathview")
for (pkg in packages) {
    if (requireNamespace(pkg, quietly = TRUE)) {
        cat(pkg, as.character(packageVersion(pkg)), "\n")
    } else {
        cat(pkg, "未安装\n")
    }
}

# 对关键函数确认当前版本参数
?MetaboAnalystR::InitDataObjects
?MetaboAnalystR::Setup.MapData
?MetaboAnalystR::CrossReferencing
```

如果出现 `could not find function`、`unused argument`、对象列名不存在或返回对象结构变化等错误，应先检查当前版本文档和函数签名，再按实际 API 调整；不要机械重复执行同一代码。

记录以下信息：R、MetaboAnalystR、KEGGREST、pathview 版本，物种，ID 类型，数据库访问日期，以及分析参数。

## 物种与输入要求

开始分析前确认：

- 物种和 KEGG organism code，例如人类 `hsa`、小鼠 `mmu`、大鼠 `rno`。
- 输入 ID 类型：HMDB、KEGG compound、PubChem、名称或其他数据库 ID。
- 代谢物名称是否经过标准化；同义词、盐形式、异构体和加合物可能导致不同映射。
- 是否提供背景代谢物集合。ORA 应优先使用“实验中实际检测到的全部可合格代谢物”作为背景，而不是默认全代谢组。
- 是否存在重复 ID、空值、未识别代谢物和一对多映射。

建议先做输入清洗，并报告映射率：

```r
clean_metabolites <- function(x) {
    x <- trimws(as.character(x))
    x <- x[!is.na(x) & nzchar(x)]
    unique(x)
}

metabolites <- clean_metabolites(metabolites)
stopifnot(length(metabolites) > 0)
```

`CrossReferencing()` 的类型必须与输入一致：

```r
# HMDB ID
mSet <- CrossReferencing(mSet, "hmdb")

# 代谢物名称
mSet <- CrossReferencing(mSet, "name")

# KEGG compound ID
mSet <- CrossReferencing(mSet, "kegg")

# PubChem ID
mSet <- CrossReferencing(mSet, "pubchem")
```

不要因为示例使用 HMDB 就对名称或 KEGG ID 固定使用 `"hmdb"`。

## 过度富集分析（ORA）

**适用场景：** 用户只有一组候选或显著代谢物，没有可靠的连续效应值。

```r
library(MetaboAnalystR)

organism <- "hsa"  # 根据研究物种修改
metabolites <- c("HMDB0000001", "HMDB0000005", "HMDB0000010")
input_type <- "hmdb"  # 也可以是 name、kegg 或 pubchem

mSet <- InitDataObjects("conc", "pathora", FALSE)
mSet <- SetOrganism(mSet, organism)
mSet <- Setup.MapData(mSet, clean_metabolites(metabolites))
mSet <- CrossReferencing(mSet, input_type)
mSet <- SetKEGG.PathLib(mSet, organism, "current")
mSet <- SetMetabolomeFilter(mSet, FALSE)
mSet <- CalculateOraScore(mSet, "rbc", "hyperg")

ora_results <- as.data.frame(mSet$analSet$ora.mat)
ora_results$pathway <- rownames(ora_results)
```

运行后必须检查结果对象的实际列名，并确认 `ora_results` 是否为空。若有背景代谢物参数，应按当前 MetaboAnalystR 版本设置；不能默认把所有数据库化合物当作研究背景。

## 定量富集分析（QEA）

**适用场景：** 每个代谢物都有 fold change、log2FC、浓度或其他连续统计量。

先明确数值的含义：`fc`、`log2FC`、浓度和 z-score 不能不加说明地互换。对于方向性分析，优先使用经过统计分析定义清楚的带方向统计量。

```r
metabolite_data <- data.frame(
    compound = c("Glucose", "Lactate", "Pyruvate"),
    value = c(1.5, 2.3, 0.7),
    stringsAsFactors = FALSE
)

mSet <- InitDataObjects("conc", "pathqea", FALSE)
mSet <- SetOrganism(mSet, "hsa")
mSet <- Setup.MapData(mSet, metabolite_data)
mSet <- CrossReferencing(mSet, "name")
mSet <- SetKEGG.PathLib(mSet, "hsa", "current")

# 以下参数需根据已安装 MetaboAnalystR 版本的帮助文档确认
mSet <- CalculateQeaScore(mSet, "rbc", "gt")
qea_results <- as.data.frame(mSet$analSet$qea.mat)
```

如果当前版本要求矩阵、特定列名或不同参数，不要直接套用上述示例；先查看 `?Setup.MapData` 和 `?CalculateQeaScore`，并记录调整内容。

## 通路拓扑分析

**适用场景：** 用户希望在富集之外考虑代谢物在通路中的位置和连接关系。

拓扑结果对数据库结构和代谢物映射十分敏感。只有在 ID 映射质量较高、物种正确且输入数据适合时才报告 `Impact` 或类似指标。

```r
mSet <- InitDataObjects("conc", "pathinteg", FALSE)
mSet <- SetOrganism(mSet, "hsa")
mSet <- Setup.MapData(mSet, metabolites)
mSet <- CrossReferencing(mSet, "hmdb")
mSet <- SetKEGG.PathLib(mSet, "hsa", "current")
mSet <- SetMetabolomeFilter(mSet, FALSE)

# 先确认当前版本中 HyperScore 的含义和适用分析模式
?MetaboAnalystR::CalculateHyperScore
mSet <- CalculateHyperScore(mSet)
topo_results <- as.data.frame(mSet$analSet$topo.mat)
```

不要把拓扑影响值解释为通路活性或因果效应；它通常是数据库拓扑和输入信号共同决定的统计指标。

## KEGG 直接映射

当用户只需要查询化合物所属通路，或希望获得比 MetaboAnalystR 更透明的映射时，可使用 KEGGREST：

```r
library(KEGGREST)

kegg_ids <- c("C00031", "C00186", "C00022")

find_pathways <- function(kegg_id) {
    result <- keggLink("pathway", kegg_id)
    if (length(result) == 0) return(character())
    unname(result)
}

pathway_map <- lapply(setNames(kegg_ids, kegg_ids), find_pathways)
```

记录 KEGG 查询日期。不同物种的通路结果不同，不能在未确认物种的情况下直接使用 `hsa`。

## Reactome 的正确使用边界

ReactomePA 的 `enrichPathway()` 主要用于**基因通路富集**，其输入通常是 Entrez gene ID。例如：

```r
library(ReactomePA)

gene_entrez <- c("3098", "5213", "226")
reactome_gene_results <- enrichPathway(
    gene = gene_entrez,
    organism = "human",
    pvalueCutoff = 0.05,
    pAdjustMethod = "BH",
    readable = TRUE
)
```

不要将以下内容直接传给 `enrichPathway(gene = ...)`：

- Reactome 通路 ID，如 `R-HSA-...`；
- HMDB 代谢物 ID；
- KEGG compound ID；
- 未转换的代谢物名称。

对于代谢物—Reactome 分析，应使用能够处理 Reactome 化合物实体的专门工具或 API，先确认化合物映射关系，再进行自定义富集。若无法获得可靠的化合物映射，应明确报告 Reactome 未用于代谢物富集，而不是伪造基因输入。

## 通路可视化

```r
library(pathview)

metabolite_data <- c("C00031" = 1.5, "C00186" = 2.3, "C00022" = 0.7)

pathview(
    cpd.data = metabolite_data,
    pathway.id = "00010",
    species = "hsa",
    cpd.idtype = "kegg",
    out.suffix = "glycolysis_mapped"
)
```

可视化前确认：

- `names(metabolite_data)` 是 KEGG compound ID；
- 数值的方向和单位已定义；
- `species` 与研究物种一致；
- 输出文件和数据库版本已记录。

## 代谢物—通路网络

仅当富集结果确实包含代谢物列表列时，才构建二部网络。不同版本的结果列名可能不同，因此先检查：

```r
names(pathway_results)
```

示例函数应对空值和空边进行检查：

```r
library(igraph)

build_metabolite_pathway_network <- function(pathway_results, metabolite_column = "Metabolites") {
    stopifnot(metabolite_column %in% names(pathway_results))

    edges_list <- lapply(seq_len(nrow(pathway_results)), function(i) {
        pathway <- as.character(pathway_results$pathway[i])
        mets <- unlist(strsplit(as.character(pathway_results[[metabolite_column]][i]), ";\\s*"))
        mets <- mets[!is.na(mets) & nzchar(mets) & mets != "NA"]
        if (!nzchar(pathway) || length(mets) == 0) return(NULL)
        data.frame(from = mets, to = pathway, stringsAsFactors = FALSE)
    })

    edges <- do.call(rbind, edges_list)
    if (is.null(edges) || nrow(edges) == 0) stop("没有可用于构建网络的代谢物—通路边")
    edges <- unique(edges)

    graph_from_data_frame(edges, directed = FALSE)
}
```

网络节点的大小、颜色和中心性只能作为探索性可视化，不应直接等同于生物学重要性。

## 多重检验、报告与导出

所有通路富集结果都应报告原始 p 值和多重检验校正结果，优先使用 BH-FDR。不要只报告原始 p 值显著的通路。

由于 ORA、QEA 和拓扑结果的列名不同，导出时不要固定假设所有列都存在：

```r
export_pathways <- function(results, output_file) {
    results_df <- as.data.frame(results)
    results_df$pathway <- rownames(results_df)

    preferred <- c("pathway", "Total", "Expected", "Hits", "Raw p",
                   "p.value", "Holm adjust", "p.adjust", "FDR", "Impact")
    selected <- intersect(preferred, names(results_df))
    if (length(selected) <= 1) {
        stop("结果中没有发现可导出的统计列；请先检查 names(results)")
    }

    out <- results_df[, selected, drop = FALSE]
    fdr_col <- intersect(c("FDR", "p.adjust"), names(out))
    if (length(fdr_col) == 1) {
        out <- out[order(out[[fdr_col]], na.last = TRUE), , drop = FALSE]
    }
    write.csv(out, output_file, row.names = FALSE)
    out
}
```

报告至少包括：

- 输入代谢物总数、成功映射数和映射率；
- 使用的 ID 类型、物种和背景集合；
- 分析方法（ORA/QEA/拓扑）；
- 通路数据库、软件包版本和访问日期；
- p 值校正方法和筛选阈值；
- 未映射、歧义映射和重复映射的处理方式；
- 结果限制，尤其是通路冗余、数据库覆盖不足和拓扑指标的解释边界。

## 常见错误

- 用 `CrossReferencing(mSet, "hmdb")` 处理代谢物名称或 KEGG ID。
- 将 Reactome 通路 ID 作为 `ReactomePA::enrichPathway()` 的基因输入。
- 使用 fold change 却不说明是 FC 还是 log2FC。
- 忽略背景代谢物集合，直接把数据库全部化合物作为背景。
- 只根据一个显著通路宣称某条生物学机制已被证实。
- 在未检查结果列名的情况下固定提取 `FDR` 或 `Impact`。
- 将拓扑 `Impact` 直接解释为通路活性、因果关系或生物学重要性。
- 不记录数据库和软件版本，导致结果无法复现。

## 验证标准

一次合格的通路映射分析至少满足：

1. 物种、输入 ID 类型和分析方法已明确。
2. 输入已去除空值、重复值和无效数值，并报告映射率。
3. 使用了与输入类型匹配的交叉引用方法。
4. 结果包含多重检验校正，并检查了结果对象的实际列名。
5. 若使用拓扑分析，明确说明其统计含义和局限性。
6. Reactome 分析没有将代谢物 ID 冒充基因 ID。
7. 输出文件、软件版本、数据库日期和关键参数已记录。

