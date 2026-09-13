---
slug: bio-flow-cytometry-integrated
version: 1.0.1
displayName: "流式细胞术 / Flow cytometry"
name: bio-flow-cytometry-integrated
summary: "中文：流式细胞术综合技能，整合 8 个相关专题，覆盖流式细胞术：FCS处理、补偿/光谱解混、分门分析、聚类表型、差异分析。 English: Integrated Flow cytometry skill covering 8 related topics, including Flow cytometry: FCS handling, compensation/spectral unmixing, gating analysis, clustering phenotyping, differential abundance."
description: "中文：这是一个面向流式细胞术的综合生物信息学 Skill，整合当前分类下 8 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：流式细胞术：FCS处理、补偿/光谱解混、分门分析、聚类表型、差异分析。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：CATALYST, diffcyt, flowAI。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Flow cytometry, combining 8 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Flow cytometry: FCS handling, compensation/spectral unmixing, gating analysis, clustering phenotyping, differential abundance. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: CATALYST, diffcyt, flowAI. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# flow-cytometry 分类 Skill 整合版

> 本文件整合同一主分类目录下 8 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: flow-cytometry -->

## 子目录：flow-cytometry/bead-normalization

<!-- BEGIN FILE: flow-cytometry/bead-normalization/SKILL.md -->
---
name: bio-flow-cytometry-bead-normalization
description: Bead-based signal normalization and cross-batch harmonization for CyTOF and high-parameter cytometry - EQ four-element bead normalization of instrument sensitivity drift (CATALYST normCytof, premessa), and reference-anchor cross-batch normalization (CytoNorm, per-cluster quantile splines). Covers the distinction between within-run drift correction and between-batch correction, the mandatory anchor/reference sample, why normalization is per-cluster with many quantiles, and the over-correction risk. Use when correcting CyTOF signal drift, harmonizing multi-batch or multi-site studies, or deciding whether to normalize data versus model batch in the design.
tool_type: r
primary_tool: CATALYST
---

## Version Compatibility

Reference examples tested with: CATALYST 1.26+, CytoNorm 2.0+, flowCore 2.14+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

`normCytof()` returns a LIST (`$data`, `$beads`, `$removed`, ...), not a flowFrame; `beads="dvs"` encodes EQ masses 140,151,153,165,175. Confirm with `?normCytof` before relying on slot names.

# Bead Normalization

**"Normalize my CyTOF data"** -> Correct instrument sensitivity drift with EQ beads (within/across runs), then harmonize batches with a reference anchor.
- R (drift): `CATALYST::normCytof()` (EQ-bead-based) or `premessa`
- R (batch): `CytoNorm::CytoNorm.train()` + `CytoNorm.normalize()` (per-cluster quantile splines)

## The Single Most Important Modern Insight -- Two Different Layers; Anchor Controls Are the Guarantee

Bead normalization and batch normalization correct DIFFERENT things and are NOT interchangeable. (1) EQ-BEAD normalization (Finck 2013 *Cytometry A* 83:483) corrects within-run and run-to-run instrument SENSITIVITY DRIFT using the four-element beads as a physical internal standard - applied first, on raw counts. (2) CROSS-BATCH normalization (CytoNorm, Van Gassen 2020 *Cytometry A* 97:268) corrects staining/acquisition batch effects using a shared ANCHOR/reference sample present in EVERY batch, learning per-FlowSOM-cluster quantile-spline transforms. Beads cannot fix staining-batch or reagent-lot effects; CytoNorm cannot fix intra-run detector drift. The anchor control is the load-bearing design element: because it is biologically identical across batches, any cross-batch difference in it is technical BY CONSTRUCTION. Dropping the anchor (CytoNorm 2.0) is convenient but reintroduces the over-correction risk the anchor was designed to eliminate - so the safest stance for inference is to MODEL batch in the diffcyt design and reserve normalization for visualization/clustering display.

## Why Per-Cluster and Many (99) Quantiles

Batch effects are cell-type-specific - a marker can drift in monocytes but not in T cells - so a single global channel transform over-corrects one population while under-correcting another and can erase real abundance differences. CytoNorm therefore learns the transform PER FlowSOM cluster. And it uses ~99 quantiles + a spline because the drift is non-linear and intensity-dependent (the negative and positive peaks move by different amounts); a single median shift or linear rescale reintroduces the distortion it is trying to remove.

## EQ-Bead Normalization (drift)

**Goal:** Correct sensitivity drift and remove bead events.

**Approach:** `normCytof()` gates beads, computes the correction on the linear scale, and returns a list - the cleaned SCE is in `$data`.

```r
library(CATALYST)

sce <- prepData(fs, panel, md)                         # no by_time arg - normalization is normCytof's job
res <- normCytof(sce, beads = 'dvs',                   # EQ masses 140,151,153,165,175
                 k = 500, remove_beads = TRUE, overwrite = FALSE)   # k = smoothing window (default; affects bead-trace viz, not correction magnitude)
sce_norm <- res$data                                   # normalized SCE; res$beads / res$removed available
```

## Cross-Batch Normalization (CytoNorm)

**Goal:** Harmonize batches using a shared reference sample.

**Approach:** Train on the anchor (present in every batch) -> learn per-cluster quantile splines -> apply to the real samples. `testCV()` first: if cluster CV is high, the FlowSOM model is batch-unstable and per-cluster splines will distort (fall back to `nClus=1`).

```r
library(CytoNorm)

model <- CytoNorm.train(files = ref_files, labels = batch_labels, channels = marker_channels,
                        transformList = tl,
                        FlowSOM.params = list(nCells = 6000, xdim = 10, ydim = 10, nClus = 10),
                        normMethod.train = QuantileNorm.train,
                        normParams = list(nQ = 99), seed = 42)
CytoNorm.normalize(model = model, files = sample_files, labels = batch_labels,
                   transformList = tl, transformList.reverse = tl_rev,   # BOTH required
                   outputDir = 'normalized/')
```

## Per-Method Failure Modes

### Treating bead and batch normalization as the same
**Trigger:** expecting beads to fix staining-batch effects. **Mechanism:** different layers. **Symptom:** residual batch structure after bead norm. **Fix:** bead norm for drift; CytoNorm for batch.

### No anchor in a batch
**Trigger:** a batch lacking the reference sample. **Mechanism:** nothing biologically-identical to learn from. **Symptom:** that batch can't be normalized / is over-corrected. **Fix:** run the anchor in every batch (or model batch instead).

### Over-correction
**Trigger:** CytoNorm with groups confounded with batch, or anchor-free on variable samples. **Mechanism:** splines absorb real biology. **Symptom:** attenuated group differences. **Fix:** `testCV()` check; model batch in diffcyt for inference; normalize for display only.

### Using normCytof return as a flowFrame
**Trigger:** `sce_norm <- normCytof(...)`. **Mechanism:** it returns a list. **Symptom:** downstream type error. **Fix:** `res$data`.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| bead drift reduced ~4.9x -> 1.3x | Finck 2013 *Cytometry A* 83:483 | EQ-bead correction over a month of runs |
| 99 quantiles, per-cluster | Van Gassen 2020 *Cytometry A* 97:268 | non-linear intensity-dependent, cell-type-specific drift |
| EQ masses 140,151,153,165,175 (`dvs`) | CATALYST | DVS/Fluidigm EQ four-element bead set |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `normCytof` output not usable | it returns a list | use `res$data` |
| `prepData(by_time=TRUE)` errors | no such argument | use `normCytof()` for bead/drift correction |
| CytoNorm distorts populations | unstable FlowSOM clustering | run `testCV()`; reduce `nClus` (or 1) |
| batch effect remains | only bead-normalized | add CytoNorm with anchor samples |

## References

- Finck 2013 *Cytometry A* 83(5):483-494 — EQ-bead normalization of CyTOF drift.
- Van Gassen 2020 *Cytometry A* 97(3):268-278 — CytoNorm per-cluster quantile normalization.
- Quintelier 2025 *Cytometry A* 107(2):69-87 — CytoNorm 2.0 (anchor-free; over-correction caveat).
- Chevrier 2018 *Cell Syst* 6(5):612-620 — CyTOF spillover (CATALYST normalization context).

## Related Skills

Workflow order (CyTOF): EQ-bead drift normalization (raw counts, FIRST) -> cytometry-qc -> doublet-detection -> clustering -> CytoNorm cross-batch (LAST). The two normalization layers sit at opposite ends.

- cytometry-qc - EQ-bead-median-vs-Time is the primary CyTOF drift readout
- doublet-detection - Remove doublets before normalization
- compensation-transformation - Transform scale used by CytoNorm
- clustering-phenotyping - Cluster across normalized batches
- differential-analysis - Model batch in the design rather than over-cleaning
- experimental-design/batch-design - Anchor/reference-sample design; differential-expression/batch-correction for execution
<!-- END FILE: flow-cytometry/bead-normalization/SKILL.md -->

## 子目录：flow-cytometry/clustering-phenotyping

<!-- BEGIN FILE: flow-cytometry/clustering-phenotyping/SKILL.md -->
---
name: bio-flow-cytometry-clustering-phenotyping
description: Unsupervised clustering and cell-type identification for high-dimensional flow, spectral, and mass cytometry - FlowSOM, PhenoGraph, FlowSOM-via-CATALYST, with UMAP/tSNE for visualization. Covers the type-vs-state marker distinction (cluster on lineage, test state within clusters), over-provision-then-metacluster, the Weber-Robinson benchmark, seed dependence and metacluster stability, why embeddings are for looking not measuring, and median-heatmap annotation/merging. Use when discovering populations without predefined gates, choosing a clustering algorithm, selecting the number of metaclusters, or annotating clusters into cell types.
tool_type: r
primary_tool: CATALYST
---

## Version Compatibility

Reference examples tested with: CATALYST 1.26+, FlowSOM 2.10+, flowCore 2.14+; Rphenograph (GitHub: JinmiaoChenLab/Rphenograph).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

`Rphenograph` is GitHub-only (`remotes::install_github('JinmiaoChenLab/Rphenograph')`) and returns a list - membership is `igraph::membership(out[[2]])`, not a vector. Adapt rather than retrying.

# Clustering and Phenotyping

**"Cluster my cytometry data to find cell types"** -> Discover populations in high-dimensional data without gates, then annotate them by marker expression.
- R: `CATALYST::cluster()` (wraps FlowSOM + ConsensusClusterPlus) - the field default
- R: `FlowSOM::FlowSOM()` directly, or `Rphenograph()` for graph-based clustering

## The Single Most Important Modern Insight -- Cluster on Type Markers; the Embedding Is for Looking, Not Measuring

Two rules carry most of the correctness here. First, the type-vs-state distinction: LINEAGE/type markers (CD3, CD4, CD8, CD19) DEFINE clusters; functional/STATE markers (phospho-epitopes, cytokines, Ki-67, activation markers) must be WITHHELD from clustering and tested within clusters instead (the DA/DS framework, Nowicka 2017 *F1000Res* 6:748). Clustering on state markers splits "activated CD4" from "resting CD4" and confounds abundance with activation - a classic, silent design error. Second, t-SNE/UMAP embeddings do NOT preserve inter-cluster distances, cluster sizes, or densities (the apparent "UMAP preserves global structure" edge over tSNE is largely an initialization artifact - Kobak & Linderman 2021 *Nat Biotechnol* 39:156). Define populations by clustering in the HIGH-DIMENSIONAL space and COLOR the embedding by cluster; never gate on the embedding or read biology off blob distances.

## Algorithm Taxonomy

| Algorithm | Citation | Mechanism | Speed | Rare-pop | Determinism |
|-----------|----------|-----------|-------|----------|-------------|
| FlowSOM | Van Gassen 2015 *Cytometry A* 87:636 | SOM grid -> MST (viz) -> consensus metaclustering | fastest | good if grid over-provisioned | stochastic; seed-controllable |
| PhenoGraph | Levine 2015 *Cell* 162:184 | kNN graph (Jaccard) + Louvain | moderate | strong (no preset k) | seed-fragile (>40% reassignment reported) |
| X-shift | Samusik 2016 *Nat Methods* 13:493 | weighted kNN density + auto cluster # | slow | excellent | more deterministic |
| flowMeans | Aghaeepour 2011 *Cytometry A* 79:6 | k-means multi-cluster + change-point k | fast | moderate | stochastic |

Benchmark: Weber & Robinson 2016 *Cytometry A* 89:1084 tested 18 methods - FlowSOM (with metaclustering) was a top performer AND by far fastest, hence the field default; but its accuracy depends on supplying the right number of metaclusters.

## Why Over-Provision the Grid, Then Metacluster

Set the SOM grid (e.g. 10x10 = 100 nodes) MUCH larger than the number of populations expected, then metacluster down. The asymmetry: metaclustering can MERGE over-fine nodes into a real population, but can NEVER SPLIT a node that erroneously fused two cell types. Too coarse commits the unrecoverable error; too fine commits only the recoverable one. So over-cluster, then merge by hand off the median heatmap.

## CATALYST Clustering Pipeline

**Goal:** Cluster on type markers and prepare for annotation.

**Approach:** `prepData` builds the SCE (panel `marker_class` flags type vs state); `cluster()` wraps FlowSOM+ConsensusClusterPlus. Defaults `xdim=ydim=10`, `maxK=20` (the metacluster cap people forget); set `seed` on the function.

```r
library(CATALYST)

sce <- prepData(fs, panel, md, transform = TRUE, cofactor = 5)   # cofactor 5 = CyTOF; ~150 for fluorescence
sce <- cluster(sce, features = 'type',                            # type markers only
               xdim = 10, ydim = 10, maxK = 20, seed = 42)        # maxK caps metaclusters at 20 by default
plotExprHeatmap(sce, features = 'type', by = 'cluster_id', k = 'meta20', scale = 'last')
```

## PhenoGraph (graph-based alternative)

**Goal:** Cluster with a kNN graph when a data-driven cluster count is wanted.

**Approach:** `Rphenograph` on the type-marker matrix (cells x markers); extract membership from the list.

```r
library(Rphenograph)
type_expr <- t(assay(sce, 'exprs')[rowData(sce)$marker_class == 'type', ])
out <- Rphenograph(type_expr, k = 30)                  # only knob: k (neighbors)
sce$phenograph <- factor(igraph::membership(out[[2]]))  # list -> membership, not a vector
```

## Dimensionality Reduction (visualization only) and Annotation

**Goal:** Visualize structure and assign cell-type labels.

**Approach:** `runDR` subsamples per sample (`cells=`); color by cluster, never gate on it. Annotate from the median heatmap, then `mergeClusters` with a curated table.

```r
sce <- runDR(sce, dr = 'UMAP', features = 'type', cells = 2000)   # subsampled embedding
plotDR(sce, 'UMAP', color_by = 'meta20')

merging <- data.frame(old_cluster = 1:20,
                      new_cluster = c('CD4 T','CD4 T','CD8 T', '...'))   # curated from the heatmap
sce <- mergeClusters(sce, k = 'meta20', table = merging, id = 'annotated')
```

## Per-Method Failure Modes

### Clustering on state markers
**Trigger:** activation/phospho markers in the clustering feature set. **Mechanism:** state contaminates lineage identity. **Symptom:** "activated" and "resting" versions of a type split as separate clusters. **Fix:** cluster on `type` only; test state markers within clusters (differential-analysis).

### Seed-dependent "novel populations"
**Trigger:** a population that appears at one seed and vanishes at another. **Mechanism:** FlowSOM init / Louvain are stochastic. **Symptom:** non-reproducible clusters. **Fix:** set + report the seed; check multi-seed stability; treat unstable clusters as hypotheses.

### Reading biology off the embedding
**Trigger:** "cluster A is closer to B than C." **Mechanism:** UMAP/tSNE distances are non-metric. **Symptom:** false developmental/relatedness claims. **Fix:** quantify in marker space; embedding for display only.

### Clustering uncompensated/untransformed data
**Trigger:** raw linear input to FlowSOM. **Mechanism:** spillover + scale dominate Euclidean distance. **Symptom:** clusters track intensity, not biology. **Fix:** compensate + transform first.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| over-provision grid (10x10) >> expected pops | Van Gassen 2015 | metacluster can merge, never split |
| maxK = 20 default | CATALYST | metacluster cap; raise if expecting more |
| FlowSOM needs correct K | Weber & Robinson 2016 | accuracy depends on metacluster number |
| use median (not mean) per cluster | Bendall 2011 *Science* 332:687 | robust to doublet/spillover contamination |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| clustering uses scatter/Time/state | `features` not restricted | `features='type'` / `colsToUse=` lineage markers |
| Rphenograph result unusable | it returns a list | `igraph::membership(out[[2]])` |
| `set.seed` doesn't make FlowSOM reproducible | internal reseeding | pass `seed=` to `cluster()` |
| only 20 clusters no matter what | `maxK` default | raise `maxK` |

## References

- Van Gassen 2015 *Cytometry A* 87(7):636-645 — FlowSOM.
- Levine 2015 *Cell* 162(1):184-197 — PhenoGraph.
- Samusik 2016 *Nat Methods* 13(6):493-496 — X-shift.
- Weber & Robinson 2016 *Cytometry A* 89(12):1084-1096 — clustering benchmark (FlowSOM top + fastest).
- Nowicka 2017 *F1000Research* 6:748 — CyTOF workflow; type-vs-state markers.
- Kobak & Linderman 2021 *Nat Biotechnol* 39:156-157 — embedding initialization artifact.
- Bendall 2011 *Science* 332(6030):687-696 — arcsinh-median analysis of CyTOF data.

## Related Skills

- compensation-transformation - Compensate/transform before clustering
- gating-analysis - Supervised alternative; needed for rare populations
- differential-analysis - Test abundance/state of clusters between conditions
- cytometry-qc - Cluster only QC-passed events
- single-cell/clustering - Leiden/Louvain on scRNA-seq (shared graph-clustering ideas)
- imaging-mass-cytometry/phenotyping - Same CATALYST/FlowSOM conventions for imaging
<!-- END FILE: flow-cytometry/clustering-phenotyping/SKILL.md -->

## 子目录：flow-cytometry/compensation-transformation

<!-- BEGIN FILE: flow-cytometry/compensation-transformation/SKILL.md -->
---
name: bio-flow-cytometry-compensation-transformation
description: Corrects fluorophore spillover (conventional compensation) or spectral overlap (spectral unmixing) and applies variance-stabilizing transforms (logicle/biexponential, arcsinh, log) for flow and mass cytometry. Covers spillover-matrix estimation from single-stain controls, AutoSpill, the spillover spreading matrix and why panel design (not compensation) bounds resolution, compensate-then-transform ordering, and arcsinh cofactor choice (5 for CyTOF, ~150 for fluorescence, per-channel via flowVS). Use when correcting spectral overlap, preparing data for gating/clustering, choosing logicle vs arcsinh, deciding a cofactor, or distinguishing compensation from spectral unmixing.
tool_type: r
primary_tool: flowCore
---

## Version Compatibility

Reference examples tested with: flowCore 2.14+, flowStats 4.14+, flowWorkspace 4.14+, CATALYST 1.26+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

Notes that bite: `estimateLogicle()` lives in flowWorkspace (not flowCore). `flowCore::spillover()` on a flowFrame returns a LIST of keyword matrices (index `[[1]]`); `flowStats::spillover()` on single-stain controls returns the matrix DIRECTLY (not a list) - do not index it with `$`.

If code throws an error, introspect the installed package and adapt rather than retrying.

# Compensation and Transformation

**"Compensate and transform my cytometry data"** -> Remove spillover (matrix subtraction, conventional) or unmix the full spectrum (least squares, spectral), then apply a transform so populations separate.
- R (conventional): `flowCore::compensate()` then `flowWorkspace::estimateLogicle()` + `flowCore::transform()`
- R (CyTOF/mass): `CATALYST::prepData(..., transform=TRUE, cofactor=5)` (arcsinh)
- R (spectral): linear UNMIXING, not compensation - see the taxonomy

## The Single Most Important Modern Insight -- Compensation Corrects the Mean; It Cannot Remove Spreading Error

Conventional compensation inverts a square spillover matrix (peak-channel subtraction); spectral cytometry solves an OVERDETERMINED least-squares unmix over all detectors, with autofluorescence modeled as an extra "fluorophore." Both correct the population MEAN. Neither removes **spreading error** - the widening of a negative population in a spillover detector that arises from the Poisson counting statistics of the spilled-in photons (Roederer 2001 *Cytometry* 45:194; Nguyen 2013 *Cytometry A* 83:306). Compensation does not INTRODUCE spreading; it makes the pre-existing variance visible by re-centering means. The corollaries are load-bearing: (1) a smeared negative cannot be fixed by tuning the matrix - over-compensating to flatten it is data falsification; (2) spreading is fixed at PANEL DESIGN (the Spillover Spreading Matrix identifies which detector pairs to avoid for co-expressed/dim markers), never downstream; (3) calling spectral unmixing "compensation" is a category error - it is a different, overdetermined model.

## Method Taxonomy

| Method | What it does | When to use | Fails when |
|--------|--------------|-------------|------------|
| Acquisition-recorded `$SPILLOVER` | applies the cytometer-computed matrix | trustworthy single-stain setup at acquisition | controls were wrong/missing |
| Computed compensation (`flowStats::spillover`) | estimates spillover from single-stain controls (medians) | conventional flow, controls available | poor/dim/contaminated controls |
| AutoSpill (Roca 2021 *Nat Commun* 12:2890) | robust-regression matrix + iterative refinement; AF as endogenous dye | high-parameter panels; messy controls | reference implementation/setup unavailable |
| Spectral unmixing (OLS/WLS/Poisson) | least-squares unmix full spectrum vs reference spectra + AF | spectral cytometers (Aurora, ID7000) | wrong/heterogeneous AF; collinear spectra |
| Logicle / biexponential | display + analysis transform, handles negatives | fluorescence flow | wrong `w` clips the negative population |
| arcsinh | variance-stabilizing transform | CyTOF/mass; computational pipelines | wrong cofactor compresses dim markers |
| log10 | legacy | rarely; strictly positive data | any negative values after compensation |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Conventional flow, `$SPILLOVER` present | apply recorded matrix -> estimateLogicle | trust acquisition controls; logicle handles negatives |
| Conventional flow, no matrix | compute via `flowStats::spillover` from single-stains (or AutoSpill) | controls drive the matrix; AutoSpill for >12 colors |
| Spectral cytometer | UNMIX (do NOT compensate), then arcsinh at ~150/per-channel (NOT 5) | overdetermined system; spectral data is fluorescence-scale, not ion counts |
| CyTOF / mass | arcsinh cofactor 5; spillover via CATALYST `compCytof` if needed | metals barely spill (~1-4%), but oxide/impurity is real |
| Dim marker driving a borderline call | test per-channel cofactor (flowVS) | a fixed cofactor can manufacture/erase the population |

## Compensate-Then-Transform Ordering (load-bearing)

Compensation/unmixing is LINEAR and must run on untransformed data; applying it after a nonlinear transform is mathematically invalid. `estimateLogicle()` must run on ALREADY-COMPENSATED data so the `w`/`a` parameters reflect the post-compensation negative spread. Negative values after compensation are expected and meaningful - do NOT clip to zero before transforming (handling negatives is the entire reason logicle/arcsinh exist; log cannot).

## Apply or Compute Compensation

**Goal:** Apply the recorded matrix, or estimate one from single-stain controls.

**Approach:** `compensate()` takes a `compensation` object built from the matrix; `flowStats::spillover()` estimates from single-stain controls and returns the matrix directly.

```r
library(flowCore)

comp <- compensation(spillover(fcs)[[1]])      # flowCore: flowFrame -> list of keyword matrices
fcs_comp <- compensate(fcs, comp)

library(flowStats)
ctrls <- read.flowSet(list.files('controls', pattern = '\\.fcs$', full.names = TRUE))
comp_matrix <- spillover(ctrls, unstained = 'Unstained.fcs', fsc = 'FSC-A', ssc = 'SSC-A',
                         patt = '-A$', method = 'median')   # flowStats: returns the matrix directly
```

## Logicle / Biexponential Transform (fluorescence)

**Goal:** Display and analyze compensated fluorescence with negatives handled honestly.

**Approach:** `estimateLogicle()` (flowWorkspace) derives `w` from the data's most-negative events; apply with `transform()`.

```r
library(flowWorkspace)

fluo <- colnames(fcs_comp)[grepl('-A$', colnames(fcs_comp)) & !grepl('FSC|SSC', colnames(fcs_comp))]
lgcl <- estimateLogicle(fcs_comp, channels = fluo)   # data-driven w; t=262144, m=4.5, a=0 defaults
fcs_t <- transform(fcs_comp, lgcl)
```

## Arcsinh Transform (CyTOF cofactor 5; fluorescence/spectral ~150 or per-channel)

**Goal:** Variance-stabilize mass-cytometry counts (or any pipeline feeding clustering).

**Approach:** `asinh(x/cofactor)`; flowCore's `arcsinhTransform` is `asinh(a + b*x) + c`, so set `b=1/cofactor`. CATALYST `prepData` defaults cofactor=5.

```r
COFACTOR <- 5      # standard CyTOF cofactor, codified in the CATALYST workflow (Nowicka 2017); ~150 for fluorescence

asinhT <- arcsinhTransform(transformationId = 'asinh', a = 0, b = 1/COFACTOR, c = 0)
fcs_t  <- transform(fcs, transformList(marker_channels, asinhT))

# CATALYST path (CyTOF): cofactor=5 default; OVERRIDE for fluorescence/spectral
sce <- CATALYST::prepData(fs, panel, md, transform = TRUE, cofactor = COFACTOR)
```

## Per-Method Failure Modes

### Over-compensation (negative pull-down)
**Trigger:** matrix slope over-estimated from dim controls. **Mechanism:** subtraction overshoots. **Symptom:** negative population pulled below zero, "comma" shape. **Fix:** controls at least as bright as the sample; AutoSpill regression; never hand-tune to flatten spread.

### Wrong logicle width clips negatives
**Trigger:** fixed `w` instead of `estimateLogicle`. **Mechanism:** linear region too narrow. **Symptom:** negative population piled on the axis. **Fix:** estimate `w` on compensated data.

### Cofactor compresses a dim marker
**Trigger:** cofactor 5 on fluorescence (or 150 on CyTOF). **Mechanism:** linear region mismatched to the noise band. **Symptom:** dim-positive collapses into the negative; clusters don't reproduce. **Fix:** 5 for CyTOF, ~150 for fluorescence; per-channel via `flowVS::estParamFlowVS`.

### Compensating spectral data
**Trigger:** treating Aurora data as conventional. **Mechanism:** subtraction is the wrong model for an overdetermined system. **Symptom:** residual spread, false positives. **Fix:** unmix against single-stain reference spectra + unstained AF.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| arcsinh cofactor = 5 (mass) | Nowicka 2017 *F1000Res* 6:748 (CATALYST workflow) | matches CyTOF ion-count near-zero noise band |
| arcsinh cofactor ~150 (fluorescence) | community/CATALYST convention (not a derived optimum) | PMT photon scale is far larger; per-channel flowVS supersedes |
| comp control >= sample brightness | Roederer 2001 *Cytometry* 45:194 | slope estimated over the widest lever arm; extrapolation amplifies error |
| spreading is intensity-dependent (~sqrt of signal) | Nguyen 2013 *Cytometry A* 83:306 | SSM is normalized to be gain-independent for panel design |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `compensate()` channel mismatch | matrix colnames != FCS channels | align names before compensate |
| all-negative after transform | transform applied before/without compensation | compensate on linear data first |
| `estimateLogicle` not found | called from flowCore | it lives in flowWorkspace |
| `arcsinhTransform` ignores "cofactor" | param is `b`, not `cofactor` | set `b = 1/cofactor` |

## References

- Roederer 2001 *Cytometry* 45(3):194-205 — spreading error / compensation artifacts.
- Nguyen 2013 *Cytometry A* 83(3):306-315 — spillover spreading matrix; panel design.
- Roca 2021 *Nat Commun* 12:2890 — AutoSpill robust-regression compensation.
- Parks 2006 *Cytometry A* 69(6):541-551 — logicle display.
- Moore & Parks 2012 *Cytometry A* 81(4):273-277 — logicle operational update.
- Bendall 2011 *Science* 332(6030):687-696 — CyTOF mass cytometry; arcsinh-median analysis.
- Nowicka 2017 *F1000Research* 6:748 — CATALYST workflow; codifies the cofactor-5 convention.
- Azad 2016 *BMC Bioinformatics* 17:291 — flowVS per-channel cofactor.
- Chevrier 2018 *Cell Syst* 6(5):612-620 — CyTOF spillover compensation (CATALYST).

## Related Skills

- fcs-handling - Load FCS and retrieve the spillover keyword first
- gating-analysis - Gate on the transformed, compensated scale
- clustering-phenotyping - Cluster compensated, transformed data
- cytometry-qc - QC before and after preprocessing
- imaging-mass-cytometry/data-preprocessing - Shared arcsinh/metal-channel conventions
- spatial-transcriptomics/spatial-proteomics - Spectral/metal unmixing context
<!-- END FILE: flow-cytometry/compensation-transformation/SKILL.md -->

## 子目录：flow-cytometry/cytometry-qc

<!-- BEGIN FILE: flow-cytometry/cytometry-qc/SKILL.md -->
---
name: bio-flow-cytometry-cytometry-qc
description: Quality control for flow, spectral, and mass cytometry - time-based anomaly cleaning (flowAI, flowCut, PeacoQC, flowClean), margin/boundary event removal, signal-drift detection, dead-cell exclusion, CyTOF Gaussian/DNA/event-length checks, instrument calibration/standardization (MESF, CS&T, peak-2), and batch-level outlier flagging. Use when assessing acquisition quality, choosing a cleaning tool, ordering QC relative to compensation, deciding margin removal before density-based steps, or flagging problematic samples before clustering or differential analysis.
tool_type: r
primary_tool: flowAI
---

## Version Compatibility

Reference examples tested with: flowAI 1.32+, PeacoQC 1.12+, flowCore 2.14+, flowDensity 1.36+, CATALYST 1.26+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

Counterintuitive defaults to confirm: flowAI checks are FR/FS/FM (FM = dynamic range, not "flow"); PeacoQC `MAD`/`IT_limit` are LESS strict when HIGHER. Verify with `?flow_auto_qc` and `?PeacoQC` before tuning.

# Cytometry QC

**"Run quality control on my cytometry data"** -> Detect and remove acquisition artifacts (flow-rate instability, signal drift, margin events, dead cells, CyTOF doublets) on the Time axis, then flag outlier samples.
- R (flow/spectral): `flowAI::flow_auto_qc()`, `PeacoQC::PeacoQC()` (+ `RemoveMargins()`)
- R (mass): `CATALYST::normCytof()` beads + Gaussian/DNA/event-length gating

## The Single Most Important Modern Insight -- The Time Parameter Is the Master QC Axis, and Order Matters

Nearly every acquisition artifact - clogs, bubbles, flow-rate surges, electronics warm-up, CyTOF sensitivity decay, oxide buildup - manifests as a CHANGE IN SIGNAL versus the Time channel. flowAI, flowCut, flowClean, and PeacoQC are all, at heart, Time-vs-signal anomaly detectors; a missing or mis-scaled `$TIMESTEP` silently degrades or breaks all of them. Just as important is the ORDER: compensation/unmixing -> transform -> margin removal -> time-based QC -> debris/doublet/dead-cell gating -> batch normalization. Margin (boundary) events piled at a detector min/max form spurious high-density ridges that fool density-based cleaning and density gates, so they must be stripped BEFORE any density step; and time-based QC on untransformed data misbehaves because the density structure the algorithms rely on lives on the transformed scale.

## Cleaning-Tool Taxonomy

| Tool | Citation | Mechanism | When to use / caveat |
|------|----------|-----------|----------------------|
| flowAI | Monaco 2016 *Bioinformatics* 32:2473 | 3 checks: flow rate (FR), signal acquisition (FS), dynamic range (FM) | classic; known AGGRESSIVE - can remove normal data |
| PeacoQC | Emmaneel 2022 *Cytometry A* 101:325 | per-channel density peaks + MAD + isolation tree | only tool validated across flow + mass + spectral; QC engine of CytoPipeline |
| flowCut | Meskas 2023 *Cytometry A* 103:71 | segments Time, removes low-density/deviant segments | less aggressive than flowAI; flags whole files |
| flowClean | Fletez-Brant 2016 *Cytometry A* 89:461 | tracks subset frequency in centered-log-ratio space | floor ~30,000 events; writes a "GoodVsBad" parameter to gate on |

## Run flowAI (with the correct API)

**Goal:** Auto-clean a sample for flow-rate, signal-acquisition, and dynamic-range anomalies.

**Approach:** `flow_auto_qc()` returns a flowFrame of high-quality events when `output=1`; FM is the dynamic-range check; supply `timeCh` for concatenated/clock-reset files. flowAI is the time-based QC step - run it after compensation/transform/margin removal (per the ordering above), not on a raw uncompensated frame.

```r
library(flowAI)

ff_clean <- flow_auto_qc(ff,
                         remove_from = 'all',          # FR + FS + FM
                         output = 1,                    # 1 = HQ events only; 2 = add QC param; 3 = bad-event IDs
                         ChExcludeFS = c('FSC', 'SSC'), # scatter excluded from the signal check
                         second_fractionFR = 0.1,
                         folder_results = 'qc_output')
cat('kept', nrow(ff_clean), 'of', nrow(ff), 'events\n')
```

## Margins First, Then PeacoQC

**Goal:** Remove boundary events, then clean unstable time/peak structure across all channels.

**Approach:** `RemoveMargins()` strips detector-min/max events; then `PeacoQC()` - remember higher `MAD`/`IT_limit` = LESS strict.

```r
library(PeacoQC)

ff_nm <- RemoveMargins(ff, channels = c('FSC-A', 'SSC-A'))   # do this BEFORE density QC
res <- PeacoQC(ff_nm, channels = marker_channels,
               MAD = 6, IT_limit = 0.55,                     # defaults; higher = less strict (counterintuitive)
               save_fcs = FALSE, plot = TRUE)
ff_clean <- res$FinalFF
```

## Dead-Cell, Drift, and CyTOF Checks

**Goal:** Exclude dead cells, detect per-channel drift, and apply CyTOF-specific gates.

**Approach:** Viability dye threshold (bimodal); per-time-bin median slope for drift; for CyTOF use DNA intercalator + Gaussian/event-length; EQ-bead-median-vs-Time is the primary CyTOF drift readout (see bead-normalization).

```r
expr <- exprs(ff)
# dead cells take up more viability dye -> cut at the bimodal density VALLEY (data-driven), not a fixed quantile
dead_cut <- flowDensity::deGate(ff, channel = 'Live_Dead')
live <- expr[, 'Live_Dead'] < dead_cut

# CyTOF single-cell gates
if ('Event_length' %in% colnames(expr)) {
    keep <- expr[, 'Event_length'] >= 10 & expr[, 'Event_length'] <= 75   # confirm range per instrument
}
dna <- grep('Ir191|Ir193', colnames(expr), value = TRUE)             # intercalator-positive = nucleated
```

## Calibration and Standardization (cross-study comparability)

A discovery analyst often skips this, but cross-experiment/cross-site MFI comparison is meaningless without it (Maecker & Trotter 2006 *Cytometry A* 69:1037):
- **MESF / MEF / ERF** beads express intensity in molecules-of-equivalent-fluorochrome - comparable across instruments and time (NIST/ISAC standard; PE/Pacific Blue use ERF surrogates).
- **Quantibrite PE** (defined PE molecules/bead, ~1:1 conjugation) converts MFI to antibodies-bound-per-cell / receptor density (bead values are LOT-dependent).
- **CS&T / 8-peak rainbow beads** for daily QC (laser delay, area scaling, linearity).
- **Peak-2 / voltration**: run a dim particle across PMT voltages, pick the CV-vs-voltage inflection = minimum voltage for optimal resolution. This is why MIFlowCyt mandates reporting voltages.

## Batch-Level Outlier Flagging

**Goal:** Flag samples whose event count, flow stability, or marker medians deviate from the batch.

**Approach:** Per-file metrics + MAD-based bounds; track an anchor/reference sample if present.

```r
qc <- do.call(rbind, lapply(fcs_files, function(f) {
  ff <- read.FCS(f); e <- exprs(ff)
  data.frame(file = basename(f), events = nrow(ff),
             med_signal = median(apply(e, 2, median)))
}))
qc$outlier <- abs(qc$events - median(qc$events)) > 3 * mad(qc$events)
```

## Per-Method Failure Modes

### Density QC on un-margin-removed data
**Trigger:** PeacoQC/flowClean before `RemoveMargins`. **Mechanism:** axis pile-ups are false high-density ridges. **Symptom:** real events removed near the boundary, or margins kept. **Fix:** remove margins first.

### flowAI over-removal
**Trigger:** default flowAI on a low-rate or short acquisition. **Mechanism:** FR check flags normal slow segments. **Symptom:** large unexplained event loss. **Fix:** raise `second_fractionFR`; inspect the HTML report; consider flowCut/PeacoQC.

### QC on untransformed/uncompensated data
**Trigger:** running QC on raw linear values. **Mechanism:** high-intensity tail dominates density. **Symptom:** misplaced anomaly calls. **Fix:** compensate + transform first.

### Time axis missing/reset
**Trigger:** concatenated files, some sorters. **Mechanism:** no usable Time. **Symptom:** flow-rate check fails or is meaningless. **Fix:** `timeCh=` or reconstruct; otherwise skip time-based checks.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| flowClean floor ~30,000 events | Fletez-Brant 2016 *Cytometry A* 89:461 | below this the CLR frequency tracking under-detects |
| PeacoQC `MAD=6`, `IT_limit=0.55` | Emmaneel 2022 *Cytometry A* 101:325 | defaults; HIGHER = less strict |
| dead cells > ~10-30% | community | sample-handling flag, not a hard cutoff - report, don't auto-exclude the sample |
| CyTOF retune ~ daily / per long run | instrument practice (flagged) | sensitivity decays from cone fouling/plasma drift |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `flow_auto_qc` returns unexpected object | assuming `$fcs`/report list | `output=1` returns a flowFrame; set `output` explicitly |
| margins not removed by PeacoQC | expecting it built-in | call `RemoveMargins()` separately, first |
| tuning MAD up removes more | sign confusion | higher MAD/IT_limit = LESS strict |
| flowClean output unchanged | it appends a parameter | gate on the "GoodVsBad" column |

## References

- Monaco 2016 *Bioinformatics* 32(16):2473-2480 — flowAI.
- Emmaneel 2022 *Cytometry A* 101(4):325-338 — PeacoQC.
- Meskas 2023 *Cytometry A* 103(1):71-81 — flowCut.
- Fletez-Brant 2016 *Cytometry A* 89(5):461-471 — flowClean.
- Fienberg 2012 *Cytometry A* 81(6):467-475 — cisplatin viability reagent (CyTOF live/dead).
- Maecker & Trotter 2006 *Cytometry A* 69(9):1037-1042 — controls, instrument setup, peak-2.
- Lee 2008 *Cytometry A* 73(10):926-930 — MIFlowCyt reporting (voltages, clones, config).

## Related Skills

- compensation-transformation - Compensate/transform before time-based QC
- doublet-detection - Singlet discrimination after QC
- bead-normalization - EQ-bead drift correction for CyTOF (QC's normalization arm)
- clustering-phenotyping - Cluster only QC-passed events
- experimental-design/batch-design - Anchor/reference-sample design for batch QC
<!-- END FILE: flow-cytometry/cytometry-qc/SKILL.md -->

## 子目录：flow-cytometry/differential-analysis

<!-- BEGIN FILE: flow-cytometry/differential-analysis/SKILL.md -->
---
name: bio-flow-cytometry-differential-analysis
description: Differential abundance (DA) and differential state (DS) analysis for flow and mass cytometry - tests which cell populations change in frequency or marker expression between conditions using diffcyt (edgeR/voom/GLMM for DA, limma/LMM for DS), with cydar, CITRUS, and compositional methods (sccomp, scCODA, DCATS) as alternatives. Covers the sample-is-the-experimental-unit principle, design/contrast and mixed-model formulas, compositionality of cluster proportions, and FDR across clusters. Use when comparing populations between groups, choosing a DA method, handling paired/batch designs, or deciding whether compositional correction is needed.
tool_type: r
primary_tool: diffcyt
---

## Version Compatibility

Reference examples tested with: diffcyt 1.22+, CATALYST 1.26+, edgeR 4.0+, limma 3.58+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

`testDA_edgeR`/`testDS_limma` are diffcyt functions operating on count/median objects from `calcCounts`/`calcMedians`; the CATALYST-integrated path is the `diffcyt()` wrapper on the SCE. Confirm the signature with `?diffcyt` before relying on it.

# Differential Analysis

**"Compare cell populations between my conditions"** -> Test cluster frequencies (DA) and within-cluster marker expression (DS) between groups, with the sample (not the cell) as the unit.
- R: `diffcyt::diffcyt(sce, analysis_type='DA', method_DA='diffcyt-DA-edgeR', design, contrast)`
- R: `diffcyt(sce, analysis_type='DS', method_DS='diffcyt-DS-limma', ...)`

## The Single Most Important Modern Insight -- The Sample Is the Experimental Unit, Not the Cell

Tens of thousands of cells from one donor are technical PSEUDOREPLICATES, not independent observations. A per-cell test (Wilcoxon across all cells) treats them as n = cells and produces astronomically significant p-values from two mice - it is the single most common statistical sin in modern cytometry (Hurlbert 1984 *Ecol Monogr* 54:187; the cytometry mirror of the scRNA-seq pseudobulk lesson). The correct unit is the SAMPLE/subject: diffcyt aggregates cells to PER-SAMPLE-PER-CLUSTER counts (DA) and PER-SAMPLE-PER-CLUSTER arcsinh-MEDIANS (DS), then tests across samples with edgeR/limma/GLMM (Weber 2019 *Commun Biol* 2:183). Biological replication is mandatory (>= 2-3 per group); DA from a single sample per condition has no valid test. Paired with this: cluster proportions are COMPOSITIONAL (they sum to 1), so a real increase in one population mechanically forces apparent depletion in others - a source of false DA in "unchanged" clusters.

## DA vs DS, and the type/state marker link

- **DA** (differential abundance): does a cluster's FREQUENCY differ? Clusters are defined by TYPE markers.
- **DS** (differential state): within a fixed-identity cluster, does a STATE marker's expression differ? State markers were withheld from clustering for exactly this test.

## Method Taxonomy

| Method | Citation | Mechanism | When to use |
|--------|----------|-----------|-------------|
| diffcyt-DA-edgeR / voom | Weber 2019 *Commun Biol* 2:183 | edgeR/voom empirical-Bayes on per-sample counts; optional TMM | standard 2+ group with replicates (DEFAULT) |
| diffcyt-DA-GLMM / DS-LMM | Weber 2019 | random effects in the formula | paired/repeated-measures/nested (subject random effect) |
| cydar | Lun 2017 *Nat Methods* 14:707 | overlapping hyperspheres + edgeR + spatial FDR | continuum, avoid hard clusters |
| CITRUS | Bruggner 2014 *PNAS* 111:E2770 | hierarchical clustering + LASSO | predictive signature, LARGE n; correlated-not-causal; largely superseded |
| sccomp / scCODA / DCATS | Mangiola 2023 *PNAS* 120:e2203828120 / Buttner 2021 *Nat Commun* 12:6876 / Lin 2023 *Genome Biol* 24:151 | simplex-aware compositional models | strong compositional shift (one pop dominates); DCATS for assignment uncertainty |

## Run diffcyt DA and DS

**Goal:** Test abundance and state on a CATALYST-clustered SCE.

**Approach:** Build design + contrast from `ei(sce)`; the `diffcyt()` wrapper uses the stored clustering. State markers are tested in DS, type markers define DA clusters.

```r
library(CATALYST); library(diffcyt)

sce <- readRDS('sce_clustered.rds')
design   <- createDesignMatrix(ei(sce), cols_design = 'condition')
contrast <- createContrast(c(0, 1))                    # Treatment vs Control

res_DA <- diffcyt(sce, clustering_to_use = 'meta20',
                  analysis_type = 'DA', method_DA = 'diffcyt-DA-edgeR',
                  design = design, contrast = contrast)
res_DS <- diffcyt(sce, clustering_to_use = 'meta20',
                  analysis_type = 'DS', method_DS = 'diffcyt-DS-limma',
                  design = design, contrast = contrast)

library(SummarizedExperiment)
rowData(res_DA$res)        # cluster_id, logFC, p_val, p_adj (BH across clusters)
```

## Paired / Repeated-Measures (mixed models)

**Goal:** Account for within-subject correlation (e.g. pre/post on the same donor).

**Approach:** Use a GLMM/LMM method with a random effect for subject via a formula.

```r
formula <- createFormula(ei(sce), cols_fixed = 'condition', cols_random = 'patient_id')
res_DA  <- diffcyt(sce, clustering_to_use = 'meta20',
                   analysis_type = 'DA', method_DA = 'diffcyt-DA-GLMM',
                   formula = formula, contrast = createContrast(c(0, 1)))
```

## Compositional Re-Check

**Goal:** Confirm a headline single-population shift is not inducing artifactual reciprocal depletion.

**Approach:** Re-test with a simplex-aware model when one cluster changes a lot or total yield differs by group.

```r
# If a dominant population expands, the apparent depletion of others may be a simplex artifact.
# Re-test with sccomp / scCODA (reference cell type) / DCATS (assignment uncertainty)
# before reporting reciprocal depletion as independent biology.
```

## Per-Method Failure Modes

### Per-cell pseudoreplication
**Trigger:** Wilcoxon/t-test across all cells. **Mechanism:** cells aren't independent. **Symptom:** p ~ 1e-40 from few subjects. **Fix:** aggregate to per-sample summaries (diffcyt).

### Compositional false DA
**Trigger:** one population expands strongly. **Mechanism:** proportions sum to 1. **Symptom:** significant "depletion" of unrelated clusters. **Fix:** TMM only when total cell abundance is NOT itself the biological signal (else it removes real signal), or a compositional method (sccomp/scCODA/DCATS); report total-yield differences.

### Batch cleaned instead of modeled
**Trigger:** normalizing batch out then testing naively. **Mechanism:** over-correction removes real signal. **Symptom:** attenuated effects. **Fix:** include batch in the design; if batch == condition, no rescue - design it out.

### No replicates
**Trigger:** 1 sample per condition. **Mechanism:** no error term. **Symptom:** uninterpretable p. **Fix:** require >= 2-3 biological replicates per group.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| >= 2-3 biological replicates per group | Weber 2019 | minimum for a valid DA/DS error term |
| BH FDR across clusters (and clusters x markers for DS) | diffcyt | high-resolution grids have many tests |
| arcsinh median as DS statistic | Nowicka 2017 | robust per-cluster per-sample summary |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `testDA_edgeR(sce, ...)` fails | wrong signature | use the `diffcyt()` wrapper on the SCE, or `calcCounts` first |
| results empty | wrong `clustering_to_use` name | match the stored clustering id (e.g. `meta20`) |
| no DS results | state markers not flagged | set `marker_class='state'` in the panel |
| paired design ignored | used fixed-effect method | use `diffcyt-DA-GLMM` with a random effect |

## References

- Weber 2019 *Commun Biol* 2:183 — diffcyt (DA + DS).
- Bruggner 2014 *PNAS* 111(26):E2770-E2777 — CITRUS.
- Lun 2017 *Nat Methods* 14(7):707-709 — cydar hypersphere DA.
- Mangiola 2023 *PNAS* 120(33):e2203828120 — sccomp compositional analysis.
- Buttner 2021 *Nat Commun* 12:6876 — scCODA.
- Lin 2023 *Genome Biol* 24:151 — DCATS (assignment-uncertainty-aware).
- Nowicka 2017 *F1000Research* 6:748 — CyTOF workflow; arcsinh-median DS statistic.
- Hurlbert 1984 *Ecol Monogr* 54(2):187-211 — pseudoreplication.

## Related Skills

- clustering-phenotyping - Cluster (type markers) before testing
- gating-analysis - Compare manually gated population frequencies
- differential-expression/de-results - Shared edgeR/limma output semantics (padj)
- differential-expression/edger-basics - The count-model engine diffcyt reuses
- experimental-design/multiple-testing - FDR across clusters and clusters x markers
- experimental-design/batch-design - Model batch in the design, don't clean it out
<!-- END FILE: flow-cytometry/differential-analysis/SKILL.md -->

## 子目录：flow-cytometry/doublet-detection

<!-- BEGIN FILE: flow-cytometry/doublet-detection/SKILL.md -->
---
name: bio-flow-cytometry-doublet-detection
description: Detects and removes doublets/aggregates from flow, spectral, and mass cytometry before clustering or quantification. Covers FSC-A vs FSC-H singlet discrimination (the Area-Height non-proportionality, not a 1D area gate), FSC-W/SSC width gating, CyTOF Gaussian discrimination parameters (Center/Offset/Width/Residual/Event_length) and DNA intercalator gating, and the residual heterotypic conjugates that survive scatter gating and masquerade as double-positive populations. Use when filtering aggregates before phenotyping, choosing a doublet method for flow vs CyTOF, or diagnosing a suspicious double-positive cluster.
tool_type: r
primary_tool: flowCore
---

## Version Compatibility

Reference examples tested with: flowCore 2.14+, CATALYST 1.26+, ggplot2 3.5+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws an error, introspect the installed package and adapt rather than retrying.

# Doublet Detection

**"Remove doublets from my cytometry data"** -> Discriminate single cells from aggregates using pulse geometry (flow) or ion-cloud parameters (CyTOF), before any clustering or quantification.
- R (flow/spectral): `flowCore` gate on the FSC-A vs FSC-H diagonal (+ FSC-W/SSC-W)
- R (mass/CyTOF): gate on DNA intercalator + Gaussian/Event_length parameters

## The Single Most Important Modern Insight -- Doublets Are Caught by Area-vs-Height Non-Proportionality, and Scatter Gating Is Necessary but Not Sufficient

A doublet has roughly double the pulse AREA of a singlet but NOT double the Height, and a longer Width/transit time - so singlets fall on a tight FSC-A vs FSC-H diagonal and doublets deflect above it. A 1D area histogram therefore does NOT remove doublets; the discriminating signal is the Area-Height relationship (plus Width). This matters because an unremoved doublet of a CD3+ and a CD19+ cell reads as an artifactual CD3+CD19+ "double-positive," and clustering will faithfully (and wrongly) carve it out as a real population. Crucially, scatter gating is necessary but NOT sufficient: heterotypic conjugates (e.g. a CD3+CD14+ T:monocyte) survive standard FSC-A/H gates and present as genuine double-positives whose lineage-marker levels look COMPARABLE to true single-positives - the tell is an ELEVATED shared marker (e.g. CD45) and a high bright-field aspect ratio, so the definitive resolver is imaging flow cytometry, not a lineage-intensity check (Stadinski 2020 *Cytometry A* 97:1102). On CyTOF there is no scatter at all - doublets are removed by ion-cloud Gaussian parameters and DNA intercalator content (Bagwell 2020 *Cytometry A* 97:184).

## Method Taxonomy

| Method | Instrument | Principle | Caveat |
|--------|-----------|-----------|--------|
| FSC-A vs FSC-H | flow/spectral | singlets on the A-H diagonal | the standard; the discriminator is non-proportionality, not area |
| FSC-W / SSC-W | flow/spectral | doublets have longer pulse Width | complementary to A-vs-H |
| DNA intercalator (Ir191/193) | CyTOF | doublets show ~2N+ DNA | also separates cells from beads/debris |
| Gaussian params + Event_length | CyTOF | ion-cloud fit residual/length flags fusions | catches fusions DNA alone misses (Bagwell 2020) |
| imaging cytometry | imaging flow | bright-field aspect ratio | the only clean resolver of heterotypic conjugates |

Note: cytometry doublet removal is GATING-based. DoubletFinder/Scrublet/scDblFinder are scRNA-seq DROPLET methods (they simulate artificial doublets) - limited transfer, because cytometry has direct physical doublet signals.

## FSC-A vs FSC-H Singlet Gating (flow/spectral)

**Goal:** Keep events on the singlet diagonal.

**Approach:** A polygon along the A=H diagonal (preferred over a rectangle, which keeps off-diagonal doublets); visualize with the gate overlaid.

```r
library(flowCore); library(ggcyto)

# matrix dimnames preserve 'FSC-A'/'FSC-H'; data.frame() would mangle them to FSC.A
singlet <- polygonGate(filterId = 'singlets', .gate = matrix(
  c(20000, 10000, 250000, 200000, 250000, 260000, 20000, 40000), ncol = 2, byrow = TRUE,
  dimnames = list(NULL, c('FSC-A', 'FSC-H'))))
singlets <- Subset(fs, singlet)
autoplot(fs[[1]], 'FSC-A', 'FSC-H') + ggcyto::geom_gate(singlet)
```

## CyTOF Doublet Removal

**Goal:** Keep intercalator-positive single ion clouds.

**Approach:** Gate DNA intercalator (nucleated, ~2N) and Event_length/Gaussian residual; CATALYST exposes these as channels in the SCE.

```r
library(CATALYST)
# prepData moves Time/Event_length to int_colData by default - keep them in the assay with FACS=TRUE
sce <- prepData(fs, panel, md, transform = TRUE, cofactor = 5, FACS = TRUE)
e <- assay(sce, 'exprs')

dna <- e['DNA1', ]                                   # intercalator-positive = nucleated single cells
keep <- dna > quantile(dna, 0.05) & dna < quantile(dna, 0.95)
if ('Event_length' %in% rownames(sce))               # retained by FACS=TRUE (now on the arcsinh scale)
  keep <- keep & e['Event_length', ] <= quantile(e['Event_length', ], 0.99)   # quantile-relative, so scale is fine
sce_singlets <- sce[, keep]
```

## Per-Method Failure Modes

### 1D area gate leaves doublets
**Trigger:** gating only FSC-A. **Mechanism:** doublets overlap singlets in area. **Symptom:** double-positive clusters persist. **Fix:** gate the FSC-A vs FSC-H diagonal (+ Width).

### Heterotypic conjugate survives scatter gating
**Trigger:** a surprising double-positive between two single-positive clusters. **Mechanism:** T:monocyte conjugate is scatter-normal, lineage markers comparable to singlets. **Symptom:** "novel" DP population with an elevated shared marker (e.g. CD45). **Fix:** treat as suspected doublet; check the shared-marker signal; confirm/resolve by imaging flow (bright-field aspect ratio) when load-bearing.

### CyTOF "doublet gate" using scatter
**Trigger:** porting flow logic to CyTOF. **Mechanism:** no FSC/SSC exists. **Symptom:** no scatter channels. **Fix:** use DNA + Gaussian/Event_length.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| expected doublet rate ~1-5% (PBMC), higher in tissue | community | flag samples far above as prep issues - not a removal cutoff |
| Gaussian + DNA gating improves CV (3.45 -> ~2.04) | Bagwell 2020 *Cytometry A* 97:184 | combined DNA + Gaussian over baseline (Gaussian alone ~2.41) |

Note: a fixed "95th-percentile residual" cutoff is arbitrary; prefer a visual diagonal gate or the instrument's Gaussian parameters over an unjustified quantile.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| double-positive cluster that "shouldn't" exist | residual heterotypic doublets | check for an elevated shared marker (CD45); confirm by imaging flow |
| no FSC/SSC channels (CyTOF) | mass data has no scatter | use DNA/Gaussian/Event_length |
| over-removal of large cells | rectangle gate clips real large singlets | use a diagonal polygon, not a box |

## References

- Stadinski 2020 *Cytometry A* 97(11):1102-1104 — heterotypic doublets survive scatter gating.
- Bagwell 2020 *Cytometry A* 97(2):184-198 — automated CyTOF cleanup via Gaussian/Event_length.
- Finck 2013 *Cytometry A* 83(5):483-494 — CyTOF DNA/event parameters in normalization context.

## Related Skills

Workflow order (CyTOF): EQ-bead drift normalization (raw, FIRST) -> cytometry-qc -> doublet-detection -> clustering -> CytoNorm cross-batch (LAST)

- cytometry-qc - Run first: flow-rate/signal/margin cleaning
- bead-normalization - CyTOF drift correction after doublet removal
- fcs-handling - Load FCS files
- gating-analysis - Where singlet discrimination sits in the hierarchy
- clustering-phenotyping - Downstream analysis after doublet removal
- single-cell/doublet-detection - Droplet scRNA-seq doublet methods (different principle)
<!-- END FILE: flow-cytometry/doublet-detection/SKILL.md -->

## 子目录：flow-cytometry/fcs-handling

<!-- BEGIN FILE: flow-cytometry/fcs-handling/SKILL.md -->
---
name: bio-flow-cytometry-fcs-handling
description: Reads, inspects, and writes Flow Cytometry Standard (FCS) files from conventional, spectral, and mass cytometry (CyTOF), and parses FlowJo/Cytobank/Diva workspaces. Covers FCS 2.0/3.0/3.1/3.2 internals ($PnE linear-vs-log, $DATATYPE, $SPILLOVER vs SPILL vs $COMP, $TIMESTEP), channel/parameter metadata, the silent linearize/truncate defaults, and R (flowCore, flowWorkspace, CytoML) plus Python (FlowKit, readfcs) readers. Use when loading flow or mass cytometry data, mapping detector channels to antibodies, extracting the event matrix, choosing a reader, or bridging FCS to the scanpy/AnnData ecosystem before preprocessing.
tool_type: mixed
primary_tool: flowCore
---

## Version Compatibility

Reference examples tested with: flowCore 2.14+, flowWorkspace 4.14+, CytoML 2.14+; Python flowkit 1.1+, readfcs 1.1+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# FCS File Handling

**"Load my FCS files and inspect the channels"** -> Parse FCS format into event matrix + parameter metadata, map detector channels to antibodies, and choose a reader appropriate to the instrument and downstream ecosystem.
- R: `flowCore::read.FCS()` / `read.flowSet()` -> `flowFrame`/`flowSet`; `CytoML::flowjo_to_gatingset()` for FlowJo workspaces
- Python: `flowkit.Sample()` (full workflow) or `readfcs.read()` -> AnnData (scanpy/scverse bridge)

## The Single Most Important Modern Insight -- read.FCS Silently Transforms by Default

`flowCore::read.FCS()` defaults to `transformation = "linearize"`, which APPLIES the `$PnE` log-amplification scaling on read. Two pipelines reading "the same raw FCS" (flowCore default vs `fcsparser`/`transformation=FALSE`) therefore return different numbers, and a compensation matrix computed on one will silently mismatch the other. For any preprocessing pipeline that will compensate and transform downstream, read with `transformation = FALSE` (or `NULL`) to get the genuinely raw values, and set `truncate_max_range = FALSE` so out-of-`$PnR` events (common on CyTOF and some digital instruments) are not silently clipped. Decide the read settings deliberately; they are not nuisance defaults.

## FCS Standard Internals (what the keywords mean)

| Keyword | Meaning | Decision-relevant nuance |
|---------|---------|--------------------------|
| `$PnE` | amplification type `"decades,offset"` | `"0,0"` = linear; FCS 3.1 FORBIDS log-stored floats (a float param must be `"0,0"`); log `$PnE` survives only on legacy integer analog-log data |
| `$DATATYPE` | I (uint) / F (float) / D (double) / A (ASCII, deprecated 3.1) | FCS 3.2 allows MIXED types per parameter via `$PnDATATYPE` (integer Time + float fluorescence) |
| `$PnR` | parameter range | for integers defines the bit mask via next power of two (`$PnR=1024` -> 10-bit), NOT a value clamp |
| `$SPILLOVER` | standardized compensation matrix (3.1+) | digital BD instruments wrote non-standard `SPILL` (no `$`); 3.0 `$COMP` stored a matrix WITHOUT naming parameters (ambiguous -> why `$SPILLOVER` exists) |
| `$TIMESTEP` | seconds per Time-channel unit | the master axis for all time-based QC; missing/wrong `$TIMESTEP` silently breaks flow-rate/drift checks |

FCS standards: 3.0 (Seamer 1997 *Cytometry* 28:118), 3.1 (Spidlen 2010 *Cytometry A* 77:97), 3.2 (Spidlen 2021 *Cytometry A* 99:100). Area/Height/Width = pulse integral/peak/duration; FSC-A vs FSC-H is the doublet axis. CyTOF channels are `<Metal><Mass>Di` (e.g. `Yb176Di`) and report dual counts (pulse-counting at low signal, intensity at high).

## Reader Taxonomy

| Reader | Language | What it does | When to use |
|--------|----------|--------------|-------------|
| `flowCore::read.FCS`/`read.flowSet` | R | core FCS -> flowFrame/flowSet | the default for any R/Bioconductor pipeline |
| `flowWorkspace` GatingSet | R | gated hierarchy container | when carrying gates/populations |
| `CytoML` | R | FlowJo (wsp) / Cytobank / Diva import-export | round-tripping a manual analysis (Finak 2018 *Cytometry A* 93:1189) |
| `flowkit` (Session/Sample) | Python | FCS + GatingML 2.0 + FlowJo wsp + compensation/transforms | Python pipelines, FlowJo interop (White 2021 *Front Immunol* 12:768541) |
| `readfcs` | Python | FCS -> AnnData | bridge to scanpy/scverse and the single-cell categories |
| `fcsparser` / `FlowCal` | Python | low-level reader / reader + MEF calibration | quick parse; FlowCal for MESF/MEF work |

## Load and Inspect FCS (R)

**Goal:** Read one file (or a directory) raw, inspect parameters, and map channels to antibodies.

**Approach:** Read with `transformation=FALSE, truncate_max_range=FALSE`; the channel->antibody map lives in `pData(parameters(fcs))` (`name` = detector, `desc` = antibody).

```r
library(flowCore)

fcs <- read.FCS('sample.fcs', transformation = FALSE, truncate_max_range = FALSE)
params <- pData(parameters(fcs))          # name (detector), desc (antibody), range, minRange
channel_map <- setNames(params$desc, params$name)

fs <- read.flowSet(list.files('data', pattern = '\\.fcs$', full.names = TRUE),
                   transformation = FALSE, truncate_max_range = FALSE)
expr <- exprs(fcs)                         # cells x channels
```

## Access the Compensation Matrix from Keywords

**Goal:** Retrieve the acquisition-recorded spillover matrix, handling the three keyword conventions.

**Approach:** Try `$SPILLOVER`, then the legacy `SPILL`, then `$COMP`; `flowCore::spillover()` resolves the standard slots.

```r
kw <- keyword(fcs)
spill <- kw$`$SPILLOVER`
if (is.null(spill)) spill <- kw$SPILL          # digital BD convention
if (is.null(spill)) spill <- kw$`$COMP`        # legacy FCS 3.0 (unnamed columns)
```

## Load FCS in Python (FlowKit / readfcs)

**Goal:** Read FCS in a Python pipeline, either for FlowKit's compensation/gating or as an AnnData for scanpy.

**Approach:** `flowkit.Sample` exposes raw/compensated/transformed events as DataFrames; `readfcs.read` returns AnnData with channels in `var`.

```python
import flowkit as fk
import readfcs

sample = fk.Sample('sample.fcs')
events = sample.as_dataframe(source='raw')   # source in {'raw','comp','xform'}

adata = readfcs.read('sample.fcs')           # AnnData; adata.var has channel + antibody names
```

## Rename Channels, Subset, Write, Annotate Samples

**Goal:** Standardize channel names to antibodies and attach sample-level metadata for downstream tools.

**Approach:** Replace blank `desc` with `name`; attach a `pData` table keyed by `sampleNames(fs)` (CATALYST/diffcyt require this).

```r
new <- ifelse(is.na(params$desc) | params$desc == '', params$name, params$desc)
colnames(fcs) <- new

fcs_markers <- fcs[, c('CD4', 'CD8', 'CD3')]          # subset channels
write.FCS(fcs, 'out.fcs')

pData(fs) <- data.frame(name = sampleNames(fs),
                        condition = c('Control','Control','Treatment','Treatment'),
                        patient = c('P1','P2','P1','P2'),
                        row.names = sampleNames(fs))
```

## Per-Method Failure Modes

### Silent log-linearization on read
**Trigger:** `read.FCS('x.fcs')` with default args. **Mechanism:** `transformation="linearize"` applies `$PnE` scaling. **Symptom:** values differ from `fcsparser`; compensation matrix mismatch. **Fix:** `transformation = FALSE`.

### Out-of-range clipping
**Trigger:** instrument wrote values above `$PnR` (common CyTOF). **Mechanism:** `truncate_max_range=TRUE` (default) clamps them. **Symptom:** a ceiling artifact at the channel max. **Fix:** `truncate_max_range = FALSE`.

### Channel names break formulas
**Trigger:** channels like `FSC-A`, `Pacific Blue-A`. **Mechanism:** hyphens/spaces are not syntactic R names. **Symptom:** formula/gating errors. **Fix:** `alter.names = TRUE` on read.

### FlowJo parsing in the wrong package
**Trigger:** looking for FlowJo import in flowWorkspace. **Mechanism:** parsing lives in CytoML. **Symptom:** function-not-found. **Fix:** `CytoML::open_flowjo_xml()` -> `flowjo_to_gatingset()`; only `.wsp` (FlowJo 10+), not legacy `.jo`.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `exprs()` numbers differ across tools | default linearize | read with `transformation=FALSE` everywhere |
| spillover keyword is `NULL` | instrument used `SPILL`/`$COMP` | try all three keyword names |
| editing `exprs(ff)` corrupts ranges | direct reassignment skips `parameters()` update | use transform/`Subset` workflows |
| readfcs compensation not applied | matrix names don't match `var_names` | align channel names before relying on it |

## References

- Seamer 1997 *Cytometry* 28(2):118-122 — FCS 3.0 standard.
- Spidlen 2010 *Cytometry A* 77(1):97-100 — FCS 3.1 standard.
- Spidlen 2021 *Cytometry A* 99(1):100-102 — FCS 3.2 standard.
- Finak 2018 *Cytometry A* 93(12):1189-1196 — CytoML cross-platform gating import/export.
- White 2021 *Front Immunol* 12:768541 — FlowKit Python toolkit.
- Lee 2008 *Cytometry A* 73(10):926-930 — MIFlowCyt minimum reporting standard.

## Related Skills

- compensation-transformation - Compensate and transform after loading
- cytometry-qc - Assess acquisition quality on the loaded data
- gating-analysis - Define populations from the loaded GatingSet
- clustering-phenotyping - Unsupervised analysis of the event matrix
- single-cell/data-io - readfcs bridges FCS to the AnnData/scanpy ecosystem
- imaging-mass-cytometry/data-preprocessing - Shared metal-channel and FCS conventions
<!-- END FILE: flow-cytometry/fcs-handling/SKILL.md -->

## 子目录：flow-cytometry/gating-analysis

<!-- BEGIN FILE: flow-cytometry/gating-analysis/SKILL.md -->
---
name: bio-flow-cytometry-gating-analysis
description: Defines cell populations in flow and spectral cytometry through manual gates (rectangle, polygon, quadrant, boolean) and reproducible automated gating (openCyto gating templates, flowDensity data-driven thresholds, flowClust model-based gates), organized as a hierarchical GatingSet (flowWorkspace) and round-tripped with FlowJo via CytoML. Covers the canonical gate order (time -> debris -> singlets -> live -> lineage), FMO-vs-isotype boundary setting, gate-order dependence and recompute semantics, rare-event/MRD gating, and per-population statistics. Use when building a gating strategy, automating a manual FlowJo scheme across samples, choosing manual vs data-driven gates, or extracting population frequencies.
tool_type: r
primary_tool: flowWorkspace
---

## Version Compatibility

Reference examples tested with: flowWorkspace 4.14+, openCyto 2.14+, flowDensity 1.36+, flowCore 2.14+, CytoML 2.14+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

openCyto gating-method names drift across versions - confirm with `gt_list_methods()` on the installed package (e.g. `gate_flowclust_2d` vs `flowClust.2d`). Adapt rather than retrying.

# Gating Analysis

**"Gate my data to identify cell populations"** -> Define populations by drawing boundaries in marker space, organized as a hierarchy, manually or with reproducible data-driven methods.
- R (manual + hierarchy): `flowCore` gates -> `flowWorkspace::GatingSet` -> `gs_pop_add` -> `recompute`
- R (automated): `openCyto` gating template (CSV) or `flowDensity::deGate`

## The Single Most Important Modern Insight -- FMO, Not Isotype, Sets the Boundary; and Gate Order Is a Funnel

The position of a positive/negative boundary is governed by SPREADING ERROR - the variance that every other bright fluorophore spills into the channel of interest - NOT by nonspecific antibody binding (Roederer 2001 *Cytometry* 45:194). An FMO control (full panel minus the one channel) reproduces exactly that spreading and is the correct way to set the gate; an isotype control addresses only nonspecific binding, has a different total fluorochrome load, and sits in the wrong place. Isotypes are deprecated for boundary-setting (still fine for a qualitative new-reagent check). Equally load-bearing is gate ORDER: time -> debris (FSC/SSC) -> singlets (FSC-A vs FSC-H) -> live/dead -> lineage. This is a funnel that removes the broadest, least-specific contaminants first (time instability corrupts ALL channels; doublets are scatter-normal AND viable AND double-positive; dead cells bind antibody nonspecifically) so each narrower downstream gate operates on clean input. Reorder it - gate lineage before singlets - and artifacts are baked into the result that no later gate can remove.

## Automated-Gating Taxonomy

| Method | Citation | Mechanism | When to use |
|--------|----------|-----------|-------------|
| openCyto | Finak 2014 *PLoS Comput Biol* 10:e1003806 | CSV gatingTemplate + per-gate algorithms | reproduce a manual SOP across many samples; human-readable + automated |
| `mindensity` (openCyto) | - | KDE valley between two peaks | clear bimodal marker, 1D cut |
| `tailgate` (openCyto) | - | KDE-derivative tail onset | rare positive tail, no clean second peak |
| `quantileGate` (openCyto) | - | cut at a fixed event quantile | threshold should track a fraction |
| flowDensity | Malek 2015 *Bioinformatics* 31:606 | sequential bivariate density cutoffs | reproduce an entire predefined manual strategy |
| flowClust / `gate_flowclust_2d` | Lo 2009 *BMC Bioinformatics* 10:145 | t-mixture + Box-Cox, K by BIC | overlapping elliptical populations |
| DAFi | Lee 2018 *Cytometry A* 93:597 | recursive filter + clustering on a hierarchy | discovery WITH interpretability |

Rule of thumb: 1D bimodal -> `mindensity`; rare tail -> `tailgate`; overlapping ellipses -> `flowClust.2d`; replicate a full manual SOP -> flowDensity; discovery-with-interpretability -> DAFi.

## Build a Gating Hierarchy

**Goal:** Apply gates in the canonical order and extract population statistics.

**Approach:** Build a GatingSet, add gates parent-by-parent, then `recompute()` - WITHOUT it, child populations are empty. Gates apply on the TRANSFORMED scale if the GatingSet is transformed.

```r
library(flowWorkspace); library(flowCore)

gs <- GatingSet(fs)
# matrix dimnames preserve 'FSC-A'/'FSC-H'; data.frame() would mangle them to FSC.A
singlet <- polygonGate('singlets', .gate = matrix(
  c(2e4, 1e4, 25e4, 2e5, 25e4, 26e4, 2e4, 4e4), ncol = 2, byrow = TRUE,
  dimnames = list(NULL, c('FSC-A', 'FSC-H'))))
gs_pop_add(gs, singlet, parent = 'root')
gs_pop_add(gs, rectangleGate('CD3+', CD3 = c(1.5, Inf)), parent = 'singlets')  # transformed scale
recompute(gs)                                   # REQUIRED - else children are empty
gs_pop_get_stats(gs, type = 'count')
```

## Automated Gating with an openCyto Template

**Goal:** Apply a reproducible, declarative gating strategy across all samples.

**Approach:** A CSV template (alias/pop/parent/dims/gating_method/gating_args) defines the hierarchy; `gt_gating` applies it. Confirm method names with `gt_list_methods()`.

```r
library(openCyto); library(data.table)

tmpl <- fread('
alias,pop,parent,dims,gating_method,gating_args
nonDebris,+,root,FSC-A,mindensity,
singlets,+,nonDebris,"FSC-A,FSC-H",singletGate,
live,-,singlets,"Live_Dead",mindensity,
CD3,+,live,CD3,mindensity,
CD4CD8,+,CD3,"CD4,CD8",gate_flowclust_2d,K=2
')
gt <- gatingTemplate(tmpl)
gs <- GatingSet(fs)
gt_gating(gt, gs)
```

## Rare-Event / MRD Gating

**Goal:** Detect a rare population (e.g. MRD at 1e-4 to 1e-5).

**Approach:** Unsupervised clustering FAILS here (a 1e-5 population is ~10 events, invisible to density/SOM); MRD stays supervised/template-gated. Compute the acquisition depth needed from the target sensitivity and the ~50-event Poisson rule BEFORE acquiring; never downsample.

```r
# Need ~50-60 target events for CV < ~15%; sensitivity 1e-5 => acquire ~1e6 cells.
target_sensitivity <- 1e-5
events_needed <- ceiling(50 / target_sensitivity)   # cells to acquire
# Gate the rare population with a prespecified template; report observed LOD from cells acquired.
```

## Per-Method Failure Modes

### Empty child populations
**Trigger:** querying stats right after `gs_pop_add`. **Mechanism:** membership not computed. **Symptom:** zero counts. **Fix:** `recompute(gs)`.

### Gate coordinates on the wrong scale
**Trigger:** raw-scale gate values on a transformed GatingSet (or vice versa). **Mechanism:** scale mismatch. **Symptom:** gate in the wrong place / empty. **Fix:** set gate values on the same (transformed) scale the GS uses.

### Isotype-defined boundary
**Trigger:** isotype control to set positivity. **Mechanism:** spreading error, not nonspecific binding, sets the edge. **Symptom:** wrong negative boundary. **Fix:** use FMO.

### Clustering used for rare events
**Trigger:** FlowSOM for a 1e-5 population. **Mechanism:** too few events. **Symptom:** rare pop absorbed into a neighbor. **Fix:** supervised/template gating; size acquisition for the Poisson floor.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| ~50-60 events for CV < 15% | Poisson statistics | rare-event detection floor |
| sensitivity 1e-5 needs ~1e6 cells | Poisson floor | to collect ~50 events at that frequency |
| FMO for boundary, not isotype | Roederer 2001; Maecker & Trotter 2006 | spreading error dominates the boundary |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| zero counts in children | no `recompute()` | call it after adding gates |
| `gt_gating` method not found | version-renamed method | check `gt_list_methods()` |
| `filter()` vs `Subset()` confusion | `filter` returns a mask, `Subset` the data | use `Subset(ff, gate)` for the population |
| FlowJo `.jo` won't import | only `.wsp` supported | re-save as wsp; use CytoML |

## References

- Roederer 2001 *Cytometry* 45(3):194-205 — spreading error sets the gate boundary.
- Maecker & Trotter 2006 *Cytometry A* 69(9):1037-1042 — FMO doctrine, controls, positivity.
- Finak 2014 *PLoS Comput Biol* 10(8):e1003806 — openCyto automated gating templates.
- Malek 2015 *Bioinformatics* 31(4):606-607 — flowDensity data-driven gating.
- Lo 2009 *BMC Bioinformatics* 10:145 — flowClust model-based gating.
- Lee 2018 *Cytometry A* 93(6):597-610 — DAFi directed filtering + clustering.
- Spidlen 2015 *Cytometry A* 87(7):683-687 — Gating-ML 2.0 portable gate standard.

## Related Skills

- compensation-transformation - Preprocess before gating; gate on the transformed scale
- doublet-detection - The singlet step of the gating funnel
- clustering-phenotyping - Unsupervised alternative for high-dim discovery
- differential-analysis - Compare gated population frequencies between conditions
- fcs-handling - Load FCS and import FlowJo workspaces via CytoML
<!-- END FILE: flow-cytometry/gating-analysis/SKILL.md -->

<!-- END CATEGORY: flow-cytometry -->

