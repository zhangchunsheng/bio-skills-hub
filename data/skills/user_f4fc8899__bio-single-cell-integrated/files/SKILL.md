---
slug: bio-single-cell-integrated
version: 1.0.0
displayName: "单细胞分析 / Full single-cell RNA/ATAC-seq analysis pipeline"
name: bio-single-cell-integrated
summary: >-
  中文：单细胞分析综合技能，整合 17 个相关专题，覆盖单细胞RNA/ATAC-seq分析全流程：QC、聚类、注释、轨迹推断、细胞通讯、Perturb-seq、谱系追踪。 English: Integrated Full single-cell RNA/ATAC-seq analysis pipeline skill covering 17 related topics, including Full single-cell RNA/ATAC-seq analysis pipeline: QC, clustering, annotation, trajectory inference, cell communication, Perturb-seq, lineage tracing.
description: >-
  中文：这是一个面向单细胞分析的综合生物信息学 Skill，整合当前分类下 17 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：单细胞RNA/ATAC-seq分析全流程：QC、聚类、注释、轨迹推断、细胞通讯、Perturb-seq、谱系追踪。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Cassiopeia, CellTypist, Harmony。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Full single-cell RNA/ATAC-seq analysis pipeline, combining 17 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Full single-cell RNA/ATAC-seq analysis pipeline: QC, clustering, annotation, trajectory inference, cell communication, Perturb-seq, lineage tracing. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Cassiopeia, CellTypist, Harmony. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# single-cell 分类 Skill 整合版

> 本文件整合同一主分类目录下 17 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: single-cell -->

## 子目录：single-cell/batch-integration

<!-- BEGIN FILE: single-cell/batch-integration/SKILL.md -->
---
name: bio-single-cell-batch-integration
description: Integrate multiple scRNA-seq samples or batches with Harmony, scVI/scANVI, Seurat (CCA/RPCA), fastMNN, Scanorama, or BBKNN. Resolves which method to use for the dataset size and design, how strongly to correct, when integration is the wrong move (confounded batch/biology), how to score integration with scIB metrics without gaming them, and why corrected expression must not be used for differential expression. Use when integrating batches or datasets, choosing an integration method, diagnosing over-correction, or judging integration quality.
tool_type: mixed
primary_tool: Harmony
---

## Version Compatibility

Reference examples tested with: scanpy 1.10+, Seurat 5.0+, scvi-tools 1.1+, harmonypy 0.0.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Batch Integration

**"Integrate my batches"** -> Learn a shared low-dimensional representation that mixes technical batches while preserving biological cell states, then cluster and visualize on it.
- Python: `sce.pp.harmony_integrate`, `scvi.model.SCVI`, `sce.pp.bbknn`, `scanorama`
- R: `RunHarmony`, `IntegrateLayers` (Seurat v5), `fastMNN` (batchelor)

## Governing Principle

Integration trades batch-mixing against biological-signal preservation, and the two cannot be jointly maximized. The algorithm removes variance along directions where batches differ, on the assumption that cell-type composition is shared across batches; it does not "know" which variance is technical. When batch correlates with a real biological axis, the method cannot distinguish them and, by construction, erases biology - this is information-theoretic, not a tuning problem. Over-correction is the silent failure: it absorbs rare cell types into common neighbors, snaps continuous gradients toward shared anchors, and deletes condition-specific populations, all while batch-mixing metrics improve. The cells most worth finding (rare, transitional, novel) are exactly the ones integration most endangers. Batch and biology are unidentifiable under confounding - the only tie-breaker is external information (shared controls, multiplexed designs, known shared types), and the fix for a confounded design is experimental, not computational. Always keep the uncorrected embedding for before/after comparison, and never run differential expression on batch-corrected expression.

## When NOT to Integrate

Visualize the uncorrected data first; integration is a bias-variance trade and removing batch variance risks removing biology correlated with batch.

- Confounded design (each condition is its own batch, e.g. all controls day 1, all treated day 2): no algorithm can separate batch from biology. The diagnostic: cluster the uncorrected data and cross-tabulate clusters x batch x condition; pure-by-batch clusters that are also condition-aligned mean integration is unsafe. The fix is experimental - multiplex conditions across batches (cell hashing; genetic demux via souporcell/vireo; split each condition across capture days).
- Technical replicates of the same tissue that already mix well: over-correction risk outweighs benefit.
- Per-sample analyses (CNV/tumor-clone inference): integration would erase the signal of interest.

Over-correction signatures: rare types collapsing into neighbors, lost known gradients, disappearing condition-specific populations, markers no longer separating known cell types.

## Method Selection

No method wins universally - the scIB benchmark (Luecken 2022, 68 method/preprocessing combos) scores integration as overall = 0.6 x bio-conservation + 0.4 x batch-removal, deliberately weighting biology higher because erasing it is worse than imperfect mixing. Methodology evolves; verify current best practice and APIs against the installed package docs, and in practice run 2-3 candidates and score them (see Evaluating Integration).

| Method | Model / assumption | Use when | Fails when |
|--------|-------------------|----------|------------|
| Harmony | Iterative soft k-means linear correction in PCA space; outputs an embedding, not counts | Few/simple batches, fast, low memory; strong default; best usability | Strong nonlinear batch effects; high `theta` over-mixes and collapses distinct types |
| scVI | Conditional VAE on raw counts (ZINB), batch as covariate -> batch-invariant latent | Large atlases, many nested batches, strong effects; memory-efficient at scale | Small data (under-trained); latent dims over-interpreted as "biology minus batch" |
| scANVI | Semi-supervised scVI using partial labels to protect biology | Some cell labels exist and bio fidelity is paramount (tops bio-conservation) | Labels noisy/wrong; training cost; closed-world for the labeled states |
| Seurat CCA | Anchor-based, canonical correlation across datasets | Strong shared structure under large shifts; smaller data | Substantial non-overlap or many samples -> over-correction (CCA aligns distinct states) |
| Seurat RPCA | Reciprocal-PCA anchors; faster, more conservative | Large/many-sample data, substantial non-overlap | Under-correction when truly shared structure is subtle (raise `k.anchor`) |
| fastMNN | Mutual nearest neighbors in PCA space | Rare-population preservation; moderate data | Order-sensitive (set `merge.order`, most-heterogeneous first); legacy mnnCorrect is slow |
| Scanorama | Mutual NN across all dataset pairs | Partial cell-type overlap across datasets; balanced bio/batch | Very large data (slower than Harmony/BBKNN) |
| BBKNN | Modifies only the neighbor graph (batch-balanced kNN) | Speed; only clustering/UMAP needed downstream | Leans toward batch removal; no embedding or corrected counts for other uses |

scIB headline: top combined performers were scANVI, scVI, Scanorama, scGen; Harmony and Seurat were strong on simpler tasks with the best usability; BBKNN sits at the batch-removal end. "Deep methods are always best" is not supported - Harmony/Seurat win simple/small tasks; deep methods win complex/large/label-rich tasks.

## Strength Parameters

Aggressive settings increase mixing and over-correction risk in lockstep - raise correction strength only after confirming under-correction, and re-check rare populations after each change.

| Parameter | Tool | Effect | Rationale |
|-----------|------|--------|-----------|
| theta | Harmony | Higher -> more aggressive batch mixing | Default is an internal fallback, not the signature default; larger theta over-corrects |
| k.anchor | Seurat | Higher -> more anchors, stronger correction | Raise (e.g. 20) only when under-correcting |
| CCA vs RPCA | Seurat | CCA more sensitive but can over-correct; RPCA conservative | Prefer RPCA for large/non-overlapping data |
| n_latent | scVI | Latent dimensionality of the embedding | ~10-30; too high refits noise, too low under-fits |
| merge.order | fastMNN | Order batches are merged | Order-sensitive; merge most-heterogeneous batch first |

## Integrate with Harmony

**Goal:** Correct batch in PCA space and run downstream steps on the corrected embedding.
**Approach:** Joint preprocessing -> PCA -> Harmony -> neighbors/UMAP/clustering on `X_pca_harmony`.

```python
import scanpy as sc
import scanpy.external as sce

adata = sc.read_h5ad('merged.h5ad')
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, batch_key='batch')
adata.raw = adata
adata = adata[:, adata.var.highly_variable]
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, n_comps=50)

sce.pp.harmony_integrate(adata, key='batch')  # writes adata.obsm['X_pca_harmony']
sc.pp.neighbors(adata, use_rep='X_pca_harmony')
sc.tl.umap(adata)
sc.tl.leiden(adata, flavor='igraph', n_iterations=2, directed=False)
```

In Seurat: `RunHarmony(obj, group.by.vars = 'orig.ident', reduction.use = 'pca')` writes a `harmony` reduction; `group.by.vars` takes a vector to correct multiple covariates.

## Integrate with scVI / scANVI

**Goal:** Learn a batch-invariant latent space from raw counts, optionally protecting known labels.
**Approach:** Put raw counts in a layer, register batch (and labels for scANVI), train, and use the latent embedding downstream.

```python
import scvi
import scanpy as sc

adata = sc.read_h5ad('merged.h5ad')
adata.layers['counts'] = adata.X.copy()  # scVI needs raw counts
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor='seurat_v3',
                            layer='counts', batch_key='batch')
adata = adata[:, adata.var.highly_variable].copy()

scvi.model.SCVI.setup_anndata(adata, layer='counts', batch_key='batch')
model = scvi.model.SCVI(adata, n_latent=10, gene_likelihood='zinb')
model.train()  # default max_epochs heuristic scales down for large data
adata.obsm['X_scVI'] = model.get_latent_representation()

scanvi = scvi.model.SCANVI.from_scvi_model(model, 'Unknown', labels_key='cell_type')
scanvi.train(max_epochs=20)
adata.obs['scanvi_label'] = scanvi.predict()
```

The scVI latent space is not "biology with batch removed": it is a learned nonlinear embedding optimized to reconstruct counts while being marginally independent of batch. Its dimensions are entangled, individually uninterpretable, and carry no guaranteed correspondence to any biological quantity - treat it as a coordinate system for neighbors/clustering, not a measurement. Note `unlabeled_category` ('Unknown') is the second positional argument to `from_scvi_model`, before `labels_key`.

## Integrate with Seurat v5

**Goal:** Use Seurat v5's modular layer-based integration with a chosen method.
**Approach:** Split layers by batch, run the standard pipeline, call IntegrateLayers, rejoin.

```r
library(Seurat)

merged[['RNA']] <- split(merged[['RNA']], f = merged$batch)
merged <- NormalizeData(merged)
merged <- FindVariableFeatures(merged)
merged <- ScaleData(merged)
merged <- RunPCA(merged)

merged <- IntegrateLayers(merged, method = RPCAIntegration,
                          orig.reduction = 'pca', new.reduction = 'integrated.rpca')
merged <- JoinLayers(merged)
merged <- FindNeighbors(merged, reduction = 'integrated.rpca', dims = 1:30)
merged <- FindClusters(merged, resolution = 0.5)
merged <- RunUMAP(merged, reduction = 'integrated.rpca', dims = 1:30)
```

Methods are passed as bare symbols: `CCAIntegration`, `RPCAIntegration`, `HarmonyIntegration`, `FastMNNIntegration`, `scVIIntegration`. For graph-only correction with BBKNN in Python: `sce.pp.bbknn(adata, batch_key='batch')` rewrites the neighbor graph in place (very fast, feeds Leiden/UMAP only).

## Evaluating Integration

**Goal:** Decide whether integration mixed batches without erasing biology.
**Approach:** Score batch-mixing and bio-conservation separately and read them jointly - never optimize a batch metric alone.

```python
import scanpy as sc
from sklearn.metrics import silhouette_score

# batch silhouette: lower = batches mixed; cell-type silhouette: higher = biology kept
batch_sil = silhouette_score(adata.obsm['X_scVI'], adata.obs['batch'])
ct_sil = silhouette_score(adata.obsm['X_scVI'], adata.obs['cell_type'])

# scib-metrics Benchmarker scores many methods on a common axis set
# from scib_metrics.benchmark import Benchmarker
```

Batch-mixing metrics (kBET, graph iLISI) are trivially maximized by over-correction - a method that destroys all structure mixes batches perfectly while annihilating biology. Bio-conservation metrics (ARI, NMI, cell-type ASW, graph cLISI, isolated-label F1) guard against that, which is why the scIB composite down-weights batch-removal to 0.4. Selecting a method on a batch metric alone selects for over-correction; always pair batch metrics with bio metrics and inspect rare populations before/after. Run candidates through `scib-metrics` (`Benchmarker`) and pick the most robust for the specific task.

Differential expression: use integration outputs (Harmony/scVI/RPCA embeddings) for clustering and visualization, but run DE on uncorrected, log-normalized counts - never on batch-corrected expression. Harmony and BBKNN produce no corrected counts; Scanorama and fastMNN do, and those must not feed DE. For cross-condition DE, aggregate to pseudobulk per sample x cell type (see differential-expression/deseq2-basics).

## Reference Mapping vs De-novo Integration

De-novo integration jointly embeds all datasets symmetrically (everything above). Reference mapping projects a query onto a fixed reference embedding without retraining (scArches architectural surgery; Azimuth `FindTransferAnchors` + `MapQuery`) - fast, reproducible, scales to millions, consistent cross-study labels. It is closed-world: a novel state the reference never saw is confidently assigned the nearest reference label, converting a technical or biological surprise into a wrong annotation that looks clean and high-confidence. Use reference mapping when a high-quality annotated atlas exists; use de-novo when no suitable reference exists or the query may hold genuinely novel populations. Always inspect per-cell mapping uncertainty and never trust transferred labels for clusters that map poorly.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| The cell type of interest vanished after integration | Over-correction absorbed a rare/condition-specific population | Reduce strength (lower theta / use RPCA / fastMNN/Scanorama); compare to uncorrected embedding |
| Batches still separate on UMAP | Under-correction | Raise correction strength (k.anchor, switch CCA, more Harmony iterations); confirm batch key is correct |
| "Integration removed my treatment effect" | Confounded batch/condition design | Stop - batch and biology are unidentifiable; redesign with multiplexing; do not integrate away the contrast |
| Great iLISI/kBET but biology looks flattened | Metric gaming by over-correction | Score bio-conservation too (ASW-celltype, cLISI, ARI); use the scIB composite, not a batch metric alone |
| DE between two control samples after integration | DE run on batch-corrected expression | Run DE on uncorrected log-normalized counts; use pseudobulk for cross-condition |
| scVI latent dimension interpreted as a biological axis | Latent space is entangled, not "biology minus batch" | Use the embedding only for neighbors/clustering; do not read individual dims |
| Reference-mapped labels look confident but wrong | Closed-world projection of a novel/shifted state | Inspect mapping uncertainty; treat poorly-mapping clusters as candidate novelty/batch |
| Results differ run to run | Stochastic training / unpinned seeds (scVI, Harmony) | Set seeds; for scVI fix `max_epochs` and report it |

## Related Skills

- preprocessing - QC and normalization that must precede integration
- clustering - Cluster on the integrated embedding, not on raw PCA
- cell-annotation - Reference mapping and label transfer after integration
- single-cell/multimodal-integration - Joint analysis across modalities (distinct from batch integration)
- single-cell/differential-abundance - Test whether composition shifts across conditions after integration
- single-cell/cnv-inference - Per-patient malignant-cell/CNV inference (do not integrate tumors across patients)
- differential-expression/deseq2-basics - Pseudobulk DE on uncorrected counts per cell type
- data-visualization/dimensionality-reduction-plots - Before/after UMAP comparison figures

## References

- Korsunsky et al. (2019). Fast, sensitive and accurate integration of single-cell data with Harmony. Nat Methods 16(12):1289-1296.
- Lopez et al. (2018). Deep generative modeling for single-cell transcriptomics (scVI). Nat Methods 15(12):1053-1058.
- Xu et al. (2021). Probabilistic harmonization and annotation of single-cell transcriptomics data with deep generative models (scANVI). Mol Syst Biol 17(1):e9620.
- Luecken et al. (2022). Benchmarking atlas-level data integration in single-cell genomics (scIB). Nat Methods 19:41-50.
- Hie, Bryson & Berger (2019). Efficient integration of heterogeneous single-cell transcriptomes using Scanorama. Nat Biotechnol 37:685-691.
- Polanski et al. (2020). BBKNN: fast batch alignment of single cell transcriptomes. Bioinformatics 36(3):964-965.
- Haghverdi et al. (2018). Batch effects in single-cell RNA-sequencing data are corrected by matching mutual nearest neighbors (MNN). Nat Biotechnol 36:421-427.
- Lotfollahi et al. (2022). Mapping single-cell data to reference atlases by transfer learning (scArches). Nat Biotechnol 40(1):121-130.
<!-- END FILE: single-cell/batch-integration/SKILL.md -->

## 子目录：single-cell/cell-annotation

<!-- BEGIN FILE: single-cell/cell-annotation/SKILL.md -->
---
name: bio-single-cell-cell-annotation
description: Automated reference-based cell type annotation for single-cell RNA-seq using CellTypist, SingleR, Azimuth, scANVI, and scmap to transfer labels from a reference. Use when annotating cell types from a reference atlas or pretrained model, transferring labels onto a query, assessing prediction confidence and rejection, or triaging whether an unexpected cluster is a novel type versus a doublet, low-quality, or batch artifact.
tool_type: mixed
primary_tool: CellTypist
---

## Version Compatibility

Reference examples tested with: scanpy 1.10+, Seurat 5.0+, celltypist 1.6+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Automated Reference-Based Cell Annotation

**"Annotate my cells from a reference"** -> Transfer labels from an annotated reference or pretrained model onto query cells, with a calibrated confidence/rejection step.
- Python: `celltypist.annotate()` (pretrained LR) or `scvi-tools` scANVI label transfer
- R: `SingleR()` (correlation to a reference) or `RunAzimuth()` (anchor-based mapping)

## Governing principle

An annotation is a HYPOTHESIS, not a measurement. Reference-based annotators are closed-world: every query cell is forced toward the nearest label the reference contains, so a genuinely novel state gets the nearest wrong label - often with high apparent confidence. Reproducible is not the same as correct; an automated label inherits the reference's annotation errors, granularity, and tissue/donor/disease scope, and propagates them at scale wearing the authority of "automated."
Markers are context-dependent. A marker gene is a conditional statement: "marker X = type Y" means "in this tissue, platform, and processing, X enriches in Y relative to these other cells." A marker in blood may be expressed broadly in tumor; "canonical confirmation" using the same markers that defined the type is circular (recovering the prior, not new evidence). Treat reference labels and marker catalogs (PanglaoDB, CellMarker) as priors to be triangulated, never ground truth.
Before naming a new cell type, triage the four-way confusion in decreasing frequency: (1) doublets - two cell types summed, co-expressing mutually exclusive lineage markers; (2) low-quality/dying - high mito %, low gene count, ambient-dominated; (3) batch/technical - the cluster maps to one sample/lane/chemistry; (4) ambient-RNA contamination (SoupX/CellBender). Only after excluding all four is "novel cell type" admissible. The field is littered with "novel populations" that were doublets or stress artifacts.

This skill covers automated reference transfer. Manual marker discovery and hand-labeling live in single-cell/markers-annotation; the two are complementary - automate a first pass, confirm with markers, reserve expert curation for the final label and ambiguous populations.

## Choosing an annotation method

| Method | Model | Reference | World | Use when | Fails when |
|--------|-------|-----------|-------|----------|------------|
| CellTypist | Logistic regression (pretrained) | Pretrained immune/cross-tissue models | Closed (+probability) | Immune/PBMC, fast first pass, no R needed | Input not log1p CP10K-normalized; query far from training distribution |
| SingleR | Spearman correlation to reference | celldex bulk or single-cell refs | Closed (+pruning) | Bulk reference available, R workflow, per-cell scoring | Strong platform/chemistry shift vs reference; forces nearest label |
| Azimuth | Supervised PCA + anchor mapping | Curated Seurat atlases (PBMC, lung...) | Closed (+mapping.score) | A curated Azimuth reference matches the tissue | No matching reference; locked to provided atlases |
| scANVI / scArches | Semi-supervised VAE | Annotated atlas + raw counts | Closed (+latent uncertainty) | Strong query batch vs reference; mapping onto a large atlas | Training cost/hyperparameters; raw counts required |
| scmap | Nearest reference centroid/cell | Single-cell reference | Open (explicit unassigned) | An explicit rejection category is needed | Coarser resolution; threshold tuning |
| LLM (GPTCelltype) | Prompted from top markers | None (uses marker list) | Open-ish | Fast hypothesis from a marker table | Hallucination, non-reproducible, never sees expression |

No method escapes the closed-world limit except by an explicit reject/unassigned bin. When methods compete, verify current best practice and reference availability against installed docs before committing.

## Normalization requirements (silent-failure risk)

| Tool | Required input | Wrong input symptom |
|------|----------------|---------------------|
| CellTypist | log1p-normalized to 10,000 counts/cell (CP10K) | Confident but degraded/wrong labels, no error |
| SingleR | log-normalized expression (`logcounts`) | Distorted correlations |
| scANVI/scArches | RAW counts in a layer | Model trains on the wrong likelihood |
| Azimuth | raw counts (SCTransform applied internally) | Mapping QC degrades |

## CellTypist (Python)

**Goal:** Transfer labels from a pretrained model with cluster-level smoothing and a probability for rejection.

**Approach:** Normalize the query to CP10K log1p (the model's expected input), run `annotate` with `majority_voting` to reassign each over-clustered subgroup to its dominant label, then keep a per-cell confidence for filtering.

```python
import scanpy as sc
import celltypist
from celltypist import models

adata = sc.read_h5ad('clustered.h5ad')
adata.X = adata.layers['counts'].copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

models.download_models(model='Immune_All_Low.pkl')
predictions = celltypist.annotate(adata, model='Immune_All_Low.pkl', majority_voting=True)
adata = predictions.to_adata()

adata.obs['cell_type'] = adata.obs['majority_voting']
adata.obs['uncertain'] = adata.obs['conf_score'] < 0.5
```

## SingleR (R)

**Goal:** Assign each cell by correlation to a reference and prune low-confidence calls.

**Approach:** Score each cell's Spearman correlation to reference profiles (per-label score is the 0.8 quantile), assign the max, fine-tune, then prune cells whose delta (assigned-label score minus median) falls >3 MADs below the delta distribution.

```r
library(SingleR)
library(celldex)
library(SingleCellExperiment)

sce <- as.SingleCellExperiment(seurat_obj)
ref <- celldex::HumanPrimaryCellAtlasData()

pred <- SingleR(test = sce, ref = ref, labels = ref$label.main, de.method = 'classic', fine.tune = TRUE)
seurat_obj$SingleR <- pred$labels
seurat_obj$SingleR_pruned <- pred$pruned.labels

plotScoreHeatmap(pred)
plotDeltaDistribution(pred)
```

Use `de.method='classic'` for bulk references and `de.method='wilcox'` for single-cell references. Cells pruned to NA are the rejection set; inspect the delta distribution rather than trusting a hard score cutoff.

## Azimuth (R/Seurat)

**Goal:** Map a query onto a curated reference atlas and transfer hierarchical labels with a mapping score.

**Approach:** Project query cells onto the supervised reference embedding via anchors, transfer l1/l2/l3 labels, and gate by `mapping.score` and `prediction.score`.

```r
library(Seurat)
library(Azimuth)

seurat_obj <- RunAzimuth(seurat_obj, reference = 'pbmcref')
seurat_obj$azimuth <- seurat_obj$predicted.celltype.l2
seurat_obj$azimuth_low_conf <- seurat_obj$predicted.celltype.l2.score < 0.7
```

## Rejection thresholds (calibrate, do not port)

| Tool | Rejection signal | Default-ish |
|------|------------------|-------------|
| SingleR | delta + `pruneScores(nmads=3)` | 3 MADs below delta distribution |
| CellTypist | `conf_score` / `p_thres` | 0.5 |
| scmap | max similarity | < 0.7 unassigned |
| Azimuth/scANVI | mapping.score / latent uncertainty | inspect per dataset |

A hard universal probability cutoff is not principled across models - inspect the score distribution and calibrate per dataset.

## Triage an unexpected cluster (before claiming novelty)

**Goal:** Decide whether a poorly-mapped cluster is a novel type or an artifact.

**Approach:** A whole cluster scoring low (vs scattered low-confidence cells) suggests "not in reference"; rule out doublets, low-quality, batch, and ambient before annotating de novo.

```python
import numpy as np

cluster_conf = adata.obs.groupby('leiden')['conf_score'].median()
suspect = cluster_conf[cluster_conf < 0.5].index.tolist()

qc = adata.obs.groupby('leiden')[['pct_counts_mt', 'n_genes_by_counts', 'predicted_doublet']].mean()
print(qc.loc[suspect])
batch_purity = adata.obs.groupby('leiden')['sample'].agg(lambda s: s.value_counts(normalize=True).max())
print(batch_purity.loc[suspect])
```

High mito or low gene count flags low-quality; doublet rate or co-expressed exclusive lineages flags doublets; near-1 batch purity flags a technical artifact. Only a low-confidence, QC-clean, batch-mixed cluster with coherent de-novo markers is a novel-type candidate.

## Validate predictions with markers

**Goal:** Confirm transferred labels against canonical markers (triangulation, not proof).

**Approach:** Dot-plot lineage markers grouped by predicted label and check the expected on/off pattern; disagreement between automated calls and markers flags cells to re-examine.

```r
canonical <- c('CD3D', 'CD8A', 'MS4A1', 'CD14', 'FCGR3A', 'NKG7', 'FCER1A')
DotPlot(seurat_obj, features = canonical, group.by = 'SingleR') + Seurat::RotatedAxis()
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Confident labels that contradict canonical markers | Closed-world: novel/absent state forced to nearest label | Add a reject bin; annotate de novo; do not trust labels outside the reference's domain |
| CellTypist labels degrade silently | Query not CP10K log1p normalized | Normalize to `target_sum=1e4` then `log1p` before annotate |
| CellTypist returns confident but nonsensical labels | Gene-ID space mismatch (query `var_names` are Ensembl IDs vs symbol-based model); few genes matched | Set `var_names` to gene symbols; check the matched-gene fraction reported by annotate before trusting labels |
| Reference labels look wrong everywhere | Platform/chemistry shift vs reference (domain shift) | Use a batch-modeling mapper (scANVI/scArches) or a matched reference |
| "Novel cell type" turns out artifactual | Doublet / low-quality / batch / ambient not excluded | Run the four-way triage before claiming novelty |
| Fine labels (CD4 Tcm vs Tem) unstable | Granularity finer than data or reference supports | Annotate hierarchically; report coarse labels confidently, fine as hypotheses |
| Two tools disagree on the same cells | Different references/granularity | Report consensus + flag disagreements as ambiguous; curate manually |

## Related Skills

- markers-annotation - Manual marker discovery and hand-labeling that complements automated transfer
- clustering - Cluster cells before annotating
- preprocessing - Normalize correctly for each annotator's expected input
- batch-integration - Reference mapping vs de-novo integration; closed-world caveats
- differential-abundance - Test whether annotated cell-type proportions changed between conditions
- pathway-analysis/go-enrichment - Functionally characterize a de-novo / novel population

## References

- Aran et al. 2019, Nat Immunol 20:163-172 - SingleR correlation-based reference annotation with delta-based pruning.
- Dominguez Conde et al. 2022, Science 376:eabl5197 - CellTypist logistic-regression cross-tissue immune annotation.
- Hao et al. 2021, Cell 184(13):3573-3587 - Azimuth / weighted-NN reference mapping and label transfer.
- Xu et al. 2021, Mol Syst Biol 17(1):e9620 - scANVI semi-supervised annotation with calibrated uncertainty.
- Kiselev, Yiu & Hemberg 2018, Nat Methods 15:359-362 - scmap projection with an explicit unassigned category.
- Hou & Ji 2024, Nat Methods 21(8):1462-1465 - GPT-4 / GPTCelltype marker-based annotation and its hallucination/reproducibility caveats.
<!-- END FILE: single-cell/cell-annotation/SKILL.md -->

## 子目录：single-cell/cell-communication

<!-- BEGIN FILE: single-cell/cell-communication/SKILL.md -->
---
name: bio-single-cell-cell-communication
description: Infers ligand-receptor cell-cell communication from scRNA-seq with a consensus-first workflow (LIANA), plus CellPhoneDB specificity tests, CellChat pathway probabilities, and NicheNet downstream ligand-activity. Use when ranking ligand-receptor interactions between cell types, comparing communication across conditions, asking which ligand drives a receiver response, or deciding which CCC method and resource to trust.
tool_type: mixed
primary_tool: LIANA
---

## Version Compatibility

Reference examples tested with: liana 1.2+, CellChat 2.1+, cellphonedb 5.0+, nichenetr 2.1+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Cell-Cell Communication Analysis

**"Find which cell types signal to each other"** -> Score ligand-receptor pairs from co-expression in sender and receiver populations, rank them, and assess specificity or downstream effect.
- Python: `liana.mt.rank_aggregate()` (consensus default), `cellphonedb` (permutation specificity)
- R: `CellChat::computeCommunProb()` (pathway probability), `nichenetr::predict_ligand_activities()` (downstream mechanism)

## Governing Principle

Every ligand-receptor output is a co-expression PROXY, not proof of signaling. Co-expression is neither necessary nor sufficient: receptor mRNA is not a responsive surface protein (desensitization, internalization, decoy receptors, missing co-receptors), a ligand must be secreted or proteolytically cleaved and activated to act, and spatial proximity is unobserved in dissociated data so the two cell types may never have been adjacent. Methods are DISCORDANT because they estimate DIFFERENT quantities, not because of noise: CellPhoneDB tests expression SPECIFICITY (label permutation), CellChat tests a mass-action PROBABILITY (magnitude + Hill saturation), NATMI/Connectome score MAGNITUDE, and there is no monotone mapping between these rankings, so top-N lists genuinely differ on identical input. The choice of RESOURCE (the L-R database) can move results as much as or more than the choice of method (Dimitrov 2022). Default to a CONSENSUS (LIANA `rank_aggregate`), run a resource-sensitivity check, treat every interaction as a hypothesis, and validate orthogonally (downstream TF/pathway activity, receptor protein by CITE-seq, spatial co-localization, or perturbation). NicheNet asks a distinct, better-grounded question (which ligand explains the receiver's DE response) but depends on a clean receiver gene set and a static, cell-type-agnostic prior network.

## Method Decision Table

| Method | Tests what / null | Use when | Fails when |
|--------|-------------------|----------|------------|
| LIANA `rank_aggregate` | Consensus rank over many scoring functions; reports magnitude AND specificity ranks | Robust default; hedge against discordance; vary resource to test sensitivity | Treated as ground truth; top-N read as stable (tail of ranks is flat, membership is unstable to subsampling/re-clustering) |
| CellPhoneDB v5 | Expression SPECIFICITY; permutes cluster labels, asks if mean L+R expression exceeds random labelling | Permutation p-values, rigorous multi-subunit complexes (limiting subunit), human, spatial microenvironments / CellSign TF add-on | Mouse data (human-only DB, ortholog mapping errors); abundance drives the null so dominant clusters over-call; magnitude ignored |
| CellChat v2 | Communication PROBABILITY; law-of-mass-action + Hill saturation, cofactor terms, trimean expression | Pathway-level summaries, sender/receiver/mediator roles, cofactor modeling, cross-condition comparison, fewer high-confidence calls | Sparse/lowly expressed genes dropped by conservative trimean; interaction COUNTS compared across datasets without normalization |
| NATMI / Connectome | MAGNITUDE; expression product (NATMI adds a specificity edge weight) | A simple, fast magnitude score; component of LIANA consensus | Used alone as "communication" - pure magnitude rewards ubiquitous high genes |
| NicheNet | Downstream LIGAND-ACTIVITY; ranks ligands by AUPR between predicted regulatory targets and the receiver's observed DE genes | The question is mechanism: which ligand best explains THIS receiver response | Receiver gene set is noisy/batch-confounded; prior network is static and cell-type-agnostic so context-specific wiring is missed; not a de-novo who-talks-to-whom tool |

Methods evolve; before committing, verify current best practice and the default resource against the installed package docs (LIANA NEWS, CellChatDB version, cellphonedb-data release).

For communication PROGRAMS varying across many samples/conditions/time, decompose with Tensor-cell2cell (commonly run as LIANA -> Tensor-cell2cell) rather than comparing raw counts; for comparison at single-cell resolution without cluster averaging, use Scriabin, which recovers edges lost to agglomeration.

## Spatial-Aware Methods (proximity != interaction)

In dissociated scRNA-seq, proximity is UNKNOWN - only spatial methods constrain by physical distance, and even then they demonstrate spatially-coherent co-expression under modeling assumptions, not binding.

| Method | Approach | Caveat |
|--------|----------|--------|
| Squidpy `sq.gr.ligrec` | CellPhoneDB-style permutation on spatial coordinates | Visium spots hold multiple cells -> "co-expression" can be two cells in one spot; deconvolve first |
| COMMOT | Collective optimal transport over a distance cost with a hard diffusion radius | Radius and cost kernel are unvalidated hyperparameters; run a sensitivity analysis over the radius |
| CellChat v2 spatial | Mass-action probability constrained by spatial distance | Same trimean conservatism; distance scaling is a modeling choice |
| LIANA+ bivariate | Local bivariate (Moran's-style) L-R co-occurrence in space | Tests spatial co-distribution, confounded by shared niche regulation; not directed signaling |

## Confounds That Mimic Signaling

| Confound | How it manufactures a fake interaction | Mitigation |
|----------|----------------------------------------|------------|
| Ambient RNA | Soup of highly expressed secreted genes (hemoglobin, albumin, cytokines) leaks into every cluster, inflating the SECRETED-ligand half of pairs and creating "universal senders" | Decontaminate (SoupX/DecontX/CellBender) before CCC, especially for secreted ligands |
| Cell-type abundance | Larger clusters give a tighter permutation null and smaller p-values, so the dominant type becomes the hub of every network | Down-sample or check that interaction counts do not simply track cluster sizes |
| Sequencing depth | Depth differences across samples change detected genes and scores, conflating technical with biological signal | Run on integrated counts; normalize depth before cross-condition comparison |
| Dissociation stress | Enzymatic dissociation induces FOS, JUN, JUNB, EGR1, HSPA1A/B, DUSP1 - several are bona fide ligands, fabricating AP-1 / heat-shock "signaling" | Flag or regress the stress-gene module; consider cold-protease or snRNA-seq |

## Consensus Inference (Default)

**Goal:** Rank ligand-receptor pairs robustly without committing to one method's estimand.

**Approach:** Run LIANA's rank aggregation over many scoring functions on one input and one resource, then read BOTH the magnitude and specificity ranks (a pair can score high on one and low on the other). CCC needs >=2 cell types in `groupby`; a single group yields only autocrine self-edges, not intercellular signaling.

```python
import liana as li
import scanpy as sc

adata = sc.read_h5ad('adata_annotated.h5ad')

# expr_prop=0.1 drops pairs expressed in <10% of a cluster (sparse-noise floor)
# n_perms=1000 builds the specificity null; use_raw=False uses log-normalized .X
li.mt.rank_aggregate(adata, groupby='cell_type', resource_name='consensus',
                     expr_prop=0.1, use_raw=False, n_perms=1000, verbose=True)

res = adata.uns['liana_res']
# rank_aggregate yields magnitude_rank and specificity_rank (NOT a single 'liana_rank')
robust = res[(res['specificity_rank'] < 0.05) & (res['magnitude_rank'] < 0.05)]
```

## Resource-Sensitivity Check

**Goal:** Establish that a finding is not an artifact of one L-R database.

**Approach:** Hold the method fixed and re-run with a second resource; a pair that survives both resources is robust, one that flips is not.

```python
from liana.method import cellphonedb

for resource in ['consensus', 'cellphonedb', 'cellchatdb']:
    cellphonedb(adata, groupby='cell_type', resource_name=resource,
                expr_prop=0.1, use_raw=False, key_added=f'cpdb_{resource}', verbose=False)
# Compare top pairs across adata.uns['cpdb_consensus'] / 'cpdb_cellphonedb' / 'cpdb_cellchatdb'
```

## Specificity Test (CellPhoneDB v5)

**Goal:** Get permutation specificity p-values with rigorous multi-subunit complex handling (human).

**Approach:** Run the statistical method on log-normalized counts plus a cell-type meta table; the permutation null shuffles cluster labels, and complexes require all subunits via the limiting (minimum) subunit.

```python
from cellphonedb.src.core.methods import cpdb_statistical_analysis_method

# threshold=0.1: a gene must be expressed in >=10% of a cluster's cells to count
# iterations=1000: label-permutation null; pvalue=0.05 reports per-pair significance
results = cpdb_statistical_analysis_method.call(
    cpdb_file_path='cellphonedb.zip',          # cellphonedb-data v5 release
    meta_file_path='meta.tsv',                  # barcode -> cell_type
    counts_file_path='counts_normalized.h5ad',  # normalized, NOT scaled
    counts_data='hgnc_symbol',
    threshold=0.1, iterations=1000, pvalue=0.05,
    score_interactions=True, threads=4, output_path='cpdb_out')
# DEG-driven escape from one-vs-rest: cpdb_degs_analysis_method.call(..., degs_file_path=...)
```

## Pathway Probability (CellChat v2)

**Goal:** Summarize communication at the signaling-pathway level with sender/receiver roles.

**Approach:** Build the object, pick a database subset, identify over-expressed interactions, compute the mass-action probability with trimean, filter tiny populations, aggregate to pathways, then compute centrality for role analysis. Order matters.

```r
library(CellChat)

cellchat <- createCellChat(object = seurat_obj, group.by = 'cell_type')
cellchat@DB <- CellChatDB.human   # or CellChatDB.mouse; subsetDB(..., search='Secreted Signaling') to restrict
cellchat <- subsetData(cellchat)
cellchat <- identifyOverExpressedGenes(cellchat)
cellchat <- identifyOverExpressedInteractions(cellchat)
cellchat <- computeCommunProb(cellchat, type = 'triMean')   # trimean ~25% truncated mean: conservative
cellchat <- filterCommunication(cellchat, min.cells = 10)   # drop populations under 10 cells
cellchat <- computeCommunProbPathway(cellchat)
cellchat <- aggregateNet(cellchat)
cellchat <- netAnalysis_computeCentrality(cellchat, slot.name = 'netP')   # sender/receiver/mediator roles
# Viz: netVisual_aggregate(signaling='WNT'), netVisual_bubble(), netAnalysis_signalingRole_heatmap()
```

## Downstream Ligand-Activity (NicheNet)

**Goal:** Identify which sender ligand best explains the receiver's observed transcriptional response - the distinct, better-grounded question.

**Approach:** Define a receiver gene set of interest (DE genes from a condition contrast), restrict to ligands expressed in senders with receptors expressed in the receiver, and rank ligands by how well their predicted regulatory targets recover that gene set (AUPR).

```r
library(nichenetr)
library(Seurat)
library(tidyverse)

ligand_target_matrix <- readRDS('ligand_target_matrix.rds')
lr_network <- readRDS('lr_network.rds')

# Receiver gene set: garbage in -> garbage out; a noisy/batch-confounded DE list invalidates the ranking
geneset_oi <- FindMarkers(seurat_obj, ident.1 = 'activated_T', ident.2 = 'naive_T') %>%
    filter(p_val_adj < 0.05, avg_log2FC > 0.5) %>% rownames()
background <- get_expressed_genes('T_cell', seurat_obj, pct = 0.10)

expressed_ligands <- intersect(unique(lr_network$from), get_expressed_genes(c('Macrophage', 'Dendritic'), seurat_obj, 0.10))
expressed_receptors <- intersect(unique(lr_network$to), background)
potential_ligands <- lr_network %>% filter(from %in% expressed_ligands, to %in% expressed_receptors) %>% pull(from) %>% unique()

ligand_activities <- predict_ligand_activities(
    geneset = geneset_oi, background_expressed_genes = background,
    ligand_target_matrix = ligand_target_matrix, potential_ligands = potential_ligands)

# Current model ranks by aupr_corrected (AUPR is the headline metric; v1 used pearson)
best_ligands <- ligand_activities %>% top_n(30, aupr_corrected) %>% arrange(-aupr_corrected) %>% pull(test_ligand)
```

## Threshold and Permutation Rationale

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| `expr_prop` / `threshold` | 0.10 | A gene expressed in <10% of a cluster is mostly dropout; below this, scores are noise - but real low-abundance signaling is also discarded (the "not necessary" side of the proxy) |
| `n_perms` / `iterations` | 1000 | Stable label-permutation p-values; 100 is fine for exploration, 1000 for reporting; the p-value is about label shuffling, not binding |
| `min.cells` (CellChat) | 10 | Populations under ~10 cells give unstable mean expression and inflated probabilities |
| trimean (CellChat) | type='triMean' | 25% truncated mean is conservative, yielding fewer, higher-confidence calls than CellPhoneDB's mean |
| `aupr_corrected` top-N | 30 | NicheNet ligand cutoff is a display choice, not a significance threshold; inspect the activity-score elbow |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `KeyError: 'liana_rank'` | `rank_aggregate` outputs `magnitude_rank` and `specificity_rank`, not a single combined rank | Filter on `specificity_rank` and/or `magnitude_rank` |
| One dominant cluster is the hub of every network | Abundance drives the permutation null; ambient RNA inflates its secreted ligands | Decontaminate ambient RNA, down-sample, check counts vs cluster size |
| Findings flip when the database changes | Resource choice moves results as much as method (Dimitrov 2022) | Report the resource and show the key pair survives >=2 resources |
| Contact-dependent pair (Notch-DLL, ephrin) called between non-adjacent types | Membrane-bound ligands scored as if secreted; no geometry in dissociated data | Restrict to secreted signaling or use a spatial method with proximity |
| AP-1 / heat-shock "stress signaling" everywhere | Dissociation-induced FOS/JUN/HSPA modules treated as ligands | Flag/regress the stress module before scoring |
| NicheNet ligand ranking looks random | Receiver gene set is noisy or batch-confounded; or pathway is inactive in that lineage (static prior) | Clean the DE contrast; treat top ligands as "consistent with the response under a generic prior" |
| Mouse CellPhoneDB run returns almost nothing | CellPhoneDB DB is human-only | Map orthologs or use CellChatDB.mouse / LIANA `mouseconsensus` |
| More interactions claimed in condition B than A | Interaction counts scale with cell number and depth | Compare score magnitudes or use CellChat differential / Tensor-cell2cell, not raw counts |

## Related Skills

- single-cell/cell-annotation - Cell-type labels define senders and receivers; annotation resolution is a hidden CCC hyperparameter
- single-cell/clustering - Cluster granularity changes who is "specific"; fix it before running CCC
- single-cell/doublet-detection - Doublets create fake co-expressing cells that masquerade as senders-receivers
- single-cell/preprocessing - Ambient-RNA decontamination and stress-gene handling happen here, before CCC
- single-cell/metabolite-communication - Metabolite-mediated CCC (enzyme-sensor) as the doubly-inferred counterpart to ligand-receptor
- spatial-transcriptomics/spatial-communication - Proximity-constrained CCC when spatial coordinates are available
- pathway-analysis/go-enrichment - Functional enrichment of NicheNet target genes or interacting receptors
- differential-expression/deseq2-basics - Pseudobulk DE to build the receiver gene set NicheNet requires

## References

- Vento-Tormo R, Efremova M, et al. Single-cell reconstruction of the early maternal-fetal interface in humans. Nature 563:347-353 (2018). [original CellPhoneDB]
- Efremova M, Vento-Tormo M, Teichmann SA, Vento-Tormo R. CellPhoneDB: inferring cell-cell communication from combined expression of multi-subunit ligand-receptor complexes. Nat Protoc 15:1484-1506 (2020). [statistical method]
- Jin S, et al. Inference and analysis of cell-cell communication using CellChat. Nat Commun 12:1088 (2021).
- Browaeys R, Saelens W, Saeys Y. NicheNet: modeling intercellular communication by linking ligands to target genes. Nat Methods 17(2):159-162 (2020).
- Dimitrov D, et al. Comparison of methods and resources for cell-cell communication inference from single-cell RNA-Seq data. Nat Commun 13:3224 (2022). [LIANA, discordance]
- Dimitrov D, et al. LIANA+ provides an all-in-one framework for cell-cell communication inference. Nat Cell Biol 26:1613-1622 (2024).
- Hou R, et al. Predicting cell-to-cell communication networks using NATMI. Nat Commun 11:5011 (2020).
- Cang Z, Nie Q, et al. Screening cell-cell communication in spatial transcriptomics via collective optimal transport [COMMOT]. Nat Methods 20:218-228 (2023).
- Palla G, et al. Squidpy: a scalable framework for spatial omics analysis. Nat Methods 19:171-178 (2022).
- Luo J, et al. ESICCC: evaluation, selection, and integration of cell-cell communication inference methods. Genome Res 33(10):1788-1805 (2023). [benchmark]
- Young MD, Behjati S. SoupX removes ambient RNA contamination from droplet-based single-cell RNA sequencing data. GigaScience 9(12):giaa151 (2020).
- van den Brink SC, et al. Single-cell sequencing reveals dissociation-induced gene expression in tissue subpopulations. Nat Methods 14(10):935-936 (2017).
<!-- END FILE: single-cell/cell-communication/SKILL.md -->

## 子目录：single-cell/clustering

<!-- BEGIN FILE: single-cell/clustering/SKILL.md -->
---
name: bio-single-cell-clustering
description: Dimensionality reduction and graph-based clustering for single-cell RNA-seq with Scanpy (Python) and Seurat (R). Resolves which algorithm to use (Leiden vs Louvain), how many PCs and neighbors to set, how to sweep and validate resolution, when a split is over-clustering, and why post-clustering marker p-values are not valid inference. Use when clustering cells, choosing a clustering resolution, deciding whether two clusters are one population, building a UMAP/tSNE, or judging whether clusters are real.
tool_type: mixed
primary_tool: Seurat
---

## Version Compatibility

Reference examples tested with: scanpy 1.10+, Seurat 5.0+, anndata 0.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Single-Cell Clustering

**"Cluster my cells"** -> Build a k-nearest-neighbor graph in PCA space, partition it into communities, and embed in 2D for display.
- Python: `sc.pp.neighbors` + `sc.tl.leiden` + `sc.tl.umap` (Scanpy)
- R: `FindNeighbors` + `FindClusters` + `RunUMAP` (Seurat)

## Governing Principle

Resolution is not a truth knob, and clusters are not discoveries. Graph-based clustering partitions a kNN graph built in PCA space; there is no ground truth, no "correct" number of clusters, and resolution selects a scale of description rather than revealing one. Clusters are hypotheses that must be validated by markers, stability, and (where claims are made) a significance test before any partition is named a cell population. Over-clustering is the default failure mode: any homogeneous blob can be bisected, and a higher resolution will always split it further. UMAP/tSNE distances, cluster sizes, and apparent gaps are artifacts of a non-linear neighbor-preserving objective and are not metric data (Chari & Pachter 2023) - cluster on the graph, never on embedding coordinates. The deepest trap: clustering chooses labels to maximize between-group separation, so running a marker test on those same clusters tests a hypothesis built from the data used to test it (double-dipping), and the resulting p-values are not merely inflated, they are invalid inference.

## Leiden vs Louvain

Leiden is the current default for graph community detection because Louvain can return internally disconnected communities (Traag 2019). Seurat still ships Louvain as its default algorithm; Scanpy uses Leiden but is mid-migration between backends. Methodology evolves - verify the current default and backend against the installed package docs before pinning a pipeline.

| Method | Model / assumption | Use when | Fails when |
|--------|-------------------|----------|------------|
| Leiden | Modularity/CPM optimization with a refinement phase guaranteeing connected communities | Default for scRNA-seq; reproducibility matters; large graphs (faster) | Backend/iteration count left unpinned -> silently different labels across Scanpy versions |
| Louvain | Modularity optimization without refinement | Legacy pipelines; Seurat default (`algorithm=1`) | Can yield internally disconnected communities; superseded by Leiden (Traag 2019) |
| SLM | Smart Local Moving refinement | Seurat option (`algorithm=3`) for tighter modularity optima | Slower; rarely needed over Leiden |

Scanpy 1.10 backend migration (pin for reproducibility): `sc.tl.leiden` still defaults to the `leidenalg` backend through 1.10-1.12 and emits a FutureWarning that the default will switch to igraph. The exact flip version is unconfirmed, so pin the backend explicitly: `sc.tl.leiden(adata, flavor='igraph', n_iterations=2, directed=False)`. Switching backend or `n_iterations` changes the labels - a pipeline that pins neither is non-reproducible across versions. Seurat's Leiden (`algorithm=4`) requires the `leidenalg` Python module via reticulate, which is why most Seurat pipelines still run Louvain.

## Parameter Reference

`n_pcs` dominates the result far more than `n_neighbors` and is the largest under-tuned lever - too few collapses real structure, too many reintroduces technical noise.

| Parameter | Typical range | Rationale | Validation |
|-----------|--------------|-----------|------------|
| n_pcs | 30-50 (check elbow) | Captures biological variance while denoising; effect dwarfs n_neighbors | Elbow plot; cluster stability across nearby n_pcs values |
| n_neighbors | 10-30 (15 default) | Higher = smoother, fewer fine clusters; lower = more local, fragmented | Secondary lever; vary only after n_pcs is set |
| resolution | 0.2-2.0 (sweep, do not fix) | Higher = more, smaller clusters; has no biological meaning | clustree across the sweep; marker check; significance test |
| min_dist (UMAP) | 0.1-0.5 | Visualization only; lower = tighter visual clusters | Affects display, never the partition |

Resolution is an unidentifiable nuisance parameter: it cannot be validated internally (no ground truth), so tuning it until clusters "match known cell types" is confirmation bias laundered as analysis. Sweep a range, visualize cell flow with clustree, and pick the coarsest level whose populations are defensible by orthogonal evidence - label finer splits as hypotheses.

## Cluster Cells with Scanpy

**Goal:** Reduce dimensions, build the neighbor graph, partition with Leiden, and embed for display.
**Approach:** PCA -> kNN graph on a chosen `n_pcs` -> Leiden with a pinned backend -> UMAP.

```python
import scanpy as sc

adata = sc.read_h5ad('preprocessed.h5ad')

sc.tl.pca(adata, n_comps=50, svd_solver='arpack')
sc.pl.pca_variance_ratio(adata, n_pcs=50, log=True)  # elbow to choose n_pcs

sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.leiden(adata, resolution=0.5, flavor='igraph', n_iterations=2, directed=False)
adata.obs['leiden'].value_counts()

sc.tl.umap(adata, min_dist=0.3)
sc.pl.umap(adata, color=['leiden', 'CD3D', 'MS4A1', 'CD14'])
```

## Sweep and Validate Resolution

**Goal:** Choose a defensible granularity instead of a single tuned-to-taste resolution.
**Approach:** Cluster across a resolution range, inspect cell flow (clustree), and confirm each cluster carries distinct markers.

```python
import scanpy as sc

for res in [0.2, 0.4, 0.6, 0.8, 1.0]:
    sc.tl.leiden(adata, resolution=res, key_added=f'leiden_r{res}',
                 flavor='igraph', n_iterations=2, directed=False)
    print(res, adata.obs[f'leiden_r{res}'].nunique(), 'clusters')

sc.pl.umap(adata, color=['leiden_r0.2', 'leiden_r0.6', 'leiden_r1.0'], ncols=3)
# clustree (R) or sc.tl.dendrogram for flow across resolutions; merge clusters
# whose top markers are indistinguishable -> they are one population over-split
```

## Cluster Cells with Seurat

**Goal:** Run PCA, build the SNN graph, partition, and embed in Seurat.
**Approach:** RunPCA -> FindNeighbors on chosen dims -> FindClusters (sweep resolutions) -> RunUMAP.

```r
library(Seurat)

seurat_obj <- readRDS('preprocessed.rds')
seurat_obj <- RunPCA(seurat_obj, npcs = 50, verbose = FALSE)
ElbowPlot(seurat_obj, ndims = 50)  # choose dims

seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30)
seurat_obj <- FindClusters(seurat_obj, resolution = c(0.2, 0.4, 0.6, 0.8, 1.0))
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30)

library(clustree)
clustree(seurat_obj, prefix = 'RNA_snn_res.')  # cell flow across the sweep
DimPlot(seurat_obj, reduction = 'umap', label = TRUE)
```

`FindClusters` defaults to Louvain (`algorithm=1`); pass `algorithm=4` for Leiden (requires the leidenalg Python module). Resolutions stored as `RNA_snn_res.<r>` columns feed clustree directly.

## Subclustering

**Goal:** Resolve fine states inside a coarse cluster without importing global axes.
**Approach:** Subset the cluster, then recompute HVGs, PCA, and the kNN graph on the subset.

```python
sub = adata[adata.obs['leiden'] == '3'].copy()
sc.pp.highly_variable_genes(sub, n_top_genes=2000)
sub = sub[:, sub.var.highly_variable]
sc.pp.scale(sub, max_value=10)
sc.tl.pca(sub, n_comps=30)
sc.pp.neighbors(sub, n_neighbors=15, n_pcs=20)
sc.tl.leiden(sub, resolution=0.4, flavor='igraph', n_iterations=2, directed=False)
```

Reusing the global PCA imports axes uninformative within a homogeneous subset and manufactures artifactual sub-splits. Subclustering compounds double-dipping (cells selected twice), so stop when splits lose distinct markers or fail a significance test - not when resolution can technically still split (it always can).

## Validating That Clusters Are Real

Stability and significance are separate questions, and both differ from biological reality.

- Stability (necessary, not sufficient): bootstrap cells, re-cluster, measure per-cluster label agreement (Jaccard >= ~0.6-0.7 = stable). A perfectly reproducible split can still be technical - driven by cell-cycle phase, dissociation stress (FOS/JUN/HSPA1A), mitochondrial fraction, ambient RNA, or batch. Stable does not mean real.
- Significance (whether a split is two populations or one): scSHC (Grabski 2023) and CHOIR (2025) test each split under a null with error control; a failed split is over-clustering and the clusters should be merged.
- Biological-vs-technical adjudication: check that a split survives regressing out cycle/mito and carries non-stress markers before claiming a population.

Double-dipping (post-clustering inference is invalid, not just inflated): `rank_genes_groups`/`FindAllMarkers` p-values are conditioned on a clustering chosen to maximize separation, so under one homogeneous population they do not follow their nominal null - type-I error approaches 1 as resolution rises, and BH correction does nothing because the p-values are invalid before correction. Use these marker tests for ranking and labeling only. To make a defensible claim that a cluster is a distinct population, pair a cluster significance test (scSHC/CHOIR) with a double-dipping-robust DE method (ClusterDE's synthetic null, or count splitting where the noise model holds - Poisson thinning on overdispersed counts silently reinstates the bias). See markers-annotation for marker testing and the pseudobulk path for cross-condition DE.

## UMAP and tSNE Are Visualization Only

Cluster on the graph or PCA, never on embedding coordinates. Inter-cluster distances, relative sizes, and apparent gaps in UMAP/tSNE are artifacts of the embedding objective and are not metric (Chari & Pachter 2023) - do not read them as lineage, evolutionary distance, or population separation. "Cells far apart in UMAP are more different" and "UMAP preserves global structure" are folklore; PCA initialization plus high perplexity makes tSNE less misleading but does not make distances trustworthy (Kobak & Berens 2019). Embeddings display graph-derived labels; back every structural claim with the graph, validly-tested markers, or quantitative analysis in PCA space.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| One giant blob, no structure | Too few HVGs or wrong n_pcs (too few), or the sample is genuinely one cell type | Increase HVGs (~2000), raise n_pcs, check the elbow plot; if markers stay uniform across a resolution sweep, the blob may be a single real population, not a parameter bug |
| Far too many clusters | Resolution too high; n_pcs too high (noise) | Lower resolution; sweep with clustree; reduce n_pcs to the elbow |
| Adjacent clusters share all top markers | Over-clustering one population | Merge them; lower resolution; significance-test the split (scSHC/CHOIR) |
| Labels change between runs/versions | Leiden backend or n_iterations unpinned | Pin `flavor='igraph', n_iterations=2, directed=False`; set random_state |
| A cluster maps to one sample/lane only | Batch effect, not biology | Integrate batches first (batch-integration); inspect QC covariates |
| A "stable" cluster of stress/cycle genes | Technical split (dissociation, cycle, mito) | Regress out cycle/mito or score and exclude; require non-stress markers |
| Cluster expresses two lineages' markers | Doublets clustering together | Run doublet detection before clustering (doublet-detection) |
| Marker p-values quoted as proof clusters are real | Double-dipping (selective inference) | Use markers for ranking only; validate with scSHC/CHOIR + ClusterDE |

## Related Skills

- preprocessing - QC, normalization, and HVG selection that must precede clustering
- doublet-detection - Remove doublets before clustering so they do not form fake intermediate clusters
- batch-integration - Integrate batches before clustering when a cluster tracks a single sample
- markers-annotation - Find and test markers per cluster (with the double-dipping caveat)
- cell-annotation - Assign cell-type identities to validated clusters
- single-cell/differential-abundance - Test whether cluster proportions shift across conditions
- data-visualization/dimensionality-reduction-plots - Publication-quality UMAP/tSNE/PCA figures
- pathway-analysis/go-enrichment - Interpret per-cluster marker sets

## References

- Traag, Waltman & van Eck (2019). From Louvain to Leiden: guaranteeing well-connected communities. Sci Rep 9:5233.
- Chari & Pachter (2023). The specious art of single-cell genomics. PLoS Comput Biol 19(8):e1011288.
- Kobak & Berens (2019). The art of using t-SNE for single-cell transcriptomics. Nat Commun 10:5416.
- Grabski, Street & Irizarry (2023). Significance analysis for clustering with single-cell RNA-sequencing data. Nat Methods 20:1196-1202.
- Neufeld, Gao, Popp, Battle & Witten (2024). Inference after latent variable estimation for single-cell RNA-seq (count splitting). Biostatistics 25(1):270-287.
- Zappia & Oshlack (2018). Clustering trees: a visualization for evaluating clusterings at multiple resolutions. GigaScience 7(7):giy083.
<!-- END FILE: single-cell/clustering/SKILL.md -->

## 子目录：single-cell/cnv-inference

<!-- BEGIN FILE: single-cell/cnv-inference/SKILL.md -->
---
name: bio-single-cell-cnv-inference
description: Infer large-scale copy-number alterations from tumor single-cell or single-nucleus RNA-seq to separate malignant from normal cells and call subclones, using inferCNV, copyKAT, Numbat, and SCEVAN. Use when separating malignant from normal cells in a tumor scRNA-seq dataset, inferring chromosome-arm CNVs or aneuploidy from expression, calling tumor subclones from single cells, choosing a CNV-inference method (reference-based vs reference-free, expression-only vs allele-aware), or deciding which cells are tumor before downstream analysis.
tool_type: r
primary_tool: inferCNV
---

## Version Compatibility

Reference examples tested with: inferCNV 1.18+, copyKAT 1.1+, numbat 1.4+, SCEVAN 1.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Copy-Number Inference from Single-Cell RNA-seq

**"Which cells are tumor, and what CNVs and subclones do they carry?"** -> Estimate large-scale copy-number from smoothed expression across genomic windows, compare against a normal reference, and cluster cells into malignant vs normal and into subclones.
- R (reference-based, expression-only): `inferCNV` - smooth expression along chromosomes against a defined normal reference, optional HMM for discrete CNV states
- R (reference-free, expression-only): `copyKAT`, `SCEVAN` - estimate the diploid baseline internally and segment, then classify aneuploid vs diploid
- R (haplotype-aware, allele + expression): `Numbat` - add phased B-allele frequency for the best subclone and copy-neutral-LOH resolution

## Governing principle

Averaged expression over a genomic window is a PROXY for DNA copy number, not a measurement of it. A chromosome-arm gain raises the average expression of the many genes sitting on that arm, and a loss lowers it, so smoothing expression across long runs of contiguous genes reconstructs a coarse copy-number landscape. Three consequences follow and drive every decision. First, the signal is noisy and indirect: it must be smoothed over windows of dozens to hundreds of neighboring genes, and its resolution is chromosome-arm or large-segment (around 5 Mb), never focal genes or exons - this is the hard line separating it from DNA-based copy-number (copy-number/cnvkit-analysis, copy-number/gatk-cnv), which measures DNA read depth and resolves focal amplifications and deletions. Second, the value is RELATIVE: copy-number is only defined against a copy-neutral baseline, so a NORMAL reference is required, and the choice of that reference is the single most consequential decision - a wrong or mismatched reference fabricates CNVs out of ordinary cell-type expression differences. Third, calling a cell malignant is a CLUSTERING decision on this noisy proxy, so it is a hypothesis that needs orthogonal support (lineage markers, mutations, allele evidence), and subclone calls are even softer hypotheses.

Tumor CNV profiles are patient-PRIVATE, so CNV inference runs PER SAMPLE / per patient. Integrating or batch-correcting cells across patients before inference mixes distinct private karyotypes and erases the per-patient signal the analysis depends on (single-cell/batch-integration notes this). Integrate across patients only for shared transcriptional-state analysis, never as input to CNV calling.

CNV-quiet tumors are invisible to this approach. Many hematologic and low-grade tumors carry little large-scale CNV, so expression-based inference returns a near-flat profile - absence of inferred CNV is NOT evidence that cells are normal, and a confident malignant call then requires allele evidence or orthogonal markers. Balanced whole-genome doubling is invisible for the same reason and to all expression methods, not just copyKAT: per-cell library-size normalization removes a uniform ploidy multiple, so a 4N WGD reads copy-neutral against a 2N reference for inferCNV and Numbat's expression channel alike, and only allele or ploidy evidence reveals it.

## Choosing a CNV-inference method

| Method | Model / assumption | Reference | Allele-aware | Use when | Fails when |
|--------|--------------------|-----------|--------------|----------|------------|
| inferCNV | Smooth expression along chromosomes vs a normal reference; optional HMM for discrete states | Reference-based (needs normal cells) | No | A clean in-sample normal reference exists; want interpretable arm-level heatmap + HMM states | No trustworthy reference; CNV-quiet tumor; needs focal resolution |
| copyKAT | Bayesian segmentation + hierarchical clustering + GMM; estimates diploid baseline internally | Reference-free (optional known normals) | No | No reference cells annotated; want a quick aneuploid-vs-diploid call at ~5 Mb | Mostly-aneuploid sample with no diploid baseline; whole-genome doubling confuses the root |
| SCEVAN | Variational multichannel segmentation sharing breakpoints across a clone | Reference-free | No | Want automatic malignant/non-malignant + subclones in one call | Same baseline ambiguity as copyKAT; very sparse data |
| Numbat | Joint expression + phased B-allele frequency + population haplotypes; iterative phylogeny | Reference (expression) + population phasing | Yes | Best subclone resolution needed; copy-neutral LOH matters; allele counts obtainable | No BAM/phasing available; very low SNP coverage (shallow or snRNA) |

Reference-based (inferCNV, Numbat expression side) is the most reliable when a clean normal reference is available; reference-free (copyKAT, SCEVAN) trades that for not needing one but is vulnerable to baseline ambiguity. Expression-only methods (inferCNV, copyKAT, SCEVAN) are simpler and need only counts; the allele-aware method (Numbat) is the most powerful for subclones and copy-neutral events but requires per-cell allele counts and phasing. Run an expression method to get the malignant/normal split, then Numbat when subclone structure is the question, and reconcile. When methods compete, verify current best practice against the installed package documentation before committing to one.

## Choosing the normal reference

**Goal:** Pick a copy-neutral baseline that defines what "no CNV" looks like, since the reference choice determines whether the inferred CNVs are real or artifacts.

**Approach:** Prefer non-malignant cells from the SAME sample (T cells, B cells, myeloid, endothelial, fibroblasts identified by lineage markers) because they share the patient, protocol, and ambient-RNA background; fall back to an external normal only when no in-sample normals exist, and expect batch artifacts.

The reference cells must be confidently non-malignant and abundant enough for a stable baseline mean: aim for tens to hundreds of reference cells, not a handful, because a few cells give a noisy baseline that fabricates CNVs in every observation cell. A reference that is itself a malignant or stressed population, or a single mismatched cell type, will make every other cell look aneuploid relative to it. The reference must also MATCH the tumor's sex: because inferCNV works on expression, X-inactivation dosage-compensates most chrX expression so there is no uniform two-fold chrX shift, but an external or cross-individual normal (including shipped or pooled-donor references) of the opposite sex still fabricates a convincing uniform sex-chromosome CNV through chrY genes present in XY versus near-absent in XX, XIST high in XX versus silent in XY, and the attenuated X-inactivation escape genes - match sexes or drop chrX and chrY before inference. With no annotated normals, use a reference-free method (copyKAT, SCEVAN) rather than guessing a reference; do not pass tumor-contaminated cells as the reference.

## inferCNV - reference-based expression smoothing

**Goal:** Build a chromosome-ordered expression heatmap against a defined normal reference and call discrete CNV states per region.

**Approach:** Assemble a raw counts matrix, a cell-to-group annotation file, and a gene-ordering file with genomic coordinates, name the normal groups as the reference, then run with droplet-appropriate cutoff, denoising, and the HMM.

```r
library(infercnv)

infercnv_obj <- CreateInfercnvObject(
    raw_counts_matrix = 'counts.matrix',
    annotations_file = 'cell_annotations.txt',
    delim = '\t',
    gene_order_file = 'gene_ordering.txt',
    ref_group_names = c('Tcell', 'Myeloid'))

infercnv_obj <- infercnv::run(
    infercnv_obj,
    cutoff = 0.1,
    out_dir = 'infercnv_out',
    cluster_by_groups = TRUE,
    denoise = TRUE,
    HMM = TRUE,
    num_threads = 4)
```

`ref_group_names` lists the normal groups from the annotation file; set it to `NULL` only when no reference exists (less reliable). `cutoff = 0.1` suits 10x and other droplet data; use `cutoff = 1` for full-length Smart-seq. `cluster_by_groups = TRUE` clusters within annotated groups rather than forcing one global tree. The HMM (`HMM_type = 'i6'` default, six copy states; `'i3'` for a simpler deletion/neutral/amplification model) yields per-region discrete states under `out_dir`.

## copyKAT - reference-free aneuploid vs diploid

**Goal:** Classify cells as aneuploid (tumor) or diploid (normal) without an annotated reference, and obtain a per-cell copy-number matrix.

**Approach:** Pass the raw gene-by-cell matrix; copyKAT estimates the diploid baseline by segmentation and clustering, then labels each cell, optionally anchored by any known-normal barcodes.

```r
library(copykat)

res <- copykat(
    rawmat = exp_rawdata,
    id.type = 'S',
    ngene.chr = 5,
    win.size = 25,
    KS.cut = 0.1,
    sam.name = 'tumor1',
    distance = 'euclidean',
    norm.cell.names = '',
    genome = 'hg20',
    n.cores = 4)

pred <- res$prediction
cna <- res$CNAmat
```

`res$prediction$copykat.pred` is `aneuploid`, `diploid`, or `not.defined` per cell; `res$CNAmat` holds smoothed copy-number values in ~220 kb bins (the output bin size; effective detection resolution is still ~5 Mb). `KS.cut` controls segmentation stringency (raise it for fewer, larger segments). Supplying confident normal barcodes via `norm.cell.names` anchors the diploid baseline and improves accuracy when the sample is mostly aneuploid.

## Numbat - haplotype-aware allele + expression

**Goal:** Resolve subclones and copy-neutral LOH by combining smoothed expression with phased B-allele frequencies.

**Approach:** Generate per-cell allele counts and population phasing with the `pileup_and_phase.R` preprocessing script, build an expression reference from matched normals (or the shipped `ref_hca`), then run the joint model.

```bash
Rscript pileup_and_phase.R --label tumor1 --samples tumor1 \
    --bams tumor1.bam --barcodes barcodes.tsv \
    --gmap genetic_map_hg38_withX.txt.gz --snpvcf genome1K.phase3.SNP.vcf \
    --paneldir 1000G_panel/ --outdir numbat_out/ --ncores 8
```

```r
library(numbat)

ref <- aggregate_counts(count_mat_normal, cell_annot)
out <- run_numbat(
    count_mat,
    lambdas_ref = ref,
    df_allele = df_allele,
    genome = 'hg38',
    t = 1e-5,
    ncores = 4,
    plot = TRUE,
    out_dir = 'numbat_out')

nb <- Numbat$new(out_dir = 'numbat_out')
```

`df_allele` is the allele dataframe written by `pileup_and_phase.R` (columns include `cell`, `snp_id`, `CHROM`, `POS`, `AD`, `DP`, `GT`). `lambdas_ref` is a gene-by-cell-type expression reference from `aggregate_counts(count_mat, cell_annot)` where `cell_annot` has `cell` and `group` columns, or the package-shipped `ref_hca`. `t` is the HMM transition probability. The loaded `Numbat` object exposes `clone_post` (clone assignments) and per-cell copy-number posteriors. Numbat needs no paired-normal DNA but does need a BAM and phasing reference.

## Turning the inferCNV heatmap into per-cell malignant calls

**Goal:** Get a per-cell malignant-vs-normal label from inferCNV, which (unlike copyKAT and SCEVAN) returns a heatmap and HMM region states but no automatic per-cell class.

**Approach:** Subcluster the observation cells on their CNV signal and/or compute a per-cell CNV score, then threshold; carry the result onto the cells with `add_to_seurat` and validate the cut against lineage markers and allele/mutation evidence.

```r
infercnv_obj <- infercnv::run(
    infercnv_obj, cutoff = 0.1, out_dir = 'infercnv_out',
    cluster_by_groups = FALSE, analysis_mode = 'subclusters',
    denoise = TRUE, HMM = TRUE, num_threads = 4)

seurat_obj <- infercnv::add_to_seurat(
    seurat_obj = seurat_obj, infercnv_output_path = 'infercnv_out', top_n = 10)

obs <- read.table('infercnv_out/infercnv.observations.txt', header = TRUE, row.names = 1)
cnv_score <- colSums((obs - 1)^2)
malignant <- cnv_score > quantile(cnv_score, 0.5)
```

`analysis_mode = 'subclusters'` (with `cluster_by_groups = FALSE`) partitions the observation cells by CNV signal so a malignant subcluster separates from a copy-neutral one. The per-cell CNV score (sum of squared deviation of the denoised `infercnv.observations.txt` profile from the copy-neutral value, or each cell's correlation to the mean putative-tumor profile) gives a continuous malignancy axis to threshold; `add_to_seurat` writes per-cell and per-chromosome CNA metadata back onto the object for plotting. The malignant/normal cut is a hypothesis: confirm it against lineage markers (single-cell/cell-annotation) and allele or mutation evidence, never treat the threshold as ground truth.

## Threshold and parameter reference

| Parameter | Tool | Default / typical | Rationale |
|-----------|------|-------------------|-----------|
| cutoff | inferCNV | 0.1 (droplet), 1 (Smart-seq) | Drops genes below mean expression; droplet data are sparse so the threshold is lower |
| HMM_type | inferCNV | i6 | Six copy states (0 to 3+) give finer state calls; i3 (del/neutral/amp) is simpler and more robust |
| ref_group_names | inferCNV | named normals | The copy-neutral baseline; NULL only when no reference exists, at a reliability cost |
| ngene.chr | copyKAT | 5 | Minimum genes per chromosome per cell so a cell has signal on each chromosome |
| win.size | copyKAT | 25 | Genes per segment for smoothing; larger windows denoise but blur small events |
| KS.cut | copyKAT | 0.1 | Segmentation stringency; raise for fewer, larger segments in noisy data |
| genome | copyKAT | hg20 | Must match the assembly the gene coordinates came from (hg20 or mm10) |
| t | Numbat | 1e-5 | HMM transition probability; lower favors longer segments |
| resolution (~5 Mb) | all expression methods | ~5 Mb | The floor of expression-based CNV; focal events below this are invisible |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Every cell looks aneuploid, including the immune cells | Reference cells are tumor-contaminated or a mismatched cell type | Re-pick confident non-malignant in-sample normals by lineage markers; do not use a stressed/malignant population as reference |
| Flat profile, no CNVs called, but cells are clearly tumor | CNV-quiet / low-grade tumor, or snRNA sparsity | Absence of CNV is not normality; switch to allele-aware Numbat or confirm malignancy with markers/mutations |
| copyKAT cannot find a diploid baseline / labels almost all aneuploid | Mostly-aneuploid sample with no internal diploid cells, or balanced whole-genome doubling that library-size normalization hides | Supply known-normal barcodes via `norm.cell.names`, or use inferCNV with an external reference; confirm ploidy with allele/DNA evidence since balanced WGD looks copy-neutral to all expression methods |
| Uniform chrX gain/loss and a chrY call across all tumor cells | Reference and tumor are opposite sex (external/shipped/pooled-donor reference) | Match reference and tumor sex, or drop chrX and chrY before inference |
| Recurrent localized segment over 6p, 14q, 22q, or 2p that tracks lineage | High, variable HLA (MHC 6p) and immunoglobulin/TCR expression clusters genomically and mimics a segment, especially with immune references | Mask or distrust segments over HLA and Ig/TCR loci; do not call them CNV |
| Stripe artifacts that track proliferating cells | Cell-cycle and high-expression gene programs mimic CNV | Account for / regress cell cycle, enable denoising, and treat cycle-correlated bands skeptically |
| Subclones from inferCNV/copyKAT do not replicate | Expression-only subclone calls are weak hypotheses | Confirm with Numbat allele evidence or DNA; report subclones as hypotheses |
| CNV signal vanishes after integrating samples | Cross-patient integration erased patient-private karyotypes | Run CNV inference per sample BEFORE any cross-patient integration |
| Genes silently dropped / wrong chromosome bands | Gene-order file or genome build mismatched to the counts | Match `gene_order_file` and `genome` to the same assembly and gene IDs as the matrix |

## Related Skills

- single-cell/preprocessing - QC and normalization that precede CNV inference; ambient RNA and depth affect the proxy
- single-cell/clustering - Provides the cell groups and the malignant-vs-normal clustering the CNV call refines
- single-cell/cell-annotation - Identifies the non-malignant lineages used as the normal reference
- single-cell/batch-integration - Why CNV inference must run per patient before any cross-patient integration
- copy-number/cnvkit-analysis - DNA/WES-based copy-number that measures read depth and resolves focal events, the orthogonal contrast to this expression proxy

## References

- Patel AP et al. 2014, Science 344:1396-1401 - single-cell RNA-seq of glioblastoma; first per-cell CNV estimation from averaged expression.
- Tirosh I et al. 2016, Science 352:189-196 - melanoma scRNA-seq; inferring large-scale CNV from smoothed expression to separate malignant cells (the inferCNV approach).
- Gao R et al. 2021, Nat Biotechnol 39:599-608 - copyKAT; reference-free Bayesian segmentation calling aneuploid vs diploid and subclones at ~5 Mb.
- Gao T et al. 2023, Nat Biotechnol 41:417-426 - Numbat; haplotype-aware joint allele and expression somatic CNV inference from scRNA-seq.
- Muller S et al. 2018, Bioinformatics 34:3217-3219 - CONICS/CONICSmat; arm-level CNV from expression mapped to tumor sub-clones.
- De Falco A et al. 2023, Nat Commun 14:1074 - SCEVAN; variational multichannel segmentation auto-classifying malignant cells and clonal substructure.
<!-- END FILE: single-cell/cnv-inference/SKILL.md -->

## 子目录：single-cell/data-io

<!-- BEGIN FILE: single-cell/data-io/SKILL.md -->
---
name: bio-single-cell-data-io
description: Read, write, create, and convert single-cell objects across AnnData (Python), Seurat (R), and SingleCellExperiment (R). Use when loading 10X Cell Ranger output (raw vs filtered), importing or exporting h5ad/RDS/h5mu/zarr, building AnnData or Seurat objects from matrices, moving objects between Python and R, or debugging lost layers, transposed matrices, or mangled gene names during conversion.
tool_type: mixed
primary_tool: Seurat
---

## Version Compatibility

Reference examples tested with: scanpy 1.10+, Seurat 5.0+, anndata 0.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Single-Cell Data I/O

**"Load my 10X data"** -> Parse a Cell Ranger matrix into an annotated object (cells, genes, counts, metadata).
- Python: `sc.read_10x_mtx()` / `sc.read_10x_h5()` -> AnnData
- R: `Read10X()` / `Read10X_h5()` -> `CreateSeuratObject()`

## Governing Principle

The dominant failure in single-cell I/O is not a crash; it is a silent semantic change to the matrix during read or conversion. Three traps drive almost every lost-data bug.

Orientation is opposite across ecosystems. AnnData is cells x genes (observations on rows, `obs` indexes rows, `var` indexes columns); Seurat and SingleCellExperiment are genes x cells (features on rows, cells on columns). So `adata.X` is the transpose of `LayerData(seu)` and `assay(sce)`. A faithful conversion must transpose AND swap which axis the metadata annotates; getting the transpose right but the metadata axis wrong is the single most common silent conversion bug.

Sparse storage compounds the transpose. R `Matrix::dgCMatrix` is CSC; scanpy conventionally stores `X` as CSR. Transposing a CSR matrix yields CSC for free, so a correct AnnData->Seurat hop involves both a logical transpose and a CSR<->CSC change. Forcing dense (`.toarray()`, `as_dense=` on write) on a 500k-cell x 30k-gene float32 matrix materializes ~60 GB; keep `X` and layers sparse and check with `scipy.sparse.issparse(adata.X)`.

Conversion is lossy by default, and the loss is silent. Cross-ecosystem hops drop `layers`, `obsp`/`varp`, nested `uns`, and coerce categoricals to character/NA. `adata.raw` has its own `var` (its purpose is to survive HVG subsetting) and tools disagree on whether to read `X` or `.raw.X` (`use_raw=`), so a mismatched expectation silently uses the wrong matrix. Always diff slot inventories before and after any cross-ecosystem conversion, and keep the original file.

One more governing fact: the Cell Ranger filtered matrix is cell-CALLED, not ambient-corrected. The widespread claim that the filtered matrix is "decontaminated" is false. Keep the RAW (unfiltered) matrix, because EmptyDrops, SoupX, CellBender, and DecontX all require it and filtered-only storage is irreversible.

## Choosing a Storage Format

| Format | Backing | Use when | Fails / weak when |
|--------|---------|----------|-------------------|
| h5ad (HDF5) | single file | Default single-machine Python I/O and sharing | Not cloud-native; concurrent/partial reads limited |
| zarr (directory of chunks) | object store | Cloud/S3, larger-than-memory, parallel/lazy (Dask), anndata 0.11+ v3 sharding | Many small files awkward on local FS; v2/v3 version skew breaks old readers |
| RDS | single R binary | Seurat-only workflow, full object fidelity in R | R-only; not portable to Python; version-tied |
| h5mu (MuData) | HDF5 | Multimodal (RNA + ADT + ATAC), one AnnData per modality | Less tool support than h5ad; needs `mdata.update()` discipline |
| Loom (HDF5) | single file | Legacy interchange (velocyto, older Seurat) | `write_loom(write_obsm_varm=False)` DROPS obsm/varm by default; aging |

Methods and tool maturity move fast here. Before committing a conversion route, verify the chosen package is still maintained and matches installed versions (`packageVersion`, `pip show`).

## Loading 10X Cell Ranger Output

**Goal:** Read a Cell Ranger matrix correctly, keeping the raw matrix and non-GEX features when present.

**Approach:** Read the raw (unfiltered) MEX/HDF5 matrix; select stable Ensembl IDs for reproducible joins; retain Antibody/CRISPR features by disabling `gex_only`.

```python
import scanpy as sc

# raw_feature_bc_matrix has every barcode (needed by EmptyDrops/SoupX/CellBender); filtered_feature_bc_matrix has only called cells
adata = sc.read_10x_mtx('raw_feature_bc_matrix/', var_names='gene_ids', gex_only=False)
# gene_ids (Ensembl) is stable across annotation releases; gene_symbols (default) is ambiguous and non-unique
# gex_only=False keeps Antibody Capture / CRISPR Guide; split later by adata.var['feature_types']
adata.var_names_make_unique()
```

```r
library(Seurat)
counts <- Read10X(data.dir = 'filtered_feature_bc_matrix/')          # list when multiple feature types present
seurat_obj <- CreateSeuratObject(counts = counts, project = 'PBMC', min.cells = 3, min.features = 200)
```

Read functions return symbols by default. `sc.read_10x_h5` has no `var_names` argument (symbols by default; Ensembl IDs land in `var['gene_ids']`). `make_unique` appends `-1`/`-2` to duplicate symbols, which can mask distinct paralog/PAR loci, so prefer IDs when joining datasets.

## AnnData Object Structure

**Goal:** Place counts, normalized values, metadata, and embeddings in the conventional slots so downstream tools find them.

**Approach:** Keep integer counts in `layers['counts']`, log-normalized values in `X`, and a frozen full-gene snapshot in `.raw` before HVG subsetting.

```python
import anndata as ad

# X is (n_obs, n_vars) = cells x genes; obs indexes rows, var indexes columns
adata.layers['counts'] = adata.X.copy()   # integer UMIs, kept to recompute or feed count models (scVI, DESeq2)
# ... normalize_total + log1p populate X ...
adata.raw = adata                         # frozen log-normalized full-gene snapshot; survives later var-subsetting
adata = adata[:, adata.var['highly_variable']].copy()
```

Slot roles: `X`/`layers` align to both axes (each exactly cells x genes); `obs`/`obsm` align to cells; `var`/`varm` align to genes; `obsp`/`varp` are square pairwise graphs; `uns` is unstructured. `adata.raw.to_adata()` reconstitutes the snapshot. Slicing the parent by obs also slices raw on obs, but var-slicing does NOT shrink raw.

## Seurat v5 Object Structure

**Goal:** Read and write the right assay layer under the v5 layers API.

**Approach:** Use `LayerData()`/`$`-accessors; rejoin split layers after `merge()` before any function expecting one layer.

```r
counts <- LayerData(seurat_obj, layer = 'counts')      # v5; GetAssayData(slot=) is the superseded v4 form
counts <- seurat_obj[['RNA']]$counts                   # shorthand
merged <- merge(obj1, y = c(obj2, obj3), add.cell.ids = c('S1', 'S2', 'S3'))
merged <- JoinLayers(merged)                           # merge() splits layers (counts.1, counts.2); rejoin first
```

Seurat v5 stores `counts`/`data`/`scale.data` as layers in an `Assay5`; v4 used fixed slots via `GetAssayData(slot=)`. After `merge()`, layers split per object until `JoinLayers()`.

## Converting Between Python and R

**Goal:** Move an object across ecosystems without dropping layers, embeddings, or `raw`.

**Approach:** Prefer a maintained pure-R or Python-pinned converter; transpose and remap metadata; diff slots before and after.

| Tool | Direction | Maintained 2026 | Use when |
|------|-----------|-----------------|----------|
| anndataR | AnnData <-> SCE <-> Seurat; h5ad+zarr R/W | Yes (v1.2.0, pure R, no Python) | First choice for R-native, Python-free h5ad/zarr I/O and conversion |
| zellkonverter | AnnData <-> SCE | Yes (Bioc 3.23) | Mature SCE<->AnnData; robust Python reader with pinned anndata |
| schard | h5ad -> Seurat/SCE (read-only) | Yes | Robust pure-R READING of h5ad (SeuratDisk replacement) |
| anndata2ri | AnnData <-> SCE (rpy2) | Yes | Live mixed Python+R sessions / Jupyter `%%R` |
| sceasy | everything -> AnnData hub | Aging | Quick one-call conversion (mind `drop_single_values` data loss) |
| SeuratDisk | AnnData <-> h5Seurat | NO (last commit 2023, broken on Seurat v5) | Avoid for new work; legacy only |

```r
# Preferred R-native read of an h5ad written in Python (no reticulate)
library(anndataR)
adata <- read_h5ad('data.h5ad')
seurat_obj <- adata$to_Seurat()
# Or via Bioconductor with a pinned Python anndata:
# library(zellkonverter); sce <- readH5AD('data.h5ad'); writeH5AD(sce, 'out.h5ad')
```

zellkonverter maps asymmetrically: `obsm`->`reducedDims`, `varm`->a `rowData` matrix column (NOT reducedDims), `obsp`/`varp`->`colPairs`/`rowPairs`, `uns`->`metadata()` (lossy), and `raw`->`altExp(sce,'raw')` only when `raw=TRUE` (default FALSE). sceasy's `drop_single_values=TRUE` silently deletes every obs/var column with one unique value (a one-sample object loses its constant batch/condition label), so set `FALSE`.

## API Defaults That Surprise

| Call | Surprising default | Consequence |
|------|--------------------|-------------|
| `sc.read_10x_mtx(gex_only=True)` | drops Antibody/CRISPR/Custom features | CITE-seq ADT and guides silently vanish; set `gex_only=False` |
| `sc.read_10x_mtx(var_names='gene_symbols')` | non-unique, release-dependent symbols | Use `'gene_ids'` for reproducible cross-dataset joins |
| `AnnData.write_h5ad(compression=None)` | no compression (gzip default removed after v0.6.16) | Larger files; pass `compression='gzip'` |
| `write_loom(write_obsm_varm=False)` | obsm/varm dropped | Embeddings lost on Loom write |
| `read_h5ad(backed='r')` | only `X` edits persist | `obs`/`var`/`obsm` edits in backed mode are NOT written; re-`.write()` to a new file |
| `sceasy convertFormat(drop_single_values=TRUE)` | constant columns deleted | Single-value batch/condition labels lost; set `FALSE` |
| `sc.read_10x_mtx(cache=True)` | cache keyed by path only | Re-reading a path with different `var_names` returns the STALE object; delete the `.h5ad` cache or omit `cache` |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Converted object has genes and cells swapped | Transpose not applied (or applied without swapping metadata axis) | Transpose the matrix AND move `obs`<->col-meta, `var`<->row-meta |
| Layers / embeddings / `raw` missing after conversion | Lossy converter dropped non-`X` slots | Diff slot inventories; use anndataR/zellkonverter; re-attach manually |
| Cannot run EmptyDrops/SoupX/CellBender | Only the filtered matrix was kept | Re-obtain and store the RAW (unfiltered) Cell Ranger matrix |
| ADT/guide counts absent after loading 10X | `gex_only=True` (default) dropped non-GEX features | Reload with `gex_only=False`, split by `var['feature_types']` |
| Kernel/session dies reading a large object | Dense materialization of a sparse matrix | Keep sparse; use `backed='r'` (Python) or BPCells/on-disk layers (Seurat v5) |
| Downstream tool uses wrong values | Tool read `X` vs `.raw.X` against expectation | Set `use_raw=` explicitly; confirm which matrix holds counts vs lognorm |
| Duplicate gene symbols collapsed or suffixed oddly | `make_unique` appended `-1`/`-2` to distinct loci | Load with `var_names='gene_ids'` for stable identifiers |

## Related Skills

- single-cell/preprocessing - QC, normalization, and HVG selection after loading
- single-cell/doublet-detection - per-sample doublet calling on raw counts after loading
- single-cell/clustering - dimensionality reduction and clustering on the loaded object
- single-cell/multimodal-integration - MuData/h5mu handling for CITE-seq and Multiome
- spatial-transcriptomics/spatial-data-io - SpatialData/zarr I/O for spatial omics
- workflows/scrnaseq-pipeline - end-to-end scRNA-seq pipeline that starts from data loading

## References

- Virshup I, et al. (2023) The scverse project provides a computational ecosystem for single-cell omics. Nature Biotechnology 41:604-606. DOI 10.1038/s41587-023-01733-8
- Virshup I, Rybakov S, Theis FJ, Angerer P, Wolf FA (2024) anndata: Access and store annotated data matrices. Journal of Open Source Software 9(101):4371. DOI 10.21105/joss.04371
- Wolf FA, Angerer P, Theis FJ (2018) SCANPY: large-scale single-cell gene expression data analysis. Genome Biology 19:15. DOI 10.1186/s13059-017-1382-0
- Hao Y, et al. (2024) Dictionary learning for integrative, multimodal and scalable single-cell analysis (Seurat v5). Nature Biotechnology 42(2):293-304. DOI 10.1038/s41587-023-01767-y
- Amezquita RA, Lun ATL, Becht E, et al. (2020) Orchestrating single-cell analysis with Bioconductor. Nature Methods 17(2):137-145. DOI 10.1038/s41592-019-0654-x
- Bredikhin D, Kats I, Stegle O (2022) MUON: multimodal omics analysis framework. Genome Biology 23:42. DOI 10.1186/s13059-021-02577-8
- Lun ATL, Riesenfeld S, Andrews T, et al. (2019) EmptyDrops: distinguishing cells from empty droplets. Genome Biology 20:63. DOI 10.1186/s13059-019-1662-y
<!-- END FILE: single-cell/data-io/SKILL.md -->

## 子目录：single-cell/differential-abundance

<!-- BEGIN FILE: single-cell/differential-abundance/SKILL.md -->
---
name: bio-single-cell-differential-abundance
description: Test whether cell-type proportions or composition changed between conditions in single-cell data using Milo (miloR), scCODA, sccomp, and propeller. Use when comparing cell-type proportions / composition between conditions, asking which populations expanded or contracted with treatment or disease, running neighborhood-level (cluster-free) abundance testing, or guarding against compositional shifts that masquerade as differential expression.
tool_type: mixed
primary_tool: Milo
---

## Version Compatibility

Reference examples tested with: miloR 2.0+, scCODA 0.1.9+, sccomp 1.8+, speckle 1.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Differential Abundance Testing

**"Did cell-type proportions change between conditions?"** -> Test whether populations expanded or contracted between groups, accounting for the fact that proportions are not independent.
- R (cluster-free): `miloR` - build kNN graph, define neighborhoods, `testNhoods()` with a GLM and SpatialFDR
- Python/R (cluster-based): `scCODA` (Bayesian Dirichlet-multinomial), `sccomp` (Bayesian, outlier-robust), `propeller` (speckle, arcsin-sqrt + limma)

## Governing principle

Composition data live on a SIMPLEX: proportions sum to 1, so they are NOT independent - when one population expands, every other proportion is mechanically forced down even if its absolute count never changed. Running a per-cluster t-test (or Wilcoxon) on proportions across samples is therefore invalid: it ignores the negative correlation the constraint imposes, treats each cell type as a free measurement, and produces correlated false positives (one true expansion drags down the rest, which then test as spurious "depletions"). Valid methods model the joint composition: either a Dirichlet-multinomial / log-ratio model with a reference (scCODA, sccomp) or a variance-stabilizing transform plus a linear model (propeller), or they sidestep hard clusters entirely by testing abundance on the kNN graph (Milo).
Replicates are samples, not cells. The unit of replication for a composition claim is the biological sample/donor; thousands of cells from one donor are one draw. Differential abundance needs biological replicates per condition (Milo, scCODA, sccomp, propeller all model sample-level counts), and few replicates (n<3-4/group) leave abundance shifts underpowered and unstable - more donors help, more cells per donor barely do. With n=1 per condition the donor is perfectly confounded with condition: the effect is unidentifiable, not merely underpowered, yet scCODA and sccomp will still emit confident `credible_effects()` that are pure donor idiosyncrasy - require >=2 (ideally 3-4) biological replicates per group before believing any abundance call.
Differential abundance and differential expression are different questions and confound each other. A pseudobulk or cluster-level "DE" signal between conditions can be pure composition: if a cluster mixes substates and treatment shifts their ratio, the aggregated profile changes although no gene changed expression in any cell - differential abundance masquerading as differential expression, invisible if only DE is run. Always pair a condition-DE analysis (single-cell/markers-annotation, differential-expression/deseq2-basics) with a differential-abundance test and interpret them jointly.

## Choosing a differential-abundance method

| Method | Model | Granularity | Use when | Fails when |
|--------|-------|-------------|----------|------------|
| Milo (miloR) | NB-GLM on kNN-neighborhood counts, SpatialFDR | Cluster-free neighborhoods | Continuous/transitional states; shifts that discrete clusters hide; want sub-cluster resolution | Very few cells/sample; results sensitive to k and `prop`; needs an integrated embedding |
| scCODA | Bayesian Dirichlet-multinomial, log-linear, reference cell type | Discrete clusters | Cluster-level testing with the simplex bias handled; want credible effects / FDR | Reference cell type mis-chosen; very few samples; HMC tuning |
| sccomp | Bayesian beta-binomial mixed model, outlier-robust | Discrete clusters | Outliers/over-dispersion present; want joint mean + variability, random effects | Small data with weak priors; longer runtime |
| propeller (speckle) | arcsin-sqrt or logit transform + limma moderated test | Discrete clusters | Fast frequentist test, several samples/group, Seurat/SCE input | Very small sample counts; ignores some compositional coupling vs Bayesian models |
| Simple proportion t-test / chi-square | Per-cluster test on proportions | Discrete clusters | Never recommended as the primary test | Always - ignores the simplex; correlated false positives |

scCODA and sccomp are cluster-based and Bayesian and report credible/FDR-controlled effects; Milo is cluster-free and catches shifts within a cell type that clustering averages away; propeller is the fast frequentist option. Run a cluster-based method and Milo when feasible and reconcile. When methods compete, verify current best practice against installed docs.

## The reference-cell-type choice in scCODA

Compositional analysis is always relative to something. scCODA fixes one cell type as the reference assumed unchanged by the covariates, and reports every other type's change relative to it; the verdict can flip with a different reference. Choose a cell type that is biologically stable and abundant across all samples, or use `reference_cell_type='automatic'` (scCODA picks a type with low dispersion present in all samples). A reference that actually changes will bias all other calls. sccomp avoids a hard reference by modeling all groups jointly; Milo avoids it via the graph.

## Adjusting for nuisance covariates and confounded designs

**Goal:** Adjust the abundance model for technical or biological nuisances (sequencing batch, timing, sex, age) and recognize when adjustment cannot help.

**Approach:** Add the nuisance as an extra additive term in the model formula with the condition of interest last; the test then reports the condition effect holding the nuisance constant. The nuisance column must vary within each condition - if a batch is perfectly confounded with condition (e.g. all controls sequenced in batch 1, all treated in batch 2), the term is unidentifiable and the test is invalid; the fix is experimental (multiplex conditions across batches), not statistical.

```r
# Milo: batch added before condition; batch column lives in design.df
design <- distinct(as.data.frame(colData(milo))[, c('sample', 'batch', 'condition')])
rownames(design) <- design$sample
da <- testNhoods(milo, design = ~ batch + condition, design.df = design, reduced.dim = 'PCA')
```

```python
# scCODA: additive patsy formula; covariate columns must be in the count table
data = dat.from_pandas(counts, covariate_columns=['sample', 'batch', 'condition'])
model = mod.CompositionalAnalysis(data, formula='batch + condition', reference_cell_type='automatic')
```

```r
# sccomp: nuisance added to formula_composition (and optionally formula_variability)
res <- sccomp_estimate(counts_tbl, formula_composition = ~ batch + condition, .sample = sample, .cell_group = cell_type, .count = count, cores = 1)
```

Diagnose confounding before modeling: cross-tabulate batch x condition; if a batch maps to a single condition, no covariate term recovers the effect. Build Milo's kNN graph on a batch-corrected embedding, but keep batch in the GLM design as well, since integration and design adjustment address different residual structure.

## Milo - cluster-free neighborhood abundance (R)

**Goal:** Test differential abundance on kNN neighborhoods so shifts within and between cell types are both visible.

**Approach:** Build the Milo object from an integrated reduced dimension, sample representative neighborhoods, count cells per sample per neighborhood, then fit a GLM with `testNhoods` and control the graph-aware SpatialFDR; annotate neighborhoods back to cell types for interpretation.

```r
library(miloR)
library(SingleCellExperiment)

milo <- Milo(sce)
milo <- buildGraph(milo, k = 30, d = 30, reduced.dim = 'PCA')
milo <- makeNhoods(milo, prop = 0.1, k = 30, d = 30, refined = TRUE, reduced_dims = 'PCA')
milo <- countCells(milo, meta.data = as.data.frame(colData(milo)), samples = 'sample')

design <- data.frame(colData(milo))[, c('sample', 'condition')]
design <- distinct(design)
rownames(design) <- design$sample
milo <- calcNhoodDistance(milo, d = 30, reduced.dim = 'PCA')

da <- testNhoods(milo, design = ~ condition, design.df = design, reduced.dim = 'PCA')
da <- annotateNhoods(milo, da, coldata_col = 'cell_type')
table(da$SpatialFDR < 0.1, da$cell_type)
```

`k` and `prop` trade resolution against power: larger neighborhoods are better powered but blur fine shifts. SpatialFDR (not raw p) corrects for overlapping neighborhoods - report it. A neighborhood with a mixed `cell_type` fraction is a genuinely transitional region, not a labeling error.

## scCODA - Bayesian cluster-level composition (Python)

**Goal:** Test cluster proportion changes while handling the simplex's negative-correlation bias.

**Approach:** Build a per-sample cell-type count table with covariates, fit the Dirichlet-multinomial model against a reference cell type, sample the posterior, then read credible effects at a chosen FDR.

```python
import pandas as pd
from sccoda.util import cell_composition_data as dat
from sccoda.util import comp_ana as mod

counts = pd.crosstab(adata.obs['sample'], adata.obs['cell_type']).reset_index()
meta = adata.obs[['sample', 'condition']].drop_duplicates()
counts = counts.merge(meta, on='sample')

data = dat.from_pandas(counts, covariate_columns=['sample', 'condition'])
model = mod.CompositionalAnalysis(data, formula='condition', reference_cell_type='automatic')
result = model.sample_hmc()
result.set_fdr(est_fdr=0.1)
result.summary()
print(result.credible_effects())
```

`set_fdr(est_fdr=0.1)` chooses the spike-and-slab threshold for the desired expected FDR; credible effects are the populations whose change is supported relative to the reference.

## sccomp - outlier-robust Bayesian composition (R)

**Goal:** Test composition (and variability) jointly, robust to outlier samples.

**Approach:** Estimate the beta-binomial model from a count table or cell-level data with `sccomp_estimate`, optionally remove outliers, then test contrasts with `sccomp_test`, which returns a Bayesian FDR (`c_FDR`).

```r
library(sccomp)

res <- counts_tbl |>
    sccomp_estimate(formula_composition = ~ condition, .sample = sample, .cell_group = cell_type, .count = count, cores = 1) |>
    sccomp_remove_outliers(cores = 1) |>
    sccomp_test()
res[res$c_FDR < 0.05, c('cell_type', 'c_effect', 'c_FDR')]
```

`sccomp_test` reports `c_effect` (composition log-fold change) and `c_FDR`; modeling variability separately catches groups that differ in dispersion, not just mean proportion.

## propeller - fast frequentist proportions (R)

**Goal:** Quickly test cell-type proportion differences across groups.

**Approach:** Compute per-sample proportions, apply an arcsin-sqrt (or logit) variance-stabilizing transform, and run a limma moderated test per cell type.

```r
library(speckle)

out <- propeller(clusters = seurat_obj$cell_type, sample = seurat_obj$sample, group = seurat_obj$condition)
out[out$FDR < 0.05, ]
```

propeller is the fast default for several samples per group; for outliers, over-dispersion, or random effects, prefer sccomp or scCODA.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Many cell types flagged as changed, all anti-correlated | Per-cluster proportion t-tests ignore the simplex | Use scCODA/sccomp/propeller/Milo, which model the joint composition |
| scCODA verdict flips between runs | Reference cell type mis-chosen or actually changing | Pick a stable abundant reference, or `reference_cell_type='automatic'` |
| No significant abundance change despite an obvious shift | Too few biological replicates; underpowered | Add donors (not cells); report effect sizes / credible intervals |
| Milo neighborhoods look noisy / unstable | k or `prop` too small, or embedding not integrated | Increase k/prop; build the graph on a batch-corrected reduced dim |
| "DE genes" between conditions but expression unchanged per cell | Compositional shift masquerading as DE | Run a differential-abundance test alongside the DE analysis |
| propeller p-values too liberal with few samples | Frequentist test under-powered/over-confident at small n | Use a Bayesian model (sccomp/scCODA) and report uncertainty |
| Abundance significant only in one direction across all types | Reporting raw proportions without the constraint | Interpret relative to a reference and report which population actually drives the shift |

## Related Skills

- clustering - Define the clusters whose abundance is tested (cluster-based methods)
- cell-annotation - Annotate cell types before testing their proportions
- markers-annotation - Pair condition DE with abundance testing to separate the confound
- batch-integration - Build the integrated embedding Milo's kNN graph relies on
- differential-expression/deseq2-basics - Pseudobulk condition DE that abundance testing complements
- pathway-analysis/go-enrichment - Characterize the populations that expanded or contracted

## References

- Dann et al. 2022, Nat Biotechnol 40:245-253 - Milo; differential abundance on kNN-graph neighborhoods with SpatialFDR.
- Buttner et al. 2021, Nat Commun 12:6876 - scCODA; Bayesian Dirichlet-multinomial compositional analysis with a reference cell type.
- Mangiola et al. 2023, PNAS 120(33):e2203828120 - sccomp; outlier-robust Bayesian differential composition and variability.
- Phipson et al. 2022, Bioinformatics 38(20):4720 - propeller; arcsin-sqrt transform plus limma for cell-type proportion testing.
- Squair et al. 2021, Nat Commun 12:5692 - sample, not cell, is the unit of replication for cross-condition single-cell claims.
<!-- END FILE: single-cell/differential-abundance/SKILL.md -->

## 子目录：single-cell/doublet-detection

<!-- BEGIN FILE: single-cell/doublet-detection/SKILL.md -->
---
name: bio-single-cell-doublet-detection
description: Detect and remove doublets (two or more cells in one droplet) from single-cell RNA-seq using scDblFinder (R), Scrublet (Python), and DoubletFinder (R). Use when flagging artificial intermediate populations before clustering, setting the expected doublet rate from recovered-cell counts, running detection per sample before integration, choosing between simulate-and-score methods, or interpreting a non-bimodal score histogram.
tool_type: mixed
primary_tool: scDblFinder
---

## Version Compatibility

Reference examples tested with: scanpy 1.10+, scDblFinder 1.16+, Seurat 5.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Doublet Detection

**"Remove doublets from my data"** -> Flag droplets that captured two or more cells, which masquerade as fake intermediate cell states.
- Python: `sc.pp.scrublet()` per sample on raw counts
- R: `scDblFinder(sce, samples=...)` per sample on raw counts

## Governing Principle

Doublets fabricate fake biology, so the goal is not a "doublet-free" dataset but avoiding false conclusions. Three facts govern every decision.

Doublets create fake intermediate populations. A heterotypic doublet (two distinct types, e.g. T cell + monocyte) sums to a profile that lands between clusters and reads as a novel "transitional" state - the most damaging failure mode, because it corrupts trajectory inference and RNA velocity by building false bridges between lineages. Treat any small cluster co-expressing two lineage programs (CD3+LYZ, EPCAM+PTPRC) as doublet-suspect until proven otherwise.

Detect per sample, before integration or clustering. A doublet is a physical event within one droplet in one capture, so two cells from different samples can never share one - any cross-sample doublet called on a merged object is meaningless. Merging also corrupts the kNN/PCA neighborhood that scoring depends on. scDblFinder's `samples=` handles this internally; Scrublet and DoubletFinder must be looped per sample. All three want raw counts after basic QC.

Removal is never complete, and over-removal deletes real cells. Homotypic doublets (two cells of the same type) sum to a profile that looks like one bigger cell of that type and are nearly invisible to any expression-based method, so reported "doublet rates" only cover the heterotypic-detectable fraction. Conversely, doublet scores correlate with total counts, the same axis as count-based QC, so aggressive filtering on both double-penalizes and strips genuine high-RNA populations (megakaryocytes, plasma cells, large neurons). Coordinate the two filters and prefer flag-and-inspect over blind deletion.

## Expected Doublet Rate

10X Chromium loading is near-Poisson, so the multiplet rate scales roughly linearly with recovered cells: ~0.8% per 1,000 cells recovered (`dbr.per1k = 0.008`).

| Cells recovered (~) | Expected rate (~) |
|---------------------|-------------------|
| 1,000 | 0.8% |
| 2,000 | 1.6% |
| 5,000 | 3.9% |
| 10,000 | 7.6-8% |

Rule: rate ~= 0.008 x recovered/1000. Always set the expected rate from the actual recovered-cell count of that lane; Scrublet's flat `expected_doublet_rate=0.05` is a placeholder, not a recommendation. High-throughput chips have lower per-cell rates. For multiplexed pools (genotype/HTO-demultiplexed), the physical doublet rate is set by TOTAL lane loading, not the demultiplexed subset: deriving the rate from one sample's cells underestimates it (four 5k samples in one 20k lane is ~15% real, not the ~3.9% implied by 5k), so set the rate from the total lane cell count.

## Heterotypic, Homotypic, Neotypic

| Type | Composition | Detectability |
|------|-------------|---------------|
| Heterotypic | Two transcriptionally distinct types | Detectable; lands between clusters; the dangerous "fake transitional" ones |
| Homotypic | Two cells of the same type | Nearly undetectable by expression; persists after removal |
| Neotypic | Heterotypic blend occupying a region no singlet occupies | Most detectable; most misleading if missed (looks like a rare new type) |

`modelHomotypic`-style adjustments only change the number expected to be detectable; they cannot recover undetectable homotypic doublets.

## Choosing a Method

| Method | Model | Use when | Fails / weak when |
|--------|-------|----------|-------------------|
| scDblFinder (R) | xgboost on kNN features vs simulated doublets | Default; best accuracy-speed balance; built-in per-sample via `samples=` | R/Bioconductor only |
| Scrublet (Python) | kNN density of simulated doublets | scanpy-native pipelines | Auto-threshold fails on unimodal histograms; loop per sample manually |
| DoubletFinder (R) | pANN from PC neighborhood | Legacy Seurat workflows | Brittle; `pK` needs per-dataset sweep; `*_v3` names removed; Seurat-version-coupled |
| solo (Python) | scVI VAE + classifier | Have a trained scVI model; GPU available | Heavier setup |
| scds cxds/bcds/hybrid (R) | Co-expression / boosted tree | Fast first pass on very large data | Lower accuracy than scDblFinder/DoubletFinder |

scDblFinder is the 2024-2026 best-balance default and is recommended by sc-best-practices. The older Xi and Li 2021 ranking ("DoubletFinder is most accurate") predates major scDblFinder improvements and is superseded - do not cite it against current scDblFinder. Methods compete and drift; verify current standing against the installed tool's docs before committing.

## scDblFinder (R, recommended)

**Goal:** Call doublets with a fast gradient-boosted classifier, per sample, with the rate inferred from cell count.

**Approach:** Convert to SingleCellExperiment, pass the per-sample key so each capture is processed independently, then read the class/score back.

```r
library(scDblFinder)
library(SingleCellExperiment)

sce <- as.SingleCellExperiment(seurat_obj)                 # or build directly from a counts matrix
sce <- scDblFinder(sce, samples = 'sample_id')             # per-capture; dbr defaults from cell count via dbr.per1k=0.008
table(sce$scDblFinder.class)                               # adds scDblFinder.class ('singlet'/'doublet') and .score
seurat_obj$scDblFinder_class <- sce$scDblFinder.class
seurat_obj$scDblFinder_score <- sce$scDblFinder.score
```

`clusters=NULL` (default) generates purely random artificial doublets and is generally recommended; pass a vector for cluster-based generation. `dbr=NULL` computes the rate from cell count; set `dbr`/`dbr.sd` explicitly to encode a known loading.

## Scrublet (Python)

**Goal:** Score doublets in a scanpy pipeline, per sample, with the rate set from recovered cells.

**Approach:** Use the maintained `sc.pp.scrublet` path on raw counts; set `expected_doublet_rate` per lane; inspect the histogram when the auto-threshold looks wrong.

```python
import scanpy as sc

n_cells = adata.n_obs
expected_rate = 0.008 * n_cells / 1000                     # from recovered cells, not the 0.05 placeholder
sc.pp.scrublet(adata, expected_doublet_rate=expected_rate)  # adds obs['doublet_score'], obs['predicted_doublet']
# auto-threshold needs a bimodal histogram; if unimodal, inspect uns['scrublet'] and set threshold manually
adata_singlets = adata[~adata.obs['predicted_doublet']].copy()
```

For pooled samples, loop `sc.pp.scrublet(adata[adata.obs.sample == s], ...)` per sample (or pass `batch_key`), never on the merged object.

## DoubletFinder (R, legacy Seurat)

**Goal:** Run DoubletFinder on a fully preprocessed Seurat object, tuning `pK` and homotypic-adjusting the expected count.

**Approach:** Sweep `pK`, pick the BCmvn maximum, then set `nExp` from the rate adjusted for the homotypic fraction.

```r
library(DoubletFinder)                                     # *_v3 function names were removed in Nov 2023; verify installed API

sweep.res <- paramSweep(seurat_obj, PCs = 1:20, sct = FALSE)
bcmvn <- find.pK(summarizeSweep(sweep.res, GT = FALSE))
pK <- as.numeric(as.character(bcmvn$pK[which.max(bcmvn$BCmetric)]))   # no default pK; tune per dataset

rate <- 0.008 * ncol(seurat_obj) / 1000
nExp <- round(rate * ncol(seurat_obj))
nExp <- round(nExp * (1 - modelHomotypic(seurat_obj$seurat_clusters)))  # discount undetectable homotypic doublets
seurat_obj <- doubletFinder(seurat_obj, PCs = 1:20, pN = 0.25, pK = pK, nExp = nExp, sct = FALSE)
```

`pN` (artificial-doublet proportion) defaults to 0.25 and performance is largely insensitive to it. DoubletFinder requires a normalized, PCA'd, clustered object and is the most version-sensitive of the three.

## Deeper Cautions

Simulated doublets are a model, not the real thing: real doublets share one RT/PCR reaction (capture competition, barcode effects), so simulated-doublet density only approximates where real doublets sit, and even the best method has a low ceiling (max mean AUPRC ~0.537 in Xi and Li 2021 - every method misses a lot). Over-removal culls proliferating (S/G2M) and genuine transitional cells that legitimately score high, so cross-check removed cells against cell-cycle and activation signatures. When available, experimental ground truth beats inference: cell hashing (CITE-seq HTOs) and MULTI-seq call inter-sample doublets directly regardless of expression similarity (catching even cross-sample homotypic doublets), and serve as a complementary filter. Heavy ambient RNA can mimic co-expression and nudge scores, so handle empty droplets and ambient RNA first (see single-cell/preprocessing).

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Doublet calls look random / too many | Run on merged multi-sample data | Run per sample before integration (`samples=` or loop) |
| Auto-threshold splits the histogram badly | Scrublet histogram is unimodal | Inspect the histogram and set `threshold` manually |
| A high-RNA cell type was wiped out | Count-based QC and doublet removal double-penalized the same axis | Coordinate the filters; do not stack aggressive cutoffs |
| "Novel transitional state" co-expresses two lineages | Heterotypic doublets masquerading as a cluster | Confirm per-sample detection; check marker co-expression / hashing before claiming a new type |
| Trajectory has an implausible bridge between lineages | Doublets forming a false intermediate | Remove/flag doublets before trajectory inference |
| Reported "0% doublets" | Homotypic doublets are invisible | Do not claim doublet-free; report only the detectable fraction |
| DoubletFinder call errors after a Seurat upgrade | `*_v3` names removed; API drift | Use current function names; re-tune `pK` |
| Expected rate clearly wrong | Used a package default | Set rate from recovered cells (~0.008 x cells/1000) |
| Multiplexed pool underestimates doublets | Rate derived from one demultiplexed sample, not total lane | Set the expected rate from total capture-lane cells |

## Related Skills

- single-cell/preprocessing - QC and ambient-RNA handling before doublet detection
- single-cell/hashing-demultiplexing - Hashtag-based cross-sample doublet calling (complements expression-based detection)
- single-cell/data-io - load raw per-sample matrices before processing
- single-cell/clustering - run clustering after doublet removal
- single-cell/batch-integration - integrate samples only after per-sample doublet calling
- single-cell/trajectory-inference - doublets create false bridges; remove them first

## References

- Wolock SL, Lopez R, Klein AM (2019) Scrublet: computational identification of cell doublets in single-cell transcriptomic data. Cell Systems 8(4):281-291.e9. DOI 10.1016/j.cels.2018.11.005
- McGinnis CS, Murrow LM, Gartner ZJ (2019) DoubletFinder: doublet detection in single-cell RNA sequencing data using artificial nearest neighbors. Cell Systems 8(4):329-337.e4. DOI 10.1016/j.cels.2019.03.003
- Germain P-L, Lun A, Macnair W, Robinson MD (2021) Doublet identification in single-cell sequencing data using scDblFinder. F1000Research 10:979. DOI 10.12688/f1000research.73600
- Xi NM, Li JJ (2021) Benchmarking computational doublet-detection methods for single-cell RNA sequencing data. Cell Systems 12(2):176-194.e6. DOI 10.1016/j.cels.2020.11.008
- Bernstein NJ, Fong NL, Lam I, et al. (2020) Solo: doublet identification in single-cell RNA-seq via semi-supervised deep learning. Cell Systems 11(1):95-101.e5. DOI 10.1016/j.cels.2020.05.010
- Bais AS, Kostka D (2020) scds: computational annotation of doublets in single-cell RNA sequencing data. Bioinformatics 36(4):1150-1158. DOI 10.1093/bioinformatics/btz698
- McGinnis CS, Patterson DM, Winkler J, et al. (2019) MULTI-seq: sample multiplexing for single-cell RNA sequencing using lipid-tagged indices. Nature Methods 16(7):619-626. DOI 10.1038/s41592-019-0433-8
- Heumos L, Schaar AC, Lance C, et al. (2023) Best practices for single-cell analysis across modalities. Nature Reviews Genetics 24:550-572. DOI 10.1038/s41576-023-00586-w
<!-- END FILE: single-cell/doublet-detection/SKILL.md -->

## 子目录：single-cell/hashing-demultiplexing

<!-- BEGIN FILE: single-cell/hashing-demultiplexing/SKILL.md -->
---
name: bio-single-cell-hashing-demultiplexing
description: Assign cells to their sample of origin from cell or nucleus hashing (CITE-seq HTOs, MULTI-seq lipid/cholesterol tags, CellPlex CMOs) and call cross-sample doublets using Seurat HTODemux/MULTIseqDemux, hashsolo, demuxEM, GMM-Demux, and demuxmix. Use when assigning pooled hashed cells back to their sample, calling cross-sample doublets from HTO counts, choosing a demultiplexing method, deciding between hashtag and genetic demultiplexing, or rescuing an oversized Negative pile from weak HTO staining or ambient spillover.
tool_type: mixed
primary_tool: Seurat
---

## Version Compatibility

Reference examples tested with: Seurat 5.0+, scanpy 1.10+, pegasus 1.8+, demuxmix 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Hashtag Demultiplexing and Cross-Sample Doublet Calling

**"Which sample did each cell come from, and which barcodes are cross-sample doublets?"** -> Classify every cell's HTO count vector to the one tag that dominates its background, and flag cells where two tags are both high.
- R: `Seurat::HTODemux` (antibody HTOs), `Seurat::MULTIseqDemux` (MULTI-seq lipid tags), `demuxmix` (regression mixture, robust to bad staining)
- Python: `scanpy.external.pp.hashsolo` (Bayesian), `pegasus.demultiplex` / demuxEM (background from empty droplets)
- CLI: `GMM-Demux` (Gaussian mixture with explicit multiplet accounting)

## Governing principle

In cell or nucleus hashing, each sample is labeled before pooling with a unique oligo-tagged reagent: a barcoded antibody (CITE-seq HTO), a lipid- or cholesterol-modified oligo (MULTI-seq), or a CellPlex CMO. A true singlet's HTO count vector is dominated by ONE tag standing well above a background of ambient and spillover counts, so sample assignment reduces to one question per cell: which tag, if any, exceeds that cell's background. Cross-sample doublets fall out directly - two tags both high - which is the decisive advantage of hashing over expression-only doublet detection.

Hashtag demux, genetic demux, and expression-doublet detection answer three DIFFERENT questions and should be combined, not substituted. Hashtag and genetic demux both assign samples and catch cross-sample doublets, but expression-doublet detection (single-cell/doublet-detection) catches within-sample and homotypic doublets that hashing and genetics are blind to, because two cells from the same sample carry the same tag and the same genotype. Conversely, expression methods miss cross-sample doublets when the two samples are transcriptionally similar. The cross-sample doublet rate also calibrates the expected TOTAL doublet rate: with two pooled samples within- and cross-sample doublets are equally frequent, while with k samples cross-sample doublets dominate and within-sample ones fall to about 1/k of all doublets, so hashing still misses that within-sample fraction (expression-doublet detection stays necessary) and a hashing doublet rate far below the expression-doublet rate is a red flag that staining or thresholds are off.

The hard part is the background, not the dominant tag. Ambient HTO from lysed cells, spillover between tags, staining failure, and batch differences in tag-capture efficiency all inflate the background and grow the "Negative" pile (real cells whose true tag never cleared background, distinct from true empty droplets removed upstream). Nucleus hashing is harder than whole-cell because tag capture is lower. Methods differ mainly in how they model that background.

## Choosing a demultiplexing modality

| Modality | Needs | Cross-sample doublets | Cannot do | Tools |
|----------|-------|-----------------------|-----------|-------|
| Hashtag/HTO (this skill) | HTO/lipid/CMO library at pooling | Yes (two tags high) | Nothing without a hashing library; sensitive to staining and ambient | HTODemux, MULTIseqDemux, hashsolo, demuxEM, GMM-Demux, demuxmix |
| Genetic (natural SNPs) | >=2 distinct genotypes, no hashing | Yes | Cannot separate same-donor samples (identical genotype) | demuxlet, freemuxlet, souporcell, vireo |
| Expression doublet (orthogonal) | Just the GEX matrix | No (misses when samples similar) | Catches within-sample/homotypic doublets the other two miss | scDblFinder, Scrublet (single-cell/doublet-detection) |

Genetic demux is the fallback when no hashing was done but samples come from different donors; it cannot resolve multiple samples from one donor, which hashing can. Pair whichever sample-assignment method applies with expression-doublet detection for the doublets it cannot see.

## Choosing a hashtag caller

| Method | Model | Use when | Fails when |
|--------|-------|----------|------------|
| HTODemux (Seurat) | k-medoids cluster per HTO + negative-distribution quantile | Standard antibody HTO, clean bimodal staining, Seurat workflow | Weak/low-depth staining or heavy ambient; clustering unstable on near-zero HTOs |
| MULTIseqDemux (Seurat) | Per-HTO KDE, threshold between maxima, quantile sweep | MULTI-seq lipid/cholesterol tags; want autoThresh to optimize the quantile | Few cells; unimodal density when one tag dominates |
| hashsolo (scanpy/solo) | Bayesian over negative/singlet/doublet | Few hashtags (works at 2), many negatives, scanpy-native pipeline | Very low signal; priors mis-set for the actual doublet rate |
| demuxEM (pegasus) | EM with background estimated from empty droplets | High ambient; nucleus hashing; raw matrix with empties available | Empty droplets filtered out before calling; very sparse signal |
| GMM-Demux (CLI) | Gaussian mixture on normalized HTO, explicit MSM multiplets | Want explicit multiplet accounting or experiment planning | Non-Gaussian background; poor per-tag separation |
| demuxmix (R) | Negative-binomial regression mixture, optional RNA covariate | Bad/variable staining, batch tag-efficiency differences | Very few cells per mixture component |

The EM and regression methods (demuxEM, demuxmix) model the background explicitly and are the robust choice when staining is marginal, and they handle a two-tag pool as readily as a many-tag one (their failure mode is too few cells per mixture component, not too few tags), so weak staining even at two tags routes to demuxmix or demuxEM rather than hashsolo; HTODemux and MULTIseqDemux are fast defaults for clean data; hashsolo handles few hashes and many negatives. When callers disagree, run a consensus (cellhashR wraps several callers) and verify current best practice against installed docs before trusting any single call.

## Normalize HTO counts before calling

**Goal:** Put HTO counts on a scale where the dominant tag separates from background.

**Approach:** Apply the centered log-ratio (CLR) transform to the HTO assay. CLR margin=1 normalizes the tags within each cell and is the Seurat default that the canonical HTO vignette uses; margin=2 normalizes each tag across cells and is a common alternative for HTO/ADT because it corrects per-tag capture-efficiency differences. Choose deliberately and compare both rather than blindly accepting the default.

```r
library(Seurat)

hto <- CreateSeuratObject(counts = gex_counts)
hto[['HTO']] <- CreateAssay5Object(counts = hto_counts)
hto <- NormalizeData(hto, assay = 'HTO', normalization.method = 'CLR', margin = 2)
```

## Classify samples and doublets with HTODemux (R)

**Goal:** Assign each cell to a single HTO or label it a cross-sample doublet or Negative.

**Approach:** Cluster cells per HTO, model the low-count (negative) cluster, and call a cell positive for any tag whose count exceeds the `positive.quantile` of that negative distribution; one positive is a singlet, two or more a doublet, none a Negative.

```r
hto <- HTODemux(hto, assay = 'HTO', positive.quantile = 0.99)

table(hto$HTO_classification.global)        # Singlet / Doublet / Negative
table(hto$hash.ID)                          # per-sample singlet counts + Doublet + Negative
singlets <- subset(hto, subset = HTO_classification.global == 'Singlet')
```

`positive.quantile = 0.99` is the quantile of the inferred negative distribution above which a cell counts as positive; raise it to be stricter (fewer false singlets, more Negatives), lower it to rescue cells when staining is weak. `HTO_classification.global` holds Singlet/Doublet/Negative; `hash.ID` holds the sample name (or Doublet/Negative) and becomes the active identity.

## Demultiplex MULTI-seq tags with MULTIseqDemux (R)

**Goal:** Classify MULTI-seq lipid/cholesterol-tagged samples, optimizing the threshold automatically.

**Approach:** For each tag, find the threshold between the two density maxima; with `autoThresh=TRUE`, sweep the quantile over `qrange` to maximize the number of singlets.

```r
hto <- MULTIseqDemux(hto, assay = 'HTO', autoThresh = TRUE)
table(hto$MULTI_ID)                          # sample / Doublet / Negative
```

`MULTI_ID` carries the per-cell call. Use a fixed `quantile = 0.7` instead of `autoThresh` only when the automated sweep over- or under-calls on a particular dataset.

## Demultiplex in scanpy with hashsolo (Python)

**Goal:** Bayesian sample assignment that behaves with few hashtags and many negatives.

**Approach:** Place raw HTO counts as columns in `adata.obs`, then run hashsolo with priors over the negative, singlet, and doublet hypotheses; the doublet prior should track the expected loading doublet rate.

```python
import scanpy as sc
import scanpy.external as sce

hto_cols = ['HTO_A', 'HTO_B', 'HTO_C', 'HTO_D']
adata.obs[hto_cols] = hto_counts_df[hto_cols]
sce.pp.hashsolo(adata, cell_hashing_columns=hto_cols, priors=(0.01, 0.8, 0.19))

adata.obs['Classification'].value_counts()   # barcode name / 'Negative' / 'Doublet'
singlets = adata[~adata.obs['Classification'].isin(['Negative', 'Doublet'])].copy()
```

`priors` are ordered [negative, singlet, doublet]; raise the doublet prior for higher loading. Output columns include `Classification`, `most_likely_hypothesis`, and the per-hypothesis probabilities.

## Model ambient background explicitly (Python / R)

**Goal:** Recover correct calls when ambient HTO or weak staining inflates the background.

**Approach:** demuxEM estimates the background from empty droplets before assigning signal; demuxmix fits a negative-binomial regression mixture using the number of detected genes as a covariate, both of which are more robust than a fixed quantile.

```python
import pegasus as pg

pg.estimate_background_probs(hashing_data)
pg.demultiplex(rna_data, hashing_data, min_signal=10.0)
rna_data.obs['demux_type'].value_counts()    # singlet / doublet / unknown
rna_data.obs['assignment']                    # sample name per cell
```

```r
library(demuxmix)

dmm <- demuxmix(as.matrix(hto_counts), rna = num_detected_genes)
calls <- dmmClassify(dmm)                      # HTO assignment + Type (singlet/multiplet/negative/uncertain)
```

`min_signal=10.0` marks cells with too little signal as unknown; lower it to rescue low-capture nucleus hashing, raise it for cleaner singlets. demuxmix's RNA covariate is what makes it robust to per-tag staining differences.

## Threshold and parameter reference

| Parameter | Default | Rationale and when to change |
|-----------|---------|------------------------------|
| HTODemux positive.quantile | 0.99 | Quantile of the negative distribution defining "positive"; raise for stricter calls (more Negatives), lower to rescue weak staining |
| NormalizeData CLR margin | 1 (Seurat default); 2 common for HTO | margin=2 normalizes each tag across cells, correcting per-tag capture bias; pick per the staining and verify |
| MULTIseqDemux quantile / autoThresh | 0.7 / FALSE | autoThresh sweeps the quantile to maximize singlets; use when a fixed threshold over- or under-calls |
| hashsolo priors | (0.01, 0.8, 0.19) | [negative, singlet, doublet]; the doublet prior should track expected loading doublets (~0.8% per 1000 cells on 10x) |
| demuxEM min_signal | 10.0 | Cells below this signal are unknown; lower for low-capture nuclei, raise for cleaner singlets |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Huge Negative pile, few singlets | Weak staining or high ambient inflating background; quantile too strict | Lower positive.quantile / min_signal; switch to demuxEM (empty-droplet background) or demuxmix (RNA covariate) |
| Cross-sample doublet rate near zero but expression doublets high | Hashing thresholds too loose, or doublet prior too low | Tighten the quantile; raise hashsolo doublet prior; reconcile against the expected loading doublet rate |
| HTODemux errors on a zero-count cluster | Cells with all-zero HTO counts cluster together | Filter cells with no HTO counts before HTODemux; check the HTO matrix barcodes match the GEX cells |
| Calls flip with normalization choice | CLR margin=1 vs margin=2 shifts per-tag thresholds | Choose margin deliberately (margin=2 corrects tag-efficiency bias); compare both and inspect ridge plots |
| Genetic demux cannot split two samples | Both samples are the same donor (identical genotype) | Use hashtag demux; genetic methods cannot separate same-donor samples |
| Cross-sample doublets present but homotypic doublets remain | Hashing is blind to within-sample doublets | Run expression-doublet detection (single-cell/doublet-detection) in addition |
| Nucleus hashing yields mostly Negatives | Lower tag capture in nuclei than whole cells | Use demuxEM (designed for nuclei); lower min_signal; expect a larger Negative fraction |
| Looks clean (low Negatives, low doublets) but nearly all cells are one sample | Staining failure where one tag dominates all cells (mispipetted/over-concentrated antibody, or all samples got the same tag) | Sanity-check the per-tag singlet distribution against the expected pooling; one tag capturing nearly all cells means staining failed even though Negatives look low |
| One sample silently lost or contaminating while others demultiplex fine | A single antibody failed to stain, so its cells fall into Negative or misassign to the nearest-ambient tag | Check each tag has a non-trivial positive population; one near-zero tag means a failed antibody dropped or misassigned that sample |
| The rare sample in unequal pooling is under-recovered | Very unequal pooling (e.g. 80/10/10) leaves the minority tag too few positives to form a clean cluster or negative distribution | Inspect per-tag ridge plots; consider demuxmix for the minority tag, whose regression mixture is more stable on small components |
| Many cells flagged generic "Doublet" | Cells positive for 3+ tags collapsed to one label, hiding over-loading or heavy ambient | Inspect the multiplet tag-count distribution (GMM-Demux MSM); 3+ tags high is a run-quality diagnostic, not an ordinary 2-cell doublet |

## Related Skills

- single-cell/doublet-detection - Expression-based within-sample doublet calling that complements cross-sample hashing doublets
- single-cell/preprocessing - Filter empty droplets and QC the cells before and after demultiplexing
- single-cell/batch-integration - Integrate the demultiplexed per-sample data; covers genetic demultiplexing as an alternative
- single-cell/multimodal-integration - HTOs are an ADT-like modality; the CLR normalization here parallels CITE-seq ADT handling
- single-cell/clustering - Cluster the recovered singlets after sample assignment

## References

- Stoeckius et al. 2018, Genome Biol 19:224 - Cell Hashing; barcoded antibodies for multiplexing and doublet detection.
- McGinnis et al. 2019, Nat Methods 16:619-626 - MULTI-seq; lipid- and cholesterol-tagged-oligo sample multiplexing.
- Kang et al. 2018, Nat Biotechnol 36:89-94 - demuxlet; genetic demultiplexing from natural variation.
- Heaton et al. 2020, Nat Methods 17:615-620 - souporcell; genotype clustering without reference genotypes.
- Huang et al. 2019, Genome Biol 20:273 - vireo; Bayesian genetic demultiplexing without a genotype reference.
- Bernstein et al. 2020, Cell Syst 11(1):95-101 - Solo and hashsolo; Bayesian hashing demultiplexing.
- Gaublomme et al. 2019, Nat Commun 10:2907 - demuxEM; nuclei multiplexing with background estimated from empty droplets.
- Xin et al. 2020, Genome Biol 21:188 - GMM-Demux; Gaussian mixture with multi-sample-multiplet accounting.
- Klein 2023, Bioinformatics 39(8):btad481 - demuxmix; negative-binomial regression mixture robust to staining differences.
<!-- END FILE: single-cell/hashing-demultiplexing/SKILL.md -->

## 子目录：single-cell/lineage-tracing

<!-- BEGIN FILE: single-cell/lineage-tracing/SKILL.md -->
---
name: bio-single-cell-lineage-tracing
description: Reconstructs single-cell lineage trees and clonal relationships from CRISPR/Cas9 scars, static expressed barcodes (LARRY/CellTag), or somatic mtDNA mutations using Cassiopeia, Startle, and CoSpar. Use when building a phylogeny from barcode scars, choosing a tree-reconstruction solver, handling homoplasy and dropout, grouping clones from mtDNA, integrating clone with transcriptomic state, or judging whether a state-based fate call is trustworthy.
tool_type: python
primary_tool: Cassiopeia
---

## Version Compatibility

Reference examples tested with: Cassiopeia 2.0+, CoSpar 0.3+, scanpy 1.10+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Lineage Tracing

**"Reconstruct cell lineage from barcodes"** -> Read heritable marks across single cells and ask which cells share which marks to recover an ontogenetic phylogeny or clonal grouping.
- Python: `cassiopeia` (scar-tree reconstruction), `cospar` (clone + state integration), mtDNA variant callers (mgatk/MAESTER pipelines)

## Governing Principle

Transcriptomic state does NOT fully predict fate. Weinreb 2020 (LARRY) showed sister cells in an indistinguishable transcriptomic state systematically diverge in fate, so the information that decides a bifurcation is heritable but invisible to the measured transcriptome. Three consequences drive every decision here.

1. Lineage is orthogonal to expression, not redundant with it. A purely state-based trajectory method is systematically wrong about commitment for such populations, which is the empirical justification for every "barcode + transcriptome in the same cell" assay and for integrative tools like CoSpar.
2. Reconstruction is phylogenetics on error-prone scars. A scar/barcode tree inherits every pathology of molecular phylogenetics, sharpened by CRISPR peculiarities: homoplasy (independent cells acquire the identical scar), dropout (missing vs unedited confusion), saturation of a finite editable array, and non-clock editing rates.
3. The state->fate map can be one-to-many. A state-based branch call can be confident precisely because it is blind to the heritable variable that actually decides fate. Prospective tracing (engineered barcodes installed BEFORE the process) is the only design that can measure fate independently of state and thus test state->fate; retrospective tracing (mtDNA read out after) recovers ancestry but cannot by itself establish what state preceded a fate.

Two hard errors a reviewer presses on. Missing-as-unedited: an uncaptured edit recorded as the "0" state is indistinguishable from a site that genuinely never edited, and heritable excision dropout removes a whole character across an entire clade, biasing topology, not merely adding noise. Homoplasy: Cas9 indel outcomes are highly non-uniform, so a handful of indels dominate and parsimony falsely fuses unrelated lineages that share a frequent scar. Topology error also compounds toward the root, where the deepest, most consequential splits rest on the fewest characters.

## Assay Decision Table

Choose the recording technology by the question, not by availability.

| Assay | Mark / model | Use when | Fails when |
|-------|--------------|----------|------------|
| CRISPR scar array (GESTALT/scGESTALT/ScarTrace/LINNAEUS) | cumulative irreversible Cas9 indels = phylogenetic characters | deep tree topology in an engineered organism; scar + scRNA-seq in the same cell | saturation caps depth; homoplasy fuses lineages; heritable dropout deletes clades; not usable in native human tissue |
| Static expressed barcode (LARRY, Weinreb 2020) | one unique inherited lentiviral barcode per founder = a flat clone | clean state->fate maps via split-and-profile; proving state underdetermines fate | gives clonal membership, NOT division-order topology; library << founders causes barcode collisions |
| Combinatorial/sequential barcode (CellTag, Biddy 2018) | combination of expressed tags + nested timepoints | extra clonal resolution and coarse multi-level nesting | shallow trees; collisions; not a resolved phylogeny |
| Somatic mtDNA (Ludwig 2019; mtscATAC-seq; MAESTER) | drifting heteroplasmy of somatic mtDNA variants | retrospective tracing in primary human tissue with no engineering | low mutation rate -> few informative variants; hotspot homoplasy; coverage/dropout; heteroplasmy drift + selection; gives clonal grouping not deep trees |

## Reconstruction Solver Decision Table

For scar data, the solver is a separate choice from the assay (Cassiopeia, Jones 2020; Startle, Sashittal 2023).

| Solver | Model | Use when | Fails when |
|--------|-------|----------|------------|
| VanillaGreedySolver | top-down parsimony, split on most-frequent mutation | fast first pass; 10^4-10^5 cells | greedy split errors propagate; sensitive to homoplasy |
| ILPSolver | integer-LP Steiner tree (Gurobi); near-optimal | small clades needing accuracy | expensive; does not scale to large trees |
| HybridSolver | greedy top + ILP on small subclades | the practical default for large data | inherits greedy errors at the top split |
| NeighborJoiningSolver | distance-based (weighted Hamming) | quick comparison baseline; non-character distances | less accurate than parsimony on scar characters |
| Startle (Startle-ILP / Startle-NNI) | star-homoplasy: a character mutates at most once per root-to-leaf path | severe homoplasy/dropout breaks parsimony | ILP cost; NNI is heuristic at scale |

Run a panel of solvers, not one: it is rare for a single solver to be optimal over all parts of a tree, and agreement across solvers is the practical certainty signal. Always weight indels by their formation probability (down-weight frequent low-information scars) and report robustness to homoplasy and dropout. Methodology evolves; verify the current solver API and recommended defaults against the installed Cassiopeia docs.

### Build a Character Matrix and Reconstruct a Tree

**Goal:** Turn scar calls into a maximum-parsimony lineage tree with missing data modeled explicitly.
**Approach:** Load a cells x sites character matrix (0 = unedited, 1+ = distinct scars, -1 = missing), assess missingness and informativeness, then solve.

```python
import cassiopeia as cas
import numpy as np

tree = cas.data.CassiopeiaTree(character_matrix=char_matrix, cell_meta=cell_meta)
print(f'cells {tree.n_cell}  characters {tree.n_character}  missing {(char_matrix == -1).mean():.2%}')

solver = cas.solver.VanillaGreedySolver()
solver.solve(tree, collapse_mutationless_edges=True)   # collapse edges with no supporting mutation
newick = tree.get_newick()
```

The `-1` missing state must stay distinct from the `0` unedited state: collapsing missing into unedited is the single most consequential preprocessing error, since heritable dropout is tree-correlated and silently erases real structure.

### Compare Solvers and Score Tree Robustness

**Goal:** Quantify how much the topology depends on solver choice and on homoplasy/dropout.
**Approach:** Solve with several solvers, then compare the resulting trees with Robinson-Foulds and the depth-stratified triplets-correct metric.

```python
hybrid = cas.solver.HybridSolver(top_solver=cas.solver.VanillaGreedySolver(), bottom_solver=cas.solver.ILPSolver(), cell_cutoff=200)
nj = cas.solver.NeighborJoiningSolver(dissimilarity_function=cas.solver.dissimilarity_functions.weighted_hamming_distance)
for s in (hybrid, nj):
    s.solve(tree)                                       # solve independent copies in practice
rf, rf_max = cas.critique.robinson_foulds(tree_a, tree_b)
triplet_acc = cas.critique.triplets_correct(tree_a, tree_b)
```

Triplets-correct is depth-stratified, so it exposes the field's hard truth: deep (near-root) splits are the least certain and the most consequential, while well-supported leaf structure is often the least interesting biologically.

### Build a Character Matrix From Raw Reads

**Goal:** Go from aligned barcode reads to an allele table and character matrix.
**Approach:** Resolve UMIs, align to the reference, call alleles, group cells into clonal populations, then convert the allele table.

```python
umi_table = cas.pp.resolve_umi_sequence(molecule_table, output_directory='.', min_umi_per_cell=10)
aligned = cas.pp.align_sequences(umi_table, ref_filepath='barcode_reference.fa')
alleles = cas.pp.call_alleles(aligned, ref_filepath='barcode_reference.fa')
alleles = cas.pp.call_lineage_groups(alleles, output_directory='.')
char_matrix, priors, state_map = cas.pp.convert_alleletable_to_character_matrix(alleles)
```

`convert_alleletable_to_character_matrix` returns indel priors alongside the matrix; pass those priors to the solver so frequent low-information scars are down-weighted against homoplasy.

### Integrate Clones With State Using CoSpar

**Goal:** Recover early fate bias from sparse clonal barcodes rather than assuming the manifold encodes fate.
**Approach:** Fit a transition map jointly from clonal observations and transcriptomic similarity, then read fate bias and fate maps.

```python
import cospar as cs
adata = cs.hf.read('lineage_traced.h5ad')
adata = cs.pp.initialize_adata_object(adata, X_clone=adata.obsm['X_clone'], time_info=adata.obs['time_info'])
adata = cs.tmap.infer_Tmap_from_multitime_clones(adata, smooth_array=[15, 10, 5], sparsity_threshold=0.1)
cs.tl.fate_bias(adata, selected_fates=['Monocyte', 'Neutrophil'])
cs.pl.fate_bias(adata, selected_fates=['Monocyte', 'Neutrophil'])
```

CoSpar operationalizes Weinreb 2020: it propagates fate probabilities onto cells lacking clonal labels and is robust to severe downsampling of lineage data, but it needs paired clone + state and does NOT build a phylogenetic tree (clones are flat). CoSpar needs MULTIPLE independent clones to be lineage-informed; with effectively one clone the constraint is vacuous and the transition map degenerates to transcriptomic similarity, the state-only answer CoSpar exists to correct. For tree topology from scars, use Cassiopeia or Startle.

## Threshold and Parameter Rationale

| Parameter | Typical value | Rationale |
|-----------|---------------|-----------|
| min_umi_per_cell | ~10 | below this, allele calls are dominated by sequencing noise |
| missing fraction per cell | drop > ~0.5 | cells missing most characters carry little phylogenetic signal and inflate ambiguity |
| informative character | states in > 1 cell | a scar seen in one cell cannot group lineages; uninformative for topology |
| indel prior weighting | from empirical indel frequencies | frequent microhomology-driven indels are high-homoplasy, low-information; down-weight them |
| barcode library complexity | >> number of founders | small libraries cause collisions (two founders share a barcode -> phantom merged clone) |
| HybridSolver cell_cutoff | ~200 | subclades below the cutoff are solved exactly by ILP; above it, greedily |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Distinct lineages collapse into one clade | missing data coded as the unedited 0 state | keep -1 missing distinct from 0; model dropout, never treat it as unedited |
| Parsimony fuses unrelated cells | homoplasy: independent cells share a frequent indel | weight indels by formation probability; use Startle's star-homoplasy model under heavy convergence |
| Late divisions are unresolved near the leaves | editable array saturated; recording stopped early | use inducible/paced recorders; report the per-site edit fraction distribution |
| Two founders appear as one giant clone | barcode library too small relative to founders -> collision | use library complexity >> cell number; estimate collisions empirically |
| Impossible chimeric clones / character vectors | doublets carry two barcode/scar sets | run doublet detection and barcode-consistency filtering before reconstruction |
| Deep splits flip between solvers | early splits rest on the fewest, most-overwritten characters | report branch support; trust leaf structure more than the root; run a solver panel |
| mtDNA "tree" is actually clonal blobs | low somatic mutation rate; hotspot homoplasy; heteroplasmy drift and selection | claim clonal grouping not deep ordered trees; blacklist NUMTs/RNA-edit/hotspot sites |
| State-based branch call confidently wrong | state underdetermines fate (Weinreb 2020); map is one-to-many | frame fate as a prediction; validate with prospective lineage data, integrate with CoSpar |

## Related Skills

- single-cell/trajectory-inference - state-based pseudotime/velocity that lineage data tests and corrects
- single-cell/preprocessing - QC, doublet handling, and normalization upstream of barcode and clone calls
- single-cell/clustering - cell-type labels annotated onto tree leaves and clones
- phylogenetics/modern-tree-inference - general phylogenetic inference, parsimony vs ML, and branch support

## References

Weinreb C, Rodriguez-Fraticelli A, Camargo FD, Klein AM (2020). Lineage tracing on transcriptional landscapes links state to fate during differentiation (LARRY). Science 367(6479):eaaw3381.
McKenna A, Findlay GM, Gagnon JA, Horwitz MS, Schier AF, Shendure J (2016). Whole-organism lineage tracing by combinatorial and cumulative genome editing (GESTALT). Science 353(6298):aaf7907.
Raj B, Wagner DE, McKenna A, et al. (2018). Simultaneous single-cell profiling of lineages and cell types in the vertebrate brain (scGESTALT). Nat Biotechnol 36(5):442-450.
Alemany A, Florescu M, Baron CS, Peterson-Maduro J, van Oudenaarden A (2018). Whole-organism clone tracing using single-cell sequencing (ScarTrace). Nature 556(7699):108-112.
Spanjaard B, Hu B, Mitic N, et al. (2018). Simultaneous lineage tracing and cell-type identification using CRISPR-Cas9-induced genetic scars (LINNAEUS). Nat Biotechnol 36:469-473.
Biddy BA, Kong W, Kamimoto K, et al. (2018). Single-cell mapping of lineage and identity in direct reprogramming (CellTag). Nature 564:219-224.
Wang SW, Herriges MJ, Hurley K, Kotton DN, Klein AM (2022). CoSpar identifies early cell fate biases from single-cell transcriptomic and lineage information. Nat Biotechnol 40:1066-1074.
Ludwig LS, Lareau CA, Ulirsch JC, et al. (2019). Lineage tracing in humans enabled by mitochondrial mutations and single-cell genomics. Cell 176(6):1325-1339.
Lareau CA, Ludwig LS, Muus C, et al. (2021). Massively parallel single-cell mitochondrial DNA genotyping and chromatin profiling (mtscATAC-seq). Nat Biotechnol 39:451-461.
Miller TE, Lareau CA, Verga JA, et al. (2022). Mitochondrial variant enrichment from high-throughput single-cell RNA sequencing resolves clonal populations (MAESTER). Nat Biotechnol 40:1030-1034.
Jones MG, Khodaverdian A, Quinn JJ, et al. (2020). Inference of single-cell phylogenies from lineage tracing data using Cassiopeia. Genome Biology 21:92.
Sashittal P, Schmidt H, Chan M, Raphael BJ (2023). Startle: a star homoplasy approach for CRISPR-Cas9 lineage tracing. Cell Systems 14(12):1113-1121.
<!-- END FILE: single-cell/lineage-tracing/SKILL.md -->

## 子目录：single-cell/markers-annotation

<!-- BEGIN FILE: single-cell/markers-annotation/SKILL.md -->
---
name: bio-single-cell-markers-annotation
description: Detect cluster marker genes and assign manual cell type labels in single-cell RNA-seq using Scanpy (Python) and Seurat (R). Use when finding genes that distinguish clusters, ranking markers for annotation, scoring gene signatures, hand-labeling clusters, or deciding between Wilcoxon marker ranking and pseudobulk condition DE.
tool_type: mixed
primary_tool: Seurat
---

## Version Compatibility

Reference examples tested with: scanpy 1.10+, Seurat 5.0+, anndata 0.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Marker Gene Detection and Manual Annotation

**"Find marker genes for my clusters"** -> Rank genes that separate each cluster from the rest, then map clusters to cell types using canonical markers.
- Python: `sc.tl.rank_genes_groups()` -> filter by effect size + fraction expressing -> `adata.obs[...].map(labels)`
- R: `Seurat::FindAllMarkers()` -> filter by `avg_log2FC` + `pct.1`/`pct.2` -> `RenameIdents()`

## Governing principle

Marker detection is descriptive ranking, NOT inference. Two distinct questions get sloppily called "DE" and must never be conflated: (1) marker detection - "which genes are higher in cluster X vs the rest?" is a ranking/annotation task where the cell is the unit and Wilcoxon is an acceptable heuristic; (2) condition DE - "which genes change in cell type X between treated and control?" is a population claim that requires biological replicates, where the unit of replication is the sample/donor, not the cell. Question 2 must use pseudobulk (aggregate raw counts per sample x cell type, then DESeq2/edgeR/limma-voom); treating cells as replicates is pseudoreplication and inflates false positives by orders of magnitude (Squair 2021).
Post-clustering marker p-values are double-dipping. Clusters were defined to maximize between-group separation, so testing those same clusters for markers tests a hypothesis built from the data used to test it. The Wilcoxon/t-test null assumes fixed a-priori labels; under a single homogeneous population the statistic does not follow its nominal null, type-I error approaches 1 as resolution rises, and BH correction does nothing because the p-values are invalid before correction. Cluster-marker p-values are descriptive labels, never evidence that a cluster is a real cell type. Rank and filter markers by effect size and fraction-expressing, not by p-value; a gene can be "significant" at p=1e-40 (n is thousands) yet useless as a marker (60% in-group vs 55% out-group).

This skill covers marker discovery for clusters plus manual labeling. Automated reference-based label transfer (SingleR, CellTypist, Azimuth, scANVI) lives in single-cell/cell-annotation. Cross-condition compositional change lives in single-cell/differential-abundance.

## Choosing a marker / DE method

| Method | Question answered | Use when | Fails when |
|--------|-------------------|----------|------------|
| Wilcoxon rank-sum (presto) | Rank cluster markers | Default for labeling a cluster vs rest; fast, non-parametric | Quoted as inference; double-dipping on the clustered data |
| t-test | Rank cluster markers | Quick first pass; scanpy `method=None` default | Heavy-tailed sparse counts violate normality; less robust than Wilcoxon |
| logistic regression (`logreg`/`LR`) | Markers controlling covariates | Need to adjust for batch/covariate when ranking | Slow; needs enough cells; still descriptive |
| ROC (`roc`, Seurat) | Classification power per gene | Want an AUC ranking of marker discriminativeness | No p-value; pure ranking |
| ClusterDE / count splitting | Are the cluster's markers real (FDR-honest)? | Validating that a split is not spurious before naming it | Adds a synthetic-null / data-thinning step; assumptions on the noise model |
| Pseudobulk + DESeq2/edgeR/limma-voom | Condition DE within a cell type | Treatment vs control with >=3 biological replicates per condition | n=1/condition (dispersion unidentifiable); cells-as-replicates |

Marker tools (`rank_genes_groups`, `FindMarkers`) will technically run a treatment-vs-control contrast cell-by-cell and return tidy tiny p-values. That is statistically invalid for a population claim. The tool not stopping the user is why this error is so common. When methods compete, verify current defaults against installed docs.

## Defaults that bite (verify before trusting tutorials)

| Tool | Folklore | Actual default |
|------|----------|----------------|
| scanpy `rank_genes_groups` | Defaults to Wilcoxon | `method=None` resolves to `t-test`; pass `method='wilcoxon'` explicitly |
| Seurat v5 `FindMarkers` `logfc.threshold` | 0.25 | 0.1 in v5 (was 0.25 in v4); permissive, returns more hits |
| Seurat v5 `FindMarkers` `min.pct` | 0.1 | 0.01 in v5 (was 0.1 in v4) |
| Seurat `test.use='wilcox'` | Always fast | Fast only if `presto` is installed; else silent slow base-R fallback |
| Pseudobulk input | Normalized/log values | Aggregate RAW counts (summed), never normalized |

## Scanpy marker detection

**Goal:** Rank cluster-specific markers and filter them by specificity, not p-value alone.

**Approach:** Run Wilcoxon explicitly (scanpy's default is t-test), pull results to a DataFrame with `pts=True` for in/out fraction, then keep genes with a large positive log fold change and a high in-group / low out-group fraction.

```python
import scanpy as sc

adata = sc.read_h5ad('clustered.h5ad')

sc.tl.rank_genes_groups(adata, groupby='leiden', method='wilcoxon', pts=True, corr_method='benjamini-hochberg')
markers = sc.get.rank_genes_groups_df(adata, group=None)

specific = markers[(markers['logfoldchanges'] > 1) & (markers['pct_nz_group'] > 0.5) & (markers['pct_nz_reference'] < 0.25)]
print(specific.groupby('group').head(10)[['group', 'names', 'logfoldchanges', 'pct_nz_group', 'pct_nz_reference']])
```

## Seurat marker detection

**Goal:** Rank markers per cluster and keep specific ones for labeling.

**Approach:** Run `FindAllMarkers` with `only.pos=TRUE`, install presto so Wilcoxon is fast, then rank within cluster by `avg_log2FC` and require a `pct.1`-`pct.2` gap.

```r
library(Seurat)
library(dplyr)

all_markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, logfc.threshold = 0.25, min.pct = 0.1)

specific <- all_markers %>%
    filter(p_val_adj < 0.05, avg_log2FC > 1, (pct.1 - pct.2) > 0.2) %>%
    group_by(cluster) %>%
    slice_max(n = 10, order_by = avg_log2FC)
print(specific)
```

Seurat v5 lowers thresholds to 0.1/0.01, so explicit `logfc.threshold=0.25` and a `pct.1-pct.2` filter restore a marker-grade (specific) shortlist from a permissive run.

## Gene signature scoring

**Goal:** Score each cell for a curated panel without library-size confounding.

**Approach:** Both tools subtract an expression-binned control set; thresholds are dataset-relative and must never be ported as absolute cutoffs.

```python
t_cell_panel = ['CD3D', 'CD3E', 'CD4', 'CD8A', 'CD8B']
sc.tl.score_genes(adata, gene_list=t_cell_panel, ctrl_size=50, n_bins=25, score_name='T_cell_score')
```

```r
seurat_obj <- AddModuleScore(seurat_obj, features = list(c('CD3D', 'CD3E', 'CD4', 'CD8A', 'CD8B')), ctrl = 100, name = 'T_cell_score')
```

scanpy uses 25 control bins, Seurat uses 24 by default (both follow Tirosh 2016) - a real cross-ecosystem non-reproducibility source for small panels.

## Cell-cycle scoring

**Goal:** Assign each cell an S and G2/M score and a phase, to diagnose (and optionally regress) cell-cycle-driven structure.

**Approach:** Score the Tirosh S and G2/M gene panels; both tools ship the lists. Regression is optional and confounded with biology (cycling is a real state in proliferating populations) - diagnose first and regress only when the cycle is a confound, not reflexively.

```python
sc.tl.score_genes_cell_cycle(adata, s_genes=s_genes, g2m_genes=g2m_genes)
```

```r
seurat_obj <- CellCycleScoring(seurat_obj, s.features = cc.genes.updated.2019$s.genes, g2m.features = cc.genes.updated.2019$g2m.genes)
```

Provide `s_genes`/`g2m_genes` as the Tirosh 2016 panels (Seurat's `cc.genes.updated.2019` exposes both lists directly); scanpy ships no built-in list, so load the panels from the reference or a regev-lab gene file.

## Manual cluster labeling

**Goal:** Map cluster ids to cell type names after marker inspection.

**Approach:** Build a cluster->label dictionary from canonical-marker evidence, map it onto cells, and flag unmapped clusters rather than silently dropping them.

```python
cluster_labels = {'0': 'CD4 T', '1': 'CD14 Mono', '2': 'B', '3': 'CD8 T', '4': 'NK', '5': 'FCGR3A Mono'}
adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_labels).fillna('Unassigned')
```

```r
new_ids <- c('0' = 'CD4 T', '1' = 'CD14 Mono', '2' = 'B', '3' = 'CD8 T', '4' = 'NK', '5' = 'FCGR3A Mono')
seurat_obj <- RenameIdents(seurat_obj, new_ids)
seurat_obj$cell_type <- Idents(seurat_obj)
```

## Condition DE the correct way (pseudobulk)

**Goal:** Test which genes change between conditions within a cell type, with valid FDR.

**Approach:** Aggregate RAW counts to one profile per sample x cell type, then hand the count matrix to a bulk engine (DESeq2/edgeR/limma-voom) which estimates dispersion across biological replicates. Run each cell type separately so a one-cell-type effect is not diluted.

```python
import scanpy as sc

cell_type = adata[adata.obs['cell_type'] == 'CD14 Mono']
pseudobulk = sc.get.aggregate(cell_type, by='sample', func='sum')
counts_df = pseudobulk.layers['sum']
```

```r
pb <- AggregateExpression(seurat_obj, group.by = c('cell_type', 'sample'), assays = 'RNA', layer = 'counts')$RNA
```

Pull the summed counts slot, build a sample-level design (condition + covariates), and run DESeq2/edgeR; see differential-expression/deseq2-basics for the modeling step. Never run DE on batch-corrected or normalized expression.

## Canonical PBMC markers (context-dependent, validate per dataset)

| Cell type | Markers | Cell type | Markers |
|-----------|---------|-----------|---------|
| CD4 T | CD3D, CD4, IL7R | NK | NKG7, GNLY, NCAM1 |
| CD8 T | CD3D, CD8A, CD8B | CD14 Mono | CD14, LYZ, S100A8 |
| B | MS4A1, CD79A, CD19 | FCGR3A Mono | FCGR3A, MS4A7 |
| DC | FCER1A, CST3 | Platelet | PPBP, PF4 |

A marker is a conditional statement, not a property of a gene: a marker in blood may be expressed broadly in tumor, and "vs rest" markers depend on what "rest" is. Re-validate any ported panel.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Thousands of "significant" markers between two visually-similar clusters | Over-clustering + double-dipping inflation | Significance-test the split (scSHC/ClusterDE) or merge; never quote raw marker p-values as proof of a cell type |
| Marker p-values used as evidence clusters are real | Selective-inference violation; BH cannot fix invalid p-values | Report markers as descriptive labels; validate identity with orthogonal markers |
| Condition DE returns huge gene lists, none replicate | Cells treated as replicates (pseudoreplication) | Aggregate to pseudobulk per sample x cell type; test across donors |
| `FindAllMarkers` hangs for minutes | presto not installed; slow base-R Wilcoxon | `install.packages('presto')` (or `remotes::install_github('immunogenomics/presto')`) |
| Same top markers in every cluster | Resolution too high; clusters split one population | Lower resolution / merge; check stability |
| Gene cutoff ported from another dataset misclassifies cells | Module scores are dataset-relative | Set thresholds from this dataset's score distribution |
| NaN / degenerate logFC and p-values from marker ranking | Only one cluster present, so the "vs rest" reference is empty | Marker ranking needs >=2 groups; subcluster the population or report it as a single homogeneous type |
| "DE genes" between conditions but no gene changed per cell | Subpopulation proportions shifted (compositional confound) | Pair condition DE with single-cell/differential-abundance |

## Related Skills

- clustering - Cluster cells before finding markers
- preprocessing - Normalize and select features before marker detection
- cell-annotation - Automated reference-based label transfer (complements manual marker labeling)
- differential-abundance - Test whether cell-type proportions changed between conditions
- differential-expression/deseq2-basics - Pseudobulk condition DE engine for the aggregated counts
- differential-expression/de-results - Shrink, filter, and interpret pseudobulk DE results
- pathway-analysis/go-enrichment - Functional interpretation of marker / DE gene lists

## References

- Squair et al. 2021, Nat Commun 12:5692 - cells-as-replicates inflate false positives; top DE methods aggregate to pseudobulk.
- Crowell et al. 2020, Nat Commun 11:6077 - muscat; pseudobulk gives well-calibrated FDR for multi-sample multi-condition DS analysis.
- Neufeld et al. 2024, Biostatistics 25(1):270-287 - count splitting / valid post-clustering inference; Poisson thinning breaks under overdispersion.
- Lee & Han 2024, Bioinformatics 40(8):btae498 - properly-offset pseudobulk is statistically equivalent to a GLMM.
- Tirosh et al. 2016, Science 352:189-196 - control-set module scoring underlying score_genes / AddModuleScore.
<!-- END FILE: single-cell/markers-annotation/SKILL.md -->

## 子目录：single-cell/metabolite-communication

<!-- BEGIN FILE: single-cell/metabolite-communication/SKILL.md -->
---
name: bio-single-cell-metabolite-communication
description: Infers metabolite-mediated cell-cell communication from scRNA-seq by scoring enzyme-to-sensor pairs (MEBOCOST), with metabolic flux (scFEA), FBA state (Compass), and neurotransmitter (NeuronChat) alternatives. Use when studying metabolic crosstalk between cell types, predicting metabolite secretion and sensing, or deciding which metabolic-communication method fits and how speculative the result is.
tool_type: python
primary_tool: MeboCost
---

## Version Compatibility

Reference examples tested with: mebocost 1.0+, scanpy 1.10+, anndata 0.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metabolite-Mediated Cell Communication

**"Find which cell types exchange metabolites"** -> Infer a metabolite's presence from the cells expressing its synthesizing enzymes, then score communication to cells expressing its sensor or transporter.
- Python: `mebocost.create_obj()` -> `infer_commu()` (metabolite-sensor scoring)

## Governing Principle

Metabolite-mediated communication is a DOUBLE inference and the most speculative layer of cell-cell communication. scRNA-seq never measures metabolites; their levels are inferred from the expression of synthesizing enzymes, then a chain of further assumptions is stacked: enzyme mRNA -> enzyme protein -> enzyme ACTIVITY -> metabolic FLUX -> intracellular metabolite POOL -> SECRETION/export -> extracellular concentration in space -> import/SENSING by the receiver. Every arrow is an assumption and none is measured. On top of this sit all the ligand-receptor caveats (proxy, no spatial geometry in dissociated data, abundance and depth confounds, ambient RNA), so the output is hypothesis-generation ONLY. A defensible claim is never "cell A produces metabolite X" but "cell A expresses the machinery consistent with producing X". Validation is non-optional and means metabolomics (LC-MS), mass-spectrometry imaging (MALDI/DESI), isotope tracing, or perturbation of the enzyme or sensor - not another expression-based method. State the enzyme->flux->level->sensing chain explicitly whenever reporting a result.

## Method Decision Table

| Method | Tests what / null | Use when | Fails when |
|--------|-------------------|----------|------------|
| MEBOCOST | Metabolite SENDER->RECEIVER communication; estimates an extracellular metabolite level from producing-enzyme expression, scores enzyme->sensor pairs, permutation FDR over shuffled labels | The question is metabolite crosstalk between cell types (enzyme-sensor), analogous to CellPhoneDB for L-R | Synthase mRNA present but substrate/cofactor absent; transporter "sensor" is bidirectional/promiscuous so sender/receiver direction is wrong; no spatial geometry |
| scFEA | Per-cell metabolic FLUX through modules; graph neural network solver enforcing flux balance (in approximately out) | The question is relative flux per cell to FEED metabolite reasoning, not direct communication | Read as absolute mol/s (fluxes are relative); needs the matching module/stoichiometry files for the species; not a CCC tool itself |
| Compass | Per-cell metabolic STATE via flux-balance analysis; reaction penalty inversely proportional to enzyme expression over Recon2, outputs a score per reaction per cell | Comparing metabolic state between conditions (e.g. pathogenic vs non-pathogenic cells) | Used to claim a SECRETED metabolite communicates (output is reaction favorability, not secretion); assumes steady state, questionable for differentiated non-proliferating cells; heavy compute, micropool first |
| NeuronChat | Neurotransmitter/neuromodulator communication; vesicular release machinery and synthesis enzymes vs target receptor abundance | Neural systems specifically (glutamate, GABA, dopamine, serotonin, neuropeptides) | Applied outside neural tissue; same expression-proxy and geometry limits |

Methods and their curated databases evolve; before committing, verify current best practice, the metabolite-sensor database version, and required config/species files against the installed package docs.

## Confounds That Mimic Communication

| Confound | How it manufactures a fake signal | Mitigation |
|----------|-----------------------------------|------------|
| Compounded inference | Enzyme mRNA is a poor proxy for metabolite concentration (post-transcriptional control, substrate availability, allostery, compartmentalization), so a "secreted" metabolite may never be made | State the enzyme->flux->level->sensing chain; require metabolomics/MSI/tracing before any production claim |
| Bidirectional transporters | A transporter labeled a "sensor" may export rather than import, and many move several metabolites, so sender/receiver direction can be inverted | Treat transporter-based calls as lower-confidence than dedicated-receptor calls; check transport directionality literature |
| Ambient RNA | Soup of highly expressed transcripts inflates enzyme/sensor "expression" in clusters that do not transcribe them | Decontaminate (SoupX/DecontX/CellBender) before inference |
| Cell-type abundance and depth | Larger clusters tighten the permutation null and deeper cells detect more genes, inflating significance independent of biology | Down-sample, run on integrated counts, do not compare raw counts across conditions |
| No spatial geometry | Metabolites diffuse and degrade, but dissociated data has no coordinates, so a "communication" may be between cells never co-located | Validate proximity with spatial metabolomics/MSI; do not claim neighbor exchange from dissociated data |

## Run MEBOCOST

**Goal:** Score metabolite sender->receiver communication between cell types with permutation significance.

**Approach:** Build a MEBOCOST object from a log-normalized AnnData with cell-type labels and a config file pointing at the metabolite-sensor database, then run permutation inference; results carry both the communication score and an FDR.

```python
from mebocost import mebocost
import scanpy as sc

adata = sc.read_h5ad('adata_annotated.h5ad')   # log-normalized, gene SYMBOLS not Ensembl IDs

# config_path points to mebocost.conf listing the metabolite-enzyme-sensor database paths
# cutoff_prop=0.15: a gene must be expressed in >=15% of a group to count (dropout floor)
# species MUST match the data: mouse data against the human enzyme/sensor DB returns almost nothing
mebo = mebocost.create_obj(adata=adata, group_col='cell_type', condition_col=None,
                           met_est='mebocost', config_path='./mebocost.conf', species='human',
                           cutoff_exp='auto', cutoff_met='auto', cutoff_prop=0.15,
                           sensor_type='All', thread=8)

# n_shuffle=1000: label-permutation null for FDR; min_cell_number=10 drops tiny groups
commu_res = mebo.infer_commu(n_shuffle=1000, seed=12345, Return=True,
                             min_cell_number=10, pval_method='permutation_test_fdr',
                             pval_cutoff=0.05, thread=None)
```

## Filter and Summarize Results

**Goal:** Extract the significant, defensible metabolite communications.

**Approach:** Filter on the permutation FDR (not the raw p-value), then summarize by metabolite and by sender->receiver pair; column names are capitalized in the result table.

```python
sig = commu_res[commu_res['permutation_test_fdr'] < 0.05].copy()

# Result columns: Sender, Receiver, Metabolite_Name, Sensor, Annotation (Transporter/Enzyme),
# Commu_Score, Norm_Commu_Score, met_in_sender, sensor_in_receiver, permutation_test_fdr
sig['pair'] = sig['Sender'] + ' -> ' + sig['Receiver']
top_metabolites = sig['Metabolite_Name'].value_counts().head(10)
top_pairs = sig['pair'].value_counts().head(10)

# Transporter-based sensors are lower-confidence (bidirectional); separate them
transporter_calls = sig[sig['Annotation'] == 'Transporter']
```

## Compare Conditions

**Goal:** Find metabolite communications that differ between conditions (e.g. tumor vs normal).

**Approach:** Either pass `condition_col` to a single object, or run MEBOCOST separately per condition subset and compare the significant sets; never compare raw interaction counts across conditions without controlling for cell number and depth.

```python
results = {}
for cond in adata.obs['condition'].unique():
    sub = adata[adata.obs['condition'] == cond].copy()
    obj = mebocost.create_obj(adata=sub, group_col='cell_type', met_est='mebocost',
                              config_path='./mebocost.conf', species='human',
                              cutoff_prop=0.15, thread=8)
    results[cond] = obj.infer_commu(n_shuffle=1000, seed=12345, Return=True,
                                    min_cell_number=10, pval_cutoff=0.05)
# A "differential" metabolite call (significant in one condition only) is a HYPOTHESIS for metabolomics
```

## Threshold and Permutation Rationale

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `cutoff_prop` | 0.15 | A chosen dropout floor (MEBOCOST tutorials use 0.15-0.25, not a fixed package default): a gene expressed in <15% of a group is mostly dropout, but real low-abundance signaling is also discarded, so tune per dataset |
| `cutoff_exp` / `cutoff_met` | 'auto' | MEBOCOST data-derived thresholds for calling a gene/metabolite present; set manually only with a documented reason |
| `n_shuffle` | 1000 | Stable label-permutation FDR; the FDR is about label shuffling, not actual metabolite flux |
| `min_cell_number` | 10 | Groups under ~10 cells give unstable mean expression and inflated scores |
| `permutation_test_fdr` cutoff | 0.05 | Filter on the FDR, not the raw permutation p-value; significance is statistical, not a measured concentration |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `KeyError: 'metabolite'` / `'pval'` | Result columns are capitalized (Sender, Receiver, Metabolite_Name, Commu_Score, permutation_test_fdr) | Use the exact column names from `commu_res.columns` |
| `AttributeError: module 'mebocost' has no attribute 'create_obj'` | Wrong import; `create_obj` lives in the submodule | `from mebocost import mebocost` then `mebocost.create_obj(...)` |
| Almost no metabolites detected | Genes are Ensembl IDs, data is not log-normalized, `config_path` database is missing, or `species` does not match the data (mouse data run against the human enzyme/sensor DB) | Convert to gene symbols, log-normalize, point `config_path` at a valid mebocost.conf, set `species` to match the organism |
| A cell type "secretes" a metabolite implausibly | Synthase mRNA present but substrate/cofactor absent, or ambient RNA inflated the enzyme | Decontaminate ambient RNA; treat as "machinery consistent with", validate with metabolomics |
| Sender/receiver direction looks reversed | Sensor is a bidirectional/promiscuous transporter | Check `Annotation == 'Transporter'` calls separately; confirm transport direction |
| More communications in condition B than A | Counts scale with cell number and depth | Compare score magnitudes or matched subsets, not raw counts |

## Related Skills

- single-cell/cell-communication - Ligand-receptor CCC; the single-inference counterpart this skill mirrors at one extra remove
- single-cell/cell-annotation - Cell-type labels define metabolite senders and receivers
- single-cell/preprocessing - Log-normalization, gene-symbol mapping, and ambient-RNA decontamination happen here, before inference
- metabolomics/pathway-mapping - Places inferred metabolites in pathway context and informs which to prioritize
- metabolomics/isotope-tracing - Orthogonal flux validation that a producing cell actually makes the metabolite
- systems-biology/flux-balance-analysis - Genome-scale FBA underlying Compass-style per-cell metabolic state

## References

- Zheng R, et al. MEBOCOST maps metabolite-mediated intercellular communications using single-cell RNA-seq. Nucleic Acids Res 53(12):gkaf569 (2025). PMID 40568942.
- Alghamdi N, et al. A graph neural network model to estimate cell-wise metabolic flux using single-cell RNA-seq data [scFEA]. Genome Res 31(10):1867-1884 (2021).
- Wagner A, et al. Metabolic modeling of single Th17 cells reveals regulators of autoimmunity [Compass]. Cell 184(16):4168-4185 (2021).
- Zhao W, et al. Inferring neuron-neuron communications from single-cell transcriptomics through NeuronChat. Nat Commun 14(1):1128 (2023).
- Dimitrov D, et al. Comparison of methods and resources for cell-cell communication inference from single-cell RNA-Seq data. Nat Commun 13:3224 (2022). [discordance framing]
- Young MD, Behjati S. SoupX removes ambient RNA contamination from droplet-based single-cell RNA sequencing data. GigaScience 9(12):giaa151 (2020).
<!-- END FILE: single-cell/metabolite-communication/SKILL.md -->

## 子目录：single-cell/multimodal-integration

<!-- BEGIN FILE: single-cell/multimodal-integration/SKILL.md -->
---
name: bio-single-cell-multimodal-integration
description: Integrate multimodal single-cell data (CITE-seq RNA+protein, 10x Multiome RNA+ATAC, unpaired/diagonal RNA+ATAC) and choose the right joint method. Use when classifying an integration task by anchor structure (paired vs unpaired), denoising CITE-seq ADT background before joint embedding, picking between WNN, totalVI, MultiVI, MOFA+, GLUE, or Seurat v5 bridge integration, or diagnosing why a modality dominates a joint clustering.
tool_type: mixed
primary_tool: Seurat
---

## Version Compatibility

Reference examples tested with: scanpy 1.10+, Seurat 5.0+, anndata 0.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Multimodal Integration

**"Jointly analyze my CITE-seq / Multiome / unpaired multi-omic data"** -> Classify the task by anchor structure, denoise each modality in its native pipeline, then build one joint representation.
- R: `Seurat::FindMultiModalNeighbors()` (WNN), `Signac` (ATAC LSI), `dsb::DSBNormalizeProtein()` (ADT denoising), `PrepareBridgeReference()` (v5 bridge)
- Python: `muon`/`mudata` (MuData container), `scvi.model.TOTALVI` / `MULTIVI`, `MOFA2`/`muon.tl.mofa`, `scglue` (diagonal)

## Governing Principle

Classify the integration task by its anchor structure FIRST, because the anchor decides which algorithm class is even applicable (Argelaguet 2021).
- Horizontal: same modality, different cells; anchor = shared features (batch correction, not this skill).
- Vertical (paired, same cell): multiple modalities measured in the same cells; anchor = shared cells. CITE-seq, 10x Multiome.
- Diagonal (unpaired): different modalities in different cells, no shared cells and no shared features; correspondence is inferred from prior knowledge. Independent scRNA + scATAC.
- Mosaic: partially observed grid of (modalities x batches); some blocks present, some missing.

Paired vs unpaired is the master fork: paired correspondence is known a priori (WNN, totalVI, MultiVI, MOFA+), unpaired/diagonal correspondence must be inferred (GLUE, Seurat v5 bridge), mosaic mixes both (MultiVI, StabMap). Two separately-paired datasets that share only one modality (for example a 10x Multiome and a CITE-seq experiment sharing only RNA) are a mosaic problem: anchor on the shared RNA and impute or bridge the modality-specific blocks with StabMap, MultiVI, or Seurat v5 bridge integration rather than forcing a single WNN.

CITE-seq ADT background is a three-part mixture, not one "ambient" term: (1) ambient antibody captured in every droplet including empties, (2) cell-intrinsic non-specific binding (Fc receptors, sticky dying cells) that does NOT appear in empties, (3) spillover/index hopping between barcodes. Denoise ADT (DSB or totalVI's built-in background mixture) BEFORE any joint embedding; raw or CLR-only ADT carries this background into the joint graph.

WNN can be dominated by the noisier modality: weights reward local neighbor predictability, and a handful of high-variance or saturating ADT features can manufacture self-consistent neighborhoods and get up-weighted despite carrying less biology. Report the per-cell weight distribution and check whether clustering survives down-weighting the suspect modality.

Imputed modalities are inferences, not measurements: MultiVI/StabMap/Cobolt impute the missing modality for unpaired cells, and gene-activity scores from ATAC approximate RNA. Differential expression or marker calls on imputed values are model-dependent and must be flagged as such.

## Classify the Task: Anchor Structure -> Method Class

| Anchor structure | What is shared | Example assay | Method class |
|---|---|---|---|
| Vertical / paired | Same cells | CITE-seq, 10x Multiome | WNN, totalVI, MultiVI(paired), MOFA+, mojitoo |
| Diagonal / unpaired | Nothing (prior graph) | Independent scRNA + scATAC | GLUE, Seurat v5 bridge, LIGER |
| Mosaic | Some modalities only | Batch A RNA+ATAC, batch B RNA | MultiVI, StabMap, Cobolt, totalVI(partial) |

When methods compete, verify the current best-practice default against the installed tool docs before committing; the field moves and defaults drift across minor versions.

## Method Decision Table (Paired CITE-seq / Multiome)

| Method | Model / assumption | Use when | Fails when |
|---|---|---|---|
| WNN (Seurat) | Per-cell, per-modality weights from cross-modality neighbor prediction; one weighted graph | Fast joint embedding/clustering of one well-normalized paired dataset | Protein background not removed upstream; noisy/saturating modality dominates; not for unpaired/mosaic |
| totalVI (scvi-tools) | Conditional VAE; RNA NB/ZINB, each protein a 2-component NB mixture (background+foreground) | Need denoised protein, principled DE, batch integration, merging different antibody panels | Tiny datasets (VAE overfits); no GPU and very large data; protein-specific background structure not captured by one per-cell factor |
| MultiVI (scvi-tools) | Single joint VAE over RNA+ATAC(+protein); mosaic-capable, imputes missing modality | Paired+unpaired RNA/ATAC mixed (mosaic); want generative DE/DA | "batch" key is the modality indicator, not sequencing batch; imputed modalities treated as measured |
| MOFA+ (MOFA2) | Linear Bayesian group factor analysis; sparse factors, per-modality variance explained | Interpreting shared vs modality-specific axes of variation (exploratory/explanatory) | Used for clustering/denoising; likelihood mismatched to data; expecting batch correction within a view |
| mojitoo | CCA across precomputed per-modality reductions; fast, parameter-free | Quick paired joint reduction from existing PCA/LSI slots | No knob to down-weight a noisy modality; bounded by input reductions; paired only |

## Method Decision Table (Unpaired / Diagonal / Mosaic)

| Method | Model / assumption | Use when | Fails when |
|---|---|---|---|
| GLUE (scglue) | Per-modality VAEs + prior feature graph (peak-near-gene); adversarial cell alignment | Unpaired diagonal scRNA + scATAC; want regulatory inference as a byproduct | Genome-build/coordinate mismatch yields an empty guidance graph and garbage alignment; adversarial over-mixing of distinct states |
| Seurat v5 bridge | Multiome bridge dataset = dictionary linking query modality to reference modality | Mapping a query (scATAC) onto a reference built in another modality (scRNA) | Poor/batch-mismatched bridge propagates error; rare query-only populations mislabeled |
| StabMap | Mosaic topology from shared features; project all cells via shortest paths | Mosaic with informative unshared features that cannot be dropped | Unshared-feature chaining compounds error per hop |
| Cobolt / scMoMaT | Generative shared latent over joint + single-modality datasets | Mosaic where a generative latent is preferred over feature chaining | DE/marker calls made on imputed values |

## ADT Normalization: CLR vs DSB

| Method | What it does | Use when | Fails when |
|---|---|---|---|
| CLR (centered log-ratio) | Rescales compositionally; Seurat `NormalizeData(method="CLR", margin=2)` | Quick, no empty droplets available; small panels | Does NOT remove background; geometric-mean denominator distorted by saturating high-abundance ADTs |
| DSB | Ambient correction from empty droplets + per-cell technical denoising via 2-component mixture + isotype controls | Raw/unfiltered matrix available (needs empty droplets); want background removed before embedding | No empty droplets retained; protein-specific non-specific binding (one per-cell factor under/over-corrects); no clearly bimodal proteins |

Seurat's CLR margin is genuinely ambiguous across versions (margin=2 = per-feature is the WNN-tutorial recommendation for large panels); verify with `?NormalizeData` on the installed version.

## CITE-seq: Denoise ADT, Then Joint Embed (Seurat)

**Goal:** Remove ADT background with DSB before WNN, because WNN does not denoise protein.

**Approach:** Estimate ambient from empty droplets and per-cell technical noise from a mixture plus isotype controls, then feed denoised ADT into the standard PCA -> WNN flow.

```r
library(dsb)
library(Seurat)

raw <- Read10X('raw_feature_bc_matrix/')           # unfiltered: contains empty droplets
cells <- Read10X('filtered_feature_bc_matrix/')    # called cells

adt_cells <- as.matrix(cells[['Antibody Capture']])
adt_empty <- as.matrix(raw[['Antibody Capture']][, setdiff(colnames(raw[['Antibody Capture']]), colnames(adt_cells))])

# isotype.control.name.vec must name the ACTUAL isotype rows (often IgG1/IgG2a/Mouse-IgG2b-Ctrl); the regex below misses those
# When isotypes are absent or not matched, set use.isotype.control = FALSE (keep denoise.counts = TRUE) and pass real names explicitly
adt_dsb <- DSBNormalizeProtein(
    cell_protein_matrix = adt_cells,
    empty_drop_matrix = adt_empty,
    denoise.counts = TRUE,
    use.isotype.control = TRUE,
    isotype.control.name.vec = grep('[Ii]sotype|IgG', rownames(adt_cells), value = TRUE)
)
```

## CITE-seq: WNN Joint Clustering (Seurat)

**Goal:** Build one weighted-NN graph from denoised RNA and ADT and cluster on it.

**Approach:** Reduce each modality independently (PCA on RNA, PCA on the small ADT panel), then learn per-cell modality weights and cluster/embed on the joint graph.

```r
obj[['ADT']] <- CreateAssay5Object(data = adt_dsb)        # DSB output is already normalized data
DefaultAssay(obj) <- 'RNA'
obj <- NormalizeData(obj) |> FindVariableFeatures() |> ScaleData() |> RunPCA(reduction.name = 'pca')

DefaultAssay(obj) <- 'ADT'
VariableFeatures(obj) <- rownames(obj[['ADT']])
obj <- ScaleData(obj) |> RunPCA(reduction.name = 'apca', npcs = min(18, nrow(obj[['ADT']]) - 1))

# dims.list matched to informative dims; small ADT panels saturate by ~1:18
obj <- FindMultiModalNeighbors(obj, reduction.list = list('pca', 'apca'), dims.list = list(1:30, 1:18))
obj <- FindClusters(obj, graph.name = 'wsnn', algorithm = 3)   # algorithm 3 = SLM (the tutorial choice), NOT Leiden
obj <- RunUMAP(obj, nn.name = 'weighted.nn', reduction.name = 'wnn.umap')

# Inspect the per-cell weight distribution; a single dominant modality is a red flag
VlnPlot(obj, features = 'RNA.weight', group.by = 'seurat_clusters')
```

## CITE-seq: totalVI (Python, denoise + DE in one model)

**Goal:** Jointly model RNA + protein with explicit protein background, yielding a denoised latent space and foreground probabilities.

**Approach:** Register a MuData object, train the conditional VAE, then read the latent representation and per-protein foreground probability.

```python
import scvi
import mudata as md

# mdata holds .mod['rna'] (raw counts) and .mod['prot'] (raw ADT counts)
scvi.model.TOTALVI.setup_mudata(
    mdata, rna_layer='counts', protein_layer=None,
    modalities={'rna_layer': 'rna', 'protein_layer': 'prot'}
)
model = scvi.model.TOTALVI(mdata)
model.train()

mdata.obsm['X_totalVI'] = model.get_latent_representation()
fg = model.get_protein_foreground_probability()        # 1 - background mixing weight per protein per cell
denoised_rna, denoised_prot = model.get_normalized_expression()
```

## Multiome (RNA + ATAC, same cell): Native Pipelines, Then Join

**Goal:** Process each modality in its own statistics before joining, because RNA and ATAC have incompatible distributions.

**Approach:** PCA on RNA, TF-IDF + LSI on ATAC (drop depth-correlated components), then WNN. See scatac-analysis for ATAC QC and the binarization/depth-component caveats.

```r
library(Signac)
DefaultAssay(obj) <- 'RNA'
obj <- NormalizeData(obj) |> FindVariableFeatures() |> ScaleData() |> RunPCA()

DefaultAssay(obj) <- 'ATAC'
obj <- RunTFIDF(obj) |> FindTopFeatures(min.cutoff = 'q0') |> RunSVD()
DepthCor(obj)                                          # diagnose which LSI components track depth

# dims = 2:30 drops LSI_1 ONLY if DepthCor confirms it tracks depth (usually true, not guaranteed)
obj <- FindMultiModalNeighbors(obj, reduction.list = list('pca', 'lsi'), dims.list = list(1:30, 2:30))
obj <- RunUMAP(obj, nn.name = 'weighted.nn', reduction.name = 'wnn.umap')
obj <- FindClusters(obj, graph.name = 'wsnn', algorithm = 3)
```

Merging multiome datasets requires a common peak set: re-quantify all cells against unified peaks, or peak-boundary differences manufacture spurious batch structure. The ATAC gene-activity matrix is an approximation, not measured RNA; do not conflate it with the RNA modality.

## MOFA+ (interpretable shared/specific factors)

**Goal:** Decompose modalities into shared latent factors with per-modality variance explained.

**Approach:** Build a MOFA object from per-modality matrices, set likelihoods to match each data type, run, then interpret factor loadings.

```python
import muon as mu

# likelihoods must match data: gaussian for scaled RNA, bernoulli for binarized ATAC, poisson for counts
mu.tl.mofa(mdata, n_factors=15, outfile='mofa_model.hdf5')   # writes mdata.obsm['X_mofa']
```

## Unpaired / Diagonal: GLUE (Python)

**Goal:** Align independent scRNA and scATAC with no shared cells via a prior feature graph.

**Approach:** Configure each dataset with a count-appropriate probabilistic model, build a gene-anchored guidance graph, fit GLUE, then read aligned embeddings.

```python
import scglue

scglue.models.configure_dataset(rna, 'NB', use_highly_variable=True, use_rep='X_pca')     # NB needs RAW counts
scglue.models.configure_dataset(atac, 'ZINB', use_highly_variable=True, use_rep='X_lsi')
graph = scglue.genomics.rna_anchored_guidance_graph(rna, atac)     # peak-near-gene prior; coords must share genome build
glue = scglue.models.fit_SCGLUE({'rna': rna, 'atac': atac}, graph)
rna.obsm['X_glue'] = glue.encode_data('rna', rna)
atac.obsm['X_glue'] = glue.encode_data('atac', atac)
```

Verify cell-type structure is preserved (not just modality overlap); adversarial alignment can over-mix distinct populations.

## MuData Housekeeping

After per-modality QC, modalities hold different cell sets; `muon.pp.intersect_obs(mdata)` before any paired analysis. Editing a modality-local `mdata.mod['rna'].obs` needs `mdata.update()` to propagate to the global `mdata.obs`. R round-trips (MuDataSeurat, zellkonverter) are lossy; plan to stay in one ecosystem.

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| WNN clustering driven entirely by ADT | A few saturating high-variance proteins dominate the neighbor graph | Report per-cell weight distribution; down-weight or denoise ADT (DSB); re-check clustering stability |
| "Background" smear in every ADT cluster | Ran WNN/CLR without empty-droplet denoising | Run DSB (needs raw/unfiltered matrix) or totalVI before joint embedding |
| DSB errors / nonsense output | Passed a filtered cell matrix only (no empty droplets) | Supply `empty_drop_matrix` from the raw/unfiltered matrix |
| Spurious batch structure after merging multiome | Per-dataset peak sets, not a unified set | Re-quantify all cells against one common peak set |
| GLUE produces a blob / no alignment | Guidance graph near-empty from genome-build/coordinate mismatch | Align RNA gene coords and ATAC peaks to the same build before building the graph |
| RNA and protein disagree for a marker | Often real post-transcriptional biology (stability, trafficking, lag), not an artifact | Do not "correct away"; treat single-gene discordance as informative |
| MultiVI batch effects persist | The `batch_key` was set to the modality indicator, not sequencing batch | Add a separate covariate for the real batch |
| DE on a modality looks too clean | Computed on imputed/gene-activity values, not measurements | Flag imputed-modality DE as model-dependent; validate against a measured modality |

## Related Skills

- single-cell/scatac-analysis - ATAC QC, TF-IDF/LSI, gene-activity caveats for the Multiome ATAC half
- single-cell/preprocessing - per-modality RNA QC and normalization before integration
- single-cell/clustering - clustering and UMAP on the joint graph
- single-cell/batch-integration - horizontal (same-modality, cross-sample) correction
- single-cell/markers-annotation - marker-based interpretation of joint clusters
- atac-seq/motif-deviation - chromVAR TF activity on the Multiome ATAC modality
- pathway-analysis/go-enrichment - functional interpretation of modality-specific factors

## References

Argelaguet R, Cuomo ASE, Stegle O, Marioni JC. Computational principles and challenges in single-cell data integration. Nat Biotechnol 39(10):1202-1215 (2021).
Stoeckius M, Hafemeister C, Stephenson W, et al. Simultaneous epitope and transcriptome measurement in single cells (CITE-seq). Nat Methods 14:865-868 (2017).
Mulè MP, Martins AJ, Tsang JS. Normalizing and denoising protein expression data from droplet-based single-cell profiling (DSB). Nat Commun 13:2099 (2022).
Hao Y, Hao S, Andersen-Nissen E, et al. Integrated analysis of multimodal single-cell data (WNN). Cell 184(13):3573-3587 (2021).
Gayoso A, Steier Z, Lopez R, et al. Joint probabilistic modeling of single-cell multi-omic data with totalVI. Nat Methods 18:272-282 (2021).
Ashuach T, Gabitto MI, Koodli RV, et al. MultiVI: deep generative model for the integration of multimodal data. Nat Methods 20(8):1222-1231 (2023).
Argelaguet R, Arnol D, Bredikhin D, et al. MOFA+: a statistical framework for comprehensive integration of multi-modal single-cell data. Genome Biol 21:111 (2020).
Cao Z-J, Gao G. Multi-omics single-cell data integration and regulatory inference with graph-linked unified embedding (GLUE). Nat Biotechnol 40(10):1458-1466 (2022).
Hao Y, Stuart T, Kowalski MH, et al. Dictionary learning for integrative, multimodal and scalable single-cell analysis (Seurat v5 bridge). Nat Biotechnol 42:293-304 (2024).
Bredikhin D, Kats I, Stegle O. MUON: multimodal omics analysis framework. Genome Biol 23:42 (2022).
Ghazanfar S, Guibentif C, Marioni JC. Stabilized mosaic single-cell data integration using unshared features (StabMap). Nat Biotechnol 42(2):284-292 (2024).
Yin Y, et al. Characterization and decontamination of background noise in droplet-based single-cell protein expression data with DecontPro. Nucleic Acids Res 52(1):e4 (2024).
<!-- END FILE: single-cell/multimodal-integration/SKILL.md -->

## 子目录：single-cell/perturb-seq

<!-- BEGIN FILE: single-cell/perturb-seq/SKILL.md -->
---
name: bio-single-cell-perturb-seq
description: Analyze Perturb-seq / CROP-seq single-cell CRISPR screens. Use when assigning guides as a mixture problem, removing non-perturbed escaper cells with Mixscape, choosing a calibrated test (SCEPTRE conditional resampling) over naive DE, quantifying effect size with E-distance, separating compositional shifts from within-state expression change, or judging whether a perturbation-prediction foundation model actually beats a baseline.
tool_type: python
primary_tool: Pertpy
---

## Version Compatibility

Reference examples tested with: pertpy 0.9+, scanpy 1.10+, anndata 0.10+, sceptre 0.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Perturb-seq Analysis

**"Analyze my Perturb-seq CRISPR screen"** -> Assign guides, remove cells that received a guide but were not perturbed, test each perturbation with a calibrated method, and separate "moves cells" from "changes cells".
- Python: `pertpy.pp.GuideAssignment`, `pertpy.tl.Mixscape`, `pertpy.tl.Distance`/`DistanceTest`, `pertpy.tl.Milo`/`Sccoda`
- R: `sceptre` (conditional-resampling test), `Seurat` Mixscape, `scMAGeCK`

## Governing Principle

Guide assignment is a mixture problem, not a threshold. Each cell's per-guide UMI vector mixes true integration with ambient guide contamination (free transcripts, index hopping, doublets), and the ambient pool is structured: it is dominated by whichever guides are most abundant in the library, so a flat UMI cutoff preferentially mis-assigns cells to common guides and calls rare-guide cells negative. Call guides by a per-guide background/foreground mixture posterior, and report the perturbed fraction. MOI changes the meaning: low-MOI (~1 guide/cell) gives clean single-gene attribution but discards 70-90% of cells; high-MOI is for combinatorial designs but measures every single-gene effect in a co-perturbed background.

Assignment is not effective perturbation. A cell can carry a guide yet be transcriptionally wild-type: incomplete CRISPR-KO editing, in-frame indels, escapers, or weak CRISPRi knockdown. The "perturbed" population is a mixture of truly perturbed and effectively-wild-type cells, which attenuates every effect-size estimate toward the null. Mixscape removes the non-perturbed cells via a local non-targeting-neighbor perturbation signature before testing. Deep caveat: an all-NP result is not evidence the gene is non-functional, because it is confounded with low guide efficiency; Mixscape cannot distinguish "no phenotype" from "no editing".

Naive DE is miscalibrated by depth and pseudoreplication. The probability of detecting a guide covaries with sequencing depth, and depth also drives expression detection, so a plain Wilcoxon/NB test between guide-positive and NT cells has inflated type-I error. SCEPTRE fixes this with conditional resampling: it models P(cell receives this guide | technical covariates incl. depth) and resamples the assignment to build a calibrated null, robust to misspecification of the expression model. Separately, treating thousands of cells from one transfection as independent replicates inflates significance (pseudoreplication, Squair 2021); the replication unit is the transfection, so pseudobulk-per-replicate is required for calibrated inference.

E-distance is the modern effect-size. Energy distance in PCA space, `E = 2*sigma_between - sigma_within_X - sigma_within_Y`, measures separation magnitude (not direction or mechanism), with a permutation E-test. It is interpretable only relative to a fixed embedding and is not comparable across studies with different pipelines.

Separate the compositional shift from the within-state change. A perturbation can (a) shift the proportions of pre-existing cell states (differential abundance) without changing any state's program, or (b) change expression within a state (differential expression). A perturbation that only redistributes cells produces a large pseudobulk "DE signature" that is entirely a composition artifact. These need different tools and answer different questions; report both.

## Guide Assignment: Mixture vs Threshold

| Method | Model | Use when | Fails when |
|---|---|---|---|
| Mixture (posterior) | Per-guide 2-component mixture (background Poisson + foreground Gaussian); `pt.pp.GuideAssignment.assign_mixture_model` | Default; ambient varies by guide abundance; low and high MOI | Very few cells per guide (mixture unstable); verify against NT contamination floor |
| Threshold | Flat UMI cutoff; `assign_by_threshold` | Quick sanity check, uniform high-signal libraries | Ambient scales with abundant guides -> mis-assigns to common guides, calls rare-guide cells negative |

Cell Ranger and Replogle's `guide_calling` fit mixtures on log counts; require a minimum dominant-guide UMI fraction, not just an absolute count, and gate doublets (they masquerade as combinatorial cells).

## Method Decision Table (Testing and Effect Size)

| Method | What it answers | Use when | Fails when |
|---|---|---|---|
| Mixscape (pertpy/Seurat) | Which cells were effectively perturbed; per-perturbation DE after removing escapers | CRISPR-KO with heterogeneous editing; need escaper removal | All-NP confounded with low guide efficiency; KO posteriors not comparable across targets |
| SCEPTRE | Calibrated perturbation-gene association | Rigorous testing under the depth confounder; element-level screens | Needs the assignment model roughly right; conservative by design |
| scMAGeCK (LR / RRA) | Per-gene effect across many genes; high-MOI deconvolution | Multi-guide cells; ridge-regression effect estimates | NEGCTRL choice defines the null; runs on scale.data so covariates propagate |
| E-distance + E-test (pertpy) | Effect-size magnitude; perturbation similarity | Ranking/clustering perturbations by how far they move cells | Embedding-dependent, not cross-study comparable; floored by permutation count |
| Pseudobulk DE (DESeq2/edgeR) | Average within-state program change | >=2-3 biological replicates per condition | One replicate per guide -> no valid inference; sum raw counts, not means |
| Milo / scCODA / Augur | Differential abundance / composition | "Does the perturbation move cells across states?" | Conflated with within-state DE if reported alone |

Verify the current best-practice default and parameter names against the installed pertpy/sceptre docs before committing; the APIs drift across releases.

## Foundation-Model Reality Check

This is settled as of 2026, not hype. scGPT, Geneformer, scFoundation, scBERT, UCE are pretrained with masked-expression objectives and learn the co-expression manifold of observational data; perturbation prediction is a causal/interventional question, and there is no theorem that co-expression transfers to intervention. The empirical result across benchmarks: none reliably beat trivial baselines on unseen perturbations (Ahlmann-Eltze 2025; Kernfeld 2025; Csendes 2025).
- For unseen single perturbations, predicting the mean perturbed profile across training perturbations is hard to beat; for unseen doubles, an additive model (sum the two single effects) captures most variance because genetic interactions are the exception.
- All-gene MSE/correlation is dominated by unchanged genes, so a "predict no change"/mean model scores deceptively high. Evaluate on DE genes against mean/additive baselines.
- Train-test leakage inflates reported success: random cell-level splits put the same perturbation in train and test. True generalization holds out entire perturbations (and ideally cell-type contexts), not random cells.

The defensible reviewer stance: demand whole-perturbation holdout, DE-gene metrics, and an explicit additive/mean baseline. Without these, a positive result is not credible.

## Guide Assignment (pertpy)

**Goal:** Call which guide each cell actually received using a mixture posterior, not a flat threshold.

**Approach:** Fit a per-guide Poisson-Gaussian mixture to the guide-count modality and assign by posterior, allowing negative and multi-guide calls.

```python
import pertpy as pt
import scanpy as sc

gdo = mdata.mod['gdo']                       # guide-count modality (cells x guides)
gdo.layers['counts'] = gdo.X.copy()

ga = pt.pp.GuideAssignment()
ga.assign_mixture_model(gdo, assigned_guides_key='assigned_guide')   # background Poisson + foreground Gaussian
# Inspect NT/abundant-guide UMI distributions as a contamination floor before trusting calls
ga.plot_heatmap(gdo, layer='counts')
```

## Mixscape: Remove Non-Perturbed Escapers (pertpy)

**Goal:** Separate effectively-perturbed (KO) from non-perturbed (NP) cells before any DE.

**Approach:** Build a local perturbation signature by subtracting each cell's NT neighbors, then fit a per-target 2-component mixture to classify cells; drop NP cells.

```python
ms = pt.tl.Mixscape()
ms.perturbation_signature(adata, pert_key='perturbation', control='NT', n_neighbors=20)   # pert_key here = the broad perturbed-vs-control column
ms.mixscape(adata, pert_key='target_gene', control='NT', layer='X_pert')   # pert_key here = the per-target column (intentionally different); renamed from labels; writes adata.obs['mixscape_class_global'] KO/NP/NT
# An all-NP target is confounded with low guide efficiency: report perturbed fraction, do not call the gene non-functional
adata.obs['mixscape_class_global'].value_counts()
```

## E-distance and the E-test (pertpy)

**Goal:** Quantify how far each perturbation moves cells and test it against a permutation null.

**Approach:** Compute energy distance in a fixed PCA embedding; pin the embedding and metric, and run the permutation E-test against the control.

```python
sc.pp.pca(adata, n_comps=50)
dist = pt.tl.Distance(metric='edistance', obsm_key='X_pca')   # pin obsm; sqeuclidean vs euclidean default changed across versions
pairwise = dist.pairwise(adata, groupby='target_gene')

etest = pt.tl.DistanceTest('edistance', n_perms=1000)         # smallest p ~ 1/(n_perms+1); crushed by multiple testing
results = etest(adata, groupby='target_gene', contrast='NT')
```

## SCEPTRE: Calibrated Testing (R)

**Goal:** Test perturbation-gene associations with calibration verified on the data itself.

**Approach:** Import counts and guide matrices, set parameters, assign guides by mixture, then run the calibration check (negative controls) before the discovery analysis.

```r
library(sceptre)

obj <- import_data(response_matrix = rna_counts, grna_matrix = grna_counts,
                   grna_target_data_frame = grna_targets, moi = 'low')
obj <- set_analysis_parameters(obj, discovery_pairs = pairs)
obj <- assign_grnas(obj, method = 'mixture')        # mixture | thresholding | maximum
obj <- run_qc(obj)
obj <- run_calibration_check(obj)                   # negative-control pairs must be well-calibrated FIRST
obj <- run_discovery_analysis(obj)
results <- get_result(obj, analysis = 'discovery_analysis')
```

## Pseudobulk DE (Within-State Change)

**Goal:** Test the average program change per perturbation with valid biological replication.

**Approach:** Sum RAW counts per (target gene, replicate), filter tiny pseudobulk samples, then run DESeq2/edgeR; this respects the replication unit and avoids pseudoreplication.

```python
import pertpy as pt

adata.layers['counts'] = adata.layers.get('counts', adata.X.copy())   # stash RAW counts before any log1p
pb = pt.tl.PseudobulkSpace()
pdata = pb.compute(adata, target_col='target_gene', groups_col='replicate', layer_key='counts', mode='sum')   # sum RAW counts, not .X (log-normalized)
# Drop pseudobulk samples below ~10 cells (verify the per-sample cell-count obs column name with help(pb.compute))
# Hand pdata to pertpy EdgeR / pydeseq2 with design ~ replicate + target_gene; needs >=2-3 replicates per condition
```

One transfection per guide means no valid biological-replicate inference exists; using guides targeting the same gene as pseudo-replicates partially helps but conflates guide-specific off-targets.

## Compositional vs Expression (Separate the Questions)

**Goal:** Decide whether a perturbation moves cells across states or changes a state's program.

**Approach:** Run a differential-abundance test (Milo neighborhoods or scCODA) for composition, and report it alongside the within-state pseudobulk DE.

```python
milo = pt.tl.Milo()
mdata_milo = milo.load(adata)
milo.make_nhoods(mdata_milo['rna'])
milo.count_nhoods(mdata_milo, sample_col='replicate')
milo.da_nhoods(mdata_milo, design='~ target_gene')   # differential abundance: does the perturbation shift proportions?
```

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| Rare-guide cells called negative | Flat UMI threshold; ambient biased to abundant guides | Mixture-model assignment by posterior; require a dominant-guide UMI fraction |
| Effect sizes weaker than expected | Escapers/incomplete KO dilute the perturbed population | Run Mixscape, remove NP cells, report perturbed fraction |
| "Gene is non-functional" from all-NP | All-NP confounds no-phenotype with no-editing | Do not claim non-functional; check guide efficiency independently |
| Hundreds of "significant" hits | Naive Wilcoxon/NB miscalibrated by depth + pseudoreplication | SCEPTRE conditional resampling; pseudobulk-per-replicate DE |
| Huge DE signature but no program change | Perturbation only redistributes cells across states | Run Milo/scCODA; attribute the signal to composition |
| E-distances disagree with another paper | Embedding/metric/PC count differ; default metric changed | Pin pertpy version, obsm key, and cell_wise_metric; do not cross-compare |
| Combinatorial cells everywhere | Doublets masquerade as multi-guide | Gate doublets (Scrublet/scDblFinder) before multi-guide analysis |
| Foundation model "beats" baselines | Cell-level split leakage; all-gene metric hides failure | Hold out whole perturbations; score DE genes vs additive/mean baseline |

## Related Skills

- single-cell/preprocessing - scRNA-seq QC and normalization upstream of the screen
- single-cell/doublet-detection - gating doublets before multi-guide analysis
- single-cell/markers-annotation - interpreting per-perturbation DE genes
- single-cell/differential-abundance - compositional shift testing (Milo/scCODA) for perturbations that change cell-state proportions
- single-cell/batch-integration - multi-sample/replicate integration
- crispr-screens/mageck-analysis - bulk CRISPR screen analysis (MAGeCK RRA/MLE)
- crispr-screens/perturb-seq-analysis - related single-cell CRISPR screen workflow
- differential-expression/deseq2-basics - pseudobulk DESeq2 testing on summed counts
- pathway-analysis/go-enrichment - pathway interpretation of perturbation signatures

## References

Dixit A, Parnas O, Li B, et al. Perturb-Seq: dissecting molecular circuits with scalable single-cell RNA profiling of pooled genetic screens. Cell 167(7):1853-1866 (2016).
Datlinger P, Rendeiro AF, Schmidl C, et al. Pooled CRISPR screening with single-cell transcriptome readout (CROP-seq). Nat Methods 14(3):297-301 (2017).
Replogle JM, Norman TM, Xu A, et al. Combinatorial single-cell CRISPR screens by direct guide RNA capture and targeted sequencing. Nat Biotechnol 38(8):954-961 (2020).
Papalexi E, Mimitou EP, Butler AW, et al. Characterizing the molecular regulation of inhibitory immune checkpoints with multimodal single-cell screens (Mixscape). Nat Genet 53(3):322-331 (2021).
Yang L, Zhu Y, Yu H, et al. scMAGeCK links genotypes with multiple phenotypes in single-cell CRISPR screens. Genome Biol 21:19 (2020).
Barry T, Wang X, Morris JA, Roeder K, Katsevich E. SCEPTRE improves calibration and sensitivity in single-cell CRISPR screen analysis. Genome Biol 22:344 (2021).
Squair JW, Gautier M, Kathe C, et al. Confronting false discoveries in single-cell differential expression. Nat Commun 12:5692 (2021).
Peidli S, Green TD, Shen C, et al. scPerturb: harmonized single-cell perturbation data (E-distance). Nat Methods 21(3):531-540 (2024).
Heumos L, Ji Y, May L, et al. Pertpy: an end-to-end framework for perturbation analysis. Nat Methods 23(2):350-359 (2026).
Dann E, Henderson NC, Teichmann SA, Morgan MD, Marioni JC. Differential abundance testing on single-cell data using k-nearest neighbor graphs (Milo). Nat Biotechnol 40(2):245-253 (2022).
Ahlmann-Eltze C, Huber W, Anders S. Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines. Nat Methods 22(8):1657-1661 (2025).
Kernfeld E, Yang Y, Weinstock JS, et al. A comparison of computational methods for expression forecasting. Genome Biol 26:388 (2025).
Csendes G, et al. Benchmarking foundation cell models for post-perturbation RNA-seq prediction. BMC Genomics 26:393 (2025).
<!-- END FILE: single-cell/perturb-seq/SKILL.md -->

## 子目录：single-cell/preprocessing

<!-- BEGIN FILE: single-cell/preprocessing/SKILL.md -->
---
name: bio-single-cell-preprocessing
description: Quality control, ambient-RNA handling, normalization, and feature selection for single-cell RNA-seq using Scanpy (Python) and Seurat (R). Use when filtering low-quality cells with MAD-adaptive thresholds, setting tissue-aware mito cutoffs, removing ambient RNA (SoupX/CellBender/DecontX), choosing a normalization (shifted-log vs scran vs sctransform vs Pearson residuals), selecting highly variable genes, or deciding whether to scale and regress out covariates.
tool_type: mixed
primary_tool: Seurat
---

## Version Compatibility

Reference examples tested with: scanpy 1.10+, Seurat 5.0+, scran 1.30+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Single-Cell Preprocessing

**"Preprocess my scRNA-seq data"** -> Remove bad barcodes, correct technical biases, and select informative genes before dimensionality reduction.
- Python: `calculate_qc_metrics()` -> filter -> `normalize_total()`+`log1p()` -> `highly_variable_genes()`
- R: QC -> `NormalizeData()` or `SCTransform()` -> `FindVariableFeatures()` -> `ScaleData()`

## Governing Principle

Every preprocessing choice propagates to every downstream result, and the two highest-leverage choices both encode a hidden biological assumption.

Normalization assumes near-constant total mRNA per cell. Shifted-log CP10k, scran deconvolution, and sctransform all divide by a per-cell size factor meant to capture only capture-efficiency and sequencing depth. They silently assume total transcriptome size is roughly constant across cell types, so a cell's total UMI count is a pure technical nuisance. This is false for plasma/antibody-secreting cells, secretory epithelia, hepatocytes, large neurons, and S/G2M cells, which carry 2-10x more mRNA. Dividing them to a common total deflates every gene that is not one of their few dominant transcripts (a compositional see-saw), and partially erases real proliferation biology. The honest framing: single-cell measures proportions, not absolute amounts.

QC metrics are biology metrics in disguise. `pct_counts_mt` conflates apoptosis, genuine metabolic activity (cardiomyocytes/hepatocytes/muscle are constitutively 20-40% mito and healthy), dissociation stress, and technical contamination. A flat global mito cutoff deletes entire healthy parenchymal populations and the survivors still cluster cleanly, so the loss is invisible. Use adaptive, tissue-aware thresholds and treat all three QC covariates jointly.

A beautiful UMAP proves nothing. Compositional normalization bias, deleted high-mito parenchyma, dissociation-stress clusters, ambient-induced co-expression, and residual homotypic doublets are all compatible with tidy clusters. The dangerous artifacts are precisely the ones that do not look like artifacts.

## Canonical Pipeline Order

1. Load the RAW (unfiltered) droplet matrix.
2. Empty-droplet calling (EmptyDrops, FDR<=0.001 on raw) or CellBender (folds calling + denoising).
3. Ambient-RNA removal (optional; SoupX/DecontX/CellBender) - BEFORE QC, because it needs the soup estimate.
4. QC filtering: cells (MAD on counts/genes/mito) + genes (`min_cells`).
5. Doublet detection - per sample, on raw counts (see single-cell/doublet-detection).
6. Normalization - shifted-log default, or scran/Pearson.
7. HVG selection - mind the raw-vs-lognorm input per flavor.
8. Scaling (optional, increasingly skipped).
9. PCA on HVG (~50 comps), then neighbors/clustering.

Ambient correction needs the raw matrix and must precede QC filtering; once subset to cells, the soup estimate is gone. Doublet detection runs on raw counts, so stash counts before normalizing.

Steps 1-5 are per-sample operations performed BEFORE merge or integration: empty-droplet calling, ambient removal (SoupX `load10X` is inherently per-run), adaptive QC, and doublet detection all reason about one capture's droplet population, so QC-then-merge is correct and merge-then-QC leaks batch effects into every threshold and contaminates the soup and doublet-scoring neighborhoods. Merge only after each sample is cleaned.

## Quality Control

**Goal:** Remove empty/dying/stressed barcodes using data-driven thresholds that do not delete real cell types.

**Approach:** Annotate mito/ribo/hemoglobin gene sets, compute joint QC metrics, then flag outliers by median absolute deviation (MAD) on the log scale rather than fixed cutoffs.

```python
import scanpy as sc
import numpy as np
from scipy.stats import median_abs_deviation

adata.var['mt'] = adata.var_names.str.startswith('MT-')                       # mouse: 'mt-'
adata.var['ribo'] = adata.var_names.str.startswith(('RPS', 'RPL'))
adata.var['hb'] = adata.var_names.str.contains(r'^HB[ABDEGMQZ]\d*(?!\w)')      # explicit subunits, not legacy ^HB[^(P)]
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt', 'ribo', 'hb'], percent_top=[20], log1p=True, inplace=True)
# inplace defaults to False and returns DataFrames; pass inplace=True to write .obs/.var

def is_outlier(adata, metric, nmads):
    M = adata.obs[metric]
    return (M < np.median(M) - nmads * median_abs_deviation(M)) | (np.median(M) + nmads * median_abs_deviation(M) < M)

adata.obs['outlier'] = (is_outlier(adata, 'log1p_total_counts', 5) | is_outlier(adata, 'log1p_n_genes_by_counts', 5)
                        | is_outlier(adata, 'pct_counts_in_top_20_genes', 5))
adata.obs['mt_outlier'] = is_outlier(adata, 'pct_counts_mt', 3) | (adata.obs['pct_counts_mt'] > 8)
adata = adata[~(adata.obs['outlier'] | adata.obs['mt_outlier'])].copy()
sc.pp.filter_genes(adata, min_cells=3)
```

When samples differ in depth/quality or were sequenced in separate batches, compute MAD thresholds PER SAMPLE, not globally: a single global MAD over-cuts the shallow batch and under-cuts the deep one. Apply `is_outlier` within each `batch_key` group (the same per-batch logic the HVG step uses).

```python
flags = ['log1p_total_counts', 'log1p_n_genes_by_counts', 'pct_counts_in_top_20_genes']
adata.obs['outlier'] = adata.obs.groupby('sample', observed=True).apply(
    lambda g: (is_outlier(adata[g.index], flags[0], 5) | is_outlier(adata[g.index], flags[1], 5)
               | is_outlier(adata[g.index], flags[2], 5))).droplevel(0)
```

```r
# '^MT-' matches gene SYMBOLS; with Ensembl-ID feature names it matches nothing and the mito filter silently does nothing
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')
VlnPlot(seurat_obj, features = c('nFeature_RNA', 'nCount_RNA', 'percent.mt'), ncol = 3)
seurat_obj <- subset(seurat_obj, subset = nFeature_RNA > 200 & nFeature_RNA < 5000 & percent.mt < 20)
```

### QC Thresholds and Rationale

| Metric | Reference value | Rationale and caveat |
|--------|-----------------|----------------------|
| `min_genes` | 200 | Below this is mostly empty droplets / debris; raise for deep data |
| `log1p_total_counts` / `log1p_n_genes_by_counts` | 5 MAD | sc-best-practices loosens from scater's 3 MAD to avoid cutting real biology; filter on the log scale (depth is right-skewed) |
| `pct_counts_in_top_20_genes` | 5 MAD | High value flags low-complexity / dying cells |
| `pct_counts_mt` | 3 MAD plus hard >8% | Tissue-dependent: 5-20% typical, but cardiomyocytes/hepatocytes/muscle are constitutively high; nuclei are ~0-2% and any mito flags ambient |
| `min_cells` (genes) | 3 | Remove genes seen in too few cells to be informative |

Fixed cutoffs are a fast first pass for well-characterized tissue but silently delete valid populations; MAD-adaptive is the modern default; miQC (a mito-vs-detected-genes mixture model) helps when that relationship varies across samples.

### Mito and Dissociation Confounds

High mito is ambiguous: apoptosis co-occurs with low gene counts and apoptotic markers, while warm-dissociation stress co-occurs with immediate-early genes (FOS, JUN, JUNB, EGR1) and heat-shock proteins (HSPA1A/B) at normal gene counts. The IEG/HSP program creates a spurious "activated/stressed" cluster that passes every count/mito filter, is cell-type-specific in magnitude (so it does not cancel as a uniform batch effect), and overlaps real immune/stem activation, so naive removal can itself delete biology. Score the dissociation module per cell, then exclude those genes from HVG/clustering or flag and interpret cautiously; cold-protease digestion and single-nucleus assays reduce the artifact. For nuclei, standard mito thresholds are meaningless (baseline near zero) - lean on counts/genes outliers.

## Ambient RNA Removal

**Goal:** Remove cell-free "soup" mRNA that inflates off-target markers (hemoglobin everywhere in PBMCs, hepatocyte genes in non-hepatocytes) and fabricates co-expression.

**Approach:** Estimate the soup profile and a per-cell contamination fraction, then subtract; pick ONE tool and validate that a known-specific marker survives.

| Tool | Input | Needs empty droplets? | Strength | Fails / risk |
|------|-------|-----------------------|----------|--------------|
| SoupX (R) | Cell Ranger raw+filtered | Yes | Fast, interpretable rho, auto-estimate | `autoEstCont` fails on homogeneous data; single global soup wrong when ambient is heterogeneous |
| CellBender (Python, GPU) | RAW h5 | Yes (core of model) | Deep generative; removes ambient + barcode noise; also does cell-calling; strong on nuclei | Over-removes real low-abundance genes at high `--fpr`; black-box; slow |
| DecontX (R, celda) | Filtered cells | No | No raw needed; easy SCE/Seurat integration | Relies on cluster purity |

```r
library(SoupX)
sc <- load10X('cellranger_outs/')          # needs BOTH raw and filtered
sc <- autoEstCont(sc)                       # estimates contamination fraction rho
counts_adj <- adjustCounts(sc, roundToInt = TRUE)   # output is non-integer by default; round for NB models
```

SoupX and CellBender disagree on what "ambient" is: SoupX subtracts a per-cell scalar of a single global soup profile; CellBender learns a probabilistic per-droplet background in a generative model. There is no consensus on which is better - CellBender is more powerful and more dangerous. Subtracting a shared soup vector from every cell can manufacture artificial negative correlations and zero out genes cells genuinely lacked, so validate. Matters most for solid tumors, snRNA-seq, and blood. Do not stack tools; double-correction compounds over-removal.

## Normalization

**Goal:** Remove per-cell depth bias and stabilize variance so high-expression genes do not dominate PCA/kNN distances.

**Approach:** Default to shifted-log; reach for scran on shallow data and Pearson residuals on UMI count models; never normalize already-normalized data.

```python
adata.layers['counts'] = adata.X.copy()                  # stash raw before normalizing (HVG/doublets need it)
sc.pp.normalize_total(adata)                             # target_sum=None scales each cell to the dataset MEDIAN; pass target_sum=1e4 for the historical, arbitrary CP10k
sc.pp.log1p(adata)                                       # natural-log(1+x); the variance-stabilizing transform (no target_sum argument)
```

```r
seurat_obj <- NormalizeData(seurat_obj, normalization.method = 'LogNormalize', scale.factor = 10000)
# or variance-stabilized: seurat_obj <- SCTransform(seurat_obj, verbose = FALSE)
```

| Method | Model / assumption | Use when | Fails when |
|--------|--------------------|----------|------------|
| Shifted-log (CP10k / median) | Size-factor + log1p; constant total mRNA | General default; strong, fast, defensible | Composition-divergent types (plasma, cycling) distort fold-changes |
| scran deconvolution | Pooled size factors robust to composition | Low-depth, high-dropout, plate-based | R-only; needs pre-clustering (`quickCluster`); factors can go negative |
| sctransform v1/v2 | NB regularized regression (Pearson residuals) | Seurat depth removal for HVG/viz | Slow; off the count scale; v1 overfits theta (use v2) |
| Analytic Pearson residuals | `r=(x-mu)/sqrt(mu+mu^2/theta)` | UMI HVG+PCA without ad-hoc steps | Experimental; residual variance depends on theta and depth; clip to +/-sqrt(n) |

Ahlmann-Eltze and Huber 2023 found plain shifted-log + PCA performs as well as or better than sctransform, Pearson residuals, and GLM-PCA on kNN-overlap recovery, so shifted-log is the defensible default and the sophisticated methods are "use if preferred," not mandated. Because methods genuinely compete here, verify current best practice against the installed tool's docs before committing. Normalize raw counts exactly once and keep the transform consistent across HVG, scaling, and PCA.

## Highly Variable Genes

**Goal:** Restrict PCA/clustering to genes carrying biological signal.

**Approach:** Select a flavor, then feed it the input type it expects - the single most consequential gotcha is that dispersion flavors want log-normalized data while `seurat_v3` and Pearson want RAW COUNTS.

```python
# seurat_v3 reads raw counts from a layer and REQUIRES n_top_genes; needs the scikit-misc package
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor='seurat_v3', layer='counts')
```

| Flavor | Function | Input | n_top_genes required? | Extra dependency |
|--------|----------|-------|-----------------------|------------------|
| `seurat` (default) | `sc.pp.highly_variable_genes` | log-normalized | No | - |
| `cell_ranger` | `sc.pp.highly_variable_genes` | log-normalized | No | - |
| `seurat_v3` | `sc.pp.highly_variable_genes` | RAW counts | Yes | scikit-misc |
| `pearson_residuals` | `sc.experimental.pp.highly_variable_genes` | RAW counts | recommended | - |

Running `seurat_v3` on logged values, or `seurat` on raw counts, runs silently and yields garbage HVGs. The field is shifting toward binomial-deviance and Pearson-residual feature selection on raw counts because dispersion HVGs are sensitive to the upstream normalization choice. Set `batch_key` to compute HVGs per batch and avoid batch-specific technical genes.

## Scaling and Regressing Out

**Goal:** Optionally equalize gene weight in PCA, and remove unwanted covariates - both now discouraged as reflexive defaults.

**Approach:** Prefer PCA on log-normalized HVG without scaling; regress out only a validated, non-confounded covariate.

```python
sc.pp.scale(adata, max_value=10)        # max_value default is None (no clipping); 10 is an explicit choice to cap z-scores
# sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])   # scanpy itself warns this overcorrects
```

"Always regress out mito and total_counts" is folklore: those covariates are confounded with real cell identity and state (cycling cells legitimately have more RNA), so regressing them erases biology and can collapse data into a blob. Modern normalization already stabilizes depth; address unwanted variation with integration (Harmony, scVI) rather than linear regression. Scaling inflates lowly-expressed noisy genes; sc-best-practices runs PCA on the normalized layer directly.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| HVGs look random; clustering is mush | `seurat_v3` fed log-normalized (or `seurat` fed raw) | Feed each flavor its required input; use `layer='counts'` for `seurat_v3` |
| An entire healthy cell type disappeared | Flat mito cutoff deleted high-mito parenchyma | Use MAD/tissue-aware thresholds; inspect what was removed |
| Values inflated ~2x after re-running normalization | Normalized already-normalized data | Normalize raw once; restore from `layers['counts']` |
| `ModuleNotFoundError: skmisc` | `seurat_v3` needs scikit-misc | `pip install scikit-misc` |
| QC metrics missing from `.obs` | `calculate_qc_metrics` `inplace` defaults to False | Pass `inplace=True` |
| Proliferation / activation signal vanished | Regressed out `total_counts` / cell-cycle confounded with biology | Do not reflexively regress; validate the covariate is not confounded |
| New "stressed/transitional" cluster | Warm-dissociation IEG/HSP artifact | Score the dissociation module; exclude those genes from HVG/clustering |
| Off-target markers everywhere (Hb, Ig) | Ambient RNA contamination | Run SoupX/CellBender/DecontX on the raw matrix before QC |
| Spike to ~2x counts deflated other genes | Compositional see-saw from a few dominant genes | Use `exclude_highly_expressed=True` or scran; report relative, not absolute, expression |
| Almost all cells filtered / tiny survivor count | MAD ~ 0 on a low-variance, tiny, or nuclei sample (>50% share a value), so `is_outlier` flags every non-median cell | Assert `n_obs > 0` and a sane survival fraction; fall back to fixed cutoffs when MAD is ~0 |
| Mito filter removes nothing (percent.mt all 0) | `'^MT-'` pattern matched against Ensembl-ID feature names | Use gene symbols, or match the mito Ensembl IDs / a mito gene list |
| Shallow batch over-filtered, deep batch under-filtered | Global MAD thresholds across samples of differing depth | Compute `is_outlier` per `batch_key`/sample group |
| Batch effects baked into QC/soup/doublet calls | Merged samples before QC, ambient, and doublet steps | Run steps 1-5 per sample, then merge |

## Related Skills

- single-cell/data-io - load the raw matrix before preprocessing
- single-cell/doublet-detection - per-sample doublet calling around the QC step
- single-cell/clustering - PCA, neighbors, and clustering after preprocessing
- single-cell/batch-integration - correct batch effects instead of regressing them out
- single-cell/markers-annotation - find markers after clustering
- differential-expression/deseq2-basics - pseudobulk DE across samples (avoids single-cell pseudo-replication)

## References

- Heumos L, Schaar AC, Lance C, et al. (2023) Best practices for single-cell analysis across modalities. Nature Reviews Genetics 24:550-572. DOI 10.1038/s41576-023-00586-w
- Ahlmann-Eltze C, Huber W (2023) Comparison of transformations for single-cell RNA-seq data. Nature Methods 20:665-672. DOI 10.1038/s41592-023-01814-1
- Lun ATL, Bach K, Marioni JC (2016) Pooling across cells to normalize single-cell RNA sequencing data (scran). Genome Biology 17:75. DOI 10.1186/s13059-016-0947-7
- Hafemeister C, Satija R (2019) Normalization and variance stabilization of single-cell RNA-seq data using regularized negative binomial regression (sctransform). Genome Biology 20:296. DOI 10.1186/s13059-019-1874-1
- Choudhary S, Satija R (2022) Comparison and evaluation of statistical error models for scRNA-seq (sctransform v2). Genome Biology 23:27. DOI 10.1186/s13059-021-02584-9
- Lause J, Berens P, Kobak D (2021) Analytic Pearson residuals for normalization of single-cell RNA-seq UMI data. Genome Biology 22:258. DOI 10.1186/s13059-021-02451-7
- Vallejos CA, Risso D, Scialdone A, Dudoit S, Marioni JC (2017) Normalizing single-cell RNA sequencing data: challenges and opportunities. Nature Methods 14(6):565-571. DOI 10.1038/nmeth.4292
- Osorio D, Cai JJ (2021) Systematic determination of the mitochondrial proportion in human and mouse tissues for scRNA-seq quality control. Bioinformatics 37(7):963-967. DOI 10.1093/bioinformatics/btaa751
- Hippen AA, Falco MM, Weber LM, et al. (2021) miQC: An adaptive probabilistic framework for quality control of single-cell RNA-seq data. PLoS Computational Biology 17(8):e1009290. DOI 10.1371/journal.pcbi.1009290
- Young MD, Behjati S (2020) SoupX removes ambient RNA contamination from droplet-based single-cell RNA sequencing data. GigaScience 9(12):giaa151. DOI 10.1093/gigascience/giaa151
- Fleming SJ, Chaffin MD, Arduini A, et al. (2023) Unsupervised removal of systematic background noise (CellBender remove-background). Nature Methods 20:1323-1335. DOI 10.1038/s41592-023-01943-7
- van den Brink SC, Sage F, Vertesy A, et al. (2017) Single-cell sequencing reveals dissociation-induced gene expression in tissue subpopulations. Nature Methods 14(10):935-936. DOI 10.1038/nmeth.4437
- Squair JW, Gautier M, Kathe C, et al. (2021) Confronting false discoveries in single-cell differential expression. Nature Communications 12:5692. DOI 10.1038/s41467-021-25960-2
<!-- END FILE: single-cell/preprocessing/SKILL.md -->

## 子目录：single-cell/scatac-analysis

<!-- BEGIN FILE: single-cell/scatac-analysis/SKILL.md -->
---
name: bio-single-cell-scatac-analysis
description: Analyze single-cell ATAC-seq with Signac/ArchR (R) and SnapATAC2 (Python alternative). Use when processing scATAC fragments, choosing a framework, calling consensus peaks, running TF-IDF/LSI while diagnosing the depth component, scoring chromVAR motif deviations against GC-matched backgrounds, detecting homotypic vs heterotypic doublets, or deciding whether to binarize the count matrix.
tool_type: r
primary_tool: Signac
---

## Version Compatibility

Reference examples tested with: Signac 1.13+, Seurat 5.0+, ArchR 1.0+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python (SnapATAC2 alternative): `pip show snapatac2` then `help(module.function)`

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# scATAC-seq Analysis

**"Analyze my single-cell ATAC-seq data"** -> Process fragments, QC on chromatin signal, reduce dimensions with TF-IDF/LSI, cluster, call consensus peaks per cell type, and score TF motif activity.
- R: `Signac::CreateChromatinAssay()` -> `RunTFIDF()` -> `FindTopFeatures()` -> `RunSVD()` -> `RunChromVAR()`
- R (large data, on-disk): `ArchR::createArrowFiles()` -> `addIterativeLSI()` -> `addReproduciblePeakSet()`
- Python (scverse, >1M cells): `snapatac2.pp.add_tile_matrix()` -> `tl.spectral()` -> `tl.macs3()`

## Governing Principle

A zero in the cell-by-peak matrix is epistemically ambiguous: it can mean "closed in this cell" (biology) or "accessible but no Tn5 fragment captured here" (sampling). With ~2 DNA copies per diploid locus and shallow per-cell coverage, sampling dominates the zeros. The matrix is near-binary by sampling statistics, not by biology; underlying accessibility is continuous but observed as a Bernoulli-like draw.

Binarization is now disfavored. Among non-zero entries the count (1 vs 2 vs >2) is informative, and collapsing to 1 discards it (Martens 2024). Model fragment counts with a count likelihood (Paired-Insertion Counting, SnapATAC2; PoissonVI), never read counts (PCR noise). Caveat: the extra information lives in the count=2 tier, so the benefit scales with sequencing depth; binarized analyses of shallow data are leaving little on the table, deep data more.

Per-cell signal is near-binary by sampling, so single-cell single-gene quantitative claims are unreliable; aggregate to cluster/pseudobulk for graded signal.

Gene-activity scores are a weak cluster-level proxy, structurally not just empirically: (1) enhancer-to-promoter assignment is unknown, and any fixed-distance heuristic (Signac gene body + 2 kb, ArchR exponential decay to 100 kb) is wrong for genes whose enhancers sit outside the window or loop differently by cell type; (2) poised/bivalent promoters are accessible while the gene is silent, so accessibility-to-expression is not monotone. Use gene activity for cluster-level annotation and scRNA-integration anchoring only, never as a single-cell transcriptome surrogate.

The peak set depends on which cells called the peaks: peaks are called on cells already grouped, but the grouping used a feature matrix that depends on a peak/tile choice. This is a circularity. Rare populations unresolved in the first pass never get their peaks called, so their defining elements stay invisible, a self-reinforcing blind spot. This is why iterative per-cluster peak calling (ArchR iterative LSI) exists, and why testing differential accessibility on a peak set called from the same clustering is double-dipping.

## Framework Decision Table

Framework choice is an infrastructure decision (language, memory, multimodal needs), not a statistics decision. Scalability numbers describe each tool's most-optimized path, not every operation.

| Framework | Language / storage | Use when | Fails when |
|---|---|---|---|
| Signac | R, in-memory Seurat ChromatinAssay | Seurat-integrated multimodal (WNN), familiar Seurat API | ~10^5+ cells (RAM-bound; `future` workers copy the object) |
| ArchR | R, on-disk HDF5 Arrow files | Large R workflows (~1M cells), built-in iterative LSI/peak/GRN suite | Networked filesystems (HDF5 file-locking); not a portable matrix |
| SnapATAC2 | Python+Rust, AnnData backed | >1M cells (matrix-free spectral), scverse/scvi-tools stack | Less turnkey footprinting/GRN; faster-moving 2.x API |
| muon + scanpy | Python, MuData | Multimodal Python container (RNA+ATAC) | Not ATAC-optimized for the heaviest steps |

R<->Python interop (reticulate, zellkonverter, sceasy) loses information (ChromatinAssay slots, ArchR HDF5 do not round-trip); plan to stay in one ecosystem. Verify the current best-practice default against installed docs before committing.

## Matrix Type: Tile vs Peak vs Gene Activity

| Matrix | What it is | Use when | Caveat |
|---|---|---|---|
| Tile/bin (500 bp) | Genome binned, no prior peaks | Initial LSI/clustering before peaks exist | Not biology-aware; 500 bp tiles vs 501 bp peaks (off-by-one feature bugs) |
| Peak (consensus) | Per-cluster MACS peaks merged to fixed width | Final accessibility quantification, DA testing | Requires peaks first; circular with clustering |
| Gene activity | Accessibility folded to per-gene scalar | Cluster annotation, scRNA-integration anchors | Weak proxy; repressed/bivalent genes fail; distal enhancers misassigned |

## TF-IDF + LSI: Diagnose the Depth Component

**Goal:** Reduce the sparse, near-binary, depth-confounded matrix without letting technical depth dominate.

**Approach:** Reweight peaks with TF-IDF, reduce with truncated SVD, then drop components that correlate with depth, diagnosed by `DepthCor`, not blindly dropping component 1.

```r
obj <- RunTFIDF(obj)                       # method 1 (default) = log(TF x IDF), Stuart & Butler
obj <- FindTopFeatures(obj, min.cutoff = 'q0')
obj <- RunSVD(obj)                         # writes the 'lsi' reduction

DepthCor(obj, n = 10)                      # per-component Pearson correlation with nCount
# LSI_1 usually has |corr| > 0.95 with depth, but verify; occasionally it is component 2/3, or none
```

Component 1 captures depth ~90% of the time but the rule is symptom-based: compute each component's depth correlation (`DepthCor`, or ArchR `corCutOff = 0.75`) and drop whichever exceed the threshold. ArchR `addIterativeLSI()` recomputes LSI on variable features across clustering passes to reduce depth/batch artifacts. A reviewer flags blind `dims = 2:30` with no depth-correlation diagnostic.

## Clustering on LSI

**Goal:** Cluster cells from the depth-cleaned LSI embedding.

**Approach:** Build the neighbor graph and UMAP on the retained LSI dimensions, then cluster.

```r
dims_use <- 2:30                            # set from DepthCor, not assumed
obj <- RunUMAP(obj, reduction = 'lsi', dims = dims_use)
obj <- FindNeighbors(obj, reduction = 'lsi', dims = dims_use)
obj <- FindClusters(obj, algorithm = 3, resolution = 0.5)   # algorithm 3 = SLM
```

## Consensus Peak Calling

**Goal:** Call peaks per cell type and merge into a non-overlapping, reusable feature set, avoiding bias toward abundant cell types.

**Approach:** Pooled bulk calling misses rare-population elements; call per cluster on pseudobulk, then merge. ArchR's fixed-width iterative-overlap set is the most reproducible; Signac's `CallPeaks` is simpler but uses a variable-width union that drops significance metadata.

```r
peaks <- CallPeaks(obj, group.by = 'seurat_clusters')       # per-group MACS, then GRanges::reduce() union
peak_counts <- FeatureMatrix(fragments = Fragments(obj), features = peaks, cells = colnames(obj))
obj[['peaks']] <- CreateChromatinAssay(counts = peak_counts, fragments = Fragments(obj), annotation = Annotation(obj))
```

Fixed-width peaks (ArchR's 501 bp) remove per-peak length normalization and give a stable reusable feature space. ArchR ranks fixed-width candidates by significance, keeps the best, removes overlappers, and requires a peak in >=2 pseudobulk replicates (reproducibility, orthogonal to MACS q-value). Wrapper parameters differ (ArchR shift -75/extsize 150 with `--nolambda`; Signac/SnapATAC2 shift -100/extsize 200), which changes which weak peaks survive. Comparing peak sets across datasets requires re-quantifying against a unified set; peak boundaries are not portable.

## Differential Accessibility

**Goal:** Find peaks more accessible in one group, controlling for the depth confounder.

**Approach:** Use a logistic-regression test with total fragments as a latent variable; do not test on a peak set called from the same clustering being compared (double-dipping).

```r
DefaultAssay(obj) <- 'peaks'
da <- FindMarkers(obj, ident.1 = 'cluster1', ident.2 = 'cluster2',
                  test.use = 'LR', latent.vars = 'nCount_peaks')
```

## chromVAR Motif Deviations

**Goal:** Find which TF motifs vary in accessibility across cells, corrected for GC content and depth.

**Approach:** Attach motif matches, then compute deviations against a GC- and accessibility-matched background; rank with z-scores, never raw deviations.

```r
library(JASPAR2020); library(TFBSTools); library(motifmatchr)
library(BSgenome.Hsapiens.UCSC.hg38)

pfm <- getMatrixSet(JASPAR2020, opts = list(collection = 'CORE', tax_group = 'vertebrates', all_versions = FALSE))
obj <- AddMotifs(obj, genome = BSgenome.Hsapiens.UCSC.hg38, pfm = pfm)
obj <- RunChromVAR(obj, genome = BSgenome.Hsapiens.UCSC.hg38)   # GC-matched background internally

DefaultAssay(obj) <- 'chromvar'
diff_motifs <- FindMarkers(obj, ident.1 = 'cluster1', ident.2 = 'cluster2',
                           mean.fxn = rowMeans, fc.name = 'avg_diff')
```

chromVAR's deviation is meaningful only against a GC- and accessibility-matched background; an unmatched background manufactures apparent enrichment for GC-rich motifs (most TF motifs are GC-rich). Use z-scores (background-normalized) for cross-motif ranking, raw deviations are not comparable across motifs. Motif != TF: paralogous TFs share near-identical motifs, so an enriched motif implicates a family, not a factor; motif presence != occupancy; and a footprint (TOBIAS, needs pseudobulk) is stronger occupancy evidence than motif-in-peak. Disambiguate with TF expression (Multiome) before claiming "TF X drives this program".

## Gene Activity (Cluster-Level Only)

**Goal:** Approximate per-gene accessibility for marker-based annotation and scRNA anchoring.

**Approach:** Sum fragments over the gene body plus a promoter window; treat the output as a cluster-level aid, not measured RNA.

```r
gene_act <- GeneActivity(obj)              # gene body + 2 kb upstream, flat count, no distance weighting
obj[['ACT']] <- CreateAssayObject(counts = gene_act)
obj <- NormalizeData(obj, assay = 'ACT', scale.factor = median(obj$nCount_ACT))
```

## Doublet Detection: Homotypic vs Heterotypic

Two strategies catch different doublet classes; run both and combine. Doublet callers are separate from QC metrics (TSS/nucleosome gate debris, not doublets).

| Tool | Principle | Catches | Key dependency |
|---|---|---|---|
| AMULET | >2 fragments overlapping a diploid locus -> Poisson + BH | Homotypic (same-type) | ~25k read pairs/cell for full recall |
| ArchR `addDoubletScores` | Simulate doublets -> LSI/UMAP -> kNN; use `DoubletEnrichment` | Heterotypic (different-type) | LSI/UMAP quality; structurally blind to homotypic |
| scDblFinder ATAC | Simulate on `nfeatures=25` aggregated meta-features | Heterotypic | Embedding quality |

AMULET silently under-calls below ~25k coverage; CNV/aneuploidy breaks its diploid null (amplified loci exceed 2 copies in true singlet cancer cells -> false positives); multinucleate/S-G2-M cells violate the <=2-copies assumption. ArchR prefers `DoubletEnrichment` over `DoubletScore`. scDblFinder uses `nfeatures=25` (not 1000) and its authors recommend against `clamulet`.

## QC Thresholds

| Metric | Signac column | Threshold | Basis |
|---|---|---|---|
| TSS enrichment | `TSS.enrichment` | >2-3 (Signac); >4 (ArchR human) | ENCODE signal/noise; threshold is annotation-dependent, not portable |
| Total fragments | `nCount_peaks` / nFrags | >1000 (often >3000) | removes empties/debris |
| Nucleosome signal | `nucleosome_signal` | <4 | banding quality; very low can mean over-transposition |
| FRiP | `FRiP` | >0.15-0.40 (study-dependent) | signal in peaks; depends on peak set and counting convention |

TSS scores are not comparable across pipelines/annotations; never port thresholds. `TSSEnrichment(fast=TRUE)` blocks later `TSSPlot()`. FRiP depends on the peak set (circular if the same cells) and counting convention (Signac counts fragments, CellRanger-ATAC counts insertions). Threshold from the joint distributions of the actual data, not copied defaults.

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| UMAP separates by depth, not biology | Did not drop the depth-correlated LSI component | Run `DepthCor`; drop components above threshold (often #1, verify) |
| Long flat run of zeros read as "closed" | Zeros are sampling-dominated, ambiguous | Interpret at cluster/pseudobulk level; check effective coverage before structural claims |
| Gene activity disagrees with RNA for a marker | Repressed/bivalent promoter is open but silent; distal enhancer outside window | Use gene activity for cluster annotation only; validate with multiome RNA |
| "Everything is GC-rich enriched" in chromVAR | Unmatched background | Use `getBackgroundPeaks`/RunChromVAR GC+accessibility-matched background; report z-scores |
| Rare cell type never appears | Peaks called from a coarse single-pass clustering missed its elements | Iterative per-cluster peak calling + re-clustering (ArchR iterative LSI) |
| DA peaks look inflated | Tested on a peak set called from the same clustering (double-dipping) | Call peaks independently of the comparison; treat as ranking |
| Doublets pass QC | TSS/nucleosome gate debris, not doublets | Run AMULET (homotypic) and ArchR/scDblFinder (heterotypic) and combine |
| AMULET finds few doublets in cancer | CNV breaks the diploid null; or coverage <25k pairs/cell | Use heterotypic callers in aneuploid samples; check per-cell coverage |
| "TF X drives this" from a motif | Motif implicates a family; presence != occupancy | Confirm with TF expression (multiome) and/or footprint (TOBIAS, pseudobulk) |
| QC, gene activity, and motifs all run but look wrong | Peaks, fragments, EnsDb annotation, and BSgenome are on different genome builds; coordinate mismatch is silently wrong (no crash) | Pin every reference to one build (e.g. all hg38); verify TSS enrichment and a known marker before trusting downstream |

## Related Skills

- single-cell/multimodal-integration - joining the ATAC modality with RNA (Multiome WNN/MultiVI)
- single-cell/preprocessing - shared QC and filtering concepts from scRNA-seq
- single-cell/clustering - clustering and UMAP shared with scRNA-seq
- single-cell/doublet-detection - doublet concepts and rate expectations
- atac-seq/atac-peak-calling - bulk ATAC peak-calling background (MACS shift/extend)
- atac-seq/motif-deviation - chromVAR deviation scoring in depth
- chip-seq/motif-analysis - motif databases (JASPAR/cisBP) and enrichment testing

## References

Buenrostro JD, Giresi PG, Zaba LC, et al. Transposition of native chromatin for fast and sensitive epigenomic profiling (ATAC-seq). Nat Methods 10(12):1213-1218 (2013).
Cusanovich DA, Daza R, Adey A, et al. Multiplex single-cell profiling of chromatin accessibility (TF-IDF/LSI). Science 348(6237):910-914 (2015).
Stuart T, Srivastava A, Madad S, Lareau CA, Satija R. Single-cell chromatin state analysis with Signac. Nat Methods 18:1333-1341 (2021).
Granja JM, Corces MR, Pierce SE, et al. ArchR is a scalable software package for integrative single-cell chromatin accessibility analysis. Nat Genet 53:403-411 (2021).
Zhang K, Zemke NR, Armand EJ, Ren B. A fast, scalable and versatile tool for analysis of single-cell omics data (SnapATAC2). Nat Methods 21(2):217-227 (2024).
Schep AN, Wu B, Buenrostro JD, Greenleaf WJ. chromVAR: inferring transcription-factor-associated accessibility from single-cell epigenomic data. Nat Methods 14(10):975-978 (2017).
Martens LD, Fischer DS, Theis FJ, Buettner F. Modeling fragment counts improves single-cell ATAC-seq analysis. Nat Methods 21(1):28-31 (2024).
Miao Z, Kim J. Uniform quantification of single-nucleus ATAC-seq data with Paired-Insertion Counting (PIC) and a model-based insertion rate estimator. Nat Methods 21:32-36 (2024).
Thibodeau A, Eroglu A, McGinnis CS, et al. AMULET: a novel read count-based method for effective multiplet detection from single-nucleus ATAC-seq data. Genome Biol 22:252 (2021).
Germain P-L, Lun A, Garcia Meixide C, Macnair W, Robinson MD. Doublet identification in single-cell sequencing data using scDblFinder. F1000Research 10:979 (2022).
Bentsen M, Goymann P, Schultheis H, et al. ATAC-seq footprinting unravels kinetics of transcription factor binding during zygotic genome activation (TOBIAS). Nat Commun 11:4267 (2020).
<!-- END FILE: single-cell/scatac-analysis/SKILL.md -->

## 子目录：single-cell/trajectory-inference

<!-- BEGIN FILE: single-cell/trajectory-inference/SKILL.md -->
---
name: bio-single-cell-trajectory-inference
description: Infers developmental trajectories, pseudotime, RNA velocity, and directed fate probabilities from single-cell data using PAGA, Slingshot, Monocle3, DPT, Palantir, scVelo, and CellRank 2. Use when ordering cells along a differentiation continuum, choosing a trajectory method by topology, rooting pseudotime, estimating RNA velocity direction, computing fate probabilities near a bifurcation, or judging whether an inferred trajectory is real.
tool_type: mixed
primary_tool: Monocle3
---

## Version Compatibility

Reference examples tested with: scanpy 1.10+, scVelo 0.3+, CellRank 2.0+, Monocle3 1.3+, Slingshot 2.x

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Trajectory Inference

**"Find the developmental trajectory in my data"** -> Order cells along a continuous manifold and assign a pseudotime, fate probabilities, or velocity direction.
- Python: `sc.tl.paga`/`sc.tl.dpt` (scanpy), `palantir`, `scvelo`, `cellrank` (kernels + GPCCA)
- R: `slingshot`, `monocle3`, `tradeSeq`

## Governing Principle

A snapshot is not a movie. Every method substitutes transcriptomic similarity for temporal adjacency: it takes a single static sample and imposes an ordering or a Markov process on the kNN graph. The output is meaningful only when the population is a genuine continuum of asynchronously-progressing cells, sampled densely enough to bridge intermediate states. Five rules follow and they drive every downstream decision.

1. Pseudotime is geometry, not a clock. The axis is monotone in progression at best; equal pseudotime intervals are NOT equal real-time intervals, and rates differ across lineages. Reading an interval as a duration is a category error.
2. The existence of a continuum is a BIOLOGICAL judgment made BEFORE ordering. Any method returns numbers on discrete cell types or on noise; no algorithm tests whether a continuum exists. Decide topology first with PAGA connectivity, then order.
3. Root-cell choice flips every gene trend. Pseudotime is defined only up to an origin; the sign of every trend and which cells are "early" invert with the root. Anchor the root with orthogonal evidence (known marker, real sampling time, velocity, or a stemness score), never by eye on a UMAP, which distorts global geometry. When no progenitor marker and no real timepoints are available and velocity is invalid (mature or non-cycling tissue), fall back to a model-free stemness score (CytoTRACE/CytoTRACE2) to nominate the root, and treat the resulting direction as a hypothesis rather than an established origin.
4. Near bifurcations use fate PROBABILITIES, not hard branch labels. A multipotent progenitor's fate is genuinely undetermined, so a hard assignment to one lineage is biologically false. Represent each cell as a distribution over terminal fates (Palantir, CellRank).
5. Transcriptomic state does not fully predict fate (Weinreb 2020). Sister cells in an indistinguishable state systematically diverge in fate, so a state-based branch call can be systematically wrong at exactly the decision point it most wants to resolve. Frame fate calls as predictions, not measurements, and validate with orthogonal evidence.

Snapshot dynamics are formally non-identifiable (Weinreb 2018, gauge freedom): a single snapshot constrains a family of dynamics, not one, and a unique answer requires extra assumptions (a potential field, known birth-death rates, or real timepoints). Treat any single-method pseudotime as a hypothesis to cross-validate, never a measurement.

## Method Decision Table

Saelens 2019 benchmarked 45 methods across 110 real + 229 synthetic datasets: no single method wins across all topologies, so selection is topology-first.

| Method | Model / assumption | Use when | Fails when |
|--------|--------------------|----------|------------|
| PAGA (Wolf 2019) | cluster-graph connectivity = observed vs expected inter-cluster edges | deciding IF a continuum exists; unknown, disconnected, or cyclic topology; the mandatory first step | gives connectivity not pseudotime/direction; threshold is manual; resolution-dependent |
| Slingshot (Street 2018) | MST on cluster centroids + simultaneous principal curves | known tree/bifurcating topology; smooth per-lineage curves; tradeSeq DE | depends entirely on input clustering; no cycles/disconnection; scales poorly |
| Monocle3 (Cao 2019) | principal graph (reversed graph embedding) in UMAP space | tree, cyclic, or disconnected topology without pre-clustered lineages; Moran's-I trajectory DE | graph learned in UMAP inherits global distortion; resolution/seed-sensitive |
| DPT (Haghverdi 2016) | reversible diffusion random walk; diffusion distance from root | linear or simple-branching; fast native-scanpy scalar after PAGA fixes topology | undirected (reversible model for an irreversible process); root-sensitive; weak at branching |
| Palantir (Setty 2019) | directed Markov chain on diffusion graph oriented by an early cell | branching fate; needs fate probabilities + differentiation-potential entropy | root-sensitive; entropy is a model-internal proxy; auto terminal states can be spurious |
| CellRank 2 (Weiler 2024) | non-reversible Markov chain; direction from pluggable kernels; GPCCA macrostates | directed fate mapping; multiview evidence; millions of cells; uncertainty-aware fate probabilities | kernel-quality dependent (garbage direction in, confident states out); n_states selection; metastability assumption |

Choosing by topology: linear -> Slingshot/DPT; bifurcating/multifurcating -> Slingshot/Palantir/CellRank 2; tree (>2 branches) -> Slingshot/Monocle3/PAGA-Tree; cyclic -> PAGA (Slingshot/Monocle2 cannot); disconnected/unknown -> PAGA first, then per-component pseudotime. Methodology evolves; verify current best practice against installed package docs before committing to one method, and report multi-method concordance.

### Decide Topology First With PAGA

**Goal:** Test whether putative branches are truly connected before committing to a continuous model.
**Approach:** Partition the kNN graph, compute PAGA connectivity, prune weak edges by threshold, then seed a global-faithful UMAP from PAGA.

```python
import scanpy as sc, numpy as np
sc.pp.neighbors(adata, n_neighbors=15, use_rep='X_pca')
sc.tl.leiden(adata, resolution=1.0, flavor='igraph', n_iterations=2, directed=False)
sc.tl.paga(adata, groups='leiden')
sc.pl.paga(adata, threshold=0.03, color='leiden')   # prune low-connectivity (likely spurious) edges
sc.tl.umap(adata, init_pos='paga')                  # global topology preserved, local detail kept
```

The `threshold` in `sc.pl.paga` is the key judgment call: isolated clusters with no surviving edges are discrete cell types, not trajectory branches, and must not be forced into one ordering.

### Diffusion Pseudotime From an Anchored Root

**Goal:** Assign a scalar pseudotime once topology is fixed.
**Approach:** Run a diffusion map, set the root as a positional index on `adata.uns['iroot']`, then run DPT.

```python
sc.tl.diffmap(adata, n_comps=15)
adata.uns['iroot'] = np.flatnonzero(adata.obs['cell_type'] == 'HSC')[0]   # root anchored by a known marker, not by eye
sc.tl.dpt(adata, n_dcs=10, n_branchings=0)          # n_branchings=0 -> pure pseudotime; branch mode is fragile
```

`iroot` is a positional integer into `adata.obs_names`, set on `adata.uns` BEFORE `dpt`. The entire ordering and the sign of every gene trend flip with this choice.

### Fate Probabilities With Palantir

**Goal:** Represent each cell as a distribution over terminal fates near bifurcations.
**Approach:** Build a diffusion-map multiscale space, run Palantir from an early cell, and read pseudotime, entropy, and branch probabilities.

```python
import palantir
dm_res = palantir.utils.run_diffusion_maps(adata, n_components=5)
ms_data = palantir.utils.determine_multiscale_space(dm_res)
pr_res = palantir.core.run_palantir(ms_data, early_cell='HSC_cell_id', terminal_states=None, num_waypoints=1200)
# pr_res.pseudotime, pr_res.entropy (differentiation potential), pr_res.branch_probs
```

Entropy of the fate-probability vector is the differentiation-potential proxy: high near multipotent cells, falling toward 0 as cells commit. Auto terminal-state detection can miss real fates or invent spurious ones, so verify terminals against markers.

### Directed Fate Mapping With CellRank 2

**Goal:** Infer initial states, terminal states, and uncertainty-aware fate probabilities from any directional evidence source.
**Approach:** Build a directed transition matrix from one or more kernels, combine with a connectivity kernel for smoothing, then coarse-grain into macrostates with GPCCA.

```python
import cellrank as cr
pk = cr.kernels.PseudotimeKernel(adata, time_key='dpt_pseudotime').compute_transition_matrix()
ck = cr.kernels.ConnectivityKernel(adata).compute_transition_matrix()
combined = 0.8 * pk + 0.2 * ck                      # weights are a researcher choice; sweep them

g = cr.estimators.GPCCA(combined)
g.compute_macrostates(n_states=10, cluster_key='leiden')   # n_states from the Schur/eigenvalue spectral gap
g.predict_terminal_states(method='stability')
g.predict_initial_states(n_states=1)
g.compute_fate_probabilities()
g.compute_lineage_drivers()
```

Kernels decouple WHERE direction comes from (RealTime when timepoints exist, Pseudotime/CytoTRACE otherwise, Velocity only when trustworthy, Connectivity for smoothing) from WHAT is computed (GPCCA macrostates + fate probabilities). Prefer the RealTimeKernel for time courses. Fate probabilities are a deterministic function of the transition matrix, so a wrong kernel yields confidently wrong, well-formed probabilities with no internal warning; check that conclusions survive dropping the velocity kernel.

### Slingshot and Monocle3 (R)

**Goal:** Fit smooth lineage curves (Slingshot) or a principal graph (Monocle3) and order cells.
**Approach:** Slingshot needs user-supplied dimred + cluster labels + a start cluster; Monocle3 learns its own graph and roots by node.

```r
library(slingshot)
sce <- slingshot(sce, clusterLabels='seurat_clusters', reducedDim='UMAP', start.clus='HSC')
pt  <- slingPseudotime(sce)     # cells x lineages; NA off-lineage; a trunk cell scores in every descendant lineage
```

```r
library(monocle3)
cds <- cluster_cells(cds)                           # produces clusters AND partitions
cds <- learn_graph(cds, use_partition = TRUE)       # TRUE allows disconnected trajectories
cds <- order_cells(cds, root_pr_nodes = root_node)  # root via graph node name, anchored by biology
graph_test_res <- graph_test(cds, neighbor_graph = 'principal_graph', cores = 4)   # Moran's I trajectory DE
```

`start.clus` is mandatory in practice for Slingshot; downstream DE goes through tradeSeq (`fitGAM` then `associationTest` for any-variation-along-pseudotime or `startVsEndTest` for endpoint contrasts), not Slingshot itself. Monocle3's own trajectory DE is `graph_test` above. Monocle3's principal graph is learned in UMAP space, so loops and branches can be embedding artifacts.

## RNA Velocity

RNA velocity infers the time derivative of the spliced-mRNA state from the lag between unspliced (nascent) and spliced mRNA: velocity ds/dt = beta*u - gamma*s. It is a model-based extrapolation on a timescale of hours, and every downstream claim inherits the model's assumptions.

| Mode (`mode=`) | Model | Use when | Fails when |
|----------------|-------|----------|------------|
| `'deterministic'` | La Manno steady-state regression on extreme quantiles | quick first pass; well-separated induction/repression | assumes common splicing rate and that data spans both steady states; transient populations mis-fit |
| `'stochastic'` (default) | adds 2nd-moment treatment; GLS on both moments | a more robust gamma without the dynamical EM cost | still steady-state; same constant-rate assumption |
| `'dynamical'` | full likelihood EM; per-gene alpha/beta/gamma + latent time | transient states; needs gene-shared latent time | `recover_dynamics` dominates runtime; can still mis-fit multi-kinetics genes |

**Goal:** Estimate velocity direction and a latent-time ordering.
**Approach:** Compute moments, recover dynamics (dynamical only), compute velocity, build the velocity graph, then sanity-check confidence and phase portraits before any embedding plot.

```python
import scvelo as scv
scv.pp.filter_and_normalize(adata, min_shared_counts=20, n_top_genes=2000)
scv.pp.moments(adata, n_pcs=30, n_neighbors=30)
scv.tl.recover_dynamics(adata)                      # dynamical only
scv.tl.velocity(adata, mode='dynamical')            # DEFAULT is 'stochastic'; pass 'dynamical' explicitly
scv.tl.velocity_graph(adata)
scv.tl.velocity_confidence(adata)                   # inspect BEFORE trusting the stream plot
scv.pl.velocity(adata, var_names=['GATA1'])         # per-gene phase portrait, not just the embedding
```

Bergen 2021 failure modes are the DEFAULT expectation, not edge cases. Velocity is unreliable or invalid in mature/terminal/non-dividing systems (adult neurons, steady-state tissue), where little net du/dt means noise dominates and arrows can point backward; under heterogeneous kinetics, one global gamma per gene mis-fits multi-branch systems; and a clean 2D stream plot can manufacture coherence the high-dimensional field lacks. Deeper still (Gorin 2022), the velocity ODE is a deterministic reduction of a stochastic process, intronic reads are a biased proxy for nascent RNA (internal priming, intron retention, 3' and length bias all corrupt gamma), and confidence/coherence metrics reward the kNN smoothing of the moments step rather than correspondence to truth (Zheng 2023). Do not consume raw arrows: feed velocity into CellRank 2 as ONE kernel, validate against known markers or metabolic labeling, and gate interpretation with uncertainty (veloVI `get_directional_uncertainty`).

Quantifier disagreement is first-order, not a detail (Soneson 2021): velocyto vs kb-python (`nac`) vs alevin-fry (USA mode) vs STARsolo (`--soloFeatures Gene Velocyto`) use different intron models and ambiguous-read rules, which shift the unspliced/spliced ratio, change gamma, and can flip velocity sign on borderline genes. Single-nucleus data is intron-rich; use the nascent/mature (`nac`/spliceu) framing. A direction that is not stable across at least two quantifiers is a pipeline artifact, not a finding.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Smooth pseudotime axis through what are actually discrete cell types | no real continuum; kNN bridges islands with spurious edges | run PAGA first; if clusters have no surviving connectivity edges, do not order them |
| Every gene trend reverses between runs | root chosen by eye / on a UMAP; ordering flips with origin | anchor `iroot`/`root_pr_nodes` with a known marker, real time, velocity, or stemness |
| Branch assignment unstable across parameters | hard-assigning progenitors whose fate is genuinely undetermined | report fate PROBABILITIES (Palantir branch_probs, CellRank), do not hard-assign near bifurcations |
| Trajectory passes through a near-empty region | rare/fast-traversed intermediate state is unsampled; graph interpolates a void | check cell density along the path; treat the gap as missing data, not a real intermediate |
| Velocity stream looks clean but points backward | mature/terminal/non-cycling system; little net du/dt, noise dominates | velocity is invalid here; do not interpret arrows; validate with markers/lineage or drop velocity |
| Velocity direction flips when the quantifier changes | intron model / ambiguous-read handling differs across tools | re-run with a second quantifier; only trust direction stable across both (Soneson 2021) |
| high `velocity_confidence` but biologically wrong arrows | metric rewards kNN smoothing, not truth (Zheng 2023) | sweep `n_neighbors`; require orthogonal validation, not the confidence score alone |
| CellRank invents discrete macrostates from a smooth flow | metastability assumption violated; GPCCA forced to partition a continuum | show the Schur/eigenvalue spectrum; justify n_states by a real gap or treat states as coarse-graining artifacts |
| Pseudotime intervals reported as durations | pseudotime is monotone in progression, not time | only RealTimeKernel/WOT exploit actual time; do not read intervals as elapsed hours |

## Related Skills

- single-cell/clustering - Leiden clusters and the kNN graph that PAGA, DPT, and the velocity moments step all depend on
- single-cell/preprocessing - normalization, HVG selection, and PCA whose choices the inferred axis inherits
- single-cell/lineage-tracing - orthogonal lineage ground truth that tests whether a state-based trajectory predicts fate
- single-cell/cell-communication - downstream signaling analysis along the inferred trajectory
- differential-expression/deseq2-basics - pseudobulk DE between trajectory endpoints or branches

## References

Haghverdi L, Buttner M, Wolf FA, Buettner F, Theis FJ (2016). Diffusion pseudotime robustly reconstructs lineage branching. Nat Methods 13(10):845-848.
Street K, Risso D, Fletcher RB, et al. (2018). Slingshot: cell lineage and pseudotime inference for single-cell transcriptomics. BMC Genomics 19:477.
Cao J, Spielmann M, Qiu X, et al. (2019). The single-cell transcriptional landscape of mammalian organogenesis (Monocle3). Nature 566(7745):496-502.
Wolf FA, Hamey FK, Plass M, et al. (2019). PAGA: graph abstraction reconciles clustering with trajectory inference. Genome Biology 20:59.
Setty M, Kiseliovas V, Levine J, et al. (2019). Characterization of cell fate probabilities in single-cell data with Palantir. Nat Biotechnol 37:451-460.
Saelens W, Cannoodt R, Todorov H, Saeys Y (2019). A comparison of single-cell trajectory inference methods. Nat Biotechnol 37(5):547-554.
Lange M, Bergen V, Klein M, et al. (2022). CellRank for directed single-cell fate mapping. Nat Methods 19(2):159-170.
Weiler P, Lange M, Klein M, Pe'er D, Theis FJ (2024). CellRank 2: unified fate mapping in multiview single-cell data. Nat Methods 21(7):1196-1205.
La Manno G, Soldatov R, Zeisel A, et al. (2018). RNA velocity of single cells. Nature 560:494-498.
Bergen V, Lange M, Peidli S, Wolf FA, Theis FJ (2020). Generalizing RNA velocity to transient cell states through dynamical modeling (scVelo). Nat Biotechnol 38(12):1408-1414.
Bergen V, Soldatov RA, Kharchenko PV, Theis FJ (2021). RNA velocity - current challenges and future perspectives. Mol Syst Biol 17(8):e10282.
Gayoso A, Weiler P, Lotfollahi M, et al. (2024). Deep generative modeling of transcriptional dynamics for RNA velocity analysis (veloVI). Nat Methods 21:50-59.
Weinreb C, Wolock S, Tusi BK, Socolovsky M, Klein AM (2018). Fundamental limits on dynamic inference from single-cell snapshots. PNAS 115(10):E2467-E2476.
Weinreb C, Rodriguez-Fraticelli A, Camargo FD, Klein AM (2020). Lineage tracing on transcriptional landscapes links state to fate (LARRY). Science 367(6479):eaaw3381.
Gorin G, Fang M, Chari T, Pachter L (2022). RNA velocity unraveled. PLoS Comput Biol 18(9):e1010492.
Zheng SC, Stein-O'Brien G, Boukas L, Goff LA, Hansen KD (2023). Pumping the brakes on RNA velocity by understanding and interpreting RNA velocity estimates. Genome Biology 24(1):246.
Soneson C, Srivastava A, Patro R, Stadler MB (2021). Preprocessing choices affect RNA velocity results for droplet scRNA-seq data. PLoS Comput Biol 17(1):e1008585.
<!-- END FILE: single-cell/trajectory-inference/SKILL.md -->

<!-- END CATEGORY: single-cell -->

