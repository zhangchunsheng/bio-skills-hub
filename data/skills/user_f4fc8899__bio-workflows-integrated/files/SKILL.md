---
slug: bio-workflows-integrated
version: 1.0.0
displayName: "分析工作流 / End-to-end analysis workflows"
name: bio-workflows-integrated
summary: >-
  中文：分析工作流综合技能，整合 41 个相关专题，覆盖端到端分析工作流：RNA-seq、scRNA-seq、变异检测、ChIP-seq、ATAC-seq、空间转录组、CRISPR筛选等。 English: Integrated End-to-end analysis workflows skill covering 41 related topics, including End-to-end analysis workflows: RNA-seq, scRNA-seq, variant calling, ChIP-seq, ATAC-seq, spatial transcriptomics, CRISPR screens, and more.
description: >-
  中文：这是一个面向分析工作流的综合生物信息学 Skill，整合当前分类下 41 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：端到端分析工作流：RNA-seq、scRNA-seq、变异检测、ChIP-seq、ATAC-seq、空间转录组、CRISPR筛选等。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Bakta, Bismark, CATALYST。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for End-to-end analysis workflows, combining 41 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers End-to-end analysis workflows: RNA-seq, scRNA-seq, variant calling, ChIP-seq, ATAC-seq, spatial transcriptomics, CRISPR screens, and more. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Bakta, Bismark, CATALYST. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# workflows 分类 Skill 整合版

> 本文件整合同一主分类目录下 41 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: workflows -->

## 子目录：workflows/atacseq-pipeline

<!-- BEGIN FILE: workflows/atacseq-pipeline/SKILL.md -->
---
name: bio-workflows-atacseq-pipeline
description: Orchestrates the end-to-end bulk ATAC-seq pipeline from FASTQ to differential accessibility and TF footprints, chaining Nextera-aware fastp QC, Bowtie2 alignment, chrM removal, dedup, a single Tn5 +4/-5 shift, MACS3 peak calling, Corces fixed-width consensus, DiffBind/csaw differential accessibility, and TOBIAS footprinting. Use when committing the reference build + blacklist once, recognizing ATAC has NO input control (the shift-extend model IS the background), applying the Tn5 shift exactly once (never combining -f BAMPE with --shift/--extsize), removing chrM before calling, building a fixed-width consensus so per-sample counts are comparable, or choosing MACS3 vs Genrich vs HMMRATAC. Hands mechanism to the atac-seq component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: MACS3
workflow: true
depends_on:
  - read-qc/fastp-workflow
  - read-alignment/bowtie2-alignment
  - alignment-files/duplicate-handling
  - atac-seq/atac-peak-calling
  - atac-seq/atac-qc
  - atac-seq/consensus-peakset
  - atac-seq/differential-accessibility
  - atac-seq/footprinting
  - atac-seq/motif-deviation
  - atac-seq/nucleosome-positioning
qc_checkpoints:
  - after_qc: "Q30 >85%, adapter content <5% (Nextera)"
  - after_alignment: "Mapping rate >80%, mitochondrial <20% (Omni-ATAC lower)"
  - before_dedup: "NRF >0.8, PBC1 >0.8 (computed PRE-dedup)"
  - after_peaks: "FRiP >0.2, TSS enrichment >5 (ENCODE v3; v4 thresholds differ, do not mix)"
  - after_consensus: "Fixed-width (Corces 501 bp) consensus built before counting for differential"
---

## Version Compatibility

Reference examples tested with: Bowtie2 2.5.3+, MACS3 3.0+, Genrich 0.6+, bedtools 2.31+, deepTools 3.5+ (alignmentSieve), fastp 0.23+, samtools 1.19+, DiffBind 3.12+, TOBIAS 0.16+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: `macs3 callpeak -f BAMPE` uses real fragment lengths and IGNORES `--shift/--extsize/--nomodel`; the cut-site style needs `-f BAM`/`-f BED` on Tn5-shifted reads. `alignmentSieve --ATACshift` applies the +4/-5 shift once. ENCODE ATAC-seq v3 and v4 QC thresholds are not interchangeable. Confirm in-tool before quoting.

# ATAC-seq Pipeline

**"Run ATAC-seq from FASTQ to differential accessibility and footprints"** -> Chain QC/trim, alignment, chrM removal, dedup, a single Tn5 shift, peak calling, fixed-width consensus, differential accessibility, and footprinting.
- CLI + R: fastp -> bowtie2 -> drop chrM -> markdup -> Tn5 shift (once) -> macs3 -> Corces consensus -> DiffBind/csaw -> TOBIAS

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

ATAC-seq differs from ChIP-seq at four seams, and each is where the analysis goes wrong.

1. **There is NO input control -- the shift-extend cut-site model IS the background.** ATAC has no matched IP/input; peak significance comes from local lambda over the Tn5 insertion signal. Do not invent a "control"; commit instead to the build + ENCODE blacklist (removed before calling) as the coordinate frame.
2. **The Tn5 +4/-5 shift is applied EXACTLY ONCE, after dedup and chrM removal.** `alignmentSieve --ATACshift` (or one bedtools awk) applies it. Applying it twice, or combining `-f BAMPE` with `--shift/--extsize` (silently ignored), misplaces every cut site. Pick ONE calling mode: cut-site (`-f BAM`/`-f BED` + `--nomodel --shift -75 --extsize 150`) OR fragment (`-f BAMPE` on shifted reads, NO `--shift`).
3. **chrM is removed BEFORE peak calling.** Mitochondrial reads dominate ATAC libraries (often 20-50%, less with Omni-ATAC); leaving them in inflates depth and distorts FRiP and normalization.
4. **Differential accessibility requires a FIXED-WIDTH consensus peakset.** Variable-width MACS peaks make per-sample counts non-comparable. Build the Corces 501 bp iterative-overlap consensus (Corces 2018) so every region is the same width before counting; DiffBind/csaw then count into uniform intervals.

Reporting corollary: ENCODE ATAC v3 and v4 define TSS-enrichment/FRiP thresholds differently -- pick one standard and state which; do not mix rows across versions.

## Pipeline map

```
FASTQ (paired, Nextera)
  | [1] QC & trim -----------------> fastp (Nextera adapters)   (read-qc/fastp-workflow)
  v
  | [2] Align ---------------------> bowtie2 --very-sensitive -X 2000   (read-alignment/bowtie2-alignment)
  v     ^-- commitment: build + ENCODE blacklist (NO input control)
  | [3] Drop chrM (BEFORE dedup/peaks) -> mito can be 20-50% of reads
  v
  | [4] Dedup --------------------> markdup -r   (alignment-files/duplicate-handling)
  v
  | [5] Tn5 shift ONCE ------------> alignmentSieve --ATACshift (+4/-5)
  v     ^-- pick ONE calling mode; never BAMPE + --shift
  | [6] Peak calling -------------> macs3 (cut-site -f BAM --shift/--extsize | -f BAMPE)  (atac-seq/atac-peak-calling)
  v
  | [7] Fixed-width consensus -----> Corces 501 bp iterative overlap   (atac-seq/consensus-peakset)
  v
  | [8] QC + differential + footprints -> TSS/FRiP/fragment; DiffBind/csaw; TOBIAS  (atac-seq/atac-qc, differential-accessibility, footprinting)
  v
Accessibility peaks + differential regions + TF activity
```

## Made-once commitments

| Commitment | Choice | Consequence inherited downstream |
|------------|--------|----------------------------------|
| Build + blacklist | One build; ENCODE blacklist (removed before calling) | ATAC has no input, so the blacklist + shift-extend model ARE the background control |
| Tn5 shift | Applied ONCE (`--ATACshift`), then ONE calling mode | Double-shift or BAMPE+`--shift` misplaces cut sites |
| chrM handling | Removed before dedup/peaks | Mito reads (20-50%) inflate depth, FRiP, normalization |
| Differential interval | Fixed-width Corces 501 bp consensus | Variable-width peaks make per-sample counts non-comparable |

## The canonical order and why

1. **QC/trim** with Nextera adapters (`CTGTCTCTTATACACATCT`).
2. **Align** (bowtie2 `--very-sensitive -X 2000`) so the full nucleosome-spanning fragment distribution is captured.
3. **Remove chrM, then compute NRF/PBC, then dedup** -- order-trap on both ends: `markdup -r` physically removes duplicates, so NRF/PBC1 computed afterwards are identically 1.0; and mito reads are over-amplified, so computing them before chrM removal measures chrM chemistry, not nuclear-library complexity. The binding constraint is PRE-DEDUP. Mito must go before peak calling regardless.
4. **Dedup** (collate -> fixmate -m -> sort -> markdup -r).
5. **Tn5 shift ONCE** (`alignmentSieve --ATACshift`).
6. **Call peaks in ONE mode** -- order-trap: `-f BAMPE` + `--shift/--extsize` silently drops the flags.
7. **Build the fixed-width consensus** (Corces 501 bp) -- order-trap: differential on variable-width peaks is not comparable.
8. **QC, differential (DiffBind/csaw on the consensus), footprinting (TOBIAS)**.

## Choosing the caller and calling mode

Pipeline-level selection only; mechanism lives in the component skills.

| Fork | Lean toward | Hand off to |
|------|-------------|-------------|
| Caller | MACS3 (standard); Genrich (`-j` ATAC mode: handles replicates + chrM + blacklist in one pass); HMMRATAC (nucleosome-aware HMM) | atac-seq/atac-peak-calling |
| Calling mode | Cut-site `-f BAM`/`-f BED` + `--nomodel --shift -75 --extsize 150` (ENCODE smoothing window on shifted reads) vs fragment `-f BAMPE` on shifted reads (no `--shift`) | atac-seq/atac-peak-calling |
| Consensus | Corces 2018 iterative-overlap fixed-width 501 bp | atac-seq/consensus-peakset |
| Differential | DiffBind / csaw / DESeq2 on the fixed-width count matrix; spike-in for global shifts | atac-seq/differential-accessibility |

## Primary path: Bowtie2 + Tn5 shift + MACS3

**Goal:** turn Nextera FASTQ into shifted, chrM-free peaks ready for a fixed-width consensus.

**Approach:** align with a wide insert window, drop chrM, dedup, Tn5-shift once, then call in ONE mode. Full runnable script: `examples/atacseq_workflow.sh`; differential: `examples/differential_atac.R`.

```bash
bowtie2 -p 8 -x bt2_index/genome -1 trimmed/${s}_R1.fq.gz -2 trimmed/${s}_R2.fq.gz \
    --very-sensitive --no-mixed --no-discordant -X 2000 2> aligned/${s}.log \
  | samtools view -@4 -bS -q 30 -f 2 - | samtools sort -@4 -o aligned/${s}.sorted.bam
samtools index aligned/${s}.sorted.bam

# Drop chrM BEFORE dedup/peaks (mito dominates ATAC), then dedup
samtools idxstats aligned/${s}.sorted.bam | cut -f1 | grep -v -e '^chrM$' -e '^MT$' \
  | xargs samtools view -b aligned/${s}.sorted.bam > aligned/${s}.noMT.bam
samtools collate -@8 -O -u aligned/${s}.noMT.bam | samtools fixmate -m -u - - \
  | samtools sort -@8 -u - | samtools markdup -r -@8 - aligned/${s}.dedup.bam
samtools index aligned/${s}.dedup.bam            # alignmentSieve needs an indexed input BAM

# Tn5 +4/-5 shift ONCE
alignmentSieve -b aligned/${s}.dedup.bam -o aligned/${s}.shifted.bam --ATACshift -p 8
samtools index aligned/${s}.shifted.bam

# Remove ENCODE blacklist regions BEFORE calling (the made-once commitment above; see the example script)
# Everything downstream (peaks, counts, footprints) consumes ${s}.filt.bam, never ${s}.shifted.bam.
# NOTE: examples/atacseq_workflow.sh names its blacklist-FILTERED output `.shifted.bam`; same reads,
# different name. Match on the step, not the suffix.
bedtools intersect -v -a aligned/${s}.shifted.bam -b "$BLACKLIST" > aligned/${s}.filt.bam
samtools index aligned/${s}.filt.bam

# Cut-site calling on the shifted, blacklist-filtered reads (ONE mode; do NOT also use -f BAMPE with these flags)
macs3 callpeak -t aligned/${s}.filt.bam -f BAM -g hs -n ${s} --outdir peaks \
    --nomodel --shift -75 --extsize 150 --keep-dup all -q 0.01
```

For the ENCODE 4 IDR + pseudoreplicate pipeline and the Corces 501 bp iterative-overlap consensus, see atac-seq/atac-peak-calling and atac-seq/consensus-peakset.

## Differential accessibility and footprinting

**Goal:** compare accessibility across conditions on comparable intervals, then read TF activity.

**Approach:** count into the fixed-width consensus with DiffBind (or csaw), then run the TOBIAS three-step (ATACorrect -> ScoreBigwig -> BINDetect) for footprints.

```r
library(DiffBind)                                  # counts into the fixed-width consensus
dba <- dba(sampleSheet = samples)                  # bamReads = shifted BAMs, Peaks = per-sample narrowPeak
dba <- dba.count(dba)                              # use summits/consensus for uniform width
dba <- dba.normalize(dba); dba <- dba.contrast(dba, categories = DBA_CONDITION)
dba <- dba.analyze(dba); report <- dba.report(dba)
```

```bash
# peaks/consensus.bed is the Corces 501 bp FIXED-WIDTH consensus from atac-seq/consensus-peakset (step 7).
# It is NOT peaks/consensus_peaks.narrowPeak, which is the variable-width pooled MACS3 call; build the
# fixed-width set first or these three commands have no input.
# TOBIAS three-step: bias-correct -> score -> detect bound motifs (differential across two conditions).
# Footprint on the BLACKLIST-FILTERED reads (${s}.filt.bam), the same reads MACS3 called peaks from --
# blacklist regions are artifact pileups, and bias-correcting over them corrupts the footprint scores.
TOBIAS ATACorrect -b aligned/${s}.filt.bam -g genome.fa -p peaks/consensus.bed --outdir foot --cores 8
TOBIAS ScoreBigwig --signal foot/${s}_corrected.bw --regions peaks/consensus.bed --output foot/${s}.bw --cores 8
TOBIAS BINDetect --motifs motifs.jaspar --signals foot/ctrl.bw foot/treat.bw --genome genome.fa \
    --peaks peaks/consensus.bed --outdir foot/bindetect --cores 8
```

## QC checkpoints between steps

| After | Gate | Interpretation |
|-------|------|----------------|
| Alignment | Mapping >80%, mito <20% (Omni-ATAC lower) | High mito = suboptimal lysis; drop before calling |
| PRE-dedup | NRF >0.8, PBC1 >0.8 | Low complexity = over-amplification/low input; compute before dedup |
| Peaks | FRiP >0.2, TSS enrichment >5 (v3) | Low TSS/FRiP = over/under-digestion or degraded chromatin (atac-seq/atac-qc) |
| Fragment size | NFR <100 bp, mono ~200 bp, di ~400 bp periodicity | Loss of nucleosome periodicity = over-digestion (Tn5:DNA too high) |
| Consensus | Fixed-width (501 bp) built before counting | Variable-width peaks make counts non-comparable |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Depth/FRiP dominated by one contig; few real peaks | chrM not removed before calling | Drop chrM/MT before dedup and peak calling |
| Cut sites offset / footprints smeared | Tn5 shift applied twice, or `-f BAMPE` used with `--shift/--extsize` | Shift ONCE; pick ONE calling mode (cut-site `-f BAM` OR fragment `-f BAMPE`) |
| Differential counts not comparable across samples | Counted into variable-width MACS peaks | Build the Corces 501 bp fixed-width consensus first |
| Looked for an input/IgG track and found none | ATAC has no input control | Use the blacklist + shift-extend model as background; do not fabricate a control |
| QC numbers disagree with a reference | Mixed ENCODE v3 and v4 thresholds | Pick one ENCODE version and report which |

## Pipeline map (hand-offs)

- read-qc/fastp-workflow - Nextera adapter trimming
- read-alignment/bowtie2-alignment - the aligner, wide insert window
- alignment-files/duplicate-handling - collate/fixmate/sort/markdup order
- atac-seq/atac-peak-calling - MACS3/Genrich/HMMRATAC, ENCODE 4 IDR, calling modes
- atac-seq/atac-qc - TSS enrichment, FRiP, NRF/PBC, fragment periodicity
- atac-seq/consensus-peakset - Corces 2018 iterative-overlap fixed-width consensus
- atac-seq/differential-accessibility - DiffBind/csaw/DESeq2 on the consensus
- atac-seq/footprinting - TOBIAS three-step and per-TF failure modes
- atac-seq/nucleosome-positioning - V-plot, NucleoATAC, +1 nucleosome

The complete runnable scripts are in this skill's examples/ (`atacseq_workflow.sh`, `differential_atac.R`).

## Related Skills

- database-access/sra-data - Pull ATAC-seq FASTQ from SRA / ENA
- database-access/geo-data - Resolve GEO accessions for ATAC datasets
- read-qc/fastp-workflow - Nextera adapter trimming and quality filtering
- read-alignment/bowtie2-alignment - Standard ATAC-seq aligner
- alignment-files/duplicate-handling - MarkDuplicates pre-peak-calling
- atac-seq/atac-peak-calling - MACS3 / Genrich / HMMRATAC details, ENCODE 4 IDR
- atac-seq/atac-qc - TSS enrichment, FRiP, NRF/PBC1/PBC2 details
- atac-seq/consensus-peakset - Corces 2018 iterative-overlap fixed-width consensus
- atac-seq/differential-accessibility - DiffBind / csaw / DESeq2; spike-in normalization
- atac-seq/footprinting - TOBIAS three-step; per-TF failure modes
- atac-seq/motif-deviation - chromVAR for motif accessibility variability
- atac-seq/nucleosome-positioning - V-plot, NucleoATAC, +1 nucleosome
- atac-seq/single-cell-atac - For scATAC instead of bulk
- atac-seq/co-accessibility - Cicero cis-regulatory inference
- atac-seq/enhancer-gene-linking - ABC, ENCODE-rE2G enhancer-gene mapping
- atac-seq/deep-learning-atac - chromBPNet variant-effect prediction
- atac-seq/allele-specific-accessibility - WASP + caQTL mapping
- chip-seq/peak-annotation - Annotate ATAC peaks to genes

## References

- Buenrostro JD, Giresi PG, Zaba LC, Chang HY, Greenleaf WJ (2013) Transposition of native chromatin for fast and sensitive epigenomic profiling of open chromatin, DNA-binding proteins and nucleosome position. *Nature Methods* 10:1213-1218. DOI 10.1038/nmeth.2688. (original ATAC-seq.)
- Corces MR, Trevino AE, Hamilton EG, et al (2017) An improved ATAC-seq protocol reduces background and enables interrogation of frozen tissues. *Nature Methods* 14:959-962. DOI 10.1038/nmeth.4396. (Omni-ATAC.)
- Corces MR, Granja JM, Shams S, et al (2018) The chromatin accessibility landscape of primary human cancers. *Science* 362:eaav1898. DOI 10.1126/science.aav1898. (fixed-width iterative-overlap consensus peakset.)
- Bentsen M, Goymann P, Schultheis H, et al (2020) ATAC-seq footprinting unravels kinetics of transcription factor binding during zygotic genome activation. *Nature Communications* 11:4267. DOI 10.1038/s41467-020-18035-1. (TOBIAS.)
<!-- END FILE: workflows/atacseq-pipeline/SKILL.md -->

## 子目录：workflows/biomarker-pipeline

<!-- BEGIN FILE: workflows/biomarker-pipeline/SKILL.md -->
---
name: bio-workflows-biomarker-pipeline
description: End-to-end biomarker discovery workflow from expression data to validated biomarker panels. Covers feature selection with Boruta/LASSO, leakage-safe cross-validation, calibration, and SHAP interpretation. Use when building and validating diagnostic or prognostic biomarker signatures from omics data.
tool_type: python
primary_tool: sklearn
workflow: true
depends_on:
  - machine-learning/biomarker-discovery
  - machine-learning/model-validation
  - machine-learning/omics-classifiers
  - machine-learning/prediction-explanation
qc_checkpoints:
  - after_selection: "Selected features 5-200, stability index reported alongside count"
  - after_cv: "Selection inside the CV pipeline; AUC reported with fold spread; AUPRC/MCC if imbalanced"
  - after_interpretation: "SHAP used as a shortcut/batch audit, aggregated over modules, not as the validated panel"
  - after_validation: "Hold-out AUC with bootstrap CI plus calibration (Brier); external cohort for the real bar"
---

## Version Compatibility

Reference examples tested with: numpy 1.26+, pandas 2.2+, scikit-learn 1.4+, shap 0.47+ (the `feature_perturbation='auto'` estimand and per-class 3-D `.values` behavior the code relies on; xgboost 2.0+ optional).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

scikit-learn drift: `CalibratedClassifierCV(cv='prefit')` deprecated in 1.6 (use `FrozenEstimator`); `LogisticRegression(penalty=)` deprecated in 1.8, and `LogisticRegressionCV(penalty='l1')` too -- the 1.8+ migration drops `penalty=` entirely and passes `l1_ratios=(1.0,)` alone (leave `penalty` at its default; `penalty='elasticnet'` still emits the FutureWarning). XGBoost moved `early_stopping_rounds` to the constructor in 2.x. If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Biomarker Discovery Pipeline

**"Build a validated biomarker panel from my omics data"** -> Orchestrate group-aware splitting, feature selection, leakage-safe cross-validation, calibration, and SHAP interpretation to produce a robust, honestly-validated biomarker signature.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

The whole pipeline stands or falls on four commitments made at the seams; each one, if broken, inflates the reported performance and a held-out set cannot detect the leak because it was already contaminated.

1. **The independent unit of splitting is the highest biological unit — patient/donor/site, NOT the sample — and it is committed first.** Multiple biopsies, longitudinal samples, or technical replicates from one subject in both train and test is group leakage; the model memorizes the subject, not the biology. Split with `GroupKFold`/`StratifiedGroupKFold` on a subject key. For single-cell-derived features the unit is the donor, not the cell.
2. **Every data-dependent transform is fit INSIDE the CV fold** — scaling, library-size/quantile normalization, ComBat/SVA, PCA/UMAP, imputation, AND feature selection. The discovery panel may be selected on all training data (that IS the deliverable), but the performance NUMBER must come from a pipeline that re-runs selection per fold. Selection is the dominant overfitting capacity in p>>n and gives near-perfect apparent accuracy on pure noise (Ambroise & McLachlan 2002).
3. **The locked test set is touched exactly once.** Every threshold, feature count, hyperparameter, and "best epoch" chosen on it leaks; when hyperparameters are tuned, use nested CV to report performance (Varma & Simon 2006).
4. **The metric is matched to the data regime, and calibration is separate from discrimination.** AUC for discrimination, AUPRC/MCC when imbalanced, and Brier + a reliability curve whenever risk estimates will be used — AUC is invariant to any monotone score transform, so it says nothing about calibration.

## Workflow Overview

```
Expression matrix + Metadata
    |
    v
[1. Data Preparation] -----> StandardScaler, train/test split
    |
    v
[2. Feature Selection] ----> Boruta or LASSO stability selection
    |
    v
[3. Model Training] -------> Pipeline with selection inside CV (leakage-safe)
    |
    v
[4. Model Interpretation] -> SHAP values, feature importance
    |
    v
[5. Validation] -----------> Hold-out test, bootstrap CI
    |
    v
Validated biomarker panel + classifier
```

## Step 1: Data Preparation

**Goal:** Load the matrix and hold out a GROUP-aware test set before anything is fit.

**Approach:** Split by the subject key so no subject appears in both train and test, then fit the scaler on training only; per-fold scaling is re-applied inside the CV pipeline in Step 3.

```python
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler

expr = pd.read_csv('expression.csv', index_col=0)
meta = pd.read_csv('metadata.csv', index_col=0)

X = expr.T  # samples x genes
# y must be 0/1: brier_score_loss and calibration_curve raise on string labels, and sklearn orders
# classes alphabetically -- for a case/control column that makes 'control' the positive class, so
# predict_proba[:, 1], the SHAP [:, :, 1] slice, and Brier all silently describe the wrong class.
# AUC is symmetric and will not expose the flip. Encode the disease class as 1 explicitly.
POSITIVE_CLASS = 'disease'
y = (meta.loc[X.index, 'condition'].values == POSITIVE_CLASS).astype(int)
# The critical key: the SUBJECT (patient/donor/site), not the sample. If truly one
# sample per subject, groups = X.index; otherwise it MUST be the subject id.
groups = meta.loc[X.index, 'subject_id'].values

# Group- AND class-aware hold-out: take one StratifiedGroupKFold fold as the test set so no
# subject spans train/test (train_test_split(stratify=y) alone would leak repeated subjects).
sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)   # 1/5 held out (~0.2)
train_idx, test_idx = next(sgkf.split(X, y, groups))
X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y[train_idx], y[test_idx]
groups_train = groups[train_idx]

# Fit scaler on training only to prevent data leakage
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

**QC Checkpoint 1:** Check class balance, sample counts, and group separation
- Minimum 10 samples per class recommended; classes reasonably balanced (ratio <3:1)
- Confirm NO subject id appears in both train and test (`set(groups[train_idx]) & set(groups[test_idx])` is empty)

## Step 2: Feature Selection

**Goal:** Produce the discovery panel (all-relevant with Boruta, or a stable minimal set with LASSO).

**Approach:** Optionally pre-filter, then run the selector and map the mask back to the full feature space for downstream indexing.

### Option A: Boruta (All-Relevant Selection)

```python
import numpy as np
from boruta import BorutaPy
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif

# Pre-filter if >10k features. selected_idx is a positional boolean mask aligned to X_train.columns.
if X_train_scaled.shape[1] > 10000:
    selector = SelectKBest(f_classif, k=5000)
    selector.fit(X_train_scaled, y_train)
    prefilter_idx = np.where(selector.get_support())[0]
    X_train_filt = X_train_scaled[:, prefilter_idx]
else:
    prefilter_idx = None
    X_train_filt = X_train_scaled

# max_depth=5: Shallow trees for stable importances
rf = RandomForestClassifier(n_estimators=100, max_depth=5, n_jobs=-1, random_state=42)
# max_iter=100: Usually sufficient; 200 if many tentative
boruta = BorutaPy(rf, n_estimators='auto', max_iter=100, random_state=42, verbose=0)
boruta.fit(X_train_filt, y_train)

# Map the (possibly pre-filtered) Boruta mask back onto the FULL feature space.
selected_idx = np.zeros(X_train.shape[1], dtype=bool)
selected_idx[prefilter_idx[boruta.support_] if prefilter_idx is not None else boruta.support_] = True
print(f'Selected {selected_idx.sum()} features')
```

### Option B: LASSO Stability Selection

```python
from sklearn.linear_model import LogisticRegressionCV
import numpy as np

# n_bootstrap=100: Quick; use 500 for publication
n_bootstrap = 100
stability_scores = np.zeros(X_train_scaled.shape[1])

for i in range(n_bootstrap):
    idx = np.random.choice(len(y_train), size=len(y_train), replace=True)
    # Cs=10: 10 regularization values to search
    model = LogisticRegressionCV(penalty='l1', solver='saga', Cs=10, cv=3, random_state=i, max_iter=1000)
    model.fit(X_train_scaled[idx], y_train[idx])
    stability_scores += (model.coef_[0] != 0).astype(int)

stability_scores /= n_bootstrap
# stability_threshold=0.6: Standard; 0.8 for strict
selected_idx = stability_scores > 0.6
print(f'Selected {selected_idx.sum()} features (stability >0.6)')
```

**QC Checkpoint 2:**
- Selected features: 5-200 range
- Too few (<5): lower threshold, increase iterations
- Too many (>200): increase threshold, add pre-filtering

## Step 3: Leakage-Safe Performance Estimation

**Goal:** Estimate performance without the selection-before-CV leakage that inflates AUC toward 1.0 even on noise.

**Approach:** The Step 2 selection produced the discovery panel (fit on all training data) -- that is fine for the final panel, but it must NOT be the data the performance number is computed on. Estimate performance with scaling and selection wrapped in a `Pipeline` so they re-fit inside each fold; for raw RNA-seq, do per-sample normalization outside the fold and gene scaling/selection inside it.

```python
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression

# Selection lives INSIDE the pipeline -> re-fit per fold, no leakage. Use the unscaled X_train.
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('select', SelectKBest(f_classif, k=min(50, X_train.shape[1]))),
    ('clf', LogisticRegression(max_iter=5000, class_weight='balanced')),
])
# Group-aware outer CV: pass groups_train so no subject spans a fold boundary.
outer_cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(pipe, X_train, y_train, groups=groups_train, cv=outer_cv, scoring='roc_auc')
print(f'Leakage-safe CV AUC: {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}')
# If hyperparameters are tuned, wrap a GridSearchCV (inner group CV) as the pipeline's estimator
# and report the OUTER cross_val_score -- flat CV that both tunes and reports is optimistic (Varma & Simon 2006).
```

**QC Checkpoint 3:**
- AUC reported with its fold spread, not a bare number (small-n CV is high-variance)
- Confirm selection is inside the pipeline and folds are group-aware; selection-before-CV inflates AUC toward 1.0 even on noise
- For imbalanced data report AUPRC/MCC, not accuracy; check the model predicts biology not batch (machine-learning/omics-classifiers)

## Step 4: Model Interpretation

**Goal:** Audit what the final model keys on, not select biomarkers.

**Approach:** Fit the final model on the discovery panel, then compute interventional SHAP against a background and aggregate over modules to catch shortcut/batch learning.

```python
import shap
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Fit the FINAL model on the discovery panel for interpretation and deployment.
sel = X_train.columns[selected_idx]
clf = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1).fit(X_train[sel], y_train)

# Interventional SHAP ('what the model uses') needs a background; set feature_perturbation
# explicitly because the 0.47+ 'auto' default flips the estimand on whether data= is given.
background = shap.utils.sample(X_train[sel], 100)
explainer = shap.TreeExplainer(clf, data=background, feature_perturbation='interventional')
shap_values = explainer(X_test[sel])
# RF returns one output per class in shap 0.47+ (n_samples, n_features, n_classes); keep the positive class.
if shap_values.values.ndim == 3:
    shap_values = shap_values[:, :, 1]
mean_shap = np.abs(shap_values.values).mean(axis=0)
```

**QC Checkpoint 4:**
- SHAP is an audit, not a selection method: use it to confirm the model is not keying on batch/housekeeping shortcuts (machine-learning/prediction-explanation)
- Aggregate SHAP over co-expression modules before ranking; within-module order is not a finding
- SHAP directions should be biologically plausible; treat top-SHAP genes as hypotheses, not a validated panel

## Step 5: Final Validation -- Discrimination AND Calibration

**Goal:** Report honest held-out performance, including calibration when risks will be used.

**Approach:** Report discrimination with an interval, but if the panel will produce risk estimates, also check calibration: AUC is invariant to any monotone transform of the score, so a high AUC says nothing about whether the probabilities are honest (machine-learning/model-validation). External validation on an independent cohort is the real bar.

```python
from sklearn.metrics import roc_auc_score
from sklearn.metrics import brier_score_loss
import numpy as np

y_prob = clf.predict_proba(X_test[sel])[:, 1]
test_auc = roc_auc_score(y_test, y_prob)

# Bootstrap CI for AUC (1000 resamples). Skip single-class resamples (roc_auc_score is nan there).
boot = []
for _ in range(1000):
    i = np.random.choice(len(y_test), len(y_test), replace=True)
    if len(np.unique(y_test[i])) == 2:
        boot.append(roc_auc_score(y_test[i], y_prob[i]))
ci_lower, ci_upper = np.percentile(boot, [2.5, 97.5])
print(f'Hold-out AUC: {test_auc:.3f}  95% CI [{ci_lower:.3f}, {ci_upper:.3f}]')
print(f'Brier score (calibration + refinement): {brier_score_loss(y_test, y_prob):.3f}')   # y must be 0/1-encoded; string labels raise unless pos_label is passed
# If risks will be used, recalibrate on a disjoint fold and report a reliability curve
# (machine-learning/model-validation); do not resample for imbalance -- it breaks calibration.
```

## Parameter Recommendations

| Step | Parameter | Recommendation |
|------|-----------|----------------|
| Split | n_splits (StratifiedGroupKFold) | 5 -> ~0.2 held out; lower n_splits for a larger test fraction |
| Boruta | max_iter | 100 (sufficient), 200 if tentative features |
| LASSO | n_bootstrap | 100 (quick), 500 for publication |
| LASSO | stability_threshold | 0.6 (standard), 0.8 for strict |
| Leakage-safe CV | folds | 5 (standard), 10 for small datasets; selection inside each fold |
| RF | n_estimators | 100-500 |
| XGBoost | learning_rate | 0.1 (conservative) |

## Common Errors

The leakage seams first (each silently inflates performance and a held-out set cannot detect it), then operational issues.

| Symptom | Cause | Fix |
|---------|-------|-----|
| Near-perfect CV AUC that collapses on external data | Features selected on the full dataset, then only the classifier CV'd | Wrap selection INSIDE the pipeline so it re-fits per fold (Ambroise & McLachlan 2002) |
| Optimistic AUC despite in-fold selection | Scaler/ComBat/PCA/imputation fit on all data before the split | Fit every data-dependent transform inside the fold (Pipeline) |
| Great CV, poor real-world performance | Repeated subjects (biopsies/longitudinal/replicates) split across train/test | Split by subject with StratifiedGroupKFold; the unit is the donor, not the sample |
| Reported AUC higher than any real fold | Same CV used to tune hyperparameters AND report | Nest: inner CV tunes, outer CV reports (Varma & Simon 2006) |
| Good AUC but risk estimates are miscalibrated | Resampling (SMOTE/undersampling) for imbalance, or AUC used as the only metric | Report AUPRC/MCC + Brier; recalibrate on a disjoint fold; do not resample-then-report calibration |
| No features selected | Too strict threshold | Lower stability threshold, increase iterations |
| Too many features (>200) | Noisy data | Add pre-filtering, increase regularization |
| Low CV AUC (<0.6) | No signal, low power | Check data quality, add samples |
| High variance across folds | Small sample size | Repeated stratified k-fold with an interval (LOOCV is degenerate for AUC) |
| SHAP features differ from selected | Correlated features split credit; attribution describes the model | Aggregate over modules; do not expect SHAP to match selection |

## Export Results

```python
import pandas as pd
import joblib

# Save biomarker panel
feature_names = X_train.columns[selected_idx].tolist()
pd.DataFrame({'feature': feature_names}).to_csv('biomarker_panel.csv', index=False)

# Save model and scaler for deployment
joblib.dump(clf, 'biomarker_classifier.joblib')
joblib.dump(scaler, 'feature_scaler.joblib')
```

## Related Skills

- database-access/geo-data - Public expression cohorts for validation sets
- database-access/sra-data - Pull raw FASTQ for re-quantified validation cohorts
- database-access/uniprot-access - Protein-level features (sequence, GO terms, PTMs) for protein biomarkers
- machine-learning/biomarker-discovery - Detailed feature selection methods
- machine-learning/model-validation - Nested CV implementation details
- machine-learning/omics-classifiers - Classifier options and tuning
- machine-learning/prediction-explanation - SHAP and LIME interpretation
- differential-expression/de-results - Pre-filter with DE genes
- pathway-analysis/go-enrichment - Functional enrichment of biomarkers

## References

- Ambroise C, McLachlan GJ (2002) Selection bias in gene extraction on the basis of microarray gene-expression data. *PNAS* 99:6562-6566. DOI 10.1073/pnas.102102699. (feature selection must be inside the CV fold.)
- Varma S, Simon R (2006) Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics* 7:91. DOI 10.1186/1471-2105-7-91. (nested CV for unbiased performance.)
- Whalen S, Schreiber J, Noble WS, Pollard KS (2022) Navigating the pitfalls of applying machine learning in genomics. *Nature Reviews Genetics* 23:169-181. DOI 10.1038/s41576-021-00434-9. (genomics-specific leakage and distribution-shift pitfalls.)
- Kapoor S, Narayanan A (2023) Leakage and the reproducibility crisis in machine-learning-based science. *Patterns* 4:100804. DOI 10.1016/j.patter.2023.100804. (a taxonomy of leakage, including group leakage.)
<!-- END FILE: workflows/biomarker-pipeline/SKILL.md -->

## 子目录：workflows/causal-genomics-pipeline

<!-- BEGIN FILE: workflows/causal-genomics-pipeline/SKILL.md -->
---
name: bio-workflows-causal-genomics-pipeline
description: End-to-end post-GWAS causal inference pipeline orchestrating heritability partitioning, genetic correlation, Mendelian randomization with CHP-aware sensitivity (CAUSE / LHC-MR), colocalization, fine-mapping with SuSiE / FOCUS, mediation, TWAS triangulation, cis-pQTL drug-target MR, effector-gene prioritization (L2G / PoPS / cS2G), and GenomicSEM common-factor GWAS. Use when triangulating causal inference across multiple complementary methods, prioritizing tissues via stratified LDSC, nominating or de-risking drug targets, mapping a lead SNP to a candidate effector gene, modeling shared genetic architecture across correlated traits, or producing a STROBE-MR-compliant publication-grade evidence battery from GWAS summary statistics.
tool_type: r
primary_tool: TwoSampleMR
workflow: true
depends_on:
  - causal-genomics/mendelian-randomization
  - causal-genomics/colocalization-analysis
  - causal-genomics/fine-mapping
  - causal-genomics/pleiotropy-detection
  - causal-genomics/mediation-analysis
  - causal-genomics/transcriptome-wide-association
  - causal-genomics/heritability-partitioning
  - causal-genomics/proteome-mr-drug-target
  - causal-genomics/effector-gene-prioritization
  - causal-genomics/genetic-correlation
  - causal-genomics/genomic-sem
qc_checkpoints:
  - after_h2_ldsc: "Mean chi-squared > 1.02; h2 SE < 0.02; intercept ratio < 0.3"
  - after_rg_check: "If abs(rg) > 0.3 then CHP suspected and CAUSE/LHC-MR required"
  - after_instrument_selection: "F-statistic > 10 (two-sample) or > 20 (one-sample); no palindromic SNPs at MAF near 0.5"
  - after_mr: "IVW + Egger + weighted median + weighted mode concordance"
  - after_sensitivity: "MR-PRESSO global p, Egger intercept p (with Isq >= 0.9 for NOME), Steiger directionality"
  - after_chp_check: "CAUSE delta_elpd z > 1.96 OR LHC-MR posterior excludes null"
  - after_coloc: "PP.H4 >= 0.7 triangulation, >= 0.8 publication, >= 0.95 industry; p12 sensitivity stable"
  - after_finemapping: "Credible-set purity (min_abs_corr) >= 0.5; estimate_s_rss lambda < 0.05 if external LD"
  - after_twas: "FOCUS PIP >= 0.8 for candidate causal gene; tissue selected via stratified LDSC"
  - after_effector_gene: "L2G + PoPS + coloc + TWAS concordance >= 3 of 6 evidence streams"
  - after_mediation: "rho_crit > 0.3 OR mediational E-value > 2 (Imai sensitivity)"
---

## Version Compatibility

Reference examples tested with: TwoSampleMR 0.5+, MR-PRESSO 1.0+, coloc 5.2+, susieR 0.12+, MendelianRandomization 0.9+, ldsc 1.0.1 (python3 fork), MetaXcan 0.7+, pyfocus 0.6+, MAGMA 1.10+, MRlap 0.0.3+, cause 1.2+, lhcMR 0.0.0.9000+, HDL 1.4+, LAVA 0.1+, GenomicSEM 0.0.5+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <pkg>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Causal Genomics Pipeline

**"Run post-GWAS causal inference from summary statistics"** -> Orchestrate heritability partitioning and tissue prioritization, genetic-correlation diagnostics, instrument selection, Mendelian randomization with CHP-aware sensitivity, colocalization, fine-mapping (SuSiE / FOCUS), mediation, TWAS triangulation, cis-pQTL drug-target MR, effector-gene prioritization, and (optionally) GenomicSEM common-factor GWAS to triangulate causal evidence and nominate publication-grade causal exposures, genes, and mechanisms.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

A causal claim is decided at the seams where summary statistics meet, not inside any single method.

1. **Everything shares ONE genome build, and effect alleles are harmonized once.** The exposure and outcome sumstats, the LD reference, and any eQTL/pQTL panel must share a build; if they differ, liftover ONCE, strand-aware (the BBIS inverted-region danger), BEFORE harmonization. `harmonise_data` aligns effect alleles; a flipped palindrome (MAF near 0.5) flips the causal-effect SIGN silently — drop intermediate-frequency palindromes.
2. **The LD reference ancestry must match the GWAS ancestry, committed once and inherited by clumping, coloc.susie, fine-mapping (SuSiE-rss), and TWAS.** A mismatched LD panel corrupts credible sets and colocalization silently; the in-pipeline alarms are `estimate_s_rss` lambda <0.05 and credible-set purity `min_abs_corr` >=0.5.
3. **Order is causal: a diagnostic at step 0 decides whether a later step runs.** Cross-trait LDSC `abs(rg)>0.3` makes correlated horizontal pleiotropy (CHP) suspected, so CAUSE/LHC-MR becomes MANDATORY — MR-PRESSO is BLIND to CHP. Tissue picked at step 0 (stratified LDSC) flows into TWAS; picking it post-hoc is circular. Steiger pre-filter directionality and LD-clump BEFORE coloc/fine-mapping.
4. **Triangulate; refuse the single number.** No single MR estimator, coloc PP.H4, or evidence stream is decisive — report IVW+Egger+median+mode concordance, coloc PP.H4 with a p12 sweep, and effector-gene evidence across >=3 of 6 streams. A bare headline statistic hides the seam.

## Pipeline Overview

```
GWAS Summary Statistics (exposure + outcome)
    |
    v
[0. Pre-flight: h2 + tissue prioritization + rg diagnostic]
    LDSC / S-LDSC baseline-LD / Finucane 2018 cell-type
    Cross-trait LDSC / HDL / LAVA --> if abs(rg) > 0.3 then CHP-aware MR required
    |
    v
[1. Instrument Selection] -----> LD clumping, F-stat filtering, Steiger pre-filter
    |
    v
[2. Mendelian Randomization] --> IVW, MR-Egger, Weighted Median/Mode, MR-RAPS
    |
    +--> [3. Sensitivity] -------> MR-PRESSO, Egger intercept (Isq), leave-one-out, Steiger
    |
    +--> [3b. CHP-aware MR] -----> CAUSE (delta_elpd), LHC-MR posterior (if rg > 0.3)
    |
    v
[4. Colocalization] -----------> coloc.abf / coloc.susie / HyPrColoc / SMR-HEIDI
    |
    v
[5. Fine-Mapping] -------------> SuSiE rss + estimate_s_rss / FINEMAP-inf / PolyFun
    |
    v
[6. Mediation Analysis] -------> Network MR / MVMR / CMAverse 4-way
    |
    +--> [7. TWAS triangulation] -> FUSION / S-PrediXcan / FOCUS PIP >= 0.8
    |
    +--> [8. Cis-pQTL drug-target MR] -> UKB-PPP / deCODE + cross-platform replication
    |
    v
[9. Effector-gene prioritization] -> Open Targets L2G + PoPS + cS2G + coloc + TWAS (>= 3 of 6 evidence)
    |
    v
[10. (optional) GenomicSEM common-factor GWAS] -> factor model + Q_SNP
    |
    v
Triangulated causal-evidence summary across methods
```

## Step 0: Pre-flight - Heritability, Tissue Prioritization, Genetic Correlation

```bash
ldsc.py --h2 trait.sumstats.gz --ref-ld-chr eur_w_ld_chr/ --w-ld-chr eur_w_ld_chr/ --out trait.h2
ldsc.py --h2-cts trait.sumstats.gz --ref-ld-chr baselineLD. --ref-ld-chr-cts Multi_tissue_gene_expr.ldcts --w-ld-chr weights. --out trait.cts
ldsc.py --rg trait1.sumstats.gz,trait2.sumstats.gz --ref-ld-chr eur_w_ld_chr/ --w-ld-chr eur_w_ld_chr/ --out rg
```

**Goal:** Confirm heritable signal, pick the right tissue for TWAS / V2G, and detect shared heritable confounding that mandates CHP-aware MR (CAUSE / LHC-MR).

**Reconciliation:** S-LDSC mean chi-squared > 1.02 with h2 SE < 0.02 and intercept ratio < 0.3 is required. Cell-type prioritization with coefficient_p < 0.05 / N_tissues nominates the tissue for downstream TWAS weights and ABC enhancer-gene priors. If cross-trait LDSC abs(rg) > 0.3 (and HDL sample-overlap < 5%), Step 3b becomes mandatory. See causal-genomics/heritability-partitioning and causal-genomics/genetic-correlation.

## Step 1: Instrument Selection

```r
library(TwoSampleMR)
exposure_dat <- read_exposure_data(filename = 'exposure_gwas.tsv', sep = '\t',
    snp_col = 'SNP', beta_col = 'BETA', se_col = 'SE',
    effect_allele_col = 'A1', other_allele_col = 'A2',
    eaf_col = 'EAF', pval_col = 'P')
exposure_dat <- subset(exposure_dat, pval.exposure < 5e-8)
exposure_dat <- clump_data(exposure_dat, clump_r2 = 0.001, clump_kb = 10000)
exposure_dat$F_stat <- (exposure_dat$beta.exposure / exposure_dat$se.exposure)^2
exposure_dat <- subset(exposure_dat, F_stat >= 10)
exposure_dat <- subset(exposure_dat, !(eaf.exposure > 0.42 & eaf.exposure < 0.58 & substr(effect_allele.exposure,1,1) %in% c('A','T') & substr(other_allele.exposure,1,1) %in% c('A','T')))
```

For cis-MR (drug target) use clump_r2 = 0.1 within +/- 500 kb of the gene. Use 5e-9 if M > 5M variants tested.

## Step 2: Mendelian Randomization

```r
outcome_dat <- read_outcome_data(filename = 'outcome_gwas.tsv', sep = '\t',
    snp_col = 'SNP', beta_col = 'BETA', se_col = 'SE',
    effect_allele_col = 'A1', other_allele_col = 'A2',
    eaf_col = 'EAF', pval_col = 'P')
dat <- harmonise_data(exposure_dat, outcome_dat)
mr_results <- mr(dat, method_list = c('mr_ivw', 'mr_egger_regression',
    'mr_weighted_median', 'mr_weighted_mode'))
```

Concordance across IVW, Egger, weighted median, and weighted mode is the headline causal claim. See causal-genomics/mendelian-randomization.

## Step 3: Sensitivity Analysis

```r
library(MRPRESSO)
presso <- mr_presso(BetaOutcome = 'beta.outcome', BetaExposure = 'beta.exposure',
    SdOutcome = 'se.outcome', SdExposure = 'se.exposure',
    OUTLIERtest = TRUE, DISTORTIONtest = TRUE, data = dat,
    NbDistribution = 5000, SignifThreshold = 0.05)
egger_int <- mr_pleiotropy_test(dat)
isq <- Isq(abs(dat$beta.exposure), dat$se.exposure)   # I^2_GX needs same-sign effects; pass abs(beta)
het <- mr_heterogeneity(dat)
loo <- mr_leaveoneout(dat)
steiger <- directionality_test(dat)
```

Isq >= 0.9 is required for the MR-Egger NOME assumption; below that, run SIMEX correction or drop Egger. See causal-genomics/pleiotropy-detection.

## Step 3b: CHP-aware MR (when rg > 0.3 or shared confounder suspected)

```r
library(cause)
library(lhcMR)
cause_fit <- cause(X = cause_dat, variants = top_vars, param_ests = params)
elpd <- summary(cause_fit)$elpd
# lhcMR is a 3-call chain: merge_sumstats (takes LD/rho paths) -> calculate_SP -> lhc_mr
lhc_df <- merge_sumstats(input.files, trait.names, LD.filepath = ld_path, rho.filepath = rho_path)
SP_list <- calculate_SP(lhc_df, trait.names, nStep = 2, SP_single = 3, SP_pair = 50)
lhc_fit <- lhc_mr(SP_list, trait.names, paral_method = 'lapply', nBlock = 200)
```

CAUSE reports delta_elpd of sharing-vs-causal model; z > 1.96 favors true causation over CHP. LHC-MR jointly estimates causal effect and confounder effect via likelihood; the 95% credible interval excluding zero is the causal-effect verdict. Required when LDSC abs(rg) > 0.3. See causal-genomics/pleiotropy-detection.

## Step 4: Colocalization

```r
library(coloc)
d1 <- list(beta = exposure_locus$BETA, varbeta = exposure_locus$SE^2,
    snp = exposure_locus$SNP, position = exposure_locus$BP,
    type = 'quant', N = exposure_n, MAF = exposure_locus$EAF)
d2 <- list(beta = outcome_locus$BETA, varbeta = outcome_locus$SE^2,
    snp = outcome_locus$SNP, position = outcome_locus$BP,
    type = 'cc', N = outcome_n, s = case_fraction, MAF = outcome_locus$EAF)
result <- coloc.abf(d1, d2, p1 = 1e-4, p2 = 1e-4, p12 = 1e-5)
sens <- coloc::sensitivity(result, rule = 'H4 > 0.7')
```

PP.H4 >= 0.7 for triangulation, >= 0.8 for publication, >= 0.95 for industry-grade target packages. Always sweep p12 over 1e-6 to 5e-5; conclusions must be stable across the sweep. For allelic heterogeneity use coloc.susie. See causal-genomics/colocalization-analysis.

## Step 5: Fine-Mapping with SuSiE

```r
library(susieR)
R <- as.matrix(read.csv('ld_matrix.csv', row.names = 1))
diag_s <- estimate_s_rss(z = locus_stats$BETA / locus_stats$SE, R = R, n = sample_size)
fitted <- susie_rss(bhat = locus_stats$BETA, shat = locus_stats$SE,
    R = R, n = sample_size, L = 10, coverage = 0.95, min_abs_corr = 0.5)
cs <- fitted$sets$cs
```

If `estimate_s_rss` lambda > 0.05 the external LD is mismatched; rerun with in-sample LD or use SuSiE-inf / FINEMAP-inf. min_abs_corr >= 0.5 (r-squared >= 0.25) is the purity threshold for retaining a credible set. For HLA use L = 20-30. See causal-genomics/fine-mapping.

## Step 6: Mediation Analysis

```r
library(TwoSampleMR)
mv_exposures <- mv_extract_exposures(c('ieu-a-2', 'ieu-a-1089'))
mv_outcome <- extract_outcome_data(mv_exposures$SNP, 'ieu-a-7')
mvdat <- mv_harmonise_data(mv_exposures, mv_outcome)
mvmr_result <- mv_multiple(mvdat)
```

Indirect effect = total - direct. For molecular mediators (expression, methylation, protein), prefer two-step MR with cis-instruments at the mediator. Run Imai sensitivity (rho_crit) or mediational E-value > 2. See causal-genomics/mediation-analysis.

## Step 7: TWAS Triangulation

```bash
python MetaXcan/SPrediXcan.py --model_db_path mashr_Whole_Blood.db \
    --covariance mashr_Whole_Blood.txt.gz --gwas_file gwas.txt.gz \
    --snp_column SNP --effect_allele_column A1 --non_effect_allele_column A2 \
    --beta_column BETA --se_column SE --pvalue_column P \
    --output_file twas.csv
focus finemap gwas.sumstats.gz 1000G.EUR.QC.1 mashr.db --chr 1 --p-threshold 5e-8 --out twas.focus
```

**Goal:** Nominate gene-level causal hits and prune LD-induced TWAS false positives.

Tissue is picked from Step 0 stratified LDSC; Bonferroni at 0.05 / N_tissues. FOCUS PIP >= 0.8 retains a single candidate causal gene per region; without FOCUS, co-regulated TWAS hits cannot be distinguished. Cross-reference TWAS hits with coloc.susie PP.H4 and cis-eQTL MR for triangulation. See causal-genomics/transcriptome-wide-association.

## Step 8: Cis-pQTL Drug-Target MR

```r
library(TwoSampleMR)
pqtl_dat <- extract_instruments(outcomes = 'prot-a-XXX', p1 = 5e-8, clump = TRUE,
    r2 = 0.1, kb = 1000)
pqtl_dat <- subset(pqtl_dat, chr.exposure == target_chr & pos.exposure > target_tss - 500000 & pos.exposure < target_tss + 500000)   # extract_instruments returns chr.exposure/pos.exposure
out_dat <- extract_outcome_data(snps = pqtl_dat$SNP, outcomes = c('ieu-a-7', 'ieu-b-31'))
dat <- harmonise_data(pqtl_dat, out_dat)
mr_results <- mr(dat, method_list = c('mr_ivw', 'mr_wald_ratio'))
```

**Goal:** Mimic pharmacological inhibition of a drug target via cis-pQTL and triangulate with coloc.

Cross-platform replication on Olink (UKB-PPP) and SomaScan (deCODE) is mandatory; the two platforms are concordant for ~60% of proteins and discordant calls are platform artifacts. Run pheWAS for on-target adverse effects, PAV-excluded sensitivity, and coloc.susie PP.H4 >= 0.8 at the cis-pQTL locus. See causal-genomics/proteome-mr-drug-target.

## Step 9: Effector-Gene Prioritization

```bash
magma --bfile g1000_eur --pval gwas.tsv N=N --gene-annot genes.annot --out trait
python munge_feature_directory.py --gene_annot_path genes.txt --feature_dir features/ --save_prefix pops
python pops.py --gene_annot_path genes.txt --feature_mat_prefix pops --num_feature_chunks 2 --magma_prefix trait --out_prefix trait.pops
```

**Goal:** Map each fine-mapped credible set to a candidate effector gene by integrating six evidence streams.

Integrate: (1) Open Targets L2G (Mountjoy 2021), (2) PoPS similarity score (Weeks 2023), (3) cS2G combined SNP-to-gene (Gazal 2022), (4) coloc.susie PP.H4 with eQTL/pQTL, (5) FOCUS TWAS PIP, (6) ABC / ENCODE-rE2G enhancer-gene linking. Require >= 3 of 6 concordant evidence streams for high-confidence claim. L2G and PoPS disagree by design (different feature regimes); report both. See causal-genomics/effector-gene-prioritization.

## Step 10 (optional): GenomicSEM Common-Factor GWAS

```r
library(GenomicSEM)
ldsc_output <- ldsc(traits = c('t1.sumstats.gz','t2.sumstats.gz','t3.sumstats.gz'),
    sample.prev = c(NA, NA, NA), population.prev = c(NA, NA, NA),
    ld = ld_path, wld = ld_path, trait.names = c('t1','t2','t3'))
model <- 'F1 =~ NA*t1 + t2 + t3\nF1 ~~ 1*F1'
fit <- usermodel(ldsc_output, model = model, estimation = 'DWLS')
factor_gwas <- userGWAS(covstruc = ldsc_output, SNPs = sumstats_combined,
    model = paste0(model, '\nF1 ~ SNP\nt1 + t2 + t3 ~ 0*SNP'),
    estimation = 'DWLS', sub = c('F1~SNP'))
```

Heywood cases (negative residual variance) require fixing residuals positive or dropping the indicator. Verify CFI > 0.95 and RMSEA < 0.06. Q_SNP p > 0.05 confirms factor-level (not trait-specific) signal. See causal-genomics/genomic-sem.

## Parameter Recommendations

| Step | Parameter | Recommendation |
|------|-----------|----------------|
| Instruments | p-value | 5e-8 standard; 5e-9 if M > 5M variants tested |
| Instruments | F-statistic | >= 10 two-sample; >= 20 one-sample |
| Instruments | clump_r2 | 0.001 polygenic; 0.1 cis-MR |
| Instruments | clump_kb | 10000 (10 Mb) |
| Coloc | p12 prior | 1e-5 standard; 5e-6 conservative; 1e-6 trans-eQTL |
| Coloc | PP.H4 | >= 0.7 triangulation; >= 0.8 publication; >= 0.95 industry |
| SuSiE | L | 10 default; 20-30 HLA |
| SuSiE | coverage | 0.95 standard; 0.9 if N < 1000 |
| SuSiE | min_abs_corr | 0.5 default (r-squared >= 0.25) |
| MR-PRESSO | NbDistribution | 1000 exploratory; >= 5000 publication; >= 10000 stringent |
| TWAS | FOCUS PIP | >= 0.8 candidate causal gene |
| TWAS | tissue Bonferroni | 0.05 / N_tissues (~2.5e-4 for 200 tissues) |
| LDSC | mean chi-squared | > 1.02 for h2 interpretability |
| LDSC | rg trigger for CHP-MR | abs(rg) > 0.3 |
| LDSC | HDL sample overlap | < 5% |

## Common Errors

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Nonsense / sign-flipped MR or coloc | Build/liftover mismatch across exposure/outcome/LD/eQTL | One build; liftover once strand-aware (BBIS danger), THEN harmonize |
| Causal-effect sign flipped | Strand-flip/allele-swap at a MAF~0.5 palindrome in harmonise | Drop intermediate-frequency palindromes; verify effect-allele alignment |
| Corrupted credible sets / wrong coloc | LD-panel ancestry mismatch (clumping/coloc/fine-map/TWAS) | Ancestry-matched LD; check estimate_s_rss lambda; prefer in-sample LD |
| "Causal" effect passes sensitivity but is confounded | MR-PRESSO blind to CHP; rg>0.3 not checked | Run the rg gate at step 0; CAUSE/LHC-MR when triggered |
| Two-sample MR biased toward observational | Sample overlap between exposure and outcome GWAS | Check overlap (<5% via HDL); MRlap/HDL correction |
| No instruments | Underpowered GWAS | Relax p-value to 5e-6 with caution |
| Weak instruments (F < 10) | Small effect SNPs | Drop weak instruments; use better-powered GWAS |
| Inconsistent MR methods | Pleiotropy | Check MR-PRESSO outliers; use weighted median |
| Egger intercept p < 0.05 | Directional pleiotropy | Report Egger estimate; check Isq >= 0.9 |
| PP.H3 > PP.H4 | Different causal variants | Use coloc.susie for allelic heterogeneity |
| No credible sets | LD matrix issues | Check estimate_s_rss lambda; use in-sample LD |
| Steiger reverse direction | Reverse causation | Run bidirectional MR; pre-filter on Steiger |
| MR-PRESSO blind to apparent confounder | Correlated horizontal pleiotropy | Run CAUSE or LHC-MR (see pleiotropy-detection) |
| TWAS hit at gene-dense locus | LD-induced false positive | Run FOCUS fine-mapping; require PIP >= 0.8 |
| Cis-pQTL MR positive, replication fails | Olink/SomaScan platform discordance | Cross-platform replication; PAV-excluded sensitivity |
| L2G + PoPS disagree | Different feature regimes | Report both; require concordance for high-confidence claim |
| Q_SNP heterogeneity in common-factor GWAS | Factor mis-specification | userGWAS with per-trait paths; report Q_pval |

## Related Skills

- causal-genomics/mendelian-randomization - IVW, Egger, MR-RAPS, MVMR
- causal-genomics/colocalization-analysis - coloc.abf, coloc.susie, HyPrColoc, SMR-HEIDI
- causal-genomics/fine-mapping - SuSiE rss, FINEMAP-inf, PolyFun, SuSiEx
- causal-genomics/pleiotropy-detection - MR-PRESSO, CAUSE, LHC-MR, contamination-mixture
- causal-genomics/mediation-analysis - Two-step MR, MVMR, CMAverse 4-way, HIMA
- causal-genomics/transcriptome-wide-association - FUSION, S-PrediXcan, FOCUS, UTMOST
- causal-genomics/heritability-partitioning - LDSC, S-LDSC, LDAK, HDL, HESS
- causal-genomics/proteome-mr-drug-target - UKB-PPP, deCODE, cis-pQTL MR, pheWAS
- causal-genomics/effector-gene-prioritization - L2G, PoPS, cS2G, MAGMA, FLAMES
- causal-genomics/genetic-correlation - Cross-trait LDSC, HDL, LAVA, Popcorn
- causal-genomics/genomic-sem - Common-factor GWAS, Q_SNP, MTAG reconciliation
- population-genetics/association-testing - Upstream GWAS methods
- atac-seq/enhancer-gene-linking - ABC / ENCODE-rE2G priors for effector-gene step
- single-cell/preprocessing - scRNA / scATAC tissue priors for stratified LDSC
- workflows/gwas-pipeline - Upstream: produces the sumstats (CHR/POS/EA/OA/EAF/BETA/SE/P/N, build documented) this pipeline consumes

## References

- Hemani G, Zheng J, Elsworth B, et al (2018) The MR-Base platform supports systematic causal inference across the human phenome. *eLife* 7:e34408. DOI 10.7554/eLife.34408. (TwoSampleMR / harmonisation.)
- Giambartolomei C, Vukcevic D, Schadt EE, et al (2014) Bayesian test for colocalisation between pairs of genetic association studies using summary statistics. *PLoS Genetics* 10:e1004383. DOI 10.1371/journal.pgen.1004383. (coloc.)
- Wang G, Sarkar A, Carbonetto P, Stephens M (2020) A simple new approach to variable selection in regression, with application to genetic fine mapping. *Journal of the Royal Statistical Society Series B* 82:1273-1300. DOI 10.1111/rssb.12388. (SuSiE.)
- Bulik-Sullivan BK, Loh PR, Finucane HK, et al (2015) LD Score regression distinguishes confounding from polygenicity in genome-wide association studies. *Nature Genetics* 47:291-295. DOI 10.1038/ng.3211. (LDSC intercept.)
<!-- END FILE: workflows/causal-genomics-pipeline/SKILL.md -->

## 子目录：workflows/chipseq-pipeline

<!-- BEGIN FILE: workflows/chipseq-pipeline/SKILL.md -->
---
name: bio-workflows-chipseq-pipeline
description: Orchestrates the end-to-end ChIP-seq pipeline from FASTQ to blacklist-filtered, annotated peaks, chaining fastp QC, Bowtie2 alignment, pre-dedup library-complexity QC (NRF/PBC), duplicate removal, chrM + ENCODE-blacklist filtering, MACS3 peak calling against a matched input, IDR/consensus reproducibility, deepTools signal tracks, and ChIPseeker annotation. Use when committing the reference build + blacklist version + effective genome size once, pairing each IP with its matched control, computing complexity metrics BEFORE dedup, choosing narrow vs broad and MACS3 vs SEACR/Genrich, keeping per-replicate peaks for IDR, or avoiding depth-normalization that erases a spike-in global shift. Hands mechanism to the chip-seq component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: MACS3
workflow: true
depends_on:
  - read-qc/fastp-workflow
  - read-alignment/bowtie2-alignment
  - alignment-files/duplicate-handling
  - chip-seq/chipseq-qc
  - chip-seq/peak-calling
  - chip-seq/peak-annotation
  - chip-seq/differential-binding
  - chip-seq/chipseq-visualization
  - chip-seq/motif-analysis
qc_checkpoints:
  - after_qc: "Q30 >85%, adapter content <5%"
  - after_alignment: "Mapping rate >80%, unique mapping >70%"
  - before_dedup: "NRF >0.8, PBC1 >0.8 (computed on the PRE-dedup BAM; after dedup the metric is meaningless)"
  - after_peaks: "FRiP >1% (TF) or >5% (sharp histone; broad marks run lower); NSC >1.05; RSC >0.8; fingerprint separates IP from input"
  - after_idr: "IDR rescue ratio max(Np,Nt)/min and self-consistency ratio max(N1,N2)/min both <=2 (ENCODE); IDR run on PER-REPLICATE peaks"
---

## Version Compatibility

Reference examples tested with: Bowtie2 2.5.3+, MACS3 3.0+, HOMER 4.11+, bedtools 2.31+, deepTools 3.5+, fastp 0.23+, samtools 1.19+, ChIPseeker 1.38+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: `macs3 callpeak -f BAMPE` uses real fragment lengths and IGNORES `--shift/--extsize/--nomodel` (those apply to single-end `-f BAM`); the `-g` shortcut (`hs/mm`) sets the effective genome size and must match the build/read length. Confirm in-tool before quoting.

# ChIP-seq Pipeline

**"Process my ChIP-seq data from FASTQ to annotated peaks"** -> Chain QC/trim, alignment, pre-dedup complexity QC, dedup + blacklist filtering, control-matched peak calling, reproducibility, signal tracks, and annotation.
- CLI + R: fastp -> bowtie2 -> (NRF/PBC pre-dedup) -> samtools markdup -> chrM/blacklist filter -> macs3 callpeak (IP vs input) -> IDR -> bamCoverage -> ChIPseeker

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

A ChIP-seq peakset is decided at four seams, not inside the caller.

1. **The reference build + blacklist version + effective genome size is one coordinate commitment made once and inherited by everything downstream** — peak coordinates, signal-track scaling, and every overlap. Blacklist filtering is a committed pipeline step, not optional cleanup: ENCODE-blacklisted regions (satellite/rDNA/high-signal artifacts) produce reproducible false peaks in every dataset regardless of biology, so they are removed before calling (Amemiya 2019).
2. **An IP is only interpretable against its matched control — the control IS the enrichment background.** Calling peaks without the right input/IgG fabricates peaks at open/accessible and copy-number-amplified regions. Pair each IP with its control at the calling step.
3. **Library-complexity QC (NRF/PBC1/PBC2) is computed on the PRE-dedup BAM.** After `markdup -r` the duplicates are gone, so computing complexity afterward reads ~1.0 and is meaningless. Compute it on the filtered, position-sorted BAM before removing duplicates.
4. **Normalization must not silently undo the experiment.** deepTools RPKM/CPM rescales every library to the same depth, which ERASES a spike-in global-shift signal (the whole point of ChIP-Rx). For spike-in experiments use `--scaleFactor` + `--normalizeUsing None`; for standard experiments RPKM/CPM is fine (chip-seq/spike-in-normalization).

Reproducibility corollary: pool replicates for a consensus peakset, but keep PER-REPLICATE peaks — IDR needs individual replicates plus pooled pseudo-replicates; running IDR on an already-pooled peakset is not IDR.

## Pipeline map

```
FASTQ (IP + matched Input, replicates)
  | [1] QC & trim -----------------> fastp                (read-qc/fastp-workflow)
  v
  | [2] Align ---------------------> bowtie2 (-q30 unique) (read-alignment/bowtie2-alignment)
  v     ^-- commitment: build + blacklist version + effective genome size
  | [3] Complexity QC (PRE-dedup) -> NRF/PBC1/PBC2         (chip-seq/chipseq-qc)
  v
  | [4] Dedup + filter ------------> markdup -r; drop chrM; SUBTRACT ENCODE blacklist  (alignment-files/duplicate-handling)
  v
  | [5] Peak calling (IP vs input)-> macs3 callpeak (narrow | --broad)  (chip-seq/peak-calling)
  v     ^-- keep PER-REPLICATE peaks for IDR
  | [6] Reproducibility -----------> IDR (per-rep + pooled pseudo-reps)  (chip-seq/peak-calling)
  v
  | [7] Signal tracks -------------> bamCoverage (RPKM | spike-in scaleFactor)  (chip-seq/chipseq-visualization)
  v
  | [8] QC + Annotate -------------> FRiP/NSC/RSC/fingerprint; ChIPseeker  (chip-seq/chipseq-qc, peak-annotation)
  v
Blacklist-filtered, annotated, reproducible peaks
```

## Made-once commitments

| Commitment | Choice | Consequence inherited downstream |
|------------|--------|----------------------------------|
| Build + blacklist + effective genome size | One genome build; the matching ENCODE blacklist BED; `-g hs/mm`/numeric | Mixed builds mis-place peaks; skipping the blacklist plants reproducible false peaks; wrong `-g` mis-scales p-values |
| Control pairing | Each IP has its input/IgG | No control => peaks at open chromatin / CN-amplified loci |
| Peak shape | Narrow (TF, H3K4me3, H3K27ac) vs broad (H3K27me3, H3K36me3, H3K9me3) | Broad marks called with narrow settings fragment into many small peaks |
| Fragment model | PE: `-f BAMPE` (real fragments); SE: `-f BAM` + `--nomodel --extsize` from predictd/xcorr | BAMPE silently ignores `--shift/--extsize` |

## The canonical order and why

1. **QC/trim** (fastp) both IP and input.
2. **Align** (bowtie2), keep uniquely-mapped (`samtools view -q 30`), coordinate-sort.
3. **Compute NRF/PBC1/PBC2 on the PRE-dedup BAM** — order-trap: after dedup they are meaningless.
4. **Mark/remove duplicates** (collate -> fixmate -m -> sort -> markdup -r), then **drop chrM** and **subtract the ENCODE blacklist** — order-trap: skipping the blacklist leaves reproducible artifact peaks.
5. **Call peaks against the matched control** (narrow or `--broad`).
6. **IDR on per-replicate peaks** (+ pooled pseudo-replicates) — order-trap: IDR on a pooled peakset is not IDR.
7. **Signal tracks** — RPKM/CPM for standard; `--scaleFactor` + `--normalizeUsing None` for spike-in (order-trap: RPKM erases the spike-in global shift).
8. **QC (FRiP/NSC/RSC/fingerprint) and annotate** (ChIPseeker).

## Choosing the caller and peak shape

Pipeline-level selection only; mechanism lives in the component skills.

| Fork | Lean toward | Hand off to |
|------|-------------|-------------|
| Caller | MACS3 (standard IP+input); SEACR (CUT&RUN/CUT&Tag, low background); Genrich (some ChIP/ATAC, built-in blacklist/replicate handling) | chip-seq/peak-calling, chip-seq/cut-and-run-tag |
| Narrow vs broad | Narrow: TFs, H3K4me3, H3K27ac. Broad (`--broad --broad-cutoff 0.1`): H3K27me3, H3K36me3, H3K9me3 | chip-seq/peak-calling |
| Reproducibility | ENCODE IDR (per-rep + pooled pseudo-reps) for TFs; naive overlap acceptable for exploratory histone | chip-seq/peak-calling |
| Consensus set | Pool for a union/consensus set AFTER IDR selects the reproducible threshold | chip-seq/differential-binding |

## Primary path: Bowtie2 + MACS3 + ChIPseeker

**Goal:** turn IP+input FASTQ into a blacklist-filtered, control-matched, annotated peakset.

**Approach:** align and keep unique reads, measure complexity before dedup, dedup + drop chrM + subtract the blacklist, call against the control, then annotate. Full runnable script: `examples/narrow_peak_workflow.sh`; annotation: `examples/peak_annotation.R`.

```bash
bowtie2 -p 8 -x bt2_index/genome -1 trimmed/${s}_R1.fq.gz -2 trimmed/${s}_R2.fq.gz \
    --no-mixed --no-discordant --maxins 1000 2> aligned/${s}.log \
  | samtools view -@4 -bS -q 30 - | samtools sort -@4 -o aligned/${s}.sorted.bam
samtools index aligned/${s}.sorted.bam

# Complexity QC on the PRE-dedup BAM (NRF = distinct positions / total; PBC1 = singletons / distinct).
# Counted per-mate here (close to ENCODE fragment-level values); use `bamtobed -bedpe` for exact parity.
bedtools bamtobed -i aligned/${s}.sorted.bam | awk 'BEGIN{OFS="\t"}{print $1,$2,$3,$6}' | sort | uniq -c \
  | awk '{tot+=$1; dist++; if($1==1) one++} END{printf "NRF=%.3f PBC1=%.3f\n", dist/tot, one/dist}'

# Dedup, drop chrM, then SUBTRACT the ENCODE blacklist (committed step, not optional)
samtools collate -@8 -O -u aligned/${s}.sorted.bam | samtools fixmate -m -u - - \
  | samtools sort -@8 -u - | samtools markdup -r -@8 - aligned/${s}.dedup.bam
samtools index aligned/${s}.dedup.bam
samtools idxstats aligned/${s}.dedup.bam | cut -f1 | grep -v -e '^chrM$' -e '^MT$' \
  | xargs samtools view -b aligned/${s}.dedup.bam > aligned/${s}.nochrM.bam
bedtools intersect -v -a aligned/${s}.nochrM.bam -b ENCODE_blacklist.bed > aligned/${s}.final.bam
samtools index aligned/${s}.final.bam
```

```bash
# Narrow (TFs, sharp marks) vs broad (spreading marks). -f BAMPE uses real fragment sizes.
macs3 callpeak -t aligned/IP_rep1.final.bam aligned/IP_rep2.final.bam \
    -c aligned/Input_rep1.final.bam aligned/Input_rep2.final.bam \
    -f BAMPE -g hs -n experiment --outdir peaks -q 0.01 --keep-dup all   # dedup done upstream (markdup -r); tell MACS3 to keep all
# Broad marks: add  --broad --broad-cutoff 0.1  (do NOT call H3K27me3 with narrow settings)
```

For IDR, call peaks PER REPLICATE (and on pooled pseudo-replicates) with a relaxed `-q`, then run `idr` across them (chip-seq/peak-calling). For higher confidence, intersect a second caller (HOMER `-style histone` for all histone marks).

## Signal tracks and annotation

```bash
# Standard experiment: RPKM/CPM is fine. SPIKE-IN experiment: this would ERASE the global shift.
bamCoverage -b aligned/IP_rep1.final.bam -o bigwig/IP_rep1.bw --normalizeUsing RPKM -p 8
# Spike-in (ChIP-Rx): bamCoverage --scaleFactor <spike-in factor> --normalizeUsing None  (chip-seq/spike-in-normalization)
```

Annotation uses a project GTF via `makeTxDbFromGFF()` when provided, else a pre-built TxDb. `overlap='all'` couples gene assignment with feature overlap (host-gene convention); default `overlap='TSS'` assigns the nearest-TSS gene independently. Full code: `examples/peak_annotation.R`.

## QC checkpoints between steps

| After | Gate | Interpretation |
|-------|------|----------------|
| QC/trim | Q30 >85%, adapter <5% | DNA higher quality than RNA |
| Alignment | Mapping >80%, unique >70% | Low unique = repeats/contamination/wrong build |
| PRE-dedup | NRF >0.8, PBC1 >0.8 | Low complexity = over-amplification/low input; MUST be computed before dedup |
| Peaks | FRiP >1% (TF) / >5% (sharp histone; broad marks run lower); NSC >1.05; RSC >0.8; fingerprint separates IP/input | Low FRiP/flat fingerprint = weak antibody or failed enrichment (chip-seq/chipseq-qc) |
| IDR | rescue ratio and self-consistency ratio both <=2 | Poor replicate consistency; run IDR on PER-replicate peaks |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Reproducible peaks over satellite/rDNA/high-signal regions | ENCODE blacklist never subtracted | `bedtools intersect -v` the blacklist BED before calling (committed step) |
| NRF/PBC ~1.0 and uninformative | Computed after `markdup -r` | Compute complexity on the PRE-dedup, filtered BAM |
| Peaks at open chromatin / CN-amplified loci | Called without a matched control | Pair each IP with its input/IgG in `callpeak -c` |
| H3K27me3/H3K9me3 fragmented into many tiny peaks | Broad mark called with narrow settings | Add `--broad --broad-cutoff 0.1` |
| `--shift/--extsize` had no effect | Used with `-f BAMPE` (ignored for PE) | Use `-f BAM` + `--nomodel` for SE; BAMPE derives fragments |
| Spike-in global shift disappears in tracks | bamCoverage RPKM/CPM re-equalized depth | `--scaleFactor` + `--normalizeUsing None` (chip-seq/spike-in-normalization) |
| "IDR" numbers look too good | IDR run on a pooled peakset | Run IDR on per-replicate peaks + pooled pseudo-replicates |

## Pipeline map (hand-offs)

- read-qc/fastp-workflow - adapter/quality trimming
- read-alignment/bowtie2-alignment - the standard ChIP-seq aligner, build/index
- alignment-files/duplicate-handling - collate/fixmate/sort/markdup order
- chip-seq/chipseq-qc - NRF/PBC, FRiP, NSC/RSC, fingerprint, hyper-ChIPable detection
- chip-seq/peak-calling - MACS3/SEACR/Genrich/HOMER, IDR vs naive overlap
- chip-seq/peak-annotation - ChIPseeker/HOMER/GREAT
- chip-seq/differential-binding - DiffBind/csaw and the normalization-problem framing
- chip-seq/chipseq-visualization - deepTools tracks and normalization choices
- chip-seq/spike-in-normalization - ChIP-Rx global-shift experiments
- chip-seq/motif-analysis - HOMER/MEME-ChIP/monaLisa

The complete runnable scripts are in this skill's examples/ (`narrow_peak_workflow.sh`, `peak_annotation.R`).

## Related Skills

- database-access/sra-data - Pull ChIP-seq FASTQ from SRA / ENA for re-analysis
- database-access/geo-data - Resolve ENCODE / Roadmap GSE accessions to SRA
- read-qc/fastp-workflow - Upstream adapter trimming and quality filtering
- read-alignment/bowtie2-alignment - Standard ChIP-seq aligner
- alignment-files/duplicate-handling - MarkDuplicates pre-peak-calling
- chip-seq/chipseq-qc - FRiP, NSC/RSC, library complexity, antibody validation
- chip-seq/peak-calling - MACS3/MACS2/HOMER/SPP, IDR vs naive overlap, per-tool failure modes
- chip-seq/peak-annotation - ChIPseeker, HOMER, ENCODE cCRE classification, GREAT regulatory domains
- chip-seq/differential-binding - DiffBind, DESeq2, csaw with the three-normalization-problems framing
- chip-seq/chipseq-visualization - deepTools, pyGenomeTracks, heatmaps with bigWig normalization choices
- chip-seq/motif-analysis - HOMER, MEME-ChIP (STREME), monaLisa with background-selection theory
- chip-seq/super-enhancers - ROSE/ROSE2/LILY for SE calling (H3K27ac vs MED1 vs BRD4)
- chip-seq/cut-and-run-tag - SEACR + MACS2 consensus for CUT&RUN/CUT&Tag (different protocol)
- chip-seq/spike-in-normalization - ChIP-Rx Drosophila spike-in for global-shift experiments
- chip-seq/chromatin-state-segmentation - ChromHMM multi-mark integration into chromatin states
- chip-seq/chip-deep-learning - BPNet/chromBPNet/Enformer for variant-effect prediction
- chip-seq/allele-specific-binding - WASP/BaalChIP/RASQUAL for allele-specific TF binding

## References

- Zhang Y, Liu T, Meyer CA, et al (2008) Model-based analysis of ChIP-Seq (MACS). *Genome Biology* 9:R137. DOI 10.1186/gb-2008-9-9-r137.
- Landt SG, Marinov GK, Kundaje A, et al (2012) ChIP-seq guidelines and practices of the ENCODE and modENCODE consortia. *Genome Research* 22:1813-1831. DOI 10.1101/gr.136184.111. (NSC/RSC, FRiP, IDR practice.)
- Li Q, Brown JB, Huang H, Bickel PJ (2011) Measuring reproducibility of high-throughput experiments. *Annals of Applied Statistics* 5:1752-1779. DOI 10.1214/11-AOAS466. (the IDR framework.)
- Amemiya HM, Kundaje A, Boyle AP (2019) The ENCODE blacklist: identification of problematic regions of the genome. *Scientific Reports* 9:9354. DOI 10.1038/s41598-019-45839-z.
<!-- END FILE: workflows/chipseq-pipeline/SKILL.md -->

## 子目录：workflows/clinical-trial-pipeline

<!-- BEGIN FILE: workflows/clinical-trial-pipeline/SKILL.md -->
---
name: bio-workflows-clinical-trial-pipeline
description: End-to-end clinical trial analysis workflow from CDISC SDTM/ADaM loading through ICH E9(R1) estimand-driven primary analysis to CONSORT 2025 regulatory-compliant reporting. Covers data preparation, FDA 2023 marginal vs conditional logistic regression, categorical tests with Boschloo, modern HTE/subgroup methods, missing-data sensitivity (MMRM, reference-based MI, Permutt tipping point), graphical multiplicity (Bretz-Maurer), survival analysis (Cox/RMST/competing risks) when applicable, and Table 1. Use when performing a complete analysis of clinical trial data.
tool_type: python
primary_tool: statsmodels
workflow: true
depends_on:
  - clinical-biostatistics/cdisc-data-handling
  - clinical-biostatistics/logistic-regression
  - clinical-biostatistics/categorical-tests
  - clinical-biostatistics/effect-measures
  - clinical-biostatistics/subgroup-analysis
  - clinical-biostatistics/trial-reporting
  - clinical-biostatistics/missing-data-sensitivity
  - clinical-biostatistics/multiplicity-graphical
  - clinical-biostatistics/survival-analysis
  - clinical-biostatistics/power-and-sample-size
qc_checkpoints:
  - after_estimand_definition: "ICH E9(R1) 5 attributes pre-specified in SAP: treatment, population, endpoint, summary measure, ICE handling strategy"
  - after_data_prep: "One row per USUBJID, no duplicate subjects, treatment arms balanced, DS domain tabulated for dropout patterns by arm"
  - after_primary_analysis: "Model converged, no separation warnings, marginal RD via g-computation reported as primary per FDA 2023; conditional OR as supportive"
  - after_subgroup: "Interaction tests run via single model (not per-subgroup p-comparisons), graphical multiplicity adjustment via gMCP, forest plot generated"
  - after_missing_data: "Per ICH E9(R1) ICE strategy: MMRM/MAR or reference-based MI (J2R/CR/CIR); Permutt tipping-point delta reported in residual SD units"
  - after_reporting: "Table 1 with SMD, missing data per CONSORT 2025 item 21c, harms per item 15, estimand statement per ICH E9(R1)"
---

## Version Compatibility

Reference examples tested with: statsmodels 0.14+, scipy 1.12+, tableone 0.9+, pyreadstat 1.2+, pandas 2.1+, numpy 1.26+, matplotlib 3.8+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Clinical Trial Analysis Pipeline

**"Analyze my clinical trial data end to end"** -> Load CDISC domain tables, prepare a subject-level analysis dataset, run primary statistical models, perform subgroup analyses, and generate regulatory-compliant tables and figures.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

A clinical-trial analysis is a commit-then-execute pipeline: its trustworthiness is decided by whether the analysis was locked BEFORE the data was seen, and every seam failure is a wrong-but-silent handoff that answers a different question with no error thrown.

1. **The ESTIMAND, locked in the SAP before unblinding, is the made-once commitment everything inherits.** ICH E9(R1) defines it by 5 attributes: treatment condition, population, endpoint, intercurrent-event (ICE) handling strategy, and population-level summary. It is the precise definition of "what treatment effect the trial estimates", committed before analysis so the estimator is matched to it rather than chosen to flatter the data.
2. **The estimator is a CONSEQUENCE of the estimand's ICE strategy, not a free modeling choice.** A treatment-policy strategy needs all post-ICE data (MMRM/treatment-policy, or reference-based MI if truly missing); a hypothetical strategy censors/models the post-ICE data as if the ICE had not occurred (MMRM under MAR); a composite strategy folds the ICE into the endpoint. Choosing MMRM vs reference-based MI vs g-computation to flatter the data is an estimand-estimator mismatch.
3. **The analysis population and all subgroups are defined a priori; the data never picks them.** Randomization licenses causal interpretation for the ITT/FAS primary only — PP and subgroups do NOT inherit that protection. Pre-specify every subgroup and the multiplicity graph in the SAP; post-hoc data-driven subgroups are hypothesis-generating only. This is the clinical analog of "don't call hits before CN correction".
4. **Baseline balance is not tested with p-values, and marginal is not conditional.** In a randomized trial any imbalance is by definition chance, and baseline hypothesis testing is incoherent (Senn 1994) — report SMD (>0.1 notable, a convention Senn does not state) and adjust via pre-specified ANCOVA, don't test-then-decide. For a binary endpoint the primary is the MARGINAL risk difference via g-computation (FDA 2023); a conditional OR is a different parameter (non-collapsibility), reported as supportive.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| The estimand (5 ICH E9(R1) attributes, SAP-locked before unblinding) | Which question the trial answers; the estimator must match its ICE strategy |
| The estimator matched to the ICE strategy | Whether the analysis answers the locked question; a mismatch is silent |
| Analysis population set (ITT/FAS primary, PP sensitivity, Safety as-treated) a priori | Causal validity; ITT is randomization-protected, PP and subgroups are not |
| SDTM -> ADaM derivation (pre-specified, one-directional; ADTTE CNSR convention) | Every downstream model; CDISC CNSR=0 means EVENT, opposite of R/Python survival packages |

### Scientific Reasoning Framework

Before executing any analysis step, establish the causal framework. For an RCT, randomization justifies causal interpretation of the primary analysis, but subgroup analyses and observational comparisons within the trial (e.g., adherence effects) do not inherit this protection. Key decisions requiring scientific judgment at each step: (1) data preparation -- which aggregation strategy matches the estimand, (2) covariate selection -- include confounders and prognostic factors from the SAP, exclude mediators and colliders, (3) subgroup analysis -- test only biologically motivated interactions, (4) missing data -- link DS domain reasons to the assumed mechanism before choosing a method. The workflow below provides the technical steps; the scientific reasoning at each decision point determines whether the results are valid.

## Workflow Overview

```
CDISC Domain Files (DM, AE, EX, LB)
    |
    v
[1. Data Preparation] ----> Subject-level dataset with outcomes and covariates
    |
    v
[2. Table 1] ------------> Baseline characteristics by treatment arm
    |
    v
[3. Primary Analysis] ---> Marginal RD via g-computation (conditional OR supportive)
    |
    v
[4. Categorical Tests] --> Chi-square / Fisher's exact for key associations
    |
    v
[5. Subgroup Analysis] --> Interaction terms, stratified ORs, forest plot
    |
    v
[6. Missing Data] -------> Multiple imputation sensitivity analysis
    |
    v
Results tables and figures
```

## Step 1: Data Preparation

**Goal:** Create a single subject-level analysis dataset from CDISC domain tables.

**Approach:** Load domain files, aggregate event-level data to one row per subject, merge on USUBJID, and code the outcome variable.

```python
import pandas as pd
import pyreadstat

dm, _ = pyreadstat.read_xport('dm.xpt')
ae, _ = pyreadstat.read_xport('ae.xpt')

# Aggregate: did each subject have the target adverse event?
target_ae = ae[ae['AEDECOD'] == 'COVID-19'].copy()
severity_map = {'MILD': 1, 'MODERATE': 2, 'SEVERE': 3, 'LIFE THREATENING': 4, 'FATAL': 5}
target_ae['AESEV_NUM'] = target_ae['AESEV'].map(severity_map)
had_event = target_ae.groupby('USUBJID')['AESEV_NUM'].max().reset_index()
had_event.columns = ['USUBJID', 'EVENT_SEVERITY']

analysis = dm[['USUBJID', 'ARM', 'ARMCD', 'AGE', 'SEX']].merge(had_event, on='USUBJID', how='left')
analysis['HAD_EVENT'] = analysis['EVENT_SEVERITY'].notna().astype(int)
analysis['TREATMENT'] = (analysis['ARMCD'] != 'PLACEBO').astype(int)
```

**QC Checkpoint:** Verify one row per USUBJID, no unexpected duplicates, treatment arms are present and reasonably balanced.

```python
assert analysis['USUBJID'].is_unique, 'Duplicate subjects detected'
print(analysis['ARM'].value_counts())
```

## Step 2: Table 1 Baseline Characteristics

**Goal:** Summarize demographics and baseline variables by treatment arm.

**Approach:** Use TableOne to generate a baseline table by arm with standardized mean differences and explicit missingness. Omit the baseline p-value column: in a randomized trial any imbalance is by definition due to chance, so a baseline p-value tests a null already known to be true (Senn 1994; CONSORT 2010/2025). Report SMD for balance instead. Table-construction and export mechanics (gtsummary/tableone, Word export, gene-symbol-safe supplements) live in reporting/publication-tables.

```python
from tableone import TableOne

columns = ['AGE', 'SEX', 'RACE']
categorical = ['SEX', 'RACE']
table1 = TableOne(analysis, columns=columns, categorical=categorical,
                  groupby='ARM', pval=False, smd=True, missing=True)
print(table1.tabulate(tablefmt='github'))
```

Interpret SMD > 0.1 as meaningful imbalance. The response to a worrying imbalance on a prognostic covariate is to adjust for it (a pre-specified ANCOVA/model covariate), not to test it.

## Step 3: Primary Analysis -- Logistic Regression

**Goal:** Estimate the treatment effect on the binary outcome as an adjusted odds ratio.

**Approach:** Fit a logistic regression with explicit reference category and clinically relevant covariates, then exponentiate coefficients to obtain ORs.

```python
import statsmodels.formula.api as smf
import numpy as np

model = smf.logit(
    'HAD_EVENT ~ C(ARM, Treatment(reference="Placebo")) + AGE + C(SEX)',
    data=analysis
).fit()

or_table = pd.DataFrame({
    'OR': np.exp(model.params),
    'Lower_CI': np.exp(model.conf_int()[0]),
    'Upper_CI': np.exp(model.conf_int()[1]),
    'p_value': model.pvalues
})
print(or_table)
print(f'McFadden pseudo-R2: {model.prsquared:.4f}')
```

The logistic fit above yields the CONDITIONAL (adjusted) OR. When the estimand's summary measure is a marginal risk difference (the FDA 2023 primary for a binary endpoint), do NOT report this conditional OR as the primary effect. Compute the MARGINAL risk difference by g-computation: fit the covariate-adjusted model, predict each subject's outcome probability under both arms, average within arm, and difference; bootstrap the whole fit-and-predict for the CI. `examples/clinical_trial_pipeline.py` implements this; see clinical-biostatistics/logistic-regression for the estimator's assumptions and variance options. Report the conditional OR as supportive. The two differ by non-collapsibility and answer different questions.

**QC Checkpoint:** Verify model converged (no warnings), check for separation (coefficients > 10 or SE > 100), report pseudo-R-squared (McFadden > 0.2 is excellent; do not compare across pseudo-R2 types). Confirm the reported PRIMARY effect matches the estimand's summary measure (marginal RD via g-computation for a marginal estimand), not whichever the model emits by default.

## Step 4: Categorical Tests

**Goal:** Test the crude association between treatment and outcome using contingency tables.

**Approach:** Build a 2x2 table, check expected cell counts, and choose chi-square or Fisher's exact accordingly.

```python
from scipy.stats import chi2_contingency, fisher_exact

table = pd.crosstab(analysis['ARM'], analysis['HAD_EVENT'])
chi2, p, dof, expected = chi2_contingency(table, correction=False)

if (expected < 5).any():
    _, p = fisher_exact(table.values)
    print(f'Fisher exact p = {p:.4f}')
else:
    print(f'Chi-square p = {p:.4f} (chi2 = {chi2:.2f}, dof = {dof})')
```

## Step 5: Subgroup Analysis

**Goal:** Test whether the treatment effect varies across pre-specified subgroups.

**Approach:** Fit a model with an interaction term and test it with a single interaction LR test. Subgroup-specific ORs are DESCRIPTIVE ONLY -- do not correct their individual p-values, do not interpret them; the alpha allocated to the subgroup family is handled by the pre-specified gMCP graph, not by a post-hoc correction. Visualize with a forest plot.

```python
import matplotlib.pyplot as plt

# The HTE test is the treatment-by-subgroup INTERACTION, not per-subgroup significance.
# Fit the main-effects (restricted) and interaction (full) models, then LR-test the interaction.
main_model = smf.logit(
    'HAD_EVENT ~ C(ARM, Treatment(reference="Placebo")) + C(SUBGROUP)',
    data=analysis
).fit(disp=0)
interaction_model = smf.logit(
    'HAD_EVENT ~ C(ARM, Treatment(reference="Placebo")) * C(SUBGROUP)',
    data=analysis
).fit(disp=0)
# compare_lr_test exists only on linear-model results, NOT LogitResults -- compute the LR test by hand.
from scipy.stats import chi2
lr_stat = 2 * (interaction_model.llf - main_model.llf)
df_diff = int(interaction_model.df_model - main_model.df_model)
interaction_pval = chi2.sf(lr_stat, df_diff)
print(f'Treatment-by-subgroup interaction: LR chi2={lr_stat:.2f}, df={df_diff}, p={interaction_pval:.3f}')

# Subgroup-specific ORs are DESCRIPTIVE ONLY (to draw the forest plot). Do NOT interpret their
# individual p-values as evidence of a subgroup effect -- that is the invalid per-subgroup
# significance pattern; the interaction p-value above is the only valid HTE test.
labels, ors, lowers, uppers = [], [], [], []
for group in analysis['SUBGROUP'].unique():
    sub = analysis[analysis['SUBGROUP'] == group]
    sub_model = smf.logit(
        'HAD_EVENT ~ C(ARM, Treatment(reference="Placebo"))',
        data=sub
    ).fit(disp=0)
    or_val = np.exp(sub_model.params.iloc[1])
    ci = np.exp(sub_model.conf_int().iloc[1])
    labels.append(group)
    ors.append(or_val)
    lowers.append(ci[0])
    uppers.append(ci[1])

# Forest plot
fig, ax = plt.subplots(figsize=(8, 5))
y_pos = range(len(labels))
ax.errorbar(ors, y_pos,
            xerr=[np.array(ors) - np.array(lowers), np.array(uppers) - np.array(ors)],
            fmt='D', color='black', capsize=3, markersize=5)
ax.axvline(x=1.0, color='gray', linestyle='--', linewidth=0.8)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels)
ax.set_xlabel('Odds Ratio (95% CI)')
ax.set_xscale('log')
plt.tight_layout()
plt.savefig('forest_plot.png', dpi=150)
```

**QC Checkpoint:** Interaction p-value reported from a single LR test. Alpha for the subgroup family allocated in the pre-specified gMCP graph (not a post-hoc p-value correction on the descriptive subgroup ORs). Forest plot shows overall estimate for context.

## Step 6: Missing Data Sensitivity Analysis (per ICH E9(R1) and clinical-biostatistics/missing-data-sensitivity)

**Goal:** Assess robustness of the primary result under the pre-specified ICE strategy with both MAR primary and MNAR sensitivity analyses.

**Approach:** First examine DS (Disposition) domain for differential dropout patterns; if dropout differs by arm, MAR is suspect and reference-based MI is required as primary. Otherwise, fit MMRM under MAR with Rubin's-rules pooling for continuous endpoints, or g-computation with bootstrap for binary. Always run Permutt 2016 tipping-point sensitivity in residual SD units.

```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

n_imputations = 20   # practical starting count; von Hippel 2020 shows required m scales with the fraction of missing information (two-stage rule), so raise it when FMI is high
# Impute AGE jointly WITH its predictors (SEX, TREATMENT, HAD_EVENT). A single-column imputer has
# no predictors, so sample_posterior draws are identical -> between-imputation variance = 0 and the
# MI collapses to complete-case. Including correlated columns makes the posterior draws actually vary.
impute_cols = ['AGE', 'TREATMENT', 'HAD_EVENT']   # numeric only; SEX ('M'/'F') would break IterativeImputer and is restored below
mi_data = analysis.dropna(subset=['HAD_EVENT', 'TREATMENT']).copy()

results = []
for i in range(n_imputations):
    imputer = IterativeImputer(max_iter=10, random_state=i, sample_posterior=True)
    imputed_cov = pd.DataFrame(imputer.fit_transform(mi_data[impute_cols]),
                               columns=impute_cols, index=mi_data.index)
    # Only AGE had missings; restore the observed discrete columns so they stay integer-valued.
    imputed_cov['HAD_EVENT'] = mi_data['HAD_EVENT'].values
    imputed_cov['TREATMENT'] = mi_data['TREATMENT'].values
    imputed_cov['SEX'] = mi_data['SEX'].values
    # Mirror the primary ADJUSTED model's RHS (AGE + SEX) so the pooled OR is comparable to it.
    model_imp = smf.logit('HAD_EVENT ~ TREATMENT + AGE + C(SEX)', data=imputed_cov).fit(disp=0)
    results.append({'coef': model_imp.params['TREATMENT'], 'se': model_imp.bse['TREATMENT']})

pooled_coef = np.mean([r['coef'] for r in results])
within_var = np.mean([r['se']**2 for r in results])
between_var = np.var([r['coef'] for r in results], ddof=1)
total_var = within_var + (1 + 1/n_imputations) * between_var
pooled_or = np.exp(pooled_coef)
pooled_ci = (np.exp(pooled_coef - 1.96 * np.sqrt(total_var)),
             np.exp(pooled_coef + 1.96 * np.sqrt(total_var)))
print(f'Pooled OR: {pooled_or:.3f} ({pooled_ci[0]:.3f}-{pooled_ci[1]:.3f})')
```

**QC Checkpoint:** Compare pooled OR and CI with the complete-case primary analysis. Large discrepancies suggest missing data may not be MCAR. Document the comparison.

## Result Reporting Checklist (CONSORT 2025 + ICH E9(R1) aligned)

- [ ] ICH E9(R1) estimand statement with 5 attributes pre-specified in SAP
- [ ] Table 1 with baseline characteristics by arm (SMD > 0.1 flagged; NOT p-values)
- [ ] Primary analysis: marginal RD via g-computation per FDA 2023 (binary) OR MMRM-MAR with Kenward-Roger (continuous longitudinal)
- [ ] Conditional OR/HR as supportive (different parameter than marginal due to non-collapsibility)
- [ ] Analysis populations defined: ITT (primary), FAS (with explicit exclusion criteria), PP (sensitivity), Safety (AE)
- [ ] Missing data per CONSORT 2025 item 21c: mechanism assumption, primary method, MNAR sensitivity (J2R/CR/CIR per Carpenter-Roger 2013)
- [ ] Permutt tipping-point delta reported in residual SD units
- [ ] Subgroup forest plot with INTERACTION p-values (not per-subgroup p-comparison); graphical multiplicity via gMCP
- [ ] Multiplicity adjustment method stated (CONSORT 2025 item 30 limitations; FDA Multiple Endpoints Final Oct 2022)
- [ ] CONSORT flow diagram numbers available
- [ ] Harms per CONSORT 2025 item 15 (absorbs CONSORT-Harms 2022)

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| The analysis answers a different question | Estimand-estimator mismatch (e.g. a hypothetical estimand analyzed treatment-policy) | Derive the estimator FROM the ICE strategy; MMRM/MI/g-computation are consequences of attribute (iv), not free choices |
| Spurious subgroup effect | Subgroups/sensitivity chosen after seeing the data | Pre-specify all subgroups + the multiplicity graph in the SAP; post-hoc is hypothesis-generating only |
| Effect loses causal validity | PP swapped in as primary because it "looks cleaner" | ITT/FAS primary (randomization-protected); PP is sensitivity; define both a priori |
| Survival results inverted | ADTTE CNSR sign flip (CDISC CNSR=0 means EVENT) | Convert the censoring indicator before passing to lifelines/survival |
| False "imbalance" conclusions | Baseline characteristics tested with p-values | Report SMD (>0.1 notable); adjust prognostic imbalance via pre-specified ANCOVA |
| Primary effect is the wrong parameter | Conditional OR reported as the marginal effect (non-collapsibility) | Marginal risk difference via g-computation is primary (FDA 2023); conditional OR supportive |
| Over-conservative inference (CIs too wide, power lost) | Stratification/randomization factors omitted from the analysis model | Include the stratification factors; omitting them biases SEs upward and Type-I below nominal (Kahan-Morris 2012) |

## When to Add Specialized Skills

This pipeline covers the typical binary-endpoint RCT workflow. For specific designs, add the corresponding specialized skill:

- **Time-to-event primary endpoint** (OS, PFS, DOR): add clinical-biostatistics/survival-analysis for Cox PH diagnostics, RMST under non-PH, competing risks via Fine-Gray vs cause-specific Cox, MaxCombo for delayed effects, informative censoring handling
- **Continuous longitudinal endpoint** (HbA1c at 24 weeks): clinical-biostatistics/missing-data-sensitivity for MMRM with Kenward-Roger via R mmrm; reference-based MI via R rbmi for MNAR sensitivity
- **Multiple primary or key secondary endpoints**: clinical-biostatistics/multiplicity-graphical for Bretz-Maurer graphical procedures via gMCP
- **Trial design / sample-size justification**: clinical-biostatistics/power-and-sample-size for Schoenfeld events, Lakatos under non-PH, FDA 2016 NI double discount, TOST equivalence
- **Adaptive trial** (group-sequential, SSR, platform): clinical-biostatistics/adaptive-designs for rpact/gsDesign, Mehta-Pocock promising zone, ICH E20 considerations
- **Bayesian primary inference or RWE comparator**: clinical-biostatistics/bayesian-trials for BOIN dose-finding, robust MAP priors via RBesT, EXNEX basket trials, psborrow2 for external controls

## Related Skills

- clinical-biostatistics/cdisc-data-handling - CDISC SDTM/ADaM, Pinnacle 21, Dataset-JSON, ADTTE CNSR conventions
- clinical-biostatistics/logistic-regression - FDA 2023 marginal vs conditional, g-computation, Brant test, Firth, Hauck-Donner
- clinical-biostatistics/categorical-tests - Boschloo, mid-p McNemar, Wilson/Newcombe/Miettinen-Nurminen CIs
- clinical-biostatistics/effect-measures - NNT Bender 2002 convention, profile likelihood, modified Poisson for RR
- clinical-biostatistics/subgroup-analysis - Causal forests, STEPP, SIDES, EXNEX, Yadlowsky RATE, EMA 2019 subgroup guideline
- clinical-biostatistics/trial-reporting - ICH E9(R1) 5 estimand strategies, Cro/Bartlett variance debate, CONSORT 2025
- clinical-biostatistics/missing-data-sensitivity - MMRM/Kenward-Roger, reference-based MI, Permutt tipping point
- clinical-biostatistics/multiplicity-graphical - Bretz-Maurer graphs, Goeman closed-testing admissibility
- clinical-biostatistics/survival-analysis - Cox/RMST/Fine-Gray/MaxCombo/recurrent events/interval censoring
- clinical-biostatistics/power-and-sample-size - Schoenfeld/Lakatos, NI double discount, crossover, MCID
- clinical-biostatistics/adaptive-designs - Group-sequential, SSR, RAR consensus, BOIN, platform trials
- clinical-biostatistics/bayesian-trials - MAP/EXNEX/RWE, FDA Bayesian Jan 2026 draft, psborrow2
- reporting/publication-tables - Table 1 construction (SMD not baseline p-values, show missingness) and Word/LaTeX export

## References

- ICH E9(R1) (2019) Addendum on Estimands and Sensitivity Analysis in Clinical Trials to the Guideline on Statistical Principles for Clinical Trials. International Council for Harmonisation. (the estimand's 5 attributes and 5 ICE strategies.)
- Kahan BC, Cro S, Li F, et al (2023) Eliminating ambiguous treatment effects using estimands. *American Journal of Epidemiology* 192:987-994. DOI 10.1093/aje/kwad036. (98% of trials do not articulate the estimand.)
- Senn S (1994) Testing for baseline balance in clinical trials. *Statistics in Medicine* 13:1715-1726. DOI 10.1002/sim.4780131703. (baseline SMD, not p-values.)
- Kahan BC, Morris TP (2012) Improper analysis of trials randomised using stratified blocks or minimisation. *Statistics in Medicine* 31:328-340. DOI 10.1002/sim.4431. (omitting stratification factors makes inference conservative: SEs biased upward, Type-I below nominal, power lost.)
- Carpenter JR, Roger JH, Kenward MG (2013) Analysis of longitudinal trials with protocol deviation: a framework for relevant, accessible assumptions, and inference via multiple imputation. *Journal of Biopharmaceutical Statistics* 23:1352-1371. DOI 10.1080/10543406.2013.834911. (reference-based MI.)
<!-- END FILE: workflows/clinical-trial-pipeline/SKILL.md -->

## 子目录：workflows/clip-pipeline

<!-- BEGIN FILE: workflows/clip-pipeline/SKILL.md -->
---
name: bio-workflows-clip-pipeline
workflow: true
depends_on: [clip-seq/clip-preprocessing, clip-seq/clip-alignment, clip-seq/clip-qc, clip-seq/clip-peak-calling, clip-seq/crosslink-site-detection, clip-seq/binding-site-annotation, clip-seq/clip-motif-analysis, clip-seq/differential-clip]
qc_checkpoints: [preprocessing_retention, alignment_rate, library_complexity, frip, idr]
description: End-to-end CLIP-seq pipeline from FASTQ to ENCODE-compliant binding sites, single-nucleotide crosslink maps, annotation, motifs, and (optionally) differential binding. Use when running the full Yeo lab eCLIP / iCLIP / iCLIP2 / iCLIP3 / irCLIP / PAR-CLIP analysis with SMInput control, protocol-specific UMI extraction, ENCODE STAR parameters, CLIPper or Skipper peak calling with stringent log2 FC and -log10 p thresholds, IDR rescue and self-consistency QC, and downstream motif registration with mCross or PEKA.
tool_type: mixed
primary_tool: CLIPper
---

## Version Compatibility

Reference examples tested with: umi_tools 1.1.5+, cutadapt 4.6+, fastp 0.23+, STAR 2.7.11b+, samtools 1.19+, bedtools 2.31+, CLIPper 2.0+, Skipper (commit 2023.05+), PureCLIP 1.3.1+, HOMER 4.11+, ChIPseeker 1.40+, preseq 3.2+, picard 3.1+, idr 2.0.4+, MultiQC 1.21+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws unexpected errors, introspect the installed tool and adapt the example rather than retrying.

# CLIP-seq End-to-End Pipeline

**"Analyze my CLIP-seq data from raw FASTQ to ENCODE-compliant binding sites"** -> Orchestrate protocol-specific UMI extraction, 3'-only adapter trimming (preserving the R2 5' truncation = crosslink site -1), ENCODE STAR alignment, UMI-based deduplication, library complexity QC, peak calling against SMInput with stringent thresholds (log2 FC >= 3 AND -log10 p >= 3), single-nucleotide crosslink-site detection, ChIPseeker annotation with CLIP-appropriate `tssRegion`, motif discovery with GC-matched background and CL-position registration, and optional differential binding between conditions.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

A CLIP callset is decided at four seams, not inside the peak caller.

1. **The protocol variant is the master commitment made once at the top.** It fixes the UMI pattern, the STAR mismatch ceiling, and the crosslink signal (truncation vs PAR-CLIP T->C vs STAMP C->U edit). The CLIP Variant Selection table below is that decision; everything downstream inherits it.
2. **Every IP is normalized against its SMInput with ENCODE-stringent thresholds (log2 FC >= 3 AND -log10 p >= 3).** Peaks called without SMInput normalization are enrichment-uncontrolled and dominated by abundance.
3. **The R2 5' end IS the crosslink site (-1), so preprocessing and alignment must PRESERVE it.** Trim 3'-only and permissively (`-q 6`, never `-g` on R1), and align with STAR `--alignEndsType EndToEnd` - soft-clipping or aggressive 5' trimming destroys the truncation base and with it single-nucleotide resolution.
4. **40-70% PCR duplication is BY DESIGN; low duplication signals a FAILED IP, not a clean library.** The IP enriches a small molecule pool, so the real quality metric is the UNIQUE-fragment count after UMI dedup - never the raw duplication rate.

## Pipeline Overview

```
FASTQ + SMInput
  -> [clip-preprocessing]    UMI extract + 3' adapter trim (-q 6 -m 18) + two-pass for eCLIP
  -> [clip-alignment]        STAR ENCODE block (alignEndsType EndToEnd, mismatch 0.04 or 0.07 for PAR-CLIP) + UMI dedup
  -> [clip-qc]               preseq, FRiP, IDR rescue + self-consistency, read distribution
  -> [clip-peak-calling]     CLIPper + SMInput log2 norm (stringent: log2 FC >= 3, -log10 p >= 3) OR Skipper (substantially more sites)
  -> [crosslink-site-detection] PureCLIP or CTK CITS for single-nt CL positions
  -> [binding-site-annotation] ChIPseeker (tssRegion=c(-100,100), level=transcript) + RBP-Maps for splicing factors
  -> [clip-motif-analysis]   HOMER + mCross (registered) + RBNS Kd cross-check
  -> [differential-clip]     DEWSeq window-level NB with type:condition interaction (optional)
```

## CLIP Variant Selection

| Variant | When to use | UMI pattern | STAR mismatch ceiling | Detection signal |
|---------|-------------|-------------|----------------------|------------------|
| eCLIP (Van Nostrand 2016) | ENCODE comparability; SMInput available | 10 nt R1 | 0.04 | R2 5' truncation |
| iCLIP / iCLIP2 / iCLIP3 | Single-end; high motif specificity | NNNXXXXNN (3+4+2; demux first) | 0.04 | R1 5' truncation |
| irCLIP / FLASH | Non-radioactive; fast | Protocol-specific | 0.04 | Truncation |
| PAR-CLIP | Photoactivatable nucleoside (4SU); HEK293/K562 | 4 nt typical | 0.07 (raised for T->C) | T->C transitions |
| miCLIP / miCLIP2 | m6A modification | iCLIP-style | 0.04 | Truncation + C->T at m6A |
| STAMP / scSTAMP | Antibody-free; in vivo or single-cell | NA (no UV) | 0.04 (RNA-seq mode) | C->U editing (RBP-APOBEC1 fusion) |
| chimeric eCLIP / miR-eCLIP | Direct miRNA-target pairs | 10 nt R1 | 0.04 | Chimeric reads |

## Step 1: Quality Control of Raw FASTQ

```bash
# Initial QC
fastqc raw_R1.fq.gz raw_R2.fq.gz -o qc/raw/

# Inspect first 12 bases of 100 reads to verify UMI pattern matches the prep
zcat raw_R1.fq.gz | awk 'NR%4==2' | head -100 | cut -c1-12 | sort | uniq -c | sort -rn | head
# Random barcode positions show ~25% per base; library barcodes are fixed
```

## Step 2: Preprocessing (Protocol-Specific)

**Goal:** Convert raw CLIP FASTQ into UMI-deduplicated, alignment-ready FASTQ while preserving the R2 5' end (= crosslink site -1) that drives single-nucleotide resolution downstream.

**Approach:** Use the protocol-matched UMI pattern (10 nt eCLIP, NNNXXXXNN iCLIP, 4 nt PAR-CLIP), run `umi_tools extract` to move random barcodes to read names, then apply cutadapt with 3'-only adapter trimming at `-q 6 -m 18` (permissive 5' to protect the truncation base). eCLIP uses two-pass trimming to remove read-through inline adapters from R2 5' only; iCLIP and PAR-CLIP use single-pass.

```bash
# eCLIP: 10 nt UMI on R1; two-pass adapter trim for read-through
# See clip-seq/clip-preprocessing for protocol-specific patterns
umi_tools extract \
    --bc-pattern=NNNNNNNNNN \
    --stdin=raw_R1.fq.gz --read2-in=raw_R2.fq.gz \
    --stdout=R1.umi.fq.gz --read2-out=R2.umi.fq.gz \
    --log=qc/umi_extract.log

# Pass 1: 3' adapter on both reads
# -q 6 is intentionally permissive; aggressive trimming destroys R2 5' = CL site -1
cutadapt \
    -a AGATCGGAAGAGCACACGTCT \
    -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT \
    --quality-base 33 -q 6 -m 18 \
    -j 8 \
    -o R1.p1.fq.gz -p R2.p1.fq.gz \
    R1.umi.fq.gz R2.umi.fq.gz \
    > qc/cutadapt_pass1.log 2>&1

# Pass 2: strip read-through 5' adapter from R2 only (NEVER -g on R1)
cutadapt \
    -G GATCGTCGGACTGTAGAACTCTGAAC \
    --quality-base 33 -q 6 -m 18 \
    -j 8 \
    -o R1.trim.fq.gz -p R2.trim.fq.gz \
    R1.p1.fq.gz R2.p1.fq.gz \
    >> qc/cutadapt_pass2.log 2>&1
```

For PAR-CLIP: same UMI extraction but downstream alignment raises `--outFilterMismatchNoverReadLmax` from 0.04 to 0.07 (the T->C signature would otherwise be filtered as sequencing error). See clip-seq/clip-preprocessing for full per-protocol guidance.

## Step 3: Alignment (ENCODE STAR Block)

```bash
# ENCODE eCLIP convention. Sacred: --alignEndsType EndToEnd (soft-clip would destroy truncation = CL site -1)
STAR --runMode alignReads \
    --runThreadN 16 \
    --genomeDir /path/to/STAR_hg38_index \
    --genomeLoad NoSharedMemory \
    --readFilesIn R1.trim.fq.gz R2.trim.fq.gz \
    --readFilesCommand zcat \
    --outFilterType BySJout \
    --outFilterMultimapNmax 1 \
    --alignEndsType EndToEnd \
    --outFilterMismatchNoverReadLmax 0.04 \
    --outFilterScoreMinOverLread 0.66 \
    --outFilterMatchNminOverLread 0.66 \
    --outSAMtype BAM SortedByCoordinate \
    --outSAMattributes All \
    --outFileNamePrefix sample_

samtools index sample_Aligned.sortedByCoord.out.bam

# MAPQ >= 10 (255 = unique in STAR; lower = multi-mapper)
samtools view -b -q 10 sample_Aligned.sortedByCoord.out.bam > sample_q10.bam
samtools index sample_q10.bam

# UMI dedup. ENCODE convention: --method=unique
umi_tools dedup \
    --stdin=sample_q10.bam \
    --stdout=sample_dedup.bam \
    --method=unique \
    --paired \
    --log=qc/dedup.log
samtools index sample_dedup.bam
```

For PAR-CLIP: change `--outFilterMismatchNoverReadLmax 0.04` to `0.07`. For repeat-binding RBPs (MATR3, ZFP36, FUS at LINE-1, HNRNPK at SINEs): change `--outFilterMultimapNmax 1` to `100` and add `--outSAMmultNmax -1`, then run CLAM downstream for EM-based multi-mapper assignment. See clip-seq/clip-alignment for full guidance.

## Step 4: QC (Five Gates)

```bash
# Gate 1: preprocessing retention (cutadapt log, target >= 70%)
grep -E "passing filters|Pairs written" qc/cutadapt_pass1.log

# Gate 2: alignment rate (STAR Log.final.out, target >= 60% eCLIP, 70% iCLIP)
grep "Uniquely mapped reads %" sample_Log.final.out

# Gate 3: library complexity (preseq, target >= 1M unique at sequenced depth)
preseq lc_extrap -B -P sample_q10.bam -o qc/preseq.txt

# Gate 4: FRiP (after peak calling; target >= 0.005 narrow-binding RBP)
# Gate 5: IDR replicate reproducibility (after peak calling; target rescue and self-consistency < 2)

# Aggregate all QC into a single MultiQC report
multiqc qc/ -o qc/multiqc/
```

CLIP libraries have 40-70% PCR duplication BY DESIGN (the IP enriches a small molecule pool). Low duplication usually means failed IP, not a good library. The unique-fragment count after UMI dedup is the actual quality metric. See clip-seq/clip-qc for full five-gate diagnostic.

## Step 5: Peak Calling

```bash
# CLIPper (ENCODE canonical) + SMInput log2 normalization
clipper \
    -b sample_dedup.bam \
    -s GRCh38 \
    -o peaks/sample.clipper.bed \
    --FDR 0.05 \
    --save-pickle \
    --processors 8   # super-local p-values are hard-coded ON in current CLIPper; the --superlocal flag was removed

# ENCODE stringent: log2(IP/SMInput) >= 3 AND -log10 p >= 3
# (Yeo lab eclip-pipeline scripts implement the normalization; see clip-seq/clip-peak-calling)
python overlap_peakfi_with_bam_PE.py \
    peaks/sample.clipper.bed \
    sample_dedup.bam sminput_dedup.bam \
    sample_dedup.bam.readnum.txt sminput_dedup.bam.readnum.txt \
    peaks/sample.normed.bed

python compress_l2foldenrpeakfi_for_replicate_overlapping_bedformat.py \
    peaks/sample.normed.bed \
    peaks/sample.compressed.bed

# Stringent filter
awk 'BEGIN{FS=OFS="\t"} $5 >= 3 && $6 >= 3' peaks/sample.compressed.bed > peaks/sample.stringent.bed
```

For maximum sensitivity (substantially more sites than CLIPper for mRNA-binding RBPs), use the Skipper Snakemake workflow with the same SMInput control. Mandatory for FASTKD2 / mt-RBPs which CLIPper misses on chrM. See clip-seq/clip-peak-calling for the full caller taxonomy.

## Step 6: Single-Nucleotide Crosslink-Site Detection

```bash
# PureCLIP: HMM jointly modeling enrichment + truncation + CL motif.
# -iv learns HMM parameters on a CHROMOSOME SUBSET (semicolon-delimited) to cut memory/runtime
# (per PureCLIP docs); it is NOT a BED. To limit the callset to expressed regions, pre-filter the input BAM.
pureclip \
    -i sample_dedup.bam -bai sample_dedup.bam.bai \
    -g genome.fa \
    -ibam sminput_dedup.bam -ibai sminput_dedup.bam.bai \
    -o crosslinks/sample.sites.bed \
    -or crosslinks/sample.regions.bed \
    -nt 8 -dm 8 \
    -iv 'chr1;chr2;chr3;'
```

Single-nt CL sites feed mCross motif registration and allele-specific binding analyses. They are NOT a replacement for the broad peak list; complementary outputs. See clip-seq/crosslink-site-detection.

## Step 7: IDR Across Replicates

```bash
# Sort each replicate's compressed BED by signal (log2 FC, column 5)
sort -k5,5gr peaks/rep1.compressed.bed > peaks/rep1.sorted.bed
sort -k5,5gr peaks/rep2.compressed.bed > peaks/rep2.sorted.bed

# True replicates threshold 0.05
idr --samples peaks/rep1.sorted.bed peaks/rep2.sorted.bed \
    --input-file-type bed --rank 5 \
    --output-file qc/idr.true.out \
    --idr-threshold 0.05 \
    --plot --log-output-file qc/idr.log

# ENCODE rule: rescue + self-consistency ratios both < 2 to pass
# Pseudo-replicate IDR (split BAM in half) at threshold 0.10
```

## Step 8: Binding-Site Annotation

```r
# CLIP-appropriate ChIPseeker (tssRegion tight; level=transcript)
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene

peaks <- readPeakFile('peaks/sample.stringent.bed')
anno <- annotatePeak(
    peaks,
    TxDb = txdb,
    level = 'transcript',
    tssRegion = c(-100, 100),
    genomicAnnotationPriority = c('Promoter','5UTR','3UTR','Exon','Intron','Downstream','Intergenic')
)
plotAnnoPie(anno)
```

Default ChIPseeker `tssRegion=c(-3000, 3000)` over-extends for CLIP (would label 30-50% peaks as "Promoter"). Splicing factors additionally need RBP-Maps (Yeo lab) for the 1400 nt cassette-exon regulatory metagene. See clip-seq/binding-site-annotation.

## Step 9: Motif Analysis (De Novo + CL-Registered)

```bash
# Extract peak sequences (strand-preserving)
bedtools getfasta -fi genome.fa -bed peaks/sample.stringent.bed -s -fo motifs/peaks.fa

# GC-matched 3' UTR background (NOT auto-shuffled, which biases to AU)
bedtools shuffle -i peaks/sample.stringent.bed -g chrom.sizes \
    -incl expressed_3utr.bed -seed 42 > motifs/background.bed
bedtools getfasta -fi genome.fa -bed motifs/background.bed -s -fo motifs/background.fa

# HOMER de novo
findMotifs.pl motifs/peaks.fa fasta motifs/homer \
    -rna -len 5,6,7,8 -p 8 -fasta motifs/background.fa

# mCross for CL-position-registered motif. mCross.pl takes a POSITIONAL FASTA of sequences
# pre-extracted/registered around the CL sites and an output stem (not a BED + genome + -i/-g/-k/-o):
#   bedtools slop -i crosslinks/sample.sites.bed -g genome.sizes -b 10 | bedtools getfasta -fi genome.fa -bed - -s > motifs/peakseqs.fa
mCross.pl motifs/peakseqs.fa motifs/mcross   # see clip-seq/clip-motif-analysis for options
```

UV254 crosslinking has a strong U bias at CL sites; naive logos centered on CL positions are U-enriched even for non-U-binding RBPs. mCross corrects this by registering motif relative to the CL offset. See clip-seq/clip-motif-analysis.

## Step 10: Differential Binding (Optional, Across Conditions)

```r
# DEWSeq window-level NB with the interaction-term design
# The interaction `~ type + condition + type:condition` tests whether IP/SMInput ratio shifts;
# naive `~ condition` confounds binding with expression changes.
library(DEWSeq)
counts <- read.table('counts/merged.tsv', sep='\t', header=TRUE, row.names=1)
colData <- data.frame(
    type = relevel(factor(c('ip','ip','ip','ip','sminput','sminput','sminput','sminput')), ref='sminput'),
    condition = relevel(factor(c('treat','treat','ctrl','ctrl','treat','treat','ctrl','ctrl')), ref='ctrl')
)
dds <- DESeqDataSetFromSlidingWindows(
    countData=counts, colData=colData,
    annotObj='annotation.txt',   # htseq-clip TAB annotation table (named columns), NOT a plain BED
    design = ~ type + condition + type:condition
)
dds <- DESeq(dds)
# with sminput/ctrl as the references, the interaction coefficient is typeip.conditiontreat
res <- results(dds, name='typeip.conditiontreat')
```

See clip-seq/differential-clip for full DEWSeq workflow and the htseq-clip preprocessing required upstream.

## Quality Checkpoints

| Step | Metric | ENCODE target |
|------|--------|---------------|
| Preprocessing | Retention after adapter trim | >= 70% |
| Alignment | Unique mapping rate | >= 60% (eCLIP); >= 70% (iCLIP) |
| Complexity | preseq predicted unique at 100M reads | >= 10M (good); >= 1M (minimum acceptable) |
| Peak calling | FRiP (narrow-binding RBP) | >= 0.005 |
| Peak calling | Stringent peaks log2(IP/SMI) | >= 3 |
| Peak calling | Stringent peaks -log10 p | >= 3 |
| IDR | Rescue ratio | < 2 |
| IDR | Self-consistency ratio | < 2 |
| Annotation | Top RBP-class match expectation | Y (HuR -> 3' UTR; PTBP1 -> intron; FASTKD2 -> chrM) |

## Per-Variant Adjustments

- **PAR-CLIP:** Raise STAR `--outFilterMismatchNoverReadLmax` from 0.04 to 0.07; downstream use PARalyzer or CTK CIMS substitution T->C
- **iCLIP / iCLIP2 multiplexed:** Demultiplex by inline library barcode (NNNXXXXNN) BEFORE umi_tools extract
- **HITS-CLIP:** Use deletion-tolerant aligner (BWA-aln); downstream CTK CIMS deletion mode
- **Repeat-binding RBPs:** STAR `--outFilterMultimapNmax 100 --outSAMmultNmax -1` + CLAM EM rescue
- **m6A profiling:** Switch to clip-seq/m6a-clip (miCLIP2 + m6Aboost or GLORI)
- **Antibody unavailable:** Switch to clip-seq/stamp-antibody-free (STAMP or TRIBE)
- **miRNA targets:** Switch to clip-seq/ago-clip-mirna-targets (chimeric eCLIP / miR-eCLIP)
- **Variant-effect prediction:** Use clip-seq/clip-deep-learning (RBPNet or RNAProt)

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Peaks everywhere, dominated by abundant transcripts | No SMInput normalization | Normalize IP against SMInput; keep log2 FC >= 3 AND -log10 p >= 3 |
| Single-nucleotide resolution lost | Soft-clipping or aggressive 5' trim destroyed the R2 truncation base | STAR `--alignEndsType EndToEnd`; 3'-only `-q 6` trim; never `-g` on R1 |
| PAR-CLIP T->C signal missing | Mismatch ceiling 0.04 filtered the transitions as error | Raise `--outFilterMismatchNoverReadLmax` to 0.07 |
| "Low-complexity" library discarded | Judged on raw duplication (40-70% is normal for CLIP) | Use the unique-fragment count after UMI dedup as the quality metric |
| Motif logo is all-U even for a non-U-binding RBP | Naive CL-centered logo + UV U-bias | mCross CL-registered motif + GC-matched (not shuffled) background |
| 30-50% of peaks labeled "Promoter" | Default `tssRegion=c(-3000,3000)` over-extends for CLIP | Tight `tssRegion=c(-100,100)`, `level='transcript'` |
| Differential binding confounded with expression | `~ condition` design | `~ type + condition + type:condition` interaction (DEWSeq) |

## References

- Van Nostrand EL, Pratt GA, Shishkin AA, et al (2016) Robust transcriptome-wide discovery of RNA-binding protein binding sites with enhanced CLIP (eCLIP). *Nature Methods* 13:508-514. DOI 10.1038/nmeth.3810.
- Van Nostrand EL, Freese P, Pratt GA, et al (2020) A large-scale binding and functional map of human RNA-binding proteins. *Nature* 583:711-719. DOI 10.1038/s41586-020-2077-3. (ENCODE RBP; SMInput + IDR practice.)
- Krakau S, Richard H, Marsico A (2017) PureCLIP: capturing target-specific protein-RNA interaction footprints from single-nucleotide CLIP-seq data. *Genome Biology* 18:240. DOI 10.1186/s13059-017-1364-2.
- Li Q, Brown JB, Huang H, Bickel PJ (2011) Measuring reproducibility of high-throughput experiments. *Annals of Applied Statistics* 5:1752-1779. DOI 10.1214/11-AOAS466. (IDR.)

## Related Skills

- clip-seq/clip-preprocessing - UMI extraction and adapter trimming details
- clip-seq/clip-alignment - STAR ENCODE block + multi-mapper rescue
- clip-seq/clip-qc - Five-gate QC framework
- clip-seq/clip-peak-calling - CLIPper / Skipper / PureCLIP / CTK taxonomy
- clip-seq/crosslink-site-detection - Single-nt CL detection by chemistry
- clip-seq/binding-site-annotation - ChIPseeker + RBP-Maps
- clip-seq/clip-motif-analysis - HOMER + mCross + RBNS validation
- clip-seq/differential-clip - DEWSeq + Flipper for cross-condition
- clip-seq/m6a-clip - miCLIP2 / GLORI / DART for m6A modifications
- clip-seq/stamp-antibody-free - STAMP / TRIBE for antibody-free profiling
- clip-seq/ago-clip-mirna-targets - chimeric eCLIP for direct miRNA-target pairs
- clip-seq/clip-deep-learning - RBPNet / RNAProt for variant-effect prediction
- read-qc/quality-reports - FastQC / MultiQC upstream QC
- reporting/automated-qc-reports - MultiQC aggregates the per-tool QC into one report; gating stays in the five-gate framework, not MultiQC
- alternative-splicing/differential-splicing - Cassette exon tables for RBP-Maps
<!-- END FILE: workflows/clip-pipeline/SKILL.md -->

## 子目录：workflows/cnv-pipeline

<!-- BEGIN FILE: workflows/cnv-pipeline/SKILL.md -->
---
name: bio-workflows-cnv-pipeline
description: Orchestrates the copy-number pipeline from BAM to segmented, integer-called, annotated CNVs, forking on germline-vs-somatic - CNVkit (somatic exome/panel: coverage -> assay-matched reference/PoN -> fix -> segment -> purity/ploidy-aware call), GATK gCNV (germline rare-CNV cohort), and allele-specific callers (ASCAT/FACETS/PURPLE) for purity/ploidy. Use when committing the build + target/access BED + PoN once (assay-matched), building the reference from normals BEFORE segmenting, fitting purity/ploidy BEFORE integer calls in tumors, centering on the true (non-diploid) mode before GISTIC2 recurrence, or routing cfDNA to ichorCNA. Hands mechanism to the copy-number component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: CNVkit
goal_approach_exempt: true
workflow: true
depends_on:
  - copy-number/cnvkit-analysis
  - copy-number/gatk-cnv
  - copy-number/copy-ratio-segmentation
  - copy-number/allele-specific-copy-number
  - copy-number/cnv-visualization
  - copy-number/cnv-annotation
  - copy-number/recurrent-cnv
qc_checkpoints:
  - after_coverage: "Uniform coverage across targets; flag systematically low-depth targets (capture dropout)"
  - after_fix: "log2-ratio noise (.cnr spread/MAD) within tolerance; high bin noise -> over-segmentation"
  - after_call: "Integer CN off a fitted purity/ploidy (not defaults); tumor purity above the ~40% death zone"
  - after_recurrent: "GISTIC2 input is diploid-CENTERED (uncentered WGD inverts recurrence)"
---

## Version Compatibility

Reference examples tested with: CNVkit 0.9.10+, GATK 4.5+ (gCNV / ModelSegments), ASCAT/FACETS/PURPLE (allele-specific), GISTIC2 2.0.23 (recurrent), ichorCNA 0.5+ (cfDNA)

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: GATK gCNV runs COHORT mode (model all normals, no prior) vs CASE mode (score a singlet against a prior model) — order is DetermineGermlineContigPloidy -> GermlineCNVCaller -> PostprocessGermlineCNVCalls. Sequenza's `copynumber` dependency was REMOVED from Bioconductor 3.18+ (needs a fork). GATK gCNV/ModelSegments have no single method paper — cite the GATK docs. Confirm in-tool before quoting.

# CNV Pipeline

**"Detect copy number variants from my sequencing data"** -> Fork germline-vs-somatic, commit the build + target/access BED + assay-matched reference, bias-correct against normals, segment, and integer-call off a fitted purity/ploidy.
- CLI: cnvkit target/access/antitarget -> coverage -> reference(normals) -> fix -> segment -> call  (OR GATK gCNV for germline cohorts)

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

A CNV callset is decided at three seams, not inside the caller.

1. **The reference build + target/access BED + reference/PoN is one made-once commitment inherited by everything downstream.** The capture-kit target BED, the `access` mappability BED, and the annotation refFlat must all be the SAME build as the BAMs (a GRCh37 BED against GRCh38 BAMs silently produces zero-coverage bins). And the PoN is the identity of the assay: it MUST be built from the same capture kit, chemistry, and (ideally) batch as the cases. A PoN from a different kit imports the wrong bias profile and fabricates CNVs at capture boundaries.
2. **The reference/PoN is built BEFORE anything is segmented, and it absorbs shared signal.** `fix` needs the reference to bias-correct; segmenting raw log2 without normalizing segments the capture bias, not biology. Beware: tangent normalization / a pooled PoN ABSORBS any CNV shared across the normals — a real common CNV becomes invisible; GC correction alone does NOT remove the replication-timing wave.
3. **The diploid baseline is a commitment, not a given — fit purity/ploidy BEFORE integer calls in tumors.** In WGD/hyper-aneuploid tumors the data mode is not diploid; naive centering inverts every call. `cnvkit.py call` with wrong `--purity`/`--ploidy` (or defaults on an impure/WGD tumor) assigns integer copy numbers off the wrong baseline. Fit purity/ploidy (ASCAT/FACETS/PURPLE) first; below ~40% purity calls degrade and below ~20% no bulk caller works.

## Pipeline map

```
BAM (tumor +/- matched normal, OR germline cohort)
  | fork: germline rare-CNV cohort? --> GATK gCNV  (copy-number/gatk-cnv)
  v  else somatic exome/panel:
  | [1] target/access/antitarget BED (build-matched)   (copy-number/cnvkit-analysis)
  v
  | [2] per-sample coverage
  v
  | [3] build reference/PoN from NORMALS first (assay-matched)
  v     ^-- tangent absorbs CNV shared across the PoN
  | [4] fix (bias-correct) -> segment -> call
  v     ^-- purity/ploidy fitted BEFORE integer call (copy-number/allele-specific-copy-number)
  | [5] visualize + gene-level annotate            (copy-number/cnv-visualization, cnv-annotation)
  v
  | [6] (cohort) center on true mode -> GISTIC2 recurrence  (copy-number/recurrent-cnv)
  v
Segmented, integer-called, annotated CNVs
```

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Build + target/access/refFlat BED | Any build mismatch -> zero-coverage bins / shifted annotations |
| Reference / PoN (assay-matched) | A different-kit PoN imports the wrong bias -> false CNVs at capture boundaries; tangent absorbs CNVs shared across the PoN |
| Purity/ploidy (fitted, not default) | Wrong baseline shifts every integer call; WGD inverts calls |
| Diploid centering (cohort) | Uncentered WGD segments into GISTIC2 invert recurrence |

## The canonical order and why

1. **Prepare target/access/antitarget BEDs** on the committed build.
2. **Per-sample coverage** (target + antitarget/off-target bins).
3. **Build the reference/PoN from normals FIRST** — order-trap: `fix` needs the reference; segmenting raw log2 segments capture bias.
4. **fix -> segment -> call**, with purity/ploidy fitted BEFORE the integer call — order-trap: default purity/ploidy on an impure/WGD tumor mis-assigns every integer CN.
5. **Visualize + gene-level annotate** (positive control: known CNVs recovered if present).
6. **(Cohort) center on the true mode, THEN GISTIC2** — order-trap: uncentered WGD inverts recurrence; and do NOT concatenate per-sample `.cns` and call recurrence naively — feed a diploid-centered `.seg` matrix to GISTIC2.

## Choosing the caller (the germline-vs-somatic fork)

Pipeline-level selection only; mechanism lives in the component skills.

| Situation | Lean toward | Hand off to |
|-----------|-------------|-------------|
| Exome/targeted panel, somatic (tumor) CNV | CNVkit (target + antitarget bins) | copy-number/cnvkit-analysis |
| Germline rare-CNV from a cohort of exomes | GATK gCNV (DetermineGermlineContigPloidy -> GermlineCNVCaller -> PostprocessGermlineCNVCalls) | copy-number/gatk-cnv |
| WGS, need allele-specific CN + purity/ploidy | ASCAT / Sequenza / FACETS / PURPLE | copy-number/allele-specific-copy-number |
| Relative copy-ratio segments (research) | GATK ModelSegments/CallCopyRatioSegments | copy-number/copy-ratio-segmentation |
| Cohort recurrent/driver CNV | GISTIC2 (diploid-centered input) | copy-number/recurrent-cnv |
| cfDNA / low-pass tumor fraction | ichorCNA (NOT CNVkit) | workflows/liquid-biopsy-pipeline |

## Primary path: CNVkit (somatic exome/panel)

```bash
# 1. Targets on the committed build (annotate with refFlat, split for WES)
cnvkit.py target capture_targets.bed --annotate refFlat.txt --split -o targets.bed
cnvkit.py access genome.fa -o access.bed
cnvkit.py antitarget targets.bed --access access.bed -o antitargets.bed

# 2-3. Coverage per sample, then build the reference from NORMALS (assay-matched) BEFORE any fix
cnvkit.py coverage $bam targets.bed -o cov/${s}.targetcoverage.cnn
cnvkit.py coverage $bam antitargets.bed -o cov/${s}.antitargetcoverage.cnn
cnvkit.py reference cov/normal*.{,anti}targetcoverage.cnn --fasta genome.fa -o reference.cnn

# 4. fix (bias-correct) -> segment -> call. Fit purity/ploidy first (ASCAT/FACETS) for tumors:
cnvkit.py fix cov/${s}.targetcoverage.cnn cov/${s}.antitargetcoverage.cnn reference.cnn -o ${s}.cnr
cnvkit.py segment ${s}.cnr -o ${s}.cns
cnvkit.py call ${s}.cns --purity 0.6 --ploidy 2 -o ${s}.call.cns   # purity/ploidy from an allele-specific fit
```

A runnable somatic CNVkit script (manual target -> coverage -> reference -> fix -> segment -> call path) is in this skill's examples/; germline cohorts use GATK gCNV (copy-number/gatk-cnv), not CNVkit.

## QC checkpoints between steps

| After | Gate | Interpretation |
|-------|------|----------------|
| Coverage | Uniform depth across targets; flag low-depth targets | Capture dropout -> phantom deletions |
| fix | `.cnr` log2 spread / MAD within tolerance | High bin noise is the #1 CNV false-positive lever (over-segmentation) |
| segment/call | Sane segment count; integer CN consistent with known events; purity plausible | Over-segmentation = noisy reference / low purity; wrong purity shifts every call |
| annotate | Known CNVs recovered (positive control) | Build/BED mismatch surfaces as missing known events |
| recurrent | GISTIC2 input diploid-centered | Uncentered WGD inverts recurrence |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Zero-coverage bins / shifted annotations | Target BED build != BAM build | Pin one build across BED, access, refFlat, BAMs |
| False CNVs at capture boundaries | PoN from a different kit/chemistry | Build the PoN from the same kit/chemistry/batch |
| A real common CNV vanishes | Tangent/pooled PoN absorbed the shared signal | Use a PoN that does not carry the event, or germline-CNV logic |
| Every integer call shifted / inverted | Default purity/ploidy on an impure/WGD tumor | Fit purity/ploidy (ASCAT/FACETS/PURPLE) BEFORE `call` |
| Inverted recurrence in the cohort | Uncentered WGD segments into GISTIC2 | Center on the true (non-diploid) mode first |
| Cohort recurrence looks wrong | Concatenated per-sample `.cns` naively | Feed a diploid-centered `.seg` matrix to GISTIC2 (copy-number/recurrent-cnv) |
| Sequenza install fails | `copynumber` removed from Bioconductor 3.18+ | Use a maintained fork (ShixiangWang/igordot) |

## Related Skills

- copy-number/cnvkit-analysis - CNVkit coverage/fix/segment/call details
- copy-number/gatk-cnv - GATK gCNV (germline cohort) and ModelSegments
- copy-number/copy-ratio-segmentation - segmentation algorithm and depth-bias correction
- copy-number/allele-specific-copy-number - purity/ploidy and integer allele-specific CN (ASCAT/FACETS/PURPLE)
- copy-number/cnv-visualization - scatter/diagram/heatmap plotting
- copy-number/cnv-annotation - gene-level CNV annotation
- copy-number/recurrent-cnv - cohort recurrent/driver CNV with GISTIC2
- copy-number/hrd-scoring - HRD scar score for PARP eligibility
- workflows/liquid-biopsy-pipeline - cfDNA tumor-fraction CNV (ichorCNA)
- workflows/somatic-variant-pipeline - consumes purity/ploidy for VAF-to-CCF

## References

- Steele CD, Abbasi A, Islam SMA, et al (2022) Signatures of copy number alterations in human cancer. *Nature* 606:984-991. DOI 10.1038/s41586-022-04738-6. (copy-number signatures need ABSOLUTE CN.)
- Telli ML, Timms KM, Reid J, et al (2016) Homologous Recombination Deficiency (HRD) score predicts response to platinum-containing neoadjuvant chemotherapy. *Clinical Cancer Research* 22:3764-3773. DOI 10.1158/1078-0432.CCR-15-2477. (GIS >= 42 HRD threshold.)
- GATK gCNV / ModelSegments have no single method paper — cite the GATK/Broad documentation.
<!-- END FILE: workflows/cnv-pipeline/SKILL.md -->

## 子目录：workflows/crispr-editing-pipeline

<!-- BEGIN FILE: workflows/crispr-editing-pipeline/SKILL.md -->
---
name: bio-workflows-crispr-editing-pipeline
description: Orchestrates an end-to-end CRISPR editing experiment design from target gene to delivery-ready, validatable constructs. Sequences guide design, off-target assessment, edit-modality selection (knockout, base editing, prime editing, HDR knock-in), and template/donor design, with a QC checkpoint at each handoff. Use when designing a complete CRISPR experiment for knockout, point correction, or tagging and the order of operations, the modality decision, and the cross-cutting traps are needed rather than a single step. Defers each step's mechanics to the genome-engineering skills.
tool_type: mixed
primary_tool: CRISPOR
workflow: true
depends_on:
  - genome-engineering/grna-design
  - genome-engineering/off-target-prediction
  - genome-engineering/base-editing-design
  - genome-engineering/prime-editing-design
  - genome-engineering/hdr-template-design
qc_checkpoints:
  - after_grna_design: "Context-valid on-target shortlist (CRISPOR: Rule Set 2 for U6/lentiviral, CRISPRscan for T7/embryo); reject TTTT and GC extremes; rank by predicted frameshift/out-of-frame fraction, not raw activity; carry 3-6 guides in an early constitutive NMD-competent exon"
  - after_offtarget: "Escalate predicted -> detected -> validated; reject guides with a low-mismatch high-CFD off-target in a gene; variant-aware (gnomAD) for therapeutic guides; high-fidelity nuclease in the delivery format used"
  - after_template: "Blocking (PAM/seed) mutation present AND codon-checked; edit within ~10 bp of the cut; donor format matches cell type (ssODN/lssDNA/dsDNA/AAV; HITI for post-mitotic); report edit:indel purity for base editing"
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, pandas 2.2+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

This workflow coordinates the five genome-engineering skills; it does not re-implement their scoring. Real on-target ranking comes from CRISPOR (context-valid model), off-target nomination from Cas-OFFinder/CRISPRme, base-editor outcomes from BE-Hive, and prime-editing ranking from PRIDICT/DeepPrime -- the embedded code is illustrative orchestration only.

# CRISPR Editing Pipeline

**"Design a complete CRISPR editing experiment for my target"** -> Run guide design -> off-target assessment -> edit-modality selection -> template/donor design -> validation, applying a QC checkpoint at each handoff and routing every mechanic to the relevant genome-engineering skill.
- Python: orchestrate the stages; enumerate/filter candidate guides with `Bio.Seq`
- CLI/web: CRISPOR (on-target + off-target), Cas-OFFinder/CRISPRme (off-target), BE-Hive, PRIDICT

## The Single Most Important Modern Insight -- the pipeline is a chain of handoffs, each with a checkpoint, and the pivotal decision is the edit modality

A CRISPR experiment fails most often not at one step but at a handoff where an unstated assumption carries through: a guide picked by on-target score that turns out non-specific, an "efficient" guide that never knocks out the protein, a base edit reported by efficiency that is a genotype soup, an HDR donor with no blocking mutation whose edit is silently re-cut. The workflow's job is to make each handoff explicit and gated. The pivotal branch is **which edit modality**: a transition (C->T/A->G) is usually a base-editing job; any other small precise edit is prime editing; a knockout is a plain nuclease; a large or non-transition insertion is HDR (or PE+integrase). Choosing the modality first reframes every downstream step. The cross-cutting traps the checkpoints exist to catch: **on-target activity != specificity** (two separate axes), **efficient editing != knockout** (frameshift fraction and NMD-competent exon biology decide it), **base-editor efficiency != purity** (bystanders), **a donor without a blocking mutation self-destructs** (re-cutting reads out as failed HDR), and **predicted != detected != validated** for off-targets.

## Edit-Modality Decision Tree (the pivotal branch)

| Goal / edit | Modality | Route to |
|-------------|----------|----------|
| Gene knockout (any frameshift) | nuclease + NHEJ | grna-design (rank by frameshift fraction) |
| Knockout without a DSB / non-dividing / multiplex | base-editor premature stop or splice disruption | base-editing-design |
| C*G->T*A or A*T->G*C transition | base editing (CBE/ABE) | base-editing-design |
| C->G transversion | CGBE | base-editing-design |
| Other transversion, small indel, combined edit | prime editing | prime-editing-design |
| Small precise edit, no DSB tolerated | prime editing (PE) | prime-editing-design |
| Tag / reporter / allele replacement (cycling cells) | HDR knock-in | hdr-template-design |
| Large insertion / post-mitotic cells | HDR (AAV/HITI) or PE+integrase (PASTE/twinPE) | hdr-template-design / prime-editing-design |

## Workflow Overview

```
Target gene / position
        |
        v
[1. Guide design] ----> CRISPOR (context-valid on-target) + outcome model (Bae microhomology / inDelphi)
        |                CHECKPOINT: shortlist 3-6, frameshift-rich, early constitutive exon
        v
[2. Off-target assessment] ----> Cas-OFFinder (+bulges) / CRISPRme (variant-aware) + CFD
        |                CHECKPOINT: no low-mm high-CFD off-target in a gene; predicted->detected->validated
        v
    DECISION: which edit modality?
        |
    +----------+-------------+--------------+-------------+
    v          v             v              v             v
[3a. KO]   [3b. Base edit] [3c. Prime edit] [3d. HDR knock-in]
 frameshift  window+purity   pegRNA panel     donor + codon-checked block
        |          |              |              |
        v          v              v              v
[4. Validation] ----> amplicon deep-seq (CRISPResso2); report purity/indels; state LoD
```

## Stage 1 -- Guide Design (-> grna-design)

**Goal:** A shortlist of 3-6 specificity-checkable guides whose predicted repair outcome is frameshift-rich, in an early constitutive NMD-competent exon.

**Approach:** Establish the delivery context (it sets the valid on-target model and the hard filters), enumerate PAMs on both strands, drop TTTT/GC-extreme guides, rank on-target with the context-valid model via CRISPOR (not a hand-rolled score), and rank knockout candidates by predicted frameshift/out-of-frame fraction (Bae microhomology / inDelphi). **Checkpoint:** carry 3-6 guides; do not commit on raw activity alone.

## Stage 2 -- Off-Target Assessment (-> off-target-prediction)

**Goal:** Reject promiscuous guides and, for therapeutics, establish an evidence-laddered specificity profile.

**Approach:** Enumerate candidates with Cas-OFFinder including bulges and a relaxed PAM; rank by CFD; for a research knockout this in-silico pass is sufficient. For a therapeutic, run variant-aware nomination (CRISPRme vs gnomAD + individual), choose a high-fidelity nuclease in the delivery format used, and plan empirical discovery + amplicon validation. **Checkpoint:** on-target score does not predict specificity; treat predicted/detected/validated distinctly.

## Stage 3 -- Modality-Specific Design

**Goal:** Produce the construct(s) for the chosen modality.

**Approach:** Branch by the decision tree. Knockout -> the frameshift-ranked guide. Base editing -> position the target base at the window peak, minimize bystanders, choose the editor variant, report the genotype spectrum (-> base-editing-design). Prime editing -> a PBS x RTT panel with PAM-disrupting/MMR-evading silent edits and a 3' motif, ranked by PRIDICT/DeepPrime (-> prime-editing-design). HDR -> the donor format for the cell type with a mandatory codon-checked blocking mutation and the cut within ~10 bp of the edit (-> hdr-template-design). **Checkpoint:** blocking mutation present and codon-checked; base-editing purity reported.

## Stage 4 -- Validation

**Goal:** Quantify the intended edit and its byproducts.

**Approach:** Design genotyping/amplicon primers around the edit (-> primer-design/primer-basics; keep both 3' ends off the cut site and any expected indel, and confirm the amplicon is unique near paralogs/pseudogenes -> primer-design/primer-specificity) and quantify outcomes by amplicon deep sequencing (CRISPResso2 / BE-Analyzer) -- intended-edit rate, indels, and (for base/prime editing) product purity -- stating the limit of detection (-> crispr-screens/crispresso-editing). The critical hand-off across the wet-lab gap: give CRISPResso2 the UNEDITED amplicon of the specific system as `--amplicon_seq` (the actual wild-type/pre-edit sequence -- matching the cell line's SNPs and primer product, NOT a mismatched canonical genome), the actual protospacer as `--guide_seq` so the quantification window centers on the cut, and for HDR/KI the intended edit as `--expected_hdr_amplicon_seq`. Reads are scored "unmodified" by matching `--amplicon_seq`, so supplying the EDITED sequence there makes real edits score as unmodified (~0%) with no error raised. **Checkpoint:** report purity and LoD, not a lone efficiency number.

## Common Errors (integration level)

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Top guide has a near-perfect off-target | picked by on-target score alone | re-rank by specificity; on-target and specificity are separate axes |
| Efficient editing, no knockout phenotype | in-frame indels / late-exon / compensation | rank by frameshift fraction; target an early constitutive exon; verify protein |
| Base edit "80% efficient" but messy genotypes | bystanders in the window | report the spectrum; reposition or use a narrowed-window editor |
| HDR gives only indels | donor lacks a blocking mutation | add a codon-checked PAM/seed block; the edit was re-cut |
| Validation shows ~0% editing on a working edit | EDITED (or wrong) sequence supplied as `--amplicon_seq`, so edited reads match the reference / wrong guide window | give CRISPResso2 the UNEDITED reference as `--amplicon_seq` (+ `--expected_hdr_amplicon_seq` for HDR) and the actual `--guide_seq` |
| "No off-targets" claimed | LoD not stated / reference-only | state the LoD; variant-aware for therapeutics |

## References

- Doench JG, Fusi N, Sullender M, et al. (2016). Optimized sgRNA design to maximize activity and minimize off-target effects of CRISPR-Cas9. *Nat Biotechnol* 34(2):184-191.
- Concordet JP, Haeussler M (2018). CRISPOR: intuitive guide selection for CRISPR/Cas9 genome editing experiments and screens. *Nucleic Acids Res* 46(W1):W242-W245.
- Bae S, Park J, Kim JS (2014). Cas-OFFinder: a fast and versatile algorithm that searches for potential off-target sites of Cas9 RNA-guided endonucleases. *Bioinformatics* 30(10):1473-1475. [off-target search]
- Bae S, Kweon J, Kim HS, Kim JS (2014). Microhomology-based choice of Cas9 nuclease target sites. *Nat Methods* 11(7):705-706. [microhomology/MMEJ frameshift-outcome predictor -- the exp(-deletionLength/20) length weight]
- Clement K, Rees H, Canver MC, et al. (2019). CRISPResso2 provides accurate and rapid genome editing sequence analysis. *Nat Biotechnol* 37(3):224-226.
- Paquet D, Kwart D, Chen A, et al. (2016). Efficient introduction of specific homozygous and heterozygous mutations using CRISPR/Cas9. *Nature* 533(7601):125-129.

## Related Skills

- genome-engineering/grna-design - Guide design and outcome-aware knockout ranking
- genome-engineering/off-target-prediction - Specificity assessment and the evidence ladder
- genome-engineering/base-editing-design - CBE/ABE window, bystander purity, off-target classes
- genome-engineering/prime-editing-design - pegRNA panel design and PE system selection
- genome-engineering/hdr-template-design - Donor format and codon-checked blocking mutation
- crispr-screens/crispresso-editing - Quantify and validate editing outcomes from amplicon reads
- crispr-screens/library-design - Scale single-gene design to a pooled screen
- primer-design/primer-basics - Design the genotyping/amplicon primers around the edit
- primer-design/primer-specificity - Confirm the genotyping amplicon is unique near paralogs/pseudogenes
<!-- END FILE: workflows/crispr-editing-pipeline/SKILL.md -->

## 子目录：workflows/crispr-screen-pipeline

<!-- BEGIN FILE: workflows/crispr-screen-pipeline/SKILL.md -->
---
name: bio-workflows-crispr-screen-pipeline
description: End-to-end pooled and single-cell CRISPR screen analysis from FASTQ to hit genes. Orchestrates library design QC, guide counting, six-stage screen QC (plasmid Gini, replicate Pearson, CEGv2 PR-AUC, copy-number artifact), method-appropriate hit calling across MAGeCK RRA/MLE, BAGEL2, drugZ, JACKS, and Chronos, cancer-cell-line copy-number correction (CRISPRcleanR / Chronos), batch correction for multi-batch screens, and the specialized branches for combinatorial paralog screens, single-cell Perturb-seq, base-editor variant-function screens, prime-editor screens, and in vivo bottleneck-aware screens. Use when analyzing any pooled CRISPR screen end-to-end, matching the hit-calling method to the experimental design, integrating copy-number correction into the pipeline, or branching the workflow for single-cell, combinatorial, base-editor, prime-editor, or in vivo variants.
tool_type: mixed
primary_tool: MAGeCK
workflow: true
depends_on:
  - crispr-screens/library-design
  - crispr-screens/screen-qc
  - crispr-screens/mageck-analysis
  - crispr-screens/bagel-essentiality
  - crispr-screens/drugz-chemogenomic
  - crispr-screens/jacks-analysis
  - crispr-screens/hit-calling
  - crispr-screens/copy-number-correction
  - crispr-screens/batch-correction
  - crispr-screens/crispresso-editing
  - crispr-screens/base-editing-analysis
  - crispr-screens/prime-editing-screens
  - crispr-screens/perturb-seq-analysis
  - crispr-screens/combinatorial-screens
  - crispr-screens/in-vivo-screens
qc_checkpoints:
  - after_counting: ">65% mapping rate; <0.5% zero-count in plasmid; Gini <0.1 on plasmid"
  - after_qc: "Replicate Pearson on log-counts >=0.8 (MAGeCK-VISPR floor; >0.85 acceptable, >0.95 ideal); Spearman >0.7; CEGv2 PR-AUC >0.7"
  - after_cn_correction: "Spearman ρ between CN and gene LFC abs <0.10 post-correction (literature 'significant bias' band; <0.05 is a stricter target). Requires a matched CN profile, which the unsupervised CRISPRcleanR path never loads -- compute in crispr-screens/copy-number-correction, or use Chronos, which takes CN as input"
  - after_hit_calling: "Tier-1 hits = 3-method consensus; Tier-2 = 2 of 3; Tier-3 = single-method exploratory"
---

## Version Compatibility

Reference examples tested with: MAGeCK 0.5.9+, BAGEL2 1.0.5+, drugZ Aug 2019+, JACKS 0.2.0+, Chronos 2.0+, CRISPRcleanR 3.0+ (R), Pertpy 0.6+, PRIDICT2, CRISPResso2 2.2.14+, MAGeCKFlute 2.0+, pandas 2.2+, numpy 1.26+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `mageck --version`, `BAGEL.py fc --help`, `drugz -h`, `CRISPResso --version`
- Python: `pip show pertpy scanpy anndata` (mageck-vispr via conda `mageck --version`; JACKS/Chronos are GitHub installs — check their repos)
- R: `packageVersion('CRISPRcleanR')`, `packageVersion('MAGeCKFlute')`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## CRISPR Screen Pipeline

**"Analyze my pooled or single-cell CRISPR screen end-to-end"** -> Pick the screen design branch, run guide counting, audit six QC stages, apply copy-number and batch correction as needed, run the design-matched hit-calling method, and consolidate across methods for high-confidence hits.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

Every LFC, QC gate, and hit call is computed against a reference that is committed once at library-order time; a wrong-but-silent commitment invalidates the endpoint with no error thrown.

1. **The guide LIBRARY definition (guide->gene map + control classes) is the denominator, the calibrator, and the training reference — committed once.** The library must carry non-targeting controls (NTCs, ~1%, the null distribution) AND CEGv2 reference essentials + NEGv1 non-essentials (the positive/negative calibrators for PR-AUC and BAGEL2/Chronos priors). NTCs calibrate the null/FDR; CEGv2/NEGv1 calibrate PR-AUC — swapping or dropping a class silently breaks FDR or QC.
2. **The baseline choice has a right answer and rescales every hit.** Dropout/enrichment LFC is against a baseline: plasmid pool for the cloning-bottleneck baseline, Day-0/T0 for the biology baseline, and vehicle (NOT Day-0) for drug screens — drug-vs-Day-0 conflates drug effect with normal proliferation.
3. **Copy-number correction MUST precede hit calling in cancer cell lines.** Multiple simultaneous Cas9 cuts at amplified loci trigger a gene-independent DNA-damage/G2 arrest (Aguirre 2016; Munoz 2016; the effect appears in both TP53-mutant and TP53-wild-type lines, though Aguirre 2016 found TP53 status correlates with its magnitude -- separately, Ihry 2018 / Haapaniemi 2018 report p53-dependent toxicity of Cas9 cutting generally), so amplified regions look essential regardless of gene function; calling hits first yields false essentials at ERBB2/MYC/FGFR1. Run CRISPRcleanR/Chronos BEFORE hit calling, or use CRISPRi to bypass the DSB. This is a pipeline step, not a post-hoc interpretation. Verifying `abs(rho(LFC,CN)) < 0.1` afterwards needs a matched CN profile: CRISPRcleanR corrects unsupervised without one, so the check happens in crispr-screens/copy-number-correction (or use Chronos, which consumes CN directly).
4. **CEGv2 essential-gene depletion is the screen's built-in positive control.** If known essentials do not deplete (CEGv2 PR-AUC below ~0.7), the screen failed selection and NO novel hit is trustworthy regardless of its p-value — the seam analog of a spike-in. Normalize -> QC -> (CN correct) -> hit-call, never hit-call first; add batch as an MLE covariate, never pre-corrected with ComBat on counts (distorts the NB mean-variance the caller assumes).

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Guide library (guide->gene map + NTC/CEGv2/NEGv1 control classes) | The counting denominator, the QC calibrator, the hit-calling priors; a missing/misassigned class breaks FDR or PR-AUC |
| Baseline (plasmid pool / Day-0 / vehicle) | Every LFC; drug-vs-Day-0 conflates drug effect with proliferation |
| Screen type (dropout / enrichment / FACS / drug-modifier) | Which hit-calling method is even valid |
| Copy-number profile (cancer lines) | Whether amplicon artifacts are removed before hit calling; residual rho(LFC,CN) is the tell |

## Pipeline Branches by Screen Design

```
                    Library Design ([[library-design]])
                              |
                              v
                FASTQ Files -> mageck count -> count matrix
                              |
                              v
                Six-Stage QC ([[screen-qc]])
                              |
        +---------------------+---------------------+
        |                                            |
        v                                            v
  Cancer cell line?                          Non-cancer?
  Apply CN correction                        No CN correction needed
  ([[copy-number-correction]])
        |                                            |
        +---------------------+---------------------+
                              v
                  Multi-batch? Apply batch covariate
                  ([[batch-correction]])
                              |
                              v
                 Pick hit-calling method by design ([[hit-calling]])
                              |
        +-----------+---------+---------+-----------+-----------+
        |           |         |         |           |           |
        v           v         v         v           v           v
    2-cond       Time      Drug      Essential   Multi-       Specialized
    MAGeCK RRA   MAGeCK    drugZ     BAGEL2      screen       (PE/BE/SC/
                 MLE                              JACKS or     in vivo/
                                                  Chronos      combinat)
        |           |         |         |           |           |
        +-----------+---------+---------+-----------+-----------+
                              v
                   Tier-based consensus
                              v
                Orthogonal validation
```

## Step 1: Library Design and Pre-Screen Validation

Reference [[library-design]] for full library composition. Verify before sequencing:
- Plasmid pool Gini <0.1 (Li W et al 2015 MAGeCK-VISPR, Genome Biol 16:281)
- >=99% guides detected at >25 reads/guide
- Skew (p90/p10) <2
- NTCs comprise ~1% of library; CEGv2 reference essentials + NEGv1 non-essentials included

## Step 2: Guide Counting

**Goal:** Turn raw FASTQ into a per-guide count matrix with consistent sample labels.

**Approach:** Run mageck count with the library CSV, sample labels in column order, the vector adapter trimmed off the 5' end, and median normalization.

```bash
mageck count \
    --list-seq library.csv \
    --sample-label Plasmid,Day0,Veh_r1,Veh_r2,Drug_r1,Drug_r2 \
    --fastq Plasmid.fq.gz Day0.fq.gz Veh_r1.fq.gz Veh_r2.fq.gz Drug_r1.fq.gz Drug_r2.fq.gz \
    --norm-method median \
    --output-prefix experiment \
    --trim-5 5   # integer base-count (or AUTO), NOT an adapter sequence; 5 trims the CACCG scaffold
```

For Cas12a libraries (Inzolia, in4mer): see [[combinatorial-screens]]. For 10X single-cell direct capture: use cellranger-arc or pertpy-aware counting; see [[perturb-seq-analysis]].

## Step 3: Six-Stage Quality Control

**Goal:** Decide whether the screen is analyzable before calling any hits, using six orthogonal QC stages.

**Approach:** Load the count matrix, compute per-sample Gini, zero-fraction, and depth plus replicate correlation against the hard gates below. Essential-gene recovery (CEGv2 PR-AUC) is a separate check computed once endpoint-vs-baseline LFCs exist (it needs CEGv2/NEGv1 labels) -- see screen-qc.

```python
import pandas as pd
import numpy as np

counts = pd.read_csv('experiment.count.txt', sep='\t', index_col=0)
genes = counts['Gene']
count_matrix = counts.drop('Gene', axis=1)

def gini(x):
    x = np.sort(x[x > 0].astype(float))
    if x.size == 0:
        return np.nan
    n = x.size
    cumx = np.cumsum(x)
    return (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n

per_sample = pd.DataFrame({
    'pct_zero': (count_matrix == 0).sum() / len(count_matrix) * 100,
    'gini': count_matrix.apply(gini),
    'reads_per_sgrna': count_matrix.sum() / len(count_matrix),
})

log_counts = np.log10(count_matrix + 1)
pearson = log_counts.corr()
print(per_sample)
print('Replicate Pearson:', pearson.values[pearson.values < 1].mean())
```

Hard gates from [[screen-qc]]:
- Plasmid Gini <0.1; endpoint <0.3 (or <0.55 for heavy drug screens)
- Replicate Pearson on log-counts >0.85
- CEGv2 PR-AUC >0.7 against the Hart 2017 reference essential gene set (community convention, not a threshold defined in that paper)
- Reads per sgRNA per sample >=300 (DepMap convention)

## Step 4: Copy-Number Correction (Cancer Cell Lines Only)

If screening in a cancer cell line, apply CRISPRcleanR (unsupervised, no CN profile needed) or Chronos (joint with CN profile). Required to remove Aguirre 2016 / Munoz 2016 amplicon artifact.

**Goal:** Strip the copy-number amplicon artifact that makes amplified regions look essential in cancer lines.

**Approach:** Run CRISPRcleanR unsupervised genome-wide LFC correction (no CN profile needed), then feed the corrected counts downstream; for DepMap-scale panels with matched CN, use Chronos instead.

```r
library(CRISPRcleanR)
data(KY_Library_v1.0)
norm <- ccr.NormfoldChanges('experiment.count.txt', min_reads = 30, EXPname = 'screen',
                              libraryAnnotation = KY_Library_v1.0)   # arg 1 is the file PATH
gw_lfc <- ccr.logFCs2chromPos(norm$logFCs, KY_Library_v1.0)          # $logFCs, not $norm_fold_changes
cleaned <- ccr.GWclean(gw_lfc, display = TRUE, label = 'screen')
corrected_counts <- ccr.correctCounts('screen', norm$norm_counts, cleaned,
                                        KY_Library_v1.0)              # (CL, normalised_counts, correctedFCs, libraryAnnotation)
# ccr.correctCounts returns an in-memory frame; it does NOT write this file. Persist it, because the
# hit callers below read a count TABLE from disk -- the CN-correction commitment in rule 3 is only
# honored if that file, not the raw experiment.count.txt, is what MAGeCK / BAGEL2 / drugZ consume.
write.table(corrected_counts, 'screen_cleanr_corrected_counts.txt',
            sep = '\t', quote = FALSE, row.names = FALSE)
```

For DepMap-scale panels with longitudinal data + matched CN, use Chronos. See [[copy-number-correction]].

## Step 5: Batch Correction (Multi-Batch Screens)

For multi-batch screens, add batch as a covariate in MAGeCK MLE rather than pre-correcting with ComBat. See [[batch-correction]] for full decision tree.

## Step 6: Method-Matched Hit Calling

**Goal:** Call hits with the method that matches the experimental design, plus at least one orthogonal method for consensus.

**Approach:** Pick by design - RRA or BAGEL2 for two-condition essentiality, MLE for time course, drugZ for drug-modifier, JACKS for multi-screen, Chronos for cancer panels - and run two methods so the consensus step has something to reconcile.

### 6a. Two-condition essentiality (MAGeCK RRA or BAGEL2)

Cancer cell lines: pass the CRISPRcleanR-corrected count file (`screen_cleanr_corrected_counts.txt` from Step 4) as `--count-table`/`-i` below, NOT the raw `experiment.count.txt` — the CN-correction commitment is only honored if the corrected counts are what the hit caller reads.

The `Day0`/`Day14_r*` columns below illustrate a time-course dropout design; they must match the count step's `--sample-label` (the drug-screen count above uses `Plasmid,Day0,Veh_r*,Drug_r*`).

```bash
mageck test \
    --count-table experiment.count.txt \
    --treatment-id Day14_r1,Day14_r2,Day14_r3 \
    --control-id Day0 \
    --norm-method median \
    --output-prefix essentiality_rra
```

```bash
BAGEL.py fc -i experiment.count.txt -o experiment -c Day0 --min-reads 30   # -o is an output LABEL; fc writes experiment.foldchange
BAGEL.py bf -i experiment.foldchange -o bayes_factor.txt -e CEGv2.txt -n NEGv1.txt \
    -c Day14_r1,Day14_r2,Day14_r3   # add -b -NB 1000 for bootstrapping; -k is not a bf option
```

### 6b. Time-course / multi-condition (MAGeCK MLE)

```bash
mageck mle --count-table experiment.count.txt --design-matrix design.txt \
    --output-prefix timecourse_mle --norm-method median
```

### 6c. Drug-modifier (drugZ)

```bash
python drugz.py \
    -i experiment.count.txt \
    -o drugz_output.txt \
    -c Veh_r1,Veh_r2 \
    -x Drug_r1,Drug_r2 \
    -p 5
```

drugZ requires vehicle as control, not Day-0. See [[drugz-chemogenomic]].

### 6d. Multi-screen joint analysis (JACKS)

```bash
python run_JACKS.py experiment.count.txt replicatemap.txt guidemap.txt \
    --rep_hdr Replicate --sample_hdr Sample --ctrl_sample_hdr Control \
    --sgrna_hdr sgRNA --gene_hdr Gene --outprefix jacks_out --apply_w_hp
```

### 6e. Cancer cell-line panels (Chronos)

```python
import chronos
# All three inputs must be dicts of DataFrame keyed by library name, not bare DataFrames.
model = chronos.Chronos(sequence_map={'screen': sequence_map},
                          guide_gene_map={'screen': guide_gene_map},
                          readcounts={'screen': counts_df})   # readcounts=, not reads=
model.train(nepochs=301)                                 # nepochs (default 301), not n_steps
gene_effects = model.gene_effect                         # attribute, not a method call
# Copy-number correction is a separate post-hoc step (chronos.alternate_CN(gene_effect, copy_number) / a CN matrix), not a constructor arg
```

DepMap quarterly standard; handles CN bias + screen quality + longitudinal jointly.

## Step 7: Tier-Based Consensus

**Goal:** Consolidate the per-method calls into confidence tiers.

**Approach:** Merge each method's gene-level result, threshold each to a per-method hit flag, and tier by how many methods agree (Tier 1 = all three, Tier 2 = two of three).

```python
mageck = pd.read_csv('essentiality_rra.gene_summary.txt', sep='\t')[['id', 'neg|fdr']].rename(
    columns={'id': 'gene', 'neg|fdr': 'mageck_neg_fdr'})
bagel = pd.read_csv('bayes_factor.txt', sep='\t')[['GENE', 'BF']].rename(
    columns={'GENE': 'gene', 'BF': 'bagel_bf'})
drugz_df = pd.read_csv('drugz_output.txt', sep='\t')[['GENE', 'fdr_synth']].rename(
    columns={'GENE': 'gene', 'fdr_synth': 'drugz_synth_fdr'})

merged = mageck.merge(bagel, on='gene', how='outer').merge(drugz_df, on='gene', how='outer')
merged['mageck_hit'] = merged['mageck_neg_fdr'] < 0.05
merged['bagel_hit'] = merged['bagel_bf'] > 6
merged['drugz_hit'] = merged['drugz_synth_fdr'] < 0.05
merged['tier'] = merged[['mageck_hit', 'bagel_hit', 'drugz_hit']].astype(int).sum(axis=1)
tier1 = merged[merged['tier'] >= 3]
tier2 = merged[merged['tier'] == 2]
merged.to_csv('tier_consensus.csv', index=False)   # the documented deliverable; the frame above is otherwise in-memory only
```

## Specialized Branches

| Screen design | Specialized workflow |
|---------------|----------------------|
| Single-cell Perturb-seq / CROP-seq / Multiome | [[perturb-seq-analysis]] -- Pertpy + Mixscape + SCEPTRE |
| Combinatorial paralog (Cas12a Inzolia / Big Papi) | [[combinatorial-screens]] -- GI scoring; synthetic-lethal identification |
| Base-editor variant-function (Hanna 2021 style) | [[base-editing-analysis]] + [[crispresso-editing]] |
| Prime-editor variant installation | [[prime-editing-screens]] -- PRIDICT2 pegRNA design |
| In vivo tumor / immune screens | [[in-vivo-screens]] -- focused library; per-animal meta-analysis |

## Visualization

**Goal:** Show the hit landscape as a volcano of effect size against significance.

**Approach:** Plot log2 fold change against -log10(FDR), highlight genes past the FDR gate, and save the figure to file.

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 8))
gene_summary = pd.read_csv('essentiality_rra.gene_summary.txt', sep='\t')
sig = gene_summary['neg|fdr'] < 0.05
ax.scatter(gene_summary.loc[~sig, 'neg|lfc'],
            -np.log10(gene_summary.loc[~sig, 'neg|fdr'].clip(lower=1e-10)),
            c='lightgray', alpha=0.5, s=10)
ax.scatter(gene_summary.loc[sig, 'neg|lfc'],
            -np.log10(gene_summary.loc[sig, 'neg|fdr'].clip(lower=1e-10)),
            c='red', alpha=0.7, s=18)
ax.axhline(-np.log10(0.05), ls='--', c='black', lw=0.5)
ax.set_xlabel('Log2 Fold Change')
ax.set_ylabel('-Log10(FDR)')
plt.savefig('volcano.png', dpi=150)
```

MAGeCKFlute R package provides one-shot FluteRRA / FluteMLE dashboards with KEGG/Reactome enrichment.

## Output Files

| File | Source step | Description |
|------|-------------|-------------|
| experiment.count.txt | mageck count | Raw count matrix |
| experiment.countsummary.txt | mageck count | Per-sample Gini, mapping, % zero |
| screen_cleanr_corrected_counts.txt | CRISPRcleanR | CN-corrected counts (cancer lines) |
| essentiality_rra.gene_summary.txt | mageck test | Gene-level RRA scores |
| bayes_factor.txt | BAGEL2 | Per-gene Bayes factors |
| drugz_output.txt | drugZ | sumZ, normZ, per-direction FDR |
| jacks_out_gene_JACKS_results.txt | JACKS | Gene effect + sgRNA efficacy |
| tier_consensus.csv | Custom aggregation | Tier-1/2/3 hits across methods |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| False essentials at ERBB2/MYC/FGFR1 | Hit calling before copy-number correction (gene-independent DNA-damage arrest at amplicons, regardless of p53 status) | Run CRISPRcleanR/Chronos BEFORE hit calling; verify abs(rho(LFC,CN)) < 0.1; or use CRISPRi to bypass the DSB |
| FDR broken or PR-AUC uncomputable | NTC (null) and CEGv2 essential (positive control) classes swapped or one absent | Keep both classes; NTCs calibrate the null/FDR, CEGv2/NEGv1 calibrate PR-AUC and BAGEL2/Chronos priors |
| Every hit rescaled / drug effect confounded | Wrong baseline (Day-0 for a drug screen) | Drug screen -> vehicle control; plasmid pool for the cloning-bottleneck baseline |
| "Everything significant at FDR<0.01" | Heavy selection breaks median normalization (>40% guides change) | Switch to `--norm-method control` on NTCs, or BAGEL2 |
| Underpowered / method mismatch | RRA on a time course; single-line Chronos | Pick method by design (fork table); RRA fails multi-condition, Chronos is overkill single-line |
| Distorted NB mean-variance | Batch pre-corrected with ComBat on counts | Add batch as a MAGeCK MLE covariate instead |
| Novel hits from a failed screen | CEGv2 essentials did not deplete (PR-AUC < 0.7) | The screen failed selection; no hit is trustworthy regardless of p-value |

## References

- Li W, Xu H, Xiao T, et al (2014) MAGeCK enables robust identification of essential genes from genome-scale CRISPR/Cas9 knockout screens. *Genome Biology* 15:554. DOI 10.1186/s13059-014-0554-4.
- Aguirre AJ, Meyers RM, Weir BA, et al (2016) Genomic copy number dictates a gene-independent cell response to CRISPR/Cas9 targeting. *Cancer Discovery* 6:914-929. DOI 10.1158/2159-8290.CD-16-0154. (the amplicon artifact.)
- Munoz DM, Cassiani PJ, Li L, et al (2016) CRISPR screens provide a comprehensive assessment of cancer vulnerabilities but generate false-positive hits for highly amplified genomic regions. *Cancer Discovery* 6:900-913. DOI 10.1158/2159-8290.CD-16-0178.
- Hart T, Moffat J (2016) BAGEL: a computational framework for identifying essential genes from pooled library screens. *BMC Bioinformatics* 17:164. DOI 10.1186/s12859-016-1015-8.
- Iorio F, Behan FM, Goncalves E, et al (2018) Unsupervised correction of gene-independent cell responses to CRISPR-Cas9 targeting (CRISPRcleanR). *BMC Genomics* 19:604. DOI 10.1186/s12864-018-4989-y.
- Joung J, Konermann S, Gootenberg JS, et al (2017) Genome-scale CRISPR-Cas9 knockout and transcriptional activation screening. *Nature Protocols* 12:828-863. DOI 10.1038/nprot.2017.016. (library QC: skew, zero-count and coverage conventions.)

## Related Skills

- crispr-screens/library-design - Library composition and design rules
- crispr-screens/screen-qc - Six-stage QC + CEGv2 PR-AUC
- crispr-screens/mageck-analysis - MAGeCK RRA + MLE detail
- crispr-screens/bagel-essentiality - BAGEL2 Bayes factor essentiality
- crispr-screens/drugz-chemogenomic - drugZ for drug-modifier screens
- crispr-screens/jacks-analysis - Joint multi-screen analysis with shared efficacy
- crispr-screens/hit-calling - Cross-method decision tree + reconciliation
- crispr-screens/copy-number-correction - CRISPRcleanR / CERES / Chronos
- crispr-screens/batch-correction - Multi-batch design matrix
- crispr-screens/crispresso-editing - CRISPResso2 editing quantification
- crispr-screens/base-editing-analysis - Variant-function BE screens
- crispr-screens/prime-editing-screens - PRIDICT2 pegRNA design
- crispr-screens/perturb-seq-analysis - Single-cell screen analysis
- crispr-screens/combinatorial-screens - Cas12a multiplex + GI scoring
- crispr-screens/in-vivo-screens - Bottleneck-aware in vivo design
- pathway-analysis/go-enrichment - Functional enrichment of hits
- pathway-analysis/gsea - Pre-ranked GSEA on hit lists
<!-- END FILE: workflows/crispr-screen-pipeline/SKILL.md -->

## 子目录：workflows/cytometry-pipeline

<!-- BEGIN FILE: workflows/cytometry-pipeline/SKILL.md -->
---
name: bio-workflows-cytometry-pipeline
description: End-to-end flow, spectral, and mass cytometry (CyTOF) pipeline from raw FCS files to differentially abundant/expressed cell populations. Orchestrates the read -> compensate/unmix -> transform -> QC -> doublet-removal -> cluster-or-gate -> annotate -> diffcyt DA/DS chain with flowCore/CATALYST/diffcyt, branching on instrument type and on clustering-vs-gating. Use when processing a cytometry experiment end-to-end, deciding the pipeline path for an instrument, or wiring the flow-cytometry component skills into one analysis with valid sample-level statistics.
tool_type: r
primary_tool: CATALYST
workflow: true
depends_on:
  - flow-cytometry/fcs-handling
  - flow-cytometry/compensation-transformation
  - flow-cytometry/cytometry-qc
  - flow-cytometry/doublet-detection
  - flow-cytometry/bead-normalization
  - flow-cytometry/gating-analysis
  - flow-cytometry/clustering-phenotyping
  - flow-cytometry/differential-analysis
qc_checkpoints:
  - after_load: "Read RAW (transformation=FALSE); >~10K cells/sample for stable per-sample frequencies"
  - after_compensation: "Compensate/unmix on LINEAR data before transform; single-stain controls >= as bright as sample; FMO for boundaries"
  - after_qc: "Margins removed BEFORE density QC; doublets removed BEFORE clustering; dead cells gated"
  - after_clustering: "10-30 metaclusters (over-provision then merge); cluster on TYPE markers only, test STATE in DS"
  - after_testing: ">=2-3 biological replicates/group (the sample is the unit); batch modeled in the design; BH FDR across clusters (and clusters x markers for DS)"
---

## Version Compatibility

Reference examples tested with: CATALYST 1.26+, diffcyt 1.22+, FlowSOM 2.10+, flowCore 2.14+, flowWorkspace 4.14+, flowStats 4.14+, edgeR 4.0+, limma 3.58+, ggplot2 3.5+; Python (partial alt) flowkit 1.1+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt rather than retrying. Each stage defers depth to its component skill.

# Flow Cytometry Pipeline

**"Process my cytometry data from FCS to differential populations"** -> read raw -> compensate/unmix -> transform -> QC -> remove doublets -> cluster (or gate) -> annotate -> test DA/DS, with the sample as the unit of inference.
- R: `flowCore` + `CATALYST::prepData/cluster/runDR` + `diffcyt::diffcyt()`

## The Single Most Important Modern Insight -- A Pipeline Is a Chain of Irreversible Decisions, and the Unit of Inference Is the Sample

Each early choice silently gates the validity of the final test: reading raw (not log-linearized), compensating BEFORE transforming, removing margin events before density QC, assigning type-vs-state markers correctly, and removing doublets before clustering. None of these is recoverable downstream - a doublet clustered as a "double-positive," a state marker used for clustering, or an uncompensated channel becomes a false population that the differential test then "confirms." The second critical thread is that the SAMPLE/subject, not the cell, is the experimental unit: diffcyt aggregates cells to per-sample-per-cluster counts (DA) and medians (DS) before testing, so biological replication (>= 2-3 per group) is mandatory and a per-cell test is invalid. Two normalization layers sit at different points in the pipeline - EQ-bead drift correction on raw counts at the very front (CyTOF), and CytoNorm cross-batch harmonization on transformed data before the analytical clustering (its internal FlowSOM clustering is part of the batch model, not the analysis) - and conflating them is a classic error.

## Decision Tree: Which Path

| Situation | Path | Why |
|-----------|------|-----|
| Conventional fluorescence flow | compensate (`$SPILLOVER`/flowStats) -> logicle -> ... | optical spillover; logicle handles negatives |
| Spectral cytometer (Aurora/ID7000) | UNMIX (not compensate) -> arcsinh ~150 | overdetermined system; fluorescence-scale |
| Mass cytometry (CyTOF) | EQ-bead normalize (raw) -> arcsinh cofactor 5 -> `compCytof` if needed | metals barely spill (~1-4%); drift correction first |
| High-dim discovery, no prior gates | cluster (FlowSOM via CATALYST) | scales; finds unexpected populations |
| Well-defined populations / rare events (MRD) | hierarchical gating (openCyto) | interpretable; clustering fails for ultra-rare |
| Multi-batch / multi-day | anchor sample per batch -> CytoNorm (normalize transformed data before analytical clustering) | model batch in the design for inference |

## Pipeline Overview

```
FCS -> compensate/unmix -> transform -> QC (margins, time, dead) -> doublets
     -> [ cluster (FlowSOM) | gate (openCyto) ] -> annotate -> diffcyt DA/DS -> report
EQ-bead drift normalization (CyTOF) runs on raw counts BEFORE everything; CytoNorm runs on transformed data and its normalized output feeds the cluster/gate step.
```

## 1. Panel, Metadata, and Load

**Goal:** Define the type/state panel and sample metadata, then load FCS.

**Approach:** Panel `marker_class` drives everything downstream (type clusters, state is tested); metadata keys samples to condition/subject. See flow-cytometry/fcs-handling.

```r
library(CATALYST); library(diffcyt); library(flowCore); library(ggplot2)

panel <- data.frame(
  fcs_colname = c('FSC-A','SSC-A','CD45','CD3','CD4','CD8','CD19','CD14','Ki67','IFNg'),
  antigen     = c('FSC','SSC','CD45','CD3','CD4','CD8','CD19','CD14','Ki67','IFNg'),
  marker_class = c('none','none','type','type','type','type','type','type','state','state'))
md <- data.frame(file_name = list.files('data', pattern = '\\.fcs$'),
                 sample_id = paste0('S', 1:8),
                 condition = rep(c('Control','Treatment'), each = 4),
                 patient_id = rep(paste0('P', 1:4), 2))
fs <- read.flowSet(file.path('data', md$file_name), transformation = FALSE, truncate_max_range = FALSE)
```

## 2. Compensate / Unmix, then Transform

**Goal:** Remove spillover on linear data, then variance-stabilize.

**Approach:** Conventional flow compensates (matrix before transform); CyTOF skips fluorescence compensation and uses cofactor 5; spectral unmixes then uses ~150. See flow-cytometry/compensation-transformation.

```r
spill <- spillover(fs[[1]]); spill <- spill[[which(!vapply(spill, is.null, logical(1)))[1]]]  # first POPULATED matrix; FACS stores it under SPILL/$SPILLOVER, not always [[1]]
fs_comp <- compensate(fs, spill)                        # conventional flow; CyTOF: omit or use compCytof
COFACTOR <- 150                                          # 5 for CyTOF, ~150 for fluorescence/spectral
sce <- prepData(fs_comp, panel, md, transform = TRUE, cofactor = COFACTOR, FACS = TRUE)
```

## 3. QC (order matters)

**Goal:** Remove margin/boundary events and time anomalies before any density step.

**Approach:** Margins first, then time-based cleaning; on CyTOF, EQ-bead drift correction happens upstream on raw counts. See flow-cytometry/cytometry-qc and flow-cytometry/bead-normalization.

```r
# per-sample sanity + sample-similarity MDS (flag outlier samples)
plotExprs(sce, color_by = 'condition'); pbMDS(sce, color_by = 'condition')
# event-level cleaning runs per-FCS upstream: PeacoQC::RemoveMargins() -> PeacoQC()/flowAI on transformed data
```

## 4. Remove Doublets

**Goal:** Drop aggregates before clustering so they don't form phantom double-positives.

**Approach:** Flow uses the FSC-A vs FSC-H diagonal; CyTOF uses DNA intercalator + Gaussian/Event_length. See flow-cytometry/doublet-detection.

```r
# CyTOF (FACS=TRUE retained Event_length on the arcsinh scale):
e <- assay(sce, 'exprs')
if (all(c('DNA1','Event_length') %in% rownames(sce))) {
  keep <- e['DNA1', ] > quantile(e['DNA1', ], 0.05) &
          e['Event_length', ] <= quantile(e['Event_length', ], 0.99)
  sce <- sce[, keep]
}
```

## 5. Cluster (FlowSOM) or Gate

**Goal:** Define populations by unsupervised clustering on TYPE markers (discovery) or hierarchical gating (defined/rare).

**Approach:** `cluster()` wraps FlowSOM+ConsensusClusterPlus; over-provision the grid, set a seed. See flow-cytometry/clustering-phenotyping (clustering) and flow-cytometry/gating-analysis (gating).

```r
sce <- cluster(sce, features = 'type', xdim = 10, ydim = 10, maxK = 20, seed = 42)
```

## 6. Annotate and Visualize Structure

**Goal:** Label metaclusters from marker medians; embed for display only.

**Approach:** Median heatmap drives annotation; UMAP colors by cluster but is never used to define or quantify populations.

```r
plotExprHeatmap(sce, features = 'type', by = 'cluster_id', k = 'meta20', scale = 'last')
sce <- runDR(sce, dr = 'UMAP', features = 'type', cells = 2000)
plotDR(sce, dr = 'UMAP', color_by = 'meta20')
```

## 7. Differential Abundance and State

**Goal:** Test which populations change in frequency (DA) or state-marker expression (DS) between conditions.

**Approach:** The `diffcyt()` wrapper aggregates to the sample level; results live in `res$res`. See flow-cytometry/differential-analysis.

```r
design   <- createDesignMatrix(ei(sce), cols_design = 'condition')
contrast <- createContrast(c(0, 1))                        # Treatment vs Control
res_DA <- diffcyt(sce, clustering_to_use = 'meta20', analysis_type = 'DA',
                  method_DA = 'diffcyt-DA-edgeR', design = design, contrast = contrast)
res_DS <- diffcyt(sce, clustering_to_use = 'meta20', analysis_type = 'DS',
                  method_DS = 'diffcyt-DS-limma', design = design, contrast = contrast)
da <- as.data.frame(SummarizedExperiment::rowData(res_DA$res))   # cluster_id, logFC, p_val, p_adj
```

## 8. Visualize Results and Export

**Goal:** Summarize significant populations and persist results.

**Approach:** Pass the inner result object (`res$res`) to plotting; export tables and the SCE.

```r
plotDiffHeatmap(sce, res_DA$res, all = TRUE, fdr = 0.05)
plotAbundances(sce, k = 'meta20', by = 'cluster_id', group_by = 'condition')
write.csv(da, 'da_results.csv', row.names = FALSE); saveRDS(sce, 'cytometry_analysis.rds')
```

## Paired / Repeated-Measures Variant

**Goal:** Account for within-subject correlation (pre/post on the same donor).

**Approach:** Use a GLMM with a random effect for subject (NOT voom, which is fixed-effects only).

```r
formula <- createFormula(ei(sce), cols_fixed = 'condition', cols_random = 'patient_id')
res_DA <- diffcyt(sce, clustering_to_use = 'meta20', analysis_type = 'DA',
                  method_DA = 'diffcyt-DA-GLMM', formula = formula, contrast = createContrast(c(0, 1)))
```

## Manual Gating Path (alternative to clustering)

**Goal:** Define populations by a reproducible hierarchy when they are well-defined or rare.

**Approach:** Build a GatingSet on transformed data; recompute after adding gates. See flow-cytometry/gating-analysis.

```r
library(flowWorkspace)
tl <- estimateLogicle(fs_comp[[1]], colnames(spill))
gs <- GatingSet(transform(fs_comp, tl))
# add openCyto template or manual gates (time -> debris -> singlets -> live -> lineage), then:
recompute(gs); gs_pop_get_stats(gs, type = 'count')
```

## Python Alternative (FlowKit) -- partial

**Goal:** Read, compensate, and gate in Python where an R pipeline is not an option.

**Approach:** FlowKit covers IO/compensation/GatingML; there is NO Python equivalent for diffcyt DA/DS, so the differential step stays in R (or bridge via readfcs -> AnnData -> scanpy for clustering only).

```python
import flowkit as fk
sample = fk.Sample('sample.fcs')
sample.apply_compensation(sample.metadata['spillover'])    # FlowKit lowercases + strips $ from keys, so $SPILLOVER -> 'spillover' (not 'spill'); use FlowKit's API, not a hand-rolled inverse
df = sample.as_dataframe(source='comp')
```

## Per-Stage Failure Modes

### Per-cell pseudoreplication
**Trigger:** testing across all cells. **Mechanism:** cells are not independent replicates. **Symptom:** p ~ 1e-40 from few subjects. **Fix:** diffcyt aggregates to sample level; require >= 2-3 replicates/group.

### Clustering on state markers
**Trigger:** activation/phospho markers in `features`. **Mechanism:** state contaminates lineage identity. **Symptom:** activated/resting splits of one type. **Fix:** cluster on `type`; test state in DS.

### Doublets / wrong cofactor / uncompensated input
**Trigger:** skipping doublet removal, cofactor 5 on fluorescence, or clustering raw data. **Mechanism:** phantom double-positives, compressed dim markers, spillover-dominated distances. **Symptom:** non-reproducible "novel" populations. **Fix:** remove doublets first; cofactor 5 (CyTOF) / 150 (fluorescence); compensate+transform before clustering.

### Batch cleaned instead of modeled
**Trigger:** CytoNorm-ing then testing naively, or batch confounded with condition. **Mechanism:** over-correction / non-identifiability. **Symptom:** attenuated or fabricated effects. **Fix:** model batch in the design; if batch == condition, no rescue.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| arcsinh cofactor 5 (CyTOF) / ~150 (fluorescence) | Nowicka 2017 *F1000Res* 6:748 | matches platform noise scale |
| >= 2-3 biological replicates per group | Weber 2019 *Commun Biol* 2:183 | minimum for a valid DA/DS error term |
| > ~10K cells per sample | community | stable per-sample cluster frequencies |
| 10-30 metaclusters typical (maxK=20 default) | Weber & Robinson 2016 *Cytometry A* 89:1084 | over-provision then merge |
| BH FDR across clusters (and clusters x markers for DS) | diffcyt | many simultaneous tests |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `testDA_edgeR(sce, ...)` not found / wrong | fabricated signature | use the `diffcyt()` wrapper; results in `res$res` |
| `compensate()` errors / silent NULL | `spillover(ff)` returns a 3-slot list; the matrix is often under `SPILL`/`$SPILLOVER`, not `[[1]]` | select the first non-null slot, not positional `[[1]]` |
| empty DS results | state markers not flagged | set `marker_class='state'` in the panel |
| paired design ignored | used fixed-effect method | `diffcyt-DA-GLMM` with a random effect |

## References

- Weber 2019 *Commun Biol* 2:183 — diffcyt DA/DS framework.
- Nowicka 2017 *F1000Research* 6:748 — CATALYST CyTOF workflow; type/state, cofactor 5.
- Weber & Robinson 2016 *Cytometry A* 89(12):1084-1096 — FlowSOM clustering benchmark.
- Van Gassen 2020 *Cytometry A* 97(3):268-278 — CytoNorm cross-batch normalization.
- Hurlbert 1984 *Ecol Monogr* 54(2):187-211 — pseudoreplication (sample is the unit).

## Related Skills

- flow-cytometry/fcs-handling - Read FCS and map channels
- flow-cytometry/compensation-transformation - Compensate/unmix and transform
- flow-cytometry/cytometry-qc - Time/margin/dead-cell QC
- flow-cytometry/doublet-detection - Singlet discrimination
- flow-cytometry/bead-normalization - EQ-bead drift and CytoNorm batch correction
- flow-cytometry/gating-analysis - Hierarchical/automated gating path
- flow-cytometry/clustering-phenotyping - FlowSOM clustering and annotation
- flow-cytometry/differential-analysis - diffcyt DA/DS testing
- single-cell/clustering - Related graph-clustering for scRNA-seq
<!-- END FILE: workflows/cytometry-pipeline/SKILL.md -->

## 子目录：workflows/edna-pipeline

<!-- BEGIN FILE: workflows/edna-pipeline/SKILL.md -->
---
name: bio-workflows-edna-pipeline
description: End-to-end eDNA metabarcoding from raw amplicons to community ecology. Covers QC, primer removal (mandatory before DADA2 filterAndTrim), denoising with OBITools3 v3 (obi stats plural; DMS-based) or DADA2 ASVs (Callahan 2017), decontam combined method as screening-not-classifier (Davis 2018), tag-jumping (Schnell 2015) with a platform-dependent baseline (NovaSeq patterned flow cells ~10x MiSeq), Hill-number effective species counts with coverage-based rarefaction (Jost 2006; Chao & Jost 2012; doubling rule), beta-diversity decomposition with MANDATORY PERMANOVA + PERMDISP pair (Anderson & Walsh 2013), constrained ordination, and the read-counts-not-abundance critique (Lamb 2019). Use when processing eDNA samples for biodiversity assessment, deciding ASV vs OTU, configuring OBITools3 v3, interpreting decontam screening, or reporting community comparisons with the dispersion confound check.
tool_type: mixed
primary_tool: obitools3
goal_approach_exempt: true
workflow: true
depends_on:
  - ecological-genomics/edna-metabarcoding
  - ecological-genomics/biodiversity-metrics
  - ecological-genomics/community-ecology
  - read-qc/quality-reports
qc_checkpoints:
  - after_demux: "Reads per sample >1000; negative controls <100 reads"
  - after_denoising: "Chimera rate <20% (>30% indicates library-prep issues); ASV/OTU count reasonable for marker"
  - after_decontam: "decontam combined method at threshold 0.1 (0.05 for low-biomass); biological-plausibility review of each flagged ASV; tag-jumping (Schnell 2015) rate quantified and filtered (~0.001-0.005 MiSeq; ~0.005-0.01 NovaSeq patterned flow cells)"
  - after_taxonomy: "Assignment rate marker-specific: 50-85% unassigned at species level is typical; report gap honestly"
  - after_diversity: "Hill numbers reported as effective species counts (not raw Shannon); coverage-based rarefaction at C=0.95; extrapolation bounded at 2x reference (doubling rule); sample completeness >80%"
  - after_ordination: "PERMANOVA + PERMDISP reported TOGETHER (Anderson & Walsh 2013); if betadisper significant, location conclusion is not supported"
---

## Version Compatibility

Reference examples tested with: DADA2 1.30+, FastQC 0.12+, MultiQC 1.21+, cutadapt 4.4+, phyloseq 1.46+, vegan 2.6+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# eDNA Metabarcoding Pipeline

**"Process my eDNA samples from raw reads to community ecology"** -> Orchestrate primer removal, denoising (OBITools3 or DADA2), contamination filtering, taxonomy assignment, Hill number diversity estimation, and constrained ordination for species-environment analysis.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

An eDNA community table is a position in a choice-chain (marker -> primer bias -> denoise -> decontam -> tag-jump -> taxonomy DB), never a census; the trustworthy result is decided at these seams.

1. **The marker + primer set + reference DB are committed together (COI/12S/ITS/rbcL/18S).** The marker fixes both what taxa amplify and the achievable assignment rate; 50-85% unassigned AT SPECIES LEVEL is TYPICAL (higher ranks assign far better) and must be reported honestly (a high unassigned fraction is a database gap, not a pipeline failure). Report the marker's known primer bias with every result.
2. **Read counts are NOT abundance (Lamb 2019).** eDNA read counts reflect biomass AND primer affinity AND copy number AND degradation — commit to presence/occupancy or effective-species-count framing, never raw-read "abundance". This is the eDNA analogue of the metagenomics read-fraction != cell-fraction seam.
3. **Coverage-based (not size-based) rarefaction; Hill numbers as effective species counts; Chao1 is a LOWER bound.** Commit to iNEXT coverage-standardization at C~0.95 and the doubling-rule extrapolation bound (Chao & Jost 2012); report Chao1 as ">=" and NEVER compute it after aggressive denoising (singletons stripped -> Chao1 degenerates to observed richness).
4. **The platform sets the tag-jump baseline, committed at sequencing.** The tag-jump phenomenon (Schnell 2015) has a platform-dependent rate: MiSeq index-hopping ~0.001-0.005 vs NovaSeq patterned flow cells ~10x higher; quantify and platform-filter the residual rate. And decontam is SCREENING, not a classifier (Davis 2018) — every flagged ASV gets a biological-plausibility review; retain only where statistics AND plausibility agree.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Marker + primer set + reference DB | What amplifies + the assignment rate; 50-85% unassigned at species level is typical; report the primer bias + DB release |
| Read-counts-not-abundance framing | Presence/occupancy or effective-species-count only; raw-read "abundance" is invalid |
| Rarefaction baseline (coverage-based iNEXT, C~0.95) | Hill effective counts; Chao1 as a lower bound, never post-denoising |
| Platform (MiSeq vs NovaSeq) | The tag-jump baseline; NovaSeq ~10x higher index hopping; quantify + filter |

## Pipeline Overview

```
Raw amplicon FASTQ (demultiplexed)
    |
    v
[1. QC] ------------------> FastQC / MultiQC quality assessment
    |
    v
[2. Primer Removal] ------> Cutadapt (remove forward + reverse primers)
    |                            |
    |                            +---> QC: reads per sample >1000
    |
    +--- Path A: OBITools3     +--- Path B: DADA2
    |       |                  |       |
    |       v                  |       v
    |   [3a. obi alignpairedend]   [3b. filterAndTrim]
    |       |                  |       |
    |       v                  |       v
    |   [4a. obi uniq]        |   [4b. learnErrors + dada]
    |       |                  |       |
    |       v                  |       v
    |   [5a. obi ecotag]      |   [5b. assignTaxonomy]
    |                          |
    +-------- Merge -----------+
                |
                v
[6. Contamination Filter] -> decontam / microDecon (negative control removal)
    |
    v
[7. Taxonomy Table] -------> Species x sample matrix
    |
    v
[8. Diversity Analysis] ---> iNEXT Hill numbers (q=0,1,2)
    |
    v
[9. Community Comparison] -> vegan CCA/RDA + indicspecies
    |
    v
Species table + diversity metrics + ordination plots
```

## Step 1: Quality Assessment

```bash
fastqc -t 8 -o fastqc_output/ raw_reads/*.fastq.gz
multiqc fastqc_output/ -o multiqc_report/
```

## Step 2: Primer Removal

```bash
# Adapter sequences are marker-specific; examples below for common eDNA markers
# --discard-untrimmed: remove reads without primers (likely off-target)
# --minimum-length 50: discard very short fragments after trimming

# COI (Leray primers mlCOIintF / jgHCO2198)
cutadapt -g GGWACWGGWTGAACWGTWTAYCCYCC -G TAIACYTCIGGRTGICCRAARAAYCA \
    --discard-untrimmed --minimum-length 50 -j 8 \
    -o trimmed/{sample}_R1.fastq.gz -p trimmed/{sample}_R2.fastq.gz \
    raw_reads/{sample}_R1.fastq.gz raw_reads/{sample}_R2.fastq.gz
```

Common primer sets by marker:

| Marker | Forward Primer | Reverse Primer | Target |
|--------|---------------|----------------|--------|
| COI | mlCOIintF | jgHCO2198 | Metazoan invertebrates |
| 12S MiFish | MiFish-U-F | MiFish-U-R | Fish |
| ITS2 | ITS3 | ITS4 | Fungi |
| rbcL | rbcLa-F | rbcLa-R | Plants |
| 18S V9 | 1389F | 1510R | Eukaryotes |

### QC Checkpoint: Demultiplexing

```bash
# Gate: reads per sample >1000; negative controls <100 reads
for f in trimmed/*_R1.fastq.gz; do
    sample=$(basename "$f" _R1.fastq.gz)
    count=$(zcat "$f" | awk 'END{print NR/4}')
    echo "$sample: $count reads"
done
```

## Step 3: Paired-End Merging and Denoising

### Path A: OBITools3

```bash
# Import, align, and SAMPLE-TAG each demultiplexed sample separately, then concatenate.
# On multiplexed data `obi ngsfilter -t tagfile` assigns the `sample` tag; with pre-demultiplexed
# FASTQ it must be set explicitly (-S takes TAG:PYTHON_EXPRESSION), otherwise `obi uniq -m sample`
# has nothing to merge on and the MERGED_sample tag `obi clean -s` needs is never created.
for s in $(cat samples.txt); do
    obi import --fastq-input trimmed/${s}_R1.fastq.gz reads/${s}_r1
    obi import --fastq-input trimmed/${s}_R2.fastq.gz reads/${s}_r2
    obi alignpairedend -R reads/${s}_r2 reads/${s}_r1 reads/${s}_aligned
    obi annotate -S "sample:'${s}'" reads/${s}_aligned reads/${s}_tagged
done
obi cat $(for s in $(cat samples.txt); do printf -- '-c reads/%s_tagged ' "$s"; done) reads/aligned

# Filter by alignment score
# score >= 50: removes poorly overlapping pairs
obi grep -p 'sequence["score"] >= 50' reads/aligned reads/filtered

# Filter by merged length (marker-dependent range)
# 100-500 bp: typical COI amplicon range
obi grep -p 'len(sequence) >= 100 and len(sequence) <= 500' \
    reads/filtered reads/length_filtered

# Dereplicate
obi uniq -m sample reads/length_filtered reads/dereplicated   # -m sample creates the MERGED_sample tag obi clean -s needs

# Remove singletons
# count >=2: removes sequencing errors; increase to 5-10 for noisy datasets
obi grep -p 'sequence["COUNT"] >= 2' reads/dereplicated reads/denoised   # obi uniq writes the COUNT tag uppercase (case-sensitive)

# Denoise (remove PCR/sequencing errors)
# ratio 0.05: sequences <5% abundance of a 1-mismatch parent are merged
obi clean -s MERGED_sample -r 0.05 -H reads/denoised reads/cleaned
```

### Path B: DADA2 (R)

```r
library(dada2)

path <- 'trimmed/'
fnFs <- sort(list.files(path, pattern = '_R1.fastq.gz', full.names = TRUE))
fnRs <- sort(list.files(path, pattern = '_R2.fastq.gz', full.names = TRUE))
sample_names <- gsub('_R1.fastq.gz', '', basename(fnFs))

# Filter and trim
# truncLen: set based on quality profiles; marker-dependent
# maxEE c(2,2): max expected errors; standard for eDNA
# minLen 50: minimum after trimming
filtFs <- file.path('filtered', paste0(sample_names, '_F_filt.fastq.gz'))
filtRs <- file.path('filtered', paste0(sample_names, '_R_filt.fastq.gz'))
out <- filterAndTrim(fnFs, filtFs, fnRs, filtRs,
                     truncLen = c(200, 180), maxEE = c(2, 2),
                     minLen = 50, truncQ = 2, rm.phix = TRUE,
                     multithread = TRUE)

# Learn error rates
errF <- learnErrors(filtFs, multithread = TRUE)
errR <- learnErrors(filtRs, multithread = TRUE)

# Denoise
dadaFs <- dada(filtFs, err = errF, multithread = TRUE)
dadaRs <- dada(filtRs, err = errR, multithread = TRUE)

# Merge paired reads
# minOverlap 20: standard; increase if amplicon has short overlap region
merged <- mergePairs(dadaFs, filtFs, dadaRs, filtRs, minOverlap = 20)

# Build ASV table
seqtab <- makeSequenceTable(merged)

# Remove chimeras
# method 'consensus': standard; 'pooled' for higher sensitivity
seqtab_nochim <- removeBimeraDenovo(seqtab, method = 'consensus', multithread = TRUE)
chimera_rate <- 1 - sum(seqtab_nochim) / sum(seqtab)
message(sprintf('Chimera rate: %.1f%%', chimera_rate * 100))
```

### QC Checkpoint: Denoising

```r
# Gate 1: Chimera rate <20%
if (chimera_rate > 0.20) message('WARNING: High chimera rate. Check primer removal and PCR conditions.')

# Gate 2: ASV count reasonable for marker
n_asvs <- ncol(seqtab_nochim)
message(sprintf('ASVs after denoising: %d', n_asvs))
# Typical ranges: COI 500-5000, 12S 50-500, ITS 200-3000
```

## Step 4: Contamination Filtering

### R (decontam)

```r
library(decontam)
library(phyloseq)

ps <- phyloseq(otu_table(seqtab_nochim, taxa_are_rows = FALSE),
               sample_data(meta))

# Identify negative controls
sample_data(ps)$is_neg <- sample_data(ps)$sample_type == 'negative_control'

# Combined method (Davis 2018): uses BOTH negative controls AND DNA concentration
# threshold=0.1 default; 0.05 for low-biomass samples
# CRITICAL: output is SCREENING, not classification; biological-plausibility check required
if ('dna_concentration' %in% sample_variables(ps)) {
    contam <- isContaminant(ps, method = 'combined', neg = 'is_neg',
                            conc = 'dna_concentration', threshold = 0.1)
} else {
    # Fall back to prevalence-only if no qPCR/Qubit DNA-concentration data
    contam <- isContaminant(ps, method = 'prevalence', neg = 'is_neg',
                            threshold = 0.1)
}
message(sprintf('Flagged candidate contaminant ASVs: %d', sum(contam$contaminant)))
message('Manual review required: verify biological plausibility before deletion')

ps_clean <- prune_taxa(!contam$contaminant, ps)

# Remove negative control samples
ps_clean <- subset_samples(ps_clean, sample_type != 'negative_control')
```

### Tag-jumping removal (Schnell 2015; NovaSeq caveat)

```r
# Tag-jumping: cross-contamination from index hopping during library prep / sequencing
# Schnell 2015 Mol Ecol Resour 15:1289-1303 documented 0.1-2% per read pair
# NovaSeq patterned flow cells have ~10x higher rates than MiSeq
# Use platform-appropriate threshold:
#   MiSeq: 0.001-0.005 (0.1-0.5% of ASV total)
#   NovaSeq: 0.005-0.01 (0.5-1% of ASV total)
# Quantify residual rate first from per-ASV cross-sample appearance
otu <- as(otu_table(ps_clean), 'matrix')
max_per_asv <- apply(otu, 2, max)
otu_filtered <- otu
# Set threshold by platform; default below is for MiSeq
tag_jump_frac <- 0.001
for (j in 1:ncol(otu)) {
    threshold <- max_per_asv[j] * tag_jump_frac
    otu_filtered[otu[, j] < threshold, j] <- 0
}
otu_table(ps_clean) <- otu_table(otu_filtered, taxa_are_rows = FALSE)
# Modern alternative: metabaR::tagjumpslayer(metabarlist_obj, threshold = 0.03)
```

### QC Checkpoint: Decontamination

```r
# Gate: verify contaminant ASVs were removed from real samples
n_before <- ntaxa(ps)
n_after <- ntaxa(ps_clean)
message(sprintf('ASVs removed as contaminants: %d (%.1f%%)',
                n_before - n_after, (n_before - n_after) / n_before * 100))
if ((n_before - n_after) / n_before > 0.5) {
    message('WARNING: >50% ASVs flagged as contaminants. Review decontam threshold.')
}
```

## Step 5: Taxonomy Assignment

### OBITools3 (ecotag)

```bash
# ecotag assigns taxonomy using LCA algorithm against reference database
# Reference databases: EMBL, BOLD, MIDORI2, UNITE (marker-dependent)
obi ecotag -R reads/refdb --taxonomy reads/taxonomy reads/cleaned reads/assigned

# Filter by assignment quality (species-level for COI)
obi grep -p 'sequence["BEST_IDENTITY"] >= 0.97' reads/assigned reads/filtered_assigned   # ecotag writes BEST_IDENTITY uppercase (case-sensitive)

obi export --tab-output reads/filtered_assigned > taxonomy_results.tsv
```

### DADA2 (assignTaxonomy)

```r
# SILVA for 16S/18S, UNITE for ITS, custom for COI/12S
# Reference databases must be formatted for DADA2
# minBoot 50: minimum bootstrap confidence; 80 for more conservative assignments
taxa <- assignTaxonomy(seqtab_nochim, 'reference_db.fa.gz', multithread = TRUE, minBoot = 50)
taxa <- addSpecies(taxa, 'species_db.fa.gz')
```

### Marker-specific taxonomy databases

| Marker | Database | Typical Assignment Rate |
|--------|----------|------------------------|
| COI | BOLD / Midori2 | >90% to phylum, 60-80% to species |
| 12S | MitoFish / 12S-seqdb | >90% to family for fish |
| ITS | UNITE | >80% to genus for fungi |
| rbcL | GenBank / NCBI nt | >85% to family for plants |
| 18S | SILVA / PR2 | >90% to phylum |

### QC Checkpoint: Taxonomy

```r
# Gate: assignment rate should meet marker expectations
assigned <- !is.na(taxa[, 'Phylum'])
assignment_rate <- sum(assigned) / length(assigned) * 100
message(sprintf('Taxonomy assignment rate (phylum level): %.1f%%', assignment_rate))
if (assignment_rate < 60) message('WARNING: Low assignment rate. Check reference database completeness.')
```

## Step 6: Diversity Analysis

### R (iNEXT)

```r
library(iNEXT)

otu_matrix <- as(otu_table(ps_clean), 'matrix')

# Hill numbers: q=0 (richness), q=1 (Shannon diversity), q=2 (Simpson diversity).
# Default endpoint = per-sample 2x reference size (the Chao 2014 doubling rule); do NOT hardcode a
# single global 2*max, which over-extrapolates small samples under unequal library sizes.
inext_out <- iNEXT(as.list(as.data.frame(t(otu_matrix))),
                   q = c(0, 1, 2), datatype = 'abundance')

# Coverage-based standardization at C=0.95: the fair cross-sample comparison (equalizes completeness,
# not raw depth). estimateD returns Hill numbers at that coverage.
div_c95 <- estimateD(as.list(as.data.frame(t(otu_matrix))),
                     q = c(0, 1, 2), datatype = 'abundance', base = 'coverage', level = 0.95)

# Sample completeness diagnostic: fraction of estimated diversity observed
completeness <- inext_out$DataInfo$SC
message(sprintf('Sample completeness range: %.1f%% - %.1f%%',
                min(completeness) * 100, max(completeness) * 100))
```

### QC Checkpoint: Diversity

```r
# Gate 1: rarefaction approaching asymptote
if (min(completeness) < 0.80) {
    message('WARNING: Some samples have low completeness (<80%). Deeper sequencing recommended.')
}

# Gate 2: richness. Use the COVERAGE-STANDARDIZED q=0, NOT inext_out$AsyEst 'Species richness' (the
# Chao1 asymptotic): denoising stripped singletons (COUNT >= 2), leaving Chao1 no f1, so it degenerates
# to observed richness -- the collapse rule 3 forbids. estimateD returns Order.q / qD.
q0_c95 <- div_c95[div_c95$Order.q == 0, ]
message(sprintf('Coverage-standardized (C=0.95) richness range: %.0f - %.0f effective species',   # qD is fractional; %d errors on doubles
                min(q0_c95$qD), max(q0_c95$qD)))
```

## Step 7: Community Comparison

### R (vegan + indicspecies)

```r
library(vegan)
library(indicspecies)

otu_matrix <- as(otu_table(ps_clean), 'matrix')
env_data <- as(sample_data(ps_clean), 'data.frame')

# Hellinger transformation: standard for community composition data
# Reduces influence of dominant species
otu_hell <- decostand(otu_matrix, method = 'hellinger')

# DCA on untransformed data to determine gradient length
dca <- decorana(otu_matrix)
gradient_length <- diff(range(scores(dca, display = 'sites', choices = 1)))
message(sprintf('DCA gradient length: %.2f SD', gradient_length))

# RDA: linear response (<=3 SD), uses Hellinger-transformed data
# CCA: unimodal response (>3 SD), uses raw abundances (chi-squared distance)
if (gradient_length <= 3) {
    ord <- rda(otu_hell ~ temperature + depth + season, data = env_data)
    method_name <- 'RDA'
} else {
    ord <- cca(otu_matrix ~ temperature + depth + season, data = env_data)
    method_name <- 'CCA'
}

# Permutation test for significance
# permutations 999: standard; increase to 9999 for publication
anova_result <- anova.cca(ord, permutations = 999)
message(sprintf('%s significance: p = %.4f', method_name, anova_result$`Pr(>F)`[1]))

# MANDATORY companion: PERMANOVA + PERMDISP (Anderson & Walsh 2013 Ecol Monogr 83:557-574)
# adonis2 tests centroid difference; betadisper tests dispersion homogeneity
# If betadisper is also significant, PERMANOVA significance is dispersion-confounded
bray_dist <- vegdist(otu_matrix, method = 'bray')
permanova <- adonis2(bray_dist ~ site, data = env_data,
                     by = 'margin', permutations = 999)
disp <- betadisper(bray_dist, env_data$site)
disp_test <- permutest(disp, permutations = 999)
message(sprintf('PERMANOVA p = %.4f; PERMDISP p = %.4f',
                permanova[['Pr(>F)']][1], disp_test$tab[['Pr(>F)']][1]))
if (permanova[['Pr(>F)']][1] < 0.05 && disp_test$tab[['Pr(>F)']][1] < 0.05) {
    message('WARNING: Both PERMANOVA and PERMDISP significant; location-vs-dispersion confounded')
}

# Indicator species analysis with group-size equalization (NOT basic IndVal)
# func='IndVal.g' corrects for unbalanced group sizes (De Caceres & Legendre 2009)
indval <- multipatt(otu_matrix, env_data$site, func = 'IndVal.g',
                    control = how(nperm = 999))
summary(indval, alpha = 0.05)
```

## Parameter Recommendations

| Step | Parameter | Recommendation |
|------|-----------|----------------|
| Cutadapt | --discard-untrimmed | Always use; removes off-target reads. MANDATORY before DADA2 filterAndTrim |
| Cutadapt | --minimum-length | 50 (general); adjust per expected amplicon size |
| DADA2 | truncLen | Set from quality profiles; marker-dependent (typical 2x250 COI: c(220,180)) |
| DADA2 | maxEE | c(2,2) standard; c(5,5) for degraded eDNA |
| DADA2 | minOverlap | 20 (standard); increase for short overlaps |
| DADA2 | chimera method | 'consensus' standard (conservative); 'pooled' more aggressive |
| OBITools3 v3 | command syntax | `obi stats` (plural; was `obistat` in v1); `.tar.gz` taxonomy |
| OBITools3 | --min-count | 2 (removes singletons); 5-10 for noisy datasets |
| decontam | method | 'combined' if concentration AND controls; 'prevalence' fallback |
| decontam | threshold | 0.1 default; 0.05 for low-biomass samples |
| Tag-jumping MiSeq | threshold | 0.001-0.005 fraction of ASV total |
| Tag-jumping NovaSeq | threshold | 0.005-0.01 (~10x MiSeq; patterned flow cells) |
| Taxonomy | minBoot | 50 (sensitive); 80 (conservative) |
| ecotag | --minimum-identity (-m) | 0.97 (COI species); 0.95 (genus); marker-dependent |
| iNEXT | endpoint | per-sample 2x reference size (default doubling rule); do not set a global 2*max |
| vegan | permutations | 999 (standard); 9999 (publication) |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Over-called rare-species presence (worst on NovaSeq) | Tag-jump rate never quantified ("we used dual indexing" and stop) | Report the residual rate (reads in should-be-zero cells / total) and platform-filter |
| Real low-biomass taxa deleted | decontam output treated as ground truth | Biological-plausibility review of every flag; retain only where statistics AND plausibility agree |
| Chao1 collapses to observed richness | Chao1 computed after aggressive denoising (singletons stripped) | Use incidence-based Chao2, or estimators only on data with a real singleton/doubleton distribution |
| A "community shift" that is really dispersion | PERMANOVA reported without PERMDISP | Always pair adonis2 with betadisper/permutest; if dispersion is significant, the location conclusion is not supported |
| Read counts interpreted as abundance | eDNA reads treated as biomass | Presence/occupancy or effective-species-count framing only (Lamb 2019) |
| Few reads after primer removal | Wrong primer sequences or orientation | Verify primer sequences; try --revcomp |
| High chimera rate (>20%) | Excessive PCR cycles or low-quality input | Reduce PCR cycles; improve DNA extraction |
| Many unassigned ASVs | Incomplete reference database | Use marker-specific database; lower minBoot |
| Contamination in negatives | Tag-jumping or lab contamination | Apply tag-jump filter; review extraction protocol |
| Low sample completeness | Insufficient sequencing depth | Increase sequencing; pool fewer samples |
| Ordination axes not significant | Weak environmental gradients | Add more environmental variables; check sample size |
| Unexpected taxa (e.g., human) | Sample contamination | Filter known contaminants; review field protocols |
| Very few ASVs | Over-aggressive filtering | Relax truncLen, maxEE, or min-count thresholds |

## Related Skills

- ecological-genomics/edna-metabarcoding - Detailed eDNA processing
- ecological-genomics/biodiversity-metrics - Diversity analysis details
- ecological-genomics/community-ecology - Ordination and indicator species
- read-qc/quality-reports - Raw read quality assessment
- reporting/automated-qc-reports - Aggregate FastQC across samples with MultiQC (a triage snapshot, not a pass/fail gate)
- microbiome/amplicon-processing - 16S clinical alternative

## References

- Lamb PD, Hunter E, Pinnegar JK, et al (2019) How quantitative is metabarcoding? A meta-analytical approach. *Molecular Ecology* 28:420-430. DOI 10.1111/mec.14920. (read counts are not abundance.)
- Schnell IB, Bohmann K, Gilbert MTP (2015) Tag jumps illuminated - reducing sequence-to-sample misidentifications in metabarcoding studies. *Molecular Ecology Resources* 15:1289-1303. DOI 10.1111/1755-0998.12402. (tag jumping.)
- Davis NM, Proctor DM, Holmes SP, Relman DA, Callahan BJ (2018) Simple statistical identification and removal of contaminant sequences in marker-gene and metagenomics data. *Microbiome* 6:226. DOI 10.1186/s40168-018-0605-2. (decontam.)
- Anderson MJ, Walsh DCI (2013) PERMANOVA, ANOSIM, and the Mantel test in the face of heterogeneous dispersions. *Ecological Monographs* 83:557-574. DOI 10.1890/12-2010.1. (PERMANOVA + PERMDISP.)
<!-- END FILE: workflows/edna-pipeline/SKILL.md -->

## 子目录：workflows/expression-to-pathways

<!-- BEGIN FILE: workflows/expression-to-pathways/SKILL.md -->
---
name: bio-workflows-expression-to-pathways
description: 'Orchestrates the full path from differential expression results to redundancy-collapsed functional enrichment: choose ORA vs GSEA, convert gene IDs per method, run enrichGO/enrichKEGG/enrichPathway/enrichWP or gseGO/gseKEGG (clusterProfiler, ReactomePA, rWikiPathways), and visualize. Use when a DESeq2/edgeR/limma result must become enriched GO terms, KEGG/Reactome/WikiPathways pathways, or a GSEA leading edge; when the input is a full ranking for all genes (GSEA, named decreasing vector) or only a pre-selected list (ORA plus a defensible background universe); or when assembling DE-to-pathway end to end. The DE list and ranking statistic come from differential-expression/de-results; per-method nuance lives in the pathway-analysis skills.'
tool_type: r
primary_tool: clusterProfiler
workflow: true
depends_on:
  - pathway-analysis/go-enrichment
  - pathway-analysis/gsea
  - pathway-analysis/kegg-pathways
  - pathway-analysis/reactome-pathways
  - pathway-analysis/wikipathways
  - pathway-analysis/enrichment-visualization
qc_checkpoints:
  - input_validation: "Gene IDs match the method (OrgDb keyType / kegg-id / ENTREZ); >85% convert; background = testable genes"
  - generation_choice: "ORA-vs-GSEA fork decided BEFORE running; a ranking for all genes -> GSEA, a pre-selected list -> ORA"
  - reproducibility: "Tool + database version/date, ranking metric, p-adjust method, and universe recorded; set.seed for GSEA"
---

## Version Compatibility

Reference examples tested with: clusterProfiler 4.10+, org.Hs.eg.db 3.18+, ReactomePA 1.46+, enrichplot 1.22+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Expression to Pathways Workflow

**"Find enriched pathways from my differential expression results"** -> Decide the generation (ORA vs GSEA) FIRST, then convert IDs to the form each method needs, run enrichment against the chosen database, and collapse redundancy before interpreting - because the enrichment result is a claim conditioned on the method, the background universe, and the database version, not a discovery the algorithm hands back.
- R: `enrichGO(...)` / `gseGO(...)` / `enrichKEGG(...)` / `enrichPathway(...)` (clusterProfiler, ReactomePA)

Scope: the ORCHESTRATION of a DE-to-enrichment pipeline - the generation fork, per-method ID conversion, the universe decision, the live-vs-local database caveat, and the handoff to redundancy-collapsed visualization. This workflow does NOT re-teach each method. The null/universe/reproducibility theory and the master method-selection tree -> the pathway-analysis README and the per-method skills (go-enrichment, gsea). ORA mechanics -> go-enrichment; GSEA mechanics -> gsea; per-database IDs and live-DB behavior -> kegg-pathways, reactome-pathways, wikipathways; the DE list and ranking statistic -> differential-expression/de-results; plotting -> enrichment-visualization.

## The Single Most Important Modern Insight -- The First Decision Is the Generation, and It Is Set by the Input, Not by Preference

Pathway analysis has three generations (Khatri 2012 *PLoS Comput Biol* 8:e1002375): over-representation analysis (ORA), functional class scoring / GSEA (FCS), and pathway topology. A workflow that "runs enrichment" without first deciding which generation applies has already made the choice silently - usually ORA, the worst-calibrated corner of the space. The fork is mechanical:

1. **Is there a meaningful per-gene ranking for (nearly) ALL measured genes?** A signed test statistic, the DESeq2 Wald `stat`, or `-sign(log2FC)*log10(p)` for every tested gene -> **GSEA** (a NAMED vector sorted in DECREASING order; the ranking metric IS the experiment). No arbitrary cutoff; detects coordinated weak shifts that ORA misses.
2. **Only a pre-selected LIST (DE hits past a cutoff, a co-expression module, GWAS loci, screen hits)?** -> **ORA**, and the deliverable hinges on a defensible **background universe** - the genes that were testable, not the whole genome. ORA's p-value is whatever the denominator says it is.

The dangerous default is running ORA on data that has a full ranking (binarizing away the signal) or running ORA against the genome (measuring expression, not enrichment). Decide the fork out loud, record it, and record the why (see the pathway-analysis README) - this workflow owns the routing, not the derivation.

## Pipeline Overview

```
DE results (differential-expression/de-results)
    |
    v
[0. Decide the generation: ranking for all genes? -> GSEA | pre-selected list? -> ORA]
    |
    +--> ORA branch: define the TESTABLE-gene universe, convert IDs per method
    |        +--> enrichGO     (OrgDb keyType)        -> go-enrichment
    |        +--> enrichKEGG   ('kegg' / 'ncbi-geneid', LIVE DB)  -> kegg-pathways
    |        +--> enrichPathway (ENTREZ, local DB)    -> reactome-pathways
    |        +--> enrichWP      (ENTREZ, LIVE GMT)    -> wikipathways
    |
    +--> GSEA branch: build a NAMED decreasing vector of ALL genes, set.seed
    |        +--> gseGO / gseKEGG / GSEA(+msigdbr)    -> gsea
    |
    v
[Redundancy collapse + visualization: simplify, pairwise_termsim, dotplot/emapplot/gseaplot2]   (enrichment-visualization)
    |
    v
A claim conditioned on universe + method + database version (record provenance)
```

## Stage Map

| Stage | Goal | Owns the nuance |
|-------|------|-----------------|
| 0. Decide generation | ORA vs GSEA from the available input | pathway-analysis README (method selection) |
| 1. Prepare input | Build the gene list AND/OR the named ranked vector; define the universe | differential-expression/de-results (the stat); pathway-analysis/go-enrichment (the universe rule) |
| 2. Convert IDs | Map to the form each method needs (OrgDb keyType / kegg-id / ENTREZ) | go-enrichment, kegg-pathways, reactome-pathways |
| 3a. ORA | Hypergeometric test of the list vs background | go-enrichment, kegg-pathways, reactome-pathways, wikipathways |
| 3b. GSEA | Running-sum over the full ranking | gsea |
| 4. Collapse + visualize | Reduce redundancy, then plot | enrichment-visualization |

## Decision Tree by Scenario

| Scenario | Route | Why |
|----------|-------|-----|
| All genes carry a DE statistic, a cutoff would be arbitrary | GSEA (gseGO/gseKEGG) -> gsea | uses the full ranking; no cutoff; named decreasing vector |
| Pre-selected list (module, GWAS loci, screen hits), no ranking | ORA (enrichGO/enrichKEGG) -> go-enrichment | no ranking available; define the universe |
| Broad function annotation | enrichGO / gseGO -> go-enrichment, gsea | GO is the broadest LOCAL resource (reproducible) |
| Metabolic / signaling pathways | enrichKEGG / gseKEGG -> kegg-pathways | KEGG maps query a LIVE DB (pin the date) |
| Reaction-level, peer-reviewed, reproducible offline | enrichPathway -> reactome-pathways | local reactome.db, version-pinned |
| Disease/drug sets the others miss, broad species | enrichWP -> wikipathways | community-curated; LIVE versioned GMT |
| Bacterial / prokaryotic data | enrichKEGG with locus tags + KEGG organism code -> kegg-pathways | KEGG covers prokaryotes; OrgDb usually does not |
| RNA-seq with strong gene-length bias | GOseq -> go-enrichment | length-aware ORA null |
| Multiple conditions/clusters side by side | compareCluster -> any DB | one model, faceted dotplot; never compare p across separate runs |
| The DE list / ranking statistic itself | -> differential-expression/de-results | that is upstream, not enrichment |
| Why this null, which universe, version reporting | -> go-enrichment (universe), gsea (null) | per-method theory owned by each skill |

## Stage 1: Prepare the Input (list, ranked vector, and the universe)

**Goal:** Turn a DE table into the two possible inputs - a gene LIST for ORA and a NAMED decreasing vector for GSEA - and define the background universe as the testable genes.

**Approach:** Read the DE result, derive the significant list, build the ranked vector from a signed statistic (not a bare log2FC), and set the universe to exactly the genes that entered the DE test. The DE mechanics (the `$padj` vs `$adj.P.Val` column, shrinkage) live at differential-expression/de-results - this is only input shaping.

```r
library(clusterProfiler)
library(org.Hs.eg.db)

res <- read.csv('deseq2_results.csv', row.names = 1)

# ORA input: a pre-selected list (DESeq2 padj column; limma/edgeR name it differently)
sig_genes <- rownames(subset(res, padj < 0.05 & abs(log2FoldChange) > 1))

# Background universe = genes that were TESTABLE (entered the DE test), NOT the genome.
# Using the genome measures expression bias, not enrichment (the universe rule; see pathway-analysis/go-enrichment).
universe_genes <- rownames(res[!is.na(res$pvalue), ])

# GSEA input: a NAMED vector of ALL genes, sorted DECREASING by a signed metric.
# Prefer the Wald stat (magnitude + precision); a bare log2FC over-weights noisy low-count genes.
# TRAP: a table from lfcShrink(type='apeglm'/'ashr') has NO `stat` column -- shrinkage drops it.
# Rank from the UNSHRUNK results(dds)$stat; use edgeR `sign(logFC)*-log10(PValue)` or limma `t`.
ranked <- res$stat
names(ranked) <- rownames(res)
ranked <- sort(ranked[!is.na(ranked)], decreasing = TRUE)
```

## Stage 2: Convert Gene IDs to What Each Method Needs

**Goal:** Map identifiers to the exact ID type each enrichment function expects, because a mismatch returns zero hits silently.

**Approach:** Use `bitr` (OrgDb) for SYMBOL/ENSEMBL -> ENTREZ, keep both list and ranked vector in the same ID space, deduplicate, and track the conversion rate. Per-method ID rules are owned by each DB skill; the table below is the routing summary.

```r
# enrichGO accepts ENSEMBL/SYMBOL/ENTREZ via keyType=; ENTREZ is the safe lingua franca downstream
sig_entrez <- bitr(sig_genes, fromType = 'SYMBOL', toType = 'ENTREZID', OrgDb = org.Hs.eg.db)
bg_entrez <- bitr(universe_genes, fromType = 'SYMBOL', toType = 'ENTREZID', OrgDb = org.Hs.eg.db)

# Carry the ranking through conversion: name the kept stat by its ENTREZ id
ranked_map <- bitr(names(ranked), fromType = 'SYMBOL', toType = 'ENTREZID', OrgDb = org.Hs.eg.db)
ranked_list <- ranked[ranked_map$SYMBOL]
names(ranked_list) <- ranked_map$ENTREZID
ranked_list <- ranked_list[!duplicated(names(ranked_list))]   # dedup or GSEA biases the score
ranked_list <- sort(ranked_list, decreasing = TRUE)           # re-sort: bitr remap can reorder rows

conv_rate <- nrow(sig_entrez) / length(sig_genes)   # report it; <0.85 -> wrong ID type/organism
```

| Method | keyType / ID required | Convert with |
|--------|-----------------------|--------------|
| enrichGO / gseGO | OrgDb keyType ('ENSEMBL', 'SYMBOL', 'ENTREZID') | bitr |
| enrichKEGG / gseKEGG | 'kegg' or 'ncbi-geneid' (NOT ENSEMBL/OrgDb) | bitr to ENTREZID, pass keyType='ncbi-geneid' (bitr_kegg only converts among KEGG ID flavors) |
| enrichPathway / gsePathway (ReactomePA) | ENTREZ | bitr |
| enrichWP / gseWP (WikiPathways) | ENTREZ + organism string | bitr |

## Stage 3a: ORA Branch (pre-selected list + universe)

**Goal:** Test each gene set for over-representation of the list against the testable-gene background.

**Approach:** Always pass `universe=`; run GO ontologies separately; KEGG/Reactome/WikiPathways each need their own ID form. KEGG and WikiPathways query a LIVE database (internet-dependent, not reproducible across releases - pin the run date); GO and Reactome read local annotation (reproducible given the Bioconductor release).

```r
# GO ORA - universe is the decision; simplify() collapses DAG redundancy (BP/MF/CC separately, not 'ALL')
go_bp <- enrichGO(sig_entrez$ENTREZID, universe = bg_entrez$ENTREZID, OrgDb = org.Hs.eg.db,
                  ont = 'BP', pAdjustMethod = 'BH', pvalueCutoff = 0.05, readable = TRUE)
go_bp <- simplify(go_bp, cutoff = 0.7, by = 'p.adjust')

# KEGG ORA - LIVE KEGG REST API; needs internet; record the access date for reproducibility
kegg <- enrichKEGG(sig_entrez$ENTREZID, universe = bg_entrez$ENTREZID, organism = 'hsa', keyType = 'ncbi-geneid', pvalueCutoff = 0.05)   # Entrez input; keyType='kegg' = Entrez for eukaryotes / locus tags for prokaryotes, 'ncbi-geneid' is explicit
kegg <- setReadable(kegg, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID')

# Reactome ORA - ENTREZ required; LOCAL reactome.db so reproducible given the release
library(ReactomePA)
reactome <- enrichPathway(sig_entrez$ENTREZID, universe = bg_entrez$ENTREZID, organism = 'human', pvalueCutoff = 0.05, readable = TRUE)
```

## Stage 3b: GSEA Branch (named decreasing vector of all genes)

**Goal:** Find gene sets whose genes shift coordinately across the full ranking, without a significance cutoff.

**Approach:** Run on the named decreasing `ranked_list`, fix the permutation seed so p-values are reproducible, then read the leading edge as the interpretable core. clusterProfiler GSEA is preranked / gene-permutation (the inter-gene-correlation-UNcorrected null) - a discovery screen; see pathway-analysis/gsea for the calibration caveat (CAMERA/ROAST).

```r
set.seed(123)   # permutation reproducibility; without it p-values drift across runs

gsea_go <- gseGO(ranked_list, OrgDb = org.Hs.eg.db, ont = 'BP',
                 minGSSize = 10, maxGSSize = 500, pvalueCutoff = 0.05, verbose = FALSE)

gsea_kegg <- gseKEGG(ranked_list, organism = 'hsa',
                     minGSSize = 10, maxGSSize = 500, pvalueCutoff = 0.05, verbose = FALSE)
```

## Stage 4: Collapse Redundancy, Then Visualize

**Goal:** Reduce overlapping terms to distinct findings before drawing conclusions, then plot deliberately.

**Approach:** A list of 40 significant GO terms is often a few biological stories told many times (shared genes via the GO true-path rule). Collapse with `simplify`/`pairwise_termsim`, then plot - `emapplot`/`treeplot` require `pairwise_termsim()` first (cnetplot does NOT; it draws the gene-concept network from the `geneID` column directly), and `gseaplot2` is for a gseaResult not an enrichResult. Encoding choice and required pre-steps are owned by pathway-analysis/enrichment-visualization.

```r
library(enrichplot)

go_bp <- pairwise_termsim(go_bp)              # required before emapplot/treeplot
dotplot(go_bp, showCategory = 20)             # GeneRatio vs Count: pick the encoding deliberately
emapplot(go_bp, showCategory = 30)            # redundancy-collapsed term-similarity map
gseaplot2(gsea_go, geneSetID = 1:3)           # gseaResult only, not enrichResult
```

## Multi-Condition Comparison

**Goal:** Compare enrichment across conditions in one model instead of comparing p-values from separate runs.

**Approach:** `compareCluster` fits all gene lists together and facets the dotplot; never compare raw -log10(p) across separate enrichments (it scales with set size and sample size). For GSEA, compare NES, not p.

```r
gene_clusters <- list(A = sig_A, B = sig_B, C = sig_C)
cc <- compareCluster(gene_clusters, fun = 'enrichKEGG', organism = 'hsa',
                     universe = bg_entrez$ENTREZID)   # compareCluster forwards ... to fun; omitting universe silently reverts to the whole-genome background
dotplot(cc, showCategory = 10)
```

## Per-Method Failure Modes

### Whole-genome background
**Trigger:** `universe=` left at default while only ~12k genes were expressed. **Mechanism:** the hypergeometric p-value is fully determined by the denominator; the genome inflates any set whose members are expressed in the tissue. **Symptom:** many tissue-specific terms enrich with tiny p. **Fix:** set `universe` to the genes that entered the DE test (the testable set).

### ORA on a ranked dataset
**Trigger:** filtering all-gene DE results to a list and running ORA. **Mechanism:** binarizing at an arbitrary cutoff discards magnitude and the coordinated-weak signal. **Symptom:** GSEA finds sets ORA missed. **Fix:** if a ranking exists for all genes, run GSEA; reserve ORA for genuinely unranked lists.

### Wrong ID type for the database
**Trigger:** ENSEMBL/SYMBOL passed to enrichKEGG/enrichPathway/enrichWP. **Mechanism:** those expect kegg-id/ENTREZ; unmatched IDs are dropped. **Symptom:** zero terms, no error. **Fix:** `bitr`/`bitr_kegg` to the required ID; check `conv_rate`.

### GSEA without set.seed or with an unsorted vector
**Trigger:** no seed, or a list that is not named and decreasing. **Mechanism:** permutation p-values drift run to run; an unsorted/unnamed vector errors or mis-ranks. **Symptom:** different leading edges each run, or a names error. **Fix:** build the named decreasing vector and `set.seed`.

### Ranking a GSEA vector off a shrunken-LFC object
**Trigger:** building the ranked vector from a `lfcShrink(type='apeglm'/'ashr')` table, or ranking by bare `log2FoldChange`. **Mechanism:** apeglm/ashr DROP the `stat` column, so the vector silently falls back to shrunken LFC; low-count genes with unstable large FC then hijack the leading edge. **Symptom:** the leading edge is dominated by low-baseMean genes, or `res$stat` is NULL. **Fix:** rank from the unshrunken `results(dds)$stat` (DESeq2), limma `topTable$t`, or edgeR `sign(logFC)*-log10(PValue)`; reserve shrunken LFC for visualization.

### Live-DB result reported as reproducible
**Trigger:** KEGG/WikiPathways result with no recorded date. **Mechanism:** those query the current data release; the same code returns different pathways later. **Symptom:** a collaborator cannot reproduce the figure. **Fix:** record the access date and data version; prefer local GO/Reactome when reproducibility is paramount.

### Redundancy read as replication
**Trigger:** interpreting 40 overlapping GO terms as 40 findings. **Mechanism:** the true-path rule and pathway overlap mean shared genes drive many sets. **Symptom:** the same 3-5 genes explain the top 20 terms. **Fix:** `simplify`/`pairwise_termsim`, inspect the leading-edge/`geneID` core, report clusters of terms.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `pvalueCutoff = 0.05` | clusterProfiler default | filters on p.adjust by default in enrichResult; standard FDR gate |
| `qvalueCutoff = 0.2` | clusterProfiler default | secondary q-value gate |
| `pAdjustMethod = 'BH'` | Benjamini-Hochberg | valid FDR control under positive dependence (overlapping sets); Bonferroni over-corrects |
| `minGSSize = 10` | enrichGO/gseGO default | drop tiny sets that overfit |
| `maxGSSize = 500` | enrichGO/gseGO default | drop overly broad sets that always "enrich" |
| `simplify(cutoff = 0.7)` | GOSemSim semantic similarity | GO DAG redundancy cutoff; lower keeps more terms |
| conversion rate > 0.85 | practical QC | <85% ID conversion flags a wrong ID type/organism |
| `set.seed(123)` | reproducibility | any fixed seed; the point is to fix the permutation draw |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| enrichKEGG returns 0 terms | ENSEMBL passed (needs kegg-id/ENTREZ), wrong organism code, or KEGG API down | convert with bitr_kegg; check organism; retry (live DB) |
| `--> No gene can be mapped` | wrong keyType/OrgDb for the input IDs | match keyType to the actual ID type |
| gseGO error about names | vector not named or not sorted decreasing | build a named vector sorted `decreasing = TRUE` |
| emapplot/treeplot empty or errors | `pairwise_termsim()` not run first (cnetplot does not need it) | run `pairwise_termsim()` before emapplot/treeplot |
| simplify fails on ont='ALL' | simplify needs one ontology | run BP/MF/CC separately, then simplify each |
| different results each run | no set.seed, or the live KEGG/WP DB changed | set.seed; pin and record the DB version/date |
| all terms have NA Description | `readable`/`setReadable` not applied | set `readable = TRUE` or call `setReadable` |

## References

- Khatri P, Sirota M, Butte AJ. 2012. Ten years of pathway analysis: current approaches and outstanding challenges. *PLoS Comput Biol* 8:e1002375.
- Subramanian A, Tamayo P, Mootha VK, et al. 2005. Gene set enrichment analysis: a knowledge-based approach for interpreting genome-wide expression profiles. *PNAS* 102:15545-15550.
- Goeman JJ, Buhlmann P. 2007. Analyzing gene expression data in terms of gene sets: methodological issues. *Bioinformatics* 23:980-987.
- Wu T, Hu E, Xu S, et al. 2021. clusterProfiler 4.0: a universal enrichment tool for interpreting omics data. *The Innovation* 2:100141.
- Yu G, He QY. 2016. ReactomePA: an R/Bioconductor package for reactome pathway analysis and visualization. *Mol BioSyst* 12:477-479.
- Kanehisa M, Goto S. 2000. KEGG: Kyoto Encyclopedia of Genes and Genomes. *Nucleic Acids Res* 28:27-30.
- Young MD, Wakefield MJ, Smyth GK, Oshlack A. 2010. Gene ontology analysis for RNA-seq: accounting for selection bias. *Genome Biol* 11:R14.
- Wijesooriya K, Jadaan SA, Perera KL, Kaur T, Ziemann M. 2022. Urgent need for consistent standards in functional enrichment analysis. *PLoS Comput Biol* 18:e1009935.

## Related Skills

- pathway-analysis/go-enrichment - GO over-representation, background universe, redundancy reduction, length bias
- pathway-analysis/gsea - Ranked-list GSEA, named decreasing vector, ranking metric, leading edge, NES
- pathway-analysis/kegg-pathways - KEGG pathway/module enrichment, live DB, prokaryotes, multi-condition
- pathway-analysis/reactome-pathways - Reactome curated-pathway ORA and GSEA, ENTREZ IDs, reproducible local DB
- pathway-analysis/wikipathways - WikiPathways community-pathway enrichment, versioned GMT, broad species
- pathway-analysis/enrichment-visualization - Dot/bar/cnet/emap/GSEA plots and required pre-steps
- differential-expression/de-results - Source of the gene list and the ranking statistic
<!-- END FILE: workflows/expression-to-pathways/SKILL.md -->

## 子目录：workflows/fastq-to-variants

<!-- BEGIN FILE: workflows/fastq-to-variants/SKILL.md -->
---
name: bio-workflows-fastq-to-variants
description: Orchestrates the end-to-end germline short-variant pipeline from FASTQ to a filtered, normalized, benchmarked VCF, chaining QC/trim, BWA-MEM2 alignment, duplicate marking, optional BQSR, calling (bcftools/GATK HaplotypeCaller/DeepVariant/DRAGEN), normalization, site+genotype filtering, annotation, and hap.py/vcfeval benchmarking. Use when deciding the pipeline-wide reference-genome commitment (GRCh38 analysis set vs T2T, ALT/decoy handling), sequencing the steps in the defensible order (normalize BEFORE annotate, filter site- then genotype-level), choosing the calling engine and single-sample vs cohort joint-calling, picking a filtering strategy by cohort size, or benchmarking stratified within GIAB confident regions. Hands off mechanism to the variant-calling and read-alignment component skills; not a re-teach of any single step.
tool_type: cli
primary_tool: bcftools
workflow: true
depends_on:
  - read-qc/fastp-workflow
  - read-alignment/bwa-alignment
  - alignment-files/alignment-sorting
  - alignment-files/duplicate-handling
  - variant-calling/variant-calling
  - variant-calling/joint-calling
  - variant-calling/variant-normalization
  - variant-calling/filtering-best-practices
  - variant-calling/variant-annotation
  - variant-calling/vcf-statistics
qc_checkpoints:
  - after_qc: "Q30 >85%, adapter content <1%"
  - after_alignment: "Mapping rate >95%, properly paired >90%"
  - after_dedup: "Duplication rate <30% for WGS, <50% for exome"
  - after_calling: "Ti/Tv ratio ~2.0-2.1 for WGS, ~3.0-3.3 for exome; dbSNP overlap >95% only after annotating the ID column"
---

## Version Compatibility

Reference examples tested with: BWA-MEM2 2.2.1+, GATK 4.5+, bcftools 1.19+, samtools 1.19+, fastp 0.23+, DeepVariant 1.6+, hap.py 0.3.15+, Ensembl VEP 111+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: GenotypeGVCFs defaults (`--max-alternate-alleles`, `--heterozygosity`, `--stand-call-conf`), the GATK hard-filter thresholds, and DRAGEN speed/accuracy figures drift by version/vendor; confirm in-tool and against current GIAB benchmarks before quoting.

# FASTQ to Variants Workflow

**"Call variants from my whole-genome or exome FASTQ files"** -> Chain QC/trim, alignment, duplicate marking, an engine-appropriate caller, normalization, filtering, annotation, and benchmarking into one filtered germline VCF.
- CLI: fastp -> bwa-mem2 -> samtools markdup -> (bcftools | gatk HaplotypeCaller | DeepVariant) -> bcftools norm -> filter -> VEP -> hap.py

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

A germline pipeline is a chain of commitments, and the two that decide whether the callset is trustworthy are made at the seams between steps, not inside them.

1. **The reference is a pipeline-wide commitment made once and inherited by everything downstream.** The build and analysis set chosen at alignment (step 2) fix the coordinates of every later comparison: the dbSNP/ClinVar/gnomAD records annotation matches against, the truth BED benchmarking scores within, and the cohort other samples are joint-called with must all be the SAME build. Changing it later means redoing alignment, calling, normalization, and annotation. Decide before aligning a single read.
2. **The step order is not arbitrary; two orderings sink reviews.** (a) **Normalize BEFORE annotate.** An indel that is not left-aligned to the database's canonical position is one base off, so the annotator silently misses the ClinVar/gnomAD record and reports a pathogenic variant as novel-absent -- a patient-safety failure that throws no error. (b) **Never `bcftools merge` single-sample VCFs into a cohort.** Absence of a record is then read as homozygous reference, fabricating genotypes; joint-genotype per-sample gVCFs instead so "confident hom-ref" is distinguished from "no data."
3. **Filter site-level first, then genotype-level, then recompute cohort QC.** Setting genotypes to no-call (`./.`) changes missingness, HWE, and allele frequencies, so those metrics must be computed on the genotype-filtered matrix, not before.
4. **A single genome-wide F1 is nearly meaningless.** Callers agree on easy SNPs (F1 > 0.999); they diverge in indels-in-repeats, segmental duplications, and MHC. Benchmark stratified, within the GIAB confident region, or do not claim accuracy (Krusche 2019 *Nat Biotechnol* 37:555-560).

## Workflow overview

```
FASTQ
  | [1] QC & trim -------------------> fastp            (read-qc/fastp-workflow)
  v
  | [2] Align ----------------------> bwa-mem2          (read-alignment/bwa-alignment)
  v     ^-- reference commitment: GRCh38 analysis set / T2T, ALT/decoy handling
  | [3] Mark duplicates ------------> samtools markdup  (alignment-files/duplicate-handling)
  v
  | [4] (BQSR? optional on modern binned-quality instruments)
  v
  | [5] Call -----------------------> bcftools | GATK HaplotypeCaller | DeepVariant | DRAGEN
  v     ^-- single-sample OR per-sample gVCF -> joint-genotype (variant-calling/joint-calling)
  | [6] Normalize (BEFORE annotate) -> bcftools norm -m-any -f ref  (variant-calling/variant-normalization)
  v
  | [7] Filter: site-level THEN genotype-level         (variant-calling/filtering-best-practices)
  v
  | [8] Recompute cohort QC on the genotype-filtered matrix  (missingness, Ti/Tv, het/hom, excess-het HWE)
  v
  | [9] Annotate -------------------> VEP / SnpEff      (variant-calling/variant-annotation)
  v
  | [10] Benchmark & QC ------------> hap.py/vcfeval, bcftools stats  (variant-calling/vcf-statistics)
  v
Filtered, normalized, benchmarked VCF
```

## Reference genome: the pipeline-wide commitment

**Decision made once, before alignment; everything downstream inherits it.** Mechanism of building/indexing the reference lives in read-alignment/bwa-alignment; the deeper reasoning below is what a reviewer expects justified.

| Choice | Commit to it when | Consequence inherited downstream |
|--------|-------------------|----------------------------------|
| GRCh38 analysis set + decoys (hs38DH), ALT-aware (bwa-postalt) | Human germline, research or most clinical | Decoys soak up off-target reads; ALT-aware mapping recovers reads in MHC/segdup loci that ALT-unaware mapping force-fits to the primary, inflating false positives |
| GRCh38 analysis set, ALT-unaware (primary only) | Frozen clinical pipeline needing deterministic simplicity | Simpler and validated, but loses signal in ~5 Mb of ALT-bearing loci |
| Masked GRCh38 (false-duplication fix) | Calling in CBS, U2AF1, KCNE1B, KCNJ18 and other affected genes | Recovers reads whose mapQ collapsed across the phantom duplicate copy |
| T2T-CHM13 | Research needing segdups/centromeres/dark genes; maximum accuracy | Reveals variants in newly resolved regions and removes GRCh38 false-duplication artifacts, but no lossless liftover to GRCh37/38, so the entire annotation/interpretation stack must be revalidated (Nurk 2022 *Science* 376:44-53; Aganezov 2022 *Science* 376:eabl3533) |

The reason to fix this first: annotation databases, panel BEDs, benchmark truth sets, and any cohort a sample is joint-called with are all coordinate-specific. Mixing builds (e.g. normalizing to GRCh38 then annotating against a GRCh37 dbSNP) is a guaranteed silent miss. "We used GRCh38" is under-specified -- plain vs masked vs analysis-set-with-decoys materially changes results in named clinical genes.

## The canonical order and why

Each step assumes the previous; the order is defensible under review (canonical preprocessing order, filtering/representation practice).

1. **QC/trim** -- remove adapters and low-quality tails before they corrupt alignment and duplicate detection.
2. **Align** -- to the committed reference, with read groups (SM/ID/PL/LB); read groups are a hard GATK requirement.
3. **Mark duplicates** -- PCR/optical duplicates are not independent evidence; marking (not removing) lets the caller down-weight them. Skip for amplicon/UMI data.
4. **BQSR -- honestly optional on modern instruments.** BQSR corrected context/cycle-dependent miscalibration on 2010-era continuous-quality Illumina. NovaSeq/NovaSeq X emit ~4 quality bins, leaving little to recalibrate; callsets are largely unchanged with vs without it. DeepVariant explicitly recommends NOT running BQSR (its CNN learned the raw-quality error model); DRAGEN handles quality internally (and uses DRAGSTR for STR/indel error modeling). Keep it for GATK-HaplotypeCaller consistency if a frozen pipeline demands it; otherwise the modern indel-accuracy lever is STR-aware error modeling (`--dragen-mode`), not BQSR.
5. **Call** -- per-sample VCF, or per-sample gVCF (`-ERC GVCF`) if a cohort will be joint-genotyped.
6. **Normalize BEFORE annotate/compare** -- `bcftools norm -m-any -f ref.fa` (split multiallelics, then left-align + parsimony), against the SAME reference used for annotation. Add `-a` (atomize) only when the downstream database is decomposed. This is the most common real ordering bug: annotate-then-normalize attaches consequences to a non-canonical representation that fails to match the database. The binding constraint is normalize-before-ANNOTATE/COMPARE, not normalize-before-filter: GATK convention runs `VariantFiltration` on the raw multiallelic records (its annotations are computed on that representation), then normalizes -- `bwa_gatk_workflow.sh` does exactly that, while `bwa_bcftools_workflow.sh` normalizes first. Both are correct; neither annotates before normalizing.
7. **Filter site-level, then genotype-level** -- site filters (VQSR/hard/ML) decide whether a *site* is real; genotype filters (`GQ`/`DP`/allele-balance) decide whether an *individual genotype* is trustworthy. SNPs and indels are filtered separately (different error processes and truth resources).
8. **Recompute cohort QC on the genotype-filtered matrix** -- missingness, Ti/Tv, het/hom, excess-het HWE. Doing HWE before genotype filtering lets low-GQ garbage drive spurious deviation.
9. **Annotate** on the normalized (and, where consequence matters, haplotype-resolved) representation.
10. **Benchmark/validate** after transforms (`hap.py`, `bcftools stats`).

## Choosing the calling engine

Pipeline-level selection only; the mechanism and full decision table live in variant-calling/variant-calling. Hand off there to pick, then return here for chaining.

| Situation | Lean toward | Hand off to |
|-----------|-------------|-------------|
| Auditable open-source, large cohort, joint calling | GATK HaplotypeCaller GVCF -> GenomicsDBImport -> GenotypeGVCFs | variant-calling/gatk-variant-calling, variant-calling/joint-calling |
| Best indel/difficult-region accuracy, single or cohort | DeepVariant (+ GLnexus for cohorts) | variant-calling/deepvariant |
| Quick/exploratory, non-model organism, limited compute | bcftools mpileup + call | variant-calling/variant-calling |
| Maximum throughput on Illumina, hardware available | DRAGEN (or GATK `--dragen-mode` for the open equivalent) | variant-calling/variant-calling |

**Single-sample vs cohort is a chaining decision, not a caller feature.** For a cohort, emit per-sample gVCFs and joint-genotype them so a variant seen in one sample is evaluated in all (cohort rescue of low-coverage hets, squared-off genotype matrix). This is what makes the pipeline forward-compatible with new samples (the N+1 problem). Full mechanism: variant-calling/joint-calling.

## Primary path: BWA-MEM2 + bcftools

Fast, dependency-light, good for exploratory work and non-model organisms; weaker on indels in homopolymers than reassembly callers.

### Step 1: QC/trim with fastp

```bash
fastp -i sample_R1.fastq.gz -I sample_R2.fastq.gz \
    -o trimmed/sample_R1.fq.gz -O trimmed/sample_R2.fq.gz \
    --detect_adapter_for_pe \
    --qualified_quality_phred 20 \
    --length_required 50 \
    --html qc/sample_fastp.html
```

### Step 2: Align with BWA-MEM2

Read groups are mandatory; add `-Y` (soft-clip supplementary) if structural-variant calling is downstream, and `-K 100000000` for thread-count-invariant output. Reference/analysis-set choice: read-alignment/bwa-alignment.

```bash
bwa-mem2 index reference.fa   # once
bwa-mem2 mem -t 8 -K 100000000 \
    -R "@RG\tID:sample\tSM:sample\tPL:ILLUMINA\tLB:lib1" \
    reference.fa trimmed/sample_R1.fq.gz trimmed/sample_R2.fq.gz \
  | samtools view -bS - > aligned/sample.bam
```

### Step 3: Mark duplicates

Strict order (samtools convention): collate (name) -> fixmate `-m` -> sort (coordinate) -> markdup. Detail: alignment-files/duplicate-handling.

```bash
# collate groups mates by name; fixmate -m adds the ms/MC tags markdup needs; markdup needs coordinate order.
# Do NOT coordinate-sort before fixmate, and do NOT markdup amplicon/PCR data (use UMIs there).
samtools collate -@ 8 -O -u aligned/sample.bam \
  | samtools fixmate -m -@ 8 -u - - \
  | samtools sort -@ 8 -u - \
  | samtools markdup -@ 8 - aligned/sample.markdup.bam
samtools index aligned/sample.markdup.bam
```

### Step 4: Call and normalize

```bash
# Single sample (mpileup passes MQ/BQ filters into the pileup)
# -a FORMAT/DP,FORMAT/AD + call -f GQ emit the per-sample DP/GQ the Step 5 genotype filter needs.
bcftools mpileup -Ou -f reference.fa -a FORMAT/DP,FORMAT/AD --max-depth 250 --min-MQ 20 --min-BQ 20 \
    aligned/sample.markdup.bam \
  | bcftools call -mv -f GQ -Oz -o variants/sample.vcf.gz

# Normalize BEFORE any annotation or cross-callset comparison, against the SAME reference
bcftools norm -m-any -f reference.fa -Oz -o variants/sample.norm.vcf.gz variants/sample.vcf.gz
bcftools index variants/sample.norm.vcf.gz
```

For multi-sample cohorts, bcftools can call several BAMs jointly, but the GATK/DeepVariant gVCF path is preferred at scale (variant-calling/joint-calling).

### Step 5: Filter (site then genotype)

```bash
# Site-level (bcftools flags rather than removes, so failures stay auditable)
bcftools filter -Oz -s LowQual \
    -e 'QUAL<20 || INFO/DP<10 || MQ<30' \
    -o variants/sample.siteflt.vcf.gz variants/sample.norm.vcf.gz

# Genotype-level: set low-confidence genotypes to no-call (NOT 0/0)
bcftools filter -Oz -S . \
    -e 'FMT/GQ<20 | FMT/DP<8' \
    -o variants/sample.filtered.vcf.gz variants/sample.siteflt.vcf.gz
bcftools index variants/sample.filtered.vcf.gz
```

## Alternative path: BWA-MEM2 + GATK HaplotypeCaller

Local reassembly + PairHMM; the auditable reference implementation, strong on indels. Full mechanism: variant-calling/gatk-variant-calling.

```bash
gatk CreateSequenceDictionary -R reference.fa
samtools faidx reference.fa

# DRAGEN mode: no BQSR, STR-aware indel model (DRAGSTR), improved QUAL calibration
gatk HaplotypeCaller -R reference.fa -I aligned/sample.markdup.bam \
    -O gvcf/sample.g.vcf.gz -ERC GVCF --dragen-mode

# Cohort: consolidate gVCFs then joint-genotype (NEVER bcftools merge single-sample VCFs)
gatk GenomicsDBImport --sample-name-map gvcf/map.txt \
    --genomicsdb-workspace-path genomicsdb -L intervals.bed
gatk GenotypeGVCFs -R reference.fa -V gendb://genomicsdb -O variants/cohort.vcf.gz
```

## Filtering strategy depends on cohort size

The site-level filter is chosen by cohort size, platform, and organism; genotype-level filtering is always applied on top. Full mechanism and thresholds: variant-calling/filtering-best-practices.

| Cohort / data | Site-level filter | Why |
|---------------|-------------------|-----|
| Large WGS cohort (~30+ jointly genotyped) | VQSR (or AS_VQSR for huge cohorts) | The Gaussian-mixture model needs tens of thousands of variants and truth-resource overlap to fit; unreliable below that |
| Single sample / small cohort | GATK hard filters or VETS/NVScoreVariants | VQSR is non-identifiable on few variants; a "converged" model on one exome is filtering on noise |
| Exome specifically | Hard filters (do NOT use DP as a VQSR annotation) | Capture-boundary coverage cliffs break the annotation manifold |
| Non-model organism | Hard filters or a bootstrapped truth set | No HapMap/Omni/Mills truth resources exist |
| DeepVariant / DRAGEN output | Use the caller's own calibration; do NOT re-apply GATK hard filters | Their error modes differ; classic annotations do not describe them |

SNPs and indels are filtered separately (different error processes, truth resources, abundance). Hard-filter starting points (SNPs `QD<2, FS>60, MQ<40, MQRankSum<-12.5, ReadPosRankSum<-8, SOR>3`; indels loosen `FS>200`, tighten `ReadPosRankSum<-20`) are lenient heuristics to tune, not universal truth. RankSum annotations are only defined at het sites -- a hand-written filter must treat a missing annotation as PASS, or every hom-alt site vanishes.

## Benchmarking the pipeline

**Goal:** a defensible accuracy statement, not a single number.

The only rigorous way to compare a callset to truth is haplotype-aware, stratified, and confined to the truth set's confident region. Two VCFs can encode the identical haplotype with different records, so a naive `bcftools isec`/line-diff overcounts errors; use `hap.py` wrapping the `vcfeval` engine, which replays variants onto the reference and matches at the haplotype level (Krusche 2019 *Nat Biotechnol* 37:555-560; GIAB truth, Zook 2019 *Nat Biotechnol* 37:561-566).

```bash
# Only meaningful when the sample IS a GIAB genome (HG001-HG007) with a truth VCF + confident BED.
# -f = confident/callable region BED (TP/FP/FN counted ONLY inside it; calls outside are UNK, not FP)
hap.py truth.vcf.gz query.norm.vcf.gz \
    -f HG002_confident.bed \
    -r reference.fa \
    -o bench/hg002 \
    --engine=vcfeval \
    --stratification stratification.tsv   # GIAB region BEDs: low-complexity, segdup, MHC, GC-extreme
```

Discipline that separates a senior benchmark from a naive one:
- **Refuse the global F1.** Report SNP and INDEL separately, and show the low-complexity/segmental-duplication/MHC rows explicitly -- hiding them behind an all-regions average is the most common soft cheat.
- **Do not benchmark an ML caller only on its training genome.** DeepVariant and DRAGEN-ML train on GIAB coordinates, so scoring on HG002 alone partly measures memorization; score on a held-out or semi-blinded sample (HG003/HG004).
- **"We found variants GIAB missed" is almost always a category error** -- calls outside the confident region, which GIAB declined to adjudicate, not accuracy. Real hard-region claims cite CMRG or an assembly-based benchmark.
- **When the sample is not a GIAB genome** (the usual case), there is no truth VCF; fall back to proxy QC -- Ti/Tv (~2.0-2.1 WGS, ~3.0-3.3 exome), dbSNP overlap, het/hom by ancestry, and trio Mendelian concordance if a family is available. These are proxies for the absence of a benchmark, not a substitute for one (variant-calling/vcf-statistics).

## QC checkpoints between steps

| After | Gate | Interpretation |
|-------|------|----------------|
| QC/trim | Q30 >85%, adapter <1% | DNA is typically higher quality than RNA |
| Alignment | Mapped >95%, properly paired >90% (`samtools flagstat`) | Low mapping rate: wrong reference or contamination |
| Dedup | Duplicates <30% WGS, <50% exome | High duplication: PCR over-amplification, low input |
| Calling | Ti/Tv ~2.0-2.1 WGS, ~3.0-3.3 exome; dbSNP overlap >95% | Ti/Tv sliding toward 0.5 (random) signals false-positive inflation -- filters too loose. `bcftools stats` counts known sites from the ID column, and callers leave it as `.`: run `bcftools annotate -c ID -a dbsnp.vcf.gz` first or the dbSNP-overlap line reads 0% regardless of quality |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Annotation reports a known pathogenic variant as novel/absent | Annotated before normalizing; indel one base off the database coordinate | `bcftools norm -m-any -f ref` against the SAME build as the annotation DB, BEFORE annotation |
| Cohort has impossible all-hom-ref genotypes at variant sites | Built the cohort by `bcftools merge` of single-sample VCFs | Emit per-sample gVCFs and joint-genotype (variant-calling/joint-calling) |
| Every hom-alt site filtered out | Hand-written filter treats missing RankSum as failing | Treat missing annotation as PASS; RankSum is defined only at het sites |
| VQSR "converged" on one exome but the callset is garbage | VQSR needs tens of thousands of variants across ~30+ samples | Use hard filters or VETS/NVScoreVariants for single samples/exomes |
| Spurious variants in CBS/U2AF1/KCNE1B | GRCh38 false duplications collapse mapQ | Use a masked GRCh38 or T2T-CHM13; commit the reference before calling |
| GATK error "sample ... has no read group" | Read groups omitted at alignment | Re-run `bwa-mem2 mem -R "@RG\t..."` (SM/ID/PL/LB) |
| Different variant counts from vt vs bcftools on the same data | vt decomposes MNPs by default, bcftools does not | Standardize ONE normalization tool + flags across every cohort compared (variant-calling/variant-normalization) |

## Pipeline map (hand-offs)

- read-qc/fastp-workflow -- QC/trim options and report interpretation
- read-alignment/bwa-alignment -- BWA-MEM2 parameters, read groups, ALT/decoy analysis set, reference indexing
- alignment-files/duplicate-handling -- the collate/fixmate/sort/markdup order and UMI cases
- variant-calling/variant-calling -- engine selection (bcftools vs GATK vs DeepVariant vs DRAGEN) and ploidy
- variant-calling/gatk-variant-calling -- HaplotypeCaller, GVCF, BQSR/DRAGSTR, edge cases
- variant-calling/deepvariant -- CNN calling, platform models, DeepTrio, GLnexus cohorts
- variant-calling/joint-calling -- per-sample gVCF -> cohort joint genotyping, the N+1 problem, scaling
- variant-calling/variant-normalization -- left-align/parsimony, multiallelic split, MNP decomposition
- variant-calling/filtering-best-practices -- VQSR vs hard vs ML by cohort size; site vs genotype filters
- variant-calling/variant-annotation -- VEP/SnpEff on the normalized representation
- variant-calling/vcf-statistics -- Ti/Tv, het/hom, contamination/relatedness identity QC

The complete runnable scripts for both paths are in this skill's examples/ (`bwa_bcftools_workflow.sh`, `bwa_gatk_workflow.sh`).

## Related Skills

- database-access/sra-data - Pull public FASTQ for reanalysis (ENA mirror or STRIDES cloud)
- database-access/ncbi-datasets-cli - Pull reference genome assembly via Datasets v2 CLI
- read-qc/fastp-workflow - Detailed QC options
- sequence-io/fastq-quality - Confirm the FASTQ quality encoding (Phred+33 vs legacy Phred+64/Solexa) before trimming public or pre-2011 data
- sequence-io/paired-end-fastq - Keep R1/R2 mates synchronized; independent per-mate filtering silently desyncs pairs
- read-alignment/bwa-alignment - BWA-MEM2 parameters, read groups, ALT/decoy analysis set, the dedup ordering
- alignment-files/duplicate-handling - Duplicate marking details
- variant-calling/variant-calling - Engine selection and bcftools calling options
- variant-calling/gatk-variant-calling - GATK HaplotypeCaller and DRAGEN mode
- variant-calling/deepvariant - Deep-learning calling and GLnexus cohorts
- variant-calling/joint-calling - Cohort joint genotyping and scaling
- variant-calling/variant-normalization - Normalize before annotate/compare
- variant-calling/filtering-best-practices - VQSR, hard filters, VETS
- variant-calling/variant-annotation - Annotate variants with VEP
- variant-calling/vcf-statistics - Ti/Tv, het/hom, and identity QC

## References

- Krusche P, Trigg L, Boutros PC, et al. (GA4GH Benchmarking Team). Best practices for benchmarking germline small-variant calls in human genomes. *Nature Biotechnology* 37:555-560 (2019). DOI 10.1038/s41587-019-0054-x. Stratified haplotype-aware benchmarking (hap.py/vcfeval).
- Zook JM, McDaniel J, Olson ND, et al. An open resource for accurately benchmarking small variant and reference calls. *Nature Biotechnology* 37:561-566 (2019). DOI 10.1038/s41587-019-0074-6. GIAB truth set + confident regions.
- DePristo MA, Banks E, Poplin R, et al. A framework for variation discovery and genotyping using next-generation DNA sequencing data. *Nature Genetics* 43:491-498 (2011). DOI 10.1038/ng.806. GATK framework.
- Van der Auwera GA, Carneiro MO, Hartl C, et al. From FastQ Data to High-Confidence Variant Calls: The Genome Analysis Toolkit Best Practices Pipeline. *Current Protocols in Bioinformatics* 43:11.10.1-11.10.33 (2013). DOI 10.1002/0471250953.bi1110s43.
- Poplin R, Ruano-Rubio V, DePristo MA, et al. Scaling accurate genetic variant discovery to tens of thousands of samples. *bioRxiv* 201178 (2018). DOI 10.1101/201178. Preprint only (never journal-published); the GVCF/joint-genotyping reference.
- Poplin R, Chang P-C, Alexander D, et al. A universal SNP and small-indel variant caller using deep neural networks. *Nature Biotechnology* 36:983-987 (2018). DOI 10.1038/nbt.4235. DeepVariant.
- Yun T, Li H, Chang P-C, et al. Accurate, scalable cohort variant calls using DeepVariant and GLnexus. *Bioinformatics* 36:5582-5589 (2020). DOI 10.1093/bioinformatics/btaa1081.
- Danecek P, Bonfield JK, Liddle J, et al. Twelve years of SAMtools and BCFtools. *GigaScience* 10:giab008 (2021). DOI 10.1093/gigascience/giab008.
- Nurk S, Koren S, Rhie A, et al. The complete sequence of a human genome. *Science* 376:44-53 (2022). DOI 10.1126/science.abj6987. T2T-CHM13.
- Aganezov S, Yan SM, et al. A complete reference genome improves analysis of human genetic variation. *Science* 376:eabl3533 (2022). DOI 10.1126/science.abl3533. Reference-choice variant-calling payoff.
<!-- END FILE: workflows/fastq-to-variants/SKILL.md -->

## 子目录：workflows/genome-annotation-pipeline

<!-- BEGIN FILE: workflows/genome-annotation-pipeline/SKILL.md -->
---
name: bio-workflows-genome-annotation-pipeline
description: Orchestrates genome annotation from assembled contigs to functional annotation, forking prokaryotic (Bakta one-step, genetic-code table from GTDB-Tk) vs eukaryotic (RepeatMask -> BRAKER3 -> functional -> ncRNA), then eggNOG/InterProScan functional assignment and Infernal/tRNAscan ncRNA. Use when committing the pro-vs-eukaryotic path and the genetic-code table from taxonomy (never guessing), annotating ONLY a decontaminated QC-passed assembly (CheckM2 before prokaryotic annotation is non-negotiable), committing the evidence set (RNA-seq + protein drives BRAKER3 training), soft-masking with a curated repeat library before gene prediction, or pinning the tool + DB version for any pangenome comparison. Hands mechanism to the genome-annotation component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: Bakta
goal_approach_exempt: true
workflow: true
depends_on:
  - genome-annotation/prokaryotic-annotation
  - genome-annotation/eukaryotic-gene-prediction
  - genome-annotation/repeat-annotation
  - genome-annotation/functional-annotation
  - genome-annotation/ncrna-annotation
  - genome-annotation/annotation-qc
  - genome-assembly/assembly-qc
qc_checkpoints:
  - after_repeat_masking: "Repeat content within expected range for taxon"
  - after_gene_prediction: "Gene count plausible, BUSCO completeness >90%"
  - after_functional_annotation: ">60% of genes with functional assignment"
---

## Version Compatibility

Reference examples tested with: BRAKER3 3.0+, BUSCO 5.5+, Bakta 1.9+, Infernal 1.1+, InterProScan 5.66+, Prokka 1.14+, RepeatMasker 4.1+, RepeatModeler 2.0.4+ (-threads replaced -pa in 2.0.4), eggNOG-mapper 2.1+, pandas 2.2+, tRNAscan-SE 2.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Genome Annotation Pipeline

**"Annotate my genome assembly"** -> Orchestrate prokaryotic (Bakta) or eukaryotic (BRAKER3) gene prediction, repeat masking (RepeatMasker), functional annotation (eggNOG-mapper, InterProScan), and ncRNA annotation (Infernal).

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

A gene set is ~95% right and 100% confident; its trustworthiness is decided at four seams, not inside the gene-finder.

1. **Pro- vs eukaryotic is THE fork, committed from taxonomy up front, and it fixes the genetic-code table.** Prokaryote -> Bakta one-step (verify the genetic-code TABLE from GTDB-Tk classification, never guess — a Mycoplasma under table 11 splits every gene at internal UGA). Eukaryote -> multi-step RepeatMask -> BRAKER3 -> functional -> ncRNA. There is no general-purpose eukaryote annotator: alternative genetic codes, trans-splicing, and polycistronic transcription break standard pipelines.
2. **Annotate ONLY a decontaminated, QC-passed assembly.** CheckM2 before prokaryotic annotation is non-negotiable: contamination >5% mixes two organisms' genes into one chimeric set; a gene-finder trained on a contaminated/fragmented assembly produces confidently-wrong models genome-wide that are invisible in the GFF3. Annotation quality is bounded above by assembly quality.
3. **The evidence set is a committed input, not an afterthought.** Eukaryotic: RNA-seq BAM + protein (OrthoDB) evidence drives BRAKER3's high-confidence training-set mining (the real advance — learning from loci where transcripts AND homology agree). Committing RNA-seq (ideally Iso-Seq for isoforms+UTRs) is decided at project design; without it the annotation is one-isoform, CDS-only, UTR-less and silently poisons AS/3'-tag/APA analyses.
4. **Tool + DB version + date is a reproducibility commitment.** Bakta's DB is versioned (record it); Prokka's is frozen ~2019 (a post-2019 gene is "hypothetical" in Prokka, "named" in Bakta — accessory-vs-core flips on tool vintage alone). For any comparison, re-annotate everyone with ONE pipeline + ONE DB version from FASTA.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Pro- vs eukaryotic path + genetic-code table (from taxonomy) | The whole tool chain; a wrong code table splits genes at recoded stops |
| Decontaminated, QC-passed assembly (CheckM2 gate) | Chimeric gene set / genome-wide corrupt training if skipped; annotation quality is bounded by assembly quality |
| Evidence set (RNA-seq + protein) | BRAKER3 training quality; without RNA-seq the annotation is isoform-naive, UTR-less |
| Tool + DB version | Named-vs-hypothetical and accessory-vs-core flip on tool vintage; re-annotate all with one version for comparison |

## Pipeline Overview

```
Assembled contigs
    |
    v
[0. Assembly QC] ----------> QUAST, BUSCO (confirm assembly quality)
    |
    +----- Prokaryotic? -----> Path A: Bakta (one-step annotation)
    |                                |
    |                                v
    |                          Annotated genome (GFF3, GenBank, FASTA)
    |
    +----- Eukaryotic? ------> Path B: Multi-step pipeline
                                    |
                                    v
                              [1. Repeat Masking] ----> RepeatModeler + RepeatMasker
                                    |
                                    v
                              [2. Gene Prediction] ---> BRAKER3 (RNA-seq + protein evidence)
                                    |
                                    v
                              [3. Functional Annotation] -> eggNOG-mapper + InterProScan
                                    |
                                    v
                              [4. ncRNA Annotation] ---> Infernal + tRNAscan-SE
                                    |
                                    v
                              Annotated genome (GFF3, proteins, functional tables)
```

## Path A: Prokaryotic Annotation (Bakta)

Bakta provides comprehensive one-step annotation for bacteria and archaea. Preferred over Prokka for new projects.

### Database Setup

```bash
bakta_db download --output /path/to/bakta_db --type full
```

### Run Bakta

```bash
bakta \
    --db /path/to/bakta_db \
    --output bakta_out \
    --prefix my_genome \
    --locus-tag MYORG \
    --genus Escherichia --species "coli" \
    --strain K12 \
    --gram - \
    --translation-table 11 \
    --threads 8 \
    assembly.fasta
# Set --translation-table from the GTDB-Tk classification, never a guess: table 11 for most
# bacteria, but --translation-table 4 for Mycoplasma/Spiroplasma (UGA = Trp, not stop) --
# annotating a Mycoplasma under table 11 splits every gene at its internal UGA codons.
# Add --complete ONLY for finished replicons; omit it for draft contigs (the common input).
```

### Prokaryotic QC Checkpoint

```python
import subprocess
import json

def validate_prokaryotic_annotation(bakta_dir, prefix, expected_cds_range=(500, 8000)):
    '''
    QC gates for prokaryotic annotation.
    - CDS count in expected range for genome size
    - tRNA count >= 20 (typical minimum for free-living bacteria)
    - rRNA operons detected
    '''
    gff_file = f'{bakta_dir}/{prefix}.gff3'

    feature_counts = {'CDS': 0, 'tRNA': 0, 'rRNA': 0, 'tmRNA': 0, 'ncRNA': 0}
    with open(gff_file) as f:
        for line in f:
            if line.startswith('#'):
                continue
            fields = line.strip().split('\t')
            if len(fields) >= 3 and fields[2] in feature_counts:
                feature_counts[fields[2]] += 1

    qc_pass = True
    if not (expected_cds_range[0] <= feature_counts['CDS'] <= expected_cds_range[1]):
        print(f'WARNING: CDS count {feature_counts["CDS"]} outside expected range {expected_cds_range}')
        qc_pass = False
    if feature_counts['tRNA'] < 20:
        print(f'WARNING: Only {feature_counts["tRNA"]} tRNAs detected (expect >= 20)')
        qc_pass = False

    print(f'Feature summary: {feature_counts}')
    return qc_pass, feature_counts
```

## Path B: Eukaryotic Annotation

### Step 1: Repeat Masking

```bash
# Build the RepeatModeler database FIRST, then the species-specific library
BuildDatabase -name mygenome assembly.fasta
RepeatModeler -database mygenome -threads 8 -LTRStruct

# CURATE the de novo library against a protein DB before masking, or real multi-copy gene
# families (NLR/R-genes, zinc-fingers) get masked and "discovered" as a gene-poor repertoire.
# Then soft-mask with the curated library (RepeatMasker uses the bundled Dfam DB in addition).
RepeatMasker \
    -lib mygenome-families.fa \
    -pa 8 \
    -xsmall \
    -gff \
    -dir repeat_out \
    assembly.fasta
```

#### Repeat Masking QC Checkpoint

```python
def check_repeat_content(repeatmasker_tbl, taxon='vertebrate'):
    '''
    Verify repeat content is within expected range for taxon.
    Typical ranges:
    - Vertebrate: 30-60%
    - Insect: 15-45%
    - Plant: 20-85%
    - Fungus: 3-20%
    '''
    expected_ranges = {
        'vertebrate': (30, 60), 'insect': (15, 45),
        'plant': (20, 85), 'fungus': (3, 20)
    }
    low, high = expected_ranges.get(taxon, (5, 80))

    with open(repeatmasker_tbl) as f:
        for line in f:
            if 'total interspersed' in line.lower():
                pct = float(line.strip().split()[-1].replace('%', ''))
                break

    qc_pass = low <= pct <= high
    if not qc_pass:
        print(f'WARNING: Repeat content {pct:.1f}% outside expected range ({low}-{high}%) for {taxon}')
    return qc_pass, pct
```

### Step 2: Gene Prediction with BRAKER3

```bash
# BRAKER3 combines GeneMark-ETP, AUGUSTUS, and TSEBRA
# Uses both RNA-seq and protein evidence for best results
braker.pl \
    --genome=repeat_out/assembly.fasta.masked \
    --bam=rnaseq_sorted.bam \
    --prot_seq=proteins.fa \
    --softmasking \
    --threads 8 \
    --species=my_species \
    --gff3 \
    --workingdir=braker_out

# If only RNA-seq evidence available
braker.pl \
    --genome=repeat_out/assembly.fasta.masked \
    --bam=rnaseq_sorted.bam \
    --softmasking \
    --threads 8 \
    --species=my_species \
    --gff3

# If only protein evidence available (use OrthoDB proteins)
braker.pl \
    --genome=repeat_out/assembly.fasta.masked \
    --prot_seq=orthodb_proteins.fa \
    --softmasking \
    --threads 8 \
    --species=my_species \
    --gff3
```

#### Gene Prediction QC Checkpoint

```bash
# BUSCO completeness on predicted proteins. Use the DEEPEST applicable clade dataset
# (e.g. insecta_odb10 / embryophyta_odb10), NOT the shallow eukaryota_odb10.
# The diagnostic that matters: compare this proteome BUSCO to a genome-mode BUSCO on the
# same assembly -- a large gap means the predictor missed present genes (see genome-annotation/annotation-qc).
busco \
    -i braker_out/braker.aa \
    -l <clade>_odb10 \
    -o busco_annotation \
    -m proteins \
    --cpu 8
```

```python
def check_gene_prediction(braker_gff, busco_summary, expected_genes_range=(15000, 35000)):
    '''
    QC gates after gene prediction.
    - Gene count within expected range for genome
    - BUSCO completeness > 90%
    - Mean exons per gene > 1 (spliced genes expected in eukaryotes)
    '''
    gene_count = 0
    exon_count = 0
    with open(braker_gff) as f:
        for line in f:
            if line.startswith('#'):
                continue
            feature = line.strip().split('\t')[2] if len(line.strip().split('\t')) >= 3 else ''
            if feature == 'gene':
                gene_count += 1
            elif feature == 'exon':
                exon_count += 1

    mean_exons = exon_count / gene_count if gene_count > 0 else 0

    with open(busco_summary) as f:
        for line in f:
            if line.strip().startswith('C:'):
                completeness = float(line.strip().split('C:')[1].split('%')[0])
                break

    issues = []
    if not (expected_genes_range[0] <= gene_count <= expected_genes_range[1]):
        issues.append(f'Gene count {gene_count} outside expected range {expected_genes_range}')
    if completeness < 90:
        issues.append(f'BUSCO completeness {completeness:.1f}% < 90%')
    if mean_exons < 2:
        issues.append(f'Mean exons/gene {mean_exons:.1f} is low for eukaryote')

    print(f'Genes: {gene_count}, Mean exons/gene: {mean_exons:.1f}, BUSCO: {completeness:.1f}%')
    return len(issues) == 0, issues
```

### Step 3: Functional Annotation

```bash
# eggNOG-mapper for comprehensive functional annotation
emapper.py \
    -i braker_out/braker.aa \
    --output eggnog_results \
    --cpu 8 \
    -m diamond \
    --tax_scope auto \
    --go_evidence non-electronic \
    --target_orthologs all \
    --seed_ortholog_evalue 1e-5 \
    --override

# InterProScan for domain annotation (complementary to eggNOG)
interproscan.sh \
    -i braker_out/braker.aa \
    -b interpro_results \
    -f tsv,gff3 \
    -goterms \
    -pa \
    -cpu 8
```

#### Functional Annotation QC Checkpoint

```python
import pandas as pd

def check_functional_annotation(eggnog_annotations, total_genes):
    '''
    QC gate: > 60% of genes should have functional assignment.
    Below 50% suggests database issues or highly divergent organism.
    '''
    cols = ['query', 'seed_ortholog', 'evalue', 'score', 'eggNOG_OGs', 'max_annot_lvl',
            'COG_category', 'Description', 'Preferred_name', 'GOs', 'EC', 'KEGG_ko']
    df = pd.read_csv(eggnog_annotations, sep='\t', comment='#', header=None)
    df.columns = (cols + [f'c{i}' for i in range(len(df.columns) - len(cols))])[:len(df.columns)]
    annotated = len(df[df['Description'] != '-'])
    pct_annotated = annotated / total_genes * 100

    has_go = len(df[df['GOs'] != '-'])
    has_kegg = len(df[df['KEGG_ko'] != '-'])

    print(f'Annotated: {annotated}/{total_genes} ({pct_annotated:.1f}%)')
    print(f'With GO terms: {has_go}, With KEGG: {has_kegg}')

    if pct_annotated < 60:
        print('WARNING: <60% annotated. Check database version or use broader taxonomy scope.')
    return pct_annotated >= 60
```

### Step 4: ncRNA Annotation

```bash
# tRNAscan-SE for tRNA genes
tRNAscan-SE \
    -E \
    --thread 8 \
    -o trna_results.txt \
    --gff trna.gff \
    assembly.fasta

# Infernal for Rfam-based ncRNA annotation. Rfam.cm ships pre-calibrated: cmpress it, never recalibrate.
# --cut_ga uses the curated per-family bit-score gathering thresholds (the correct Rfam default over a
# flat E-value); --rfam is the large-DB strict filter; --nohmmonly keeps GA valid for every model.
cmpress Rfam.cm
cmscan \
    --cpu 8 \
    --cut_ga --rfam --nohmmonly \
    --tblout rfam_results.tbl \
    --fmt 2 \
    --clanin Rfam.clanin \
    Rfam.cm \
    assembly.fasta
# Clan deoverlapping: drop hits marked '=' (dominated by a higher-scoring clanmate)
grep -v ' = ' rfam_results.tbl > rfam_results.deoverlapped.tbl
```

## Merging Annotations

```python
def merge_annotations(braker_gff, trna_gff, rfam_tbl, eggnog_tsv, output_gff):
    '''Merge gene predictions, ncRNAs, and functional annotations into final GFF3.'''
    import subprocess

    # Use AGAT for GFF merging and validation
    subprocess.run([
        'agat_sp_merge_annotations.pl',
        '--gff', braker_gff,
        '--gff', trna_gff,
        '-o', output_gff
    ], check=True)

    # Validate final GFF3
    subprocess.run([
        'agat_sp_statistics.pl',
        '--gff', output_gff,
        '-o', output_gff.replace('.gff3', '_stats.txt')
    ], check=True)

    print(f'Merged annotations written to {output_gff}')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Chimeric gene set; training corrupted genome-wide | Annotated a contaminated assembly | CheckM2/FCS-GX gate BEFORE annotation; decontaminate first |
| Genes split at recoded stops; low coding density, high hypothetical | Wrong genetic-code table | Set the table from GTDB-Tk taxonomy, not a guess |
| Real NLR/immune gene families deleted; suspiciously gene-poor | Over-masking with an uncurated repeat library | Filter the RepeatModeler library against a protein DB; confirm conserved families survive; soft-mask `-xsmall` |
| Accessory genome inflated ~10x in a pangenome | Frozen-DB annotation drift (Panaroo) | Re-annotate all assemblies with ONE pipeline + DB version from FASTA; existing GenBank annotations are unusable for pangenomics |
| BUSCO looks great but models are wrong | BUSCO-only quality claim (certifies ~1000 easy genes) | Proteome-mode BUSCO on delivered proteins; add mono-exonic fraction + length distribution + mRNA:gene ratio |
| Low gene count | Repeat masking too aggressive | Soft-mask (`-xsmall`) not hard-mask; curate the TE library first |
| Isoform-naive annotation (mRNA:gene = 1.00) | No RNA-seq evidence | Add RNA-seq (Iso-Seq for isoforms/UTRs) to BRAKER3 |

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

GENOME="assembly.fasta"
RNASEQ_BAM="rnaseq_sorted.bam"
PROTEINS="orthodb_proteins.fa"
BAKTA_DB="/path/to/bakta_db"
THREADS=8

# Determine organism type
ORGANISM_TYPE="${1:-eukaryotic}"  # prokaryotic or eukaryotic

if [ "$ORGANISM_TYPE" == "prokaryotic" ]; then
    echo "Running prokaryotic annotation with Bakta"
    echo "Step 0: Contamination/completeness gate (CheckM2 before annotation is non-negotiable)"
    checkm2 predict --input $GENOME --output-directory checkm2_out --threads $THREADS
    # Inspect checkm2_out/quality_report.tsv: proceed only if Completeness is high and Contamination < 5%
    # --translation-table comes from the GTDB-Tk classification, never a guess (rule 1). Bakta silently
    # assumes table 11; Mycoplasma/Spiroplasma need 4 (UGA = Trp, not stop) or every gene is truncated.
    bakta --db $BAKTA_DB --output bakta_out --prefix genome --translation-table 11 \
          --locus-tag MYORG --threads $THREADS $GENOME
    echo "Done. Results in bakta_out/"

else
    echo "Running eukaryotic annotation pipeline"

    echo "Step 0: Assembly QC (contiguity + completeness before committing to annotation)"
    quast.py $GENOME -o quast_out --threads $THREADS
    busco -i $GENOME -l "${LINEAGE:?set the DEEPEST applicable clade dataset, e.g. insecta_odb10 / embryophyta_odb10; eukaryota_odb10 is too shallow and inflates completeness}" -o busco_asm -m genome --cpu $THREADS

    echo "Step 1: Repeat masking"
    BuildDatabase -name mygenome $GENOME
    RepeatModeler -database mygenome -threads $THREADS -LTRStruct
    RepeatMasker -lib mygenome-families.fa -pa $THREADS -xsmall -gff -dir repeat_out $GENOME

    echo "Step 2: Gene prediction with BRAKER3"
    braker.pl --genome=repeat_out/$(basename $GENOME).masked \
              --bam=$RNASEQ_BAM --prot_seq=$PROTEINS \
              --softmasking --threads $THREADS --gff3 --workingdir=braker_out

    echo "Step 3: BUSCO QC (use the deepest applicable clade dataset, not eukaryota_odb10)"
    busco -i braker_out/braker.aa -l "${LINEAGE:?set the DEEPEST applicable clade dataset, e.g. insecta_odb10 / embryophyta_odb10; eukaryota_odb10 is too shallow and inflates completeness}" -o busco_check -m proteins --cpu $THREADS

    echo "Step 4: Functional annotation"
    emapper.py -i braker_out/braker.aa --output eggnog_out --cpu $THREADS -m diamond

    echo "Step 5: ncRNA annotation"
    tRNAscan-SE -E --thread $THREADS -o trna_out.txt --gff trna.gff $GENOME
    cmscan --cpu $THREADS --cut_ga --rfam --nohmmonly --tblout rfam.tbl --fmt 2 --clanin Rfam.clanin Rfam.cm $GENOME

    echo "Done. Check braker_out/, eggnog_out*, trna.gff, rfam.tbl"
fi
```

## Related Skills

- genome-annotation/prokaryotic-annotation - Bakta and Prokka details
- genome-annotation/eukaryotic-gene-prediction - BRAKER3 and AUGUSTUS options
- genome-annotation/repeat-annotation - Soft-masking before gene prediction
- genome-annotation/functional-annotation - eggNOG-mapper and InterProScan
- genome-annotation/ncrna-annotation - Infernal/Rfam and tRNAscan-SE detail
- rna-structure/ncrna-search - Covariance-model search, gathering thresholds, and clan resolution
- genome-annotation/annotation-qc - BUSCO genome-vs-proteome, OMArk, CheckM2 gates
- genome-assembly/assembly-qc - Pre-annotation assembly quality checks
- genome-intervals/gtf-gff-handling - GFF3/GTF hierarchy traversal, AGAT sanitizing/validation, coordinate conversion, and seqid-consistency checks on the merged annotation
- workflows/genome-assembly-pipeline - Upstream: hands off the decontaminated, QC-passed FASTA (with its QV/BUSCO)

## References

- Salzberg SL (2019) Next-generation genome annotation: we still struggle to get it right. *Genome Biology* 20:92. DOI 10.1186/s13059-019-1715-2. (error propagation.)
- Gabriel L, Bruna T, Hoff KJ, et al (2024) BRAKER3: fully automated genome annotation using RNA-seq and protein evidence with GeneMark-ETP, AUGUSTUS, and TSEBRA. *Genome Research* 34:769-777. DOI 10.1101/gr.278090.123. (high-confidence training-set mining.)
- Tonkin-Hill G, MacAlasdair N, Ruis C, et al (2020) Producing polished prokaryotic pangenomes with the Panaroo pipeline. *Genome Biology* 21:180. DOI 10.1186/s13059-020-02090-4. (annotation-drift accessory inflation.)
- Schwengers O, Jelonek L, Dieckmann MA, et al (2021) Bakta: rapid and standardized annotation of bacterial genomes via alignment-free sequence identification. *Microbial Genomics* 7:000685. DOI 10.1099/mgen.0.000685.
<!-- END FILE: workflows/genome-annotation-pipeline/SKILL.md -->

## 子目录：workflows/genome-assembly-pipeline

<!-- BEGIN FILE: workflows/genome-assembly-pipeline/SKILL.md -->
---
name: bio-workflows-genome-assembly-pipeline
description: Orchestrates an end-to-end de novo genome assembly project, routing each step to the right genome-assembly skill rather than restating it. Profiles the genome first (k-mer spectrum -> size, heterozygosity, ploidy), QCs reads, chooses an assembly path by data type (SPAdes for Illumina, Flye for noisy long reads, hifiasm for HiFi, metaFlye for communities), polishes only when needed, decontaminates, scaffolds with Hi-C, and finishes with three-axis QC (contiguity + completeness + correctness). Use when assembling a genome from raw reads and deciding which assembler, whether to polish, and how to prove the result is good.
tool_type: cli
primary_tool: Flye
workflow: true
depends_on:
  - genome-assembly/genome-profiling
  - read-qc/fastp-workflow
  - long-read-sequencing/long-read-qc
  - genome-assembly/short-read-assembly
  - genome-assembly/long-read-assembly
  - genome-assembly/hifi-assembly
  - genome-assembly/metagenome-assembly
  - genome-assembly/assembly-polishing
  - genome-assembly/contamination-detection
  - genome-assembly/scaffolding
  - genome-assembly/assembly-qc
qc_checkpoints:
  - after_profiling: "Genome-size and heterozygosity estimate obtained; sets NG50 denominator, purge level, assembler choice"
  - after_assembly: "Total length within ~10-20% of profiled size; contig count plausible for read type"
  - after_polishing: "Merqury QV improved or plateaued (do not over-polish HiFi); k-mers from accurate reads, not the polishing reads"
  - after_decontamination: "Single-organism: FCS-GX/BlobToolKit clean; MAG: CheckM2 >90% complete, <5% contam, GUNC pass"
  - after_scaffolding: "Contact map shows clean diagonal; off-diagonal blocks inspected/broken before calling chromosome-scale"
  - final_three_axis_qc: "Contiguity (auN/NG50 vs profiled size) + completeness (BUSCO/compleasm) + correctness (Merqury QV) all reported; never N50 alone"
---

## Version Compatibility

Reference examples tested with: GenomeScope2 2.0+, meryl 1.4+, Merqury 1.3+, fastp 0.23+, SPAdes 4.0+, Flye 2.9+, hifiasm 0.25+, metaFlye 2.9+, Racon 1.5+, medaka 2.0+, minimap2 2.26+, FCS-GX 0.5+, CheckM2 1.0+, GUNC 1.0+, YaHS 1.2+, QUAST 5.2+, BUSCO 5.5+, samtools 1.19+. Each owning genome-assembly skill is the source of truth for its tool's pinned version.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Tool outputs are driven by more than the binary version: medaka consensus quality depends on the basecaller MODEL string (must match the basecaller, e.g. `-m r1041_e82_400bps_sup_v5.0.0`); BUSCO/compleasm results depend on the lineage dataset and OrthoDB generation (record them); CheckM2/GTDB-Tk results track the reference DATABASE release; hifiasm output filenames and default purge behaviour change across versions (verify against the installed build). If a command errors, introspect the installed tool and adapt rather than retrying.

# Genome Assembly Pipeline

**"Assemble a genome from my sequencing reads and prove it is good"** -> Profile the genome, QC reads, route to the right assembler by data type, polish only if needed, decontaminate, scaffold if Hi-C exists, and finish with three-axis QC. This skill ORCHESTRATES the genome-assembly category; it routes each step to the owning skill and encodes the cross-cutting decisions, not each tool's full option set.

## The Single Most Important Modern Insight -- Assembly Is Three Orthogonal Questions, and Each Step Answers One

A genome project fails when one number stands in for the whole. Profiling sets expectations (how big, how heterozygous, how many haplotypes) BEFORE assembling, the assembler answers contiguity, polishing answers per-base accuracy, decontamination answers provenance, scaffolding answers arrangement, and QC must independently address all three of contiguity, completeness, and correctness. The orchestration job is to keep these separate and route each to its skill: a high N50 says nothing about whether the bases are right (Merqury QV) or whether the sequence is the organism's (contamination), and skipping profiling means the assembler guesses the parameters that profiling would have set.

## Decision Flow (Step 0 -> 6)

```
Raw reads (+ optional Hi-C, trio, short reads)
    |
    v
[0. Profile the genome] --> genome-assembly/genome-profiling
    |   k-mer spectrum (GenomeScope2) -> genome size, heterozygosity, ploidy.
    |   Sets NG50 denominator, expected haplotype count, hifiasm purge level,
    |   and which assembly path is even sensible. Do this BEFORE assembling.
    v
[1. QC reads] -----------> short: read-qc/fastp-workflow
    |                       long:  long-read-sequencing/long-read-qc
    |   Garbage-in caps assembly quality; record platform + basecaller era
    |   (it is an assembly PARAMETER, see step 2), trim internal adapters.
    v
[2. Choose path BY DATA TYPE]
    |  Illumina-only small/isolate -> genome-assembly/short-read-assembly (SPAdes)
    |  noisy ONT/CLR              -> genome-assembly/long-read-assembly (Flye --nano-hq for R10)
    |  PacBio HiFi                -> genome-assembly/hifi-assembly (hifiasm, phased)
    |  community sample           -> genome-assembly/metagenome-assembly (metaFlye/metaSPAdes + binning)
    |  large/heterozygous euk     -> long-read or HiFi, NOT short reads
    v
[3. Polish IF needed] ---> genome-assembly/assembly-polishing
    |   noisy long-read assemblies: Racon -> medaka (model MUST match basecaller).
    |   Do NOT polish HiFi reflexively (often net-harmful). Measure with Merqury QV,
    |   not the reads polished with. Skip entirely for SPAdes/HiFi when QV is already high.
    v
[4. Decontaminate] ------> genome-assembly/contamination-detection
    |   single organism: FCS-GX (GenBank-mandatory) + BlobToolKit blob plot.
    |   MAG:              CheckM2 + GUNC (chimerism). Two disjoint problems (see below).
    v
[5. Scaffold IF Hi-C] ---> genome-assembly/scaffolding
    |   automated YaHS produces a DRAFT; manual contact-map curation is the standard.
    |   Scaffold N50 != contig N50 (gaps are Ns). Skip if no Hi-C.
    v
[6. Three-axis QC] ------> genome-assembly/assembly-qc
        contiguity (auN/NG50 vs profiled size) + completeness (BUSCO/compleasm)
        + correctness (Merqury QV). Report the triad; NEVER N50 alone.
```

## Routing Table by Scenario

| Scenario | Path | Routes to |
|----------|------|-----------|
| Bacterial isolate, ONT R10 only | profile -> QC -> Flye `--nano-hq` -> medaka -> FCS-GX -> QC | long-read-assembly, assembly-polishing, contamination-detection |
| Bacterial isolate, Illumina only | profile -> fastp -> SPAdes `--isolate` -> FCS-GX -> QC | short-read-assembly |
| Small genome, ONT, max quality | profile -> QC -> multi-assembler consensus (Trycycler/Autocycler) -> medaka -> QC | long-read-assembly |
| Diploid eukaryote, HiFi (+Hi-C/trio) | profile -> QC -> hifiasm (hap1/hap2) -> purge check -> decontam -> scaffold -> QC | hifi-assembly, scaffolding, contamination-detection |
| Large heterozygous eukaryote, ONT | profile -> QC -> Flye -> purge_dups -> medaka -> decontam -> scaffold -> QC | long-read-assembly, scaffolding |
| Community / microbiome sample | QC -> metaFlye/metaSPAdes -> binning -> CheckM2 + GUNC | metagenome-assembly, contamination-detection |
| Hi-C reads available | after contigs+polish: scaffold, curate contact map | scaffolding |
| Reads not yet QC'd | start at step 1 | read-qc/fastp-workflow, long-read-sequencing/long-read-qc |

## Cross-Cutting Gotchas (surface these at every project)

- **Basecaller era must match the assembler flag.** `--nano-raw` on R10/Dorado-SUP reads silently collapses real repeats while RAISING N50; `--nano-hq` is the R10 default. The platform + basecaller model is an assembly parameter, not metadata.
- **A primary assembly is not a haplotype.** The hifiasm primary is a maternal/paternal mosaic that exists in no cell; for any allele-aware downstream use hap1/hap2 phased with trio or Hi-C, and treat HiFi-only hap1/hap2 as only partially phased.
- **N50 is gamed.** It rises when an assembly gets WORSE (misjoins, collapsed repeats, retained haplotigs). Report the triad (auN/NG50 + BUSCO + Merqury QV), never N50 alone.
- **A MAG is a population consensus, not a genome.** The unit of success is a binned, MIMAG-gated MAG, and "% contamination" conflates foreign-organism mixing, strain mixing, and assembly artifacts.
- **"Contamination" is two disjoint problems.** Single-organism cross-kingdom foreign sequence (FCS-GX, blob plot) is a different question from intra-domain MAG contamination/chimerism (CheckM2 + GUNC); do not apply one tool's question to the other's input.
- **Scaffold N50 >> contig N50 because gaps are Ns.** Scaffold contiguity is glue, not sequence; every join is a hypothesis a contact map must confirm. Report contig N50 alongside scaffold N50.

## Step 0: Profile the Genome (do this first)

Route the full treatment to genome-assembly/genome-profiling. The minimal orchestration step:

```bash
# k-mer count from ACCURATE reads (Illumina/HiFi, NEVER noisy ONT), then GenomeScope2 for size / heterozygosity / ploidy
meryl count k=21 output reads.meryl accurate_reads.fq.gz
meryl histogram reads.meryl > reads.hist
genomescope2 -i reads.hist -o gscope_out -k 21
# read off: estimated haploid genome size, heterozygosity %, and (with -p) ploidy.
# These set the NG50 denominator, the expected number of haplotypes, and the purge decision.
```

## Step 1: QC Reads

Short reads route to read-qc/fastp-workflow; long reads to long-read-sequencing/long-read-qc.

```bash
fastp -i R1.fq.gz -I R2.fq.gz -o t_R1.fq.gz -O t_R2.fq.gz \
    --detect_adapter_for_pe --qualified_quality_phred 20 --length_required 50 --html qc.html
```

## Step 2: Assemble (route by data type)

Give the assembler the exact preset for the chemistry; the wrong preset is silent. Detailed options live in the owning skills.

```bash
# Illumina-only small/isolate genome -> short-read-assembly
spades.py --isolate -1 t_R1.fq.gz -2 t_R2.fq.gz -o spades_out -t 16
# NOTE: --careful is small-genome-only; do NOT use it on large eukaryote genomes.

# Noisy ONT (R10/Dorado-SUP) -> long-read-assembly. --nano-hq is the modern default.
flye --nano-hq ont.fq.gz --out-dir flye_out --threads 16     # --genome-size optional in recent Flye

# PacBio HiFi -> hifi-assembly (phased by default; verify output filenames per version)
hifiasm -o asm -t 16 hifi.fq.gz                              # add --h1/--h2 (Hi-C) or -1/-2 (trio) to phase

# Community sample -> metagenome-assembly
flye --nano-hq ont.fq.gz --meta --out-dir metaflye_out --threads 16    # --meta is a modifier; still need a read-type selector. Then bin + CheckM2/GUNC
```

## Step 3: Polish IF Needed

Polishing is read-type-matched and conditional. Route to genome-assembly/assembly-polishing.

```bash
# Noisy long-read assembly: medaka with the MATCHING model. medaka_consensus does its own
# read-to-assembly alignment from -i/-d (no separate minimap2/BAM step needed); add a Racon
# round upstream only if the assembler did not already polish - see assembly-polishing.
medaka_consensus -i ont.fq.gz -d flye_out/assembly.fasta -o medaka_out -t 16 \
    -m r1041_e82_400bps_sup_v5.0.0   # MUST match the basecaller model used to call the reads
# For a BACTERIAL isolate, prefer the methylation-aware bacterial model (medaka 2.0+):
#   medaka_consensus -i ont.fq.gz -d assembly.fasta -o medaka_out --bacteria
```

Do NOT reflexively polish a HiFi assembly (already ~Q30+; over-polishing lowers QV). SPAdes output needs no separate long-read polish. The stop signal is a Merqury QV plateau, not a fixed iteration count, and the QV must be measured against reads independent of those used to polish.

## Step 4: Decontaminate (route by sample type)

```bash
# Single-organism assembly (GenBank-mandatory foreign screen + blob plot)
python3 ./fcs.py screen genome --fasta assembly.fa --out-dir gx_out/ --gx-db "$GXDB/gxdb" --tax-id <taxid>
# acts on EXCLUDE/TRIM/FIX cross-kingdom contigs; keep host-integrated foreign sequence (see contamination-detection)

# MAG (intra-domain contamination + chimerism)
checkm2 predict --input bins/ --output-directory checkm2_out --threads 16
gunc run --input_dir bins/ --out_dir gunc_out                            # chimerism, orthogonal to CheckM2
```

## Step 5: Scaffold IF Hi-C Is Available

YaHS produces a draft; the contact map is the QC, not decoration. Route to genome-assembly/scaffolding.

```bash
# Map Hi-C to contigs, then YaHS; inspect the contact map (PretextMap/Juicer) and break misjoins.
yahs assembly.fasta hic_to_contigs.bam -o yahs_out          # output scaffolds + AGP; curate before publishing
```

## Step 6: Three-Axis QC (contiguity + completeness + correctness)

Route the full treatment to genome-assembly/assembly-qc. Report all three axes; lead with the QV.

```bash
# Contiguity vs the PROFILED genome size (NG50/auN, not bare N50)
quast.py final.fasta -o quast_out -t 16 --est-ref-size <profiled_size>

# Completeness on the DEEPEST applicable clade (compleasm on good genomes; BUSCO otherwise)
busco -i final.fasta -l <clade>_odb10 -o busco_out -m genome -c 16

# Correctness: Merqury QV from ACCURATE reads (k from best_k.sh, not hardcoded)
K=$(sh $MERQURY/best_k.sh <genome_size_bp> | tail -n1 | awk '{print int($1+0.5)}')   # round float->int
meryl count k=$K output reads.meryl accurate_reads.fq.gz
merqury.sh reads.meryl final.fasta merqury_out          # QV + k-mer completeness + spectra-cn
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Assembly ~1.5-2x profiled size, high BUSCO-Duplicated | uncollapsed haplotigs (false duplication) | purge_dups; check half-coverage depth peak; do not over-purge real segmental duplications |
| Contiguous but gene models frameshift | noisy long-read assembly not polished | Racon -> medaka (matched model); measure QV |
| QV drops after polishing | over-polishing an already-accurate (HiFi) assembly | stop polishing; HiFi rarely needs short-read polish |
| medaka consensus worse than input | wrong basecaller model string | set `-m` to the model the reads were basecalled with |
| Fewer contigs than expected but repeats collapsed | `--nano-raw` used on R10 reads | re-run Flye with `--nano-hq` |
| CheckM2 says clean but bin looks mixed | chimera with disjoint markers | run GUNC; CheckM2 marker redundancy cannot see chimerism |
| Scaffold N50 huge, contig N50 small | scaffolding glue, not sequence | inspect contact map, break off-diagonal misjoins |

## Related Skills

- genome-assembly/genome-profiling - Step 0: k-mer spectrum for size, heterozygosity, ploidy; sets expectations before assembling
- genome-assembly/short-read-assembly - SPAdes path for Illumina-only small/isolate genomes
- genome-assembly/long-read-assembly - Flye/Canu path for noisy ONT/CLR reads
- genome-assembly/hifi-assembly - hifiasm phased path for PacBio HiFi
- genome-assembly/metagenome-assembly - metaFlye/metaSPAdes + binning for community samples
- genome-assembly/assembly-polishing - Racon/medaka/Pilon, applied only when needed
- genome-assembly/contamination-detection - FCS-GX/BlobToolKit (single organism) vs CheckM2/GUNC (MAG)
- genome-assembly/scaffolding - YaHS Hi-C scaffolding and contact-map curation
- genome-assembly/assembly-qc - Three-axis QC: auN/NG50 + BUSCO + Merqury QV
- read-qc/fastp-workflow - Short-read QC before assembly
- long-read-sequencing/long-read-qc - Long-read length/quality QC and basecaller-era awareness
- workflows/genome-annotation-pipeline - Downstream: only a decontaminated, QC-passed FASTA should hand off to annotation

## References

- Rhie A, Walenz BP, Koren S, Phillippy AM (2020) Merqury: reference-free quality, completeness, and phasing assessment for genome assemblies. *Genome Biology* 21:245. DOI 10.1186/s13059-020-02134-9. (QV/completeness from k-mers.)
- Manni M, Berkeley MR, Seppey M, Simao FA, Zdobnov EM (2021) BUSCO update: novel and streamlined workflows. *Molecular Biology and Evolution* 38:4647-4654. DOI 10.1093/molbev/msab199.
- Rhie A, McCarthy SA, Fedrigo O, et al (2021) Towards complete and error-free genome assemblies of all vertebrate species. *Nature* 592:737-746. DOI 10.1038/s41586-021-03451-0. (three-axis / VGP standard.)
- Ranallo-Benavidez TR, Jaron KS, Schatz MC (2020) GenomeScope 2.0 and Smudgeplot for reference-free profiling of polyploid genomes. *Nature Communications* 11:1432. DOI 10.1038/s41467-020-14998-3.
<!-- END FILE: workflows/genome-assembly-pipeline/SKILL.md -->

## 子目录：workflows/grn-pipeline

<!-- BEGIN FILE: workflows/grn-pipeline/SKILL.md -->
---
name: bio-workflows-grn-pipeline
description: Orchestrates gene regulatory network inference from processed single-cell data to regulons and in-silico perturbation, via pySCENIC (RNA-only GRNBoost2 -> cisTarget -> AUCell), SCENIC+ (multiome cisTopic -> pycistarget -> eGRN), and CellOracle perturbation. Use when recognizing that an inferred GRN is UNDIRECTED by default and reporting only the evidence tier delivered (co-expression vs motif-pruned vs enhancer-resolved vs perturbation), matching species/assembly/namespace across the TF-list + cisTarget DB + motif2TF annotation, feeding RAW counts of the cleaned/doublet-free/batch-controlled cells (never imputed/batch-corrected values), running the cisTarget pruning that buys directionality (modules are not regulons without it), or choosing the RNA-only vs multiome path. Hands mechanism to the gene-regulatory-networks component skills; not a re-teach of any single step.
tool_type: python
primary_tool: pySCENIC
workflow: true
depends_on:
  - gene-regulatory-networks/scenic-regulons
  - gene-regulatory-networks/multiomics-grn
  - gene-regulatory-networks/perturbation-simulation
  - single-cell/clustering
qc_checkpoints:
  - after_grn_inference: "50-500 regulons detected, known TFs present"
  - after_activity_scoring: "AUCell scores separate known cell types"
  - after_perturbation: "Predicted shifts match known biology"
---

## Version Compatibility

Reference examples tested with: pySCENIC 0.12+, arboreto 0.1.6+, ctxcore 0.2+, pycisTopic 2.0+, pycistarget 1.0+, SCENIC+ 1.0a1 (Snakemake CLI), CellOracle 0.18+, anndata 0.10+, pandas 2.2+, scanpy 1.10+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: SCENIC+ is now a Snakemake pipeline (`scenicplus init_snakemake`); the pre-2024 manual `create_SCENICPLUS_object`/`build_grn` object API is deprecated. GRNBoost2's arboreto dask backend is the #1 operational landmine — use the bundled multiprocessing if the dask cluster hangs. The TF-list, cisTarget ranking DB, and motif2TF `.tbl` must all be the SAME species + assembly + collection vintage. Confirm in-tool before quoting.

# Gene Regulatory Network Pipeline

**"Infer gene regulatory networks from my single-cell data"** -> Orchestrate pySCENIC regulon inference (GRNBoost2, cisTarget, AUCell), CellOracle perturbation simulation, and regulon-based cell type characterization.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

1. **An inferred GRN is an UNDIRECTED association graph by default; directionality is IMPORTED, and only the evidence tier actually delivered should be reported.** GRNBoost2 co-expression is tier-1 (undirected); the cisTarget motif-pruning step (Path A step 2) is what buys directionality and discards indirect edges — modules before ctx are NOT regulons, calling them so is a category error. SCENIC+ adds enhancer resolution; perturbation adds causal direction. Do not write tier-6 "master regulator drives X" prose over a tier-1 co-expression result.
2. **Species/assembly/namespace must match across the TF-list, the cisTarget ranking DB, and the motif2TF `.tbl` — all three.** A mismatch (mouse genes in an hg38 DB; feather v1 DB with a v10 motif annotation) yields near-empty regulons. Also commit and report the search-space window (500bp/100bp proximal vs TSS±10kb) — results are not comparable across windows.
3. **Feed RAW counts of the CLEANED, doublet-free, batch-controlled cells — never imputed or batch-corrected values.** GRNBoost2 on imputed counts inflates correlations (imputation smooths neighbors into agreement); on batch-corrected values a batch module can pass motif enrichment by chance; doublets create a fake "hybrid regulator." Run SCENIC ONCE on the integrated object.
4. **Validate a regulon with an ORTHOGONAL modality, not the TF's own mRNA.** AUCell activity != TF expression; correlating a regulon's activity with its TF's expression is circular (and activity is dropout-robust while the TF mRNA may read zero). GRNBoost2 is stochastic — run multiple seeds and keep recurrent links (Van de Sande 2020).

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Species + assembly + gene namespace (HGNC vs MGI; hg38 vs mm10) | TF list, cisTarget DB, motif2TF `.tbl` must all match, or regulons are near-empty |
| cisTarget DB vintage + search window (proximal vs TSS±10kb; gene- vs region-based) | Which edges survive ctx pruning; results not comparable across windows/vintages |
| Input matrix identity (RAW counts, from the cleaned/doublet-free/integrated object) | Every adjacency and regulon; imputed/batch values fabricate edges |
| RNA-only vs multiome availability | Which path is possible: SCENIC+ REQUIRES paired multiome; RNA-only -> pySCENIC or CellOracle-with-prebuilt-base-GRN |

## Pipeline Overview

```
Processed AnnData (QC'd, normalized, clustered)
    |
    +----- RNA only? -------> Path A: pySCENIC (3-step)
    |                              |
    |                              v
    |                         [1. GRNBoost2] ----> TF-target adjacencies
    |                              |
    |                              v
    |                         [2. RcisTarget] ---> Regulon pruning (motif enrichment)
    |                              |
    |                              v
    |                         [3. AUCell] -------> Regulon activity scoring
    |
    +----- Multiome? -------> Path B: SCENIC+
    |                              |
    |                              v
    |                         [1. cisTopic] -----> Topic modeling on ATAC
    |                              |
    |                              v
    |                         [2. pycistarget] --> Enhancer-TF mapping
    |                              |
    |                              v
    |                         [3. SCENIC+] ------> eGRN construction
    |
    +---> [CellOracle Perturbation Simulation] (either path)
              |
              v
         Perturbation scores + predicted cell state shifts
```

## Path A: pySCENIC (RNA-Only)

### Step 1: GRN Inference with GRNBoost2

```python
import scanpy as sc
import pandas as pd
from arboreto.algo import grnboost2

adata = sc.read_h5ad('processed.h5ad')

# Extract expression matrix (raw counts recommended for GRNBoost2)
expr_matrix = pd.DataFrame(
    adata.raw.X.toarray() if hasattr(adata.raw.X, 'toarray') else adata.raw.X,
    index=adata.obs_names, columns=adata.raw.var_names
)

# TF list from cisTarget resources
# Human: https://resources.aertslab.org/cistarget/tf_lists/
tf_names = pd.read_csv('allTFs_hg38.txt', header=None)[0].tolist()
tf_names = [tf for tf in tf_names if tf in expr_matrix.columns]

adjacencies = grnboost2(expr_matrix, tf_names=tf_names, seed=42, verbose=True)
adjacencies.to_csv('adjacencies.tsv', sep='\t', index=False, header=False)
```

### Step 2: Regulon Pruning with RcisTarget

```python
from pyscenic.prune import prune2df, df2regulons
from pyscenic.utils import modules_from_adjacencies
from ctxcore.rnkdb import FeatherRankingDatabase

# cisTarget databases (~10 GB each, download once)
# Human: hg38_10kbp_up_10kbp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather
# Mouse: mm10_10kbp_up_10kbp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather
# FeatherRankingDatabase(fname, name) -- `name` is REQUIRED (no default) in ctxcore
dbs = [FeatherRankingDatabase(db, name=os.path.splitext(os.path.basename(db))[0]) for db in [
    'hg38_500bp_up_100bp_down.genes_vs_motifs.rankings.feather',
    'hg38_10kbp_up_10kbp_down.genes_vs_motifs.rankings.feather'
]]

motif_annotations = 'motifs-v10nr_clust-nr.hgnc-m0.001-o0.0.tbl'

# Build co-expression modules as Regulon objects. prune2df reads module.transcription_factor,
# which a bare GeneSignature lacks (AttributeError); modules_from_adjacencies applies pySCENIC's
# standard top-target/importance thresholds and returns the Regulon objects prune2df expects.
modules = list(modules_from_adjacencies(adjacencies, expr_matrix))

# Prune modules using motif enrichment
# NES threshold 3.0 (default); rank_threshold=5000 matches the CLI (prune2df default is 1500).
df_motifs = prune2df(dbs, modules, motif_annotations, rank_threshold=5000, num_workers=8)
regulons = df2regulons(df_motifs)

print(f'Discovered {len(regulons)} regulons')
```

### Step 3: AUCell Activity Scoring

```python
from pyscenic.aucell import aucell

auc_matrix = aucell(expr_matrix, regulons, num_workers=8)

adata.obsm['X_aucell'] = auc_matrix.loc[adata.obs_names].values
adata.uns['regulon_names'] = [r.name for r in regulons]
```

### QC Checkpoint: GRN Inference

```python
def validate_grn(regulons, auc_matrix, adata, cell_type_key='cell_type'):
    '''
    QC gates after GRN inference.
    - 50-500 regulons is typical range
    - Known lineage TFs should appear (e.g., PAX6 in neurons, GATA1 in erythroid)
    - AUCell scores should separate known cell types
    '''
    n_regulons = len(regulons)
    regulon_names = [r.name for r in regulons]

    # Gate 1: Regulon count
    if n_regulons < 50:
        print(f'WARNING: Only {n_regulons} regulons. Check TF list or lower NES threshold.')
    elif n_regulons > 500:
        print(f'WARNING: {n_regulons} regulons found. Consider stricter pruning.')
    else:
        print(f'OK: {n_regulons} regulons in expected range (50-500)')

    # Gate 2: Known TFs present
    known_tfs = ['PAX6', 'SOX2', 'GATA1', 'SPI1', 'FOXP3', 'TBX21', 'EBF1']
    # df2regulons names regulons 'PAX6(+)' / 'PAX6(-)'; strip the suffix or this gate never fires
    regulon_bases = {name.split('(')[0] for name in regulon_names}
    found = [tf for tf in known_tfs if tf in regulon_bases]
    print(f'Known lineage TFs found: {found}')

    # Gate 3: AUCell separates cell types
    import scipy.stats as stats
    cell_types = adata.obs[cell_type_key].unique()
    if len(cell_types) >= 2:
        ct1_idx = adata.obs[cell_type_key] == cell_types[0]
        ct2_idx = adata.obs[cell_type_key] == cell_types[1]
        n_differential = 0
        for i, rname in enumerate(regulon_names[:min(50, len(regulon_names))]):
            stat, pval = stats.mannwhitneyu(
                auc_matrix.values[ct1_idx, i], auc_matrix.values[ct2_idx, i]
            )
            if pval < 0.01:
                n_differential += 1
        print(f'Differentially active regulons between top 2 types: {n_differential}/50')

    return n_regulons
```

## Path B: SCENIC+ (Multiome)

### Step 1: ATAC Topic Modeling with cisTopic

```python
import pycisTopic
from pycisTopic.cistopic_class import create_cistopic_object
from pycisTopic.lda_models import run_cgs_models

# Create cisTopic object from fragments
cistopic_obj = create_cistopic_object(
    fragment_matrix=adata_atac.X.T,   # cisTopic wants regions x cells; AnnData .X is cells x regions
    cell_names=adata_atac.obs_names.tolist(),
    region_names=adata_atac.var_names.tolist()
)

# Run LDA topic modeling
# n_topics: test range around expected cell types (e.g., 2x number of clusters)
models = run_cgs_models(
    cistopic_obj,
    n_topics=[10, 20, 30, 40, 50],
    n_cpu=8, n_iter=300, random_state=42
)

# evaluate_models plots the model-selection metrics; read the elbow and pass that topic COUNT
# as select_model (an int, not True -- True==1 would select a non-existent 1-topic model).
from pycisTopic.lda_models import evaluate_models
model = evaluate_models(models, select_model=40, return_model=True)
cistopic_obj.add_LDA_model(model)
```

### Step 2: Enhancer-TF Mapping

```python
import pyranges as pr
from pycistarget.utils import region_names_to_coordinates
from pycistarget.motif_enrichment_cistarget import run_cistarget
from pycisTopic.topic_binarization import binarize_topics

region_bin = binarize_topics(cistopic_obj, method='otsu')   # dict of DataFrames keyed by topic (region names in the index)

# run_cistarget needs a dict of pyranges.PyRanges, not the raw binarized DataFrames.
region_sets = {topic: pr.PyRanges(region_names_to_coordinates(region_bin[topic].index.tolist()))
               for topic in region_bin}

# Run motif enrichment on accessible regions. The first arg is the cisTarget ranking DB: pass the
# feather path and run_cistarget instantiates cisTargetDatabase itself. Prebuilt DBs at
# https://resources.aertslab.org/cistarget/ . The parameter is spelled `specie`, not `species`.
CTX_DB = '/path/to/hg38_screen_v10_clust.regions_vs_motifs.rankings.feather'
cistarget_results = run_cistarget(
    CTX_DB,
    region_sets=region_sets,
    specie='homo_sapiens',
    auc_threshold=0.005,
    nes_threshold=3.0,
    rank_threshold=0.05,
    n_cpu=8
)
```

### Step 3: eGRN Construction

**Goal:** Assemble eRegulons (TF -> enhancer -> gene triplets) from the multiome data.

**Approach:** Current SCENIC+ runs topic modeling, motif enrichment, and eGRN construction through one Snakemake pipeline; the deprecated manual `create_SCENICPLUS_object`/`build_grn` API (and pre-2024 tutorials) should not be used. See gene-regulatory-networks/multiomics-grn for the full pipeline and the peak-to-gene caveats.

```bash
# Scaffold, edit the config (point at fragments, scRNA AnnData, cell-type labels, databases),
# then run from inside the Snakemake directory.
scenicplus init_snakemake --out_dir scenicplus_run
# edit scenicplus_run/Snakemake/config/config.yaml
cd scenicplus_run/Snakemake && snakemake --cores 16
```

```python
# Read the resulting direct (high-confidence) eRegulon table (filename is config-/version-
# dependent, so resolve it by glob).
import glob, pandas as pd
eregulons = pd.read_csv(glob.glob('scenicplus_run/**/eRegulon*direct*.tsv', recursive=True)[0], sep='\t')
print(f'eRegulons: {eregulons["TF"].nunique()} enhancer-driven regulators')
```

## CellOracle Perturbation Simulation

**Goal:** Predict the direction cells move under a TF knockout, as a hypothesis (direction, not calibrated magnitude).

**Approach:** CellOracle needs a base GRN (a TF-target scaffold from motif scanning of accessible regions, not the pySCENIC adjacencies), then learns per-cluster weights, propagates a forced expression shift, and projects it onto the cell-state graph. See gene-regulatory-networks/perturbation-simulation for the base-GRN construction and the local-linear / direction-only caveats.

```python
import celloracle as co
import numpy as np

oracle = co.Oracle()
oracle.import_anndata_as_raw_count(adata=adata, cluster_column_name='cell_type',
                                   embedding_name='X_umap')

# Base GRN = motif-scanned accessible regions (preferred) or a prebuilt CellOracle base GRN;
# this is NOT the pySCENIC adjacencies. See multiomics-grn / perturbation-simulation.
base_grn = co.data.load_human_promoter_base_GRN()   # `version` must match the genome build
oracle.import_TF_data(TF_info_matrix=base_grn)

oracle.perform_PCA()
k = int(0.025 * oracle.adata.n_obs)
oracle.knn_imputation(n_pca_dims=50, k=k, balanced=True, b_sight=k * 8, b_maxl=k * 4)

# Learn context-specific weights, then fit the simulation GRN.
links = oracle.get_links(cluster_name_for_GRN_unit='cell_type', alpha=10)
links.filter_links(p=0.001, weight='coef_abs', threshold_number=2000)
oracle.get_cluster_specific_TFdict_from_Links(links_object=links)
oracle.fit_GRN_for_simulation(alpha=10, use_cluster_specific_TFdict=True)

# Simulate TF knockout (0.0) and project the shift onto the embedding.
oracle.simulate_shift(perturb_condition={'MYC': 0.0}, n_propagation=3)
oracle.estimate_transition_prob(n_neighbors=200, knn_random=True, sampled_fraction=1)
oracle.calculate_embedding_shift(sigma_corr=0.05)
shift = np.sqrt((oracle.delta_embedding ** 2).sum(axis=1))
```

### QC Checkpoint: Perturbation

```python
def validate_perturbation(oracle, perturbed_tf, expected_affected_cluster=None):
    '''
    QC gate: perturbation shifts should match known biology.
    - Transition probabilities should show directional shift
    - If expected_affected_cluster known, check it shows largest change
    '''
    import numpy as np, pandas as pd
    # Shift magnitude per cell from the simulated embedding shift (delta_embedding).
    shift = np.sqrt((oracle.delta_embedding ** 2).sum(axis=1))
    # observed=True: cell_type is categorical, and the default retains filtered-out categories as NaN rows.
    # Sort here, not at print time: the gate below reads index[:3], which is category order until sorted.
    mean_shift = pd.Series(shift, index=oracle.adata.obs_names).groupby(
        oracle.adata.obs['cell_type'].values, observed=True).mean().sort_values(ascending=False)

    print(f'Mean shift magnitude by cell type after {perturbed_tf} KO:')
    print(mean_shift)

    if expected_affected_cluster:
        if expected_affected_cluster in mean_shift.index[:3]:
            print(f'OK: {expected_affected_cluster} among top affected clusters')
        else:
            print(f'WARNING: {expected_affected_cluster} not among top affected')

    return mean_shift
```

## Complete Pipeline Script

```python
import scanpy as sc
import pandas as pd
from arboreto.algo import grnboost2
from pyscenic.prune import prune2df, df2regulons
from pyscenic.aucell import aucell
from pyscenic.utils import modules_from_adjacencies
from ctxcore.rnkdb import FeatherRankingDatabase

def run_scenic_pipeline(adata_path, tf_list_path, db_paths, motif_annotations_path, output_prefix):
    '''Run complete pySCENIC pipeline.'''
    adata = sc.read_h5ad(adata_path)

    expr_matrix = pd.DataFrame(
        adata.raw.X.toarray() if hasattr(adata.raw.X, 'toarray') else adata.raw.X,
        index=adata.obs_names, columns=adata.raw.var_names
    )

    tf_names = pd.read_csv(tf_list_path, header=None)[0].tolist()
    tf_names = [tf for tf in tf_names if tf in expr_matrix.columns]

    print(f'Step 1: GRN inference with {len(tf_names)} TFs')
    adjacencies = grnboost2(expr_matrix, tf_names=tf_names, seed=42, verbose=True)

    print('Step 2: Regulon pruning')
    dbs = [FeatherRankingDatabase(db, name=os.path.splitext(os.path.basename(db))[0]) for db in db_paths]
    modules = list(modules_from_adjacencies(adjacencies, expr_matrix))
    df_motifs = prune2df(dbs, modules, motif_annotations_path, rank_threshold=5000, num_workers=8)
    regulons = df2regulons(df_motifs)
    print(f'Discovered {len(regulons)} regulons')

    print('Step 3: AUCell scoring')
    auc_matrix = aucell(expr_matrix, regulons, num_workers=8)
    adata.obsm['X_aucell'] = auc_matrix.loc[adata.obs_names].values
    adata.uns['regulon_names'] = [r.name for r in regulons]

    adata.write(f'{output_prefix}_scenic.h5ad')
    auc_matrix.to_csv(f'{output_prefix}_aucell.csv')

    print(f'Pipeline complete: {len(regulons)} regulons, AUCell matrix saved')
    return adata, regulons, auc_matrix
```

## Parameter Recommendations

| Step | Parameter | Recommendation |
|------|-----------|----------------|
| GRNBoost2 | min_targets | 10 (minimum targets per TF module) |
| RcisTarget | NES threshold | 3.0 (standard), 2.5 (permissive) |
| RcisTarget | databases | Use both 500bp and 10kbp upstream databases |
| AUCell | auc_threshold | 0.05 (fraction of ranked genes) |
| cisTopic | n_topics | Test 2x expected cell types |
| CellOracle | n_propagation | 3 (default signal propagation steps) |
| CellOracle | k (imputation) | int(0.025 * n_cells) (CellOracle tutorial rule; ~1250 at 50k cells) |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Near-empty regulons | Species/namespace/DB-vintage mismatch across TF-list, ranking DB, motif2TF | Pin all three to the SAME species + assembly + collection vintage |
| "Hybrid-state regulator" artifact | Ran GRN on a doublet-contaminated or un-integrated object | Infer on cleaned, doublet-free, batch-controlled cells; run SCENIC once on the integrated object |
| Inflated adjacencies / everything correlates | Inferred on imputed/smoothed counts | Use RAW counts; imputation only inside CellOracle's simulation scope |
| Regulon "validated" by TF-expression correlation | AUCell activity <-> TF mRNA circularity | Validate with an orthogonal modality (perturbation/ChIP), not the TF's own mRNA |
| ctx step returns empty | Missing/mismatched motif2TF annotation (most common) | Confirm the `.tbl` matches the DB vintage + species |
| SCENIC+ peaks miss rare types | Called peaks before/without cell-type labels | Label cells first; pycisTopic calls per-celltype pseudobulk peaks |
| Perturbation magnitudes reported as quantitative | Over-read the direction-only local model | Report direction + a baseline; never a quantitative KO magnitude |
| Modules called "regulons" without directionality | Skipped the cisTarget ctx pruning step | Run ctx; co-expression modules become regulons only after motif pruning |
| < 50 regulons / > 500 regulons | Strict pruning-wrong TF list / permissive thresholds | Lower NES to 2.5 (verify species) / raise NES to 3.5 |
| GRNBoost2 hangs or memory error | arboreto dask backend / large dataset | Use bundled multiprocessing; subsample to ~50k cells for GRNBoost2 |

## References

- Van de Sande B, Flerin C, Davie K, et al (2020) A scalable SCENIC workflow for single-cell gene regulatory network analysis. *Nature Protocols* 15:2247-2276. DOI 10.1038/s41596-020-0336-2. (pySCENIC 3-step; multi-run stability.)
- Bravo González-Blas C, De Winter S, Hulselmans G, et al (2023) SCENIC+: single-cell multiomic inference of enhancers and gene regulatory networks. *Nature Methods* 20:1355-1367. DOI 10.1038/s41592-023-01938-4. (eRegulons; needs paired multiome + cell-type labels before peak calling.)
- Kamimoto K, Stringa B, Hoffmann CM, et al (2023) Dissecting cell identity via network inference and in silico gene perturbation. *Nature* 614:742-751. DOI 10.1038/s41586-022-05688-9. (CellOracle; direction-only in-silico perturbation.)

## Related Skills

- gene-regulatory-networks/scenic-regulons - pySCENIC implementation details
- gene-regulatory-networks/multiomics-grn - SCENIC+ enhancer-driven GRNs
- gene-regulatory-networks/perturbation-simulation - CellOracle details
- single-cell/clustering - Upstream cell type annotation
- single-cell/preprocessing - QC and normalization before GRN inference
- atac-seq/single-cell-atac - scATAC preprocessing for SCENIC+ Multiome input
- atac-seq/co-accessibility - Cicero / SCENIC+ cis-regulatory connections
- atac-seq/enhancer-gene-linking - ABC / ENCODE-rE2G enhancer-gene mapping
- atac-seq/motif-deviation - chromVAR for TF motif accessibility
- workflows/scrnaseq-pipeline - Upstream: provides the cleaned, annotated RNA object for Path A (pySCENIC)
- workflows/multiome-pipeline - Upstream: provides the paired RNA+ATAC object for Path B (SCENIC+)
<!-- END FILE: workflows/grn-pipeline/SKILL.md -->

## 子目录：workflows/gwas-pipeline

<!-- BEGIN FILE: workflows/gwas-pipeline/SKILL.md -->
---
name: bio-workflows-gwas-pipeline
description: Orchestrates the GWAS pipeline from genotypes to association results, chaining PLINK2 QC (variant-then-sample missingness, controls-only HWE, KING relatedness), panel harmonization + joint phasing/imputation to dosages, long-range-LD-excluded PCA, and an engine chosen by sample structure (PLINK2-GLM / regenie / SAIGE / BOLT-LMM), with LDSC-intercept diagnostics. Use when committing the genome build + ancestry-matched imputation panel once (ancestry match > panel size), running the strand/allele harmonization gate (drop intermediate-frequency palindromes), imputing cases+controls TOGETHER on dosages, excluding long-range-LD regions before PCA, choosing an LMM when relatedness/structure is present (PCs cannot remove a covariance), or separating polygenicity from confounding via the LDSC intercept. Hands mechanism to the population-genetics and phasing-imputation component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: PLINK2
workflow: true
depends_on:
  - population-genetics/plink-basics
  - phasing-imputation/reference-panels
  - phasing-imputation/haplotype-phasing
  - phasing-imputation/genotype-imputation
  - phasing-imputation/imputation-qc
  - population-genetics/population-structure
  - population-genetics/association-testing
  - population-genetics/rare-variant-association
  - population-genetics/linkage-disequilibrium
qc_checkpoints:
  - after_qc: "Sample/variant call rates >95%, HWE p>1e-6"
  - after_imputation: "INFO/R2 or DR2 filtered (MAF-stratified), cases+controls imputed together, dosages carried forward"
  - after_structure: "No population stratification bias"
  - after_association: "Lambda ~1.0, expected QQ plot"
---

## Version Compatibility

Reference examples tested with: PLINK 2.0 (alpha 5+), regenie 3.4+, SAIGE 1.3+, Eagle 2.4+ / SHAPEIT5, Minimac4 / Beagle 5.4, bcftools 1.19+, LDSC 1.0, qqman 0.1.9+, ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: regenie/SAIGE run a two-step design (step 1 whole-genome ridge / null GLMM on LD-pruned common markers; step 2 tests the imputed set with LOCO) — step-1 and step-2 sample IDs + variance-ratio file MUST match or calibration silently fails. Binary PLINK2 `--glm` defaults to `firth-fallback` (output `.glm.logistic.hybrid`). Sequencing/WGS and non-EUR LD shift the genome-wide threshold off the 5e-8 EUR-array folklore. Confirm in-tool before quoting.

# GWAS Pipeline

**"Run a GWAS from my genotype data"** -> Orchestrate sample/variant QC (PLINK2), population stratification (PCA), association testing (linear/logistic regression), multiple testing correction, and Manhattan/QQ plot visualization.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

A GWAS result is decided at four seams, not inside the association test.

1. **The genome build + ancestry-matched imputation panel is a made-once commitment.** The panel fixes what can be imputed (HRC MAF floor ~5e-4; TOPMed imputes far rarer) AND the build (HRC/1000G-P3 are GRCh37; TOPMed/1000G-NYGC are GRCh38). Ancestry match > panel size: a bigger ancestry-mismatched panel imputes WORSE because there are no matching haplotypes to copy.
2. **Strand/allele harmonization is a made-once GATE, and the silent corruptor.** Align every study variant's alleles to the panel REF/ALT, fix strand, and DROP unresolvable palindromes (A/T, C/G at MAF>0.4). A flipped palindrome or a build mismatch flips BETA and cancels/manufactures signal WITHOUT erroring — caught only on the AF-concordance plot (points on the y=1-x anti-diagonal), not by a crash.
3. **QC runs before association and in a defensible internal order; the engine is chosen by structure, not convenience.** Variant missingness before sample missingness; HWE in CONTROLS only (a true non-additive risk variant deviates in cases); impute cases+controls TOGETHER; exclude long-range-LD regions before PCA. PC-covariate GLM is valid only for unrelated, continuous-ancestry cohorts — relatedness/structure needs an LMM (regenie/SAIGE/BOLT) with LOCO, because PCs remove a mean shift, not a covariance.
4. **Refuse the bare lambda.** lambda_GC alone cannot separate polygenicity from confounding — read it WITH the LDSC intercept (~1 = polygenic, fine; >1 = confounding). Do not reflexively genomic-control (it over-corrects true signal). Filter INFO/R2 MAF-stratified (a flat cutoff is a hidden rare-variant filter).

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Genome build + imputation panel (ancestry-matched) | What can be imputed + the build; ancestry mismatch imputes worse regardless of size |
| Strand/allele harmonization | A flipped palindrome / build mismatch flips BETA silently; drop MAF>0.4 palindromes |
| Ancestry/LD reference for structure | Flows into PCA and (if LMM) the GRM; must match the cohort |
| Association engine (by structure) | PC-GLM (unrelated) vs LMM+LOCO (related/structured); SPA/Firth for imbalance/low MAC |

## Workflow Overview

```
VCF/PLINK files
    |
    v
[1. QC Filtering] ------> Sample and variant QC
    |
    v
[2. Phase + Impute] ----> Align to panel, phase, impute to dosages, filter by R2 (-> phasing-imputation)
    |
    v
[3. LD Pruning] --------> Independent variants for PCA
    |
    v
[4. Population Structure] --> PCA for covariates
    |
    v
[5. Association Testing] --> Logistic/linear regression on dosages
    |
    v
[6. Results] -----------> Manhattan plot, QQ plot
    |
    v
Significant associations
```

## Step 1: Data Import and QC

### Convert VCF to PLINK

```bash
# VCF to PLINK binary format
plink2 --vcf input.vcf.gz \
    --pheno phenotypes.txt \
    --make-bed \
    --out study   # load --pheno at conversion so PHENO1 is in the .fam for the controls-only HWE gate below
```

QC order is critical (-> population-genetics/plink-basics): variant missingness runs FIRST, in its own invocation, so a sample is not dropped for missingness driven by variants slated for removal.

### Variant call-rate (first)

```bash
plink2 --bfile study --missing --out study_stats
plink2 --bfile study --geno 0.05 --make-bed --out study_var_qc   # variant missingness BEFORE sample missingness
```

### Sample QC

```bash
# Sample missingness AFTER variant missingness.
plink2 --bfile study_var_qc --mind 0.05 --make-bed --out study_sample_qc

# Sex check: split the pseudoautosomal region first or male PAR het reads as a sex error (see plink-basics).
plink2 --bfile study_sample_qc --split-par hg38 --check-sex --out study_sex_check

# KING-robust relatedness - structure-robust and IBD-free (this is the point of KING; no --genome needed).
plink2 --bfile study_sample_qc --king-cutoff 0.0884 --make-bed --out study_unrelated
```

### Variant QC: MAF and controls-only HWE

```bash
# Controls-only HWE with mid-p. plink2 is NOT controls-only by default, so gate to controls explicitly:
# a true risk variant depletes heterozygotes in cases and would fail a case-inclusive HWE test (see plink-basics).
plink2 --bfile study_unrelated --keep-if "PHENO1 == control" --hwe 1e-6 midp --write-snplist --out hwe_pass
plink2 --bfile study_unrelated --maf 0.01 --extract hwe_pass.snplist --make-bed --out study_qc
plink2 --bfile study_qc --freq --out study_qc
```

**QC Checkpoint:**
- Variant call rate >95% (applied before sample missingness)
- Sample call rate >95%
- MAF >1%
- HWE applied to controls only with mid-p (p>1e-6)

## Step 2: Phasing and Imputation

Most GWAS impute the QC'd array genotypes up to a dense reference panel before association, to increase variant density and harmonize across platforms and studies. This stage is owned by the phasing-imputation skills; the workflow only orchestrates the handoff. The decisions that matter here, in order:

1. **Select and prepare the panel** (-> phasing-imputation/reference-panels). Match the panel ancestry to the cohort (TOPMed for diverse/admixed, HRC or 1000G for European, HGDP+1kGP for diverse-and-downloadable), reconcile genome build, and run the strand/allele harmonization check; a flipped palindromic SNP or build mismatch corrupts results without erroring.
2. **Phase, then impute** (-> phasing-imputation/haplotype-phasing, phasing-imputation/genotype-imputation). Pre-phase the QC'd VCF (Eagle2/SHAPEIT5) and impute against the panel per chromosome (Beagle/Minimac4/IMPUTE5), or upload to the Michigan/TOPMed server for controlled-access panels. Impute cases and controls TOGETHER; separate imputation manufactures false associations. The output carries dosages (DS), not hard calls.
3. **Filter by quality** (-> phasing-imputation/imputation-qc). Drop variants below an INFO/R2/DR2 cutoff paired with a MAF floor, MAF-stratified, because a flat cutoff is a hidden rare-variant filter. Carry dosages forward.

**Goal:** Increase variant density and harmonize across platforms by imputing the QC'd genotypes against a dense ancestry-matched panel, carrying dosages (not hard calls) into association.

**Approach:** Export the QC'd genotypes to VCF, hand off to the phasing-imputation skills for strand/build harmonization, phasing, and per-chromosome imputation (cases and controls together), then filter on the engine's quality field plus a MAF floor.

```bash
# Convert QC'd PLINK back to VCF, align to the panel, phase + impute (see phasing-imputation skills for the full commands)
plink2 --bfile study_qc --export vcf bgz --out study_qc
# ... reference-panels: strand/build harmonization; haplotype-phasing: phase; genotype-imputation: impute to dosages ...
# Post-imputation quality filter on the engine's field (DR2 Beagle / R2 Minimac), with a MAF floor
bcftools view -e 'INFO/DR2<0.3 || INFO/AF<0.01 || INFO/AF>0.99' imputed.vcf.gz -Oz -o imputed.qc.vcf.gz
```

**QC Checkpoint:** cases and controls imputed together; INFO/R2 filtered (MAF-stratified) with a MAF floor; dosages (DS), not hard calls, carried into association.

## Step 3: LD Pruning for PCA

```bash
# Exclude long-range-LD regions and inversions FIRST (MHC, 8p23.1, 17q21.31, LCT) - their internal r2 is
# high and real, so a window prune keeps them and a PC then tracks the inversion (-> population-structure).
plink2 --bfile study_qc --exclude range longrange_ld.txt --make-bed --out study_noLR

# Identify independent variants (r2 0.1 matches the linkage-disequilibrium / population-structure default).
plink2 --bfile study_noLR --indep-pairwise 50 5 0.1 --out pruned
plink2 --bfile study_noLR --extract pruned.prune.in --make-bed --out study_pruned
```

## Step 4: Population Structure (PCA)

```bash
# Calculate principal components
plink2 --bfile study_pruned \
    --pca 10 \
    --out study_pca

# The eigenvec file contains PCs for use as covariates
```

### Visualize PCA

```r
library(ggplot2)

# Load PCA results
pca <- read.table('study_pca.eigenvec', header = FALSE)
colnames(pca) <- c('FID', 'IID', paste0('PC', 1:10))

# Load phenotype for coloring
pheno <- read.table('phenotypes.txt', header = TRUE)
pca <- merge(pca, pheno, by = c('FID', 'IID'))

# Plot
ggplot(pca, aes(x = PC1, y = PC2, color = as.factor(PHENO))) +
    geom_point(alpha = 0.5) +
    labs(title = 'PCA of Study Samples', color = 'Phenotype') +
    theme_minimal()
ggsave('pca_plot.pdf', width = 8, height = 6)
```

## Step 5: Association Testing

Run the association on imputed DOSAGES, not hard calls, so the imputation uncertainty is propagated (PLINK2 reads dosages with `--vcf imputed.qc.vcf.gz dosage=DS`, or use a `.pgen` built from dosages). The examples below use the QC'd best-guess genotypes for brevity; substitute the dosage input for an imputed analysis.

The engine choice is set by sample structure, not convenience (-> population-genetics/association-testing). PC-covariate GLM (below) is valid only for unrelated samples whose confounding is continuous ancestry; any related, family-based, or fine-scale-structured cohort needs a linear mixed model with leave-one-chromosome-out, because PCs cannot remove a covariance structure.

| Situation | Engine | Hand off to |
|-----------|--------|-------------|
| Unrelated, continuous-ancestry confounding only | PLINK2 `--glm` (PC covariates) | population-genetics/association-testing |
| Relatedness / family / fine-scale structure | LMM (regenie / SAIGE / BOLT-LMM) with LOCO | population-genetics/association-testing |
| Biobank binary, case:control worse than ~1:10 or low MAC | SAIGE (SPA) or regenie (`--firth`/`--spa`) | population-genetics/association-testing |
| Rare-variant, aggregate by gene | burden/SKAT/SKAT-O via SAIGE-GENE+/regenie | population-genetics/rare-variant-association |
| Threshold | 5e-8 is EUR-common-array folklore; ~1e-8-3e-8 (African LD), ~5e-9 (WGS/rare) | population-genetics/association-testing |

### Case-Control (Binary Trait)

```bash
# Logistic regression with PCA covariates
plink2 --bfile study_qc \
    --pheno phenotypes.txt \
    --covar study_pca.eigenvec \
    --covar-col-nums 3-12 \
    --glm firth-fallback hide-covar \
    --out gwas_results

# Binary --glm defaults to firth-fallback -> results in gwas_results.PHENO.glm.logistic.hybrid
```

### Quantitative Trait

```bash
# Linear regression
plink2 --bfile study_qc \
    --pheno phenotypes.txt \
    --pheno-name BMI \
    --covar study_pca.eigenvec \
    --covar-col-nums 3-12 \
    --glm hide-covar \
    --out gwas_bmi

# Results in gwas_bmi.BMI.glm.linear
```

### With Additional Covariates

```bash
# Include age, sex, and PCs
plink2 --bfile study_qc \
    --pheno phenotypes.txt \
    --covar covariates.txt \
    --covar-name AGE,SEX,PC1-PC10 \
    --glm hide-covar \
    --out gwas_adjusted
```

## Step 6: Results Visualization

### Manhattan Plot

```r
library(qqman)

# Load results
# comment.char='' is REQUIRED: PLINK2's header starts with '#CHROM', which the default
# comment.char='#' would eat (dropping the header and the first variant).
results <- read.table('gwas_results.PHENO.glm.logistic.hybrid', header = TRUE, comment.char = '')
results <- results[!is.na(results$P),]
# qqman's manhattan needs a NUMERIC chromosome: recode X/Y/MT (e.g. X->23) or filter to autosomes first.
results$X.CHROM <- suppressWarnings(as.integer(sub('^chr', '', results$X.CHROM)))
results <- results[!is.na(results$X.CHROM),]

# Manhattan plot
png('manhattan.png', width = 1200, height = 600)
manhattan(results, chr = 'X.CHROM', bp = 'POS', snp = 'ID', p = 'P',
          suggestiveline = -log10(1e-5), genomewideline = -log10(5e-8))
dev.off()

# QQ plot
png('qq_plot.png', width = 600, height = 600)
qq(results$P)
dev.off()
```

### Calculate Genomic Inflation

```r
# Lambda (genomic inflation factor)
chisq <- qchisq(1 - results$P, 1)
lambda <- median(chisq) / qchisq(0.5, 1)
cat('Lambda:', round(lambda, 3), '\n')
# Lambda should be close to 1.0 (1.0-1.1 acceptable)
```

### Extract Significant Hits

```bash
# Select the P column by header, not a fixed index (firth-fallback adds columns and shifts positions).
awk 'NR==1{for(i=1;i<=NF;i++) if($i=="P") p=i; print; next} $p<5e-8' \
    gwas_results.PHENO.glm.logistic.hybrid > significant_hits.txt
awk 'NR==1{for(i=1;i<=NF;i++) if($i=="P") p=i; print; next} $p<1e-5' \
    gwas_results.PHENO.glm.logistic.hybrid > suggestive_hits.txt
```

## Parameter Recommendations

| Step | Parameter | Value |
|------|-----------|-------|
| Sample QC | --mind | 0.05 |
| Variant QC | --geno | 0.05 |
| Variant QC | --maf | 0.01 |
| Variant QC | --hwe | 1e-6 |
| LD pruning | --indep-pairwise | 50 5 0.1 (after long-range-LD exclusion) |
| PCA | --pca | 10 |
| Significance | p-value | 5e-8 |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| "0 variants matched" the panel | chr-naming (`1` vs `chr1`) or build mismatch | `bcftools annotate --rename-chrs`; match study build to the panel before any check |
| Flipped BETA / cancelled or manufactured signal | Strand-flip / allele-swap at intermediate-frequency palindromes | Run the Rayner check + AF-concordance FreqPlot; drop MAF>0.4 palindromes |
| Case-control association that is imputation artifact | Cases and controls imputed SEPARATELY | Impute jointly; separate imputation makes error differ between arms |
| Disproportionate rare-variant loss | Flat INFO/R2 cutoff | MAF-stratified R2 thresholds + a MAF floor |
| A PC tracks an inversion, not ancestry | Long-range-LD region kept before pruning | Exclude MHC/8p23.1/17q21.31/LCT BEFORE `--indep-pairwise` |
| Elevated lambda | Polygenicity OR confounding (lambda alone cannot separate) | Read the LDSC intercept (~1 = polygenic, fine); do NOT reflexively genomic-control |
| Residual structure after PCs | Relatedness/fine-scale structure (a covariance PCs cannot remove) | LMM (regenie/SAIGE/BOLT) with LOCO |
| Inflation at low MAC / extreme case:control ratio | Score/Wald anti-conservative | SPA (SAIGE) or Firth |
| chrX mis-analyzed | chrX coded as an autosome | split-PAR, sex covariate, explicit X handling |

## References

- McCarthy S, Das S, Kretzschmar W, et al (2016) A reference panel of 64,976 haplotypes for genotype imputation. *Nature Genetics* 48:1279-1283. DOI 10.1038/ng.3643. (HRC.)
- Taliun D, Harris DN, Kessler MD, et al (2021) Sequencing of 53,831 diverse genomes from the NHLBI TOPMed Program. *Nature* 590:290-299. DOI 10.1038/s41586-021-03205-y. (TOPMed diversity.)
- Sheng X, Xia L, Cahoon JL, et al (2023) Inverted genomic regions between reference genome builds. *HGG Advances* 4:100159. DOI 10.1016/j.xhgg.2022.100159. (liftover/BBIS strand danger.)
- Mbatchou J, Barnard L, Backman J, et al (2021) Computationally efficient whole-genome regression for quantitative and binary traits. *Nature Genetics* 53:1097-1103. DOI 10.1038/s41588-021-00870-7. (regenie.)

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

INPUT_VCF="genotypes.vcf.gz"
PHENO="phenotypes.txt"
OUTDIR="gwas_results"

mkdir -p ${OUTDIR}

# Step 1: Convert, then QC in order (variant missingness, then sample, then MAF + controls-only HWE).
plink2 --vcf ${INPUT_VCF} --pheno ${PHENO} --make-bed --out ${OUTDIR}/raw   # --pheno embeds PHENO1 in .fam for the controls-only HWE gate
plink2 --bfile ${OUTDIR}/raw --geno 0.05 --make-bed --out ${OUTDIR}/var_qc
plink2 --bfile ${OUTDIR}/var_qc --mind 0.05 --king-cutoff 0.0884 --make-bed --out ${OUTDIR}/samp_qc
plink2 --bfile ${OUTDIR}/samp_qc --keep-if "PHENO1 == control" --hwe 1e-6 midp \
    --write-snplist --out ${OUTDIR}/hwe_pass
plink2 --bfile ${OUTDIR}/samp_qc --maf 0.01 --extract ${OUTDIR}/hwe_pass.snplist \
    --make-bed --out ${OUTDIR}/qc

# Step 2: LD pruning (exclude long-range-LD regions first; r2 0.1)
plink2 --bfile ${OUTDIR}/qc --exclude range longrange_ld.txt --make-bed --out ${OUTDIR}/noLR
plink2 --bfile ${OUTDIR}/noLR --indep-pairwise 50 5 0.1 --out ${OUTDIR}/pruned
plink2 --bfile ${OUTDIR}/noLR --extract ${OUTDIR}/pruned.prune.in \
    --make-bed --out ${OUTDIR}/pruned_set

# Step 3: PCA
plink2 --bfile ${OUTDIR}/pruned_set --pca 10 --out ${OUTDIR}/pca

# Step 4: Association on the full QC'd set (binary --glm defaults to firth-fallback -> .glm.logistic.hybrid)
plink2 --bfile ${OUTDIR}/qc --pheno ${PHENO} \
    --covar ${OUTDIR}/pca.eigenvec --covar-col-nums 3-12 \
    --glm firth-fallback hide-covar --out ${OUTDIR}/gwas

echo "=== GWAS Complete ==="
echo "Results: ${OUTDIR}/gwas.*.glm.*"
```

## Related Skills

- database-access/ensembl-rest - VEP annotation for top GWAS variants (per-variant); local VEP for >1K
- database-access/biomart-queries - Bulk SNP-to-gene mapping via BioMart
- population-genetics/plink-basics - PLINK file formats and commands
- phasing-imputation/reference-panels - Select and prepare the reference panel; strand/build harmonization
- phasing-imputation/haplotype-phasing - Pre-phase the QC'd genotypes before imputation
- phasing-imputation/genotype-imputation - Impute to dosages against the panel
- phasing-imputation/imputation-qc - Filter imputed variants by R2 and MAF before association
- population-genetics/population-structure - PCA and admixture
- population-genetics/association-testing - Single-variant models (PC-GLM vs LMM, SPA/Firth) on dosages
- population-genetics/rare-variant-association - Gene-based burden/SKAT/SKAT-O for rare variants
- population-genetics/linkage-disequilibrium - LD concepts
- workflows/causal-genomics-pipeline - Downstream: the emitted sumstats (CHR/POS/EA/OA/EAF/BETA/SE/P/N, build documented) are its input contract
<!-- END FILE: workflows/gwas-pipeline/SKILL.md -->

## 子目录：workflows/hic-pipeline

<!-- BEGIN FILE: workflows/hic-pipeline/SKILL.md -->
---
name: bio-workflows-hic-pipeline
description: End-to-end Hi-C analysis workflow from FASTQ to compartments, TADs, and loops, with the decision of WHICH features the sequencing depth can support. Covers pairtools read-pair processing and library QC, cooler matrices, ICE balancing and distance-decay expected, A/B compartments, TAD boundaries, loop calling, and the routing of HiChIP/PLAC-seq/Capture Hi-C to protein-directed loop callers. Use when processing Hi-C data end to end, deciding a resolution for a given depth, or choosing between bulk-Hi-C and protein-directed loop calling.
tool_type: mixed
primary_tool: cooler
workflow: true
depends_on:
  - hi-c-analysis/contact-pairs
  - hi-c-analysis/hic-data-io
  - hi-c-analysis/matrix-operations
  - hi-c-analysis/compartment-analysis
  - hi-c-analysis/tad-detection
  - hi-c-analysis/loop-calling
  - hi-c-analysis/hic-visualization
  - hi-c-analysis/hic-differential
  - hi-c-analysis/hichip-plac-loops
qc_checkpoints:
  - after_pairs: "Long-range cis (>=20kb) fraction, not just %valid; trans is genome-size-dependent"
  - after_balance: "balance=True returns finite weights; masked bins are NaN by design"
  - after_analysis: "Eigenvector sign phased by GC; feature scale matches the resolution"
---

## Version Compatibility

Reference examples tested with: BWA-MEM2 2.2.1+, cooler 0.10+, cooltools 0.7+, bioframe 0.7+, matplotlib 3.8+, pairtools 1.1+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Hi-C Pipeline

**"Analyze my Hi-C data from FASTQ to 3D genome features"** -> Process read pairs and judge library quality, build and balance a cooler, then call ONLY the features the depth can support: compartments are cheap, TADs need moderate depth, de-novo loops need billions of contacts.

Complete workflow for Hi-C chromosome conformation capture analysis.

## The Decision That Frames the Whole Pipeline -- depth dictates the feature

Contacts scale with the SQUARE of the bin count, so the affordable resolution is set by depth, not ambition. Read `hi-c-analysis/matrix-operations` for the budget; the rule of thumb is ~1000 contacts/bin. Compartments (100kb-1Mb) come from almost any library; TAD boundaries (10-40kb) need a moderate map; de-novo loop calling (5-10kb dots) needed ~5 billion contacts in Rao 2014. On a shallow map, do NOT de-novo call loops -- run aggregate peak analysis (APA) on known CTCF/cohesin anchors instead (`hi-c-analysis/loop-calling`).

Protein-directed assays branch here: HiChIP, PLAC-seq, and Capture Hi-C have non-uniform peak-anchored coverage, so generic dots/HiCCUPS use the wrong null. Route them to `hi-c-analysis/hichip-plac-loops` (FitHiChIP/MAPS/CHiCAGO), NOT to step 6 below.

## Workflow Overview

```
Hi-C FASTQ files
    |
    v
[1. Alignment & Pairs] --> bwa-mem2 -SP5M + pairtools (parse/sort/dedup/split)
    |                       QC: long-range cis fraction is the one-number readout
    v
[2. Matrix Generation] --> cooler cload + zoomify (sum RAW, re-balance per resolution)
    |
    v
[3. Balancing] --------> ICE (cooler balance); REQUIRED before any analysis
    |
    v
[4. Compartments 100kb] -> eigs_cis, sign-phased by GC (E1 is a choice, not an output)
    |
    v
[5. TADs 10kb] ---------> insulation score across a window sweep (boundaries, not domains)
    |
    v
[6. Loops 10kb] --------> cooltools dots IF deep; else APA on known anchors
    |
    v
Hi-C features (compartments / boundaries / loops)
```

## Step 1: Alignment and Pair Processing

**Goal:** Turn raw Hi-C FASTQ into a deduplicated, classified `.pairs` list and judge whether the library worked.

**Approach:** Align the two mates independently with `bwa-mem2 -SP5M` (proper pairing would destroy long-range contacts), then parse, sort, deduplicate, and split with pairtools, reading the long-range cis fraction as the go/no-go.

```bash
# Pass BOTH mates to ONE bwa-mem2 call. -SP5M: -S/-P make bwa treat the mates as single-end and
# skip proper-pair rescue (so long-range contacts survive), while both sides are still emitted for
# pairtools to form the pair; -5 reports the 5'-most alignment of split reads, -M flags secondaries.
bwa-mem2 mem -SP5M -t 16 reference.fa reads_R1.fastq.gz reads_R2.fastq.gz | \
    pairtools parse --min-mapq 40 --walks-policy 5unique \
    --max-inter-align-gap 30 --nproc-in 8 --nproc-out 8 \
    --chroms-path reference.genome | \
    pairtools sort --nproc 16 --tmpdir ./tmp | \
    pairtools dedup --nproc-in 8 --nproc-out 8 \
    --mark-dups --output-stats stats.txt | \
    pairtools split --nproc-in 8 --output-pairs sample.pairs.gz
```

**QC Checkpoint:** read `pairtools stats` as the go/no-go. The one-number readout is the LONG-RANGE cis fraction (>=20kb), not bare %valid: short-range cis is inflated by dangling ends and self-circles. Trans fraction is a noise floor but its acceptable value is genome-size-dependent (a human <10% threshold is meaningless for a microbe). High duplicate rate = low library complexity (not rescuable by sequencing deeper). See `hi-c-analysis/contact-pairs` for the orientation-balance QC and the Micro-C/Arima variants.

## Step 2: Generate Contact Matrix

```bash
# Create cooler file at multiple resolutions
cooler cload pairs \
    -c1 2 -p1 3 -c2 4 -p2 5 \
    reference.genome:1000 \
    sample.pairs.gz \
    sample.1000.cool

# Multi-resolution (mcool)
cooler zoomify sample.1000.cool \
    -r 1000,2000,5000,10000,25000,50000,100000,250000,500000,1000000 \
    -o sample.mcool
```

## Step 3: Normalization (ICE Balancing)

**Goal:** ICE-balance the matrix so every bin has equal marginal coverage, without letting empty/artifact bins corrupt the result.

**Approach:** Mask low-coverage and blacklist bins BEFORE balancing, then balance per resolution. ICE assumes equal visibility per bin, so an unmasked empty or repeat/blacklist bin is iteratively up-weighted into a bright stripe artifact; `mad_max` filters bins whose coverage is `mad_max` MADs below the median, and a blacklist/`--blacklist` (or pre-masking bad bins) removes known artifacts. Balancing is REQUIRED before any analysis, but it does NOT make two maps comparable across conditions — that needs depth-matching + distance-stratified normalization (hi-c-analysis/hic-differential).

```python
import cooler
import cooltools

# Mask before balancing: mad_max drops low-coverage bins that would otherwise become stripes.
# Balance EVERY resolution the downstream steps analyze -- weights are resolution-specific, and an
# unbalanced cooler has no 'weight' column, so cooltools (eigs_cis, insulation, dots) fails on it.
# Steps 4-6 below use 100kb (compartments) and 10kb (loops and insulation).
for res in (10000, 25000, 100000):
    clr = cooler.Cooler(f'sample.mcool::/resolutions/{res}')
    cooler.balance_cooler(clr, store=True, mad_max=5, ignore_diags=2, min_nnz=10)   # masked bins are NaN by design

# CLI equivalent (add --blacklist regions.bed to remove known-artifact bins first):
# for res in 10000 25000 100000; do cooler balance --mad-max 5 --ignore-diags 2 --min-nnz 10 sample.mcool::/resolutions/${res}; done
```

## Step 4: Compartment Analysis

**Goal:** Assign each genomic bin to the active (A) or inactive (B) compartment with a non-arbitrary sign.

**Approach:** At a coarse 100kb resolution, compute the cis eigenvector and orient it with a GC phasing track so positive E1 is the active compartment (the sign is arbitrary without it).

```python
import cooler
import cooltools
import bioframe
import numpy as np

# Compartments are coarse-scale: 100kb, balanced matrix
clr = cooler.Cooler('sample.mcool::/resolutions/100000')

# Phasing track is NOT optional: the eigenvector sign is arbitrary. A GC track
# (matching the cooler binning exactly) orients positive E1 to the active (A) compartment.
view_df = bioframe.make_viewframe(clr.chromsizes)
gc = bioframe.frac_gc(clr.bins()[:][['chrom', 'start', 'end']], bioframe.load_fasta('reference.fa'))

eig_values, eig_vectors = cooltools.eigs_cis(clr, gc, view_df=view_df, n_eigs=3)
compartments = eig_vectors[['chrom', 'start', 'end', 'E1']].copy()
# Masked bins have E1 = NaN; NaN > 0 is False, so guard or a bare np.where mislabels them all 'B'.
compartments['compartment'] = np.where(compartments['E1'].isna(), None, np.where(compartments['E1'] > 0, 'A', 'B'))
compartments.to_csv('compartments.tsv', sep='\t', index=False)
```

## Step 5: TAD Detection

**Goal:** Locate domain boundaries at the sub-Mb scale.

**Approach:** Compute the insulation score across a window sweep at 10kb and read the `is_boundary`/`boundary_strength` columns the function returns directly (report boundaries, not a fixed domain partition).

```python
import cooltools

# Load matrix at TAD resolution
clr = cooler.Cooler('sample.mcool::/resolutions/10000')

# Insulation across a window sweep; the function already returns boundary columns
# (is_boundary_<W>, boundary_strength_<W>) -- there is no separate find_boundaries call.
ins = cooltools.insulation(clr, window_bp=[100000, 200000, 500000])

# Boundaries at the 200kb window; keep the continuous strength (comparable across samples).
# is_boundary is NaN for bad/low-mappability bins; fillna(False) before masking or pandas raises.
boundaries = ins[ins['is_boundary_200000'].fillna(False).astype(bool)][['chrom', 'start', 'end', 'boundary_strength_200000']]
boundaries.to_csv('tad_boundaries.tsv', sep='\t', index=False)

# Alternative: use HiCExplorer
# hicFindTADs -m sample.cool --outPrefix tads --correctForMultipleTesting fdr
```

## Step 6: Loop Calling

**Goal:** Detect focal CTCF/enhancer-promoter contacts, but only when the map is deep enough to support de-novo calling.

**Approach:** Compute a distance-matched expected, then run `cooltools dots` on a deep map; on a shallow library, skip de-novo calling and run APA on known anchors instead.

```python
import cooltools

# Load high-resolution matrix
clr = cooler.Cooler('sample.mcool::/resolutions/10000')

# De-novo dot calling is only honest on a DEEP map (Rao 2014 used ~5B contacts).
# On a shallow library, skip this and run APA on known anchors (see loop-calling).
expected = cooltools.expected_cis(clr)
loops = cooltools.dots(clr, expected, max_loci_separation=2000000, nproc=4)
loops.to_csv('loops.tsv', sep='\t', index=False)

# Alternative caller (template matching): chromosight
# chromosight detect --pattern loops sample.mcool::/resolutions/10000 loops
# For HiChIP/PLAC-seq/Capture Hi-C do NOT use dots -> hi-c-analysis/hichip-plac-loops
```

## Step 7: Visualization

```python
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import cooltools.lib.plotting   # registers the 'fall' cmap; if unavailable in your stack, use 'afmhot_r'

# A square balanced map on a log scale; importing cooltools.lib.plotting registers 'fall'.
# Show O/E with a symmetric diverging cmap to see compartments/loops (see hic-visualization).
mat = clr.matrix(balance=True).fetch('chr1:50000000-60000000')
fig, ax = plt.subplots(figsize=(8, 8))
ax.matshow(mat, norm=LogNorm(vmax=mat[mat > 0].max() * 0.5), cmap='fall')
plt.savefig('hic_matrix.pdf')

# Triangle/track-stacked browser views: use pyGenomeTracks or HiCExplorer hicPlotTADs
# (data-visualization/genome-tracks), not a hand-rolled rotation.
```

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

THREADS=16
REF="reference.fa"
GENOME="reference.genome"
R1="sample_R1.fastq.gz"
R2="sample_R2.fastq.gz"
OUTDIR="hic_results"

mkdir -p ${OUTDIR}/{pairs,cool,analysis}

# Step 1: Alignment and pairs
echo "=== Alignment ==="
bwa-mem2 mem -SP5M -t ${THREADS} ${REF} ${R1} ${R2} | \
    pairtools parse --min-mapq 40 --walks-policy 5unique \
    --chroms-path ${GENOME} | \
    pairtools sort --nproc ${THREADS} --tmpdir ./tmp | \
    pairtools dedup --mark-dups --output-stats ${OUTDIR}/pairs/stats.txt | \
    pairtools split --output-pairs ${OUTDIR}/pairs/sample.pairs.gz

# Step 2: Generate matrix
echo "=== Matrix Generation ==="
cooler cload pairs -c1 2 -p1 3 -c2 4 -p2 5 \
    ${GENOME}:1000 ${OUTDIR}/pairs/sample.pairs.gz ${OUTDIR}/cool/sample.1000.cool

cooler zoomify ${OUTDIR}/cool/sample.1000.cool \
    -r 1000,5000,10000,25000,50000,100000,500000 \
    -o ${OUTDIR}/cool/sample.mcool

# Step 3: Balance
echo "=== Balancing ==="
for res in 10000 25000 100000; do
    cooler balance ${OUTDIR}/cool/sample.mcool::/resolutions/${res}
done

echo "=== Pipeline Complete ==="
echo "Run Python script for compartments, TADs, and loops"
```

## Python Analysis Script

```python
import cooler
import cooltools
import bioframe
import os

outdir = 'hic_results/analysis'
os.makedirs(outdir, exist_ok=True)

# Compartments (100kb) -- pass a GC phasing track (Step 4) so the sign is meaningful;
# eigs_cis without phasing returns an arbitrary-sign eigenvector.
print('Compartments...')
clr = cooler.Cooler('hic_results/cool/sample.mcool::/resolutions/100000')
gc = bioframe.frac_gc(clr.bins()[:][['chrom', 'start', 'end']], bioframe.load_fasta('reference.fa'))
eig_values, eig_vectors = cooltools.eigs_cis(clr, gc, n_eigs=3)
eig_vectors.to_csv(f'{outdir}/compartments.tsv', sep='\t', index=False)

# TADs (10kb)
print('TADs...')
clr = cooler.Cooler('hic_results/cool/sample.mcool::/resolutions/10000')
insulation = cooltools.insulation(clr, window_bp=[100000, 200000])
insulation.to_csv(f'{outdir}/insulation.tsv', sep='\t')

# Loops (10kb)
print('Loops...')
expected = cooltools.expected_cis(clr)
loops = cooltools.dots(clr, expected, nproc=4)
loops.to_csv(f'{outdir}/loops.tsv', sep='\t')

print(f'Results saved to {outdir}/')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Long-range contacts missing / map looks like short-range only | Mates aligned as a proper pair instead of independently | Align with `bwa-mem2 mem -SP5M` (each end separately, no proper-pair rescue) |
| Library "passed" %valid but is unusable | Judged on bare %valid; short-range cis is inflated by dangling ends/self-circles | Read the long-range cis (>=20kb) fraction as the go/no-go |
| Bright stripes/plaid artifacts after balancing | Empty/repeat/blacklist bins not masked before ICE | Mask with `mad_max`/`--blacklist`/`min_nnz` before balancing |
| A/B compartments flipped between samples | Eigenvector sign is arbitrary without phasing | Phase E1 by a GC track matching the cooler binning exactly |
| De-novo loops look sparse/noisy | Called `dots` on a shallow map | Only de-novo call on deep maps (~billions of contacts, Rao 2014); else APA on known anchors |
| Cross-condition differences dominated by depth | Compared balanced maps directly | Depth-match + distance-stratified normalize first (hi-c-analysis/hic-differential) |
| HiChIP/PLAC "loops" full of false positives | Generic dots/HiCCUPS null on peak-anchored coverage | Route to FitHiChIP/MAPS/CHiCAGO (hi-c-analysis/hichip-plac-loops) |

## References

- Rao SSP, Huntley MH, Durand NC, et al (2014) A 3D map of the human genome at kilobase resolution reveals principles of chromatin looping. *Cell* 159:1665-1680. DOI 10.1016/j.cell.2014.11.021. (depth-vs-resolution; ~5B contacts for kilobase loops.)
- Imakaev M, Fudenberg G, McCord RP, et al (2012) Iterative correction of Hi-C data reveals hallmarks of chromosome organization. *Nature Methods* 9:999-1003. DOI 10.1038/nmeth.2148. (ICE balancing.)
- Abdennur N, Mirny LA (2020) Cooler: scalable storage for Hi-C data and other genomically labeled arrays. *Bioinformatics* 36:311-316. DOI 10.1093/bioinformatics/btz540.
- Open2C, Abdennur N, Fudenberg G, et al (2024) Cooltools: enabling high-resolution Hi-C analysis in Python. *PLOS Computational Biology* 20:e1012067. DOI 10.1371/journal.pcbi.1012067.
- Open2C, Abdennur N, Fudenberg G, et al (2024) Pairtools: from sequencing data to chromosome contacts. *PLOS Computational Biology* 20:e1012164. DOI 10.1371/journal.pcbi.1012164.

## Related Skills

- hi-c-analysis/contact-pairs - Read-pair processing and the library-QC decision
- hi-c-analysis/hic-data-io - Cooler file operations and format conversion
- hi-c-analysis/matrix-operations - ICE balancing, expected/P(s), and the resolution-vs-depth budget
- hi-c-analysis/compartment-analysis - Sign-phased A/B compartments and saddle strength
- hi-c-analysis/tad-detection - Insulation-score boundaries across a window sweep
- hi-c-analysis/loop-calling - Dot calling and APA validation
- hi-c-analysis/hic-visualization - Normalization-aware contact-map plotting
- hi-c-analysis/hic-differential - Scale-matched comparison between conditions
- hi-c-analysis/hichip-plac-loops - Protein-directed loops (HiChIP/PLAC-seq/Capture Hi-C)
<!-- END FILE: workflows/hic-pipeline/SKILL.md -->

## 子目录：workflows/imc-pipeline

<!-- BEGIN FILE: workflows/imc-pipeline/SKILL.md -->
---
name: bio-workflows-imc-pipeline
description: Orchestrates imaging mass cytometry from raw MCD acquisitions to patient-level spatial analysis, chaining steinbock preprocessing, Mesmer/Cellpose segmentation, single-cell quantification, phenotyping, and squidpy spatial statistics. Use when committing the panel + segmentation frame + pixel size (every per-cell number is a mask-bounded pixel average), compensating channel spillover on PIXELS before segmentation but running REDSEA lateral-spillover on the per-cell table AFTER segmentation, using arcsinh cofactor 1 (not the suspension-CyTOF 5), and aggregating to the PATIENT before any cross-condition test (cells and ROIs from one patient are not independent replicates). Hands mechanism to the imaging-mass-cytometry component skills; not a re-teach of any single step.
tool_type: python
primary_tool: steinbock
goal_approach_exempt: true
workflow: true
depends_on:
  - imaging-mass-cytometry/data-preprocessing
  - imaging-mass-cytometry/cell-segmentation
  - imaging-mass-cytometry/phenotyping
  - imaging-mass-cytometry/spatial-analysis
  - imaging-mass-cytometry/differential-analysis
  - imaging-mass-cytometry/interactive-annotation
  - imaging-mass-cytometry/quality-metrics
---

## Version Compatibility

Reference examples tested with: Cellpose 4.0+ (cpsam model), anndata 0.10+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, scvi-tools 1.1+, squidpy 1.3+, steinbock 0.16+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Imaging Mass Cytometry Pipeline

**"Process my imaging mass cytometry data from images to spatial analysis"** -> Orchestrate image preprocessing (steinbock), cell segmentation (Cellpose), phenotyping (FlowSOM/scanpy), spatial neighborhood analysis (squidpy), and tissue community detection.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

Segmentation is the largest irreversible error source, and it is spatial: every per-cell number is a mask-bounded pixel average, so a wrong boundary fabricates cell types before any expression QC can see them. The seam ORDER — and the patient-level unit — is therefore what decides trustworthiness.

1. **The comparison frame (panel + segmentation frame + pixel size) is committed once and inherited by every per-cell number.** The summed membrane channel encodes a cell-type bias (sum BROADLY-expressed markers, or segmentation under-performs on cell types lacking a strong membrane marker); Mesmer was trained at model_mpp ~0.5 um and rescales the input to it, so passing the wrong pixel size (Mesmer's `image_mpp` defaults to None = NO rescaling, assuming the input is already at model resolution — the true pixel size must be passed explicitly; steinbock's `--pixelsize` flag wraps `image_mpp` and defaults to 1.0) rescales cells to the wrong learned size and degrades every boundary. No downstream step recovers a merged or split cell.
2. **Channel spillover is compensated on PIXELS before segmentation; lateral spillover (REDSEA) runs on the per-cell table AFTER segmentation — they are DIFFERENT problems.** Metal-isotope crosstalk is a pixel-level NNLS correction whose compensated value must be what gets averaged into the per-cell mean (post-aggregation is wrong). REDSEA corrects real signal leaking across shared cell boundaries at ~1 um even with perfect segmentation and zero channel spillover — it is defined on segmented neighbors, so it must run after segmentation. Running REDSEA pre-segmentation, or channel comp post-aggregation, is a category error.
3. **The experimental unit is the PATIENT, not the cell or the ROI.** Cells and ROIs from one patient are not independent replicates; a cell-level or per-image test over correlated cells is pseudoreplication (reports p~0 for trivial effects). Aggregate to per-patient proportions/summaries, then a mixed model / scCODA. Arcsinh cofactor is 1 for IMC integer ion counts, NOT the suspension-CyTOF 5 (which over-compresses them). Impossible lineage-exclusive co-expression is a segmentation/spillover ALARM, not a hybrid cell type.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Panel (metal->antibody; membrane-sum channels) | Which channels extract and phenotype; a narrow membrane sum biases segmentation against some cell types |
| Segmentation frame (nuclear + membrane channels) | Every per-cell number (all are mask-bounded pixel averages); the largest irreversible error source |
| Pixel size (steinbock `--pixelsize` / Mesmer `image_mpp`, ~1.0 um for IMC) | Boundary quality + all spatial distances; the wrong value rescales cells to the wrong learned size |
| Arcsinh cofactor = 1 (IMC), not 5 (CyTOF) | Clustering/phenotyping distances; cofactor 5 over-compresses integer ion counts |

## Pipeline Overview

```
Raw MCD/TIFF Files ──> Image Processing ──> Cell Masks
                                                 │
                                                 ▼
                ┌─────────────────────────────────────────────┐
                │              imc-pipeline                   │
                ├─────────────────────────────────────────────┤
                │  1. Data Preprocessing (spillover, hot px)  │
                │  2. Cell Segmentation (Cellpose/Mesmer)     │
                │  3. Single-cell Quantification              │
                │  4. Clustering & Phenotyping                │
                │  5. Spatial Analysis                        │
                │  6. Visualization                           │
                └─────────────────────────────────────────────┘
                                                 │
                                                 ▼
                    Cell Types + Spatial Neighborhoods
```

## Decisions Threaded Through This Pipeline

Four reframes govern every stage and are detailed in the depended-on skills: IMC pixels are integer ion COUNTS (arcsinh cofactor 1, not the suspension-CyTOF 5), and spillover is spatial so it must be NNLS-compensated before segmentation; segmentation is the largest irreversible error source, so impossible double-positives are a QC alarm, not biology; a spatial interaction is a hypothesis test whose null silently decides whether the result is real or a density artifact; and the experimental unit is the patient, not the cell, so cross-condition tests aggregate to patients before testing.

## Complete steinbock Workflow

### Step 1: Setup and Preprocessing

```bash
# generate the panel template; edit the keep column before extracting
steinbock preprocess imc panel

# extract per-channel TIFFs (keep-filtered, panel-ordered) with hot-pixel removal
# (--hpf is a signed 8-neighbor difference; 50 is a count, tune to dynamic range)
steinbock preprocess imc images --hpf 50

# channel spillover is compensated with NNLS (CATALYST/cytomapper, R) on the pixel images
# BEFORE segmentation when spatial analysis is the endpoint -- see data-preprocessing
```

### Step 2: Cell Segmentation

```bash
# Mesmer/DeepCell whole-cell (nuclear-first); membrane channels aggregated via the panel column.
# --pixelsize is steinbock's CLI flag for the acquisition resolution (it wraps Mesmer's image_mpp);
# steinbock defaults it to 1.0 um for IMC, so pass the true value explicitly rather than relying on it.
steinbock segment deepcell --pixelsize 1.0 --minmax -o masks

# Alternative: Cellpose container (Cellpose 4+ default model cpsam; channel order reversed vs native)
steinbock segment cellpose --minmax -o masks
```

### Step 3: Single-cell Quantification

```bash
# Extract per-cell MEAN intensities (mean is the default and the right phenotyping aggregator;
# sum confounds cell size with expression)
steinbock measure intensities -o intensities

# Measure cell properties (area, centroid, eccentricity)
steinbock measure regionprops -o regionprops

# Build the spatial neighbor graph (expansion within a max distance; match the graph to the
# biological claim -- contact vs proximity -- in spatial-analysis)
steinbock measure neighbors --type expansion --dmax 15 -o neighbors
```

## Complete Python Workflow

```python
import pandas as pd
import numpy as np
import anndata as ad
import scanpy as sc
import squidpy as sq
from pathlib import Path

# === 1. LOAD DATA ===
data_dir = Path('steinbock_output')

intensities = pd.read_csv(data_dir / 'intensities.csv', index_col=0)
regionprops = pd.read_csv(data_dir / 'regionprops.csv', index_col=0)
neighbors = pd.read_csv(data_dir / 'neighbors.csv')

print(f'Loaded {len(intensities)} cells')

# === 2. CREATE ANNDATA ===
adata = ad.AnnData(X=intensities.values, obs=regionprops, var=pd.DataFrame(index=intensities.columns))
adata.obs['image_id'] = pd.Categorical([idx.rsplit('_', 1)[0] for idx in intensities.index])   # strip only the trailing cell index: rsplit keeps Patient1_ROI002 distinct from Patient1_ROI001. squidpy library_key requires a categorical, not object/string
adata.obs['cell_id'] = intensities.index

# Add spatial coordinates (skimage regionprops_table names them centroid-0 (y) / centroid-1 (x))
adata.obsm['spatial'] = regionprops[['centroid-0', 'centroid-1']].values

# === 3. PREPROCESSING ===
# Arcsinh transform: cofactor 1 for IMC single-cell means (Hunter 2024), NOT the
# suspension-CyTOF cofactor 5, which over-compresses IMC's lower-count means
adata.layers['counts'] = adata.X.copy()
adata.X = np.arcsinh(adata.X / 1)

# Scale for clustering
sc.pp.scale(adata, max_value=10)
adata.raw = adata.copy()

# === 4. DIMENSIONALITY REDUCTION ===
sc.pp.pca(adata, n_comps=20)
sc.pp.neighbors(adata, n_neighbors=15)
sc.tl.umap(adata)

# === 5. CLUSTERING ===
sc.tl.leiden(adata, resolution=0.8)
print(f'Found {adata.obs["leiden"].nunique()} clusters')

# === 6. PHENOTYPING ===
# Marker expression per cluster
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
marker_genes = sc.get.rank_genes_groups_df(adata, group=None)

# Annotate clusters based on markers
cluster_annotations = {
    '0': 'T cells',
    '1': 'Macrophages',
    '2': 'Tumor',
    '3': 'B cells',
    '4': 'Stromal'
}
adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_annotations)

# === 7. SPATIAL ANALYSIS ===
# Build spatial graph PER IMAGE (library_key), else Delaunay fabricates edges across ROIs
sq.gr.spatial_neighbors(adata, coord_type='generic', delaunay=True, library_key='image_id')

# Neighborhood enrichment
sq.gr.nhood_enrichment(adata, cluster_key='cell_type')

# Co-occurrence analysis
sq.gr.co_occurrence(adata, cluster_key='cell_type')

# Ripley's statistics
sq.gr.ripley(adata, cluster_key='cell_type', mode='L')

# === 8. VISUALIZATION ===
import matplotlib.pyplot as plt

# UMAP by cell type
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sc.pl.umap(adata, color='cell_type', ax=axes[0], show=False)
sc.pl.umap(adata, color='leiden', ax=axes[1], show=False)
plt.savefig('umap_celltypes.png', dpi=150, bbox_inches='tight')

# Spatial plot. Pick the image dynamically: image_id is derived from the cell index, so a hardcoded
# literal selects zero cells and spatial_scatter errors on the empty subset.
fig, ax = plt.subplots(figsize=(10, 10))
first_image = adata.obs['image_id'].iloc[0]
sq.pl.spatial_scatter(adata[adata.obs['image_id'] == first_image],
                      color='cell_type', shape=None, size=10, ax=ax)
plt.savefig('spatial_celltypes.png', dpi=150, bbox_inches='tight')

# Neighborhood enrichment heatmap
sq.pl.nhood_enrichment(adata, cluster_key='cell_type')
plt.savefig('neighborhood_enrichment.png', dpi=150, bbox_inches='tight')

# === 9. DIFFERENTIAL ANALYSIS (patient is the unit, NOT the cell) ===
import statsmodels.formula.api as smf

# aggregate to per-image proportions, then test across PATIENTS -- a cell-level or per-image
# test over correlated cells is pseudoreplication and reports p~0 for trivial effects.
# obs must carry patient and condition columns; see differential-analysis for scCODA
# (compositional) and the spatial differential path.
counts = adata.obs.groupby(['patient', 'condition', 'image_id', 'cell_type'], observed=True).size().unstack(fill_value=0)   # observed=True: image_id is categorical; the default expands the full cartesian product into all-zero phantom rows -> NaN proportions
image_prop = counts.div(counts.sum(axis=1), axis=0).reset_index()
target = 'Tumor'   # an actual cell_type column from cluster_annotations above (single-word for the formula)
res = smf.mixedlm(f'{target} ~ condition', image_prop, groups=image_prop['patient']).fit()  # patient random effect
print(res.summary())

adata.write('imc_analysis.h5ad')
print('Analysis complete!')
```

## R Alternative (imcRtools)

```r
library(imcRtools)
library(cytomapper)
library(CATALYST)

# Read steinbock output
spe <- read_steinbock('steinbock_output/')

# Transform (cofactor 1 for IMC single-cell means, not 5)
assay(spe, 'exprs') <- asinh(counts(spe) / 1)

# Cluster (CATALYST runDR takes assay=; cluster() always uses the 'exprs' assay, no assay arg)
spe <- runDR(spe, features = rownames(spe), assay = 'exprs', dr = 'UMAP')
spe <- cluster(spe, features = rownames(spe), xdim = 10, ydim = 10, maxK = 20)

# Spatial analysis. buildSpatialGraph names the colPair '<type>_interaction_graph';
# aggregateNeighbors counts a label via aggregate_by='metadata' + count_by=.
spe <- buildSpatialGraph(spe, img_id = 'sample_id', type = 'expansion', threshold = 20)
spe <- aggregateNeighbors(spe, colPairName = 'expansion_interaction_graph',
                          aggregate_by = 'metadata', count_by = 'cluster_id')

# Spatial context
spe <- detectCommunity(spe, colPairName = 'expansion_interaction_graph',
                       size_threshold = 10, group_by = 'sample_id')

# Plot (img_id is the colData COLUMN used to facet; read_steinbock names it 'sample_id', not 'image_id')
plotSpatial(spe, img_id = 'sample_id', node_color_by = 'cluster_id')
```

## QC Checkpoints

| Stage | Check | Action if Failed |
|-------|-------|------------------|
| Preprocessing | No hot pixel streaks | Lower threshold |
| Segmentation | >80% cells detected | Adjust diameter |
| Quantification | All markers extracted | Check panel.csv |
| Clustering | 5-20 clusters | Adjust resolution |
| Spatial | Neighbors detected | Check distance |

## Workflow Variants

### High-plex Panels (40+ markers)
```python
# Use batch-aware clustering
import scvi

scvi.model.SCVI.setup_anndata(adata, batch_key='image_id')
model = scvi.model.SCVI(adata)
model.train()
adata.obsm['X_scvi'] = model.get_latent_representation()
sc.pp.neighbors(adata, use_rep='X_scvi')
```

### Tumor Microenvironment Analysis
```python
# Spatial cell-cell co-location around tumor (per-image, then aggregate to patient).
# Note: sq.gr.ligrec keys ligand-receptor pairs on gene symbols from OmniPath, so it is
# usually empty on a ~40-marker antibody panel -- prefer neighborhood enrichment for IMC.
sq.gr.nhood_enrichment(adata, cluster_key='cell_type')   # see spatial-analysis for the null caveat
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Impossible double-positive "hybrid" cell types | Spillover not corrected before phenotyping (channel and/or lateral) | NNLS channel compensation on pixels before segmentation; REDSEA on the per-cell table after; treat lineage-exclusive co-expression as a QC failure until proven |
| Every boundary degraded, cells the wrong size | Wrong pixel size (Mesmer `image_mpp` defaults None=no rescaling, model trained at ~0.5; steinbock `--pixelsize` defaults 1.0) | Pass the true acquisition resolution explicitly (~1.0 um for IMC) |
| Macrophages under-captured; biased comparison | Nuclear-expansion segmentation cross-compared with whole-cell data | Never quantitatively compare expansion-segmented vs whole-cell; report the expansion radius; use constrained (not free) dilation |
| p~0 for a trivial effect | Pseudoreplication (cells/ROIs treated as replicates) | Aggregate to per-patient summaries; mixed model with patient random effect / scCODA |
| Markers over-compressed, noise clusters | Arcsinh cofactor 5 used on IMC | Cofactor 1 for IMC integer ion counts |
| Acquisition batch drives the clusters | Batch confounded with / not modeled against condition | Randomize acquisition order; batch-aware clustering (Harmony/scVI) for clustering ONLY; model batch as a covariate; no rescue if batch==condition |

## References

- Windhager J, Zanotelli VRT, Schulz D, et al (2023) An end-to-end workflow for multiplexed image processing and analysis. *Nature Protocols* 18:3565-3613. DOI 10.1038/s41596-023-00881-0. (steinbock.)
- Greenwald NF, Miller G, Moen E, et al (2022) Whole-cell segmentation of tissue images with human-level performance using large-scale data annotation and deep learning. *Nature Biotechnology* 40:555-565. DOI 10.1038/s41587-021-01094-0. (Mesmer/DeepCell.)
- Bai Y, Zhu B, Rovira-Clave X, et al (2021) Adjacent cell marker lateral spillover compensation and reinforcement for multiplexed images. *Frontiers in Immunology* 12:652631. DOI 10.3389/fimmu.2021.652631. (REDSEA.)
- Palla G, Spitzer H, Klein M, et al (2022) Squidpy: a scalable framework for spatial omics analysis. *Nature Methods* 19:171-178. DOI 10.1038/s41592-021-01358-2.
- Hunter B, Nicorescu I, Foster E, et al (2024) OPTIMAL: an OPTimized Imaging Mass cytometry AnaLysis framework for benchmarking segmentation and data exploration. *Cytometry Part A* 105:36-53. DOI 10.1002/cyto.a.24803. (arcsinh cofactor 1 for IMC.)

## Related Skills

- imaging-mass-cytometry/data-preprocessing - Hot pixel, spillover
- imaging-mass-cytometry/cell-segmentation - Cellpose/Mesmer details
- imaging-mass-cytometry/phenotyping - Cluster annotation
- imaging-mass-cytometry/spatial-analysis - Spatial statistics
- imaging-mass-cytometry/differential-analysis - Patient-level cross-condition testing
- imaging-mass-cytometry/interactive-annotation - Manual cell labeling
- imaging-mass-cytometry/quality-metrics - QC metrics
- single-cell/clustering - Clustering methods
- spatial-transcriptomics/spatial-statistics - Related spatial methods
<!-- END FILE: workflows/imc-pipeline/SKILL.md -->

## 子目录：workflows/liquid-biopsy-pipeline

<!-- BEGIN FILE: workflows/liquid-biopsy-pipeline/SKILL.md -->
---
name: bio-workflows-liquid-biopsy-pipeline
description: Orchestrates the cell-free DNA / liquid-biopsy pipeline from plasma sequencing to tumor monitoring, forking tumor-naive (screening) vs tumor-informed (MRD), and chaining pre-analytic QC, UMI/duplex error-suppression (fgbio), fragment QC, ichorCNA tumor fraction (sWGS) or VarDict low-VAF calling (panel), CHIP subtraction against matched WBC, optional fragmentomics/methylation, and longitudinal tracking. Use when treating pre-analytics as the irreversible sensitivity ceiling (tube/time-to-plasma/hemolysis), running error-suppression BEFORE calling (single-strand consensus does not remove deamination; only duplex does), reporting a VAF only with input genome-equivalents (TF ~ 2x VAF only for clonal-het-diploid), subtracting CHIP before reporting somatic, or keeping tube/panel/pipeline identical across a longitudinal MRD series. Hands mechanism to the liquid-biopsy component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: ichorCNA
goal_approach_exempt: true
workflow: true
depends_on:
  - liquid-biopsy/cfdna-preprocessing
  - liquid-biopsy/analytical-validation
  - liquid-biopsy/ctdna-mutation-detection
  - liquid-biopsy/tumor-fraction-estimation
  - liquid-biopsy/fragment-analysis
  - liquid-biopsy/methylation-based-detection
  - liquid-biopsy/longitudinal-monitoring
qc_checkpoints:
  - pre_analytics: "Tube type/time-to-plasma in window; double-spin; low hemolysis; gDNA-contamination fragment check"
  - after_consensus: "Unique-molecule coverage / genome-equivalents recovered (NOT raw depth); duplication plateaued -- read both off the GroupReadsByUmi --family-size-histogram output"
  - after_fragment: "Modal insert ~167bp (150-180); mononucleosome fraction >0.3"
  - after_tf: "TF above the ~3% ichorCNA LoD to trust the value (below = below detection, not low burden)"
  - after_mutation: "VarDict -f 0.005 is a reporting floor, NOT a detection threshold: confirm each call against a per-locus background-error model (PoN or smCounter2) before reporting; CHIP-subtracted against matched WBC"
---

## Version Compatibility

Reference examples tested with: BWA 0.7.17+, VarDict 1.8+, fgbio 2.1+, ichorCNA 0.6.0+, FinaleToolkit 0.9+ (the `delfi` param was `autosomes` before 0.9, renamed `chrom_sizes`), MethylDackel 0.6+, numpy 1.26+, pandas 2.2+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Liquid Biopsy Analysis Pipeline

**"Analyze my liquid biopsy cfDNA data end-to-end"** -> Orchestrate UMI-aware preprocessing (fgbio), ctDNA mutation detection (VarDict), tumor fraction estimation (ichorCNA), fragmentomics analysis, and longitudinal monitoring for treatment response.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

A liquid-biopsy result is decided at four seams, two of them set before the sequencer ever runs.

1. **Pre-analytics is irreversible and is the sensitivity ceiling — set at the blood draw, not the pipeline.** WBC lysis dumps high-quality germline/CHIP DNA into the denominator; a 0.5% tumor fraction diluted to 0.1% by a processing delay is a false negative with NO bioinformatic recovery. Tube chemistry (Streck ~7d RT vs EDTA <6h), double-spin, and hemolysis are the FIRST gate the whole pipeline is conditional on. Mixing tube types within a longitudinal series is a batch confound.
2. **The error-suppression / UMI scheme is committed at library prep and cannot be upgraded after sequencing.** Single-strand UMI consensus floors error ~1e-4 to 1e-5 but does NOT remove deamination (C>T) or oxidation (G>T) — those lesions are on the template, so every PCR copy inherits them and the family votes unanimously for the artifact. Only DUPLEX (both-strand concordance) reaches <1e-7. Call on the consensus BAM, never the raw BAM.
3. **A VAF is undefined without input genome-equivalents, and TF != VAF.** 0.1% on 100 GE is noise; on 30,000 GE it is solid. The LoD is set by input GE and assay design (tumor-informed bespoke integrates 16-50 loci to ppm; tumor-naive fixed panel is error/sampling-limited ~0.1-0.5%; ichorCNA sWGS floors ~3% TF). TF ~ 2x VAF only for a clonal, heterozygous, diploid locus — copy number breaks the factor of 2.
4. **Matched buffy-coat/WBC is the CHIP-subtraction commitment.** ~81.6% of cfDNA variants in controls and ~53.2% in cancer patients are CHIP, not tumor (Razavi 2019). Without matched WBC, a tumor-naive cfDNA call is presumptively CHIP-contaminated; a gene-list filter is a weak fallback. Decide at study design.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Pre-analytics (tube/time-to-plasma/double-spin) | Irreversible TF dilution; the whole pipeline's sensitivity ceiling; consistent across a longitudinal series |
| Error-suppression scheme (single-strand vs DUPLEX) | The achievable error floor; single-strand cannot remove deamination/oxidation; cannot upgrade post-hoc |
| Assay design (tumor-naive vs tumor-informed; panel vs sWGS) + input GE | The LoD and whether it is per-locus or panel-integrated; a VAF is undefined without input GE |
| Matched WBC available? | Whether CHIP is definitively subtracted (WBC) or only gene-list-filtered (weak) |

## Pipeline Overview

```
Pre-analytical QC -> cfDNA Preprocessing -> Fragment QC
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                   ↓
   sWGS Branch                        Panel Branch
        ↓                                   ↓
   ichorCNA                          VarDict/smCounter2
   (Tumor Fraction)                  (Mutation Detection)
        ↓                                   ↓
        └─────────────────┬─────────────────┘
                          ↓
                 Longitudinal Tracking
```

## Step 0: Pre-Analytical QC

```python
def check_preanalytical_quality(sample_metadata):
    '''
    Pre-analytical factors critical for cfDNA quality.

    Requirements:
    - Streck tube: up to 7 days at room temperature
    - EDTA tube: process within 6 hours
    - Avoid hemolysis
    - Store extracted DNA at -80C
    '''
    issues = []

    if sample_metadata['tube_type'] == 'EDTA':
        if sample_metadata['processing_delay_hours'] > 6:
            issues.append('EDTA tube processed > 6 hours - risk of gDNA contamination')

    if sample_metadata['hemolysis_score'] > 1:
        issues.append('Hemolysis detected - expect cellular DNA contamination')

    return issues
```

## Step 1: cfDNA Preprocessing with UMI Consensus

```bash
# For UMI-tagged libraries (targeted panels)
# fgbio pipeline

# Extract UMIs. Read-structure is library-specific; see liquid-biopsy/cfdna-preprocessing.
fgbio ExtractUmisFromBam \
    --input raw.bam \
    --output with_umis.bam \
    --read-structure 3M2S+T 3M2S+T \
    --single-tag RX

# Align. bwa reads FASTQ, not BAM, and stripping to FASTQ drops the RX/UMI tag -- so emit FASTQ
# carrying RX (samtools fastq -T RX), align, then re-zip the uBAM tags back on with fgbio ZipperBams
# so GroupReadsByUmi still sees RX.
samtools fastq -T RX with_umis.bam | \
    bwa mem -C -p -t 8 -Y reference.fa - | \
    fgbio ZipperBams --unmapped with_umis.bam --ref reference.fa --output aligned.bam

# Group by UMI. --family-size-histogram is not optional here: rule 3 says a VAF is undefined without
# input genome-equivalents, and this histogram is where GE and the duplication plateau are read off.
# Raw depth after consensus collapse is not a sensitivity measure -- unique molecules are.
fgbio GroupReadsByUmi \
    --input aligned.bam \
    --output grouped.bam \
    --strategy adjacency \
    --edits 1 \
    --family-size-histogram qc/family_sizes.txt

# Consensus calling: keep the caller permissive (fgbio #1009), apply strictness at the filter
fgbio CallMolecularConsensusReads \
    --input grouped.bam \
    --output consensus.bam \
    --min-reads 1

# Filter: this is the real quality gate
fgbio FilterConsensusReads \
    --input consensus.bam \
    --output final.bam \
    --ref reference.fa \
    --min-reads 2
```

## Step 2: Fragment QC Checkpoint

```python
import pysam
import numpy as np

def verify_cfdna_quality(bam_path):
    '''
    QC Checkpoint: Verify cfDNA fragment profile.
    Expected: peak at ~167bp (mononucleosome)
    '''
    bam = pysam.AlignmentFile(bam_path, 'rb')
    sizes = []

    for read in bam.fetch():
        # cfDNA fragments are short; cap at 400 bp (fragments beyond are gDNA/noise) so the
        # modal-size bincount is bounded and not skewed by a few long outliers.
        if read.is_proper_pair and not read.is_secondary and 0 < read.template_length <= 400:
            sizes.append(read.template_length)

    bam.close()
    sizes = np.array(sizes)

    modal_size = np.bincount(sizes).argmax()
    mono_frac = np.sum((sizes >= 150) & (sizes <= 180)) / len(sizes)

    qc_pass = 150 <= modal_size <= 180 and mono_frac > 0.3

    return {
        'modal_size': modal_size,
        'mononucleosome_fraction': mono_frac,
        'qc_pass': qc_pass,
        'message': 'Good cfDNA profile' if qc_pass else 'Atypical fragment distribution'
    }
```

## Step 3a: Tumor Fraction Estimation (sWGS)

ichorCNA is a command-line script (`Rscript scripts/runIchorCNA.R`), NOT an importable `runIchorCNA()` function, and it is preceded by HMMcopy `readCounter` to bin the BAM. The ~3% tumor-fraction floor is an analytical limit of detection; below it, route to fragmentomics or methylation rather than trusting a low value (see liquid-biopsy/analytical-validation and liquid-biopsy/tumor-fraction-estimation).

```bash
# For shallow WGS data (0.1-1x coverage); GavinHaLab fork
readCounter --window 1000000 --quality 20 \
    --chromosome "chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX" \
    sample.bam > sample.wig

Rscript scripts/runIchorCNA.R \
    --id sample_id --WIG sample.wig \
    --gcWig gc_hg38_1000kb.wig --mapWig map_hg38_1000kb.wig \
    --centromere GRCh38.GCA_000001405.2_centromere_acen.txt \
    --normalPanel HD_ULP_PoN_hg38_1Mb_normAutosomes_median.rds \   # GavinHaLab/ichorCNA extdata name; PoN build MUST match the gc/map/centromere build (the non-hg38 1Mb PoN is hg19)
    --normal "c(0.5,0.6,0.7,0.8,0.9)" --ploidy "c(2,3)" --maxCN 7 \
    --estimateNormal TRUE --estimatePloidy TRUE --estimateScPrevalence TRUE \
    --outDir ichor_results/
# Tumor fraction = 1 - n in sample_id.params.txt
```

## Step 3b: Mutation Detection (Targeted Panel)

```bash
# For deep targeted sequencing
# Use UMI-consensus BAM from Step 1

vardict-java \
    -G reference.fa \
    -f 0.005 \
    -N sample_id \
    -b consensus.bam \
    -c 1 -S 2 -E 3 -g 4 \
    panel.bed | \
teststrandbias.R | \
var2vcf_valid.pl \
    -N sample_id \
    -E \
    -f 0.005 \
    > sample.vcf
```

## Step 4: CHIP Filtering

Clonal hematopoiesis (CHIP) is the dominant false-positive source in plasma: ~81.6% of cfDNA variants in controls and ~53.2% in cancer patients trace to white blood cells (Razavi 2019 Nat Med 25:1928). A gene-list filter is a weak fallback; the definitive control is sequencing matched buffy-coat/WBC DNA and subtracting any variant present there. See liquid-biopsy/ctdna-mutation-detection.

```python
CHIP_GENES = ['DNMT3A', 'TET2', 'ASXL1', 'PPM1D', 'JAK2', 'SF3B1', 'SRSF2', 'TP53']

def filter_chip(variants_df, wbc_variants=None, chip_genes=CHIP_GENES):
    '''Subtract WBC-matched variants when available; else fall back to a CHIP gene list.'''
    if wbc_variants is not None:
        # REF must be in the key. Left-aligned indels share (chrom, pos, alt): a 1bp deletion
        # (REF=AT, ALT=A) and a 2bp deletion (REF=ATT, ALT=A) collide, so a (chrom, pos, alt) key
        # would silently subtract a real somatic indel as CHIP.
        key = ['chrom', 'pos', 'ref', 'alt']
        wbc_keys = set(map(tuple, wbc_variants[key].itertuples(index=False, name=None)))
        in_wbc = variants_df[key].apply(lambda r: tuple(r) in wbc_keys, axis=1)
        return variants_df[~in_wbc], variants_df[in_wbc]

    chip = variants_df[variants_df['gene'].isin(chip_genes)]
    somatic = variants_df[~variants_df['gene'].isin(chip_genes)]
    return somatic, chip
```

## Step 5: Fragmentomics Analysis (Optional)

FinaleToolkit (MIT license, not DELFI software) exposes real hyphenated CLI subcommands and an underscored `finaletoolkit.frag` Python API; `delfi` GC-corrects the short/long ratio (raw ratios are dominated by GC and sequencing batch). DELFI is a methodology and a company, not a `pip install`-able tool.

```bash
# GC-corrected genome-wide DELFI profile and end-motif diversity.
# delfi positionals: input chrom_sizes reference bins_file; GC correction is on by default.
# --no-remove-nocov keeps all bins on non-hg19 references (the default removes two hardcoded hg19 no-coverage regions).
finaletoolkit delfi consensus.bam hg38.chrom.sizes hg38.2bit bins_100kb.bed -g gaps.bed --no-remove-nocov -o sample.delfi.bed
finaletoolkit end-motifs consensus.bam hg38.2bit -o sample.end_motifs.tsv
finaletoolkit mds sample.end_motifs.tsv
```

```python
from finaletoolkit.frag import delfi  # see liquid-biopsy/fragment-analysis

def run_fragmentomics(bam_path, chrom_sizes, reference, bins_bed, gap_bed):
    '''GC-corrected DELFI short/long profile (MDS comes from end_motifs().motif_diversity_score()).
    Python positional order is (input, chrom_sizes, bins_file, reference_file) - note this differs
    from the CLI order (input, chrom_sizes, reference, bins), so pass by keyword to be safe.'''
    return delfi(bam_path, chrom_sizes=chrom_sizes, bins_file=bins_bed,
                 reference_file=reference, gap_file=gap_bed)
```

## Step 6: Longitudinal Tracking

```python
import pandas as pd
import numpy as np

def track_longitudinal(samples_df):
    '''
    Track ctDNA over treatment.

    samples_df columns: [sample_id, timepoint, tumor_fraction, mutations...]
    '''
    samples_df = samples_df.sort_values('timepoint')

    baseline = samples_df.iloc[0]['tumor_fraction']
    samples_df['log2_fc'] = np.log2(samples_df['tumor_fraction'] / baseline)

    nadir = samples_df['tumor_fraction'].min()

    response = 'unknown'
    if nadir < 0.001:
        response = 'Complete molecular response'
    elif nadir < baseline * 0.01:
        response = 'Major molecular response (>2 log)'
    elif nadir < baseline * 0.5:
        response = 'Partial molecular response'

    return samples_df, response
```

## Complete Pipeline Script

```python
def run_liquid_biopsy_pipeline(sample_config):
    '''
    Complete liquid biopsy analysis pipeline.

    sample_config: dict with keys:
        - bam_file: Input BAM
        - data_type: 'swgs' or 'panel'
        - reference: Reference FASTA
        - bed_file: Panel BED (for panel data)
        - output_dir: Output directory
    '''
    results = {}

    # Step 1: Preprocess (if UMI data)
    if sample_config.get('has_umis'):
        preprocessed_bam = preprocess_with_fgbio(sample_config['bam_file'])
    else:
        preprocessed_bam = sample_config['bam_file']

    # Step 2: Fragment QC
    frag_qc = verify_cfdna_quality(preprocessed_bam)
    if not frag_qc['qc_pass']:
        print(f"WARNING: {frag_qc['message']}")
    results['fragment_qc'] = frag_qc

    # Step 3: Analysis based on data type
    if sample_config['data_type'] == 'swgs':
        # Tumor fraction estimation
        results['tumor_fraction'] = run_ichorcna(preprocessed_bam)
    elif sample_config['data_type'] == 'panel':
        # Mutation detection. CHIP subtraction is not optional (rule 4): without matched WBC the
        # calls are presumptively CHIP-contaminated and the gene list is only a weak fallback.
        variants = call_variants(preprocessed_bam, sample_config['bed_file'])
        wbc = call_variants(sample_config['wbc_bam'], sample_config['bed_file']) if sample_config.get('wbc_bam') else None
        somatic, chip = filter_chip(variants, wbc_variants=wbc)
        results['variants'] = somatic
        results['chip_variants'] = chip

    # Step 4: Optional fragmentomics
    if sample_config.get('run_fragmentomics'):
        results['fragmentomics'] = run_fragmentomics(preprocessed_bam)

    return results
```

## Choosing the branch (tumor-naive vs tumor-informed)

Pipeline-level selection only; mechanism lives in the component skills.

| Situation | Branch | Hand off to |
|-----------|--------|-------------|
| Screening / no known tumor / MCED | tumor-NAIVE (fixed panel, sWGS, or methylation) | liquid-biopsy/methylation-based-detection |
| MRD/recurrence of a KNOWN tumor | tumor-INFORMED bespoke (16-50 clonal variants from tissue WES) | liquid-biopsy/longitudinal-monitoring |
| Tumor fraction from sWGS (0.1-1x) | ichorCNA (copy-number-based, floor ~3% TF) | liquid-biopsy/tumor-fraction-estimation |
| Low-VAF mutations from a deep panel | VarDict / smCounter2 on the UMI-consensus BAM | liquid-biopsy/ctdna-mutation-detection |
| Below mutation LoD, still need signal | fragmentomics (DELFI/end-motifs) or methylation | liquid-biopsy/fragment-analysis |
| Stating/trusting a sensitivity claim | LoB/LoD/LoD95/LoQ, per-locus vs panel-integrated | liquid-biopsy/analytical-validation |

Tumor-informed reaches ppm by integrating across 16-50 loci (beats the single-locus Poisson floor) but is BLIND by design to new/resistance variants; tumor-naive sees any panel variant but is CHIP-dominated and error-limited.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| False negative on a real low-TF sample | Bad blood draw irreversibly diluted TF | Pre-analytic gate; cannot be rescued downstream |
| Residual C>T / G>T false positives | Single-strand consensus assumed to remove damage | Duplex, or UDG for deamination; flag the substitution spectrum |
| Money spent, no sensitivity gain | Sequenced past molecular saturation | Report unique-molecule coverage; invest in plasma volume / conversion efficiency |
| Blood clones reported as tumor | CHIP not subtracted (esp. TP53/PPM1D, both CHIP and driver) | Matched buffy-coat/WBC sequencing (gene list is a weak fallback) |
| Apparent burden halved or doubled | VAF reported as TF (or vice versa) | State VAF vs TF; TF ~ 2x VAF only for clonal-het-diploid; prefer CNA-based TF when CN is non-neutral |
| A "low" TF trusted below the assay floor | ~3% ichorCNA LoD ignored | Below the floor = below detection; route to fragmentomics/methylation |
| Longitudinal "response" that is a batch shift | Tube/panel/pipeline changed between draws | Same tube, same panel, same pipeline across timepoints |

## References

- Razavi P, Li BT, Brown DN, et al (2019) High-intensity sequencing reveals the sources of plasma circulating cell-free DNA variants. *Nature Medicine* 25:1928-1937. DOI 10.1038/s41591-019-0652-7. (CHIP dominance of cfDNA variants.)
- Adalsteinsson VA, Ha G, Freeman SS, et al (2017) Scalable whole-exome sequencing of cell-free DNA reveals high concordance with metastatic tumors. *Nature Communications* 8:1324. DOI 10.1038/s41467-017-00965-y. (ichorCNA; ~3% TF LoD.)
- Schmitt MW, Kennedy SR, Salk JJ, et al (2012) Detection of ultra-rare mutations by next-generation sequencing. *PNAS* 109:14508-14513. DOI 10.1073/pnas.1208715109. (duplex error floor.)
- Reinert T, Henriksen TV, Christensen E, et al (2019) Analysis of plasma cell-free DNA by ultradeep sequencing in patients with stages I to III colorectal cancer. *JAMA Oncology* 5:1124-1131. DOI 10.1001/jamaoncol.2019.0528. (tumor-informed bespoke MRD.)

## Related Skills

- liquid-biopsy/cfdna-preprocessing - UMI/duplex consensus error suppression
- liquid-biopsy/analytical-validation - molecule-counting limits of detection and honest LoD reporting
- liquid-biopsy/ctdna-mutation-detection - low-VAF calling and CHIP subtraction
- liquid-biopsy/tumor-fraction-estimation - ichorCNA tumor fraction from sWGS
- liquid-biopsy/fragment-analysis - fragmentomics features
- liquid-biopsy/methylation-based-detection - methylation detection and tissue-of-origin
- liquid-biopsy/longitudinal-monitoring - serial MRD tracking
<!-- END FILE: workflows/liquid-biopsy-pipeline/SKILL.md -->

## 子目录：workflows/longread-sv-pipeline

<!-- BEGIN FILE: workflows/longread-sv-pipeline/SKILL.md -->
---
name: bio-workflows-longread-sv-pipeline
description: Orchestrates an end-to-end long-read structural-variant pipeline - basecalling to minimap2 alignment (platform-matched preset) to Sniffles2/cuteSV/pbsv calling to optional assembly-based calling (dipcall/PAV) to two-step .snf cohort merging to Truvari benchmarking - chaining ONT and PacBio HiFi runs while handing the SV signal mechanism off to the component skills. Use when running a long-read SV workflow from reads to a benchmarked callset, choosing the minimap2 preset and SV caller by platform and goal, deciding when long reads are worth it for the insertions and repeat-mediated SVs short reads physically miss, building a joint-genotyped cohort with the two-step .snf design, or parameterizing a Truvari benchmark against GIAB HG002 Tier 1 plus CMRG. Not for the SV signal mechanism itself (see variant-calling/structural-variant-calling) or short-read SV.
tool_type: cli
primary_tool: Sniffles
workflow: true
depends_on:
  - long-read-sequencing/basecalling
  - long-read-sequencing/long-read-alignment
  - long-read-sequencing/long-read-qc
  - long-read-sequencing/structural-variants
qc_checkpoints:
  - after_qc: "Read N50 >10kb, mean quality >Q10 (ONT R10) / HiFi rq>0.99"
  - after_alignment: "Mapping rate >90%, coverage >=15x for confident SV calling"
  - after_calling: "SV count in the expected range, INS/DEL ratio sane, genotypes concordant"
  - after_benchmark: "Truvari F1 reported WITH its refdist/pctsize/pctseq, on Tier 1 AND CMRG"
---

## Version Compatibility

Reference examples tested with: minimap2 2.28+, Sniffles 2.2+, cuteSV 2.1+, pbsv 2.9+, dipcall 0.3+, bcftools 1.19+, samtools 1.19+, truvari 4.0+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Use minimap2 >= 2.28: the `lr:hq` accurate-read preset was added in 2.27, and 2.28 fixes the 2.27 `--MD` regression. Supply a reference-matched tandem-repeat BED to the caller - it is the single biggest false-positive lever in repeats. Truvari renamed the alt-sequence-similarity param from `--pctsim` to `--pctseq` at v4; confirm against `truvari bench --help`.

If code throws an error, introspect the installed tool and adapt the example to the actual API rather than retrying.

# Long-Read SV Pipeline

**"Detect structural variants from my long-read sequencing data"** -> Chain basecalling, platform-matched minimap2 alignment, an SV caller selected by platform and goal, an optional assembly-based branch, cohort merging, and a parameterized Truvari benchmark - with the SV mechanism delegated to the component skills.

This is a workflow (orchestration) skill: it makes the stage-to-stage decisions and quality gates that connect the component skills. It does NOT re-teach how a caller sees an SV or the VCF representation minefield - that lives in variant-calling/structural-variant-calling and long-read-sequencing/structural-variants.

## Why long reads for SV: the physics that justifies this pipeline

Run this pipeline instead of a short-read SV workflow for one mechanistic reason: a single long read (PacBio HiFi ~15-25 kb, ONT tens of kb to >Mb ultralong) physically spans the SV and both flanks in one molecule, turning SV detection from an inference-over-fragments problem into near-direct observation. Two consequences decide whether long reads earn their per-sample cost:

- Insertions become tractable. Placing and sizing an insertion needs reads that carry the novel bases; when an INS exceeds Illumina read length (150 bp) no short read spans it, so short-read INS recall is stuck at ~30-50% while long reads reach ~90%+. Ebert 2021 (*Science* 372:eabf7117) found 68% of 107,590 assembly-discovered SVs were missed by short reads. If insertions matter, this pipeline is the answer, not a tuning knob.
- Repeat-mediated junctions resolve. A 20 kb read anchored in unique sequence on both flanks spans a breakpoint buried in a 5 kb repeat that no 150 bp read can straddle, bringing segmental-duplication NAHR, mobile-element insertions, and VNTR/STR expansions into reach.

The governing pipeline principle: an SV call is a *representation artifact* of choices made upstream. The aligner preset, the tandem-repeat BED handed to the caller, and the Truvari matching parameters move precision/recall as much as the caller does. Chaining decisions - not the caller name - are what this skill is about.

## Pipeline map

```
POD5/FAST5 (ONT only)
    |  [Step 0] Dorado basecall  -> long-read-sequencing/basecalling
    v            (model + methylation are IRREVERSIBLE choices; sup model for SV)
FASTQ (ONT / PacBio HiFi)
    |  [QC]     NanoPlot / NanoComp -> long-read-sequencing/long-read-qc
    v            gate: read N50 >10 kb, sane quality, chimera screen
[Step 1] minimap2 alignment       -> long-read-sequencing/long-read-alignment
    |            preset by platform/chemistry; -Y keeps breakpoint seq on split reads
    v            gate: mapping rate >90%, coverage >=15x
[Step 2] SV calling               -> long-read-sequencing/structural-variants
    |            Sniffles2 / cuteSV / pbsv, caller by platform + goal
    |            + tandem-repeat BED (biggest FP lever)      variant-calling/structural-variant-calling
    v
[Step 3, optional] assembly-based SV (dipcall / PAV against a phased diploid assembly)
    |            highest-quality callset; the way truth sets are built
    v
[Step 4] cohort merge             -> two-step Sniffles2 .snf (per-sample -> combine)
    |
    v
[Step 5] benchmark                -> Truvari vs GIAB HG002 Tier 1 + CMRG
                 an F1 is meaningless without refdist/pctsize/pctseq
```

## Platform decision: ONT vs PacBio HiFi

The platform sets the preset, the caller options, and what bonus channels are available. Decide before basecalling.

| Dimension | ONT (R10.4.1) | PacBio HiFi |
|-----------|---------------|-------------|
| Per-base accuracy | ~Q20+ simplex, higher duplex | ~Q30+ (circular consensus) |
| Read length | tens of kb; ultralong >Mb achievable | ~15-25 kb |
| minimap2 preset | `lr:hq` (R10/Q20 accurate) or `map-ont` (older R9) | `map-hifi` |
| Best for | ultralong spans, repeat/centromere traversal, native methylation | highest base accuracy, small variants + SV in one run |
| SV caller | Sniffles2 or cuteSV | Sniffles2, cuteSV, or pbsv (official, TR-aware) |
| Bonus channel | 5mCG/6mA methylation if requested AT basecall time | 5mCG via kinetics; phasing native from HiFi length |

R10.4 chemistry moved ONT simplex to ~Q20, which is why `lr:hq` (not the noisy-read `map-ont`) is the right preset for modern ONT - it rewrites the scoring/chaining model for accurate reads and runs faster at equal accuracy. Older R9 data still needs `map-ont`.

## SV caller selection (by platform and goal)

Do not re-derive the caller mechanism here; pick by goal and hand tuning to the component skill.

| Goal / platform | Caller | Why / cross-reference |
|-----------------|--------|-----------------------|
| ONT/HiFi germline, cohorts, mosaic | Sniffles2 | field standard; two-step `.snf` population merge scales linearly in N; `--mosaic` for low-VAF (Smolka 2024) |
| Highest recall on noisy ONT | cuteSV | signature clustering; MUST pass the per-platform param set and `--genotype` (Jiang 2020) |
| PacBio HiFi, official, TR-aware | pbsv | expects pbmm2 alignments; single- and joint-sample modes |
| tandem-vs-interspersed DUP detail | SVIM | reports origin AND destination of duplications (Heller 2019) |
| Highest-quality callset / truth set | dipcall or PAV | assembly-vs-reference from a phased diploid assembly (Li 2018; Ebert 2021) |
| Somatic (tumor-normal) | Severus / nanomonsv | matched-normal subtraction; do NOT use Sniffles `--mosaic` for somatic (Keskus 2025) |

Methods evolve; verify current best practice against each tool's docs before committing. Deeper caller tuning (cuteSV per-platform params, the tandem-repeat BED, aligner effects) lives in long-read-sequencing/structural-variants.

## Step 0: Basecalling (ONT only)

**Goal:** Convert raw POD5/FAST5 signal into reads suitable for SV calling, capturing methylation if it will ever be needed.

**Approach:** Basecall with Dorado using a chemistry-matched `sup` (super-accuracy) model; request modified bases at basecall time because methylation cannot be recovered later. PacBio HiFi arrives as reads already, so this step is skipped.

```bash
# sup model maximizes accuracy for SV; 5mCG_5hmCG requested now (irreversible if omitted).
# See long-read-sequencing/basecalling for model selection and duplex.
dorado basecaller sup pod5_dir/ --modified-bases 5mCG_5hmCG > reads.bam
samtools fastq -T MM,ML reads.bam | gzip > reads.fastq.gz   # -T carries methylation tags through
```

## Step 1: Alignment

**Goal:** Produce a sorted, indexed BAM whose split (supplementary) alignments retain the breakpoint sequence SV callers reconstruct from.

**Approach:** Align with the platform-matched minimap2 preset; keep `-Y` so supplementary alignments are soft-clipped (not hard-clipped), which preserves the junction bases on split reads. SV calling rides on supplementary, not secondary, alignments.

```bash
# ONT R10/Q20: lr:hq (accurate reads). Older R9: map-ont. HiFi: map-hifi. PacBio CLR: map-pb.
minimap2 -ax lr:hq -t 16 --MD -Y reference.fa reads.fastq.gz | \
    samtools sort -@ 4 -o aligned.bam
samtools index aligned.bam
```

**QC checkpoint** (gate before spending compute on calling):

```bash
samtools flagstat aligned.bam                                  # mapping rate should be >90%
samtools depth -a aligned.bam | awk '{s+=$3} END{print "mean cov:", s/NR}'
# Gate: >=15x for confident SV calling; below ~10x callers drift toward false negatives.
```

## Step 2: SV calling

**Goal:** Call SVs (>=50 bp DEL/INS/DUP/INV/BND) from the aligned reads with a caller matched to the platform.

**Approach:** Run Sniffles2 (the default) with a reference-matched tandem-repeat BED - it clusters the repeat-driven false positives that otherwise dominate the callset. `--minsvlen 50` enforces the GIAB >=50 bp SV convention (Sniffles2 defaults to 35).

```bash
# Sniffles2: the tandem-repeat BED is the single biggest false-positive lever in repeats.
sniffles --input aligned.bam --reference reference.fa \
    --tandem-repeats human_GRCh38_TR.bed \
    --vcf svs.vcf.gz --threads 8 --minsvlen 50 --output-rnames
```

cuteSV as an alternative - its defaults are NOT platform-appropriate, and `--genotype` is off by default:

```bash
# ONT param set shown. HiFi: 1000/0.9/1000/0.5. CLR: 100/0.3/200/0.5. See structural-variants.
mkdir -p work_dir   # cuteSV requires the work dir to pre-exist; it does not create it
cuteSV aligned.bam reference.fa svs.vcf work_dir/ --threads 8 --genotype \
    --max_cluster_bias_INS 100 --diff_ratio_merging_INS 0.3 \
    --max_cluster_bias_DEL 100 --diff_ratio_merging_DEL 0.3
```

## Step 3 (optional): Assembly-based SV

**Goal:** Produce the highest-quality SV callset by comparing a phased diploid assembly to the reference, rather than inferring from read alignments.

**Approach:** Assemble the genome (hifiasm/verkko), then call variants from the two haplotype assemblies aligned to the reference. dipcall (the syndip method) and PAV (the HGSVC method) are the assembly-vs-reference callers; this is how the GIAB and HGSVC truth sets themselves are built. Use it when an assembly already exists or when callset quality outranks turnaround.

```bash
# dipcall needs two haplotype assemblies (hap1/hap2) plus minimap2/k8/htsbox on PATH.
run-dipcall prefix reference.fa hap1.fa hap2.fa > prefix.mak
make -j2 -f prefix.mak                                          # emits prefix.dip.vcf.gz + prefix.dip.bed
```

## Step 4: Cohort merging (the two-step .snf design)

**Goal:** Build a joint-genotyped multi-sample SV matrix, not a union of per-sample discovery VCFs.

**Approach:** Sniffles2's population design processes each sample independently into a compact `.snf`, then combines the `.snf` files in a second pass - scaling linearly in N. A union of per-sample discovery VCFs is wrong: a sample recorded 0/0 may simply not have had that event *discovered* in it (a false missing), which corrupts allele frequencies. The two-step `.snf` combine force-genotypes every sample at every merged site.

```bash
# Pass 1: per-sample .snf (each sample processed once, independently).
for s in sample1 sample2 sample3; do
    sniffles --input ${s}.bam --reference reference.fa \
        --tandem-repeats human_GRCh38_TR.bed --snf ${s}.snf
done
# Pass 2: combine into a jointly genotyped cohort VCF (linear in N).
sniffles --input sample1.snf sample2.snf sample3.snf --vcf cohort.vcf.gz
```

For sequence-aware AF work across callsets, prefer Truvari `collapse` over position-only merging (position-only mergers inflate allele frequency by up to 2.2x; English 2022) - see variant-calling/structural-variant-calling for the merger decision table.

## Step 5: Benchmarking - an SV F1 is meaningless without its parameters

**Goal:** Report a defensible, reproducible accuracy figure - not a number that looks good because of loose matching.

**Approach:** Truvari `bench` counts a call as a true positive only if it matches a truth variant under ALL of `--refdist`, `--pctsize`, and `--pctseq` simultaneously. Every one of these moves the score, so a bare F1 is uninterpretable. Report the full parameter set, run `truvari refine` for a harmonized re-comparison, and stratify by region.

```bash
# Report EVERY parameter. --pctseq 0 disables alt-sequence checking and quietly inflates INS scores.
truvari bench -b HG002_SV_Tier1.vcf.gz -c svs.vcf.gz -o bench_tier1/ --passonly \
    -f reference.fa --refdist 500 --pctsize 0.70 --pctseq 0.70 --sizemin 50   # -f persists reference to params.json
truvari refine bench_tier1/                                     # harmonized breakpoint re-comparison (needs the reference bench recorded)

# CMRG is NOT optional: Tier 1 EXCLUDES the medically relevant repetitive genes.
truvari bench -b HG002_CMRG_SV.vcf.gz -c svs.vcf.gz -o bench_cmrg/ --passonly \
    --refdist 500 --pctsize 0.70 --pctseq 0.70 --sizemin 50
```

Three escalating bars are routinely conflated, and a pipeline can pass the first while failing the ones that matter:

- Event detection - something of about the right type/size near the right place (loose refdist, no sequence check). Easy.
- Breakpoint accuracy - POS/END within a few bp (tight `--refdist`, `--pctseq` on). Matters at exon/splice boundaries.
- Genotype accuracy - the sample GT (het/hom) is correct (genotype-aware comparison). A caller can detect an event perfectly and still call het-as-hom, which is fatal for Mendelian analyses.

Region stratification is decisive: Tier 1 (Zook 2020 *Nat Biotechnol* 38:1347) is conservative isolated SVs, while CMRG (Wagner 2022 *Nat Biotechnol* 40:672) covers the repetitive medically relevant genes Tier 1 leaves out - where GRCh38 false duplications cause reference-specific misses that masking raised from 8% to 100% recall. A good Tier 1 F1 certifies nothing about the genes clinicians care about; run both.

## Filtering and annotation

```bash
bcftools view -i 'QUAL>=20 && ABS(SVLEN)>=50' svs.vcf.gz -Oz -o svs.filtered.vcf.gz
bcftools index svs.filtered.vcf.gz          # ABS() is mandatory: DEL SVLEN is negative by convention
bcftools stats svs.filtered.vcf.gz > sv_stats.txt

AnnotSV -SVinputFile svs.filtered.vcf.gz -genomeBuild GRCh38 -outputFile annotated_svs
# gene overlap, DGV/gnomAD-SV population AF, ClinVar pathogenicity
```

## Phased and methylation-aware SV (bonus channels)

Heterozygous variants on the same long read are physically phased, so SVs can be assigned to haplotypes with no statistical phasing. Haplotag the BAM (whatshap/`sniffles --phase`) before or during calling to get haplotype-resolved SVs; see long-read-sequencing/haplotype-phasing. If methylation was requested at basecall time (Step 0), the MM/ML tags ride through alignment (via minimap2 `-y` / `samtools fastq -T`) and give a per-haplotype methylation channel alongside the SV call at no extra sequencing cost - useful for imprinting and allele-specific silencing, but it must be captured at basecall time or it is gone.

## SV types detected

| Type | ALT | Notes for long reads |
|------|-----|----------------------|
| Deletion | DEL | excellent recall; breakpoints base-precise when a read spans the junction |
| Insertion | INS | the reason to use long reads; the read carries the inserted sequence |
| Duplication | DUP | tandem vs interspersed distinguishable (SVIM reports origin + destination) |
| Inversion | INV | resolved when unique anchors flank the repeat-embedded breakpoints |
| Translocation | BND | paired breakend records linked by MATEID; complex events are BND graphs |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Few SVs / missing known INS | coverage <10x or missing tandem-repeat BED | raise depth to >=15x; pass `--tandem-repeats` |
| Many false positives in repeats | no tandem-repeat BED supplied | provide a reference-matched TR BED (biggest FP lever) |
| `map-ont` on R10 data is slow/less accurate | wrong preset for accurate reads | use `lr:hq` for R10/Q20 ONT; `map-ont` only for R9 |
| Split reads lost breakpoint sequence | aligned without `-Y` (hard-clipped supplementaries) | re-align with `-Y` |
| Methylation channel gone | not requested at basecall time | rebasecall with `--modified-bases`; it is irreversible |
| cuteSV recall poor / no genotypes | ran defaults; `--genotype` off | pass the per-platform param set and `--genotype` |
| Cohort "0/0" wrong, AF too low | took a union of per-sample discovery VCFs | use the two-step `.snf` combine (force-genotypes all sites) |
| `ABS(SVLEN)>=50` filter drops all deletions | filtered raw SVLEN (DEL is negative) | always wrap in `ABS()` |
| Truvari F1 not reproducible / suspiciously high | reported without params, or `--pctseq 0` | state refdist/pctsize/pctseq/sizemin; never disable pctseq to look good |
| Passed Tier 1 but clinical genes fail | benchmarked only on Tier 1 | also run CMRG (Tier 1 excludes those genes) |

## Related Skills

- long-read-sequencing/basecalling - Dorado model choice and requesting methylation at basecall time (Step 0)
- long-read-sequencing/long-read-alignment - minimap2 preset selection, `-Y` soft-clipping, MM/ML tag passthrough
- long-read-sequencing/long-read-qc - read-length/quality QC and chimera screening before alignment
- long-read-sequencing/structural-variants - caller tuning (cuteSV per-platform params, tandem-repeat BED, Truvari) - the SV mechanism for long reads
- long-read-sequencing/haplotype-phasing - haplotag the BAM for phased/somatic SVs
- variant-calling/structural-variant-calling - the SV signal model, SVLEN-sign / symbolic-vs-BND / CIPOS representation, force-genotyping, sequence-aware merging (also short-read SV)
- variant-calling/consensus-sequences - why symbolic `<DEL>`/`<INS>` alleles are not directly consensus-able

## References

- Li H. Minimap2: pairwise alignment for nucleotide sequences. 2018 *Bioinformatics* 34:3094-3100.
- Sedlazeck FJ, Rescheneder P, Smolka M, Fang H, Nattestad M, von Haeseler A, Schatz MC. Accurate detection of complex structural variations using single-molecule sequencing. 2018 *Nature Methods* 15:461-468. (Sniffles v1 + NGMLR)
- Smolka M, Paulin LF, Grochowski CM, Horner DW, Mahmoud M, Behera S, et al. Detection of mosaic and population-level structural variants with Sniffles2. 2024 *Nature Biotechnology*. doi:10.1038/s41587-023-02024-y. (two-step .snf population merge; mosaic SVs)
- Jiang T, Liu Y, Jiang Y, Li J, Gao Y, Cui Z, et al. Long-read-based human genomic structural variation detection with cuteSV. 2020 *Genome Biology* 21:189.
- Heller D, Vingron M. SVIM: structural variant identification using mapped long reads. 2019 *Bioinformatics* 35:2907-2915.
- Li H, Bloom JM, Farjoun Y, Fleharty M, Gauthier L, Neale B, MacArthur D. A synthetic-diploid benchmark for accurate variant-calling evaluation. 2018 *Nature Methods* 15:595-597. (dipcall/syndip)
- Ebert P, Audano PA, Zhu Q, Rodriguez-Martin B, Porubsky D, Bonder MJ, et al. Haplotype-resolved diverse human genomes and integrated analysis of structural variation. 2021 *Science* 372:eabf7117. (PAV; 68% of SVs missed by short reads)
- Keskus AG, et al. Severus detects somatic structural variation and complex rearrangements in cancer genomes using long-read sequencing. 2025 *Nature Biotechnology*. doi:10.1038/s41587-025-02618-8.
- English AC, Menon VK, Gibbs RA, Metcalf GA, Sedlazeck FJ. Truvari: refined structural variant comparison preserves allelic diversity. 2022 *Genome Biology* 23:271. (defaults refdist 500, pctsize 0.70, pctseq 0.70, sizemin 50; up to 2.2x AF inflation from position-only merging)
- Zook JM, Hansen NF, Olson ND, Chapman L, Mullikin JC, Xiao C, et al. A robust benchmark for detection of germline large deletions and insertions. 2020 *Nature Biotechnology* 38:1347-1355. (GIAB HG002 SV Tier 1)
- Wagner J, Olson ND, Harris L, McDaniel J, Cheng H, Fungtammasan A, et al. Curated variation benchmarks for challenging medically relevant autosomal genes. 2022 *Nature Biotechnology* 40:672-680. (GIAB-CMRG; false-duplication masking raises recall 8%->100%)
- pbsv - PacBio structural variant caller (no dedicated publication): github.com/PacificBiosciences/pbsv
<!-- END FILE: workflows/longread-sv-pipeline/SKILL.md -->

## 子目录：workflows/merip-pipeline

<!-- BEGIN FILE: workflows/merip-pipeline/SKILL.md -->
---
name: bio-workflows-merip-pipeline
description: Orchestrates an end-to-end MeRIP-seq / m6A-seq analysis from raw FASTQ to differential m6A peak calls and metagene plots, chaining fastp adapter trimming, STAR splice-aware alignment (NO deduplication for non-UMI MeRIP), deepTools replicate-concordance + IP-enrichment QC, PreSeq saturation curves, exomePeak2 (transcript-aware, GC-bias-aware negative-binomial GLM) peak calling, optional MACS3 broad-peak cross-check, DRACH motif confirmation as a sanity check (NOT a per-peak filter), exomePeak2 differential calling via the four-BAM-vector interface (bam_ip + bam_input control; bam_treated_ip + bam_treated_input treatment), ChIPseeker annotation, and the canonical Guitar metagene with stop-codon enrichment as the biological QC anchor. Use when running a complete MeRIP analysis from raw reads, when chaining the constituent epitranscriptomics skills (merip-preprocessing -> m6a-peak-calling -> m6a-differential -> modification-visualization), or when wrapping the pipeline in Snakemake / Nextflow.
tool_type: mixed
primary_tool: exomePeak2
workflow: true
depends_on:
  - read-qc/fastp-workflow
  - read-alignment/star-alignment
  - epitranscriptomics/merip-preprocessing
  - epitranscriptomics/m6a-peak-calling
  - epitranscriptomics/m6a-differential
  - epitranscriptomics/modification-visualization
qc_checkpoints:
  - after_align: "Properly-paired >=85%; NO deduplication for non-UMI MeRIP"
  - after_qc: "Replicate Spearman >=0.85 IP-IP (10kb bins); plotFingerprint IP-vs-input JS >=0.5"
  - after_peaks: "DRACH enrichment P-value <1e-50 on the peak SET (sanity check, never a per-peak filter)"
  - after_metagene: "Guitar metagene shows the stop-codon/3'UTR-proximal peak; else STOP (IP failure)"
---

## Version Compatibility

Reference examples tested with: STAR 2.7.11+, samtools 1.19+, fastp 0.23+, deepTools 3.5+, PreSeq 3.2+, exomePeak2 1.14.x (Bioconductor 3.18 ONLY -- deprecated in Bioc 3.19, removed in 3.20; on current Bioc install from the Bioc 3.18 archive or use a successor), MACS3 3.0+, ChIPseeker 1.38+, Guitar 2.18+, BSgenome.Hsapiens.UCSC.hg38 1.4+, TxDb.Hsapiens.UCSC.hg38.knownGene 3.18+, HOMER 4.11+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

exomePeak2 has NO `mode=` or `experiment_design=` argument; differential is triggered by populating `bam_treated_ip` + `bam_treated_input`. MeTPeak defaults are `WINDOW_WIDTH=50, SLIDING_STEP=50, FRAGMENT_LENGTH=100`. MACS3 default `--keep-dup` is 1 and MUST be overridden to `all` for non-UMI MeRIP. Guitar `txTxdb=` is the modern argument name (older releases used `txdb=`).

# MeRIP-seq End-to-End Pipeline

**"Analyze my MeRIP-seq data from FASTQ to differential m6A peaks"** -> Orchestrate read alignment (STAR splice-aware to GENOME), IP-enrichment QC (deepTools plotFingerprint, replicate Spearman, PreSeq saturation), m6A peak calling (exomePeak2 transcript-aware default, MACS3 broad as cross-check), DRACH motif sanity check (HOMER), exomePeak2 differential via the four-BAM-vector interface, ChIPseeker feature annotation, and Guitar transcript-feature metagene confirming canonical stop-codon enrichment. Defer per-skill deep treatment to `epitranscriptomics/merip-preprocessing`, `epitranscriptomics/m6a-peak-calling`, `epitranscriptomics/m6a-differential`, and `epitranscriptomics/modification-visualization`.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

MeRIP-seq inverts several DNA-pipeline reflexes; the trustworthy callset is decided at these seams.

1. **Do NOT deduplicate non-UMI MeRIP — duplicates are signal, not artifact.** A highly methylated, highly expressed transcript legitimately produces many identical fragments; removing them (or MACS3 default `--keep-dup 1`) erases the strongest m6A peaks. Keep all reads (`--keep-dup all`); only dedup when a UMI is present.
2. **Enrichment is IP-vs-Input, and differential is a FOUR-BAM comparison.** Every condition needs its own IP AND Input. exomePeak2 has no `mode=`/`experiment_design=` argument; differential is triggered simply by populating `bam_treated_ip` + `bam_treated_input` alongside the control `bam_ip` + `bam_input`.
3. **DRACH is a peak-SET sanity check, never a per-peak filter.** Confirm the motif is enriched across the whole peak set (P-value < 1e-50); post-hoc dropping individual peaks that lack a DRACH match discards real non-canonical sites and biases the callset.
4. **The Guitar stop-codon metagene is the biological go/no-go.** m6A concentrates near the stop codon / 3'UTR-proximal CDS end; if that enrichment is absent, the IP failed or the antibody is wrong — STOP, do not interpret downstream. And before comparing peak COUNTS across conditions, rarefy BAMs to a common unique-read depth (peak number scales with depth).

## Pipeline Overview

```
FASTQ -> fastp trim -> STAR genome align -> samtools sort/index -> deepTools QC + PreSeq saturation
       -> exomePeak2 peak calling (+ MeTPeak / MACS3 cross-check)
       -> HOMER DRACH sanity check
       -> exomePeak2 differential (bam_ip + bam_treated_ip)
       -> ChIPseeker feature annotation
       -> Guitar metagene (stop-codon QC anchor) + pyGenomeTracks browser figures
```

## Step 1: Adapter Trimming

```bash
fastp \
    --in1 raw/IP_R1.fastq.gz --in2 raw/IP_R2.fastq.gz \
    --out1 trimmed/IP_R1.fq.gz --out2 trimmed/IP_R2.fq.gz \
    --json qc/IP_fastp.json --html qc/IP_fastp.html \
    --length_required 25 --detect_adapter_for_pe --thread 8

fastp \
    --in1 raw/Input_R1.fastq.gz --in2 raw/Input_R2.fastq.gz \
    --out1 trimmed/Input_R1.fq.gz --out2 trimmed/Input_R2.fq.gz \
    --json qc/Input_fastp.json --html qc/Input_fastp.html \
    --length_required 25 --detect_adapter_for_pe --thread 8
```

Standard non-UMI MeRIP: do NOT pass `--umi`. See `epitranscriptomics/merip-preprocessing` for the do-NOT-dedup rationale.

## Step 2: STAR Splice-Aware Genome Alignment

```bash
STAR --runMode alignReads \
    --genomeDir refs/star_index \
    --readFilesIn trimmed/IP_R1.fq.gz trimmed/IP_R2.fq.gz \
    --readFilesCommand zcat \
    --outSAMtype BAM SortedByCoordinate \
    --outFilterMultimapNmax 20 \
    --outSAMattributes NH HI AS nM NM MD \
    --outFileNamePrefix aligned/IP_rep1_ \
    --runThreadN 12

samtools index aligned/IP_rep1_Aligned.sortedByCoord.out.bam
ln -sf IP_rep1_Aligned.sortedByCoord.out.bam aligned/IP_rep1.bam     # downstream QC/peak steps consume the short ${sample}_rep${n}.bam name
ln -sf IP_rep1_Aligned.sortedByCoord.out.bam.bai aligned/IP_rep1.bam.bai
```

Repeat for each IP and Input replicate. Align to GENOME (not transcriptome) for downstream MeRIP peak calling. Do NOT deduplicate (no UMI in standard MeRIP).

## Step 3: IP-Enrichment + Replicate-Concordance QC

```bash
multiBamSummary bins \
    --bamfiles aligned/IP_rep[0-9].bam aligned/Input_rep[0-9].bam \
    --binSize 10000 --numberOfProcessors 8 \
    -o qc/cov.npz

plotCorrelation --corData qc/cov.npz --corMethod spearman --skipZeros \
    --whatToPlot heatmap --colorMap RdYlBu_r --plotNumbers \
    -o qc/replicate_correlation.pdf

plotFingerprint \
    --bamfiles aligned/IP_rep[0-9].bam aligned/Input_rep[0-9].bam \
    --skipZeros --numberOfProcessors 8 \
    --JSDsample aligned/Input_rep1.bam \
    --outQualityMetrics qc/fingerprint_metrics.tab \
    -o qc/fingerprint.pdf

preseq lc_extrap -B -o qc/IP_rep1_lc_extrap.txt aligned/IP_rep1.bam
```

For peak-count comparison across conditions, rarefy BAMs to a common unique-read depth informed by the saturation curve before calling peaks.

## Step 4: exomePeak2 Peak Calling (Per-Condition)

**Goal:** Produce a transcript-aware set of m6A peaks with FDR and IP/input fold-change from paired IP/Input genome BAM files, suitable as input to differential analysis, motif scanning, or downstream visualisation.

**Approach:** Build a TxDb from the matched GTF; pass paired IP/Input BAM vectors to `exomePeak2()` with `txdb` and `genome` (BSgenome) for GC correction; export BED12 + RDS to `save_dir/`.

```r
library(exomePeak2)
library(GenomicFeatures)
library(BSgenome.Hsapiens.UCSC.hg38)

txdb <- makeTxDbFromGFF('refs/annotation.gtf', format='gtf')

result <- exomePeak2(
    bam_ip       = c('aligned/IP_rep1.bam', 'aligned/IP_rep2.bam', 'aligned/IP_rep3.bam'),
    bam_input    = c('aligned/Input_rep1.bam', 'aligned/Input_rep2.bam', 'aligned/Input_rep3.bam'),
    txdb         = txdb,
    bsgenome     = BSgenome.Hsapiens.UCSC.hg38,   # bsgenome= (a BSgenome object) for GC correction; genome= would be the UCSC string 'hg38'
    paired_end   = TRUE,
    library_type = 'unstranded',
    save_dir     = 'exomePeak2_output'            # no experiment_name arg; output goes straight under save_dir/
)

peaks <- result
nrow(peaks)   # SummarizedExomePeak has no length method (would return 1); nrow = peak count
```

`exomePeak2()` writes fixed filenames under `save_dir/`: `Mod.bed` (BED12 peaks), `Mod.csv` (per-peak fold-change / FDR), `Mod.rds`.

## Step 5: MACS3 Broad-Peak Cross-Check (Optional)

```bash
macs3 callpeak \
    --treatment aligned/IP_rep[0-9].bam \
    --control aligned/Input_rep[0-9].bam \
    --format BAMPE --gsize hs \
    --nomodel --extsize 150 \
    --keep-dup all \
    --broad --broad-cutoff 0.1 --qvalue 0.05 \
    --outdir macs3_output --name m6a_run1
```

`--keep-dup all` is non-negotiable for non-UMI MeRIP (default `--keep-dup 1` destroys signal at high-coverage transcripts).

## Step 6: DRACH Motif Sanity Check

```bash
findMotifsGenome.pl \
    exomePeak2_output/Mod.bed \
    hg38 motif_output \
    -rna -size 100 -len 5,6 -p 8
```

Report DRACH enrichment on the peak set as a sanity check (P-value < 1e-50 expected). NEVER post-hoc filter individual peaks by DRACH.

## Step 7: exomePeak2 Differential (Control vs Treatment)

**Goal:** Identify m6A peaks that change between control and treatment conditions, with per-peak log2FC + FDR, using exomePeak2's integrated peak-calling + differential interface.

**Approach:** Populate `bam_ip` + `bam_input` with the control arm and `bam_treated_ip` + `bam_treated_input` with the treatment arm; populating the treated arms triggers differential mode (there is NO `mode=` argument). Apply effect-size + FDR filters downstream.

```r
library(exomePeak2)
library(GenomicFeatures)
library(BSgenome.Hsapiens.UCSC.hg38)

txdb <- makeTxDbFromGFF('refs/annotation.gtf', format='gtf')

ctrl_ip     <- c('aligned/ctrl_IP1.bam', 'aligned/ctrl_IP2.bam', 'aligned/ctrl_IP3.bam')
ctrl_input  <- c('aligned/ctrl_Input1.bam', 'aligned/ctrl_Input2.bam', 'aligned/ctrl_Input3.bam')
treat_ip    <- c('aligned/treat_IP1.bam', 'aligned/treat_IP2.bam', 'aligned/treat_IP3.bam')
treat_input <- c('aligned/treat_Input1.bam', 'aligned/treat_Input2.bam', 'aligned/treat_Input3.bam')

diff_result <- exomePeak2(
    bam_ip            = ctrl_ip,
    bam_input         = ctrl_input,
    bam_treated_ip    = treat_ip,
    bam_treated_input = treat_input,
    txdb              = txdb,
    bsgenome          = BSgenome.Hsapiens.UCSC.hg38,   # bsgenome=, not genome=
    paired_end        = TRUE,
    library_type      = 'unstranded',
    peak_calling_mode = 'exon',
    save_dir          = 'exomePeak2_diff_output'       # writes DiffMod.bed / DiffMod.csv; no experiment_name arg
)

diff_table <- Results(diff_result)   # SummarizedExomePeak has no as.data.frame method; Results() returns the data.frame
# differential effect-size column is DiffModLog2FC (not log2FC)
sig <- diff_table[diff_table$padj < 0.05 & abs(diff_table$DiffModLog2FC) > 0.5, ]
nrow(sig)
```

exomePeak2 has NO `mode=` or `experiment_design=` argument. Populating `bam_treated_ip` + `bam_treated_input` triggers differential output. For batch / antibody-lot covariate adjustment, fall through to featureCounts-on-peaks -> DESeq2 (see `epitranscriptomics/m6a-differential`).

## Step 8: Peak Annotation to Transcript Features

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(rtracklayer)

peaks <- import('exomePeak2_output/Mod.bed')
anno <- annotatePeak(peaks, TxDb=TxDb.Hsapiens.UCSC.hg38.knownGene, level='transcript')
plotAnnoBar(anno)
plotDistToTSS(anno)
```

Flag peaks within ~50 nt of TSS as m6A-or-m6Am ambiguous (antibody cross-reactivity with PCIF1-deposited cap m6Am).

## Step 9: Guitar Metagene (Biological QC Anchor)

```r
library(Guitar)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

GuitarPlot(
    txTxdb          = TxDb.Hsapiens.UCSC.hg38.knownGene,
    stBedFiles      = list('exomePeak2_output/Mod.bed'),
    miscOutFilePrefix = 'figures/m6a_metagene'
)
```

Expected pattern: peak density rises toward and peaks near the stop codon (3'UTR-proximal end of CDS). If absent, suspect IP failure or wrong antibody; do NOT proceed to downstream interpretation.

## Complete Bash Driver

```bash
#!/usr/bin/env bash
set -euo pipefail

STAR_INDEX=$1
GTF=$2
IP_R1=$3
IP_R2=$4
INPUT_R1=$5
INPUT_R2=$6
OUTPUT_DIR=$7

mkdir -p "${OUTPUT_DIR}"/{qc,trimmed,aligned,peaks,figures}

fastp --in1 "${IP_R1}" --in2 "${IP_R2}" \
    --out1 "${OUTPUT_DIR}/trimmed/IP_R1.fq.gz" --out2 "${OUTPUT_DIR}/trimmed/IP_R2.fq.gz" \
    --json "${OUTPUT_DIR}/qc/IP_fastp.json" --length_required 25 --detect_adapter_for_pe --thread 8

fastp --in1 "${INPUT_R1}" --in2 "${INPUT_R2}" \
    --out1 "${OUTPUT_DIR}/trimmed/Input_R1.fq.gz" --out2 "${OUTPUT_DIR}/trimmed/Input_R2.fq.gz" \
    --json "${OUTPUT_DIR}/qc/Input_fastp.json" --length_required 25 --detect_adapter_for_pe --thread 8

for sample in IP Input; do
    STAR --runMode alignReads --genomeDir "${STAR_INDEX}" \
        --readFilesIn "${OUTPUT_DIR}/trimmed/${sample}_R1.fq.gz" "${OUTPUT_DIR}/trimmed/${sample}_R2.fq.gz" \
        --readFilesCommand zcat --outSAMtype BAM SortedByCoordinate \
        --outFilterMultimapNmax 20 \
        --outFileNamePrefix "${OUTPUT_DIR}/aligned/${sample}_" --runThreadN 12
    samtools index "${OUTPUT_DIR}/aligned/${sample}_Aligned.sortedByCoord.out.bam"
done

macs3 callpeak \
    --treatment "${OUTPUT_DIR}/aligned/IP_Aligned.sortedByCoord.out.bam" \
    --control "${OUTPUT_DIR}/aligned/Input_Aligned.sortedByCoord.out.bam" \
    --format BAMPE --gsize hs --nomodel --extsize 150 --keep-dup all \
    --broad --broad-cutoff 0.1 --qvalue 0.05 \
    --outdir "${OUTPUT_DIR}/peaks" --name m6a
```

The full pipeline (incl. exomePeak2 peak calling, DRACH check, ChIPseeker annotation, Guitar metagene) is best orchestrated in Snakemake or Nextflow with the per-skill recipes from the four `epitranscriptomics/` skills.

## QC Checkpoints

| Checkpoint | Expected | Action if Failed |
|------------|----------|------------------|
| Properly-paired rate (samtools flagstat) | >=85% | Check trimming and adapter contamination |
| Replicate Spearman within condition (10 kb bins) | >=0.85 IP-IP | Inspect divergent replicate; consider exclusion |
| plotFingerprint IP-vs-input JS distance | >=0.5 | Suspect failed IP if lower |
| Saturation plateau depth | ~30-60M unique reads | Sequence deeper if not plateaued |
| DRACH motif enrichment (HOMER, peak set) | P-value < 1e-50 | Suspect IP failure or wrong antibody |
| Stop-codon enrichment in Guitar metagene | Clear 3'UTR-proximal peak | Suspect IP failure, wrong antibody, or non-m6A modification |
| 5'UTR peaks fraction | Note ambiguity zone (~50 nt of TSS) | Flag as m6A-or-m6Am ambiguous; PCIF1 cross-reactivity |

## Output Files

| File | Description |
|------|-------------|
| `exomePeak2_output/Mod.bed` | exomePeak2 peak BED12 |
| `exomePeak2_diff_output/DiffMod.bed` | Differential peaks with log2FC + FDR |
| `motif_output/` | HOMER DRACH motif enrichment report |
| `figures/m6a_metagene.pdf` | Guitar transcript-feature metagene (stop-codon QC anchor) |
| `qc/replicate_correlation.pdf` | deepTools Spearman heatmap |
| `qc/fingerprint.pdf` | deepTools Lorenz IP-enrichment plot |
| `qc/IP_rep*_lc_extrap.txt` | PreSeq saturation curves |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Strongest m6A peaks (high-expression transcripts) vanish | Deduplicated non-UMI MeRIP, or MACS3 default `--keep-dup 1` | Keep all reads (`--keep-dup all`); never dedup non-UMI MeRIP |
| exomePeak2 runs but gives no differential output | Expected a `mode=`/`experiment_design=` argument | Populate `bam_treated_ip` + `bam_treated_input` to trigger differential |
| Real non-canonical m6A sites lost | Filtered individual peaks by DRACH presence | DRACH is a peak-SET sanity check (E<1e-50), never a per-peak filter |
| Peak counts "differ" between conditions but it's depth | Compared raw peak numbers at unequal depth | Rarefy BAMs to a common unique-read depth before cross-condition counts |
| No stop-codon enrichment in the metagene | IP failure, wrong antibody, or non-m6A signal | STOP; do not interpret downstream (Guitar go/no-go) |
| 5'UTR peaks over-interpreted as m6A | Antibody cross-reacts with cap-adjacent m6Am (PCIF1) | Flag peaks within ~50 nt of TSS as m6A-or-m6Am ambiguous |

## References

- Dominissini D, Moshitch-Moshkovitz S, Schwartz S, et al (2012) Topology of the human and mouse m6A RNA methylomes revealed by m6A-seq. *Nature* 485:201-206. DOI 10.1038/nature11112. (MeRIP/m6A-seq; stop-codon enrichment.)
- Meyer KD, Saletore Y, Zumbo P, et al (2012) Comprehensive analysis of mRNA methylation reveals enrichment in 3' UTRs and near stop codons. *Cell* 149:1635-1646. DOI 10.1016/j.cell.2012.05.003.
- Meng J, Lu Z, Liu H, et al (2014) A protocol for RNA methylation differential analysis with MeRIP-Seq data and the exomePeak R/Bioconductor package. *Methods* 69:274-281. DOI 10.1016/j.ymeth.2014.06.008. (exome-based peak calling.)
- Cui X, Wei Z, Zhang L, et al (2016) Guitar: an R/Bioconductor package for gene annotation guided transcriptomic analysis of RNA-related genomic features. *BioMed Research International* 2016:8367534. DOI 10.1155/2016/8367534. (transcript-feature metagene.)

## Related Skills

- epitranscriptomics/merip-preprocessing - Per-step preprocessing (trim, align, QC, saturation, IP-over-Input bigWig)
- epitranscriptomics/m6a-peak-calling - exomePeak2 / MeTPeak / MACS3 deep treatment, DRACH sanity check, m6A-vs-m6Am 5'UTR flag
- epitranscriptomics/m6a-differential - Differential methods (exomePeak2, QNB, RADAR), batch / lot covariate handling, stoichiometry-vs-expression confound
- epitranscriptomics/modification-visualization - Guitar metagene, peak-centred heatmaps, pyGenomeTracks browser figures
- epitranscriptomics/m6anet-analysis - ONT direct-RNA alternative for orthogonal stoichiometry validation
- chip-seq/peak-calling - Sibling IP-vs-input peak-calling framework
- chip-seq/chipseq-qc - IP enrichment QC concepts that transfer to MeRIP
- read-alignment/star-alignment - General STAR splice-aware alignment
- workflow-management/snakemake-workflows - Snakemake orchestration patterns
- workflow-management/nextflow-pipelines - Nextflow orchestration patterns
- workflows/rnaseq-to-de - General RNA-seq -> DE pipeline patterns
<!-- END FILE: workflows/merip-pipeline/SKILL.md -->

## 子目录：workflows/metabolic-modeling-pipeline

<!-- BEGIN FILE: workflows/metabolic-modeling-pipeline/SKILL.md -->
---
name: bio-workflows-metabolic-modeling-pipeline
description: Orchestrates genome-scale metabolic modeling from a protein FASTA to flux predictions, chaining CarveMe/gapseq reconstruction, memote QC, gap-filling, media-constrained FBA/FVA, gene essentiality, and context-specific models. Use when committing the reconstruction tool (which locks the identifier NAMESPACE forever - BiGG vs ModelSEED vs KEGG, no automatic translation), setting the medium BEFORE FBA (the exchange bounds ARE the medium; essentiality and gap-fill are computed relative to it), curating iteratively (stoichiometric-consistency first, then mass/charge, then directionality, then GPR) with energy-generating-cycle removal, and reading a MEMOTE score as well-formedness NOT correctness. Hands mechanism to the systems-biology component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: cobrapy
goal_approach_exempt: true
workflow: true
depends_on:
  - systems-biology/metabolic-reconstruction
  - systems-biology/model-curation
  - systems-biology/flux-balance-analysis
  - systems-biology/gene-essentiality
  - systems-biology/context-specific-models
qc_checkpoints:
  - after_reconstruction: "Reactions 1000-2500, growth >0.01 on target media"
  - after_curation: "Memote score >50%, <5% orphan reactions"
  - after_fba: "Realistic growth rate, major pathways active"
  - after_essentiality: "Core essential genes match literature >70%"
---

## Version Compatibility

Reference examples tested with: COBRApy 0.29+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, seaborn 0.13+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metabolic Modeling Pipeline

**"Build and analyze a metabolic model for my organism"** -> Orchestrate CarveMe reconstruction, memote quality scoring, gap-filling, FBA/FVA flux analysis, gene essentiality prediction, and context-specific model building from expression data.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

An automated reconstruction is a HYPOTHESIS about metabolism, not a finished model — the tool does only stage 1 of a four-stage process (Thiele & Palsson) and makes a 30-second draft look finished. Three commitments are made before flux ever means anything, and a high MEMOTE score does NOT certify any of them.

1. **The reconstruction tool locks the identifier NAMESPACE forever.** D-glucose is `glc__D_c` (BiGG, CarveMe) = `cpd00027_c0` (ModelSEED, gapseq) = `C00031` (KEGG). Mixing namespaces (merging a BiGG CarveMe model with a ModelSEED gapseq model) is a silent, error-free failure: metabolites fail to string-match, producing duplicated metabolites, disconnected reactions, and wrong growth. MetaNetX/MNXref is the required, non-automatic reconciliation layer before ANY cross-tool merge.
2. **The medium IS the model, and it is set before FBA means anything.** The exchange-reaction bounds (`EX_*_e` lower bounds = uptake) define what the cell can do; FBA on a wrong/default medium invalidates everything, and gap-fill + essentiality are computed RELATIVE to the medium (a biosynthetic gene is essential in minimal, non-essential in rich). The in-silico medium must match the wet-lab condition being validated against.
3. **The biomass objective function drives every flux and every knockout call.** The BOF is a gene-less pseudo-reaction whose flux = growth rate; copying E. coli biomass into a non-model organism carries the wrong physiology. Two ATP-maintenance terms both matter (GAM inside biomass; NGAM as a separate `ATPM` with a fixed floor — `ATPM` lower bound = 0 is a red flag).
4. **MEMOTE 95% is well-formedness, not correctness.** It scores stoichiometric consistency + annotation coverage + SBO, and is partly gameable; the predictive tests (energy-generating-cycle sweep, essentiality, Biolog) are NOT in the scored total. A 95% model can still make ATP from nothing.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Reconstruction tool = namespace (BiGG/ModelSEED/KEGG) | Every metabolite ID; a cross-namespace merge silently duplicates metabolites and breaks growth |
| Input = protein FASTA with genes split (CarveMe) vs genome FASTA (gapseq) | Whether the reconstruction runs at all; feeding a raw assembly to CarveMe is the classic trap |
| Medium (exchange bounds) | What the cell can do; gap-fill and essentiality are computed relative to it |
| Biomass objective function + GAM/NGAM | Every flux and knockout call; a foreign or zero-ATPM BOF invalidates essentiality |

## Workflow Overview

```
Protein FASTA (genome annotation)
        |
        v
[1. Reconstruction] --> CarveMe / gapseq / ModelSEED
        |
        v
[2. Model Validation] --> memote QC (snapshot report)
        |
        v
[3. Model Curation] --> gap-filling, mass/charge balance
        |
        | <---- Iterative refinement loop
        v
[4. FBA Analysis] --> Growth prediction, flux distribution
        |
        +-----------------------+
        |                       |
        v                       v
[5a. Gene Essentiality]   [5b. Context-Specific]
    Single/double KO       Tissue-specific models
        |                       |
        v                       v
Essential Gene List      Condition-Specific Fluxes
```

## Prerequisites

```bash
pip install cobra carveme memote escher pandas numpy matplotlib seaborn

conda install -c bioconda diamond
```

CarveMe's MILP carving needs a commercial solver (CPLEX or Gurobi, both free for academics) via `reframed` (CarveMe 1.5+ depends on reframed, the refactored `framed`) — the #1 install pain; the open SCIP fallback is far slower. gapseq (GLPK default) is the solver-free reconstruction alternative.

**Required data:**
- Protein FASTA file from genome annotation
- BiGG universal model (downloaded by CarveMe)

## Primary Path: Bacterial Model from Genome

### Step 1: Automated Reconstruction with CarveMe

```bash
# Basic reconstruction from a PROTEIN FASTA (CarveMe rejects raw/GenBank genomes)
carve genome.faa -o model_draft.xml

# Gram type / universe is a VALUE of -u/--universe, NOT a --gram-neg flag
carve genome.faa -o model_draft.xml -u gramneg

# Gap-fill for a specific medium (opt-in; the medium determines what gets added)
carve genome.faa -o model_draft.xml -u gramneg --gapfill M9
```

```python
import cobra

model = cobra.io.read_sbml_model('model_draft.xml')
print(f'Model: {model.id}')
print(f'Reactions: {len(model.reactions)}')
print(f'Metabolites: {len(model.metabolites)}')
print(f'Genes: {len(model.genes)}')

# Quick growth test
# Growth rate >0.01 h^-1 indicates viable model
solution = model.optimize()
print(f'Growth rate: {solution.objective_value:.4f} h^-1')
```

### Step 2: Model Validation with Memote

```bash
# Run the memote test suite (results stored as JSON when --filename is given)
memote run --filename model_result.json.gz model_draft.xml

# Generate the human-readable HTML snapshot report
memote report snapshot --filename model_report.html model_draft.xml
```

```python
# The memote SCORE measures consistency and annotation (well-formedness), NOT biological
# correctness -- a model can score high and mispredict every knockout. Read WHICH tests fail
# (stoichiometric consistency, mass/charge balance, energy-generating cycles) in the HTML report,
# and validate predictions separately (see systems-biology/model-curation). Programmatic access:
from memote.suite.api import test_model
code, result = test_model(model, results=True)   # result is a MemoteResult of the raw outcomes
```

### Step 3: Model Curation (Iterative)

Curation order matters and the steps interact: fix stoichiometric consistency FIRST (unconserved metabolites poison everything), then per-reaction mass/charge balance, then directionality, then GPR. Gap-filling can break a balance and an energy-generating-cycle fix frequently unmasks a SECOND nested EGC, so re-run memote + the EGC sweep + a growth check after every change. Mechanism lives in systems-biology/model-curation.

```python
import cobra
from cobra.flux_analysis import gapfill

model = cobra.io.read_sbml_model('model_draft.xml')

# Check for common issues
def diagnose_model(model):
    issues = []

    # Dead-end metabolites (produced but not consumed, or vice versa)
    for met in model.metabolites:
        producing = [r for r in met.reactions if met in r.products]
        consuming = [r for r in met.reactions if met in r.reactants]
        if len(producing) > 0 and len(consuming) == 0:
            issues.append(f'Dead-end (not consumed): {met.id}')
        elif len(producing) == 0 and len(consuming) > 0:
            issues.append(f'Dead-end (not produced): {met.id}')

    # Blocked reactions: reactions that CANNOT carry flux under any feasible state. fraction_of_optimum
    # defaults to 1.0, which instead pins growth at the optimum and reports reactions unused by that
    # particular optimal solution -- a different, much larger set. Pass 0 (or use find_blocked_reactions).
    fva = cobra.flux_analysis.flux_variability_analysis(model, fraction_of_optimum=0)
    blocked = fva[(fva['minimum'] == 0) & (fva['maximum'] == 0)]
    if len(blocked) > 0:
        issues.append(f'Blocked reactions: {len(blocked)}')

    return issues

issues = diagnose_model(model)
print(f'Found {len(issues)} issues')
for issue in issues[:10]:
    print(f'  {issue}')
```

```python
# Gap-filling for growth on specific media
from cobra.flux_analysis import gapfill

# Load universal reaction database for gap-filling
universal = cobra.io.read_sbml_model('universal_model.xml')

# Define target medium (e.g., glucose minimal)
target_medium = {
    'EX_glc__D_e': 10,  # Glucose uptake
    'EX_o2_e': 20,       # Oxygen
    'EX_nh4_e': 100,     # Ammonium
    'EX_pi_e': 100,      # Phosphate
    'EX_so4_e': 100,     # Sulfate
}

# Apply medium (model.exchanges yields Reaction objects, not id strings). This is a FULLY DEFINED
# medium: every exchange absent from target_medium is closed, so target_medium must also list the
# trace metals and cofactors biomass requires (Fe, K, Mg, Ca, Zn, ...) or growth is zero. To vary only
# the carbon source instead, layer overrides onto `model.medium` rather than replacing it.
for rxn in model.exchanges:
    rxn.lower_bound = -target_medium[rxn.id] if rxn.id in target_medium else 0  # block other uptakes

# Gap-fill to enable growth
# Gap-filling adds minimal reactions from universal model to enable growth
gapfill_solution = gapfill(model, universal, demand_reactions=False)
print(f'Gap-fill added {len(gapfill_solution[0])} reactions')

# Gap-filled reactions are the LEAST-evidenced part of the model (added to force growth on this
# medium, not because homology supports them) -- flag them low-confidence, do not treat as validated.
for rxn in gapfill_solution[0]:
    model.add_reactions([rxn])
    print(f'  Added (low-confidence): {rxn.id} - {rxn.name}')

# Verify growth
solution = model.optimize()
print(f'Growth after gap-fill: {solution.objective_value:.4f} h^-1')

# Persist the curated model -- downstream steps read model_curated.xml, not the draft
cobra.io.write_sbml_model(model, 'model_curated.xml')
```

### Step 4: Flux Balance Analysis

```python
import cobra
import pandas as pd
import matplotlib.pyplot as plt

model = cobra.io.read_sbml_model('model_curated.xml')

# Basic FBA
solution = model.optimize()
print(f'Objective (growth): {solution.objective_value:.4f} h^-1')
print(f'Status: {solution.status}')

# Get active fluxes
fluxes = solution.fluxes
active_fluxes = fluxes[abs(fluxes) > 1e-6]
print(f'Active reactions: {len(active_fluxes)} / {len(model.reactions)}')

# Key exchange fluxes (uptake/secretion)
exchange_fluxes = fluxes[[r.id for r in model.exchanges]]
significant_exchanges = exchange_fluxes[abs(exchange_fluxes) > 0.1]
print('\nSignificant exchanges:')
print(significant_exchanges.sort_values())
```

```python
# Flux Variability Analysis (FVA)
from cobra.flux_analysis import flux_variability_analysis

# FVA identifies reaction flexibility
# Fraction 0.9 = allow 90% of optimal growth
fva = flux_variability_analysis(model, fraction_of_optimum=0.9)

# Identify rigid vs flexible reactions
fva['range'] = fva['maximum'] - fva['minimum']
rigid = fva[fva['range'] < 1e-6]
flexible = fva[fva['range'] > 1]

print(f'Rigid reactions (fixed flux): {len(rigid)}')
print(f'Flexible reactions: {len(flexible)}')

# Plot flux ranges for key pathways
glycolysis = ['PGI', 'PFK', 'FBA', 'TPI', 'GAPD', 'PGK', 'PGM', 'ENO', 'PYK']
glyc_fva = fva.loc[fva.index.isin(glycolysis)]

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(range(len(glyc_fva)), glyc_fva['maximum'] - glyc_fva['minimum'],
        left=glyc_fva['minimum'], alpha=0.7)
ax.set_yticks(range(len(glyc_fva)))
ax.set_yticklabels(glyc_fva.index)
ax.set_xlabel('Flux range (mmol/gDW/h)')
ax.set_title('Glycolysis Flux Variability')
plt.tight_layout()
plt.savefig('glycolysis_fva.pdf')
```

### Step 5a: Gene Essentiality Prediction

```python
from cobra.flux_analysis import single_gene_deletion, double_gene_deletion

# Single gene knockouts. Result columns: ids (a SET of gene-id strings), growth, status.
single_ko = single_gene_deletion(model)
single_ko['growth_ratio'] = single_ko['growth'] / solution.objective_value

# Essential genes: knockout drops growth below the cutoff (a policy, not a library default).
# Report and sweep the cutoff; match the medium to any experiment being compared. Essentiality
# is model- and medium-relative (see systems-biology/gene-essentiality).
essential = single_ko[single_ko['growth_ratio'] < 0.1]
print(f'Essential genes: {len(essential)} / {len(model.genes)} on this medium')

# ids elements are gene-id STRINGS (a set), so list(s)[0] gives the id -- there is no .id attribute.
essential_list = [list(s)[0] for s in essential['ids']]
with open('essential_genes.txt', 'w') as f:
    f.write('\n'.join(essential_list))
```

```python
# Double gene knockouts (synthetic lethality)
# WARNING: Computationally intensive for large models

# Focus on non-essential genes only (a synthetic lethal needs both singles viable)
non_essential = [g.id for g in model.genes if g.id not in essential_list]

# Run pairwise deletions (positional gene_list1/gene_list2; cap the O(n^2) sweep)
double_ko = double_gene_deletion(model, non_essential[:100], non_essential[:100])

# Synthetic lethality: neither single KO is lethal, but the double KO is
synthetic_lethal = double_ko[double_ko['growth'] < 0.01]
print(f'Synthetic lethal pairs: {len(synthetic_lethal)}')
```

### Step 5b: Context-Specific Models

Use a validated extraction method rather than ad-hoc pruning. COBRApy has no native GIMME/iMAT/INIT; the real Python options are troppo and corda, and the threshold/method choice dominates the result more than the data does. See systems-biology/context-specific-models for the method decision table and the threshold-sensitivity discipline.

```python
# corda is the most turnkey native-Python extraction method.
from corda import CORDA, reaction_confidence

# Translate expression into CORDA confidence classes (-1 absent, 0 unknown, 1 low, 2 med, 3 high)
# through the GPR, then build the context model.
gene_conf = {g.id: 2 for g in model.genes}                       # derive from expression quantiles
rxn_conf = {r.id: reaction_confidence(r, gene_conf) for r in model.reactions}   # corda 0.5+ takes the Reaction object (reads r.gpr); the old GPR-string form was removed
opt = CORDA(model, rxn_conf)
opt.build()
context_model = opt.cobra_model('tissue')
print(f'Context model: {len(context_model.reactions)} reactions')
# Rebuild at 2-3 thresholds and report which reactions are threshold-dependent (hypotheses).
```

## Visualization with Escher

```python
import escher

# Load model and solution
model = cobra.io.read_sbml_model('model_curated.xml')
solution = model.optimize()

# Create Escher map
builder = escher.Builder(
    map_name='e_coli_core.Core metabolism',
    model=model,
    reaction_data=solution.fluxes.to_dict()
)

builder.save_html('flux_map.html')
```

## Parameter Recommendations

| Step | Parameter | Value | Rationale |
|------|-----------|-------|-----------|
| CarveMe | --gapfill | M9 or LB | Match experimental media |
| Memote | score threshold | >50% | Minimum for usable model |
| FBA | solver | gurobi/cplex | Faster than glpk for large models |
| FVA | fraction_of_optimum | 0.9 | 90% allows realistic flexibility |
| Essentiality | growth threshold | 0.1 | Standard 10% of WT growth |
| Context | expression percentile | 25 | Balance specificity vs viability |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Duplicated metabolites, disconnected reactions, wrong growth | Mixed identifier namespaces (BiGG + ModelSEED merge) | Reconcile via MetaNetX/MNXref before any merge; never string-join across namespaces |
| Every yield and essentiality inflated | Energy-generating cycle (free ATP from over-permissive reversibility + gap-fill) | Close exchanges + add ATP demand, confirm max=0; constrain directionality (eQuilibrator dG); EGCs nest, re-test |
| Unrealistic growth rate | Unbounded/wrong uptake | Audit the full boundary set; set `model.medium` (POSITIVE magnitudes) to mirror the assay |
| MEMOTE 95% but predictions wrong | MEMOTE scores well-formedness, not correctness | Treat MEMOTE as a hygiene floor; add EGC + essentiality/Biolog validation (not in the scored total) |
| Extra "essential" genes vs literature | Essentiality reported without stating the medium | In-silico medium = wet-lab medium; report and SWEEP the cutoff (1/2/5/10% WT growth) |
| Gap-filled reactions trusted as real | Gap-fill adds reactions to force growth, not from evidence | Flag low-confidence, keep distinguishable, prioritize for experimental verification |
| No growth | Missing reactions on THIS medium | Gap-fill FOR the specified medium; do not gap-fill to one medium then predict on another |

## References

- Machado D, Andrejev S, Tramontano M, Patil KR (2018) Fast automated reconstruction of genome-scale metabolic models for microbial species and communities. *Nucleic Acids Research* 46:7542-7553. DOI 10.1093/nar/gky537. (CarveMe.)
- Zimmermann J, Kaleta C, Waschina S (2021) gapseq: informed prediction of bacterial metabolic pathways and reconstruction of accurate metabolic models. *Genome Biology* 22:81. DOI 10.1186/s13059-021-02295-1.
- Lieven C, Beber ME, Olivier BG, et al (2020) MEMOTE for standardized genome-scale metabolic model testing. *Nature Biotechnology* 38:272-276. DOI 10.1038/s41587-020-0446-y.
- Thiele I, Palsson BO (2010) A protocol for generating a high-quality genome-scale metabolic reconstruction. *Nature Protocols* 5:93-121. DOI 10.1038/nprot.2009.203. (four-stage reconstruction.)
- Fritzemeier CJ, Hartleb D, Szappanos B, Papp B, Lercher MJ (2017) Erroneous energy-generating cycles in published genome scale metabolic networks: identification and removal. *PLoS Computational Biology* 13:e1005494. DOI 10.1371/journal.pcbi.1005494.

## Output Files

| File | Description |
|------|-------------|
| `model_draft.xml` | Initial reconstruction (SBML) |
| `model_curated.xml` | Gap-filled and validated model |
| `model_report.html` | Memote QC report |
| `essential_genes.txt` | Predicted essential genes |
| `gene_essentiality.tsv` | Full single-gene-deletion table (growth ratio per gene) |
| `fba_fluxes.tsv` | Optimal flux distribution |
| `fva_results.tsv` | Flux variability ranges |
| `model_analysis_summary.pdf` / `.png` | Summary figure (exchanges, FVA, essentiality) |
| `flux_map.html` | Escher visualization |

## Extensions

Beyond the core genome-to-flux path, the model feeds two further analyses: build a multi-species community from several reconstructions (systems-biology/community-metabolic-modeling), or design growth-coupled knockouts to overproduce a target chemical (systems-biology/strain-design).

## Related Skills

- systems-biology/metabolic-reconstruction - CarveMe, gapseq details
- systems-biology/model-curation - Memote, gap-filling, energy-generating-cycle checks
- systems-biology/flux-balance-analysis - FBA, FVA, pFBA, sampling
- systems-biology/gene-essentiality - Single/double knockouts, MOMA/ROOM
- systems-biology/context-specific-models - Tissue-specific models (troppo/corda)
- systems-biology/community-metabolic-modeling - Multi-species community FBA (MICOM/SMETANA)
- systems-biology/strain-design - Growth-coupled knockout design (OptKnock/RobustKnock)
<!-- END FILE: workflows/metabolic-modeling-pipeline/SKILL.md -->

## 子目录：workflows/metabolomics-pipeline

<!-- BEGIN FILE: workflows/metabolomics-pipeline/SKILL.md -->
---
name: bio-workflows-metabolomics-pipeline
description: Orchestrates the untargeted LC-MS metabolomics pipeline end-to-end (xcms 4.x feature extraction, QC/drift/normalization, confidence-stratified annotation, permutation-validated statistics, background-aware pathway mapping), naming what each stage decides and where it silently fails. Use when running a full LC-MS metabolomics study from raw mzML to enriched pathways and needing the honest handoffs between stages. Each stage defers to its component skill for parameters and traps; for stable-isotope flux (a separate branch, not this untargeted flow) see metabolomics/isotope-tracing.
tool_type: r
primary_tool: xcms
workflow: true
depends_on:
  - metabolomics/xcms-preprocessing
  - metabolomics/metabolite-annotation
  - metabolomics/normalization-qc
  - metabolomics/statistical-analysis
  - metabolomics/pathway-mapping
  - metabolomics/lipidomics
  - metabolomics/targeted-analysis
  - metabolomics/msdial-preprocessing
qc_checkpoints:
  - after_extraction: "Feature count plausible after redundancy collapse; EICs of top hits inspect cleanly; is_filled cells tracked"
  - after_drift: "QC RSD DROPS after correction AND biological-sample RSD is unchanged (a rise means the spline absorbed signal)"
  - after_qc_filter: "QC RSD <=20-30%, D-ratio <=0.5, blank ratio >=3-5x, detection rate >=50-80% applied BEFORE imputation"
  - after_stats: "Univariate FDR (BH) AND permutation-validated multivariate (permI>=1000; Q2 high with small pQ2)"
  - after_annotation: "MSI/Schymanski level assigned per compound; only Level 1-2 enter identified-ORA"
  - after_pathway: "Background = assay coverage (identified ORA) OR full feature table (mummichog); PREDICTED vs MEASURED stated"
---

## Version Compatibility

Reference examples tested with: xcms 4.x+ (MsExperiment/XcmsExperiment), pmp 1.14+, ropls 1.34+, MetaboAnalystR 4.0+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

This pipeline is only as honest as its weakest stage: a flawless feature table fed to a too-flexible drift model, or a clean OPLS-DA plot fed to background-free enrichment, produces confident wrong biology. Validate each stage against its own held-out check (QCs, permutation null, assay-coverage background), not against the next stage looking nice.

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metabolomics Pipeline

**"Process my LC-MS metabolomics data end-to-end"** -> Chain xcms feature extraction, QC/normalization, confidence-stratified annotation, validated statistics, and background-aware pathway mapping, treating each stage's output as a hypothesis its component skill scrutinizes.
- R: `readMsExperiment()` -> `findChromPeaks()` -> `groupChromPeaks()` -> `fillChromPeaks()` -> `featureValues()` (xcms), then `QCRSC()`/`pqn_normalisation()` (pmp), `opls()` (ropls), `CalculateOraScore()`/`PerformPSEA()` (MetaboAnalystR)

## The governing principle

An untargeted metabolomics result is only as honest as its weakest seam: a feature table is a PARAMETERIZED HYPOTHESIS, not a measurement; injection-order drift is technical variance collinear with run order that masquerades as biology unless corrected BEFORE stats; and a database name is an MSI Level 4-5 guess until an authentic standard makes it Level 1. Three commitments are fixed at the bench and inherited by everything downstream:

1. **Ionization mode is a mode-lock.** Positive and negative ESI have entirely different adduct chemistries ([M+H]+/[M+Na]+ vs [M-H]-/[M+Cl]-); the mode selects which mass-shift table is legal for every candidate, so annotation and pathway mapping must run against the SAME mode the feature was acquired in, and mixed-mode data must carry a per-feature mode column all the way through.
2. **The annotation-confidence contract gates entry into pathway mapping.** MSI/Schymanski level is a made-once reporting decision: a bare DB hit with no orthogonal MS/MS or RT evidence is Level 4-5, NOT Level 2-3, and feeding tentative IDs into ORA as if confirmed launders uncertainty into a pathway p-value.
3. **The pooled-QC + blank + dilution baseline, fixed at the bench, makes every correction possible.** The pooled QC is the substrate for BOTH drift correction and feature-quality filtering; biological samples MUST be block-randomized in run order (group confounded with order is the unwinnable "original sin"); conditioning injections are excluded from drift modeling.

## What Each Stage Decides and Where the Traps Are

This skill is an orchestrator: it sequences the five component skills and enforces the honest handoffs between them. It does not re-teach each stage's parameters -- those live in the component SKILLs cited per row.

| Stage | The decision it owns | The trap it must not paper over | Defers to |
|---|---|---|---|
| 1. Feature extraction | centWave/grouping/alignment parameters that set the detection floor | A feature table is a parameterized hypothesis; `fillChromPeaks` fabricates intensities; 1 compound = 5-15 features | metabolomics/xcms-preprocessing |
| 2. QC + normalization | drift correction, RSD/D-ratio filtering, dilution normalization, mechanism-aware imputation | Over-correction is invisible to QC RSD; half-min-impute-then-test inflates significance; confounded design is unrescuable | metabolomics/normalization-qc |
| 3. Annotation | the MSI/Schymanski confidence level of every name | A database hit is Level 4-5, not an identification; ambiguous m/z inflates downstream pathways | metabolomics/metabolite-annotation |
| 4. Statistics | univariate FDR + permutation-validated multivariate, reconciled | A clean PLS-DA score plot is the generic output of p>>n; R2 is no evidence; scaling changes conclusions | metabolomics/statistical-analysis |
| 5. Pathway mapping | ORA on IDs vs mummichog on m/z, with an explicit background | The background IS the null; enrichment launders annotation uncertainty into confident biology | metabolomics/pathway-mapping |

## Pipeline Flow

```
raw mzML (centroided)
   |  metabolomics/xcms-preprocessing
   v  readMsExperiment -> findChromPeaks -> adjustRtime -> groupChromPeaks -> fillChromPeaks
features x samples table (+ is_filled flags, mzmed/rtmed)
   |  metabolomics/normalization-qc
   v  blank/detection filter -> within-batch drift (QCRSC) -> RSD/D-ratio filter -> PQN -> mechanism-aware impute
QC-clean, dilution-normalized matrix
   |  split: statistics  AND  annotation (independent axes)
   v
metabolomics/statistical-analysis            metabolomics/metabolite-annotation
permutation-validated hits + univariate FDR  confidence-stratified names (MSI level per feature)
   |                                                |
   +-------------------- join on feature_id --------+
   v  metabolomics/pathway-mapping
identified compounds -> ORA/MSEA   OR   raw m/z (no IDs) -> mummichog/PSEA (background = FULL table)
   v
pathways "consistent with perturbation", conditional on annotations + background
```

Stable-isotope tracing (flux) is a SEPARATE branch off labeled raw data, not a stage of this untargeted flow -- see metabolomics/isotope-tracing.

## Stage 1 -- Feature Extraction (modern xcms 4.x)

**Goal:** Turn centroided mzML into a features-by-samples table, carrying the parameters as part of the result.

**Approach:** Use the `MsExperiment`/`XcmsExperiment` containers with `*Param` objects; align to pooled QC, group AFTER alignment (obiwarp aligns the raw profile directly, so no pre-grouping is needed; the PeakGroups method instead needs group -> align -> regroup because it uses grouped anchor peaks), and treat filled values as imputations. Full parameter rationale (ppm, peakwidth, bw, prefilter) lives in metabolomics/xcms-preprocessing.

```r
library(xcms)
# pd: data.frame, one row per file, with a sample_group column ('QC'/'Control'/'Treatment')
raw <- readMsExperiment(spectraFiles = mzml_files, sampleData = pd)

cwp <- CentWaveParam(ppm = 10, peakwidth = c(2, 20), snthresh = 10,
                     prefilter = c(3, 1000), noise = 1000)   # set from instrument; see xcms-preprocessing
xdata <- findChromPeaks(raw, param = cwp)
xdata <- adjustRtime(xdata, param = ObiwarpParam(binSize = 0.6,
    subset = which(sampleData(xdata)$sample_group == 'QC'), subsetAdjust = 'average'))   # anchor RT alignment on pooled QCs
pdp <- PeakDensityParam(sampleGroups = sampleData(xdata)$sample_group,
                        bw = 5, minFraction = 0.5, binSize = 0.025)
xdata <- groupChromPeaks(xdata, param = pdp)        # group on corrected RT (obiwarp needs no pre-grouping)
xdata <- fillChromPeaks(xdata, param = ChromPeakAreaParam())

feat <- featureValues(xdata, value = 'into')        # features x samples; filled cells are imputations
defs <- featureDefinitions(xdata)                   # mzmed / rtmed per feature, for annotation + mummichog
```

## Stage 2 -- QC, Drift, Normalization (not naive median + half-min)

**Goal:** Filter junk features, flatten injection-order drift, normalize per-sample dilution, and impute by mechanism -- before any test sees the data.

**Approach:** Follow the normalization-qc pipeline order: blank/detection filter -> within-batch drift correction (QCRSC) -> RSD/D-ratio filter -> PQN -> mechanism-aware imputation. Do NOT silently half-min-impute and feed limma; validate drift correction on held-out QCs, not on QC clustering.

```r
library(pmp)
# feature_matrix: features in ROWS, samples in COLUMNS (pmp convention); transpose featureValues output
fm <- t(feat)

filtered <- filter_peaks_by_fraction(fm, classes = sample_class, min_frac = 0.5, qc_label = 'QC')
corrected <- QCRSC(df = filtered, order = injection_order, batch = batch_id,
                   classes = sample_class, spar = 0, minQC = 5, qc_label = 'QC')  # CV-selected spline
rsd_filtered <- filter_peaks_by_rsd(corrected, max_rsd = 30, classes = sample_class, qc_label = 'QC')
normalized <- pqn_normalisation(rsd_filtered, classes = sample_class, qc_label = 'QC')
# Impute only the sparse residual holes, by mechanism (QRILC for MNAR / left-censored); see normalization-qc.
```

Drift correction should lower QC RSD AND leave biological-sample RSD unchanged; if biological RSD rises, the spline absorbed signal. Mechanism-aware imputation (QRILC/GSimp for left-censored zeros) replaces the old half-min step, which collapses imputed-subset variance and inflates false significance.

## Stage 3 -- Annotation Before Claiming IDs

**Goal:** Attach an MSI/Schymanski confidence level to each feature so the pathway stage knows what it is allowed to claim.

**Approach:** Match MS/MS to a library (Level 2a) or run SIRIUS/CSI:FingerID (formula Level 4, structure Level 2b/3); a bare m/z is Level 5. Collapse ion families (CAMERA) first so adducts of one compound are not counted as separate metabolites. Mechanics and thresholds live in metabolomics/metabolite-annotation. Annotation and statistics are independent axes -- run them in parallel and join on feature_id.

## Stage 4 -- Statistics (univariate FDR + validated multivariate)

**Goal:** Decide which metabolites genuinely differ, with neither a score plot nor an unadjusted p-value standing alone.

**Approach:** Transform (if heteroscedastic), pick a scaling explicitly (run >=1 alternative and check the conclusion is not scaling-fragile), run a Welch/Mann-Whitney univariate test with BH FDR, AND a permutation-validated OPLS-DA (`permI >= 1000`), then reconcile the two. Full validation checklist in metabolomics/statistical-analysis.

```r
library(ropls)
# t(normalized): samples x features; group aligned to sample order
group <- factor(sample_info$group[sample_info$group != 'QC'])
oplsda <- opls(t(normalized)[study_samples, ], group, predI = 1, orthoI = NA,
               scaleC = 'pareto', permI = 1000, crossvalI = 7,
               fig.pdfC = 'none', info.txtC = 'none')
summ <- getSummaryDF(oplsda)   # claim licensed only if Q2 high AND pQ2 small; R2Y alone proves nothing
```

Univariate Welch + BH (`p.adjust(method='BH')` in R, `multipletests(method='fdr_bh')` in Python -- neither default is BH) gives the per-feature answer with effect sizes. Features are correlated (adducts, pathways), so collapse to compounds before counting "how many metabolites changed."

## Stage 5 -- Pathway Mapping (the background is the null)

**Goal:** Interpret the differential result in pathway context without laundering annotation uncertainty into confident biology.

**Approach:** Two disjoint entry points. Confidently identified compounds -> ORA/MSEA with an assay-coverage background (NOT all of KEGG). Raw m/z with no IDs -> mummichog/PSEA whose permutation null is sampled from the FULL feature table. Either way, report mapping coverage and the MSI levels of the driving compounds; downgrade claims to "consistent with perturbation." Full method choice and background construction in metabolomics/pathway-mapping.

```r
library(MetaboAnalystR)
# Path A: identified compounds (MSI level 1-2) -> ORA
mSet <- InitDataObjects('conc', 'pathora', FALSE)
mSet <- SetOrganism(mSet, 'hsa')
mSet <- Setup.MapData(mSet, identified_compounds)
mSet <- CrossReferencing(mSet, 'name')
mSet <- CreateMappingResultTable(mSet)              # inspect coverage before trusting any p-value
mSet <- SetKEGG.PathLib(mSet, 'hsa', 'current')
mSet <- SetMetabolomeFilter(mSet, TRUE)             # TRUE = restrict to measured metabolome (the honest background)
mSet <- CalculateOraScore(mSet, 'rbc', 'hyperg')

# Path B: no IDs -> mummichog on the FULL peak table (m/z + p-value + t-score)
# mSet <- InitDataObjects('mass_all', 'mummichog', FALSE)
# mSet <- UpdateInstrumentParameters(mSet, 5.0, 'negative')   # ppm + ionization mode are mandatory
# mSet <- Read.PeakListData(mSet, 'peaks_full.txt')           # ENTIRE table, not significant-only
# mSet <- PerformPSEA(mSet, 'hsa_mfn', 'current', permNum = 1000)
```

## Alternative Front End -- MS-DIAL

When peak detection happens in the MS-DIAL GUI/console (MS2Dec deconvolution, GC-EI, DIA/SWATH), import the alignment-result table and enter the pipeline at Stage 2. The framing is unchanged: the imported table is still a parameterized hypothesis. See metabolomics/msdial-preprocessing for the export-parsing details, then continue with normalization-qc onward.

## QC Checkpoints

Each gate hands off to its component skill when it fails; "refresh" means re-run the upstream stage with revised parameters, not patch the symptom downstream.

| Stage | Keep (pass) | Refresh (fail) -> where |
|---|---|---|
| Feature extraction | EIC + alignment of top hits inspect cleanly; feature count plausible after redundancy collapse | Tune centWave/bw against EIC FWHM -> xcms-preprocessing |
| Drift correction | QC RSD dropped AND biological-sample RSD unchanged; dilution-QC linearity holds | Back off spline span / exclude weak-in-QC features -> normalization-qc |
| QC quality | QC RSD <= 20-30%, D-ratio <= 0.5, blank ratio >= 3-5x | Drop failing features; check instrument/injection -> normalization-qc |
| Missingness | impute only sparse residual holes, by mechanism (no half-min-then-test) | Detection-rate filter before imputing -> normalization-qc |
| PCA / QC clustering | pooled QCs cluster tightly at center; no batch-driven separation | Revisit batch correction / design -> normalization-qc, experimental-design/batch-design |
| Multivariate | Q2 high AND pQ2 small (permI >= 1000); PCA shows the same structure | Do not report a noise-separated score plot -> statistical-analysis |
| Annotation | each reported name carries an MSI level; ion families collapsed | Downgrade Level 3-5 names; do not promote a DB hit -> metabolite-annotation |
| Pathway background | ORA uses assay-coverage background; mummichog uses the FULL table | Set `SetMetabolomeFilter(TRUE)` / supply R_all -> pathway-mapping |

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `could not find function "readMSData"` | Legacy xcms <3 API | Use `readMsExperiment()` + `*Param` verbs (xcms 4.x) |
| `unused argument (ppm = ...)` | Loose args to `findChromPeaks` | Wrap in `CentWaveParam(...)`, pass via `param =` |
| Features on uncorrected RT | Grouped before alignment and never grouped after | Group AFTER `adjustRtime` (obiwarp needs no pre-grouping; PeakGroups alignment needs group -> align -> regroup) |
| Significance explodes after imputation | Half-min impute then test | Mechanism-aware QRILC/GSimp on sparse holes only |
| Clean OPLS-DA plot but it is noise | `permI = 20` (ropls default) | `permI >= 1000`; read `pQ2` from `getSummaryDF` |
| FDR is actually Holm/Holm-Sidak | R `p.adjust` default `'holm'`; statsmodels `'hs'` | Pass BH explicitly |
| Every pathway is significant | ORA on all-of-KEGG / mummichog on significant-only | Assay-coverage background; supply the FULL feature table |

## References

- Smith CA, Want EJ, O'Maille G, Abagyan R, Siuzdak G. 2006. XCMS: processing mass spectrometry data for metabolite profiling using nonlinear peak alignment, matching, and identification. *Anal Chem* 78:779-787.
- Broadhurst D, Goodacre R, Reinke SN, Kuligowski J, Wilson ID, Lewis MR, Dunn WB. 2018. Guidelines and considerations for the use of system suitability and quality control samples in mass spectrometry assays applied in untargeted clinical metabolomic studies. *Metabolomics* 14:72.
- Westerhuis JA, Hoefsloot HCJ, Smit S, Vis DJ, Smilde AK, et al. 2008. Assessment of PLSDA cross validation. *Metabolomics* 4:81-89.
- Schymanski EL, Jeon J, Gulde R, Fenner K, Ruff M, Singer HP, Hollender J. 2014. Identifying small molecules via high resolution mass spectrometry: communicating confidence. *Environ Sci Technol* 48:2097-2098.
- Wieder C, Frainay C, Poupin N, Rodriguez-Mier P, Vinson F, Cooke J, Lai RPJ, Bundy JG, Jourdan F, Ebbels T. 2021. Pathway analysis in metabolomics: recommendations for the use of over-representation analysis. *PLOS Comput Biol* 17(9):e1009105.

## Related Skills

- metabolomics/xcms-preprocessing - Stage 1 feature extraction parameters and the feature-table-as-artifact framing
- metabolomics/normalization-qc - Stage 2 drift correction, RSD/D-ratio filtering, PQN, mechanism-aware imputation
- metabolomics/metabolite-annotation - Stage 3 MSI/Schymanski confidence levels
- metabolomics/statistical-analysis - Stage 4 permutation-validated multivariate and dependence-aware FDR
- metabolomics/pathway-mapping - Stage 5 ORA vs mummichog and background construction
- metabolomics/msdial-preprocessing - Alternative front end entering at Stage 2
- metabolomics/lipidomics - Lipid-specific peak widths and annotation
- metabolomics/targeted-analysis - Absolute quantification branch
- metabolomics/isotope-tracing - Separate stable-isotope flux branch, not a stage of this untargeted pipeline
- multi-omics-integration/mofa-integration - Integrating the feature table with other omics layers
<!-- END FILE: workflows/metabolomics-pipeline/SKILL.md -->

## 子目录：workflows/metagenomics-pipeline

<!-- BEGIN FILE: workflows/metagenomics-pipeline/SKILL.md -->
---
name: bio-workflows-metagenomics-pipeline
description: End-to-end shotgun metagenomics workflow from FASTQ to taxonomic and functional profiles, orchestrating controls/host depletion, Kraken2+Bracken classification, MetaPhlAn marker profiling, and HUMAnN functional profiling. Covers the controls-first ordering, why Kraken2 read counts are not abundances and MetaPhlAn cell fractions do not equal Bracken read fractions, and the consistent-pipeline framing. Use when profiling shotgun metagenomic samples end to end, or chaining classification, abundance, and function. For resistome see metagenomics/amr-detection; for strains see metagenomics/strain-tracking; for assembly see genome-assembly/metagenome-assembly.
tool_type: cli
primary_tool: Kraken2
workflow: true
depends_on:
  - read-qc/fastp-workflow
  - metagenomics/contamination-controls
  - metagenomics/kraken-classification
  - metagenomics/metaphlan-profiling
  - metagenomics/abundance-estimation
  - metagenomics/functional-profiling
  - metagenomics/metagenome-visualization
qc_checkpoints:
  - after_qc: "Q30 >80%, host reads removed"
  - after_classification: "Classification rate >60%, known taxa dominant"
  - after_functional: "Pathway coverage reasonable, unmapped <50%"
---

## Version Compatibility

Reference examples tested with: Bowtie2 2.5.3+, Bracken 2.9+, HUMAnN 3.8+, Kraken2 2.1+, MetaPhlAn 4.1+, fastp 0.23+, samtools 1.19+, matplotlib 3.8+, pandas 2.2+, seaborn 0.13+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metagenomics Pipeline

**"Analyze my metagenomic samples from FASTQ to taxonomic and functional profiles"** -> Orchestrate controls and host depletion, Kraken2/Bracken taxonomic classification, MetaPhlAn profiling, and HUMAnN3 functional analysis - reporting results relative to a consistent pipeline, never as a direct observation of the community.

Complete workflow from metagenomic FASTQ to taxonomic and functional profiles. This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

A taxonomic/functional profile is a position in a choice-chain (extraction -> depletion -> depth -> classifier -> DB -> normalization), never a direct observation; the trustworthy result is decided at these seams.

1. **The reference DB + version is THE inherited commitment.** The Kraken2/GTDB (or standard/RefSeq/UHGG) DB chosen at classification fixes what is detectable — a zero means below-detection OR not-in-DB OR lost-in-extraction OR removed-by-depletion, almost never biological absence. Pin the DB build (version alone moves species/genus calls); match DB to habitat (UHGG for gut); report the CLASSIFIED FRACTION (a low fraction is the tell that the DB is wrong).
2. **Host removal against T2T-CHM13 is a made-once commitment done BEFORE profiling.** Prefer the complete T2T over gapped GRCh38 (which lets human reads masquerade as novel microbes); mask rDNA; discard both mates if either maps host. It is a privacy obligation (leaked human reads are identifiable), not just QC.
3. **Controls-first is a design commitment, not a step added later.** Extraction blanks + a whole-cell mock carried through the WHOLE workflow. NO low-biomass result (skin, BAL, CSF, blood, tissue) is interpretable without blanks + DNA-concentration + decontam; at near-zero biomass the signal IS the kitome (Salter 2014). A blank cannot be retrofitted.
4. **Read-fraction is not cell-fraction, and tools/DBs are not comparable.** Kraken2 read-fraction (genome-size/copy-number biased) and MetaPhlAn cell-fraction must never be merged into one table. Holding tool+DB constant within a study is the only way a comparison measures biology and not the tool.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Reference DB + version + habitat match | What is detectable; a zero is below-detection/not-in-DB, not absence; report classified fraction |
| Host-removal reference (T2T-CHM13) | Human reads masquerading as microbes; a privacy obligation; removed before profiling |
| Controls (blanks + mock) carried through | Whether any low-biomass result is interpretable; the signal IS the kitome without them |
| Extraction method held constant | Extraction bias outweighs much biological signal (Costea 2017); interacts with read-vs-assembly choice |

## Workflow Overview

```
FASTQ files (+ extraction blanks, mock)
    |
    v
[0. QC, Host Removal & Controls] --> fastp + Hostile/Bowtie2(T2T) + blanks/decontam + Nonpareil depth check
    |
    v
[1. Taxonomic Classification]
    |
    +---> Kraken2 (+confidence, +hit-groups) + Bracken -> read fraction
    |
    +---> MetaPhlAn 4 (marker-based, pinned --index) -> cell fraction (NOT comparable to Bracken %)
    |
    v
[2. Functional Profiling] --> HUMAnN (potential, not activity; keep UNMAPPED)
    |
    v
Taxonomic profiles + Pathway abundances (+ AMR/strain via their own skills)
```

## Primary Path: Kraken2 + Bracken + HUMAnN

### Step 0: Quality Control, Host Removal, and Controls

Carry extraction blanks and a mock through the whole workflow; host-deplete against T2T-CHM13; confirm depth with Nonpareil. See metagenomics/contamination-controls for the controls/decontam detail.

```bash
# QC with fastp (trimming mechanics: read-qc/fastp-workflow)
for sample in sample1 sample2 sample3; do
    fastp -i ${sample}_R1.fastq.gz -I ${sample}_R2.fastq.gz \
        -o trimmed/${sample}_R1.fq.gz -O trimmed/${sample}_R2.fq.gz \
        --detect_adapter_for_pe \
        --qualified_quality_phred 20 \
        --length_required 50 \
        --html qc/${sample}_fastp.html
done

# Remove host reads - Hostile with a T2T-CHM13 index removes >99.5% host with low microbial loss.
# Report the reads removed; host depletion can halve usable depth.
for sample in sample1 sample2 sample3; do
    hostile clean --fastq1 trimmed/${sample}_R1.fq.gz --fastq2 trimmed/${sample}_R2.fq.gz \
        --index human-t2t-hla --aligner bowtie2 --output host_removed/
    # hostile names each paired output from its OWN input basename: fastq1 -> {R1}.clean_1.fastq.gz,
    # fastq2 -> {R2}.clean_2.fastq.gz. Rename to the ${sample}_R1/_R2.fq.gz the steps below consume.
    mv host_removed/${sample}_R1.clean_1.fastq.gz host_removed/${sample}_R1.fq.gz
    mv host_removed/${sample}_R2.clean_2.fastq.gz host_removed/${sample}_R2.fq.gz
done
# Then run decontam on the classifier output table using the blanks (contamination-controls),
# and confirm depth adequacy with Nonpareil before interpreting any non-detection.
```

### Step 1A: Kraken2 Classification

```bash
# Classify reads. Raise --confidence above the default 0 to suppress single-k-mer false positives,
# and require >=2 hit groups. The database defines what can be detected.
for sample in sample1 sample2 sample3; do
    kraken2 --db kraken2_db \
        --threads 8 \
        --paired \
        --confidence 0.1 \
        --minimum-hit-groups 2 \
        --report kraken/${sample}.report \
        --output kraken/${sample}.output \
        host_removed/${sample}_R1.fq.gz \
        host_removed/${sample}_R2.fq.gz
done
```

### Step 1B: Bracken Abundance Estimation

```bash
# Estimate species abundance
for sample in sample1 sample2 sample3; do
    bracken -d kraken2_db \
        -i kraken/${sample}.report \
        -o bracken/${sample}.species.txt \
        -r 150 \
        -l S \
        -t 10
done

# Combine samples into abundance matrix
combine_bracken_outputs.py \
    --files bracken/*.species.txt \
    -o bracken/combined_species.txt
```

### Step 1C: Alternative - MetaPhlAn Profiling

```bash
# Profile with MetaPhlAn 4. Pin --index (DB version is a batch variable). MetaPhlAn % is a cell
# fraction - do NOT merge it with Bracken read fractions. In 4.2 --bowtie2out is renamed --mapout.
for sample in sample1 sample2 sample3; do
    metaphlan host_removed/${sample}_R1.fq.gz,host_removed/${sample}_R2.fq.gz \
        --bowtie2out metaphlan/${sample}.bowtie2.bz2 \
        --index mpa_vJun23_CHOCOPhlAnSGB_202403 \
        --input_type fastq \
        --nproc 8 \
        -o metaphlan/${sample}_profile.txt
done

# Merge profiles
merge_metaphlan_tables.py metaphlan/*_profile.txt > metaphlan/merged_abundance.txt
```

### Step 2: Functional Profiling with HUMAnN

```bash
# Run HUMAnN
for sample in sample1 sample2 sample3; do
    # Concatenate paired reads
    cat host_removed/${sample}_R1.fq.gz host_removed/${sample}_R2.fq.gz > \
        host_removed/${sample}_concat.fq.gz

    humann --input host_removed/${sample}_concat.fq.gz \
        --output humann/${sample} \
        --threads 8 \
        --metaphlan-options "--bowtie2db metaphlan_db"
done

# Normalize and join tables. HUMAnN names outputs from the input STEM, so the ${sample}_concat.fq.gz
# input above yields sample1_concat_pathabundance.tsv (not sample1_pathabundance.tsv).
humann_renorm_table --input humann/sample1/sample1_concat_pathabundance.tsv \
    --output humann/sample1/sample1_concat_pathabundance_cpm.tsv \
    --units cpm

# --search-subdirectories: per-sample outputs live in humann/<sample>/ subdirs; the join is
# non-recursive by default and would otherwise find zero files.
humann_join_tables --input humann \
    --search-subdirectories \
    --output humann/merged_pathabundance.tsv \
    --file_name pathabundance
```

### Visualization

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Bracken species table. combine_bracken_outputs.py emits name, taxonomy_id, taxonomy_lvl,
# then per-sample {sample}_num / {sample}_frac columns. Keep ONLY the fractions: taxonomy_lvl is a
# string ('S') and summing it raises TypeError; summing taxonomy_id would be meaningless anyway.
species = pd.read_csv('bracken/combined_species.txt', sep='\t', index_col=0)
species = species.filter(regex='_frac$').rename(columns=lambda c: c.replace('_frac', ''))

# Top 20 species heatmap
top20 = species.sum(axis=1).nlargest(20).index
plt.figure(figsize=(12, 8))
sns.heatmap(species.loc[top20], cmap='viridis', annot=False)
plt.title('Top 20 Species Abundance')
plt.tight_layout()
plt.savefig('top20_species_heatmap.pdf')

# Stacked bar plot
species_norm = species.div(species.sum()) * 100
top10 = species_norm.sum(axis=1).nlargest(10).index
other = species_norm.loc[~species_norm.index.isin(top10)].sum()

plot_data = species_norm.loc[top10].T
plot_data['Other'] = other
plot_data.plot(kind='bar', stacked=True, figsize=(10, 6))
plt.ylabel('Relative Abundance (%)')
plt.legend(bbox_to_anchor=(1.05, 1))
plt.tight_layout()
plt.savefig('species_barplot.pdf')
```

## Parameter Recommendations

| Step | Parameter | Value |
|------|-----------|-------|
| fastp | --length_required | 50 (metagenomic reads) |
| Kraken2 | --confidence | 0.1-0.4 (default 0.0 over-classifies; see metagenomics/kraken-classification) |
| Kraken2 | --minimum-hit-groups | 2 (cut single-region false positives) |
| Bracken | -r | Read length (e.g., 150; must match the DB build) |
| Bracken | -l | S (species) or G (genus) |
| Bracken | -t | 10 (min reads threshold) |
| MetaPhlAn | --min_cu_len | 2000 (default) |
| HUMAnN | --threads | 8+ |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| A "novel community" that is the kitome | Negative controls skipped / contamination bleed | Blanks + mock through the full workflow; decontam; skepticism toward canonical kitome genera |
| Same organism appears twice under different names | Merged GTDB-Tk-labelled and NCBI-labelled tables (Firmicutes vs Bacillota) | State which taxonomy each table uses; never name-merge without a crosswalk |
| Cross-study comparison is really tool differences | Compared across tools/DBs | Hold tool + DB constant within a study; benchmark on a mock with OPAL |
| A zero read as biological absence | Confused detection-limit with biology | Name which link (depth/DB/extraction/depletion) is responsible before any biological reading; Nonpareil depth check |
| Read-fraction and cell-fraction merged | Kraken2 % joined to MetaPhlAn % | Keep separate tables; they use different absence semantics |
| Low classification rate | Database mismatch / novel organisms | Match DB to habitat; report classified fraction; a low fraction = wrong/incomplete DB |
| High host reads | Incomplete host removal | Use the complete T2T host reference; mask rDNA |

## References

- Salter SJ, Cox MJ, Turek EM, et al (2014) Reagent and laboratory contamination can critically impact sequence-based microbiome analyses. *BMC Biology* 12:87. DOI 10.1186/s12915-014-0087-z. (the kitome.)
- Costea PI, Zeller G, Sunagawa S, et al (2017) Towards standards for human fecal sample processing in metagenomic studies. *Nature Biotechnology* 35:1069-1076. DOI 10.1038/nbt.3960. (extraction dominates.)
- Meyer F, Bremges A, Belmann P, et al (2019) Assessing taxonomic metagenome profilers with OPAL. *Genome Biology* 20:51. DOI 10.1186/s13059-019-1646-y.
- Sczyrba A, Hofmann P, Belmann P, et al (2017) Critical Assessment of Metagenome Interpretation (CAMI). *Nature Methods* 14:1063-1071. DOI 10.1038/nmeth.4458.

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

THREADS=8
KRAKEN_DB="kraken2_standard_db"
HOST_INDEX="human_bt2_index"   # MUST be built from T2T-CHM13 (CHM13v2, +HLA) per the made-once host-removal commitment, not a legacy GRCh38 index
SAMPLES="sample1 sample2 sample3"
OUTDIR="metagenomics_results"

mkdir -p ${OUTDIR}/{trimmed,host_removed,kraken,bracken,metaphlan,humann,qc}

# Step 1: QC
echo "=== QC ==="
for sample in $SAMPLES; do
    fastp -i ${sample}_R1.fastq.gz -I ${sample}_R2.fastq.gz \
        -o ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        -O ${OUTDIR}/trimmed/${sample}_R2.fq.gz \
        --length_required 50 \
        --html ${OUTDIR}/qc/${sample}_fastp.html -w ${THREADS}
done

# Host removal
echo "=== Host Removal ==="
for sample in $SAMPLES; do
    # -f 12 (read unmapped AND mate unmapped) keeps only pairs where NEITHER mate hit the host.
    # --un-conc-gz would instead keep every non-CONCORDANT pair, retaining pairs whose mate mapped
    # human -- a privacy leak, not just a QC lapse. -F 256 drops secondary alignments.
    bowtie2 -p ${THREADS} -x ${HOST_INDEX} --very-sensitive \
        -1 ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        -2 ${OUTDIR}/trimmed/${sample}_R2.fq.gz \
        2> ${OUTDIR}/qc/${sample}_host.log \
      | samtools view -b -f 12 -F 256 - \
      | samtools sort -n -@ ${THREADS} - \
      | samtools fastq -1 ${OUTDIR}/host_removed/${sample}_R1.fq.gz \
                       -2 ${OUTDIR}/host_removed/${sample}_R2.fq.gz \
                       -0 /dev/null -s /dev/null -n -
done

# Step 2: Kraken2
echo "=== Kraken2 ==="
for sample in $SAMPLES; do
    kraken2 --db ${KRAKEN_DB} --threads ${THREADS} --paired \
        --confidence 0.1 --minimum-hit-groups 2 \
        --report ${OUTDIR}/kraken/${sample}.report \
        --output ${OUTDIR}/kraken/${sample}.output \
        ${OUTDIR}/host_removed/${sample}_R1.fq.gz \
        ${OUTDIR}/host_removed/${sample}_R2.fq.gz
done

# Bracken
echo "=== Bracken ==="
for sample in $SAMPLES; do
    bracken -d ${KRAKEN_DB} \
        -i ${OUTDIR}/kraken/${sample}.report \
        -o ${OUTDIR}/bracken/${sample}.species.txt \
        -r 150 -l S -t 10
done

echo "=== Pipeline Complete ==="
echo "Kraken reports: ${OUTDIR}/kraken/"
echo "Bracken abundances: ${OUTDIR}/bracken/"
```

## Related Skills

- database-access/sra-data - Pull metagenomic FASTQ from SRA / ENA (16S amplicon or shotgun)
- database-access/ncbi-datasets-cli - Bulk-pull reference genomes for read mapping
- database-access/remote-homology - DIAMOND --ultra-sensitive for predicted-ORF annotation
- metagenomics/contamination-controls - Host depletion, blanks/decontam, depth checks up front
- metagenomics/kraken-classification - Kraken2 details
- metagenomics/metaphlan-profiling - MetaPhlAn parameters
- metagenomics/abundance-estimation - Bracken options and compositional handling
- metagenomics/functional-profiling - HUMAnN workflow
- metagenomics/amr-detection - Community resistome from the same reads
- metagenomics/strain-tracking - Strain resolution from the same reads
- metagenomics/metagenome-visualization - Plotting and community statistics
<!-- END FILE: workflows/metagenomics-pipeline/SKILL.md -->

## 子目录：workflows/methylation-pipeline

<!-- BEGIN FILE: workflows/methylation-pipeline/SKILL.md -->
---
name: bio-workflows-methylation-pipeline
description: Orchestrates the end-to-end bisulfite/EM-seq methylation pipeline from FASTQ to differentially methylated regions, chaining Trim Galore/fastp QC, Bismark alignment + deduplication, methylation calling, methylKit coverage-filtering/normalization, and selection-aware DMR detection (dmrseq/DSS). Use when gating the run on bisulfite conversion (lambda + pUC19 controls) BEFORE any beta value, committing the genome build + library directionality once, keeping mate-overlap deduplicated (--no_overlap), M-bias-trimming from the plot, filtering coverage before testing, choosing a count model (beta-binomial/DSS) over a bare-beta t-test, or using a region-selection-aware FDR (dmrseq/DSS) rather than raw methylKit tiles. Hands mechanism to the methylation-analysis component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: Bismark
workflow: true
depends_on:
  - read-qc/fastp-workflow
  - methylation-analysis/bismark-alignment
  - methylation-analysis/methylation-calling
  - methylation-analysis/methylkit-analysis
  - methylation-analysis/differential-cpg-testing
  - methylation-analysis/dmr-detection
qc_checkpoints:
  - after_qc: "Q30 >80%, adapter content removed"
  - after_alignment: "Mapping efficiency >50%, bisulfite conversion >99%"
  - after_calling: "Coverage distribution reasonable, no biased positions"
---

## Version Compatibility

Reference examples tested with: Bismark 0.24+, Bowtie2 2.5.3+, FastQC 0.12+, Trim Galore 0.6.10+, fastp 0.23+, methylKit 1.28+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Methylation Pipeline

**"Analyze my bisulfite sequencing data from FASTQ to DMRs"** -> Chain QC/trim, Bismark alignment + dedup, methylation calling, coverage-filtered per-CpG testing, and selection-aware DMR detection.
- CLI + R: Trim Galore/fastp -> bismark -> deduplicate_bismark -> bismark_methylation_extractor -> methylKit (filter/normalize/unite) -> DSS/dmrseq

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

A methylation callset is decided at four seams, not inside the caller.

1. **Bisulfite conversion is verified BEFORE any beta value is trusted — this is the gate that most pipelines skip.** An unmethylated lambda (or spike-in) bounds UNDER-conversion (residual C read as methylated -> false hyper); a methylated pUC19 control bounds OVER-conversion (5mC deaminated -> false hypo). Require conversion >99% from the lambda control before computing a single methylation level; a 98% library silently shifts every call.
2. **Mate overlap must be deduplicated once.** In paired-end WGBS the R1/R2 insert overlaps, and counting a CpG in both mates double-weights it. `bismark_methylation_extractor --paired-end` applies `--no_overlap` by default; running the extractor in single-end mode on paired data (or losing `--no_overlap`) inflates coverage and distorts levels.
3. **M-bias is trimmed from the plot, and coverage is filtered BEFORE testing.** End-repair fill-in biases the first/last few bases (read the M-bias plot, trim positionally — not a fixed number). Then filter low- and extreme-coverage CpGs before any test: variance depends on coverage, so unfiltered low-coverage sites dominate the FDR.
4. **The statistic must respect counts, and region FDR must respect selection.** A bare-beta t-test discards coverage (the precision unique to sequencing); use a beta-binomial/overdispersion model (DSS, methylKit `overdispersion='MN'`) for counts, or limma-on-M-values for arrays. For REGIONS, methylKit fixed tiles do not correct for the region-selection step — use dmrseq (permutation null over selection) or DSS `callDMR` for a rigorous region-level FDR.

## Made-once commitments

| Commitment | Choice | Consequence inherited downstream |
|------------|--------|----------------------------------|
| Genome build + library model | One build; directional (WGBS/EM-seq) vs non-directional/PBAT | Wrong strand model tanks mapping; build fixes all coordinates |
| Conversion controls | Lambda (unmethylated) + pUC19 (methylated) spike-ins | Without them, under/over-conversion is undetectable and biases every call |
| Assay entry | WGBS/EM-seq (this pipeline) vs Infinium array (array-preprocessing) | Array data enters at beta/M matrix, not Bismark |
| Context | CpG (default) vs CHG/CHH (plants/non-CpG) | Non-CpG contexts need conversion-aware calling and separate testing |

## Workflow Overview

```
FASTQ files
    |
    v
[1. QC & Trimming] -----> fastp/Trim Galore
    |
    v
[2. Alignment] ---------> Bismark
    |
    v
[3. Deduplication] -----> deduplicate_bismark
    |
    v
[4. Methylation Calling] -> bismark_methylation_extractor
    |
    v
[5. Per-CpG Analysis] ---> methylKit (R) or scipy (Python)
    |
    v
[6. DMR Detection] ------> methylKit/DSS
    |
    v
Differentially methylated regions
```

## Primary Path: Bismark + methylKit

### Step 1: Quality Control

```bash
# Trim Galore recommended for bisulfite data (handles adapter bias)
trim_galore --paired --fastqc \
    -o trimmed/ \
    sample_R1.fastq.gz sample_R2.fastq.gz

# Or fastp with conservative settings
fastp -i sample_R1.fastq.gz -I sample_R2.fastq.gz \
    -o trimmed/sample_R1.fq.gz -O trimmed/sample_R2.fq.gz \
    --detect_adapter_for_pe \
    --qualified_quality_phred 20 \
    --length_required 35 \
    --html qc/sample_fastp.html
```

### Step 2: Bismark Alignment

```bash
# Prepare genome (once)
bismark_genome_preparation --bowtie2 genome/

# Align
bismark --genome genome/ \
    -1 trimmed/sample_R1_val_1.fq.gz \
    -2 trimmed/sample_R2_val_2.fq.gz \
    -o aligned/ \
    --parallel 4 \
    --temp_dir tmp/

# Output: sample_R1_val_1_bismark_bt2_pe.bam
```

**QC Checkpoint:** Check Bismark report
- Mapping efficiency >50% (the 3-letter alphabet lowers uniqueness; 50-70% is normal for WGBS)
- Bisulfite conversion >99% from the unmethylated lambda spike-in (bounds under-conversion -> false hyper); also check a methylated pUC19 control for over-conversion (-> false hypo). With NO spike-in, use the genome-wide non-CpG (CHH) methylation rate as a conversion proxy in mammals (expected near 0)

### Step 3: Deduplication (WGBS / EM-seq ONLY)

Deduplicate WGBS and EM-seq. Do NOT deduplicate RRBS, amplicon, or other target-enrichment libraries: their reads legitimately stack at the MspI cut sites, so positional dedup destroys real coverage (Bismark's own docs say so). Skip this step entirely for RRBS.

```bash
# WGBS / EM-seq only -- skip for RRBS/amplicon
deduplicate_bismark \
    --bam \
    -p \
    --output_dir deduplicated/ \
    aligned/sample_R1_val_1_bismark_bt2_pe.bam
```

### Step 4: Methylation Calling

```bash
# --paired-end enables --no_overlap by DEFAULT (deduplicates the R1/R2 insert overlap so a CpG in
# the overlap is not double-counted). Do NOT run the extractor in single-end mode on paired data.
bismark_methylation_extractor \
    --paired-end \
    --comprehensive \
    --bedGraph \
    --cytosine_report \
    --genome_folder genome/ \
    -o methylation/ \
    deduplicated/sample_R1_val_1_bismark_bt2_pe.deduplicated.bam

# Generate summary report
bismark2report
bismark2summary
```

### Step 5: Analysis with methylKit

**Goal:** Turn per-sample coverage/cytosine reports into a coverage-filtered, normalized, united methylation object ready for testing.

**Approach:** Read each sample with the matching pipeline, drop low-coverage and extreme-coverage CpGs, normalize coverage across libraries, then unite to the sites covered in every sample.

```r
library(methylKit)

# Read methylation calls
files <- list(
    'methylation/control_1.CpG_report.txt',
    'methylation/control_2.CpG_report.txt',
    'methylation/treated_1.CpG_report.txt',
    'methylation/treated_2.CpG_report.txt'
)

sample_ids <- c('control_1', 'control_2', 'treated_1', 'treated_2')
treatment <- c(0, 0, 1, 1)

# Read cytosine reports
meth_obj <- methRead(
    location = as.list(files),
    sample.id = as.list(sample_ids),
    assembly = 'hg38',
    treatment = treatment,
    context = 'CpG',
    pipeline = 'bismarkCytosineReport'
)

# Filter by coverage
meth_filtered <- filterByCoverage(meth_obj, lo.count = 10, hi.perc = 99.9)

# Normalize coverage
meth_norm <- normalizeCoverage(meth_filtered)

# Merge samples (keep sites covered in all)
meth_merged <- unite(meth_norm, destrand = TRUE)

# Sample statistics
getMethylationStats(meth_obj[[1]], plot = TRUE)
getCoverageStats(meth_obj[[1]], plot = TRUE)
```

### Step 5b: Python Alternative for Per-CpG Testing

When methylKit is unavailable or a Python-only workflow is preferred, per-CpG testing can be performed with scipy and statsmodels on beta values computed from the coverage files.

```python
import pandas as pd
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
import numpy as np

# Read Bismark coverage files and compute beta values
# beta = count_methylated / (count_methylated + count_unmethylated)
# Filter CpGs with < 10x coverage in any sample
# Run per-CpG Welch's t-test between groups
# Apply BH FDR correction: multipletests(pvals, method='fdr_bh')
# See methylation-analysis/differential-cpg-testing for full pipeline
```

A bare-beta t-test discards coverage (the precision information unique to sequencing) and is only a quick look. For sequencing counts, route to a beta-binomial / overdispersion-corrected count model (DSS, or methylKit with overdispersion='MN'); for array or continuous data, use limma on M-values. The count-vs-continuous decision is owned by methylation-analysis/differential-cpg-testing.

### Step 6: DMR Detection

methylKit fixed tiles are a fast screen, but their region q-value is not corrected for the region-selection step. For a rigorous region-level FDR use dmrseq (a permutation null over the selection) or DSS callDMR, and confirm with cross-tool overlap - see methylation-analysis/dmr-detection.

```r
# Calculate differential methylation (per CpG). overdispersion='MN' + test='Chisq' applies the
# overdispersion correction seam #4 requires; the default 'none' gives underdispersed p-values.
diff_meth <- calculateDiffMeth(meth_merged, overdispersion = 'MN', test = 'Chisq')

# Get significant DMCs
dmc <- getMethylDiff(diff_meth, difference = 25, qvalue = 0.01)

# Tile into regions (DMRs)
tiles <- tileMethylCounts(meth_merged, win.size = 1000, step.size = 1000)
diff_tiles <- calculateDiffMeth(tiles, overdispersion = 'MN', test = 'Chisq')   # same overdispersion correction as per-CpG (seam #4)
dmr <- getMethylDiff(diff_tiles, difference = 25, qvalue = 0.01)

# Export
write.csv(as.data.frame(dmc), 'dmc_results.csv')
write.csv(as.data.frame(dmr), 'dmr_results.csv')

# Annotate with genomic features
library(genomation)
gene_obj <- readTranscriptFeatures('genes.bed')
annotateWithGeneParts(as(dmr, 'GRanges'), gene_obj)
```

## Parameter Recommendations

| Step | Parameter | Value |
|------|-----------|-------|
| Trim Galore | default | Recommended for BS-seq |
| Bismark | --parallel | 4 (per sample parallelization) |
| methylKit | lo.count | 10 (minimum coverage) |
| methylKit | difference | 25 (% methylation difference) |
| methylKit | qvalue | 0.01 |
| DMR tiles | win.size | 500-1000 bp |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Genome-wide hyper- or hypo-methylation shift | Under/over-conversion never checked | Gate on lambda (>99%) + pUC19 controls BEFORE trusting any beta value |
| Coverage inflated, levels off in mate-overlap regions | Extractor run single-end on paired data / lost `--no_overlap` | Use `--paired-end` (applies `--no_overlap`); do not single-end paired data |
| Systematic bias at read ends | M-bias from end-repair fill-in | Trim positionally from the M-bias plot, not a fixed number |
| Low-coverage CpGs dominate the DMC list | No coverage filter before testing | `filterByCoverage(lo.count=10, hi.perc=99.9)` before `calculateDiffMeth` |
| Spurious DMCs / underdispersed p-values | Bare-beta t-test ignores counts/overdispersion | Beta-binomial/DSS or methylKit `overdispersion='MN'`; limma-M for arrays |
| Region q-values too optimistic | methylKit fixed tiles ignore the region-selection step | Use dmrseq (permutation null) or DSS `callDMR` for region-level FDR |
| Very low mapping efficiency | Wrong library directionality (PBAT/non-directional aligned as directional) | Set the correct Bismark strand model (methylation-analysis/bismark-alignment) |

The full per-step chain is shown above; the runnable methylKit analysis is in this skill's examples/ (`methylkit_analysis.R`).

## References

- Krueger F, Andrews SR (2011) Bismark: a flexible aligner and methylation caller for Bisulfite-Seq applications. *Bioinformatics* 27:1571-1572. DOI 10.1093/bioinformatics/btr167.
- Akalin A, Kormaksson M, Li S, et al (2012) methylKit: a comprehensive R package for the analysis of genome-wide DNA methylation profiles. *Genome Biology* 13:R87. DOI 10.1186/gb-2012-13-10-r87.
- Feng H, Conneely KN, Wu H (2014) A Bayesian hierarchical model to detect differentially methylated loci from single nucleotide resolution sequencing data. *Nucleic Acids Research* 42:e69. DOI 10.1093/nar/gku154. (DSS.)
- Korthauer K, Chakraborty S, Benjamini Y, Irizarry RA (2019) Detection and accurate false discovery rate control of differentially methylated regions from whole genome bisulfite sequencing. *Biostatistics* 20:367-383. DOI 10.1093/biostatistics/kxy007. (dmrseq; region-selection-aware FDR.)

## Related Skills

- methylation-analysis/bismark-alignment - Bisulfite/EM-seq alignment, library/strand model, conversion QC
- methylation-analysis/methylation-calling - Calling from BAM (Bismark/MethylDackel), contexts, variant-aware
- methylation-analysis/methylkit-analysis - methylKit object model and overdispersion gotchas
- methylation-analysis/differential-cpg-testing - Per-CpG testing (count-vs-continuous fork)
- methylation-analysis/dmr-detection - Selection-aware region callers (dmrseq/DSS) and PMD segmentation
- methylation-analysis/array-preprocessing - Alternate entry: Infinium IDAT to beta/M matrix
- methylation-analysis/cell-type-deconvolution - Cell-fraction covariates for bulk-tissue EWAS
- methylation-analysis/epigenetic-clocks - DNAm age and age acceleration
- methylation-analysis/ewas-design - EWAS confounding, batch, inflation, and replication
<!-- END FILE: workflows/methylation-pipeline/SKILL.md -->

## 子目录：workflows/microbiome-pipeline

<!-- BEGIN FILE: workflows/microbiome-pipeline/SKILL.md -->
---
name: bio-workflows-microbiome-pipeline
description: End-to-end 16S/ITS amplicon workflow from demultiplexed FASTQ to a consensus differential-abundance result, orchestrating cutadapt primer removal, per-run DADA2 ASV inference (learnErrors/mergeSequenceTables/removeBimeraDenovo), region-matched taxonomy assignment, a SEPP/Greengenes2 tree, alpha/beta diversity at a declared sampling depth (phyloseq/vegan, adonis2 paired with betadisper), compositional DA as a consensus of >=2 tools (ALDEx2/ANCOM-BC2) on unrarefied counts, and optional PICRUSt2 functional prediction gated on NSTI. Covers the stage-ordering decisions (primers before truncation, per-run error model, rarefy for diversity not DA, predicted potential not activity) and defers each per-step choice to the six microbiome skills. Use when staging an amplicon study end to end or chaining ASV inference, taxonomy, diversity, and differential abundance. For shotgun reads see workflows/metagenomics-pipeline.
tool_type: mixed
primary_tool: DADA2
workflow: true
depends_on:
  - read-qc/adapter-trimming
  - microbiome/amplicon-processing
  - microbiome/taxonomy-assignment
  - microbiome/diversity-analysis
  - microbiome/differential-abundance
  - microbiome/functional-prediction
qc_checkpoints:
  - after_denoising: "Per-sample reads tracked through filter/denoise/merge/nonchim; no merge cliff"
  - after_diversity: "Sampling depth declared; dropped-sample list reported"
  - after_da: "Consensus of >=2 CoDA tools on unrarefied counts; tools named"
---

## Version Compatibility

Reference examples tested with: DADA2 1.30+, cutadapt 4.6+, phyloseq 1.46+, vegan 2.6+, ALDEx2 1.34+, ANCOMBC 2.4+, QIIME2 2024.2+, PICRUSt2 2.5+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The error model is a PER-RUN artifact and the reference database is a versioned dependency, not just a tool: run `learnErrors` once per sequencing run, never pooled; record the SILVA/GTDB/UNITE release and the classifier training region, the tree-build method (SEPP/Greengenes2 vs de novo), the rarefaction depth, and the PICRUSt2 reference release alongside every result.

# Microbiome Pipeline

**"Run my 16S amplicon study end to end from FASTQ"** -> Stage primer removal, per-run denoising, region-matched taxonomy, a placed tree, declared-depth diversity, and a consensus differential-abundance result - deferring every per-step decision to the owning microbiome skill, because each stage's parameters silently set what the next stage can find.

Complete workflow from demultiplexed amplicon FASTQ to a confidence-graded differential-abundance result. This is an ORCHESTRATION skill: it sequences the stages and routes the science to the six microbiome category skills; it does not re-teach the per-step decisions.

Scope: amplicon (16S/ITS) reads -> ASV table -> taxonomy -> diversity + consensus DA + optional predicted function. Shotgun/WGS reads -> workflows/metagenomics-pipeline. Each method choice -> its owning microbiome skill (links below). QIIME2 artifact/provenance route -> microbiome/qiime2-workflow.

## The Single Most Important Modern Insight -- The Pipeline Is a Chain of Modeling Choices, Not a Conveyor Belt

The feature table, the diversity number, and the differential-taxa list are not observations of the community - each is the residue of a knob turned at an EARLIER stage, before any result existed. Turn the knobs differently and the answer changes. The orchestration discipline is therefore to declare and defend each stage's choice, in order, because every stage silently constrains the next:

1. **What is stripped and where reads are truncated decides what is detectable.** Primers left on corrupt the error model and inflate chimeras; truncating below the merge-overlap budget erases taxa by arithmetic. These are set before any ASV exists (microbiome/amplicon-processing).
2. **The error model is per-run, the tree is a model, and the depth is a sample-deletion knob.** Pooling runs into one `learnErrors` denoises wrong; a de novo tree from short reads injects topology noise into UniFrac; a sampling depth above some samples' totals silently drops the lowest-biomass samples (microbiome/diversity-analysis).
3. **Rarefy for diversity, never for DA; and which taxa are "significant" depends more on the tool than the biology.** Keep the raw counts, rarefy only into the diversity branch, and report a CONSENSUS of >=2 compositionally-aware tools rather than one tool's hit list (Nearing 2022 *Nat Commun* 13:342; microbiome/differential-abundance).
4. **PICRUSt2 predicts potential, not activity, and is circular with taxonomy.** Predicted function is the ASV table re-encoded through a fixed lookup - hypothesis-generating, gated on NSTI, never "more active" (microbiome/functional-prediction).

## Pipeline Stages

Each stage hands its decisions to the owning skill; this table is the routing map, not a parameter sheet.

| Stage | Operation | Owning skill (decisions) |
|-------|-----------|--------------------------|
| 0 | Read QC; confirm primers/region known | read-qc/quality-reports, read-qc/adapter-trimming |
| 1 | Remove primers (cutadapt, BEFORE truncation) | microbiome/amplicon-processing, read-qc/adapter-trimming |
| 2 | Per-RUN DADA2: filterAndTrim -> learnErrors -> dada -> mergePairs | microbiome/amplicon-processing |
| 3 | mergeSequenceTables across runs, then ONE removeBimeraDenovo | microbiome/amplicon-processing |
| 4 | Region-matched taxonomy (genus, not species, for 16S) | microbiome/taxonomy-assignment |
| 5 | Build phyloseq + a SEPP/Greengenes2 tree (NOT de novo for short reads) | microbiome/diversity-analysis, phylogenetics/tree-io |
| 6 | Alpha/beta diversity at a DECLARED depth; adonis2 + betadisper | microbiome/diversity-analysis |
| 7 | Consensus DA of >=2 CoDA tools on UNrarefied counts | microbiome/differential-abundance |
| 8 | Optional PICRUSt2 functional PREDICTION, gated on NSTI | microbiome/functional-prediction |

QIIME2 artifact/provenance alternative for the whole chain: microbiome/qiime2-workflow (`qiime cutadapt` -> `dada2 denoise-paired` -> `feature-classifier classify-sklearn` -> `fragment-insertion sepp` -> `diversity core-metrics-phylogenetic` -> `composition ancombc` -> `q2-picrust2`). Same decisions, `.qza`/`.qzv` provenance ecosystem.

## Workflow Overview

```
Demultiplexed amplicon FASTQ (per sample, per run; primers/region known)
    |
    v
[0. Read QC]                         FastQC/MultiQC -> read-qc/quality-reports
    |
    v
[1. Remove primers]  cutadapt -g FWD -G REV --discard-untrimmed   (BEFORE truncation)
    |
    v
[2. Per-RUN DADA2]   filterAndTrim -> learnErrors (one run) -> dada -> mergePairs
    |                (repeat per sequencing run; never pool FASTQs into one learnErrors)
    v
[3. Combine + chimeras]  mergeSequenceTables(run1, run2, ...) -> ONE removeBimeraDenovo
    |
    v
[4. Taxonomy]        region-matched SILVA/GTDB/UNITE classifier -> genus (16S)
    |
    v
[5. phyloseq + tree] otu+tax+sample_data + SEPP/Greengenes2 placed tree (NOT de novo)
    |
    +--> [6. Diversity]  rarefy_even_depth(declared depth) -> alpha; UniFrac/Bray + adonis2 + betadisper
    |        (report the depth AND the dropped-sample list)
    |
    +--> [7. Differential abundance]  UNRAREFIED counts -> ALDEx2 AND ANCOM-BC2/LinDA -> CONSENSUS
    |
    +--> [8. Functional prediction]  PICRUSt2 (optional) -> KO/MetaCyc POTENTIAL, report NSTI
    |
    v
ASV table + taxonomy + diversity + consensus DA hits (+ predicted potential)
```

## Stage 1 to 3: Primers, Per-Run Denoising, Chimeras

**Goal:** Turn demultiplexed reads into one chimera-free ASV table, with primers off first and the error model fit per run.

**Approach:** Strip primers with cutadapt before any quality step; run the DADA2 block (filter -> learnErrors -> dada -> mergePairs) ONCE PER sequencing run; merge the run-level tables by exact sequence string; remove chimeras once on the combined table. Decisions (truncLen budget, maxEE, pooling mode, ITS handling) live in microbiome/amplicon-processing.

```bash
# Primers come OFF before truncation - leftover primer bases corrupt the error model and look chimeric.
# -g = forward primer (5' on R1), -G = reverse primer (5' on R2); --discard-untrimmed drops primerless pairs.
cutadapt -g GTGYCAGCMGCCGCGGTAA -G GGACTACNVGGGTWTCTAAT --discard-untrimmed \
    -o trimmed_R1.fastq.gz -p trimmed_R2.fastq.gz sample_R1.fastq.gz sample_R2.fastq.gz
```

```r
library(dada2)
# Run this block ONCE PER sequencing run. truncLen is a merge-overlap budget, not just a quality cut:
# truncLen_F + truncLen_R >= amplicon_length + ~12 (mergePairs minOverlap). See amplicon-processing.
out <- filterAndTrim(fnFs, filtFs, fnRs, filtRs, truncLen = c(240, 160),
                     maxEE = c(2, 2), truncQ = 2, maxN = 0, rm.phix = TRUE,
                     compress = TRUE, multithread = TRUE)
errF <- learnErrors(filtFs, multithread = TRUE)   # fit THIS run only - never pool runs
errR <- learnErrors(filtRs, multithread = TRUE)
mergers <- mergePairs(dada(filtFs, err = errF, multithread = TRUE), filtFs,
                      dada(filtRs, err = errR, multithread = TRUE), filtRs)
seqtab_run <- makeSequenceTable(mergers)
# Combine per-run tables (exact-sequence string is the join key), THEN one chimera removal:
seqtab <- mergeSequenceTables(seqtab_run1, seqtab_run2)   # single run: skip; pass seqtab_run
seqtab_nochim <- removeBimeraDenovo(seqtab, method = 'consensus', multithread = TRUE)
```

A merge cliff (near-zero `merged` column) or a large READ fraction lost as chimeric is a stage-1/2 knob problem, not bad data - see microbiome/amplicon-processing. For low-biomass studies, sequence negative/positive controls and run decontam on the ASV table before downstream analysis (microbiome/amplicon-processing; metagenomics/contamination-controls).

## Stage 4 to 6: Taxonomy, Tree, Diversity

**Goal:** Label ASVs against a region-matched reference, assemble a phyloseq object with a PLACED tree, and summarize diversity at a depth that retains samples.

**Approach:** Assign taxonomy with a classifier trained on the amplicon region (report genus for 16S, not species); filter host mitochondria/chloroplast features (universal 16S primers amplify them); build the phyloseq object and attach a SEPP/Greengenes2 placed tree rather than a de novo tree from short reads; rarefy ONLY into the diversity branch at a declared depth, report the dropped samples, and pair adonis2 with betadisper. Decisions live in microbiome/taxonomy-assignment and microbiome/diversity-analysis.

```r
library(phyloseq); library(vegan)
# minBoot 50 = DADA2/RDP default for reads <=250 nt; ranks below it return NA, not a guess.
taxa <- assignTaxonomy(seqtab_nochim, 'silva_nr99_v138.1_train_set.fa.gz', minBoot = 50, multithread = TRUE)
ps <- phyloseq(otu_table(seqtab_nochim, taxa_are_rows = FALSE), tax_table(taxa),
               sample_data(metadata), phy_tree(placed_tree))   # placed_tree from SEPP/GG2, NOT de novo
ps <- subset_taxa(ps, is.na(Order) | Order != 'Chloroplast')      # drop host organelle 16S before diversity/DA
ps <- subset_taxa(ps, is.na(Family) | Family != 'Mitochondria')

# Diversity branch ONLY: rarefy to a DECLARED depth (not min(sample_sums)) and report who was dropped.
depth <- 10000   # choose on the alpha-rarefaction plateau; below this samples are dropped - report them
ps_rare <- rarefy_even_depth(ps, sample.size = depth, rngseed = 42, replace = FALSE)
adonis2(UniFrac(ps_rare, weighted = TRUE) ~ Group, data = data.frame(sample_data(ps_rare)), permutations = 999)
permutest(betadisper(UniFrac(ps_rare, weighted = TRUE), sample_data(ps_rare)$Group))   # location vs dispersion
```

SEPP placement is `qiime fragment-insertion sepp`; a de novo `align-to-tree-mafft-fasttree` is acceptable only when no reference package fits the marker, and unweighted UniFrac on it must be treated as suspect (microbiome/diversity-analysis).

## Stage 7: Consensus Differential Abundance

**Goal:** Identify differentially abundant taxa as a confidence-graded consensus, not one tool's volcano plot.

**Approach:** On the UNrarefied counts (rarefying discards information DA needs), filter rare features, run ALDEx2 plus a second compositionally-aware tool (ANCOM-BC2 or LinDA), gate ALDEx2 on q AND effect size, and report the intersection as high-confidence. Tool mechanics live in microbiome/differential-abundance.

```r
library(ALDEx2); library(ANCOMBC)
ps_filt <- filter_taxa(ps, function(x) sum(x > 0) >= 0.10 * nsamples(ps), TRUE)   # >=10% prevalence; declared knob
counts <- as.matrix(otu_table(ps_filt)); if (!taxa_are_rows(ps_filt)) counts <- t(counts)   # taxa in ROWS, integer counts
groups <- as.character(sample_data(ps_filt)$Group)

ax <- aldex(counts, groups, mc.samples = 128, test = 't', effect = TRUE, denom = 'all')
sig_aldex <- rownames(ax)[ax$we.eBH < 0.05 & abs(ax$effect) > 1]   # q AND |effect|>1 (between-group diff exceeds within-condition dispersion); NOT p alone

# Multi-run study: carry run as a batch covariate -> fix_formula = 'run_id + Group'. (ALDEx2 cannot
# take a covariate via aldex(); use aldex.clr() + aldex.glm() on a model matrix for the run-adjusted arm.)
ab <- ancombc2(data = ps_filt, fix_formula = 'Group', p_adj_method = 'BH',   # default is 'holm' - set BH deliberately
               prv_cut = 0.10, group = 'Group', struc_zero = TRUE, pseudo_sens = TRUE)$res
dcol <- grep('^diff_Group', names(ab), value = TRUE)[1]   # coefficient = variable+factor level, verbatim case (e.g. 'Grouptreated')
sig_ancombc <- ab$taxon[ab[[dcol]] & ab[[sub('^diff_', 'passed_ss_', dcol)]]]    # significant AND pseudo-count-robust

confident <- intersect(sig_aldex, sig_ancombc)   # high-confidence; union = exploratory; name both tools
```

## Stage 8: Functional Prediction (optional)

**Goal:** Summarize predicted community functional POTENTIAL, framed as hypothesis-generating and gated on NSTI.

**Approach:** Run PICRUSt2 on the rep-seqs and ASV table, report the NSTI distribution and the read fraction dropped at `--max_nsti 2`, and restrict every claim to "potential" - never "activity". Decisions live in microbiome/functional-prediction; for MEASURED function use shotgun (metagenomics/functional-profiling).

```bash
# Predicts KO/MetaCyc POTENTIAL from who-is-there - never measured genes, never activity.
picrust2_pipeline.py -s asv_seqs.fna -i asv_table.biom -o picrust2_out -p 8 --max_nsti 2 --hsp_method mp
# Report mean/median NSTI and the ASV+read fraction dropped at NSTI>2 (marker_predicted_and_nsti.tsv.gz).
```

## Per-Stage Failure Modes

### Primers left on before truncation (stage 1)
**Trigger:** running filterAndTrim/learnErrors on reads still carrying primers. **Mechanism:** degenerate primer bases read as sequencing error, corrupting the error model and masquerading as chimeras. **Symptom:** wrong error fit, a large READ fraction lost as chimeric, inflated ASV count. **Fix:** cutadapt `--discard-untrimmed` first; order is primers -> filter -> learnErrors (microbiome/amplicon-processing).

### Pooling runs into one error model (stage 2)
**Trigger:** concatenating multiple runs' FASTQs before `learnErrors`. **Mechanism:** one error model is fit to a mixture of run-specific error structures. **Symptom:** ASVs that vanish or appear when runs are split. **Fix:** per-run inference, then `mergeSequenceTables`, then one chimera removal; carry run as a batch covariate into DA.

### Merge cliff from over-truncation (stage 2)
**Trigger:** truncLen_F + truncLen_R below amplicon length + ~12. **Mechanism:** denoised pairs no longer overlap enough to merge. **Symptom:** near-zero `merged` column, misread as "low diversity". **Fix:** compute the overlap budget first; keep length and loosen `maxEE` on the reverse for long amplicons.

### De novo tree on short reads (stage 5)
**Trigger:** UniFrac/Faith PD on a MAFFT+FastTree tree from ~250 bp reads. **Mechanism:** short reads give an unstable topology and arbitrary midpoint root. **Symptom:** unweighted-UniFrac separation that vanishes under SEPP. **Fix:** use SEPP fragment-insertion or Greengenes2 placement (microbiome/diversity-analysis).

### Sampling-depth sample massacre (stage 6)
**Trigger:** a rarefaction depth above some samples' totals (or `min(sample_sums)`). **Mechanism:** samples below the depth are silently dropped; the lost ones skew low-biomass. **Symptom:** fewer points in the PCoA than samples in the metadata. **Fix:** pick the depth from the alpha-rarefaction plateau, report the dropped-sample list, confirm at a nearby depth.

### Rarefied table reused for DA (stage 6 -> 7)
**Trigger:** feeding `ps_rare` into the DA tools. **Mechanism:** rarefaction discards count information the compositional model needs. **Symptom:** underpowered or distorted DA. **Fix:** keep raw counts; rarefy only into the diversity branch; run DA on the unrarefied `ps`.

### Single-tool DA hit list (stage 7)
**Trigger:** reporting only ALDEx2 (or only the tool that flagged the favored taxon). **Mechanism:** the significant-taxa list depends more on the tool than the biology (Nearing 2022). **Symptom:** "the method found X" with no mention of disagreeing tools. **Fix:** run >=2 CoDA tools, report the intersection as confident and the union as exploratory, name every tool.

### PICRUSt2 reported as activity (stage 8)
**Trigger:** "increased butyrate production" / "upregulated" from predicted KOs. **Mechanism:** PICRUSt2 measured no genes and no transcripts - it re-encodes taxonomy through a fixed lookup. **Symptom:** an activity verb on a predicted pathway, or predicted+taxonomic differences claimed as two independent findings. **Fix:** restrict claims to "potential"; report NSTI; for activity use metatranscriptomics (microbiome/functional-prediction).

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| truncLen budget: truncLen_F + truncLen_R >= amplicon_len + ~12 | DADA2 `mergePairs` `minOverlap` default | below this, denoised pairs cannot merge; the merge cliff is arithmetic, not data |
| `maxEE` c(2,2) (loosen R for long amplicons) | Callahan 2016 *Nat Methods* 13:581 | expected-errors filter beats a hard Q cut; computed on the truncated read |
| assignTaxonomy `minBoot` 50 (default) | Wang 2007 *Appl Environ Microbiol* 73:5261 | RDP floor for reads <=250 nt; ranks below it return NA, not a guess |
| Sampling depth on the alpha-rarefaction plateau (not `min(sample_sums)`) | McMurdie 2014 *PLoS Comput Biol* 10:e1003531 | depth must saturate richness while retaining samples; report the dropped list |
| PERMANOVA permutations >= 999, paired with betadisper | vegan docs; Anderson & Walsh 2013 *Ecol Monogr* 83:557 | resolution floor; separates a location shift from a dispersion difference |
| Rarefy for diversity, NOT for DA | McMurdie 2014; Schloss 2024 *mSphere* 9:e00354-23 | per-analysis decision; DA needs the raw counts |
| Prevalence cut 10-25% before DA | Nearing 2022 *Nat Commun* 13:342; tool defaults | rare features crush the BH denominator; declare and test sensitivity |
| ALDEx2 `we.eBH` <= 0.05 AND `|effect|` > 1 | Gloor 2016 *J Comput Graph Stat* 25:971 | gate on the standardized effect (|effect|>1 = between-group diff exceeds within-condition dispersion), not p alone; large n makes trivial diffs "significant" |
| Consensus of >=2 CoDA tools | Nearing 2022 *Nat Commun* 13:342 | tool choice drives the hit list more than biology; intersection = confident |
| PICRUSt2 `--max_nsti` 2.0 (default) | Douglas 2020 *Nat Biotechnol* 38:685 | ASVs >2 substitutions/site from a reference genome are too extrapolated; report the dropped read fraction |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Near-zero merge rate | truncLen below the overlap budget | recompute the budget; keep length, loosen `maxEE` R |
| Large read fraction "chimeric" | primers not trimmed | cutadapt `--discard-untrimmed` before filtering |
| ASVs vanish/appear when runs split | one error model fit across runs | per-run `learnErrors`, then `mergeSequenceTables` |
| PCoA has fewer points than samples | rarefaction depth dropped low-count samples | lower the depth or report the loss; never assume zero drops |
| adonis2 p<0.05 but groups overlap | dispersion difference, not location | run betadisper/permutest; report both |
| ALDEx2 returns NA effects / errors | proportions or non-integer matrix passed | feed integer COUNTS with taxa in rows |
| Far fewer ANCOM-BC2 hits than expected | `p_adj_method` left at `holm` | set `p_adj_method = 'BH'` deliberately if FDR is wanted |
| Tools disagree on the DA hit list | normal - tool choice drives results | report the consensus and the disagreement, do not cherry-pick |
| PICRUSt2 result with no NSTI numbers | NSTI distribution not reported | summarize `metadata_NSTI`; report ASV+read fraction dropped at NSTI>2 |

## References

- Callahan BJ, McMurdie PJ, Rosen MJ, Han AW, Johnson AJA, Holmes SP. 2016. DADA2: high-resolution sample inference from Illumina amplicon data. *Nat Methods* 13:581-583.
- Martin M. 2011. Cutadapt removes adapter sequences from high-throughput sequencing reads. *EMBnet J* 17:10-12.
- Wang Q, Garrity GM, Tiedje JM, Cole JR. 2007. Naive Bayesian classifier for rapid assignment of rRNA sequences into the new bacterial taxonomy. *Appl Environ Microbiol* 73:5261-5267.
- Janssen S, McDonald D, Gonzalez A, et al. 2018. Phylogenetic placement of exact amplicon sequences improves associations with clinical information. *mSystems* 3:e00021-18.
- McDonald D, Jiang Y, Balaban M, et al. 2024. Greengenes2 unifies microbial data in a single reference tree. *Nat Biotechnol* 42:715-718.
- McMurdie PJ, Holmes S. 2014. Waste not, want not: why rarefying microbiome data is inadmissible. *PLoS Comput Biol* 10:e1003531.
- Schloss PD. 2024. Rarefaction is currently the best approach to control for uneven sequencing effort in amplicon sequence analyses. *mSphere* 9:e00354-23.
- Anderson MJ, Walsh DCI. 2013. PERMANOVA, ANOSIM, and the Mantel test in the face of heterogeneous dispersions: what null hypothesis are you testing? *Ecol Monogr* 83:557-574.
- Fernandes AD, Reid JNS, Macklaim JM, McMurrough TA, Edgell DR, Gloor GB. 2014. Unifying the analysis of high-throughput sequencing datasets by compositional data analysis. *Microbiome* 2:15.
- Gloor GB, Macklaim JM, Fernandes AD. 2016. Displaying Variation in Large Datasets: Plotting a Visual Summary of Effect Sizes. *J Comput Graph Stat* 25:971-979.
- Lin H, Peddada SD. 2020. Analysis of compositions of microbiomes with bias correction. *Nat Commun* 11:3514.
- Nearing JT, Douglas GM, Hayes MG, et al. 2022. Microbiome differential abundance methods produce different results across 38 datasets. *Nat Commun* 13:342.
- Douglas GM, Maffei VJ, Zaneveld JR, et al. 2020. PICRUSt2 for prediction of metagenome functions. *Nat Biotechnol* 38:685-688.

## Related Skills

- microbiome/amplicon-processing - Primer removal, per-run error model, truncLen budget, chimeras, ITS
- reporting/automated-qc-reports - Aggregate FastQC/MultiQC across samples (sample-name resolution; the report is a snapshot, not a gate)
- microbiome/taxonomy-assignment - Region-matched classifier and reference-database choice
- microbiome/diversity-analysis - Sampling depth, tree choice, metric choice, adonis2 + betadisper
- microbiome/differential-abundance - Compositional DA tools and the consensus deliverable
- microbiome/functional-prediction - PICRUSt2 predicted potential gated on NSTI
- microbiome/qiime2-workflow - The QIIME2 artifact/provenance route for the whole chain
- read-qc/adapter-trimming - cutadapt primer removal mechanics before DADA2
- metagenomics/kraken-classification - Shotgun (not amplicon) read classification
- metagenomics/abundance-estimation - Shared compositional/normalization/rarefaction theory
- workflows/metagenomics-pipeline - The shotgun (WGS) equivalent of this amplicon pipeline
<!-- END FILE: workflows/microbiome-pipeline/SKILL.md -->

## 子目录：workflows/multi-omics-pipeline

<!-- BEGIN FILE: workflows/multi-omics-pipeline/SKILL.md -->
---
name: bio-workflows-multi-omics-pipeline
description: Orchestrates VERTICAL bulk multi-omics integration (RNA + protein + methylation on the SAME samples) from harmonization to a validated result, routing to MOFA2 (shared factors), mixOmics/DIABLO (predictive signature), or SNF (patient subtypes). Use when confirming the correspondence is vertical (not horizontal same-features-different-cohorts), joining on a stable sample primary key rather than cbind on assumed row order, normalizing each omic in its OWN space and equalizing block variance BEFORE stacking (or the widest omic hijacks every shared factor), correcting batch ONCE in one place, and validating in a HELD-OUT cohort because in-cohort CV at n<<p is optimistically biased. Hands mechanism to the multi-omics-integration component skills; not a re-teach of any single step.
tool_type: r
primary_tool: MOFA2
workflow: true
depends_on:
  - multi-omics-integration/integration-design
  - multi-omics-integration/data-harmonization
  - multi-omics-integration/mofa-integration
  - multi-omics-integration/mixomics-analysis
  - multi-omics-integration/similarity-network
qc_checkpoints:
  - after_harmonization: "Sample overlap >80% across blocks; join on a stable primary key (MAE sampleMap / MuData obs), never cbind on row order"
  - after_per_block_norm: "Each omic normalized in its OWN space (VST/M-values/log2+MNAR/CLR); missingness per modality <20%"
  - after_scaling: "Per-VIEW variance equalized (scale_views) BEFORE stacking; no single view's feature count dominates"
  - after_integration: "Per-(factor,view) R2 balanced; drop factors <1-2% R2 in ALL views; no single view dominates every factor"
  - after_validation: "Held-out cohort (not in-cohort CV, biased at n<<p); batch correlated with every factor; batch corrected ONCE"
---

## Version Compatibility

Reference examples tested with: MOFA2 1.12+, mixOmics 6.26+, SNFtool 2.3+, clusterProfiler 4.10+, ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Multi-omics Integration Pipeline

**"Integrate my multi-omics datasets"** -> Decide the strategy first, then orchestrate harmonization, the chosen integration method (MOFA2, mixOmics, or SNF), interpretation, and validation - because bulk multi-omics is small-n, huge-p, so an unvalidated integrated result is the default noise outcome.

Before any tool runs, settle the design with multi-omics-integration/integration-design: confirm the data is vertical (different omics on the SAME samples, not the same features across cohorts), map the question to a method (shared factors -> MOFA2, predictive signature -> DIABLO, patient subtypes -> SNF), and plan a held-out cohort because in-cohort cross-validation at small n is optimistically biased. Inspect the per-view variance-explained table to confirm no single omic dominates the shared structure.

## The governing principle

Bulk multi-omics is small-n, huge-p, so an UNVALIDATED integrated result is the DEFAULT noise outcome, not the exception. Every honesty decision is made at a seam before the integrator runs.

1. **The sample-matching key must be VERTICAL, and joined on a stable primary key.** Vertical = different features, SAME samples (what this category is FOR); horizontal (same features, different cohorts) is meta-analysis/batch, a different problem — conflating them is the deepest category error. The shared latent factor is indexed by SAMPLE, so establish the subject primary key ONCE and externalize it (MAE `sampleMap` / consistent MuData `obs_names`); NEVER `cbind`/`pd.concat` on assumed row order (silently mis-pairs subjects). Gene SYMBOLS are display labels, not join keys (MARCH1->MARCHF1, Excel corruption) — join on stable Ensembl IDs.
2. **Each omic is normalized in its OWN space FIRST, then block variance is equalized BEFORE stacking.** A shared-latent integrator decomposes total variance and assumes each feature is ~continuous/Gaussian; the non-negotiable per-omic transforms (RNA-seq -> VST/logCPM never raw counts; methylation -> M-values; prot/metab -> log2 + MNAR-aware; microbiome -> CLR) come first, then per-VIEW scaling (MOFA `scale_views=TRUE`) equalizes each block's CONTRIBUTION. Variance is additive across features, so a block with more features (850k CpGs vs 100 metabolites) casts more votes and hijacks the shared space regardless of biological importance. Both failures are silent.
3. **No factor/subtype/signature is credible until it reproduces in a HELD-OUT cohort.** In-cohort CV at n<<p is optimistically biased (tuning feature selection on the full data then reporting same-data CV inflates AUC by up to ~0.15); the gold standard is an external test set or fully nested CV. Spurious cross-omic correlation is the DEFAULT at p>>n. Batch is corrected ONCE, in ONE place (ComBat each omic AND modeling batch downstream removes it twice and over-shrinks real biology).

**The single best honesty check:** if every shared factor is dominated by one view, the pipeline did not integrate — it re-discovered the biggest omic.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Correspondence axis (VERTICAL, not horizontal) | Whether the integrator's math has anything to align on; conflating the two is the deepest category error |
| Sample primary key (externalized in MAE/MuData) | Correct subject-to-assay linkage; cbind-on-row-order silently mis-pairs subjects |
| Per-block normalization + per-view variance scaling | Whether the widest omic hijacks every factor; done before stacking, never after |
| Validation plan (held-out cohort) | Whether any factor/signature is credible; in-cohort CV at n<<p is optimistically biased |

## Pipeline Overview

```
RNA-seq Data ─────┐
                  │
Proteomics Data ──┼──> Data Harmonization ──> Integration ──> Factors/Components
                  │                                                    │
Metabolomics ─────┘                                                    ▼
                        ┌─────────────────────────────────────────────────────┐
                        │           multi-omics-pipeline                      │
                        ├─────────────────────────────────────────────────────┤
                        │  1. Data Preprocessing per Modality                 │
                        │  2. Sample Harmonization (matching samples)         │
                        │  3. Feature Selection/Filtering                     │
                        │  4. Integration (MOFA2 / mixOmics / SNF)            │
                        │  5. Factor/Component Interpretation                 │
                        │  6. Downstream Analysis                             │
                        └─────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼
                              Integrated Factors + Biomarker Signatures
```

## Complete MOFA2 Workflow

**Goal:** Discover unsupervised shared and view-specific factors across the harmonized omics, then interpret and validate them.

**Approach:** Harmonize to common samples, feature-select per view, train MOFA2, read the per-view variance decomposition first, label factors against biological and technical covariates, and run enrichment on the signed weights.

```r
library(MOFA2)
library(MOFAdata)
library(ggplot2)
library(tidyverse)

# === 1. LOAD AND HARMONIZE DATA ===
# RNA-seq data (samples x genes)
rna <- read.csv('rnaseq_normalized.csv', row.names = 1)
cat('RNA:', nrow(rna), 'samples,', ncol(rna), 'genes\n')

# Proteomics data (samples x proteins)
protein <- read.csv('proteomics_normalized.csv', row.names = 1)
cat('Protein:', nrow(protein), 'samples,', ncol(protein), 'proteins\n')

# Metabolomics data (samples x metabolites)
metab <- read.csv('metabolomics_normalized.csv', row.names = 1)
cat('Metabolites:', nrow(metab), 'samples,', ncol(metab), 'metabolites\n')

# Find common samples
common_samples <- Reduce(intersect, list(rownames(rna), rownames(protein), rownames(metab)))
cat('Common samples:', length(common_samples), '\n')

# Subset to common samples
rna <- rna[common_samples, ]
protein <- protein[common_samples, ]
metab <- metab[common_samples, ]

# === 2. FEATURE SELECTION ===
# Select most variable features per modality
select_variable <- function(data, n = 2000) {
    vars <- apply(data, 2, var, na.rm = TRUE)
    top_features <- names(sort(vars, decreasing = TRUE))[1:min(n, ncol(data))]
    data[, top_features]
}

rna_var <- select_variable(rna, n = 2000)
protein_var <- select_variable(protein, n = 1000)
metab_var <- select_variable(metab, n = 500)

# === 3. CREATE MOFA OBJECT ===
# Prepare data as list of matrices (features x samples)
data_list <- list(
    RNA = t(as.matrix(rna_var)),
    Protein = t(as.matrix(protein_var)),
    Metabolome = t(as.matrix(metab_var))
)

# Create MOFA object
mofa <- create_mofa(data_list)

# Add sample metadata (samples_metadata<- requires a literal 'sample' column)
sample_metadata <- read.csv('sample_metadata.csv')
rownames(sample_metadata) <- sample_metadata$sample_id
sample_metadata$sample <- sample_metadata$sample_id
samples_metadata(mofa) <- sample_metadata[common_samples, ]

# === 4. CONFIGURE AND TRAIN MODEL ===
# Data options
data_opts <- get_default_data_options(mofa)
data_opts$scale_views <- TRUE  # Scale each view

# Model options
model_opts <- get_default_model_options(mofa)
model_opts$num_factors <- 15  # Number of factors to learn

# Training options
train_opts <- get_default_training_options(mofa)
train_opts$maxiter <- 1000
train_opts$convergence_mode <- 'slow'
train_opts$seed <- 42

# Prepare and train
mofa <- prepare_mofa(mofa, data_options = data_opts,
                      model_options = model_opts,
                      training_options = train_opts)

cat('Training MOFA model...\n')
mofa <- run_mofa(mofa, outfile = 'mofa_model.hdf5', use_basilisk = TRUE)

# === 5. ANALYZE FACTORS ===
# Variance explained per factor per view
plot_variance_explained(mofa, max_r2 = 15)
ggsave('variance_explained.png', width = 10, height = 6)

# Factor values
factor_values <- get_factors(mofa)[[1]]

# Correlate factors with biological AND technical covariates; a factor that tracks batch is a batch factor
correlate_factors_with_covariates(mofa, covariates = c('condition', 'batch', 'depth'))

# Factor plots
plot_factor(mofa, factors = 1:4, color_by = 'condition', dot_size = 3)
ggsave('factor_scatter.png', width = 12, height = 10)

# === 6. INTERPRET FACTORS ===
# Get top weights per factor per view
for (f in 1:5) {
    cat('\nFactor', f, ':\n')
    weights <- get_weights(mofa, factors = f, as.data.frame = TRUE)

    for (view in unique(weights$view)) {
        view_weights <- weights[weights$view == view, ]
        view_weights <- view_weights[order(abs(view_weights$value), decreasing = TRUE), ]
        cat('  ', view, ':', paste(head(view_weights$feature, 5), collapse = ', '), '\n')
    }
}

# Heatmap of top features per factor
plot_top_weights(mofa, view = 'RNA', factors = 1:5, nfeatures = 10)
ggsave('top_weights_rna.png', width = 10, height = 8)

# === 7. ENRICHMENT ANALYSIS ===
library(clusterProfiler)
library(org.Hs.eg.db)

# Get RNA weights for factor 1
rna_weights <- get_weights(mofa, views = 'RNA', factors = 1)[[1]][, 1]
top_genes <- names(sort(abs(rna_weights), decreasing = TRUE))[1:200]

# GO enrichment -- use all RNA features as background (not the full genome)
all_rna_genes <- names(rna_weights)
ego <- enrichGO(gene = top_genes,
                universe = all_rna_genes,
                OrgDb = org.Hs.eg.db,
                keyType = 'SYMBOL',
                ont = 'BP',
                pvalueCutoff = 0.05)
ego <- simplify(ego, cutoff = 0.7, by = 'p.adjust')

dotplot(ego, showCategory = 15)
ggsave('factor1_enrichment.png', width = 8, height = 10)

# === 8. DOWNSTREAM: SURVIVAL ANALYSIS ===
library(survival)
library(survminer)

# Add factor values to metadata
surv_data <- data.frame(
    sample = rownames(factor_values),
    factor1 = factor_values[, 1],
    time = sample_metadata[rownames(factor_values), 'survival_time'],
    status = sample_metadata[rownames(factor_values), 'survival_status']
)

# Median split
surv_data$factor1_group <- ifelse(surv_data$factor1 > median(surv_data$factor1), 'High', 'Low')

# Kaplan-Meier
fit <- survfit(Surv(time, status) ~ factor1_group, data = surv_data)
ggsurvplot(fit, data = surv_data, pval = TRUE, risk.table = TRUE)
ggsave('survival_factor1.png', width = 8, height = 8)

# === 9. EXPORT RESULTS ===
# Factor values
write.csv(factor_values, 'mofa_factor_values.csv')

# Weights
all_weights <- get_weights(mofa, as.data.frame = TRUE)
write.csv(all_weights, 'mofa_weights.csv', row.names = FALSE)

cat('\nMOFA analysis complete!\n')
```

## mixOmics DIABLO Workflow

**Goal:** Build a supervised cross-omic signature that discriminates a known outcome, with an honest performance estimate.

**Approach:** Set the design matrix from the goal, tune the component count then keepX inside cross-validation folds with balanced error rate, fit, and report performance from data not used in tuning.

```r
library(mixOmics)

# === 1. PREPARE DATA ===
# Same preprocessing as above
X <- list(
    RNA = as.matrix(rna_var),
    Protein = as.matrix(protein_var),
    Metabolome = as.matrix(metab_var)
)

# Outcome variable
Y <- factor(sample_metadata[common_samples, 'condition'])

# === 2. DESIGN MATRIX (the central DIABLO decision) ===
# off-diagonal trades discrimination vs cross-block correlation: ~1 for a coherent network,
# <0.5 for prediction. 0.1 leans toward prediction and is tutorial convention, not a default.
design <- matrix(0.5, ncol = length(X), nrow = length(X),
                 dimnames = list(names(X), names(X)))
diag(design) <- 0

# === 3. TUNE MODEL ===
# Tune number of components
perf.diablo <- perf(block.splsda(X, Y, ncomp = 5, design = design),
                    validation = 'Mfold', folds = 5, nrepeat = 10)

ncomp <- perf.diablo$choice.ncomp$WeightedVote['Overall.BER', 'max.dist']
cat('Optimal components:', ncomp, '\n')

# Tune number of variables per component
test.keepX <- list(
    RNA = c(10, 25, 50, 100),
    Protein = c(5, 10, 25, 50),
    Metabolome = c(5, 10, 25)
)

tune.diablo <- tune.block.splsda(X, Y, ncomp = ncomp, test.keepX = test.keepX,
                                  design = design, validation = 'Mfold', folds = 5)

optimal.keepX <- tune.diablo$choice.keepX

# === 4. FINAL MODEL ===
diablo.model <- block.splsda(X, Y, ncomp = ncomp,
                              keepX = optimal.keepX, design = design)

# === 5. VISUALIZATION ===
# Sample plot
plotIndiv(diablo.model, ind.names = FALSE, legend = TRUE, title = 'DIABLO Sample Plot')

# Variable plot
plotVar(diablo.model, var.names = FALSE, style = 'graphics', legend = TRUE)

# Circos plot
circosPlot(diablo.model, cutoff = 0.7, line = TRUE,
           color.blocks = c('darkorchid', 'brown1', 'lightgreen'))

# Heatmap
cimDiablo(diablo.model, color.blocks = c('darkorchid', 'brown1', 'lightgreen'),
          margins = c(10, 5))

# === 6. PERFORMANCE (report from data not used to tune; an external test set is the honest estimate) ===
perf.final <- perf(diablo.model, validation = 'Mfold', folds = 5, nrepeat = 10)
perf.final$WeightedVote.error.rate   # matrix: classes + Overall.BER by component

# ROC curves
auc.diablo <- auroc(diablo.model, roc.block = 'RNA', roc.comp = 1)
```

## Similarity Network Fusion (SNF)

**Goal:** Stratify patients into candidate subtypes from the fused multi-omic similarity network.

**Approach:** Standardize each omic, build local-scaled affinity networks, fuse by cross-diffusion, estimate a plausible cluster number, and defend it with a fused-versus-single-omic concordance check before claiming subtypes.

```r
library(SNFtool)

# === 1. CREATE SIMILARITY MATRICES ===
K <- 20       # neighbors for the local kernel bandwidth (10-30)
sigma <- 0.5  # affinityMatrix width (the arg is sigma, not alpha); 0.3-0.8

# standardize per feature, then squared-Euclidean -> root -> local-scaled kernel
views <- lapply(list(rna_var, protein_var, metab_var), function(x) standardNormalization(as.matrix(x)))
affinities <- lapply(views, function(x) affinityMatrix(dist2(x, x)^(1/2), K, sigma))   # dist2 returns SQUARED distance

# === 2. FUSE NETWORKS ===
W <- SNF(affinities, K, t = 20)

# === 3. CLUSTER ON FUSED NETWORK (defend the count, do not assume it) ===
estimateNumberOfClustersGivenGraph(W, NUMC = 2:8)   # four eigengap/rotation estimates - plausibility, not truth
clusters <- spectralClustering(W, K = 3)            # here K is the CLUSTER COUNT
concordanceNetworkNMI(c(affinities, list(W)), 3)    # did fusion beat the best single omic? (Rappoport and Shamir 2018)

# === 4. VISUALIZATION ===
# Plot fused network
displayClustersWithHeatmap(W, clusters)
```

## QC Checkpoints

| Stage | Check | Action if Failed |
|-------|-------|------------------|
| Sample matching | >80% samples shared | Check sample IDs |
| Missing values | <20% per modality | Impute or remove |
| Feature variance | Features vary | Filter low variance |
| Model convergence | ELBO plateau | Increase iterations |
| Factor variance | drop factors below ~1-2% in all views | set drop_factor_threshold; keep fewer factors |
| Variance imbalance | no single view dominates every factor | per-view scaling or filter the wider view harder |
| Validation | held-out cohort, not in-cohort CV | replicate before claiming a biomarker/subtype |

## Workflow Variants

### With Missing Samples
```r
# MOFA2 handles missing views gracefully; create_mofa_from_df wants one row per (sample, feature, value)
to_long <- function(mat, view) {
    df <- as.data.frame(as.table(as.matrix(mat)))   # samples x features -> Var1=sample, Var2=feature, Freq=value (alignment preserved)
    data.frame(sample = as.character(df$Var1), feature = as.character(df$Var2), view = view, value = df$Freq)
}
data_long <- rbind(to_long(rna, 'RNA'), to_long(protein, 'Protein'))
mofa <- create_mofa_from_df(data_long)
```

### Single-cell Multi-omics
Single-cell multimodal data (CITE-seq, 10x Multiome) is a different paradigm - per-cell generative models with abundant observations rather than the bulk small-n regime. Route it to single-cell/multimodal-integration rather than applying this bulk pipeline.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Integrated result on mislabeled subjects (both axes have plausible lengths) | `cbind`/`pd.concat` on assumed sample order | Enforce sample linkage via a container (MAE `sampleMap` / MuData `intersect_obs`); assert shape after every cross-language hop |
| One view dominates every factor | Block scale/feature-count imbalance (850k CpGs vs 100 metabolites) | Per-VIEW scaling (`scale_views=TRUE`), NOT per-feature; filter larger views harder; check per-(factor,view) R2 |
| A near-constant noise feature blown up to variance 1 | Per-feature scaling (`scale=TRUE` in mixOmics) | Aggressive low-variance filtering BEFORE scaling; prefer per-view scaling |
| A "biological" factor that is really batch | Technical variance not regressed out | Correlate every factor with technical covariates (run date, plate, site); exclude a factor tracking batch more than biology |
| AUC inflated by up to ~0.15 | In-cohort CV with feature selection outside the folds | CV must WRAP selection (nested); gold standard is an external test set (`predict()`/`auroc()`) |
| Batch removed twice, real biology over-shrunk | ComBat each omic AND batch in the downstream model | Correct batch ONCE: pre-correct and do not re-enter, OR leave raw and model batch as a covariate |
| Transposed matrices make every gene a "sample" | Bioconductor (samples=cols) vs mixOmics/MOFA (samples=rows) mismatch | Transpose deliberately + assert shape on every cross-package hop |

## References

- Argelaguet R, Velten B, Arnol D, et al (2018) Multi-Omics Factor Analysis - a framework for unsupervised integration of multi-omics data sets. *Molecular Systems Biology* 14:e8124. DOI 10.15252/msb.20178124. (MOFA.)
- Rohart F, Gautier B, Singh A, Le Cao KA (2017) mixOmics: an R package for 'omics feature selection and multiple data integration. *PLoS Computational Biology* 13:e1005752. DOI 10.1371/journal.pcbi.1005752.
- Singh A, Shannon CP, Gautier B, et al (2019) DIABLO: an integrative approach for identifying key molecular drivers from multi-omics assays. *Bioinformatics* 35:3055-3062. DOI 10.1093/bioinformatics/bty1054.
- Wang B, Mezlini AM, Demir F, et al (2014) Similarity network fusion for aggregating data types on a genomic scale. *Nature Methods* 11:333-337. DOI 10.1038/nmeth.2810. (SNF.)
- Rappoport N, Shamir R (2018) Multi-omic and multi-view clustering algorithms: review and cancer benchmark. *Nucleic Acids Research* 46:10546-10562. DOI 10.1093/nar/gky889. (integration is not automatically better than the best single omic.)
- Nygaard V, Rodland EA, Hovig E (2016) Methods that remove batch effects while retaining group differences may lead to exaggerated confidence in downstream analyses. *Biostatistics* 17:29-39. DOI 10.1093/biostatistics/kxv027.

## Related Skills

- multi-omics-integration/integration-design - Method selection, correspondence, and the n<<p discipline (decide first)
- multi-omics-integration/mofa-integration - MOFA2 unsupervised factor analysis
- multi-omics-integration/mixomics-analysis - mixOmics DIABLO/sPLS/MINT methods
- multi-omics-integration/similarity-network - SNF patient stratification
- multi-omics-integration/data-harmonization - Cross-omic preprocessing and scaling
- pathway-analysis/go-enrichment - Factor/signature interpretation
- differential-expression/batch-correction - Batch effects
- clinical-biostatistics/survival-analysis - Survival validation of factors and subtypes
- single-cell/multimodal-integration - Single-cell multimodal integration (different paradigm)
<!-- END FILE: workflows/multi-omics-pipeline/SKILL.md -->

## 子目录：workflows/multiome-pipeline

<!-- BEGIN FILE: workflows/multiome-pipeline/SKILL.md -->
---
name: bio-workflows-multiome-pipeline
description: Orchestrates the end-to-end 10x Multiome (paired scRNA + scATAC) pipeline from Cell Ranger ARC output to a jointly-embedded, annotated object, chaining per-modality QC, AMULET fragment-based ATAC doublet detection, per-modality normalization (RNA SCT/PCA; ATAC TF-IDF/LSI), WNN (or MultiVI) integration, joint clustering, RNA-based annotation, and LinkPeaks peak-to-gene linking. Use when enforcing the shared cell-barcode intersection between modalities (cellranger-ARC not -atac), keeping per-modality QC/doublets before the joint embedding, dropping the depth-correlated LSI component, annotating identity from RNA (ATAC is regulatory state), treating peak-to-gene links as correlational hypotheses, or aggregating to pseudobulk for cross-condition DE. Hands mechanism to the single-cell and atac-seq component skills; not a re-teach of any single step.
tool_type: r
primary_tool: Seurat
goal_approach_exempt: true
workflow: true
depends_on:
  - single-cell/data-io
  - single-cell/preprocessing
  - single-cell/clustering
  - single-cell/multimodal-integration
  - single-cell/scatac-analysis
  - atac-seq/single-cell-atac
  - atac-seq/co-accessibility
  - atac-seq/motif-deviation
qc_checkpoints:
  - after_loading: "Both modalities detected per cell"
  - after_rna_qc: "RNA quality filters passed"
  - after_atac_qc: "TSS enrichment >2, nucleosome signal <4"
  - after_wnn: "Joint embedding separates cell types"
---

## Version Compatibility

Reference examples tested with: Cell Ranger ARC 2.2+, Seurat 5.1+, Signac 1.14+, EnsDb.Hsapiens.v86, BSgenome.Hsapiens.UCSC.hg38 1.4+, ggplot2 3.5+ (AMULET via the standalone java/python tool or scDblFinder's amulet() in R -- ArchR and snapATAC2 ship their OWN simulation-based doublet callers, not AMULET; MultiVI via scvi-tools if using the Python path)

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: `cellranger-arc count` (NOT `cellranger-atac`) emits the paired RNA+ATAC per-nucleus barcodes. Seurat `FindClusters(algorithm=3)` is SLM, not Leiden (1=Louvain, 2=Louvain-multilevel, 3=SLM, 4=Leiden). The `atac_fragments.tsv.gz` must be block-gzipped + tabix-indexed; the Tn5 +4/-5 offset is already applied by 10x -- do not re-shift. Confirm in-tool before quoting.

# Multiome Pipeline

**"Analyze my 10X Multiome data jointly"** -> Orchestrate Cell Ranger ARC processing, Seurat/Signac scRNA+scATAC integration via WNN, chromatin accessibility peak calling, motif enrichment, and gene regulatory network inference.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| `cellranger-arc` run (NOT `cellranger-atac`) | Only ARC emits the joined RNA+ATAC per-nucleus barcodes; -atac gives ATAC-only barcodes and the join is impossible |
| Shared cell-barcode join | RNA and ATAC QC pass DIFFERENT barcodes; the analyzable set is their INTERSECTION. A namespace mismatch (`-1` suffix, RNA vs ATAC whitelist) silently empties the join |
| Same genome build for GEX + ATAC (EnsDb + BSgenome) | Gene activity, LinkPeaks, and motif coordinates require identical build, else peak-to-gene linking is garbage |
| Consensus peak set (multi-sample) | Peaks are dataset-specific; merging samples on discordant peaks fabricates batch structure -- re-quantify against a unified peak set |
| Intron inclusion (GEX half) | Multiome is nuclei (mostly unspliced) -- introns are essential for the RNA UMI totals |

## Pipeline orchestration: the joint-modality decisions that make or break the result

Multiome's defining feature is that RNA and ATAC are measured in the SAME nucleus, so the two assays share one barcode universe and must be reconciled, not analyzed independently. The orchestration decisions:
- The paired-cell anchor is the whole point: keep only barcodes that pass QC in BOTH modalities. RNA and ATAC QC use different metrics (RNA: gene count, mito %; ATAC: TSS enrichment, nucleosome signal, fragment count) and are computed per modality, but the surviving cell set is their intersection. cellranger-arc (not cellranger-atac) produces the paired barcodes; their universes differ. See single-cell/preprocessing and single-cell/scatac-analysis.
- Per-modality QC and doublet detection run BEFORE the joint embedding. ATAC doublets are missed by RNA-based callers (scDblFinder/Scrublet, see single-cell/doublet-detection) and need a fragment-based detector such as AMULET (see single-cell/scatac-analysis); resolving them after WNN lets fake intermediate states drive the joint clustering.
- Drop the depth-correlated LSI component before joint analysis. The first ATAC LSI/SVD component usually (not always) captures sequencing depth rather than biology; check with DepthCor and exclude whichever component correlates with depth (commonly #1, hence dims 2:30 in WNN). Forgetting this lets depth dominate the ATAC contribution to the joint graph.
- WNN vs a generative joint embedding is a real choice. Seurat/Signac WNN learns a per-cell modality weight on precomputed PCA + LSI and is the default when both modalities are well processed; MultiVI (scvi-tools) jointly models RNA + ATAC counts end-to-end and handles batch and mosaic (RNA-only or ATAC-only) cells better. WNN cannot integrate cells missing a modality. See single-cell/multimodal-integration; verify current best practice against installed docs.
- Embed (WNN) then cluster then annotate, and annotate from RNA primarily. Gene-activity scores derived from ATAC are an approximation of expression, so cell-type labels come from RNA markers; ATAC informs the regulatory state, not the identity call. See single-cell/clustering, single-cell/markers-annotation, single-cell/cell-annotation.
- Peak-to-gene linking is correlational, not causal. LinkPeaks correlates peak accessibility with gene expression across cells within a window; a link is a hypothesis to validate, not a proven enhancer-target pair. For genome-wide enhancer-gene mapping use ABC/ENCODE-rE2G. See atac-seq/co-accessibility and atac-seq/enhancer-gene-linking.
- Cross-condition questions still need pseudobulk and separate composition testing. Condition DE on either modality aggregates RAW counts per sample x cell type (cells-as-replicates is pseudoreplication, Squair 2021); proportion shifts between conditions are tested separately and can masquerade as DE. See single-cell/differential-abundance and differential-expression/deseq2-basics.

## Workflow Overview

```
10X Multiome data
    |
    v
[1. Load Data] ---------> Read RNA + ATAC
    |
    v
[2. RNA Processing] ----> Standard scRNA workflow
    |
    v
[3. ATAC Processing] ---> Peak calling, LSI
    |
    v
[4. WNN Integration] ---> Weighted nearest neighbors
    |
    v
[5. Joint Analysis] ----> Clustering, markers
    |
    v
[6. Linked Features] ---> Gene-peak links
    |
    v
Integrated multiome object
```

## Step 1: Load Multiome Data

```r
library(Seurat)
library(Signac)
library(EnsDb.Hsapiens.v86)
library(ggplot2)

# Load RNA
rna_counts <- Read10X_h5('filtered_feature_bc_matrix.h5')
# For multiome, this returns a list with 'Gene Expression' and 'Peaks'

# Create Seurat object with RNA
seurat_obj <- CreateSeuratObject(
    counts = rna_counts$`Gene Expression`,
    assay = 'RNA'
)

# Load ATAC
atac_counts <- rna_counts$Peaks
# Or from fragments file
frags <- CreateFragmentObject('atac_fragments.tsv.gz', cells = colnames(seurat_obj))

# EnsDb returns Ensembl seqnames (1,2,X); cellranger-arc peaks/fragments are UCSC (chr1,chr2).
# Convert, or TSSEnrichment and LinkPeaks silently fail on zero seqname overlap.
annotations <- GetGRangesFromEnsDb(ensdb = EnsDb.Hsapiens.v86)
seqlevelsStyle(annotations) <- 'UCSC'

# Create ChromatinAssay
atac_assay <- CreateChromatinAssay(
    counts = atac_counts,
    sep = c(':', '-'),
    fragments = frags,
    annotation = annotations
)

seurat_obj[['ATAC']] <- atac_assay
```

## Step 2: RNA Quality Control and Processing

```r
# QC metrics
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')

# Filter
seurat_obj <- subset(seurat_obj,
    nCount_RNA > 1000 &
    nCount_RNA < 25000 &
    percent.mt < 20
)

# Normalize RNA
seurat_obj <- SCTransform(seurat_obj, assay = 'RNA', verbose = FALSE)

# PCA
seurat_obj <- RunPCA(seurat_obj, assay = 'SCT', verbose = FALSE)
```

## Step 3: ATAC Quality Control and Processing

```r
# ATAC QC metrics
DefaultAssay(seurat_obj) <- 'ATAC'

seurat_obj <- NucleosomeSignal(seurat_obj)
seurat_obj <- TSSEnrichment(seurat_obj)

# Visualize
VlnPlot(seurat_obj, features = c('nCount_ATAC', 'TSS.enrichment', 'nucleosome_signal'),
        pt.size = 0, ncol = 3)

# Filter ATAC
seurat_obj <- subset(seurat_obj,
    nCount_ATAC > 1000 &
    nCount_ATAC < 100000 &
    TSS.enrichment > 2 &
    nucleosome_signal < 4
)

# Normalize ATAC (TF-IDF + SVD = LSI)
seurat_obj <- RunTFIDF(seurat_obj)
seurat_obj <- FindTopFeatures(seurat_obj, min.cutoff = 'q0')
seurat_obj <- RunSVD(seurat_obj)

# Check LSI components (first often correlates with depth)
DepthCor(seurat_obj)
```

## Step 3b: Doublet detection (per modality, BEFORE WNN)

Remove doublets before the joint embedding, or fake intermediate states drive the joint clustering. RNA-based callers (scDblFinder/Scrublet) MISS ATAC doublets -- ATAC needs a fragment-based caller (AMULET), run on the same nuclei. Detect per modality, drop the union of doublets, then build WNN. Mechanism: single-cell/doublet-detection (RNA) and single-cell/scatac-analysis (AMULET).

## Step 4: Weighted Nearest Neighbors (WNN)

```r
# Build WNN graph using both modalities
seurat_obj <- FindMultiModalNeighbors(
    seurat_obj,
    reduction.list = list('pca', 'lsi'),
    dims.list = list(1:30, 2:30),  # Skip LSI component 1 if depth-correlated
    modality.weight.name = 'RNA.weight'
)

# UMAP on WNN graph
seurat_obj <- RunUMAP(seurat_obj, nn.name = 'weighted.nn',
                       reduction.name = 'wnn.umap', reduction.key = 'wnnUMAP_')

# Cluster on WNN
seurat_obj <- FindClusters(seurat_obj, graph.name = 'wsnn',
                            algorithm = 3, resolution = 0.5, verbose = FALSE)
```

## Step 5: Visualization and Markers

```r
# Compare modality-specific and joint embeddings
p1 <- DimPlot(seurat_obj, reduction = 'pca', label = TRUE) + ggtitle('RNA PCA')
p2 <- DimPlot(seurat_obj, reduction = 'lsi', label = TRUE) + ggtitle('ATAC LSI')
p3 <- DimPlot(seurat_obj, reduction = 'wnn.umap', label = TRUE) + ggtitle('WNN UMAP')
p1 + p2 + p3

# Modality weights per cell
VlnPlot(seurat_obj, features = 'RNA.weight', group.by = 'seurat_clusters', pt.size = 0)

# Find markers (RNA)
DefaultAssay(seurat_obj) <- 'SCT'
rna_markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25)

# Find markers (ATAC - differentially accessible peaks)
DefaultAssay(seurat_obj) <- 'ATAC'
atac_markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.05,
                                test.use = 'LR', latent.vars = 'nCount_ATAC')
```

## Step 6: Gene-Peak Linkage

```r
# Link peaks to genes
DefaultAssay(seurat_obj) <- 'ATAC'
seurat_obj <- RegionStats(seurat_obj, genome = BSgenome.Hsapiens.UCSC.hg38)

seurat_obj <- LinkPeaks(
    seurat_obj,
    peak.assay = 'ATAC',
    expression.assay = 'SCT',
    genes.use = c('CD8A', 'CD4', 'MS4A1', 'CD14')  # Example genes
)

# Visualize links
CoveragePlot(seurat_obj, region = 'CD8A', features = 'CD8A',
             expression.assay = 'SCT', extend.upstream = 10000, extend.downstream = 10000)
```

## Complete Workflow Script

```r
library(Seurat)
library(Signac)
library(EnsDb.Hsapiens.v86)
library(BSgenome.Hsapiens.UCSC.hg38)
library(ggplot2)

# Configuration
data_dir <- 'multiome_output'
output_dir <- 'multiome_results'
dir.create(output_dir, showWarnings = FALSE)

# === Load Data ===
cat('Loading data...\n')
counts <- Read10X_h5(file.path(data_dir, 'filtered_feature_bc_matrix.h5'))
frags <- file.path(data_dir, 'atac_fragments.tsv.gz')

seurat_obj <- CreateSeuratObject(counts = counts$`Gene Expression`, assay = 'RNA')
annotations <- GetGRangesFromEnsDb(ensdb = EnsDb.Hsapiens.v86)
seqlevelsStyle(annotations) <- 'UCSC'   # match cellranger-arc UCSC seqnames or TSS/LinkPeaks fail
seurat_obj[['ATAC']] <- CreateChromatinAssay(
    counts = counts$Peaks,
    sep = c(':', '-'),
    fragments = frags,
    annotation = annotations
)
cat('Cells:', ncol(seurat_obj), '\n')

# === RNA QC ===
cat('RNA QC...\n')
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')
seurat_obj <- subset(seurat_obj, nCount_RNA > 1000 & nCount_RNA < 25000 & percent.mt < 20)

# === ATAC QC ===
cat('ATAC QC...\n')
DefaultAssay(seurat_obj) <- 'ATAC'
seurat_obj <- NucleosomeSignal(seurat_obj)
seurat_obj <- TSSEnrichment(seurat_obj)
seurat_obj <- subset(seurat_obj, nCount_ATAC > 1000 & TSS.enrichment > 2 & nucleosome_signal < 4)
cat('After QC:', ncol(seurat_obj), 'cells\n')

# === Process RNA ===
cat('Processing RNA...\n')
DefaultAssay(seurat_obj) <- 'RNA'
seurat_obj <- SCTransform(seurat_obj, verbose = FALSE)
seurat_obj <- RunPCA(seurat_obj, verbose = FALSE)

# === Process ATAC ===
cat('Processing ATAC...\n')
DefaultAssay(seurat_obj) <- 'ATAC'
seurat_obj <- RunTFIDF(seurat_obj)
seurat_obj <- FindTopFeatures(seurat_obj, min.cutoff = 'q0')
seurat_obj <- RunSVD(seurat_obj)

# === WNN Integration ===
cat('WNN integration...\n')
seurat_obj <- FindMultiModalNeighbors(seurat_obj,
    reduction.list = list('pca', 'lsi'),
    dims.list = list(1:30, 2:30),
    modality.weight.name = 'RNA.weight'
)
seurat_obj <- RunUMAP(seurat_obj, nn.name = 'weighted.nn',
    reduction.name = 'wnn.umap', reduction.key = 'wnnUMAP_')
seurat_obj <- FindClusters(seurat_obj, graph.name = 'wsnn', algorithm = 3, resolution = 0.5, verbose = FALSE)

# === Save ===
saveRDS(seurat_obj, file.path(output_dir, 'multiome_analyzed.rds'))

# === Plots ===
pdf(file.path(output_dir, 'wnn_umap.pdf'), width = 10, height = 8)
DimPlot(seurat_obj, reduction = 'wnn.umap', label = TRUE)
dev.off()

cat('Results saved to:', output_dir, '\n')
cat('Clusters:', length(unique(seurat_obj$seurat_clusters)), '\n')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Near-empty joint object / no cells after join | RNA vs ATAC barcode namespace mismatch (`-1` suffix, different whitelist) | Reconcile barcodes; intersect on identical strings; confirm cellranger-ARC (not -atac) |
| ATAC depth dominates the joint graph | Kept the depth-correlated LSI component | `DepthCor` -> drop it (WNN `dims.list` `2:30` for ATAC) |
| Fake intermediate joint clusters | ATAC doublets not removed (RNA caller is blind to them) | AMULET fragment-based doublet call per modality before WNN |
| Cell types mislabeled | Annotated from ATAC gene-activity | Annotate identity from RNA markers; activity is a cluster-level proxy |
| Spurious batch across multi-sample multiome | Merged on discordant peak sets | Unify peaks and re-quantify |
| "Enhancer regulates gene" overclaim | Read LinkPeaks correlation as causal | Treat as a composition-confounded hypothesis; validate |
| Inflated cross-condition DE | Tested cells as replicates on either modality | Pseudobulk RAW per sample x cell-type (Squair 2021) |

## References

- Hao Y, Hao S, Andersen-Nissen E, et al (2021) Integrated analysis of multimodal single-cell data. *Cell* 184:3573-3587.e29. DOI 10.1016/j.cell.2021.04.048. (WNN.)
- Ashuach T, Gabitto MI, Koodli RV, et al (2023) MultiVI: deep generative model for the integration of multimodal data. *Nature Methods* 20:1222-1231. DOI 10.1038/s41592-023-01909-9. (mosaic-capable joint RNA+ATAC alternative to WNN.)
- Squair JW, Gautier M, Kathe C, et al (2021) Confronting false discoveries in single-cell differential expression. *Nature Communications* 12:5692. DOI 10.1038/s41467-021-25960-2. (pseudobulk for cross-condition DE.)

## Related Skills

- single-cell/data-io - Loading 10X, h5ad, RDS, and h5mu formats
- single-cell/preprocessing - Per-modality QC and normalization choice
- single-cell/doublet-detection - RNA-based and hashing doublet removal
- single-cell/clustering - Resolution sweep and cluster validation on the joint graph
- single-cell/markers-annotation - Marker discovery, manual labeling, and pseudobulk condition DE
- single-cell/cell-annotation - Automated reference-based label transfer from the RNA modality
- single-cell/differential-abundance - Test whether cell-type proportions shifted between conditions
- single-cell/multimodal-integration - WNN, totalVI/MultiVI, and MOFA joint-embedding details
- single-cell/scatac-analysis - ATAC-specific processing, LSI, gene activity, and AMULET fragment-based doublet detection
- differential-expression/deseq2-basics - Pseudobulk condition DE engine for aggregated counts
- atac-seq/single-cell-atac - Signac / ArchR / SnapATAC2 ecosystem decision; AMULET; cellranger-arc
- atac-seq/co-accessibility - Cicero / ArchR getCoAccessibility for cis-regulatory inference
- atac-seq/enhancer-gene-linking - ABC / ENCODE-rE2G for enhancer-gene mapping
- atac-seq/motif-deviation - chromVAR for per-cell TF motif activity
- atac-seq/footprinting - scprinter for sc footprinting
- workflows/grn-pipeline - Downstream: the paired object feeds SCENIC+ enhancer-GRN inference (Path B)
<!-- END FILE: workflows/multiome-pipeline/SKILL.md -->

## 子目录：workflows/neoantigen-pipeline

<!-- BEGIN FILE: workflows/neoantigen-pipeline/SKILL.md -->
---
name: bio-workflows-neoantigen-pipeline
description: Orchestrates neoantigen discovery from somatic variants to ranked vaccine candidates, chaining HLA typing (OptiType/arcasHLA + LOHHLA), VEP annotation (Wildtype+Frameshift plugins) + expression/readcount annotation, proximal-variant phasing, pVACseq MHC-I/II binding, CCF/clonality, and immunogenicity/quality ranking. Use when recognizing that binding is single-digit PPV and the critical steps are downstream (full-resolution HLA + LOH gating, proximal-variant phasing, clonality from purity+CN not raw VAF, expression), sequencing normalize+annotate -> phase -> HLA -> binding -> quality in the defensible order, dropping candidates on LOH-lost alleles, supplying --phased-proximal-variants-vcf so the mutant peptide is real, or ranking WITHIN patient rather than a fixed IC50 threshold. Hands mechanism to the immunoinformatics component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: pVACtools
goal_approach_exempt: true
workflow: true
depends_on:
  - clinical-databases/hla-typing
  - immunoinformatics/mhc-binding-prediction
  - immunoinformatics/mhc-class-ii-prediction
  - immunoinformatics/neoantigen-prediction
  - immunoinformatics/immunogenicity-scoring
  - immunoinformatics/epitope-prediction
qc_checkpoints:
  - after_hla: "HLA types resolved to 4-digit, coverage adequate"
  - after_binding: "Predictions for ALL alleles (LOH-lost alleles dropped); ranked within patient, not hard-thresholded across patients"
  - after_neoantigen: "Expressed (RNA-confirmed); clonality via CCF from purity+CN, not raw VAF"
  - after_scoring: "Top candidates are a tier-1 hypothesis list for MS + T-cell validation"
---

## Version Compatibility

Reference examples tested with: Ensembl VEP 111+, pVACtools 4.1+ (Frameshift plugin REPLACED the legacy Downstream in 2.0+), MHCflurry 2.1+, NetMHCpan 4.1, OptiType 1.3+ / arcasHLA, LOHHLA, WhatsHap 2.0+ (phasing), matplotlib 3.8+, numpy 1.26+, pandas 2.2+, seaborn 0.13+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Neoantigen Pipeline

**"Predict neoantigens from my tumor sequencing data"** -> Orchestrate HLA typing (OptiType), somatic variant calling, pVACtools neoantigen prediction, MHC binding scoring, and immunogenicity-based candidate ranking for personalized cancer immunotherapy.

Complete workflow from somatic variants to ranked neoantigen vaccine candidates for personalized cancer immunotherapy.

## Key Judgment -- binding is the easy part; PPV lives downstream

A binding-only pipeline has single-digit-percent positive predictive value (TESLA; Wells 2020 Cell 183:818). The critical steps are downstream of binding: correct full-resolution HLA typing (wrong allele = confident garbage), HLA loss-of-heterozygosity (run LOHHLA and DROP candidates on a lost allele; it invalidates predictions silently), proximal-variant phasing (supply `--phased-proximal-variants-vcf` or the mutant peptide is wrong), cancer cell fraction for clonality (clonal beats subclonal; use purity + copy number, not raw VAF), expression, and quality features (agretopicity, foreignness). Treat the ranked output as a tier-1 hypothesis list for immunopeptidomics MS and functional T-cell validation, not a final answer. Add MHC class II (CD4) neoantigens for vaccine help (see immunoinformatics/mhc-class-ii-prediction). Note on DAI below: agretopicity is most often the WT/MT binding ratio; whichever form is used, an anchor-position mutation inflates it without changing the TCR-facing surface, and a barely-presented WT makes it unstable; pair it with anchor evaluation.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| HLA typing at full 4-digit resolution (class I + II) | A wrong allele is confident garbage; every binding prediction inherits it; reconcile DNA vs RNA calls |
| Variant source + somatic caller (matched-normal preferred) | Tumor-only calling leaks germline; indels/frameshifts are disproportionately valuable; expression must be RNA-confirmed and annotated INTO the VCF |
| Proximal-variant phasing | Without it the mutant peptide is one the tumor never makes; germline SNPs in cis are especially treacherous |
| HLA-LOH gate | Candidates on a lost allele are silently invalid (~17% pan-cancer, 30%+ HNSCC/NSCLC/cervical) |

## The canonical order and why

Somatic PASS calls -> normalize + VEP-annotate (Wildtype + Frameshift plugins) -> annotate expression + DNA/RNA readcounts INTO the VCF -> PHASE proximal variants -> HLA typing + LOHHLA -> MHC binding -> clonality (CCF from purity+CN) -> quality features -> tier/rank -> pVACview review.

- **Order-trap 1 - normalize + annotate with the RIGHT plugins BEFORE pVACseq.** pVACseq needs the Wildtype plugin (matched WT peptide -> agretopicity) and the Frameshift plugin (novel ORF); Frameshift REPLACED the legacy Downstream in pVACtools 2.0+. Normalize before annotate.
- **Order-trap 2 - PHASE proximal variants BEFORE translating the mutant peptide.** THE review-sinker: editing variants independently yields a peptide the patient never makes. Merge somatic+germline, phase (WhatsHap/GATK), supply `--phased-proximal-variants-vcf`.
- **Order-trap 3 - HLA typing (+ LOHHLA) BEFORE binding.** Binding is per-allele; a wrong or lost allele makes every downstream prediction garbage. Drop LOH-lost alleles before ranking.
- **Order-trap 4 - CCF/clonality from purity+copy-number BEFORE calling something subclonal.** Low purity makes clonal look subclonal; correct VAF to cancer-cell fraction (copy-number/allele-specific-copy-number). Clonal beats subclonal.
- **Order-trap 5 - rank WITHIN patient; do NOT hard-threshold IC50 across patients.** Immunogenicity scores are relative.

## Workflow Overview

```
Somatic VCF (annotated) + Tumor RNA-seq (optional)
        |
        v
[1. HLA Typing] --> arcasHLA / OptiType (if types not provided)
        |
        v
[2. MHC Binding Prediction] --> MHCflurry / NetMHCpan
        |
        v
[3. Neoantigen Calling] --> pVACseq
        |
        v
[4. Immunogenicity Scoring] --> Multi-factor ranking
        |
        v
Ranked Vaccine Candidates (TSV + visualizations)
```

## Prerequisites (Ensembl VEP 111+)

```bash
pip install pvactools mhcflurry vatools

mhcflurry-downloads fetch

conda install -c bioconda ensembl-vep arcas-hla optitype
```

## Primary Path: pVACseq Pipeline

### Step 1: HLA Typing (if not provided)

HLA types are critical for MHC binding prediction. If not already known from clinical testing:

```bash
# From tumor RNA-seq BAM
arcasHLA extract tumor.bam -t 8 -o hla_output/
arcasHLA genotype hla_output/tumor.extracted.1.fq.gz hla_output/tumor.extracted.2.fq.gz \
    -g A,B,C,DRB1,DQB1,DQA1,DPB1,DPA1 -t 8 -o hla_output/   # type the DQA1/DPA1 alpha chains too: NetMHCIIpan needs PAIRED DQ/DP alleles

# Parse results
cat hla_output/tumor.genotype.json
```

```python
import json

with open('hla_output/tumor.genotype.json') as f:
    hla_data = json.load(f)

hla_alleles = []
for gene, alleles in hla_data.items():
    for allele in alleles:
        # arcasHLA emits 3-field alleles (A*01:01:01); pVACseq/IEDB validate 2-field (HLA-A*01:01)
        hla_alleles.append('HLA-' + ':'.join(allele.split(':')[:2]))

# Format for pVACseq: HLA-A*02:01,HLA-A*24:02,HLA-B*07:02,...
hla_string = ','.join(hla_alleles)
print(f'HLA alleles: {hla_string}')
```

### Step 2: VCF Annotation with VEP

pVACseq requires VEP-annotated VCF with specific fields:

```bash
# Annotate somatic VCF
vep --input_file somatic.vcf \
    --output_file somatic.vep.vcf \
    --format vcf --vcf --symbol --terms SO \
    --plugin Frameshift --plugin Wildtype \
    --offline --cache \
    --pick --fork 4

# Add expression data (optional but recommended)
# Positionals: <vcf> <expression_file> {kallisto,stringtie,cufflinks,custom} {gene,transcript}
vcf-expression-annotator somatic.vep.vcf \
    expression.tsv custom gene \
    -s tumor_sample --id-column gene_id --expression-column tpm \
    -o somatic.vep.expression.vcf

# PHASE proximal variants (the review-sinker). Merge somatic + germline, phase with WhatsHap,
# and pass the result to pVACseq via --phased-proximal-variants-vcf so a second variant in the
# same codon-window (esp. a germline SNP in cis) yields the peptide the tumor ACTUALLY makes.
whatshap phase -o phased.vcf.gz --reference reference.fa somatic_plus_germline.vcf.gz tumor.bam
tabix -p vcf phased.vcf.gz
```

### Step 3: Run pVACseq (Ensembl VEP 111+)

```bash
# Basic run with MHC Class I
pvacseq run \
    somatic.vep.vcf \
    tumor_sample \
    "HLA-A*02:01,HLA-A*24:02,HLA-B*07:02,HLA-B*44:02,HLA-C*07:02,HLA-C*05:01" \
    MHCflurry MHCnuggetsI NetMHCpan \
    pvacseq_output/ \
    -e1 8,9,10,11 \
    --iedb-install-directory /path/to/iedb \
    -t 8

# With expression filtering
pvacseq run \
    somatic.vep.expression.vcf \
    tumor_sample \
    "HLA-A*02:01,HLA-A*24:02,HLA-B*07:02,HLA-B*44:02" \
    MHCflurry NetMHCpan \
    pvacseq_output/ \
    -e1 8,9,10,11 \
    --phased-proximal-variants-vcf phased.vcf.gz \
    --tumor-purity 0.7 \
    --tdna-vaf 0.1 \
    --expn-val 1 \
    -t 8
```

Drop candidates on HLA-LOH-lost alleles (run LOHHLA/DASH) BEFORE ranking, and correct clonality to cancer-cell fraction (CCF from purity + copy number, not raw VAF; see copy-number/allele-specific-copy-number). The raw-VAF filter below is a coarse proxy.

### Step 4: Filter and Rank Candidates

```python
import pandas as pd
import numpy as np

results = pd.read_csv('pvacseq_output/MHC_Class_I/tumor_sample.filtered.tsv', sep='\t')

# Binding affinity filter (IC50 <500nM considered strong binder)
# IC50 <500nM: strong binder; 500-5000nM: weak binder
strong_binders = results[results['Median MT IC50 Score'] < 500].copy()

# Differential agretopicity index (DAI): WT/MT IC50 ratio (== pVACtools Fold Change), matching the
# WT/MT ratio definition. DAI > 1 = MT binds better than WT (mutation created/improved binding); higher = more tumor-specific.
strong_binders['DAI'] = strong_binders['Median WT IC50 Score'] / strong_binders['Median MT IC50 Score']

# Expression filter (if available)
if 'Gene Expression' in strong_binders.columns:
    # TPM >1 ensures detectable expression
    strong_binders = strong_binders[strong_binders['Gene Expression'] > 1]

# VAF filter: prioritize clonal mutations
# VAF >0.1 ensures mutation present in substantial tumor fraction
strong_binders = strong_binders[strong_binders['Tumor DNA VAF'] > 0.1]

# Multi-factor scoring
def immunogenicity_score(row):
    score = 0
    # Strong binding (IC50 <150nM is very strong)
    if row['Median MT IC50 Score'] < 150:
        score += 3
    elif row['Median MT IC50 Score'] < 500:
        score += 2

    # High DAI (tumor-specificity). DAI is the WT/MT IC50 ratio: >1 = MT binds better than WT.
    if row['DAI'] > 10:
        score += 2
    elif row['DAI'] > 2:
        score += 1

    # Clonal mutation (high VAF)
    if row['Tumor DNA VAF'] > 0.3:
        score += 2
    elif row['Tumor DNA VAF'] > 0.15:
        score += 1

    # Expressed (if available)
    if 'Gene Expression' in row.index and row['Gene Expression'] > 10:
        score += 1

    return score

strong_binders['Immunogenicity Score'] = strong_binders.apply(immunogenicity_score, axis=1)

# Rank by composite score
ranked = strong_binders.sort_values('Immunogenicity Score', ascending=False)

# Top candidates for vaccine
top_candidates = ranked.head(20)
top_candidates.to_csv('top_neoantigen_candidates.tsv', sep='\t', index=False)

print(f'Total strong binders: {len(strong_binders)}')
print(f'Top 20 candidates exported')
print(ranked[['Gene Name', 'MT Epitope Seq', 'HLA Allele', 'Median MT IC50 Score', 'DAI', 'Immunogenicity Score']].head(10))
```

### Step 5: MHC Class II Neoantigens (CD4+ T cell help)

```bash
pvacseq run \
    somatic.vep.vcf \
    tumor_sample \
    "DRB1*01:01,DRB1*07:01,DQA1*05:01-DQB1*02:01,DQA1*03:01-DQB1*03:01" \
    MHCnuggetsII NetMHCIIpan \
    pvacseq_class2_output/ \
    -e2 15 \
    --iedb-install-directory /path/to/iedb \
    -t 8
```

## Alternative: Standalone MHCflurry

For quick binding predictions without full pVACseq pipeline:

```python
from mhcflurry import Class1PresentationPredictor

predictor = Class1PresentationPredictor.load()

peptides = ['SIINFEKL', 'GILGFVFTL', 'NLVPMVATV']
alleles = ['HLA-A*02:01', 'HLA-B*07:02']

results = predictor.predict(peptides=peptides, alleles=alleles,
                            include_affinity_percentile=True, verbose=0)
print(results[['peptide', 'best_allele', 'presentation_score', 'affinity', 'affinity_percentile']])
```

## Visualization

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# IC50 distribution
ax1 = axes[0]
ax1.hist(ranked['Median MT IC50 Score'], bins=50, edgecolor='black')
ax1.axvline(500, color='red', linestyle='--', label='500nM threshold')
ax1.set_xlabel('Median MT IC50 (nM)')
ax1.set_ylabel('Count')
ax1.set_title('Binding Affinity Distribution')
ax1.legend()

# DAI vs IC50
ax2 = axes[1]
scatter = ax2.scatter(ranked['Median MT IC50 Score'], ranked['DAI'],
                      c=ranked['Immunogenicity Score'], cmap='viridis', alpha=0.7)
ax2.set_xlabel('MT IC50 (nM)')
ax2.set_ylabel('Differential Agretopicity Index')
ax2.set_title('Tumor Specificity vs Binding')
plt.colorbar(scatter, ax=ax2, label='Immunogenicity Score')

# Top genes
ax3 = axes[2]
gene_counts = ranked['Gene Name'].value_counts().head(15)
gene_counts.plot(kind='barh', ax=ax3)
ax3.set_xlabel('Number of Neoantigens')
ax3.set_title('Top Genes with Neoantigens')

plt.tight_layout()
plt.savefig('neoantigen_summary.pdf')
```

## Parameter Recommendations

| Step | Parameter | Value | Rationale |
|------|-----------|-------|-----------|
| pVACseq | -e1 | 8,9,10,11 | MHC-I binds 8-11mer peptides |
| pVACseq | -e2 | 15 | MHC-II binds 13-25mer, 15 is core |
| Filtering | IC50 | <500nM | Standard strong binder threshold |
| Filtering | VAF | >0.1 | Ensures clonal representation |
| Filtering | Expression | >1 TPM | Detectable transcription |
| Ranking | DAI (WT/MT IC50 ratio) | >2 moderate, >10 strong | MT binds better than WT (>1); higher = more tumor-specific |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Peptides the tumor never makes | Proximal variants edited independently (unphased) | `--phased-proximal-variants-vcf` (WhatsHap/GATK); include germline in cis |
| Frameshift ORFs lost / no agretopicity | Wrong/legacy VEP plugin (Downstream instead of Frameshift; missing Wildtype) | `pvacseq install_vep_plugin`; run `--plugin Wildtype --plugin Frameshift` |
| Confident but invalid predictions | HLA allele wrong or on a LOH-lost haplotype | Full 4-digit typing + LOHHLA drop before ranking |
| `--expn-val`/VAF filters silently pass everything | Expression/readcounts not annotated into the VCF | `vcf-expression-annotator` + `vcf-readcount-annotator` before pVACseq |
| Clonal candidate mis-tiered subclonal | Raw VAF used as clonality on a low-purity tumor | CCF from purity + copy number (copy-number/allele-specific-copy-number) |
| Candidates mis-ranked across patients | Fixed IC50 threshold applied cross-patient | Rank WITHIN patient (immunoinformatics/immunogenicity-scoring) |
| No neoantigens found | Low mutation burden | Lower IC50 threshold to 1000nM; check TMB/MSI first |

## References

- Hundal J, Kiwala S, McMichael J, et al (2020) pVACtools: a computational toolkit to identify and visualize cancer neoantigens. *Cancer Immunology Research* 8:409-420. DOI 10.1158/2326-6066.CIR-19-0401.
- Wells DK, van Buuren MM, Dang KK, et al (2020) Key parameters of tumor epitope immunogenicity revealed through a consortium approach improve neoantigen prediction (TESLA). *Cell* 183:818-834. DOI 10.1016/j.cell.2020.09.015. (single-digit PPV of binding-only.)
- McGranahan N, Rosenthal R, Hiley CT, et al (2017) Allele-specific HLA loss and immune escape in lung cancer evolution. *Cell* 171:1259-1271. DOI 10.1016/j.cell.2017.10.001. (LOHHLA.)
- Wood MA, Nguyen A, Struck AJ, et al (2020) neoepiscope improves neoepitope prediction with multivariant phasing. *Bioinformatics* 36:713-720. DOI 10.1093/bioinformatics/btz653. (phasing matters.)

## Output Files

| File | Description |
|------|-------------|
| `*.filtered.tsv` | pVACseq filtered neoantigens |
| `*.all_epitopes.tsv` | All predicted epitopes |
| `top_neoantigen_candidates.tsv` | Ranked vaccine candidates |
| `neoantigen_summary.pdf` | Visualization figures |

## Related Skills

- immunoinformatics/mhc-binding-prediction - MHCflurry parameters; BA vs EL, %Rank vs nM, abundance bias
- immunoinformatics/mhc-class-ii-prediction - class II (CD4) neoantigens for vaccine help
- immunoinformatics/neoantigen-prediction - pVACtools details; LOHHLA, phasing, clonality
- immunoinformatics/immunogenicity-scoring - rank within patient (don't threshold); fitness-model quality
- immunoinformatics/epitope-prediction - B-cell epitopes
- clinical-databases/hla-typing - HLA typing (T1K is the 2024-2026 all-rounder; OptiType for class I; arcasHLA for RNA-seq); check HLA-LOH via LOHHLA / DASH which abolishes neoantigen presentation in ~17% pan-cancer (~30%+ HNSCC / NSCLC / cervical)
- clinical-databases/tumor-mutational-burden - TMB-H pan-tumor ICI biomarker; check before neoantigen-vaccine candidate selection
- clinical-databases/msi-detection - MSI-H / dMMR pan-tumor ICI biomarker; MSI-H supersedes TMB-H per Sha 2020
- clinical-databases/somatic-signatures - Clonal neoantigen burden (McGranahan 2016 Science) predicts ICI response better than total TMB
- workflows/somatic-variant-pipeline - Upstream somatic calling
<!-- END FILE: workflows/neoantigen-pipeline/SKILL.md -->

## 子目录：workflows/outbreak-pipeline

<!-- BEGIN FILE: workflows/outbreak-pipeline/SKILL.md -->
---
name: bio-workflows-outbreak-pipeline
description: Orchestrates genomic-epidemiology outbreak investigation from pathogen isolates to transmission networks, forking bacterial (snippy -> Gubbins recombination-masking -> IQ-TREE -> TreeTime -> TransPhylo) vs viral (Nextstrain/augur), with parallel MLST typing (cgMLST delegated to epidemiological-genomics/pathogen-typing) and AMR surveillance. Use when committing ONE reference genome for SNP calling (every isolate and distance inherits its coordinates), applying MANDATORY Gubbins recombination-masking on core.full.aln before the tree for recombining bacteria (skipping it inflates the clock 2-5x), gating time-scaling on a temporal-signal test (TempEst R2 >= 0.3), using a pathogen- AND population-specific cluster threshold rather than a universal SNP cutoff, or pinning pangolin-data/Nextclade/Freyja versions for the viral route. Hands mechanism to the epidemiological-genomics component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: mlst
workflow: true
depends_on:
  - epidemiological-genomics/pathogen-typing
  - epidemiological-genomics/amr-surveillance
  - epidemiological-genomics/phylodynamics
  - epidemiological-genomics/transmission-inference
  - epidemiological-genomics/variant-surveillance
qc_checkpoints:
  - after_typing: "Valid ST assigned (7-locus mlst); cgMLST via chewBBACA is deferred to epidemiological-genomics/pathogen-typing"
  - after_amr: "AMR genes identified; AMRFinderPlus applies its curated per-gene thresholds (it does not use a flat 90% identity cutoff)"
  - after_phylodynamics: "Root-to-tip R2 >=0.3, clock rate plausible"
  - after_transmission: "Transmission pairs consistent with epi data"
---

## Version Compatibility

Reference examples tested with: ncbi-amrfinderplus 4.0+, hamronization 1.1+, tb-profiler 6.2+, mlst 2.23+, chewBBACA 3.3+, pangolin 4.3+ (pangolin-data 1.30+), nextclade 3.8+, snippy 4.6+, gubbins 3.3+, clonalframeml 1.13+, IQ-TREE 2.3.6+, TreeTime 0.11+, BEAST 2.7.6+ (BDSKY 1.5+, MASCOT 3.0+, BICEPS), TransPhylo 1.4+ (R), outbreaker2 1.2+ (R), bactdating 1.1+ (R), freyja 1.4+, mob_suite 3.1+, BioPython 1.84+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>`; CLI: `<tool> --version` then `--help`
- R: `packageVersion('<pkg>')` then `?function_name`
- Pangolin: `pangolin --all-versions` (records pangolin + pangolin-data + scorpio + constellations)
- Nextclade: `nextclade dataset list --tag latest sars-cov-2`
- TB-Profiler: `tb-profiler list_db` (verify WHO catalogue edition)

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Outbreak Pipeline

**"Characterize a pathogen outbreak from my isolate sequences"** -> Orchestrate MLST typing, SNP phylogeny, TreeTime time-scaled tree construction, TransPhylo transmission inference, AMR profiling, and variant surveillance for genomic epidemiology.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

A transmission tree is the MAP estimate among many equally probable trees, and its trustworthiness is decided at four seams.

1. **One reference genome for SNP calling, committed before any isolate.** snippy calls SNPs against ONE reference; every isolate, the core alignment, and the cluster distances inherit its coordinates. A build/coordinate mismatch (isolates called against different references, or an AMR panel keyed to a different build) fabricates or hides SNPs. Commit the reference (GenBank format for snippy) up front.
2. **Recombination-masking is MANDATORY for recombining bacteria, on core.full.aln, before the tree.** Gubbins masking is not optional for S. pneumoniae, N. gonorrhoeae, E. coli, Klebsiella, Campylobacter, H. pylori — skipping it inflates the clock rate 2-5x and biases R_e. Input MUST be `core.full.aln` (full positions incl. invariant), NOT `core.aln` (variable-only). Skip masking ONLY for documented-clonal Mtb.
3. **Time-scaling requires a passing temporal-signal test, committed before trusting any dated tree.** TempEst root-to-tip regression (Rambaut 2016) with R2 >= 0.3 as a field convention (the paper sets no threshold and cautions R2 is not a valid significance test); the date-randomisation test is a secondary check (can pass with narrow sampling windows), NOT a substitute. The outbreak-scale clock is lineage/host-specific, not a universal constant.
4. **The cluster threshold is pathogen- AND population-specific — never a universal cutoff.** From the literature per pathogen (Mtb <=12/<=5 SNP; S. aureus <=15; K. pneumoniae KPC <=21; C. difficile <=2 masked; Salmonella <=5 cgMLST alleles). Walker's 5-SNP Mtb threshold was calibrated in low-transmission UK and inflates apparent recent transmission 2-5x in high-burden settings. A genomic distance is not an epidemiological distance without a time-scaled prior.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Reference genome + build (bacterial) | Every isolate's SNPs, the core alignment, cluster distances; a mismatch fabricates/hides SNPs |
| Recombination-masking scheme (Gubbins on core.full.aln) | The clock rate and R_e; skipping inflates the clock 2-5x for recombining taxa |
| Clock + temporal-signal (TempEst R2 >= 0.3) | Whether the dated tree is supported at all |
| Cluster threshold (pathogen + population-specific) | Who is "linked"; a universal SNP cutoff over-clusters in high-burden settings |
| Viral tool versions (pangolin-data/Nextclade/Freyja) | The lineage call; same genome, different call across versions — pin them |

## Workflow Overview

```
Pathogen Isolate Genomes (FASTA/FASTQ) + collection dates + (optional) contact data
        |
        v
   +---------+---------+
   |                   |
   v                   v
[1a. MLST + serotyping    [1b. AMR + species mode:
     + Pangolin/UShER          AMRFinderPlus --organism,
     for SARS-CoV-2;           TB-Profiler for Mtb,
     cgMLST ->                 hAMRonization across tools]
     pathogen-typing]
   |                   |
   +--------+----------+
            |
            v
[2. snippy + snippy-core (bacteria) -> Gubbins on core.full.aln to mask recombination
    (mandatory for bacteria; skip only for clonal Mtb)]
            |
            v
[3. IQ-TREE on recombination-masked alignment + TempEst R^2 >= 0.3 + date-randomisation;
    TreeTime --coalescent skyline --clock-filter 4 OR BactDating;
    BEAST2 BDSKY (origin > rootHeight, multi-chain) for posterior R_e]
            |
            v
[4. Transmission inference: outbreaker2 (dense + contact data) OR TransPhylo (sparse,
    from dated tree) OR transcluster (pair-level probability); pathogen-specific SNP
    threshold for cluster definition -- NEVER a universal cutoff]
            |
            v
Transmission tree posterior + R_e(t) + lineage / clone context + AMR phenotype
```

## Prerequisites

```bash
conda install -c bioconda mlst chewbbaca ncbi-amrfinderplus hamronization tb-profiler \
    snippy snp-dists gubbins clonalframeml iqtree treetime pangolin nextclade freyja \
    mob_suite plasmidfinder sistr_cmd seqsero2 kleborate kaptive seroba

conda install -c bioconda beast2
packagemanager -add BDSKY BEASTLabs feast ORC MASCOT BICEPS

Rscript -e "install.packages(c('TransPhylo', 'outbreaker2', 'BactDating', 'bdskytools', 'coda', 'ape'))"

amrfinder -u
tb-profiler update_tbdb
```

## Primary Path: Bacterial Outbreak Investigation

### Step 1a: MLST Typing (Parallel)

**Goal:** Assign 7-locus PubMLST sequence types to all isolates for clonal-context interpretation.

**Approach:** Run Seemann's `mlst` per assembly; auto-detect scheme; concatenate the per-isolate output into a cohort TSV.

```bash
#!/bin/bash
ISOLATES="isolate1.fasta isolate2.fasta isolate3.fasta"
OUTDIR="outbreak_results"
mkdir -p ${OUTDIR}/{mlst,amr,alignment,phylo,transmission}

# Run MLST on all isolates
echo "=== MLST Typing ==="
for fasta in $ISOLATES; do
    sample=$(basename $fasta .fasta)
    mlst $fasta > ${OUTDIR}/mlst/${sample}.mlst.txt
done

# Combine results
cat ${OUTDIR}/mlst/*.mlst.txt > ${OUTDIR}/mlst/all_mlst.tsv
echo "MLST complete: ${OUTDIR}/mlst/all_mlst.tsv"
```

### Step 1b: AMR Detection (Parallel) -- AMRFinderPlus with species mode

**Goal:** Produce per-isolate AMR calls with species-specific point-mutation panel activated, then harmonise across the cohort to the PHA4GE schema for cross-lab comparison.

**Approach:** AMRFinderPlus `-n` for nucleotide assembly with `--organism` and `--plus`; pipe each per-isolate TSV through `hamronize amrfinderplus` with mandatory PHA4GE metadata; `hamronize summarize` merges to a cohort table. For *M. tuberculosis*, switch to TB-Profiler -- AMRFinderPlus has no Mtb organism mode.

```bash
echo "=== AMR Detection ==="
SPECIES="Klebsiella_pneumoniae"
for fasta in $ISOLATES; do
    sample=$(basename $fasta .fasta)
    amrfinder -n $fasta --organism $SPECIES --plus --threads 8 \
        -o ${OUTDIR}/amr/${sample}.amrfinder.tsv

    hamronize amrfinderplus \
        --analysis_software_version $(amrfinder -V | awk '/Software/{print $NF}') \
        --reference_database_version $(amrfinder -V | awk '/Database/{print $NF}') \
        --input_file_name ${sample} \
        ${OUTDIR}/amr/${sample}.amrfinder.tsv > ${OUTDIR}/amr/${sample}.hamr.tsv
done

hamronize summarize -t tsv -o ${OUTDIR}/amr/cohort.hamr.tsv ${OUTDIR}/amr/*.hamr.tsv
echo "AMR summary: ${OUTDIR}/amr/cohort.hamr.tsv"
```

For *M. tuberculosis*, route to TB-Profiler instead -- AMRFinderPlus has no Mtb organism mode. For colistin / mcr surveillance and any plasmid-mobility claim, follow with MOB-suite (`mob_recon` + `mob_typer`) to determine plasmid context. See epidemiological-genomics/amr-surveillance for the full decision tree.

### Step 2: Core Genome Alignment + Recombination Masking (Bacteria)

**Goal:** Build a recombination-aware core-genome alignment that is safe for downstream clock inference.

**Approach:** Snippy per isolate against the reference; snippy-core to merge into the core alignment; Gubbins on `core.full.aln` (NOT `core.aln`) to mask recombinant tracts. Skipping recombination masking inflates the clock rate 2-5x for recombining bacteria (S. pneumoniae, N. gonorrhoeae, E. coli, Klebsiella, Campylobacter, H. pylori); the date-randomisation test is NOT a sufficient guard.

```bash
echo "=== Core Genome Alignment ==="
REFERENCE="reference.gbk"  # Reference genome in GenBank format

# Run snippy for each isolate
for fasta in $ISOLATES; do
    sample=$(basename $fasta .fasta)
    snippy --outdir ${OUTDIR}/alignment/snippy_${sample} \
           --ref $REFERENCE \
           --ctgs $fasta \
           --cpus 8
done

# Core SNP alignment
snippy-core --ref $REFERENCE --prefix core ${OUTDIR}/alignment/snippy_*

# Mandatory for recombining bacteria (S. pneumoniae, N. gonorrhoeae, E. coli, Klebsiella,
# Campylobacter, H. pylori). Skip ONLY for clonal Mtb cross-lineage analyses where
# recombination is documented to be rare; even then a recombination check is defensible.
# Input MUST be core.full.aln (full positions including invariant); core.aln (variable-only)
# gives wrong recombination calls because Gubbins cannot estimate background SNP density.
run_gubbins.py --prefix gubbins core.full.aln

mv core.* gubbins.* ${OUTDIR}/alignment/
echo "Recombination-masked alignment: ${OUTDIR}/alignment/gubbins.filtered_polymorphic_sites.fasta"
```

### Step 3: Phylodynamics with TreeTime

**Goal:** Time-scale the recombination-masked phylogeny with a global clock-rate estimate, gated by temporal-signal QC.

**Approach:** IQ-TREE on the recombination-masked alignment with `+ASC` ascertainment correction; TreeTime with coalescent skyline prior and `--clock-filter 4`; inspect `root_to_tip_regression.pdf` BEFORE trusting downstream output (R^2 >= 0.3 minimum as a field convention; TempEst sets no threshold).

```python
import subprocess
from Bio import Phylo, AlignIO
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

outdir = Path('outbreak_results')

# Build ML tree on the recombination-masked alignment with ascertainment-bias correction
# +ASC is required because the input contains variable positions only post-Gubbins
subprocess.run([
    'iqtree2', '-s', str(outdir / 'alignment/gubbins.filtered_polymorphic_sites.fasta'),
    '-m', 'GTR+G+ASC', '-B', '1000', '-bnni', '-T', 'AUTO',
    '--prefix', str(outdir / 'phylo/outbreak')
], check=True)

# Prepare metadata with dates
# Format: name\tdate (YYYY-MM-DD or decimal year)
metadata = pd.DataFrame({
    'name': ['isolate1', 'isolate2', 'isolate3', 'isolate4', 'isolate5'],
    'date': ['2024-01-15', '2024-01-22', '2024-02-01', '2024-02-10', '2024-02-15']
})
metadata.to_csv(outdir / 'phylo/metadata.tsv', sep='\t', index=False)

# Run TreeTime
subprocess.run([
    'treetime',
    '--tree', str(outdir / 'phylo/outbreak.treefile'),
    '--aln', str(outdir / 'alignment/gubbins.filtered_polymorphic_sites.fasta'),
    '--dates', str(outdir / 'phylo/metadata.tsv'),
    '--outdir', str(outdir / 'phylo/treetime_output'),
    '--coalescent', 'skyline',
    '--clock-filter', '4',  # SD multiplier for TreeTime's clock filter
    '--confidence',
    '--reroot', 'best'
], check=True)

# Temporal-signal QC: inspect root_to_tip_regression.pdf BEFORE trusting any downstream output.
# R^2 >= 0.3 minimum (field convention, NOT from Rambaut 2016 -- TempEst sets no threshold and
# states R^2 is an informal dispersion measure, not a significance test). If R^2 < 0.3, time-scaling is not
# supported -- report uncertainty and consider extending the sampling window. The
# date-randomisation test is a secondary check; it can pass with narrow sampling windows
# (false negative).
print('TreeTime output:', outdir / 'phylo/treetime_output')
```

### Step 4: Transmission Inference with TransPhylo

**Goal:** Reconstruct the posterior who-infected-whom transmission tree and R_e from the dated phylogeny.

**Approach:** Convert the TreeTime dated tree to TransPhylo `ptree`; supply pathogen-tuned generation-time and sampling-time Gamma priors; run MCMC at >=1e5 iterations (10k is smoke-test only); summarise via medoid transmission tree and per-pair WIWS probability. For dense outbreaks with contact-tracing data, outbreaker2 with `ctd` is preferred over TransPhylo (genomic-only).

```r
library(TransPhylo)
library(ape)

# Load dated tree from TreeTime
tree <- read.nexus("outbreak_results/phylo/treetime_output/timetree.nexus")

# Set parameters
# dateT: date when sampling stopped
# w.shape, w.scale: generation time distribution (Gamma)
# For many bacteria: mean ~14 days, shape=2, scale=7
dateT <- 2024.2  # Decimal year when sampling ended (end of observation)
w_shape <- 2     # Generation time shape (Gamma)
w_scale <- 7/365 # Gamma SCALE = 7 days; mean generation time = shape*scale = 2*7 = ~14 days

# TransPhylo operates on a `ptree` (dated phylogeny + last-sample date), NOT a raw ape phylo;
# convert first or inferTTree errors on a NULL ptree$ptree/$nam.
ptree <- ptreeFromPhylo(tree, dateLastSample = dateT)

# Run TransPhylo with enough iterations for posterior convergence; 10k is a smoke-test only.
# For publication, run >=1e5 (small outbreaks) to >=1e6+ iterations and inspect trace plots.
res <- inferTTree(ptree, dateT = dateT,
                   w.shape = w_shape, w.scale = w_scale,
                   mcmcIterations = 1e5,
                   startNeg = 1, startPi = 0.5)

# medTTree returns a coloured transmission tree (ctree); plot it with plotCTree
med_ctree <- medTTree(res)

# Plot transmission tree
pdf("outbreak_results/transmission/transmission_tree.pdf", width=10, height=8)
plotCTree(med_ctree)
dev.off()

# Who infected whom matrix (same 0.5 burn-in as the R_e estimate below, so both discard pre-convergence)
wiw <- computeMatWIW(res, burnin = 0.5)
write.csv(wiw, "outbreak_results/transmission/who_infected_whom.csv")

# R_e estimate (effective reproduction number under current immunity / interventions).
# This is NOT R_0 (basic reproduction number in a fully susceptible population);
# the phylodynamics literature is explicit about this distinction.
# getOffspringDist(record, burnin, k) gives the per-case offspring distribution; average
# across sampled hosts for a cohort R_e (or use BEAST2 BDSKY for a posterior Re(t)).
# Host names come from the ptree (res has no $ttree$nam field).
offspring <- sapply(ptree$nam, function(k) mean(getOffspringDist(res, k = k, burnin = 0.5)))
# The interval is the 2.5-97.5% spread of per-host mean offspring (across-host dispersion), NOT a
# posterior credible interval (per-host posteriors were collapsed by mean() first).
cat("R_e estimate:", mean(offspring), "(across-host 2.5-97.5%:", quantile(offspring, 0.025), "-", quantile(offspring, 0.975), ")\n")
```

### Python Alternative: TransPhylo via rpy2

**Goal:** Drive the same TransPhylo workflow from Python pipelines that prefer not to fork into R.

**Approach:** rpy2 bridges into the TransPhylo R package with named-argument passing; same priors and MCMC iteration discipline apply.

```python
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import pandas as pd
from pathlib import Path

pandas2ri.activate()

transphylo = importr('TransPhylo')
ape = importr('ape')

outdir = Path('outbreak_results')

tree = ape.read_nexus(str(outdir / 'phylo/treetime_output/timetree.nexus'))

date_t = 2024.2
w_shape = 2
w_scale = 7/365

# Convert to a TransPhylo ptree before inference (inferTTree needs ptree, not a raw phylo).
ptree = transphylo.ptreeFromPhylo(tree, dateLastSample=date_t)
res = transphylo.inferTTree(ptree, dateT=date_t, w_shape=w_shape, w_scale=w_scale,
                             mcmcIterations=10000, startNeg=1, startPi=0.5)

# medTTree returns a ctree; hand it to R's global env and plot with plotCTree.
med_ctree = transphylo.medTTree(res)
ro.globalenv['med_ctree'] = med_ctree
ro.r(f'''
pdf("{outdir}/transmission/transmission_tree.pdf", width=10, height=8)
plotCTree(med_ctree)
dev.off()
''')

print(f'Transmission tree saved to {outdir}/transmission/')
```

## Visualization: Outbreak Timeline

**Goal:** Plot isolates over time coloured by sequence type to communicate cluster expansion and clonal context.

**Approach:** Merge collection-date metadata with MLST output; plot per-isolate timestamps as a strip chart with per-ST colour.

```python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

metadata = pd.read_csv('outbreak_results/phylo/metadata.tsv', sep='\t')
metadata['date'] = pd.to_datetime(metadata['date'])

mlst = pd.read_csv('outbreak_results/mlst/all_mlst.tsv', sep='\t', header=None,
                    names=['file', 'scheme', 'ST'] + [f'locus{i}' for i in range(7)])
mlst['sample'] = mlst['file'].apply(lambda x: x.split('/')[-1].replace('.fasta', ''))

# Merge data
combined = metadata.merge(mlst[['sample', 'ST']], left_on='name', right_on='sample')

fig, ax = plt.subplots(figsize=(12, 6))

colors = {'ST11': 'red', 'ST258': 'blue', 'ST307': 'green'}
for st in combined['ST'].unique():
    subset = combined[combined['ST'] == st]
    ax.scatter(subset['date'], [1]*len(subset), label=f'ST{st}',
               s=100, c=colors.get(f'ST{st}', 'gray'), alpha=0.7)

ax.set_xlabel('Date')
ax.set_ylabel('')
ax.set_title('Outbreak Timeline by Sequence Type')
ax.legend()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('outbreak_results/outbreak_timeline.pdf')
```

## Parameter Recommendations

| Step | Parameter | Value | Rationale |
|------|-----------|-------|-----------|
| snippy | --mincov | 10 | Minimum coverage for variant call |
| Gubbins | input | core.full.aln | Full positions required to estimate background SNP density; core.aln is wrong |
| IQ-TREE | -m | GTR+G+ASC | +ASC ascertainment correction for SNP-only post-Gubbins input |
| TreeTime | --clock-filter | 4 | SD multiplier on root-to-tip residual; TreeTime convention |
| TreeTime | R^2 minimum | 0.3 | Below this, temporal signal treated as insufficient (field convention; TempEst itself sets no cutoff) |
| TransPhylo | w.shape, w.scale | 2, 7/365 | Gamma scale 7 days x shape 2 = ~14-day mean generation time; cite the pathogen-specific literature |
| TransPhylo | mcmcIterations | 1e5-1e6+ | 10k is a smoke-test only; inspect trace and ESS before reporting |
| BEAST2 BDSKY | origin | > rootHeight | Initialise to ~(tMRCA + 0.1*tMRCA); origin == rootHeight biases R_e upward (Stadler 2013) |
| BEAST2 chains | independent runs | >=3-4 | Single-chain ESS >=200 is necessary but not sufficient; combine after marginal overlap |
| Pangolin | --analysis-mode | usher | pangoLEARN deprecated mid-2023; UShER default since v4 (de Bernardi Schneider 2024, Virus Evol 10:vead085) |

## Pathogen-Specific SNP / cgMLST Cluster Thresholds

Cluster definition is pathogen- AND population-specific. NEVER apply a universal cutoff. See epidemiological-genomics/transmission-inference for full table with citations.

| Pathogen | Cluster threshold | Source |
|----------|-------------------|--------|
| *M. tuberculosis* (core SNP) | <=12 SNPs (likely transmission); <=5 (recent) | Walker 2013 *Lancet Infect Dis* 13:137 (UK low-transmission setting -- inflates 2-5x in high-burden) |
| *S. aureus* (core SNP) | <=15 SNPs (within hospital) | Coll 2020 *Lancet Microbe* 1:e328 |
| *K. pneumoniae* (KPC outbreak) | <=21 SNPs | Field convention; no threshold source |
| *C. difficile* (recombination-masked core SNP) | <=2 SNPs (likely direct) | Eyre 2013 *NEJM* 369:1195 |
| *Salmonella* (cgMLST, EnteroBase) | <=5 alleles | EnteroBase / EFSA convention |
| *Listeria* (PulseNet cgMLST) | <=4 alleles | PulseNet protocol |
| SARS-CoV-2 | NOT defined by SNP alone | 0-2 SNPs + epi link + sampling window |
| HIV-1 subtype B | 1.5% TN93 distance | HIV-TRACE US-CDC default (re-tune for non-B subtypes) |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Fabricated or hidden SNPs / wrong distances | Build/coordinate mismatch (isolates called against different references, or AMR panel on another build) | One committed reference for every isolate + the AMR panel; verify contig/seqid consistency |
| Clock inflated 2-5x, false transmission links | Recombination masking skipped | Gubbins on core.full.aln BEFORE the tree; the date-randomisation test is NOT a sufficient guard |
| Over-clustered outbreak in a high-burden setting | Universal SNP cutoff | Pathogen- AND population-specific threshold from the literature; a genomic distance is not an epidemiological distance |
| "Who infected whom" overclaimed | Transmission read from single-isolate SNP distances | "Transmission consistent with genomics"; single-isolate-per-host trees are under-identified (MAP among many) |
| Same genome, different lineage across labs/dates (viral) | pangolin-data/Nextclade/Freyja version churn | Pin the versions in metadata; re-run all samples against ONE version before comparing |
| Poor temporal signal | Insufficient sampling / recombination | Mask recombination (Gubbins); check dates; do not time-scale below TempEst R2 0.3 |
| Missing AMR genes | Database mismatch | Try multiple databases (ncbi/card/resfinder); report allele identity, not just family |

## Output Files

| File | Description |
|------|-------------|
| `mlst/all_mlst.tsv` | Sequence types for all isolates |
| `amr/cohort.hamr.tsv` | AMR gene presence/absence matrix |
| `alignment/core.aln` | Core genome SNP alignment |
| `phylo/outbreak.treefile` | ML phylogenetic tree |
| `phylo/treetime_output/` | Dated tree and molecular clock |
| `transmission/transmission_tree.pdf` | Inferred transmission network |
| `transmission/who_infected_whom.csv` | Transmission probability matrix |

## Related Skills

- database-access/sra-data - Download outbreak FASTQ from SRA / ENA
- database-access/ncbi-datasets-cli - Bulk-pull pathogen reference genomes (e.g. `datasets download virus`)
- epidemiological-genomics/pathogen-typing - MLST and cgMLST details
- epidemiological-genomics/amr-surveillance - AMRFinderPlus, ResFinder
- epidemiological-genomics/phylodynamics - TreeTime, BEAST2 parameters
- epidemiological-genomics/transmission-inference - TransPhylo configuration
- epidemiological-genomics/variant-surveillance - Nextclade for viral outbreaks
- phylogenetics/modern-tree-inference - IQ-TREE2 model selection

## References

- Croucher NJ, Page AJ, Connor TR, et al (2015) Rapid phylogenetic analysis of large samples of recombinant bacterial whole genome sequences using Gubbins. *Nucleic Acids Research* 43:e15. DOI 10.1093/nar/gku1196. (recombination masking.)
- Didelot X, Fraser C, Gardy J, Colijn C (2017) Genomic infectious disease epidemiology in partially sampled and ongoing outbreaks (TransPhylo). *Molecular Biology and Evolution* 34:997-1007. DOI 10.1093/molbev/msw275. (transmission inference.)
- Walker TM, Ip CLC, Harrell RH, et al (2013) Whole-genome sequencing to delineate Mycobacterium tuberculosis outbreaks: a retrospective observational study. *Lancet Infectious Diseases* 13:137-146. DOI 10.1016/S1473-3099(12)70277-3. (5-SNP threshold, low-transmission calibration.)
- Sagulenko P, Puller V, Neher RA (2018) TreeTime: maximum-likelihood phylodynamic analysis. *Virus Evolution* 4:vex042. DOI 10.1093/ve/vex042.
<!-- END FILE: workflows/outbreak-pipeline/SKILL.md -->

## 子目录：workflows/proteomics-pipeline

<!-- BEGIN FILE: workflows/proteomics-pipeline/SKILL.md -->
---
name: bio-workflows-proteomics-pipeline
description: Orchestrates bottom-up proteomics from a search engine's output (MaxQuant/FragPipe/DIA-NN) to differential protein abundance with limma/DEqMS/MSstats. Use when committing the search database + acquisition mode (DDA vs DIA) up front, re-controlling FDR at PSM AND peptide AND protein-group level (not just PSM), removing contaminant/reverse rows and inspecting RAW distributions before normalizing, bridging cross-plex TMT with an IRS reference channel, modeling MNAR missingness rather than downshift-imputing on/off proteins, batching as a covariate (not pre-subtracted), and testing with treat()/DEqMS. Hands mechanism to the proteomics component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: limma
workflow: true
depends_on:
  - proteomics/data-import
  - proteomics/proteomics-qc
  - proteomics/quantification
  - proteomics/protein-inference
  - proteomics/differential-abundance
  - proteomics/dia-analysis
---

## Version Compatibility

Reference examples tested with: MSnbase 2.28+, limma 3.58+, DEqMS 1.20+, proDA 1.20+, MSstatsTMT 2.10+, arrow 15.0+ (DIA-NN report.parquet), ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Proteomics Pipeline

**"Process my proteomics data from raw MS files to differential abundance"** -> Orchestrate data import (pyopenms/MaxQuant), QC assessment, protein quantification, normalization, differential abundance testing (limma/DEqMS, or MSstats for feature-level designs), and PTM analysis.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

Bottom-up proteomics never measures proteins; it measures peptides and INFERS proteins, and the trustworthiness decisions are made at seams before the statistics.

1. **The search database + acquisition mode are committed once and inherited by everything.** The FASTA fixes the target-decoy frame (concatenated one-search FDR = #decoy/#target; a separate-search design needs mix-max instead — mixing the two mis-estimates FDR), what counts as a "unique peptide" (relative to the DB: canonical vs +isoforms), and the contaminants (cRAP must be IN the search DB from the start; a contaminant can BE the protein of interest, so never blind-delete `CON__` rows). DDA vs DIA is set at the instrument and dictates which imputation is even legitimate.
2. **FDR is re-controlled at THREE levels, not just PSM — and match-between-runs has its OWN FDR.** 1% PSM-FDR does NOT give 1% protein-FDR — each level (PSM, peptide, protein-group) needs its own target-decoy estimation; PSM-only filtering yields 10-30% real protein-FDR on deep data (one false PSM nucleates a false one-hit-wonder, and false proteins grow with dataset size). Use picked-protein/picked-group FDR. The two-peptide rule INCREASES protein-FDR, it does not reduce it. MBR transfers IDs across runs by RT/m-z and can be wrong for low-abundance precursors — do NOT report MBR-filled counts as directly measured; DIA-NN controls MBR-FDR via `Lib.*` q-values, IonQuant via an explicit MBR-FDR mixture model.
3. **Missingness is MODELED, not filled.** DDA missingness is structured left-censored MNAR; downshift imputation (mean=mu-1.8sigma) on an on/off protein inflates the t-numerator AND deflates the denominator (the volcano "wing" artifact). The honest report for a protein missing in one whole group is "undetected in group B", not a fold change — model the MNAR (proDA/msqrob2/MSstats-AFT).
4. **Normalize AFTER contaminant removal and AFTER inspecting raw distributions; batch is a covariate, not pre-subtracted.** Median-normalizing first mathematically erases a 3x-low load. Cross-plex TMT is invalid without an IRS bridge. `removeBatchEffect` before testing understates residual variance (anticonservative p) — put batch in the same model.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Search FASTA + target-decoy strategy | The FDR estimator, what a "unique peptide" is, which contaminants exist; a mismatch mis-estimates FDR silently |
| Enzyme + fixed/variable mods (Carbamidomethyl-Cys fixed) | Which peptides exist to quantify; a fixed-mod misconfig loses all Cys peptides |
| DDA vs DIA acquisition mode | Missingness structure (MNAR vs ~MCAR), whether TMT is possible, which imputation is legitimate |
| FDR framing (PSM + peptide + protein-group, 1% each) | Real protein-FDR; PSM-only is 10-30% wrong on deep data |

## Pipeline Overview

```
Raw MS Data (mzML) --> MaxQuant/DIA-NN --> proteinGroups.txt
                                                 |
                                                 v
            +--------------------------------------------+
            |             proteomics-pipeline            |
            +--------------------------------------------+
            |  1. Data Import & Filtering                |
            |  2. Log2 + inspect RAW distributions       |
            |  3. Normalization (after the inspection)   |
            |  4. Per-Group Completeness Filter          |
            |  5. QC: PCA, Correlation                   |
            |  6. Differential Abundance (limma/MSstats) |
            |  7. Visualization & Export                 |
            +--------------------------------------------+
                                                 |
                                                 v
                  Differential Proteins + Volcano Plots
```

## Complete R Workflow

**Goal:** Turn a MaxQuant or DIA-NN protein matrix into a table of differentially abundant proteins with honest missing-value handling.

**Approach:** Strip bookkeeping rows, log2 and inspect the RAW per-sample distributions (dropping failed loads before normalization can hide them), median-center, filter on per-group completeness, then model the dropout with proDA (or fall back to imputation), and test with moderated limma using treat() for a minimum fold change.

```r
library(limma)
library(ggplot2)
library(pheatmap)

# === 1. DATA IMPORT ===
proteins <- read.delim('proteinGroups.txt', stringsAsFactors = FALSE)
cat('Loaded', nrow(proteins), 'protein groups\n')

# Filter contaminants, reverse, only-by-site
proteins <- proteins[proteins$Potential.contaminant != '+' &
                      proteins$Reverse != '+' &
                      proteins$Only.identified.by.site != '+', ]
cat('After filtering:', nrow(proteins), 'proteins\n')

# Extract LFQ intensities
lfq_cols <- grep('^LFQ\\.intensity\\.', colnames(proteins), value = TRUE)
intensities <- proteins[, lfq_cols]
rownames(intensities) <- proteins$Majority.protein.IDs
colnames(intensities) <- gsub('LFQ\\.intensity\\.', '', colnames(intensities))

# === 2. LOG2 TRANSFORM, THEN INSPECT RAW DISTRIBUTIONS ===
intensities[intensities == 0] <- NA
log2_int <- log2(intensities)

# Inspect BEFORE normalizing (rule 4). Median-centering rescales every sample onto a common median,
# so it mathematically erases the 3x-low load that marks a failed injection -- after this point the
# failure is invisible. Identify and drop failures HERE.
boxplot(log2_int, las = 2, main = 'RAW log2 LFQ (pre-normalization)', ylab = 'log2 intensity')
id_counts <- colSums(!is.na(log2_int))
print(data.frame(id_count = id_counts, raw_median_log2 = round(apply(log2_int, 2, median, na.rm = TRUE), 2)))

# <50% of the cohort median ID count is a failed injection / low load, not biology.
failed <- names(id_counts)[id_counts < 0.5 * median(id_counts)]
if (length(failed) > 0) {
    message('Dropping failed samples: ', paste(failed, collapse = ', '))
    log2_int <- log2_int[, !colnames(log2_int) %in% failed, drop = FALSE]
}

# === 3. NORMALIZE (only after the raw inspection above) ===
sample_medians <- apply(log2_int, 2, median, na.rm = TRUE)
global_median <- median(sample_medians)
normalized <- sweep(log2_int, 2, sample_medians - global_median)

# === 4. FILTER ON PER-GROUP COMPLETENESS (do NOT impute by default) ===
# Filter FIRST on completeness PER GROUP: keep a protein if it is valid in >= ~50-70%
# of replicates in AT LEAST ONE condition. A protein missing in every group fails QC.
sample_info <- read.csv('sample_annotation.csv')
# Re-align the annotation to the samples that SURVIVED the raw-distribution QC above; otherwise the
# column indexing below requests a dropped sample and errors (or silently misaligns the design).
sample_info <- sample_info[sample_info$sample %in% colnames(normalized), ]
sample_info$condition <- droplevels(factor(sample_info$condition))
min_frac <- 0.6   # >= 60% present within at least one group; tune 0.5-0.7 per design
group_complete <- sapply(levels(sample_info$condition), function(g) {
    cols <- sample_info$sample[sample_info$condition == g]
    rowSums(!is.na(normalized[, cols, drop = FALSE])) >= ceiling(length(cols) * min_frac)
})
valid_rows <- rowSums(group_complete) > 0
filtered <- normalized[valid_rows, ]
cat('Proteins after per-group completeness filter:', nrow(filtered), '\n')

# Missingness in label-free DDA is left-censored MNAR (missing BECAUSE low). The modern,
# correct approach is to MODEL the missingness in the likelihood, NOT impute it. See
# proteomics/differential-abundance for the decision (proDA / msqrob2 / MSstats-AFT). The
# proDA path below is the RECOMMENDED route; the impute-then-limma path is a fallback.

# --- RECOMMENDED: model the missingness with proDA (no imputation) ---
# library(proDA)
# fit <- proDA(as.matrix(filtered), design = ~ condition, col_data = sample_info,
#              reference_level = 'Control')
# da <- test_diff(fit, contrast = 'conditionTreatment')   # columns: diff (log2FC), pval, adj_pval
# (Skip the === 5-6 impute/limma blocks below when using proDA.)

# --- FALLBACK ONLY: left-censored downshift imputation, then limma ---
# WARNING: downshift MANUFACTURES systematic false positives for on/off proteins near the
# detection limit (the volcano "anchor arms"): it pins missing values ~1.8 SD below the mean
# with an artificially tight 0.3 SD spread, inflating the t-statistic. The honest report for
# a protein fully missing in one group is "undetected in group B", NOT a fold change.
impute_minprob <- function(x) {
    nas <- is.na(x)
    if (all(nas)) return(x)
    x[nas] <- rnorm(sum(nas), mean = mean(x, na.rm = TRUE) - 1.8 * sd(x, na.rm = TRUE),
                    sd = 0.3 * sd(x, na.rm = TRUE))
    x
}
imputed <- as.data.frame(t(apply(filtered, 1, impute_minprob)))

# === 5. QC ===
# PCA
pca <- prcomp(t(imputed), scale. = TRUE)
pca_df <- data.frame(PC1 = pca$x[, 1], PC2 = pca$x[, 2], Sample = rownames(pca$x))

# === 6. DIFFERENTIAL ANALYSIS (fallback impute-then-limma path) ===
# sample_info is already loaded and factored in step 4. Put any batch in the design
# (~ batch + condition); removeBatchEffect() is visualization-only, never an input to lmFit.
design <- model.matrix(~ 0 + condition, data = sample_info)
colnames(design) <- levels(sample_info$condition)

fit <- lmFit(as.matrix(imputed), design)
contrast <- makeContrasts(Treatment - Control, levels = design)
fit2 <- contrasts.fit(fit, contrast)

# Select on FDR ALONE. A post-hoc fold-change + significance double filter inflates FDR
# (a collider/selection effect; realized FDR can exceed 50%). To require a minimum effect,
# use the moderated minimum-fold-change test treat()/topTreat() instead of filtering after.
fit2_treat <- treat(fit2, lfc = log2(1.5), trend = TRUE, robust = TRUE)   # moderated min-FC test; trend+robust ~mandatory for label-free LFQ
results <- topTreat(fit2_treat, coef = 1, number = Inf)
results$protein <- rownames(results)
results$significant <- results$adj.P.Val < 0.05

# === 7. OUTPUT ===
cat('\nResults:\n')
cat('  Significant proteins:', sum(results$significant), '\n')
cat('  Up-regulated:', sum(results$significant & results$logFC > 0), '\n')
cat('  Down-regulated:', sum(results$significant & results$logFC < 0), '\n')

write.csv(results, 'proteomics_results.csv', row.names = FALSE)
```

## MSstats Workflow

```r
library(MSstats)

# From MaxQuant
evidence <- read.table('evidence.txt', sep = '\t', header = TRUE)
proteinGroups <- read.table('proteinGroups.txt', sep = '\t', header = TRUE)
annotation <- read.csv('annotation.csv')

# Convert to MSstats format
msstats_input <- MaxQtoMSstatsFormat(evidence = evidence,
                                      proteinGroups = proteinGroups,
                                      annotation = annotation)

# Process data
processed <- dataProcess(msstats_input, normalization = 'equalizeMedians',
                         summaryMethod = 'TMP', censoredInt = 'NA')

# Comparison. +1 on the numerator: Treatment=+1, Control=-1 so log2FC = Treatment - Control
# (positive = up in Treatment), matching the label and the limma makeContrasts(Treatment-Control) path.
comparison <- matrix(c(-1, 1), nrow = 1)
rownames(comparison) <- 'Treatment_vs_Control'
colnames(comparison) <- c('Control', 'Treatment')

results <- groupComparison(contrast.matrix = comparison, data = processed)
```

## QC Checkpoints

| Stage | Check | Action if Failed |
|-------|-------|------------------|
| Import | >1000 proteins | Re-run MaxQuant |
| Filter | <30% removed | Check sample prep |
| Missing | <40% per sample | Check MS performance |
| PCA | Replicates cluster | Check for batch effects |
| Stats | FC/FDR pre-specified | Verify thresholds were pre-specified; inspect the volcano for downshift-imputation 'anchor arms' |

## Workflow Variants

### TMT/iTRAQ Isobaric Labeling
Reporter extraction is a spectra-level step, not a text-matrix read. Within a single plex the channels are co-isolated/co-fragmented in the same MS2 event, so relative ratios are stable; but MULTI-batch TMT CANNOT be compared across plexes without an IRS bridge (a pooled reference channel in every plex; Plubell 2017). Route to proteomics/quantification for the mechanics.
```r
library(MSnbase)

# Extract reporter ions from spectra (NOT readMSnSet, which loads an existing text matrix)
raw <- readMSData('tmt.mzML', mode = 'onDisk')
tmt_data <- quantify(raw, reporters = TMT10, method = 'max')
# Correct isobaric impurity cross-talk with the LOT-SPECIFIC matrix from the reagent CoA.
# edit=FALSE avoids the interactive editor (default edit=TRUE blocks in scripts); load the CoA
# cross-talk values rather than the near-identity template makeImpuritiesMatrix(10) returns alone.
impurities <- makeImpuritiesMatrix(filename = 'tmt10_coa.csv', edit = FALSE)
tmt_data <- purityCorrect(tmt_data, impurities)

# Multi-batch TMT: do NOT concatenate plexes directly. Use MSstatsTMT, which applies the
# reference-channel (IRS) bridge during summarization:
#   library(MSstatsTMT)
#   summ <- proteinSummarization(msstatstmt_input)   # includes the cross-plex bridge
#   groupComparisonTMT(summ, contrast.matrix = comparison)
```

### SILAC Workflow
Caveat: heavy-Arg -> heavy-Pro metabolic conversion biases ratios for proline-containing peptides (under-counts the heavy channel), and labeling efficiency must be checked (residual light reads as down-regulation). Route to proteomics/quantification for the mechanics.
```r
# SILAC ratios from MaxQuant
silac <- read.delim('proteinGroups.txt')
ratio_cols <- grep('Ratio.H.L.normalized', colnames(silac), value = TRUE)

# Log2 transform ratios
silac_log2 <- log2(silac[, ratio_cols])

# One-sample t-test against 0 (no change)
results <- apply(silac_log2, 1, function(x) t.test(x, mu = 0)$p.value)
```

### DIA-NN Workflow
DIA-NN 1.9+ defaults to report.parquet (the only default in 2.0); read it with arrow, not read.delim. Filter on q-values BEFORE pivoting, or low-confidence rows enter the matrix. Route to proteomics/dia-analysis for the mechanics.
```r
library(arrow)
library(dplyr)
library(tidyr)

diann <- read_parquet('report.parquet')

# Filter to 1% FDR at precursor AND protein-group level before pivoting.
# Use the GLOBAL protein-group q-value for the cross-run matrix (per-run min(Q.Value) is anti-conservative).
# When MBR is ON, MBR has its own FDR: add the Lib.* q-values (Lib.Q.Value, Lib.PG.Q.Value <= 0.01).
diann_filt <- diann %>%
    filter(Q.Value <= 0.01 & PG.Q.Value <= 0.01 & Global.PG.Q.Value <= 0.01)

# PG.MaxLFQ is ALREADY cross-run MaxLFQ-normalized at report generation. Re-normalizing it
# double-normalizes -- go straight to log2 + limma with no further normalization. To apply the
# skill's own median-centering instead, pivot raw PG.Quantity here, not PG.MaxLFQ.
protein_matrix <- diann_filt %>%
    select(Protein.Group, Run, PG.MaxLFQ) %>%
    distinct() %>%
    pivot_wider(names_from = Run, values_from = PG.MaxLFQ)

# PG.MaxLFQ path: log2-transform and go straight to limma (no re-normalization)
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| ~1% PSM-FDR but 10-30% wrong proteins | FDR controlled only at PSM level | Estimate FDR at peptide AND protein-group level (picked-group FDR) |
| Volcano "wings" of huge-FC on/off proteins | Downshift imputation on MNAR (Perseus/MaxQuant) | Model the MNAR (proDA/msqrob2/MSstats-AFT); report "undetected in group B", not a fold change |
| Cross-plex TMT ratios differ 2-5x for no biology | Compared TMT across plexes without IRS | Pooled reference channel in EVERY plex + IRS bridge before comparison |
| A failed-load sample silently carried forward | Normalized before inspecting raw distributions | Filter contaminant/reverse rows -> inspect raw boxplots + ID counts -> remove failures -> THEN normalize |
| Anticonservative p-values | `removeBatchEffect` before testing | Put batch in the model (`~ batch + condition`); removeBatchEffect only for PCA |
| Every ratio subtly wrong | Wrong intensity column (`Intensity` vs `LFQ intensity` vs `iBAQ`) | Pick the right column; convert 0 -> NaN before log2 |
| Spurious DA that flips between conditions | Razor-peptide inference reassigns a shared peptide | Quantify at protein-group level or unique-peptides-only for sensitive comparisons |

## References

- Elias JE, Gygi SP (2007) Target-decoy search strategy for increased confidence in large-scale protein identifications by mass spectrometry. *Nature Methods* 4:207-214. DOI 10.1038/nmeth1019.
- Savitski MM, Wilhelm M, Hahne H, Kuster B, Bantscheff M (2015) A scalable approach for protein false discovery rate estimation in large proteomic data sets. *Molecular & Cellular Proteomics* 14:2394-2404. DOI 10.1074/mcp.M114.046995. (picked-protein FDR.)
- Plubell DL, Wilmarth PA, Zhao Y, et al (2017) Extended multiplexing of tandem mass tags (TMT) labeling reveals age and high-fat-diet specific proteome changes in mouse epididymal adipose tissue. *Molecular & Cellular Proteomics* 16:873-890. DOI 10.1074/mcp.M116.065524. (IRS.)
- Ritchie ME, Phipson B, Wu D, et al (2015) limma powers differential expression analyses for RNA-sequencing and microarray studies. *Nucleic Acids Research* 43:e47. DOI 10.1093/nar/gkv007.
- Zhu Y, Orre LM, Zhou Tran Y, et al (2020) DEqMS: a method for accurate variance estimation in differential protein expression analysis. *Molecular & Cellular Proteomics* 19:1047-1057. DOI 10.1074/mcp.TIR119.001646.

## Related Skills

- proteomics/data-import - Load MS data formats
- proteomics/proteomics-qc - Quality control before analysis
- proteomics/quantification - Normalization, TMT IRS bridge, SILAC mechanics
- proteomics/protein-inference - Razor/shared-peptide assignment to protein groups
- proteomics/differential-abundance - Modeling missingness, moderated testing details
- proteomics/dia-analysis - DIA-NN report parsing and q-value filtering
- proteomics/ptm-analysis - Phosphoproteomics and other PTMs
- data-visualization/volcano-and-ma-plots - Volcano plots with LFC shrinkage
<!-- END FILE: workflows/proteomics-pipeline/SKILL.md -->

## 子目录：workflows/riboseq-pipeline

<!-- BEGIN FILE: workflows/riboseq-pipeline/SKILL.md -->
---
name: bio-workflows-riboseq-pipeline
description: End-to-end Ribo-seq analysis from FASTQ through periodicity QC, P-site calibration, ORF detection, translation efficiency, and stalling. Use when orchestrating a full ribosome profiling pipeline and deciding harvest/dedup/alignment options and which downstream analyses the library can support.
tool_type: mixed
primary_tool: STAR
workflow: true
depends_on:
  - ribo-seq/riboseq-preprocessing
  - ribo-seq/ribosome-periodicity
  - ribo-seq/orf-detection
  - ribo-seq/translation-efficiency
  - ribo-seq/ribosome-stalling
  - ribo-seq/initiation-site-mapping
qc_checkpoints:
  - after_align: "EndToEnd footprint alignment; deduplicate ONLY with UMIs; transcriptome BAM emitted"
  - periodicity_gate: "Strong 3-nt frame-0 periodicity REQUIRED before any ORF/stalling analysis; else gene-level counts only"
  - after_psite: "Per-read-length P-site offsets calibrated (not a single hardcoded 28 / read 5' end)"
  - after_te: "TE via count-based GLM (riborex/Xtail/anota2seq), never a ratio of ratios"
---

## Version Compatibility

Reference examples tested with: cutadapt 4.4+, umi_tools 1.1+, STAR 2.7.11+, bowtie2 2.5.3+, plastid 0.6+, riboWaltz 2.0+, RiboCode 1.2+, riborex 2.4+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Ribo-seq Pipeline

**"Analyze my ribosome profiling data from FASTQ to translation efficiency"** -> Orchestrate UMI handling, trimming, rRNA depletion, footprint-aware alignment, periodicity QC, P-site calibration, ORF detection, and differential translation, gating each downstream analysis on library quality.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## The governing principle

A Ribo-seq analysis is decided at four seams, two of them set at the bench before any sequencing.

1. **The harvest method is the deepest commitment and it fixes which analyses are even valid.** Cycloheximide (CHX) pre-treatment freezes elongating ribosomes but distorts codon-level dwell times (it can flip the codon-occupancy/tRNA-abundance correlation, Hussmann 2015); dwell-time / stalling / pausing analyses are only valid on flash-frozen, no-drug libraries. Gene-level footprint counts and TE are robust to CHX; codon-resolution analyses are not.
2. **Deduplicate ONLY when a UMI is present.** Ribosome footprints are ~28-30 nt and massively over-represented at abundant transcripts, so identical reads are mostly real signal; position-deduplicating a non-UMI library destroys it. With UMIs, dedup BOTH the genome and the transcriptome BAM.
3. **3-nt periodicity is a HARD gate, not a QC nicety.** Frame-based ORF calling and P-site analyses require strong frame-0 periodicity; a library that lacks it supports only gene-level counts. Certify it (riboWaltz frame-0 fraction) BEFORE any ORF/stalling step.
4. **P-site offsets are per-read-length, and TE is a count model.** Never hardcode a single 28-nt offset or the read 5' end; calibrate per length. Differential translation efficiency is a count-based GLM (riborex/Xtail/anota2seq) on CDS counts from BOTH assays, never a ratio of ribo/RNA ratios.

## Pipeline overview

```
FASTQ -> UMI extract -> trim -> rRNA remove -> STAR (EndToEnd) -> dedup (UMI only)
      -> periodicity QC (HARD GATE) + per-length P-site offsets -> [ORF detection | translation efficiency | stalling]
```

## Step 1: Preprocess

**Goal:** Produce a clean, footprint-aware alignment.

**Approach:** Extract UMIs first (if present), trim with a permissive floor, deplete rRNA before alignment, align end-to-end, and deduplicate only with UMIs. See riboseq-preprocessing for the decision tables.

```bash
# UMI-extract (if present) -> trim -> rRNA remove -> STAR EndToEnd -> dedup (UMI only)
cutadapt -a CTGTAGGCACCATCAAT --discard-untrimmed -m 15 -M 40 -o trimmed.fq.gz reads.fq.gz
bowtie2 -x contaminant_index -U trimmed.fq.gz --un-gz noncontam.fq.gz -S /dev/null -p 8
STAR --genomeDir STAR_index --readFilesIn noncontam.fq.gz --readFilesCommand zcat \
    --alignEndsType EndToEnd --seedSearchStartLmax 15 --outFilterMismatchNmax 2 \
    --quantMode TranscriptomeSAM --outSAMtype BAM SortedByCoordinate --outFileNamePrefix ribo_
samtools index ribo_Aligned.sortedByCoord.out.bam
```

`--quantMode TranscriptomeSAM` writes a SEPARATE `ribo_Aligned.toTranscriptome.out.bam` alongside the sorted genome BAM. RiboCode and riboWaltz transcriptome paths consume the TRANSCRIPTOME BAM; the sorted genome BAM is for plastid/genome-coordinate steps. With UMIs, deduplicate the transcriptome BAM too (coordinate-sort it first, then plain `umi_tools dedup --method directional`; see riboseq-preprocessing), or its ORF/periodicity inputs stay PCR-inflated. Do NOT add `--per-contig`/`--per-gene` here: they treat all reads on a transcript as one position, collapsing the per-codon footprints periodicity depends on.

## Step 2: Periodicity QC and P-site offsets

**Goal:** Certify the library and obtain per-length P-site offsets.

**Approach:** Run riboWaltz to filter periodic read lengths and calibrate offsets; the frame-0 fraction is the pass/fail metric. See ribosome-periodicity.

```r
library(riboWaltz)
annotation <- create_annotation("annotation.gtf")
reads <- bamtolist("bams", annotation = annotation)
reads <- length_filter(reads, length_filter_mode = "periodicity", periodicity_threshold = 50)
offsets <- psite(reads, extremity = "auto")   # per-length P-site offsets
```

Either riboWaltz (above) or the plastid `metagene generate` + `psite` CLI (used in the example script) is acceptable for offsets; pick one per project.

## Step 3: Detect ORFs

**Goal:** Call translated ORFs once offsets are known.

**Approach:** Run RiboCode; read lengths come from the metaplots config, and `-l` is the longest-ORF toggle. See orf-detection.

```bash
prepare_transcripts -g annotation.gtf -f genome.fa -o annot
metaplots -a annot -r ribo_Aligned.toTranscriptome.out.bam -o metaplots
RiboCode -a annot -c metaplots_pre_config.txt -A CTG,GTG -l no -p 0.05 -o ribocode_result
```

## Step 4: Translation efficiency

**Goal:** Test differential translation with matched RNA-seq.

**Approach:** Count both assays over the CDS and use a count-based GLM; use anota2seq when buffering vs control matters. See translation-efficiency.

```r
library(riborex)
res <- riborex(rnaCntTable = rna_cds_counts, riboCntTable = ribo_cds_counts,
               rnaCond = cond, riboCond = cond, engine = "DESeq2")
sig <- res[which(res$padj < 0.05), ]
```

## Step 5: Optional analyses

Stalling/pausing (only on flash-frozen no-drug data; see ribosome-stalling) and initiation-site mapping (needs a harringtonine/LTM library; see initiation-site-mapping) run off the same aligned BAM and calibrated offsets.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Downstream analyses all noisy | Periodicity QC skipped | Gate ORF/stalling on the frame-0 fraction first |
| P-site offsets look wrong | Single hardcoded offset across lengths | Calibrate per length with riboWaltz |
| RiboCode uses wrong read lengths | `-l` passed read lengths | Read lengths come from metaplots; `-l` is a toggle |
| TE hits dominated by low-count genes | Ratio testing | Use riborex/Xtail/anota2seq count GLMs |

## Related Skills

- ribo-seq/riboseq-preprocessing - UMI handling, trimming, rRNA removal, alignment
- ribo-seq/ribosome-periodicity - Periodicity QC and P-site calibration
- ribo-seq/orf-detection - Translated ORF calling
- ribo-seq/translation-efficiency - Differential TE and buffering
- ribo-seq/initiation-site-mapping - Start-codon mapping from TI-seq
- differential-expression/deseq2-basics - Count-based differential testing

## References

- McGlincy NJ, Ingolia NT. 2017. Transcriptome-wide measurement of translation by ribosome profiling. Methods 126:112-129. doi:10.1016/j.ymeth.2017.05.028
- Lauria F, Tebaldi T, Bernabò P, Groen EJN, Gillingwater TH, Viero G. 2018. riboWaltz: Optimization of ribosome P-site positioning in ribosome profiling data. PLoS Comput Biol 14(8):e1006169. doi:10.1371/journal.pcbi.1006169
- Xiao Z, Huang R, Xing X, Chen Y, Deng H, Yang X. 2018. De novo annotation and characterization of the translatome with ribosome profiling data. Nucleic Acids Res 46(10):e61. doi:10.1093/nar/gky179
- Hussmann JA, Patchett S, Johnson A, Sawyer S, Press WH. 2015. Understanding biases in ribosome profiling experiments reveals signatures of translation dynamics in yeast. PLoS Genet 11(12):e1005732. doi:10.1371/journal.pgen.1005732 (cycloheximide distorts codon-level dwell times)
<!-- END FILE: workflows/riboseq-pipeline/SKILL.md -->

## 子目录：workflows/rnaseq-to-de

<!-- BEGIN FILE: workflows/rnaseq-to-de/SKILL.md -->
---
name: bio-workflows-rnaseq-to-de
description: Orchestrates the end-to-end bulk RNA-seq differential-expression pipeline from FASTQ to an annotated DE gene table, chaining fastp QC/trim, Salmon (decoy-aware) or STAR+featureCounts quantification, tximport gene-level collapse, DESeq2/edgeR/limma-voom testing, apeglm shrinkage, and VST-based visualization. Use when committing the reference release and gene-ID namespace once for the whole run, sequencing steps in the defensible order (tximport before DE, raw counts into the model, VST only for viz/clustering), choosing alignment-free vs align-then-count and the DE engine, setting strandedness correctly, keeping batch in the design instead of correcting-then-testing, or handing the signed ranking statistic to downstream enrichment. Hands mechanism to the component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: DESeq2
workflow: true
depends_on:
  - read-qc/fastp-workflow
  - rna-quantification/alignment-free-quant
  - read-alignment/star-alignment
  - read-qc/rnaseq-qc
  - rna-quantification/tximport-workflow
  - rna-quantification/count-matrix-qc
  - differential-expression/deseq2-basics
  - differential-expression/edger-basics
  - differential-expression/de-results
  - differential-expression/de-visualization
qc_checkpoints:
  - after_qc: "Q30 >80%, adapter content <5% (RNA has a lower quality floor than DNA)"
  - after_quant: "Mapping rate >70%, >10M reads mapped, flat gene-body coverage, low rRNA/intronic"
  - after_import: "tx2gene release matches the Salmon index; ID conversion loses few transcripts"
  - after_de: "Dispersion trend sane, PCA separates condition not batch, no Cook's outliers"
---

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, tximport 1.30+, apeglm 1.24+, STAR 2.7.11+, Salmon 1.10+, Subread/featureCounts 2.0.2+ (--countReadPairs added in 2.0.2), fastp 0.23+, ggplot2 3.5+ (kallisto 0.50+ as a Salmon alternative)

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: Salmon selective alignment is default since 1.0 (the historical `--validateMappings` is now a no-op); `DESeqDataSetFromTximport` carries the average-transcript-length offset automatically; `lfcShrink(type='apeglm')` requires `coef` to name a `resultsNames(dds)` coefficient and DROPS the `stat` column. Confirm these in-tool before quoting.

# RNA-seq to Differential Expression Workflow

**"Find differentially expressed genes from my RNA-seq FASTQ files"** -> Chain QC/trim, decoy-aware quantification, tximport gene-level collapse, a count-based DE test, shrinkage, and visualization into one annotated DE table.
- CLI + R: fastp -> (salmon | STAR + featureCounts) -> tximport -> DESeq2/edgeR/limma-voom -> lfcShrink -> VST/volcano

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

A bulk RNA-seq result is decided at four seams between steps, not inside any one tool.

1. **The reference RELEASE + transcriptome/GTF pair is a pipeline-wide commitment made once at quantification and inherited by everything downstream.** The transcriptome FASTA that builds the Salmon index and the GTF that builds the tx2gene map (and drives featureCounts) must be the SAME Ensembl/GENCODE release. Mixing an index built on release 104 with a tx2gene from release 110 silently drops renamed/removed transcripts — no error, just missing genes. This choice also fixes the gene-ID namespace (ENSG is the safe backbone; convert to symbol/Entrez only at the reporting/enrichment seam). Changing the release later forces re-quantification.
2. **Raw counts flow forward; normalized/transformed values are terminal.** Integer counts (or tximport count-scale output) are the ONLY valid input to DESeq2/edgeR/limma-voom. TPM/CPM are for within-sample ranking only; a VST/rlog matrix is for PCA, clustering, heatmaps, and ML — never for re-running a count-based test. Feeding the wrong scale across a join is the single most common silent corruption.
3. **Collapse transcript->gene through tximport, not by summing counts.** tximport carries the average-transcript-length offset that corrects for isoform-usage shifts; naively summing Salmon `NumReads` biases gene counts whenever isoform usage changes across conditions.
4. **Batch belongs in the design, not "corrected" then tested.** Put known batch in the formula (`~ batch + condition`). Running `removeBatchEffect`/ComBat and then testing on the corrected matrix exaggerates confidence (Nygaard 2016); the corrected matrix is for visualization/clustering/ML input only.

## Pipeline map

```
FASTQ (paired)
  | [1] QC & trim ----------------> fastp              (read-qc/fastp-workflow)
  v
  | [2] Quantify -----------------> salmon (decoy-aware)   (rna-quantification/alignment-free-quant)
  v     |   OR  STAR + featureCounts (need a BAM?)         (read-alignment/star-alignment)
  v     ^-- commitment: reference RELEASE + tx/GTF pair, gene-ID namespace
  | [3] Import & collapse tx->gene -> tximport         (rna-quantification/tximport-workflow)
  v     ^-- carries the length offset; NEVER sum NumReads
  | [4] Pre-DE QC ----------------> PCA / dispersion / outliers  (rna-quantification/count-matrix-qc)
  v
  | [5] DE test ------------------> DESeq2 | edgeR-QL | limma-voom  (differential-expression/deseq2-basics)
  v     ^-- RAW counts in; batch in the design, not corrected-then-tested
  | [6] Shrink & extract ---------> lfcShrink(apeglm); pull Wald `stat` for ranking  (differential-expression/de-results)
  v
  | [7] Visualize ----------------> VST heatmap/PCA, volcano  (differential-expression/de-visualization)
  v
Annotated DE table (ENSG + symbol + biotype, log2FC, stat, pvalue, padj, baseMean)
```

## Reference, IDs, and quantification target: the made-once commitments

Decided before the first `salmon quant`; everything downstream inherits them. Mechanism lives in the component skills; the reasoning below is what a reviewer expects justified.

| Commitment | Options | Consequence inherited downstream |
|------------|---------|----------------------------------|
| Reference release | One Ensembl/GENCODE release for BOTH the transcriptome FASTA (index) and the GTF (tx2gene / featureCounts) | Any mismatch silently drops renamed transcripts; fixes DE row names and the pathway-DB key space |
| Gene-ID namespace | ENSG backbone (convert to symbol/Entrez only at reporting) | Symbol space is lossy (aliases, many-ENSG-one-symbol merges genes); stripping the ENSG `.version` with `\..*` also destroys the GENCODE `_PAR_Y` tag, collapsing chrY-PAR onto chrX (rna-quantification/tximport-workflow) |
| Quantification target | Gene-level DGE (`countsFromAbundance="no"`, offset carried) vs transcript-level DTU | DTU needs a DIFFERENT import (`txOut=TRUE` + `dtuScaledTPM`); switching later is a re-import, not a filter — see workflows/splicing-pipeline |
| 3'-tagged vs full-length | 3'-tagged (QuantSeq/bulk-10x): `countsFromAbundance="no"`, no length offset | Length-bias correction does not apply to 3'-tagged libraries |

## The canonical order and why

Each step assumes the previous; two reorderings silently produce wrong results.

1. **QC/trim before quantification** — adapter/quality tails corrupt pseudo-mapping and duplicate structure.
2. **Quantify to the committed reference** — Salmon decoy-aware (genome as decoy) so intron/pseudogene reads are not misassigned to transcripts; STAR only when a genome BAM is also needed downstream.
3. **Import via tximport** — the tx->gene collapse happens HERE, carrying the length offset (order-trap: summing `NumReads` biases genes under isoform shift).
4. **Pre-filter low-count genes** (`rowSums(counts) >= 10`) — this is a speed/memory step, NOT the FDR filter. Order-trap: it does not replace the baseMean independent filtering that `results()` applies at the FDR step; `filterByExpr(y, design)` (edgeR) is the design-aware version and must run once BEFORE dispersion, never after.
5. **DESeq()** on raw counts with batch in the design — size factors, dispersion, Wald/LRT.
6. **results() then lfcShrink()** — independent filtering happens inside `results()` on baseMean; shrink LFC for effect sizes/ranking, but p-values stay from the unshrunken test. Order-trap: apeglm/ashr objects DROP the `stat` column — pull the Wald `stat` from unshrunk `results()` if a signed ranking metric is needed for GSEA.
7. **Visualize on VST** (heatmaps/PCA); volcano uses shrunken LFC + unshrunken p.

## Choosing the quantifier and the DE engine

Pipeline-level selection only; mechanism lives in the component skills.

| Fork | Lean toward | Hand off to |
|------|-------------|-------------|
| Alignment-free (Salmon/kallisto) vs align-then-count (STAR+featureCounts) | Salmon for gene-level DGE (decoy-aware, GC/seq-bias correction, no BAM); STAR when a genome BAM is also needed (splicing, coverage, novel junctions, variants) | rna-quantification/alignment-free-quant, read-alignment/star-alignment |
| DESeq2 vs edgeR-QL vs limma-voom | limma-voom when library sizes vary >3x or outliers dominate; edgeR-QL for tight finite-sample type-I control; DESeq2 for the apeglm/downstream ecosystem (70-90% top-gene overlap on well-designed data) | differential-expression/deseq2-basics, differential-expression/edger-basics |
| `countsFromAbundance` | `no` (gene DGE via DESeqDataSetFromTximport) / `lengthScaledTPM` (DGE when the tool can't take offsets) / `dtuScaledTPM`+`txOut` (DTU) | rna-quantification/tximport-workflow |
| Strandedness `-s` | Confirm, never assume: STAR `ReadsPerGene.out.tab` cols 3 vs 4, or RSeQC `infer_experiment.py`; dUTP/TruSeq is reverse (`-s 2`) | read-qc/rnaseq-qc |

## Primary path: Salmon + tximport + DESeq2

**Goal:** turn trimmed FASTQ into a shrunken, annotated gene-level DE table.

**Approach:** build a decoy-aware index once, quantify each sample, collapse to genes via tximport (release-matched tx2gene), test raw counts with batch in the design, shrink for ranking. Full runnable script: `examples/salmon_deseq2_workflow.R`.

```bash
# Index once: decoy-aware (genome as decoy) so intron/pseudogene reads are not misassigned
grep "^>" genome.fa | cut -d " " -f 1 | sed 's/>//g' > decoys.txt
cat transcriptome.fa genome.fa > gentrome.fa
salmon index -t gentrome.fa -d decoys.txt -i salmon_index -k 31 -p 8

# Quantify (selective alignment is default since 1.0; --gcBias/--seqBias correct known biases)
salmon quant -i salmon_index -l A -1 trimmed/${s}_R1.fq.gz -2 trimmed/${s}_R2.fq.gz \
    -o quants/${s} --gcBias --seqBias -p 8
```

```r
library(tximport); library(DESeq2)
# tx2gene MUST come from the same release as the index (else renamed transcripts drop silently)
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene, ignoreTxVersion = TRUE)
dds <- DESeqDataSetFromTximport(txi, colData = coldata, design = ~ batch + condition)  # batch in design
dds <- dds[rowSums(counts(dds)) >= 10, ]              # speed filter, NOT the FDR filter
dds$condition <- relevel(dds$condition, ref = 'control')
dds <- DESeq(dds)                                     # RAW counts in
res <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')  # ranking/effect size
# For GSEA ranking, pull the Wald stat from the UNSHRUNK results (apeglm drops `stat`):
res_stat <- results(dds, name = 'condition_treated_vs_control')$stat
```

## Alternative path: STAR + featureCounts + DESeq2

**Goal:** produce a genome BAM (reused by splicing/coverage/variant steps) alongside gene counts.

**Approach:** align with `--sjdbOverhang` = readlen-1, count with the verified strandedness, then `DESeqDataSetFromMatrix`. Full script: `examples/star_deseq2_workflow.sh`.

```bash
STAR --runMode genomeGenerate --genomeDir star_index --genomeFastaFiles genome.fa \
    --sjdbGTFfile genes.gtf --sjdbOverhang 149 --runThreadN 8   # 149 for 2x150, not a blanket 100
STAR --genomeDir star_index --readFilesIn trimmed/${s}_R1.fq.gz trimmed/${s}_R2.fq.gz \
    --readFilesCommand zcat --outSAMtype BAM SortedByCoordinate --quantMode GeneCounts \
    --outFileNamePrefix aligned/${s}_ --runThreadN 8
# -s from ReadsPerGene.out.tab cols 3 vs 4 (or infer_experiment.py); -s 2 = dUTP/TruSeq reverse
featureCounts -T 8 -p --countReadPairs -s 2 -a genes.gtf -o counts.txt aligned/*_Aligned.sortedByCoord.out.bam
```

```r
counts <- read.table('counts.txt', header = TRUE, row.names = 1, skip = 1)[, -(1:5)]
dds <- DESeqDataSetFromMatrix(countData = counts, colData = coldata, design = ~ batch + condition)
```

## QC checkpoints between steps

| After | Gate | Interpretation |
|-------|------|----------------|
| QC/trim | Q30 >80%, adapter <5% | RNA has a lower quality floor than DNA; sharp Q30 drop = degraded input |
| Quant/align | Mapping >70%, >10M reads mapped; flat gene-body coverage; low rRNA%/intronic% | 3' bias = degradation/oligo-dT; high intronic = pre-mRNA/gDNA; high intergenic = gDNA/annotation gap — all compromise DE BEFORE it runs (read-qc/rnaseq-qc) |
| Import | tx2gene release == index release; few transcripts dropped; report the ID-conversion rate (<0.85 => wrong ID type or organism) | Mismatched release silently loses renamed transcripts |
| Pre-DE | Dispersion trend sane; PCA separates condition not batch; no Cook's outliers | PCA clustering by batch => batch dominates; add it to the design (rna-quantification/count-matrix-qc) |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Many genes missing / low tx conversion | Salmon index and tx2gene from different releases | Rebuild both from ONE release; pin it for the whole cohort |
| Gene counts biased where isoforms switch | Summed Salmon `NumReads` instead of importing | Collapse via tximport (carries the length offset) |
| "invalid class DESeqDataSet" or nonsense LFCs | TPM/VST fed into DESeq2 | Raw counts (or `lengthScaledTPM`) only; VST is for viz/ML |
| Counts collapsed / library looks failed | Wrong featureCounts `-s` strandedness | Infer with `infer_experiment.py` or STAR cols 3 vs 4 before counting |
| Suspiciously many DE genes, tiny p-values | Batch-corrected matrix fed to the test | Keep batch in the design; correct only for visualization |
| `lfcShrink` error / wrong contrast | `coef` not in `resultsNames(dds)`, or ranking off the shrunk object | Use a `resultsNames` coefficient; pull `stat` from unshrunk `results()` |

## Pipeline map (hand-offs)

- read-qc/fastp-workflow - adapter/quality trimming and report interpretation
- rna-quantification/alignment-free-quant - Salmon/kallisto decoy-aware quantification
- read-alignment/star-alignment - STAR index/sjdbOverhang, 2-pass, GeneCounts strandedness
- rna-quantification/tximport-workflow - tx->gene collapse, countsFromAbundance, tx2gene, ID-version traps
- rna-quantification/count-matrix-qc - pre-DE PCA, dispersion, Cook's outliers, batch checks
- differential-expression/deseq2-basics - the DESeq2 model, design, contrasts
- differential-expression/de-results - extracting/annotating results and the signed ranking statistic
- differential-expression/de-visualization - volcano/MA/heatmap on the right scale

The complete runnable scripts for both paths are in this skill's examples/ (`salmon_deseq2_workflow.R`, `star_deseq2_workflow.sh`).

## Related Skills

- database-access/geo-data - Find a GSE on GEO, detect SuperSeries, link to SRA
- database-access/sra-data - Download paired-end FASTQ from SRA / ENA / STRIDES cloud
- sequence-io/fastq-quality - Confirm the FASTQ quality encoding before trimming public or pre-2011 data
- sequence-io/paired-end-fastq - Keep R1/R2 mates synchronized; independent per-mate filtering desyncs pairs
- read-qc/fastp-workflow - Detailed QC options and parameters
- read-qc/rnaseq-qc - Post-alignment RNA QC: strandedness, gene-body coverage, rRNA/intronic
- read-alignment/star-alignment - The align path (BAM for splicing/coverage/variants)
- rna-quantification/alignment-free-quant - Salmon and kallisto details
- rna-quantification/tximport-workflow - tximport options, countsFromAbundance, tx2gene creation
- rna-quantification/count-matrix-qc - Pre-DE QC and diagnostics
- differential-expression/deseq2-basics - Complete DESeq2 reference
- differential-expression/de-results - Results extraction, annotation, ranking statistic
- differential-expression/de-visualization - Advanced visualization options
- alternative-splicing/isoform-switching - Transcript-level DTU when gene-level is not enough (splicing fork)
- pathway-analysis/go-enrichment - Next step: functional enrichment (workflows/expression-to-pathways)

## References

- Soneson C, Love MI, Robinson MD (2015) Differential analyses for RNA-seq: transcript-level estimates improve gene-level inferences. *F1000Research* 4:1521. DOI 10.12688/f1000research.7563.1. (tximport; the tx->gene length-offset seam.)
- Love MI, Huber W, Anders S (2014) Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biology* 15:550. DOI 10.1186/s13059-014-0550-8.
- Patro R, Duggal G, Love MI, Irizarry RA, Kingsford C (2017) Salmon provides fast and bias-aware quantification of transcript expression. *Nature Methods* 14:417-419. DOI 10.1038/nmeth.4197.
- Nygaard V, Rødland EA, Hovig E (2016) Methods that remove batch effects while retaining group differences may lead to exaggerated confidence in downstream analyses. *Biostatistics* 17:29-39. DOI 10.1093/biostatistics/kxv027. (batch belongs in the design.)
- Ewels PA, Peltzer A, Fillinger S, et al (2020) The nf-core framework for community-curated bioinformatics pipelines. *Nature Biotechnology* 38:276-278. DOI 10.1038/s41587-020-0439-x. (nf-core/rnaseq: the reproducible reference orchestration.)
<!-- END FILE: workflows/rnaseq-to-de/SKILL.md -->

## 子目录：workflows/scrnaseq-pipeline

<!-- BEGIN FILE: workflows/scrnaseq-pipeline/SKILL.md -->
---
name: bio-workflows-scrnaseq-pipeline
description: Orchestrates the end-to-end single-cell RNA-seq pipeline from 10x Cell Ranger output to annotated cell types, chaining ambient-RNA removal, doublet detection, MAD-adaptive QC, normalization, integration, clustering, marker annotation, and (separately) pseudobulk DE + differential abundance. Use when honoring the made-once counting commitments (reference build/Ensembl vintage, --include-introns, cell-calling, feature namespace), ordering correct-then-detect-then-normalize (ambient before doublet before normalize), running per-sample QC before merge, integrating-then-clustering (never testing on integrated values), aggregating to pseudobulk for condition DE instead of cells-as-replicates, or pairing DE with differential abundance. Hands mechanism to the single-cell component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: Seurat
goal_approach_exempt: true
workflow: true
depends_on:
  - single-cell/data-io
  - single-cell/preprocessing
  - single-cell/doublet-detection
  - single-cell/clustering
  - single-cell/markers-annotation
qc_checkpoints:
  - after_loading: "Expected cell count, reasonable UMI distribution"
  - after_qc: "Remove low-quality cells and doublets"
  - after_normalization: "No batch effects, HVGs look sensible"
  - after_clustering: "Clusters are biologically meaningful"
---

## Version Compatibility

Reference examples tested with: Cell Ranger 10.0+ (human/mouse refs on Ensembl v110), Seurat 5.1+, Scanpy 1.10+, scDblFinder 1.16+, SoupX 1.6+, CellBender 0.3+, harmony/scvi-tools current, ggplot2 3.5+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: the Cell Ranger `filtered_feature_bc_matrix` is cell-CALLING only, NOT ambient-corrected; recovering low-RNA cells or running SoupX/CellBender needs the RAW matrix. `--include-introns` is default TRUE since Cell Ranger 7 (essential for nuclei). `gex_only=True`/default silently drops Antibody Capture/CRISPR/HTO features. Confirm in-tool before quoting.

# Single-Cell RNA-seq Pipeline

**"Analyze my single-cell RNA-seq data from counts to cell types"** -> Orchestrate QC filtering, normalization (scanpy/Seurat), batch integration (scVI/Harmony), clustering, marker detection, cell type annotation, and trajectory inference.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## Made-once commitments (decided at `cellranger count`, inherited downstream)

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Reference build + Ensembl vintage (CR v10 = Ensembl v110) | Every gene ID/marker lookup/cross-dataset merge; join on `gene_ids` (stable), not symbols (lossy across releases) |
| `--include-introns` (default TRUE since CR 7) | Total UMI/cell and snRNA-vs-scRNA comparability; nuclei need introns; mixing intron-on/off samples is a hidden batch axis |
| Cell-vs-empty-droplet calling | The filtered matrix is cell-CALLING only, NOT ambient-corrected; SoupX/CellBender and low-RNA-cell rescue need the RAW matrix (filtered-only is irreversible loss) |
| Feature/barcode namespace (`gex_only`) | `gex_only=True` silently drops ADT/HTO/CRISPR features; set False and split by `feature_types` for CITE-seq/hashed pools |

## Pipeline orchestration: the ordering decisions that make or break the result

Stage order is not arbitrary; getting it wrong silently corrupts every downstream step. The cross-cutting decisions this pipeline must get right:
- Correct-then-detect-then-normalize, never reorder. Ambient-RNA removal (SoupX/CellBender) reads the RAW droplet matrix and MUST precede doublet detection and the final QC thresholds (ambient inflation distorts both doublet scores and per-cell QC); doublet detection precedes integration (doublets seed fake intermediate clusters). See single-cell/preprocessing.
- Multiplexed (hashed) pools are demultiplexed FIRST. When samples are pooled with cell hashing (HTO/MULTI-seq) or genotype multiplexing, assign each cell to its sample of origin and remove cross-sample doublets before any per-sample step; the per-sample QC and doublet operations below assume the pool is already split by sample. See single-cell/hashing-demultiplexing.
- Per-sample QC and doublet detection come BEFORE any merge or integration. Ambient-RNA cleanup (SoupX/CellBender), mito/gene-count filtering, and doublet calling (expected rate ~0.8% per 1,000 recovered cells) are per-capture operations; running them on a pooled object lets one lane's artifacts contaminate the shared null and lets surviving doublets form fake intermediate clusters. See single-cell/preprocessing and single-cell/doublet-detection.
- Integrate, THEN cluster, THEN annotate - never reorder. For multi-sample designs, batch-correct on a shared embedding (Harmony/scVI/RPCA) and cluster on the corrected graph; clustering before correction makes clusters track samples or lanes instead of biology, and annotation has nothing to label until clusters exist. See single-cell/batch-integration, single-cell/clustering, single-cell/cell-annotation.
- Over-integration erases biology. Batch-mixing metrics (kBET, iLISI) are maximized by destroying structure, so a method that flattens real cell states scores perfectly; pair every batch metric with a bio-conservation metric and re-inspect rare populations after correction. Batch-corrected expression is for embedding and clustering only - never feed it to differential expression. See single-cell/batch-integration.
- Condition-level DE must use pseudobulk, not cells-as-replicates. Testing thousands of cells per donor as independent replicates is pseudoreplication and inflates false positives by orders of magnitude (Squair 2021); aggregate RAW counts per sample x cell type and hand them to DESeq2/edgeR/limma-voom. Step 7 marker p-values are descriptive ranking for labeling, not condition inference. See single-cell/markers-annotation and differential-expression/deseq2-basics.
- Composition shifts are tested separately and masquerade as DE. A cluster-level expression change between conditions can be a pure proportion shift (a mixed cluster's substates re-balance with no gene changing per cell), invisible if only DE is run; always pair condition DE with a differential-abundance test (Milo cluster-free, or scCODA/sccomp/propeller cluster-based). See single-cell/differential-abundance.

The Seurat and Scanpy paths below are written single-sample for clarity. A multiplexed design demultiplexes the pool first (single-cell/hashing-demultiplexing); a multi-sample design then inserts per-sample QC and doublet removal, a merge, and an integration step between normalization (Step 4) and dimensionality reduction (Step 5); the rest of the order is unchanged.

## Workflow Overview

```
10X data (RAW + filtered_feature_bc_matrix)
    |
    v
[0. Ambient removal] ---> SoupX/CellBender on RAW (per sample)   (single-cell/preprocessing)
    |
    v
[1. Load Data] ---------> Read10X / read_10x_h5
    |
    v
[2. QC + Doublets] -----> MAD-adaptive nFeature/percent.mt; scDblFinder/Scrublet (per sample, before merge)
    |
    v
[3. Normalization] -----> SCTransform or LogNormalize
    |
    v
[4. HVG Selection] -----> FindVariableFeatures
    |
    v
[5. Dim Reduction] -----> PCA -> UMAP
    |
    v
[6. Clustering] --------> FindNeighbors -> FindClusters
    |
    v
[7. Markers] -----------> FindAllMarkers
    |
    v
[8. Annotation] --------> Manual or automated
    |
    v
Annotated Seurat/AnnData object
```

## Primary Path: Seurat (R)

The Seurat/Scanpy paths below start from the filtered matrix for clarity. In practice, run ambient-RNA removal FIRST on the RAW droplet matrix per sample (SoupX needs raw+filtered+clusters; CellBender folds calling+denoise and is best for snRNA/high-ambient) — pick ONE (double-correction over-strips). See single-cell/preprocessing.

### Step 1: Load 10X Data

```r
library(Seurat)
library(ggplot2)
library(dplyr)

# Load from Cell Ranger output
data_dir <- 'cellranger_output/filtered_feature_bc_matrix'
counts <- Read10X(data.dir = data_dir)

# Create Seurat object
seurat_obj <- CreateSeuratObject(counts = counts, project = 'my_project',
                                  min.cells = 3, min.features = 200)
```

### Step 2: Quality Control

```r
# Calculate QC metrics
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')
seurat_obj[['percent.ribo']] <- PercentageFeatureSet(seurat_obj, pattern = '^RP[SL]')

# Visualize QC metrics
VlnPlot(seurat_obj, features = c('nFeature_RNA', 'nCount_RNA', 'percent.mt'), ncol = 3)

# Filter cells
seurat_obj <- subset(seurat_obj,
                     nFeature_RNA > 200 &
                     nFeature_RNA < 5000 &
                     percent.mt < 20 &
                     nCount_RNA > 500)

cat('Cells after QC:', ncol(seurat_obj), '\n')
```

**QC Checkpoint 1:** Review QC plots
- Remove cells with very low/high gene counts
- Remove cells with high mitochondrial content (dying cells)

### Step 3: Doublet Detection

```r
library(scDblFinder)

# Convert to SCE for scDblFinder
sce <- as.SingleCellExperiment(seurat_obj)
sce <- scDblFinder(sce)

# Add back to Seurat
seurat_obj$doublet_class <- sce$scDblFinder.class
seurat_obj$doublet_score <- sce$scDblFinder.score

# Remove doublets
seurat_obj <- subset(seurat_obj, doublet_class == 'singlet')
cat('Cells after doublet removal:', ncol(seurat_obj), '\n')
```

### Step 4: Normalization with SCTransform

```r
# SCTransform (recommended for most analyses)
seurat_obj <- SCTransform(seurat_obj, verbose = FALSE)
```

Alternative: Standard normalization
```r
seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj, selection.method = 'vst', nfeatures = 2000)
seurat_obj <- ScaleData(seurat_obj)
```

Regressing out `percent.mt` (or `nCount`/cell-cycle) is NOT reflexive: those covariates are confounded with real cell state and regressing them can erase biology, so only pass `vars.to.regress` for a covariate verified not confounded with the signal of interest. See single-cell/preprocessing.

### Step 5: Dimensionality Reduction

```r
# PCA
seurat_obj <- RunPCA(seurat_obj, npcs = 50, verbose = FALSE)

# Determine optimal PCs
ElbowPlot(seurat_obj, ndims = 50)

# UMAP
n_pcs <- 30  # Choose based on elbow plot
seurat_obj <- RunUMAP(seurat_obj, dims = 1:n_pcs, verbose = FALSE)
```

### Step 6: Clustering

```r
# Find neighbors
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:n_pcs, verbose = FALSE)

# Find clusters (try multiple resolutions)
seurat_obj <- FindClusters(seurat_obj, resolution = c(0.2, 0.4, 0.6, 0.8, 1.0), verbose = FALSE)

# Visualize
DimPlot(seurat_obj, reduction = 'umap', group.by = 'SCT_snn_res.0.4', label = TRUE)
```

**QC Checkpoint 2:** Assess clustering
- Clusters should be visually separable on UMAP
- Resolution 0.4-0.8 is often appropriate

### Step 7: Find Marker Genes

```r
# Set identity to chosen resolution
Idents(seurat_obj) <- 'SCT_snn_res.0.4'

# Find markers for all clusters
markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)

# Top markers per cluster
top_markers <- markers %>%
    group_by(cluster) %>%
    slice_max(n = 10, order_by = avg_log2FC)

# Visualize top markers
DoHeatmap(seurat_obj, features = top_markers$gene) + NoLegend()
```

### Step 8: Cell Type Annotation

```r
# Manual annotation based on known markers
# Example for PBMC data:
cluster_annotations <- c(
    '0' = 'CD4 T cells',
    '1' = 'CD14 Monocytes',
    '2' = 'B cells',
    '3' = 'CD8 T cells',
    '4' = 'NK cells',
    '5' = 'CD16 Monocytes',
    '6' = 'Dendritic cells'
)

seurat_obj$cell_type <- cluster_annotations[as.character(Idents(seurat_obj))]

# Final UMAP
DimPlot(seurat_obj, reduction = 'umap', group.by = 'cell_type', label = TRUE)

# Save object
saveRDS(seurat_obj, 'seurat_annotated.rds')
```

## Alternative Path: Scanpy (Python)

```python
import scanpy as sc
import numpy as np

# Load 10X data
adata = sc.read_10x_h5('filtered_feature_bc_matrix.h5')
adata.var_names_make_unique()

# QC metrics
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)

# Filter (flat cutoffs are illustrative; prefer MAD-adaptive, tissue-aware thresholds, see single-cell/preprocessing)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata = adata[adata.obs.n_genes_by_counts < 5000, :]
adata = adata[adata.obs.pct_counts_mt < 20, :]

# Doublet detection (rate from recovered cells, not the 0.05 placeholder, see single-cell/doublet-detection)
expected_rate = 0.008 * adata.n_obs / 1000
sc.pp.scrublet(adata, expected_doublet_rate=expected_rate)
adata = adata[~adata.obs['predicted_doublet'], :]

# Normalize and HVGs
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# PCA, neighbors, UMAP -- stash log-normalized values in .raw BEFORE scaling, or rank_genes_groups
# later computes logfoldchanges from z-scores (negative means -> NaN/garbage LFCs)
adata.raw = adata
adata = adata[:, adata.var.highly_variable]
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, n_comps=50)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.umap(adata)

# Clustering (pin the backend for reproducibility; default flips to igraph)
sc.tl.leiden(adata, resolution=0.5, flavor='igraph', n_iterations=2, directed=False)

# Markers
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=10, sharey=False)

# Save
adata.write('scanpy_annotated.h5ad')
```

## Parameter Recommendations

| Step | Parameter | Recommendation |
|------|-----------|----------------|
| QC | min.features | 200-500 |
| QC | max.features | 2500-5000 (depends on data) |
| QC | percent.mt | <10-20% (tissue-dependent) |
| SCTransform | vars.to.regress | none by default; only a validated non-confounded covariate |
| PCA | npcs | 30-50 |
| UMAP | dims | 15-30 (check elbow plot) |
| Clustering | resolution | 0.4-0.8 (start with 0.5) |

QC cutoffs above are illustrative starting points, not universal thresholds: set min/max features and mito % per dataset from the data (MAD-adaptive, tissue-aware) rather than porting flat values, since healthy mito fraction varies by tissue. See single-cell/preprocessing.

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| All cells filtered | QC too strict | Relax thresholds |
| Poor UMAP separation | Too few HVGs or PCs | Increase nfeatures, check n_pcs |
| Too many/few clusters | Wrong resolution | Adjust resolution parameter |
| Unknown cell types | Missing markers | Check known marker genes manually |

## Complete R Workflow

```r
library(Seurat)
library(scDblFinder)
library(ggplot2)
library(dplyr)

# Configuration
data_dir <- 'filtered_feature_bc_matrix'
output_dir <- 'results'
dir.create(output_dir, showWarnings = FALSE)

# Load
counts <- Read10X(data.dir = data_dir)
seurat_obj <- CreateSeuratObject(counts = counts, min.cells = 3, min.features = 200)
cat('Initial cells:', ncol(seurat_obj), '\n')

# QC
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')
seurat_obj <- subset(seurat_obj, nFeature_RNA > 200 & nFeature_RNA < 5000 & percent.mt < 20)
cat('After QC:', ncol(seurat_obj), '\n')

# Doublets
sce <- as.SingleCellExperiment(seurat_obj)
sce <- scDblFinder(sce)
seurat_obj$doublet <- sce$scDblFinder.class
seurat_obj <- subset(seurat_obj, doublet == 'singlet')
cat('After doublet removal:', ncol(seurat_obj), '\n')

# Normalize (no reflexive vars.to.regress; regress only a validated non-confounded covariate)
seurat_obj <- SCTransform(seurat_obj, verbose = FALSE)

# Dimension reduction
seurat_obj <- RunPCA(seurat_obj, npcs = 50, verbose = FALSE)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30, verbose = FALSE)

# Cluster
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30, verbose = FALSE)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5, verbose = FALSE)

# Markers
markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)
write.csv(markers, file.path(output_dir, 'markers.csv'))

# Save
saveRDS(seurat_obj, file.path(output_dir, 'seurat_object.rds'))

# Plots
pdf(file.path(output_dir, 'umap.pdf'), width = 10, height = 8)
DimPlot(seurat_obj, reduction = 'umap', label = TRUE)
dev.off()

cat('Pipeline complete. Object saved to:', output_dir, '\n')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Ambient markers everywhere (e.g. Hb across all PBMCs) | Ran SoupX/CellBender on the FILTERED matrix (soup already removed) | Run ambient removal on the RAW droplet matrix, before QC |
| Fake intermediate cell states | Doublets removed AFTER clustering/integration | Call doublets per sample before merge/normalize |
| Clusters track sample/lane, not biology | Clustered before integration | Integrate -> cluster -> annotate |
| Inflated DE, thousands of false positives | Tested cells as replicates (on integrated values) | Pseudobulk RAW counts per sample x cell-type -> DESeq2/edgeR/limma (Squair 2021) |
| "DE change" is really a proportion shift | Only ran DE, not abundance | Pair with differential abundance (Milo/scCODA/propeller) |
| Biology collapses to one blob | Reflexively regressed total_counts/cell-cycle | Regress only a validated, non-confounded covariate |
| CITE-seq/hashtag features vanish | `gex_only=True` default | Set False; split by `feature_types` |

## References

- Heumos L, Schaar AC, Lance C, et al (2023) Best practices for single-cell analysis across modalities. *Nature Reviews Genetics* 24:550-572. DOI 10.1038/s41576-023-00586-w. (canonical pipeline order.)
- Squair JW, Gautier M, Kathe C, et al (2021) Confronting false discoveries in single-cell differential expression. *Nature Communications* 12:5692. DOI 10.1038/s41467-021-25960-2. (cells-as-replicates is pseudoreplication; pseudobulk.)
- Fleming SJ, Chaffin MD, Arduini A, et al (2023) Unsupervised removal of systematic background noise from droplet-based single-cell experiments using CellBender. *Nature Methods* 20:1323-1335. DOI 10.1038/s41592-023-01943-7. (ambient removal on the RAW matrix.)

## Related Skills

- database-access/geo-data - Resolve GSE to SRA; detect SuperSeries before processing
- database-access/sra-data - Download 10x records with --include-technical for barcodes/UMIs
- single-cell/data-io - Loading 10X, h5ad, RDS, and h5mu formats
- single-cell/preprocessing - QC thresholds, ambient-RNA removal, normalization choice
- single-cell/doublet-detection - Per-sample doublet calling before integration
- single-cell/hashing-demultiplexing - Assign multiplexed pools to samples and call cross-sample doublets before QC
- single-cell/batch-integration - Multi-sample integration and over-correction diagnosis
- single-cell/clustering - Resolution sweep and cluster validation
- single-cell/markers-annotation - Marker discovery, manual labeling, and pseudobulk condition DE
- single-cell/cell-annotation - Automated reference-based label transfer
- single-cell/differential-abundance - Test whether cell-type proportions shifted between conditions
- single-cell/trajectory-inference - Pseudotime and lineage reconstruction for continuous processes
- single-cell/multimodal-integration - CITE-seq and multiome joint analysis
- differential-expression/deseq2-basics - Pseudobulk condition DE engine for aggregated counts
- differential-expression/de-results - Shrink, filter, and interpret pseudobulk DE results
- pathway-analysis/go-enrichment - Functional interpretation of marker and DE gene lists
- workflows/grn-pipeline - Downstream: infer gene regulatory networks (pySCENIC Path A) from the annotated object
- workflows/spatial-pipeline - Downstream: the annotated reference deconvolves spatial spots
<!-- END FILE: workflows/scrnaseq-pipeline/SKILL.md -->

## 子目录：workflows/smrna-pipeline

<!-- BEGIN FILE: workflows/smrna-pipeline/SKILL.md -->
---
name: bio-workflows-smrna-pipeline
description: Orchestrates the end-to-end small RNA-seq pipeline from FASTQ to differential miRNAs and expression-filtered targets, chaining kit-aware cutadapt trimming (adapter on every read, UMI/4N handling), miRge3 known+isomiR quantification or miRDeep2 novel discovery, compositionally-aware DESeq2, and miRanda target prediction. Use when committing the library-kit adapter/UMI handling once, choosing the NORMALIZER (which drives which miRNAs are called DE more than the DE model does), deciding known quantification vs novel discovery, handling biofluid/plasma libraries that lack a trustworthy endogenous normalizer, routing tRF/piRNA reads to their own profiling, or feeding RAW (not RPM) counts with size-factor inspection into DE. Hands mechanism to the small-rna-seq component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: miRge3.0
workflow: true
depends_on:
  - small-rna-seq/smrna-preprocessing
  - small-rna-seq/mirge3-analysis
  - small-rna-seq/mirdeep2-analysis
  - small-rna-seq/differential-mirna
  - small-rna-seq/target-prediction
  - small-rna-seq/trf-pirna-profiling
qc_checkpoints:
  - after_trim: "Read-length peak 21-23 nt (30+ smear = degradation/tRNA/rRNA; 26-32 peak = piRNA)"
  - after_quant: "RNA-class composition checked (miRNA vs tRF/rRF/piRNA); abundant non-miRNA = different story"
  - before_de: "RAW counts confirmed (not RPM); size factors inspected for compositional distortion"
  - after_de: "baseMean reported with every call (significant FC on a ~5-count miRNA is noise)"
---

## Version Compatibility

Reference examples tested with: cutadapt 4.4+, miRge3.0 0.1.4+, miRDeep2 2.0.1.3+, DESeq2 1.42+, apeglm 1.24+, miRanda 3.3a, umi_tools 1.1+, miRTrace 1.0+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: the correct 3' adapter sequence and the UMI/4N scheme are KIT-specific (TruSeq vs NEXTflex vs QIAseq) — confirm against the kit before trimming. The normalizer that best fits compositional miRNA data drifts with the method literature; treat the table below as a decision aid to validate, not a fixed rule.

# Small RNA-seq Pipeline

**"Analyze my small RNA-seq data from FASTQ to differential miRNAs"** -> Chain kit-aware trimming, known-miRNA quantification (or novel discovery), a compositionally-aware DE test, and expression-filtered target prediction.
- CLI + R: cutadapt -> (miRge3.0 | miRDeep2) -> DESeq2 (inspect size factors) -> miRanda (filter by anti-correlated mRNA)

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

A small RNA-seq result turns on two things the mRNA pipeline never faces — the adapter is on every read, and the counts are compositional — so the trustworthy result is decided at these seams.

1. **The library kit fixes adapter + UMI/4N handling, committed once at trimming and un-reversible.** The insert (~22 nt) is far shorter than the read, so the 3' adapter is on EVERY real read and `--discard-untrimmed` correctly drops no-insert junk (the inverse of genomic DNA). NEXTflex 4N random bases are stripped AFTER adapter removal; QIAseq UMIs are extracted and deduped. NEVER position-dedup a non-UMI small-RNA library — abundant miRNAs legitimately share start positions, so position-dedup destroys real signal.
2. **The normalizer is the dominant analytic commitment — more than the DE model.** miRNA counts are few-featured and compositional; a handful of miRNAs can dominate the library. Global scaling (TMM's 30%/5% trimming, median-of-ratios) is built for ~20k mRNAs and is harmful among hundreds of miRNAs (Garmire 2012). The normalizer choice CHANGES which miRNAs are called DE. Commit and report it; do not default silently.
3. **RAW counts (not RPM) flow into DESeq2, and size factors must be inspected.** A large rise in one abundant miRNA mechanically deflates all others (the closed-composition artifact), manufacturing spurious "down" calls. Confirm the input is raw integer counts and inspect `sizeFactors(dds)` before trusting any call.
4. **Targets are hypotheses, not findings.** miRanda output must be intersected with anti-correlated mRNA DE and validated databases before interpretation.

## Pipeline map

```
FASTQ (single-end small RNA)
  | [1] Trim (kit-aware) --------> cutadapt (+ umi_tools / 4N)   (small-rna-seq/smrna-preprocessing)
  v     ^-- commitment: kit adapter + UMI/4N; --discard-untrimmed; NO position-dedup w/o UMI
  | [2] Quantify OR discover ----> miRge3.0 (known+isomiR) | miRDeep2 (novel)  (small-rna-seq/mirge3-analysis, mirdeep2-analysis)
  v
  | [3] Differential expression -> DESeq2 on RAW counts; INSPECT size factors   (small-rna-seq/differential-mirna)
  v     ^-- commitment: the NORMALIZER (drives which miRNAs are DE)
  | [4] Target prediction -------> miRanda, filtered by anti-correlated mRNA DE  (small-rna-seq/target-prediction)
  v
Differential miRNAs + expression-supported targets
   (tRF/piRNA reads -> small-rna-seq/trf-pirna-profiling)
```

## Made-once commitments

| Commitment | Choice | Consequence inherited downstream |
|------------|--------|----------------------------------|
| Library kit adapter + UMI/4N | TruSeq / NEXTflex-4N / QIAseq-UMI handling, set at trimming | Wrong adapter or missed 4N/UMI corrupts every count; non-UMI position-dedup destroys real miRNAs |
| Quantification target | Known-miRNA + isomiR (miRge3) vs novel discovery (miRDeep2) | Discovery is high-FP and needs a genome + bowtie1; quantification is the common curated case |
| Normalizer | median-of-ratios/TMM vs quantile/loess vs RUVg vs CoDA/ALDEx2 | Which miRNAs are DE (more than the DE model choice) |
| Biofluid vs tissue | plasma/serum has NO trustworthy endogenous normalizer | DE may be uninterpretable without spike-ins + hemolysis modeling |

## The canonical order and why

1. **Trim (kit-aware)** — adapter removal with `--discard-untrimmed`; 4N/UMI handling before or during collapse. Order-trap: position-deduping a non-UMI library removes real high-abundance miRNAs.
2. **miRTrace QC** — length/complexity, RNA-class composition, cross-clade contamination BEFORE quantification (a good mapping rate hides sample swaps and reagent contamination).
3. **Quantify (miRge3) or discover (miRDeep2)** — to raw integer counts. For miRDeep2, choose the score cutoff from `survey.pl` signal-to-noise, not a fixed rule.
4. **Low-count filter** (`rowSums >= 10`, lower than mRNA) BEFORE normalization.
5. **DE with the committed normalizer** — raw counts into DESeq2; inspect `sizeFactors`. Order-trap: feeding RPM/CPM bakes compositional distortion into an invalid model.
6. **Target prediction** — intersect miRanda predictions with anti-correlated mRNA DE (order-trap: enrichment on raw predictions is false-positive-laden).

## Fork/decision points

Pipeline-level selection only; mechanism lives in the component skills.

| Fork | Lean toward | Hand off to |
|------|-------------|-------------|
| Quantify vs discover | miRge3.0 (known + isomiR, curated, common) vs miRDeep2 (novel only; high FP, genome + bowtie1, survey.pl cutoff) | small-rna-seq/mirge3-analysis, small-rna-seq/mirdeep2-analysis |
| Normalizer | median-of-ratios/TMM (risky under composition shift) vs quantile/loess (better on skewed miRNA) vs RUVg (control/empirical miRNAs) vs CoDA/ALDEx2 (compositional sensitivity check) | small-rna-seq/differential-mirna |
| Biofluid/plasma | no trustworthy endogenous normalizer (miR-16 is hemolysis-sensitive, U6 degrades); cel-miR-39 spike controls EXTRACTION not biological scale; model batch/hemolysis explicitly | small-rna-seq/differential-mirna |
| RNA class | miRNA vs tRF/piRNA (26-32 nt peak) -> route to trf-pirna-profiling (MINTmap/unitas) | small-rna-seq/trf-pirna-profiling |

## Primary path: cutadapt -> miRge3.0 -> DESeq2 -> miRanda

**Goal:** turn kit-specific FASTQ into differential miRNAs with expression-supported targets.

**Approach:** trim to the kit, quantify known miRNAs/isomiRs, test RAW counts with size-factor inspection, then filter targets by anti-correlation. (The runnable script in examples/ shows the miRDeep2 novel-discovery route below; the miRge3.0 commands are shown here.)

```bash
# Kit-aware trim: adapter on EVERY read, so --discard-untrimmed drops no-insert junk (inverse of gDNA).
# NEXTflex 4N: cutadapt -u 4 -u -4 AFTER adapter. QIAseq UMIs: umi_tools. NEVER position-dedup non-UMI.
cutadapt -a TGGAATTCTCGGGTGCCAAGG --minimum-length 18 --maximum-length 30 --discard-untrimmed \
    -o trimmed.fastq.gz reads.fastq.gz

# Known-miRNA + isomiR quantification (the common case). NOTE: v3 has NO 'annotate' subcommand
# (that was miRge2); it is `miRge3.0 -s ...`. Reads are already cutadapt-trimmed, so -a is OMITTED
# (v3 has no 'none' keyword; passing one makes cutadapt treat it as an adapter sequence and fail).
# isomiRs are annotated by default; -gff emits the isomiR GFF.
# (-ai would instead compute A-to-I editing, a separate analysis, not isomiR reporting.)
miRge3.0 -s trimmed.fastq.gz -lib /path/to/miRge3_Lib -on human -db mirbase \
    -gff -cpu 8 -o mirge_out
```

```r
library(DESeq2)
# RAW counts (miR.Counts.csv), NOT RPM. A few miRNAs can dominate, so inspect sizeFactors first.
# miRge3.0 writes into a timestamped subfolder (mirge_out/miRge.YYYY-M-D_h-m-s/), not directly into -o
counts <- read.csv(Sys.glob('mirge_out/miRge.*/miR.Counts.csv')[1], row.names = 1)
dds <- DESeqDataSetFromMatrix(round(counts), colData, ~condition)
dds <- dds[rowSums(counts(dds)) >= 10, ]      # lower prefilter than mRNA
dds <- DESeq(dds)
print(sizeFactors(dds))                       # a dominant-miRNA shift distorts these -> spurious calls
res <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')
```

```bash
# Targets are a hypothesis: intersect with anti-correlated mRNA DE before trusting them.
# -sc 140: miRanda default alignment-score floor; -en -20: keep duplexes with MFE <= -20 kcal/mol (stable binding)
miranda mature_mirnas.fa target_3utrs.fa -sc 140 -en -20 -strict -out targets.txt
```

## Novel discovery alternative: miRDeep2

**Goal:** discover previously unannotated miRNAs (only when that is the question).

**Approach:** collapse reads, map to the genome with bowtie1, run miRDeep2, and pick the score cutoff from the signal-to-noise survey — not a fixed threshold. Full runnable script: `examples/smrna_full_pipeline.sh`.

```bash
gunzip -kc trimmed.fastq.gz > trimmed.fastq            # mapper.pl reads plain-text FASTQ, not gzip
mapper.pl trimmed.fastq -e -h -i -j -l 18 -m -p genome_index \
    -s reads_collapsed.fa -t reads_collapsed_vs_genome.arf
miRDeep2.pl reads_collapsed.fa genome.fa reads_collapsed_vs_genome.arf \
    mature_ref.fa none hairpin_ref.fa -t Human      # score cutoff from survey.pl signal-to-noise
```

## QC checkpoints between steps

| After | Gate | Interpretation |
|-------|------|----------------|
| Trim | Read-length peak 21-23 nt | 30+ nt smear = degradation/tRNA/rRNA; 26-32 nt peak = piRNA (route to trf-pirna-profiling) |
| miRTrace/align | RNA-class composition (miRNA vs tRF/rRF/piRNA); cross-clade contamination | Abundant non-miRNA classes mean this is a tRF/piRNA story, not a miRNA one |
| Before DE | RAW counts (not RPM); size factors inspected | A dominant-miRNA shift distorts size factors and manufactures spurious "down" calls |
| After DE | baseMean reported with every call | A significant fold-change on a ~5-count miRNA is noise |
| Targets | filtered by anti-correlated mRNA DE + validated DBs | Raw miRanda predictions are hypotheses, not findings |

Ligation bias means absolute cross-miRNA abundance WITHIN a sample is untrustworthy; compare the same miRNA across samples, never across kits. For a fully reproducible run, nf-core/smrnaseq chains these steps (workflow-management/nf-core-pipelines).

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Real high-abundance miRNAs vanish | Position-deduped a non-UMI library | Dedup ONLY with UMIs (umi_tools); non-UMI libraries are not position-deduped |
| Invalid model / distorted calls | Fed RPM/CPM to DESeq2 | Use RAW integer counts; RPM bakes in composition |
| Many spurious "down" miRNAs | One abundant miRNA rose and deflated the rest (closed composition) | Inspect size factors; consider quantile/RUVg/ALDEx2 as a sensitivity check |
| DE looks strong but is noise | Fold-change on a ~5-count miRNA | Report and gate on baseMean |
| Plasma miRNA DE uninterpretable | No trustworthy endogenous normalizer; hemolysis confound | Spike-ins for extraction control + model hemolysis/batch explicitly |
| "miRNA" library is mostly tRF/piRNA | 26-32 nt peak / broad tRF distribution | Route to trf-pirna-profiling (MINTmap/unitas) |

## Pipeline map (hand-offs)

- small-rna-seq/smrna-preprocessing - kit-specific adapter, UMI, and 4N handling
- small-rna-seq/mirge3-analysis - known-miRNA and isomiR quantification
- small-rna-seq/mirdeep2-analysis - novel miRNA discovery and survey.pl cutoff
- small-rna-seq/differential-mirna - compositionally-aware DE and normalizer selection
- small-rna-seq/target-prediction - seed prediction filtered by expression
- small-rna-seq/trf-pirna-profiling - tRF and piRNA profiling

The runnable miRDeep2 discovery-route script is in this skill's examples/ (`smrna_full_pipeline.sh`).

## Related Skills

- small-rna-seq/smrna-preprocessing - Kit-specific adapter, UMI, and 4N handling
- small-rna-seq/mirdeep2-analysis - Novel miRNA discovery
- small-rna-seq/mirge3-analysis - Known-miRNA and isomiR quantification
- small-rna-seq/differential-mirna - Compositionally-aware DE
- small-rna-seq/target-prediction - Seed prediction filtered by expression
- small-rna-seq/trf-pirna-profiling - tRF and piRNA profiling
- differential-expression/deseq2-basics - DESeq2 model, contrasts, shrinkage
- workflow-management/nf-core-pipelines - Run nf-core/smrnaseq as a curated, reproducible pipeline

## References

- Garmire LX, Subramaniam S (2012) Evaluation of normalization methods in mammalian microRNA-Seq data. *RNA* 18:1279-1288. DOI 10.1261/rna.030916.111. (normalization, not the DE model, drives miRNA DE results.)
- Risso D, Ngai J, Speed TP, Dudoit S (2014) Normalization of RNA-seq data using factor analysis of control genes or samples. *Nature Biotechnology* 32:896-902. DOI 10.1038/nbt.2931. (RUVg for miRNA/unwanted variation.)
- Friedländer MR, Mackowiak SD, Li N, Chen W, Rajewsky N (2012) miRDeep2 accurately identifies known and hundreds of novel microRNA genes in seven animal clades. *Nucleic Acids Research* 40:37-52. DOI 10.1093/nar/gkr688.
<!-- END FILE: workflows/smrna-pipeline/SKILL.md -->

## 子目录：workflows/somatic-variant-pipeline

<!-- BEGIN FILE: workflows/somatic-variant-pipeline/SKILL.md -->
---
name: bio-workflows-somatic-variant-pipeline
description: Chains a somatic (tumor-normal) SNV/indel and structural-variant pipeline end to end with GATK Mutect2 (or Strelka2), wiring the somatic-specific machinery - panel-of-normals and gnomAD germline-resource priors, GetPileupSummaries/CalculateContamination, and LearnReadOrientationModel FFPE/oxoG orientation-bias filtering fed into FilterMutectCalls. Use when calling somatic mutations from a tumor-normal pair (or tumor-only with PoN caveats), deciding which artifact filter removes which class of false positive, reasoning about VAF/purity/ploidy and clonal-vs-subclonal detection, adding somatic SV/CNV or TMB/MSI/signatures, or routing variants to AMP/ASCO/CAP tier and oncogenicity interpretation (never germline ACMG).
tool_type: cli
primary_tool: GATK Mutect2
workflow: true
depends_on:
  - read-alignment/bwa-alignment
  - variant-calling/gatk-variant-calling
  - variant-calling/filtering-best-practices
  - variant-calling/structural-variant-calling
  - variant-calling/variant-annotation
  - variant-calling/clinical-interpretation
  - copy-number/cnvkit-analysis
qc_checkpoints:
  - after_alignment: "Tumor + normal mapping rate >95%, tumor coverage adequate for the target VAF"
  - after_contamination: "CalculateContamination estimate low (<~0.02); high contamination inflates false positives"
  - after_filtering: "FilterMutectCalls PASS fraction sane; FFPE/oxoG orientation-bias artifacts removed via --ob-priors"
  - after_interpretation: "Variants tiered by AMP/ASCO/CAP + oncogenicity (never germline ACMG); drivers vs passengers separated"
---

## Version Compatibility

Reference examples tested with: GATK 4.5+, Strelka2 2.9+, Manta 1.6+, Ensembl VEP 111+, bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: this is a WORKFLOW skill - it wires the somatic-specific chain and the DECISIONS between steps. Component mechanism (caller internals, filter thresholds, annotation, CNV) lives in the cross-referenced component skills; interpretation lives in variant-calling/clinical-interpretation and uses the AMP/ASCO/CAP tier system, NOT germline ACMG.

# Somatic Variant Pipeline

**"Call somatic mutations from my tumor-normal pair"** -> Orchestrate somatic SNV/indel calling (Mutect2 or Strelka2) with panel-of-normals + germline-resource priors, contamination and orientation-bias filtering, then somatic SV/CNV, then tier/oncogenicity interpretation.
- CLI: `gatk Mutect2` (+ FilterMutectCalls chain), `configureStrelkaSomaticWorkflow.py` (Strelka2), `configManta.py` (Manta SV), VEP/Funcotator for annotation.

## The governing principle

A somatic callset is not a fact about the tumor; it is a joint property of (tumor, matched normal, caller, filters, reference). Three consequences drive every decision in this pipeline:

1. **There is no universal somatic truth set.** The ICGC-TCGA DREAM Mutation Calling challenge (Alioto 2015 *Nat Commun* 6:10001) gave expert teams the SAME tumor-normal WGS and got widely varying call rates and low SNV concordance - indels and SVs far worse. Somatic reproducibility is intrinsically worse than germline (low VAF, subclonality, purity/ploidy, normal contamination) and there is still no GIAB-grade generalizable somatic reference. Practical corollary: pin the pipeline, benchmark against orthogonal validation for the assay, and prefer multi-caller consensus where feasible - do not treat one caller's VCF as ground truth.
2. **Somatic variants are sub-1.0 VAF and depth/purity-limited.** Unlike a germline 0/0.5/1.0 genotype, a somatic variant sits at a continuous allele fraction set by tumor purity, local copy number, and clonal fraction. Detecting a low-VAF subclonal or low-purity variant is a depth problem (the somatic regime is the one place more coverage genuinely helps). This is why Mutect2 uses a somatic likelihood model, not a diploid genotyper.
3. **Somatic interpretation uses a DIFFERENT framework.** Never apply germline ACMG (PVS1/PM2/PP3) to a tumor variant - it is a category error. Somatic variants are classified by clinical actionability (AMP/ASCO/CAP tiers, Li 2017) and oncogenicity (ClinGen/CGC/VICC, Horak 2022), and the tier is tumor-type-specific. See the interpretation section and variant-calling/clinical-interpretation.

## Pipeline map

```
Tumor BAM + matched Normal BAM   (aligned, dedup'd, BQSR - see read-alignment/*)
    |
    ├── SNV/indel calling
    │     Mutect2 (GATK)    - somatic likelihood, tumor+normal in one command
    │     Strelka2          - faster; pair with Manta candidateSmallIndels
    │
    ├── Somatic-specific filtering  (the four artifact/germline removers, below)
    │     PoN + germline-resource -> Mutect2 call
    │     LearnReadOrientationModel  (FFPE/oxoG)
    │     GetPileupSummaries -> CalculateContamination
    │     FilterMutectCalls (consumes all three) -> PASS somatic VCF
    │
    ├── Structural variants     -> variant-calling/structural-variant-calling (Manta somatic mode)
    ├── Copy number + purity/ploidy -> copy-number/cnvkit-analysis (purity feeds VAF reasoning)
    ├── Annotation (normalize FIRST) -> variant-calling/variant-annotation (VEP/Funcotator)
    │
    └── Interpretation -> variant-calling/clinical-interpretation
          AMP/ASCO/CAP Tier I-IV + oncogenicity (Horak) + TMB/MSI/signatures
```

## The four somatic-specific filters - what each removes

The machinery that separates somatic calling from germline is four independent artifact/germline removers. Knowing WHICH false-positive class each addresses is the core decision - do not treat them as interchangeable boilerplate.

| Filter | Removes | Built from | When it is critical |
|--------|---------|------------|---------------------|
| Panel of Normals (PoN) | Recurrent technical/site artifacts + common germline that reproduce across normals | 40+ unrelated normals from the SAME assay/platform, `CreateSomaticPanelOfNormals` | Always; the ONLY artifact defense in tumor-only mode |
| Germline resource (gnomAD AF-only) | Germline variants, via a population-AF prior in the somatic model | `af-only-gnomad.vcf.gz` (AF field only) | Always; carries the germline burden alone in tumor-only mode |
| Contamination estimate | Cross-individual sample contamination masquerading as low-VAF somatic | `GetPileupSummaries` on common biallelic SNPs -> `CalculateContamination` | Any sample with suspected swap/contamination; low-VAF calls |
| Orientation-bias model | FFPE deamination (C>T/G>A) and oxoG (C>A/G>T) library artifacts, detected as F1R2/F2R1 strand imbalance | `--f1r2-tar-gz` from Mutect2 -> `LearnReadOrientationModel` | FFPE, archival, or oxidatively damaged input; ALWAYS for FFPE |

PoN and germline-resource act at CALL time (priors passed to Mutect2); contamination and orientation-bias are learned separately and injected at FILTER time (`FilterMutectCalls`). The tumor-only trap: without a matched normal, the PoN and germline resource are the ONLY things removing germline and artifacts, so both must be assay-matched and current, and the false-positive rate is materially higher.

## Mutect2 tumor-normal workflow

The end-to-end chained script is in `examples/run_mutect2.sh`; the steps and their decisions:

### Step 1: Build a Panel of Normals (do once per assay)

```bash
# Each normal called in tumor-only mode; --max-mnp-distance 0 is REQUIRED for GenomicsDBImport
for normal in normal1.bam normal2.bam normal3.bam; do
    s=$(basename "$normal" .bam)
    gatk Mutect2 -R reference.fa -I "$normal" --max-mnp-distance 0 -O "${s}.vcf.gz"
done

gatk GenomicsDBImport -R reference.fa --genomicsdb-workspace-path pon_db \
    -V normal1.vcf.gz -V normal2.vcf.gz -V normal3.vcf.gz -L intervals.bed

gatk CreateSomaticPanelOfNormals -R reference.fa -V gendb://pon_db -O pon.vcf.gz
```

A PoN needs 40+ normals from the same platform/chemistry to capture recurrent artifacts; a PoN from a different assay imports the wrong artifact profile and misses real ones. Do NOT build a PoN from tumor-adjacent normals if they may carry tumor-in-normal contamination.

### Step 2: Call somatic variants (tumor + normal in one command)

```bash
gatk Mutect2 -R reference.fa \
    -I tumor.bam -I normal.bam -normal normal_sample_name \
    --germline-resource af-only-gnomad.vcf.gz \
    --panel-of-normals pon.vcf.gz \
    --f1r2-tar-gz f1r2.tar.gz \
    -O unfiltered.vcf.gz
```

`-normal` takes the normal read-group SM name (not the filename). `--f1r2-tar-gz` collects the read-orientation counts needed in Step 3 - omit it and orientation-bias filtering is impossible. Mutect2 also writes `unfiltered.vcf.gz.stats`, which `FilterMutectCalls` reads automatically.

### Step 3: Learn the orientation-bias model

```bash
gatk LearnReadOrientationModel -I f1r2.tar.gz -O read-orientation-model.tar.gz
```

Models the strand-orientation artifacts (oxoG C>A/G>T from oxidative shearing damage; FFPE cytosine-deamination C>T/G>A). These masquerade as low-VAF somatic SNVs; the model lets FilterMutectCalls down-weight them by their F1R2/F2R1 imbalance.

### Step 4: Estimate contamination

```bash
gatk GetPileupSummaries -I tumor.bam \
    -V small_exac_common_3.vcf.gz -L small_exac_common_3.vcf.gz -O tumor_pileups.table
gatk GetPileupSummaries -I normal.bam \
    -V small_exac_common_3.vcf.gz -L small_exac_common_3.vcf.gz -O normal_pileups.table

gatk CalculateContamination -I tumor_pileups.table -matched normal_pileups.table \
    -O contamination.table --tumor-segmentation segments.table
```

`GetPileupSummaries` uses a COMMON biallelic-SNP sites resource (e.g. `small_exac_common_3.vcf.gz`), not the af-only-gnomAD used for the germline prior - it needs sites with a known population AF where reference/alt read counts reveal foreign DNA. `--tumor-segmentation` also captures allelic-copy segments that feed the filter.

### Step 5: Filter, then extract PASS

```bash
gatk FilterMutectCalls -R reference.fa -V unfiltered.vcf.gz \
    --contamination-table contamination.table \
    --tumor-segmentation segments.table \
    --ob-priors read-orientation-model.tar.gz \
    -O filtered.vcf.gz

bcftools view -f PASS filtered.vcf.gz -Oz -o somatic_final.vcf.gz
bcftools index -t somatic_final.vcf.gz
```

`FilterMutectCalls` applies a single joint model (contamination + orientation + segmentation + the built-in weak-evidence/germline/strand filters) and sets a per-variant FILTER. Never hand-tune individual thresholds first - the filter is calibrated to balance them together.

## Tumor-only mode and its caveats

When no matched normal exists (archival FFPE, cell lines, legacy cohorts):

```bash
gatk Mutect2 -R reference.fa -I tumor.bam \
    --germline-resource af-only-gnomad.vcf.gz \
    --panel-of-normals pon.vcf.gz \
    -O tumor_only.vcf.gz
```

Decision framing: with no normal, every germline variant is a candidate somatic call, and only the PoN (artifacts) and gnomAD prior (germline) remove them - so both must be assay-matched and the false-positive rate rises sharply. High-VAF (~50% or ~100%) calls are especially suspect for germline. Tumor-only cannot cleanly separate somatic from germline, which creates a disclosure problem (a germline pathogenic finding surfaced as "somatic") - see the interpretation section. Paired tumor-normal is the defensible design; tumor-only requires explicit germline-subtraction logic and reporting caveats.

## VAF, purity, ploidy, and clonality

Somatic VAF is not a genotype - it is `(clonal_fraction x mutation_copies) / local_total_copies`, scaled by tumor purity. Reasoning consequences:

- **Purity sets sensitivity.** At 30% purity a truly clonal heterozygous mutation in diploid regions sits near ~15% VAF; at 10% purity near ~5%. Low-purity samples need higher depth to call the same variant - the one regime where "sequence deeper" is the correct fix (contrast germline, which saturates ~30-35x).
- **Clonal vs subclonal.** High-VAF (adjusted for purity/copy number) variants are clonal (present in most cells, likely early drivers); low-VAF are subclonal (later, spatially/temporally heterogeneous). Clonality informs driver-vs-passenger and treatment-resistance reasoning.
- **Copy number confounds VAF.** A mutation on an amplified allele reads high; on a deleted/LOH background it reads near 1.0. Interpret VAF only alongside local copy number and purity - run copy-number/cnvkit-analysis (or PURPLE) to get purity/ploidy and correct VAF to cancer-cell fraction before calling something subclonal.

## Strelka2 (faster alternative / consensus arm)

```bash
# Run Manta first; its small-indel candidates sharpen Strelka2 indel calls
configManta.py --normalBam normal.bam --tumorBam tumor.bam \
    --referenceFasta reference.fa --runDir manta_run
manta_run/runWorkflow.py -m local -j 16

configureStrelkaSomaticWorkflow.py \
    --normalBam normal.bam --tumorBam tumor.bam --referenceFasta reference.fa \
    --indelCandidates manta_run/results/variants/candidateSmallIndels.vcf.gz \
    --runDir strelka_run
strelka_run/runWorkflow.py -m local -j 16

bcftools concat \
    strelka_run/results/variants/somatic.snvs.vcf.gz \
    strelka_run/results/variants/somatic.indels.vcf.gz \
    -a -Oz -o strelka_somatic.vcf.gz
```

Strelka2 is faster and strong on indels (Kim 2018 *Nat Methods* 15:591); passing Manta's `candidateSmallIndels.vcf.gz` via `--indelCandidates` is the documented coupling that improves Strelka2 indel recall.

## Multi-caller consensus and reproducibility

Given the Alioto/DREAM discordance, running independent callers and requiring agreement raises precision - the concordant core is the reproducible callset:

```bash
# Intersect PASS calls from callers with uncorrelated error modes (2/3 agreement)
bcftools isec -n+2 -p consensus_dir \
    mutect2_pass.vcf.gz strelka2_pass.vcf.gz muse_pass.vcf.gz
```

Strict all-agree intersection sacrifices too much recall; union admits too many false positives; majority voting (e.g. 2 of 3) balances the two. Normalize every caller's VCF to the same representation first (`bcftools norm -f ref.fa -m-`) or the intersection undercounts because an indel left-aligned differently in two callers will not match. Consensus is a precision tool, not a substitute for orthogonal validation on the assay.

## Somatic SV, CNV, and genomic biomarkers

A complete somatic profile is more than SNVs/indels - hand each off to its component skill:

- **Structural variants:** run Manta in tumor-normal (somatic) mode; it emits `somaticSV.vcf.gz`. For complex rearrangements/fusions use GRIDSS -> GRIPSS -> LINX. See variant-calling/structural-variant-calling.
- **Copy number + purity/ploidy:** CNVkit (targeted/exome), or PURPLE for allele-specific CN with purity/ploidy fit. Purity/ploidy is a required input for correct VAF-to-cancer-cell-fraction. See copy-number/cnvkit-analysis.
- **Genomic biomarkers (brief):** Tumor Mutational Burden (TMB) = eligible somatic mutations per Mb of covered target (filter out germline and low-VAF artifacts first - inflated TMB is usually residual germline in tumor-only). Microsatellite instability (MSI) is called from indel patterns at microsatellite loci (e.g. MSIsensor). Mutational signatures (SBS/ID/CNV, COSMIC catalogue) attribute the mutation spectrum to processes (APOBEC, UV, MMR-deficiency, platinum) and cross-check artifacts - a dominant C>A/G>T signature can be residual oxoG, not biology. Verify current tool choices and thresholds against the latest docs.

## Annotation (normalize FIRST)

```bash
bcftools norm -f reference.fa -m- somatic_final.vcf.gz -Oz -o somatic_norm.vcf.gz  # left-align + split multiallelics

gatk Funcotator -R reference.fa -V somatic_norm.vcf.gz -O annotated.vcf.gz \
    --output-file-format VCF --data-sources-path funcotator_dataSources.v1.7 --ref-version hg38

vep -i somatic_norm.vcf.gz -o annotated_vep.vcf --vcf --cache --offline \
    --assembly GRCh38 --everything \
    --custom cosmic.vcf.gz,COSMIC,vcf,exact,0,CNT --fork 4
```

Normalize BEFORE annotating (annotate-then-normalize is an order error): un-normalized records attach annotations to a non-canonical representation and fail to match COSMIC/gnomAD. Full annotation mechanics (transcript choice, MANE, HGVS 3'-shift) live in variant-calling/variant-annotation.

## Interpretation: somatic tiers, NOT germline ACMG

This is the critical decision of the whole pipeline and the most common category error. Route the annotated somatic VCF to variant-calling/clinical-interpretation, which applies TWO orthogonal cancer frameworks:

**AMP/ASCO/CAP four-tier clinical actionability (Li 2017 *J Mol Diagn* 19:4-23):**

| Tier | Meaning | Example |
|------|---------|---------|
| I | Strong clinical significance - FDA-approved therapy or in professional guidelines for THIS tumor type | BRAF V600E in melanoma |
| II | Potential significance - therapy in a different tumor type, or clinical-trial/multi-study evidence | same variant in a non-approved tumor type |
| III | Unknown clinical significance (the somatic "VUS") | rare novel missense, no actionability |
| IV | Benign / likely benign - high population frequency, no oncogenic role | common polymorphism |

Tier is tumor-type-specific - the SAME variant can be Tier I in one cancer and Tier II/III in another (no germline-ACMG analog).

**Oncogenicity (Horak 2022 *Genet Med* 24:986):** a SEPARATE points-based ClinGen/CGC/VICC axis (Oncogenic / Likely Oncogenic / VUS / Likely Benign / Benign) from hotspot recurrence, functional data, and tumor-type frequency. Oncogenicity (is it a driver) and actionability (is there a drug) are complementary: an oncogenic driver may still be Tier III if no therapy exists.

- **Driver vs passenger:** a tumor carries thousands of somatic mutations; only a few drive it. Hotspot recurrence (COSMIC, Tate 2019), presence in known oncogenes/tumor suppressors, functional evidence, and clonality (clonal drivers vs subclonal passengers) distinguish them.
- **Knowledgebase evidence levels:** OncoKB therapeutic levels 1-4 + R1/R2 (Chakravarty 2017); CIViC evidence items graded A (validated) to E (inferential), read the item not just the letter (Griffith 2017).
- **Tumor-only germline leak:** in tumor-only assays a high-VAF variant may be germline - reporting it as somatic (or applying a somatic tier to a germline pathogenic finding requiring genetic counseling) is a dual danger. Disclose and filter explicitly.

## Quality metrics

```bash
bcftools query -f '%FILTER\n' filtered.vcf.gz | sort | uniq -c   # counts by filter status

# Substitution spectrum: excess C>A/G>T flags residual oxoG; excess C>T/G>A flags FFPE deamination
bcftools query -f '%REF>%ALT\n' somatic_final.vcf.gz | sort | uniq -c

# VAF distribution (a spike near 0.5/1.0 in tumor-only suggests residual germline).
# -s takes the read-group SM name, NOT the filename -- read it from the BAM header, as Step 2 does.
TUMOR_SM=$(samtools view -H tumor.bam | awk '/^@RG/{for(i=1;i<=NF;i++) if($i ~ /^SM:/){sub(/^SM:/,"",$i); print $i; exit}}')
# -s restricts to the tumor sample: a bare [%AF] iterates BOTH samples and concatenates
# them with no separator (0.25 + 0.01 -> "0.250.01"), which awk then silently truncates to 0.25.
bcftools query -s "$TUMOR_SM" -f '[%AF]\n' somatic_final.vcf.gz | awk '{print int($1*100)/100}' | sort -n | uniq -c
```

Do NOT judge somatic SNVs by a fixed germline-like Ti/Tv (~2-3); the somatic spectrum is signature-dependent, and a collapse toward transversion excess signals artifact contamination, not a target value.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Flood of germline variants in output | Missing/wrong germline-resource, or tumor-only without a good PoN | Pass `--germline-resource af-only-gnomad.vcf.gz`; use an assay-matched 40+ normal PoN |
| Excess C>A/G>T (or C>T/G>A) low-VAF calls | oxoG (or FFPE) artifacts, orientation-bias filter not applied | Emit `--f1r2-tar-gz`, run `LearnReadOrientationModel`, pass `--ob-priors` to FilterMutectCalls |
| `FilterMutectCalls` errors on missing stats | `unfiltered.vcf.gz.stats` not alongside the VCF | Keep the `.stats` Mutect2 wrote next to the VCF, or pass `--stats` |
| GetPileupSummaries gives nonsense contamination | Used af-only-gnomAD instead of a common biallelic-SNP resource | Use `small_exac_common_3.vcf.gz` (common SNP sites with AF) |
| Consensus intersection drops real shared calls | VCFs not normalized before `bcftools isec` | `bcftools norm -f ref.fa -m-` every caller's VCF first |
| Low-purity tumor: expected drivers missing | VAF below detection at that purity/depth | Get purity from copy-number; increase depth; correct VAF to cancer-cell fraction |
| Applied ACMG PVS1/PM2 to a tumor variant | Germline framework used for somatic | Use AMP/ASCO/CAP tiers + oncogenicity via variant-calling/clinical-interpretation |

## Related Skills

- variant-calling/gatk-variant-calling - Mutect2 mechanism and germline HaplotypeCaller context
- variant-calling/filtering-best-practices - FilterMutectCalls internals, normalization, hard filters
- variant-calling/variant-annotation - VEP/Funcotator/SnpEff, transcript choice, HGVS, COSMIC
- variant-calling/clinical-interpretation - AMP/ASCO/CAP tiers and oncogenicity (somatic interpretation)
- variant-calling/structural-variant-calling - Somatic SV detection (Manta somatic mode, GRIDSS/LINX)
- copy-number/cnvkit-analysis - Somatic CNV, purity/ploidy for VAF-to-cancer-cell-fraction
- read-alignment/bwa-alignment - Upstream alignment/dedup/BQSR of tumor and normal BAMs

## References

- Li MM, Datto M, Duncavage EJ, et al. Standards and guidelines for the interpretation and reporting of sequence variants in cancer: a joint consensus recommendation of AMP, ASCO, and CAP. *Journal of Molecular Diagnostics*. 2017;19(1):4-23. doi:10.1016/j.jmoldx.2016.10.002 (four-tier actionability).
- Horak P, Griffith M, Danos AM, et al. Standards for the classification of pathogenicity of somatic variants in cancer (oncogenicity): joint recommendations of ClinGen, CGC, and VICC. *Genetics in Medicine*. 2022;24(5):986-998. doi:10.1016/j.gim.2022.01.001.
- Benjamin D, Sato T, Cibulskis K, Getz G, Stewart C, Lichtenstein L. Calling Somatic SNVs and Indels with Mutect2. *bioRxiv* 861054 (2019). doi:10.1101/861054 (PREPRINT - the Mutect2 somatic workflow reference; never formally journal-published).
- Alioto TS, Buchhalter I, Derdak S, et al. A comprehensive assessment of somatic mutation detection in cancer using whole-genome sequencing. *Nature Communications*. 2015;6:10001. doi:10.1038/ncomms10001 (ICGC-TCGA DREAM; somatic reproducibility).
- Kim S, Scheffler K, Halpern AL, et al. Strelka2: fast and accurate calling of germline and somatic variants. *Nature Methods*. 2018;15(8):591-594. doi:10.1038/s41592-018-0051-x.
- Chen X, Schulz-Trieglaff O, Shaw R, et al. Manta: rapid detection of structural variants and indels for germline and cancer sequencing applications. *Bioinformatics*. 2016;32(8):1220-1222. doi:10.1093/bioinformatics/btv710.
- Karczewski KJ, Francioli LC, Tiao G, et al. The mutational constraint spectrum quantified from variation in 141,456 humans. *Nature*. 2020;581(7809):434-443. doi:10.1038/s41586-020-2308-7 (gnomAD; germline-resource / AF prior).
- Chakravarty D, Gao J, Phillips SM, et al. OncoKB: a precision oncology knowledge base. *JCO Precision Oncology*. 2017;2017:PO.17.00011. doi:10.1200/PO.17.00011 (therapeutic levels 1-4, R1/R2).
- Griffith M, Spies NC, Krysiak K, et al. CIViC is a community knowledgebase for expert crowdsourcing the clinical interpretation of variants in cancer. *Nature Genetics*. 2017;49:170-174. doi:10.1038/ng.3774 (evidence levels A-E).
- Tate JG, Bamford S, Jubb HC, et al. COSMIC: the Catalogue Of Somatic Mutations In Cancer. *Nucleic Acids Research*. 2019;47(D1):D941-D947. doi:10.1093/nar/gky1015 (hotspot recurrence, signatures).
<!-- END FILE: workflows/somatic-variant-pipeline/SKILL.md -->

## 子目录：workflows/spatial-pipeline

<!-- BEGIN FILE: workflows/spatial-pipeline/SKILL.md -->
---
name: bio-workflows-spatial-pipeline
description: Orchestrates the end-to-end spatial transcriptomics pipeline from Space Ranger / vendor output to spatial domains and statistics, branching FIRST on platform class (imaging in-situ Xenium/MERFISH/CosMx vs sequencing/capture Visium/Visium HD/Slide-seq). Use when deciding segmentation-vs-deconvolution and the QC floors from the platform class, committing the coordinate/image-registration frame and panel identity, deconvolving multi-cell spots against an annotated scRNA reference (never relabeling spot clusters as cell types), building the spatial neighbor graph on PHYSICAL not expression space, gating spatially-variable genes on FDR, or using a real domain method (BANKSY/BayesSpace/STAGATE) rather than clustering the spatial graph alone. Hands off deconvolution and cell-cell communication to the component skills; not a re-teach of any single step.
tool_type: python
primary_tool: Squidpy
goal_approach_exempt: true
workflow: true
depends_on:
  - spatial-transcriptomics/spatial-data-io
  - spatial-transcriptomics/spatial-preprocessing
  - spatial-transcriptomics/image-analysis
  - spatial-transcriptomics/spatial-deconvolution
  - spatial-transcriptomics/spatial-neighbors
  - spatial-transcriptomics/spatial-statistics
  - spatial-transcriptomics/spatial-domains
  - spatial-transcriptomics/spatial-visualization
qc_checkpoints:
  - platform_fork: "Imaging vs sequencing decided; QC floors and deconvolution-vs-segmentation set accordingly"
  - after_loading: "Spots/cells detected, image aligned"
  - after_qc: "Low-quality spots filtered, genes detected"
  - after_clustering: "Spatial domains correspond to tissue regions"
---

## Version Compatibility

Reference examples tested with: Space Ranger 4.1+ (Visium HD; nucleus/cell segmentation in the count pipeline since v4.0), scanpy 1.10+, squidpy 1.3+, spatialdata-io current (imaging platforms), matplotlib 3.8+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: `squidpy.read` provides `visium`/`vizgen`/`nanostring` only — there is NO `sq.read.xenium`; imaging platforms load via `spatialdata_io` (returns a SpatialData object preserving the molecule table). Visium HD default bin is 8 µm. Confirm in-tool before quoting.

# Spatial Transcriptomics Pipeline

**"Analyze my spatial transcriptomics data end-to-end"** -> Orchestrate data loading (squidpy/scanpy), QC, normalization, spatial neighbor analysis, spatial statistics, spatial domain detection, and tissue visualization. Composition estimation (deconvolution, spatial-deconvolution) and cell-cell communication (spatial-communication) are deliberately separate steps -- this pipeline hands off to those skills rather than inlining them.

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step.

## Made-once commitments

| Commitment | Consequence inherited downstream |
|------------|----------------------------------|
| Platform class (imaging vs sequencing) | EVERY downstream choice: segment-vs-deconvolve, discovery-vs-classification, QC floors, panel-bounded-vs-whole-transcriptome |
| Coordinate system + image-registration frame | All spatial neighbors/overlays/niches; a wrong registration frame silently misplaces every spot relative to histology |
| Panel identity (targeted vs whole-transcriptome; FFPE probe vs FF poly-A) | What "gene absent" means: on a targeted panel absence = "not in panel", not "not expressed"; RIN (FF) vs DV200 (FFPE) QC metric switch |
| Spot/bin geometry (Visium 55 µm >> cell; Visium HD 2/8 µm; Xenium single-molecule) | Whether to DECONVOLVE (spot >> cell), SEGMENT/bin-up (spot << cell), or neither |
| Segmentation policy (imaging: Baysor / Cellpose / vendor Xenium; Visium HD bin-to-cell: Space Ranger v4+) | Every cell x gene value; segmentation is the DOMINANT imaging error source and over-expansion manufactures cross-type DE |

## The platform-class fork (decide first)

This pipeline branches on platform class before any step. Sequencing/capture data (Visium, Visium HD, Slide-seq, Stereo-seq) are spot/bin MIXTURES of cells: QC on spot counts, normalize knowing that library size partly carries cellularity, then DECONVOLVE composition (spatial-deconvolution) rather than read a spot as one cell. Imaging/in-situ data (Xenium, MERFISH, CosMx) are single molecules: SEGMENT cells first (image-analysis), apply low-count-aware QC floors (an scRNA `min_counts=500` deletes nearly every real imaging cell, whose vector is tens-to-low-hundreds of transcripts), drop on negative-control probe rate, and SKIP deconvolution. The Squidpy+Scanpy path below is written for Visium; the imaging branch is flagged at each step.

## Workflow Overview

```
Spatial data (Space Ranger output)
    |
    v
[1. Load Data] ---------> Read Visium/Xenium
    |
    v
[2. QC & Preprocessing] -> Filter, normalize
    |
    v
[3. Clustering] --------> Standard scRNA-seq clustering
    |
    v
[4. Spatial Analysis] --> Neighbors, statistics
    |
    v
[5. Domain Detection] --> Spatial domains
    |
    v
[6. Visualization] -----> Spatial plots
    |
    v
Annotated spatial data
```

## Primary Path: Squidpy + Scanpy

### Step 1: Load Data

```python
import scanpy as sc
import squidpy as sq
import numpy as np
import matplotlib.pyplot as plt

# Load Visium data (Space Ranger output). squidpy.read provides only visium,
# vizgen, and nanostring -- there is NO sq.read.xenium.
adata = sq.read.visium('spaceranger_output/')

# For Xenium and other imaging platforms use spatialdata_io, which returns a
# SpatialData object preserving the per-transcript molecule table (the cell
# matrix is one table inside it). See spatial-data-io.
# import spatialdata_io as sdio
# sdata = sdio.xenium('xenium_output/')
# adata = sdata.tables['table']  # segmentation-derived cell matrix

print(f'Loaded: {adata.n_obs} spots/cells, {adata.n_vars} genes')
```

### Step 2: Quality Control

```python
# QC metrics. Mito genes are present on Visium but usually OFF-PANEL for imaging
# platforms, so guard the mito calculation rather than assuming MT- genes exist.
has_mito = adata.var_names.str.startswith('MT-').any()
if has_mito:
    adata.var['mt'] = adata.var_names.str.startswith('MT-')
    sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
else:
    sc.pp.calculate_qc_metrics(adata, inplace=True)

# Always inspect QC SPATIALLY (a gradient across the section is a technical
# artifact, not biology); violins alone hide it.
sc.pl.spatial(adata, color='total_counts', show=False)
plt.savefig('qc_spatial.pdf')

# Filter. These floors are VISIUM defaults (spot = 1-10-cell mixture) and are
# tissue-dependent. For IMAGING data use low-count-aware floors (~10 transcripts
# per cell, NOT 500) or aggressive filtering deletes nearly every real cell and
# preferentially removes small cells (lymphocytes), biasing composition.
sc.pp.filter_cells(adata, min_counts=500)
sc.pp.filter_genes(adata, min_cells=10)
if has_mito:
    adata = adata[adata.obs.pct_counts_mt < 25, :]

print(f'After QC: {adata.n_obs} spots/cells')
```

### Step 3: Normalization and Clustering

```python
# Store raw counts
adata.layers['counts'] = adata.X.copy()

# Normalize. In spatial data library size partly CARRIES BIOLOGY (Visium total
# counts confound with cells-per-spot and cellularity; imaging total counts with
# cell size), so total-count normalization is a Visium starting point, not a
# universal default -- for imaging consider cell volume/area normalization and
# see spatial-preprocessing before dividing library size out.
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# HVGs
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# PCA and clustering
adata.raw = adata
adata = adata[:, adata.var.highly_variable]
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, n_comps=50)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5, flavor='igraph', n_iterations=2, directed=False)

# Visualize clusters in space. On Visium these spot clusters are REGIONS/niches,
# NOT cell types -- a spot is a 1-10-cell mixture, so recovering cell-type
# composition needs deconvolution (spatial-deconvolution), not clustering.
sc.pl.spatial(adata, color='leiden', spot_size=1.5)
plt.savefig('clusters_spatial.pdf')
```

### Step 4: Spatial Analysis

```python
# Build spatial neighbors graph. Visium is a hex lattice -> coord_type='grid'
# (n_neighs=6); 'generic' kNN is for imaging point clouds. See spatial-neighbors.
sq.gr.spatial_neighbors(adata, coord_type='grid', n_neighs=6)

# Neighborhood enrichment. The Squidpy permutation null only tests "more adjacent
# than complete spatial randomness" -- two abundant types sharing a compartment
# pass trivially. A positive z is NOT a specific A-B interaction; demand a
# conditional/toroidal null before claiming affinity. See spatial-statistics.
sq.gr.nhood_enrichment(adata, cluster_key='leiden')
sq.pl.nhood_enrichment(adata, cluster_key='leiden')
plt.savefig('nhood_enrichment.pdf')

# Co-occurrence analysis
sq.gr.co_occurrence(adata, cluster_key='leiden')
sq.pl.co_occurrence(adata, cluster_key='leiden')
plt.savefig('co_occurrence.pdf')

# Spatially variable genes. Gate on FDR, not raw I; and a top-Moran gene is
# usually a marker of a spatially-clustered cell TYPE (composition), not a gene
# regulated WITHIN a type -- intersect with non-HVG to find the latter. See
# spatial-statistics.
sq.gr.spatial_autocorr(adata, mode='moran', n_perms=100, n_jobs=4)
moran = adata.uns['moranI']
svg = moran[moran['pval_norm_fdr_bh'] < 0.05].sort_values('I', ascending=False)
print('Spatially autocorrelated genes (FDR<0.05):', svg.head(10).index.tolist())
```

### Step 5: Domain Detection

```python
# Spatial domain detection. Clustering the spatial graph topology ALONE (below)
# is a quick proxy, NOT a real domain method -- it ignores expression and carries
# none of the over-smoothing / spatial-weight-knob / k-as-biological-choice
# framing. For real domains use BANKSY (lambda ~0.8), BayesSpace, or STAGATE and
# tune the spatial weight. See spatial-domains.
sq.gr.spatial_neighbors(adata, coord_type='grid', n_neighs=6)
sc.tl.leiden(adata, resolution=0.3, key_added='spatial_domains',
             adjacency=adata.obsp['spatial_connectivities'],
             flavor='igraph', n_iterations=2, directed=False)

# Visualize domains
sc.pl.spatial(adata, color='spatial_domains', spot_size=1.5)
plt.savefig('spatial_domains.pdf')

# Compare transcriptomic vs spatial clusters
sc.pl.spatial(adata, color=['leiden', 'spatial_domains'], ncols=2)
plt.savefig('clusters_comparison.pdf')
```

### Step 6: Visualization

```python
# Gene expression in space
genes = ['EPCAM', 'VIM', 'PTPRC', 'COL1A1']
sc.pl.spatial(adata, color=genes, ncols=2, spot_size=1.5, cmap='viridis')
plt.savefig('marker_genes_spatial.pdf')

# Cluster markers in space. On Visium these are markers of spot REGIONS (mixtures),
# not of pure cell types; for cell-type-level signal deconvolve first.
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
sc.pl.rank_genes_groups_dotplot(adata, n_genes=5)
plt.savefig('cluster_markers.pdf')

# Save
adata.write('spatial_analyzed.h5ad')
```

## Complete Workflow Script

```python
import scanpy as sc
import squidpy as sq
import matplotlib.pyplot as plt
import os

# Configuration
data_dir = 'spaceranger_output'
output_dir = 'spatial_results'
os.makedirs(output_dir, exist_ok=True)
os.makedirs(f'{output_dir}/plots', exist_ok=True)

# Load
print('Loading data...')
adata = sq.read.visium(data_dir)
print(f'Loaded: {adata.n_obs} spots, {adata.n_vars} genes')

# QC (Visium defaults; for imaging use low-count-aware floors and skip mito)
print('QC filtering...')
has_mito = adata.var_names.str.startswith('MT-').any()
if has_mito:
    adata.var['mt'] = adata.var_names.str.startswith('MT-')
    sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
else:
    sc.pp.calculate_qc_metrics(adata, inplace=True)
sc.pp.filter_cells(adata, min_counts=500)
sc.pp.filter_genes(adata, min_cells=10)
if has_mito:
    adata = adata[adata.obs.pct_counts_mt < 25, :]
print(f'After QC: {adata.n_obs} spots')

# Normalize and cluster
print('Processing...')
adata.layers['counts'] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
adata.raw = adata
adata = adata[:, adata.var.highly_variable]
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, n_comps=50)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.leiden(adata, resolution=0.5, flavor='igraph', n_iterations=2, directed=False)

# Spatial analysis (Visium hex -> coord_type='grid'; nhood z and top-Moran genes
# need the caveats from Step 4 before interpretation)
print('Spatial analysis...')
sq.gr.spatial_neighbors(adata, coord_type='grid', n_neighs=6)
sq.gr.nhood_enrichment(adata, cluster_key='leiden')
sq.gr.spatial_autocorr(adata, mode='moran', n_perms=100)

# Plots
print('Creating plots...')
sc.pl.spatial(adata, color='leiden', spot_size=1.5, save='_clusters.pdf')
sq.pl.nhood_enrichment(adata, cluster_key='leiden', save='_nhood.pdf')

# Save
adata.write(f'{output_dir}/spatial_analyzed.h5ad')
print(f'Results saved to {output_dir}/')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Spot clusters mislabeled as cell types | Skipped deconvolution on multi-cell Visium spots | Deconvolve against an annotated scRNA reference; clusters = niches (spatial-deconvolution) |
| Nearly all imaging cells filtered; small cells lost | Applied scRNA QC floor (min_counts=500) to single-molecule data | Low-count-aware floors (~10 transcripts) + negative-control-probe gating |
| Spurious cross-type DE (neuronal markers in astrocytes) | Over-aggressive segmentation expansion | Molecule-aware (Baysor) or uniform re-segmentation; segmentation is critical |
| "Spatial" neighbors are wrong | Built the neighbor graph on the expression embedding | Build on PHYSICAL coordinates (grid for Visium, kNN for imaging) |
| Overlays/niches misplaced | Image-vs-expression coordinate/registration mismatch | Verify fiducial registration; keep tissue and matrix coordinates reconciled |
| "Novel cell state" on a targeted panel | Treated a fixed panel as discovery | Classification/label-transfer only; absence = not-in-panel |
| Top-Moran gene over-interpreted as regulation | Gated on raw Moran's I / read a composition marker as within-type | Gate SVGs on FDR; a top-Moran gene usually marks a spatially-clustered cell TYPE |

## References

- Palla G, Spitzer H, Klein M, et al (2022) Squidpy: a scalable framework for spatial omics analysis. *Nature Methods* 19:171-178. DOI 10.1038/s41592-021-01358-2. (spatial neighbor graph / neighborhood enrichment / autocorrelation.)
- Kleshchevnikov V, Shmatko A, Dann E, et al (2022) Cell2location maps fine-grained cell types in spatial transcriptomics. *Nature Biotechnology* 40:661-671. DOI 10.1038/s41587-021-01139-4. (deconvolution: spot != cell.)
- Cable DM, Murray E, Zou LS, et al (2022) Robust decomposition of cell type mixtures in spatial transcriptomics (RCTD). *Nature Biotechnology* 40:517-526. DOI 10.1038/s41587-021-00830-w.
- Petukhov V, Xu RJ, Soldatov RA, et al (2022) Cell segmentation in imaging-based spatial transcriptomics with Baysor. *Nature Biotechnology* 40:345-354. DOI 10.1038/s41587-021-01044-w. (segmentation as the dominant imaging error source.)

## Related Skills

- spatial-transcriptomics/spatial-data-io - Loading formats (Visium/imaging; SpatialData)
- spatial-transcriptomics/spatial-preprocessing - QC floors and normalization by platform
- spatial-transcriptomics/image-analysis - Cell segmentation for imaging platforms
- spatial-transcriptomics/spatial-neighbors - Physical-space neighbor graphs
- spatial-transcriptomics/spatial-statistics - Moran's I, co-occurrence, neighborhood enrichment nulls
- spatial-transcriptomics/spatial-domains - BANKSY/BayesSpace/STAGATE domain methods
- spatial-transcriptomics/spatial-deconvolution - Cell-type composition of multi-cell spots
- spatial-transcriptomics/spatial-communication - Cell-cell communication / ligand-receptor (separate hand-off)
- spatial-transcriptomics/spatial-visualization - Spatial overlays and figures
- workflows/scrnaseq-pipeline - Upstream: provides the annotated scRNA reference for deconvolution
<!-- END FILE: workflows/spatial-pipeline/SKILL.md -->

## 子目录：workflows/splicing-pipeline

<!-- BEGIN FILE: workflows/splicing-pipeline/SKILL.md -->
---
name: bio-workflows-splicing-pipeline
description: Orchestrates the end-to-end bulk short-read alternative-splicing pipeline from FASTQ to differential splicing, chaining fastp QC, cohort-consistent STAR 2-pass alignment (one shared junction DB), junction QC, event-level differential splicing (rMATS-turbo + leafcutter, optional MAJIQ V3), parallel isoform-level DTU (Salmon -> tximport dtuScaledTPM -> DRIMSeq/DEXSeq -> stageR), and sashimi visualization. Use when committing the annotation GTF and a shared 2-pass junction database for the whole cohort, keeping the analysis at splice-aware resolution (never collapsing to gene), choosing event-level vs isoform-level DTU and reconciling them, applying the stageR two-stage gene->transcript FDR, or off-ramping to splice-variant / outlier / long-read / single-cell splicing. Hands mechanism to the alternative-splicing component skills; not a re-teach of any single step.
tool_type: mixed
primary_tool: rMATS-turbo
workflow: true
depends_on:
  - read-qc/fastp-workflow
  - read-alignment/star-alignment
  - alternative-splicing/splicing-qc
  - alternative-splicing/splicing-quantification
  - alternative-splicing/differential-splicing
  - rna-quantification/alignment-free-quant
  - rna-quantification/tximport-workflow
  - alternative-splicing/isoform-switching
  - alternative-splicing/sashimi-plots
qc_checkpoints:
  - after_qc: "Q30 >80%, adapter <5%; reads NOT over-trimmed (short reads lose junction-spanning power)"
  - after_align: "Uniquely-mapped >80%; junction-saturation curves plateau (else sequence deeper)"
  - after_diff: "|deltaPSI| >0.1 (lenient) / >0.2 (stringent), FDR <0.05, >=10 junction reads supporting the event"
  - after_dtu: "stageR gene-level screen passed BEFORE trusting any transcript-level q-value"
---

## Version Compatibility

Reference examples tested with: STAR 2.7.11+, fastp 0.23+, rMATS-turbo 4.3+, leafcutter 0.2.9+, Salmon 1.10+, tximport 1.30+, DRIMSeq 1.30+, DEXSeq 1.48+, stageR 1.24+, IsoformSwitchAnalyzeR 2.2+, RSeQC 5.0+, ggsashimi 1.1+ (numpy 1.26+, pandas 2.2+)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: rMATS-turbo `--readLength` must match the trimmed read length (add `--variable-read-length` if trimming produced a range); IsoformSwitchAnalyzeR's `importRdata` argument is genuinely spelled `isoformExonAnnoation` (a package typo, not an error here). Confirm in-tool before quoting.

# Alternative Splicing Analysis Pipeline

**"Find differential alternative splicing between my two conditions"** -> Chain QC/trim, cohort-consistent 2-pass alignment, junction QC, event-level and (parallel) isoform-level differential testing, and sashimi visualization.
- CLI + R: fastp -> STAR 2-pass (shared SJ DB) -> junction QC -> rMATS-turbo + leafcutter -> [Salmon -> tximport dtuScaledTPM -> DRIMSeq/DEXSeq -> stageR] -> ggsashimi

This is a workflow skill: it owns the chaining decisions and hand-offs, not the internals of any one step. Every step below cross-references the component skill that teaches its mechanism.

## The governing principle

Splicing quantification is comparative by construction, so the trustworthy result is decided at four seams, not inside any one caller.

1. **Splice-aware alignment must be cohort-consistent — one shared junction database for the whole experiment.** STAR 2-pass where pass 2 uses the COMBINED `SJ.out.tab` from all samples is a made-once commitment, the splicing analogue of a shared reference. Junctions discovered per-sample and applied unevenly make PSI values non-comparable across samples, so a "differential" event is really a coverage artifact. Never run 2-pass independently per sample for a cohort.
2. **The analysis lives at splice-aware resolution and does NOT collapse to gene.** Feeding the standard gene-level tximport import (`txOut=FALSE`) averages the isoform-switch signal away. The DTU branch uses the OPPOSITE import from workflows/rnaseq-to-de: `countsFromAbundance="dtuScaledTPM"` + `txOut=TRUE`.
3. **Event-level and isoform-level tests answer different questions and are reconciled, not merged.** rMATS/leafcutter test exon-inclusion (ΔPSI); DTU tests within-gene isoform-proportion shifts. A gene can be significant for one and not the other; treating their p-values as interchangeable is a category error.
4. **Transcript-level DTU FDR is only honest through the stageR two-stage test.** Report per-transcript q-values only after a gene-level screen has passed; raw transcript-level FDR is inflated. stageR is the seam that converts gene-screened-then-transcript-confirmed tests into calibrated FDR.

## Pipeline map

```
FASTQ (paired)
  | [1] QC & trim ---------------> fastp                (read-qc/fastp-workflow)
  v
  | [2] STAR 2-pass -------------> pass1 (all) -> COMBINED SJ.out.tab -> pass2 (all)  (read-alignment/star-alignment)
  v     ^-- commitment: annotation GTF + ONE shared junction DB + readLength
  | [3] Junction QC -------------> saturation plateau, entropy   (alternative-splicing/splicing-qc)
  v
  +---------------------------+-----------------------------------+
  | EVENT level               | ISOFORM level (parallel, optional)|
  v                           v
[4a] rMATS-turbo + leafcutter [4b] Salmon -> tximport dtuScaledTPM(txOut=TRUE)
     (alternative-splicing/       -> DRIMSeq/DEXSeq -> stageR
      differential-splicing)      (alternative-splicing/isoform-switching)
  |   ^-- reconcile, don't merge      ^-- gene screen BEFORE transcript q
  v
[5] Sashimi on top events -----> ggsashimi   (alternative-splicing/sashimi-plots)
```

## Made-once commitments

Decided before the first alignment; every downstream PSI/DTU value inherits them.

| Commitment | Choice | Consequence inherited downstream |
|------------|--------|----------------------------------|
| Annotation GTF | ONE GTF used by rMATS, leafcutter, and IsoformSwitchAnalyzeR | Different GTFs make their events irreconcilable; fixes the event universe |
| 2-pass junction DB | Combined `SJ.out.tab` from ALL samples fed into pass 2 | Per-sample junctions -> non-comparable PSI, false "differential" events from coverage |
| Measurement level | Splice-aware (event PSI and/or transcript DTU); NEVER gene collapse | Gene-level tximport (`txOut=FALSE`) averages away the switch signal |
| `--readLength` | Matches the trimmed read length (or `--variable-read-length`) | A wrong value miscomputes inclusion-junction lengths and biases PSI |

## The canonical order and why

1. **QC/trim** — but do NOT over-trim; short reads lose junction-spanning power.
2. **STAR pass 1 (all samples)** -> collect every `SJ.out.tab`.
3. **Build ONE combined junction DB** from the concatenated `SJ.out.tab` (order-trap: skipping this / per-sample DBs makes PSI incomparable).
4. **STAR pass 2 (all samples, same combined DB)** -> coordinate-sorted BAMs.
5. **Junction QC** — saturation curves must plateau (else deeper sequencing), entropy sane.
6. **Event-level differential splicing** — rMATS-turbo plus leafcutter for concordance.
7. **(Parallel) isoform-level DTU** — Salmon transcript quant -> tximport `dtuScaledTPM`+`txOut=TRUE` -> DRIMSeq/DEXSeq -> **stageR** (order-trap: reporting transcript q-values without the stageR gene screen inflates FDR).
8. **Sashimi** on the top reconciled events.

Order-traps that silently produce wrong results: per-sample (not cohort) 2-pass junctions; collapsing to gene before splicing analysis; transcript FDR without stageR; mixing ΔPSI significance with DTU proportion significance as if interchangeable.

## Choosing event-level vs isoform-level (and the caller)

Pipeline-level selection only; mechanism lives in the component skills.

| Fork | Lean toward | Hand off to |
|------|-------------|-------------|
| Event-level vs isoform-level | rMATS/leafcutter (which exon?) vs IsoformSwitchAnalyzeR/DRIMSeq+DEXSeq (which isoform, + NMD/ORF/domain consequences) | alternative-splicing/differential-splicing, alternative-splicing/isoform-switching |
| rMATS vs leafcutter vs MAJIQ | rMATS (known event types, replicate-based) + leafcutter (annotation-free intron clusters) for concordance; MAJIQ V3 HET for complex/heterogeneous cohorts | alternative-splicing/differential-splicing |
| DTU import scale | Salmon -> tximport `dtuScaledTPM` + `txOut=TRUE` (the ONLY correct DTU import) | rna-quantification/tximport-workflow |
| Transcript FDR | stageR two-stage: gene-level screen then transcript confirmation | alternative-splicing/isoform-switching |

## Primary path: STAR 2-pass + rMATS-turbo (+ leafcutter)

**Goal:** produce cohort-comparable PSI and a filtered differential-event table.

**Approach:** align all samples through one shared junction DB, QC junction saturation, then run rMATS-turbo (and leafcutter for concordance). Full runnable script: `examples/splicing_pipeline.sh`.

```bash
# Pass 1 (all samples) -> collect junctions
STAR --runThreadN 8 --genomeDir star_index/ --readFilesIn ${s}_R1.fq.gz ${s}_R2.fq.gz \
    --readFilesCommand zcat --outSAMtype BAM Unsorted --outFileNamePrefix ${s}_pass1_
cat *_pass1_SJ.out.tab > combined_SJ.out.tab          # ONE shared DB for the whole cohort
# Pass 2 (all samples, same combined DB) -> comparable coordinates
STAR --runThreadN 8 --genomeDir star_index/ --readFilesIn ${s}_R1.fq.gz ${s}_R2.fq.gz \
    --readFilesCommand zcat --sjdbFileChrStartEnd combined_SJ.out.tab \
    --outSAMtype BAM SortedByCoordinate --outFileNamePrefix ${s}_

# Differential splicing. --readLength MUST match the trimmed reads, and --variable-read-length is
# required because the fastp step above trims to a RANGE, not a single length; without it rMATS
# miscomputes inclusion-junction lengths and biases PSI.
rmats.py --b1 cond1_bams.txt --b2 cond2_bams.txt --gtf annotation.gtf \
    -t paired --readLength 150 --variable-read-length --nthread 8 --od rmats_output --tmp rmats_tmp
```

Filter events on `|IncLevelDifference| > 0.1`, `FDR < 0.05`, and >=10 supporting junction reads averaged per replicate (sum `IJC_SAMPLE_1`, `SJC_SAMPLE_1`, `IJC_SAMPLE_2`, `SJC_SAMPLE_2` — each a comma-separated per-replicate list — and divide by the replicate count); rank by `-log10(FDR) * |IncLevelDifference|` (clamp FDR with `max(FDR, 1e-300)`). Resolve every column by header name: MXE carries two extra coordinate columns, so fixed positions silently read the wrong field. The read floor is not cosmetic — PSI is a ratio, so a 2-read event can reach `|dPSI| = 0.9` and pass FDR on noise alone.

## Parallel path: isoform-level DTU (Salmon -> stageR)

**Goal:** detect within-gene isoform-proportion switches with honest transcript-level FDR.

**Approach:** quantify transcripts with Salmon, import at DTU scale, test proportions with DRIMSeq/DEXSeq, and gate transcript q-values through stageR.

```r
library(tximport)
# DTU import is the OPPOSITE of gene-level DGE: keep transcripts, dtuScaledTPM.
# dtuScaledTPM scales by median tx length AMONG a gene's isoforms, so tx2gene is required even with txOut.
txi <- tximport(files, type = 'salmon', txOut = TRUE, countsFromAbundance = 'dtuScaledTPM', tx2gene = tx2gene)

# Canonical two-stage FDR route (Love, Soneson & Patro 2018): DRIMSeq/DEXSeq proportion test, then
# stageR gene-level SCREEN -> transcript-level CONFIRM. This is the "stageR seam" the principle names;
# mechanism lives in alternative-splicing/isoform-switching.

# Alternative route -- IsoformSwitchAnalyzeR adds NMD/ORF/protein-domain consequences. Its gene-level
# q-value comes from DEXSeq's perGeneQValue (min-p aggregation), NOT the stageR package:
library(IsoformSwitchAnalyzeR)
sList <- importRdata(isoformCountMatrix = txi$counts, isoformRepExpression = txi$abundance,
                     designMatrix = design, isoformExonAnnoation = 'annotation.gtf',
                     isoformNtFasta = 'transcripts.fa')      # 'isoformExonAnnoation' is the real (typo'd) arg
sList <- isoformSwitchTestDEXSeq(sList, reduceToSwitchingGenes = TRUE)   # gene q via DEXSeq perGeneQValue
```

## When NOT to use this pipeline (regime off-ramps)

This pipeline targets **bulk short-read differential splicing between two groups**. For other regimes, use the dedicated skill.

| Question | Use instead |
|----------|-------------|
| "Does this DNA variant alter splicing?" | alternative-splicing/splice-variant-prediction (SpliceAI, Pangolin, MMSplice) |
| "What is aberrant in this single rare-disease patient?" | alternative-splicing/outlier-splicing-detection (FRASER 2.0, OUTRIDER, DROP) |
| "Full-isoform analysis from PacBio Iso-Seq / ONT" | alternative-splicing/long-read-splicing (FLAIR, IsoQuant, Bambu, SQANTI3) |
| "Single-cell splicing analysis" | alternative-splicing/single-cell-splicing (chemistry-first; MARVEL, BRIE2) |
| "Heterogeneous cohort, n>=10 vs n>=10" | This pipeline + MAJIQ V3 HET (alternative-splicing/differential-splicing) |
| "Microexon-focused (3-27 nt)" | This pipeline with VAST-TOOLS or MicroExonator (alternative-splicing/splicing-quantification) |

## QC checkpoints between steps

| After | Gate | Interpretation |
|-------|------|----------------|
| QC/trim | Q30 >80%, adapter <5%, reads not over-trimmed | Aggressive trimming below ~75 nt weakens junction-spanning evidence |
| Alignment | Uniquely-mapped >80%; junction-saturation curves plateau | Still-rising curves = under-sequenced for splicing; deeper reads needed |
| Differential | \|ΔPSI\| >0.1 / >0.2, FDR <0.05, >=10 junction reads | Low read support = PSI is noise; require the read floor per event |
| DTU | stageR gene-level screen passed | Transcript q-values are only valid after the gene screen (alternative-splicing/isoform-switching) |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Differential" events that are really coverage differences | Per-sample 2-pass junctions, not a shared DB | Concatenate all `SJ.out.tab`, feed the combined DB to pass 2 for every sample |
| Isoform-switch signal disappears | Gene-level tximport (`txOut=FALSE`) before splicing | Keep transcripts: `txOut=TRUE` + `dtuScaledTPM` on the DTU branch |
| Too many "significant" transcripts | Transcript q-values reported without stageR | Run the stageR two-stage gene->transcript test |
| Biased PSI across samples | `--readLength` != trimmed length | Set `--readLength` to the real length or add `--variable-read-length` |
| Event- and isoform-level calls "disagree" | Treating ΔPSI and DTU proportion tests as the same question | Reconcile as complementary; they test different things |

## Pipeline map (hand-offs)

- read-qc/fastp-workflow - QC/trim without over-trimming junction-spanning reads
- read-alignment/star-alignment - STAR 2-pass cohort-style, the shared junction DB
- alternative-splicing/splicing-qc - junction saturation/entropy, depth thresholds
- alternative-splicing/splicing-quantification - PSI computation, event taxonomy, sign conventions
- alternative-splicing/differential-splicing - rMATS/leafcutter/MAJIQ selection and reconciliation
- rna-quantification/alignment-free-quant - Salmon transcript quant for the DTU branch
- rna-quantification/tximport-workflow - dtuScaledTPM + txOut import
- alternative-splicing/isoform-switching - DTU + stageR + NMD/ORF/domain consequences
- alternative-splicing/sashimi-plots - ggsashimi/leafviz visualization

The complete runnable script is in this skill's examples/ (`splicing_pipeline.sh`).

## Related Skills

- read-qc/fastp-workflow - QC/trim options
- read-alignment/star-alignment - STAR 2-pass cohort-style configuration
- alternative-splicing/splicing-quantification - PSI computation, event taxonomy, sign conventions
- alternative-splicing/differential-splicing - Tool selection, MAJIQ V3, leafcutter, reconciliation
- alternative-splicing/isoform-switching - DTU + NMD/ORF/domain consequences (IsoformSwitchAnalyzeR v2, stageR)
- alternative-splicing/sashimi-plots - ggsashimi, MAJIQ-VOILA, leafviz visualization
- alternative-splicing/splicing-qc - STAR 2-pass cohort-style, library prep, depth thresholds
- alternative-splicing/single-cell-splicing - 10X chemistry decision; plate-based and long-read SC
- alternative-splicing/splice-variant-prediction - SpliceAI / Pangolin / MMSplice variant interpretation
- alternative-splicing/outlier-splicing-detection - FRASER 2.0 / DROP rare-disease workflow
- alternative-splicing/long-read-splicing - PacBio HiFi / ONT full-isoform analysis
- rna-quantification/alignment-free-quant - Salmon TPM for SUPPA2 and DTU pipelines
- rna-quantification/tximport-workflow - dtuScaledTPM + txOut DTU import

## References

- Shen S, Park JW, Lu ZX, et al (2014) rMATS: robust and flexible detection of differential alternative splicing from replicate RNA-Seq data. *PNAS* 111:E5593-E5601. DOI 10.1073/pnas.1419161111.
- Li YI, Knowles DA, Humphrey J, et al (2018) Annotation-free quantification of RNA splicing using LeafCutter. *Nature Genetics* 50:151-158. DOI 10.1038/s41588-017-0004-9.
- Vitting-Seerup K, Sandelin A (2019) IsoformSwitchAnalyzeR: analysis of changes in genome-wide patterns of alternative splicing and its functional consequences. *Bioinformatics* 35:4469-4471. DOI 10.1093/bioinformatics/btz247.
- Van den Berge K, Soneson C, Robinson MD, Clement L (2017) stageR: a general stage-wise method for controlling the gene-level false discovery rate in differential expression and differential transcript usage. *Genome Biology* 18:151. DOI 10.1186/s13059-017-1277-0.
- Love MI, Soneson C, Patro R (2018) Swimming downstream: statistical analysis of differential transcript usage following Salmon quantification. *F1000Research* 7:952. DOI 10.12688/f1000research.15398.3. (the dtuScaledTPM -> DRIMSeq/DEXSeq -> stageR two-stage DTU workflow.)
<!-- END FILE: workflows/splicing-pipeline/SKILL.md -->

## 子目录：workflows/tcr-pipeline

<!-- BEGIN FILE: workflows/tcr-pipeline/SKILL.md -->
---
name: bio-workflows-tcr-pipeline
description: Orchestrates an end-to-end immune-repertoire pipeline from FASTQ to clonotypes, diversity, overlap, somatic hypermutation and lineages, routing on two forks. Use when deciding bulk vs single-cell (bulk amplicon/RNA-seq -> MiXCR analyze preset -> VDJtools/immunarch depth-normalized diversity and overlap -> figures; 10x paired VDJ -> MiXCR 10x preset or Cell Ranger -> scirpy gene-expression integration, chain QC, clonotype clusters); and TCR vs BCR (TCR -> exact CDR3-nt+V/J clonotypes, VDJtools diversity is fine; BCR -> somatic hypermutation makes exact clonotypes wrong -> Immcantation distToNearest/findThreshold clonal clustering, germline reconstruction, SHM, Dowser lineages); selecting the MiXCR 4.x preset by chemistry and activating its license; downsampling to equal depth before comparing diversity or overlap; and optionally annotating antigen specificity.
tool_type: cli
primary_tool: MiXCR
workflow: true
depends_on:
  - tcr-bcr-analysis/mixcr-analysis
  - tcr-bcr-analysis/vdjtools-analysis
  - tcr-bcr-analysis/immcantation-analysis
  - tcr-bcr-analysis/scirpy-analysis
  - tcr-bcr-analysis/repertoire-visualization
  - tcr-bcr-analysis/specificity-annotation
qc_checkpoints:
  - after_align: "Amplicon alignment >80-90%; RNA-seq legitimately low, judge by clonotype yield; chain usage on-target"
  - after_assemble: "Clonotype count plausible; report UMI/molecule counts, not reads, on UMI libraries"
  - before_diversity: "All samples downsampled to a common depth, else diversity/overlap are confounded by library size"
---

## Version Compatibility

Reference examples tested with: MiXCR 4.7+, VDJtools 1.2.1+, Immcantation suite 4.x, scirpy 0.24+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: MiXCR 4.x replaced the 3.x hand-built `mixcr align -s hsa -p rna-seq` chain with the preset-driven `mixcr analyze <preset>` system, and 4.x refuses to run any command without an activated license (`mixcr activate-license`, or `MI_LICENSE_FILE` on HPC/Docker). A copied 3.x recipe fails on both counts.

# TCR/BCR Repertoire Pipeline

**"Analyze my immune-repertoire sequencing data end-to-end"** -> Route the data by chemistry and receptor, assemble clonotypes with MiXCR, then hand off to depth-normalized diversity (bulk TCR), clonal clustering plus somatic-hypermutation and lineages (BCR), or single-cell gene-expression integration (10x), and finally figures.

This workflow is a router, not a fixed line. Two forks decide everything downstream; pick both before running anything.

## The governing principle: the pipeline forks on two axes

A repertoire measurement is a depth- and chemistry-confounded sample of an unevenly-expanded clonal population, so the correct pipeline depends on how the library was made and which receptor was sequenced. Choosing the wrong branch silently produces plausible-but-wrong numbers.

### Fork A -- bulk vs single-cell

| Axis | Bulk (amplicon or RNA-seq) | Single-cell (10x VDJ) |
|------|----------------------------|-----------------------|
| Assembler | `mixcr analyze <bulk preset>` | `mixcr analyze 10x-sc-xcr-vdj` OR Cell Ranger `vdj` |
| Chain pairing | UNPAIRED (TRB or IGH alone) | Native pairing (TRA+TRB, IGH+IGK/L) |
| Depth vs breadth | Deep repertoire, no cell state | Shallower, links receptor to transcriptome |
| Downstream | VDJtools / immunarch diversity + overlap -> figures | scirpy: chain QC, clonotype clusters, GEX integration |
| Best when | Diversity, overlap, tracking, deep clonotype capture | Antigen-specific cell state, alpha-beta / heavy-light pairing |

### Fork B -- TCR vs BCR

| Axis | TCR (TRA/TRB/TRG/TRD) | BCR (IGH/IGK/IGL) |
|------|-----------------------|-------------------|
| Somatic hypermutation | None | Yes -- clone members are NOT identical |
| Clonotype definition | Exact CDR3-nt + V + J (after UMI/error correction) | NEVER exact CDR3; cluster same-V/J/junction-length by distance |
| Diversity path | VDJtools `CalcDiversityStats` on exact clonotypes is fine | Cluster clones FIRST, then diversity on `clone_id` |
| Extra stages | none | germline reconstruction, SHM, selection, Dowser lineage trees |
| Tool | VDJtools / immunarch | Immcantation (Change-O, SHazaM, SCOPer, Dowser, TIGGER) |

The most common pipeline mistake is running BCR through exact-CDR3 VDJtools diversity. SHM shatters one clone into hundreds of near-identical variants, so exact clonotypes over-count diversity and destroy lineage structure. BCR must route to Immcantation clonal clustering (distToNearest -> findThreshold) before any diversity, SHM, or lineage step. TCR has no SHM, so exact CDR3-nt+V/J is the correct, defensible clonotype and VDJtools diversity is appropriate.

## Pipeline overview

```
FASTQ (+ chemistry, species, receptor known)
    |
    v
[0. License + preset choice] --- mixcr activate-license ; pick preset by kit
    |
    v
[1. MiXCR analyze] ---------- <preset> R1 R2 out_prefix  ->  clones.clns + reports
    |
    +-- QC: mixcr qc / exportQc align + chainUsage
    |
    v
  FORK on data type
    |
    |-- bulk --> [2b. Export] exportClones (VDJtools) / exportAirr
    |               |
    |               v
    |            FORK on receptor
    |               |-- TCR --> [3t. DownSample to equal depth] --> CalcDiversityStats + overlap
    |               |-- BCR --> [3b. Immcantation] distToNearest->findThreshold->clones
    |               |                                -> CreateGermlines --cloned -> SHM -> Dowser trees
    |               v
    |            [4. Visualization] VDJtools / immunarch / ggplot
    |
    |-- single-cell --> [2s. exportAirr / Cell Ranger] --> [3s. scirpy]
                            chain_qc -> ir_dist -> define_clonotypes -> GEX integration
    |
    v
[5. Optional] specificity annotation (VDJdb / GLIPH2 / TCRdist) -- hypothesis, not label
```

## Stage 0: License and preset selection

MiXCR 4.x will not run unlicensed. Activate once (academic license is free), then choose the preset by the exact kit -- the preset encodes species, RNA vs DNA, 5' boundary model (floating for multiplex primers, rigid for 5'-RACE), tag pattern, and assembling feature. The wrong preset does not error; it silently mis-calls V and truncates CDR3.

```bash
mixcr activate-license                 # or: export MI_LICENSE_FILE=/path/mi.license
mixcr exportPreset --preset-name generic-amplicon   # audit what a preset actually does
```

Preset by chemistry (verify against `mixcr analyze --help` and the built-in preset list; MiLaboratories renames occasionally):

| Data | Preset |
|------|--------|
| Generic multiplex/RACE amplicon | `generic-amplicon`, `generic-amplicon-with-umi` (+ `--species hsa`, `--rna`/`--dna`, boundary mixins) |
| Bulk RNA-seq mining | `rna-seq` (judge by clonotype yield, not alignment %) |
| 10x single-cell V(D)J | `10x-sc-xcr-vdj` |
| Takara SMARTer | `takara-human-rna-tcr-umi-smarter-v2`, `takara-human-rna-bcr-umi-smarter` |
| BD Rhapsody | `bd-human-sc-xcr-rhapsody-cdr3` |
| Full component-skill preset table | tcr-bcr-analysis/mixcr-analysis |

## Stage 1: MiXCR assembly (all branches)

```bash
# One command runs align -> refineTagsAndSort -> (assemblePartial) -> assemble -> export.
# From MiXCR 4.7, presets without an intrinsic assembling feature require --assemble-clonotypes-by.
# generic-amplicon REQUIRES material type + both alignment-boundary mixins (it errors without them).
# Multiplex primers on both ends -> floating boundaries; 5'RACE -> --rigid-left-alignment-boundary.
mixcr analyze generic-amplicon \
    --species hsa \
    --rna \
    --floating-left-alignment-boundary \
    --floating-right-alignment-boundary C \
    sample_R1.fastq.gz sample_R2.fastq.gz \
    results/sample

# QC every sample -- low alignment or off-target chains means wrong preset/species/contamination
mixcr qc results/sample.clns
mixcr exportQc align results/*.clns results/qc_align.pdf
mixcr exportQc chainUsage results/*.clns results/qc_chains.pdf
```

**QC checkpoint 1 (after align):** amplicon libraries should align at high rate (often >80-90%); a low rate signals wrong species, wrong boundary model, or untrimmed primers. RNA-seq mining legitimately aligns a tiny fraction -- judge it by absolute clonotype yield. chainUsage catches cross-contamination and index hopping (a TRB library showing appreciable IGH).

Detailed alignment, UMI/cell-barcode handling, and export flags: tcr-bcr-analysis/mixcr-analysis.

## Stage 2: Export (branch-specific handoff)

```bash
# Bulk -> VDJtools-readable clonotype table (per chain)
mixcr exportClones -c TRB results/sample.clns results/sample.clones_TRB.tsv

# BCR or single-cell -> AIRR Rearrangement TSV (the Immcantation / scirpy interchange)
mixcr exportAirr results/sample.clns results/sample.airr.tsv
```

**QC checkpoint 2 (after assemble):** a large reads-to-clonotypes drop-off is normal (millions of reads -> thousands of clones), especially after UMI collapse. Report the right denominator: `uniqueMoleculeCount` on UMI libraries (reporting reads re-introduces the PCR bias the UMIs removed), cells on single-cell, reads only on non-UMI bulk.

## Stage 3t: Bulk TCR diversity and overlap -- downsample FIRST

Diversity (richness, Shannon, clonality) and set-based overlap (Jaccard, shared-clonotype counts) are strictly increasing functions of sequencing depth. Comparing raw values across samples of unequal depth measures depth, not biology -- the single most common error in the field. `DownSample` every sample to a common depth (or read rarefaction curves at a common x) before comparing.

```bash
# 1. Equalize depth: set the target near the cohort lower quartile, and EXCLUDE (do not drag
#    everyone down to) any sample far below it -- an under-sampled library cannot support a claim.
vdjtools DownSample -x 50000 -m metadata.txt ds/

# 2. Diversity on depth-normalized samples; report the resampled table for cross-sample claims
vdjtools CalcDiversityStats -m ds/metadata.txt diversity/

# 3. Overlap with a depth-robust, abundance-weighted metric (F2 / Morisita-Horn), not Jaccard
vdjtools CalcPairwiseDistances -m ds/metadata.txt overlap/
```

**Version caveat (MiXCR 4.x -> VDJtools):** VDJtools is unmaintained for MiXCR 4.x and its parser breaks on raw `exportClones` output (`Unable to parse clonotype string`; 4.x injects commas and renames/moves columns). For a MiXCR 4.7+ cohort, prefer MiXCR's own `mixcr postanalysis individual` / `mixcr postanalysis overlap` (its native 4.x replacement for VDJtools diversity/overlap, with the same downsample-first semantics) over the `vdjtools Convert -S mixcr` route; if VDJtools is required, strip the added contig/target-sequence columns before `Convert`. immunarch (R) is the other modern alternative.

**QC checkpoint 3 (before diversity):** confirm all samples share one depth, and drop any sample whose rarefaction curve is still climbing steeply below that depth (under-sampled -- exclude rather than normalize the cohort down to it). Hold the clonotype match key (nt vs aa, +/-V, +/-J) constant study-wide; aa-level matching inflates apparent sharing via convergent recombination. Report clonality alongside a q=2 Hill number (inverse Simpson) and a rarefaction curve, not alone. immunarch is the modern R alternative with the same normalization semantics: tcr-bcr-analysis/vdjtools-analysis.

## Stage 3b: BCR clonal clustering, SHM and lineages (Immcantation)

BCR cannot use exact clonotypes. Feed the AIRR TSV to Immcantation and follow the mandatory order: annotate -> (TIGGER genotype) -> per-sequence germline -> data-derived clonal threshold -> cluster -> per-clone germline -> SHM/selection -> lineage trees. The threshold from the bimodal distance-to-nearest distribution drives every downstream number; a wrong threshold merges or splits clones.

```r
library(shazam); library(scoper); library(dowser)
db <- airr::read_rearrangement('results/sample.airr.tsv')
# 1. Clonal threshold: valley between the intra-clone and inter-clone modes (per dataset, never reused)
dtn <- distToNearest(db, model = 'ham', normalize = 'len')
thr <- findThreshold(dtn$dist_nearest, method = 'density')@threshold
# 2. Cluster within same-V/J/junction-length partitions at that threshold
cl <- hierarchicalClones(dtn, threshold = thr)
# 3. Reconstruct per-clone germline (CreateGermlines.py --cloned), then observedMutations, then Dowser getTrees
```

Cluster clones within an individual only (genotypes and thresholds are private). Diversity for BCR runs on `clone_id`, not exact CDR3. Full germline reconstruction, SHM quantification, BASELINe selection, and IgPhyML/Dowser trees: tcr-bcr-analysis/immcantation-analysis.

## Stage 3s: Single-cell integration (scirpy)

10x paired VDJ carries native chain pairing and links receptor to cell state. The clonotype definition is a choice, not a default, and multichain cells are likely doublets.

```python
import scirpy as ir
import mudata as mu
airr = ir.io.read_airr('results/sample.airr.tsv')           # or read_10x_vdj on Cell Ranger output
mdata = mu.MuData({'gex': gex_adata, 'airr': airr})         # scirpy 0.13+ stores AIRR as an awkward array
ir.pp.index_chains(mdata)                                    # REQUIRED before chain_qc / clonotyping
ir.tl.chain_qc(mdata)                                        # flag multichain (doublet) / orphan cells
# TCR path: exact-identity clonotypes on CDR3-nt + V/J
ir.pp.ir_dist(mdata)                                         # default metric='identity'
ir.tl.define_clonotypes(mdata)
# BCR path: SHM breaks exact identity, so cluster. ir_dist MUST be recomputed with the SAME
# metric+sequence the clustering call uses (scirpy keys the matrix as ir_dist_{sequence}_{metric};
# the identity matrix above will not satisfy a normalized_hamming call).
# ir.pp.ir_dist(mdata, metric='normalized_hamming', sequence='nt')
# ir.tl.define_clonotype_clusters(mdata, sequence='nt', metric='normalized_hamming', same_v_gene=True)
# integrate with the scanpy GEX modality; measure expansion vs cell state
```

Filtering multichain/orphan cells before expansion analysis preferentially deletes small clones and inflates apparent expansion -- state the trade-off, do not blindly drop them. CellRanger BCR contigs are not IMGT-numbered and include partial/nonproductive contigs; reannotate with IgBLAST (dandelion/airrflow) before rigorous BCR clustering. GEX side (clustering, annotation): single-cell/preprocessing and single-cell/clustering. Full clonotype-definition decisions: tcr-bcr-analysis/scirpy-analysis.

## Stage 4: Visualization

Spectratype (CDR3-length), V-J usage circos, clonal-space bars, rarefaction curves, and clonal tracking across timepoints. Every figure inherits the depth caveat -- plot rarefaction at a common x, and track clones only after downsampling timepoints to equal depth. Recipes: tcr-bcr-analysis/repertoire-visualization.

## Stage 5 (optional): Specificity annotation

Annotate or cluster clonotypes by likely antigen (VDJdb/McPAS lookup, or GLIPH2/TCRdist clustering). A database hit is a sequence match to a published antigen-specific receptor, not proof the clone binds that antigen. "Public" clonotypes are enriched for high generation-probability (Pgen), short, low-insertion CDR3s produced independently in many donors by convergent recombination (Venturi 2006 *PNAS* 103:18691-18696) -- publicity is not antigen selection. Treat every specificity call as a hypothesis, condition on Pgen, and validate. Handoff: tcr-bcr-analysis/specificity-annotation.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| MiXCR exits immediately, "no license" | 4.x needs an activated license | `mixcr activate-license`, or set `MI_LICENSE_FILE` on HPC/Docker; whitelist the phone-home IPs on firewalled clusters |
| `mixcr align -s hsa -p rna-seq` unrecognized | 3.x syntax removed in 4.x | Use `mixcr analyze <preset> R1 R2 out_prefix` |
| Analysis runs but clonotypes look wrong (truncated CDR3, inflated diversity) | Wrong preset -- RNA/DNA, boundary model, or missing tag pattern | Match preset to the exact kit; `mixcr exportPreset` to audit; set `--species` on generic presets |
| MiXCR 4.7 errors on `analyze` needing an assembling feature | Preset lacks an intrinsic assembling feature | Add `--assemble-clonotypes-by CDR3` |
| Diversity/clonality differ across samples but tracks read count | Comparing raw diversity at unequal depth | `DownSample` to a common depth first; report the resampled table / rarefaction at common x |
| BCR clones fragmented, diversity absurdly high, no lineages | Exact-CDR3 clonotypes applied to a hypermutating receptor | Route BCR to Immcantation distToNearest -> findThreshold clustering before any diversity/SHM |
| SHM counts inflated, spurious mutations in junction | No germline reconstruction, or junction not masked | `CreateGermlines.py -g dmask` then `--cloned`; restrict `observedMutations` to `IMGT_V` |
| scirpy expansion inflated by doublets | multichain cells not filtered | Run `chain_qc` and drop multichain cells before clonotype/expansion analysis |
| Overlap dominated by the shallower sample | Jaccard / shared-count on unequal depth | Downsample, then use abundance-weighted F2 or Morisita-Horn |

## Related Skills

- tcr-bcr-analysis/mixcr-analysis - V(D)J alignment and clonotype assembly
- tcr-bcr-analysis/vdjtools-analysis - Depth-normalized diversity and overlap
- tcr-bcr-analysis/immcantation-analysis - BCR clonal clustering, SHM and lineages
- tcr-bcr-analysis/scirpy-analysis - Single-cell VDJ + gene-expression integration
- tcr-bcr-analysis/repertoire-visualization - Figures for the pipeline outputs
- tcr-bcr-analysis/specificity-annotation - Optional antigen-specificity annotation

## References

- Bolotin DA, et al. MiXCR: software for comprehensive adaptive immunity profiling. *Nat Methods* 2015; 12:380-381.
- Shugay M, et al. VDJtools: unifying post-analysis of T cell receptor repertoires. *PLoS Comput Biol* 2015; 11:e1004503.
- Gupta NT, et al. Change-O: a toolkit for analyzing large-scale B cell immunoglobulin repertoire sequencing data. *Bioinformatics* 2015; 31:3356-3358.
- Sturm G, et al. Scirpy: a Scanpy extension for analyzing single-cell T-cell receptor-sequencing data. *Bioinformatics* 2020; 36:4817-4818.
- Chao A, et al. Rarefaction and extrapolation with Hill numbers: a framework for sampling and estimation in species diversity studies. *Ecol Monogr* 2014; 84:45-67.
- Venturi V, et al. Sharing of T cell receptors in antigen-specific responses is driven by convergent recombination. *PNAS* 2006; 103:18691-18696.
<!-- END FILE: workflows/tcr-pipeline/SKILL.md -->

## 子目录：workflows/timecourse-pipeline

<!-- BEGIN FILE: workflows/timecourse-pipeline/SKILL.md -->
---
name: bio-workflows-timecourse-pipeline
description: End-to-end bulk time-course analysis from an expression matrix to temporal gene modules and per-cluster pathway enrichment. Orchestrates temporal DE (limma splines or DESeq2 LRT), Mfuzz/tslearn soft clustering of expression-profile shapes, GAM trajectory fitting, per-cluster GO enrichment against a temporal-gene background, and an OPTIONAL circadian rhythm-detection branch (MetaCycle/CosinorPy) that runs only when the design covers >=2 full cycles with >=6-8 evenly spaced samples per cycle. Use when analyzing a bulk time-series expression experiment from any omics platform and deciding limma-splines vs DESeq2-LRT for temporal DE, soft vs hard clustering, whether the sampling design even licenses rhythm detection, and which background to use for enrichment. Not for single-cell pseudotime (see temporal-genomics/trajectory-modeling for the bulk-vs-pseudotime boundary) or unknown-period discovery (see temporal-genomics/periodicity-detection).
tool_type: mixed
primary_tool: Mfuzz
goal_approach_exempt: true
workflow: true
depends_on:
  - differential-expression/timeseries-de
  - temporal-genomics/temporal-clustering
  - temporal-genomics/circadian-rhythms
  - temporal-genomics/trajectory-modeling
  - pathway-analysis/go-enrichment
qc_checkpoints:
  - after_de: "Significant temporal genes >100 at FDR <0.05; model-fit residuals reasonable"
  - after_clustering: "Membership >0.5 for soft clustering; no empty clusters; k validated by silhouette/gap or bootstrap stability (typical 4-20)"
  - before_rhythm_detection: "GATE: design covers >=2 full cycles AND >=6-8 samples/cycle at ~even spacing AND collection order was randomized; else SKIP rhythm detection"
  - after_enrichment: "At least 3 clusters with significant GO terms at FDR <0.05; background = temporal genes, not the genome"
---

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, limma 3.58+, splines (R base), Mfuzz 2.62+, MetaCycle 1.2+, mgcv 1.9+, clusterProfiler 4.10+, CosinorPy 3.1+, tslearn 0.6+, pygam 0.9+, gseapy 1.2+, statsmodels 0.14+, patsy 1.0+, scikit-learn 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: the whole pipeline is dominated by the SAMPLING DESIGN, not the algorithm. Temporal DE, clustering, and trajectory fitting need genes pre-selected for temporal change and enough timepoints to resolve a shape; rhythm detection additionally requires >=2 full cycles and >=6-8 evenly spaced samples per cycle. A small p-value on 6 timepoints over a single cycle is not evidence of a rhythm.

# Time-Course Analysis Pipeline

**"Analyze my bulk time-course expression data end-to-end"** -> Orchestrate temporal differential expression, soft clustering of expression-profile shapes, GAM trajectory fitting, per-cluster pathway enrichment, and (only under a circadian sampling design) rhythm detection.
- Python: statsmodels/patsy spline F-test -> tslearn TimeSeriesKMeans -> pygam LinearGAM -> gseapy; CosinorPy for the optional rhythm branch
- R: limma splines or DESeq2 LRT -> Mfuzz -> mgcv -> clusterProfiler; MetaCycle for the optional rhythm branch

## Pipeline principles (read before running)

- Clustering, GAM fitting, and enrichment are DESCRIPTIVE steps DOWNSTREAM of the temporal-DE gene selection; they add no inference of their own. Cluster only the temporally variable genes, never the full matrix, or every method returns confident-looking clusters of noise.
- Do NOT test the clusters for the temporal signal used to select the genes (circular / double-dipping). Enrichment is valid only against an INDEPENDENT annotation (GO/KEGG), with the temporal genes as background.
- Rhythm detection is an OPTIONAL branch, not a routine default. It is licensed only by a circadian sampling design (>=2 full cycles, >=6-8 samples/cycle, roughly even spacing, randomized collection order). Under any other design it is SKIPPED, not run with a warning.
- Cluster number k and Mfuzz fuzzifier m are analyst CHOICES, not results; sweep and report the criterion.

## Pipeline Overview

```
Expression matrix + time metadata
    |
    v
[1. Temporal DE] ---------> limma splines / DESeq2 LRT / statsmodels spline F-test
    |                            (selects temporally variable genes; FDR <0.05)
    v
[2. Filter] --------------> Significant temporal genes only (clustering input)
    |
    v
[3. Soft Clustering] -----> Mfuzz (R) / tslearn TimeSeriesKMeans (Python) on z-scored profiles
    |                            +---> QC: membership >0.5, no empty clusters, sweep k
    |
    v
[4b. GAM Trajectory] -----> mgcv / pygam GAM on standardized cluster-mean profiles
    |
    v
[5. Pathway Enrichment] --> clusterProfiler / gseapy per cluster
    |                            background = temporal genes (NOT the genome)
    v
Temporal gene modules + enriched pathways + trajectory fits

    OPTIONAL branch, gated (NOT on the default path):
    IF design covers >=2 full cycles AND >=6-8 samples/cycle (even spacing)
       AND collection order was randomized:
        [4a. Rhythm Detection] --> MetaCycle meta2d / CosinorPy fit_group
                                   period/phase/amplitude + BH q across genes
    ELSE: SKIP (design does not license a rhythm test)
```

## Step 1: Temporal Differential Expression

### R (limma splines)

```r
library(limma)
library(splines)

expr <- as.matrix(read.csv('counts_normalized.csv', row.names = 1))
meta <- read.csv('metadata.csv')

# Natural cubic spline on time; df=3 is enough for most courses, raise to 4-5 for >10 timepoints
design <- model.matrix(~ ns(meta$time, df = 3))
fit <- lmFit(expr, design)
fit <- eBayes(fit)

# Joint F-test on all spline coefficients = "expression changes over time"
temporal_results <- topTable(fit, coef = 2:ncol(design), number = Inf, sort.by = 'F')
# topTable already returns adj.P.Val (BH-corrected); use it directly (not $FDR, which does not exist)
```

### R (DESeq2 LRT)

```r
library(DESeq2)

counts <- as.matrix(read.csv('raw_counts.csv', row.names = 1))
meta <- read.csv('metadata.csv')
meta$time <- factor(meta$time)

# LRT: full model (time as factor) vs reduced (intercept) = any between-timepoint change
dds <- DESeqDataSetFromMatrix(counts, colData = meta, design = ~ time)
dds <- DESeq(dds, test = 'LRT', reduced = ~ 1)
res <- results(dds)   # BH-adjusted padj
```

Choose limma-splines when the time axis is continuous and a smooth trend is expected (normalized/voom or vst input); choose DESeq2-LRT for raw counts and few, discrete timepoints treated as a factor.

### Python (statsmodels spline F-test)

```python
import pandas as pd
import numpy as np
from statsmodels.stats.multitest import multipletests
from patsy import dmatrix
from scipy import stats

expr = pd.read_csv('counts_normalized.csv', index_col=0)
meta = pd.read_csv('metadata.csv')

spline_basis = dmatrix('bs(time, df=3)', data=meta, return_type='dataframe')
# patsy already includes an Intercept column; do NOT prepend another np.ones (that duplicates the
# intercept, inflates model df, and miscalibrates the F-test -> wrong temporal-DE FDR). Use it directly.
design_full = spline_basis.values                          # [Intercept, bs1, bs2, bs3] = 4 cols
design_reduced = np.ones((len(meta), 1))
df_diff = design_full.shape[1] - design_reduced.shape[1]   # 4 - 1 = 3
df_resid = len(meta) - design_full.shape[1]                # n - 4

pvals = []
for gene in expr.index:
    y = expr.loc[gene].values
    ss_full = np.sum((y - design_full @ np.linalg.lstsq(design_full, y, rcond=None)[0]) ** 2)
    ss_red = np.sum((y - design_reduced @ np.linalg.lstsq(design_reduced, y, rcond=None)[0]) ** 2)
    f_stat = ((ss_red - ss_full) / df_diff) / (ss_full / df_resid)
    pvals.append(1 - stats.f.cdf(f_stat, df_diff, df_resid))

# multipletests default is Holm-Sidak; force BH explicitly
_, fdr, _, _ = multipletests(pvals, method='fdr_bh')
temporal_genes = expr.index[fdr < 0.05].tolist()
```

### QC Checkpoint: Temporal DE

```r
sig_genes <- temporal_results[temporal_results$adj.P.Val < 0.05, ]
n_sig <- nrow(sig_genes)
message(sprintf('Significant temporal genes: %d', n_sig))
# <100: underpowered clustering; >10000: check batch/normalization before proceeding
if (n_sig < 100) message('WARNING: Few temporal genes. Check timepoint spacing or relax FDR.')
if (n_sig > 10000) message('WARNING: Many temporal genes. Inspect batch effects / normalization.')
```

## Step 2: Filter Significant Genes

```r
# FDR <0.05 standard; 0.1 acceptable for exploratory clustering only
sig_genes <- rownames(temporal_results[temporal_results$adj.P.Val < 0.05, ])
expr_sig <- expr[sig_genes, ]
message(sprintf('Genes passing FDR <0.05: %d', length(sig_genes)))
```

## Step 3: Soft Clustering (of expression-profile shapes)

Clustering groups genes by SHAPE, not magnitude, so profiles are z-scored per gene first; otherwise abundance dominates and high-expression genes cluster together regardless of dynamics. Cluster only `expr_sig` (the temporal genes), never the full matrix.

### R (Mfuzz)

```r
library(Mfuzz)

eset <- ExpressionSet(assayData = as.matrix(expr_sig))
eset <- standardise(eset)   # per-gene mean 0, sd 1: makes distance shape-based, not magnitude-based

# mestimate() implements Schwaemmle & Jensen (2010): the smallest m that stops fuzzy c-means
# from clustering RANDOMIZED data. It is dominated by the number of timepoints; inspect the
# returned value and the membership distribution rather than trusting it blindly (or hardcoding m=2).
m <- mestimate(eset)
message(sprintf('Estimated fuzzifier m = %.2f', m))

# k is a resolution CHOICE, not a result: start ~sqrt(n_genes/2), then sweep and validate (below)
n_clusters <- 8
cl <- mfuzz(eset, c = n_clusters, m = m)

# Membership >0.5 = core (confident) genes; lower to 0.3 only for exploratory overlap
core_genes <- acore(eset, cl, min.acore = 0.5)
```

### Python (tslearn)

```python
from tslearn.clustering import TimeSeriesKMeans

# Row-wise z-score: normalize each gene across its own timepoints (shape, not level)
expr_scaled = (expr_sig.values - expr_sig.values.mean(axis=1, keepdims=True)) / expr_sig.values.std(axis=1, keepdims=True)

# soft-DTW tolerates phase-shifted profiles Euclidean would split; gamma smooths the DTW geometry.
# Use plain 'euclidean' when absolute phase is biologically meaningful (morning vs evening genes).
model = TimeSeriesKMeans(n_clusters=8, metric='softdtw', metric_params={'gamma': 0.01},
                         max_iter=50, random_state=42)
labels = model.fit_predict(expr_scaled.reshape(expr_scaled.shape[0], expr_scaled.shape[1], 1))
```

### QC Checkpoint: Clustering

```r
library(cluster)
cluster_sizes <- table(cl$cluster)
print(cluster_sizes)
if (any(cluster_sizes == 0)) message('WARNING: Empty clusters. Reduce n_clusters.')

for (i in seq_along(core_genes)) {
    message(sprintf('Cluster %d: %d core genes (membership >0.5)', i, nrow(core_genes[[i]])))
}

# Silhouette on the z-scored profiles; triangulate k with a sweep, do not crown one index
sil <- silhouette(cl$cluster, dist(exprs(eset)))
message(sprintf('Mean silhouette: %.3f', mean(sil[, 3])))
```

## Step 4a: Rhythm Detection (OPTIONAL branch - GATED)

**This branch runs only when the sampling design licenses a rhythm test. Otherwise it is SKIPPED, not run with a warning.** Rhythm detection is not a routine step in a general time-course pipeline.

Hard precondition (all must hold), a design gate, not a soft aside:
- **>=2 full cycles** of the target period (48h+ for a 24h circadian rhythm). One cycle cannot distinguish an oscillation from a monotone trend or a single transient bump.
- **>=6-8 samples per cycle at roughly even spacing** (a lenient practical convention; Hughes 2017 recommends denser -- every 2h / >=12 per cycle -- and calls 4h intervals underpowered). Nyquist's 2/cycle is a mathematical floor with zero robustness to noise, no phase, no amplitude, no waveform shape.
- **Collection order randomized.** Harvest/collection order aliases directly onto circadian time: any drift (reagent lot, RIN, lane) is perfectly confounded with the rhythm axis and CANNOT be removed analytically. The only fix is design (randomize processing order).

Even when the gate passes, a rhythm found under a light-dark (LD) cycle may be light/feeding-DRIVEN masking, not endogenous clock output: diurnal != circadian. Endogeneity requires persistence under constant conditions (constant darkness, DD). Report ZT for entrained (LD) data, CT for free-running (DD) data.

```python
CIRCADIAN_DESIGN = False  # the un-computable precondition (circadian design + randomized order); set True only if it holds

n_cycles = (meta['time'].max() - meta['time'].min()) / 24.0
samples_per_cycle = meta['time'].nunique() / max(n_cycles, 1e-9)
gate_design = n_cycles >= 2 and samples_per_cycle >= 6   # the COMPUTABLE part of the gate
if CIRCADIAN_DESIGN and gate_design:
    pass  # run rhythm detection (CosinorPy/MetaCycle below)
elif not gate_design:
    print(f'Rhythm detection SKIPPED: inadequate design ({n_cycles:.1f} cycles, {samples_per_cycle:.1f}/cycle; need >=2 and >=6-8).')
else:
    print('Rhythm detection SKIPPED: design meets the cycle/sampling floor but CIRCADIAN_DESIGN is not set (randomized-order / circadian precondition unconfirmed).')
```

### R (MetaCycle)

```r
library(MetaCycle)
expr_for_meta <- expr_sig
colnames(expr_for_meta) <- meta$time
write.csv(expr_for_meta, 'expr_for_metacycle.csv')

# Circadian search window 20-28h; ARS/JTK require EVEN integer sampling and drop out silently
# (analysisStrategy='auto') on uneven/replicated data, leaving LS only.
meta2d('expr_for_metacycle.csv', filestyle = 'csv',
       minper = 20, maxper = 28,
       timepoints = sort(unique(meta$time)),
       outdir = 'metacycle_results')
# Filter on meta2d_BH.Q (BH FDR) AND meta2d_rAMP (relative amplitude); significance alone over-detects.
```

### Python (CosinorPy)

```python
from CosinorPy import cosinor   # note: import name is capitalized CosinorPy, not cosinorpy

# fit_group expects long-format columns 'x' (time), 'y' (expression), 'test' (gene id).
# period=24 for circadian; n_components=2 adds the 12h harmonic for non-sinusoidal shapes.
results = cosinor.fit_group(expr_long, period=24, n_components=1)

# fit_group ALREADY returns a BH-adjusted 'q' column across the fitted group; use it, do NOT
# threshold the raw per-gene 'p'. Add a RELATIVE-amplitude filter (fit_group has no rAMP column,
# so compute rAMP = amplitude/mesor): significance alone over-detects rhythms. rAMP>0.1 = >=10% of baseline.
results['rAMP'] = results['amplitude'] / results['mesor']
rhythmic = results[(results['q'] < 0.05) & (results['rAMP'] > 0.1)]
```

## Step 4b: GAM Trajectory Fitting

GAMs here summarize each cluster's temporal shape by fitting a penalized smooth to the STANDARDIZED cluster-mean profile. Because the input is a z-scored mean (not raw counts), a Gaussian family is appropriate; NB-family/offsets are needed only when fitting raw counts directly (see temporal-genomics/trajectory-modeling).

### R (mgcv)

```r
library(mgcv)

cluster_trajectories <- list()
for (cl_id in 1:n_clusters) {
    cl_genes <- names(cl$cluster[cl$cluster == cl_id])
    mean_profile <- colMeans(expr_sig[cl_genes, ])
    df_gam <- data.frame(time = meta$time, expr = mean_profile)

    # k is a flexibility CEILING (max basis dimension), NOT the number of knots/bends to fit.
    # REML (not GCV) then picks the wiggliness penalty; realized complexity is reported as edf.
    # Keep k < number of unique timepoints (identifiability); k=5 suits >=6-8 timepoints.
    gam_fit <- gam(expr ~ s(time, k = 5), data = df_gam, method = 'REML')

    cluster_trajectories[[cl_id]] <- list(fit = gam_fit,
                                          r_squared = summary(gam_fit)$r.sq,
                                          edf = summary(gam_fit)$edf)
    message(sprintf('Cluster %d: R^2 = %.3f, EDF = %.2f (edf~1 => linear; edf~k-1 => highly non-linear)',
                    cl_id, summary(gam_fit)$r.sq, summary(gam_fit)$edf))
}
```

### Python (pygam)

```python
from pygam import LinearGAM, s

for cl_id in range(n_clusters):
    mean_profile = expr_scaled[labels == cl_id].mean(axis=0)
    # n_splines is the basis-dimension ceiling (like mgcv k); the penalty picks realized wiggliness.
    gam = LinearGAM(s(0, n_splines=5)).fit(meta['time'].values.reshape(-1, 1), mean_profile)
    print(f'Cluster {cl_id}: GCV = {gam.statistics_["GCV"]:.4f}, edof = {gam.statistics_["edof"]:.2f}')
```

## Step 5: Per-Cluster Pathway Enrichment

The enrichment BACKGROUND (universe) must be the temporal genes that were clustered, NOT the whole genome. Genome background re-detects the generic biology of being a dynamic gene (the selection step), so every cluster lights up; temporal-gene background isolates what makes THIS shape distinct.

### R (clusterProfiler)

```r
library(clusterProfiler)
library(org.Hs.eg.db)

all_temporal_entrez <- bitr(rownames(expr_sig), fromType = 'SYMBOL', toType = 'ENTREZID',
                            OrgDb = org.Hs.eg.db)

enrichment_results <- list()
for (i in seq_along(core_genes)) {
    entrez <- bitr(core_genes[[i]]$NAME, fromType = 'SYMBOL', toType = 'ENTREZID', OrgDb = org.Hs.eg.db)
    ego <- enrichGO(gene = entrez$ENTREZID,
                    universe = all_temporal_entrez$ENTREZID,   # background = temporal genes
                    OrgDb = org.Hs.eg.db, ont = 'BP', pAdjustMethod = 'BH',
                    pvalueCutoff = 0.05, qvalueCutoff = 0.05, readable = TRUE)
    if (nrow(as.data.frame(ego)) > 0) {
        ego <- simplify(ego, cutoff = 0.7, by = 'p.adjust')   # collapse redundant parent-child GO terms
    }
    enrichment_results[[i]] <- ego
    message(sprintf('Cluster %d: %d significant GO terms', i, nrow(as.data.frame(ego))))
}
```

### Python (gseapy)

```python
import gseapy as gp

all_temporal_genes = list(expr_sig.index)   # background = temporal genes, not the genome

for cl_id in range(n_clusters):
    cl_genes = [g for g, l in zip(expr_sig.index, labels) if l == cl_id]
    # enrichr hits the Enrichr web API; pass background=temporal genes and outdir=None (no files).
    # For a strictly offline hypergeometric test with a custom background, gp.enrich(gene_sets=<gmt/dict>,
    # background=all_temporal_genes) computes it locally instead.
    enr = gp.enrichr(gene_list=cl_genes, gene_sets='GO_Biological_Process_2023',
                     organism='human', background=all_temporal_genes, outdir=None)
    sig_terms = enr.results[enr.results['Adjusted P-value'] < 0.05]
    print(f'Cluster {cl_id}: {len(sig_terms)} significant GO terms')
```

### QC Checkpoint: Enrichment

```r
clusters_with_terms <- sum(sapply(enrichment_results, function(x) nrow(as.data.frame(x)) > 0))
message(sprintf('Clusters with significant GO terms: %d / %d', clusters_with_terms, length(enrichment_results)))
if (clusters_with_terms < 3) message('WARNING: Few clusters enriched. Check gene ID mapping or thresholds.')
```

## Parameter Recommendations

| Step | Parameter | Recommendation |
|------|-----------|----------------|
| Temporal DE | Spline df | 3 (default); 4-5 for >10 timepoints |
| Temporal DE | FDR | 0.05 (standard); 0.1 exploratory clustering only |
| Clustering | fuzzifier m | Use mestimate(); inspect returned value + membership distribution |
| Clustering | n_clusters (k) | 4-20; a CHOICE, not a result; sweep + validate (silhouette/gap/bootstrap) |
| Clustering | min membership | 0.5 (core); 0.3 (exploratory) |
| Rhythm (gated) | design gate | >=2 cycles AND >=6-8 samples/cycle AND randomized order; else skip |
| Rhythm (gated) | period window | 20-28h circadian; filter on BH q AND rAMP |
| GAM | k (basis ceiling) | 5 for >=6-8 timepoints; keep k < #unique timepoints; REML picks the penalty |
| Enrichment | background | temporal genes (NOT genome); pvalueCutoff 0.05 |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Clusters look clean but mean nothing | Clustered the full matrix / did not z-score | Cluster only temporal-DE hits; standardise per gene first |
| Cluster enrichment lights up everywhere with generic terms | Genome used as enrichment background | Use temporal genes as universe/background |
| "Rhythmic" hits on a short/1-cycle design | Rhythm test run without the design gate | Enforce >=2 cycles + >=6-8 samples/cycle; else skip the branch |
| A 24h rhythm appears at ~12h or ~36h | Aliasing from sub-Nyquist sampling | Sample >=2x per target period; report the interval |
| Implausibly many rhythmic genes | Significance-only threshold; undetrended trend | Filter on rAMP/amplitude too; require >=2 cycles |
| CosinorPy import fails | Wrong import name | `from CosinorPy import cosinor` (capitalized) |
| MetaCycle "wrote files but read.csv fails" | Output is under `outdir/` as `meta2d_<infile>` | Read the actual emitted path; ARS/JTK silently drop on uneven sampling |
| gam.check k-index < 1 | Basis ceiling k too low (or residual autocorrelation) | Double k and refit; if edf barely moves, suspect autocorrelation, not k |
| GAM p=1e-30 over-trusted | Smooth-term p-values are approximate | Treat as categorical significant/not; apply BH across genes |

## Related Skills

- differential-expression/timeseries-de - Temporal DE methods (limma splines, DESeq2 LRT, maSigPro)
- temporal-genomics/temporal-clustering - Soft/hard clustering, k selection, DTW details
- temporal-genomics/circadian-rhythms - Single-condition rhythm detection, sampling design, phase/amplitude
- temporal-genomics/differential-rhythmicity - Comparing rhythms between conditions (gain/loss/phase/amplitude)
- temporal-genomics/trajectory-modeling - GAM fitting, k-vs-edf, bulk-vs-pseudotime boundary
- temporal-genomics/periodicity-detection - Unknown-period discovery (Lomb-Scargle, wavelets)
- pathway-analysis/go-enrichment - Enrichment, background choice, GO term simplification

## References

- Hughes ME, Abruzzi KC, Allada R, et al. 2017. Guidelines for Genome-Scale Analysis of Biological Rhythms. *J Biol Rhythms* 32(5):380-393. doi:10.1177/0748730417728663. (Recommends >=2 cycles and dense sampling -- at least every 2 h / >=12 timepoints per cycle, explicitly calling 4 h intervals underpowered -- plus biological replicates. The lenient 6-8/cycle floor used above is a stated practical convention, denser is better.)
- Wu G, Anafi RC, Hughes ME, Kornacker K, Hogenesch JB. 2016. MetaCycle: an integrated R package to evaluate periodicity in large scale data. *Bioinformatics* 32(21):3351-3353. doi:10.1093/bioinformatics/btw405. (meta2d integrating ARS/JTK/LS; output columns.)
- Moškon M. 2020. CosinorPy: a python package for cosinor-based rhythmometry. *BMC Bioinformatics* 21(1):485. doi:10.1186/s12859-020-03830-w. (fit_group / cosinor rhythmometry.)
- Futschik ME, Carlisle B. 2005. Noise-robust soft clustering of gene expression time-course data. *J Bioinform Comput Biol* 3(4):965-988. doi:10.1142/S0219720005001375. (Fuzzy c-means noise-robustness rationale for Mfuzz.)
- Schwämmle V, Jensen ON. 2010. A simple and fast method to determine the parameters for fuzzy c-means cluster analysis. *Bioinformatics* 26(22):2841-2848. doi:10.1093/bioinformatics/btq534. (The mestimate() fuzzifier estimator.)
- Wood SN. 2011. Fast stable restricted maximum likelihood and marginal likelihood estimation of semiparametric generalized linear models. *J R Stat Soc B* 73(1):3-36. doi:10.1111/j.1467-9868.2010.00749.x. (Why REML over GCV for the smoothing penalty.)
- Laloum D, Robinson-Rechavi M. 2020. Methods detecting rhythmic gene expression are biologically relevant only for strong signal. *PLoS Comput Biol* 16(3):e1007666. doi:10.1371/journal.pcbi.1007666. (Amplitude filtering; significance alone over-detects rhythms.)
<!-- END FILE: workflows/timecourse-pipeline/SKILL.md -->

<!-- END CATEGORY: workflows -->

