---
slug: bio-multi-omics-integration-integrated
version: 1.0.0
displayName: "多组学整合 / Multi-omics integration"
name: bio-multi-omics-integration-integrated
summary: >-
  中文：多组学整合综合技能，整合 5 个相关专题，覆盖多组学整合：MOFA2因子分析、mixOmics/DIABLO监督签名、SNF患者分型、数据对齐与标准化。 English: Integrated Multi-omics integration skill covering 5 related topics, including Multi-omics integration: MOFA2 factor analysis, mixOmics/DIABLO supervised signatures, SNF patient subtyping, data harmonization.
description: >-
  中文：这是一个面向多组学整合的综合生物信息学 Skill，整合当前分类下 5 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：多组学整合：MOFA2因子分析、mixOmics/DIABLO监督签名、SNF患者分型、数据对齐与标准化。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：MOFA2, MultiAssayExperiment, SNFtool。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Multi-omics integration, combining 5 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Multi-omics integration: MOFA2 factor analysis, mixOmics/DIABLO supervised signatures, SNF patient subtyping, data harmonization. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: MOFA2, MultiAssayExperiment, SNFtool. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# multi-omics-integration 分类 Skill 整合版

> 本文件整合同一主分类目录下 5 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: multi-omics-integration -->

## 子目录：multi-omics-integration/data-harmonization

<!-- BEGIN FILE: multi-omics-integration/data-harmonization/SKILL.md -->
---
name: bio-multi-omics-data-harmonization
description: Harmonizes already-normalized per-omic matrices onto a common footing before joint integration - assembling a MultiAssayExperiment, choosing the per-omic variance-stabilizing transform, deciding per-view versus per-feature scaling, picking a cross-omic batch strategy, and triaging missing data (feature, value, or whole sample; MAR versus MNAR). Covers why a shared-latent integrator is blind to what an omic is so scaling silently decides which block dominates, why batch confounded with biology is irrecoverable and should be modeled as a covariate not scrubbed, and why stacking blocks and running one ComBat erases cross-omic signal. Use when preparing two or more omics for MOFA2, mixOmics, or SNF, deciding a transform or scaling, correcting batch across modalities, or handling missing omics per sample. For deep per-omic normalization see differential-expression, methylation-analysis, proteomics, metabolomics; for the method decision see integration-design; for fusion see mofa-integration, mixomics-analysis.
tool_type: r
primary_tool: MultiAssayExperiment
---

## Version Compatibility

Reference examples tested with: MultiAssayExperiment 1.36+, SummarizedExperiment 1.40+, sva 3.50+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Deep per-omic normalization (DESeq2 VST internals, methylation noob/BMIQ, proteomics VSN) is owned by the per-omic categories and pinned to their own tool versions; this skill calls the cross-omic container and batch tools, so MultiAssayExperiment and sva are the binding versions here.

# Data Harmonization for Multi-Omics

**"Get my omics onto a common footing for integration"** -> Transform each block to a comparable scale, equalize block contribution, decide a single batch strategy, and triage missingness - because the integrator sees one stacked matrix of numbers and spends its first factors on whichever block has the largest raw variance, which is a property of the assay, not the biology.
- R: `MultiAssayExperiment` to coordinate assays, sample map, and colData

Scope: cross-omic harmonization of already-normalized blocks - container assembly, transform choice, per-view scaling, batch strategy, missing-data triage. Deep single-omic normalization -> differential-expression, methylation-analysis, proteomics, metabolomics. The method-selection decision -> integration-design. Fusion math -> mofa-integration, mixomics-analysis. Single-omic RNA batch mechanics -> differential-expression/batch-correction.

## The Single Most Important Modern Insight -- A Shared-Latent Integrator Is Blind to What an Omic Is

A factor model sees one stacked matrix and spends its leading factors on whichever block has the largest raw variance and the most non-Gaussian structure - a property of the measurement scale, not the biology. Harmonization is the act of making the variance budget mean something biological before the model gets to it. Every choice is therefore a silent vote on which omic dominates the shared latent space and which signal is allowed to appear:

1. **The transform decides distribution.** Raw NB counts (0-10^5), bounded methylation betas, right-skewed proteomics, and closed compositional proportions are not comparable; feed them together and the factorization is driven by scale artifacts. Apply the per-omic variance-stabilizing transform FIRST (RNA -> VST/logCPM; methylation -> M-values; proteomics/metabolomics -> log2; compositional -> CLR).
2. **The scaling decides dominance.** Even after transforming, blocks differ in total variance and feature count, and variance is additive across features, so a 20k-gene block out-votes a 200-metabolite block. Per-VIEW scaling equalizes blocks; per-FEATURE unit-variance scaling (mixOmics default) inflates near-constant noise features into spurious factors - filter them first.
3. **The batch model decides what is deleted.** A batch-corrected matrix is the data conditioned on a model of what batch is. When batch is confounded with biology the correction deletes biology with confidence; even on a balanced design, scrub-then-test exaggerates significance (Nygaard 2016). Correct once, prefer modeling batch as a covariate over scrubbing.

The deliverable is not "the harmonized data" - it is a documented chain of transform -> scaling -> batch -> missing-value triage, each justified, because each silently determines the integration result.

## Per-Omic Transform Decision Table

| Omic | Raw-data pathology | Transform for integration | Why |
|------|--------------------|---------------------------|-----|
| RNA-seq (bulk) | NB counts; variance grows with mean; loads on high-count genes | VST or rlog (DESeq2), or log-CPM (voom) | variance-stabilize to approximately homoscedastic and Gaussian (Love 2014); `blind=TRUE` for unsupervised integration |
| Methylation | beta in [0,1]; variance compressed near 0 and 1 | M-value = log2(beta/(1-beta)) for modeling; beta for interpretation | logit un-compresses the extremes -> homoscedastic (Du 2010) |
| Proteomics / metabolomics | positive, right-skewed, multiplicative error; MNAR below detection | log2, then MNAR-aware imputation | log makes multiplicative error additive and Gaussian (Lazar 2016) |
| Microbiome / compositional | simplex, fixed-sum; spurious negative correlation | CLR after zero replacement | maps the simplex to Euclidean space; raw proportions invalid for L2 methods (Gloor 2017) -> metagenomics/abundance-estimation |
| ALL, after the above | blocks differ in total variance and feature count | per-VIEW scaling (MFA singular-value weighting; MOFA `scale_views`) | equalize block contribution without inflating individual features |

The transform is per-omic (owned by the per-omic categories); the scaling is cross-block (owned here). They are sequential and both required - scaling a heteroscedastic block does not make it homoscedastic.

## Harmonization Tool Taxonomy

| Tool | Citation | Role | When |
|------|----------|------|------|
| MultiAssayExperiment | Ramos 2017 *Cancer Res* 77:e39 | container: assays + sampleMap + colData | always - makes sample linkage a structural invariant, not string-munging |
| sva ComBat | Johnson 2007 *Biostatistics* 8:118 | empirical-Bayes batch adjustment (transformed data) | scrub batch PER OMIC when the integrator needs clean input |
| ComBat-seq | Zhang 2020 *NAR Genom Bioinform* 2:lqaa078 | batch adjustment on RNA-seq COUNTS | batch-correct counts before VST, not after |
| limma removeBatchEffect | Ritchie 2015 *Nucleic Acids Res* 43:e47 | regress out batch for visualization | ordination/QC plots only - never feed to an inferential test |
| sva / RUV | Leek 2007 *PLoS Genet* 3:e161; Risso 2014 *Nat Biotechnol* 32:896 | estimate hidden/unwanted variation as covariates | batch is unknown or driven by control genes |
| imputeLCMD / DEP | Lazar 2016 *J Proteome Res* 15:1116 | QRILC/MinProb (MNAR) + kNN (MAR) imputation | below-detection proteomics/metabolomics gaps |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Blocks on different scales going into MOFA/PLS | per-omic transform then per-view scaling | the integrator assumes comparable, homoscedastic inputs |
| One omic has far more features than another | per-view scaling and/or filter the wider view harder | feature count buys variance votes; equalize block contribution |
| Batch differs across omics, integrator needs clean input | ComBat PER OMIC (ComBat-seq for counts) | scrub once per modality; never stack blocks and ComBat together |
| Downstream step is an inferential test | model batch as a covariate (`~ batch + condition`) | scrub-then-test exaggerates confidence (Nygaard 2016) |
| Batch correlates with the condition | do NOT correct; redesign or report the confound | confounded batch is irrecoverable; correcting deletes biology |
| Proteomics missing below detection (MNAR) | QRILC / MinProb (imputeLCMD) | MAR imputation biases low-abundance proteins upward |
| Sporadic within-feature gaps (MAR) | kNN / missForest | local borrowing is valid when missingness is random |
| Some samples missing a whole omic (mosaic) | -> mofa-integration (models the missingness) | do not impute a whole block; intersecting loses scarce n |
| Need the method decision, not the prep | -> integration-design | which integration paradigm fits the question |

## Assemble the Container and Decide Correspondence

**Goal:** Make sample linkage across omics a structural invariant and quantify how mosaic the cohort is, so the impute-versus-model-the-missingness decision is explicit.

**Approach:** Build a MultiAssayExperiment from per-omic SummarizedExperiments; the sampleMap (assay, primary, colname) links assay columns to subjects. `intersectColumns` gives complete cases (subjects), which is what integration wants; `intersectRows` aligns features and is a trap on heterogeneous omics.

```r
library(MultiAssayExperiment)

rna  <- SummarizedExperiment(assays=list(vst=vst_rna), colData=sample_info)       # already VST-normalized
prot <- SummarizedExperiment(assays=list(log2=norm_prot), colData=sample_info)    # already log2 + median-normalized
meth <- SummarizedExperiment(assays=list(mval=m_values), colData=sample_info)     # already M-values

mae <- MultiAssayExperiment(experiments=ExperimentList(RNA=rna, Protein=prot, Methylation=meth),
                            colData=sample_info)
table(complete.cases(mae))        # subjects with every omic
paired <- intersectColumns(mae)   # complete-case fallback; counts the n it costs
```

## Per-View Scaling (Equalize Block Contribution)

**Goal:** Stop the highest-variance or highest-dimensional omic from hijacking the shared factors without inflating noise features.

**Approach:** Filter near-constant features per block, then scale each block so its blocks contribute comparably. Per-view scaling divides a whole block by its total variance/first singular value; reserve per-feature unit-variance scaling for inside PLS and only after filtering low-variance features.

```r
drop_constant <- function(mat, min_sd=1e-8) mat[apply(mat, 1, sd, na.rm=TRUE) > min_sd, ]   # per-feature scaling blows up zero-variance features

scale_per_view <- function(mat) mat / sqrt(sum(apply(mat, 1, var, na.rm=TRUE)))             # whole-block scaling: equalizes contribution, preserves within-block feature ratios

blocks <- lapply(list(RNA=vst_rna, Protein=norm_prot, Methylation=m_values), drop_constant)
blocks <- lapply(blocks, scale_per_view)
sapply(blocks, function(x) sum(apply(x, 1, var)))    # each block now contributes comparably
```

## Cross-Omic Batch Strategy

**Goal:** Remove technical batch once, in one place, without deleting biology or double-correcting.

**Approach:** First cross-tabulate batch against the biological variable; if they are collinear, stop - the effect is unrecoverable. Otherwise correct PER OMIC (ComBat on transformed data, ComBat-seq on counts) when the integrator needs clean input, OR model batch as a covariate inside the downstream step - never both, and never on a stacked multi-omic matrix.

```r
library(sva)

with(as.data.frame(colData(mae)), table(Batch, Condition))   # confounding gate: any empty cell = collinear -> do NOT correct

mod <- model.matrix(~ Condition, data=as.data.frame(colData(mae)))   # protect biology
vst_rna_bc <- ComBat(dat=vst_rna, batch=colData(mae)$Batch, mod=mod, par.prior=TRUE)   # ONE omic at a time
```

Stacking RNA, protein, and methylation into one matrix and running a single ComBat (with omic-type as the batch or a covariate) is a failure mode, not a recipe: it treats cross-omic differences as noise and erases the very signal the integration is meant to find. MOFA's multi-group `group=` is also not batch correction - it asks whether the same factors operate within each group, and does not regress batch out.

## Missing-Value Triage

**Goal:** Match the imputation to the missingness mechanism, and never fabricate a whole assay.

**Approach:** Separate the three regimes - missing features (filter), missing values within a feature (impute by mechanism: MNAR below detection vs MAR sporadic), and whole missing samples (do not impute; use a missing-tolerant integrator). Proteomics/metabolomics missingness is largely MNAR (a peptide is absent because it is low), so MAR methods bias it upward.

```r
keep <- rowMeans(is.na(norm_prot)) < 0.30          # drop features missing in >30% of samples before imputing
prot_f <- norm_prot[keep, ]

library(imputeLCMD)
prot_mnar <- impute.QRILC(prot_f)[[1]]             # left-censored draw for below-detection (MNAR) gaps
```

For a mosaic cohort (a subject profiled for RNA and methylation but not proteomics), do not impute the missing proteomics profile - MOFA2 ignores missing entries in its likelihood and tolerates incomplete views natively, so route that case to mofa-integration rather than fabricating a block that would manufacture cross-omic correlation.

## Per-Method Failure Modes

### Mismatched scales fed to a shared-latent method
**Trigger:** stacking raw counts, betas, and z-scores into one factorization. **Mechanism:** the model assumes comparable, homoscedastic, roughly-Gaussian features. **Symptom:** the leading factors are dominated by the highest-dynamic-range block; small blocks never surface. **Fix:** per-omic transform then per-view scaling, in that order.

### Per-feature scaling inflating noise
**Trigger:** mixOmics `scale=TRUE` (its default) on unfiltered blocks. **Mechanism:** a near-constant feature's tiny SD is divided out, blowing it up to unit variance. **Symptom:** a factor built from technical jitter at the detection floor. **Fix:** filter near-constant features before any per-feature scaling; prefer per-view scaling for cross-block equalization.

### Correcting confounded batch
**Trigger:** ComBat with batch correlated with (or equal to) the condition. **Mechanism:** the batch and biology terms are collinear, so the correction has no way to separate them. **Symptom:** the condition effect vanishes after correction. **Fix:** cross-tabulate batch x condition first; if collinear, do not correct - the design cannot be rescued post hoc.

### Double-correcting batch
**Trigger:** ComBat per omic AND a batch term inside the integration/DE step. **Mechanism:** the second correction operates on residuals already partly stripped. **Symptom:** over-shrunk effects and inflated confidence. **Fix:** correct once, in one place; prefer modeling for inferential steps, scrubbing only when the tool cannot accept a covariate.

### MAR imputation on MNAR data
**Trigger:** kNN/missForest on below-detection proteomics gaps. **Mechanism:** MAR methods borrow toward the observed mean, but the missing values are low by definition. **Symptom:** low-abundance proteins biased upward; the low-abundance biology is erased. **Fix:** QRILC/MinProb for MNAR entries, kNN/missForest only for sporadic MAR gaps.

### Feature filter treated as housekeeping
**Trigger:** top-N HVG / variable-feature selection per omic applied without justification. **Mechanism:** an integration model can only place a feature on a latent factor if the feature is in the input, so the cutoff pre-commits which axes of variation can be discovered. **Symptom:** two analysts with different cutoffs fit different models and get different factors; a real low-variance signal silently cannot appear. **Fix:** treat the filter as a modeling choice - declare and justify it, filter the wider views harder to equalize dimensionality, and confirm the headline factors are stable across a sensible cutoff range.

### Whole-sample imputation to satisfy a complete-case method
**Trigger:** imputing an entire missing omic profile so DIABLO/CCA will run. **Mechanism:** the imputed block is reconstructed from the other omics. **Symptom:** "discovered" cross-omic correlation that the imputation manufactured. **Fix:** use MOFA2 (models the missingness) or restrict to overlapping samples; never fabricate a whole assay.

### Orientation transpose and one-to-many ID mapping
**Trigger:** exporting an MAE assay to Python, or joining omics on gene symbols. **Mechanism:** Bioconductor is samples-in-columns while AnnData/mixOmics are samples-in-rows; symbols are non-unique and IDs map one-to-many. **Symptom:** genes treated as samples (silent), or duplicated/lost rows after a merge. **Fix:** assert matrix shape after every cross-language hop; join on Ensembl/UniProt/RefMet, and decide the collapse rule for ambiguous mappings explicitly.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Per-view scaling (not per-feature) for cross-block equalization | Escofier 1994 *Comput Stat Data Anal* 18:121 (MFA) | equalizes block contribution without inflating individual noise features |
| Near-constant feature filter (sd > ~1e-8) before per-feature scaling | mixOmics docs | per-feature unit-variance scaling blows up zero-variance features |
| Feature missingness filter ~30-50% before imputing | Lazar 2016 *J Proteome Res* 15:1116 | a feature missing in most samples cannot be imputed reliably |
| Batch x condition cross-tab must have no empty cell before ComBat | Nygaard 2016 *Biostatistics* 17:29 | an empty cell means batch and biology are collinear and inseparable |
| Model batch as covariate (not scrub) for inferential steps | Nygaard 2016 *Biostatistics* 17:29 | scrub-then-test understates variance and exaggerates significance |
| M-values (not beta) for methylation modeling | Du 2010 *BMC Bioinformatics* 11:587 | beta is heteroscedastic; the logit is approximately homoscedastic |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| One omic dominates every shared factor | no per-view scaling / unequal feature counts | per-view scale; filter the wider view harder |
| A factor is built from low-signal features | per-feature scaling without filtering | drop near-constant features before scaling |
| Condition effect disappears after batch correction | batch confounded with condition | check the cross-tab; do not correct collinear designs |
| Low-abundance proteins look unexpectedly high | MAR imputation on MNAR gaps | QRILC/MinProb for below-detection values |
| Cross-omic correlation that does not replicate | whole-sample imputation | use MOFA missing-view handling; do not fabricate a block |
| Genes appear as samples after export | orientation flip across languages | transpose; assert shape after every hop |

## References

- Ramos M, Schiffer L, Re A, et al. 2017. Software for the integration of multiomics experiments in Bioconductor. *Cancer Res* 77:e39-e42.
- Du P, Zhang X, Huang C-C, et al. 2010. Comparison of Beta-value and M-value methods for quantifying methylation levels by microarray analysis. *BMC Bioinformatics* 11:587.
- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biol* 15:550.
- Gloor GB, Macklaim JM, Pawlowsky-Glahn V, Egozcue JJ. 2017. Microbiome datasets are compositional: and this is not optional. *Front Microbiol* 8:2224.
- Escofier B, Pages J. 1994. Multiple factor analysis (AFMULT package). *Comput Stat Data Anal* 18:121-140.
- Johnson WE, Li C, Rabinovic A. 2007. Adjusting batch effects in microarray expression data using empirical Bayes methods. *Biostatistics* 8:118-127.
- Zhang Y, Parmigiani G, Johnson WE. 2020. ComBat-seq: batch effect adjustment for RNA-seq count data. *NAR Genom Bioinform* 2:lqaa078.
- Ritchie ME, Phipson B, Wu D, et al. 2015. limma powers differential expression analyses for RNA-sequencing and microarray studies. *Nucleic Acids Res* 43:e47.
- Leek JT, Storey JD. 2007. Capturing heterogeneity in gene expression studies by surrogate variable analysis. *PLoS Genet* 3:e161.
- Risso D, Ngai J, Speed TP, Dudoit S. 2014. Normalization of RNA-seq data using factor analysis of control genes or samples. *Nat Biotechnol* 32:896-902.
- Lazar C, Gatto L, Ferro M, Bruley C, Burger T. 2016. Accounting for the multiple natures of missing values in label-free quantitative proteomics data sets to compare imputation strategies. *J Proteome Res* 15:1116-1125.
- Nygaard V, Rodland EA, Hovig E. 2016. Methods that remove batch effects while retaining group differences may lead to exaggerated confidence in downstream analyses. *Biostatistics* 17:29-39.

## Related Skills

- integration-design - The method-selection decision this harmonization feeds
- mofa-integration - Consumes harmonized blocks; models missing-view samples natively
- mixomics-analysis - Consumes harmonized blocks; needs complete cases and is per-feature scaled
- similarity-network - Consumes harmonized blocks for patient stratification
- differential-expression/batch-correction - Single-omic RNA-seq batch mechanics (ComBat/limma)
- methylation-analysis/array-preprocessing - Methylation beta/M-value normalization
- proteomics/proteomics-qc - Proteomics normalization and QC
- metabolomics/normalization-qc - Metabolomics normalization and scaling
- metagenomics/abundance-estimation - Compositional/CLR theory for compositional omics
<!-- END FILE: multi-omics-integration/data-harmonization/SKILL.md -->

## 子目录：multi-omics-integration/integration-design

<!-- BEGIN FILE: multi-omics-integration/integration-design/SKILL.md -->
---
name: bio-multi-omics-integration-design
description: Chooses a bulk multi-omics integration strategy before any tool runs by mapping the biological question (subtype discovery, shared axis of variation, predictive signature, pairwise correlation) to a method class, naming the sample correspondence (paired-vertical, horizontal, mosaic, diagonal), enforcing the n<<p discipline that makes a held-out cohort the endpoint instead of in-cohort cross-validation, and running the per-view variance-imbalance diagnostic. Covers the early/mixed/intermediate/late taxonomy, why vertical and horizontal integration are different problems, and why a shared factor dominated by one omic is not integration. Use when deciding which integration method fits a question, whether data is paired or mosaic, supervised or unsupervised, or how to validate an integrated result. For unsupervised factors see mofa-integration; for supervised signatures see mixomics-analysis; for stratification see similarity-network; for single-cell see single-cell/multimodal-integration.
tool_type: r
primary_tool: MultiAssayExperiment
---

## Version Compatibility

Reference examples tested with: MultiAssayExperiment 1.36+, SummarizedExperiment 1.40+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The tool versions that matter most are MOFA2 and mixOmics, whose APIs have moved across releases; this skill routes to those tool skills rather than calling them, so the binding version here is MultiAssayExperiment (the container in which the paired-vs-mosaic decision is made).

# Multi-Omics Integration Design

**"How should I integrate these omics?"** -> Map the biological question and the sample correspondence to a method class BEFORE running a tool - because at tens of samples and 10^5-10^6 features a spurious cross-omic signal is the default outcome, not the surprise.
- R: assemble a `MultiAssayExperiment`, then choose MOFA2 (shared factors) / mixOmics (signature) / SNF (subtypes) by question

Scope: the integration decision itself - method selection, correspondence (paired/horizontal/mosaic/diagonal), supervised-vs-unsupervised mapping, the n<<p discipline, and the variance-imbalance diagnostic. Running the chosen tool -> mofa-integration, mixomics-analysis, similarity-network. Cross-omic preprocessing -> data-harmonization. Single-cell multimodal -> single-cell/multimodal-integration. Horizontal same-feature meta-analysis -> differential-expression/batch-correction.

## The Single Most Important Modern Insight -- Bulk Multi-Omics Is a Small-n, Huge-p Discovery Problem Where a Spurious Cross-Omic Signal Is the Default

A typical bulk cohort has n = 30-300 samples and 10^4-10^6 features per omic, so after stacking blocks n is smaller than p by three to four orders of magnitude. In that regime an integrated signature that has not been validated out-of-sample is overwhelmingly noise that fit the training samples. The deliverable is never "the integrated signature" - it is question-matched structure that survives three gates, each of which a common failure violates:

1. **The correspondence gate.** Vertical integration (different omics, SAME samples) and horizontal integration (same features, different cohorts) are different problems. The bulk joint-latent tools are indexed by sample; feed them unpaired same-feature data and they still run but emit factors that are pure batch. Name the correspondence first.
2. **The variance gate.** Total variance scales with feature count and feature scale, so a 850k-CpG block out-votes a 100-metabolite block and the shared factors become methylation PCs. Inspect the per-factor, per-view variance-explained table every time; if one view dominates every shared factor, the integration re-discovered the biggest omic.
3. **The validation gate.** With n = 40 and 5-fold CV each fold tests 8 samples, so in-cohort cross-validation is optimistically biased to the point of fiction. An integrated subtype or signature is not credible until it reproduces in an INDEPENDENT cohort. The held-out cohort is the finding.

Organize the analysis around defending these three gates, not around picking a favorite tool.

## The Integration Taxonomy -- Three Orthogonal Axes, Not One Label

A method is a point in a 3D space, not a single name. Stating where a method sits on each axis prevents the category's two deepest errors (horizontal/vertical confusion and concatenation at n<<p).

| Axis | Values | What it decides |
|------|--------|-----------------|
| Stage - WHEN blocks combine (Ritchie 2015, Picard 2021) | early (concatenate then model), mixed (transform each block then combine), intermediate (jointly model blocks into shared + specific factors), late (model each omic, combine results) | early is worst at n<<p and variance imbalance; intermediate joint-latent (MOFA/JIVE/iCluster) is the discovery sweet spot; late is robust to missing blocks but drops feature-level cross-talk |
| Correspondence - WHAT is tied together (Argelaguet 2021) | vertical (diff omics, same samples - THIS category), horizontal (same features, diff cohorts - meta-analysis), mosaic (partial overlap), diagonal (no shared axis - single-cell) | conflating horizontal and vertical is the deepest category error; only vertical and mosaic belong here |
| Supervision - WHETHER an outcome drives it | unsupervised (discover subtypes/factors), supervised (predict/discriminate a label) | unsupervised plus then-correlate-with-outcome is hypothesis-generating, NOT a validated predictor |

MOFA = intermediate, vertical, unsupervised. DIABLO = intermediate, vertical, supervised. SNF = mixed/transformation, vertical, unsupervised. ComBat-across-cohorts = horizontal, unsupervised harmonization (routes OUT to differential-expression/batch-correction).

## Tool Taxonomy

| Tool / class | Citation | Stage / supervision | When |
|--------------|----------|---------------------|------|
| MOFA2 | Argelaguet 2018 *Mol Syst Biol* 14:e8124; Argelaguet 2020 *Genome Biol* 21:111 | intermediate, unsupervised | shared vs view-specific factors; tolerant of missing omics-per-sample; the default factor model -> mofa-integration |
| mixOmics DIABLO (`block.splsda`) | Singh 2019 *Bioinformatics* 35:3055; Rohart 2017 *PLoS Comput Biol* 13:e1005752 | intermediate, supervised | sparse cross-omic signature that DISCRIMINATES known groups -> mixomics-analysis |
| mixOmics sPLS (`spls`) | Rohart 2017 *PLoS Comput Biol* 13:e1005752 | intermediate, unsupervised | covariance-maximizing feature pairs between TWO blocks -> mixomics-analysis |
| mixOmics MINT (`mint.splsda`) | Rohart 2017 *BMC Bioinformatics* 18:128 | horizontal | SAME omic across multiple STUDIES (study as a known effect) - not cross-omic |
| SNF (SNFtool) | Wang 2014 *Nat Methods* 11:333 | mixed/transformation, unsupervised | patient stratification; feature count buys no votes; robust as complexity grows -> similarity-network |
| iCluster / iClusterPlus / moCluster | Shen 2009 *Bioinformatics* 25:2906; Meng 2016 *J Proteome Res* 15:755 | intermediate, unsupervised | ONE joint-latent clustering (vs reconciling K separate clusterings); subtype discovery |
| JIVE | Lock 2013 *Ann Appl Stat* 7:523 | intermediate, unsupervised | explicit joint + individual + noise decomposition (how much signal is cross-omic) |
| MFA / mixKernel | Mariette 2018 *Bioinformatics* 34:1009 | mixed | block weighting / kernel fusion to stop one omic dominating |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Different omics on the SAME samples, no phenotype, find shared axes | MOFA2 | unsupervised factor model; variance decomposition; native missing-block handling -> mofa-integration |
| Different omics on the same samples, want patient SUBTYPES | SNF + spectral clustering (or iCluster) | transformation-stage; robust to high p and a noisy omic -> similarity-network |
| Have a class label, want a cross-omic signature that discriminates it | mixOmics DIABLO + held-out cohort | supervised sparse multi-block PLS-DA -> mixomics-analysis |
| Just two omics, want correlated feature pairs | mixOmics sPLS | sparse PLS for a block pair -> mixomics-analysis |
| Quantify how much variation is joint vs omic-specific | JIVE (or the MOFA variance table) | explicit joint/individual split |
| SAME omic across multiple studies/cohorts | -> differential-expression/batch-correction or mixOmics MINT | horizontal integration / meta-analysis, NOT cross-omic |
| Mosaic cohort (some samples missing an omic) | MOFA2 (models the missingness) | intersecting to complete cases wastes scarce n -> data-harmonization |
| Single-cell CITE-seq / 10x Multiome / unpaired diagonal | -> single-cell/multimodal-integration | per-cell generative models; n is large; different paradigm |
| Per-omic DE then overlap the hit lists | -> differential-expression, methylation-analysis, proteomics | that is late integration by intersection, not joint modeling |
| Validate a discovered subtype against outcome | -> clinical-biostatistics/survival-analysis | survival / KM / Cox lives there |

Default when uncertain: assemble a `MultiAssayExperiment`, confirm vertical paired (or mosaic) correspondence, run MOFA2 for an unsupervised map and read its per-view variance-explained table, then escalate to a supervised (DIABLO) or stratification (SNF) tool only if the question demands it.

## Name the Correspondence First

**Goal:** Decide whether the data is a job for this category at all, and whether to model the missingness or intersect to complete cases.

**Approach:** Assemble the blocks into a `MultiAssayExperiment` (it coordinates assays, a sample map, and colData), then read off whether samples are fully paired, mosaic, or actually horizontal. Only vertical-paired and mosaic belong here.

```r
library(MultiAssayExperiment)

mae <- MultiAssayExperiment(experiments=ExperimentList(rna=rna_mat, prot=prot_mat, methyl=methyl_mat),
                            colData=clinical)
upsetSamples(mae)                 # visualize which samples have which omics (mosaic structure)
table(complete.cases(mae))        # how many samples have EVERY omic
paired <- intersectColumns(mae)   # complete-case fallback - counts the n it would cost
```

If `complete.cases` keeps most samples, complete-case methods (mixOmics, SNF) are fine. If a large fraction is mosaic, prefer MOFA2 (it models missing-view samples in its likelihood) over intersecting, because at n<<p discarding incomplete samples is expensive and imputing a whole block fabricates data (data-harmonization owns that decision).

## The Variance-Imbalance Diagnostic

**Goal:** Detect, before trusting any shared factor, whether one omic is set to dominate the integration purely because it has more features or larger scale.

**Approach:** After per-feature scaling, compare each block's total variance and feature count; a block contributing the overwhelming majority of stacked variance will hijack the shared latent space. The definitive check is the per-view variance-explained table that MOFA2 reports after fitting - if every factor loads on one view, equalize the blocks (MFA weighting, per-block keepX, or move to SNF) and refit.

```r
block_var <- sapply(assays_list, function(x) sum(apply(x, 1, var)))   # total variance per block
share     <- block_var / sum(block_var)
share                                                                 # any block >> others = imbalance risk
```

A block holding most of the stacked variance is a red flag that concatenation-style integration will re-discover it. This is the single best honesty check in the category; never skip the post-fit per-view variance read-out.

## The n<<p Discipline

The held-out cohort is the endpoint, not in-cohort cross-validation. Three rules follow from n<<p:

- **Tune with repeated cross-validation, never a single run.** At n = 40 a single CV estimate is mostly noise; mixOmics `perf`/`tune.*` take `nrepeat` (10-50) - use it. Generic CV/overfitting theory lives in machine-learning/model-validation.
- **Report out-of-sample performance, not the in-sample fit.** A supervised signature's training-set discrimination is guaranteed by construction; only an independent cohort makes it a biomarker.
- **An unsupervised factor that correlates with the outcome is a hypothesis.** MOFA found it without the label, which is a strength - but calling it predictive requires held-out validation, not the in-cohort correlation that found it.
- **Prefer regularized/sparse methods over early concatenation plus plain CCA.** Classical CCA divides out within-block variance and, when p > n, achieves correlation 1 trivially by overfitting; sparse PLS (covariance plus an L1 penalty) and sparse factor models stay identifiable, so the regularization is what makes the fit real, not a stylistic choice.

## Per-Method Failure Modes

### Horizontal data fed to a vertical method
**Trigger:** running MOFA/DIABLO/SNF on same-feature, multi-cohort data ("integrate my three RNA-seq studies"). **Mechanism:** the shared latent is indexed by sample and has nothing to align across feature-identical cohorts. **Symptom:** the tool runs and the top factors track cohort/run, not biology. **Fix:** recognize this as horizontal integration; use MINT, ComBat/sva, or differential-expression/batch-correction.

### Unvalidated in-cohort signature reported as a result
**Trigger:** reporting a DIABLO panel or a MOFA-factor-vs-outcome correlation from one cohort. **Mechanism:** at n<<p thousands of cross-omic feature pairs clear any threshold under the null; in-cohort CV is optimistically biased. **Symptom:** a beautiful signature that fails to replicate. **Fix:** hold out an independent cohort; frame an unvalidated finding as hypothesis-generating, never as a biomarker.

### Variance imbalance mistaken for integration
**Trigger:** concatenating blocks of very different feature counts/scales without equalization. **Mechanism:** the high-feature/high-variance omic casts the most votes for the shared factors. **Symptom:** every shared factor loads almost entirely on one view. **Fix:** read the per-view variance-explained table; equalize via MFA weighting / per-block keepX / per-feature z-scoring, or use SNF where each omic is one n x n network.

### Question-method mismatch
**Trigger:** using a tool whose output does not answer the question (e.g. SNF clusters reported with "driver features"). **Mechanism:** SNF selects no features, MOFA is unsupervised, DIABLO needs a label. **Symptom:** claims the method cannot support (SNF drivers without a post-hoc per-omic test; MOFA factors called predictive). **Fix:** map question -> class first (decision tree); do post-hoc per-omic differential analysis to find SNF subtype drivers.

### Cross-omic batch masquerading as shared biology
**Trigger:** omics generated on different platforms/labs/dates, interpreted without a technical check. **Mechanism:** the samples that ran together in every assay form a shared technical axis. **Symptom:** the top shared factor tracks run date / plate / site better than phenotype. **Fix:** correlate top factors against technical covariates before interpreting; correct per omic or model batch as a covariate (data-harmonization), watching for over-correction.

### Mosaic cohort forced to complete cases
**Trigger:** `intersectColumns` on a mosaic cohort before integrating. **Mechanism:** complete-case intersection drops every sample missing any omic. **Symptom:** n halves and power collapses. **Fix:** prefer MOFA2's native missing-view handling; reserve intersection for when mosaicism is minor.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| n<<p by ~3-4 orders of magnitude is the default regime | Subramanian 2020 *Bioinform Biol Insights* 14 | tens of samples, 10^4-10^6 features; dictates regularized/sparse methods and held-out validation |
| Repeated CV `nrepeat` 10-50 for any tuning at small n | mixOmics docs; n<<p variance | a single CV run at n~40 is noise; repetition stabilizes the estimate |
| Per-view variance-explained dominance flag: one view >~80% of every shared factor | Argelaguet 2018 *Mol Syst Biol* 14:e8124 (per-view variance decomposition) | a factor dominated by one view is view-specific structure, not integration |
| Drop MOFA factors below ~1-2% variance explained in every view | Argelaguet 2018 *Mol Syst Biol* 14:e8124 | low-variance factors are noise/over-parameterization |
| Held-out independent cohort for any reported biomarker/subtype | Subramanian 2020 *Bioinform Biol Insights* 14 | in-cohort CV at n<<p is optimistically biased; replication is the endpoint |
| Cross-check the headline with a second method class | Cantini 2021 *Nat Commun* 12:124; Tini 2019 *Brief Bioinform* 20:1269; Pierre-Jean 2020 *Brief Bioinform* 21:2011 | no single best method and methods diverge; a real result should survive a second class (e.g. a factor model and a fusion clustering) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Tool runs on multi-cohort data but factors are all batch | horizontal data in a vertical method | use MINT / ComBat; this is meta-analysis, not cross-omic integration |
| n drops sharply after assembling the object | complete-case intersection on a mosaic cohort | use MOFA2 missing-view handling; intersect only if mosaicism is minor |
| Shared factors explain mostly one omic | variance imbalance (feature count / scale) | equalize blocks (MFA / per-block keepX / z-score) or use SNF |
| Signature does not replicate in a new cohort | reported from in-cohort CV at n<<p | hold out an independent cohort before claiming a biomarker |
| Two methods give different subtypes | method-dependent result (benchmarks rank methods differently because each optimizes a different criterion - robustness vs clustering recovery vs feature selection) | report which method and why; cross-check; no universal best method |

## References

- Ritchie MD, Holzinger ER, Li R, Pendergrass SA, Kim D. 2015. Methods of integrating data to uncover genotype-phenotype interactions. *Nat Rev Genet* 16:85-97.
- Picard M, Scott-Boyer M-P, Bodein A, Perin O, Droit A. 2021. Integration strategies of multi-omics data for machine learning analysis. *Comput Struct Biotechnol J* 19:3735-3746.
- Argelaguet R, Cuomo ASE, Stegle O, Marioni JC. 2021. Computational principles and challenges in single-cell data integration. *Nat Biotechnol* 39:1202-1215.
- Argelaguet R, Velten B, Arnol D, et al. 2018. Multi-Omics Factor Analysis - a framework for unsupervised integration of multi-omics data sets. *Mol Syst Biol* 14:e8124.
- Argelaguet R, Arnol D, Bredikhin D, et al. 2020. MOFA+: a statistical framework for comprehensive integration of multi-modal single-cell data. *Genome Biol* 21:111.
- Shen R, Olshen AB, Ladanyi M. 2009. Integrative clustering of multiple genomic data types using a joint latent variable model with application to breast and lung cancer subtype analysis. *Bioinformatics* 25:2906-2912.
- Lock EF, Hoadley KA, Marron JS, Nobel AB. 2013. Joint and individual variation explained (JIVE) for integrated analysis of multiple data types. *Ann Appl Stat* 7:523-542.
- Meng C, Helm D, Frejno M, Kuster B. 2016. moCluster: identifying joint patterns across multiple omics data sets. *J Proteome Res* 15:755-765.
- Mariette J, Villa-Vialaneix N. 2018. Unsupervised multiple kernel learning for heterogeneous data integration. *Bioinformatics* 34:1009-1016.
- Rohart F, Gautier B, Singh A, Le Cao K-A. 2017. mixOmics: an R package for 'omics feature selection and multiple data integration. *PLoS Comput Biol* 13:e1005752.
- Singh A, Shannon CP, Gautier B, et al. 2019. DIABLO: an integrative approach for identifying key molecular drivers from multi-omics assays. *Bioinformatics* 35:3055-3062.
- Wang B, Mezlini AM, Demir F, et al. 2014. Similarity network fusion for aggregating data types on a genomic scale. *Nat Methods* 11:333-337.
- Tini G, Marchetti L, Priami C, Scott-Boyer M-P. 2019. Multi-omics integration - a comparison of unsupervised clustering methodologies. *Brief Bioinform* 20:1269-1279.
- Cantini L, Zakeri P, Hernandez C, et al. 2021. Benchmarking joint multi-omics dimensionality reduction approaches for the study of cancer. *Nat Commun* 12:124.
- Pierre-Jean M, Deleuze J-F, Le Floch E, Mauger F. 2020. Clustering and variable selection evaluation of 13 unsupervised methods for multi-omics data integration. *Brief Bioinform* 21:2011-2030.
- Subramanian I, Verma S, Kumar S, Jere A, Anamika K. 2020. Multi-omics data integration, interpretation, and its application. *Bioinform Biol Insights* 14:1177932219899051.

## Related Skills

- mofa-integration - Unsupervised shared-factor discovery (the default tool once correspondence is vertical)
- mixomics-analysis - Supervised DIABLO signatures, sPLS pairs, and MINT multi-study integration
- similarity-network - Patient stratification via similarity network fusion
- data-harmonization - Per-block normalization, scaling, batch, and the mosaic missing-omic decision
- single-cell/multimodal-integration - Single-cell CITE-seq/Multiome integration (different paradigm)
- differential-expression/batch-correction - Horizontal same-feature meta-analysis and batch correction
- machine-learning/model-validation - Cross-validation and overfitting theory for supervised integration
- clinical-biostatistics/survival-analysis - Survival validation of discovered subtypes
- pathway-analysis/gsea - Enrichment of integrated factor or signature features
- workflows/multi-omics-pipeline - End-to-end multi-omics integration pipeline
<!-- END FILE: multi-omics-integration/integration-design/SKILL.md -->

## 子目录：multi-omics-integration/mixomics-analysis

<!-- BEGIN FILE: multi-omics-integration/mixomics-analysis/SKILL.md -->
---
name: bio-multi-omics-mixomics-analysis
description: Builds supervised and unsupervised multivariate integration across bulk omics blocks with mixOmics - sPLS for sparse pairwise correlation, DIABLO (block.splsda) for a multi-block discriminant signature, rCCA for regularized canonical correlation, and MINT for multi-study integration. Covers why these projection methods maximize covariance or correlation and not truth, why DIABLO's design matrix is the central correlation-versus-discrimination decision, why cross-validation must wrap keepX selection or the reported error is leaked, why balanced error rate is required under class imbalance, and why DIABLO needs matched samples while MINT handles multiple cohorts. Use when finding a cross-omic discriminant signature for a known outcome, selecting correlated features between two omics, tuning keepX, or integrating one omic across studies. For unsupervised factors see mofa-integration; for the method decision see integration-design; for cross-validation theory see machine-learning/model-validation.
tool_type: r
primary_tool: mixOmics
---

## Version Compatibility

Reference examples tested with: mixOmics 6.26+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('mixOmics')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The DIABLO model is `block.splsda` - there is no function literally named `diablo`. mixOmics input is samples-by-features (the opposite of MOFA2's features-by-samples), and `scale=TRUE` is the default, so feed appropriately transformed but not pre-standardized matrices.

# mixOmics Multi-Omics Analysis

**"Find a cross-omic signature that discriminates my groups"** -> Project the blocks onto sparse latent components that maximize an association criterion - because these methods maximize covariance, not truth, so a signature that discriminates the training cohort is guaranteed and only out-of-sample replication makes it real.
- R: `block.splsda()` (DIABLO, supervised), `spls()` (pairwise), `mint.splsda()` (multi-study)

Scope: supervised multi-block discriminant integration (DIABLO), sparse pairwise correlation (sPLS), regularized CCA (rCCA), and multi-study integration (MINT). Unsupervised factor models -> mofa-integration. The method-selection decision -> integration-design. Generic cross-validation / leakage theory -> machine-learning/model-validation. Per-omic scaling/batch -> data-harmonization. Enrichment of selected features -> pathway-analysis/go-enrichment.

## The Single Most Important Modern Insight -- DIABLO Maximizes Covariance, Not Truth, So a Signature Scored on the Data That Selected It Is an Artifact

These are projection methods: they find linear combinations of features that optimize an association criterion (covariance for PLS/DIABLO, correlation for CCA), and DIABLO additionally optimizes whatever the design matrix tells it to. With n much smaller than p the methods can fit almost anything, so the output is never "the cross-omic drivers of the disease" - it is the features that best satisfied the chosen criterion on the available samples. Three rules follow:

1. **Cross-validation must wrap feature selection, not follow it.** Tuning keepX on the full data and then reporting `perf()` cross-validation error on the same data is leakage (up to ~0.15 AUC inflation). mixOmics selects inside folds when tuning, which is correct for choosing keepX - but the minimized CV error it returns is still optimistic. The honest number comes from an external test set never touched during tuning, or a fully nested CV.
2. **The design matrix is the central decision, not a default.** The off-diagonal weights in [0,1] trade discrimination against cross-block correlation: near 1 gives biologically coherent, inter-correlated signatures at the cost of classification; near 0 gives the best classification with a disconnected network. The tutorials' 0.1 leans toward prediction and is not a recommendation from the DIABLO paper - choose it from the goal and report it.
3. **The selected features are candidates, not biomarkers.** selectVar discriminates the training cohort by construction; that is the null result, not the finding. Replication in an independent cohort (or MINT across studies) is the finding.

## Tool Taxonomy

| Method (mixOmics fn) | Citation | Optimizes | Supervision |
|----------------------|----------|-----------|-------------|
| sPLS (`spls`) | Le Cao 2008 *Stat Appl Genet Mol Biol* 7:Article 35 | covariance between TWO blocks, sparse | unsupervised pairwise |
| rCCA (`rcc`) | Gonzalez 2008 *J Stat Softw* 23(12) | correlation between two blocks, ridge/shrinkage regularized | unsupervised pairwise |
| DIABLO (`block.splsda`) | Singh 2019 *Bioinformatics* 35:3055 | covariance across MANY blocks + discrimination, sparse | supervised, multi-block |
| MINT (`mint.splsda`) | Rohart 2017 *BMC Bioinformatics* 18:128 | one omic across studies, study as fixed effect | supervised, horizontal |
| sPLS-DA (`splsda`) | Le Cao 2011 *BMC Bioinformatics* 12:253 | discrimination in ONE block, sparse | supervised, single-block |
| sPCA (`spca`) | Shen 2008 *J Multivar Anal* 99:1015 | variance in one block, sparse | unsupervised, single-block |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Two or more omics, matched samples, a categorical outcome | DIABLO (`block.splsda`) | supervised multi-block; design tunes correlation vs discrimination |
| Two omics, no outcome, want a sparse correlated feature list | sPLS canonical (`spls`, mode='canonical') | covariance, symmetric, feature selection |
| Two omics, no outcome, want the global correlation landscape | rCCA (`rcc`, shrinkage) | correlation criterion, regularized for p>n |
| One omic predicts another (directional) | sPLS regression (`spls`, mode='regression') | asymmetric, Y as response |
| SAME omic across multiple cohorts, reproducible signature | MINT (`mint.splsda`) | horizontal; study as a fixed effect |
| No outcome, want variance-attributed factors, missing blocks OK | -> mofa-integration | Bayesian factor model, not a projection |
| Need an honest performance number | external test set or nested CV | the tuned CV error is optimistic |
| Which method at all / paired vs horizontal | -> integration-design | the correspondence and supervision decision |

## Set Up Matched Blocks

**Goal:** Guarantee the row-by-row sample matching DIABLO/sPLS/rCCA require, so the model correlates feature vectors of the same individuals.

**Approach:** Intersect to common samples and verify identical rowname order across every block; for combining one omic across cohorts, that is horizontal integration and needs MINT, not DIABLO.

```r
library(mixOmics)

common <- Reduce(intersect, list(rownames(X_rna), rownames(X_prot)))   # samples x features
X_blocks <- list(RNA=X_rna[common, ], Protein=X_prot[common, ])
Y <- factor(pheno[common, 'Condition'])
stopifnot(identical(rownames(X_blocks$RNA), rownames(X_blocks$Protein)))   # matched rownames or the result is garbage
```

## sPLS: Sparse Pairwise Correlation

**Goal:** Select a sparse set of features that covary between two omics.

**Approach:** Choose `mode` deliberately - 'canonical' for two omics on equal footing (the CCA-like symmetric framing), 'regression' (the default) only when one block is a designated response. Tune component count, then fit with keepX/keepY feature selection.

```r
spls_res <- spls(X_blocks$RNA, X_blocks$Protein, ncomp=3, mode='canonical',   # symmetric; default 'regression' treats Protein as a response of RNA
                 keepX=c(50, 50, 50), keepY=c(30, 30, 30))
plotVar(spls_res, comp=c(1, 2))
```

## DIABLO: Supervised Multi-Block Signature

**Goal:** Find a cross-omic feature signature that discriminates a known outcome, with the correlation-versus-discrimination trade-off chosen and reported.

**Approach:** Set the design matrix from the goal (high off-diagonal for coherent networks, low for prediction), tune the component count on a non-sparse model, tune keepX inside cross-validation folds using balanced error rate, fit, then report performance on an external set.

```r
design <- matrix(0.5, nrow=length(X_blocks), ncol=length(X_blocks),
                 dimnames=list(names(X_blocks), names(X_blocks)))   # 0.5-1 favors cross-block correlation; <0.5 favors prediction - choose from the goal
diag(design) <- 0

ncomp_fit <- perf(block.plsda(X_blocks, Y, ncomp=5, design=design),               # tune ncomp on a NON-sparse model first
                  validation='Mfold', folds=10, nrepeat=10)                       # nrepeat>=10; a single split is noise

tune <- tune.block.splsda(X_blocks, Y, ncomp=2, design=design,
                          test.keepX=list(RNA=c(10, 25, 50), Protein=c(10, 25, 50)),
                          validation='Mfold', folds=10, nrepeat=10,
                          measure='BER', BPPARAM=BiocParallel::MulticoreParam(workers=4))   # BER, not overall error, for imbalanced classes; cpus= is defunct, use BPPARAM
diablo <- block.splsda(X_blocks, Y, ncomp=2, keepX=tune$choice.keepX, design=design)
```

The features chosen here discriminate the training cohort by construction. For an honest accuracy, hold out an external test set never used in tuning and report `predict()` / `auroc()` on it; the `perf()` error on the tuning data is optimistic because keepX was chosen to minimize it.

## Interpret and Validate

**Goal:** Extract the signature as candidates and visualize cross-block structure without overclaiming.

**Approach:** Pull selected variables per block and component, inspect inter-block correlations, and frame the list as cohort-specific candidates requiring replication.

```r
sel_rna  <- selectVar(diablo, block='RNA', comp=1)$RNA$name        # candidate features, not validated biomarkers
circosPlot(diablo, cutoff=0.7)                                     # inter-block correlations of the selected features
auc <- auroc(diablo, roc.block='RNA', roc.comp=1)
```

## MINT: Multi-Study (Horizontal) Integration

**Goal:** Build a signature for ONE omic that replicates across cohorts by modeling study as a known effect.

**Approach:** Pass a study factor so the model accounts for study-specific variation; this is horizontal integration (same features, different cohorts), the opposite of DIABLO's vertical matched-sample design.

```r
mint_res <- mint.splsda(X=X_rna, Y=Y, study=study, ncomp=3, keepX=c(50, 50, 50))   # study = fixed effect; one omic, many cohorts
plotIndiv(mint_res, study='global', legend=TRUE)
```

## Per-Method Failure Modes

### CV that follows selection instead of wrapping it
**Trigger:** tuning keepX on all samples, then reporting `perf()` CV error on all samples. **Mechanism:** the features were chosen with knowledge of every sample, so no fold is truly held out. **Symptom:** an excellent CV error that collapses in a new cohort. **Fix:** external test set or nested CV; the number used to pick keepX is not an estimate of performance.

### Design matrix copied as a default
**Trigger:** using 0.1 (or any value) without choosing it. **Mechanism:** the off-diagonal trades discrimination against cross-block correlation. **Symptom:** a result marketed as "integrated" while the design told the model to ignore most cross-block correlation. **Fix:** choose the design from the goal, justify it, and ideally show the result under a high and a low weight.

### Un-regularized CCA on p>n
**Trigger:** running plain CCA on omics. **Mechanism:** CCA divides out variances and needs to invert a singular covariance, so it reports correlation 1.0 by overfitting. **Symptom:** perfect, meaningless canonical correlations. **Fix:** use `rcc` with ridge or shrinkage regularization, or sPLS canonical.

### Unmatched samples (or DIABLO where MINT is needed)
**Trigger:** partially overlapping or mis-ordered samples across blocks, or DIABLO on two cohorts of one omic. **Mechanism:** DIABLO/sPLS relate samples row-by-row. **Symptom:** garbage signatures from correlating different individuals. **Fix:** intersect and verify identical rowname order; use MINT for one omic across cohorts.

### Overall error under class imbalance
**Trigger:** tuning on overall classification error with imbalanced classes. **Mechanism:** the majority class dominates the metric. **Symptom:** high accuracy while the minority class is mis-predicted. **Fix:** `measure='BER'` and report per-class error.

### selectVar list presented as validated biomarkers
**Trigger:** calling the selected features mechanistic drivers. **Mechanism:** they discriminate the training cohort by construction. **Symptom:** a biomarker claim that fails to replicate. **Fix:** frame as cohort candidates; require external/cross-study replication.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Design off-diagonal: ~1 for coherence, <0.5 for prediction | Singh 2019 *Bioinformatics* 35:3055 | weights trade cross-block correlation against discrimination; 0.1 is tutorial convention only |
| `nrepeat` >= 10 (50 for a headline number) | mixOmics docs | a single M-fold split is high-variance; nrepeat=1 is illustration only |
| `folds` 5-10 in M-fold CV | mixOmics docs | balances bias and variance of the CV estimate at small n |
| `measure='BER'` for imbalanced classes | mixOmics docs | overall error is dominated by the majority class |
| `ncomp` 1-3, set by `perf()` elbow | Singh 2019 *Bioinformatics* 35:3055 | more components rarely help and risk overfit |
| External test set or nested CV for reported accuracy | machine-learning/model-validation | the tuned CV error is optimistically biased |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `could not find function "diablo"` | DIABLO is `block.splsda` | call `block.splsda`, not `diablo` |
| Perfect canonical correlations | un-regularized CCA on p>n | use `rcc` ridge/shrinkage |
| Reported accuracy fails in a new cohort | CV scored on tuning data | external test set or nested CV |
| `tune.block.splsda` very slow | grid too large / not parallelized | shrink `test.keepX`, set `BPPARAM` (cpus= is defunct) |
| High accuracy, minority class missed | overall error under imbalance | `measure='BER'` |
| Nonsense signature | unmatched/mis-ordered samples | intersect and verify rowname order |

## References

- Le Cao K-A, Rossouw D, Robert-Granie C, Besse P. 2008. A sparse PLS for variable selection when integrating omics data. *Stat Appl Genet Mol Biol* 7:Article 35.
- Le Cao K-A, Boitard S, Besse P. 2011. Sparse PLS discriminant analysis: biologically relevant feature selection and graphical displays for multiclass problems. *BMC Bioinformatics* 12:253.
- Gonzalez I, Dejean S, Martin PGP, Baccini A. 2008. CCA: an R package to extend canonical correlation analysis. *J Stat Softw* 23(12):1-14.
- Rohart F, Gautier B, Singh A, Le Cao K-A. 2017. mixOmics: an R package for 'omics feature selection and multiple data integration. *PLoS Comput Biol* 13:e1005752.
- Rohart F, Eslami A, Matigian N, Bougeard S, Le Cao K-A. 2017. MINT: a multivariate integrative method to identify reproducible molecular signatures across independent experiments and platforms. *BMC Bioinformatics* 18:128.
- Singh A, Shannon CP, Gautier B, et al. 2019. DIABLO: an integrative approach for identifying key molecular drivers from multi-omics assays. *Bioinformatics* 35:3055-3062.
- Shen H, Huang JZ. 2008. Sparse principal component analysis via regularized low rank matrix approximation. *J Multivar Anal* 99:1015-1034.

## Related Skills

- integration-design - The method-selection and paired-vs-horizontal decision
- mofa-integration - Unsupervised factor alternative where no outcome drives the fit
- data-harmonization - Per-block scaling and batch before matrices enter mixOmics
- machine-learning/model-validation - Nested cross-validation and data-leakage theory
- machine-learning/biomarker-discovery - Biomarker-panel selection and validation
- pathway-analysis/go-enrichment - Enrichment of the selected features
- differential-expression/de-results - Single-omic differential expression
- workflows/multi-omics-pipeline - End-to-end multi-omics integration pipeline
<!-- END FILE: multi-omics-integration/mixomics-analysis/SKILL.md -->

## 子目录：multi-omics-integration/mofa-integration

<!-- BEGIN FILE: multi-omics-integration/mofa-integration/SKILL.md -->
---
name: bio-multi-omics-mofa-integration
description: Discovers shared and view-specific latent factors across bulk multi-omics blocks (RNA-seq, proteomics, methylation) on a common sample axis with MOFA2's unsupervised Bayesian group factor model, then attributes per-view variance explained and interprets signed factor weights. Covers why a factor is an unsupervised axis of variance and not a pathway, why a factor that correlates with batch is a batch factor, why the per-view variance-explained table is the primary read-out rather than p-values, why raw counts in a Gaussian view make factor 1 the library-size factor, and why MOFA2 handles missing omics-per-sample natively. Use when integrating two or more bulk omics to find joint axes of variation, choosing factor count, labeling factors against metadata, or running enrichment on factor weights. For supervised discriminant integration see mixomics-analysis; for the method decision see integration-design; for single-cell see single-cell/multimodal-integration; for enrichment see pathway-analysis/gsea.
tool_type: r
primary_tool: MOFA2
---

## Version Compatibility

Reference examples tested with: MOFA2 1.12+ (Bioconductor), mofapy2 0.7+, muon 0.1+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('MOFA2')` then `?function_name` to verify parameters
- Python: `pip show mofapy2 muon` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

MOFA2 is R/Bioconductor and trains through the Python mofapy2 backend via basilisk/reticulate; the trained model serializes to an `.hdf5` file whose schema is version-coupled. The R defaults differ from the muon Python defaults (spikeslab_weights, ard_factors, seed 42 vs 1) - confirm per ecosystem.

# MOFA2 Integration

**"Find shared variation across my omics layers"** -> Learn unsupervised latent factors that decompose variation into shared and view-specific axes - because the factors are found WITHOUT the phenotype, so a factor need not separate the groups of interest, and the variance-explained table is the read-out.
- R: `create_mofa(data_list)` -> `prepare_mofa()` -> `run_mofa()`
- Python: `mofapy2` for training, `muon` / `mofax` for downstream

Scope: unsupervised cross-block factor modeling of bulk omics, variance decomposition, and signed-weight interpretation. Supervised discriminant integration -> mixomics-analysis. The method-selection decision -> integration-design. Per-omic normalization / HVG / transform-to-Gaussian -> data-harmonization. Enrichment mechanics -> pathway-analysis/gsea. Single-cell multimodal MOFA+ -> single-cell/multimodal-integration.

## The Single Most Important Modern Insight -- A MOFA Factor Is an Unsupervised Axis of Variance, Not a Pathway, and a Factor That Correlates With Batch Is a Batch Factor

MOFA is PCA generalized to multiple omics: it returns factor scores (Z), per-view loadings (W), and a variance decomposition (R^2 per factor per view) that says which axis is shared across modalities and which is view-specific. That decomposition is the output. Three properties every misuse forgets:

1. **Factors are unsupervised and blind to the phenotype.** MOFA never saw the groups, so "factor 3 separates cases from controls" is genuinely strong evidence - but only if K factors were not scanned to find the one that splits the groups. A factor becomes biology only after its weights are annotated, it correlates with a known covariate, and it is shown NOT to be a technical-covariate factor.
2. **MOFA greedily captures the largest variance.** An unregressed batch effect or a depth gradient is often the largest variance, so it becomes a top factor. Always run `correlate_factors_with_covariates` against batch/depth/plate and exclude technical factors from biological interpretation. A factor that tracks run date is a batch factor, not confounded biology.
3. **Factors are unordered and ARD-pruned.** Factor 1 is not "the most important" the way PC1 is. The honest deliverable is "factor k explains X% of variance in views {A,B}, its top weights enrich for pathway P at sign s, it correlates with covariate C and not with batch, and it recurs across seeds" - anything less is an axis dressed up as a finding.

## Tool Taxonomy (Unsupervised Integrators)

| Tool | Citation | Output | When |
|------|----------|--------|------|
| MOFA / MOFA+ | Argelaguet 2018 *Mol Syst Biol* 14:e8124; Argelaguet 2020 *Genome Biol* 21:111 | continuous factors + R^2 per (factor,view) | interpretable variance-attributed axes; missing-data tolerant; the default factor model |
| MEFISTO (within MOFA2) | Velten 2022 *Nat Methods* 19:179 | smooth factors along a covariate | samples carry a spatial or temporal coordinate |
| iCluster / iClusterPlus / iClusterBayes | Shen 2009 *Bioinformatics* 25:2906; Mo 2018 *Biostatistics* 19:71 | a hard sample clustering | discrete SUBTYPES (a partition) rather than axes |
| JIVE | Lock 2013 *Ann Appl Stat* 7:523 | explicit joint + per-view-individual + residual subspaces | quantify and separate joint vs dataset-specific structure |
| MCIA | Meng 2016 *J Proteome Res* 15:755 (moCluster); omicade4 | co-inertia ordination across views | fast exploratory co-structure / visual pathway exploration |
| mixOmics DIABLO | Singh 2019 *Bioinformatics* 35:3055 | supervised discriminant signature | the OUTCOME must drive the projection -> mixomics-analysis |

## Decision Tree by Deliverable

| Deliverable | Recommended | Why |
|-------------|-------------|-----|
| Interpretable axes attributed across views, hypothesis generation | MOFA / MOFA+ | continuous factors + variance decomposition; native missing-data |
| Discrete patient subtypes (a partition) | iCluster / iClusterPlus | the output IS a hard clustering -> integration-design, similarity-network |
| Explicitly separate joint from view-specific structure | JIVE | decomposition is joint + individual + residual by construction |
| Samples have a spatial/temporal coordinate | MEFISTO (within MOFA2) | GP prior gives smooth factors along the covariate |
| The outcome/class must drive the projection | -> mixomics-analysis (DIABLO) | supervised; the phenotype is in the model |
| Some samples missing a whole omic | MOFA (handles it natively) | the likelihood ignores missing entries; do not impute a block |
| Single-cell CITE-seq / Multiome MOFA+ | -> single-cell/multimodal-integration | single-cell object plumbing and stochastic inference |
| Enrich the factor weights | -> pathway-analysis/gsea | GSEA/ORA mechanics; here only `run_enrichment` on weights |

## Prepare the Views

**Goal:** Get each omic into the orientation and distribution MOFA assumes, so the factors reflect biology rather than measurement scale.

**Approach:** Each view must be features-by-samples (the transpose of the usual samples-by-features matrix), per-omic normalized and variance-stabilized upstream, and HVG-filtered so feature counts are within an order of magnitude across views. The per-omic transform and HVG selection are owned by data-harmonization.

```r
library(MOFA2)

common <- Reduce(intersect, list(colnames(rna), colnames(prot), colnames(meth)))   # shared samples; mosaic samples may be kept, see below
data_list <- list(RNA=rna[, common], Protein=prot[, common], Methylation=meth[, common])   # each features x samples, already transformed
mofa <- create_mofa(data_list)
plot_data_overview(mofa)        # shows views, samples, and the missing-data pattern (grey = missing, tolerated)
```

MOFA tolerates missing samples in a view (it ignores missing entries in the likelihood), so a mosaic cohort can be passed directly rather than intersected to complete cases - this is a core reason to choose MOFA when data is incomplete.

## Create and Train

**Goal:** Configure a factor model whose count and likelihoods match the data and the sample size, then train by variational inference.

**Approach:** Over-specify the factor count and let ARD prune, transform counts to a Gaussian likelihood rather than using Poisson, set a seed for reproducibility, and write the model to a versioned `.hdf5`.

```r
data_opts  <- get_default_data_options(mofa)       # scale_views=FALSE, center_groups=TRUE
model_opts <- get_default_model_options(mofa)      # num_factors=10, likelihoods='gaussian'
train_opts <- get_default_training_options(mofa)   # convergence_mode='fast', drop_factor_threshold=-1, stochastic=FALSE, seed=42

model_opts$num_factors <- 15                       # over-specify; ARD prunes inactive factors
model_opts$likelihoods <- c(RNA='gaussian', Protein='gaussian', Methylation='gaussian')   # transform counts upstream, prefer gaussian
train_opts$drop_factor_threshold <- 0.01           # drop factors explaining <1% variance in ALL views
data_opts$scale_views <- TRUE                      # equalize per-view variance if feature counts cannot be balanced by filtering

mofa <- prepare_mofa(mofa, data_options=data_opts, model_options=model_opts, training_options=train_opts)
mofa <- run_mofa(mofa, outfile=file.path(tempdir(), 'model.hdf5'), use_basilisk=TRUE)
```

## Read the Variance Decomposition (the Output)

**Goal:** Identify which factors are shared across views and which are view-specific before interpreting any of them.

**Approach:** The R^2 per factor per view is the central result: a factor active in two or more views is a shared axis, a factor active in one view is view-specific. Inspect this table first; factors with near-zero R^2 everywhere are noise.

```r
var_exp <- get_variance_explained(mofa)            # $r2_total, $r2_per_factor  <- the central output
plot_variance_explained(mofa)                      # heatmap: factors x views
plot_variance_explained(mofa, plot_total=TRUE)     # total variance explained per view
```

## Label the Factors (and Exclude Technical Ones)

**Goal:** Earn a biological label for a factor instead of asserting one from its existence.

**Approach:** Attach metadata after fitting (it is never used to train), correlate each factor with both biological and technical covariates, and exclude any factor that tracks batch/depth/plate from biological interpretation. Then run enrichment on the signed weights, treating the two poles of the axis separately.

```r
md <- metadata[unlist(samples_names(mofa)), ]
md$sample <- rownames(md)                       # samples_metadata<- requires a literal 'sample' column
samples_metadata(mofa) <- md
correlate_factors_with_covariates(mofa, covariates=c('condition', 'batch', 'depth'))   # a factor that correlates with batch IS a batch factor

# enrichment per sign - the two poles are biological opposites along one axis
up   <- run_enrichment(mofa, view='RNA', feature.sets=msig_binary_matrix, factors=1:5, sign='positive')
down <- run_enrichment(mofa, view='RNA', feature.sets=msig_binary_matrix, factors=1:5, sign='negative')
```

Multi-group MOFA (`group` in `create_mofa`) partitions samples so factor activity can differ across groups while weights stay shared - it asks "do the same axes operate within each group?" It is NOT batch correction and putting the phenotype in as a group does not make MOFA supervised. For samples with a spatial or temporal coordinate, MEFISTO (a GP-prior mode of MOFA2, via `mefisto_options` + `set_covariates`) learns factors that vary smoothly along that covariate.

## Per-Method Failure Modes

### Factor narrated as a mechanism
**Trigger:** "factor 1 represents immune activation" from the factor's existence. **Mechanism:** a factor is a direction of covariation the ARD prior kept; it has no intrinsic meaning. **Symptom:** a biological story with no enrichment, no covariate correlation, no replication. **Fix:** report the R^2 footprint, the signed-weight enrichment, and the known-covariate correlation; call it hypothesis-generating until validated.

### Batch factor mistaken for biology
**Trigger:** interpreting a top factor without a technical-covariate check. **Mechanism:** MOFA captures the largest variance, and unregressed batch is often largest. **Symptom:** the top factor tracks run date / plate better than phenotype. **Fix:** regress known batch out upstream (before HVG selection); always `correlate_factors_with_covariates` and exclude technical factors.

### Confirmation-bias factor scanning
**Trigger:** reporting the one of K factors that splits the groups. **Mechanism:** with enough factors one will split any grouping by chance. **Symptom:** a factor-phenotype association that does not replicate. **Fix:** pre-specify the test or correct for K; validate the chosen factor on a held-out cohort.

### Raw counts in a Gaussian view
**Trigger:** feeding un-transformed RNA counts to a gaussian likelihood. **Mechanism:** counts are heavy-tailed and mean-variance-coupled, so high-count genes carry the most raw variance. **Symptom:** factor 1 tracks library size / housekeeping genes. **Fix:** normalize and variance-stabilize per view upstream (data-harmonization), then use gaussian; reserve bernoulli for genuine binaries.

### Big modality eats the factors
**Trigger:** a 20k-gene view beside a 50-feature view, unequalized. **Mechanism:** bigger modalities are overrepresented in the factors. **Symptom:** every factor describes mostly the large view. **Fix:** HVG-filter to comparable feature counts and/or set `scale_views=TRUE` (which changes the R^2 interpretation to within-view relative variance).

### Too many factors at small n
**Trigger:** num_factors=20 with 30 samples. **Mechanism:** factor analysis needs sample size (the package floor is >15). **Symptom:** factors that fit noise and split the cohort by accident. **Fix:** request fewer factors, prune with `drop_factor_threshold`, confirm robustness across seeds, validate out-of-sample.

### Seed fragility unchecked
**Trigger:** building a story on one training run, especially with `stochastic=TRUE`. **Mechanism:** PCA init makes standard VI mostly reproducible, but local optima and stochastic inference still vary. **Symptom:** a headline factor that does not reappear on a retrain. **Fix:** set the seed AND retrain with a different seed/factor count; a robust axis recurs with factor-score correlation near 1.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `num_factors` over-specified, ARD prunes | Argelaguet 2018 *Mol Syst Biol* 14:e8124 | a factor never allocated cannot be recovered; default cap is N-dependent (5 if N<=25, 15 if N<=1000) |
| `drop_factor_threshold` ~0.01 | MOFA2 docs | drop factors explaining <1% variance in ALL views; default -1 keeps all |
| Sample size floor > 15 | MOFA2 FAQ | factor analysis is only useful with adequate n; tens of samples overfit a generous factor count |
| `scale_views=TRUE` only when filtering cannot equalize | MOFA2 FAQ | bigger modalities are overrepresented; scaling equalizes per-view variance but changes R^2 reading |
| Transform counts to gaussian rather than poisson | MOFA2 FAQ | non-gaussian likelihoods are less-accurate approximations; transform if it can be defended |
| Robustness: factor recurs across seeds with |r|~1 | Argelaguet 2018 *Mol Syst Biol* 14:e8124 | a factor that does not reappear on retrain is fragile noise |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `create_mofa` orientation error or nonsense factors | views passed samples-by-features | transpose to features-by-samples |
| Factor 1 tracks sequencing depth | raw counts into a gaussian view | normalize + variance-stabilize per view first |
| Every factor describes one omic | variance imbalance | HVG-filter to comparable feature counts / `scale_views=TRUE` |
| Model will not converge / factors NaN | unscaled blocks or a constant feature | center/scale; drop zero-variance features upstream |
| A factor loads almost entirely on one sample | an outlier hijacking a factor | inspect and remove the outlier; refit |
| Headline factor vanishes on rerun | seed fragility / stochastic inference | set seed; confirm the factor recurs across retrains |

## References

- Argelaguet R, Velten B, Arnol D, et al. 2018. Multi-Omics Factor Analysis - a framework for unsupervised integration of multi-omics data sets. *Mol Syst Biol* 14:e8124.
- Argelaguet R, Arnol D, Bredikhin D, et al. 2020. MOFA+: a statistical framework for comprehensive integration of multi-modal single-cell data. *Genome Biol* 21:111.
- Velten B, Braunger JM, Argelaguet R, et al. 2022. Identifying temporal and spatial patterns of variation from multimodal data using MEFISTO. *Nat Methods* 19:179-186.
- Shen R, Olshen AB, Ladanyi M. 2009. Integrative clustering of multiple genomic data types using a joint latent variable model with application to breast and lung cancer subtype analysis. *Bioinformatics* 25:2906-2912.
- Lock EF, Hoadley KA, Marron JS, Nobel AB. 2013. Joint and individual variation explained (JIVE) for integrated analysis of multiple data types. *Ann Appl Stat* 7:523-542.
- Meng C, Helm D, Frejno M, Kuster B. 2016. moCluster: identifying joint patterns across multiple omics data sets. *J Proteome Res* 15:755-765.
- Singh A, Shannon CP, Gautier B, et al. 2019. DIABLO: an integrative approach for identifying key molecular drivers from multi-omics assays. *Bioinformatics* 35:3055-3062.
- Cantini L, Zakeri P, Hernandez C, et al. 2021. Benchmarking joint multi-omics dimensionality reduction approaches for the study of cancer. *Nat Commun* 12:124.

## Related Skills

- integration-design - The method-selection decision; MOFA is the default once correspondence is vertical
- mixomics-analysis - Supervised DIABLO/sPLS where the outcome drives the projection
- data-harmonization - Per-omic transform, HVG selection, and batch regression before MOFA
- similarity-network - Hard patient stratification alternative to soft factors
- single-cell/multimodal-integration - Single-cell MOFA+ (CITE-seq/Multiome) plumbing
- pathway-analysis/gsea - Enrichment of factor weights (mechanics)
- clinical-biostatistics/survival-analysis - Survival validation using factors as features
- workflows/multi-omics-pipeline - End-to-end multi-omics integration pipeline
<!-- END FILE: multi-omics-integration/mofa-integration/SKILL.md -->

## 子目录：multi-omics-integration/similarity-network

<!-- BEGIN FILE: multi-omics-integration/similarity-network/SKILL.md -->
---
name: bio-multi-omics-similarity-network
description: Stratifies patients into multi-omics subtypes by building one patient-by-patient similarity network per omic, fusing them with SNF's cross-network diffusion, and spectral-clustering the fused graph - then defending the clusters with stability, survival separation, and replication. Covers why spectral clustering always returns the requested cluster count so a subtype is a claim not a discovery, why the eigengap is a graph property not a biological truth, why fusion is not automatically better than the best single omic, why SNF needs complete data while NEMO handles mosaic cohorts, and the SNFtool API gotchas (dist2 returns squared distance, affinityMatrix width is sigma, spectralClustering K is the cluster count). Use when discovering patient subtypes from multiple omics, choosing a cluster number, validating subtypes, or handling partial multi-omic data. For feature-space factors see mofa-integration; for supervised signatures see mixomics-analysis; for survival see clinical-biostatistics/survival-analysis.
tool_type: r
primary_tool: SNFtool
---

## Version Compatibility

Reference examples tested with: SNFtool 2.3+, igraph 2.0+, pheatmap 1.0+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('SNFtool')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

SNFtool argument names are easy to misread: `affinityMatrix`'s width argument is `sigma` (not alpha or mu), `dist2` returns SQUARED Euclidean distance (take the square root), and `spectralClustering`'s `K` is the number of CLUSTERS, a name collision with the K-neighbors argument of `affinityMatrix`/`SNF`.

# Similarity Network Fusion

**"Stratify my patients using multi-omics data"** -> Fuse per-omic patient-similarity networks into one graph and spectral-cluster it - because the clustering always returns the number of subtypes requested, so the subtype is a claim to defend, not a discovery.
- R: `SNF()` to fuse networks, `spectralClustering()` to partition, then validate

Scope: patient-similarity-space integration - per-omic affinity networks, SNF fusion, spectral clustering into candidate subtypes, cluster-number choice, and the stability/survival/replication defense, plus the integrative-clustering landscape (NEMO, PINS, iCluster, CIMLR, intNMF, consensus). Feature-space latent factors -> mofa-integration. Supervised feature signatures -> mixomics-analysis. Survival mechanics -> clinical-biostatistics/survival-analysis. Single-cell graph clustering -> single-cell/clustering.

## The Single Most Important Modern Insight -- Spectral Clustering Always Returns the Requested Number of Clusters, So a Subtype Is a Claim to Defend, Not a Thing Discovered

Ask the spectral step for four clusters and it returns four, whether or not four real patient groups exist; the eigengap suggesting "four" means only that the fused graph has a roughly four-block shape, not that the disease has four subtypes. SNF's fusion is genuinely powerful - its cross-network diffusion reinforces patient pairs that multiple omics agree on and erodes omic-specific noise - but power to draw a boundary is not evidence the boundary is real. Three defenses, none of which the algorithm supplies:

1. **Stability.** Resample the patients, re-cluster, and measure agreement (consensus index / NMI across subsamples). A real subtype recurs; an artifact does not. Report stability across a fixed (K, sigma) grid rather than tuning those hyperparameters to a target.
2. **Survival separation after adjustment.** Subtypes should differ in outcome in a Cox model adjusted for known prognostic covariates (stage, age, grade), so a "subtype" is not just re-encoded stage. The discovery-cohort p is supporting evidence, not proof - and a permutation p is safer than the chi-square approximation at small arm sizes.
3. **Replication and the fused-versus-best-single-omic check.** Multi-omics does not consistently beat the best single omic (Rappoport and Shamir 2018), and SNF's diffusion can dilute a signal carried by one omic. Benchmark the fused clustering against each single-omic clustering, and replicate the subtypes in an independent cohort.

The honest report names the hyperparameters, shows the clusters are not knife-edge-sensitive to them, and treats the discovery survival p as supporting evidence, not the finding.

## Tool Taxonomy (Integrative Clustering)

| Tool | Citation | Mechanism | When |
|------|----------|-----------|------|
| SNF (SNFtool) | Wang 2014 *Nat Methods* 11:333 | per-omic affinity + cross-network diffusion -> spectral | complete data; non-linear consensus reinforcing multi-omic agreement; the default |
| NEMO | Rappoport 2019 *Bioinformatics* 35:3348 | per-omic relative similarity, AVERAGED (no iteration) -> spectral | PARTIAL/mosaic data; fast; comparable accuracy on full data |
| PINS / PINSPlus | Nguyen 2017 *Genome Res* 27:2025; Nguyen 2019 *Bioinformatics* 35:2843 | perturbation clustering; keeps partitions robust to noise; auto-picks C | when partition stability is the priority |
| iCluster / iClusterPlus | Shen 2009 *Bioinformatics* 25:2906; Mo 2013 *PNAS* 110:4245 | model-based joint latent-variable + feature selection | want a generative model and feature selection; tends to pick few clusters |
| CIMLR | Ramazzotti 2018 *Nat Commun* 9:4453 | multiple-kernel learning per omic -> k-means | one Gaussian kernel per omic too rigid; strong survival results |
| intNMF | Chalise 2017 *PLoS One* 12:e0176278 | joint non-negative matrix factorization | non-negative data; parts-based factorization + clustering |
| Consensus / COCA | Monti 2003 *Mach Learn* 52:91; Hoadley 2014 *Cell* 158:929 | cluster each omic, then cluster the matrix-of-clusters | late integration; want each omic's clustering visible and a consensus |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Complete multi-omics, want a non-linear consensus partition | SNF + spectralClustering | cross-network diffusion reinforces multi-omic agreement |
| Some patients missing an omic (mosaic/partial) | NEMO | built for partial data; no imputation, no patient loss |
| Partition robustness/auto cluster number is the priority | PINSPlus | perturbation clustering builds stability in |
| Want a generative model and integrated feature selection | iCluster / iClusterBayes | model-based joint latent variable |
| Need feature-level interpretation (which genes define a subtype) | -> mofa-integration / mixomics-analysis | SNF has no feature model; feature-space tools live there |
| Validate subtypes against outcome | -> clinical-biostatistics/survival-analysis | Cox / log-rank / KM mechanics |
| SNF underperforms on survival in a benchmark | MCCA (survival) or rMKL-LPP (clinical enrichment) | topped those criteria in Rappoport and Shamir 2018 |
| Which method at all / paired vs mosaic | -> integration-design | the correspondence and method decision |

## Build the Per-Omic Affinity Networks

**Goal:** Turn each omic into a patient-by-patient similarity network on a common scale, collapsing the high-dimensional feature space into an n-by-n object so feature count buys no votes.

**Approach:** Standardize each continuous omic per feature, compute the (square-rooted) Euclidean distance, then apply the local-scaled Gaussian kernel. SNF requires every patient to have every omic, so intersect to common samples first and report how many that drops.

```r
library(SNFtool)

K <- 20        # neighbors defining the local kernel bandwidth; SNFtool guidance 10-30; changes cluster count
sigma <- 0.5   # kernel width multiplier (affinityMatrix's third arg, named sigma not alpha); guidance 0.3-0.8
t_iter <- 20   # cross-diffusion iterations; converges by ~10-20

norm_views <- lapply(list(rna=rna, meth=meth, mirna=mirna), standardNormalization)   # per-feature z-score before distance
dists <- lapply(norm_views, function(x) dist2(x, x)^(1/2))                            # dist2 returns SQUARED distance
affinities <- lapply(dists, function(d) affinityMatrix(d, K, sigma))
```

## Fuse and Cluster

**Goal:** Fuse the per-omic networks into one graph and partition it, treating the cluster number as the central claim rather than a nuisance parameter.

**Approach:** Run SNF's cross-diffusion, read the four cluster-number estimates the package returns (not as truth but as plausibility), then spectral-cluster. The package itself warns the estimates cannot guarantee accuracy.

```r
fused <- SNF(affinities, K, t_iter)
estimateNumberOfClustersGivenGraph(fused, NUMC=2:8)   # returns FOUR estimates: K1/K12 (eigengap), K2/K22 (rotation cost)
clusters <- spectralClustering(fused, K=4, type=3)    # here K is the CLUSTER COUNT (not neighbors); type 3 = Ng-Jordan-Weiss default
```

## Defend the Subtypes

**Goal:** Show the clusters are stable, separate outcome, and are not just the best single omic before calling them subtypes.

**Approach:** Compare the fused clustering against each single-omic clustering, assess stability under resampling, and rank the post-hoc feature attribution with the package function rather than a hand-rolled test. Survival mechanics are routed out.

```r
concordanceNetworkNMI(c(affinities, list(fused)), C=4)   # NMI among per-omic and fused clusterings: did fusion beat the best single omic?
feat_rank <- rankFeaturesByNMI(norm_views, fused)        # POST-HOC attribution: features that track the clusters, not a model that made them
```

Validate survival separation in a covariate-adjusted Cox model and report events per arm (clinical-biostatistics/survival-analysis owns the mechanics); assess stability by resampling patients and re-clustering, reporting agreement across subsamples. To assign a new patient to an existing subtype without re-clustering, use `groupPredict(train_views, test_views, groups, K=20, method=1)` (label propagation). For a mosaic cohort, switch to NEMO rather than dropping the incomplete patients.

## Per-Method Failure Modes

### Subtype count reported as a discovery
**Trigger:** "I found 4 subtypes" with no defense. **Mechanism:** spectral clustering returns the requested C regardless of structure. **Symptom:** a clean-looking partition that does not replicate. **Fix:** require eigengap plausibility, resampling stability, covariate-adjusted survival, and external replication before claiming a subtype count.

### Hyperparameters tuned to a label, then claimed
**Trigger:** grid-searching K and sigma to maximize NMI against known labels. **Mechanism:** in real discovery there are no labels, so tuning to NMI is circular. **Symptom:** a result that only holds at the chosen (K, sigma). **Fix:** fix or pre-register a small (K, sigma) grid and show the clustering is stable across it; report sensitivity as a result.

### Complete-data requirement ignored
**Trigger:** `Reduce(intersect, ...)` silently dropping patients missing an omic. **Mechanism:** SNF's cross-diffusion multiplies aligned n-by-n matrices, so it needs complete data. **Symptom:** a decimated, biased cohort. **Fix:** report the dropped count and bias; use NEMO for partial data; do not impute a whole omic to keep a patient.

### Fusion assumed to beat the best single omic
**Trigger:** reporting the fused clustering without a single-omic comparison. **Mechanism:** fusion's diffusion can dilute a signal carried by one omic; multi-omics is not consistently better (Rappoport and Shamir). **Symptom:** a fused result no better than the best layer. **Fix:** benchmark fused vs each single omic with `concordanceNetworkNMI` and per-omic survival.

### Survival p taken at face value
**Trigger:** a log-rank p on discovery clusters. **Mechanism:** C, K, sigma were chosen partly to get separable groups, and arms are small. **Symptom:** an over-optimistic p that does not replicate. **Fix:** adjust for prognostic covariates, report events per arm, use a permutation p, and require replication.

### Feature attribution treated as the model
**Trigger:** presenting ranked features as what generated the clusters. **Mechanism:** SNF has no feature-level model; attribution is post-hoc. **Symptom:** causal claims SNF cannot support. **Fix:** use `rankFeaturesByNMI` and present it as post-hoc characterization; for a feature model use MOFA/DIABLO.

### SNFtool API misread
**Trigger:** treating `dist2` output as Euclidean, passing alpha to `affinityMatrix`, or reading `spectralClustering`'s K as neighbors. **Mechanism:** `dist2` is squared, the width arg is `sigma`, and that `K` is the cluster count. **Symptom:** distorted affinities or the wrong number of clusters. **Fix:** take `dist2(...)^(1/2)`, pass `sigma`, and read the K name in context.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| K neighbors ~20 (range 10-30) | Wang 2014 *Nat Methods* 11:333; SNFtool docs | sets the local kernel bandwidth; small K fragments, large K over-smooths and changes cluster count |
| sigma ~0.5 (range 0.3-0.8) | SNFtool docs | kernel width multiplier; wider blurs clusters, narrower sharpens noise |
| t iterations ~10-20 | Wang 2014 *Nat Methods* 11:333 | cross-diffusion converges; more iterations do little past convergence |
| `estimateNumberOfClustersGivenGraph` returns FOUR estimates | SNFtool docs | eigengap (K1/K12) and rotation cost (K2/K22); plausibility not proof |
| Fused must beat the best single omic to justify fusion | Rappoport and Shamir 2018 *Nucleic Acids Res* 46:10546 | multi-omics is not consistently better; check explicitly |
| Stability across a fixed (K, sigma) grid + permutation survival p | Monti 2003 *Mach Learn* 52:91 | resampling stability and a permutation p guard against artifact subtypes |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Distorted affinities / wrong-scale distances | `dist2` output used as Euclidean | take `dist2(...)^(1/2)` |
| Clusters change unexpectedly | `affinityMatrix` width passed as alpha or wrong arg | the third argument is `sigma` |
| Wrong number of clusters | `spectralClustering`'s K read as neighbors | that `K` is the cluster count |
| Function `dist2` not found after first call | a variable named `dist2` shadowing the function | name distance variables differently (d1, d2) |
| Many patients silently dropped | complete-data intersection on a mosaic cohort | report the drop; use NEMO for partial data |
| Hand-rolled feature ranking | reimplementing attribution with `aov` | use `rankFeaturesByNMI(list_of_views, fused)` |

## References

- Wang B, Mezlini AM, Demir F, et al. 2014. Similarity network fusion for aggregating data types on a genomic scale. *Nat Methods* 11:333-337.
- Rappoport N, Shamir R. 2018. Multi-omic and multi-view clustering algorithms: review and cancer benchmark. *Nucleic Acids Res* 46:10546-10562.
- Rappoport N, Shamir R. 2019. NEMO: cancer subtyping by integration of partial multi-omic data. *Bioinformatics* 35:3348-3356.
- Nguyen T, Tagett R, Diaz D, Draghici S. 2017. A novel approach for data integration and disease subtyping. *Genome Res* 27:2025-2039.
- Nguyen H, Shrestha S, Draghici S, Nguyen T. 2019. PINSPlus: a tool for tumor subtype discovery in integrated genomic data. *Bioinformatics* 35:2843-2846.
- Shen R, Olshen AB, Ladanyi M. 2009. Integrative clustering of multiple genomic data types using a joint latent variable model with application to breast and lung cancer subtype analysis. *Bioinformatics* 25:2906-2912.
- Mo Q, Wang S, Seshan VE, et al. 2013. Pattern discovery and cancer gene identification in integrated cancer genomic data. *PNAS* 110:4245-4250.
- Ramazzotti D, Lal A, Wang B, Batzoglou S, Sidow A. 2018. Multi-omic tumor data reveal diversity of molecular mechanisms that correlate with survival. *Nat Commun* 9:4453.
- Chalise P, Fridley BL. 2017. Integrative clustering of multi-level 'omic data based on non-negative matrix factorization algorithm. *PLoS One* 12:e0176278.
- Monti S, Tamayo P, Mesirov J, Golub T. 2003. Consensus clustering: a resampling-based method for class discovery and visualization of gene expression microarray data. *Mach Learn* 52:91-118.
- von Luxburg U. 2007. A tutorial on spectral clustering. *Stat Comput* 17:395-416.

## Related Skills

- integration-design - The method-selection and paired-vs-mosaic decision
- mofa-integration - Feature-space latent factors (which molecular axes matter)
- mixomics-analysis - Supervised feature signatures for known classes
- data-harmonization - Per-omic scaling before building distances
- clinical-biostatistics/survival-analysis - Survival validation of discovered subtypes
- single-cell/clustering - Graph clustering of cells (different object)
- pathway-analysis/go-enrichment - Enrichment of subtype-associated features
- workflows/multi-omics-pipeline - End-to-end multi-omics integration pipeline
<!-- END FILE: multi-omics-integration/similarity-network/SKILL.md -->

<!-- END CATEGORY: multi-omics-integration -->

