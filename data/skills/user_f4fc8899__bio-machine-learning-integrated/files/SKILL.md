---
slug: bio-machine-learning-integrated
version: 1.0.1
displayName: "机器学习 / Machine learning"
name: bio-machine-learning-integrated
summary: "中文：机器学习综合技能，整合 6 个相关专题，覆盖机器学习：生物标志物发现、p>>n分类器、泄漏安全验证、SHAP解释、生存预测。 English: Integrated Machine learning skill covering 6 related topics, including Machine learning: biomarker discovery, p>>n classifiers, leakage-safe validation, SHAP explanation, survival prediction."
description: "中文：这是一个面向机器学习的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：机器学习：生物标志物发现、p>>n分类器、泄漏安全验证、SHAP解释、生存预测。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：boruta, scikit-survival, scvi-tools。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Machine learning, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Machine learning: biomarker discovery, p>>n classifiers, leakage-safe validation, SHAP explanation, survival prediction. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: boruta, scikit-survival, scvi-tools. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# machine-learning 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: machine-learning -->

## 子目录：machine-learning/atlas-mapping

<!-- BEGIN FILE: machine-learning/atlas-mapping/SKILL.md -->
---
name: bio-machine-learning-atlas-mapping
description: Maps query single-cell data onto reference atlases and transfers cell-type labels using scArches surgery (scVI/scANVI), Symphony, Azimuth, CellTypist, scPoli, popV, and foundation models, with explicit out-of-distribution and label-transfer uncertainty. Use when annotating new single-cell datasets against a pre-trained reference, deciding which mapping method fits, or judging whether transferred labels are trustworthy. For de novo clustering and manual annotation see single-cell/cell-annotation; for batch integration without a reference see single-cell/batch-integration.
tool_type: python
primary_tool: scvi-tools
---

## Version Compatibility

Reference examples tested with: anndata 0.10+, scanpy 1.10+, scvi-tools 1.1+, scikit-learn 1.3+, celltypist 1.6+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

scvi-tools 1.x has had API churn around minified/registered models and the semi-supervised loader. Confirm `scvi.__version__` and `help(scvi.model.SCANVI.load_query_data)` before relying on argument names. If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Reference Mapping and Label Transfer for Single-Cell Data

**"Annotate my scRNA-seq query against a reference atlas"** -> Project query cells into a fixed reference latent space and transfer labels, then gate every label on an out-of-distribution signal.
- scArches surgery: `scvi.model.SCANVI.prepare_query_anndata()` -> `load_query_data()` -> `train(plan_kwargs={'weight_decay': 0.0})` -> `predict(soft=True)`
- Linear/fixed reference: Symphony (R) or Azimuth/Seurat anchor transfer
- Pure classifier (no embedding): CellTypist logistic regression

## The Single Most Important Modern Insight -- Mapping Is a Projection, Not an Annotation Oracle

Reference mapping indicates *where in a fixed reference manifold a query cell lands*; it does not establish whether that location is biologically meaningful for the query. The projection always succeeds geometrically: every query cell is assigned its nearest reference label whether or not that label is true. A softmax over reference classes is normalized to sum to 1 and therefore *cannot* express "I have never seen this cell" -- a hepatocyte handed to an immune reference gets confidently called a T cell. Every failure mode below is a corollary of confusing projection with annotation.

The operational consequence: a transferred label is untrustworthy until paired with an out-of-distribution / label-transfer-uncertainty signal that measures *whether the cell belongs to the reference at all*, which is a different quantity from the prediction probability that measures *which reference label*. Conflating these two is the field's most common error.

## Methods Taxonomy

| Method | Model class | Needs reference model? | Novel-cell-type signal | Best when | Fails when |
|--------|-------------|------------------------|------------------------|-----------|------------|
| scVI + scArches surgery | Conditional VAE; surgery freezes reference weights, fits query-batch nodes | Yes (saved scVI model) | None intrinsic; add kNN uncertainty / OOD distance | Unseen batch; want a de novo joint embedding then cluster query yourself | Expected to *label* (it only embeds); reference lacks query biology |
| scANVI + scArches surgery | Semi-supervised VAE (scVI latent + label classifier head) | Yes (scANVI, often `from_scvi_model`) | Classifier softmax (overconfident); kNN-on-latent uncertainty | Reference well-labeled, query is the *same* tissue/biology | Semi-supervised leakage carves latent; novel states confidently mislabeled |
| Symphony | Linear Harmony soft-cluster mixture; query projected into fixed reference | Yes (compressed reference object) | Per-cell Mahalanobis distance to soft-cluster centroids | Seconds-scale, deterministic, CPU-only, reproducible/clinical | Strong nonlinear batch the reference never saw |
| Azimuth / Seurat anchor transfer | CCA/PCA anchors; supervised PCA projection | Yes (precomputed ref) | `prediction.score.max`, `mapping.score` | Multimodal refs (CITE-seq/WNN), curated tissue atlases, R shop | Filtered-anchor pathology when query is very divergent |
| scPoli | Conditional VAE + learnable sample embeddings + cell-type prototypes | Yes (built on scArches) | Prototype distance + uncertainty | Want sample-level (patient) embeddings too, many small batches | Few samples (condition embedding underdetermined) |
| popV | Ensemble of methods + ontology-aware voting | Mixed (wraps several) | Cross-method disagreement = uncertainty | High-stakes atlas annotation; distrust any single method | Compute-heavy; consensus can be confidently wrong if all share reference bias |
| CellTypist | Logistic regression (pre-trained models) | No embedding (ships models) | Low max-probability = ambiguous; no true OOD | Fast immune annotation, no integration needed | Treated as a mapper (no shared embedding, no batch handling) |
| treeArches / scHPL | scArches + hierarchical classifier with rejection | Yes | Explicit rejection -> "unseen" node | Expect novel subtypes, want hierarchy-aware fallback | Mis-specified hierarchy propagates error down branches |
| Foundation models (scGPT, Geneformer) | Transformer pretrained on 10s of millions of cells | Checkpoint; fine-tune needs labels | None intrinsic; OOD poorly characterized | *Fine-tuned* on the target task; cross-modality/species; data-scarce | Zero-shot: underperform scVI/Harmony/HVG-PCA (Kedzierska 2025) |

Cross-cutting: linear methods (Symphony, Azimuth-sPCA) give a *fixed, reproducible* reference embedding (the query never perturbs the reference); VAE surgery *fine-tunes* and can drift. Reproducibility-critical or clinical pipelines lean linear; maximal batch-effect flexibility leans VAE.

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Same tissue as a published scVI/scANVI atlas; want one embedding + labels | scArches surgery onto the scANVI model; then gate labels on kNN uncertainty | Built for this; reuses the learned manifold; only query fine-tuned |
| Seconds-scale, deterministic, CPU-only, must re-run identically (clinical) | Symphony (or Azimuth if curated) | Fixed reference embedding, no fine-tuning drift, built-in Mahalanobis OOD |
| Query likely contains cell types/states NOT in the reference (disease, new niche) | treeArches/scHPL rejection, or scArches + explicit OOD distance | Default kNN/softmax confidently mislabels novel cells |
| High-stakes annotation; distrust any single method | popV ensemble | Cross-method disagreement is a more honest uncertainty than any softmax |
| Want patient/sample-level structure too | scPoli | Only method learning sample (condition) embeddings jointly with cell prototypes |
| Just need fast immune labels, no integration | CellTypist (`Immune_All_Low`, `majority_voting=True`) | Calibrated classifier, no embedding needed; QC the query first |
| Multimodal reference (CITE-seq/ATAC) | Azimuth/Seurat WNN or totalVI+scArches | Anchor framework natively weights modalities |
| Considering scGPT/Geneformer | Only if fine-tuning with labels, or cross-modality/species, or data too scarce | Zero-shot foundation embeddings are not a justified default for same-tissue transfer |
| De novo clustering, no reference, or manual marker annotation | -> single-cell/markers-annotation, single-cell/clustering | Out of scope here |

## scArches Surgery: Embedding (scVI)

**Goal:** Project query cells into a pre-trained reference latent space without retraining on combined data.

**Approach:** Align query genes to the reference exactly, load into the frozen reference model, and fine-tune only query-specific parameters with zero weight decay so the shared manifold does not drift.

```python
import scvi
import scanpy as sc

ref_model = scvi.model.SCVI.load('reference_model/')          # saved with save_anndata=True (or minified)

adata_query = sc.read_h5ad('query.h5ad')
# Align genes to the reference EXACTLY: zero-pad missing, reorder. Mandatory and silent if skipped.
scvi.model.SCVI.prepare_query_anndata(adata_query, 'reference_model/')

query_model = scvi.model.SCVI.load_query_data(adata_query, 'reference_model/')
# weight_decay=0.0 + frozen reference weights make surgery a query-only fine-tune;
# non-zero decay drifts the shared latent and breaks cross-query comparability.
query_model.train(max_epochs=200, plan_kwargs={'weight_decay': 0.0}, check_val_every_n_epoch=10)
adata_query.obsm['X_scVI'] = query_model.get_latent_representation()
```

## scANVI Label Transfer

**Goal:** Transfer reference cell-type labels to an unlabeled query.

**Approach:** Build a semi-supervised scANVI head on the reference, map the query by surgery, then read hard labels and per-class probabilities -- treating the probability as "which label," not "does it belong."

```python
# Reference side (once): scANVI from a trained scVI model. unlabeled_category is REQUIRED.
ref_scanvi = scvi.model.SCANVI.from_scvi_model(ref_vae, unlabeled_category='Unknown', labels_key='cell_type')
ref_scanvi.train(max_epochs=20, n_samples_per_label=100)
ref_scanvi.save('ref_scanvi/', save_anndata=True)

# Query side (surgery):
scvi.model.SCANVI.prepare_query_anndata(adata_query, 'ref_scanvi/')
query_scanvi = scvi.model.SCANVI.load_query_data(adata_query, 'ref_scanvi/')
query_scanvi.train(max_epochs=100, plan_kwargs={'weight_decay': 0.0})

adata_query.obs['predicted_label'] = query_scanvi.predict()          # hard labels
adata_query.obsm['X_scANVI'] = query_scanvi.get_latent_representation()
proba = query_scanvi.predict(soft=True)                             # per-class probabilities (which label)
```

## Out-of-Distribution Gating (the step that makes labels trustworthy)

**Goal:** Decide *whether* each query cell belongs to the reference, separately from which label it would get.

**Approach:** Compute a distance/entropy signal on the shared latent. The canonical scArches/HLCA approach is a weighted-kNN label-transfer uncertainty (neighbor disagreement in the reference latent), thresholded at 0.2 to set cells to "Unknown." A portable kNN-entropy version is shown; the softmax `proba` is NOT this signal.

```python
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

ref_latent = ref_scanvi.get_latent_representation()                  # reference cells in latent
knn = KNeighborsClassifier(n_neighbors=15, weights='distance').fit(ref_latent, adata_ref.obs['cell_type'])
query_latent = adata_query.obsm['X_scANVI']

neighbor_proba = knn.predict_proba(query_latent)                    # weighted neighbor label distribution
# Uncertainty = 1 - max neighbor agreement. HLCA sets cells above 0.2 to 'Unknown'.
uncertainty = 1.0 - neighbor_proba.max(axis=1)
adata_query.obs['transfer_uncertainty'] = uncertainty
adata_query.obs.loc[uncertainty > 0.2, 'predicted_label'] = 'Unknown'   # gate, do not trust ungated labels
print(f'Flagged Unknown: {(uncertainty > 0.2).mean():.1%}')
```

## Per-Method Failure Modes

### scANVI / kNN -- forcing the query onto reference labels
- **Trigger:** Query contains a population absent from the reference (novel type, disease state, perturbed program).
- **Mechanism:** The classifier/kNN assigns every query cell to its nearest reference label; there is no "none of the above" unless added.
- **Symptom:** A coherent novel cluster split across 2-3 reference labels, each with *high* probability; the UMAP looks "well integrated."
- **Fix:** Always gate on transfer uncertainty / OOD distance (above). Inspect query-only clusters for marker genes independent of transferred labels.

### Softmax overconfidence vs label-transfer uncertainty conflated
- **Trigger:** Reporting "confidence" as the `predict(soft=True)` max.
- **Mechanism:** The softmax measures *which* reference label conditional on belonging; it is normalized away from distance and cannot say "far from everything." A cell can be 0.99 "T cell" and be a hepatocyte.
- **Symptom:** Pipeline filters on softmax >= 0.5 and still passes OOD cells.
- **Fix:** Threshold the weighted-kNN uncertainty (HLCA 0.2) or a Mahalanobis/ensemble OOD signal for the "Unknown" decision; use the softmax only to disambiguate among in-distribution labels.

### scANVI -- semi-supervised label leakage / latent carving
- **Trigger:** scANVI reference where labels strongly drive latent geometry; trajectory or novel-state query.
- **Mechanism:** The classifier head back-propagates label structure into the latent, carving it to separate reference types; query cells are pulled toward that structure even when their biology lies between/outside it.
- **Symptom:** A query continuum (differentiation trajectory) collapses onto discrete reference clusters; intermediate states vanish.
- **Fix:** For trajectory/novel-state queries prefer *unsupervised* scVI surgery, annotate the query independently, and cross-check against the scVI latent.

### Reference composition / missing-biology bias
- **Trigger:** Reference from healthy/limited donors; query from disease, different age, ancestry, or tissue region.
- **Mechanism:** The reference manifold is the entire hypothesis space; off-manifold cells are projected onto the nearest on-manifold point and rare reference populations act as attractors.
- **Symptom:** Disease-specific states labeled as the closest healthy type; ancestry/age effects read as "batch."
- **Fix:** Audit reference composition before mapping; prefer references covering the query's expected biology; treat mapping as hypothesis generation and validate query findings de novo; consider extending the reference (treeArches).

### Query QC artifacts laundered into confident labels
- **Trigger:** Query not QC'd to the reference's standard (empty droplets, ambient RNA, doublets, high-MT).
- **Mechanism:** A doublet sits between two reference types and maps to a spurious "intermediate"; ambient RNA shifts profiles toward the dominant type.
- **Symptom:** Artifactual "transitional" populations; doublet clusters labeled as rare real types.
- **Fix:** Run full query QC *before* mapping (single-cell/doublet-detection, ambient correction, MT/count filters matched to the reference). Mapping does not clean data.

### Feature-space / gene-set mismatch
- **Trigger:** Query missing reference HVGs; different gene annotation/version; `prepare_query_anndata` skipped.
- **Mechanism:** The encoder expects the exact reference gene order; missing genes are zero-padded and reordering silently corrupts the input.
- **Symptom:** Garbage latent, everything maps to one blob, or a silent accuracy cliff (no error raised).
- **Fix:** Always `prepare_query_anndata(query, reference_model)`; verify the shared-gene fraction; too few shared HVGs is a hard stop.

### Good integration metrics, wrong labels
- **Trigger:** Judging mapping by scIB integration scores alone.
- **Mechanism:** Integration metrics reward query/reference mixing; mixing OOD cells into the wrong neighborhood *raises* the batch-removal score, and bio-conservation uses reference labels (circular for the query).
- **Symptom:** Top scIB total score with biologically wrong annotation.
- **Fix:** Integration metrics validate the *embedding*, not labels. Evaluate transfer on held-out labeled query cells (per-type F1, especially rare types), OOD detection on spiked-in unseen types, and marker-gene sanity checks.

### Zero-shot foundation-model embedding as a mapper
- **Trigger:** Using scGPT/Geneformer zero-shot embeddings for clustering/transfer expecting SOTA.
- **Mechanism:** The masked-gene pretraining objective does not guarantee a label- or batch-aware embedding; zero-shot embeddings are not batch-corrected.
- **Symptom:** Worse AvgBio/integration than scVI or even HVG-PCA + Harmony.
- **Fix:** Fine-tune with task labels, or use an established mapper; reserve foundation models for cross-modality/species/data-scarce cases (Kedzierska 2025).

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| scANVI label confident but kNN uncertainty high | OOD cell forced onto nearest label | Trust the uncertainty; set Unknown and inspect markers |
| Symphony Mahalanobis flags OOD but scANVI does not | scANVI latent carved to absorb the cell | Prefer the distance-based flag; novel biology likely |
| popV members disagree | Genuine ambiguity or granularity mismatch | Route to manual review; report the disagreement, do not force a leaf |
| High scIB score, poor per-type F1 on held-out labels | Embedding mixes well but labels wrong | Believe the F1; integration score is not a label metric |

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Transfer uncertainty > 0.2 -> "Unknown" | Sikkema 2023 (HLCA) | Weighted-kNN neighbor-disagreement cutoff bounding false labels; recalibrate per reference |
| Surgery `weight_decay=0.0`, ~100-200 epochs | scvi-tools scArches tutorial | Frozen reference weights + no decay keep the shared latent fixed |
| scIB total = 0.6*bio + 0.4*batch | Luecken 2022 | Benchmark weighting; scores the embedding, NOT query labels |
| CellTypist input = log1p of CP10k | CellTypist docs | Wrong normalization silently degrades accuracy |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Everything maps to one blob | `prepare_query_anndata` skipped; gene mismatch | Run it before `load_query_data`; check shared-gene fraction |
| OOD cells pass a 0.5 softmax filter | Thresholding the wrong quantity | Gate on weighted-kNN uncertainty / OOD distance, not softmax |
| Reference cells move between runs | Non-zero `weight_decay` or over-training in surgery | Set `weight_decay=0.0`, keep `freeze_*` defaults, modest epochs |
| `load_query_data` errors on labels | scANVI needs `unlabeled_category` | Pass it to `from_scvi_model`; query labels filled with that category |
| CellTypist labels look random | Raw or wrongly normalized counts | Feed log1p CP10k input |

## References

- Lopez R, Regier J, Cole MB, Jordan MI, Yosef N. 2018. Deep generative modeling for single-cell transcriptomics. *Nat Methods* 15:1053-1058.
- Xu C, Lopez R, Mehlman E, Regier J, Jordan MI, Yosef N. 2021. Probabilistic harmonization and annotation of single-cell transcriptomics data with deep generative models. *Mol Syst Biol* 17:e9620.
- Lotfollahi M, Naghipourfar M, Luecken MD, et al. 2022. Mapping single-cell data to reference atlases by transfer learning. *Nat Biotechnol* 40:121-130.
- Kang JB, Nathan A, Weinand K, et al. 2021. Efficient and precise single-cell reference atlas mapping with Symphony. *Nat Commun* 12:5890.
- Hao Y, Hao S, Andersen-Nissen E, et al. 2021. Integrated analysis of multimodal single-cell data. *Cell* 184:3573-3587.
- De Donno C, Hediyeh-Zadeh S, Moinfar AA, et al. 2023. Population-level integration of single-cell datasets enables multi-scale analysis across samples. *Nat Methods* 20:1683-1692.
- Ergen C, Xing G, Xin C, et al. 2024. Consensus prediction of cell type labels in single-cell data with popV. *Nat Genet* 56:2731-2738.
- Dominguez Conde C, Xu C, Jarvis LB, et al. 2022. Cross-tissue immune cell analysis reveals tissue-specific features in humans. *Science* 376:eabl5197.
- Michielsen L, Lotfollahi M, Strobl D, et al. 2023. Single-cell reference mapping to construct and extend cell-type hierarchies. *NAR Genom Bioinform* 5:lqad070.
- Luecken MD, Buttner M, Chaichoompu K, et al. 2022. Benchmarking atlas-level data integration in single-cell genomics. *Nat Methods* 19:41-50.
- Sikkema L, Ramirez-Suastegui C, Strobl DC, et al. 2023. An integrated cell atlas of the lung in health and disease. *Nat Med* 29:1563-1577.
- Kedzierska KZ, Crawford L, Amini AP, Lu AX. 2025. Zero-shot evaluation reveals limitations of single-cell foundation models. *Genome Biol* 26:101.

## Related Skills

- single-cell/preprocessing - QC, normalization, and HVG selection the query needs before mapping
- single-cell/markers-annotation - Manual marker-based cluster annotation when there is no reference
- single-cell/batch-integration - Integrating datasets without a labeled reference
- single-cell/doublet-detection - Removing doublets that map to spurious intermediates
- differential-expression/de-results - Pseudobulk validation of mapping-derived populations
<!-- END FILE: machine-learning/atlas-mapping/SKILL.md -->

## 子目录：machine-learning/biomarker-discovery

<!-- BEGIN FILE: machine-learning/biomarker-discovery/SKILL.md -->
---
name: bio-machine-learning-biomarker-discovery
description: Selects biomarker features from high-dimensional omics data using Boruta all-relevant selection, mRMR, LASSO/elastic-net, and stability selection, while controlling the leakage, irreproducibility, and correlated-feature traps that make most published signatures fail to replicate. Use when identifying candidate biomarkers, deciding between an all-relevant and a minimal-optimal selector, or judging whether a selected gene set is reproducible. For unbiased performance estimation of the resulting model see machine-learning/model-validation; for interpreting a trained model see machine-learning/prediction-explanation.
tool_type: python
primary_tool: boruta
---

## Version Compatibility

Reference examples tested with: numpy 1.26+, pandas 2.2+, scikit-learn 1.4+, boruta 0.4+, mrmr-selection 0.2+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

BorutaPy expects numpy arrays and breaks on newer numpy where the `np.float`/`np.int` aliases were removed -- pin a compatible numpy or use a maintained fork. On scikit-learn 1.8+ the `LogisticRegression(penalty=)` argument is deprecated (removed in 1.10) in favor of `l1_ratio`+`C`; the examples show the 1.4-1.7 form. If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Feature Selection for Biomarker Discovery

**"Find the biomarkers in my omics data"** -> First decide which question is being answered (all-relevant vs minimal-optimal), then select features INSIDE a resampling loop, then quantify stability -- because a selected list means little without it.
- All-relevant (which genes carry signal?): `BorutaPy(rf)`
- Minimal-optimal (smallest predictive set?): `ElasticNetCV`, `LogisticRegressionCV(penalty='elasticnet')`
- Stability (does the list reproduce?): bootstrap selection frequencies + a stability index

## The Single Most Important Modern Insight -- Most Gene Signatures Do Not Replicate, and Significance Is the Wrong Bar

A signature being "significantly associated with outcome" is near-worthless evidence: *random* gene sets -- and signatures of biologically irrelevant phenomena -- are significantly associated with breast-cancer survival, often matching published prognostic signatures, because the transcriptome is dominated by a few axes (proliferation) that almost any large gene set captures (Venet 2011). The correct null is not "no association" but *random gene sets of equal size* plus a proliferation meta-gene. Two further hard facts complete the picture: many disjoint gene lists predict equally well (Ein-Dor 2005), so non-overlap with a prior list is the *expected* result, not a contradiction; and obtaining a *stable* list (as opposed to an accurate predictor) needs on the order of thousands of samples (Ein-Dor 2006), far more than typical omics n.

The operational consequences run through every section below: report a stability index next to accuracy; benchmark against a random-signature and proliferation-meta-gene null; never interpret the specific genes a minimal-optimal selector kept as "the biomarkers"; and keep selection inside the cross-validation loop or the reported performance is fiction.

## All-Relevant vs Minimal-Optimal (the distinction usually conflated)

This axis matters more than filter/wrapper/embedded. Choosing the wrong one is the most common conceptual error in applied biomarker papers.

- **Minimal-optimal** = the *smallest* subset giving optimal prediction (LASSO, RFE, forward selection). If two genes are correlated and both informative, it keeps **one and drops the other**; the dropped gene is still biologically relevant. Minimal-optimal sets are non-unique, unstable, and systematically exclude redundant-but-real features. *Absence from a minimal-optimal set is not evidence of irrelevance.*
- **All-relevant** = *every* feature carrying information, redundant or not (Boruta: keep anything beating the best "shadow" permuted feature). This is the right framing for *biological interpretation* -- the whole co-expression module is wanted, not one representative.

Decision rule: parsimonious assay with few measurements -> minimal-optimal; understand biology / enumerate implicated genes / pathway analysis -> all-relevant; stable deployable signature -> elastic net or stability selection.

## Methods Taxonomy

| Family | Method | Optimizes | Redundancy handling | Output | Key trap |
|--------|--------|-----------|---------------------|--------|----------|
| Filter (univariate) | t-test / `SelectKBest(f_classif)` | Marginal association, one gene at a time | None (keeps correlated blocks) | Ranked list | Ignores multivariate structure; huge multiplicity |
| Filter (multivariate) | mRMR (Peng 2005) | Relevance minus redundancy | Explicit penalty | Ranked K | Greedy/first-order; K must still be chosen |
| Wrapper | RFE / RFECV; SVM-RFE | A specific model's accuracy | Indirect | Ranked subset | Expensive; **must be inside CV**; SVM-RFE needs a linear kernel |
| Embedded | LASSO (Tibshirani 1996) | Prediction + L1 sparsity | **None** -- arbitrarily keeps one of a correlated group | Sparse coefs | Unstable under collinearity; caps at n features when p>n |
| Embedded | Elastic net (Zou-Hastie 2005) | Prediction + L1+L2 grouping | Keeps correlated groups together | Sparse coefs | Two hyperparameters; still not "causal" |
| All-relevant | Boruta (Kursa 2010) | Every feature beating shadow features | Keeps all relevant (redundant included) | Confirmed/Tentative/Rejected | Slow; returns redundant sets by design |
| Meta / stability | Stability selection (Meinshausen 2010; Shah-Samworth 2013) | Selection probability under subsampling | Inherits base learner | Selection frequencies + threshold | Error bounds assume exchangeability omics violates |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Want every implicated gene for pathway/biology interpretation | Boruta (all-relevant), or stability-based consensus | Keeps whole correlated modules, not one representative |
| Want a small deployable assay/signature | Elastic-net (not bare LASSO); report stability | L2 grouping keeps correlated genes together and resamples more stably |
| p is huge (>20k); selection is slow | Univariate pre-filter to a few thousand, then Boruta/elastic-net, all inside the CV fold | Cheap dimensionality cut; never pre-filter on the full dataset |
| Need to report model performance | Wrap selection in a `Pipeline`, estimate by nested CV | Selection outside CV inflates AUC to ~perfect on pure noise |
| Single-cell biomarker across conditions | Pseudobulk per donor, then select at the donor level | The unit is the donor, not the cell (Squair 2021); cells are pseudoreplicates |
| Want to know which genes "drive" a trained model | -> machine-learning/prediction-explanation | SHAP ranking is not validated selection |
| Want unbiased accuracy/calibration of the selected model | -> machine-learning/model-validation | Selection is one step; validation is its own discipline |

## Leakage-Safe Selection (the single most damaging error to avoid)

**Goal:** Estimate the performance of a selection-plus-model pipeline without optimistic bias.

**Approach:** Put selection in a `Pipeline` so it is re-fit on each training fold only; the held-out fold never informs which features are kept. Selecting the top-k features on the *whole* dataset before cross-validating the classifier produces near-zero apparent error even on pure noise (Ambroise-McLachlan 2002). Selection is where almost all overfitting capacity lives when p>>n.

```python
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold

pipe = Pipeline([
    ('select', SelectKBest(f_classif, k=20)),               # re-fit per fold -> no leakage
    ('clf', LogisticRegression(penalty='l2', max_iter=5000)),
])
cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=0)
auc = cross_val_score(pipe, X, y, cv=cv, scoring='roc_auc')   # honest estimate
print(f'Nested-safe AUC: {auc.mean():.3f} +/- {auc.std():.3f}')
```

The standalone Boruta/LASSO blocks below select features on a full matrix to *discover* candidates; that is fine for discovery, but any performance number must come from the Pipeline pattern above, with selection inside the fold.

## All-Relevant: Boruta

**Goal:** Enumerate every feature carrying signal, including redundant co-expressed genes.

**Approach:** Compare each real feature's importance to the maximum importance of permuted "shadow" features over many iterations; confirm features that consistently beat the best shadow.

```python
from boruta import BorutaPy
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=100, n_jobs=-1, class_weight='balanced', max_depth=5, random_state=42)
# perc=100 uses the max shadow importance (strict); two_step (default True) controls the multiple-testing correction.
boruta = BorutaPy(rf, n_estimators='auto', perc=100, two_step=True, max_iter=100, random_state=42)
boruta.fit(X.values, y.values)                              # numpy arrays, not pandas

confirmed = X.columns[boruta.support_]                      # all-relevant set (redundant by design)
tentative = X.columns[boruta.support_weak_]
```

## Minimal-Optimal: Elastic Net (prefer over bare LASSO)

**Goal:** A small, stable predictive signature from correlated omics features.

**Approach:** Use elastic net, whose L2 term induces a grouping effect so correlated genes enter or leave together; standardize first because the penalty is scale-sensitive. Bare LASSO keeps one arbitrary member of a correlated group and flips on tiny data perturbations.

```python
from sklearn.linear_model import LogisticRegressionCV
from sklearn.preprocessing import StandardScaler

X_scaled = StandardScaler().fit_transform(X)               # for real scoring, do this inside the Pipeline
# saga is the only solver supporting elasticnet; C = 1/lambda (opposite of alpha in Lasso/ElasticNet).
enet = LogisticRegressionCV(penalty='elasticnet', solver='saga',
                            l1_ratios=[0.1, 0.5, 0.9], Cs=20, cv=10, max_iter=10000)
enet.fit(X_scaled, y)
selected = X.columns[enet.coef_[0] != 0]
```

## Stability: Are the Selected Features Reproducible?

**Goal:** Distinguish a robust signature from a resampling accident, and report stability alongside accuracy.

**Approach:** Run the selector on many subsamples, count per-feature selection frequency, keep features above a threshold (0.6 is the common default), and compute a chance-corrected stability index. Use the Nogueira 2018 measure (handles variable-size selections, gives a confidence interval); the older Kuncheva index needs equal-size subsets and breaks for LASSO.

```python
import numpy as np
from sklearn.linear_model import LogisticRegression

n_subsample, p = 100, X.shape[1]
counts = np.zeros(p)
subsets = []
for _ in range(n_subsample):
    idx = np.random.choice(len(X), size=len(X) // 2, replace=False)   # n/2 subsampling
    fit = LogisticRegression(penalty='l1', solver='liblinear', C=0.1, max_iter=2000).fit(X.iloc[idx], y.iloc[idx])
    mask = fit.coef_[0] != 0
    counts += mask
    subsets.append(mask.astype(int))

stable = X.columns[counts / n_subsample > 0.6]             # pi_thr=0.6: Meinshausen-Buhlmann default
# Nogueira stability index (chance-corrected; 1 = identical selections, ~0 = random):
Z = np.array(subsets); pbar = Z.mean(axis=0); k = Z.sum(axis=1)
stability = 1 - (Z.var(axis=0, ddof=1).mean()) / ((k.mean() / p) * (1 - k.mean() / p))
print(f'{len(stable)} stable features; Nogueira stability = {stability:.2f}')
```

## Per-Method Failure Modes

### Interpreting minimal-optimal membership as biology
- **Trigger:** Reporting "LASSO selected gene X but not its co-expressed partner Y" as a biological finding.
- **Mechanism:** L1 geometry keeps one vertex of a correlated group arbitrarily; the choice flips across resamples.
- **Symptom:** Selected genes change completely on a different train/test split though accuracy is stable.
- **Fix:** Use elastic net (grouping effect) or report selection *frequencies*; never read membership as importance ordering.

### Selection-before-CV leakage
- **Trigger:** Pick top-k features on all samples, then cross-validate the classifier on those features.
- **Mechanism:** The held-out folds informed which genes were kept; selection is the dominant overfitting capacity in p>>n.
- **Symptom:** Near-perfect CV accuracy, even reproducible on label-permuted (null) data; collapse on an external cohort.
- **Fix:** Selection lives inside the CV fold (Pipeline); estimate by nested CV (machine-learning/model-validation).

### Significance against the wrong null
- **Trigger:** Concluding a signature is real because it significantly predicts outcome.
- **Mechanism:** Random gene sets clear that bar; the transcriptome's proliferation axis is captured by almost any large set (Venet 2011).
- **Symptom:** The signature does not beat a size-matched random signature or a proliferation meta-gene in independent data.
- **Fix:** Benchmark against random-signature and proliferation-meta-gene nulls; require added value over clinical covariates in an *independent* cohort.

### Winner's curse / inflated effect sizes
- **Trigger:** Estimating effect sizes or AUC on the same data used to select features.
- **Mechanism:** Selected features are disproportionately those whose noise inflated their apparent effect (Goring 2001); the inflation can be near-total for small true effects.
- **Symptom:** Discovery AUC much higher than replication; replication is under-powered because it was sized to the inflated effect.
- **Fix:** Estimate effects on an independent split (cross-fitting / data-splitting); size replication for the shrunken effect.

### Pseudoreplication in single-cell selection
- **Trigger:** Treating thousands of cells from a few donors as independent samples.
- **Mechanism:** Cells within a donor are correlated; the effective n is the number of donors.
- **Symptom:** Grossly inflated significance and false discoveries.
- **Fix:** Pseudobulk per donor, select at the donor level (Squair 2021); confront the small true n.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Boruta keeps 200 genes, LASSO keeps 12 | All-relevant vs minimal-optimal answering different questions | Both can be right; pick by goal, do not "average" them |
| A list barely overlaps a published signature | Many disjoint equally-predictive lists exist (Ein-Dor 2005) | Expected, not a contradiction; compare *performance* and stability, not membership |
| High accuracy, low stability index | Resampling accident exploiting a dominant axis | Distrust the specific genes; prefer the lower-accuracy higher-stability candidate |
| FDR-clean list still fails to replicate | FDR controls testing, not selection stability | They are orthogonal; add stability + independent validation |

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Samples for a *stable* gene list ~ thousands | Ein-Dor 2006 | Small effects need large n for reproducible membership (accuracy needs far fewer) |
| Selection inside every CV fold; nested CV for tuning | Ambroise 2002; Simon 2003 | Selection outside CV gives ~0% error on noise |
| Stability threshold pi_thr ~ 0.6-0.9 | Meinshausen-Buhlmann 2010 | Selection-frequency cutoff; tune to false-positive cost |
| Random-signature null | Venet 2011 | Benchmark against size-matched random sets + proliferation meta-gene |
| Single-cell unit = donor (pseudobulk) | Squair 2021 | Cells are pseudoreplicates |
| Biomarker clinical translation rate <1% | Kern 2012 | Sets expectations; failures follow a foreseeable taxonomy |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| BorutaPy raises on `np.float`/pandas input | Newer numpy removed aliases; needs arrays | Pass `X.values`, `y.values`; pin numpy or use a fork |
| Regularization strength backwards | `C=1/lambda` (logistic) vs `alpha` (Lasso/ElasticNet) are opposite conventions | Verify which API; small C = strong shrinkage |
| `elasticnet` penalty errors | Only `solver='saga'` supports it | Set `solver='saga'`, pass `l1_ratio(s)` |
| `mrmr_classif` returns wrong type | Pandas backend needs a DataFrame X and Series y | Pass `X` DataFrame, `y=pd.Series(y)`; K must still be chosen |
| glmnet signature unstable across runs (R) | Used `lambda.min` | Use `lambda.1se` for a sparser, more reproducible set |

## References

- Tibshirani R. 1996. Regression shrinkage and selection via the lasso. *J R Stat Soc B* 58:267-288.
- Goring HHH, Terwilliger JD, Blangero J. 2001. Large upward bias in estimation of locus-specific effects from genomewide scans. *Am J Hum Genet* 69:1357-1369.
- Ambroise C, McLachlan GJ. 2002. Selection bias in gene extraction on the basis of microarray gene-expression data. *PNAS* 99:6562-6566.
- Simon R, Radmacher MD, Dobbin K, McShane LM. 2003. Pitfalls in the use of DNA microarray data for diagnostic and prognostic classification. *J Natl Cancer Inst* 95:14-18.
- Ein-Dor L, Kela I, Getz G, Givol D, Domany E. 2005. Outcome signature genes in breast cancer: is there a unique set? *Bioinformatics* 21:171-178.
- Peng H, Long F, Ding C. 2005. Feature selection based on mutual information: criteria of max-dependency, max-relevance, and min-redundancy. *IEEE Trans Pattern Anal Mach Intell* 27:1226-1238.
- Zou H, Hastie T. 2005. Regularization and variable selection via the elastic net. *J R Stat Soc B* 67:301-320.
- Ein-Dor L, Zuk O, Domany E. 2006. Thousands of samples are needed to generate a robust gene list for predicting outcome in cancer. *PNAS* 103:5923-5928.
- Kursa MB, Rudnicki WR. 2010. Feature selection with the Boruta package. *J Stat Softw* 36:1-13.
- Meinshausen N, Buhlmann P. 2010. Stability selection. *J R Stat Soc B* 72:417-473.
- Venet D, Dumont JE, Detours V. 2011. Most random gene expression signatures are significantly associated with breast cancer outcome. *PLoS Comput Biol* 7:e1002240.
- Kern SE. 2012. Why your new cancer biomarker may never work: recurrent patterns and remarkable diversity in biomarker failures. *Cancer Res* 72:6097-6101.
- Shah RD, Samworth RJ. 2013. Variable selection with error control: another look at stability selection. *J R Stat Soc B* 75:55-80.
- Nogueira S, Sechidis K, Brown G. 2018. On the stability of feature selection algorithms. *J Mach Learn Res* 18:1-54.
- Squair JW, Gautier M, Kathe C, et al. 2021. Confronting false discoveries in single-cell differential expression. *Nat Commun* 12:5692.

## Related Skills

- machine-learning/model-validation - Nested CV and leakage-safe estimation of the selected model
- machine-learning/prediction-explanation - Why SHAP rankings are not a validated selection method
- machine-learning/omics-classifiers - Build a classifier from the selected features
- differential-expression/de-results - Pre-filter candidates with differential expression
- experimental-design/multiple-testing - FDR control and why it is orthogonal to selection stability
- experimental-design/power-analysis - Sample size for a stable signature vs an accurate predictor
- pathway-analysis/go-enrichment - Functional enrichment of an all-relevant gene set
<!-- END FILE: machine-learning/biomarker-discovery/SKILL.md -->

## 子目录：machine-learning/model-validation

<!-- BEGIN FILE: machine-learning/model-validation/SKILL.md -->
---
name: bio-machine-learning-model-validation
description: Validates predictive models on omics and biomedical data with nested cross-validation, group/batch/temporal-aware splits, the full data-leakage taxonomy, probability calibration, decision-curve net benefit, optimism correction, sample-size planning, and TRIPOD+AI reporting. Use when estimating model performance honestly, choosing a CV scheme, detecting leakage, or judging whether reported discrimination means the model is actually useful. For feature selection itself see machine-learning/biomarker-discovery; for confirmatory-trial inference see clinical-biostatistics/trial-reporting.
tool_type: python
primary_tool: sklearn
---

## Version Compatibility

Reference examples tested with: numpy 1.26+, scikit-learn 1.4+ (note 1.6/1.8 API changes below).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

scikit-learn drift to watch: `CalibratedClassifierCV(cv='prefit')` was deprecated in 1.6 and removed in 1.8 (it now raises; wrap a fitted model in `sklearn.frozen.FrozenEstimator` instead); `ensemble` default became `'auto'` in 1.6; `method='temperature'` was added in 1.8. If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Model Validation for Biomedical and Omics Data

**"Validate my omics classifier honestly"** -> Keep every data-dependent step inside the resampling loop, never use the same data to both choose and grade, and report calibration and net benefit, not just AUC.
- Nested CV: `GridSearchCV` (inner) wrapped by `cross_val_score` (outer)
- Group/structured: `StratifiedGroupKFold`, `TimeSeriesSplit`
- Calibration: `calibration_curve`, `brier_score_loss`, `CalibratedClassifierCV`

## The Single Most Important Modern Insight -- A Reported Number Is an Honest Estimate Only If Nothing Leaked and Nothing Was Graded on What Was Chosen

A reported performance number is a claim about a data-generating process that will never recur. Almost every inflated result in ML-for-biology traces to one of two root causes: information from the test distribution leaked into model construction, or the same data was used to both choose and grade a decision. A clean train/test split is necessary but nowhere near sufficient -- the leakage has usually already contaminated the test set (a scaler fit on all data, a duplicate patient, ComBat run across the split). Leakage causes a reproducibility crisis across ML-based science (Kapoor 2023), and the bias is largest exactly when the true signal is weakest -- the omics regime.

A second, equally load-bearing insight: discrimination (AUC/C) and calibration (do predicted probabilities match observed frequencies) are *orthogonal*. AUC is invariant to any monotone transform of the score, so it is blind to calibration. For any decision that uses the probability itself, calibration -- not AUC -- is the property that matters, and it is the one routinely ignored (Van Calster 2019, "the Achilles heel").

## Leakage Taxonomy

| Leakage type | How it happens in omics | Symptom | Prevention |
|--------------|-------------------------|---------|------------|
| Preprocessing (most common, most missed) | z-scoring, quantile/library normalization, ComBat/SVA, PCA, kNN/MICE imputation, VST fit on the *full* dataset before splitting | Test performance suspiciously close to train; collapses on external data | Fit every transform inside the CV fold via a `Pipeline` |
| Feature selection (severe special case) | top-k DE genes / highest-variance / univariate filter chosen on all samples, then CV only the classifier | Near-perfect CV from pure noise; unstable selected set | Selection lives in the CV fold (Ambroise 2002) |
| Target / label | a feature is a proxy for or downstream of the outcome (post-diagnosis labs, treatment-derived fields, a collection-site that tracks case/control) | One feature dominates implausibly; fails when removed | Audit temporal/causal admissibility; exclude post-outcome variables |
| Group / patient / replicate | same patient, tumor, organoid, or technical replicate in train and test; `KFold` scatters them | Inflated metrics that vanish under leave-one-group-out | Split by the highest independent unit (`GroupKFold`/`StratifiedGroupKFold`) |
| Batch | batch correlated with outcome and not respected in the split, or ComBat across the train/test boundary | Model discriminates batches not biology; external batch destroys it | Block the split by batch; never run unsupervised correction across the split |
| Temporal | random-splitting time-ordered data; future-period statistics standardize the past | Backtest beats prospective deployment | Time-based split (`TimeSeriesSplit`); never shuffle first |
| Duplicate / homolog | near-identical samples, augmented copies, public-dataset overlap, homologous sequences across the split | Memorization passes as generalization | Deduplicate / cluster-then-split before CV |
| Test-reuse / threshold | repeatedly peeking to pick features, thresholds, "best epoch"; choosing the classification threshold on the test set | Irreproducible SOTA; fragile config | One locked test set; all tuning + thresholds inside nested CV |

## Decision Tree by Scenario

| Scenario / generalization question | Recommended scheme | Why |
|------------------------------------|--------------------|-----|
| "A new sample like training" (and any tuning occurs) | Nested CV: inner `GridSearchCV`, outer `cross_val_score`, Pipeline inside | Tuning and grading on the same CV is optimistic (Cawley-Talbot 2010) |
| "A new patient" (repeated measures) | `GroupKFold`/`StratifiedGroupKFold` by patient/donor | The unit of independence is not the row |
| "A new hospital/site" (transportability) | Leave-one-site-out (internal-external CV) | Approximates external validation |
| "Next year" (time-ordered) | `TimeSeriesSplit` forward-chaining | Random folds leak the future |
| Small n (dozens), need a stable estimate | `RepeatedStratifiedKFold` (5x10) with an interval | A single CV is one high-variance draw |
| Probabilities will drive a decision | Add calibration + decision-curve net benefit | AUC is blind to calibration and utility |
| Final evidence for a clinical model | External/temporal validation + TRIPOD+AI report | Internal CV cannot detect a whole-dataset confound |
| Choosing the features themselves | -> machine-learning/biomarker-discovery | Selection is its own discipline (run it inside the fold) |
| Confirmatory trial inference (HR, p-value) | -> clinical-biostatistics/trial-reporting | Estimand is a treatment effect, not a prediction |

## Nested Cross-Validation

**Goal:** Estimate the performance of the whole procedure (tuning + fit) without optimistic bias.

**Approach:** The inner loop does all tuning, feature selection, and threshold choice; the outer loop grades the winning configuration once on a fold it never touched. The reported number is the aggregate over outer folds; it answers "if I run this pipeline on new data, what do I get?"

```python
from sklearn.model_selection import cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression

pipe = Pipeline([('scaler', StandardScaler()),
                 ('select', SelectKBest(f_classif)),         # re-fit per inner fold -> no leakage
                 ('clf', LogisticRegression(max_iter=5000))])
grid = {'select__k': [10, 50, 200], 'clf__C': [0.01, 0.1, 1]}

inner = StratifiedKFold(5, shuffle=True, random_state=0)
outer = StratifiedKFold(5, shuffle=True, random_state=1)
search = GridSearchCV(pipe, grid, cv=inner, scoring='roc_auc')
scores = cross_val_score(search, X, y, cv=outer, scoring='roc_auc')   # unbiased estimate
print(f'Nested AUC: {scores.mean():.3f} +/- {scores.std():.3f}')
```

Nested CV is needed whenever model selection happens -- even informal "tried three options, kept the best." Flat CV with tuning is a known reviewer red flag (Varma-Simon 2006).

## Group-Aware, Structured, and Small-Sample CV

**Goal:** Match the CV scheme to the real unit of independence and get a variance-aware estimate.

**Approach:** Pass a grouping vector so no group spans folds; for tiny n, repeat stratified k-fold and report the spread, not a bare number. Standard `KFold` assumes i.i.d. rows, which biomedical data almost never satisfy.

```python
from sklearn.model_selection import StratifiedGroupKFold, RepeatedStratifiedKFold, cross_val_score

groups = meta['patient_id'].values                          # multiple samples per patient
gcv = StratifiedGroupKFold(n_splits=5)                      # group-disjoint AND class-balanced
g_auc = cross_val_score(pipe, X, y, cv=gcv, groups=groups, scoring='roc_auc')

rcv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=0)
r_auc = cross_val_score(pipe, X, y, cv=rcv, scoring='roc_auc')   # report an interval
```

Leave-one-out is high-variance and degenerate for ranking metrics (AUC is undefined on a size-1 test fold) -- prefer repeated stratified k-fold. The .632+ bootstrap (Efron-Tibshirani 1997) is a defensible alternative but is optimistic for zero-apparent-error learners; for internal validation of a single fixed model, bootstrap optimism correction is the cleaner choice.

## Calibration vs Discrimination

**Goal:** Verify that predicted probabilities mean what they say, not just that they rank correctly.

**Approach:** Plot a reliability curve, score it with the proper Brier score, and recalibrate on a held-out fold if needed. AUC measures only ranking; the calibration slope (<1 signals overfitting) and the reliability curve localize the failure.

```python
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.metrics import brier_score_loss
from sklearn.frozen import FrozenEstimator                  # sklearn >=1.6

prob_true, prob_pred = calibration_curve(y_test, p_test, n_bins=10, strategy='quantile')
brier = brier_score_loss(y_test, p_test)                    # proper score: calibration + refinement

# Recalibrate a fitted model on a disjoint calibration fold (cv='prefit' deprecated in 1.6, removed in 1.8):
calibrated = CalibratedClassifierCV(FrozenEstimator(fitted_model), method='isotonic')
calibrated.fit(X_cal, y_cal)                                # X_cal disjoint from train and test
```

Calibration cautions: use `strategy='quantile'` (equal-mass bins) under imbalance; do not report a single Expected Calibration Error as ground truth -- equal-width ECE is biased and reports error even for perfectly calibrated models (Roelofs 2022). Use Platt (`method='sigmoid'`) for small calibration sets, isotonic for hundreds-plus points. Recalibrating on the test set is leakage.

**Net benefit / Decision Curve Analysis (Vickers-Elkin 2006):** `net_benefit = TP/n - (FP/n)*(pt/(1-pt))`, where the threshold probability `pt` encodes the relative harm of a false positive. Plot it against treat-all and treat-none references; a model is clinically useful only where it sits above both. DCA requires good calibration to be valid and is the bridge from statistical performance to clinical usefulness -- a model can have high AUC yet zero net benefit at every plausible threshold.

## Metric Selection in Imbalanced Data

| Metric | Use | Trap |
|--------|-----|------|
| Accuracy | Almost never headline it under imbalance | At 5% prevalence, "always negative" scores 95% |
| AUC / C | Discrimination, prevalence-independent | Blind to calibration; not a usefulness measure |
| AUPRC (average precision) | Rare-positive problems | Baseline is the prevalence, not 0.5 -- state it (Saito 2015) |
| Brier / log-loss | When probabilities are used | Proper; not comparable across prevalences without scaling |
| MCC | Balanced single-threshold summary | Still threshold-dependent (Chicco 2020) |
| F1 | Retrieval-style problems | Ignores true negatives; assumes a cost ratio |

The multiple-threshold problem: reporting the *best* F1/accuracy over thresholds is optimistic, and choosing that threshold on the test set is leakage. Pick the operating point on a separate fold (or by net benefit), then report the locked-threshold metric once; prefer threshold-free curves (ROC, PR, calibration) plus one pre-specified operating point.

## External Validation, Optimism, Sample Size, and TRIPOD+AI

- **Internal vs external.** Internal validation (bootstrap optimism correction, repeated/nested CV) estimates reproducibility on new patients from the *same* source; external validation (different time, place, setting) estimates transportability and is the usual point of failure -- calibration degrades first (slope <1, intercept shift). Internal-external CV (leave-one-cluster-out) is the recommendation when multiple cohorts exist (Steyerberg 2001).
- **Optimism and shrinkage.** Apparent performance overstates the future; the gap (optimism) grows with more predictors, more flexibility, smaller n. Remedy with a uniform shrinkage factor (the bootstrap calibration slope) or penalized estimation. A development-data calibration slope <1 *is* the optimism signal.
- **Sample size.** The "10 events per variable" heuristic (Peduzzi 1996) is obsolete; the standard is Riley et al.'s minimum-sample-size framework (2019, Stat Med Parts I-II), which sizes for shrinkage >=0.9 and precise risk estimation (`pmsampsize`). For p>>n omics these formulas are out of regime, which is precisely why heavy penalization + nested validation, not unpenalized multivariable fits, are mandatory.
- **Reporting.** TRIPOD+AI (Collins 2024, *BMJ* 385:e078378) supersedes TRIPOD 2015 and is the 2024+ target for any biomedical predictive-model claim -- it demands data-splitting and leakage controls, calibration (not just discrimination), fairness/subgroup performance, and uncertainty. PROBAST+AI is the companion risk-of-bias appraisal.

## Per-Method Failure Modes

### Preprocessing fit before the split
- **Trigger:** `StandardScaler().fit_transform(X)` (or ComBat, PCA, imputation) on all data, then CV.
- **Mechanism:** The fitted parameters encode the test rows.
- **Symptom:** Test variance tiny; drop on external data.
- **Fix:** Put every transform in the Pipeline so `fit` only sees training folds.

### Threshold or best-of-many chosen on the test set
- **Trigger:** Reporting the best F1 over thresholds, or the best of several CV runs.
- **Mechanism:** Each peek leaks; over many tries the test set becomes a training set.
- **Symptom:** Irreproducible "SOTA"; a fresh test set disappoints.
- **Fix:** Lock one test set, pre-specify metric and threshold rule, choose thresholds on a separate fold.

### SMOTE/resampling to fix imbalance breaks calibration
- **Trigger:** Oversampling/SMOTE for a *risk* model.
- **Mechanism:** Changing training prevalence inflates minority-class probabilities; no AUC gain (van den Goorbergh 2022).
- **Symptom:** Good AUC, badly miscalibrated risks.
- **Fix:** Do not resample for probability models; move the threshold on a calibrated model. If resampled, use `imblearn.pipeline.Pipeline` (train-fold only).

### LOO for a ranking metric
- **Trigger:** Leave-one-out with AUC.
- **Mechanism:** AUC is undefined within a size-1 fold; pooling OOF predictions then scoring once is not equivalent to averaging fold scores for non-decomposable metrics.
- **Symptom:** Unstable or misleading AUC.
- **Fix:** Use repeated stratified k-fold; reserve `cross_val_predict` for visuals, not the headline metric.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Selection/preprocessing inside every fold; nested CV for tuning | Ambroise 2002; Varma-Simon 2006 | Same-data tune-and-grade is optimistic |
| Repeated 5-fold x ~10, report the spread | field standard | A single CV is one high-variance draw at small n |
| Calibration slope ~1; <1 means overfitting | Van Calster 2019 | Basis of shrinkage |
| Sample size from Riley framework (shrinkage >=0.9) | Riley 2019 | "10 EPV" is obsolete |
| Report per TRIPOD+AI | Collins 2024 | 2024+ standard: discrimination + calibration + fairness |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `cv='prefit'` warns or errors | Deprecated in 1.6, removed in 1.8 (now raises) | Wrap the fitted model in `FrozenEstimator` |
| Calibration looks perfect on the test set | Calibrated on the evaluation data | Calibrate on a disjoint fold |
| Scaler/selector fit outside the Pipeline | Preprocessing leakage | Move into the Pipeline passed to `cross_val_score`/`GridSearchCV` |
| `groups=` ignored | Not threaded to the splitter | Pass `groups=` to `cross_validate`/`GridSearchCV.fit` |
| `cross_val_predict` used as the headline AUC | Non-decomposable metric over pooled OOF | Average per-fold scores instead |

## References

- Peduzzi P, Concato J, Kemper E, Holford TR, Feinstein AR. 1996. A simulation study of the number of events per variable in logistic regression analysis. *J Clin Epidemiol* 49:1373-1379.
- Efron B, Tibshirani R. 1997. Improvements on cross-validation: the .632+ bootstrap method. *J Am Stat Assoc* 92:548-560.
- Steyerberg EW, Harrell FE, Borsboom GJ, et al. 2001. Internal validation of predictive models. *J Clin Epidemiol* 54:774-781.
- Ambroise C, McLachlan GJ. 2002. Selection bias in gene extraction on the basis of microarray gene-expression data. *PNAS* 99:6562-6566.
- Vickers AJ, Elkin EB. 2006. Decision curve analysis: a novel method for evaluating prediction models. *Med Decis Making* 26:565-574.
- Varma S, Simon R. 2006. Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics* 7:91.
- Cawley GC, Talbot NLC. 2010. On over-fitting in model selection and subsequent selection bias in performance evaluation. *J Mach Learn Res* 11:2079-2107.
- Saito T, Rehmsmeier M. 2015. The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLoS ONE* 10:e0118432.
- Van Calster B, McLernon DJ, van Smeden M, Wynants L, Steyerberg EW. 2019. Calibration: the Achilles heel of predictive analytics. *BMC Med* 17:230.
- Riley RD, Snell KIE, Ensor J, et al. 2019. Minimum sample size for developing a multivariable prediction model: Parts I-II. *Stat Med* 38:1262-1296.
- Chicco D, Jurman G. 2020. The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation. *BMC Genomics* 21:6.
- Roelofs R, Cain N, Shlens J, Mozer MC. 2022. Mitigating bias in calibration error estimation. *Proc AISTATS* PMLR 151:4036-4054.
- van den Goorbergh R, van Smeden M, Timmerman D, Van Calster B. 2022. The harm of class imbalance corrections for risk prediction models. *J Am Med Inform Assoc* 29:1525-1534.
- Whalen S, Schreiber J, Noble WS, Pollard KS. 2022. Navigating the pitfalls of applying machine learning in genomics. *Nat Rev Genet* 23:169-181.
- Kapoor S, Narayanan A. 2023. Leakage and the reproducibility crisis in machine-learning-based science. *Patterns* 4:100804.
- Collins GS, Moons KGM, Dhiman P, et al. 2024. TRIPOD+AI statement. *BMJ* 385:e078378.

## Related Skills

- machine-learning/biomarker-discovery - Feature selection run inside the CV fold
- machine-learning/omics-classifiers - Model training, calibration directions, and imbalance handling
- machine-learning/survival-analysis - Validation metrics for time-to-event models
- experimental-design/batch-design - Designing out batch-outcome confounding before analysis
- experimental-design/multiple-testing - FDR control for high-dimensional testing
- clinical-biostatistics/trial-reporting - Confirmatory-trial reporting and the prediction-vs-inference boundary
<!-- END FILE: machine-learning/model-validation/SKILL.md -->

## 子目录：machine-learning/omics-classifiers

<!-- BEGIN FILE: machine-learning/omics-classifiers/SKILL.md -->
---
name: bio-machine-learning-omics-classifiers
description: Builds diagnostic and prognostic classifiers on omics feature matrices with regularized logistic regression, random forest, and gradient-boosted trees, handling the p>>n regime, batch shortcut learning, class imbalance, and probability calibration. Use when building a classifier from expression, methylation, or variant data, choosing an algorithm for high-dimensional small-n data, or diagnosing a suspiciously perfect AUC. For unbiased evaluation see machine-learning/model-validation; for feature selection see machine-learning/biomarker-discovery; for time-to-event outcomes see machine-learning/survival-analysis.
tool_type: python
primary_tool: sklearn
---

## Version Compatibility

Reference examples tested with: pandas 2.2+, scikit-learn 1.4+, xgboost 2.0+, imbalanced-learn 0.12+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

Two high-risk drifts: XGBoost moved `early_stopping_rounds` from `fit()` to the constructor (deprecated 1.6, removed from `fit()` in 2.1); scikit-learn deprecated `LogisticRegression(penalty=)` in 1.8 (use `l1_ratio`+`C`) and `CalibratedClassifierCV(cv='prefit')` in 1.6 (use `FrozenEstimator`). If code throws TypeError/FutureWarning, switch to the constructor / `l1_ratio` / `FrozenEstimator` form.

# Classification Models for Omics Data

**"Build a classifier from my expression data"** -> Start with a regularized linear model (often the ceiling in p>>n), check for batch shortcuts, and treat the probability -- not the label -- as the product.
- Linear (often best): `LogisticRegression(penalty='elasticnet', solver='saga')`
- Trees when nonlinear/interaction signal: `RandomForestClassifier`, `xgboost.XGBClassifier`
- Imbalance: `class_weight='balanced'` or threshold tuning, NOT SMOTE for risk models

## The Single Most Important Modern Insight -- In p>>n, Simple Often Wins and the Probability, Not the Label, Is the Product

Omics classification almost always lives in p>>n (thousands of features, tens-to-hundreds of samples). Two counterintuitive consequences follow. First, more flexible is not better: with n in the dozens the variance of a flexible learner dominates, the full covariance is singular so QDA/full-LDA are undefined, and simple diagonal/linear methods match or beat elaborate ones (Dudoit 2002). "Random forest is the obvious choice for expression data" is a myth -- SVM/regularized logistic frequently win on microarray-style problems (Statnikov 2008), and gradient-boosted trees beat deep nets on tabular/omics data (Grinsztajn 2022). Regularization is the load-bearing wall, not a tuning nicety.

Second, in diagnostic/prognostic use the probability is the product, not the label -- which makes calibration, not accuracy, the thing that breaks silently (Van Calster 2019). A model can rank perfectly (AUC 0.9) and still output dishonest risks. And the most common cause of a beautiful AUC is not skill but a batch artifact: if batch correlates with the outcome, the classifier learns the cleaner technical signal and the performance collapses on any independent cohort.

## Algorithm Choice for p>>n

| Model | Wins when | Overfits / fails when | Calibration | Scaling |
|-------|-----------|------------------------|-------------|---------|
| L1 logistic (lasso) | Sparse signal, want a small signature | Correlated features -> unstable selection; >n true signals | Good (proper loss); shrinks toward base rate | Standardize |
| L2 / elastic-net logistic | Many small correlated effects; omics default | Needs C (and l1_ratio) tuning | Good; preferred when calibration matters | Standardize |
| DLDA / nearest-centroid | Tiny n, roughly linear (Dudoit 2002) | Strong interactions; non-Gaussian | Crude; recalibrate | Variance-scaled |
| Linear SVM | High-dim linear separability (Statnikov 2008) | Heavy overlap; needs C | No native probabilities -- Platt-scale `decision_function` | Critical |
| Random forest | Nonlinear/interaction signal; robust baseline | Sparse-linear signal; tiny n; OOB-as-test leakage | Bagged votes bounded away from 0 and 1 | Scale-invariant |
| GBDT (XGBoost/LightGBM) | Best general tabular performer | Tiny n + deep/many rounds; needs early stopping | Log-loss overfitting tends to overconfident extremes | Scale-invariant |
| Tabular deep nets | Very large n; multimodal/transfer | Typical omics n -> loses to GBDT | Variable; often needs temperature scaling | Standardize |

Tree ensembles are often miscalibrated and the direction depends on the learner and loss: classic boosted ensembles push probabilities toward 0.5 (sigmoid distortion; Niculescu-Mizil 2005), bagged forests are comparatively well-calibrated but bound their votes away from 0 and 1, and modern gradient boosting trained to log-loss for many rounds tends to overfit toward overconfident extremes. Check a reliability curve and recalibrate rather than assuming a direction.

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Default omics classifier, want a signature | Elastic-net logistic | Often the ceiling in p>>n; sparse + grouping; well-calibrated |
| Suspected nonlinear/interaction (epistasis, thresholds) | Random forest then XGBoost with early stopping | Trees capture interactions; benchmark vs the linear baseline |
| Probabilities will drive a clinical decision | Linear model + calibration check; recalibrate if needed | Probability is the product; AUC is blind to calibration |
| Class imbalance | `class_weight='balanced'` or threshold tuning; never SMOTE for risk | Resampling destroys calibration for no AUC gain |
| Mixed continuous + categorical features | `ColumnTransformer` (scale continuous, encode categorical) | Different feature types need different handling |
| Missing values, especially below-detection | XGBoost/LightGBM native NaN handling | Missingness is often informative (MNAR) |
| Considering a deep net | Only at very large n or multimodal/raw inputs | GBDT beats deep on engineered omics matrices (Grinsztajn 2022) |
| Need unbiased performance / nested CV / calibration metrics | -> machine-learning/model-validation | Evaluation is its own discipline |
| Time-to-event outcome | -> machine-learning/survival-analysis | Censoring needs survival models, not classifiers |

## Core Workflow: Regularized Logistic First

**Goal:** A calibrated, interpretable baseline that is often the best omics classifier.

**Approach:** Standardize inside a Pipeline and fit elastic-net logistic with cross-validated penalty; the L2 component keeps correlated genes together, the L1 component yields a sparse signature.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegressionCV

# saga supports elasticnet; C = 1/lambda (small C = strong shrinkage). Standardize: the penalty is scale-sensitive.
clf = LogisticRegressionCV(penalty='elasticnet', solver='saga', l1_ratios=[0.1, 0.5, 0.9],
                           Cs=20, cv=5, max_iter=10000, class_weight='balanced')
pipe = Pipeline([('scaler', StandardScaler()), ('clf', clf)])
pipe.fit(X_train, y_train)
```

## Tree Ensembles

**Goal:** Capture nonlinear and interaction structure when the linear baseline leaves signal on the table.

**Approach:** Random forest needs no scaling and is a robust baseline; XGBoost needs a low learning rate, shallow depth, and early stopping (set in the constructor in 2.x) to avoid overfitting tiny n.

```python
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

rf = RandomForestClassifier(n_estimators=500, max_features='sqrt', min_samples_leaf=3,
                            class_weight='balanced', n_jobs=-1, random_state=0)

# XGBoost 2.x: early_stopping_rounds and eval_metric go in the CONSTRUCTOR, not fit().
# scale_pos_weight is omitted on purpose: like resampling, it reweights the prior and
# distorts calibration -- use it only for hard-label problems, not risk models (see Class Imbalance).
xgb = XGBClassifier(n_estimators=2000, learning_rate=0.03, max_depth=4, subsample=0.8,
                    colsample_bytree=0.5, reg_lambda=1.0,
                    early_stopping_rounds=50, eval_metric='aucpr', n_jobs=-1, random_state=0)
xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)])      # NaN handled natively (missing=np.nan)
```

## Detecting Batch Shortcut Learning

**Goal:** Rule out that a high AUC is a batch artifact rather than biology.

**Approach:** Try to predict the batch from the features and use batch-aware splits; if batch is confounded with the outcome, no correction rescues the design (Soneson 2014) -- fix it at the design stage.

```python
from sklearn.model_selection import cross_val_score, StratifiedGroupKFold
from scipy.stats import chi2_contingency
import pandas as pd

# 1. Can the classifier predict the BATCH? If yes, batch is a strong axis and the label model is suspect.
batch_auc = cross_val_score(pipe, X, batch_labels, cv=5, scoring='roc_auc')
print(f'Batch predictability AUC: {batch_auc.mean():.2f} (high = shortcut risk)')

# 2. Is the outcome associated with batch by design?
print('label vs batch p:', chi2_contingency(pd.crosstab(y, batch_labels))[1])

# 3. Leave-one-batch-out is the honest generalization estimate (usually << random-split CV).
gcv = StratifiedGroupKFold(n_splits=5)
honest = cross_val_score(pipe, X, y, cv=gcv, groups=batch_labels, scoring='roc_auc')
print(f'Batch-aware AUC: {honest.mean():.2f}')
```

## Class Imbalance: What Works and What Fails

**Goal:** Handle a rare positive class without destroying the probabilities.

**Approach:** For a risk model, do not resample -- class-weight cautiously or tune the threshold on a validation fold; SMOTE/oversampling change the training prior, inflate minority probabilities, give no AUC gain, and the same sensitivity is recoverable by moving the threshold (van den Goorbergh 2022). When resampling is unavoidable (a hard-label problem), use an `imblearn` Pipeline so only training folds are resampled.

```python
from imblearn.pipeline import Pipeline as ImbPipeline   # NOT sklearn's Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression

# Correct placement: SMOTE's fit_resample runs only during fit on the train fold, no-op on transform.
imb = ImbPipeline([('smote', SMOTE(random_state=0)),
                   ('clf', LogisticRegression(max_iter=5000))])
# Prefer for risk models: no resampling, then pick the operating threshold by cost on a validation fold.
```

## Probability Calibration

**Goal:** Ensure a "0.9" means a 90% risk, not just a high rank.

**Approach:** Tree ensembles are often miscalibrated -- bagged forests bound votes away from 0 and 1, classic boosting is sigmoid-distorted toward 0.5 (Niculescu-Mizil 2005), and log-loss GBDT can overfit to overconfident extremes -- so check a reliability curve and recalibrate on a disjoint fold. Logistic regression optimizes a proper scoring rule and is usually best-calibrated out of the box. See machine-learning/model-validation for reliability curves, Brier, and the full protocol.

```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator               # sklearn >=1.6; cv='prefit' deprecated
calibrated = CalibratedClassifierCV(FrozenEstimator(rf.fit(X_tr, y_tr)), method='isotonic')
calibrated.fit(X_cal, y_cal)                             # X_cal disjoint from train and test
```

## Preprocessing, Scaling, Encoding, Missing Data

- Inside the CV fold (refit per fold via Pipeline): feature selection, scaling, log/VST/quantile normalization, ComBat batch correction, imputation, PCA. Fitting any of these on the full matrix is leakage (machine-learning/model-validation).
- Scale-sensitive: regularized logistic, SVM, kNN, PCA, neural nets -- standardize. Scale-invariant: trees/RF/GBDT.
- Variant features: additive 0/1/2 ordinal for trees/additive logistic; one-hot for non-additive (dominant/recessive) effects; CatBoost-style encoding for high-cardinality (HLA).
- Missing data: XGBoost/LightGBM learn a default split direction for NaN; in omics missingness is often MNAR (below detection limit) and a missingness indicator can carry signal -- naive zero-fill conflates "absent" with "not measured."

## Hyperparameters That Matter

| Model | Tune these | Leave default |
|-------|-----------|---------------|
| Logistic | `C` (log-spaced), `l1_ratio`, `class_weight` | solver (saga for elasticnet) |
| Random forest | `max_features`, `min_samples_leaf`, `max_depth` (cap for tiny n) | `n_estimators` (more is safe; 500-1000) |
| XGBoost | `learning_rate`+`n_estimators`+early stopping, `max_depth` (3-6), `subsample`, `colsample_bytree`, `reg_lambda` | most others |

## Per-Method Failure Modes

### Beautiful AUC that is a batch artifact
- **Trigger:** Cases and controls processed in different batches/sites/times.
- **Mechanism:** The classifier exploits the cleaner technical signal; even nested CV is optimistic, and ComBat cannot rescue a confounded design (Soneson 2014).
- **Symptom:** Near-perfect CV AUC; collapse on an independent cohort; the model predicts batch easily.
- **Fix:** Detect with the batch-prediction check; use leave-one-batch-out; fix at design (balance batches across outcome).

### RF/boosting probabilities trusted as risks
- **Trigger:** Reading `predict_proba` from RF or XGBoost as a calibrated risk.
- **Mechanism:** RF bounds votes away from 0 and 1; classic boosting is sigmoid-distorted (Niculescu-Mizil 2005) and log-loss GBDT can overfit to overconfident extremes.
- **Symptom:** Good AUC, reliability curve far from diagonal.
- **Fix:** Recalibrate on a disjoint fold; or prefer logistic when the probability matters.

### SMOTE-before-split / SMOTE for a risk model
- **Trigger:** Resampling before the CV split, or to "fix" imbalance for a probability model.
- **Mechanism:** Synthetic points derived from test samples leak; resampling inflates minority risk and wrecks calibration (van den Goorbergh 2022; Carriero 2025).
- **Symptom:** Inflated CV performance; predicted risks systematically too high.
- **Fix:** `imblearn` Pipeline (train-fold only); for risk models, do not resample -- tune the threshold.

### OOB error read as an unbiased test estimate
- **Trigger:** Reporting RF out-of-bag error after selecting features on the full data.
- **Mechanism:** Selection leaked; OOB then reflects the contaminated feature set.
- **Symptom:** Optimistic OOB; external collapse.
- **Fix:** Selection inside CV; estimate performance by nested CV.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Try a regularized linear model first | Dudoit 2002; Statnikov 2008 | Simple often beats complex in p>>n |
| GBDT over deep nets for tabular omics | Grinsztajn 2022 | Trees handle uninformative features and non-rotational data |
| Do not resample for risk models | van den Goorbergh 2022; Carriero 2025 | Resampling destroys calibration for no AUC gain |
| XGBoost: low LR + many rounds + early stopping | field standard | Prevents overfitting tiny n |
| Report AUPRC + MCC under imbalance | Saito 2015; Chicco 2020 | Accuracy and ROC-AUC mislead when positives are rare |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| XGBoost `early_stopping_rounds` TypeError in `fit()` | Moved to constructor in 2.x | Pass it (and `eval_metric`) in `XGBClassifier(...)` |
| `penalty='l1'` FutureWarning | Deprecated in sklearn 1.8 | Use `l1_ratio=1` + `C` (1.8+) or keep `penalty` on 1.4-1.7 |
| `elasticnet` solver error | Only saga supports it | `solver='saga'` + `l1_ratio` |
| `CalibratedClassifierCV(cv='prefit')` deprecated | sklearn 1.6 | Wrap in `FrozenEstimator` |
| 95% accuracy but useless model | Imbalance + accuracy metric | Report AUPRC/MCC; check the confusion matrix |

## References

- Dudoit S, Fridlyand J, Speed TP. 2002. Comparison of discrimination methods for the classification of tumors using gene expression data. *J Am Stat Assoc* 97:77-87.
- Chawla NV, Bowyer KW, Hall LO, Kegelmeyer WP. 2002. SMOTE: Synthetic Minority Over-sampling Technique. *J Artif Intell Res* 16:321-357.
- Zou H, Hastie T. 2005. Regularization and variable selection via the elastic net. *J R Stat Soc B* 67:301-320.
- Niculescu-Mizil A, Caruana R. 2005. Predicting good probabilities with supervised learning. *Proc 22nd ICML* 625-632.
- Diaz-Uriarte R, Alvarez de Andres S. 2006. Gene selection and classification of microarray data using random forest. *BMC Bioinformatics* 7:3.
- Statnikov A, Wang L, Aliferis CF. 2008. A comprehensive comparison of random forests and support vector machines for microarray-based cancer classification. *BMC Bioinformatics* 9:319.
- Soneson C, Gerster S, Delorenzi M. 2014. Batch effect confounding leads to strong bias in performance estimates obtained by cross-validation. *PLoS ONE* 9:e100335.
- Saito T, Rehmsmeier M. 2015. The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLoS ONE* 10:e0118432.
- Van Calster B, McLernon DJ, van Smeden M, Wynants L, Steyerberg EW. 2019. Calibration: the Achilles heel of predictive analytics. *BMC Med* 17:230.
- Chicco D, Jurman G. 2020. The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation. *BMC Genomics* 21:6.
- Shwartz-Ziv R, Armon A. 2022. Tabular data: deep learning is not all you need. *Inf Fusion* 81:84-90.
- Grinsztajn L, Oyallon E, Varoquaux G. 2022. Why do tree-based models still outperform deep learning on typical tabular data? *NeurIPS Datasets and Benchmarks*.
- van den Goorbergh R, van Smeden M, Timmerman D, Van Calster B. 2022. The harm of class imbalance corrections for risk prediction models. *J Am Med Inform Assoc* 29:1525-1534.
- Carriero A, Luijken K, de Hond A, Moons KGM, van Calster B, van Smeden M. 2025. The harms of class imbalance corrections for machine learning based prediction models. *Stat Med* 44:e10320.

## Related Skills

- machine-learning/model-validation - Nested CV, calibration, and net benefit for the trained classifier
- machine-learning/biomarker-discovery - Select features before modeling (inside the CV fold)
- machine-learning/prediction-explanation - Interpret the classifier and detect shortcuts with SHAP
- machine-learning/survival-analysis - Time-to-event outcomes that classifiers cannot handle
- differential-expression/batch-correction - Batch correction done design-aware, not across the split
- expression-matrix/normalization - Per-sample normalization that is safe outside the CV fold
<!-- END FILE: machine-learning/omics-classifiers/SKILL.md -->

## 子目录：machine-learning/prediction-explanation

<!-- BEGIN FILE: machine-learning/prediction-explanation/SKILL.md -->
---
name: bio-machine-learning-prediction-explanation
description: Explains ML predictions on omics data with SHAP, LIME, and permutation importance, handling the correlated-feature trap, the conditional-vs-interventional Shapley choice, and the attribution-is-not-causation boundary. Use when interpreting an omics classifier, debugging shortcut/batch learning, or deciding whether an attribution ranking can be trusted as biology. For validated feature selection see machine-learning/biomarker-discovery; explanations are not a selection method.
tool_type: python
primary_tool: shap
---

## Version Compatibility

Reference examples tested with: numpy 1.26+, pandas 2.2+, scikit-learn 1.4+, shap 0.44+, lime 0.2+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

Two shap drifts: the Explanation-object plotting API arrived ~0.36 (new-style `shap.plots.*` take an `Explanation`, legacy `shap.summary_plot`/`dependence_plot` take numpy arrays -- mixing them is the most common runtime error); and `TreeExplainer(..., feature_perturbation='auto')` became the default in 0.47 (was `interventional`), so providing or omitting `data=` silently changes the estimand. Always set `feature_perturbation` explicitly. If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt rather than retrying.

# Model Interpretation for Omics Classifiers

**"Which genes drive my classifier?"** -> Compute attributions, but treat them as a description of the model (not biology), choose the Shapley conditioning deliberately, and aggregate over correlated gene modules before ranking.
- Tree models: `shap.TreeExplainer(model, data=background, feature_perturbation='interventional')`
- Model-agnostic local: `lime.lime_tabular.LimeTabularExplainer`
- Model-reliance screen: `sklearn.inspection.permutation_importance`

## The Single Most Important Modern Insight -- Attributions Explain the Model, Not Biology, and Under Correlation the Algorithm Chooses How to Split Credit

A feature attribution describes the function the model learned on this training distribution; it is not a measurement of biology. A high-SHAP gene can be a pure correlate of a batch, scanner, or library-prep signal the model exploited (DeGrave 2021 is the canonical proof). And because genes co-express in tight modules, the attribution algorithm has genuine freedom in how it splits credit among correlated genes -- the choice of conditioning (`tree_path_dependent`/conditional vs `interventional`/marginal) is not a cosmetic knob, it changes *which* genes get credit, and it is a live methodological controversy with no universally correct answer (Janzing 2020). The operational rule: SHAP/LIME rankings are a debugging and hypothesis-generation tool, never a validated biomarker-selection criterion, and within a co-expression module the ordering is not a finding.

## Method Taxonomy

| Method | What it estimates | Correlated-feature behavior | Cost | Best use |
|--------|-------------------|------------------------------|------|----------|
| TreeSHAP `tree_path_dependent` | Conditional Shapley via tree coverage; approximates E[f \| x_S] | Can give nonzero credit to a feature the model never uses (correlation leak); no background needed | Fast, exact for this estimand | Fast cohort summaries when conditional semantics are acceptable |
| TreeSHAP `interventional` | Marginal/do-operator Shapley; features replaced from a background | Zero credit to unused features even if correlated | Scales with background size (~100-1000) | "What the model actually uses"; most defensible default |
| KernelSHAP | Model-agnostic Shapley via masking; assumes independence | Masking lands off-manifold under correlation; corrupted | Expensive | Last resort for non-tree/non-net models |
| DeepSHAP / GradientSHAP | SHAP for nets via backprop relative to a background | Background-dependent under correlation | Moderate | Neural omics models |
| LinearExplainer | Exact Shapley for linear models | `interventional` vs `correlation_dependent` give different values | Cheap | Penalized linear models; choose the mode |
| LIME | Local sparse linear surrogate on perturbed samples | Off-manifold perturbations; unstable across seeds | Moderate | Eyeballing one local prediction, never global ranking |
| Permutation importance | Drop in score when a feature is shuffled | Shuffling A while correlated B intact zeros BOTH; extrapolates | n_repeats x n_features | Global screen on decorrelated features |
| Conditional permutation (Strobl) | Importance permuting within correlated strata | Fairer among correlated predictors | Higher | RF importance under correlation |

## The Correlated-Feature / Conditional-vs-Marginal Problem (the core)

When Shapley values "drop" a feature subset, they replace it by some distribution, and two incompatible choices exist:

- **Conditional / observational** (`tree_path_dependent`): dropped features drawn from `p(x_dropped | x_S)`. A feature the model *never uses* can still receive nonzero attribution purely because it is correlated with a used feature. So **high SHAP does not mean the model relies on this gene.**
- **Marginal / interventional** (`interventional`): dropped features drawn from the marginal `p(x_dropped)`, i.e. `do(x_dropped = background)`. Features the model genuinely ignores get **exactly zero**, even if correlated. Janzing 2020 argues this is the principled "drop" for attribution; it is why modern SHAP added and (pre-0.47) defaulted to it.

There is no free lunch: every method either extrapolates off-manifold (interventional SHAP, unrestricted permutation -- Hooker 2021's "no free variable importance") or leaks credit through correlation (conditional SHAP). Decide which pathology the question can tolerate, and **aggregate attributions over co-expression modules before ranking** -- "gene A ranked above gene B" within a correlated module is governed by off-manifold value-function behavior, not biology.

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| "Which genes is my model actually keying on" (debug shortcuts) | TreeSHAP `interventional` with a representative background | Gives unused genes zero; reveals true reliance |
| "Which genes are informative about the outcome here" (descriptive) | TreeSHAP `tree_path_dependent`, but never call it model reliance | Conditional semantics answer the descriptive question |
| Ranking importance across correlated genes | Aggregate \|SHAP\| within co-expression clusters first | Within-module order is arbitrary |
| Penalized linear model | `LinearExplainer` (choose `interventional` vs `correlation_dependent`) | Or just read the coefficients -- the model is its own explanation |
| One local prediction, communication | LIME or SHAP waterfall, pinned seed, labeled model-internal | Local surrogate; not global, not reproducible across seeds |
| "I want to pick a biomarker panel" | -> machine-learning/biomarker-discovery | SHAP ranking is not validated selection (no FDR, no replication) |
| High-stakes clinical decision | Prefer an inherently interpretable model | Sparse linear/rule list is exact; avoids the conditional-vs-marginal ambiguity (Rudin 2019) |

## SHAP TreeExplainer (set the conditioning explicitly)

**Goal:** Attribute a tree model's predictions to features with a chosen, stated estimand.

**Approach:** Pass a background and `feature_perturbation='interventional'` for "what the model uses," or omit the background and use `tree_path_dependent` for the conditional/descriptive view. The default `'auto'` flips between them based on whether `data=` is given.

```python
import shap
import numpy as np

# Interventional ('what the model uses'): needs a background (~100-1000 rows).
background = shap.utils.sample(X_train, 200)
explainer = shap.TreeExplainer(model, data=background, feature_perturbation='interventional')
sv = explainer(X_test)                                  # modern Explanation object

# Aggregate over correlated modules BEFORE ranking (clusters = a precomputed gene->module map).
mean_abs = np.abs(sv.values).mean(axis=0)
module_importance = {}
for gene, m in zip(X_test.columns, mean_abs):
    module_importance[clusters[gene]] = module_importance.get(clusters[gene], 0) + m
```

## Attribution Is Not Causation, Mechanism, or a Validated Biomarker

Three layers of "not": (1) **not biology** -- the attribution describes the model, which may have exploited a batch/confounder shortcut; (2) **not causation** -- predictive features conflate direct effects, confounders, mediators, and colliders, and turning attribution into a causal claim needs an explicit causal model SHAP does not contain; (3) **not a validated biomarker** -- taking "top-20 SHAP genes" as a panel is same-data feature selection with no FDR and no replication (winner's curse). The strongest *legitimate* use runs the other way: because attribution exposes what the model used, it is one of the best tools to **catch shortcut/batch learning** -- if top features are batch indicators or depth-tracking housekeeping genes, the model is cheating (DeGrave 2021). That is where attribution is most trustworthy.

## LIME and Explanation Instability

LIME fits a sparse linear surrogate to predictions on perturbed samples around one instance. It is **non-reproducible by construction**: different seeds, different `kernel_width`, and `discretize_continuous=True` (the default) each flip the top features, and the per-feature perturbations land off-manifold for correlated genes. Worse, perturbation-based explainers can be deliberately fooled -- a biased model can be wrapped to look innocuous on the out-of-distribution points LIME/KernelSHAP probe (Slack 2020). Use LIME only to eyeball a single prediction's local logic with a pinned seed, never for global ranking, and never as evidence a model is unbiased.

```python
from lime.lime_tabular import LimeTabularExplainer

explainer = LimeTabularExplainer(X_train.values, feature_names=list(X_train.columns),
                                 mode='classification', discretize_continuous=True,
                                 random_state=0)         # pin the seed; still only conditional stability
exp = explainer.explain_instance(X_test.values[0], model.predict_proba, num_features=10, num_samples=5000)
```

## Background / Baseline Choice (the silent attribution-changer)

SHAP explains the deviation from `E[f(X)]` over the background dataset, so the background defines what "absence of a feature" means and changes every attribution. A tumor sample explained against a tumor-heavy vs a healthy-tissue background yields different "important genes" -- only one matches the scientific question. Use a background of real samples representative of the contrast of interest (a single global mean across a heterogeneous cohort is no real sample). `check_additivity=True` (default) raises when the SHAP values plus the base value do not sum to the model output (a local-accuracy violation) -- often a probability-vs-raw-margin or implementation mismatch; investigate rather than disabling it. Attributions in log-odds (`model_output='raw'`) differ from probability space -- report the scale.

## Permutation Importance Also Breaks Under Correlation

A common error is to "fix" SHAP's correlation problem by switching to permutation importance, but it has the same root pathology: shuffling gene A while correlated gene B is intact lets the model recover the signal through B, so both look unimportant (scikit-learn's own multicollinearity example). Unrestricted permutation also forces the model to predict on points that cannot occur (Hooker 2021). For correlated omics predictors, cluster features and keep one per cluster, or use Strobl's conditional permutation (R `party::cforest`, `varimp(conditional=TRUE)`) -- there is no `conditional=` flag in sklearn's `permutation_importance`. Always evaluate permutation importance on held-out data, not training data.

## Per-Method Failure Modes

### Reading high `tree_path_dependent` SHAP as model reliance
- **Trigger:** Using path-dependent SHAP (no background) and concluding the model depends on a top gene.
- **Mechanism:** Conditional Shapley leaks credit to unused-but-correlated features.
- **Symptom:** A gene the model never splits on ranks high.
- **Fix:** Use `interventional` with a background for reliance questions; state the estimand.

### Within-module ranking treated as a finding
- **Trigger:** Reporting "gene A more important than gene B" for co-expressed A, B.
- **Mechanism:** Shapley fairly splits credit, but the split is governed by off-manifold behavior, not biology.
- **Symptom:** The credit split (and sometimes the order) changes with the conditioning mode or when the other module member is dropped.
- **Fix:** Aggregate \|SHAP\| over co-expression modules before ranking.

### SHAP ranking used as feature selection
- **Trigger:** Taking top-k SHAP genes as a biomarker panel.
- **Mechanism:** Same-data selection with no FDR/replication; winner's curse.
- **Symptom:** The panel fails to replicate in an independent cohort.
- **Fix:** Generate hypotheses with SHAP, validate with biomarker-discovery + independent data.

### LIME/KernelSHAP global aggregates trusted
- **Trigger:** Averaging LIME or KernelSHAP across samples for a global ranking.
- **Mechanism:** Seed/kernel instability + off-manifold perturbation; adversarially foolable (Slack 2020).
- **Symptom:** Ranking changes across runs.
- **Fix:** Use TreeSHAP/LinearExplainer for global; keep LIME local.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Background ~100-1000 rows | shap docs | Interventional/Kernel SHAP cost scales with background; shap warns above ~1000 |
| Set `feature_perturbation` explicitly | shap 0.47 changelog | `'auto'` default silently flips estimand on `data=` presence |
| Aggregate over co-expression modules before ranking | Janzing 2020; Aas 2021 | Within-module order is not identifiable from attributions |
| Validate SHAP-derived genes in independent cohorts | Rudin 2019 | Attribution rankings are model-internal, not replicated associations |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `shap.plots.beeswarm` errors on a numpy array | Explanation-object API since ~0.36 | Pass `explainer(X)` (Explanation); use legacy `summary_plot` for arrays |
| Attribution estimand changed silently | `feature_perturbation='auto'` (0.47+) | Set `'interventional'` or `'tree_path_dependent'` explicitly |
| `check_additivity` raises | SHAP values + base do not sum to output (local-accuracy) | Fix the config (raw vs probability); do not just disable |
| `interventional` errors | No `data=` background supplied | Provide a background sample |
| Permutation importance zeros real features | Correlation dilution | Cluster features or use conditional permutation |

## References

- Ribeiro MT, Singh S, Guestrin C. 2016. "Why Should I Trust You?": Explaining the Predictions of Any Classifier. *Proc KDD* 1135-1144.
- Lundberg SM, Lee S-I. 2017. A unified approach to interpreting model predictions. *Adv Neural Inf Process Syst* 30:4765-4774.
- Strobl C, Boulesteix A-L, Kneib T, Augustin T, Zeileis A. 2008. Conditional variable importance for random forests. *BMC Bioinformatics* 9:307.
- Rudin C. 2019. Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nat Mach Intell* 1:206-215.
- Lundberg SM, Erion G, Chen H, et al. 2020. From local explanations to global understanding with explainable AI for trees. *Nat Mach Intell* 2:56-67.
- Janzing D, Minorics L, Blobaum P. 2020. Feature relevance quantification in explainable AI: a causal problem. *Proc AISTATS* PMLR 108:2907-2916.
- Kumar IE, Venkatasubramanian S, Scheidegger C, Friedler S. 2020. Problems with Shapley-value-based explanations as feature importance measures. *Proc ICML* PMLR 119:5491-5500.
- Slack D, Hilgard S, Jia E, Singh S, Lakkaraju H. 2020. Fooling LIME and SHAP: adversarial attacks on post hoc explanation methods. *Proc AIES*.
- Aas K, Jullum M, Loland A. 2021. Explaining individual predictions when features are dependent: more accurate approximations to Shapley values. *Artif Intell* 298:103502.
- DeGrave AJ, Janizek JD, Lee S-I. 2021. AI for radiographic COVID-19 detection selects shortcuts over signal. *Nat Mach Intell* 3:610-619.
- Hooker G, Mentch L, Zhou S. 2021. Unrestricted permutation forces extrapolation: variable importance requires at least one more model. *Stat Comput* 31:82.

## Related Skills

- machine-learning/omics-classifiers - Train the model being explained; debug batch shortcuts
- machine-learning/biomarker-discovery - Validated feature selection (SHAP ranking is not selection)
- machine-learning/model-validation - Confirm the model generalizes before interpreting it
- data-visualization/heatmaps-clustering - Visualize module-aggregated attributions
<!-- END FILE: machine-learning/prediction-explanation/SKILL.md -->

## 子目录：machine-learning/survival-analysis

<!-- BEGIN FILE: machine-learning/survival-analysis/SKILL.md -->
---
name: bio-machine-learning-survival-analysis
description: Builds and validates predictive time-to-event models on clinical and omics data with penalized Cox, random survival forests, gradient-boosted and deep survival models, and prediction-grade evaluation (Uno's C, time-dependent AUC, integrated Brier, calibration, competing risks). Use when building an individualized risk predictor or prognostic omics signature, choosing a survival model, or evaluating one beyond the C-index. For Kaplan-Meier, log-rank, and classical Cox hazard-ratio inference in a trial see clinical-biostatistics/survival-analysis.
tool_type: python
primary_tool: scikit-survival
---

## Version Compatibility

Reference examples tested with: scikit-survival 0.22+, lifelines 0.30+, numpy 1.26+, pandas 2.2+ (pycox 0.3+ for deep models).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

scikit-survival requires the target `y` to be a structured array with a boolean event field and a float time field; its IPCW metrics need the *training* `y` first. lifelines `concordance_index` expects higher-score = longer-survival (negate the partial hazard). If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Predictive Survival Modeling

**"Build a validated risk model from time-to-event data"** -> Fit a penalized Cox or ensemble survival model, then evaluate with censoring-robust discrimination AND calibration, not the C-index alone.
- Penalized Cox / RSF / boosting: `sksurv.linear_model.CoxnetSurvivalAnalysis`, `sksurv.ensemble.RandomSurvivalForest`
- Evaluation: `concordance_index_ipcw`, `cumulative_dynamic_auc`, `integrated_brier_score`
- Deep survival (large n): `pycox` DeepSurv / DeepHit

## The Single Most Important Modern Insight -- C-Index Only Is the Cardinal Sin

The C-index is necessary but radically insufficient, for three reasons most papers miss. It is **censoring-distribution-dependent**: Harrell's C is biased upward under heavy censoring and gives different values on cohorts that differ only in follow-up -- report Uno's IPCW C with an explicit truncation tau instead (Uno 2011). It is **invariant to any monotone transform of the risk score**, so a model can have an excellent C and be wildly miscalibrated and clinically harmful -- C measures ranking, not the correctness of the predicted probabilities. And it is **insensitive**: adding a genuinely useful marker barely moves it, which is exactly why reclassification metrics (NRI/IDI) were invented. Decision-grade evaluation is Uno's C(tau) + time-dependent AUC(t) + integrated Brier vs a Kaplan-Meier baseline + calibration curves, all on honestly held-out or external data.

## ML-vs-Confirmatory Scope Boundary

Two survival cultures, two skills; mixing them is the most common authoring error. Resolve every overlap by one question: *is the goal to estimate and test a treatment effect in a (pre-specified) study, or to build and validate a risk-prediction model?*

| This skill (machine-learning) -- prediction | clinical-biostatistics/survival-analysis -- inference |
|---------------------------------------------|--------------------------------------------------------|
| Estimand is an individualized risk (survival curve, risk score, CIF) | Estimand is a treatment effect (hazard ratio with CI, p-value) |
| Penalized Cox, RSF, boosting, DeepSurv/DeepHit | Kaplan-Meier, log-rank, classical low-dimensional Cox |
| p>>n omics signatures; feature selection inside the resampling loop | Pre-specified analysis plan, FWER control, regulated trial |
| Judged by out-of-sample prediction (Uno's C, IBS, calibration) | Judged by validity of the HR and PH diagnostics (`cox.zph`) |
| PH is an assumption to relax (RSF/DeepHit do not assume it) | PH is a hypothesis whose violation invalidates the reported HR |

PH concepts, censoring definitions, and the Cox partial likelihood are foundational to both -- stated in clinical-biostatistics and referenced here. This skill's value begins at "I want a validated predictor."

## Model Taxonomy

| Model | Assumes PH? | Handles p>>n? | Competing risks? | Best when |
|-------|-------------|----------------|-------------------|-----------|
| Penalized Cox (elastic-net, coxnet) | Yes | Yes -- the omics workhorse; elastic-net handles correlated genes | Cause-specific by recoding | Sparse, interpretable, reproducible risk score; the default |
| Random Survival Forest | No | Yes (tune mtry/nodesize) | Yes (per-cause CIF) | Nonlinear/interaction effects, non-PH, moderate n |
| Gradient-boosted survival | Componentwise: yes (sparse); tree base: no | Yes (componentwise selects) | Via cause-specific | Boosting accuracy + sparsity, or relaxing PH with trees |
| Survival SVM | No (optimizes concordance) | Yes (kernel) | No | Pure ranking goals; gives a score, not a survival function |
| DeepSurv (pycox CoxPH) | Yes (NN replaces the linear predictor) | Needs large n | No | Large n, nonlinear main effects, PH plausible |
| DeepHit | No (discrete-time PMF) | Needs large n | Yes -- purpose-built | Large n + competing risks + non-PH |
| Cox-Time | No (time-dependent NN) | Needs large n | Discrete-hazard extensions | Large n, non-PH, flexible survival function |

Load-bearing empirical fact: on typical clinical-omics n, **penalized Cox and RSF are very hard to beat**; deep survival models usually only pull ahead at large n and/or with genuine non-PH or competing-risk structure. Start with elastic-net Cox and RSF baselines; escalate to deep models only if they demonstrably beat those on a held-out set.

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Prognostic omics signature, p>>n | Elastic-net Cox (coxnet), selection inside nested CV | Sparse + correlated-gene grouping; the workhorse |
| Nonlinear/interaction effects, non-PH suspected | Random survival forest | Assumes no PH; captures interactions |
| Large n, suspected nonlinear main effects | DeepSurv, benchmarked against coxnet/RSF | Deep only earns its keep at large n |
| Competing events (death from other causes) | Fine-Gray (CIF) or DeepHit; report cause-specific too | 1-KM overestimates incidence; sHR is not the rate effect |
| Dynamic prediction with updating biomarkers | Landmarking | Internal time-varying covariates cannot be plugged into the future |
| Evaluating any survival model | Uno's C(tau) + AUC(t) + IBS-vs-KM + calibration | C-index alone is insufficient |
| KM curve, log-rank, or a trial hazard ratio | -> clinical-biostatistics/survival-analysis | Confirmatory inference, not prediction |
| Selecting the prognostic genes | -> machine-learning/biomarker-discovery (same irreproducibility) | Selection is its own discipline, inside the loop |

## Fitting Predictive Survival Models

**Goal:** Fit a penalized Cox and an RSF baseline with the correct target format.

**Approach:** Build the structured `y` (boolean event, float time), fit coxnet with an elastic-net mix and a baseline model for survival functions, and an RSF for nonlinear structure.

```python
from sksurv.util import Surv
from sksurv.linear_model import CoxnetSurvivalAnalysis
from sksurv.ensemble import RandomSurvivalForest

# event MUST be bool, time float. Field order in from_arrays is (event, time).
y = Surv.from_arrays(event=df['status'].astype(bool), time=df['time'].astype(float))

# Elastic-net Cox: l1_ratio in (0,1]; fit_baseline_model=True enables predict_survival_function.
coxnet = CoxnetSurvivalAnalysis(l1_ratio=0.9, alpha_min_ratio=0.01, fit_baseline_model=True)
coxnet.fit(X_train, y_train)

rsf = RandomSurvivalForest(n_estimators=500, min_samples_leaf=15, max_features='sqrt', n_jobs=-1)
rsf.fit(X_train, y_train)
risk = coxnet.predict(X_test)              # a risk score (higher = higher risk), NOT a probability
```

## Prediction-Grade Evaluation

**Goal:** Report discrimination AND calibration on out-of-sample data, not the C-index alone.

**Approach:** Use Uno's IPCW C (truncated at tau), time-dependent AUC over a horizon grid, integrated Brier vs the KM baseline, and a calibration check at clinical horizons. IPCW metrics take the *training* `y` first to estimate the censoring distribution.

```python
import numpy as np
from sksurv.metrics import concordance_index_ipcw, cumulative_dynamic_auc, integrated_brier_score

c_uno = concordance_index_ipcw(y_train, y_test, risk, tau=t_horizon)[0]      # censoring-robust

times = np.percentile(y_test['time'][y_test['event']], np.linspace(10, 80, 15))   # inside follow-up
auc_t, mean_auc = cumulative_dynamic_auc(y_train, y_test, risk, times)

surv_fns = coxnet.predict_survival_function(X_test)              # needs fit_baseline_model=True
surv_prob = np.vstack([[fn(t) for t in times] for fn in surv_fns])
ibs = integrated_brier_score(y_train, y_test, surv_prob, times)  # compare against the KM-only IBS
print(f"Uno C: {c_uno:.3f}  mean AUC(t): {mean_auc:.3f}  IBS: {ibs:.3f}")
```

Calibration (the most decision-relevant, most-ignored axis): at a clinical horizon, plot predicted P(event by t) against the observed event probability (KM within risk groups, or a smooth calibration curve), and summarize with ICI/E50/E90 (Austin 2020) -- never Hosmer-Lemeshow. Calibration is what usually breaks on external validation even when discrimination is preserved.

## Competing Risks

A competing event precludes the event of interest (death from another cause precludes cause-specific death). Treating competing events as ordinary censoring is wrong: **Kaplan-Meier overestimates cumulative incidence** (1-KM >= the cumulative incidence function), so report the CIF (Aalen-Johansen), not 1-KM. Two hazards answer two questions: the **cause-specific hazard** (Cox censoring competing events) is the etiologic rate; the **Fine-Gray subdistribution hazard** maps to the CIF and is the prognostic/absolute-risk target -- but a Fine-Gray sHR is NOT the cause-specific HR and not an effect on the event rate (a covariate can raise a CIF purely by lowering the competing hazard). Since this skill is the prediction regime, the CIF is usually the target; report both models for a complete picture. DeepHit is purpose-built for competing risks at large n; evaluate with competing-risks-aware concordance (Wolbers 2009) and CIF-based Brier.

## Censoring, Immortal Time, and Landmarking

- **Non-informative censoring** is assumed by the Cox likelihood, KM, and all IPCW metrics: censored subjects must be representative of those still at risk. If sicker patients drop out (informative censoring), survival is overestimated and IPCW does not fix it with a misspecified censoring model. Administrative censoring is the benign case; informative censoring is generally untestable and needs sensitivity analysis. Truncate IPCW metrics at tau because tail weights explode.
- **Immortal time bias** -- defining a group by a post-baseline event ("patients who received treatment") manufactures a survival advantage from guaranteed event-free time (Levesque 2010). Endemic in EHR/omics; fix with time-varying exposure, landmarking, or target-trial emulation.
- **Landmarking** (van Houwelingen 2007) -- internal time-varying covariates (a biomarker that changes with disease) cannot be plugged into the future; pick a landmark time, restrict to those still event-free, use covariate values as of the landmark, and predict forward. It is the robust route to honest dynamic prediction.

## High-Dimensional Penalized Cox and Validation

In p>>n, elastic-net Cox beats LASSO for stability with correlated genes (LASSO arbitrarily keeps one of a correlated group). The same irreproducibility as biomarker discovery applies: different cohorts select near-disjoint gene sets at similar performance, so the deliverable is the *prediction*, not the gene list. Feature selection and tuning MUST live inside the resampling loop -- nested CV with survival metrics (Uno's C, IBS) as the objective; selecting genes on the full data then CV-ing the final model is leakage producing grossly optimistic signatures. Optimism-correct internal validation via Harrell's bootstrap, validate externally, and report per TRIPOD+AI (Collins 2024).

## Per-Method Failure Modes

### Reporting only the C-index
- **Trigger:** Summarizing a survival model by Harrell's C alone.
- **Mechanism:** C is censoring-dependent, monotone-invariant (blind to calibration), and insensitive.
- **Symptom:** Great C, badly miscalibrated absolute risks; ranking-equivalent models look identical.
- **Fix:** Uno's C(tau) + AUC(t) + IBS-vs-KM + calibration curves on out-of-sample data.

### Kaplan-Meier under competing risks
- **Trigger:** Using 1-KM for incidence when a competing event exists.
- **Mechanism:** 1-KM assumes competing-event subjects could still have the event; they cannot.
- **Symptom:** Incidence overestimated; sums across causes exceed 1.
- **Fix:** Report the CIF (Aalen-Johansen); use cause-specific and Fine-Gray models.

### Misverbalizing a Fine-Gray coefficient
- **Trigger:** Saying a Fine-Gray sHR "increases the rate of the event."
- **Mechanism:** The subdistribution hazard maps to cumulative incidence, not the event rate.
- **Symptom:** Causal/etiologic claims from a prognostic model.
- **Fix:** State it as an effect on *cumulative incidence*; report cause-specific too.

### Immortal time bias
- **Trigger:** Grouping subjects by a post-baseline event.
- **Mechanism:** Guaranteed event-free time is attributed to the exposed group.
- **Symptom:** Spectacular development performance, external collapse.
- **Fix:** Time-varying exposure, landmarking, or target-trial emulation.

### Selection-before-CV in a signature
- **Trigger:** Selecting genes on all data, then CV-ing the final Cox model.
- **Mechanism:** Held-out folds informed selection (the dominant overfitting capacity in p>>n).
- **Symptom:** Optimistic, irreproducible signature.
- **Fix:** Selection inside nested CV with survival metrics; elastic net for stability.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Report Uno's C with explicit tau | Uno 2011 | Harrell's C is censoring-dependent and biased upward |
| Evaluate beyond C: AUC(t), IBS-vs-KM, calibration | Graf 1999; Austin 2020 | C is monotone-invariant and insensitive |
| CIF (not 1-KM) under competing risks | Putter 2007 | 1-KM overestimates incidence |
| Selection inside nested CV with survival metrics | field standard | Selection-before-CV leaks in p>>n |
| Start with penalized Cox / RSF baselines | neutral benchmarks | Deep models rarely beat them at clinical n |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| sksurv crash / silent misbehavior on `y` | y not a structured (bool event, float time) array | Use `Surv.from_arrays(event=..bool, time=..float)` |
| IPCW metric wrong | Training `y` not passed first | `concordance_index_ipcw(y_train, y_test, risk, tau=)` |
| `predict_survival_function` errors | coxnet without baseline | `CoxnetSurvivalAnalysis(fit_baseline_model=True)` |
| lifelines C reported as 1-C | partial hazard not negated | `concordance_index(time, -predict_partial_hazard(df), event)` |
| pycox survival nonsense | baseline hazard not computed | `model.compute_baseline_hazards()` before `predict_surv_df` |
| `times` for AUC/IBS out of range | beyond largest uncensored test time | Clip `times` to the observed follow-up |

## References

- Harrell FE, Lee KL, Mark DB. 1996. Multivariable prognostic models. *Stat Med* 15:361-387.
- Graf E, Schmoor C, Sauerbrei W, Schumacher M. 1999. Assessment and comparison of prognostic classification schemes for survival data. *Stat Med* 18:2529-2545.
- Fine JP, Gray RJ. 1999. A proportional hazards model for the subdistribution of a competing risk. *J Am Stat Assoc* 94:496-509.
- Heagerty PJ, Zheng Y. 2005. Survival model predictive accuracy and ROC curves. *Biometrics* 61:92-105.
- Putter H, Fiocco M, Geskus RB. 2007. Tutorial in biostatistics: competing risks and multi-state models. *Stat Med* 26:2389-2430.
- van Houwelingen HC. 2007. Dynamic prediction by landmarking in event history analysis. *Scand J Stat* 34:70-85.
- Ishwaran H, Kogalur UB, Blackstone EH, Lauer MS. 2008. Random survival forests. *Ann Appl Stat* 2:841-860.
- Wolbers M, Koller MT, Witteman JCM, Steyerberg EW. 2009. Prognostic models with competing risks. *Epidemiology* 20:555-561.
- Levesque LE, Hanley JA, Kezouh A, Suissa S. 2010. Problem of immortal time bias in cohort studies. *BMJ* 340:b5087.
- Simon N, Friedman J, Hastie T, Tibshirani R. 2011. Regularization paths for Cox's proportional hazards model via coordinate descent. *J Stat Softw* 39:1-13.
- Uno H, Cai T, Pencina MJ, D'Agostino RB, Wei LJ. 2011. On the C-statistics for evaluating overall adequacy of risk prediction procedures with censored survival data. *Stat Med* 30:1105-1117.
- Katzman JL, Shaham U, Cloninger A, et al. 2018. DeepSurv: personalized treatment recommender system using a Cox proportional hazards deep neural network. *BMC Med Res Methodol* 18:24.
- Lee C, Zame WR, Yoon J, van der Schaar M. 2018. DeepHit: a deep learning approach to survival analysis with competing risks. *Proc AAAI* 32:2314-2321.
- Austin PC, Harrell FE, van Klaveren D. 2020. Graphical calibration curves and the integrated calibration index (ICI) for survival models. *Stat Med* 39:2714-2742.
- Polsterl S. 2020. scikit-survival: a library for time-to-event analysis built on top of scikit-learn. *J Mach Learn Res* 21:1-6.
- Collins GS, Moons KGM, Dhiman P, et al. 2024. TRIPOD+AI statement. *BMJ* 385:e078378.

## Related Skills

- clinical-biostatistics/survival-analysis - Kaplan-Meier, log-rank, classical Cox inference, PH diagnostics for trials
- machine-learning/model-validation - Nested CV, calibration, and optimism correction shared with prediction models
- machine-learning/biomarker-discovery - Selecting prognostic genes inside the resampling loop
- differential-expression/de-results - Pre-filter candidate prognostic genes
- clinical-databases/variant-prioritization - Clinical interpretation of prognostic variants
<!-- END FILE: machine-learning/survival-analysis/SKILL.md -->

<!-- END CATEGORY: machine-learning -->

