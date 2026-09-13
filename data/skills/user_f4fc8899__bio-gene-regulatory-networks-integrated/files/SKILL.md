---
slug: bio-gene-regulatory-networks-integrated
version: 1.0.1
displayName: "基因调控网络 / Gene regulatory networks"
name: bio-gene-regulatory-networks-integrated
summary: "中文：基因调控网络综合技能，整合 6 个相关专题，覆盖基因调控网络：WGCNA共表达网络、pySCENIC regulon、SCENIC+多组学GRN、扰动模拟。 English: Integrated Gene regulatory networks skill covering 6 related topics, including Gene regulatory networks: WGCNA co-expression networks, pySCENIC regulons, SCENIC+ multi-omics GRN, perturbation simulation."
description: "中文：这是一个面向基因调控网络的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：基因调控网络：WGCNA共表达网络、pySCENIC regulon、SCENIC+多组学GRN、扰动模拟。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：CellOracle, DiffCorr, SCENIC+。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Gene regulatory networks, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Gene regulatory networks: WGCNA co-expression networks, pySCENIC regulons, SCENIC+ multi-omics GRN, perturbation simulation. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: CellOracle, DiffCorr, SCENIC+. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# gene-regulatory-networks 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: gene-regulatory-networks -->

## 子目录：gene-regulatory-networks/coexpression-networks

<!-- BEGIN FILE: gene-regulatory-networks/coexpression-networks/SKILL.md -->
---
name: bio-gene-regulatory-networks-coexpression-networks
description: Build weighted gene co-expression networks to identify modules of co-regulated genes, relate them to phenotypes, and find hub genes using WGCNA, hdWGCNA, MEGENA, CEMiTool, and Gaussian graphical models. Covers signed-network choice, soft-threshold selection, module preservation, and the marginal-vs-partial-correlation distinction. Use when finding co-expression modules, identifying hub genes, relating gene networks to clinical or experimental traits, or building single-cell co-expression networks. For directed TF-target inference see scenic-regulons and grn-inference; for condition rewiring see differential-networks.
tool_type: r
primary_tool: WGCNA
---

## Version Compatibility

Reference examples tested with: WGCNA 1.72+, hdWGCNA 0.3+, CEMiTool 1.26+, GENIE3-adjacent GGM via GeneNet 1.2.16+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

WGCNA argument defaults differ by entry point: `pickSoftThreshold()` and `blockwiseModules()` default to `networkType='unsigned'`. The signed-network choice (below) must be set identically at every step or the soft power and modules silently mismatch.

# Co-expression Networks

**"Find co-expression modules and hub genes from my expression data"** -> Build a weighted gene co-expression network, detect modules of co-regulated genes by clustering a topological-overlap dissimilarity, summarize each module by its eigengene, and relate modules to sample traits.
- R: `WGCNA::blockwiseModules()` for network construction + module detection (bulk)
- R: `hdWGCNA` metacell workflow for single-cell expression
- R: `GeneNet`/graphical lasso when direct (not indirect) edges are required

## The Single Most Important Modern Insight -- Co-expression Is Marginal Correlation; Regulation Is Conditional Dependence

A WGCNA edge between genes B and C exists whenever a common driver A correlates with both -- even if B and C never interact. If A regulates B and C, then B and C are conditionally independent given A, yet a co-expression network still draws a strong B-C edge. **A co-expression module is a descriptive object ("these genes vary together"), not a regulatory network, even when its hub is a transcription factor.** The dividing line is marginal vs partial correlation: WGCNA, MEGENA, and CEMiTool measure **marginal** correlation (direct + indirect edges mixed together), while Gaussian graphical models (GeneNet, graphical lasso) estimate **partial** correlation (conditional dependence, i.e. direct edges only). Decide which object the biological question needs before choosing a tool. Causal/regulatory language ("module X is driven by hub TF Y") from a marginal co-expression edge is the single most common over-claim in this domain.

A secondary, load-bearing caveat: the **scale-free topology assumption underpinning soft-threshold selection is empirically weak**. Broido & Clauset 2019 (*Nat Commun* 10:1017) found scale-free structure in only ~4% of ~1000 real networks; Khanin & Wit 2006 (*J Comput Biol* 13:810) found none of 10 biological networks fit a pure power law. The scale-free R^2 >= 0.8 rule is a heuristic for picking the power where the connectivity curve flattens, **not** a hypothesis test confirming the biology is scale-free -- so it does not license "the network is scale-free, therefore hubs are master regulators."

## Co-expression Method Taxonomy

| Method | Edge type | Strength | Use / fails when |
|--------|-----------|----------|------------------|
| WGCNA (Langfelder & Horvath 2008) | marginal, soft-threshold + TOM | de facto standard; eigengenes; preservation | bulk, n>=15-20; fails on raw scRNA-seq |
| hdWGCNA (Morabito 2023) | marginal, on metacells | flattens dropout/zero-inflation | single-cell; fails if metacells overlap (pseudo-replication) |
| MEGENA (Song & Zhang 2015) | marginal, planar filtered network | principled sparsification; multiscale/nested modules | hierarchical biology; nested output breaks WGCNA-style one-module-per-gene code |
| CEMiTool (Russo 2018) | marginal, auto-beta | fast first pass + GSEA/ORA + HTML report | exploratory; S4 object (accessors, not `$`); silently variance-filters genes |
| GeneNet / graphical lasso | **partial** (direct edges) | distinguishes direct from indirect | when "who regulates whom directly" matters; collapses at small n / large p |

Rule of thumb: module discovery and trait association -> WGCNA (signed); single-cell -> hdWGCNA; "is this edge direct or indirect?" -> a Gaussian graphical model.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Bulk RNA-seq, >=15-20 samples, want modules + trait links | WGCNA signed, bicor | stable marginal modules; eigengene-trait correlation |
| Single-cell / sparse counts | hdWGCNA on metacells | naive WGCNA fails on zero-inflation; metacells flatten dropout |
| Need direct vs indirect edges | GeneNet / graphical lasso | partial correlation removes confounded indirect edges |
| Hierarchical / multiscale structure expected | MEGENA | nested modules at multiple resolutions |
| Want directed TF -> target regulons | -> scenic-regulons (single-cell) / grn-inference (bulk) | co-expression is undirected; motif/regression priors add direction |
| Compare networks across conditions | -> differential-networks | rewiring is a different question from module discovery |
| <15 samples | none reliable | correlation estimates too noisy; report this, do not force WGCNA |

## WGCNA: Build a Signed Network

**Goal:** Detect robust co-expression modules from a bulk expression matrix and choose network parameters defensibly.

**Approach:** Use a **signed** network with **biweight midcorrelation (bicor)** so activators and repressors are not merged into one module and outliers are down-weighted; pick the soft power on the SAME network type used for construction; set `maxBlockSize` above the gene count to avoid the block artifact.

```r
library(WGCNA)
options(stringsAsFactors = FALSE)
allowWGCNAThreads()

# WGCNA convention: genes as columns, samples as rows
expr <- t(as.matrix(read.csv('normalized_counts.csv', row.names = 1)))
gsg <- goodSamplesGenes(expr, verbose = 0)
expr <- expr[gsg$goodSamples, gsg$goodGenes]

# Soft power on the SIGNED fit (must match construction below)
powers <- 1:20
sft <- pickSoftThreshold(expr, powerVector = powers, networkType = 'signed', verbose = 0)
soft_power <- sft$powerEstimate            # signed networks usually land near 12

# Signed network, bicor with maxPOutliers to avoid spurious outlier flags at modest n.
# maxBlockSize >= n_genes keeps everything in one block (no cross-block blindness).
net <- blockwiseModules(
    expr, power = soft_power,
    networkType = 'signed', TOMType = 'signed',
    corType = 'bicor', maxPOutliers = 0.05,
    minModuleSize = 30, mergeCutHeight = 0.25, deepSplit = 2,
    maxBlockSize = ncol(expr) + 1,
    numericLabels = TRUE, pamRespectsDendro = FALSE, verbose = 0
)
module_colors <- labels2colors(net$colors)
table(module_colors)                       # large 'grey' fraction = poor fit, not a module
```

## WGCNA: Eigengenes, Hubs, and Trait Relationships

**Goal:** Relate modules to sample traits and identify defensible hub genes.

**Approach:** Summarize each module by its eigengene (first PC), correlate eigengenes with traits, and define hubs by **module membership kME** (signed, bounded, comparable across modules) rather than raw connectivity.

```r
# Recompute eigengenes from the COLOR labels so ME/kME columns are MEturquoise/kMEturquoise.
# (net$MEs uses numeric names ME0/ME1... under numericLabels=TRUE and won't match colors.)
MEs <- orderMEs(moduleEigengenes(expr, module_colors)$eigengenes)
traits <- read.csv('sample_traits.csv', row.names = 1)

module_trait_cor  <- cor(MEs, traits, use = 'p')
module_trait_pval <- corPvalueStudent(module_trait_cor, nrow(expr))

# Hub = high module membership (kME), the WGCNA-preferred definition.
# kME is signed and bounded [-1,1] with a p-value; prefer it over kWithin connectivity.
kME <- signedKME(expr, MEs)
moi <- 'turquoise'
moi_genes <- colnames(expr)[module_colors == moi]
hubs <- sort(kME[moi_genes, paste0('kME', moi)], decreasing = TRUE)
head(hubs, 20)
```

## WGCNA: Module Preservation (the step that makes a module real)

**Goal:** Test whether discovered modules reproduce in an independent dataset -- the scientific claim, not module detection itself.

**Approach:** Run `modulePreservation()` with the discovery network as reference and an independent cohort as test; read Zsummary and medianRank.

```r
# multiData/multiColor hold reference + test expression and the reference module labels
mp <- modulePreservation(
    multiData, multiColor,
    referenceNetworks = 1, nPermutations = 200,
    randomSeed = 1, verbose = 0
)
stats <- mp$preservation$Z$ref.reference$inColumnsAlsoPresentIn.test
stats[, c('moduleSize', 'Zsummary.pres')]
# Zsummary > 10 strong preservation; 2-10 weak/moderate; < 2 no evidence (Langfelder 2011).
# medianRank (mp$preservation$observed) compares modules to each other, size-independent.
```

## hdWGCNA: Single-Cell Co-expression

**Goal:** Build co-expression networks from scRNA-seq without dropout-driven spurious correlation.

**Approach:** Aggregate transcriptionally similar cells into metacells (pseudobulk) to flatten zero-inflation; cap metacell sharing to avoid pseudo-replication; then run standard WGCNA on the metacells.

```r
library(hdWGCNA); library(Seurat)
seurat_obj <- readRDS('clustered.rds')
seurat_obj <- SetupForWGCNA(seurat_obj, gene_select = 'fraction', fraction = 0.05,
                            wgcna_name = 'hdwgcna')

# Build metacells WITHIN cell types; max_shared caps how many cells two metacells share.
# Heavy overlap inflates downstream correlations (pseudo-replication) -- keep it low.
seurat_obj <- MetacellsByGroups(seurat_obj, group.by = 'cell_type',
                                k = 25, max_shared = 10, ident.group = 'cell_type')
seurat_obj <- NormalizeMetacells(seurat_obj)

seurat_obj <- SetDatExpr(seurat_obj, group.by = 'cell_type', group_name = 'all')
seurat_obj <- TestSoftPowers(seurat_obj, networkType = 'signed')
seurat_obj <- ConstructNetwork(seurat_obj, setDatExpr = FALSE, tom_name = 'hdwgcna')
seurat_obj <- ModuleEigengenes(seurat_obj)
seurat_obj <- ModuleConnectivity(seurat_obj)   # kME per module
```

## Direct vs Indirect Edges: Gaussian Graphical Model

**Goal:** Recover edges that survive conditioning on all other genes (direct dependence), not marginal co-expression.

**Approach:** Estimate a shrinkage partial-correlation matrix (n << p safe) and test edges by local FDR.

```r
library(GeneNet)
# expr: samples x genes
pcor   <- ggm.estimate.pcor(expr)              # shrinkage partial correlations
edges  <- network.test.edges(pcor, direct = FALSE, plot = FALSE)
net_gg <- extract.network(edges, method.ggm = 'prob', cutoff.ggm = 0.9)
# Far sparser than WGCNA -- that is the point: indirect edges have been removed.
```

CEMiTool (`cemitool(expr, annot)`) returns an **S4 object** -- use accessors (`module_genes()`, `get_hubs()`, `generate_report()`), never `$` -- and silently variance-filters genes with `filter=TRUE`. MEGENA returns nested modules; do not feed them to one-module-per-gene WGCNA code.

## Per-Method Failure Modes

### Unsigned-by-default network
**Trigger:** leaving `networkType='unsigned'` (the default) then interpreting modules as co-regulated programs. **Mechanism:** unsigned uses |cor|, so a gene and its strong anti-correlate land in the same module. **Symptom:** modules mixing clearly opposing programs (e.g. proliferation and quiescence). **Fix:** use `networkType='signed'` (and `TOMType='signed'`) at pickSoftThreshold AND blockwiseModules.

### Soft power chosen on the wrong network type
**Trigger:** `pickSoftThreshold()` run unsigned, then `blockwiseModules(networkType='signed')`. **Mechanism:** the scale-free fit and chosen power differ by network type. **Symptom:** near-disconnected network or one giant module. **Fix:** set `networkType` identically in both calls (signed power is roughly double unsigned).

### blockwiseModules block artifact
**Trigger:** n_genes > `maxBlockSize` (historical default 5000) with no mention of blocking. **Mechanism:** TOM is computed within each block only; cross-block co-expression is invisible and assignments shift with block size/RAM. **Symptom:** module membership changes when rerun on a different machine. **Fix:** set `maxBlockSize >= n_genes`, or report the block size.

### Naive WGCNA on raw scRNA-seq
**Trigger:** running WGCNA on sparse single-cell counts. **Mechanism:** zero-inflation creates a spike of zero correlations and dropout-driven spurious correlation. **Symptom:** a pathological correlation distribution and unstable modules. **Fix:** use hdWGCNA metacells (and cap `max_shared`).

### Detection without preservation
**Trigger:** reporting modules from one cohort with no replication test. **Mechanism:** any dendrogram can be cut into modules. **Symptom:** modules that do not reproduce in independent data. **Fix:** run `modulePreservation()`; report Zsummary/medianRank.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Samples >= 15 (ideally >= 20) | Horvath/Langfelder WGCNA FAQ | correlation estimates too noisy below 15; modules become random |
| Scale-free R^2 >= 0.8 (0.8-0.9) | WGCNA convention | heuristic for power where connectivity flattens -- NOT proof of scale-free biology |
| Signed soft power ~12 (vs ~6 unsigned) | WGCNA FAQ table | signed adjacency = ((1+cor)/2)^power needs higher power for the same connectivity |
| maxPOutliers = 0.05-0.10 | Langfelder & Horvath 2012 | prevents bicor flagging legitimate observations as outliers at modest n |
| minModuleSize = 30 (default); mergeCutHeight = 0.25 (chosen; default is 0.15) | WGCNA | smaller modules are usually noise; 0.25 merges eigengenes correlating > 0.75 |
| Zsummary > 10 / 2-10 / < 2 | Langfelder 2011 | strong / weak-moderate / no preservation evidence |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| One giant module + large grey | power too low or wrong network type | re-pick power on the correct `networkType` |
| `cemitool` results via `$` return NULL | CEMiTool returns an S4 object | use accessors `module_genes()`, `get_hubs()` |
| hub list dominated by housekeeping genes | hubness tracking mean expression | define hubs by kME, control for expression level |
| top module is the sequencing batch | batch correlates with many genes | correct batch before network construction (-> differential-expression/batch-correction) |
| modules irreproducible across reruns | block artifact | set `maxBlockSize >= n_genes` |

## References

- Langfelder P, Horvath S. 2008. WGCNA: an R package for weighted correlation network analysis. *BMC Bioinformatics* 9:559.
- Langfelder P, Horvath S. 2012. Fast R functions for robust correlations and hierarchical clustering. *J Stat Softw* 46(11):1-17. -- bicor / maxPOutliers.
- Langfelder P, Luo R, Oldham MC, Horvath S. 2011. Is my network module preserved and reproducible? *PLoS Comput Biol* 7(1):e1001057.
- Broido AD, Clauset A. 2019. Scale-free networks are rare. *Nat Commun* 10:1017. -- soft-threshold caveat.
- Khanin R, Wit E. 2006. How scale-free are biological networks? *J Comput Biol* 13(3):810-818.
- Song WM, Zhang B. 2015. Multiscale embedded gene co-expression network analysis (MEGENA). *PLoS Comput Biol* 11(11):e1004574.
- Russo PST, et al. 2018. CEMiTool. *BMC Bioinformatics* 19:56.
- Morabito S, Reese F, Rahimzadeh N, Miyoshi E, Swarup V. 2023. hdWGCNA. *Cell Rep Methods* 3(6):100498.

## Related Skills

- differential-networks - compare co-expression structure between conditions (rewiring)
- scenic-regulons - directed TF regulons from single-cell data (motif-pruned)
- grn-inference - bulk directed GRN inference and TF protein-activity (VIPER)
- differential-expression/batch-correction - remove batch effects before network construction
- single-cell/preprocessing - QC and normalization for single-cell inputs to hdWGCNA
- pathway-analysis/go-enrichment - functional enrichment of co-expression modules
<!-- END FILE: gene-regulatory-networks/coexpression-networks/SKILL.md -->

## 子目录：gene-regulatory-networks/differential-networks

<!-- BEGIN FILE: gene-regulatory-networks/differential-networks/SKILL.md -->
---
name: bio-gene-regulatory-networks-differential-networks
description: Compare gene co-expression and regulatory networks between biological conditions to find rewired relationships using DiffCorr, DiffCoEx, DINGO/iDINGO, and CoDiNA. Covers the differential-connectivity-is-not-differential-expression distinction, the pairwise multiple-testing explosion, marginal vs partial (direct) rewiring, and the underpowered-rewiring failure mode. Use when comparing co-expression networks between disease vs control, treatment, or developmental stages, or finding hub genes that rewire without changing mean expression. For single-condition modules see coexpression-networks; for differential expression of means see differential-expression/de-results.
tool_type: r
primary_tool: DiffCorr
---

## Version Compatibility

Reference examples tested with: DiffCorr 0.4.1+, DINGO/iDINGO 1.0.4+, CoDiNA 1.1.2+; Python path uses scipy 1.12+, statsmodels 0.14+, networkx 3.0+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

In statsmodels, `multipletests()` defaults to method `'hs'` (Holm-Sidak), NOT Benjamini-Hochberg. Always pass `method='fdr_bh'` explicitly for differential-correlation FDR.

# Differential Networks

**"Compare gene co-expression networks between my disease and control groups"** -> Test whether gene-gene relationships differ between two conditions, identifying gained, lost, and reversed edges and the genes that rewire.
- R: `DiffCorr::comp.2.cc.fdr()` (pairwise Fisher z); `DiffCoEx` (module-level); `iDINGO::dingo()` (partial-correlation)
- Python: Fisher z-test with `scipy.stats` + `statsmodels` FDR

## The Single Most Important Modern Insight -- Differential Connectivity Is Not Differential Expression

A gene can have identical mean expression in two conditions yet a completely rewired set of correlation partners -- and that rewiring, not the mean shift, can be the disease signal. The classic demonstration is Hudson, Reverter & Dalrymple 2009 (*PLoS Comput Biol* 5:e1000382): myostatin received the top Regulatory Impact Factor despite **not being differentially expressed**, correctly fingering the gene carrying the causal mutation purely from the change in its correlation wiring to differentially-expressed targets. So differential expression (a shift in means) and differential connectivity (a shift in the correlation structure) are **orthogonal questions**, and the most differentially-connected hub is often not differentially expressed. Three distinct analyses are routinely conflated and must be kept separate: differential **expression** (mean shift), differential **co-expression** (pairwise correlation shift, DiffCorr/DiffCoEx), and differential **connectivity/rewiring** at the conditional-independence level (DINGO).

The dominant practical failure is **statistical power**. The variance of a *difference* of two correlations is large, so rewiring detection needs many samples per group -- far more than differential expression. Worse, pairwise differential-correlation testing has a multiple-testing explosion: p genes produce ~p^2/2 edge tests, so without aggressive FDR (or a module-level method that sidesteps per-edge testing) the results are dominated by false positives. Most "rewired hub" findings in small cohorts are underpowered noise.

## Differential-Network Method Taxonomy

| Method | Citation | Level | Edge type | Note |
|--------|----------|-------|-----------|------|
| DiffCorr | Fukushima 2013 *Gene* | per-edge | marginal | simple Fisher z; p^2/2 tests -> aggressive FDR needed |
| DiffCoEx | Tesson 2010 *BMC Bioinformatics* | module | marginal | WGCNA-based; tests modules, sidesteps per-edge multiplicity |
| DINGO | Ha 2015 *Bioinformatics* | per-edge | **partial** | group-specific GGM; bootstrap differential score (direct rewiring) |
| iDINGO | Class 2018 *Bioinformatics* | per-edge | partial, multi-omics | chain-graph across data types (e.g. miRNA->mRNA->protein) |
| CoDiNA | Gysi 2020 *PLoS ONE* | per-edge | on supplied nets | compares >=2 networks; common/specific/different edge classes |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Two conditions, quick pairwise rewiring | DiffCorr (Fisher z) + strict FDR | simplest; report gained/lost/reversed |
| Want modules that rewire, not edges | DiffCoEx | module-level testing avoids the p^2/2 explosion |
| Need direct (not indirect) rewiring | DINGO/iDINGO | partial correlation removes confounded indirect changes |
| More than two conditions | CoDiNA | n-way comparison with edge classification |
| Multi-omics rewiring | iDINGO | chain-graph respects the biological hierarchy |
| Just want mean-expression changes | -> differential-expression/de-results | that is DE, not rewiring |
| Build the per-condition networks first | -> coexpression-networks | rewiring compares already-built networks |

## DiffCorr: Pairwise Differential Correlation (R)

**Goal:** Find gene pairs whose correlation differs significantly between two conditions.

**Approach:** Fisher z-transform each correlation per condition and test the z-difference with FDR; classify surviving edges as gained, lost, or reversed.

```r
library(DiffCorr)

expr_all <- read.csv('normalized_counts.csv', row.names = 1)        # genes x samples
info <- read.csv('sample_info.csv', row.names = 1)
# Filter to top variable genes first: p^2/2 edge tests make the full matrix intractable.
gene_vars <- apply(expr_all, 1, var)
top <- names(sort(gene_vars, decreasing = TRUE))[1:3000]
d1 <- expr_all[top, info$condition == 'control']
d2 <- expr_all[top, info$condition == 'disease']

# Returns the differential correlations directly (threshold filters exported pairs by lfdr).
# It only writes the file when save = TRUE, so use the returned data.frame. Columns carry
# spaces ('molecule X', 'molecule Y', 'r1', 'r2', 'lfdr (difference)') -- index with [[ ]].
res <- comp.2.cc.fdr(data1 = d1, data2 = d2, threshold = 0.05, save = TRUE,
                     output.file = 'diffcorr.txt')
```

## DINGO: Direct Differential Rewiring (R)

**Goal:** Detect rewiring at the conditional-independence (direct edge) level rather than marginal correlation.

**Approach:** Estimate a group-specific Gaussian graphical model and bootstrap an edge-wise differential score.

```r
library(iDINGO)
# dingo(dat, x, ...): dat = samples x genes; x = the binary group covariate (length n).
fit <- dingo(dat = expr_mat, x = group, B = 100, cores = 8)   # B = bootstrap reps
# fit$diff.score / fit$p.val give edge-wise differential connectivity (direct edges).
```

## Python: Fisher z Differential Network

**Goal:** Compare correlation networks between two conditions in a Python-native workflow.

**Approach:** Compute per-condition correlation matrices, test each pair with Fisher's z, apply BH FDR (explicitly), and classify edges.

```python
import numpy as np, pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

def fisher_z(r1, n1, r2, n2):
    z1, z2 = np.arctanh(np.clip([r1, r2], -0.9999, 0.9999))
    se = np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))
    z = (z1 - z2) / se
    return z, 2 * stats.norm.sf(abs(z))

def differential_network(e1, e2, fdr=0.05):
    genes = e1.columns.tolist()
    n1, n2 = len(e1), len(e2)
    c1, c2 = e1.corr().values, e2.corr().values
    rows = []
    for i in range(len(genes)):
        for j in range(i + 1, len(genes)):
            z, p = fisher_z(c1[i, j], n1, c2[i, j], n2)
            rows.append((genes[i], genes[j], c1[i, j], c2[i, j], z, p))
    df = pd.DataFrame(rows, columns=['g1', 'g2', 'r1', 'r2', 'z', 'p'])
    # statsmodels default is Holm-Sidak ('hs'); BH must be requested explicitly.
    df['padj'] = multipletests(df['p'], method='fdr_bh')[1]
    return df
```

## Per-Method Failure Modes

### Underpowered rewiring claims
**Trigger:** declaring rewired hubs from a small cohort. **Mechanism:** the variance of a correlation difference is large; rewiring needs more samples than DE. **Symptom:** few or no edges survive FDR, or unstable results across resampling. **Fix:** require adequate n per group; treat low-power results as exploratory.

### Pairwise multiple-testing explosion
**Trigger:** testing all gene pairs with weak/no FDR. **Mechanism:** p genes -> ~p^2/2 tests. **Symptom:** thousands of "significant" edges, irreproducible. **Fix:** pre-filter to variable genes, apply strict FDR, or use a module-level method (DiffCoEx).

### Conflating DE with rewiring
**Trigger:** interpreting differentially-connected genes as differentially expressed (or vice versa). **Mechanism:** they are orthogonal. **Symptom:** a rewired hub dismissed because it is not DE. **Fix:** report DE and differential connectivity separately; a non-DE gene can be the key rewired hub.

### Marginal rewiring read as direct
**Trigger:** interpreting a DiffCorr gained edge as a direct regulatory change. **Mechanism:** marginal correlation mixes direct and indirect edges; a changed edge may reflect a shifted common driver. **Symptom:** mechanistic claims from marginal rewiring. **Fix:** use DINGO (partial correlation) when directness matters.

### Holm-Sidak instead of BH
**Trigger:** `multipletests(p)` without `method=`. **Mechanism:** statsmodels defaults to `'hs'`, more conservative than intended. **Symptom:** unexpectedly few hits. **Fix:** pass `method='fdr_bh'`.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| >= 15-20 samples per group | correlation-stability convention | rewiring is lower-powered than DE; small n gives noise |
| Pre-filter to top ~2000-5000 variable genes | practical | bounds the p^2/2 test count |
| BH FDR < 0.05 | standard | controls the false-discovery rate across many edge tests |
| effect-size filter abs(delta r) > 0.3 | convention | avoid reporting trivially different correlations |
| DINGO bootstrap B = 100 | iDINGO default-scale | stabilizes the differential score |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| millions of edge tests / out of memory | full gene matrix | pre-filter to variable genes |
| far fewer hits than expected | statsmodels Holm-Sidak default | use `method='fdr_bh'` |
| rewired hub "should be DE" objection | conflating connectivity with expression | report them as separate, orthogonal results |
| DGCA not installable from CRAN | archived May 2024 | install from GitHub (`andymckenzie/DGCA`) |
| reversed edges look like noise | no effect-size filter | require abs(delta r) above a threshold |

## References

- Hudson NJ, Reverter A, Dalrymple BP. 2009. A differential wiring analysis... correctly identifies the gene containing the causal mutation. *PLoS Comput Biol* 5(5):e1000382.
- de la Fuente A. 2010. From 'differential expression' to 'differential networking'. *Trends Genet* 26(7):326-333.
- Fukushima A. 2013. DiffCorr: analyze and visualize differential correlations in biological networks. *Gene* 518(1):209-214.
- Tesson BM, Breitling R, Jansen RC. 2010. DiffCoEx: differentially coexpressed gene modules. *BMC Bioinformatics* 11:497.
- Ha MJ, Baladandayuthapani V, Do KA. 2015. DINGO: differential network analysis in genomics. *Bioinformatics* 31(21):3413-3420.
- Class CA, Ha MJ, Baladandayuthapani V, Do KA. 2018. iDINGO: integrative differential network analysis in genomics. *Bioinformatics* 34(7):1243-1245.
- Gysi DM, et al. 2020. Co-expression differential network analysis (CoDiNA). *PLoS ONE* 15(10):e0240523.

## Related Skills

- coexpression-networks - build the per-condition co-expression networks being compared
- scenic-regulons - TF regulon activity differences as a complementary rewiring readout
- grn-inference - VIPER differential protein activity between conditions
- differential-expression/de-results - differential expression of means (the orthogonal question)
- temporal-genomics/temporal-grn - time-resolved network change across stages
<!-- END FILE: gene-regulatory-networks/differential-networks/SKILL.md -->

## 子目录：gene-regulatory-networks/grn-inference

<!-- BEGIN FILE: gene-regulatory-networks/grn-inference/SKILL.md -->
---
name: bio-gene-regulatory-networks-grn-inference
description: Infer gene regulatory networks from bulk or general expression data with mutual-information (ARACNe) and tree-ensemble (GENIE3, GRNBoost2) methods, and infer transcription-factor protein activity from regulons with VIPER and msVIPER. Covers the activity-not-edges paradigm, the undirected-association caveat, the DREAM5 wisdom-of-crowds and method-complementarity result, AUPRC-over-AUROC evaluation, and gold-standard incompleteness. Use when inferring a regulatory network from a bulk expression matrix, finding master regulators, or scoring TF activity from a signature. For single-cell motif-pruned regulons see scenic-regulons; for co-expression modules see coexpression-networks.
tool_type: mixed
primary_tool: VIPER
---

## Version Compatibility

Reference examples tested with: VIPER 1.36+ (Bioconductor), GENIE3 1.24+ (Bioconductor), ARACNe-AP (Java, build from source), arboreto 0.1.6+ (Python GRNBoost2).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

GENIE3 expects the expression matrix as genes-in-rows, samples-in-columns (the transpose of the WGCNA convention); a transposed matrix silently produces a meaningless network.

# GRN Inference and TF Activity

**"Infer a gene regulatory network from my bulk expression data and find the master regulators"** -> Reverse-engineer TF -> target edges from an expression matrix, assemble them into regulons, then score the protein activity of each TF from a gene-expression signature.
- R: `GENIE3()` (tree-ensemble) or ARACNe-AP (mutual information) for edges
- R: `viper::aracne2regulon()` -> `msviper()` / `viper()` for TF activity

## The Single Most Important Modern Insight -- Activity, Not Edges: A Regulon Is a Multiplexed Reporter

A GRN inferred from observational expression is, by default, an **undirected statistical association graph**: correlation and mutual information are symmetric and cannot distinguish TF -> target from target -> TF or from a shared upstream driver. Tree-ensemble methods (GENIE3/GRNBoost2) appear directed only because they restrict predictors to a TF list -- that direction is an input assumption, not an inference. Individual inferred edges are therefore unreliable, and benchmarks confirm it (below).

The paradigm that survives this (the Califano-lab lineage: ARACNe -> VIPER) is to **stop trusting individual edges and instead read TF protein activity from the regulon as a whole**. VIPER treats a regulon (a TF and its inferred targets, each carrying a Mode-of-Regulation sign) as a **multiplexed reporter assay**: even if many edges are wrong, the *coordinated* up/down shift of the targets in a signature is a robust estimate of the regulator's activity (Alvarez 2016 *Nat Genet* 48:838). This is why VIPER can identify an active master regulator whose **own mRNA is unchanged** -- because the protein is regulated post-transcriptionally. Master-regulator analysis (MARINa/VIPER) is a fundamentally different computation from "the most-connected node," and edge-level precision matters less than activity inference. The Mode-of-Regulation signs are load-bearing: without them VIPER collapses to a plain enrichment test.

## Method Taxonomy

| Family | Tool | Citation | Mechanism | Structural bias |
|--------|------|----------|-----------|-----------------|
| Mutual information | ARACNe-AP | Lachmann 2016 *Bioinformatics* | MI + data-processing-inequality pruning of indirect edges | good on feed-forward loops; deletes the direct leg of true FFLs |
| Tree ensemble (RF) | GENIE3 | Huynh-Thu 2010 *PLoS ONE* | per-target random-forest variable importance | good on cascades; trades away FFLs |
| Tree ensemble (GBM) | GRNBoost2 | Moerman 2019 *Bioinformatics* | per-target gradient boosting; fast/scalable | as GENIE3; stochastic without a seed |
| Info-theoretic | CLR / MRNET | Faith 2007; Meyer 2007 | MI z-scored against per-gene background / mRMR | suppress hub artifacts |
| TF activity | VIPER / msVIPER | Alvarez 2016 *Nat Genet* | regulon-enrichment (aREA) on a signature | needs a regulon + Mode of Regulation |

DREAM5 (Marbach 2012 *Nat Methods* 9:796): no single method dominates; families make complementary errors, so an **ensemble ("wisdom of crowds") is the most robust**. And methods that excel on synthetic data collapse on real eukaryotic data (yeast was near-random) because TF and target mRNA decorrelate -- synthetic AUPRC does not transfer.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Bulk RNA-seq, want a TF -> target network | GENIE3 or ARACNe-AP | tree-ensemble or MI edge inference |
| Find master regulators of a phenotype | ARACNe regulon -> msVIPER | activity inference is robust to edge errors |
| Score per-sample TF activity for stratification | `viper()` per-sample matrix | turns expression into an activity readout |
| Want robustness / no single best method | ensemble multiple inferences | DREAM5 wisdom-of-crowds |
| Single-cell data with motif resources | -> scenic-regulons | motif pruning adds directness SCENIC-style |
| Just co-expression modules (no direction) | -> coexpression-networks | WGCNA modules, no TF privileging |
| Compare TF activity between conditions | msViper on a 2-group signature | differential activity, not differential edges |

## Edge Inference with GENIE3 (R)

**Goal:** Reverse-engineer a ranked TF -> target network from a bulk expression matrix.

**Approach:** Fit a per-target random forest predicting each gene from candidate regulators (TFs); the regulator's variable importance is the edge weight. Restrict predictors to a TF list to orient edges.

```r
library(GENIE3)

# GENIE3 convention: genes in ROWS, samples in COLUMNS (transpose of WGCNA).
expr <- as.matrix(read.csv('normalized_counts.csv', row.names = 1))
regulators <- readLines('tf_list.txt')                  # candidate TFs only

set.seed(42)                                            # tree ensembles are stochastic
weight_matrix <- GENIE3(expr, regulators = regulators, treeMethod = 'RF',
                        K = 'sqrt', nTrees = 1000, nCores = 8)
link_list <- getLinkList(weight_matrix)                 # ranked edge list (NOT thresholded)
head(link_list)
```

## Edge Inference with ARACNe-AP (Java CLI)

**Goal:** Build a mutual-information network with indirect edges pruned.

**Approach:** ARACNe-AP is a two-phase Java pipeline: compute the MI threshold, run many bootstrap reconstructions, then consolidate them (with data-processing-inequality pruning) into a final network. Running a single bootstrap or skipping consolidation is the classic misuse.

```bash
# Phase 1: MI threshold at a chosen p-value (needs the expression matrix + TF list).
java -Xmx32G -jar aracne.jar -e expr.txt -o out/ --tfs tf_list.txt \
    --pvalue 1E-8 --seed 1 --calculateThreshold

# Phase 2: many bootstraps (vary --seed) -- 100 is conventional.
for s in $(seq 1 100); do
    java -Xmx32G -jar aracne.jar -e expr.txt -o out/ --tfs tf_list.txt \
        --pvalue 1E-8 --seed $s
done

# Phase 3: consolidate bootstraps into the final network (DPI + a Poisson edge-significance
# test with Bonferroni correction across bootstraps).
java -Xmx32G -jar aracne.jar -o out/ --consolidate
```

## TF Activity with VIPER / msVIPER (R)

**Goal:** Infer transcription-factor protein activity from a regulon and an expression signature, and rank master regulators.

**Approach:** Convert an ARACNe network into a regulon object (assigning each target a Mode-of-Regulation sign and likelihood), build a null model by sample permutation, then run msVIPER on a two-group signature (master regulators) or VIPER per sample (activity matrix).

```r
library(viper)

# Build the regulon from the ARACNe network + matched expression (assigns Mode of Regulation).
# ARACNe-AP network.txt has a header + 4 columns (Regulator, Target, MI, p-value); viper's
# '3col' reader wants Regulator/Target/MI with no header, so strip them first (shell):
#   tail -n +2 out/network.txt | cut -f1-3 > net_3col.txt
# ('adj' is the legacy ARACNE adjacency-matrix format, not ARACNe-AP.)
regulon <- aracne2regulon('net_3col.txt', eset, format = '3col')

# msVIPER: master regulators of a two-group contrast.
signature <- rowTtest(eset, pheno = 'group', group1 = 'tumor', group2 = 'normal')
sig_z <- (qnorm(signature$p.value / 2, lower.tail = FALSE) * sign(signature$statistic))[, 1]
nullmodel <- ttestNull(eset, pheno = 'group', group1 = 'tumor', group2 = 'normal', per = 1000)
mra <- msviper(sig_z, regulon, nullmodel)
summary(mra)                                            # top master regulators by NES

# VIPER: a per-sample TF-activity matrix for clustering/stratification.
activity <- viper(eset, regulon, method = 'scale')
```

For single cells or tissues lacking a matched network, `metaVIPER` integrates multiple interactomes; DIGGIT then intersects master regulators with genetic alterations to nominate causal drivers.

## Per-Method Failure Modes

### Fabricated directionality
**Trigger:** presenting an MI/correlation network as a directed causal GRN. **Mechanism:** symmetric measures carry no direction; the TF-list restriction is an assumption. **Symptom:** arrowheads with no perturbation/time/sequence support. **Fix:** state edges are associations; reserve causal claims for perturbation-validated edges.

### Master regulators from edge counts
**Trigger:** calling the most-connected node a master regulator. **Mechanism:** MRA (VIPER) is regulon enrichment in a signature, not node degree. **Symptom:** "hub = driver" with no activity computation. **Fix:** run msVIPER; report NES.

### Skipping ARACNe consolidation
**Trigger:** a single bootstrap, or no `--consolidate`. **Mechanism:** the network is unstabilized and DPI/Bonferroni unapplied. **Symptom:** noisy, non-reproducible edges. **Fix:** run ~100 bootstraps then consolidate.

### Missing Mode of Regulation in VIPER
**Trigger:** a regulon without target signs. **Mechanism:** aREA needs activating/repressing signs so a repressed-target down-shift counts toward activation. **Symptom:** VIPER behaves like a plain enrichment test. **Fix:** build the regulon with `aracne2regulon` (which assigns MoR).

### AUROC-only / synthetic-only validation
**Trigger:** reporting AUROC near 1, or validating only on simulated data. **Mechanism:** with ~0.1-1% true edges AUROC hides near-random AUPRC; synthetic success does not transfer (DREAM5). **Symptom:** no AUPRC, no real-data gold standard. **Fix:** report AUPRC + early precision against an independent gold standard; acknowledge gold-standard incompleteness.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| ARACNe bootstraps ~100 then consolidate | ARACNe-AP workflow | stabilizes edges; DPI + Poisson edge test, Bonferroni-corrected |
| ARACNe MI p-value 1E-8 | ARACNe-AP default-scale | controls edge false positives genome-wide |
| GENIE3 nTrees = 1000, K = 'sqrt' | GENIE3 defaults | variance/runtime trade-off for importances |
| VIPER/msVIPER null permutations ~1000 | VIPER convention | calibrates the NES null distribution |
| Report AUPRC + early precision (not AUROC) | Marbach 2012 / Pratapa 2020 | AUROC misleads under sparse positives |
| Set a seed for GENIE3/GRNBoost2 | reproducibility | tree ensembles are stochastic |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| meaningless GENIE3 network | matrix transposed (samples in rows) | genes in rows, samples in columns |
| ARACNe network unstable across runs | single bootstrap / no consolidate | run ~100 bootstraps then `--consolidate` |
| VIPER acts like plain enrichment | regulon lacks Mode of Regulation | build via `aracne2regulon` |
| top regulator is just highly expressed | using degree/expression as "activity" | use msVIPER NES |
| great synthetic accuracy, fails on real data | over-fit to in-silico benchmark (DREAM5) | validate on real gold standards; report AUPRC |

## References

- Margolin AA, et al. 2006. ARACNE: reconstruction of gene regulatory networks in a mammalian cellular context. *BMC Bioinformatics* 7(Suppl 1):S7.
- Lachmann A, Giorgi FM, Lopez G, Califano A. 2016. ARACNe-AP. *Bioinformatics* 32(14):2233-2235.
- Huynh-Thu VA, et al. 2010. Inferring regulatory networks using tree-based methods (GENIE3). *PLoS ONE* 5(9):e12776.
- Moerman T, et al. 2019. GRNBoost2 and Arboreto. *Bioinformatics* 35(12):2159-2161.
- Faith JJ, et al. 2007. Large-scale mapping and validation of E. coli transcriptional regulation (CLR). *PLoS Biol* 5(1):e8.
- Alvarez MJ, et al. 2016. Network-based inference of protein activity (VIPER). *Nat Genet* 48(8):838-847.
- Marbach D, et al. 2012. Wisdom of crowds for robust gene network inference (DREAM5). *Nat Methods* 9(8):796-804.
- Pratapa A, et al. 2020. Benchmarking single-cell GRN inference (BEELINE). *Nat Methods* 17(2):147-154.

## Related Skills

- scenic-regulons - single-cell regulons with motif-pruning directness
- coexpression-networks - undirected co-expression modules (no TF privileging)
- differential-networks - VIPER differential activity / rewiring between conditions
- multiomics-grn - enhancer-driven directed GRNs from accessibility
- differential-expression/de-results - signatures that feed msVIPER
- single-cell/perturb-seq - interventional validation of inferred regulation
<!-- END FILE: gene-regulatory-networks/grn-inference/SKILL.md -->

## 子目录：gene-regulatory-networks/multiomics-grn

<!-- BEGIN FILE: gene-regulatory-networks/multiomics-grn/SKILL.md -->
---
name: bio-gene-regulatory-networks-multiomics-grn
description: Build enhancer-driven gene regulatory networks (eGRNs) by integrating single-cell RNA-seq and ATAC-seq using SCENIC+, CellOracle base GRNs, Pando, FigR, DIRECT-NET, TRIPOD, and scMEGA. Covers the accessibility-defines-enhancers principle, peak-to-gene linking and its cell-composition confound, the paired-vs-unpaired decision, and TF-region-gene eRegulon triplets. Use when analyzing 10x multiome or paired/unpaired scRNA+scATAC to infer cis-regulatory GRNs. For RNA-only regulons see scenic-regulons; for in silico TF perturbation see perturbation-simulation.
tool_type: python
primary_tool: SCENIC+
---

## Version Compatibility

Reference examples tested with: SCENIC+ (current Snakemake workflow), pycisTopic 2.0+, pycistarget 1.0+, scanpy 1.10+, MACS3 3.0+; FigR/Signac/ArchR (R).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

SCENIC+ has undergone major API churn: the manual-object API (cisTopicObject, separate pycistarget, SCENICPLUS objects) is superseded by a Snakemake workflow (`scenicplus init_snakemake`). Pre-2024 tutorials are stale; verify against scenicplus.readthedocs.io before coding.

# Multiomics GRN Inference

**"Build an enhancer-driven gene regulatory network from my multiome data"** -> Integrate scRNA-seq and scATAC-seq to identify eRegulons: transcription-factor -> enhancer-region -> target-gene triplets that link TF motif occupancy in accessible chromatin to gene expression.
- Python: SCENIC+ Snakemake pipeline (pycisTopic -> pycistarget -> eRegulons)
- Python: CellOracle base GRN (motif scan in Cicero co-accessible regions); R: Pando / FigR

## The Single Most Important Modern Insight -- Accessibility Defines the Candidate Enhancers, but Every Inference Arrow Leaks

The advance of multiomic GRN inference over expression-only methods is **where the candidate regulatory regions come from**: expression-only tools can only search promoter-proximal motifs, while scATAC nominates the actual distal enhancers active in these cells -- and most cell-type-specific regulatory information is distal. So an eGRN edge is a **triplet (TF -> region -> gene)**, with the region as the mechanistic anchor available for validation (ChIP/CUT&Tag, CRISPRi, reporter). But the reasoning chain leaks at every step: motif-present does not mean the TF binds (motifs are short, degenerate, and shared across a family -- the model cannot tell GATA1 from GATA2); accessible does not mean this TF holds the peak open; and peak-gene correlation does not mean the peak controls the gene. Treat an eGRN as a **prioritized hypothesis list**, not a wiring diagram.

The hardest and least-appreciated step is **peak-to-gene linking, which is confounded by cell-type composition**: across a heterogeneous dataset, any peak open in a cell type correlates with any gene expressed in that same type, whether or not the peak regulates it -- cell identity is a massive shared latent factor. Genome-wide peak-gene correlation therefore mostly recovers co-marker pairs. Mitigations (distance window, within-cell-type or GC/accessibility-matched null, requiring a motif, requiring the TF to be co-expressed) reduce but never eliminate it. Metacell aggregation, needed to beat scATAC sparsity, then introduces pseudo-replication: metacell-derived p-values are not calibrated significance and should be treated as ranking scores.

## eGRN Method Taxonomy

| Method | Citation | Approach | Data regime | Note |
|--------|----------|----------|-------------|------|
| SCENIC+ | Bravo Gonzalez-Blas 2023 *Nat Methods* | topics -> motif enrichment -> region-to-gene & TF-to-gene GBM -> eRegulons | paired or separate | reference eGRN method; heavy (Snakemake, cluster job) |
| CellOracle base GRN | Kamimoto 2023 *Nature* | motif scan in Cicero co-accessible regions; prebuilt base GRNs | scRNA alone OK | base GRN is a prior; feeds perturbation-simulation |
| Pando | Fleck 2023 *Nature* | regression with TF x peak-accessibility interaction term | paired (Seurat) | regions = peaks intersect conserved/annotated CREs |
| FigR | Kartha 2022 *Cell Genomics* | DORCs (genes with many correlated peaks) -> TF-DORC scores | SHARE-seq/paired | `pairCells` for unpaired (pairing caps quality) |
| DIRECT-NET | Zhang 2022 *Sci Adv* | XGBoost CRE-gene importance -> TF via motif | paired or scATAC alone | |
| TRIPOD | Jiang 2022 *Cell Syst* | nonparametric TF-peak-gene trio test, matched/conditional | paired | strong false-positive control |
| scMEGA | Li 2023 *Bioinform Adv* | integrate -> trajectory -> TF-gene network | paired, trajectory | lighter-weight |
| GLUE | Cao & Gao 2022 *Nat Biotechnol* | graph-linked latent embedding | **unpaired/diagonal** | run first to integrate, then a paired method |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Paired 10x Multiome / SHARE-seq, want full eGRN | SCENIC+ | reference method; eRegulon triplets + activity |
| Paired data, lighter/faster | Pando or DIRECT-NET | single-regression / XGBoost, less infrastructure |
| Rigorous false-positive control on trios | TRIPOD | conditional/matched testing removes the composition confound |
| scRNA-seq only (no ATAC) | -> CellOracle prebuilt base GRN | base GRN is a prior; no paired data needed |
| Unpaired scRNA + scATAC (separate experiments) | GLUE to integrate first, then FigR/SCENIC+ | computed pairing caps all downstream link confidence |
| RNA-only regulons, no enhancers needed | -> scenic-regulons | promoter-proximal motif pruning suffices |
| Goal is in silico TF perturbation | -> perturbation-simulation | CellOracle/Dynamo simulate; build the base GRN here |

## SCENIC+ Pipeline (current Snakemake workflow)

**Goal:** Assemble eRegulons (TF -> enhancer -> gene) from paired or separate scRNA + scATAC.

**Approach:** Topic-model the ATAC with pycisTopic, call consensus peaks from per-cell-type pseudobulk (so cell-type labels are needed before peak calling), run pycistarget motif enrichment, then region-to-gene and TF-to-gene GBM regression to build triplets; orchestrate with Snakemake.

```python
# Initialize and run the Snakemake workflow (the supported modern entry point).
# init_snakemake scaffolds a config.yaml pointing at the scATAC fragments, the scRNA
# AnnData, the motif/cisTarget databases, and the cell-type annotation used for pseudobulk.
# scenicplus init_snakemake --out_dir scenicplus_run
# (edit scenicplus_run/Snakemake/config/config.yaml, then run from inside that dir:)
# cd scenicplus_run/Snakemake && snakemake --cores 16

# Region-to-gene search space defaults to min 1kb / max 150kb from the gene, capped at the
# nearest neighboring gene's promoter -- narrower than the +/-500kb used by ArchR/Signac.
```

```python
# Inspect the resulting eRegulons (TF -> region -> gene triplets). The output filename and
# directory are set in config.yaml (output_data); the direct (high-confidence) and extended
# (motif-similarity-inferred) tables are written there. The exact spelling has varied across
# versions, so resolve it by glob rather than hard-coding.
import glob, pandas as pd
ereg_file = glob.glob('scenicplus_run/**/eRegulon*direct*.tsv', recursive=True)[0]
eregulons = pd.read_csv(ereg_file, sep='\t')
summary = (eregulons.groupby('TF')
           .agg(n_regions=('Region', 'nunique'), n_genes=('Gene', 'nunique'))
           .sort_values('n_genes', ascending=False))
# Direct vs extended is a motif-to-TF annotation CONFIDENCE distinction, not topology:
# direct = curated/orthology; _extended adds motif-similarity-inferred (larger, noisier).
```

## CellOracle Base GRN (works without paired multiome)

**Goal:** Build a base GRN -- the candidate TF -> gene scaffold -- from accessibility, as a prior for context-specific modeling.

**Approach:** Define active regions by Cicero co-accessibility (in R), scan them for TF motifs, and format the result as the base GRN; or load a prebuilt base GRN and skip ATAC entirely.

```python
import celloracle as co
import pandas as pd

# Custom base GRN: peaks already filtered to Cicero co-accessible, promoter-linked regions.
peaks = pd.read_parquet('processed_peak_file.parquet')   # columns: peak_id, gene_short_name
tfi = co.motif_analysis.TFinfo(peak_data_frame=peaks, ref_genome='hg38')
tfi.scan(fpr=0.02)                                       # motif FPR
tfi.filter_motifs_by_score(threshold=10)
tfi.make_TFinfo_dataframe_and_dictionary()
base_grn = tfi.to_dataframe()

# Or skip ATAC: prebuilt base GRN as a prior (CellOracle ships ~10 species + mouse atlas).
# base_grn = co.data.load_mouse_scATAC_atlas_base_GRN()
```

The base GRN constrains which TF -> gene edges are allowed; the context-specific weights are then learned per cluster in perturbation-simulation.

## FigR (paired, DORC-based, R)

**Goal:** Identify domains of regulatory chromatin (DORCs) and the TFs that regulate them.

**Approach:** Correlate peaks to genes, call DORCs (genes with an unusually large number of significant peaks), then score TF-DORC associations from motif enrichment plus TF expression correlation.

```r
library(FigR)
# Step 1: peak-gene correlations (smoothed over KNN metacells for sparsity)
cisCor <- runGenePeakcorr(ATAC.se = atac_se, RNAmat = rna_mat,
                          genome = 'hg38', nCores = 8, p.cut = 0.05)
# Step 2: DORC scores then TF-DORC regulation scores (signed: activator/repressor)
dorcMat <- getDORCScores(atac_se, cisCor, geneList = unique(cisCor$Gene), nCores = 8)
figR <- runFigRGRN(ATAC.se = atac_se, dorcTab = cisCor, dorcMat = dorcMat,
                   rnaMat = rna_mat, genome = 'hg38', nCores = 8)
```

## Per-Method Failure Modes

### Cell-composition confound in peak-gene linking
**Trigger:** genome-wide peak-gene correlation with no within-type control. **Mechanism:** any peak open in a cell type correlates with any gene expressed in it. **Symptom:** "links" that are just cell-type co-markers. **Fix:** restrict to the distance window, use a matched null (Signac) or within-type correlation, and require a motif.

### Metacell p-value laundering
**Trigger:** reporting astronomically small p-values from KNN-smoothed metacells. **Mechanism:** metacells are not independent (overlapping cells). **Symptom:** millions of "significant" links. **Fix:** treat metacell p-values as ranking scores; apply FDR honest about pseudo-replication.

### Motif-family overclaiming
**Trigger:** naming a specific TF (GATA1) from a family motif. **Mechanism:** paralogs share near-identical motifs. **Symptom:** confident single-TF claims where only a family is detectable. **Fix:** report the motif/family and require orthogonal evidence to single out a member.

### Unstated/wrong pairing in unpaired data
**Trigger:** computing "joint" correlations on separately-measured scRNA and scATAC. **Mechanism:** cells were computationally matched, not co-measured. **Symptom:** no pairing method or accuracy reported. **Fix:** integrate with GLUE/anchors first; report pairing quality; treat links as upper-bounded by it.

### Treating eGRN edges as ground truth
**Trigger:** a published wiring diagram with no orthogonal validation. **Mechanism:** accessibility != binding != regulation, and motif/proximity validation is circular. **Symptom:** no ChIP/CRISPRi/perturbation check; validation uses the same motif DB used to build the net. **Fix:** validate against independent ChIP-seq or perturbation data.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Region-to-gene window: 1kb-150kb (SCENIC+) | Bravo Gonzalez-Blas 2023 | capped at nearest gene promoter; narrower than +/-500kb conventions |
| Peak-gene window +/-500kb (ArchR/Signac/Cicero) | tool defaults | distal enhancer reach; pair with a matched null |
| MACS3 `--keep-dup all`, BEDPE/shift-extsize | ATAC convention | fragment-based peak calling for the region universe |
| Motif FPR ~0.02 (CellOracle scan) | CellOracle default | motif-match false-positive rate |
| eRegulon: direct vs _extended | SCENIC+ | direct = curated motif2TF; extended adds inferred (noisier) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| stale SCENIC+ API errors | following pre-2024 manual-object tutorials | use the Snakemake workflow; check scenicplus.readthedocs.io |
| consensus peak step fails | no cell-type labels for pseudobulk | annotate cell types before peak calling |
| feather DB format error | region-based vs gene-based DB mismatch / old ctxcore | use region-based DBs for ATAC; align versions |
| huge spurious link set | composition confound + no matched null | window + within-type/matched-null + motif requirement |
| empty eRegulons | species/assembly/motif-collection mismatch | match genome, motif DB, and gene IDs |

## References

- Bravo Gonzalez-Blas C, et al. 2023. SCENIC+: single-cell multiomic inference of enhancers and gene regulatory networks. *Nat Methods* 20(9):1355-1367.
- Kamimoto K, et al. 2023. Dissecting cell identity via network inference and in silico gene perturbation (CellOracle). *Nature* 614(7949):742-751.
- Fleck JS, et al. 2023. Inferring and perturbing cell fate regulomes in human brain organoids (Pando). *Nature* 621:365-372.
- Kartha VK, et al. 2022. Functional inference of gene regulation using single-cell multi-omics (FigR). *Cell Genomics* 2(9):100166.
- Zhang L, Zhang J, Nie Q. 2022. DIRECT-NET. *Sci Adv* 8(22):eabl7393.
- Jiang Y, et al. 2022. TRIPOD: nonparametric single-cell multiomic trio characterization. *Cell Syst* 13(9):737-751.e4.
- Li Z, et al. 2023. scMEGA. *Bioinform Adv* 3(1):vbad003.
- Cao ZJ, Gao G. 2022. Multi-omics integration and regulatory inference with graph-linked embedding (GLUE). *Nat Biotechnol* 40(9):1458-1466.
- Pliner HA, et al. 2018. Cicero: cis-regulatory DNA interactions from single-cell accessibility. *Mol Cell* 71(5):858-871.e8.

## Related Skills

- scenic-regulons - RNA-only regulon inference (promoter-proximal motif pruning)
- perturbation-simulation - in silico TF perturbation built on a CellOracle base GRN
- coexpression-networks - undirected co-expression baseline
- single-cell/scatac-analysis - scATAC preprocessing with Signac/ArchR
- atac-seq/atac-peak-calling - peak calling for the region universe
- chip-seq/motif-analysis - motif enrichment and TF binding for validation
<!-- END FILE: gene-regulatory-networks/multiomics-grn/SKILL.md -->

## 子目录：gene-regulatory-networks/perturbation-simulation

<!-- BEGIN FILE: gene-regulatory-networks/perturbation-simulation/SKILL.md -->
---
name: bio-gene-regulatory-networks-perturbation-simulation
description: Simulate transcription factor perturbation effects on cell state in silico with CellOracle and Dynamo, and predict transcriptional responses to genetic perturbations with GEARS, scGen, and CPA. Covers the direction-not-magnitude principle, local-linear validity, the GRN/velocity error it inherits, baseline discipline (mean and additive baselines), and the validation gap. Use when predicting TF knockout or overexpression effects, ranking driver TFs for fate transitions, or planning perturbation experiments. For GRN construction see multiomics-grn; for experimental Perturb-seq see single-cell/perturb-seq.
tool_type: python
primary_tool: CellOracle
---

## Version Compatibility

Reference examples tested with: CellOracle 0.18+, scanpy 1.10+, anndata 0.10+; Dynamo (dynamo-release 1.4+), GEARS, CPA (scvi-tools ecosystem) where used.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Perturbation Simulation

**"Predict what happens if I knock out this transcription factor"** -> Propagate a forced expression change through a learned GRN (or a learned velocity vector field), then project the shift onto the cell-state manifold to predict the DIRECTION cells move.
- Python: `celloracle.Oracle` for GRN-based in silico KO/overexpression
- Python: `dynamo` for vector-field (Jacobian) perturbation; `GEARS`/`CPA` for response prediction

## The Single Most Important Modern Insight -- These Methods Predict a Direction, Locally, and Inherit Every Error of the Underlying Model

In silico perturbation outputs a **shift vector whose orientation is the deliverable**; its absolute magnitude is uncalibrated. CellOracle propagates an expression *shift* (not absolute counts) and is explicit that it is for **hypothesis generation**, predicting direction not magnitude. The machinery is a **local linear approximation**: CellOracle's per-cluster GRN is a regularized linear model iterated a small fixed number of steps (`n_propagation` default 3), and Dynamo's perturbation is a first-order Taylor expansion of the learned vector field via its Jacobian. So predictions are valid only for **small perturbations near the observed manifold, for one or a few steps** -- they cannot capture long-range feedback, trans effects, or transitions to attractors not already in the data (CellOracle moves probability mass among observed states on the KNN graph; it cannot invent a new cell type). And every prediction **inherits the errors of its substrate**: CellOracle is only as good as its GRN, Dynamo only as good as its RNA-velocity estimate (which has documented reliability problems, Bergen 2021; Gorin 2022).

The 2025 baseline discipline is non-negotiable: for perturbation *response prediction*, deep and foundation models do **not** consistently beat trivial baselines -- Ahlmann-Eltze, Huber & Anders 2025 (*Nat Methods* 22:1657) show that for unseen single perturbations no DL model beats predicting the training **mean** response, and for combinations none beats the **additive** baseline (summing single-gene effects). Always report the mean baseline (unseen singles) and additive baseline (combinations); a method that does not beat them adds no value. And ask the validation question of any result: how many predictions were tested against a real knockout, and were the failures reported?

## Method Taxonomy

| Method | Citation | Mechanism | Predicts | Inherits errors of |
|--------|----------|-----------|----------|--------------------|
| CellOracle | Kamimoto 2023 *Nature* | shift propagated through per-cluster linear GRN, projected on KNN graph | direction of cell-state shift | the GRN (base + regression) |
| Dynamo | Qiu 2022 *Cell* | Jacobian of a learned analytical vector field (Df = J*Dx) | redirected fate / least-action path | RNA-velocity estimate |
| GEARS | Roohani 2024 *Nat Biotechnol* | GNN over gene + GO graphs | unseen single & combinatorial responses, GI type | training Perturb-seq + graphs |
| scGen / CPA | Lotfollahi 2019/2023 | latent-space arithmetic / disentangled composable embeddings | response to known/composed perturbations | training distribution |
| Boolean / ODE (BoolNet, BoolODE) | Müssel 2010 | mechanistic logic/kinetic simulation; attractors | extrapolative fate, multistability | the hand-curated wiring |

Data-driven methods (CellOracle/Dynamo/DL) are genome-scale, local, linear, direction-only; mechanistic Boolean/ODE models are hand-curated and small but nonlinear and extrapolative. State which regime a result belongs to.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Predict TF KO/OE effect on cell fate from scRNA + accessibility prior | CellOracle | GRN-based shift onto the developmental flow; direction + perturbation score |
| Have high-quality (labeling-based) velocity, want fate redirection | Dynamo | learned vector field + Jacobian; no GRN prior needed |
| Predict response to unseen perturbations / combinations | GEARS or CPA | generalize via gene/GO graphs or composable embeddings -- but check baselines |
| Need mechanistic attractor/multistability reasoning | Boolean/ODE (BoolNet) | only family that extrapolates beyond observed states |
| Build the base GRN that CellOracle perturbs | -> multiomics-grn | base GRN construction lives there |
| Validate predictions experimentally | -> single-cell/perturb-seq | Perturb-seq is the interventional ground truth |

## CellOracle: Build the GRN

**Goal:** Learn context-specific (per-cluster) regulatory weights on top of a base-GRN prior.

**Approach:** Import scRNA-seq and the base GRN, impute, then fit a regularized linear model per cluster and filter links by significance.

```python
import scanpy as sc
import celloracle as co
import pandas as pd

adata = sc.read_h5ad('clustered.h5ad')          # normalized, log, PCA, clustered
oracle = co.Oracle()
oracle.import_anndata_as_raw_count(adata=adata, cluster_column_name='cell_type',
                                   embedding_name='X_umap')
oracle.import_TF_data(TF_info_matrix=pd.read_parquet('base_grn.parquet'))  # prior; see multiomics-grn
oracle.perform_PCA()
oracle.knn_imputation(n_pca_dims=50, k=None, balanced=True, b_sight=3000, b_maxl=1500)

links = oracle.get_links(cluster_name_for_GRN_unit='cell_type', alpha=10)
links.filter_links(p=0.001, weight='coef_abs', threshold_number=2000)
oracle.get_cluster_specific_TFdict_from_Links(links_object=links)
oracle.fit_GRN_for_simulation(alpha=10, use_cluster_specific_TFdict=True)
```

## CellOracle: Simulate and Score

**Goal:** Predict the direction cells move under a TF knockout or overexpression.

**Approach:** Set the gene of interest to 0 (KO) or above-max (OE), propagate the shift a few steps, estimate KNN transition probabilities, compute the per-cell embedding shift, and score it against the developmental vector field by inner product.

```python
import numpy as np

# perturb_condition sets the clamped value: 0.0 = knockout; above observed max = overexpression.
# n_propagation is small BY DESIGN (3); increasing it amplifies linear-approximation error.
oracle.simulate_shift(perturb_condition={'GATA1': 0.0}, n_propagation=3)
oracle.estimate_transition_prob(n_neighbors=200, knn_random=True, sampled_fraction=1)
oracle.calculate_embedding_shift(sigma_corr=0.05)

# Perturbation score = inner product of the simulated shift with the developmental flow.
# It is meaningless without a defined development vector field (Gradient_calculator below).
from celloracle.applications import Gradient_calculator
grad = Gradient_calculator(oracle_object=oracle, pseudotime_key='pseudotime')
grad.calculate_p_mass(smooth=0.8, n_grid=40, n_neighbors=200)
grad.calculate_mass_filter(min_mass=0.01, plot=False)   # required before calculate_gradient
grad.calculate_gradient()
shift = np.sqrt((oracle.adata.obsm['delta_embedding'] ** 2).sum(axis=1))   # magnitude is uncalibrated
```

## Dynamo: Vector-Field Perturbation

**Goal:** Predict fate redirection from a learned dynamical system rather than a GRN prior.

**Approach:** Reconstruct the analytical vector field, compute its Jacobian, then apply a genetic perturbation as a local linear response.

```python
import dynamo as dyn

dyn.vf.VectorField(adata, basis='umap')          # learn the analytical vector field first
dyn.vf.jacobian(adata, regulators=['GATA1'], effectors=['SPI1'])
# expression is a LIST aligned to genes (negative = suppress); perturbation writes a new basis.
dyn.pd.perturbation(adata, 'GATA1', [-100], emb_basis='umap')
dyn.pl.streamline_plot(adata, color='cell_type', basis='umap_perturbation')
```

## Baseline Discipline (always run these)

**Goal:** Establish whether a perturbation-prediction model beats triviality before trusting it.

**Approach:** Compare predictions against the training-mean response (unseen single perturbations) and the additive baseline (combinations).

```python
import numpy as np

# Mean baseline: predict the average perturbed profile across the training perturbations.
mean_baseline = train_perturbed.mean(axis=0)

# Additive baseline for a double perturbation: sum the two single-gene log-fold-changes.
additive_pred = lfc_singleA + lfc_singleB

# A model only "works" if its error is below these baselines (Ahlmann-Eltze 2025).
```

## Per-Method Failure Modes

### Reporting magnitudes as quantitative
**Trigger:** citing a predicted fold-change as an effect size. **Mechanism:** the methods are direction-only; amplitude is uncalibrated. **Symptom:** quantitative KO transcriptome claims. **Fix:** report direction / perturbation score; validate magnitude experimentally.

### No trivial baseline
**Trigger:** a DL/foundation-model perturbation predictor reported without baselines. **Mechanism:** mean (singles) and additive (combos) baselines are often competitive. **Symptom:** "state of the art" with no mean/additive comparison. **Fix:** report both baselines; require the model to beat them.

### Perturbing far outside the manifold
**Trigger:** extreme overexpression, knocking out a gene not expressed in the cluster, or expecting a brand-new cell type. **Mechanism:** local linear validity is violated; CellOracle can only move mass among observed states. **Symptom:** implausible jumps. **Fix:** keep perturbations small and near observed states; interpret one step.

### Cranking n_propagation
**Trigger:** raising `n_propagation` to get "long-range" effects. **Mechanism:** iterating a linear model amplifies approximation error. **Symptom:** runaway shifts. **Fix:** keep the small default; treat it as a local estimate.

### Trusting the substrate blindly
**Trigger:** treating the CellOracle GRN as ground truth, or running Dynamo on noisy splicing-based velocity. **Mechanism:** predictions inherit GRN/velocity error (Bergen 2021; Gorin 2022; and a 2024 preprint critiques CellOracle's GRN for ignoring distal interactions). **Symptom:** confident predictions on a poorly-validated network/field. **Fix:** sanity-check the GRN/velocity; present results as hypotheses.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| n_propagation = 3 | CellOracle default | small by design; local linear validity |
| KO value = 0.0; OE = above observed max | CellOracle convention | clamped perturbation input |
| link filter p<0.001, top ~2000 by coef_abs | CellOracle tutorial | sparsify the GRN before simulation |
| mean baseline (unseen singles), additive (combos) | Ahlmann-Eltze 2025 | the bar any predictor must clear |
| sigma_corr ~0.05 | CellOracle default | embedding-shift smoothing |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| perturbation score all ~0 / meaningless | no development vector field defined | run `Gradient_calculator` before scoring |
| KeyError on gene in `simulate_shift` | gene absent from the fitted GRN | confirm the gene is in the base GRN and expressed |
| Dynamo perturbation errors | vector field/Jacobian not computed | run `dyn.vf.VectorField` then `dyn.vf.jacobian` first |
| huge predicted shift | n_propagation too high / out-of-manifold perturbation | keep n_propagation small; perturb near observed states |
| "model beats prior methods" but no baseline | missing mean/additive comparison | add baselines (Ahlmann-Eltze 2025) |

## References

- Kamimoto K, et al. 2023. Dissecting cell identity via network inference and in silico gene perturbation (CellOracle). *Nature* 614(7949):742-751.
- Qiu X, et al. 2022. Mapping transcriptomic vector fields of single cells (Dynamo). *Cell* 185(4):690-711.e45.
- Roohani Y, Huang K, Leskovec J. 2024. Predicting transcriptional outcomes of novel multigene perturbations with GEARS. *Nat Biotechnol* 42(6):927-935.
- Lotfollahi M, Wolf FA, Theis FJ. 2019. scGen predicts single-cell perturbation responses. *Nat Methods* 16:715-721.
- Lotfollahi M, et al. 2023. Predicting cellular responses to complex perturbations in high-throughput screens (CPA). *Mol Syst Biol* 19(6):e11517.
- Ahlmann-Eltze C, Huber W, Anders S. 2025. Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines. *Nat Methods* 22:1657-1661.
- Bergen V, et al. 2021. RNA velocity - current challenges and future perspectives. *Mol Syst Biol* 17(8):e10282.
- Gorin G, Fang M, Chari T, Pachter L. 2022. RNA velocity unraveled. *PLoS Comput Biol* 18(9):e1010492.
- Müssel C, Hopfensitz M, Kestler HA. 2010. BoolNet. *Bioinformatics* 26(10):1378-1380.

## Related Skills

- multiomics-grn - build the CellOracle base GRN from accessibility
- scenic-regulons - regulon activity as an alternative TF-driver readout
- single-cell/perturb-seq - experimental Perturb-seq, the interventional ground truth
- single-cell/trajectory-inference - pseudotime/development flow for the perturbation score
- causal-genomics/mendelian-randomization - population-genetics route to causality (contrast)
<!-- END FILE: gene-regulatory-networks/perturbation-simulation/SKILL.md -->

## 子目录：gene-regulatory-networks/scenic-regulons

<!-- BEGIN FILE: gene-regulatory-networks/scenic-regulons/SKILL.md -->
---
name: bio-gene-regulatory-networks-scenic-regulons
description: Infer transcription factor regulons from single-cell RNA-seq with pySCENIC by combining GRNBoost2 co-expression, cisTarget motif-enrichment pruning, and AUCell per-cell activity scoring. Covers the motif-pruning-as-directionality principle, regulon specificity scoring, run-to-run stability, and database/species matching. Use when identifying TF regulons, scoring TF activity per cell, finding master regulators of cell identity, or comparing regulon activity across conditions. For enhancer-driven multiomic GRNs see multiomics-grn; for bulk inference and VIPER protein-activity see grn-inference.
tool_type: python
primary_tool: pySCENIC
---

## Version Compatibility

Reference examples tested with: pySCENIC 0.12+, ctxcore 0.2+, arboreto 0.1.6+, scanpy 1.10+, loompy 3.0+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The motif-DB machinery lives in `ctxcore`; a ctxcore/feather-format version mismatch is the most common silent failure. pySCENIC is most reliable on a dedicated Python 3.10 environment.

# SCENIC Regulons

**"Identify transcription factor regulons and score TF activity from my scRNA-seq data"** -> Run the pySCENIC three-step pipeline: infer TF-target co-expression with GRNBoost2, prune to direct targets by cis-regulatory motif enrichment with cisTarget, then score per-cell regulon activity with AUCell.
- CLI: `pyscenic grn` -> `pyscenic ctx` -> `pyscenic aucell`
- Python: `arboreto_with_multiprocessing.py` for the GRN step (avoids the dask breakage)

## The Single Most Important Modern Insight -- Motif Pruning Is What Converts Co-expression into Directed Regulation

Step 1 (GRNBoost2) produces **undirected co-expression only** -- it is no better than WGCNA and inherits all of co-expression's confounding (indirect edges, batch, cell-cycle). The entire conceptual payload of SCENIC is **Step 2 (cisTarget)**: for each module it asks whether the candidate TF's binding motif is significantly enriched (NES >= 3.0) in the cis-regulatory space of the module's targets, and keeps only the targets in the motif's leading edge. This (a) imposes a mechanistic prior -- the TF can physically bind near its retained targets, (b) breaks the symmetry of co-expression into a TF -> target direction, and (c) discards indirect targets. **A "regulon" is by definition only the post-cisTarget TF plus its direct targets.** Modules that were never pruned are co-expression modules, and calling them regulons misuses the word.

The second non-obvious consequence is **AUCell: regulon activity is not TF expression.** AUCell ranks genes within each cell and computes the area under the recovery curve for the regulon's gene set, so activity can be high even when the TF's own mRNA is dropout-zero (TF transcripts are sparse). Showing TF *expression* in place of regulon AUC -- or "validating" activity by its correlation with TF expression -- misses the method's point and is circular. SCENIC regulons remain motif-supported co-expression: a strong, directed hypothesis worth a knockdown, not proof of causal regulation.

## Pipeline Taxonomy

| Step | Tool | Produces | Key parameter | Watch out for |
|------|------|----------|---------------|---------------|
| 1. GRN | GRNBoost2 (or GENIE3) | TF-target co-expression adjacencies | `--seed`, `--num_workers` | stochastic; not reproducible without a fixed seed |
| 2. Prune | cisTarget (ctxcore) | regulons (direct targets) | `--nes_threshold 3.0`, `--rank_threshold 5000` | feather DB + motif2TF version must match |
| 3. Score | AUCell | per-cell regulon activity (AUC) | `--auc_threshold 0.05` | this is the top-fraction, NOT the binarization cut |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| scRNA-seq, want TF regulons + per-cell activity | pySCENIC grn/ctx/aucell | the canonical workflow |
| GRN step hangs / KilledWorker | `arboreto_with_multiprocessing.py` | arboreto's dask backend breaks on newer dask |
| Need reproducible regulons | run GRN 10-100x, keep links recurring >80% | GRNBoost2/GENIE3 are stochastic |
| Which regulons mark a cell type | Regulon Specificity Score (RSS) | JSD-based specificity, not just magnitude |
| Paired scRNA + scATAC available | -> multiomics-grn (SCENIC+) | accessibility defines enhancers; eRegulons add the region layer |
| Bulk RNA-seq / want protein activity | -> grn-inference (ARACNe + VIPER) | SCENIC is single-cell; VIPER reads TF activity from bulk |
| Compare activity across conditions | run SCENIC once on the integrated object | raw AUC is population-relative; batch survives into regulons |

## Required Databases

cisTarget needs three matched resources: ranking database(s), motif-to-TF annotations, and the TF list -- all the same species/assembly/symbol namespace. Download from `resources.aertslab.org/cistarget/`.

```bash
# Human hg38 gene-based rankings (~1.5 GB each). Run ctx with BOTH search-space DBs
# (500bp+100bp around TSS, and TSS +/-10kb) so the leading-edge logic pools them.
wget https://resources.aertslab.org/cistarget/databases/homo_sapiens/hg38/refseq_r80/mc9nr/gene_based/hg38__refseq-r80__10kb_up_and_down_tss.mc9nr.genes_vs_motifs.rankings.feather
wget https://resources.aertslab.org/cistarget/motif2tf/motifs-v9-nr.hgnc-m0.001-o0.0.tbl
# The ranking-DB version (mc9nr / v10) and the motif2tf annotation version MUST match.
```

## Step 1: GRN Inference (use the multiprocessing wrapper)

**Goal:** Infer TF-target co-expression adjacencies as candidate regulatory modules.

**Approach:** Run GRNBoost2 via the bundled multiprocessing script (single-node, stable) rather than the dask backend, and fix the seed so the stochastic boosting is reproducible.

```bash
# arboreto's dask backend breaks on dask>=2.x (silent hangs, KilledWorker).
# The bundled multiprocessing wrapper is the supported workaround.
python arboreto_with_multiprocessing.py \
    filtered.loom allTFs_hg38.txt \
    --method grnboost2 --output adj.tsv \
    --num_workers 8 --seed 42
```

## Step 2: Prune to Regulons by Motif Enrichment

**Goal:** Keep only TF-target links whose target genes are enriched for the TF's binding motif -- the step that confers directness and direction.

**Approach:** Load the ranking databases and motif2TF annotations, build candidate modules from the adjacencies, and run cisTarget pruning; targets surviving motif enrichment (NES >= 3.0) form the regulon.

```python
import glob, pickle, pandas as pd
from pyscenic.utils import modules_from_adjacencies
from pyscenic.prune import prune2df, df2regulons
from ctxcore.rnkdb import FeatherRankingDatabase

adjacencies = pd.read_csv('adj.tsv', sep='\t')
expr = pd.read_csv('expr.csv', index_col=0)            # cells x genes
modules = list(modules_from_adjacencies(adjacencies, expr))

dbs = [FeatherRankingDatabase(f, name=f) for f in glob.glob('*.genes_vs_motifs.rankings.feather')]
# rank_threshold=5000 matches the CLI default (the prune2df Python default is 1500).
df = prune2df(dbs, modules, 'motifs-v9-nr.hgnc-m0.001-o0.0.tbl', rank_threshold=5000)
regulons = df2regulons(df)                              # TF + direct targets only

with open('regulons.pkl', 'wb') as fh:
    pickle.dump(regulons, fh)
```

CLI equivalent for steps 1-2 (`pyscenic grn`, then `pyscenic ctx adj.tsv DB.feather --annotations_fname motifs.tbl --expression_mtx_fname filtered.loom -o reg.csv`). ctx verified defaults: `--rank_threshold 5000`, `--auc_threshold 0.05`, `--nes_threshold 3.0`, `--min_genes 20`. `--mask_dropouts` now defaults to False (matching R SCENIC); it changes the TF-target correlation sign that splits activating `(+)` from repressing `(-)` regulons, so report the setting used.

## Step 3: AUCell Per-Cell Activity

**Goal:** Score each regulon's activity in every cell, robustly to dropout.

**Approach:** Rank genes within each cell, integrate the recovery curve over the top fraction (`auc_threshold`, default 0.05 = top 5%), and emit a cell-by-regulon AUC matrix.

```python
from pyscenic.aucell import aucell

# auc_threshold = top 5% of the ranking integrated for the AUC -- NOT a binarization cut.
auc_mtx = aucell(expr, regulons, auc_threshold=0.05, num_workers=8)
auc_mtx.to_csv('auc_matrix.csv')
```

## Interpretation: Specificity and Binarization

**Goal:** Surface the regulons that define each cell type and convert activity to on/off states for clustering.

**Approach:** Use the Regulon Specificity Score (Jensen-Shannon divergence vs an idealized cell-type-specific distribution) for identity regulators, and binarize the AUC distribution (bimodal -> density threshold) for state heatmaps.

```python
from pyscenic.rss import regulon_specificity_scores
from pyscenic.binarization import binarize

cell_types = pd.read_csv('cell_types.csv', index_col=0)['cell_type']
rss = regulon_specificity_scores(auc_mtx, cell_types)     # high RSS = identity regulator
binary_mtx, thresholds = binarize(auc_mtx)                # per-regulon on/off
```

RSS (rewards specificity) and a per-cluster AUC z-score (rewards magnitude) can disagree; prefer RSS for "which regulon marks this cluster."

## Per-Method Failure Modes

### Calling unpruned modules "regulons"
**Trigger:** skipping ctx, or dropping the NES threshold to admit everything. **Mechanism:** without motif enrichment the output is co-expression, not direct regulation. **Symptom:** no motif DB/version reported; implausibly large "regulons." **Fix:** always run cisTarget; report DB + motif2TF versions and the search-space windows.

### Dask hang in the GRN step
**Trigger:** native arboreto on dask>=2.x. **Mechanism:** scheduler incompatibility. **Symptom:** silent hang or KilledWorker. **Fix:** use `arboreto_with_multiprocessing.py` (single-node, stable).

### Species / assembly mismatch
**Trigger:** mouse genes against an hg38 ranking DB, or HGNC vs MGI symbol mismatch. **Mechanism:** gene IDs do not map into the database. **Symptom:** near-empty regulon set. **Fix:** match expression IDs, ranking DB, and motif2TF to one species/assembly/namespace.

### Cross-condition AUC comparison without batch control
**Trigger:** comparing raw AUC across separately-run SCENIC analyses or strong batches. **Mechanism:** AUC is relative to the population it was ranked within; batch-driven co-expression can pass motif enrichment by chance. **Symptom:** a "condition-specific regulator" that tracks the batch. **Fix:** run SCENIC once on the integrated object; sanity-check condition regulons against batch.

### Over-reading _extended or _- regulons
**Trigger:** using `_extended` regulons for direct-binding claims, or building a story on `(-)` repressor activity. **Mechanism:** `_extended` adds orthology/similarity-inferred (low-confidence) motif annotations; negative regulons are sparse and weakly enriched. **Symptom:** direct-regulation claims from low-confidence edges. **Fix:** default to high-confidence positive regulons; treat `_extended`/`(-)` as hypotheses.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| NES >= 3.0 (motif enrichment) | Aibar 2017 / iRegulon (Janky 2014) | recovery-curve enrichment cutoff defining a supported motif |
| auc_threshold = 0.05 (top 5%) | pySCENIC default | fraction of the ranking integrated for the AUC |
| GRN reruns: keep links recurring >80% of runs | Van de Sande 2020 | GRNBoost2/GENIE3 are stochastic; recurrence = high confidence |
| min_genes = 20 per regulon | pySCENIC default | smaller target sets give unstable AUC |
| >= a few hundred cells per cell type | practical | rare clusters and doublets inflate spurious regulons |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "not a cisTarget Feather database in v1 or v2 format" | ctxcore/DB version mismatch | download current DB; align `ctxcore` version |
| empty regulon set | species/assembly or symbol mismatch | match gene IDs to the DB namespace |
| different regulons each run | unset seed in GRN step | fix `--seed`; run multiple seeds and intersect |
| activity != TF expression confuses the reader | conflating regulon AUC with TF mRNA | report AUCell activity; that independence is the point |
| ctx returns nothing | missing/mismatched `--annotations_fname` | supply matching motif2TF; check DB is gene-based (not region-based) |

## References

- Aibar S, et al. 2017. SCENIC: single-cell regulatory network inference and clustering. *Nat Methods* 14(11):1083-1086.
- Van de Sande B, et al. 2020. A scalable SCENIC workflow for single-cell gene regulatory network analysis. *Nat Protoc* 15(7):2247-2276.
- Moerman T, et al. 2019. GRNBoost2 and Arboreto. *Bioinformatics* 35(12):2159-2161.
- Janky R, et al. 2014. iRegulon: cisTarget ranking-and-recovery framework. *PLoS Comput Biol* 10(7):e1003731.
- Suo S, et al. 2018. Revealing critical regulators of cell identity (Regulon Specificity Score). *Cell Rep* 25(6):1436-1445.e3.
- Huynh-Thu VA, et al. 2010. GENIE3. *PLoS ONE* 5(9):e12776.

## Related Skills

- multiomics-grn - enhancer-driven eRegulons from paired scRNA+scATAC (SCENIC+)
- grn-inference - bulk GRN inference and VIPER TF protein-activity (the Califano lineage)
- coexpression-networks - undirected co-expression modules (what step 1 produces alone)
- single-cell/clustering - cluster cells before regulon and RSS analysis
- single-cell/preprocessing - QC, doublet removal, and normalization of scRNA-seq inputs
- single-cell/doublet-detection - remove doublets that inflate spurious regulons
<!-- END FILE: gene-regulatory-networks/scenic-regulons/SKILL.md -->

<!-- END CATEGORY: gene-regulatory-networks -->

