---
name: bio-microbiome-taxonomy-assignment
description: 用于对16S、18S或ITS扩增子测序获得的ASV进行可靠、可复现的分类学注释，涵盖DADA2、QIIME 2、IDTAXA和VSEARCH，并强调参考数据库、引物区域、置信度与物种级解释的限制。
---

# 微生物组 ASV 分类学注释

## 适用场景

当用户需要将扩增子测序流程产生的ASV/代表序列注释到门、纲、目、科、属或种等分类等级时使用本 skill。支持：

- 16S rRNA：细菌和古菌；
- 18S rRNA：真核微生物；
- ITS：真菌，优先使用 UNITE；
- DADA2、QIIME 2、DECIPHER/IDTAXA 和 VSEARCH 工作流。

## 总体原则

1. **先确认实验设计**：标记类型（16S/18S/ITS）、扩增区域、引物序列、测序平台、读长、是否已去引物，以及 ASV 表和代表序列的格式。
2. **先确认软件版本**：
   - R：`packageVersion("dada2")`、`packageVersion("DECIPHER")`；
   - CLI：`qiime --version`、`vsearch --version`。
   示例命令不能替代版本核验；参数不兼容时先查看 `<tool> --help` 或 R 帮助并按实际版本调整。
3. **参考数据库必须匹配标记和研究目的**：
   - 16S：SILVA、GTDB 或 RDP；
   - ITS：UNITE；
   - 18S/原生生物：PR2 或适用的 SILVA 数据集。
4. **记录可复现信息**：数据库名称、版本、下载日期、URL、参考序列裁剪方式、软件版本、分类器、阈值和命令。
5. **不要过度解释低分辨率结果**：未达到可靠支持时保留为 `NA` 或更高分类层级，不要强行给出种名。

## 方法选择

### DADA2 朴素贝叶斯分类器

适合已经拥有 DADA2 ASV/序列表，并希望使用 DADA2 原生流程的情况。优点是简单、速度快、易于整合到 R/phyloseq；分类结果应结合 bootstrap 或 `minBoot` 阈值解释。

```r
library(dada2)

seqtab_nochim <- readRDS("seqtab_nochim.rds")

# 使用DADA2官方页面提供的当前格式和最新适用参考集。
# 文件名仅为示例，实际使用前应核对最新版本和标记区域。
taxa_out <- assignTaxonomy(
  seqtab_nochim,
  "silva_nr99_CURRENT_train_set.fa.gz",
  minBoot = 80,
  outputBootstraps = TRUE,
  multithread = TRUE
)

taxa <- taxa_out$tax
boot <- taxa_out$boot
```

注意：`assignTaxonomy()` 默认只返回分类矩阵；需要数值置信度时必须设置 `outputBootstraps = TRUE`。`minBoot = 80` 只是常用起点，应根据数据、数据库和研究目的调整并报告。

### 物种级精确匹配

```r
# 仅当序列与物种参考序列满足DADA2的精确匹配要求时补充物种名。
taxa <- addSpecies(
  taxa,
  "silva_species_assignment_CURRENT.fa.gz"
)
```

`addSpecies()` 主要依赖精确匹配。物种名为 `NA` 很常见；属级或更高等级结果仍可能可靠。16S/18S/ITS 的短片段通常不能稳定区分近缘物种，不应把该结果当作培养或全基因组水平的物种鉴定。

### GTDB（16S）

GTDB适合希望采用基于基因组和系统发育的现代分类体系的研究。它不一定比 SILVA 在所有环境样本中都“更好”，应根据覆盖度、历史研究可比性和目标生物选择。

```r
taxa_gtdb <- assignTaxonomy(
  seqtab_nochim,
  "GTDB_CURRENT_16S_train_set.fa.gz",
  minBoot = 80,
  multithread = TRUE
)
```

### RDP（16S）

```r
taxa_rdp <- assignTaxonomy(
  seqtab_nochim,
  "rdp_train_set_CURRENT.fa.gz",
  minBoot = 80,
  multithread = TRUE
)
```

RDP 分类等级（通常 6 级）比 SILVA/GTDB 更简洁，覆盖度和分辨率也相对有限，适合对分类精细度要求不高或需要与历史 RDP 结果比较的场景。

### UNITE（ITS）

```r
taxa_its <- assignTaxonomy(
  seqtab_nochim,
  "unite_CURRENT_dynamic.fasta",
  minBoot = 80,
  multithread = TRUE
)
```

ITS长度变异较大，必须确认参考集与目标 ITS 区域相符，并对种级结果采取更谨慎的解释。

## QIIME 2 工作流

### 推荐：按引物提取参考区域后训练分类器

不要直接用全长参考序列训练短扩增子分类器。应先根据实际 forward/reverse primer 提取参考区域，再训练分类器：

```bash
# 1. 从全长参考序列提取与实验扩增区域对应的片段
qiime feature-classifier extract-reads \
  --i-sequences silva-138-99-seqs.qza \
  --p-f-primer FORWARD_PRIMER \
  --p-r-primer REVERSE_PRIMER \
  --p-trunc-len 0 \
  --o-reads silva-amplicon-seqs.qza

# 2. 使用同一批已裁剪的参考序列和对应taxonomy训练分类器
qiime feature-classifier fit-classifier-naive-bayes \
  --i-reference-reads silva-amplicon-seqs.qza \
  --i-reference-taxonomy silva-138-99-tax.qza \
  --o-classifier silva-amplicon-nb-classifier.qza

# 3. 对ASV代表序列进行分类
qiime feature-classifier classify-sklearn \
  --i-classifier silva-amplicon-nb-classifier.qza \
  --i-reads rep-seqs.qza \
  --o-classification taxonomy.qza
```

`FORWARD_PRIMER` 和 `REVERSE_PRIMER` 必须替换为真实引物序列；若序列已经去引物，应确认参考序列提取策略与 ASV 序列方向一致。必要时使用 `qiime feature-classifier classify-consensus-vsearch` 进行比较，但不要把不同方法的结果未经检查直接混合。

## IDTAXA（DECIPHER）

IDTAXA通常比简单朴素贝叶斯分类更保守，适合关注错误归属和低置信度分类的场景。

```r
library(DECIPHER)
library(Biostrings)

load("SILVA_SSU_training.RData")  # 应包含 trainingSet

dna <- Biostrings::DNAStringSet(getSequences(seqtab_nochim))
ids <- IdTaxa(
  dna,
  trainingSet,
  strand = "top",
  processors = NULL,
  verbose = TRUE
)

ranks <- c("domain", "phylum", "class", "order", "family", "genus", "species")
taxa_idtaxa <- t(vapply(ids, function(x) {
  out <- rep(NA_character_, length(ranks))
  idx <- match(ranks, x$rank)
  out[!is.na(idx)] <- x$taxon[idx[!is.na(idx)]]
  out[grepl("^unclassified_", out)] <- NA_character_
  out
}, character(length(ranks))))
colnames(taxa_idtaxa) <- ranks
```

实际使用前应核对 IDTAXA training set 的对象结构、分类等级命名和 DECIPHER 版本；不同训练集可能使用 `kingdom` 而不是 `domain`。

## VSEARCH：精确/近似匹配与 LCA

VSEARCH 的 `--blast6out` 只输出比对命中信息，不会自动生成完整 taxonomy。使用时必须准备参考序列 ID 到分类字符串的映射表，并明确多重命中、identity、query coverage 和最低共同祖先（LCA）规则。

```bash
vsearch --usearch_global asv_seqs.fasta \
  --db silva_reference.fasta \
  --id 0.97 \
  --query_cov 0.8 \
  --blast6out hits.tsv \
  --top_hits_only
```

后处理至少应：

1. 用参考序列 ID 查找 taxonomy 映射；
2. 检查 identity、alignment length 和 query coverage；
3. 对相同或近似最佳命中取 LCA，而不是任意选择一个命中；
4. 将无法一致归属的等级设为 `NA`；
5. 说明 97% identity 是近似阈值，不能直接等同于属级或种级鉴定。

若需要完整自动化流程，应提供一个经过测试的后处理脚本，并在输出中保留命中证据和阈值。

## 置信度与结果质控

### DADA2 bootstrap过滤

```r
# taxa 和 boot 的维度应一致；boot通常按百分制表示。
keep <- boot >= 80
taxa_filtered <- taxa

taxa_filtered[!keep] <- NA

# 可选：使分类层级保持一致，避免较高层级不确定却保留更低层级。
ranks <- colnames(taxa_filtered)
for (i in seq_len(nrow(taxa_filtered))) {
  unknown <- which(is.na(taxa_filtered[i, ]))[1]
  if (!is.na(unknown)) taxa_filtered[i, unknown:length(ranks)] <- NA
}
```

推荐同时检查：未分类 ASV 比例、各分类等级的置信度分布、每个样本的分类覆盖度、污染/非目标序列，以及参考数据库是否覆盖目标类群。阈值不是普适真理，应在方法部分说明依据。

## 整合到 phyloseq

```r
library(phyloseq)

ps <- phyloseq(
  otu_table(seqtab_nochim, taxa_are_rows = FALSE),
  tax_table(taxa_filtered)
)
sample_data(ps) <- sample_data(
  read.csv("sample_metadata.csv", row.names = 1, check.names = FALSE)
)
taxa_names(ps) <- paste0("ASV", seq_len(ntaxa(ps)))
```

在构造 `phyloseq` 对象前，确认 ASV/样本名称在丰度表、分类表和元数据中一致，并确认分类表列名和顺序符合后续分析需求。

## 数据库选择速查

| 标记/目标 | 优先考虑的数据库 | 说明 |
|---|---|---|
| 16S 细菌/古菌 | SILVA、GTDB、RDP | SILVA便于文献比较；GTDB采用现代基因组分类；RDP较简洁 |
| ITS 真菌 | UNITE | 优先使用与目标ITS区域及版本匹配的动态参考集 |
| 18S/原生生物 | PR2、SILVA | 根据目标类群和研究目的选择 |

## 输出要求

每次完成分类注释时，报告：

- 输入文件和 ASV 数量；
- 标记类型、扩增区域和引物；
- 数据库名称、版本、下载日期和来源；
- 软件/分类器版本；
- 置信度或 identity/query coverage 阈值；
- 各分类等级的未分类比例；
- 物种级结果的限制；
- 如使用 VSEARCH，说明 taxonomy 映射和 LCA 规则；
- 如比较多个方法，说明冲突处理方式。

## 禁止或避免

- 不要把 ASV 分类结果称为确定的物种鉴定；
- 不要在未核对引物区域的情况下直接套用全长参考库；
- 不要把 VSEARCH 的 top hit 直接当作完整 taxonomy；
- 不要混用不同数据库的等级名称而不做标准化；
- 不要静默覆盖或丢弃低置信度结果；
- 不要假设示例中的数据库文件名永远有效，始终从官方来源核对最新版本。
