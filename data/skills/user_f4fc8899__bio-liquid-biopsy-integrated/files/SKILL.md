---
slug: bio-liquid-biopsy-integrated
version: 1.0.1
displayName: "液体活检 / Liquid biopsy"
name: bio-liquid-biopsy-integrated
summary: "中文：液体活检综合技能，整合 7 个相关专题，覆盖液体活检：cfDNA预处理、UMI/duplex consensus、ctDNA突变检测、片段组学、甲基化检测、MRD监测。 English: Integrated Liquid biopsy skill covering 7 related topics, including Liquid biopsy: cfDNA preprocessing, UMI/duplex consensus, ctDNA mutation detection, fragmentomics, methylation-based detection, MRD monitoring."
description: "中文：这是一个面向液体活检的综合生物信息学 Skill，整合当前分类下 7 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：液体活检：cfDNA预处理、UMI/duplex consensus、ctDNA突变检测、片段组学、甲基化检测、MRD监测。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：FinaleToolkit, MethylDackel, VarDict。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Liquid biopsy, combining 7 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Liquid biopsy: cfDNA preprocessing, UMI/duplex consensus, ctDNA mutation detection, fragmentomics, methylation-based detection, MRD monitoring. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: FinaleToolkit, MethylDackel, VarDict. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# liquid-biopsy 分类 Skill 整合版

> 本文件整合同一主分类目录下 7 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: liquid-biopsy -->

## 子目录：liquid-biopsy/analytical-validation

<!-- BEGIN FILE: liquid-biopsy/analytical-validation/SKILL.md -->
---
name: bio-analytical-validation
description: Treats a ctDNA assay as a molecule-counting experiment at the Poisson edge and builds its analytical-validation case the measurement-science way. Covers the genome-equivalent currency (~330 haploid copies/ng), the lambda = input_GE x VAF sampling ceiling (lambda>=3 for ~95% detection), the error-suppression ladder (raw NGS ~1e-3 -> single-strand UMI ~1e-4/1e-5 -> duplex <1e-7), the CLSI EP17 LoB/LoD/LoD95/LoQ framework, the per-locus-vs-panel-integrated LoD distinction that lets bespoke MRD reach ppm, contrived/SEQC2 reference standards, and honest LoD reporting conditioned on input mass + consensus depth + replicate detection rate. Use when stating or trusting a sensitivity claim, designing a dilution-series validation, deciding how many genome equivalents are needed at a target VAF, choosing a single-locus vs panel-integrated LoD, or auditing a "detects 0.1% VAF" claim.
tool_type: python
primary_tool: scipy
---

## Version Compatibility

Reference examples tested with: numpy 1.26+, scipy 1.12+, statsmodels 0.14+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Analytical Validation and Detection Limits

**"What is the real limit of detection of my ctDNA assay, and can I trust the number I am about to report?"** -> Quantify the Poisson sampling ceiling, the error-suppression floor, and the LoB/LoD/LoQ that together define a defensible sensitivity claim.
- Python: `scipy.stats.poisson` for detection-probability math, `scipy.stats.norm` for CLSI LoB/LoD, `statsmodels` Probit/Logit for a dilution-series LoD95 fit.

## The Single Most Important Modern Insight -- LoD Is Set by Genome Equivalents Sampled and Error Suppression, NOT by Sequencing Depth or the Caller

A ctDNA assay is a molecule-counting experiment at the Poisson edge. The mutant signal is a fixed, tiny number of physical template molecules in the tube, and the limit of detection is governed by two ceilings: how many genome equivalents were sampled (Poisson), and how low the background error floor was driven (error suppression). 1 ng of human DNA is ~330 haploid genome equivalents; the expected mutant-molecule count is lambda = input_GE x VAF. A 0.1% variant on 1,000 GE (~3.0 ng) has lambda = 1, so e^-1 ~= 37% of the time the mutant template was never in the tube and a perfect sequencer detects nothing. Past the point where every input molecule has been read once (sampling saturation, visible as a deduplication plateau in UMI families), additional read depth re-sequences the same physical molecules and adds zero information. Reporting an LoD as a bare VAF -- with no input mass, no unique-molecule (consensus) depth, no replicate detection rate -- is reporting an undefined quantity.

The second ceiling is the per-base background error rate, which sets the VAF floor independently: a 0.1% variant cannot be distinguished from noise if the assay manufactures that base at 0.1%. Error suppression is a ladder (raw NGS ~1e-3 -> single-strand UMI consensus ~1e-4/1e-5 -> duplex <1e-7), and single-strand consensus does NOT remove template-resident damage (C->T deamination, G->T 8-oxoG) because every PCR copy of that strand inherits the lesion -- only duplex strand-concordance catches it. The achieved LoD is the *worse* of the two ceilings: error dominates above ~0.1% VAF for tumor-naive single-locus calling, sampling dominates below it. The escape hatch is integration -- a bespoke panel summing mutant molecules across 16-50 loci against summed background reaches single-ppm even though each locus alone is ~1e-3 to 1e-4 (per-locus vs panel-integrated LoD).

## Methods Landscape

| Concept | Definition | Source |
|---------|------------|--------|
| LoB (Limit of Blank) | Highest signal expected from an analyte-free blank (95th pct): LoB = mean_blank + 1.645*SD_blank; the false-positive anchor on true negatives | CLSI EP17-A2 |
| LoD (Limit of Detection) | Lowest level reliably distinguishable from LoB: LoD = LoB + 1.645*SD_low; a sample at LoD is detected ~95% of the time | CLSI EP17-A2 |
| LoD95 | The concentration/VAF where detection probability = 95%; a point on a probit/logistic detection curve, not a separate definition | CLSI EP17-A2; Newman 2016 |
| LoQ (Limit of Quantitation) | Lowest level measurable with stated precision (e.g. CV<=20%); LoQ >= LoD always, so a "VAF" near the floor is detectable but not trustworthy | CLSI EP17-A2 |
| Per-locus LoD | Single-variant LoD; sampling- and error-limited (~0.05-0.1% VAF typical) | Newman 2014/2016 |
| Panel-integrated LoD | Evidence summed across N tracked variants via a >=k-of-N positivity rule (binomial over per-locus Poisson detection), reaching single-ppm at 16-50 loci; ~sqrt(N) variance-averaging is only a loose lower bound | Reinert 2019 |
| Reference standards | Contrived defined-VAF cell-line admixtures fragmented to ~160 bp into normal cfDNA; SEQC2 Sample A / HCC1395 truth sets | Fang 2021 (SEQC2) |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| "How many GE for 95% detection at VAF X?" | Solve lambda = input_GE x VAF >= 3, so input_GE >= 3/VAF | 1 - e^-3 = 0.95; ~30,000 GE (~91 ng at 330 GE/ng) for a single 1e-4 variant -- often more than one tube provides |
| "Why is more depth not helping?" | Report unique (consensus) molecular coverage, not raw depth; check the dedup plateau | Past sampling saturation, depth re-reads the same molecules; the ceiling is GE in the tube |
| Single hotspot vs bespoke panel for low VAF | Single locus: error/sampling-limited ~0.1%; need ppm -> integrate across 16-50 clonal loci | Per-locus Poisson/error floor is escaped only by summing independent detections (panel-integrated LoD) |
| Reporting an LoD | Condition on input mass (GE) + consensus depth + replicate detection rate (e.g. "LoD95 0.1% VAF at 30 ng / 2x duplex / 95% of 20 replicates") | A bare VAF omits the input mass, the unique depth, and per-locus vs integrated -- it is undefined |
| Estimating LoD95 from a dilution series | Probit (or logistic) regression of detection (0/1) on VAF; read off the 95% point with a CI | CLSI EP17-A2 detection-curve method; binary detection is a clean GLM target |
| Distinguishing detection from quantitation | Set LoD for yes/no calls; set LoQ (CV<=20%) separately for any reported VAF/TF | MRD calls are binary and can sit far below LoQ; a near-floor VAF number is not quantitative |
| Validating against truth | Contrived SEQC2 Sample A / HCC1395 admixtures, fragmented to cfDNA-like ~160 bp | Real low-VAF patient material is scarce/unverifiable; commutability with plasma is the caveat |

## Genome-Equivalent and Poisson Detection Calculator

**Goal:** Convert an input mass and target VAF into an expected mutant-molecule count and a detection probability, so a sensitivity claim is anchored to molecules rather than to a VAF alone.

**Approach:** Convert ng to haploid genome equivalents (~330/ng), set lambda = input_GE x VAF, and read the detection probability as a Poisson tail P(X >= k) = 1 - cdf(k-1, lambda); invert for the minimum GE that puts lambda at the >=3 sampling-detection threshold.

```python
import numpy as np
from scipy.stats import poisson

GE_PER_NG = 330  # haploid ~3.3 pg -> strict 1 ng / 3.3 pg = 303; 330 is the common diploid-6.6 pg/rounding convention

def genome_equivalents(input_ng):
    return input_ng * GE_PER_NG

def detection_probability(input_ng, vaf, min_mutant_molecules=1):
    '''P(at least min_mutant_molecules present) under Poisson(lambda = GE * VAF).'''
    lam = genome_equivalents(input_ng) * vaf
    return float(poisson.sf(min_mutant_molecules - 1, lam))

def ge_for_sampling_detection(vaf, target_lambda=3.0):
    '''GE needed so lambda >= 3 -> ~95% chance the mutant molecule is present at all.'''
    return target_lambda / vaf

# A 0.1% variant on 3.0 ng (~990 GE) has lambda ~= 1 -> ~63% detected, ~37% missed by sampling alone.
detection_probability(3.0, 0.001)          # ~0.63
ge_for_sampling_detection(1e-4)            # 30000 GE (~91 ng) for a single 0.01% variant
```

## LoB and LoD95 from a Dilution Series (CLSI EP17 style)

**Goal:** Estimate the VAF at which the assay detects 95% of the time, from a contrived dilution series, and anchor it to the blank-derived false-positive floor.

**Approach:** Compute LoB from blank replicates (mean + 1.645*SD, one-sided 95th pct), then fit a probit GLM of binary detection on log10(VAF) (CLSI EP17 fits on log concentration) across the dilution series and invert it for the 95% detection point. The series must bracket the 0.95 crossing — all-detected upper levels cause near-complete separation and an unstable slope.

```python
import numpy as np
import statsmodels.api as sm
from scipy.stats import norm

def limit_of_blank(blank_signals):
    '''LoB = mean + 1.645*SD; one-sided 95th percentile of analyte-free blanks.'''
    blank_signals = np.asarray(blank_signals, dtype=float)
    return blank_signals.mean() + 1.645 * blank_signals.std(ddof=1)

def lod95_probit(vaf_levels, detected):
    '''Probit fit of detection (0/1) on log10(VAF); returns the VAF where P(detect) = 0.95.'''
    log_vaf = np.log10(np.asarray(vaf_levels, dtype=float))
    y = np.asarray(detected, dtype=float)
    X = sm.add_constant(log_vaf)
    fit = sm.GLM(y, X, family=sm.families.Binomial(link=sm.families.links.Probit())).fit()
    intercept, slope = fit.params
    return 10 ** ((norm.ppf(0.95) - intercept) / slope)
```

## Per-Locus to Panel-Integrated LoD

**Goal:** Combine independent per-locus detection probabilities into the panel-level detection probability that a bespoke MRD assay actually achieves, and find the integrated LoD.

**Approach:** Treat each tracked locus as an independent Poisson sampler at the same tumor VAF; a panel positive call requires at least k loci detected, so the panel detection probability is the binomial-tail over the per-locus probabilities -- this is why summing 16-50 loci reaches ppm.

```python
import numpy as np
from scipy.stats import poisson, binom

def panel_detection_probability(input_ng, vaf, n_loci, min_loci_positive=2):
    '''P(>= min_loci_positive of n_loci detected); >=2-of-N is the Signatera-style positivity rule.'''
    per_locus = float(poisson.sf(0, input_ng * 330 * vaf))
    return float(binom.sf(min_loci_positive - 1, n_loci, per_locus))

def panel_integrated_lod95(input_ng, n_loci, min_loci_positive=2, grid=None):
    '''Lowest VAF on a log grid where the >=k-of-N panel call hits 95%.'''
    grid = np.logspace(-6, -2, 400) if grid is None else np.asarray(grid)
    probs = [panel_detection_probability(input_ng, v, n_loci, min_loci_positive) for v in grid]
    hits = grid[np.asarray(probs) >= 0.95]
    return float(hits.min()) if hits.size else float('nan')
```

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| ~330 haploid genome equivalents per ng cfDNA | Standard (haploid ~3.3 pg) | Converts input mass to the molecule count that actually sets sensitivity; strict 1 ng / 3.3 pg = 303, with 330 the common diploid-6.6 pg/rounding convention |
| lambda = input_GE x VAF; lambda >= 3 for ~95% sampling-detection | Poisson, 1 - e^-3 = 0.95 | Below lambda~3 the mutant template is often simply absent from the tube regardless of sequencing |
| Raw NGS error floor ~1e-3 | Schmitt 2012 context; field consensus | Sets the per-base VAF floor before any consensus; a global VAF cutoff above this is noise-limited |
| Single-strand UMI consensus ~1e-4 to 1e-5 | Newman 2014/2016 (CAPP-Seq/iDES) | Majority-vote within a UMI family erases PCR/sequencing error not shared across the family |
| Duplex sequencing <1e-7 (theory <1/1e9 nt) | Schmitt 2012 *PNAS* 109:14508 | Requires the variant on BOTH original strands; independent strand errors cannot agree |
| iDES adds ~3-15x over baseline; ctDNA to ~4e-5 | Newman 2016 *Nat Biotechnol* 34:547 | Position/trinucleotide background model subtracts stereotyped artifacts per locus |
| ichorCNA tumor-fraction floor ~3% | Adalsteinsson 2017 *Nat Commun* 8:1324 | Copy-number-based TF estimation; sWGS/ULP-WGS cannot resolve TF below ~3% -- an LoD, not a VAF |
| Bespoke panel reaches single-ppm by integrating 16-50 loci | Reinert 2019 *JAMA Oncol* 5:1124 | Per-locus ~1e-4 floor escaped by summing independent detections; >=2-of-N positivity rule |
| LoQ >= LoD (e.g. CV<=20% for quantitation) | CLSI EP17-A2 | Detection (binary) is easier than quantitation (continuous); near-floor VAFs are not trustworthy numbers |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "Assay detects 0.1% VAF" with no input mass | VAF reported as a standalone sensitivity spec | Condition the LoD on input GE + consensus depth + replicate detection rate; 0.1% on 100 GE is noise |
| Buying more sequencing depth to improve sensitivity | Conflating read depth with molecule count | Past the dedup plateau the assay is sampling-saturated; add plasma volume / conversion efficiency, not depth |
| Per-locus LoD quoted as the panel LoD (or vice versa) | Ignoring integration across tracked loci | State which is reported; a 50-variant panel's integrated LoD is orders of magnitude below any single locus |
| VAF used as the sensitivity unit | Omitting the molecule count behind the fraction | Pair every VAF with input GE; lambda = GE x VAF is the quantity that determines detection |
| Single-strand UMI assumed to remove damage artifacts | Template-resident C->T/G->T inherited by every copy | Use duplex strand-concordance for sub-1e-5 claims; single-strand votes unanimously for the lesion |
| Reporting a near-floor VAF as a measured value | Confusing LoD (detect) with LoQ (quantify) | Quantitative VAF/TF only at/above LoQ (CV<=20%); below it report detected/not-detected |
| Global VAF cutoff across all loci | Background error is position/context-dependent | Use a per-locus background model (iDES-style); a flat threshold loses sensitivity and specificity |

## References

- Diehl F, Schmidt K, Choti MA, et al. 2008. Circulating mutant DNA to assess tumor dynamics. *Nat Med* 14:985-990. -- ctDNA half-life ~114 min; molecule-counting framing of tumor dynamics.
- Schmitt MW, Kennedy SR, Salk JJ, et al. 2012. Detection of ultra-rare mutations by next-generation sequencing. *PNAS* 109:14508-14513. -- Duplex sequencing; theoretical error floor <1 per 1e9 nt.
- Newman AM, Bratman SV, To J, et al. 2014. An ultrasensitive method for quantitating circulating tumor DNA with broad patient coverage. *Nat Med* 20:548-554. -- CAPP-Seq; UMI-consensus error suppression.
- Newman AM, Lovejoy AF, Klass DM, et al. 2016. Integrated digital error suppression for improved detection of circulating tumor DNA. *Nat Biotechnol* 34:547-555. -- iDES; ~3-15x gain; ctDNA to ~4e-5.
- Razavi P, Li BT, Brown DN, et al. 2019. High-intensity sequencing reveals the sources of plasma circulating cell-free DNA variants. *Nat Med* 25:1928-1937. -- CHIP as the dominant non-tumor signal in the LoB blank.
- Adalsteinsson VA, Ha G, Freeman SS, et al. 2017. Scalable whole-exome sequencing of cell-free DNA reveals high concordance with metastatic tumors. *Nat Commun* 8:1324. -- ichorCNA; copy-number tumor-fraction floor ~3%.
- Reinert T, Henriksen TV, Christensen E, et al. 2019. Analysis of plasma cell-free DNA by ultradeep sequencing in patients with stages I to III colorectal cancer. *JAMA Oncol* 5:1124-1131. -- Signatera; 16-variant integration; >=2-of-N positivity.
- Fang LT, Zhu B, Zhao Y, et al.; SEQC2 Consortium. 2021. Establishing community reference samples, data and call sets for benchmarking cancer mutation detection using whole-genome sequencing. *Nat Biotechnol* 39:1151-1160. -- SEQC2 Sample A / HCC1395 contrived reference standards.
- CLSI EP17-A2. 2012. Evaluation of Detection Capability for Clinical Laboratory Measurement Procedures; Approved Guideline -- Second Edition. Clinical and Laboratory Standards Institute. -- Governing LoB/LoD/LoQ definitions.

## Related Skills

- ctdna-mutation-detection - applies these limits to low-VAF somatic calls
- longitudinal-monitoring - per-timepoint LoD and left-censoring of undetectable samples
- tumor-fraction-estimation - the ~3% CNA-based detection floor as an LoD
- experimental-design/multiple-testing - repeated-surveillance specificity and FDR
- clinical-biostatistics/power-and-sample-size - validation-study design
<!-- END FILE: liquid-biopsy/analytical-validation/SKILL.md -->

## 子目录：liquid-biopsy/cfdna-preprocessing

<!-- BEGIN FILE: liquid-biopsy/cfdna-preprocessing/SKILL.md -->
---
name: bio-cfdna-preprocessing
description: Decides how to preprocess plasma cfDNA sequencing data so the recoverable signal survives - library-prep-aware fragment expectations (dsDNA vs ssDNA/adaptase prep), UMI/duplex consensus with fgbio (ExtractUmisFromBam, GroupReadsByUmi --strategy paired for duplex, CallMolecularConsensusReads vs CallDuplexConsensusReads, FilterConsensusReads min-reads "total s1 s2"), the align->group->consensus->RE-align ordering, and the cfDNA dedup trap where naive coordinate dedup collapses nucleosome-coincident independent molecules. Covers when single-strand consensus suffices vs when duplex is mandatory, the singleton/sensitivity tax at low input, and reading the insert-size histogram as a pre-analytical QC instrument. Use when processing plasma cfDNA reads before fragmentomics, ctDNA mutation calling, or tumor-fraction estimation.
tool_type: mixed
primary_tool: fgbio
---

## Version Compatibility

Reference examples tested with: bwa 0.7.17+, fgbio 2.1+, numpy 1.26+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: fgbio flag semantics drift across major versions - in `CallDuplexConsensusReads` the `--min-reads` is a permissive PRE-filter (fgbio issue #1009), and in `FilterConsensusReads` the `--min-reads` (`-M`) takes up to three values "total strand1 strand2" where if values two and three differ the more stringent value must come first. Confirm both against the installed `fgbio --help` before scripting.

# cfDNA Preprocessing

**"Preprocess my plasma cfDNA reads"** -> Convert reads to consensus molecules and an analysis-ready BAM without destroying the fragment-size signal or collapsing independent molecules.
- CLI: `fgbio ExtractUmisFromBam` -> `bwa mem -Y` -> `fgbio GroupReadsByUmi` -> `fgbio Call*ConsensusReads` -> RE-align -> `fgbio FilterConsensusReads`
- Python: shell the fgbio/bwa chain with `subprocess`; read insert sizes with `pysam` for QC

## The Single Most Important Modern Insight -- Pre-Analytics and Library Prep Set the Ceiling; Consensus Is Error Suppression, Not Just Dedup

What a cfDNA assay can ever see is fixed before any bioinformatics runs. cfDNA is not randomly sheared - it is a nucleosome footprint with a mononucleosome mode at ~167 bp and a ctDNA-enriched short tail (134-144 bp), so fragment length is structured biological signal, not noise to be normalized away. Two upstream choices determine what survives: (1) the blood draw and plasma prep (a delayed draw dumps leukocyte gDNA into the denominator and irreversibly dilutes tumor fraction - no algorithm recovers it; defer that QC to liquid-biopsy/analytical-validation), and (2) the library chemistry (dsDNA ligation polishes native ends and discards the sub-100 bp population; ssDNA/adaptase prep recovers short and damaged molecules). Reverse engineering a fragment the prep threw away, or a molecule a bad draw never delivered, is impossible.

The second reframe: UMI/duplex consensus is error suppression, not merely duplicate removal. Grouping reads by UMI and majority-voting a consensus erases PCR/sequencing errors that are not shared across a family - but a single-strand consensus votes unanimously for damage (C->T deamination, G->T 8-oxoG) that was on the template before amplification. Only DUPLEX consensus, requiring the same base on both independently-copied strands, removes those lesions. Single-strand consensus cannot. Choosing simplex vs duplex is choosing an error floor, and it trades against molecular recovery at low input (the singleton tax below).

## Library-Prep and Consensus Landscape

| Choice | What it does | Recoverable distribution / error floor |
|--------|--------------|----------------------------------------|
| dsDNA ligation prep (NEB/KAPA-style) | needs duplex substrate; end-repair/A-tail polishes native ends | clean ~167 bp mode; sub-100 bp tail and native-end signal LOST |
| ssDNA prep, SRSLY/Kircher-Meyer lineage | denatures, ligates single strands; retains native ends + sawtooth | recovers short/nicked/damaged + sub-nucleosomal; prep for fragmentomics |
| ssDNA prep, adaptase/tail-based (Swift/Accel-1S) | single-strand but adaptase chemistry shifts apparent size | ~10 bp short of the canonical mode; sawtooth blunted (a chemistry signature, not a bug) |
| Single-strand UMI consensus (CallMolecularConsensusReads) | majority-vote one source strand's reads | removes PCR/sequencer error (~1e-4 to 1e-5); CANNOT remove deamination/oxidation damage |
| DUPLEX consensus (CallDuplexConsensusReads) | combine both-strand single-strand consensuses | error must occur identically on both strands to survive (~<1e-7); removes deamination/oxidation |

## Decision Tree by Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Deep targeted panel with single-strand UMIs | adjacency group -> CallMolecularConsensusReads -> FilterConsensusReads | simplex consensus suppresses PCR/sequencer error to ~1e-4; the panel-VAF workhorse |
| Need VAF below ~0.1% / MRD-grade specificity | duplex prep -> `--strategy paired` -> CallDuplexConsensusReads -> filter `2 1 1` | duplex removes damage artifacts; reaches the ~1e-7 floor single-strand cannot |
| sWGS / ULP-WGS for tumor fraction | minimal processing: trim -> align -> light dedup; NO consensus | TF from copy number needs even coverage, not error suppression; defer to tumor-fraction-estimation |
| Degraded / low-input / FFPE-adjacent sample | ssDNA prep (SRSLY) to recover short+damaged molecules | dsDNA prep discards exactly the molecules a degraded sample has left |
| Fragmentomics / end-motif readout | ssDNA prep (native ends), NO in-silico size selection upstream | dsDNA fills jagged ends; size-selecting conditions on length and biases every feature |
| Picogram input, detection (not genotyping) | call permissively (`--min-reads 1`), accept singletons | requiring duplicate observation discards the only evidence for a low-VAF variant |
| No UMIs at all, quantitative readout | do NOT coordinate-dedup; document the bias (see Failure Modes) | nucleosome-positioned ends make naive dedup delete real molecules |

Methodology evolves: confirm current fgbio flag semantics and prep-vendor size behavior against live docs before committing a pipeline.

## The fgbio Consensus Pipeline

**Goal:** Turn UMI-tagged raw reads into error-suppressed consensus molecules with correct coordinates.

**Approach:** Extract UMIs into the `RX` tag, align (consensus needs coordinates to group), group by UMI + approximate position, call consensus (which emits UNMAPPED reads because the consensus sequence differs from any input read), RE-align the consensus, then apply the real quality gate with `FilterConsensusReads`. The two-pass alignment is mandatory.

```bash
# 1. Extract inline UMIs into RX. Read structure tokens: M=UMI, S=skip/stem, T=template, +=all remaining.
#    6M11S+T per end = 6 bp UMI, 11 bp stem (the S that bleeds into T if omitted), rest = insert.
fgbio ExtractUmisFromBam --input raw.unmapped.bam --output with_umis.bam \
    --read-structure 6M11S+T 6M11S+T --single-tag RX

# 2. Align. -Y soft-clips supplementaries so tag-bearing short-fragment sequence is not dropped.
bwa mem -t 8 -Y reference.fa with_umis.bam | samtools sort -o aligned.bam -
samtools index aligned.bam

# 3. Group by UMI. adjacency = simplex default; paired = MANDATORY for duplex (reconstructs strand pairing).
fgbio GroupReadsByUmi --input aligned.bam --output grouped.bam \
    --strategy paired --edits 1          # use --strategy adjacency for single-strand UMIs

# 4a. SIMPLEX: single-strand consensus, --min-reads takes ONE value.
fgbio CallMolecularConsensusReads --input grouped.bam --output consensus.unmapped.bam --min-reads 1

# 4b. DUPLEX: --min-reads here is a permissive PRE-filter (fgbio #1009) - call low, filter later.
fgbio CallDuplexConsensusReads --input grouped.bam --output consensus.unmapped.bam --min-reads 1

# 5. RE-align: consensus reads are emitted UNMAPPED by design. Re-map, then ZipperBams
#    transfers the consensus/UMI tags from the unmapped BAM onto the new alignments.
samtools fastq consensus.unmapped.bam | bwa mem -t 8 -Y -p reference.fa - \
  | fgbio ZipperBams --unmapped consensus.unmapped.bam --ref reference.fa \
  | samtools sort -o consensus.bam -

# 6. The REAL quality gate. --min-reads "total strand1 strand2"; "2 1 1" = true duplex (both strands seen).
#    If values two and three differ, the more stringent must come first (e.g. "6 3 0", not "0 3").
fgbio FilterConsensusReads --input consensus.bam --output filtered.bam --ref reference.fa \
    --min-reads 2 1 1 --max-read-error-rate 0.025 --max-base-error-rate 0.1 \
    --min-base-quality 40 --reverse-per-base-tags
```

Key flags: `--strategy paired` is non-negotiable for duplex (`adjacency` cannot reconstruct A/B strand pairing). `--min-reads 1 1 0` on the filter accepts single-strand consensus too (one strand may be absent); `2 1 1` requires both strands = true duplex. `--reverse-per-base-tags` makes per-base depth/error tags read in genomic orientation after alignment.

## Reading the Insert-Size Histogram (QC)

**Goal:** Use the fragment-length distribution as a pre-analytical instrument before trusting any downstream number.

**Approach:** Tabulate proper-pair template lengths from the BAM, locate the mode, and compare the shape against the expected nucleosome footprint - the mode, the sawtooth, and the long-fragment fraction each diagnose a specific failure.

```python
import pysam
import numpy as np

def insert_size_qc(bam_path, max_size=600):
    '''Summarize cfDNA fragment lengths as a QC readout.'''
    bam = pysam.AlignmentFile(bam_path, 'rb')
    sizes = [r.template_length for r in bam.fetch()
             if r.is_proper_pair and not r.is_secondary and 0 < r.template_length <= max_size]
    bam.close()
    sizes = np.array(sizes)
    long_frac = np.mean(sizes > 250)  # excess >250 bp signals gDNA/leukocyte-lysis contamination
    return {'n': len(sizes), 'mode_bp': int(np.bincount(sizes).argmax()),
            'median_bp': float(np.median(sizes)), 'frac_over_250bp': float(long_frac)}
```

A mode at ~167 bp with a ~10.4 bp sawtooth below it is healthy. A mode drifting up plus excess mass >250 bp is gDNA contamination. A mode ~10 bp low is the adaptase chemistry signature, not contamination. A ~120-130 bp spike is adapter dimer (trim adapters before reading the histogram).

## Per-Method Failure Modes

### The dedup trap (naive coordinate dedup on no-UMI cfDNA)
**Trigger:** running Picard MarkDuplicates / `samtools markdup` on cfDNA without UMIs. **Mechanism:** cfDNA ends pile up non-randomly at nucleosome/linker boundaries, so many independent molecules genuinely share the same ~167 bp start+end; coordinate dedup declares them PCR duplicates and keeps one. **Symptom:** deflated unique-molecule counts and depressed VAF for true low-frequency variants - worst exactly where coverage and nucleosome positioning are strongest. **Fix:** use UMIs and group by family; if none, do not dedup by position alone for quantitative readouts and document the bias. This is the strongest single argument for putting UMIs on a cfDNA assay.

### Strict filtering on the consensus caller instead of FilterConsensusReads
**Trigger:** setting `CallDuplexConsensusReads --min-reads` high. **Mechanism:** it is a PRE-filter (fgbio #1009) that discards data before the real filter sees it. **Symptom:** lower molecular recovery than expected with no specificity gain. **Fix:** call permissively (`--min-reads 1`), apply strictness in `FilterConsensusReads`.

### adjacency grouping on duplex data
**Trigger:** `--strategy adjacency` for a duplex library. **Mechanism:** adjacency cannot link the two strands of one duplex (which carry the UMI in opposite order). **Symptom:** duplex consensus finds no two-strand molecules; output collapses to simplex. **Fix:** `--strategy paired`.

### Blanket MAPQ filtering kills short ctDNA fragments
**Trigger:** a global `MAPQ >= 30/60` filter. **Mechanism:** a 40-80 bp insert has fewer anchoring bases and lands in the low-MAPQ tail even when correctly placed. **Symptom:** the short, ctDNA-enriched fragments are preferentially deleted - the molecules size-selection was meant to keep. **Fix:** filter MAPQ with the size distribution in mind; use a gentler threshold for fragmentomics.

### Reflexive `--min-reads >= 2` at low input (the singleton tax)
**Trigger:** requiring duplicate observation per family on a picogram-input library. **Mechanism:** a large fraction of unique cfDNA molecules are sequenced once (singletons); requiring two reads discards genuine, often the only, evidence for a variant. **Symptom:** sensitivity loss disguised as quality. **Fix:** for detection favor recovery (call permissively); reserve `2 1 1` for genotyping/MRD where error suppression dominates.

### Fragmentomics on a size-selected library
**Trigger:** computing end-motif/ratio/VAF features after in-vitro (Pippin) or in-silico size selection. **Mechanism:** selection conditions on length, so length-derived features are biased by construction. **Symptom:** distorted end-motif spectra and fragment-ratio features that do not reproduce. **Fix:** size-select for detection sensitivity only; never report length-derived features from a length-selected library; keep the selection step in metadata.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Mononucleosome mode 167 bp; ~10.4 bp sub-mode periodicity | Snyder 2016 *Cell* 164:57 | core particle (~147 bp) + linker; periodicity = helical pitch of nucleosome-bound DNA, a QC sanity check |
| TF/CTCF-footprint short fragments 35-80 bp | Snyder 2016 *Cell* 164:57 | sub-nucleosomal protection; only surfaces with ssDNA prep |
| ctDNA principal length 134-144 bp vs 167 bp germline | Underhill 2016 *PLoS Genet* 12:e1006162 | tumor fragments shorter; BRAF V600E mutant 132-145 bp vs WT 165 bp |
| ctDNA-enrichment selection windows 90-150 bp (and 250-320 bp) | Mouliere 2018 *Sci Transl Med* 10:eaat4921 | selecting the short window enriches mutant allele fraction at no extra sequencing cost |
| ssDNA prep mitochondrial / microbial cfDNA enrichment ~10.7x / ~71.3x | Burnham 2016 *Sci Rep* 6:27859 | dsDNA prep is blind to the ultrashort fraction these reside in |
| iDES error-suppression gain ~3x (barcode) x ~3x (in-silico) ~= ~15x | Newman 2016 *Nat Biotechnol* 34:547 | family-size and background polishing are complementary, not redundant |
| Duplex error floor <1 per 1e7 nt | Kennedy 2014 *Nat Protoc* 9:2586 | both-strand concordance requirement |
| FilterConsensusReads defaults: max-read-error 0.025, max-base-error 0.1, max-no-calls 0.2 | fgbio docs | per-read vs per-base vs fraction/count switch (<1.0 = fraction, >=1.0 = count) |
| gDNA-contamination signature: excess mass >180-250 bp / ladder distortion | Snyder 2016 (biology); pre-analytical QC | leukocyte-lysis gDNA is long; a "too clean, too long" library is contaminated, not pristine |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Consensus BAM has garbage coordinates | skipped re-alignment (consensus emitted unmapped) | RE-align consensus reads before FilterConsensusReads |
| UMI bases corrupt mapping / consensus | omitted the `S` skip in the read structure | include the stem: e.g. `6M11S+T` not `6M+T` |
| Duplex run finds no two-strand molecules | grouped with `--strategy adjacency` | regroup with `--strategy paired` |
| FilterConsensusReads rejects valid strand spec | `--min-reads 0 3` (less stringent first) | put the more stringent value first: `3 0` (or `6 3 0`) |
| Deflated VAF / low unique-molecule count | coordinate dedup on no-UMI cfDNA | use UMI families; never naive-dedup quantitative cfDNA |
| Short ctDNA fragments missing after filtering | blanket high MAPQ filter | lower MAPQ threshold; account for short-fragment mapping |
| Apparent ~10 bp size shift "needs correcting" | adaptase (Swift/Accel-1S) chemistry signature | record the prep; do not correct a real chemistry effect |

## References

- Snyder MW, Kircher M, Hill AJ, Daza RM, Shendure J. 2016. Cell-free DNA comprises an in vivo nucleosome footprint that informs its tissues-of-origin. *Cell* 164:57-68. -- 167 bp mode, ~10.4 bp periodicity, 35-80 bp TF/CTCF footprints; the nucleosome-positioning basis of the dedup trap.
- Underhill HR, Kitzman JO, Hellwig S, Welker NC, Daza R, Baker DN, Gligorich KM, Rostomily RC, Bronner MP, Shendure J. 2016. Fragment length of circulating tumor DNA. *PLoS Genet* 12:e1006162. -- ctDNA 134-144 bp vs 167 bp germline.
- Mouliere F, Chandrananda D, Piskorz AM, Moore EK, Morris J, Ahlborn LB, Mair R, Goranova T, Marass F, Heider K, et al. 2018. Enhanced detection of circulating tumor DNA by fragment size analysis. *Sci Transl Med* 10:eaat4921. -- 90-150 bp and 250-320 bp ctDNA-enrichment windows.
- Burnham P, Kim MS, Agbor-Enoh S, Luikart H, Valantine HA, Khush KK, De Vlaminck I. 2016. Single-stranded DNA library preparation uncovers the origin and diversity of ultrashort cell-free DNA in plasma. *Sci Rep* 6:27859. -- ssDNA prep recovers the ultrashort mitochondrial/microbial fraction dsDNA prep discards.
- Newman AM, Lovejoy AF, Klass DM, Kurtz DM, Chabon JJ, Scherer F, Stehr H, Liu CL, Bratman SV, Say C, et al. 2016. Integrated digital error suppression for improved detection of circulating tumor DNA. *Nat Biotechnol* 34:547-555. -- barcode + in-silico error suppression are complementary (~3x each).
- Kennedy SR, Schmitt MW, Fox EJ, Kohrn BF, Salk JJ, Ahn EH, Prindle MJ, Kuong KJ, Shen JC, Risques RA, Loeb LA. 2014. Detecting ultralow-frequency mutations by Duplex Sequencing. *Nat Protoc* 9:2586-2606. -- both-strand concordance and the <1e-7 error floor that single-strand consensus cannot reach.

## Related Skills

- analytical-validation - the LoD/molecule-counting framework input quality feeds
- fragment-analysis - fragmentomics consumes the preprocessed fragment ends
- ctdna-mutation-detection - consensus reads feed low-VAF calling
- tumor-fraction-estimation - sWGS minimal-processing path
- alignment-files/duplicate-handling - general dedup vs the cfDNA UMI caveat
- read-qc/quality-reports - upstream read QC
<!-- END FILE: liquid-biopsy/cfdna-preprocessing/SKILL.md -->

## 子目录：liquid-biopsy/ctdna-mutation-detection

<!-- BEGIN FILE: liquid-biopsy/ctdna-mutation-detection/SKILL.md -->
---
name: bio-ctdna-mutation-detection
description: Detects somatic mutations in circulating tumor DNA, treating low-VAF detection as a signal-versus-noise problem set by error suppression and molecules sampled, not by the choice of caller. Distinguishes de novo CALLING (scanning a panel for unknown variants, bounded by per-locus error and multiple testing) from tumor-informed DETECTION (tracking a pre-specified variant set, where panel integration reaches single-ppm). Covers VarDict and Mutect2 for de novo calling, UMI-aware callers, and a pysam-based known-variant VAF tracker, with matched-WBC subtraction as the mandatory defense against clonal hematopoiesis (the dominant false positive). Use when calling or tracking tumor mutations from plasma cfDNA, setting a VAF threshold, or deciding whether a low-VAF call is tumor versus CHIP.
tool_type: mixed
primary_tool: VarDict
---

## Version Compatibility

Reference examples tested with: pysam 0.22+, pandas 2.2+, VarDictJava 1.8+, GATK 4.5+, Ensembl VEP 111+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: VarDict's `-c -S -E -g` are 1-based BED COLUMN INDICES, not genomic coordinates; var2vcf_valid.pl's `-E` suppresses the END tag (opposite meaning to VarDict's `-E`). VEP gnomAD flags are `--af_gnomade` (exomes)/`--af_gnomadg` (genomes); the bare `--af_gnomad` is a legacy alias that returns only exome AF, so prefer the explicit forms.

# ctDNA Mutation Detection

**"Detect mutations in my cfDNA sample"** -> Either scan a panel for unknown low-VAF somatic variants (de novo calling) or quantify a pre-specified mutation set across samples (tumor-informed tracking) — two different statistical problems.
- CLI: `vardict-java | teststrandbias.R | var2vcf_valid.pl` for de novo low-VAF calling on a consensus BAM
- CLI: `gatk Mutect2` with the read-orientation model for de novo calling with artifact filtering
- Python: `pysam` pileup of ref/alt counts at fixed loci for known-variant tracking (MRD)

## The Single Most Important Modern Insight -- detection is a signal-vs-noise problem, and tracking is not the same problem as calling

Low-VAF ctDNA detection is set by two limits that no caller can overcome: the per-base error floor (raw Illumina ~1e-3 caps naive VAF detection near 0.5-1%) and the number of tumor molecules physically present in the tube (1 ng cfDNA ~= 303 haploid genome-equivalents; at 0.01% VAF in 10 ng the expected mutant count is ~0.3 copies — there is nothing to detect at any depth). The achieved limit of detection is the worse of the two. Error suppression (UMI consensus -> ~1e-5, duplex -> <1e-7) and input mass move the floor; swapping VarDict for Mutect2 does not.

Critically, de novo CALLING and known-variant DETECTION are different statistical problems. De novo calling scans every covered position for an unknown alt and pays a multiple-testing tax across 1e5-1e6 loci, so per-locus thresholds must be stringent (practical LoD ~0.1-0.5% on UMI consensus). Tumor-informed detection tests ONE hypothesis — "is tumor present?" — by integrating signal across a pre-specified set of N patient-specific loci; the multiple-testing penalty collapses and per-locus signal that is individually indistinguishable from noise sums into a confident panel-level call. This is why per-locus LoD is poor while panel-integrated LoD reaches single-ppm. Conflating the two is the most common conceptual error in the field.

## Methods Landscape

| Method | Class | Citation | Role | When |
|--------|-------|----------|------|------|
| VarDict / vardict-java | de novo caller | AstraZeneca-NGS | sensitive low-VAF amplicon/capture calling with explicit strand-bias test | de novo panel calling on a UMI-consensus BAM |
| Mutect2 (tumor-only) | de novo caller | GATK | local-assembly somatic caller + learned orientation-bias artifact model | de novo calling needing FFPE/OxoG artifact filtering, PoN, germline resource |
| umi-varcal | UMI-aware caller | Sater 2020 *Bioinformatics* 36(9):2718 | own UMI-aware pileup + per-position Poisson test against local background | UMI-tagged BAM where a consensus-aware caller is wanted (floor ~0.3%) |
| CAPP-Seq / iDES | tumor-informed integration | Newman 2014 *Nat Med* 20:548; 2016 *Nat Biotechnol* 34:547 | hybrid-capture deep panel + molecular barcoding + in-silico background polishing | de novo ctDNA to ~0.02%; iDES stacks ~15x error suppression |
| INVAR | tumor-informed integration | Wan 2020 *Sci Transl Med* 12:eaaz8084 | integrate variant reads across 100s-1000s patient loci, background-weighted | MRD/monitoring with tumor WES; quantifies to ~1e-5, best ~2.5 ppm |
| MRDetect | tumor-informed integration | Zviran 2020 *Nat Med* 26:1114 | shallow WGS vs patient SNV compendium, read-level SVM noise model | MRD trading depth for breadth (~35x WGS, thousands of SNVs); ~1e-5 |
| PhasED-Seq | tumor-informed integration | Kurtz 2021 *Nat Biotechnol* 39:1537 | enrich phased (co-occurring) variants to suppress single-molecule error | sub-ppm MRD where phased variants are available |

Per-locus LoD for any of these is error- and sampling-limited (~0.1-0.5%); the tumor-informed methods reach ppm only by integrating across a known, large, patient-specific variant set. Methodology evolves — verify current best practice against each tool's live docs before committing to one.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Tumor tissue available, MRD/monitoring of a known cancer | Tumor-informed tracking (INVAR/MRDetect/Signatera-class), or the pysam tracker below for a fixed list | Integrating across N pre-specified loci is the only route to ppm; CHIP excluded by construction (CHIP variants are not on the tumor list) |
| No tumor tissue, screening/discovery | de novo panel calling (VarDict or Mutect2) + matched WBC | Must scan for unknown variants; CHIP subtraction is mandatory or most calls are not tumor |
| VAF regime > 1% | Any standard caller on a deduplicated BAM | Above the raw error floor; consensus not strictly required |
| VAF regime 0.1-1% | UMI single-strand consensus + VarDict/umi-varcal/Mutect2 | Below the raw 1e-3 floor; consensus needed to recover real signal from error |
| VAF regime < 0.1% | Duplex consensus + tumor-informed integration | Single-strand consensus cannot remove one-strand deamination/oxidation; only duplex + panel integration reaches this regime |
| No matched WBC available | Do NOT report de novo calls as somatic-tumor | Without WBC subtraction, CHIP (the majority of non-germline cfDNA variants) is indistinguishable from tumor |

## CHIP -- the dominant false positive, not background

Clonal hematopoiesis of indeterminate potential (CHIP) is the single largest source of false-positive somatic calls in plasma, and it is the null hypothesis for any low-VAF cfDNA variant. Razavi 2019 sequenced cfDNA with matched white-blood-cell DNA (508 genes, >60,000x) and found that **53.2% of non-germline cfDNA variants in cancer patients and 81.6% in non-cancer controls** had features consistent with clonal hematopoiesis; only ~24.4% of cfDNA somatic variants in patients were also in the matched tumor (the remainder split between white-cell CHIP and variants of uncertain origin). These are bona fide somatic mutations — in cancer genes — that come from lysed leukocytes, not tumor. No error-suppression tier removes them because they are not errors.

The biology: CHIP arises in hematopoietic stem cells and rises steeply with age (Jaiswal 2014: ~10% prevalence over age 70), enriched for PPM1D/TP53/CHEK2 clones after prior chemo/radiation — exactly the monitored population. The canonical genes are DNMT3A, TET2, ASXL1 (the big three), then PPM1D, TP53, JAK2, SF3B1, SRSF2, GNB1, GNAS, CBL, ATM, CHEK2. TP53 and ATM are both CHIP genes and bona fide tumor suppressors, so a low-VAF TP53 cfDNA call is the ambiguous case par excellence.

The only reliable filter is matched buffy-coat/WBC subtraction: sequence the WBC fraction of the same draw at comparable depth and remove any cfDNA variant also present in WBC. gnomAD filtering removes germline only — CHIP variants are somatic and absent from germline databases, so they sail straight through. A canonical-CHIP-gene list (the example's `CHIP_GENES`) is a heuristic flag for extra scrutiny, NOT a substitute for WBC subtraction. See analytical-validation for the LoB/LoD statistics that quantify how confidently a subtracted call clears background.

## De Novo Calling with VarDict

**Goal:** Scan a target panel for unknown low-VAF somatic variants on a UMI-consensus BAM.

**Approach:** Run vardict-java with a lowered `-f`, pipe through the strand-bias test, then convert to VCF — matching `-f` across both stages so the threshold is not silently re-applied.

```bash
AF_THR=0.005   # 0.5% — practical UMI-consensus de novo floor; below this approaches the per-base error floor
vardict-java -G ref.fa -f $AF_THR -N sample -b consensus.bam \
  -c 1 -S 2 -E 3 -g 4 targets.bed | \
  teststrandbias.R | \
  var2vcf_valid.pl -N sample -E -f $AF_THR > sample.vcf
```

Key flags: `-G` indexed reference; `-f` min VAF (VarDict default 0.01); `-N` sample name; `-b` BAM. `-c 1 -S 2 -E 3 -g 4` are the 1-based BED COLUMN INDICES for chrom/start/end/gene in a standard 4-column BED — they are column positions, not genomic values. On var2vcf_valid.pl, `-E` means "do NOT print the END tag" (unrelated to VarDict's `-E`); its `-f` default is 0.02, so set it to match. For PCR/amplicon data add `-P 0` (positional std is expected to be ~0). For paired tumor/normal use the `testsomatic.R | var2vcf_paired.pl` path instead.

## De Novo Calling with Mutect2 and the Orientation-Bias Model

**Goal:** Call de novo somatic variants while filtering FFPE-deamination (C>T) and OxoG (G>T) strand-biased artifacts that dominate low-VAF false positives.

**Approach:** Collect F1R2/F2R1 counts during calling, learn the orientation-bias prior, then apply it during filtering alongside a panel of normals and germline resource.

```bash
gatk Mutect2 -R ref.fa -I consensus.bam --f1r2-tar-gz f1r2.tar.gz \
  --germline-resource af-only-gnomad.vcf.gz --panel-of-normals pon.vcf.gz \
  -O unfiltered.vcf.gz
gatk LearnReadOrientationModel -I f1r2.tar.gz -O read-orientation-model.tar.gz
gatk FilterMutectCalls -R ref.fa -V unfiltered.vcf.gz \
  --ob-priors read-orientation-model.tar.gz -O filtered.vcf.gz
```

Mutect2 is run tumor-only here (no normal sample arg); the orientation model is the load-bearing low-VAF filter. At true ctDNA VAFs Mutect2 is underpowered relative to a dedicated UMI/duplex + background-polishing pipeline, and local assembly can miss extremely low-AF alt support — it is a reasonable de novo caller on consensus reads with the orientation model + PoN (and ideally a matched normal, not shown in this tumor-only command), not a substitute for tumor-informed integration at ppm.

## Track Known Mutations Across Serial Samples

**Goal:** Quantify the VAF of a pre-specified mutation set at fixed loci for MRD monitoring — the detection (not calling) problem.

**Approach:** For each target mutation, pileup reads at the position, count ref/alt/other alleles, and compute VAF with depth; aggregate across loci as the panel-level detection signal. The single-base pileup below tracks SNVs only — indel reporters (e.g. EGFR exon-19 deletions) need `read.indel`/CIGAR-aware counting; a single-base comparison silently scores every indel read as `other` and reports the locus as cleared.

```python
import pysam

def track_known_variants(bam_file, variants):
    '''Pileup ref/alt counts at fixed (chrom, pos, ref, alt) SNV loci; pos is 1-based.
    SNVs only - indel reporters need read.indel/CIGAR handling, not a single-base compare.'''
    bam = pysam.AlignmentFile(bam_file, 'rb')
    rows = []
    for chrom, pos, ref, alt in variants:
        counts = {'ref': 0, 'alt': 0, 'other': 0}
        for col in bam.pileup(chrom, pos - 1, pos, truncate=True):
            for read in col.pileups:
                if read.is_del or read.is_refskip:
                    continue
                base = read.alignment.query_sequence[read.query_position]
                counts['alt' if base == alt else 'ref' if base == ref else 'other'] += 1
        depth = sum(counts.values())
        rows.append({'chrom': chrom, 'pos': pos, 'ref': ref, 'alt': alt,
                     'depth': depth, 'alt_count': counts['alt'],
                     'vaf': counts['alt'] / depth if depth else 0.0})
    bam.close()
    return rows
```

Annotate calls for interpretation with Ensembl VEP (`--cache --offline --fasta --vcf --everything`); the gnomAD allele-frequency flags are `--af_gnomade` (exomes) and `--af_gnomadg` (genomes) — the bare `--af_gnomad` is a legacy alias returning only exome AF. gnomAD presence separates germline; only WBC presence separates CHIP.

## Per-Method Failure Modes

### CHIP misclassified as tumor
Trigger: de novo calling without matched WBC. Mechanism: leukocyte-derived clonal somatic variants in cancer genes look identical to tumor signal and pass gnomAD filtering. Symptom: low-VAF calls in DNMT3A/TET2/TP53; "tumor" mutations not in the matched tissue. Fix: subtract matched buffy-coat/WBC genotype; never report somatic-tumor without it.

### Strand-biased / deamination artifacts at low VAF
Trigger: FFPE-style C>T or oxidative G>T at VAF near the floor. Mechanism: damage on one template strand is inherited by every PCR copy, so single-strand UMI consensus votes unanimously for the artifact. Symptom: alt support concentrated on one strand. Fix: VarDict strand-bias test or Mutect2 orientation model; for sub-0.1% require duplex consensus.

### Calling below the error floor
Trigger: lowering `-f` to e.g. 0.001 on a non-consensus BAM. Mechanism: the raw ~1e-3 error rate manufactures alt reads at that frequency. Symptom: a flood of low-VAF calls scaling with depth. Fix: do consensus upstream; do not set a VAF threshold below the demonstrated error floor of the input.

### Germline-vs-somatic confusion at low coverage
Trigger: classifying by VAF alone when depth is low. Mechanism: a true 50% het reads 3/12 = 0.25 by chance. Symptom: germline hets mislabeled subclonal somatic. Fix: gnomAD + matched-WBC presence (germline ~0.5 in WBC; CHIP at clone VAF; tumor-only absent from WBC).

### Per-locus LoD quoted as the assay LoD
Trigger: reporting a single-variant sensitivity for a multi-locus tracking assay (or vice versa). Mechanism: panel-integrated LoD is orders of magnitude below per-locus LoD. Symptom: a "0.1%" claim that does not match observed ppm-level tracking. Fix: state per-locus vs panel-integrated explicitly; see analytical-validation.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Raw Illumina error ~1e-3 caps naive VAF near 0.5-1% | Schmitt 2012 *PNAS* 109:14508 | Per-base miscall rate sets the per-locus VAF floor; alt support below it is mostly error |
| UMI single-strand consensus -> ~1e-5; duplex -> <1e-7 | Schmitt 2012; Newman 2016 *Nat Biotechnol* 34:547 | Family consensus erases PCR/sequencing error; duplex strand concordance also catches one-strand damage |
| CAPP-Seq de novo LoD ~0.02% at 96% specificity | Newman 2014 *Nat Med* 20:548 | Deep hybrid-capture + reporter set; demonstrates the de novo panel floor |
| iDES ~15x error suppression (UMI ~3x x polishing ~3x) | Newman 2016 *Nat Biotechnol* 34:547 | Molecular consensus and in-silico background polishing are orthogonal and stack |
| INVAR quantifies to ~1e-5, detects to ~2.5 ppm | Wan 2020 *Sci Transl Med* 12:eaaz8084 | Integrating variant reads across 100s-1000s of patient loci collapses multiple testing |
| MRDetect ~1e-5 tumor fraction at ~35x WGS, 95% spec | Zviran 2020 *Nat Med* 26:1114 | Breadth (thousands of SNVs) + read-level SVM (~14.4x error reduction) substitutes for depth |
| CHIP = 53.2% (cancer pts) / 81.6% (controls) of cfDNA variants | Razavi 2019 *Nat Med* 25:1928 | Most non-germline cfDNA variants are not tumor; matched WBC is mandatory |
| Depth >= 1000-5000x unique consensus for panels | community / Phallen 2017 *Sci Transl Med* 9:eaan2415 (~30,000x) | Detecting <1% VAF needs enough unique molecules sampled at each locus |
| ~303 genome-equivalents per ng cfDNA (3.3 pg/haploid) | standard constant | Input mass sets a hard Poisson ceiling on detectable VAF independent of sequencing |
| LoB / LoD / LoD95 per CLSI EP17 | CLSI EP17-A2 | A bare VAF without input mass + replicate detection rate is not a sensitivity spec |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Flood of low-VAF calls scaling with depth | `-f` set below the input's error floor on non-consensus reads | Do UMI/duplex consensus first; keep `-f` >= demonstrated floor |
| VarDict emits nothing or wrong regions | `-c -S -E -g` read as genomic values | They are 1-based BED column indices; use `-c 1 -S 2 -E 3 -g 4` for a 4-column BED |
| var2vcf re-filters away VarDict calls | var2vcf_valid.pl `-f` default 0.02 mismatched | Set var2vcf `-f` to match VarDict's `-f` |
| Real amplicon calls dropped as positional artifacts | var2vcf `-P` (filter pstd=0) on by default | Add `-P 0` for PCR/amplicon data |
| "Tumor" variants absent from matched tissue | CHIP not subtracted | Sequence and subtract matched WBC; flag CHIP-gene hits |
| `--af_gnomad` returns only exome AF | bare flag is a legacy exome-only alias | Use `--af_gnomade` (exomes) / `--af_gnomadg` (genomes) |
| ppm "LoD" not reproducible | per-locus LoD quoted for a tracking assay | Report panel-integrated LoD with input mass and LoD95 |

## References

- Schmitt MW, Kennedy SR, Salk JJ, Fox EJ, Hiatt JB, Loeb LA. 2012. Detection of ultra-rare mutations by next-generation sequencing. *Proc Natl Acad Sci USA* 109(36):14508-14513. — Duplex Sequencing; DCS error <1e-7.
- Newman AM, Bratman SV, To J, et al. 2014. An ultrasensitive method for quantitating circulating tumor DNA with broad patient coverage. *Nat Med* 20(5):548-554. — CAPP-Seq; ~0.02% LoD.
- Newman AM, Lovejoy AF, Klass DM, et al. 2016. Integrated digital error suppression for improved detection of circulating tumor DNA. *Nat Biotechnol* 34(5):547-555. — iDES; UMI + background polishing.
- Phallen J, Sausen M, Adleff V, et al. 2017. Direct detection of early-stage cancers using circulating tumor DNA. *Sci Transl Med* 9(403):eaan2415. — TEC-Seq deep panel.
- Razavi P, Li BT, Brown DN, et al. 2019. High-intensity sequencing reveals the sources of plasma circulating cell-free DNA variants. *Nat Med* 25(12):1928-1937. — CHIP is the majority of cfDNA variants; matched WBC.
- Wan JCM, Heider K, Gale D, et al. 2020. ctDNA monitoring using patient-specific sequencing and integration of variant reads. *Sci Transl Med* 12(548):eaaz8084. — INVAR; integration to ~2.5 ppm.
- Zviran A, Schulman RC, Shah M, et al. 2020. Genome-wide cell-free DNA mutational integration enables ultra-sensitive cancer monitoring. *Nat Med* 26(7):1114-1124. — MRDetect; shallow WGS + read SVM.
- Kurtz DM, Soo J, Co Ting Keh L, et al. 2021. Enhanced detection of minimal residual disease by targeted sequencing of phased variants in circulating tumor DNA. *Nat Biotechnol* 39(12):1537-1547. — PhasED-Seq; phased-variant enrichment.
- Sater V, Viailly P-J, Lecroq T, et al. 2020. UMI-VarCal: a new UMI-based variant caller that efficiently improves low-frequency variant detection in paired-end sequencing NGS libraries. *Bioinformatics* 36(9):2718-2724. — UMI-aware pileup + per-position Poisson test.

## Related Skills

- cfdna-preprocessing - UMI/duplex consensus input that sets the error floor
- analytical-validation - LoD/LoB and the panel-integration math behind detection
- longitudinal-monitoring - track detected variants across serial samples
- tumor-fraction-estimation - orthogonal burden estimate to cross-check
- variant-calling/variant-calling - general somatic calling principles
- clinical-databases/variant-prioritization - clinical annotation and interpretation
<!-- END FILE: liquid-biopsy/ctdna-mutation-detection/SKILL.md -->

## 子目录：liquid-biopsy/fragment-analysis

<!-- BEGIN FILE: liquid-biopsy/fragment-analysis/SKILL.md -->
---
name: bio-fragment-analysis
description: Extracts cfDNA fragmentomics features (DELFI genome-wide short/long ratios, WPS nucleosome positioning, Griffin GC-corrected accessibility profiles, end-motifs/MDS, OCF) for cancer detection and tissue-of-origin from plasma WGS. Centers on the nuclease-footprint reframe (every feature re-reads one nucleosome object), the mandatory GC correction, and the cross-protocol non-comparability that breaks naive classifiers. Runs FinaleToolkit (real CLI/Python, MIT) and the Griffin Snakemake pipeline; DELFI is a method, not a package. Use when deriving fragment-based signal from cfDNA, choosing a feature family for detection vs subtyping, or diagnosing why a fragmentomic model failed validation.
tool_type: python
primary_tool: FinaleToolkit
---

## Version Compatibility

Reference examples tested with: numpy 1.26+, pandas 2.2+, pysam 0.22+, finaletoolkit 0.7+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: FinaleToolkit CLI subcommands are hyphenated (`frag-length-bins`, `end-motifs`, `delfi-gc-correct`); the Python functions are underscored in `finaletoolkit.frag`. The filter subcommand is `filter-file`, NOT `filter-bam`. Griffin is a Snakemake pipeline, not an importable function. DELFI is a methodology and a company (DELFI Diagnostics), not a `pip install`-able tool.

# Fragment Analysis

**"Analyze cfDNA fragment patterns for cancer signal"** -> Quantify nucleosome-footprint features (size ratios, protection scores, accessibility profiles, end motifs) from plasma WGS for detection or tissue-of-origin.
- Python/CLI: `finaletoolkit` for DELFI ratios, WPS, end-motifs, MDS, cleavage profiles
- Snakemake: `Griffin` pipeline for GC-corrected nucleosome profiling at TF/accessible sites
- Python: `pysam` for a custom binned short/long ratio when a dependency-light readout is wanted

## The Single Most Important Modern Insight -- Fragmentomics measures nucleosome positioning, not sequence; the biology is real but it can be destroyed in the wet lab or left un-GC-corrected

Plasma cfDNA is the digestion product of chromatin by apoptotic and intracellular nucleases, so every fragmentomic feature is a re-readout of the same physical object: the nucleosome footprint. The ~167 bp mode is the 147 bp histone-protected core plus ~20 bp of linker; the 10.4 bp sawtooth below it is the helical pitch of DNA on the histone surface (the nuclease cuts only where the minor groove faces out, once per turn). DELFI ratios, WPS, Griffin profiles, end-motifs, and OCF are four views of this one object, not four independent measurements -- their correlation inflates apparent multi-feature performance and leaks across train/test splits.

Two consequences dominate practice. First, the single biggest threat to any fragmentomic feature is GC, library, and batch confounding, not biology: an uncorrected genome-wide short/long ratio tracks GC content and library prep far more strongly than tumor fraction, which is why naive fragmentomics works in discovery and dies in validation. Griffin's actual contribution is its fragment-length-specific GC correction, not the nucleosome plot. Second, DELFI-style ratios are partly entangled with copy-number alteration and coverage (a bin's ratio reflects both fragmentation state and how many genomes contributed): deconvolving the fragmentation-specific signal from CNA is a known open problem, so a raw 5 Mb ratio is a hybrid CNA + fragmentation + GC readout, not pure fragmentation.

## Methods / Feature-Family Landscape

| Feature family | Primary method | What it physically measures | Citation |
|---|---|---|---|
| Genome-wide short/long ratio | DELFI: ~5 Mb bins, GC-corrected short(100-150)/long(151-220), boosted classifier | Coarse fragmentation state across the genome (entangled with CNA + GC) | Cristiano 2019 Nature 570:385 |
| Nucleosome positioning | WPS: spanning fragments minus end-containing fragments in a sliding window | Where nucleosomes sit; promoter/gene-body phasing encodes tissue + expression | Snyder 2016 Cell 164:57 |
| GC-corrected accessibility | Griffin: length-specific GC correction then composite coverage around site sets | TF/DHS accessibility in the tissue of origin; robust at low tumor fraction | Doebley 2022 Nat Commun 13:7475 |
| End motifs / MDS | 4-mer at the 5' cut site; MDS = normalized Shannon entropy of the 256 motifs | Nuclease-cleavage signature (DNASE1L3 sculpts the normal CC-ending spectrum) | Jiang 2020 Cancer Discov 10:664 |
| Orientation-aware ends | OCF: phase offset between upstream- and downstream-end peaks in open chromatin | Tissue-of-origin via end orientation, not coverage | Sun 2019 Genome Res 29:418 |

DELFI = DNA EvaLuation of Fragments; the end-motif/MDS biology is anchored in DNASE1L3, whose deletion reorders length and end-motif frequencies (Serpas 2019 PNAS 116:641). Methodology here is still evolving (CNA deconvolution, standalone GC correctors like GCparagon) -- verify current best practice against live FinaleToolkit and Griffin docs before committing to one feature family.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|---|---|---|
| Cancer detection, pan-genome screen | DELFI genome-wide short/long profile (FinaleToolkit `delfi`) | Coarse genome-wide signal is what the boosted classifier was built on; cheap at low-pass WGS |
| Tissue / subtype of origin (e.g. ER status, NEPC) | Griffin nucleosome profiling around TF/accessible site sets | Accessibility composite scales with the contributing tissue; the GC correction makes it portable |
| Low tumor fraction (TF < ~0.03) | Griffin (GC-correction removes dominant technical signal) and/or in-silico size selection (90-150 bp) | Raw ratios are GC-dominated at low TF; Griffin holds AUC ~0.92 vs ~0.99 at TF >= 0.05 |
| Nuclease / cleavage biology, single-scalar comparison | End-motifs + MDS (FinaleToolkit `end-motifs` then `mds`) | MDS is one number per sample; rises in cancer as orderly DNASE1L3 cleavage is lost |
| Nucleosome positions / TF footprints directly | WPS (FinaleToolkit `wps` + `adjust-wps`) | WPS peaks recover nucleosome positions; S-WPS exposes TF footprints |
| Any cross-batch or cross-protocol comparison | GC-correct AND co-process through one pipeline, or do not compare | Uncorrected, cross-protocol fragmentomics is uninterpretable (see Failure Modes) |

## Genome-Wide Short/Long Ratio (custom DELFI-style)

**Goal:** Produce a genome-wide vector of short-to-long fragment ratios in fixed bins as a dependency-light DELFI-style feature, with the explicit caveat that without GC correction it is a GC + CNA readout.

**Approach:** Walk proper-pair fragments per bin from the BAM template length, classify each as short (100-150 bp) or long (151-220 bp), and emit the per-bin ratio. For a publication-grade profile, prefer FinaleToolkit `delfi` (which GC-corrects) over this illustrative version.

```python
import pysam
import numpy as np
import pandas as pd

def binned_short_long_ratio(bam_path, bin_size=5_000_000, chroms=None):
    '''Per-bin short(100-150)/long(151-220) ratio. NOT GC-corrected -- illustrative only.'''
    chroms = chroms or [f'chr{i}' for i in range(1, 23)]
    bam = pysam.AlignmentFile(bam_path, 'rb')
    rows = []
    for chrom in chroms:
        if chrom not in bam.references:
            continue
        n_bins = bam.get_reference_length(chrom) // bin_size + 1
        short = np.zeros(n_bins)
        long = np.zeros(n_bins)
        for read in bam.fetch(chrom):
            if not read.is_proper_pair or read.is_secondary or read.template_length <= 0:
                continue
            size = read.template_length
            b = read.reference_start // bin_size
            if 100 <= size <= 150:
                short[b] += 1
            elif 151 <= size <= 220:
                long[b] += 1
        ratio = np.divide(short, long, out=np.full(n_bins, np.nan), where=long > 0)
        rows.extend({'chrom': chrom, 'bin': i, 'short': short[i], 'long': long[i], 'ratio': ratio[i]} for i in range(n_bins))
    bam.close()
    return pd.DataFrame(rows)
```

## GC-Corrected DELFI Score (FinaleToolkit)

**Goal:** Compute a GC-corrected DELFI score so the genome-wide profile reflects fragmentation rather than base composition.

**Approach:** FinaleToolkit's `delfi` corrects short and long bin counts for GC before forming the ratio; the CLI and Python API are equivalent. Run on a BAM/CRAM or a tabix-indexed `.frag.gz` fragment file.

```bash
# CLI (subcommands are hyphenated). delfi positionals: input chrom_sizes reference bins_file.
# GC correction is ON by default (-G disables it); 100kb bins are merged to 5Mb by default.
# -R keeps no-coverage regions when the genome is not hg19.
finaletoolkit delfi sample.bam hg38.chrom.sizes hg38.fa bins_100kb.bed -g gaps.bed -R -o sample.delfi.bed
finaletoolkit end-motifs sample.bam hg38.fa -o sample.end_motifs.tsv
finaletoolkit mds sample.end_motifs.tsv          # Motif Diversity Score (normalized Shannon entropy)
finaletoolkit wps sample.bam sites.bed -c hg38.chrom.sizes -o sites.wps.bw   # per-site, not a single region
```

```python
from finaletoolkit.frag import delfi, end_motifs, wps  # public finaletoolkit.frag symbols
# delfi() returns GC-corrected short/long per bin; end_motifs() returns an EndMotifFreqs
# object whose .motif_diversity_score() gives the MDS (there is no top-level frag.mds).
```

## Griffin Nucleosome Profiling (Snakemake pipeline)

**Goal:** Obtain GC-corrected composite coverage around a TF/accessible-site set for tissue-of-origin, robust at low tumor fraction and ~0.1x WGS.

**Approach:** Griffin is not an importable function; it is three sequential Snakemake modules. Run them in order against `samples.yaml`, the hg38 reference, and a `sites.yaml` site list.

```bash
# Run each module from Griffin's snakemakes/ dir (config edited per cohort)
snakemake -s griffin_genome_GC_frequency/griffin_genome_GC_frequency.snakefile --cores 8
snakemake -s griffin_GC_and_mappability_correction/griffin_GC_and_mappability_correction.snakefile --cores 8
snakemake -s griffin_nucleosome_profiling/griffin_nucleosome_profiling.snakefile --cores 8
# Output: GC-corrected + uncorrected composite coverage profiles around each site set.
```

## Per-Method Failure Modes

### Uncorrected GC dominates the ratio
Trigger: comparing raw short/long ratios across samples without GC correction. Mechanism: PCR and binding-based purification overrepresent GC-balanced fragments, and short vs long fragments have different GC dependence. Symptom: a beautiful discovery-cohort separation that collapses in validation; the profile clusters by sequencing batch. Fix: GC-correct (FinaleToolkit `delfi`/`delfi-gc-correct`, Griffin, or GCparagon) and co-process all samples through one pipeline.

### Cross-protocol non-comparability
Trigger: combining ssDNA and dsDNA libraries, or two end-repair/PCR chemistries, in one analysis. Mechanism: ssDNA prep recovers the sub-100 bp ultrashort population that dsDNA prep loses at the double-strand ligation step, shifting the entire size distribution and every derived feature. Symptom: a model trained on one chemistry mislabels the other systematically. Fix: a fragmentomic model is conditioned on its library chemistry -- match protocols, never cross them, and state the prep as a precondition.

### DELFI / CNA entanglement
Trigger: interpreting a 5 Mb ratio bin as pure fragmentation. Mechanism: copy-number alterations change how many genomes contribute to a bin, moving coverage and therefore the ratio independent of fragmentation. Symptom: ratio "signal" that mirrors the CNA profile. Fix: treat DELFI as a hybrid CNA + fragmentation + GC feature; deconvolve with caution and do not overclaim a pure fragmentation readout.

### Low-coverage WPS noise
Trigger: computing WPS or per-site profiles on too few fragments. Mechanism: WPS is a difference of spanning vs end-containing counts; at low coverage both terms are tiny and the score is dominated by sampling noise. Symptom: no clean nucleosome periodicity, jagged tracks. Fix: aggregate over many copies of a site (composite profiles, Griffin/`multi_wps`), smooth (`adjust-wps`), and require adequate depth before single-locus WPS.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|---|---|---|
| Mononucleosome mode ~167 bp (147 core + ~20 linker) | Snyder 2016 Cell 164:57 | The protected core is 147 bp; the variable ~20 bp linker is the rest of the mode |
| 10.4 bp periodicity below 167 bp | Snyder 2016 | Helical pitch of B-form DNA; the cleanest sanity check that footprints and size estimation are sane |
| Di-/tri-nucleosome ~334 / ~500 bp | Snyder 2016 | Successive nucleosomes add ~167 bp each |
| ctDNA mode ~20-50 bp shorter (toward ~145 bp), enrich 90-150 bp | Mouliere 2018 Sci Transl Med 10:eaat4921 | Tumor chromatin/nuclease processing shifts length down; the lever size selection exploits |
| Short 100-150 bp vs long 151-220 bp | Cristiano 2019 Nature 570:385 | The DELFI ratio numerator/denominator windows |
| ~5 Mb DELFI bins | Cristiano 2019 | Bin scale at which the genome-wide ratio vector was defined and classified |
| In-silico size selection 90-150 bp | Mouliere 2018 | Retaining this window enriches tumor fraction >2x in >95% of cases, >4x in >10% |
| End-motif 4-mer, 256 categories; MDS = normalized Shannon entropy | Jiang 2020 Cancer Discov 10:664 | The categorical end-motif space and its single-scalar diversity summary |

Size selection is a tumor-fraction-vs-depth lever, not a universal win: it discards the 167 bp bulk, so it helps when ctDNA is dilute and short but hurts when already depth-limited.

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `pip install delfi` fails / no DELFI CLI | DELFI is a method + company, not a package | Compute DELFI features via FinaleToolkit `delfi`, or a custom binned ratio |
| `finaletoolkit filter-bam` not found | The subcommand is `filter-file`, not `filter-bam` | Use `finaletoolkit filter-file` for mapq/size/region filtering |
| `import griffin` fails | Griffin is a Snakemake pipeline, not an importable module | Run the three `griffin_*` snakefiles in sequence |
| Profiles cluster by batch, not biology | Uncorrected GC / mixed protocols | GC-correct and co-process one chemistry through one pipeline |
| Confusing end-motif and breakpoint-motif | Different objects (cut-site 4-mer vs k-mer spanning the cut) | FinaleToolkit exposes both: `end-motifs` vs `breakpoint-motifs` |

## References

- Snyder MW, Kircher M, Hill AJ, Daza RM, Shendure J. 2016. Cell-free DNA comprises an in vivo nucleosome footprint that informs its tissues-of-origin. *Cell* 164(1-2):57-68. -- nucleosome footprint, 167 bp, 10.4 bp periodicity, WPS.
- Cristiano S, Leal A, Phallen J, et al. 2019. Genome-wide cell-free DNA fragmentation in patients with cancer. *Nature* 570(7761):385-389. -- DELFI; 5 Mb bins, short/long ratio.
- Mouliere F, Chandrananda D, Piskorz AM, et al. 2018. Enhanced detection of circulating tumor DNA by fragment size analysis. *Sci Transl Med* 10(466):eaat4921. -- size selection, 90-150 bp enrichment.
- Doebley A-L, Ko M, Liao H, et al. 2022. A framework for clinical cancer subtyping from nucleosome profiling of cell-free DNA. *Nat Commun* 13:7475. -- Griffin; length-specific GC correction.
- Jiang P, Sun K, Peng W, et al. 2020. Plasma DNA end-motif profiling as a fragmentomic marker in cancer, pregnancy, and transplantation. *Cancer Discov* 10(5):664-673. -- end motifs and MDS (journal is *Cancer Discovery*, not PNAS).
- Sun K, Jiang P, Wong AIC, et al. 2019. Orientation-aware plasma cell-free DNA fragmentation analysis in open chromatin regions informs tissue of origin. *Genome Res* 29(3):418-427. -- OCF.
- Serpas L, Chan RWY, Jiang P, et al. 2019. Dnase1l3 deletion causes aberrations in length and end-motif frequencies in plasma DNA. *PNAS* 116(2):641-649. -- DNASE1L3 biology behind end motifs.
- Burnham P, Kim MS, Agbor-Enoh S, et al. 2016. Single-stranded DNA library preparation uncovers the origin and diversity of ultrashort cell-free DNA in plasma. *Sci Rep* 6:27859. -- ssDNA prep recovers ultrashort cfDNA.
- FinaleToolkit: accelerating cell-free DNA fragmentation analysis with a high-speed computational toolkit. 2025. *Bioinformatics Advances* 5(1):vbaf236. -- the toolkit; ~50x faster WPS than the original Snyder implementation on BH01 (scope-limited).

## Related Skills

- cfdna-preprocessing - library prep determines which fragments (and features) are recoverable
- tumor-fraction-estimation - fragmentomics enables signal below the CNA-based TF floor
- methylation-based-detection - orthogonal genome-wide cfDNA signal
- atac-seq/nucleosome-positioning - shared nucleosome-footprint biology
<!-- END FILE: liquid-biopsy/fragment-analysis/SKILL.md -->

## 子目录：liquid-biopsy/longitudinal-monitoring

<!-- BEGIN FILE: liquid-biopsy/longitudinal-monitoring/SKILL.md -->
---
name: bio-longitudinal-monitoring
description: Tracks ctDNA across serial liquid-biopsy timepoints for molecular residual disease (MRD) and treatment-response monitoring, treating MRD as a binary integrated detection call across the patient's full variant set (with a defined LoD95 and per-sample specificity) rather than a per-timepoint VAF threshold, and handling undetectable samples as left-censored at the per-sample limit of detection rather than true zeros. Covers tumor-informed bespoke vs tumor-naive design, landmark vs surveillance sampling, molecular-response definitions and their non-standardization, censoring-aware clearance kinetics, and the multiple-testing structure of repeated surveillance. Use when monitoring ctDNA during therapy, calling molecular relapse before imaging, or estimating clearance half-life from serial samples.
tool_type: python
primary_tool: pandas
---

## Version Compatibility

Reference examples tested with: numpy 1.26+, pandas 2.2+, scipy 1.12+, matplotlib 3.8+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: this skill is statistical, not tool-bound. The hard parts are interpretive (left-censoring, multiple testing, lead-time bias), not API calls. `scipy.stats.linregress` returns a named tuple whose `.slope`/`.pvalue` attributes are stable across recent versions; the censoring-aware fit below uses only `linregress` on the uncensored decay phase plus a manual interval check, so version drift is low-risk.

# Longitudinal Monitoring

**"Track ctDNA over this course of treatment"** -> Integrate serial plasma measurements into a binary detected/not-detected trajectory plus censoring-aware burden kinetics for MRD and response monitoring.
- Python: `pandas` for the per-timepoint table, `scipy.stats` for censoring-aware decay/trend, `matplotlib` for log-scale trajectory plots

## The Single Most Important Modern Insight -- MRD is a binary integrated detection call, and "undetectable" is left-censored, not zero

A tumor-informed MRD assay does not ask "is the VAF at locus X above a threshold?" It integrates signal across the patient's entire personal variant set (16 to 500+ loci) into ONE detected/not-detected call with a defined LoD95 (the tumor fraction detected 95% of the time at a given input) and a per-sample specificity. Signal invisible at any single 0.001%-VAF locus becomes significant when summed across hundreds of loci against a modeled error background; this is why bespoke assays reach 10^-4 to 10^-6 tumor fraction. The detected/not-detected call is the unit of analysis -- per-locus VAF is plumbing, not the readout. Re-deriving a per-timepoint "VAF < X" cutoff throws away the multi-locus integration that makes MRD work and inflates false positives from a single noisy locus.

The second half of the insight: an "undetectable" result is conditional on how many genome-equivalents were interrogated. VAF=0 is LEFT-CENSORED at the per-sample LoD, not a true zero. A 10 mL tube yields roughly 50 ng cfDNA, around 15,000 haploid genome-equivalents; at 0.01% tumor fraction that is roughly 1.5 expected tumor molecules, squarely in the Poisson-limited regime (lambda < 3) where detection is stochastic. "Undetectable" at a low-input draw may simply mean the assay could not have seen the burden it saw at a higher-input draw. Every undetectable must carry its per-sample LoD; plugging 0 into a log-fit or fold-change biases everything and log(0) breaks the fit outright.

## Design Decision: tumor-informed vs tumor-naive, landmark vs surveillance

| Axis | Tumor-informed bespoke | Tumor-naive (fixed panel) |
|------|------------------------|---------------------------|
| Variant set | Patient-specific, designed from tumor/normal WES/WGS | Fixed gene panel, identical across patients |
| Examples | Signatera (16 SNVs, Reinert 2019), RaDaR (up to ~48 amplicons), INVAR (hundreds-thousands of loci, Wan 2020) | Broad cfDNA panels, sWGS |
| MRD sensitivity | Very high (10^-4 to 10^-6 TF); LoD scales with #loci x input | Lower for MRD; few loci per region |
| Needs tumor tissue | Yes (design step, weeks of turnaround) | No (tissue-free, faster) |
| CHIP confounding | Low (tracks known tumor somatic variants) | High (de novo calls include clonal hematopoiesis) |
| Best use | Defined-burden MRD/surveillance after curative intent | No tissue available, or broad genotyping in metastatic disease |

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Post-curative-intent MRD / recurrence surveillance | Tumor-informed bespoke, binary call | Reaches ppm LoD by integrating across the personal variant set; CHIP-resistant |
| No tissue available, metastatic response monitoring | Tumor-naive panel, track aggregated burden | Tissue-free and immediate; accept higher LoD and mandatory CHIP control |
| Post-surgical landmark (single decisive timepoint) | One draw at ~2-10 weeks post-op | Avoids the surgical cfDNA surge; conventional Week 4 default |
| Serial surveillance over months-years | Trend over >=2 consecutive draws, confirm before acting | Each draw is another false-positive opportunity (multiple testing) |
| Defining "molecular response" | Use the assay's own validated cutoff; do not import "2-log" or "90%" blindly | Cutoffs are non-harmonized across assays (see below) |

Methodology evolves: verify the current best practice and the assay's validated definitions against the latest tool/vendor documentation before fixing any threshold in code.

## ctDNA Kinetics Biology -- why timing and shedding gate interpretation

ctDNA has a plasma half-life of roughly 2 h (114 min, Diehl 2008); broader literature spans ~16 min to 2.5 h. This fast turnover is the entire reason serial monitoring works: plasma concentration tracks CURRENT tumor flux, not a weeks-old average, while imaging tumor volume lags. The same fast clearance makes landmark timing fragile. Surgery dumps a transient cfDNA surge into plasma (tissue trauma, wound healing, neutrophil extracellular traps) that dilutes tumor fraction and can transiently raise total cfDNA. Drawing at post-op day 1-3 reads this surge, not residual disease; the conventional landmark window is ~2-10 weeks (Week 4 a frequent default). A clearance fit that includes a post-op surge point mis-estimates the half-life.

Shedding is not uniform. "ctDNA-negative" does NOT equal "disease-free": some early lung adenocarcinomas and indolent/low-volume tumors shed below detectable thresholds, and brain metastases behind the blood-brain barrier shed poorly into plasma (CSF is the better CNS compartment). A patient can have radiographic progression with clean plasma. Negativity has high negative predictive value for relapse in shedding tumors but is never a guarantee -- imaging stays mandatory for low/non-shedders and sanctuary sites.

## Molecular-Response Definitions -- and the non-standardization caveat

| Term | Representative operationalization | Caveat |
|------|-----------------------------------|--------|
| Molecular response (MR) | >= 90% drop (ctMoniTR-style) or >= 2-log/100x (immuno/heme heritage) from baseline | 2-log and 90% are different magnitudes; cutoff is study/assay-specific |
| Molecular complete response (mCR) | ctDNA becomes undetectable | "Undetectable" is LoD-conditional, not zero |
| ctDNA clearance | Sustained detectable -> undetectable | Depends on input/depth of the clearing draw; confirm with re-draw |
| Molecular progression / relapse | Confirmed re-detection or rise-from-nadir | Require trend over >=2 draws (multiple testing) |

These definitions are NOT harmonized. "2-log reduction," "90% reduction," and "molecular complete response" are assay- and study-dependent, not interchangeable. The Friends of Cancer Research ctMoniTR project is the field's standardization attempt (pooling ctDNA-change data across NSCLC immunotherapy studies to validate ctDNA change as an intermediate endpoint), not a settled standard. The FDA ctDNA guidance for curative-intent solid-tumor drug development was issued as a draft in May 2022 and finalized in November 2024; it endorses ctDNA for patient selection, MRD-based enrichment, and as a measure of response, but does NOT yet endorse ctDNA change as a validated surrogate endpoint for DFS/EFS/OS. Code should accept the assay's own validated cutoff rather than baking one in.

## Clinical Evidence and Lead Time

ctDNA MRD predicts relapse months before imaging across tumor types: breast median ~8 mo (Garcia-Murillas 2015), NSCLC median ~5.2 mo (Chaudhuri 2017), CRC mean ~8.7 mo (Reinert 2019); TRACERx phylogenetic ctDNA tracks clonal evolution and metastatic seeding (Abbosh 2017, 2023). The interventional landmark is DYNAMIC (Tie 2022): a ctDNA-guided strategy in stage II colon cancer reduced adjuvant chemotherapy use (15% vs 28%) without compromising 2-year recurrence-free survival, proving an MRD-negative call can justify de-escalation. Caveat -- lead-time bias: "ctDNA detects relapse N months before imaging" is a real analytic-sensitivity advantage, but measuring survival from molecular detection vs clinical detection merely moves the clock back and inflates apparent survival. Demonstrating clinical utility (that acting on the earlier signal improves outcomes) requires an interventional design like DYNAMIC, not earlier detection alone. Flag lead-time bias wherever lead time is reported.

## Tumor-Fraction Trend with Baseline and Nadir

**Goal:** Summarize a serial trajectory into baseline, nadir, and baseline-referenced change, with below-LoD points marked as censored, not zero.

**Approach:** Sort by time, carry a per-sample LoD column, flag any point at-or-below its LoD as left-censored, and compute log-fold change from baseline only on the uncensored estimates (substituting the LoD bound, never 0, for censored points).

```python
import numpy as np
import pandas as pd

def summarize_trajectory(df):
    '''df columns: timepoint, tumor_fraction, per_sample_lod (genome-equivalent-aware).'''
    df = df.sort_values('timepoint').copy()
    df['censored'] = df['tumor_fraction'] <= df['per_sample_lod']
    df['tf_for_log'] = np.where(df['censored'], df['per_sample_lod'], df['tumor_fraction'])
    baseline = df.iloc[0]['tf_for_log']
    df['log2_fc_baseline'] = np.log2(df['tf_for_log'] / baseline)
    detected = df[~df['censored']]
    nadir = detected['tumor_fraction'].min() if len(detected) else np.nan
    return df, {'baseline_tf': baseline, 'nadir_tf': nadir, 'n_censored': int(df['censored'].sum())}
```

## Mutation Tracking and Censoring-Aware Clearance Kinetics

**Goal:** Pivot per-mutation VAF over time and estimate a clearance half-life only over the genuine decay phase, treating below-LoD timepoints as censored.

**Approach:** Build a timepoint-by-mutation pivot, mark cleared loci as below-LoD (not missing-equals-zero), then fit ln(VAF) ~ time by OLS over the monotonic-decay phase only, excluding the surgical-surge point, any post-nadir rebound, and all censored points; half-life = ln(2)/(-slope).

```python
from scipy import stats

def clearance_half_life(df, lod):
    '''df columns: timepoint, vaf for one mutation. lod = per-sample detection bound.
       Fits the uncensored decay phase up to the nadir (drops post-nadir rebound and
       every below-LoD point); never feeds log(0) into the OLS.'''
    df = df.sort_values('timepoint')
    uncensored = df[df['vaf'] > lod].reset_index(drop=True)
    if len(uncensored) < 3:
        return None
    decay = uncensored.iloc[:uncensored['vaf'].idxmin() + 1]
    if len(decay) < 3:
        return None
    fit = stats.linregress(decay['timepoint'].values, np.log(decay['vaf'].values))
    half_life = np.log(2) / -fit.slope if fit.slope < 0 else np.inf
    return {'half_life_days': half_life, 'slope': fit.slope, 'r_squared': fit.rvalue ** 2,
            'n_points': len(decay), 'n_censored_excluded': int((df['vaf'] <= lod).sum())}
```

## Molecular-Relapse Calling

**Goal:** Call molecular relapse from confirmed re-detection or sustained rise-from-nadir, not a single excursion.

**Approach:** Find the nadir, then require detection (above per-sample LoD) on >=2 consecutive post-nadir draws, or a rise above an assay-defined margin above nadir confirmed on a re-draw; annotate every call with the draw's per-sample LoD so a low-LoD draw is not mistaken for new biology.

```python
def call_molecular_relapse(df, rise_factor=2.0, min_consecutive=2):
    '''df columns: timepoint, tumor_fraction, per_sample_lod. Requires a confirmed trend.'''
    df = df.sort_values('timepoint').copy()
    df['detected'] = df['tumor_fraction'] > df['per_sample_lod']
    nadir_time = df.loc[df['tumor_fraction'].idxmin(), 'timepoint']
    nadir_tf = max(df['tumor_fraction'].min(), df['per_sample_lod'].min())  # floor at LoD, not a censored value
    post = df[df['timepoint'] > nadir_time]
    consec = (post['detected'] & (post['tumor_fraction'] > nadir_tf * rise_factor)).astype(int)
    run = consec.groupby((consec == 0).cumsum()).cumsum().max() if len(consec) else 0
    relapse = bool(run >= min_consecutive)
    return {'relapse': relapse, 'nadir_tf': nadir_tf, 'confirmed_consecutive': int(run)}
```

## Per-Method Failure Modes

### Naive per-timepoint VAF thresholding
Trigger: applying "VAF < X" per timepoint to a multi-locus assay. Mechanism: discards the integration that makes MRD work; one noisy locus calls positive. Symptom: inflated false positives, jumpy trajectory. Fix: use the assay's integrated binary detected/not-detected call across the full variant set.

### Treating undetectable as a true zero
Trigger: plugging 0.0 (or VAF/2) into a log-fit or fold-change. Mechanism: log(0) is undefined; substituting a small number biases slope and fold-change. Symptom: NaN/inf fits or implausibly fast clearance. Fix: treat below-LoD as left-censored at the per-sample LoD; report "below LoD = X," never "0%."

### Ignoring per-timepoint LoD changes with input mass
Trigger: comparing "undetectable" across draws of different cfDNA input. Mechanism: LoD is input-conditional; a low-input draw could not have seen the prior burden. Symptom: spurious "clearance" or "relapse" at draws with anomalous input. Fix: carry per-sample LoD/genome-equivalents as a covariate; down-weight low-input negatives.

### CHIP rising over time read as relapse
Trigger: tumor-naive longitudinal panel without matched WBC sequencing. Mechanism: clonal hematopoiesis clones expand over time and under chemotherapy (Razavi 2019: majority of plasma variants are CHIP-derived), producing a rising non-tumor "ctDNA" signal. Symptom: false molecular progression in DNMT3A/TET2/ASXL1 hotspots. Fix: tumor-informed tracking, or matched serial WBC sequencing / known-CHIP-gene blacklisting.

### Lead-time bias in outcome claims
Trigger: reporting survival from molecular detection vs clinical detection. Mechanism: moving the detection clock back inflates apparent survival without changing outcome. Symptom: a "benefit" that is an artifact of earlier detection. Fix: claim clinical utility only from interventional designs (DYNAMIC); label lead time as analytic sensitivity, not benefit.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| ctDNA plasma half-life ~114 min (~2 h) | Diehl 2008, *Nat Med* 14:985 | Single-patient post-op estimate; broader range 16 min-2.5 h. Sets why monitoring works and why post-op timing matters |
| Post-op landmark window ~2-10 weeks (Week 4 common) | Convention across DYNAMIC/Signatera/RaDaR | Late enough for the surgical cfDNA surge to clear before reading residual disease |
| ~15,000 haploid genome-equivalents per 10 mL tube (~50 ng cfDNA, ~300 GE/ng) | Standard biophysical constants | Hard sampling floor: at 0.01% TF that is ~1.5 expected tumor molecules |
| Poisson-limited regime: lambda < 3 expected tumor molecules | Poisson detection theory (1-e^-3=0.95) | Below this, detection is stochastic; small input/recovery shifts flip a result across the LoD |
| Bespoke MRD sensitivity 10^-4 to 10^-6 tumor fraction | INVAR (Wan 2020), Signatera (Reinert 2019), RaDaR | Achieved only by integrating across the personal variant set, not per-locus |
| Molecular response ~2-log (100x) or ~90% reduction | ctMoniTR (Vega 2022); immuno/heme heritage | Non-harmonized convention -- surface the assay's own validated cutoff, do not hard-code |
| Per-course false-positive risk = 1 - s^n (s = per-sample specificity, n = draws) | Multiple-testing arithmetic | s=0.995,n=12 -> ~5.8%; s=0.99,n=12 -> ~11%. Report specificity per monitoring course, confirm positives by re-draw |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| log(0) / inf in clearance fit | Censored (below-LoD) point fed into ln(VAF) | Fit only the uncensored decay phase; carry LoD as the censoring bound |
| Half-life implausibly short or fits the surge | Post-op surge or post-nadir rebound point included | Restrict the OLS to the monotonic on-treatment decay phase |
| "Relapse" at one noisy draw | Acting on a single positive | Require >=2 consecutive confirmed draws; re-draw before acting |
| Rising signal in a tissue-free panel mistaken for tumor | CHIP drift over time | Matched WBC sequencing or tumor-informed tracking |
| "Negative = cured" overcall | Low-shedder / sanctuary site / low-input draw | Frame negative as below-LoD; keep imaging for low/non-shedders |

## References

- Diehl F, et al. 2008. Circulating mutant DNA to assess tumor dynamics. *Nature Medicine* 14:985-990. -- ctDNA half-life ~114 min; post-resection clearance kinetics.
- Tie J, et al. 2022. Circulating Tumor DNA Analysis Guiding Adjuvant Therapy in Stage II Colon Cancer (DYNAMIC). *New England Journal of Medicine* 386:2261-2272. -- Interventional MRD-guided de-escalation.
- Abbosh C, et al. 2017. Phylogenetic ctDNA analysis depicts early-stage lung cancer evolution. *Nature* 545:446-451. -- TRACERx tumor-informed clonal tracking.
- Abbosh C, et al. 2023. Tracking early lung cancer metastatic dissemination in TRACERx using ctDNA. *Nature* 616:553-562. -- Deep tumor-informed surveillance (~200 mutations).
- Garcia-Murillas I, et al. 2015. Mutation tracking in circulating tumor DNA predicts relapse in early breast cancer. *Science Translational Medicine* 7:302ra133. -- Lead time ~8 mo in breast cancer.
- Wan JCM, et al. 2020. ctDNA monitoring using patient-specific sequencing and integration of variant reads (INVAR). *Science Translational Medicine* 12:eaaz8084. -- Per-sample LoD derived from informative reads; the formal binary-integration framing.
- Reinert T, et al. 2019. Analysis of Plasma Cell-Free DNA by Ultradeep Sequencing in Patients With Stages I to III Colorectal Cancer. *JAMA Oncology* 5:1124-1131. -- Signatera; serial HR ~43.5; mean lead ~8.7 mo.
- Chaudhuri AA, et al. 2017. Early Detection of Molecular Residual Disease in Localized Lung Cancer by Circulating Tumor DNA Profiling. *Cancer Discovery* 7:1394-1403. -- CAPP-Seq; median lead ~5.2 mo.
- Razavi P, et al. 2019. High-intensity sequencing reveals the sources of plasma circulating cell-free DNA variants. *Nature Medicine* 25:1928-1937. -- Majority of plasma cfDNA variants are CHIP-derived; matched WBC sequencing essential.
- Merino Vega D, et al. 2022. Changes in Circulating Tumor DNA Reflect Clinical Benefit Across Multiple Studies of Patients With Non-Small-Cell Lung Cancer Treated With Immune Checkpoint Inhibitors. *JCO Precision Oncology* 6:e2100372. -- Friends of Cancer Research ctMoniTR Step 1; the molecular-response standardization effort, not a settled threshold.

The RaDaR/LUCID early-NSCLC residual-ctDNA study (*Annals of Oncology* 2022, 33:500-510) is referenced generically above; verify first-author attribution and the exact article identifier against the journal record before citing it formally.

## Related Skills

- ctdna-mutation-detection - detect the variant set that is then tracked
- tumor-fraction-estimation - per-timepoint tumor burden
- analytical-validation - per-timepoint LoD and left-censoring of undetectable samples
- fragment-analysis - fragmentomic trends as a complementary monitoring signal
- clinical-biostatistics/survival-analysis - relapse, lead-time, and endpoint analysis
<!-- END FILE: liquid-biopsy/longitudinal-monitoring/SKILL.md -->

## 子目录：liquid-biopsy/methylation-based-detection

<!-- BEGIN FILE: liquid-biopsy/methylation-based-detection/SKILL.md -->
---
name: bio-methylation-based-detection
description: Detects cancer and infers tissue-of-origin from cfDNA methylation by choosing conversion chemistry (bisulfite vs EM-seq vs TAPS vs cfMeDIP), calling read-level methylation haplotypes rather than averaged beta values, and deconvolving a hematopoietic-dominated cfDNA mixture against a methylation atlas via NNLS/quadratic programming. Encodes the GRAIL/CCGA thesis that thousands of tissue-specific markers make methylation outperform sparse mutations for multi-cancer early detection (MCED) and localization, and that single concordantly-methylated fragments give ppm-level sensitivity. Uses MethylDackel for extraction (mbias-then-extract), MEDIPS/QSEA for enrichment data, scipy.optimize.nnls for deconvolution. Use when building an MCED or methylation-MRD assay, picking a conversion chemistry for low-input plasma, or deconvolving tissue-of-origin from cfDNA.
tool_type: mixed
primary_tool: MethylDackel
---

## Version Compatibility

Reference examples tested with: MethylDackel 0.6+, Bismark 0.24+, numpy 1.26+, pandas 2.2+, scipy 1.12+, statsmodels 0.14+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: MethylDackel `extract` bedGraph column order is fixed (chrom / start / end / methylation-% rounded to integer / count-methylated / count-unmethylated); always run `MethylDackel mbias` first and feed its suggested `--OT/--OB` trimming into `extract`. cfMeDIP data are coverage, not conversion — do not feed them into per-CpG bisulfite pipelines.

# Methylation-Based Detection

**"Detect cancer and find where it came from using cfDNA methylation"** -> Call per-CpG (and read-level) methylation from converted plasma DNA, then deconvolve tissue-of-origin against a reference atlas.
- CLI: `MethylDackel extract` for per-CpG methylation from bisulfite/EM-seq BAMs
- CLI: `MethylDackel mbias` to choose strand-specific trimming before extraction
- R: MEDIPS / QSEA for cfMeDIP enrichment (coverage, not conversion)
- Python: `scipy.optimize.nnls` for atlas-based tissue deconvolution

## The Single Most Important Modern Insight -- methylation beats mutations, and read-level haplotypes beat averaged beta

Methylation is the right altitude for multi-cancer early detection (MCED) and tissue-of-origin (TOO) in a single assay because the genome carries thousands of stable, cell-type-specific differentially methylated regions, whereas somatic mutations are sparse, recurrent only at a few driver loci, and carry no tissue label. On the same cfDNA inside CCGA, the methylation assay outperformed WGS-SNV/CNV approaches, which is why GRAIL down-selected to a targeted methylation panel (Liu 2020). One panel answers both "is there cancer?" and "where is it?" — mutations answer neither well.

The sensitivity engine is read-level, not site-level. Averaging beta across reads at a CpG discards phasing. A single tumor-derived fragment that is concordantly methylated across the k CpGs of a methylation haplotype block (Guo 2017) has a background probability of roughly p^k of arising from the hematopoietic ocean; for a block of 5-8 CpGs that is small enough that ONE such fragment is strong evidence, independent of tumor fraction. Per-site beta dilutes that signal into sampling noise and clonal-hematopoiesis variance and has essentially no power at parts-per-million tumor fraction. The correct primitive for detection is molecule counting over haplotype blocks, not site averaging.

## Conversion Chemistry Tradeoffs

The conversion step is chosen on the worst possible substrate — already-fragmented, low-input plasma DNA — so destructiveness is load-bearing, not a footnote.

| Method | Destructiveness | Min input | Base resolution | 5mC readout | Key bias / caveat |
|--------|-----------------|-----------|-----------------|-------------|-------------------|
| Bisulfite (WGBS/targeted) | Severe — depurinates/fragments, >90% loss possible | High (degradation eats low input) | Yes | C->T after conversion; remaining C = methylated | Complexity collapse on cfDNA; incomplete conversion -> false methylation; GC/coverage bias |
| EM-seq (Vaisvila 2021) | Much gentler — enzymatic, no chemical fragmentation | Picograms demonstrated | Yes | Same C->T readout as bisulfite, milder | Reads 5mC+5hmC together unless separated; APOBEC over/under-deamination edge cases |
| TAPS (Liu 2019) | Non-destructive — mild | Low / cfDNA-friendly | Yes | Direct: 5mC/5hmC -> T, unmethylated C untouched | Only a few % of Cs convert -> preserves complexity, lower seq cost; needs TET + pyridine borane |
| cfMeDIP-seq (Shen 2018) | No conversion (antibody enrichment) | Very low (>=5-10 ng) | No — region/enrichment-level only | Antibody pulls down methylated fragments | CpG-density bias; no single-CpG quantitation; needs MEDIPS/QSEA density modeling |

Bisulfite is gold standard for cell-line gDNA, not for low-input fragmented plasma; EM-seq and TAPS exist precisely to recover ctDNA molecules bisulfite destroys. Neither bisulfite nor EM-seq separates 5mC from 5hmC without added oxBS/TAB steps; TAPS variants (TAPSbeta, CAPS) can split the marks. cfMeDIP coverage is enrichment, not quantitation — density bias must be modeled before any absolute-methylation claim.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| MCED + tissue-of-origin in one assay | Targeted methylation panel + atlas deconvolution | Thousands of tissue markers carry both cancer and organ signal (Liu 2020; Loyfer 2023) |
| Ultra-low-input plasma, genome-wide | cfMeDIP-seq | Antibody enrichment works at ng-to-low input where conversion destroys the library (Shen 2018) |
| Need base resolution at low input | EM-seq or TAPS, not bisulfite | Gentle/non-destructive conversion preserves complexity bisulfite collapses (Vaisvila 2021; Liu 2019) |
| MRD / ppm-level detection | Read-level haplotype counting over pre-defined blocks | One concordant fragment is decisive; averaged beta has no power at low tumor fraction (Guo 2017) |
| Absolute methylation level from enrichment data | QSEA (Bayesian density + CNV + TMM) | Converts cfMeDIP coverage to BS-comparable values; MEDIPS gives differential coverage only (Lienhard 2017) |

Methodology evolves; verify current atlas versions and panel-marker coverage against live tool docs before committing — atlas markers are platform-specific and do not transfer across assays.

## Extract Per-CpG Methylation with MethylDackel

**Goal:** Produce per-CpG methylation calls from a bisulfite/EM-seq cfDNA BAM, with end-repair artifacts trimmed.

**Approach:** Run `mbias` first to read the suggested strand-specific trimming, then `extract` with `--mergeContext` and that trimming so each CpG is one row; parse the fixed 6-column bedGraph.

```bash
# Step 1: choose trimming. mbias prints a suggestion like --OT 2,0,0,98 and writes M-bias SVGs.
MethylDackel mbias ref.fa sample.bam sample_mbias

# Step 2: extract per-CpG (one row per CpG) with the suggested trimming.
MethylDackel extract ref.fa sample.bam -o sample --mergeContext --minDepth 1 --OT 2,0,0,98
# Output sample_CpG.bedGraph columns (fixed order):
#   chrom  start  end  methylation%(integer, rounded)  count_methylated  count_unmethylated
```

Add `--CHG --CHH` only to audit non-CpG methylation (a conversion-failure check); CpG is the default context. Low per-CpG depth gates can erase cfDNA signal — prefer region/molecule aggregation over a high `--minDepth`.

## Tissue-of-Origin Deconvolution Against an Atlas

**Goal:** Attribute cfDNA to its cell types of origin and surface a solid-tissue coefficient elevated above the hematopoietic baseline.

**Approach:** Model the observed methylation vector m ~ A*w with atlas A (rows = markers, cols = cell types), solve for non-negative mixing fractions w with NNLS over atlas-covered markers, then renormalize so the fractions sum to one.

```python
from scipy.optimize import nnls

def deconvolve_tissue(sample_beta, atlas):
    'sample_beta: Series indexed by marker; atlas: DataFrame markers x cell_types.'
    markers = sample_beta.index.intersection(atlas.index)
    w, _ = nnls(atlas.loc[markers].values, sample_beta.loc[markers].values)
    w = w / w.sum()
    return dict(zip(atlas.columns, w))
```

The simplex constraint (w >= 0, sum w = 1) is mandatory — unconstrained regression gives nonsense fractions (Moss 2018). Use Loyfer 2023's fragment-level WGBS atlas (39 cell types from 205 healthy samples) where the assay covers its markers; a generic atlas does not transfer, because WGBS-fragment markers differ from 450K/EPIC probes and from capture-panel coverage.

## Region-Level DMR Discovery

**Goal:** Define a discriminating panel by finding regions (not single CpGs) that separate cancer from normal cfDNA.

**Approach:** Aggregate per-CpG beta into pre-defined regions/blocks, test cancer vs normal per region, and control FDR with Benjamini-Hochberg specified explicitly — naming method='fdr_bh' rather than relying on the statsmodels default ('hs', Holm-Sidak).

```python
from scipy import stats
from statsmodels.stats.multitest import multipletests

def region_dmrs(cancer, normal, region_col='region'):
    'cancer/normal: long DataFrames with [region_col, beta]; one row per sample-region.'
    out = []
    for region, c in cancer.groupby(region_col)['beta']:
        n = normal.loc[normal[region_col] == region, 'beta'].dropna()
        c = c.dropna()
        if len(c) < 3 or len(n) < 3:
            continue
        _, p = stats.mannwhitneyu(c, n, alternative='two-sided')
        out.append((region, c.mean() - n.mean(), p))
    import pandas as pd
    res = pd.DataFrame(out, columns=['region', 'delta_beta', 'pvalue'])
    res['fdr'] = multipletests(res['pvalue'], method='fdr_bh')[1]
    return res.sort_values('fdr')
```

## cfMeDIP Enrichment Analysis

**Goal:** Get density-corrected differential methylation from antibody-enrichment coverage rather than conversion data.

**Approach:** Use MEDIPS (Lienhard 2014) for CpG-density-corrected differential coverage, or QSEA (Lienhard 2017) when absolute, BS-comparable methylation levels are needed — QSEA adds a Bayesian CpG-density model, CNV correction, and TMM effective-library-size normalization. Both are R/Bioconductor; do not pass cfMeDIP coverage through MethylDackel.

## Per-Method Failure Modes

### Averaged beta wastes the read-level signal
**Trigger:** Reporting region beta means / per-CpG DMR t-tests for an MCED or MRD assay. **Mechanism:** Averaging across reads discards fragment-level concordance, the exact signal that lets one tumor fragment be called. **Symptom:** No power at low tumor fraction despite deep coverage. **Fix:** Count concordantly-methylated molecules over haplotype blocks; reserve beta for discovery and QC.

### Per-CpG t-tests + naive BH are the wrong altitude
**Trigger:** Genome-wide per-CpG Welch t-tests with plain Benjamini-Hochberg. **Mechanism:** ~28M correlated CpGs violate BH independence (anticonservative) and per-site estimates are coverage-starved. **Symptom:** Inflated "DMR" lists that do not replicate. **Fix:** Region/block methods (dmrseq/metilene/methylKit windows) with permutation or correlation-aware FDR.

### Bisulfite degradation lowers complexity
**Trigger:** WGBS on low-input plasma. **Mechanism:** Chemical depurination/fragmentation destroys input, collapsing unique molecules. **Symptom:** Low library complexity, duplicate-heavy, lost ctDNA molecules. **Fix:** EM-seq or TAPS; track conversion completeness via CHH methylation.

### WBC background swamps the tumor coefficient
**Trigger:** Deconvolving with a mis-specified or unmatched hematopoietic reference. **Mechanism:** >90% of cfDNA is leukocyte/megakaryocyte-derived; reference error leaks variance into the small tumor term. **Symptom:** False or unstable TOO; a methylation analog of CHIP (clonal hematopoiesis/age/inflammation shifts the WBC methylome). **Fix:** Age/condition-matched background, fine-grained atlas, treat tumor as a small residual.

### cfMeDIP density bias / no base resolution
**Trigger:** Reading cfMeDIP coverage as methylation level, or running it through a per-CpG pipeline. **Mechanism:** Antibody enriches CpG-dense regions; there is no single-CpG quantitation. **Symptom:** Apparent hypermethylation tracking CpG density, not biology. **Fix:** Model density with MEDIPS coupling factor or QSEA's Bayesian model.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Specificity 99.3%, sensitivity 54.9%, TOO 93% (among detected) | Liu 2020 *Ann Oncol* 31(6):745 | CCGA2 targeted-methylation operating point; screening fixes high specificity and accepts modest sensitivity |
| Specificity 99.5%, sensitivity 51.5%; stage I 16.8% -> IV 90.1%; TOO 88.7% | Klein 2021 *Ann Oncol* 32(9):1167 | CCGA3 clinical validation; sensitivity is stage- and tumor-type-dominated, never quote it as uniform |
| cfMeDIP input >= 5-10 ng | Shen 2018 *Nature* 563:579 | Enrichment works below conversion-assay input floors but still needs ng-scale material |
| Deconvolution: w >= 0 and sum w = 1 | Moss 2018 *Nat Commun* 9:5068; Loyfer 2023 *Nature* 613:355 | Simplex constraint mandatory; unconstrained regression yields nonsense fractions |
| Avoid high per-CpG `--minDepth` for cfDNA | MethylDackel docs; community | Per-CpG depth gates erase low-coverage cfDNA signal; aggregate over regions/molecules instead |

## References

- Liu MC, et al. 2020. Sensitive and specific multi-cancer detection and localization using methylation signatures in cell-free DNA. *Annals of Oncology* 31(6):745-759. — CCGA2 targeted-methylation MCED; spec 99.3%, sens 54.9%, TOO 93%.
- Klein EA, et al. 2021. Clinical validation of a targeted methylation-based multi-cancer early detection test using an independent validation set. *Annals of Oncology* 32(9):1167-1177. — CCGA3 validation; stage-dependent sensitivity.
- Shen SY, et al. 2018. Sensitive tumour detection and classification using plasma cell-free DNA methylomes. *Nature* 563(7732):579-583. — cfMeDIP-seq.
- Moss J, et al. 2018. Comprehensive human cell-type methylation atlas reveals origins of circulating cell-free DNA in health and disease. *Nature Communications* 9:5068. — NNLS atlas deconvolution.
- Loyfer N, et al. 2023. A DNA methylation atlas of normal human cell types. *Nature* 613(7943):355-364. — 39 cell types, 205 samples; fragment-level WGBS atlas.
- Liu Y, et al. 2019. Bisulfite-free direct detection of 5-methylcytosine and 5-hydroxymethylcytosine at base resolution (TAPS). *Nature Biotechnology* 37(4):424-429.
- Guo S, et al. 2017. Identification of methylation haplotype blocks aids in deconvolution of heterogeneous tissue samples and tumor tissue-of-origin mapping from plasma DNA. *Nature Genetics* 49(4):635-642. — methylation haplotype blocks.
- Vaisvila R, et al. 2021. Enzymatic methyl sequencing detects DNA methylation at single-base resolution from picograms of DNA (EM-seq). *Genome Research* 31(7):1280-1289. — page span verified from DOI 10.1101/gr.266551.120; confirm against the published PDF if citing the exact pages.
- Lienhard M, et al. 2014. MEDIPS: genome-wide differential coverage analysis of sequencing data derived from DNA enrichment experiments. *Bioinformatics* 30(2):284-286.
- Lienhard M, et al. 2017. QSEA — modelling of genome-wide DNA methylation from sequencing enrichment experiments. *Nucleic Acids Research* 45(6):e44.

## Related Skills

- cfdna-preprocessing - conversion chemistry and library choices upstream
- fragment-analysis - orthogonal genome-wide cfDNA signal
- analytical-validation - read-level detection framed as a limit-of-detection problem
- methylation-analysis/bismark-alignment - bisulfite read alignment
- methylation-analysis/dmr-detection - region-level differential methylation statistics
<!-- END FILE: liquid-biopsy/methylation-based-detection/SKILL.md -->

## 子目录：liquid-biopsy/tumor-fraction-estimation

<!-- BEGIN FILE: liquid-biopsy/tumor-fraction-estimation/SKILL.md -->
---
name: bio-tumor-fraction-estimation
description: Estimates tumor fraction (the genome-wide proportion of cfDNA molecules that are tumor-derived, the cfDNA analogue of bulk-tumor purity) from shallow whole-genome sequencing with ichorCNA, an HMM over 1 Mb bins that jointly EM-estimates tumor fraction, ploidy, and subclonal prevalence over a normal/ploidy grid. Encodes the load-bearing reframes: tumor fraction is the quantity that travels across assays and is NOT mutation VAF (clonal-het VAF approximately TF/2), CNA-based estimation has a hard ~3 percent limit-of-detection floor, and near-diploid or copy-neutral-LOH genomes return a falsely low value. Selects the estimator by data type (sWGS to ichorCNA, deep panel to max-VAF, methylation to deconvolution, sub-3 percent to fragmentomics or methylation). Use when quantifying tumor burden from a liquid biopsy, picking a tumor-fraction estimator for a given assay, or reconciling a TF estimate against a panel VAF.
tool_type: r
primary_tool: ichorCNA
---

## Version Compatibility

Reference examples tested with: ichorCNA 0.6.0+ (GavinHaLab fork), HMMcopy 1.40+, R 4.2+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: ichorCNA is NOT an importable R function `runIchorCNA()` — it is a command-line script invoked as `Rscript scripts/runIchorCNA.R` with `optparse` flags, preceded by HMMcopy `readCounter` to build the WIG. Use the GavinHaLab fork (v0.6.0, 22 Nov 2024) for new work; the original broadinstitute/ichorCNA holds the wiki. The flag `--repTimeWig` does not exist — do not invent it.

# Tumor Fraction Estimation

**"Estimate tumor fraction from my cfDNA sample"** -> Estimate the genome-wide proportion of cfDNA molecules that are tumor-derived, mutation-agnostic, from copy-number signal.
- CLI: `readCounter` (HMMcopy) to bin the BAM, then `Rscript scripts/runIchorCNA.R` for the HMM
- R: parse `.params.txt` (tumor fraction = 1 - n); a Python subprocess wrapper is a thin alternative

## The Single Most Important Modern Insight -- tumor fraction is the quantity that travels across assays; it is NOT VAF and it is blind below ~3 percent

Tumor fraction (TF) is the fraction of cfDNA *molecules* that are tumor-derived — the cfDNA analogue of bulk-tumor purity. It is the burden metric that is comparable across assays and over time, which is exactly why it is the right unit to report. The two errors that dominate cfDNA work are unit confusion and floor confusion. Unit confusion: TF is NOT mutation VAF — a clonal heterozygous SNV in a diploid region sits at VAF approximately TF/2, so reporting a max-VAF as "tumor fraction" halves the true burden (and the factor changes entirely under LOH, amplification, or subclonality). Floor confusion: ichorCNA derives TF from copy-number deflection averaged over hundreds of 1 Mb bins, and that signal has a hard ~3 percent limit of detection. Below it the depth shift is smaller than per-bin sampling noise; a near-diploid or copy-neutral-LOH tumor returns a *falsely low* TF even at high true burden because it carries no depth signal. A low ichorCNA value is "low burden" only if the genome-wide plot is genuinely flat; otherwise it is uninformative, not negative.

## Estimator Landscape

| Estimator | Class | Input | Strength | Fails when |
|-----------|-------|-------|----------|------------|
| ichorCNA | CNA / depth (HMM) | sWGS 0.1-1x | Mutation-agnostic genome-wide burden; calibrated standard | TF < ~3%; near-diploid / copy-neutral-LOH genome |
| TitanCNA | CNA + allelic (B-allele) | deeper WGS with het-SNP depth | Resolves CNLOH via allelic imbalance | Needs informative het-SNP coverage (not 0.1x) |
| max-VAF / clonal-cluster MAF | Mutation / panel | deep targeted or WES | Sensitive to <0.1% VAF with UMI/duplex | Needs callable variants + CHIP filtering; CN-sensitive |
| Methylation deconvolution (CelFiE, CelFEER) | Methylation | WGBS/EM-seq or methyl panel | Dense per-molecule signal reaches below CNA floor | Needs a tumor-type methylation reference atlas |
| Fragmentomics (Griffin, DELFI) | Fragmentomic | sWGS | CN-independent corroboration at low TF | Quantifies "tumor signal," not a calibrated molecular fraction |

## Decision Tree by Data Type

| Data available | TF regime | Recommended | Why |
|---------------|-----------|-------------|-----|
| sWGS 0.1-1x, no known variants, aneuploid tumor | >= ~3% | ichorCNA | Mutation-agnostic genome-wide burden; the standard |
| sWGS, tumor type known to be near-diploid / quiet | any | mutation or methylation | ichorCNA underestimates with no depth signal |
| sWGS, TF suspected < 3% | < 3% | deep-panel max-VAF, methylation, or fragmentomics | Below the CNA floor (see fragment-analysis, methylation-based-detection) |
| Deep targeted / WES panel | down to <0.1% VAF | max-VAF excl. CHIP, or clonal-cluster MAF | Per-locus sensitivity; convert via TF approximately 2*VAF with CN care (see ctdna-mutation-detection) |
| Methylation (WGBS/EM-seq/panel) | very low | methylation deconvolution | Dense per-molecule signal; needs reference atlas |
| Targeted panel, want CN-based TF | >= few % | ichorCNA on off-target reads | Recovers genome-wide CN from off-target coverage |

Methodology evolves; verify current best practice against the live ichorCNA wiki and the relevant tool docs before committing to an estimator.

## ichorCNA Mechanics

ichorCNA is a hidden Markov model over copy-number states across 1 Mb bins. The emission per bin is the GC- and mappability-corrected log2 read-depth ratio (tumor vs a panel of normals). The HMM simultaneously segments the genome, calls large-scale CNAs (HOMD/DLOH/NEUT/GAIN/AMP/HLAMP up to `maxCN`), and by EM jointly estimates three global latent parameters: tumor fraction (via `n`), tumor ploidy (`phi`), and subclonal prevalence. The observed copy at a bin is a mixture: copy approximately 2*(1-TF) + TF*(tumor copy), and the sample ploidy identity is 2*(1-TF) + TF*tumor.ploidy. Because TF, ploidy, and per-bin tumor copy are all unknown, the same log-ratio can be explained by (low TF, large CN swing) or (high TF, small CN swing) — this ploidy/TF degeneracy is why ichorCNA fits over a grid of (`normal`, `ploidy`) start points and selects the maximum-likelihood solution.

### Bin the BAM and Run the HMM

**Goal:** Produce a calibrated tumor-fraction estimate plus genome-wide CN segments from a single sWGS BAM.

**Approach:** Bin coverage into 1 Mb WIG with HMMcopy `readCounter` (chromosome naming must match the BAM `@SQ` style), then run `runIchorCNA.R` with build-matched GC/map/centromere references and a protocol-matched panel of normals; read `.params.txt`.

```bash
# Step 1: 1 Mb bins. --chromosome style ('1' vs 'chr1') MUST match the BAM @SQ names.
readCounter --window 1000000 --quality 20 \
  --chromosome "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y" \
  tumor.bam > tumor.wig

# Step 2: the HMM. NOT an R function call -- it is a script with optparse flags.
Rscript scripts/runIchorCNA.R \
  --id tumor --WIG tumor.wig \
  --gcWig gc_hg38_1000kb.wig --mapWig map_hg38_1000kb.wig \
  --centromere GRCh38.centromere.txt \
  --normalPanel HD_ULP_PoN_1Mb_median.rds \
  --normal "c(0.5,0.6,0.7,0.8,0.9)" --ploidy "c(2,3)" --maxCN 7 \
  --estimateNormal TRUE --estimatePloidy TRUE --estimateScPrevalence TRUE \
  --scStates "c(1,3)" --txnE 0.9999999 --txnStrength 1e7 \
  --minMapScore 0.9 --genomeBuild hg38 --genomeStyle UCSC \
  --outDir ichor_out/
```

Key flags (verified defaults from `runIchorCNA.R`): `--maxCN 7` (lower to 3 for low-TF); `--normal "0.5"` and `--ploidy "2"` are grid *start* points, not fixed values (`--estimateNormal`/`--estimatePloidy` still estimate them; these are optparse `type=logical` flags so they need an explicit `TRUE`/`FALSE`, not a bare flag); `--txnE 0.9999999` and `--txnStrength 1e7` set the segment-length prior; `--minMapScore 0.9` drops low-mappability bins; `--gcWig`/`--mapWig`/`--centromere`/`--normalPanel` must all match the BAM's build and the 1 Mb bin size.

### Parse the Optimal Solution

**Goal:** Extract the calibrated tumor fraction, ploidy, and QC from ichorCNA output.

**Approach:** Read `.params.txt`; TF = 1 - n_est for the selected (max-loglik) solution; gate on the GC-Map MAD; inspect subclonal fractions and the genome-wide plot before trusting a borderline call.

```r
parse_ichor <- function(params_file) {
    p <- read.table(params_file, header = TRUE, sep = '\t', stringsAsFactors = FALSE)
    list(
        tumor_fraction = 1 - p$n_est[1],   # TF = 1 - normal fraction; selected solution is row 1
        ploidy = p$phi_est[1],
        loglik = p$loglik[1]
    )
}
```

The `.params.txt` also carries `Tumor Fraction` (= 1 - n), `Tumor Ploidy` (phi), `Fraction Genome Subclonal`, `Fraction CNA Subclonal`, and `GC-Map Correction MAD` (the data-noise QC). Companion outputs: `.cna.seg` (per-bin CN and log-ratio), `.seg` (IGV-compatible Viterbi segments), `.RData` (all grid solutions), and the genome-wide plot PDF — always inspect it for borderline calls because the ploidy/TF degeneracy can select a ploidy-3 alias of a ploidy-2 truth.

## Unit Confusion -- TF vs VAF vs ctDNA%

These three are routinely conflated; the relation is exact and copy-number-dependent. For a variant at local copy number `Cn` with mutant-copy multiplicity `m`:

```
VAF = (TF * m) / [ TF * Cn + 2 * (1 - TF) ]
```

For a clonal heterozygous SNV in a diploid region (`Cn`=2, `m`=1) this collapses to VAF approximately TF/2, equivalently **TF approximately 2*VAF**. The common errors:

- LOH variant (mutant on both copies, normal copy lost): `m`=`Cn`, so VAF -> TF, not TF/2 — treating it as TF/2 doubles the estimate.
- Amplified mutant allele inflates VAF above TF/2; a mutant on a deleted copy deflates it — so max-VAF over-estimates TF for amplified drivers and under-estimates for deleted ones.
- Subclonal variants carry an extra cancer-cell-fraction factor and understate TF.
- Germline heterozygous SNPs sit at VAF approximately 0.5 regardless of TF — never feed them into a TF-from-VAF calculation.
- CHIP (clonal hematopoiesis) variants are blood-derived, not tumor — exclude them from any max-VAF TF proxy.
- ctDNA% is loosely used for either TF or max-VAF; always pin down which a lab means.

Cross-check: for a clonal heterozygous driver in a diploid region, ichorCNA TF and 2*(panel VAF) should agree. TF >> 2*VAF implies a subclonal/deleted variant or a ploidy mis-call; TF << 2*VAF implies a near-diploid/CNLOH tumor or an amplified/LOH driver. Never average the two blindly (see ctdna-mutation-detection).

## Per-Method Failure Modes

### ~3 percent CNA floor
**Trigger:** TF below ~0.03 at 0.1x sWGS. **Mechanism:** the log2 deflection from a single-copy event is proportional to TF (~±0.02 at TF=0.03), smaller than per-bin sampling noise; only averaging over hundreds of bins recovers it. **Symptom:** TF collapses toward 0; replicate variability (MNSD) rises sharply. **Fix:** the floor scales with aneuploidy magnitude and coverage — it needs roughly one >100 Mb gain AND one >100 Mb loss; sequence deeper (>1-5x) or switch estimator class (fragment-analysis, methylation-based-detection).

### Near-diploid / copy-neutral-LOH
**Trigger:** quiet tumor type or CNLOH-rich genome. **Mechanism:** CNLOH has identical total coverage to diploid, indistinguishable on depth alone; ichorCNA is also tuned conservative and "may underestimate." **Symptom:** falsely low TF with a flat genome-wide plot. **Fix:** treat a flat low call as uninformative, not negative; escalate to a mutation/methylation assay; TitanCNA can use allelic imbalance if het-SNP depth exists.

### Mismatched panel of normals / references
**Trigger:** PoN, GC/map/centromere WIG, or build does not match the library prep, bin size, or genome build. **Mechanism:** the PoN models protocol-specific coverage bias; a mismatched PoN injects its own bias as spurious CN waviness. **Symptom:** wavy log-ratio, implausible TF. **Fix:** build/obtain a PoN from healthy-donor cfDNA on the exact protocol at the same bin size and build; keep hg19 vs hg38 and `1` vs `chr1` consistent end-to-end.

### Ploidy aliasing
**Trigger:** ploidy/TF degeneracy. **Mechanism:** the max-loglik solution is occasionally a ploidy-3 alias of a ploidy-2 truth. **Symptom:** doubled ploidy with halved TF. **Fix:** read all `.params.txt` solutions, inspect the plot; for low-TF samples force `--ploidy "c(2)"`.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Coverage 0.1-1x sWGS; 1 Mb bins | Adalsteinsson 2017; ichorCNA wiki | Finer bins add noise at 0.1x; ~0.1x is the calibrated ULP-WGS operating point |
| ~3% TF limit of detection at ~0.1x | Adalsteinsson 2017 (95% sens, 1125/1288 mixtures; 91% spec, 20/22 donors at 0.03 TF cutoff) | Below 0.03 the depth deflection falls under per-bin noise |
| 97.2-100% sensitivity to detect 3% TF (1x and 0.1x) | J Mol Diagn 2024 assay validation | Independent dilution/replicate validation; MNSD rises sharply below 3%, establishing 3% as the LOD |
| GC-Map Correction MAD < 0.15 good; > 0.3 distrust | ichorCNA FAQ | Residual post-correction noise; high MAD means the depth signal is unreliable |
| Manual-curation band 0.03-0.10 TF | ichorCNA wiki | Model can pick the wrong solution and tends to underestimate near the floor; inspect the plot |
| Low-TF recipe: `--normal "c(0.95,0.99,0.995,0.999)" --ploidy "c(2)" --maxCN 3 --estimateScPrevalence FALSE --scStates "c()"` | ichorCNA wiki | Seeds EM near TF 5/1/0.5/0.1%; ploidy and subclonality are unidentifiable when CN signal is weak |

## References

- Adalsteinsson VA, Ha G, Freeman SS, et al. 2017. Scalable whole-exome sequencing of cell-free DNA reveals high concordance with metastatic tumors. *Nat Commun* 8(1):1324. — ichorCNA primary method; the ~3% LOD benchmark (95% sensitivity, 91% specificity at a 0.03 TF cutoff, ~0.1x).
- Assay Validation of Cell-Free DNA Shallow Whole-Genome Sequencing to Determine Tumor Fraction in Advanced Cancers. 2024. *J Mol Diagn* 26(5):413-422 (PMC11090203). — Independent validation: 97.2-100% sensitivity at 3% TF (1x and 0.1x); MNSD rising below 3% establishes 3% as the LOD.
- broadinstitute/ichorCNA and GavinHaLab/ichorCNA GitHub repositories and wiki (Usage, Output, Parameter-tuning, Create-Panel-of-Normals, FAQ). — `readCounter` command, `runIchorCNA.R` flag defaults, `.params.txt` fields, MAD QC thresholds, CNLOH/near-diploid underestimation, PoN construction.

## Related Skills

- cfdna-preprocessing - sWGS BAM input and minimal-processing path
- fragment-analysis - the estimator to use below the ~3% CNA floor
- ctdna-mutation-detection - max-VAF cross-check and the TF-vs-VAF reconciliation
- analytical-validation - the ~3% floor framed as a limit of detection
- copy-number/cnvkit-analysis - copy-number calling concepts
- copy-number/copy-ratio-segmentation - segmentation concepts
<!-- END FILE: liquid-biopsy/tumor-fraction-estimation/SKILL.md -->

<!-- END CATEGORY: liquid-biopsy -->

