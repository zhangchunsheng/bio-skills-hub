---
slug: bio-methylation-analysis-integrated
version: 1.0.1
displayName: "甲基化分析 / DNA methylation analysis"
name: bio-methylation-analysis-integrated
summary: "中文：甲基化分析综合技能，整合 10 个相关专题，覆盖DNA甲基化分析：Bisulfite测序与Infinium芯片数据处理、CpG差异甲基化、DMR检测、表观遗传时钟。 English: Integrated DNA methylation analysis skill covering 10 related topics, including DNA methylation analysis: bisulfite sequencing and Infinium array processing, CpG differential methylation, DMR detection, epigenetic clocks."
description: "中文：这是一个面向甲基化分析的综合生物信息学 Skill，整合当前分类下 10 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：DNA甲基化分析：Bisulfite测序与Infinium芯片数据处理、CpG差异甲基化、DMR检测、表观遗传时钟。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Bismark, EpiDISH, dmrseq。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for DNA methylation analysis, combining 10 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers DNA methylation analysis: bisulfite sequencing and Infinium array processing, CpG differential methylation, DMR detection, epigenetic clocks. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Bismark, EpiDISH, dmrseq. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# methylation-analysis 分类 Skill 整合版

> 本文件整合同一主分类目录下 10 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: methylation-analysis -->

## 子目录：methylation-analysis/array-preprocessing

<!-- BEGIN FILE: methylation-analysis/array-preprocessing/SKILL.md -->
---
name: bio-methylation-array-preprocessing
description: Turns raw Illumina Infinium methylation BeadChip IDATs (450K, EPIC, EPICv2) into a defensible beta/M matrix with sesame (openSesame/SigDF) or minfi (RGChannelSet -> MethylSet -> GenomicRatioSet). Covers Type I vs Type II probe chemistry and why raw Type II beta is compressed, the signal-to-beta math (beta = M/(M+U+100)) and M-value logit, detection-p / pOOBAH masking including the out-of-band deletion-artifact catch, dye-bias correction, and the normalization decision (noob, funnorm, quantile, SWAN, BMIQ, dasen, sesame QCDPB). Use when reading IDATs, choosing a normalization for a 450K/EPIC/EPICv2 cohort, deciding beta vs M, masking failed probes, or producing the corrected matrix before testing. For probe/sample filtering, EPICv2 replicate collapse, and sample-identity QC see array-qc-filtering; for native long-read 5mC see long-read-sequencing/nanopore-methylation (a different platform).
tool_type: r
primary_tool: sesame
---

## Version Compatibility

Reference examples tested with: sesame 1.20+, minfi 1.48+, ChAMP 2.32+, wateRmelon 2.8+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The ARRAY VERSION and GENOME BUILD are versions that matter as much as the package. EPICv2 REQUIRES sesame (mainstream minfi does not auto-detect it and returns "Unknown"); the manifest/annotation packages are array-version- and genome-build-specific (450K and EPICv1 are hg19; EPICv2 is hg38-native). sesame pulls platform/address data from its own hub, so `sesameDataCache()` must run once before processing. Record the array (450K/EPIC/EPICv2) and the genome build in any output, the way a sequencing run records its reference.

# Array Preprocessing

**"Give me a clean methylation matrix from my IDATs"** -> Read the raw two-channel intensities, correct the Type I/II design mismatch, dye/background bias, and failed probes, then emit beta (for reporting) and M (for testing) - because an Infinium beta is a two-chemistry fluorescence ratio, not a methylation value, until those corrections are applied.
- R: `openSesame(idat_dir, prep='QCDPB', func=getBetas)` (sesame) or `preprocessFunnorm(rgSet)` (minfi)

Scope: IDAT -> corrected, masked, normalized beta/M matrix for one array version. Probe filtering (cross-reactive/SNP/sex), EPICv2 replicate collapse, and sample-identity QC -> array-qc-filtering. Per-CpG testing -> differential-cpg-testing. Region calling -> dmr-detection. Native long-read 5mC -> long-read-sequencing/nanopore-methylation. Bisulfite-sequencing (Bismark/WGBS/RRBS) is the other modality in this category, not this skill.

## The Single Most Important Modern Insight -- An Infinium Beta Value Is a Two-Chemistry Fluorescence Ratio, Not a Methylation Measurement

An Infinium array does not measure methylation - it measures the relative fluorescence of a methylated vs unmethylated allele at a fixed, manufacturer-chosen set of CpGs, glued together from two incompatible chemistries. A raw beta becomes a comparable methylation estimate only after preprocessing; preprocessing IS the measurement, not optional cleanup. Three corollaries every misuse violates:

1. **The manifest is the experiment.** The array interrogates <3% of human CpGs, and a DIFFERENT <3% across 450K (~485K), EPIC (~865K), and EPICv2 (~935K). "Absent" almost always means "not on this array," and a 450K-trained clock or EWAS does not transfer to EPICv2 without intersecting probe sets. Do not start from a supplied beta matrix when IDATs exist - the raw two-channel intensities, control probes, and out-of-band signal that noob/funnorm/pOOBAH need are already gone.
2. **Type I and Type II betas disagree by design.** Type II probes (one bead, two dyes) have a narrower dynamic range and dye-incorporation bias, so raw Type II betas are compressed toward 0.5 relative to Type I (two beads, one channel). Mixing the two chemistries without a design correction (BMIQ/SWAN/sesame matchDesign) injects a probe-type artifact that can exceed the biological effect. The diagnostic is a per-type beta-density plot showing two mismatched peaks.
3. **Raw beta is uninterpretable until detection-masked.** Failed probes - low signal, germline/somatic deletions, cross-reactive, SNP-hit - return confident-looking betas that are pure noise. pOOBAH / detection-p masking is what separates a number from a measurement of nothing; pOOBAH additionally catches deletion-driven false-intermediate methylation that negative-control detection-p misses.

Organize the work around DELIVERING a defensible matrix (read -> correct -> mask -> normalize), not around listing minfi functions.

## Three Modalities of the Same Biology

DNA methylation is measured three ways, each with different tradeoffs - state which one the data is before choosing tools:

| Modality | Readout | Coverage | Cohort-comparability | This skill |
|----------|---------|----------|----------------------|------------|
| Infinium array (450K/EPIC/EPICv2) | intensity ratio, no depth | fixed <3% of CpGs, regulatory-enriched | high (shared manifest, no alignment) | YES |
| WGBS / RRBS bisulfite | count ratio, depth-gated | genome-wide (WGBS) or enriched (RRBS) | needs alignment + matched genome | -> bismark-alignment, methylkit-analysis |
| Long-read native (ONT/PacBio) | per-molecule modification calls | genome-wide, phased | growing | -> long-read-sequencing/nanopore-methylation |

Arrays dominate human epigenetic epidemiology (essentially every published clock and large EWAS is array-based) because cost is a fraction of WGBS and the fixed manifest makes cohorts directly comparable.

## Object Models (do not start from a beta matrix)

The raw output per sample is a pair of binary IDATs (`_Grn.idat`, `_Red.idat`); background, dye, and detection-p correction REQUIRE these plus the control probes.

- **minfi:** `RGChannelSet` (raw red/green) -> a `preprocess*` step -> `MethylSet` (M/U intensities) -> `RatioSet` (beta/M) -> `GenomicRatioSet` (genome-mapped). `read.metharray.exp()` reads IDATs; `getBeta()`, `getM()`, `getCN()` extract values.
- **sesame:** a `SigDF` (one signal data.frame per sample). `readIDATpair()` reads one sample; `openSesame()` drives the whole pipeline across a directory and returns a betas matrix directly.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| sesame | Zhou 2018 *Nucleic Acids Res* 46:e123 | SigDF; openSesame QCDPB; pOOBAH OOB masking; EPICv2-native | EPICv2; best detection masking; the modern default |
| minfi | Aryee 2014 *Bioinformatics* 30:1363 | RGChannelSet->GenomicRatioSet; noob/funnorm/quantile/SWAN | 450K/EPICv1; large downstream ecosystem (DMRcate, conumee) |
| ChAMP | Tian 2017 *Bioinformatics* 33:3982 | end-to-end pipeline; BMIQ default | one-call newcomer pipeline on 450K/EPICv1 |
| wateRmelon | Pidsley 2013 *BMC Genomics* 14:293 | dasen/nasen + metric-driven normalization eval | dasen default; normalization benchmarking |

## Normalization Decision Tree by Scenario

Separate the two correction layers that get conflated: (a) background + dye bias (within-sample): noob, sesame dyeBias, dasen background step; (b) Type I/II design correction + between-array harmonization: SWAN, BMIQ, quantile, funnorm, dasen quantile step. A complete pipeline does both.

| Scenario | Recommended | Why |
|----------|-------------|-----|
| EPICv2 (any design) | sesame `openSesame(prep='QCDPB')` | EPICv2-native; pOOBAH; minfi mis-handles duplicate IDs |
| Cancer / cross-tissue (global differences expected) | minfi `preprocessFunnorm` (noob + control-PCs) | preserves real global shifts; quantile would erase them |
| Subtle blood EWAS (no global difference expected) | `preprocessQuantile` or wateRmelon `dasen` | marginal distributions assumed equal; safe to harmonize |
| Strong Type I/II design correction wanted | BMIQ (Teschendorff 2013) or SWAN (Maksimovic 2012) | dilate Type II onto the Type I distribution; pair with a between-array step |
| Single-sample / clinical / streaming | ssNoob or per-IDAT openSesame | reproducible without re-normalizing the cohort |
| Probe/sample filtering, EPICv2 collapse, identity | -> array-qc-filtering | this skill stops at the corrected matrix |
| Per-CpG testing on the matrix | -> differential-cpg-testing | test on M-values; report delta-beta |

There is no universally best normalization (Pidsley 2013 favored dasen; Fortin 2014 favored funnorm for global-difference studies; Welsh 2023 ranked a sesame/pOOBAH pipeline best and quantile worst on EPIC replicate-concordance). Key the choice on array version + whether global differences are expected + single-sample vs cohort, and verify against current benchmarks rather than hard-coding one method.

## Signal -> Beta -> M

- **Beta:** `beta = M / (M + U + alpha)`, M = methylated-allele intensity, U = unmethylated, `alpha = 100` (minfi default) stabilizes the ratio when both intensities are near zero. beta in [0,1] is interpretable but HETEROSCEDASTIC (variance collapses near 0 and 1), violating the constant-variance assumption of linear models.
- **M-value:** `M = log2((M_int + alpha) / (U_int + alpha))`, the logit of beta. Approximately homoscedastic; the correct scale for limma/t-tests (Du 2010 *BMC Bioinformatics* 11:587). Rule: test on M-values, report delta-beta for effect size - the same rule as bisulfite sequencing.

## Process IDATs with sesame (the EPICv2-safe default)

**Goal:** Produce a corrected, detection-masked betas matrix from a directory of IDAT pairs without manually juggling manifest packages.

**Approach:** Cache the sesame data hub once, then run openSesame with the default `QCDPB` prep (qualityMask, inferInfiniumIChannel, dyeBiasNL, pOOBAH, noob, in that order), which auto-detects the platform and returns betas; pOOBAH writes NA into failed probes in place.

```r
library(sesame)
sesameDataCache()                          # once per machine; pulls platform/address data
betas <- openSesame('idat_dir', prep = 'QCDPB', func = getBetas)
# prep codes: Q qualityMask  C inferInfiniumIChannel  D dyeBiasNL  P pOOBAH  B noob
# pOOBAH masks (sets NA) probes whose out-of-band signal is indistinguishable from background,
# catching deletion-driven false-intermediate methylation that negative-control detection-p misses
mvals <- log2(betas / (1 - betas))         # M-values for statistical testing (logit of beta)
```

For EPICv2, openSesame detects the platform automatically; the replicate-probe collapse (`betasCollapseToPfx`) belongs to the next stage and is documented in array-qc-filtering.

## Process IDATs with minfi (450K / EPICv1)

**Goal:** Build a normalized GenomicRatioSet and extract beta and M, choosing the normalization by whether global methylation differences are expected.

**Approach:** Read IDATs into an RGChannelSet, compute a detection-p mask before normalizing, then apply funnorm (global differences) or quantile (no global differences); extract beta and M with the offset-100 defaults.

```r
library(minfi)
rgSet <- read.metharray.exp(base = 'idat_dir')
detP <- detectionP(rgSet)                   # neg-control-based; pre-normalization probe-failure map

grSet <- preprocessFunnorm(rgSet, nPCs = 2) # noob first, then 2 control-probe PCs; preserves global shifts
# preprocessQuantile(rgSet) instead when NO global difference is expected (subtle blood EWAS)

beta <- getBeta(grSet)                       # GenomicRatioSet holds precomputed betas (offset applied upstream)
mval <- getM(grSet)                          # log2(beta/(1-beta)) on the ratio set
beta[detP[rownames(beta), colnames(beta)] > 0.01] <- NA   # mask probes failing detection-p (0.01)
```

EPICv2 is NOT handled by mainstream minfi (it returns "Unknown" and duplicates probe IDs); use sesame for EPICv2.

## Per-Method Failure Modes

### Starting from a supplied beta matrix
**Trigger:** processing begins from a `.csv`/`.RData` beta matrix instead of IDATs. **Mechanism:** a beta matrix has discarded the raw two-channel intensities, control probes, and out-of-band signal. **Symptom:** noob/funnorm/pOOBAH/dye correction cannot run; detection-p cannot be recomputed. **Fix:** obtain the raw IDAT pairs; treat a beta matrix as a last resort and document that preprocessing could not be applied.

### Type I/II mismatch left in the data
**Trigger:** testing on raw or only background-corrected betas. **Mechanism:** Type II betas are compressed toward 0.5 relative to Type I. **Symptom:** "differential" probes that are design artifacts; a two-peak per-type beta density. **Fix:** apply BMIQ/SWAN or sesame matchDesign (or use openSesame, which corrects channel/dye) before testing; confirm the two per-type peaks align.

### minfi on EPICv2
**Trigger:** `read.metharray.exp` on EPICv2 IDATs with mainstream minfi. **Mechanism:** EPICv2 is not auto-detected; 5,483 loci carry duplicate IDs. **Symptom:** array reads as "Unknown"; `getBeta()` returns repeated rownames so `match()`-based merges silently misbehave. **Fix:** use sesame (EPICv2-native), or install a third-party EPICv2 manifest/anno, tag the annotation manually, and collapse replicates in array-qc-filtering.

### Quantile-normalizing a global-difference contrast
**Trigger:** `preprocessQuantile` on cancer vs normal or cross-tissue data. **Mechanism:** between-array quantile assumes equal marginal beta distributions. **Symptom:** real global hypomethylation flattened away. **Fix:** use funnorm (control-probe PCs preserve global shifts); reserve quantile/dasen for subtle no-global-difference designs.

### Testing on beta instead of M
**Trigger:** limma/t-tests run directly on beta. **Mechanism:** beta is heteroscedastic (variance collapses near 0 and 1). **Symptom:** miscalibrated variance; inflated or deflated p-values at extreme methylation. **Fix:** test on M-values, report delta-beta for effect size.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| beta offset `alpha = 100` | Aryee 2014; minfi default | stabilizes the ratio when M and U are both near zero |
| detection-p `> 0.01` = failed | minfi convention | signal indistinguishable from background; beta is noise |
| pOOBAH default p ~ 0.05 | Zhou 2018 | OOB-based mask; also catches deletion-driven false intermediate methylation |
| funnorm `nPCs = 2` | Fortin 2014 | first 2 control-probe PCs absorb technical variation without erasing biology |
| Test on M-values, report delta-beta | Du 2010 | M is homoscedastic for modeling; beta is interpretable for effect size |
| sesame prep `QCDPB` (ordered) | Zhou 2018 | Q quality, C channel, D dye, P pOOBAH, B noob - the validated default order |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Array reads as "Unknown" | EPICv2 in mainstream minfi | use sesame; or third-party manifest + manual annotation tag |
| `getBeta()` has repeated rownames | EPICv2 duplicate probe IDs | collapse replicates (array-qc-filtering); do not merge by ID first |
| Two-peak beta density per probe type | Type I/II design bias uncorrected | BMIQ/SWAN/openSesame before testing |
| Global signal vanished after normalization | quantile applied to a global-difference study | use funnorm |
| `sesameDataCache` / platform-not-found | hub not cached | run `sesameDataCache()` once before processing |
| Coordinates misalign merging EPICv2 with 450K | EPICv2 is hg38, 450K/EPICv1 hg19 | track build per array; liftover before merging (array-qc-filtering) |

## References

- Aryee MJ, Jaffe AE, Corrada-Bravo H, et al. 2014. Minfi: a flexible and comprehensive Bioconductor package for the analysis of Infinium DNA methylation microarrays. *Bioinformatics* 30:1363-1369.
- Zhou W, Triche TJ Jr, Laird PW, Shen H. 2018. SeSAMe: reducing artifactual detection of DNA methylation by Infinium BeadChips in genomic deletions. *Nucleic Acids Res* 46:e123.
- Triche TJ Jr, Weisenberger DJ, Van Den Berg D, Laird PW, Siegmund KD. 2013. Low-level processing of Illumina Infinium DNA methylation BeadArrays. *Nucleic Acids Res* 41:e90.
- Fortin JP, Labbe A, Lemire M, et al. 2014. Functional normalization of 450k methylation array data improves replication in large cancer studies. *Genome Biol* 15:503.
- Maksimovic J, Gordon L, Oshlack A. 2012. SWAN: subset-quantile within array normalization for Illumina Infinium HumanMethylation450 BeadChips. *Genome Biol* 13:R44.
- Teschendorff AE, Marabita F, Lechner M, et al. 2013. A beta-mixture quantile normalization method for correcting probe design bias in Illumina Infinium 450k DNA methylation data. *Bioinformatics* 29:189-196.
- Pidsley R, Wong CCY, Volta M, Lunnon K, Mill J, Schalkwyk LC. 2013. A data-driven approach to preprocessing Illumina 450K methylation array data. *BMC Genomics* 14:293.
- Du P, Zhang X, Huang CC, et al. 2010. Comparison of Beta-value and M-value methods for quantifying methylation levels by microarray analysis. *BMC Bioinformatics* 11:587.
- Tian Y, Morris TJ, Webster AP, et al. 2017. ChAMP: updated methylation analysis pipeline for Illumina BeadChips. *Bioinformatics* 33:3982-3984.
- Kaur D, Lee SM, Goldberg D, et al. 2023. Comprehensive evaluation of the Infinium human MethylationEPIC v2 BeadChip. *Epigenetics Commun* 3:6.

## Related Skills

- array-qc-filtering - Probe and sample QC/filtering downstream of preprocessing
- differential-cpg-testing - Per-CpG testing on the resulting beta/M matrix
- dmr-detection - DMRcate array-mode region calling
- cell-type-deconvolution - Consumes the clean beta matrix
- epigenetic-clocks - Consumes the clean beta matrix
- ewas-design - Study design, batch, and inference layer
- long-read-sequencing/nanopore-methylation - Native long-read methylation (different platform)
- workflows/methylation-pipeline - End-to-end pipeline
<!-- END FILE: methylation-analysis/array-preprocessing/SKILL.md -->

## 子目录：methylation-analysis/array-qc-filtering

<!-- BEGIN FILE: methylation-analysis/array-qc-filtering/SKILL.md -->
---
name: bio-methylation-array-qc-filtering
description: Performs probe filtering and sample-level QC on Illumina Infinium methylation arrays (450K / EPIC / EPICv2) to decide which probes and samples to trust. Drops detection-p-failed and low-bead-count probes, removes cross-reactive/non-specific probes (Chen 2013 / Pidsley 2016 lists via maxprobes), excludes SNP-overlapping probes with dropLociWithSnps, and handles sex-chromosome probes. Collapses EPICv2 replicate probes with betasCollapseToPfx and harmonizes across array versions (EPICv2 hg38 vs 450K/EPIC hg19, intersect plus mLiftOver). Runs sample-identity QC: getSex sex prediction vs sample sheet for swap detection, rs-SNP fingerprint clustering for duplicates/swaps, and Sentrix chip/array-position batch diagnosis. Use when filtering methylation array probes, detecting sample swaps or mislabels, collapsing EPICv2 replicates, or merging 450K/EPIC/EPICv2 cohorts. For IDAT-to-corrected-beta normalization see array-preprocessing; for batch correction and study design see ewas-design.
tool_type: r
primary_tool: minfi
---

## Version Compatibility

Reference examples tested with: minfi 1.48+, sesame 1.20+, maxprobes 0.0.2+, ChAMP 2.32+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The ARRAY VERSION is the version that matters most here. Cross-reactive probe lists, SNP-overlap annotation, the manifest, and the genome build are all array-version-specific. Record whether the data is 450K (hg19), EPIC v1 (hg19), or EPIC v2 (hg38), and which annotation package supplies the probe metadata (`IlluminaHumanMethylation450kanno.ilmn12.hg19`, `...EPICanno.ilm10b4.hg19`, `...EPICv2anno.20a1.hg38`). EPICv2 carries ~5,100 replicate probes (2-10 designs per locus) and is hg38-native; both facts break naive cross-version merges if ignored.

# Array QC and Filtering

**"Which probes and samples can I trust on my methylation array?"** -> Mask the failed/cross-reactive/SNP-overlapping probes, collapse EPICv2 replicates, and check every sample's predicted sex and rs-SNP fingerprint against the sample sheet - because a raw array beta is uninterpretable until it is detection-masked and probe-filtered, and a sample swap is the failure no downstream model can rescue.
- R: `dropLociWithSnps(gset, snps=c('CpG','SBE'), maf=0)` then `getSex()` and `getSnpBeta()` for identity QC

Scope: probe filtering + sample-level QC + EPICv2 replicate collapse + cross-version harmonization for Infinium arrays. IDAT reading, background/dye correction, detection-p masking, and normalization -> array-preprocessing (it produces the matrix QC'd here). Explicit chip/position batch CORRECTION and study design -> ewas-design. Per-CpG testing on the filtered matrix -> differential-cpg-testing. Cohort cell-composition QC -> cell-type-deconvolution. Short-read bisulfite or long-read MM/ML calling are different modalities (see the bisulfite skills and long-read-sequencing/nanopore-methylation).

## The Single Most Important Modern Insight -- A Raw Array Beta Is Uninterpretable Until Detection-Masked and Probe-Filtered, and a Sample Swap Is the Failure Nothing Downstream Can Rescue

A beta value of 0.5 from a failed probe, a cross-reactive probe, or a SNP-overlapping probe looks exactly like a real intermediate methylation call - confident, reproducible, and wrong. Deciding which probes and samples to TRUST is the measurement's integrity layer, not optional cleanup. Three corollaries every misuse violates:

1. **A confident beta can be pure noise or pure genotype.** A detection-p-failed probe returns a number with no signal behind it. A cross-reactive probe sums fluorescence from multiple genomic locations. A CpG-SNP or SBE-SNP probe reports the donor's GENOTYPE, not methylation - producing reproducible-but-genetic "associations." None of these are visible in the beta value itself.
2. **The most common and most embarrassing failure is a sample swap or chip-confounded batch.** A `getSex()` prediction that disagrees with the sample sheet, or rs-SNP fingerprints that cluster two "different" samples together, reveals a mislabel that no model corrects after the fact. If Sentrix chip or array-position is confounded with the biological group, the technical and biological signals are mathematically inseparable - randomize at design (-> ewas-design), do not try to rescue it.
3. **Merging across array versions silently misaligns loci.** EPICv2 measures ~5,100 loci with 2-10 replicate probes and is annotated on hg38; 450K/EPIC are hg19 and have unique probe IDs. Collapse replicates and intersect/liftover BEFORE merging, or the same locus is counted multiple times (inflating its weight and breaking per-CpG FDR) and coordinates clash across builds.

Organize the work around delivering a trustworthy, merge-safe matrix: filter probes, collapse replicates, verify sample identity. Over-filtering is its own error - dropping every flagged probe discards real signal, so the maf cutoff and the cross-reactive list are calibrated decisions, not a fixed recipe.

## Filtering Taxonomy

| Filter | Tool / function | Citation | What it removes |
|--------|-----------------|----------|-----------------|
| Failed detection-p | `detectionP()` (minfi) / `pOOBAH` (sesame) | Aryee 2014 *Bioinformatics* 30:1363; Zhou 2018 *NAR* 46:e123 | probes with signal indistinguishable from background (per applied in array-preprocessing) |
| Low bead count | `getNBeads()` (minfi) / sesame bead data | Aryee 2014 *Bioinformatics* 30:1363 | probes built from too few beads (<3), unreliable |
| Cross-reactive / non-specific | `dropXreactiveLoci()` / `xreactive_probes()` (maxprobes) | Chen 2013 *Epigenetics* 8:203; Pidsley 2016 *Genome Biol* 17:208 | probes co-hybridizing to multiple loci; list is ARRAY-VERSION-specific |
| SNP-overlapping | `dropLociWithSnps()`, `getSnpInfo()` (minfi) | Aryee 2014 *Bioinformatics* 30:1363 | CpG-SNP / SBE-SNP probes that report genotype not methylation |
| Sex-chromosome | annotation `chr` (minfi) | Aryee 2014 *Bioinformatics* 30:1363 | chrX/chrY probes (sex-confounded; drop or sex-stratify) |
| EPICv2 replicates | `betasCollapseToPfx()` (sesame) | Kaur 2023 *Epigenetics Commun* 3:6 | extra designs per locus; collapse to one value per cg core ID |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| 450K cohort, EWAS-grade filter | maxprobes 450K list + `dropLociWithSnps` + drop chrX/Y | Chen 2013 list is 450K-specific; standard EWAS attrition |
| EPIC v1 cohort | maxprobes EPIC list + `dropLociWithSnps` + sex-chr decision | Pidsley 2016 list is EPIC-specific; do not reuse the 450K list |
| EPIC v2 cohort | sesame `betasCollapseToPfx` FIRST, then filter on hg38 anno | collapse replicates before any per-locus filter or FDR |
| Sex is the phenotype | keep chrX/chrY, analyze sex-stratified | dropping sex probes throws away the signal of interest |
| Suspected mislabels / replicates | `getSex()` vs sheet + `getSnpBeta()` rs-fingerprint clustering | swaps and duplicates are invisible in methylation alone |
| Merge 450K + EPIC + EPICv2 | intersect probe IDs after collapse; `mLiftOver` for coordinates | EPICv2 is hg38, others hg19; counts/coords clash otherwise |
| Chip/position confounded with group | -> ewas-design | unrecoverable by filtering; a design problem |
| Need the corrected matrix to filter | -> array-preprocessing | this skill QC's a matrix it does not produce |

## Probe Filtering on a GenomicRatioSet

**Goal:** Reduce a corrected `GenomicRatioSet` to the probes whose beta values reflect methylation rather than noise, genotype, or cross-hybridization.

**Approach:** Drop SNP-overlapping probes with minfi, remove the array-version-matched cross-reactive list with maxprobes, optionally drop sex-chromosome probes, and record the attrition at each step for the methods section.

```r
library(minfi)
library(maxprobes)

# gset is a corrected GenomicRatioSet from array-preprocessing (IDAT -> noob/funnorm -> ratios)
start_n <- nrow(gset)

# SNP at the CpG interrogation or single-base-extension site reports genotype, not methylation.
# maf=0 drops ANY annotated SNP (conservative EWAS default); raise maf to keep rare variants.
gset <- dropLociWithSnps(gset, snps = c('CpG', 'SBE'), maf = 0)

# Cross-reactive list is ARRAY-VERSION-specific: 'EPIC' (Pidsley 2016) vs '450K' (Chen 2013).
gset <- maxprobes::dropXreactiveLoci(gset)

# Sex-chromosome probes are sex-confounded; drop for autosomal EWAS or analyze sex-stratified.
anno <- getAnnotation(gset)
autosomal <- !(anno$chr %in% c('chrX', 'chrY'))
gset <- gset[autosomal, ]

attrition <- c(start = start_n, after_snp_xreact_sex = nrow(gset))
attrition
```

## Detection-p and Low-Bead Masking (boundary with array-preprocessing)

Per-probe detection-p and low-bead masking depend on the raw two-channel signal and control probes, which only exist at the `RGChannelSet`/`SigDF` stage handled in array-preprocessing. That skill applies `detectionP()` (minfi) or `pOOBAH` (sesame, which also catches deletion-driven false-intermediate calls) and `getNBeads()` before producing the corrected matrix. This skill assumes that masking is already done; if a supplied beta matrix has NOT been detection-masked, route back to array-preprocessing rather than trusting the betas. The thresholds (detection-p, fraction-of-samples-failed) live with the masking step, not here.

## EPICv2 Replicate Collapse

**Goal:** Reduce EPICv2's multiple probe designs per locus to one value per legacy CpG before any per-CpG analysis or cross-version merge.

**Approach:** Collapse replicate betas by probe-ID prefix with sesame, choosing mean (default) or the minimum-detection-p replicate, which also strips the design suffix so IDs revert to the classic cg form.

```r
library(sesame)

# EPICv2 IDs carry a design/replicate suffix (e.g. cg00000029_TC21); ~5,100 loci have 2-10 designs.
# Leaving replicates uncollapsed counts a locus multiple times: inflates its weight, makes
# correlated duplicate "tests" break per-CpG FDR, and corrupts any cross-version merge.
betas_collapsed <- betasCollapseToPfx(betas_epicv2)   # averages the replicate designs to one value per cg core ID

# betasCollapseToPfx only AVERAGES (it takes betas and nothing else). To keep the best-detection
# replicate instead, request collapse at the SigDF stage from the IDATs (a beta matrix has already
# discarded the per-probe detection p that minPval needs):
# betas <- openSesame(idat_prefixes, func = getBetas, collapseToPfx = TRUE, collapseMethod = 'minPval')
```

## Cross-Version Harmonization

**Goal:** Merge 450K, EPIC, and EPICv2 cohorts (or apply a 450K-trained clock/EWAS signature to EPICv2) without double-counting loci or clashing genome builds.

**Approach:** Collapse EPICv2 replicates first, intersect on the shared cg core IDs, then liftover coordinates because EPICv2 is hg38 while 450K/EPIC are hg19.

```r
library(sesame)

# 1. Collapse EPICv2 to cg core IDs (above), then intersect probe sets across versions.
shared <- Reduce(intersect, list(rownames(betas_450k), rownames(betas_epic), rownames(betas_collapsed)))

# 2. Coordinates differ by build: EPICv2 is hg38, 450K/EPIC are hg19. mLiftOver harmonizes
#    probe-level data across platforms/builds; intersect IDs first, lift coordinates before merging.
# betas_v2_hg19 <- mLiftOver(betas_collapsed, target_platform = 'HM450')

merged <- cbind(betas_450k[shared, ], betas_epic[shared, ], betas_collapsed[shared, ])
dim(merged)   # a 450K-trained clock/EWAS does not transfer to EPICv2 without this intersection
```

## Sample-Level Identity QC

**Goal:** Catch sample swaps, mislabels, and unintended duplicates before any analysis - the single most common data-integrity failure.

**Approach:** Predict sex from chrX/chrY intensity and compare to the sample sheet, then cluster samples on the rs-SNP genotyping probes (65 on 450K, ~59 on EPIC) to find duplicates and swaps independent of methylation.

```r
library(minfi)

# Sex from log2(median chrY intensity) - log2(median chrX intensity); two clusters = M/F.
# A predicted sex that disagrees with the sample sheet is the canonical sample-swap flag.
predicted <- getSex(gmset)              # gmset = mapped MethylSet/GenomicMethylSet
mismatch <- predicted$predictedSex != sample_sheet$Sex
sample_sheet$Basename[mismatch]

# rs-SNP fingerprint: ~59 explicit rs genotyping probes. Clustering on these betas (each ~0/0.5/1)
# reveals duplicate individuals and swaps regardless of methylation - genotype is identity.
snp_betas <- getSnpBeta(rgset)          # rgset = the raw RGChannelSet from array-preprocessing
identity_clusters <- hclust(dist(t(snp_betas)))
plot(identity_clusters)                 # technical replicates of one person cluster tightly
```

## Chip / Array-Position Batch Diagnosis

Sentrix chip (BeadChip barcode) and array position (`Sentrix_Position`, the row/column on the chip) are the dominant technical axes in Infinium data. This skill DIAGNOSES whether they associate with top variance components; it does NOT correct them. ChAMP's `champ.SVD()` regresses the leading singular vectors of the beta matrix against chip, position, plate, and the biological factors, flagging which technical axis loads on real variance. If chip or position is confounded with the biological group, it is mathematically unrecoverable - hand the explicit correction (ComBat/SVA, or chip/position as covariates/random effects) and the design fix to ewas-design.

## Per-Method Failure Modes

### SNP-overlapping probes left in
**Trigger:** running a per-CpG test without `dropLociWithSnps`. **Mechanism:** a SNP at the CpG or SBE site makes the probe report genotype, not methylation. **Symptom:** reproducible "associations" that are actually genetic (often mQTL-driven, trimodal beta). **Fix:** `dropLociWithSnps(snps=c('CpG','SBE'), maf=0)`; raise maf only to deliberately keep rare variants.

### Wrong cross-reactive list for the array
**Trigger:** applying the Chen 2013 450K list to EPIC/EPICv2 data (or vice versa). **Mechanism:** the cross-reactive probe set is array-version-specific. **Symptom:** wrong probes dropped, real cross-reactive probes retained. **Fix:** use the array-matched list (`xreactive_probes(array_type='EPIC')` vs `'450K'`); maxprobes maps EPICv2 via the collapsed EPIC core IDs.

### EPICv2 replicates not collapsed
**Trigger:** treating EPICv2 betas as if probe IDs were unique. **Mechanism:** ~5,100 loci have 2-10 designs; the same locus appears multiple times. **Symptom:** duplicated rownames, inflated locus weight, broken per-CpG FDR, corrupted cross-version merge. **Fix:** `betasCollapseToPfx()` first; strip the suffix back to the cg core ID before anything downstream.

### Build mismatch on merge
**Trigger:** merging EPICv2 (hg38) coordinates with 450K/EPIC (hg19). **Mechanism:** EPICv2 annotation is hg38-native. **Symptom:** loci silently misaligned by the hg19/hg38 offset. **Fix:** intersect on cg IDs and `mLiftOver` (or restrict to shared IDs and track the build per version).

### Sample swap not checked
**Trigger:** analyzing without the sex/identity QC. **Mechanism:** a mislabeled IDAT carries the wrong phenotype. **Symptom:** weakened or spurious associations; `getSex()` disagrees with the sheet; rs-fingerprints cluster two "different" samples. **Fix:** run `getSex()` vs sample sheet and `getSnpBeta()` fingerprint clustering as mandatory pre-analysis QC.

### Over-filtering
**Trigger:** dropping every flagged probe reflexively. **Mechanism:** some "cross-reactive" probes are fine for the specific locus of interest; maf=0 removes any-SNP probes including innocuous ones. **Symptom:** real signal discarded; clock/signature CpGs lost. **Fix:** treat the maf cutoff and cross-reactive list as calibrated to the question; report attrition and check that target CpGs survive.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| detection-p > 0.01 = failed | Aryee 2014 *Bioinformatics* 30:1363 | signal indistinguishable from background; applied in array-preprocessing |
| bead count < 3 = unreliable | minfi docs | too few beads per probe to trust the intensity |
| `dropLociWithSnps(maf=0)` | minfi docs | maf=0 drops any annotated SNP; raise to keep rare variants (calibrated) |
| ~6% of 450K probes cross-reactive | Chen 2013 *Epigenetics* 8:203 | ~29-39K loci co-hybridize; array-version-specific list |
| EPICv2 ~5,100 replicate loci (2-10 designs) | Kaur 2023 *Epigenetics Commun* 3:6 | collapse to one cg core ID before per-locus FDR |
| 65 rs-SNP probes on 450K (~59 on EPIC) | minfi annotation | enough genotype to fingerprint identity and catch swaps |
| getSex on log2 medY - log2 medX | Aryee 2014 *Bioinformatics* 30:1363 | X/Y intensity clusters by sex; mismatch = swap flag |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Duplicated rownames in EPICv2 beta matrix | replicate probes not collapsed | `betasCollapseToPfx()` before merge/test |
| Reproducible genetic-looking hits | SNP-overlap probes retained | `dropLociWithSnps(snps=c('CpG','SBE'), maf=0)` |
| Coordinates off when merging cohorts | EPICv2 hg38 vs 450K/EPIC hg19 | intersect cg IDs; `mLiftOver` before merge |
| `getSex` disagrees with sample sheet | sample swap/mislabel | trace the IDAT; rs-SNP fingerprint to confirm |
| Cross-reactive filter drops too few/many | wrong array_type list | match the list to the array version |
| `dropXreactiveLoci` errors on EPICv2 object | maxprobes keys on EPIC core IDs | collapse EPICv2 to cg core IDs first |

## References

- Aryee MJ, Jaffe AE, Corrada-Bravo H, et al. 2014. Minfi: a flexible and comprehensive Bioconductor package for the analysis of Infinium DNA methylation microarrays. *Bioinformatics* 30:1363-1369.
- Zhou W, Triche TJ Jr, Laird PW, Shen H. 2018. SeSAMe: reducing artifactual detection of DNA methylation by Infinium BeadChips in genomic deletions. *Nucleic Acids Res* 46:e123.
- Chen YA, Lemire M, Choufani S, et al. 2013. Discovery of cross-reactive probes and polymorphic CpGs in the Illumina Infinium HumanMethylation450 microarray. *Epigenetics* 8:203-209.
- Pidsley R, Zotenko E, Peters TJ, et al. 2016. Critical evaluation of the Illumina MethylationEPIC BeadChip microarray for whole-genome DNA methylation profiling. *Genome Biol* 17:208.
- Kaur D, Lee SM, Goldberg D, et al. 2023. Comprehensive evaluation of the Infinium human MethylationEPIC v2 BeadChip. *Epigenetics Commun* 3:6.

## Related Skills

- array-preprocessing - Produces the corrected beta/M matrix being QC'd and filtered
- ewas-design - Chip/position batch correction and study design
- cell-type-deconvolution - Cohort composition QC
- differential-cpg-testing - Downstream per-CpG testing on the filtered matrix
- workflows/methylation-pipeline - End-to-end pipeline
<!-- END FILE: methylation-analysis/array-qc-filtering/SKILL.md -->

## 子目录：methylation-analysis/bismark-alignment

<!-- BEGIN FILE: methylation-analysis/bismark-alignment/SKILL.md -->
---
name: bio-methylation-bismark-alignment
description: Aligns bisulfite-converted (WGBS, RRBS, PBAT) and enzymatic (EM-seq) short reads to an in-silico C->T/G->A-converted reference with Bismark (Bowtie2 or HISAT2), preparing the genome index, choosing the directional vs non-directional vs PBAT strand flag, deduplicating WGBS/EM-seq (never RRBS), and bounding bisulfite conversion efficiency with unmethylated lambda and methylated pUC19 spike-ins. Covers why the library protocol (not the aligner) decides whether calls are meaningful, why incomplete conversion masquerades as methylation, the 3-letter reduced-complexity mapping bias (50-70% efficiency is normal), and M-bias end-clipping. Use when aligning bisulfite or EM-seq reads, preparing a bisulfite genome, choosing the strand flag, or diagnosing low mapping efficiency. For methylation extraction see methylation-calling; for long-read MM/ML modification calling see long-read-sequencing/nanopore-methylation.
tool_type: cli
primary_tool: Bismark
---

## Version Compatibility

Reference examples tested with: Bismark 0.24+, Bowtie2 2.5+, HISAT2 2.2+, Trim Galore 0.6.10+, samtools 1.19+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags and defaults

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The genome build and the aligner backend ARE the versions that matter. The bisulfite index is built once per genome FASTA with a specific backend (`--bowtie2` vs `--hisat2`); the index must match the backend used at alignment time, and the FASTA build (hg38 vs T2T-CHM13) fixes every downstream coordinate. EM-seq uses the identical aligners and flags as bisulfite - only the upstream chemistry and the coverage/efficiency expectations change.

# Bismark Alignment

**"Align my bisulfite sequencing reads"** -> Confirm the library type to pick the strand flag, trim the chemistry-specific artifacts, then map the C->T-converted reads to a C->T/G->A-converted reference - because the protocol and conversion, not the aligner, decide whether the calls mean anything.
- CLI: `bismark_genome_preparation --bowtie2 genome/` then `bismark --genome genome/ -1 R1.fq.gz -2 R2.fq.gz -o out/`

Scope: short-read bisulfite (WGBS/RRBS/PBAT) and enzymatic (EM-seq) alignment, the genome index, the strand/library flag, deduplication, and conversion QC. Methylation extraction from the BAM (XM tag, MethylDackel, cytosine reports) -> methylation-calling. Per-CpG/DMR statistics -> differential-cpg-testing, dmr-detection. Long-read native MM/ML modification calling -> long-read-sequencing/nanopore-methylation. Adapter trimming mechanics -> read-qc/adapter-trimming.

## The Single Most Important Modern Insight -- Methylation Is Never Sequenced; the Survivors of a Deamination Assay Are

A bisulfite (or EM-seq) run never reads methylation. It reads which cytosines SURVIVED deamination, against a 3-letter genome deliberately depleted of cytosines, as a C-vs-T choice. Every methylation call is two stacked conditional bets, and both fail silently:

1. **Conversion went to completion in BOTH directions.** An unmethylated C that escapes deamination survives as C and is called methylated -> false HYPER-methylation (under-conversion, the dominant fear). A genuinely methylated C deaminated anyway reads T -> false HYPO-methylation (over-conversion). Neither error is visible in the BAM or the mapping rate - only spike-in controls see them, and one control sees only one direction (lambda for under, pUC19 for over).
2. **The read mapped to the right place despite throwing its cytosines away.** The 3-letter alphabet collapses uniqueness, so a wrong library-type flag (PBAT or non-directional run as directional) silently drops half to nearly all reads, and a C/T SNP masquerades as an unmethylated CpG with no alignment penalty.

Organize the work around defending these two bets - chemistry control (both directions) and library/strand correctness - not around listing `bismark` flags. The aligner reports a clean, sorted, indexed BAM whether conversion failed or half the reads went unmapped.

## Why 3-Letter Mapping Is Hard (and Why 50-70% Is Normal)

After conversion, unmethylated Cs become Ts, so the read/genome alphabet collapses toward {A,G,T}. A normal aligner would penalize every C->T as a mismatch, so bisulfite aligners convert all Cs to T in BOTH the reads AND the reference, map in the reduced alphabet, then recover methylation by comparing the original read to the original reference. Bismark builds two converted indices (C->T for OT/CTOT, G->A for OB/CTOB) and aligns each read against both. Reduced complexity means more multi-mapping and a lower mapping efficiency (~50-70% for WGBS vs >95% for ordinary DNA) - this is expected, not a bug. The same collapse means a sample CpG->TpG variant aligns with no extra mismatch and is scored as an unmethylated CpG: methylation at a C/T-polymorphic site is a hypothesis until SNP-aware (Bis-SNP, BISCUIT).

## The Four Strands and the Library-Type Flag

Bisulfite PCR generates four strand species: OT (original top), OB (original bottom), CTOT (complement of OT), CTOB (complement of OB). The library protocol decides which exist, and the flag must match or reads vanish silently:

| Library | Strands sequenced | Bismark flag | Dedup? | Trim Galore special-case |
|---------|-------------------|--------------|--------|--------------------------|
| WGBS (directional) | OT, OB | (default) | YES | M-bias end-clip |
| EM-seq (directional) | OT, OB | (default) | YES | M-bias end-clip (gentler) |
| RRBS | OT, OB | (default) | NO | `--rrbs` (MspI fill-in) |
| PBAT / scBS-seq | CTOT, CTOB | `--pbat` | usually NO | aggressive 5' clip (random priming) |
| non-directional | all four | `--non_directional` | YES | M-bias end-clip (Trim Galore `--non_directional` is RRBS-only, needs `--rrbs`) |

PBAT does bisulfite conversion FIRST then tags by random priming, so its reads originate from CTOT/CTOB - the OPPOSITE of directional. PBAT needs `--pbat` for strand reasons; it is unrelated to RRBS. A non-directional library run as directional silently loses ~half its reads; PBAT run as directional maps near zero.

## Tool Taxonomy

| Tool | Citation | Strategy | When |
|------|----------|----------|------|
| Bismark | Krueger & Andrews 2011 *Bioinformatics* 27:1571 | 3-letter, Bowtie2/HISAT2 backend | de-facto standard; self-contained (index + align + dedup + extractor); teach this |
| bwa-meth | Pedersen 2014 arXiv:1401.1129 | 3-letter, BWA-MEM | lean clinical/cfDNA; handles indels/clipping; pairs with MethylDackel for calling |
| BISCUIT | Zhou 2024 *Nucleic Acids Res* 52:e32 | 3-letter, BWA-derived | when SNPs / allele-specific methylation are needed alongside (joint genetic+epigenetic) |
| gemBS | Merkel 2019 *Bioinformatics* 35:737 | 3-letter, GEM3 | population-scale; the ENCODE WGBS pipeline mapper |
| abismal / methylpy | de Sena Brandine & Smith 2021 *NAR Genom Bioinform* 3:lqab115 | 2-letter (purine/pyrimidine) | memory-constrained, large cohorts |

All produce a BAM whose methylation is recovered by a SEPARATE caller (Bismark extractor, MethylDackel, or the tool's own). Alignment and calling are two steps.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Standard WGBS or EM-seq, mammalian | Bismark default (directional) + dedup | OT/OB only; the common case |
| RRBS | `trim_galore --rrbs` then Bismark default, NO dedup | MspI fixed ends look like (but are not) PCR duplicates |
| PBAT / scBS-seq | `bismark --pbat` | reads come from CTOT/CTOB, not OT/OB |
| Non-directional library | `bismark --non_directional` | all four strands present; default loses half |
| Precious low-input (cfDNA / FFPE / single-cell) | prefer EM-seq or TAPS upstream | bisulfite degrades 84-96% of input; same aligners apply |
| Need SNPs / allele-specific methylation | -> bwa-meth + Bis-SNP, or BISCUIT | C/T SNPs masquerade as methylation in 3-letter space |
| Large mammalian genome, low RAM | `bismark --hisat2` (index must match) | HISAT2 backend is lighter than Bowtie2 |
| Extract per-CpG methylation from the BAM | -> methylation-calling | this skill stops at the deduplicated, M-bias-clipped BAM |
| Long-read ONT/PacBio modBAM (MM/ML tags) | -> long-read-sequencing/nanopore-methylation | native modification calling, not bisulfite |

## Prepare the Genome Index

**Goal:** Build the bisulfite-converted index once per genome, with the backend that alignment will use.

**Approach:** Place the reference FASTA(s) in a folder, run `bismark_genome_preparation` with the chosen backend; it writes `Bisulfite_Genome/` containing the C->T and G->A converted indices.

```bash
bismark_genome_preparation --bowtie2 genome/   # or --hisat2 for large genomes, lower RAM
# genome/ holds the FASTA (e.g. hg38.fa); writes genome/Bisulfite_Genome/{CT_conversion,GA_conversion}
# The backend chosen here MUST match the bismark alignment backend below.
```

## Trim First, with the Chemistry-Specific Flag

**Goal:** Remove adapters and the library-specific end artifacts before alignment so they do not become spurious methylation calls.

**Approach:** Run Trim Galore (Cutadapt wrapper). Add `--rrbs` for RRBS (clips the MspI end-repair fill-in), `--non_directional` for non-directional, or extra 5' clipping for PBAT. Bismark itself does not trim. Mechanics live in read-qc/adapter-trimming.

```bash
trim_galore --paired R1.fq.gz R2.fq.gz                 # WGBS / EM-seq (auto-detect adapter, -q 20)
trim_galore --rrbs --paired R1.fq.gz R2.fq.gz          # RRBS: extra 2 bp off 3' R1 (+ 5' R2) = MspI fill-in
trim_galore --clip_r2 6 --paired R1.fq.gz R2.fq.gz     # PBAT/scBS: random-priming bias at 5' (amount from M-bias)
```

## Align

```bash
bismark --genome genome/ -1 R1_val_1.fq.gz -2 R2_val_2.fq.gz \
    --bowtie2 \         # must match the index backend; --hisat2 if prepared that way
    --parallel 4 \      # instances PER direction; total threads scale up several-fold per instance
    -o out/             # writes *_bismark_bt2_pe.bam + *_PE_report.txt (mapping efficiency, %meth per context)
# Add --pbat for PBAT/scBS, or --non_directional for non-directional libraries (NOT both).
```

## Deduplicate (WGBS/EM-seq Only)

**Goal:** Remove PCR duplicates from random-fragmentation libraries, while leaving RRBS untouched.

**Approach:** `deduplicate_bismark` removes reads sharing mapping coordinate + strand. Run it on the by-name (unsorted) Bismark BAM, before extraction. For RRBS, SKIP it: every fragment starts at an MspI cut site, so identical coordinates are biologically distinct molecules, not PCR copies (apparent duplication ~90-95% is real data).

```bash
deduplicate_bismark --paired --bam out/sample_R1_bismark_bt2_pe.bam   # WGBS/EM-seq ONLY
# RRBS: do NOT run this. UMI-tagged RRBS can dedup by UMI+coordinate; optical dups can still be removed.
samtools sort out/sample_R1_bismark_bt2_pe.deduplicated.bam -o out/sample.sorted.bam   # IGV/downstream
samtools index out/sample.sorted.bam
```

## Conversion QC: Both Directions, and the Spike-In Is an Optimistic Floor

**Goal:** Bound both conversion error directions before believing any methylation level.

**Approach:** Spike unmethylated lambda phage (measures under-conversion -> false hyper) AND CpG-methylated pUC19 (measures over-conversion -> false hypo). Align each spike-in genome separately and read off context methylation. With no spike-in, sample CHH methylation is a weak fallback (somatic tissue only; confounded in ESCs/neurons/plants).

```bash
bismark_genome_preparation --bowtie2 lambda/   # lambda: residual %meth = non-conversion rate (target <=1%)
bismark --genome lambda/ -1 R1.fq.gz -2 R2.fq.gz -o lambda_qc/
# pUC19 (CpG-methylated): fraction of CpGs called UNmethylated = over-conversion (expect ~96-98% methylated)
```

Spike-ins are naked, fully accessible DNA that denature completely, so their conversion is an OPTIMISTIC upper bound. Real genomic conversion is region-dependent: GC-rich CpG islands and structured regions denature less, under-convert more, and inflate apparent methylation exactly where the biology is. Treat the spike-in number as a floor; a rising per-GC-bin CHH rate flags local under-conversion.

## Per-Method Failure Modes

### PBAT or non-directional run with the default flag
**Trigger:** running PBAT/scBS or a non-directional library without `--pbat`/`--non_directional`. **Mechanism:** PBAT reads come from CTOT/CTOB and non-directional from all four strands, but the default tries only OT/OB. **Symptom:** near-zero (PBAT) or ~halved (non-directional) mapping efficiency on a clean-looking run. **Fix:** confirm the kit/protocol directionality, pass the matching flag; never reach for `-N 1` first.

### Incomplete conversion read as methylation
**Trigger:** no conversion control, or only a lambda (under-conversion) control. **Mechanism:** an unmethylated C surviving deamination is indistinguishable from real 5mC. **Symptom:** globally elevated methylation, worst in GC-rich CpG islands. **Fix:** report BOTH a lambda non-conversion rate (<=1%) and a pUC19 over-conversion rate; add per-GC CHH as an internal check.

### RRBS deduplicated by coordinate
**Trigger:** running `deduplicate_bismark` on RRBS. **Mechanism:** MspI cuts give every fragment a fixed start, so distinct molecules share coordinates. **Symptom:** ~90-95% of reads discarded, coverage decimated. **Fix:** skip coordinate dedup for RRBS; use UMIs if dedup is required.

### MspI fill-in not trimmed
**Trigger:** RRBS aligned without `trim_galore --rrbs`. **Mechanism:** end-repair fills MspI overhangs with unmethylated dCTP, creating artificial cytosines at fragment ends. **Symptom:** artificial hypomethylation clustered at MspI sites. **Fix:** `trim_galore --rrbs`; Bismark aligns RRBS fine but does NOT fix this trimming artifact.

### M-bias not clipped before calling
**Trigger:** calling methylation off raw read ends. **Mechanism:** end-repair fills 5' overhangs with unmethylated dCTP, worst at the start of R2. **Symptom:** an M-bias plot (methylation vs read position) shows a dip/spike at the ends instead of a flat line. **Fix:** read the M-bias plot, clip the affected ends; extraction `--ignore`/`--clip` mechanics live in methylation-calling.

### Index/backend mismatch
**Trigger:** index prepared with `--bowtie2`, alignment run with `--hisat2` (or vice versa). **Mechanism:** the two backends use incompatible converted indices. **Symptom:** Bismark errors or fails to find the index. **Fix:** prepare and align with the same backend.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Lambda non-conversion <=1% | manufacturer spec; field standard | residual apparent methylation on unmethylated spike-in = false-positive floor (EM-seq v2 ~<=0.5%) |
| pUC19 ~96-98% methylated | manufacturer spec | bounds over-conversion -> false hypo; lambda alone cannot see this direction |
| WGBS mapping efficiency ~50-70% | Krueger & Andrews 2011; 3-letter complexity | reduced alphabet costs uniqueness; below this, diagnose (library flag > trimming > reference > biology) |
| EM-seq mapping efficiency typically higher | Vaisvila 2021 | no chemical fragmentation -> flatter coverage; WGBS expectations are too pessimistic |
| Bisulfite degrades 84-96% of input | Grunau 2001 *Nucleic Acids Res* 29:e65 | only ~4-16% of molecules survive intact; the reason low-input fails and EM-seq/TAPS exist |
| `-N` = 0 (seed mismatches) | Bismark manual | default; `-N 1` raises sensitivity AND mis-mapping - last resort, not the low-mapping fix |
| `--rrbs` clips 2 bp | Trim Galore guide | the MspI end-repair fill-in length; confirm on the installed version |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Near-zero mapping efficiency | PBAT run as directional | add `--pbat` |
| ~Half the reads unmapped | non-directional run as directional | add `--non_directional` |
| RRBS loses ~90% of reads | deduplicated by coordinate | skip `deduplicate_bismark` for RRBS |
| Globally high methylation | incomplete conversion (no/one-sided control) | lambda + pUC19 spike-ins; check per-GC CHH |
| Artificial hypomethylation at MspI sites | `--rrbs` trimming omitted | `trim_galore --rrbs` |
| FastQC per-base content / GC FAIL | expected for converted libraries (C depleted) | not a defect; do not "fix" a healthy bisulfite library |
| 0% sites at C/T variants | C/T SNP read as unmethylated CpG | SNP-aware calling (Bis-SNP/BISCUIT) or mask known C/T SNPs |
| Bismark cannot find the index | backend mismatch with genome prep | re-prep or align with the matching `--bowtie2`/`--hisat2` |
| Output named "5mC" | standard BS and EM-seq report 5mC+5hmC summed | label the sum; oxBS/TAB pairing is needed to separate (see methylation-calling) |

## References

- Krueger F, Andrews SR. 2011. Bismark: a flexible aligner and methylation caller for Bisulfite-Seq applications. *Bioinformatics* 27:1571-1572.
- Vaisvila R, Ponnaluri VKC, Sun Z, et al. 2021. Enzymatic methyl sequencing detects DNA methylation at single-base resolution from picograms of DNA. *Genome Res* 31:1280-1289.
- Meissner A, Gnirke A, Bell GW, et al. 2005. Reduced representation bisulfite sequencing for comparative high-resolution DNA methylation analysis. *Nucleic Acids Res* 33:5868-5877.
- Miura F, Enomoto Y, Dairiki R, Ito T. 2012. Amplification-free whole-genome bisulfite sequencing by post-bisulfite adaptor tagging. *Nucleic Acids Res* 40:e136.
- Hansen KD, Langmead B, Irizarry RA. 2012. BSmooth: from whole genome bisulfite sequencing reads to differentially methylated regions. *Genome Biol* 13:R83.
- Grunau C, Clark SJ, Rosenthal A. 2001. Bisulfite genomic sequencing: systematic investigation of critical experimental parameters. *Nucleic Acids Res* 29:e65.
- Pedersen BS, Eyring K, De S, Yang IV, Schwartz DA. 2014. Fast and accurate alignment of long bisulfite-seq reads. arXiv:1401.1129.
- Zhou W, Johnson BK, Morrison J, et al. 2024. BISCUIT: an efficient, standards-compliant tool suite for simultaneous genetic and epigenetic inference in bulk and single-cell studies. *Nucleic Acids Res* 52:e32.
- Merkel A, Fernandez-Callejo M, Casals E, et al. 2019. gemBS: high throughput processing for DNA methylation data from bisulfite sequencing. *Bioinformatics* 35:737-742.
- de Sena Brandine G, Smith AD. 2021. Fast and memory-efficient mapping of short bisulfite sequencing reads using a two-letter alphabet. *NAR Genom Bioinform* 3:lqab115.

## Related Skills

- methylation-calling - Extract per-CpG methylation from the aligned BAM
- methylkit-analysis - Downstream import, filtering, normalization
- read-qc/adapter-trimming - Trim Galore before Bismark (RRBS/PBAT handling)
- read-qc/quality-reports - FastQC (expect per-base C-depletion FAIL on converted libraries)
- alignment-files/sam-bam-basics - BAM manipulation after alignment
- sequence-io/read-sequences - FASTQ handling before alignment
- long-read-sequencing/nanopore-methylation - Native long-read MM/ML modification calling (out of scope here)
- workflows/methylation-pipeline - End-to-end bisulfite pipeline
<!-- END FILE: methylation-analysis/bismark-alignment/SKILL.md -->

## 子目录：methylation-analysis/cell-type-deconvolution

<!-- BEGIN FILE: methylation-analysis/cell-type-deconvolution/SKILL.md -->
---
name: bio-methylation-cell-type-deconvolution
description: Estimates cell-type composition from bulk DNA methylation and uses it to defuse the single biggest EWAS confounder. Covers reference-based deconvolution (Houseman constrained-projection, minfi estimateCellCounts2 with FlowSorted.Blood.EPIC + IDOL-optimized libraries, EpiDISH RPC/CBS/CP, 12-cell extended, cord-blood nRBC references, EpiSCORE/hepidish for solid tissue), reference-free correction (ReFACTor, RefFreeEWAS, SVA), using fractions as covariates vs the compositionality/collinearity trap, and cell-type-resolved EWAS (CellDMC, TCA, TOAST, omicwas, HIRE). Use when estimating blood/tissue cell fractions, adjusting an EWAS for composition, choosing a deconvolution reference, or attributing a methylation signal to a cell type. For the EWAS confounder-vs-mediator decision see ewas-design; for the IEAA cell-count adjustment of DNAm age see epigenetic-clocks; for clean beta input see array-preprocessing.
tool_type: r
primary_tool: EpiDISH
---

## Version Compatibility

Reference examples tested with: EpiDISH 2.18+, minfi 1.48+, FlowSorted.Blood.EPIC 2.0+, FlowSorted.CordBloodCombined.450k 1.20+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The REFERENCE package is the version that matters most. A reference package is platform-, tissue-, and age-specific: `FlowSorted.Blood.EPIC` ships `IDOLOptimizedCpGs` (EPIC) and `IDOLOptimizedCpGs450klegacy` (450K) as distinct libraries, the 12-cell library lives in a separate `FlowSorted.BloodExtended.EPIC` package, and cord blood needs `FlowSorted.CordBloodCombined.450k` (it carries nucleated red blood cells). `estimateCellCounts2` returns a `Neu` (neutrophil) column where the older `minfi::estimateCellCounts` returns `Gran` - the label changes the downstream column names. Record the reference package and version alongside the array build.

# Cell-Type Deconvolution

**"How much of my methylation signal is just cell composition?"** -> Project the bulk beta matrix onto a purified-cell reference to estimate per-sample fractions, then carry those fractions forward as covariates - because a bulk methylome is a composition-weighted average and a composition difference is a methylation difference.
- R: `epidish(beta.m, ref.m = centDHSbloodDMC.m, method = 'RPC')$estF`

Scope: estimate cell-type fractions from a clean bulk beta matrix and use them downstream. Clean beta read-in and EPICv2 replicate-probe collapse -> array-preprocessing. The confounder-vs-mediator decision and the EWAS regression itself -> ewas-design. Adjusting a DNAm clock for cell counts (IEAA) -> epigenetic-clocks. Single-cell/sorted atlases for reference building and validation ground truth -> single-cell/preprocessing. Predictive-model training/leakage -> machine-learning/biomarker-discovery.

## The Single Most Important Modern Insight -- A Cell-Fraction Estimate Is a Projection, Not a Measurement

A reference-based fraction is not a measurement of a sample's composition; it is a projection of that sample onto cell types someone else purified, on someone else's platform, in someone else's tissue. Three corollaries each common misuse violates:

1. **A composition difference IS a methylation difference.** Bulk DNAm is the fraction-weighted average of its constituent cell-type methylomes, and most CpG variance is between cell types, not between conditions. If cases and controls differ in composition - which they almost always do (age, sex, infection, smoking shift the neutrophil-to-lymphocyte ratio) - the EWAS reports cell-count differences as if they were disease methylation. This is the #1 EWAS confounder (Jaffe & Irizarry 2014 *Genome Biol* 15:R31).
2. **The reference defines the answer.** A cell type present in the sample but absent from the reference is silently redistributed onto the nearest reference types - no error, the fractions still sum to ~1. Cord blood without nRBC, a solid tissue against a blood reference, EPICv2 data against a 450K library: all return confident, wrong proportions.
3. **Fractions are compositional.** They live on a simplex (sum ~1), so they are not independent: one going up forces others down. Naively co-regressing or correlating all K fractions manufactures spurious negative associations.

Organize the analysis around matching the reference and handling compositionality, not around picking an algorithm. Deconvolution turns an uncontrollable confounder into a measurable covariate - but only as accurately as the reference matches the sample.

## Reference-Based: The Houseman Constrained-Projection Foundation

Houseman 2012 (*BMC Bioinformatics* 13:86) is the origin. From a matrix of FACS/MACS-purified cell-type mean methylation at discriminating CpGs (L-DMRs), solve for each sample a constrained quadratic program: the non-negative fraction vector w (w_i >= 0, sum ~1) minimizing the squared distance between observed beta and reference x w over the L-DMR CpGs. This "CP" (constrained projection) is what every later method is measured against. The L-DMR selection is itself a tuning choice that the IDOL work (Koestler 2016 *BMC Bioinformatics* 17:120) optimized into a fixed, benchmarked library.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| EpiDISH (RPC) | Teschendorff 2017 *BMC Bioinformatics* 18:105 | robust partial correlation; downweights noisy CpGs | general; the robust default across tissues/noise |
| EpiDISH (CP) | Houseman 2012 *BMC Bioinformatics* 13:86 | constrained quadratic projection | reproduce the classic Houseman estimate |
| EpiDISH (CBS) | Newman 2015 *Nat Methods* 12:453 | CIBERSORT nu-SVR | borrowed from expression; an alternative |
| minfi estimateCellCounts2 | Salas 2018 *Genome Biol* 19:64 | Houseman projection on the IDOL-optimized EPIC/450K library | from an RGChannelSet; modern 6-cell blood (Neu) |
| FlowSorted.BloodExtended.EPIC | Salas 2022 *Nat Commun* 13:761 | 12-cell IDOL library | naive/memory T, Treg, eosinophil/basophil resolution |
| hepidish | Teschendorff 2017 *BMC Bioinformatics* 18:105 | hierarchical Epi/Fib/Immune then immune subtypes | solid tissue with immune infiltration |
| EpiSCORE | Teschendorff 2020 *Genome Biol* 21:221 | scRNA-seq-imputed DNAm reference | solid tissues with no sorted reference |
| ReFACTor | Rahmani 2016 *Nat Methods* 13:443 | sparse-PCA components as covariates | reference-free; no matched reference exists |
| RefFreeEWAS | Houseman 2014 *Bioinformatics* 30:1431 | NMF/SVD-style latent cell-mixture | reference-free; unlabeled components |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Adult whole blood | estimateCellCounts2 IDOL (6: Neu/CD4T/CD8T/NK/Bcell/Mono) or EpiDISH RPC (centDHSbloodDMC.m gives 7, adds Eos) | benchmarked blood references |
| Need naive/memory T, Treg, Eos, Bas | 12-cell FlowSorted.BloodExtended.EPIC | the 6-cell library cannot resolve these |
| Cord blood / newborn | FlowSorted.CordBloodCombined.450k | adds nRBC; an adult reference is silently wrong |
| Saliva / buccal | epithelial + immune reference (hepidish) | saliva is not blood; epithelial fraction dominates |
| Solid tissue / tumor with infiltration | hepidish or EpiSCORE | flat blood reference on solid tissue is meaningless |
| 450K data | EpiDISH cent*450k.m / IDOLOptimizedCpGs450klegacy | platform-matched CpGs; EPIC library drops CpGs |
| EPICv2 data | collapse replicate probes first -> array-preprocessing | suffixed replicate beads hide the reference CpGs |
| No matched reference (novel tissue) | ReFACTor / RefFreeEWAS + sensitivity | reference-free fallback; components are unlabeled |
| Which cell type drives a signal | CellDMC / TCA / TOAST (below) | model composition, do not just regress it out |
| Confounder-vs-mediator decision | -> ewas-design | upstream: adjust out, or resolve cell-specific? |

## Estimate Blood Fractions with EpiDISH (RPC)

**Goal:** Get per-sample fractions of the major immune cell types from a clean beta matrix to use as EWAS covariates.

**Approach:** Pass the beta matrix and a tissue-matched reference centroid to `epidish` with `method='RPC'` (the robust option), then read the sample-by-cell-type matrix from `$estF`.

```r
library(EpiDISH)
data(centDHSbloodDMC.m)    # 7 immune cell types, adult whole blood

out <- epidish(beta.m = beta_matrix, ref.m = centDHSbloodDMC.m, method = 'RPC')
fractions <- out$estF       # samples x cell types; rows sum to ~1
```

## Estimate Blood Fractions from an RGChannelSet (minfi + IDOL)

**Goal:** Estimate the modern 6-cell IDOL blood composition straight from raw IDAT-derived data.

**Approach:** Run `estimateCellCounts2` on the RGChannelSet with the IDOL probe selection and the platform-matched reference; for 450K data switch the reference library so the same cell types are estimated cross-platform.

```r
library(FlowSorted.Blood.EPIC)

counts <- estimateCellCounts2(
  rgSet,
  compositeCellType = 'Blood',
  processMethod = 'preprocessNoob',
  probeSelect = 'IDOL',
  cellTypes = c('CD8T', 'CD4T', 'NK', 'Bcell', 'Mono', 'Neu'),   # Neu, not Gran
  referencePlatform = 'IlluminaHumanMethylationEPIC'
)$counts
```

## Solid Tissue: Hierarchical Deconvolution

**Goal:** Deconvolve a solid tissue (epithelial + fibroblast + infiltrating immune) rather than forcing a blood reference onto it.

**Approach:** Use `hepidish` to first split Epithelial/Fibroblast/total-Immune, then deconvolve the immune fraction into subtypes and multiply through. For tissues with no sorted reference at all, EpiSCORE builds an imputed DNAm reference from a single-cell RNA atlas.

```r
library(EpiDISH)
data(centEpiFibIC.m)       # Epithelial / Fibroblast / Immune-Cell
data(centBloodSub.m)       # immune subtypes for the second level

frac <- hepidish(beta.m = beta_matrix, ref1.m = centEpiFibIC.m,
                 ref2.m = centBloodSub.m, h.CT.idx = 3, method = 'RPC')
# h.CT.idx = 3 = the Immune column in ref1 to expand with ref2
```

## Reference-Free Correction

**Goal:** Capture composition structure when no matched reference exists, accepting unlabeled components.

**Approach:** ReFACTor selects the most composition-informative CpGs and runs sparse-PCA; use the top components as EWAS covariates. RefFreeEWAS decomposes the matrix into a latent cell-mixture term. Both correct without naming the cell types, so check that genuine top hits survive (they can absorb real signal).

```r
library(TCA)
ref <- refactor(beta_matrix, k = 6)   # k = expected number of cell types
covariates <- ref$scores              # top sparse-PC components as EWAS covariates
```

## Using the Fractions: Covariate vs Cell-Type-Resolved

There are two distinct moves once fractions exist, and they answer different questions.

**As covariates (the standard EWAS defense).** Include the fractions in the per-CpG design matrix so composition is regressed out. Because fractions are compositional (sum ~1), do NOT enter all K - drop one reference cell type (or use a compositional transform) to avoid perfect collinearity. The confounder-vs-mediator decision (regress out, or treat composition as the mechanism) belongs to ewas-design; execution belongs to differential-cpg-testing.

**Cell-type-resolved EWAS (which cell type drives the signal).** Instead of regressing composition away, model a phenotype x cell-fraction INTERACTION per CpG to ask which cell type carries the differential methylation and in which direction. CellDMC (Zheng 2018 *Nat Methods* 15:1059) is the simplest member; a family generalizes it:

| Method | Citation | Adds beyond the interaction | Output |
|--------|----------|-----------------------------|--------|
| CellDMC | Zheng 2018 *Nat Methods* 15:1059 | per-CpG linear pheno x fraction interaction | which cell type is DM + direction (a test) |
| TCA | Rahmani 2019 *Nat Commun* 10:3417 | tensor model; per-sample per-cell-type levels | cell-type-specific methylation + association test |
| TOAST | Li & Wu 2019 *Genome Biol* 20:190 | iterative csDM; improves reference-free composition | csTest per cell type; runs reference-free |
| omicwas | Takeuchi & Kato 2021 *BMC Bioinformatics* 22:141 | nonlinear ridge for the logit scale + fraction collinearity | cell-type-specific association statistics |
| HIRE | Luo 2019 *Nat Commun* 10:3113 | joint multiplicative-composition hierarchical model | risk-CpG sites per cell type |

```r
library(EpiDISH)
res <- CellDMC(beta.m = beta_matrix, pheno.v = phenotype, frac.m = fractions)
# res$dmct: per-CpG, which cell type is differentially methylated (-1/0/1)
```

A cell-type-resolved call is an ill-posed inverse problem regularized by an assumed reference: rare cell types (2-5% of the mixture) are badly underpowered, fraction collinearity destabilizes the interactions, and deconvolution error propagates straight into the attribution (HIRE's argument for estimating composition jointly). Validation is hard without sorted/single-cell ground truth - method papers lean on simulations and reconstructed mixtures, which are circular. Treat an in-silico cell-type-specific hit as a HYPOTHESIS about what to sort next, not a finding; confirm load-bearing attributions in sorted or single-cell DNAm from independent samples (Walker 2025 *Brief Bioinform* 26:bbaf427).

## The IEAA Link to Clocks

Intrinsic epigenetic age acceleration (IEAA) is DNAm age residualized on chronological age AND estimated blood cell counts - so deconvolution is the prerequisite step: estimate fractions here, then hand them to epigenetic-clocks as the cell-count covariates that distinguish cell-intrinsic aging from a composition shift. Do not teach the clock here; compute the fractions and route the IEAA adjustment to epigenetic-clocks.

## Per-Method Failure Modes

### Missing cell type silently redistributed
**Trigger:** a sample contains a cell type absent from the reference (cord-blood nRBC, a rare infiltrate, a granulocyte subtype collapsed to Gran). **Mechanism:** the constrained projection has no column for it, so its signal lands on the nearest present types. **Symptom:** plausible-looking fractions that sum to ~1 with no warning. **Fix:** match the reference to tissue+age (FlowSorted.CordBloodCombined.450k for newborns; hepidish/EpiSCORE for solid tissue).

### Platform-mismatched reference library
**Trigger:** 450K data with the EPIC IDOL library, or EPICv2 with either. **Mechanism:** reference CpGs are partly absent on the other platform, shrinking the L-DMR set used for the projection. **Symptom:** biased fractions, no error. **Fix:** `IDOLOptimizedCpGs450klegacy` / `cent*450k.m` for 450K; collapse EPICv2 replicate probes first (-> array-preprocessing).

### Collinear cell-fraction covariates
**Trigger:** entering all K fractions (sum ~1) into a design matrix. **Mechanism:** the simplex constraint makes the K-th fraction a linear function of the others. **Symptom:** rank-deficient design, dropped coefficient, or spurious negative fraction-fraction correlations. **Fix:** drop one reference cell type or use a compositional (CLR/ILR) transform.

### Reference-free over-correction
**Trigger:** including too many ReFACTor/RefFreeEWAS components, or using them when a reference exists. **Mechanism:** unlabeled latent components can absorb true biological signal alongside composition. **Symptom:** top EWAS hits vanish; false negatives. **Fix:** prefer reference-based when a reference exists; use reference-free as a fallback/sensitivity check and confirm hits survive.

### Cell-type attribution from rare cells
**Trigger:** reading a CellDMC/TCA call for a 2-5% cell type. **Mechanism:** a rare cell contributes a fraction-attenuated slice of bulk variance, so its interaction estimate is dominated by deconvolution noise. **Symptom:** confident-looking csDM in basophils/eosinophils; nulls misread as "no effect." **Fix:** report each cell type's mean fraction; distrust specific calls for low-abundance types; never infer absence of effect from an underpowered null.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| IDOL EPIC 6-cell library ~450 CpGs | Salas 2018 *Genome Biol* 19:64 | benchmarked L-DMR set; R^2 ~0.992 on reconstructed mixtures |
| method = 'RPC' for EpiDISH | Teschendorff 2017 *BMC Bioinformatics* 18:105 | robust to outlier/noisy CpGs; more stable than CP across tissues |
| drop 1 of K fractions as covariates | compositional constraint | fractions sum to ~1, so all K are perfectly collinear |
| cord blood reference must carry nRBC | Gervin 2019 / CordBloodCombined | nRBC abundant in cord blood, absent from adult references |
| ReFACTor k = expected cell-type count | Rahmani 2016 *Nat Methods* 13:443 | k sets the rank; too high over-corrects, too low under-corrects |
| csDM credible only for abundant types | Walker 2025 *Brief Bioinform* 26:bbaf427 | rare cells are fraction-attenuated and underpowered |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Fractions look fine but EWAS still inflated | unmodeled cell type / wrong reference | match reference to tissue+age+platform |
| Design matrix rank-deficient | all K fractions entered as covariates | drop one cell type or CLR-transform |
| estimateCellCounts2 returns Neu, code expects Gran | minfi vs FlowSorted label difference | use Neu (estimateCellCounts2) consistently |
| Reference CpGs not found on EPICv2 | replicate probes not collapsed | collapse to one value per CpG first |
| Negative or all-zero fraction for a type | platform mismatch / absent in sample | check platform-matched library; inspect mean fraction |
| csDM hit in a rare cell type | underpowered interaction | report the fraction; validate by sorting/single-cell |

## References

- Houseman EA, Accomando WP, Koestler DC, et al. 2012. DNA methylation arrays as surrogate measures of cell mixture distribution. *BMC Bioinformatics* 13:86.
- Jaffe AE, Irizarry RA. 2014. Accounting for cellular heterogeneity is critical in epigenome-wide association studies. *Genome Biol* 15:R31.
- Koestler DC, Jones MJ, Usset J, et al. 2016. Improving cell mixture deconvolution by identifying optimal DNA methylation libraries (IDOL). *BMC Bioinformatics* 17:120.
- Salas LA, Koestler DC, Butler RA, et al. 2018. An optimized library for reference-based deconvolution of whole-blood biospecimens assayed using the Illumina HumanMethylationEPIC BeadArray. *Genome Biol* 19:64.
- Salas LA, Zhang Z, Koestler DC, et al. 2022. Enhanced cell deconvolution of peripheral blood using DNA methylation for high-resolution immune profiling. *Nat Commun* 13:761.
- Teschendorff AE, Breeze CE, Zheng SC, Beck S. 2017. A comparison of reference-based algorithms for correcting cell-type heterogeneity in epigenome-wide association studies. *BMC Bioinformatics* 18:105.
- Teschendorff AE, Zhu T, Breeze CE, Beck S. 2020. EPISCORE: cell type deconvolution of bulk tissue DNA methylomes from single-cell RNA-Seq data. *Genome Biol* 21:221.
- Houseman EA, Molitor J, Marsit CJ. 2014. Reference-free cell mixture adjustments in analysis of DNA methylation data. *Bioinformatics* 30:1431-1439.
- Rahmani E, Zaitlen N, Baran Y, et al. 2016. Sparse PCA corrects for cell type heterogeneity in epigenome-wide association studies. *Nat Methods* 13:443-445.
- Zheng SC, Breeze CE, Beck S, Teschendorff AE. 2018. Identification of differentially methylated cell types in epigenome-wide association studies. *Nat Methods* 15:1059-1066.
- Rahmani E, Schweiger R, Rhead B, et al. 2019. Cell-type-specific resolution epigenetics without the need for cell sorting or single-cell biology. *Nat Commun* 10:3417.
- Li Z, Wu H. 2019. TOAST: improving reference-free cell composition estimation by cross-cell type differential analysis. *Genome Biol* 20:190.
- Takeuchi F, Kato N. 2021. Nonlinear ridge regression improves cell-type-specific differential expression analysis. *BMC Bioinformatics* 22:141.
- Luo X, Yang C, Wei Y. 2019. Detection of cell-type-specific risk-CpG sites in epigenome-wide association studies. *Nat Commun* 10:3113.
- Walker EM, Dempster EL, Franklin A, et al. 2025. Guidance for the design and analysis of cell-type-specific DNA methylation epidemiology studies. *Brief Bioinform* 26:bbaf427.

## Related Skills

- array-preprocessing - Provides the clean beta matrix deconvolution consumes
- ewas-design - Cell-fraction covariate strategy (confounder vs mediator)
- epigenetic-clocks - IEAA: adjust the clock for estimated cell composition
- differential-cpg-testing - Uses cell fractions as design-matrix covariates
- single-cell/preprocessing - scRNA atlases for reference building (EpiSCORE) and ground truth
- machine-learning/biomarker-discovery - Predictive-model boundary
- workflows/methylation-pipeline - End-to-end pipeline
<!-- END FILE: methylation-analysis/cell-type-deconvolution/SKILL.md -->

## 子目录：methylation-analysis/differential-cpg-testing

<!-- BEGIN FILE: methylation-analysis/differential-cpg-testing/SKILL.md -->
---
name: bio-methylation-differential-cpg
description: Tests individual CpG sites for differential methylation (DMC/DMP) from bisulfite sequencing counts or array/continuous beta-value matrices. Covers the count-vs-continuous fork that dictates the model, beta-value vs M-value logit (Du 2010), beta-binomial overdispersion count models (DSS, methylKit, MOABS, RADMeth) for sequencing, limma moderated-t on M-values (eBayes trend/robust) for arrays, the bare-beta Welch t-test caveat, coverage-as-precision coupling, delta-beta effect size, BH-FDR with the neighboring-CpG dependence problem, EWAS genome-wide thresholds, and differential variability (DiffVar/iEVORA). Use when comparing per-CpG methylation between groups from WGBS/RRBS/targeted bisulfite or 450K/EPIC arrays, choosing a per-site test, or scanning for variance (not just mean) differences. For region-level aggregation see dmr-detection; for covariate/cell-fraction strategy and genomic inflation see ewas-design.
tool_type: mixed
primary_tool: limma
---

## Version Compatibility

Reference examples tested with: limma 3.58+, DSS 2.50+, methylKit 1.28+, missMethyl 1.36+, scipy 1.13+, statsmodels 0.14+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The DATA OBJECT is the version that matters most: sequencing yields integer (M, Cov) counts whose coverage is precision (a count model uses it); arrays yield a continuous beta with no coverage (a Gaussian model on M-values). The genome build of the calls (hg38 vs T2T-CHM13) and, for arrays, the platform (`450K` vs `EPIC`) fix the CpG universe and the genome-wide threshold. methylKit defaults (`overdispersion="none"`, `adjust="SLIM"`) silently change results; always confirm with `?calculateDiffMeth`.

# Per-CpG Differential Methylation Testing

**"Which single CpGs differ between my groups?"** -> First decide whether the data is sequencing COUNTS or a continuous array ratio, because that choice dictates the entire model - then test on M, report effect on beta, and gate on the intersection of FDR and |delta-beta|.
- R: `DSS::DMLtest()` on counts (sequencing); `limma::lmFit() |> eBayes(trend=TRUE, robust=TRUE)` on M-values (array/continuous)
- Python: `scipy.stats.ttest_ind(equal_var=False)` + `multipletests(method='fdr_bh')` - a continuous/array QUICK-LOOK only, never the headline sequencing test

Scope: the per-SITE test (DMC/DMP). Region-level aggregation (DSS callDMR, BSmooth, DMRcate) -> dmr-detection. Producing the (M, Cov) counts -> methylation-calling. Long-read MM/ML modBAM input -> long-read-sequencing/nanopore-methylation (pipe per-site counts back here). Covariate strategy, cell-fraction confounding, genomic inflation, replication design -> ewas-design.

## The Single Most Important Modern Insight -- The Right Test Is Dictated by the Data Object, and the Variance to Model Is Biological, Not Sampling Noise

The hardest lesson in the field is that the spread between biological replicates - not the coin-flip sampling at a single site - is the variance the test must capture. Three corollaries dictate the whole skill:

1. **Counts are not a beta.** Sequencing gives `(M, Cov)` per site per sample, and Cov IS precision: a beta of 0.80 from 80/100 reads is far more certain than 0.80 from 4/5. Collapsing to `beta = M/Cov` and running a t-test weights both sites equally and throws coverage away. For sequencing use a beta-binomial / overdispersion-corrected count model (DSS, methylKit `overdispersion="MN"`) that USES the coverage. Arrays genuinely have no counts - there a Gaussian model on M-values is correct.
2. **Binomial variance is not biological variance.** Fisher's exact (especially pooled across replicates) and uncorrected logistic regression assume the only randomness is binomial sampling at fixed depth. Two healthy individuals differ at a CpG far more than that, so these tests are anticonservative BY CONSTRUCTION - they hand back a long list of false positives that look exactly like findings. The whole job of DSS/MOABS/RADMeth and of methylKit's overdispersion option is to add the between-replicate (Beta) dispersion layer.
3. **Test on M, interpret on beta.** M-values (logit) are homoscedastic and well-calibrated; beta is bounded, heteroscedastic, and the only interpretable effect (delta-beta). The M-scale logFC is NOT a delta-beta and never maps linearly to one. The correct call is the INTERSECTION: `adj.P < cutoff AND |delta-beta| >= cutoff`.

Organize the analysis around defending these three, with the count-vs-continuous fork as the first decision - not around listing tests.

## Beta vs M-Value -- Why the Scale Matters

Beta = proportion methylated, range [0, 1], the unit of biological interpretation and of effect size (delta-beta). Its fatal property is heteroscedasticity: the variance of a proportion depends on its mean (maximal near 0.5, crushed toward 0 at the extremes where most genomic CpGs actually sit). A Gaussian linear model assumes constant variance, so a t-test/limma on raw beta is mis-calibrated, worst at the extremes. The M-value (Du 2010 *BMC Bioinformatics* 11:587), `log2(beta/(1-beta))`, is approximately homoscedastic and gives better-calibrated p-values, with the gap largest at high/low methylation. The division of labor: test on M, report delta-beta on beta. To avoid log(0) at beta in {0,1}, prefer computing M from intensities/counts as `log2((Meth+alpha)/(Unmeth+alpha))` (alpha ~ 1-100, never hits the boundary) over a symmetric offset on a precomputed beta.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| DSS | Feng 2014 *Nucleic Acids Res* 42:e69; Park & Wu 2016 *Bioinformatics* 32:1446 | beta-binomial, Bayesian dispersion shrinkage, Wald test | the count-based per-site default; few replicates; general designs |
| methylKit | Akalin 2012 *Genome Biol* 13:R87 | per-site logistic regression; `overdispersion="MN"` -> F-test | WGBS/RRBS; fast; SET overdispersion with replicates |
| MOABS (mcomp) | Sun 2014 *Genome Biol* 15:R38 | beta-binomial CDIF folding biological + statistical signal | CLI; depth-adjusted single metric |
| RADMeth | Dolzhenko & Smith 2014 *BMC Bioinformatics* 15:215 | beta-binomial regression, arbitrary multifactor design | CLI (methpipe); complex covariate models |
| limma | Ritchie 2015 *Nucleic Acids Res* 43:e47 | moderated-t on M-values, empirical-Bayes variance shrinkage | arrays (450K/EPIC) and any continuous matrix; small n |
| scipy Welch / Mann-Whitney | scipy docs | per-site continuous two-group test | array/continuous QUICK-LOOK only; NOT a count model |
| DiffVar (missMethyl) | Phipson & Oshlack 2014 *Genome Biol* 15:465 | Levene-style deviations + EB moderation (variance test) | scan for differentially VARIABLE CpGs alongside the mean |
| iEVORA | Teschendorff 2016 *Nat Commun* 7:10478 | Bartlett variance test + t re-ranking | field defects / rare stochastic outliers / risk prediction |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| WGBS/RRBS counts, replicates | DSS `DMLtest`, or methylKit `overdispersion="MN", test="F"` | beta-binomial uses coverage and models between-replicate dispersion |
| Sequencing, complex/multifactor design | DSS `DMLfit.multiFactor` or RADMeth | regression on counts with covariates |
| Unreplicated sequencing (n=1 vs n=1) | Fisher's exact on counts (exploratory) | no replicates means no biological variance to estimate; never pool replicates into this |
| 450K / EPIC array (or any continuous matrix) | limma moderated-t on M-values (`trend=TRUE, robust=TRUE`) | no counts exist; EB rescues small n; THE array workhorse |
| Quick continuous look, high uniform coverage | scipy Welch on M-values + BH | defensible shortcut at high depth; loses coverage-as-precision |
| Per-site, but biology is regional | per-site test, then -> dmr-detection | neighboring CpGs are correlated; aggregate for regional inference |
| Bulk tissue (blood etc.), any platform | add cell-fraction covariates to the design -> ewas-design | cell composition is the #1 EWAS confounder (Jaffe & Irizarry 2014) |
| Signal may be variance, not mean (cancer/aging) | DiffVar / iEVORA ON M-VALUES, alongside the mean scan | a variance change is invisible to a mean test |
| Long-read MM/ML per-site counts | -> long-read-sequencing/nanopore-methylation | calling/QC owned there; transfer (mod, valid) counts here |

When the design is contested (count model vs continuous, smooth vs not), verify current best practice against the installed tool's vignette rather than hard-coding one approach; count models are the rigorous default for sequencing, continuous tests a high-coverage shortcut, NOT a small-n shortcut.

## DSS Beta-Binomial on Counts (R, sequencing default)

**Goal:** Test each CpG for a mean methylation difference using a model that uses coverage as precision and shrinks the between-replicate dispersion.

**Approach:** Assemble per-sample (chr, pos, N=Cov, X=M) data frames into a BSseq object, run the Wald test per site with shrunken dispersion, then gate on FDR and an explicit effect-size floor.

```r
library(DSS)

# Each sample is a data.frame with columns chr, pos, N (total Cov), X (methylated M)
bs_obj <- makeBSseqData(list(c1, c2, c3, t1, t2, t3),
                        c('c1', 'c2', 'c3', 't1', 't2', 't3'))

# smoothing=FALSE keeps this a true per-SITE test; smoothing=TRUE borrows from
# neighbors (span 500 bp) and crosses into DMR territory -> dmr-detection
dml <- DMLtest(bs_obj, group1 = c('c1', 'c2', 'c3'), group2 = c('t1', 't2', 't3'), smoothing = FALSE)

# delta = effect-size floor on beta (default 0 applies NO gate); p.threshold is the FDR cut
dmc <- callDML(dml, delta = 0.1, p.threshold = 0.05)
# dml columns: mu1, mu2, diff (delta-beta on the beta scale), diff.se, stat, pval, fdr
```

## methylKit on Counts (R, the overdispersion trap)

**Goal:** Run a per-site logistic-regression test that accounts for between-replicate overdispersion (the default does not).

**Approach:** After uniting per-sample coverage objects, fit with overdispersion correction so the test becomes an F-test, then extract hyper/hypo sites with explicit effect and FDR floors.

```r
library(methylKit)

# meth is a united methylBase object (from methRead -> filterByCoverage -> unite)
# overdispersion="none" is the DEFAULT and over-calls under replication; set "MN" -> F-test
diff <- calculateDiffMeth(meth, overdispersion = 'MN', test = 'F', adjust = 'BH')
# adjust="SLIM" is the methylKit default, NOT BH; pass adjust="BH" to match other tools

# difference is in percentage points (25 = 25 points); qvalue is the FDR floor
dmc <- getMethylDiff(diff, difference = 25, qvalue = 0.01, type = 'all')
# meth.diff is a weighted-mean model difference, NOT mean(case_beta)-mean(ctrl_beta);
# recompute delta-beta from raw betas when comparing tools
```

## limma Moderated-t on M-Values (R, array/continuous default)

**Goal:** Identify DMPs from an array or continuous matrix at small n by borrowing variance across the ~10^5-10^6 probes.

**Approach:** Convert beta to M-values, fit per-probe linear models with EB moderation (trend+robust), extract BH-adjusted p-values, then attach delta-beta computed from the RAW betas.

```r
library(limma)

# M from intensities is cleaner; from a beta matrix use a boundary-safe transform
m_values <- log2((beta_matrix + 1e-3) / (1 - beta_matrix + 1e-3))

group <- factor(c(rep('case', 6), rep('ctrl', 6)))
design <- model.matrix(~ 0 + group)        # add cell-fraction/covariate columns here -> ewas-design
colnames(design) <- levels(group)
contrast_matrix <- makeContrasts(case - ctrl, levels = design)

fit <- lmFit(m_values, design)
fit2 <- contrasts.fit(fit, contrast_matrix)
fit2 <- eBayes(fit2, trend = TRUE, robust = TRUE)   # both default FALSE; set TRUE for methylation

res <- topTable(fit2, number = Inf, adjust.method = 'BH', sort.by = 'none')
# adjusted column is adj.P.Val (limma), NOT padj (DESeq2) or FDR; logFC is M-scale, NOT delta-beta
res$delta_beta <- rowMeans(beta_matrix[, group == 'case']) - rowMeans(beta_matrix[, group == 'ctrl'])
```

## Differential Variability -- Test the Variance, Not Just the Mean

A whole class of cancer/aging/field-defect signal lives in the SECOND moment: a CpG tight in controls (beta ~ 0.8) but scattered 0.3-0.95 in cases at the SAME mean is invisible to every mean test above. Run a differential-variability (DV) scan ALONGSIDE the mean scan; a CpG can be a DMP, a DVC, both, or neither.

**Goal:** Find CpGs whose spread (not mean) differs between groups, with FDR control robust to outliers.

**Approach:** On M-VALUES (the logit decouples variance from mean - see the boundary caveat below), fit Levene-style deviations with limma's EB moderation, then rank by adjusted p-value.

```r
library(missMethyl)

# Run on M-values: a variance difference on raw beta can be a pure mean-at-boundary artifact
fit <- varFit(m_values, design = design, coef = c(1, 2))   # ALWAYS pass coef (the group columns)
dvc <- topVar(fit, coef = 2, number = Inf)                 # coef must match; default is LAST column
# iEVORA (Bartlett variance + t re-ranking, Bartlett FDR < 0.001) is the field-defect alternative
```

Boundary caveat (the load-bearing DV trap): on beta in [0,1] variance is structurally tied to the mean (~ p(1-p)), so a mean shift from beta~0.95 toward ~0.6 mechanically RAISES variance and fakes a DV hit. Both DiffVar and iEVORA run on M-values for exactly this reason; always co-report the mean delta-beta next to any DV hit so a reader can judge whether the variance signal is independent of a boundary-driven mean move.

## Welch Quick-Look on Continuous Data (Python)

**Goal:** A fast continuous two-group per-site test for ARRAY/continuous matrices (or high uniform-coverage sequencing where coverage loss is accepted) - explicitly not the sequencing headline.

**Approach:** Test on M-values per CpG with Welch (unequal variance), then apply BH FDR; report delta-beta from raw betas.

```python
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

# m_case / m_ctrl: M-value matrices (rows CpGs, cols samples). For SEQUENCING counts prefer DSS.
_, pvalues = ttest_ind(m_case, m_ctrl, axis=1, equal_var=False, nan_policy='omit')  # Welch; scipy default is Student's
reject, padj, _, _ = multipletests(pvalues, method='fdr_bh')  # default is 'hs' (Holm-Sidak), must set fdr_bh
delta_beta = beta_case.mean(axis=1) - beta_ctrl.mean(axis=1)  # effect on the beta scale
```

## Multiple Testing and the Dependence Problem

BH-FDR is the default at both platforms; Bonferroni leaves almost nothing at 850k EPIC probes or 28M+ WGBS CpGs. Two caveats: (1) BH assumes independence (or positive dependence), but neighboring CpGs are strongly spatially correlated, so per-site BH on methylation is conservative-but-not-exact, and a lone significant CpG flanked by null neighbors is suspect - this regional dependence is precisely why region-level methods exist (-> dmr-detection); do not try to fix it inside per-site BH. (2) Large consortium array EWAS often use a fixed genome-wide threshold for comparability instead of BH: ~2.4e-7 experiment-wide for 450K (Saffari 2018), and P < 9e-8 (~8.6e-9 genome-wide) for EPIC (Mansell 2019). WGBS has no single accepted constant - BH or region-level FDR dominate.

## Per-Method Failure Modes

### Bare-beta t-test on sequencing counts
**Trigger:** computing `beta = M/Cov` from bisulfite counts and running a t-test. **Mechanism:** discards coverage (an 8-read and an 800-read site weigh equally) and, on raw beta, fights heteroscedasticity. **Symptom:** noisy low-coverage sites masquerade as confident hits; poor replication. **Fix:** for sequencing use DSS or methylKit `overdispersion="MN"` on counts; if forced continuous, at least test on M-values at high depth.

### methylKit left at overdispersion="none"
**Trigger:** `calculateDiffMeth(meth)` with replicates and no overdispersion argument. **Mechanism:** the default does NO overdispersion correction - a plain logistic LRT that assumes binomial-only variance. **Symptom:** inflated significant-CpG count; anticonservative p-values. **Fix:** `overdispersion="MN", test="F"`; pass `adjust="BH"` (default is SLIM).

### Pooling replicates for Fisher's exact
**Trigger:** summing M and U across replicates into one super-sample per group to "have enough counts". **Mechanism:** collapses biological variance - treats N mice as one giant mouse. **Symptom:** wildly anticonservative p-values. **Fix:** a replicate-aware count model; Fisher only for n=1 vs n=1, reported as exploratory.

### Reporting the M-scale logFC as delta-beta
**Trigger:** quoting limma `logFC` or methylKit `meth.diff` as the methylation-percentage change. **Mechanism:** the logit is steep at 0.5 and flat at the ends, so the same logFC is a large beta-change mid-range and a tiny one at the extremes. **Symptom:** overstated effect sizes near 0/1. **Fix:** recompute delta-beta from raw betas for reporting, always.

### Significance without effect size (and the reverse)
**Trigger:** ranking by FDR alone at large n, or by delta-beta alone at small n. **Mechanism:** at 28M CpGs a 2-point delta-beta within noise clears FDR; a big delta from 3 noisy samples is not a finding. **Symptom:** non-reproducible top hits. **Fix:** gate on the intersection `adj.P < cutoff AND |delta-beta| >= cutoff`.

### Winner's curse on discovery effect sizes
**Trigger:** quoting the top hits' discovery delta-betas as the true effect. **Mechanism:** thresholding selects sites where noise pushed the estimate up, so reported magnitudes are upward-biased. **Symptom:** replication cohorts show attenuated effects; replications powered on the inflated delta-beta are underpowered. **Fix:** flag discovery |delta-beta| as an upper bound; estimate the honest effect from independent replication (Palmer & Pe'er 2017).

### Ignoring cell composition in bulk tissue
**Trigger:** an EWAS on whole blood / bulk tissue with no cell-fraction covariates. **Mechanism:** the top "DMPs" are often shifts in cell-type proportion, not within-cell methylation (Jaffe & Irizarry 2014). **Symptom:** hits that fail to replicate across cohorts. **Fix:** estimate cell fractions and add them to the design matrix -> ewas-design.

### Differential-variability hit that is a mean artifact
**Trigger:** a DV test on raw beta values. **Mechanism:** beta variance is tied to the mean, so a mean move toward 0.5 fakes higher variance. **Symptom:** DV hits that co-occur with large mean shifts toward 0.5. **Fix:** run DiffVar/iEVORA on M-values and co-report the mean delta-beta.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Min coverage 10x in EVERY sample | field standard | below it a single-CpG beta is granular and noisy; floor must hold in all compared samples |
| Upper cap at 99.9th percentile Cov | field standard | drops PCR-duplicate pileups / collapsed-repeat mapping artifacts |
| WGBS 5-10x / RRBS 10x / targeted 30-100x | assay convention | smoothing tolerates 5x; targeted expects deep, even depth |
| delta-beta floor 0.10 / 0.20 / 0.30 | convention | 0.10 EWAS discovery (diluted by cell mixture), 0.20 general, 0.30 cancer-vs-normal |
| methylKit getMethylDiff difference=25, qvalue=0.01 | Akalin 2012 *Genome Biol* 13:R87 | tool defaults; 25 percentage points, FDR 0.01 |
| DSS callDML delta default 0 (set it) | DSS docs | delta=0 applies NO effect-size gate; set delta=0.1 |
| BH-FDR, not Bonferroni | field standard | Bonferroni leaves almost nothing at 10^5-10^7 tests |
| 450K ~2.4e-7; EPIC P<9e-8 | Saffari 2018; Mansell 2019 | fixed array EWAS thresholds for cross-study comparability |
| Fisher's exact: n=1 vs n=1 only | mechanism | no replicates means no biological variance; never pool replicates |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Long list of low-coverage false positives | bare-beta t-test on sequencing counts | DSS / methylKit `overdispersion="MN"` on counts |
| methylKit returns too many DMCs | left at `overdispersion="none"` | set `overdispersion="MN", test="F"` |
| methylKit q-values disagree with other tools | default `adjust="SLIM"`, not BH | pass `adjust="BH"` |
| Effect sizes overstated near 0/1 | reported M-scale logFC as delta-beta | recompute delta-beta from raw betas |
| Almost nothing significant genome-wide | Bonferroni at millions of tests | BH-FDR (WGBS) or EWAS thresholds (array) |
| `padj`/`$FDR` column not found in limma | wrong column name | limma column is `adj.P.Val` |
| All p-values NaN in Python | `multipletests` default `method='hs'` or wrong axis | pass `method='fdr_bh'`; test on M-values, `axis=1` |
| EWAS hits do not replicate | cell composition / winner's curse | cell-fraction covariates; treat discovery effects as upper bounds |

## References

- Du P, Zhang X, Huang C-C, Jafari N, Kibbe WA, Hou L, Lin SM. 2010. Comparison of Beta-value and M-value methods for quantifying methylation levels by microarray analysis. *BMC Bioinformatics* 11:587.
- Feng H, Conneely KN, Wu H. 2014. A Bayesian hierarchical model to detect differentially methylated loci from single nucleotide resolution sequencing data. *Nucleic Acids Res* 42:e69.
- Park Y, Wu H. 2016. Differential methylation analysis for BS-seq data under general experimental design. *Bioinformatics* 32:1446-1453.
- Akalin A, Kormaksson M, Li S, Garrett-Bakelman FE, Figueroa ME, Melnick A, Mason CE. 2012. methylKit: a comprehensive R package for the analysis of genome-wide DNA methylation profiles. *Genome Biol* 13:R87.
- Sun D, Xi Y, Rodriguez B, Park HJ, Tong P, Meong M, Goodell MA, Li W. 2014. MOABS: model based analysis of bisulfite sequencing data. *Genome Biol* 15:R38.
- Dolzhenko E, Smith AD. 2014. Using beta-binomial regression for high-precision differential methylation analysis in multifactor whole-genome bisulfite sequencing experiments. *BMC Bioinformatics* 15:215.
- Ritchie ME, Phipson B, Wu D, Hu Y, Law CW, Shi W, Smyth GK. 2015. limma powers differential expression analyses for RNA-sequencing and microarray studies. *Nucleic Acids Res* 43:e47.
- Phipson B, Oshlack A. 2014. DiffVar: a new method for detecting differential variability with application to methylation in cancer and aging. *Genome Biol* 15:465.
- Teschendorff AE, Gao Y, Jones A, Ruebner M, Beckmann MW, Wachter DL, Fasching PA, Widschwendter M. 2016. DNA methylation outliers in normal breast tissue identify field defects that are enriched in cancer. *Nat Commun* 7:10478.
- Jaffe AE, Irizarry RA. 2014. Accounting for cellular heterogeneity is critical in epigenome-wide association studies. *Genome Biol* 15:R31.
- Saffari A, Silver MJ, Zavattari P, Moi L, Columbano A, Meaburn EL, Dudbridge F. 2018. Estimation of a significance threshold for epigenome-wide association studies. *Genet Epidemiol* 42:20-33.
- Mansell G, Gorrie-Stone TJ, Bao Y, Kumari M, Schalkwyk LS, Mill J, Hannon E. 2019. Guidance for DNA methylation studies: statistical insights from the Illumina EPIC array. *BMC Genomics* 20:366.
- Palmer C, Pe'er I. 2017. Statistical correction of the Winner's Curse explains replication variability in quantitative trait genome-wide association studies. *PLoS Genet* 13:e1006916.

## Related Skills

- methylation-calling - Produces the (M, coverage) counts tested here
- methylkit-analysis - methylKit object model and calculateDiffMeth mechanics
- dmr-detection - Region-level aggregation downstream of per-site testing
- cell-type-deconvolution - Cell-fraction covariates (the dominant bulk-tissue confounder)
- ewas-design - Covariate strategy, genomic inflation, and genome-wide thresholds
- experimental-design/multiple-testing - FDR/FWER theory behind the corrections applied here
- long-read-sequencing/nanopore-methylation - Long-read MM/ML calling; pipe per-site counts here for count-based statistics
- differential-expression/deseq2-basics - Analogous dispersion-shrinkage / empirical-Bayes machinery
- workflows/methylation-pipeline - End-to-end bisulfite pipeline
<!-- END FILE: methylation-analysis/differential-cpg-testing/SKILL.md -->

## 子目录：methylation-analysis/dmr-detection

<!-- BEGIN FILE: methylation-analysis/dmr-detection/SKILL.md -->
---
name: bio-methylation-dmr-detection
description: Detects differentially methylated regions (DMRs) from short-read bisulfite (WGBS/RRBS), array, and long-read methylation count tables using dmrseq (permutation region-FDR over the region selection), DSS callDMR (beta-binomial), methylKit tiles, bsseq BSmooth, DMRcate Gaussian-kernel smoothing, metilene, and comb-p. Covers why a DMR is DEFINED by arbitrary thresholds (min-CpGs, max-gap, delta-beta, q) and a smoothing bandwidth, why selecting extreme runs of CpGs then testing them on the same data is post-selection inference, why region q-values are not comparable across tools, and a single-sample domain-segmentation section (PMD, UMR/LMR, MethylSeekR, solo-WCGW) that must run before focal calling on cancer/aging genomes. Use when calling region-level methylation differences, choosing a DMR caller, controlling region-level FDR, or segmenting megabase methylation domains. For per-site testing see differential-cpg-testing; for the methylKit object model see methylkit-analysis.
tool_type: r
primary_tool: dmrseq
---

## Version Compatibility

Reference examples tested with: dmrseq 1.22+, DSS 2.50+, methylKit 1.28+, bsseq 1.38+, DMRcate 2.16+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The GENOME BUILD is a version that matters. methylKit/bsseq/DMRcate `assembly=` is metadata, but annotation packages (`annotatr::build_annotations(genome='hg38')`, `TxDb.Hsapiens.UCSC.hg38.knownGene`) are build-specific and must match the alignment genome. DMRcate `arraytype='EPIC'`/`'450K'` and the IlluminaHumanMethylation annotation package set the array CpG universe. DMRcate defaults shift across Bioconductor releases (the `C` kernel scaling has no single default - it is platform-dependent); confirm with `?dmrcate` on the installed build.

# DMR Detection

**"Find differentially methylated regions"** -> Detect candidate regions, then score them with a null that re-ran the selection - because a DMR is defined by a chain of thresholds, not found, and only a selection-aware q-value is honest.
- R: `dmrseq(bs, testCovariate='condition')` (selection-aware) ; `DSS::callDMR()`, `methylKit::tileMethylCounts()`, `bsseq` BSmooth, `DMRcate::dmrcate()` (combine-and-correct)

Scope: REGION-level differential methylation from any per-CpG methylation+coverage table (WGBS/RRBS counts, array beta/M, long-read modkit bedMethyl), plus single-sample domain segmentation. Per-site DMC/DMP testing -> differential-cpg-testing. The methylKit import/filter/unite object model -> methylkit-analysis. Long-read MM/ML calling that produces the counts -> long-read-sequencing/nanopore-methylation. Functional enrichment of DMR genes -> pathway-analysis/go-enrichment (with the CpG-bias correction noted below).

## The Single Most Important Modern Insight -- A DMR Is DEFINED, Not Found, and the Region p-Value Is Only Honest If Its Null Re-Ran the Selection

The naive recipe - compute a per-CpG statistic, select runs of CpGs that look extreme to DEFINE candidate regions, then test those same regions and report a p/q on the same data - reuses the data twice. The regions were CHOSEN because they were extreme; scoring them with the data that selected them inflates significance and produces uncalibrated region FDR. This is post-selection inference, the field's original sin. No error is thrown; the q-values just lie. Three corollaries:

1. **dmrseq neutralizes the selection; the others combine-and-correct but do not re-select.** dmrseq (Korthauer 2019 *Biostatistics* 20:367) builds the null by PERMUTING the condition labels and RE-RUNNING the entire candidate-detection procedure on each permutation, pooling permuted region statistics into one genome-wide null - so its q-value is on REGIONS and accounts for selection. comb-p and DMRcate combine existing per-CpG p-values (Stouffer/Fisher/SLK) and apply a region multiplicity correction, but never re-run selection. methylKit tiles use FIXED windows (boundaries not chosen from the data, so the selection part is sidestepped) but ignore inter-tile correlation. DSS callDMR merges significant CpGs (threshold-then-define).

2. **Region q-values are NOT comparable across tools.** "I found 4,000 DMRs at q<0.05" is meaningless without naming the tool and what its q controls. Cross-tool OVERLAP is the real evidence - run two callers and intersect.

3. **Thresholds are conventions, not biology.** delta-beta 25%, min-CpGs 3, max-gap 1000bp, q<0.01 are tutorial folklore. The same data yields radically different DMR sets under different settings. Report and justify every knob; never present one config as correct.

Organize the analysis around defending these, not around listing functions.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| dmrseq | Korthauer 2019 *Biostatistics* 20:367 | GLS area statistic + permutation null that re-runs selection; smooths the difference internally | headline WGBS inference; calibrated region FDR; >=2 reps/group |
| DSS callDMR | Feng 2014 *Nucleic Acids Res* 42:e69; Park & Wu 2016 *Bioinformatics* 32:1446 | per-CpG Bayesian beta-binomial dispersion shrinkage, then merge significant CpGs | small n, complex/multi-factor designs; low-coverage with smoothing |
| methylKit tiles | Akalin 2012 *Genome Biol* 13:R87 | fixed windows + logistic/F test per tile | fast RRBS/WGBS screening; reuses the methylKit object model |
| bsseq (BSmooth) | Hansen 2012 *Genome Biol* 13:R83 | per-sample local-likelihood smoothing -> smoothed t-statistic | low/uneven-coverage WGBS; superseded by dmrseq for calibrated FDR |
| DMRcate | Peters 2015 *Epigenetics Chromatin* 8:6; Peters 2021 *Nucleic Acids Res* 49:e109 | Gaussian-kernel smoothing of the per-CpG statistic | arrays (450K/EPIC) and WGBS (different kernel) |
| metilene | Juhling 2016 *Genome Res* 26:256 | binary segmentation + 2D Kolmogorov-Smirnov; standalone C CLI | fast whole-genome second caller; data-adaptive boundaries; tolerates missingness |
| comb-p | Pedersen 2012 *Bioinformatics* 28:2986 | ACF + Stouffer-Liptak-Kechris combination + Sidak; Python CLI on any p-values | array EWAS regions; tool-agnostic corroboration of any per-CpG p-values |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| WGBS, >=2 reps/group, headline region inference | dmrseq | only caller whose region FDR accounts for selection |
| WGBS, small n, multi-factor / covariates | DSS (`DMLtest.multiFactor` -> `callDMR`) | beta-binomial dispersion shrinkage + model formula |
| Low / uneven coverage WGBS | dmrseq (smooths internally) or DSS `smoothing=TRUE` | smoothing borrows strength across CpGs |
| RRBS, quick region screen | methylKit tiles (filtered, `cov.bases>=3`) | fixed windows; fast; CpG-island enriched; screening q, not selection-corrected |
| EPIC/450K array | DMRcate array mode (`cpg.annotate('array')`) or comb-p on limma p | kernel tuned for array spacing; methylKit/bsseq/dmrseq are count-based |
| Corroborate any DMR set | run a second caller, intersect | region q is not comparable across tools |
| Cancer / aging / placenta / cultured-cell WGBS | segment PMDs FIRST (see domain section) | a focal caller manufactures fake hypo-DMRs from PMD background |
| Per-CpG, not region | -> differential-cpg-testing | site-level test before aggregating to regions |
| Long-read modkit bedMethyl input | -> long-read-sequencing/nanopore-methylation, then any caller here | modkit calls; feed Nmod + Nvalid_cov here for region statistics |

## dmrseq: The Selection-Aware Headline Caller

**Goal:** Call WGBS DMRs with a region-level FDR that survives the region-selection step.

**Approach:** Build a `BSseq` object from raw counts (do NOT pre-smooth), filter loci with zero coverage in any sample, then run `dmrseq`, which detects candidate regions (runs of CpGs whose smoothed methylation-difference coefficient exceeds `cutoff`), computes one GLS area statistic per region, and generates the null by permuting labels and re-running detection.

```r
library(dmrseq)
library(bsseq)

bs <- read.bismark(c('ctrl1.cov.gz', 'ctrl2.cov.gz', 'treat1.cov.gz', 'treat2.cov.gz'),
                   colData = DataFrame(condition = c('ctrl', 'ctrl', 'treat', 'treat')),
                   rmZeroCov = TRUE, strandCollapse = TRUE)

# dmrseq requires every locus to have non-zero coverage in EVERY sample.
bs <- bs[rowSums(getCoverage(bs) == 0) == 0, ]

# cutoff=0.1 only SEEDS candidate detection (10% smoothed difference); significance
# comes from the permutation statistic, so dmrseq does NOT hard-threshold delta-beta.
dmrs <- dmrseq(bs, testCovariate = 'condition', cutoff = 0.1)
sig <- dmrs[dmrs$qval < 0.05]   # qval is a REGION FDR that accounts for selection
```

dmrseq smooths the DIFFERENCE internally (`bpSpan`/`minInSpan`/`maxGapSmooth`); running `BSmooth()` first double-smooths and invalidates the model. The permutation null is COARSE at 2-vs-2 (few distinct label permutations) - the package pools across all candidate regions to compensate, but more replicates give a finer null. Use `adjustCovariate` for nuisance variables and `block = TRUE` for large-scale differential blocks.

## DSS: Beta-Binomial Dispersion Shrinkage

**Goal:** Call DMRs with per-CpG dispersion shrinkage for small n or a multi-factor design.

**Approach:** `DMLtest` does per-CpG Wald tests with a Bayesian beta-binomial dispersion estimate, then `callDMR` merges significant CpGs into regions.

```r
library(DSS)

bs <- makeBSseqData(list(c1, c2, t1, t2), c('C1', 'C2', 'T1', 'T2'))   # each: chr/pos/N/X data.frame
dml <- DMLtest(bs, group1 = c('C1', 'C2'), group2 = c('T1', 'T2'), smoothing = TRUE)   # TRUE for low-cov WGBS

# callDMR defaults (verify on installed build): delta=0, p.threshold=1e-5,
# minlen=50, minCG=3, dis.merge=100, pct.sig=0.5.
# delta=0 means NO effect-size floor - SET it explicitly so tiny shifts are not called.
dmrs <- callDMR(dml, delta = 0.1, p.threshold = 1e-5, minlen = 50, minCG = 3,
                dis.merge = 100, pct.sig = 0.5)   # pct.sig=0.5: >=50% of region CpGs individually significant
```

callDMR merges significant CpGs (threshold-then-define), so its region p is NOT selection-corrected; its strengths are dispersion shrinkage and multi-factor support (`DMLtest.multiFactor` with a model formula).

## bsseq BSmooth

**Goal:** Call DMRs on low/uneven-coverage WGBS by smoothing each sample before testing.

**Approach:** Smooth per sample, compute the smoothed t-statistic, then threshold it into regions.

```r
library(bsseq)

bs_smooth <- BSmooth(bs, BPPARAM = MulticoreParam(4), verbose = TRUE)
keep <- rowSums(getCoverage(bs_smooth) >= 2) == ncol(bs_smooth)   # >=2x in every sample
bs_filt <- bs_smooth[keep, ]

tstat <- BSmooth.tstat(bs_filt, group1 = c('C1', 'C2'), group2 = c('T1', 'T2'),
                       estimate.var = 'same', mc.cores = 4)
dmrs <- dmrFinder(tstat, cutoff = c(-4.6, 4.6))   # t-stat cutoff (Hansen 2012 uses quantile-based cutoffs)
```

`dmrFinder` needs `BSmooth.tstat` output, not the smoothed `BSseq` object directly. BSmooth gives a RANKED DMR list, not a calibrated region FDR - dmrseq (same lab lineage) supersedes it for region inference. Over-smoothing (too-wide bandwidth) washes out focal promoter DMRs.

## DMRcate: The Array-vs-WGBS Fork

**Goal:** Call DMRs by Gaussian-kernel smoothing of the per-CpG statistic, with the correct kernel for the platform.

**Approach:** Annotate per-CpG statistics through the array OR sequencing entry point, then smooth and extract.

```r
library(DMRcate)

# ARRAY (450K/EPIC): beta/M matrix; arraytype sets the CpG universe.
design <- model.matrix(~ condition)
ann_array <- cpg.annotate('array', m_values, what = 'M', arraytype = 'EPIC',
                          analysis.type = 'differential', design = design, coef = 2)
dmrs_array <- extractRanges(dmrcate(ann_array, lambda = 1000, C = 2))   # array kernel

# WGBS: different entry point AND a much smaller kernel - the array C=2 over-smooths
# dense sequencing CpGs ~25x. Annotate from a count/edgeR-DSS path, then C=50.
ann_seq <- sequencing.annotate(bs, design = design, coef = 2)
dmrs_seq <- extractRanges(dmrcate(ann_seq, C = 50))   # WGBS kernel (Peters 2021)
```

The default `lambda=1000, C=2` is ARRAY-only; applying it to WGBS produces massively over-smoothed, merged, inflated DMRs. `pcutoff='fdr'` returns no DMRs if the upstream limma/DSS yields no significant CpGs.

## metilene and comb-p (Second Callers)

metilene is a standalone C CLI taking one tab table (chrom, pos, per-sample methylation rate); binary segmentation + a 2D-KS test find data-adaptive boundaries. comb-p is a Python CLI that takes a BED of per-CpG p-values from ANY upstream test, estimates the p-value autocorrelation, does a Stouffer-Liptak-Kechris combination of neighbors, groups regions, and applies a one-step Sidak correction.

```bash
metilene -M 1000 -m 10 -d 0.1 -a g1 -b g2 input.tsv | metilene_output.pl   # -m min CpGs, -d min mean diff
comb-p pipeline -c 4 --seed 0.01 --dist 500 --step 50 -p out methyl_pvals.bed   # --seed = p to start a region
```

Both combine-and-correct rather than re-select; use them as fast corroboration and intersect with dmrseq.

## Thresholds Are Conventions; Region FDR Is Tool-Specific

Every caller exposes the same coupled knobs under different names: min-CpGs (`minNumRegion`/`minCG`/`-m`/`min.cpgs`/`cov.bases`), max-gap (`maxGap`/`dis.merge`/`-M`), delta-beta (`cutoff`/`delta`/`-d`/`betacutoff`/`difference`), and a significance cutoff. Shrinking max-gap, raising min-CpGs, and raising delta all reduce the DMR count, and the same data yields wildly different DMR sets. The phrase "region-level FDR" means three different objects: a selection-aware permutation FDR (dmrseq), a BH/Sidak correction on combined per-CpG p-values (DMRcate/comb-p), or per-unit q on independent tiles/CpGs (methylKit/DSS). Report all knobs, name the tool, and use cross-tool overlap as the evidence statement.

## DMR-to-Gene Mapping and the CpG-Density Enrichment Bias

**Goal:** Interpret DMRs without inflating enrichment from CpG-rich genes.

**Approach:** Annotate DMRs to features (annotatr returns one row per DMR-feature overlap; genomation collapses by precedence), then run enrichment with a method that corrects for CpG/probe count.

```r
library(annotatr)
annots <- build_annotations(genome = 'hg38', annotations = c('hg38_basicgenes', 'hg38_cpg_islands'))
dmr_ann <- annotate_regions(regions = sig, annotations = annots, ignore.strand = TRUE)   # one row per overlap

# Enrichment: methylation has a CpG-density bias (CpG-rich genes harbor DMRs by chance),
# so a plain hypergeometric GO test is biased. Use missMethyl goregion (probe/CpG-bias-aware).
# missMethyl::goregion(sig_ranges, all.cpg=..., collection='GO', array.type='EPIC')
```

A single DMR commonly overlaps or sits between several genes; mapping DMR -> gene (nearest TSS vs overlap vs within-X-kb) is a modeling choice that changes the gene list. Hand the corrected enrichment to pathway-analysis/go-enrichment, flagging that methylation input needs a CpG-bias-aware method (missMethyl `gometh`/`goregion`), not a generic hypergeometric test.

## Single-Sample Domain Structure (NOT Differential)

This is a DIFFERENT problem from the focal between-group callers above. The mammalian methylome partitions at MEGABASE scale into Highly Methylated Domains (HMDs, ~80-90%, ordered) and Partially Methylated Domains (PMDs, ~40-70%, disordered, high-variance), and PMDs coincide with late replication, Lamina-Associated Domains, and the Hi-C B-compartment (Lister 2009 *Nature* 462:315; Berman 2012 *Nat Genet* 44:40). Cancer "global hypomethylation" is a DOMAIN phenomenon - focal CpG-island hypermethylation sitting ON a background of megabase PMD hypomethylation - not a focal one. Domain structure is a SINGLE-SAMPLE, structural question answered by SEGMENTERS, not by any between-group DMR caller (methylKit/DSS/dmrseq/DMRcate/metilene/comb-p have no single-sample segmentation mode).

- **MethylSeekR** (Burger 2013 *Nucleic Acids Res* 41:e155) segments one WGBS methylome into UMRs (CpG-rich unmethylated = promoters/CGIs), LMRs (CpG-poor low-methylated ~30% = distal enhancers), and PMDs. Pipeline: `readMethylome()` -> `plotAlphaDistributionOneChr()` (diagnostic: does the sample have PMDs?) -> `segmentPMDs()` (2-state Gaussian HMM, 101-CpG windows) -> `calculateFDRs()` -> `segmentUMRsLMRs(m=0.5, n=..., pmdGRanges=...)`. PMDs MUST be masked before UMR/LMR calling or PMD disorder spawns spurious LMRs.
- **solo-WCGW** (Zhou 2018 *Nat Genet* 50:591) - an isolated CpG in `[A/T]CG[A/T]` context - loses methylation fastest and most monotonically with cell division and is the most sensitive PMD/mitotic-clock readout, detecting PMD hypomethylation even in near-normal tissue. Quantify as the mean over the published common-PMD solo-WCGW CpG set, not as a DMR. See epigenetic-clocks for the broader clock taxonomy.

The warning: running a focal DMR caller on a PMD-bearing genome manufactures thousands of fake hypo-DMRs that are really one phenomenon - the PMD background shifting - chopped into pieces by the max-gap/min-CpG knobs. Segment domains FIRST, then EXCLUDE PMD intervals from focal calling or STRATIFY every DMR by in-PMD vs out-of-PMD and report the fraction that is PMD background.

## Per-Method Failure Modes

### PMD background reported as DMRs
**Trigger:** focal caller on tumor/aged/placenta/cultured WGBS without domain screening. **Mechanism:** megabase PMD hypomethylation chopped into pieces by max-gap/min-CpG. **Symptom:** thousands of large hypo-DMRs in gene-desert, late-replicating, low-CpG-density coordinates. **Fix:** segment PMDs (MethylSeekR) first; exclude or stratify; report the PMD fraction.

### Pre-smoothing before dmrseq
**Trigger:** `BSmooth()` then feeding the smoothed object to `dmrseq`. **Mechanism:** dmrseq smooths the difference internally; pre-smoothing double-smooths. **Symptom:** distorted candidate regions and invalid statistics. **Fix:** feed dmrseq the raw `BSseq` counts.

### DMRcate array defaults on WGBS
**Trigger:** copying `lambda=1000, C=2` onto sequencing data. **Mechanism:** the array kernel is ~25x too wide for dense WGBS CpGs. **Symptom:** massively over-smoothed, merged, inflated DMRs. **Fix:** `sequencing.annotate()` + `C=50` for WGBS (Peters 2021).

### Threshold-then-test reported as region FDR
**Trigger:** greping runs of significant per-CpG calls and reporting the per-CpG q. **Mechanism:** the regions were selected for extremeness, then tested on the same data. **Symptom:** anti-conservative, uncalibrated region q. **Fix:** use dmrseq (selection-aware) for the headline; at minimum state that a tile/merge q is a screening q.

### Single-CpG tiles
**Trigger:** `tileMethylCounts` at the default `cov.bases=0`. **Mechanism:** a window with one covered CpG becomes a "DMR." **Symptom:** thousands of single-CpG noisy regions. **Fix:** set `cov.bases >= 3`.

### Cross-tool count comparison
**Trigger:** comparing "N DMRs at q<0.05" between callers. **Mechanism:** each tool's q controls a different object. **Symptom:** apparent disagreement that is really an FDR-definition mismatch. **Fix:** compare OVERLAP, not counts.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| dmrseq `cutoff` 0.1 (candidate seed only) | Korthauer 2019 | seeds detection; significance is the permutation statistic, NOT a delta floor |
| DSS `callDMR(delta=0)` default -> SET it | Park & Wu 2016; DSS docs | delta=0 calls regions with no effect-size floor; set ~0.1 to require a real shift |
| min-CpGs per region 3-5 | convention | single-CpG "regions" are DMPs in disguise; trades sensitivity vs specificity |
| delta-beta 25% ("moderate") | methylKit tutorial folklore | NOT derived; biologically meaningful delta is feature- and purity-dependent |
| methylKit `tileMethylCounts(cov.bases>=3)` | nuance (default is 0) | the default 0 lets single-CpG tiles through |
| coverage floor ~10x per CpG | field standard | a single-CpG beta below ~10x is a coin flip |
| DMRcate WGBS `C=50` (array `C=2`) | Peters 2021 *Nucleic Acids Res* 49:e109 | dense WGBS CpGs need a far narrower kernel than array probes |
| MethylSeekR `m=0.5`, FDR<5% | Burger 2013 | methylation cutoff for hypomethylated regions; FDR target picks the CpG-count threshold n |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| dmrseq error about zero-coverage loci | a locus has 0 coverage in some sample | filter `rowSums(getCoverage(bs)==0)==0` first |
| Thousands of huge hypo-DMRs in cancer WGBS | PMD background not segmented | MethylSeekR `segmentPMDs` first; exclude/stratify |
| Over-merged WGBS DMRs with DMRcate | array kernel on sequencing | `sequencing.annotate()` + `C=50` |
| `dmrFinder` errors on a smoothed object | needs `BSmooth.tstat` output | run `BSmooth.tstat` before `dmrFinder` |
| DMRcate returns no DMRs | `pcutoff='fdr'` and no significant upstream CpGs | check the upstream limma/DSS result first |
| Biased GO enrichment of DMR genes | plain hypergeometric ignores CpG density | use missMethyl `goregion`/`gometh` |

## References

- Korthauer K, Chakraborty S, Benjamini Y, Irizarry RA. 2019. Detection and accurate false discovery rate control of differentially methylated regions from whole genome bisulfite sequencing. *Biostatistics* 20:367-383.
- Feng H, Conneely KN, Wu H. 2014. A Bayesian hierarchical model to detect differentially methylated loci from single nucleotide resolution sequencing data. *Nucleic Acids Res* 42:e69.
- Park Y, Wu H. 2016. Differential methylation analysis for BS-seq data under general experimental design. *Bioinformatics* 32:1446-1453.
- Hansen KD, Langmead B, Irizarry RA. 2012. BSmooth: from whole genome bisulfite sequencing reads to differentially methylated regions. *Genome Biol* 13:R83.
- Akalin A, Kormaksson M, Li S, et al. 2012. methylKit: a comprehensive R package for the analysis of genome-wide DNA methylation profiles. *Genome Biol* 13:R87.
- Peters TJ, Buckley MJ, Statham AL, et al. 2015. De novo identification of differentially methylated regions in the human genome. *Epigenetics Chromatin* 8:6.
- Peters TJ, Buckley MJ, Chen Y, et al. 2021. Calling differentially methylated regions from whole genome bisulphite sequencing with DMRcate. *Nucleic Acids Res* 49:e109.
- Juhling F, Kretzmer H, Bernhart SH, Otto C, Stadler PF, Hoffmann S. 2016. metilene: fast and sensitive calling of differentially methylated regions from bisulfite sequencing data. *Genome Res* 26:256-262.
- Pedersen BS, Schwartz DA, Yang IV, Kechris KJ. 2012. Comb-p: software for combining, analyzing, grouping and correcting spatially correlated P-values. *Bioinformatics* 28:2986-2988.
- Lister R, Pelizzola M, Dowen RH, et al. 2009. Human DNA methylomes at base resolution show widespread epigenomic differences. *Nature* 462:315-322.
- Berman BP, Weisenberger DJ, Aman JF, et al. 2012. Regions of focal DNA hypermethylation and long-range hypomethylation in colorectal cancer coincide with nuclear lamina-associated domains. *Nat Genet* 44:40-46.
- Zhou W, Dinh HQ, Ramjan Z, et al. 2018. DNA methylation loss in late-replicating domains is linked to mitotic cell division. *Nat Genet* 50:591-602.
- Burger L, Gaidatzis D, Schubeler D, Stadler MB. 2013. Identification of active regulatory regions from DNA methylation data. *Nucleic Acids Res* 41:e155.

## Related Skills

- differential-cpg-testing - Per-site testing before region aggregation
- methylkit-analysis - methylKit object model and tile construction
- methylation-calling - Produces the input count tables
- array-preprocessing - Array beta/M-value input for DMRcate array mode
- epigenetic-clocks - Mitotic-clock / solo-WCGW overlap (domain section)
- pathway-analysis/go-enrichment - CpG-bias-aware enrichment of DMR genes (missMethyl gometh)
- long-read-sequencing/nanopore-methylation - Pipe modkit bedMethyl counts here for region statistics
- workflows/methylation-pipeline - End-to-end bisulfite pipeline
<!-- END FILE: methylation-analysis/dmr-detection/SKILL.md -->

## 子目录：methylation-analysis/epigenetic-clocks

<!-- BEGIN FILE: methylation-analysis/epigenetic-clocks/SKILL.md -->
---
name: bio-methylation-epigenetic-clocks
description: Computes DNA methylation age (DNAm age) and pace of aging by applying frozen elastic-net epigenetic clocks to a clean beta matrix with methylclock, dnaMethyAge, or methylCIPHER. Covers the clock menu by question (chronological Horvath/Hannum/skin&blood; health-mortality PhenoAge/GrimAge; DunedinPACE pace; pediatric/gestational; mitotic epiTOC), age acceleration (EAA/IEAA/EEAA) as the real endpoint, the principal-component (PC) clock fix for the per-CpG reliability crisis, and EPICv2 clock-CpG dropout with missing-CpG imputation bias. Use when estimating epigenetic age, computing age acceleration, choosing a clock for an outcome, assessing clock reliability, or porting a clock to EPICv2. A clock is a frozen predictor: do not GO-enrich its CpGs and do not train it here. For cell-count adjustment (IEAA) see cell-type-deconvolution; for predictor training/validation/leakage see machine-learning/model-validation; for survival modeling of age acceleration see clinical-biostatistics/survival-analysis.
tool_type: r
primary_tool: methylclock
---

## Version Compatibility

Reference examples tested with: methylclock 1.8+, dnaMethyAge (GitHub yiluyucheng), methylCIPHER (GitHub MorganLevineLab), DunedinPACE (GitHub danbelsky).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The clock coefficient sets are FIXED and version-pinned (a clock is a frozen list of CpGs and weights), so the package version mostly controls which clocks ship and what the clock-name strings are. Verify accepted names live: `methylclock` via `checkClocks(beta)`; `dnaMethyAge` via `availableClock()`. The ARRAY PLATFORM is the version that matters most: EPICv2 drops a clock-specific fraction of CpGs, so always report how many of each clock's CpGs were actually present.

# Epigenetic Clocks

**"How old is this sample epigenetically?"** -> Apply a frozen elastic-net clock to the beta matrix, then report the age ACCELERATION (residual vs chronological age), not the raw age - because a clock is a predictor, and the residual is the signal.
- R: `DNAmAge(beta, clocks = c('Horvath', 'Hannum', 'Levine'), age = pheno$age)`

Scope: applying pre-trained clocks (DNAm age, pace, mitotic) and computing age acceleration from a clean beta/M-value matrix. Cell-count adjustment for IEAA -> cell-type-deconvolution. Clean beta matrix / EPICv2 replicate-probe collapse -> array preprocessing. Training a predictor / cross-validation / leakage -> machine-learning/model-validation. Survival/mortality modeling of EAA -> clinical-biostatistics/survival-analysis. Per-CpG and region testing -> differential-cpg-testing, dmr-detection.

## The Single Most Important Modern Insight -- A Clock Is a Predictor, Not a Mechanism, and Not Even a Reliable One Per-CpG

DNAm age is a frozen elastic-net weighted sum over CpGs that a penalty chose for out-of-sample prediction. The CpGs are prediction features, never an aging pathway. Four corollaries every common misuse violates:

1. **The CpG set is not biology.** Do not GO-enrich clock CpGs. Two clocks for the same outcome can share almost zero CpGs (the elastic net arbitrarily keeps one of many correlated predictors), so non-overlap is expected, not a contradiction.
2. **The endpoint is age ACCELERATION, not the raw age.** Raw DNAm age just recapitulates chronological age (r often > 0.9). The signal is the residual of DNAm age on chronological age (EAA); IEAA additionally residualizes on cell counts - which is exactly where deconvolution meets this skill.
3. **First-gen per-CpG reliability can be smaller than the effect being chased.** Many first-gen clock CpGs have low test-retest ICC (Sugden 2020 *Patterns* 1:100014), so the same sample can age several years between technical replicates. PC clocks (Higgins-Chen 2022 *Nat Aging* 2:644) exist specifically to fix this for longitudinal and trial use.
4. **Association is not causation is not transfer.** EAA associating with an exposure does not make the clock causal; a blood clock does not automatically work in another tissue or ancestry without a recalibration check.

Organize the analysis around defending these four, not around listing clock names.

## The Clock Menu by Question

The question dictates the clock; there is no single best clock. Pick by what is being predicted, not by popularity.

| Generation | Clock | Citation | Predicts | Tissue | Note |
|------------|-------|----------|----------|--------|------|
| 1st (chronological) | Horvath multi-tissue | Horvath 2013 *Genome Biol* 14:R115 | chronological age | 51 tissues | 353 CpGs; works cross-tissue; log-linear age transform for <20y |
| 1st | Hannum | Hannum 2013 *Mol Cell* 49:359 | chronological age | whole blood | 71 CpGs; tight in blood, poor cross-tissue |
| 1st | skin & blood | Horvath 2018 *Aging* 10:1758 | chronological age | skin, blood, fibroblasts | 391 CpGs; for in-vitro/fibroblast/skin work |
| 2nd (health-mortality) | PhenoAge | Levine 2018 *Aging* 10:573 | morbidity/mortality composite | blood | 513 CpGs; trained on a 9-biomarker phenotypic age |
| 2nd | GrimAge | Lu 2019 *Aging* 11:303 | lifespan/healthspan | blood | composite of DNAm protein surrogates; strongest mortality predictor |
| pace | DunedinPACE | Belsky 2022 *eLife* 11:e73420 | RATE of aging | blood | 173 CpGs; ~1.0 = one biological year per calendar year; NOT an age |
| pediatric | PedBE | McEwen 2020 *PNAS* 117:23329 | age 0-20 | buccal | buccal-specific |
| gestational | Knight / Bohlin | Knight 2016 *Genome Biol* 17:206 / Bohlin 2016 *Genome Biol* 17:207 | gestational age | cord blood | newborn GA estimation |
| mitotic | epiTOC | Yang 2016 *Genome Biol* 17:205 | cumulative stem-cell divisions | normal tissue | tracks mitotic, not chronological, age; cancer-risk relevant |

DunedinPACE is reported as the raw PACE value (already a rate); never residualize it like an age clock and never compare its number to Horvath years.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Chronological-age accuracy in blood | Hannum or Horvath | trained on chronological age; Hannum tighter in blood |
| Cross-tissue or non-blood sample | Horvath multi-tissue or skin&blood | only the multi-tissue clocks transfer; report a known-age check |
| Morbidity / mortality / healthspan endpoint | GrimAge (or PhenoAge) | second-gen; trained on health outcomes, not just age |
| Pace of aging / intervention sensitivity | DunedinPACE | a rate; sensitive to caloric-restriction-style trials |
| Longitudinal or clinical-trial endpoint | PC clocks (methylCIPHER) | first-gen test-retest noise can exceed the intervention effect |
| Pediatric buccal / newborn cord blood | PedBE / Knight or Bohlin | age-and-tissue-matched clocks |
| Cancer / mitotic-age question | epiTOC / epiTOC2 | estimates cell divisions, a different aging axis |
| EPICv2 data | clock that retains its CpGs (Horvath/PhenoAge) | GrimAge/Hannum/DunedinPACE lose >10% of CpGs on EPICv2 |
| Adjust EAA for cell composition (IEAA) | -> cell-type-deconvolution | residualize the clock on estimated cell counts |
| Train or validate a new predictor | -> machine-learning/model-validation | clocks here APPLY frozen models; they are not trained here |
| Survival/mortality model of EAA | -> clinical-biostatistics/survival-analysis | EAA-to-outcome modeling lives there |

## Apply a Clock and Extract Age Acceleration

**Goal:** Compute DNAm age for several clocks and turn the raw ages into age acceleration, the actual endpoint.

**Approach:** Run `DNAmAge` with chronological age supplied so it returns acceleration columns directly; `ageAcc` is the raw DNAm-minus-chronological difference and `ageAcc2` is the residual of DNAm age on chronological age (the EAA to test). Always check clock-CpG coverage first.

```r
library(methylclock)

cpg_report <- checkClocks(beta)        # which clock CpGs are missing BEFORE estimating
ages <- DNAmAge(beta, clocks = c('Horvath', 'Hannum', 'Levine', 'skinHorvath'),
                age = pheno$age,       # supplying age yields ageAcc and ageAcc2 columns
                cell.count = FALSE,    # set TRUE only when adjusting toward IEAA-style estimates
                min.perc = 0.8)        # refuse a clock missing >20% of its CpGs (default 0.8)
# ageAcc  = DNAm age - chronological age (raw difference)
# ageAcc2 = residual of DNAm age on chronological age = the EAA endpoint with cell.count=FALSE
#   (methylclock labels ageAcc2 "similar to IEAA"; confirm the exact column semantics in the
#    installed vignette, and the cell-count-adjusted residual when cell.count=TRUE)
```

The `dnaMethyAge` package returns acceleration in one call and exposes author-year clock IDs:

```r
library(dnaMethyAge)
availableClock()                                  # confirm the installed clock-name strings
phenoage <- methyAge(beta, clock = 'LevineM2018',
                     age_info = pheno,            # data.frame with Sample, Age (Sex for GrimAge variants)
                     fit_method = 'Linear')       # adds an Age_Acceleration column
```

## Pace of Aging Is Not an Age

**Goal:** Compute DunedinPACE as a rate and keep it on its own scale.

**Approach:** Use the dedicated package; the output is a per-sample pace (~1.0 = normal). Do not regress it on chronological age and do not merge it with age-clock acceleration.

```r
library(DunedinPACE)
pace <- PACEProjector(beta)   # returns the DunedinPACE pace values (~1.0 = normal, >1 = faster aging); report as-is
# Never residualize PACE on chronological age and never compare its value to Horvath years.
```

## Reliability and PC Clocks

For longitudinal, interventional, or clinical-trial endpoints, first-gen per-CpG noise (Sugden 2020) can swamp a small intervention effect. PC clocks (Higgins-Chen 2022) train the elastic net on principal components across thousands of CpGs, averaging out per-CpG noise and lifting test-retest ICC toward ~0.9. They live in methylCIPHER (MorganLevineLab), not in methylclock. Use a PC clock, or at minimum document an ICC/reliability assessment, for any repeated-measures design.

## Per-Method Failure Modes

### GO-enriching clock CpGs
**Trigger:** running pathway enrichment on a clock's CpG list to "explain aging." **Mechanism:** the CpGs are penalty-selected prediction features, one arbitrary representative per correlated cluster. **Symptom:** a plausible-looking enrichment that is an artifact of feature selection. **Fix:** do not enrich clock CpGs; treat them as predictors only.

### Reporting raw DNAm age instead of acceleration
**Trigger:** correlating raw DNAm age with an exposure. **Mechanism:** raw age is dominated by chronological age (r > 0.9). **Symptom:** every clock "associates" with age-correlated variables. **Fix:** test the residual (ageAcc2 / Age_Acceleration / IEAA), not the raw age.

### Missing clock CpGs mean-imputed
**Trigger:** a platform or failed probes drop clock CpGs; the tool imputes to the training mean. **Mechanism:** mean-imputation pulls the prediction toward the training population age and shrinks variance. **Symptom:** age acceleration biased toward zero; attenuated associations; on EPICv2 Hannum can return NEGATIVE ages. **Fix:** report the fraction of clock CpGs present (`checkClocks`); flag/refuse samples with high missingness; prefer a clock that retains its CpGs on the platform.

### EPICv2 replicate probes not collapsed
**Trigger:** feeding a raw EPICv2 matrix with suffixed replicate probe IDs. **Mechanism:** EPICv2 carries multiple beads per CpG with suffixed names, so the clock cannot find its CpGs. **Symptom:** huge apparent CpG dropout, nonsensical ages. **Fix:** collapse replicate probes to one value per CpG upstream before any clock call.

### First-gen clock used for a longitudinal endpoint
**Trigger:** detecting a small intervention effect with Horvath/Hannum across timepoints. **Mechanism:** per-CpG test-retest noise (Sugden 2020) rivals the effect. **Symptom:** unstable EAA between replicates; the effect is inside the noise band. **Fix:** PC clocks (methylCIPHER) or a documented reliability assessment.

### Cross-tissue or cross-ancestry application
**Trigger:** a blood-trained clock (Hannum) on saliva, or a European-cohort clock applied elsewhere. **Mechanism:** clocks do not automatically transfer. **Symptom:** a systematic age offset vs known age. **Fix:** use a tissue-appropriate clock (skin&blood, PedBE, gestational) and report a known-age calibration check.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Report fraction of clock CpGs present | Higgins-Chen 2022 *Nat Aging* 2:644 | high imputed fraction invalidates the estimate |
| `min.perc` >= 0.8 of clock CpGs | methylclock docs | below ~80% coverage mean-imputation dominates the prediction |
| EPICv2 dropout 3.5-32.6% per clock; GrimAge/Hannum/DunedinPACE > 10% | EPICv2 clock benchmarks | platform-specific; pick a CpG-retaining clock on EPICv2 |
| First-gen clock CpG ICC often < 0.5 | Sugden 2020 *Patterns* 1:100014 | technical noise rivals signal; use PC clocks for repeated measures |
| PC clock ICC ~0.9+ | Higgins-Chen 2022 *Nat Aging* 2:644 | the reliability bar for longitudinal/trial designs |
| EAA = residual of DNAm age on chronological age | Horvath 2013 *Genome Biol* 14:R115 | the endpoint; raw age is uninformative (r > 0.9 with chronological age) |
| Horvath age transform applied for age < 20 | Horvath 2013 *Genome Biol* 14:R115 | the clock is log-linear below 20y; do not compare pre/post-transform values |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Every clock correlates with an age-linked variable | testing raw DNAm age | test age acceleration (residual), not raw age |
| Hannum returns negative ages | EPICv2 clock-CpG dropout | use a CpG-retaining clock; report coverage; collapse replicate probes |
| Age acceleration shrunk toward zero | clock CpGs mean-imputed | report `checkClocks` coverage; refuse high-missingness samples |
| Many clock CpGs "missing" on EPICv2 | replicate probes not collapsed | collapse suffixed probes to one value per CpG upstream |
| DunedinPACE compared to Horvath years | mixing a rate with an age | keep PACE on its own scale; never residualize it |
| Unstable EAA across replicates | first-gen per-CpG noise | PC clocks (methylCIPHER) or a reliability assessment |
| `methyAge` clock name not found | wrong clock-ID string | `availableClock()` for installed author-year IDs |

## References

- Horvath S. 2013. DNA methylation age of human tissues and cell types. *Genome Biol* 14:R115.
- Hannum G, Guinney J, Zhao L, et al. 2013. Genome-wide methylation profiles reveal quantitative views of human aging rates. *Mol Cell* 49:359-367.
- Horvath S, Oshima J, Martin GM, et al. 2018. Epigenetic clock for skin and blood cells applied to Hutchinson Gilford Progeria Syndrome and ex vivo studies. *Aging (Albany NY)* 10:1758-1775.
- Levine ME, Lu AT, Quach A, et al. 2018. An epigenetic biomarker of aging for lifespan and healthspan. *Aging (Albany NY)* 10:573-591.
- Lu AT, Quach A, Wilson JG, et al. 2019. DNA methylation GrimAge strongly predicts lifespan and healthspan. *Aging (Albany NY)* 11:303-327.
- Belsky DW, Caspi A, Corcoran DL, et al. 2022. DunedinPACE, a DNA methylation biomarker of the pace of aging. *eLife* 11:e73420.
- McEwen LM, O'Donnell KJ, McGill MG, et al. 2020. The PedBE clock accurately estimates DNA methylation age in pediatric buccal cells. *PNAS* 117:23329-23335.
- Knight AK, Craig JM, Theda C, et al. 2016. An epigenetic clock for gestational age at birth based on blood methylation data. *Genome Biol* 17:206.
- Bohlin J, Haberg SE, Magnus P, et al. 2016. Prediction of gestational age based on genome-wide differentially methylated regions. *Genome Biol* 17:207.
- Yang Z, Wong A, Kuh D, et al. 2016. Correlation of an epigenetic mitotic clock with cancer risk. *Genome Biol* 17:205.
- Sugden K, Hannon EJ, Arseneault L, et al. 2020. Patterns of reliability: assessing the reproducibility and integrity of DNA methylation measurement. *Patterns (N Y)* 1:100014.
- Higgins-Chen AT, Thrush KL, Wang Y, et al. 2022. A computational solution for bolstering reliability of epigenetic clocks. *Nat Aging* 2:644-661.
- Pelegi-Siso D, de Prado P, Ronkainen J, et al. 2021. methylclock: a Bioconductor package to estimate DNA methylation age. *Bioinformatics* 37:1759-1760.

## Related Skills

- array-preprocessing - Provides the clean beta matrix clocks consume
- cell-type-deconvolution - IEAA: adjust age acceleration for cell composition
- machine-learning/model-validation - Predictor training, cross-validation, leakage (clocks apply frozen models)
- clinical-biostatistics/survival-analysis - Survival/mortality modeling of age acceleration
- ewas-design - Age-acceleration association study design
- workflows/methylation-pipeline - End-to-end methylation pipeline
<!-- END FILE: methylation-analysis/epigenetic-clocks/SKILL.md -->

## 子目录：methylation-analysis/ewas-design

<!-- BEGIN FILE: methylation-analysis/ewas-design/SKILL.md -->
---
name: bio-methylation-ewas-design
description: Designs and defends an epigenome-wide association study (EWAS) on 450K/EPIC array or bisulfite methylation - the layer deciding whether a hit is credible. Covers the confounding hierarchy (cell composition covariates as the dominant confounder, batch/Sentrix chip/array position, age/sex, smoking AHRR cg05575921, ancestry/mQTL, reverse causation), chip randomization (no-rescue theorem), surrogate variable analysis sva/SmartSVA, ComBat, RUVm, over-correction, genomic inflation lambda vs GWAS genomic control, BACON bias/inflation, genome-wide significance threshold 450K/EPIC, FWER vs FDR, pwrEWAS power, meta-analysis, EWAS Catalog/Atlas, methylation risk scores. Use when designing an EWAS, choosing a covariate set, randomizing a plate layout, interpreting lambda, applying BACON, setting a threshold, powering a study, or using an MRS. For the per-site test see differential-cpg-testing; for cell fractions see cell-type-deconvolution; for causal mQTL orientation see causal-genomics/mendelian-randomization.
tool_type: mixed
primary_tool: meffil
---

## Version Compatibility

Reference examples tested with: meffil 1.3+, sva 3.50+, bacon 1.30+, limma 3.58+, missMethyl 1.36+, pwrEWAS 1.16+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Two versions decide everything downstream. The ARRAY (450K vs EPIC v1 ~850K vs EPIC v2 ~935K) sets the CpG universe and therefore the effective number of tests and the genome-wide threshold - confirm against the current manifest before quoting a threshold. The CELL-TYPE REFERENCE panel must match the tissue and age (cord blood, adult blood, and tumor need different references); a mismatched reference silently biases the cell-fraction covariates. BACON slot names, pwrEWAS argument names, and sva method options have shifted across Bioconductor releases - check `?function` on the installed build.

# EWAS Design

**"Run an EWAS for my phenotype"** -> Build the covariate model and the chip randomization BEFORE the per-CpG test, because the confounders are larger than the signal - the p-value is the last and least interesting thing.
- R: `meffil.ewas(beta, variable, covariates=data.frame(age, sex, cellprops, chip, plate))` then BACON-correct the test statistics.

Scope: the design-and-inference layer of an EWAS - confounding, randomization, batch/SVA/RUV correction, genomic inflation/BACON, genome-wide thresholds, power, meta-analysis, replication, and methylation risk scores. The per-CpG test mechanics (beta vs M-value, limma) -> differential-cpg-testing. Cell-fraction estimation algorithms (Houseman/IDOL/EpiDISH) -> cell-type-deconvolution. Normalization internals (funnorm/noob) -> array-preprocessing. mQTL Mendelian randomization for causal orientation -> causal-genomics/mendelian-randomization. MRS weight-learning (penalized regression, nested CV) -> the machine-learning category.

## The Single Most Important Modern Insight -- An EWAS Hit Is a Cell-Composition Difference Until Proven Otherwise

The defining feature of the field is that the confounders are LARGER than the signal: a true effect is typically a sub-2% absolute methylation difference, while cell mix, batch, age, sex, smoking, and ancestry each move methylation 10-50%. An EWAS is therefore won or lost BEFORE the per-CpG test - in the chip randomization, the covariate set, and the replication cohort. Four corollaries, each of which a common misuse violates:

1. **Composition before regulation.** Whole blood is a leukocyte mixture; a CpG can be 90% methylated in granulocytes and 10% in lymphocytes. Any phenotype that shifts the mixture (age, inflammation, infection, stress, smoking, most diseases) produces methylation differences that are composition artifacts, not within-cell regulatory change. Cell-proportion covariates are mandatory, not optional; the default suspicion for any unadjusted hit is "a blood-count difference."
2. **Confounder > signal.** Design (randomization, matching) is the primary defense; statistical adjustment is the backstop. No analysis rescues a design that confounded chip/plate with phenotype at the bench.
3. **Blood is the lamppost, not the keys.** Blood is convenient; the disease tissue (brain, adipose, tumor) is usually inaccessible and weakly correlated (blood-brain mean r ~0.15, Hannon 2015). A blood EWAS for a brain trait tests a confounded surrogate, and a cross-sectional design cannot orient cause vs consequence (reverse causation).
4. **Discovery is a hypothesis; replication is the finding.** With tiny effects and pervasive confounding, a single-cohort genome-wide-significant CpG is a lead, not a result. The EWAS Catalog/Atlas exist so a "novel" hit can be checked against the generic age/smoking/cell-comp CpGs everyone finds.

Organize the analysis around defending these four, not around listing `sva`/`ComBat`/`bacon` functions.

## The Confounding Hierarchy (ordered by damage, not convenience)

| Rank | Confounder | Why it dominates | Defense | Owner |
|------|-----------|------------------|---------|-------|
| 1 | Cell composition | Each leukocyte has a radically different methylome; any mixture shift is a fake signal | Estimate cell fractions and ALWAYS adjust | -> cell-type-deconvolution (estimation); decide here |
| 2 | Batch / Sentrix chip / array position / plate / scan date | EPIC runs 8 samples per BeadChip (450K: 12); position and chip imprint methylation | Randomize at design time; then SVA/RUVm/ComBat + chip/position covariates | here + array-preprocessing |
| 3 | Age and sex | Age is the most reproducible methylome correlate (the clock); sex drives X/Y and X-inactivation | Always include; analyze sex chromosomes separately; sex is a mislabel QC check | here |
| 4 | Smoking | Largest reproducible blood exposure signature; confounds half of all health phenotypes | Adjust (methylation smoking score > self-report); AHRR cg05575921 is the positive control | here |
| 5 | Genetic / ancestry / mQTL | Many CpGs are under genetic control; population structure confounds like GWAS | Genetic PCs; analyze within ancestry; drop SNP-affected/cross-reactive probes | here + array-preprocessing |
| 6 | Reverse causation / tissue relevance | Cross-sectional methylation may be a consequence, not a cause; blood != disease tissue | Prospective/longitudinal or MZ-discordant design; cross-tissue concordance | here; causal -> causal-genomics/mendelian-randomization |

Default covariate set for a blood EWAS: age, sex, cell proportions, chip/position (or SVs), and where relevant genetic PCs and a smoking score. The omission of any one is the most common EWAS error.

## Design Beats Correction -- The No-Rescue Theorem

If all cases ran on chip A and all controls on chip B, batch and phenotype are inseparable - ComBat will remove the batch AND the signal, or preserve a spurious one. No statistical adjustment recovers a confounded design (general principle: experimental-design/batch-design).

**Goal:** Make technical batch orthogonal to phenotype before any sample touches the array.

**Approach:** Randomize (or block) sample-to-chip, sample-to-position, and sample-to-plate assignment so case/control, age, and sex are balanced across chips; reserve no chip for one group. This single uncorrectable decision matters more than every analysis choice that follows.

```r
# Stratified randomization of samples to 8-position EPIC BeadChips (450K: 12), balancing case/control per chip
meta$chip <- NA_integer_
for (grp in split(seq_len(nrow(meta)), meta$case)) {
  meta$chip[sample(grp)] <- rep(seq_len(ceiling(length(grp) / 4)), each = 4, length.out = length(grp))
}
# Then interleave the two case groups across chips so no chip is single-group; verify balance:
with(meta, table(chip, case))   # every chip should hold both groups
```

## Batch / SVA / RUV Correction (and the over-correction trap)

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| sva | Leek & Storey 2007 *PLoS Genet* 3:e161 | latent surrogate variables built orthogonal to the variable of interest | reference-free soak-up of cell mix + unknown batch |
| SmartSVA | Chen 2017 *BMC Genomics* 18:413 | order-of-magnitude-faster SVA with explicit convergence | the de-facto EWAS SVA for large cohorts |
| ComBat | Johnson 2007 *Biostatistics* 8:118 | empirical-Bayes removal of a SPECIFIED batch (chip/plate) | known, labelled batch; protect biology via `mod=` |
| RUVm | Maksimovic 2015 *Nucleic Acids Res* 43:e106 | two-stage RUV-inverse using Illumina's ~600 negative control probes | array EWAS; estimates unwanted variation from control probes |
| funnorm | Fortin 2014 *Genome Biol* 15:503 | control-probe PCA at the normalization stage | fix unwanted variation BEFORE testing (-> array-preprocessing) |

The central tension: cell-composition and technical variation MUST be removed, but aggressive correction removes REAL biology when the unwanted variation overlaps the phenotype. Every tool above can erase a true effect.

**The positive-control check (the pragmatic referee).** Monitor a known signal through correction. In a blood EWAS containing smokers, smoking->cg05575921 (AHRR, ~18% hypomethylation, Joehanes 2016) MUST survive. If adding surrogate variables makes the QQ plot look clean BUT kills AHRR, the pipeline is over-corrected. A clean QQ with a dead positive control is a broken pipeline, not a good one. Do not keep adding SVs until lambda hits 1.0.

ComBat and limma/EWAS modeling run on M-values (logit of beta), not betas (betas are bounded [0,1] and heteroscedastic); effect sizes are reported back on the beta / delta-beta scale for interpretability. Pass the biological covariate to ComBat's `mod=` so it is protected. sva: pass the FULL model (`mod`, including the variable of interest) AND the null model (`mod0`) so SVs are orthogonal to the phenotype; choose the number with `num.sv(method='be')`.

## Genomic Inflation and BACON -- Why GWAS Intuition Fails

Lambda (the genomic inflation factor) = median observed chi-square / expected median. In GWAS, lambda > 1 signals stratification and is corrected by genomic control (divide all statistics by lambda). This reasoning is WRONG for EWAS:

1. EWAS statistics are routinely BOTH inflated AND deflated for non-GWAS reasons - residual cell-composition variation, the strong correlation among CpGs, un-modeled technical variation, and the fact that a strong exposure (smoking) genuinely associates with a large fraction of the genome (real signal that legitimately inflates lambda). A lambda of 1.2 may be real biology in a smoking EWAS and cell-composition leakage in an under-powered case-control study - the SAME number means different things.
2. Genomic control assumes a single multiplicative inflation on a mostly-null genome and ignores BIAS (a systematic mean shift off zero). EWAS violates all three assumptions.

**BACON (van Iterson 2017 *Genome Biol* 18:19)** fits a Bayesian Gaussian mixture to the observed test statistics, estimates the empirical-null distribution, and reports BOTH a bias (mean shift) AND an inflation (scale) - then standardizes statistics against that empirical null without assuming the genome is mostly null. Report lambda but correct with BACON; show QQ plots before and after. Caveat: BACON can over-deflate a highly polygenic exposure if the alternative component is large - apply it with the QQ plot, not as a reflex.

## Genome-Wide Thresholds and the FWER-vs-FDR Decision

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| 450K: P < 2.4e-7 | Saffari 2018 *Genet Epidemiol* 42:20 | empirical effective-test FWER 5%; ~210,000 effective tests (< probe count due to correlation) |
| EPIC v1: P < 9e-8 | Mansell 2019 *BMC Genomics* 20:366 | null-simulation FWER 5% for the ~850K EPIC array |
| Pragmatic 1e-7 | community | round number between the two array-specific values |
| FDR (BH) q < 0.05 | Benjamini-Hochberg | more powerful; discovery / exposure scans; report as a sensitivity layer |

Naive Bonferroni on the probe count is over-conservative because CpGs are correlated (co-methylation, shared mQTLs); raw p is anti-conservative because there are ~850K tests. Use the array-specific FWER threshold for the cross-study-comparable headline claim and the EWAS Catalog; use BH-FDR for hypothesis-generating discovery. BH's independence assumption is imperfect under probe correlation but robust to positive dependence. Region-level (DMR) multiple-testing is owned by dmr-detection; mechanical p.adjust is owned by differential-cpg-testing. EPIC v2 (~935K probes, renamed/dropped vs v1) may shift the threshold - verify against the manifest.

## Power and Meta-Analysis

**Goal:** Size an EWAS for a realistic (tiny) effect using site-specific methylation variance, not a single assumed sd.

**Approach:** pwrEWAS (Graw 2019 *BMC Bioinformatics* 20:218) simulates DNAm using empirical per-CpG variance from a reference dataset, so power reflects the real site-specific variance structure (bimodal sites near 0/1 behave differently from intermediate sites). Specify target delta-beta, sample size, and the genome-wide threshold; expect to need hundreds-to-thousands of samples for a 1-2% effect - which is why meta-analysis dominates.

EWAS meta-analysis is the field standard for power: each cohort runs an identical pre-specified pipeline (meffil enables this), BACON-corrects per cohort, uploads summary statistics, and a central site does fixed-effect inverse-variance pooling with heterogeneity testing (Cochran's Q, I^2). meffil's distinguishing feature is distributed normalization - cohorts normalize locally without sharing individual data, reducing meta-analysis heterogeneity - plus automated selection of the number of normalization PCs.

## Study Designs

| Design | Controls for | Cost |
|--------|--------------|------|
| Case-control (cross-sectional) | nothing inherently; adjust on age/sex/ancestry/cell-mix, randomize chips | reverse causation, composition confounding |
| Longitudinal / prospective | reverse causation (methylation measured before outcome); within-person change via mixed model | needs follow-up; repeated samples |
| MZ-discordant twin | genetic + shared-environment confounding by design (paired within-pair analysis) | discordant pairs are rare -> power-limited |
| Exposure EWAS | smoking is the template/positive-control | exposure misclassification (self-report) |
| Meta-analysis | low power of single cohorts | requires harmonized pipelines + BACON per cohort |

## Replication and Look-Up

Replication is the real significance bar. After discovery, triage every hit against both databases - a "novel" CpG that is in fact a top smoking/age/blood-cell CpG is almost certainly residual confounding.

- **EWAS Catalog** (Battram 2022 *Wellcome Open Res* 7:41; ewascatalog.org) - published associations at P < 1e-4 (so a Catalog "hit" is a lookup, not a genome-wide claim) plus de-novo EWAS; check whether a CpG was reported for any trait.
- **EWAS Atlas / Open Platform** (Li 2019 *Nucleic Acids Res* 47:D983) - curated associations with a trait-ENRICHMENT tool for interpreting a CpG set.

## Methylation Risk Scores (MRS)

An EWAS produces per-CpG associations; an MRS turns many of them into one number - a weighted CpG sum, MRS = sum_j w_j * beta_ij, with weights from a training EWAS or a penalized fit. It is the methylation analogue of a polygenic risk score (PRS), and an epigenetic clock is the age/health special case (-> epigenetic-clocks).

**The load-bearing distinction from a PRS.** A PRS sums germline variants - fixed at conception, antecedent, plausibly causal. An MRS sums methylation - modifiable, tissue/time-specific, and frequently a CONSEQUENCE of the exposure/trait rather than a cause. The methylation smoking score (Elliott 2014 *Clin Epigenetics* 6:4; generalized by Sugden 2019) does not predict a propensity to smoke; it MEASURES the footprint smoking left. So an MRS is reverse-causal-by-default: report it as a predictive BIOMARKER / objective exposure proxy, and reserve "risk" and "cause" for prospectively- or MR-supported claims. PRS = germline cause; MRS = state consequence.

The most useful design role is as a better-measured confounder: self-reported smoking is biased and coarse, so adjusting an EWAS for the methylation smoking score controls residual smoking confounding far better whenever the phenotype is smoking-correlated (caveat: if smoking is on the causal path, over-adjusting via the score removes real signal - the same confounder-vs-mediator tension as cell composition). Other DNAm scores exist for BMI/alcohol/education (McCartney 2018) and circulating proteins (EpiScores, Gadd 2022 *eLife* 11:e71802). Portability fails across array (450K vs EPIC drop CpGs), tissue, and ancestry - report how many score CpGs are present on the array. Defer MRS weight-learning (penalized regression, nested CV, calibration, leakage) to the machine-learning category; an MRS validated in its own training cohort is not validated.

## Per-Method Failure Modes

### EWAS without cell-composition covariates
**Trigger:** running the regression on whole-blood betas with no cell-fraction adjustment. **Mechanism:** any phenotype that shifts the leukocyte mixture moves methylation 10-50%. **Symptom:** the top hits are known granulocyte/lymphocyte-proportion CpGs. **Fix:** estimate cell proportions (-> cell-type-deconvolution) and always include them; treat any unadjusted hit as composition until shown otherwise.

### Chip/plate confounded with phenotype, then "fixed" by ComBat
**Trigger:** all cases on chip A, controls on chip B. **Mechanism:** batch and phenotype are inseparable. **Symptom:** ComBat removes the signal or fabricates one; no error. **Fix:** randomize sample-to-chip/position at design time - this is uncorrectable after the bench.

### GWAS genomic control applied to EWAS
**Trigger:** dividing all test statistics by lambda. **Mechanism:** assumes single multiplicative inflation on a mostly-null genome and ignores bias. **Symptom:** real polygenic signal (smoking) deflated or residual confounding under-corrected. **Fix:** use BACON to estimate empirical-null bias AND inflation.

### Over-correction with too many surrogate variables
**Trigger:** adding SVs/PCs until lambda hits 1.0. **Mechanism:** latent factors correlated with the phenotype deflate true signal. **Symptom:** clean QQ but the positive control (AHRR) is gone. **Fix:** monitor cg05575921 through correction; stop when adding SVs starts killing it.

### Bonferroni-on-probe-count or raw-p reporting
**Trigger:** 0.05/850000, or reporting nominal p. **Mechanism:** probe correlation makes Bonferroni too strict; ignoring 850K tests is too loose. **Symptom:** missed real hits or a flood of false ones. **Fix:** array-specific FWER threshold (2.4e-7 / 9e-8) for claims, BH-FDR for discovery.

### Blood EWAS interpreted as disease-tissue mechanism
**Trigger:** a blood EWAS for a brain/adipose/tumor phenotype read as tissue biology. **Mechanism:** blood-brain methylation r ~0.15. **Symptom:** hits with no plausible blood mechanism. **Fix:** justify tissue relevance (BECon/blood-brain tools); frame blood as a biomarker, not mechanism, unless the CpG is cross-tissue concordant.

### MRS treated as a germline-like risk score
**Trigger:** describing a DNAm score for a disease as "risk" like a PRS. **Mechanism:** methylation is modifiable and frequently downstream. **Symptom:** a "DNAm risk score" that is actually the footprint of disease/treatment/behavior. **Fix:** call it a predictive biomarker; orient cause vs consequence only with prospective or MR evidence.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| 450K genome-wide P < 2.4e-7 | Saffari 2018 *Genet Epidemiol* 42:20 | empirical effective-test FWER 5% (~210,000 effective tests) |
| EPIC genome-wide P < 9e-8 | Mansell 2019 *BMC Genomics* 20:366 | null-simulation FWER 5% for ~850K EPIC |
| BH-FDR q < 0.05 | Benjamini-Hochberg | discovery / exposure scans; report alongside FWER |
| AHRR cg05575921 ~18% hypomethylation in smokers | Joehanes 2016 *Circ Cardiovasc Genet* 9:436 | the canonical positive control; must survive correction |
| EWAS Catalog inclusion P < 1e-4 | Battram 2022 *Wellcome Open Res* 7:41 | a Catalog entry is a lookup, not a genome-wide claim |
| Detect 1-2% delta-beta -> hundreds-to-thousands of samples | pwrEWAS, Graw 2019 | tiny site-specific effects drive the field to meta-analysis |
| Run ComBat/limma on M-values, report delta-beta | Du 2010 *BMC Bioinformatics* 11:587 | betas are bounded/heteroscedastic; M-values stabilize variance |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Top hits are blood-cell CpGs | no cell-composition covariates | estimate and adjust cell fractions |
| ComBat removed the signal | batch confounded with phenotype | randomize at design time; cannot fix after |
| Lambda misread as pass/fail | GWAS dogma applied to EWAS | pair lambda with QQ shape + positive control; correct with BACON |
| Clean QQ but AHRR gone | over-correction with too many SVs | stop adding SVs when the positive control dies |
| Threshold flood or famine | Bonferroni-on-probe-count or raw p | use array-specific FWER / BH-FDR |
| "Novel" CpG is a known generic hit | no Catalog/Atlas triage | look up the CpG before claiming novelty |
| MRS called a risk score | PRS connotations on modifiable methylation | report as biomarker; orient cause only with prospective/MR design |

## References

- van Iterson M, van Zwet EW, Heijmans BT; BIOS Consortium. 2017. Controlling bias and inflation in epigenome- and transcriptome-wide association studies using the empirical null distribution. *Genome Biol* 18:19.
- Saffari A, Silver MJ, Zavattari P, et al. 2018. Estimation of a significance threshold for epigenome-wide association studies. *Genet Epidemiol* 42:20-33.
- Mansell G, Gorrie-Stone TJ, Bao Y, et al. 2019. Guidance for DNA methylation studies: statistical insights from the Illumina EPIC array. *BMC Genomics* 20:366.
- Leek JT, Storey JD. 2007. Capturing heterogeneity in gene expression studies by surrogate variable analysis. *PLoS Genet* 3:e161.
- Chen J, Behnam E, Huang J, et al. 2017. Fast and robust adjustment of cell mixtures in epigenome-wide association studies with SmartSVA. *BMC Genomics* 18:413.
- Johnson WE, Li C, Rabinovic A. 2007. Adjusting batch effects in microarray expression data using empirical Bayes methods. *Biostatistics* 8:118-127.
- Maksimovic J, Gagnon-Bartsch JA, Speed TP, Oshlack A. 2015. Removing unwanted variation in a differential methylation analysis of Illumina HumanMethylation450 array data. *Nucleic Acids Res* 43:e106.
- Min JL, Hemani G, Davey Smith G, Relton C, Suderman M. 2018. Meffil: efficient normalization and analysis of very large DNA methylation datasets. *Bioinformatics* 34:3983-3989.
- Graw S, Henn R, Thompson JA, Koestler DC. 2019. pwrEWAS: a user-friendly tool for comprehensive power estimation for epigenome wide association studies (EWAS). *BMC Bioinformatics* 20:218.
- Joehanes R, Just AC, Marioni RE, et al. 2016. Epigenetic Signatures of Cigarette Smoking. *Circ Cardiovasc Genet* 9:436-447.
- Elliott HR, Tillin T, McArdle WL, et al. 2014. Differences in smoking associated DNA methylation patterns in South Asians and Europeans. *Clin Epigenetics* 6:4.
- Gadd DA, Hillary RF, McCartney DL, et al. 2022. Epigenetic scores for the circulating proteome as tools for disease prediction. *eLife* 11:e71802.
- McCartney DL, Hillary RF, Stevenson AJ, et al. 2018. Epigenetic prediction of complex traits and death. *Genome Biol* 19:136.
- Battram T, Yousefi P, Crawford G, et al. 2022. The EWAS Catalog: a database of epigenome-wide association studies. *Wellcome Open Res* 7:41.
- Li M, Zou D, Li Z, et al. 2019. EWAS Atlas: a curated knowledgebase of epigenome-wide association studies. *Nucleic Acids Res* 47:D983-D988.
- Hannon E, Lunnon K, Schalkwyk L, Mill J. 2015. Interindividual methylomic variation across blood, cortex, and cerebellum. *Epigenetics* 10:1024-1032.
- Michels KB, Binder AM, Dedeurwaerder S, et al. 2013. Recommendations for the design and analysis of epigenome-wide association studies. *Nat Methods* 10:949-955.

## Related Skills

- differential-cpg-testing - The per-site test this design layer feeds
- cell-type-deconvolution - Cell-fraction covariates (the dominant confounder)
- array-preprocessing - Normalization choice (funnorm) vs model-level batch correction
- array-qc-filtering - Probe filtering and chip/position batch diagnosis
- causal-genomics/mendelian-randomization - mQTL-based causal orientation (reverse causation)
- experimental-design/batch-design - General randomization and batch-design principles
- clinical-biostatistics/multiplicity-graphical - FWER for confirmatory trials (contrast with discovery FDR)
- workflows/methylation-pipeline - End-to-end pipeline
<!-- END FILE: methylation-analysis/ewas-design/SKILL.md -->

## 子目录：methylation-analysis/methylation-calling

<!-- BEGIN FILE: methylation-analysis/methylation-calling/SKILL.md -->
---
name: bio-methylation-calling
description: Extracts per-cytosine methylation calls from aligned bisulfite/EM-seq reads with bismark_methylation_extractor (Bismark BAM) or the aligner-agnostic MethylDackel/BISCUIT (bwa-meth BAM), producing the beta value M/(M+U) as a coverage file, bedGraph, or genome-wide cytosine report across CpG/CHG/CHH context. Covers conversion-rate QC as the first gate, the 5mC vs 5hmC summed caveat, variant-aware calling so a C/T SNP does not masquerade as unmethylation, paired-end --no_overlap double-counting, symmetric CpG dyad collapse, and the 0-based vs 1-based coordinate trap. Use when extracting methylation levels from a bisulfite/EM-seq alignment, choosing an extractor for a non-Bismark BAM, QC-ing conversion efficiency, or producing coverage/cytosine-report input for testing. For long-read MM/ML modification calling see long-read-sequencing/nanopore-methylation; for the upstream BAM see bismark-alignment; for per-CpG statistics see differential-cpg-testing.
tool_type: cli
primary_tool: Bismark
---

## Version Compatibility

Reference examples tested with: Bismark 0.24+, MethylDackel 0.6+, samtools 1.19+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The extractor must match the aligner: bismark_methylation_extractor reads Bismark's own XM call string and CANNOT process a bwa-meth BAM (no XM tag); MethylDackel and BISCUIT recompute the call from BAM + reference and are aligner-agnostic. The genome FASTA build (hg38 vs T2T-CHM13) defines every coordinate downstream, and BISCUIT/Bis-SNP need a SNP-aware reference workflow. Always run `<tool> --help` on the installed build before quoting a default; MethylDackel `--maxVariantFrac` and EM-seq end-trim recommendations have no universal value.

# Methylation Calling

**"Get methylation levels from my bisulfite BAM"** -> Count converted-vs-unconverted bases at each reference cytosine and divide - because a methylation level is a per-cytosine COUNT RATIO, not a measurement, and every number is hostage to conversion completeness, SNPs, overlap, and the 5mC/5hmC conflation.
- CLI (Bismark BAM): `bismark_methylation_extractor -p --comprehensive --bedGraph --cytosine_report --genome_folder genome/ sample_pe.bam`
- CLI (bwa-meth BAM): `MethylDackel extract --mergeContext ref.fa sample.bam`

Scope: per-cytosine M/U counting from a short-read bisulfite/EM-seq/TAPS alignment, the conversion/M-bias/variant QC gates, and the coverage/cytosine-report handoff. Native long-read MM/ML modification calling -> long-read-sequencing/nanopore-methylation. The aligned BAM -> bismark-alignment. Per-CpG statistics on the counts -> differential-cpg-testing. Region calling -> dmr-detection. Array (EPIC/450K) beta-from-intensity is a different readout entirely and is not this skill.

## The Single Most Important Modern Insight -- A Methylation Level Is a Count Ratio, Not a Measurement

The extractor does not measure methylation. Bisulfite/EM-seq turns an epigenetic state into a sequence state (an unmethylated C converts to T; a methylated C stays C), and the extractor tallies, at each reference cytosine, M reads that show C and U reads that show T, then reports `beta = M / (M + U)`. Every beta is therefore hostage to four upstream choices the extractor cannot fix:

1. **Whether conversion was complete.** An unconverted unmethylated C is byte-for-byte identical to a methylated C, so incomplete conversion inflates EVERY beta and is invisible per-site. It must be measured globally before any beta is trusted (CHH rate or a lambda spike-in).
2. **Whether a C/T SNP is hiding as unmethylation.** The reference says C, the sample carries a T allele, the read shows T, and the extractor scores "converted" = unmethylated. Polymorphic CpGs are silently miscalled and can fabricate SNP-driven DMRs.
3. **Whether the paired-end overlap was double-counted.** A cytosine in the R1/R2 overlap is one molecule observed twice; counting both votes inflates coverage and biases beta when the mates disagree.
4. **Whether "5mC" is actually 5mC+5hmC.** 5hmC is also protected from conversion, so a standard WGBS/EM-seq beta is the SUM 5mC+5hmC. In brain/ESC/liver this is a real misattribution that no extractor flag can undo.

Organize the analysis around defending these four (conversion QC -> overlap -> M-bias -> variant-awareness -> what context/chemistry am I even calling), not around listing flags. And one deeper caveat: beta is itself a lossy average - collapsing reads to a `.cov` matrix discards the read-level epiallele, the strand (hemimethylation), and the allele (ASM); see the last sections.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| bismark_methylation_extractor | Krueger & Andrews 2011 *Bioinformatics* 27:1571 | reads Bismark's own XM call string; ecosystem standard | input is a Bismark BAM; want the genome-wide cytosine report / methylKit `.cov`; plant `--CX` |
| MethylDackel | github.com/dpryan79/MethylDackel (no journal) | recomputes calls from BAM + reference; fast; aligner-agnostic | bwa-meth BAM; want built-in M-bias `--OT/--OB` bounds and `--maxVariantFrac` SNP guard |
| BISCUIT | github.com/huishenlab/biscuit (no journal) | aligner + JOINT methylation/SNP/ASM caller; VCF + epiBED | human population / allele-specific work needing SNP-aware betas |
| Bis-SNP | Liu 2012 *Genome Biol* 13:R61 | Bayesian joint genotype + methylation | the original SNP-aware caller; mask C/T SNPs from betas |
| methylpy | github.com/yupenghe/methylpy (no journal) | allc format + binomial methylated-flag | the allc / ALLCools ecosystem; built-in per-site significance |
| asTair | bitbucket.org/bsblabludwig/astair (no journal) | polarity-aware caller (mCtoT / CtoT) | TAPS data (inverted polarity); explicit per-context stats |

EM-seq extraction arithmetic is identical to bisulfite (unmodified C reads as T either way) - the same Bismark/MethylDackel command works. TAPS INVERTS the polarity (modified C->T), so a bisulfite extractor reports 1-beta; use ASTAIR `--mod_mapping mCtoT`.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Bismark-aligned BAM, mammalian CpG | `bismark_methylation_extractor -p --comprehensive --cytosine_report` | reads the XM tag; cytosine report is the bsseq/methylKit input |
| bwa-meth-aligned WGBS/EM-seq | `MethylDackel extract --mergeContext` | bismark extractor cannot read a bwa-meth BAM (no XM tag) |
| Human population / polymorphic CpGs / ASM | BISCUIT (or Bis-SNP) | joint SNP+methylation; C/T SNP recognized as a variant, not unmethylation |
| Plant methylome (CHG/CHH real) | `--CX` (Bismark) / `--CHG --CHH` (MethylDackel) + lambda spike-in | non-CpG is biology; CHH-as-conversion-proxy fails |
| TAPS data | ASTAIR `--mod_mapping mCtoT` | polarity inverted; a bisulfite extractor reports 1-beta |
| Need 5hmC resolved from 5mC | second chemistry (oxBS/TAB/ACE) -> route, not a flag | WGBS/EM-seq sums them; the extractor cannot split |
| Read-level heterogeneity / clonality / cfDNA | keep reads (epiread/epiBED), do NOT collapse to `.cov` | the epiallele dies in the per-CpG average |
| Long-read modBAM with MM/ML tags | -> long-read-sequencing/nanopore-methylation | native modification tags, not conversion counting |

## Conversion-Rate QC -- the First Gate

**Goal:** Reject a methylome whose betas are inflated by incomplete conversion before computing anything.

**Approach:** Measure non-conversion globally, two ways. In mammals, genome-wide CHH methylation is near-zero biology, so the observed CHH rate IS the non-conversion rate (~2% CHH implies ~98% conversion). Where non-CpG methylation is real (plants, ESCs, neurons - Schultz 2015), spike in unmethylated lambda phage DNA and align to it: all its cytosines are unmethylated, so its observed "methylation" is the non-conversion rate. Require conversion >=99% (community convention; Shirane 2013 is a representative source). Extract CHH at least once even for a CpG-only mammalian study, purely for this number.

```bash
# Bismark: extract all contexts, then read the CHH methylation rate from the splitting report
bismark_methylation_extractor -p --comprehensive --CX --genome_folder genome/ sample_pe.bam
# The *_splitting_report.txt prints C methylated in CHH context %; (100 - that) ~ conversion efficiency in mammals.

# Lambda spike-in (the gold standard, mandatory in plants/ESC/neurons):
# align to the lambda genome, extract, and treat its global methylation as the non-conversion rate.
bismark --genome lambda_genome/ -1 R1.fq.gz -2 R2.fq.gz -o lambda_qc/
```

MethylDackel `--minConversionEfficiency` can additionally drop individual reads whose own conversion (from non-CpG Cs) is too low - a per-read complement to the global gate, not a replacement for it.

## Extract from a Bismark BAM

```bash
bismark_methylation_extractor \
    -p \                                # paired-end (--no_overlap is ON BY DEFAULT for -p)
    --comprehensive \                   # merge OT/OB/CTOT/CTOB into one file per context
    --bedGraph --cytosine_report \      # coverage/bedGraph + genome-wide every-C report
    --genome_folder genome/ \           # MANDATORY for --cytosine_report (scans the FASTA for all Cs)
    --ignore_r2 2 \                     # trim R2 5' end-repair artifact (set from M-bias; near-universal for EM-seq/PBAT)
    --parallel 4 --gzip \
    -o methylation/ sample_pe.bam
# Outputs: sample_pe.bismark.cov.gz (1-BASED), sample_pe.bedGraph.gz (0-BASED), sample_pe.CpG_report.txt.gz (1-BASED).
```

Collapse the symmetric CpG dyad with `coverage2cytosine --merge_CpG` (NOT `--merge_non_CpG`, which merges the CHG+CHH files). `--merge_CpG` adds the + strand C at position p and the - strand C at p+1 into one dyad entry, doubling effective coverage; it is CpG-only and incompatible with `--CX`.

## Extract from a bwa-meth BAM (MethylDackel)

```bash
MethylDackel mbias ref.fa sample.bam mbias_prefix   # inspect the SVGs; it SUGGESTS --OT/--OB bounds (do NOT accept blindly)
MethylDackel extract \
    --mergeContext \                   # collapse the symmetric CpG dyad (the MethylDackel equivalent of --merge_CpG)
    --maxVariantFrac 0.25 \            # exclude a C if the opposite-strand non-G fraction exceeds this (cheap SNP guard)
    --OT 3,0,0,98 --OB 3,0,0,98 \     # inclusion bounds from mbias: first/last bp to keep on read1,read2
    ref.fa sample.bam
# Output sample_CpG.bedGraph is 0-BASED, half-open: chr start end round(%meth) count_M count_U. CpG ONLY by default;
# add --CHG --CHH for plants. Default --minDepth 1, -q (MAPQ) 10, -p (Phred) 5.
```

## Coverage, Precision, and the Handoff -- Pass Counts, Not Betas

A beta is a binomial proportion: at coverage n its granularity is 1/n and its SE is ~sqrt(beta(1-beta)/n). At n=1 beta is only 0 or 1; at n=4 it lands on {0,.25,.5,.75,1}. A 1/2 site and a 50/100 site both read beta=0.5 but carry wildly different evidence. The extractors impose no biological floor (MethylDackel `--minDepth` and Bismark `.cov` both default to >=1). Do NOT pre-threshold to a single beta and t-test it - that discards the coverage information. Hand the COUNT data (M and total) forward; the downstream DMR callers (DSS/methylKit/bsseq) model the beta-binomial and USE n. A common per-CpG floor is >=10x AFTER symmetric merge, but it is a tradeoff (site count vs precision), not a magic constant.

## 5mC vs 5hmC and the Oxidation Cascade -- a Chemistry Decision, Not a Flag

Standard bisulfite AND standard EM-seq protect BOTH 5mC and 5hmC from conversion, so the "methylated" bin is 5mC+5hmC, never 5mC alone. Worse, bisulfite DEAMINATES the downstream TET-oxidation products 5fC and 5caC, so they read as T and land in the "unmethylated" bin - both bins are biochemically impure at TET-active loci (ESC, early embryo, neurons, some tumors). The full cascade is 5mC -> 5hmC -> 5fC -> 5caC. Resolving any derivative requires a SECOND wet-lab chemistry, not an extractor flag: 5hmC via oxBS-seq (Booth 2012; 5hmC = BS - oxBS by subtraction), TAB-seq (Yu 2012; direct 5hmC), or ACE-seq (Schutsky 2018; enzymatic, low-input); the bisulfite-free TAPS (Liu 2019) sidesteps the harsh chemistry but inverts polarity. Never let a plain WGBS/EM-seq beta be labeled "5mC" or its complement "unmodified C."

## Read-Level Heterogeneity -- the Epiallele Dies in the Average

beta=0.5 is consistent with three opposite biologies that beta cannot distinguish: a 50/50 mixture of fully-methylated and fully-unmethylated cells, every cell ~50% methylated with CpGs scattered differently per molecule (stochastic disorder), or a true uniform intermediate. The discriminator lives in the JOINT CpG pattern on a single read - intramolecular co-methylation - which the per-CpG average integrates out. Read-level metrics (PDR, Landau 2014; epipolymorphism, Landan 2012; methylation entropy; MHL for cfDNA tissue-of-origin, Guo 2017; FDRP/qFDRP) measure clonal/epigenetic instability and power liquid-biopsy deconvolution, and they require a READ-PRESERVING format (BISCUIT epiread/epiBED or the raw BAM) plus tools like Metheor or methclone - none of which are extractors. The moment the pipeline collapses to a `.cov` beta matrix, the epiallele is gone. If the question is heterogeneity, clonality, or cfDNA deconvolution, do NOT collapse to beta; this deeper analysis may warrant its own workflow, but at minimum the calling stage must flag that beta discards it.

## Hemimethylation and Allele-Specific Methylation -- two more things the average hides

**Hemimethylation (the strand axis).** `--merge_CpG` / `--mergeContext` is not a neutral coverage optimization: it bakes in the assumption that the two strands of a dyad agree and silently zeroes the hemimethylation channel (one strand methylated, the other not). Hemimethylation is real biology - the obligate post-replication maintenance intermediate, and a stable heritable mark at CTCF/cohesin sites required for chromatin looping (Xu & Corces 2018). Default destranding ON for bulk symmetric-CpG DMR work; turn it OFF (strand-specific extraction) and budget high per-strand coverage the moment strand asymmetry is the question. Per-molecule dyad state needs hairpin-bisulfite (Laird 2004).

**Allele-specific methylation (the allele axis).** The same C/T SNP that corrupts a beta (insight #2) becomes the measurement axis once reads are phased: assign each read's methylation to the SNP allele it carries and compare beta per allele (BISCUIT `epiread -B snps.bed` then `biscuit asm`; or Bis-SNP). The headline trap: a stable ~50% beta at a KNOWN imprinted control region (H19/IGF2, KCNQ1OT1, SNRPN, GNAS, MEG3) is NOT intermediate methylation and NOT a conversion artifact - it is two superimposed monoallelic states (one allele ~100%, one ~0%) averaged into a deceptive midpoint, a signature to PHASE, not a value to model. Sequence-dependent ASM is the mQTL bridge to causal-genomics/mendelian-randomization; produce the allele-phased betas here, do the colocalization there.

## Per-Method Failure Modes

### No conversion-rate gate
**Trigger:** reporting betas without checking CHH rate or a lambda spike-in. **Mechanism:** an unconverted unmethylated C is identical to a methylated C; non-conversion inflates every beta. **Symptom:** uniformly elevated methylation, fabricated low-methylation regions. **Fix:** require >=99% conversion (CHH-proxy in mammals; lambda spike-in in plants/ESC/neurons).

### bismark extractor on a bwa-meth BAM
**Trigger:** `bismark_methylation_extractor` on a non-Bismark BAM. **Mechanism:** it reads Bismark's XM tag, absent from bwa-meth output. **Symptom:** error or empty/garbage calls. **Fix:** use MethylDackel or BISCUIT, which recompute from BAM + reference.

### C/T SNP read as unmethylation
**Trigger:** extracting human population data with no variant-awareness. **Mechanism:** a T allele at a reference C is scored as converted. **Symptom:** spurious hypomethylation at polymorphic CpGs; SNP-driven false DMRs. **Fix:** BISCUIT/Bis-SNP joint calling, or MethylDackel `--maxVariantFrac`, or mask dbSNP/sample-VCF CpGs.

### Paired-end overlap double-counted
**Trigger:** single-end mode on paired data, or a non-default tool. **Mechanism:** the R1/R2 overlap counts one molecule twice. **Symptom:** inflated coverage, biased beta on mate disagreement. **Fix:** `-p` (Bismark `--no_overlap` is on by default for paired-end); MethylDackel handles overlap automatically.

### M-bias not trimmed
**Trigger:** extracting without inspecting the M-bias plot. **Mechanism:** end-repair fill-in introduces unmethylated Cs at fragment ends; the per-position methylation deviates near read ends. **Symptom:** a non-flat M-bias curve; biased calls in the trimmable region. **Fix:** trim with `--ignore`/`--ignore_r2` (Bismark) or `--OT/--OB` bounds (MethylDackel). The diagnostic is FLATNESS/positional stability, not any particular global level.

### Coordinate base mismatch on a join
**Trigger:** joining a MethylDackel bedGraph (0-based) to a Bismark `.cov` (1-based). **Mechanism:** the two formats index differently. **Symptom:** every site shifts by one; strands silently mismatch. **Fix:** pick one format end-to-end or convert explicitly; the cytosine report and allc are 1-based, both bedGraphs are 0-based.

### --merge_non_CpG mistaken for dyad collapse
**Trigger:** using `--merge_non_CpG` to merge the symmetric CpG strands. **Mechanism:** `--merge_non_CpG` merges the CHG+CHH output files, NOT the CpG dyad. **Symptom:** strand-specific CpG report unchanged; CpG coverage not doubled. **Fix:** symmetric CpG collapse is `coverage2cytosine --merge_CpG` / MethylDackel `--mergeContext`.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Conversion efficiency >=99% | Shirane 2013 *PLoS Genet* 9:e1003439; community | below it, residual unconverted Cs inflate every beta |
| CHH rate ~= (1 - conversion) in mammals | Schultz 2015 *Nature* 523:212 | true mammalian CHH is near-zero, so it reads out non-conversion |
| Per-CpG coverage >=10x (after merge) | community | granularity 1/n; SE of an intermediate beta ~0.16 at 10x |
| `--ignore_r2` ~2 for EM-seq/PBAT | M-bias plot | R2 5' end-repair fill-in adds unmethylated Cs; set from the plot |
| MethylDackel `-q` 10 / `-p` 5 | MethylDackel defaults | MAPQ/base-quality minima; defaults, confirm with `--help` |
| `--maxVariantFrac` no universal value | MethylDackel docs | set per-experiment against known-SNP density |
| `--merge_CpG` doubles dyad coverage | Bismark docs | + and - strand of a symmetric CpG are co-methylated; merge then threshold |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Empty/garbage calls from bismark extractor | bwa-meth BAM (no XM tag) | use MethylDackel/BISCUIT |
| Uniformly high methylation | incomplete conversion | check CHH rate / lambda; require >=99% |
| Spurious hypomethylation at SNPs | C/T SNP read as conversion | `--maxVariantFrac`; BISCUIT/Bis-SNP; mask dbSNP |
| Inflated coverage on overlaps | single-end mode on paired data | `-p`; MethylDackel handles it automatically |
| Sites shifted by one after a join | 0-based vs 1-based format mix | reconcile coordinate base; one format end-to-end |
| Plant CHH/CHG methylome missing | CpG-only default | `--CX` (Bismark) / `--CHG --CHH` (MethylDackel) |
| `coverage2cytosine: option --merge_CpG` ignored | used `--merge_non_CpG` instead, or paired with `--CX` | `--merge_CpG` is CpG-only, incompatible with `--CX` |
| Inverted (1-beta) methylome | bisulfite extractor on TAPS data | ASTAIR `--mod_mapping mCtoT` |

## References

- Krueger F, Andrews SR. 2011. Bismark: a flexible aligner and methylation caller for Bisulfite-Seq applications. *Bioinformatics* 27:1571-1572.
- Liu Y, Siegmund KD, Laird PW, Berman BP. 2012. Bis-SNP: combined DNA methylation and SNP calling for Bisulfite-seq data. *Genome Biol* 13:R61.
- Vaisvila R, Ponnaluri VKC, Sun Z, et al. 2021. Enzymatic methyl sequencing detects DNA methylation at single-base resolution from picograms of DNA. *Genome Res* 31:1280-1289.
- Booth MJ, Branco MR, Ficz G, et al. 2012. Quantitative sequencing of 5-methylcytosine and 5-hydroxymethylcytosine at single-base resolution. *Science* 336:934-937.
- Yu M, Hon GC, Szulwach KE, et al. 2012. Base-resolution analysis of 5-hydroxymethylcytosine in the mammalian genome. *Cell* 149:1368-1380.
- Schutsky EK, DeNizio JE, Hu P, et al. 2018. Nondestructive, base-resolution sequencing of 5-hydroxymethylcytosine using a DNA deaminase. *Nat Biotechnol* 36:1083-1090.
- Liu Y, Siejka-Zielinska P, Velikova G, et al. 2019. Bisulfite-free direct detection of 5-methylcytosine and 5-hydroxymethylcytosine at base resolution. *Nat Biotechnol* 37:424-429.
- Schultz MD, He Y, Whitaker JW, et al. 2015. Human body epigenome maps reveal noncanonical DNA methylation variation. *Nature* 523:212-216.
- Shirane K, Toh H, Kobayashi H, et al. 2013. Mouse oocyte methylomes at base resolution reveal genome-wide accumulation of non-CpG methylation and role of DNA methyltransferases. *PLoS Genet* 9:e1003439.
- Landau DA, Clement K, Ziller MJ, et al. 2014. Locally disordered methylation forms the basis of intratumor methylome variation in chronic lymphocytic leukemia. *Cancer Cell* 26:813-825.
- Landan G, Cohen NM, Mukamel Z, et al. 2012. Epigenetic polymorphism and the stochastic formation of differentially methylated regions in normal and cancerous tissues. *Nat Genet* 44:1207-1214.
- Guo S, Diep D, Plongthongkum N, et al. 2017. Identification of methylation haplotype blocks aids in deconvolution of heterogeneous tissue samples and tumor tissue-of-origin mapping from plasma DNA. *Nat Genet* 49:635-642.
- Xu C, Corces VG. 2018. Nascent DNA methylome mapping reveals inheritance of hemimethylation at CTCF/cohesin sites. *Science* 359:1166-1170.
- Laird CD, Pleasant ND, Clark AD, et al. 2004. Hairpin-bisulfite PCR: assessing epigenetic methylation patterns on complementary strands of individual DNA molecules. *PNAS* 101:204-209.
- MethylDackel. github.com/dpryan79/MethylDackel (no associated journal publication).
- BISCUIT. github.com/huishenlab/biscuit (no associated journal publication).

## Related Skills

- bismark-alignment - Produces the aligned BAM consumed here
- differential-cpg-testing - Per-CpG statistical testing on the counts
- dmr-detection - Region-level methods downstream
- methylkit-analysis - methylKit import of the coverage/cytosine report
- long-read-sequencing/nanopore-methylation - Native long-read MM/ML modification calling (the wall)
- causal-genomics/mendelian-randomization - mQTL / causal follow-up of allele-specific methylation
- workflows/methylation-pipeline - End-to-end bisulfite pipeline
<!-- END FILE: methylation-analysis/methylation-calling/SKILL.md -->

## 子目录：methylation-analysis/methylkit-analysis

<!-- BEGIN FILE: methylation-analysis/methylkit-analysis/SKILL.md -->
---
name: bio-methylation-methylkit
description: Imports Bismark coverage or cytosine-report files into the methylKit object model, then runs the import-to-results spine - filterByCoverage, normalizeCoverage, unite/destrand, calculateDiffMeth, getMethylDiff - for both per-CpG (DMC) and fixed-tile (DMR) differential methylation, plus tileMethylCounts, PCA/correlation/clustering QC, and assocComp/removeComp batch handling. Covers the silent default traps that shape the false-positive rate: overdispersion='none' does no correction while 'MN' forces the F-test (ignoring test='Chisq'), adjust defaults to SLIM not BH, getMethylDiff defaults difference=25/qvalue=0.01, cov.bases=0 admits single-CpG tiles, and pool destroys biological replication. Use when importing bisulfite count tables, filtering/normalizing/uniting methylation samples, running methylKit differential testing, or QC-ing methylomes. For per-site test-choice (count vs continuous) see differential-cpg-testing; for selection-aware region FDR (dmrseq/DSS) see dmr-detection.
tool_type: r
primary_tool: methylKit
---

## Version Compatibility

Reference examples tested with: methylKit 1.28+, GenomicRanges 1.54+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The `assembly=` string (e.g. `hg38`) is metadata only - methylKit never checks it. The genome build is real elsewhere: coordinates must match the alignment genome, and annotation packages (`TxDb.Hsapiens.UCSC.hg38.knownGene`, annotatr `build_annotations(genome='hg38')`) are genome-build-specific. methylKit's `overdispersion`, `test`, and `adjust` defaults have shifted across Bioconductor releases - run `?calculateDiffMeth` on the installed build before trusting any default.

# methylKit Analysis

**"Analyze methylation across my samples"** -> Import per-cytosine counts into a methylRawList, then filter, normalize, unite, and test - because each of those steps is a modeling decision that sets which CpGs survive and how many false positives the test emits, not boilerplate.
- R: `methRead(pipeline='bismarkCoverage')` -> `filterByCoverage()` -> `normalizeCoverage()` -> `unite(destrand=)` -> `calculateDiffMeth(overdispersion='MN')` -> `getMethylDiff()`

Scope: the methylKit OBJECT MODEL and the short-read bisulfite import-to-results workflow, for BOTH per-CpG (DMC) and fixed-tile (DMR) results. Which per-site test to use (count vs continuous, beta vs M) -> differential-cpg-testing. Selection-aware region callers (dmrseq/DSS/metilene) and region FDR -> dmr-detection. Long-read MM/ML modBAM input -> long-read-sequencing/nanopore-methylation (its counts pipe back into this object model).

## The Single Most Important Modern Insight -- The Object Model Is the Analysis

Coverage filtering, normalization, destranding, and the overdispersion model are not setup before the "real" test - they ARE the test. Each silently changes which CpGs exist and what the p-value means, and methylKit's defaults are tuned for nothing in particular. Three corollaries every misuse violates:

1. **The defaults offer no protection.** `calculateDiffMeth` defaults to `overdispersion='none'` - a plain logistic LRT that assumes binomial-only variance and over-calls under biological replication. Two healthy replicates differ at a CpG far more than coin-flip sampling predicts; only `overdispersion='MN'` adds the between-replicate (beta-binomial) layer. The paper discusses overdispersion; the function does not apply it unless told.
2. **The knobs interact and several are silent.** `overdispersion='MN'` automatically switches to the F-test, so a passed `test='Chisq'` is ignored with no warning. `adjust` defaults to SLIM (methylKit's own q-method), not BH, so counts are not comparable to a DSS/limma BH analysis. `tileMethylCounts(cov.bases=0)` lets a one-CpG window become a "region." None of these throw an error; the result just quietly changes.
3. **Coverage is the substrate, not the answer.** A single CpG's methylation percentage is a count ratio; below ~10x it is a coin flip. Filtering the low tail (noise) and the high tail (PCR/repeat artifacts) before testing decides the result more than the test does.

Organize the workflow around defending these, not around calling functions in order.

## The Import-to-Results Spine

Run these in order. Skipping or reordering them changes the result silently.

### 1. Import: methRead with the pipeline matching the input

**Goal:** Load per-cytosine counts into a methylRawList, choosing the parser that matches the Bismark output format.

**Approach:** `pipeline='bismarkCoverage'` reads `.cov`/`.cov.gz` (chr/start/end/%meth/numC/numT - NO strand, so destranding is limited); `pipeline='bismarkCytosineReport'` reads the CX/CpG report (carries strand + context, enables proper destranding). `treatment` is an integer vector (0/1, or 0/1/2 for multi-group). `context='CpG'` only - never destrand CHG/CHH downstream.

```r
library(methylKit)
file_list <- list('ctrl1.cov.gz', 'ctrl2.cov.gz', 'treat1.cov.gz', 'treat2.cov.gz')
sample_ids <- list('ctrl_1', 'ctrl_2', 'treat_1', 'treat_2')
meth_obj <- methRead(file_list, sample.id=sample_ids, treatment=c(0,0,1,1),
                     assembly='hg38', context='CpG', pipeline='bismarkCoverage')
# dbtype='tabix', save.db=TRUE gives disk-backed methylRawDB objects for large WGBS
```

### 2. Filter and normalize BEFORE uniting (and before tiling)

**Goal:** Drop unreliable and artifactual CpGs per sample, then remove library-size-driven coverage differences so a deeper sample does not look more "confident."

**Approach:** `filterByCoverage(lo.count, hi.perc)` removes the noisy low tail and the artifactual high tail; `normalizeCoverage` scales coverage between samples. Both are per-sample and must precede `unite` and `tileMethylCounts`.

```r
meth_filt <- filterByCoverage(meth_obj, lo.count=10, lo.perc=NULL, hi.count=NULL, hi.perc=99.9)
meth_norm <- normalizeCoverage(meth_filt, method='median')
```

### 3. Unite: destrand only for CpG, only with strand info

**Goal:** Build the per-base table of CpGs covered across samples for testing.

**Approach:** `unite` keeps CpGs covered in ALL samples; `min.per.group=2L` relaxes that to >=2 per group (keeps more sites, allows missingness). `destrand=TRUE` merges the + and - strand counts of a CpG dyad - valid ONLY for symmetric CpG context AND only meaningful when strand is present (cytosine report). On `.cov` (bismarkCoverage, no strand) destranding is limited; on CHG/CHH it is wrong.

```r
meth_united <- unite(meth_norm, destrand=TRUE)            # destrand only if strand info present
meth_united <- unite(meth_norm, min.per.group=2L)         # allow missingness across replicates
```

### 4. QC the united object before testing

**Goal:** Confirm samples cluster by biology, not by batch, before believing any DMC.

**Approach:** Run correlation, PCA, and clustering on the united (% methylation) object. A control clustering with the treated group, or PC1 tracking sequencing batch, means the contrast is confounded.

```r
getCorrelation(meth_united, plot=TRUE)
PCASamples(meth_united)
clusterSamples(meth_united, dist='correlation', method='ward.D', plot=TRUE)
```

### 5. Test: calculateDiffMeth with overdispersion correction

**Goal:** Test each CpG for a group difference using a model that accounts for between-replicate overdispersion.

**Approach:** With replicates, set `overdispersion='MN'`, which automatically uses the F-test (the `test=` argument is then ignored - passing `test='Chisq'` alongside MN does not produce a chi-square test). Set `adjust='BH'` if the q-values must be comparable to other tools; the default SLIM is methylKit-specific. `getMethylDiff` filters by effect size AND q.

```r
diff_meth <- calculateDiffMeth(meth_united, overdispersion='MN', adjust='BH', mc.cores=4)
dmcs <- getMethylDiff(diff_meth, difference=25, qvalue=0.01)             # all DMCs
dmcs_hyper <- getMethylDiff(diff_meth, difference=25, qvalue=0.01, type='hyper')
# positive meth.diff = hyper in the higher-treatment group
```

## Tile-Based Regions (a fast screen, not selection-corrected inference)

**Goal:** Aggregate CpGs into fixed windows for a quick region-level scan.

**Approach:** Tile AFTER filter/normalize, raise `cov.bases` so a window needs real CpG support, then flow through the same unite -> calculateDiffMeth -> getMethylDiff path. The same `getMethylDiff` returns DMCs on a per-base object and (window) DMRs on a tiled object.

```r
tiles <- tileMethylCounts(meth_norm, win.size=1000, step.size=1000, cov.bases=3)  # cov.bases>=3
tiles_united <- unite(tiles, destrand=FALSE)              # tiles are not strand objects
diff_tiles <- calculateDiffMeth(tiles_united, overdispersion='MN', adjust='BH', mc.cores=4)
dmrs <- getMethylDiff(diff_tiles, difference=25, qvalue=0.01)
```

The per-tile q is a per-test SLIM/BH value: it does NOT model correlation between tiles and is NOT corrected for the region-selection step. Fixed windows also split or merge true DMRs at arbitrary boundaries. Treat methylKit tiles as a defensible screen; for rigorous region FDR (a permutation null that survives region selection) go to dmr-detection (dmrseq).

## Batch, Multi-Group, and the Single-Factor Limit

methylKit's `calculateDiffMeth` is a single-factor 2-group test. For known batch, remove the associated principal components before testing; for >2 groups, subset to pairwise contrasts. Complex designs (covariates, multi-factor) exceed what methylKit models - move to dmr-detection (DSS multiFactor / dmrseq covariates) or a continuous limma-on-M path (differential-cpg-testing).

```r
sample_anno <- data.frame(batch=c('a','a','b','b'))
as_comp <- assocComp(meth_united, sample_anno)            # which PCs track the covariate
meth_corrected <- removeComp(meth_united, comp=1)         # drop the batch PC, then test
meth_AB <- reorganize(meth_united, sample.ids=c('ctrl_1','ctrl_2','treat_1','treat_2'),
                      treatment=c(0,0,1,1))               # subset/relabel for a pairwise contrast
```

`pool(meth_united, sample.ids=...)` sums replicate counts into one pseudo-sample per group. This DESTROYS biological replication - the test then has no within-group variance estimate and its p-values are meaningless for inference. Use it only for no-replicate exploratory visualization, never for the reported test.

## Per-Method Failure Modes

### Overdispersion left at the default
**Trigger:** `calculateDiffMeth` with replicates and no `overdispersion=` argument. **Mechanism:** the default `'none'` is a binomial-only logistic LRT that ignores between-replicate variance. **Symptom:** implausibly many significant CpGs; q-values far smaller than a beta-binomial tool gives on the same data. **Fix:** `overdispersion='MN'` (which uses the F-test) whenever replicates exist.

### MN plus test='Chisq'
**Trigger:** passing both `overdispersion='MN'` and `test='Chisq'`. **Mechanism:** MN forces the F-test; `test=` is silently ignored. **Symptom:** the reported "chi-square test" was never run. **Fix:** drop `test=` when using MN; `test=` is honored only with `overdispersion='none'`.

### SLIM read as BH
**Trigger:** comparing methylKit q-value counts to a DSS/limma BH analysis. **Mechanism:** `adjust` defaults to SLIM, methylKit's own sliding-linear-model q-method. **Symptom:** DMC counts disagree with another tool's BH results at the "same" q. **Fix:** set `adjust='BH'` for cross-tool comparability and state the method used.

### cov.bases=0 tiles
**Trigger:** `tileMethylCounts` at the default `cov.bases=0`. **Mechanism:** a window with one covered CpG becomes a "region." **Symptom:** thousands of single-CpG "DMRs," many noisy. **Fix:** raise `cov.bases` to >=3.

### Tiling or testing the raw object
**Trigger:** `tileMethylCounts(meth_obj, ...)` or uniting before filtering/normalizing. **Mechanism:** low-coverage and library-size artifacts propagate into the tiles and the test. **Symptom:** artifactual regions; deeper samples look hyper-confident. **Fix:** `filterByCoverage` then `normalizeCoverage` BEFORE tiling/uniting.

### Destranding the wrong context or input
**Trigger:** `unite(destrand=TRUE)` on `.cov` input or on CHG/CHH context. **Mechanism:** `.cov` carries no strand; non-CpG dyads are not symmetric. **Symptom:** double-counting or wrong merges. **Fix:** destrand CpG only, ideally from the cytosine report.

### pool() then test
**Trigger:** `pool()` followed by `calculateDiffMeth`. **Mechanism:** pooling removes within-group variance. **Symptom:** tiny p-values with no biological meaning. **Fix:** never pool for the reported test; keep replicates separate.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `lo.count` = 10 | convention (methylKit tutorial) | below ~10x a single-CpG percentage is a coin flip; not a derived value |
| `hi.perc` = 99.9 | convention | drops the top 0.1% coverage (PCR/repeat artifacts) |
| `overdispersion` = 'MN' with replicates | Akalin 2012 *Genome Biol* 13:R87 | adds the beta-binomial between-replicate layer; default 'none' over-calls |
| `adjust` = 'BH' (default SLIM) | Akalin 2012 *Genome Biol* 13:R87 | BH for comparability; SLIM is methylKit-specific |
| `getMethylDiff` difference=25, qvalue=0.01 | methylKit defaults | 25% is tutorial convention, NOT derived; justify per feature/coverage/purity and report it |
| `tileMethylCounts` cov.bases >= 3 | nuance | default 0 admits single-CpG tiles; require real CpG support |
| `win.size`=`step.size`=1000 (default) | methylKit defaults | `step < win` gives overlapping (sliding) tiles |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Implausibly many DMCs | `overdispersion='none'` under replication | set `overdispersion='MN'` |
| Reported chi-square never ran | `test='Chisq'` with MN | MN forces F; drop `test=` |
| Counts disagree with another tool at same q | default `adjust='SLIM'` | set `adjust='BH'`, state the method |
| Thousands of single-CpG "regions" | `cov.bases=0` | raise `cov.bases` to >=3 |
| Destrand error / double counts | destrand on `.cov` or non-CpG | destrand CpG only, from cytosine report |
| Meaningless tiny p-values | `pool()` before testing | keep replicates; never pool for inference |
| Deeper sample looks more confident | no `normalizeCoverage` | normalize before unite/test |

## References

- Akalin A, Kormaksson M, Li S, Garrett-Bakelman FE, Figueroa ME, Melnick A, Mason CE. 2012. methylKit: a comprehensive R package for the analysis of genome-wide DNA methylation profiles. *Genome Biol* 13:R87.
- Krueger F, Andrews SR. 2011. Bismark: a flexible aligner and methylation caller for Bisulfite-Seq applications. *Bioinformatics* 27:1571-1572.
- Robinson MD, Kahraman A, Law CW, Lindsay H, Nowicka M, Weber LM, Zhou X. 2014. Statistical methods for detecting differentially methylated loci and regions. *Front Genet* 5:324.

## Related Skills

- methylation-calling - Produces the coverage/cytosine reports read here
- differential-cpg-testing - Per-site statistical model choice (count vs continuous)
- dmr-detection - Selection-aware region callers (dmrseq/DSS) beyond methylKit tiles
- pathway-analysis/go-enrichment - Functional annotation of differentially methylated genes
- long-read-sequencing/nanopore-methylation - Long-read MM/ML calling; pipe counts into this object model
- workflows/methylation-pipeline - End-to-end bisulfite pipeline
<!-- END FILE: methylation-analysis/methylkit-analysis/SKILL.md -->

<!-- END CATEGORY: methylation-analysis -->

