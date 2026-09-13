---
slug: bio-temporal-genomics-integrated
version: 1.0.0
displayName: "时间序列基因组学 / Temporal genomics"
name: bio-temporal-genomics-integrated
summary: >-
  中文：时间序列基因组学综合技能，整合 6 个相关专题，覆盖时间序列基因组学：circadian节律检测、差异节律性、未知周期发现、时序聚类、轨迹建模。 English: Integrated Temporal genomics skill covering 6 related topics, including Temporal genomics: circadian rhythm detection, differential rhythmicity, unknown periodicity discovery, temporal clustering, trajectory modeling.
description: >-
  中文：这是一个面向时间序列基因组学的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：时间序列基因组学：circadian节律检测、差异节律性、未知周期发现、时序聚类、轨迹建模。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：CosinorPy, Mfuzz, limorhyde。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Temporal genomics, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Temporal genomics: circadian rhythm detection, differential rhythmicity, unknown periodicity discovery, temporal clustering, trajectory modeling. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: CosinorPy, Mfuzz, limorhyde. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# temporal-genomics 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: temporal-genomics -->

## 子目录：temporal-genomics/circadian-rhythms

<!-- BEGIN FILE: temporal-genomics/circadian-rhythms/SKILL.md -->
---
name: bio-temporal-genomics-circadian-rhythms
description: Tests and estimates rhythmicity at a PRE-SPECIFIED period (canonically 24h) in time-series omics using cosinor regression (CosinorPy), JTK_CYCLE/ARSER/Lomb-Scargle meta-analysis (MetaCycle meta2d), and non-parametric tests for asymmetric waveforms (RAIN, DiscoRhythm); estimates phase (acrophase), amplitude, and MESOR, and controls FDR with an effect-size (rAMP) filter against over-detection. Use when testing for 24-hour or other known-period oscillations in a single condition (circadian, feeding-fasting, or light-dark experiments) and estimating their phase/amplitude. Not for unknown-period discovery (see temporal-genomics/periodicity-detection) or comparing rhythms between conditions (see temporal-genomics/differential-rhythmicity).
tool_type: mixed
primary_tool: CosinorPy
---

## Version Compatibility

Reference examples tested with: CosinorPy 3.1 (requires numpy<2.0 - v3.1 calls the removed `np.round_`), pandas 2.2+, statsmodels 0.14+, MetaCycle 1.2+, RAIN 1.x (Bioconductor), DiscoRhythm 1.x (Bioconductor).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

CosinorPy 3.1 imports as `from CosinorPy import cosinor, cosinor1, file_parser` (capitalized package, lowercase submodules); older 0.x/1.x releases used the lowercase `cosinorpy` package name.

# Known-Period Rhythm Testing

## Governing principle: known-period TESTING, not unknown-period DISCOVERY

This skill answers "at THIS period (usually 24h), is a feature rhythmic, and what are its phase, amplitude, and MESOR?" - a hypothesis test plus parameter estimation at a period the analyst specifies. That is categorically different from asking "what period does this feature have?", which is a spectral DISCOVERY search (Lomb-Scargle periodogram, wavelets, FFT) handled by temporal-genomics/periodicity-detection. Conflating them is the field's most common conceptual error: opening a wide period window turns a test into a search and inflates false positives, because structured noise can always be "fit" better at SOME period in a broad window.

The load-bearing consequence: temporal conclusions are dominated by SAMPLING DESIGN, not by the algorithm. Nyquist (>=2 samples/cycle) is a mathematical FLOOR that only prevents aliasing - it gives zero robustness to noise and no ability to estimate phase/amplitude. Real detection needs >=6 (ideally 8-12) samples/cycle AND >=2 full cycles. Resolving that a period exists < estimating its phase < estimating its amplitude, in ascending sampling demand. A design good enough to say "yes, 24h" is usually too thin to trust its phase and far too thin to trust its amplitude.

## Core Workflow

1. Declare the light regime (LD=entrained, use ZT; DD=free-running, use CT) and the period window (entrained: fix `minper=maxper=24`; free-running: allow ~22-26h for tau != 24h)
2. Prepare the time-series matrix (features x timepoints), decide log-vs-linear scale and any detrending BEFORE testing
3. Fit cosinor models or apply rhythmicity tests at the specified period
4. Extract parameters: amplitude, relative amplitude (rAMP), phase (acrophase), MESOR, p-value
5. Control FDR (BH), then apply an EFFECT-SIZE filter (rAMP / fold-change) - significance alone over-detects
6. For between-condition questions, fit a differential-rhythmicity model (never intersect two separate rhythm lists)

## Method Selection (which to pick and why)

| Method | Pick when | Mechanism | Fails / caveat |
|--------|-----------|-----------|----------------|
| Cosinor (single-component) | Sinusoidal waveform; uneven/sparse/non-integer sampling; CIs on phase/amplitude/MESOR are needed; substrate for differential rhythmicity | OLS of expression on a fixed `cos`/`sin` basis at period T (linear regression); rhythmicity = zero-amplitude F-test | Miscalls asymmetric/spiky waveforms (a fast-rise/slow-decay pulse) as arrhythmic; needs a variance-stabilizing transform for count data |
| Cosinor (multi-component) | Visibly non-sinusoidal shape AND dense sampling AND a biological reason (e.g. a known 12h "12h-clock" transcript) | Adds 12h (`n_components=2`), 8h (`=3`) harmonics; joint zero-amplitude F-test | Each harmonic costs 2 df; with 6-8 pts/cycle a 3-component model is near-saturated and fits noise - use AIC/BIC or automatic model selection |
| JTK_CYCLE | Evenly sampled at integer-hour intervals; robust rank-based test; genome-scale speed | Correlates the series against reference cosines of all phases (Jonckheere-Terpstra + Kendall tau); best phase = matched reference | Requires EVEN integer sampling, no gaps; with few timepoints/1 replicate the tau null is DISCRETE so p-values are quantized and ANTI-conservative (source of "everything is rhythmic") |
| eJTK / BooteJTK | Short/sparse or few-replicate series where JTK p-values are untrustworthy; asymmetric/spiky waveforms | Empirical (permutation/Gamma) null restores calibration; asymmetric reference-waveform library; BooteJTK adds replicate bootstrap + variance shrinkage | Slower; still cannot fully fix temporal autocorrelation |
| ARSER | Non-sinusoidal short series; combines time- and frequency-domain info | Estimates period from an AUTOregressive spectrum, then harmonic regression | Requires EVEN sampling, no missing values, no replicate structure; AR order unstable on very short/noisy series; wants denser sampling than JTK |
| RAIN | ASYMMETRIC waveforms (fast induction / slow decay); distribution-free | Umbrella/Mack-Wolfe (Jonckheere-Terpstra) test with SEPARATE rising and falling limbs | LOWER power than cosinor/JTK for genuinely symmetric sinusoids; gives a coarse phase/peak-shape, not clean amplitude CIs |
| MetaCycle meta2d | A robust consensus RANK across methods is wanted on a standard even design | Runs a subset of {ARS,JTK,LS}, combines p by Fisher's method -> `meta2d_pvalue` (BH -> `meta2d_BH.Q`), averages period, circular-averages phase | Fisher assumes INDEPENDENT p; ARS/JTK/LS on the same data are correlated, so `meta2d_BH.Q` is NOT a literal FDR (read it as a rank aid); `analysisStrategy='auto'` SILENTLY drops ARS/JTK on uneven/replicated data (may run LS only); averaged period is meaningless when methods disagree |

For between-condition comparison, see temporal-genomics/differential-rhythmicity - none of the single-condition tests above answer it correctly.

## Design constraints (upstream of any method; non-negotiable)

- >=2 full cycles (48h circadian minimum; 3 cycles / 72h improves power and reveals damping). One cycle cannot distinguish an oscillation from a monotone trend or a single transient.
- >=6, ideally 8-12+, samples/cycle. 2-4h spacing is standard; 1-2h is needed to resolve waveform shape or fast harmonics. Sparse designs are exactly where JTK's calibration fails.
- >=2-3 biological replicates/timepoint. Single-replicate designs cripple FDR calibration (no within-timepoint variance; empirical-null/bootstrap corrections cannot work). Replication in TIME and AT a timepoint buy different things - do not trade all of one for the other.
- Harvest-ORDER confound (the silent killer): collecting/extracting/sequencing timepoints in temporal order aliases any drift (reagent lots, RIN, lane position) PERFECTLY onto ZT and manufactures spurious 24h rhythms. No rhythmicity test detects this. Fix by DESIGN: randomize processing order, balance replicates across batches, model batch as a covariate (trivial in a limma/DESeq2 design). It cannot be repaired analytically because batch and the rhythm are the same axis.

## CosinorPy (Python)

**Goal:** Test each feature for rhythmicity at a known period and estimate amplitude, relative amplitude, acrophase, and MESOR with FDR control.

**Approach:** Fit cosine curves per feature with `fit_group` (batch), use its built-in BH `q` column (or recompute BH over a chosen correction set), then filter on both q and relative amplitude.

### Single- and multi-component fit

Fits `y = M + A*cos(2*pi*t/T + phi)` where M = MESOR (rhythm-adjusted midline, NOT the arithmetic mean unless sampling is balanced), A = amplitude, phi = acrophase stored as `atan2(-gamma, beta)` (usually negative).

```python
from CosinorPy import cosinor, cosinor1, file_parser

df = file_parser.read_csv('expression_timecourse.csv')  # long format: columns x (time), y (value), test (feature id)

# Single-component (sinusoidal). period=24: standard circadian period in hours.
# fit_me returns a 5-tuple: (results, statistics, rhythm_params, X_test, Y_fit_test).
single = cosinor.fit_me(df[df['test'] == 'Arntl']['x'].values,
                        df[df['test'] == 'Arntl']['y'].values,
                        period=24, n_components=1)

# Multi-component adds harmonics for non-sinusoidal shape; add ONLY with dense sampling + a biological reason.
# fit_me takes a SINGLE n_components (an int); n_components=2 adds one 12h harmonic to the 24h fundamental.
two_comp = cosinor.fit_me(df[df['test'] == 'Dbp']['x'].values,
                          df[df['test'] == 'Dbp']['y'].values,
                          period=24, n_components=2)

# To let CosinorPy PICK the harmonic order by information criterion, fit a range with fit_group over a
# candidate list, then select per feature with get_best_models (do not pass a list to fit_me).
group_multi = cosinor.fit_group(df, period=24, n_components=[1, 2, 3], plot=False)
best_models = cosinor.get_best_models(df, group_multi, n_components=[1, 2, 3])
```

### Batch analysis with built-in q-values

**Goal:** Score every feature genome-wide and keep confident, high-amplitude oscillators.

**Approach:** `fit_group` returns per-feature statistics INCLUDING a BH-adjusted `q` column; add an rAMP effect-size filter on top of q.

```python
import numpy as np
from statsmodels.stats.multitest import multipletests

# fit_group returns columns: test, period, n_components, p, q, p_reject, q_reject, RSS, R2, R2_adj,
# log-likelihood, amplitude, acrophase, mesor, peaks, heights, troughs, heights2, ME, resid_SE.
results = cosinor.fit_group(df, period=24, n_components=1, plot=False)

# 'q' is already BH-adjusted across the fitted group. Recompute BH only if the correction SET should differ
# (e.g. exclude non-expressed features first). Default multipletests method is Holm-Sidak, so pass fdr_bh explicitly.
valid = results['p'].notna()
results.loc[valid, 'q_bh'] = multipletests(results.loc[valid, 'p'], method='fdr_bh')[1]

# rAMP = amplitude / MESOR normalizes out expression level so calls are comparable across features.
# rAMP > 0.1 (>=10% of baseline) is a conventional biological-relevance floor - sweep it, do not treat as law.
results['rAMP'] = results['amplitude'] / results['mesor']
rhythmic = results[(results['q'] < 0.05) & (results['rAMP'] > 0.1)]
```

### Population-mean cosinor (replicated / multi-subject)

**Goal:** Get group-level amplitude/phase with CIs that propagate BETWEEN-subject variance, instead of pseudoreplicating.

**Approach:** Fit one cosinor per subject and combine the estimates - pooling all subjects' points into one fit understates uncertainty.

```python
# cosinor1.population_fit_cosinor returns a DICT with keys: test, names, values, means, confint (nested amp/acr/mesor CIs),
# p_value, p_amp, p_acr, p_mesor (all underscore; e.g. pop['confint']['amp'], pop['p_amp']).
pop = cosinor1.population_fit_cosinor(subject_df, period=24, plot_on=False)
# cosinor1.population_fit_group(df, period=24) batches this across groups; cosinor1.population_test_cosinor_pairs
# compares two populations' rhythms (a differential-rhythmicity test on replicated data).
```

Convert acrophase to peak-hour with `peak_h = (-acrophase) * T / (2*pi) % T`; sanity-check against a known clock gene (mouse liver Arntl/Bmal1 peaks ~CT22-0, Nr1d1 ~CT4-6, Dbp ~CT8-10).

## MetaCycle meta2d (R)

**Goal:** Produce a robust consensus rhythmicity rank on an evenly sampled design.

**Approach:** Run meta2d over {JTK,ARS,LS}; read `meta2d_BH.Q` as a ranking aid (Fisher over correlated nulls, not a literal FDR), and distrust the averaged period/phase when constituents disagree.

```r
library(MetaCycle)
# minper=maxper=24 for entrained (LD) data; 22-26 for free-running (DD) where tau != 24h.
# timepoints must match column order. ARS/JTK need EVEN integer sampling with no missing values / no replicates;
# analysisStrategy='auto' silently drops ineligible methods (may leave LS only) - check the per-method columns.
# timepoints span 0-68h at 4h resolution: >=2 full 24h cycles at ~6 samples/cycle (the design floor this skill sets).
meta2d(infile = 'expression_matrix.csv', filestyle = 'csv', outdir = 'metaout',
       timepoints = seq(0, 68, by = 4), cycMethod = c('JTK', 'ARS', 'LS'),
       minper = 24, maxper = 24, outputFile = TRUE, outRawData = FALSE)

res <- read.csv('metaout/meta2d_expression_matrix.csv')
# meta2d_pvalue (Fisher-combined), meta2d_BH.Q, meta2d_period, meta2d_phase (hours from ZT0, peak time),
# meta2d_Base (baseline/MESOR), meta2d_AMP, meta2d_rAMP (= AMP/Base). Filter on rank AND relative amplitude.
rhythmic <- res[res$meta2d_BH.Q < 0.05 & res$meta2d_rAMP > 0.1, ]
```

## RAIN (R/Bioconductor)

**Goal:** Detect ASYMMETRIC waveforms (fast induction, slow decay) that cosinor/JTK miss.

**Approach:** Transpose to one-row-per-timepoint, declare replicate count, adjust p for multiple testing.

```r
library(rain)
# x needs ONE ROW PER TIMEPOINT (transpose a features x timepoints matrix). deltat = sampling interval (h).
# nr.series = replicates per timepoint (interleaved r1t1,r2t1,r1t2,...). method='independent' vs 'longitudinal'
# sets replicate handling. peak.border controls the allowed rising-fraction (asymmetry) window.
res <- rain(t(expression_mat), period = 24, deltat = 4, nr.series = 2, method = 'independent')
res$q <- p.adjust(res$pVal, method = 'BH')  # output columns: pVal, phase, peak.shape, period
rhythmic <- res[res$q < 0.05, ]
```

## DiscoRhythm (R/Bioconductor)

**Goal:** Run Cosinor/JTK/LS/ARS under one interface with built-in QC/PCA (scripted or Shiny).

```r
library(DiscoRhythm)
se <- discoGetSimu(TRUE)                                   # bundled demo SummarizedExperiment
disco <- discoBatch(se, osc_method = 'CS', report = NULL, osc_period = 24)  # osc_method='CS'=Cosinor; report=NULL skips the HTML report
```

Comparing rhythms BETWEEN conditions (differential rhythmicity: gain/loss/phase-shift/amplitude-change with LimoRhyde/dryR/compareRhythms, and the detect-then-Venn anti-pattern) is a distinct analysis - see temporal-genomics/differential-rhythmicity. Do NOT infer "genes that lost rhythm in the KO" by subtracting two independently thresholded single-condition rhythm lists.

## Common Errors (trap -> fix)

| Trap | Fix |
|------|-----|
| Opening a wide period window on a known-period test | Fix `minper=maxper=24` (entrained) or 22-26h (free-running); a wide window is discovery, not testing, and inflates false positives |
| Trusting JTK p-values / BH-Q from a single-replicate sparse design | Expect anti-conservative, quantized p-values; use eJTK/BooteJTK (empirical/bootstrap null) and inspect the genome-wide p-value HISTOGRAM before believing FDR |
| Reading `meta2d_BH.Q` as a literal FDR | Fisher integration over correlated ARS/JTK/LS p-values is not calibrated; use it as a consensus RANK and distrust averaged period/phase when methods disagree |
| Calling reduced BULK amplitude "arrhythmic" | Ensemble amplitude damps from cell DESYNCHRONY too; report "reduced ensemble amplitude" and use single-cell or imaging assays to separate loss-of-rhythm vs loss-of-synchrony |
| Claiming an "endogenous circadian rhythm" from LD data | LD rhythms can be light/feeding-DRIVEN (masking); endogeneity requires free-running (DD/constant) conditions. Diurnal != circadian. Use ZT for entrained, CT for free-running |
| Claiming a rhythm is "clock-CONTROLLED" from wild-type data alone | Persistence in DD proves endogeneity, not clock control; genetic dependence needs a clock-gene perturbation (compare WT vs clock-mutant, see temporal-genomics/differential-rhythmicity) |
| Mixing phase units/conventions (radians vs hours, +phi vs -phi, ZT vs CT) | State the convention; convert CosinorPy acrophase via `peak_h = (-acrophase)*T/(2*pi) % T`; sanity-check against a known clock gene's phase |
| Ranking features by RAW amplitude across the genome | Raw amplitude scales with expression and normalization; use relative amplitude (AMP/MESOR) or peak-to-trough fold-change for cross-feature comparison and the amplitude filter |
| Reporting significant rhythms with NO effect-size filter | Significance alone over-detects (Laloum 2020); add an rAMP/fold-change cutoff and report the amplitude DISTRIBUTION of the hit list, not just the count |
| Trusting phase/amplitude POINT estimates for near-threshold features | Estimation is unreliable where detection is marginal; interpret parameters only for confidently rhythmic features |
| Overfitting with `n_components=3` on 6-8 points/cycle | Harmonics cost 2 df each; use AIC/BIC or automatic model selection; add harmonics only with dense sampling and a biological reason |
| Harvest-order drift confounded with ZT | Randomize PROCESSING order, balance replicates across batches, model batch as a covariate; no rhythmicity test detects this |
| Feeding replicates to cosinor as one pooled single-fit | Use population-mean cosinor (subject = replication unit) so between-subject variance enters the CI and the test |

## The over-detection controversy (state it as live)

Laloum & Robinson-Rechavi (2020) showed that across seven popular methods (ARS, LS, RAIN, JTK, eJTK, GeneCycle, meta2d) rhythm calls are consistent and biologically meaningful ONLY for strong-amplitude signals; weak-signal calls are method-dependent and largely non-functional. There is no consensus "correct" method. The pragmatic (not full) response: (1) require an amplitude/rAMP effect-size filter IN ADDITION to FDR; (2) prefer methods with calibrated empirical nulls (eJTK, BooteJTK) over raw JTK on sparse data; (3) verify the genome-wide p-value histogram is roughly uniform with a spike near 0 before trusting any q. Report the amplitude distribution of the hit list, not just "N% of the transcriptome is rhythmic."

## Parameter Guide

| Parameter | Typical value | Rationale |
|-----------|---------------|-----------|
| Period | 24h (12h for ultradian) | Specified a priori; this is a test, not a search |
| Period window | 24 (LD) / 22-26 (DD) | Entrained locks to 24h; free-running tau != 24h. Wide windows inflate false positives |
| Sampling interval | 2-4h | Nyquist (<=12h) is a floor, not a target; shape resolution needs 1-2h |
| Cycles | >=2 (>=3 better) | One cycle cannot separate rhythm from trend/transient |
| Samples/cycle | >=6 (8-12+ better) | Six gives stable fit df; more resolves waveform and calibrates FDR |
| Replicates/timepoint | >=2-3 | Single replicate has no within-timepoint variance; FDR miscalibrates |
| FDR threshold | q < 0.05 | Necessary but not sufficient; always pair with an amplitude filter |
| Relative amplitude | rAMP > 0.1 | >=10% of baseline as a biological-relevance floor; a convention to sweep, not a law |

## Related Skills

temporal-genomics/differential-rhythmicity - Comparing rhythms between conditions (gain/loss/phase/amplitude change)
temporal-genomics/periodicity-detection - Unknown-period discovery with Lomb-Scargle and wavelets
temporal-genomics/temporal-clustering - Group rhythmic genes by phase/shape
differential-expression/timeseries-de - Temporal differential expression (a monotone trend, not rhythmicity)
data-visualization/heatmaps-clustering - Circular phase heatmaps and phase-ordered maps

## References

- Hughes ME, Hogenesch JB, Kornacker K. 2010. JTK_CYCLE: an efficient nonparametric algorithm for detecting rhythmic components in genome-scale data sets. J Biol Rhythms 25(5):372-380. doi:10.1177/0748730410379711
- Hughes ME, Abruzzi KC, Allada R, et al. 2017. Guidelines for genome-scale analysis of biological rhythms. J Biol Rhythms 32(5):380-393. doi:10.1177/0748730417728663
- Thaben PF, Westermark PO. 2014. Detecting rhythms in time series with RAIN. J Biol Rhythms 29(6):391-400. doi:10.1177/0748730414553029
- Wu G, Anafi RC, Hughes ME, Kornacker K, Hogenesch JB. 2016. MetaCycle: an integrated R package to evaluate periodicity in large scale data. Bioinformatics 32(21):3351-3353. doi:10.1093/bioinformatics/btw405
- Yang R, Su Z. 2010. Analyzing circadian expression data by harmonic regression based on autoregressive spectral estimation (ARSER). Bioinformatics 26(12):i168-i174. doi:10.1093/bioinformatics/btq189
- Hutchison AL, Maienschein-Cline M, Chiang AH, et al. 2015. Improved statistical methods enable greater sensitivity in rhythm detection for genome-wide data (eJTK). PLoS Comput Biol 11(3):e1004094. doi:10.1371/journal.pcbi.1004094
- Cornelissen G. 2014. Cosinor-based rhythmometry. Theor Biol Med Model 11:16. doi:10.1186/1742-4682-11-16
- Laloum D, Robinson-Rechavi M. 2020. Methods detecting rhythmic gene expression are biologically relevant only for strong signal. PLoS Comput Biol 16(3):e1007666. doi:10.1371/journal.pcbi.1007666
- Mei W, Jiang Z, Chen Y, Chen L, Sancar A, Jiang Y. 2021. Genome-wide circadian rhythm detection methods: systematic evaluations and practical guidelines. Brief Bioinform 22(3):bbaa135. doi:10.1093/bib/bbaa135
- Moškon M. 2020. CosinorPy: a python package for cosinor-based rhythmometry. BMC Bioinformatics 21:485. doi:10.1186/s12859-020-03830-w
<!-- END FILE: temporal-genomics/circadian-rhythms/SKILL.md -->

## 子目录：temporal-genomics/differential-rhythmicity

<!-- BEGIN FILE: temporal-genomics/differential-rhythmicity/SKILL.md -->
---
name: bio-temporal-genomics-differential-rhythmicity
description: Compares how a rhythm CHANGES between conditions, genotypes, treatments, tissues, or ages (differential rhythmicity), classifying each feature as gain-of-rhythm, loss-of-rhythm, phase change, amplitude change, unchanged-rhythmic, or arrhythmic-in-both, and distinguishing differential EXPRESSION (condition main effect) from differential RHYTHMICITY (condition x time interaction). Uses model-based approaches that borrow strength across conditions - LimoRhyde (sin/cos interaction terms in a limma/edgeR/DESeq2 design), dryR (BIC model selection across >=2 conditions), compareRhythms (direct gain/loss/change/same classification), DODR, CircaCompare - instead of the detect-then-Venn anti-pattern that overestimates reprogramming. Use when testing whether rhythms differ between conditions/genotypes/tissues/ages, classifying gain/loss/phase/amplitude change, or separating differential expression from differential rhythmicity. Not for detecting rhythms in one condition (see temporal-genomics/circadian-rhythms).
tool_type: r
primary_tool: limorhyde
---

## Version Compatibility

Reference examples tested with: limorhyde 1.0+, limma 3.50+, compareRhythms 1.0+, dryR (GitHub naef-lab), DODR 0.99+, CircaCompare 0.2+, R 4.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: differential rhythmicity estimates an INTERACTION (condition x time), so it needs MORE power than single-condition detection - the same matched, evenly-sampled, replicated grid must exist in BOTH conditions, and unmatched timepoints across conditions break the interaction model.

# Differential Rhythmicity (comparing rhythms between conditions)

**"How does this gene's rhythm change in the knockout / high-fat diet / aged tissue?"** -> classify each feature's rhythm CHANGE relative to a reference condition into gain, loss, phase, or amplitude change, using a model that borrows strength across conditions.
- R: `limorhyde()` (sin/cos basis for a limma/edgeR/DESeq2 interaction model); `compareRhythms()` (direct gain/loss/change/same classification); `dryseq()` (dryR, BIC model selection); `DODR`, `circacompare()`, `diffCircadian` (targeted comparators)

This is the sibling of temporal-genomics/circadian-rhythms, which asks the single-condition question "is this feature rhythmic at 24h?" (cosinor/JTK/RAIN detection). Do not re-run detection here; this skill answers the categorically different question of how a rhythm DIFFERS between groups.

## The governing principle: differential rhythmicity is a distinct question, and detect-then-Venn overestimates it

The #1 error is the detect-then-Venn anti-pattern: defining "genes that lost rhythm in the KO" as "rhythmic in WT MINUS rhythmic in KO" from two independently thresholded rhythmicity lists. This systematically OVERESTIMATES reprogramming, because near p~0.05 the two lists differ mostly from threshold noise, not biology - a gene at q=0.04 in WT and q=0.06 in KO is called "lost" when nothing changed (Pelikan 2022 *FEBS J* 289:6605). The fix is to never intersect two lists: fit ONE model spanning both conditions and test the condition x time INTERACTION directly, so a single calibrated test asks "did the rhythm change?" with strength borrowed across conditions.

The second load-bearing distinction is differential EXPRESSION vs differential RHYTHMICITY. A gene whose mean level shifts between conditions but whose oscillation is unchanged is differentially EXPRESSED, not differentially rhythmic. In the sin/cos framing these are orthogonal: the condition MAIN effect = differential expression (mean shift, adjusting for time), the condition:time INTERACTION = differential rhythmicity (amplitude/phase change). Reporting a main-effect hit as "rhythm reprogramming" is a common and wrong conflation.

## The four canonical outcome classes (relative to a reference group)

| Class | What changed | Interaction signature |
|-------|--------------|-----------------------|
| Gain of rhythm | arrhythmic in reference, rhythmic in test | interaction significant; reference amplitude ~0 |
| Loss of rhythm | rhythmic in reference, arrhythmic in test | interaction significant; test amplitude ~0 |
| Phase change | rhythmic in both, peak time shifted | interaction significant; amplitudes similar, acrophases differ |
| Amplitude change | rhythmic in both, oscillation damped/amplified | interaction significant; same phase, amplitudes differ |
| Unchanged-rhythmic (same) | rhythmic in both, same amplitude+phase | interaction NOT significant; both rhythmic |
| Arrhythmic-in-both | flat in both | neither main effect nor interaction; excluded by amplitude filter |

Interpret phase and amplitude CHANGE only for features confidently rhythmic in AT LEAST ONE condition; a "phase shift" between two genes that are arrhythmic in both is noise. Amplitude-filter first (peak-to-trough or relative amplitude), then classify.

## Method selection (which to pick and why)

| Method | Pick when | Mechanism | Fails / caveat |
|--------|-----------|-----------|----------------|
| LimoRhyde + limma/edgeR/DESeq2 | 2 conditions; want to fold DR into a standard DE pipeline with covariates/batch; count or microarray data | `limorhyde()` adds sin/cos time columns; condition:time interaction = DR, condition main effect = DE | Two-condition framing; the interaction test flags THAT a rhythm changed, not which class - read per-condition amplitude/phase to classify |
| dryR (`dryseq`) | >=2 conditions; want a parsimonious per-gene MODEL assignment (shared vs independent rhythm parameters) | BIC model selection over a family of shared/independent-parameter models, tailored to RNA-seq noise | Model-selection categories depend on the model family and BIC penalty; needs enough timepoints for BIC to discriminate models |
| compareRhythms | want gain/loss/change/same DIRECTLY, built to replace the Venn approach; microarray or RNA-seq | wraps model-selection (`mod_sel`) or hypothesis tests (`dodr`/`limma`/`voom`/`deseq2`/`edger`/`cosinor`); classifies vs reference | Two groups only; `mod_sel` needs no DE package but `deseq2`/`edger`/`voom` do; a feature must clear `amp_cutoff` in >=1 group to be reported |
| DODR | direct two-condition differential-rhythmicity test on already-detected rhythmic features | robust/rank comparison of rhythm shape (amplitude, phase, signal-to-noise) between conditions | Tests differential rhythmicity given rhythmicity; pre-filter to features rhythmic in >=1 group first |
| CircaCompare | a FEW targeted genes; want explicit estimates + p-values for the mesor/amplitude/phase DIFFERENCE | non-linear regression fitting both curves jointly with difference parameters | Compares two groups only if BOTH are rhythmic (amplitude non-zero); not a genome-scale screen |
| diffCircadian | a few genes; want likelihood-ratio tests separating differential amplitude vs phase vs basal vs fit | likelihood-based tests (`LR_diff`) on two conditions | Two conditions; targeted rather than transcriptome-wide throughput |

Methodology here is evolving (LimoRhyde2 reframes around effect-size/posterior shrinkage; benchmarks disagree on the best classifier) - verify current best practice against the latest tool docs before committing to one method, and prefer a screen (LimoRhyde/dryR/compareRhythms) followed by targeted confirmation (CircaCompare/diffCircadian) on hits.

## LimoRhyde + limma interaction test

**Goal:** Rank features by differential rhythmicity between two conditions while separately quantifying differential expression, in a single linear model.

**Approach:** Decompose measured time into a sin/cos basis with `limorhyde()`, fit `condition*(time_cos+time_sin)`, moderated-F-test the two interaction coefficients for DR and the condition main effect for DE.

```r
library(limorhyde); library(limma)

# limorhyde() decomposes measured time into a cosinor basis; prefix 'time_' names them time_cos, time_sin.
# period = 24h circadian; time is MEASURED (ZT/CT), not inferred pseudotime.
meta <- cbind(meta, limorhyde(meta$time, 'time_', period = 24))

# Differential RHYTHMICITY = condition:time interaction; differential EXPRESSION = condition main effect.
design <- model.matrix(~ condition * (time_cos + time_sin), data = meta)
fit <- eBayes(lmFit(expr, design))   # expr: features x samples, columns aligned to meta rows

dr_cols <- grep('conditionKO:time_', colnames(design), value = TRUE)  # the two interaction coefficients
dr <- topTable(fit, coef = dr_cols, number = Inf, sort.by = 'F')      # BH-adjusted adj.P.Val ranks DR
de <- topTable(fit, coef = 'conditionKO', number = Inf, sort.by = 'p')  # condition main effect = DE
```

The interaction F-test says a rhythm changed; it does not name the class. To assign gain/loss/phase/amplitude, fit a per-condition cosinor (or read `limorhyde2` posterior estimates) and compare amplitudes and acrophases between conditions for the significant features. For count data, run the same design through `voom`+limma, edgeR, or DESeq2 with the sin/cos and interaction columns.

## compareRhythms direct classification

**Goal:** Assign every feature directly to gain / loss / change / same relative to a reference condition, without intersecting two detection lists.

**Approach:** Pass a features x samples matrix plus an `exp_design` data.frame (numeric `time`, 2-level factor `group`), choose a `method`, and read the returned category per feature.

```r
library(compareRhythms)

# exp_design: one row per sample; numeric 'time', factor 'group' with EXACTLY 2 levels (reference first).
# data: numeric matrix, rows = features (rownames = ids), columns = samples matching exp_design rows.
# method='mod_sel' = BIC model selection (no DE package); 'deseq2'/'edger'/'voom' for RNA-seq counts;
# 'limma' for log-microarray; 'dodr'/'cosinor' also available. amp_cutoff = peak-to-trough floor (>=1 group).
res <- compareRhythms(data, exp_design = exp_design, period = 24,
                      method = 'mod_sel', amp_cutoff = 0.5, criterion = 'bic')
# res: data.frame with id + category (gain / loss / change / same, relative to the reference group).
```

For >2 conditions, dryR does BIC model selection across all conditions at once: `dryseq(counts, group, time)` assigns each gene a rhythm-parameter-sharing model and returns per-condition amplitude/phase/mean. Prefer it over pairwise interaction tests when the design has three or more groups and a parsimonious classification is wanted.

## The confounds a differential-rhythmicity claim must address

**Reduced bulk amplitude can be loss of SYNCHRONY, not loss of per-cell rhythm.** A bulk/tissue readout is the sum over many single-cell oscillators; if cells DESYNCHRONIZE (dephase) between conditions, the ensemble amplitude damps toward zero even though every cell still oscillates. Bulk "amplitude change" or "loss of rhythm" therefore has three indistinguishable causes: true loss of cell-autonomous rhythmicity, loss of inter-cell synchrony, or reduced single-cell amplitude. Report it as "reduced ensemble amplitude" and use single-cell or live-imaging assays to separate the causes; see single-cell/preprocessing for cell-level analysis.

**A rhythm change under light-dark may be a driven change, not a clock change.** Under an entraining LD cycle, an apparent rhythm can be masked (driven directly by light/feeding/temperature). A between-condition difference (e.g. a feeding-time or lighting manipulation) can shift the DRIVEN component without touching the endogenous clock. Only free-running (DD/constant) conditions license "the clock rewired"; under LD, a differential-rhythmicity hit may reflect a change in the environmental drive. Declare the light regime and use ZT (entrained) vs CT (free-running) accordingly.

## Design constraints (shared with detection, stricter here)

- Matched sampling GRID across conditions: the SAME timepoints, evenly spaced, in every condition. Unmatched timepoints break the interaction model (the condition:time terms become non-estimable or confounded) - this is the constraint most often violated when two datasets are compared post hoc.
- >=2 full cycles and >=6 (ideally 8-12) samples/cycle in EACH condition (the genome-scale rhythm-analysis design guidelines of Hughes et al. 2017 apply per condition). One cycle cannot separate a rhythm from a trend, so it certainly cannot compare rhythms.
- Replicates per timepoint in each condition. DR estimates an interaction (a difference of differences), so it is hungrier for power than detection; a design just adequate to detect a rhythm is usually too thin to confidently call a rhythm CHANGE.
- The amplitude filter is not optional. Classify phase/amplitude change only for features confidently rhythmic in at least one condition; significance without an effect-size floor over-detects (Laloum 2020 *PLoS Comput Biol* 16:e1007666), and the effect is worse for a difference test.

## Common Errors (trap -> fix)

| Trap | Fix |
|------|-----|
| Defining "lost rhythm" as (rhythmic in WT) minus (rhythmic in KO) via two thresholded lists | Fit one model across both conditions and test the condition:time INTERACTION (LimoRhyde/dryR/compareRhythms); the Venn approach overestimates reprogramming (Pelikan 2022) |
| Calling a condition MAIN-effect (mean-shift) hit "differential rhythmicity" | Main effect = differential EXPRESSION; differential RHYTHMICITY is the condition:time INTERACTION. Report them separately |
| Unmatched or unevenly-spaced timepoints across conditions | Use a matched, evenly-sampled grid in every condition; unmatched times make the interaction terms non-estimable or confound them with condition |
| Interpreting a "phase shift" for features arrhythmic in both conditions | Amplitude-filter FIRST; classify phase/amplitude change only for features confidently rhythmic in >=1 condition |
| Calling reduced BULK amplitude "loss of rhythm" | Ensemble amplitude damps from cell DESYNCHRONY too; report "reduced ensemble amplitude" and separate with single-cell or imaging assays |
| Claiming the clock "rewired" from LD (entrained) data | An LD rhythm change can be a driven/masking change (light/feeding); endogenous rewiring needs free-running (DD) conditions |
| Running DR on a design too sparse to even DETECT a rhythm | DR needs MORE power than detection (it estimates an interaction); ensure >=2 cycles, >=6/cycle, replicates in EACH condition before comparing |
| Reading the interaction F-test as the CLASS | The interaction says a rhythm changed, not which class; fit per-condition amplitude/phase (or LimoRhyde2 posteriors) to assign gain/loss/phase/amplitude |
| Using compareRhythms `deseq2`/`edger`/`voom` on already-normalized log data | Those methods expect RAW counts; use `mod_sel`/`limma`/`cosinor` for normalized or microarray data |

## Related Skills

temporal-genomics/circadian-rhythms - Single-condition rhythm DETECTION and parameter estimation (cosinor/JTK/RAIN); run it first, this skill compares its results across conditions
differential-expression/timeseries-de - Temporal differential expression (a monotone trend or between-timepoint change), which is differential EXPRESSION over time, not differential rhythmicity
temporal-genomics/temporal-clustering - Group differentially-rhythmic genes by the shape of their change
single-cell/preprocessing - Entry to cell-level analysis, to separate reduced ensemble amplitude (desynchrony) from true loss of per-cell rhythm

## References

- Singer JM, Hughey JJ. 2019. LimoRhyde: a flexible approach for differential analysis of rhythmic transcriptome data. J Biol Rhythms 34(1):5-18. doi:10.1177/0748730418813785
- Weger BD, Gobet C, David FPA, et al. 2021. Systematic analysis of differential rhythmic liver gene expression mediated by the circadian clock and feeding rhythms (dryR). PNAS 118(3):e2015803118. doi:10.1073/pnas.2015803118
- Pelikan A, Herzel H, Kramer A, Ananthasubramaniam B. 2022. Venn diagram analysis overestimates the extent of circadian rhythm reprogramming (compareRhythms). FEBS J 289(21):6605-6621. doi:10.1111/febs.16095
- Thaben PF, Westermark PO. 2016. Differential rhythmicity: detecting altered rhythmicity in biological data (DODR). Bioinformatics 32(18):2800-2808. doi:10.1093/bioinformatics/btw309
- Parsons R, Parsons R, Garner N, Oster H, Rawashdeh O. 2020. CircaCompare: a method to estimate and statistically support differences in mesor, amplitude and phase, between circadian rhythms. Bioinformatics 36(4):1208-1212. doi:10.1093/bioinformatics/btz730
- Ding H, Meng L, Liu AC, et al. 2021. Likelihood-based tests for detecting circadian rhythmicity and differential circadian patterns in transcriptomic applications (diffCircadian). Brief Bioinform 22(6):bbab224. doi:10.1093/bib/bbab224
- Hughes ME, Abruzzi KC, Allada R, et al. 2017. Guidelines for genome-scale analysis of biological rhythms. J Biol Rhythms 32(5):380-393. doi:10.1177/0748730417728663
- Laloum D, Robinson-Rechavi M. 2020. Methods detecting rhythmic gene expression are biologically relevant only for strong signal. PLoS Comput Biol 16(3):e1007666. doi:10.1371/journal.pcbi.1007666
<!-- END FILE: temporal-genomics/differential-rhythmicity/SKILL.md -->

## 子目录：temporal-genomics/periodicity-detection

<!-- BEGIN FILE: temporal-genomics/periodicity-detection/SKILL.md -->
---
name: bio-temporal-genomics-periodicity-detection
description: Discovers a periodic signal of UNKNOWN period in time-series omics data and puts a defensible significance on it, especially when sampling is IRREGULAR (dropped timepoints, pooled harvests) so FFT/Welch/JTK are invalid. Estimates the dominant period with Lomb-Scargle / generalized Lomb-Scargle (scipy, astropy), corroborates with autocorrelation, resolves transient/time-varying periodicity with the wavelet CWT (pywt), and screens genome-wide with false-alarm probabilities under BH FDR. Use when finding an oscillation whose period is not known a priori, analyzing cell-cycle or ultradian rhythms, or handling unevenly sampled time courses. Not for testing a KNOWN 24-hour rhythm (see temporal-genomics/circadian-rhythms).
tool_type: python
primary_tool: scipy
---

## Version Compatibility

Reference examples tested with: numpy 2.2+, scipy 1.15+ (lombscargle floating_mean present), astropy 8.0+, PyWavelets 1.8+, statsmodels 0.14+, matplotlib 3.8+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- scipy: `scipy.signal.lombscargle` changed in 1.17 (`precenter` deprecated -> removed 1.19; use `floating_mean=True` or pre-center). Check `scipy.__version__`.

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Periodicity Detection

**"Find a periodic pattern of unknown period in my time-series data"** -> Estimate the dominant period, attach a false-alarm probability, and (for transient signals) localize it in time. This is the complement of temporal-genomics/circadian-rhythms, which TESTS a known 24 h period; here the period is unknown and sampling is often uneven.

## Governing Principle

Unknown-period discovery is an ESTIMATION problem stacked on a DETECTION problem, and uneven sampling corrupts both. (1) Estimation: the period is a continuous quantity with a confidence region, not a yes/no on 24 h. (2) Detection: a periodogram peak is a random variable even under pure noise, and the MAX over a frequency grid is extreme-value-distributed, so significance is the False Alarm Probability (FAP) of that max, NOT the raw peak height. (3) Sampling design dominates: regular-grid methods (FFT, Welch, JTK, RAIN) assume equal spacing; genomics rarely delivers it (a timepoint fails QC, harvests are pooled, sampling is denser early). For uneven sampling the Lomb-Scargle least-squares periodogram replaces the FFT.

The single most important consequence: do NOT interpolate-then-FFT. Interpolation is a low-pass filter that injects spurious low-frequency power, suppresses power near the average Nyquist, and biases the whole spectrum red. Analyze the uneven series directly with Lomb-Scargle; interpolate only when a wavelet transform forces a grid, and flag it as an assumption.

## Method Selection

| Method | Sampling | Estimates | Significance model | Fails when |
|--------|----------|-----------|--------------------|-----------|
| Generalized Lomb-Scargle (astropy default, or scipy `floating_mean=True`) | Uneven OK | Global dominant period(s), amplitude, phase | Baluev analytic FAP (screen); bootstrap (few hits) | <2 cycles; strong harmonics; red noise mistaken for a peak |
| Classic Lomb-Scargle (scipy, pre-centered) | Uneven OK | Global dominant period | Permutation / Baluev via astropy | Nonzero-mean data if not centered; sparse points |
| Autocorrelation (statsmodels) | Even only | Fundamental period (coarse) | Bartlett bands (weak) | Uneven sampling; trend; poor resolution -> use as CHECK only |
| Wavelet CWT (pywt Morlet) | Even (interp small gaps) | Time-varying / transient period | Torrence-Compo AR(1) chi-square + COI mask | Edge claims (COI); needs a grid -> interpolation caveat |
| Welch PSD (scipy) | Even required | Smoothed global PSD | Segment-averaging variance reduction | Any gaps; long/close periods vs `nperseg` |
| Fisher's g-test (Wichert 2004) | Even only | Single dominant frequency, exact p | Exact analytic (white null) | Uneven sampling; red noise (white-null limitation) |

Decision spine: uneven times -> GLS + Baluev FAP -> BH FDR for a genome-wide screen; suspected transient -> CWT with COI + red-noise chi-square; even and want a quick classical p -> Fisher's g; ACF/Welch are even-sampling sanity checks, never the primary estimate. Re-verify the astropy FAP methods and scipy `floating_mean`/`normalize` semantics against the installed versions before relying on them.

## Lomb-Scargle Periodogram

**Goal:** Estimate the dominant period of an unevenly sampled series and attach a false-alarm probability.

**Approach:** Fit a sinusoid (plus a floating offset) at each trial frequency over a grid whose min/max and density are set from the record length, then read the peak period and its FAP. Prefer the generalized LS (floating mean) so a poorly-determined offset cannot leak into the amplitude.

Lomb-Scargle is NOT an FFT with jitter tolerance; it is a least-squares sinusoid fit at each frequency, invariant to time-origin, and (for even sampling) equivalent to the classical periodogram. Classical LS assumes zero-mean data; expression is always positive, so a nonzero mean leaks into the sinusoid and inflates power. Two correct fixes: pre-center (`y - y.mean()`, plug-in mean, old-school) or fit a per-frequency floating mean (generalized LS, the modern default).

### scipy: classic (pre-centered) vs generalized

```python
import numpy as np
from scipy.signal import lombscargle

# scipy uses ANGULAR frequency (rad/time): omega = 2*pi/period. Mixing ordinary
# frequency (1/period) is the #1 units bug -> periods off by 2*pi.
periods = np.linspace(6.0, 72.0, 2000)   # biologically plausible periods
angular = 2 * np.pi / periods

# Classic LS assumes zero mean: pre-center or power is inflated/distorted.
power_classic = lombscargle(times, values - values.mean(), angular, normalize=True)

# Generalized LS: fit a floating offset per frequency (Zechmeister & Kuerster).
# Preferred with sparse/uneven data; pass RAW values. floating_mean added in scipy
# 1.15; before that, pre-center. `precenter` is deprecated in 1.17, removed in 1.19.
power_gls = lombscargle(times, values, angular, normalize=True, floating_mean=True)

dominant_period = periods[np.argmax(power_gls)]
```

### astropy: generalized LS by default, with real FAP

**Goal:** Get a peak period plus a Baluev false-alarm probability, using a grid astropy sizes automatically.

**Approach:** astropy's LombScargle fits a floating mean by default; pass RAW values, let `autopower` build a correctly oversampled grid, then convert the peak power to a FAP.

```python
from astropy.timeseries import LombScargle

# fit_mean=True and center_data=True by DEFAULT -> generalized LS out of the box.
# Pass RAW values; pre-centering here is redundant. Uses ORDINARY frequency
# (cycles/time), NOT angular -> do not reuse a scipy omega-grid.
ls = LombScargle(times, values)          # add dy=sigma for heteroskedastic weighting
freq, power = ls.autopower(
    minimum_frequency=1 / 72.0,          # <= 1/record-span; need >=2 cycles to trust
    maximum_frequency=1 / 6.0,           # pseudo-Nyquist; uneven times can exceed 1/(2*dt_mean)
    samples_per_peak=10)                 # oversample: a peak has finite width ~1/T_span

best_period = 1 / freq[np.argmax(power)]

# FAP = P(noise produces a peak this high anywhere on the grid). It is GRID-DEPENDENT
# (rises with wider range / more oversampling), so always report the grid.
fap = ls.false_alarm_probability(power.max(), method='baluev')   # analytic, fast, screen-safe
levels = ls.false_alarm_level([0.1, 0.05, 0.01], method='baluev')
# method='bootstrap' (method_kwds={'n_bootstraps': 1000}) is most faithful but ~1000x cost
```

### Frequency-grid design (where peaks get missed)

The grid is not cosmetic: a bad grid silently loses signals.
- Minimum frequency comes from the record length: a period longer than ~the span cannot be claimed. Require >=2 full cycles (`f_min ~ 1/(T_span/2)`); 1 cycle cannot be told from a trend.
- Maximum frequency is a pseudo-Nyquist. There is no single Nyquist for irregular times; the average `1/(2*dt_mean)` is only a heuristic, and genuine unevenness permits probing far above it. Set `nyquist_factor` to a few, understanding it is a convention.
- Oversampling: a peak has finite width ~`1/T_span`; a grid coarser than a fraction of that steps over the true peak and under-reports its height and location. Use `samples_per_peak` 5-10 (astropy's `autopower` does this) rather than an ad-hoc `linspace(...,1000)`.
- Leakage / aliasing: gapped sampling has a window function that convolves the true spectrum, creating sidelobes and aliases at `1/(1/P +/- 1/P_sampling)`. Eyeball the window-function periodogram (LS of a constant signal at the same times) to see where sampling itself manufactures peaks.

## Autocorrelation (a sanity check, not an estimator)

**Goal:** Corroborate an LS-estimated period, not measure it.

**Approach:** Detrend, then look for a harmonic comb of ACF peaks at multiples of the period; treat a single band-crossing as weak evidence.

```python
from statsmodels.tsa.stattools import acf

# statsmodels assumes EVEN sampling and takes NO time vector -> invalid on the
# uneven data that motivates this skill. Detrend first: a trend gives a slowly
# decaying ACF that mimics periodicity.
vals_dt = values_even - np.polyval(np.polyfit(np.arange(len(values_even)), values_even, 1), np.arange(len(values_even)))
acf_vals, confint = acf(vals_dt, nlags=len(vals_dt) // 2, alpha=0.05)   # index 0 is lag-0 = 1.0
```

ACF is a WEAK period estimator: its resolution is quantized to the sampling step (period only to +/- one step), it requires even sampling, and trends fool it. A periodic signal repeats at lags `P, 2P, 3P`; the partial ACF (PACF) helps isolate the fundamental from harmonic echoes. Use it as a robustness box after detrending, never as the primary estimate.

## Wavelet CWT (transient / time-varying periodicity)

Global LS/Welch report one spectrum for the whole record and blur a signal that oscillates only early (cell-cycle synchrony decaying as cells desynchronize) or shifts period after a stimulus. The CWT resolves power in the time x period plane, at the cost of lower frequency precision and edge artifacts.

**Goal:** Map how the dominant period changes over time and mark which of that map is trustworthy and significant.

**Approach:** Transform with a complex Morlet, mask the cone of influence (edge artifacts), and test power against a Torrence-Compo AR(1) red-noise background rather than an ad-hoc `mean + 2*SD`.

```python
import pywt
import numpy as np
from scipy.stats import chi2

# Complex Morlet 'cmorB-C' (bandwidth B, center freq C): complex -> amplitude AND phase.
wavelet = 'cmor1.5-1.0'
C = pywt.central_frequency(wavelet)        # 1.0 for cmor1.5-1.0
dt = times[1] - times[0]                    # requires even sampling
periods_to_test = np.arange(6, 49, 0.5)
scales = C * periods_to_test / dt           # scale = C * period / dt ; verify below
# sanity: pywt.scale2frequency(wavelet, scales) / dt  ->  1/periods_to_test

# Pass sampling_period, else returned freqs are in per-sample units (period axis off by dt).
coeffs, freqs = pywt.cwt(signal, scales, wavelet, sampling_period=dt)
power = np.abs(coeffs) ** 2                  # power = |coefficients|^2
```

### Cone of influence (COI) - mask edge artifacts BEFORE reading ridges

Near each end of a finite record a wavelet overlaps the edge and its coefficients are computed against padding - edge artifacts, not signal. The COI widens for LONGER periods (larger scales reach farther from the edge). For the Morlet the e-folding half-width is ~`sqrt(2)*scale` in time; since `period = scale*dt/C` and C=1, a period is inside the COI (unreliable) where `sqrt(2)*period > distance-to-nearest-edge`. Grey out / mask the two triangular corners before ridge extraction or peak reading. Claiming a long-period oscillation that lives only in the first/last fraction of the record, inside the COI, is a classic false positive.

```python
n = len(signal)
edge_dist = np.minimum(np.arange(n), np.arange(n)[::-1]) * dt   # time to nearest edge
coi_max_period = edge_dist / np.sqrt(2)                          # longest reliable period per time
inside_coi = periods_to_test[:, None] > coi_max_period[None, :]
power_masked = np.where(inside_coi, np.nan, power)               # ignore masked cells downstream
```

### Red-noise significance (Torrence & Compo 1998), NOT mean + 2*SD

`mean(power) + 2*SD(power)` is indefensible: wavelet power under noise is not Gaussian and its variance changes with scale. Model the null as red noise - an AR(1) process with lag-1 autocorrelation `alpha` estimated from the data (white noise, alpha=0, is too permissive for intrinsically red / 1/f omics). The theoretical background is `P_k = (1-alpha^2)/(1 - 2*alpha*cos(2*pi*dt/period) + alpha^2)`; local power normalized by this background is chi-square with 2 dof (complex wavelet), so the 95% contour is `(noise level) * P_k * chi2(0.95, 2)/2`. Peaks poking through it are significant. Report the `alpha` assumed. pywt's Morlet power is not in variance units, so calibrate one wavelet constant `k` from the ROBUST (median) noise level of the scalogram - the median is dominated by noise cells, so it estimates the white-noise power per unit variance without the strong signal cells inflating it.

```python
alpha = np.corrcoef(signal[:-1], signal[1:])[0, 1]   # lag-1 autocorrelation
variance = signal.var(ddof=1)
Pk = (1 - alpha**2) / (1 - 2*alpha*np.cos(2*np.pi*dt/periods_to_test) + alpha**2)
k = np.nanmedian(power_masked / (variance * Pk[:, None]))   # robust wavelet power constant
sig95 = variance * Pk * k * chi2.ppf(0.95, df=2) / 2 # per-period 95% level, 2 dof
significant = power_masked > sig95[:, None]          # inside COI is NaN -> False
```

### Ridge extraction

Track `argmax` over scale at each time for the instantaneous dominant period, but only AFTER masking the COI and only for points above the red-noise contour; enforce continuity (a real ridge does not teleport between distant periods sample-to-sample). The global wavelet spectrum (time-average of power) is the wavelet analogue of a Fourier/LS spectrum, with its own chi-square test at reduced dof.

## Welch PSD (evenly sampled only)

```python
from scipy.signal import welch

# nperseg is the bias/variance knob: longer segments -> finer frequency resolution but
# fewer segments -> noisier PSD; shorter -> smoother but cannot resolve close/long periods.
# n//2 is a middling, defensible-but-arbitrary compromise; you cannot see a period longer
# than one segment. Welch CANNOT handle gaps -> feeding it interpolated data reintroduces
# interpolation bias. Even sampling only; otherwise use Lomb-Scargle.
freqs_w, psd = welch(values_even, fs=1/dt, nperseg=len(values_even)//2, detrend='constant')
periods_w = 1 / freqs_w[1:]
```

## Genome-Wide Screening

**Goal:** Turn per-gene FAPs into a genome-wide error rate without inflating the hit list with harmonics or trends.

**Approach:** Compute one FAP per gene, control FDR across genes, and guard against harmonic contamination and non-white noise.

```python
from statsmodels.stats.multitest import multipletests

# FAP is per-gene: thresholding 15,000 genes at FAP<0.01 yields ~150 false positives.
# Convert per-gene FAPs to q-values with Benjamini-Hochberg (assumes independence /
# positive dependence; gene-gene correlation makes it mildly conservative).
reject, qvals, _, _ = multipletests(fap_per_gene, method='fdr_bh')
n_periodic = int((qvals < 0.05).sum())
```

Screening subtleties:
- Harmonic contamination: a non-sinusoidal 24 h oscillation has real power at 12 h, 8 h, 6 h. The 12 h peak is a genuine harmonic, NOT an independent 12 h rhythm. A naive screen reports a phantom cohort of 12 h genes. Guard: check whether a putative P/2 peak co-occurs with a stronger peak at P; fit the fundamental plus harmonics jointly with astropy `LombScargle(t, y, nterms=k)` and attribute power correctly; distrust exact 2:1 period ratios.
- Permutation null validity: shuffling values across the fixed times destroys ALL temporal structure -> the null becomes WHITE noise. That is correct only if the alternative is "periodicity vs i.i.d. noise." Real omics noise is autocorrelated / red (1/f): a gene with a smooth trend or slow drift beats a white null and is falsely flagged periodic. On un-detrended, autocorrelated data a shuffle test is ANTI-CONSERVATIVE. Fixes: detrend first; use an AR(1) surrogate / block-bootstrap null that preserves short-range autocorrelation; or use the analytic Baluev FAP. State which null was used and what alternative it implies.
- Fisher's g-test (Wichert, Fokianos & Strimmer 2004): for EVENLY sampled series, g = (max periodogram ordinate)/(sum of ordinates) has a known exact distribution under the white-noise null, giving an exact per-gene p with no simulation - the canonical microarray cell-cycle screen. Even sampling only; shares the white-null limitation.
- Interpolate-then-FFT biases the spectrum red; never interpolate uneven data to run an even-sampling screen - use LS/GLS directly.
- Genuine oscillation vs 1/f vs trend: a real oscillation is a NARROW peak riding above the smooth 1/f background and recurring at harmonics; 1/f humps are broad and non-harmonic; a trend is indistinguishable from a very long period over <2 cycles. Require >=2-3 cycles, detrend, and test against a colored (AR(1)) null, not white.

## Common Errors

| Trap | Why it is wrong | Fix |
|------|-----------------|-----|
| Raw (nonzero-mean) values into `scipy.signal.lombscargle` | Classic LS assumes zero mean; the offset leaks into the sinusoid -> inflated power | `floating_mean=True` (GLS) OR pass `y - y.mean()`; `precenter` deprecated in 1.17 |
| Ordinary frequency (1/period) in scipy | scipy takes ANGULAR omega=2*pi/period; period off by 2*pi | `angular = 2*np.pi/periods`; use astropy for ordinary-frequency grids |
| Pre-centering then handing to astropy | astropy already fits the mean (`fit_mean=True`) -> redundant / conceptual muddle | Pass RAW values to astropy; it is GLS by default |
| Ad-hoc `np.linspace(f_min,f_max,1000)` grid | Too-coarse spacing steps over the finite-width peak | `autopower(samples_per_peak=5..10)` or space finer than `~1/T_span` |
| Reporting FAP without the grid | FAP grows with grid width / oversampling; numbers not comparable | Always report `[f_min,f_max]` and `samples_per_peak` |
| Interpolate-then-FFT/Welch on uneven data | Interpolation is a low-pass filter -> spurious red power, killed high-freq signal | Analyze the uneven series directly with LS/GLS |
| Wavelet scalogram with no COI mask | Edge coefficients are artifacts against padding; worse at long periods | Compute the COI (Morlet half-width `sqrt(2)*scale`), grey it out |
| `mean + 2*SD` wavelet significance | Wavelet power is not Gaussian; variance varies with scale | Torrence-Compo AR(1) background x chi2(0.95,2)/2 contour; report alpha |
| Shuffle-time permutation on un-detrended data | White null; a trend / red-noise gene beats it -> false "periodic" | Detrend first, or AR(1)/block-bootstrap surrogate, or Baluev FAP |
| ACF as the period estimator | Poor resolution; assumes even sampling; trend-fooled | Use ACF only as a corroborating check after detrending |
| Treating the 12 h (P/2) peak as an independent rhythm | It is the harmonic of a non-sinusoidal 24 h signal | Check co-occurrence with a stronger peak at P; fit `nterms>1` |
| Claiming a period longer than the record | <2 cycles cannot separate oscillation from trend | Require >=2 (ideally 3) cycles; cap `max_period <= T_span/2` |
| Assuming 24 h for cell cycle | Cell-cycle period is cell-type / condition dependent, usually != 24 h | Estimate the period; use circadian-rhythms only when 24 h is the hypothesis |

## References

- Lomb 1976. Least-squares frequency analysis of unequally spaced data. Astrophys Space Sci 39(2):447-462.
- Scargle 1982. Studies in astronomical time series analysis. II. Statistical aspects of spectral analysis of unevenly spaced data. Astrophys J 263:835-853.
- VanderPlas 2018. Understanding the Lomb-Scargle Periodogram. Astrophys J Suppl Ser 236(1):16.
- Baluev 2008. Assessing the statistical significance of periodogram peaks. Mon Not R Astron Soc 385(3):1279-1285.
- Torrence & Compo 1998. A Practical Guide to Wavelet Analysis. Bull Amer Meteor Soc 79(1):61-78.
- Wichert, Fokianos & Strimmer 2004. Identifying periodically expressed transcripts in microarray time series data. Bioinformatics 20(1):5-20.

## Related Skills

temporal-genomics/circadian-rhythms - Known-period (24 h) rhythm testing with cosinor and JTK_CYCLE
temporal-genomics/temporal-clustering - Group genes by periodicity characteristics
temporal-genomics/trajectory-modeling - Non-periodic trajectory fitting with GAMs
<!-- END FILE: temporal-genomics/periodicity-detection/SKILL.md -->

## 子目录：temporal-genomics/temporal-clustering

<!-- BEGIN FILE: temporal-genomics/temporal-clustering/SKILL.md -->
---
name: bio-temporal-genomics-temporal-clustering
description: Clusters temporally variable genes by expression-profile SHAPE (not significance) using Mfuzz fuzzy c-means, TCseq, DEGreport degPatterns, and tslearn DTW/soft-DTW. Use when grouping pre-selected time-course genes into shared trajectory programs (co-expression modules), choosing between soft vs hard clustering, picking k, selecting a distance metric (Euclidean/correlation/DTW), or interpreting clusters with per-cluster enrichment. Requires temporally variable genes selected FIRST (differential-expression/timeseries-de or a variance filter); clustering is descriptive and downstream of selection, never a test of which genes are dynamic.
tool_type: mixed
primary_tool: Mfuzz
---

## Version Compatibility

Reference examples tested with: Mfuzz 2.64+, TCseq 1.14+, DEGreport 1.30+ (R/Bioconductor); tslearn 0.8+, scikit-learn 1.4+ (Python).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show tslearn scikit-learn` then `help(module.function)` to check signatures
- R: `packageVersion('Mfuzz')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Temporal Gene Clustering

**"Group my time-course genes by expression pattern shape"** -> Partition PRE-SELECTED temporally variable genes into co-expression modules by trajectory shape (fuzzy c-means, hierarchical, or DTW), producing candidate temporal programs.
- R: `Mfuzz::mfuzz()` (fuzzy/soft), `TCseq::timeclust()`, `DEGreport::degPatterns()`
- Python: `tslearn.clustering.TimeSeriesKMeans` (Euclidean / DTW / soft-DTW)

## Governing Principle - read before clustering anything

Clustering answers only "which genes share a temporal SHAPE." It is DESCRIPTIVE and UNSUPERVISED: it has no null model, no p-value, and no notion of a "true" cluster count, so it ALWAYS returns clusters from whatever it is handed. It is strictly DOWNSTREAM of gene selection.

- It does NOT answer "which genes are rhythmic" (that is temporal-genomics/circadian-rhythms) and does NOT answer "is this gene significantly changing" (that is differential-expression/timeseries-de: LRT, spline-DE, maSigPro). Clustering adds description, not inference.
- The input MUST already be the temporally variable genes - the output of timeseries-DE or, at minimum, a variance filter. Never the full expression matrix.
- **Feeding in flat/all genes is the #1 error.** Per-gene z-scoring (mandatory, below) rescales a flat gene's pure noise to unit variance, so it lands in a "cluster" of noise that mimics a real program. Z-scoring erases the one signal (near-zero variance) that flagged the gene as flat, which is exactly why prefiltering is a gate, not optional hygiene.
- Clusters are HYPOTHESES. A centroid is a candidate program; membership is not evidence a gene is regulated - that evidence came (or did not) from the upstream DE step.

If a user asks "cluster my RNA-seq time course," the first question is always: have these genes already been selected for temporal change, and how? If the answer is "no, it is all 20,000 genes," stop and prefilter.

## Core Workflow

1. Confirm the input is pre-selected temporally variable genes (DE hits or top-variance); if not, prefilter
2. Standardize each gene's profile (z-score across timepoints) - mandatory
3. Choose a distance metric (Euclidean-on-zscore / correlation / DTW), then an algorithm and k
4. Assign genes to clusters (soft membership or hard labels); filter by membership if fuzzy
5. Validate by stability (bootstrap/consensus), then interpret centroids and run per-cluster enrichment with the correct background

## Soft vs Hard, and Why Standardization Is Mandatory

**Soft (fuzzy) clustering is preferred for expression.** Genes participate in multiple regulatory programs, so forcing one gene into one cluster (hard k-means) is biologically false at boundaries and brittle: a gene between two centroids flips clusters under trivial noise. Futschik & Carlisle (2005) established fuzzy c-means as noise-ROBUST for expression time courses - low-membership (ambiguous, likely-noise) genes are down-weighted in centroid estimation, so centroids track the high-confidence core of each program, and ambiguity is exposed as a continuous membership score to threshold rather than hidden inside a hard label.

**Z-score per gene is mandatory** (Mfuzz `standardise()`, TCseq `standardize=TRUE`, tslearn `TimeSeriesScalerMeanVariance()`). Without it, MAGNITUDE dominates SHAPE: a high-abundance housekeeping gene sits far (Euclidean) from a low-abundance gene of identical shape, while two high-abundance genes co-cluster on abundance alone. Clustering-by-shape requires removing each gene's mean and scaling to unit variance across timepoints.

## Mfuzz (R/Bioconductor)

**Goal:** Group temporally variable genes into soft co-expression clusters by trajectory shape.

**Approach:** Build an ExpressionSet, gate out flat genes (`filter.std`), z-score (`standardise`), estimate then VALIDATE the fuzzifier, run fuzzy c-means, and filter genes by membership. Mfuzz wraps `e1071::cmeans` (it does not implement its own optimizer); distance is Euclidean on z-scored profiles.

### Setup and Preprocessing

```r
library(Mfuzz)
library(Biobase)

# Rows = genes (already selected as temporally variable), columns = timepoints (mean across replicates)
expr_mat <- as.matrix(read.csv('temporal_expression.csv', row.names = 1))
eset <- ExpressionSet(assayData = expr_mat)

# filter.std: flat-gene GATE (keeps the governing principle true). min.std=0.5 is a starting
# point; inspect the SD distribution and set it above the flat-gene noise floor for your data.
eset <- filter.std(eset, min.std = 0.5)

# Per-gene mean 0, sd 1 across timepoints (British spelling; no 'standardize' alias)
eset <- standardise(eset)
```

### Fuzzifier Estimation - inspect, do not trust blindly

**Goal:** Pick a fuzzifier `m` that keeps clusters informative for THIS number of timepoints.

**Approach:** `mestimate()` implements Schwaemmle & Jensen (2010): it returns the smallest `m` that stops fuzzy c-means from finding tight clusters in RANDOMIZED data. The estimate is dominated by D (number of timepoints) via a D^-2 term, so it can go degenerate at the extremes - inspect the returned `m` AND the membership distribution rather than trusting either the estimate or the historical `m=2` default.

```r
# With FEW timepoints (small D), mestimate pushes m HIGH -> over-fuzzy: memberships flatten
# toward 1/c and an acore(0.5) filter can discard nearly everything.
# With MANY timepoints (large D), m falls toward ~1.05-1.2 -> near-hard, soft advantage evaporates.
m <- mestimate(eset)
cat(sprintf('Estimated fuzzifier m: %.2f\n', m))

cl <- mfuzz(eset, c = 8, m = m)  # c=8: starting point for 6-12 timepoints; refine below

# VALIDATE m: what fraction of genes clears the alpha-core cutoff? If very few do, m is too high.
max_mem <- apply(cl$membership, 1, max)
cat(sprintf('Genes with max membership >= 0.5: %.0f%%\n', 100 * mean(max_mem >= 0.5)))
# Sanity check the estimate's own criterion: cluster a permuted copy; it should NOT form tight clusters.
```

### Membership Filtering and Cluster Selection

```r
# acore returns, per cluster, genes with MAX membership >= min.acore ("alpha cores").
# 0.5 is a convention; it discards a data-dependent fraction (larger m -> more discarded).
# Relaxing to 0.3 is legitimate for exploratory work but admits more noise. Always report the retained fraction.
core_genes <- acore(eset, cl, min.acore = 0.5)

# Minimum centroid distance vs k: as k grows the closest centroid pair collapses; a knee hints at
# over-splitting. This is a WEAK, monotone-ish signal, not an oracle -- triangulate with stability (below).
min_dist <- sapply(4:20, function(k) {
    d <- as.matrix(dist(mfuzz(eset, c = k, m = m)$centers))
    diag(d) <- Inf
    min(d)
})
plot(4:20, min_dist, type = 'b', xlab = 'k', ylab = 'Min centroid distance')
```

### Visualization

```r
mfuzz.plot2(eset, cl, mfrow = c(2, 4), time.labels = colnames(expr_mat), centre = TRUE, x11 = FALSE)
overlap.plot(cl, over = overlap(cl), thres = 0.05)  # centroid-overlap view; merges hint at over-clustering
```

## TCseq (R/Bioconductor)

TCseq was built for time-course SEQUENCING (RNA-seq/ATAC-seq); upstream DE/peak steps live in the same package, and `timeclust` clusters the summarized (per-gene, per-timepoint) matrix.

```r
library(TCseq)

# algo='cm': fuzzy c-means (soft, Mfuzz-like). Also 'km' (hard k-means), 'pam', 'hc' (hierarchical).
# standardize=TRUE does the mandatory per-gene z-score.
tc <- timeclust(expr_mat, algo = 'cm', k = 6, standardize = TRUE)
timeclustplot(tc, value = 'z-score', cols = 3)

tc_km <- timeclust(expr_mat, algo = 'km', k = 6, standardize = TRUE)  # hard alternative
```

## DEGreport degPatterns (R)

**Goal:** Hierarchical clustering with automatic k and design-aware grouping.

**Approach:** `degPatterns` takes replicate-level data plus metadata, collapses samples within each (time, col) group to a MEAN internally, then clusters on correlation distance and cuts the tree. Convenient, but "auto k" is really "cut + merge under `minc`," a heuristic - not an optimum.

```r
library(DEGreport)

# time, col: COLUMN NAMES in metadata (col defaults to NULL). minc=15: minimum cluster size;
# clusters smaller than minc are DROPPED -- this both blocks singletons AND silently discards genes,
# so it can yield fewer clusters than the tree suggested. Set deliberately.
patterns <- degPatterns(expr_mat, metadata = sample_info, time = 'timepoint', col = 'condition', minc = 15)

cluster_df <- patterns$df                     # gene -> cluster assignments
degPlotCluster(patterns$normalized, time = 'timepoint', color = 'condition')  # note: 'color', not 'col'
```

## tslearn (Python) - Euclidean / DTW / soft-DTW

**Goal:** Cluster time-series profiles, optionally warping the time axis for phase-shifted genes.

**Approach:** Z-score, then `TimeSeriesKMeans`. The DISTANCE METRIC matters more than the algorithm - default to Euclidean-on-zscore (which, after standardization, is monotone in Pearson correlation and captures "same shape, different amplitude"). Escalate to DTW ONLY for real, expected phase shifts, and ALWAYS constrain it.

```python
import numpy as np
from tslearn.clustering import TimeSeriesKMeans, silhouette_score
from tslearn.preprocessing import TimeSeriesScalerMeanVariance

# expr_mat: (n_genes, n_timepoints) of PRE-SELECTED temporally variable genes
expr_scaled = TimeSeriesScalerMeanVariance().fit_transform(expr_mat[:, :, np.newaxis])

# Default, safe choice: Euclidean on z-scored profiles (phase-SENSITIVE, cheap, no fabricated structure)
model = TimeSeriesKMeans(n_clusters=8, metric='euclidean', max_iter=50, random_state=42)
labels = model.fit_predict(expr_scaled)
```

### DTW - powerful for phase shifts, but constrain the band or it invents structure

DTW (Sakoe & Chiba 1978) warps the time axis so a profile peaking one timepoint later can still match - the ONLY reason to reach for it (signaling cascades, developmental heterochrony, unequal sampling). Its default failure mode is the SINGULARITY: unconstrained DTW maps one point of series A onto a long run of points of series B, manufacturing apparent co-regulation from noise. tslearn's default `global_constraint=None` is exactly this singularity-prone configuration.

```python
# The Sakoe-Chiba BAND caps how far in time a point may be matched -- kills most singularities AND
# cuts cost. This constraint is mandatory, not optional, for DTW clustering.
# sakoe_chiba_radius: warping-window half-width in timepoints; small (1-2) for tight sampling.
model = TimeSeriesKMeans(
    n_clusters=8, metric='dtw',
    metric_params={'global_constraint': 'sakoe_chiba', 'sakoe_chiba_radius': 2},
    max_iter=50, random_state=42)
labels = model.fit_predict(expr_scaled)

# Soft-DTW: replaces DTW's hard min with a soft-min -> DIFFERENTIABLE loss, enabling proper
# soft-DTW barycenters (cluster centers). It is NOT "faster" -- still quadratic; use it for smooth,
# well-defined averaging, not speed. gamma via metric_params (NOT the deprecated gamma_sdtw kwarg).
soft = TimeSeriesKMeans(n_clusters=8, metric='softdtw', metric_params={'gamma': 0.5},
                        max_iter=50, random_state=42)
```

**When DTW is worth it:** only when phase shift is real and expected, the band is set, AND DTW has been checked against fabricating structure. On data with NO phase shifts, DTW should not beat Euclidean - if it "finds more clusters" there, that is invented structure, not signal.

### Selecting k - score under the SAME geometry that formed the clusters

```python
# Scoring DTW clusters with a EUCLIDEAN silhouette is geometrically inconsistent: clusters were
# formed under DTW geometry but ranked under Euclidean, which can pick a DIFFERENT (wrong) k.
# tslearn.clustering.silhouette_score takes metric='dtw'/'softdtw' and precomputes the matching
# distances internally -- score under the SAME geometry that formed the clusters.
dtw_params = {'global_constraint': 'sakoe_chiba', 'sakoe_chiba_radius': 2}
scores = {}
for k in range(3, 11):
    km = TimeSeriesKMeans(n_clusters=k, metric='dtw', metric_params=dtw_params, max_iter=30, random_state=42)
    labels_k = km.fit_predict(expr_scaled)
    scores[k] = silhouette_score(expr_scaled, labels_k, metric='dtw', metric_params=dtw_params)
best_k = max(scores, key=scores.get)
```

Under a pure-Euclidean pipeline, `sklearn.metrics.silhouette_score(expr_scaled.squeeze(), labels)` is consistent and fast. It is only the DTW/Euclidean MISMATCH that mis-ranks k.

## Choosing k - the honest story

No index is authoritative; triangulate and let biology and stability decide.

| Signal | What it says | Caveat |
|---|---|---|
| Min centroid distance / Dmin | knee where centroids start collapsing = over-splitting | weak, monotone-ish |
| Silhouette | within- vs nearest-other-cluster separation | must match the clustering metric (DTW vs Euclidean) |
| Within-cluster dispersion / elbow / gap | dispersion drop-off | elbow subjective; gap assumes a null reference, expensive |
| Biology heuristic | does +1 cluster split a coherent program or resolve two real shapes? | the honest arbiter |
| **Stability (bootstrap/consensus)** | do the same genes co-cluster under resampling? | **the real validation, not a lone index** |

Over-clustering FRAGMENTS one real program across centroids (the same GO terms then reappear in three clusters); under-clustering MERGES distinct programs into an averaged centroid matching no gene. Report a stable partition, not a single silhouette peak.

## Distance Metric - it dominates the algorithm choice

| Metric | Captures | Phase shifts | Cost | Use when |
|---|---|---|---|---|
| Euclidean on z-score | shape + amplitude (monotone in Pearson after z-score) | NO | cheap | default for aligned timepoints |
| Correlation (DEGreport) | shape, amplitude-invariant | NO | cheap | shape-only focus |
| DTW (constrained) | shape with time warping | YES | O(n·T^2)/pair, worse for clustering | genuine, expected phase shifts only |

## The Circularity / Double-Dipping Trap

Selecting genes by a temporal criterion, clustering them, then TESTING those clusters for the same temporal signal is circular and inflates everything. If genes were selected for temporal variability, a follow-up test asking "are these clusters temporally structured / rhythmic?" is guaranteed to say yes - the signal was baked in at selection (Kriegeskorte-style non-independence). Interpreting per-cluster centroid p-values after DE selection is the same error: the genes are already significant by construction. Selection -> clustering is fine as a DESCRIPTIVE pipeline; what is not permissible is a test on the same data whose null was already violated by selection. Test clusters only against INDEPENDENT annotations (GO, TF targets, a held-out condition), never the temporal criterion used to select.

## Per-Cluster Enrichment - the background-set trap

Run GO/GSEA per cluster to name programs, but the enrichment BACKGROUND (universe) must be the INPUT gene set that was clustered (the temporally variable genes), NOT the whole genome. Genome-as-background makes every cluster light up for the generic biology of "being a dynamic/expressed gene" (translation, stress, cell cycle) - that signal comes from the SELECTION step, not the cluster, and re-tests what was already done (mirrors the circularity trap). Testing cluster-vs-(rest-of-input) isolates what makes THIS shape distinct.

## Replicate Handling

The examples cluster on replicate-AVERAGED profiles (standard and simple), but averaging DISCARDS uncertainty the DE step had: two genes with identical means but very different within-timepoint variance are treated as equally reliable. `degPatterns` makes the collapse explicit (mean within each time/col group) but still computes similarity on group means. The rigorous-but-rare alternative is a variance-aware/weighted distance; at minimum, state that averaging is a known limitation.

## Method Comparison

| Method | Clustering | Distance | Best for |
|--------|-----------|----------|----------|
| Mfuzz | Soft (fuzzy c-means) | Euclidean on z-score | standard soft temporal profiling |
| TCseq | Soft (`cm`) or hard (`km`/`pam`/`hc`) | Euclidean on z-score | RNA-seq/ATAC time courses |
| DEGreport | Hierarchical, auto-k | Correlation | design-aware, quick auto-k |
| tslearn | Hard k-means | Euclidean / DTW / soft-DTW | phase-shifted profiles (constrained DTW) |

## Common Errors

| Trap | Why it is wrong | Fix |
|---|---|---|
| Clustering ALL genes (incl. flat) | no null -> always returns clusters; z-score amplifies flat-gene noise into fake programs | prefilter to timeseries-DE hits or `filter.std`/top-variance FIRST |
| Skipping z-score | magnitude dominates shape; abundance clusters, not dynamics | `standardise()` / `standardize=TRUE` / `TimeSeriesScalerMeanVariance()` |
| Hardcoding `m=2` or trusting `mestimate()` blindly | m=2 over-fuzzy for many timepoints; mestimate degenerates at extreme D | inspect returned m + membership fraction; check it does not cluster randomized data |
| Treating k as having a "true" value | indices disagree; clustering has no true count | triangulate indices + biology + bootstrap stability |
| Unconstrained DTW | singularities invent structure from noise | set `global_constraint='sakoe_chiba'`; use DTW only for real phase shifts |
| "soft-DTW is just faster DTW" | still quadratic; its value is differentiability/barycenters | use soft-DTW for smooth averaging, not speed |
| Euclidean silhouette to pick k for DTW clusters | scores a different geometry than formed the clusters -> mis-ranks k | `tslearn.clustering.silhouette_score(..., metric='dtw')`, or cluster Euclidean throughout |
| Testing clusters for the temporal signal selected on | circular / double-dipping; p-values inflated | test only INDEPENDENT annotations |
| GO enrichment vs whole-genome background | re-detects "being dynamic" from the selection step | background = the clustered input gene set |
| Reporting centroids as if genes follow them exactly | centroid is an average; membership/spread varies | report membership (acore) fraction + within-cluster spread |

## References

- Futschik ME, Carlisle B (2005). Noise-robust soft clustering of gene expression time-course data. J Bioinform Comput Biol 3(4):965-988. (Original noise-robustness rationale for fuzzy c-means on expression time courses.)
- Kumar L, Futschik ME (2007). Mfuzz: a software package for soft clustering of microarray data. Bioinformation 2(1):5-7.
- Schwaemmle V, Jensen ON (2010). A simple and fast method to determine the parameters for fuzzy c-means cluster analysis. Bioinformatics 26(22):2841-2848. (Implemented by `mestimate()`; fuzzifier depends on the number of timepoints.)
- Cuturi M, Blondel M (2017). Soft-DTW: a Differentiable Loss Function for Time-Series. PMLR 70:894-903. (Differentiable soft-min smoothing of DTW; gamma controls smoothing.)
- Sakoe H, Chiba S (1978). Dynamic programming algorithm optimization for spoken word recognition. IEEE Trans Acoust Speech Signal Process 26(1):43-49. (Foundational DTW and the Sakoe-Chiba warping-window band.)
- Bezdek JC (1981). Pattern Recognition with Fuzzy Objective Function Algorithms. Plenum Press, New York. (Foundational fuzzy c-means and the fuzzifier m.)

## Related Skills

- circadian-rhythms - Rhythm detection by phase (answers "which genes are rhythmic", not shape clustering)
- trajectory-modeling - Continuous trajectory fitting before clustering
- differential-expression/timeseries-de - Upstream temporal DE that selects the genes to cluster
- pathway-analysis/go-enrichment - Per-cluster functional enrichment (use the input gene set as background)
<!-- END FILE: temporal-genomics/temporal-clustering/SKILL.md -->

## 子目录：temporal-genomics/temporal-grn

<!-- BEGIN FILE: temporal-genomics/temporal-grn/SKILL.md -->
---
name: bio-temporal-genomics-temporal-grn
description: Infers directed, time-delayed gene regulatory edges from BULK time-series expression using Granger causality (statsmodels VAR F-test), dynGENIE3 (tree ensembles regressing ODE-derived derivatives; Random Forests by default, Extra-Trees optional), and dynamic Bayesian networks (bnlearn). Use when the output is a RANKED HYPOTHESIS list for perturbation validation, not validated causal edges; deciding Granger vs dynGENIE3 vs DBN by timepoint count and linearity; sizing maxlag against the n>3*maxlag+1 degrees-of-freedom floor; handling stationarity/differencing before Granger; restricting regulators to known TFs; and comparing network rewiring across conditions at matched edge density. Not for single-cell pseudotime GRNs (see gene-regulatory-networks/scenic-regulons) or static co-expression (see gene-regulatory-networks/coexpression-networks).
tool_type: mixed
primary_tool: statsmodels
---

## Version Compatibility

Reference examples tested with: statsmodels 0.14+, numpy 1.26+, pandas 2.2+, dynGENIE3 (GitHub vahuynh/dynGENIE3), bnlearn 4.9+, R 4.x

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: bulk time-series GRN inference is low-precision and assumption-heavy. Every edge is a HYPOTHESIS. Results are dominated by the sampling design (interval vs the minutes-scale of transcription, number of timepoints, replicate count), not by the algorithm. A tiny p-value from 6-12 timepoints is not evidence of regulation.

# Temporal Gene Regulatory Network Inference

**"Infer causal regulatory relationships from my time-series expression data"** -> Rank directed, time-delayed TF->target edges from bulk temporal expression, to prioritize perturbation experiments.
- Python: `statsmodels.tsa.stattools.grangercausalitytests()` (VAR F-test on predictive precedence)
- R: `dynGENIE3::dynGENIE3()` (tree ensembles on ODE-derived derivatives); `bnlearn::hc()` + `boot.strength()` (dynamic Bayesian network)

## The governing principle: inference produces ranked HYPOTHESES, not validated causal edges

Bulk temporal GRN inference turns a time course into a ranked list of candidate directed edges whose only honest downstream use is prioritizing perturbation experiments (knockdown / overexpression + re-measure). Two hard facts set the ceiling and must be stated up front, not buried.

1. Granger is PREDICTIVE precedence, not mechanism. It tests whether past X improves prediction of future Y, which is neither necessary nor sufficient for regulation. It collapses in three routine biological situations:
   - Unobserved common driver (confounding). An unmeasured TF, or a shared circadian/cell-cycle oscillation driving hundreds of genes, makes X "Granger-cause" Y with zero direct regulation. Pairwise methods are structurally blind to this; a shared sinusoid manufactures dense, entirely spurious directed structure whose lags are just phase offsets.
   - Sampling coarser than the regulation timescale (aliasing). Transcription acts in minutes; bulk courses are sampled every 1-6 h. When the interval exceeds the regulatory delay, cause and effect land in the same sampled timepoint and directionality becomes unidentifiable. No statistic recovers information the sampling threw away.
   - Non-stationarity. VAR-Granger assumes weak stationarity, but the interesting biology (a stimulus response, a developmental transient, a monotone induction) IS the non-stationary trend, and differencing it away removes the signal (see the differencing dilemma below).
2. Community benchmarks put a LOW ceiling on precision and no single method wins. DREAM5 (Marbach 2012 *Nat Methods* 9:796) evaluated 30+ methods and found time-series network inference is low-precision, no method is best across datasets, and the robust win is the "wisdom of crowds": integrating independent methods beats any one. Prior information (restricting regulators to known TFs) is the other reliable lever.

Operational consequence: restrict regulators to annotated TFs, run more than one method, keep edges recovered by >=2 methods and stable across replicate series, match density before comparing conditions, and hand the top edges to perturbation. This skill is bounded to BULK real-clock-time data; single-cell pseudotime GRN is a different problem (gene-regulatory-networks/scenic-regulons).

## Method selection

| Method | Models | Best when | Fails when |
|--------|--------|-----------|------------|
| Granger (statsmodels) | Bivariate VAR; F-test restricted vs unrestricted | Enough timepoints (n comfortably > 3*maxlag+1); a small a-priori TF->target set; roughly linear, stationary-after-differencing series | 6-12 timepoints (no residual DoF -> no power); genome-wide pairwise (confounding + O(TF*target) tests); saturating/switch-like regulation (linear only) |
| dynGENIE3 (R) | Semi-ODE: trees regress dx/dt on regulator expression | Non-linear / combinatorial regulation; multiple replicates and reasonably dense sampling; a curated regulator list | Sparse or unevenly-spaced timepoints (finite-difference derivative is garbage); calibrated significance is required (it gives a RANKING, no p-values) |
| DBN (bnlearn) | Unrolled first-order Markov Bayesian network across slices | Feedback loops matter (autoregulation, negative feedback); a pre-filtered set of tens-to-low-hundreds of nodes; edge-confidence needed | Genome-wide (super-exponential DAG search); delays longer than one sampling interval (first-order Markov); tiny samples (CI/score tests underpowered) |

Methodology evolves; verify current best practice against each tool's latest documentation before committing to one. The defensible default is to run more than one and intersect.

## Granger causality (Python / statsmodels)

**Goal:** Rank TF->target pairs by whether past TF expression improves prediction of future target expression, with honest multiple-testing control.

**Approach:** Difference all genes uniformly to approach stationarity, select a single lag per pair by BIC (so the reported p-value is not the best-of-several), run ONE F-test at that lag, then BH-correct across pairs. Test only TF->target pairs to shrink the family and encode the TF prior.

The F-test compares an unrestricted VAR (Y on its own lags AND X's lags) to a restricted model (Y on its own lags only); statsmodels reports it as `ssr_ftest`, matching R's `lmtest::grangertest`. Two constraints dominate:

- Degrees-of-freedom floor. After lagging, `n_eff = n - maxlag` rows fit `2*maxlag+1` parameters, so the test is only defined for `n > 3*maxlag + 1`, and barely-defined means no power. With n=8 and maxlag=2 the F-test has ~1 residual DoF: a coin flip. This, not compute, is why genome-wide pairwise Granger fails. Prefer maxlag=1 on short courses.
- Lag selection is itself a multiple test. Taking the minimum p-value over lags 1..maxlag and reporting it as a single test inflates significance. Fix by selecting one lag a priori, or by BIC (below), or by Bonferroni across lags before the across-pairs BH.

```python
import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.stats.multitest import multipletests

# expr_df: genes x timepoints DataFrame; columns MUST be in temporal order.
# Difference uniformly to approach stationarity. Uniform (not per-gene) differencing
# keeps every series on the same footing: mixing I(0) and differenced I(1) series in one
# VAR corrupts the F-test reference distribution. Cost: over-differencing already-stationary
# genes. The deeper tradeoff: differencing removes the trend that CARRIES the regulatory
# signal, so on short courses prefer maxlag=1 over aggressive differencing.
expr_diff = expr_df.diff(axis=1).iloc[:, 1:]

tf_genes = ['TF1', 'TF2', 'TF3']
target_genes = ['geneA', 'geneB', 'geneC']
maxlag = 1  # short courses have ~no DoF beyond lag 1 (need n > 3*maxlag+1)

def granger_pvalue(pair_data, maxlag):
    # column 0 = response Y (target), column 1 = predictor X (TF): tests X -> Y.
    # Select ONE lag by BIC, then run a SINGLE test at it -> avoids the min-p-over-lags
    # multiple test. Guard BIC=0 (no lag structure) up to 1.
    lag = max(1, int(VAR(pair_data).select_order(maxlag).bic))
    res = grangercausalitytests(pair_data, maxlag=[lag])  # list -> tests only this lag
    return res[lag][0]['ssr_ftest'][1], lag  # (p_value, lag)

records = []
for tf in tf_genes:
    for target in target_genes:
        if tf == target:
            continue
        pair = np.column_stack([expr_diff.loc[target].values, expr_diff.loc[tf].values])
        p, lag = granger_pvalue(pair, maxlag)
        records.append({'tf': tf, 'target': target, 'p_value': p, 'lag': lag})

results_df = pd.DataFrame(records)
# multipletests default is Holm-Sidak, NOT BH; force fdr_bh explicitly.
results_df['q_value'] = multipletests(results_df['p_value'], method='fdr_bh')[1]
significant = results_df[results_df['q_value'] < 0.05].sort_values('q_value')
```

Pairwise Granger cannot separate direct regulation from a chain X->Z->Y or a fork Z->{X,Y}. The correct fix is conditional (multivariate) Granger, conditioning on all other regulators' lags, but that explodes the parameter count and is infeasible at transcriptomic sample sizes. Label pairwise output as a CONFOUNDED candidate set, not direct interactions.

## dynGENIE3 (R)

**Goal:** Rank regulator->target edges non-linearly by how much a regulator's current expression predicts a target's temporal derivative.

**Approach:** dynGENIE3 models each gene as `dx_i/dt = f_i(x) - alpha_i * x_i`, estimates `dx_i/dt` by finite differences between consecutive timepoints, and trains a tree ensemble to regress that derivative-plus-decay target on candidate-regulator expression; summed variable importance becomes the edge weight.

```r
library(dynGENIE3)

# TS.data: list of genes x timepoints matrices (one per replicate/series).
# time.points: matching list of time vectors (real deltas -> handles uneven spacing).
expr_list <- list(as.matrix(expr_series1), as.matrix(expr_series2), as.matrix(expr_series3))
time_list <- list(c(0, 4, 8, 12, 24, 48), c(0, 4, 8, 12, 24, 48), c(0, 4, 8, 12, 24, 48))

# Restrict regulators to known TFs (AnimalTFDB / PlantTFDB). This helps TWICE: fewer
# features searched per split (faster) AND a non-TF can never be reported as a regulator
# (higher precision). Single highest-yield precision lever.
tf_indices <- which(rownames(expr_list[[1]]) %in% tf_names)

# tree.method DEFAULTS to 'RF' (Random Forests). Extra-Trees is opt-in: tree.method='ET'
# (the config GENIE3 used to win DREAM4). alpha='from.data' (default) estimates per-gene
# mRNA decay from the data; pass a numeric vector to inject measured half-lives (4sU/BRIC-seq).
res <- dynGENIE3(TS.data = expr_list, time.points = time_list, regulators = tf_indices)

# get.link.list (DOT form) is the dynGENIE3 function. The camelCase getLinkList belongs to
# the separate Bioconductor GENIE3 package -- do not swap them.
link_list <- get.link.list(res$weight.matrix, report.max = 1000)
```

Two properties gate interpretation:
- The weight matrix is a RANKING with no null, no p-value, no calibrated threshold. A "top edge" is top only relative to the others in this run; thresholding by rank (top-K) is unavoidably arbitrary. This is why cross-method agreement and stability matter more here than anywhere.
- Finite-difference derivatives amplify noise. With few, unevenly-spaced timepoints (0,4,8,12,24,48 h is typical) each `dx/dt` rests on one noisy pair and late wide intervals blur short-timescale regulation into a single slope. More REPLICATES (independent derivative samples averaging the noise down) help far more than adding one or two timepoints.

## Dynamic Bayesian networks (R / bnlearn)

**Goal:** Learn a directed network that can represent feedback, with bootstrap edge confidence, over a pre-filtered gene set.

**Approach:** Unroll time into t-1 and t slices and allow edges only from t-1 to t; because A_{t-1}->B_t and B_{t-1}->A_t both point forward, the unrolled graph is acyclic even though the biology has an A<->B feedback loop. So DBNs represent feedback that static Bayesian networks (which must be DAGs) structurally cannot -- the main reason to reach for one. The cost: it is first-order Markov (state at t depends only on t-1; longer delays need t-2/t-3 slices) and the super-exponential DAG search caps realistic inference at tens-to-low-hundreds of nodes, never genome-wide.

```r
library(bnlearn)

# Build the 2-slice frame: columns _t1 (predictors at t-1) and _t (response at t).
n_t <- ncol(expr_mat)
lagged_df <- data.frame(
    t(expr_mat[, 2:n_t]),      # response slice t
    t(expr_mat[, 1:(n_t - 1)]) # predictor slice t-1
)
colnames(lagged_df) <- c(paste0(rownames(expr_mat), '_t'),
                         paste0(rownames(expr_mat), '_t1'))

# Constrain edges to t-1 -> t so the learned graph is a proper DBN transition model.
nodes_t  <- paste0(rownames(expr_mat), '_t')
nodes_t1 <- paste0(rownames(expr_mat), '_t1')
blacklist <- rbind(
    expand.grid(from = nodes_t, to = nodes_t1),   # forbid t -> t-1 (backward in time)
    expand.grid(from = nodes_t1, to = nodes_t1)   # forbid within-slice t-1 edges
)

# score='bic-g': Gaussian BIC; penalizes parameters, guarding the tiny sample against
# overfit. Gaussian assumes linear-Gaussian dependencies (misses threshold logic, like
# Granger); discretizing captures nonlinearity but needs data you do not have on short
# courses. hc is greedy -> trust boot.strength, not one DAG.
boot_res <- boot.strength(lagged_df, R = 200, algorithm = 'hc',
                          algorithm.args = list(score = 'bic-g', blacklist = blacklist))

# strength = fraction of bootstraps containing the arc; direction = fraction of those
# oriented the stated way. direction >= 0.5 is a COIN FLIP -- require >= 0.8 for a
# confidently oriented edge. bnlearn can also compute a data-driven strength threshold:
thr <- attr(boot_res, 'threshold')  # data-driven threshold lives on the bn.strength object, a principled alternative to hand-picked 0.7
confident <- boot_res[boot_res$strength >= max(0.7, thr) & boot_res$direction >= 0.8, ]
```

## Comparing networks across conditions

**Goal:** Identify genuine rewiring between two conditions, not artifacts of threshold choice.

**Approach:** Edge-set differences are dominated by density mismatch and near-threshold flips unless controlled. Compare at MATCHED edge density (top-K from each, same K), and only call an edge gained/lost if it is present-and-bootstrap-stable in one condition and absent-and-stable in the other.

```python
def top_k_edges(edge_df, k):
    return set(map(tuple, edge_df.sort_values('weight', ascending=False)
                   .head(k)[['tf', 'target']].values))

k = min(len(edges_a), len(edges_b))  # density-match BEFORE comparing
set_a, set_b = top_k_edges(edges_a, k), top_k_edges(edges_b, k)
jaccard = len(set_a & set_b) / len(set_a | set_b) if (set_a | set_b) else 0.0
gained, lost = set_b - set_a, set_a - set_b  # keep only bootstrap-stable ones
```

Jaccard heuristics (< 0.3 rewired, > 0.7 conserved) are uncalibrated and, without density-matching, mostly measure the threshold rather than biology -- present them as rough anchors only after matching.

## What experts do instead of trusting one method

- Prior-constrain regulators to annotated TFs (dynGENIE3 `regulators=`; Granger test only TF->target; DBN whitelist/blacklist). Highest-yield, cheapest precision lever.
- Ensemble across methods; edges recovered by >=2 orthogonal methods are the ones worth an experiment (Marbach 2012's wisdom-of-crowds result).
- Require replication across independent time series; bootstrap-subsample and re-rank to separate reproducible edges from artifacts.
- Treat the output as a prioritized hypothesis list for perturbation. Nothing in bulk inference validates an edge; only perturbation does.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `grangercausalitytests(..., verbose=False)` raises FutureWarning | `verbose` deprecated since statsmodels 0.14, slated for removal | Drop the argument; index the returned dict (`res[lag][0]['ssr_ftest'][1]`) |
| Granger q-values suspiciously optimistic | `min_p` across lags then BH is an uncorrected within-pair multiple test | Fix one lag a priori, or BIC-select one lag then run a single test, or Bonferroni across lags before BH |
| Granger has no power / errors on few timepoints | `n > 3*maxlag+1` barely met -> ~1 residual DoF | Use maxlag=1 on short courses; get more timepoints/replicates before trusting any q-value |
| "dynGENIE3 uses Extra-Trees" | dynGENIE3 defaults to `tree.method='RF'` (Random Forests); ET is opt-in | Pass `tree.method='ET'` if ET is wanted, else describe it as RF |
| dynGENIE3 edges read as calibrated | Importances have no null / no p-value | Threshold by rank explicitly; validate top edges by cross-method agreement + perturbation |
| dynGENIE3 gives garbage on sparse/uneven series | Finite-difference `dx/dt` amplifies noise | Add replicates (independent derivative samples), not just one more timepoint |
| DBN `direction >= 0.5` admits reversed edges | 0.5 = "more often than not" = coin-flip orientation | Require `direction >= 0.8`; consider bnlearn's data-driven strength threshold over a hand-picked 0.7 |
| Pairwise Granger reported as direct regulation | Blind to common drivers / chains; circadian oscillation fabricates dense edges | Label as confounded candidates; restrict to TF->target; intersect methods |
| Jaccard swings wildly between conditions | Density mismatch + near-threshold flips, not biology | Match edge density (top-K each); require bootstrap-stable presence/absence |
| Lag structure vanishes silently | Expression columns not in temporal order | Assert timepoint ordering before any lagging |

## Related Skills

- gene-regulatory-networks/coexpression-networks - Static (non-temporal) co-expression networks
- gene-regulatory-networks/scenic-regulons - Single-cell pseudotime regulon inference (different data and assumptions)
- gene-regulatory-networks/differential-networks - Condition-specific network comparison
- differential-expression/timeseries-de - Filter to temporally-variable genes before edge inference
- data-visualization/network-visualization - Plotting inferred networks

## References

- Granger CWJ. 1969. Investigating causal relations by econometric models and cross-spectral methods. *Econometrica* 37(3):424-438. Predictive-precedence definition of causality.
- Huynh-Thu VA, Geurts P. 2018. dynGENIE3: dynamical GENIE3 for the inference of gene networks from time series expression data. *Sci Rep* 8:3384. Semi-ODE + tree-regression-on-derivative method.
- Huynh-Thu VA, Irrthum A, Wehenkel L, Geurts P. 2010. Inferring regulatory networks from expression data using tree-based methods. *PLoS ONE* 5(9):e12776. GENIE3 tree-based variable selection.
- Marbach D, Costello JC, Kuffner R, et al. 2012. Wisdom of crowds for robust gene network inference. *Nat Methods* 9(8):796-804. Low precision, no single method wins, community-ensemble superiority.
- Scutari M. 2010. Learning Bayesian networks with the bnlearn R package. *J Stat Softw* 35(3):1-22. bnlearn `hc` / `boot.strength` API.
- Friedman N, Murphy K, Russell S. 1998. Learning the structure of dynamic probabilistic networks. *Proc. 14th Conf. on Uncertainty in Artificial Intelligence (UAI)*, pp. 139-147. Score-based DBN structure learning.
<!-- END FILE: temporal-genomics/temporal-grn/SKILL.md -->

## 子目录：temporal-genomics/trajectory-modeling

<!-- BEGIN FILE: temporal-genomics/trajectory-modeling/SKILL.md -->
---
name: bio-temporal-genomics-trajectory-modeling
description: Models continuous temporal trajectories from BULK or time-resolved omics where the x-axis is measured experimental time: penalized GAMs (mgcv) for smooth trends and changepoint detection (segmented, ruptures) for abrupt regime shifts. Use when deciding between a smooth GAM and a changepoint model; choosing the GAM distribution (nb() plus a library-size offset for raw counts vs Gaussian on vst/log-CPM); setting the basis-dimension ceiling k below the number of timepoints and letting REML pick wiggliness; handling residual autocorrelation across timepoints with corAR1/bam(rho=); testing whether two conditions' trajectories diverge with an ordered-factor difference smooth; and choosing a changepoint search/cost/penalty (Pelt/Binseg, l2/rbf). Not for single-cell pseudotime (see single-cell/trajectory-inference).
tool_type: mixed
primary_tool: mgcv
---

## Version Compatibility

Reference examples tested with: mgcv 1.9+, tradeSeq 1.16+, segmented 2.0+, ruptures 1.1+, numpy 1.26+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: the modeled quantity must be on a scale the family assumes. A Gaussian GAM is valid only on variance-stabilized/log-transformed expression (vst, rlog, log-CPM); raw RNA-seq counts require `family=nb()` with a `offset(log(library_size))`. Successive timepoints are correlated, so a plain `gam()` (which assumes independent residuals) inflates smooth-term significance unless the AR structure is modeled or the residual ACF is checked.

# Temporal Trajectory Modeling

**"Fit smooth curves to my gene expression over real time, compare trajectories, and find abrupt shifts"** -> model a continuous function of MEASURED time f(time), test whether it changes / differs between conditions, and locate discrete regime changes.
- R: `mgcv::gam()`/`gamm()`/`bam()` for penalized-spline GAMs; `segmented::segmented()` for slope breaks
- Python: `ruptures` for level/distribution changepoints

## The governing principle: measured time is not pseudotime, and the model class must match the mechanism

This skill models trajectories where the x-axis is ACTUAL experimental time (hours, days, developmental stage) or a pseudobulk value aggregated over real time. Time is measured and shared across every sample at a timepoint, so replicates are exchangeable, timepoints are few and fixed, and residual autocorrelation across ordered timepoints is real. This is categorically different from single-cell pseudotime, which is a latent per-cell ordering estimated with error and belongs to single-cell/trajectory-inference (and to tradeSeq's native use case). Conflating the two is the deepest error in the area.

Three decisions dominate correctness before any p-value is read:
1. Distribution. A Gaussian GAM on raw counts gives wrong SEs, wrong p-values, and can predict negatives. Model counts with `nb()` and a library-size offset, or fit Gaussian on a variance-stabilized scale.
2. Autocorrelation. Positive residual correlation across timepoints shrinks the effective sample size, so a plain `gam()` under-estimates SEs and over-calls temporal trends. Name the assumption and model it (`corAR1`/`bam(rho=)`) or at least inspect the residual ACF.
3. Mechanism. A smooth GAM assumes a gradually curving process; a changepoint model assumes a genuinely abrupt regime shift. Imposing changepoints on smooth data invents regime shifts; smoothing a true step Gibbs-rings over it. Match the model to the biology.

## Smooth GAM vs changepoint: choosing the model class

| Question | Model | Use when | Do NOT use when |
|----------|-------|----------|-----------------|
| Does expression change / curve over time? | GAM `s(time)` (mgcv) | process is gradual (induction/decay kinetics, developmental ramps) | the process is a discrete switch -> a smooth smears the discontinuity |
| Do two conditions' trajectories diverge? | ordered-factor difference smooth (mgcv) | testing whether treated shape departs from control | groups have no shared reference / only a constant offset differs (use a parametric term) |
| When does the regime shift (slope break)? | `segmented` (broken-line) | continuous piecewise-LINEAR change in slope | the shift is a level jump, not a slope change (use ruptures `l2`) |
| When does the regime shift (level/distribution)? | `ruptures` Pelt/Binseg | step change in mean (`l2`) or distribution (`rbf`) | the curve is smooth -> any liberal penalty fabricates breaks |
| Is a curve even warranted? | AIC/edf of `s(time)` vs linear | deciding non-linear vs linear is enough | over-interpreting edf near 1 as a real curve |

Methodology evolves; before committing verify current defaults and recommendations against the latest mgcv/ruptures/segmented documentation.

## mgcv GAM (R)

**Goal:** Fit a smooth non-linear curve to expression over measured time and test whether it changes, on the correct distributional scale.

**Approach:** Use a penalized regression spline `s(time)`; set the basis-dimension ceiling k generously but below the number of unique timepoints and let REML choose the realized wiggliness; use `nb()` + a library-size offset for raw counts, or Gaussian on a variance-stabilized scale.

```r
library(mgcv)

# k is a CEILING (max basis dimension), NOT the number of knots the curve will use.
# The REML-chosen penalty picks the realized wiggliness; edf (below) reports it.
# k must be < number of unique timepoints; realistically k <= (#timepoints - 1).
# method='REML': better-behaved objective than GCV, resists under/over-smoothing (Wood 2011).
fit <- gam(expression ~ s(time, k = 6, bs = 'tp'), data = gene_df, method = 'REML')

summary(fit)
# s.table columns: edf, Ref.df, F (Gaussian/unknown scale), p-value.
# edf ~ 1 => penalty shrank the smooth to linear; edf near k-1 => nearly full flexibility.
# The smooth-term p-value is APPROXIMATE (conditional on estimated lambda; Wood 2013):
# treat it as categorical significant/not, do not compare tiny magnitudes.
```

### Raw counts: NB family with a library-size offset

**Goal:** Model overdispersed RNA-seq counts on the count scale without violating the Gaussian assumption.

**Approach:** Fit `family=nb()` (mgcv estimates theta by REML) with `offset(log(library_size))` so the smooth describes rate, not depth.

```r
# Counts are mean-variance coupled and overdispersed: Gaussian is wrong on raw counts.
# nb() estimates theta jointly with the smoothing parameters under REML.
# offset(log(libsize)) absorbs sequencing depth so s(time) models expression rate.
fit_nb <- gam(counts ~ s(time, k = 6) + offset(log(library_size)),
              data = gene_df, family = nb(), method = 'REML')
# With a known-scale family the test column becomes Chi.sq, not F.
summary(fit_nb)$s.table
```

### Residual autocorrelation across timepoints

**Goal:** Prevent inflated smooth-term significance caused by correlation between successive timepoints.

**Approach:** Model a lag-1 AR structure grouped by the replication unit with `gamm(correlation=corAR1())`, or fix `rho` in `bam()` for genome-wide fits after reading the lag-1 residual ACF.

```r
# Plain gam() assumes independent residuals; positive AR(1) shrinks effective n,
# under-estimates SEs, and lets the smooth get too wiggly -> false temporal trends.
# corAR1 models e_t = rho * e_{t-1} + noise; group by subject/animal/plate.
fit_ar <- gamm(expression ~ s(time, k = 6),
               correlation = corAR1(form = ~ time | subject),
               data = gene_df, method = 'REML')
# fit_ar$gam holds the smooth; fit_ar$lme holds the correlation estimate.

# Genome-wide alternative: fit once without AR, read lag-1 residual ACF, set rho, refit.
# AR.start flags the first observation of each independent series.
fit_bam <- bam(expression ~ s(time, k = 6), data = gene_df,
               rho = 0.4, AR.start = series_start, method = 'fREML')
```

With independent biological replicates AT EACH timepoint the correlation is often weak or unidentifiable and plain `gam()` is defensible; a single series sampled repeatedly over many timepoints is where AR bites hardest. Always inspect the residual ACF before trusting the smooth p-value.

### Comparing conditions with an ordered-factor difference smooth

**Goal:** Directly test whether the treated trajectory's shape diverges from control, with its own p-value.

**Approach:** Make the grouping an ORDERED factor so `s(time, by=grp)` becomes a difference smooth (level minus reference); keep the reference global smooth AND the parametric main effect.

```r
# Unordered by= gives each group's curve vs zero -- NOT a divergence test.
# Ordered factor: s(time, by=grp) is the difference smooth; its single p-value
# directly tests whether the trajectories diverge. Extends cleanly to >2 groups.
gene_df$condition <- as.ordered(gene_df$condition)
fit_diff <- gam(expression ~ condition + s(time, k = 6) + s(time, k = 6, by = condition),
                data = gene_df, method = 'REML')
# The parametric 'condition' term is REQUIRED: centered smooths cannot carry the
# group's overall level, so without it a constant offset is misattributed to the smooth.
summary(fit_diff)
```

A numeric 0/1 `by=is_treated` indicator is a valid shortcut for a single 2-level contrast (the second smooth is the treatment deviation), but the ordered-factor form is the general, canonical idiom.

### Diagnostics: gam.check, k-index, concurvity

**Goal:** Decide whether the basis is adequate and whether smooth terms are mutually identifiable.

**Approach:** Read `gam.check()`/`k.check()`; respond to a low k-index by doubling k and refitting, not by reflexively cranking k; use `concurvity()` only for multi-smooth models.

```r
gam.check(fit)   # 4 residual plots + k.check(): reports k', edf, k-index, p-value

# k-index < 1 with a small p means residual pattern the basis is too rigid to capture.
# CORRECT diagnostic = double k and refit: if edf rises substantially, k was too low;
# if edf barely moves, k was fine and the low k-index reflects autocorrelation or
# a distributional problem -- do not just raise k.

# Concurvity = the smooth analog of collinearity; only meaningful for multi-term models.
# Near 1 => partial attribution between smooths is unstable; > 0.8 is a worry, not a cutoff.
concurvity(fit_diff, full = TRUE)
```

### Prediction and pointwise intervals

**Goal:** Visualize the fitted trajectory with an uncertainty band, within the sampled range only.

**Approach:** Predict on a fine grid with `se.fit=TRUE`; band = fit +/- 1.96*SE (pointwise, not simultaneous); never extrapolate.

```r
grid <- data.frame(time = seq(min(gene_df$time), max(gene_df$time), length.out = 200))
pred <- predict(fit, newdata = grid, se.fit = TRUE)
grid$fitted <- pred$fit
# 1.96*SE is a POINTWISE 95% band; whole-curve (simultaneous) coverage is < 95%,
# so overlapping condition bands are NOT a formal test -- use the difference smooth p-value.
grid$lower <- pred$fit - 1.96 * pred$se.fit
grid$upper <- pred$fit + 1.96 * pred$se.fit
# Beyond [min(time), max(time)] the spline and its SE diverge -- do not predict outside range.
```

### Genome-wide GAM fitting + FDR

**Goal:** Rank genes by temporal significance across the transcriptome.

**Approach:** Fit `s(time)` per gene, collect the smooth p-value, apply BH across genes (the per-gene p-values are approximate, so the FDR is approximate; permutation calibration is the gold standard for strong claims).

```r
# expr_mat here must be variance-stabilized (vst / log-CPM); for raw counts use the family=nb() + offset
# form above instead of this default-Gaussian fit, or the per-gene SEs and p-values are invalid.
results <- data.frame()
for (gene in rownames(expr_mat)) {
    df <- data.frame(expression = as.numeric(expr_mat[gene, ]), time = timepoints)
    fit <- gam(expression ~ s(time, k = 6), data = df, method = 'REML')
    s_tab <- summary(fit)$s.table
    results <- rbind(results, data.frame(gene = gene, edf = s_tab[, 'edf'],
                                         p_value = s_tab[, 'p-value']))
}
results$q_value <- p.adjust(results$p_value, method = 'BH')  # q<0.05: standard FDR floor
temporal_genes <- results[results$q_value < 0.05, ]
```

## tradeSeq (R/Bioconductor) -- off-label for bulk

tradeSeq is BUILT for single-cell pseudotime lineages, not bulk real-time. `fitGAM(counts, pseudotime, cellWeights, nknots)` expects a gene x cell count matrix, a cell x lineage pseudotime matrix, and cell x lineage soft-assignment weights, and fits an NB GAM per gene per lineage. Its tests (`associationTest`, `startVsEndTest`, `conditionTest`, `patternTest`) are keyed to pseudotime lineages.

```r
# Only reasonable when the design is genuinely a pseudobulk-over-a-lineage.
# For a standard bulk time-course with replicates at fixed timepoints, use mgcv directly:
# the same NB GAM, with full control over by= contrasts, offsets, and AR structure,
# and without single-cell scaffolding. nknots plays the same ceiling role as k (choose it with evaluateK()).
library(tradeSeq)
sce <- fitGAM(counts = count_mat, pseudotime = pt_mat, cellWeights = cw_mat, nknots = 6)
assoc_res <- associationTest(sce)   # matrix of Wald stat + df + p-value, NOT an SCE
```

## segmented (R) -- broken-line slope break

**Goal:** Locate a continuous change in SLOPE and test whether a break exists at all.

**Approach:** Pre-test with `davies.test` before fitting a break; estimate the breakpoint with `segmented()` from a starting value; limit to one break unless the data are dense.

```r
library(segmented)
lm_fit <- lm(expression ~ time, data = gene_df)

# davies.test H0: difference-in-slopes = 0 (no breakpoint). It searches candidate
# locations and corrects the minimum p for the search (slightly conservative).
# Decide WHETHER a break exists before interpreting one. pscore.test() is more powerful
# for a single break.
davies.test(lm_fit, seg.Z = ~time)

# segmented models a CONTINUOUS slope change (not a level jump); psi = starting value(s),
# NA auto-initializes. The estimator is a local search: sensitive to psi, fragile with
# multiple breaks (closely spaced breaks are non-identifiable).
seg_fit <- segmented(lm_fit, seg.Z = ~time, psi = NA)
summary(seg_fit)$psi   # breakpoint estimate + SE (break CI is approximate/often too narrow)
```

## ruptures (Python) -- level/distribution changepoints

**Goal:** Detect discrete times where the mean (or whole distribution) shifts.

**Approach:** Factorize as (search method) x (cost model) x (penalty); the penalty choice IS the number-of-changepoints choice; match the cost model to the shift type and estimate the noise variance, not the total variance.

```python
import numpy as np
import ruptures as rpt

signal = np.asarray(expression_values)

# model='l2' detects changes in MEAN (piecewise-constant level -- the natural choice for
#   step-like expression regimes). 'rbf' detects changes in the whole distribution
#   (mean AND variance) -- more general, hungrier for data, less interpretable.
# min_size=2: minimum segment length. Pelt is exact (O(n) via pruning); it takes a penalty
#   and RETURNS the number+location of breaks -- there is no separate 'how many' knob.
n = len(signal)
# Noise variance, NOT total variance: np.var(signal) includes between-regime variation, so
# a BIC-style penalty log(n)*np.var(signal) is too large and UNDER-detects. Estimate noise
# from lag-1 differences instead. BIC is derived for the l2/Gaussian-mean cost -- pairing it
# with model='rbf' is theoretically mismatched; use l2 with BIC, or calibrate rbf empirically.
sigma2 = np.var(np.diff(signal)) / 2.0
penalty = np.log(n) * sigma2
bkps = rpt.Pelt(model='l2', min_size=2).fit(signal).predict(pen=penalty)
# predict returns break indices INCLUDING the terminal index n:
n_changepoints = len(bkps) - 1   # bkps[:-1] are the actual break locations

# Binseg: greedy, approximate, fast; takes a KNOWN number of breaks (sanity check vs Pelt).
bkps_binseg = rpt.Binseg(model='l2', min_size=2).fit(signal).predict(n_bkps=2)
```

Guard against fabricated breaks: a liberal penalty always "finds" changepoints in a smooth ramp. Require a pre-test (a break exists) or compare a piecewise fit against a smooth-GAM fit by AIC -- if the smooth wins, the "changepoint" is a sampling-noise artifact. With few timepoints, be extremely skeptical of more than one break.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| p-values wrong / fitted curve predicts negative expression | Gaussian GAM on raw overdispersed counts | `family=nb()` + `offset(log(library_size))`, or fit Gaussian on vst/log-CPM |
| Many genes "significantly change over time" implausibly | residual autocorrelation inflates smooth-term significance | `gamm(..., correlation=corAR1(form=~time|subject))` or `bam(..., rho=, AR.start=)`; check residual ACF |
| Treating k as "the number of bends I want" | k is the flexibility CEILING, not realized complexity | set k generously (< #timepoints), let REML pick lambda; read `edf`, not k |
| Cranking k whenever k-index < 1 | low k-index can mean autocorrelation/heteroscedasticity, not low basis | double k and refit -- if edf jumps, raise k; if not, look at correlation/distribution |
| Reading p=1e-30 as thirty orders of certainty | smooth p-values are approximate (ignore full lambda uncertainty) | treat as categorical significant/not; apply BH FDR across genes |
| Unordered `by=` used "to test if curves differ" | it gives each group vs zero, not a divergence test | `as.ordered(condition)` -> the difference smooth's p-value IS the divergence test |
| `by=` smooth without the parametric main effect | centered smooths cannot carry the group level | include `condition +` alongside `s(time, by=condition)` |
| `tradeSeq::fitGAM` on a plain bulk time-course | tradeSeq is single-cell pseudotime machinery (needs cellWeights) | use `mgcv` directly for bulk real-time; reserve tradeSeq for pseudobulk lineages |
| ruptures under-detects real changepoints | `pen=log(n)*np.var(signal)` uses TOTAL variance -> penalty too large | estimate noise from `np.var(np.diff(signal))/2`; sweep the penalty |
| `model='rbf'` with a BIC (`log n * var`) penalty | BIC penalty is derived for the l2/Gaussian-mean cost | use `model='l2'` with BIC, or calibrate the rbf penalty empirically |
| Changepoints "found" in a clearly smooth ramp | a liberal penalty fabricates breaks in gradual data | pre-test with `davies.test`; compare piecewise vs smooth-GAM AIC; the smooth often wins |
| Fitted curve behaves wildly past the last timepoint | extrapolating a penalized spline beyond the data | predict only within `[min(time), max(time)]` |
| "The condition bands overlap, so no difference" | 1.96*SE bands are pointwise, not simultaneous | use the difference-smooth p-value or simultaneous (posterior-simulation) intervals |
| `segmented` with several `psi` gives unstable breaks | multiple breakpoints are weakly identifiable with few noisy points | limit to 1 break unless data are dense; supply good `psi` starts; check convergence |

## Related Skills

- temporal-clustering - group genes by trajectory shape after fitting
- circadian-rhythms - periodic (known-period) trajectory models rather than smooth trends
- periodicity-detection - discover unknown-period oscillation instead of a smooth trend
- differential-expression/timeseries-de - linear/spline model alternatives for temporal DE
- single-cell/trajectory-inference - single-cell pseudotime (latent inferred ordering), the case tradeSeq is built for

## References

- Wood SN. 2011. Fast stable restricted maximum likelihood and marginal likelihood estimation of semiparametric generalized linear models. *J R Stat Soc B* 73(1):3-36. doi:10.1111/j.1467-9868.2010.00749.x. (REML smoothing-parameter selection, better-behaved than GCV.)
- Wood SN. 2013. On p-values for smooth components of an extended generalized additive model. *Biometrika* 100(1):221-228. doi:10.1093/biomet/ass048. (Smooth-term p-values are approximate; pointwise interval coverage.)
- Wood SN. 2017. *Generalized Additive Models: An Introduction with R*, 2nd ed. Chapman & Hall/CRC. ISBN 9781498728331. (Basis-penalty framework, gam.check, concurvity.)
- Pedersen EJ, Miller DL, Simpson GL, Ross N. 2019. Hierarchical generalized additive models in ecology: an introduction with mgcv. *PeerJ* 7:e6876. doi:10.7717/peerj.6876. (Global-plus-difference-smooth and factor-smooth condition-comparison structure.)
- Van den Berge K, Roux de Bezieux H, Street K, Saelens W, Cannoodt R, Saeys Y, Dudoit S, Clement L. 2020. Trajectory-based differential expression analysis for single-cell sequencing data. *Nat Commun* 11(1):1201. doi:10.1038/s41467-020-14766-3. (tradeSeq: NB-GAM DE along pseudotime lineages, hence off-label for bulk.)
- Muggeo VMR. 2003. Estimating regression models with unknown break-points. *Stat Med* 22(19):3055-3071. doi:10.1002/sim.1545. (Broken-line estimator behind segmented and davies.test.)
- Killick R, Fearnhead P, Eckley IA. 2012. Optimal detection of changepoints with a linear computational cost. *J Am Stat Assoc* 107(500):1590-1598. doi:10.1080/01621459.2012.737745. (PELT exact O(n) penalized algorithm behind rpt.Pelt.)
- Truong C, Oudre L, Vayatis N. 2020. Selective review of offline change point detection methods. *Signal Processing* 167:107299. doi:10.1016/j.sigpro.2019.107299. (The cost x search x constraint taxonomy; the ruptures reference paper.)
<!-- END FILE: temporal-genomics/trajectory-modeling/SKILL.md -->

<!-- END CATEGORY: temporal-genomics -->

