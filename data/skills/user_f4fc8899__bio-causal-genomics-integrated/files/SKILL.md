---
slug: bio-causal-genomics-integrated
version: 1.0.1
displayName: "因果基因组学 / Causal genomics"
name: bio-causal-genomics-integrated
summary: "中文：因果基因组学综合技能，整合 11 个相关专题，覆盖因果基因组学：孟德尔随机化、共定位、精细定位、TWAS、遗传力分区、GenomicSEM。 English: Integrated Causal genomics skill covering 11 related topics, including Causal genomics: Mendelian randomization, colocalization, fine-mapping, TWAS, heritability partitioning, GenomicSEM."
description: "中文：这是一个面向因果基因组学的综合生物信息学 Skill，整合当前分类下 11 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：因果基因组学：孟德尔随机化、共定位、精细定位、TWAS、遗传力分区、GenomicSEM。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：FUSION, GenomicSEM, MAGMA。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Causal genomics, combining 11 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Causal genomics: Mendelian randomization, colocalization, fine-mapping, TWAS, heritability partitioning, GenomicSEM. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: FUSION, GenomicSEM, MAGMA. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# causal-genomics 分类 Skill 整合版

> 本文件整合同一主分类目录下 11 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: causal-genomics -->

## 子目录：causal-genomics/colocalization-analysis

<!-- BEGIN FILE: causal-genomics/colocalization-analysis/SKILL.md -->
---
name: bio-causal-genomics-colocalization-analysis
description: Test whether two or more traits share a causal variant at a locus using Bayesian colocalization (coloc.abf, coloc.susie, HyPrColoc, moloc, eCAVIAR, SMR/HEIDI, PWCoCo, SharePro). Use when integrating GWAS with eQTL/sQTL/pQTL/mQTL, distinguishing shared causal variants from LD-driven coincidence, handling allelic heterogeneity, choosing between single-causal vs multi-causal methods, picking PP.H4 thresholds, running sensitivity over p12, or harmonising summary statistics for colocalization.
tool_type: r
primary_tool: coloc
---

## Version Compatibility

Reference examples tested with: coloc 5.2.3+, susieR 0.12.35+, hyprcoloc 1.0+ (GitHub jrs95/hyprcoloc), SMR 1.3.1+ (CLI, cnsgenomics.com), eCAVIAR 2.2+ (compiled from caviar/eCAVIAR repo), PWCoCo 1.0+ (jwr-git/pwcoco), moloc 0.1+ (clagiamba/moloc), SharePro_coloc 7.0+ (zhwm/SharePro_coloc), R >= 4.1.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('coloc')`; check `?coloc.abf`, `?coloc.susie`, `?runsusie`
- CLI: `smr --version`, `pwcoco --help`, `sharepro_coloc.py --help`

If code throws AttributeError, NULL list elements, or `Error in coloc.abf: dataset must have...`, introspect the installed package signature and adapt the example rather than retrying.

# Colocalization Analysis

**"Test whether my GWAS signal and an eQTL share the same causal variant"** -> Compute Bayesian posterior probabilities over five hypotheses (H0 neither, H1 trait-1-only, H2 trait-2-only, H3 distinct causal variants, H4 shared causal variant) to discriminate true causal overlap from LD-driven coincidence, then run sensitivity analysis over the p12 prior.

- R (single-causal, fastest): `coloc::coloc.abf(dataset1, dataset2, p12=5e-6)` -> `coloc::sensitivity(res, 'H4 > 0.75')`
- R (multi-causal, needs LD): `runsusie(d1)` -> `runsusie(d2)` -> `coloc.susie(s1, s2)` -> per-credible-set PP
- R (many traits, single-causal cluster): `hyprcoloc::hyprcoloc(effect.est = betas_mat, effect.se = ses_mat, trait.names = ..., snp.id = ...)` -> trait clusters
- CLI (causality vs linkage): `smr --bfile ref --gwas-summary g.ma --beqtl-summary eqtl.besd --out smr` -> SMR p + HEIDI p
- CLI (allelic heterogeneity): eCAVIAR `eCAVIAR -l ld1 -l ld2 -z z1 -z z2 -o out -c 2` -> CLPP per SNP
- CLI (conditional): PWCoCo conditions on each independent signal via GCTA-COJO then runs pairwise coloc.abf

## Algorithmic Taxonomy

| Method | Model | Inputs | Output | Strength | Fails when |
|--------|-------|--------|--------|----------|------------|
| coloc.abf (Giambartolomei 2014) | Single causal variant per locus; Bayesian ABF | beta+varbeta or p+MAF; sample sizes; type/s/sdY | PP.H0-H4 | Fast (~1s/locus), no LD required, mature, widely-cited | 2+ causal variants in moderate LD -> PP.H3 inflates spuriously; assumes a single causal per trait |
| coloc.susie (Wallace 2021) | Multi-causal via SuSiE; per-credible-set pairwise coloc | Summary stats + ancestry-matched LD matrix | PP.H4 per (CS1, CS2) pair | Handles allelic heterogeneity; principled CS framework | Sensitive to LD-mismatch; sample-size-LD mismatch -> spurious credible sets; needs in-sample or matched LD |
| SMR + HEIDI (Zhu 2016) | Tests pleiotropy (one variant -> both traits) vs linkage (two variants in LD) | GWAS .ma; eQTL .besd; LD reference (plink bfile) | SMR p (significance) + HEIDI p (null = shared causal) | Distinguishes shared-causal from linkage at a top SNP; standard for eQTLGen / GTEx integration | Fails to discriminate when LD between causal SNPs > 0.7 (HEIDI loses power); HEIDI requires >= 10 SNPs near top |
| eCAVIAR / CLPP (Hormozdiari 2016) | Fine-mapping-aware; computes Colocalization Posterior Probability per SNP | Z-scores; LD matrices per trait | CLPP per SNP; per-locus sum | Handles allelic heterogeneity natively; per-SNP resolution | Computationally heavy at -c > 3 causal variants; CLPP thresholds debated (0.01 vs 0.1) |
| PWCoCo (Robinson 2022) | Pairwise conditional via GCTA-COJO conditioning | Summary stats + individual-level LD bfile | Per-conditional-signal coloc.abf results | Cleanly handles AH at top GWAS hit + secondary signals | Needs individual-level reference; sensitive to COJO collinearity threshold |
| moloc (Giambartolomei 2018) | Multi-trait extension of coloc.abf (3-5 traits) | Per-trait summary stats | 15 (3-trait) / 31 (4-trait) / 63 (5-trait) hypothesis PPs | First principled multi-omic coloc | Hypothesis count = 2^k - 1 explodes; >= 6 traits computationally infeasible; minimally updated since 2019 |
| HyPrColoc (Foley 2021) | Many-trait cluster-based; iterative branch-and-bound under single-causal | Beta + SE matrices SNPs x traits | Trait clusters sharing a causal variant | Scales to 50+ traits; identifies cluster substructure | Inherits single-causal assumption from coloc.abf; clusters can fragment under AH |
| SharePro_coloc (Zhang 2024) | Variational effect-group joint model | Beta + SE; LD per ancestry | Effect-group level PP | Handles multiple causal signals jointly; faster than coloc.susie at scale | Newer (2024); benchmarks evolving; trickier installation |
| Pullin & Wallace 2025 variant-specific priors | Function-aware p12 (e.g. up-weight coding/promoter SNPs) | Same as coloc.abf + per-SNP prior weights | PP.H0-H4 with non-uniform prior | Improves discovery when functional annotation is informative | Annotation choice is a methodological lever; report sensitivity |

Methodology evolves; verify the current Open Targets Genetics, eQTL Catalogue, and FinnGen colocalization pipelines before locking parameters. Open Targets uses coloc.abf at PP.H4 >= 0.75 with p12 = 1e-5; FinnGen uses coloc.susie at PP.H4 >= 0.8 with in-sample LD.

## Decision Tree by Scenario

| Scenario | Recommended method | Why |
|----------|---------------------|-----|
| GWAS + single-tissue eQTL, top GWAS variant looks single-signal | coloc.abf + sensitivity() | Fast, no LD needed, well-validated; single-causal assumption typically holds at clean loci |
| GWAS + eQTL, conditional analysis shows 2+ independent signals | coloc.susie OR PWCoCo | Multi-causal handling; coloc.susie if summary-stats LD available, PWCoCo if individual-level reference accessible |
| GWAS + multi-tissue eQTL (e.g. all 49 GTEx tissues) | coloc.abf per tissue + HyPrColoc across tissues | Per-tissue PP.H4 gives tissue-specific causality; HyPrColoc identifies tissue clusters sharing the variant |
| GWAS + eQTL + sQTL + mQTL (3-5 omics) | moloc (k <= 5) OR HyPrColoc | moloc gives explicit hypothesis posterior; HyPrColoc scales but loses hypothesis structure |
| Many GWAS traits at one locus (pleiotropic hub) | HyPrColoc | Designed for many-trait clustering; coloc.abf pairwise scales as k^2 |
| Top SNP has only modest GWAS p; is it the same causal as eQTL? | SMR + HEIDI | SMR tests pleiotropy/causality; HEIDI rejects shared-causal -> linkage |
| Want per-SNP credibility under allelic heterogeneity | eCAVIAR (CLPP) | Per-SNP CLPP integrates fine-mapping with coloc |
| MHC / HLA region (chr6:25-35 Mb) | HLA-coloc (Butler-Laporte 2024) OR exclude MHC | Long-range LD breaks single-causal assumption; standard PP.H4 not interpretable |
| Trans-eQTL / GWAS pair | coloc.abf with p12 lowered to 5e-6 or 1e-6 | Shared causality is biologically rare; default p12=1e-5 over-favours H4 |
| Ancestry-mismatched GWAS vs eQTL | ancestry-matched coloc.susie OR coloc_SuSiEx | LD differs across ancestries; using EUR LD on AFR z-scores produces spurious credible sets |
| Very small eQTL (N < 200) | None reliably; flag locus underpowered | All methods report H0/H1/H2 dominance; report PP transparently and gather larger reference (eQTLGen N~31k, GTEx v8) |

## Per-Method Failure Modes

### coloc.abf -- PP.H3 inflation under multiple causal variants

**Trigger:** Locus has 2+ independent causal signals in moderate LD (r2 ~ 0.3-0.6).

**Mechanism:** The single-causal-variant assumption forces the model to allocate posterior mass to H3 (distinct causal variants) whenever the per-SNP Bayes factors for the two top SNPs do not align.

**Symptom:** Visual co-localization in LocusZoom looks convincing, but `result$summary['PP.H3.abf']` dominates over PP.H4; sensitivity() shows PP.H4 stays low across the entire p12 grid.

**Fix:** Run coloc.susie (or eCAVIAR or PWCoCo) to allow multiple causal variants. If coloc.susie returns multiple credible sets with one pair showing PP.H4 > 0.75, this is real allelic heterogeneity not failure.

### coloc.susie -- LD reference mismatch

**Trigger:** Z-scores from GWAS / eQTL of one ancestry, LD matrix from 1000 Genomes EUR (or any non-matched reference).

**Mechanism:** SuSiE assumes z-scores and the supplied LD are jointly consistent. Ancestry mismatch or sample-size mismatch produces a non-positive-definite implicit covariance; SuSiE responds by returning spurious credible sets that include LD-mismatched SNPs.

**Symptom:** `susieR::estimate_s_rss(z, R, n)` returns lambda > 0.05; `susieR::kriging_rss` flags off-diagonal SNPs with extreme studentized residuals; credible sets are oddly large (50+ SNPs) or include SNPs distant in LD from the lead.

**Fix:** Use in-sample LD when at all possible (per-cohort plink `--r square`). If reference must be external, match ancestry (1KG superpopulation) and superpopulation-stratify. Run `estimate_s_rss` and report lambda; if > 0.05, drop the locus or switch to coloc.abf.

### coloc default p12 too liberal for trans-eQTL

**Trigger:** Applying `p12 = 1e-5` (the default) to a trans-eQTL / GWAS pair.

**Mechanism:** The default p12 was calibrated for cis-eQTL where biological proximity makes shared causality reasonable. For trans-eQTL, prior probability of shared causality is much lower; uniform p12 over-favours H4.

**Symptom:** PP.H4 > 0.8 reported, but sensitivity() reveals PP.H4 falls below 0.5 for p12 < 1e-5; replication in independent data fails.

**Fix:** Operational definition: "trans" = >5 Mb from TSS or different chromosome. Default p12=1e-5 over-favors H4 for trans (genome-rare biology). For trans: lower p12 to 5e-6 or 1e-6 AND raise PP.H4 threshold to >= 0.8 (compensate for higher FP risk). Cross-reference Vosa 2021 Nat Genet 53:1300 (eQTLGen trans) for empirical patterns.

### MHC / HLA + chr 8 inversion -- single-causal assumption breaks

**Trigger:** Locus within chr6:25-35 Mb (extended MHC, hg38), or chr8:8.1-11.9 Mb (chr 8 inversion, hg38).

**Mechanism:** The MHC contains classical HLA genes with extreme long-range LD (r2 > 0.5 over many Mb), multiple independent causal haplotypes, and structural variation. The chr 8p23.1 inversion similarly produces long-range LD across megabases of polymorphic inversion alleles. The single-causal-variant assumption is biologically wrong in both regions.

**Symptom:** coloc.abf almost always returns PP.H3 or fragmented PP across H1/H2/H3/H4 even when the underlying biology is well-established (e.g. HLA-DRB1 in autoimmune GWAS).

**Fix (MHC):** Use HLA-imputed classical alleles via SNP2HLA / HIBAG / HLA-TAPAS, then HLA-coloc (Butler-Laporte 2024 medRxiv) -- NOT coloc on SNPs in MHC. OR exclude MHC from genome-wide coloc and report HLA association at the haplotype/allele level. **Fix (chr 8 inversion):** Exclude chr8:8.1-11.9 Mb or pre-condition on inversion genotype before coloc. Never report a single coloc PP.H4 in either region without this caveat.

### Lead-SNP swap and window bias

**Trigger:** The two traits have different lead SNPs at the same locus; analyst centres each window on the trait-specific lead.

**Mechanism:** coloc PP is sensitive to the SNPs in the window; centring on different leads gives different per-SNP overlap and biases toward H3.

**Symptom:** Re-centring the window on the GWAS lead vs the eQTL lead produces qualitatively different PP.H4.

**Fix:** Use a SINGLE window (typically +/- 500 kb or 1 Mb) centred on the joint top-variant (the SNP with the lowest min-p across both traits), or on the GWAS lead consistently. Report PP under multiple centring choices; flag the locus if PP swings > 0.2 across centrings.

### Underpowered eQTL (N < 200)

**Trigger:** Small eQTL discovery (e.g. tissue-specific bulk study, N < 200; per-cell-type sc-eQTL).

**Mechanism:** With low N, varbeta is large; the eQTL's per-SNP Bayes factors are flat; the joint likelihood concentrates on H0 or H1 (GWAS-only).

**Symptom:** PP.H0 or PP.H1 dominates; the eQTL panel shows visible signal but coloc cannot resolve causal vs noise.

**Fix:** Use eQTLGen (N ~ 31k whole-blood) or GTEx v8 (N ~ 70-700 per tissue) where possible. For rare cell types, accept the limitation and report the locus as underpowered rather than claim absence of colocalization.

| eQTL N | Coloc viability | Notes |
|--------|-----------------|-------|
| < 200 | Underpowered | PP.H1 dominant; flag |
| 200-500 | Cis only, modest | Single-tissue cis |
| 500-1000 | Good for cis | Most GTEx v8 tissues |
| >= 1000 | Well-powered | Trans accessible |
| >= 10000 | Meta (eQTLGen) | Cross-tissue / sc |

### Reference QTL panel choice

GTEx v8 (838 donors, 49 tissues, 2020) is the current PredictDB-supported standard. GTEx v10 (released 2024) has limited harmonisation and is not yet PredictDB-default. eQTLGen blood meta-eQTL (N ~ 31k) wins on sample size for blood cis-eQTL discovery, beating any single tissue on power. Always pin version in methods (e.g. "GTEx v8 MASHR-EUR, PredictDB release 2022-01").

## PP.H4 Threshold Framework

| Threshold | Use case | Source |
|-----------|----------|--------|
| 0.5 - 0.7 | Suggestive / pilot / hypothesis-generating | Giambartolomei 2014 original |
| >= 0.7 | Triangulation tier for TWAS / cis-MR / effector-gene cross-evidence | Open Targets Genetics common practice; cross-reference downstream skills |
| >= 0.75 | Open Targets Platform / eQTL Catalogue / FinnGen default screening threshold | Open Targets Genetics docs; Mountjoy 2021 Nat Genet 53:1527 |
| >= 0.80 | Most published colocalizations / standard publication tier | Wallace 2020 PLoS Genet 16:e1008720 |
| >= 0.90 | Stringent clinical / therapeutic-target prioritization | Reserved for high-confidence claims |
| >= 0.95 | Industry / regulatory drug-target submission grade | Internal pharma default |
| PP.H3 >= 0.80 | Confident distinct causal variants (negative coloc result) | Standard |
| PP.H4 / (PP.H3 + PP.H4) >= 0.9 | Conditional probability framing (some pipelines) | Foley 2021 |

**Operational rule:** Three operational tiers map onto the most common downstream uses: (a) **>= 0.7** when PP.H4 is one of several lines of triangulating evidence (TWAS + coloc, cis-MR + coloc, effector-gene multi-evidence) -- this is the threshold downstream skills (causal-genomics/transcriptome-wide-association, causal-genomics/mendelian-randomization cis-MR, causal-genomics/effector-gene-prioritization, causal-genomics/proteome-mr-drug-target) require; (b) **>= 0.8** for standard peer-reviewed publication as a stand-alone coloc claim (Wallace 2020); (c) **>= 0.95** for industry / clinical drug-target submission. Open Targets and FinnGen pipelines screen at >= 0.75 but downstream publication-grade coloc claims should clear >= 0.8 and triangulation claims >= 0.7. ALWAYS report PP.H3 alongside PP.H4 -- a locus with PP.H4 = 0.6, PP.H3 = 0.3 is qualitatively different from PP.H4 = 0.6, PP.H3 = 0.05 (the former is real ambiguity over single vs distinct causal; the latter is underpowered evidence). Run `coloc::sensitivity()` and report the p12 range over which PP.H4 stays above the threshold.

## Default Priors and the p12 Sensitivity Question

| Prior | Default | Interpretation | When to change |
|-------|---------|----------------|----------------|
| p1 | 1e-4 | Prob a random SNP is associated with trait 1 | Rarely changed |
| p2 | 1e-4 | Prob a random SNP is associated with trait 2 | Rarely changed |
| p12 | 1e-5 | Prob a random SNP is associated with both traits | Lower (5e-6 or 1e-6) for trans-eQTL or unrelated trait pairs; raise (5e-5) only with strong prior, e.g. molecular QTL in the same tissue as causal cell type |

The p12/p1 ratio (= 0.1 under defaults) is the prior odds of colocalization given a trait-1 association. Wallace 2020 (PLoS Genet 16:e1008720) showed default p12 = 1e-5 is too liberal for many real-world settings and recommended sensitivity analysis as standard practice. Pullin & Wallace 2025 (PLoS Genet 21:e1011697) extended this with variant-specific priors weighted by functional annotation.

### p12 Sensitivity Grid

| p12 grid point | Use case | Reporting rule |
|----------------|----------|-----------------|
| 1e-4 | Suggestive only / EUR cis-eQTL relaxed | PP.H4 here cannot support a publication claim |
| 1e-5 | Default for most cis-eQTL <-> GWAS pairs | Standard |
| 5e-6 | Conservative cis; default for trans-eQTL coloc | Recommended publication baseline |
| 1e-6 | Very conservative; trans coloc with weak prior | Required for cross-trait genome-rare coloc |

**Operational rule:** Require PP.H4 to remain above threshold across at least 3 adjacent grid points; report the lowest p12 at which PP.H4 >= 0.75. Use `coloc::sensitivity(result, rule = 'H4 > 0.75')` for the diagnostic plot.

Required reporting: PP.H4 at default priors + p12 range over which PP.H4 stays above threshold.

## eCAVIAR CLPP Threshold Framework

CLPP (Colocalization Posterior Probability) is the per-SNP product of the two per-trait fine-mapping posteriors. Threshold conventions:

- Hormozdiari 2016 AJHG 99:1245 used CLPP >= 0.01 (validated against null simulations).
- 2024 GTEx / Open Targets pipelines use CLPP >= 0.05.
- High-confidence claims require CLPP >= 0.1.
- Report both sum-CLPP across the credible set AND max-CLPP at any single SNP -- the two answer different questions (locus-level vs lead-SNP-level confidence).

```bash
eCAVIAR -l ld_gwas.ld -l ld_eqtl.ld \
        -z gwas.z -z eqtl.z \
        -o coloc_out -c 2     # -c = max independent causal variants per trait
# Output: per-SNP CLPP in coloc_out_col file; report sum and max
```

## LD Matrix Construction for coloc.susie

**Requirements:**

- Signed Pearson r (not r2). coloc.susie expects directional LD; squared LD silently inverts effect-direction inference.
- Ancestry-matched to GWAS / eQTL ancestry. EUR LD on AFR z-scores produces spurious credible sets.
- SNP-order-aligned to the beta vector and named to match (row/column names = SNP IDs).
- Positive semi-definite. Numerical-noise negative eigenvalues must be repaired.
- Effective N sample-size-matched to the trait being fine-mapped (provide via `runsusie(..., n = N)`).

```bash
# plink2 phased r (signed Pearson); square matrix output
plink2 --pfile 1KG_EUR \
    --extract snps.txt --chr 6 --from-bp X --to-bp Y \
    --r-phased square --out locus_ld
```

```r
# Alternative: in-sample LD from BED via bigsnpr
R <- bigsnpr::snp_cor(snp_obj$genotypes, ind.col = locus_snps)
# PSD repair if negative eigenvalues from numerical noise
R <- as.matrix(Matrix::nearPD(R)$mat)
dimnames(R) <- list(snp_ids, snp_ids)
```

**Critical:** Row and column order of R MUST match SNP order in the beta vector -- silent failure otherwise. The SuSiE objective stays finite under mis-ordering and returns nonsense credible sets. Verify with `stopifnot(rownames(R) == names(beta))` before `runsusie`. Cross-reference causal-genomics/fine-mapping for the full LD diagnostic block (`estimate_s_rss` lambda < 0.05, `kriging_rss` outlier inspection).

## SMR vs coloc Reconciliation

SMR (Zhu 2016) and coloc test related but non-identical questions:

- **SMR** tests pleiotropy vs linkage: does the top eQTL SNP show a GWAS effect explainable by its eQTL effect (pleiotropic / causal) or does the GWAS effect come from a different SNP in LD (linkage)?
- **coloc** tests shared vs distinct causal variants over an entire window of SNPs.
- **HEIDI** is SMR's heterogeneity test; null hypothesis is single shared causal SNP. Zhu 2016 Nat Genet 48:481 specifies **HEIDI p > 0.05** (NOT 0.01) as non-rejection of single shared causal. HEIDI p > 0.05 does NOT prove shared causality -- only that data cannot reject it; pair with SMR p Bonferroni-corrected across probes. When LD between causal SNPs > 0.7, HEIDI loses power same as coloc.

When LD between two true causal SNPs is high (r2 > 0.7), both SMR/HEIDI and coloc.abf lose discriminatory power: SMR cannot pick which of the LD-tied SNPs is causal, and coloc.abf cannot reject H4 even if biology is two-distinct-causal. coloc.susie + ancestry-matched LD is the modern resolution.

**Operational rule:** SMR + HEIDI is appropriate when the question is "does this eQTL gene mediate the GWAS effect at all?" coloc is appropriate when the question is "do the two traits share a causal variant in this window?" Run both; agreement (significant SMR + non-rejected HEIDI + PP.H4 >= 0.75) is high-confidence; disagreement requires inspection (often the multi-causal / LD scenario above).

## moloc Multi-Omic Framework (3-5 Traits)

For k traits, moloc tests `2^k - 1` hypotheses. 3 traits -> 15 hypotheses (H_a, H_b, H_c, H_ab, H_ac, H_bc, H_abc, plus "none of the above"); 4 traits -> 31; 5 traits -> 63. The hypothesis H_{all-share} (all k share a single causal variant) is the multi-omic analog of PP.H4.

```r
# moloc 3-trait example; install via remotes::install_github('clagiamba/moloc')
library(moloc)
# Input: list of k dataframes with BETA, SE, N, MAF per SNP and shared SNP IDs
result_moloc <- moloc_test(listData=list(gwas=gwas_df, eqtl=eqtl_df, sqtl=sqtl_df),
                            prior_var=c(0.01, 0.1, 0.5), priors=c(1e-4, 1e-6, 1e-7))
# PPA: posterior over all 15 hypotheses (3-trait case)
# Key column: PPA.abc (all-three-share)
```

moloc is computationally tractable up to k = 5 but explodes beyond; use HyPrColoc for k >= 6.

## HyPrColoc Cluster-Based Coloc (Many Traits)

HyPrColoc (Foley 2021) extends single-causal coloc to many traits by clustering traits that share a causal variant. Output: per-cluster posterior + per-trait cluster assignment.

```r
library(hyprcoloc)
# Inputs: SNPs-by-traits matrices of betas and standard errors
# Rows = SNPs (must be shared across all traits); Columns = traits
res <- hyprcoloc(effect.est=betas, effect.se=ses,
                  trait.names=colnames(betas), snp.id=rownames(betas),
                  reg.thresh=0.7,     # regional probability of coloc threshold
                  align.thresh=0.7)   # alignment threshold for traits within a cluster
res$results  # cluster assignment per trait + posterior
```

HyPrColoc inherits the single-causal-per-cluster assumption from coloc.abf; clusters can fragment if the true biology is allelic heterogeneity.

## PWCoCo (Conditional Pairwise Coloc)

PWCoCo (Robinson 2022) wraps GCTA-COJO conditional analysis around coloc.abf. For a locus with `k1` independent trait-1 signals and `k2` independent trait-2 signals, PWCoCo runs `k1 * k2` pairwise coloc.abf tests after conditioning each summary statistic on the other independent signals.

**When to use:** When GCTA-COJO has identified >= 2 independent signals in at least one trait and individual-level reference genotypes are available. Particularly suited to bulk eQTL with secondary cis signals.

**Inputs:** Per-trait summary stats (SNP, A1, A2, freq, beta, se, p, N) + plink bfile reference. **Output:** One coloc.abf result per (conditional signal 1, conditional signal 2) pair. Interpret each row as an independent single-signal coloc.

**Caveats:** PWCoCo requires individual-level reference (plink bfile); cannot run on summary stats alone. Collinearity threshold in COJO (default `--cojo-collinear 0.9`) controls how aggressively independent signals are split; lower values fragment, higher values merge. Worked CLI recipe in usage-guide.md.

## Standard coloc.abf Pipeline

**Goal:** Test whether a single GWAS lead variant shares a causal variant with an eQTL gene's top signal at a defined locus.

**Approach:** Extract a 1 Mb window centred on the GWAS lead; harmonise alleles between datasets; format coloc input lists with `type` ('quant' or 'cc'), sample size `N`, and either `sdY` (quant) or `s` (cc); run coloc.abf; run sensitivity() over the p12 grid.

```r
library(coloc)

# Inputs: harmonised gwas_df and eqtl_df with SNP, BETA, SE, MAF, N, POS columns
# Both must share the same SNP set and allele coding (verify with harmonise step)

gwas_input <- list(
    beta=gwas_df$BETA, varbeta=gwas_df$SE^2,
    snp=gwas_df$SNP, position=gwas_df$POS,
    type='cc',           # case-control GWAS
    s=0.30,              # case fraction
    N=50000)

eqtl_input <- list(
    beta=eqtl_df$BETA, varbeta=eqtl_df$SE^2,
    snp=eqtl_df$SNP, position=eqtl_df$POS,
    type='quant',        # quantitative eQTL
    sdY=1,               # SD(expression); 1 if standardised, else estimate from MAF+varbeta
    N=500)

res <- coloc.abf(dataset1=gwas_input, dataset2=eqtl_input,
                  p1=1e-4, p2=1e-4, p12=5e-6)   # conservative p12

print(res$summary)
sens <- coloc::sensitivity(res, rule='H4 > 0.75')   # generates plot + table
```

`sdY` semantics: when omitted, coloc estimates from `MAF` and `varbeta`; supplying `sdY=1` ASSUMES the trait is already standardised (eQTL with inverse-normal-transformed expression). Mismatch produces silently wrong Bayes factors -- the most common silent failure.

- For quantitative trait: leave `sdY=NULL` to estimate via `coloc:::sdY.est(varbeta, MAF, N)`. If CV of estimated sdY across SNPs > 0.5, varbeta/MAF are inconsistent -- coloc will silently miscalibrate Bayes factors.
- For inverse-normal-transformed expression: use `sdY = 1` (already standardized).
- Mismatch produces silently wrong PP -- most common silent failure.

`s` parameter for case-control (`type='cc'`):

- `s` = N_cases / N_total (NOT cases-per-control; NOT 0.5 default).
- For population-cohort case-control: `s` ~ disease prevalence in the cohort (~0.005 for rare disease).
- Wrong `s` does not error -- silently biases PP at extreme MAF.

## coloc.susie Multi-Causal Pipeline

**Goal:** Test colocalization at a locus with multiple independent signals (allelic heterogeneity).

**Approach:** Run SuSiE on each trait's summary statistics with ancestry-matched LD; verify LD-z-score consistency; coloc-test each pair of credible sets.

```r
library(coloc); library(susieR)

# Diagnostic: z-score vs LD consistency MUST be checked
z_gwas <- gwas_df$BETA / gwas_df$SE
lam_gwas <- susieR::estimate_s_rss(z=z_gwas, R=ld_matrix, n=gwas_n)
if (lam_gwas > 0.05) stop('LD reference mismatched to z-scores; lambda=', lam_gwas)

s1 <- runsusie(list(beta=gwas_df$BETA, varbeta=gwas_df$SE^2,
                    snp=gwas_df$SNP, position=gwas_df$POS,
                    type='cc', s=0.3, N=50000, LD=ld_matrix), L=10)
s2 <- runsusie(list(beta=eqtl_df$BETA, varbeta=eqtl_df$SE^2,
                    snp=eqtl_df$SNP, position=eqtl_df$POS,
                    type='quant', sdY=1, N=500, LD=ld_matrix), L=10)

res_susie <- coloc.susie(s1, s2)   # NULL if no overlapping CS
# res_susie$summary rows: each (hit1, hit2) pair of credible sets
```

LD matrix MUST be in the same SNP order as the beta vector; mis-ordering silently produces nonsense.

## SMR + HEIDI Pipeline

```bash
# SMR is a command-line tool. Pre-format GWAS into .ma (SNP A1 A2 freq beta se p N).
# eQTL data as BESD (binary eQTL summary data); pre-built BESD available from eQTLGen / GTEx.

smr --bfile 1KG_EUR_chr6 \
    --gwas-summary gwas.ma \
    --beqtl-summary eqtl_chr6.besd \
    --out smr_result \
    --thread-num 4 \
    --peqtl-smr 5e-8 \
    --heidi-mtd 1
# Output smr_result.smr: probe (gene) | top SNP | p_SMR | p_HEIDI | nsnp_HEIDI
```

Interpretation: significant `p_SMR` (Bonferroni-corrected across probes tested, typically < 5e-8 / N_probes) AND non-rejection by HEIDI (`p_HEIDI > 0.05`, per Zhu 2016) indicates pleiotropy / shared causal; `p_HEIDI <= 0.05` rejects shared-causal -> linkage. HEIDI p > 0.05 does NOT prove shared causality, only that data cannot reject it. Require `nsnp_HEIDI >= 10` for HEIDI reliability.

## Allele Harmonisation (Critical Pre-Step)

Mismatched effect alleles silently invert signs of betas, collapsing PP.H4 into PP.H3. Required steps before coloc:

1. Merge GWAS and eQTL summary stats by SNP ID (rsID or chr:pos:ref:alt).
2. Mark SNP-pairs as `same` (A1/A2 match) or `flip` (A1/A2 swap); drop SNPs that match neither.
3. For `flip` rows, negate the second dataset's beta (and swap A1/A2).
4. Drop palindromic SNPs (A/T or C/G) at MAF > 0.42; their strand cannot be inferred from coding alone (TwoSampleMR `harmonise_data` standard cutoff).
5. Verify genome build alignment (hg19 vs hg38 must match; lift over if not).

Worked harmonisation code and build-mismatch pitfalls: see usage-guide.md.

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Sensitivity to p12 prior?" | `coloc::sensitivity()` reported; PP.H4 robust across 1e-7 to 1e-5 grid |
| "Why not coloc.susie? Multi-causal possible?" | coloc.abf single-causal assumption stated; if PP.H3 dominant or GCTA-COJO identifies >= 2 independent signals, coloc.susie / SuSiE-based run; reported |
| "LD reference matched?" | In-sample preferred; if reference panel used, `estimate_s_rss(z, R, N)` lambda < 0.05; `kriging_rss` diagnostic clean |
| "PP.H4 = 0.6 is colocalization?" | No -- bands stated: 0.5-0.7 suggestive; >= 0.7 triangulation tier; >= 0.8 standard publication; >= 0.95 industry/clinical |
| "MHC region included?" | chr6:25-35 Mb excluded; HLA-coloc (Butler-Laporte 2024) for classical-allele-level coloc |
| "Ancestry mismatch?" | LD reference ancestry-matched to GWAS; for cross-ancestry use coloc_SuSiEx |
| "Sentinel SNP swap?" | Re-centered window on each trait's lead, joint top, eQTL top; PP.H4 stable within 0.1 |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `Error in coloc.abf: dataset must have N` | Forgot `N` in list, or `type` not set | Supply both; case-control also needs `s`; quant also needs `sdY` |
| PP.H3 dominant despite obvious visual overlap | 2+ causal in moderate LD breaks single-causal assumption | Run coloc.susie or eCAVIAR |
| `estimate_s_rss` lambda > 0.05 | LD reference does not match z-scores (ancestry / sample / build) | Use in-sample LD or ancestry-matched reference; do not proceed |
| PP.H4 unstable across p12 sensitivity grid | Borderline evidence; default priors not justified | Report the p12 range; lower priors for trans-eQTL; do not over-claim |
| coloc.susie returns NULL summary | No overlapping credible sets between traits | Genuine result (no shared signal) or both traits underpowered |
| Per-SNP betas have opposite signs but same magnitude across traits | Effect-allele mismatch | Run harmonisation; flip betas where A1/A2 swap; drop palindromic at high MAF |
| SMR significant + HEIDI p <= 0.05 | Linkage, not shared causal | Report as linkage; do not call colocalization |
| moloc all-share PPA collapses to ~0 | Different sample sizes / power across omics | Inspect per-omic effect sizes; consider HyPrColoc for cluster output |
| HyPrColoc trait cluster fragments | Underlying biology is multi-causal | Switch to coloc.susie at each suspected cluster centre |
| MHC PP.H4 close to 0 with strong visual signal | Long-range LD breaks single-causal | Use HLA-coloc or exclude MHC; never report standard coloc PP at MHC |

## Tool Install Notes

- **coloc**: CRAN. `install.packages('coloc')`. Bundles susieR dependency for >= 5.1.
- **susieR**: CRAN. `install.packages('susieR')`. >= 0.12.35 for `estimate_s_rss` and `kriging_rss`.
- **HyPrColoc**: GitHub only (never CRAN). `remotes::install_github('jrs95/hyprcoloc')`. Requires R >= 3.5.
- **SMR**: Pre-compiled binary from cnsgenomics.com/software/smr. Linux/Mac/Windows binaries; no R package.
- **eCAVIAR**: Compile from GitHub fhormoz/caviar; C++ source. CLI `eCAVIAR`. PAINTOR is the related multi-trait fine-mapping toolkit.
- **PWCoCo**: GitHub jwr-git/pwcoco. Compiled C++ CLI; can also be invoked from R via wrapper scripts.
- **SharePro_coloc**: GitHub only (no PyPI release). `git clone https://github.com/zhwm/SharePro_coloc` then `pip install -r requirements.txt`.
- **moloc**: GitHub clagiamba/moloc. R package; minimally updated since 2019, no CRAN release. R >= 3.5.

## Reviewer-Grade Reporting Template

For each colocalization claim, the report should include:

1. **Method and version** (e.g. coloc 5.2.3 coloc.abf, or coloc.susie with SuSiE L=10).
2. **Window definition** (e.g. +/- 500 kb around the GWAS lead rs12345 at chr6:30450000, hg38), and lead-SNP-swap sensitivity (PP.H4 at GWAS lead vs eQTL lead vs joint top).
3. **Priors** p1, p2, p12 used; **sensitivity** plot from `coloc::sensitivity()` and the p12 range over which PP.H4 stays above threshold.
4. **All five posteriors** PP.H0 through PP.H4 (not PP.H4 alone).
5. **Threshold band** the result clears (>= 0.7 triangulation tier, >= 0.75 Open Targets screening, >= 0.80 published, >= 0.90 stringent, >= 0.95 clinical).
6. **LD reference** ancestry, source (1000G phase 3 EUR / in-sample / UKBB), and lambda from `estimate_s_rss` if coloc.susie.
7. **Reference QTL panel** version (e.g. GTEx v8 MASHR-EUR, PredictDB release 2022-01; eQTLGen 2019).
8. **Conditional analysis** GCTA-COJO results if multi-causal; per-credible-set PP if coloc.susie.
9. **Failure-mode caveats** explicitly addressed: MHC excluded, chr 8 inversion excluded, ancestry-matched LD, sdY/s correctly specified, palindromic SNPs handled.
10. **Methods-section H0-H4 prose** describing what each hypothesis means (see usage-guide.md).

## References

- Giambartolomei C et al 2014 PLoS Genet 10:e1004383 (coloc.abf)
- Wallace C 2020 PLoS Genet 16:e1008720 (prior elicitation; relaxing the single-causal-variant assumption; default-prior sensitivity)
- Pullin JM & Wallace C 2025 PLoS Genet 21:e1011697 (variant-specific priors)
- Wallace C 2021 PLoS Genet 17:e1009440 (coloc.susie; multiple causal variants)
- Zhu Z et al 2016 Nat Genet 48:481 (SMR + HEIDI)
- Hormozdiari F et al 2016 AJHG 99:1245 (eCAVIAR / CLPP)
- Giambartolomei C et al 2018 Bioinformatics 34:2538 (moloc)
- Foley CN et al 2021 Nat Commun 12:764 (HyPrColoc)
- Robinson JW et al 2022 bioRxiv 2022.08.08.503158 (PWCoCo)
- Zhang W et al 2024 Bioinformatics 40:btae295 (SharePro_coloc)
- Butler-Laporte G et al 2024 medRxiv 2024.11.05.24316783 (hlacoloc)
- Mountjoy E et al 2021 Nat Genet 53:1527 (Open Targets Genetics colocalization pipeline)
- Vosa U et al 2021 Nat Genet 53:1300 (eQTLGen, N ~ 31,684 whole blood)
- GTEx Consortium 2020 Science 369:1318 (GTEx v8 multi-tissue eQTL)

## Related Skills

- causal-genomics/mendelian-randomization - Causal effect estimation from coloc-validated SNPs
- causal-genomics/fine-mapping - SuSiE / FINEMAP / CAVIAR credible sets feeding coloc.susie; LD construction protocol cross-ref
- causal-genomics/mediation-analysis - Downstream causal mediation given coloc shared causal variants
- causal-genomics/pleiotropy-detection - Distinguishing horizontal pleiotropy from shared causality
- causal-genomics/transcriptome-wide-association - TWAS / PrediXcan / FOCUS gene-level prioritization complementary to coloc
- causal-genomics/proteome-mr-drug-target - pQTL coloc + MR for drug-target prioritization
- causal-genomics/effector-gene-prioritization - Locus-to-gene with coloc, ABC, V2G integration
- population-genetics/association-testing - GWAS summary statistic generation and locus extraction
- population-genetics/linkage-disequilibrium - LD reference panels for coloc.susie and PWCoCo
- variant-calling/variant-annotation - Functional annotation for variant-specific priors
- variant-calling/filtering-best-practices - Pre-coloc QC for summary stats
- differential-expression/deseq2-basics - Generating eQTL / molecular QTL counts
- single-cell/scatac-analysis - Per-cell-type chromatin context for coloc interpretation
- workflows/gwas-pipeline - Upstream GWAS analysis producing coloc input
- data-visualization/ggplot2-fundamentals - Regional and LocusCompare plot construction
<!-- END FILE: causal-genomics/colocalization-analysis/SKILL.md -->

## 子目录：causal-genomics/effector-gene-prioritization

<!-- BEGIN FILE: causal-genomics/effector-gene-prioritization/SKILL.md -->
---
name: bio-causal-genomics-effector-gene-prioritization
description: Maps GWAS-implicated loci to candidate effector (causal) genes by integrating variant-to-gene (V2G) features via Open Targets L2G (Mountjoy 2021), MAGMA gene-based association (de Leeuw 2015), FUMA SNP2GENE, cS2G combined SNP-to-gene scores (Gazal 2022), Polygenic Priority Scores (PoPS, Weeks 2023), FLAMES, INQUISIT, DEPICT, and enhancer-gene predictors (ABC, ENCODE-rE2G). Use when narrowing a GWAS lead locus to a candidate causal gene, picking between proximity, eQTL-based, and similarity-based prioritizers, integrating multi-evidence streams (fine-mapping, colocalization, ABC enhancer-gene, distance, chromatin), reconciling discordant L2G vs PoPS calls, prioritizing tissue-specific eQTL evidence, or triangulating across at least three independent lines of evidence for a publication-grade effector-gene nomination.
tool_type: mixed
primary_tool: MAGMA
---

## Version Compatibility

Reference examples tested with: MAGMA 1.10+ (cncr.nl/research/magma), FUMA web platform v1.6+ (fuma.ctglab.nl), Open Targets Genetics API (REST + GraphQL, June 2024 release), PoPS (head of `FinucaneLab/pops`, 2024), cS2G pre-computed scores (Zenodo record 7754032, Gazal 2022), ABC-Enhancer-Gene-Prediction 0.2.2+, ENCODE-rE2G v1.0+ (Gschwind 2023 preprint), DEPICT v1 rel194, INQUISIT (Fachal 2020 supplementary), Python 3.9-3.11, R 4.3+, PLINK 1.9 + PLINK 2.0.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `magma --help` to confirm gene-window, gene-annot, and gene-set flag names
- Python: `pip show gentropy`; introspect endpoints at `api.platform.opentargets.org/api/v4/graphql`
- R: `packageVersion('coloc')` etc. for upstream evidence integration

If a script throws an error about an argument that has moved (e.g. an Open Targets endpoint renamed during a release) or a model file schema change, introspect the installed tool and adapt rather than retrying. Open Targets Genetics deprecated the standalone Genetics Portal in 2024 in favour of the integrated platform; verify endpoint URLs at the time of use.

# Effector Gene Prioritization

**"Which gene at this GWAS locus is actually the causal mediator?"** -> Integrate fine-mapping, colocalization, chromatin-based enhancer-gene predictions, distance, and gene-similarity priors into a per-locus per-gene confidence score, then require concordance across multiple orthogonal evidence streams before nominating a causal effector. Effector gene prioritization is the bridge between statistical fine-mapping (variant level) and biological hypothesis (gene level); it is the most failure-prone step in GWAS-to-target pipelines because the nearest-gene assumption is wrong roughly 30-50% of the time at well-studied loci.

- CLI (gene-level association): `magma --bfile ref --gene-loc geneloc.txt --pval gwas.tsv ncol=N --out out` -> `magma --gene-results out.genes.raw --set-annot annot.txt --out out`
- Web (integrative): FUMA SNP2GENE at fuma.ctglab.nl (positional + eQTL + Hi-C + chromatin in one workflow)
- API (pre-computed L2G): Open Targets Genetics GraphQL `studyLocus2GeneTable` query (note: Open Targets Genetics was consolidated into the Open Targets Platform in 2024; verify the live endpoint at `api.platform.opentargets.org/api/v4/graphql`)
- Python (similarity prior): `python pops.py --gene_annot_path gene_annot.txt --feature_mat_prefix features --control_features_path control.features --magma_prefix magma_out --out_prefix out`
- Lookup (combined SNP-to-gene): cS2G pre-computed gene scores at zenodo.org/records/7754032
- CLI (enhancer-gene): ABC pipeline or ENCODE-rE2G (cross-reference atac-seq/enhancer-gene-linking)

V2G is not one method but a portfolio. Open Targets L2G aggregates per-locus per-gene features (distance + coloc + chromatin + V2G) trained on curated gold-standard genes; PoPS adds an orthogonal genome-wide polygenic prior from gene-pathway co-membership; MAGMA provides the lightweight gene-level p-value baseline. Strong effector calls emerge from concordance across these orthogonal signal types, not from any single tool.

## Algorithmic Taxonomy

| Tool | Model | Inputs | Output | Strength | Fails when |
|------|-------|--------|--------|----------|------------|
| Open Targets L2G (Mountjoy 2021 Nat Genet 53:1527) | Gradient-boosting classifier on per-(locus, gene) features (distance, fine-mapping, coloc, chromatin, V2G) trained on curated gold standards | Pre-computed per study; queried via API | Per-(study, locus, gene) L2G score 0-1 | Most validated integrative scorer; built into Open Targets Platform; updated quarterly | Trait must be in OT release; custom traits need re-training; coverage limited to OT-curated GWAS catalog |
| V2G (Ghoussaini 2021 Nucleic Acids Res 49:D1311) | Open Targets V2G feature aggregator: per-variant eQTL/sQTL/pQTL + chromatin + distance | OT pre-computed | Per-(variant, gene) score | Variant-resolution; complements locus-resolution L2G | Feature weights are fixed; cannot tune per-trait |
| MAGMA (de Leeuw 2015 PLoS Comput Biol 11:e1004219) | SNP-to-gene window aggregation + multiple regression on summary statistics | GWAS sumstats + gene annotation + LD reference (PLINK bfile) | Gene-level Z, p; gene-set p | Mature, fast, lightweight; supports gene-set enrichment in same pass; widely cited | Window choice (0+0 vs 35kb+10kb vs 50kb+50kb) shifts top genes; cannot detect distal regulation outside window |
| FUMA SNP2GENE (Watanabe 2017 Nat Commun 8:1826) | Web platform combining positional + eQTL + Hi-C + chromatin annotation + MAGMA | Sumstats upload to fuma.ctglab.nl | Annotated locus + prioritised gene table | One-click integrative analysis; no local install needed; community standard for GWAS post-hoc | Web-only; no API for high-throughput; pre-baked annotations may lag latest reference releases |
| cS2G (Gazal 2022 Nat Genet 54:827) | Weighted aggregation of 7 constituent SNP-to-gene strategies (Exon, Promoter, fine-mapped cis-eQTL, EpiMap enhancer-gene, ABC, Cicero, etc.) calibrated on heritability enrichment | Per-SNP lookup | Combined per-SNP score allocated to genes | Heritability-calibrated; pre-computed gene scores for downstream filtering | Aggregation weights are population-averaged; cell-type-specific signal averaged out; coverage limited to baseline-LF SNP universe |
| PoPS (Weeks 2023 Nat Genet 55:1267) | Ridge (L2-penalized) regression of per-gene MAGMA Z on genome-wide gene-feature matrix (pathway membership, co-expression, PPI) | MAGMA Z + gene-feature matrix | Per-gene priority score (PoPS); per-locus relative ranking | Orthogonal to distance / proximity; identifies genes with similar pathway / co-expression profile to other GWAS hits | Pathway co-membership similarity is similarity-based; can hand-feed bias if features are not curated; complementary to L2G, not redundant |
| FLAMES (Schipper M et al 2025 Nat Genet 57:323) | Combined per-feature scoring with a machine-learning (XGBoost) classifier + convergence module | Sumstats + features | Per-gene prioritisation | Recent integrative method | Limited validation outside the publication test set; method choice still evolving |
| INQUISIT (Fachal 2020 Nat Genet 52:56) | Three-level scoring for coding, regulatory-proximal, regulatory-distal; trait-specific (breast cancer) | Sumstats + cancer-specific annotation panel | Per-gene INQUISIT score | Cancer-tuned; integrates expression and chromatin context | Originally trait-specific (breast cancer); adapting to other diseases requires re-curation |
| DEPICT (Pers 2015 Nat Commun 6:5890) | Empirical Bayes; gene set enrichment + tissue prioritisation + reconstituted gene sets | Sumstats | Per-gene p; pathway enrichment; tissue priority | Old but still cited; combines three useful outputs | Reconstituted gene sets are dated (2015 expression panel); largely superseded by L2G + PoPS combination |
| ABC + ENCODE-rE2G | Activity x Contact enhancer-gene model (Fulco 2019) and logistic-regression refinement (Gschwind 2023 preprint) | ATAC + H3K27ac + Hi-C/Micro-C | Per-(enhancer, gene) score | Direct mechanistic enhancer-gene link in matched cell type; gold-standard for distal regulation | Requires matched epigenome data; cell-type-specific; covered in detail in atac-seq/enhancer-gene-linking |
| sc-eQTL + cell-type-specific TWAS (e.g. Yazar 2022 OneK1K) | Per-cell-type eQTL panels + per-cell-type prediction weights | sc-eQTL panel + sumstats | Cell-type-resolved gene candidates | Resolves cell-type-specific causal genes that bulk-tissue TWAS averages out | Requires matched single-cell eQTL panel; not yet pre-built for most cell types |

Methodology evolves; verify against the current Open Targets release (platform-docs.opentargets.org), the latest PoPS feature matrix at FinucaneLab/pops, and ABC / ENCODE-rE2G releases before locking on a single prioritiser. The L2G + PoPS combination is the current de facto two-method baseline; cS2G is the heritability-calibrated lookup; FUMA is the no-install community standard.

## Decision Tree by Scenario

| Scenario | Recommended workflow | Why |
|----------|---------------------|-----|
| Open Targets Platform covers the trait | Query L2G via GraphQL + cross-check V2G; sanity-check with PoPS | Pre-computed, gold-standard-validated; minimal compute |
| Custom trait, EUR GWAS sumstats only | MAGMA + manual fine-mapping (SuSiE) + coloc per QTL panel | Build evidence streams from primitives; combine in own integrative scorer |
| Tissue known (e.g. liver for lipid traits) | Tissue-specific eQTL coloc + ABC / ENCODE-rE2G + S-PrediXcan + L2G | Tissue-targeted evidence reduces false positives from wrong-tissue eQTLs |
| Tissue unknown a priori | LDSC-SEG (Finucane 2018 Nat Genet 50:621) to prioritise tissue + S-MultiXcan + PoPS | Identify causal tissue before locking on a single eQTL panel |
| Distal / long-range regulation suspected | ABC / ENCODE-rE2G / HiChIP / Cicero overlay; deprioritise distance-only methods | Nearest-gene fails ~ 30-50% of the time at well-studied loci |
| Polygenic background trait (e.g. height, BMI) | L2G + PoPS concordance | PoPS captures pathway prior absent from L2G features; concordance flags strong candidates |
| Publication-grade triangulation | All evidence streams; require concordance across >= 3 orthogonal lines | High-confidence claim defensible to reviewers |
| Multi-ancestry GWAS | MAGMA per ancestry + ancestry-specific eQTL coloc + MA-FOCUS for TWAS | Single-ancestry weights miscalibrated for other ancestries |
| Locus with no coding variants, no significant eQTL | ABC / ENCODE-rE2G in candidate tissue + chromatin annotation; tag as "regulatory of unknown gene" | Distance + chromatin may be the only signal; acknowledge low confidence |
| HLA region (chr6:28477797-33448354 hg19; chr6:28510120-33480577 hg38; extended chr6:25-35 Mb both builds) | Exclude or use HLA-imputation; do not run standard V2G; verify build before excluding | Long-range LD breaks every gene-by-gene method |

## Per-Method Failure Modes

### Nearest-gene assumption fails (most common pitfall)

**Trigger:** Assigning the GWAS lead variant to the closest gene without checking long-range regulation.

**Mechanism:** Approximately 30-50% of well-fine-mapped GWAS variants regulate a gene that is NOT the nearest TSS (Mountjoy 2021; Fulco 2019 Nat Genet 51:1664). Distal enhancer-promoter contacts span 50 kb to > 1 Mb; LD around the lead variant often spans only kilobases, so the credible-set centroid may sit closer to a passenger gene than to the true target.

**Symptom:** Distance-based prioritisation names the nearest gene; subsequent eQTL coloc, ABC, and ENCODE-rE2G converge on a different gene at the same locus. Functional validation (CRISPRi at the variant) confirms the distal gene.

**Fix:** Use L2G (which includes distance but does not let it dominate), PoPS (which is distance-orthogonal by construction), and ABC / ENCODE-rE2G when matched epigenome data are available. Report all candidate genes at the locus with their evidence-stream contributions; do not collapse to the nearest by default.

### eQTL tissue mis-specification

**Trigger:** Using a single-tissue eQTL panel (e.g. whole blood) when the causal tissue is different (e.g. liver for lipid traits, hypothalamus for energy balance).

**Mechanism:** Cis-eQTL effect sizes are tissue-specific; eQTLs in the wrong tissue still tag the GWAS signal via LD and produce spurious colocalisations or TWAS hits. The right gene at the wrong tissue is statistically detectable but biologically uninterpretable.

**Symptom:** Strong colocalisation in a tissue biologically irrelevant to the trait; null in the expected tissue. LDSC-SEG / CELLEX / EWCE prioritisation on the GWAS sumstats independently disagrees with the eQTL tissue.

**Fix:** Run multi-tissue eQTL coloc (e.g. all GTEx tissues via S-MultiXcan + per-tissue coloc) and prioritise the tissue identified by LDSC-SEG (Finucane 2018 Nat Genet 50:621) or CELLEX. For cell-type-specific traits, move to sc-eQTL panels (OneK1K, Yazar 2022 Science 376:eabf3041). S-MultiXcan (Barbeira 2019 PLoS Genet 15:e1007889) jointly tests per-tissue z-scores via PC-decomposition of LD-induced covariance and is preferred for standard GTEx v8 panels (pre-computed weights available); UTMOST (Hu 2019 Nat Genet 51:568) imputes cross-tissue expression weights before testing and is preferred when retraining cross-tissue weights for a custom panel.

### MAGMA gene-window choice

**Trigger:** Default `--gene-loc` with 0kb upstream / 0kb downstream window assigns all SNPs only within annotated gene bodies.

**Mechanism:** A wide window (e.g. 35kb upstream + 10kb downstream) captures more regulatory SNPs per gene but assigns each tag-SNP to multiple genes simultaneously, diluting per-gene signal and inflating false positives at gene-dense regions. A narrow window misses regulatory SNPs outside the gene body and loses true positives at intergenic enhancers. The three window conventions in circulation are not interchangeable: MAGMA-native default is 0+0 (no expansion); the MAGMA paper recommended a 50+50 sensitivity check; FUMA SNP2GENE uses 35+10 (35 kb upstream + 10 kb downstream) which is FUMA's convention, NOT MAGMA's default. For brain traits, 50+50 captures distal cis-eQTL signal; for cardiometabolic traits a tighter 10+10 is more conservative. State explicitly which window was used in methods reporting.

**Symptom:** Many genes per locus flagged at p < 0.05/22k with the wide window; few genes at all flagged with the narrow window; top genes change substantially across window choices.

**Fix:** Use a sensible default (35kb upstream + 10kb downstream is the FUMA recommendation; 0+0 is MAGMA-native; 50+50 is the MAGMA-paper sensitivity window). Always pair MAGMA with eQTL-based mapping (S-PrediXcan, coloc) for distal-regulatory signal; MAGMA alone is the lightweight baseline, not the full answer.

**Wide-window 1Mb warning:** Going to 100+100 kb or 1 Mb assigns one SNP to 8-12 genes simultaneously at gene-dense loci (e.g. MHC, chr19q13, chr17q21), diluting power and creating interpretation ambiguity. Avoid 1Mb windows; if distal regulation is suspected supplement with ABC / ENCODE-rE2G enhancer-gene linkage (cross-reference atac-seq/enhancer-gene-linking) rather than widening the MAGMA window.

### Coloc fails when the locus has multiple causal variants

**Trigger:** PP.H4 < threshold despite biological evidence that the gene is causal.

**Mechanism:** coloc.abf's single-causal-variant assumption forces posterior mass to PP.H3 (distinct causal variants) when 2+ independent signals in moderate LD drive both traits. The result is a false-negative coloc call at a true effector-gene locus.

**Symptom:** Visual LocusZoom overlap is convincing but PP.H4 stays in 0.3-0.6; coloc.susie or eCAVIAR reveals multiple credible sets and a per-credible-set PP.H4 > 0.7.

**Fix:** Run coloc.susie (not coloc.abf) at gene-dense / signal-rich loci. Cross-reference causal-genomics/colocalization-analysis; do not rely on coloc.abf as the sole coloc evidence stream when allelic heterogeneity is plausible.

### PoPS vs L2G discordance

**Trigger:** PoPS top-ranked gene at locus disagrees with L2G top-ranked gene.

**Mechanism:** PoPS uses similarity-based features (pathway membership, co-expression, PPI), L2G uses per-locus features (distance, fine-mapping, coloc, chromatin). They are orthogonal by construction; disagreement is informative, not a failure.

**Symptom:** Same locus, different top gene under each method.

**Fix:** Use BOTH and treat concordance (top gene matches across L2G and PoPS) as the strongest single-locus signal short of CRISPR validation. Concordance between PoPS and locus-based methods markedly increases positive predictive value over either method alone (Weeks 2023 Nat Genet 55:1267). Report both ranks; flag concordance.

### Pleiotropic locus / multiple causal genes per locus

**Trigger:** Two or more genes at a single GWAS locus are each independently causal (different SNPs or different mechanisms).

**Mechanism:** Standard V2G frameworks assume one causal gene per locus. Real biology violates this: an estimated 5-10% of GWAS loci have multiple causal genes (a working convention; CRISPRi-FlowFISH catalogs document multi-gene loci).

**Symptom:** Two genes at the locus both pass conditional independence checks (FUSION.post_process.R conditional/joint analysis, GCTA-COJO); both show strong eQTL coloc; both have CRISPRi support.

**Fix:** Allow multi-gene reporting. Each candidate gene needs its own credible variant set (SuSiE / coloc.susie). Report the locus as multi-effector; consider CRISPRi-FlowFISH or MPRA for ground-truth resolution. Do not force a single-gene assignment. Existing CRISPRi enhancer-gene perturbation catalogs for cross-checking computational predictions: Fulco 2019 Nat Genet 51:1664 (>3,500 CRISPRi-FlowFISH enhancer-gene connections for 30 genes in K562); Gasperini 2019 Cell 176:377 (~75,000 pairs at-scale); Schraivogel 2020 Nat Methods 17:629 (TAP-seq / targeted Perturb-seq enhancer-gene screen in K562). Cite the specific catalog when reporting "validated against CRISPRi" rather than the generic term.

## Per-Credible-Set Gene-Assignment Hierarchy

When fine-mapping returns credible sets (cross-reference causal-genomics/fine-mapping), each credible variant should be assigned to a gene using a fixed lexicographic ladder rather than a single feature. The ladder collapses ambiguity by preferring direct mechanistic evidence first and falling back to weaker signals only when stronger ones are absent:

1. **Coding consequence at credible variant** (missense, splice-donor / splice-acceptor, stop-gained, start-lost via VEP / Ensembl consequence) -> assign variant to that gene.
2. **eQTL / pQTL colocalization PP.H4 >= 0.7** with the gene's expression QTL (matched tissue) -> assign to that gene (cross-reference causal-genomics/colocalization-analysis).
3. **ABC or ENCODE-rE2G enhancer-gene linkage** when matched ATAC + H3K27ac (+ optional Hi-C) is available in the candidate tissue -> assign to the linked gene (cross-reference atac-seq/enhancer-gene-linking).
4. **Nearest TSS** -> assign as last-resort fallback; flag as low-confidence (nearest-gene is correct only 50-70% of the time at well-fine-mapped loci).

If a single credible variant ties across two or more genes at the same rung (e.g. coding consequence in gene A AND a competing eQTL coloc to gene B), report multi-gene candidacy explicitly rather than forcing a single assignment; the locus may be multi-effector or the credible set may straddle a regulatory boundary.

## Multi-Evidence Integration Framework

A strong candidate causal gene at a GWAS locus requires concordance across multiple orthogonal evidence streams. The six canonical streams:

| Evidence stream | What it tests | Pass threshold | Source |
|----------------|---------------|----------------|--------|
| Fine-mapping | SuSiE PIP for variant; variant assigned to gene by ABC or eQTL coloc | PIP > 0.5; credible set purity > 0.5 | susieR (cross-reference causal-genomics/fine-mapping) |
| Colocalization | Shared causal variant with gene's eQTL / pQTL / sQTL | coloc.abf or coloc.susie PP.H4 >= 0.7 | coloc (cross-reference causal-genomics/colocalization-analysis) |
| Distance | Variant within annotated regulatory unit (gene body or enhancer-gene unit) | Distance to TSS <= 100 kb OR within ABC enhancer-gene unit | Convention; Mountjoy 2021 |
| Polygenic prior (similarity) | Gene shares pathway / co-expression / PPI with other GWAS hits for the trait | PoPS score in top decile per locus | Weeks 2023 |
| L2G (integrative classifier) | Per-locus per-gene gradient-boosting on a panel of features | L2G score >= 0.5 (Open Targets default high-confidence) | Mountjoy 2021 |
| Chromatin / enhancer-gene | ABC or ENCODE-rE2G connects fine-mapped variant to gene's promoter | ABC >= 0.02 OR ENCODE-rE2G >= 0.5 | Fulco 2019; Gschwind 2023 |
| Deep-learning variant effect (optional 7th) | chromBPNet / EnFormer in silico variant effect on accessibility/expression at credible variant | \|log2FC\| > 1 (chromBPNet strong-effect); agreement across two models | chromBPNet: Pampari 2025 bioRxiv 2024.12.25.630221 (preprint); EnFormer: Avsec 2021 Nat Methods 18:1196; cross-reference atac-seq/deep-learning-atac |
| Cross-trait coincidence (optional 8th) | Same gene flagged at related-trait loci (e.g. lipid GWAS at CHD lead variant) | Same gene top-ranked at >= 2 related traits | Convention |

**Operational rule:** Report a gene as a "high-confidence causal effector" only when >= 3 of the 6 core evidence streams are concordant (deep-learning variant effect and cross-trait coincidence are optional supplementary streams). >= 4 concordant is "strong-confidence"; >= 5 is "near-certain pending experimental validation". Single-stream evidence is associational only; two-stream concordance is suggestive. This is the standard used by Open Targets Genetics (Mountjoy 2021), GTEx-derived target nomination pipelines (Open Targets Platform), and pharma drug-discovery workflows.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|---------------------|
| L2G score (high-confidence) | >= 0.5 | Open Targets default; gradient-boosted classifier calibrated against curated gold standards |
| L2G score (suggestive) | >= 0.2 | Open Targets exploratory threshold |
| MAGMA gene-wide p | < 2.5e-6 (Bonferroni 0.05 / 20k genes) | Standard genome-wide gene-level significance |
| coloc PP.H4 (triangulation) | >= 0.7 | Open Targets / common practice; >= 0.8 for stringent |
| PoPS score (high-confidence) | Top decile per locus | Weeks 2023 Nat Genet 55:1267; threshold is relative per-locus rank, NOT an absolute cutoff. Absolute PoPS score is scale-dependent on trait polygenicity, so an absolute "PoPS >= 0.5" rule is incorrect across traits |
| ABC enhancer-gene score | >= 0.02 (standard) or >= 0.04 (stringent) | Fulco 2019; cross-reference atac-seq/enhancer-gene-linking |
| ENCODE-rE2G probability | >= 0.5 (binarised) | Gschwind 2023 |
| cS2G aggregate score | >= 0.5 per SNP-gene allocation | Gazal 2022; heritability-calibrated aggregator |
| Distance to TSS (regulatory window) | <= 100 kb (default); <= 500 kb (liberal); <= 1 Mb (absolute) | Convention; Mountjoy 2021. Beyond 100 kb distance ceases to be a reliable single feature |
| MAGMA gene-window | 35 kb upstream + 10 kb downstream | FUMA default; balances regulatory capture vs gene-dense dilution |
| Fine-mapping PIP (causal variant) | > 0.5 (suggestive); > 0.9 (strong) | Convention (cross-reference causal-genomics/fine-mapping) |
| Multi-evidence concordance | >= 3 of 6 streams | Operational rule from Open Targets Genetics and Mountjoy 2021 |
| Single-cell eQTL panel size | >= 200 donors per cell type | Below this, per-cell-type eQTL discovery underpowered |

## MAGMA Gene-Based and Gene-Set Pipeline

**Goal:** Compute gene-level p-values from GWAS summary statistics and test gene sets (e.g. MSigDB pathways) for enrichment.

**Approach:** Pre-format the SNP-to-gene annotation (per-gene SNP membership using a configurable window); run gene-based analysis with `--gene-results`; downstream, test gene sets via `--set-annot`. MAGMA's lambda-correction handles LD via the reference panel.

```bash
# Step 1: SNP-to-gene annotation using a 35kb upstream + 10kb downstream window (FUMA default)
magma --annotate window=35,10 \
    --snp-loc gwas.snploc \
    --gene-loc NCBI37.3.gene.loc \
    --out annot_35_10

# Step 2: Gene-based association (raw GWAS sumstats; multi-model approach)
magma --bfile g1000_eur \
    --pval gwas.pval ncol=N \
    --gene-annot annot_35_10.genes.annot \
    --out gene_step

# Step 3: Gene-set enrichment via competitive testing (recommended over self-contained)
magma --gene-results gene_step.genes.raw \
    --set-annot msigdb_v7.5_C2.gmt \
    --out gene_set_step

# Inspect: gene_step.genes.out (per-gene Z, p); gene_set_step.gsa.out (per-set p)
```

The `--gene-annot` window choice is the dominant methodological lever; 35kb upstream + 10kb downstream is the FUMA recommendation but is not universally accepted. Sensitivity over 0+0, 35+10, and 50+50 is good practice for high-stakes reports.

## Open Targets L2G via GraphQL

**Goal:** Query pre-computed L2G scores for a study and locus without re-running the integrative pipeline.

**Approach:** Query the Open Targets GraphQL endpoint with a study ID and lead variant; parse per-gene scores.

### Open Targets Platform vs Genetics Portal (2024 Consolidation)

In 2024 Open Targets Genetics was merged into the Open Targets Platform GraphQL API at `api.platform.opentargets.org/api/v4/graphql`. The legacy Genetics endpoint (`api.genetics.opentargets.org/graphql`) still responds but is deprecated; new pipelines should target the Platform API. The schema also changed: the Platform exposes `credibleSet(studyLocusId)` with `l2GPredictions` (target, score, SHAP per-feature explainability), whereas the legacy schema exposed `studyLocus2GeneTable` with `yProbaModel` and per-component sub-scores.

Legacy (Genetics, deprecated):

```graphql
query L2G_legacy($studyId: String!, $variantId: String!) {
  studyLocus2GeneTable(studyId: $studyId, variantId: $variantId) {
    rows {
      gene { symbol }
      yProbaModel
      yProbaDistance
      yProbaMolecularQTL
      hasColoc
    }
  }
}
```

Modern (Platform, recommended):

```graphql
query L2G_modern($studyId: String!) {
  credibleSet(studyLocusId: $studyId) {
    l2GPredictions {
      rows {
        target { approvedSymbol }
        score
        features { name value shapValue }
        shapBaseValue
      }
    }
  }
}
```

```python
import requests
import pandas as pd

resp = requests.post('https://api.platform.opentargets.org/api/v4/graphql',
                     json={'query': '...modern L2G query...',
                           'variables': {'studyId': 'GCST006464_locus_42'}})
preds = resp.json()['data']['credibleSet']['l2GPredictions']['rows']
l2g_df = pd.json_normalize(preds).sort_values('score', ascending=False)
```

The headline `score` (Platform) corresponds to `yProbaModel` (legacy). Platform `features[].shapValue` values replace the legacy `yProba*` sub-scores and explain what drove the prediction. Genes whose SHAP is dominated by the distance feature but minimal on QTL or chromatin features are distance-only candidates; trust the integrated `score` as primary.

## PoPS Polygenic Priority Score

**Goal:** Add a distance-orthogonal similarity-based prior to ranked gene candidates.

**Approach:** Run MAGMA genome-wide to produce gene Z; feed gene Z plus a curated gene-feature matrix (pathway membership + co-expression + PPI) to PoPS ridge (L2-penalized) regression. Per-gene priority scores are produced; per-locus relative ranking is informative.

```bash
# PoPS requires the gene-feature matrix and MAGMA gene Z output
# Download features and gene_annot from FinucaneLab/pops releases

python pops.py \
    --gene_annot_path gene_annot.txt \
    --feature_mat_prefix PoPS_features_full \
    --control_features_path control.features \
    --num_feature_chunks 10 \
    --magma_prefix gene_step \
    --out_prefix pops_out

# Output pops_out.preds: per-gene priority score
# Output pops_out.coefs: per-feature ridge coefficients (interpretation)
```

PoPS is biology-agnostic; the feature matrix encodes biology. Bias in the features (e.g. cancer-pathway-heavy gene sets for a non-cancer trait) propagates to the output; verify feature coverage matches the trait.

## Multi-Evidence Integration: Concordance Scoring

**Goal:** Combine fine-mapping, coloc, ABC, L2G, PoPS, and distance into a per-locus per-gene concordance score; flag high-confidence candidates.

**Approach:** Per-locus, gather evidence per candidate gene from each method; score each evidence stream as pass / fail at the canonical threshold; sum the passing streams; report >= 3 passing as high-confidence.

```r
library(dplyr)

# Per-locus candidate gene table; one row per (locus, gene)
candidates <- read.table('locus_candidates.tsv', header = TRUE, sep = '\t')

# Score each evidence stream against canonical thresholds
candidates <- candidates %>%
  mutate(
    pass_finemap = pip_top_variant > 0.5 & credible_set_purity > 0.5,
    pass_coloc = coloc_pph4 >= 0.7,
    pass_distance = distance_to_tss <= 100000,
    pass_pops = pops_decile_rank == 1,
    pass_l2g = l2g_score >= 0.5,
    pass_abc = abc_score >= 0.02 | encode_re2g_score >= 0.5,
    concordance = pass_finemap + pass_coloc + pass_distance +
                  pass_pops + pass_l2g + pass_abc,
    confidence_tier = case_when(
      concordance >= 5 ~ 'near_certain',
      concordance >= 4 ~ 'strong',
      concordance >= 3 ~ 'high',
      concordance >= 2 ~ 'suggestive',
      TRUE ~ 'associational_only'))

# Report
candidates %>%
  filter(concordance >= 3) %>%
  arrange(desc(concordance), desc(l2g_score)) %>%
  select(locus, gene, concordance, confidence_tier, l2g_score, pops_decile_rank, coloc_pph4)
```

Concordance scoring is conservative; some real causal genes score 2-of-6 because not all evidence streams are available at all loci. Report the per-stream availability alongside the concordance score so readers know whether failure reflects negative evidence or absent evidence.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| L2G top gene != nearest gene | Distal regulation; L2G integrates fine-mapping + coloc + chromatin | Trust L2G; verify with ABC / ENCODE-rE2G if epigenome data exists |
| L2G top gene != PoPS top gene | Orthogonal methods; one is locus-feature-based, one is similarity-based | Both valid signals; concordance is high-confidence, discordance is investigate-further |
| MAGMA top gene different from L2G | MAGMA is window-based; L2G integrates distal regulation | MAGMA is a baseline; L2G is the more comprehensive scorer |
| Two genes both pass L2G >= 0.5 at the locus | Multi-effector locus or LD-tied co-regulated genes | Run FUSION.post_process.R (conditional/joint analysis by default) or coloc.susie for independence; functional validation needed |
| L2G high, no eQTL coloc | Driver may be a coding variant or chromatin-mediated regulation absent from eQTL panel | Check VEP for coding consequence; check pQTL panels (Sun 2018 Nature; UKB-PPP) |
| FUMA top gene != Open Targets L2G top gene | Different feature weighting and FUMA web-platform version may lag OT pipeline | Both informative; document which version of each |
| ABC predicts gene A, eQTL coloc predicts gene B | Cell-type mismatch in epigenome panel vs eQTL panel | Match cell type; if not possible, prefer the panel matched to causal tissue (per LDSC-SEG) |
| All methods agree | Strong concordance | Report as high-confidence; consider for CRISPRi validation |
| All methods fail at this locus | No causal gene resolvable from current data | Report as unresolved; flag for matched-tissue eQTL or epigenome data |

**Operational rule:** Concordance across L2G + PoPS + (coloc OR ABC) is the publication-grade triangulation standard. Single-method calls are weak; require >= 3 of 6 orthogonal evidence streams. Disagreement between L2G and PoPS at a locus often points to (a) a multi-effector locus, (b) a method-feature artefact, or (c) genuine biological complexity. Report both, with their per-locus ranks.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| MAGMA error `--gene-loc file required` | Path mismatch or wrong reference build | Provide hg19 or hg38 gene location file matching the GWAS build |
| All MAGMA genes show p ~ 1 | LD reference panel mismatch (ancestry or sample size) | Use 1000G EUR g1000_eur reference for EUR GWAS; verify with `--gene-results` summary |
| Open Targets API returns empty | Study not in the OT release OR wrong study ID format | Verify study ID via OT study search; some studies require GCST prefix |
| PoPS output has all genes scoring near 0 | Feature matrix mis-aligned to gene_annot OR MAGMA gene Z scale wrong | Verify column ordering in feature matrix; check MAGMA `genes.raw` parsing |
| cS2G gene allocation differs from L2G | Different aggregation strategies; cS2G heritability-calibrated, L2G classifier-trained | Both informative; cS2G is a per-SNP aggregator, L2G is per-(locus, gene) |
| ABC predicts a passenger gene | Wrong cell-type Hi-C or H3K27ac in ABC input | Verify cell-type-matched epigenome; cross-reference atac-seq/enhancer-gene-linking |
| FUMA SNP2GENE job stuck | Web platform queue OR exceeded GWAS size limit | Re-submit; reduce sumstats to genome-wide-significant loci if oversize |
| L2G high at HLA region | Method is not designed for long-range LD | Exclude HLA from genome-wide V2G summaries; report separately |
| Multiple candidate genes at locus, no clear winner | Multi-effector or LD-tied co-regulation | Allow multi-gene reporting; functional validation needed |
| PoPS top gene is a passenger | Feature matrix bias (pathway over-representation) | Inspect PoPS coefficients; verify feature relevance to trait |

## Tool Install Notes

- **MAGMA**: Pre-compiled binary from cncr.nl/research/magma. Linux / Mac / Windows. Ships as `magma` CLI; needs PLINK bfile reference (e.g. 1000G g1000_eur).
- **FUMA**: Web platform at fuma.ctglab.nl/snp2gene. No local install. Requires user account; SNP2GENE jobs run server-side with current reference annotations.
- **Open Targets Platform (current)**: GraphQL at `api.platform.opentargets.org/api/v4/graphql`. Query L2G via `credibleSet(studyLocusId)` -> `l2GPredictions { rows { target, score, features } }`. Recommended for new pipelines.
- **Open Targets Genetics (legacy, deprecated)**: GraphQL at `api.genetics.opentargets.org/graphql`. Python `pip install gentropy` (official Open Targets) or `pip install otargenpy` (community GraphQL wrapper) OR direct GraphQL queries via `requests`. Genetics Portal was consolidated into the integrated Open Targets Platform in 2024; legacy endpoint still responds but new work should target the Platform.
- **PoPS**: `git clone https://github.com/FinucaneLab/pops`. Python; ships with feature matrix download instructions. Pre-built feature matrix at the releases page.
- **cS2G**: Pre-computed gene scores downloadable from zenodo.org/records/7754032 (cS2G_UKBB.zip / cS2G_1000GEUR.zip). No install; lookup table.
- **DEPICT**: `git clone https://github.com/perslab/depict`. Java + Python; legacy method, see Pers 2015.
- **FLAMES**: Recent (Schipper M et al 2025 Nat Genet 57:323); check the publication's GitHub for the current install path.
- **INQUISIT**: Originally for breast cancer (Fachal 2020 Nat Genet 52:56); see the paper's supplementary methods for adaptation to other traits.
- **ABC**: `git clone https://github.com/broadinstitute/ABC-Enhancer-Gene-Prediction`. Python; see atac-seq/enhancer-gene-linking for the full pipeline.
- **ENCODE-rE2G**: `git clone https://github.com/EngreitzLab/ENCODE_rE2G`. Snakemake; see atac-seq/enhancer-gene-linking.

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Was the nearest gene just taken?" | No. L2G + PoPS concordance reported per locus; ABC / ENCODE-rE2G applied when matched epigenome exists. Nearest-gene flagged as low-confidence fallback only. |
| "Was L2G + PoPS concordance tried?" | Yes. Both scores reported per (locus, gene) candidate; multi-stream concordance score (>= 3 of 6 streams) gates high-confidence calls. |
| "Was the eQTL panel tissue-relevant?" | Causal tissue identified via stratified LDSC / LDSC-SEG; TWAS run in that tissue; cross-tissue check via S-MultiXcan. |
| "Was ABC / ENCODE-rE2G applied?" | Applied when matched ATAC + H3K27ac (+ Hi-C optional) available; otherwise flagged as limitation. Cross-reference atac-seq/enhancer-gene-linking. |
| "Was CRISPRi-FlowFISH validation considered?" | Cross-referenced against Fulco 2019 K562 catalog (>3,500 pairs); Gasperini 2019 at-scale catalog (~75,000 pairs); Schraivogel 2020 TAP-seq / targeted Perturb-seq screen in K562. |
| "What MAGMA window was used?" | Window stated explicitly. FUMA 35+10 vs MAGMA-native 0+0 distinction made; sensitivity over 0+0, 35+10, 50+50 reported for high-stakes loci. |

## References

- Mountjoy E, Schmidt EM, Carmona M, Schwartzentruber J, Peat G et al 2021 Nat Genet 53:1527 (Open Targets L2G; locus-to-gene integrative scorer)
- Ghoussaini M, Mountjoy E, Carmona M, Peat G, Schmidt EM et al 2021 Nucleic Acids Res 49:D1311 (Open Targets V2G/Genetics)
- de Leeuw CA, Mooij JM, Heskes T, Posthuma D 2015 PLoS Comput Biol 11:e1004219 (MAGMA gene-based association)
- Watanabe K, Taskesen E, van Bochoven A, Posthuma D 2017 Nat Commun 8:1826 (FUMA SNP2GENE integrative annotation)
- Gazal S, Weissbrod O, Hormozdiari F, Dey KK, Nasser J et al 2022 Nat Genet 54:827 (cS2G combined SNP-to-gene)
- Weeks EM, Ulirsch JC, Cheng NY, Trippe BL, Fine RS et al 2023 Nat Genet 55:1267 (PoPS Polygenic Priority Score)
- Fulco CP, Nasser J, Jones TR, Munson G, Bergman DT et al 2019 Nat Genet 51:1664 (ABC enhancer-gene linking; CRISPRi-FlowFISH validation)
- Nasser J, Bergman DT, Fulco CP, Guckelberger P, Doughty BR et al 2021 Nature 593:238 (ABC genome-wide application)
- Gschwind AR, Mualim KS, Karbalayghareh A, Sheth MU, Dey KK et al 2023 bioRxiv 2023.11.09.563812 (ENCODE-rE2G; preprint)
- Pers TH, Karjalainen JM, Chan Y, Westra HJ, Wood AR et al 2015 Nat Commun 6:5890 (DEPICT)
- Fachal L, Aschard H, Beesley J, Barnes DR, Allen J et al 2020 Nat Genet 52:56 (INQUISIT breast-cancer V2G)
- Finucane HK, Reshef YA, Anttila V, Slowikowski K, Gusev A et al 2018 Nat Genet 50:621 (LDSC-SEG tissue prioritisation)
- Yazar S, Alquicira-Hernandez J, Wing K, Senabouth A, Gordon MG et al 2022 Science 376:eabf3041 (OneK1K sc-eQTL)
- Stacey D, Fauman EB, Ziemek D, Sun BB, Harshfield EL et al 2019 Nucleic Acids Res 47:e3 (ProGeM)
- Sun BB, Maranville JC, Peters JE, Stacey D, Staley JR et al 2018 Nature 558:73 (pQTL panel)
- Vosa U, Claringbould A, Westra HJ, Bonder MJ, Deelen P et al 2021 Nat Genet 53:1300 (eQTLGen reference)
- Mancuso N, Freund MK, Johnson R, Shi H, Kichaev G et al 2019 Nat Genet 51:675 (FOCUS for gene-level fine-mapping; cross-reference TWAS skill)
- Schaid DJ, Chen W, Larson NB 2018 Nat Rev Genet 19:491 (fine-mapping review)
- Barbeira AN, Pividori M, Zheng J, Wheeler HE, Nicolae DL, Im HK 2019 PLoS Genet 15:e1007889 (S-MultiXcan; joint per-tissue TWAS via PC decomposition)
- Hu Y, Li M, Lu Q, Weng H, Wang J et al 2019 Nat Genet 51:568 (UTMOST; cross-tissue weight imputation TWAS)
- Gasperini M, Hill AJ, McFaline-Figueroa JL, Martin B, Kim S et al 2019 Cell 176:377 (at-scale CRISPRi-FlowFISH enhancer-gene screen, ~75,000 pairs)
- Schraivogel D, Gschwind AR, Milbank JH, Leonce DR, Jakob P et al 2020 Nat Methods 17:629 (TAP-seq / targeted Perturb-seq enhancer-gene screen in K562)
- Amemiya HM, Kundaje A, Boyle AP 2019 Sci Rep 9:9354 (ENCODE blacklist v2; HLA-region exclusion reference)

## Related Skills

- causal-genomics/fine-mapping - Variant-level credible sets feeding L2G and concordance scoring
- causal-genomics/colocalization-analysis - coloc PP.H4 as one of the six evidence streams
- causal-genomics/transcriptome-wide-association - TWAS gene-level association and FOCUS fine-mapping
- causal-genomics/mendelian-randomization - cis-eQTL MR as orthogonal causal evidence
- causal-genomics/mediation-analysis - Downstream gene-mediated trait effects
- causal-genomics/proteome-mr-drug-target - pQTL-based effector-gene nomination for drug targets
- atac-seq/enhancer-gene-linking - ABC and ENCODE-rE2G enhancer-gene predictions feeding distal-regulation evidence
- atac-seq/atac-peak-calling - Generating enhancer candidates from matched-tissue ATAC
- atac-seq/deep-learning-atac - chromBPNet variant-effect prediction as 7th evidence stream for non-coding effector inference
- gene-regulatory-networks/coexpression-networks - Gene co-expression features feeding PoPS
- gene-regulatory-networks/scenic-regulons - TF-target regulons as supporting evidence at regulatory loci
- pathway-analysis/go-enrichment - Pathway context for effector-gene candidates
- population-genetics/association-testing - Upstream GWAS summary-statistic generation
- variant-calling/variant-annotation - Coding-consequence annotation for effector-gene variants
- workflows/gwas-pipeline - End-to-end GWAS pipeline producing effector-gene-prioritisation input
<!-- END FILE: causal-genomics/effector-gene-prioritization/SKILL.md -->

## 子目录：causal-genomics/fine-mapping

<!-- BEGIN FILE: causal-genomics/fine-mapping/SKILL.md -->
---
name: bio-causal-genomics-fine-mapping
description: Resolves GWAS associations to candidate causal variants and credible sets via SuSiE, susie_rss, FINEMAP, CAVIAR, DAP-G, PAINTOR, PolyFun, SuSiEx, MultiSuSiE, and FOCUS. Use when narrowing a GWAS lead SNP to a 95 percent credible set, choosing between in-sample and reference LD, calibrating non-sparse loci with SuSiE-inf or FINEMAP-inf, integrating functional priors via PolyFun, fine-mapping across ancestries with SuSiEx, diagnosing LD mismatch via estimate_s_rss and kriging_rss, handling HLA or long-range LD, or feeding credible sets into coloc.susie for colocalization.
tool_type: r
primary_tool: susieR
---

## Version Compatibility

Reference examples tested with: susieR 0.12.27+, coloc 5.2.3+, FINEMAP 1.4.2+, PolyFun (head of `omerwe/polyfun` 2024), PAINTOR V3.0, SuSiEx (head of `getian107/SuSiEx`), DAP-G (head of `xqwen/dap`), pyfocus 0.8+, R 4.3+, PLINK 1.9 / 2.0.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('susieR')` then `?susie_rss` to confirm argument names (e.g., `prior_weights` vs `prior_variance` semantics)
- CLI: `finemap --help`, `SuSiEx --help`, `PAINTOR --help`, `dap-g --help` to confirm flags
- Python: `polyfun.py --help`

If a call throws an error about an argument that no longer exists, introspect the installed function and adapt rather than retrying.

# Fine-Mapping

**"Narrow my GWAS locus to the variants likely to be causal"** -> Fit a sparse Bayesian regression that propagates LD into posterior inclusion probabilities (PIPs) and credible sets, then validate that credible sets correspond to physically reasonable haplotypes given the LD reference.

- R (summary statistics + LD): `susieR::susie_rss(z, R, n, L=10)` + `estimate_s_rss` LD diagnostic
- R (individual-level genotypes): `susieR::susie(X, y, L=10)`
- CLI (shotgun stochastic search): `finemap --sss --in-files master.z --n-causal-snps 5 --prob-tol 0.001`
- CLI (cross-ancestry joint): `SuSiEx --sst_file=eur.sst,eas.sst --n_gwas=N1,N2 --ref_file=eur.bim,eas.bim --ld_file=eur_ld,eas_ld --chr_col=1,1 --snp_col=2,2 --bp_col=3,3 --a1_col=4,4 --a2_col=5,5 --eff_col=6,6 --se_col=7,7 --pval_col=8,8 --chr=<chr> --bp=<start,end> --out_dir=<dir> --out_name=<name>` (column-number flags and `--ld_file` are required; populations are assigned by the ORDER of the comma-separated `--sst_file`/`--n_gwas`/`--ref_file`/`--ld_file` lists, not a `--pop` flag; see `SuSiEx --help`)
- Python (functional priors): `polyfun.py --compute-h2-L2` -> per-SNP priors -> susie_rss with `prior_weights=`
- Python (TWAS fine-mapping): `focus finemap` on gene-level Z-scores

Fine-mapping is a Bayesian model selection problem; LD is not noise but structured prior information. Most failure modes trace back to one of three issues: (a) LD reference mismatched to the GWAS sample; (b) the sparse-effects prior being wrong for the locus (polygenic background); or (c) too small an L cap. The `estimate_s_rss()` lambda and `kriging_rss()` per-SNP diagnostic catch (a) before downstream credible sets are reported.

## Algorithmic Taxonomy

| Tool | Model | Input | Strength | Fails when |
|------|-------|-------|----------|------------|
| SuSiE / susie_rss (Wang 2020 JRSSB 82:1273; Zou 2022 PLoS Genet) | Iterative Bayesian sum-of-single-effects (IBSS), variational | Individual-level (X, y) or (z, R, n) | Fast; native PIP + credible sets; pluggable priors; default in modern pipelines | Reference LD mismatched to GWAS sample; locus dominated by polygenic background; >L true effects |
| SuSiE-inf / FINEMAP-inf (Cui 2024 Nat Genet 56:162) | SuSiE + infinitesimal random-effect component | (z, R, n) | Calibrated credible sets when locus is non-sparse (polygenic shoulder around a sparse causal); recommended for biobank-scale GWAS | Very small loci with truly sparse architecture (over-conservative); slower convergence |
| FINEMAP (Benner 2016 Bioinformatics 32:1493) | Shotgun stochastic search over causal configurations | .z + .ld + .master files | Exact Bayes factors at small k; widely cited | Slow at L > 5; binary install only (christianbenner.com); same LD-mismatch fragility as SuSiE |
| CAVIAR (Hormozdiari 2014 Genetics 198:497) | Exhaustive enumeration up to k causals | (z, R) | Exact posterior at small k | Combinatorial explosion beyond k=6; legacy method largely superseded by SuSiE |
| DAP-G (Wen 2016 AJHG 98:1114) | Deterministic posterior approximation with adaptive scan | SBAMS format; TORUS for enrichment priors | Fast at QTL scale (whole-transcriptome); pairs with TORUS hierarchical priors | SBAMS format is awkward; less ubiquitous tooling |
| PAINTOR (Kichaev 2014 PLoS Genet 10:e1004722) | EM with binary functional annotations | (z, R, A) per locus | Locus-level functional priors; multi-trait variant | Single-trait mode often matched by PolyFun + SuSiE; slower than SuSiE |
| PolyFun + SuSiE/FINEMAP (Weissbrod 2020 Nat Genet 52:1355) | Stratified LDSC genome-wide -> per-SNP prior_weights | GWAS sumstats + pre-baked baseline-LF | Most powerful single-trait functional prior; >20% more high-PIP (PIP>0.95) variants in simulations, >32% in real UK Biobank traits (Weissbrod 2020) | Requires matched-ancestry baseline-LF; runs in two stages |
| SuSiEx (Yuan 2024 Nat Genet 56:1841) | Joint cross-ancestry SuSiE; shared causal, population-specific LD | Per-pop sumstats + per-pop LD reference | Smaller credible sets than per-ancestry meta or marginal fine-mapping; principled when causal variants are shared | Trans-ethnic heterogeneity violated (population-specific causals); ancestry must be cleanly assigned |
| MultiSuSiE (Rossen 2025 Nat Genet) | Cross-ancestry SuSiE variant; flexible heterogeneity | Per-pop sumstats + per-pop LD | Similar to SuSiEx; alternative implementation | Same as SuSiEx; newer, less battle-tested |
| FOCUS / MA-FOCUS (Mancuso 2019 Nat Genet 51:675) | Probabilistic TWAS fine-mapping over gene models | TWAS Z-scores + gene LD (predicted expression) | Identifies likely causal gene among co-regulated TWAS hits; cross-ancestry MA-FOCUS variant | Requires pre-computed expression weights (e.g., FUSION/PrediXcan); gene-level rather than variant-level inference |

Methodology evolves; verify the latest susieR vignette and the SuSiE-inf paper before locking on a single method. Wang Lab maintains susieR; the IBSS algorithm is stable but argument semantics (e.g., `prior_weights` vs `prior_variance`) have changed across versions.

## Decision Tree by Experimental Scenario

| Scenario | Recommended workflow | Why |
|----------|---------------------|-----|
| Individual-level genotypes available (UKB, in-house cohort) | `susie(X, y, L=10)` | In-sample LD is exact; no mismatch fragility |
| Summary statistics only, ancestry matches reference panel | `susie_rss(z, R, n, L=10)` + `estimate_s_rss` diagnostic | Standard external-LD pattern; verify lambda < 0.05 |
| Single-locus EUR GWAS, sparse architecture | susie_rss with L=10, baseline functional priors optional | Most-common setting; SuSiE default works |
| Locus with strong polygenic shoulder (biobank scale) | SuSiE-inf (Cui 2024) | Adds infinitesimal component; calibrates non-sparse PIPs |
| Multi-ancestry GWAS (EUR + EAS + AFR) | SuSiEx with per-pop sumstats and LD | Joint inference shrinks credible sets; per-ancestry meta loses LD information |
| Locus with > 5 expected independent signals (HLA, lipid loci) | susie_rss with L=20-30 | Default L=10 caps signal count; HLA needs extension |
| TWAS hits with co-regulated genes | FOCUS / MA-FOCUS | Variant-level fine-mapping cannot distinguish co-regulated gene candidates |
| Want functional priors (coding, conserved, regulatory) | PolyFun -> susie_rss with `prior_weights` | Genome-wide SLDSC priors sharpen PIPs more than locus-level annotations |
| QTL fine-mapping (eQTL, sQTL, caQTL) at transcriptome scale | DAP-G + TORUS OR susie_rss per gene | DAP-G is built for QTL throughput; SuSiE works per gene |
| Low-N QTL (GTEx tissue panel, N < 1000) | susie_rss with `coverage = 0.9` (or 0.8); document choice | Default 0.95 returns very wide credible sets at low power; report the relaxed coverage explicitly in methods |
| HLA region (chr6:28-34 Mb) or chr8 inversion | Specialized workflow: stratify haplotypes; consider HLA-specific imputation; or exclude | LD structure is too complex; standard methods unreliable |
| Cross-feed into colocalization | susie_rss -> coloc.susie() | Modern coloc operates on credible sets, not single SNPs |

## Critical LD Diagnostic Block (susie_rss)

**Goal:** Detect LD reference mismatch before reporting credible sets.

**Approach:** `estimate_s_rss()` quantifies the global Z-score / LD inconsistency as a scalar; `kriging_rss()` identifies individual SNPs whose Z-scores are inconsistent with the LD reference (typically genotyping errors, strand flips, or wrong reference panel).

```r
library(susieR)
s_hat <- estimate_s_rss(z = z_scores, R = ld_matrix, n = N)
# s_hat is the inferred scale of LD inconsistency.
# Source: susieR vignette "Diagnostic for summary statistic"; Zou 2022 PLoS Genet.
# Rule of thumb: s_hat < 0.05 acceptable; 0.05-0.10 marginal; > 0.10 refit or change LD reference.

cond_z <- kriging_rss(z = z_scores, R = ld_matrix, n = N)
# cond_z$conditional_dist returns per-SNP expected vs observed z; flag |z_obs - z_exp| > 3
# Common cause: strand flip, allele coding mismatch, or single-SNP imputation error.

# If diagnostic fails: refit with explicit scale parameter to absorb LD mismatch
fit <- susie_rss(z = z_scores, R = ld_matrix, n = N, L = 10, estimate_residual_variance = TRUE)
```

Skipping this block is the dominant cause of irreproducible fine-mapping. Always run before reporting credible sets.

## Per-Tool Failure Modes

### LD reference mismatch (most common)

**Trigger:** External LD matrix from 1000 Genomes / UK Biobank reference used for a GWAS conducted on a different cohort or ancestry mix.

**Mechanism:** Z-scores reflect the GWAS sample's LD; the reference R does not. The susie_rss likelihood depends on `z' R^{-1} z` being consistent with the modeled effects, and inconsistency manifests as spurious credible sets containing tag SNPs from the reference but not from the discovery cohort.

**Symptom:** `estimate_s_rss()` lambda > 0.05; `kriging_rss()` flags many SNPs with `|z_obs - z_exp| > 3`; credible sets contain physically distant SNPs (anti-correlated in LD with the lead) or include all SNPs at the locus.

**Fix:** Use in-sample LD whenever the cohort genotypes are accessible (compute with `plink --r2 square` on the GWAS samples themselves). When only summary statistics are available, ancestry-stratify the LD reference exactly (e.g., 1000G EUR FIN+CEU+GBR+IBS+TSI for a Northern European GWAS, not full EUR). For mixed-ancestry GWAS, fine-map per ancestry then meta-analyze, or move to SuSiEx.

### Non-sparse architecture (biobank scale)

**Trigger:** Locus with one strong signal plus hundreds of weakly associated SNPs (polygenic shoulder); typical at biobank scale.

**Mechanism:** Vanilla SuSiE assumes a sparse sum-of-single-effects prior. With polygenic background, the model misallocates effects, producing inflated credible sets or many small spurious ones. Cui 2024 (Nat Genet 56:162) showed PIPs from SuSiE in this regime are systematically miscalibrated.

**Symptom:** Many small credible sets (5-15 per locus); replication in independent cohorts fails for non-lead credible sets; PIP distribution has a heavy tail.

**Fix:** Use SuSiE-inf or FINEMAP-inf (Cui 2024). These augment the sum-of-single-effects with an infinitesimal random-effect component that absorbs polygenic background. Source: github.com/FinucaneLab/fine-mapping-inf.

### L too small

**Trigger:** Locus with > 5 independent signals (HLA region, APOC1/APOE, LPA, IL6R region for some traits).

**Mechanism:** SuSiE assumes at most L independent effects. When the true number exceeds L, some signals are absorbed into existing components, distorting PIPs and credible sets for the captured signals.

**Symptom:** `length(fit$sets$cs)` equals L (all L slots used); credible set purity for higher-indexed sets is low (`fit$sets$purity[,'min.abs.corr'] < 0.5`); fits with larger L change top-PIP variants.

**Fix:** Increase L iteratively (L=10 -> 20 -> 30) until `length(fit$sets$cs)` < L (susieR auto-prunes unsupported effects so the returned CS count is the effective L). For HLA, start at L=30. The cost is mostly computational, not statistical: SuSiE prunes unused slots, so L=30 is safe when L=10 was right.

### prior_weights vs prior_variance confusion (PolyFun integration)

**Trigger:** Passing PolyFun output to susie_rss with `prior_variance=polyfun_priors` (wrong argument).

**Mechanism:** `prior_variance` in susie_rss is a single scalar (or vector of length L) for the per-effect variance, NOT a per-SNP probability. `prior_weights` is the per-SNP causal probability vector (sums to ~1). Passing PolyFun's per-SNP prior to `prior_variance` is silently accepted but applies a numerically nonsensical per-effect variance.

**Symptom:** PIPs nearly identical to the uniform-prior fit; functional annotations appear to have no effect.

**Fix:** Use `prior_weights = polyfun_priors$SNPVAR` (the PolyFun output column is uppercase `SNPVAR`; R is case-sensitive). Verify with `?susie_rss` in the installed version. Reference: github.com/omerwe/polyfun README, Weissbrod 2020 supplementary methods.

### Credible-set misinterpretation

**Trigger:** Reporting per-variant PIP without distinguishing "in credible set" from "high PIP".

**Mechanism:** The 95 percent credible-set guarantee is `P(causal variant in set) >= 0.95`. Per-variant PIPs within a set do not necessarily sum to 1 across all variants, and PIPs across overlapping sets can double-count posterior mass.

**Symptom:** Reporting "the top PIP variant" when the credible set is wide (size > 50); claiming a single variant is causal when the set contains 30 high-LD SNPs.

**Fix:** Always report (a) number of credible sets, (b) size of each set, (c) purity (`fit$sets$purity[,'min.abs.corr']`), (d) the top PIP variant within the set as the candidate lead. The credible set is the unit of inference; the top PIP variant is a candidate, not a conclusion.

### Cross-ancestry with single-ancestry LD

**Trigger:** Multi-ancestry meta-analyzed GWAS, then susie_rss with EUR LD.

**Mechanism:** Meta-analysis z-scores reflect a weighted mix of population LD structures; no single-population LD matrix matches.

**Fix:** Move to SuSiEx (joint cross-ancestry SuSiE; Yuan 2024). Per-ancestry fine-mapping followed by manual merging loses the shared-causal-variant information that SuSiEx exploits.

### Case-control GWAS passing Ntotal instead of Neff

**Trigger:** Passing `n = N_total` to `susie_rss()` for case-control GWAS derived from logistic regression.

**Mechanism:** susie_rss expects the effective sample size that determined the standard errors. For case-control logistic regression, `Neff = 4 / (1/Ncase + 1/Ncontrol)`; when cases are rare, total N can exceed Neff by 25x or more. Passing Ntotal rescales z-scores into a regime SuSiE never sees and makes the implied prior variance wrong.

**Symptom:** PIPs systematically biased; credible sets either too narrow (PIPs collapse to a single SNP that is not robust) or too wide (PIPs flatten); replication poor; sometimes z-score scale warnings from susieR.

**Fix:** `Neff = 4 / (1/Ncase + 1/Ncontrol)`. Example: Ncase=5000, Ncontrol=495000 -> Neff ~= 19,800 (NOT 500,000). For quantitative traits from linear regression, `n = N_total` is correct. Reference: Privé F et al 2022 HGG Adv 3:100136 (`bigsnpr` documents Neff handling); Willer 2010 Bioinformatics (METAL Neff convention).

### Allele Harmonization with the LD Reference

**Trigger:** Effect allele in GWAS sumstats differs from the coding/A1 allele in the LD reference panel; or palindromic SNPs (A/T, C/G) carried without strand resolution.

**Mechanism:** susie_rss treats `z` and `R` as defined on the same allele coding. If the effect allele is swapped relative to the LD-reference A1, the sign of z is wrong and the LD row/column for that SNP is implicitly flipped. SNPs matching by rsID can silently swap alleles between sumstats and reference, breaking the `z' R z` consistency the model relies on.

**Symptom:** `estimate_s_rss` lambda inflated despite ancestry-matched panel; `kriging_rss` flags many SNPs with `|z_obs - z_exp| > 3` clustered at SNPs where reference A1 != GWAS effect allele; credible sets pick up tag-only SNPs anti-correlated with the lead.

**Fix:** Harmonize before fitting:

```r
harmonize_z_to_ref <- function(z, gwas_a1, gwas_a2, ref_a1, ref_a2) {
    palindromic <- (gwas_a1 == 'A' & gwas_a2 == 'T') | (gwas_a1 == 'T' & gwas_a2 == 'A') |
                   (gwas_a1 == 'C' & gwas_a2 == 'G') | (gwas_a1 == 'G' & gwas_a2 == 'C')
    flip <- (gwas_a1 == ref_a2) & (gwas_a2 == ref_a1)
    z[flip] <- -z[flip]
    drop <- palindromic | !((gwas_a1 == ref_a1 & gwas_a2 == ref_a2) | flip)
    list(z = z, keep = !drop)
}
```

Drop palindromic SNPs at MAF > 0.42 (ambiguous strand); or resolve via external strand info (TopMed, 1000G strand files). `TwoSampleMR::harmonise_data()` offers an alternative implementation. See causal-genomics/colocalization-analysis for an equivalent harmonize helper used downstream.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| SuSiE finds 3 credible sets, FINEMAP finds 1 | FINEMAP's stochastic search did not converge OR SuSiE absorbed background into spurious sets | Increase FINEMAP `--n-iterations`; check SuSiE purity (sets with purity < 0.5 are spurious) |
| SuSiE PIPs much sharper than FINEMAP | susie_rss assumes single residual variance; FINEMAP marginalizes over noise | Both can be correct; report the intersection of high-PIP variants from both as primary candidates |
| PolyFun + SuSiE collapses 10-variant credible set to 1 | Functional priors are doing real work (coding variant in set) | Verify with `prior_weights` plot; if priors are coding-specific the result is interpretable |
| SuSiEx credible set excludes the EUR top-PIP variant | EUR signal is tag, true causal shared across ancestries lies elsewhere | Trust SuSiEx if both populations have well-powered GWAS; verify with conditional analysis |
| HLA gives 50-variant credible set in every method | HLA LD structure cannot be fine-mapped by linear methods | Use HLA-specific imputation (HIBAG, SNP2HLA) and haplotype-level analysis |

**Operational rule:** For high-confidence reporting, require that (a) `estimate_s_rss()` lambda < 0.05; (b) at least one credible set has purity > 0.5 (`min_abs_corr >= 0.5`, equivalent to r2 >= 0.25); (c) the lead PIP variant within that set is reproduced by an independent method (FINEMAP, SuSiEx, or in-sample SuSiE if reference-LD was used). Anything failing these three is exploratory.

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|-------------------|
| Credible set coverage (well-powered GWAS) | 0.95 (default) | Wang 2020 JRSSB; standard convention |
| Credible set coverage (low-N eQTL, GTEx tissue) | 0.9 or 0.8 | At N < 1000, default 0.95 returns very wide CS; document choice in methods |
| Credible set purity (rare-variant fine-mapping) | min_abs_corr >= 0.1 | LD genuinely sparse; relax to retain signal |
| Credible set purity (default common-variant) | min_abs_corr >= 0.5 (r2 >= 0.25) | susieR default; below this the set is LD-confounded |
| Credible set purity (publication-strict) | min_abs_corr >= 0.7 | Stringent claim; rare in practice |
| PIP suggestive | > 0.5 | Convention; "more likely than not causal among set" |
| PIP strong | > 0.9 | Convention; high-confidence single candidate |
| PIP very strong | > 0.95 | Convention; near-certain candidate within credible set |
| L (default cap) | 10 | susieR default; sufficient for most non-HLA loci |
| L (HLA / complex loci) | 20-30 | Empirical; HLA hosts > 10 independent signals for many traits |
| `n` for case-control susie_rss | Neff = 4/(1/Ncase + 1/Ncontrol), NOT Ntotal | Privé F et al 2022 HGG Adv 3:100136; matches the SE scale of logistic-regression sumstats |
| `estimate_s_rss` lambda acceptable | < 0.05 | susieR vignette; > 0.10 indicates serious LD mismatch |
| `kriging_rss` per-SNP flag | |z_obs - z_exp| > 3 | susieR vignette; flag for manual review |
| Locus window (default) | +/- 500 kb from sentinel | Conventional; covers most LD blocks |
| Locus window (conditional-p floor) | Extend until conditional -log10(p) < 4 | Avoids truncating a secondary signal whose conditional evidence leaks into the window edge |
| Locus window (long-range LD) | 5+ Mb or stratify | HLA chr6:25-35Mb, chr8 inversion chr8:8.1-11.9Mb hg38, chr17 H1/H2 inversion |
| FINEMAP `--n-causal-snps` | 5 | Default; raise for HLA |
| FINEMAP `--prob-tol` | 0.001 | Convergence tolerance; rarely needs change |

## Functional Priors with PolyFun

**Goal:** Use genome-wide stratified LDSC heritability to weight per-SNP causal priors, sharpening PIPs at coding, conserved, and regulatory variants.

**Approach:** Run PolyFun once genome-wide to estimate per-SNP h2 from the baseline-LF annotation set; extract per-SNP causal prior; pass to susie_rss as `prior_weights`.

```bash
# Parametric route: L2-regularized S-LDSC writes per-SNP priors directly (--no-partitions)
polyfun.py --compute-h2-L2 --no-partitions \
    --output-prefix polyfun_h2 \
    --sumstats gwas_munged.sumstats \
    --ref-ld-chr UKB_baseline_LF/baselineLF2.2.UKB. \
    --w-ld-chr UKB_baseline_LF/weights.UKB.
# Per-SNP priors written to polyfun_h2.<CHR>.snpvar_ridge_constrained.gz

# Non-parametric route (finer, optional): drop --no-partitions above, then add an
# intermediate LD-score step before re-estimating binned per-SNP h2:
#   polyfun.py --compute-ldscores --output-prefix polyfun_h2 ...
#   polyfun.py --compute-h2-bins --output-prefix polyfun_h2 --sumstats gwas_munged.sumstats --w-ld-chr UKB_baseline_LF/weights.UKB.
```

```r
library(susieR)
priors <- read.table('polyfun_h2.6.snpvar_ridge_constrained.gz', header = TRUE)
priors <- priors[match(gwas_df$SNP, priors$SNP), ]
prior_w <- priors$SNPVAR / sum(priors$SNPVAR, na.rm = TRUE)

fit <- susie_rss(z = z_scores, R = ld_matrix, n = N, L = 10,
                 prior_weights = prior_w)
```

UKB baseline-LF priors are pre-computed EUR-only at `data.broadinstitute.org/alkesgroup/UKBB_LD/` for hg19 and hg38. For EAS, AFR, or SAS GWAS, the EUR weights are NOT valid: functional-prior fine-mapping in a non-EUR ancestry requires baseline-LF annotations matched to that ancestry. For ancestries lacking matched baseline-LF (admixed, under-represented), accept reduced power and run uniform-prior susie_rss; applying EUR weights to non-EUR sumstats produces miscalibrated PIPs that look sharper than reality.

### Manual Coding-Variant Priors Without PolyFun

For postdocs without PolyFun infrastructure or with single-locus inputs, manual annotation-based priors are a reasonable approximation (Hutchinson 2020 Hum Mol Genet 29:R81). As a stated convention, coding variants get ~10x uniform weight; broadly conserved variants ~5x (binned by CADD-PHRED quantile).

```r
build_manual_priors <- function(vep_df, cadd) {
    w <- rep(1, nrow(vep_df))
    w[vep_df$Consequence %in% c('missense_variant', 'stop_gained', 'splice_donor_variant',
                                'splice_acceptor_variant', 'frameshift_variant')] <- 10
    w[cadd >= quantile(cadd, 0.95, na.rm = TRUE)] <- pmax(w[cadd >= quantile(cadd, 0.95, na.rm = TRUE)], 5)
    w / sum(w)
}
fit <- susie_rss(z = z_scores, R = ld_matrix, n = Neff, L = 10, prior_weights = build_manual_priors(vep, cadd))
```

Report the prior construction explicitly; reviewers will ask whether the prior was tuned post hoc.

## Cross-Ancestry Fine-Mapping with SuSiEx

**Goal:** Jointly fine-map a locus across multiple ancestries assuming shared causal variants but population-specific LD.

**Approach:** Per-ancestry summary statistics + per-ancestry LD reference; SuSiEx runs a joint SuSiE model with population-specific R matrices. SuSiEx assigns populations by the ORDER of the comma-separated `--sst_file`/`--n_gwas`/`--ref_file`/`--ld_file` lists (there is no `--pop` flag); keep all four lists in the same population order.

```bash
SuSiEx \
    --sst_file=eur_sumstats.txt,eas_sumstats.txt,afr_sumstats.txt \
    --n_gwas=500000,200000,80000 \
    --ref_file=1000G_EUR,1000G_EAS,1000G_AFR \
    --ld_file=eur_ld,eas_ld,afr_ld \
    --out_dir=susiex_out \
    --out_name=locus1 \
    --chr=6 --bp=30000000,31000000 \
    --chr_col=1,1,1 --snp_col=2,2,2 --bp_col=3,3,3 \
    --a1_col=4,4,4 --a2_col=5,5,5 --eff_col=6,6,6 \
    --se_col=7,7,7 --pval_col=8,8,8 \
    --level=0.95
```

The output includes per-population PIPs and a joint credible set. Credible sets from SuSiEx are typically 2-5x smaller than EUR-only susie_rss when AFR is included, because AFR shorter LD blocks resolve EUR-tagged regions.

## FINEMAP CLI Pattern

**Goal:** Independent confirmation via shotgun stochastic search.

**Approach:** Build .z, .ld, and master files; run FINEMAP with `--sss` and parse the .snp and .cred outputs.

```bash
# .z file format: snp chromosome position allele1 allele2 maf beta se
# .ld file: square LD matrix, space-separated, no header

cat > locus.master <<'EOF'
z;ld;snp;config;cred;log;n_samples
locus.z;locus.ld;locus.snp;locus.config;locus.cred;locus.log;500000
EOF

finemap --sss \
    --in-files locus.master \
    --n-causal-snps 5 \
    --prob-tol 0.001 \
    --n-iterations 100000 \
    --n-convergence 5000

# Parse:
# locus.snp -> per-variant prob (PIP), log10bf
# locus.cred -> credible sets at increasing causal counts
# locus.config -> top configurations
```

FINEMAP and SuSiE agree when sparsity holds; disagreement often reveals non-sparse loci that need SuSiE-inf.

## Coloc.susie Integration

**Goal:** Test colocalization between two traits using credible sets, not single SNPs.

**Approach:** Fit susie_rss separately per trait; pass both `susie` objects to `coloc.susie`; per-credible-set colocalization probabilities are returned.

```r
library(coloc)

fit_trait1 <- susie_rss(z = z1, R = ld_matrix, n = N1, L = 10)
fit_trait2 <- susie_rss(z = z2, R = ld_matrix, n = N2, L = 10)

coloc_res <- coloc.susie(fit_trait1, fit_trait2)
# coloc_res$summary: per-credible-set PP.H4 (shared causal probability)
print(coloc_res$summary)
```

PP.H4 > 0.8 per credible set is the conventional shared-causal threshold; weaker thresholds suggest distinct or conditional signals. See causal-genomics/colocalization-analysis.

## HLA and Long-Range LD: When to Stop

The HLA region (chr6:28-34 Mb), chromosome 8 inversion (chr8:8-12 Mb), and a handful of other extended LD blocks violate the assumptions of every fine-mapping method.

**Symptoms of irrecoverable LD structure:** Credible sets contain 30+ SNPs at low purity even with L=30; SuSiE-inf credible sets remain wide; `kriging_rss` flags hundreds of SNPs.

**Options:**
- Stratify by classical HLA allele (HIBAG, SNP2HLA imputation) and test allelic series
- Conditional analysis on the lead variant before fine-mapping the residual
- Exclude the region from genome-wide fine-mapping summaries and report separately
- For chr8 inversion: stratify by inversion genotype if known

Document the caveat in any methods section; standard PIPs at HLA are not interpretable as causality estimates.

## TWAS Fine-Mapping (FOCUS) -- delegated

Variant-level fine-mapping cannot distinguish causal genes among co-regulated TWAS hits. FOCUS / MA-FOCUS extend fine-mapping to the predicted-expression level; see causal-genomics/transcriptome-wide-association for the full FOCUS workflow and reconciliation with variant-level credible sets.

## Required Reporting Schema for Fine-Mapping

Every locus reported should carry these columns; missing fields are the most common reviewer complaint.

| Column | Description |
|--------|-------------|
| locus_id | Locus identifier (chr:start-end or sentinel rsID) |
| method | susie_rss / FINEMAP / PAINTOR / SuSiEx / SuSiE-inf |
| L_used | `sum(!fit$sets$pruned)` (effective L; not just the cap passed in) |
| n_credible_sets | Number of returned credible sets at the chosen coverage |
| cs_size | Variants per credible set |
| cs_purity_min / cs_purity_mean | min and mean `fit$sets$purity[,'min.abs.corr']` per set |
| top_pip_snp | Lead variant in each credible set |
| top_pip | Posterior inclusion probability of top_pip_snp |
| lambda_s | `estimate_s_rss` diagnostic for the locus |
| kriging_outlier_count | Count of SNPs with `|z_obs - z_exp| > 3` |
| ld_panel | 1KG-EUR / UKB-EUR / in-sample / TopMed |
| prior_source | uniform / PolyFun-EUR / PolyFun matched-ancestry baseline-LF / manual coding-variant |
| coverage | 0.95 default; 0.9 or 0.8 documented for low-N |
| n_effective | Sample size passed to susie_rss (Neff for case-control) |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "In-sample vs reference LD?" | In-sample preferred when cohort genotypes available; if reference, report `estimate_s_rss` lambda < 0.05 plus `kriging_rss` outlier count |
| "Credible-set purity?" | `min_abs_corr >= 0.5` (r2 >= 0.25) default; reported per set; relaxed only with explicit rationale for rare-variant fine-mapping |
| "Is L set high enough?" | If returned CS count < L cap: OK (susieR auto-prunes); otherwise raise L. HLA needs L=20-30 |
| "Why not SuSiE-inf?" | Polygenic-shoulder test: count SNPs with marginal -log10(p) > 4 outside the lead credible set; > 50 indicates a polygenic shoulder and SuSiE-inf (Cui 2024) should be used |
| "Why no functional priors?" | PolyFun applied (or manual coding-variant prior used) and reported; if uniform, justify (low-N, mismatched-ancestry baseline-LF) |
| "Credible set has 50 SNPs -- is that fine-mapping?" | Acknowledged as imprecise; reported alongside diagnostics; cross-trait colocalization or functional fine-mapping (PolyFun, MPRA, allelic series) recommended for resolution |
| "Was Neff used for case-control?" | Yes: `Neff = 4/(1/Ncase + 1/Ncontrol)`; report the value used |
| "Allele harmonization?" | Yes: flipped z when GWAS effect allele differs from reference A1; palindromic SNPs at MAF > 0.42 dropped |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `IBSS algorithm did not converge` warning | L too small OR LD mismatch | Increase L; run `estimate_s_rss`; check ancestry match |
| Credible set contains all SNPs at locus | LD reference matches discovery poorly; `s_hat` > 0.1 | Switch to in-sample LD or stratify reference ancestry |
| PIPs identical to GWAS p-value rank | Effectively no LD information used; check LD matrix orientation | Verify SNP order in z and R match exactly; check for transposed R |
| Negative eigenvalues in LD matrix | Numerical PSD violation from finite-precision storage | Add small ridge: `R <- R + diag(1e-4, nrow(R))`; or use `Matrix::nearPD` |
| `pip` all ~ 1/p (uniform) | Convergence failure OR all effects pruned | Check `fit$converged`; raise L; check Z scale |
| FINEMAP `Error: SNP names do not match` | .z and .ld SNP order differ | Ensure both are sorted identically; pass matched .snp file |
| Coloc.susie returns NULL | One trait has zero credible sets | Verify both fits succeeded; lower coverage to 0.9 if signal is weak |
| SuSiEx output empty | Per-population lists misaligned with reference panels | Verify `--sst_file`/`--ref_file`/`--ld_file` are in the same population order; check `--bp` window |
| PolyFun priors do not change PIPs | Passed to `prior_variance` instead of `prior_weights` | Read susieR docs; use `prior_weights=` |

## References

- Wang G, Sarkar A, Carbonetto P, Stephens M 2020 J R Stat Soc B 82:1273 (SuSiE / IBSS)
- Zou Y, Carbonetto P, Wang G, Stephens M 2022 PLoS Genet 18:e1010299 (susie_rss for summary statistics)
- Cui R, Elzur RA, Kanai M, Ulirsch JC, Weissbrod O et al 2024 Nat Genet 56:162 (SuSiE-inf / FINEMAP-inf for non-sparse loci)
- Benner C, Spencer CC, Havulinna AS, Salomaa V, Ripatti S, Pirinen M 2016 Bioinformatics 32:1493 (FINEMAP)
- Hormozdiari F, Kostem E, Kang EY, Pasaniuc B, Eskin E 2014 Genetics 198:497 (CAVIAR)
- Wen X, Lee Y, Luca F, Pique-Regi R 2016 AJHG 98:1114 (DAP-G)
- Kichaev G, Yang WY, Lindstrom S, Hormozdiari F, Eskin E et al 2014 PLoS Genet 10:e1004722 (PAINTOR)
- Weissbrod O, Hormozdiari F, Benner C, Cui R, Ulirsch J et al 2020 Nat Genet 52:1355 (PolyFun + functional priors)
- Yuan K, Longchamps RJ, Pardinas AF, Yu M, Chen TT et al 2024 Nat Genet 56:1841 (SuSiEx cross-ancestry)
- Rossen J, Shi H, Strober BJ, Zhang MJ, Kanai M, McCaw ZR, Liang L, Weissbrod O, Price AL 2025 Nat Genet 58:67 (MultiSuSiE; doi:10.1038/s41588-025-02450-5)
- Mancuso N, Freund MK, Johnson R, Shi H, Kichaev G et al 2019 Nat Genet 51:675 (FOCUS for TWAS fine-mapping)
- Wallace C 2021 PLoS Genet 17:e1009440 (coloc.susie integration)
- Schaid DJ, Chen W, Larson NB 2018 Nat Rev Genet 19:491 (fine-mapping review)
- Hutchinson A, Asimit J, Wallace C 2020 Hum Mol Genet 29:R81 (fine-mapping review)

## Related Skills

- causal-genomics/colocalization-analysis - coloc.susie consumes susie_rss credible sets; equivalent harmonize helper
- causal-genomics/effector-gene-prioritization - Downstream gene-assignment from credible-set variants
- causal-genomics/transcriptome-wide-association - FOCUS / MA-FOCUS for gene-level fine-mapping
- causal-genomics/genomic-sem - Joint multi-trait fine-mapping when credible sets are shared across traits
- causal-genomics/mendelian-randomization - Fine-mapped variants as cis-instruments
- causal-genomics/pleiotropy-detection - Per-credible-set pleiotropy testing
- atac-seq/enhancer-gene-linking - ABC / ENCODE-rE2G linking credible-set variants to target genes
- population-genetics/linkage-disequilibrium - Constructing LD matrices for susie_rss
- population-genetics/association-testing - Upstream GWAS summary statistic generation
- workflows/gwas-pipeline - End-to-end GWAS pipeline producing fine-mapping input
- variant-calling/variant-annotation - Annotating credible-set variants with VEP / coding consequence
- pathway-analysis/go-enrichment - Downstream gene-level interpretation of credible-set targets
<!-- END FILE: causal-genomics/fine-mapping/SKILL.md -->

## 子目录：causal-genomics/genetic-correlation

<!-- BEGIN FILE: causal-genomics/genetic-correlation/SKILL.md -->
---
name: bio-causal-genomics-genetic-correlation
description: Estimates bivariate genetic correlation (rg) between traits from GWAS summary statistics or individual-level genotypes using cross-trait LDSC, HDL, LAVA, rho-HESS, GREML-bivariate, Popcorn, and HDL-L. Use when quantifying shared genetic architecture between two traits, screening MR validity before causal inference, distinguishing global from locus-level rg, estimating trans-ancestry rg, separating partial from full causation via LCV gcp, or producing a STROBE-MR-compliant cross-trait sensitivity battery. Cross-trait LDSC intercept absorbs sample overlap and is NOT a bias; HDL is biased under sample overlap above ~5%. High rg between exposure and outcome motivates CHP-aware MR sensitivity (CAUSE, LHC-MR).
tool_type: mixed
primary_tool: ldsc
---

## Version Compatibility

Reference examples tested with: LDSC v1.0.1+ (Python 3; prefer `abdenlab/ldsc-python3` v2.0.0 -- `belowlab/ldsc` v3.0.1 README states the `--h2 / --rg / --h2-cts` CLI is broken; use Docker `jtb114/ldsc:latest` for the belowlab fallback; original `bulik/ldsc` is Python 2.7 unmaintained since 2019), HDL 1.4.0+ (R; GitHub `zhenin/HDL`), LAVA 0.1.0+ (R; GitHub `josefin-werme/LAVA`), HESS 0.5.4+ (Python; huwenboshi/hess), Popcorn 1.0+ (Python; brielin/Popcorn), GCTA 1.94+ (GREML-bivariate), baselineLD_v2.2 / eur_w_ld_chr LD-score panels from alkesgroup.broadinstitute.org/LDSCORE, UKB-array SVD eigen reference for HDL.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `python -c 'import <module>; help(<module>)'`
- R: `packageVersion('<pkg>')` then `?function_name`
- CLI: `<tool> --version` then `<tool> --help`

If code throws an LD-score "category not found" error, an HDL reference-panel mismatch, or a LAVA locus-ID lookup failure, introspect the installed LD-score column headers and the supplied partitioning file rather than retrying with default flags.

# Genetic Correlation

**"Estimate the genetic correlation between two traits from GWAS summary statistics"** -> Decompose the bivariate genetic architecture into a single global rg (cross-trait LDSC, HDL), per-locus local rg (LAVA, rho-HESS, HDL-L), or cross-population rg (Popcorn). Genetic correlation is the central cross-trait statistic in causal genomics: it quantifies shared etiology, motivates CHP-aware MR sensitivity when high, gates LCV's gcp partial-causation parameter, and feeds into multi-trait analysis frameworks (MTAG, GenomicSEM). Tool choice is a decision about the **regime** (sumstats vs individual-level; global vs local; same-ancestry vs trans-ancestry) and the **sample-overlap structure** between input GWAS.

- CLI (LDSC, robust to overlap): `ldsc.py --rg trait1.sumstats.gz,trait2.sumstats.gz --ref-ld-chr eur_w_ld_chr/ --w-ld-chr eur_w_ld_chr/ --out rg`
- R (HDL, lower variance, requires independent samples): `HDL.rg(gwas1.df, gwas2.df, LD.path = 'UKB_array_SVD_eigen90_extraction', N0 = 0)`
- R (LAVA, local rg per locus): `process.input() -> run.univ() -> run.bivar(input, locus_id)` over ~2495 LDetect-derived loci
- CLI (rho-HESS, locus-level): `hess.py --local-rhog t1.sumstats.gz t2.sumstats.gz --bfile <ref> --partition <part>.bed --chrom <chr>`
- CLI (Popcorn, trans-ancestry): `popcorn fit -v 1 --cfile cross_pop_scores.txt --sfile1 pop1.txt --sfile2 pop2.txt out`

## Algorithmic Taxonomy

| Method | Model | Input | Output | Strength | Fails when |
|--------|-------|-------|--------|----------|------------|
| Cross-trait LDSC (Bulik-Sullivan 2015 Nat Genet 47:1236) | Bivariate LD-score regression; off-diagonal absorbs rg, intercept absorbs sample overlap | Sumstats + ancestry-matched LD scores | rg, SE, intercept (overlap proxy) | Robust to sample overlap (intercept absorbs it without biasing rg); fast; calibrated EUR | Mean chi-square < 1.02 in either trait (underpowered); non-EUR sumstats with EUR LD scores |
| HDL (Ning 2020 Nat Genet 52:859) | High-Definition Likelihood; eigen-decomposition of full LD with closed-form variance | Sumstats + UKB-array SVD eigen reference (EUR N=336k) | rg, SE | ~60% lower variance than LDSC; equivalent to ~2.5x sample size; preferred when both GWAS truly independent | Sample overlap > 5% biases likelihood; only public reference panel is EUR UKB-array |
| LAVA (Werme 2022 Nat Genet 54:274) | Semi-parametric local genetic correlation per locus; PC-projected SNP effects under a local null | Sumstats + LDetect partitioning (~2495 loci) | Per-locus univariate h2 + bivariate rg + p-value | Detects heterogeneous rg masked by global cancellation; conditional + partial rg supported | Locus has too few SNPs (< 50) or low local h2 (univariate p > 0.05 in either trait); LD reference mismatch |
| rho-HESS (Shi 2017 AJHG 101:737) | Quadratic form on LD-projected effect estimates per locus | Sumstats + LDetect partition + LD reference | Per-locus rho_g + bivariate local rg | Earliest locus-level rg method; complements LAVA | Locus < 1000 SNPs; LD ref must match in-sample structure |
| HDL-L (Li Y et al 2025 Nat Genet) | HDL likelihood applied to local windows | Sumstats + windowed LD reference | Per-window local rg | Lower variance than rho-HESS at locus level | Same sample-overlap caveat as HDL; reference-panel coverage limited |
| GREML-bivariate (Lee 2012 Bioinformatics 28:2540) | Joint REML on bivariate GRM | Individual-level genotypes + both phenotypes | rg + SE | Gold standard at individual level; better precision than sumstats methods | Needs individual-level data on overlapping individuals OR carefully matched two-cohort; population stratification leaks |
| Popcorn (Brown 2016 AJHG 99:76) | Cross-population genetic effect (rho_ge) and impact (rho_gi) correlation under MAF-LD model | Sumstats per population + cross-population LD scores | Trans-ancestry rg + per-pop h2 | Quantifies shared causal architecture across ancestries | Effective N per population < 5000; cross-population LD score reference mismatched to GWAS ancestry |
| Cross-pop causal-effect rg (Galinsky KJ et al 2019 Genet Epidemiol 43:180) | Cross-population genetic correlation of causal effect sizes | Sumstats per population + cross-population reference | Trans-ancestry causal-effect rg + SE | Estimates cross-population correlation of causal effects; complements Popcorn | Same data-volume limit as Popcorn |
| GenomicSEM `ldsc()` (Grotzinger 2019 Nat Hum Behav 3:513) | LDSC wrapper feeding into SEM | Multiple sumstats | Genetic covariance matrix + multivariable SEM | Multi-trait extension of LDSC; common-factor and bifactor models | Same per-pair limits as LDSC; SEM identification problems |
| SUPERGNOVA (Zhang Y et al 2021 Genome Biol 22:262) | LD-block local rg via eigen-decomposition of the LD matrix | Sumstats + LD-block partition | Per-locus rg + p; orthogonal philosophy from LAVA | Different LD partitioning than LDetect; useful as triangulation against LAVA | Same chi-square floor as LDSC; non-EUR coverage limited |
| KGGSEE gene-based conditional heritability (Miao L et al 2023 AJHG) | Gene-based conditional heritability via effective heritability estimation (EHE) | Sumstats + gene annotation | Per-gene conditional h2 | Java pipeline; gene-level conditional heritability | NOT a local-rg method -- answers a different question than LAVA |

Methodology evolves; benchmark consensus shifts. Verify against the alkesgroup LDSC tutorial (current as of release), Werme 2022 LAVA paper + GitHub, and Speed 2020 *Nat Genet* model-comparison work before locking a primary method. When a claim depends on the model assumption (e.g. enrichment in shared loci), report at least two methods (e.g. LDSC global + LAVA local).

## Cross-Trait LDSC Intercept: Sample Overlap is Absorbed, Not a Bias

**The most common postdoc-level misreading:** Treating a non-zero cross-trait LDSC intercept as evidence of bias in the rg estimate.

The bivariate LDSC regression has the form:
`E[Z1 Z2] = sqrt(N1 N2) * rg * h2-product / M * LD_score + rho_overlap`

The intercept (`rho_overlap`) ABSORBS the contribution of sample overlap (correlated trait residuals on shared individuals). The slope (which carries rg) is unbiased even when overlap is non-zero. A non-zero intercept is the expected signature of sample overlap and is informative (it estimates phenotypic correlation among overlapping individuals), but it does NOT indicate that rg is contaminated.

**Operational rule:** Report the intercept alongside rg. When intercept is non-zero, document the overlap inferred (intercept = rho_phenotypic * sqrt(N_shared / N1 / N2) approximately) but do not discount rg. HDL, in contrast, assumes truly independent samples and does become biased above ~5% overlap; switch to LDSC under any non-trivial overlap.

## HDL Bias Under Sample Overlap

**The mirror image trap:** Running HDL on two GWAS that share controls or come from the same biobank.

HDL maximizes a likelihood that assumes independence of the two trait residuals after marginalizing genetics. With sample overlap, the residual correlation is non-zero and the likelihood is misspecified; bias is typically toward the rg estimate that corresponds to phenotypic correlation in the overlapping subset.

**Operational rule:** Use HDL only when sample overlap < 5%. When in doubt about overlap (e.g. two UKB-derived GWAS), compute LDSC intercept first; if intercept is materially non-zero, switch to LDSC for the primary rg estimate.

## Relationship to MR Causal Inference

Genetic correlation between an exposure and an outcome is a screening statistic, not a causal claim. High |rg| has three biological explanations:

| Explanation | Manifestation |
|-------------|----------------|
| Direct causation X -> Y | All causal SNPs of X feed through to Y; rg reflects mediated covariance |
| Shared heritable confounder (CHP) | A latent factor causes both; rg captures the shared variance with no direct edge |
| Reverse causation Y -> X | Symmetric structure; rg cannot resolve direction |

LCV's `gcp` parameter (O'Connor & Price 2018 Nat Genet 50:1728) attempts to distinguish partial from full causation: `gcp = 0` is pure correlation (no causation in tested direction), `gcp = 1` is full causation, `0 < gcp < 1` is partial causation. LCV uses the LDSC-style bivariate moments and is complementary to instrument-based MR.

**Operational rule for any MR analysis where |rg| > 0.3:** The IVW + Egger + MR-PRESSO triple is insufficient because all three are blind to CHP (Morrison 2020 Nat Genet 52:740). Add CAUSE (if sig SNPs >= 100) or LHC-MR. See causal-genomics/pleiotropy-detection for the full CHP-aware battery.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Standard EUR-EUR rg from sumstats | Cross-trait LDSC | Robust to sample overlap via intercept; standard ENCODE-equivalent default |
| Truly independent EUR samples, want maximum precision | HDL | ~60% lower variance than LDSC; equivalent to 2.5x sample size |
| Suspect heterogeneous rg across genome (e.g. neuropsychiatric pair with weak global rg) | LAVA local rg | Detects loci of shared etiology hidden by global cancellation |
| Locus-level rg with explicit LD partitioning | rho-HESS (or LAVA) | LAVA is newer and better-supported; rho-HESS remains the original framework |
| Cross-population (trans-ancestry) rg | Popcorn | Within-population LDSC fails cross-pop; Popcorn models ancestry-specific causal architecture |
| Individual-level genotypes available | GREML-bivariate (GCTA) | Better precision than sumstats; gold standard at individual level |
| MR validity check before running MR | LDSC rg + LCV gcp | If |rg| > 0.3 add CHP-aware MR sensitivity (CAUSE / LHC-MR) |
| Multi-trait modeling (many traits jointly) | GenomicSEM `ldsc()` | SEM extension of LDSC; common-factor, bifactor, and network models |
| Sumstats with mean chi-square < 1.02 | Defer; meta-analyze to ~50k effective N first | LDSC variance explodes below this; nothing else fixes underpower |
| Confirmatory after a single LAVA hit | LDSC global + bidirectional MR + colocalization | Triangulate; LAVA flags shared etiology but does not establish causation |

## Per-Method Failure Modes

### Cross-trait LDSC intercept misread as bias

**Trigger:** Reader (collaborator, reviewer) sees a non-zero LDSC intercept and reports the rg as "biased by sample overlap".

**Mechanism:** The bivariate LDSC model partitions covariance between traits into a slope (rg-driven, scales with LD score) and an intercept (overlap-driven, constant in LD score). The slope is what carries rg, and it remains unbiased regardless of intercept value (Bulik-Sullivan 2015 Nat Genet 47:1236, Methods). Confusing the intercept with bias on the slope is a routine misinterpretation.

**Symptom:** Reviewer comment requesting "correction for sample overlap" when LDSC was already used; collaborator suggesting switching to HDL because intercept is non-zero.

**Fix:** Report rg with SE and the intercept as a separate statistic; cite Bulik-Sullivan 2015 Methods explicitly; do NOT switch to HDL (which is the wrong direction since HDL is the method that breaks under overlap, not LDSC).

### HDL bias with sample overlap

**Trigger:** Running HDL on two GWAS that share > 5% of individuals (e.g. two UKB-derived GWAS, two MVP-derived GWAS, GWAS reusing controls).

**Mechanism:** HDL likelihood assumes independent trait residuals after marginalizing genetics. Overlap induces non-zero residual correlation; the likelihood is misspecified and the estimate is pulled toward phenotypic correlation in the shared subset (Ning 2020 Nat Genet 52:859 Supplement).

**Symptom:** HDL rg differs substantially from cross-trait LDSC rg; HDL CI is narrower than expected from N alone; LDSC intercept (which absorbs overlap) is materially non-zero.

**Fix:** Compute LDSC intercept first as an overlap diagnostic; if non-zero, switch to LDSC as primary. HDL remains valid only when the two GWAS draw from non-overlapping cohorts (verify by cohort identifier, not just by file source).

### Non-EUR ancestry mismatch with EUR LD scores

**Trigger:** Running LDSC on a non-EUR GWAS (or admixed sample) with the default `eur_w_ld_chr/` reference.

**Mechanism:** LD scores are ancestry-specific; mean LD per SNP differs across populations and bivariate moments use the wrong null. h2 and rg estimates are systematically biased; intercept can be inflated.

**Symptom:** LDSC ratio is unusually high (>0.2); per-chromosome estimates wildly heterogeneous; total h2 mismatches independent estimates from the same cohort.

**Fix:** Use ancestry-matched LD scores from alkesgroup (eas_w_ld_chr, afr_w_ld_chr) or compute custom LD scores from in-sample LD reference. For trans-ancestry rg, switch to Popcorn.

### Global rg masks local rg variation

**Trigger:** Two traits with biologically plausible shared etiology return global rg ~ 0 in cross-trait LDSC.

**Mechanism:** Global rg averages over the genome; loci with positive local rg can cancel against loci with negative local rg, particularly for traits with antagonistic pleiotropy (e.g. autoimmune vs infectious-disease susceptibility), or when shared etiology is confined to a small fraction of the genome.

**Symptom:** Well-powered (mean chi-square >> 1.02) global LDSC rg near zero with wide CI overlapping zero, while domain biology, prior co-occurrence studies, or shared-pathway analyses strongly suggest shared etiology.

**Fix:** Run LAVA over the standard ~2495 LDetect loci; per-locus Bonferroni-significant rg at any locus is evidence of localized shared etiology. Annotate hit loci with overlapping GWAS catalog signals and pathway/tissue enrichment.

### Cross-population rg below 1 even at causal level

**Trigger:** Computing rg between same-trait GWAS in two ancestries (e.g. EUR T2D vs EAS T2D).

**Mechanism:** Even when the trait has the same biological definition, causal variant identity and effect sizes can differ across populations due to gene-environment interaction, allele-frequency divergence, and population-specific epistasis. Popcorn 2016 demonstrated that rg(cross-pop) < 1 is common and biologically real, not a methodological artifact.

**Symptom:** Trans-ancestry rg point estimate around 0.6-0.9 with CI excluding 1 for a trait expected to be "the same disease".

**Fix:** Use Popcorn (within-pop LDSC is invalid for cross-pop rg); interpret rg(cross-pop) < 1 as quantifying population-specific architecture rather than as bias; report rho_ge (effect correlation) and rho_gi (impact correlation) separately.

### Same-Trait Cross-Cohort rg as Consistency Check

**Use case:** Meta-analysis QC -- two same-trait GWAS (e.g. UKB IBD vs FinnGen IBD) yield rg < 1 with CI excluding 1. This is distinct from the cross-population analog above (handled by Popcorn); here both cohorts are same-ancestry but different studies.

**Interpretation:** (a) population-substructure differences, (b) phenotype-definition heterogeneity (e.g. different ICD coding, self-report vs registry), (c) genuine biology (founder effects in isolates like FinnGen).

**Decision rule:** rg ~ 0.9-1.0 with CI overlapping 1 -> consistent enough to meta-analyze; rg ~ 0.7-0.9 -> moderate heterogeneity, consider sensitivity meta with random effects; rg < 0.7 -> re-examine phenotype definitions before meta-analyzing.

### Low chi-square mean (underpowered GWAS)

**Trigger:** Mean chi-square in either input GWAS is below 1.02 (heuristic LDSC threshold).

**Mechanism:** LDSC, HDL, and LAVA all depend on bivariate moments of Z-scores against LD score; weak signal means the slope is dominated by noise.

**Symptom:** LDSC rg SE > 0.2; intercept estimates fluctuate across chromosome; HDL convergence warnings; LAVA returns p > 0.05 at most loci.

**Fix:** Meta-analyze contributing cohorts to push effective N to ~50k or higher before running rg; if meta-analysis is not feasible, report rg as exploratory; do NOT switch methods to "salvage" power, the problem is upstream of method choice.

### LAVA univariate filter ignored

**Trigger:** Reporting LAVA bivariate rg at a locus where the univariate local h2 is non-significant in one or both traits.

**Mechanism:** LAVA's bivariate test is only valid at loci with detectable local heritability in BOTH traits. Without local h2 signal in at least one trait, the bivariate test is unidentified and can return spurious significant rg.

**Symptom:** LAVA bivariate p < 0.05 at loci where univariate h2 p > 0.05 for one trait; rg estimates near +/- 1 (boundary cases).

**Fix:** Filter loci on `univ.p < 0.05 / N_loci` (Bonferroni for ~2495 loci) in BOTH traits before running `run.bivar()`; report only at filtered loci. This is the documented LAVA workflow in Werme 2022 Supplement and the GitHub vignette.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| |rg| > 0.7 | Operational high correlation | Suggests strong shared genetic architecture; near-universal in pairs like MDD-anxiety or LDL-CHD |
| |rg| 0.3-0.7 | Operational moderate correlation | Common in psychiatric / cardiometabolic trait pairs; routine to flag for joint analysis |
| |rg| < 0.3 | Operational low correlation | Globally weak; may still harbor biologically meaningful local rg via LAVA |
| rg SE < 0.05 | Operational reliable estimate | Above this SE, point estimate is uncertain to 1 decimal place |
| HDL sample overlap < 5% | Ning 2020 Nat Genet (Supplement) | Above this, HDL likelihood is misspecified and biased |
| LDSC mean chi-square > 1.02 | LDSC documentation (Bulik-Sullivan 2015 tutorial) | Below this, LD-score regression is severely underpowered for h2 / rg |
| LAVA local p < 0.05 / N_loci | Werme 2022 Nat Genet 54:274 | Bonferroni for ~2495 LDetect loci; standard genome-wide local-rg correction |
| Popcorn rho_ge CI excludes 1 | Brown 2016 AJHG 99:76 | Evidence of population-specific causal architecture |
| LCV gcp != 0 (two-sided p < 0.05) | O'Connor & Price 2018 Nat Genet 50:1728 | Directional evidence of (partial) causation given non-zero rg |
| LDSC ratio < 0.2 | Bulik-Sullivan 2015 Methods | High ratio (intercept / chi-square - 1) indicates population stratification or model misfit |
| MR + rg sensitivity trigger | Operational | |rg| > 0.3 with a significant IVW estimate REQUIRES CHP-aware sensitivity (CAUSE / LHC-MR) |
| Conditional-rg LAVA covariate set | Werme 2022 | Up to 4 conditioning traits per `run.pcor()` call before identification fails |

## Cross-Trait LDSC: Standard Workflow

**Goal:** Estimate global rg from two GWAS summary statistics, robust to any sample overlap.

**Approach:** Munge each sumstats file (column harmonization + filters), supply ancestry-matched LD scores, run `--rg` mode; interpret slope (rg) and intercept (overlap proxy) separately.

```bash
# Step 1: munge each GWAS to LDSC format (harmonize columns, filter on MAF and INFO, restrict to HapMap3)
munge_sumstats.py \
    --sumstats trait1.tsv.gz \
    --N 250000 \
    --merge-alleles w_hm3.snplist \
    --out trait1.munged

munge_sumstats.py \
    --sumstats trait2.tsv.gz \
    --N 180000 \
    --merge-alleles w_hm3.snplist \
    --out trait2.munged

ldsc.py \
    --rg trait1.munged.sumstats.gz,trait2.munged.sumstats.gz \
    --ref-ld-chr eur_w_ld_chr/ \
    --w-ld-chr eur_w_ld_chr/ \
    --out rg_t1_t2

grep -A 11 'Summary of Genetic Correlation Results' rg_t1_t2.log
```

The log block reports rg, SE, p-value, h2 per trait, and `gcov_int` (genetic covariance intercept = phenotypic-correlation overlap proxy). When running rg of one base trait against many others, use comma-separated lists: `--rg base.sumstats.gz,t1.gz,t2.gz,t3.gz`.

## HDL: Lower-Variance rg for Independent Samples

**Goal:** Estimate global rg with ~60% lower variance than LDSC when the two GWAS draw from non-overlapping samples.

**Approach:** Format each GWAS as an HDL data frame; supply the UKB-array SVD eigen reference path; pass `N0` (overlapping sample count, 0 for independent).

```r
# remotes::install_github('zhenin/HDL/HDL')
library(HDL)

gwas1 <- data.frame(
    SNP = trait1$rsid,
    A1 = trait1$effect_allele,
    A2 = trait1$other_allele,
    N = trait1$N,
    Z = trait1$beta / trait1$se,
    b = trait1$beta,
    se = trait1$se
)

gwas2 <- data.frame(
    SNP = trait2$rsid,
    A1 = trait2$effect_allele,
    A2 = trait2$other_allele,
    N = trait2$N,
    Z = trait2$beta / trait2$se,
    b = trait2$beta,
    se = trait2$se
)

res <- HDL.rg(
    gwas1.df = gwas1,
    gwas2.df = gwas2,
    LD.path = 'UKB_array_SVD_eigen90_extraction',
    N0 = 0,  # number of overlapping individuals; 0 for independent cohorts. HDL corrects for overlap via N0 and is robust to its misspecification
    output.file = 'hdl_rg.txt'
)

print(res$rg)
print(res$rg.se)
print(res$P)
```

Pre-download the UKB SVD reference (`HDL_documentation.html` -> "How to obtain LD reference panel" link); `eigen90` is the UKB-array (genotyped-SNP) panel used here, while `eigen99` exists only for the imputed-variant panel -- match the panel to the SNP coverage of the input GWAS, not to a speed/precision setting. Do NOT run HDL when sample overlap is unknown or non-trivial; the wrapper does not warn.

## LAVA: Local Genetic Correlation Per Locus

**Goal:** Identify loci where two traits share genetic etiology, including loci hidden by global rg cancellation.

**Approach:** Process inputs once -> filter to loci with detectable univariate local h2 in BOTH traits -> run bivariate per-locus rg; apply Bonferroni for ~2495 loci.

```r
# remotes::install_github('josefin-werme/LAVA')
library(LAVA)

input <- process.input(
    input.info.file = 'input.info.txt',
    sample.overlap.file = 'sample.overlap.txt',
    ref.prefix = '1kg_EUR_chr',
    phenos = c('trait1', 'trait2')
)

loci <- read.loci('blocks_s2500_m25_f1_w200.GRCh37_hg19.locfile')

univ_results <- list()
biv_results <- list()
N_loci <- nrow(loci)

for (i in seq_len(N_loci)) {
    locus <- process.locus(loci[i, ], input)
    if (is.null(locus)) next  # no SNPs / no h2 / monomorphic
    univ <- run.univ(locus)
    univ_results[[i]] <- univ
    pass_univ <- all(univ$p < 0.05 / N_loci)  # Bonferroni on both traits
    if (!pass_univ) next
    biv_results[[i]] <- run.bivar(locus)
}

univ_df <- do.call(rbind, univ_results)
biv_df <- do.call(rbind, biv_results)
biv_df$padj <- p.adjust(biv_df$p, method = 'bonferroni', n = N_loci)
sig_loci <- subset(biv_df, padj < 0.05)
```

The standard LDetect partitioning files (~2495 EUR loci, ~1700 EAS, ~2700 AFR) are at the LAVA GitHub. Sample-overlap file (a per-pair phenotypic-correlation matrix; LDSC intercept is the standard proxy) protects LAVA from the same overlap bias that LDSC's intercept absorbs. For partial / conditional local rg, use `run.pcor(locus, target = c('phenoA', 'phenoB'), phenos = c('cond1', 'cond2', ...))` with up to 4 conditioning traits; the canonical multi-predictor regression alternative is `run.multireg()`.

## rho-HESS: Alternative Local rg

**Goal:** Per-locus bivariate rg using the HESS quadratic-form estimator; complementary to LAVA.

**Approach:** Estimate local h2 per trait first; then bivariate cross-trait estimator using LD-projected effect estimates per locus.

```bash
# Step 1: eigenvalues + projections for both traits (per chromosome; two sumstats SPACE-separated).
# --local-rhog auto-writes per-trait files (step1_trait1_*, step1_trait2_*) AND the covariance
# intermediates (step1_chrN.eig.gz, step1_chrN.prjprod.gz) under the shared --out prefix.
for chr in {1..22}; do
    hess.py \
        --local-rhog trait1.sumstats.gz trait2.sumstats.gz \
        --chrom $chr \
        --bfile 1kg_EUR_chr${chr} \
        --partition fourier_ls-chr${chr}.bed \
        --out step1
done

# Step 2: per-trait local h2 from the Step-1 outputs (MUST run before Step 3)
hess.py --prefix step1_trait1 --out step2_trait1
hess.py --prefix step1_trait2 --out step2_trait2

# Step 3: local genetic covariance / rg. --local-hsqg-est passes the Step-2 per-trait local h2,
# --num-shared is the overlap count, --pheno-cor the phenotypic correlation (any value when
# --num-shared 0). Auto-aggregates across all chromosomes; no per-chromosome loop here.
hess.py \
    --prefix step1 \
    --local-hsqg-est step2_trait1.txt step2_trait2.txt \
    --num-shared 0 \
    --pheno-cor 0 \
    --out step3
```

`--num-shared` is the number of overlapping individuals; set 0 only if truly independent. HESS partition files use the Berisa & Pickrell 2016 LD-block boundaries (`fourier_ls-*.bed`). LAVA has largely superseded HESS for new analyses, but rho-HESS remains in active use for replication / triangulation.

## Popcorn: Trans-Ancestry rg

**Goal:** Quantify shared causal architecture between two ancestries (e.g. EUR T2D vs EAS T2D) under a MAF-LD-aware model.

**Approach:** Compute cross-population LD scores once per ancestry pair; fit rg using sumstats from each population.

```bash
# Step 1: cross-population LD scores (one-time per ancestry pair)
popcorn compute -v 1 \
    --bfile1 1kg_EUR \
    --bfile2 1kg_EAS \
    --SNPs_to_store 20000 \
    --gen_effect \
    eur_eas_scores.txt

# Step 2: fit cross-population rg
popcorn fit -v 1 \
    --cfile eur_eas_scores.txt \
    --gen_effect \
    --sfile1 t2d_eur.sumstats.txt \
    --sfile2 t2d_eas.sumstats.txt \
    t2d_eur_eas_rg.txt
```

`--gen_effect` (which must be passed at BOTH `compute` and `fit`) selects the genetic-effect model and reports `rho_ge` (correlation of causal effect sizes); omitting it at both steps yields `rho_gi` (correlation of variant-level impacts, MAF-weighted). A single run reports one or the other, so run both modes to report both. When MAFs differ markedly across populations, `rho_ge` and `rho_gi` diverge; both are biologically meaningful and report-worthy. Effective N per population must be > ~5000 for stable estimates.

## Reconciliation Across Methods

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| LDSC rg and HDL rg agree (independent samples) | Both methods converging on true value | Report HDL as primary (lower SE); LDSC as sensitivity |
| LDSC rg substantially below HDL rg, LDSC intercept large | Sample overlap; HDL is biased toward phenotypic correlation | Report LDSC as primary; flag overlap; do not report HDL |
| Global LDSC rg ~ 0 but LAVA shows multiple Bonferroni-significant local rg | Locus-level cancellation in global average | Report both; the biology is "shared at specific loci, divergent overall" |
| LAVA significant but univariate h2 non-significant at hit locus | Spurious bivariate without identified local h2 signal | Filter univariate first; do NOT report bivariate at unidentified loci |
| Popcorn rho_ge << 1 across many trait pairs | Population-specific causal architecture | Real finding; report rho_ge alongside within-pop h2 |
| LDSC ratio > 0.2 | Population stratification or model misfit | Re-check ancestry; consider LD-score reference mismatch; report with caveat |
| LCV gcp ~ 0 with large rg | Genetic correlation without (partial) causation in either direction | Shared confounder hypothesis is preferred; do NOT report as causal |
| LCV gcp > 0 (significant) with large rg | Partial-to-full causation in tested direction | Combine with bidirectional MR + CHP-aware sensitivity; this is supportive but not sufficient |

**Operational rule for publication:** Report LDSC rg + intercept as primary global statistic; report HDL only if overlap is verified < 5%; complement with LAVA local rg whenever global rg is near zero or biology suggests heterogeneity; report LCV gcp when downstream MR is planned; trans-ancestry analyses require Popcorn (not within-population LDSC).

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| LDSC `category not found` after `--rg` | LD score column header mismatch (custom reference) | Inspect M_5_50 and `.l2.ldscore` headers; align with `--ref-ld-chr` prefix |
| LDSC ratio > 1 (negative h2 z-score) | Severe stratification or wrong LD-score ancestry | Switch to ancestry-matched reference; check for population structure |
| HDL convergence warning / NA SE | Reference panel mismatch or extreme overlap | Verify SVD eigen reference path; switch to LDSC when overlap suspected |
| LAVA `Insufficient SNPs at locus` for most loci | LD reference and partition file from different builds | Match GRCh37 vs GRCh38; align LD reference to partition file |
| LAVA bivariate rg = +/- 1 at boundary | Univariate filter not applied; locus is unidentified | Apply `univ$p < 0.05/N_loci` filter to BOTH traits before `run.bivar()` |
| Popcorn complains about MAF format | sumstats EAF column missing or NA | Provide EAF; do not impute from external reference (creates miscalibration) |
| HESS `--num-shared` defaulting to wrong value | Forgot to set explicitly; default 0 is independent | Always set explicitly; if unknown, use LDSC intercept to infer overlap |
| GenomicSEM `ldsc()` returns negative-definite covariance | Numerical instability with many traits | Inspect per-pair LDSC results; drop low-h2 traits; regularize |
| rg point estimate > 1 with CI overlapping 1 | Sampling variance; same-trait pair near identity | Report as "rg not distinguishable from 1"; constrained likelihood at the rg=1 boundary gives different SE -- LRT against H0: rg=1 is more precise than Wald CI |
| Binary-vs-continuous trait pair scale concern | Reviewer asks about liability-vs-observed scale propagation | LDSC rg is scale-invariant -- case-control h2 liability vs observed scale propagates equivalently into rg; no correction needed |

## Required Reporting for rg Analyses

| Component | Required |
|-----------|----------|
| Per-trait h2 + SE + intercept + mean chi-square | Yes |
| Bivariate rg + SE + p | Yes |
| gcov_int (cross-trait intercept) | Yes; non-zero under known overlap is expected, not bias |
| LD reference panel + ancestry | Yes |
| Method used (LDSC / HDL / LAVA / Popcorn) | Yes; rationale per Decision Tree |
| Local rg supplementary (LAVA) | If global rg null but biology suggests sharing |
| Sample-size: Neff per trait | Yes |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Sample overlap?" | LDSC: gcov_int reported; non-zero under known overlap is expected, NOT bias. HDL: only valid if independent (<5% overlap) |
| "Why LDSC not HDL?" | HDL gives lower variance but is biased > 5% overlap; LDSC is the conservative default |
| "Local vs global rg?" | If global rg modest but biology suggests sharing, LAVA (Werme 2022) reported as supplementary |
| "Cross-ancestry?" | Popcorn for trans-ancestry; rg < 1 in trans is real biology, not noise |
| "Does rg motivate CHP-MR?" | If `|rg| > 0.3`, CAUSE / LHC-MR sensitivity reported (cross-ref pleiotropy-detection) |
| "rg = 1 boundary?" | If CI includes 1, reported as "not distinguishable from rg=1"; constrained LRT alternative provided |

## Tool Installation Notes

```bash
# LDSC Python 3 fork (original bulik/ldsc is Python 2.7 unmaintained since 2019).
# belowlab/ldsc v3.0.1 broke the --h2/--rg/--h2-cts CLI per its README;
# abdenlab/ldsc-python3 (v2.0.0) retains the working CLI. Docker
# `jtb114/ldsc:latest` is the recommended belowlab fallback.
git clone https://github.com/abdenlab/ldsc-python3.git
cd ldsc-python3 && pip install .   # Poetry project (pyproject.toml); no environment.yml
# pre-computed EUR / EAS / AFR LD scores at alkesgroup.broadinstitute.org/LDSCORE

# HESS
git clone https://github.com/huwenboshi/hess.git
# Berisa-Pickrell LDetect partition files bundled in repo

# Popcorn
git clone https://github.com/brielin/Popcorn.git
cd Popcorn && python setup.py install
```

```r
# HDL
remotes::install_github('zhenin/HDL/HDL')
# UKB-array SVD eigen reference: HDL GitHub README has download link

# LAVA
remotes::install_github('josefin-werme/LAVA')
# Pre-computed LDetect partitioning at LAVA GitHub (s2500_m25_f1_w200 is GRCh37/hg19; lift over for GRCh38)

# GenomicSEM
remotes::install_github('GenomicSEM/GenomicSEM')
```

## References

- Bulik-Sullivan B et al 2015 Nat Genet 47:1236 (cross-trait LDSC; intercept absorbs sample overlap)
- Bulik-Sullivan B et al 2015 Nat Genet 47:291 (univariate LDSC h2; companion paper)
- Ning Z et al 2020 Nat Genet 52:859 (HDL; high-definition likelihood; ~60% lower variance than LDSC)
- Werme J et al 2022 Nat Genet 54:274 (LAVA; local genetic correlation via per-locus PC projection)
- Shi H et al 2017 AJHG 101:737 (rho-HESS; locus-level bivariate)
- Shi H et al 2016 AJHG 99:139 (HESS univariate; companion)
- Lee SH et al 2012 Bioinformatics 28:2540 (GREML-bivariate)
- Brown BC et al 2016 AJHG 99:76 (Popcorn; trans-ancestry rg)
- Galinsky KJ et al 2019 Genet Epidemiol 43:180 (cross-population genetic correlation of causal effect sizes)
- Grotzinger AD et al 2019 Nat Hum Behav 3:513 (GenomicSEM)
- O'Connor LJ & Price AL 2018 Nat Genet 50:1728 (LCV; gcp parameter)
- Morrison J et al 2020 Nat Genet 52:740 (CAUSE; CHP-aware MR motivated by high rg)
- Berisa T & Pickrell JK 2016 Bioinformatics 32:283 (LDetect LD blocks underpinning LAVA / HESS)
- Speed D, Holmes J & Balding DJ 2020 Nat Genet 52:458 (model comparison of heritability frameworks)
- Bulik-Sullivan B 2015 bioRxiv 018283 (relationship between LD Score regression and Haseman-Elston regression)
- Skrivankova VW et al 2021 JAMA 326:1614 (STROBE-MR; rg reporting in MR context)

## Related Skills

- causal-genomics/mendelian-randomization - Primary causal estimation; |rg| > 0.3 motivates CHP-aware sensitivity
- causal-genomics/pleiotropy-detection - CAUSE, LHC-MR, LCV; CHP-aware MR battery triggered by high rg
- causal-genomics/heritability-partitioning - Partner method; LDSC stack for univariate h2 and partitioned enrichment
- causal-genomics/genomic-sem - GenomicSEM `ldsc()` is the multivariate extension of bivariate LDSC
- causal-genomics/colocalization-analysis - Locus-level shared causal variant; complements LAVA hits
- causal-genomics/fine-mapping - Credible-set construction at LAVA-significant loci
- causal-genomics/mediation-analysis - MVMR for X -> M -> Y after rg motivates causal hypothesis
- population-genetics/association-testing - GWAS summary statistics underlying all rg methods
- clinical-biostatistics/effect-measures - Translate genetic-architecture findings to clinical effect measures
<!-- END FILE: causal-genomics/genetic-correlation/SKILL.md -->

## 子目录：causal-genomics/genomic-sem

<!-- BEGIN FILE: causal-genomics/genomic-sem/SKILL.md -->
---
name: bio-causal-genomics-genomic-sem
description: Fits structural equation models to GWAS summary statistics using GenomicSEM (Grotzinger 2019), including common-factor models, confirmatory factor models, ESEM, common-factor GWAS with Q_SNP heterogeneity, multivariate Wald tests, and stratified GenomicSEM partitioned heritability. Reconciles results against MTAG multi-trait analysis. Handles sample overlap via the LDSC sampling-covariance matrix, identifies and resolves Heywood cases, and verifies model fit with CFI / RMSEA. Use when modeling latent genetic architecture across correlated traits, running multivariate GWAS on a shared factor, distinguishing factor-mediated from trait-specific SNP effects, or comparing GenomicSEM common-factor results against MTAG when both depend on accurate sampling covariance.
tool_type: r
primary_tool: GenomicSEM
---

## Version Compatibility

Reference examples tested with: GenomicSEM 0.0.5+ (GitHub `GenomicSEM/GenomicSEM`), lavaan 0.6-17+, LDSC v1.0.1+ (Python 3; prefer `abdenlab/ldsc-python3` v2.0.0 -- `belowlab/ldsc` v3.0.1 README states the CLI is broken; Docker `jtb114/ldsc:latest` is the belowlab fallback), baselineLD_v2.2 annotations (alkesgroup.broadinstitute.org/LDSCORE), MTAG 1.0.8+ (Python; `JonJala/mtag`), R 4.4+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('GenomicSEM')` then `?ldsc`, `?commonfactor`, `?usermodel`, `?commonfactorGWAS`
- Python (LDSC, MTAG): `<tool>.py -h` and inspect the source under `ldsc/` or `mtag/`

GenomicSEM is GitHub-only (never on CRAN). If `ldsc()` or `usermodel()` throws an error about lavaan syntax or non-positive-definite covariance, introspect the installed API (`getMethod('ldsc')`) and adapt rather than retrying.

# Genomic SEM

**"Model the latent genetic architecture across several correlated GWAS"** -> Treat each GWAS as a measured indicator of one or more latent genetic factors and fit a structural equation model to the LDSC-derived genetic covariance matrix S and its sampling covariance V (Grotzinger 2019 Nat Hum Behav 3:513). The framework extends naturally to a multivariate GWAS in which a SNP is regressed on a latent factor (common-factor GWAS), with Q_SNP testing whether the SNP effect is homogeneous across factor loadings. Sample overlap between input GWAS is absorbed by the off-diagonals of V; ignoring V inflates Type-I.

- R: `GenomicSEM::ldsc()` produces the (S, V) covariance pair from munged sumstats
- R: `GenomicSEM::commonfactor()` fits a single-factor CFA across all traits in S
- R: `GenomicSEM::usermodel()` fits an arbitrary lavaan-syntax model
- R: `GenomicSEM::commonfactorGWAS()` runs SNP -> factor multivariate GWAS with Q_SNP
- R: `GenomicSEM::userGWAS()` runs arbitrary multivariate SNP regression with per-path Q_SNP
- Python (alternative): `mtag.py --sumstats t1,t2,t3 --out mtag_out` (multi-trait power boost on individual traits)

## Statistical Model Taxonomy

| Method | Latent structure | Min traits | SNP-level test | Strength | Fails when |
|--------|------------------|-----------|----------------|----------|------------|
| Common-factor CFA (Grotzinger 2019) | Single F loading all traits | 3 | None (model-fit only) | Tests whether shared variance is unidimensional | Heterogeneous architecture; CFI < 0.9; near-zero loadings |
| User-specified CFA (`usermodel`) | Pre-specified lavaan syntax | 3 | None | Confirmatory; arbitrary structure | Misspecified model; identification under-determined |
| ESEM | Exploratory rotation; cross-loadings allowed | 6+ | None | When factor count and structure unknown | Few traits; collinear traits; rotation arbitrary |
| Common-factor GWAS (`commonfactorGWAS`) | SNP -> F -> trait1..k | 3 | Wald on F + Q_SNP heterogeneity | Discovers SNPs acting via the common factor; flags Q_SNP outliers | Q_SNP-significant SNPs not interpretable as factor SNPs |
| User GWAS (`userGWAS`) | Arbitrary SNP-path lavaan | 3 | Wald per path + Q_SNP | Tests SNP on any specified path | Highly parameterized models lose power |
| Multivariate Wald test | Joint test across SNP -> trait paths | 2+ | Joint chi-square | Boost power when SNP affects multiple traits | Heterogeneous SNP effects collapse joint test |
| Stratified GenomicSEM (Grotzinger AD et al 2022 Nat Genet 54:548) | Factor model with sLDSC-partitioned annotations | 3 | Per-annotation factor tau | Localizes heritability of the factor to functional categories | Same sLDSC failure modes (small annotation, collinearity) |
| MTAG (Turley 2018 Nat Genet 50:229) | Empirical-Bayes shrinkage across correlated traits | 2 | Per-trait shrunk z-score | Boosts marginal power for any input trait | MaxFDR > 5% indicates heterogeneity violates MTAG assumption |

Methodology evolves; verify the current Grotzinger 2023+ tutorials at `github.com/GenomicSEM/GenomicSEM/wiki` before locking a method. ESEM rotation choice (geomin vs target rotation) is an active area; report sensitivity to rotation.

## MTAG vs GenomicSEM Common-Factor GWAS

Both methods exploit genetic correlation among input GWAS, but their goals and outputs differ.

| Property | MTAG | GenomicSEM commonfactorGWAS |
|----------|------|------------------------------|
| Output | Per-trait shrunk z-scores | SNP effect on latent factor |
| Sample-overlap handling | Bivariate LDSC intercept | Full LDSC sampling-covariance matrix V |
| Heterogeneity diagnostic | MaxFDR (Turley 2018) | Q_SNP (Grotzinger 2019) |
| Interpretation | "Boosted power for trait k" | "Effect on what the traits share" |
| Min traits | 2 | 3 (otherwise factor not identified) |
| Best when | Power-boost an individual trait | Common factor hypothesized |

Both depend on accurate sampling covariance. MTAG fails (MaxFDR > 5%) under the same heterogeneity that produces large Q_SNP in GenomicSEM. The two methods should be reported together when the prior on a common factor is non-trivial; agreement increases confidence, disagreement points to architecture-specific SNPs.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Multi-trait GWAS power boost for one focal trait | MTAG | Optimized for per-trait marginal power |
| Common-factor architecture hypothesized | GenomicSEM `commonfactorGWAS` | Tests SNP -> factor; reports Q_SNP heterogeneity |
| Heterogeneous architecture (>1 latent factor) | ESEM, then confirmatory `usermodel` | Exploratory first, then confirm |
| Confirming a pre-specified factor structure | `usermodel` with lavaan syntax | Confirmatory factor analysis |
| Partition heritability of factor across annotations | Stratified GenomicSEM | Combines sLDSC + factor model |
| Mediation in a SEM framework | `usermodel` with indirect path | Path coefficients + delta-method SE |
| Sample overlap unknown or any-overlap suspected | Always use `ldsc()` output as input | V matrix off-diagonals absorb overlap |
| Cross-ancestry common-factor analysis | Run per-ancestry, compare loadings; no published cross-ancestry SEM as of 2026 | Method not yet validated for mixed-ancestry V |
| Single biobank for all traits (e.g., UKB only) | GenomicSEM with `ldsc()`; the V matrix will reflect overlap | Equivalent to one-sample MR -- the V matrix is the correction |
| Comparing GenomicSEM and MTAG on the same traits | Run both; compare top hits + heterogeneity | Concordance increases confidence; divergence flags heterogeneity |

## Per-Method Failure Modes

### Heywood case (negative residual variance)

**Trigger:** A residual variance estimate is < 0, or a standardized loading exceeds 1.

**Mechanism:** Empirical underidentification; the genetic covariance matrix S is near-singular OR a trait has near-zero specific variance under the model. The maximum-likelihood / DWLS estimator runs past the boundary of the parameter space.

**Symptom:** `lavaan` warning "some estimated lv variances are negative" or "covariance matrix is not positive definite"; standardized loading > 1; non-convergence.

**Fix:** First, inspect the LDSC S matrix for genetic correlations near 1 (multicollinearity). Drop or merge near-identical traits. Second, constrain the offending residual variance to be non-negative in the lavaan syntax (`trait1 ~~ a*trait1; a > 0`). Third, verify the V matrix is positive definite via `chol(V_LD)`; if not, the bivariate LDSC inputs disagree on intercept signs and need re-munging. Never re-fit without diagnosing the cause.

### Sample overlap mis-specified

**Trigger:** Using LDSC intercept manually or supplying covariance from non-`ldsc()` source.

**Mechanism:** GenomicSEM's `ldsc()` function returns a list with `S` (genetic covariance) AND `V` (sampling covariance of the lower-triangle of S). The V off-diagonals capture sample overlap via cross-trait LDSC intercept. Skipping V and supplying only S treats all inputs as independent samples; Type-I error inflates because the sampling distribution under H0 is wrong.

**Symptom:** SE on factor loadings far too small; many SNPs significant in common-factor GWAS that don't replicate; comparison to MTAG shows disagreement consistent with overlap.

**Fix:** Always pass the full output of `ldsc()` -- both S and V -- to `commonfactor()`, `usermodel()`, and `commonfactorGWAS()`. Never construct S manually from rg estimates.

### Q_SNP not reported in commonfactorGWAS

**Trigger:** Running `commonfactorGWAS()` and reporting only the factor p-value per SNP.

**Mechanism:** Q_SNP tests heterogeneity of the SNP's effect across factor loadings (Grotzinger 2019 supplement). A SNP with significant Q_SNP violates the common-factor assumption: its effect is NOT mediated by the factor, and the factor estimate is meaningless for that SNP.

**Symptom:** Top "common-factor SNPs" are dominated by trait-specific effects; replication in independent cohorts is poor for SNPs with high Q_SNP.

**Fix:** Always report Q_SNP p-value alongside the factor p-value. Flag SNPs with Q_SNP p < 5e-8 / N_factor_SNPs (Bonferroni for the discovered set) as architecture-violating and exclude from "common-factor SNP" claims. Re-fit those SNPs in `userGWAS()` with separate paths to each trait.

### Trait inclusion under heterogeneous factor structure

**Trigger:** Forcing a common-factor model on traits that don't share a single latent factor.

**Mechanism:** When two or more traits load on a different factor than the rest, the single-factor model misfits. lavaan still returns parameter estimates but model fit is poor.

**Symptom:** CFI < 0.9; RMSEA > 0.08; some standardized loadings near 0 while others near 1; chi-square highly significant even after accounting for N.

**Fix:** Run ESEM first (`commonfactor` then `usermodel` with cross-loadings allowed) to discover structure. If two factors emerge, fit a two-factor `usermodel`. Drop traits with near-zero loadings on all factors. Document the model search.

### MTAG MaxFDR > 5%

**Trigger:** Running MTAG on traits with low pairwise genetic correlation or with one trait that has a very different architecture.

**Mechanism:** MTAG assumes a homogeneous variance-covariance structure across SNPs. When heterogeneity dominates, the empirical-Bayes shrinkage can over-claim SNPs in the focal trait. Turley 2018 defines MaxFDR as the maximum estimated false discovery rate under worst-case heterogeneity; > 5% invalidates the published trait-specific summary statistics.

**Symptom:** MTAG output file reports `maxFDR` > 0.05; per-trait MTAG hits don't replicate in independent cohorts.

**Fix:** Check pairwise rg via LDSC; if any pair is < 0.7, MTAG is risky. Drop the most heterogeneous trait and re-run. Alternatively, switch to GenomicSEM's `commonfactorGWAS` which models heterogeneity explicitly via Q_SNP.

### Non-positive-definite V_LD matrix

**Trigger:** LDSC inputs from different ancestry GWAS, or one trait with very low mean chi-square (< 1.02).

**Mechanism:** V is the sampling covariance of vech(S); when individual entries of S have huge SE relative to off-diagonal covariance, the resulting V is not positive definite (negative eigenvalues).

**Symptom:** `commonfactor()` errors with "matrix is not positive definite" before fitting; `eigen(LDSCoutput$V)$values` shows negative values.

**Fix:** Verify per-trait mean chi-square via `ldsc()` log; below 1.02, exclude that trait. Verify all GWAS are EUR ancestry (or match ancestry of LD scores). Apply nearest-PD smoothing via `Matrix::nearPD(V)$mat` ONLY as a last resort and document the approximation in methods.

## Model Fit Diagnostics

| Index | Acceptable | Good | Source |
|-------|-----------|------|--------|
| CFI | >= 0.90 | >= 0.95 | Hu & Bentler 1999 Struct Equ Model 6:1 |
| TLI / NNFI | >= 0.90 | >= 0.95 | Hu & Bentler 1999 |
| RMSEA | <= 0.08 | <= 0.05 | Hu & Bentler 1999 |
| SRMR | <= 0.08 | <= 0.05 | Hu & Bentler 1999 |
| chi-square p-value | (less informative at large N) | n/a | Penalize for N inflation |

AIC / BIC are used for nested-model comparison (lower is better); only compare nested models fit on the same S.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| CFI >= 0.95 | Hu & Bentler 1999 | Conventional good fit; SEM literature default |
| RMSEA <= 0.05 | Hu & Bentler 1999 | Conventional good fit |
| RMSEA 0.05 - 0.08 | Hu & Bentler 1999 | Acceptable; flag as "adequate" not "good" |
| Q_SNP p < 0.05 / N_SNP_factor | Grotzinger 2019 Nat Hum Behav 3:513 | Bonferroni for heterogeneity among factor-significant SNPs |
| MTAG MaxFDR < 5% | Turley 2018 Nat Genet 50:229 | Above this, MTAG marginal trait results invalid |
| Per-trait LDSC mean chi-square > 1.02 | LDSC documentation | Below this, V entries too noisy; factor SE inflated |
| Standardized loading 0.3 - 0.9 typical | SEM conventions | < 0.3 trait loads weakly; > 0.95 may indicate over-fit / collinearity |
| Min 3 traits for common factor | SEM identification | Single factor with k traits has k(k+1)/2 moments; needs k>=3 to identify |

## Standard Workflow

**Goal:** Fit a common-factor model across correlated GWAS and run a multivariate GWAS on the factor with Q_SNP.

**Approach:** Munge sumstats -> LDSC for (S, V) -> common-factor CFA -> inspect fit -> prepare SNPs -> common-factor GWAS -> report factor effects with Q_SNP flags.

```r
library(GenomicSEM)

# Step 1: Munge sumstats (one-time; produces .sumstats.gz files)
files <- c('raw/trait1.txt', 'raw/trait2.txt', 'raw/trait3.txt')
hm3 <- 'w_hm3.snplist'  # HapMap3 SNP list
trait_names <- c('trait1', 'trait2', 'trait3')
N <- c(150000, 200000, 175000)
munge(files = files, hm3 = hm3, trait.names = trait_names, N = N)

# Step 2: LDSC produces both S (genetic covariance) and V (sampling covariance)
traits <- c('trait1.sumstats.gz', 'trait2.sumstats.gz', 'trait3.sumstats.gz')
ldsc_results <- ldsc(
    traits = traits,
    sample.prev = c(0.5, 0.5, NA),    # case prevalence; NA for continuous
    population.prev = c(0.05, 0.05, NA),
    ld = 'eur_w_ld_chr/',
    wld = 'eur_w_ld_chr/',
    trait.names = trait_names
)
# ldsc_results$S = genetic covariance; ldsc_results$V = sampling covariance

# Step 3a: Common-factor CFA via DWLS
cf_fit <- commonfactor(covstruc = ldsc_results, estimation = 'DWLS')
print(cf_fit$modelfit)  # CFI, RMSEA, SRMR, chi-square
print(cf_fit$results)   # loadings + SEs

# Step 3b: Alternative -- user-specified two-factor model (>=3 indicators per factor)
# Identification rule: each factor needs >= 3 indicators OR one anchor loading fixed
# to 1 plus factor variance free. A factor with a single indicator is NOT identified.
model_syntax <- '
    F1 =~ NA*trait1 + trait2 + trait3
    F2 =~ NA*trait4 + trait5 + trait6
    F1 ~~ 1*F1
    F2 ~~ 1*F2
    F1 ~~ F2
'
user_fit <- usermodel(covstruc = ldsc_results, model = model_syntax, estimation = 'DWLS')
```

`estimation = 'DWLS'` (diagonally weighted least squares) is the default and is required when V is large; `'ML'` is faster but assumes a known V and can produce wrong SE under sample overlap.

### ESEM (Exploratory Factor Structure)

When the factor structure is unknown, fit `usermodel()` with all loadings free across all factors, then apply a rotation post-fit. Rotation choices: **geomin oblique** (default; allows factor correlation), **target rotation** (Browne 2001 Multivariate Behav Res 36:111; uses a hypothesized loading template), **quartimin** (orthogonal; assumes factors are uncorrelated).

```r
model_esem <- '
    F1 =~ NA*trait1 + trait2 + trait3 + trait4
    F2 =~ NA*trait1 + trait2 + trait3 + trait4
    F1 ~~ 1*F1
    F2 ~~ 1*F2
    F1 ~~ F2
'
esem_fit <- usermodel(covstruc = ldsc_results, model = model_esem, estimation = 'DWLS')
# Rotate post-fit via GPArotation::GPForth/GPFoblq or lavaan::rotate()
```

**Decision:** ESEM for K-factor exploration when structure is unknown; CFA via `usermodel()` once a structure is confirmed. Report rotation sensitivity (geomin vs target vs quartimin) and treat as exploratory.

**Cross-loadings.** Cross-loadings (one trait loads on > 1 factor) are common in psychiatric and behavioral GWAS. Brown 2015 *Confirmatory Factor Analysis for Applied Research* recommends allowing cross-loadings first and using modification indices to guide simplification. Allow a cross-loading when constraining residual variance otherwise forces a Heywood case. Constrain when CFI < 0.9 and modification indices instead suggest a correlated residual between two indicators (which is the more parsimonious fix).

### userGWAS for Custom Path Models

`userGWAS()` fits arbitrary lavaan-syntax SNP regressions and is the right tool when the SNP needs to be tested on multiple paths simultaneously (e.g. factor-mediated effect AND a direct effect on one indicator).

```r
# Test SNP -> F path + SNP -> trait1 direct path simultaneously
model <- '
    F =~ NA*trait1 + trait2 + trait3
    F ~~ 1*F
    F ~ SNP
    trait1 ~ SNP    # direct effect on trait1, partialed out of F
'
user_results <- userGWAS(covstruc = ldsc_results,
                         SNPs = ss,
                         estimation = 'DWLS',
                         model = model,
                         sub = c('F~SNP', 'trait1~SNP'),
                         parallel = TRUE,
                         cores = 8)
# Output columns include: lhs, op, rhs, est, SE, Z, Pvalue, Q_pval, Q_df.
# Q_pval per SNP measures heterogeneity across loadings AFTER conditioning on
# the direct path; remaining Q_SNP signal indicates a third path is needed.
```

### Higher-Order / Bifactor / p-Factor Models

Use case: psychiatric genetics p-factor (Caspi 2014 Clin Psychol Sci 2:119; Grotzinger 2022 Nat Genet 54:548 cross-disorder), cognitive g-factor (de la Fuente 2021 Nat Hum Behav 5:49).

Hierarchical template -- first-order factors load on a single second-order p-factor:

```r
model_pfactor <- '
    # First-order factors
    INT =~ NA*trait_anx + trait_dep + trait_neuro       # internalizing
    EXT =~ NA*trait_adhd + trait_alc + trait_subst       # externalizing
    THT =~ NA*trait_scz + trait_bp                       # thought-disorder
    # Second-order p-factor
    p =~ NA*INT + EXT + THT
    INT ~~ 1*INT
    EXT ~~ 1*EXT
    THT ~~ 1*THT
    p ~~ 1*p
'
```

Bifactor alternative: `p =~` all traits directly, with `INT`/`EXT`/`THT` as orthogonal residual factors. Bifactor typically gives tighter CFI/RMSEA but the substantive interpretation of the residual factors is harder; bifactor is also prone to over-fitting at modest trait counts (Bonifay W & Cai L 2017 Multivariate Behav Res 52:465). Cite Grotzinger 2022 Nat Genet 54:548 and Karlsson Linner R, Mallard TT et al 2021 Nat Neurosci 24:1367 for the canonical psychiatric implementations.

## Common-Factor GWAS with Q_SNP

**Goal:** Identify SNPs that affect the latent factor and flag SNPs whose effect is heterogeneous across loadings.

**Approach:** Build SNP-by-trait effect-and-SE matrix via `sumstats()`, then fit the SNP-augmented model genome-wide via `commonfactorGWAS()`. Report both factor p-value and Q_SNP p-value per SNP.

`sumstats()` flips effect signs based on the reference panel A1/A2 to enforce consistent allele coding across input GWAS. Required input columns (case-sensitive) are `SNP, A1, A2, BETA/Z/OR, SE, P, N, MAF`; some are conditional on `se.logit` / `OLS`. Silent failures are almost always column-name mismatches (e.g. `EA`/`NEA` instead of `A1`/`A2` -> 0% SNPs retained) or a missing `N` column -> SNPs dropped. Always run `head(read.table(file, header=TRUE, nrow=2))` per input before the `sumstats()` call.

```r
# Prepare per-SNP betas and SEs across all input GWAS
ss <- sumstats(
    files = c('raw/trait1.txt', 'raw/trait2.txt', 'raw/trait3.txt'),
    ref = 'reference.1000G.maf.0.005.txt',
    trait.names = trait_names,
    se.logit = c(TRUE, TRUE, FALSE),     # TRUE if trait is logistic-scale (case-control); FALSE if continuous
    OLS = c(FALSE, FALSE, TRUE),
    linprob = c(FALSE, FALSE, FALSE),
    N = N,
    info.filter = 0.9,                   # standard imputation INFO threshold
    maf.filter = 0.01
)

# GenomicSEM internally detects the OS via Sys.info()[['sysname']] and chooses
# PSOCK (Windows) vs FORK (Linux/Mac) clusters automatically; there is no user
# `Operating=` argument. MPI=TRUE switches to an mpirun-based strategy for
# cluster job submission. parallel=TRUE is the default.
cfgwas <- commonfactorGWAS(
    covstruc = ldsc_results,
    SNPs = ss,
    estimation = 'DWLS',
    parallel = TRUE,
    cores = 8,
    MPI = FALSE
)

# cfgwas columns include rsID/chr/BP/MAF/A1/A2/est/se_c/Z_Estimate/Pval_Estimate (factor effect)
# plus heterogeneity columns Q / Q_df / Q_pval. Q_pval IS the per-SNP heterogeneity
# test (often referred to as Q_SNP in the literature; the column name in the data.frame is Q_pval).
cfgwas$factor_sig <- cfgwas$Pval_Estimate < 5e-08
cfgwas$qsnp_sig <- cfgwas$Q_pval < (0.05 / sum(cfgwas$factor_sig))
cfgwas$factor_only <- cfgwas$factor_sig & !cfgwas$qsnp_sig
```

The "factor-only" subset (factor-significant AND Q_SNP non-significant) is the publication-grade set of common-factor SNPs.

## MTAG Comparison

**Goal:** Cross-check GenomicSEM common-factor results against MTAG per-trait shrunk z-scores.

**Approach:** Run MTAG CLI on the same input sumstats; compare top hits with GenomicSEM factor hits. Report MaxFDR.

```bash
# MTAG CLI (Python)
python mtag.py \
    --sumstats trait1.txt,trait2.txt,trait3.txt \
    --n_min 0 \
    --out mtag_results
# MTAG uses the signed Z by default; --use_beta_se was disabled upstream (raises a
# RuntimeError since Dec 2021 due to beta-se bugs), so supply a Z column and omit it.

# Check MaxFDR per trait
grep -iE 'max ?fdr' mtag_results.log   # matches both the section header and the 'Max FDR of Trait' value lines
# Each per-trait MTAG file: mtag_results_trait_<k>.txt
```

If MaxFDR > 0.05 for any trait, MTAG results for that trait are unreliable; GenomicSEM with Q_SNP filtering is the more defensible report.

## Stratified GenomicSEM (Partitioned Heritability of Factor)

For partitioning the heritability of the latent factor across functional annotations, use `s_ldsc()` (stratified LDSC inside GenomicSEM) and pass the multi-annotation output to a stratified model fit.

```r
# Stratified LDSC across baseline + custom annotations
s_results <- s_ldsc(
    traits = traits,
    sample.prev = c(0.5, 0.5, NA),
    population.prev = c(0.05, 0.05, NA),
    ld = 'baselineLD_v2.2.',
    wld = 'weights.hm3_noMHC.',
    frq = '1000G.EUR.QC.',
    trait.names = trait_names
)

# enrich() inventory:
#   params: lavaan syntax of the parameter under enrichment (loading, residual var, or F~~F latent var)
#   fix='regressions': hold regression paths fixed at the genome-wide estimate during stratified fit
#   std.lv=FALSE: do not standardize the latent variance
#   rm_flank=TRUE: drop flanking-window contributions (default)
#   tau=FALSE: use the baseline-annotation S/V matrices (TRUE switches to the V_Tau/S_Tau tau parametrization)
#   base=TRUE: include baseline annotation contributions in the partition
#   toler=NULL: matrix-inversion tolerance (let GenomicSEM choose; supply a small value when S is near-singular)
strat_factor <- enrich(s_covstruc = s_results,
                       model = '',
                       params = 'F =~ trait1',
                       fix = 'regressions',
                       std.lv = FALSE,
                       rm_flank = TRUE,
                       tau = FALSE,
                       base = TRUE,
                       toler = NULL)
```

The output gives per-annotation enrichment of the factor h2 -- the analog of cell-type S-LDSC for the latent factor (Grotzinger AD et al 2022 Nat Genet 54:548).

## Computational Footprint

| Step | Runtime | Hardware |
|------|---------|----------|
| `ldsc()` multi-trait sampling covariance | minutes | laptop |
| `commonfactor()` / `usermodel()` (no SNP loop) | seconds | laptop |
| `commonfactorGWAS()` over 6-8M SNPs | 4-24h depending on cores | cluster recommended |
| `userGWAS()` over 6-8M SNPs with complex path model | 8-48h | cluster recommended |
| Stratified GenomicSEM with 50+ annotations | 1-3 days | cluster |
| MTAG over 6-8M SNPs | 1-2h | laptop or cluster |

Cluster runs of `commonfactorGWAS()` / `userGWAS()` should use `MPI=TRUE` when submitting via mpirun; GenomicSEM detects the OS internally (via `Sys.info()[['sysname']]`) and selects FORK (Linux/Mac) vs PSOCK (Windows) cluster types automatically -- there is no `Operating=` user argument. On a Mac/Windows workstation, reduce `cores` to the physical-core count to avoid PSOCK fork failures.

## Reconciliation: When GenomicSEM and MTAG Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| GenomicSEM factor SNP sig, MTAG sig for all traits | Genuine common-factor SNP | Report; high confidence |
| GenomicSEM factor SNP sig, MTAG sig in only 1 trait | Q_SNP heterogeneity likely; one-trait-dominant | Check Q_SNP; if sig, this is NOT a factor SNP |
| MTAG sig, GenomicSEM factor null, Q_SNP sig | Trait-specific SNP captured by MTAG shrinkage | Report as trait-specific, not common-factor |
| Both null but per-trait univariate sig | Power loss from multivariate parameterization | Re-check sample overlap V matrix |
| GenomicSEM and MTAG both sig but opposite direction | Sample-overlap mis-specification OR sign error in munging | Re-munge with same allele convention; re-run `ldsc()` |
| MTAG MaxFDR > 5%, GenomicSEM with Q_SNP works | MTAG assumption violated | Prefer GenomicSEM as primary |
| One-trait GWAS sig but common-factor not | Trait-specific architecture | Don't force into common-factor frame |

**Operational rule for publication:** A common-factor SNP claim requires (1) factor p < 5e-8, (2) Q_SNP p > 0.05 / N_factor_SNPs (non-heterogeneous), and (3) replication in an independent set of traits or cohorts. Trait-specific SNPs from MTAG require MaxFDR < 5% for the trait. Reporting only the factor effect without Q_SNP is the most common reviewer-flagged error.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `commonfactor()` complains "S not positive definite" | Genetic correlations near +/-1 among inputs | Drop redundant traits; verify rg < 0.95 pairwise |
| Standardized loading > 1 | Heywood case; under-identification | Constrain residual variance >= 0; inspect S for collinearity |
| Factor p-value reported, Q_SNP not reported | Default focus is on factor effect | Always report Q_SNP from `commonfactorGWAS` output |
| `ldsc()` fails with "category not found" | Wrong LD score column names (legacy format) | Use Python 3 LDSC fork; download `eur_w_ld_chr/` from alkesgroup |
| `lavaan` says "model not identified" | Too few traits for too many parameters | Need >= 3 traits per factor; constrain factor variance to 1 |
| MTAG `MaxFDR` not in log | Older MTAG version (< 1.0.7) | Update MTAG; MaxFDR reporting added late 2019 |
| Singular V matrix on smooth `nearPD` | One trait has near-zero h2 or mean chi-square < 1.02 | Drop the trait; do not smooth as a fix |
| `usermodel()` slow or fails | Complex syntax + many traits | Simplify model; estimate with `estimation = 'DWLS'`, not `'ML'`, when V is informative |
| Sumstats output has zero overlap with reference | Allele coding mismatch in `sumstats()` | Check `se.logit` and `OLS` settings per trait; align A1/A2 |
| GenomicSEM and TwoSampleMR give different rg | TwoSampleMR uses bivariate LDSC; GenomicSEM uses the same S | Match the underlying LDSC reference panel and weights |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Q_SNP reported?" | `Q_pval` column reported alongside SNP->factor effect; Bonferroni threshold 5e-8 / N_factor_SNPs applied |
| "MaxFDR > 5%?" | MTAG `maxFDR` reported per trait; > 5% invalidates MTAG for that trait -> GenomicSEM common-factor used instead |
| "Sample overlap absorbed?" | Full V matrix from `ldsc()` is the input to all model fits; S is never constructed manually from pairwise rg estimates |
| "Model fit?" | CFI >= 0.95, RMSEA <= 0.08, SRMR <= 0.08 reported; AIC / BIC for nested comparison; chi-square reported but treated as inflated at large N |
| "Why a factor model and not MTAG?" | Factor structure tested first; if traits load on a common factor with CFI > 0.95, common-factor GWAS preferred -- explicitly models heterogeneity via Q_SNP |
| "Heywood case?" | Negative residual variance constrained >= 0; OR the offending indicator dropped and the model re-specified; the choice is documented in methods |
| "Cross-ancestry?" | Run per-ancestry; no validated cross-ancestry V matrix as of 2026; loadings compared qualitatively |
| "Why DWLS and not ML?" | ML assumes V is known; DWLS uses the empirical V from `ldsc()` and is the appropriate estimator under sample overlap |

## Tool Installation

```r
# GenomicSEM is GitHub-only
remotes::install_github('GenomicSEM/GenomicSEM')

# Dependencies
install.packages(c('lavaan', 'Matrix', 'gdata'))

# Optional companions
remotes::install_github('MRCIEU/TwoSampleMR')  # for downstream MR using factor GWAS as exposure
```

For Python tools:

```bash
# LDSC python3 fork (GenomicSEM input format). belowlab/ldsc v3.0.1 broke the
# --h2/--rg/--h2-cts CLI per its README; use abdenlab/ldsc-python3 (v2.0.0)
# for a working CLI. Docker jtb114/ldsc:latest is the belowlab fallback.
git clone https://github.com/abdenlab/ldsc-python3.git
cd ldsc-python3 && pip install .   # Poetry project (pyproject.toml); no requirements.txt

# MTAG
git clone https://github.com/JonJala/mtag.git
cd mtag && pip install -r requirements.txt
```

Pre-downloaded reference files: `eur_w_ld_chr/`, `baselineLD_v2.2.*`, `w_hm3.snplist`, and 1000G allele-frequency files are hosted at `alkesgroup.broadinstitute.org/LDSCORE/`.

## References

- Grotzinger AD et al 2019 Nat Hum Behav 3:513 (GenomicSEM, common-factor GWAS, Q_SNP)
- Grotzinger AD et al 2022 Nat Genet 54:548 (Stratified GenomicSEM)
- Turley P et al 2018 Nat Genet 50:229 (MTAG; MaxFDR)
- Bulik-Sullivan B et al 2015 Nat Genet 47:291 (LDSC for genetic covariance)
- Bulik-Sullivan B et al 2015 Nat Genet 47:1236 (bivariate LDSC, sample overlap)
- Rosseel Y 2012 J Stat Softw 48:1-36 (lavaan package)
- Hu LT & Bentler PM 1999 Struct Equ Model 6:1 (CFI / RMSEA cutoffs)
- Asparouhov T & Muthen B 2009 Struct Equ Model 16:397 (ESEM framework)
- Finucane HK et al 2015 Nat Genet 47:1228 (S-LDSC, foundation for stratified GenomicSEM)
- Gazal S et al 2017 Nat Genet 49:1421 (baseline-LD annotations)
- Demange PA et al 2021 Nat Genet 53:35 (GenomicSEM GWAS-by-subtraction for noncognitive skills; Q_SNP in practice)
- Karlsson Linner R, Mallard TT et al 2021 Nat Neurosci 24:1367 (multivariate externalizing GWAS via GenomicSEM)
- de la Fuente J et al 2021 Nat Hum Behav 5:49 (GenomicSEM for cognitive g factor)
- Skrivankova VW et al 2021 JAMA 326:1614 (STROBE-MR; relevant when downstream MR uses factor GWAS)

## Related Skills

- causal-genomics/mendelian-randomization - Use factor-GWAS effect sizes as MR exposure
- causal-genomics/genetic-correlation - Bivariate LDSC produces the off-diagonals of the S matrix; GenomicSEM is the multi-trait extension
- causal-genomics/heritability-partitioning - LDSC and S-LDSC foundations for stratified GenomicSEM
- causal-genomics/colocalization-analysis - Cross-trait colocalization at common-factor loci
- causal-genomics/pleiotropy-detection - Q_SNP is a per-SNP pleiotropy diagnostic; sibling concept
- causal-genomics/fine-mapping - Resolve factor-significant loci to credible sets
- causal-genomics/mediation-analysis - SEM mediation paths overlap with `usermodel` indirect effects
- causal-genomics/transcriptome-wide-association - TWAS on factor sumstats from `commonfactorGWAS`
- population-genetics/association-testing - GWAS sumstats are the input format
<!-- END FILE: causal-genomics/genomic-sem/SKILL.md -->

## 子目录：causal-genomics/heritability-partitioning

<!-- BEGIN FILE: causal-genomics/heritability-partitioning/SKILL.md -->
---
name: bio-causal-genomics-heritability-partitioning
description: Estimates SNP heritability and partitions it across functional annotations, cell types, and loci from GWAS summary statistics or individual-level genotypes. Implements LDSC, stratified LDSC with the baseline-LD model, Finucane 2018 cell-type prioritization, LDAK SumHer, HDL, HESS local heritability, BOLT-REML, GCTA-GREML, graphREML, and Popcorn cross-population genetic correlation. Use when computing total h2_SNP from summary stats, partitioning heritability across functional categories, prioritizing trait-relevant tissues or cell types from ENCODE/Roadmap chromatin marks, reconciling LDSC vs LDAK enrichment estimates, computing local heritability with HESS, estimating genetic correlation between traits, or producing publication-grade enrichment with calibrated sensitivity to model assumptions.
tool_type: mixed
primary_tool: ldsc
---

## Version Compatibility

Reference examples tested with: LDSC v1.0.1+ (Python 3 fork; prefer `abdenlab/ldsc-python3` v2.0.0 which retains the working `--h2 / --rg / --h2-cts` CLI -- `belowlab/ldsc` v3.0.1 explicitly broke that CLI per its README and is best run via Docker `jtb114/ldsc:latest`), LDAK 6.0+, BOLT-LMM 2.4.1+, GCTA 1.94+, HESS 0.5.4+, HDL 1.4.0+ (R; GitHub `zhenin/HDL`), Popcorn 1.0+ (Python; brielin/Popcorn), baselineLD_v2.2 annotations (alkesgroup.broadinstitute.org/LDSCORE).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `python -c 'import <module>; help(<module>)'`
- R: `packageVersion('<pkg>')` then `?function_name`
- CLI: `<tool> --version` then `<tool> --help`

LDSC's official repository (bulik/ldsc) is Python 2.7 only and unmaintained since 2019; use the Python 3 community forks. If code throws ImportError, AttributeError, or a "category not found" error in the LD score file, introspect the installed binary and the actual LD-score column headers rather than retrying.

# Heritability Partitioning

**"Estimate SNP heritability and partition it across functional categories, cell types, and loci"** -> Decompose `h2_SNP` from GWAS summary statistics (or individual-level genotypes) into contributions from baseline annotations (coding, conserved, regulatory), tissue-specific chromatin marks, and per-locus components, then reconcile model-dependent enrichment estimates across LDSC and LDAK. Tool choice is a decision about the **regime** (summary-stat vs individual-level; one-trait vs two-trait genetic correlation; total vs partitioned vs local) and the **model assumption** about how per-SNP heritability scales with LD, MAF, and functional annotation (GCTA model vs LDAK-Thin vs baseline-LD).

- CLI (h2 from sumstats, EUR): `ldsc.py --h2 trait.sumstats.gz --ref-ld-chr eur_w_ld_chr/ --w-ld-chr eur_w_ld_chr/ --out h2`
- CLI (functional partitioning): `ldsc.py --h2 trait.sumstats.gz --ref-ld-chr baselineLD.,<annot>. --frqfile-chr 1000G.EUR.QC. --w-ld-chr weights. --overlap-annot --print-coefficients --out part`
- CLI (cell-type prioritization, Finucane 2018): `ldsc.py --h2-cts trait.sumstats.gz --ref-ld-chr-cts <cts_file>.ldcts --w-ld-chr weights. --out cts`
- CLI (cross-trait rg): `ldsc.py --rg t1.sumstats.gz,t2.sumstats.gz --ref-ld-chr eur_w_ld_chr/ --w-ld-chr eur_w_ld_chr/ --out rg`
- CLI (LDAK alternative): `ldak --sum-hers <out> --summary trait.txt --tagfile ldak.thin.<build>.tagging --check-sums NO`
- R (HDL): `HDL::HDL.rg(gwas1.df, gwas2.df, LD.path = 'UKB_array_SVD_eigen90_extraction')`
- CLI (local h2): HESS step1 `hess.py --local-hsqg trait.sumstats.gz --chrom <chr> --bfile <ref> --partition <part>.bed --out hess_<chr>`

## Statistical Model Taxonomy

| Method | Heritability model | Input | Output | Strength | Fails when |
|--------|--------------------|-------|--------|----------|------------|
| LDSC h2 (Bulik-Sullivan 2015 Nat Genet 47:291) | GCTA model: per-SNP h2 proportional to LD score | Sumstats + ancestry-matched LD scores | h2 estimate + intercept + ratio | Standard for sumstats; fast; calibrated EUR LD scores | N too low (mean chi-square < 1.02); non-EUR ancestry with EUR LD scores; population stratification not captured |
| Stratified LDSC / S-LDSC (Finucane 2015 Nat Genet 47:1228) | GCTA model with per-annotation tau coefficients | Sumstats + baseline + custom annotations | Per-annotation enrichment + tau | Reference functional partitioning method | Highly collinear annotations inflate per-tau SE; small annotation (<0.5% genome) underpowered |
| Baseline-LD model (Gazal 2017 Nat Genet 49:1421) | Adds LD-related and MAF-dependent annotations to baseline | Sumstats + `baselineLD_v2.2.` | Enrichment robust to LD-MAF confounding | Modern S-LDSC default; calibrates LD/MAF dependence | EUR-only baseline-LD v2.2 must NOT be used on non-EUR GWAS; use baseline-LD-X / S-LDXR (Shi H & Gazal S et al 2021 Nat Commun 12:1098) instead |
| Cell-type S-LDSC (Finucane 2018 Nat Genet 50:621) | Per-cell-type annotation marginal to baseline | Sumstats + cell-type chromatin annotations (.ldcts) | Per-cell-type p-value | Tissue / cell-type prioritization; published per-tissue ldcts files | Sample size small (mean chi-square < 1.02); annotation overlaps strongly with baseline |
| HDL (Ning 2020 Nat Genet 52:859) | Genome-wide eigen-decomposition likelihood | Sumstats + HDL reference panel (UKB N=336k) | h2 and rg with ~60% lower variance than LDSC | Equivalent to ~2.5x sample size for h2 / rg | Sample overlap > 5% biases the likelihood; only EUR HDL reference panel publicly available; no non-EUR HDL eigen-reference exists as of 2026 -- for non-EUR fall back to ancestry-matched cross-trait LDSC (intercept absorbs overlap; rg unbiased) |
| LDAK SumHer (Speed 2019 Nat Genet 51:277) | LDAK-Thin model: per-SNP h2 reweighted by MAF + LD | Sumstats + LDAK-Thin tagging file | h2 + enrichment | Alternative to LDSC; often better-fitting per cross-validation per Speed 2017 Nat Genet 49:986 | Tagging file must match build / ancestry; non-EUR support limited |
| HESS (Shi 2016 AJHG 99:139; Shi 2017 AJHG 101:737) | Per-locus h2 via quadratic form on LD-projected effect estimates | Sumstats + LD reference + locus partition (LDetect) | Per-locus h2 + bivariate local rg | Locus-level resolution; identifies high-h2 loci for follow-up | Locus has < 1000 SNPs; LD reference must be in-sample or matched |
| BOLT-REML (Loh 2015 Nat Genet 47:1385) | Bayesian REML; multi-component variance | Individual-level genotypes (PLINK BED) + phenotype | h2 + per-component partition | Biobank-scale (N=500k feasible); more precise than LDSC at high N | Needs individual-level data; assumes Gaussian residual; not for case-control < 5% prevalence without LMM-BOLT |
| GCTA-GREML (Yang 2011 AJHG 88:76) | GRM-based REML on individual genotypes | GRM (PLINK BED) + phenotype + covariates | h2 + SE | Gold standard for individual-level data; PCGC for case-control | N <= 5000 has wide SE; case-control needs PCGC-S correction; population stratification leaks into h2 |
| graphREML (Li H et al 2024 medRxiv 2024.11.04.24316716; published Nat Genet 2026) | Sumstat REML using LDGM graph | Sumstats + LDGM reference | h2 + functional partition | Use when an LDGM reference exists for the ancestry AND runtime matters at biobank N (> 200k); pre-built LDGM panels currently cover EUR + EAS | Newer (2024); reference panel availability evolving; non-EUR/EAS ancestries lack pre-built LDGM |
| Popcorn (Brown 2016 AJHG 99:76) | Trans-ancestry genetic correlation under MAF-LD model | Sumstats + cross-population LD scores | rg trans-ancestry + h2 per population | Distinguishes shared-causal vs ancestry-specific signal | Effective N per population must be > 5000; small non-EUR cohorts unstable |
| Cross-model reconciliation (Gazal 2019 Nat Genet 51:1202) | Joint LDSC + LDAK comparison framework | Both LDSC and LDAK outputs | Enrichment model-comparison (Gazal: baseline-LD better-calibrated; LDAK developers dispute) | Quantifies model-dependent component of enrichment | Methodological / reporting practice, not a separate primary estimator |

Methodology evolves; benchmark consensus shifts. Verify against current Yengo 2022 *Nat Methods*, Speed D, Holmes J & Balding DJ 2020 Nat Genet 52:458 (heritability model comparison), and the alkesgroup/Price Lab tutorial (LDSC) before locking method as primary. Per-SNP-h2 model choice is an open debate; report both LDSC and LDAK SumHer when a claim depends on model assumption.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Total h2 from sumstats, EUR GWAS, N > 50k | LDSC h2 | Standard, fast, well-calibrated against EUR reference |
| Partitioned h2 by functional category | S-LDSC with baseline-LD_v2.2 | Default functional partitioning; LD/MAF-robust |
| Tissue / cell-type prioritization | S-LDSC --h2-cts with ENCODE/Roadmap or scATAC ldcts | Designed for this; per-tissue Bonferroni-controlled |
| Two-trait genetic correlation from sumstats, no overlap | HDL (primary) + cross-trait LDSC (secondary) | HDL ~60% lower variance; LDSC robust under any overlap |
| Two-trait rg with sample overlap > 5% | Cross-trait LDSC | HDL biased by overlap; LDSC intercept absorbs overlap |
| Individual-level biobank h2, N > 100k | BOLT-REML | Better precision; multi-component partition |
| Smaller individual-level cohort, N 5-50k | GCTA-GREML | Gold-standard REML; PCGC if case-control < 20% prevalence |
| Local heritability and bivariate local rg | HESS | Per-locus resolution; identifies hotspots for follow-up |
| Trans-ancestry rg / cross-population h2 | Popcorn | Designed for trans-ethnic; LD scores per population |
| Functional enrichment claim depends on model | Report BOTH LDSC and LDAK SumHer | Per Gazal 2019; model-dependence is real |
| Case-control GWAS with low prevalence | LDSC on liability scale (--samp-prev --pop-prev) | Observed-scale h2 understates liability-scale truth |
| Single-cell ATAC cell-type prioritization | S-LDSC with per-cluster ATAC peaks as annotations | Cross-reference atac-seq/single-cell-atac for peak generation |

## LDSC Intercept Interpretation (Postdoc Nuance)

The LDSC intercept is widely misinterpreted as a "confounding score". The correct interpretation:

- Intercept = 1 indicates no inflation from population structure, cryptic relatedness, or sample overlap (idealised)
- Intercept > 1 indicates SOME source of inflation, BUT polygenic background can elevate the intercept too: at very high N, polygenic signal can lift the intercept modestly without stratification
- The **ratio** statistic `ratio = (intercept - 1) / (mean_chi2 - 1)` is the fraction of inflation attributable to non-polygenic sources; a ratio of 0 means all inflation is polygenic, a ratio near 1 means most of it is stratification or overlap
- Bulik-Sullivan 2015 recommends interpreting intercept jointly with mean chi-square; intercept of 1.05 is innocuous if mean chi-square is 1.5 (ratio = 0.1) but worrying if mean chi-square is 1.05 (ratio = 1.0)

**Operational rule:** Always report intercept, mean chi-square, and ratio together. Do not interpret intercept in isolation. For sample-overlap diagnosis between two GWAS, use bivariate LDSC intercept, not univariate.

**Intercept > 1.5 troubleshooting ladder** (work in order; stop when source is found): (a) per-cohort PC adjustment was insufficient; refit GWAS with more PCs (10-20) or per-cohort separately, (b) cryptic relatedness in the GWAS cohort -- run `king --related` and remove pairs with kinship > 0.05 (or 0.0884 for second-degree), (c) case-control matching imbalance -- check case/control PCs separately, (d) sample-overlap with one of the contributing cohorts (especially in meta-analysis) -- check bivariate intercepts pairwise, (e) if biobank-internal, recompute the GWAS with sample-level relatedness exclusion before LDSC.

## LDSC vs LDAK Reconciliation

LDSC (GCTA model) and LDAK SumHer (LDAK-Thin model) make different assumptions about how per-SNP heritability scales with LD and MAF:

- **GCTA model (LDSC default):** per-SNP h2 inversely proportional to local LD score; high-LD SNPs tag many causal variants
- **LDAK-Thin (Speed 2017 Nat Genet 49:986-992 introduced the LDAK model; the Thin model was formalized in Speed 2020 Nat Genet 52:458):** per-SNP h2 weighted by MAF and inversely by LD with empirical exponents; less weight on common high-LD SNPs

These give systematically different functional enrichment estimates. Speed 2019 reported that LDAK-Thin often gives **lower** conserved-region enrichment than baseline LDSC; conversely LDSC can over-attribute h2 to coding/conserved regions because the GCTA prior couples LD to causality. Gazal 2019 Nat Genet 51:1202-1204 argues the baseline-LD S-LDSC model is better-calibrated (higher model likelihood) and that LDAK/SumHer's lower functional-enrichment estimates are downward-biased; the LDAK developers dispute this (Speed 2020 Nat Genet 52:458), so report both models and flag the model-dependence.

**Operational rule:** Whenever functional enrichment is the primary claim (e.g. "h2 is enriched in tissue T by N-fold"), report enrichment from BOTH LDSC and LDAK. Flag the model assumption. If LDSC and LDAK disagree by > 2x, treat the claim as model-dependent and cite Gazal 2019. For non-enrichment claims (total h2, rg between two traits), the model dependence is smaller and LDSC alone is acceptable.

## Cell-Type Prioritization (Finucane 2018)

Finucane 2018 Nat Genet 50:621 introduced cell-type-specific S-LDSC: partition heritability against ENCODE / Roadmap chromatin marks (H3K4me3, H3K27ac, H3K4me1, DNase, ATAC) tissue-by-tissue, retain per-tissue p-value adjusting for the baseline model. Trait-relevant tissue = top-ranked tissue with p < 0.05/N_tissues (Bonferroni for ~200 tissues, threshold ~2.5e-4).

**Goal:** Rank tissues / cell types by their per-annotation contribution to trait heritability.

**Approach:** Build per-cell-type LD scores from chromatin-marker BED files; compile `.ldcts` manifest (one row per cell type: name, ldscore prefix, control ldscore); run `--h2-cts` and interpret per-cell-type coefficient p-value.

```bash
# Cell-type prioritization example workflow (Finucane 2018)
# Inputs: trait.sumstats.gz (munged), <cts>.ldcts manifest, baseline annotations,
#         eur_w_ld weights, 1000G EUR frequency files

ldsc.py \
    --h2-cts trait.sumstats.gz \
    --ref-ld-chr 1000G_EUR_Phase3_baseline/baseline. \
    --ref-ld-chr-cts Multi_tissue_chromatin.ldcts \
    --w-ld-chr weights_hm3_no_hla/weights. \
    --out trait_cts
# trait_cts.cell_type_results.txt: Name, Coefficient, Coefficient_std_error, Coefficient_P_value
# Apply Bonferroni at 0.05 / nrow; top tissues are trait-relevant
```

Published `.ldcts` files cover GTEx tissues, Roadmap epigenome, immune cell types, and scATAC clusters. Custom .ldcts for novel cell types requires computing per-cell-type LD scores from a chromatin BED via `ldsc.py --l2 --bfile ... --annot <cell>.annot.gz`.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| mean chi-square > 1.02 | LDSC wiki / Bulik-Sullivan 2015 | Below this, LDSC h2 estimate has huge SE; need N proportional to 1 / h2 |
| h2 SE < 0.02 | LDSC convention | Below this SE, h2 estimate is interpretable; above, treat as exploratory |
| h2 SE >= 0.02 OR mean chi-square < 1.02 | LDSC convention | Estimate unreliable; N >= 50k is typical noise floor for h2 ~ 0.1 (scales as ~1/h2) |
| LDSC intercept in (1, 1.5] | Bulik-Sullivan 2015 | Mild inflation acceptable; report ratio |
| LDSC intercept > 1.5 | -- | Substantial inflation; investigate stratification / overlap before interpreting h2 |
| LDSC ratio < 0.2 | Bulik-Sullivan 2015 | Most inflation is polygenic; estimate is trustworthy |
| Stratified LDSC enrichment p < 0.05 / N_annot | Finucane 2015 | Bonferroni across annotations in the baseline-LD model |
| S-LDSC cell-type p < 2.5e-4 | Finucane 2018; ~200 tissues | Bonferroni for tissue prioritization |
| HESS h2 per locus needs >= 1000 SNPs | Shi 2017 AJHG 101:737 | Quadratic form unstable below this density |
| HDL sample overlap < 5% | Ning 2020 Nat Genet 52:859 | Above 5%, HDL likelihood is biased |
| LDAK tagging file build match | Speed 2019 | hg19 vs hg38 tagging files non-interchangeable |
| Annotation > 0.5% of genome | Finucane 2015 | Smaller categories underpowered for tau estimation |
| Effective N > 5000 per population (Popcorn) | Brown 2016 AJHG 99:76 | Below this, trans-ancestry rg has very wide CI |

## LDSC Standard Workflow

**Goal:** Compute total h2 plus partitioned heritability across functional categories from EUR GWAS summary statistics.

**Approach:** Munge sumstats to LDSC format -> run --h2 for total -> run --h2 with --ref-ld-chr including baseline annotations -> --overlap-annot for enrichment p-values -> --print-coefficients for per-annotation tau.

```bash
# 1. Munge GWAS summary statistics into LDSC format
munge_sumstats.py \
    --sumstats gwas_raw.tsv \
    --N-col N \
    --snp SNP --a1 A1 --a2 A2 --p P --signed-sumstats BETA,0 \
    --merge-alleles w_hm3.snplist \
    --out trait
# Produces trait.sumstats.gz with SNP, A1, A2, Z, N columns

# 2. Total h2 (univariate; intercept, ratio, mean chi2 reported)
ldsc.py \
    --h2 trait.sumstats.gz \
    --ref-ld-chr eur_w_ld_chr/ \
    --w-ld-chr eur_w_ld_chr/ \
    --out trait_h2

# 3. Partitioned h2 with baseline-LD v2.2 model (Gazal 2017)
ldsc.py \
    --h2 trait.sumstats.gz \
    --ref-ld-chr 1000G_Phase3_baselineLD_v2.2_ldscores/baselineLD. \
    --frqfile-chr 1000G_Phase3_frq/1000G.EUR.QC. \
    --w-ld-chr 1000G_Phase3_weights_hm3_no_MHC/weights.hm3_noMHC. \
    --overlap-annot \
    --print-coefficients \
    --out trait_partitioned
```

Ancestry-matched LD scores (EAS, AFR, AMR) are available at alkesgroup.broadinstitute.org/LDSCORE; do NOT apply EUR LD scores to non-EUR GWAS.

## Cross-Trait LDSC for Genetic Correlation

**Goal:** Estimate genetic correlation `rg` between two traits with calibrated handling of sample overlap.

**Approach:** Munge both sumstats with identical SNP list -> run --rg with two munged files; the bivariate intercept absorbs sample overlap and the rg estimate remains unbiased.

```bash
ldsc.py \
    --rg trait1.sumstats.gz,trait2.sumstats.gz \
    --ref-ld-chr eur_w_ld_chr/ \
    --w-ld-chr eur_w_ld_chr/ \
    --out rg
# Output: rg, se, p, gcov_int (cross-trait intercept), h2_obs, h2_int per trait
```

The cross-trait intercept (`gcov_int`) is the LDSC analog of sample-overlap z-score correlation; non-zero indicates sample overlap or cryptic shared structure. LDSC rg is unbiased even with sample overlap because the bivariate intercept absorbs it. HDL is more precise but requires non-overlapping samples.

Non-zero `gcov_int` under known sample overlap is the **correct** behavior, NOT pathology. The rg estimate remains unbiased; the intercept is the overlap absorber, doing its job. Pre-empt the reviewer comment "gcov_int = 0.05 with a shared cohort is expected, not confounding evidence" by reporting `gcov_int` alongside rg and explaining the absorber role.

## Per-Method Failure Modes

### LDSC intercept misinterpretation

**Trigger:** Reporting intercept ~1.05 as "evidence of confounding".

**Mechanism:** Intercept absorbs mean chi-square inflation from any non-polygenic source PLUS some polygenic contribution at very high N. In isolation, intercept above 1 does not imply confounding.

**Symptom:** Methods section claims population stratification based solely on intercept value; reviewers flag the omission of ratio statistic.

**Fix:** Always report intercept, mean chi-square, ratio = (intercept - 1) / (mean_chi2 - 1), and h2 jointly. Interpret ratio < 0.2 as "mostly polygenic, h2 trustworthy"; ratio > 0.3 as "investigate population structure / overlap before claiming h2".

### LDSC vs LDAK enrichment discordance

**Trigger:** Running both LDSC baseline-LD and LDAK SumHer and getting different per-annotation enrichment.

**Mechanism:** GCTA model (LDSC) couples per-SNP h2 to local LD; LDAK-Thin de-couples and re-weights by MAF + LD with empirical exponents. These priors differ; the data alone cannot determine which is correct.

**Symptom:** LDSC reports conserved-region enrichment of 25x; LDAK reports 10x; both are model-internally consistent.

**Fix:** Cite Gazal 2019 Nat Genet 51:1202 as the LDSC-vs-LDAK reconciliation reference; report BOTH models; treat 2x or larger discordance as model-dependent. For enrichment-driven hypotheses (e.g. tissue prioritization), reconcile by reporting LDSC primary + LDAK confirmatory and emphasize directional agreement over magnitude. Do not pick the model that gives the desired answer.

### HDL bias with sample overlap

**Trigger:** Running HDL.rg on two GWAS that share > 5% of samples (e.g. two UKB traits, or UKB + FinnGen with overlapping recruitment).

**Mechanism:** HDL's eigen-decomposition likelihood treats the two traits as independent samples; sample-correlation in residuals biases the likelihood (typically inflates rg toward 1).

**Symptom:** HDL rg substantially different from cross-trait LDSC rg; HDL z-score very large compared to LDSC z; suspicious for high-correlation trait pairs.

**Fix:** Use cross-trait LDSC instead (intercept absorbs overlap). If both must be used, restrict HDL to unambiguously non-overlapping cohorts (e.g. UKB-only trait1 vs FinnGen-only trait2 with no shared individuals confirmed via individual ID exchange or IBD).

### LDSC with non-EUR ancestry and EUR LD scores

**Trigger:** Applying default EUR LD scores from `alkesgroup.broadinstitute.org/LDSCORE/eur_w_ld_chr/` to an EAS, AFR, or AMR GWAS.

**Mechanism:** LD-score regression assumes the LD-score covariate matches the GWAS population's LD structure. Cross-ancestry application produces biased h2 (typically underestimates) and inflated intercept.

**Symptom:** h2 estimate < 0.05 despite trait being known-heritable from twin / family studies; intercept > 1.2 with non-polygenic mean chi-square; ratio > 0.5.

**Fix:** Use ancestry-matched LD scores (EAS, AFR, AMR available at the same Alkes group URL). If multi-ancestry meta-analysis, use Popcorn or trans-ancestry MAMA framework rather than LDSC on the combined sumstats.

### Stratified LDSC with collinear annotations

**Trigger:** Adding a custom annotation that overlaps heavily with an existing baseline category (e.g. "active promoter" against "promoter").

**Mechanism:** Per-annotation tau coefficients are estimated jointly via multivariable regression; collinearity inflates per-tau SE and can flip the sign of marginal effect.

**Symptom:** Custom annotation tau has very large SE, p-value > 0.5; baseline categories that were significant become non-significant.

**Fix:** Test annotations marginal to the baseline by including baseline-LD_v2.2 plus the new annotation only; never test multiple highly correlated annotations jointly; report VIF of annotation matrix; use the joint enrichment of {baseline + new} category not per-tau.

### HESS locus instability at sparse SNP density

**Trigger:** Running HESS at a locus with < 1000 LD-pruned SNPs (e.g. centromere-adjacent region).

**Mechanism:** HESS quadratic form on projected effect estimates is unstable at low SNP density; matrix conditioning explodes.

**Symptom:** Locus h2 estimate negative or > 0.5 (unphysical); standard error very large; subsequent loci stable.

**Fix:** Require >= 1000 SNPs per locus; use LDetect partition (Berisa & Pickrell 2016 Bioinformatics 32:283) which targets ~1700 loci genome-wide; discard sparse loci or merge with neighbors.

### Case-control LDSC observed vs liability scale

**Trigger:** Reporting LDSC h2 from a case-control GWAS on the observed (0/1) scale.

**Mechanism:** Observed-scale h2 depends on case fraction in the GWAS sample, not population prevalence; comparisons across studies require liability-scale transformation.

**Symptom:** h2 looks tiny (0.02) for a known-heritable disease; differs across studies with different case fractions.

**Fix:** Always supply `--samp-prev <case_fraction>` and `--pop-prev <population_lifetime_prevalence>` to LDSC; report h2 on liability scale. Without these flags, LDSC defaults to observed scale. Lee 2011 (AJHG 88:294) conversion: `h2_liab = h2_obs * (K(1-K))^2 / (P(1-P) * z^2)` (numerator is K^2(1-K)^2), where K = population prevalence, P = sample case proportion, z = standard-normal density at the quantile (1-K). LDSC applies this via `--samp-prev/--pop-prev`; verify K and P are assigned correctly (K is population, P is sample). Skipping the conversion typically yields a 2-10x underestimate vs the liability-scale truth.

## LDAK SumHer Pipeline

**Goal:** Alternative h2 and functional enrichment estimate using the LDAK-Thin model for reconciliation with LDSC.

**Approach:** Reformat sumstats to LDAK input -> run `ldak --sum-hers` against the pre-computed LDAK-Thin tagging file -> compare to LDSC.

```bash
# 1. LDAK requires header: Predictor A1 A2 n Z (Z optional; can use beta + se instead)
# Reference LDAK-Thin tagging files at dougspeed.com/pre-computed-tagging-files
ldak --sum-hers trait_sumher \
    --summary trait_ldak.txt \
    --tagfile ldak.thin.hapmap.gbr.tagging \
    --check-sums NO

# 2. Partitioned with BaselineLD annotations (two steps)
# BaselineLD provides binary + continuous annotations covering coding/conserved/regulatory/MAF
# bins; download BaselineLD.zip (96 annotations) from dougspeed.com/resources and extract to ./BaselineLD/BaselineLD{1..96} (the run uses the first 86).
# The annotation flags belong to --calc-tagging (which builds the tagging file), NOT to
# --sum-hers. LDAK uses --annotation-number + --annotation-prefix (continuous) or
# --partition-number + --partition-prefix (binary). No --category-file flag exists.

# 2a. Build the annotated tagging file from a genotype reference (--power -.25 = LDAK-Thin)
ldak --calc-tagging trait_bld --bfile ref_panel --power -.25 \
    --annotation-number 86 \
    --annotation-prefix BaselineLD/BaselineLD

# 2b. Estimate partitioned h2 against that tagging file (no annotation flags here)
ldak --sum-hers trait_bld --summary trait_ldak.txt \
    --tagfile trait_bld.tagging \
    --check-sums NO
```

Pre-computed tagging files exist for GBR (HapMap reference); other ancestries require building tagging file via `--calc-tagging`. LDAK SumHer outputs h2 estimate, per-category h2 share, and enrichment with Z-scores.

## HESS Local h2 Pipeline

**Goal:** Estimate per-locus heritability genome-wide using LDetect partition.

**Approach:** Step 1 computes quadratic forms per locus from LD reference; step 2 estimates h2; output per-locus h2 with SE.

```bash
# HESS step 1: per-chromosome local h2 quadratic forms (run per chromosome)
for chr in {1..22}; do
    hess.py \
        --local-hsqg trait.sumstats.gz \
        --chrom $chr \
        --bfile 1000G_EUR_chr${chr} \
        --partition LDetect_EUR_chr${chr}.bed \
        --out hess_chr${chr}
done

# HESS step 2: aggregate across chromosomes and estimate h2
hess.py \
    --prefix hess_chr \
    --out trait_local_h2 \
    --tot-hsqg <total_h2_estimate> <total_h2_SE>
# Provide total h2 and SE from LDSC for the global constraint
```

LDetect partition files (Berisa & Pickrell 2016) are available pre-computed for EUR/EAS/AFR at https://bitbucket.org/nygcresearch/ldetect-data. HESS detects high-h2 loci suitable for fine-mapping prioritization.

## HDL Genetic Correlation (R)

**Goal:** Genetic correlation with ~60% lower variance than LDSC when samples are non-overlapping.

**Approach:** Reformat sumstats to HDL input -> download UKB reference panel eigen-decomposition -> run HDL.rg.

```r
library(HDL)

# Sumstats need columns: SNP, A1, A2, b (beta), se, N
gwas1 <- read.table('trait1.txt', header = TRUE, stringsAsFactors = FALSE)
gwas2 <- read.table('trait2.txt', header = TRUE, stringsAsFactors = FALSE)

LD.path <- 'UKB_array_SVD_eigen90_extraction'

rg_result <- HDL.rg(gwas1.df = gwas1, gwas2.df = gwas2, LD.path = LD.path,
                    Nref = 335265, output.file = 'hdl_rg.log',
                    eigen.cut = 'automatic')

# rg_result: rg, rg.se, p, h2_1, h2_2, gen.cov
```

HDL UKB reference (`UKB_array_SVD_eigen90_extraction`) requires non-overlapping samples; if either GWAS is from UKB, HDL is biased.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| LDSC h2 negative | Trait truly null heritable; or LD scores ancestry-mismatched | Verify mean chi-square > 1.02; switch to ancestry-matched LD; report as null |
| `munge_sumstats.py` drops > 50% of SNPs | Allele mismatch with HapMap3 SNPlist; or A1/A2 swapped | Inspect drop reasons; pre-harmonize alleles; check rsID format |
| LDSC intercept > 1.5 | Population stratification, cryptic relatedness, or extensive sample overlap | Report jointly with ratio; investigate per-cohort PC adjustment |
| Stratified LDSC enrichment > 100x | Tiny annotation (<0.1% genome) underpowered | Set annotation size floor >= 0.5%; report joint enrichment of larger composite category |
| LDAK h2 markedly different from LDSC h2 | Model assumption divergence (GCTA vs LDAK-Thin) | Per Gazal 2019 / Hou 2019; report both and flag model-dependence |
| HDL rg = NA or numerical error | Sumstat format wrong; or eigen.cut too aggressive | Use eigen.cut='automatic'; check column names exactly |
| HESS locus h2 negative | < 1000 SNPs in locus; LD ref-stat mismatch | Drop locus or merge with neighbor; ensure LD ref matches GWAS ancestry |
| `--samp-prev/--pop-prev` not supplied for case-control | LDSC defaults to observed scale | Always supply both for case-control; report liability-scale h2 |
| Cell-type S-LDSC: no tissue p < 2.5e-4 | Trait underpowered for tissue prioritization (mean chi-square low) | Pool with related traits via MTAG; or report no tissue distinguishable |
| LDAK tagging file: build mismatch | Using hg19 tagging on hg38 GWAS sumstats | Tagging files are build-specific; download matched build |
| BOLT-REML "matrix not positive definite" | GRM has duplicated individuals or extreme relatedness | Pre-filter to unrelated < 0.05 kinship; or use REML method-of-moments instead |
| `munge_sumstats.py`: missing N column | Per-SNP N column not supplied | Pass `--N <Ntot>` (numeric total) OR `--N-col N` (column name); pick one |
| `munge_sumstats.py`: all SNPs drop silently | A1/A2 flipped relative to HM3 reference (`--merge-alleles`) | Verify allele coding matches `w_hm3.snplist`; pre-harmonize or swap A1 <-> A2 |
| `munge_sumstats.py` drops multi-allelic SNPs | Expected behavior (LDSC requires biallelic) | Document the drop count in methods; not a fix |
| Sign of Z reversed across studies | `--signed-sumstats BETA,0` vs `--signed-sumstats Z,0` confusion | Use `BETA,0` for additive effect sign convention, `Z,0` for Z-score; never both; verify direction with a known sentinel SNP |

## Tool Install Notes

```bash
# LDSC Python 3 fork (official bulik/ldsc is Python 2.7, unmaintained since 2019)
# IMPORTANT: belowlab/ldsc v3.0.1 broke the --h2 / --rg / --h2-cts CLI per its README.
# For a working CLI matching the flags below, use abdenlab/ldsc-python3 (v2.0.0)
# OR run belowlab/ldsc via Docker: `docker pull jtb114/ldsc:latest`.
git clone https://github.com/abdenlab/ldsc-python3.git   # working CLI
cd ldsc-python3
pip install .   # abdenlab/ldsc-python3 is a Poetry project (pyproject.toml); no environment.yml/requirements.txt

# LDAK 6+
wget https://raw.githubusercontent.com/dougspeed/LDAK/main/ldak6.3.linux
chmod +x ldak6.3.linux

# Pre-computed reference resources (one-time download)
# EUR LD scores (HapMap3 SNPs)
wget https://alkesgroup.broadinstitute.org/LDSCORE/eur_w_ld_chr.tar.bz2
# Baseline-LD v2.2 (Gazal 2017)
wget https://alkesgroup.broadinstitute.org/LDSCORE/1000G_Phase3_baselineLD_v2.2_ldscores.tgz
# 1000G EUR frequency files
wget https://alkesgroup.broadinstitute.org/LDSCORE/1000G_Phase3_frq.tgz
# Weights
wget https://alkesgroup.broadinstitute.org/LDSCORE/1000G_Phase3_weights_hm3_no_MHC.tgz
# Multi-tissue chromatin ldcts (Finucane 2018)
wget https://alkesgroup.broadinstitute.org/LDSCORE/Multi_tissue_chromatin_1000Gv3_ldscores.tgz
```

```r
# HDL
remotes::install_github('zhenin/HDL/HDL')
# HDL UKB reference (downloads ~5 GB)
# https://github.com/zhenin/HDL/wiki/Reference-panels
```

```bash
# HESS (Python 2 by default; Python 3 fork: huwenboshi/hess Python 3 branch)
git clone https://github.com/huwenboshi/hess.git
pip install -r hess/requirements.txt

# BOLT-LMM / BOLT-REML
wget https://alkesgroup.broadinstitute.org/BOLT-LMM/downloads/BOLT-LMM_v2.4.1.tar.gz

# GCTA
wget https://yanglab.westlake.edu.cn/software/gcta/bin/gcta-1.94.1-linux-kernel-3-x86_64.zip

# Popcorn
git clone https://github.com/brielin/Popcorn.git && cd Popcorn && pip install .
```

## References

- Bulik-Sullivan BK et al 2015 Nat Genet 47:291 (LDSC)
- Bulik-Sullivan BK et al 2015 Nat Genet 47:1236 (cross-trait LDSC genetic correlation)
- Finucane HK et al 2015 Nat Genet 47:1228 (stratified LDSC baseline)
- Gazal S et al 2017 Nat Genet 49:1421 (baseline-LD model)
- Shi H & Gazal S et al 2021 Nat Commun 12:1098 (S-LDXR / baseline-LD-X cross-population)
- Finucane HK et al 2018 Nat Genet 50:621 (cell-type S-LDSC)
- Speed D et al 2017 Nat Genet 49:986-992 (LDAK model; cross-validation model comparison)
- Speed D, Holmes J & Balding DJ 2020 Nat Genet 52:458 (LDAK-Thin model; heritability model comparison)
- Speed D et al 2019 Nat Genet 51:277 (SumHer)
- Gazal S et al 2019 Nat Genet 51:1202-1204 (LDSC vs LDAK reconciliation, model-dependence)
- Hou K et al 2019 Nat Genet 51:1244 (heritability accuracy and h2 model comparison)
- Ning Z et al 2020 Nat Genet 52:859 (HDL)
- Shi H et al 2016 AJHG 99:139 (HESS univariate)
- Shi H et al 2017 AJHG 101:737 (HESS bivariate local rg)
- Loh PR et al 2015 Nat Genet 47:1385 (BOLT-REML)
- Yang J et al 2011 AJHG 88:76 (GCTA-GREML)
- Brown BC et al 2016 AJHG 99:76 (Popcorn trans-ancestry rg)
- Berisa T & Pickrell JK 2016 Bioinformatics 32:283 (LDetect locus partition)
- Li H, Kamath T, Mazumder R, Lin X, O'Connor LJ 2024 medRxiv 2024.11.04.24316716 (graphREML; published Nat Genet 2026)

## Related Skills

- causal-genomics/mendelian-randomization - h2 / rg-aware instrument selection and one-sample-equivalent design decisions
- causal-genomics/colocalization-analysis - Per-locus shared-causal evidence complementary to HESS local h2
- causal-genomics/fine-mapping - Credible-set construction at high-h2 HESS loci
- causal-genomics/pleiotropy-detection - Cross-trait pleiotropy via LCV / LHC-MR using LDSC outputs
- causal-genomics/genomic-sem - Genomic SEM extends LDSC rg to multivariate structural models
- causal-genomics/transcriptome-wide-association - TWAS uses partitioned-h2 weights for gene-level testing
- atac-seq/differential-accessibility - Per-cell-type chromatin annotations as S-LDSC input
- atac-seq/single-cell-atac - scATAC peaks per cluster as Finucane 2018 .ldcts annotations
- chip-seq/peak-calling - ENCODE / Roadmap chromatin marks for cell-type prioritization
- population-genetics/association-testing - GWAS source summary statistics for LDSC munging
- population-genetics/linkage-disequilibrium - LD reference panels for HESS / coloc.susie
- workflows/gwas-pipeline - Upstream GWAS pipeline feeding sumstats to LDSC
<!-- END FILE: causal-genomics/heritability-partitioning/SKILL.md -->

## 子目录：causal-genomics/mediation-analysis

<!-- BEGIN FILE: causal-genomics/mediation-analysis/SKILL.md -->
---
name: bio-causal-genomics-mediation-analysis
description: Decompose total effects into direct and indirect paths through mediators using mediation, CMAverse 4-way, HIMA/HIMA2 high-dimensional, BAMA, two-step / MVMR mediation, or double-ML medDML. Use when testing whether a molecular phenotype (expression, methylation, protein) mediates a treatment-outcome relationship, decomposing exposure-mediator interaction via VanderWeele 4-way, screening high-dimensional EWAS mediators, or running MR-based mediation when sequential ignorability is implausible.
tool_type: mixed
primary_tool: mediation
---

## Version Compatibility

Reference examples tested with: R 4.3+, mediation 4.5.0+, CMAverse 0.1.0+ (GitHub `BS1125/CMAverse`), HIMA >= 2.3.0 (GitHub `YinanZheng/HIMA`; archived from CRAN 2026-07), bama 1.3+, causalweight 1.0.5+ (medDML), MVMR 0.4+, TwoSampleMR 0.6+, EValue 4.1+, gesttools 1.3+, ipw 1.0.11+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- HIMA must be pinned at `>= 2.3.0` for the code patterns below; the formula interface `hima(formula, data.pheno, data.M, mediator.type, penalty, ...)` was introduced in 2.3.0. On HIMA 2.2.x the classic engine is the top-level `hima(X, Y, M, COV.XM=, COV.MY=, Y.family=, penalty=)` (positional order X, Y, M) with no formula interface; HIMA 2.2.x is NOT API-compatible with the examples here.
- In 2.3+ the classic engine is `hima_classic(X, M, Y, COV.XM=, COV.MY=, Y.type=)` (positional order X, M, Y; outcome type via `Y.type`, not `Y.family`); use it only to reproduce the original 2016-2021 SIS+penalty pipelines.

If code throws an error, introspect the installed package (`?hima`, `args(cmest)`) and adapt the example to match the actual API rather than retrying.

# Mediation Analysis

**"Does expression of GENE_X mediate the SNP-to-disease effect?"** -> Decompose the total effect of a treatment (genotype, exposure) on an outcome into direct and indirect paths through one or more mediators, with explicit handling of exposure-mediator interaction, sensitivity to unmeasured confounding, and high-dimensional mediator screening.

- R (single-mediator, observational, sequential-ignorability assumed): `mediation::mediate(med_model, out_model, treat='X', mediator='M', boot=TRUE, sims=5000)`
- R (4-way decomposition with exposure-mediator interaction): `CMAverse::cmest(...EMint=TRUE, estimation='paramfunc', inference='bootstrap', nboot=1000)`
- R (high-dimensional / EWAS mediators): `HIMA::hima(Y ~ X + covariates, data.pheno, data.M, mediator.type='gaussian', penalty='DBlasso')` (modern v2.3+ formula interface)
- R (MR-based mediation): two-step `TwoSampleMR` with independent instruments OR `MVMR::ivw_mvmr` for joint direct effect
- R (doubly-robust double-ML): `causalweight::medDML(y, d, m, x)`

Sequential ignorability (no unmeasured confounder of treatment-mediator, mediator-outcome, treatment-outcome) is the single load-bearing assumption of observational mediation and is fundamentally untestable. Every report should include a sensitivity result (Imai's rho via `medsens()` or a mediational E-value).

## Algorithmic Taxonomy

| Method | Framework | Handles E-M interaction | High-D mediators | Min n | Fails when |
|--------|-----------|--------------------------|------------------|-------|------------|
| Baron-Kenny (1986) | Additive regression-based product/difference | No | No | ~100 | Any non-linearity, interaction, or binary outcome; deprecated for causal inference |
| Imai mediation R (Imai 2010 Psychol Methods) | Counterfactual ACME/ADE with bootstrap | Yes (via interaction term in outcome model) | No | ~200 | Sequential ignorability violated; exposure-induced M-Y confounder; rare binary outcome with logistic outcome model |
| VanderWeele 4-way (VanderWeele 2014 Epidemiology 25:749; 2015 OUP) | CDE + PIE + INTref + INTmed decomposition | Native | No | ~300 | Without interaction term reduces to standard mediation; binary outcome needs rare-disease assumption |
| CMAverse (Shi 2021 Epidemiology 32:e20) | 6 estimators: regression (`rb`), weighting (`wb`), IORW (`iorw`), natural effect models (`ne`), MSM (`msm`), g-formula (`gformula`) | Yes | No (single M, or M-vector) | ~300 | Estimator-specific; `wb` fails with rare exposure; `msm` needs censoring weights for survival |
| HIMA1 / hima_classic (Zhang 2016 Bioinformatics 32:3150) | SIS screen by beta (M->Y) + MCP penalty | No | Yes (up to ~10k) | ~150 + p>>n | Misses mediators with strong alpha and weak beta; screening-step false-negatives |
| HIMA2 / hima (Perera 2022 BMC Bioinformatics 23:296) | SIS screen by alpha*beta (indirect effect) + de-biased Lasso (DBlasso) | No (linear by default) | Yes | ~150 | Outcome family limited (gaussian/binomial); HIMA-Cox for survival; HIMA-Pois for count |
| HILAMA (Wang et al 2025) | High-D mediation with latent confounders | No | Yes (>= 100k) | ~500 | Newer; benchmarks evolving; requires latent-factor specification |
| BAMA (Song 2020 Biometrics) | Bayesian high-D continuous shrinkage | No | Yes (~5k) | ~200 | Slow MCMC; prior sensitivity for very weak mediators |
| Two-step MR / network MR (Burgess 2015 IJE 44:484) | IV-based at each step with INDEPENDENT instruments | Implicit (no interaction modeling) | One mediator at a time | Large summary-stat samples | Same SNP used for E and M (violates exclusion); horizontal pleiotropy; Steiger reversal of M->E direction |
| MVMR-mediation (Carter & Sanderson 2021 Eur J Epidemiol 36:465-478) | Total minus direct via MVMR | Implicit | Single mediator | Large GWAS samples for both E and M | Conditional F < 10 for either exposure; correlated instruments |
| medDML (Farbmacher 2022 Econometrics J 25:277) | Double-debiased ML, doubly-robust | Limited (depends on learner) | Moderate (sparsity-friendly) | ~500 | Severe overlap violations; cross-fitting variance with small n |

Methodology evolves; verify against the current CMAverse vignette and the Steen / Vansteelandt natural-effects-model literature before locking analytic choices. Difference-in-coefficients and product-of-coefficients give identical estimates in fully linear-Gaussian models but DIVERGE for any non-linear outcome model (logistic, Cox, Poisson); the counterfactual ACME from `mediation::mediate()` is the correct quantity for non-linear outcomes.

## 4-Way Decomposition Framework

VanderWeele 4-way explicitly separates effects from exposure-mediator interaction:

```
Total Effect = CDE + INTref + INTmed + PIE
```

| Component | Meaning | Active when |
|-----------|---------|-------------|
| CDE | Controlled direct effect (with mediator fixed at reference level) | E directly affects Y |
| INTref | Interaction-reference -- needs interaction AND exposure | E*M interaction with mediator at reference |
| INTmed | Mediated interaction -- needs interaction AND exposure AND mediation | E shifts M which then interacts with E |
| PIE | Pure indirect effect (older "mediation" quantity) | E shifts M which shifts Y additively |

Without an exposure-mediator interaction term, INTref = INTmed = 0 and the decomposition collapses to CDE + PIE (= ADE + ACME). With interaction present, traditional ACME mixes PIE and INTmed; the 4-way separation is the only framework that disentangles them. Most epidemiology applications include the interaction term and report all four components (Valeri & VanderWeele 2013 Psychol Methods).

## Decision Tree by Scenario

| Scenario | Recommended pipeline |
|----------|---------------------|
| Observational, single measured mediator, no plausible E-M interaction, continuous outcome | `mediation::mediate()` with `boot=TRUE, sims=5000`; always run `medsens()` |
| Observational, single mediator, suspected E-M interaction, any outcome family | `CMAverse::cmest(..., EMint=TRUE)` -> read CDE, PIE, INTref, INTmed |
| Observational, BINARY outcome, rare disease (< 10%) | `cmest(yreg='logistic', EMint=TRUE, casecontrol=FALSE)` -- OR-based 4-way decomposition is valid under rare-disease |
| Observational, survival outcome | `cmest(yreg='coxph')` OR `HIMA::hima_cox` for high-D; report HRs |
| High-D mediators (EWAS, transcriptome-wide), continuous outcome | `HIMA::hima(formula, data.pheno, data.M, mediator.type='gaussian', penalty='DBlasso')`; report `sigcut` (FDR threshold, default 0.05) |
| High-D mediators with latent confounding (very-high-D EWAS) | `HILAMA` (2025) |
| High-D mediators with Bayesian shrinkage (small n, ~5k features) | `bama::bama()` |
| Strong genetic IVs for exposure available, single mediator with own IVs | Two-step MR with independent instruments + Steiger filter on mediator |
| Both E and M have IVs but instruments are weak / correlated | MVMR-mediation with conditional F > 10 each |
| Observational with rich confounder set, want doubly-robust estimate | `causalweight::medDML` (double-debiased ML) |
| Longitudinal with time-varying confounding | g-formula via `CMAverse::cmest(estimation='gformula')` OR `gfoRmula` package |
| Exposure-induced confounder of M-Y exists | Interventional indirect effects (Vansteelandt & Daniel 2017); `CMAverse::cmest(estimation='msm')` |

## Sequential Ignorability and Why It Always Needs Sensitivity

Observational mediation requires three no-unmeasured-confounding assumptions. The third (M-Y unmeasured confounder, after conditioning on E) is the most common violator in genomic mediation because biological confounders (cell composition, batch effects, technical mediators) frequently affect both M and Y.

### Sequential ignorability untestable

**Trigger:** Always, by design.

**Mechanism:** No statistical test can detect an unmeasured confounder of M-Y. Bootstrap CIs assume the assumption holds; they do NOT propagate uncertainty about it.

**Symptom:** Significant ACME with no sensitivity reported -> reviewer rejects.

**Fix:** Report at least one of:
- Imai's rho sensitivity: `medsens(med_result, rho.by=0.05, sims=1000)`; the critical rho where ACME crosses 0; |rho_crit| > 0.3 is "reasonably robust" (Imai 2010), |rho_crit| < 0.1 is highly sensitive.
- Mediational E-value (Smith & VanderWeele 2019 Epidemiology 30:835): minimum risk-ratio strength of an unmeasured confounder needed to nullify the observed indirect effect; computed via `EValue::evalues.OLS()` for linear outcomes or by-hand from ACME risk ratio bounds.
- Reporting BOTH rho-based and E-value sensitivity is standard for high-stakes claims.

### Methods-Section Defense of Sequential Ignorability

Template sentence for the methods write-up: "We assumed sequential ignorability conditional on {age, sex, ancestry PCs, cell composition, batch, smoking}. Robustness was assessed via Imai rho_crit at the ACME contrast (`medsens`, sims = 1000) and the mediational E-value on the risk-ratio scale (Smith & VanderWeele 2019 Epidemiology 30:835)."

Quantitative interpretation thresholds:
- rho_crit: |rho_crit| > 0.3 robust; 0.1-0.3 moderately sensitive; < 0.1 highly sensitive (Imai 2010).
- E-value: E > 2 robust to plausible biological confounding; 1.5-2 moderate; < 1.5 fragile (Smith & VanderWeele 2019).

For high-stakes claims (clinical, drug-target, regulatory submissions) report BOTH rho_crit and the mediational E-value; for exploratory work either alone suffices.

### Exposure-induced M-Y confounder

**Trigger:** A covariate L sits between E and Y, AND is affected by E, AND confounds M-Y.

**Mechanism:** Standard regression-based mediation cannot adjust for L without blocking part of the indirect effect (collider stratification bias). Adjusting biases CDE; not adjusting biases ACME.

**Symptom:** Sensitivity to confounder set; ACME flips sign when L is added vs removed.

**Operational identification:** From the DAG, L is a covariate of M and Y that is also affected by E. VanderWeele TJ, Vansteelandt S & Robins JM 2014 (Epidemiology 25:300) give the criterion: if L is adjusted, part of the indirect E -> L -> M -> Y pathway is blocked; if L is not adjusted, L confounds the M-Y leg. Both are wrong under natural-effects; the natural indirect effect is simply not identified.

**Fix:** Switch to **interventional indirect effects** (Vansteelandt & Daniel 2017 Epidemiology 28:258), NOT natural indirect effects. Use `CMAverse::cmest(estimation='msm')` with stabilized inverse-probability weights (yields the randomized-interventional analogue), `gfoRmula` (parametric g-formula), or randomized/interventional indirect effects (Lin SH & VanderWeele TJ 2017 J Causal Inference 5:20150027). The interventional indirect is identified under weaker assumptions than the natural indirect.

### HIMA covariate or data.pheno error

**Trigger:** `data.pheno` contains factor columns with NA, or formula references columns missing from `data.pheno`.

**Mechanism:** HIMA v2.3+ uses a formula interface and constructs the design matrix internally from `data.pheno`; missing values or unparseable formulas surface as cryptic `glmnet` errors.

**Symptom:** Pipeline fails inside `hima()` with a non-obvious `storage.mode` or `model.matrix` error.

**Fix:** Pre-clean `data.pheno` (drop NA rows for the variables in the formula; convert factors with `factor()`; ensure all RHS variables exist as columns). Example:
```r
dat <- na.omit(dat[, c('outcome', 'exposure', 'age', 'sex', 'batch', 'pc1', 'pc2')])
dat$batch <- factor(dat$batch)
result <- hima(outcome ~ exposure + age + sex + batch + pc1 + pc2,
               data.pheno=dat, data.M=M_matrix, mediator.type='gaussian')
```

### HIMA mediator-type vs outcome-type mismatch

**Trigger:** Survival outcome (`Surv()` on LHS) with `mediator.type='compositional'` chosen against text mediator panel; or count mediators passed as `'gaussian'`.

**Mechanism:** HIMA v2.3+ auto-detects outcome family from the LHS of `formula` (continuous, binary, survival, count); `mediator.type` is set for the mediator data only (`'gaussian'`, `'negbin'`, `'compositional'`). Mismatching mediator-type to the actual mediator distribution biases the screening step.

**Symptom:** Hazard / rate ratios for indirect effects look implausible; many "significant" mediators fail replication.

**Fix:** Set `mediator.type='gaussian'` for continuous (e.g., methylation beta, log-CPM expression), `'negbin'` for raw count (RNA-seq), `'compositional'` for relative-abundance microbiome. Verify by `?hima` in the installed version since the catalogue of mediator types has expanded across releases.

### Bootstrap iterations too low

**Trigger:** `sims=100` or `sims=500` in early exploration left in for the final report.

**Mechanism:** ACME CIs from bootstrap have Monte-Carlo error that scales as 1/sqrt(sims); at sims=500 the 95% CI bounds have ~5% MC noise, enough to flip the conclusion at the boundary.

**Symptom:** Re-running `mediate()` with a different `set.seed()` gives substantially different CI bounds.

**Fix:** `sims=1000` minimum for any reported result; `sims=5000` for publication; `sims=10000` if proximity to zero matters. BCa CIs (`boot.ci.type='bca'` in `mediate()`) are slightly more accurate than percentile CIs near zero but require more sims for stability.

### Two-step MR instrument independence

**Trigger:** Same set of SNPs used as instruments for E in step 1 and for M in step 2.

**Mechanism:** If a SNP affects both E and M, the M-instrument violates exclusion restriction (the SNP-Y association is not exclusively through M). Estimates are biased toward the direct effect.

**Symptom:** Two-step MR shows large indirect effect; replacing M-instruments with non-overlapping SNPs makes it vanish.

**Fix:** Apply Steiger filter on the mediator: keep only SNPs where the SNP-M F-statistic exceeds SNP-E F-statistic (or where SNP explains more variance in M than E). For MVMR-mediation, require conditional F > 10 for each exposure independently (Sanderson 2019 IJE 48:713).

### Difference vs product of coefficients diverge for non-linear outcomes

**Trigger:** Binary or survival outcome modeled with logistic / Cox.

**Mechanism:** Difference = total - direct; product = alpha * beta. Equivalent under linear-Gaussian; diverge under any link function. Counterfactual ACME from `mediation::mediate()` is the correct quantity; hand-computed product-of-coefficients on logistic output is biased except under rare-disease.

**Fix:** Report only counterfactual ACME (Imai or CMAverse). For OR-based 4-way decomposition on rare outcomes (<= 10%), Valeri & VanderWeele 2013 formulas apply; for common outcomes use risk-ratio scale or marginal effects rather than ORs.

### Required Reporting for Publication

| Component | Required |
|-----------|----------|
| ACME estimate + 95% CI (BCa preferred) | Yes |
| ADE + 95% CI | Yes |
| Total effect | Yes |
| Proportion mediated | Yes when total > effect-size threshold |
| Bootstrap method + sims | percentile / BCa; min 1000, recommend 5000 |
| Sequential ignorability sensitivity | rho_crit (medsens) OR mediational E-value |
| Exposure-mediator interaction test | Coefficient + p; 4-way decomposition if significant |
| Confounder set justification | DAG description |
| Mediator measurement reliability | Cite |
| Sample size + missing-data handling | Yes |
| Mediator / exposure scale | Standardized? log? raw? |

Reference: AGReMA guideline (Lee H et al 2021 JAMA 326:1045) and MacKinnon 2008 Introduction to Statistical Mediation Analysis.

## Reconciliation: Observational vs MR Mediation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Observational ACME significant; MR-mediation null | Unmeasured M-Y confounding inflated observational estimate; OR weak IVs in MR | Re-run observational with `medsens()`; if rho_crit < 0.1, trust MR null |
| Observational ACME null; MR-mediation significant | Measurement error in M attenuated observational estimate | Trust MR (regression-dilution-free) IF instruments pass Steiger and pleiotropy tests (MR-Egger intercept, MR-PRESSO) |
| Both significant with same sign | Convergent evidence | High-confidence mediation; report effect size from the more-conservative estimate |
| Both significant with opposite signs | At least one is biased; revisit confounder structure and IV assumptions | Do not pool; investigate via cross-method sensitivity |

**Operational rule for high-stakes claims (clinical / drug-target mediation):** Require (1) significant observational ACME, (2) Imai rho_crit > 0.2 OR mediational E-value > 1.5, (3) directionally consistent MR-mediation result OR documented absence of valid instruments. Single-method mediation claims should be reported as exploratory.

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Sequential ignorability?" | Imai rho_crit reported via `medsens`; mediational E-value reported on the risk-ratio scale |
| "Exposure-induced confounder of M-Y?" | DAG drawn; if L present, switch to `CMAverse::cmest(estimation='msm')` for interventional indirect effect (Vansteelandt & Daniel 2017) |
| "Why this bootstrap method?" | BCa with sims=5000 for publication; percentile fallback when BCa fails to converge (acceleration estimate unstable at boundary) |
| "Why was MR-mediation not done?" | If valid IVs for E and M exist: two-step MR or MVMR-mediation done (see code below); if not, documented absence of trans-instruments |
| "Mediator measured with error?" | Regression calibration (Carroll 2006 Measurement Error in Nonlinear Models) OR sensitivity analysis assuming reliability r = 0.7 (Valeri & VanderWeele 2014) |
| "Why HIMA2 not BAMA?" | HIMA2 = frequentist + FDR control + faster; BAMA = Bayesian when prior information is available; sample-size justification given against simulation rule-of-thumb |
| "Proportion mediated unstable?" | When |total| < 2*SE(total), proportion-mediated CI is unreliable (denominator near zero); report indirect effect alone with absolute effect size |

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|--------------------|
| `sims` (bootstrap iterations) | >= 1000 exploratory, >= 5000 publication | Imai 2010; MC error scales 1/sqrt(sims) |
| Proportion mediated -- meaningful | > 0.2 | Convention; weak guideline only -- effect size in absolute terms matters more (MacKinnon 2008) |
| Proportion mediated -- "most of the effect" | > 0.5-0.8 | Convention |
| Imai rho_crit -- robust | > 0.3 | Imai 2010 Psychol Methods 15:309 |
| Imai rho_crit -- sensitive | < 0.1 | Same |
| Mediational E-value -- robust | > 2.0 (working convention; the original Smith & VanderWeele 2019 E-value framework does not prescribe a specific cutoff -- magnitude is context-dependent) | Smith & VanderWeele 2019 Epidemiology 30:835 |
| HIMA FDR cutoff | BH FDR < 0.05 | Default; report q-values not raw p |
| MVMR conditional F per exposure | > 10 each | Sanderson 2019 IJE 48:713 |
| Two-step MR -- F for both stages | > 10 each | Burgess weak-instrument convention |
| Sample size -- single-mediator (Imai) | >= 200 for stable bootstrap | Simulation rule-of-thumb |
| Sample size -- HIMA EWAS | >= 150 with p_mediators up to ~10k | Zhang 2016 simulations |
| Rare-outcome cutoff for OR-based 4-way | outcome prevalence <= 10% | Valeri & VanderWeele 2013 |

## Working Code Patterns

### Single-Mediator Observational with Sensitivity

**Goal:** Decompose a genotype-disease effect via measured molecular mediator with explicit sensitivity to unmeasured M-Y confounding.

**Approach:** Fit mediator and outcome models, bootstrap ACME/ADE, run `medsens()` for Imai rho-based sensitivity.

```r
library(mediation)

med_model <- lm(expression ~ genotype + age + sex + pc1 + pc2 + pc3, data=dat)
out_model <- glm(disease ~ genotype + expression + age + sex + pc1 + pc2 + pc3,
                 data=dat, family=binomial)

med_result <- mediate(med_model, out_model,
                      treat='genotype', mediator='expression',
                      boot=TRUE, sims=5000, boot.ci.type='bca')
summary(med_result)

sens <- medsens(med_result, rho.by=0.05, effect.type='indirect', sims=1000)
summary(sens)
```

`d0`, `z0`, `n0`, `tau.coef` slots return ACME, ADE, proportion mediated, total effect.

### 4-Way Decomposition with Exposure-Mediator Interaction

**Goal:** Separate CDE, PIE, INTref, INTmed when exposure-mediator interaction is biologically plausible (e.g., gene-environment interaction modifying mediator effect).

**Approach:** Use CMAverse regression-based estimator with `EMint=TRUE`; bootstrap CIs.

```r
library(CMAverse)

result_4way <- cmest(
  data=dat, model='rb',
  outcome='disease', exposure='genotype', mediator='expression',
  basec=c('age','sex','pc1','pc2'),
  EMint=TRUE,
  mreg=list('linear'), yreg='logistic',
  astar=0, a=1, mval=list(0),
  estimation='paramfunc', inference='bootstrap', nboot=1000
)
summary(result_4way)
```

CMAverse reports the 4-way decomposition (Vanderweele 2014): for continuous outcomes the components are `cde`, `intref`, `intmed`, `pnie` (or `pie`), `te`, `pm`; for non-continuous outcomes (logistic / Cox / Poisson) the ratio versions `Rcde`, `Rpnde`, `Rtnde`, `Rpnie`, `Rtnie` are reported. When `EMint=TRUE`, additional proportion-attributable-to-interaction terms (`int`, `pe`) are included. Verify column names with `summary(result)$results` in the installed CMAverse version, since naming has evolved.

### High-Dimensional EWAS Mediation (HIMA2)

**Goal:** Among thousands of candidate CpG mediators, identify those mediating an exposure-outcome effect with FDR control.

**Approach:** HIMA v2.3+ uses a formula interface and auto-detects outcome family (Gaussian / binomial / Cox / Poisson). Screening + MCP/DBlasso penalisation + joint significance with BH; the `sigcut` argument controls the FDR threshold (default 0.05).

```r
library(HIMA)

dat <- na.omit(dat[, c('outcome', 'exposure', 'age', 'sex', 'cell_pc1', 'cell_pc2')])
M_matrix <- as.matrix(beta_values)

result <- hima(
  outcome ~ exposure + age + sex + cell_pc1 + cell_pc2,
  data.pheno=dat,
  data.M=M_matrix,
  mediator.type='gaussian',          # 'negbin' for count, 'compositional' for microbiome
  penalty='DBlasso',                  # default; alternatives 'MCP', 'SCAD', 'lasso'
  scale=TRUE,
  sigcut=0.05,
  parallel=TRUE, ncore=8, verbose=TRUE
)
# result is a data.frame of significant mediators below sigcut
```

For survival outcomes wrap the LHS as `Surv(time, status)`; HIMA auto-routes to Cox. The old `hima_classic()` (Zhang 2016 original) is still exported but screens by beta only and misses mediators with strong alpha + weak beta -- prefer the wrapper `hima()` unless reproducing a 2016-2021 paper.

For highly-correlated mediators (CpG-island clusters, gene-module co-expression): HIMA uses joint significance with BH-FDR on max(p_alpha, p_beta) and handles correlation only weakly. Within `hima()`, set `penalty='MCP'` for stronger correlation handling; alternatively pre-reduce the mediator panel by principal components or by clustering correlated mediators and screening the cluster centroid (VanderWeele & Vansteelandt 2014 Epidemiol Methods 2:95).

### Time-Varying Mediation Methods

When the mediator is measured at multiple timepoints (or exposure varies over time), natural-effects estimands are not identified; switch to one of:

- g-formula (parametric or Monte Carlo): `gfoRmula::gformula_continuous_eof()`; `CMAverse::cmest(estimation='gformula')`
- g-estimation of a structural nested mean model: `gesttools::gestSingle()` / `gestMultiple()`
- Marginal structural model with stabilized IPTW: `ipw::ipwtm()` followed by `glm(..., weights=sw)`
- Sequential mediation for K timepoints: VanderWeele & Tchetgen Tchetgen 2017 JRSSB 79:917

Choose based on the experimental structure:
- >= 3 timepoints required for g-methods to identify time-varying indirect effects
- Longitudinal mediator measurement at EACH timepoint is required (not just baseline)
- MSM is preferred when treatment is binary and time-varying; g-formula when continuous
- Sequential mediation when the causal ordering of multiple mediators is known and stable across time

### MR-Mediation: Two-Step vs MVMR-Mediation

Decision tree:
- Independent instrument sets available for E and M -> two-step MR (Burgess 2015 IJE 44:484)
- E and M share instruments (common in cis-eQTL / cis-pQTL mediator cases) -> MVMR-mediation (Carter & Sanderson 2021 Eur J Epidemiol 36:465)
- Both feasible -> report both (triangulation)

Two-step code sketch:

```r
library(TwoSampleMR)
exp_E <- extract_instruments('ieu-a-2', clump=TRUE)
m_E <- extract_outcome_data(exp_E$SNP, 'ieu-b-30')
dat_EM <- harmonise_data(exp_E, m_E)
mr_EM <- mr(dat_EM)

exp_M <- extract_instruments('ieu-b-30', clump=TRUE)
exp_M_indep <- exp_M[!exp_M$SNP %in% exp_E$SNP, ]
exp_M_indep <- steiger_filtering(exp_M_indep)
out_M <- extract_outcome_data(exp_M_indep$SNP, 'ieu-a-7')
dat_MY <- harmonise_data(exp_M_indep, out_M)
mr_MY <- mr(dat_MY)
```

Indirect effect = beta_EM * beta_MY (product of coefficients). CI via delta method or parametric bootstrap of the joint (beta_EM, beta_MY) distribution. Steiger filter on M-instruments is mandatory to ensure the M -> Y direction (not Y -> M).

### MR-Mediation: Total Minus Direct via MVMR

**Goal:** Estimate the proportion of a genetic-instrument-identified causal effect that flows through a mediator, using independent IVs for E and (E + M).

**Approach:** Univariable MR for total E->Y; MVMR for direct E->Y conditional on M; indirect = total - direct via delta-method CI.

```r
library(TwoSampleMR); library(MVMR)

total <- mr_ivw(beta_E, beta_Y, se_E, se_Y)
mvmr_dat <- format_mvmr(BXGs=cbind(beta_E, beta_M),
                        BYG=beta_Y, seBXGs=cbind(se_E, se_M), seBYG=se_Y, RSID=snps)
fstat <- strength_mvmr(mvmr_dat, gencov=0)
mvmr_fit <- ivw_mvmr(mvmr_dat)
direct <- mvmr_fit[1, 'Estimate']
direct_se <- mvmr_fit[1, 'Std. Error']

indirect <- total$b - direct
indirect_se <- sqrt(total$se^2 + direct_se^2)
indirect_ci <- indirect + c(-1.96, 1.96) * indirect_se
```

Require `fstat` conditional F > 10 for both E and M independently. If `fstat < 10`, use Q-statistic-adjusted IVW (`qhet_mvmr`) or report the result as weak-instrument-limited.

### Double-ML Doubly-Robust Mediation

**Goal:** Avoid model misspecification of both mediator and outcome models via cross-fitted ML nuisance estimators.

**Approach:** `causalweight::medDML` uses random forests (or other learners) with sample splitting to estimate nuisance parameters; final estimator is doubly robust.

```r
library(causalweight)

result_dml <- medDML(
  y=dat$outcome, d=dat$treatment, m=dat$mediator,
  x=as.matrix(dat[, covariates]),
  trim=0.05, order=1
)
```

Reports direct, indirect (via mediator), and total effects with influence-function-based standard errors. Robust to non-linearity and interactions; assumes sequential ignorability still.

### Mediational E-Value for Sensitivity

**Goal:** Report the minimum strength of an unmeasured M-Y confounder required to nullify the observed indirect effect.

**Approach:** Convert ACME and its CI to a risk-ratio scale, then apply VanderWeele E-value formula.

```r
library(EValue)

acme_rr <- exp(med_result$d0)
acme_lower_rr <- exp(med_result$d0.ci[1])
evalues.RR(acme_rr, lo=acme_lower_rr, hi=NULL)
```

For binary outcomes, convert ACME on probability scale to RR; for continuous, use `evalues.OLS()` with the standardized indirect effect. E-value > 2 indicates a confounder would need >2-fold associations with both M and Y to nullify the indirect effect (Smith & VanderWeele 2019).

## Tool Install Notes

| Package | Source | Notes |
|---------|--------|-------|
| mediation | CRAN | `install.packages('mediation')`; actively maintained (Imai group) |
| CMAverse | GitHub | `remotes::install_github('BS1125/CMAverse')`; NOT on CRAN; 6 estimators in one interface |
| HIMA | GitHub | `remotes::install_github('YinanZheng/HIMA')`; archived from CRAN 2026-07 (needs archived `scalreg`); v2.x renamed `hima()` to HIMA2 -- verify with `?hima` |
| bama | CRAN | `install.packages('bama')`; Bayesian; slow MCMC |
| causalweight | CRAN | `install.packages('causalweight')`; medDML for double-ML mediation |
| EValue | CRAN | `install.packages('EValue')`; for mediational E-values |
| TwoSampleMR | r-universe | See causal-genomics/mendelian-randomization for setup |
| MVMR | r-universe | `remotes::install_github('WSpiller/MVMR')`; for MVMR-mediation |
| gfoRmula | CRAN | For longitudinal / time-varying confounders |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `Error in storage.mode(x) <- "double"` inside `hima()` | NA in `data.pheno` columns referenced by formula, or unconverted factors | `na.omit(data.pheno)` first; ensure all RHS vars in formula are numeric or factor |
| ACME significant, ADE significant, total NOT significant | Suppression / inconsistent mediation | Report transparently; effect partitioning can exceed total in suppression |
| `medsens()` errors on glm outcome | `medsens` requires linear OR probit (not logit) outcome | Refit outcome as `glm(..., family=binomial(link='probit'))` |
| `mediate()` runs forever with binary outcome | `sims=5000` with bootstrap and small n | Use `sims=1000` exploratory; verify model converges first; consider parallel via `parallel='multicore'` |
| CMAverse `cmest()` reports NaN for `pm` | Total effect crosses zero -> proportion ill-defined | Report ACME and TE separately; pm is unstable when |TE| is small |
| Different ACME between `mediation` and CMAverse `rb` | Default `astar/a` levels differ; binary mediator handled differently | Set `astar=0, a=1` explicitly; for binary mediator pass `mval=list(0)` |
| HIMA returns zero significant mediators | Screening too aggressive; or no true mediators | Try `topN=2*sqrt(n)` instead of default; verify with permutation null |
| Two-step MR shows indirect > total | Steiger reversal: M actually causes E; or pleiotropic SNPs | Run MR-Steiger filter; use MR-PRESSO for pleiotropy |
| `medDML` trim removes most data | Severe positivity violation -- few units with overlapping treatment/mediator distributions | Tighten covariate set; check propensity score distributions |

## References

- Baron RM, Kenny DA 1986 J Pers Soc Psychol 51:1173 (original product-of-coefficients)
- Imai K, Keele L, Tingley D 2010 Psychol Methods 15:309 (counterfactual mediation, sequential ignorability)
- VanderWeele TJ 2014 Epidemiology 25:749 (4-way decomposition)
- VanderWeele TJ 2015 Explanation in Causal Inference (OUP) -- canonical textbook
- Valeri L, VanderWeele TJ 2013 Psychol Methods 18:137 (binary outcomes; rare-disease 4-way)
- Vansteelandt S, Daniel RM 2017 Epidemiology 28:258 (interventional / randomized indirect effects)
- Shi B et al 2021 Epidemiology 32:e20 (CMAverse package; 6 estimators)
- Zhang H et al 2016 Bioinformatics 32:3150 (HIMA original)
- Perera C et al 2022 BMC Bioinformatics 23:296 (HIMA2 alpha-beta screening)
- Song Y et al 2020 Biometrics 76:700 (BAMA Bayesian high-D mediation)
- Burgess S et al 2015 IJE 44:484 (network / two-step MR)
- Sanderson E et al 2019 IJE 48:713 (MVMR conditional F-statistic)
- Carter AR & Sanderson E 2021 Eur J Epidemiol 36:465 (MVMR-mediation)
- Farbmacher H et al 2022 Econometrics J 25:277 (medDML / double-ML mediation)
- Smith LH, VanderWeele TJ 2019 Epidemiology 30:835 (mediational E-value)

## Related Skills

- causal-genomics/mendelian-randomization - IV-based causal inference; foundation for MR-mediation
- causal-genomics/pleiotropy-detection - MR-mediation instrument validity hinges on pleiotropy diagnostics (MR-Egger intercept, MR-PRESSO)
- causal-genomics/colocalization-analysis - Confirm shared causal variant before causal mediation
- causal-genomics/fine-mapping - Identify the causal variant driving the exposure
- methylation-analysis/differential-cpg-testing - Per-CpG inputs for HIMA EWAS mediation
- differential-expression/deseq2-basics - Expression inputs for eQTL mediation
- multi-omics-integration/mofa-integration - Multi-layer mediator construction
- population-genetics/association-testing - GWAS summary statistics for MR-mediation
- clinical-biostatistics/effect-measures - Risk-ratio / odds-ratio scales for binary outcomes
- machine-learning/model-validation - Cross-fitting and sample splitting for medDML
<!-- END FILE: causal-genomics/mediation-analysis/SKILL.md -->

## 子目录：causal-genomics/mendelian-randomization

<!-- BEGIN FILE: causal-genomics/mendelian-randomization/SKILL.md -->
---
name: bio-causal-genomics-mendelian-randomization
description: Estimate causal effects of an exposure on an outcome from GWAS summary statistics using genetic instruments. Implements IVW (fixed/random), MR-Egger, weighted median/mode, MR-RAPS, CAUSE, GSMR-HEIDI, MR-PRESSO, MVMR, MR-Clust, LCV, and LHC-MR via TwoSampleMR, MendelianRandomization, MR-PRESSO, cause, and lhcMR. Use when testing causal direction between traits, evaluating drug-target effects via cis-pQTL/cis-eQTL, performing multivariable mediation MR, distinguishing causation from correlated horizontal pleiotropy, or producing STROBE-MR-compliant sensitivity batteries.
tool_type: mixed
primary_tool: TwoSampleMR
---

## Version Compatibility

Reference examples tested with: TwoSampleMR 0.6.0+, MendelianRandomization 0.10+, MR-PRESSO 1.0+, cause 1.2+, MVMR 0.4+, ieugwasr 1.0+, MRlap 0.0.3.2+, coloc 5.2+, mrclust 0.1+, lhcMR 0.0.1+, R 4.4+. Both TwoSampleMR 0.6.0 and ieugwasr 1.0 are the JWT-transition versions; older versions still expect deprecated OAuth.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI (plink, GCTA-GSMR): `<tool> --version` then `<tool> --help`

If code throws an error referencing a function that has moved (e.g. `ieugwasr::ld_clump` vs `TwoSampleMR::clump_data`) or an OAuth token failure, introspect the installed API and adapt the example rather than retrying.

# Mendelian Randomization

**"Test whether trait X causally affects trait Y from GWAS summary statistics"** -> Use genetic variants as instrumental variables (IVs) that satisfy three assumptions (relevance, independence, exclusion restriction) to estimate `beta_causal = beta_outcome / beta_exposure` under the IV framework (Davey Smith & Ebrahim 2003 IJE 32:1; Burgess & Thompson 2021 Chapman & Hall/CRC, 2nd ed.). Tool choice is a decision about the **regime** (one-sample vs two-sample, sparse vs polygenic, drug-target vs polygenic exposure) and the **pleiotropy model** (balanced, directional InSIDE, correlated horizontal). Wrong tool inflates Type-I error or attenuates true effects in a direction predictable from the bias structure.

- R: `TwoSampleMR::mr()` orchestrates IVW + Egger + weighted median + weighted mode in one call
- R: `MendelianRandomization::mr_ivw / mr_egger / mr_median / mr_mbe / mr_conmix` per-method API (S4 objects; MR-RAPS is NOT in this package -- use `TwoSampleMR::mr_raps()` which wraps the GitHub `mr.raps`)
- R: `MRPRESSO::mr_presso()` global / outlier / distortion tests
- R: `cause::cause()` correlated horizontal pleiotropy mixture
- R: `MVMR::strength_mvmr() + MVMR::ivw_mvmr()` multivariable conditional-F + IVW

## Statistical Model Taxonomy

| Method | Pleiotropy assumption | Min instruments | Strength | Fails when |
|--------|------------------------|-----------------|----------|------------|
| IVW (fixed) | All IVs valid | 2 | Most efficient under no pleiotropy | Any directional or balanced pleiotropy inflates Type-I |
| IVW (random effects) | Balanced + InSIDE | 3 | Standard primary; absorbs heterogeneity into wider SE | Directional pleiotropy biases the point estimate |
| MR-Egger | Directional pleiotropy + InSIDE | 10+ for power | Detects + corrects directional pleiotropy via intercept (Bowden 2015 IJE 44:512) | NOME violated (`I^2_GX < 0.9`); SIMEX correction required; underpowered <10 SNPs |
| Weighted median | Up to 50% invalid IVs | 3 | Robust to a minority of bad instruments (Bowden 2016 Genet Epidemiol 40:304) | >50% invalid IVs |
| Weighted mode | Zero modal pleiotropy (ZEMPA) | 3 | Robust if the modal estimate is unbiased (Hartwig 2017 IJE 46:1985) | Bimodal pleiotropy; small numbers |
| MR-RAPS | Balanced pleiotropy + weak instruments | 10+ | Profile-score robust to weak-IV + balanced horizontal pleiotropy (Zhao 2020 Ann Stat 48:1742) | Strong directional pleiotropy; CRAN-archived 2025-03-01 |
| CAUSE | Correlated horizontal pleiotropy (CHP) | 100+ sig SNPs | Explicit shared-factor mixture; protects against CHP-driven false positives (Morrison 2020 Nat Genet 52:740) | Sparse polygenic exposures; <100 sig SNPs |
| GSMR + HEIDI-outlier | Outlier removal under InSIDE | 10+ | Alternative outlier detection; integrates with LD reference (Zhu 2018 Nat Commun 9:224) | Requires individual-level LD; HEIDI conservative |
| MR-PRESSO | Outlier-driven horizontal pleiotropy | 4+ | Global / outlier / distortion three-step (Verbanck 2018 Nat Genet 50:693) | Blind to CHP; computationally heavy at large NbDistribution |
| MVMR (IVW) | Conditional independence after measured pleiotropy | 1+ per exposure | Accounts for measured horizontal pleiotropy via multivariable regression (Sanderson 2019 IJE 48:713) | Conditional F < 10 on any exposure |
| MR-Clust | Heterogeneous causal effects (multiple mechanisms) | 30+ | Clusters SNPs by their causal-effect estimate (Foley 2021 Bioinformatics 37:531) | Single causal mechanism; small instrument sets |
| Contamination mixture | Mixture of valid + invalid IVs | 10+ | Profile-likelihood mixture (Burgess 2020 Nat Commun 11:376) | Sparse signal |
| LCV | Genome-wide; distinguishes causation vs genetic correlation | All SNPs | Tests `gcp` parameter using LDSC-style block jackknife (O'Connor & Price 2018 Nat Genet 50:1728) | Two-trait covariance dominated by a third confounder |
| LHC-MR | Bidirectional + heritable confounder | All SNPs | Joint likelihood over genome-wide markers; estimates both directions + confounder (Darrous 2021 Nat Commun 12:7274) | Computationally heavy; rare-variant trait |
| MRlap | Sample overlap + winner's curse + weak-IV jointly | Genome-wide sumstats | LDSC-scaffolded joint correction (Mounier & Kutalik 2023 Genet Epidemiol 47:314) | LDSC intercept poorly estimated (h^2 < 0.05); non-EUR without matched LD scores |
| Doubly-Ranked MR (DRMR) | Non-linear, non-parametric | 5+ strata | Non-parametric stratification (Tian 2023 PLoS Genet 19:e1010823); replaces residual stratification when linearity fails | Continuous exposures only; needs individual-level data; Hamilton 2023 medRxiv 23293658 shows stratum-specific bias from age/sex |

Methodology evolves; benchmark consensus shifts every 2-3 years. Verify against the current Slob & Burgess 2020 *Genet Epidemiol*, Burgess 2023 *Wellcome Open Res* "Guidelines for performing Mendelian randomization" (v3+), and STROBE-MR 2021 reporting standards before locking a method as primary.

## Decision Tree by Experimental Scenario

| Scenario | Primary method | Sensitivity battery | Why |
|----------|----------------|----------------------|-----|
| Standard two-sample, independent cohorts, polygenic exposure | IVW (random) | Egger + weighted median + MR-PRESSO + MR-RAPS + Steiger | Default; covers balanced, directional, outlier, weak-IV regimes |
| One-sample (e.g. UK Biobank both ends) | IVW with weak-IV-aware (MR-RAPS) | Egger + LCV + jackknife SE | One-sample F-stat floor shifts to F >= 20; jackknife SE preferred over analytic at one-sample scale; do NOT run exposure GWAS and outcome GWAS on the same individuals then claim two-sample (Barry 2021 PLoS Genet 17:e1009703 collider bias); within-stratum MR (e.g. "MR among smokers") risks collider bias from the stratification variable |
| Partial sample overlap (UKB exposure + UKB outcome) | MR-RAPS with overlap correction | Sample-overlap-adjusted IVW (Burgess 2016 Genet Epidemiol 40:597) | Bias is intermediate, proportional to z-score correlation |
| Drug-target / cis-MR (cis-pQTL, cis-eQTL) | IVW restricted to cis window | Colocalization PP.H4 + LD-prune within window | Exclusion restriction relaxed because the protein/transcript directly mediates effect (Schmidt 2020 Nat Commun 11:3255) |
| MVMR for measured pleiotropy (e.g. LDL adjusted for HDL/TG) | `MVMR::ivw_mvmr` | Conditional F + Q_A heterogeneity | Required when exposures correlate via shared SNPs |
| Mediation MR (X -> M -> Y) | MVMR difference of total vs direct | Two-step MR + product-of-coefficients (Carter 2021 Eur J Epidemiol 36:465) | Network MR; quantifies indirect effect |
| Polygenic exposure with potential CHP (e.g. BMI -> CHD) | CAUSE (primary) + IVW (secondary) | Egger + MR-PRESSO + LCV | CAUSE explicitly models CHP via shared-factor; needs >=100 sig SNPs |
| Binary outcome (e.g. T2D) on linear scale | IVW on log-OR with log-additive coding | All sensitivity on log-OR; report exp(beta) | Linearity of MR estimating equation holds on log-OR not OR |
| Time-to-event (Cox) outcome | IVW on log-HR | Non-collapsibility-aware log-HR reporting | Non-collapsibility caveats apply |
| Non-linear MR (e.g. alcohol J-curve) | DRMR (Tian 2023) + residual stratification side-by-side | Negative-control outcomes (genotype-vs-sex within strata); Hamilton 2023 limitation cited | Both methods produce stratum-specific bias from age/sex effects (Hamilton 2023 medRxiv 23293658); pre-specify the non-linear hypothesis, do not data-snoop the J-curve, report negative-control sanity checks |
| Single-patient rare disease | Not MR -- use FRASER/DROP outlier framework | See alternative-splicing/outlier-splicing-detection | MR requires summary stats; n=1 is wrong regime |

## One-Sample vs Two-Sample Bias Direction

| Design | Weak-IV bias direction | Reason |
|--------|------------------------|--------|
| One-sample, F<10 | Toward confounded observational estimate (overestimates causal effect if confounding is in same direction) | Sample correlation between IV-X and IV-Y residuals |
| Two-sample non-overlapping, F<10 | Toward null | Independent samples decouple residuals (Burgess 2011 IJE 40:755) |
| Two-sample with partial overlap | Intermediate; proportional to overlap fraction and z-score correlation | Burgess 2016 Genet Epidemiol 40:597; correction available |

**Operational rule:** Whenever both GWAS came from UK Biobank (or any single biobank), treat the analysis as one-sample-equivalent and prefer MR-RAPS as primary. Treating it as "two-sample because separate GWAS files" is a common error and produces overestimates.

### MRlap: unified correction for sample overlap + winner's curse + weak instruments

MRlap (Mounier & Kutalik 2023 Genet Epidemiol 47:314) jointly corrects three biases that previously required three separate tools: sample overlap, winner's curse, and weak-instrument bias. It builds on an LDSC scaffold (cross-trait LD-score regression intercept estimates the overlap-induced covariance) and reweights the IVW estimate against the analytical bias-correction formula.

```r
remotes::install_github('n-mounier/MRlap')   # never on CRAN; bioconductor unsuitable
library(MRlap)

fit <- MRlap(
    exposure = gwas_X_df, exposure_name = 'BMI',
    outcome = gwas_Y_df, outcome_name = 'T2D',
    ld = 'eur_w_ld_chr/', hm3 = 'w_hm3.snplist',   # LDSC reference files
    MR_threshold = 5e-8, MR_pruning_dist = 500, MR_pruning_LD = 0.05
)
fit$MRcorrection$corrected_effect       # overlap + winner's curse + weak-IV corrected
fit$MRcorrection$corrected_effect_se
fit$LDSC$h2_exp                          # exposure heritability sanity check
fit$LDSC$int_crosstrait                  # cross-trait LDSC intercept; ~0 means no sample overlap
```

**Decision rule -- prefer MRlap when:** (a) any sample overlap is suspected, (b) only sumstats are available (no individual-level data for re-running GWAS on disjoint samples), (c) exposure discovery and outcome were both run inside the same biobank (UKB-on-UKB, FinnGen-on-FinnGen). MRlap returns NA / unstable estimates when h^2 < 0.05; in that regime, fall back to Burgess 2016 overlap-corrected IVW plus MR-RAPS for the weak-IV component.

## Drug-Target / cis-MR Framework

cis-MR restricts instruments to the cis-regulatory window of the gene encoding the protein/transcript exposure (Schmidt 2020 Nat Commun 11:3255), relaxing the exclusion-restriction assumption because the protein product directly mediates the SNP's effect on the outcome. Operational core: extract cis-pQTL/cis-eQTL within +/-500 kb of the gene; clump at r2 < 0.1 (looser than polygenic MR to retain power within a narrow window); require colocalization PP.H4 >= 0.7; flag protein-altering variants (PAV) which can break SomaScan/Olink aptamer/antibody binding rather than reflect biology.

Full drug-target cis-MR workflow including UKB-PPP / deCODE / Fenland pQTL panels, PAV flagging, Olink vs SomaScan replication (~15-30% cross-platform disagreement), and the operational claim ladder lives in causal-genomics/proteome-mr-drug-target. Use that skill for any drug-target nomination.

### Binary outcomes and non-collapsibility

MR with logistic-GWAS sumstats returns per-allele log-OR on the **population-averaged** (marginal) scale, NOT the conditional log-OR (Burgess 2017 Stat Methods Med Res 26:2333). For rare disease (prevalence < 10%), OR ~= RR ~= HR and the distinction is harmless. For common disease, OR diverges from RR/HR and the MR estimate cannot be back-converted to a conditional effect without strong assumptions; report as "per 1-SD increase in genetically-predicted X, OR for Y = ..." rather than implying an individual-level intervention effect.

Collider bias when conditioning on a collider variable (Coscia 2022 Eur J Epidemiol 37:671 formalizes this for stratified MR): case-only or disease-progression designs condition the sample on disease status, opening a collider path between any cause of disease and any cause of progression. MR within affected subsets without explicit adjustment for selection probability is fragile; weight by inverse probability of selection or restrict claims to the unconditioned population.

## Per-Method Failure Modes

### IVW under directional pleiotropy

**Trigger:** Several SNPs affect the outcome through pathways not via the exposure, in a consistent direction.

**Mechanism:** IVW is a weighted regression through origin; non-zero mean pleiotropy shifts the slope.

**Symptom:** Egger intercept p < 0.05 with non-zero estimate; IVW differs from weighted median; MR-PRESSO global test p < 0.05.

**Fix:** Use Egger (if `I^2_GX >= 0.9` -- otherwise SIMEX-correct via the `simex` package applied to the Egger fit, treating `se.exposure` as measurement error in `beta.exposure`); cross-check with weighted median, MR-PRESSO, and CAUSE; report IVW only as one of a panel, never alone. The `MendelianRandomization::mr_egger()` function accepts `distribution='normal'` and reports the `I.sq` (I^2_GX) NOME diagnostic but applies no NOME/SIMEX correction to the estimate itself and does NOT expose a SIMEX wrapper.

### Weak-instrument bias direction

**Trigger:** Mean per-instrument F-statistic < 10, or several individual F < 10.

**Mechanism:** Weak IVs amplify finite-sample correlation between IV-X and IV-Y errors; bias direction depends on overlap regime (see table above).

**Symptom:** Estimates shift markedly when removing the weakest instruments; one-sample MR estimates much larger than two-sample.

**Fix:** Compute F per instrument from the EXPOSURE GWAS, not the outcome; exclude F < 10; use MR-RAPS (handles weak IVs by design); for two-sample, also report unweighted IVW (less weak-IV-bias-inflated than weighted in some regimes).

### Winner's curse at P~5e-8

**Trigger:** Discovery GWAS is the source of both instrument selection and effect-size estimates.

**Mechanism:** SNPs that just cross 5e-8 in discovery have over-estimated effect sizes (regression toward the mean in independent replication); MR uses inflated `beta_X`, biasing causal estimate.

**Symptom:** MR effect shrinks substantially when using effect sizes from an independent replication GWAS.

**Fix:** (1) Three-sample design (discovery / replication-for-instrument-effect / outcome) where feasible. (2) When sumstats-only: MRlap (Mounier 2023), MR-SimSS (sample-splitting from sumstats), or RIVW (Ma 2023 Ann Statist 51:211 -- rerandomized IVW) jointly correct winner's curse + weak IVs + overlap. (3) Jiang 2023 IJE 52:1209 empirical magnitude: variant-level inflation ~50-400% near the genome-wide-significance threshold, dropping to <25% when the minimum P <= 1e-13.

### NOME violation invalidating Egger

**Trigger:** Running MR-Egger with `I^2_GX < 0.9`.

**Mechanism:** Egger assumes NO Measurement Error in exposure effect sizes (NOME); when violated, Egger slope is attenuated toward null with reciprocal bias on the intercept.

**Symptom:** `mr_pleiotropy_test()` Egger estimate disagrees with weighted median in magnitude but agrees in direction; `Isq()` function returns <0.9.

**Fix:** Compute `Isq(beta_X, se_X)` (Bowden 2016 IJE 45:1961); if <0.9, apply SIMEX correction via `simex` package or report Egger as exploratory only. The MendelianRandomization package's `mr_egger()` reports the `I.sq` (I^2_GX) NOME diagnostic but does not itself apply a NOME/SIMEX correction; SIMEX must be run separately.

### Steiger filter false flag under unmeasured confounding

**Trigger:** Applying `steiger_filtering()` on traits with unmeasured shared confounders (e.g. SES).

**Mechanism:** Steiger compares variance explained in exposure vs outcome per SNP; an unmeasured confounder upstream of both produces SNPs that explain more variance in the outcome than the exposure, falsely flagging "reverse causation" (Lutz 2022 Genet Epidemiol 46:139).

**Symptom:** Many SNPs flagged as wrong-direction yet biology and prior MR support forward causation.

**Fix:** Treat Steiger as a heuristic, not gospel; cross-validate direction with bidirectional MR (forward + reverse with independent instrument sets); for known-confounder-rich domains (psychiatric traits, SES proxies) use LCV or LHC-MR instead, which jointly model confounders.

### Palindromic SNP harmonization

**Trigger:** SNPs with alleles A/T or C/G near MAF 0.5.

**Mechanism:** Strand orientation is ambiguous for palindromic SNPs when allele frequencies are intermediate; flipping introduces sign errors that look like pleiotropy.

**Symptom:** `harmonise_data()` reports many palindromic SNPs dropped; remaining SNPs show heterogeneity from a handful.

**Fix:** Default `action = 2` (infer from allele frequencies) drops MAF~0.5 palindromes; `action = 3` drops ALL palindromes (most conservative); never use `action = 1` (assumes forward strand) unless both GWAS are guaranteed to use the same strand convention. Document choice in methods.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| F-statistic > 10 per instrument | Staiger & Stock 1997 (linear IV) | Heuristic; debated (Burgess 2011 IJE; Zhao 2020 argues 10 is too low for one-sample) |
| Conditional F > 10 per exposure (MVMR) | Sanderson 2019 IJE 48:713 | Total F can be high while conditional F low; per-exposure F is what matters |
| `I^2_GX >= 0.9` for Egger | Bowden 2016 IJE 45:1961 | NOME assumption; below this, SIMEX correction required |
| CAUSE >= 100 significant SNPs | Morrison 2020 Nat Genet 52:740 | Mixture model needs signal density for shared-factor estimation |
| Egger >= 10 instruments | Bowden 2015 IJE 44:512 | Power for slope test in weighted regression |
| Sample-overlap z-score correlation | Burgess 2016 Genet Epidemiol 40:597 | Use LDSC bivariate intercept as proxy; correct IVW SE accordingly |
| Clumping r2 < 0.001, 10 Mb window | TwoSampleMR default; matches GWAS LD norms | Polygenic MR; cis-MR uses r2 < 0.1 within window |
| Steiger p < 0.05 | Hemani 2017 PLoS Genet 13:e1007081 | Heuristic; subject to confounder caveat (Lutz 2022) |
| MR-PRESSO NbDistribution | 1000 exploratory; >= 5000 publication; >= 10000 stringent | Verbanck 2018 Nat Genet 50:693; precision of global p-value scales with NbDistribution |
| STROBE-MR all 20 items | Skrivankova 2021 JAMA 326:1614; BMJ 375:n2233 | Required since 2022 by most epidemiology journals |
| Bonferroni for pheWAS-MR | Standard | Many outcomes; FDR if exploratory |

## TwoSampleMR Standard Workflow

**Goal:** Produce a defensible primary IVW estimate plus a full sensitivity battery from two-sample summary statistics.

**Approach:** Extract genome-wide significant instruments -> clump (local plink preferred) -> extract outcome -> harmonise -> mr -> pleiotropy + heterogeneity + leave-one-out -> Steiger -> MR-PRESSO -> report.

```r
library(TwoSampleMR)
library(ieugwasr)

exposure_raw <- read_exposure_data(
    filename = 'exposure_gwas.tsv', sep = '\t',
    snp_col = 'SNP', beta_col = 'BETA', se_col = 'SE',
    effect_allele_col = 'A1', other_allele_col = 'A2',
    eaf_col = 'EAF', pval_col = 'P'
)

exposure_sig <- subset(exposure_raw, pval.exposure < 5e-08)  # genome-wide significance

# F-statistic computed from EXPOSURE (Burgess 2011); ratio of squared effect to its variance
exposure_sig$f_stat <- (exposure_sig$beta.exposure / exposure_sig$se.exposure)^2
exposure_sig <- subset(exposure_sig, f_stat >= 10)  # Staiger-Stock 1997 weak-IV heuristic

clumped <- ld_clump(
    data.frame(rsid = exposure_sig$SNP, pval = exposure_sig$pval.exposure),
    clump_r2 = 0.001, clump_kb = 10000,  # polygenic MR convention
    plink_bin = genetics.binaRies::get_plink_binary(),
    bfile = '1kg_EUR/EUR'
)
exposure_dat <- subset(exposure_sig, SNP %in% clumped$rsid)

outcome_dat <- read_outcome_data(
    filename = 'outcome_gwas.tsv', snps = exposure_dat$SNP, sep = '\t',
    snp_col = 'SNP', beta_col = 'BETA', se_col = 'SE',
    effect_allele_col = 'A1', other_allele_col = 'A2',
    eaf_col = 'EAF', pval_col = 'P'
)

dat <- harmonise_data(exposure_dat, outcome_dat, action = 2)  # infer from EAF; drops MAF~0.5 palindromes

primary <- mr(dat, method_list = c('mr_ivw', 'mr_egger_regression',
                                    'mr_weighted_median', 'mr_weighted_mode'))

heterogeneity <- mr_heterogeneity(dat)         # Cochran Q
pleiotropy <- mr_pleiotropy_test(dat)          # Egger intercept
loo <- mr_leaveoneout(dat)                     # influential-SNP check
steiger <- directionality_test(dat)            # variance-explained direction
```

## MR-PRESSO Outlier Detection

**Goal:** Detect horizontal-pleiotropy outliers, remove them, and test whether the corrected estimate differs from the uncorrected one (distortion test).

**Approach:** Three-step framework: global test (presence of pleiotropy), outlier test (per-SNP), distortion test (effect change after outlier removal).

```r
library(MRPRESSO)

presso <- mr_presso(
    BetaOutcome = 'beta.outcome', BetaExposure = 'beta.exposure',
    SdOutcome = 'se.outcome', SdExposure = 'se.exposure',
    OUTLIERtest = TRUE, DISTORTIONtest = TRUE,
    data = dat, NbDistribution = 10000,  # >= 10000 for publication-grade p-value precision
    SignifThreshold = 0.05
)

print(presso$`MR-PRESSO results`$`Global Test`)         # any pleiotropy
print(presso$`MR-PRESSO results`$`Distortion Test`)     # change after outlier removal
outlier_snps <- which(presso$`MR-PRESSO results`$`Outlier Test`$Pvalue < 0.05 / nrow(dat))
```

## CAUSE for Correlated Horizontal Pleiotropy

CAUSE (Morrison 2020 Nat Genet 52:740) fits a shared-factor mixture to genome-wide sumstats and compares causal vs sharing-only models by delta-ELPD. Workflow: `gwas_merge()` -> sample ~1M variants for `est_cause_params()` -> filter sig SNPs (P < 1e-3) and optionally LD-prune -> `cause(X, variants, param_ests)`. Needs >= 100 sig SNPs. Full annotated example and ELPD interpretation in causal-genomics/pleiotropy-detection.

## MVMR with Conditional F

**Goal:** Estimate the causal effect of exposure X1 on Y, adjusting for measured pleiotropy via X2.

**Approach:** Format exposures + outcome into MVMR object; compute conditional F per exposure (>10 required); run multivariable IVW; report Q_A heterogeneity.

```r
library(MVMR)

mvmr_dat <- format_mvmr(
    BXGs = cbind(dat$beta.x1, dat$beta.x2),
    BYG = dat$beta.y,
    seBXGs = cbind(dat$se.x1, dat$se.x2),
    seBYG = dat$se.y,
    RSID = dat$SNP
)

condF <- strength_mvmr(r_input = mvmr_dat, gencov = 0)  # per-exposure conditional F
# condF must be > 10 for EACH exposure (Sanderson 2019); total F is misleading

mv_ivw <- ivw_mvmr(r_input = mvmr_dat)
mv_qa <- pleiotropy_mvmr(r_input = mvmr_dat, gencov = 0)  # Q_A heterogeneity test
```

`gencov = 0` is valid ONLY if the exposure GWAS samples don't overlap; for overlapping exposures use the bivariate LDSC intercept matrix as `gencov`. If any conditional F < 10, the IVW point estimate is weak-IV-biased; switch to the Q-minimization estimator: `qhet_mvmr(r_input, pcor, CI = TRUE, iterations = 1000)` (Sanderson 2021 Stat Med 40:5434), which minimizes Q-statistic heterogeneity rather than weighting by inverse variance and is robust to weak conditional instruments.

## Bidirectional and Steiger

```r
exposure_rev <- format_data(outcome_raw, type = 'exposure')  # treat former outcome as exposure
outcome_rev <- format_data(exposure_raw, type = 'outcome')
dat_rev <- harmonise_data(exposure_rev, outcome_rev, action = 2)
results_rev <- mr(dat_rev, method_list = 'mr_ivw')

dat_filt <- steiger_filtering(dat)  # per-SNP; flags SNPs where variance(Y) > variance(X)
dir_test <- directionality_test(dat) # global; correct_causal_direction == TRUE if forward
```

**Report direction operationally:** forward p < 5e-8 with reverse p > 0.05; `directionality_test()` `correct_causal_direction == TRUE` with Steiger p < 0.05; point estimate in reverse direction has |effect| substantially smaller than forward (reflecting reverse-instrument-strength asymmetry). Example sentence: "Forward MR showed BMI -> T2D (IVW beta = 0.85, p = 2e-15); reverse MR was null (IVW beta = 0.02, p = 0.61); Steiger directionality test favored the forward direction (p = 3e-7)."

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| IVW sig, Egger null with non-zero intercept | Directional pleiotropy | Report Egger as primary if `I^2_GX >= 0.9`; otherwise SIMEX-correct |
| IVW sig, weighted median sig, mode null | Mode underpowered or bimodal pleiotropy | Trust the agreement of IVW + median |
| MR-PRESSO distortion test sig | Outliers materially shift estimate | Report PRESSO-adjusted estimate as primary |
| CAUSE sig, IVW sig, same direction | High-confidence causal claim | Report both; emphasize CAUSE rules out CHP |
| CAUSE null, IVW sig, same direction | CHP indistinguishable from causation | Downgrade to "consistent with causation but not separable from CHP" |
| Forward MR sig, reverse MR also sig | Bidirectional causation OR confounded | Use LHC-MR or LCV for genome-wide resolution |
| IVW sig but `mean F << 10` in one-sample design | Weak-IV bias toward observational | Re-run with MR-RAPS; report adjusted estimate |

**Operational rule for publication:** Primary IVW + concordant Egger (or weighted median if NOME violated) + non-significant MR-PRESSO global test + Steiger correct direction = publication-ready evidence. CAUSE concordance is required when the exposure is polygenic and the prior on CHP is high (e.g. BMI -> outcome, lipids -> outcome). Single-method "significant IVW" claims should be downgraded to exploratory.

## Cohort Gotchas

- UKB GWAS commonly include non-EUR participants; pan-UKB EUR/AFR/EAS/SAS subsets are separate releases. Mixing ancestries inflates instrument strength via population stratification rather than biology.
- FinnGen DF12 (2024) cohort: Finnish founder effects produce narrower LD blocks and higher winner's curse magnitude than UKB at matched sample size.
- MVP / GBMI / AoU: multi-ancestry meta-analyses; stratify by ancestry before MR or use ancestry-specific subsets.
- UKB-on-UKB MR creates one-sample-equivalent bias regardless of "different GWAS file" appearance; use MRlap or move the outcome to an external cohort (FinnGen, BBJ, MVP).

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Sample overlap between exposure and outcome GWAS?" | LDSC bivariate intercept reported; MRlap or sample-overlap-corrected IVW applied; document overlap fraction |
| "Weak instruments (F < 10)?" | F computed from EXPOSURE; per-instrument and mean F reported; MR-RAPS used as sensitivity if mean F borderline |
| "Horizontal pleiotropy?" | IVW + Egger + weighted median + weighted mode + MR-PRESSO; if rg > 0.3 also CAUSE (see pleiotropy-detection) |
| "Reverse causation?" | Steiger filter applied; bidirectional MR ran; LCV gcp reported if rg > 0.3 |
| "Pre-registered?" | OSF protocol filed; STROBE-MR all 20 items reported |
| "InSIDE assumption?" | INstrument Strength Independent of Direct Effect -- pleiotropic effects alpha uncorrelated with instrument-exposure effects gamma. Tested via Egger intercept + CHP-aware sensitivity (CAUSE) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| F-statistic computed from outcome | Reading off `beta.outcome / se.outcome` | Compute from EXPOSURE; outcome F is meaningless for IV strength |
| All instruments dropped at harmonise | All SNPs palindromic; or allele coding mismatch | Verify A1/A2 conventions match; try `action = 3` to drop, not assume |
| `Unauthorized` / `403` from OpenGWAS | OAuth deprecated May 2024; JWT token required | Generate at api.opengwas.io -> set `OPENGWAS_JWT=<token>` in `~/.Renviron` -> restart R -> verify with `ieugwasr::get_opengwas_jwt()`. For production, skip the API: use `ld_clump_local()` with local 1KG bfile (saves rate-limit + auth headaches). |
| Conditional F vs total F confusion in MVMR | Reporting `mean(F)` not `strength_mvmr()` per-exposure | Always use `MVMR::strength_mvmr()` and report each column |
| `install.packages("mr.raps")` fails | CRAN-archived 2025-03-01 | `remotes::install_github('qingyuanzhao/mr.raps')`; TwoSampleMR's `mr_raps()` wrapper internally calls this package |
| MR-PRESSO returns NA p-value | `NbDistribution` too small; signal too thin | Increase to >= 10000; check that >= 4 SNPs remain after harmonization |
| Egger intercept "highly significant" with 5 SNPs | Underpowered Egger over-fits the slope | Egger needs >= 10 SNPs; below that, intercept is unreliable |
| Sample-overlap correction ignored | Treating UKB-on-UKB as two-sample | Apply Burgess 2016 correction; or use MR-RAPS |
| `cause()` runs forever | Default model fit on too many SNPs | Filter to sig SNPs (P < 1e-3) before `cause()`; `est_cause_params` uses the random subset |
| MAF column missing -> harmonise action=2 silently downgrades | EAF unavailable | Provide EAF or use `action = 3` and document the loss |

## Tool Installation Notes

```r
# CRAN-stable
install.packages(c('remotes', 'MendelianRandomization', 'MVMR', 'coloc'))

# GitHub-only or recently archived
remotes::install_github('MRCIEU/TwoSampleMR')          # primary orchestrator
remotes::install_github('MRCIEU/ieugwasr')             # OpenGWAS client + local clumping
remotes::install_github('rondolab/MR-PRESSO')          # never on CRAN
remotes::install_github('qingyuanzhao/mr.raps')        # CRAN-archived 2025-03-01
remotes::install_github('jean997/cause')               # depends on mixsqp; suggests Rfast
remotes::install_github('cnfoley/mrclust')             # heterogeneity clusters
remotes::install_github('LizaDarrous/lhcMR')           # bidirectional + heritable confounder
remotes::install_github('HDTian/DRMR')                 # doubly-ranked stratification
remotes::install_github('n-mounier/MRlap')             # joint overlap + winner's-curse + weak-IV correction
```

`TwoSampleMR::mr_raps()` is a thin wrapper that calls `mr.raps::mr.raps()` under the hood; the GitHub `mr.raps` install above is therefore required. The `MendelianRandomization` package does NOT export `mr_raps()` (verify with `ls('package:MendelianRandomization')`); only TwoSampleMR offers a MR-RAPS entry point. For local clumping, install plink2 and download a 1KG EUR (or matched-ancestry) reference bfile.

## STROBE-MR Reporting

STROBE-MR (Skrivankova 2021 JAMA 326:1614; BMJ 375:n2233): 20-item checklist required by Eur J Epi / Nat Genet / JAMA / Diabetologia since 2022. See causal-genomics/pleiotropy-detection for the per-item table -- that skill is the consolidated reporting reference for the full MR + sensitivity battery.

## References

- Davey Smith G & Ebrahim S 2003 IJE 32:1 (foundational framework)
- Burgess S & Thompson SG, Mendelian Randomization: Methods for Causal Inference Using Genetic Variants, Chapman & Hall/CRC (1st ed. 2015 / 2nd ed. 2021) (MR canonical reference)
- Bowden J et al 2015 IJE 44:512 (MR-Egger)
- Bowden J et al 2016 Genet Epidemiol 40:304 (weighted median)
- Hartwig FP et al 2017 IJE 46:1985 (weighted mode)
- Zhao Q et al 2020 Ann Stat 48:1742 (MR-RAPS)
- Morrison J et al 2020 Nat Genet 52:740 (CAUSE)
- Zhu Z et al 2018 Nat Commun 9:224 (GSMR + HEIDI)
- Verbanck M et al 2018 Nat Genet 50:693 (MR-PRESSO)
- Sanderson E et al 2019 IJE 48:713 (MVMR conditional F)
- Foley CN et al 2021 Bioinformatics 37:531 (MR-Clust)
- Burgess S et al 2020 Nat Commun 11:376 (contamination mixture)
- O'Connor LJ & Price AL 2018 Nat Genet 50:1728 (LCV)
- Darrous L et al 2021 Nat Commun 12:7274 (LHC-MR)
- Tian H et al 2023 PLoS Genet 19:e1010823 (DRMR)
- Burgess S et al 2016 Genet Epidemiol 40:597 (sample-overlap correction)
- Schmidt AF et al 2020 Nat Commun 11:3255 (drug-target / cis-MR framework)
- Lutz SM et al 2022 Genet Epidemiol 46:139 (Steiger filter caveat)
- Skrivankova VW et al 2021 JAMA 326:1614 (STROBE-MR statement)
- Mounier N & Kutalik Z 2023 Genet Epidemiol 47:314 (MRlap joint correction)
- Sanderson E et al 2021 Stat Med 40:5434 (qhet_mvmr Q-minimization estimator)
- Coscia C et al 2022 Eur J Epidemiol 37:671 (collider bias in case-only / progression cohorts)
- Hamilton FW et al 2023 medRxiv 23293658 (NLMR stratum-specific bias critique)
- Jiang T et al 2023 IJE 52:1209 (winner's curse empirical magnitude)
- Ma X et al 2023 Ann Statist 51:211 (RIVW rerandomized IVW)

## Related Skills

- causal-genomics/colocalization-analysis - Confirm shared causal variant for cis-MR drug-target work
- causal-genomics/pleiotropy-detection - Deep dive on MR-PRESSO, Egger, contamination mixture diagnostics
- causal-genomics/fine-mapping - Credible-set construction at instrument loci before cis-MR
- causal-genomics/mediation-analysis - Two-step MR and MVMR difference method for X -> M -> Y mediation
- causal-genomics/transcriptome-wide-association - TWAS as MR-adjacent framework for gene-level inference
- causal-genomics/proteome-mr-drug-target - Dedicated cis-pQTL drug-target MR workflow with UKB-PPP/deCODE/Fenland and coloc triangulation
- population-genetics/association-testing - GWAS source for instrument selection
- clinical-databases/clinvar-lookup - Annotate instrument SNPs for downstream interpretation
<!-- END FILE: causal-genomics/mendelian-randomization/SKILL.md -->

## 子目录：causal-genomics/pleiotropy-detection

<!-- BEGIN FILE: causal-genomics/pleiotropy-detection/SKILL.md -->
---
name: bio-causal-genomics-pleiotropy-detection
description: Detect and adjust for horizontal pleiotropy in two-sample Mendelian randomization by distinguishing uncorrelated (UHP) from correlated (CHP) pleiotropy and choosing among Egger, MR-PRESSO, MR-RAPS, CAUSE, LHC-MR, LCV, MR-Clust, MR-Mix, and contamination-mixture methods. Use when validating an MR causal claim, running the STROBE-MR sensitivity battery, suspecting a shared heritable confounder, working under weak-instrument or polygenic-exposure regimes, or reconciling discordant estimates across robust methods.
tool_type: r
primary_tool: TwoSampleMR
---

## Version Compatibility

Reference examples tested with: TwoSampleMR 0.5.11+, MendelianRandomization 0.9.0+, MR-PRESSO 1.0+, CAUSE 1.2.0+, MR-Clust 0.1.0+, MRMix 0.1+, mr.raps 0.4.1+ (GitHub), LHC-MR 0.0.0.9000+ (GitHub), LCV (script-based, no version tag), simex 1.8+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- For GitHub-only packages, check the repo HEAD vs the local install date

If code throws errors, introspect the installed package and adapt the example rather than retrying.

# Pleiotropy Detection in Mendelian Randomization

**"Validate my MR result against pleiotropic bias"** -> Decompose violations of the exclusion-restriction assumption into uncorrelated horizontal pleiotropy (UHP, addressable by Egger / median / mode / MR-PRESSO) and correlated horizontal pleiotropy (CHP, addressable only by CAUSE / LHC-MR / LCV), then run a method battery whose assumptions span both regimes.

- R: `TwoSampleMR::mr()` (IVW + Egger + median + mode), `mr_pleiotropy_test()`, `mr_heterogeneity()`, `mr_leaveoneout()`, `directionality_test()`
- R: `MRPRESSO::mr_presso()` for UHP outlier removal + distortion test
- R: `cause::cause()` for CHP-aware estimation; `mrclust::mr_clust_em()` for mechanism-heterogeneous instruments
- R: `MendelianRandomization::mr_conmix()` for contamination mixture; `MRMix::MRMix()` for mixture-of-distributions

## UHP vs CHP: The Central Postdoc-Grade Distinction

Horizontal pleiotropy comes in two regimes, and most "standard" MR sensitivity methods address only one of them.

| Regime | Definition | InSIDE assumption | Methods that handle it |
|--------|------------|--------------------|------------------------|
| UHP (uncorrelated horizontal pleiotropy) | Pleiotropic effect alpha_j independent of instrument-exposure effect gamma_j | Holds | IVW (balanced UHP only), MR-Egger, weighted median, weighted mode, MR-PRESSO, MR-RAPS, MR-Mix, contamination mixture |
| CHP (correlated horizontal pleiotropy) | alpha_j correlates with gamma_j through a shared upstream factor (heritable confounder, network mediator) | Violated | CAUSE, LHC-MR, LCV, MR-Clust (partial), Steiger-filtered MR (partial) |

**InSIDE = INstrument Strength Independent of Direct Effect** (Bowden 2015 IJE 44:512). Plain English: across SNPs, the per-SNP pleiotropic effect alpha and per-SNP instrument-exposure effect gamma are treated as independent random variables. CHP is the case where they covary because both flow from a shared upstream genetic factor.

**The trap (Morrison 2020 Nat Genet 52:740):** IVW, MR-Egger, MR-PRESSO, and GSMR are all blind to CHP. Under a shared heritable confounder they each return a plausible-looking corrected causal estimate that is systematically biased in the direction of the confounder. The MR-PRESSO global test does not flag CHP because correlated pleiotropy is not an outlier pattern, it is a population mean shift in the alpha distribution conditional on gamma.

**Operational rule:** If genetic correlation rg(exposure, outcome) is high (LDSC `>= 0.3`) or biology strongly suggests a shared upstream factor, the IVW / Egger / PRESSO triple is insufficient. Add CAUSE (preferred when sig SNPs `>= 100`) or LHC-MR (preferred for polygenic genome-wide IVs).

## Operational Decision Flow (4 Steps)

1. **Compute genetic correlation (LDSC).** Run `ldsc.py --rg <exposure.sumstats.gz>,<outcome.sumstats.gz>` (see causal-genomics/genetic-correlation). If `|rg| > 0.3`, CHP is plausible -> flag for Step 3 escalation. If the LDSC rg standard error spans zero broadly, treat low-rg evidence as weak rather than confirming absence of CHP.
2. **Standard battery.** IVW (random-effects when Cochran Q p < 0.05) + MR-Egger (with NOME I^2_GX check) + weighted median + weighted mode + MR-PRESSO (NbDistribution `>= 10000` for stringent reporting). Report all five with point estimate, SE, p, 95% CI, and n_SNPs_used. Compute Egger I^2_GX; apply SIMEX if I^2_GX < 0.9 (see examples/simex_egger_correction.R).
3. **CHP escalation.** Trigger when rg > 0.3 OR PRESSO global p < 0.05 with > 50% nominal outliers OR Egger / median / mode disagree by > 2 SE. Run CAUSE (if `>= 100` significant SNPs after pruning) or LHC-MR (any N; uses genome-wide sumstats). Report ELPD delta + z + q (CHP fraction) + gamma (CHP-adjusted causal estimate).
4. **Triangulate.** Pre-MR Steiger filter; bidirectional MR (examples/bidirectional_mr.R); LCV gcp; LDSC rg report. Consensus across methods supports a publication-ready claim. Disagreement requires narrowing the scope (e.g., subgroup, cis-MR, time-varying analysis) rather than reporting a single point estimate.

## Algorithmic Taxonomy

| Method | Models | UHP-robust | CHP-robust | Min #SNPs | Fails when | Citation |
|--------|--------|-----------|-----------|-----------|------------|----------|
| Inverse-variance weighted (IVW) | Weighted regression through origin | Balanced UHP only | No | 3 | Directional UHP; CHP; weak IV bias; heterogeneity | Burgess 2013 Genet Epidemiol 37:658 |
| MR-Egger intercept + slope | IVW + free intercept | Directional UHP | No | >=10 for power | NOME violated (I^2_GX < 0.9); <10 SNPs; CHP | Bowden 2015 IJE 44:512 |
| Weighted median | Median of Wald ratios | Up to 50% invalid | No | >=10 | >50% invalid; CHP | Bowden 2016 Genet Epidemiol 40:304 |
| Weighted mode (MBE) | Mode of estimate density | Plurality valid | Partial | >=10 | Multimodal estimates from CHP clusters | Hartwig 2017 IJE 46:1985 |
| Cochran Q | Heterogeneity across Wald ratios | Total heterogeneity flag, not direction-specific | No | 3 | Cannot distinguish UHP from heterogeneity from CHP | Del Greco M F 2015 Stat Med 34:2926 |
| MR-PRESSO | Detect + remove UHP outliers via RSS-out | Yes (assumes majority valid) | No | >=4 | >50% pleiotropic; any CHP; small n | Verbanck 2018 Nat Genet 50:693 |
| GSMR + HEIDI-outlier | Outlier removal via single-instrument estimate heterogeneity | Yes | No | >=10 | CHP (HEIDI-outlier is heterogeneity-driven) | Zhu 2018 Nat Commun 9:224 |
| MR-RAPS | Profile likelihood with overdispersion + Huber/Tukey loss | Yes; weak-IV robust | Partial via overdispersion | >=10 | Strong CHP | Zhao 2020 Ann Stat 48:1742 |
| MR-Mix | Mixture-of-distributions over valid + invalid | Yes | Partial | >=20 | Few SNPs; very heterogeneous CHP | Qi & Chatterjee 2019 Nat Commun 10:1941 |
| Contamination mixture | Profile likelihood over contamination fraction | Yes | Partial | >=20 | Few SNPs | Burgess 2020 Nat Commun 11:376 |
| MR-Clust | k-means over Wald estimates with NULL cluster | Yes | Diagnostic for CHP via clusters | >=20 | Single-mechanism exposure (no clustering signal) | Foley 2021 Bioinformatics 37:531 |
| CAUSE | Bayesian mixture: shared causal + shared-factor (CHP) components | Yes | Yes (explicit) | >=100 sig SNPs at p<5e-8 | <100 sig SNPs; non-overlapping GWAS samples | Morrison 2020 Nat Genet 52:740 |
| LHC-MR | Latent heritable confounder + bidirectional + heritability | Yes | Yes | Genome-wide GWAS sumstats | Heritability mis-estimated; severe sample overlap | Darrous 2021 Nat Commun 12:7274 |
| LCV (latent causal variable) | gcp parameter on genome-wide rg | N/A (not an MR method) | Diagnostic | Genome-wide GWAS sumstats | Heritability low; non-Gaussian effect distribution | O'Connor & Price 2018 Nat Genet 50:1728 |

Methodology evolves; verify against the Burgess & Thompson textbook (2nd ed 2021), Hemani 2018 (basic four-method battery), and Sanderson 2022 Nat Rev Methods Primers 2:6 before locking a sensitivity battery.

## Decision Tree by Scenario

| Scenario | Primary estimator | Sensitivity / triangulation |
|----------|-------------------|----------------------------|
| Many strong IVs, no biological shared trait suspected | IVW + Egger + weighted median + weighted mode + PRESSO | Cochran Q; leave-one-out; F-stat; Steiger filtering |
| LDSC rg(exposure, outcome) `>= 0.3` or strong shared-factor biology | CAUSE (if sig SNPs `>= 100`) OR LHC-MR | LCV gcp; cross-check IVW after Steiger filter |
| Many weak IVs (mean F < 20) | MR-RAPS with overdispersion + robust Huber loss | MR-Mix or contamination mixture; report F-stat range |
| Suspected heterogeneous causal mechanisms (e.g. LDL on CHD via multiple lipoprotein pathways) | MR-Clust; report per-cluster IVW | Pathway annotation of cluster instruments; Bayesian mixture |
| Cis-MR drug target (single locus, few SNPs in LD) | Colocalization (causal-genomics/colocalization-analysis) + Steiger | PWCoCo; conditional analysis; not Egger (low SNP count) |
| Polygenic exposure (heritability spread genome-wide; few significant loci) | LHC-MR (uses all SNPs) | LDSC rg; genome-wide IVW with weak-IV-aware methods (RAPS) |
| Reverse causation suspected | Bidirectional MR with Steiger filter; LHC-MR (jointly estimates both directions) | directionality_test; effect-size r2 comparison |
| Population-level summary discordant with biology | Re-examine instrument selection; check Winner's curse; LD pruning settings | Triangulate with cis-MR; family-based MR if available |

## Per-Method Failure Modes

### MR-Egger NOME violation

**Trigger:** I^2_GX = (Q_GX - df) / Q_GX is below 0.9, indicating measurement-error attenuation of the Egger slope (NOME = "no measurement error" in the exposure GWAS effect sizes).

**Mechanism:** MR-Egger regresses outcome effects on exposure effects with a free intercept. Imprecise exposure effects (high beta.exposure SE relative to beta.exposure variability across instruments) introduce regression dilution that pulls the Egger slope toward the null and inflates the intercept.

**Symptom:** Egger slope much closer to zero than IVW, weighted median, and weighted mode estimates; large Egger SE.

**Fix:** Apply SIMEX correction (Bowden 2016 IJE 45:1961; Cook & Stefanski 1994 JASA 89:1314 SIMEX framework) using the `simex` package on the Egger regression, treating beta.exposure SE as measurement error. See examples/simex_egger_correction.R. Alternative: use MR-RAPS, which models the exposure-effect error explicitly via profile likelihood and does not suffer the NOME failure.

### MR-PRESSO majority-outlier breakdown

**Trigger:** More than 50% of instruments are pleiotropic (UHP), e.g. when instrument set was loosely selected (genome-wide significant but unfiltered).

**Mechanism:** MR-PRESSO's global RSS-out statistic and outlier detection both assume a majority-valid set; outliers are defined relative to that majority. With a pleiotropic majority, PRESSO removes the valid minority.

**Symptom:** PRESSO-corrected estimate is similar in magnitude (and sign) to the uncorrected estimate even after dropping nominally "outlier" SNPs; distortion-test p-value paradoxically non-significant; few or no outliers detected despite obvious global-test significance.

**Fix:** Do not trust PRESSO corrected estimate. Re-examine instrument selection (drop loose p-thresholds, prune LD harder); switch to CAUSE or LHC-MR; consider weighted-mode estimator which is plurality-valid rather than majority-valid.

### MR-PRESSO false negative under CHP

**Trigger:** Strong shared heritable confounder (high rg) producing CHP. Confirmed by significant LDSC rg or LCV gcp.

**Mechanism:** Correlated pleiotropy is a population-level mean shift in alpha conditional on gamma; it is not an outlier pattern. PRESSO's RSS-out distance is invariant under such a mean shift, so the global test is not powered against CHP.

**Symptom:** PRESSO global p > 0.05 (no detected pleiotropy) while a CHP-aware method (CAUSE, LHC-MR) returns a substantially different (often null) causal estimate.

**Fix:** When CHP is plausible, ALWAYS run CAUSE or LHC-MR in addition to PRESSO; do not rely on PRESSO global non-significance as evidence of no pleiotropy.

### MR-Egger underpowered with few SNPs

**Trigger:** Fewer than 10 instruments.

**Mechanism:** Egger's intercept variance is driven by the spread of beta.exposure across instruments; with few SNPs the intercept CI is so wide that even strongly pleiotropic data give non-significant intercepts.

**Symptom:** Non-significant Egger intercept p-value alongside obviously discordant IVW and weighted-median estimates.

**Fix:** Report intercept point estimate and CI rather than a binary "pleiotropy present / absent" verdict; do not use Egger as the only sensitivity method when SNP count is low; weight evidence toward weighted-median, weighted-mode, and CAUSE / LHC-MR.

### Steiger filter inverted by exposure measurement error (Hemani 2017)

**Trigger:** Exposure is imprecisely measured (lower heritability ascertained in the exposure GWAS) and outcome is well-measured.

**Mechanism:** Steiger compares r^2_GX vs r^2_GY per SNP. Measurement error in the exposure underestimates r^2_GX; well-measured outcome captures r^2_GY accurately. Per-SNP, the inequality can flip even when the true causal direction is exposure -> outcome.

**Symptom:** A large fraction of instruments fail Steiger (`steiger_dir == FALSE`) in a direction that conflicts with biological plausibility.

**Fix:** Interpret Steiger as one signal among many, not a hard gate; cross-check with bidirectional MR; verify exposure GWAS heritability and sample size; switch to LHC-MR which models both directions jointly and accounts for heritability.

### CAUSE underpowered with few significant SNPs

**Trigger:** Fewer than 100 genome-wide-significant instruments (p < 5e-8) after harmonization and LD pruning.

**Mechanism:** CAUSE fits a Bayesian mixture model over a shared-factor (CHP) component, a shared-causal component, and a null component. Posterior identification of the mixture weights requires substantial signal across many SNPs.

**Symptom:** CAUSE delta_ELPD CI crosses zero; Pareto-k diagnostic flags unstable points; posterior intervals on q (CHP fraction) span [0, 1].

**Fix:** Use LCV gcp for genome-wide directional inference (does not require many significant SNPs); use LHC-MR if heritability and sumstats are available; or report CAUSE alongside an explicit caveat about its underpowered regime.

### LCV gcp under non-Gaussian effect distributions

**Trigger:** Highly polygenic trait with substantial sparsity in true effects (mixture of large-effect and zero-effect loci).

**Mechanism:** LCV assumes a bivariate normal model for effect sizes after LDSC adjustment. Sparse architectures (e.g. immune traits with HLA dominance) violate this and bias gcp estimates.

**Symptom:** LCV gcp point estimate appears extreme but heritability LDSC z-scores are modest; partitioned heritability shows extreme HLA enrichment.

**Fix:** Exclude HLA region from LDSC inputs; complement with CAUSE / LHC-MR; report gcp with awareness of the polygenicity caveat.

## Quantitative Thresholds

| Metric | Threshold | Source / rationale |
|--------|-----------|--------------------|
| F-statistic per SNP | `>=10` strong; `<10` weak | Burgess 2011 IJE 40:755 (rule of thumb); weak-IV bias toward observational confounded estimate |
| I^2_GX (NOME) | `>=0.9` Egger reliable | Bowden 2016 IJE 45:1961 |
| I^2_GX (NOME) intermediate | 0.6-0.9 SIMEX-corrected Egger | Bowden 2016 IJE |
| I^2_GX (NOME) severe | `<0.6` drop Egger; use MR-RAPS or CAUSE | Bowden 2016 IJE; SIMEX unreliable below 0.6 |
| Egger min SNP count for adequate power | `>=10` | Bowden 2015 IJE 44:512 |
| Cochran Q significance | p < 0.05 indicates heterogeneity | Del Greco M F 2015 Stat Med 34:2926 |
| MR-PRESSO NbDistribution | 1000 exploratory; `>=5000` publication; `>=10000` stringent | Verbanck 2018 Nat Genet 50:693 (Methods) |
| MR-PRESSO global test p | < 0.05 -> heterogeneity / outliers present | Verbanck 2018 Nat Genet |
| MR-PRESSO distortion test p | < 0.05 -> outliers materially shifted estimate; if `>= 0.05` report uncorrected IVW | Verbanck 2018 Nat Genet |
| MR-PRESSO min instruments | `>=4` to run; `>=10` for non-degenerate global test | Verbanck 2018 Nat Genet |
| MR-PRESSO SignifThreshold | 0.05 default | Verbanck 2018 Nat Genet |
| MR-PRESSO majority-valid breakdown | Fails when `>50%` instruments pleiotropic | Verbanck 2018 Nat Genet (theoretical limit) |
| Weighted median validity | Robust to `<=50%` invalid IVs | Bowden 2016 Genet Epidemiol 40:304 |
| Weighted mode validity | Plurality-valid (largest valid subset is most common estimate) | Hartwig 2017 IJE 46:1985 |
| CAUSE min #SNPs | `>=100` p < 5e-8 SNPs after pruning | Morrison 2020 Nat Genet 52:740 (Supplement) |
| CAUSE delta_ELPD criterion | one-sided p < 0.05; z = delta_elpd / se(delta_elpd); z > 1.96 standard; z > 3.0 stringent | Morrison 2020 Nat Genet |
| LDSC rg suggesting CHP | `>= 0.3` flags need for CAUSE / LHC-MR | Operational rule; see causal-genomics/genetic-correlation |
| Steiger r^2 difference | Reverse-causal flag at any per-SNP r2_GY > r2_GX | Hemani 2017 PLoS Genet 13:e1007081 |
| Standard sensitivity battery | IVW + Egger + median + mode + PRESSO + Steiger + LOO | Hemani 2018 eLife 7:e34408 / STROBE-MR 2021 |

LCV gcp interpretation thresholds (0, 0.5, 0.6, 1) are tabulated in usage-guide.md.

## Standard Sensitivity Battery (Working Reference)

**Goal:** Run the canonical UHP-focused MR sensitivity suite on harmonized two-sample data.

**Approach:** Compute IVW + Egger + median + mode side-by-side; test Egger intercept and heterogeneity; run MR-PRESSO with `>=5000` distributions for publication or `>=10000` for stringent reporting; apply Steiger filter; leave-one-out; report all estimates.

```r
library(TwoSampleMR)
library(MRPRESSO)

methods <- c('mr_ivw', 'mr_egger_regression', 'mr_weighted_median', 'mr_weighted_mode')
res_mr <- mr(dat, method_list = methods)

het <- mr_heterogeneity(dat)
pleio <- mr_pleiotropy_test(dat)
loo <- mr_leaveoneout(dat)
steiger <- directionality_test(dat)

isq <- Isq(dat$beta.exposure, dat$se.exposure)
nome_pass <- isq >= 0.9

presso <- mr_presso(
    BetaOutcome='beta.outcome', BetaExposure='beta.exposure',
    SdOutcome='se.outcome', SdExposure='se.exposure',
    OUTLIERtest=TRUE, DISTORTIONtest=TRUE,
    data=dat, NbDistribution=10000, SignifThreshold=0.05)

global_p <- presso$`MR-PRESSO results`$`Global Test`$Pvalue
outlier_p <- presso$`MR-PRESSO results`$`Outlier Test`$Pvalue
distortion_p <- presso$`MR-PRESSO results`$`Distortion Test`$Pvalue
n_outliers <- sum(outlier_p < 0.05, na.rm=TRUE)
```

Full working pipeline incl SIMEX, MR-RAPS, contamination mixture, and STROBE-MR table: examples/sensitivity_battery.R.

## CAUSE for CHP-Aware Estimation

**Goal:** Distinguish causal from shared-factor (correlated horizontal pleiotropy) explanations of an exposure-outcome association.

**Approach:** Fit nuisance parameters (LD pruning + rho_GWAS sample-overlap correction) on a random SNP set; fit the sharing and causal posterior; compare ELPD (expected log predictive density) via Pareto-k smoothed importance sampling.

```r
library(cause)
params <- est_cause_params(dat_cause, variants = pruned_subset_snps)
res_cause <- cause(X = dat_cause, variants = pruned_snps, param_ests = params)
elpd <- summary(res_cause)$tab
```

Full posterior extraction + reporting: examples/cause_analysis.R.

**Interpreting CAUSE output:**

- `q`: posterior CHP fraction; 0 = no CHP, 1 = all instruments operate via the shared factor
- `eta`: shared-factor effect on Y (the "confounder pathway" magnitude)
- `gamma`: posterior causal effect of E on Y after partialling out CHP; report median + 95% credible interval
- `delta_ELPD` (sharing - causal): negative -> causal model preferred; z = delta_elpd / se(delta_elpd); z > 1.96 standard, z > 3.0 stringent; one-sided p reported alongside posterior gamma
- Pareto-k > 0.7 indicates unstable posterior on those points; if more than 10% of points are unstable, treat the posterior as unreliable; remediation: add more SNPs (loosen p-threshold one notch then re-prune in LD) or re-fit excluding flagged outliers

CAUSE requires sumstats from both exposure and outcome GWAS in matched effect-allele coding. The pruning step typically retains 100-5000 signature SNPs at LD r^2 < 0.01 in a 1 Mb window; nuisance estimation should use a larger random SNP subset (`>= 100,000` genome-wide SNPs) to fit rho (sample overlap) stably.

## MR-RAPS Loss Function and Overdispersion

**Trigger:** Weak instruments (mean F < 20) and/or suspected UHP requiring outlier-resistant estimation.

- `over.dispersion = TRUE` always for MR (horizontal-pleiotropy variance is real, not noise; turning this off underestimates SE)
- `loss.function = 'huber'` (default; outlier-resistant; suited to mild to moderate UHP)
- `loss.function = 'tukey'` (more aggressive; downweights extreme outliers more; choose when many obvious outliers suspected)
- `loss.function = 'l2'` (non-robust; equivalent to weighted least squares; do not use when UHP suspected)

Tukey is preferable when leave-one-out reveals 2+ SNPs single-handedly shifting the IVW estimate by > 1 SE.

## MR-Clust for Mechanism Heterogeneity

**Goal:** When a single causal estimate is misleading because instruments operate through multiple causal mechanisms (e.g. LDL on CHD via multiple lipoprotein subfractions), identify clusters of instruments with similar per-SNP Wald ratios.

```r
library(mrclust)
ratio_hat <- dat$beta.outcome / dat$beta.exposure
ratio_se <- abs(dat$se.outcome / dat$beta.exposure)
res_mc <- mr_clust_em(theta=ratio_hat, theta_se=ratio_se,
                     bx=dat$beta.exposure, by=dat$beta.outcome,
                     bxse=dat$se.exposure, byse=dat$se.outcome,
                     obs_names=dat$SNP)
per_cluster <- res_mc$results$best
```

Clusters with cluster_class = 'null' are pleiotropy-only instruments. Per-cluster IVW estimates may differ substantially; biological annotation of the SNPs in each cluster (pathway, target gene) is the interpretation step.

## LHC-MR Workflow

**Goal:** Jointly estimate forward causal effect, reverse causal effect, and the heritable-confounder contribution from genome-wide sumstats (not just significant SNPs).

```r
library(lhcMR)
merged <- merge_sumstats(list(df_x, df_y), c('X', 'Y'), LD.filepath='ldsc/LDscores.txt', rho.filepath='ldsc/LDrho.txt')
sp_list <- calculate_SP(merged, trait.names=c('X', 'Y'), run_ldsc=TRUE, run_MR=TRUE, hm3='ldsc/w_hm3.snplist', ld='ldsc/eur_w_ld_chr/', nStep=2, SP_single=3, SP_pair=50)
res_lhc <- lhc_mr(sp_list, trait.names=c('X', 'Y'), paral_method='lapply', nBlock=200, nCores=4)
```

LHC-MR is computationally heavy (hours on full sumstats) but among the most rigorous CHP-aware estimators when both GWAS are well-powered. Output includes axx, ayy, hxy (confounder effect on each trait), and bidirectional alpha_xy, alpha_yx.

**Choosing CAUSE vs LHC-MR (Darrous 2021):**

| Condition | Preferred method |
|-----------|------------------|
| `>= 100` genome-wide significant SNPs after pruning | CAUSE (Bayesian; CHP-explicit; mature posterior diagnostics) |
| Polygenic exposure with few significant loci | LHC-MR (uses genome-wide signal, not just significant SNPs) |
| Severe sample overlap between exposure and outcome GWAS | LHC-MR (jointly models overlap); CAUSE's rho correction is exposed to misspecification at high overlap |
| Bidirectionality of central interest | LHC-MR (jointly estimates alpha_xy and alpha_yx); CAUSE only models forward |
| Limited compute / quick turnaround | CAUSE (minutes to hours); LHC-MR may be > 24h on full sumstats |

When both apply, report both with the agreement / disagreement explicit in the discussion.

## Bidirectional MR Procedure

1. **Forward MR:** instrument exposure E, test effect on outcome Y (primary)
2. **Reverse MR:** instrument outcome Y, test effect on exposure E (using outcome-direction instruments)
3. **Steiger pre-filter both directions:** `steiger_filtering(dat)`; drop SNPs where outcome r^2 > exposure r^2 before primary IVW
4. **Compare estimates:** null reverse + significant forward strengthens the forward causal claim; bidirectional significance flags feedback / shared confounder / reciprocal causation
5. **LCV gcp orthogonal check:** genome-wide directional inference independent of the instrument set

Working code: examples/bidirectional_mr.R.

**Interpretation cheat-sheet:**

| Forward p | Reverse p | Reading |
|-----------|-----------|---------|
| significant | non-significant | Forward causal claim strengthened |
| non-significant | significant | Re-examine instrument-exposure assignment; the "outcome" may causally drive the "exposure" |
| significant | significant | Feedback loop, shared confounder, or reciprocal causation; resolve with LHC-MR |
| non-significant | non-significant | No evidence of causation in either direction |

When forward and reverse both clear Steiger and both IVW p < 0.05, run LHC-MR jointly rather than reporting two univariable estimates.

## LCV (Latent Causal Variable)

LCV uses LDSC-merged genome-wide sumstats and reports gcp (genetic causality proportion) on [-1, 1]. It is a complement to, not a replacement for, MR; gcp ~ 0 with high LDSC rg implies pure genetic correlation without partial causation.

```r
source('LCV/R/RunLCV.R')
res_lcv <- RunLCV(ldscores$L2, x$Z, y$Z)
# res_lcv$gcp; res_lcv$pval.gcpzero.2tailed
```

Full gcp interpretation table is in usage-guide.md.

## Required Supplementary Tables

**Instrument table** (one row per SNP retained for primary analysis):

| Column | Content |
|--------|---------|
| rsID, chr, pos | Variant identifier and genome position |
| EA, OA, EAF | Effect allele, other allele, effect allele frequency in exposure GWAS |
| beta_E, se_E, p_E, F | Exposure-side estimate, SE, p-value, per-SNP F-statistic |
| beta_Y, se_Y, p_Y | Outcome-side estimate, SE, p-value (harmonized to EA) |
| harmonization_action | 1=kept, 2=flipped, 3=dropped (palindromic ambiguity) |
| palindromic_flag | TRUE / FALSE; tracked per Hartwig 2016 IJE 45:1717 |
| Steiger_direction | forward / reverse / inconclusive |
| Steiger_p | per-SNP directionality p-value |

**Sensitivity-battery table** (one row per method):

| Column | Content |
|--------|---------|
| method | IVW / Egger / WM / WMode / PRESSO (raw + corrected) / RAPS / CAUSE |
| estimate, se, p, 95% CI | Point estimate and inference |
| n_SNPs_used | Post-harmonization, post-Steiger SNP count |
| heterogeneity_p | Q for IVW; Q' for Egger; global p for PRESSO |
| intercept_p | Egger only (directional UHP test) |
| ELPD_delta + z | CAUSE only (sharing - causal; negative + |z| > 1.96 -> causal) |

## Reconciliation Across Methods

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| IVW and Egger agree (small Egger intercept); median and mode agree | Likely true causal; minimal pleiotropy | Report all; STROBE-MR; emphasize agreement |
| IVW significant; Egger non-significant with similar slope; PRESSO global p > 0.05 | Egger underpowered (few SNPs) OR Egger NOME violated | Check I^2_GX; SIMEX-correct if 0.6 < I^2_GX < 0.9 |
| IVW shifted relative to Egger / median / mode; Egger intercept significant | Directional UHP | Trust Egger slope; PRESSO-corrected IVW; mode estimator |
| IVW + Egger + median + mode + PRESSO all agree but CAUSE delta_ELPD non-significant or in opposite direction | CHP via shared confounder | Trust CAUSE; report all five UHP methods alongside but flag the discordance; check LDSC rg |
| All UHP methods agree; LCV gcp ~ 0 | Genetic correlation only, not causation | Causation evidence is weak; report rg explicitly; consider colocalization (cis-MR) instead |
| MR-Clust shows >=2 distinct non-null clusters | Heterogeneous mechanisms | Report per-cluster estimates; do not summarize as a single effect |
| Steiger fails on a substantial fraction of instruments | Reverse causation OR exposure measurement error | Run bidirectional MR; check exposure GWAS heritability; LHC-MR |
| MR-PRESSO global p < 0.05 but corrected estimate similar to uncorrected | >50% pleiotropic OR CHP masquerading as UHP | Re-prune instruments; switch to weighted-mode / CAUSE / LHC-MR |

**Operational rule for publication:** Report IVW (primary), Egger slope + intercept, weighted median, weighted mode, MR-PRESSO global + distortion + corrected, Cochran Q, Steiger directionality, F-statistic distribution, I^2_GX (for Egger validity), and at least one CHP-aware method (CAUSE or LHC-MR) when rg `>= 0.3` or biology suggests shared upstream. Failure to report a CHP-aware result when CHP is plausible is a reviewer-flagged red flag since 2020.

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Was CHP checked for?" | LDSC rg reported (causal-genomics/genetic-correlation); if rg > 0.3, CAUSE or LHC-MR ran; q posterior reported |
| "Why CAUSE and not LHC-MR?" | CAUSE preferred when `>= 100` significant SNPs available (Morrison 2020). LHC-MR preferred when significant-SNP set is small or polygenic, using genome-wide sumstats (Darrous 2021) |
| "Egger NOME?" | I^2_GX computed; if 0.6 <= I^2_GX < 0.9, SIMEX correction applied; if < 0.6, Egger dropped in favor of MR-RAPS |
| "PRESSO doesn't catch CHP?" | Confirmed (Morrison 2020); CAUSE / LHC-MR reported alongside PRESSO for that reason |
| "Steiger filter applied pre-MR or post?" | Pre-MR: SNPs failing per-SNP Steiger directionality dropped before primary IVW |
| "Why no replication cohort?" | Two-sample design uses independent exposure and outcome cohorts; if same biobank, MRlap used or noted as a limitation |
| "Why not just trust the IVW?" | IVW assumes balanced UHP and no CHP; both violated routinely; sensitivity battery is the standard since STROBE-MR 2021 |
| "Effect size is implausibly large" | Re-examine F-statistic distribution for weak IV bias; check Winner's curse; consider Wald ratio at a single strong instrument as sanity check |

## STROBE-MR Reporting (Skrivankova 2021)

| Item | Required content |
|------|-----------------|
| 1-3 | Title / abstract / background indicates this is an MR study; pre-registered protocol |
| 4-7 | Study design, data sources, instrument selection criteria (p-threshold, LD clumping, MAF) |
| 8-11 | Harmonization, palindrome handling, allele alignment |
| 12-14 | F-statistic distribution; weak-instrument bias mitigation |
| 15-17 | Primary MR method + all sensitivity methods + CHP-aware method when relevant |
| 18-19 | Pleiotropy tests, Steiger, heterogeneity |
| 20 | Discussion of remaining assumption violations; limitations |

Sub-items (30 total) detail per-method reporting. The full statement (JAMA 326:1614) and explanation (BMJ 375:n2233) are now reviewer-required at most cardiovascular and psychiatric journals since 2022.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| MR-PRESSO crashes with `Not enough intrumental variables` | Fewer than 4 SNPs | Need >=4 for PRESSO; for cis-MR with few SNPs use colocalization |
| Egger intercept p < 0.05 but I^2_GX = 0.5 | NOME violated; intercept is artifactually inflated | SIMEX-correct or do not trust Egger; use MR-RAPS instead |
| `Isq()` not found | TwoSampleMR version where Isq is unexported | Compute manually: Q_GX = sum((beta_GX/se_GX)^2); I2 = (Q_GX - (n-1))/Q_GX, clipped to [0,1] |
| MR-RAPS `package not found` after CRAN install | CRAN-archived 2025-03-01 | `remotes::install_github('qingyuanzhao/mr.raps')`; call via `TwoSampleMR::mr_raps()` wrapper (MendelianRandomization does NOT export `mr_raps`) |
| CAUSE delta_ELPD CI spans zero; Pareto-k > 0.7 | <100 sig SNPs OR severe sample overlap | Use LHC-MR; or report CAUSE with the explicit caveat |
| Steiger labels most instruments reverse-causal | Exposure GWAS imprecise OR sample size mismatch | Treat as one signal; cross-check with bidirectional MR |
| LHC-MR runtime > 24h | Default nCores=1 on full sumstats | Use nCores >= 4; restrict to LDSC-overlapping SNPs first |
| MR-PRESSO outliers all on same chromosome | Genome-wide LD not properly pruned; clumping window too narrow | Re-clump at r^2 < 0.001 in 10 Mb window |
| MR-Mix returns NA | Few SNPs OR no variation in mixture support | Need >=20 SNPs; default mixture grid may need tuning |

## References

- Bowden J et al 2015 Int J Epidemiol 44:512 (MR-Egger; InSIDE)
- Bowden J et al 2016 Int J Epidemiol 45:1961 (NOME, I^2_GX, SIMEX)
- Cook JR & Stefanski LA 1994 JASA 89:1314 (SIMEX framework)
- Burgess S 2020 Nat Commun 11:376 (contamination mixture)
- Burgess S & Thompson SG 2021 (Mendelian Randomization 2nd ed)
- Darrous L et al 2021 Nat Commun 12:7274 (LHC-MR)
- Foley CN et al 2021 Bioinformatics 37:531 (MR-Clust)
- Hartwig FP et al 2017 Int J Epidemiol 46:1985 (weighted mode)
- Hemani G et al 2017 PLoS Genet 13:e1007081 (Steiger orientation)
- Hemani G et al 2018 eLife 7:e34408 (TwoSampleMR framework)
- Morrison J et al 2020 Nat Genet 52:740 (CAUSE; CHP)
- O'Connor LJ & Price AL 2018 Nat Genet 50:1728 (LCV)
- Sanderson E et al 2022 Nat Rev Methods Primers 2:6 (MR Primer)
- Skrivankova VW et al 2021 JAMA 326:1614 (STROBE-MR statement); BMJ 375:n2233 (explanation)
- Verbanck M et al 2018 Nat Genet 50:693 (MR-PRESSO)
- Zhao Q et al 2020 Ann Stat 48:1742 (MR-RAPS)

## Related Skills

- causal-genomics/mendelian-randomization - Primary causal estimation that this sensitivity battery validates
- causal-genomics/genetic-correlation - LDSC rg required for Step 1 of the decision flow; CHP escalation trigger
- causal-genomics/colocalization-analysis - Required for cis-MR drug-target signals where instruments are too few for Egger
- causal-genomics/fine-mapping - Identify causal variants underlying instrument loci
- causal-genomics/mediation-analysis - Multivariable MR for mediator-adjusted causal estimates
- population-genetics/association-testing - GWAS summary statistics underlying MR instruments
- clinical-biostatistics/effect-measures - Translate MR estimates to clinical effect measures
<!-- END FILE: causal-genomics/pleiotropy-detection/SKILL.md -->

## 子目录：causal-genomics/proteome-mr-drug-target

<!-- BEGIN FILE: causal-genomics/proteome-mr-drug-target/SKILL.md -->
---
name: bio-causal-genomics-proteome-mr-drug-target
description: Runs cis-pQTL Mendelian randomization for drug-target validation using UKB-PPP (Olink), deCODE (SomaScan), Fenland, INTERVAL, ARIC, and FinnGen-PPP proteomes plus colocalization triangulation, phenome-wide on-target adverse-effect scans, cross-platform Olink/SomaScan replication, and PAV (protein-altering variant) sensitivity. Use when nominating or de-risking a drug target from plasma-proteome GWAS, mimicking pharmacological inhibition via cis-pQTL instruments, separating shared-causal from LD-confounded signal under the Schmidt 2020 cis-MR framework, screening on-target adverse phenotypes pheWAS-style, or producing publication-grade STROBE-MR plus PP.H4 evidence for a target gene.
tool_type: mixed
primary_tool: TwoSampleMR
---

## Version Compatibility

Reference examples tested with: TwoSampleMR 0.5.11+, MendelianRandomization 0.10+, MR-PRESSO 1.0+, coloc 5.2.3+, susieR 0.12.35+, ieugwasr 1.0+, plink2 2.00a5+, R 4.4+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `plink2 --version`; VEP `vep --help`

If code throws OAuth or rate-limit errors from OpenGWAS, or a missing `dataset$N` from coloc, introspect the installed API and adapt the example rather than retrying. UKB-PPP, deCODE, and Fenland summary statistics changed file layouts between 2023 and 2025; verify column headers before passing into `format_data()`.

# Proteome-Wide Drug-Target Mendelian Randomization

**"Does genetically lowering plasma protein X cause a change in disease Y, mimicking a drug?"** -> Use cis-pQTLs in the gene window for protein X as instruments under the Schmidt 2020 framework (Nat Commun 11:3255), restrict the exclusion-restriction violation to the geometric neighbourhood of the encoding gene, triangulate with colocalization (3-tier PP.H4 ladder below) and cross-platform replication (Olink vs SomaScan), and flag protein-altering-variant (PAV) confounding. A single significant cis-MR estimate is necessary but not sufficient for a drug-target claim; the operational bar is MR + coloc + cross-platform agreement + PAV-excluded sensitivity.

### PP.H4 Three-Tier Threshold Ladder

| Tier | PP.H4 | Use case |
|------|-------|----------|
| Suggestive | >= 0.7 | Open Targets / exploratory; consistent with shared-causal |
| Standard publication | >= 0.8 | Wallace 2020 PLoS Genet 16:e1008720; most peer-reviewed pubs |
| Industry / clinical | >= 0.95 | Drug-claim grade; pharma internal target-validation standard |

Operational rule: drug-target nomination requires PP.H4 >= 0.8 minimum; industry-grade clinical claim requires PP.H4 >= 0.95 plus the full triangulation panel.

- R (canonical): `TwoSampleMR::mr()` orchestrates the cis-IVW + Egger + median + Wald-ratio panel
- R (correlated cis-pQTLs in a window): `MendelianRandomization::mr_input(..., correlation = ld_matrix)` then `mr_ivw(mr_obj, model='default', correl = TRUE)`
- R (triangulation): `coloc::coloc.abf()` or `coloc::coloc.susie()` on the same cis-window
- pheWAS: `ieugwasr::associations()` against the OpenGWAS catalogue, looped over outcomes
- VEP CLI: annotate every cis-pQTL with `vep --species homo_sapiens --canonical --check_existing` for PAV flagging

## Data Source Taxonomy

| pQTL dataset | Platform | N | Proteins | Reference | Fails when |
|--------------|----------|---|----------|-----------|------------|
| UKB-PPP | Olink Explore 3072 (antibody PEA) | 54,219 | 2923 (54k primary cis-pQTLs across studies; 14,287 primary pQTLs across cis+trans) | Sun 2023 Nature 622:329 | Target not on Olink panel; ancestry mostly EUR; antibody epitope may miss isoforms |
| deCODE | SomaScan v4 (aptamer SOMAmer) | 35,559 | 4907 | Ferkingstad 2021 Nat Genet 53:1712 | Population isolate; LD differs from outbred EUR; aptamers can be PAV-confounded |
| Fenland | SomaScan v4 | 10,708 | 4775 | Pietzner 2021 Science 374:eabj1541 | UK Fenland-specific ascertainment; SomaScan caveats |
| INTERVAL | SomaScan v3 (older) | 3301 | 3622 | Sun 2018 Nature 558:73 | Smaller N; older SomaScan version; useful only as replication |
| ARIC | SomaScan v4 | ~7000 (multi-ancestry sub-cohorts) | 4877 | Zhang 2022 Nat Genet 54:593 | Stratify by ancestry; do not pool |
| FinnGen-PPP | Olink Explore | ~12,000 | ~3000 | FinnGen DF12 (2024 release) | Finnish-specific allele frequencies; not always meta-analyse with UKB |
| AGES-Reykjavik | SomaScan v4 | ~5400 | 4782 | Emilsson 2018 Science 361:769 | Elderly Icelandic cohort; ascertainment bias |
| Olink Explore 1536 disease-specific cohorts (CARDIoGRAMplusC4D, etc) | Olink Explore subset | varies | varies | per-study | Lower N per cohort; use as replication |

Methodology evolves; check the UKB-PPP portal (ukb-ppp.gwas.eu), deCODE Genetics summary-stat releases, and the eQTL Catalogue / GTEx Portal for the current data version. UKB-PPP was substantially re-released in 2024 (extended ancestry meta-analyses); pin a download date in the methods.

### Platform and Cohort Versioning (2024-2026)

- **UKB-PPP Phase 2 (2024)** -- cross-ancestry meta-analyses; ~54k EUR plus multi-ancestry expansion; file layouts differ from Phase 1 (per-protein parquet vs flat TSV); the 14,287 primary pQTL count from Phase 1 shifts in Phase 2 results. Verify the freeze used.
- **FinnGen-PPP** -- Olink Explore platform; DF12 (2024) release is current; Finnish-specific allele frequencies require ancestry-aware downstream analysis.
- **AoU pQTL (2024)** -- All-of-Us proteomics; pre-symptomatic-cohort design strength for reverse-causation control and longitudinal follow-up.
- **SomaScan v4 vs v5** -- v5 expands to ~11k SOMAmers (vs ~5k in v4); binding consistency for shared SOMAmers documented in deCODE / SomaLogic technical notes but not guaranteed; pin platform version.
- **Olink Explore HT** -- ~5,400 proteins (vs ~3,072 in Explore Expansion, ~1,536 in Explore 1536); UKB-PPP Phase 1 used Explore 3072 -- do not assume Explore HT coverage when reading Phase 1 papers.
- Pin specific platform version + release date in the methods section of every cis-MR drug-target manuscript.

## Cis-MR Methodological Taxonomy

| Method | Cis-window assumption | Min cis-pQTLs | Strength | Fails when |
|--------|------------------------|----------------|----------|------------|
| Single cis-pQTL Wald ratio | Single sentinel SNP within +/-500 kb | 1 | Simplest, transparent point estimate `beta_Y/beta_X` and ratio SE | Confounded by LD-linked eQTL/pQTL of neighbour gene; no heterogeneity test |
| Cis-IVW (clumped r2 < 0.1) | Multiple weakly-correlated cis-pQTLs | 2 | Pools information, increases precision (Schmidt 2020) | r2 between pQTLs > 0.1 inflates SE under independence assumption |
| Cis-IVW with correlation `correl=TRUE` | Cis-pQTLs in moderate LD; supply LD matrix | 2 | Correct SE under correlated instruments (Burgess, Zuber, Valdes-Marquez, Sun, Hopewell 2017 Genet Epidemiol 41:714-725) | LD matrix mismatched to summary-stat ancestry |
| Cis-MR-Egger | Directional pleiotropy across cis-pQTLs | 3+ (>=10 for power) | Sensitivity for in-window directional pleiotropy | Underpowered <10 cis-pQTLs; NOME violation `I^2_GX < 0.9` |
| Cis-weighted-median | Up to 50% invalid cis-pQTLs | 3+ | Robust to a minority of bad instruments | >50% invalid cis-pQTLs |
| MR-PRESSO in cis-window | Outlier cis-pQTLs from LD-confounded neighbours | 4+ | Removes neighbour-eQTL-tagged cis-pQTLs; distortion test (Verbanck 2018) | <4 instruments; underpowered global test |
| Conditional cis-MR with weak genetic factors (Patel 2023 Biometrics 79:3458) | Factor-analysis dimension reduction of correlated cis-pQTLs + weak-factor-robust conditional inference | 2+ | Methodologically modern alternative when instruments are highly correlated | Newer; benchmarks evolving; separate implementation from mr_ivw |
| Generalized cis-IVW with correlated SNPs | Joint multivariable cis-window | 2+ | Sound under any LD provided matrix supplied | Numerical instability when r2 ~ 1 (collinear) |
| coloc.susie + Wald-ratio per CS | Multiple independent cis-signals (allelic heterogeneity) | 1+ per credible set | Per-signal MR + per-signal PP.H4 | Requires ancestry-matched LD; spurious CS under mismatch |

Verify against Burgess 2023 *Wellcome Open Res* "Guidelines for performing Mendelian randomization" (v3+) and the Open Targets Genetics drug-target pipeline (Mountjoy 2021) before pinning a primary method for a publication.

## Decision Tree by Scenario

| Scenario | Primary method | Triangulation | Why |
|----------|----------------|----------------|-----|
| Single drug target, single sentinel cis-pQTL, single outcome | Wald ratio | coloc.abf PP.H4 + cross-platform replication + PAV flag | Minimum publishable cis-MR; simplest and most transparent |
| Single drug target, multiple independent cis-pQTLs, single outcome | Cis-IVW correl=TRUE with in-window LD | coloc.susie per credible set + cross-platform | Pools signal; correctly handles within-window LD |
| Drug target with secondary independent cis-signal (allelic heterogeneity) | coloc.susie + per-CS Wald ratio | Compare effect direction across CSs | Each independent signal is its own instrument; report each |
| Phenome-wide MR on a single target | Loop Wald ratio or cis-IVW across hundreds of outcomes | Bonferroni over outcomes; coloc PP.H4 on top hits | On-target adverse-effect discovery (e.g. PCSK9 -> T2D) |
| On-target adverse-effect scan (already-marketed drug) | pheWAS cis-MR vs all FinnGen / OpenGWAS phenotypes | Bonferroni + coloc + clinical-event registry | Re-derives known and novel on-target effects |
| Cross-platform replication required for clinical claim | Run independently on UKB-PPP (Olink) AND deCODE (SomaScan) | Direction agreement + magnitude within 2x | Single platform never sufficient for therapeutic decision |
| Trans-pQTL "wants" to be an instrument | Refuse | -- | Trans = horizontal pleiotropy by definition; use only as confirmatory |
| Target gene not on Olink panel | deCODE / Fenland SomaScan only | Cross-replicate across two SomaScan cohorts | Olink panel is gated; do not infer "untested" as null |
| Target in cis-region with strong neighbour eQTL | coloc.susie + coloc to non-target gene's pQTL/eQTL | Drop cis-pQTLs that coloc with non-target | Mandatory: must rule out neighbour-gene mediation |
| Sample overlap (UKB-PPP exposure + UKB phenotype outcome) | MR-RAPS with one-sample-equivalent correction OR independent outcome (FinnGen, BBJ) | Repeat in non-overlapping cohort | Pretending overlap is two-sample inflates effect estimates |

## Per-Method Failure Modes

### Olink vs SomaScan platform discordance

**Trigger:** A cis-pQTL effect size or even direction differs between UKB-PPP (Olink antibody) and deCODE/Fenland (SomaScan aptamer) for the same protein.

**Mechanism:** Olink uses paired antibody proximity-extension assay (PEA) binding distinct epitopes; SomaScan uses single-aptamer SOMAmer binding a folded epitope. A missense SNP that alters one epitope produces an apparent pQTL on that platform only (a pseudo-PAVQTL / aptamer-affinity QTL, AAVQTL). Splice/isoform differences also produce platform-specific signal. A direct Olink-vs-SomaScan cross-platform comparison reported only modest cross-platform correlation, with roughly half of cis-pQTL signals not shared across platforms (72% of Olink vs 43% of SomaScan assays had a cis-pQTL) (Eldjarn G et al 2023 Nature 622:348).

**Symptom:** Cis-MR significant on one platform, null on the other; or significant on both but opposite direction.

**Fix:** Replicate every cis-MR claim on at least one alternate platform; annotate cis-pQTLs with VEP and flag missense / nonsense / splice variants in the gene; consult Olink and SomaScan documentation for the protein's antibody / aptamer binding region; perform a PAV-excluded sensitivity analysis and report both estimates. If platforms disagree irreconcilably, report the protein as platform-discordant and do NOT advance for clinical claim.

**Olink panel coverage pre-check:** Olink Explore 3072 covers ~3,000 proteins; Explore Expansion ~3,000; Explore HT ~5,400. Always confirm the target is on the panel BEFORE running cis-MR: `grep -i <GENE> olink_panel_proteins.tsv` (panel manifest from olink.com). Sun 2023 Nature supplementary Table S1 lists every UKB-PPP-covered protein explicitly; absence from Table S1 means the target was not measured in Phase 1 (regardless of biology) and the analysis must use SomaScan.

### LD-based pleiotropy in the cis-window

**Trigger:** A cis-pQTL for target gene X is also a strong eQTL or pQTL for a neighbouring gene within +/-500 kb.

**Mechanism:** The instrument's effect on outcome may be mediated by the neighbour gene's protein, not by target X. Cis-window proximity does NOT guarantee specificity.

**Symptom:** Colocalization with the non-target gene's pQTL or eQTL returns PP.H4 >= 0.7; cis-MR using only "clean" cis-pQTLs (those not coloc'd with neighbours) gives a substantially different estimate.

**Fix:** For every cis-pQTL, run colocalization against all eQTL/pQTL signals within +/-500 kb in the relevant tissue; drop cis-pQTLs that coloc (PP.H4 >= 0.5) with any non-target gene; coloc.susie is preferred when multiple credible sets exist in the window. Reports must list which cis-pQTLs were retained and the rationale.

### Reverse causation from disease state on plasma protein

**Trigger:** The outcome trait elevates the protein as a downstream consequence (e.g. CRP elevated in coronary disease patients; TNF in autoimmune disease).

**Mechanism:** Plasma proteomes measured in observational cohorts (including UKB-PPP) include people who have or will develop the outcome; the observed protein-disease association may be downstream not upstream.

**Symptom:** Observational protein-disease association is large; cis-MR estimate is much smaller, null, or in the opposite direction.

**Fix:** Apply Steiger filtering on each cis-pQTL (`steiger_filtering()`); restrict to pre-symptomatic samples where possible (pediatric or early-adult cohorts); replicate in longitudinal cohorts measuring protein years before disease onset. Note: Steiger has its own caveat under unmeasured confounding (Lutz SM et al 2022 Genet Epidemiol 46:139); cross-validate via bidirectional cis-MR.

```r
library(TwoSampleMR)
dat <- harmonise_data(exposure_pQTL, outcome_GWAS)
dat <- steiger_filtering(dat)
dat_forward <- dat[dat$steiger_dir, ]   # drop reverse-direction SNPs
dir_test <- directionality_test(dat_forward)
```

### PAV (protein-altering-variant) confound

**Trigger:** A cis-pQTL is itself a missense, nonsense, frameshift, splice-site, or stop-gain variant in the target gene.

**Mechanism:** The variant changes the protein sequence, which can change antibody affinity (Olink) or SOMAmer affinity (SomaScan) without changing the actual protein abundance in plasma. The pQTL appears strong but reflects measurement artifact.

**Symptom:** The strongest cis-pQTL is a coding variant; cis-MR effect magnitude shrinks substantially when PAVs are excluded; the pQTL is platform-specific.

**Fix:** Annotate ALL cis-pQTLs with Ensembl VEP (`--check_existing --canonical`). Tabulate every cis-pQTL's most-severe consequence. Run two cis-MR analyses: (a) all cis-pQTLs, (b) PAV-excluded. Report both; require concordance for a publishable claim (Sun 2023 supplementary). For aptamer panels, also annotate the SOMAmer binding-region overlap if available.

**PAV-excluded concordance rule:** Concordance between all-cis and PAV-excluded estimates requires (i) effect direction preserved, (ii) |effect| within 2x of the all-cis estimate, AND (iii) p-value still nominally significant (P < 0.05) after PAV exclusion. If ANY of the three criteria fails, report both estimates and downgrade the claim from "drug-target" to "suggestive cis association requiring orthogonal confirmation."

### Trans-pQTL pleiotropy if used as instrument

**Trigger:** Including trans-pQTLs (outside +/-500 kb of the gene) in the instrument set to gain power.

**Mechanism:** A trans-pQTL acts through some other gene's protein that then regulates target X; using it as an instrument violates the exclusion-restriction by definition (horizontal pleiotropy).

**Symptom:** Effect estimate shifts when trans-pQTLs are added; Egger intercept significant.

**Fix:** Restrict instrument set to cis-window only (Schmidt 2020). Trans-pQTLs may be confirmatory ("does the regulator gene also predict outcome?") but never primary instruments for a drug-target claim.

### Sample overlap when both ends are UKB

**Trigger:** Using UKB-PPP for the exposure (Olink protein) AND a UKB phenotype (HES, cancer registry, ICD-10) for the outcome.

**Mechanism:** The same individuals contribute to both summary statistics; weak-instrument bias is now one-sample-equivalent and points TOWARD the confounded observational estimate, not the null.

**Symptom:** UKB-on-UKB cis-MR effect is substantially larger than the same protein-disease pair tested in an independent cohort.

**Fix:** Use an independent outcome cohort whenever possible (FinnGen, Biobank Japan, MVP). If UKB-on-UKB is necessary, apply MR-RAPS with one-sample-equivalent treatment OR the Burgess 2016 (Genet Epidemiol 40:597) sample-overlap correction. Document the overlap fraction. MRlap (Mounier 2023 Genet Epidemiol 47:314) is the recommended modern tool for joint sample-overlap and winner's-curse correction; see causal-genomics/mendelian-randomization for the canonical implementation.

## Triangulation Requirement (Operational Postdoc Rule)

A drug-target causal claim that survives peer review and informs pharmacology requires MULTIPLE concordant streams, not a single significant cis-MR p-value:

1. **Cis-MR estimate** with `P < 0.05 / N_proteins` (Bonferroni proteome-wide ~ 1.7e-5 for 2923 Olink proteins) OR `P < 0.05 / N_outcomes` (Bonferroni pheWAS-wide) -- depending on the testing regime
2. **Colocalization PP.H4 >= 0.8** between cis-pQTL and outcome GWAS at the gene locus -- standard publication tier; >= 0.95 for industry-grade claim (cross-reference causal-genomics/colocalization-analysis)
3. **Cross-platform replication** -- significant on both Olink (UKB-PPP) AND SomaScan (deCODE or Fenland); direction agreement is mandatory, magnitude within 2x is acceptable
4. **Cross-cohort replication** (ideal but not strictly required) -- UKB-PPP -> deCODE -> FinnGen-PPP step-up
5. **PAV-excluded sensitivity** -- the cis-MR survives when missense / nonsense / splice / aptamer-binding-region SNPs are dropped
6. **No neighbour-gene coloc** -- no cis-pQTL in the instrument set coloc-shares a causal variant with any non-target gene's eQTL or pQTL within +/-500 kb
7. **Open Targets L2G concordance** -- Open Targets Platform locus-to-gene score for the target gene >= 0.5 at the disease GWAS lead (cross-reference causal-genomics/effector-gene-prioritization)

Operational claim ladder: cis-MR significant alone = exploratory; +coloc PP.H4 >= 0.7 = consistent with shared-causal; +cross-platform = consistent across detection chemistries; +PAV-excluded + neighbour-clear = publication-grade target nomination; +cohort replication + Open Targets L2G >= 0.5 = clinical-pharmacology-grade. Clinical-pharmacology claims require ALL 6 original criteria PLUS L2G concordance.

## Phenome-Wide Drug-Target MR

**Goal:** For a single drug target (single protein), test causal effect across hundreds of outcomes to discover on-target adverse effects.

**Approach:** Hold cis-pQTL instrument set fixed; loop outcome over OpenGWAS catalogue or FinnGen DF12; multi-test correct over outcomes.

```r
library(TwoSampleMR); library(ieugwasr)

target_pqtl <- read.table('pcsk9_cis_pqtls.tsv', header = TRUE)
exposure_dat <- format_data(target_pqtl, type = 'exposure',
    snp_col = 'SNP', beta_col = 'BETA', se_col = 'SE',
    effect_allele_col = 'A1', other_allele_col = 'A2', eaf_col = 'EAF', pval_col = 'P')

curated_endpoints <- read.table('finngen_DF12_endpoints.tsv', header = TRUE)  # ~3000 curated endpoints from finngen.fi
outcomes <- available_outcomes()
outcomes_filt <- subset(outcomes, id %in% curated_endpoints$id & sample_size >= 50000 & population == 'European')

results <- lapply(outcomes_filt$id, function(out_id) {
    outcome_dat <- extract_outcome_data(snps = exposure_dat$SNP, outcomes = out_id)
    if (nrow(outcome_dat) < 2) return(NULL)
    dat <- harmonise_data(exposure_dat, outcome_dat, action = 2)
    mr(dat, method_list = 'mr_ivw')
})

results_df <- do.call(rbind, Filter(Negate(is.null), results))
n_tests <- nrow(curated_endpoints)
results_df$p_bonf <- pmin(results_df$pval * n_tests, 1)
top_hits <- subset(results_df, pval < 0.05 / n_tests)   # 0.05 / 3000 = 1.7e-5
```

Document the curated endpoint list (FinnGen DF12, Open Targets curated trait map, or a manuscript-specific phecode hierarchy) in methods. The `outcomes_filt$id[1:200]` pattern is a debug shortcut, not a defensible pheWAS protocol. The PCSK9 -> T2D signal (Schmidt 2017 Lancet Diabetes Endocrinol 5:97) was discovered exactly via curated-endpoint pheWAS: cis-MR of LDL-lowering instruments revealed on-target T2D risk before clinical trials confirmed it. Drug-target pheWAS is the canonical use case.

## Cis-MR Standard Workflow

**Goal:** Produce a defensible cis-MR estimate with triangulation, given a target gene and an outcome.

**Approach:** Extract cis-pQTLs in +/-500 kb of the gene -> compute F per instrument from exposure -> clump within window at r2 < 0.1 -> harmonise with outcome -> run TwoSampleMR -> run coloc.abf on the same window -> PAV-annotate via VEP -> report panel.

```r
library(TwoSampleMR); library(coloc); library(ieugwasr)

cis_window_kb <- 500  # +/- 500 kb per Schmidt 2020 standard cis-window
gene_chr <- 1; gene_start <- 55039548; gene_end <- 55064852  # PCSK9 hg38

pqtl <- read.table('ukbppp_pcsk9.tsv', header = TRUE)
pqtl_cis <- subset(pqtl, CHR == gene_chr &
    POS > (gene_start - cis_window_kb * 1000) &
    POS < (gene_end + cis_window_kb * 1000) &
    P < 5e-8)

pqtl_cis$f_stat <- (pqtl_cis$BETA / pqtl_cis$SE)^2  # F from exposure (Burgess 2011)
pqtl_cis <- subset(pqtl_cis, f_stat >= 10)  # Staiger-Stock 1997 weak-IV floor

exposure_dat <- format_data(pqtl_cis, type = 'exposure',
    snp_col = 'SNP', beta_col = 'BETA', se_col = 'SE',
    effect_allele_col = 'A1', other_allele_col = 'A2', eaf_col = 'EAF', pval_col = 'P')

clumped <- ld_clump(
    dplyr::tibble(rsid = exposure_dat$SNP, pval = exposure_dat$pval.exposure),
    clump_r2 = 0.1, clump_kb = cis_window_kb,  # cis-MR clumping per Schmidt 2020
    plink_bin = genetics.binaRies::get_plink_binary(),
    bfile = '1kg_EUR/EUR'
)
exposure_dat <- subset(exposure_dat, SNP %in% clumped$rsid)

outcome_dat <- read_outcome_data('cad_gwas.tsv', snps = exposure_dat$SNP, sep = '\t',
    snp_col = 'SNP', beta_col = 'BETA', se_col = 'SE',
    effect_allele_col = 'A1', other_allele_col = 'A2', eaf_col = 'EAF', pval_col = 'P')

dat <- harmonise_data(exposure_dat, outcome_dat, action = 2)

primary <- mr(dat, method_list = c('mr_wald_ratio', 'mr_ivw',
                                    'mr_egger_regression', 'mr_weighted_median'))

# Triangulation step 1: colocalization on the same window
gwas_window <- read.table('cad_gwas_pcsk9_window.tsv', header = TRUE)
pqtl_window <- read.table('ukbppp_pcsk9_full_window.tsv', header = TRUE)

coloc_res <- coloc.abf(
    dataset1 = list(beta = pqtl_window$BETA, varbeta = pqtl_window$SE^2,
                    snp = pqtl_window$SNP, type = 'quant', N = 54219, sdY = 1),
    dataset2 = list(beta = gwas_window$BETA, varbeta = gwas_window$SE^2,
                    snp = gwas_window$SNP, type = 'cc', N = 122733, s = 0.34),
    p1 = 1e-4, p2 = 1e-4, p12 = 5e-6  # conservative p12 for drug-target
)

cat('PP.H4 =', coloc_res$summary['PP.H4.abf'], '\n')
```

## Cis-IVW with Correlated Instruments

**Goal:** When several cis-pQTLs in the window are correlated (r2 between 0.1 and 0.7), use the generalized IVW that takes the LD matrix as an explicit parameter.

**Approach:** Compute or load the LD matrix in the cis-window from an ancestry-matched plink reference; build the input with `MendelianRandomization::mr_input(..., correlation = ld_matrix)` then call `mr_ivw(mr_obj, model = 'default', correl = TRUE)`.

```r
library(MendelianRandomization); library(ieugwasr)

ld <- ld_matrix(exposure_dat$SNP, bfile = '1kg_EUR/EUR', plink_bin = genetics.binaRies::get_plink_binary())

mr_obj <- mr_input(bx = dat$beta.exposure, bxse = dat$se.exposure,
                   by = dat$beta.outcome, byse = dat$se.outcome,
                   corr = ld)

result_correl <- mr_ivw(mr_obj, model = 'default', correl = TRUE)
```

Numerical caveat: when any pair of cis-pQTLs has r2 ~ 1 (e.g. perfect proxies), the LD matrix is rank-deficient and the SE explodes. Pre-prune at r2 < 0.95.

**API caveat for `MendelianRandomization::mr_ivw`:** Correlation between cis-pQTLs is supplied at MRInput construction via the correlation-matrix argument, whose formal name is `correlation=`; `corr=` also works only as an abbreviation resolved by R partial-matching, so prefer the explicit `correlation=`: `mr_input(bx, bxse, by, byse, correlation = ld_matrix)`. `mr_ivw()` then reads the correlation slot directly; passing `correl = TRUE` as an argument is redundant when MRInput already has a non-NA correlation matrix. A common bug is supplying both, which produces inconsistent behaviour across versions; prefer the MRInput-slot approach and treat `correl = TRUE` as a legacy flag.

### Robust / Penalized cis-IVW as a Correlated-Instrument Sensitivity Estimator

**Goal:** Provide a robust sensitivity estimate when cis-pQTLs are correlated and a minority may be outliers.

**Approach:** `mr_ivw(robust=TRUE, penalized=TRUE)` applies Burgess's robust-regression + penalized-weights IVW, down-weighting heterogeneous/outlying instruments. A distinct, more modern option is Patel, Gill, Newcombe, Burgess 2023 *Biometrics* 79:3458-3471, which reduces the dimension of correlated cis-variants in a single gene region via factor analysis and applies weak-factor-robust conditional inference; it exploits the within-region genetic-correlation (LD) structure rather than avoiding it, and is implemented separately from `mr_ivw`.

```r
library(MendelianRandomization)

mr_obj <- mr_input(bx = dat$beta.exposure, bxse = dat$se.exposure,
                   by = dat$beta.outcome, byse = dat$se.outcome,
                   corr = ld)
robust_res <- mr_ivw(mr_obj, model = 'default', robust = TRUE, penalized = TRUE)
```

Decision rule: standard cis-IVW when post-clumped LD r2 < 0.1; correlated-IV cis-IVW (Burgess 2017 Genet Epidemiol) when r2 between 0.1 and 0.7 AND ancestry-matched LD matrix is trustworthy; robust/penalized IVW (above) as a sensitivity check when a minority of instruments may be outliers; Patel 2023 conditional cis-MR when instruments are highly correlated and weak (factor-analysis + conditional inference). Benchmarks for these correlated-IV estimators are still evolving; report more than one as sensitivity when feasible.

## PAV Annotation via VEP

**Goal:** Tag every cis-pQTL with its most severe coding consequence to enable a PAV-excluded sensitivity panel.

**Approach:** Format SNPs as VEP input, run VEP, parse the `Consequence` column.

```bash
echo -e "chr1\t55039548\t.\tG\tT" > cis_pqtls.vcf
vep --species homo_sapiens --assembly GRCh38 --canonical --check_existing \
    --input_file cis_pqtls.vcf --output_file pqtl_vep.tsv --tab --force_overwrite
```

PAV consequences to flag (drop in sensitivity analysis): `missense_variant`, `stop_gained`, `stop_lost`, `frameshift_variant`, `splice_acceptor_variant`, `splice_donor_variant`, `start_lost`, `protein_altering_variant`. For aptamer panels, additionally consider `synonymous_variant` within the SOMAmer-binding region (rare but documented).

## Cis-Window Width: 500 kb vs 1 Mb Decision

- **Default ±500 kb** (Schmidt 2020 Nat Commun 11:3255 standard) -- balances cis-specificity against power; matches Open Targets Genetics defaults
- **Widen to ±1 Mb** when: (a) target gene has a documented distal regulatory element in ENCODE-rE2G or ABC enhancer-gene maps; (b) < 2 genome-wide-significant pQTLs are present in ±500 kb; (c) the target gene is unusually large (gene body > 500 kb itself, e.g. DMD, RBFOX1)
- **Narrow to ±250 kb** when high-density cis-eQTL background causes multi-gene pleiotropy concerns (e.g. HLA region; gene-dense pericentromeric loci)

Pre-specify the window in the methods section; window-width sensitivity is a recognized peer-review pushback (see Anticipated Reviewer Pushback below).

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Bonferroni for cis-MR pheWAS | Standard | `P < 0.05 / N_outcomes` for on-target adverse-effect scan |
| Bonferroni for proteome-wide cis-MR | Standard | `P < 0.05 / N_proteins` ~ 1.7e-5 for 2923 Olink proteins; ~1e-5 for 4907 SomaScan |
| Coloc PP.H4 >= 0.7 (suggestive) | Open Targets Genetics; Mountjoy 2021 Nat Genet 53:1527 | Exploratory; consistent with shared-causal |
| Coloc PP.H4 >= 0.8 (publication) | Wallace 2020 PLoS Genet 16:e1008720 | Standard peer-reviewed publication bar |
| Coloc PP.H4 >= 0.95 (industry) | Pharma internal target-validation standard | Drug-claim grade; clinical-pharmacology bar |
| Cis-pQTL F >= 10 | Staiger & Stock 1997; Burgess 2011 | Weak-instrument floor |
| Cis-window +/-500 kb | Schmidt 2020 Nat Commun 11:3255 | Standard cis definition; some pipelines use 1 Mb |
| r2 < 0.1 clumping in cis-window | Schmidt 2020 | Reduces LD-based pleiotropy while retaining power |
| N >= 2 pQTL datasets in agreement | Best-practice (UKB-PPP + deCODE) | Cross-platform replication mandatory for clinical claim |
| PAV-excluded sensitivity | Sun 2023 supplementary | Required for clinical claim; Olink/SomaScan vulnerable to PAV artifact |
| Neighbour-gene coloc PP.H4 < 0.5 | Operational | Cis-pQTL must NOT coloc with non-target gene; drop if it does |
| Steiger p > 0.05 (correct direction) | Hemani 2017 PLoS Genet 13:e1007081 | Directionality check; subject to Lutz 2022 caveat |
| Sample-overlap correction if both ends UKB | Burgess 2016 Genet Epidemiol 40:597 | One-sample-equivalent bias correction |

## Reconciliation: When Evidence Streams Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Cis-MR significant on Olink, null on SomaScan | Platform-specific epitope/aptamer artifact | PAV-annotate; flag protein as platform-discordant; do not claim |
| Cis-MR sig, coloc PP.H4 < 0.5 | LD-confounded signal; not shared causal | Downgrade; cis-MR alone insufficient; do not claim drug target |
| Coloc PP.H4 high, cis-MR null | Underpowered cis-MR (few cis-pQTLs, weak F) OR shared-causal for non-causal protein | Inspect cis-pQTL strength; consider increasing window to 1 Mb |
| Cis-MR sig with all pQTLs, null after PAV exclusion | PAV artifact dominating instrument | Report PAV-excluded as primary; original as supplementary |
| Cis-MR sig in UKB-PPP -> UKB outcome, null in FinnGen outcome | Sample-overlap one-sample bias | Treat FinnGen as truth; report UKB-on-UKB as biased upward |
| Cis-pQTL coloc with non-target gene's eQTL (PP.H4 >= 0.7) | Neighbour-gene mediation | Drop this cis-pQTL; re-run cis-MR with clean instruments |
| Two independent cis-pQTLs give opposite direction effects | Allelic heterogeneity with distinct biology | Run coloc.susie per credible set; report each signal separately |
| Wald ratio at sentinel SNP differs from cis-IVW | One outlier cis-pQTL dominates IVW | Run MR-PRESSO; check Egger intercept |

**Operational rule for publication:** Cis-IVW (or Wald ratio if N=1 SNP) + coloc.abf PP.H4 >= 0.8 + cross-platform replication (Olink and SomaScan agree in direction) + PAV-excluded sensitivity concordant + L2G >= 0.5 at disease GWAS lead = drug-target nomination ready. Industry-grade clinical claim requires PP.H4 >= 0.95. Any single missing leg downgrades the claim to "consistent with" rather than "evidence for."

## Drug Repurposing and Target Nomination

The Open Targets Drug platform (Ochoa 2021 Nucleic Acids Res 49:D1302) integrates approved-drug-target relationships, cis-pQTL/cis-eQTL MR, and locus-to-gene (L2G) scores (Mountjoy 2021). A target is nominated for repurposing when:

- L2G score at the GWAS lead points to the target gene
- Cis-MR estimate concordant with disease direction (lower protein -> lower disease for inhibitor candidate)
- Coloc PP.H4 >= 0.7 between target's cis-pQTL and disease GWAS
- A licensed drug exists that modulates the target
- The on-target adverse-effect pheWAS is acceptable

The PCSK9 monoclonal-antibody story is the canonical positive example; the CETP-inhibitor story is a canonical cautionary tale (cis-MR underestimated trial result due to off-target effects).

Cross-validate target nominations against the Comparative Toxicogenomics Database (CTD; ctdbase.org) and the Drug-Gene Interaction Database (DGIdb; dgidb.org) for established drug-target evidence and tractability annotations. STROBE-MR (Skrivankova 2021 JAMA 326:1614) provides the 20-item checklist for drug-target MR reporting; see causal-genomics/pleiotropy-detection for the full table.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `harmonise_data` drops most SNPs | EAF columns missing or palindromic at MAF~0.5 | Provide EAF; use `action = 2` (default) or `action = 3` for strictest |
| F-statistic from outcome | Computed `beta.outcome / se.outcome` | F must come from exposure (Burgess 2011) |
| Trans-pQTL included as instrument | Filtered only by P, not by genomic position | Restrict to +/-500 kb of target gene |
| PAV cis-pQTL artifact | Did not VEP-annotate | Run VEP; flag missense/nonsense/splice; report PAV-excluded sensitivity |
| Neighbour-gene mediation | Did not coloc cis-pQTL against neighbours | Run coloc.susie or coloc.abf vs non-target eQTL/pQTL in window |
| OpenGWAS OAuth failure | Token expired (OpenGWAS auth tightened 2024) | Use local plink + 1KG bfile via `ieugwasr::ld_clump(..., bfile=...)` |
| `mr_ivw(correl=TRUE)` SE explodes | Two cis-pQTLs in near-perfect LD | Pre-prune at r2 < 0.95; or drop redundant proxy |
| Cis-IVW null but Wald ratio at lead significant | Inclusion of weak / outlier cis-pQTLs | Tighten clumping; run MR-PRESSO outlier test |
| Sample overlap unreported | Both GWAS from UKB; analyst assumed two-sample | Apply Burgess 2016 correction OR use MR-RAPS OR move outcome to FinnGen |
| Coloc PP.H3 dominant | Multiple causal in moderate LD | Switch to coloc.susie with ancestry-matched LD |
| Olink and SomaScan disagree | Platform-specific epitope artifact | Annotate PAV; flag as platform-discordant; do not claim drug-target |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Cross-platform replication?" | Olink (UKB-PPP) and SomaScan (deCODE / Fenland) agreement reported; direction match mandatory, magnitude within 2x; PAV-excluded sensitivity included |
| "PAV check?" | Ensembl VEP annotation of every cis-pQTL; PAV-excluded sensitivity reported alongside primary; concordance criteria (direction + 2x magnitude + nominal P) documented |
| "Neighbour-gene coloc?" | coloc.abf of each cis-pQTL against all eQTLs and pQTLs within ±500 kb in the relevant tissue; PP.H4 < 0.5 for off-target genes required for instrument retention |
| "Reverse causation?" | Steiger filter applied per cis-pQTL; bidirectional cis-MR run; pre-symptomatic-cohort replication (AoU, longitudinal sub-studies) reported when available |
| "Sample overlap (UKB-on-UKB)?" | MRlap correction applied (Mounier 2023); or outcome moved to independent cohort (FinnGen DF12, MVP, Biobank Japan); overlap fraction documented |
| "Industry-grade threshold?" | PP.H4 >= 0.95 reported for drug-claim grade; >= 0.8 for standard publication; 3-tier ladder pre-specified in methods |
| "OT L2G concordance?" | Open Targets Platform L2G score >= 0.5 at the disease GWAS lead reported (cross-reference effector-gene-prioritization) |
| "Cis-window width?" | ±500 kb default (Schmidt 2020) pre-specified; widened to ±1 Mb only with documented distal regulatory rationale |
| "Patel 2023 vs Burgess 2017?" | Both reported when post-clumped LD r2 > 0.1; Patel 2023 robust estimator preferred when LD reference is ancestry-mismatched |

## Tool Installation Notes

```r
install.packages(c('remotes', 'MendelianRandomization', 'coloc', 'susieR', 'dplyr'))
remotes::install_github('MRCIEU/TwoSampleMR')
remotes::install_github('MRCIEU/ieugwasr')
remotes::install_github('MRCIEU/genetics.binaRies')   # bundles plink binary
remotes::install_github('rondolab/MR-PRESSO')
```

```bash
# Ensembl VEP for PAV annotation
conda install -c bioconda ensembl-vep
vep_install -a cf -s homo_sapiens -y GRCh38 -c $HOME/.vep

# 1000 Genomes EUR plink reference for local clumping / LD matrix
# Prebuilt at https://mrcieu.github.io/ieugwasr/
```

pQTL data acquisition: UKB-PPP via the UK Biobank pre-published portal (ukb-ppp.gwas.eu); deCODE via the deCODE Genetics summary-stat website with a data-use agreement; Fenland via the EBI GWAS catalog and Pietzner 2021 supplementary; OpenGWAS hosts many pre-formatted pQTL studies but always verify the upstream reference and download date.

## References

- Schmidt AF et al 2020 Nat Commun 11:3255 (cis-MR drug-target framework)
- Sun BB et al 2023 Nature 622:329 (UKB-PPP Olink Explore)
- Ferkingstad E et al 2021 Nat Genet 53:1712 (deCODE SomaScan)
- Pietzner M et al 2021 Science 374:eabj1541 (Fenland SomaScan)
- Sun BB et al 2018 Nature 558:73 (INTERVAL SomaScan)
- Zhang J et al 2022 Nat Genet 54:593 (ARIC multi-ancestry pQTL)
- Emilsson V et al 2018 Science 361:769 (AGES-Reykjavik)
- Eldjarn G et al 2023 Nature 622:348 (Olink vs SomaScan cross-platform comparison)
- Schmidt AF et al 2017 Lancet Diabetes Endocrinol 5:97 (PCSK9 -> T2D pheWAS exemplar)
- Burgess S, Zuber V, Valdes-Marquez E, Sun BB, Hopewell JC 2017 Genet Epidemiol 41:714-725 (correlated-IV IVW)
- Burgess S et al 2016 Genet Epidemiol 40:597 (sample-overlap correction)
- Mountjoy E et al 2021 Nat Genet 53:1527 (Open Targets Genetics L2G + coloc)
- Ochoa D et al 2021 Nucleic Acids Res 49:D1302 (Open Targets Drug platform)
- Lutz SM et al 2022 Genet Epidemiol 46:139 (Steiger caveat under unmeasured confounding)
- Verbanck M et al 2018 Nat Genet 50:693 (MR-PRESSO)
- Wallace C 2020 PLoS Genet 16:e1008720 (coloc p12 sensitivity)
- Skrivankova VW et al 2021 JAMA 326:1614 (STROBE-MR)
- Patel A, Gill D, Newcombe P, Burgess S 2023 Biometrics 79:3458-3471 (robust cis-MR with correlated instruments)
- Mounier N & Kutalik Z 2023 Genet Epidemiol 47:314 (MRlap sample-overlap + winner's-curse correction)

## Related Skills

- causal-genomics/mendelian-randomization - Parent polygenic-MR framework; cis-MR is the drug-target specialization; MRlap sample-overlap correction
- causal-genomics/colocalization-analysis - Required PP.H4 triangulation for any cis-MR drug-target claim
- causal-genomics/fine-mapping - Credible-set construction prior to coloc.susie at the cis-locus
- causal-genomics/pleiotropy-detection - MR-PRESSO / Egger diagnostics adapted to cis-window; STROBE-MR 20-item checklist
- causal-genomics/transcriptome-wide-association - eQTL-based parallel evidence for the same target
- causal-genomics/mediation-analysis - Step from cis-MR to downstream mediator pathway
- causal-genomics/effector-gene-prioritization - Open Targets L2G concordance leg of the triangulation panel
- population-genetics/association-testing - Source GWAS pipelines for pQTL discovery
- population-genetics/linkage-disequilibrium - LD-matrix construction for cis-IVW correl=TRUE
- variant-calling/variant-annotation - VEP PAV annotation for sensitivity analysis
- clinical-databases/clinvar-lookup - Pathogenic-variant context for nominated targets
<!-- END FILE: causal-genomics/proteome-mr-drug-target/SKILL.md -->

## 子目录：causal-genomics/transcriptome-wide-association

<!-- BEGIN FILE: causal-genomics/transcriptome-wide-association/SKILL.md -->
---
name: bio-causal-genomics-transcriptome-wide-association
description: Performs gene-level association from GWAS summary statistics via genetically predicted tissue expression using FUSION, PrediXcan, S-PrediXcan, S-MultiXcan, UTMOST, MOSTWAS, kTWAS, EpiXcan, TIGAR-V2, and probabilistic fine-mapping with FOCUS and MA-FOCUS. Use when running TWAS from GWAS sumstats, prioritising candidate causal genes from a GWAS lead locus, picking single-tissue vs cross-tissue models, identifying LD-induced TWAS false positives, choosing ancestry-matched prediction weights, fine-mapping co-regulated TWAS hits, or triangulating TWAS with cis-eQTL Mendelian randomization and colocalization to nominate a causal gene.
tool_type: mixed
primary_tool: FUSION
---

## Version Compatibility

Reference examples tested with: FUSION (head of `gusevlab/fusion_twas`, scripts dated 2023+), MetaXcan / S-PrediXcan / S-MultiXcan 0.7.5+ (`hakyimlab/MetaXcan`), PrediXcan model files from PredictDB (GTEx v8 elastic-net + MASHR), UTMOST (head of `Joker-Jerome/UTMOST`), pyfocus 0.8+ (`bogdanlab/focus`), MA-FOCUS (head of `mancusolab/ma-focus`), TIGAR-V2 (head of `yanglab-emory/TIGAR`), PLINK 1.9 + PLINK 2.0, R 4.3+, Python 3.9-3.11.

Before using code patterns, verify installed versions match. If versions differ:
- R: `Rscript --version`; for FUSION scripts inspect `--help` flags directly in the source
- Python: `pip show pyfocus` (MetaXcan is git-cloned, not on PyPI) then `SPrediXcan.py --help`, `SMulTiXcan.py --help`, `focus finemap --help`
- CLI: `plink2 --version`; FUSION ships as R scripts not a binary

If a script throws an error about an argument that has moved (e.g. `--gwas_file` vs `--gwas-file`) or a model database schema change, introspect the installed script with `--help` and adapt rather than retrying. PredictDB model file paths change with GTEx version; pin the version explicitly in scripts.

# Transcriptome-Wide Association

**"Find genes whose predicted tissue expression is associated with my GWAS trait"** -> Train SNP -> expression prediction models on a reference eQTL panel, apply the per-gene SNP weights to GWAS summary statistics or genotypes, and produce a gene-level Z-score equivalent to a weighted sum of SNP Z-scores. The output is a gene-by-tissue association, but TWAS is NOT direct evidence of causal mediation: an LD-tagged eQTL signal produces the same statistical association as a truly causal one, and the dominant failure modes are LD-induced false positives at gene-dense loci, tissue mis-specification, and ancestry mismatch between GWAS and prediction weights.

- CLI (sumstat TWAS, R): `FUSION.assoc_test.R --sumstats g.sumstats --weights weights.pos --weights_dir wgt/ --ref_ld_chr 1KG/EUR. --chr 22 --out chr22.dat`
- CLI (S-PrediXcan, Python): `SPrediXcan.py --model_db_path gtex_v8.db --covariance gtex_v8.cov --gwas_file g.txt --output_file out.csv`
- CLI (S-MultiXcan joint): `SMulTiXcan.py --models_folder mashr_models/ --gwas_folder gwas/ --metaxcan_folder spredixcan_per_tissue/ --output joint.csv`
- CLI (UTMOST cross-tissue): joint test across tissues via UTMOST's per-tissue GBJ / GBJ2 step
- CLI (FOCUS fine-mapping): `focus finemap gwas.sumstats 1KG_EUR focus.db --chr 22 --p-threshold 5e-8 --out chr22.focus`
- CLI (MA-FOCUS multi-ancestry): `focus finemap` with colon-separated per-ancestry sumstats / LD / weights and hyphen-joined ancestry codes in `--locations` (e.g. `38:EUR-EAS-AFR`)

TWAS, cis-eQTL MR, and coloc operate on overlapping evidence: TWAS asks "is the gene's predicted expression associated with the trait?"; cis-eQTL MR asks "does the eQTL effect on expression mediate the trait effect under IV assumptions?"; coloc asks "do the GWAS and eQTL share a causal variant?". Strong causal claims require triangulation, not single-method significance.

## Algorithmic Taxonomy

| Tool | Model | Input | Output | Strength | Fails when |
|------|-------|-------|--------|----------|------------|
| FUSION (Gusev 2016 Nat Genet 48:245) | Weighted sum of SNP Z-scores; per-gene multi-model (BLUP, lasso, elnet, top1, bslmm) selected by cross-validation R^2 | GWAS sumstats + pre-computed weights (.pos + per-gene RData) | TWAS Z, p; conditional joint analysis | Mature, ENCODE-style, pre-trained weights for many tissues (GTEx, CMC, METSIM, YFS, NTR) | LD-induced false positives at gene-dense loci; needs ancestry-matched LD reference; weights are heritability-thresholded so low-h2 genes drop |
| PrediXcan (Gamazon 2015 Nat Genet 47:1091) | Elastic-net SNP -> expression prediction; individual-level genotypes | PLINK genotypes + GWAS phenotype + GTEx prediction DB | Per-gene association test with full regression machinery | Most flexible (allows covariates, interactions, binary outcomes); same TWAS interpretation | Requires individual-level data; biobank-scale compute |
| S-PrediXcan (Barbeira 2018 Nat Commun 9:1825) | Summary-statistic equivalent of PrediXcan; Z-score weighted sum analogous to FUSION | GWAS sumstats + PredictDB model + covariance | Per-gene Z, p | Public PredictDB models (GTEx v8 elastic-net + MASHR-EUR); minimal compute | Pre-trained weights ancestry-specific (EUR primarily); covariance file must match model DB |
| S-MultiXcan (Barbeira 2019 PLoS Genet 15:e1007889) | Joint multi-tissue test combining per-tissue S-PrediXcan via PCA-regularised regression | Folder of per-tissue S-PrediXcan outputs + model folder | Single joint p per gene + per-tissue significance | Boosts power when causal tissue is unknown; standard for transcriptome-wide screens | Joint test cannot pinpoint causal tissue; correlated tissues produce ill-conditioned regression |
| UTMOST (Hu 2019 Nat Genet 51:568) | Cross-tissue elastic-net (group lasso) for joint tissue prediction + GBJ test | Per-tissue eQTL data + GWAS sumstats | Cross-tissue joint statistic | Often better-powered than S-MultiXcan at cross-tissue genes | Computationally heavier than MetaXcan; tissue weights are less interpretable |
| MOSTWAS (Bhattacharya 2021 PLoS Genet 17:e1009398) | Mediator-aware TWAS adding distal trans-mediating SNPs to cis-only models | GWAS sumstats + MOSTWAS weights | Per-gene Z, p (TWAS + distal mediator extension) | Recovers signal at genes with non-cis genetic regulation | Trans-mediation models need large reference panel; weights less broadly available |
| kTWAS (Cao 2021 Brief Bioinform 22:bbaa270) | Kernel-based TWAS using SKAT-style aggregation | GWAS sumstats or genotypes + per-gene SNP set | Per-gene p | Robust to non-linear and rare-variant contributions | Loses the eQTL-weighting interpretability; less standardised |
| EpiXcan (Zhang 2019 Nat Commun 10:3834) | Adds epigenome-derived per-SNP prior to weight training | eQTL + epigenome + GWAS sumstats | Per-gene Z, p (epigenome-informed) | Higher prediction R^2 in epigenome-rich tissues | Requires matched epigenome data for the prediction tissue |
| TIGAR-V2 (Parrish 2022 HGG Adv 3:100068) | Dirichlet process regression (non-parametric Bayes) for SNP -> expression | Reference eQTL + GWAS sumstats | Per-gene Z, p | Captures non-elastic-net effect structures; more flexible weight learning | Slower training; benefits depend on locus genetics |
| FOCUS (Mancuso 2019 Nat Genet 51:675) | Probabilistic gene-level fine-mapping over TWAS Z-scores using gene-by-gene predicted-expression correlation as analog of LD | FUSION/S-PrediXcan TWAS Z + ancestry-matched LD reference | Per-gene PIP + credible gene set | Resolves co-regulated gene clusters into a probabilistic causal gene; standard add-on after TWAS | Requires the same prediction-weight panel that produced TWAS Z; PIPs depend on prior |
| MA-FOCUS (Lu 2022 AJHG 109:1388-1404) | Multi-ancestry FOCUS; joint gene fine-mapping across ancestries with shared causal-gene assumption | Per-ancestry TWAS sumstats + per-ancestry weights + per-ancestry LD | Cross-ancestry PIP | Smaller credible gene sets when AFR/EAS contribute non-EUR LD information | Trans-ethnic gene-effect heterogeneity violated; weights must be ancestry-matched |
| JEPEG / JEPEG-Mix (Lee 2015 / 2016) | Gene-based test combining eQTL and functional weights | GWAS sumstats + JEPEG annotation database | Per-gene p | Lightweight gene-burden alternative to TWAS | Less granular than full PrediXcan/FUSION machinery; minimally updated |

Methodology evolves; the FUSION-vs-PrediXcan landscape has been stable but probabilistic fine-mapping (FOCUS, MA-FOCUS) and integrative methods (MOSTWAS, EpiXcan, OmicsXcan) continue to advance. Verify against the current PredictDB release notes (predictdb.org) and the latest FUSION weight panels (gusevlab.org/projects/fusion) before locking on a tissue or model.

S-PrediXcan and FUSION are mathematically near-identical: both compute a weighted sum of GWAS SNP Z-scores using per-gene SNP-expression weights and an LD-aware variance correction. The practical differences reduce to (a) the weight panel (FUSION elastic-net vs PredictDB MASHR), (b) the LD reference, and (c) the per-gene heritability threshold; the supplement of Barbeira 2018 works through the algebra. Method choice should therefore be driven by panel availability and ancestry-match, not by the underlying algorithm.

### PredictDB Model Choice and GTEx Versioning

| Release | Cohort | Status (2026) | When to use |
|---------|--------|----------------|-------------|
| GTEx v8 (838 donors, 49 tissues, 2020) | EUR-dominant (~85%) | Current PredictDB standard | Default; pre-trained MASHR + elastic-net DBs available |
| GTEx v9 (2023) | Expanded harmonization | Not migrated into PredictDB | Do not use until PredictDB rebuilds |
| GTEx v10 (2024 AnVIL release) | Re-aligned to GRCh38 v44 | Limited harmonization; not PredictDB-default | Wait for community-validated weight panels |

**Operational rule:** Use GTEx v8 unless there is an explicit biological reason to deviate (tissue not in v8, ancestry-specific panel preferred). In methods, pin exactly: "GTEx v8 MASHR-EUR, PredictDB release 2022-01".

### MASHR vs Elastic-Net Models

PredictDB ships two cross-validated model families per tissue (Barbeira 2021 Genome Biol 22:49):

| Model | Construction | Per-gene SNP count | When to use |
|-------|--------------|---------------------|-------------|
| MASHR | Cross-tissue posterior mean from DAP-G fine-mapped SNPs | ~10x sparser | Primary discovery; higher per-gene R^2 in most genes; standard for S-MultiXcan |
| Elastic-net | Per-tissue lasso/ridge mix (alpha = 0.5) | Denser | Tissues where MASHR's cross-tissue prior is mis-specified (ovary, testis, isolated-organ traits) |

**Operational rule:** Never mix MASHR and elastic-net within a single S-MultiXcan run; the inter-tissue covariance and condition number assumptions break. Pick one family and apply consistently across all tissues.

## Decision Tree by Experimental Scenario

| Scenario | Recommended workflow | Why |
|----------|---------------------|-----|
| GWAS summary stats only, EUR, single hypothesis tissue (e.g. liver for LDL) | S-PrediXcan with GTEx v8 MASHR-EUR weights, or FUSION with GTEx liver | Standard pre-trained pipeline; minimal compute |
| GWAS summary stats only, tissue unknown a priori | S-MultiXcan (standard GTEx v8) OR UTMOST (custom panel) -- see S-MultiXcan vs UTMOST table | Joint multi-tissue inflates power; tissue prioritisation requires LDSC-SEG separately |
| Multiple TWAS hits at one locus (gene-dense region) | Run TWAS then FOCUS for probabilistic fine-mapping | LD ties co-regulated genes; FOCUS PIP distinguishes likely causal gene |
| Multi-ancestry GWAS (EUR + EAS + AFR) | Per-ancestry S-PrediXcan with matched weights, then MA-FOCUS to combine | Single-ancestry weights miscalibrated in other ancestries; joint fine-mapping shrinks credible set |
| Individual-level genotypes available (UKB) | PrediXcan (full regression) | Allows covariates, interactions, binary outcomes natively |
| Low-N tissue (GTEx N < 100) | Substitute eQTLGen (whole blood, N ~ 31k) OR skip the tissue | Per-gene CV R^2 unstable below N ~ 100; weights overfit |
| Drug-target prioritisation (TWAS as causal-gene evidence) | TWAS + cis-eQTL MR + coloc + FOCUS triangulation | TWAS alone is associational; triangulation strengthens causal claim |
| Trans-acting / mediator-aware analysis | MOSTWAS | Adds distal trans-mediating SNPs to cis-only models |
| Rare-variant or non-linear gene effects | kTWAS or TIGAR-V2 | Kernel / non-parametric flexibility |
| HLA region (chr6:25-35 Mb hg38) | Exclude or use HLA-specific tools | Long-range LD breaks every gene-by-gene method; standard TWAS PIPs not interpretable |
| Splicing-mediated trait (e.g. neuropsych for sQTL) | sTWAS (sQTL-weighted TWAS) using GTEx splicing models | Splicing mediates many GWAS effects; cis-sQTL panels available in PredictDB |
| Cell-type-specific trait | sc-eQTL-based TWAS (e.g. OneK1K, Yazar 2022 Science 376:eabf3041) | Bulk-tissue TWAS averages over cell types; single-cell eQTL recovers cell-type specificity |

### Tissue Selection Protocol

Tissue choice drives TWAS power and false-positive rate; selecting tissues by inspecting TWAS hit count is circular. Run all three of the following on the GWAS sumstats (independent of any TWAS run) and pick the primary TWAS tissue from the intersection:

1. **Stratified LDSC tissue prioritization** (Finucane 2018 Nat Genet 50:621): `ldsc.py --h2-cts <sumstats> --ref-ld-chr-cts <annot> --w-ld-chr <weights>` against 200+ tissue-specific gene expression annotations
2. **CELLEX** (Timshel 2020 eLife 9:e55851): single-cell tissue / cell-type prioritization on the same GWAS
3. **MAGMA gene-property analysis** (de Leeuw 2015 PLoS Comput Biol 11:e1004219): cheaper substitute when LDSC unavailable

**Operational rule:** Primary TWAS tissue = the tissue with FDR-significant enrichment in at least two of the three methods. Run secondary tissues in S-MultiXcan for cross-tissue replication. Bonferroni for tissue selection alone: 0.05 / 200 annotations = 2.5e-4.

### S-MultiXcan vs UTMOST

| Method | Use case | Rationale |
|--------|----------|-----------|
| S-MultiXcan (Barbeira 2019) | Standard GTEx v8 analysis | Pre-computed MASHR weights; lower compute barrier; PCA-regularised inter-tissue regression |
| UTMOST (Hu 2019 Nat Genet 51:568) | Custom eQTL panel with cross-tissue retraining | Higher power at genes with shared cross-tissue eQTL architecture; group-lasso enforces sparsity across tissues |

Benchmarks: Hu 2019, Barbeira 2019. Choose by panel availability first; the methods recover overlapping but non-identical gene sets.

### Single-Cell and Cell-Type-Resolved TWAS

Bulk-tissue TWAS averages over cell composition; sc-eQTL TWAS recovers cell-type-specific regulation but at lower per-cell-type power.

| Panel | Reference | Cells / tissue |
|-------|-----------|----------------|
| OneK1K | Yazar 2022 Science 376:eabf3041 | PBMC, ~982 donors, 14 cell types |
| HipSci iPSC-eQTL | Kilpinen 2017 Nature 546:370 | iPSC, ~317 donors |
| BLUEPRINT | Chen 2016 Cell 167:1398 | Monocytes, neutrophils, T cells |

**Tooling state (2026):** No fully pre-built scPrediXcan equivalent to MASHR; sc-eQTL weights are panel-specific. Train custom PredictDB or use TIGAR-V2's Bayesian DPR on the sc-eQTL matrix.

**Operational rule:** Run standard bulk-tissue TWAS first; run sc-eQTL TWAS in the prioritized cell type as a secondary analysis; require concordance between bulk and sc results before nominating a cell-type-specific gene. Upstream sc preprocessing: cross-reference single-cell/preprocessing.

## Per-Tool Failure Modes

### LD-induced TWAS false positives (most common pitfall)

**Trigger:** Two or more genes at the same locus have correlated cis-eQTLs (shared causal eQTL SNP or LD-linked eQTL SNPs).

**Mechanism:** TWAS Z-scores are linear combinations of SNP Z-scores weighted by per-gene SNP effects. When two genes share many high-weight SNPs (e.g. nearby genes regulated by the same enhancer or LD-tagged independent eQTLs), their TWAS Z-scores are positively correlated. A single causal GWAS variant therefore produces significant Z at multiple co-regulated genes (Wainberg 2019 Nat Genet 51:592; Mancuso 2019 Nat Genet 51:675).

**Symptom:** A GWAS lead locus shows 3-10 genes all passing genome-wide TWAS significance (p < 2.3e-6 ~ 0.05/22k); per-gene LocusZoom-style plots look near-identical; conditional analysis (FUSION.post_process.R runs conditional/joint analysis by default; FUSION.assoc_test.R's `--coloc_P` adds single-SNP coloc) reveals only 1-2 independent gene signals; the genes lie within 1 Mb of each other.

**Fix:** Always run FOCUS after TWAS to obtain per-gene PIPs. Report only genes with PIP >= 0.8 as candidate causal; report co-significant genes with PIP < 0.5 as LD-tagged. Cross-check with cis-eQTL coloc (PP.H4 >= 0.7) for the candidate causal gene. FUSION's `FUSION.post_process.R` performs conditional/joint analysis by default (no `--joint` flag) as a lighter-weight alternative.

### Tissue mis-specification

**Trigger:** Running TWAS in a tissue that does not host the causal regulatory effect (e.g. whole blood for a psychiatric trait; pancreas for an LDL trait).

**Mechanism:** A gene's cis-eQTL effect size varies across tissues; a wrong-tissue model has weaker per-gene prediction R^2 and lower power. Conversely, eQTL effects in the wrong tissue can still tag the GWAS signal via LD and produce spurious associations not present in the causal tissue.

**Symptom:** Strong TWAS signal in a tissue biologically irrelevant to the trait; null in the expected tissue; tissue-prioritisation methods (LDSC-SEG, Finucane 2018 Nat Genet 50:621; RolyPoly (Calderon 2017 AJHG 101:686)) disagree with the TWAS tissue.

**Fix:** Run S-MultiXcan to combine tissues if causal tissue is unknown. For prioritisation, use LDSC-SEG / CELLEX / EWCE on the GWAS sumstats independently of TWAS, and report TWAS in the prioritised tissues. Never report a single-tissue TWAS hit as causal without independent tissue evidence (single-cell eQTL, chromatin accessibility in matched cell type).

### Ancestry mismatch in prediction weights

**Trigger:** Running TWAS on a non-EUR GWAS using GTEx (~ 85% EUR) weights, or vice versa.

**Mechanism:** Cis-eQTL effect sizes and LD structure are ancestry-specific; prediction weights trained in one ancestry transfer with reduced R^2 and biased Z-scores in another. Power is lost preferentially at loci where the causal eQTL is not shared across ancestries (Patel 2022 AJHG 109:1286).

**Symptom:** Genome-wide TWAS hit count much lower than expected given GWAS power; non-EUR-specific GWAS loci fail to produce TWAS hits; per-gene prediction R^2 substantially reduced.

**Fix:** Use ancestry-matched prediction panels where available: MESA multi-ethnic eQTL (Mogil 2018 PLoS Genet), eQTLGen-Asian, AFGR (Africa) when published, or MAGE (Taliun-style multi-ancestry eQTL). Move to MA-FOCUS for cross-ancestry joint fine-mapping. Document the ancestry assumption explicitly in methods.

### Low-N tissue weights are unstable

**Trigger:** Using a GTEx tissue with N < 100 donors (e.g. several brain sub-regions, kidney cortex in v7).

**Mechanism:** Per-gene elastic-net weights are cross-validated with the available donors. Below ~ 100 donors, the cross-validation R^2 has high variance and the heritability filter (FUSION requires hsq_p < 0.01) drops many genes. Surviving weights overfit, inflating per-gene Z under the null.

**Symptom:** Tissue produces unusually high TWAS hit count or unusually high genomic inflation; per-gene CV R^2 distribution is bimodal with a long heavy tail.

**Fix:** Skip GTEx tissues with N < 100 unless biologically essential. Substitute eQTLGen for whole blood (N ~ 31k, Vosa 2021 Nat Genet 53:1300) where blood is acceptable. For brain, use PsychENCODE (N ~ 1300, Wang 2018 Science 362:eaat8464) or BrainSeq (N ~ 350+) when available; verify the matching prediction-weight panel exists.

### HLA region

**Trigger:** Any gene within chr6:25-35 Mb (hg38; extended MHC) reported by TWAS.

**Mechanism:** Long-range LD (r2 > 0.5 over many Mb) and extreme structural variation mean per-gene prediction weights at HLA capture haplotype rather than gene-specific regulation. Standard TWAS gene-level inference is biologically meaningless here.

**Fix:** Exclude chr6:25-35 Mb from genome-wide TWAS summaries by default. For HLA-driven traits (autoimmune, infection, transplantation), impute classical HLA alleles using one of:

| Tool | Reference | Notes |
|------|-----------|-------|
| HIBAG | Zheng 2014 Pharmacogenomics J 14:192 | R package; pre-trained per-ancestry classifiers |
| SNP2HLA | Jia 2013 PLoS One 8:e64683 | Beagle-based imputation; supports T1DGC reference |
| HLA-TAPAS | Luo 2021 Nat Genet 53:1504 | Current standard; multi-ancestry reference; recommended for new analyses |

Then test classical alleles plus amino-acid residues (Raychaudhuri 2012 Nat Genet 44:291 set the gold standard for residue-level association in MHC). Do NOT run SNP-level TWAS inside the MHC.

### Correlated-expression confounding (co-regulated genes)

**Trigger:** Two or more genes are functionally co-regulated by a single TF or enhancer, producing nearly-identical predicted-expression vectors.

**Mechanism:** Even with separate per-gene cis-eQTL prediction, downstream co-regulation makes predicted expression highly correlated; TWAS cannot distinguish which gene mediates the trait.

**Symptom:** FOCUS credible gene set contains multiple genes with PIP roughly equal (e.g. three genes at 0.3 each); functional follow-up (MPRA, CRISPRi screens) is needed to break the tie.

**Fix:** Acknowledge the limit of statistical resolution; report the full credible gene set and prioritise on orthogonal evidence (CRISPRi/CRISPRa effect size in matched cell type, e.g. Open Targets-style, or MPRA at allelic series; protein-level pQTL coloc if available).

## TWAS - MR - Coloc Triangulation

A TWAS-significant gene is associational, not causal. The strongest defensible claim that a gene mediates a GWAS effect comes from triangulating three orthogonal lines of evidence:

| Line | What it tests | Threshold |
|------|---------------|-----------|
| TWAS | Predicted-expression association with trait | S-MultiXcan joint p < 2.3e-6, OR S-PrediXcan per-tissue p < 4.6e-8 (49-tissue Bonferroni), OR per-tissue FDR < 0.05 |
| cis-eQTL MR | Causal effect of expression on trait under IV assumptions (cross-reference causal-genomics/mendelian-randomization) | Wald-ratio or IVW p < 0.05/n_genes; instrument F > 10 |
| Colocalization | Shared causal variant between GWAS and eQTL (cross-reference causal-genomics/colocalization-analysis) | coloc.abf or coloc.susie PP.H4 >= 0.7 |
| FOCUS | Probabilistic per-gene PIP under TWAS fine-mapping | PIP >= 0.8 |

**Operational rule:** Report a gene as a "strong candidate causal gene" only when 3 of the 4 are concordant (TWAS hit + coloc PP.H4 >= 0.7 + FOCUS PIP >= 0.8, with cis-MR as a supporting fourth). 2-of-4 concordance is "suggestive"; 1-of-4 is "associational only". The combination is more conservative than any single method but matches the standards used in modern GWAS-to-target pipelines (Open Targets Genetics Mountjoy 2021 Nat Genet 53:1527; FinnGen R10 release notes).

## Quantitative Thresholds

| Quantity | Threshold | Source / Rationale |
|----------|-----------|--------------------|
| S-MultiXcan joint p (gene-wide) | < 2.3e-6 (0.05 / 22k genes) | One p per gene across tissues; standard genome-wide TWAS significance |
| S-PrediXcan per-tissue (49 tissues) | < 4.6e-8 (0.05 / (49 x 22k)) | Cross-tissue x cross-gene Bonferroni |
| Per-tissue FDR (alternative) | BH q < 0.05 within each tissue | Less conservative; report cross-tissue replication of FDR-significant hits |
| FUSION cross-validation R^2 | >= 0.01 (per gene) | FUSION default heuristic; below this, gene is not heritable in tissue and weights drop |
| FUSION heritability p | < 0.01 (hsq_p) | FUSION default; filters out non-heritable expression |
| Coloc PP.H4 for triangulation | >= 0.7 | Open Targets / common practice; >= 0.8 for high-confidence |
| FOCUS gene PIP (causal) | >= 0.8 | Mancuso 2019 convention; PIP >= 0.5 is suggestive |
| cis-eQTL MR instrument F | >= 10 | Standard MR convention to avoid weak-instrument bias |
| Tissue eQTL N (weight stability) | >= 100 donors | Below this, per-gene elastic-net weights unstable |
| cis-window radius | +/- 500 kb of gene TSS/TES (FUSION) or +/- 1 Mb (S-PrediXcan) | Captures most cis-eQTL signal; window choice rarely changes top hits |
| LD reference panel size | >= 500 individuals matched ancestry | 1000 Genomes superpopulation reference is standard |
| MA-FOCUS minimum ancestry N | >= 2 ancestries with significant TWAS | Joint inference requires non-trivial heterogeneity |
| S-MultiXcan condition number | < 30 (correlation matrix) | PCA regularisation kicks in above this; near-collinear tissues collapsed |

## FUSION Pipeline

**Goal:** Run sumstat TWAS using FUSION and conditional joint analysis to identify independently associated genes.

**Approach:** Format GWAS sumstats to FUSION expected columns (SNP A1 A2 Z); run `FUSION.assoc_test.R` per chromosome with pre-computed weights and ancestry-matched LD; post-process with `FUSION.post_process.R` (conditional/joint analysis run by default) to identify independent genes; flag conditional-significant genes for follow-up.

```bash
# Pre-computed FUSION weights live at http://gusevlab.org/projects/fusion/
# Example: GTEx v8 Whole_Blood; download .pos summary + per-gene RData files into wgt_dir/

# GWAS sumstats expected columns: SNP A1 A2 Z (Z-score on standardised scale)
# Use TwoSampleMR or a custom munger to harmonise alleles upstream

for chr in {1..22}; do
    Rscript FUSION.assoc_test.R \
        --sumstats gwas.sumstats \
        --weights gtex_whole_blood.pos \
        --weights_dir gtex_whole_blood_wgt/ \
        --ref_ld_chr 1000G_EUR_LD/EUR. \
        --chr ${chr} \
        --out twas_chr${chr}.dat
done
cat twas_chr*.dat > twas_all.dat

# Conditional joint analysis at each significant locus
Rscript FUSION.post_process.R \
    --sumstats gwas.sumstats \
    --input twas_all.dat \
    --out twas_joint.dat \
    --ref_ld_chr 1000G_EUR_LD/EUR. \
    --chr 22 \
    --plot --locus_win 100000
# twas_joint.dat reports per-gene conditional Z; genes with joint Z > 4 are independent
```

The `--locus_win 100000` parameter defines the conditioning window; 100 kb is conservative for non-HLA loci. FUSION's `--coloc_P` flag runs single-SNP coloc internally but is less robust than running coloc separately on the per-gene top eQTL.

## S-PrediXcan + S-MultiXcan Pipeline

**Goal:** Run TWAS across all GTEx tissues using pre-trained PredictDB models, then combine via S-MultiXcan for a joint multi-tissue test.

**Approach:** For each tissue, run S-PrediXcan with the matched model DB and covariance file; collect per-tissue outputs into a folder; run S-MultiXcan with the same model folder and GWAS to produce a joint multi-tissue Z and per-tissue significance.

```bash
# PredictDB models: predictdb.org
# GTEx v8 MASHR-EUR is the standard EUR panel
# Each tissue has a .db (model) and .txt.gz (covariance) file pair

mkdir -p spredixcan_out
for tissue in Whole_Blood Liver Brain_Frontal_Cortex_BA9 Adipose_Subcutaneous; do
    python SPrediXcan.py \
        --model_db_path mashr_models/mashr_${tissue}.db \
        --covariance mashr_models/mashr_${tissue}.txt.gz \
        --gwas_file gwas.txt \
        --snp_column SNP --effect_allele_column A1 --non_effect_allele_column A2 \
        --beta_column BETA --pvalue_column P \
        --output_file spredixcan_out/${tissue}.csv
done

# Joint multi-tissue
python SMulTiXcan.py \
    --models_folder mashr_models/ \
    --models_name_pattern "mashr_(.*)\.db" \
    --snp_covariance gtex_v8_expression_mashr_snp_covariance.txt.gz \
    --metaxcan_folder spredixcan_out/ \
    --metaxcan_filter "(.*)\.csv" \
    --metaxcan_file_name_parse_pattern "(.*)\.csv" \
    --gwas_file gwas.txt \
    --snp_column SNP --effect_allele_column A1 --non_effect_allele_column A2 \
    --beta_column BETA --pvalue_column P \
    --output joint_multitissue.csv
```

S-MultiXcan applies PCA regularisation on the inter-tissue correlation matrix; `--regularization 0.1` (not a default -- it must be passed explicitly; the argument otherwise defaults to off) applies a ridge, while `--cutoff_condition_number 30` (the canonical MetaXcan setting) conditions by dropping near-collinear components. Tissues that are nearly collinear with another (e.g. multiple brain sub-regions) are absorbed into shared components and do not contribute independent power.

## FOCUS Probabilistic Fine-Mapping

**Goal:** Resolve a locus with multiple co-significant TWAS genes into a probabilistic causal-gene credible set.

**Approach:** Build (or download) a FOCUS gene-prediction database matching the TWAS weight panel; run `focus finemap` with the TWAS sumstats and ancestry-matched LD reference; report PIPs and credible sets.

```bash
# Install: pip install pyfocus
# Pre-built FOCUS DBs for FUSION/PrediXcan weights live at github.com/bogdanlab/focus

# Convert FUSION TWAS output to FOCUS sumstat format if needed
# FOCUS expects: CHR SNP BP A1 A2 Z P from the underlying GWAS sumstats (NOT TWAS Z)

focus finemap \
    gwas.sumstats \
    1000G_EUR_chr \
    focus_gtex_v8_whole_blood.db \
    --p-threshold 5e-8 \
    --tissue Whole_Blood \
    --out gwas_focus_whole_blood
# Output: per-gene PIP, credible-set membership flag, and locus-level group probability
```

For a custom prediction-weight panel without a pre-built FOCUS DB, construct one from FUSION weights:

```bash
focus import custom_panel.pos fusion --tissue Whole_Blood --output custom_focus
```

FOCUS PIPs depend on the per-locus prior probability that any gene is causal. Report a sensitivity scan over `--prior-prob`:

| Setting | Use case |
|---------|----------|
| `--prior-prob 1e-3` (default) | Standard genome-wide TWAS; matches Mancuso 2019 |
| `--prior-prob 1e-4` (conservative) | High-prior gene-dense locus where most genes are not causal |
| `--prior-prob 1e-2` (liberal) | Pre-prioritised candidate region where one gene is expected |

Cite the Mancuso 2019 supplement for the sensitivity-scan protocol. MA-FOCUS extends with per-ancestry weights and is invoked via the same `focus finemap` CLI -- multi-ancestry mode is signaled by colon-separated per-ancestry sumstats, LD references, and weight DBs, plus paired ancestry codes in `--locations`:

```bash
focus finemap \
    eur.sumstats.tsv.gz:eas.sumstats.tsv.gz:afr.sumstats.tsv.gz \
    1000G_EUR_chr:1000G_EAS_chr:1000G_AFR_chr \
    focus_eur.db:focus_eas.db:focus_afr.db \
    --chr 22 --locations 38:EUR-EAS-AFR \
    --out gwas_ma_focus
```

MA-FOCUS assumes a shared causal gene across ancestries; gene-specific heterogeneity (e.g. an ancestry-specific eQTL) violates the assumption and produces inflated H0/heterogeneous-group probability.

## When Standard Pipeline is Insufficient

The FUSION / S-PrediXcan / S-MultiXcan + FOCUS pipeline is the default. Escalate to a specialised method only when the standard pipeline misses an expected hit (a strong GWAS signal with no TWAS gene, or a known causal gene without recovery).

| Method | Triggering scenario | Yield |
|--------|--------------------|-------|
| MOSTWAS (Bhattacharya 2021 PLoS Genet 17:e1009398) | Trans-mediator architecture suspected (immune, neuropsych traits) | ~15% additional hits via distal mediator terms |
| EpiXcan (Zhang 2019 Nat Commun 10:3834) | Paired epigenome data available (Roadmap, EpiMap, ENCODE cell-matched DNase/H3K27ac) | Higher prediction R^2 in epigenome-rich tissues |
| TIGAR-V2 (Parrish 2022 HGG Adv 3:100068) | Training a custom Bayesian DPR panel (no pre-trained PredictDB for the tissue) | Captures non-elastic-net effect structures |
| kTWAS (Cao 2021 Brief Bioinform 22:bbaa270) | Rare-variant or population-specific contexts; cis-eQTL panels under-powered | Kernel aggregation robust to non-linear and rare effects |

**Operational rule:** Default to FUSION / S-PrediXcan / S-MultiXcan + FOCUS first; document an expected-but-missing hit before escalating.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| FUSION significant + S-PrediXcan null | Different weight panels (FUSION vs PredictDB) or different LD references | Re-run with matched panel; check FUSION weight CV-R^2 vs PredictDB MASHR posterior mean |
| S-MultiXcan p << min per-tissue p | Joint test borrowing strength across tissues | Genuine; report the joint p and the top contributing tissue |
| Many co-significant genes at one locus, no FOCUS PIP > 0.5 | LD-tied co-regulated genes, true causal gene not in panel | Expand panel (add brain or tissue-specific weights); functional follow-up needed |
| FOCUS PIP > 0.8 + coloc PP.H4 < 0.5 | Sparse eQTL signal (single SNP drives prediction) + locus has another co-localising signal | Investigate the single top-eQTL SNP; check for fine-mapped credible-set overlap |
| TWAS hit + cis-eQTL MR null | TWAS hit is LD-tagged, not mediated by expression | Trust the cis-eQTL MR result; flag the gene as TWAS-positive but non-causal |
| MA-FOCUS PIP much lower than per-ancestry FOCUS | Cross-ancestry heterogeneity; gene effect is not shared | Report per-ancestry separately; do not pool |
| TWAS significant in wrong tissue | LD-induced via tissue-shared eQTL | Verify with LDSC-SEG tissue prioritisation; treat top-tissue TWAS hit as the trustworthy one |

**Operational rule:** No single-method TWAS result is sufficient evidence of causal gene identity. The minimum reporting standard is (a) TWAS significance threshold met with multiple-testing correction; (b) FOCUS PIP >= 0.8 OR coloc PP.H4 >= 0.7; (c) explicit acknowledgement of tissue choice and ancestry of prediction weights. Triangulation with cis-eQTL MR or independent CRISPR/MPRA validation lifts a finding from "candidate" to "supported".

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `Error: weight file <gene>.RDat not found` (FUSION) | weights.pos points to relative paths; `--weights_dir` not set correctly | Verify `--weights_dir` matches the .pos `WGT` column directory |
| `KeyError: 'SNP'` or `'A1'` (S-PrediXcan) | GWAS sumstat columns not mapped via `--snp_column` etc. | Pass `--snp_column SNP --effect_allele_column A1 --non_effect_allele_column A2 --beta_column BETA --pvalue_column P` explicitly |
| All TWAS Z's are 0 or NA | Allele coding mismatch between GWAS and weight panel | Harmonise (effect-allele flip); check `--keep_non_rsid` if using non-rsID SNPs |
| Genomic inflation lambda >> 1.05 | Wrong LD reference OR population structure not controlled in upstream GWAS | Fix at the GWAS stage; do not adjust TWAS lambda post-hoc |
| FOCUS reports PIP = 1 for one gene at every locus | Only one gene in panel at locus; degenerate posterior | Expand panel coverage or report locus as panel-limited |
| S-MultiXcan condition number warning | Tissues near-collinear (multiple brain regions) | Increase regularisation (`--regularization 0.5`) or restrict to tissue subset |
| FOCUS DB not matching FUSION weights | Custom weight panel without FOCUS DB | Build FOCUS DB from weights using `focus import <panel>.pos fusion` |
| MA-FOCUS H0 probability dominates | Cross-ancestry heterogeneity at the locus | Run per-ancestry FOCUS separately; do not force joint |
| S-PrediXcan output has effect sizes much larger than expected | `sdY` proxy mis-specified; standardised vs unstandardised mismatch | Confirm GWAS Z and beta scale; rerun with `--additional_output` |

## Required Reporting for Publication

A defensible TWAS report includes every item below in methods or supplement:

- GWAS sumstat source, effective N (Neff), and ancestry composition
- Weight panel and version (e.g. "GTEx v8 MASHR-EUR, PredictDB release 2022-01")
- LD reference panel and version (e.g. "1000 Genomes Phase 3 EUR" or "UK Biobank array")
- Per-tissue list (or explicit "all 49 GTEx v8 tissues")
- Multiple-testing correction strategy (S-MultiXcan joint, per-tissue Bonferroni, or per-tissue FDR)
- FOCUS PIP threshold and prior-probability sensitivity scan
- Coloc PP.H4 threshold (cross-reference causal-genomics/colocalization-analysis)
- cis-eQTL MR estimate, instrument F-statistic, and TwoSampleMR package version (cross-reference causal-genomics/mendelian-randomization)
- Triangulation rule (e.g. "3-of-4 concordance across TWAS, FOCUS, coloc, cis-MR")
- HLA exclusion confirmed (chr6:25-35 Mb dropped from genome-wide summaries)

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "LD-induced false positive at gene-dense locus?" | FOCUS PIP reported per gene; only PIP >= 0.8 carried forward as candidate causal |
| "Tissue mis-specification?" | Tissue Selection Protocol applied (sLDSC + CELLEX + MAGMA); cross-tissue S-MultiXcan reported for replication |
| "Why GTEx and not eQTLGen?" | Justified by trait biology: blood-relevant traits use eQTLGen (N ~ 31k); tissue-specific traits use GTEx v8 MASHR |
| "MHC?" | chr6:25-35 Mb excluded; HLA-TAPAS run separately for HLA-relevant traits |
| "Triangulation?" | TWAS + coloc + cis-MR + FOCUS run; 3-of-4 concordance required for the strong-candidate label |
| "Ancestry transfer?" | Ancestry-matched weights used where available; MA-FOCUS applied for multi-ancestry GWAS |
| "Prior sensitivity in FOCUS?" | `--prior-prob` scanned at 1e-2, 1e-3, 1e-4; PIPs reported across the scan |

## Tool Install Notes

- **FUSION**: gusevlab.org/projects/fusion or `git clone https://github.com/gusevlab/fusion_twas`. R scripts; needs plink (PLINK 1.9), Rscript, and the GBJ R package for omnibus. Pre-computed weights for GTEx v7/v8, CMC, YFS, METSIM, NTR, MESA at the same site.
- **MetaXcan / S-PrediXcan / S-MultiXcan**: `git clone https://github.com/hakyimlab/MetaXcan` (not on PyPI). Python scripts in `software/`. Compatible with Python 3.9-3.11.
- **PredictDB models**: predictdb.org. GTEx v8 elastic-net (single-tissue) and MASHR (cross-tissue posterior) databases for EUR; multi-ethnic panels emerging.
- **UTMOST**: `git clone https://github.com/Joker-Jerome/UTMOST`. Python. Needs precomputed cross-tissue weights or training pipeline.
- **FOCUS**: `pip install pyfocus`. CLI `focus`. Pre-built DBs for GTEx v7/v8 panels at github.com/bogdanlab/focus.
- **MA-FOCUS**: `git clone https://github.com/mancusolab/ma-focus && cd ma-focus && pip install .` (no PyPI release; install from source). Same CLI as single-ancestry FOCUS -- `focus finemap` -- with colon-separated per-ancestry sumstats / LD / weight DBs and paired ancestry codes in `--locations`.
- **TIGAR-V2**: `git clone https://github.com/yanglab-emory/TIGAR`. Python + R hybrid; ships with example data.
- **MOSTWAS**: `git clone https://github.com/bhattacharya-a-bt/MOSTWAS`. R package; install via `devtools::install_github`.
- **EpiXcan**: Bitbucket roussoslab/epixcan. Workflow-style pipeline.

## References

- Gamazon ER, Wheeler HE, Shah KP, Mozaffari SV, Aquino-Michaels K et al 2015 Nat Genet 47:1091 (PrediXcan)
- Gusev A, Ko A, Shi H, Bhatia G, Chung W et al 2016 Nat Genet 48:245 (FUSION TWAS)
- Barbeira AN, Dickinson SP, Bonazzola R, Zheng J, Wheeler HE et al 2018 Nat Commun 9:1825 (S-PrediXcan)
- Barbeira AN, Pividori M, Zheng J, Wheeler HE, Nicolae DL et al 2019 PLoS Genet 15:e1007889 (S-MultiXcan)
- Hu Y, Li M, Lu Q, Weng H, Wang J et al 2019 Nat Genet 51:568 (UTMOST cross-tissue)
- Mancuso N, Freund MK, Johnson R, Shi H, Kichaev G et al 2019 Nat Genet 51:675 (FOCUS gene-level fine-mapping)
- Lu Z, Gopalan S, Yuan D, Conti DV, Pasaniuc B, Gusev A, Mancuso N 2022 AJHG 109:1388-1404 (MA-FOCUS multi-ancestry)
- Wainberg M, Sinnott-Armstrong N, Mancuso N, Barbeira AN, Knowles DA et al 2019 Nat Genet 51:592 (TWAS limitations and LD-induced false positives)
- Bhattacharya A, Li Y, Love MI 2021 PLoS Genet 17:e1009398 (MOSTWAS distal mediation)
- Cao C, Kwok D, Edie S, Li Q, Ding B et al 2021 Brief Bioinform 22:bbaa270 (kTWAS)
- Zhang W, Voloudakis G, Rajagopal VM, Readhead B, Dudley JT et al 2019 Nat Commun 10:3834 (EpiXcan)
- Parrish RL, Gibson GC, Epstein MP, Yang J 2022 HGG Adv 3:100068 (TIGAR-V2)
- Vosa U, Claringbould A, Westra HJ, Bonder MJ, Deelen P et al 2021 Nat Genet 53:1300 (eQTLGen reference)
- GTEx Consortium 2020 Science 369:1318 (GTEx v8 multi-tissue eQTL)
- Mountjoy E, Schmidt EM, Carmona M, Schwartzentruber J, Peat G et al 2021 Nat Genet 53:1527 (Open Targets Genetics)
- Mogil LS, Andaleon A, Badalamenti A, Dickinson SP, Guo X et al 2018 PLoS Genet 14:e1007586 (MESA multi-ethnic eQTL)
- Patel RA, Musharoff SA, Spence JP, Pimentel H, Tcheandjieu C et al 2022 AJHG 109:1286 (TWAS ancestry transfer)
- Yazar S, Alquicira-Hernandez J, Wing K, Senabouth A, Gordon MG et al 2022 Science 376:eabf3041 (OneK1K sc-eQTL)

## Related Skills

- causal-genomics/fine-mapping - Variant-level credible sets feeding FOCUS gene-level fine-mapping
- causal-genomics/colocalization-analysis - Coloc PP.H4 triangulation with TWAS hits
- causal-genomics/mendelian-randomization - cis-eQTL MR triangulation; drug-target prioritisation
- causal-genomics/effector-gene-prioritization - Downstream gene mapping from TWAS candidate sets
- causal-genomics/proteome-mr-drug-target - Drug-target triangulation using protein-level evidence
- causal-genomics/pleiotropy-detection - Distinguishing horizontal pleiotropy from mediated TWAS signal
- causal-genomics/mediation-analysis - Downstream gene-mediated trait effects given TWAS hits
- population-genetics/association-testing - Upstream GWAS summary statistic generation
- population-genetics/linkage-disequilibrium - LD reference panel construction for FUSION / FOCUS
- differential-expression/deseq2-basics - Generating eQTL count data for custom prediction-weight training
- single-cell/preprocessing - Cell-type-resolved eQTL panels for sc-TWAS
- workflows/gwas-pipeline - End-to-end GWAS pipeline producing TWAS input
- variant-calling/variant-annotation - Functional annotation of TWAS / FOCUS top variants
<!-- END FILE: causal-genomics/transcriptome-wide-association/SKILL.md -->

<!-- END CATEGORY: causal-genomics -->

