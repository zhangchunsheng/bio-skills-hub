---
slug: bio-population-genetics-integrated
version: 1.0.0
displayName: "群体遗传学 / Population genetics analysis"
name: bio-population-genetics-integrated
summary: >-
  中文：群体遗传学综合技能，整合 7 个相关专题，覆盖群体遗传学分析：PLINK QC、LD分析、PCA/ADMIXTURE、GWAS、罕见变异关联、选择信号扫描。 English: Integrated Population genetics analysis skill covering 7 related topics, including Population genetics analysis: PLINK QC, LD analysis, PCA/ADMIXTURE, GWAS, rare variant association, selection scans.
description: >-
  中文：这是一个面向群体遗传学的综合生物信息学 Skill，整合当前分类下 7 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：群体遗传学分析：PLINK QC、LD分析、PCA/ADMIXTURE、GWAS、罕见变异关联、选择信号扫描。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：plink, plink2, regenie。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Population genetics analysis, combining 7 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Population genetics analysis: PLINK QC, LD analysis, PCA/ADMIXTURE, GWAS, rare variant association, selection scans. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: plink, plink2, regenie. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# population-genetics 分类 Skill 整合版

> 本文件整合同一主分类目录下 7 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: population-genetics -->

## 子目录：population-genetics/association-testing

<!-- BEGIN FILE: population-genetics/association-testing/SKILL.md -->
---
name: bio-population-genetics-association-testing
description: Single-variant common-variant GWAS with plink2 --glm (linear/logistic, Firth) and the linear mixed models GEMMA, BOLT-LMM, SAIGE, regenie (SPA). A GWAS statistic is valid only when genotype is independent of unmodeled phenotype drivers after the chosen covariates and random effects, so the engine follows sample structure and case:control imbalance, not taste: PC covariates absorb continuous ancestry but cannot remove relatedness (a covariance structure needing an LMM), genomic inflation above 1 is mostly true polygenic signal not confounding (the LDSC intercept is the diagnostic), LOCO prevents proximal contamination, and SPA/Firth keep the tail calibrated at extreme imbalance and low MAC. Use when running single-variant GWAS, choosing between a GLM and a mixed model, or controlling stratification, relatedness, and case:control imbalance. For rare-variant aggregation (burden, SKAT, SKAT-O, ACAT) see rare-variant-association; fine-mapping and MR see causal-genomics; PRS see clinical-databases/polygenic-risk.
tool_type: cli
primary_tool: plink2
---

## Version Compatibility

Reference examples tested with: PLINK 2.0 (alpha 6+), SAIGE 1.3+, regenie 3.4+, BOLT-LMM 2.4+, GEMMA 0.98+, numpy 1.26+, pandas 2.2+, scipy 1.12+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Version traps that change results, not just syntax: PLINK 2.0 `--glm firth-fallback` is the DEFAULT for binary traits and writes `.glm.logistic.hybrid` (mixed logistic and Firth rows), not `.glm.logistic`. SAIGE `--LOCO=TRUE` is the recommended default and the step-1 and step-2 sample IDs plus variance-ratio file must match exactly. regenie applies Firth/SPA only when `--firth`/`--spa` are explicitly set in step 2 (not automatic for every variant). BOLT-LMM is calibrated only for quantitative traits at large N (case fraction >= 10%, MAF > 0.1% for binary coding). The single source of truth for versions is this block, not headings.

# Association Testing

**"Run a GWAS on my genotypes"** -> Fit one regression per variant (additive dosage as predictor) under a confounder model chosen to make genotype independent of unmodeled phenotype drivers, then read effect sizes and p-values that are honest only insofar as that model holds.
- CLI: `plink2 --glm firth-fallback hide-covar --covar pcs.eigenvec` for an unrelated sample whose structure is captured by PCs
- CLI: `SAIGE` (SPA) or `regenie --step 1/2 --firth` for relatedness and/or case:control imbalance; `GEMMA -lmm` or `BOLT-LMM --lmm` for related quantitative traits

Scope: single-variant common-variant GWAS (linear/logistic GLM, linear mixed models, SPA, Firth) and the choice between them. Rare-variant GENE-BASED AGGREGATION (burden, SKAT, SKAT-O, ACAT, STAAR) routes to rare-variant-association. Fine-mapping, Mendelian randomization, and TWAS route to causal-genomics/fine-mapping and causal-genomics/mendelian-randomization. Polygenic risk scores route to clinical-databases/polygenic-risk. Imputed dosages enter from phasing-imputation/genotype-imputation.

## The Single Most Important Insight -- a GWAS statistic is valid only if genotype is independent of unmodeled phenotype drivers AFTER the chosen covariates and random effects

1. Every classic GWAS pathology is one violation of that assumption with a specific signature: structure or cryptic relatedness lifts the whole QQ plot; a heritable covariate adjusted as a collider manufactures direction-flipped hits; case:control imbalance with low MAC under a score test makes the significant tail anti-conservative.
2. The corollary that organizes the toolchain: under a real polygenic trait genomic inflation (lambda) is EXPECTED to exceed 1 and is mostly true signal, so genomic control over-corrects and erases discoveries; the LDSC intercept (not lambda) separates confounding from polygenicity (Bulik-Sullivan 2015).
3. The fix differs per distortion, and the wrong fix makes it worse: lambda-correcting a polygenic trait, or adding PCs to a family sample, both silently degrade the result.
4. Choosing the engine is choosing the assumption: a PC-adjusted GLM assumes structure is a low-rank mean shift, an LMM assumes a polygenic covariance, SPA/Firth assume the score/Wald tail needs the cumulant-generating-function correction.

## Tool Taxonomy

| Method | Citation | Mechanism | When |
|--------|----------|-----------|------|
| plink2 `--glm` | Chang 2015 | Per-variant linear/logistic GLM; Firth fallback for separation | Unrelated sample, common variants, structure captured by PCs |
| GEMMA `-lmm` | Zhou & Stephens 2012 | Exact LMM; fits sigma_g^2 once under the null, then per-variant Wald/LRT/score | Relatedness/structure, quantitative trait, small-medium N |
| BOLT-LMM `--lmm` | Loh 2015 | Variational LMM with a non-infinitesimal Bayesian mixture prior; LD-Score calibrated | Quantitative trait, very large N; gains power with large-effect loci |
| SAIGE | Zhou 2018 | Sparse-GRM LMM + saddlepoint approximation (SPA) on the score statistic | Binary trait with relatedness AND case:control imbalance |
| regenie `--step 1/2` | Mbatchou 2021 | Whole-genome ridge (LOCO) predictor in step 1, Firth/SPA test in step 2, no GRM eigendecomposition | Biobank scale, mixed binary+quantitative; one pipeline |

## Decision Tree by Scenario

| Scenario | Use | Why |
|----------|-----|-----|
| Unrelated, common variants, PCs absorb structure (LDSC intercept ~ 1) | plink2 `--glm` + PC covariates | Fast and exact; an LMM is unnecessary when PCs suffice |
| Relatedness, family, or fine-scale structure | any LMM (GEMMA/BOLT/SAIGE/regenie) | PCs cannot remove a covariance structure; the GRM random effect can |
| Quantitative trait, related, small-medium N | GEMMA `-lmm` or GCTA `--mlma-loco` | Exact LMM; LOCO avoids proximal contamination |
| Quantitative trait, biobank N (>5000) | BOLT-LMM `--lmm` | Scales; non-infinitesimal model adds power; calibrated only at large N |
| Binary trait, related AND imbalanced case:control | SAIGE (SPA) or regenie (`--firth`/`--spa`) | SPA/Firth keep the tail calibrated under imbalance and low MAC |
| Binary trait, unbalanced, NO relatedness | plink2 `--glm firth-fallback` (default) | Firth handles separation; no GRM needed |
| Imputed variants | regress on DOSAGES not hard calls | hard-calling discards imputation uncertainty and biases the SE |
| Rare-variant signal at low MAC | rare-variant-association (burden/SKAT/SKAT-O/ACAT) | single-variant tests are powerless at low MAC; aggregate in a region/gene |

## plink2 GLM (unrelated sample, PC-adjusted)

```bash
# Logistic for binary, linear for quantitative is auto-detected from the phenotype coding.
# firth-fallback is the binary-trait default: ordinary logistic, falling back to Firth only on
# non-convergence (separation). Output is .glm.logistic.hybrid (mixed logistic and Firth rows).
plink2 --bfile qc --pheno pheno.txt --glm firth-fallback hide-covar \
    --covar pcs.eigenvec --covar-name PC1-PC10 --out gwas

# Regress on imputed DOSAGES, not hard calls, so imputation uncertainty enters the SE. Reporting
# columns add A1 frequency and the imputation R2 (machr2 is meaningful only on dosage input) for
# downstream QC and effect-allele bookkeeping.
plink2 --pfile imputed --pheno pheno.txt --glm firth-fallback hide-covar cols=+a1freq,+machr2 \
    --covar covars.txt --covar-name PC1-PC10,age,sex --out gwas_dosage
```

PCs must be computed on LD-pruned, MAF-filtered genotypes with long-range-LD regions excluded (see population-structure); too few PCs leave residual stratification, too many absorb real signal. `--glm sex` adds sex as a covariate on chrX (`no-x-sex` suppresses it); split the pseudoautosomal region before any chrX test (see plink-basics).

## Linear mixed model with LOCO (relatedness / structure)

```bash
# GEMMA: -gk builds the GRM (1=centered, 2=standardized), then -lmm fits one variance component.
# The covariate file passed to -c MUST contain an explicit intercept column of 1s (GEMMA does not add one).
gemma -bfile qc -gk 1 -o grm
gemma -bfile qc -k output/grm.cXX.txt -c covars_with_intercept.txt -lmm 4 -o lmm   # -lmm 4 = Wald+LRT+score

# BOLT-LMM: --lmm decides by cross-validation whether the non-infinitesimal model adds power.
# --lmmInfOnly forces the standard infinitesimal model; --lmmForceNonInf forces the mixture.
bolt --bfile=qc --phenoFile=pheno.txt --phenoCol=trait \
    --covarFile=covars.txt --qCovarCol=PC{1:10} --lmm --LDscoresFile=LDSCORE.1000G_EUR.tab.gz \
    --statsFile=bolt.stats

# SAIGE: step 1 fits the null GLMM (sparse GRM, variance ratio); step 2 runs the SPA score test per variant.
# --LOCO=TRUE (default, recommended) excludes the tested chromosome from the polygenic predictor.
step1_fitNULLGLMM.R --plinkFile=qc --phenoFile=pheno.txt --phenoCol=trait --traitType=binary \
    --covarColList=PC1,PC2,age,sex --sampleIDColinphenoFile=IID --outputPrefix=step1 --LOCO=TRUE
step2_SPAtests.R --vcfFile=chr1.vcf.gz --GMMATmodelFile=step1.rda --varianceRatioFile=step1.varianceRatio.txt \
    --minMAC=20 --is_Firth_beta=TRUE --LOCO=TRUE --SAIGEOutputFile=chr1.saige

# regenie: step 1 builds the whole-genome LOCO ridge predictor; step 2 tests with Firth (--approx for speed) or SPA.
regenie --step 1 --bed qc --phenoFile pheno.txt --covarFile covars.txt --bt --bsize 1000 --out step1
regenie --step 2 --bed qc --phenoFile pheno.txt --covarFile covars.txt --bt \
    --firth --approx --pThresh 0.01 --pred step1_pred.list --bsize 400 --out step2
```

LOCO (leave-one-chromosome-out) is not optional: if the tested variant's chromosome is in the GRM/predictor, the random effect explains part of the variant's own signal and deflates power (proximal contamination). A hand-rolled "GRM from all SNPs" silently throws away power at every true locus.

## Diagnose inflation: lambda vs the LDSC intercept

```python
import numpy as np
from scipy import stats

def lambda_gc(pvalues):
    chisq = stats.chi2.ppf(1 - pvalues, 1)
    return np.median(chisq) / stats.chi2.ppf(0.5, 1)

# lambda > 1 under a polygenic trait is EXPECTED and mostly true signal. Do NOT divide statistics by it.
# Rescale to lambda_1000 (per 1000 cases/1000 controls) before comparing studies of different N.
def lambda_1000(lam, n_cases, n_controls):
    return 1 + (lam - 1) * (1 / n_cases + 1 / n_controls) / (1 / 1000 + 1 / 1000)

# The confounding diagnostic is the LDSC INTERCEPT (run ldsc on the sumstats), not lambda:
# intercept ~ 1 with high lambda = polygenicity (clean); intercept materially > 1 = confounding.
# Prefer the attenuation ratio = (intercept - 1) / (mean(chi2) - 1): the fraction of inflation NOT due
# to polygenicity (~0-0.2 acceptable). The intercept is also inflated by sample overlap in bivariate LDSC.
```

## Per-Method Failure Modes

### Genomic control on a polygenic trait
**Trigger:** dividing every chi-square by lambda_GC because lambda > 1.1. **Mechanism:** lambda rises with N and h2 under true polygenicity, so it is mostly signal. **Symptom:** discoveries vanish; power destroyed. **Fix:** never lambda-correct on lambda alone; use the LDSC intercept and only deflate if intercept-minus-1 is materially > 0.

### PCs for a related sample
**Trigger:** adding "10 PCs" to a family or cryptically-related cohort. **Mechanism:** relatedness is a pairwise covariance, not a low-rank mean shift, so no finite PC set removes it. **Symptom:** inflated, miscalibrated tail statistics despite the PCs. **Fix:** switch to an LMM (GEMMA/BOLT/SAIGE/regenie); more PCs is the wrong lever.

### LMM without LOCO
**Trigger:** building the GRM from all chromosomes including the candidate. **Mechanism:** the variant partly explains itself as a random effect. **Symptom:** deflated statistics, lost power at true loci. **Fix:** use the LOCO variant (`--mlma-loco`, SAIGE `--LOCO=TRUE`, regenie step-1 predictor).

### Wald collapse / score anti-conservatism at imbalance
**Trigger:** plain logistic for a rare or near-monomorphic-in-one-arm variant, or a score test at extreme case:control. **Mechanism:** the MLE diverges (Wald BETA/SE -> 0) or the score null is wrong in the tail. **Symptom:** real rare-variant signal looks non-significant, or the significant tail fills with artifacts. **Fix:** Firth (plink2 firth-fallback, regenie `--firth`) or SPA (SAIGE, regenie `--spa`).

### HWE filtered in cases
**Trigger:** HWE filter on the case-only or combined sample as a discovery QC step. **Mechanism:** a true non-additive disease variant legitimately deviates from HWE in cases. **Symptom:** real associations removed before testing. **Fix:** compute HWE in CONTROLS (or founders) only (see plink-basics).

### Adjusting for a heritable covariate (collider)
**Trigger:** GWAS of a trait while adjusting for a genetically influenced covariate (BMI, smoking). **Mechanism:** opens a non-causal genotype-phenotype path. **Symptom:** spurious, often direction-flipped hits at loci affecting the covariate that replicate within the conditioned design. **Fix:** only adjust for covariates not affected by genotype, or interpret as a different (interventional) question (Aschard 2015).

### BOLT-LMM on a binary trait
**Trigger:** treating BOLT as a logistic engine. **Mechanism:** it runs linear regression on case/control coding. **Symptom:** miscalibration and rare-variant false positives under imbalance. **Fix:** use it only for quantitative traits at case fraction >= 10%, MAF > 0.1%, large N; otherwise SAIGE/regenie.

## Quantitative Thresholds

| Quantity | Typical value | Rationale |
|----------|---------------|-----------|
| Genome-wide significance | p < 5e-8 | Bonferroni over ~1e6 independent common-variant tests in European HapMap LD (Pe'er 2008); ancestry/array-dependent |
| ...for African ancestry | ~1e-8 to 3e-8 | less LD = more independent tests; 5e-8 is too lax |
| ...for WGS / rare-variant scans | ~5e-9 or stricter | far larger effective test count; 5e-8 too permissive |
| Suggestive | p < 1e-5 | follow-up convention, not a calibrated threshold |
| lambda_GC | ~1.0-1.05 fine; 1.05-1.10 inspect; >1.10 investigate | scales with N and h2; pair with lambda_1000 and the LDSC intercept |
| MAC floor (single-variant) | MAC >= 20 (>= 10 with SPA/Firth) | below this even SPA/Firth are unstable; aggregate instead |
| SPA/Firth trigger | case:control more extreme than ~1:10, or low MAC | the score/Wald tail breaks exactly there (SAIGE motivated by ~1:600, Zhou 2018) |
| HWE filter (controls only) | p < 1e-6 | catches genotyping artifacts; never case-only as a discovery filter |

Thresholds are conventions, not laws; inspect distributions and verify current best practice before applying numbers blindly.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `.glm.logistic.hybrid` expected `.glm.logistic` | firth-fallback is the binary default and mixes Firth rows | read the `.hybrid` file; the `FIRTH?` column flags Firth rows |
| 0/1 phenotype gives a null GWAS | PLINK reads 1=control, 2=case by default | pass `--1` for 0/1 coding (see plink-basics) |
| Inflated tail despite 10 PCs | relatedness in the sample | switch to an LMM; PCs cannot remove relatedness |
| Lost power at top loci in an LMM | GRM includes the candidate chromosome | enable LOCO |
| Rare-variant hits look non-significant | Wald collapse under separation | use Firth or SPA |
| Flipped BETA cancels in meta-analysis | effect-allele/strand not harmonized | carry CHR, POS, EA, OA, EAF; resolve A/T and C/G palindromes by frequency or drop |
| Discovery effect size too large downstream | winner's curse | use out-of-sample or shrinkage-corrected effects for PRS/power/MR |
| chrX mis-coded | males hemizygous, PAR diploid | `--glm sex`, split PAR first, handle X-inactivation coding explicitly |
| GEMMA model wrong, no error | `-c` does not add an intercept | the covariate file must contain a column of 1s |
| Fixed-effect pooled OR with I^2 = 80% | heterogeneous true effects | check Cochran's Q / I^2; use random-effects or MR-MEGA for trans-ancestry |

## References

1. Devlin B, Roeder K. Genomic control for association studies. Biometrics 1999; 55(4):997-1004. DOI:10.1111/j.0006-341X.1999.00997.x.
2. Purcell S, Neale B, Todd-Brown K, et al. PLINK: a tool set for whole-genome association and population-based linkage analyses. American Journal of Human Genetics 2007; 81(3):559-575. DOI:10.1086/519795.
3. Pe'er I, Yelensky R, Altshuler D, Daly MJ. Estimation of the multiple testing burden for genomewide association studies of nearly all common variants. Genetic Epidemiology 2008; 32(4):381-385. DOI:10.1002/gepi.20303.
4. Zhou X, Stephens M. Genome-wide efficient mixed-model analysis for association studies. Nature Genetics 2012; 44(7):821-824. DOI:10.1038/ng.2310.
5. Yang J, Lee SH, Goddard ME, Visscher PM. GCTA: a tool for genome-wide complex trait analysis. American Journal of Human Genetics 2011; 88(1):76-82. DOI:10.1016/j.ajhg.2010.11.011.
6. Aschard H, Vilhjalmsson BJ, Joshi AD, Price AL, Kraft P. Adjusting for heritable covariates can bias effect estimates in genome-wide association studies. American Journal of Human Genetics 2015; 96(2):329-339. DOI:10.1016/j.ajhg.2014.12.021.
7. Chang CC, Chow CC, Tellier LCAM, Vattikuti S, Purcell SM, Lee JJ. Second-generation PLINK: rising to the challenge of larger and richer datasets. GigaScience 2015; 4:7. DOI:10.1186/s13742-015-0047-8.
8. Loh PR, Tucker G, Bulik-Sullivan BK, et al. Efficient Bayesian mixed-model analysis increases association power in large cohorts. Nature Genetics 2015; 47(3):284-290. DOI:10.1038/ng.3190.
9. Bulik-Sullivan BK, Loh PR, Finucane HK, et al. LD Score regression distinguishes confounding from polygenicity in genome-wide association studies. Nature Genetics 2015; 47(3):291-295. DOI:10.1038/ng.3211.
10. Zhou W, Nielsen JB, Fritsche LG, et al. Efficiently controlling for case-control imbalance and sample relatedness in large-scale genetic association studies. Nature Genetics 2018; 50(9):1335-1341. DOI:10.1038/s41588-018-0184-y.
11. Mbatchou J, Barnard L, Backman J, et al. Computationally efficient whole-genome regression for quantitative and binary traits. Nature Genetics 2021; 53(7):1097-1103. DOI:10.1038/s41588-021-00870-7.

## Related Skills

- plink-basics - QC, phenotype encoding, and the fileset that enters association
- population-structure - PCA covariates for stratification control
- linkage-disequilibrium - LD pruning before PCA and clumping of GWAS hits
- rare-variant-association - gene-based aggregation (burden, SKAT, SKAT-O, ACAT) below the single-variant MAC floor
- causal-genomics/fine-mapping - from an associated locus to a credible set of causal variants
- causal-genomics/mendelian-randomization - GWAS variants as instruments for causal inference
- clinical-databases/polygenic-risk - PRS built from association sumstats
- phasing-imputation/genotype-imputation - imputed dosages that enter --glm
<!-- END FILE: population-genetics/association-testing/SKILL.md -->

## 子目录：population-genetics/linkage-disequilibrium

<!-- BEGIN FILE: population-genetics/linkage-disequilibrium/SKILL.md -->
---
name: bio-population-genetics-linkage-disequilibrium
description: Computes linkage disequilibrium (r2, D', composite Rogers-Huff r2), prunes correlated variants, clumps GWAS summary statistics to lead SNPs, and defines haplotype blocks with PLINK 1.9/2.0 and scikit-allel. r2 and D' answer different questions - r2 (= chi2/N) is the tagging and GWAS-power currency, D' marks observed recombination and is upward-biased for rare variants. PLINK 2.0 has no bare --r2 (split into --r2-phased and --r2-unphased); pruning (--indep-pairwise, genotype-blind) and clumping (--clump, p-value-aware) are distinct operations that are constantly confused. The clumping or fine-mapping LD reference must be ancestry-matched or it fails silently into false credible sets. Use when calculating LD, pruning variants for PCA or structure, clumping GWAS hits, or selecting tag SNPs. For QC see plink-basics; for PCA see population-structure; fine-mapping is causal-genomics/fine-mapping.
tool_type: mixed
primary_tool: plink2
---

## Version Compatibility

Reference examples tested with: PLINK 1.9 (1.90b7+), PLINK 2.0 (alpha 6+), scikit-allel 1.3+, numpy 1.26+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Version traps that change results, not just syntax: PLINK 2.0 has NO bare `--r2` (it was split into `--r2-phased`, the EM haplotype-frequency estimator, and `--r2-unphased`, the composite dosage estimator); PLINK 1.9 still uses bare `--r2`. PLINK 2.0 `--indep-pairwise <window>['kb'] [step] <r2>` requires the step to be 1 when the window is given in kb. `allel.rogers_huff_r` returns a CONDENSED upper-triangle array, not a square matrix - `scipy.spatial.distance.squareform` it before 2D indexing. The single source of truth for versions is this block, not headings.

# Linkage Disequilibrium

**"Measure LD between my variants"** -> Quantify how predictably one variant's alleles co-occur with another's, choosing r2 or D' by the question being asked.
- CLI: `plink2 --r2-unphased` (composite dosage r2, no phasing) or `--r2-phased` (EM haplotype r2)
- Python: `allel.rogers_huff_r(gn) ** 2` (composite r2, scikit-allel)

**"Thin correlated variants before PCA or structure"** -> Remove variants so no remaining pair is in high LD, leaving a near-independent marker set.
- CLI: `plink2 --indep-pairwise 50 5 0.1` (genotype-blind, phenotype-agnostic)
- Python: `allel.locate_unlinked(gn, size=50, step=5, threshold=0.1)` (scikit-allel)

**"Reduce my GWAS hits to one signal per locus"** -> Group correlated associations around the most significant SNP per region.
- CLI: `plink --clump sumstats --clump-p1 5e-8 --clump-r2 0.1 --clump-kb 250`

Scope: LD measures, pruning, clumping, haplotype blocks, and LD decay. QC/conversion route to plink-basics; PCA/ADMIXTURE to population-structure; `--glm` GWAS to association-testing; resolving independent causal variants to causal-genomics/fine-mapping; phased haplotypes to phasing-imputation/haplotype-phasing.

## The Single Most Important Insight -- D' and r2 answer different questions

1. D' measures whether recombination has been observed between two loci (a historical/structural question); r2 measures how well one variant predicts the other (a statistical/predictive question), so they are not interchangeable.
2. r2 owns tagging, imputation, pruning, and GWAS power because r2 = chi2/N exactly (N = number of haplotypes = 2 x sampled individuals, for the 1-df allelic 2x2 table; the composite estimator targets this gametic r2 under random mating): a proxy multiplies the association test's non-centrality by r2, so 1/r2 times the sample size is needed to recover the lost power (Pritchard & Przeworski 2001).
3. D'=1 routinely coexists with r2 ~ 0.05 because allele-frequency asymmetry caps r2: r2/r2max = D'^2 over most of frequency space (VanLiere & Rosenberg 2008), which is exactly why a common array SNP cannot tag a rare causal variant despite "complete LD".
4. Every operation that consumes an LD matrix (clumping, fine-mapping, LD-score regression) silently assumes that matrix matches the study sample's LD; a wrong-ancestry or underpowered reference does not error, it produces confidently wrong output.

## Tool Taxonomy

| Method | Tool / call | Mechanism | When |
|--------|-------------|-----------|------|
| Composite (Rogers-Huff) r2 | `plink2 --r2-unphased`; `allel.rogers_huff_r` | correlation of 0/1/2 dosage vectors, no phasing | robust default when phase or HWE is doubtful |
| EM haplotype r2 | `plink2 --r2-phased`; `vcftools --hap-r2` | infers haplotype frequencies under HWE, then r2 | large HWE-consistent samples, or truly phased input |
| D' | `plink --r2 dprime`; `plink2 --ld <a> <b>` | D normalized by its frequency-constrained max | block boundaries, recombination history (NOT tagging) |
| LD pruning | `plink2 --indep-pairwise`; `allel.locate_unlinked` | genotype-blind windowed r2 thinning | independent marker set for PCA/ADMIXTURE/GRM |
| LD clumping | `plink --clump` | p-value-aware grouping around an index SNP | one lead SNP per associated GWAS locus |
| Haplotype blocks | `plink --blocks no-pheno-req` | Gabriel confidence-interval D' method | block maps, recombination inference |
| LD score regression | `ldsc` (`--l2`, `--h2`, `--rg`) | regress GWAS chi2 on LD score | h2, genetic correlation, confounding from sumstats |

## Decision Tree by Scenario

| Scenario | Use | Why |
|----------|-----|-----|
| Thin variants for PCA/ADMIXTURE/GRM | `--indep-pairwise` after excluding long-range-LD regions | phenotype-blind independence; MHC/inversions must go by coordinate first |
| Reduce GWAS hits to lead SNPs | `--clump` with ancestry-matched LD | p-value-aware; one index SNP per locus |
| Establish independent causal signals | conditional analysis or fine-mapping, NOT tighter clumping | clumping picks the top SNP, not the causal one; over-clumping deletes real secondaries |
| Assess a proxy/tag SNP | r2 (`--r2-unphased`), require r2 >= 0.8 | r2 = fraction of effective N retained at the proxy |
| Define haplotype blocks / recombination | D' (`--blocks`, `--r2 dprime`) | D' marks observed recombination; r2 does not |
| Phase or HWE doubtful, small N, missingness | composite r2 (`--r2-unphased`, Rogers-Huff) | EM can manufacture haplotype-frequency artifacts |
| LD from genotypes in Python at scale | `allel.locate_unlinked` / `allel.rogers_huff_r` | composite estimator, chunkable; no phased-EM in scikit-allel |
| h2 / confounding from summary stats | LD-score regression with ancestry-matched scores | slope = h2, intercept-1 = confounding |

## Pairwise LD and the Phased/Unphased Choice

**Goal:** Compute pairwise r2 (and D' when recombination is the question) without an EM artifact under structure or missingness.

**Approach:** Default to the composite dosage estimator that needs no phasing; reach for EM haplotype r2 only when the sample is large and HWE-consistent, and use D' solely for block/recombination work.

```bash
# Composite dosage r2 (Rogers-Huff): robust default, no HWE assumption.
plink2 --bfile data --r2-unphased --ld-window-kb 1000 --ld-window-r2 0.2 --out ld_unphased

# EM haplotype-frequency r2: only when phase is trustworthy / sample is large and HWE-consistent.
plink2 --bfile data --r2-phased --ld-window-kb 1000 --out ld_phased

# D' for a single pair (recombination / block question), with observed haplotype frequencies.
plink2 --bfile data --ld rs123 rs456 --out pair

# PLINK 1.9 still has the bare --r2; add dprime to also report D'.
plink --bfile data --r2 dprime --ld-window-kb 500 --out ld_dprime
```

```python
import allel
from scipy.spatial.distance import squareform

callset = allel.read_vcf('data.vcf.gz')
gn = allel.GenotypeArray(callset['calldata/GT']).to_n_alt()

# rogers_huff_r returns a CONDENSED upper-triangle vector; square it for r2, squareform for a matrix.
r2_matrix = squareform(allel.rogers_huff_r(gn[:200]) ** 2)
```

## LD Pruning for Structure (genotype-blind)

**Goal:** Produce a near-independent marker set so PCA/ADMIXTURE/GRM are not dominated by a handful of LD blocks.

**Approach:** Exclude long-range-LD regions by coordinate FIRST (their internal r2 is high and real, so a threshold cannot remove them sensibly), then slide an r2 window over the survivors.

```bash
# 1. Drop long-range-LD regions by position (MHC chr6:25-35 Mb, 8p23.1, 17q21.31, LCT/2q21; coordinates are build-specific).
plink2 --bfile data --exclude range longrange_ld.txt --make-bed --out data_noLR

# 2. Windowed r2 prune (50 here is a variant count, so step 5 is fine; step MUST be 1 only with a kb window).
plink2 --bfile data_noLR --indep-pairwise 50 5 0.1 --out prune     # 50-variant window, step 5, r2 0.1
plink2 --bfile data_noLR --extract prune.prune.in --make-bed --out data_pruned
```

```python
import allel

callset = allel.read_vcf('data.vcf.gz')
gn = allel.GenotypeArray(callset['calldata/GT']).to_n_alt()

loc_unlinked = allel.locate_unlinked(gn, size=50, step=5, threshold=0.1)  # boolean keep-mask
gn_pruned = gn.compress(loc_unlinked, axis=0)
```

## Clumping GWAS Summary Statistics (p-value-aware)

**Goal:** Collapse a region of correlated associations to one lead SNP per independent locus.

**Approach:** Index on genome-wide-significant SNPs and absorb nearby LD partners, overriding PLINK's permissive defaults; use an ancestry-matched LD reference, ideally the study sample itself.

```bash
# Defaults (p1=1e-4, p2=1e-2, r2=0.5, kb=250) are neither genome-wide nor strict - set them explicitly.
plink --bfile ld_reference \
    --clump gwas_sumstats.txt \
    --clump-p1 5e-8 --clump-p2 1e-5 --clump-r2 0.1 --clump-kb 250 \
    --out clumped
# clumped.clumped lists one index SNP per locus. This is NOT conditional analysis or fine-mapping.
```

## Haplotype Blocks and LD Decay

**Goal:** Map regions of little observed recombination, or characterize how LD decays with distance.

**Approach:** Use the Gabriel D'-CI block method for boundaries; for decay, bin composite r2 by physical distance after stratifying by population so admixture LD does not flatten the curve.

```bash
plink --bfile data --blocks no-pheno-req --out blocks   # blocks.blocks, blocks.blocks.det (Gabriel CI)
```

```python
import allel, numpy as np

callset = allel.read_vcf('data.vcf.gz')
gn = allel.GenotypeArray(callset['calldata/GT']).to_n_alt()
pos = callset['variants/POS']

n = min(1000, gn.shape[0])
r2, dist = [], []
for i in range(n):
    for j in range(i + 1, min(i + 100, n)):
        r2.append(allel.rogers_huff_r(gn[[i, j]])[0] ** 2)  # condensed length-1 -> index [0]
        dist.append(pos[j] - pos[i])
r2, dist = np.array(r2), np.array(dist)

edges = np.arange(0, 100001, 1000)
decay = [np.mean(r2[(dist >= edges[k]) & (dist < edges[k + 1])]) if ((dist >= edges[k]) & (dist < edges[k + 1])).any() else np.nan for k in range(len(edges) - 1)]
```

## Per-Method Failure Modes

### Long-range-LD regions survive pruning
**Trigger:** `--indep-pairwise` run without excluding MHC/inversions by coordinate. **Mechanism:** their internal r2 is high and genuine, so a window prune keeps a dense cluster. **Symptom:** the top PCs capture the MHC (chr6:25-35Mb) or 17q21.31 inversion, not ancestry. **Fix:** `--exclude range` the long-range-LD list (MHC, 8p23.1, 17q21.31, LCT; Price 2008) before pruning, not a tighter r2.

### D' read as "high LD" for tagging
**Trigger:** selecting tag SNPs or judging proxy adequacy from D'. **Mechanism:** D'=1 only says no recombinant was observed; frequency asymmetry caps r2 far below 1. **Symptom:** a "perfectly linked" common SNP retains almost no association power for a rare causal variant. **Fix:** use r2 for tagging/power and require r2 >= 0.8; reserve D' for blocks.

### D' inflated at rare alleles / small N
**Trigger:** interpreting D' or `--blocks` where minor-allele count is below ~10-20. **Mechanism:** the fourth haplotype is unobserved by chance, pushing the D' MLE to ~1 even for independent loci. **Symptom:** spurious "perfect LD" blocks that vanish with more samples. **Fix:** do not interpret D' at low MAC; report r2, which is noisy but not systematically inflated.

### EM haplotype r2 on structured/missing data
**Trigger:** `--r2-phased` or `--hap-r2` under inbreeding, structure, or high missingness. **Mechanism:** EM converges to biased haplotype frequencies that violate the HWE assumption. **Symptom:** r2 disagrees with the composite estimate and shifts with missingness. **Fix:** use `--r2-unphased` (composite Rogers-Huff) when phase or HWE is doubtful.

### Wrong-ancestry LD reference
**Trigger:** clumping, LD-score regression, or fine-mapping with a panel that does not match the GWAS ancestry. **Mechanism:** the LD matrix consumed differs from the sample's true LD; no error is raised. **Symptom:** mis-grouped clumps, biased heritability, false fine-mapping credible sets with "impossible" configurations. **Fix:** compute LD from the study sample itself, or use an ancestry-matched panel.

### Over-clumping merges independent signals
**Trigger:** treating `--clump` as conditional or fine-mapping analysis. **Mechanism:** clumping keeps the single most significant SNP and discards everything in LD with it. **Symptom:** two truly independent causal variants in modest LD collapse to one locus. **Fix:** use conditional analysis (COJO) or fine-mapping (causal-genomics/fine-mapping); do not just tighten `--clump-r2`.

### LD decay curve flattens at a spurious floor
**Trigger:** plotting LD decay on a pooled multi-population sample. **Mechanism:** admixture and background LD inflate long-range r2 independent of distance. **Symptom:** the decay curve plateaus at a nonzero asymptote instead of decaying toward zero. **Fix:** stratify by population before computing decay (LD ~ 1/(4*Ne*c+1), Hill & Robertson 1968).

## Quantitative Thresholds

| Operation | Flag / value | Typical | Rationale |
|-----------|--------------|---------|-----------|
| Pruning for PCA/ADMIXTURE/GRM | `--indep-pairwise` r2 | 0.1 (range 0.05-0.2) | near-independence so structure is not double-counted; strictness trades marker count for independence |
| Pruning window / step | window / step | 50 var / 5, or 200kb / 1 | window must exceed local LD extent; step is 1 for kb windows in plink2 |
| Pruning for polygenic scores | `--indep-pairwise` r2 | 0.1-0.5 within 250kb-1Mb | retain more signal; tuned by validation |
| Clumping LD threshold | `--clump-r2` | 0.1 (default 0.5 under-clumps) | r2 0.1 within 250kb defines one independent locus; set explicitly |
| Clumping p-values | `--clump-p1` / `--clump-p2` | 5e-8 / 1e-5 (defaults 1e-4/1e-2) | index at genome-wide significance; defaults are neither genome-wide nor strict |
| Tag / proxy adequacy | r2 | >= 0.8 | r2 = chi2/N: retains >= 80% of association power at the proxy (Pritchard & Przeworski 2001) |
| Gabriel "strong LD" block | upper 95% D' CI | > 0.98 (lower > 0.7) | one recombinant makes D'=1 impossible yet the CI can sit just below 1 (Gabriel 2002) |
| MAF floor for stable D' | MAF | >~ 0.05 | D' upward bias and r2 variance both blow up at low MAC |
| LDSC applicability | mean chi2 / N | > ~1.02 / N > ~5000 | below this the slope is too noisy; exclude MHC; munge to HapMap3 SNPs (Bulik-Sullivan 2015) |

Thresholds are conventions, not laws - inspect the LD distributions and verify current best practice before applying numbers blindly.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `plink2 --r2` "unrecognized flag" | bare `--r2` removed in PLINK 2.0 | choose `--r2-phased` or `--r2-unphased`; PLINK 1.9 keeps `--r2` |
| `--indep-pairwise 50kb 5 0.1` errors | step must be 1 for kb windows | use `--indep-pairwise 50kb 1 0.1` or a variant-count window |
| `rogers_huff_r(gn)[0,1]` index error | function returns a condensed vector | `squareform(rogers_huff_r(gn))` first, or index `[0]` for a single pair |
| Top PCs capture one region | long-range-LD region left in | `--exclude range` MHC/8p23.1/17q21.31/LCT by coordinate before pruning |
| Clumping reports correlated SNPs as separate loci | default `--clump-r2 0.5` too loose | set `--clump-r2 0.1` and `--clump-p1 5e-8` explicitly |
| Independent secondary hit disappears | over-clumping treated as fine-mapping | use conditional analysis / fine-mapping, not a tighter clump |
| False fine-mapping credible sets | wrong-ancestry LD reference | use in-sample or ancestry-matched LD |
| LDSC intercept read as pure stratification | intercept also absorbs sample overlap | use the attenuation ratio (intercept-1)/(mean chi2 - 1) |

## References

1. Lewontin RC. The interaction of selection and linkage. I. General considerations; heterotic models. Genetics 1964; 49(1):49-67.
2. Hill WG, Robertson A. Linkage disequilibrium in finite populations. Theoretical and Applied Genetics 1968; 38(6):226-231. DOI:10.1007/BF01245622.
3. Pritchard JK, Przeworski M. Linkage disequilibrium in humans: models and data. American Journal of Human Genetics 2001; 69(1):1-14. DOI:10.1086/321275.
4. Gabriel SB, Schaffner SF, Nguyen H, et al. The structure of haplotype blocks in the human genome. Science 2002; 296(5576):2225-2229. DOI:10.1126/science.1069424.
5. Price AL, Weale ME, Patterson N, et al. Long-range LD can confound genome scans in admixed populations. American Journal of Human Genetics 2008; 83(1):132-135. DOI:10.1016/j.ajhg.2008.06.005.
6. VanLiere JM, Rosenberg NA. Mathematical properties of the r2 measure of linkage disequilibrium. Theoretical Population Biology 2008; 74(1):130-137. DOI:10.1016/j.tpb.2008.05.006.
7. Rogers AR, Huff C. Linkage disequilibrium between loci with unknown phase. Genetics 2009; 182(3):839-844. DOI:10.1534/genetics.108.093153.
8. Bulik-Sullivan BK, Loh P-R, Finucane HK, et al. LD Score regression distinguishes confounding from polygenicity in genome-wide association studies. Nature Genetics 2015; 47(3):291-295. DOI:10.1038/ng.3211.

## Related Skills

- plink-basics - format conversion and QC before any LD operation
- population-structure - PCA and ADMIXTURE on the LD-pruned marker set
- association-testing - GWAS whose summary statistics feed clumping
- selection-statistics - haplotype statistics that depend on LD structure
- causal-genomics/fine-mapping - resolving independent causal variants beyond clumping
- phasing-imputation/haplotype-phasing - phased haplotypes for EM/haplotype-based r2
<!-- END FILE: population-genetics/linkage-disequilibrium/SKILL.md -->

## 子目录：population-genetics/plink-basics

<!-- BEGIN FILE: population-genetics/plink-basics/SKILL.md -->
---
name: bio-population-genetics-plink-basics
description: Manages PLINK genotype filesets - format conversion (VCF, BED/BIM/FAM, PED/MAP, pgen/pvar/psam) and sample/variant QC (missingness, MAF, HWE, sex check, heterozygosity, KING relatedness) with PLINK 1.9 and 2.0. PLINK rewrites allele bookkeeping: PLINK 1.x A1 defaults to the minor allele and is recomputed every load, silently flipping effect-allele meaning unless --keep-allele-order, while PLINK 2.0 tracks explicit REF/ALT. QC order matters (variant before sample missingness), HWE is controls-only in 1.9 but not 2.0, add midp, and differential case/control missingness injects false hits. Use when converting between PLINK formats or running genotype QC before association, structure, or LD analysis. For LD pruning/clumping see linkage-disequilibrium; for GWAS see association-testing; VCF input from variant-calling/vcf-basics.
tool_type: cli
primary_tool: plink
---

## Version Compatibility

Reference examples tested with: PLINK 1.9 (1.90b7+), PLINK 2.0 (alpha 6+), pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Version traps that change results, not just syntax: PLINK 2.0 `--freq` reports ALT/nonmajor allele frequency, PLINK 1.9 `--freq` reports MAF. PLINK 2.0 has no `--recode` (use `--export`) and cannot read `.ped/.map` (convert with 1.9 first). PLINK 2.0 `--hwe` is NOT controls-only by default; PLINK 1.9 is. Missing-rate outputs are `.smiss/.vmiss` (2.0) vs `.imiss/.lmiss` (1.9). PLINK 2.0 dropped `--genome`; use `--make-king` for relatedness. The single source of truth for versions is this block, not headings.

# PLINK Basics

**"Convert my VCF to PLINK and run QC"** -> Project a VCF into a PLINK fileset and apply sample/variant quality filters, holding the allele coding and filter order fixed so downstream effect estimates stay meaningful.
- CLI: `plink2 --vcf in.vcf.gz --make-pgen` (keeps REF/ALT and dosage) or `--make-bed` (biallelic hard calls, A1/A2)
- CLI: `plink2 --geno 0.02` then `plink2 --mind 0.02 --maf 0.01 --hwe 1e-6 midp` (ordered QC)

Scope: PLINK file formats, conversion, and sample/variant QC (missingness, MAF, HWE, sex check, heterozygosity, KING relatedness, merging). LD pruning/clumping (`--indep-pairwise`, `--clump`) route to linkage-disequilibrium; PCA/ADMIXTURE to population-structure; `--glm` GWAS to association-testing; VCF generation to variant-calling/vcf-basics.

## The Single Most Important Insight -- PLINK is a stateful rewriter of allele bookkeeping, not a calculator

1. The most expensive error in the field is trusting that the allele an effect estimate is "for" is the allele assumed. PLINK 1.x has no reference allele: it tracks A1 (the counted/effect allele) and A2, and **A1 defaults to the minor allele, recomputed from the data at load time**. The same SNP flips A1 between two cohorts when the minor allele differs by a few percent, and every `--make-bed` re-derives A2 as the major allele unless `--keep-allele-order` is passed. Betas, odds ratios, and PRS weights are all relative to A1 and become meaningless across cohorts that were not harmonized.
2. PLINK 2.0 fixed the **design** by tracking explicit REF/ALT in `.pvar` (REF is the genuine reference base; the counted allele for `--glm` is set independently), but exporting back to `.bed` collapses into the A1/A2 world and re-inherits the trap.
3. Pinning alleles to a fixed reference (`--ref-allele`/`--a1-allele` from a file, `--ref-from-fa`, or staying in `.pgen`) plus `--keep-allele-order` on any `.bed` export is the line between reproducible and quietly-wrong analysis.
4. Two QC choices silently corrupt association before any test is run: filter **order** (sample-vs-variant missingness) and the **case/control missingness confounder**. Both are covered below.

## Tool Taxonomy -- PLINK 1.9 vs PLINK 2.0

| Axis | PLINK 1.9 (`plink`) | PLINK 2.0 (`plink2`) |
|------|---------------------|----------------------|
| Status / model | Stable, feature-frozen; hard calls only; A1/A2 | Active; hard calls and dosages; explicit REF/ALT, multiallelic-aware |
| Native format | `.bed/.bim/.fam` | `.pgen/.pvar/.psam` |
| Allele bookkeeping | A1 = minor by default (the trap) | REF/ALT tracked; counted allele explicit |
| PED/MAP (`--file`) | Yes | No (convert via 1.9) |
| IBD `--genome` / `--cluster` | Yes | No (use 1.9 or KING) |
| KING-robust relatedness | No | `--make-king`, `--king-cutoff` |
| Multi-fileset merge | `--bmerge` / `--merge-list` (battle-tested) | `--pmerge` / `--pmerge-list` (newer) |
| HWE default | controls-only | NOT controls-only |
| `--freq` default | MAF | ALT/nonmajor frequency |
| Missing-rate output | `.imiss` / `.lmiss` | `.smiss` / `.vmiss` |
| Speed/memory at biobank N | baseline | substantially faster, lower memory |

## Decision Tree by Scenario

| Scenario | Use | Why |
|----------|-----|-----|
| Imputed data with dosage uncertainty | plink2 `.pgen` | 1.9 hard-calls and discards dosage |
| Relatedness in a structured/multi-ancestry sample | plink2 `--make-king` | PI_HAT (`--genome`) is biased under structure; KING gives negative kinship for cross-ancestry unrelateds |
| Classic multi-dataset merge | plink1.9 `--bmerge`/`--merge-list` | most documented and predictable path |
| IBD `--genome` / IBS `--cluster` | plink1.9 | plink2 dropped these |
| Reading PED/MAP or Affymetrix-era text | plink1.9 `--file` | plink2 cannot read them |
| Big modern QC/association/PCA inputs | plink2, export `.bed` last | speed plus correct allele handling; minimize time in A1/A2 land |
| Default working format | stay in `.pgen` through QC | keeps REF/ALT honest; export `.bed` only when a tool demands it (then `--keep-allele-order`) |

## File Formats

| Binary (1.9) | Contents | PLINK 2.0 | Contents |
|------|----------|-----------|----------|
| `.bed` | binary hard-call genotypes (biallelic only) | `.pgen` | genotypes + dosages, multiallelic-aware |
| `.bim` | variant info (chr, ID, cM, pos, **A1, A2**) | `.pvar` | variant info with genuine **REF/ALT** |
| `.fam` | sample info (FID, IID, father, mother, sex, pheno) | `.psam` | sample info |

Text `.ped/.map` (PLINK 1.9 `--file`) is legacy; convert to binary once and work from there.

## Format Conversion

```bash
# VCF -> PLINK. --make-pgen preserves REF/ALT and dosage; --make-bed collapses to A1/A2 hard calls.
plink2 --vcf in.vcf.gz --make-pgen --out data            # preferred working format
plink2 --vcf in.vcf.gz --double-id --make-bed --out data # biallelic hard calls; --double-id copies the VCF sample name into both FID and IID

# Keep the reference allele honest when leaving pgen for bed (otherwise A2 is re-set to major):
plink2 --pfile data --ref-from-fa --fa GRCh38.fa --make-bed --keep-allele-order --out data_bed

# PLINK -> VCF. plink2 uses --export (no --recode); add bgz to compress.
plink2 --bfile data --export vcf bgz --out out
plink  --bfile data --recode vcf --out out               # PLINK 1.9 idiom

# PED/MAP must be read by PLINK 1.9; plink2 cannot.
plink --file textdata --make-bed --out data
```

Multiallelic sites cannot live in `.bed` (biallelic by construction). Split first with `bcftools norm -m-` or accept plink2's split, and track which records changed. Strand-flip logic cannot operate on indels; `--snps-only just-acgt` removes them when needed.

## Quality Control Filtering

```bash
# Variant missingness FIRST, in its own run, so a sample is not dropped for missingness driven by variants slated for removal.
plink2 --pfile data --geno 0.02 --make-pgen --out step1     # default --geno is 0.1; GWAS QC tightens to 0.02-0.05

# THEN sample missingness, MAF, and HWE on the surviving variants.
plink2 --pfile step1 --mind 0.02 --maf 0.01 --hwe 1e-6 midp --make-pgen --out step2
```

HWE caveats that change which variants survive:
- `midp` is not optional. The plain exact test is discrete and conservative for low-count genotypes, biasing toward retaining variants with missing data; mid-p brings rejection to nominal (Graffelman 2013).
- **Apply HWE to controls only.** A true risk variant depletes heterozygotes in cases and would fail a case-inclusive HWE test and be wrongly removed. PLINK 1.9 does this automatically; override with the `include-nonctrl` modifier. **plink2 does NOT** - replicate the behavior with `--keep-if "PHENO1 == control"` before `--hwe`, or the rewrite over-filters real associations.
- In a structured sample the Wahlund effect reduces heterozygosity, so a two-sided HWE filter drops real variants; many genotyping artifacts (contamination, paralog mismapping) instead inflate heterozygosity, so under structure a one-sided excess-het filter (plink2 `keep-fewhet`) avoids dropping Wahlund-deficient real variants.

```bash
# Differential missingness: a top source of false GWAS hits. A variant genotyped less well in cases than controls
# correlates missingness with phenotype; a flat --geno keeps it and injects association.
plink2 --bfile data --pheno pheno.txt --test-missing --out diffmiss   # drop variants with case/control missingness skew
```

## Sample QC

```bash
# Sex check. Split the pseudoautosomal region FIRST or male PAR heterozygosity reads as a sex error.
plink2 --bfile data --split-par hg38 --check-sex --out sexcheck   # PLINK 1.9 uses --split-x hg38
# Default calls: F < 0.2 -> female, F > 0.8 -> male, between -> PROBLEM. These ~2007 defaults are often wrong
# for modern arrays; plot the F histogram and re-pick thresholds at the gap between the two clumps.

# Heterozygosity outliers, on LD-pruned MAF-filtered SNPs only (raw data is dominated by a few regions).
plink2 --bfile data_pruned --het --out het   # flag |F - cohort_mean| > 3 SD: excess het = contamination, deficit = inbreeding/dup

# Relatedness. KING-robust is structure-robust; PI_HAT (--genome) is not.
plink2 --bfile data --make-king-table --out king
plink2 --bfile data --king-cutoff 0.0884 --out unrelated   # prune to no-closer-than 2nd-degree (dup 0.354, 1st 0.177, 2nd 0.0884)
```

`--check-sex` and heterozygosity outliers usually signal a sample swap or contamination, not biology - investigate the sample before dropping it. KING uses autosomes only; the same negative bias that makes cross-ancestry unrelated pairs read below zero also pulls true cross-ancestry relatives toward zero, so KING UNDER-detects relatives in admixed or multi-ancestry cohorts (use PC-Relate / PC-AiR there, out of scope here).

## Merging Datasets

```bash
plink --bfile data1 --bmerge data2 --make-bed --out merged
# Aborts with a "3+ alleles" error when the same SNP is on opposite strands (A/G vs T/C). Flip the offenders, then retry:
plink --bfile data2 --flip merged-merge.missnp --make-bed --out data2_flipped
```

`--flip` swaps A<->T and C<->G only and **cannot disambiguate palindromic A/T and C/G SNPs** (identical on both strands) - resolve those by allele frequency or drop them. Harmonize variant IDs to `chr:pos:ref:alt` (`--set-all-var-ids @:#:\$r:\$a`) before merging so the key is positional and allele-aware, not rsID-collision-prone. Build mismatch (hg19 vs hg38) requires liftover first, which can itself flip strand in inverted regions.

## Per-Operation Failure Modes

### A1/A2 effect-allele flip
**Trigger:** `--make-bed` without `--keep-allele-order`, or merging two cohorts. **Mechanism:** A1 is re-derived as the minor allele from whatever data is present. **Symptom:** betas/ORs/PRS weights point at the wrong allele; meta-analysis cancels true signal. **Fix:** `--keep-allele-order` on every `.bed` export and pin alleles from a fixed reference (`--ref-from-fa` / `--a1-allele`).

### Wrong QC order
**Trigger:** `--geno` and `--mind` in one command. **Mechanism:** plink applies `--mind` (sample) before `--geno` (variant) in a single run; published QC wants variants dropped first. **Symptom:** good samples removed for missingness caused by variants that were about to be filtered. **Fix:** run `--geno` and `--mind` in separate invocations, variant filter first.

### Differential missingness
**Trigger:** case/control cohorts genotyped in separate batches. **Mechanism:** missingness correlates with phenotype; a flat `--geno` retains the variant. **Symptom:** false genome-wide hits at batch-skewed sites. **Fix:** `--test-missing` and drop variants with case/control missingness skew, not just a global `--geno`.

### Phenotype encoding inversion
**Trigger:** loading a 0/1 case/control file without `--1`. **Mechanism:** PLINK reads `1`=control, `2`=case, `0`/`-9`=missing by default; a 0/1 file makes every case read as control and every control as missing. **Symptom:** silent, total phenotype corruption; null or inverted GWAS. **Fix:** `--1` for 0/1 coding; any value outside {-9,0,1,2} is treated as quantitative.

### PAR not split before sex/X analysis
**Trigger:** `--check-sex` or X-specific work without `--split-par`/`--split-x`. **Mechanism:** male PAR is diploid and heterozygous; uncoded it looks like X het. **Symptom:** males mis-called female; spurious sex PROBLEMs. **Fix:** `--split-par <build>` with the correct genome build (hg19 vs hg38 boundaries differ).

## Quantitative Thresholds

| Operation | Flag | Typical value | Rationale |
|-----------|------|---------------|-----------|
| Variant missingness | `--geno` | 0.02 (PCA/structure), 0.05 (standard) | default 0.1; >2-5% missing flags batch artifacts |
| Sample missingness | `--mind` | 0.02-0.05 | default 0.1; apply AFTER `--geno` |
| MAF | `--maf` | 0.01 (common-variant GWAS), 0.05 (PCA), down to 0.001 at large N | below ~0.01 power and HWE/sex-check stability collapse |
| HWE | `--hwe ... midp` | 1e-6 controls-only | loose vs association: screens artifacts, not biology |
| Sex F | `--check-sex` | female <0.2, male >0.8 (default) | re-pick from the F histogram gap |
| Heterozygosity | `--het` | \|F - mean\| > 3 SD | excess het = contamination, deficit = inbreeding/dup; on LD-pruned SNPs |
| Relatedness (KING) | `--king-cutoff` | 0.0884 (2nd-deg+), 0.177 (1st), 0.354 (dup/MZ cutoff; a true MZ/dup pair sits at ~0.5) | KING boundaries, Manichaikul 2010 |

Thresholds are conventions, not laws - inspect the distributions and verify current best practice before applying numbers blindly.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `--hwe-all` "unrecognized flag" | flag does not exist | controls-only override is `include-nonctrl` (1.9); plink2 needs `--keep-if "PHENO1 == control"` |
| HWE over-filters real associations | assuming plink2 `--hwe` is controls-only | it is not; gate to controls first; always add `midp` |
| ALT_FREQ read as MAF | plink2 `--freq` reports ALT frequency | inspect columns; PLINK 1.9 `--freq` reports MAF |
| Script reads empty missingness file | wrong suffix | 2.0 `.smiss/.vmiss`, 1.9 `.imiss/.lmiss` |
| `--keep-fam sample_id` keeps nothing | `--keep-fam` takes a FILE of FIDs | use `--keep` with a FID IID file |
| Frequencies use a subset in family data | MAF/HWE/`--freq` are founders-only | add `--nonfounders` if intended |
| Duplicate variant IDs break `--extract`/merge | duplicate IDs | `--rm-dup force-first` or set `chr:pos:ref:alt` IDs |

## References

1. Purcell S, et al. PLINK: a tool set for whole-genome association and population-based linkage analyses. American Journal of Human Genetics 2007; 81(3):559-575. DOI:10.1086/519795.
2. Chang CC, Chow CC, Tellier LCAM, Vattikuti S, Purcell SM, Lee JJ. Second-generation PLINK: rising to the challenge of larger and richer datasets. GigaScience 2015; 4:7. DOI:10.1186/s13742-015-0047-8.
3. Manichaikul A, Mychaleckyj JC, Rich SS, Daly K, Sale M, Chen W-M. Robust relationship inference in genome-wide association studies. Bioinformatics 2010; 26(22):2867-2873. DOI:10.1093/bioinformatics/btq559.
4. Wigginton JE, Cutler DJ, Abecasis GR. A note on exact tests of Hardy-Weinberg equilibrium. American Journal of Human Genetics 2005; 76(5):887-893. DOI:10.1086/429864.
5. Graffelman J, Moreno V. The mid p-value in exact tests for Hardy-Weinberg equilibrium. Statistical Applications in Genetics and Molecular Biology 2013; 12(4):433-448. DOI:10.1515/sagmb-2012-0039.

## Related Skills

- linkage-disequilibrium - LD pruning and clumping on QC'd genotypes
- population-structure - PCA and ADMIXTURE after QC and relatedness pruning
- association-testing - GWAS with `--glm` on the filtered fileset
- variant-calling/vcf-basics - VCF generation and manipulation before conversion
- phasing-imputation/genotype-imputation - imputed dosages that enter as `.pgen`
<!-- END FILE: population-genetics/plink-basics/SKILL.md -->

## 子目录：population-genetics/population-structure

<!-- BEGIN FILE: population-genetics/population-structure/SKILL.md -->
---
name: bio-population-genetics-population-structure
description: Infers and describes population structure with PCA (plink2 --pca, smartpca/EIGENSOFT, FlashPCA2), model-based clustering (ADMIXTURE, fastSTRUCTURE), FST estimators (Weir-Cockerham vs Hudson), and f-statistics (f3/f4/D via AdmixTools/admixr), plus Python plotting of PCs and Q barplots. Every output is a model-conditioned description of variance, not truth: PCs conflate ancestry with LD/inversions/relatedness/batch, ADMIXTURE Q-values are panel- and K-dependent artifacts, and CV-minimum K is a guide not the true population count. FST must combine SNPs as a ratio of averages (sum numerators / sum denominators), never an average of per-SNP FST; negative per-SNP FST is normal and must not be clamped. f3/f4/D need a block jackknife or the significance is fake. Use when running PCA, ADMIXTURE, FST, or f-statistics on QC'd genotypes. For QC and KING relatedness see plink-basics; for LD pruning see linkage-disequilibrium; for array-based Python pipelines see scikit-allel-analysis.
tool_type: mixed
primary_tool: plink2
---

## Version Compatibility

Reference examples tested with: PLINK 2.0 (alpha 6+), ADMIXTURE 1.3+, EIGENSOFT 7.2+, scikit-allel 1.3+, numpy 1.26+, pandas 2.2+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Version traps that change results, not just syntax: ADMIXTURE is a standalone CLI (`admixture --cv input.bed K`), never an R or Python package, and `--cv` defaults to 5-fold. plink2 `--pca` builds on the variance-standardized relationship matrix from `--make-rel`/`--make-grm` and has no Tracy-Widom test; smartpca does. plink2 `--make-king` gives kinship (cutoff 0.0884 = second-degree), not the deprecated PI_HAT from PLINK 1.9 `--genome`. f-statistics live in AdmixTools (CLI) wrapped by admixr (R), not in plink. The single source of truth for versions is this block, not headings.

# Population Structure

**"Analyze the population structure in my genotypes"** -> Project genotype covariance into continuous axes or discrete clusters, after pruning the artifacts the model would otherwise mistake for ancestry, and attach the uncertainty machinery any interpreted statistic requires.
- CLI: `plink2 --pca 20 approx` (top eigenvectors of the relationship matrix; LD-pruned, relatives removed first)
- CLI: `admixture --cv data_pruned.bed 3` (maximum-likelihood mixing weights for K abstract clusters)
- Python: `allel.hudson_fst(ac1, ac2)` then `num.sum()/den.sum()` (FST as a ratio of averages)

Scope: PCA, model-based clustering (ADMIXTURE/fastSTRUCTURE), FST estimators, and f-/D-statistics, with Python plotting. QC and KING relatedness route to plink-basics; LD pruning to linkage-disequilibrium; array-scale Python diversity/FST windows to scikit-allel-analysis; phased haplotype work to phasing-imputation/haplotype-phasing; introgression detection to comparative-genomics/introgression-detection.

## The Single Most Important Insight -- every structure method returns a model-conditioned description of variance, not truth

1. The output is a deterministic function of three silent choices: which samples are in the panel, which SNPs survive ascertainment/QC/LD-pruning, and which model is imposed (continuous PCs vs K discrete clusters vs a tree-with-admixture); change any one and the "answer" changes.
2. PCA does not find ancestry, it finds the directions of greatest genotype covariance, which conflate ancestry with LD blocks, inversions, relatedness, batch, and differential missingness, so the mandatory work is pruning those out before reading axes.
3. ADMIXTURE Q-values are not ancestry fractions but maximum-likelihood weights on K abstract allele-frequency vectors that exist only because K of them were requested, and the CV-minimum K is a prediction-accuracy guide, not the true number of populations.
4. Any interpreted statistic needs its own uncertainty: FST combines across SNPs as a ratio of averages (never an average of per-SNP FST), negative per-SNP FST is kept not clamped, and every f3/f4/D needs a block-jackknife standard error or the significance is fabricated.

## Tool Taxonomy

| Method | Citation | Mechanism / role | When |
|--------|----------|------------------|------|
| plink2 `--pca` | Patterson 2006; Price 2006 | Eigenvectors of the variance-standardized relationship matrix; `approx` for large N | Stratification covariates, gross structure, QC outliers |
| smartpca (EIGENSOFT) | Patterson 2006 | PCA plus Tracy-Widom significance, outlier removal, `lsqproject` projection | Rigorous PCA, aDNA projection, per-PC p-values |
| FlashPCA2 | Abraham 2017 | Randomized PCA for biobank N (>100k) | Very large cohorts |
| ADMIXTURE | Alexander 2009 | Fast ML point estimate of Q (ancestry weights) and P (cluster frequencies) | Genome-wide discrete ancestry proportions |
| fastSTRUCTURE | Raj 2014 | Variational Bayes clustering with `chooseK.py` K guidance | Fast K exploration |
| Hudson FST | Hudson 1992; Bhatia 2013 | Per-SNP heterozygosity estimator; ratio of averages | Pairwise differentiation, unequal sample sizes, rare variants / SNP-array ascertainment |
| Weir-Cockerham FST | Weir & Cockerham 1984 | ANOVA estimator (a/(a+b+c)); ratio of averages | Classic variance-partition framing, balanced n |
| f3 / f4 / D | Patterson 2012; Durand 2011 | Drift-distance tests of admixture and tree-ness; block jackknife | Admixture detection, gene-flow tests |
| TreeMix | Pickrell 2012 | ML tree plus migration edges from frequency covariance | Tree + migration hypotheses |
| admixr / AdmixTools | Petr 2019; Patterson 2012 | Reproducible R wrappers for qp3Pop/qpDstat/qpAdm/qpGraph | f-statistics and admixture graphs |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Stratification covariates for GWAS | plink2 `--pca` (`approx` >5000) | assumption-light, fast, feeds `--glm` directly |
| Per-PC significance, outlier removal, aDNA projection | smartpca | Tracy-Widom test plus `lsqproject` for shrinkage-robust projection |
| Biobank-scale PCA (>100k) | plink2 `--pca approx` or FlashPCA2 | randomized algorithms scale; exact PCA does not |
| Discrete ancestry proportions | ADMIXTURE over a K span (`--cv` as guide) | present a span, never the CV argmin alone |
| Fast K exploration | fastSTRUCTURE + `chooseK.py` | variational, very fast |
| Pairwise differentiation, unequal n or rare variants | Hudson FST, ratio of averages | Bhatia 2013; WC is sensitive to n, population count, and rare variants |
| "Is population C admixed?" | f3(C; A,B) (qp3Pop / admixr) | f3 < 0 proves admixture; block-jackknife Z |
| "Is there gene flow / introgression?" | D / f4 (qpDstat, ABBA-BABA) | `|Z|` > 3; cannot separate from ancient structure alone |
| Clinal / spatial structure | EEMS, Mantel | clines are isolation-by-distance, not discrete demes |
| Relatedness QC before everything | plink2 `--king-cutoff` (see plink-basics) | a relative cluster grabs a spurious PC |

## Mandatory Preprocessing Before PCA

**Goal:** Compute PCs that track ancestry rather than inversions, relatedness, or batch.

**Approach:** LD-prune, exclude long-range-LD/inversion regions by coordinate, remove relatives before computing axes, drop very-low-MAF variants, then run PCA on the survivors.

```bash
# LD-prune so a single dense block cannot dominate a PC (route detail to linkage-disequilibrium).
plink2 --bfile data --indep-pairwise 50 5 0.1 --out prune

# Exclude long-range-LD regions and inversions that survive pruning and create karyotype PCs.
# range_lrld.txt holds MHC chr6:25-35 Mb, 8p23.1, 17q21.31, and LCT/2q21 in plink --exclude range format.
plink2 --bfile data --extract prune.prune.in --exclude range range_lrld.txt --maf 0.01 \
    --make-bed --out data_for_pca

# PCA on the LD-pruned, inversion-stripped, relatedness-pruned set. approx is near-required above ~50k.
plink2 --bfile data_for_pca --pca 20 approx --out pca
# Outputs: pca.eigenvec (FID IID PC1..PCn), pca.eigenval (variance per PC).
```

Relatives must be removed BEFORE computing axes (a cluster of cousins forms its own high-covariance PC); compute the KING cutoff with `plink2 --king-cutoff 0.0884` from plink-basics, build PCs on the unrelated set, then project relatives back. plink2 has no Tracy-Widom test: feed the eigenvalues to smartpca `twstats` or read a scree elbow to decide which PCs are real.

## Rigorous PCA and Projection (smartpca)

**Goal:** Attach per-PC significance and project new/ancient samples without shrinkage artifacts.

**Approach:** Run smartpca with outlier iterations and Tracy-Widom output for the reference build, and use `lsqproject: YES` to place additional samples robustly to missingness.

```bash
# smartpca parameter file (key params verified against the EIGENSOFT POPGEN README):
#   numoutevec: 20            # PCs to output (default 10)
#   numoutlieriter: 5         # outlier-removal iterations (default 5; 0 disables)
#   outliersigmathresh: 6.0   # SD threshold for outlier removal (default 6.0)
#   lsqproject: YES           # least-squares projection, robust to missing data (aDNA standard)
#   poplistname: ref_pops.txt # which populations build the axes (others are projected)
#   altnormstyle: NO          # NO = Price 2006 EIGENSTRAT normalization; YES = Patterson 2006
smartpca -p smartpca.par
# Tracy-Widom test on the eigenvalues: only PCs with p < ~0.05 plus a scree elbow are interpretable.
twstats -t twtable -i out.eval -o out.tw
```

Projected scores shrink toward the origin, worse with a small reference panel (<~5000) and more missing data, so an ancient sample plotting "between" two clusters may be shrunk, not admixed; `lsqproject` is the standard fix. plink2 projects via `--pca allele-wts` then `--score` on the `.eigenvec.allele` weights, but does not correct shrinkage.

## ADMIXTURE Over a K Span

**Goal:** Estimate discrete ancestry proportions while treating K as a model-selection choice, not a discovery.

**Approach:** Run ADMIXTURE on LD-pruned data across a span of K with cross-validation, plot CV error as a guide, and check Q stability across seeds before interpreting any single K.

```bash
# admixture is a standalone CLI; --cv defaults to 5-fold. -jN threads, -BN bootstrap SEs.
for K in $(seq 2 8); do
    admixture --cv -j4 data_pruned.bed "$K" 2>&1 | tee "log_K${K}.out"
done
# Outputs per K: data_pruned.K.Q (N x K ancestry weights) and data_pruned.K.P (cluster frequencies).
# CV error prints as: CV error (K=3): 0.512 -- a guide, never "the true number of populations".
grep -h "CV error" log_K*.out
```

Supervised mode (`admixture --supervised data_pruned.bed K`, reading `data_pruned.pop` with one label per individual, blank for unknowns) fixes labeled individuals to their population but assumes the reference populations are themselves unadmixed. Replicate Q at the same K can land in different local optima; align cluster labels across runs with CLUMPP or pong before averaging or plotting, and treat unstable Q as a sign of mis-specified K, not noise to smooth away.

## FST as a Ratio of Averages

**Goal:** Estimate pairwise differentiation without the average-of-ratios bias.

**Approach:** Compute per-SNP Hudson numerators and denominators, keep negative numerators, then divide summed numerators by summed denominators across SNPs.

```python
import allel
import numpy as np

# ac1, ac2 are AlleleCountsArrays for the two populations at the same SNPs (see scikit-allel-analysis).
num, den = allel.hudson_fst(ac1, ac2)   # per-SNP Hudson numerator and denominator (Bhatia 2013)
fst = num.sum() / den.sum()             # RATIO OF AVERAGES across SNPs; never np.mean(num/den)
# Negative per-SNP numerators are normal sampling behavior near FST=0 and stay in the sum.
# Use Weir-Cockerham only with balanced n: allel.weir_cockerham_fst returns a, b, c variance components.
a, b, c = allel.weir_cockerham_fst(genotype_array, subpops)
fst_wc = np.nansum(a) / np.nansum(a + b + c)   # still a ratio of averages
```

The Hudson estimator is preferred under sample-size asymmetry because Weir-Cockerham's finite-sample correction makes it sensitive to n and to the number of populations; the two can disagree enough to cross a Wright differentiation band. SNP-array ascertainment compresses and warps FST relative to whole-genome sequencing, so cross-study comparisons require matched ascertainment.

## f-statistics with a Block Jackknife (admixr)

**Goal:** Test admixture and gene flow with honest standard errors.

**Approach:** Run f3/f4/D through AdmixTools (wrapped by admixr) so each statistic carries a block-jackknife SE, and read Z, never a raw point estimate.

```r
library(admixr)
# admixr wraps AdmixTools (Petr 2019); each call returns the statistic with a block-jackknife SE and Z.
data <- eigenstrat('prefix')
res_f3 <- f3(A = 'PopA', B = 'PopB', C = 'PopC', data = data)   # f3(C; A,B) < 0 with Z < -3 proves C admixed
res_d  <- d(W = 'PopW', X = 'PopX', Y = 'PopY', Z = 'PopZ', data = data)  # |Z| > 3 indicates gene flow
```

A significantly negative f3 proves the target is admixed (no tree produces a negative f3), but a non-negative f3 is inconclusive, not proof of a clean tree: post-admixture drift in the target itself (a bottleneck after the admixture event), or heavily drifted sources, adds a positive term that can mask the negative cross-product even when admixture is real. A nonzero D or f4 is evidence of a tree violation, not specifically recent introgression: symmetric ancient structure mimics the same ABBA/BABA asymmetry (Durand 2011), so separating them needs admixture-LD decay or explicit modeling.

## Per-Method Failure Modes

### PCA tracks an inversion, not a deme
**Trigger:** PCA on LD-pruned data with MHC/8p23/17q21.31/LCT regions still in. **Mechanism:** megabase-long LD in inversions survives `--indep-pairwise` and dominates a PC. **Symptom:** a PC loads almost entirely on one chromosome arm and splits samples by karyotype. **Fix:** `--exclude range` the long-range-LD and inversion regions by coordinate before PCA.

### Relatives grab a principal component
**Trigger:** computing PCs before relatedness pruning. **Mechanism:** a cluster of relatives forms a high-covariance bundle. **Symptom:** a tight outlier cluster on a top PC that is not a real population. **Fix:** `--king-cutoff 0.0884` first, build PCs on the unrelated set, project relatives back.

### Projection shrinkage misread as admixture
**Trigger:** projecting new/ancient/low-coverage samples onto reference PCs naively. **Mechanism:** projected scores are biased toward the origin, worse with small panels and missing data. **Symptom:** a sample plots "between" two clusters and is narrated as admixed. **Fix:** smartpca `lsqproject: YES`; do not interpret shrunk scores as intermediacy.

### CV-minimum K over-splits
**Trigger:** picking K at the CV argmin when the curve plateaus or keeps falling. **Mechanism:** CV error is prediction accuracy, not a population count. **Symptom:** uninterpretable extra clusters at high K. **Fix:** run K across a span with at least 10 seeds each (`-s`), align replicates with pong/CLUMPP, and report the K where CV error plateaus AND Q is seed-stable; if CV and stability disagree, present both and let sampling design plus orthogonal evidence pick the interpreted K.

### Label switching corrupts averaged barplots
**Trigger:** averaging Q across runs or seeds without alignment. **Mechanism:** cluster labels permute arbitrarily between runs. **Symptom:** a smeared, meaningless mean barplot. **Fix:** align labels with CLUMPP or pong before averaging; treat unstable Q as a mis-specification warning.

### Average-of-ratios FST
**Trigger:** combining per-SNP FST as `mean(num/den)`. **Mechanism:** low-MAF SNPs have tiny denominators and dominate the mean. **Symptom:** badly biased genome-wide FST. **Fix:** ratio of averages, `num.sum()/den.sum()`; never clamp negative per-SNP values first.

### f-statistic significance without a jackknife
**Trigger:** naive SNP-level standard errors for f3/f4/D. **Mechanism:** LD correlates neighboring SNPs, so per-SNP SEs are far too small. **Symptom:** everything looks significant. **Fix:** block-jackknife SE (drop ~5 cM blocks); report Z with `|Z|` > 3.

### Clinal sample forced into discrete clusters
**Trigger:** running K-cluster ADMIXTURE on an isolation-by-distance continuum. **Mechanism:** smooth clines have no discrete demes. **Symptom:** phantom populations and "admixed" intermediates that are really IBD. **Fix:** describe clinal structure with EEMS / Mantel, not a STRUCTURE barplot.

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|----------|-----------|--------------------|
| LD pruning for PCA/ADMIXTURE | `--indep-pairwise 50 5 0.1` (range 0.05-0.2) | near-independence so structure is not double-counted (see linkage-disequilibrium) |
| MAF floor before PCA | drop MAF < ~0.01 (often < 0.05) | plink2 docs: very-low-MAF variants destabilize PCA |
| Relatedness removal | KING `--king-cutoff 0.0884` (2nd-degree) | KING boundaries 0.354/0.177/0.0884/0.0442 = MZ/1st/2nd/3rd |
| PC significance | Tracy-Widom p < 0.05 plus scree elbow | Patterson 2006; TW null for the largest eigenvalue |
| smartpca outlier removal | `outliersigmathresh 6.0`, `numoutlieriter 5` | EIGENSOFT defaults |
| ADMIXTURE CV | default 5-fold; `--cv=10` for stability | Alexander/Shringarpure manual |
| f3/f4/D significance | `|Z|` > 3 (block jackknife) | Patterson 2012 convention (~3 SE) |
| FST bands (Wright guideposts) | 0-0.05 little, 0.05-0.15 moderate, 0.15-0.25 great, >0.25 very great | heuristic only; estimator-, MAF-, ascertainment-dependent |
| Negative per-SNP FST | keep (do not clamp) | unbiased estimators yield negatives near FST=0 by sampling |

Thresholds are conventions, not laws; the FST bands predate SNP arrays, and the estimator, MAF spectrum, ascertainment, and sample size each move FST by a whole band. Verify current best practice before applying numbers blindly.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `import admixture` fails | ADMIXTURE is a CLI, not a package | run `admixture --cv data.bed K` on the shell |
| CV argmin reported as the true K | reading CV error as a population count | present a K span; CV is a guide, check Q stability |
| A PC tracks one chromosome arm | inversion/long-range-LD region left in | `--exclude range` MHC/8p23/17q21.31/LCT before PCA |
| Outlier cluster is "a new population" | relatives not removed before PCA | `--king-cutoff 0.0884` first, project relatives back |
| Genome-wide FST is biased high | average-of-ratios and/or clamped negatives | ratio of averages; keep negative per-SNP values |
| WC and Hudson FST disagree | unequal sample sizes between populations | prefer Hudson under sample-size asymmetry (Bhatia 2013) |
| Everything is f3/D-significant | naive (non-jackknife) standard errors | use block-jackknife SE; report Z, `|Z|` > 3 |
| Non-negative f3 read as "no admixture" | post-admixture drift in the target (or drifted sources) masks the negative term | non-negative f3 is inconclusive, not a clean tree |
| Smeared mean Q barplot | label switching across replicates | align with CLUMPP/pong before averaging |

## References

1. Patterson N, Price AL, Reich D. Population structure and eigenanalysis. PLoS Genetics 2006; 2(12):e190. DOI:10.1371/journal.pgen.0020190.
2. Price AL, Patterson NJ, Plenge RM, Weinblatt ME, Shadick NA, Reich D. Principal components analysis corrects for stratification in genome-wide association studies. Nature Genetics 2006; 38(8):904-909. DOI:10.1038/ng1847.
3. Alexander DH, Novembre J, Lange K. Fast model-based estimation of ancestry in unrelated individuals. Genome Research 2009; 19(9):1655-1664. DOI:10.1101/gr.094052.109.
4. Raj A, Stephens M, Pritchard JK. fastSTRUCTURE: variational inference of population structure in large SNP data sets. Genetics 2014; 197(2):573-589. DOI:10.1534/genetics.114.164350.
5. Weir BS, Cockerham CC. Estimating F-statistics for the analysis of population structure. Evolution 1984; 38(6):1358-1370. DOI:10.1111/j.1558-5646.1984.tb05657.x.
6. Hudson RR, Slatkin M, Maddison WP. Estimation of levels of gene flow from DNA sequence data. Genetics 1992; 132(2):583-589. DOI:10.1093/genetics/132.2.583.
7. Bhatia G, Patterson N, Sankararaman S, Price AL. Estimating and interpreting FST: the impact of rare variants. Genome Research 2013; 23(9):1514-1521. DOI:10.1101/gr.154831.113.
8. Patterson N, Moorjani P, Luo Y, Mallick S, Rohland N, Zhan Y, Genschoreck T, Webster T, Reich D. Ancient admixture in human history. Genetics 2012; 192(3):1065-1093. DOI:10.1534/genetics.112.145037.
9. Durand EY, Patterson N, Reich D, Slatkin M. Testing for ancient admixture between closely related populations. Molecular Biology and Evolution 2011; 28(8):2239-2252. DOI:10.1093/molbev/msr048.
10. Pickrell JK, Pritchard JK. Inference of population splits and mixtures from genome-wide allele frequency data. PLoS Genetics 2012; 8(11):e1002967. DOI:10.1371/journal.pgen.1002967.
11. Petr M, Vernot B, Kelso J. admixr - R package for reproducible analyses using ADMIXTOOLS. Bioinformatics 2019; 35(17):3194-3195. DOI:10.1093/bioinformatics/btz030.
12. Abraham G, Qiu Y, Inouye M. FlashPCA2: principal component analysis of Biobank-scale genotype datasets. Bioinformatics 2017; 33(17):2776-2778. DOI:10.1093/bioinformatics/btx299.

## Related Skills

- plink-basics - QC, KING relatedness pruning, and fileset preparation before structure analysis
- linkage-disequilibrium - LD pruning the SNP set that PCA and ADMIXTURE require
- scikit-allel-analysis - array-scale FST and diversity windows in Python
- phasing-imputation/haplotype-phasing - phased haplotypes for haplotype-based structure methods
- comparative-genomics/introgression-detection - D/f4 introgression scans beyond pairwise tests
<!-- END FILE: population-genetics/population-structure/SKILL.md -->

## 子目录：population-genetics/rare-variant-association

<!-- BEGIN FILE: population-genetics/rare-variant-association/SKILL.md -->
---
name: bio-population-genetics-rare-variant-association
description: Gene and region-based rare-variant aggregation - burden/collapsing, SKAT, SKAT-O, ACAT-V/ACAT-O, annotation-weighted STAAR - with regenie (--vc-tests), SAIGE-GENE+, and the SKAT R package. Single-variant tests are powerless at low minor allele count, so rare variants are aggregated across a gene or region under an explicit mask (functional class plus a MAF cutoff). A burden test collapses variants into one score assuming a single effect direction (powerful when true, near-zero power when risk and protective variants cancel); SKAT is a variance-component test robust to mixed directions; SKAT-O blends the two; ACAT/STAAR are dependence-robust and annotation-weighted. The mask is the hypothesis, imbalance needs SPA or Firth, and testing burden is per-gene-per-mask. Use when aggregating rare coding or regulatory variants into gene or region tests, choosing burden vs SKAT vs SKAT-O, or building masks. For single-variant GWAS see association-testing; for mask annotations see variant-calling/variant-annotation.
tool_type: mixed
primary_tool: regenie
---

## Version Compatibility

Reference examples tested with: regenie 3.4+, SAIGE 1.3+, SKAT 2.2+ (R), STAAR 0.9.7+ (R).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Version traps that change results, not just syntax: regenie `--vc-tests` accepts `skat,skato,skato-acat,acatv,acato,acato-full` (not `skat-o`), `--aaf-bins` upper bounds always add an implicit singleton mask, and `--build-mask` defaults to `max` (one carrier-status column per set) not `sum`. SAIGE-GENE+ `--maxMAF_in_groupTest` takes multiple comma-separated cutoffs in ONE run (the whole point of GENE+ over GENE). The SKAT R package selects SKAT-O with `method="optimal.adj"` or `method="SKATO"`, and `r.corr` is the rho grid (0=SKAT, 1=burden); `weights.beta=c(1,25)` is the rarer-up-weighting default. The single source of truth for versions is this block, not headings.

# Rare-Variant Association

**"Test whether rare variants in this gene associate with my trait"** -> Aggregate the rare variants in a gene or region into one set-based statistic under an explicit mask, because no single rare variant has enough carriers to test alone.
- CLI: `regenie --step 2 --anno-file ... --set-list ... --mask-def ... --aaf-bins 0.01 --vc-tests skato,acato` (biobank masks plus omnibus tests)
- CLI: `step2_SPAtests.R --groupFile ... --annotation_in_groupTest lof,missense;lof --maxMAF_in_groupTest 0.0001,0.001,0.01` (SAIGE-GENE+, imbalance-robust)
- R: `SKAT(Z, obj, method="SKATO", weights.beta=c(1,25))` (direct, small cohorts)

Scope: gene/region-based rare-variant aggregation (burden, SKAT, SKAT-O, ACAT-V/ACAT-O, STAAR), variant masks (functional class plus MAF cutoff), and the per-gene multiple-testing burden. Single-variant GWAS (linear/logistic/LMM/SPA per marker) routes to association-testing. The functional annotations that define masks (LoF, missense, CADD, regulatory) come from variant-calling/variant-annotation. Variant prioritization for clinical interpretation routes to clinical-databases/variant-prioritization.

## The Single Most Important Insight -- a gene-based test is a bet about the direction-of-effect architecture, and the mask IS the hypothesis

1. Single-variant GWAS is underpowered for rare variants because a handful of carriers gives a tiny non-centrality, so signal must be aggregated across a gene or region - and HOW it is aggregated encodes a belief about the unobserved effect architecture.
2. A burden test collapses the set into one direction and is the most powerful test WHEN that holds, but mixing risk and protective variants makes their contributions cancel to a null (false negative); SKAT sums squared scores so directions cannot cancel but is weaker when the truth is unidirectional; SKAT-O optimizes a rho grid between the two and is the default when the architecture is unknown.
3. The MASK is the hypothesis, not a preprocessing detail: which variants enter (LoF-only vs LoF+missense, MAF<0.01 vs <0.001, annotation weights) defines what is being tested, and a different mask is a different question with a different answer - so report the mask, not just the p-value.
4. The aggregate is only as calibrated as the null model: case/control imbalance and low MAC make naive set tests anti-conservative (SAIGE-GENE+ uses SPA, regenie uses Firth/SPA), population structure and relatedness still need an LMM null, and imputed/low-quality variants silently corrupt the mask unless filtered by INFO/R2 and genotype quality first.

## Tool Taxonomy

| Method | Citation | Mechanism | When |
|--------|----------|-----------|------|
| Burden / collapsing (CMC, weighted-sum) | Li & Leal 2008; Madsen & Browning 2009 | Collapse variants into one score, test its single coefficient; assumes one effect direction | Strong prior that variants act the same way (e.g. LoF in a gene) |
| SKAT | Wu 2011 | Variance-component score test on summed squared weighted single-variant scores; directions do not cancel | Mixed directions, or many neutral variants diluting the set |
| SKAT-O | Lee 2012 | Optimal linear combination of burden and SKAT over a rho grid in [0,1]; data choose rho | Unknown architecture - the safe default |
| ACAT-V / ACAT-O | Liu 2019 | Cauchy combination of p-values, calibrated under arbitrary dependence, no permutation/GRM; the smallest p dominates (one artifact can drive it) | Sparse-causal sets, fast omnibus, combining masks/tests |
| STAAR / STAAR-O | Li 2020 | Variance-component test weighting variants by multiple functional annotations (annotation PCs) | WGS regulatory regions where annotations carry the signal |
| SAIGE-GENE+ | Zhou 2022 | LMM null + SPA + variance ratio; multiple MAF cutoffs and annotations in one set test | Biobank binary traits, case/control imbalance, relatedness |
| regenie --vc-tests | Mbatchou 2021 | Whole-genome ridge null (step 1), then masked burden/SKAT/SKAT-O/ACAT in step 2 with Firth/SPA | Biobank pipelines wanting single-variant and gene tests together |

## Decision Tree by Scenario

| Scenario | Use | Why |
|----------|-----|-----|
| Strong prior all variants act one direction (LoF mask) | Burden / collapsing | Most powerful under a true single direction |
| Risk and protective variants expected in the same set | SKAT | Squared scores, directions do not cancel |
| Architecture unknown | SKAT-O | Optimizes rho between burden and SKAT |
| Sparse causal set, or one omnibus across masks | ACAT-V / ACAT-O | Dependence-robust Cauchy combiner, no permutation |
| WGS noncoding where annotations carry the signal | STAAR-O | Multiple functional-annotation weights in one test |
| Biobank, imbalanced binary trait, relatedness | SAIGE-GENE+ | SPA + LMM null keeps the tail calibrated at low MAC |
| One pipeline for single-variant + gene tests at biobank scale | regenie --vc-tests | Shared step-1 null, Firth/SPA in step 2 |
| Small cohort, full control of mask and weights | SKAT R package | Direct, scriptable, SSD files for many sets |

## Build the Mask and Run Aggregate Tests with regenie

**Goal:** test each gene under one or more masks (functional class x MAF cutoff) using burden plus variance-component tests in a biobank-scale pipeline.

**Approach:** reuse the step-1 whole-genome ridge null, then in step 2 define annotations, gene sets, and mask rules and request the omnibus tests, letting Firth handle imbalanced binary traits.

```bash
# Step 1 builds the LOCO whole-genome predictor (the null) once, shared with single-variant GWAS.
regenie --step 1 --bed geno_array --phenoFile pheno.txt --covarFile covar.txt \
    --bsize 1000 --lowmem --out fit_null

# Step 2: --anno-file maps variant -> gene -> annotation; --set-list lists each gene's variants;
# --mask-def names which annotation categories form each mask. --aaf-bins sets the MAF ceilings
# (a singleton mask is always added). --vc-tests requests SKAT-O and the ACAT omnibus alongside
# burden. --firth keeps the imbalanced binary-trait tail calibrated; --build-mask max is the default.
regenie --step 2 --bed geno_wes --phenoFile pheno.txt --covarFile covar.txt \
    --pred fit_null_pred.list --anno-file annot.txt --set-list sets.txt --mask-def masks.txt \
    --aaf-bins 0.001,0.01 --vc-tests skato,acato --build-mask max \
    --bt --firth --approx --pThresh 0.05 --out gene_tests
```

Mask-building file formats (one entry per line, space/tab separated):
- `annot.txt`: `VARIANT_ID GENE ANNOTATION` (e.g. `1:55039839:T:C PCSK9 LoF`); variants with no entry fall in `NULL`.
- `sets.txt`: `GENE CHR POS VARIANT_ID,VARIANT_ID,...` (the gene plus its comma-separated variant list).
- `masks.txt`: `MASK_NAME ANNOTATION,ANNOTATION` (e.g. `Mask_LoF LoF` and `Mask_LoF_mis LoF,missense`).

Run `regenie --step 2 ... --check-burden-files --ignore-pred` first to catch variants in the set-list that are absent from the annotation file (a silent source of empty or wrong masks). `--ignore-pred` is required here because this validation runs before the step-1 predictor exists.

## Imbalance-Robust Set Tests with SAIGE-GENE+

**Goal:** test genes for an imbalanced binary trait in a related sample, scanning several MAF cutoffs and annotation groups in one pass.

**Approach:** fit the SPA-LMM null once (step 1, with a variance ratio), then run the set test passing multiple annotations and multiple max-MAF thresholds so GENE+ combines them.

```bash
# Step 2 set test. --annotation_in_groupTest gives the masks (semicolon-separated groups, each a
# comma-separated annotation list). --maxMAF_in_groupTest passes several MAF cutoffs in ONE run -
# this multi-cutoff combination is exactly what GENE+ adds over the original SAIGE-GENE.
step2_SPAtests.R --bgenFile geno_wes.bgen --groupFile groups.txt \
    --GMMATmodelFile null.rda --varianceRatioFile null.varianceRatio.txt \
    --annotation_in_groupTest "lof;lof,missense;lof,missense,synonymous" \
    --maxMAF_in_groupTest 0.0001,0.001,0.01 --is_output_moreDetails TRUE \
    --SAIGEOutputFile gene_tests.txt
```

The `groups.txt` file gives, per gene, a line of variant IDs and a matching line of their annotations (and optionally a weight line); the annotation labels there must match `--annotation_in_groupTest`.

## Direct SKAT-O in R for a Small Cohort

**Goal:** run burden, SKAT, and SKAT-O on a gene's rare-variant genotype matrix with explicit MAF weighting, for a sample small enough to hold in memory.

**Approach:** fit the null model once on covariates, then call SKAT per gene with the rho grid; for many genes use SSD files keyed by a SetID rather than passing matrices.

```r
library(SKAT)

# Null model on covariates only (out_type='D' binary, 'C' continuous). Refit once, reuse per gene.
obj <- SKAT_Null_Model(phenotype ~ age + sex + PC1 + PC2, out_type = 'D', data = covar_df)

# Z is the n x m genotype matrix (0/1/2) for the m rare variants in one gene.
# weights.beta=c(1,25) is the Beta(MAF;1,25) up-weighting of rarer variants (the SKAT default; the
# Madsen-Browning weight is the gentler Beta(0.5,0.5)). method='SKATO' searches the rho grid (rho=0
# SKAT, rho=1 burden); 'burden' or default SKAT recover the endpoints. r.corr passes an explicit rho grid.
skato <- SKAT(Z, obj, method = 'SKATO', weights.beta = c(1, 25))
burden <- SKAT(Z, obj, r.corr = 1, weights.beta = c(1, 25))
skat <- SKAT(Z, obj, weights.beta = c(1, 25))
c(skato = skato$p.value, burden = burden$p.value, skat = skat$p.value)
```

For genome-wide gene scans, build an SSD file with `Generate_SSD_SetID(bed, bim, fam, SetID, SSD, Info)`, `Open_SSD()`, then `SKAT.SSD.All(SSD.INFO, obj)` to test every set without holding all matrices in memory.

## Per-Method Failure Modes

### Burden test cancels under mixed directions
**Trigger:** a mask mixing risk and protective (or many null) variants. **Mechanism:** the collapsed score sums signed contributions that offset. **Symptom:** near-null p for a gene that SKAT flags strongly. **Fix:** use SKAT or SKAT-O; reserve pure burden for a mask with a real single-direction prior (LoF-only).

### SKAT underpowered when truth is unidirectional
**Trigger:** a clean LoF mask where every variant raises risk. **Mechanism:** the variance-component test spends power on a 2-sided alternative it does not need. **Symptom:** burden hits, SKAT does not. **Fix:** SKAT-O (lets rho->1) or a burden test for that mask.

### Wrong or default mask
**Trigger:** running one default MAF cutoff or an unfiltered annotation set. **Mechanism:** the mask defines the hypothesis; a too-loose MAF or LoF+benign-missense mask dilutes signal with noise. **Symptom:** a true gene disappears under one mask, appears under another. **Fix:** test a small grid of masks (LoF, LoF+missense; MAF 0.001, 0.01) and combine with ACAT-O, accounting for the masks in the burden.

### Uncalibrated tail under case/control imbalance
**Trigger:** a naive set test on an imbalanced binary trait at low MAC. **Mechanism:** the score statistic's normal/chi-square null is wrong in the tail. **Symptom:** anti-conservative gene p-values, inflated QQ for rare masks. **Fix:** SAIGE-GENE+ (SPA) or regenie `--firth`/`--spa`; never a plain score test here.

### Residual structure/relatedness in the null
**Trigger:** aggregating in a structured or related sample with a fixed-effect-only null. **Mechanism:** relatedness is a covariance structure PCs cannot remove. **Symptom:** genome-wide gene inflation that PCs do not fix. **Fix:** an LMM null (SAIGE-GENE+, regenie step-1 LOCO predictor) before the set test.

### Imputed/low-quality variants in the mask
**Trigger:** building masks from imputed or low-callrate genotypes. **Mechanism:** miscalled rare variants add spurious carriers. **Symptom:** unreplicable gene hits driven by a few low-quality sites. **Fix:** filter by INFO/R2 (>=0.8 for rare) and genotype quality before masking; prefer sequenced calls for rare-variant sets.

## Quantitative Thresholds

| Quantity | Typical value | Rationale |
|----------|---------------|-----------|
| "Rare" MAF cutoff for aggregation | MAF < 0.01 (< 0.001 for LoF-only) | below this single-variant power collapses; aggregate instead |
| Mask MAF tiers | 0.0001 / 0.001 / 0.01 | nested AAF bins capture ultra-rare and rare jointly (regenie `--aaf-bins`, SAIGE `--maxMAF_in_groupTest`) |
| Exome-wide gene significance | ~2.5e-6 | Bonferroni 0.05 over ~20,000 genes; tighten further for multiple masks per gene |
| Per-mask multiple testing | divide by (genes x masks) or combine masks via ACAT-O | each mask is a separate test unless an omnibus absorbs them |
| Ultra-rare collapsing (MAC) | collapse MAC < ~10 into one pseudo-variant | regenie `--vc-MACthr` default 10; SAIGE-GENE+ collapses ultra-rare for calibration |
| Imputed-variant quality for masks | INFO/R2 >= 0.8 (rare) | rare imputed dosages are noisy; lenient 0.3 cutoffs corrupt masks |
| SKAT MAF weighting | Beta(MAF; 1, 25) | `weights.beta=c(1,25)` up-weights rarer variants (Wu 2011 default) |

Thresholds are conventions; inspect the per-gene QQ plot and verify current best practice before applying numbers blindly.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| regenie `--vc-tests skat-o` unrecognized | wrong token | use `skato` (and `acato`, `acatv`, `skato-acat`); not `skat-o` |
| Empty or tiny masks, genes silently dropped | variants in set-list absent from anno-file | run `--check-burden-files` first; harmonize variant IDs |
| Inflated gene QQ for an imbalanced trait | plain score test, no SPA/Firth | SAIGE-GENE+ or regenie `--firth`/`--spa` |
| SKAT-O not actually run in R | passing `method="SKAT"` or omitting it | `method="SKATO"` or `"optimal.adj"`; `r.corr=1` is pure burden |
| Single MAF cutoff misses ultra-rare signal | one `--aaf-bins`/`--maxMAF` value | pass nested cutoffs (0.0001,0.001,0.01) in one run |
| Same single-variant p reported as "gene" | testing markers, not a set | confirm a set/group file is supplied and the test is set-based |
| Gene hit driven by one artifactual variant | ACAT/burden dominated by a miscalled site | QC inputs (INFO/R2, genotype quality) before aggregating |

## References

1. Li B, Leal SM. Methods for detecting associations with rare variants for common diseases: application to analysis of sequence data. American Journal of Human Genetics 2008; 83(3):311-321. DOI:10.1016/j.ajhg.2008.06.024.
2. Madsen BE, Browning SR. A groupwise association test for rare mutations using a weighted sum statistic. PLoS Genetics 2009; 5(2):e1000384. DOI:10.1371/journal.pgen.1000384.
3. Wu MC, Lee S, Cai T, Li Y, Boehnke M, Lin X. Rare-variant association testing for sequencing data with the sequence kernel association test. American Journal of Human Genetics 2011; 89(1):82-93. DOI:10.1016/j.ajhg.2011.05.029.
4. Lee S, Emond MJ, Bamshad MJ, et al. Optimal unified approach for rare-variant association testing with application to small-sample case-control whole-exome sequencing studies. American Journal of Human Genetics 2012; 91(2):224-237. DOI:10.1016/j.ajhg.2012.06.007.
5. Liu Y, Chen S, Li Z, Morrison AC, Boerwinkle E, Lin X. ACAT: a fast and powerful p value combination method for rare-variant analysis in sequencing studies. American Journal of Human Genetics 2019; 104(3):410-421. DOI:10.1016/j.ajhg.2019.01.002.
6. Li X, Li Z, Zhou H, et al. Dynamic incorporation of multiple in silico functional annotations empowers rare variant association analysis of large whole-genome sequencing studies at scale. Nature Genetics 2020; 52(9):969-983. DOI:10.1038/s41588-020-0676-4.
7. Mbatchou J, Barnard L, Backman J, et al. Computationally efficient whole-genome regression for quantitative and binary traits. Nature Genetics 2021; 53(7):1097-1103. DOI:10.1038/s41588-021-00870-7.
8. Zhou W, Bi W, Zhao Z, et al. SAIGE-GENE+ improves the efficiency and accuracy of set-based rare variant association tests. Nature Genetics 2022; 54(10):1466-1469. DOI:10.1038/s41588-022-01178-w.

## Related Skills

- association-testing - single-variant GWAS (linear/logistic/LMM/SPA per marker) that this skill aggregates beyond
- plink-basics - genotype QC and format conversion before masking
- population-structure - PCs and relatedness for the null model that calibrates the set test
- variant-calling/variant-annotation - functional annotations (LoF, missense, CADD, regulatory) that define masks
- clinical-databases/variant-prioritization - clinical interpretation of variants flagged by gene tests
- causal-genomics/fine-mapping - resolving which variants in a significant gene/region carry the signal
<!-- END FILE: population-genetics/rare-variant-association/SKILL.md -->

## 子目录：population-genetics/scikit-allel-analysis

<!-- BEGIN FILE: population-genetics/scikit-allel-analysis/SKILL.md -->
---
name: bio-population-genetics-scikit-allel-analysis
description: In-memory Python population genetics with scikit-allel - GenotypeArray/HaplotypeArray/AlleleCountsArray, diversity (pi, theta, Tajima's D), SFS, FST (Weir-Cockerham, Hudson, Patterson), f3/D admixture stats, LD pruning, PCA, and selection scans (iHS, XP-EHH, nSL, Garud H). Nearly every statistic is a ratio or density with one silent denominator bug in two faces: omit is_accessible= and per-base pi/theta divide by total span not accessible bp (deflated 2-5x); average per-SNP FST instead of sum(a)/(sum(a)+sum(b)+sum(c)) and the estimate is rare-variant-biased - scikit-allel returns the (a,b,c) and (num,den) components on purpose to force ratio-of-sums. to_n_alt default fill=0 imputes missing to reference; sfs() is unfolded and wants derived not alt counts; iHS/XP-EHH need phased data and standardization. Use when computing population-genetics statistics in Python, scanning for selection, or building array pipelines. For PLINK QC see plink-basics; for VCF input see variant-calling/vcf-basics.
tool_type: python
primary_tool: scikit-allel
---

## Version Compatibility

Reference examples tested with: scikit-allel 1.3.13+, numpy 1.26+, zarr 2.18+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Version traps that change results, not just syntax: scikit-allel is in MAINTENANCE mode (latest line v1.3.x, e.g. v1.3.13 Sep 2024); the README names sgkit (xarray+dask) as the successor but states it is "not yet at feature parity", so scikit-allel remains the pragmatic choice for established stat workflows. `average_patterson_f3`/`average_patterson_d` are the current names; pre-2020 code used `blockwise_patterson_*` (gone). `to_n_alt()` default is `fill=0`, not `fill=-1`. `read_vcf` is eager and loads the whole file into RAM. The single source of truth for versions is this block, not headings.

# scikit-allel Analysis

**"Analyze population genetics in Python"** -> Read a VCF into array structures, then compute frequency-, diversity-, differentiation-, and haplotype-based statistics with correct denominators.
- Python: `allel.GenotypeArray`, `allel.AlleleCountsArray`, `allel.windowed_diversity(..., is_accessible=)`, `allel.average_hudson_fst`, `allel.pca`

Scope: in-memory and dask/zarr scikit-allel analysis - the array-API mechanics of the data model, diversity/SFS, FST and f/D admixture statistics, LD pruning, PCA, and selection-scan computation. PLINK-format QC routes to plink-basics; PCA/ADMIXTURE via CLI tools to population-structure; selection-scan DESIGN (standardization, outlier calling, demographic confounding) to selection-statistics; phased input to phasing-imputation/haplotype-phasing; VCF generation to variant-calling/vcf-basics.

## The Single Most Important Insight -- one denominator bug, two faces

1. Almost every statistic scikit-allel computes is a RATIO or a DENSITY, and the two ways the denominator is silently wrong both return a finite, plausible, unflagged number.
2. Face (a) - the per-base denominator: pi, Watterson's theta, and Dxy divide a segregating-site sum by the number of bases; omit `is_accessible=` and they divide by total span (`stop-start+1`) instead of callable bp, deflating values 2-5x AND distorting the genome-wide landscape because callability varies per window.
3. Face (b) - FST is a ratio of variance components: the correct multi-locus estimate is `sum(a)/(sum(a)+sum(b)+sum(c))`, NOT `mean(per_snp_fst)` (which is rare-variant-dominated and biased, Bhatia 2013); scikit-allel returns the `(a,b,c)` components from `weir_cockerham_fst` and `(num,den)` from `hudson_fst`/`patterson_fst` precisely to force ratio-of-sums.
4. Both bugs run silently with no exception or warning, so correctness is a design decision the analyst makes, not something the library enforces.

## Tool Taxonomy -- the data model and the scaling path

| Object / path | Shape / form | Role | When |
|---------------|--------------|------|------|
| `GenotypeArray` | `(n_variants, n_samples, ploidy)` int8, -1 = missing | the fundamental call array | diploid genotypes from `calldata/GT` |
| `HaplotypeArray` | `(n_variants, n_haplotypes)` | phased chromosomes | iHS/XP-EHH/nSL/Garud H (REQUIRE phasing) |
| `AlleleCountsArray` | `(n_variants, n_alleles)` int32 | currency of all frequency stats | `gt.count_alleles()`; ignores -1 |
| `to_n_alt` 012 matrix | `(n_variants, n_samples)` | input to PCA/LD | `gt.to_n_alt(fill=...)` (default fill=0 imputes to ref) |
| in-memory numpy | dense, all in RAM | fast, simple | fits-in-memory regions/chromosomes |
| `GenotypeDaskArray` + zarr | chunked, on-disk, lazy | out-of-core / parallel | biobank-scale; `vcf_to_zarr` once then dask |
| scikit-allel | maintenance mode, v1.3.x | established stat workflows | the pragmatic default today |
| sgkit | xarray+dask, active | successor, NOT yet feature-parity | greenfield biobank-scale infrastructure |

## Decision Tree by Scenario

| Scenario | Use | Why |
|----------|-----|-----|
| Per-base pi/theta/Dxy | `windowed_diversity(..., is_accessible=mask)` | without the mask the per-base denominator is total span, not callable bp |
| Genome-wide FST point estimate + SE | `average_hudson_fst(ac1, ac2, blen)` | ratio-of-sums + block-jackknife done correctly; Hudson is robust to unequal n (Bhatia 2013) |
| FST landscape across the genome | `moving_hudson_fst` / `windowed_weir_cockerham_fst` | per-window ratio aggregation, not `mean(per_snp_fst)` |
| SFS without a confident ancestral allele | `sfs_folded(ac)` | folds on minor-allele count; `sfs()` is unfolded and treats ALT as derived |
| Test if pop C is admixed | `average_patterson_f3(acc, aca, acb, blen)` | significantly negative f3 (z < ~-3) is the formal admixture test; C goes FIRST |
| LD-prune before PCA | `locate_unlinked(gn)` iterated ~3 rounds | one pass leaves residual LD; PCs otherwise track LD blocks/inversions |
| Selection scan on phased data | `ihs`/`nsl` then `standardize_by_allele_count` (DAF bins); `xpehh` then genome-wide `standardize` | raw scores are uninterpretable; the standardization differs by statistic |
| Whole-genome callset (tens of M SNPs) | `vcf_to_zarr` + `GenotypeDaskArray` | `read_vcf` is eager and OOMs; dask materializes per chunk |

## Reading Genotypes and Counting Alleles

**Goal:** Load a VCF region into a GenotypeArray and derive the allele-count currency, missing-aware.

**Approach:** Read only the needed fields (read_vcf is eager), wrap GT, count alleles per site (missing ignored), and get per-population counts in one pass with count_alleles_subpops.

```python
import allel
import numpy as np

callset = allel.read_vcf('data.vcf.gz', fields=['samples', 'calldata/GT', 'variants/POS', 'variants/CHROM'], region='2L:1-5000000')
gt = allel.GenotypeArray(callset['calldata/GT'])   # (n_variants, n_samples, 2); -1 = missing
pos = callset['variants/POS']

ac = gt.count_alleles()                            # ignores -1, so per-site allele number varies
subpops = {'pop1': [0, 1, 2, 3, 4], 'pop2': [5, 6, 7, 8, 9]}
ac_subpops = gt.count_alleles_subpops(subpops)     # one pass, consistent variant axis
ac1, ac2 = ac_subpops['pop1'], ac_subpops['pop2']
```

## Per-base Diversity with the Accessibility Mask

**Goal:** Compute pi and Watterson's theta as honest per-base quantities, not span-deflated ones.

**Approach:** Pass a boolean callability mask (one entry per base, from coverage/mappability, NOT from variant positions) as is_accessible; inspect the returned n_bases per window to confirm the denominator.

```python
# is_accessible: bool array over genomic positions (a callable-loci mask), NOT the VCF variant sites.
pi = allel.sequence_diversity(pos, ac, is_accessible=is_accessible)
theta_w = allel.watterson_theta(pos, ac, is_accessible=is_accessible)

# windowed_diversity returns 4 values; n_bases is the accessible-bp denominator PER window.
pi_w, windows, n_bases, counts = allel.windowed_diversity(pos, ac, size=100000, is_accessible=is_accessible)
# windowed_tajima_d returns 3 values (no n_bases): Tajima's D is dimensionless, no is_accessible.
D, td_windows, td_counts = allel.windowed_tajima_d(pos, ac, size=100000)
```

## FST as a Ratio of Sums

**Goal:** Get a genome-wide FST point estimate with a jackknife SE, and a per-window landscape, without the mean-of-ratios bias.

**Approach:** Let average_hudson_fst do the ratio-of-sums plus block-jackknife; if hand-aggregating, sum the components THEN divide; size blocks (blen) to exceed the LD scale.

```python
# Genome-wide estimate + standard error (ratio-of-sums + delete-one-block jackknife):
fst, se, vb, vj = allel.average_hudson_fst(ac1, ac2, blen=2000)   # blen must exceed the LD decay length

# Hand-aggregating Hudson correctly (NEVER mean of per-SNP fst):
num, den = allel.hudson_fst(ac1, ac2)
fst_manual = np.sum(num) / np.sum(den)

# Weir-Cockerham returns per-allele components (a, b, c); aggregate over BOTH axes:
a, b, c = allel.weir_cockerham_fst(gt, subpops=[[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
fst_wc = np.sum(a) / (np.sum(a) + np.sum(b) + np.sum(c))

# Landscape: per-window FST is already ratio-aggregated within each window.
fst_windows = allel.moving_hudson_fst(ac1, ac2, size=1000)
```

## Admixture: f3 and D (block-jackknifed)

**Goal:** Formally test whether a population is admixed (f3) or whether gene flow violates a tree (D / ABBA-BABA).

**Approach:** Call the average_* form for the jackknife z-score; put the test population FIRST in f3; treat a significantly negative f3 (z < ~-3) as admixture and |z| > ~3 for D as treeness violation.

```python
# f3(C; A, B): TEST population C is the FIRST argument. Returns (f3, se, z, vb, vj).
f3, se3, z3, vb3, vj3 = allel.average_patterson_f3(acc, aca, acb, blen=2000)
# Significantly negative f3 (z3 < ~-3) => C is admixed between A and B.

# D-statistic (ABBA-BABA): returns (d, se, z, vb, vj). |z| > ~3 flags gene flow.
d, sed, zd, vbd, vjd = allel.average_patterson_d(aca, acb, acc, acd, blen=2000)
```

## LD Pruning and PCA

**Goal:** Project samples onto ancestry axes that reflect drift, not LD blocks or inversions.

**Approach:** Convert to a missing-free 012 matrix, LD-prune iteratively with locate_unlinked, mask known inversions by position, then run Patterson-scaled PCA (randomized at scale).

```python
gn = gt.to_n_alt(fill=-1)                          # default fill=0 imputes missing to REF; use -1 then handle
gn = np.where(gn < 0, 0, gn)                        # impute-to-reference is a deliberate choice here

# Iterate LD pruning ~3 rounds; one pass leaves residual LD. Returns a KEEP mask (True = unlinked).
for _ in range(3):
    keep = allel.locate_unlinked(gn, size=100, step=20, threshold=0.1)
    gn = gn[keep]

coords, model = allel.randomized_pca(gn, n_components=10, scaler='patterson', random_state=0)
explained = model.explained_variance_ratio_        # scree; coords is (n_samples, n_components)
```

## Selection Scans on Phased Haplotypes

**Goal:** Score the genome for recent selection from haplotype structure.

**Approach:** Reshape phased genotypes to a HaplotypeArray, compute the raw scan, then standardize - iHS/nSL binned by derived-allele frequency (`standardize_by_allele_count`), XP-EHH genome-wide (`standardize`); the raw scores are not directly interpretable.

```python
h = gt.to_haplotypes()                              # VALID only if data are PHASED
ihs_raw = allel.ihs(h, pos, min_maf=0.05)           # unstandardized
ihs_std, bins = allel.standardize_by_allele_count(ihs_raw, ac[:, 1])   # bin by DERIVED count; ac[:,1] is derived only if REF is ancestral (polarize first); |z| > 2 flags candidates
h1, h12, h123, h2_h1 = allel.garud_h(h)             # soft-vs-hard-sweep haplotype-homozygosity stats
```

## Per-Function Failure Modes

### sequence_diversity / watterson_theta without is_accessible
**Trigger:** calling per-base diversity with no callability mask. **Mechanism:** divides the numerator by `stop-start+1` (total span) instead of callable bp. **Symptom:** pi/theta deflated 2-5x and the genome-wide landscape distorted because callability varies per window. **Fix:** pass `is_accessible=` from a coverage/mappability callable-loci mask and inspect the returned `n_bases`.

### mean(per_snp_fst) instead of ratio-of-sums
**Trigger:** averaging per-SNP `a/(a+b+c)` for the genome-wide FST. **Mechanism:** mean-of-ratios is dominated by low-frequency SNPs with tiny noisy denominators. **Symptom:** a biased FST that differs from published estimates of the same comparison (Bhatia 2013). **Fix:** `sum(a)/(sum(a)+sum(b)+sum(c))`, or `average_hudson_fst`/`average_weir_cockerham_fst` which do it plus a jackknife SE.

### to_n_alt default fill=0
**Trigger:** `gt.to_n_alt()` with no `fill`. **Mechanism:** missing calls become 0 alt alleles = homozygous reference. **Symptom:** PCA/LD silently biased toward the reference allele. **Fix:** `to_n_alt(fill=-1)` then impute deliberately, or pre-filter for high call rate; state the imputation choice.

### sfs() fed alt counts and run unfolded
**Trigger:** `allel.sfs(ac[:, 1])` without a confident ancestral allele. **Mechanism:** `sfs()` is unfolded and treats the ALT count as the DERIVED count; ALT != DERIVED. **Symptom:** mis-polarized spectrum biasing demographic/DFE inference. **Fix:** use `sfs_folded(ac)` when polarization is uncertain; use `sfs(dac)` only with a verified ancestral allele.

### iHS/XP-EHH/nSL on unphased or unstandardized data
**Trigger:** running selection scans on unphased genotypes or reporting raw scores. **Mechanism:** these stats need phased haplotype structure, and raw output is on an unstandardized scale. **Symptom:** meaningless scans; un-binned scores not comparable across the genome. **Fix:** require PHASED input and standardize - `standardize_by_allele_count` (DAF bins) for iHS/nSL, genome-wide `standardize` for XP-EHH.

### blen smaller than the LD scale
**Trigger:** a small `blen` in any `average_*` FST or `average_patterson_f3/_d`. **Mechanism:** blocks within an LD region are correlated, so the delete-one-block jackknife under-estimates the SE. **Symptom:** spurious-significant f3 admixture / D-statistics. **Fix:** size `blen` to exceed the LD decay length (multi-Mb / >~1 cM for humans).

### read_vcf on a whole-genome callset
**Trigger:** `allel.read_vcf('genome.vcf.gz')` with no region/fields limits. **Mechanism:** read_vcf is eager and materializes the entire file in RAM. **Symptom:** out-of-memory crash on biobank-scale data. **Fix:** `vcf_to_zarr` once, then `GenotypeDaskArray` for out-of-core counting/filtering; limit `read_vcf(fields=, region=)`.

## Quantitative / correctness notes

| Item | Value / rule | Rationale |
|------|--------------|-----------|
| Accessibility deflation | multiplicative AND per-window | a 40%-accessible window deflates pi ~2.5x, a 90% one ~1.1x - the relative landscape is wrong |
| FST estimator default | Hudson for unequal n / rare variants | Bhatia 2013 recommends the ratio estimator robust to sample-size imbalance |
| Jackknife block size | `blen` > LD decay length | too-small blocks are correlated -> anticonservative SE -> false significance |
| f3 admixture | z < ~-3 (negative) | a significantly negative f3(C; A, B) is the formal admixture test for C |
| D / ABBA-BABA | \|z\| > ~3 | conventional treeness-violation / gene-flow threshold |
| iHS/XP-EHH/nSL | standardized \|z\| > 2, in CLUSTERS | sweeps show clusters of extreme binned z-scores, not isolated SNPs |
| LD pruning rounds | ~3 iterations of `locate_unlinked` | one pass leaves residual LD; expect to discard most SNPs |
| PCA scaler | `'patterson'` (default) | centers then divides each SNP by sqrt(p(1-p)); equal expected variance under drift |

Thresholds are conventions, not laws - inspect distributions and verify current best practice before applying numbers blindly.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| pi/theta look 2-5x too small | `is_accessible=` omitted | pass a callable-loci mask; check the returned `n_bases` |
| FST disagrees with published value | `mean(per_snp_fst)` aggregation | `sum(num)/sum(den)` or `average_hudson_fst(ac1, ac2, blen)` |
| `hudson_fst`/`patterson_fst` "FST" out of range | treating the first return as FST | they return `(num, den)`; aggregate `np.sum(num)/np.sum(den)` |
| `ValueError` unpacking `windowed_tajima_d` | expecting 4 values | it returns 3 `(D, windows, counts)`; `windowed_diversity` returns 4 |
| PCA skewed toward reference allele | `to_n_alt()` default `fill=0` | `to_n_alt(fill=-1)` then impute deliberately, or pre-filter |
| `pca` raises on -1/NaN | missing values in the 012 matrix | impute or filter; the patterson scaler cannot handle missing |
| f3 admixture test makes no sense | wrong argument order | `average_patterson_f3(acc, aca, acb, blen)` - test pop C is FIRST |
| `blockwise_patterson_f3` AttributeError | old name | use `average_patterson_f3` / `average_patterson_d` |
| raw iHS values uninterpretable | not standardized | `standardize_by_allele_count(score, aac)` binned by DAF |
| MemoryError on `read_vcf` | eager whole-genome read | `vcf_to_zarr` + `GenotypeDaskArray`; limit `fields=`/`region=` |

## References

1. Miles A, Harding N, et al. scikit-allel: explore and analyse genetic variation. Zenodo; cite-all-versions DOI:10.5281/zenodo.597309. Docs: scikit-allel.readthedocs.io; successor sgkit: github.com/sgkit-dev/sgkit.
2. Weir BS, Cockerham CC. Estimating F-statistics for the analysis of population structure. Evolution 1984; 38(6):1358-1370. DOI:10.1111/j.1558-5646.1984.tb05657.x.
3. Hudson RR, Slatkin M, Maddison WP. Estimation of levels of gene flow from DNA sequence data. Genetics 1992; 132(2):583-589. PMID:1427045.
4. Bhatia G, Patterson N, Sankararaman S, Price AL. Estimating and interpreting FST: the impact of rare variants. Genome Research 2013; 23(9):1514-1521. PMID:23861382.
5. Patterson N, Moorjani P, Luo Y, Mallick S, Rohland N, Zhan Y, Genschoreck T, Webster T, Reich D. Ancient admixture in human history. Genetics 2012; 192(3):1065-1093. DOI:10.1534/genetics.112.145037.
6. Patterson N, Price AL, Reich D. Population structure and eigenanalysis. PLoS Genetics 2006; 2(12):e190. DOI:10.1371/journal.pgen.0020190.
7. Tajima F. Statistical method for testing the neutral mutation hypothesis by DNA polymorphism. Genetics 1989; 123(3):585-595. PMID:2513255.
8. Voight BF, Kudaravalli S, Wen X, Pritchard JK. A map of recent positive selection in the human genome. PLoS Biology 2006; 4(3):e72. DOI:10.1371/journal.pbio.0040072.
9. Sabeti PC, et al. Genome-wide detection and characterization of positive selection in human populations. Nature 2007; 449:913-918. DOI:10.1038/nature06250.
10. Ferrer-Admetlla A, Liang M, Korneliussen T, Nielsen R. On detecting incomplete soft or hard selective sweeps using haplotype structure. Molecular Biology and Evolution 2014; 31(5):1275-1291. DOI:10.1093/molbev/msu077.
11. Garud NR, Messer PW, Buzbas EO, Petrov DA. Recent selective sweeps in North American Drosophila melanogaster show signatures of soft sweeps. PLoS Genetics 2015; 11(2):e1005004. DOI:10.1371/journal.pgen.1005004.

## Related Skills

- selection-statistics - selection-scan design, standardization, and demography-aware outlier interpretation (this skill owns the array mechanics)
- population-structure - PCA and ADMIXTURE via PLINK2/FlashPCA2
- linkage-disequilibrium - LD pruning and clumping
- plink-basics - PLINK-format QC before array-based analysis
- variant-calling/vcf-basics - VCF generation and manipulation before loading
- phasing-imputation/haplotype-phasing - phased haplotypes required for iHS/XP-EHH/nSL
<!-- END FILE: population-genetics/scikit-allel-analysis/SKILL.md -->

## 子目录：population-genetics/selection-statistics

<!-- BEGIN FILE: population-genetics/selection-statistics/SKILL.md -->
---
name: bio-population-genetics-selection-statistics
description: Scans genomes for natural selection with SFS tests (Tajima's D, Fay & Wu H, Zeng E, SweepFinder2 CLR), haplotype tests (iHS, nSL, XP-EHH, Rsb, H12), and differentiation (FST, PBS) using scikit-allel, selscan, and SweepFinder2. No single statistic separates selection from demography at one locus, so the deliverable is empirical genome-wide outliers plus multiple orthogonal signals, not an absolute cutoff. iHS detects incomplete sweeps and collapses to zero at fixation while XP-EHH catches fixed sweeps; iHS/nSL standardize within derived-allele-frequency bins but XP-EHH gets a genome-wide z-score; derived-allele tests need substitution-model polarization; background selection mimics FST and CLR. Use when computing selection statistics like FST, Tajima's D, iHS, or XP-EHH, or scanning for selective sweeps. For phasing inputs see phasing-imputation/haplotype-phasing; for dN/dS see comparative-genomics/positive-selection.
tool_type: mixed
primary_tool: scikit-allel
---

## Version Compatibility

Reference examples tested with: scikit-allel 1.3+, numpy 1.26+, selscan 2.0+, SweepFinder2 1.0+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Version traps that change results, not just syntax: `allel.standardize_by_allele_count(score, aac, ...)` is for iHS and nSL (it bins by derived-allele count), while XP-EHH and iHH12 use plain genome-wide `allel.standardize(score)`; conflating them is a real bug. `allel.nsl(h)` takes no `pos`/`map_pos` (nSL is map-free by construction) whereas `allel.ihs(h, pos, map_pos=...)` distorts without a genetic map. selscan 2.0 adds `--unphased` for multilocus genotypes; selscan 1.x requires phased haplotypes. The single source of truth for versions is this block, not headings.

# Selection Statistics

**"Scan my population for signatures of natural selection"** -> Contrast each locus against the genome-wide neutral expectation that already carries the demographic history, using statistics that read complementary features of a sweep.
- Python: `allel.ihs()`, `allel.xpehh()`, `allel.nsl()`, `allel.garud_h()`, `allel.windowed_tajima_d()`, `allel.hudson_fst()` (scikit-allel)
- CLI: `selscan --ihs|--xpehh|--nsl` then `norm` for standardization; `SweepFinder2 -lrb` for CLR with a background-selection map

Scope: selection-scan DESIGN - SFS neutrality tests, haplotype/EHH sweep statistics, differentiation outliers (FST, PBS), CLR scans, and polygenic Qx, with standardization and demography-aware outlier interpretation. PCA/ADMIXTURE population assignment routes to population-structure; LD/EHH mechanics to linkage-disequilibrium; the scikit-allel array-API mechanics (signatures, accessibility masks, data loading) to scikit-allel-analysis; phasing to phasing-imputation/haplotype-phasing; dN/dS and McDonald-Kreitman to comparative-genomics/positive-selection.

## The Single Most Important Insight -- no single statistic separates selection from demography at one locus

1. A bottleneck removes variation genome-wide and skews the SFS toward rare variants exactly as a sweep does, so a single Tajima's D cannot tell them apart; recent expansion gives genome-wide negative D that mimics a post-sweep signal, and population structure gives positive D that mimics balancing selection.
2. The field's response is structural, not statistical: rank windows and flag empirical genome-wide OUTLIERS (the bulk absorbs the shared demography), intersect MULTIPLE ORTHOGONAL signals (a sweep distorts haplotype, SFS, diversity, and differentiation together while each confound acts differently), and calibrate against an explicit demographic-model SIMULATION (dadi/momi/fastsimcoal2 + msprime/SLiM).
3. iHS and nSL detect INCOMPLETE/ongoing sweeps and collapse to ~0 once the allele fixes; XP-EHH and Rsb catch FIXED/near-fixed sweeps by borrowing a second population, so they are COMPLEMENTARY not redundant (high XP-EHH with near-zero iHS is the textbook completed-sweep signature).
4. An absolute cutoff such as "Tajima's D < -2 means a sweep" is wrong by construction; -2 means nothing without the genome-wide context, which is why the entire skill is outlier-based.

## Tool Taxonomy

| Family | Statistic / tool | Citation | Reads / role | Phasing |
|--------|------------------|----------|--------------|---------|
| SFS | Tajima's D (`allel.tajima_d`) | Tajima 1989 | theta_pi - theta_W; rare-vs-intermediate variant skew | no |
| SFS | Fay & Wu H, Zeng E | Fay & Wu 2000; Zeng 2006 | high-frequency-DERIVED excess; needs polarization | no |
| SFS-CLR | SweepFinder2 (`-f/-l/-lr/-lrb`) | DeGiorgio 2016 | local SFS vs empirical background; localizes target; `-lrb` deconfounds BGS | no |
| SFS-CLR | SweeD, OmegaPlus | Pavlidis 2013; Alachiotis 2012 | parallel CLR; LD-shoulder omega | no |
| Haplotype | iHS (`allel.ihs`, selscan `--ihs`) | Voight 2006 | INCOMPLETE sweeps; standardize by DAF bin | YES |
| Haplotype | nSL (`allel.nsl`, selscan `--nsl`) | Ferrer-Admetlla 2014 | incomplete hard+soft; map-free | YES |
| Haplotype | XP-EHH (`allel.xpehh`, selscan `--xpehh`) | Sabeti 2007 | FIXED/near-fixed sweeps; genome-wide z-score | YES |
| Haplotype | Rsb | Tang 2007 | XP-EHH niche; iES ratio | YES |
| Haplotype | H12 / H2H1 (`allel.garud_h`) | Garud 2015 | SOFT sweeps; hard-vs-soft tendency | YES |
| Differentiation | FST (`allel.hudson_fst`, `allel.weir_cockerham_fst`) | Weir & Cockerham 1984; Bhatia 2013 | local-adaptation divergence | no |
| Differentiation | PBS | Yi 2010 | which branch the divergence is on (3 pops) | no |
| Polygenic | Qx | Berg & Coop 2014 | over-dispersed polygenic scores across pops | no |

## Decision Tree by Scenario

| Scenario | Use | Why |
|----------|-----|-----|
| Localized recent sweep, ongoing/incomplete, one population, genetic map available | iHS | reads the frequency contrast between long derived and short ancestral haplotypes |
| Same but no reliable genetic map | nSL | integrates over segregating-site count; map-free, robust to recombination-rate variation |
| Sweep complete/fixed in one of two populations | XP-EHH or Rsb | maximum power exactly where iHS is blind (no within-population contrast remains) |
| Selection on standing variation (soft sweep) | H12 / H2H1 | collapses co-rising haplotypes; hard-sweep stats lose power |
| Localize the target with a demographic/BGS model | SweepFinder2 CLR (`-lrb`) or SweeD; OmegaPlus | empirical background SFS as null; B-value map deconfounds background selection |
| Differentiation outliers, unequal sample sizes | FST Hudson estimator + PBS for 3 pops | Hudson is robust to unequal n; PBS localizes the branch |
| Quick SFS reconnaissance | windowed Tajima's D + pi + Fay & Wu H (substitution-model polarization) | cheap, but never an absolute cutoff |
| Polygenic trait shift across populations | Qx with within-family GWAS effect sizes only | sweep scans are blind to coordinated tiny shifts; standard GWAS betas carry stratification bias |
| Ancient/recurrent coding selection across species | hand off to comparative-genomics/positive-selection | dN/dS and MK are a different timescale, not a within-population sweep |

## FST and PBS - Differentiation

**Goal:** Quantify allele-frequency divergence between populations and flag local-adaptation candidates without being fooled by rare variants or unequal samples.

**Approach:** Count alleles per subpopulation, compute the Hudson estimator per SNP, and report mean FST as a ratio-of-averages over windows after an MAF filter (rare variants deflate FST, Bhatia 2013).

```python
import allel
import numpy as np

callset = allel.read_vcf('data.vcf.gz')
gt = allel.GenotypeArray(callset['calldata/GT'])
pos = callset['variants/POS']

subpops = {'pop1': [0, 1, 2, 3, 4], 'pop2': [5, 6, 7, 8, 9]}
ac_subpops = gt.count_alleles_subpops(subpops)
ac1, ac2 = ac_subpops['pop1'], ac_subpops['pop2']

# MAF filter first: rare variants systematically deflate FST (Bhatia 2013).
maf = np.minimum(ac1.to_frequencies()[:, 1], ac2.to_frequencies()[:, 1])
keep = (maf > 0.05) | (1 - maf > 0.05)

# Hudson estimator: robust to unequal sample sizes. Mean FST = ratio-of-averages, never mean of per-SNP ratios.
num, den = allel.hudson_fst(ac1[keep], ac2[keep])
fst_mean = np.nansum(num) / np.nansum(den)

# Windowed scan for outlier localization.
fst_win, windows, n_snps = allel.windowed_hudson_fst(pos[keep], ac1[keep], ac2[keep], size=100000, step=50000)
outlier = fst_win > np.nanpercentile(fst_win, 99)
```

PBS (Population Branch Statistic, Yi 2010) needs three populations: convert three pairwise FST values to branch lengths via T = -log(1 - FST) and isolate the focal branch as PBS = (T_12 + T_13 - T_23) / 2. A long focal branch in a small/bottlenecked population can be drift, not selection.

## iHS and nSL - Within-Population Incomplete Sweeps

**Goal:** Detect ongoing sweeps from extended haplotype homozygosity around derived core alleles.

**Approach:** Filter to segregating biallelic SNPs, compute the raw integrated-EHH score, then standardize WITHIN derived-allele-frequency bins (the raw score depends strongly on derived frequency and is uninterpretable unbinned).

```python
import allel
import numpy as np

h = gt.to_haplotypes()
ac = h.count_alleles()
flt = (ac[:, 0] > 1) & (ac[:, 1] > 1)
h_flt, pos_flt, ac_flt = h.compress(flt, axis=0), pos[flt], ac.compress(flt, axis=0)

# iHS needs a genetic map (map_pos) where recombination rate varies; physical distance distorts iHH.
ihs_raw = allel.ihs(h_flt, pos_flt, min_maf=0.05, include_edges=True)
# Standardize WITHIN derived-allele-count bins (NOT genome-wide) - the most common iHS bug.
ihs_std, _ = allel.standardize_by_allele_count(ihs_raw, ac_flt[:, 1])
ihs_outlier = np.abs(ihs_std) > 2

# nSL: map-free (no pos/map_pos), robust to recombination-rate variation; still bin-standardized.
nsl_raw = allel.nsl(h_flt)
nsl_std, _ = allel.standardize_by_allele_count(nsl_raw, ac_flt[:, 1])
```

A null iHS does NOT mean no selection: once the derived allele fixes, the ancestral haplotype is gone and iHS collapses to zero. Switch to XP-EHH/Rsb for completed sweeps. Report the windowed PROPORTION of |iHS|>2 SNPs, not single noisy hits.

## XP-EHH - Cross-Population Completed Sweeps

**Goal:** Catch fixed or near-fixed sweeps in one of two populations, where within-population haplotype tests are blind.

**Approach:** Compute the cross-population integrated-EHH ratio on shared positions, then apply a plain GENOME-WIDE z-score (XP-EHH is not strongly correlated with derived frequency, so frequency-bin standardization is the wrong rule).

```python
import allel
import numpy as np

h1 = h_flt.take(pop1_hap_idx, axis=1)
h2 = h_flt.take(pop2_hap_idx, axis=1)

xpehh_raw = allel.xpehh(h1, h2, pos_flt, include_edges=True)
# Genome-wide z-score for XP-EHH/iHH12 - NOT standardize_by_allele_count (that is for iHS/nSL).
xpehh_std = allel.standardize(xpehh_raw)
completed_sweep = np.abs(xpehh_std) > 2
```

A shared ancestral sweep at the same locus in BOTH populations cancels in the contrast (false negative). Differential phasing quality between the two populations systematically biases the difference statistic.

## H12 - Soft Sweeps

**Goal:** Recover sweeps on standing variation that iHS and CLR miss because no single long haplotype dominates.

**Approach:** Compute Garud's H over haplotype-frequency spectra; H12 collapses the two most common haplotypes into one, and H2/H1 tends (not classifies) toward hard-vs-soft.

```python
h1, h12, h123, h2_h1 = allel.garud_h(h_flt)
h12_win = allel.moving_garud_h(h_flt, size=100)  # SNP-count windows, not bp
```

## SFS-CLR with selscan and SweepFinder2

```bash
# selscan haplotype scans (phased VCF + genetic map), then norm for standardization.
selscan --ihs --vcf phased.vcf --map genetic.map --out scan        # within-pop incomplete sweeps
selscan --xpehh --vcf pop1.vcf --vcf-ref pop2.vcf --map genetic.map --out xp  # completed sweeps
selscan --nsl --vcf phased.vcf --out nsl_scan                       # no map; map-free
selscan --ihs --unphased --vcf unphased.vcf --map genetic.map --out scan_unphased  # selscan 2.0 multilocus-genotype

# norm bins iHS/nSL by derived-allele frequency (--bins default 100); XP-EHH/iHH12 get a genome-wide z-score.
norm --ihs --files scan.ihs.out --bins 100
norm --xpehh --files xp.xpehh.out

# SweepFinder2 CLR: build a genome-WIDE background SFS, then scan with recombination + B-value (BGS) map.
SweepFinder2 -f genome.freq genome.spect                            # empirical background spectrum
# -lrb takes N1 (current ingroup Ne), N2 (ancestral Ne), T (divergence time in generations) before OutFile.
SweepFinder2 -lrb 2000 region.freq genome.spect region.rec bvalue.map "$N1" "$N2" "$T" out.clr  # G=2000 grid; -lrb deconfounds BGS
```

## Polarization and Polygenic Selection

Derived-allele tests (Fay & Wu H, Zeng E, unfolded SFS, the iHS sign) are POLARIZATION traps: one mispolarized CpG site masquerades as a high-frequency-derived variant and fakes a strongly negative H. Polarize with a probabilistic substitution model and two or more outgroups (Hernandez 2007), never a single chimp allele. Conservation scores (phyloP, GERP, phastCons) measure CONSTRAINT (purifying selection), the opposite sign of a recent positive sweep, and must not be read as "under selection." Polygenic Qx (Berg & Coop 2014) inherits every stratification bias in the GWAS effect sizes it uses: the celebrated European height-selection signal was shown to be a stratification artifact (Sohail 2019; Berg 2019), so use within-family/sibling effect estimates and treat standard-GWAS-beta Qx as provisional.

## Per-Method Failure Modes

### Absolute Tajima's D cutoff
**Trigger:** flagging windows on |D|>2 as selection. **Mechanism:** growth/bottleneck/structure produce the same sign as a sweep/balancing selection (non-identifiable at one locus). **Symptom:** genome-wide false positives that are pure demography. **Fix:** use the genome-wide empirical distribution and intersect orthogonal statistics; report D relative to the genomic background.

### Unstandardized or mis-standardized iHS
**Trigger:** reporting raw iHS, or applying a genome-wide z-score to iHS. **Mechanism:** raw iHH ratio depends strongly on derived-allele frequency. **Symptom:** uninterpretable scores, false tails at particular frequencies. **Fix:** `standardize_by_allele_count` (DAF bins) for iHS/nSL; reserve `standardize` (genome-wide) for XP-EHH/iHH12.

### iHS null read as no-selection
**Trigger:** concluding neutrality from absent iHS signal. **Mechanism:** a completed sweep fixes the derived allele, erasing the within-population contrast iHS needs. **Symptom:** real fixed sweeps missed. **Fix:** add XP-EHH/Rsb against a second population for completed sweeps.

### Single-outgroup polarization
**Trigger:** deriving ancestral state from one chimp allele for H/E/unfolded SFS. **Mechanism:** recurrent mutation at CpG/hypermutable sites biases the single-allele ancestral estimator. **Symptom:** spurious strongly-negative Fay & Wu H (fake sweep). **Fix:** substitution-model polarization with >=2 outgroups (Hernandez 2007; est-sfs).

### Background selection as sweep
**Trigger:** reading an FST or CLR peak in a low-recombination region as positive selection. **Mechanism:** purifying selection against linked deleterious variants reduces local diversity. **Symptom:** FST/PBS/CLR peaks with no positive selection. **Fix:** supply SweepFinder2 a B-value map (`-lrb`); control for recombination rate; treat low-recombination outliers with suspicion.

### Switch error in haplotype stats
**Trigger:** EHH statistics on poorly phased data. **Mechanism:** a switch error truncates long haplotypes and deflates EHH. **Symptom:** iHS/nSL/XP-EHH biased toward null; XP-EHH biased by differential phasing between populations. **Fix:** read-backed/high-quality phasing (see phasing-imputation/haplotype-phasing), or selscan 2.0 `--unphased` multilocus-genotype mode.

### Polygenic Qx on stratified GWAS betas
**Trigger:** running Qx on standard meta-analysis effect sizes. **Mechanism:** residual population stratification correlates effect sizes with ancestry axes. **Symptom:** spurious polygenic-adaptation clines (the height story). **Fix:** within-family/sibling effect sizes; treat PC-corrected meta-analysis betas as insufficient.

## Quantitative Thresholds

| Quantity | Typical value | Rationale |
|----------|---------------|-----------|
| iHS / nSL flag | \|standardized score\| > 2 | ~top 2.5% two-sided of N(0,1); an empirical convention, NOT a calibrated p-value (Voight 2006) |
| Empirical outlier tail | top 1% (top 0.1% for stringency) | genome-wide bulk absorbs demography; percentile is a sensitivity/specificity tradeoff, not an alpha |
| iHS/nSL standardization | within derived-allele-frequency bins (selscan `--bins 100`) | raw score is frequency-dependent; binning makes scores comparable |
| XP-EHH/iHH12 standardization | genome-wide z-score | not frequency-correlated; bin-standardizing inverts the rule |
| Window size | 10-100 kb, 50% step (scale to LD decay) | wide enough for stable SFS estimates, narrow enough to localize |
| Haplotype-stat MAF | drop core alleles MAF < ~0.05 | EHH on singletons is undefined/uninformative (`min_maf=0.05`) |
| SweepFinder2 grid G | finer than expected sweep width (~1-2 kb in humans) | coarse grids step over narrow sweeps; significance from demographic-model simulation |
| FST mean | ratio-of-averages, MAF-filtered, Hudson estimator | rare variants deflate FST; arithmetic mean of per-SNP ratios is biased (Bhatia 2013) |

Thresholds are conventions, not laws - inspect distributions and calibrate against a demographic-model simulation or the genome-wide empirical tail before quoting any number.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "D < -2 = sweep" | absolute cutoff ignoring demography | use the genome-wide empirical tail; D sign never identifies cause |
| iHS scores incomparable across SNPs | unstandardized or genome-wide-standardized iHS | `standardize_by_allele_count` by DAF bin |
| XP-EHH never standardized | applying the iHS rule or no standardization | `allel.standardize(xpehh)` genome-wide z-score |
| "no iHS so no selection" | completed sweep has no within-pop contrast | add XP-EHH/Rsb against a second population |
| spurious negative Fay & Wu H | single-outgroup polarization at CpG sites | substitution-model polarization, >=2 outgroups (Hernandez 2007) |
| FST/CLR peak misread as positive selection | background selection in low-recombination region | B-value map (`-lrb`); recombination control |
| `allel.nsl(h, pos)` TypeError | nSL is map-free; takes no pos/map_pos | call `allel.nsl(h)` |
| FST tail driven by rare variants | no MAF filter; mean of per-SNP ratios | MAF filter + Hudson ratio-of-averages |
| Qx height-style false signal | stratified GWAS effect sizes | within-family/sibling effect estimates |
| "high phyloP = under selection" | conflating constraint with positive selection | phyloP/GERP measure purifying constraint (opposite sign) |

## References

1. Tajima F. Statistical method for testing the neutral mutation hypothesis by DNA polymorphism. Genetics 1989; 123(3):585-595.
2. Fay JC, Wu CI. Hitchhiking under positive Darwinian selection. Genetics 2000; 155(3):1405-1413.
3. Zeng K, Fu YX, Shi S, Wu CI. Statistical tests for detecting positive selection by utilizing high-frequency variants. Genetics 2006; 174(3):1431-1439.
4. DeGiorgio M, Huber CD, Hubisz MJ, Hellmann I, Nielsen R. SweepFinder2: increased sensitivity, robustness and flexibility. Bioinformatics 2016; 32(12):1895-1897.
5. Voight BF, Kudaravalli S, Wen X, Pritchard JK. A map of recent positive selection in the human genome. PLoS Biology 2006; 4(3):e72.
6. Sabeti PC, Varilly P, Fry B, et al. Genome-wide detection and characterization of positive selection in human populations. Nature 2007; 449(7164):913-918.
7. Ferrer-Admetlla A, Liang M, Korneliussen T, Nielsen R. On detecting incomplete soft or hard selective sweeps using haplotype structure. Molecular Biology and Evolution 2014; 31(5):1275-1291.
8. Garud NR, Messer PW, Buzbas EO, Petrov DA. Recent selective sweeps in North American Drosophila melanogaster show signatures of soft sweeps. PLoS Genetics 2015; 11(2):e1005004.
9. Yi X, Liang Y, Huerta-Sanchez E, et al. Sequencing of 50 human exomes reveals adaptation to high altitude. Science 2010; 329(5987):75-78.
10. Weir BS, Cockerham CC. Estimating F-statistics for the analysis of population structure. Evolution 1984; 38(6):1358-1370.
11. Bhatia G, Patterson N, Sankararaman S, Price AL. Estimating and interpreting FST: the impact of rare variants. Genome Research 2013; 23(9):1514-1521.
12. Hernandez RD, Williamson SH, Bustamante CD. Context dependence, ancestral misidentification, and spurious signatures of natural selection. Molecular Biology and Evolution 2007; 24(8):1792-1800.
13. Berg JJ, Coop G. A population genetic signal of polygenic adaptation. PLoS Genetics 2014; 10(8):e1004412.
14. Sohail M, Maier RM, Ganna A, et al. Polygenic adaptation on height is overestimated due to uncorrected stratification in genome-wide association studies. eLife 2019; 8:e39702.
15. Berg JJ, Harpak A, Sinnott-Armstrong N, et al. Reduced signal for polygenic adaptation of height in UK Biobank. eLife 2019; 8:e39725.

## Related Skills

- scikit-allel-analysis - genotype/haplotype array loading and allele-count basics
- population-structure - PCA and ADMIXTURE for population assignment before FST/PBS
- linkage-disequilibrium - EHH and LD mechanics underlying haplotype statistics
- phasing-imputation/haplotype-phasing - phased haplotypes that all EHH statistics require
- comparative-genomics/positive-selection - dN/dS and McDonald-Kreitman for recurrent coding selection
- comparative-genomics/introgression-detection - archaic/admixture signals that confound differentiation outliers
<!-- END FILE: population-genetics/selection-statistics/SKILL.md -->

<!-- END CATEGORY: population-genetics -->

