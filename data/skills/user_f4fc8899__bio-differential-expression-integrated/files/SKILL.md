---
slug: bio-differential-expression-integrated
version: 1.0.1
displayName: "差异表达分析 / RNA-seq differential expression analysis"
name: bio-differential-expression-integrated
summary: "中文：差异表达分析综合技能，整合 6 个相关专题，覆盖RNA-seq差异表达分析：DESeq2、edgeR、limma-voom，涵盖标准化、批次校正、结果提取与可视化。 English: Integrated RNA-seq differential expression analysis skill covering 6 related topics, including RNA-seq differential expression analysis: DESeq2, edgeR, limma-voom, covering normalization, batch correction, result extraction, and visualization."
description: "中文：这是一个面向差异表达分析的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：RNA-seq差异表达分析：DESeq2、edgeR、limma-voom，涵盖标准化、批次校正、结果提取与可视化。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：DESeq2, edgeR, sva。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for RNA-seq differential expression analysis, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers RNA-seq differential expression analysis: DESeq2, edgeR, limma-voom, covering normalization, batch correction, result extraction, and visualization. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: DESeq2, edgeR, sva. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# differential-expression 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: differential-expression -->

## 子目录：differential-expression/batch-correction

<!-- BEGIN FILE: differential-expression/batch-correction/SKILL.md -->
---
name: bio-differential-expression-batch-correction
description: Handles batch effects in bulk RNA-seq via design-matrix inclusion (the correct path for DE), ComBat/ComBat-seq for visualization, SVA for unknown latent factors, RUVSeq for negative-control-gene-anchored unwanted variation, and limma::removeBatchEffect for plotting only. Encodes the Nygaard 2016 cardinal sin against testing on a batch-corrected matrix, the choice between SVA/RUVg/RUVs/RUVr, the confounding non-identifiability problem, the single-cell boundary (Harmony/MNN are NOT for bulk), and the Goh 2017 harmonization critique. Use when designing a DE analysis with batch structure, troubleshooting batch-dominated PCA, choosing ComBat vs ComBat-seq, handling unknown batch via SVA, integrating across studies, or deciding when (rarely) to subtract batch.
tool_type: r
primary_tool: sva
---

## Version Compatibility

Reference examples tested with: sva 3.50+ (includes ComBat + ComBat_seq), DESeq2 1.42+, edgeR 4.0+, limma 3.58+, RUVSeq 1.36+, ggplot2 3.5+, harmony 1.2+ (single-cell context only)

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Batch Effect Correction

**"Remove the batch effect before DE"** -> Almost always WRONG. Include batch as a covariate in the design formula (`~ batch + condition`) so DESeq2/edgeR/limma model it without subtracting. Subtraction is for visualization only.

## The Single Most Important Modern Insight -- The Nygaard 2016 cardinal sin

Nygaard, Rødland, Hovig 2016 *Biostatistics* 17(1):29-39, "Methods that remove batch effects while retaining group differences may lead to exaggerated confidence in downstream analyses." Translation: **never run ComBat (or ComBat-seq, or `removeBatchEffect`, or SVA-subtract-then-test) and then run DE on the corrected matrix.**

Mechanism: batch-correction methods fit a model `y_ij = alpha + X_ij beta + gamma_i + delta_i epsilon_ij` and subtract the batch terms. The downstream DE test then computes p-values as if those degrees of freedom had never been spent. Residual df is lower than what DESeq2/edgeR/limma assume. Type-I error inflates -- the gene list looks more significant than it should.

The right approach: **include batch in the design**. `~ batch + condition`. DESeq2/edgeR/limma will properly partial out the batch effect from the condition estimate and account for the spent degrees of freedom in the inference. The batch is corrected at the inference stage, not by mutating counts.

`removeBatchEffect` (limma) is for visualization only -- the function's help page says so. ComBat/ComBat-seq output is for visualization, clustering, or downstream tools that cannot take a design matrix (rare; mostly ML).

A second clarification: structural confounding (every "treated" sample in batch 1, every "control" in batch 2) is non-identifiable. No method fixes this -- the "treatment effect" and "batch effect" are mathematically the same vector. The fix is experimental design (randomize batches in advance). ComBat/SVA on a fully-confounded design silently removes the treatment effect along with the batch effect.

## Algorithmic Taxonomy

| Method | Input | Mechanism | Use for |
|--------|-------|-----------|---------|
| Design-matrix inclusion (`~ batch + condition`) | Raw counts; known batch | Partial out batch in the GLM, spent df accounted | DE testing -- the correct path |
| ComBat (Johnson, Li, Rabinovic 2007) | Log-transformed / continuous expression | Empirical-Bayes location and scale shifts per batch | Visualization of microarray / continuous data |
| ComBat-seq (Zhang, Parmigiani, Johnson 2020) | Raw RNA-seq counts | NB-GLM equivalent of ComBat; returns integer counts | Visualization of RNA-seq counts; cross-study harmonization for ML (with caveat) |
| `limma::removeBatchEffect` | Normalized expression | Linear regression subtraction with design protection | Visualization only -- explicit help-page warning |
| SVA (Leek, Storey 2007 + Leek 2012) | Normalized expression | Estimate latent surrogate variables explaining residual variance independent of variable-of-interest | Unknown batch / hidden technical structure -- add SVs to design |
| svaseq (Leek 2014) | Counts | Count-data variant of SVA | Counts version |
| RUVg (Risso, Ngai, Speed, Dudoit 2014) | Counts; negative control genes | Factor analysis of control-gene residual; W as covariate | Strong negative controls (ERCC, housekeeping) -- add W to design |
| RUVs | Counts; replicate samples | Factor analysis within replicate groups; assumes replicates differ only by unwanted variation | Multi-condition with biological replicates as "controls" |
| RUVr | Counts; design only | Factor analysis of residuals from initial fit | Most data-driven; most likely to absorb biology -- caution |
| Harmony, MNN, Scanorama, BBKNN | Single-cell embeddings | Iterative alignment of clusters across samples | Single-cell ONLY; not bulk |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Known batch, want DE | `~ batch + condition` in design; do NOT subtract | Cardinal sin avoidance |
| PCA shows batch separation | Include batch in design; for the figure, `removeBatchEffect` is OK (visualization only) | Two purposes, two tools |
| Unknown batch structure | `sva` / `svaseq`; add SVs as covariates in design | Captures latent technical factors |
| Have ERCC spike-ins or trusted housekeeping | `RUVSeq::RUVg` with control gene indices; add W to design | Most principled UV removal |
| Have replicate samples (technical reps within biological) | `RUVSeq::RUVs` | Replicate structure indicates "this differs only by UV" |
| Cross-study integration (TCGA + ICGC + own data) | ComBat-seq for counts, ComBat for log-expression, THEN meta-analysis -- do NOT pool then DE | Goh 2017 warning |
| Fully confounded batch and condition | Re-collect samples; no method fixes this | Non-identifiable |
| Visualizing batch removal for a figure | `removeBatchEffect(expr, batch = batch, design = model.matrix(~condition))` | Visualization is what it's for |
| Single-cell data | Harmony / MNN / Scanorama in the single-cell category, not here | Different problem |

## Standard Workflow -- Design-Matrix Inclusion

**Goal:** Test the condition effect while accounting for known batch structure with proper degrees-of-freedom accounting.

**Approach:** Include batch as a covariate in the design formula; DESeq2/edgeR/limma will partial it out and compute correct p-values.

```r
library(DESeq2)

dds <- DESeqDataSetFromMatrix(countData = counts, colData = coldata,
                               design = ~ batch + condition)
dds <- DESeq(dds)
res <- results(dds, name = 'condition_treated_vs_control')
```

```r
library(edgeR)
y <- DGEList(counts = counts, group = coldata$condition)
keep <- filterByExpr(y, design = model.matrix(~ batch + condition, coldata))
y <- y[keep, , keep.lib.sizes = FALSE]
y <- normLibSizes(y)

design <- model.matrix(~ batch + condition, coldata)
y <- estimateDisp(y, design, robust = TRUE)
fit <- glmQLFit(y, design, robust = TRUE)
qlf <- glmQLFTest(fit, coef = 'conditiontreated')
```

When known confounders are continuous (RIN, library prep date as days), include them as continuous covariates -- no batch correction needed for those:

```r
design = ~ RIN + library_prep_day + condition
```

## ComBat-seq (Visualization or Cross-Study Counts)

**Goal:** Adjust raw counts to remove known batch effects while preserving biology, for VISUALIZATION or for downstream tools that need a single corrected matrix.

**Approach:** `ComBat_seq(counts, batch, group)` returns batch-adjusted integer counts via NB-GLM. Use the output for PCA, clustering, ML -- NOT for DE testing.

```r
library(sva)

corrected_counts <- ComBat_seq(counts = as.matrix(counts),
                                batch = coldata$batch,
                                group = coldata$condition,
                                full_mod = TRUE)

vsd_corrected <- vst(DESeqDataSetFromMatrix(corrected_counts, coldata, ~1))
plotPCA(vsd_corrected, intgroup = 'condition')
```

`full_mod = TRUE` keeps biological covariates protected (the `group` argument). With `full_mod = FALSE`, ComBat-seq removes batch AND group differences -- a serious failure mode.

`ComBat` (the non-seq version) is for log-transformed or microarray data, NOT raw counts. Running `ComBat` on raw counts produces fractional values and assumes Gaussian residuals where counts are NB. Wrong tool, silent failure.

## SVA -- Unknown Batch

**Goal:** Discover latent technical factors when batch is not recorded, add them as covariates.

**Approach:** Estimate the number of surrogate variables; estimate the SVs themselves; add them to the design and re-run DE.

```r
library(sva)
library(DESeq2)

dds <- DESeqDataSetFromMatrix(counts, coldata, design = ~ condition)
dds <- estimateSizeFactors(dds)
norm_counts <- counts(dds, normalized = TRUE)

mod  <- model.matrix(~ condition, coldata)
mod0 <- model.matrix(~ 1, coldata)

n_sv <- num.sv(norm_counts, mod, method = 'leek')
svobj <- svaseq(norm_counts, mod, mod0, n.sv = n_sv)

for (i in seq_len(ncol(svobj$sv))) {
    colData(dds)[[paste0('SV', i)]] <- svobj$sv[, i]
}
sv_formula <- as.formula(paste('~', paste(paste0('SV', seq_len(ncol(svobj$sv))),
                                          collapse = ' + '), '+ condition'))
design(dds) <- sv_formula
dds <- DESeq(dds)
```

CRITICAL CHECK: compute the correlation between each SV and the variable of interest. If any SV correlates with treatment at r > 0.3, do NOT include it -- doing so would partial out biology, deflating the effect of interest.

```r
sapply(seq_len(ncol(svobj$sv)),
       function(i) cor(svobj$sv[, i], as.numeric(coldata$condition)))
```

`svaseq` is the count-data version (Leek 2014); `sva` is for log-transformed / microarray data.

## RUVSeq -- Negative-Control-Anchored UV

**Goal:** Estimate unwanted variation using ERCC spike-ins, housekeeping genes, replicate samples, or post-fit residuals; add as covariates in design.

**Approach:** Pick the RUV variant matching the available controls; add the resulting W matrix to the design.

```r
library(RUVSeq)
library(edgeR)

control_idx <- which(rownames(counts) %in% ercc_genes)

set <- newSeqExpressionSet(as.matrix(counts), phenoData = coldata)
set <- betweenLaneNormalization(set, which = 'upper')

ruv <- RUVg(set, control_idx, k = 2)

design <- model.matrix(~ pData(ruv)$W_1 + pData(ruv)$W_2 + condition,
                        data = coldata)
y <- DGEList(counts = counts, group = coldata$condition)
y <- normLibSizes(y)
y <- estimateDisp(y, design, robust = TRUE)
fit <- glmQLFit(y, design, robust = TRUE)
qlf <- glmQLFTest(fit, coef = 'conditiontreated')
```

| Variant | Control source | Most appropriate when | Failure mode |
|---------|----------------|----------------------|--------------|
| RUVg | Negative control genes (ERCC, housekeeping) | Strong, validated controls exist | Bad controls -> partials out biology |
| RUVs | Replicate samples / technical reps | Multi-condition with reps that should differ only by UV | Wrong replicate structure absorbs condition effect |
| RUVr | Residuals from an initial GLM | No external controls; most data-driven | Most likely to absorb true biology -- use last |

Choice of k (number of unwanted factors): no automatic procedure. Try k = 1, 2, 3 and inspect PCA after RUV correction. Treatment effect should remain visible; if it disappears, k is too high. 5-10 is typical; >10 is suspicious.

## removeBatchEffect -- Visualization Only

```r
library(limma)

design <- model.matrix(~ condition, coldata)
log_expr_corrected <- removeBatchEffect(log_expr,
                                         batch = coldata$batch,
                                         design = design)

library(ggplot2)
pca <- prcomp(t(log_expr_corrected), scale. = TRUE)
ggplot(data.frame(PC1 = pca$x[,1], PC2 = pca$x[,2],
                  condition = coldata$condition, batch = coldata$batch),
       aes(PC1, PC2, color = condition, shape = batch)) +
    geom_point(size = 3) +
    ggtitle('After removeBatchEffect (visualization only)')
```

The `design` argument protects condition while removing batch. Common error: passing batch ALSO in the design ("Coefficients not estimable" warning) -- pass batch via `batch=` only, NOT also in `design=`.

DO NOT feed `log_expr_corrected` back into limma `lmFit` for DE testing. The function's own help page says so. The right approach: `lmFit(log_expr, model.matrix(~ batch + condition, coldata))` -- include batch as a covariate.

## Detecting Confounding Early

```r
ct <- table(coldata$condition, coldata$batch)
ct
```

| Pattern | Status | Action |
|---------|--------|--------|
| All cells > 0 with roughly equal proportions | Balanced | Include batch as covariate |
| Some cells low (e.g., 4/4/2/0) | Partially confounded | Include batch; report reduced power |
| Some cells zero AND one factor entirely in one batch | Perfectly confounded | UNFIXABLE -- re-collect or drop the affected comparison |

`alias()` reveals collinear columns in a design matrix:

```r
alias(model.matrix(~ batch + condition, coldata))$Complete
```

## The Single-Cell Boundary

Harmony (Korsunsky et al. 2019 *Nat Methods* 16:1289), MNN (Haghverdi et al. 2018 *Nat Biotechnol* 36:421), Scanorama, BBKNN are designed for single-cell integration where the goal is aligning cell-type clusters across samples/batches. They modify the embedding (PCA coordinates) for downstream UMAP/clustering -- they assume the structural alignment problem of single-cell (many similar cells; align clusters).

DO NOT apply to bulk RNA-seq. Bulk lacks the cluster structure these methods assume.

Conversely, DO NOT use ComBat / ComBat-seq for single-cell. ComBat assumes much more homogeneity than scRNA exhibits; it does not handle zeros well.

See `single-cell/batch-integration` for the single-cell methods.

## The Goh 2017 Critique on "Harmonization"

Goh, Wang, Wong 2017 *Trends Biotechnol* 35(6):498-507 warn that batch-correction methods can:

- Introduce NEW batch-like artifacts (false positives) when the batch structure is unclear
- Fail when the "most genes not DE" assumption is violated (heat shock, immune activation, viral host shutoff)
- Inflate downstream confidence (echoing Nygaard 2016)

Their recommendation for cross-study work: per-cohort DE first, then meta-analyze the effect sizes (`metafor`, `limma` `treat` across cohorts). DO NOT pool data, harmonize, then re-test.

"Harmonization" in clinical genomics often means ComBat across cohorts then DE on the harmonized matrix -- the exact failure mode Nygaard 2016 describes. Same problem, different vocabulary.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Design-inclusion (`~ batch + condition`) and SVA give different gene lists | SVA captured biology (high SV-condition correlation) OR known batch was incomplete | Check SV-vs-condition correlations; if any |r|>0.3, drop that SV. If SVA still differs after pruning, hidden technical factor exists beyond known batch -- combine `~ batch + SV_clean + condition` |
| Design-inclusion and RUVg disagree | RUVg control genes (ERCC, housekeeping) had real biological variation | Validate control set; switch RUVg -> RUVs (replicate-based) or back to design only |
| ComBat-seq corrected gene list larger than design-included gene list | Nygaard 2016 cardinal sin: spent df not accounted for in downstream DE on corrected matrix | DISCARD the ComBat-seq DE result; report design-included only |
| Cross-cohort meta-analysis shows different DE per cohort | Real biological heterogeneity OR cohort-specific technical drift | Per-cohort DE then meta-analyze effect sizes (`metafor`); do NOT pool then test (Goh 2017) |
| All methods (design, SVA, RUVg) agree on top 100 genes | Robust signal | Report the intersection as high-confidence |
| All methods disagree | Confounded design OR weak signal at high noise floor | Suspect non-identifiability; verify `alias()` and balance |

The design-inclusion result (`~ batch + condition` or `~ confounders + condition`) is the reference. SVA/RUV results are sensitivity analyses; when they agree with the design result, confidence rises. When they diverge, investigate before believing either.

## Per-Method Failure Modes

### Tested on a batch-corrected matrix -- inflated significance

**Trigger:** Pipeline: `ComBat_seq(counts, batch)` -> `DESeq2 on corrected_counts`. Many more "significant" genes than expected.

**Mechanism:** ComBat-seq removed batch terms; DESeq2 then computed inference as if those df had not been spent. Type-I error inflates.

**Symptom:** Implausibly long DE gene list; replication in independent cohort recovers <50%; p-value histogram leans anti-conservative.

**Fix:** Re-run with `~ batch + condition` design on RAW counts. Discard the corrected-counts DE result.

### SVA captured the biology

**Trigger:** `sva` returned 5 SVs; SV2 correlates with `condition` at r = 0.7; user added all SVs to design.

**Mechanism:** When biology is correlated with the hidden factor (e.g., disease severity drives both expression AND blood-draw timing), SVA's SVs capture biology along with technical noise. Partialling them out deflates the effect of interest.

**Symptom:** Condition effect that was clear in raw PCA disappears after SV adjustment; few or no DE genes.

**Fix:** Compute SV-vs-condition correlations; exclude any SV with |r| > 0.3 from the design. Re-fit.

### ComBat applied to raw counts

**Trigger:** Pipeline uses `ComBat(counts, batch)` (not `ComBat_seq`); output is fractional.

**Mechanism:** ComBat is for log-transformed / Gaussian data. Counts are NB. The Gaussian assumption is wrong and the output is uninterpretable as counts.

**Symptom:** Corrected matrix has fractional values; DESeq2 errors out ("counts matrix should be integers"); naive `round()` gives garbage.

**Fix:** Use `ComBat_seq()` for counts. Or better, include batch as a design covariate.

### Confounded design corrected with SVA -- biology gone

**Trigger:** All treated samples in batch 1, all control in batch 2; user runs SVA hoping it will rescue the design.

**Mechanism:** Batch and treatment vectors are identical (or nearly so). SVA estimates "the unwanted factor"; "the unwanted factor" is treatment.

**Symptom:** SV1 correlates with treatment at r ~ 1; after adjustment, no DE genes.

**Fix:** Acknowledge the design is non-identifiable. No statistical method fixes structural confounding. Re-collect with randomized batches.

### Used Harmony on bulk RNA-seq

**Trigger:** Bulk RNA-seq with batch effect; user reaches for Harmony because they've used it for single-cell.

**Mechanism:** Harmony aligns cluster centroids in single-cell embeddings. Bulk has no cluster structure -- typically 6-30 samples, not 10000+ cells.

**Symptom:** Harmony "succeeds" but the result is meaningless; downstream DE is nonsense.

**Fix:** Use design-matrix inclusion (`~ batch + condition`) or ComBat-seq for visualization. Harmony belongs to `single-cell/batch-integration`.

## Common errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `Coefficients not estimable` from removeBatchEffect | Batch included in both `batch=` and `design=` | Pass batch via `batch=` only |
| ComBat output has fractional values | Wrong tool for counts | Use `ComBat_seq` |
| SV adjustment kills condition effect | SVs captured biology | Check correlation; exclude high-correlation SVs |
| `Inconsistent dimensions` in RUVg | `control_idx` is symbols vs ENSEMBL rownames | Match index type |
| `full_mod` not specified in ComBat-seq | Defaults; biology may not be protected | Set `full_mod = TRUE` and pass `group =` |

## References

- Nygaard V, Rødland EA, Hovig E. 2016. Methods that remove batch effects while retaining group differences may lead to exaggerated confidence in downstream analyses. *Biostatistics* 17(1):29-39. doi:10.1093/biostatistics/kxv027
- Johnson WE, Li C, Rabinovic A. 2007. Adjusting batch effects in microarray expression data using empirical Bayes methods. *Biostatistics* 8(1):118-127. doi:10.1093/biostatistics/kxj037
- Zhang Y, Parmigiani G, Johnson WE. 2020. ComBat-seq: batch effect adjustment for RNA-seq count data. *NAR Genom Bioinform* 2(3):lqaa078. doi:10.1093/nargab/lqaa078
- Leek JT, Storey JD. 2007. Capturing heterogeneity in gene expression studies by surrogate variable analysis. *PLoS Genet* 3(9):e161. doi:10.1371/journal.pgen.0030161
- Leek JT, Johnson WE, Parker HS, Jaffe AE, Storey JD. 2012. The sva package for removing batch effects and other unwanted variation in high-throughput experiments. *Bioinformatics* 28(6):882-883. doi:10.1093/bioinformatics/bts034
- Leek JT. 2014. svaseq: removing batch effects and other unwanted noise from sequencing data. *Nucleic Acids Res* 42(21):e161. doi:10.1093/nar/gku864
- Risso D, Ngai J, Speed TP, Dudoit S. 2014. Normalization of RNA-seq data using factor analysis of control genes or samples. *Nat Biotechnol* 32(9):896-902. doi:10.1038/nbt.2931
- Goh WWB, Wang W, Wong L. 2017. Why batch effects matter in omics data, and how to avoid them. *Trends Biotechnol* 35(6):498-507. doi:10.1016/j.tibtech.2017.02.012
- Korsunsky I et al. 2019. Fast, sensitive and accurate integration of single-cell data with Harmony. *Nat Methods* 16(12):1289-1296. doi:10.1038/s41592-019-0619-0
- Haghverdi L, Lun ATL, Morgan MD, Marioni JC. 2018. Batch effects in single-cell RNA-sequencing data are corrected by matching mutual nearest neighbors. *Nat Biotechnol* 36(5):421-427. doi:10.1038/nbt.4091
- Ritchie ME et al. 2015. limma powers differential expression analyses for RNA-sequencing and microarray studies. *Nucleic Acids Res* 43(7):e47. doi:10.1093/nar/gkv007

## Related Skills

- deseq2-basics - DE with `~ batch + condition` design
- edger-basics - edgeR pipeline with batch in design
- de-results - p-value histogram diagnostics for missed batch
- de-visualization - PCA shows batch effects; sample distance heatmap; figure-time use of removeBatchEffect
- expression-matrix/metadata-joins - Confounding detection; sample swap detection
- expression-matrix/normalization - TMM/RLE failure modes overlap with batch failure modes
- single-cell/batch-integration - Harmony, MNN, Scanorama for single-cell (not bulk)
<!-- END FILE: differential-expression/batch-correction/SKILL.md -->

## 子目录：differential-expression/de-results

<!-- BEGIN FILE: differential-expression/de-results/SKILL.md -->
---
name: bio-differential-expression-de-results
description: Extracts, filters, annotates, and exports differential expression results from DESeq2 or edgeR with proper handling of padj=NA (independent filtering, Cook's outliers, all-zero), multiple-testing correction choice (BH vs Storey q-value vs IHW vs lfsr), TREAT vs post-hoc fold-change filtering, p-value histogram diagnostics, gene annotation via org.db/biomaRt/mygene, GSEA preranked input, ORA background construction, replication reality (Schurch 2016 small-n result), and SABV/sex-stratified reporting. Use when extracting and interpreting DE results, troubleshooting padj=NA, choosing FDR method, preparing ranked lists for pathway analysis, annotating gene IDs, or comparing DESeq2 vs edgeR outputs.
tool_type: r
primary_tool: DESeq2
---

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, edgeR 4.0+, IHW 1.34+, qvalue 2.34+, ashr 2.2+, AnnotationDbi 1.66+, org.Hs.eg.db 3.18+, biomaRt 2.58+, mygene 1.38+ (Python), dplyr 1.1+, openxlsx 4.2+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# DE Results

**"What are my significant genes?"** -> Extract DE estimates and p-values from the fitted model, handle missing padj correctly, apply FDR control appropriate to the design, and produce the table or ranked list the downstream tool actually needs.

## The Single Most Important Modern Insight -- `padj = NA` has three distinct meanings

A `NA` in the `padj` column is not a missing value; it is a flag indicating which filter excluded the gene. The three causes -- independent filtering, Cook's distance outlier, and all-zero in a group -- have completely different remediations. Dropping all NA rows blindly silently discards real signal, most often from low-count master regulators (transcription factors expressed at ~10 counts) that pass biology but fail the data-driven baseMean threshold.

| `padj = NA` cause | DESeq2 detection | What it means | Fix if undesired |
|-------------------|------------------|---------------|-------------------|
| Independent filtering | finite `pvalue`, `NA` `padj`, baseMean below auto threshold | Removed before BH adjustment to maximize rejections at `alpha` | `results(dds, independentFiltering = FALSE)` OR `filterFun = ihw` |
| Cook's distance outlier | `NA` `pvalue`, `NA` `padj`, baseMean > 0, group has >=3 reps | One sample has Cook's > `qf(0.99, p, m-p)` | `results(dds, cooksCutoff = FALSE)` |
| All-zero or near-zero in a group | `NA` `pvalue` AND baseMean very low | Insufficient information to test | Filter at preprocess time; or accept |

Independent filtering (Bourgon, Gentleman, Huber 2010 *PNAS* 107:9546) chooses the baseMean threshold to maximize rejections. The filter MUST be independent of the test statistic under the null -- this is why baseMean (the across-sample mean) is the canonical choice. Using "min count in treatment group" as a filter VIOLATES the independence requirement and inflates type-I error. Most pipelines unknowingly do this; do not.

A second axis: at n>=7 per group, `DESeq()` also REPLACES outlier counts via `replaceOutliers()` and refits (default `minReplicatesForReplace = 7`). Cook's filtering is NOT computed for continuous covariates -- a continuous-covariate analysis has effectively no outlier filtering.

## Algorithmic Taxonomy

| Method | What it computes | When to use | Failure mode |
|--------|------------------|-------------|--------------|
| BH (`p.adjust(method='BH')`, DESeq2 default `pAdjustMethod='BH'`) | FDR at fixed alpha; Benjamini-Hochberg 1995 | Default for most RNA-seq DE | Assumes independence or PRDS; many overlapping tests violate |
| Storey q-value (`qvalue::qvalue`) | q-value using estimated pi_0 | Genome-scale with many true nulls | Pi_0 estimation can fail at small test counts |
| IHW (`results(filterFun=ihw)`, Ignatiadis 2016 *Nat Methods* 13:577) | Weighted BH with covariate-informed weights | Modern default for DESeq2; +5-20% discoveries at same FDR | Covariate MUST be independent under null |
| ashr local false sign rate (`lfsr` / `svalue`, with `svalue=TRUE`) | P(sign of estimate is wrong) | When effect-direction certainty is what matters | Conservative lower bound on FDR; not interchangeable with padj |
| BY (`p.adjust(method='BY')`) | Benjamini-Yekutieli; arbitrary dependence | Strongly correlated tests | Uniformly conservative; rarely needed for DE |
| Holm / Bonferroni | FWER | Small confirmatory test sets | Far too conservative for genome-scale |
| TREAT / `lfcThreshold=` | FDR for "|LFC| > tau" hypothesis | Pre-specified biologically meaningful threshold | tau must be set BEFORE looking at data |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Standard bulk DE, two groups | DESeq2 results with default BH; report padj < 0.05 | Default works |
| Want more power at same FDR | `results(dds, filterFun = ihw)` | IHW typically gains 5-20% |
| Pre-specified biological fold-change matters | `results(dds, lfcThreshold = log2(1.5), altHypothesis = 'greaterAbs')` OR `glmTreat(fit, lfc = log2(1.5))` | Post-hoc `padj<0.05 & abs(LFC)>1` does NOT control FDR for the magnitude claim |
| Ranking for GSEA preranked | `stat` (Wald Z) for DESeq2 OR shrunken LFC | Never use unshrunken LFC -- low-count noise dominates |
| ORA input | Subset by padj<0.05; background = ALL TESTED genes (post-independent-filtering) | Background = "all genes in genome" is wrong; pre-filtering already excluded many |
| Many NA padj including biologically interesting genes | Diagnose: independent filtering vs Cook's vs all-zero; turn off the offending filter only for that gene set | Blanket `na.omit` discards signal |
| Multi-condition design | LRT for "any change" first; pairwise per-level Wald for effect sizes | LRT padj is omnibus; LRT LFC is one specific coefficient |
| Small n (<=3/group) | Report as exploratory, top hits only | Schurch 2016: tools miss 20-40% of true positives at n=3 |
| Human / mouse with mixed sexes | Include sex as covariate; run sex-stratified sensitivity | SABV mandate; sex effect is real and chromosomal |
| Prokaryotic | Use Prokka/Bakta GFF, KEGG strain code | Ensembl/org.db are eukaryote-only |

## Extracting Results

**Goal:** Pull DE estimates and p-values from a fitted DESeq2 or edgeR object into a usable data frame with explicit contrast naming.

**Approach:** `results()` (DESeq2) or `topTags()` (edgeR) with explicit `name=` / `coef=`; convert to data.frame; preserve row order if planning to join with annotation.

```r
library(DESeq2)
library(dplyr)

resultsNames(dds)
res <- results(dds, name = 'condition_treated_vs_control', alpha = 0.05)
res_shrunk <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')

res_df <- as.data.frame(res)
res_df$gene <- rownames(res_df)
```

```r
library(edgeR)
tt <- topTags(qlf, n = Inf, sort.by = 'none')$table
tt$gene <- rownames(tt)
```

`sort.by = 'none'` in `topTags` preserves the original gene order -- critical when joining with an annotation table by row index. Default is sort by p-value.

Column name reminder (a recurring cross-tool bug):

| Tool | LFC column | Adjusted p-value column |
|------|------------|------------------------|
| DESeq2 | `log2FoldChange` | `padj` |
| edgeR | `logFC` | `FDR` |
| limma `topTable` | `logFC` | `adj.P.Val` |
| limma `topTreat` | `logFC` | `adj.P.Val` (post-TREAT) |

## TREAT vs Post-hoc LFC Filtering

**Goal:** Make a defensible FDR claim about "biologically meaningful fold change" genes.

**Approach:** Use TREAT or `lfcThreshold=` to test a magnitude hypothesis with proper FDR control. Post-hoc filtering of `padj<0.05 & abs(LFC)>tau` does NOT control FDR for the magnitude claim.

```r
res_treat <- results(dds, lfcThreshold = log2(1.5), altHypothesis = 'greaterAbs', alpha = 0.05)

# edgeR equivalent
tr <- glmTreat(fit, coef = 2, lfc = log2(1.5))
```

What a reviewer is really probing with a "200 genes >2x changed at FDR 5%" claim: is the FDR for the change>2x claim or for the change-non-zero claim? Post-hoc filtering controls FDR only for the latter. TREAT (or `lfcThreshold=`) controls FDR for the former. McCarthy & Smyth 2009 *Bioinformatics* 25:765 is the canonical citation.

## IHW for Better Power

**Goal:** Gain 5-20% more discoveries at the same FDR by weighting p-values with a covariate (typically baseMean) that informs power but is independent of the null.

**Approach:** `results(dds, filterFun = ihw)` replaces independent filtering with Ignatiadis 2016 hypothesis weighting.

```r
library(IHW)
res_ihw <- results(dds, filterFun = ihw, alpha = 0.05)
```

When IHW does NOT help:
- Small number of tests (<5000 after filtering) -- not enough data to learn weights
- Covariate is treatment-correlated (violates the null-independence requirement)
- Covariate uninformative about test power

Storey q-value as an alternative (different framework -- estimates pi_0 fraction of true nulls):

```r
library(qvalue)
qv <- qvalue(res$pvalue[!is.na(res$pvalue)])
res$qvalue <- NA
res$qvalue[!is.na(res$pvalue)] <- qv$qvalues
```

ashr lfsr (local false sign rate -- probability the estimated direction is wrong):

```r
res_ashr <- lfcShrink(dds, coef = 'condition_treated_vs_control',
                       type = 'ashr', svalue = TRUE)
res_ashr$svalue  # FDR-like, based on lfsr; requires svalue=TRUE
```

`svalue=TRUE` is required to populate the `svalue` column; the default returns the standard `pvalue`/`padj` columns only. lfsr and padj are NOT interchangeable. lfsr asks "P(sign wrong)"; padj asks "expected fraction of false discoveries". When reporting, state which.

## P-value Histogram Diagnostics

**Goal:** Diagnose model misspecification, hidden batch effects, or over-correction by inspecting the raw p-value distribution.

**Approach:** Plot raw p-values; under a correctly specified null, the histogram is uniform with an upward spike near zero (the true DE genes).

```r
library(ggplot2)
ggplot(res_df, aes(x = pvalue)) +
    geom_histogram(bins = 50, fill = 'steelblue', color = 'white') +
    labs(x = 'P-value', y = 'Frequency', title = 'P-value distribution') +
    theme_bw()
```

| Shape | Meaning | Action |
|-------|---------|--------|
| Uniform + spike near 0 | Correct: null genes uniform, true DE near 0 | Proceed |
| Anti-conservative (U-shape; both ends spiked) | Hidden batch effect, unmodeled confounder, dispersion misspecified | Inspect PCA for batch; add covariate; check `plotDispEsts` |
| Conservative (depleted near 0, spike near 1) | Over-correction; too many covariates; wrong dispersion | Simplify model; check dispersion plot for excess shrinkage |
| Spike only at p = 1 | Discrete artifact from very-low-count genes | Pre-filter more aggressively |
| Bimodal with spike at 0.5 | Unusual; suggests a discrete categorical test masquerading | Investigate |

The histogram is one of the cheapest sanity checks in a DE pipeline; always plot it before believing the gene list.

## Filtering and Ordering

**Goal:** Subset to significant genes and rank by p-value, fold change, or expression level for downstream use.

**Approach:** dplyr-style filter + arrange; handle NA padj explicitly per the three-meanings table at the top.

```r
sig <- res_df %>%
    filter(!is.na(padj), padj < 0.05, abs(log2FoldChange) > 1, baseMean > 10) %>%
    arrange(padj)

# Up- vs down-regulated
up   <- sig %>% filter(log2FoldChange > 0)
down <- sig %>% filter(log2FoldChange < 0)

# Summary
n_tested <- sum(!is.na(res$padj))
n_sig    <- sum(res$padj < 0.05, na.rm = TRUE)
cat(sprintf('Tested: %d   Significant (padj<0.05): %d   Up: %d   Down: %d\n',
            n_tested, n_sig, sum(sig$log2FoldChange > 0), sum(sig$log2FoldChange < 0)))
```

## Gene Annotation

**Goal:** Map gene IDs to symbols, descriptions, and cross-database identifiers for human-readable results.

**Approach:** Prefer `AnnotationDbi::mapIds` with org.db (fast, local, version-pinned); fall back to biomaRt or mygene for symbols/aliases not in org.db; for prokaryotes, use Prokka/Bakta GFF.

```r
library(org.Hs.eg.db)
library(AnnotationDbi)

res_df$symbol <- mapIds(org.Hs.eg.db, keys = sub('\\..*', '', res_df$gene),
                         keytype = 'ENSEMBL', column = 'SYMBOL', multiVals = 'first')
res_df$entrez <- mapIds(org.Hs.eg.db, keys = sub('\\..*', '', res_df$gene),
                         keytype = 'ENSEMBL', column = 'ENTREZID', multiVals = 'first')
```

The `sub('\\..*', '', ...)` strips the Ensembl version. CAUTION: this regex destroys the `_PAR_Y` suffix in GENCODE 25-43 PAR genes -- use `sub('\\.[0-9]+(_PAR_Y)?$', '\\1', ...)` to preserve. See `expression-matrix/gene-id-mapping` for full details.

For HGNC symbols changed since 2020 (`SEPT1` -> `SEPTIN1`, `MARCH1` -> `MARCHF1`, `MARC1` -> `MTARC1`, `DEC1` -> `DELEC1`) old symbol-keyed downstream tools silently drop genes. Always join on stable Ensembl or Entrez IDs; use symbols as display labels only.

For prokaryotes:

```r
library(rtracklayer)
gff <- import('annotation.gff3')
gene_info <- as.data.frame(gff[gff$type == 'gene',
                                c('locus_tag', 'Name', 'product')])
res_annotated <- merge(res_df, gene_info, by.x = 'gene',
                        by.y = 'locus_tag', all.x = TRUE)
```

## GSEA Preranked Input

**Goal:** Produce a ranked list of all genes (no significance filter) for fgsea / clusterProfiler GSEA.

**Approach:** Rank by Wald statistic (DESeq2 `stat`) or shrunken LFC. NEVER use a filtered set as GSEA input -- GSEA's permutation null requires the full background.

```r
gsea_ranks <- res_df$stat
names(gsea_ranks) <- res_df$gene
gsea_ranks <- sort(gsea_ranks[!is.na(gsea_ranks)], decreasing = TRUE)

# edgeR equivalent
gsea_ranks_edger <- sign(tt$logFC) * -log10(tt$PValue)
names(gsea_ranks_edger) <- rownames(tt)
gsea_ranks_edger <- sort(gsea_ranks_edger[is.finite(gsea_ranks_edger)],
                         decreasing = TRUE)
```

`stat` (Wald Z) is preferred over raw LFC for GSEA because it combines effect and precision in one number. Unshrunken LFC is dominated by low-count noise.

## ORA Input

**Goal:** Run over-representation analysis (enrichGO, enrichKEGG) on a significant gene list with the correct background.

**Approach:** Subset to padj<0.05; background = ALL TESTED genes (post-independent-filtering), NOT the genome.

```r
library(clusterProfiler)

sig_entrez <- na.omit(res_df$entrez[res_df$padj < 0.05])
bg_entrez  <- na.omit(res_df$entrez[!is.na(res_df$padj)])

ora <- enrichGO(gene          = sig_entrez,
                universe      = bg_entrez,
                OrgDb         = org.Hs.eg.db,
                keyType       = 'ENTREZID',
                ont           = 'BP',
                pAdjustMethod = 'BH')
```

Common mistake: omitting `universe=` lets clusterProfiler default to "all annotated genes for this organism" -- which includes thousands of genes never tested. The resulting enrichment p-values are wrong (too small). The background MUST be the tested set.

## Cross-Tool Concordance Check

```r
deseq2_sig <- rownames(subset(deseq2_res, padj < 0.05))
edger_sig  <- rownames(subset(edger_tt,  FDR  < 0.05))

common      <- intersect(deseq2_sig, edger_sig)
deseq2_only <- setdiff(deseq2_sig, edger_sig)
edger_only  <- setdiff(edger_sig, deseq2_sig)

cat(sprintf('DESeq2 sig: %d   edgeR sig: %d   Common: %d (%.1f%%)\n',
            length(deseq2_sig), length(edger_sig), length(common),
            100 * length(common) / min(length(deseq2_sig), length(edger_sig))))
```

Concordance >70% at the top 500: robust. <60%: suspect filtering, normalization, or design difference -- not a tool difference. Run both pipelines with the same filtering and design to isolate.

## Per-Method Failure Modes

### Dropped a key gene by removing NAs

**Trigger:** Pipeline does `res_df <- na.omit(res_df)`; downstream gene of interest is missing from results.

**Mechanism:** Gene was flagged by independent filtering OR Cook's distance; padj is NA but the biology is real.

**Symptom:** A gene with clear differential expression in the count matrix is absent from the results table.

**Fix:** Diagnose which filter fired (independent filtering vs Cook's vs all-zero); rerun `results()` with the appropriate filter off (`independentFiltering = FALSE` or `cooksCutoff = FALSE`).

### Reported FDR on a magnitude-filtered gene set

**Trigger:** Methods section says "genes with padj < 0.05 and abs(LFC) > 1 (FDR < 5%)".

**Mechanism:** BH controls FDR for the |LFC| > 0 hypothesis, not the |LFC| > 1 hypothesis. The post-hoc filter adds no FDR control.

**Symptom:** Reviewer challenges the FDR claim; replication studies show many of the filtered genes are not the magnitude expected.

**Fix:** Use TREAT (`glmTreat`) or `lfcThreshold=` to test the magnitude hypothesis with proper FDR control. Re-do the methods sentence to match what was actually computed.

### ORA universe wrong

**Trigger:** ORA p-values look implausibly small for a small significant gene set.

**Mechanism:** `universe=` argument omitted; clusterProfiler defaulted to all annotated genes in the organism, including thousands never in the tested set.

**Symptom:** Many enriched pathways at strict thresholds; results don't replicate; reviewer questions the background.

**Fix:** Explicitly pass `universe = bg_entrez` where `bg_entrez` is the set of tested gene IDs (i.e., those with non-NA padj).

### "Significant" gene list in n=3 study doesn't replicate

**Trigger:** Small RNA-seq study finds 200 DE genes; validation in independent cohort recovers 60.

**Mechanism:** Schurch 2016 *RNA* 22:839: at n=3/group, all tools miss 20-40% of true positives compared to n=30. Variability of the gene list itself is high.

**Symptom:** 30-50% replication of the gene list across independent runs of the SAME data.

**Fix:** Frame the small-n DE list as hypothesis-generating, not as a stable set of facts. Validate top hits orthogonally before drawing conclusions. Use TREAT for biologically meaningful thresholds to require larger effects.

### Sex-confounded design gives spurious chrX/chrY signal

**Trigger:** Mixed-sex cohort; sex not in the design; many chrY genes call as DE.

**Mechanism:** Sex distribution differs across the experimental groups; the "treatment effect" partially captures sex.

**Symptom:** chrY genes (DDX3Y, RPS4Y1, UTY) and XIST dominate the top DE list.

**Fix:** Include sex in the design (`~ sex + condition`); rerun. For chrX/chrY-specific analyses, sex MUST be in the model or the analysis is uninterpretable. Mauvais-Jarvis et al. 2020 *Lancet* 396:565 reviews the SABV requirement.

## Common errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `$FDR` not found on DESeq2 result | DESeq2 uses `padj`; edgeR uses `FDR` | Check tool, use correct column |
| `summary(res)` shows different cutoff than `results(alpha=)` | `summary(res, alpha=)` defaults to 0.1 | Pass `alpha` explicitly to `summary()` |
| All `padj` NA | All genes filtered (rare; usually a data problem) | Check `independentFilteringResults(res)`; inspect baseMean distribution |
| Direction of LFC reversed | Reference level not set; alphabetical default | `relevel()` BEFORE `DESeq()` |
| Gene symbol mapping rate <50% | Mixed Ensembl versions; recent HGNC renames | Verify Ensembl release, check for SEPT/MARCH/MARC renames |
| `enrichGO` reports thousands of pathways | Wrong `universe=` | Pass `universe = bg_entrez` (tested set, not genome) |

## References

- Benjamini Y, Hochberg Y. 1995. Controlling the false discovery rate: a practical and powerful approach to multiple testing. *J R Stat Soc Ser B* 57(1):289-300. doi:10.1111/j.2517-6161.1995.tb02031.x
- Storey JD. 2003. The positive false discovery rate: a Bayesian interpretation and the q-value. *Ann Stat* 31(6):2013-2035. doi:10.1214/aos/1074290335
- Ignatiadis N, Klaus B, Zaugg JB, Huber W. 2016. Data-driven hypothesis weighting increases detection power in genome-scale multiple testing. *Nat Methods* 13(7):577-580. doi:10.1038/nmeth.3885
- Bourgon R, Gentleman R, Huber W. 2010. Independent filtering increases detection power for high-throughput experiments. *PNAS* 107(21):9546-9551. doi:10.1073/pnas.0914005107
- Stephens M. 2017. False discovery rates: a new deal. *Biostatistics* 18(2):275-294. doi:10.1093/biostatistics/kxw041
- McCarthy DJ, Smyth GK. 2009. Testing significance relative to a fold-change threshold is a TREAT. *Bioinformatics* 25(6):765-771. doi:10.1093/bioinformatics/btp053
- Schurch NJ et al. 2016. How many biological replicates are needed in an RNA-seq experiment and which differential expression tool should you use? *RNA* 22(6):839-851. doi:10.1261/rna.053959.115
- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biol* 15(12):550. doi:10.1186/s13059-014-0550-8
- Mauvais-Jarvis F et al. 2020. Sex and gender: modifiers of health, disease, and medicine. *Lancet* 396(10250):565-582. doi:10.1016/S0140-6736(20)31561-0
- Bruford EA et al. 2020. Guidelines for human gene nomenclature. *Nat Genet* 52:754-758. doi:10.1038/s41588-020-0669-3
- Ziemann M, Eren Y, El-Osta A. 2016. Gene name errors are widespread in the scientific literature. *Genome Biol* 17:177. doi:10.1186/s13059-016-1044-7
- Wu T et al. 2021. clusterProfiler 4.0: A universal enrichment tool for interpreting omics data. *The Innovation* 2(3):100141. doi:10.1016/j.xinn.2021.100141

## Related Skills

- deseq2-basics - Generate DESeq2 results; design, contrasts, LRT, shrinkage
- edger-basics - Generate edgeR results; QL F-test, TREAT, voom
- de-visualization - P-value histogram, MA plot, volcano with shrunken LFC, heatmap, sample distance
- batch-correction - Include batch in design (vs Nygaard 2016 cardinal sin)
- timeseries-de - LRT-with-reduced-model patterns for time
- expression-matrix/gene-id-mapping - ID conversion, HGNC renames, ortholog mapping
- expression-matrix/metadata-joins - Sex covariate, paired design, sample swap detection
- pathway-analysis/go-enrichment - ORA with proper background
- pathway-analysis/gsea - GSEA preranked input from `stat` or shrunken LFC
- pathway-analysis/kegg-pathways - KEGG with strain-specific organism codes
- data-visualization/volcano-and-ma-plots - Custom volcano with apeglm-shrunken LFC
<!-- END FILE: differential-expression/de-results/SKILL.md -->

## 子目录：differential-expression/de-visualization

<!-- BEGIN FILE: differential-expression/de-visualization/SKILL.md -->
---
name: bio-differential-expression-de-visualization
description: Creates DE-specific diagnostic and result visualizations using DESeq2/edgeR built-in functions and lightweight ggplot2 wrappers. Covers MA plot (with the shrunken-LFC compression effect), volcano (with the apeglm caveat that p-values are unchanged), PCA on VST/rlog (never raw counts), sample distance heatmaps, top-DE-gene heatmaps with the row-scaling trap, dispersion / BCV plot interpretation, p-value histogram diagnostics, plotCounts for individual genes, blind=TRUE vs FALSE rationale, and the n=3 visualization stake. Use when generating DE diagnostic plots, choosing VST vs rlog for visualization, troubleshooting suspicious plot patterns (shifted MA cloud, batch-dominated PCA, anti-conservative p-value histogram), or building a standard QC figure panel.
tool_type: r
primary_tool: DESeq2
---

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, edgeR 4.0+, limma 3.58+, ggplot2 3.5+, pheatmap 1.0+, RColorBrewer 1.1+, ggrepel 0.9+, EnhancedVolcano 1.20+, matrixStats 1.2+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# DE Visualization

**"Make the standard DE figure panel"** -> Use built-in functions or thin wrappers to produce diagnostic plots (dispersion, p-value histogram, PCA, sample distance) and result plots (MA, volcano, heatmap of top DE genes, per-gene counts), interpreted as diagnostics of the underlying model.

## Scope

This skill covers DE-specific built-in plots and immediate wrappers. For richer customization:
- Custom volcano/MA with apeglm-shrunken LFC and ggrepel labelling -> `data-visualization/volcano-and-ma-plots`
- PCA / UMAP / t-SNE customization -> `data-visualization/dimensionality-reduction-plots`
- Heatmap customization and ComplexHeatmap recipes -> `data-visualization/heatmaps-clustering`

## The Single Most Important Modern Insight -- A volcano with shrunken LFC compresses the cloud, but the p-values are unchanged

`lfcShrink()` pulls noisy estimates toward zero. On the volcano, that pulls genes horizontally toward the center. But the y-axis (`-log10(pvalue)`) is the **unshrunken Wald p-value** -- shrinkage does NOT recompute p-values (Zhu, Ibrahim, Love 2019 *Bioinformatics* 35:2084). A naive reader sees fewer extreme dots and concludes "fewer genes are significant". Wrong: the same genes are significant; the effect sizes are smaller and more honest.

Always label the volcano x-axis "shrunken log2 fold change (apeglm)" and note the y-axis comes from the unshrunken Wald test. The whole point of the apeglm volcano is the honest effect-size axis; if a publication shows an unshrunken volcano, it is showing inflated effects from low-count noise.

The MA plot has its own version of this: shrinkage flattens the left side (low-mean, formerly extreme LFC) and barely touches the right (high-mean, well-estimated LFC). That asymmetry is the visual signature of working shrinkage.

## Plot Taxonomy

| Plot | Diagnostic OR result | Built-in function | What it tests |
|------|---------------------|-------------------|---------------|
| Dispersion plot | Diagnostic | `plotDispEsts(dds)` (DESeq2), `plotBCV(y)` (edgeR) | Mean-dispersion trend fit quality |
| p-value histogram | Diagnostic | None; use ggplot2 | Null calibration, hidden batch, over-correction |
| PCA on VST/rlog | Diagnostic + result | `plotPCA(vsd, intgroup=...)` (DESeq2), `plotMDS()` (edgeR via limma) | Sample clustering, batch effects, outliers |
| Sample distance heatmap | Diagnostic | `pheatmap` on `dist(t(assay(vsd)))` | Within-group consistency, sample swaps |
| MA plot | Diagnostic + result | `plotMA(res)` (DESeq2), `plotMD(qlf)` (edgeR) | Normalization sanity, LFC vs mean |
| Volcano | Result | ggplot2 wrapper; `EnhancedVolcano` | Top-effect, top-significance gene story |
| Top-DE heatmap | Result | `pheatmap` on `assay(vsd)[sig_genes,]` | Per-gene pattern across conditions |
| `plotCounts` per gene | Result | `plotCounts(dds, gene, intgroup)` | Per-gene biology |

## Decision Tree by Scenario

| Scenario | Recommended approach |
|----------|---------------------|
| PCA for unbiased QC | `vst(dds, blind = TRUE)`; ask "do samples group as expected without design influence?" |
| PCA for results figure | `vst(dds, blind = FALSE)`; design is settled, accept its influence on dispersion |
| n < 30, library sizes vary >4x | `rlog(dds, blind = FALSE)` instead of vst |
| n > 30 | `vst()`; rlog impractical |
| Volcano | Plot shrunken LFC on x, unshrunken p-value on y; label both axes |
| Sample distance heatmap | `vst(blind = TRUE)`; tells if a sample is the wrong group regardless of design |
| Top-DE heatmap, want to see PATTERN | `scale = 'row'` (z-score per gene) |
| Top-DE heatmap, want to see ABSOLUTE LEVEL | `scale = 'none'` on `assay(vsd)`; otherwise weak signal looks strong |
| Top-variable-gene selection | `matrixStats::rowMads(assay(vsd))` instead of `rowVars` -- MAD is outlier-robust |
| n = 3, top genes in volcano | Note Schurch 2016 finding: 20-40% of true positives missed; treat as exploratory |
| Many groups, comparing DE sets | UpSet plot (Lex 2014); Venn drowns above 3 sets |

## Dispersion Diagnostic (Run This First)

**Goal:** Verify the dispersion-mean trend was fit acceptably before trusting any results.

**Approach:** `plotDispEsts(dds)` (DESeq2) or `plotBCV(y)` (edgeR) shows gene-wise (black/blue), fitted trend (red), and final shrunken (blue) dispersions vs mean.

```r
plotDispEsts(dds)

plotBCV(y)
```

| Pattern | Meaning | Action |
|---------|---------|--------|
| Cloud follows trend; final shrunken estimates pulled toward red curve | Healthy fit | Proceed |
| Red trend nowhere near the gene-wise cloud | Parametric trend failed | `DESeq(dds, fitType = 'local')` or `fitType = 'mean'` |
| Many gene-wise dispersions FAR ABOVE the trend | Outlier or unmodeled batch genes | Inspect rather than trust QL F-test alone |
| Final estimates much lower than gene-wise everywhere | Excessive shrinkage; sample too small or trend too flat | Check `useEM`, robust hyperparameter setting |
| BCV decreases monotonically with mean | Correct in edgeR | Default trend |

A plot inspected before trusting results is worth a hundred lines of statistical safeguards.

## P-value Histogram (Run This Second)

**Goal:** Detect model misspecification or hidden batch before reporting any gene list.

**Approach:** Histogram of raw p-values; under a correctly specified null, uniform with a spike near zero.

```r
library(ggplot2)
ggplot(res_df, aes(x = pvalue)) +
    geom_histogram(bins = 50, fill = 'steelblue', color = 'white') +
    labs(x = 'P-value', y = 'Frequency', title = 'P-value distribution') +
    theme_bw()
```

| Shape | Meaning | Action |
|-------|---------|--------|
| Uniform + spike at 0 | Correctly specified | Proceed |
| U-shape (spikes at 0 AND 1) | Anti-conservative; hidden batch or unmodeled covariate | Add the missing covariate; re-fit |
| Depleted near 0, spike near 1 | Conservative; over-modeled or wrong dispersion | Simplify model; check dispersion plot |
| Spike only at p = 1 | Discrete artifact from very-low-count genes | Pre-filter more aggressively |

## MA Plot (LFC vs Mean)

**Goal:** Inspect the relationship between LFC and mean expression for normalization correctness and shrinkage effect.

**Approach:** `plotMA` (DESeq2) or `plotMD` (edgeR). Always pick `ylim` deliberately; default can flatten the signal.

```r
plotMA(res, ylim = c(-5, 5), main = 'MA plot (unshrunken)')

res_apeglm <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')
plotMA(res_apeglm, ylim = c(-5, 5), main = 'MA plot (apeglm-shrunken)')

plotMD(qlf, main = 'edgeR MD plot')
abline(h = c(-1, 1), col = 'blue', lty = 2)
```

| Pattern | Meaning |
|---------|---------|
| Symmetric cloud centered at LFC = 0 | Correct normalization |
| Cloud median clearly above or below 0 | Normalization failed (TMM/RLE assumption violated) -- see normalization skill |
| Funnel widening at low mean | Expected (low counts noisier) |
| Dramatic up/down asymmetry | Possibly real (large biological perturbation), possibly normalization failure -- cross-check |
| Discrete horizontal bands at low mean | Low-count artifacts; pre-filter more aggressively |

The apeglm-shrunken MA visually flattens the left side; the post-shrinkage cloud should be tighter at low means.

## Volcano with Shrunken LFC

**Goal:** Show effect size vs significance with honest fold changes.

**Approach:** Use a built-in renderer (EnhancedVolcano for quick publication-quality output) on shrunken LFCs. Always plot shrunken LFC; always set `max.overlaps = Inf` when labeling >10 genes -- the ggrepel default (10) silently drops labels. EnhancedVolcano accepts `max.overlaps` directly in 1.12+; version 1.10-1.11 has the older `maxoverlapsConnectors` argument (default 15); for either, falling back to `options(ggrepel.max.overlaps = Inf)` at the top of the script also works. For full ggplot2 customization (color schemes, faceting, label-set engineering), see `data-visualization/volcano-and-ma-plots`.

```r
library(EnhancedVolcano)

res_apeglm <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')

EnhancedVolcano(res_apeglm,
    lab = rownames(res_apeglm),
    x = 'log2FoldChange', y = 'pvalue',
    pCutoff = 0.05, FCcutoff = 1,
    title = 'Treatment vs Control',
    subtitle = 'Shrunken LFC (apeglm); unshrunken Wald p',
    max.overlaps = Inf)
```

## PCA on VST/rlog (Never on Raw Counts)

**Goal:** Show sample clustering by condition; detect batch effects, swaps, outliers.

**Approach:** Variance-stabilize first (VST or rlog), THEN PCA. Raw counts make PC1 = library size; log(counts+1) makes PC1 = mean expression. Neither carries biological signal until variance is stabilized.

```r
vsd <- vst(dds, blind = FALSE)
plotPCA(vsd, intgroup = c('condition', 'batch'))

pca_df <- plotPCA(vsd, intgroup = c('condition', 'batch'), returnData = TRUE)
percentVar <- round(100 * attr(pca_df, 'percentVar'))

library(ggplot2)
ggplot(pca_df, aes(PC1, PC2, color = condition, shape = batch)) +
    geom_point(size = 4) +
    xlab(paste0('PC1: ', percentVar[1], '% variance')) +
    ylab(paste0('PC2: ', percentVar[2], '% variance')) +
    theme_bw()

library(limma)
plotMDS(cpm(y, log = TRUE), col = as.numeric(group), pch = 16)
```

`blind=TRUE` (default for `vst()`) re-estimates dispersions ignoring the design -- appropriate for unbiased QC ("are samples consistent independent of design?"). `blind=FALSE` uses the fitted dispersions -- appropriate for downstream visualization where the design is settled. Modern DESeq2 vignette recommends `blind=FALSE` for any plot after the model is fit.

| PCA pattern | Interpretation | Action |
|-------------|----------------|--------|
| Clear separation by condition on PC1 or PC2 | Strong biological signal | Proceed |
| Separation by batch, not condition | Batch effect dominates | Include batch in design; DO NOT subtract before DE (see batch-correction Nygaard 2016) |
| One sample far from its group | Outlier or swap | Check library QC; sex check; somalier |
| Condition signal on PC3+, not PC1-PC2 | Subtle effect | May still find DE; review dispersion plot |
| Two distinct sample clusters not explained by metadata | Hidden covariate | Investigate processing date, lane, machine |

## Sample Distance Heatmap (for QC)

```r
library(pheatmap)
vsd <- vst(dds, blind = TRUE)
sd <- dist(t(assay(vsd)))
mat <- as.matrix(sd)
ann <- data.frame(condition = colData(dds)$condition,
                  row.names = colnames(dds))
pheatmap(mat, annotation_col = ann, annotation_row = ann,
         clustering_distance_rows = sd, clustering_distance_cols = sd,
         color = colorRampPalette(c('white', 'steelblue'))(100),
         main = 'Sample distance (vst blind)')
```

The diagonal should be dark; within-group samples should cluster. A within-group sample distant from its peers is a candidate for sample swap.

## Top-DE Heatmap and the Row-Scaling Trap

**Goal:** Show expression patterns of significant genes across samples for results figure.

**Approach:** Use `vst(blind=FALSE)`, select top genes (by adjusted p-value or MAD-robust variance), choose scaling deliberately.

```r
library(pheatmap)

sig <- rownames(subset(res, padj < 0.01))[1:50]
vsd <- vst(dds, blind = FALSE)
mat <- assay(vsd)[sig, ]

mat_scaled <- t(scale(t(mat)))

ann_col <- data.frame(condition = colData(dds)$condition,
                      batch     = colData(dds)$batch,
                      row.names = colnames(mat))

pheatmap(mat_scaled, annotation_col = ann_col,
         show_rownames = FALSE,
         clustering_distance_rows = 'correlation',
         clustering_distance_cols = 'correlation',
         color = colorRampPalette(c('blue', 'white', 'red'))(100),
         main = 'Top 50 DE genes (z-scored per gene)')
```

`scale='row'` (z-score per gene) is the conventional choice for "show me patterns". It DESTROYS absolute expression level information -- a gene at 5-7 with mean 6 looks identical to a gene at 10-1000. For pattern detection: correct. For QC heatmaps showing batch shifts: WRONG -- use `scale='none'` on `assay(vsd)`.

Top-variable-gene selection robustness:

```r
library(matrixStats)
vars_mad <- rowMads(assay(vsd))
top500 <- order(vars_mad, decreasing = TRUE)[1:500]
```

`rowMads` (median absolute deviation) is outlier-robust; `rowVars` is dominated by single-outlier-sample genes. For exploratory PCA of "top variable genes", MAD selection avoids artifacts.

## Per-gene Plot

```r
plotCounts(dds, gene = 'GENE_NAME', intgroup = 'condition')

d <- plotCounts(dds, gene = 'GENE_NAME', intgroup = c('condition','batch'),
                returnData = TRUE)
library(ggplot2)
ggplot(d, aes(x = condition, y = count, color = batch)) +
    geom_jitter(width = 0.1, size = 3) +
    scale_y_log10() +
    ggtitle('GENE_NAME') +
    theme_bw()
```

With n=3, the boxplot is misleading (3 points per box). Prefer `geom_jitter` over `geom_boxplot` at small n.

## UpSet for Multi-set Comparisons

For >3 DE gene sets (e.g., contrasts treated_drugA, treated_drugB, treated_drugC each vs control), Venn diagrams become unreadable. UpSet (Lex et al. 2014 *IEEE Trans Vis Comput Graph* 20:1983) scales:

```r
library(UpSetR)
upset(fromList(list(drugA = sig_drugA, drugB = sig_drugB, drugC = sig_drugC)))
```

## Per-Method Failure Modes

### Volcano with unshrunken LFC -- inflated story

**Trigger:** `ggplot(res_df, aes(x=log2FoldChange, ...))` without `lfcShrink()`; extreme dots at the corners are low-count genes.

**Mechanism:** Unshrunken MLE LFCs are dominated by very-low-count genes whose log ratios are noisy. The visual top-left and top-right corners look impressive but are artifacts.

**Symptom:** Top genes by abs(LFC) are obscure low-count genes; reviewer asks "why are these the top hits?"

**Fix:** `res_apeglm <- lfcShrink(dds, coef=..., type='apeglm')`; plot from `res_apeglm`. Label axis "shrunken log2 fold change (apeglm)".

### ggrepel `max.overlaps` silently drops labels

**Trigger:** `geom_text_repel(data = top30, aes(label = gene))`; only 10 labels render.

**Mechanism:** Default `max.overlaps = 10`; warning printed but easily missed in a knitr/Quarto render.

**Symptom:** Reviewer asks "where is gene X?"; it was in `top30` but did not render.

**Fix:** `geom_text_repel(..., max.overlaps = Inf)` or `options(ggrepel.max.overlaps = Inf)` at top of script.

### PCA shows batch, not condition

**Trigger:** `plotPCA(vsd, intgroup='batch')` cleanly separates batches; `intgroup='condition'` does not separate.

**Mechanism:** Batch variance exceeds condition variance.

**Symptom:** Treatment effect looks weak; DE p-values inflated if batch not in design.

**Fix:** Include batch in design (`design = ~ batch + condition`). DO NOT use `removeBatchEffect` then re-do DE on corrected counts (Nygaard 2016 cardinal sin -- see `batch-correction`). For VISUALIZATION only, `removeBatchEffect` is OK.

### Heatmap row-scaling hid a sample-level shift

**Trigger:** QC heatmap with `scale='row'` looks consistent within group; downstream PCA shows clear sample outlier.

**Mechanism:** z-score per gene removes per-sample additive shifts. A sample that's globally inflated 1.5x looks identical to peers after row scaling.

**Symptom:** "The heatmap looked fine but PCA shows a problem."

**Fix:** For QC heatmaps, use `scale = 'none'` on `assay(vsd)` directly. For result heatmaps after QC is clean, `scale = 'row'` is the appropriate choice for pattern emphasis.

### Top-N-by-rowVars dominated by single-outlier-sample genes

**Trigger:** "Top 500 variable genes" PCA shows a striped pattern, one or two samples driving the spread.

**Mechanism:** `rowVars` is squared-deviation; one outlier sample of one gene inflates that gene's "variance" massively.

**Symptom:** Top variable gene list includes many genes where N-1 samples are flat and one sample is extreme.

**Fix:** `matrixStats::rowMads()` for MAD-based selection; or `genefilter::rowQ()`.

## Common errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `plotPCA` reports only 2 PCs | DESeq2 `plotPCA` is hard-coded to PC1/PC2 | Use `prcomp(t(assay(vsd)))` and plot any pair |
| PCA cloud collapses to one point | Forgot to log-transform; raw counts plotted | `vst(dds)` first |
| All MA-plot points red | `alpha` set too high or sig-flag bug | Verify `alpha`; check `padj` vs `pvalue` in flag |
| `pheatmap` complains "infinite values" | NA / Inf in scaled matrix; gene with zero variance | Remove zero-variance rows before scaling |
| Volcano axis labels obscured | Default ggplot theme too compact | `theme_bw(base_size = 14)` |
| `plotCounts` says gene not found | Wrong ID type (symbol vs Ensembl) | Match `rownames(dds)` exactly |
| `vst()` errors with very low gene count post-filter | Default `nsub=1000` exceeds available genes | Lower `nsub` (e.g., `vst(dds, nsub=500)`) |

## References

- Anders S, Huber W. 2010. Differential expression analysis for sequence count data. *Genome Biol* 11(10):R106. doi:10.1186/gb-2010-11-10-r106
- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biol* 15(12):550. doi:10.1186/s13059-014-0550-8
- Zhu A, Ibrahim JG, Love MI. 2019. Heavy-tailed prior distributions for sequence count data: removing the noise and preserving large differences. *Bioinformatics* 35(12):2084-2092. doi:10.1093/bioinformatics/bty895
- Robinson MD, McCarthy DJ, Smyth GK. 2010. edgeR: a Bioconductor package for differential expression analysis of digital gene expression data. *Bioinformatics* 26(1):139-140. doi:10.1093/bioinformatics/btp616
- Lex A, Gehlenborg N, Strobelt H, Vuillemot R, Pfister H. 2014. UpSet: Visualization of Intersecting Sets. *IEEE Trans Vis Comput Graph* 20(12):1983-1992. doi:10.1109/TVCG.2014.2346248
- Schurch NJ et al. 2016. How many biological replicates are needed in an RNA-seq experiment and which differential expression tool should you use? *RNA* 22(6):839-851. doi:10.1261/rna.053959.115
- Nygaard V, Rødland EA, Hovig E. 2016. Methods that remove batch effects while retaining group differences may lead to exaggerated confidence in downstream analyses. *Biostatistics* 17(1):29-39. doi:10.1093/biostatistics/kxv027

## Related Skills

- deseq2-basics - Generates the `dds` / `res` objects plotted here; `vst`/`rlog` choice
- edger-basics - Generates `y` / `qlf` for plotMD, plotBCV, plotMDS
- de-results - p-value histogram, padj=NA diagnosis informs what to plot
- batch-correction - removeBatchEffect for visualization only (never as DE input)
- expression-matrix/normalization - VST vs rlog vs log-CPM mechanics
- data-visualization/volcano-and-ma-plots - Full custom volcano/MA with apeglm + ggrepel
- data-visualization/dimensionality-reduction-plots - PCA, UMAP, t-SNE customization
- data-visualization/heatmaps-clustering - pheatmap and ComplexHeatmap recipes
- data-visualization/upset-plots - UpSet plot customization
<!-- END FILE: differential-expression/de-visualization/SKILL.md -->

## 子目录：differential-expression/deseq2-basics

<!-- BEGIN FILE: differential-expression/deseq2-basics/SKILL.md -->
---
name: bio-differential-expression-deseq2-basics
description: Performs differential expression on bulk RNA-seq count data with DESeq2's negative-binomial GLM, Wald and LRT testing, apeglm/ashr/normal LFC shrinkage, independent filtering, Cook's outlier handling, VST/rlog transforms, and design formulas including paired, batch, and interaction terms. Use when running bulk DE, choosing DESeq2 over edgeR or limma-voom, building a paired or interaction design, applying LFC shrinkage for ranking or GSEA, choosing Wald vs LRT, troubleshooting padj=NA, picking VST vs rlog, importing salmon/kallisto via tximport, or analyzing prokaryotic RNA-seq.
tool_type: r
primary_tool: DESeq2
---

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, apeglm 1.28+, ashr 2.2+, IHW 1.34+, tximport 1.30+, edgeR 4.0+ (for cross-comparison), PyDESeq2 0.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# DESeq2 Basics

**"Find differentially expressed genes between conditions"** -> Fit a negative-binomial GLM per gene with shared dispersion shrinkage, test the coefficient of interest (Wald) or the joint effect of a factor (LRT), and report a shrunken effect-size estimate for ranking.

## The Single Most Important Modern Insight -- Shrunken LFC and the Wald p-value come from different models

`lfcShrink()` returns LFCs from a Bayesian posterior with apeglm/ashr/normal priors, BUT the p-value column it carries forward is still the **unshrunken Wald p-value** from `results()`. This is a deliberate design choice (Zhu, Ibrahim, Love 2019 *Bioinformatics* 35:2084) -- the shrunken estimate is for ranking and visualization; the p-value is for inference. Reporting "shrunken LFC = 0.4, padj = 1e-8" mixes two models, which is fine because both are correct for their stated purpose. What is NOT fine: using the shrunken LFC in a downstream filter and then claiming FDR control on that filter (it has none). For threshold-based FDR claims, use `lfcThreshold=` or TREAT (`glmTreat` in edgeR).

A second consequence: `results(dds)` with no `name=` or `contrast=` argument silently returns the **last coefficient in `resultsNames(dds)`** -- which depends on factor level order and design formula order. Always specify the contrast explicitly. Tutorials that hard-code `results(dds)` are setting an example that breaks the moment another factor is added.

## Algorithmic Taxonomy

| Test / estimator | What it tests | When mandatory | Failure mode |
|------------------|---------------|----------------|--------------|
| Wald | One coefficient = 0 | Two-level factor or single contrast | Anti-conservative with many low-count outliers |
| LRT (`test='LRT'`, `reduced=`) | Joint effect of dropped terms (>=1 df) | Multi-level factor, omnibus, interaction with >1 df | Reports LFC of the LAST coefficient, not omnibus -- read p-value but never report the LFC as "the effect" |
| `lfcShrink(type='apeglm')` (Zhu 2019) | Posterior LFC under heavy-tailed Cauchy prior | DEFAULT for ranking and visualization | Requires `coef=`; cannot use `contrast=` or numeric vectors |
| `lfcShrink(type='ashr')` (Stephens 2017) | Posterior LFC under unimodal prior; reports `lfsr`/`svalue` with `svalue=TRUE` | Arbitrary contrasts via `contrast=` | Slightly different inferential frame (sign-error rather than null-FDR) |
| `lfcShrink(type='normal')` | Posterior LFC under zero-centered normal; accepts `coef=` or `contrast=` (with `res=`) | Quasi-deprecated since v1.16; only path to get shrunken p-values | Cannot be used with formulas containing interaction terms |
| TREAT / `lfcThreshold=` (McCarthy & Smyth 2009) | LFC magnitude exceeds threshold tau | Want FDR control for "|LFC| > 1.5x" claims | Conservative; use only when threshold is biologically pre-specified |

## Decision Tree by Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Two-group bulk RNA-seq, n>=3/group | `DESeq()` + `results(name=...)` + `lfcShrink(coef=..., type='apeglm')` | Modern default; apeglm is the right prior |
| Factor with 3+ levels, "any change" question | `DESeq(test='LRT', reduced=~1)`; read padj only | Wald + p-value combining is wrong |
| Interaction `~ genotype * treatment` | Build combined factor `group = paste(genotype, treatment)` and design `~ 0 + group`; contrast pairs of interest | Avoids the resultsNames trap; works with apeglm via relevel |
| Paired design (tumor/normal same patient) | `~ patient + tissue`; pairing variable FIRST | Absorbs subject variability; n_paired effective sample size |
| Salmon/kallisto input | `tximport()` -> `DESeqDataSetFromTximport()` | Carries length offsets automatically; `DESeqDataSetFromMatrix(round(...))` loses length correction |
| n=2/group, no choice | Continue but report results as exploratory; consider edgeR QL F-test as sensitivity | Schurch 2016 *RNA* 22:839: all tools miss 20-40% of true positives at n=3 |
| Single-cell pseudobulk (counts aggregated per donor) | DESeq2 standard pipeline on pseudobulk matrix | Crowell 2020 *Nat Commun* 11:6077: pseudobulk avoids the FDR inflation of cell-level DE |
| Many DE genes expected (>50% of genome) | `estimateSizeFactors(controlGenes=stable)` or spike-in normalization | Median-of-ratios assumes most genes unchanged |
| GSEA preranked input | Shrunken LFC OR `stat` (Wald Z) as the rank | Unshrunken LFC dominated by low-count noise |
| Cross-sample heatmap, PCA, ML feature | `vst(dds, blind=FALSE)` (or `rlog` if n<30 and library sizes vary >4x) | Raw counts make PC1 = library size |

## Standard Workflow

**Goal:** Take a raw integer count matrix and a sample table to a ranked, shrunken DE result table.

**Approach:** Construct DESeqDataSet with the design formula, set reference levels explicitly, run the pipeline, extract by explicit contrast, shrink for downstream use.

```r
library(DESeq2)
library(apeglm)

dds <- DESeqDataSetFromMatrix(countData = counts, colData = coldata, design = ~ condition)
dds$condition <- relevel(dds$condition, ref = 'control')

keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep, ]

dds <- DESeq(dds)
resultsNames(dds)

res <- results(dds, name = 'condition_treated_vs_control', alpha = 0.05)
res_shrunk <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')

summary(res)
sig <- subset(res, padj < 0.05)
```

The reference level fix is non-cosmetic: DESeq2 picks alphabetically if not told otherwise, so `c('Treated','Untreated')` makes 'Treated' the reference and the LFC reads inverted. Set it BEFORE `DESeq()`.

## Tximport (Salmon / kallisto / RSEM)

For salmon/kallisto/RSEM input, use `DESeqDataSetFromTximport()` which carries the per-sample length matrix as an offset automatically:

```r
library(tximport)
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene)
dds <- DESeqDataSetFromTximport(txi, colData = samples, design = ~ condition)
dds <- DESeq(dds)
```

The `tximport(..., countsFromAbundance='lengthScaledTPM')` form is for limma-voom (no offset mechanism). Full mechanics, the four `countsFromAbundance` options, RSEM zero-length traps, and tximeta provenance: see `expression-matrix/counts-ingest`.

## Design Formulas and the resultsNames Trap

**Goal:** Encode batch, paired, and interaction structure correctly and extract the intended contrast.

**Approach:** Put the variable of interest LAST for readability, but never trust the default `results(dds)` -- inspect `resultsNames(dds)` and pass `name=` or `contrast=` explicitly.

```r
design(dds) <- ~ batch + condition
dds <- DESeq(dds)
resultsNames(dds)
# "Intercept" "batch_B_vs_A" "condition_treated_vs_control"

res <- results(dds, name = 'condition_treated_vs_control')
```

Interaction design with the canonical trap:

```r
design(dds) <- ~ genotype + treatment + genotype:treatment
dds <- DESeq(dds)
resultsNames(dds)
# "Intercept" "genotype_KO_vs_WT" "treatment_drug_vs_vehicle" "genotypeKO.treatmentdrug"
```

- `results(dds, name='treatment_drug_vs_vehicle')` returns the drug effect IN THE WT REFERENCE only, NOT a marginal average. This is the single most common misinterpretation.
- `results(dds, name='genotypeKO.treatmentdrug')` returns the DIFFERENCE in drug effect between KO and WT.
- Drug effect in KO requires summing: `results(dds, contrast=list(c('treatment_drug_vs_vehicle','genotypeKO.treatmentdrug')))`.

Cleaner alternative for interactions when many pairwise contrasts are needed: combined factor + `~ 0 + group`.

```r
dds$group <- factor(paste(dds$genotype, dds$treatment, sep = '_'))
design(dds) <- ~ 0 + group
dds <- DESeq(dds)
res_drug_in_ko <- results(dds, contrast = c('group', 'KO_drug', 'KO_vehicle'))
```

## Wald vs LRT

**Goal:** Choose Wald for single-coefficient hypotheses, LRT for joint hypotheses involving more than 1 df.

**Approach:** Wald is default. LRT is mandatory for multi-level factors tested as "any change", interactions with >1 df, and ANOVA-style omnibus tests. With LRT, the reported LFC is for the LAST coefficient in `resultsNames(dds)` -- not the omnibus effect.

```r
dds <- DESeq(dds, test = 'LRT', reduced = ~ batch)
res_lrt <- results(dds)
# res_lrt$padj is the LRT joint p-value (correct).
# res_lrt$log2FoldChange is for the last coefficient in resultsNames -- NOT an omnibus summary.
```

When reporting LRT results, name what the LFC actually represents or extract specific Wald coefficients per level for the effect-size table.

## LFC Shrinkage -- Three Flavors, Three Failure Modes

**Goal:** Get a stable effect-size estimate appropriate for ranking, GSEA input, volcano-plot x-axis, and reporting.

**Approach:** Default to apeglm. Switch to ashr when arbitrary contrasts are needed. Never use normal for new analyses.

```r
res_apeglm <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')
res_ashr   <- lfcShrink(dds, contrast = c('condition','treated','control'), type = 'ashr')
```

| Method | Prior | Accepts | Use when |
|--------|-------|---------|----------|
| apeglm | Cauchy (heavy-tailed) | `coef=` only | Default; preserves large effects, suppresses low-count noise |
| ashr | Unimodal scale-mixture | `coef=` or `contrast=` (incl. numeric) | Need contrast= for interaction sums or pairwise from `~ 0 + group` |
| normal | Zero-centered normal | `coef=` only; not interaction designs | Only when the old shrunken p-value is required (legacy) |

The apeglm-cannot-use-contrast footgun: if the question is "drug effect in KO" from `~ genotype * treatment`, apeglm cannot directly shrink that contrast. Workarounds: (a) rebuild as combined factor `~ 0 + group` and relevel so the desired comparison is a coefficient; (b) use ashr; (c) accept the unshrunken LFC for that one comparison.

p-values do NOT change when shrinking. `lfcShrink()` preserves the Wald p-value from `results()`. See the Single Most Important Insight at the top.

## Independent Filtering, Cook's Outliers, padj=NA

`padj = NA` has three distinct causes (independent filtering, Cook's outlier, all-zero in a group), each with a different remediation -- see `de-results` for the full diagnostic table, IHW alternative, and recovery code.

Two DESeq2-specific points worth knowing at this layer:

- Cook's distance filtering is NOT computed for continuous covariates -- a continuous-covariate analysis has effectively no automatic outlier filtering. Disable Cook's only when the outlier IS the signal (`results(dds, cooksCutoff = FALSE)`). At n>=7 per group, `DESeq()` REPLACES outliers via `replaceOutliers()` and refits (`minReplicatesForReplace = 7`).
- Pre-filtering (`rowSums(counts(dds)) >= 10`) is for memory and speed ONLY. It does NOT replace independent filtering, which operates downstream at `results()` time. Independent filtering can be swapped for IHW via `results(dds, filterFun = ihw)`.

## VST vs rlog vs normTransform (Visualization Only)

**Goal:** Produce homoskedastic log2-scale counts for PCA, heatmaps, clustering, ML features.

**Approach:** Use `vst()` by default. Switch to `rlog()` only for n<30 with size factors varying >4x. Never use `normTransform()` for distance-based plots. Never use VST/rlog values as input to DE.

```r
vsd <- vst(dds, blind = FALSE)
rld <- rlog(dds, blind = FALSE)
```

The `vst()` function default is `blind=TRUE`, but the current DESeq2 vignette recommends `blind=FALSE` for any downstream visualization AFTER the model is fit (it uses the design when fitting dispersions; appropriate when the design is already settled). Reserve `blind=TRUE` for unsupervised QC where the design should not influence the transformation (e.g., "is this sample consistent with its group?"). The vignette has flip-flopped over the years on which to recommend by default -- pass `blind=` explicitly.

`vst()` uses 1000 most-variable genes to fit the dispersion trend by default. With <1000 genes after filtering, set `nsub` lower.

## betaPrior Deprecation Timeline

DESeq2 v1.0-v1.15: `betaPrior = TRUE` was the default. Shrinkage was baked in and p-values were computed on the shrunken estimates. v1.16 (2017) flipped the default to `FALSE` and introduced `lfcShrink()`. Today: `betaPrior = TRUE` is quasi-deprecated and is the ONLY path to a p-value of the shrunken estimate. Most users do not want this. `lfcShrink()` with apeglm and the unshrunken Wald p-value is the modern compromise.

The contrast= vs name= numerical difference that older tutorials describe was specific to `betaPrior = TRUE`. With the current default, `name=` and `contrast=` for the same comparison return identical LFCs.

## Size Factor Alternatives

`estimateSizeFactors()` defaults to `type='ratio'` (median-of-ratios). Edge cases:

| Situation | Use |
|-----------|-----|
| Zero counts in some samples for many genes | `type='poscounts'` -- uses only positive entries per gene |
| Very small libraries, hard to converge | `type='iterate'` |
| Spike-ins (ERCC) or known stable housekeeping genes | `controlGenes = indices` |
| Majority-DE biology (prokaryotic stress, viral host shutoff, MYC amplification) | `controlGenes` with curated stable genes; or spike-in SBN (Jiang 2011 *Genome Res* 21:1543) |

Single-cell pseudobulk: most genes have zeros across donors, so `type='poscounts'` is often required for pseudobulk DESeq2.

## Per-Method Failure Modes

### apeglm refuses arbitrary contrasts

**Trigger:** Question of the form "drug effect in KO genotype" from `~ genotype * treatment`; user tries `lfcShrink(dds, contrast=list(...), type='apeglm')`.

**Mechanism:** apeglm fits per-coefficient priors. A numeric or list contrast is a linear combination of coefficients, not a coefficient -- no prior to apply.

**Symptom:** Error: "type='apeglm' shrinkage only for use with 'coef'"

**Fix:** Rebuild design as `~ 0 + group` with `group = paste(genotype, treatment)`, relevel so the comparison is a coefficient, refit. Or use `type='ashr'` which accepts contrasts.

### LRT reports the wrong LFC

**Trigger:** Multi-level factor analyzed with `DESeq(dds, test='LRT', reduced=~1)`; user reports the `log2FoldChange` column as "the effect".

**Mechanism:** The LRT p-value is the omnibus test of "any difference among levels". The LFC reported by `results()` after LRT is for the LAST coefficient in `resultsNames(dds)`, which is one specific level-vs-reference comparison.

**Symptom:** A 4-level factor produces a single LFC value per gene; reviewer asks "the effect of which condition?"

**Fix:** Treat LRT padj as a screen for "any change". For effect sizes, extract per-level Wald coefficients individually via `results(dds, name='<specific coefficient>')` for each non-reference level.

### Cook's silences the gene of interest

**Trigger:** Rare-disease cohort or CNV-amplified patient where ONE sample drives the biology; that gene has `padj=NA`.

**Mechanism:** Cook's distance flagged the patient as an outlier and zeroed the gene's p-value (or replaced its counts if n>=7).

**Symptom:** A gene of clear biological interest comes back as NA in the results table even though the count matrix shows the expected pattern.

**Fix:** `results(dds, cooksCutoff = FALSE)`. Optionally cross-validate the result by running a sensitivity analysis with and without the outlier sample.

### Independent filtering kills the master regulator

**Trigger:** A transcription factor expressed at ~10 counts but consistently across all samples shows `padj=NA` despite obvious biology.

**Mechanism:** baseMean is below the data-driven independent filtering threshold; the gene was excluded from FDR adjustment.

**Symptom:** Low-count genes with clean signal end up NA.

**Fix:** `results(dds, independentFiltering = FALSE)`; or `filterFun = ihw` from the IHW package (often less aggressive on low-count genes).

### Parametric dispersion-mean trend doesn't fit the cloud

**Trigger:** `plotDispEsts(dds)` shows the red parametric trend curve nowhere near the cloud of gene-wise (blue) and final (black) dispersion estimates.

**Mechanism:** Default `fitType='parametric'` assumes `dispersion ~ a/mean + b`. Fails when the experiment has very few samples per group with highly heterogeneous biology, many very-low-count genes pulling the trend, or a continuous covariate driving large variability.

**Symptom:** Curved trend that doesn't match the cloud; mismatch shows up most clearly in low-baseMean genes.

**Fix:** Refit with `DESeq(dds, fitType='local')` (local regression) or `fitType='mean'` (flat trend); compare `plotDispEsts` between fits and pick the one tracking the cloud. Falling back to `'mean'` is a sign the data is unusual; investigate before trusting results.

### Median-of-ratios fails on prokaryotic stress

**Trigger:** Bacterial RNA-seq under stress where >50% of genes change in one direction; PCA shows huge global shift.

**Mechanism:** Median-of-ratios assumes most genes are not DE. Under massive global perturbation, the reference is dominated by DE genes; size factors absorb the biology.

**Symptom:** MA plot shows the bulk cloud shifted off zero; reported fold changes don't match qPCR.

**Fix:** Use `controlGenes` with curated stable housekeeping genes; or spike-in normalization (Jiang 2011); or RUVg with negative controls.

## PyDESeq2 (Python alternative)

```python
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

dds = DeseqDataSet(counts=count_df, metadata=metadata, design='~condition')
dds.deseq2()
stat_res = DeseqStats(dds, contrast=('condition', 'treated', 'control'))
stat_res.summary()
results_df = stat_res.results_df
```

PyDESeq2 0.5+ supports Wald, multi-factor designs, and apeglm shrinkage. No LRT yet. Results are numerically close to R DESeq2 but with small differences from MLE solver choice.

## Prokaryotic RNA-seq

- Non-spliced aligners (BWA-MEM, Bowtie2) -- no introns.
- Polycistronic operons cause read-through between adjacent genes; confirm gene boundaries in the GFF.
- rRNA depletion essential (80-95% rRNA without poly-A selection, which prokaryotes lack anyway).
- Median-of-ratios fails under stress (see failure mode above) -- use `controlGenes` or spike-ins.
- KEGG organism codes are strain-specific (e.g., `pae` for P. aeruginosa PAO1): `clusterProfiler::search_kegg_organism()`.
- Annotation comes from Prokka or Bakta GFF; Ensembl/biomaRt are eukaryote-only.

## Common errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `design matrix not full rank` | Confounded covariates | `alias(model.matrix(design, coldata))$Complete` to find the redundant column |
| `counts matrix should be integers` | Salmon/kallisto/RSEM counts are fractional | Use `DESeqDataSetFromTximport()` -- it rounds AND carries length offsets |
| Wrong sign of LFC vs expected | Reference level set alphabetically | `relevel()` BEFORE `DESeq()` |
| `padj = NA` for biologically meaningful gene | Independent filtering or Cook's outlier | See padj=NA section |
| LRT LFC doesn't match Wald LFC for the same comparison | LRT reports last coefficient; Wald reports the named coefficient | Extract specific Wald per level for the effect size |
| `summary(res)` shows fewer DE genes than expected | `summary()` default `alpha=0.1`, NOT the alpha passed to `results()` | `summary(res, alpha = 0.05)` |

## References

- Anders S, Huber W. 2010. Differential expression analysis for sequence count data. *Genome Biol* 11(10):R106. doi:10.1186/gb-2010-11-10-r106
- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biol* 15(12):550. doi:10.1186/s13059-014-0550-8
- Zhu A, Ibrahim JG, Love MI. 2019. Heavy-tailed prior distributions for sequence count data: removing the noise and preserving large differences. *Bioinformatics* 35(12):2084-2092. doi:10.1093/bioinformatics/bty895
- Stephens M. 2017. False discovery rates: a new deal. *Biostatistics* 18(2):275-294. doi:10.1093/biostatistics/kxw041
- Ignatiadis N, Klaus B, Zaugg JB, Huber W. 2016. Data-driven hypothesis weighting increases detection power in genome-scale multiple testing. *Nat Methods* 13(7):577-580. doi:10.1038/nmeth.3885
- Bourgon R, Gentleman R, Huber W. 2010. Independent filtering increases detection power for high-throughput experiments. *PNAS* 107(21):9546-9551. doi:10.1073/pnas.0914005107
- McCarthy DJ, Smyth GK. 2009. Testing significance relative to a fold-change threshold is a TREAT. *Bioinformatics* 25(6):765-771. doi:10.1093/bioinformatics/btp053
- Soneson C, Love MI, Robinson MD. 2015. Differential analyses for RNA-seq: transcript-level estimates improve gene-level inferences. *F1000Res* 4:1521. doi:10.12688/f1000research.7563.2
- Schurch NJ et al. 2016. How many biological replicates are needed in an RNA-seq experiment and which differential expression tool should you use? *RNA* 22(6):839-851. doi:10.1261/rna.053959.115
- Crowell HL et al. 2020. muscat detects subpopulation-specific state transitions from multi-sample multi-condition single-cell transcriptomics data. *Nat Commun* 11:6077. doi:10.1038/s41467-020-19894-4
- Jiang L et al. 2011. Synthetic spike-in standards for RNA-seq experiments. *Genome Res* 21(9):1543-1551. doi:10.1101/gr.121095.111

## Related Skills

- edger-basics - Cross-check or use when n<5/group; QL F-test framework
- de-results - padj=NA handling, IHW, TREAT, GSEA input preparation, gene annotation
- de-visualization - MA, volcano (with shrunken LFC), PCA, heatmap, dispersion plot
- batch-correction - Include batch in design vs Nygaard 2016 cardinal sin
- timeseries-de - DESeq2 LRT with splines for time-course
- expression-matrix/counts-ingest - tximport, featureCounts, STAR output decisions
- expression-matrix/normalization - RLE/TMM/VST/rlog mechanics and failure modes
- expression-matrix/metadata-joins - Reference level, paired design, interaction parameterization
- expression-matrix/gene-id-mapping - Annotating DE results with symbols
- rna-quantification/tximport-workflow - Detailed tximport mechanics
- pathway-analysis/gsea - Ranked-list input from DE
- pathway-analysis/go-enrichment - ORA with proper background
- data-visualization/volcano-and-ma-plots - Custom volcano with apeglm-shrunken LFC
<!-- END FILE: differential-expression/deseq2-basics/SKILL.md -->

## 子目录：differential-expression/edger-basics

<!-- BEGIN FILE: differential-expression/edger-basics/SKILL.md -->
---
name: bio-differential-expression-edger-basics
description: Performs differential expression on bulk RNA-seq count data with edgeR's negative-binomial GLM and quasi-likelihood F-test framework. Covers DGEList construction, filterByExpr, TMM/TMMwsp normalization, robust dispersion estimation, glmQLFit/glmQLFTest, TREAT for magnitude-bounded hypotheses, contrasts via no-intercept designs, voom and voomWithQualityWeights for heterogeneous samples, and the edgeR v4 bias-corrected APL changes. Use when running bulk DE with edgeR, choosing edgeR over DESeq2 (small n, transcript DE via catchSalmon, large samples), needing TREAT for a fold-change-threshold hypothesis, troubleshooting v3-to-v4 reproducibility, building paired or interaction designs, or handling library-quality heterogeneity.
tool_type: r
primary_tool: edgeR
---

## Version Compatibility

Reference examples tested with: edgeR 4.0+, limma 3.58+, statmod 1.5+ (for voom internals), tximport 1.30+ (for catchSalmon path)

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# edgeR Basics

**"Find differentially expressed genes between conditions"** -> Fit a negative-binomial GLM per gene with empirical-Bayes-moderated dispersions, test coefficients with the quasi-likelihood F-test (proper finite-sample FPR control), and report ranked DE lists.

## The Single Most Important Modern Insight -- edgeR v4 changed the QL framework and `legacy=FALSE` is now default

Chen, Chen, Lun, Baldoni, Smyth (2025) *Nucleic Acids Res* 53(2):gkaf018 introduced a bias-corrected adjusted profile likelihood (APL) for dispersion estimation that handles small/zero counts properly, and reworked the QL framework. `glmQLFit()` in v4 takes `legacy=FALSE` by default. Old (v3) pipelines that worked perfectly in 2023 now produce subtly different numbers in 2025 -- not wrong, just different. If a tutorial result doesn't match, check which version was used; set `legacy=TRUE` to reproduce v3 exactly OR (preferred) re-run with v4 defaults and accept the new -- better -- numbers.

Two other v4 changes worth knowing: (1) `calcNormFactors()` is deprecated in favor of `normLibSizes()` (same function, new name); (2) `method='TMM'` remains the documented default; `method='TMMwsp'` (TMM with singleton pairing) is an alternative introduced for samples with many zeros and is the preferred choice for sparse / low-count data. Pass `method=` explicitly for reproducibility. Old names still work, so old scripts run, but new code should use the new names.

The choice between Wald-equivalent (`glmLRT`) and QL-F (`glmQLFTest`) is not a stylistic preference: `glmQLFTest` is the modern default because it accounts for uncertainty in the dispersion estimate via an additional QL dispersion. `glmLRT` is anti-conservative with small n. The two p-values differ -- `glmQLFTest` p-values are typically >= `glmLRT` p-values for the same model (the second-stage QL dispersion correction is usually >= 1).

## Algorithmic Taxonomy

| Test | What it does | When mandatory | Failure mode |
|------|--------------|----------------|--------------|
| QL F-test (`glmQLFit` + `glmQLFTest`) | NB GLM with second-stage QL dispersion to model dispersion uncertainty | DEFAULT for any modern bulk DE | None within design assumptions |
| LRT (`glmFit` + `glmLRT`) | Likelihood-ratio of nested GLMs using point dispersion estimate | Only when n>=10/group AND simple design AND no QL F-test available | Anti-conservative with small n -- inflated false positives |
| Exact test (`exactTest`) | Conditional NB test for two groups, no covariates | Legacy; one-factor two-group ONLY | Cannot adjust for batch or covariates |
| TREAT (`glmTreat`) | Tests H0: |LFC| <= tau vs HA: |LFC| > tau (McCarthy & Smyth 2009) | Want FDR control for "biologically meaningful fold change" claim | Conservative; tau must be pre-specified |
| voom + lmFit + eBayes | Linear model with empirical-Bayes moderation on voom-weighted log-CPM | Heterogeneous library sizes (>3x); samples with widely varying quality | Assumes log-normal-after-weighting; less direct count model |
| voomWithQualityWeights | voom + per-sample quality weights from arrayWeights (Liu 2015) | Some samples markedly worse quality (low RIN, contamination) | With very small n, sample weights are noisy |

## Decision Tree by Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Standard bulk RNA-seq, n>=3/group, modern script | `filterByExpr -> normLibSizes -> estimateDisp(robust=TRUE) -> glmQLFit(robust=TRUE) -> glmQLFTest` | Modern default with proper FPR control |
| n=2-3/group | edgeR QL F-test (over DESeq2) | Schurch 2016 *RNA* 22:839 + edgeR v4 changes: QL is the tightest FPR control at small n |
| Library sizes vary >3x or RIN heterogeneous | `voom` or `voomWithQualityWeights` + lmFit + eBayes | Precision weights downweight noisy observations per sample |
| Pre-specified biologically meaningful fold-change threshold | `glmTreat(fit, coef=..., lfc=log2(1.5))` | Post-hoc filtering by |LFC| does NOT control FDR for the magnitude hypothesis |
| Multi-group, "any change" omnibus | `glmQLFTest(fit, coef=2:k)` | Joint F-test on multiple coefficients |
| Multi-group, all pairwise contrasts | `~ 0 + group` parameterization + `makeContrasts` | Clean, readable contrasts |
| Transcript-level DE (DTE) | `catchSalmon()` / `catchKallisto()` -> `DGEList` with overdispersion | Baldoni 2024 *NAR* 52:e13: properly handles inferential variance |
| Cross-tool sanity check | Run DESeq2 in parallel; expect >=70% overlap at top 500 | <60% overlap suggests modeling problem, not tool difference |
| Single-cell pseudobulk | Aggregate counts per donor; standard edgeR QL pipeline | Crowell 2020 *Nat Commun* 11:6077: pseudobulk avoids the FDR inflation of cell-level DE |
| Reproducing pre-2025 result | `glmQLFit(legacy=TRUE)` | edgeR v4 introduced bias-corrected APL with `legacy=FALSE` default; v3 was slightly biased |

## Standard Workflow

**Goal:** Take a raw integer count matrix and group labels to a ranked DE table with proper finite-sample FPR control.

**Approach:** DGEList -> design-aware filtering -> TMM normalization (or TMMwsp for sparse data) -> robust dispersion estimation -> QL fit with robust dispersion shrinkage -> QL F-test on the coefficient of interest -> ranked table.

```r
library(edgeR)
library(limma)

y <- DGEList(counts = counts, group = group)
design <- model.matrix(~ group)

keep <- filterByExpr(y, design)
y <- y[keep, , keep.lib.sizes = FALSE]

y <- normLibSizes(y)
y <- estimateDisp(y, design, robust = TRUE)
plotBCV(y)

fit <- glmQLFit(y, design, robust = TRUE)
qlf <- glmQLFTest(fit, coef = 2)

topTags(qlf, n = 20)
all_de <- topTags(qlf, n = Inf, sort.by = 'none')$table
```

The `robust = TRUE` flags propagate Phipson, Lee, Majewski, Alexander, Smyth (2016) *Ann Appl Stat* 10:946 robust hyperparameter estimation through both the NB dispersion shrinkage (`estimateDisp`) AND the QL dispersion shrinkage (`glmQLFit`). Set BOTH; setting only one is the single most common omission. The default `robust=FALSE` is a relic.

## Filtering -- `filterByExpr` Internals

**Goal:** Remove genes with insufficient expression to reduce noise and multiple-testing burden, in a design-aware way.

**Approach:** `filterByExpr(y, design)` uses the smallest group size from the design matrix to set the minimum number of samples; threshold is CPM >= `min.count / median.lib.size * 1e6` AND total count >= `min.total.count`.

Default parameters: `min.count = 10`, `min.total.count = 15`, `large.n = 10`, `min.prop = 0.7`.

```r
keep <- filterByExpr(y, design)
y <- y[keep, , keep.lib.sizes = FALSE]
```

Filter ONCE, before normalization and dispersion estimation. Filtering after `estimateDisp` invalidates the trended dispersion (the trend was fit on the now-smaller gene set). edgeR has no automatic independent filtering like DESeq2 -- skipping `filterByExpr` is the single biggest reason an edgeR analysis underperforms a comparable DESeq2 analysis.

## Normalization -- TMM/TMMwsp Is an Offset, Not a Division

**Goal:** Correct for library composition bias (the "few genes consume disproportionate reads" problem) via a per-sample scaling factor.

**Approach:** `normLibSizes(y)` defaults to `method='TMM'` in v4 (same as v3); `method='TMMwsp'` is the preferred alternative for sparse / single-cell-pseudobulk data with many zeros. Result is a vector of normalization factors stored in `y$samples$norm.factors`; the effective library size is `lib.size * norm.factors`. Counts are NOT divided.

```r
y <- normLibSizes(y)
y$samples$norm.factors

cpm_vis <- cpm(y, normalized.lib.sizes = TRUE)
log_cpm <- cpm(y, log = TRUE, prior.count = 2)
```

The factor enters the GLM as part of the offset. Running TMM on pre-normalized values is wrong (and silent -- gives wrong numbers without error). `prior.count = 2` is the modern edgeR default for `cpm(log=TRUE)`; smaller priors (0.25) make low-count log values noisy; larger priors (5-10) shrink them toward zero.

When TMM/TMMwsp assumptions fail (see Failure Modes: prokaryotic stress, MYC amplification, viral host shutoff): use `method='upperquartile'` or supply known stable reference genes via offsets.

## QL F-test vs LRT vs Exact Test

```r
fit_ql <- glmQLFit(y, design, robust = TRUE)
qlf <- glmQLFTest(fit_ql, coef = 2)

fit_lrt <- glmFit(y, design)
lrt <- glmLRT(fit_lrt, coef = 2)

y <- estimateDisp(y)
et <- exactTest(y)
```

QL F-test is the modern default. LRT is anti-conservative with small n because it does not account for dispersion uncertainty. The exact test handles only two-group one-factor designs and exists for backward compatibility -- use the GLM pipeline for anything with covariates or blocking.

In v4, the QL F-test is bias-corrected via the new APL when `legacy=FALSE` (the v4 default). To exactly reproduce a v3 result: `glmQLFit(y, design, robust = TRUE, legacy = TRUE)`.

## TREAT -- Testing Against a Fold-Change Threshold

**Goal:** Control FDR for the hypothesis "biologically meaningful fold change", not "fold change non-zero".

**Approach:** `glmTreat(fit, coef=..., lfc=log2(tau))` tests H0: |LFC| <= tau vs HA: |LFC| > tau. The threshold tau MUST be biologically pre-specified -- choosing tau after seeing the data is p-hacking.

```r
tr <- glmTreat(fit, coef = 2, lfc = log2(1.5))
topTags(tr)
```

The cardinal sin TREAT avoids: filtering `padj < 0.05 & abs(logFC) > 1` after a vanilla QL F-test does NOT control FDR for "the LFC exceeds 1". Post-hoc filtering is FDR-controlled for the |LFC|>0 hypothesis only. If reviewers ask "what is the FDR of the '2-fold up' gene list", the only honest answers are TREAT (FDR controlled at the threshold) or "FDR is for non-zero only; the magnitude filter has no FDR guarantee".

Equivalent in DESeq2: `results(dds, lfcThreshold = log2(1.5), altHypothesis = 'greaterAbs')`. Both implement the McCarthy & Smyth 2009 *Bioinformatics* 25:765 idea.

## Contrasts via No-Intercept Designs

**Goal:** Define clean pairwise or multi-group contrasts.

**Approach:** Use `~ 0 + group` parameterization so each coefficient is the group mean; build `makeContrasts(...)` for any pairwise or weighted-average comparison.

```r
design <- model.matrix(~ 0 + group)
colnames(design) <- levels(group)
y <- estimateDisp(y, design, robust = TRUE)
fit <- glmQLFit(y, design, robust = TRUE)

con <- makeContrasts(
    TreatedVsControl = treated - control,
    DrugAVsDrugB     = drugA - drugB,
    ATvsBT           = (treated_A - control_A) - (treated_B - control_B),
    levels = design
)

qlf_t_vs_c <- glmQLFTest(fit, contrast = con[, 'TreatedVsControl'])
qlf_interaction <- glmQLFTest(fit, contrast = con[, 'ATvsBT'])
```

`makeContrasts` is more readable than numeric vectors for any non-trivial design.

## voom and voomWithQualityWeights

**Goal:** Use limma's linear-model framework with empirical-Bayes moderation, applying voom precision weights for the mean-variance trend of log-CPM.

**Approach:** voom transforms counts to log-CPM with per-observation precision weights derived from the mean-variance trend; lmFit + eBayes proceeds as for microarrays.

```r
v <- voom(y, design, plot = TRUE)
fit <- lmFit(v, design)
fit <- eBayes(fit, robust = TRUE)
tt <- topTable(fit, coef = 2, number = Inf)
```

`voomWithQualityWeights` (Liu, Holik, Su et al. 2015 *NAR* 43:e97) adds per-sample weights to downweight outlier samples. Use when:
- Library sizes vary >5x across samples
- RIN varies >2 units
- PCA shows one or more samples clearly off the main cluster

```r
v <- voomWithQualityWeights(y, design, plot = TRUE)
fit <- lmFit(v, design)
fit <- eBayes(fit, robust = TRUE)
```

`eBayes(robust = TRUE)` uses Phipson 2016 robust hyperparameter estimation -- NOT the default but strongly recommended for RNA-seq.

## Transcript-Level DE via catchSalmon

**Goal:** Test differential transcript expression with proper inferential variance from quantification bootstrap replicates.

**Approach:** `catchSalmon()` / `catchKallisto()` import per-transcript counts with overdispersion estimates from the bootstrap replicates; pass to `DGEList`; the rest of the pipeline is standard.

```r
salmon <- catchSalmon(paths = file.path('salmon_out', samples$id))
y_tx <- DGEList(counts = salmon$counts / salmon$annotation$Overdispersion,
                genes  = salmon$annotation)
```

Baldoni, Chen, Hediyeh-zadeh et al. 2024 *NAR* 52:e13 ("Dividing out quantification uncertainty"): the per-transcript Overdispersion column captures the variance contribution from the Salmon EM. Dividing the counts by this scaling provides effective counts that limma/edgeR can model as if quantification was certain.

## edgeR vs DESeq2 vs limma-voom

| Scenario | Recommended | Rationale |
|----------|-------------|-----------|
| Modern default | DESeq2 or edgeR QL (both fine) | ~70-90% overlap on top hits; choose by ecosystem |
| n = 2-3/group | edgeR QL | Tightest FPR at small n |
| Library sizes heterogeneous | limma-voom or voomWithQualityWeights | Precision weights matter most here |
| Salmon/kallisto -> gene-level DGE | DESeq2 (DESeqDataSetFromTximport handles offsets natively) | Cleanest path |
| Salmon -> transcript-level DTE | edgeR `catchSalmon` | Baldoni 2024 framework |
| Need apeglm/ashr LFC shrinkage | DESeq2 | edgeR has no equivalent built-in |
| Need TREAT-style threshold testing | Both (`glmTreat` or `lfcThreshold=`) | Equivalent |
| Python-only environment | PyDESeq2 | No edgeR Python equivalent |

If DESeq2 and edgeR agree on >=70% of the top 500: results are robust. <60%: investigate filtering, normalization, dispersion, or a confounded covariate -- usually a modeling issue.

## Per-Method Failure Modes

### Forgot `filterByExpr` -- inflated multiple-testing burden

**Trigger:** edgeR pipeline run on a count matrix with all genes (~60k for human) including many with zero or near-zero counts; significant gene list smaller than expected.

**Mechanism:** edgeR's QL pipeline does NOT have DESeq2's automatic independent filtering. Every gene tested contributes to the BH denominator.

**Symptom:** Low-count genes dominate the tested set; tested-gene count is 60k instead of ~15-20k; padj distribution skewed toward 1.

**Fix:** `filterByExpr(y, design)` BEFORE normalization and dispersion estimation. Filtering after `estimateDisp` invalidates the trended dispersion.

### Used `glmLRT` with n=3 -- inflated false positives

**Trigger:** Tutorial copy-paste of `glmFit` + `glmLRT` on small-n data; many "significant" genes that don't replicate.

**Mechanism:** `glmLRT` uses a point dispersion estimate; with small n, dispersion is uncertain and the test is anti-conservative.

**Symptom:** Many more DE genes than DESeq2 or limma-voom on the same data; p-value histogram has anti-conservative left tail.

**Fix:** Use `glmQLFit` + `glmQLFTest` with `robust = TRUE` on both.

### TMM/RLE assumption broken -- size factors absorb biology

**Trigger:** Bacterial stress response, viral infection with host shutoff, MYC-amplified tumor vs normal -- biological systems where >50% of genes truly change.

**Mechanism:** TMM/TMMwsp assumes most genes are unchanged. When violated, the "trimmed reference" is dominated by DE genes; the size factor compensates by absorbing the biological shift.

**Symptom:** MA plot shows the bulk cloud shifted off zero; reported fold changes don't match orthogonal validation (qPCR, Western); known DE genes show muted LFC.

**Fix:** `normLibSizes(y, method='upperquartile')` is a partial fix; supply ERCC spike-in offsets or curated stable housekeeping genes via `y$offset` for the principled solution.

### Reproducibility break between edgeR v3 and v4

**Trigger:** Pre-2025 script run on edgeR 4.0+ produces different DE genes than the published result.

**Mechanism:** v4 changed the QL framework (bias-corrected APL) and the default behavior of `glmQLFit` (`legacy = FALSE`). TMM remains the documented default for `normLibSizes`; TMMwsp is an added alternative for sparse data.

**Symptom:** Different significant gene set; absolute LFC differences of 5-15% on low-count genes; reviewer confusion.

**Fix:** For exact reproduction: `glmQLFit(y, design, robust=TRUE, legacy=TRUE)`. The normalization default has not actually changed -- TMM remains the v4 default. Better: rerun and accept the v4 -- improved -- numbers, noting the version change in methods.

## Common errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `decidetestsDGE` not found | Removed in edgeR v4 | Use `decideTests(qlf)` |
| `design matrix not full rank` | Confounded covariates | Inspect with `alias(design)$Complete` |
| `No residual df` | Too few replicates for the model | Reduce model complexity or get more samples |
| Script expects `$adj.P.Val` but `topTags` returns `$FDR` | Tool-name column mix-up | edgeR uses `$FDR`; limma uses `$adj.P.Val`; DESeq2 uses `$padj` |
| QL F p-values numerically different from a 2023 paper | edgeR v4 default `legacy=FALSE` | Set `legacy=TRUE` to reproduce v3, or note the version change |

## References

- Robinson MD, McCarthy DJ, Smyth GK. 2010. edgeR: a Bioconductor package for differential expression analysis of digital gene expression data. *Bioinformatics* 26(1):139-140. doi:10.1093/bioinformatics/btp616
- McCarthy DJ, Chen Y, Smyth GK. 2012. Differential expression analysis of multifactor RNA-Seq experiments with respect to biological variation. *Nucleic Acids Res* 40(10):4288-4297. doi:10.1093/nar/gks042
- Chen Y, Lun ATL, Smyth GK. 2016. From reads to genes to pathways: differential expression analysis of RNA-Seq experiments using Rsubread and the edgeR quasi-likelihood pipeline. *F1000Res* 5:1438. doi:10.12688/f1000research.8987.2
- Chen Y, Chen L, Lun ATL, Baldoni PL, Smyth GK. 2025. edgeR v4: powerful differential analysis of sequencing data with expanded functionality and improved support for small counts and larger datasets. *Nucleic Acids Res* 53(2):gkaf018. doi:10.1093/nar/gkaf018
- Lund SP, Nettleton D, McCarthy DJ, Smyth GK. 2012. Detecting differential expression in RNA-sequence data using quasi-likelihood with shrunken dispersion estimates. *Stat Appl Genet Mol Biol* 11(5):Article 8. doi:10.1515/1544-6115.1826
- Phipson B, Lee S, Majewski IJ, Alexander WS, Smyth GK. 2016. Robust hyperparameter estimation protects against hypervariable genes and improves power to detect differential expression. *Ann Appl Stat* 10(2):946-963. doi:10.1214/16-AOAS920
- Law CW, Chen Y, Shi W, Smyth GK. 2014. voom: precision weights unlock linear model analysis tools for RNA-seq read counts. *Genome Biol* 15(2):R29. doi:10.1186/gb-2014-15-2-r29
- Liu R, Holik AZ, Su S, Jansz N, Chen K, Leong HS, Blewitt ME, Asselin-Labat M-L, Smyth GK, Ritchie ME. 2015. Why weight? Modelling sample and observational level variability improves power in RNA-seq analyses. *Nucleic Acids Res* 43(15):e97. doi:10.1093/nar/gkv412
- McCarthy DJ, Smyth GK. 2009. Testing significance relative to a fold-change threshold is a TREAT. *Bioinformatics* 25(6):765-771. doi:10.1093/bioinformatics/btp053
- Baldoni PL, Chen Y, Hediyeh-zadeh S, Liao Y, Dong X, Ritchie ME, Shi W, Smyth GK. 2024. Dividing out quantification uncertainty allows efficient assessment of differential transcript expression with edgeR. *Nucleic Acids Res* 52(3):e13. doi:10.1093/nar/gkad1167
- Ritchie ME, Phipson B, Wu D, Hu Y, Law CW, Shi W, Smyth GK. 2015. limma powers differential expression analyses for RNA-sequencing and microarray studies. *Nucleic Acids Res* 43(7):e47. doi:10.1093/nar/gkv007
- Schurch NJ et al. 2016. How many biological replicates are needed in an RNA-seq experiment and which differential expression tool should you use? *RNA* 22(6):839-851. doi:10.1261/rna.053959.115
- Robinson MD, Oshlack A. 2010. A scaling normalization method for differential expression analysis of RNA-seq data. *Genome Biol* 11(3):R25. doi:10.1186/gb-2010-11-3-r25

## Related Skills

- deseq2-basics - Cross-check, or use when LFC shrinkage (apeglm) needed
- de-results - FDR, IHW, GSEA preparation, padj column name variation
- de-visualization - BCV plot, MD plot, PCA via plotMDS
- batch-correction - Include batch in design vs correct-then-test cardinal sin
- timeseries-de - voom + splines for time-course
- expression-matrix/counts-ingest - Salmon/kallisto input via tximport or catchSalmon
- expression-matrix/normalization - TMM/TMMwsp/RLE mechanics
- expression-matrix/metadata-joins - Reference level, paired design, interaction parameterization
- expression-matrix/gene-id-mapping - Annotating DE results with symbols
- rna-quantification/tximport-workflow - Detailed tximport mechanics
- pathway-analysis/gsea - Ranked-list input from DE
<!-- END FILE: differential-expression/edger-basics/SKILL.md -->

## 子目录：differential-expression/timeseries-de

<!-- BEGIN FILE: differential-expression/timeseries-de/SKILL.md -->
---
name: bio-differential-expression-timeseries-de
description: Analyzes time-series and longitudinal RNA-seq for differential expression and trajectory structure. Covers DESeq2 LRT with reduced models, time as factor vs continuous vs natural splines, maSigPro (Nueda 2014 for RNA-seq), ImpulseDE2 with explicit impulse-model failure modes, DREAM for repeated measures via linear mixed models, pseudoreplication avoidance, conditional vs marginal modeling, and trajectory clustering with DPGP, Mfuzz (with Schwämmle 2010 fuzzifier estimation), and splines+k-means. Use when modeling time-course or longitudinal expression, choosing factor vs spline, handling repeated measures from the same subject, avoiding pseudoreplication, clustering temporal trajectories, or selecting between dedicated time-course tools and pairwise+LRT.
tool_type: r
primary_tool: DESeq2
---

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, edgeR 4.0+, limma 3.58+, splines (base R), maSigPro 1.74+, ImpulseDE2 1.10+ (Bioconductor archive; verify availability), variancePartition / dream 1.32+, Mfuzz 2.62+, TCseq 1.26+, ggplot2 3.5+, pheatmap 1.0+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Time-Series Differential Expression

**"Find genes that change over time"** -> Define what "change" means -- any non-zero time effect (LRT), a smooth nonlinear trend (splines), a transient impulse (ImpulseDE2), or differing trajectories between groups (interaction LRT) -- and choose the model that asks that specific question while handling repeated-measures correctly.

## The Single Most Important Modern Insight -- Most dedicated time-course tools UNDERPERFORM pairwise + LRT on short series

Spies, Renz, Beyer, Ciaudo 2019 *Brief Bioinform* 20:288 benchmarked dedicated time-course tools (ImpulseDE2, splineTC, maSigPro, EBSeqHMM, TimeReg) against naive DESeq2/edgeR pairwise comparisons + LRT for omnibus, on simulated and real time-courses. Finding: **on short series (<8 time points), naive pairwise pattern-of-significance OUTPERFORMS dedicated TC tools** because of high false-positive rates in the latter. The exception is ImpulseDE2, which holds up better than the others -- IF its impulse assumption (rise-then-plateau or fall-then-plateau) actually fits the biology.

For most experimental time courses (3-6 time points, common in pharmacology and developmental biology), the right tool is DESeq2 with `test='LRT'` and a sensible reduced model. Reserve splines for >5 evenly-spaced time points; reserve ImpulseDE2 for monotonic-then-saturating dynamics; reserve DREAM for repeated measures.

A second insight that is constantly violated: pseudoreplication. If 3 subjects each contribute 4 time points (12 samples), the effective sample size for testing TIME effects is closer to 3, not 12 -- the within-subject observations are not independent. Treating them as independent inflates type-I error dramatically. Either include subject as a fixed effect, use DREAM (mixed model), or collapse to per-subject means (loses time info).

## Algorithmic Taxonomy

| Method | What it tests | Best for | Failure mode |
|--------|---------------|----------|--------------|
| DESeq2 LRT (`test='LRT'`, `reduced=`) | Joint hypothesis: dropped terms are jointly zero | Default for "any time effect"; multi-group time interaction | Reports LFC of last coefficient, not omnibus -- use padj only |
| DESeq2 + splines (`ns(time, df=3)`) | Smooth nonlinear time effect | 5+ time points, smooth dynamics, multi-group interaction | Spline df > unique time points / 2 overfits |
| maSigPro (Nueda 2014 RNA-seq update) | Polynomial regression on time per group | Multi-group time-course, regression-style hypotheses | Polynomial assumption can be wrong; less popular than DESeq2 LRT |
| ImpulseDE2 (Fischer, Theis, Yosef 2018) | Constant vs monotonic vs impulse trajectories | Monotonic-then-saturating or impulse-like responses | Fails on oscillatory, multi-phase, monotonic-non-asymptotic; sensitive to noise on short series |
| DREAM (Hoffman, Roussos 2021) | Per-gene linear mixed model with random subject | Repeated measures with >2 time points per subject | Slower; requires variancePartition stack; `ddf='adaptive'` default (Kenward-Roger for n<=20, Satterthwaite otherwise) |
| voom + duplicateCorrelation | Single average within-subject correlation | Technical reps within bio reps, paired pre/post | Single correlation across all genes is approximation |
| edgeR LRT with subject as factor | Subject as fixed effect | Small subject count, simple design | Wastes df; can't handle continuous time well |
| TCseq | Spline-based DE + fuzzy clustering | Combined pipeline for DE + cluster discovery | Single-tool dependency; verify maintenance |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| 2-3 discrete time points, independent samples per time | DESeq2 LRT, time as factor, `reduced = ~1` | Too few points for splines |
| 5+ time points, single group, smooth dynamics | DESeq2 LRT with `ns(time, df=3)`, `reduced = ~1` | Splines capture nonlinearity efficiently |
| 5+ time points, two groups, "do trajectories differ?" | LRT with `~ treatment * ns(time, df=3)` vs `reduced = ~ treatment + ns(time, df=3)` | Tests the interaction (treatment-specific time response) |
| Same subject sampled over time (longitudinal) | DREAM (random subject) OR DESeq2 with subject fixed effect | Mandatory: pseudoreplication otherwise |
| Monotonic-then-saturating biology expected | ImpulseDE2 | Built for the assumption |
| Circadian or cell-cycle (cyclical) | Fourier basis (`fda::create.fourier.basis`) or dedicated tools (JTK_CYCLE, MetaCycle) | Splines can't represent periodicity |
| Short series (<8 time points) | DESeq2 pairwise + LRT (Spies 2019 finding) | Dedicated TC tools have high FPR on short series |
| Want to cluster trajectories after DE | DPGP (nonparametric), Mfuzz (with Schwämmle 2010 m estimation), splines + k-means | Standardize per gene first |
| Multi-batch time course | Add batch to design; test the interaction term | Standard DESeq2 / edgeR pattern |

## DESeq2 LRT for Time -- The Canonical Pattern

**Goal:** Test whether time has ANY effect (omnibus), or whether time trajectories differ between groups (interaction).

**Approach:** Specify a full design including the time terms; specify a reduced design dropping those terms; LRT compares.

```r
library(DESeq2)

dds <- DESeqDataSetFromMatrix(counts, colData, design = ~ time)
dds <- DESeq(dds, test = 'LRT', reduced = ~ 1)
res <- results(dds)
```

The LRT p-value tests "any difference among time points". The `log2FoldChange` column reports the LAST coefficient in `resultsNames(dds)` -- NOT the omnibus effect. Use padj only from LRT results; extract individual Wald per time point for effect sizes.

Interaction (treatment-specific time response):

```r
dds <- DESeqDataSetFromMatrix(counts, colData,
    design = ~ treatment + time + treatment:time)
dds <- DESeq(dds, test = 'LRT', reduced = ~ treatment + time)
res_interaction <- results(dds)
```

This tests "does the time trajectory differ between treatment groups?" -- a different question than "is there a time effect" or "is there a treatment effect".

## Time as Factor vs Continuous vs Spline

| Encoding | Assumption | df spent | When |
|----------|------------|----------|------|
| Factor (`time` as factor) | No structure; each level independent | (n_levels - 1) | Few discrete time points, irregular spacing, interest in specific pairwise comparisons |
| Continuous (`as.numeric(time)`) | Linear effect on log expression | 1 | Linear biology, well-spaced time points -- often wrong |
| Natural spline (`ns(time, df=k)`) | Smooth nonlinear; k basis functions | k | Dense time courses (5+ points), smooth biology |

Rule of thumb: `df <= unique_time_points / 2`.

```r
library(splines)

dds <- DESeqDataSetFromMatrix(counts, colData,
    design = ~ treatment * ns(time, df = 3))
dds <- DESeq(dds, test = 'LRT', reduced = ~ treatment + ns(time, df = 3))
```

## limma-voom + Splines (Modern Alternative)

```r
library(limma)
library(edgeR)
library(splines)

y <- DGEList(counts = counts)
y <- normLibSizes(y)
keep <- filterByExpr(y, group = metadata$treatment)
y <- y[keep, , keep.lib.sizes = FALSE]

design <- model.matrix(~ treatment * ns(time, df = 3), data = metadata)
v <- voom(y, design, plot = TRUE)
fit <- lmFit(v, design)
fit <- eBayes(fit, robust = TRUE)

interaction_cols <- grep(':ns\\(time', colnames(design))
tt <- topTable(fit, coef = interaction_cols, number = Inf)
```

Tests the joint significance of all interaction spline coefficients.

## DREAM for Repeated Measures

**Goal:** Properly model longitudinal data where the same subject is sampled multiple times.

**Approach:** Linear mixed model per gene with subject as a random intercept (or slope), via `variancePartition::dream`. Uses voom-weighted linear regression internally. Default `ddf='adaptive'` uses Kenward-Roger for n <= 20 samples (the typical longitudinal-DE regime) and Satterthwaite otherwise; force either explicitly with `ddf='Kenward-Roger'` or `ddf='Satterthwaite'`.

```r
library(variancePartition)
library(edgeR)
library(BiocParallel)

y <- DGEList(counts = counts)
y <- normLibSizes(y)
keep <- filterByExpr(y, group = metadata$treatment)
y <- y[keep, , keep.lib.sizes = FALSE]

formula <- ~ treatment + time + treatment:time + (1 | subject)

vobj <- voomWithDreamWeights(y, formula, metadata)
fitmm <- dream(vobj, formula, metadata)
fitmm <- eBayes(fitmm)
tt <- topTable(fitmm, coef = grep(':time', colnames(coefficients(fitmm))),
               number = Inf)
```

When to use DREAM over `~ subject + treatment + time` (subject as fixed effect):
- More than 2 time points per subject (more random-effect signal to estimate)
- Many subjects (random effects more parsimonious than fixed)
- Random slopes needed (e.g., `(1 + time | subject)`)
- Multiple random effects (e.g., `(1 | donor) + (1 | batch)`)

`duplicateCorrelation` (`limma`) is the older approximate alternative -- assumes a SINGLE within-subject correlation across all genes. Adequate for technical replicates within biological replicates; less so for proper longitudinal data with multiple time points.

## maSigPro (Nueda 2014 for RNA-seq)

```r
library(maSigPro)

edesign <- data.frame(
    Time      = metadata$time,
    Replicate = metadata$replicate,
    Control   = as.numeric(metadata$treatment == 'Control'),
    Treatment = as.numeric(metadata$treatment == 'Treatment')
)
rownames(edesign) <- metadata$sample

design <- make.design.matrix(edesign, degree = 3)

fit <- p.vector(norm_counts, design, Q = 0.05, MT.adjust = 'BH')
tstep <- T.fit(fit, step.method = 'backward', alfa = 0.05)
sigs <- get.siggenes(tstep, rsq = 0.6, vars = 'groups')
see.genes(sigs$sig.genes, show.fit = TRUE, dis = design$dis,
          cluster.method = 'hclust', k = 9)
```

CITATION: Nueda MJ, Tarazona S, Conesa A (2014) "Next maSigPro: updating maSigPro bioconductor package for RNA-seq time series." *Bioinformatics* 30(18):2598-2602. The earlier Conesa et al. 2006 *Bioinformatics* 22:1096 is the microarray-era original. Cite 2014 for RNA-seq use; many secondary refs miscite 2006.

## ImpulseDE2

**Goal:** Detect transient impulse-like expression patterns (rise then decay, or constant-then-monotonic).

**Approach:** Fits constant, monotonic, and impulse (6-parameter sigmoid: baseline, peak, post-peak baseline, rise rate, decay rate) models per gene; selects the best-fitting and tests for differential dynamics.

```r
library(ImpulseDE2)

dfAnnotation <- data.frame(
    Sample    = colnames(counts),
    Time      = metadata$time,
    Condition = metadata$condition,
    Batch     = metadata$batch
)

imp <- runImpulseDE2(
    matCountData    = as.matrix(counts),
    dfAnnotation    = dfAnnotation,
    boolCaseCtrl    = TRUE,
    vecConfounders  = c('Batch'),
    scaNProc        = 4
)

sig <- imp$dfImpulseDE2Results[imp$dfImpulseDE2Results$padj < 0.05, ]
```

The impulse model FAILS on:
- Oscillatory expression (circadian, cell cycle) -- model can't represent periodicity
- Monotonic-but-non-asymptotic responses (linear increases that don't plateau)
- Multi-phase responses (rise-fall-rise)

For oscillatory biology, use Fourier basis or dedicated tools (JTK_CYCLE, MetaCycle). For non-asymptotic monotonic, splines fit better.

NOTE: ImpulseDE2 was removed from Bioconductor at the 3.13 release (May 2021); last hosted version was 3.10 -- install from the BiocArchive (pin to Bioc 3.10) or the YosefLab GitHub mirror. The Spies 2019 benchmark showed ImpulseDE2 holds up on longer time courses (~8+ time points) but is sensitive to noise on short series; below ~8 time points, DESeq2 pairwise + LRT typically outperforms.

## Trajectory Clustering of DE Genes

**Goal:** After identifying DE-over-time genes, group them by trajectory shape.

**Approach:** Standardize per gene (subtract mean, divide by SD per gene) -- otherwise clusters reflect mean level, not shape. Then apply DPGP (nonparametric), Mfuzz (fuzzy c-means), or splines + k-means.

```r
library(Mfuzz)

eset <- ExpressionSet(assayData = as.matrix(norm_counts[sig_genes, ]))
eset_std <- standardise(eset)

m <- mestimate(eset_std)
cl <- mfuzz(eset_std, c = 9, m = m)

mfuzz.plot(eset_std, cl, mfrow = c(3, 3))
```

The Mfuzz fuzzifier `m` is critical -- too low gives crisp clusters (loses fuzzy advantage); too high collapses everything. `mestimate()` implements Schwämmle & Jensen 2010 *Bioinformatics* 26:2841 to estimate `m` from the data.

CITATION CARE: the Mfuzz PACKAGE paper is Kumar L, Futschik ME (2007) *Bioinformation* 2(1):5-7 (the journal is *Bioinformation*, NOT *Bioinformatics*). The Schwämmle 2010 paper is the fuzzifier-estimation methodology paper, *Bioinformatics*. Many references confuse the two.

For DPGP (Dirichlet Process Gaussian Process; nonparametric in cluster number AND trajectory shape):

CITATION: McDowell IC, Manandhar D, Vockley CM, Schmid AK, Reddy TE, Engelhardt BE (2018) "Clustering gene expression time series data using an infinite Gaussian process mixture model." *PLoS Comput Biol* 14(1):e1005896. CITATION CARE: this is *PLoS Comp Biol*, NOT *Genome Research* (a common miscitation).

Splines + k-means (fast alternative):

```r
library(splines)
spline_coefs <- t(apply(norm_counts[sig_genes, ], 1, function(x) {
    fit <- lm(x ~ ns(metadata$time, df = 4))
    coef(fit)
}))
km <- kmeans(scale(spline_coefs), centers = 6)
```

## Time as the Only Variable (Developmental Series)

When time is the sole variable (e.g., embryonic development series), the DE question becomes "which genes change across the trajectory":

```r
dds <- DESeqDataSetFromMatrix(counts, colData, design = ~ time)
dds <- DESeq(dds, test = 'LRT', reduced = ~ 1)
res <- results(dds)
```

Caveats:
- Reference time point biases the reported LFC (it's the LFC at the LAST time point vs reference)
- For cyclical biology (circadian, cell cycle), use periodic basis functions

## Per-Method Failure Modes

### Pseudoreplication -- treated 12 samples from 3 subjects as 12 independent

**Trigger:** 3 subjects x 4 time points = 12 samples; vanilla DESeq2 with `~ time`; many DE genes.

**Mechanism:** Within-subject observations are correlated; treating them as independent inflates effective sample size from 3 to 12 in the inference, deflating standard errors.

**Symptom:** p-value histogram anti-conservative; many false-positive DE genes; replication fails.

**Fix:** Include subject in design (`~ subject + time`) OR use DREAM with random subject. Collapsing to per-subject means is OK but loses time info.

### LRT reports the wrong LFC

**Trigger:** `DESeq(dds, test='LRT', reduced=~1)` on a 5-time-point study; user reports the `log2FoldChange` column as "the time effect".

**Mechanism:** LRT padj is the omnibus joint test. The LFC reported is for the LAST coefficient in `resultsNames(dds)`, one specific level-vs-reference comparison.

**Symptom:** A 5-time-point factor produces one LFC per gene; reviewer asks "the effect of which time?"

**Fix:** Treat LRT padj as a screen for "any change". For effect sizes, extract Wald coefficients per time point via `results(dds, name='time_T2_vs_T0')` etc.

### ImpulseDE2 reports noise as "impulse"

**Trigger:** Short series (4-5 time points), oscillatory or non-monotonic biology; ImpulseDE2 flags many "impulse" genes that look like noise on inspection.

**Mechanism:** Impulse model has 6 parameters; on short series, easy to fit by chance. For oscillatory data, model is wrong.

**Symptom:** Validation orthogonal data shows the "impulse" genes are not actually transient; replication low.

**Fix:** Use DESeq2 LRT + spline interaction for short or non-impulse data. Reserve ImpulseDE2 for cases where biology is known to be monotonic-then-asymptotic (immune response, cytokine release).

### Wrong spline df

**Trigger:** 4 time points; user sets `ns(time, df = 5)`; bizarre fits per gene.

**Mechanism:** df > number of unique time points produces overfitting; spline basis is rank-deficient.

**Symptom:** Errors about singular fits; or apparently-clean fits that don't generalize.

**Fix:** `df <= unique_time_points / 2`. For 4 time points, df = 2 (or use factor encoding instead).

### Trajectory clusters dominated by expression level

**Trigger:** Mfuzz / k-means clustering of trajectories; clusters separate high- vs low-expressed genes rather than shape patterns.

**Mechanism:** Forgot to standardize per gene; absolute levels dominate distance computations.

**Symptom:** Clusters labeled by mean expression, not trajectory shape.

**Fix:** `standardise()` in Mfuzz, or `scale()` per gene before k-means. The point of trajectory clustering is shape, not magnitude.

### maSigPro miscited as 2006

**Trigger:** Methods section cites "Conesa 2006 maSigPro" for an RNA-seq analysis.

**Mechanism:** The 2006 Conesa paper is the original microarray maSigPro. The 2014 Nueda paper is the RNA-seq update with NB GLM.

**Symptom:** Reviewer asks for the RNA-seq citation specifically.

**Fix:** Cite Nueda MJ, Tarazona S, Conesa A (2014) *Bioinformatics* 30(18):2598-2602 for RNA-seq use.

## Common errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `singular fit` from spline model | df > unique time points | Reduce df or use factor encoding |
| LRT p-values numerically identical across genes | Reduced model matches full model (no effect tested) | Verify `reduced` actually drops the term of interest |
| ImpulseDE2 not installable from Bioconductor | Removed at Bioconductor 3.13 (May 2021); last hosted version 3.10 | Install from BiocArchive (pin Bioc 3.10) or YosefLab GitHub mirror |
| Mfuzz clusters dominated by mean level | Forgot standardisation | Use `standardise()` before `mfuzz()` |
| Trajectory plot shows flat lines | Counts not log-transformed before clustering | Use `cpm(y, log=TRUE)` or `vst()` then standardize |
| DREAM very slow | Large gene set with mixed model per gene | Filter to DE-over-time first (LRT screen), then DREAM on the subset |

## References

- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biol* 15(12):550. doi:10.1186/s13059-014-0550-8
- Nueda MJ, Tarazona S, Conesa A. 2014. Next maSigPro: updating maSigPro bioconductor package for RNA-seq time series. *Bioinformatics* 30(18):2598-2602. doi:10.1093/bioinformatics/btu333
- Conesa A, Nueda MJ, Ferrer A, Talón M. 2006. maSigPro: a method to identify significantly differential expression profiles in time-course microarray experiments. *Bioinformatics* 22(9):1096-1102. doi:10.1093/bioinformatics/btl056
- Fischer DS, Theis FJ, Yosef N. 2018. Impulse model-based differential expression analysis of time course sequencing data. *Nucleic Acids Res* 46(20):e119. doi:10.1093/nar/gky675
- Hoffman GE, Roussos P. 2021. dream: powerful differential expression analysis for repeated measures designs. *Bioinformatics* 37(2):192-201. doi:10.1093/bioinformatics/btaa687
- Hoffman GE, Schadt EE. 2016. variancePartition: interpreting drivers of variation in complex gene expression studies. *BMC Bioinformatics* 17:483. doi:10.1186/s12859-016-1323-z
- Spies D, Renz PF, Beyer TA, Ciaudo C. 2019. Comparative analysis of differential gene expression tools for RNA sequencing time course data. *Brief Bioinform* 20(1):288-298. doi:10.1093/bib/bbx115
- Kumar L, Futschik ME. 2007. Mfuzz: a software package for soft clustering of microarray data. *Bioinformation* 2(1):5-7.
- Schwämmle V, Jensen ON. 2010. A simple and fast method to determine the parameters for fuzzy c-means cluster analysis. *Bioinformatics* 26(22):2841-2848. doi:10.1093/bioinformatics/btq534
- McDowell IC, Manandhar D, Vockley CM, Schmid AK, Reddy TE, Engelhardt BE. 2018. Clustering gene expression time series data using an infinite Gaussian process mixture model. *PLoS Comput Biol* 14(1):e1005896. doi:10.1371/journal.pcbi.1005896
- Law CW, Chen Y, Shi W, Smyth GK. 2014. voom: precision weights unlock linear model analysis tools for RNA-seq read counts. *Genome Biol* 15(2):R29. doi:10.1186/gb-2014-15-2-r29

## Related Skills

- deseq2-basics - LRT mechanics; design formulas
- edger-basics - voom + splines pattern
- de-results - LRT padj interpretation; pseudoreplication detection
- de-visualization - Per-gene trajectories; heatmap with time order
- batch-correction - Time-batch confounding; multi-batch time courses
- expression-matrix/metadata-joins - Subject as covariate; repeated measures designs
- pathway-analysis/go-enrichment - Functional analysis of trajectory clusters
- temporal-genomics/circadian-rhythms - Circadian-specific detection (JTK_CYCLE, MetaCycle)
- temporal-genomics/temporal-clustering - Standalone trajectory clustering methods
- temporal-genomics/trajectory-modeling - GAM trajectory fitting
- temporal-genomics/temporal-grn - Dynamic gene regulatory network inference
<!-- END FILE: differential-expression/timeseries-de/SKILL.md -->

<!-- END CATEGORY: differential-expression -->

