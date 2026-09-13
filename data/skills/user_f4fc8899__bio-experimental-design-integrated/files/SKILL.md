---
slug: bio-experimental-design-integrated
version: 1.0.1
displayName: "实验设计 / Experimental design"
name: bio-experimental-design-integrated
summary: "中文：实验设计综合技能，整合 5 个相关专题，覆盖实验设计：随机化/区组设计、统计功效、样本量估计、多重检验校正、批次设计。 English: Integrated Experimental design skill covering 5 related topics, including Experimental design: randomization/blocking, statistical power, sample size estimation, multiple testing correction, batch design."
description: "中文：这是一个面向实验设计的综合生物信息学 Skill，整合当前分类下 5 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：实验设计：随机化/区组设计、统计功效、样本量估计、多重检验校正、批次设计。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：RNASeqPower, designit, qvalue。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Experimental design, combining 5 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Experimental design: randomization/blocking, statistical power, sample size estimation, multiple testing correction, batch design. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: RNASeqPower, designit, qvalue. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# experimental-design 分类 Skill 整合版

> 本文件整合同一主分类目录下 5 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: experimental-design -->

## 子目录：experimental-design/batch-design

<!-- BEGIN FILE: experimental-design/batch-design/SKILL.md -->
---
name: bio-experimental-design-batch-design
description: Designs genomics experiments so technical nuisance variation (batch, lane, plate, flow cell, operator, reagent lot, processing day) is balanced against the biological variable of interest and therefore estimable rather than confounded, using constrained sample-to-batch assignment (designit, OSAT), the confounder/mediator/collider distinction, and the principle that no post-hoc correction recovers a fully confounded design. Covers detecting hidden batches with surrogate variable analysis, a decision table for downstream correction (ComBat-seq, RUVSeq, SVA) whose execution is deferred to differential-expression/batch-correction, and reproducibility metadata. Use when assigning samples to sequencing batches/lanes/plates, avoiding batch-condition confounding, deciding whether a design is salvageable by correction, choosing a correction method, or estimating the number of hidden batches. For the experimental unit, randomization, and blocking concepts see experimental-design/randomization-blocking.
tool_type: r
primary_tool: designit
---

## Version Compatibility

Reference examples tested with: designit 0.5+, OSAT 1.50+ (Bioconductor), sva 3.50+, RUVSeq 1.36+, limma 3.58+, edgeR 4.0+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws an error, introspect the installed package and adapt to the actual API. Notes: OSAT uses `optimal.shuffle()` on a setup object (there is no bare `osat()` function); designit is R6 (`BatchContainer$new()`, `optimize_design()`, `*_score_generator()`) and its signatures drift between releases; `sva::ComBat_seq()` is for integer counts while `ComBat()` expects log-normalized values. Confirm each against the installed vignette before relying on it.

# Batch Design

**"Design my experiment so batch effects don't ruin it"** -> Assign samples to batches/lanes/plates so the biological variable is balanced against (orthogonal to) every technical nuisance factor, making batch estimable rather than confounded — because no post-hoc correction recovers a design where batch and condition are aliased.
- R: `designit::optimize_design()`, `OSAT::optimal.shuffle()` — constrained assignment at design time
- R: `sva::sva()`/`num.sv()` — detect hidden batches; `sva::ComBat_seq()`, `RUVSeq::RUVg()` — DOWNSTREAM correction (executed in differential-expression/batch-correction)

## The Single Most Important Modern Insight -- No Post-Hoc Method Recovers a Confounded Design

When a technical factor is perfectly aliased with the biological factor (all treated in batch 1, all controls in batch 2), batch and condition occupy the same column space and are mathematically non-identifiable; ComBat, SVA, and RUV cannot separate them, and "removing the batch effect" removes the biology with it. Worse, on *partially* confounded or merely **unbalanced** designs, mean-centering batches can *manufacture* false positives and inflate downstream confidence — Nygaard, Rødland & Hovig 2016 *Biostatistics* 17:29 showed a pipeline that returned >1000 spurious DE probes where the honest analysis (batch kept *in the model*) found 11. The operative rules: (1) balance the biological variable across batches **at design time** because correction is not a rescue (Leek 2010 *Nat Rev Genet* 11:733); (2) for inference, keep batch *in the model* so its degrees of freedom are charged honestly — reserve a batch-"cleaned" matrix for visualization and clustering only. The experimental unit, not the measurement, still defines replication (see experimental-design/randomization-blocking).

## Confounding vs Blocking vs Nuisance -- the Causal-Graph View

Batch is the genomics face of confounding, and not all metadata should be "adjusted for". A **confounder** is a common cause of treatment and outcome (adjust for it); a **mediator** lies on the causal path (adjusting removes signal); a **collider** is a common effect (adjusting *induces* spurious association). "Adjust for everything measured" is therefore wrong in general — conditioning on a collider opens a backdoor path. In a properly *randomized* design the biological variable has no confounders by construction, so batch is handled by **balanced assignment + a block/covariate term**, not by scrubbing every measured variable.

## Algorithmic Taxonomy -- Design Strategies for Technical Variation

| Strategy | What it does | When to use | Fails when |
|----------|--------------|-------------|------------|
| Balanced (orthogonal) assignment | every condition appears equally in every batch | always achievable when batches hold >=1 of each condition | not all conditions fit per batch |
| Block randomization across batches | randomize condition within each batch | batch = a block; conditions fit per batch | batch variance is genuinely zero (rare) |
| Incomplete block + batch in model | conditions split across smaller batches, batch term retained | plate/chip smaller than #conditions | unbalanced split inflates artifacts (Nygaard 2016) |
| Reference / bridge sample per batch | shared anchor measured in every batch | cross-batch normalization (TMT proteomics, large cohorts) | anchor not representative |
| Multiplexing + demultiplexing | pool biological units in one lane, split by barcode/genotype | breaking the donor<->lane confound (scRNA-seq) | insufficient SNPs/hashes to assign |
| Run-order randomization | randomize processing/injection order | position/time gradients (LC-MS, plate edge) | order set by convenience |

## Decision Tree by Scenario

| Scenario | Recommended design | Why |
|----------|--------------------|-----|
| 24 samples, 3 batches, 2 conditions | balanced: 4 of each condition per batch | batch orthogonal to condition; estimable |
| Conditions outnumber batch capacity | incomplete block; keep batch in the DE model | preserves estimability; no scrubbing |
| Large cohort across many runs | include a shared reference sample per batch | enables cross-batch normalization |
| scRNA-seq, several donors, few lanes | pool donors per lane, demultiplex (demuxlet / hashing) | removes donor<->lane confound (Kang 2018) |
| Hidden/unknown technical structure suspected | estimate surrogate variables (SVA), include in model | captures unmodeled variation (Leek & Storey 2007) |
| Design already confounds batch with condition | redesign; no correction will rescue it | non-identifiable (Nygaard 2016; Leek 2010) |
| General randomization / blocking / unit choice | -> experimental-design/randomization-blocking | foundational design structure |
| Running ComBat-seq / RUVSeq / SVA on real data | -> differential-expression/batch-correction | execution lives there; this skill decides |

## Confounded vs Balanced -- the Canonical Contrast

**Goal:** Make batch effects correctable by keeping the biological variable orthogonal to batch.

**Approach:** Never place all of one condition in one batch. Distribute conditions (and known covariates such as sex) equally across batches so a linear model can estimate batch and condition separately.

```r
# BAD (confounded): batch is aliased with condition -> non-identifiable
#   batch 1: treat, treat, treat, treat       batch 2: ctrl, ctrl, ctrl, ctrl
# GOOD (balanced): batch is orthogonal to condition -> batch effect estimable, removable
#   batch 1: 2 treat + 2 ctrl                 batch 2: 2 treat + 2 ctrl
```

## Constrained Sample-to-Batch Assignment

**Goal:** Allocate samples to batches/lanes/plates to minimize correlation between batch and the biological variables of interest.

**Approach:** Use a block-randomization-with-optimization tool that scores assignments by how evenly the biological factors spread across batches and returns a near-optimal layout.

```r
library(designit)                              # verify API against installed vignette
samples <- data.frame(id = sprintf('S%02d', 1:24),
                      condition = rep(c('ctrl', 'treat'), each = 12),
                      sex = rep(c('M', 'F'), 12))
bc <- BatchContainer$new(dimensions = list(batch = 3, position = 8))
bc <- assign_in_order(bc, samples = samples)
bc <- optimize_design(
  bc,
  scoring = osat_score_generator(batch_vars = 'batch',
                                 feature_vars = c('condition', 'sex')))   # balance both factors
assignment <- bc$get_samples()                # R6 method on the container (no standalone get_samples())

# OSAT alternative (Bioconductor): build a setup object, then optimal.shuffle() -- NOT a bare osat().
```

## Downstream Correction -- Choose by Design, Execute Elsewhere

Correction method selection is a design decision; the execution lives in differential-expression/batch-correction (and single-cell/batch-integration for scRNA-seq). Prefer keeping batch in the analysis model over producing a "cleaned" matrix for inference.

| Method | When it applies | Assumption / caveat | Owner of execution |
|--------|-----------------|---------------------|--------------------|
| Batch as a model covariate | batch known, balanced | charges df honestly; the default for inference | differential-expression |
| ComBat-seq | known batch, integer counts | batch ~ orthogonal to biology; Nygaard caveat if unbalanced | differential-expression/batch-correction |
| ComBat (parametric eB) | known batch, log-normalized data | Gaussian; not for raw counts | differential-expression/batch-correction |
| RUVSeq (RUVg/RUVs/RUVr) | negative-control genes/samples available | controls must be truly null to the biology | differential-expression/batch-correction |
| SVA | hidden/unknown structure | surrogate variables can absorb biology if confounded | this skill estimates; DE consumes |
| limma removeBatchEffect | visualization/clustering ONLY | not for the hypothesis test | data-visualization |
| Harmony / scVI / Seurat anchors | scRNA-seq integration | integration, not DE inference | single-cell/batch-integration |

## Detecting Hidden Batch Effects (SVA)

**Goal:** Estimate unmodeled technical structure (hidden batches) so it can be included in the downstream model.

**Approach:** Fit a model matrix for the biological variable and a null matrix, estimate the number of surrogate variables, then compute them for inclusion as covariates in the DE analysis.

```r
library(sva)
mod  <- model.matrix(~ condition, data = colData)   # full model
mod0 <- model.matrix(~ 1, data = colData)           # null model
n_sv <- num.sv(expr_normalized, mod)                # estimate number of hidden batches
svobj <- sva(expr_normalized, mod, mod0, n.sv = n_sv)
# Add svobj$sv to the design used by differential-expression/de-results; do NOT subtract them
# from the data for the test (subtracting is for visualization only).
```

## Per-Method Failure Modes

### Batch confounded with condition
- **Trigger:** all of one condition processed in one batch/run.
- **Mechanism:** batch and condition are aliased -> non-identifiable.
- **Symptom:** condition effect vanishes (or an artifact appears) after correction.
- **Fix:** redesign with balanced assignment; no post-hoc method recovers it (Leek 2010).

### ComBat on unbalanced groups
- **Trigger:** ComBat applied when condition is partially confounded with batch.
- **Mechanism:** mean-centering batches injects between-group differences and understates residual variance.
- **Symptom:** inflated DE counts and over-confident downstream inference (Nygaard 2016).
- **Fix:** keep batch in the model (ComBat-seq with the biological covariate, or batch as a DE covariate); best is balanced design.

### Subtracting surrogate variables before testing
- **Trigger:** feeding an SV-"cleaned" matrix into the DE test.
- **Mechanism:** double-counts the adjustment and loses degrees of freedom.
- **Symptom:** anti-conservative p-values.
- **Fix:** include SVs as covariates in the model; reserve cleaned matrices for plots.

### Adjusting for a collider
- **Trigger:** "adjust for everything measured" includes a downstream/common-effect variable.
- **Mechanism:** conditioning on a collider opens a spurious path.
- **Symptom:** associations that appear only after adjustment.
- **Fix:** adjust for confounders (common causes), not mediators or colliders.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Balance every condition equally across batches | Leek 2010 *Nat Rev Genet* 11:733 | makes batch estimable and removable |
| Unbalanced ComBat can inflate DE (>1000 vs 11 in one case) | Nygaard 2016 *Biostatistics* 17:29 | mean-centering injects group differences |
| ~50 SNPs/cell suffice to demultiplex pooled donors | Kang 2018 *Nat Biotechnol* 36:89 | breaks donor<->lane confound |
| Keep batch in the model for inference; clean only for viz | Nygaard 2016; Leek 2010 | honest degrees of freedom |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Condition effect disappears after ComBat | batch confounded with condition | balance at design time |
| Inflated DE list after batch correction | unbalanced ComBat | keep batch in model; ComBat-seq with covariate |
| scRNA-seq donor effect equals lane effect | one donor per lane | pool + demultiplex (demuxlet / hashing) |
| Spurious associations after "adjusting for all metadata" | conditioning on a collider/mediator | adjust only for confounders |
| Cannot reconstruct who/when/which-lot | no metadata captured | record date, lot, operator, lane, position |

## Reproducibility Metadata

Record for every sample, because these become the batch/blocking variables: processing date, reagent and kit lot numbers, operator, instrument/flow-cell/lane and well/plate position, library prep batch, and any protocol deviations. Unrecorded technical variation cannot be modeled or balanced after the fact, and is a leakage source for any downstream machine-learning model (see machine-learning/model-validation).

## References

- Leek JT, Scharpf RB, Bravo HC, Simcha D, Langmead B, Johnson WE, Geman D, Baggerly K, Irizarry RA. 2010. Tackling the widespread and critical impact of batch effects in high-throughput data. *Nat Rev Genet* 11:733-739.
- Nygaard V, Rødland EA, Hovig E. 2016. Methods that remove batch effects while retaining group differences may lead to exaggerated confidence in downstream analyses. *Biostatistics* 17:29-39.
- Johnson WE, Li C, Rabinovic A. 2007. Adjusting batch effects in microarray expression data using empirical Bayes methods. *Biostatistics* 8:118-127.
- Zhang Y, Parmigiani G, Johnson WE. 2020. ComBat-seq: batch effect adjustment for RNA-seq count data. *NAR Genom Bioinform* 2:lqaa078.
- Leek JT, Storey JD. 2007. Capturing heterogeneity in gene expression studies by surrogate variable analysis. *PLoS Genet* 3:e161.
- Gagnon-Bartsch JA, Speed TP. 2012. Using control genes to correct for unwanted variation in microarray data. *Biostatistics* 13:539-552.
- Kang HM, Subramaniam M, Targ S, et al. 2018. Multiplexed droplet single-cell RNA-sequencing using natural genetic variation. *Nat Biotechnol* 36:89-94.
- Yan L, Ma C, Wang D, Hu Q, Qin M, Conroy JM, Sucheston LE, Ambrosone CB, Johnson CS, Wang J, Liu S. 2012. OSAT: a tool for sample-to-batch allocations in genomics experiments. *BMC Genomics* 13:689.

## Related Skills

- randomization-blocking - The experimental unit, randomization, and blocking concepts behind a good batch layout
- power-analysis - Account for blocking/batch factors in the power calculation
- sample-size - Balanced designs assume equal n per group
- multiple-testing - Surrogate variables change the effective number of tests
- differential-expression/batch-correction - Executes ComBat-seq/RUVSeq/SVA on real data
- single-cell/batch-integration - scRNA-seq integration (Harmony, scVI, Seurat anchors)
- machine-learning/model-validation - Batch confounding is a data-leakage source for ML
- clinical-biostatistics/power-and-sample-size - Trial randomization and design (regulated regime)
<!-- END FILE: experimental-design/batch-design/SKILL.md -->

## 子目录：experimental-design/multiple-testing

<!-- BEGIN FILE: experimental-design/multiple-testing/SKILL.md -->
---
name: bio-experimental-design-multiple-testing
description: Controls error rates across thousands of simultaneous tests in genomics discovery using false-discovery-rate methods (Benjamini-Hochberg 1995; Benjamini-Yekutieli 2001 for arbitrary dependence; Storey q-value with pi0 estimation; local FDR; independent filtering Bourgon 2010; covariate-weighted FDR via IHW Ignatiadis 2016), plus family-wise error control (Bonferroni, Holm) and the GWAS genome-wide threshold. Covers the FDR-versus-FWER choice as the discovery-versus-confirmatory distinction, the dependence assumptions behind BH (PRDS) versus BY, pi0 estimation, the independent-filtering and false-coverage-rate traps, and reproducibility ranking via IDR (Li 2011). Use when correcting p-values from genome-wide tests, choosing between BH/BY/q-value/Bonferroni, setting an FDR threshold, applying IHW or independent filtering, or interpreting q-values. For confirmatory trials with few pre-specified endpoints (closed testing, graphical/gatekeeping), see clinical-biostatistics/multiplicity-graphical.
tool_type: mixed
primary_tool: qvalue
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: qvalue 2.34+, IHW 1.30+, R stats (base) p.adjust, statsmodels 0.14+, scipy 1.12+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws an error, introspect the installed package and adapt to the actual API. Note: `statsmodels.stats.multitest.multipletests` defaults to `method='hs'` (Holm-Sidak, an FWER method), NOT Benjamini-Hochberg — always pass `method='fdr_bh'`/`'fdr_by'`/`'bonferroni'`/`'holm'` explicitly.

# Multiple Testing Correction

**"Correct p-values for testing thousands of features"** -> Choose an error rate appropriate to the regime (FDR for discovery, FWER for confirmatory), apply a procedure whose dependence assumptions match the data, and report the adjusted quantity with its interpretation.
- R: `p.adjust(p, method = 'BH')`, `qvalue::qvalue()`, `IHW::ihw()`
- Python: `statsmodels.stats.multitest.multipletests(p, method='fdr_bh')`

## The Single Most Important Modern Insight -- FDR vs FWER Is a Choice About Which Error Matters

The choice between false-discovery-rate and family-wise-error control is not a technicality; it is a statement about which kind of mistake is costly. In **discovery** (20,000 genes, thousands of peaks), tolerating a small, controlled fraction of false positives among the rejections buys enormous power — FDR is the right currency, and Bonferroni would discard nearly every true effect. In **confirmatory** work (a handful of pre-specified endpoints), a single false positive is unacceptable and FWER/closed testing is the standard (that regime lives in clinical-biostatistics/multiplicity-graphical). Two further levers buy back power that plain BH leaves on the table: estimating **pi0** (the proportion of true nulls) turns BH into the more powerful **q-value** (Storey 2002 *J R Stat Soc B* 64:479; Storey & Tibshirani 2003 *PNAS* 100:9440), and weighting hypotheses by an **independent informative covariate** recovers power via **IHW** (Ignatiadis 2016 *Nat Methods* 13:577). The dependence structure matters: BH controls FDR under independence or positive regression dependence (PRDS); under arbitrary or negative dependence use **BY** (Benjamini & Yekutieli 2001 *Ann Stat* 29:1165).

## Algorithmic Taxonomy

| Method | Controls | Dependence assumption | When to use | Tool |
|--------|----------|------------------------|-------------|------|
| Bonferroni | FWER | any | tiny families; confirmatory | `p.adjust(method='bonferroni')` |
| Holm | FWER | any | uniformly beats Bonferroni | `p.adjust(method='holm')` |
| Hochberg / Hommel | FWER | positive dependence | step-up FWER, more power | `p.adjust(method='hochberg'/'hommel')` |
| Benjamini-Hochberg | FDR | independence / PRDS | genome-wide discovery default | `p.adjust(method='BH')` |
| Benjamini-Yekutieli | FDR | arbitrary (incl. negative) | unknown/negative dependence | `p.adjust(method='BY')` |
| Storey q-value | pFDR | independence / weak dependence | many true positives (pi0 << 1) | `qvalue::qvalue` |
| Local FDR | posterior null prob | two-groups model | per-feature null probability | `qvalue` ($lfdr); `locfdr` |
| IHW | FDR | covariate independent of null p | informative covariate available | `IHW::ihw` |
| IDR | reproducibility | replicate ranks | thresholding by replicate consistency | `idr` (ENCODE) |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Genome-wide DE / peaks, discovery | BH or q-value at FDR 0.05 | controlled false-positive fraction; high power |
| Many true positives expected | q-value (estimates pi0) | more powerful than BH when pi0 << 1 |
| Strong/unknown/negative dependence | BY | BH guarantee needs PRDS |
| Informative covariate (mean expr, peak width) | IHW | data-driven weights recover power |
| Per-feature "is this one real?" | local FDR | posterior null probability, not tail average |
| Reporting CIs only on significant hits | FCR-adjusted intervals | naive selected CIs under-cover |
| Small confirmatory gene panel | Bonferroni/Holm | FWER appropriate; power loss acceptable |
| GWAS | genome-wide threshold ~5e-8 | ~1M effective independent tests |
| Confirmatory trial, few endpoints | -> clinical-biostatistics/multiplicity-graphical | closed testing / gatekeeping |
| Applying padj to a finished DE table | -> differential-expression/de-results | method choice here; application there |

## FDR -- Benjamini-Hochberg and the q-value

```r
# Benjamini-Hochberg adjusted p-values (the genome-wide default)
padj <- p.adjust(pvalues, method = 'BH')
sum(padj < 0.05)                                  # discoveries at FDR 5%

# Storey q-value: estimates pi0 (fraction of true nulls) for more power when pi0 << 1
library(qvalue)
qobj <- qvalue(pvalues)
qobj$pi0                                           # estimated proportion of true nulls
q   <- qobj$qvalues                                # min FDR at which each feature is called
lfdr <- qobj$lfdr                                  # local FDR: posterior P(null | statistic)
```

## Dependence -- When BH Is Not Enough (BY)

```r
# BH controls FDR under independence or positive regression dependence (PRDS).
# Under arbitrary or negative dependence, use Benjamini-Yekutieli (more conservative).
padj_by <- p.adjust(pvalues, method = 'BY')        # valid under any dependence structure
```

## Covariate-Weighted FDR -- IHW

```r
# Weight hypotheses by an INDEPENDENT informative covariate (e.g. mean expression),
# which must be independent of the p-value under the null. Recovers power vs plain BH.
library(IHW)
res <- ihw(pvalue ~ mean_expression, data = de_table, alpha = 0.05)
de_table$padj_ihw <- adj_pvalues(res)
rejections(res)
```

## Independent Filtering -- Power for Free, If the Filter Is Independent

Filtering out features before testing increases power **only if** the filter statistic is independent of the test statistic under the null (Bourgon, Gentleman & Huber 2010 *PNAS* 107:9546). Overall mean count is independent and is why DESeq2 filters low-count genes automatically; a pre-test on variance or a preliminary t-test is **not** independent and biases the FDR. The DE filtering itself is executed in differential-expression; this skill governs whether a proposed filter is legitimate.

## Python Equivalent (mind the default)

```python
from statsmodels.stats.multitest import multipletests
# DEFAULT method is 'hs' (Holm-Sidak, FWER) -- ALWAYS pass method explicitly.
rej, padj, _, _ = multipletests(pvalues, alpha=0.05, method='fdr_bh')   # Benjamini-Hochberg
rej_by, padj_by, _, _ = multipletests(pvalues, alpha=0.05, method='fdr_by')  # BY
```

## GWAS and the Family-Definition Problem

The genome-wide significance threshold of ~5e-8 is a Bonferroni-style bound for roughly one million effectively independent common-variant tests; Dudbridge & Gusnanto 2008 (*Genet Epidemiol* 32:227) derived ~7.2e-8 for European-ancestry data, near the standard 5e-8. The GWAS test machinery lives in population-genetics/association-testing. More broadly, **what counts as "the family"** of tests is an analyst decision and part of the garden of forking paths: correcting within one contrast, across all contrasts, or across a whole paper are different alpha budgets. Pre-specify the family before seeing results.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| q-value finds many more hits than BH | pi0 << 1 (many true positives) | q-value legitimately more powerful; report pi0 |
| BY far more conservative than BH | strong/negative dependence penalty | if dependence is positive, BH is justified; state the assumption |
| IHW and BH differ substantially | informative, null-independent covariate | IHW gain is real if independence holds; verify the covariate |
| Filtering changed the hit count | filter not independent of the test statistic | use a null-independent filter (mean count), not variance/preliminary test |
| Per-feature local FDR high but BH q low | tail-average vs per-feature interpretation | report both; local FDR answers "is THIS one real?" |

## Per-Method Failure Modes

### Bonferroni on a transcriptome
- **Trigger:** Bonferroni across 20,000 genes in a discovery study.
- **Mechanism:** FWER control is far too strict for discovery.
- **Symptom:** almost nothing significant; true effects discarded.
- **Fix:** BH or q-value at a target FDR.

### BH under arbitrary/negative dependence
- **Trigger:** BH on strongly/negatively correlated statistics.
- **Mechanism:** BH guarantee requires independence or PRDS (Benjamini-Yekutieli 2001).
- **Symptom:** realized FDR exceeds nominal.
- **Fix:** BY when dependence is unknown or negative.

### statsmodels default is not BH
- **Trigger:** `multipletests(p)` expecting Benjamini-Hochberg.
- **Mechanism:** default `method='hs'` (Holm-Sidak, FWER).
- **Symptom:** far fewer significant calls than expected.
- **Fix:** pass `method='fdr_bh'` explicitly.

### Non-independent filtering
- **Trigger:** filter on variance or a preliminary test before the main test.
- **Mechanism:** filter statistic correlated with the test statistic under the null (Bourgon 2010).
- **Symptom:** anti-conservative FDR.
- **Fix:** filter only on a null-independent statistic (overall mean count).

### Selected CIs without FCR adjustment
- **Trigger:** reporting unadjusted CIs only for significant features.
- **Mechanism:** selection induces under-coverage (false coverage rate).
- **Symptom:** intervals too narrow; replication misses.
- **Fix:** FCR-adjusted intervals for the selected set.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| FDR < 0.05 discovery default | Benjamini-Hochberg 1995 *JRSS-B* 57:289 | 5% of calls expected false |
| FDR < 0.10 exploratory | common practice | more leads at higher false fraction |
| q-value uses estimated pi0 | Storey 2002 *JRSS-B* 64:479 | power gain when pi0 << 1 |
| BH valid under independence/PRDS; else BY | Benjamini-Yekutieli 2001 *Ann Stat* 29:1165 | dependence governs validity |
| GWAS ~5e-8 (7.2e-8 derived) | Dudbridge-Gusnanto 2008 *Genet Epidemiol* 32:227 | ~1M effective tests |
| Filter must be null-independent | Bourgon 2010 *PNAS* 107:9546 | otherwise FDR is biased |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Almost nothing significant genome-wide | Bonferroni in a discovery study | BH or q-value |
| Realized FDR exceeds nominal | BH under negative dependence | BY |
| Far fewer hits than expected in Python | statsmodels default 'hs' | `method='fdr_bh'` |
| FDR biased after pre-filtering | non-independent filter | filter on mean count only |
| Replication misses "significant" effects | unadjusted selected CIs | FCR-adjusted intervals |

## References

- Benjamini Y, Hochberg Y. 1995. Controlling the false discovery rate: a practical and powerful approach to multiple testing. *J R Stat Soc B* 57:289-300.
- Benjamini Y, Yekutieli D. 2001. The control of the false discovery rate in multiple testing under dependency. *Ann Stat* 29:1165-1188.
- Storey JD. 2002. A direct approach to false discovery rates. *J R Stat Soc B* 64:479-498.
- Storey JD, Tibshirani R. 2003. Statistical significance for genomewide studies. *PNAS* 100:9440-9445.
- Efron B. 2008. Microarrays, empirical Bayes and the two-groups model. *Stat Sci* 23:1-22.
- Bourgon R, Gentleman R, Huber W. 2010. Independent filtering increases detection power for high-throughput experiments. *PNAS* 107:9546-9551.
- Ignatiadis N, Klaus B, Zaugg JB, Huber W. 2016. Data-driven hypothesis weighting increases detection power in genome-scale multiple testing. *Nat Methods* 13:577-580.
- Li Q, Brown JB, Huang H, Bickel PJ. 2011. Measuring reproducibility of high-throughput experiments. *Ann Appl Stat* 5:1752-1779.
- Dudbridge F, Gusnanto A. 2008. Estimation of significance thresholds for genomewide association scans. *Genet Epidemiol* 32:227-234.

## Related Skills

- power-analysis - The FDR target feeds the power/EDR calculation
- sample-size - Replicate number depends on the FDR threshold chosen here
- batch-design - Surrogate variables change the effective number of tests
- differential-expression/de-results - Where the padj column is applied to a DE table
- population-genetics/association-testing - GWAS genome-wide significance machinery
- pathway-analysis/go-enrichment - Correcting enrichment p-values
- clinical-biostatistics/multiplicity-graphical - Confirmatory FWER / closed testing for trials with few endpoints
<!-- END FILE: experimental-design/multiple-testing/SKILL.md -->

## 子目录：experimental-design/power-analysis

<!-- BEGIN FILE: experimental-design/power-analysis/SKILL.md -->
---
name: bio-experimental-design-power-analysis
description: Calculates statistical power for high-dimensional genomics experiments (bulk RNA-seq, scRNA-seq, ATAC-seq, ChIP-seq, methylation, proteomics) under negative-binomial count models using RNASeqPower, PROPER, and simulation via powsimR, distinguishing per-gene from marginal (transcriptome-wide) power, the role of mean expression and dispersion, and the sequencing-depth-versus-replicate tradeoff. Covers simulation as the honest default for overdispersed counts, FDR-aware average power versus single-test power, observed/post-hoc power as an anti-pattern, and the winner's-curse / Type-S / Type-M consequences of underpowering. Use when planning replicate number for a sequencing experiment, deciding whether to add depth or samples, choosing closed-form versus simulation power, estimating power from pilot dispersions, or justifying replication in a grant. For clinical-trial power see clinical-biostatistics/power-and-sample-size; for the inverse sample-size question see experimental-design/sample-size.
tool_type: r
primary_tool: RNASeqPower
---

## Version Compatibility

Reference examples tested with: RNASeqPower 1.42+, PROPER 1.34+, powsimR 1.2+ (GitHub), DESeq2 1.42+, edgeR 4.0+, pwr 1.3+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws an error, introspect the installed package and adapt to the actual API. Notes: `RNASeqPower::rnapower()` solves for whichever of `n` or `power` is omitted; PROPER is a multi-step pipeline (`RNAseq.SimOptions.2grp` -> `simRNAseq` -> `runSims` -> `comparePower`); powsimR is GitHub-only and its `estimateParam`/`Setup`/`simulateDE` signatures drift — pin a commit SHA for reproducible work. Verify each against the installed help before relying on argument names.

# Power Analysis for Genomics Experiments

**"How many replicates does my sequencing experiment need?"** -> Compute the probability of detecting a biologically meaningful effect given replicate number, sequencing depth, and biological variability — modeling counts as negative-binomial and recognizing that power is a per-gene quantity, not one number for the whole transcriptome.
- R: `RNASeqPower::rnapower()` — closed-form NB power/sample size; `PROPER`, `powsimR` — simulation from the mean-dispersion trend

## The Single Most Important Modern Insight -- Genomics Power Is Per-Gene; Simulate, and Never Report Observed Power

Power in a sequencing experiment is not a single number. It is a per-gene quantity that depends on that gene's mean expression and dispersion, so the honest summary is the **marginal (average) power** across the expression distribution at a target FDR — the expected discovery rate. A single coefficient of variation plugged into a closed-form formula mis-states power for low- and high-expressed genes alike, because dispersion varies systematically with the mean; the defensible default for count data is **simulation from the empirical mean-dispersion trend** (PROPER, Wu 2015 *Bioinformatics* 31:233; powsimR, Vieth 2017 *Bioinformatics* 33:3486). The second rule is negative: **observed (post-hoc) power is information-free.** Computed from the effect a study actually estimated, it is a one-to-one function of the p-value and cannot explain a null result (Hoenig & Heisey 2001 *Am Stat* 55:19). Power is a design-stage quantity, computed for hypothesized effects before data exist. Underpowering does not merely miss true effects — it makes the significant ones overstate magnitude (Type-M) and sometimes reverse sign (Type-S), lowering the chance a significant call is real (Button 2013 *Nat Rev Neurosci* 14:365; Gelman & Carlin 2014 *Perspect Psychol Sci* 9:641).

## Algorithmic Taxonomy

| Approach | Model | Tool | Strength | Fails / costs when |
|----------|-------|------|----------|--------------------|
| NB closed-form | negative-binomial, single CV/dispersion | `RNASeqPower::rnapower` | fast; transparent; grant-ready | one CV cannot represent the mean-dispersion trend |
| Simulation, parametric | NB with mean-dispersion relationship | `PROPER` | honest marginal power + EDR at target FDR | needs a dispersion model / pilot |
| Simulation, empirical | resampled from pilot (incl. dropout) | `powsimR` | bulk AND scRNA-seq; realistic | GitHub-only; heavier; version drift |
| Gaussian closed-form | t-test / Cohen's d | `pwr::pwr.t.test` | per-feature ATAC/proteomics after transform | wrong for raw counts; ignores overdispersion |
| Effect-inflation design analysis | retrodesign for Type-S/Type-M | `retrodesign` (Gelman) | exposes exaggeration in noisy small-n | needs a plausible true effect |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Bulk RNA-seq, pilot data available | PROPER/powsimR simulation from pilot dispersions | matches the real mean-dispersion trend |
| Bulk RNA-seq, no pilot, quick grant number | `rnapower()` with a literature CV, stated as approximate | transparent; flag as conservative-to-rough |
| scRNA-seq cross-condition DE | powsimR on a pseudobulk model; power scales with samples | population power is set by donors, not cells |
| ATAC/ChIP/methylation per-region | NB simulation (PROPER-style) or pwr after variance-stabilizing | overdispersed counts; per-region power |
| Proteomics (continuous, log-abundance) | `pwr::pwr.t.test` per protein with missingness caveat | Gaussian after transform; MNAR matters |
| Justifying a null result post-hoc | report CI / effect size, NOT observed power | post-hoc power is uninformative (Hoenig-Heisey) |
| Fixed budget: depth vs replicates | favor replicates past ~10-20M mapped reads | biological variance dominates (Liu 2014) |
| Clinical-trial endpoint | -> clinical-biostatistics/power-and-sample-size | regulated regime, different machinery |

## Closed-Form NB Power -- RNASeqPower

**Goal:** Get a fast, transparent power or replicate number for bulk RNA-seq from depth, biological CV, and fold change.

**Approach:** Supply per-gene depth, biological coefficient of variation, the fold change to detect, and alpha; supply `n` to get power, or `power` to get the required `n`. Treat the result as a single-gene approximation and sanity-check against simulation.

```r
library(RNASeqPower)
# depth = reads/gene; cv = biological coefficient of variation; effect = fold change
rnapower(depth = 20, n = 5, cv = 0.4, effect = 2, alpha = 0.05)          # solves for POWER
rnapower(depth = 20, cv = 0.4, effect = 2, alpha = 0.05, power = 0.80)   # solves for n per group
```

## Simulation-Based Power -- the Honest Default for Counts

**Goal:** Estimate marginal power and the true realized FDR across the whole expression distribution, accounting for the mean-dispersion trend.

**Approach:** Build (or fit from pilot) a simulation model of counts with a realistic dispersion-mean relationship and DE-effect distribution, simulate many datasets at each candidate sample size, run the intended DE test, and read the average power at the target FDR.

```r
library(PROPER)
sim_opts <- RNAseq.SimOptions.2grp(ngenes = 20000, p.DE = 0.05,
                                   lOD = 'cheung', lBaselineExpr = 'cheung')  # empirical dispersion/expr priors
sims <- runSims(Nreps = c(3, 5, 8, 12), sim.opts = sim_opts, nsims = 50,
                DEmethod = 'edgeR')
powr <- comparePower(sims, alpha.type = 'fdr', alpha.nominal = 0.05,
                     stratify.by = 'expr', delta = log(1.5))          # delta is NATURAL-log lfc in PROPER; marginal power by expression stratum
summaryPower(powr)
```

## Depth vs Replicates -- the Budget Question

For bulk RNA-seq differential expression, sequencing depth shows diminishing returns once it is adequate — Liu, Zhou & White 2014 (*Bioinformatics* 30:301) found the inflection near **~10 million mapped reads** in MCF7 (commonly generalized to a 10-20M band) — whereas adding biological replicates improves power across the whole range. Under a fixed budget, allocate to more biological units before more depth. ATAC/ChIP have their own depth floors (library complexity, peak detection), but the principle holds: biological variance, not read count, limits discovery once depth is adequate.

## CV / Dispersion Guidelines (estimate from pilot when possible)

| Material | Typical biological CV | Source / note |
|----------|----------------------|---------------|
| Cell lines (technical replicates) | 0.1-0.2 | low biological variability |
| Inbred mice | 0.2-0.3 | moderate |
| Primary cells / donor-derived | 0.3-0.4 | donor-dependent |
| Human population samples | 0.3-0.5 | high; Hart 2013 *J Comput Biol* 20:970 default examples |

These are starting points, not substitutes for a pilot estimate; real dispersion is study-specific and a literature CV can be off by a factor of two (estimate via DESeq2/edgeR `estimateDispersions` — see experimental-design/sample-size).

## Per-Method Failure Modes

### Single CV for the whole transcriptome
- **Trigger:** one `cv` plugged into `rnapower()` for all genes.
- **Mechanism:** dispersion varies with mean expression; a single CV mis-states low/high-expressed genes.
- **Symptom:** simulation gives materially different power than the closed form.
- **Fix:** simulation-based power (PROPER/powsimR) from the mean-dispersion trend.

### Observed (post-hoc) power
- **Trigger:** "non-significant, but observed power was 0.3, so add samples."
- **Mechanism:** observed power is a monotone function of the p-value (Hoenig-Heisey 2001).
- **Symptom:** circular reasoning that adds nothing to the CI.
- **Fix:** report effect size + CI; do prospective power for the next study.

### Powering to the expected (or pilot-observed) effect
- **Trigger:** setting the effect to the hoped-for or pilot point estimate.
- **Mechanism:** the pilot estimate is itself noisy; building it in bakes in the winner's curse.
- **Symptom:** chronic underpowering; inflated significant effects (Type-M).
- **Fix:** power to the minimum biologically meaningful effect; propagate pilot variance, not its mean.

### Depth instead of replicates
- **Trigger:** "we will sequence deeper rather than add samples."
- **Mechanism:** past ~10-20M reads, biological variance dominates technical (Liu 2014).
- **Symptom:** deep libraries, still underpowered.
- **Fix:** add biological replicates.

### scRNA-seq power computed on cells
- **Trigger:** "100k cells from 2 patients gives huge power."
- **Mechanism:** population DE power is set by the number of biological samples; cells are pseudoreplicates.
- **Symptom:** power estimate wildly optimistic; results do not replicate.
- **Fix:** power on a pseudobulk model over donors (powsimR); see randomization-blocking.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Power >= 0.80 standard; >= 0.90 for pivotal | convention | tolerable Type-II risk |
| Depth saturates ~10-20M mapped reads for DE | Liu 2014 *Bioinformatics* 30:301 | biological variance then dominates |
| >=6 biological replicates recover most true DE | Schurch 2016 *RNA* 22:839 | n=3 misses many true DE at realistic effects |
| Observed power is a function of the p-value | Hoenig-Heisey 2001 *Am Stat* 55:19 | never use it to interpret a null |
| Type-M exaggeration large in noisy small-n | Gelman-Carlin 2014 *Perspect Psychol Sci* 9:641 | significant effects overstated |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Closed-form and simulation power disagree | single CV vs mean-dispersion trend | use simulation for the reported number |
| "Underpowered (observed power 0.3)" to excuse a null | post-hoc power fallacy | report CI; prospective power only |
| Deep libraries still underpowered | depth over replicates | add biological replicates |
| scRNA-seq power absurdly high | power computed on cells | pseudobulk power over donors |
| Significant effect far larger than literature | winner's curse from underpowering | design analysis (Type-S/Type-M); replicate |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Where did the CV come from?" | estimated from pilot dispersions (DESeq2); literature value used only as a conservative cross-check |
| "Why simulation rather than a formula?" | count power is per-gene; simulation captures the mean-dispersion trend and reports marginal power at the target FDR |
| "Is the study powered?" | marginal power >= 0.8 at FDR 0.05 for the minimum meaningful fold change; power curve provided |
| "Why not just sequence deeper?" | depth saturates ~10-20M reads (Liu 2014); replicates added instead |
| "Observed power of the null?" | observed power is uninformative (Hoenig-Heisey); CI on the effect reported instead |

## References

- Hart SN, Therneau TM, Zhang Y, Poland GA, Kocher JP. 2013. Calculating sample size estimates for RNA sequencing data. *J Comput Biol* 20:970-978.
- Wu H, Wang C, Wu Z. 2015. PROPER: comprehensive power evaluation for differential expression using RNA-seq. *Bioinformatics* 31:233-241.
- Vieth B, Ziegenhain C, Parekh S, Enard W, Hellmann I. 2017. powsimR: power analysis for bulk and single cell RNA-seq experiments. *Bioinformatics* 33:3486-3488.
- Liu Y, Zhou J, White KP. 2014. RNA-seq differential expression studies: more sequence or more replication? *Bioinformatics* 30:301-304.
- Schurch NJ, Schofield P, Gierliński M, et al. 2016. How many biological replicates are needed in an RNA-seq experiment and which differential expression tool should you use? *RNA* 22:839-851.
- Hoenig JM, Heisey DM. 2001. The abuse of power: the pervasive fallacy of power calculations for data analysis. *Am Stat* 55:19-24.
- Button KS, Ioannidis JPA, Mokrysz C, Nosek BA, Flint J, Robinson ESJ, Munafò MR. 2013. Power failure: why small sample size undermines the reliability of neuroscience. *Nat Rev Neurosci* 14:365-376.
- Gelman A, Carlin J. 2014. Beyond power calculations: assessing Type S (sign) and Type M (magnitude) errors. *Perspect Psychol Sci* 9:641-651.
- Ioannidis JPA. 2005. Why most published research findings are false. *PLoS Med* 2:e124.

## Related Skills

- sample-size - The inverse problem: minimum replicates for a target power at a target FDR
- randomization-blocking - The experimental unit defines what is replicated; blocking changes error variance
- batch-design - Account for batch/blocking factors in the power model
- differential-expression/deseq2-basics - Estimating dispersions from pilot data for the power model
- single-cell/preprocessing - Pseudobulk model underlying scRNA-seq power
- clinical-biostatistics/power-and-sample-size - Power for regulated clinical-trial endpoints
<!-- END FILE: experimental-design/power-analysis/SKILL.md -->

## 子目录：experimental-design/randomization-blocking

<!-- BEGIN FILE: experimental-design/randomization-blocking/SKILL.md -->
---
name: bio-experimental-design-randomization-blocking
description: Structures biological experiments so inference is valid by construction, covering Fisher's principles (randomization, replication, local control), the experimental-vs-observational unit distinction and pseudoreplication (Hurlbert 1984; Lazic 2018), randomization mechanics (complete, restricted, stratified, rerandomization, run-order), blocking layouts (randomized complete block, Latin square, incomplete block), factorial designs and interactions, and the split-plot/nested error strata hidden inside multi-batch genomics. Use when deciding the experimental unit and what counts as a replicate, planning randomization and run order, choosing a blocked/factorial/split-plot/nested layout, avoiding pseudoreplication in cell-culture or animal studies, or specifying the random-effects structure of the analysis model. For assigning samples to sequencing batches/lanes/plates and batch-effect correction see experimental-design/batch-design; for regulated clinical-trial randomization see clinical-biostatistics.
tool_type: r
primary_tool: designit
---

## Version Compatibility

Reference examples tested with: designit 0.5+, lme4 1.1-35+, lmerTest 3.1+, pwr 1.3+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws an error, introspect the installed package and adapt the example to the actual API rather than retrying. designit is an R6 package whose `BatchContainer$new()`, `optimize_design()`, and `*_score_generator()` signatures evolve between releases; confirm against the installed vignette (`vignette(package = 'designit')`) before relying on argument names.

# Randomization and Blocking

**"Design the experiment so the statistics will be valid"** -> Decide what the experimental unit is, randomize treatments to those units, replicate the unit (not the measurement), and remove known nuisance variation by blocking — so that the analysis model mirrors how the experiment was actually run.
- R: `designit::optimize_design()` for constrained randomization; `lme4::lmer()` / `lmerTest` for the matching mixed model
- The design and the analysis are one decision: "analyze as randomized"

## The Single Most Important Modern Insight -- The Experimental Unit, Not the Measurement, Is the n

The most consequential and most violated idea in biological design: the **experimental unit (EU)** is the smallest entity *independently assigned to a treatment* — and it, not the number of measurements, is the sample size for inference. Lazic 2018 *PLoS Biol* 16:e2005282 separates three entities: the **biological unit** (what conclusions are about), the **experimental unit** (what randomization acts on, = the n), and the **observational unit** (what is measured). When observational units are counted as independent replicates, the standard error shrinks illegitimately and p-values become meaningless — **pseudoreplication** (Hurlbert 1984 *Ecol Monogr* 54:187). Ten thousand cells from three mice are n = 3, not n = 10,000, for a between-mouse question; mice co-housed in a cage dosed through the chow make the *cage* the EU, not the mouse. Lazic et al. found ~46% of surveyed animal studies pseudoreplicated. The fix is structural: model the design's hierarchy (random effects) or aggregate to the EU before testing — pseudoreplication is, formally, an omitted random effect.

A second, deeper point (Fisher): **randomization is what licenses the p-value.** It supplies the physical basis for the error term and converts systematic lurking-variable bias into random error balanced *in expectation*. Model-based tests are approximations to the randomization distribution. Skip randomization and the causal claim rests entirely on assumptions.

## Algorithmic Taxonomy

| Design | Controls / estimates | When to use | Fails / costs when |
|--------|----------------------|-------------|--------------------|
| Completely randomized (CRD) | error variance only | units homogeneous; no known nuisance | inefficient if real nuisance structure exists |
| Randomized complete block (RCBD) | one known nuisance (day, litter, chip, donor) | nuisance factor identifiable and blockable | costs error df; harmful if block variance is ~0 ("blocking on noise") |
| Latin square | two orthogonal nuisances (day x technician) | n² runs affordable for n treatments | assumes no interaction among row/col/treatment |
| (Balanced) incomplete block | one nuisance, block smaller than #treatments | plate/chip holds fewer samples than treatments | analysis more complex; needs balance for efficiency |
| Factorial | main effects + interactions, "hidden replication" | >1 factor; interaction is of interest | #runs grows multiplicatively |
| Fractional factorial / screening | main effects under sparsity-of-effects | many factors, few runs (Plackett-Burman) | aliases effects; cannot resolve all interactions |
| Split-plot | two EU sizes, two error strata | one factor hard to randomize finely (lane, incubator, batch) | wrong error term if analyzed as a flat factorial -> anti-conservative |
| Nested / hierarchical | variance components across levels | sub-sampling within units (cells in mice in cages) | pseudoreplication if the nesting is ignored |
| Repeated measures | within-unit change over time | longitudinal sampling of the same EU | a split-plot in time; needs the within-unit error term |

## Decision Tree by Scenario

| Scenario | Recommended structure | Why |
|----------|----------------------|-----|
| Treatment given per animal, one tissue measured each | CRD or RCBD; n = animals | EU = animal |
| Many cells measured per animal, between-animal question | nested; aggregate to per-animal (pseudobulk) before testing | EU = animal, cells are observational units |
| Treatment delivered per cage (chow/water), several mice/cage | EU = cage; block or model cage as random | randomization acted on the cage |
| Two factors of interest (genotype x drug) | factorial; estimate the interaction | main effects uninterpretable if interaction is large |
| One factor fixed per run (incubator temp, sequencing lane) | split-plot; whole-plot = run, sub-plot = sample | two error strata; test whole-plot against whole-plot error |
| Known batch/day nuisance, all conditions fit per block | RCBD; include block in the model | removes nuisance from error; "analyze as randomized" |
| Plate holds fewer samples than conditions | incomplete block + include block term | balance preserves estimability |
| Assigning samples to sequencing batches/lanes | -> experimental-design/batch-design | constrained sample-to-batch allocation lives there |
| Regulated clinical trial randomization | -> clinical-biostatistics | confirmatory/regulated regime out of scope |

## Choosing and Counting the Experimental Unit

**Goal:** Identify the EU and therefore the true n before any power or analysis decision.

**Approach:** Trace the randomization: the EU is the smallest entity to which a treatment level was independently assigned. Anything measured below that level is an observational unit and is summarized (mean/sum) up to the EU, or modeled as a nested random effect — never counted as an independent replicate.

```r
# Between-condition question with multiple cells per donor:
# the donor is the experimental unit, NOT the cell.
# Correct: aggregate observational units to the EU, then test on EU-level values.
library(dplyr)
eu_level <- cells |>
  group_by(donor, condition) |>
  summarise(value = mean(measurement), .groups = 'drop')   # one row per experimental unit
# n for inference = number of donors per condition, not number of cells
```

## Randomization Mechanics

**Goal:** Assign treatments to units with a documented random mechanism, optionally restricted to guarantee balance on known factors.

**Approach:** Use a seeded pseudo-random generator (never "haphazard" order, which aliases treatment with processing position/time). For known prognostic factors, restrict the randomization (block/stratify) and then *include those factors in the model*. When finite-sample imbalance matters, rerandomize against a pre-specified balance criterion (Morgan & Rubin 2012 *Ann Stat* 40:1263) or use minimization for sequential enrollment (Pocock & Simon 1975 *Biometrics* 31:103).

```r
set.seed(20260528)                      # record the seed for reproducibility
units <- data.frame(id = sprintf('S%02d', 1:24),
                    block = rep(c('day1','day2','day3'), each = 8))

# Restricted (block) randomization: randomize treatment WITHIN each block
units$treatment <- ave(units$id, units$block,
                       FUN = function(ids) sample(rep(c('ctrl','treat'),
                                                      length.out = length(ids))))
# Also randomize RUN ORDER so processing position is not confounded with treatment
units$run_order <- sample(nrow(units))
```

## Blocking and Local Control

**Goal:** Remove a known nuisance source from the error term to sharpen the treatment comparison.

**Approach:** Group units into homogeneous blocks (day, litter, chip, donor), randomize treatments within block, and add the block as a term in the model. The paired t-test is the special case of an RCBD with block size 2. Block only on factors with real between-block variation; blocking on a noise factor spends error df for nothing.

```r
library(designit)                        # constrained assignment; verify API vs installed vignette
bc <- BatchContainer$new(dimensions = list(block = 3, position = 8))
bc <- assign_in_order(bc, samples = units)
bc <- optimize_design(
  bc,
  scoring = osat_score_generator(batch_vars = 'block',
                                 feature_vars = c('treatment')))  # balance treatment across blocks
```

## Split-Plot and Nested Designs -- the Genomics Trap

A **split-plot** has two experimental-unit sizes and therefore two error strata: a *whole-plot* factor that is hard to randomize finely (incubator temperature, the sequencing run/lane, the 10x chip, the staining batch) and a *sub-plot* factor randomized within each whole plot (the individual sample, the genotype). Analyzing a split-plot as a flat factorial uses the wrong, too-small error term for the whole-plot factor and gives **anti-conservative** tests for exactly the factor that was hardest to replicate. In genomics the lane/run/chip is almost always a whole plot; "batch effects" are frequently a split-plot structure to be modeled, not a nuisance to scrub.

**Goal:** Match the model's random-effects structure to the design's randomization structure.

**Approach:** Encode each randomization level as a random effect; fixed effects carry the questions. Crossed vs nested structure determines the denominator for each fixed effect; with few EUs use Satterthwaite or Kenward-Roger degrees of freedom (lmerTest / pbkrtest).

```r
library(lme4); library(lmerTest)
# Whole plot = run (random); sub-plot factor = condition (fixed); cells nested in sample
fit <- lmer(expression ~ condition + (1 | run/sample), data = df)   # run, and sample within run
anova(fit)                               # Satterthwaite df via lmerTest
```

## Factorial Designs and Interactions

A factorial design crosses factors so every observation informs every main effect ("hidden replication") and, uniquely, estimates **interactions** — the joint action one-factor-at-a-time (OFAT) cannot see. When an interaction is large, main effects are not interpretable alone; reporting a main effect while ignoring a strong interaction is the most common misreading of a 2x2 design. OFAT is less efficient and silently assumes additivity.

## Per-Method Failure Modes

### Pseudoreplication (observational units counted as n)
- **Trigger:** treating cells/wells/sections/technical aliquots as independent replicates.
- **Mechanism:** units within an EU are correlated; the SE is computed as if they were independent (Hurlbert 1984; Lazic 2018).
- **Symptom:** implausibly small p-values that fail to replicate; reviewers ask "what is n?".
- **Fix:** aggregate to the EU (pseudobulk) or add the EU as a random effect; the n is the number of EUs.

### Split-plot analyzed as a flat factorial
- **Trigger:** lane/run/incubator factor crossed with a within-run factor, fit with one error term.
- **Mechanism:** whole-plot factor tested against sub-plot error (too small).
- **Symptom:** the hard-to-randomize factor looks significant on thin evidence.
- **Fix:** two-stratum model; whole-plot factor uses whole-plot error (`(1 | run)`).

### Haphazard assignment mistaken for randomization
- **Trigger:** processing units "in the order they arrived".
- **Mechanism:** order aliases treatment with time/position/temperature gradients.
- **Symptom:** apparent treatment effect tracks run order.
- **Fix:** seeded PRNG assignment; randomize run order too; record the seed.

### Blocking on a noise factor
- **Trigger:** adding a block term with negligible between-block variance.
- **Mechanism:** spends error df without removing variance.
- **Symptom:** power lower than the unblocked design.
- **Fix:** block only on factors with documented between-block variation.

### Over-/under-specified random effects
- **Trigger:** maximal random structure that will not converge, or a structure missing a randomization level.
- **Mechanism:** maximal protects Type-I but may be singular (Barr 2013); too-lean inflates Type-I (pseudoreplication).
- **Symptom:** singular-fit warnings, or anti-conservative tests.
- **Fix:** keep the structure justified by the design; for small EU counts prune by a selection criterion (Matuschek 2017) and report the choice.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| EU = level of independent treatment assignment | Hurlbert 1984; Lazic 2018 | defines the n for inference |
| Paired design = RCBD with block size 2 | Fisher; standard | pairing is blocking |
| Latin square needs n² runs for n treatments | standard design theory | controls two nuisances orthogonally |
| Use Kenward-Roger/Satterthwaite df when EU count is small (roughly < ~10/group) | Kenward & Roger 1997 *Biometrics* 53:983 | naive F df are anti-conservative with few units |
| Maximal random effects for confirmatory; prune for small samples | Barr 2013; Matuschek 2017 | Type-I protection vs convergence/power tradeoff |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Significant result that will not replicate | pseudoreplication (cells as n) | aggregate to EU or add EU random effect |
| Whole-plot factor over-significant | split-plot analyzed flat | two-stratum mixed model |
| Treatment effect tracks processing order | no run-order randomization | seeded randomization of run order |
| Blocked design analyzed without block term | "design but don't analyze" | include block in the model; analyze as randomized |
| Main effect reported despite strong interaction | factorial misread | interpret simple effects within the interaction |
| Mixed model singular fit | over-specified random effects | prune to the design-justified structure (Matuschek 2017) |

## References

- Hurlbert SH. 1984. Pseudoreplication and the design of ecological field experiments. *Ecol Monogr* 54:187-211.
- Lazic SE, Clarke-Williams CJ, Munafò MR. 2018. What exactly is 'N' in cell culture and animal experiments? *PLoS Biol* 16:e2005282.
- Blainey P, Krzywinski M, Altman N. 2014. Points of significance: replication. *Nat Methods* 11:879-880.
- Krzywinski M, Altman N. 2014. Points of significance: designing comparative experiments. *Nat Methods* 11:597-598.
- Krzywinski M, Altman N. 2014. Points of significance: analysis of variance and blocking. *Nat Methods* 11:699-700.
- Morgan KL, Rubin DB. 2012. Rerandomization to improve covariate balance in experiments. *Ann Stat* 40:1263-1282.
- Pocock SJ, Simon R. 1975. Sequential treatment assignment with balancing for prognostic factors in the controlled clinical trial. *Biometrics* 31:103-115.
- Barr DJ, Levy R, Scheepers C, Tily HJ. 2013. Random effects structure for confirmatory hypothesis testing: keep it maximal. *J Mem Lang* 68:255-278.
- Matuschek H, Kliegl R, Vasishth S, Baayen H, Bates D. 2017. Balancing Type I error and power in linear mixed models. *J Mem Lang* 94:305-315.
- Kenward MG, Roger JH. 1997. Small sample inference for fixed effects from restricted maximum likelihood. *Biometrics* 53:983-997.
- Auer PL, Doerge RW. 2010. Statistical design and analysis of RNA sequencing data. *Genetics* 185:405-416.

## Related Skills

- batch-design - Assigning samples to sequencing batches/lanes and batch-effect correction
- sample-size - The experimental unit defines what is replicated and counted
- power-analysis - Blocking and nesting change the effective error variance
- multiple-testing - The design fixes what counts as a family of tests
- single-cell/preprocessing - Pseudobulk aggregation to the donor (experimental unit) for scRNA-seq
- differential-expression/deseq2-basics - The DE model that consumes the design's structure
- clinical-biostatistics/power-and-sample-size - Randomization and design in the regulated-trial regime
<!-- END FILE: experimental-design/randomization-blocking/SKILL.md -->

## 子目录：experimental-design/sample-size

<!-- BEGIN FILE: experimental-design/sample-size/SKILL.md -->
---
name: bio-experimental-design-sample-size
description: Estimates the minimum biological replicates (or cells/events) for a target power at a target FDR in genomics experiments using ssizeRNA, PROPER, powsimR for scRNA-seq, and pilot-data dispersion estimation from DESeq2/edgeR. Covers the biological-versus-technical replication distinction (technical replicates do not add degrees of freedom for biological inference), replicate-number-versus-sequencing-depth budgeting, scRNA-seq sample-versus-cell allocation under a pseudobulk model, and the critique that "n=3" is a publication convention rather than a power calculation. Use when budgeting a sequencing experiment, writing the sample-size justification in a grant, estimating replicates from pilot data, allocating a fixed budget between samples and depth, or planning scRNA-seq cohort size. For clinical-trial sample size see clinical-biostatistics/power-and-sample-size; for the power-given-n direction see experimental-design/power-analysis.
tool_type: r
primary_tool: ssizeRNA
---

## Version Compatibility

Reference examples tested with: ssizeRNA 1.3+, PROPER 1.34+, powsimR 1.2+ (GitHub), DESeq2 1.42+, edgeR 4.0+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws an error, introspect the installed package and adapt to the actual API. Notes: ssizeRNA provides `ssizeRNA_single()` (one mean/dispersion for all genes), `ssizeRNA_vary()` (genes vary), and `check.power()` (average power and true FDR for a given n); powsimR is GitHub-only with drifting signatures. Verify against the installed help before use.

# Sample Size for Genomics Experiments

**"How many samples do I need?"** -> Find the smallest number of biological replicates per group that achieves a target marginal power at a target FDR, given the dispersion and effect-size distribution expected for the assay — counting biological units, not measurements.
- R: `ssizeRNA::ssizeRNA_vary()`, `ssizeRNA::check.power()` — FDR-aware NB sample size; pilot dispersions from `DESeq2`/`edgeR`

## The Single Most Important Modern Insight -- The Biological Replicate Is the Unit, and n=3 Is a Convention

Sample size is a count of **biological replicates** — independent experimental units (animals, donors, cultures from independent passages), not measurements. Technical replicates (one library split across lanes, one RNA split into preps) reduce measurement noise but add **no degrees of freedom** for biological inference; averaging them into their biological unit is correct, and selling "n = 3 samples x 3 technical reps = 9" as biological power is a standard error (Blainey, Krzywinski & Altman 2014 *Nat Methods* 11:879). The ubiquitous **"n=3" is a publication convention, not a calculation**: in the 48-vs-48 yeast benchmark, **>=6** biological replicates were needed to recover most true DE genes at realistic effect sizes, and below that the choice of DE tool mattered more than at higher n (Schurch 2016 *RNA* 22:839). Human and primary material, with higher dispersion, need more. For single-cell, the corollary is sharp: population-level DE power is set by the **number of donors**, not the number of cells, because cells are pseudoreplicates — pseudobulk per donor is the correct unit (Squair 2021 *Nat Commun* 12:5692; Murphy & Skene 2022 *Nat Commun* 13:7851).

## Algorithmic Taxonomy

| Approach | Model | Tool | Strength | Fails / costs when |
|----------|-------|------|----------|--------------------|
| FDR-aware NB sample size | NB, varying mean/dispersion | `ssizeRNA::ssizeRNA_vary` | controls average power at a true FDR | needs a dispersion/expression model |
| Pilot-dispersion simulation | empirical dispersions from pilot | `PROPER`, `powsimR` | most defensible; study-specific | requires a pilot dataset |
| Single-parameter NB | one mean/dispersion for all genes | `ssizeRNA::ssizeRNA_single` | quick; transparent | ignores the mean-dispersion trend |
| Verify a planned n | average power + true FDR at fixed n | `ssizeRNA::check.power` | sanity-checks a budget-driven n | not a search over n |
| scRNA-seq cohort sizing | pseudobulk over donors | `powsimR` | counts the right unit (donors) | cell-level sizing is wrong unit |
| Per-feature t-test n | Gaussian (Cohen's d) | `pwr::pwr.t.test` | proteomics/continuous after transform | wrong for raw counts |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Bulk RNA-seq, pilot available | estimate dispersions, then `ssizeRNA_vary`/PROPER | study-specific dispersion beats a guess |
| Bulk RNA-seq, no pilot | `ssizeRNA_vary` with a literature dispersion, stated as approximate | transparent starting point |
| Budget already fixed at some n | `check.power` to report achieved power and true FDR | answers "is this n adequate?" |
| scRNA-seq disease vs control | size the number of DONORS (pseudobulk; powsimR) | population power scales with donors |
| ChIP/ATAC/methylation | NB sample size per region; assay floor as minimum | overdispersed counts; detection floor |
| Proteomics (continuous) | `pwr::pwr.t.test` per protein, with missingness caveat | Gaussian after transform |
| Have technical replicates | collapse to biological units first | technical reps add no biological df |
| Clinical-trial endpoint | -> clinical-biostatistics/power-and-sample-size | regulated regime |

## FDR-Aware NB Sample Size -- ssizeRNA

**Goal:** Find the minimum biological replicates per group for a target power at a target FDR, accounting for the proportion of DE genes and the mean-dispersion structure.

**Approach:** Specify the number of genes, the proportion non-DE (pi0), the mean count and dispersion (ideally from pilot data), the fold change, the target FDR, and the target power; let `ssizeRNA_vary` search replicate numbers and return the smallest that reaches the target.

```r
library(ssizeRNA)
res <- ssizeRNA_vary(nGenes = 20000, pi0 = 0.95,        # 5% DE
                     mu = 10, disp = 0.2,                # mean count + dispersion (from pilot ideally)
                     fc = 1.5, fdr = 0.05, power = 0.80,
                     maxN = 30)
res$ssize                                                # minimum n per group

# Verify a budget-fixed n: average power and TRUE realized FDR
check.power(nGenes = 20000, pi0 = 0.95, m = 6, mu = 10, disp = 0.2, fc = 1.5, fdr = 0.05, sims = 50)
```

## Pilot Dispersions Drive Honest Sample Size

**Goal:** Replace a guessed CV with a measured dispersion-mean trend from pilot data.

**Approach:** Fit dispersions on the pilot with DESeq2 or edgeR, summarize them, and feed them into the simulation-based estimator (PROPER or powsimR) rather than a single-CV closed form.

```r
library(DESeq2)
dds <- DESeqDataSetFromMatrix(pilot_counts, pilot_coldata, ~ condition)
dds <- DESeq(dds)
disp <- dispersions(dds)                                 # per-gene dispersion estimates
summary(disp[is.finite(disp)])                           # feed median/trend to PROPER/powsimR
# A literature CV can be off by ~2x; a pilot dispersion is the defensible input.
```

## Biological vs Technical Replication

Technical replicates estimate measurement variance; biological replicates estimate the variance that generalizes to the population, and only the latter supports inference about the biology. Average or sum technical replicates into their biological unit before any test. "n = 3 samples x 3 technical reps" is n = 3, not n = 9 (Blainey 2014). This is the sample-size face of the experimental-unit principle (see experimental-design/randomization-blocking).

## Replicates vs Depth Under a Fixed Budget

Once depth is adequate (roughly >=10-20M mapped reads for bulk RNA-seq DE), additional biological replicates buy more power than additional depth (Liu 2014 *Bioinformatics* 30:301). Allocate a fixed budget toward more biological units first. scRNA-seq has an analogous rule at the donor level: more donors beat more cells per donor for population DE, with cells per cell type showing diminishing returns past a few hundred (Squair 2021; Murphy-Skene 2022).

## Sample Size by Assay (floors under favorable conditions, not targets)

| Assay | Practical minimum | For small effects | Source / note |
|-------|-------------------|-------------------|---------------|
| Bulk RNA-seq | 3 (convention) | 6-12 | Schurch 2016 *RNA* 22:839: >=6 recovers most true DE |
| scRNA-seq (population DE) | 3 donors | 6+ donors | Squair 2021; donors, not cells, drive power |
| ATAC-seq | 2 | 4-6 | library complexity + peak detection floor |
| ChIP-seq | 2 | 3-4 | IDR reproducibility framework (ENCODE) |
| Proteomics (DIA/TMT) | 3 | 6-10 | higher missingness; MNAR |
| Methylation (array/WGBS) | 4 | 8-12 | high per-CpG variance |

The "minimum" columns are floors that assume low dispersion and large effects; treat them as the smallest defensible n only after a pilot or literature dispersion supports them.

## Per-Method Failure Modes

### Technical replicates counted as biological n
- **Trigger:** "n = 9: 3 samples x 3 technical reps."
- **Mechanism:** technical reps add no biological degrees of freedom (Blainey 2014).
- **Symptom:** over-stated power; results do not generalize.
- **Fix:** collapse technical reps to the biological unit; biological n = 3.

### n=3 by convention
- **Trigger:** choosing 3 because "everyone uses 3."
- **Mechanism:** 3 is a habit, not a calculation; misses many true DE (Schurch 2016).
- **Symptom:** chronic underpowering, irreproducibility.
- **Fix:** size from dispersion + target FDR; expect >=6 for realistic effects, more for human material.

### scRNA-seq sized on cells
- **Trigger:** "100k cells from 2 donors is plenty."
- **Mechanism:** population power scales with donors; cells are pseudoreplicates (Squair 2021).
- **Symptom:** false-discovery-laden DE that does not replicate.
- **Fix:** budget for more donors; size on a pseudobulk model.

### Guessed CV instead of pilot dispersion
- **Trigger:** "human samples are ~0.4, so use 0.4."
- **Mechanism:** real dispersion is study-specific; the guess can be off ~2x.
- **Symptom:** the planned n is wrong by a large factor.
- **Fix:** estimate dispersion from any available pilot (DESeq2/edgeR).

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| >=6 biological replicates for bulk RNA-seq DE | Schurch 2016 *RNA* 22:839 | recovers most true DE at realistic effects |
| n=3 is a convention, not a calculation | Schurch 2016 | low power and tool-dependent below 6 |
| Donors, not cells, set scRNA-seq DE power | Squair 2021 *Nat Commun* 12:5692 | cells are pseudoreplicates |
| Technical reps add 0 biological df | Blainey 2014 *Nat Methods* 11:879 | only biological reps generalize |
| Depth saturates ~10-20M reads; add replicates | Liu 2014 *Bioinformatics* 30:301 | biological variance dominates |
| Add 10-20% extra units for failures | common practice | RNA degradation, failed libraries |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Over-stated power | technical reps counted as n | collapse to biological units |
| Underpowered at n=3 | convention not calculation | size to >=6 (or pilot-driven) |
| scRNA-seq DE does not replicate | sized on cells | size on donors (pseudobulk) |
| Planned n off by a large factor | guessed CV | estimate dispersion from pilot |
| Study fails after sample loss | no failure margin | add 10-20% extra units |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Why this n?" | smallest n reaching marginal power >= 0.8 at FDR 0.05 for the minimum meaningful FC; power curve provided |
| "Where did dispersion come from?" | estimated from pilot (DESeq2); literature value used only as a cross-check |
| "Is n=3 enough?" | no; sized to >=6 per Schurch 2016 for realistic effects |
| "Why so many donors for scRNA-seq?" | population DE power scales with donors, not cells (Squair 2021) |
| "Technical replicates?" | collapsed to biological units; they add no biological degrees of freedom |

## References

- Bi R, Liu P. 2016. Sample size calculation while controlling false discovery rate for differential expression analysis with RNA-sequencing experiments. *BMC Bioinformatics* 17:146.
- Schurch NJ, Schofield P, Gierliński M, et al. 2016. How many biological replicates are needed in an RNA-seq experiment and which differential expression tool should you use? *RNA* 22:839-851.
- Blainey P, Krzywinski M, Altman N. 2014. Points of significance: replication. *Nat Methods* 11:879-880.
- Liu Y, Zhou J, White KP. 2014. RNA-seq differential expression studies: more sequence or more replication? *Bioinformatics* 30:301-304.
- Squair JW, Gautier M, Kathe C, et al. 2021. Confronting false discoveries in single-cell differential expression. *Nat Commun* 12:5692.
- Murphy AE, Skene NG. 2022. A balanced measure shows superior performance of pseudobulk methods in single-cell RNA-sequencing analysis. *Nat Commun* 13:7851.
- Wu H, Wang C, Wu Z. 2015. PROPER: comprehensive power evaluation for differential expression using RNA-seq. *Bioinformatics* 31:233-241.
- Vieth B, Ziegenhain C, Parekh S, Enard W, Hellmann I. 2017. powsimR: power analysis for bulk and single cell RNA-seq experiments. *Bioinformatics* 33:3486-3488.

## Related Skills

- power-analysis - The power-given-n direction and simulation-based power
- randomization-blocking - The experimental unit defines what is counted as a replicate
- batch-design - Balanced designs assume equal n per group
- differential-expression/deseq2-basics - Estimating pilot dispersions for the sample-size model
- single-cell/preprocessing - Pseudobulk aggregation underlying scRNA-seq cohort sizing
- clinical-biostatistics/power-and-sample-size - Sample size for regulated clinical trials
<!-- END FILE: experimental-design/sample-size/SKILL.md -->

<!-- END CATEGORY: experimental-design -->

