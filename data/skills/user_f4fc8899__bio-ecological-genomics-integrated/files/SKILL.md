---
slug: bio-ecological-genomics-integrated
version: 1.0.1
displayName: "生态基因组学 / Ecological genomics"
name: bio-ecological-genomics-integrated
summary: "中文：生态基因组学综合技能，整合 6 个相关专题，覆盖生态基因组学：eDNA宏条形码、生物多样性度量、群落生态学、景观基因组学、物种界定。 English: Integrated Ecological genomics skill covering 6 related topics, including Ecological genomics: eDNA metabarcoding, biodiversity metrics, community ecology, landscape genomics, species delimitation."
description: "中文：这是一个面向生态基因组学的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：生态基因组学：eDNA宏条形码、生物多样性度量、群落生态学、景观基因组学、物种界定。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：ASAP, LEA, dada2。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Ecological genomics, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Ecological genomics: eDNA metabarcoding, biodiversity metrics, community ecology, landscape genomics, species delimitation. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: ASAP, LEA, dada2. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# ecological-genomics 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: ecological-genomics -->

## 子目录：ecological-genomics/biodiversity-metrics

<!-- BEGIN FILE: ecological-genomics/biodiversity-metrics/SKILL.md -->
---
name: bio-ecological-genomics-biodiversity-metrics
description: Quantifies biodiversity from species abundance/incidence tables using Hill numbers (iNEXT) with coverage-based rarefaction-extrapolation (Chao & Jost 2012), asymptotic richness via Chao1/ACE/jackknife as a lower bound, Baselga turnover/nestedness partition with the Podani alternative as sensitivity check, mandatory Hellinger transformation before ordination (Legendre & Gallagher 2001), Faith PD and SES_MPD/SES_MNTD with explicit null-model choice, and Maire 2015 functional-diversity dimensionality optimization. Use when comparing diversity across sites with unequal sampling effort, picking the right richness estimator for singleton-heavy amplicon data, partitioning beta diversity into turnover vs nestedness, reporting Hill-number effective species counts rather than raw entropies, computing SES_MPD with explicit null-model justification, or deciding whether to apply standard metrics to compositional amplicon data. Not for clinical 16S microbiome diversity (see microbiome/diversity-analysis).
tool_type: r
primary_tool: iNEXT
---

## Version Compatibility

Reference examples tested with: iNEXT 3.0+, iNEXT.3D 1.0+, vegan 2.6+, betapart 1.6+, picante 1.8+, ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Biodiversity Metrics

**"Calculate species diversity for my ecological samples"** -> Compute Hill-number diversity (numbers-equivalent of richness, Shannon, Simpson) with coverage-based rarefaction/extrapolation, choose the richness estimator appropriate to the singleton/doubleton signature of the data, and partition beta diversity into turnover and nestedness components with a documented partition framework.
- R: `iNEXT::iNEXT()` for coverage-based rarefaction/extrapolation
- R: `betapart::beta.multi()` for Baselga turnover/nestedness partition
- R: `picante::ses.mpd()` for phylogenetic-community SES with explicit null model

## The Single Most Important Modern Insight -- Standardize by COVERAGE not by sample size

Chao & Jost 2012 *Ecology* 93(12):2533-2547 established that comparing diversity across assemblages by rarefying to a common sample size systematically biases comparisons whenever assemblages differ in underlying diversity: a 100-read rarefaction of a 50-species community is essentially saturated (coverage approximately 99%) while the same 100 reads from a 500-species community covers only approximately 40% of the underlying diversity. The two rarefied diversities are not measuring the same thing. **Coverage-based rarefaction with iNEXT is the postdoc-grade default; sample-size rarefaction is now considered a methodological anti-pattern for cross-site comparison.**

A second insight pairs with this: raw Shannon and Simpson indices are entropies, NOT diversities. Jost 2006 *Oikos* 113(2):363-375 showed that only their numbers-equivalents (exp(H), 1/D) are comparable as effective species counts and have the intuitive "doubling property" (merging two equally diverse equally abundant assemblages doubles the diversity). Reporting raw Shannon = 3.2 vs 3.0 hides whether the difference is large or trivial; reporting `1`D = 24.5 vs 20.1 species-equivalents makes the 22% gap visible.

## Algorithmic Taxonomy

| Method | Estimand | Strength | Fails when |
|--------|----------|----------|------------|
| Hill numbers q=0,1,2 (iNEXT) | Effective species count at order q | Unifies richness, Shannon, Simpson; doubling property | None; report all three q values |
| Chao1 = S + f1^2/(2*f2) | Lower bound on asymptotic richness | Non-parametric; works at low coverage | Singletons dominated by PCR error (amplicon data); f2 near zero |
| Chao1bc = S + f1(f1-1)/(2(f2+1)) | Bias-corrected Chao1 | Stable when f2 = 0 | Same singleton-bias issue |
| ACE | Asymptotic richness using all rare classes (f1...f10) | Uses more rare-class information than Chao1 | Choice of "rare" cutoff (default 10) is arbitrary |
| Jackknife1 = S + f1*(n-1)/n | Asymptotic richness via resampling | Robust when f2 = 0 | Sensitive to singleton count alone |
| Coverage-based rarefaction (iNEXT) | Diversity at standardized completeness | Correct comparison across sites with unequal effort | Extrapolation beyond 2x reference size is unreliable |
| Sample-size rarefaction | Diversity at common n | Legacy familiar | Systematically biased when communities differ in true diversity |
| Faith's PD | Sum of branch lengths on spanning tree | Captures evolutionary distinctness | Sensitive to richness; report alongside SES_PD |
| Rao's Q | Pairwise functional/phylogenetic distance * abundance | Unifies taxonomic and functional/phylogenetic diversity | Trait dimensionality artifacts (see Maire 2015) |
| FRic / FEve / FDiv | Functional richness/evenness/divergence | Multidimensional trait coverage | FRic inflates with collinear traits; optimize axis count |
| Baselga beta partition | Sorensen = turnover (Simpson) + nestedness | Decomposes beta into ecological processes | Not unique; Podani partition gives different components |
| Podani / Carvalho partition | Alternative turnover + richness-difference | Conceptually distinct from Baselga | Same data, different conclusion possible; report both |
| Hellinger transform + PCA/RDA | Solves double-zero problem | Standard for community ordination | None; required preprocessing |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Cross-site diversity comparison with unequal sampling effort | Coverage-based rarefaction in iNEXT to common C (typically 0.95) | Sample-size rarefaction is biased when assemblages differ in true diversity |
| Reporting diversity for publication | Hill numbers q=0,1,2 (numbers-equivalents) | Comparable, additive, doubling property; raw entropies are not |
| Amplicon/eDNA data with many singletons | Skip Chao1 OR use after careful denoising; report Good's coverage alongside | Singletons in amplicon data are dominated by PCR error, not undersampling |
| Singleton-heavy real data (f1 >> f2) | Chao1 with wide CI; cross-check with ACE | Chao1 variance grows as f1^4; ACE uses more rare-class information |
| f2 = 0 (no doubletons) | Chao1bc or jackknife1 | Original Chao1 is undefined; bias-corrected form is the standard |
| Diversity at much larger sample size than observed | Stop extrapolation at 2x reference size (the doubling rule) | iNEXT will silently extrapolate further; variance grows superlinearly beyond |
| Beta diversity for two assemblages | Sorensen or Jaccard with Baselga partition; document choice | Bray-Curtis is not a true metric and breaks some downstream methods |
| Beta diversity reported as turnover/nestedness | Run BOTH Baselga AND Podani partitions and report both | The partition is not mathematically unique; one alone hides ambiguity |
| Before PCA/RDA on community data | Hellinger transformation first | Solves double-zero problem; raw Euclidean PCA on counts is malpractice |
| Phylogenetic community structure (NRI/NTI) | SES_MPD with explicit null.model justification | Default null may not match question; document choice |
| Functional diversity (FRic) | Optimize PCoA axis count via Maire 2015 mAD; report chosen k | FRic biased by trait-axis count; defaults (k=2-3) are too few |
| Amplicon/compositional data | Either presence/absence metrics (Chao2, Sorensen) OR explicit CLR-based diversity per Gloor 2017 *Front Microbiol* 8:2224 | Hill-numbers assume absolute abundances; amplicon counts are compositional |

## Hill Numbers and Why Raw Entropies Are Not Diversities

**Goal:** Report diversity values that are interpretable as effective species counts and additive under standard partitions.

**Approach:** Compute Hill numbers `q`D at q = 0, 1, 2 (Jost 2006 *Oikos* 113:363-375; iNEXT software paper Hsieh, Ma, Chao 2016 *Methods Ecol Evol* 7:1451-1456). q controls sensitivity to rare vs common species in a continuous parametric family: q=0 weights all species equally (richness); q=1 is the geometric-mean weighting (Shannon-equivalent exp(H)); q=2 weights down rare species rapidly (Simpson-equivalent 1/D). qD has the doubling property — merging two equally diverse equally abundant assemblages exactly doubles qD. Raw Shannon and Simpson values do NOT.

```r
library(iNEXT)
library(vegan)

abundance_data <- list(
    site_A = c(100, 45, 23, 12, 8, 5, 3, 2, 1, 1),
    site_B = c(80, 60, 40, 30, 20, 15, 10, 8, 5, 3, 2, 1),
    site_C = c(200, 10, 5, 2, 1, 1, 1)
)

# Hill numbers q=0,1,2 with coverage-based rarefaction/extrapolation
# nboot=200 is the publication-quality floor; default nboot=50 is too few for CIs
result <- iNEXT(abundance_data, q = c(0, 1, 2), datatype = 'abundance', nboot = 200)

# Report effective species counts at standardized coverage (postdoc-grade default)
# coverage=0.95: 95% of individuals in the underlying community belong to detected species
est <- estimateD(abundance_data, datatype = 'abundance', base = 'coverage', level = 0.95)
est

# For vegan equivalence: numbers-equivalent of Shannon
shannon_eff <- exp(diversity(community_matrix, index = 'shannon'))
# Inverse Simpson is already in numbers-equivalent units
invsimp <- diversity(community_matrix, index = 'invsimpson')
```

## Asymptotic Richness — Chao1 is a Lower Bound, NOT a Point Estimate

**Goal:** Estimate the lower bound on true richness when sampling is incomplete and report it correctly.

**Approach:** Compute Chao1 from the singleton/doubleton ratio (Chao 1984), check that singletons are real biology rather than PCR/sequencing error, and report as a LOWER BOUND with Good's coverage to indicate sampling adequacy. Switch to ACE or jackknife1 when f2 is near zero or singletons are unreliable.

The original Chao1 derivation (Chao 1984) under a Gamma-Poisson mixture model produces a NON-PARAMETRIC LOWER BOUND on richness, not a point estimate. The bound is tight only under specific homogeneity assumptions. Reporting "Chao1 estimated richness = 320" without "at least" is widespread in published literature but statistically wrong.

```r
library(iNEXT)

# AsyEst returns Chao1 (q=0), Chao-Shannon (q=1), Chao-Simpson (q=2) with CIs
asymp <- iNEXT(abundance_data, q = c(0, 1, 2), datatype = 'abundance')$AsyEst

# CRITICAL: also report Good's coverage to indicate whether the bound is informative
# Coverage < 0.85 means heavily under-sampled; Chao1 CI will be huge and bound is uninformative
coverage <- estimateD(abundance_data, datatype = 'abundance',
                      base = 'coverage', level = 0.95)
# Inspect estimateD output's Coverage column at the OBSERVED sample size

# Singleton check: if f1 >> f2 and singletons are likely PCR artifacts (amplicon data),
# do NOT report Chao1 — it will measure "how much PCR error" not "how much undiscovered diversity"
f1_check <- sapply(abundance_data, function(x) sum(x == 1))
f2_check <- sapply(abundance_data, function(x) sum(x == 2))
cat('Singletons f1:', f1_check, '\n')
cat('Doubletons f2:', f2_check, '\n')
cat('f1^2/(2*f2) Chao1 bound term:', f1_check^2 / (2 * pmax(f2_check, 0.5)), '\n')
```

## Coverage-Based Rarefaction with the Doubling Rule

**Goal:** Compare diversity across sites at a common sampling completeness, with extrapolation bounded by statistical reliability.

**Approach:** Use iNEXT's coverage-based rarefaction-extrapolation interpolating to the minimum coverage across sites; bound extrapolation at 2x the reference sample size (Chao et al. 2014 *Ecol Monogr* 84:45-67 derive variance bounds that grow superlinearly beyond 2x).

```r
# Type 3 (diversity vs coverage) is the cross-site comparison plot
# nboot=200 minimum for publication-quality CIs (default 50 is too few)
ggiNEXT(result, type = 3) + theme_bw() +
    labs(title = 'Coverage-Based Hill-Number Diversity')

# The doubling rule: endpoint should be at most 2 * max(observed sample size)
# iNEXT default endpoint = 2 * max(sample size); do NOT override above this
# Beyond 2x, the variance estimate grows superlinearly and CIs become unreliable

# To extract numerical results at standardized coverage:
est_95 <- estimateD(abundance_data, datatype = 'abundance',
                    base = 'coverage', level = 0.95)
```

## The Double-Zero Problem and Hellinger Transformation

**Goal:** Compute community dissimilarity in a way that does not treat shared absences as evidence of similarity.

**Approach:** Apply the Hellinger transformation (Legendre & Gallagher 2001 *Oecologia* 129:271-280) before computing Euclidean distance, PCA, or RDA. This is the single most important preprocessing decision for community ordination.

Standard Euclidean distance and Pearson correlation treat "both samples have 0 abundance of species X" as evidence of similarity. In community ecology this is wrong — two deserts both lacking a rainforest species are not thereby similar. Hellinger transformation removes this artifact while preserving total-abundance information.

```r
library(vegan)

# Hellinger transformation: y_ij' = sqrt(y_ij / row_sum_i)
# Euclidean distance on Hellinger-transformed data = Hellinger distance
species_hell <- decostand(community_matrix, method = 'hellinger')

# Now PCA/RDA on the transformed matrix is biologically meaningful
pca_result <- rda(species_hell)

# Alternative: chord transformation (similar effect, slightly different scaling)
species_chord <- decostand(community_matrix, method = 'normalize')
```

## Beta Diversity Partition — Run BOTH Baselga AND Podani

For the broader "multiple meanings of beta diversity" framework, see Anderson et al. 2011 *Ecol Lett* 14:19-28.

**Goal:** Decompose total beta diversity into ecologically interpretable components, acknowledging that the partition is not mathematically unique.

**Approach:** Compute the Baselga partition (Sorensen = turnover + nestedness) with `betapart`, and the alternative Podani/Carvalho partition (richness-difference framework), and report both. The two frameworks give different ecological interpretations of the same data; presenting only one hides ambiguity.

```r
library(betapart)

pa_matrix <- ifelse(community_matrix > 0, 1, 0)

# --- Baselga partition (Baselga 2010 Glob Ecol Biogeogr 19:134-143) ---
# beta.SIM (turnover/Simpson) + beta.SNE (nestedness) = beta.SOR (total Sorensen)
pair_sor <- beta.pair(pa_matrix, index.family = 'sorensen')
multi_sor <- beta.multi(pa_matrix, index.family = 'sorensen')

# --- Abundance-based: Bray-Curtis balanced + gradient ---
# beta.bray.bal (balanced variation; analogous to turnover)
# beta.bray.gra (abundance gradient; analogous to nestedness)
pair_abund <- beta.pair.abund(community_matrix, index.family = 'bray')

# --- Podani/Carvalho framework (different decomposition of same data) ---
# Use betapart::beta.pair with the .fam family option, or carvalho package
# These produce richness-difference components instead of nestedness
# Reporting only Baselga without acknowledging Podani exists is incomplete
```

## Phylogenetic Diversity — Faith's PD, MPD, MNTD with Null-Model Choice

**Goal:** Quantify evolutionary distinctness and phylogenetic community structure with an explicit, justified null model.

**Approach:** Compute Faith's PD on a community matrix and ultrametric phylogeny (Faith 1992 *Biol Conserv* 61:1-10), then SES_MPD and SES_MNTD (Webb 2002 *Annu Rev Ecol Syst* 33:475-505) standardizing against a documented null model. The choice of null model is the dominant scientific decision — different nulls answer different ecological questions.

```r
library(picante)

# Faith's PD: sum of branch lengths spanning the focal species
# include.root=TRUE counts root branch; FALSE excludes (matters for within-clade comparisons)
faith_pd <- pd(community_matrix, phylo_tree, include.root = TRUE)

# SES_MPD with EXPLICIT null model (do not accept default silently)
# null.model='taxa.labels': shuffles species across tree, holds sample richness constant
# null.model='richness': randomizes within sample, preserves species occurrence frequencies
# null.model='independentswap': preserves both row and column sums of community matrix
# Each null answers a different question; document the choice in methods
ses_mpd_taxa <- ses.mpd(community_matrix, cophenetic(phylo_tree),
                        null.model = 'taxa.labels', runs = 999, iterations = 1000)
ses_mpd_indep <- ses.mpd(community_matrix, cophenetic(phylo_tree),
                         null.model = 'independentswap', runs = 999, iterations = 1000)

# SES_MPD < 0 (NRI > 0): phylogenetic clustering
# SES_MPD > 0 (NRI < 0): phylogenetic overdispersion
# DO NOT infer "clustering = environmental filtering" from sign alone;
# Mayfield & Levine 2010 Ecol Lett 13:1085-1093 showed competition can cluster
# when traits track phylogeny and similar species coexist via R*-rule dynamics
```

## Functional Diversity with Trait-Axis Dimensionality Optimization

**Goal:** Compute multidimensional functional diversity without inflating values via correlated trait axes.

**Approach:** Run Maire et al. 2015 *Glob Ecol Biogeogr* 24:728-740 trait-space-quality assessment (mAD metric) to choose the number of PCoA axes that minimizes deviation between original trait distances and axis-reconstructed distances. Use that k for FRic, FEve, FDiv. Default k=2-3 typically biases FRic; optimum is usually 4-6 for typical trait datasets.

```r
library(FD)
library(mFD)

# Trait dissimilarity from a trait matrix (Gower for mixed quantitative/categorical)
trait_dist <- gowdis(trait_matrix)

# mFD optimizes the number of trait axes via Maire 2015 mAD criterion
# Smaller mAD = better fidelity between trait distances and PCoA-axis distances
quality_funct_space <- quality.fspaces(trait_dist, maxdim_pcoa = 10,
                                       fdist_scaling = TRUE, fdendro = NULL)
best_k <- which.min(quality_funct_space$quality_fspaces$mad)
cat('Maire-optimal number of trait axes:', best_k, '\n')

# Compute FD with the optimal k
fd_result <- dbFD(trait_matrix, community_matrix, m = best_k, corr = 'cailliez')
fd_result$FRic   # functional richness (convex hull volume)
fd_result$FEve   # functional evenness
fd_result$FDiv   # functional divergence
```

## Per-Method Failure Modes

### Singleton-driven Chao1 inflation in amplicon data

**Trigger:** Computing Chao1 directly on ASV/OTU tables that include singletons of suspected PCR-error origin.

**Mechanism:** Chao1 assumes singletons are biologically real rare species; under that assumption, more singletons relative to doubletons signals more undiscovered diversity. PCR/sequencing error produces many singletons that look like rare species to Chao1, inflating the bound.

**Symptom:** Chao1 dramatically exceeds observed richness (e.g., Chao1 = 500 from S_obs = 100) with extremely wide confidence intervals; Good's coverage < 0.85 despite > 10,000 reads per sample.

**Fix:** Denoise first (DADA2 / UNOISE3 / swarm v2) to remove PCR-error variants, then either skip Chao1 entirely (Callahan 2017 ASV philosophy) or report observed ASV count + Good's coverage instead. Alternative: report Chao2 from incidence (presence across replicates), which is robust to PCR-error singletons.

### Rarefaction across mismatched assemblage sizes

**Trigger:** Sample-size rarefaction to the smallest assemblage when sites differ in true diversity.

**Mechanism:** A 100-read rarefaction of a 50-species community is nearly saturated (coverage approximately 99%); the same 100 reads from a 500-species community covers approximately 40% of true diversity. The two rarefied values measure different completeness levels.

**Symptom:** Rarefied richness ordering disagrees with intuitive site-by-site comparison; small-sample-size sites appear artificially equal in rarefied diversity to high-diversity sites.

**Fix:** Use coverage-based rarefaction via `estimateD(..., base = 'coverage', level = 0.95)`. The 0.95 coverage target is the modern default; 0.99 for high-precision work, 0.85 minimum for accepting a site into the comparison.

### Hellinger forgotten before PCA/RDA on community data

**Trigger:** Running `rda(species_matrix)` or `prcomp(species_matrix)` on raw species counts without prior transformation.

**Mechanism:** The double-zero problem inflates dissimilarity for sample pairs sharing many absent species. Raw-count PCA projects samples primarily by sequencing depth (PC1 = library size proxy), not by community composition.

**Symptom:** PC1 axis correlates strongly with sample read totals; biological gradients appear only on PC3 or later; ordination is dominated by sites with extreme sample sizes.

**Fix:** `decostand(matrix, method = 'hellinger')` before ordination. Always.

### FRic inflation from collinear trait axes

**Trigger:** Computing FRic from 8-10 raw correlated traits without dimensionality optimization.

**Mechanism:** FRic = convex-hull volume in trait PCoA space. Adding correlated traits increases the apparent dimensionality of the trait space without adding ecological information; convex-hull volume inflates accordingly.

**Symptom:** FRic increases when adding new correlated traits to the analysis; FRic comparisons across studies that use different trait counts are inconsistent.

**Fix:** Run `mFD::quality.fspaces()` and use the mAD-optimal k. Report k in methods.

### SES_MPD interpretation by sign alone

**Trigger:** Reporting "SES_MPD < 0 indicates environmental filtering" without testing alternative explanations.

**Mechanism:** Mayfield & Levine 2010 *Ecol Lett* 13(9):1085-1093 showed competition can produce phylogenetic clustering when ecologically similar species (which tend to be closely related) coexist via R*-rule trait differences. The clustering = filtering / overdispersion = competition dichotomy from Webb 2002 is incomplete.

**Symptom:** Phylogenetic clustering interpretation is challenged at review; trait-similarity vs phylogenetic-similarity correlation has not been examined.

**Fix:** Report SES_MPD with one explicit null model AND test trait conservatism (Blomberg's K, Pagel's lambda) — if traits track phylogeny strongly, clustering may reflect either filtering OR competition; cite Mayfield & Levine 2010 in interpretation.

## Quantitative Thresholds

| Threshold | Value | Source / rationale |
|-----------|-------|-------------------|
| Coverage target for cross-site comparison | C = 0.95 | Postdoc-grade convention; 0.99 for high-precision, 0.85 minimum to accept site |
| iNEXT extrapolation limit | endpoint <= 2x reference sample size | Chao et al. 2014 doubling rule; variance grows superlinearly beyond |
| iNEXT bootstrap floor for CIs | nboot = 200 | Default 50 is too few for publication-quality CIs |
| Chao1 reliability | f2 > 0 AND singletons biological | If f2 = 0, switch to Chao1bc or jackknife1 |
| Hellinger before ordination | Always for community data | Legendre & Gallagher 2001; non-negotiable |
| SES_MPD significance | |SES| > 1.96 (two-tailed) | Standard 0.05 alpha; report alongside explicit null model |
| Functional-diversity axis count k | Maire 2015 mAD-optimal | Default k=2-3 too few; typically 4-6 optimal |
| Phylogenetic-tree requirement | Ultrametric | If not, `ape::chronos()` or BEAST-based dating |

## Common errors

| Error | Cause | Solution |
|-------|-------|----------|
| Chao1 reports infinity or NaN | f2 = 0 (no doubletons) | Use Chao1bc form or jackknife1 |
| iNEXT extrapolation curve flat then explodes | Extrapolated beyond doubling-rule limit | Set endpoint <= 2 * max(sample sizes) |
| Hellinger PCA gives flat results | Decostand not applied or applied to wrong axis | `decostand(matrix, method = 'hellinger')` rows = sites |
| ses.mpd returns all p-values approximately 0.5 | Wrong null model for question (e.g., `taxa.labels` on a single-richness dataset) | Choose null that varies the quantity tested |
| FRic dramatically increases with new traits | Correlated trait axes inflating convex hull | Optimize axis count with mFD::quality.fspaces |
| beta.multi returns NaN for nestedness | Communities entirely disjoint (no shared species) | beta.SNE -> 0 trivially; interpret as pure turnover |
| Bray-Curtis flagged for triangle-inequality violation | Bray-Curtis is not a true metric | Switch to Sorensen (a metric) for downstream methods requiring metricity |

## References

- Chao A, Jost L (2012) Coverage-based rarefaction and extrapolation. *Ecology* 93(12):2533-2547. doi:10.1890/11-1952.1
- Chao A, Gotelli NJ, Hsieh TC, Sander EL, Ma KH, Colwell RK, Ellison AM (2014) Rarefaction and extrapolation with Hill numbers. *Ecol Monogr* 84(1):45-67. doi:10.1890/13-0133.1
- Hsieh TC, Ma KH, Chao A (2016) iNEXT: an R package for rarefaction and extrapolation of species diversity. *Methods Ecol Evol* 7(12):1451-1456. doi:10.1111/2041-210X.12613
- Jost L (2006) Entropy and diversity. *Oikos* 113(2):363-375. doi:10.1111/j.2006.0030-1299.14714.x
- Faith DP (1992) Conservation evaluation and phylogenetic diversity. *Biol Conserv* 61(1):1-10. doi:10.1016/0006-3207(92)91201-3
- Legendre P, Gallagher ED (2001) Ecologically meaningful transformations for ordination. *Oecologia* 129(2):271-280. doi:10.1007/s004420100716
- Baselga A (2010) Partitioning the turnover and nestedness components of beta diversity. *Glob Ecol Biogeogr* 19(1):134-143. doi:10.1111/j.1466-8238.2009.00490.x
- Anderson MJ, Crist TO, Chase JM et al. (2011) Navigating the multiple meanings of beta diversity. *Ecol Lett* 14(1):19-28. doi:10.1111/j.1461-0248.2010.01552.x
- Webb CO, Ackerly DD, McPeek MA, Donoghue MJ (2002) Phylogenies and community ecology. *Annu Rev Ecol Syst* 33:475-505. doi:10.1146/annurev.ecolsys.33.010802.150448
- Mayfield MM, Levine JM (2010) Opposing effects of competitive exclusion on phylogenetic community structure. *Ecol Lett* 13(9):1085-1093. doi:10.1111/j.1461-0248.2010.01509.x
- Maire E, Grenouillet G, Brosse S, Villeger S (2015) How many dimensions are needed to accurately assess functional diversity? *Glob Ecol Biogeogr* 24(6):728-740. doi:10.1111/geb.12299
- Chao A (1984) Nonparametric estimation of the number of classes in a population. *Scand J Stat* 11(4):265-270
- Gloor GB, Macklaim JM, Pawlowsky-Glahn V, Egozcue JJ (2017) Microbiome datasets are compositional: and this is not optional. *Front Microbiol* 8:2224. doi:10.3389/fmicb.2017.02224

## Related Skills

- ecological-genomics/edna-metabarcoding - Generate ASV/species tables prior to diversity analysis
- ecological-genomics/community-ecology - Constrained ordination, indicator species, PERMANOVA on transformed data
- microbiome/diversity-analysis - 16S clinical microbiome diversity metrics with compositional considerations
- data-visualization/ggplot2-fundamentals - Customize diversity plots and rarefaction curves
- phylogenetics/tree-io - Ultrametric tree preparation for PD/MPD/MNTD
<!-- END FILE: ecological-genomics/biodiversity-metrics/SKILL.md -->

## 子目录：ecological-genomics/community-ecology

<!-- BEGIN FILE: ecological-genomics/community-ecology/SKILL.md -->
---
name: bio-ecological-genomics-community-ecology
description: Analyzes species-environment relationships with constrained ordination (CCA, RDA, db-RDA), variance partitioning, indicator species (indicspecies IndVal.g group-equalized), PERMANOVA paired MANDATORILY with PERMDISP (Anderson & Walsh 2013; dispersion confounds centroid tests), Joint Species Distribution Models (HMSC, sjSDM, gjam) with explicit rejection of "residual covariance equals biotic interaction", phylogenetic community ecology (SES_MPD/MNTD), trait-environment via RLQ + fourth-corner with corrected modeltype=6 (Dray 2014), bipartite network metrics (NODF, modularity) with curveball null (Strona 2014), and Mantel-test replacements (dbRDA, GDM) for spatial data. Use when testing how environmental gradients structure communities, identifying habitat indicator taxa, partitioning variance among predictors, deciding whether PERMANOVA significance is location vs dispersion, picking among HMSC/sjSDM/gjam, or replacing Mantel tests for landscape data.
tool_type: r
primary_tool: vegan
---

## Version Compatibility

Reference examples tested with: vegan 2.6+, indicspecies 1.7+, Hmsc 3.0+, sjSDM 1.0+, ade4 1.7+, picante 1.8+, ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Community Ecology

**"Test how environmental gradients structure my species communities"** -> Constrained ordination (CCA / RDA / db-RDA) with explicit dispersion testing alongside PERMANOVA, indicator-species analysis with group-size correction, Joint Species Distribution Models for residual covariance and prediction, and trait-environment testing with statistically corrected permutation schemes.
- R: `vegan::rda()`, `vegan::dbrda()`, `vegan::adonis2()` for ordination and PERMANOVA
- R: `vegan::betadisper()` for the mandatory PERMDISP companion to PERMANOVA
- R: `Hmsc` or `sjSDM` for joint species distribution modeling
- R: `indicspecies::multipatt(..., func = 'IndVal.g')` for indicator species

## The Single Most Important Modern Insight -- Always run PERMDISP alongside PERMANOVA

Anderson & Walsh 2013 *Ecol Monogr* 83(4):557-574 established that PERMANOVA's pseudo-F is **sensitive to dispersion heterogeneity** — a significant PERMANOVA can reflect centroid difference, dispersion difference, or both. **Running PERMANOVA without PERMDISP is the single most common methodological failure in community-ecology papers.** If `betadisper` is significant alongside a significant PERMANOVA, the location-difference conclusion is not supported by the data alone; the two could be entirely a dispersion artifact.

A second cornerstone insight: residual species-species covariance in Joint Species Distribution Models is NOT a clean estimator of biotic interaction (Pollock 2014, reaffirmed by Zurell 2018 and Poggiato 2021). It reflects unmeasured covariates, dispersal limitation, sampling artifacts, AND any genuine biotic interactions, in unknown proportions. Skills that interpret residual covariance as interaction are over-interpreting.

## Algorithmic Taxonomy

| Method | Estimand | Strength | Fails when |
|--------|----------|----------|------------|
| CCA | Species-environment unimodal | Standard for chi-square data; fits bell-shaped responses | Linear gradients (use RDA); does not handle short gradients well |
| RDA | Species-environment linear | High power with short gradients; Hellinger-friendly | Long unimodal gradients (>3 SD DCA axis 1); needs no missing data |
| db-RDA / capscale | Constrained ordination on any distance | Flexible (Bray-Curtis, Sorensen, weighted Unifrac); dispersion-robust | Less power than RDA for purely linear gradients |
| PERMANOVA (adonis2) | Centroid difference among groups | Non-parametric; handles any dissimilarity | Sensitive to dispersion difference — MUST run PERMDISP alongside |
| PERMDISP (betadisper) | Dispersion difference among groups | Tests the confound that contaminates PERMANOVA | Low power with small N; report alongside PERMANOVA |
| ANOSIM | Group-difference test | Legacy familiarity | Worse than PERMANOVA for the same use case; biased by unbalanced N |
| Mantel test | Correlation between two distance matrices | Conceptually simple | Low power under spatial autocorrelation; biased; replace with dbRDA or GDM |
| Partial Mantel | Correlation controlling for a third matrix | Conceptually simple | INFLATES Type I error under autocorrelation (worse than basic Mantel) |
| HMSC (Helsinki tradition) | Bayesian JSDM with phylogeny + traits + spatial | Rigorous; ecological-theory priors | Slow for S > 500 species |
| sjSDM (Pichler & Hartig) | Latent-variable-free JSDM via MC + elastic net | Orders of magnitude faster; high-S friendly | Less explicit interpretation than HMSC |
| gjam | Cross-data-type JSDM (counts, presence, continuous) | Integrates heterogeneous data | Different output structure than HMSC; not directly comparable |
| IndVal (Dufrene-Legendre) | Species-group association | Combines specificity AND fidelity | Biased by group size unless `func='IndVal.g'` |
| SES_MPD / SES_MNTD | Phylogenetic structure vs null | Tests whether communities are clustered or overdispersed | Interpretation of sign requires trait-conservatism check (Mayfield & Levine 2010) |
| RLQ + fourth-corner | Trait-environment relationship | Tests species-trait response to environment | Default modeltype gives inflated Type I; use modeltype=6 |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Unimodal species responses, gradient > 3 SD (DCA axis 1) | CCA | Linear assumption fails for long gradients |
| Linear species responses, gradient <= 3 SD | RDA on Hellinger-transformed data | RDA assumes linearity; Hellinger solves double-zero problem |
| Bray-Curtis or other non-Euclidean distance preferred | db-RDA | Handles any distance metric while preserving constrained-ordination interpretation |
| Test "do these groups differ in community composition" | PERMANOVA (adonis2) AND PERMDISP (betadisper) | Never PERMANOVA alone; dispersion confound is non-negotiable |
| ANOSIM out of habit | Use PERMANOVA + PERMDISP instead | ANOSIM is biased by unbalanced N and dispersion |
| Mantel test for landscape genetics | dbRDA with spatial covariates OR GDM | Mantel has low power; partial Mantel inflates Type I |
| Joint species modeling with traits and phylogeny | HMSC (S < 500); sjSDM (S > 500) | HMSC encodes theory in priors; sjSDM is the only scalable option for high-S |
| Multi-species "association" structure | JSDM residual covariance | Interpret as ANY of (interaction, shared response to unmeasured driver, dispersal, sampling), NOT pure interaction |
| Indicator species with unbalanced group sizes | `multipatt(..., func = 'IndVal.g')` | `IndVal` is biased by group size; group-equalized form corrects |
| Phylogenetic community structure | SES_MPD with EXPLICIT null model + trait-conservatism test | Cite Mayfield & Levine 2010 for the "clustering = filtering" interpretation trap |
| Trait-environment hypothesis | RLQ + fourth-corner with `modeltype=6` | Default `modeltype=2` or `modeltype=4` gives inflated Type I error |
| Bipartite network nestedness/modularity | NODF2 + modularity with `curveball` null randomization | Strona 2014 curveball is exponentially faster and unbiased for binary matrices |

## CCA vs RDA — Gradient-Length Decision

**Goal:** Choose between unimodal (CCA) and linear (RDA) constrained ordination based on the dominant gradient length in the species data.

**Approach:** Run a Detrended Correspondence Analysis (DCA) on the raw community matrix; use the axis-1 SD length as the gradient-length metric. > 3 SD suggests unimodal CCA; < 3 SD suggests linear RDA on Hellinger-transformed data; 2-3 SD is a gray zone where either is defensible.

```r
library(vegan)

# Step 1: Check gradient length
dca <- decorana(species_matrix)
dca  # axis 1 length in SD units

# Step 2a: Long gradient -> CCA
cca_result <- cca(species_matrix ~ temperature + precipitation + pH + elevation,
                  data = env_data)
anova(cca_result, by = 'margin', permutations = 999)

# Step 2b: Short gradient -> RDA with Hellinger transformation
# Hellinger (Legendre & Gallagher 2001) is MANDATORY before RDA on community data
species_hell <- decostand(species_matrix, method = 'hellinger')
rda_result <- rda(species_hell ~ temperature + precipitation + pH + elevation,
                  data = env_data)
RsquareAdj(rda_result)$adj.r.squared
anova(rda_result, by = 'margin', permutations = 999)

# Forward selection with adjusted R-squared criterion (Peres-Neto 2006 Ecology 87:2614)
rda_null <- rda(species_hell ~ 1, data = env_data)
rda_full <- rda(species_hell ~ ., data = env_data)
rda_sel <- ordiR2step(rda_null, scope = formula(rda_full),
                      direction = 'forward', permutations = 999)

# VIF check: > 10 indicates problematic multicollinearity
vif.cca(rda_sel)
```

## PERMANOVA with the Mandatory PERMDISP Companion

**Goal:** Test whether community composition differs across groups while detecting the dispersion-heterogeneity confound.

**Approach:** Run `adonis2` (modern PERMANOVA per Anderson 2001 *Austral Ecol*) on Hellinger or Bray-Curtis distances; THEN run `betadisper` (PERMDISP per Anderson 2006 *Biometrics*) to test whether group dispersions are unequal. Report BOTH results. If betadisper is significant, the adonis2 conclusion of centroid difference is not supported — the apparent "group difference" may be entirely a dispersion artifact.

```r
library(vegan)

# Distance matrix
bray_dist <- vegdist(species_matrix, method = 'bray')

# PERMANOVA via adonis2 (modern API; adonis() is deprecated)
# by='margin' for unbalanced designs (sequential SS gives wrong result)
permanova <- adonis2(bray_dist ~ habitat + soil_pH, data = env_data,
                     by = 'margin', permutations = 999)
permanova

# MANDATORY companion: PERMDISP via betadisper
# Tests homogeneity of multivariate dispersions across groups
disp <- betadisper(bray_dist, env_data$habitat)
disp_test <- permutest(disp, permutations = 999)
disp_test

# Interpretation rule:
# PERMANOVA p < 0.05 AND betadisper p > 0.05 -> location difference is real
# PERMANOVA p < 0.05 AND betadisper p < 0.05 -> CONFOUNDED, cannot conclude location difference
# PERMANOVA p > 0.05 -> no group difference detected

# Visualize dispersions
plot(disp)
boxplot(disp)

# For pairwise group comparisons, do NOT use Bonferroni-corrected pairwise PERMANOVA
# (permutation tests with overlapping sets do not give nominal FWER from Bonferroni);
# use pairwiseAdonis::pairwise.adonis2 with FDR correction instead
# install.packages('pairwiseAdonis')
```

## Joint Species Distribution Models — HMSC vs sjSDM

**Goal:** Model species occurrences jointly to capture environmental responses, traits, phylogeny, and residual covariance among species.

**Approach:** For S < 500 species with rich theory and traits/phylogeny: use HMSC (Ovaskainen 2017 *Ecol Lett* 20:561-576; current R package Tikhonov 2020 *Methods Ecol Evol* 11:442-447) for Bayesian inference with explicit ecological priors. For S > 500 species (modern metabarcoding datasets): use sjSDM (Pichler & Hartig 2021 *Methods Ecol Evol* 12:2159-2173) which is orders of magnitude faster via Monte Carlo approximation of the joint likelihood with elastic-net regularization. The Wilkinson 2019 *Methods Ecol Evol* 10:198-211 benchmark is essential reading before picking among HMSC, sjSDM, gjam, and BayesComm. **Do NOT interpret residual species-species covariance as biotic interaction** (see Zurell 2018 *Ecography* 41:1812-1819; Poggiato 2021 *Trends Ecol Evol* 36:391-401).

```r
library(Hmsc)

# HMSC for moderate-S Bayesian JSDM
# X: site x environment data
# Y: site x species presence-absence or abundance
# distr: 'probit' for presence-absence; 'lognormal poisson' for counts
m <- Hmsc(Y = species_matrix, XData = env_data, XFormula = ~ temperature + soil_pH,
         distr = 'probit')

# Sample posterior (production runs need thin >= 100, transient >= 1000, samples >= 1000)
m <- sampleMcmc(m, thin = 10, samples = 1000, transient = 5000, nChains = 4)

# Variance partitioning into fixed (environment), random (latent factors), traits, phylogeny
VP <- computeVariancePartitioning(m)
plotVariancePartitioning(m, VP = VP)

# Predict to new environment
pred <- predict(m, XData = new_env_data, expected = TRUE)

# For S > 500: switch to sjSDM
# library(sjSDM)
# m_sj <- sjSDM(Y = species_matrix, env = linear(env_data, ~ temperature + soil_pH),
#               family = binomial('probit'))
# summary(m_sj); plot(m_sj)
```

## Indicator Species with Group-Size Correction

**Goal:** Identify species statistically associated with site groups using an indicator value that combines specificity and fidelity, corrected for unequal group sizes.

**Approach:** Run `indicspecies::multipatt` with `func = 'IndVal.g'` (the group-size-equalized form per De Caceres & Legendre 2009 *Ecology* 90:3566-3574). The original `IndVal` is biased toward larger groups; the `.g` form corrects this. For continuous-vs-categorical or rank-based associations, use `func = 'r.g'` (point-biserial correlation, group-equalized).

```r
library(indicspecies)

# IndVal.g: group-size-equalized indicator value
# multipatt tests species-group associations with permutation
# duleg=TRUE: tests only single-group associations (not combinations)
# duleg=FALSE: tests species against all group combinations (more powerful but more tests)
mp <- multipatt(species_matrix, site_groups,
                func = 'IndVal.g',       # Group-equalized; NOT 'IndVal' (biased)
                duleg = TRUE,
                control = how(nperm = 999))

summary(mp, alpha = 0.05)

# Extract significant indicators sorted by p-value
sig <- mp$sign[!is.na(mp$sign$p.value) & mp$sign$p.value < 0.05, ]
sig[order(sig$p.value), ]
```

## Mantel Replacement — dbRDA with Spatial Covariates

**Goal:** Test whether community/genetic distance correlates with environmental distance while controlling for spatial autocorrelation, replacing the low-power and bias-prone Mantel framework.

**Approach:** Use db-RDA with spatial predictors (PCNM eigenvectors or raw coordinates) as `Condition()` (Legendre & Fortin 2010 *Mol Ecol Resour* 10:831-844). Partial Mantel inflates Type I error under autocorrelation — do not use for landscape data.

```r
library(vegan)
library(adespatial)

# Build spatial predictors: PCNM (principal coordinates of neighbor matrices)
geo_dist <- dist(coords[, c('longitude', 'latitude')])
pcnm <- pcnm(geo_dist)
pcnm_vars <- pcnm$vectors  # significant axes

# db-RDA controlling for spatial structure
dbrda_result <- dbrda(bray_dist ~ temperature + precipitation +
                       Condition(as.matrix(pcnm_vars)),
                      data = env_data, add = 'lingoes')

# Test marginal significance of environment AFTER conditioning out space
anova(dbrda_result, by = 'margin', permutations = 999)

# DO NOT use partial Mantel for this question; cite Legendre & Fortin 2010
```

## Per-Method Failure Modes

### PERMANOVA significant, betadisper also significant -> conclusion not supported

**Trigger:** Reporting PERMANOVA p < 0.05 as evidence of "community composition differs across groups" without running betadisper, OR running betadisper and finding it significant but ignoring the result.

**Mechanism:** PERMANOVA's pseudo-F responds to BOTH centroid shifts AND dispersion heterogeneity (Anderson & Walsh 2013). When groups differ in dispersion but not centroid, PERMANOVA can return p < 0.05 from the dispersion difference alone.

**Symptom:** Reviewer asks "was dispersion checked?"; PCoA visualization shows overlapping centroids but one group is more dispersed; betadisper p < 0.05.

**Fix:** Report both PERMANOVA and betadisper. If betadisper is significant, the conclusion must be reframed: "Groups differ in either centroid or dispersion, with dispersion heterogeneity present." Consider db-RDA which is more dispersion-robust.

### Mantel test reports low p but reflects spatial autocorrelation

**Trigger:** Using Mantel or partial Mantel to test "is genetic distance correlated with environmental distance" in a spatially-structured landscape.

**Mechanism:** Mantel statistics are biased downward by spatial autocorrelation in either distance matrix (Legendre & Fortin 2010). Partial Mantel further inflates Type I error rates under autocorrelation (see Guillot & Rousset 2013 *Methods Ecol Evol* 4:336-344 for the formal demonstration).

**Symptom:** Mantel p < 0.001 but no detectable signal when re-tested with dbRDA conditioning on geographic distance.

**Fix:** Use db-RDA with PCNM spatial eigenvectors as `Condition()`, OR GDM (Generalized Dissimilarity Modeling).

### JSDM residual covariance interpreted as biotic interaction

**Trigger:** Reporting "species A and species B have residual covariance after fitting environment, indicating biotic interaction."

**Mechanism:** Residual covariance after environmental fitting reflects (a) unmeasured covariates, (b) dispersal limitation, (c) sampling artifacts, (d) shared response to unmeasured drivers, AND (e) any genuine biotic interactions, in unknown proportions. Without manipulative or independent corroboration, the interaction signal cannot be isolated.

**Symptom:** Reviewer challenges "interaction" interpretation; sensitivity tests with different environmental specifications change the residual structure dramatically.

**Fix:** Report residual covariance descriptively ("residual association after fitting environment"), explicitly acknowledge alternative explanations, and cite Zurell 2018 or Poggiato 2021 for the interpretation caveat.

### IndVal biased by unequal group sizes

**Trigger:** Running `multipatt(..., func = 'IndVal')` with strongly unbalanced groups.

**Mechanism:** The original IndVal index from Dufrene & Legendre 1997 is biased toward larger groups because larger groups have higher average occupancy by chance.

**Symptom:** All indicators are assigned to the largest group; small-group indicators are undetected.

**Fix:** Use `func = 'IndVal.g'` (group-equalized) per De Caceres & Legendre 2009. The `.g` correction is the modern default.

### SES_MPD sign interpreted as filtering vs competition without trait check

**Trigger:** Reporting "SES_MPD < 0 (NRI > 0) indicates environmental filtering" without testing whether traits track phylogeny.

**Mechanism:** Mayfield & Levine 2010 *Ecol Lett* 13:1085-1093 showed competition can produce phylogenetic clustering (not just overdispersion) when ecologically similar species coexist via R*-rule trait differences. The Webb 2002 sign-to-process mapping is incomplete.

**Symptom:** Trait-similarity vs phylogenetic-similarity correlation has not been examined; reviewer asks about Mayfield-Levine alternative.

**Fix:** Compute Blomberg's K AND Pagel's lambda; if traits track phylogeny strongly, the clustering signal could be either filtering OR competition. Cite Mayfield & Levine 2010 in interpretation.

## Quantitative Thresholds

| Threshold | Value | Source / rationale |
|-----------|-------|-------------------|
| DCA gradient length | < 3 SD: RDA; > 3 SD: CCA; 2-3 SD: gray zone | Standard ordination decision rule |
| VIF | > 10: collinearity problem | Hair et al. ecology convention |
| PERMANOVA + PERMDISP rule | Report BOTH; if both p < 0.05, location difference not supported | Anderson & Walsh 2013 |
| RDA R^2 reporting | Adjusted R^2 (`RsquareAdj$adj.r.squared`) | Peres-Neto 2006 Ecology 87:2614 |
| HMSC MCMC settings | Thin 100, samples 1000, transient 1000, chains >= 2 | Hmsc tutorial recommendations |
| Sample-size rule for sjSDM | Used when S > 500 species | HMSC computational practicality |
| IndVal significance | p < 0.05 after 999 permutations | Standard alpha; use FDR for many comparisons |
| Bootstrap iterations | nperm = 999 minimum for tests | Standard for permutation tests |

## Common errors

| Error | Cause | Solution |
|-------|-------|----------|
| adonis() doesn't accept new arguments | adonis() deprecated in vegan 2.6+ | Use adonis2() |
| betadisper produces NA | Unequal group sizes with very small N | Increase replicates per group |
| PCoA shows no group separation despite p < 0.05 | Dispersion-driven PERMANOVA significance | Report betadisper alongside |
| HMSC convergence diagnostics flag | Insufficient thinning/transient | Increase thin and transient parameters |
| sjSDM error about GPU/CUDA | Default device misconfigured | Set `device='cpu'` if no GPU |
| multipatt all p-values 1.0 | Group factor not a factor | `as.factor(site_groups)` |
| IndVal flags only large-group species | Using `func='IndVal'` not `'IndVal.g'` | Switch to `IndVal.g` |
| dbRDA negative eigenvalues warning | Non-Euclidean distance with no correction | Add `add = 'lingoes'` |
| Mantel test always significant | Spatial autocorrelation inflating correlation | Switch to dbRDA with spatial covariates |

## References

- Anderson MJ (2001) A new method for non-parametric multivariate analysis of variance. *Austral Ecol* 26(1):32-46. doi:10.1111/j.1442-9993.2001.01070.pp.x
- Anderson MJ (2006) Distance-based tests for homogeneity of multivariate dispersions. *Biometrics* 62(1):245-253. doi:10.1111/j.1541-0420.2005.00440.x
- Anderson MJ, Walsh DCI (2013) PERMANOVA, ANOSIM, and the Mantel test in the face of heterogeneous dispersions. *Ecol Monogr* 83(4):557-574. doi:10.1890/12-2010.1
- Legendre P, Fortin M-J (2010) Comparison of the Mantel test and alternative approaches for detecting complex multivariate relationships. *Mol Ecol Resour* 10(5):831-844. doi:10.1111/j.1755-0998.2010.02866.x
- Legendre P, Gallagher ED (2001) Ecologically meaningful transformations for ordination of species data. *Oecologia* 129(2):271-280. doi:10.1007/s004420100716
- Peres-Neto PR, Legendre P, Dray S, Borcard D (2006) Variation partitioning of species data matrices. *Ecology* 87(10):2614-2625. doi:10.1890/0012-9658(2006)87[2614:VPOSDM]2.0.CO;2
- Dufrene M, Legendre P (1997) Species assemblages and indicator species. *Ecol Monogr* 67(3):345-366. doi:10.1890/0012-9615(1997)067[0345:SAAIST]2.0.CO;2
- De Caceres M, Legendre P (2009) Associations between species and groups of sites. *Ecology* 90(12):3566-3574. doi:10.1890/08-1823.1
- Pollock LJ, Tingley R, Morris WK et al. (2014) Joint Species Distribution Model (JSDM). *Methods Ecol Evol* 5(5):397-406. doi:10.1111/2041-210X.12180
- Ovaskainen O, Tikhonov G, Norberg A et al. (2017) Hierarchical Modelling of Species Communities (HMSC). *Ecol Lett* 20(5):561-576. doi:10.1111/ele.12757
- Tikhonov G, Opedal OH, Abrego N et al. (2020) Joint species distribution modelling with the R-package Hmsc. *Methods Ecol Evol* 11(3):442-447. doi:10.1111/2041-210X.13345
- Pichler M, Hartig F (2021) A new joint species distribution model for faster and more accurate inference. *Methods Ecol Evol* 12(11):2159-2173. doi:10.1111/2041-210X.13687
- Wilkinson DP, Golding N, Guillera-Arroita G et al. (2019) Comparison of joint species distribution models. *Methods Ecol Evol* 10(2):198-211. doi:10.1111/2041-210X.13106
- Zurell D, Pollock LJ, Thuiller W (2018) Do joint species distribution models reliably detect interspecific interactions from co-occurrence data in homogenous environments? *Ecography* 41(11):1812-1819. doi:10.1111/ecog.03315
- Poggiato G, Munkemuller T, Bystrova D et al. (2021) On the interpretations of joint modeling in community ecology. *Trends Ecol Evol* 36(5):391-401. doi:10.1016/j.tree.2021.01.002
- Guillot G, Rousset F (2013) Dismantling the Mantel tests. *Methods Ecol Evol* 4(4):336-344. doi:10.1111/2041-210x.12018
- Webb CO, Ackerly DD, McPeek MA, Donoghue MJ (2002) Phylogenies and community ecology. *Annu Rev Ecol Syst* 33:475-505. doi:10.1146/annurev.ecolsys.33.010802.150448
- Mayfield MM, Levine JM (2010) Opposing effects of competitive exclusion on phylogenetic community structure. *Ecol Lett* 13(9):1085-1093. doi:10.1111/j.1461-0248.2010.01509.x
- Dray S, Choler P, Doledec S et al. (2014) Combining fourth-corner and RLQ methods. *Ecology* 95(1):14-21. doi:10.1890/13-0196.1
- Strona G, Nappo D, Boccacci F, Fattorini S, San-Miguel-Ayanz J (2014) A fast and unbiased procedure to randomize ecological binary matrices. *Nat Commun* 5:4114. doi:10.1038/ncomms5114

## Related Skills

- ecological-genomics/biodiversity-metrics - Alpha/beta diversity and Hill numbers prior to ordination
- ecological-genomics/edna-metabarcoding - Generate community data from environmental samples
- ecological-genomics/landscape-genomics - Genotype-environment associations (genetic analog of GEA)
- microbiome/diversity-analysis - Unconstrained ordination alternative for 16S microbiome
- data-visualization/ggplot2-fundamentals - Customize triplots, ordination plots, and indicator-species visualizations
<!-- END FILE: ecological-genomics/community-ecology/SKILL.md -->

## 子目录：ecological-genomics/conservation-genetics

<!-- BEGIN FILE: ecological-genomics/conservation-genetics/SKILL.md -->
---
name: bio-ecological-genomics-conservation-genetics
description: Assesses genetic health of populations for conservation with Ne estimation across time horizons (LDNe NeEstimator V2 option-file API + SNeP physical-linkage correction; recent trajectory via GONE/GONE2; deep history via Stairway Plot 2 / dadi / fastsimcoal2 / PSMC), F-statistics, runs of homozygosity binned by length class to date inbreeding, genetic-load decomposition (Bertorelle 2022 realized vs masked), the modern 100/1000 Ne rule (Frankham 2014), Ne/Nc 2-6 orders of magnitude in marine fish (Hauser & Carvalho 2008), tree-sequence forward simulations (SLiM 4 + pyslim + tskit), and the Sukumaran-Knowles caveat against MSC methods for management-unit definition. Use when estimating Ne by time horizon, detecting inbreeding via F_ROH, decomposing genetic load, justifying conservation thresholds, distinguishing ESU/MU/DPS, configuring NeEstimator V2, or correcting LDNe physical linkage.
tool_type: mixed
primary_tool: hierfstat
---

## Version Compatibility

Reference examples tested with: hierfstat 0.5+, adegenet 2.1+, detectRUNS 2.0+, poppr 2.9+, NeEstimator V2.1+, GONE2, SNeP 1.1+, SLiM 4+, msprime 1.3+, bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Conservation Genetics

**"Assess the genetic health of my endangered population"** -> Estimate Ne by time horizon (contemporary LD, recent trajectory, deep demographic history), measure inbreeding via F_ROH with length-class thresholds, decompose realized vs masked genetic load, and interpret against the modern 100/1000 Ne rule.
- R: `hierfstat::basic.stats()` for F-statistics and diversity
- R: `detectRUNS::consecutiveRUNS.run()` or `bcftools roh -G30` for ROH detection
- CLI: `Ne2.exe option_file.ne2` for NeEstimator V2 contemporary Ne (option-file driven, NOT CLI flags)
- CLI: `gone2` for recent Ne trajectory from genome-wide LD (requires populated cM map)

## The Single Most Important Modern Insight -- There is No Single Best Ne Estimator

The most common methodological failure in conservation genetics is treating "Ne" as one quantity. **It is not.** Each Ne estimator captures a different time horizon with different biases:
- **LD-based (NeEstimator V2, Waples 2006)**: Last 1-few generations; biased downward at small N
- **GONE / GONE2 (Santiago 2020)**: Recent 100-200 generations trajectory; requires populated cM genetic map
- **Heterozygote-excess**: Last 1 generation only; very low power
- **Temporal (Jorde-Ryman)**: Between two time-sampled cohorts
- **Stairway Plot 2 / dadi / fastsimcoal2**: 10^3 to 10^5 generations from SFS
- **PSMC**: 10^4 to 10^6 generations from single high-coverage genome

A second cornerstone: **Ne/Nc ratio is NOT 0.1 universally.** Frankham 1995 reported a median of 0.1 in vertebrates, but Hauser & Carvalho 2008 *Fish Fish* 9:333-362 documented Ne/Nc spanning 2-6 orders of magnitude smaller than census (i.e., 10^-2 to 10^-6) in marine fish with sex-biased and sweepstakes-recruitment reproduction. Conservation papers that assume Ne/Nc = 0.1 are wrong for many taxa.

A third: **the 50/500 rule was revised to 100/1000** by Frankham et al. 2014 *Biol Conserv* 170:56-63. The 50/500 numbers came from 1980 and underestimate the Ne needed for adaptive maintenance. The modern thresholds are Ne >= 100 for short-term inbreeding-fitness protection and Ne >= 1000 for long-term adaptive potential.

## Algorithmic Taxonomy

| Method | Time horizon | Strength | Bias mode |
|--------|--------------|----------|-----------|
| LDNe (NeEstimator V2 LD method) | Last 1-few generations | Single sample; SNP-friendly | Biased downward at small N; sensitive to physical linkage |
| SNeP (LD with physical-linkage correction) | Last 1-few generations | Corrects LDNe for chromosomal linkage in genomic data | Requires phased genotypes |
| GONE / GONE2 | Recent 100-200 generations | Detects bottleneck/expansion trajectory | Requires populated cM genetic map column (NOT physical position) |
| Heterozygote-excess | Last 1 generation | Detects recent bottleneck | Very low power; requires high heterozygosity |
| Temporal (Jorde-Ryman, Pollak) | Between two cohorts | Direct drift estimate | Requires temporal samples |
| Sibship (Wang COLONY) | Current generation | Pedigree-based from kinship | Computationally expensive |
| dadi (Gutenkunst 2009) | 10^3 - 10^5 generations | Diffusion SFS-based; analytical | Local-optima trap; <=3 populations practical |
| fastsimcoal2 (Excoffier 2013) | 10^3 - 10^5 generations | Simulation-based composite-likelihood | Optimization needs >= 50 replicates |
| moments (Jouganous 2017) | 10^3 - 10^5 generations | Moment-based ODE; faster than dadi | Same dimensionality limits |
| momi2 (Kamm 2020) | 10^3 - 10^5 generations | Analytical SFS via moments | Stiff at very recent times |
| Stairway Plot 2 | 10^3 - 10^5 generations | Folded SFS; no parametric model | Requires explicit mutation rate and generation time |
| PSMC | 10^4 - 10^6 generations | Whole-genome pairwise coalescent | Requires >= 20x WGS coverage |
| MSMC2 | Multi-individual deep coalescent | Better recent resolution than PSMC | Requires phased data; computational |
| msprime (Kelleher 2016) | Simulation (not inference) | Gold-standard neutral simulator | Used to generate data under a fitted model |
| SLiM 3/4 (Haller & Messer 2019) | Forward simulation | Non-WF, age structure, spatial | Eidos scripting; tree-sequence recording essential for speed |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Contemporary Ne from a single SNP sample | NeEstimator V2 LD method with Pcrit = 0.02 | Standard; widely accepted by conservation reviewers |
| LDNe applied to RAD-seq / WGS | Use SNeP (Barbato 2015) OR thin SNPs to >= 1 cM apart | LDNe assumes inter-locus r^2 reflects demography only; physical linkage inflates it |
| Recent Ne trajectory (bottleneck detection) | GONE2 with populated cM genetic-map column | GONE2 fails silently if cM column is zero (PLINK default uses physical position) |
| Deep demographic history (mammal/vertebrate) | PSMC with >= 20x WGS or Stairway Plot 2 from SFS | PSMC requires high coverage; Stairway Plot 2 needs only the SFS |
| Multi-population demographic inference | dadi / fastsimcoal2 with >= 50 independent optimization replicates | Likelihood surfaces have local optima; single-replicate inference is unreliable |
| Inbreeding from genomic data | F_ROH with length-class thresholds (bcftools roh OR detectRUNS) | F_IS is genome-averaged; F_ROH partitions inbreeding by time |
| Genetic-load assessment | Decompose realized vs masked via Bertorelle 2022 framework | Single "load" estimate hides the dynamics |
| Define management unit (MU) or ESU | Moritz 1994 reciprocal monophyly + nuclear divergence | Do NOT use BPP/BFD* species-delimitation methods (Sukumaran-Knowles 2017 oversplitting) |
| Forward simulation of selection + demography | SLiM 4 with tree-sequence recording + pyslim/tskit | Tree-sequence recording is 5-100x faster than mutation tracking |
| Comparing Ne across species | Cite Ne/Nc taxonomic variation (Hauser & Carvalho 2008) | The Ne/Nc = 0.1 default is wrong for many taxa |
| Genetic rescue decision | Frankham 2015 meta-analysis; usually favors rescue | Outbreeding-depression fear is overstated for most cases |

## Genetic Diversity and F-Statistics

**Goal:** Compute standard population-genetic metrics with Weir-Cockerham estimators and bootstrap confidence intervals.

**Approach:** Convert VCF to genind via adegenet, then to hierfstat format. Run `basic.stats` for Fis/Fst/Ho/He and `pairwise.WCfst` with bootstrapping for population differentiation.

```r
library(hierfstat)
library(adegenet)
library(poppr)

# VCF/genepop/PLINK -> genind via adegenet
data_genind <- read.genepop('populations.gen')
data_hf <- genind2hierfstat(data_genind)

# F-statistics with Weir-Cockerham estimators
bstats <- basic.stats(data_hf)
cat('Overall Fis:', bstats$overall['Fis'], '\n')
cat('Overall Fst:', bstats$overall['Fst'], '\n')

# Pairwise FST with bootstrap CIs
pw_fst <- pairwise.WCfst(data_hf)
boot_fst <- boot.ppfst(data_hf, nboot = 1000)

# Rarefied allelic richness (corrects for unequal sample sizes)
ar <- allelic.richness(data_hf)

# Private alleles unique to each population
pa <- private_alleles(data_genind, count.alleles = TRUE)
```

## Runs of Homozygosity with Length-Class Dating

**Goal:** Detect autozygous segments and date the inbreeding events by ROH length class.

**Approach:** Use `bcftools roh -G30` (HMM-based, density-independent) for VCF input OR `detectRUNS::consecutiveRUNS.run()` for PLINK. Bin ROH by length to date inbreeding events: > 16 Mb means parents/grandparents; 4-16 Mb means ~5 generations; 1-4 Mb means ~10-20 generations; < 1 Mb is deep background.

```r
library(detectRUNS)

# detectRUNS: SNP-by-SNP scanning from PLINK files
runs <- consecutiveRUNS.run(
    genotypeFile = 'genotypes.ped',
    mapFile = 'genotypes.map',
    minSNP = 20,        # Minimum SNPs per run; prevents short-stretch false positives
    minLengthBps = 1e6, # 1 Mb minimum; shorter ROH usually not IBD-derived
    maxGap = 1e6,
    maxOppRun = 1,
    maxMissRun = 2
)

# F_ROH per individual = sum(ROH length) / autosomal genome length
# > 16 Mb ROH: parents/grandparents inbreeding (very recent)
# 4-16 Mb: ~5 generations back
# 1-4 Mb: ~10-20 generations (historical bottleneck)
# < 1 Mb: deep background, ancient homozygosity
froh <- Froh_inbreeding(runs, mapFile = 'genotypes.map', genome_wide = TRUE)

# Bin ROH by length to estimate inbreeding timing
runs_summary <- summaryRuns(runs, genotypeFile = 'genotypes.ped',
                            mapFile = 'genotypes.map')
plot_DistributionRuns(runs)
```

```bash
# Alternative: bcftools roh with HMM (density-independent; better for low-density data)
# -G30: per-sample genotype likelihood threshold (30 = high-quality calls)
# --AF-tag AF: use AF tag from VCF for allele frequencies (else --AF-file)
bcftools roh -G30 --AF-tag AF -o roh_results.txt input.vcf.gz
```

## NeEstimator V2 — Option-File API

**Goal:** Estimate contemporary Ne via LD method from a single sample (Do et al. 2014 *Mol Ecol Resour* 14:209-214).

**Approach:** NeEstimator V2 is option-file driven, NOT CLI-flag driven. Create a `.ne2` text option file specifying input format, methods (LD/HetExcess/Coancestry/Temporal), Pcrit thresholds, and output. Run with `Ne2.exe option_file.ne2`.

```text
# Example NeEstimator V2 option file (option_file.ne2)
# Line order matters; defaults can cause silent failures
# See NeEstimator V2 documentation: https://github.com/bunop/NeEstimator2.X

# Input format
1 0                                   # 1=GenePop, 2=FSTAT; second value reserved
input_genotypes.gen

# Methods (1 = run; 0 = skip)
1 0 0 0                               # LD only; others (HetExcess, Coancestry, Temporal) off

# Pcrit cutoffs (allele frequencies below threshold excluded)
3                                     # number of Pcrit values
0.05 0.02 0.01                        # 0.02 is standard; 0.05 conservative; 0.01 sensitive

# Mating system: 0 = random mating; 1 = monogamy
0

# Output
output_results.txt
```

```bash
# Run NeEstimator V2 (Java-based)
java -jar NeEstimator.jar option_file.ne2
# Verify INFO output line: confirms which methods ran and which were skipped

# Common failure: "Ne = infinity" reported
# Diagnosis: insufficient drift signal (population larger than method can detect)
# Try multiple Pcrit; with genomic data add SNeP physical-linkage correction
```

## GONE2 — Recent Ne Trajectory with the cM-Column Trap

**Goal:** Estimate the Ne trajectory over the last ~100-200 generations from genome-wide LD across recombination rates.

**Approach:** GONE2 requires a genetic map with POPULATED cM positions (not just physical position). PLINK MAP files default to cM=0; if this is not corrected, GONE2 will silently produce nonsense. Verify the cM column is populated from a genetic-map file or use Hi-C-derived recombination map.

```bash
# GONE2 input: PLINK BED/BIM/FAM or VCF + populated MAP
# CRITICAL: BIM/MAP cM column must be populated; default cM=0 produces silent failure

# Check cM column populated
head genotypes.bim   # column 3 should NOT be all zeros

# Run GONE2
# -t 4: threads
# -u 0.05: upper recombination rate bound (exclude pairs with r > 0.05)
# Smaller -u focuses on more recent generations
./gone2 -t 4 -u 0.05 genotypes.vcf

# Output: OUTPUT_GONE2 with generation, Ne, CI_low, CI_high
```

```r
# Parse GONE2 output and plot Ne trajectory
gone_out <- read.table('OUTPUT_GONE2', header = TRUE, sep = '\t')

pdf('gone2_ne_trajectory.pdf', width = 8, height = 5)
plot(gone_out$generation, gone_out$Ne,
     type = 'l', lwd = 2, col = 'blue',
     xlab = 'Generations ago', ylab = 'Effective population size (Ne)',
     main = 'Recent Ne Trajectory (GONE2)', log = 'y')
polygon(c(gone_out$generation, rev(gone_out$generation)),
        c(gone_out$CI_low, rev(gone_out$CI_high)),
        col = adjustcolor('blue', alpha = 0.2), border = NA)
dev.off()
```

## SNeP — Physical-Linkage-Corrected LDNe for Genomic Data

**Goal:** Apply physical-linkage correction to LDNe when SNPs come from RAD-seq or WGS (where inter-locus r^2 reflects chromosomal linkage, not just demography).

**Approach:** SNeP (Barbato 2015 *Front Genet* 6:109) implements Waples & Do's physical-linkage correction. Use when SNPs are not pre-thinned to >= 1 cM apart.

```bash
# SNeP input: PLINK PED/MAP or VCF + map file
# Multi-threaded; supports several corrections (sample size, mutation, phasing, recombination)
./SNeP1.1 -ped genotypes.ped -map genotypes.map -threads 4 \
          -mutationrate 1.4e-8 -out snep_results.txt

# Output: Ne estimates per recombination-rate bin
```

## Deep Demographic History

**Goal:** Reconstruct Ne trajectory over thousands of generations from genome-wide variation.

**Approach:** Pick the appropriate tool by data type. PSMC for a single high-coverage diploid genome. Stairway Plot 2 for SFS from population samples. dadi or fastsimcoal2 for multi-population history with composite likelihood.

```bash
# --- PSMC: single high-coverage WGS (>= 20x) ---
bcftools mpileup -C50 -Q 30 -q 30 -f reference.fa sample.bam | \
    bcftools call -c | vcfutils.pl vcf2fq -d 10 -D 100 > consensus.fq
fq2psmcfa -q20 consensus.fq > consensus.psmcfa
psmc -N25 -t15 -r5 -p '4+25*2+4+6' -o sample.psmc consensus.psmcfa
psmc_plot.pl -u 1.4e-8 -g 5 -p sample_psmc_plot sample.psmc

# --- Stairway Plot 2: SFS-based (works with RAD-seq or WGS) ---
# Build SFS from VCF (use easySFS or vcf2sfs)
# Create blueprint.txt specifying nseq, L, mu, generation time
java -cp stairway_plot_v2.jar Stairbuilder blueprint.txt
bash blueprint.sh

# --- fastsimcoal2: multi-population composite-likelihood SFS ---
# REQUIRES >= 50 independent optimization replicates; single-run is unreliable
for i in {1..50}; do
    fsc27 -t template.tpl -e template.est -m -L 50 -n 100000 -q
done
# Compare likelihoods across replicates; report best AND distribution
```

## Genetic Load — Realized vs Masked Decomposition

**Goal:** Decompose total genetic load into realized (currently expressed) and masked (heterozygous, potential) components per Bertorelle 2022 framework.

**Approach:** Use SnpEff/VEP to annotate variants for predicted functional effect. Compute realized load from homozygous-derived-allele counts at deleterious positions; compute masked load from heterozygous counts. Hedrick & Garcia-Dorado 2016 distinguish purging vs drift dynamics; report both.

```r
# Conceptual workflow (Bertorelle et al. 2022 NRG 23:492-503)
# Realized load: count_homozygous_deleterious / total_deleterious_sites
# Masked load: count_heterozygous_deleterious / total_deleterious_sites
# Total load = realized + 0.5 * masked (assuming partial dominance)

# Annotate VCF with SnpEff or VEP first to classify deleterious vs neutral
# Then per individual:
# realized_load <- sum(genotype == 2 & severity == 'HIGH') / sum(severity == 'HIGH')
# masked_load <- sum(genotype == 1 & severity == 'HIGH') / sum(severity == 'HIGH')

# Cite Hedrick & Garcia-Dorado 2016 TREE 31:940-952 for purging vs drift:
# Strong-s alleles purge under inbreeding (potentially good)
# Weak-s alleles fix by drift (definitely bad)
# Net effect depends on selection-coefficient distribution
# Empirical purging example: Robinson 2018 Curr Biol 28:3487-3494 (Channel Island foxes)
# Simulation-based load assessment: Kyriazis 2021 Evol Lett 5:33-47
```

## Forward Simulation with Tree-Sequence Recording

**Goal:** Simulate selection and non-Wright-Fisher demography efficiently using SLiM 4 with tskit tree-sequence recording.

**Approach:** SLiM 4 with `treeSeqOutput()` records the genealogy; `pyslim` + `tskit` adds neutral mutations a posteriori. This is 5-100x faster than mutation-tracking (Haller, Galloway, Kelleher, Messer, Ralph 2019 *Mol Ecol Resour* 19:552-566). The Eidos scripting language is NOT Python.

```python
# Reference: SLiM 4+, pyslim 1.0+, tskit 0.5+, msprime 1.3+
# Note: SLiM scripts (.slim files) use Eidos, not Python.
# See https://messerlab.org/slim/ for full Eidos syntax.

# After running a SLiM simulation with treeSeqOutput():
import tskit
import pyslim
import msprime

ts = tskit.load('simulation.trees')
ts = pyslim.update(ts)  # update to current SLiM/pyslim conventions

# Recapitate: add coalescence above the SLiM tree root (neutral burn-in)
ts_recap = pyslim.recapitate(ts, recombination_rate=1e-8,
                              ancestral_Ne=10000, random_seed=42)

# Add neutral mutations after-the-fact via msprime
ts_mut = msprime.sim_mutations(ts_recap, rate=1e-8, random_seed=42)

# Export VCF for downstream analyses
with open('simulation.vcf', 'w') as f:
    ts_mut.write_vcf(f)
```

## Per-Method Failure Modes

### LDNe applied to RAD-seq SNPs without physical-linkage correction

**Trigger:** Running NeEstimator V2 LD method on RAD-seq or WGS genotypes thinned only by MAF, with multiple SNPs per chromosome at close physical distance. For RAD-seq biases more broadly, see Andrews 2016 *Nat Rev Genet* 17:81-92.

**Mechanism:** LDNe assumes inter-locus r^2 reflects only demographic LD (drift, random mating). With physically linked SNPs, much r^2 is chromosomal, NOT demographic. The estimator interprets this as "more drift has happened" and reports a smaller Ne.

**Symptom:** LDNe estimate dramatically lower than ecologically reasonable; downward bias compared with temporal or other estimators on the same population.

**Fix:** Thin SNPs to >= 1 cM apart OR use SNeP (Barbato 2015) which corrects for physical linkage explicitly. NeEstimator V2 has a `Chrom` flag for chromosome-aware LDNe; document its use.

### GONE2 silent failure with PLINK MAP cM=0 (the default)

**Trigger:** Running GONE/GONE2 on PLINK output where the MAP file's cM column was never populated (defaults to 0 because PLINK uses physical position).

**Mechanism:** GONE/GONE2 use the cM positions to interpret recombination distances; cM=0 for all loci means the algorithm cannot distinguish linked from unlinked SNPs and produces nonsense.

**Symptom:** GONE2 output shows extreme Ne values or completely flat trajectory; results inconsistent across runs or with other methods.

**Fix:** Populate the cM column from a species-specific genetic map, OR build one from Hi-C data, OR use the linkage-rate approximation from PLINK `--cm-map`. Verify with `head genotypes.bim` — column 3 should not be all zeros.

### NeEstimator silently fails with malformed option file

**Trigger:** Modifying line order in the `.ne2` option file or omitting expected parameters.

**Mechanism:** NeEstimator V2 reads the option file by line order with rigid parsing. Reordered lines or skipped parameters cause the program to misinterpret subsequent lines without raising clear errors.

**Symptom:** "INFO" output line shows fewer methods running than expected; results file is empty or has impossible values.

**Fix:** Strictly follow the documented option-file format. The INFO line confirms which methods actually ran. Cross-reference with the official documentation (https://github.com/bunop/NeEstimator2.X).

### dadi/fastsimcoal2 single-replicate inference at local optimum

**Trigger:** Running dadi or fastsimcoal2 with only 1-5 optimization replicates and reporting the result.

**Mechanism:** Likelihood surfaces for demographic inference have local optima. A single optimization may converge to a local maximum that is much worse than the global maximum.

**Symptom:** Reviewer asks "how many replicates?"; parameter estimates inconsistent across studies; demographic events implausible.

**Fix:** Run >= 50 independent replicates with random starting parameters; report the best-likelihood replicate AND the spread; flag if the top replicates disagree.

### Ne/Nc = 0.1 assumption applied to fish or other high-fecundity taxon

**Trigger:** Converting Ne to Nc via ratio = 0.1 for a marine fish, broadcast spawner, or other species with high reproductive skew.

**Mechanism:** Frankham 1995 median Ne/Nc = 0.1 was derived from primarily terrestrial vertebrates. Hauser & Carvalho 2008 documented Ne/Nc spanning 2-6 orders of magnitude smaller than census (10^-2 to 10^-6) in marine fish with sex-biased and sweepstakes recruitment. The 0.1 default produces wildly wrong Nc estimates.

**Symptom:** Census size estimate disagrees with field observations by orders of magnitude.

**Fix:** Use taxon-specific Ne/Nc ratios from the literature. For marine fish with sweepstakes recruitment, Hauser & Carvalho 2008 documented Ne/Nc spanning 2-6 orders of magnitude smaller than census (10^-2 to 10^-6). For long-lived mammals, 0.1 - 0.3 is typical. Cite Hauser & Carvalho 2008 when discussing Ne/Nc.

## Quantitative Thresholds

| Threshold | Value | Source / rationale |
|-----------|-------|-------------------|
| Modern Ne for inbreeding protection | Ne >= 100 | Frankham 2014 Biol Conserv 170:56-63 (revised from 50) |
| Modern Ne for adaptive maintenance | Ne >= 1000 | Frankham 2014 (revised from 500) |
| F_ROH for very recent inbreeding | ROH > 16 Mb | Parents/grandparents-scale; standard ROH-length-class convention |
| F_ROH for historical bottleneck | 1-4 Mb ROH | ~10-20 generations back |
| LDNe Pcrit (allele frequency cutoff) | 0.02 standard; 0.05 conservative; 0.01 sensitive | NeEstimator V2 convention |
| GONE2 minimum SNPs | 10,000 | Reliable trajectory inference |
| GONE2 minimum N | 50 diploids | Statistical power floor |
| PSMC minimum coverage | >= 20x WGS | Single-genome SMC requires high coverage |
| dadi / fsc2 optimization replicates | >= 50 | Local-optima trap below this |
| Ne/Nc default (use cautiously) | 0.1 vertebrate median | Hauser & Carvalho 2008 documented 2-6 orders of magnitude variation in marine fish (10^-2 to 10^-6) |
| SLiM forward-sim with tree sequences | treeSeqOutput() mandatory for speed | 5-100x faster than mutation tracking |

## Common errors

| Error | Cause | Solution |
|-------|-------|----------|
| LDNe reports Ne = infinity | Population too large for method to detect drift | Try multiple Pcrit; switch to SNeP for genomic data; acknowledge "Ne very large" |
| GONE2 nonsense trajectory | cM column = 0 in BIM/MAP file (PLINK default) | Populate cM with species genetic map or Hi-C inference |
| NeEstimator silent skip | Malformed option file or wrong method index | Check INFO line in output; align with documented format |
| bcftools roh empty output | Missing -G30 flag or --AF-tag | Add `-G30 --AF-tag AF` |
| detectRUNS missing F_ROH | Wrong mapFile path or chromosome naming mismatch | Verify map file format matches PED file |
| dadi numerical error at recent times | Mixing float32 in SFS construction | Use numpy float64 explicitly |
| SLiM script error "Eidos not Python" | Trying to use Python syntax | SLiM uses Eidos; consult SLiM manual |
| msprime PopulationConfiguration deprecation | Old msprime <1.0 API in newer install | Use `msprime.Demography()` constructor |

## References

- Waples RS (2006) A bias correction for estimates of effective population size based on linkage disequilibrium. *Conserv Genet* 7(2):167-184. doi:10.1007/s10592-005-9100-y
- Do C, Waples RS, Peel D, Macbeth GM, Tillett BJ, Ovenden JR (2014) NeEstimator V2. *Mol Ecol Resour* 14(1):209-214. doi:10.1111/1755-0998.12157
- Santiago E, Novo I, Pardiñas AF, Saura M, Wang J, Caballero A (2020) Recent demographic history inferred by high-resolution analysis of linkage disequilibrium (GONE). *Mol Biol Evol* 37(12):3642-3653. doi:10.1093/molbev/msaa169
- Barbato M, Orozco-terWengel P, Tapio M, Bruford MW (2015) SNeP: physical-linkage-corrected LDNe. *Front Genet* 6:109. doi:10.3389/fgene.2015.00109
- Frankham R, Bradshaw CJA, Brook BW (2014) Revised 100/1000 Ne rules. *Biol Conserv* 170:56-63. doi:10.1016/j.biocon.2013.12.036
- Hauser L, Carvalho GR (2008) Paradigm shifts in marine fisheries genetics. *Fish Fish* 9(4):333-362. doi:10.1111/j.1467-2979.2008.00299.x
- Hedrick PW, García-Dorado A (2016) Understanding inbreeding depression, purging, and genetic rescue. *Trends Ecol Evol* 31(12):940-952. doi:10.1016/j.tree.2016.09.005
- Bertorelle G, Raffini F, Bosse M, Bortoluzzi C, Iannucci A, Trucchi E, Morales HE, van Oosterhout C (2022) Genetic load. *Nat Rev Genet* 23(8):492-503. doi:10.1038/s41576-022-00448-x
- Gutenkunst RN, Hernandez RD, Williamson SH, Bustamante CD (2009) Inferring joint demographic history with dadi. *PLoS Genet* 5(10):e1000695. doi:10.1371/journal.pgen.1000695
- Excoffier L, Dupanloup I, Huerta-Sánchez E, Sousa VC, Foll M (2013) Robust demographic inference (fastsimcoal2). *PLoS Genet* 9(10):e1003905. doi:10.1371/journal.pgen.1003905
- Jouganous J, Long W, Ragsdale AP, Gravel S (2017) Inferring the joint demographic history of multiple populations: beyond the diffusion approximation (moments). *Genetics* 206(3):1549-1567. doi:10.1534/genetics.117.200493
- Kamm J, Terhorst J, Durbin R, Song YS (2020) Efficiently inferring the demographic history of many populations with allele count data (momi2). *J Am Stat Assoc* 115(531):1472-1487. doi:10.1080/01621459.2019.1635482
- Kelleher J, Etheridge AM, McVean G (2016) Efficient coalescent simulation (msprime). *PLoS Comput Biol* 12(5):e1004842. doi:10.1371/journal.pcbi.1004842
- Haller BC, Messer PW (2019) SLiM 3: forward genetic simulation beyond Wright-Fisher. *Mol Biol Evol* 36(3):632-637. doi:10.1093/molbev/msy228
- Haller BC, Galloway J, Kelleher J, Messer PW, Ralph PL (2019) Tree-sequence recording in SLiM. *Mol Ecol Resour* 19(2):552-566. doi:10.1111/1755-0998.12968
- Andrews KR, Good JM, Miller MR, Luikart G, Hohenlohe PA (2016) Harnessing RADseq for population genomics. *Nat Rev Genet* 17(2):81-92. doi:10.1038/nrg.2015.28
- Frankham R (2015) Genetic rescue meta-analysis. *Mol Ecol* 24(11):2610-2618. doi:10.1111/mec.13139
- Frankham R (1995) Effective population size / adult population size ratios in wildlife. *Genet Res* 66:95-107. doi:10.1017/S0016672300034455
- Moritz C (1994) Defining 'Evolutionarily Significant Units' for conservation. *Trends Ecol Evol* 9(10):373-375. doi:10.1016/0169-5347(94)90057-4
- Robinson JA, Brown C, Kim BY, Lohmueller KE, Wayne RK (2018) Purging of strongly deleterious mutations explains long-term persistence and absence of inbreeding depression in island foxes. *Curr Biol* 28(21):3487-3494.e4. doi:10.1016/j.cub.2018.08.066
- Kyriazis CC, Wayne RK, Lohmueller KE (2021) Strongly deleterious mutations are a primary determinant of extinction risk due to inbreeding depression. *Evol Lett* 5(1):33-47. doi:10.1002/evl3.209

## Related Skills

- ecological-genomics/landscape-genomics - Adaptive variation and genotype-environment associations
- ecological-genomics/species-delimitation - Taxonomic unit definition (cite Sukumaran-Knowles caveat for ESU/MU vs species)
- population-genetics/population-structure - Population stratification and STRUCTURE/ADMIXTURE
- population-genetics/selection-statistics - Genome-wide selection signatures
- variant-calling/vcf-basics - VCF preparation from RAD-seq or WGS
<!-- END FILE: ecological-genomics/conservation-genetics/SKILL.md -->

## 子目录：ecological-genomics/edna-metabarcoding

<!-- BEGIN FILE: ecological-genomics/edna-metabarcoding/SKILL.md -->
---
name: bio-ecological-genomics-edna-metabarcoding
description: Processes eDNA metabarcoding from raw paired-end reads to species tables, navigating ASV (DADA2, UNOISE3) vs OTU (swarm v2) decision (Callahan 2017 vs Schloss multi-copy-16S critique), marker/primer choice (Leray COI, MiFish 12S, 515F/806R 16S, ITS2) with primer-specific bias, OBITools3 v3 command-name break (obi stats plural; .tar.gz taxonomy), tag-jumping with dual-indexing (Schnell 2015; NovaSeq 10x MiSeq), decontam as screening-not-classifier (Davis 2018), read-counts-not-abundance critique (Lamb 2019), site-occupancy modeling (Ficetola 2015), Naive-Bayes calibration limits (Bokulich 2018), and eDNA decay (Strickler 2015). Use when going from raw eDNA FASTQ to species tables, picking marker + denoising pipeline, deciding whether read counts represent abundance, applying occupancy modeling, configuring OBITools3 v3, or interpreting decontam output. Not for clinical 16S microbiome (see microbiome/amplicon-processing).
tool_type: mixed
primary_tool: dada2
---

## Version Compatibility

Reference examples tested with: DADA2 1.30+, cutadapt 4.7+, OBITools3 (Python 3), decontam 1.20+, microDecon 1.0+, occumb 1.0+, vsearch 2.27+, swarm 3.1+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# eDNA Metabarcoding

**"Process eDNA samples to identify species present"** -> Trim primers, denoise to ASVs (or cluster to OTUs), detect chimeras, assign taxonomy, filter contamination with negative controls AND DNA concentration, decompose tag-jumping artifacts, and quantify detection uncertainty via site-occupancy modeling. For the foundational eDNA-for-wildlife review, see Bohmann et al. 2014 *Trends Ecol Evol* 29:358-367.
- CLI: `cutadapt` for primer removal (linked-adapter mode)
- R: `dada2::filterAndTrim()` -> `dada()` -> `assignTaxonomy()` for ASV pipeline
- CLI: `obi stats` / `obi clean` / `obi ecotag` for OBITools3 (NOTE: v3 plural commands)
- R: `decontam::isContaminant()` for contamination screening
- R: `occumb::occumb()` for detection-corrected occurrence

## The Single Most Important Modern Insight -- Read Counts Are NOT Abundance

Elbrecht & Leese 2015 *PLoS One* 10:e0130324 and Lamb et al. 2019 *Mol Ecol* 28:420-430 (meta-analysis) established that metabarcoding read counts have weak-to-moderate, taxon-specific, NONLINEAR correlation with biomass or DNA input. Primer-binding bias dominates; PCR replicates introduce stochasticity. **Reporting read counts as abundance without mock-community calibration is malpractice.** Modern practice: report PRESENCE/ABSENCE or relative abundance with explicit calibration; use multiple PCR replicates; apply site-occupancy models for detection correction.

A second cornerstone: the ASV-vs-OTU debate is taxon-specific, not universal. Callahan, McMurdie, Holmes 2017 *ISME J* 11:2639-2643 argued ASVs replace OTUs because modern denoising resolves single-nucleotide differences. Schloss 2021 *mSphere* 6:e00191-21 showed that for bacterial 16S with 1-15 intra-genomic rRNA copies, a single E. coli strain produces ~7 distinct ASVs, splitting bacterial genomes across artificial clusters. **For COI metazoan metabarcoding, ASVs (DADA2/UNOISE3) are recommended; for bacterial 16S, ASVs inflate alpha-diversity and OTUs may be appropriate.**

A third: **decontam (Davis 2018) is a SCREENING tool, not a deterministic classifier.** It flags candidates; biological plausibility check is required before deletion. The default `threshold=0.1` over-flags in low-biomass data.

## Algorithmic Taxonomy

| Method | Output | Strength | Fails when |
|--------|--------|----------|------------|
| DADA2 | Single-nucleotide ASVs | High resolution; learned error model; standard for COI/12S/18S/fungal-ITS | Small datasets (< 100 samples) for error learning; multi-copy bacterial rRNA |
| UNOISE3 (USEARCH/VSEARCH; Edgar 2016) | zOTUs (essentially ASVs) | Fast; algorithmic simplicity | Limited Linux/Mac binary distribution under license |
| Swarm v2 `-d 1 --fastidious` (Mahé 2015) | Abundance-weighted single-linkage OTUs | Modern OTU pipeline; better than legacy 97% UCLUST | OTUs by design (not single-nt resolution) |
| 97% UCLUST | Classical OTUs | Legacy familiarity | Biologically arbitrary threshold; supersedes by DADA2/swarm |
| VSEARCH global pairwise | Taxonomic assignment via best-hit | Fast, transparent, no training | Conservative; mis-assigns sister species when ref incomplete |
| Naive Bayes (q2-feature-classifier, RDP) | Probabilistic taxonomic assignment | Probabilistic confidence; standard for 16S | Confidence values are scikit-learn calibrated, not true probabilities (Bokulich 2018) |
| SINTAX (Edgar) | Bootstrap-supported taxonomy | Fast; no training | Less accurate than Naive Bayes for divergent sequences |
| LCA (BASTA, MEGAN-LCA) | Lowest common ancestor of multiple hits | Conservative; never over-confident | Can over-merge to high taxonomic ranks |
| Phylogenetic placement (EPA-ng + gappa) | Position on reference tree | Most rigorous; phylogenetically explicit | 10-100x slower; emerging not yet standard |
| decontam | Flagged contaminant candidates | Statistical screening of negative controls and DNA concentration patterns | Output is screening, not classification; needs biological-plausibility check |
| UCHIME3 (in DADA2/VSEARCH) | Chimera detection | Standard for de novo chimera removal | Some divergent chimeras escape |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Metazoan COI metabarcoding (water, gut content) | mlCOIintF/jgHCO2198 (Leray 2013) primers; DADA2 ASVs | Standard primer set; ASVs preserve single-nt resolution |
| Fish eDNA from water | MiFish-U/E (Miya 2015) 12S primers; DADA2 ASVs | Dominant eDNA fish marker globally |
| Freshwater macroinvertebrate bioassessment | BF1/BR1 freshwater-optimized COI primers | Higher primer-binding inclusivity for aquatic insects |
| Bacterial community 16S | 515F/806R (V4) Parada modified; ASVs OR Swarm v2 | Schloss 2021 caveat applies; ASVs may oversplit multi-copy rRNA |
| Fungal community ITS | ITS2 primers; DADA2 or UNITE pipeline | UNITE is curated for fungal ITS |
| Plant community DNA | trnL P6 loop (Taberlet 2007) for degraded DNA | Robust to degradation |
| Deciding ASV vs OTU | ASVs for COI/12S/18S/fungi; OTU consideration for 16S with multi-copy concern | Taxon-specific |
| NovaSeq library (patterned flow cell) | Heavier tag-jumping correction; expect 10x higher rates than MiSeq | Patterned-cell index hopping |
| Low-biomass eDNA (deep ocean, ancient) | decontam frequency + prevalence methods; explicit reagent-contamination check | Reagent contamination dominates |
| Quantitative comparison across samples | Mock-community calibration BEFORE reporting read counts | Without mock, read counts are biased estimators of biomass |
| Detection probability with replication | Site-occupancy models (occumb, eDNAoccupancy; Ficetola 2015) | Read counts alone underestimate occurrence; replicates correct |
| Taxonomic assignment for marker > 80% covered | Naive Bayes (q2-feature-classifier) | Probabilistic; well-supported |
| Taxonomic assignment for sparse reference | Phylogenetic placement (EPA-ng) | Robust to incomplete references |
| OBITools3 pipeline | `obi stats` (NOTE: plural), DMS-based, `.tar.gz` taxonomy | v3 syntax differs from v1 |

## Primer Trimming with cutadapt

**Goal:** Remove primer sequences while discarding reads that lack primers, before quality filtering.

**Approach:** Use cutadapt linked-adapter mode with marker-specific 5' and 3' primer pairs. `--discard-untrimmed` removes reads lacking expected primers; `min_overlap` prevents false primer detection in random sequence regions.

```bash
# COI metazoan (Leray mlCOIintF / jgHCO2198 -> 313 bp)
cutadapt -g 'GGWACWGGWTGAACWGTWTAYCCYCC;min_overlap=20' \
         -G 'TAIACYTCIGGRTGICCRAARAAYCA;min_overlap=20' \
         --discard-untrimmed --pair-filter=any \
         -o trimmed_R1.fastq.gz -p trimmed_R2.fastq.gz \
         raw_R1.fastq.gz raw_R2.fastq.gz

# Fish 12S (MiFish-U -> 163-185 bp)
cutadapt -g 'GTCGGTAAAACTCGTGCCAGC;min_overlap=18' \
         -G 'CATAGTGGGGTATCTAATCCCAGTTTG;min_overlap=18' \
         --discard-untrimmed --pair-filter=any \
         -o trimmed_R1.fastq.gz -p trimmed_R2.fastq.gz \
         raw_R1.fastq.gz raw_R2.fastq.gz

# Fungal ITS2
cutadapt -g 'GTGAATCATCGAATCTTTGAAC;min_overlap=18' \
         -G 'TCCTCCGCTTATTGATATGC;min_overlap=18' \
         --discard-untrimmed --pair-filter=any \
         -o trimmed_R1.fastq.gz -p trimmed_R2.fastq.gz \
         raw_R1.fastq.gz raw_R2.fastq.gz
```

## DADA2 ASV Pipeline

**Goal:** Denoise paired-end amplicon reads into exact amplicon sequence variants (ASVs) with chimera removal and reference-based taxonomy assignment, per Callahan et al. 2016 *Nat Methods* 13:581-583.

**Approach:** Filter to length/quality thresholds, learn error rates per dataset, run dada() to denoise, merge pairs, build sequence table, remove chimeras with UCHIME3-equivalent in DADA2, then assign taxonomy against the marker-appropriate reference DB. CRITICAL: primers must be removed (cutadapt) BEFORE filterAndTrim, OR the error model is corrupted.

```r
library(dada2)

# CRITICAL: primer removal MUST precede filterAndTrim
# DADA2's error model assumes primer-free reads
fwd_reads <- sort(list.files('primer_trimmed/', pattern = '_R1', full.names = TRUE))
rev_reads <- sort(list.files('primer_trimmed/', pattern = '_R2', full.names = TRUE))
filt_fwd <- file.path('filtered', basename(fwd_reads))
filt_rev <- file.path('filtered', basename(rev_reads))

# Filter and trim
# maxEE=c(2,2): expected errors per read; tradeoff sensitivity/specificity
# truncLen: set from quality profile inspection; do not guess
out <- filterAndTrim(fwd_reads, filt_fwd, rev_reads, filt_rev,
                     maxN = 0, maxEE = c(2, 2), truncQ = 2,
                     truncLen = c(220, 180),     # data-dependent; inspect plotQualityProfile()
                     minLen = 100, rm.phix = TRUE, multithread = TRUE)

# Learn error rates
# For small datasets (< 100 samples), pool aggressively or use pre-learned model
err_fwd <- learnErrors(filt_fwd, multithread = TRUE)
err_rev <- learnErrors(filt_rev, multithread = TRUE)

# Denoise
dada_fwd <- dada(filt_fwd, err = err_fwd, multithread = TRUE)
dada_rev <- dada(filt_rev, err = err_rev, multithread = TRUE)

# Merge pairs with minimum overlap
merged <- mergePairs(dada_fwd, filt_fwd, dada_rev, filt_rev, minOverlap = 12)

# Build sequence table
seqtab <- makeSequenceTable(merged)

# Remove chimeras
# method='consensus': per-sample then consensus; conservative (default)
# method='pooled': pooled across samples; aggressive; can over-merge real diversity
# Chimera rate >30% typically indicates library prep problems
seqtab_nochim <- removeBimeraDenovo(seqtab, method = 'consensus',
                                     multithread = TRUE)
cat('Chimera rate:', round(1 - sum(seqtab_nochim) / sum(seqtab), 3), '\n')

# Taxonomy assignment
# minBoot=80: standard genus-level confidence; 50 for family-level
# IMPORTANT: pair the marker with the appropriate reference DB
# COI -> MIDORI2 LONGEST_NUC_GB259_CO1 (or BOLD with curation)
# 12S -> MitoFish (Miya lab)
# 16S V4 -> SILVA 138.1+
# 18S V4/V9 -> SILVA 138.1+ or PR2
# Fungal ITS -> UNITE 9.0+
taxa <- assignTaxonomy(seqtab_nochim,
                       'MIDORI2_LONGEST_NUC_GB259_CO1_DADA2.fasta.gz',
                       minBoot = 80, multithread = TRUE)
```

## OBITools3 Pipeline — The v1 -> v3 Command Break

**Goal:** Process eDNA reads through the Unix-style OBITools v3 pipeline (Boyer et al. 2016 *Mol Ecol Resour* 16:176-182 introduced OBITools v1; v3 is the post-2018 Python 3 rewrite) with DMS-based sequence management.

**Approach:** v3 introduces a Database Management System (DMS) abstraction; sequences are imported into a DMS rather than read directly from FASTQ. Commands use spaces (e.g., `obi stats` plural, not `obistat`). Taxonomy import expects `.tar.gz` archive, not a directory.

```bash
# v1 -> v3 command-name changes (critical):
# v1: obistat       -> v3: obi stats
# v1: obigrep       -> v3: obi grep
# v1: obiuniq       -> v3: obi uniq
# v1: obitab        -> v3: obi annotate / obi export --tab-output (different semantics)
# v1: ngsfilter     -> v3: obi ngsfilter
# v1: taxdump dir   -> v3: .tar.gz archive

# Import paired FASTQ into DMS
obi import --fastq-input raw_R1.fastq.gz EDNA/reads1
obi import --fastq-input raw_R2.fastq.gz EDNA/reads2

# Paired-end alignment
obi alignpairedend -R EDNA/reads2 EDNA/reads1 EDNA/aligned

# Filter by alignment score and length
obi grep -p 'sequence["score"] >= 50' EDNA/aligned EDNA/filtered
obi grep -p 'len(sequence) >= 100 and len(sequence) <= 500' \
    EDNA/filtered EDNA/length_filtered

# Demultiplex (NGS filter file maps barcodes -> samples)
obi ngsfilter -t ngsfilter.txt -u EDNA/unassigned \
    EDNA/length_filtered EDNA/demux

# Dereplicate (obi uniq creates merged_sample attribute automatically)
obi uniq EDNA/demux EDNA/derep

# Remove suspected error singletons
obi grep -p 'sequence["count"] >= 2' EDNA/derep EDNA/no_singletons

# Denoise via obi clean
obi clean -s merged_sample -r 0.05 -H EDNA/no_singletons EDNA/denoised

# Taxonomy assignment against reference database
obi ecotag -R EDNA/refdb --taxonomy EDNA/taxonomy EDNA/denoised EDNA/assigned

# Export tab-separated species table
obi export --tab-output EDNA/assigned > species_table.tsv
```

Across most metabarcoding studies, 50-85% of ASVs cannot be assigned to species level due to incomplete references (Wangensteen et al. 2018 *PeerJ* 6:e4705 documented this for marine COI + 18S). Report this gap honestly; do not infer ecology from "unassigned" reads.

## Tag-Jumping Mitigation — Schnell 2015 + NovaSeq Caveat

**Goal:** Detect and remove sequence-to-sample misassignments arising from chimeric library molecules with mismatched indices.

**Approach:** Use dual-indexing (different indices at both ends; cross-jumped pairs are discarded). Quantify residual tag-jumping rate from per-ASV cross-sample appearance and apply per-ASV abundance threshold filtering with `metabaR::tagjumpslayer`. For NovaSeq libraries, expect ~10x higher tag-jumping than MiSeq due to patterned flow cells.

```r
library(metabaR)

# metabaR expects an metabarlist object (asv table + sample info + ngsfilter)
# tagjumpslayer applies per-ASV abundance-threshold filter
# threshold: 0.01 (1% of ASV total) is conservative; 0.001 for aggressive removal
# Adjust threshold higher for NovaSeq (~0.005-0.01) than MiSeq (~0.001-0.005)

# Quantify residual tag-jumping rate before filtering:
# Count reads in sample x ASV combinations that should be 0 by experimental design
# (e.g., samples explicitly excluded from a particular condition)
# That rate / total reads = empirical tag-jumping rate
# Report this rate in methods section
```

## Contamination Screening with decontam

**Goal:** Identify candidate contaminant ASVs from negative controls and DNA-concentration patterns.

**Approach:** Use `decontam::isContaminant` with `method='combined'` when both DNA concentration AND negative controls are available. Treat flagged ASVs as SCREENING CANDIDATES; verify biological plausibility before deletion. The default `threshold=0.1` is over-aggressive in low-biomass data.

```r
library(decontam)

# Frequency method: contaminants more frequent at LOW DNA concentration
# Prevalence method: contaminants more frequent in negative controls
# Combined: uses both signals (most robust)

contam <- isContaminant(seqtab_nochim,
                        conc = dna_concentration,        # qPCR or Qubit per sample
                        neg = is_negative_control,       # logical: which samples are controls
                        method = 'combined',
                        threshold = 0.1)                 # default; lower for high-confidence calls

# CRITICAL: decontam output is SCREENING, not classification
# Manually inspect each flagged ASV: is the taxonomic assignment plausibly a reagent contaminant?
# Common reagent contaminants: Delftia, Sphingomonas, Burkholderia, Propionibacterium
flagged <- which(contam$contaminant)
cat('Decontam flagged', length(flagged), 'ASVs as candidates\n')

# After manual review, remove confirmed contaminants
confirmed_contam <- intersect(flagged, biological_plausibility_check_result)
seqtab_clean <- seqtab_nochim[, !(colnames(seqtab_nochim) %in% confirmed_contam)]
```

## Site-Occupancy Modeling — Correcting for Imperfect Detection

**Goal:** Estimate true species occurrence probabilities from replicated eDNA samples, accounting for false negatives in any single PCR replicate.

**Approach:** Fit a multi-species occupancy model via MCMC (Ficetola 2015 *Mol Ecol Resour* 15:543-556) on a 3D array of replicated read counts. Output: per-site, per-species occupancy probabilities corrected for detection.

```r
library(occumb)

# y: 3D array [species, sites, replicates] of read counts
# spec_cov: species covariates (traits)
# site_cov: site covariates (env)
data_obj <- occumbData(y = count_array, spec_cov = species_covariates,
                       site_cov = site_covariates)

# Fit hierarchical occupancy model
# Requires JAGS installation
# n.iter >= 10000, n.burn >= 2500 for publication-quality posteriors
fit <- occumb(data = data_obj, n.chains = 4, n.iter = 10000,
              n.thin = 5, n.burn = 2500)

# Extract detection-corrected occupancy
summary(fit)
```

## Per-Method Failure Modes

### Reporting read counts as biomass without mock-community calibration

**Trigger:** Comparing read counts of two ASVs and reporting the ratio as a biomass / abundance estimate.

**Mechanism:** Primer-template binding affinity varies systematically across taxa; PCR amplification is non-linear (saturates); read counts have weak-to-moderate, NONLINEAR correlation with biomass (Elbrecht 2015; Lamb 2019).

**Symptom:** Reviewer asks "how is it known that reads = biomass?"; cross-study quantitative comparisons fail to replicate.

**Fix:** Either (a) restrict reporting to presence/absence; (b) report read counts as relative abundances with explicit caveat; or (c) include mock-community of known composition for primer-specific calibration. Do not silently equate reads with biomass.

### NovaSeq tag-jumping with MiSeq-tuned filtering

**Trigger:** Applying tag-jumping filters calibrated on MiSeq libraries to NovaSeq data.

**Mechanism:** NovaSeq patterned flow cells have ~10x higher index hopping than MiSeq. MiSeq-calibrated thresholds (often ~0.001 fraction) are too permissive on NovaSeq data.

**Symptom:** Apparent rare-species detections in NovaSeq libraries do not replicate; per-ASV cross-sample appearance is unusually broad.

**Fix:** Use NovaSeq-appropriate tag-jumping thresholds (~0.005-0.01) and report the empirical tag-jumping rate from explicit-zero combinations.

### decontam threshold over-aggressive in low-biomass data

**Trigger:** Applying default `threshold = 0.1` to ASVs from open-ocean water, ancient sediments, or other dilute samples.

**Mechanism:** In low-biomass samples, the contaminant signal/background ratio approaches 1; decontam over-flags real but dilute biology as "contaminant" because the statistical pattern looks similar.

**Symptom:** Many ASVs flagged from low-biomass samples; taxonomic profile of "flagged contaminants" looks biologically realistic.

**Fix:** Lower threshold (0.05 or 0.01); always manually review flagged ASVs for biological plausibility; cite Salter 2014 *BMC Biol* 12:87 for the low-biomass reagent-contamination caveat.

### Skipping primer removal before DADA2 filterAndTrim

**Trigger:** Running DADA2's `filterAndTrim()` on FASTQ files that still contain primer sequences.

**Mechanism:** DADA2 learns sequencing error from the empirical data; if primer sequences are present, they look like "perfect agreement" and corrupt the error model. ASVs are inferred with primer artifacts attached.

**Symptom:** DADA2 reports "phix-like contamination" (false; it's primers); ASVs start with the primer sequence; chimera rate elevated.

**Fix:** Always run cutadapt (or similar) BEFORE filterAndTrim. Verify with `head` of trimmed FASTQ that primer sequences are gone.

### OBITools v3 commands with v1 syntax

**Trigger:** Running `obistat` or `obigrep` on a v3 install.

**Mechanism:** v1 used concatenated command names (`obistat`); v3 uses subcommand syntax with a space (`obi stats` — note plural).

**Symptom:** Bash error `obistat: command not found`; tutorial documentation does not match installed version.

**Fix:** Use `obi <subcommand>` syntax; consult `obi --help` for current command list. Taxonomy import requires `.tar.gz` archive, not unpacked directory.

## Quantitative Thresholds

| Threshold | Value | Source / rationale |
|-----------|-------|-------------------|
| DADA2 maxEE per read | 2 | Standard sensitivity/specificity balance |
| DADA2 chimera rate alarm | > 30% suggests library issues | Empirical convention |
| DADA2 minBoot for taxonomy | 80 for genus; 50 for family | Standard confidence cutoffs |
| Tag-jumping filter MiSeq | 0.001-0.005 fraction of ASV total | Schnell 2015 |
| Tag-jumping filter NovaSeq | 0.005-0.01 fraction of ASV total | Patterned-cell index hopping ~10x higher |
| decontam threshold | 0.1 default; 0.05 for low-biomass | Davis 2018; reduce for dilute samples |
| Per-sample minimum reads | 1000 (after filtering) | Below this rare-species detection unreliable |
| Singleton removal | count >= 2 | Singletons often error-driven |
| Bootstrap nperm for tests | 999 | Standard permutation count |
| Occupancy model iterations | n.iter >= 10000, n.burn >= 2500 | occumb default for stable posteriors |
| eDNA decay (20 deg C surface water) | half-life ~4-15 hours | Strickler 2015 Biol Conserv 183:85-92 |

## Common errors

| Error | Cause | Solution |
|-------|-------|----------|
| `obistat: command not found` | OBITools v3 uses `obi stats` (plural) | Use v3 syntax |
| DADA2 error rate plot looks pathological | Primer sequences still in reads | Re-run cutadapt before filterAndTrim |
| Chimera rate > 30% | Library-prep issue or primer dimers | Inspect raw FASTQ; check PCR conditions |
| decontam flags many real species | Default threshold too aggressive for low-biomass | Lower threshold; manual review |
| Naive Bayes confidence 0.95 but species is wrong | scikit-learn-calibrated "confidence" not true probability | Use phylogenetic placement for borderline assignments |
| occumb JAGS not found error | JAGS not installed system-wide | Install JAGS (CRAN page has platform instructions) |
| eDNA detections do not replicate | Read counts treated as abundance | Switch to presence/absence; use mock-community calibration |
| MIDORI2 download path expired | Database updated; old URL gone | Check current MIDORI2 / MitoFish download page |

## References

- Callahan BJ, McMurdie PJ, Rosen MJ, Han AW, Johnson AJA, Holmes SP (2016) DADA2. *Nat Methods* 13(7):581-583. doi:10.1038/nmeth.3869
- Callahan BJ, McMurdie PJ, Holmes SP (2017) Exact sequence variants should replace OTUs. *ISME J* 11(12):2639-2643. doi:10.1038/ismej.2017.119
- Edgar RC (2016) UNOISE2 / UNOISE3. *bioRxiv* preprint. doi:10.1101/081257
- Mahe F, Rognes T, Quince C, de Vargas C, Dunthorn M (2015) Swarm v2. *PeerJ* 3:e1420. doi:10.7717/peerj.1420
- Leray M, Yang JY, Meyer CP et al. (2013) mlCOIintF/jgHCO2198 metazoan COI primer. *Front Zool* 10:34. doi:10.1186/1742-9994-10-34
- Miya M, Sato Y, Fukunaga T et al. (2015) MiFish 12S fish eDNA primer. *R Soc Open Sci* 2(7):150088. doi:10.1098/rsos.150088
- Schnell IB, Bohmann K, Gilbert MTP (2015) Tag jumps illuminated. *Mol Ecol Resour* 15(6):1289-1303. doi:10.1111/1755-0998.12402
- Davis NM, Proctor DM, Holmes SP, Relman DA, Callahan BJ (2018) decontam. *Microbiome* 6:226. doi:10.1186/s40168-018-0605-2
- Boyer F, Mercier C, Bonin A, Le Bras Y, Taberlet P, Coissac E (2016) OBITools. *Mol Ecol Resour* 16(1):176-182. doi:10.1111/1755-0998.12428
- Elbrecht V, Leese F (2015) DNA-based ecosystem quantification critique. *PLoS One* 10(7):e0130324. doi:10.1371/journal.pone.0130324
- Lamb PD, Hunter E, Pinnegar JK, Creer S, Davies RG, Taylor MI (2019) How quantitative is metabarcoding: meta-analysis. *Mol Ecol* 28(2):420-430. doi:10.1111/mec.14920
- Ficetola GF, Pansu J, Bonin A et al. (2015) Replication levels and false presences in eDNA. *Mol Ecol Resour* 15(3):543-556. doi:10.1111/1755-0998.12338
- Wangensteen OS, Palacin C, Guardiola M, Turon X (2018) COI + 18S marine metabarcoding. *PeerJ* 6:e4705. doi:10.7717/peerj.4705
- Strickler KM, Fremier AK, Goldberg CS (2015) eDNA degradation kinetics. *Biol Conserv* 183:85-92. doi:10.1016/j.biocon.2014.11.038
- Bokulich NA, Kaehler BD, Rideout JR et al. (2018) Optimizing taxonomic classification with q2-feature-classifier. *Microbiome* 6:90. doi:10.1186/s40168-018-0470-z
- Bohmann K, Evans A, Gilbert MTP et al. (2014) eDNA for wildlife and biodiversity. *Trends Ecol Evol* 29(6):358-367. doi:10.1016/j.tree.2014.04.003
- Schloss PD (2021) Amplicon sequence variants artificially split bacterial genomes into separate clusters. *mSphere* 6(4):e00191-21. doi:10.1128/mSphere.00191-21
- Salter SJ, Cox MJ, Turek EM et al. (2014) Reagent and laboratory contamination can critically impact sequence-based microbiome analyses. *BMC Biol* 12:87. doi:10.1186/s12915-014-0087-z
- Taberlet P, Coissac E, Pompanon F et al. (2007) Power and limitations of the chloroplast trnL (UAA) intron for plant DNA barcoding. *Nucleic Acids Res* 35(3):e14. doi:10.1093/nar/gkl938

## Related Skills

- ecological-genomics/biodiversity-metrics - Diversity analysis from species occurrence tables (Hill numbers, beta partition)
- ecological-genomics/community-ecology - Environmental gradient analysis of community composition (PERMANOVA + PERMDISP, ordination)
- microbiome/amplicon-processing - 16S clinical microbiome alternative pipeline
- read-qc/quality-reports - Upstream read-quality assessment before primer trimming
- database-access/entrez-fetch - Retrieve reference sequences for custom taxonomy databases
<!-- END FILE: ecological-genomics/edna-metabarcoding/SKILL.md -->

## 子目录：ecological-genomics/landscape-genomics

<!-- BEGIN FILE: ecological-genomics/landscape-genomics/SKILL.md -->
---
name: bio-ecological-genomics-landscape-genomics
description: Tests genotype-environment associations and identifies adaptive loci while correcting for the four-confound landscape (structure, demography, background selection, sampling design) using LFMM2 with mandatory K via sNMF cross-entropy elbow (LEA 3), BayPass Core/AUX/C2/IS with Omega covariance matrix, RDA / pRDA for polygenic adaptation (Forester 2018; requires imputed genotypes), OutFLANK with trimmed FST null, pcadapt, gradient forests (Ellis-Smith-Pitcher 2012, NOT mis-cited Ellis-Manel), Capblancq & Forester 2021 RDA Swiss-army-knife, genomic-offset prediction with Lind & Lotterhos 2025 three-regime caveat, Lotterhos-Whitlock sampling optima, Wang & Bradburd 2014 IBD vs IBE, and Circuitscape + ResistanceGA. Use when identifying adaptive loci across gradients, choosing K for LFMM2, deciding among GEA methods, predicting maladaptation with the novel-environment caveat, distinguishing IBD vs IBE, or optimizing sampling design.
tool_type: r
primary_tool: LEA
---

## Version Compatibility

Reference examples tested with: LEA 3.14+ (lfmm2 via LEA 3), pcadapt 4.3+, OutFLANK 0.2+, vegan 2.6+, gradientForest 0.1-32+, terra 1.7+, qvalue 2.34+, BayPass 2.3+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Landscape Genomics

**"Find loci associated with environmental adaptation in my populations"** -> Genotype-environment association with K-selected latent-factor correction, multivariate RDA for polygenic signal, paired with demography-calibrated FST outliers; genomic-offset prediction with explicit prediction-novelty regime characterization.
- R: `LEA::lfmm2()` (modern; via LEA 3) for univariate GEA with cross-entropy-elbow K choice
- R: `vegan::rda()` with `Condition()` for partial-RDA polygenic GEA
- R: `OutFLANK::OutFLANK()` for demography-calibrated FST outliers
- R: `pcadapt::pcadapt()` for PC-based scans without environmental data
- CLI: `g_baypass` for BayPass Bayesian Core/AUX/C2/IS analyses

## The Single Most Important Modern Insight -- GEA is a Four-Confound Problem, Not a Signal-Plus-Noise Problem

The number-one failure mode in landscape genomics is treating "is locus X associated with environment Y" as a simple signal-extraction problem (the NimBios working group consolidated this view in Hoban 2016 *Am Nat* 188:379-397). **GEA has FOUR concurrent confounds**:
1. **Population structure** — IBD-driven allele-frequency gradients track distance, which correlates with most environmental variables
2. **Demographic history** — range expansion creates allele-frequency clines along the expansion axis that mimic selection (Lotterhos & Whitlock 2014 *Mol Ecol* 23:2178-2192)
3. **Background and linked selection** — reduces diversity in low-recombination regions, inflating apparent local-FST signals
4. **Sampling design** — non-random spatial sampling creates spurious GEA signals (Lotterhos & Whitlock 2015 *Mol Ecol* 24:1031-1046; **paired contrasts > random > transects** when demography is concerning)

A second cornerstone: **Forester et al. 2018 established RDA as the best polygenic-adaptation detector** but with a caveat — RDA performance requires imputed genotypes (no missing data) and is best for linear-gradient environments. For monogenic strong-selection loci, OutFLANK and BayPass-C2 remain competitive.

A third: **Genomic offset has three regimes** (Lind & Lotterhos 2025 *Mol Ecol Resour* 25:e14008): works well for interpolation (similar-to-training environments), degrades gracefully for modest extrapolation, FAILS for highly novel future environments. Reporting a single offset map without characterizing prediction-novelty is methodologically incomplete. For the broader eco-evolutionary integration framework, see Aguirre-Liguori 2021 *Nat Ecol Evol* 5:1350-1360.

## Algorithmic Taxonomy

| Method | Type | Strength | Fails when |
|--------|------|----------|------------|
| FST outliers (naive) | Univariate per-locus | Simple; widely understood | Inflated FDR under demography (Lotterhos & Whitlock 2014) |
| OutFLANK (Whitlock & Lotterhos 2015) | Univariate FST with trimmed null | Robust to demography via trimmed-tail null | Conservative; misses weak-effect polygenic |
| pcadapt (Luu 2017) | PC-based Mahalanobis | Handles continuous structure; no need to define populations | Detects axes-of-divergence loci; not environment-specific |
| LFMM (Frichot 2013) | MCMC mixed model with latent factors | Original framework | Slow; superseded by LFMM2 |
| LFMM2 (Caye 2019) | LSE-based mixed model with K latent factors | Fast; orders of magnitude faster than LFMM; modern default | K choice is critical; wrong K silently invalidates results |
| BayPass Core (Gautier 2015) | Bayesian FST with covariance matrix Omega | Explicit shared-history correction via Omega | Computationally heavy; convergence needs care |
| BayPass AUX | Bayesian env association with binary auxiliary variable | Posterior gives Bayes Factor per locus | Same as Core |
| BayPass C2 | Bayesian contrast between two pre-defined groups | Like Bayesian Fisher exact | Requires pre-defined groups, not continuous env |
| BayPass IS | Importance-sampling joint Bayesian | Multiple covariates simultaneously | Most computationally expensive |
| RDA (Forester 2018) | Multivariate constrained ordination | HIGH power and LOW FDR for polygenic adaptation | Requires imputed genotypes; less power for monogenic |
| pRDA (partial RDA) | RDA conditioning out population structure | Controls for structure explicitly | Conservative; depends on which axes are conditioned out |
| Gradient forests (Ellis 2012; Ellis-Smith-Pitcher) | Random-forest non-linear GEA | Detects non-linear gene-environment | Less interpretable; no formal p-values |
| RDA offset (Capblancq 2021) | Linear genomic-offset prediction | Linear gradient assumption | Fails under highly novel future climate (Lind 2025) |
| Gradient-forest offset | Non-linear genomic-offset prediction | Captures non-linearity | Same three-regime caveat |
| RONA | Locus-by-locus offset | Simple, transparent | Locus-specific; ignores multilocus structure |
| Circuitscape (McRae 2008) | Circuit-theory landscape resistance | Integrates ALL paths; not single-best | Symmetric only; asymmetric landscapes need directional methods |
| ResistanceGA (Peterman 2018) | Genetic-algorithm optimization of resistance | Optimizes cost surface itself | MLPE parameterization needed (specific lmer form) |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Monogenic local adaptation | OutFLANK or BayPass Core; cross-check with simulations | Demography-calibrated null |
| Polygenic local adaptation | RDA with environmental matrix; pRDA conditioning on structure | Forester 2018 superior power + lower FDR |
| Environmental association with structure correction | LFMM2 (K from sNMF cross-entropy elbow) | Modern default; orders of magnitude faster than LFMM |
| Binary group contrast | BayPass C2 | Like Bayesian Fisher exact |
| Joint multi-covariate Bayesian inference | BayPass IS | Multiple env simultaneously |
| Quantifying maladaptation under climate change | RDA offset OR gradientForest offset | Report Lind 2025 caveat: works for interpolation, fails for novel |
| Multi-method consensus | Run OutFLANK + LFMM2 + BayPass; overlap is high-confidence | Method differences = methodological coverage |
| Mapping landscape resistance | Circuitscape + ResistanceGA optimization | Circuitscape integrates all paths; ResistanceGA optimizes the surface |
| Distinguishing IBD vs IBE | dbRDA variance partitioning (geographic + env) | Mantel-based methods have known autocorrelation issues |
| Sampling design optimization | Paired contrasts at environmental endpoints; cite Lotterhos & Whitlock 2015 | Most powerful under demographic concern |
| Polyploid species | polyRAD / fitPoly / updog FIRST; then standard GEA | Diploid-assuming tools give biased FST estimates |

## LFMM2 with Mandatory K Selection

**Goal:** Identify loci significantly associated with environmental variables while controlling for unobserved demographic structure via K latent factors.

**Approach:** Run sNMF on the genotype matrix across K = 1...10 (or higher), compute cross-entropy at each K, pick K at the elbow (where cross-entropy first plateaus), then pass that K to `LEA::lfmm2()`. Wrong K silently invalidates results — too few K means residual structure confounds environment; too many K absorbs the environmental signal.

```r
library(LEA)
library(qvalue)

# Convert VCF -> LFMM/GENO format
vcf2lfmm('variants.vcf', 'genotypes.lfmm')
vcf2geno('variants.vcf', 'genotypes.geno')

# MANDATORY K selection via sNMF cross-entropy elbow
# Run multiple repetitions per K (5 minimum) for stability
snmf_result <- snmf('genotypes.geno', K = 1:10, repetitions = 5,
                     entropy = TRUE, project = 'new')
ce_values <- sapply(1:10, function(k) min(cross.entropy(snmf_result, K = k)))
plot(1:10, ce_values, xlab = 'K', ylab = 'Cross-entropy',
     pch = 19, col = 'blue', type = 'b')

# Pick K at elbow (first plateau); report sensitivity across K
best_K <- which.min(ce_values)

# Run LFMM2 with selected K
genotypes <- read.lfmm('genotypes.lfmm')
env_vars <- read.env('environment.env')
lfmm_result <- lfmm2(input = genotypes, env = env_vars, K = best_K)

# Test associations with genomic-control calibration
pvalues <- lfmm2.test(lfmm_result, input = genotypes, env = env_vars,
                       full = TRUE, genomic.control = TRUE)

# Check genomic inflation factor (GIF / lambda)
# Target ~1.0; > 1.5 means insufficient structure correction (try larger K)
# < 0.5 means over-correction (try smaller K)
gif <- median(qchisq(1 - pvalues$pvalues[, 1], df = 1)) / qchisq(0.5, df = 1)
cat('Genomic inflation factor (lambda):', round(gif, 3), '\n')

# Storey FDR control
qvals <- qvalue(pvalues$pvalues[, 1])$qvalues
candidates <- which(qvals < 0.05)
cat('Candidate adaptive loci (q < 0.05):', length(candidates), '\n')

# Sensitivity check: re-run with K +/- 1 and report overlap of candidates
# Loci detected only at one K are sensitive to latent-factor choice; flag as lower-confidence
```

## RDA — Capblancq & Forester 2021 Swiss-Army-Knife Workflow

**Goal:** Detect polygenic local adaptation via multivariate constrained ordination, with optional climate-offset prediction.

**Approach:** Apply the Capblancq & Forester 2021 RDA workflow: (1) variable selection via forward selection with adjusted R^2; (2) variance partitioning into pure-environment / pure-spatial / shared; (3) GEA outlier identification at SD > 3 on RDA axes 1-3; (4) adaptive-index computation; (5) genomic-offset prediction with the Lind 2025 three-regime caveat. **CRITICAL: genotypes must be imputed before RDA** (no missing data); cite Forester 2018 for the polygenic-power result.

```r
library(vegan)

# CRITICAL: impute missing genotypes BEFORE RDA (Forester 2018 benchmark requirement)
# Column-mean imputation per locus is the simplest valid choice;
# population-stratified mean imputation is preferred when populations are known.
# For LEA-generated data, LEA::impute() is the canonical option.
for (j in seq_len(ncol(allele_freq))) {
    col_mean <- mean(allele_freq[, j], na.rm = TRUE)
    allele_freq[is.na(allele_freq[, j]), j] <- col_mean
}

# Partial RDA conditioning on population structure (e.g., Q-matrix from sNMF)
# This is pRDA per Capblancq 2021
rda_result <- rda(allele_freq ~ temperature + precipitation + altitude +
                  Condition(as.matrix(q_matrix)), data = env_data)

# Permutation test
anova(rda_result, permutations = 999)

# Variance partitioning (Capblancq workflow step 2)
vp <- varpart(allele_freq, env_data, q_matrix)
vp$part$fract  # pure env / shared / pure structure / residual

# GEA outliers (z-score > 3 on RDA axes 1-3)
# Threshold of 3 SD is conservative; for polygenic adaptation, may use 2.5 SD
loadings <- scores(rda_result, choices = 1:3, display = 'species')
zscores <- apply(loadings, 2, function(x) (x - mean(x)) / sd(x))
rda_candidates <- which(apply(abs(zscores), 1, max) > 3)
cat('RDA candidate loci (|z| > 3):', length(rda_candidates), '\n')
```

## BayPass — Core, AUX, C2, IS Models

**Goal:** Bayesian Genotype-Environment Association with explicit population-history correction via covariance matrix Omega.

**Approach:** Convert VCF to BayPass's space-separated allele-count format. Run Core (estimates Omega; like Bayesian FST); use AUX for binary env-association testing; C2 for two-group contrast; IS for joint multi-covariate.

```bash
# BayPass input: space-separated allele counts, NOT VCF
# Use vcf2baypass.pl OR bcftools query to convert

# Core model: estimate Omega (population covariance from genome-wide SNPs)
g_baypass -gfile geno_BayPass.txt -outprefix core_run -nthreads 4

# AUX (binary auxiliary variable): test environmental association
# omegafile from Core run; covariates is samples x env file
g_baypass -gfile geno_BayPass.txt -efile env_BayPass.txt \
          -omegafile core_run_mat_omega.out \
          -outprefix aux_run -auxmodel -nthreads 4

# C2 (contrast between two pre-defined groups)
# contrasts.txt: 1 = group 1, -1 = group 2, 0 = excluded
g_baypass -gfile geno_BayPass.txt -contrastfile contrasts.txt \
          -omegafile core_run_mat_omega.out \
          -outprefix c2_run -nthreads 4

# Bayes Factor > 20 dB: strong evidence
# Bayes Factor > 30 dB: decisive evidence
# Convert: BFis (decibel scale) = 10 * log10(BF)
```

## Genomic Offset — Lind & Lotterhos 2025 Three-Regime Framework

**Goal:** Predict maladaptation under future climate using genomic-offset methods (gradientForest, RDA-offset, LFMM2offset, RONA) while characterizing prediction-novelty. For the broader genomic-prediction review (foundation of the offset literature), see Capblancq et al. 2020 *Annu Rev Ecol Evol Syst* 51:245-269.

**Approach:** Compute offset per location as the distance in transformed genomic-environmental space between current and future predicted climate. CRITICAL: characterize whether each prediction falls into regime 1 (interpolation), regime 2 (modest extrapolation), or regime 3 (highly novel, where offset is uninformative or misleading). Report offset alongside prediction-novelty mapping.

```r
library(gradientForest)
library(terra)

# Fit gradient forests on candidate loci x environment
gf <- gradientForest(cbind(env_predictors, allele_data),
                     predictor.vars = colnames(env_predictors),
                     response.vars = colnames(allele_data),
                     ntree = 500, trace = FALSE)

# Variable importance (which env drives most allele turnover)
plot(gf, plot.type = 'Overall.Importance')

# Predict genetic offset under current vs future
current <- rast('bioclim_current.tif')
future <- rast('bioclim_2070_ssp585.tif')
current_vals <- extract(current, sampling_coords)
future_vals <- extract(future, sampling_coords)

# Genomic offset = Euclidean distance in transformed space
current_transformed <- predict(gf, current_vals)
future_transformed <- predict(gf, future_vals)
genetic_offset <- sqrt(rowSums((current_transformed - future_transformed)^2))

# CRITICAL: characterize prediction-novelty regime per location
# For each future location, compute distance to nearest training-data envelope
# locations in regime 3 (high novelty) should have offset values down-weighted
# in interpretation per Lind & Lotterhos 2025

# Cross-validation with multiple offset methods (gradientForest + RDA + LFMM2offset)
# Robust signals appear in ALL methods; method-specific offset is suspect
```

## Per-Method Failure Modes

### LFMM2 with wrong K silently invalidates results

**Trigger:** Running LFMM2 with K too small (residual structure confounds environment) or K too large (latent factors absorb the environmental signal).

**Mechanism:** LFMM2 uses K latent factors to capture unobserved population structure. Wrong K means structure is either undercorrected (false positives) or overcorrected (false negatives), with no error message.

**Symptom:** Thousands of significant SNPs (too small K) OR almost none (too large K); genomic inflation factor lambda far from 1.0.

**Fix:** Use sNMF cross-entropy elbow as the primary K choice; run LFMM2 at K-1, K, K+1 and report sensitivity; flag loci detected at only one K as lower-confidence.

### RDA on un-imputed genotypes silently degrades

**Trigger:** Running RDA on an allele-frequency matrix with NA values without imputation.

**Mechanism:** RDA cannot handle missing data internally; default behavior is to use `na.omit` which drops loci AND samples. Forester 2018's RDA-dominance benchmark assumed imputed genotypes.

**Symptom:** Effective sample size much smaller than expected; results sensitive to which loci have missing data.

**Fix:** Impute missing genotypes (mean within population, kNN, or `snmf::impute()`) BEFORE running RDA.

### Genomic offset reported without prediction-novelty characterization

**Trigger:** Producing a country-wide genomic-offset map without indicating which areas are inside vs outside the training-data envelope.

**Mechanism:** Per Lind & Lotterhos 2025, genomic-offset accuracy declines with novelty of the predicted environment. Highly novel future climates fall in "regime 3" where offset is uninformative.

**Symptom:** Map shows highest predicted maladaptation in geographically extreme areas; cross-validation with multiple methods shows divergent predictions.

**Fix:** Compute prediction novelty per location (e.g., Mahalanobis distance to training envelope); annotate offset values with their regime; report cross-method consensus rather than single-method offset.

### OutFLANK applied to continuous sampling design

**Trigger:** Running OutFLANK on continuous-gradient samples treated as a single "population".

**Mechanism:** OutFLANK assumes distinct, well-defined populations for FST calculation. Continuous sampling does not have natural population delimitation; the FST distribution depends arbitrarily on how samples are binned.

**Symptom:** OutFLANK results unstable to alternative population definitions; very few or impossibly many outliers.

**Fix:** Use LFMM2 or RDA for continuous gradient data; OutFLANK is appropriate when distinct populations are defined a priori.

### LDNe physical-linkage trap on RAD-seq SNPs

**Trigger:** Running LFMM2 / RDA / OutFLANK on RAD-seq SNPs without LD pruning.

**Mechanism:** Physical linkage among RAD-seq SNPs creates correlated test statistics; outlier counts are inflated by chromosomal clustering rather than independent adaptation signal.

**Symptom:** Outliers cluster in large blocks along the genome; individual-locus inference is dominated by linkage.

**Fix:** LD-prune SNPs (PLINK `--indep-pairwise 50 5 0.2`) before GEA; OR thin to >= 1 cM apart with a genetic map.

## Quantitative Thresholds

| Threshold | Value | Source / rationale |
|-----------|-------|-------------------|
| LFMM2 K selection | Cross-entropy elbow from sNMF (`LEA`) | Caye 2019; sensitivity check at K-1, K+1 |
| Genomic inflation factor target | Lambda ~ 1.0 | > 1.5 = under-correction; < 0.5 = over-correction |
| FDR threshold | q < 0.05 (Storey) | qvalue package; more powerful than BH for genomic data |
| RDA outlier threshold | abs(z) > 3 on RDA axes 1-3 | Capblancq & Forester 2021 conservative; 2.5 for polygenic |
| BayPass Bayes Factor | BF > 20 dB strong; > 30 dB decisive | Gautier 2015 convention |
| OutFLANK trim fractions | LeftTrim = RightTrim = 0.05 | Whitlock & Lotterhos 2015 default |
| OutFLANK Hmin | 0.1 | Exclude low-heterozygosity unreliable FST |
| Forester 2018 RDA imputation | Required (no missing data) | RDA performance benchmark assumed imputed genotypes |
| Lind & Lotterhos 2025 offset regimes | Regime 1 (interpolation) / 2 (modest extrapolation) / 3 (highly novel) | Characterize per location |
| Lotterhos & Whitlock 2015 sampling design | Paired contrasts > random > transects under demographic concern | Genome-scan power |

## Common errors

| Error | Cause | Solution |
|-------|-------|----------|
| LFMM2 returns thousands of significant SNPs | K too small | Increase K via sNMF cross-entropy elbow |
| LFMM2 returns no significant SNPs | K too large; signal absorbed | Decrease K |
| Lambda (GIF) >> 1.5 | Insufficient structure correction | Increase K or add structure covariate |
| RDA effective N much smaller than total | NA values in allele matrix | Impute before RDA |
| pcadapt screeplot shows no elbow | Continuous population structure or single-cline data | Switch to LFMM2 or RDA |
| OutFLANK error about populations | Continuous sampling, no defined populations | Use LFMM2 / RDA instead |
| BayPass "format error" | Passing VCF directly | Convert to space-separated allele counts via vcf2baypass.pl |
| Gradient-forest plot blank | Insufficient SNPs in candidate set | Increase candidate-locus pool |
| Genomic offset highest in intermediate climate | PC axes capture environment; structure absorbing signal | pRDA conditioning on geographic distance |

## References

- Frichot E, Schoville SD, Bouchard G, François O (2013) LFMM. *Mol Biol Evol* 30(7):1687-1699. doi:10.1093/molbev/mst063
- Caye K, Jumentier B, Lepeule J, François O (2019) LFMM 2: fast LSE estimator. *Mol Biol Evol* 36(4):852-860. doi:10.1093/molbev/msz008
- Gain C, François O (2021) LEA 3 package. *Mol Ecol Resour* 21(8):2738-2748. doi:10.1111/1755-0998.13366
- Gautier M (2015) BayPass. *Genetics* 201(4):1555-1579. doi:10.1534/genetics.115.181453
- Forester BR, Lasky JR, Wagner HH, Urban DL (2018) Multilocus adaptation methods: RDA superior. *Mol Ecol* 27(9):2215-2233. doi:10.1111/mec.14584
- Capblancq T, Forester BR (2021) RDA Swiss-army-knife for landscape genomics. *Methods Ecol Evol* 12(12):2298-2309. doi:10.1111/2041-210X.13722
- Capblancq T, Fitzpatrick MC, Bay RA, Exposito-Alonso M, Keller SR (2020) Genomic prediction of (mal)adaptation. *Annu Rev Ecol Evol Syst* 51:245-269. doi:10.1146/annurev-ecolsys-020720-042553
- Whitlock MC, Lotterhos KE (2015) OutFLANK. *Am Nat* 186(S1):S24-S36. doi:10.1086/682949
- Lotterhos KE, Whitlock MC (2014) Demographic confounders of FST outlier tests. *Mol Ecol* 23(9):2178-2192. doi:10.1111/mec.12725
- Lotterhos KE, Whitlock MC (2015) Sampling-design optimization for genome scans. *Mol Ecol* 24(5):1031-1046. doi:10.1111/mec.13100
- Lind BM, Lotterhos KE (2025) Accuracy of predicting maladaptation. *Mol Ecol Resour* 25:e14008. doi:10.1111/1755-0998.14008
- Wang IJ, Bradburd GS (2014) Isolation by environment (IBD vs IBE). *Mol Ecol* 23(23):5649-5662. doi:10.1111/mec.12938
- McRae BH, Dickson BG, Keitt TH, Shah VB (2008) Circuitscape circuit-theory. *Ecology* 89(10):2712-2724. doi:10.1890/07-1861.1
- Peterman WE (2018) ResistanceGA. *Methods Ecol Evol* 9(6):1638-1647. doi:10.1111/2041-210X.12984
- Ellis N, Smith SJ, Pitcher CR (2012) Gradient forests. *Ecology* 93(1):156-168. doi:10.1890/11-0252.1
- Aguirre-Liguori JA, Ramírez-Barahona S, Gaut BS (2021) Evolutionary genomics of climate response. *Nat Ecol Evol* 5(10):1350-1360. doi:10.1038/s41559-021-01526-9
- Hoban S, Kelley JL, Lotterhos KE et al. (2016) Finding the genomic basis of local adaptation. *Am Nat* 188(4):379-397. doi:10.1086/688018
- Luu K, Bazin E, Blum MGB (2017) pcadapt: an R package to perform genome scans for selection based on principal component analysis. *Mol Ecol Resour* 17(1):67-77. doi:10.1111/1755-0998.12592
- Legendre P, Fortin M-J (2010) Comparison of the Mantel test and alternative approaches for detecting complex multivariate relationships. *Mol Ecol Resour* 10(5):831-844. doi:10.1111/j.1755-0998.2010.02866.x

## Related Skills

- ecological-genomics/conservation-genetics - Population genetic health (Ne, F_ROH); use ESU/MU framework not species delimitation for management units
- ecological-genomics/community-ecology - Environmental gradient analysis for species composition (analog of GEA for community data)
- population-genetics/selection-statistics - Selection scans in human population genetics
- population-genetics/population-structure - STRUCTURE / ADMIXTURE for substructure inference
- variant-calling/vcf-basics - VCF preparation from RAD-seq or WGS
<!-- END FILE: ecological-genomics/landscape-genomics/SKILL.md -->

## 子目录：ecological-genomics/species-delimitation

<!-- BEGIN FILE: ecological-genomics/species-delimitation/SKILL.md -->
---
name: bio-ecological-genomics-species-delimitation
description: Delimits putative species boundaries from molecular data within the de Queiroz 2007 unified-lineage framework using ASAP (Puillandre 2021 successor to ABGD), mPTP C++ (Kapli 2017 successor to bPTP; bPTP is Python NOT R), GMYC single/multi-threshold (Pons 2006; Fujisawa 2013), multilocus BPP v4 with prior calibration from data (NOT defaults; Yang 2015), SNAPP + BFD* for SNP delimitation, DELINEATE (Sukumaran 2021) speciation-process modeling to address Sukumaran & Knowles 2017 PNAS critique that MSC delimits structure not species, integrative-taxonomy congruence (Padial 2010; Carstens 2013), Dsuite for introgression testing before sister claims (Malinsky 2021), and Meyer & Paulay 2005 barcoding-gap-absence caveat. Use when delineating species from DNA barcoding data, resolving cryptic complexes, choosing among ASAP/mPTP/BPP/DELINEATE, calibrating BPP priors, distinguishing introgression from ILS, or applying the Sukumaran-Knowles oversplitting correction.
tool_type: mixed
primary_tool: ASAP
---

## Version Compatibility

Reference examples tested with: ASAP (current CLI), mPTP (current C++), bPTP (Python from github.com/zhangjiajie/PTP), splits 1.0+ for GMYC, BPP 4.7+, SNAPP/BEAST 2.7+, DELINEATE (current Python), Dsuite 0.5+, ape 5.7+, fossil 0.4+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Species Delimitation

**"Delineate species boundaries from my DNA barcoding or genomic data"** -> Apply distance-based (ASAP) and tree-based (mPTP) methods for primary delimitation, multilocus coalescent (BPP) for genomic confirmation, DELINEATE for speciation-process modeling to address MSC oversplitting, integrative-taxonomy validation across multiple lines of evidence, and Dsuite to test introgression before claiming sister relationships.
- CLI: `asap` (downloadable C binary) OR web (https://bioinfo.mnhn.fr/abi/public/asap/) for single-locus primary delimitation
- CLI: `mptp` (https://github.com/Pas-Kapli/mptp) for tree-based multi-rate PTP (faster than bPTP)
- Python: `bPTP` (https://github.com/zhangjiajie/PTP) for legacy tree-based delimitation — NOTE: Python not R
- R: `splits::gmyc()` for GMYC on ultrametric trees
- CLI: `bpp` (https://bpp.github.io) for multilocus MSC delimitation; control-file driven
- CLI: `Dsuite` for D-statistics / f4-ratio / f-branch introgression testing

## The Single Most Important Modern Insight -- MSC Methods Delimit Structure, NOT Species

Sukumaran & Knowles 2017 *PNAS* 114(7):1607-1612 established that BPP, BFD*, and other multispecies-coalescent methods **delimit genetic structure, not species**. The mathematical reason: the MSC model treats every panmictic population as a "species" in the parameterization. Applied to data with substructure (isolated demes within a species), MSC methods partition that structure into "species" — leading to systematic oversplitting in published literature, especially in lizards, frogs, geckos, and insects.

**Modern best practice (post-2021):**
1. Run MSC methods (BPP, BFD*) as PRELIMINARY enumeration of candidate population lineages
2. Apply DELINEATE (Sukumaran 2021 *PLoS Comput Biol* 17:e1008924) to test which lineages have completed speciation vs are in the speciation process
3. Validate via integrative taxonomy (Padial 2010; Carstens 2013) — morphological, ecological, geographic congruence

A second cornerstone: **the barcoding gap is OFTEN absent in real data** (Meyer & Paulay 2005 *PLoS Biol* 3:e422). ABGD and ASAP are theoretically grounded in the gap; when the gap is absent, both fail gracefully but their output is unreliable. Always inspect the pairwise distance histogram.

A third: **Dsuite-checked introgression must precede sister-species claims.** D-statistics, f4-ratio, and f-branch (Malinsky 2021) distinguish admixture from incomplete lineage sorting; without this check, ILS-driven discordance is misinterpreted as gene flow.

## Algorithmic Taxonomy

| Method | Input | Approach | Strength | Fails when |
|--------|-------|----------|----------|------------|
| ASAP (Puillandre 2021) | Aligned sequences | Hierarchical-clustering distance partitioning with new scoring | Fast; modern; web + CLI | Single locus; works only if barcoding gap exists |
| ABGD (Puillandre 2012) | Aligned sequences | Distance gap-detection across priors | Legacy; superseded by ASAP | Less robust when gap is weak |
| GMYC (Pons 2006) | Ultrametric tree | Yule-coalescent transition threshold | Theoretical foundation | Requires time-calibrated tree |
| Multi-threshold GMYC (Fujisawa & Barraclough 2013) | Ultrametric tree | Per-lineage transition thresholds | Heterogeneous rates | Same; not always more powerful |
| bPTP (Zhang 2013) | Rooted phylogeny | Bayesian PTP MCMC | Posterior support per partition | Single intraspecific rate assumption; slower than mPTP |
| mPTP (Kapli 2017) | Rooted phylogeny | Multi-rate PTP, C++ | Faster (5+ orders); per-species intraspecific rates | Heterogeneity-friendly; for shallow phylogenies bPTP may be more powerful |
| BPP A10/A11 (Yang & Rannala) | Multi-locus alignments | Bayesian multispecies coalescent | Rigorous, multilocus | Computationally heavy; oversplits per Sukumaran-Knowles |
| SNAPP (Bryant 2012) | Biallelic SNP data | Coalescent species-tree bypassing gene trees | High-power genomic | Cubic complexity; not for very large datasets |
| BFD* (Leache 2014) | SNP data via SNAPP | Bayes-factor delimitation | Genomic-scale species hypothesis testing | Same oversplitting risk |
| DELINEATE (Sukumaran 2021) | BPP output + guide tree | Speciation-process modeling | Distinguishes structure from species | Requires preliminary delimitation as input |
| Dsuite (Malinsky 2021) | VCF + populations | D-statistic, f4-ratio, f-branch | Tests introgression vs ILS | Tree must accurately reflect history |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Primary species hypothesis from single locus | ASAP first; cross-check with mPTP | ASAP is the modern successor to ABGD; faster and better-scoring |
| Tree-based delimitation, heterogeneous intraspecific rates | mPTP | Per-species rate model; 5+ orders faster than bPTP |
| Tree-based delimitation, shallow phylogeny | bPTP (single-rate) or mPTP | When rates are similar, single-rate model may be more powerful |
| Time-calibrated tree from BEAST / chronos | GMYC (single or multi-threshold) | Requires ultrametric; both threshold variants worth comparing |
| Multilocus genomic delimitation | BPP A10/A11 + DELINEATE | BPP alone oversplits per Sukumaran-Knowles 2017 |
| SNP-based species hypothesis test | SNAPP + BFD* | Coalescent species-tree from biallelic SNPs |
| Confirm BPP result is not oversplitting | DELINEATE (Sukumaran 2021) | Speciation-process modeling distinguishes structure from species |
| Test introgression before sister-species claim | Dsuite (D, f4-ratio, f-branch) | Distinguishes admixture from ILS |
| Cryptic species complex | Integrative taxonomy: genetic + morphological + ecological congruence | Single-method conclusion unreliable |
| ABGD/ASAP returns no clear partition | Inspect pairwise distance histogram; do not force partition | Barcoding gap may be absent (Meyer & Paulay 2005) |
| Recently-diverged populations (Ne*t << 1) | Caution; MSC methods very prone to oversplit | Incomplete lineage sorting indistinguishable from shallow structure |
| Conservation management unit definition | Moritz 1994 ESU/MU framework, NOT MSC delimitation | Sukumaran-Knowles caveat applies |

## ASAP — The Modern Successor to ABGD

**Goal:** Primary species hypothesis from a single-locus alignment via hierarchical clustering of pairwise distances, scored by a new asap-score (Puillandre 2021).

**Approach:** Run ASAP via the web interface (https://bioinfo.mnhn.fr/abi/public/asap/) OR the downloadable C binary. ASAP ranks candidate partitions by asap-score (lower = better); always inspect the top 5-10 partitions, not just the best, and check for large score gaps that signal robust partitioning. Output: ranked species partitions with asap-score, p-value, and threshold distance per partition.

```bash
# ASAP CLI (downloadable C binary)
# Substitution model: K2P standard for COI; p-distance for very closely related; JC for general
./asap -d K2P -o asap_results/ aligned_sequences.fasta

# Inspect output
# - asap_output.csv: ranked partitions by asap-score (lower = better)
# - Always look at top 5-10 partitions; large score gaps = robust partitioning
# - The "best" partition is the top-ranked; report secondary partitions too
```

```python
# Python ASAP-style analysis for inspection (NOT a substitute for ASAP)
# Useful for understanding the distance landscape
from Bio import AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
import numpy as np
import matplotlib.pyplot as plt

alignment = AlignIO.read('aligned_sequences.fasta', 'fasta')
calc = DistanceCalculator('identity')  # use K2P-friendly model in practice
dm = calc.get_distance(alignment)

names = [r.id for r in alignment]
n = len(names)
dist_array = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        dist_array[i][j] = dm[names[i], names[j]]

# Inspect distance histogram for barcoding gap (often ABSENT per Meyer & Paulay 2005)
upper = dist_array[np.triu_indices(n, k=1)]
plt.hist(upper, bins=50)
plt.xlabel('Pairwise distance')
plt.ylabel('Frequency')
plt.title('Distance histogram — look for bimodality (gap)')
plt.savefig('barcoding_gap_histogram.pdf')

# Hierarchical clustering at threshold scan
condensed = squareform(dist_array)
Z = linkage(condensed, method='average')
thresholds = np.arange(0.01, 0.10, 0.005)
for t in thresholds:
    clusters = fcluster(Z, t=t, criterion='distance')
    print(f'Threshold {t:.3f}: {len(set(clusters))} groups')
```

## mPTP — Multi-Rate PTP for Heterogeneous Intraspecific Rates

**Goal:** Delimit species from a phylogeny by detecting the transition from speciation to coalescent branching rates, allowing per-species intraspecific rates (Kapli 2017).

**Approach:** Run mPTP on a rooted ML tree (e.g., from RAxML or IQ-TREE). mPTP's multi-rate model is more flexible than bPTP's single-rate; for shallow phylogenies with similar rates, bPTP may be competitive. mPTP is C++ (5+ orders of magnitude faster than bPTP), available from https://github.com/Pas-Kapli/mptp.

```bash
# mPTP installation: build from C source
# git clone https://github.com/Pas-Kapli/mptp
# cd mptp && ./autogen.sh && ./configure && make

# Run mPTP ML inference
mptp --ml --tree_file rooted_tree.nwk --output_file mptp_ml

# MCMC for posterior support
mptp --mcmc 1000000 --mcmc_sample 1000 --mcmc_burnin 100000 \
     --tree_file rooted_tree.nwk --output_file mptp_mcmc

# Output: species partition with branch annotations
# > 0.95 posterior support: strong; 0.80-0.95: moderate; < 0.80: uncertain
```

## bPTP — Legacy Tree-Based Delimitation (Python, NOT R)

**Goal:** Bayesian Poisson Tree Processes delimitation with single intraspecific rate (Zhang 2013).

**Approach:** Run bPTP via the Python package from https://github.com/zhangjiajie/PTP (NOTE: this is a Python tool, NOT an R package; `install.packages('PTP')` does not exist). For heterogeneous-rate data, prefer mPTP.

```bash
# bPTP Python install (NOT R)
pip install git+https://github.com/iTaxoTools/PTP-pyqt5

# Run bPTP MCMC
python -m PTP.PTP -t rooted_tree.nwk -o bptp_results \
    --type bayesian --ngen 100000 --burnin 0.1 --seed 42

# Output: posterior support per species partition (> 0.95 strong)
# bPTP over-splits when populations have strong geographic substructure
# Cross-check with ASAP and/or mPTP for consensus
```

## GMYC with Mandatory Ultrametric Tree

**Goal:** Detect the threshold on an ultrametric phylogeny where branching transitions from interspecific (Yule) to intraspecific (coalescent).

**Approach:** Convert ML tree to ultrametric with `ape::chronos` (penalized likelihood) or BEAST (Bayesian time-calibration), then run GMYC. Single-threshold vs multi-threshold; multi-threshold handles heterogeneous rates across the tree.

```r
library(splits)
library(ape)

tree <- read.tree('rooted_tree.nwk')

# Convert to ultrametric (REQUIRED for GMYC)
# chronos: penalized likelihood; lambda=1 mid-clock
# For rigorous time-calibration, use BEAST2 instead
ultrametric_tree <- chronos(tree, lambda = 1)
class(ultrametric_tree) <- 'phylo'
stopifnot(is.ultrametric(ultrametric_tree))

# Single-threshold GMYC
gmyc_single <- gmyc(ultrametric_tree, method = 'single')
summary(gmyc_single)
cat('GMYC species (single-threshold):', gmyc_single$entity[1], '\n')
cat('LR test p-value:', gmyc_single$p.value[1], '\n')

# Multi-threshold for heterogeneous rates
gmyc_multi <- gmyc(ultrametric_tree, method = 'multiple')
summary(gmyc_multi)

# Compare single vs multi-threshold; report both
species_single <- spec.list(gmyc_single)
species_multi <- spec.list(gmyc_multi)
```

## BPP A10/A11 — Multilocus MSC Delimitation with Calibrated Priors

**Goal:** Bayesian multilocus species delimitation under the multispecies coalescent (Yang & Rannala 2010; current Flouri 2018 BPP v4).

**Approach:** Configure BPP A10 (joint delimitation + species tree estimation) with priors on theta and tau ESTIMATED FROM DATA — NOT defaults. Yang 2015 *Curr Zool* 61:854-865 gives explicit guidance: `thetaprior = G(2, 2000)` for small/moderate data; tighter for large genomic data. Wrong priors dominate the analysis.

```text
# BPP control file for A10 analysis
# CRITICAL: priors below are CALIBRATED to data, not defaults
# Defaults are tuned for primate-mammal data; insects/fish/plants need adjustment

seed = 12345

seqfile = alignment.phy
Imapfile = imap.txt                   # map individuals -> putative species
outfile = bpp_results.txt
mcmcfile = bpp_mcmc.txt

speciesdelimitation = 1 0 2 0.5       # 1 = delimitation mode; rjMCMC parameters
speciestree = 1                       # 1 = estimate species tree
speciesmodelprior = 1                 # 1 = uniform prior on rooted trees

species&tree = 4  speciesA speciesB speciesC speciesD
                  10 8 12 6
                  ((speciesA, speciesB), (speciesC, speciesD));

# CALIBRATED theta prior (per-locus nucleotide diversity)
# G(2, 2000) -> mean = 0.001 (calibrate from observed per-locus pi)
# Yang 2015 Curr Zool 61:854 has taxon-specific recommendations
thetaprior = 2 2000

# CALIBRATED tau prior (divergence times)
# Calibrate from observed maximum genetic distance / mutation rate
tauprior = 2 2000

# MCMC
nsample = 100000
sampfreq = 2
burnin = 50000

# Run multiple independent chains; check convergence
```

```bash
# Run BPP with multiple independent chains
for i in 1 2 3 4; do
    bpp --cfile bpp_control.bpp --seed $((1000 * i)) --out bpp_run_$i.txt &
done
wait

# Compare chains; posterior probabilities must agree across chains
# PP > 0.95 for a delimitation: strong support
# PP 0.50-0.95: moderate; integrate other evidence
```

## DELINEATE — Addressing the Sukumaran-Knowles Oversplitting

**Goal:** Test whether candidate lineages from BPP represent fully-formed species OR incomplete-speciation structure (Sukumaran 2021).

**Approach:** Provide DELINEATE with a guide tree of population lineages and a hypothesis about which are species. The output: probability that each population lineage is a true species vs an incipient lineage. THE post-2021 best practice complement to BPP.

```bash
# DELINEATE (https://github.com/jsukumaran/delineate)
# Python tool
pip install delineate

# Configure delineate input
# - guide tree: rooted Newick with population lineages as tips
# - constraint file: which tips are confirmed species, which to test
delineate-estimate partitions \
    --tree-file population_lineage_tree.nwk \
    --config-file delineate_config.json \
    --output-prefix delineate_run

# Output: probability that each lineage is a species
# Use ALONGSIDE BPP; do not claim species from BPP alone post-2021
```

## Dsuite — Introgression vs Incomplete Lineage Sorting

**Goal:** Test for introgression before claiming sister-species relationships, distinguishing admixture from ILS.

**Approach:** Compute D-statistic (ABBA-BABA), f4-ratio (admixture fraction), and f-branch (Malinsky 2021 *Mol Ecol Resour* 21:584-595) on a VCF with population assignments. Non-zero D indicates introgression between H3 and one of H1/H2.

```bash
# Dsuite (https://github.com/millanek/Dsuite)
# Sets file: 3 columns (sample_id, population/species, optional outgroup tag)
# Tree file: Newick with population names matching the sets file

# All-trio D-statistic
Dsuite Dtrios -t species_tree.nwk sets.txt input.vcf.gz

# F-branch decomposition (more interpretable than raw D)
Dsuite Fbranch species_tree.nwk Dtrios_output_tree.txt > fbranch.txt

# Plot f-branch matrix
dtools.py fbranch.txt species_tree.nwk

# D > 0 with |Z| > 3: significant ABBA-BABA imbalance -> introgression
# f4-ratio gives the admixture fraction estimate
```

## Per-Method Failure Modes

### MSC delimitation oversplits population structure as species

**Trigger:** Running BPP, BFD*, or other multispecies-coalescent methods on data with within-species substructure (isolated demes), then claiming the delimited lineages are species.

**Mechanism:** The MSC model treats every panmictic population as a "species" in its parameterization (Sukumaran & Knowles 2017). When applied to data with population substructure, MSC partitions that structure into "species."

**Symptom:** Many "species" delimited; each with low sample size; lineages defined by geography rather than morphology; BPP posterior support is high but biological reality is unclear.

**Fix:** Run DELINEATE (Sukumaran 2021) on the BPP output to test which lineages have completed speciation. Validate via integrative taxonomy (Padial 2010): require congruence across genetic + morphological + ecological evidence before publishing species.

### ABGD/ASAP forced to partition data without a barcoding gap

**Trigger:** Reporting "best partition" from ABGD or ASAP when the pairwise distance histogram is unimodal (no gap).

**Mechanism:** ABGD and ASAP detect a gap in the pairwise-distance distribution that separates intra- from inter-specific divergences. Meyer & Paulay 2005 *PLoS Biol* 3:e422 demonstrated the gap is frequently absent.

**Symptom:** Distance histogram is unimodal (no clear bimodality); ASAP partitions have similar scores across many K values; ABGD priors disagree.

**Fix:** Inspect the distance histogram first; if no clear gap, do NOT report ASAP/ABGD results as definitive; integrate other lines of evidence.

### bPTP oversplit on populations with strong substructure

**Trigger:** Running bPTP on a tree where the same biological species has multiple isolated demes contributing genetic structure.

**Mechanism:** bPTP detects branching-rate shifts as species boundaries; isolated demes within a species show coalescent-rate branching that bPTP partitions as separate species.

**Symptom:** More bPTP species than morphologically recognized; species correspond to geographic regions.

**Fix:** Cross-check with ASAP (more conservative) and with mPTP at multi-rate option; treat bPTP/mPTP as preliminary; require congruence with other lines of evidence.

### BPP with default theta and tau priors

**Trigger:** Running BPP without calibrating priors to the data; using priors copied from a primate/mammal example file.

**Mechanism:** BPP results depend critically on theta (per-locus nucleotide diversity) and tau (divergence time) priors. Default priors are typically tuned for mammal data; for insects, fish, plants with different mutation-rate and Ne contexts, defaults can dominate the posterior.

**Symptom:** Posterior support clusters at 1.0 OR 0.0; results inconsistent with morphological / ecological data; sensitivity to alternative priors is very high.

**Fix:** Calibrate priors from data per Yang 2015 *Curr Zool* 61:854: estimate per-locus heterozygosity for theta mean; estimate divergence times from observed maximum genetic distances and mutation rate.

### Reporting D-statistic without f-branch

**Trigger:** Reporting raw D-statistics for many taxa without decomposing introgression patterns.

**Mechanism:** D-statistic measures asymmetric site-pattern counts; with taxon-rich datasets, D > 0 can be confounded by ancient introgression in the outgroup or by ghost lineages. f-branch (Malinsky 2018) decomposes admixture across the tree more interpretably.

**Symptom:** Many trios with D > 0; difficult to identify which specific introgression event drives the pattern.

**Fix:** Report f-branch decomposition alongside D; check for consistent patterns across phylogenetic levels.

## Quantitative Thresholds

| Threshold | Value | Source / rationale |
|-----------|-------|-------------------|
| COI K2P "species" cutoff | typically 2-3% pairwise distance (variable) | Animal barcoding convention; verify per taxon |
| ASAP score gap signaling robust partition | Large drop between consecutive scores | Puillandre 2021; inspect top 5-10 partitions |
| bPTP/mPTP posterior support | > 0.95 strong; 0.80-0.95 moderate; < 0.80 uncertain | Standard Bayesian inference |
| GMYC LR test p-value | < 0.05 detects significant transition | Pons 2006 |
| BPP posterior probability | > 0.95 strong; 0.50-0.95 moderate; < 0.50 uncertain | Yang 2015 |
| BPP minimum independent chains | 4 with different seeds | Convergence check |
| Dsuite D significance | |Z| > 3 | Standard test statistic |
| Sukumaran-Knowles validation rule | DELINEATE OR integrative-taxonomy congruence required post-2021 | Modern best practice |
| Integrative taxonomy congruence | Genetic + morphological + ecological all support hypothesis | Padial 2010; Carstens 2013 |

## Common errors

| Error | Cause | Solution |
|-------|-------|----------|
| ABGD/ASAP returns no clear partition | Barcoding gap absent in data | Inspect distance histogram; do not force partition |
| bPTP install error in R | bPTP is Python, NOT R | `pip install git+https://github.com/iTaxoTools/PTP-pyqt5` |
| GMYC error "not ultrametric" | ML tree directly fed without chronos | Run `ape::chronos()` first or use BEAST output |
| BPP all PP = 1.0 (oversplit) | Default priors too informative; population substructure | Calibrate priors from data; run DELINEATE alongside |
| BPP no convergence across chains | Insufficient burnin or sampling | Increase nsample and burnin; multiple chains |
| Dsuite format error | Sets file column ordering | First column = sample ID, second = species/population |
| mPTP not found | Build from source github.com/Pas-Kapli/mptp | `pip install mptp` does not exist |
| ASAP web upload "too many sequences" | > 10^4 sequences | Use downloadable C binary instead of web |

## References

- de Queiroz K (2007) Species concepts and species delimitation. *Syst Biol* 56(6):879-886. doi:10.1080/10635150701701083
- Pons J, Barraclough TG, Gomez-Zurita J et al. (2006) GMYC original. *Syst Biol* 55(4):595-609. doi:10.1080/10635150600852011
- Fujisawa T, Barraclough TG (2013) Revised GMYC. *Syst Biol* 62(5):707-724. doi:10.1093/sysbio/syt033
- Puillandre N, Lambert A, Brouillet S, Achaz G (2012) ABGD original. *Mol Ecol* 21(8):1864-1877. doi:10.1111/j.1365-294X.2011.05239.x
- Puillandre N, Brouillet S, Achaz G (2021) ASAP. *Mol Ecol Resour* 21(2):609-620. doi:10.1111/1755-0998.13281
- Zhang J, Kapli P, Pavlidis P, Stamatakis A (2013) PTP / bPTP. *Bioinformatics* 29(22):2869-2876. doi:10.1093/bioinformatics/btt499
- Kapli P, Lutteropp S, Zhang J et al. (2017) mPTP. *Bioinformatics* 33(11):1630-1638. doi:10.1093/bioinformatics/btx025
- Yang Z, Rannala B (2010) BPP original. *Proc Natl Acad Sci USA* 107(20):9264-9269. doi:10.1073/pnas.0913022107
- Yang Z (2015) BPP review with prior guidance. *Curr Zool* 61(5):854-865. doi:10.1093/czoolo/61.5.854
- Flouri T, Jiao X, Rannala B, Yang Z (2018) BPP v4 genomic-scale. *Mol Biol Evol* 35(10):2585-2593. doi:10.1093/molbev/msy147
- Bryant D, Bouckaert R, Felsenstein J et al. (2012) SNAPP. *Mol Biol Evol* 29(8):1917-1932. doi:10.1093/molbev/mss086
- Leache AD, Fujita MK, Minin VN, Bouckaert RR (2014) BFD*. *Syst Biol* 63(4):534-542. doi:10.1093/sysbio/syu018
- Sukumaran J, Knowles LL (2017) MSC delimits structure, not species. *Proc Natl Acad Sci USA* 114(7):1607-1612. doi:10.1073/pnas.1607921114
- Sukumaran J, Holder MT, Knowles LL (2021) DELINEATE (speciation-process modeling). *PLoS Comput Biol* 17(5):e1008924. doi:10.1371/journal.pcbi.1008924
- Padial JM, Miralles A, De la Riva I, Vences M (2010) Integrative future of taxonomy. *Front Zool* 7:16. doi:10.1186/1742-9994-7-16
- Carstens BC, Pelletier TA, Reid NM, Satler JD (2013) How to fail at species delimitation. *Mol Ecol* 22(17):4369-4383. doi:10.1111/mec.12413
- Malinsky M, Matschiner M, Svardal H (2021) Dsuite. *Mol Ecol Resour* 21(2):584-595. doi:10.1111/1755-0998.13265
- Malinsky M, Svardal H, Tyers AM et al. (2018) Whole-genome sequences of Malawi cichlids reveal multiple radiations interconnected by gene flow (f-branch original). *Nat Ecol Evol* 2(12):1940-1955. doi:10.1038/s41559-018-0717-x
- Meyer CP, Paulay G (2005) Barcoding-gap-absence critique. *PLoS Biol* 3(12):e422. doi:10.1371/journal.pbio.0030422

## Related Skills

- ecological-genomics/edna-metabarcoding - Generate barcode sequences from environmental samples for primary delimitation
- ecological-genomics/conservation-genetics - Population-level genetic assessment (use ESU/MU framework, NOT species delimitation, for management units)
- phylogenetics/tree-io - Tree input/output for tree-based delimitation methods
- phylogenetics/modern-tree-inference - ML and Bayesian tree construction for delimitation input
- database-access/entrez-fetch - Retrieve barcode sequences from GenBank for reference comparison
<!-- END FILE: ecological-genomics/species-delimitation/SKILL.md -->

<!-- END CATEGORY: ecological-genomics -->

