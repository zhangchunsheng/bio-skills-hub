---
slug: bio-epitranscriptomics-integrated
version: 1.0.1
displayName: "表观转录组学 / Epitranscriptomics"
name: bio-epitranscriptomics-integrated
summary: "中文：表观转录组学综合技能，整合 5 个相关专题，覆盖表观转录组学：MeRIP-seq m6A峰调用、m6Anet纳米孔检测、差异m6A、修饰可视化。 English: Integrated Epitranscriptomics skill covering 5 related topics, including Epitranscriptomics: MeRIP-seq m6A peak calling, m6Anet nanopore detection, differential m6A, modification visualization."
description: "中文：这是一个面向表观转录组学的综合生物信息学 Skill，整合当前分类下 5 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：表观转录组学：MeRIP-seq m6A峰调用、m6Anet纳米孔检测、差异m6A、修饰可视化。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Guitar, STAR, exomePeak2。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Epitranscriptomics, combining 5 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Epitranscriptomics: MeRIP-seq m6A peak calling, m6Anet nanopore detection, differential m6A, modification visualization. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Guitar, STAR, exomePeak2. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# epitranscriptomics 分类 Skill 整合版

> 本文件整合同一主分类目录下 5 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: epitranscriptomics -->

## 子目录：epitranscriptomics/m6a-differential

<!-- BEGIN FILE: epitranscriptomics/m6a-differential/SKILL.md -->
---
name: bio-epitranscriptomics-m6a-differential
description: Identifies differential m6A methylation between conditions from MeRIP-seq paired IP/input data using exomePeak2 (GC-bias-aware differential via its bam_ip/bam_input control + bam_treated_ip/bam_treated_input treatment arms), QNB beta-binomial, MeTDiff HMM, and RADAR, plus the paired-symmetric edgeR/DESeq2-on-peak-counts route when batch/lot covariates need fixed-effect handling that exomePeak2's API does not accept. Covers paired vs unpaired vs interaction designs, batch confounding and per-lot meta-analysis, the stoichiometry-vs-expression-vs-IP-efficiency confound, and effect-size filtering against under-powered N=2 designs. Use when comparing m6A across two or more conditions, choosing between exomePeak2/QNB/RADAR/MeTDiff for a design, handling batch confounding when exomePeak2's API is too rigid, distinguishing real hyper/hypo-methylation from expression shifts, applying effect-size thresholds, or planning orthogonal stoichiometry validation (GLORI/SAC-seq/m6Anet mod_ratio).
tool_type: r
primary_tool: exomePeak2
---

## Version Compatibility

Reference examples tested with: exomePeak2 1.14+ (Bioconductor 3.18+), QNB 1.1.11 (GitHub `lzcyzm/QNB`), MeTDiff (GitHub, bundled with MeTPeak), RADAR 0.2.4+ (GitHub `scottzijiezhang/RADAR`), DESeq2 1.42+, edgeR 4.0+, GenomicFeatures 1.54+, ggplot2 3.5+, GenomicAlignments 1.38+, Rsubread 2.16+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('exomePeak2')` then `?exomePeak2` to verify parameters
- R: `packageVersion('QNB')` then `?qnbtest` to confirm argument signature

If R throws `unused argument` or `argument is missing`, the API moved between Bioconductor minor releases; consult `?exomePeak2` directly. QNB function signature has been stable since 2017 but the GitHub source has occasional changes; pin the commit SHA.

exomePeak2's differential interface is NOT a `mode=` argument — populate the `bam_treated_ip=` and `bam_treated_input=` arguments alongside the standard `bam_ip=` / `bam_input=` (control arm) to trigger paired differential calling. `peak_calling_mode` is a separate argument controlling locus scope (`exon` | `full_transcript` | `whole_genome`). Verify against `?exomePeak2` and Bioconductor 3.20+ release notes. QNB is on GitHub only; install via `devtools::install_github('lzcyzm/QNB')`. RADAR is on GitHub only; install via `devtools::install_github('scottzijiezhang/RADAR')`; its differential workflow is `countReads -> normalizeLibrary -> adjustExprLevel -> filterBins -> diffIP -> reportResult`.

# Differential m6A Analysis

**"Compare m6A methylation between my conditions"** -> Quantify how much each m6A peak's IP/input enrichment shifts between conditions, after normalising for transcript-abundance changes (which all show up in input) and for IP-efficiency drift (which the design matrix and within-run replicates control for). Then apply effect-size filtering to distinguish real biology from the technical noise floor that all MeRIP differential methods inherit (McIntyre 2020 *Sci Rep* 10:6590: between-study m6A peak overlap is ~45% median; differential calls within that noise envelope routinely fail to replicate). Critically: a higher MeRIP signal in condition A vs B can mean (1) more transcripts of the peak-bearing gene, (2) more methylation per transcript, OR (3) higher IP efficiency in batch A — distinguishing requires careful normalisation or an orthogonal absolute-stoichiometry method.

- R: `exomePeak2::exomePeak2(bam_ip, bam_input, bam_treated_ip, bam_treated_input, ...)` -- integrated peak + differential GLM (modern default)
- R: `QNB::qnbtest(control_ip, treated_ip, control_input, treated_input)` -- beta-binomial for small N (Liu 2017 *BMC Bioinformatics* 18:387)
- R: `RADAR::diffIP()` then `reportResult()` -- Poisson-NB on peak windows with TMM normalisation (Zhang 2019 *Genome Biol* 20:294)
- R: `MeTDiff::metdiff()` -- HMM-based differential paired with MeTPeak
- R: edgeR / DESeq2 on featureCounts-on-peaks matrix -- defensible for paired symmetric designs with strong input normalisation; also the route for arbitrary batch / lot covariates exomePeak2's API does not accept

## The Single Most Important Modern Insight -- IP fold-change between conditions conflates stoichiometry change with expression change and IP efficiency drift

A higher m6A peak signal in condition A vs B can mean ANY of: (1) more transcripts of the peak-bearing gene (expression up; the input increases proportionally, so the ratio should not change — but residual normalisation noise leaks through), (2) more methylation per transcript (stoichiometry up; the real biology of interest), (3) higher IP efficiency in batch A (technical; antibody lot, IP day, RNA prep). Differential MeRIP WITHOUT per-window input-normalisation OR an orthogonal stoichiometry-aware method (GLORI Liu 2023 *Nat Biotechnol* 41:355; SAC-seq Hu 2022 *Nat Biotechnol* 40:1210; MAZTER-seq Garcia-Campos 2019 *Cell* 178:731; m6Anet per-read modification rate) cannot separate the three. exomePeak2 differential mode, QNB, RADAR, and MeTDiff all implement per-window IP/input ratio modelling, but each has different default normalisations and the choice matters. Equally critical: McIntyre 2020 *Sci Rep* 10:6590 showed that "differential" m6A peaks from MeRIP-seq routinely do not replicate between independent studies in nominally identical conditions. The empirical noise floor is high; effect-size filtering (|log2FC| >= 0.5 minimum, often >= 1) AND replicate-direction concordance (the change is consistent in direction across replicates) AND minimum N=3 per condition are needed for differential calls to survive replication. For any absolute stoichiometry claim ("this peak is 80% methylated in tumour vs 20% in normal"), require an orthogonal stoichiometry method, not MeRIP alone.

## Algorithmic Taxonomy

| Tool / mode | Mechanism | Inputs | Output | Strength | Fails when |
|-------------|-----------|--------|--------|----------|------------|
| exomePeak2 differential (Liu 2022) | Transcript-windowed Poisson GLM with GC-bias correction; integrated peak + differential | control IP/input BAM vectors + treated IP/input BAM vectors + TxDb + BSgenome | Differential peaks with log2FC + FDR per peak | Most use cases; integrates with peak calling; modern default | Small-N (<=2) overdispersion poorly estimated; top-level API does NOT accept arbitrary covariates (use DESeq2/edgeR for batch-aware designs) |
| QNB (Liu 2017 *BMC Bioinformatics* 18:387) | Quad-negative-binomial joint model of IP, input, condition | per-peak count matrices (4 matrices: ip1, ip2, input1, input2) | Differential peaks with p-value + log2 RR | Designed for small N (2-3 per group); handles overdispersion explicitly | Requires pre-computed count matrices; not integrated with peak calling |
| MeTDiff (bundled with MeTPeak) | HMM + Beta-binomial differential paired with MeTPeak | paired IP/input BAM + GTF + condition factor | Differential peaks per window | Pairs naturally with MeTPeak output; HMM smoothing helps low-coverage | GitHub-only; less benchmarked than exomePeak2 / QNB |
| RADAR (Zhang 2019 *Genome Biol* 20:294) | Poisson-NB with TMM normalisation; reproducibility-aware | paired IP/input BAM + condition factor | Differential peaks with logFC + FDR | Explicit replicate-variance modeling; reproducibility-aware framework | GitHub-only; slower than exomePeak2 |
| DRME (Liu 2016 *Anal Biochem* 499:15) | Count-based small-sample alternative | per-peak count matrices | Differential peaks | Sister to QNB from same group; small-N alternative | Less benchmarked than QNB / exomePeak2 |
| edgeR / DESeq2 on peak counts | Generic RNA-seq differential framework applied to featureCounts-on-peaks | peak count matrix + sample sheet | Differential peaks with log2FC + FDR | Familiar; flexible designs; well-tested in RNA-seq | Treats peak counts as RNA counts; loses IP/input pairing structure; defensible only for paired symmetric designs with strong input normalisation |
| Ratio-of-ratios (heuristic) | Compute per-peak log2 (IP_A / Input_A) - log2 (IP_B / Input_B) per sample, then t-test | per-peak count matrix | per-peak t-test | Transparent; no model assumptions | No multiple-testing correction; ignores overdispersion; not recommended for primary analysis |

## Decision Tree by Scenario

| Scenario | Recommended | Why wrong choices fail |
|----------|-------------|------------------------|
| Standard 3-vs-3 paired-design MeRIP differential | exomePeak2 with `bam_ip` (ctrl) + `bam_treated_ip` (treat) and matching inputs | QNB usable but designed for smaller N; edgeR/DESeq2 loses IP/input pairing |
| Very small N (2 vs 2) | QNB (designed for small-sample overdispersion); supplement with exomePeak2 if possible | edgeR / DESeq2 dispersion estimation collapses; exomePeak2 GLM also struggles at N=2 |
| Paired design (patient as blocking factor) | QNB per-pair then aggregate; OR featureCounts-on-peaks -> DESeq2 with `~patient + condition` design; exomePeak2 cannot encode patient blocking via its top-level API | Unpaired analysis inflates within-group variance |
| Interaction design (genotype × treatment) | featureCounts-on-peaks -> DESeq2 / edgeR with interaction term; exomePeak2 top-level API is two-group only | QNB pairwise only; build interaction model from pairwise contrasts manually |
| Batch confounding (antibody lot, sequencing run, IP day) | Include batch as fixed effect in DESeq2 / edgeR model on featureCounts-on-peaks matrix; OR run exomePeak2 per-batch and meta-analyse | Pooling cross-batch counts without batch term attributes lot-effect to condition |
| Time-course differential | featureCounts-on-peaks -> DESeq2 / limma with time as numeric covariate; OR pairwise time-point exomePeak2 contrasts | Naive group-vs-group ignores time structure |
| Stoichiometry claims (not just enrichment) | NOT MeRIP differential -- orthogonal GLORI / SAC-seq / m6Anet per-read | MeRIP IP fold-change is relative; cannot give per-molecule stoichiometry |
| Cross-batch differential (different antibody lots) | featureCounts-on-peaks -> DESeq2 / edgeR with `lot` in design; OR run exomePeak2 per-lot then meta-analyse; ideally avoid confounding lot with condition at the experimental-design stage | Lot effect inflates false positives; exomePeak2 top-level API cannot encode lot |
| Validation of differential calls | Run >=2 differential methods; require concordant direction across replicates AND |log2FC| > 0.5 minimum (>= 1 stringent); orthogonal validation at top hits | Single-method differential calls within technical noise floor (per McIntyre 2020) |
| Visualising differential peaks | Volcano plot with |log2FC| + FDR thresholds; MA plot to inspect normalisation; per-peak boxplot for top hits | Single number summaries hide stoichiometry vs expression confound |
| Wanting to test a single gene / locus | Targeted: per-peak boxplot across replicates with condition factor; manual t-test or Wilcoxon at high-coverage peak | Whole-transcriptome differential testing wastes multiple-testing budget for single-locus questions |

Methodology evolves; before any high-stakes differential analysis, web-search "exomePeak2 differential mode Bioconductor 3.20" and "MeRIP differential benchmark McIntyre" for current consensus parameters.

## exomePeak2 Differential Workflow

**Goal:** Identify m6A peaks that differ in methylation level between conditions, controlling for transcript-abundance differences (via input normalisation) and GC bias (via internal correction), with an integrated peak-calling + differential pipeline.

**Approach:** Build TxDb from the matched GTF; pass control IP/input BAM vectors via `bam_ip` and `bam_input` AND treatment IP/input BAM vectors via `bam_treated_ip` and `bam_treated_input` — populating the treated arms triggers differential mode (there is no separate `mode=` argument). Output is per-peak log2FC + FDR.

```r
library(exomePeak2)
library(GenomicFeatures)
library(BSgenome.Hsapiens.UCSC.hg38)

txdb <- makeTxDbFromGFF('refs/annotation.gtf', format='gtf')

ctrl_ip      <- c('aligned/ctrl_IP1.bam', 'aligned/ctrl_IP2.bam', 'aligned/ctrl_IP3.bam')
ctrl_input   <- c('aligned/ctrl_Input1.bam', 'aligned/ctrl_Input2.bam', 'aligned/ctrl_Input3.bam')
treat_ip     <- c('aligned/treat_IP1.bam', 'aligned/treat_IP2.bam', 'aligned/treat_IP3.bam')
treat_input  <- c('aligned/treat_Input1.bam', 'aligned/treat_Input2.bam', 'aligned/treat_Input3.bam')

result <- exomePeak2(
    bam_ip             = ctrl_ip,
    bam_input          = ctrl_input,
    bam_treated_ip     = treat_ip,
    bam_treated_input  = treat_input,
    txdb               = txdb,
    genome             = BSgenome.Hsapiens.UCSC.hg38,
    paired_end         = TRUE,
    library_type       = 'unstranded',
    peak_calling_mode  = 'exon',
    save_dir           = 'exomepeak2_diff_output',
    experiment_name    = 'ctrl_vs_treat'
)

diff_table <- as.data.frame(result)
nrow(diff_table)
head(diff_table[, c('seqnames', 'start', 'end', 'log2FC', 'pvalue', 'padj')])
```

`peak_calling_mode` accepts `'exon'` (transcript-aware, default), `'full_transcript'`, or `'whole_genome'`; the meaning is locus scope, NOT differential-vs-non-differential. For arbitrary covariate adjustment (batch, antibody lot, patient blocking), the exomePeak2 top-level API is insufficient — move counts into DESeq2 / edgeR via the featureCounts-on-peaks route below.

## QNB Beta-Binomial for Small-N Designs

**Goal:** Test differential m6A at pre-called peaks using a quad-negative-binomial model that handles small-N overdispersion better than generic GLM frameworks.

**Approach:** Count reads in each IP and Input BAM at each peak using featureCounts or summarizeOverlaps; pass the four count matrices (ip1, ip2, input1, input2 — ip/input per group) to `qnbtest()`.

```r
library(QNB)
library(Rsubread)
library(rtracklayer)

peaks <- import('exomepeak2_output/m6a_run1/peaks.bed')
peak_saf <- data.frame(
    GeneID = paste0('peak_', seq_along(peaks)),
    Chr    = as.character(seqnames(peaks)),
    Start  = start(peaks),
    End    = end(peaks),
    Strand = as.character(strand(peaks))
)

count_matrix <- function(bam_paths, peak_saf) {
    fc <- featureCounts(
        files       = bam_paths,
        annot.ext   = peak_saf,
        isPairedEnd = TRUE,
        nthreads    = 8,
        allowMultiOverlap = TRUE
    )
    fc$counts
}

ip_ctrl   <- count_matrix(c('aligned/ctrl_IP1.bam', 'aligned/ctrl_IP2.bam', 'aligned/ctrl_IP3.bam'), peak_saf)
ip_treat  <- count_matrix(c('aligned/treat_IP1.bam', 'aligned/treat_IP2.bam', 'aligned/treat_IP3.bam'), peak_saf)
in_ctrl   <- count_matrix(c('aligned/ctrl_Input1.bam', 'aligned/ctrl_Input2.bam', 'aligned/ctrl_Input3.bam'), peak_saf)
in_treat  <- count_matrix(c('aligned/treat_Input1.bam', 'aligned/treat_Input2.bam', 'aligned/treat_Input3.bam'), peak_saf)

qnb_result <- qnbtest(
    control_ip    = ip_ctrl,
    treated_ip    = ip_treat,
    control_input = in_ctrl,
    treated_input = in_treat,
    mode          = 'per-condition'
)

head(qnb_result)
sig <- qnb_result[qnb_result$padj < 0.05 & abs(qnb_result$log2.RR) > 0.5, ]
nrow(sig)
```

Verify QNB argument names against `?qnbtest` for the installed version; older tutorials may show different signatures.

## RADAR Reproducibility-Aware Differential

**Goal:** Test differential m6A using a Poisson-NB framework with TMM normalisation and explicit replicate-variance modeling; useful when replicate variability is a known issue.

**Approach:** RADAR's documented workflow is `countReads -> normalizeLibrary -> adjustExprLevel -> filterBins -> diffIP -> reportResult`. CRITICAL: RADAR expects matched BAMs in `bamFolder` named `<sample>.input.bam` and `<sample>.m6A.bam` per replicate; the generic IP / Input naming used elsewhere must be re-conformed or symlinked. `variable()` is set with a data.frame, NOT a bare factor.

```r
library(RADAR)

radar <- countReads(
    samplenames  = c('ctrl_rep1', 'ctrl_rep2', 'ctrl_rep3', 'treat_rep1', 'treat_rep2', 'treat_rep3'),
    gtf          = 'refs/annotation.gtf',
    bamFolder    = 'aligned_radar/',
    modification = 'm6A',
    strandToKeep = 'opposite',
    threads      = 8
)

radar <- normalizeLibrary(radar)
radar <- adjustExprLevel(radar)

variable(radar) <- data.frame(group = c('ctrl', 'ctrl', 'ctrl', 'treat', 'treat', 'treat'))

radar <- filterBins(radar, minCountsCutOff = 15)
radar <- diffIP(radar)

result <- reportResult(radar, cutoff = 0.1, Beta_cutoff = 0.5)
sig <- result[result$padj < 0.05 & abs(result$logFC) > 0.5, ]
nrow(sig)
```

`reportResult` thresholds (`cutoff` = p-value cutoff; `Beta_cutoff` = effect-size cutoff in beta units) are RADAR-specific; convert to the project's standard reporting thresholds downstream. The `aligned_radar/` directory should contain BAMs with RADAR's expected naming (`<sample>.input.bam`, `<sample>.m6A.bam`).

## Volcano Plot of Differential Peaks

**Goal:** Visualise the differential peak set with effect size on the x-axis and statistical significance on the y-axis; flag peaks passing |log2FC| and FDR thresholds.

**Approach:** Standard ggplot2 volcano with colour-coded significance and threshold lines.

```r
library(ggplot2)

diff_table$significance <- with(diff_table,
    ifelse(padj < 0.05 & abs(log2FC) > 0.5, 'differential', 'not_sig'))

ggplot(diff_table, aes(x=log2FC, y=-log10(padj), colour=significance)) +
    geom_point(alpha=0.5, size=0.8) +
    geom_vline(xintercept=c(-0.5, 0.5), linetype='dashed') +
    geom_hline(yintercept=-log10(0.05), linetype='dashed') +
    scale_colour_manual(values=c(differential='red', not_sig='grey60')) +
    labs(x='log2 (treat / ctrl) MeRIP enrichment ratio',
         y='-log10 (FDR)',
         title='Differential m6A peaks: ctrl vs treat',
         caption='Per-window IP/input ratio normalised; not absolute stoichiometry') +
    theme_minimal()
```

The caption is intentional: MeRIP differential reports CHANGES IN ENRICHMENT RATIO, NOT changes in absolute stoichiometry. For stoichiometry claims, cross-validate with GLORI / SAC-seq / m6Anet.

## Per-Method Failure Modes

### Reporting "hyper-methylation" without orthogonal calibration

**Trigger:** "Peak X shows hyper-methylation in treatment" inferred from MeRIP IP fold-change alone.

**Mechanism:** MeRIP IP fold-change conflates per-molecule methylation stoichiometry, transcript abundance, and IP efficiency variation between libraries. An IP fold-change increase can reflect any or all of these.

**Symptom:** Reported m6A "hyper-methylation" tracks RNA-seq expression changes between conditions; reverse-direction effects when properly normalised against input.

**Fix:** Use "increased / decreased enrichment" terminology for MeRIP-only studies. Reserve "hyper- / hypo-methylated" for studies with absolute quantification orthogonal validation (GLORI, SAC-seq, MAZTER-seq, m6Anet per-read). For high-stakes claims at named loci, run GLORI on a subset of conditions.

### Effect-size threshold absence

**Trigger:** Reporting "1,500 differential m6A peaks" with FDR < 0.05 (uncorrected p-value or naive multiple testing) and no effect-size filter.

**Mechanism:** With sufficient sequencing depth, MeRIP-seq has high statistical power to detect very small (~1.1-1.2x) IP-ratio changes that lie within antibody / technical noise. McIntyre 2020 *Sci Rep* 10:6590 showed these changes do not replicate.

**Symptom:** Differential peak set has many peaks with small effect sizes; replication in an independent study recovers <30% of original calls.

**Fix:** Apply effect-size filter (|log2FC| >= 0.5 minimum, often >= 1) AND adjusted p-value (FDR < 0.05) AND replicate-direction concordance. Differential peaks should be reported with effect size, not just p-value. Report effect-size distribution alongside peak count.

### Underpowered N=2 design

**Trigger:** Differential m6A study with N=2 IP and N=2 input per condition.

**Mechanism:** Per McIntyre 2020 and many subsequent benchmarks, MeRIP replicate variance is high; N=2 estimates of dispersion are unreliable; differential calls are unstable.

**Symptom:** Many "differential" peaks; volcano plot dense; small fraction replicates in held-out replicate.

**Fix:** Minimum N=3 per condition (per condition per IP/input arm = 12 BAMs for a 2-condition study); N=4-5 preferred for high-stakes claims. Underpowered studies should report effect-size-only filtered subsets (the most extreme peaks) and acknowledge the noise floor explicitly.

### Batch confounded with condition (antibody lot, IP day)

**Trigger:** Control samples processed in batch 1 with antibody lot A; treatment samples processed in batch 2 with antibody lot B.

**Mechanism:** Anti-m6A antibody lots have batch-to-batch variability in pulldown efficiency and m6A-vs-m6Am cross-reactivity. Pooling cross-batch counts in a differential model attributes batch-effect to condition.

**Symptom:** "Differential" peaks at high-abundance transcripts; effect sizes track batch rather than condition; reanalysis with `batch` in the model removes most differential peaks.

**Fix:** Include `antibody_lot` / `batch` / `prep_day` as a fixed effect in a DESeq2 / edgeR model on featureCounts-on-peaks counts; OR run exomePeak2 separately per lot and meta-analyse the per-lot differential peak sets; OR re-design the experiment to avoid lot-condition confounding. exomePeak2's top-level API does NOT accept arbitrary covariates — DESeq2 / edgeR is the route when covariate handling is required.

### exomePeak2 invoked with a fabricated `mode=` argument

**Trigger:** `exomePeak2(..., mode='differential')` OR `exomePeak2(..., mode='diff_peak')` returns "unused argument" error.

**Mechanism:** exomePeak2 has NO `mode=` argument. Differential is triggered by populating `bam_treated_ip` and `bam_treated_input` alongside the standard `bam_ip` and `bam_input` (control arm). The `peak_calling_mode` argument is unrelated — it accepts `'exon' | 'full_transcript' | 'whole_genome'` and controls locus scope, not differential-vs-non-differential.

**Fix:** Populate the four BAM-vector arguments (`bam_ip`, `bam_input`, `bam_treated_ip`, `bam_treated_input`); drop any `mode=` reference; consult `?exomePeak2` for the authoritative signature in the installed version.

### Treating peak count matrices like RNA count matrices in edgeR/DESeq2

**Trigger:** Compute featureCounts at peaks, build a count matrix, run edgeR / DESeq2 on the matrix as if peaks were genes.

**Mechanism:** Peak counts reflect both IP enrichment AND transcript abundance. Generic RNA-seq DE on peak counts mixes the two; size-factor normalisation on IP-only counts loses the input-pair information.

**Fix:** edgeR / DESeq2 on peak counts is defensible ONLY for paired symmetric designs where input is modelled as an offset (per-sample size factor on input counts AND per-sample size factor on IP counts, then differential on the ratio). For most uses, exomePeak2 / QNB / RADAR's purpose-built models are more appropriate.

### Counting reads at peaks WITHOUT featureCounts strand-awareness

**Trigger:** `featureCounts(...)` invoked without `strandSpecific=` flag; or with wrong strand setting.

**Mechanism:** Strand-aware counting matters when the protocol is stranded (most modern MeRIP is unstranded; some are reverse-stranded). Wrong strand counts include antisense reads as if they were sense.

**Fix:** Verify protocol strandedness from sequencing-core notes or by inspecting featureCounts summary at a few transcripts. Pass `strandSpecific=0` (unstranded), `1` (forward), or `2` (reverse) explicitly.

## Reconciliation: When Differential Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| exomePeak2 calls a differential peak; QNB does not | Different dispersion estimates; QNB more conservative at low coverage | Trust intersection; report concordant set as high-confidence |
| Most "differential" peaks fall at high-abundance housekeeping transcripts | Expression / IP-efficiency confound | Check log2FC vs input log2FC; if correlated, batch effect or expression-driven |
| RADAR vs exomePeak2 disagree on direction | Different normalisation (TMM vs internal) | Inspect normalisation diagnostic; choose method aligned with experimental design |
| Differential peaks anti-correlated with RNA-seq DE | Expression conflated with methylation in the differential model | Re-run with stronger input normalisation; consider per-peak ratio normalisation |
| Single differential peak survives across all methods | High-confidence call | Orthogonally validate (GLORI / SAC-seq) at the named locus |
| Differential calls scatter randomly across genome | Underpowered; technical noise dominates | Increase N; apply stricter effect-size filter; report null result honestly |
| Cross-condition peak overlap < 50% before differential | Conditions are biologically very different; OR antibody lot effect | Inspect cross-replicate concordance; check antibody lot metadata |
| Volcano shows extreme outliers at low-coverage peaks | Per-peak variance dominated by Poisson sampling | Filter peaks by minimum coverage (>=30 reads in IP AND input) before differential |

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|----------|-----------|--------------------|
| Minimum biological replicates per condition | 3 (4-5 preferred) | McIntyre 2020 *Sci Rep* 10:6590 — N=2 routinely under-powered |
| FDR threshold | 0.05 | Standard convention |
| Effect-size threshold (|log2FC|) | >= 0.5 minimum; >= 1 stringent | Below 0.5, calls within technical noise floor |
| Minimum coverage per peak window (each IP AND input) | 30 reads | Standard convention; below this, statistical calls noisy |
| Replicate-direction concordance | Same direction in >=2/N replicates | Guardrail against single-replicate artifacts |
| Antibody lot tracking | Mandatory in design matrix when lots differ | Lot confounding is a known false-positive source |
| MeRIP per-window IP/input ratio inflation | log2(IP/input) >= 1 for "enriched"; >=2 for "strongly enriched" | Convention |
| Cross-study peak overlap baseline | ~45% median between labs | McIntyre 2020 *Sci Rep* 10:6590 — bounds inter-study reproducibility |
| Effect size for biological validation | |log2FC| >= 1 AND padj < 0.05 typically used for downstream wet-lab follow-up | Field convention; tighten for low-N studies |
| GLORI orthogonal validation threshold | Stoichiometry change >= 10% at named site | Liu C 2023 *Nat Biotechnol* 41:355 calibration |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| exomePeak2 `mode='differential'` rejected | exomePeak2 has no `mode=` arg; differential is via `bam_treated_ip` + `bam_treated_input` | Populate the four BAM-vector args; consult `?exomePeak2` |
| QNB error "unused argument" | Function signature changed between versions | Pin commit SHA; verify against installed `?qnbtest` |
| RADAR install fails | GitHub-only; requires devtools and specific Bioconductor deps | `devtools::install_github('scottzijiezhang/RADAR')`; check Bioconductor requirements |
| featureCounts returns zero counts | Strand setting wrong; OR peak BED has different chromosome naming than BAM | Verify `strandSpecific=`; reconcile chromosome names |
| Volcano plot all peaks near origin | Low effect sizes; technical noise dominant | Check input normalisation; increase N; report null result if appropriate |
| FDR-significant but small effect size | Large dataset finds small differences with high power | Apply effect-size filter; report effect-size distribution |
| Many differential peaks track expression changes | Input normalisation insufficient | Re-run with stronger input adjustment; OR use ratio-of-ratios |
| edgeR `estimateDisp()` fails at N=2 | Small-N dispersion estimation collapses | Use QNB instead; designed for this case |
| MeTDiff install fails | GitHub-only, bundled with MeTPeak | `devtools::install_github('compgenomics/MeTPeak')` |
| exomePeak2 result has no log2FC / padj columns | `bam_treated_ip` / `bam_treated_input` were not populated; only ran peak calling on the control arm | Pass all four BAM-vector arguments (`bam_ip`, `bam_input`, `bam_treated_ip`, `bam_treated_input`) to trigger differential output |
| Per-peak boxplot shows huge within-condition variance | High biological noise; OR one replicate is an outlier | Inspect plotCorrelation in merip-preprocessing for outlier; consider exclusion |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "How many replicates per condition?" | N=3 minimum; N=4-5 preferred; rationale McIntyre 2020 |
| "What's the effect-size threshold?" | |log2FC| >= 0.5 minimum; results table reports effect size alongside FDR |
| "Was batch / antibody lot controlled for?" | Yes — `antibody_lot` included as fixed effect in DESeq2 model on featureCounts-on-peaks counts (exomePeak2's top-level API does not accept covariates); per-lot exomePeak2 + meta-analysis when DESeq2 path infeasible; lot-condition confounding assessed |
| "Does the differential signal track expression changes?" | Cross-checked log2FC vs input log2FC per peak; only peaks with strong IP/input ratio shift reported as differential |
| "Was orthogonal validation done?" | Top hits orthogonally validated via GLORI / m6Anet / per-locus assay |
| "Why exomePeak2 over QNB?" | exomePeak2 default for standard 3-vs-3; QNB used for small-N sensitivity analyses; both reported as concordance check |
| "What about absolute stoichiometry?" | MeRIP differential reports relative enrichment changes; absolute stoichiometry requires GLORI / SAC-seq |
| "Was the right normalisation used?" | Per-window IP/input ratio normalisation; exomePeak2 internal; alternative TMM (RADAR) compared |
| "How does this replicate in independent studies?" | Cross-study peak overlap reported; differential subset checked against published m6A-Atlas |
| "Why not edgeR / DESeq2?" | Generic RNA-seq DE on peak counts loses IP/input pairing structure; used only for sensitivity analysis with paired symmetric design |

## References

- Dominissini D, Moshitch-Moshkovitz S, Schwartz S et al (2012) Topology of the human and mouse m6A RNA methylomes revealed by m6A-seq. *Nature* 485(7397):201-206. doi:10.1038/nature11112
- Meyer KD, Saletore Y, Zumbo P, Elemento O, Mason CE, Jaffrey SR (2012) Comprehensive analysis of mRNA methylation reveals enrichment in 3' UTRs and near stop codons. *Cell* 149(7):1635-1646. doi:10.1016/j.cell.2012.05.003
- Liu L, Zhang SW, Huang Y, Meng J (2017) QNB: differential RNA methylation analysis for count-based small-sample sequencing data with a quad-negative binomial model. *BMC Bioinformatics* 18(1):387. doi:10.1186/s12859-017-1808-4
- Cui X, Meng J, Zhang S, Chen Y, Huang Y (2016) A novel algorithm for calling mRNA m6A peaks by modeling biological variances in MeRIP-seq data. *Bioinformatics* 32(12):i378-i385. doi:10.1093/bioinformatics/btw281
- Liu L, Zhang SW, Gao F et al (2016) DRME: count-based differential RNA methylation analysis at small sample size scenario. *Anal Biochem* 499:15-23. doi:10.1016/j.ab.2016.01.014
- Zhang Z, Zhan Q, Eckert M et al (2019) RADAR: differential analysis of MeRIP-seq data with a random effect model. *Genome Biol* 20(1):294. doi:10.1186/s13059-019-1915-9
- Meng J, Lu Z, Liu H et al (2014) A protocol for RNA methylation differential analysis with MeRIP-Seq data and exomePeak R/Bioconductor package. *Methods* 69(3):274-281. doi:10.1016/j.ymeth.2014.06.008
- Liu J, Zhang Z, Meng J et al (2022) exomePeak2: a peak calling and differential analysis tool for MeRIP-Seq with bias awareness. *NAR Genom Bioinform* 4(3):lqac046. doi:10.1093/nargab/lqac046
- McIntyre ABR, Gokhale NS, Cerchietti L, Jaffrey SR, Horner SM, Mason CE (2020) Limits in the detection of m6A changes using MeRIP/m6A-seq. *Sci Rep* 10(1):6590. doi:10.1038/s41598-020-63355-3
- Liu C, Sun H, Yi Y et al (2023) Absolute quantification of single-base m6A methylation in the mammalian transcriptome using GLORI. *Nat Biotechnol* 41(3):355-366. doi:10.1038/s41587-022-01487-9
- Hu L, Liu S, Peng Y et al (2022) m6A RNA modifications are measured at single-base resolution across the mammalian transcriptome. *Nat Biotechnol* 40(8):1210-1219. doi:10.1038/s41587-022-01243-z
- Garcia-Campos MA, Edelheit S, Toth U et al (2019) Deciphering the m6A code via antibody-independent quantitative profiling. *Cell* 178(3):731-747.e16. doi:10.1016/j.cell.2019.06.013
- Robinson MD, McCarthy DJ, Smyth GK (2010) edgeR: a Bioconductor package for differential expression analysis of digital gene expression data. *Bioinformatics* 26(1):139-140. doi:10.1093/bioinformatics/btp616
- Love MI, Huber W, Anders S (2014) Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biol* 15(12):550. doi:10.1186/s13059-014-0550-8
- Liao Y, Smyth GK, Shi W (2014) featureCounts: an efficient general purpose program for assigning sequence reads to genomic features. *Bioinformatics* 30(7):923-930. doi:10.1093/bioinformatics/btt656

## Related Skills

- merip-preprocessing - Upstream IP/input BAM preparation; design-matrix metadata (antibody lot, batch) originates here
- m6a-peak-calling - Peak calling step that produces input to differential analysis
- m6anet-analysis - Orthogonal ONT-direct-RNA validation for stoichiometry claims at high-stakes loci
- modification-visualization - Volcano / MA / per-peak boxplot rendering of differential results
- differential-expression/deseq2-basics - Canonical DE design philosophy; m6a-differential defers to this for general design-matrix patterns
- differential-expression/de-results - Post-DE interpretation, ranking, gene-list extraction
- differential-expression/edger-basics - edgeR fundamentals for the paired-symmetric sensitivity case
- chip-seq/differential-binding - Closest sibling for IP-vs-input differential binding (general framework)
- rna-quantification/featurecounts-counting - Peak count matrix construction
- data-visualization/volcano-and-ma-plots - Volcano + MA plot recipes
- data-visualization/multipanel-figures - Figure assembly
- pathway-analysis/go-enrichment - GO enrichment on differential-peak-bearing gene lists
- workflows/rnaseq-to-de - End-to-end pipeline orchestration patterns
<!-- END FILE: epitranscriptomics/m6a-differential/SKILL.md -->

## 子目录：epitranscriptomics/m6a-peak-calling

<!-- BEGIN FILE: epitranscriptomics/m6a-peak-calling/SKILL.md -->
---
name: bio-epitranscriptomics-m6a-peak-calling
description: Calls m6A peaks from MeRIP-seq / m6A-seq paired IP-vs-input data using exomePeak2 (transcript-aware, GC-bias-corrected Poisson GLM), MeTPeak (HMM over sliding windows), MACS3/MACS2 with --nomodel --broad --keep-dup all (genome-wide broad alternative), and DRACH motif enrichment via HOMER or ggseqlogo as a sanity check (NOT a filter). Covers BED12 vs narrowPeak output, exonic vs intronic peak handling, multi-tool reconciliation (intersection vs union), the m6A-vs-m6Am ambiguity at 5'UTR peaks that antibody methods cannot resolve, and orthogonal validation (miCLIP/GLORI/m6A-SAC-seq/m6Anet). Use when calling peaks from paired IP/input genome BAMs, choosing exomePeak2 (transcript-aware default) vs MACS3 (broad genomic) vs MeTPeak (HMM-smoothed low-coverage), confirming DRACH enrichment as a sanity check on the peak set, reconciling differing peak sets across tools, validating MeRIP peaks against single-base methods, interpreting 5' peaks where m6Am contamination is possible, or recommending a consensus strategy.
tool_type: mixed
primary_tool: exomePeak2
---

## Version Compatibility

Reference examples tested with: exomePeak2 1.14+ (Bioconductor 3.18+), MeTPeak (GitHub commit SHA-pinned; no Bioconductor release), MACS3 3.0+, MACS2 2.2.9+, samtools 1.19+, GenomicFeatures 1.54+, BSgenome.Hsapiens.UCSC.hg38 1.4+, HOMER 4.11+, ggseqlogo 0.2+, rtracklayer 1.62+, GenomicRanges 1.54+, ChIPseeker 1.38+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('exomePeak2')` then `?exomePeak2` to verify parameters
- CLI: `macs3 callpeak --help`, `findMotifsGenome.pl` to confirm flags

If R throws `unused argument` or `argument is missing`, the exomePeak2 / MeTPeak API may have moved between releases; consult `?exomePeak2` and the installed package's NAMESPACE.

exomePeak2 differential is triggered by populating `bam_treated_ip` / `bam_treated_input` alongside the control-arm `bam_ip` / `bam_input` (see m6a-differential); there is NO `mode=` argument. MeTPeak is GitHub-only and unversioned — pin a commit SHA in any reproducible analysis; defaults are `WINDOW_WIDTH=50, SLIDING_STEP=50, FRAGMENT_LENGTH=100`. MACS3 supersedes MACS2 in development activity but both are widely used; default `--keep-dup` is 1 in BOTH and MUST be overridden to `all` for MeRIP. HOMER `findMotifsGenome.pl` is mature; the `-rna` flag is the RNA-mode entry.

# m6A Peak Calling

**"Find m6A sites in my MeRIP data"** -> Compare paired IP and input read distributions per transcript window, call windows with statistically significant IP enrichment as peaks, annotate against transcript features (5'UTR / CDS / 3'UTR / stop-codon), and confirm DRACH motif enrichment on the peak set relative to background as a sanity check that the antibody-IP worked. CRITICAL: DRACH is a sanity check on the WHOLE peak set, NOT a filter on individual peaks (filtering by DRACH drops 5-10% of real m6A sites and creates circular validation). Equally critical: peaks within ~50 nt of TSS may be PCIF1 m6Am, not METTL3 m6A — anti-m6A antibodies cross-react.

- R: `exomePeak2::exomePeak2()` -- transcript-aware GC-corrected GLM (field default)
- R: `MeTPeak::metpeak()` -- HMM-smoothed sliding-window alternative
- CLI: `macs3 callpeak --nomodel --keep-dup all --broad` -- broad genomic alternative
- CLI: `findMotifsGenome.pl peaks.bed -rna` (HOMER) -- DRACH enrichment sanity check
- R: `ggseqlogo::ggseqlogo()` -- peak-centre 5-mer sequence logo

## The Single Most Important Modern Insight -- MeRIP cannot distinguish m6A from m6Am near the 5' end, and DRACH is a sanity check not a filter

Anti-m6A antibodies (Synaptic Systems 202-003, Abcam ab151230, NEB EpiMark E1610, Cell Signaling 56593, Active Motif 61755) cross-react with m6Am — the cap-adjacent N6,2'-O-dimethyladenosine at the +1 nucleotide of capped mRNAs, installed by PCIF1 / CAPAM (Akichika 2019 *Science* 363:eaav0080; Boulias 2019 *Mol Cell* 75:631). METTL3 / METTL14 do NOT methylate the cap-adjacent position; PCIF1 does. Peaks within the first ~50 nt of a transcript are ambiguous between m6A and m6Am. METTL3-KO will REMOVE internal m6A peaks but LEAVE the cap m6Am peaks intact, which has caused multiple papers to mis-attribute METTL3-independent peaks to non-canonical writers when they are really PCIF1 m6Am. Linder 2015 *Nat Methods* 12:767 (miCLIP, the antibody-based single-base method) explicitly notes the cross-reactivity. Separately: while ~70% of mammalian METTL3-deposited m6A sites sit within the DRACH consensus (D=A/G/U, R=A/G, A=methylated, C=C, H=A/C/U), a non-trivial fraction are non-DRACH. Post-hoc filtering peaks by DRACH content drops real m6A peaks; DRACH should be reported as enrichment-relative-to-background (HOMER / MEME / ggseqlogo) on the PEAK SET as a whole, NOT as a per-peak filter. For unambiguous internal-m6A studies, restrict analysis to peaks past the first ~50 nt AND validate at high-stakes sites with an orthogonal method (miCLIP for single-base antibody validation; GLORI Liu 2023 *Nat Biotechnol* 41:355 for absolute stoichiometry; m6A-SAC-seq Hu 2022 *Nat Biotechnol* 40:1210; m6Anet for ONT direct-RNA confirmation).

## Algorithmic Taxonomy

| Tool / mode | Mechanism | Inputs | Output | Strength | Fails when |
|-------------|-----------|--------|--------|----------|------------|
| exomePeak2 (Liu 2022 *NAR Genom Bioinform* 4:lqac046) | Transcript-windowed Poisson GLM with on-the-fly GC-bias correction; supersedes exomePeak v1 | paired IP/input BAM + TxDb / GTF | BED12 + RDS + per-peak fold-change / FDR | Transcript-aware; GC-aware; integrates motif annotation; modern field default | Slow on very large datasets; argument signatures shift between Bioconductor minor releases — verify against `?exomePeak2` |
| MeTPeak (Cui 2016 *Bioinformatics* 32:i378) | HMM over sliding windows with Beta-binomial emission per window | paired IP/input BAM + GTF (or TxDb) | BED12 | HMM smooths spatial dependency; better at low coverage | GitHub-only; unversioned; default window/step is 50/50 not the small values some tutorials suggest |
| MACS3 / MACS2 broad mode (Zhang 2008 *Genome Biol* 9:R137) | Sliding-window negative-binomial test; `--broad` extends; `--nomodel` disables ChIP fragment-shift model | paired IP/input BAM | narrowPeak / broadPeak | Battle-tested ChIP-seq lineage; very fast | Not transcript-aware; misses GC-confounded peaks; default `--keep-dup 1` collapses MeRIP signal at high-coverage transcripts |
| MeRIPtools (R wrapper) | Bundles exomePeak / MeTPeak / motif / annotation steps | FASTQ -> peaks pipeline | full report | Reproducible end-to-end | Less flexibility than calling tools separately |
| MoAIMS | Mixture model alternative | paired IP/input BAM | peaks | Smaller user base; less benchmarked | Niche use |
| m6Aboost (R) | Boost peak-calling sensitivity by leveraging DRACH motif as a prior | paired IP/input BAM + motif file | refined peak set | Improves sensitivity in low-coverage regions | Builds DRACH into the calling — DON'T use as evidence for DRACH enrichment downstream (circular) |
| m6ACali (recent ML peak filter; verify current citation against the project repo) | ML-based false-peak filter trained on exomePeak2 + MACS2 outputs across many cell lines | called peak set + IP/input BAM | refined peak set | Modern QC layer; cuts antibody artifact peaks | Trained on specific antibody clones; verify it generalises to the antibody used |

## Decision Tree by Scenario

| Scenario | Recommended | Why wrong choices fail |
|----------|-------------|------------------------|
| Standard mammalian MeRIP, 3+ replicates per arm | exomePeak2 + DRACH confirmation; reconcile with MeTPeak as a second opinion | MACS3 misses GC-confounded peaks; MeTPeak alone gives less GC awareness |
| Viral / kilobase-broad peaks | MACS3 `--broad --broad-cutoff 0.1 --keep-dup all` | exomePeak2 splits broad enrichment into many small per-window peaks |
| Low-coverage / scarce-sample MeRIP | MeTPeak HMM smooths; exomePeak2 as cross-check | MACS3 default loses sensitivity at low coverage |
| Need single-nucleotide resolution | NOT MeRIP -- switch to miCLIP, m6Anet, GLORI, SAC-seq | MeRIP windows are ~100-200 nt; cannot resolve to base |
| 5'UTR / cap-proximal peaks | Run normally BUT flag 5' peaks (within ~50 nt of TSS) as m6A-or-m6Am ambiguous; validate with PCIF1-KO if available | Antibody cross-reacts with m6Am; cannot assign without orthogonal data |
| Cross-tool reconciliation | Call with exomePeak2 + MeTPeak + MACS3 broad; intersect (NOT union) for high-confidence; report each separately | Union inflates false-positive rate; single-tool reports under-call ~30% of consensus peaks |
| Validation of high-stakes peak set | Cross-check against published m6A-Atlas / REPIC databases; orthogonal validation at top hits (miCLIP / GLORI / m6A-SAC-seq) | Single-method-single-study peaks have ~50% inter-study overlap (McIntyre 2020) |
| Wanting absolute stoichiometry | NOT MeRIP -- use GLORI (Liu 2023 *Nat Biotechnol*), SAC-seq (Hu 2022), eTAM-seq (Xiao 2023) | MeRIP IP fold-change is relative, not absolute |
| METTL3-KO validation experiment | Call peaks in WT and KO; peaks that DISAPPEAR in KO are m6A-dependent; peaks that REMAIN are antibody artifacts OR m6Am OR non-METTL3 modifications (METTL16, METTL5) | Calling only WT and assuming all peaks are m6A; many are not |
| Anti-m6A vs anti-m6Am specific analysis | For internal m6A only: exclude TSS-proximal peaks AND use GLORI / SAC-seq orthogonal validation; for m6Am specifically: m6Am-seq (Sun H 2021 *Nat Commun* 12:4778), m6ACE-seq, or PCIF1-KO subtraction | Antibody alone CANNOT distinguish — this is a chemistry problem, not a software problem |

Methodology evolves; before any high-stakes peak-calling analysis, web-search "exomePeak2 Bioconductor release notes" and "MeRIP peak caller benchmark 2024" for current consensus parameters.

## exomePeak2 Standard Workflow

**Goal:** Produce a transcript-aware set of m6A peaks with FDR and IP/input fold-change from paired IP/input genome BAM files, suitable as input to differential analysis, motif scanning, or downstream visualisation.

**Approach:** Build a TxDb from the matched GTF; pass paired IP/input BAM vectors with `bam_ip` and `bam_input`; let exomePeak2 handle GC-bias correction internally; export BED12 + RDS for downstream use; annotate against transcript features.

```r
library(exomePeak2)
library(GenomicFeatures)
library(BSgenome.Hsapiens.UCSC.hg38)

txdb <- makeTxDbFromGFF('refs/annotation.gtf', format='gtf')

result <- exomePeak2(
    bam_ip       = c('aligned/IP_rep1.bam', 'aligned/IP_rep2.bam', 'aligned/IP_rep3.bam'),
    bam_input    = c('aligned/Input_rep1.bam', 'aligned/Input_rep2.bam', 'aligned/Input_rep3.bam'),
    txdb         = txdb,
    genome       = BSgenome.Hsapiens.UCSC.hg38,
    paired_end   = TRUE,
    library_type = 'unstranded',
    save_dir     = 'exomepeak2_output',
    experiment_name = 'm6a_run1'
)

# Inspect peaks: GRanges with metadata
peaks <- result
length(peaks)
head(as.data.frame(peaks))
```

`exomePeak2()` writes BED12 + RDS + per-peak fold-change / FDR to `save_dir/experiment_name/`. The `txdb` argument is the canonical interface; older tutorials use `gff=` (path) which is deprecated. `BSgenome` is required for GC correction; if unavailable, exomePeak2 falls back to a less-accurate GC-uncorrected mode.

## MeTPeak HMM-Smoothed Alternative

**Goal:** Call peaks with HMM smoothing across spatial windows, useful when coverage is low or when peak boundaries are ambiguous from per-window negative-binomial tests alone.

**Approach:** MeTPeak accepts IP and INPUT BAM vectors plus either a GTF file path (`GENE_ANNO_GTF=`) or a TxDb object (`TXDB=`); defaults are `WINDOW_WIDTH=50, SLIDING_STEP=50, FRAGMENT_LENGTH=100, MINIMAL_PEAK_LENGTH=FRAGMENT_LENGTH/2, MINIMAL_MAPQ=30`. The example below uses GTF input with explicit defaults shown for transparency; adjust only with rationale.

```r
library(MeTPeak)

metpeak(
    IP_BAM              = c('aligned/IP_rep1.bam', 'aligned/IP_rep2.bam', 'aligned/IP_rep3.bam'),
    INPUT_BAM           = c('aligned/Input_rep1.bam', 'aligned/Input_rep2.bam', 'aligned/Input_rep3.bam'),
    GENE_ANNO_GTF       = 'refs/annotation.gtf',
    OUTPUT_DIR          = 'metpeak_output',
    EXPERIMENT_NAME     = 'm6a_run1',
    WINDOW_WIDTH        = 50,
    SLIDING_STEP        = 50,
    FRAGMENT_LENGTH     = 100,
    MINIMAL_PEAK_LENGTH = 50,
    PEAK_CUTOFF_PVALUE  = 1e-5,
    PEAK_CUTOFF_FDR     = 0.05,
    FOLD_ENRICHMENT     = 1
)
```

MeTPeak accepts either `GENE_ANNO_GTF=` (a file path) or `TXDB=` (a TxDb object); the GTF path is the more common usage and is documented in the GitHub README. Output BED12 is at `OUTPUT_DIR/EXPERIMENT_NAME/peak.bed`. MeTPeak is GitHub-only (`compgenomics/MeTPeak`) and unversioned; pin a commit SHA in reproducible analyses.

## MACS3 Broad-Peak Alternative

**Goal:** Call broad MeRIP peaks across the genome using the ChIP-seq sliding-window negative-binomial framework; useful for viral genomes where peaks span kilobases, or as a cross-caller second opinion.

**Approach:** MACS3 `callpeak` with `--nomodel --extsize 150 --keep-dup all --broad`. The `--nomodel` flag disables the ChIP-seq fragment-shift model (designed for DNA); `--keep-dup all` is REQUIRED because MACS3 default deduplicates and collapses MeRIP signal at high-coverage transcripts.

```bash
macs3 callpeak \
    --treatment aligned/IP_rep1.bam aligned/IP_rep2.bam aligned/IP_rep3.bam \
    --control   aligned/Input_rep1.bam aligned/Input_rep2.bam aligned/Input_rep3.bam \
    --format BAMPE \
    --gsize hs \
    --nomodel \
    --extsize 150 \
    --keep-dup all \
    --broad \
    --broad-cutoff 0.1 \
    --qvalue 0.05 \
    --outdir macs3_output \
    --name m6a_run1
```

`--keep-dup all` is non-negotiable for MeRIP; the default `--keep-dup 1` (keep one read per position) destroys real signal. `--broad` and `--broad-cutoff 0.1` extend narrow peaks into broader regions, appropriate for MeRIP fragments. Output: narrowPeak + broadPeak + gappedPeak files in `macs3_output/`.

## DRACH Motif Confirmation (Sanity Check, NOT a Filter)

**Goal:** Confirm that the called peak set is enriched for the DRACH consensus motif relative to genomic background, validating antibody specificity. NEVER post-hoc remove individual non-DRACH peaks.

**Approach:** Run HOMER `findMotifsGenome.pl` with `-rna` mode on peak centres ±50 bp against a length-matched random-shuffled background; expect DRACH-like consensus in the top motifs with E-value < 1e-50 for a well-behaved MeRIP dataset.

```bash
findMotifsGenome.pl \
    exomepeak2_output/m6a_run1/peaks.bed \
    hg38 \
    motif_output \
    -rna \
    -size 100 \
    -len 5,6 \
    -p 8
```

```r
library(Biostrings)
library(BSgenome.Hsapiens.UCSC.hg38)
library(ggseqlogo)
library(rtracklayer)

peaks <- import('exomepeak2_output/m6a_run1/peaks.bed')

peak_centres <- resize(peaks, width=5, fix='center')
genome <- BSgenome.Hsapiens.UCSC.hg38
seqs <- as.character(getSeq(genome, peak_centres))

ggseqlogo(seqs, method='probability') +
    ggplot2::labs(title='Peak-centre 5-mer (DRACH consensus expected)')
```

If DRACH enrichment is NOT observed in the peak set, the IP failed OR the wrong antibody was used OR the assay actually captured a different modification (m6A is centred in coding regions / 3'UTR; m1A is centred at TSS — different metagene signature). Do NOT proceed to differential analysis until DRACH is confirmed on the peak set as a whole.

## Multi-Tool Consensus

**Goal:** Build a high-confidence peak set by intersecting multiple peak callers run on the same data; report both per-tool peak counts and the intersection.

**Approach:** Use `bedtools intersect` to combine exomePeak2, MeTPeak, and MACS3 broadPeak outputs; require at least 2-of-3 caller agreement for the high-confidence set.

```bash
bedtools intersect \
    -a exomepeak2_output/m6a_run1/peaks.bed \
    -b metpeak_output/m6a_run1/peak.bed macs3_output/m6a_run1_peaks.broadPeak \
    -wa \
    -u \
    -f 0.5 > consensus_at_least_2of3.bed

wc -l \
    exomepeak2_output/m6a_run1/peaks.bed \
    metpeak_output/m6a_run1/peak.bed \
    macs3_output/m6a_run1_peaks.broadPeak \
    consensus_at_least_2of3.bed
```

Intersection (consensus) is the conservative choice; union inflates the false-positive rate (every caller's idiosyncratic false positives propagate). For published analyses, report both per-tool count AND consensus count; the ratio is a useful caller-agreement metric.

## Per-Method Failure Modes

### Anti-m6A antibody cross-reacts with m6Am at 5' peaks

**Trigger:** Peak called at the very 5' end of a transcript (within ~50 nt of TSS), attributed to METTL3-deposited internal m6A.

**Mechanism:** Anti-m6A antibodies cross-react with m6Am (the cap-adjacent N6,2'-O-dimethyladenosine at the +1 nucleotide of capped mRNAs), installed by PCIF1 / CAPAM (Akichika 2019 *Science* 363:eaav0080). METTL3 / METTL14 do NOT methylate the cap-adjacent position. Linder 2015 *Nat Methods* 12:767 explicitly noted the cross-reactivity; Mauer 2017 *Nature* 541:371 deepened the m6Am story.

**Symptom:** 5' peaks remain in METTL3-KO cells; agent infers METTL3-independent m6A writers when the peaks are really PCIF1 m6Am.

**Fix:** Flag peaks within ~50 nt of TSS as m6A-or-m6Am ambiguous. For unambiguous internal-m6A studies, exclude TSS-proximal peaks; for m6Am-specific studies, use PCIF1-KO subtraction or m6Am-seq (Sun H 2021); for orthogonal stoichiometric resolution, use GLORI / SAC-seq.

### Peaks called at GC-extreme transcripts by MACS3 but not exomePeak2

**Trigger:** MACS3 broadPeak output has peaks at high-GC or low-GC transcripts that exomePeak2 does NOT call on the same BAMs.

**Mechanism:** exomePeak2 implements internal GC-bias correction; MACS3 does not. The IP step has GC bias because anti-m6A antibody pull-down efficiency varies with local GC content. MACS3 attributes GC-driven IP enrichment to true methylation; exomePeak2 corrects for it.

**Fix:** Trust exomePeak2 for transcript-aware analyses. Use MACS3 only as a second opinion or for broad / viral analyses. If a MACS3-only peak is biologically interesting, validate orthogonally.

### DRACH filtering applied post-hoc

**Trigger:** Filtering called MeRIP peaks to retain only those containing a DRACH motif within the peak window.

**Mechanism:** ~70% of mammalian METTL3-deposited m6A sites sit within DRACH (Linder 2015), but a non-trivial fraction are non-DRACH. MeRIP peaks span ~100-200 nt; the methylated A is somewhere within the window but the peak boundary is not the modification position. Filtering by "no DRACH in window" rejects real peaks where DRACH sits at the edge or where the m6A is non-DRACH. The filter also creates circular validation — the filtered set is enriched for DRACH by construction.

**Symptom:** Peak count drops 30-50% after DRACH filtering; reviewers note the filter is not a standard convention.

**Fix:** Report DRACH enrichment as a SANITY CHECK on the peak set (HOMER E-value < 1e-50 expected) — never as a per-peak filter. For single-nucleotide methods (miCLIP, m6Anet, GLORI), the DRACH constraint is built into the calling model and need not be re-applied.

### MACS3 default `--keep-dup 1` on MeRIP

**Trigger:** MACS3 invoked without `--keep-dup all`; default behaviour is to retain one read per position.

**Mechanism:** MeRIP libraries have NO UMI (standard protocol); positional duplicates in MeRIP are a mix of PCR duplicates and biological re-sampling of high-coverage transcripts. Default `--keep-dup 1` collapses the latter and destroys real signal at the most-abundant transcripts.

**Symptom:** MACS3 reports very few peaks at housekeeping genes (GAPDH, ACTB) despite obvious IP enrichment in IGV; peak count drops 5-20x compared to `--keep-dup all`.

**Fix:** Always pass `--keep-dup all` to MACS3 / MACS2 for MeRIP. This is the same logic as the do-NOT-dedup rule in merip-preprocessing.

### MeTPeak called with wrong argument name for annotation

**Trigger:** `metpeak(IP_BAM=..., INPUT_BAM=..., txdb=txdb_object)` (lowercase `txdb=` rather than `TXDB=`).

**Mechanism:** MeTPeak's annotation arguments are `GENE_ANNO_GTF=` (GTF file path) or `TXDB=` (uppercase, TxDb object). Lowercase `txdb=` is not recognised. exomePeak2 uses lowercase `txdb=` instead, which leads to easy confusion between the two skills' APIs.

**Fix:** Pass either `GENE_ANNO_GTF='annotation.gtf'` (string path) or `TXDB=txdb_object` (capitalised). Verify argument casing against the installed MeTPeak source.

### Single-tool peak set reported without cross-caller agreement

**Trigger:** Paper reports "18,234 m6A peaks" from exomePeak2 alone; downstream biology built on this single set.

**Mechanism:** Cross-tool concordance on MeRIP is empirically ~70% between exomePeak2 and MeTPeak on the same BAMs; single-tool reports include ~30% tool-specific calls. McIntyre 2020 *Sci Rep* 10:6590 documents this directly.

**Fix:** Run at least 2 callers (typically exomePeak2 + MeTPeak; or exomePeak2 + MACS3 broad); report the intersection as high-confidence; full per-tool counts as supplementary.

### Transcriptome alignment passed to peak caller

**Trigger:** A transcriptome BAM (reads aligned to a transcripts.fa file) passed to exomePeak2 or MACS3 instead of a genome BAM.

**Mechanism:** Peak callers operate on genome BAMs and use the GTF to project peaks back to transcript features. Transcriptome BAMs have reads in per-transcript coordinates; the GTF cannot resolve these back to genome coordinates without re-alignment.

**Fix:** Align to GENOME with STAR / HISAT2 for downstream MeRIP peak calling (see merip-preprocessing). Transcriptome BAMs are for m6anet-analysis only.

## Reconciliation: When Peak Callers Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| exomePeak2 calls a peak; MACS3 does not | GC-confounded; MACS3 calibration ignores GC | Trust exomePeak2 for transcript-aware analysis |
| MACS3 calls a broad peak; exomePeak2 calls 3-5 sub-peaks | Broad biology (e.g., long 3'UTR); exomePeak2 splits broad enrichment into per-window peaks | Merge exomePeak2 sub-peaks within 200 nt; report as broad |
| miCLIP single-nt site OUTSIDE MeRIP peak window | MeRIP window slightly shifted; OR low-coverage transcript | Inspect MeRIP coverage; consider miCLIP authoritative for single-nt identity |
| m6Anet high-confidence site at non-MeRIP-peak location | Non-DRACH site invisible to MeRIP antibody preferences; OR low MeRIP coverage; OR site is real but stoichiometry too low for MeRIP detection | Trust m6Anet for DRACH-context sites at adequate coverage |
| Two replicates concordant; third diverges | Failed IP in third replicate | Inspect IP enrichment QC in merip-preprocessing for the diverging replicate; consider exclusion |
| GLORI calls a high-stoichiometry site that MeRIP misses | MeRIP under-calls at low-expression transcripts; OR site outside common-core consensus | Trust GLORI for absolute stoichiometry; MeRIP is qualitative |
| exomePeak2 gives different peak counts across Bioconductor releases on same BAMs | Default-parameter or signature shifts between minor Bioconductor releases | Verify against `?exomePeak2`; pin Bioconductor + exomePeak2 version in reproducible analyses |
| MACS3 narrowPeak vs broadPeak give very different counts | `--broad` extends peaks; narrow mode requires strong per-window enrichment | For MeRIP, use `--broad`; broadPeak is the appropriate output format |
| 5' peaks dominate the peak set | High m6Am signal (PCIF1) OR TSS-proximal antibody binding artifact | Flag 5' peaks; restrict downstream to internal peaks for METTL3 biology |

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|----------|-----------|--------------------|
| exomePeak2 default FDR | 0.05 | exomePeak2 default; standard in field |
| exomePeak2 fold-change minimum | log2(IP/input) > 0 (any enrichment) by default; stringent set: log2 > 1 | exomePeak2 default vs commonly-applied stringent threshold |
| MACS3 broad-cutoff for m6A | 0.1 | MACS2/3 default for `--broad` mode |
| MACS3 `--extsize` for MeRIP | 150 | MeRIP fragment length convention |
| MACS3 `--qvalue` | 0.05 | Convention (applies to narrow-peak output; broad-peak file uses `--broad-cutoff` instead) |
| DRACH enrichment E-value (HOMER) | < 1e-50 | Convention for "well-validated antibody dataset"; below this threshold the IP likely failed |
| Minimum coverage per peak window | 30 reads in BOTH IP and Input | Standard convention; below this, statistical calls are noisy |
| Peak reproducibility threshold | >=2 of N replicates | Stringency-vs-recall trade-off; report multiple thresholds |
| 5'UTR peak ambiguity zone | first 50 nt of transcript | Conservative; antibody cross-reactivity with m6Am peaks here |
| Minimum peak length | >=20 nt | Below this, suspect noise or peak-edge artefact |
| MeTPeak default p-value cutoff | 1e-5 | MeTPeak default |
| MeTPeak default FDR cutoff | 0.05 | MeTPeak default |
| MeTPeak `WINDOW_WIDTH` / `SLIDING_STEP` | 50 / 50 (defaults) | MeTPeak GitHub source; do not assume smaller values without rationale |
| MeTPeak `FRAGMENT_LENGTH` | 100 (default) | MeTPeak GitHub source; matches non-stranded MeRIP convention |
| Common-core m6A sites (cross-method) | ~6,000-15,000 in HEK293T | The intersection of MeRIP + miCLIP + GLORI + SAC-seq; peaks outside the common core need orthogonal validation |
| Cross-replicate peak overlap | ~80% within lab; ~30-60% between labs (median ~45%) | McIntyre 2020 *Sci Rep* 10:6590; bounds reproducibility expectations |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| exomePeak2 errors on TxDb chromosome mismatch | BAM uses `chr1`; GTF uses `1` (or reverse) | Verify with `samtools view -H` and `head genes.gtf`; reconcile with `seqlevelsStyle()` in R |
| exomePeak2 reports zero peaks | TxDb built from incorrect GTF; OR `paired_end` flag wrong; OR all peaks below FDR threshold | Verify TxDb covers same chromosomes as BAM; verify `paired_end=TRUE` for PE; relax `pvalue_cutoff` |
| MACS3 reports zero peaks | Default `--keep-dup 1` collapsed signal; OR `--nomodel` not set; OR `--gsize` wrong | Add `--keep-dup all --nomodel`; confirm `--gsize hs` (2.7e9) or `mm` |
| MeTPeak install fails | GitHub-only, requires devtools | `devtools::install_github('compgenomics/MeTPeak')` |
| MeTPeak `metpeak()` error on lowercase `txdb=` | MeTPeak uses uppercase `TXDB=` (TxDb object) or `GENE_ANNO_GTF=` (file path); exomePeak2 uses lowercase `txdb=` — easy to confuse | Use `GENE_ANNO_GTF='annotation.gtf'` or `TXDB=txdb_object` |
| HOMER DRACH motif not detected | Antibody failure OR wrong protocol OR insufficient peaks for motif detection | Re-inspect IP/input fingerprint in merip-preprocessing; verify peak count >>100 |
| Peak file is empty BED | exomePeak2 silently filtered all peaks | Check `pvalue_cutoff` / `fold_enrichment` arguments; lower thresholds |
| Cross-tool peak intersect tiny | Tool-default thresholds differ; OR fragment length parameters differ | Harmonise thresholds across callers; reconcile via IDR-equivalent |
| exomePeak2 takes >24h on whole-genome BAMs | Large BAM + many transcripts | Subset to expressed transcripts; OR use more cores via downstream parallelisation |
| `findMotifsGenome.pl` error on chromosome naming | hg38 vs HG38 vs Hg38 | Use lowercase `hg38` consistently |
| ggseqlogo throws "sequences must be equal length" | Mixed-length sequences passed | Resize peak ranges to fixed width: `resize(peaks, width=5, fix='center')` |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "How many peak callers were used?" | Two minimum (exomePeak2 + MeTPeak or + MACS3); intersection reported as high-confidence; per-tool counts as supplementary |
| "Was filtering by DRACH applied?" | No — DRACH reported as enrichment-on-the-peak-set (HOMER E-value); per-peak DRACH filtering drops 5-10% real m6A sites |
| "How were 5'UTR peaks handled?" | Flagged peaks within 50 nt of TSS as m6A-or-m6Am ambiguous; restricted internal-m6A analyses to peaks past the 5'UTR; cited Linder 2015 / Mauer 2017 cross-reactivity |
| "What's the FDR threshold?" | exomePeak2 default FDR 0.05; MACS3 q-value 0.05; peaks reported with both fold-change and FDR |
| "Was orthogonal validation done?" | High-stakes sites validated against published miCLIP / GLORI / SAC-seq / m6A-Atlas; cross-method overlap reported |
| "Why exomePeak2 over MeTPeak?" | exomePeak2 implements GC-bias correction; MeTPeak does not. For low-coverage datasets MeTPeak HMM smoothing helps; for typical datasets exomePeak2 is the field default |
| "Were failed IPs checked for?" | Replicate IPs inspected via plotFingerprint AND per-transcript IP/input ratio distribution in merip-preprocessing BEFORE peak calling |
| "What's the cross-replicate peak overlap?" | Reported per pair; expect ~80% within-lab per McIntyre 2020 |
| "Was the peak set intersected with m6A-Atlas?" | Yes — common-core overlap reported as a confidence anchor; novel peaks flagged for orthogonal validation |
| "Why weren't m6A-CLIP peaks called here?" | miCLIP / m6A-CLIP single-nucleotide methods live in `clip-seq/peak-calling`; this skill is for fragment-level MeRIP peak calling |

## References

- Dominissini D, Moshitch-Moshkovitz S, Schwartz S et al (2012) Topology of the human and mouse m6A RNA methylomes revealed by m6A-seq. *Nature* 485(7397):201-206. doi:10.1038/nature11112
- Meyer KD, Saletore Y, Zumbo P, Elemento O, Mason CE, Jaffrey SR (2012) Comprehensive analysis of mRNA methylation reveals enrichment in 3' UTRs and near stop codons. *Cell* 149(7):1635-1646. doi:10.1016/j.cell.2012.05.003
- Linder B, Grozhik AV, Olarerin-George AO, Meydan C, Mason CE, Jaffrey SR (2015) Single-nucleotide-resolution mapping of m6A and m6Am throughout the transcriptome. *Nat Methods* 12(8):767-772. doi:10.1038/nmeth.3453
- Mauer J, Luo X, Blanjoie A et al (2017) Reversible methylation of m6Am in the 5' cap controls mRNA stability. *Nature* 541(7637):371-375. doi:10.1038/nature21022
- Liu J, Yue Y, Han D et al (2014) A METTL3-METTL14 complex mediates mammalian nuclear RNA N6-adenosine methylation. *Nat Chem Biol* 10(2):93-95. doi:10.1038/nchembio.1432
- Cui X, Meng J, Zhang S, Chen Y, Huang Y (2016) A novel algorithm for calling mRNA m6A peaks by modeling biological variances in MeRIP-seq data. *Bioinformatics* 32(12):i378-i385. doi:10.1093/bioinformatics/btw281
- Meng J, Lu Z, Liu H, Zhang L, Zhang S, Chen Y, Rao MK, Huang Y (2014) A protocol for RNA methylation differential analysis with MeRIP-Seq data and exomePeak R/Bioconductor package. *Methods* 69(3):274-281. doi:10.1016/j.ymeth.2014.06.008
- Liu J, Zhang Z, Meng J et al (2022) exomePeak2: a peak calling and differential analysis tool for MeRIP-Seq with bias awareness. *NAR Genom Bioinform* 4(3):lqac046. doi:10.1093/nargab/lqac046
- Zhang Y, Liu T, Meyer CA et al (2008) Model-based analysis of ChIP-Seq (MACS). *Genome Biol* 9(9):R137. doi:10.1186/gb-2008-9-9-r137
- Akichika S, Hirano S, Shichino Y et al (2019) Cap-specific terminal N6-methylation of RNA by an RNA polymerase II-associated methyltransferase. *Science* 363(6423):eaav0080. doi:10.1126/science.aav0080
- Boulias K, Toczydłowska-Socha D, Hawley BR et al (2019) Identification of the m6Am methyltransferase PCIF1 reveals the location and functions of m6Am in the transcriptome. *Mol Cell* 75(3):631-643.e8. doi:10.1016/j.molcel.2019.06.006
- Liu C, Sun H, Yi Y et al (2023) Absolute quantification of single-base m6A methylation in the mammalian transcriptome using GLORI. *Nat Biotechnol* 41(3):355-366. doi:10.1038/s41587-022-01487-9
- Hu L, Liu S, Peng Y et al (2022) m6A RNA modifications are measured at single-base resolution across the mammalian transcriptome. *Nat Biotechnol* 40(8):1210-1219. doi:10.1038/s41587-022-01243-z
- Garcia-Campos MA, Edelheit S, Toth U et al (2019) Deciphering the m6A code via antibody-independent quantitative profiling. *Cell* 178(3):731-747.e16. doi:10.1016/j.cell.2019.06.013
- McIntyre ABR, Gokhale NS, Cerchietti L, Jaffrey SR, Horner SM, Mason CE (2020) Limits in the detection of m6A changes using MeRIP/m6A-seq. *Sci Rep* 10(1):6590. doi:10.1038/s41598-020-63355-3
- Heinz S, Benner C, Spann N et al (2010) Simple combinations of lineage-determining transcription factors prime cis-regulatory elements required for macrophage and B cell identities. *Mol Cell* 38(4):576-589. doi:10.1016/j.molcel.2010.05.004

## Related Skills

- merip-preprocessing - IP/input BAM preparation, library complexity QC, and IP enrichment QC upstream of peak calling
- m6a-differential - Compare peak sets between conditions; uses peaks called here as input
- m6anet-analysis - Orthogonal validation of MeRIP peaks via ONT direct-RNA single-nucleotide resolution
- modification-visualization - Metagene, browser-track, and peak-centred heatmap rendering of called peaks
- clip-seq/peak-calling - miCLIP / m6A-CLIP single-nucleotide validation methods (PureCLIP, PEKA, paraclu)
- clip-seq/clip-motif-analysis - Antibody-CLIP motif analysis context for cross-validation
- chip-seq/peak-calling - General sliding-window IP-vs-input peak calling (MACS3 design lineage)
- chip-seq/peak-annotation - Annotation of peaks against gene features (re-usable for m6A)
- read-alignment/star-alignment - Splice-aware STAR alignment defaults referenced by merip-preprocessing
- rna-quantification/featurecounts-counting - Peak count matrix construction (input to m6a-differential)
- pathway-analysis/go-enrichment - GO enrichment on gene lists derived from peak-bearing transcripts
- variant-calling/vcf-basics - Cross-reference m6A peaks against A-to-I edit sites (sometimes confounded)
- data-visualization/multipanel-figures - Combining metagene + heatmap + volcano for figures
<!-- END FILE: epitranscriptomics/m6a-peak-calling/SKILL.md -->

## 子目录：epitranscriptomics/m6anet-analysis

<!-- BEGIN FILE: epitranscriptomics/m6anet-analysis/SKILL.md -->
---
name: bio-epitranscriptomics-m6anet-analysis
description: Detects m6A modifications from Oxford Nanopore direct-RNA-seq (DRS) signal using m6Anet (multiple-instance-learning over DRACH 5-mer signal). Covers the upstream pipeline (Dorado/Guppy basecalling -> minimap2 map-ont -> nanopolish eventalign -> m6anet dataprep -> m6anet inference), per-site vs per-read probability including the mod_ratio stoichiometry column, the DRACH-only constraint, minimum-coverage thresholds (20-50 reads/site), multi-condition comparison via xPore/Nanocompore/ELIGOS, Dorado native modification calling (RNA004, 2024+), and the cDNA-vs-DRS distinction (cDNA Nanopore CANNOT detect modifications). Use when calling m6A from ONT DRS without immunoprecipitation, choosing m6Anet vs xPore vs Nanocompore vs ELIGOS vs Dorado native, interpreting probability_modified vs mod_ratio vs per-read probabilities, deciding between m6Anet (known DRACH sites) and Dorado/Remora (genome-wide screening), pinning RNA002 vs RNA004 chemistry and basecaller versions, or troubleshooting eventalign/dataprep failures.
tool_type: python
primary_tool: m6Anet
---

## Version Compatibility

Reference examples tested with: m6anet 2.1+ (PyPI; project capitalisation `m6Anet`), nanopolish 0.14+, minimap2 2.26+, samtools 1.19+, Dorado 0.5+, xpore 2.1+, nanocompore 1.0.4+, ELIGOS 2 (GitHub `novoalab/Eligos2`), CHEUI (GitHub `comprna/CHEUI`), pandas 2.2+, pyranges 0.0.129+, pysam 0.22+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show m6anet` then `m6anet --help`, `m6anet dataprep --help`, `m6anet inference --help`
- CLI: `nanopolish --version`, `minimap2 --version`, `dorado --version`

If `m6anet` is invoked as a hyphenated command (`m6anet-dataprep`), the v1.x CLI is installed; v2.x uses subcommand syntax (`m6anet dataprep`). Pin m6anet version explicitly in any reproducible analysis. Dorado modification models are versioned independently of the basecaller (`m6A_DRACH@v0.1`, `m6A_DRACH@v1`, ...); model versions are NOT directly comparable across releases. RNA002 vs RNA004 nanopore chemistry use different signal characteristics — models trained on RNA002 do NOT transfer to RNA004.

# m6Anet Direct-RNA m6A Detection

**"Detect m6A from my Nanopore direct RNA data without IP"** -> Run the full pipeline from POD5 / FAST5 signal to per-site m6A modification probabilities: Dorado basecalling -> minimap2 alignment to TRANSCRIPTOME (not genome) with `-ax map-ont -uf -k14` -> nanopolish eventalign with `--scale-events --signal-index` (the m6Anet-required pair) -> m6anet dataprep -> m6anet inference. Report per-site `probability_modified` (model posterior that any reads at the site are modified) AND `mod_ratio` (per-site stoichiometry, the fraction of reads called modified) with coverage. CRITICAL: m6Anet is DRACH-only — non-DRACH sites are invisible to the model; cDNA-Nanopore data CANNOT be used (PCR erases the signal); RNA002 and RNA004 chemistry require different model versions.

- CLI: `dorado basecaller rna004_130bps_sup@v5.0.0 --emit-fastq pod5/` -- modern RNA004 basecalling
- CLI: `minimap2 -ax map-ont -uf -k14 --secondary=no transcriptome.fa reads.fastq` -- transcriptome alignment
- CLI: `nanopolish eventalign --reads reads.fastq --bam aligned.bam --genome transcriptome.fa --scale-events --signal-index` -- signal-to-event (m6Anet-required flag pair)
- CLI: `m6anet dataprep --eventalign eventalign.txt --out_dir m6anet_data/` -- feature extraction
- CLI: `m6anet inference --input_dir m6anet_data/ --out_dir m6anet_results/` -- per-site probability + mod_ratio

## The Single Most Important Modern Insight -- m6Anet scores per-site DRACH probabilities, but reliability depends on coverage and the model is DRACH-only

Hendra 2022 *Nat Methods* 19:1590 recommends a minimum 20-50 reads per site for stable per-site `probability_modified` estimates; sites with <20 reads at probability_modified > 0.9 are likely false positives driven by per-read noise. The per-site `mod_ratio` column (the fraction of reads called modified at the site) is the stoichiometry-aware signal — informative even when per-site `probability_modified` is borderline. CRITICAL: m6Anet only scores DRACH 5-mers (D=A/G/U, R=A/G, A=methylated, C=C, H=A/C/U); non-DRACH sites are invisible to the model regardless of methylation status. For non-DRACH discovery, switch to Dorado / Remora modification basecallers (genome-wide; pin the modification-model version explicitly) or to xPore / Nanocompore (which compare two conditions without an a-priori 5-mer restriction). cDNA-Nanopore data cannot be used for m6Anet because PCR amplification erases the modification signal — only direct-RNA-sequencing (ONT DRS, kit SQK-RNA002 or SQK-RNA004) preserves the modification signal in the ionic current. Cross-method comparison: m6Anet ~0.51 recall on the Pratanwanich/Hendra synthetic-mix benchmark at >=10% modification / >=10x coverage; Dorado RNA004 recall is markedly higher (reported ~0.9 at the same threshold in a 2024-2025 RNA004 benchmark) but with higher per-site FDR (~40% at low-prevalence sites) — the two figures are NOT from a head-to-head test set, so treat as bounds rather than a comparable pair. The systematic 10-tool benchmark Zhong 2023 *Nat Commun* 14:1906 documents broader precision-vs-recall tradeoffs. The right modern pipeline is Dorado native for first-pass discovery -> m6Anet (or CHEUI) for filtering high-confidence subset -> GLORI for orthogonal stoichiometry validation at named loci.

## Algorithmic Taxonomy

| Tool | Mechanism | RNA002 | RNA004 | Strength | Fails when |
|------|-----------|--------|--------|----------|------------|
| m6Anet (Hendra 2022 *Nat Methods* 19:1590) | Multiple-instance-learning NN over DRACH 5-mer ionic-current features from nanopolish eventalign | YES | YES (recent) | Best-in-class for DRACH m6A on RNA002; generalises across cell lines | DRACH-only; requires nanopolish eventalign upstream |
| CHEUI (Acera Mateos 2024 *Nat Commun* 15:3899) | Deep CNN on ionic-current signals predicting m6A AND m5C in single molecules | YES | Limited | Simultaneous m6A + m5C calling; single-molecule co-occurrence | Newer; smaller user base; m5C less validated than m6A |
| Nanocompore (Leger 2021 *Nat Commun* 12:7198) | 2-component GMM comparing current + dwell-time between two samples | YES | Limited | Generic (any modification with signal change); replicate-aware | Requires modification-free control sample (WT vs KO or IVT) |
| xPore (Pratanwanich 2021 *Nat Biotechnol* 39:1394) | Bayesian multi-sample GMM; estimates fraction-modified per site per sample | YES | Limited | No matched WT/KO needed; multi-sample design; replicate support | Per-site coverage threshold dropout |
| ELIGOS / Eligos2 (Jenjaroenpun 2021 *NAR* 49:e7) | Compares error profile between native dRNA and unmodified controls (IVT) | YES | Limited | General-purpose; validated on yeast rRNA (95% recall); both error AND signal modes | Requires IVT or cDNA-seq control; modification-type-blind |
| EpiNano (Liu H et al. 2019 *Nat Commun* 10:4079) | Basecalling-error features as classifier features for m6A | Albacore 2.1.7 only | NO | Historical relevance; the original error-feature approach | Tied to obsolete Albacore basecaller; do NOT use for new analyses |
| Tombo (`ont-tombo`; Stoiber 2017 bioRxiv) | Signal-level model comparison; de novo against canonical RNA model OR sample-compare | YES | Limited | First general modification-detection tool; multi-modification | Less actively maintained since 2020; modern Dorado / m6Anet preferred |
| Dorado native modification calls (ONT; RNA004 chemistry, 2024+) | ONT basecaller with built-in modification calling (m6A, Ψ, m5C, inosine) | Limited (ONT focus shifted to RNA004; verify against current Dorado release notes) | YES | Modification calls in same output as base calls; per-read probabilities; first-pass discovery | Per-site precision lower than m6Anet at borderline sites; FDR ~40% at low-prevalence sites; model-version-pinning mandatory |
| m6ABasecaller / m6Aiso / mAFiA / m6ATM (2023-2024) | Newer ML approaches integrated with Dorado / basecaller | Mixed | Mixed | Active development; some integrated with Dorado | Less benchmarked; verify model lineage before reporting |
| DRUMMER | Pipeline integrating multiple modification tools | YES | Limited | Convenience wrapper | Inherits each tool's limitations |
| DiffErr | Error-rate differential between samples | YES | Limited | Lightweight differential | Modification-type-blind |

## Decision Tree by Scenario

| Scenario | Recommended | Why wrong choices fail |
|----------|-------------|------------------------|
| RNA002 chemistry, single-sample m6A discovery, DRACH context | m6Anet for first-pass; CHEUI for cross-check at high-confidence | EpiNano tied to obsolete basecaller; Tombo less maintained |
| RNA004 chemistry, first-pass screening | Dorado native modification calling -> m6Anet (or CHEUI) for filtering high-confidence subset | Single Dorado pass has ~40% FDR at low-prevalence sites |
| Two-condition comparison (WT vs KO) | xPore (Bayesian; no matched IVT needed) OR Nanocompore (with control sample); avoid single-condition tool with post-hoc differential | Single-tool per-condition then ad-hoc comparison loses statistical efficiency |
| Multi-condition (time course, multiple KOs) | xPore (multi-sample Bayesian); fall back to per-condition m6Anet + manual differential | Per-condition + ad-hoc comparison is less efficient |
| Need m6A AND m5C simultaneously | CHEUI (only published tool covering both) | Running m6Anet (m6A only) + separate m5C tool loses single-molecule co-occurrence |
| Non-DRACH site discovery | Dorado native modification calling (genome-wide) OR xPore / Nanocompore (5-mer-agnostic) | m6Anet / CHEUI are DRACH-only |
| Verified cDNA-Nanopore data (no DRS) | None of these tools apply — PCR erases modification signal; modification detection is impossible | Running m6Anet on cDNA returns near-zero modification probabilities everywhere |
| Cross-laboratory reproducibility | Pin: basecaller version, Dorado modification model version, m6Anet model SHA, nanopolish version, reference transcriptome version (GENCODE / Ensembl release) | Unpinned versions break cross-batch comparability |
| Absolute stoichiometry needed | NOT direct-RNA alone -- supplement with GLORI on a subset of sites for calibration | Per-read modification rate is a stoichiometry estimate but has ~5-15% per-read error; GLORI is the gold standard |
| Wanting to validate MeRIP peaks orthogonally | m6Anet at the MeRIP peak positions in DRACH context; report concordance | Cross-method validation by independent technologies is the strongest evidence |

Methodology evolves; before any high-stakes m6Anet / direct-RNA analysis, web-search "m6anet v2 release notes", "Dorado modification model release notes", "RNA004 m6A benchmark 2024" for current best practice.

## Full m6Anet Pipeline (RNA002 / RNA004 chemistry)

**Goal:** Take POD5 / FAST5 signal data through basecalling, transcriptome alignment, nanopolish event alignment, and m6anet inference to produce per-site m6A modification probabilities at DRACH 5-mers.

**Approach:** Basecall with Dorado (modern) or Guppy (legacy); align to TRANSCRIPTOME (not genome) with minimap2 `-ax map-ont -uf -k14 --secondary=no`; sort and index BAM; run nanopolish eventalign with the m6Anet-required `--scale-events --signal-index` flag pair (plus `--summary` / `--threads` for housekeeping); m6anet dataprep extracts features; m6anet inference produces per-site `probability_modified` and `mod_ratio`.

```bash
# Step 1: Basecalling (RNA004 chemistry example).
dorado download --model rna004_130bps_sup@v5.0.0

dorado basecaller \
    rna004_130bps_sup@v5.0.0 \
    pod5/ \
    --emit-fastq \
    > reads.fastq

# Step 2: Transcriptome alignment (NOT genome).
minimap2 \
    -ax map-ont \
    -uf \
    -k14 \
    --secondary=no \
    -t 12 \
    refs/transcriptome.fa \
    reads.fastq | \
samtools sort -@ 8 -o aligned.bam -

samtools index aligned.bam

# Step 3: Nanopolish eventalign with m6Anet-required --scale-events --signal-index pair.
# nanopolish uses --genome for both genome AND transcriptome FASTA (confusing nomenclature; the flag accepts either).
nanopolish index \
    -d pod5/ \
    reads.fastq

nanopolish eventalign \
    --reads reads.fastq \
    --bam aligned.bam \
    --genome refs/transcriptome.fa \
    --scale-events \
    --signal-index \
    --threads 12 \
    --summary nanopolish_summary.tsv \
    > eventalign.txt

# Step 4: m6Anet dataprep + inference. Output includes mod_ratio (per-site stoichiometry) as well as probability_modified.
m6anet dataprep \
    --eventalign eventalign.txt \
    --out_dir m6anet_data/ \
    --n_processes 8

m6anet inference \
    --input_dir m6anet_data/ \
    --out_dir m6anet_results/ \
    --n_processes 4 \
    --num_iterations 1000

ls m6anet_results/
```

The m6Anet-required nanopolish flags are `--scale-events --signal-index`; m6Anet was trained on this feature set. The additional `--samples --print-read-names` flags are sometimes needed by downstream tools (yanocomp, f5c-pipeline interop) but are NOT required by m6Anet itself. Transcriptome alignment with `-uf` forces the forward-strand interpretation (DRS is directional); `-k14` is the recommended k-mer for ONT DRS. Use `-ax map-ont` against a TRANSCRIPTOME reference (the reference is already spliced); switch to `-ax splice -uf -k14` only when aligning DRS reads to a GENOME reference (the lh3 cookbook pattern for SIRV / spike-in genomes).

## Filtering and Interpreting m6Anet Results

**Goal:** Apply minimum-coverage and probability thresholds to `data.site_proba.csv` to retain high-confidence m6A site calls; report `mod_ratio` (per-site stoichiometry) alongside `probability_modified` (per-site model posterior).

**Approach:** Read the CSV; filter by `n_reads >= 20` (conservative) or `>= 50` (stringent) AND `probability_modified >= 0.9` (high-precision threshold per Hendra 2022); inspect `mod_ratio` as the per-site stoichiometry estimate. The full column set is `transcript_id, transcript_position, n_reads, probability_modified, kmer, mod_ratio`.

```python
import pandas as pd

PROBABILITY_THRESHOLD = 0.9
MIN_COVERAGE = 20

sites = pd.read_csv('m6anet_results/data.site_proba.csv')

print(sites.columns.tolist())
print(f'Total DRACH sites tested: {len(sites)}')

filtered = sites[(sites['n_reads'] >= MIN_COVERAGE) &
                 (sites['probability_modified'] >= PROBABILITY_THRESHOLD)]

print(f'High-confidence m6A sites (n_reads >= {MIN_COVERAGE}, prob >= {PROBABILITY_THRESHOLD}): {len(filtered)}')

print(f'mod_ratio summary among high-confidence: min={filtered["mod_ratio"].min():.2f} median={filtered["mod_ratio"].median():.2f} max={filtered["mod_ratio"].max():.2f}')

per_transcript = (filtered
    .groupby('transcript_id')
    .agg(n_high_conf_sites=('transcript_position', 'count'),
         mean_mod_ratio=('mod_ratio', 'mean'),
         total_coverage=('n_reads', 'sum'))
    .reset_index()
    .sort_values('n_high_conf_sites', ascending=False))

per_transcript.head(20).to_csv('m6anet_results/top_modified_transcripts.tsv', sep='\t', index=False)
filtered.to_csv('m6anet_results/high_confidence_sites.tsv', sep='\t', index=False)
```

`probability_modified` is the per-site model posterior (multiple-instance-learning aggregation over reads); `mod_ratio` is the per-site stoichiometry (fraction of reads called modified above the model's internal per-read threshold). For stoichiometry claims, `mod_ratio` is the right column. For genuine per-read output (probability per individual read), enable `--read_proba_threshold <T>` during inference (NOT `--per_read_proba_threshold`); per-model defaults are very small (`0.033379376` for HCT116_RNA002), so 0.5 is an interpretation threshold on the output column, not the CLI default.

## xPore Two-Condition Differential

**Goal:** Compare m6A modification rate at each DRACH site between two conditions using a Bayesian multi-sample GMM; no matched IVT control needed.

**Approach:** Run nanopolish eventalign + xpore dataprep separately for each condition; build a YAML config listing conditions and per-condition runs; xpore diffmod tests for differential modification per site.

```bash
xpore dataprep \
    --eventalign eventalign_ctrl.txt \
    --out_dir xpore_ctrl/

xpore dataprep \
    --eventalign eventalign_treat.txt \
    --out_dir xpore_treat/

cat > xpore_config.yaml << 'EOF'
data:
  ctrl:
    rep1: xpore_ctrl/dataprep
  treat:
    rep1: xpore_treat/dataprep
out: xpore_diff_output/
EOF

xpore diffmod \
    --config xpore_config.yaml \
    --n_processes 8

head xpore_diff_output/diffmod.table
```

xPore reports `diff_mod_rate` (per-site rate difference) AND p-value AND posterior probability. Filter for high-confidence differential by combining `diff_mod_rate >= 0.1` (10 percentage points) AND `pval < 0.05`.

## Nanocompore Comparative Modification Detection

**Goal:** Compare current intensity and dwell time per position between WT and KO (or treated vs control) to detect modification differences via Gaussian mixture comparison.

**Approach:** nanopolish eventalign per condition; Nanocompore CLI compares the two; outputs per-position differential GMM logit + KS + MWU statistics.

```bash
nanocompore eventalign_collapse \
    --input eventalign_ctrl.txt \
    --output_dir nanocompore_ctrl/

nanocompore eventalign_collapse \
    --input eventalign_treat.txt \
    --output_dir nanocompore_treat/

nanocompore sampcomp \
    --file_list1 nanocompore_ctrl/out_eventalign_collapse.tsv \
    --file_list2 nanocompore_treat/out_eventalign_collapse.tsv \
    --label1 ctrl \
    --label2 treat \
    --fasta refs/transcriptome.fa \
    --outpath nanocompore_diff_output/ \
    --nthreads 8

head nanocompore_diff_output/outSampComp_results.tsv
```

Nanocompore reports `GMM_logit_pvalue`, `KS_dwell_pvalue`, `KS_intensity_pvalue`, `MW_dwell_pvalue`, `MW_intensity_pvalue`. The GMM_logit test is the primary modification signal; use as a starting filter, then inspect dwell / intensity for direction. CRITICAL: Nanocompore is modification-type-AGNOSTIC — it detects signal differences which may be any of m6A, m5C, Ψ, or other modifications. Type assignment requires orthogonal information.

## Per-Method Failure Modes

### cDNA-Nanopore data fed to m6Anet

**Trigger:** Sequencing run used cDNA-Nanopore (PCR-amplified) rather than DRS (direct RNA); m6Anet pipeline attempted on the output.

**Mechanism:** Modification detection from nanopore signals (m6Anet, xPore, Nanocompore, ELIGOS, Dorado native) requires the RAW ionic-current signal from direct-RNA sequencing. cDNA-Nanopore amplifies the cDNA via PCR, which erases all modification signal because PCR uses canonical bases. Only DRS protocols (kit SQK-RNA002 or SQK-RNA004; no PCR; RNA-native sequencing with the DNA RT-adapter) preserve the modification signal.

**Symptom:** `nanopolish eventalign` runs successfully but produces uniform-looking event distributions; m6anet inference returns near-zero `probability_modified` everywhere; no DRACH enrichment in flagged sites.

**Fix:** Confirm DRS protocol BEFORE running any modification-detection pipeline. Check sequencing-core run report for kit (SQK-RNA002 / SQK-RNA004) vs cDNA kit (SQK-PCS, SQK-LSK). If cDNA, modification detection is impossible; defer to MeRIP or chemistry-based methods.

### m6Anet run with low-coverage sites at high probability

**Trigger:** Reporting m6Anet `probability_modified > 0.9` at sites with `n_reads < 10`.

**Mechanism:** m6Anet's per-site probability is computed via multiple-instance aggregation over reads. With low coverage, per-read predictions are weakly aggregated and per-site probability is noisy. Hendra 2022 recommends 20-50 reads per site minimum for stable calls.

**Symptom:** Many "high-confidence" m6A sites at sparsely-covered transcripts; per-site probability scatter at low coverage; sites do not validate orthogonally.

**Fix:** Apply minimum-coverage filter (`n_reads >= 20` conservative; `>= 50` stringent) BEFORE the probability filter. For high-stakes sites at low coverage, report both per-site probability AND per-read modification rate; orthogonally validate with GLORI / SAC-seq.

### Genome alignment instead of transcriptome alignment

**Trigger:** minimap2 invoked with `-ax splice -uf` (genome splice-aware) before m6Anet pipeline.

**Mechanism:** m6Anet expects reads aligned to a TRANSCRIPTOME FASTA (per-transcript coordinates); nanopolish eventalign signal alignment is per-transcript. Genome-aligned reads with splice junctions break the per-transcript signal interpretation.

**Symptom:** m6anet dataprep fails with chromosome / transcript ID errors; OR runs but produces few site calls; OR per-site probabilities are nonsensical.

**Fix:** Use `minimap2 -ax map-ont -uf -k14 --secondary=no` against a TRANSCRIPTOME FASTA for the m6Anet pipeline. For downstream genome-coordinate visualisation, convert site predictions back to genome coordinates via the transcript-to-genome mapping (use the GTF + a custom script or `samtools` lifting).

### Nanopolish eventalign without m6Anet-required flags

**Trigger:** `nanopolish eventalign` invoked without `--scale-events --signal-index`.

**Mechanism:** m6Anet was trained on the specific eventalign output format produced by `--scale-events --signal-index`. Without these, the dataprep step fails or produces feature vectors that don't match the model's expected input. The additional `--samples --print-read-names` flags are commonly added because other downstream tools (yanocomp, f5c interop) need them, but m6Anet itself does NOT require them.

**Symptom:** m6anet dataprep fails with parse errors; OR runs but produces empty feature files; OR inference returns no calls.

**Fix:** Always pass `--scale-events --signal-index` for m6Anet; add `--samples --print-read-names` only if downstream tools need them. Verify against m6anet quickstart for the installed version.

### f5c eventalign substituted for nanopolish without validation

**Trigger:** GPU-accelerated f5c eventalign used in place of nanopolish for speed; m6Anet model run on f5c output.

**Mechanism:** f5c is a re-implementation of nanopolish; eventalign output is numerically very close but NOT bit-identical, particularly in `event_level_mean` and `model_kmer` columns under certain edge cases. m6Anet was trained on nanopolish output; f5c is empirically usable but not officially supported and can shift per-site probabilities by 5-10% in extreme cases.

**Fix:** Use nanopolish unless GPU acceleration is required AND the user has validated f5c output equivalence on a control dataset. Document the eventalign source in any published analysis.

### Dorado modification model version not pinned

**Trigger:** SKILL.md / pipeline uses Dorado for m6A modification calling without specifying the model version.

**Mechanism:** Dorado modification models are versioned independently of the basecaller (`m6A_DRACH@v0.1`, `m6A_DRACH@v1.0`, etc.). Calls from different model versions are NOT directly comparable; model retraining shifts per-site probabilities.

**Fix:** Pin the exact modification model SHA / version in every CLI invocation; record in pipeline metadata. For multi-batch projects, re-call older batches with the new model when upgrading.

### Reference transcriptome version drift

**Trigger:** m6Anet results in batch 1 computed against GENCODE v44 transcripts; batch 2 against GENCODE v45; direct transcript-coordinate comparison.

**Mechanism:** Transcript IDs include version suffixes (`ENST00000123456.1` vs `.2`); some transcripts change between releases. Site coordinates relative to transcript start may shift.

**Fix:** Pin GENCODE / Ensembl transcript release for ALL m6Anet runs in a project. Lift over results when upgrading.

### Per-read modification rate confused with per-site probability

**Trigger:** Reporting m6Anet `probability_modified` as "the fraction of molecules modified at this site".

**Mechanism:** `probability_modified` is the model's posterior probability that the site has any modified reads (multiple-instance learning aggregation). It is NOT the per-read modification rate. Per-read modification rate is the fraction of reads at the site whose per-read posterior exceeds 0.5 (or another threshold).

**Symptom:** Stoichiometry claims based on per-site probability; numbers don't match orthogonal GLORI / SAC-seq stoichiometry estimates.

**Fix:** For stoichiometry, compute per-read modification rate from per-read output; cross-validate against GLORI at named sites.

### RNA002 model run on RNA004 chemistry data

**Trigger:** Pipeline uses an m6Anet model trained on RNA002 to analyse RNA004 chemistry runs.

**Mechanism:** RNA002 and RNA004 nanopore chemistry produce different signal characteristics — different motor protein, different translocation kinetics. Models trained on RNA002 do NOT transfer to RNA004 (and vice versa).

**Fix:** Pin RNA chemistry version per project; use the m6Anet model trained on the matching chemistry. m6Anet v2+ has explicit RNA004 model support; verify against `m6anet --help`.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| m6Anet high-confidence; GLORI does not call | Site in low-stoichiometry tail; GLORI conservatism | Trust GLORI for absolute; m6Anet probability + per-read rate informative for prevalence |
| m6Anet calls; MeRIP peak in same gene but different position | MeRIP fragment-level vs m6Anet single-base; methylation position offset within peak | Map m6Anet site against MeRIP peak coordinates with tolerance (~100 nt); concordance at gene level |
| Dorado calls; m6Anet does not at same DRACH | Dorado broader / less conservative; m6Anet model trained more strictly | Use m6Anet for high-precision; Dorado for high-recall first-pass |
| xPore differential strong; Nanocompore weak | xPore Bayesian multi-sample; Nanocompore pairwise GMM less powered | Trust xPore for multi-sample designs |
| Per-site probability high but per-read rate low | Few reads contributed strongly; rest were near-threshold | Suspect over-fit per-site at low coverage; verify with higher-coverage replicate |
| All ELIGOS / EpiNano sites have low signal | Older tools tied to obsolete basecallers; signal interpretation broken | Switch to modern tools (m6Anet, Dorado native) |
| CHEUI m6A and m5C overlap at same site | Co-occurring modifications OR cross-talk in model | CHEUI is the only published tool that handles co-occurrence; interpret as biological signal if validated |
| Tombo de novo and sample-compare disagree | Different baseline assumptions | Prefer sample-compare with KO / IVT control |

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|----------|-----------|--------------------|
| m6Anet per-site `probability_modified` (high confidence) | >= 0.9 | Hendra 2022 *Nat Methods* 19:1590 default; high precision, lower recall |
| m6Anet per-site `probability_modified` (discovery) | >= 0.7 | Hendra 2022 lower threshold for less-stringent screens |
| m6Anet per-site minimum coverage | >= 20 reads (conservative); >= 50 (stringent) | Hendra 2022 recommendation for stable per-site estimates |
| Per-read modification probability interpretation threshold | >= 0.5 on output column (NOT CLI default) | m6Anet per-read posterior column convention; the CLI flag is `--read_proba_threshold` and per-model defaults are very small (~0.003-0.03) |
| xPore differential modification rate | >= 0.1 (10 percentage points) | xPore convention for meaningful biological effect |
| Nanocompore GMM_logit p-value | < 0.05 | Standard convention; primary statistic |
| ELIGOS error-rate ratio threshold | >= 2 (modified vs control) | Jenjaroenpun 2021 convention |
| Dorado native modification probability (per-read) | >= 0.5 (default) | ONT convention; threshold tuned per model version |
| minimap2 k-mer for ONT DRS | 14 | ONT recommendation for direct-RNA |
| minimap2 strand flag for DRS | `-uf` (forward strand only) | DRS is directional; reverse-strand alignment is incorrect |
| Per-tool benchmark recall (>=10% mod, >=10x cov, GLORI ground truth) | m6Anet ~0.51 (Pratanwanich/Hendra synthetic-mix); Dorado RNA004 ~0.9 (reported in 2024-2025 RNA004 benchmarks; NOT head-to-head) | Hendra 2022 *Nat Methods* 19:1590; broader 10-tool tradeoff context in Zhong 2023 *Nat Commun* 14:1906 |
| Cross-method concordance (m6Anet + GLORI + SAC-seq) | ~70-85% at high-confidence sites | Approximate from per-method validation tables in Liu C 2023 *Nat Biotechnol* 41:355 and Hu L 2022 *Nat Biotechnol* 40:1210; verify against current cross-method benchmark |
| Common-core m6A sites (HEK293T cross-method) | ~6,000-15,000 | Intersection of orthogonal methods |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `m6anet-dataprep` not found | v1 hyphenated CLI not in installed v2 | Use `m6anet dataprep` (subcommand syntax) |
| nanopolish eventalign errors with "no event annotation" | FAST5 / POD5 not indexed; OR `--scale-events --signal-index` missing | Run `nanopolish index -d pod5/ reads.fastq` first; include the m6Anet-required flag pair |
| m6anet inference returns empty CSV | dataprep output empty; OR all sites filtered by default coverage threshold | Check dataprep log; verify feature TSV in dataprep output dir |
| Reads marked as cDNA in run summary | Library prep used cDNA kit (SQK-PCS / SQK-LSK), not DRS | Modification detection impossible; switch to MeRIP / chemistry-based methods |
| `minimap2 -ax splice` instead of `map-ont` | Genome-splice flag used for transcriptome alignment | Switch to `-ax map-ont -uf -k14` |
| `nanopolish eventalign` extremely slow | Single-threaded by default | Pass `--threads N` |
| f5c output produces shifted m6Anet probabilities | f5c is numerically near-identical but not bit-identical to nanopolish | Use nanopolish unless GPU acceleration required |
| Per-site probability high at 5 reads | Low coverage; per-site noise | Filter by `n_reads >= 20` before interpretation |
| xPore diffmod takes hours per condition | Single-threaded default | Pass `--n_processes 8` |
| Dorado m6A model not found | Model not downloaded | `dorado download --model m6A_DRACH@v1` |
| Transcriptome IDs missing from m6anet output | Reference mismatch between minimap2 input and m6anet config | Use same transcriptome FASTA throughout pipeline |
| Modification probabilities differ between Dorado releases | Model versioned independently from basecaller | Pin model version explicitly |
| Per-read CSV not generated | `--read_proba_threshold` not set (NOT `--per_read_proba_threshold`) | Add `--read_proba_threshold <T>` to `m6anet inference`; T is model-specific (default very small, e.g., 0.033 for HCT116_RNA002) |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Why m6Anet over Dorado native?" | m6Anet for high-precision DRACH calling; Dorado for high-recall first-pass; both reported when feasible |
| "How were non-DRACH sites handled?" | m6Anet is DRACH-only by design; non-DRACH discovery via Dorado / xPore / Nanocompore; cited limitation |
| "What's the per-site coverage threshold?" | `n_reads >= 20` conservative per Hendra 2022; `>= 50` for stringent calls |
| "Was cross-validation against orthogonal methods done?" | High-stakes sites cross-checked against GLORI / m6A-SAC-seq / MeRIP peaks; cross-method concordance reported |
| "Why RNA002 vs RNA004?" | Chemistry version pinned per project; m6Anet model selected to match (RNA002 model on RNA002 data, RNA004 on RNA004) |
| "Was the Dorado modification model version pinned?" | Yes — version recorded in pipeline metadata; rerun batches with new model when upgrading |
| "Per-site probability vs mod_ratio?" | `probability_modified` is the per-site model posterior; `mod_ratio` is the per-site stoichiometry (fraction of reads called modified) — both reported |
| "Is mod_ratio the same as absolute stoichiometry?" | Approximately; per-read calls have ~5-15% error; for absolute stoichiometry at named loci, cross-validate with GLORI |
| "Why not just use Tombo / EpiNano?" | Tombo less maintained since 2020; EpiNano tied to obsolete Albacore basecaller; m6Anet / Dorado / CHEUI are modern |
| "How were f5c vs nanopolish handled?" | Used nanopolish (m6Anet-trained source); did not substitute f5c |

## References

- Hendra C, Pratanwanich PN, Wan YK, Goh WSS, Thiery A, Göke J (2022) Detection of m6A from direct RNA sequencing using a multiple instance learning framework. *Nat Methods* 19(12):1590-1598. doi:10.1038/s41592-022-01666-1
- Pratanwanich PN, Yao F, Chen Y et al (2021) Identification of differential RNA modifications from nanopore direct RNA sequencing with xPore. *Nat Biotechnol* 39(11):1394-1402. doi:10.1038/s41587-021-00949-w
- Leger A, Amaral PP, Pandolfini L et al (2021) RNA modifications detection by comparative Nanopore direct RNA sequencing. *Nat Commun* 12(1):7198. doi:10.1038/s41467-021-27393-3
- Jenjaroenpun P, Wongsurawat T, Wadley TD et al (2021) Decoding the epitranscriptional landscape from native RNA sequences. *Nucleic Acids Res* 49(2):e7. doi:10.1093/nar/gkaa620
- Liu H, Begik O, Lucas MC et al (2019) Accurate detection of m6A RNA modifications in native RNA sequences. *Nat Commun* 10(1):4079. doi:10.1038/s41467-019-11713-9
- Acera Mateos P, Sethi AJ, Ravindran A et al (2024) Prediction of m6A and m5C at single-molecule resolution reveals a transcriptome-wide co-occurrence of RNA modifications. *Nat Commun* 15:3899. doi:10.1038/s41467-024-47953-7
- Stoiber MH, Quick J, Egan R et al (2017) De novo identification of DNA modifications enabled by genome-guided nanopore signal processing. *bioRxiv* 094672. doi:10.1101/094672
- Zhong ZD, Xie YY, Chen HX et al (2023) Systematic comparison of tools used for m6A mapping from nanopore direct RNA sequencing. *Nat Commun* 14:1906. doi:10.1038/s41467-023-37596-5
- Liu C, Sun H, Yi Y et al (2023) Absolute quantification of single-base m6A methylation in the mammalian transcriptome using GLORI. *Nat Biotechnol* 41(3):355-366. doi:10.1038/s41587-022-01487-9
- Hu L, Liu S, Peng Y et al (2022) m6A RNA modifications are measured at single-base resolution across the mammalian transcriptome. *Nat Biotechnol* 40(8):1210-1219. doi:10.1038/s41587-022-01243-z
- Li H (2018) Minimap2: pairwise alignment for nucleotide sequences. *Bioinformatics* 34(18):3094-3100. doi:10.1093/bioinformatics/bty191
- Loman NJ, Quick J, Simpson JT (2015) A complete bacterial genome assembled de novo using only nanopore sequencing data. *Nat Methods* 12(8):733-735. doi:10.1038/nmeth.3444
- Dominissini D, Moshitch-Moshkovitz S, Schwartz S et al (2012) Topology of the human and mouse m6A RNA methylomes revealed by m6A-seq. *Nature* 485(7397):201-206. doi:10.1038/nature11112
- Linder B, Grozhik AV, Olarerin-George AO, Meydan C, Mason CE, Jaffrey SR (2015) Single-nucleotide-resolution mapping of m6A and m6Am throughout the transcriptome. *Nat Methods* 12(8):767-772. doi:10.1038/nmeth.3453

## Related Skills

- merip-preprocessing - Genome-aligned MeRIP for cross-validation against direct-RNA calls
- m6a-peak-calling - MeRIP fragment-level peaks for orthogonal validation comparison
- m6a-differential - Per-site direct-RNA modification rate comparable to MeRIP differential at named loci
- modification-visualization - Metagene and browser-track rendering of m6Anet site calls
- long-read-sequencing/basecalling - Upstream Dorado / Guppy basecalling fundamentals
- long-read-sequencing/long-read-alignment - General minimap2 alignment patterns
- long-read-sequencing/long-read-qc - Direct RNA QC (yield, length distribution, basecall accuracy)
- long-read-sequencing/nanopore-methylation - DNA methylation calling sibling (different chemistry, related framework)
- read-alignment/star-alignment - Splice-aware alignment for cross-method comparison context
- variant-calling/vcf-basics - General per-site variant call framework (analogue)
- rna-quantification/featurecounts-counting - For cross-method site-vs-MeRIP-peak comparison
<!-- END FILE: epitranscriptomics/m6anet-analysis/SKILL.md -->

## 子目录：epitranscriptomics/merip-preprocessing

<!-- BEGIN FILE: epitranscriptomics/merip-preprocessing/SKILL.md -->
---
name: bio-epitranscriptomics-merip-preprocessing
description: Aligns and QCs methylated-RNA-immunoprecipitation (MeRIP / m6A-seq) IP and input libraries using STAR or HISAT2 splice-aware mapping, samtools sort/index, IP/input matched-pair tracking, antibody-lot metadata recording, replicate concordance via deepTools multiBamSummary + plotCorrelation, IP enrichment QC via plotFingerprint and per-transcript IP/input ratio distributions, library-complexity saturation curves via PreSeq, and the explicit do-NOT-deduplicate convention for standard non-UMI MeRIP. Use when preparing paired IP and input BAM files for exomePeak2 / MeTPeak / MACS3 peak calling, evaluating MeRIP replicate concordance and IP enrichment, deciding whether to deduplicate (standard MeRIP typically NOT), choosing genome-vs-transcriptome alignment for downstream peak vs m6Anet workflows, recording antibody clone and lot metadata for cross-batch reconciliation, detecting failed IPs via saturation curves and IP/input distribution shape, or generating IP-over-Input bigWig tracks for visualisation.
tool_type: cli
primary_tool: STAR
---

## Version Compatibility

Reference examples tested with: STAR 2.7.11+, HISAT2 2.2.1+, samtools 1.19+, deepTools 3.5+, PreSeq 3.2+, fastp 0.23+, Trim Galore 0.6.10+, Picard 3.1+, MultiQC 1.25+, bowtie2 2.5+, BWA-MEM2 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

STAR `--outSAMtype` accepts `BAM SortedByCoordinate` since 2.5.x; check the `Log.final.out` file for input/output statistics. deepTools `bamCompare --operation log2` is the modern syntax (older `--ratio log2` still works but is being phased out). PreSeq `c_curve` and `lc_extrap` have stable interfaces; HISAT2 reports unique vs multi-mapped in the summary log.

# MeRIP-seq Preprocessing

**"Get my MeRIP IP and input libraries ready for peak calling"** -> Trim adapters with MeRIP-appropriate defaults (do NOT trim UMIs unless the library is UMI-MeRIP — most are not), splice-aware-align IP and input to the GENOME (not transcriptome) with STAR / HISAT2, sort and index, evaluate replicate concordance and IP enrichment with deepTools, build a saturation curve per library so peak counts can be honestly compared across libraries, record antibody clone and lot metadata so cross-batch comparison is later auditable, and produce IP-over-Input log2 bigWig tracks for downstream visualisation. Crucially, do NOT deduplicate non-UMI MeRIP — see the failure-modes section.

- CLI: `STAR --runMode alignReads` -- splice-aware genome alignment, the field default
- CLI: `hisat2 -x index -1 R1.fq.gz -2 R2.fq.gz` -- graph-based alternative; lighter memory footprint
- CLI: `samtools sort -@ 8 -o sorted.bam in.bam && samtools index sorted.bam` -- post-alignment mechanics
- CLI: `deeptools multiBamSummary bins -b *.bam -o cov.npz` + `plotCorrelation` -- replicate Spearman
- CLI: `deeptools plotFingerprint -b IP.bam Input.bam -o fp.pdf` -- IP enrichment QC (ChIP-seq term; transfers cleanly)
- CLI: `preseq lc_extrap -B -o curve.txt sorted.bam` -- library complexity / saturation
- CLI: `deeptools bamCompare -b1 IP.bam -b2 Input.bam --operation log2 -o IP_over_Input.bw` -- downstream-ready coverage track

## The Single Most Important Modern Insight -- Peak counts are library-size-dependent; saturation curves are the only honest cross-library comparison

A MeRIP library sequenced to 20 million unique reads finds substantially fewer peaks than the same biology at 60 million reads. Per-sample peak counts reported without saturation curves (PreSeq `c_curve` / `lc_extrap`; Daley & Smith 2013 *Nat Methods* 10:325) are uninterpretable across studies and often across replicates within a study. Subsample BAMs to a common unique-read depth before peak calling for any cross-condition peak-count comparison, OR report peaks alongside the saturation curve. A corollary: **do NOT deduplicate standard MeRIP** — the typical MeRIP protocol (Synaptic Systems 202-003 / Abcam ab151230 / NEB EpiMark E1610 antibody pull-down on fragmented poly(A)-selected RNA) has NO unique molecular identifiers, and `picard MarkDuplicates` on such libraries collapses real biological replicates of high-coverage transcripts (the opposite of what dedup achieves in DNA ChIP-seq). UMI-MeRIP is the only exception — and most MeRIP libraries in print are NOT UMI. McIntyre et al. 2020 *Sci Rep* 10:6590 demonstrated that replicate-to-replicate peak overlap is ~80% within a single lab but drops to a median 45% between labs using nominally identical conditions; this irreducible technical noise constrains how strongly any single MeRIP study can support biological claims, and the preprocessing pipeline is where the variance is set.

## Algorithmic Taxonomy

| Tool / step | Mechanism | Output | Strength | Fails when |
|-------------|-----------|--------|----------|------------|
| STAR 2.7+ (Dobin 2013 *Bioinformatics* 29:15) | Two-pass splice-aware alignment with on-the-fly splice junction database | Sorted BAM + splice-junction TSV | Field default; multi-mapper retention configurable; STAR splice-junction DB | Memory-heavy (~30 GB human); slower than HISAT2 |
| HISAT2 2.2.1+ (Kim 2019 *Nat Biotechnol* 37:907) | Hierarchical graph FM-index; splice-aware | Sorted BAM | ~5x lighter memory than STAR; comparable accuracy | Less mature splice-junction handling for novel introns |
| BWA-MEM2 (Vasimuddin 2019 *IPDPS* 314) | DNA-style local alignment; NO splice awareness | Sorted BAM | Use ONLY for transcriptome-aligned MeRIP (rare) | Splits reads across exon junctions if used on genome |
| fastp 0.23+ (Chen 2018 *Bioinformatics* 34:i884) | Streaming adapter detection + quality trim | Trimmed FASTQ + JSON QC | Fast; JSON-readable QC output | UMI handling disabled by default; do NOT pass `--umi` for standard non-UMI MeRIP (the opposite of the failure direction in some other library types) |
| Trim Galore | Wrapper over cutadapt with paired-end auto-detect | Trimmed FASTQ | Conservative defaults; widely cited | Slower than fastp on large datasets |
| samtools sort / index | BAM coordinate sort + .bai index | Sorted BAM + index | Standard | None at default |
| Picard MarkDuplicates | Identifies PCR duplicates by 5' alignment start | Marked / removed BAM | Standard in DNA / ChIP | The dominant MeRIP convention is to SKIP dedup for non-UMI libraries (collapses real biology at high-coverage transcripts); a minority of pipelines dedup MeRIP — record the choice in metadata |
| deepTools multiBamSummary + plotCorrelation | Per-bin read counts; Spearman / Pearson matrix | Heatmap + clustering | Standard replicate-concordance plot | Bin size sensitive (use 10 kb for transcriptome-genome) |
| deepTools plotFingerprint (Diaz 2012 *Stat Appl Genet Mol Biol* 11:9) | Cumulative read-fraction vs cumulative-bin-fraction Lorenz curve | PDF + raw counts | Direct IP-vs-input enrichment QC; "good" IP has steep tail | A flat fingerprint = failed IP (or mock IgG) |
| deepTools bamCompare --operation log2 | Per-bin log2 (IP/input) bigWig | bigWig | Ready for downstream visualisation | Pseudocount choice matters at low-coverage bins |
| PreSeq c_curve / lc_extrap (Daley & Smith 2013 *Nat Methods* 10:325) | Capture-recapture; rational-function extrapolation | Curve TSV | The only honest library-complexity estimate | Requires uniquely-mapped reads to be reliable |
| MultiQC (Ewels 2016 *Bioinformatics* 32:3047) | Aggregator across tools | HTML report | Consolidates STAR + HISAT2 + samtools + deepTools + PreSeq into one report | None |

## Decision Tree by Scenario

| Scenario | Recommended | Why wrong choices fail |
|----------|-------------|------------------------|
| Standard mammalian MeRIP, downstream exomePeak2 | STAR splice-aware -> genome BAM; do NOT deduplicate; build saturation curve | Transcriptome alignment breaks exomePeak2 (expects genome BAM + GTF); dedup collapses biology |
| Downstream m6Anet (ONT direct RNA) | Defer to `m6anet-analysis` -- alignment is to TRANSCRIPTOME with minimap2 `-ax map-ont -uf -k14` | Genome-aligned ONT input breaks m6Anet entirely (signal-level dataprep requires per-transcript coordinates) |
| Limited memory (<16 GB) | HISAT2 instead of STAR | STAR human genome index requires ~30 GB |
| UMI-MeRIP (rare) | Trim UMI to read header (umi_tools / fastp `--umi_loc`), align, then dedup with `umi_tools dedup` | Standard `picard MarkDuplicates` ignores UMI; effective dedup rate wrong |
| Cross-batch comparison (different antibody lots) | Record antibody clone + lot in sample-sheet metadata; include `batch` factor in downstream design | Pooling cross-batch counts without batch term inflates false-positive differential peaks |
| Spike-in normalisation (NEB EpiMark control oligos) | Align separately to spike-in reference; report IP-spike-in / Input-spike-in ratio per sample; use for absolute normalisation | Most users discard the NEB EpiMark Gluc / Cluc controls; they are the per-sample IP-efficiency QC anchor |
| Cross-library peak-count comparison | Subsample BAMs to common unique-read depth with `samtools view -s` BEFORE downstream peak calling, OR fit saturation curves and compare at common depth | Raw peak counts are sequencing-depth-dependent and not biologically interpretable |
| Suspect failed IP | Inspect deepTools `plotFingerprint` AND per-transcript IP/input ratio distribution; failed IP shows shallow Lorenz tail AND median IP/input ~1.0 | Trusting raw peak count alone — failed IPs still produce peaks |
| Viral / contamination-suspect samples | Build a combined host + viral index (and rRNA index) and check unmapped reads | Single-organism indexes hide systematic contamination |
| Aligning to transcriptome (rare; specific downstream tools) | BWA-MEM2 or bowtie2; defer to `read-alignment/` | STAR splice-aware on transcriptome causes spurious splice calls inside transcripts |

Methodology evolves; before any high-stakes preprocessing pipeline, web-search "STAR vs HISAT2 MeRIP 2024" and "MeRIP saturation curve preseq" for current consensus parameters.

## Adapter Trimming for MeRIP

**Goal:** Remove sequencing adapters and low-quality 3' ends WITHOUT removing biological signal (UMI-MeRIP must keep UMI sequences; standard MeRIP does not have UMIs and trimming should be minimal).

**Approach:** Use fastp or Trim Galore with adapter auto-detection; require minimum read length 25-30 nt (shorter reads multi-map and confound exomePeak2); for standard non-UMI MeRIP, do NOT pass `--umi` flags; preserve random-hexamer-priming artifacts ONLY if downstream pipeline expects them (most do not).

```bash
mkdir -p trimmed

for sample in IP_rep1 IP_rep2 IP_rep3 Input_rep1 Input_rep2 Input_rep3; do
    fastp \
        --in1 raw/${sample}_R1.fastq.gz \
        --in2 raw/${sample}_R2.fastq.gz \
        --out1 trimmed/${sample}_R1.fq.gz \
        --out2 trimmed/${sample}_R2.fq.gz \
        --html qc/${sample}_fastp.html \
        --json qc/${sample}_fastp.json \
        --length_required 25 \
        --detect_adapter_for_pe \
        --thread 8
done
```

For UMI-MeRIP (rare), insert `--umi --umi_loc read1 --umi_len 8` BEFORE the alignment step. Default fastp output preserves base quality information needed by downstream variant-aware tools; do NOT pass `--disable_quality_filtering` for MeRIP libraries.

## STAR Splice-Aware Alignment for IP and Input

**Goal:** Produce coordinate-sorted, indexed GENOME BAM files for each IP and input library with splice-junction-aware mapping, retaining a moderate number of multi-mappers for accurate per-window read counts at multi-isoform loci.

**Approach:** Build STAR genome index once with the matched GENCODE / Ensembl GTF used downstream; loop IP and input samples with identical parameters; retain up to 20 multi-mappers per read (MeRIP read counts at multi-isoform genes need this); request explicit BAM SortedByCoordinate; emit splice-junction tables for QC.

```bash
STAR \
    --runMode genomeGenerate \
    --genomeDir star_index \
    --genomeFastaFiles genome.fa \
    --sjdbGTFfile annotation.gtf \
    --sjdbOverhang 100 \
    --runThreadN 12

mkdir -p aligned

for sample in IP_rep1 IP_rep2 IP_rep3 Input_rep1 Input_rep2 Input_rep3; do
    STAR \
        --runMode alignReads \
        --genomeDir star_index \
        --readFilesIn trimmed/${sample}_R1.fq.gz trimmed/${sample}_R2.fq.gz \
        --readFilesCommand zcat \
        --outSAMtype BAM SortedByCoordinate \
        --outFilterMultimapNmax 20 \
        --outSAMattributes NH HI AS nM NM MD \
        --outFileNamePrefix aligned/${sample}_ \
        --runThreadN 12

    samtools index -@ 4 aligned/${sample}_Aligned.sortedByCoord.out.bam
done
```

`--outFilterMultimapNmax 20` is intentional: MeRIP at rRNA / snoRNA / pseudogene-rich loci needs multi-mapper retention. Reduce to 1 only if downstream analysis explicitly cannot tolerate multi-mappers. `--sjdbOverhang` should equal (read length - 1) but 100 is the common-enough default for 100-150 bp reads.

## HISAT2 Alternative for Memory-Constrained Environments

**Goal:** Achieve splice-aware alignment in ~5x less memory than STAR (12-16 GB suffices for human), with comparable accuracy for MeRIP applications.

**Approach:** Build HISAT2 graph index; align with `--dta` for downstream-transcript-assembly compatibility; pipe directly to samtools sort.

```bash
hisat2-build genome.fa hisat2_index/genome

for sample in IP_rep1 IP_rep2 IP_rep3 Input_rep1 Input_rep2 Input_rep3; do
    hisat2 \
        -x hisat2_index/genome \
        -1 trimmed/${sample}_R1.fq.gz \
        -2 trimmed/${sample}_R2.fq.gz \
        --dta \
        --summary-file qc/${sample}_hisat2.log \
        -p 12 | \
    samtools sort -@ 8 -o aligned/${sample}.sorted.bam -

    samtools index -@ 4 aligned/${sample}.sorted.bam
done
```

HISAT2 multi-mapper handling is governed by `-k`; the default reports the primary alignment only. For MeRIP, pass `-k 5` if multi-mapper-aware downstream counting is required.

## Per-Sample QC: flagstat and idxstats

```bash
mkdir -p qc

for bam in aligned/*sortedByCoord.out.bam aligned/*sorted.bam; do
    name=$(basename ${bam} .bam)
    samtools flagstat ${bam} > qc/${name}.flagstat
    samtools idxstats ${bam} > qc/${name}.idxstats
done
```

Inspect `flagstat` for properly-paired rate (>=85% indicates good pairing); inspect `idxstats` for unexpected chromosome-level read piles (rRNA bleed-through, mitochondrial domination — both are MeRIP red flags).

## Replicate Concordance via deepTools

**Goal:** Quantify how similar replicate IP libraries are to each other (and likewise input libraries) using a Spearman correlation matrix; flag a divergent replicate before it propagates into peak calling.

**Approach:** Compute genome-wide per-bin read counts at 10 kb resolution across all IP and input BAMs; convert to a clustered Spearman heatmap with deepTools `plotCorrelation`.

```bash
multiBamSummary bins \
    --bamfiles aligned/IP_rep1*.bam aligned/IP_rep2*.bam aligned/IP_rep3*.bam \
                aligned/Input_rep1*.bam aligned/Input_rep2*.bam aligned/Input_rep3*.bam \
    --binSize 10000 \
    --numberOfProcessors 8 \
    --outRawCounts qc/raw_bin_counts.tab \
    -o qc/cov.npz

plotCorrelation \
    --corData qc/cov.npz \
    --corMethod spearman \
    --skipZeros \
    --whatToPlot heatmap \
    --colorMap RdYlBu_r \
    --plotNumbers \
    -o qc/replicate_correlation.pdf
```

IP replicates within a condition should cluster (Spearman >= 0.85 typical); input replicates should cluster with each other; IP and input should NOT cluster together. A failed IP looks like input.

## IP Enrichment via plotFingerprint

**Goal:** Confirm IP libraries are enriched (a few transcripts have many reads) and input libraries are uniform (reads spread across transcripts); fail-fast on poor IP before peak calling.

**Approach:** deepTools `plotFingerprint` builds a cumulative Lorenz-style curve; a steep tail = signal concentrated in few regions (good IP); a diagonal = uniform coverage (input or failed IP). The framework is from ChIP-seq (Diaz 2012 *Stat Appl Genet Mol Biol* 11:9) and transfers cleanly to MeRIP.

```bash
plotFingerprint \
    --bamfiles aligned/IP_rep1*.bam aligned/IP_rep2*.bam aligned/IP_rep3*.bam \
                aligned/Input_rep1*.bam aligned/Input_rep2*.bam aligned/Input_rep3*.bam \
    --labels IP1 IP2 IP3 In1 In2 In3 \
    --numberOfProcessors 8 \
    --skipZeros \
    --outQualityMetrics qc/fingerprint_metrics.tab \
    -o qc/fingerprint.pdf
```

Good MeRIP IP: cumulative-fraction-of-reads vs cumulative-fraction-of-bins curve sits well below the diagonal in the right half (top-X% of bins capture >50% of reads). Input: near-diagonal. The `--outQualityMetrics` file reports JS distance and synthetic JS distance; the IP-vs-Input JS distance is a single-number IP-quality summary (higher = more concentrated signal).

## Library Complexity / Saturation Curves via PreSeq

**Goal:** Compute per-library complexity so peak counts can be honestly compared across libraries and conditions of different sequencing depth.

**Approach:** PreSeq `c_curve` (interpolation up to observed depth) and `lc_extrap` (extrapolation beyond observed) on the sorted BAM. Daley & Smith 2013 *Nat Methods* 10:325 capture-recapture model.

```bash
mkdir -p complexity

for bam in aligned/*.bam; do
    name=$(basename ${bam} .bam)

    preseq c_curve -B -o complexity/${name}_c_curve.txt ${bam}

    preseq lc_extrap -B -o complexity/${name}_lc_extrap.txt ${bam}
done
```

Inspect: the `lc_extrap` curve plots distinct molecules vs total reads; a plateau indicates saturation. For cross-condition peak-count comparison: pick a common depth (often 30M unique reads), subsample with `samtools view -s 0.<frac>` to that depth, THEN call peaks.

## IP-over-Input bigWig for Downstream Visualisation

**Goal:** Produce a per-bin log2 (IP / Input) coverage track per replicate, ready for downstream metagene / browser plots.

**Approach:** deepTools `bamCompare` with `--operation log2`; choose a sensible pseudocount to avoid divide-by-zero at low-coverage bins.

```bash
mkdir -p tracks

paste -d ' ' \
    <(printf '%s\n' IP_rep1 IP_rep2 IP_rep3) \
    <(printf '%s\n' Input_rep1 Input_rep2 Input_rep3) | \
while read ip input; do
    bamCompare \
        -b1 aligned/${ip}_Aligned.sortedByCoord.out.bam \
        -b2 aligned/${input}_Aligned.sortedByCoord.out.bam \
        --operation log2 \
        --pseudocount 1 \
        --binSize 25 \
        --normalizeUsing CPM \
        --numberOfProcessors 8 \
        -o tracks/${ip}_over_${input}.bw
done
```

`--pseudocount 1` prevents division-by-zero at zero-coverage bins; `--binSize 25` is fine-grained enough to preserve peak topology while keeping bigWig files reasonably sized.

## Per-Method Failure Modes

### Dedup applied to non-UMI MeRIP

**Trigger:** `picard MarkDuplicates REMOVE_DUPLICATES=true` invoked on a standard MeRIP BAM that has no UMI.

**Mechanism:** Standard MeRIP libraries have no unique molecular identifiers. PCR duplicates and biological re-sampling at high-coverage transcripts look identical at the alignment level. Dedup removes both, collapsing real coverage at the most-abundant transcripts to an artificially flat profile. This is the opposite of dedup's intent in DNA ChIP-seq.

**Symptom:** Coverage at housekeeping mRNAs (e.g., GAPDH, ACTB) drops 5-20x after dedup; downstream peak counts at highly-expressed transcripts collapse; volcano plot of differential peaks shows expression-driven false positives.

**Fix:** Skip dedup for standard non-UMI MeRIP. If the library is UMI-MeRIP, use `umi_tools dedup` (Smith 2017 *Genome Res* 27:491) which respects UMI rather than alignment position alone. Record dedup status in sample-sheet metadata.

### Transcriptome alignment for downstream peak calling

**Trigger:** STAR or bowtie2 aligned to transcriptome FASTA, then BAM passed to exomePeak2 / MeTPeak / MACS3.

**Mechanism:** exomePeak2 and MeTPeak expect a GENOME BAM plus GTF; they project peaks back to transcript features internally. A transcriptome BAM has reads in per-transcript coordinates which the GTF cannot resolve back to genome coordinates without re-alignment.

**Symptom:** exomePeak2 throws errors on TxDb-genome consistency; MeTPeak returns zero peaks; MACS3 calls peaks on transcript IDs as if they were chromosomes.

**Fix:** Align to GENOME with STAR / HISAT2 for downstream MeRIP peak calling. Transcriptome alignment is correct only for `m6anet-analysis` (ONT DRS) and rare quantification-only downstream tools.

### Failed IP indistinguishable from input

**Trigger:** A single replicate IP library has IP/input ratio distribution centred at 1.0 across all transcripts (no enrichment); fingerprint Lorenz curve sits at the diagonal.

**Mechanism:** Failed IP — antibody-RNA binding did not enrich m6A-containing fragments. Causes include antibody-batch defect, insufficient pulldown wash, RNA degradation during IP, or accidental mock IgG IP.

**Symptom:** plotFingerprint shows IP overlaying input on the Lorenz plot; per-transcript IP/input ratio histogram is centred at 1.0; downstream peak callers find few or no peaks AT THE FAILED REPLICATE while other replicates produce normal counts.

**Fix:** Identify the failed replicate via plotFingerprint AND IP/input ratio distribution BEFORE peak calling; exclude or re-do. Single failed IP in a 3-replicate design routinely produces "differential" peaks driven entirely by the failure.

### Antibody lot mismatch across samples

**Trigger:** A multi-condition MeRIP study uses Synaptic Systems 202-003 antibody lot A for the control IPs and lot B for the treatment IPs (because lot A ran out mid-study).

**Mechanism:** Anti-m6A polyclonals (Synaptic Systems 202-003, Abcam ab151230, NEB EpiMark E1610, Cell Signaling 56593, Active Motif 61755) have batch-to-batch variability in pulldown efficiency and m6A-vs-m6Am cross-reactivity. Pooling lot-A and lot-B counts in a downstream differential model attributes lot-effect to condition.

**Symptom:** "Differential" peaks at high abundance transcripts; effect sizes track antibody lot rather than condition; reanalysis with lot in the design matrix removes most differential peaks.

**Fix:** Record `antibody_clone` and `antibody_lot` per sample in metadata; include `lot` as a fixed effect in downstream differential analysis. Within a single study, ideally use a single lot for ALL replicates and ALL conditions.

### Peak counts compared across libraries of different depth

**Trigger:** "Condition A has 14,000 peaks; condition B has 22,000 peaks; condition B has more m6A."

**Mechanism:** Peak count is library-size-dependent. A library at 60M unique reads finds more peaks than 30M. Without rarefaction or saturation correction, peak-count comparisons across libraries are dominated by sequencing depth.

**Symptom:** Peak counts track total mapped reads more closely than they track biological condition; downstream "biological m6A change" claims do not survive rarefaction-to-common-depth.

**Fix:** Either rarefy all BAMs to common unique-read depth before peak calling, OR fit saturation curves with PreSeq `lc_extrap` and compare at matched depth, OR report peak count alongside the saturation curve.

### Random hexamer priming over-trim

**Trigger:** Aggressive 5' trimming of the first 6-12 nt to remove "random hexamer priming bias" applied to MeRIP libraries.

**Mechanism:** Random hexamer priming bias affects the 5' nucleotide composition of reads but does NOT degrade downstream peak-calling accuracy. Over-trimming removes biological signal and shortens reads enough to inflate multi-mapper fraction.

**Fix:** Standard adapter trimming with `--length_required 25` is sufficient; do not 5'-trim for hexamer bias unless downstream tooling explicitly requires unbiased 5' ends (most do not). The bias is a known artifact in the RNA-seq community and is robust to standard analytical pipelines.

## Reconciliation: When QC Signals Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| plotFingerprint diagonal but IP/input ratio shows enrichment | Mismatched chromosome naming (chr1 vs 1) between samples | Verify `samtools view -H bam | grep '@SQ'` matches across samples |
| Replicate Spearman 0.95 but plotFingerprint diverges | Replicates correlate in bulk but differ in IP enrichment depth | Check per-sample sequencing depth; reduce to common depth |
| Saturation curve plateaus early but peak count low | Library complexity exhausted (e.g., over-amplified PCR) | Inspect duplicate rate; re-prep library if possible |
| MultiQC reports input has higher mapping rate than IP | IP enriches non-canonical sequences (m6A on intronic RNA, mt-RNA) that map differently | Acceptable if STAR multi-mapper retention is on; verify with idxstats |
| Properly-paired rate < 60% | Insert size distribution off (RNA degradation; library prep failure) | Inspect `samtools view -f 0x2` count; re-prep if severe |
| HISAT2 reports many `discordant` pairs | Splice-junction not captured in index | Re-build with `--dta` and confirm GTF matches genome |
| plotFingerprint synthetic JS distance < 0.5 | Marginal IP enrichment; borderline failed | Inspect per-transcript IP/input ratio distribution; consider exclusion |

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|----------|-----------|--------------------|
| Minimum read length after trimming | 25 nt | Below this, multi-mapping fraction inflates; downstream peak callers lose specificity |
| STAR `--outFilterMultimapNmax` for MeRIP | 20 | Retains multi-isoform mapping; tighten to 1 only when downstream cannot tolerate |
| `--sjdbOverhang` | read length - 1 | STAR convention; 100 is common for 100-150 bp reads |
| Properly-paired rate (samtools flagstat) | >=85% | Below indicates degraded RNA or library-prep failure |
| Replicate Spearman correlation (multiBamSummary 10 kb bins) | >=0.85 (IP-vs-IP within condition) | Below suggests one replicate is anomalous |
| plotFingerprint IP-vs-input JS distance | >=0.5 | Higher indicates better IP enrichment; <0.3 suggests failed IP |
| Saturation curve plateau depth | ~30-60M unique reads typical | Below this, peak calling under-samples; depth depends on cell type / antibody |
| Per-transcript IP/input ratio median | >1.5 (genome-wide median) | Lower suggests failed IP; conditions / cell lines vary |
| Minimum biological replicates | 3 (4-5 preferred) per condition | McIntyre 2020 *Sci Rep* 10:6590 — N=2 routinely under-powered |
| Dedup status for non-UMI MeRIP | OFF | Standard convention; UMI-MeRIP is the only exception |
| BAM sort order for downstream tools | Coordinate (SortedByCoordinate) | exomePeak2, MeTPeak, MACS3, deepTools all expect coordinate sort |
| `bamCompare --binSize` for downstream metagene | 25 | Fine enough to preserve peak topology; coarser only for whole-chromosome browser views |
| `bamCompare --pseudocount` | 1 | Prevents divide-by-zero at zero-coverage bins; larger values flatten signal |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| STAR runs out of memory on human genome | --genomeDir build needs ~30 GB RAM | Use HISAT2 (~12 GB) or run STAR on a high-memory node |
| `samtools index` fails with "is not coordinate sorted" | BAM is name-sorted or unsorted | Re-run `samtools sort` (not `sort -n`) |
| exomePeak2 errors on TxDb chromosome mismatch | BAM uses chr1, GTF uses 1 (or reverse) | Verify with `samtools view -H bam | head` and `head genes.gtf`; reconcile with `seqlevelsStyle()` in R or rename in shell |
| deepTools `bamCompare --ratio log2` deprecation warning | Newer deepTools uses `--operation log2` | Switch to `--operation log2` |
| PreSeq `lc_extrap` rejects with "low complexity" | Library too shallow OR genome too small (BAM under 1M unique reads) | Use `c_curve` only; or sequence deeper |
| MultiQC misses STAR Log.final.out | STAR output naming non-standard | Re-run with `--outFileNamePrefix` and rerun MultiQC; check `multiqc_config.yaml` search patterns |
| `picard MarkDuplicates` collapses all reads to 1 per position | Tiny BAM or single read pair per fragment | Verify BAM has many properly-paired reads; do NOT dedup non-UMI MeRIP regardless |
| Empty fingerprint output | All BAMs have identical bin coverage | Verify BAMs are different files; check `multiBamSummary --outRawCounts` |
| bigWig file size too large | Bin size too small at deep coverage | Increase `--binSize` from 25 to 50; bigWig is lossy at large bin sizes |
| Saturation curve never plateaus | Library deeply under-sampled | Sequence deeper OR accept curve does not plateau and report accordingly |
| `fastp --umi` errors on non-UMI library | UMI flag passed but library has no UMI | Drop `--umi` flag for standard non-UMI MeRIP |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Was deduplication applied?" | No — standard non-UMI MeRIP protocol; PCR duplicate vs biological resampling indistinguishable without UMI; dedup collapses real coverage at high-expression transcripts |
| "What is the IP enrichment QC?" | deepTools plotFingerprint reported per replicate; JS distance >=0.5 vs input |
| "Are the replicates concordant?" | Spearman correlation matrix reported via deepTools plotCorrelation on 10 kb bins; IP-IP within condition >=0.85 |
| "Saturation curve?" | PreSeq lc_extrap per library; libraries rarefied to common depth before downstream peak calling |
| "What antibody clone and lot?" | Recorded per sample in metadata; same lot for all replicates within study |
| "Why STAR instead of HISAT2?" | STAR splice-junction-DB-based vs HISAT2 graph-based; both valid for MeRIP; choice driven by memory budget |
| "How many biological replicates?" | N >=3 per condition (per McIntyre 2020); N=2 is under-powered for differential downstream |
| "Was alignment to genome or transcriptome?" | Genome (required for exomePeak2 / MeTPeak / MACS3 downstream); transcriptome alignment is for m6anet-analysis only |

## References

- Dobin A, Davis CA, Schlesinger F et al (2013) STAR: ultrafast universal RNA-seq aligner. *Bioinformatics* 29(1):15-21. doi:10.1093/bioinformatics/bts635
- Kim D, Paggi JM, Park C, Bennett C, Salzberg SL (2019) Graph-based genome alignment and genotyping with HISAT2 and HISAT-genotype. *Nat Biotechnol* 37(8):907-915. doi:10.1038/s41587-019-0201-4
- Vasimuddin Md, Misra S, Li H, Aluru S (2019) Efficient Architecture-Aware Acceleration of BWA-MEM for Multicore Systems. *IPDPS* 314-324. doi:10.1109/IPDPS.2019.00041
- Chen S, Zhou Y, Chen Y, Gu J (2018) fastp: an ultra-fast all-in-one FASTQ preprocessor. *Bioinformatics* 34(17):i884-i890. doi:10.1093/bioinformatics/bty560
- Ramírez F, Ryan DP, Grüning B et al (2016) deepTools2: a next generation web server for deep-sequencing data analysis. *Nucleic Acids Res* 44(W1):W160-W165. doi:10.1093/nar/gkw257
- Diaz A, Park K, Lim DA, Song JS (2012) Normalization, bias correction, and peak calling for ChIP-seq. *Stat Appl Genet Mol Biol* 11(3):Article 9. doi:10.1515/1544-6115.1750
- Daley T, Smith AD (2013) Predicting the molecular complexity of sequencing libraries. *Nat Methods* 10(4):325-327. doi:10.1038/nmeth.2375
- Smith T, Heger A, Sudbery I (2017) UMI-tools: modeling sequencing errors in Unique Molecular Identifiers to improve quantification accuracy. *Genome Res* 27(3):491-499. doi:10.1101/gr.209601.116
- McIntyre ABR, Gokhale NS, Cerchietti L, Jaffrey SR, Horner SM, Mason CE (2020) Limits in the detection of m6A changes using MeRIP/m6A-seq. *Sci Rep* 10(1):6590. doi:10.1038/s41598-020-63355-3
- Ewels P, Magnusson M, Lundin S, Käller M (2016) MultiQC: summarize analysis results for multiple tools and samples in a single report. *Bioinformatics* 32(19):3047-3048. doi:10.1093/bioinformatics/btw354
- Dominissini D, Moshitch-Moshkovitz S, Schwartz S et al (2012) Topology of the human and mouse m6A RNA methylomes revealed by m6A-seq. *Nature* 485(7397):201-206. doi:10.1038/nature11112
- Meyer KD, Saletore Y, Zumbo P, Elemento O, Mason CE, Jaffrey SR (2012) Comprehensive analysis of mRNA methylation reveals enrichment in 3' UTRs and near stop codons. *Cell* 149(7):1635-1646. doi:10.1016/j.cell.2012.05.003

## Related Skills

- m6a-peak-calling - Immediate downstream consumer of the IP/input BAM pairs
- m6a-differential - Downstream differential analysis on peak count matrices; design matrix relies on IP/input pairing recorded here
- m6anet-analysis - ONT DRS alternative; uses TRANSCRIPTOME alignment with minimap2, NOT the genome BAMs produced here
- modification-visualization - Uses the bigWig output of bamCompare for metagene plots and browser tracks
- read-qc/quality-reports - FastQC / MultiQC upstream of trimming
- read-alignment/star-alignment - General STAR splice-aware alignment patterns
- read-alignment/hisat2-alignment - HISAT2 graph-based alternative; general usage
- alignment-files/sam-bam-basics - General BAM mechanics, samtools fundamentals
- alignment-files/bam-statistics - flagstat / idxstats / per-chromosome counts
- alignment-files/duplicate-handling - General dedup philosophy (note: NOT applicable to non-UMI MeRIP)
- chip-seq/chipseq-qc - ChIP-seq IP QC concepts (FRiP, fingerprint, library complexity) that transfer directly
- chip-seq/peak-calling - General IP-vs-input peak-calling concepts
- clip-seq/clip-preprocessing - Antibody-RNA crosslink protocols (miCLIP / m6A-CLIP) overlap with MeRIP design
- rna-quantification/featurecounts-counting - Count matrix construction for downstream differential
- workflows/rnaseq-to-de - End-to-end pipeline orchestration patterns
<!-- END FILE: epitranscriptomics/merip-preprocessing/SKILL.md -->

## 子目录：epitranscriptomics/modification-visualization

<!-- BEGIN FILE: epitranscriptomics/modification-visualization/SKILL.md -->
---
name: bio-epitranscriptomics-modification-visualization
description: Visualises RNA-modification data with transcript-feature metagene plots (Guitar GuitarPlot; MetaPlotR; deepTools computeMatrix scale-regions), peak-centred heatmaps (ComplexHeatmap; deepTools plotHeatmap), IP-vs-input paired browser tracks (log2 IP/input bigWig via deepTools bamCompare; pyGenomeTracks; Gviz; IGV/UCSC track hubs), DRACH sequence-logo plots (ggseqlogo; MEME), feature-distribution stacked bars, and volcano/MA plots for differential modification. Establishes stop-codon enrichment in the metagene plot as the biological QC anchor for any MeRIP dataset (Dominissini 2012; Meyer 2012). Use when producing the canonical metagene plot with stop-codon enrichment as a QC anchor, building paired IP/input genome-browser tracks at single-locus resolution, plotting peak-centred heatmaps clustered by condition, summarising peak distribution across transcript features, generating DRACH motif logos as sanity checks, rendering volcano plots of differential m6A, or reproducing the stop-codon enrichment plot.
tool_type: mixed
primary_tool: Guitar
---

## Version Compatibility

Reference examples tested with: Guitar 2.18+ (Bioconductor), MetaPlotR (GitHub, unversioned), deepTools 3.5+, ggcoverage 1.4+, pyGenomeTracks 3.8+, Gviz 1.46+, ComplexHeatmap 2.18+, ggseqlogo 0.2+, ggplot2 3.5+, rtracklayer 1.62+, GenomicFeatures 1.54+, BSgenome.Hsapiens.UCSC.hg38 1.4+, TxDb.Hsapiens.UCSC.hg38.knownGene 3.18+, ChIPseeker 1.38+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('Guitar')` then `?GuitarPlot` to verify parameters
- CLI: `<tool> --help`; `deepTools <tool> --help`

If R throws `unused argument` or `argument is missing`, the API moved between Bioconductor minor releases. Guitar's older API used `txdb=` while newer uses `txTxdb=`; verify with `?GuitarPlot`. deepTools `bamCompare --operation log2` is the modern syntax (older `--ratio log2` is being phased out).

# RNA Modification Visualisation

**"Make the canonical m6A metagene plot for my paper"** -> Render the 5'UTR / CDS / 3'UTR transcript-feature metagene with stop-codon enrichment for visual confirmation of the canonical m6A topology (THE smoke test that the antibody-IP captured real m6A), the peak-feature-distribution stacked bar ("where do my peaks land?" Figure 1), peak-centred heatmaps clustered by condition, IP-over-Input paired browser tracks at specific loci, the DRACH sequence logo as a sanity check on antibody specificity, and the volcano / MA plots for differential modification. CRITICAL: the stop-codon enrichment plot is a biological-QC anchor — a MeRIP dataset that does NOT show enrichment at and around the stop codon indicates IP failure, wrong antibody, wrong protocol, or the assay captured a different modification (e.g., m1A is centred at TSS, not stop). Build this plot FIRST as a smoke test BEFORE any downstream visualisation.

- R: `Guitar::GuitarPlot(peakBedFiles, txTxdb=...)` -- canonical transcript-feature metagene (THE field-standard plot)
- CLI: `deeptools computeMatrix scale-regions ...` + `plotProfile` -- genome-coordinate metagene
- R: `ComplexHeatmap::Heatmap()` on peak-centred signal matrix -- peak-centred heatmap clustered by condition
- CLI: `pyGenomeTracks --tracks tracks.ini --region chr:start-end` -- multi-track browser plot
- R: `ggcoverage::ggcoverage(data=track, mark.region=peaks)` + `geom_gene()` -- ggplot2-based browser tracks
- R: `ggseqlogo::ggseqlogo(seqs)` -- DRACH sequence logo from peak-centre 5-mers
- R: `ChIPseeker::annotatePeak()` + `ggplot2` stacked bar -- 5'UTR / CDS / 3'UTR feature distribution

## The Single Most Important Modern Insight -- Stop-codon enrichment in the metagene plot is the biological QC anchor — a MeRIP dataset without it is suspect

Dominissini 2012 *Nature* 485:201 and Meyer 2012 *Cell* 149:1635 — concurrent papers from different labs using different protocols (MeRIP-seq and m6A-seq, respectively) — both independently showed m6A enrichment at and around the stop codon (3'UTR-proximal end of the CDS). This is the most robust biological signal in MeRIP-seq, reproduced across cell types, conditions, and decades. A metagene plot from a MeRIP library that does NOT show stop-codon enrichment indicates: (1) IP failure (antibody did not bind), (2) wrong antibody, (3) wrong protocol (e.g., the assay actually captured a different modification — m1A is centred at TSS, not stop), or (4) sample-RNA degradation. Build the Guitar metagene plot FIRST after peak calling, BEFORE any downstream visualisation, as a smoke test. The corollary: the 5'UTR / CDS / 3'UTR feature-distribution stacked bar (the "where do m6A peaks land?" Figure 1) should always be PAIRED with the metagene plot, because the stacked bar can look right (peaks land in 3'UTR / stop area) while the metagene is off (peak DENSITY not concentrated at the codon itself), or vice versa. The two plots are complementary biology-QC anchors, not redundant.

## Algorithmic Taxonomy

| Tool / plot | Mechanism | Inputs | Output | Strength | Fails when |
|-------------|-----------|--------|--------|----------|------------|
| Guitar GuitarPlot (Cui 2016 *Biomed Res Int* 2016:8367534) | Per-peak distance computation relative to TSS / start / stop / TES; feature-scaled rendering | BED + TxDb | PDF + per-feature density | THE field-standard m6A metagene; transcript-feature-aware | Older / newer API uses `txdb=` vs `txTxdb=` argument |
| MetaPlotR (Olarerin-George 2017 *Bioinformatics* 33:1563) | Alternative metagene approach with different segment-rescaling | BED + GTF | PDF | Alternative segment rescaling philosophy | GitHub-only; less actively maintained |
| deepTools computeMatrix + plotProfile (Ramírez 2016 *NAR* 44:W160) | Genome-coordinate signal aggregation over scaled gene regions | bigWig + BED | PDF + matrix | Fast; flexible region/anchor choice; well-tested ChIP-seq lineage | Not transcript-feature-aware; misses 5'UTR / CDS / 3'UTR distinction |
| deepTools plotHeatmap | Same matrix as plotProfile; rendered as heatmap with row clustering | bigWig matrix | PDF | Standard peak-centred heatmap | Single-condition view (use ComplexHeatmap for multi-condition clustering) |
| ComplexHeatmap (Gu 2016 *Bioinformatics* 32:2847) | General-purpose heatmap with multi-dimensional clustering | numeric matrix | PDF / interactive | Multi-condition cluster + annotation; publication-quality | Requires pre-computed signal matrix |
| pyGenomeTracks (Lopez-Delisle 2021 *Bioinformatics* 37:422) | Config-file (INI) driven multi-track browser plot | bigWig / bed / GTF + INI config | PDF / PNG | Reproducible browser figures via config; multi-track stacking | INI config syntax error-prone for new users |
| ggcoverage (Song & Wang 2023 *BMC Bioinformatics* 24:309) | ggplot2-native track plotting | bigWig / BAM + GTF | ggplot2 object | ggplot2 syntax; combinable with annotation layers | Newer tool; smaller user base than Gviz |
| Gviz (Hahne & Ivanek 2016 *Methods Mol Biol* 1418:335) | R/Bioconductor general genome track | bigWig / BAM / GRanges + TxDb | PDF / R plot | Most flexible R-native; long Bioconductor history | Heavier than ggcoverage; steeper learning curve |
| IGV / IGV.js (Robinson 2011 *Nat Biotechnol* 29:24) | Interactive browser via Java / JS | bigWig / BAM / bed | interactive | Standard for ad-hoc inspection | Not reproducible for figure generation |
| UCSC Track Hubs | UCSC genome browser display | bigWig + hub.txt + genomes.txt | URL | Public-display standard | Setup overhead for short projects |
| ggseqlogo (Wagih 2017 *Bioinformatics* 33:3645) | Sequence-logo rendering in ggplot2 | character vector of equal-length sequences | ggplot2 object | Native ggplot2; method='bits' or 'probability' | Requires equal-length sequences |
| MEME-ChIP (Machanick & Bailey 2011 *Bioinformatics* 27:1696) | Motif discovery + logo | BED + genome | HTML + PWM | Comprehensive motif suite; gold standard | Heavier than ggseqlogo for simple visualisation |
| HOMER findMotifsGenome.pl (Heinz 2010 *Mol Cell* 38:576) | Motif discovery via cumulative hypergeometric on shuffled background | BED + genome | HTML + motif files | Battle-tested; RNA mode via `-rna` | Less flexible output formatting than MEME |

## Decision Tree by Scenario

| Scenario | Recommended | Why wrong choices fail |
|----------|-------------|------------------------|
| Canonical Figure 1 metagene plot for m6A paper | Guitar GuitarPlot with TxDb -- transcript-feature scaled | deepTools computeMatrix is genome-coordinate only; misses 5'UTR / CDS / 3'UTR distinction |
| QC: does my MeRIP show stop-codon enrichment? | Guitar GuitarPlot FIRST -- the canonical biological-QC anchor | Skipping this and rushing to peak counting is the most common QC failure |
| Browser-track Figure for a specific locus | pyGenomeTracks (config-file driven; reproducible) OR ggcoverage (ggplot2-native) | IGV is interactive but not reproducible for figures |
| Multi-condition peak-centred heatmap with clustering | ComplexHeatmap; row-cluster k-means; annotate by condition | deepTools plotHeatmap is single-condition view |
| DRACH sequence logo from peak centres | ggseqlogo on resized peak ranges (width=5, fix='center') | MEME-ChIP heavier than needed for visualisation only |
| Differential m6A volcano plot | ggplot2 native (see m6a-differential) -- modification-visualization should NOT duplicate | Duplicating volcano recipe across skills inflates content |
| Genome-coordinate metagene over custom features | deepTools computeMatrix scale-regions; plotProfile | Guitar restricted to transcript features; doesn't scale to arbitrary BED |
| Cross-sample paired IP/input track display | bamCompare -> log2 bigWig; pyGenomeTracks multi-track | Single bigWig hides the IP/input pairing structure |
| 5'UTR / CDS / 3'UTR stacked bar | ChIPseeker annotatePeak -> ggplot2 stacked bar | Manual annotation error-prone; ChIPseeker handles edge cases |
| Reproducing Dominissini 2012 / Meyer 2012 stop-codon plot | Guitar GuitarPlot; the canonical recipe | Other tools produce similar but not identical plots |

Methodology evolves; before high-stakes figure generation, web-search "Guitar Bioconductor release notes" and "pyGenomeTracks vs ggcoverage" for current best practice.

## Guitar Transcript-Feature Metagene (THE Canonical Plot)

**Goal:** Render the canonical m6A metagene plot showing peak density along scaled transcript features (5'UTR, CDS, 3'UTR), with the stop-codon-proximal enrichment that is the field's biological QC anchor.

**Approach:** Load called peaks from BED; pass to GuitarPlot with the matched TxDb; export per-feature density and the PDF.

```r
library(Guitar)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(rtracklayer)

txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene

# Older Guitar versions: argument is `txdb=`; newer: `txTxdb=`. Verify with ?GuitarPlot.
GuitarPlot(
    txTxdb           = txdb,
    stBedFiles       = list('exomepeak2_output/m6a_run1/peaks.bed'),
    miscOutFilePrefix = 'figures/m6a_metagene',
    enableCI         = FALSE,
    saveToPDFprefix  = 'figures/m6a_metagene'
)
```

If `txTxdb=` is rejected, fall back to `txdb=` and consult `?GuitarPlot`. The expected output: stop-codon-proximal enrichment, with peak density rising toward and peaking near the stop codon in the 3'UTR. If the plot does NOT show this pattern, do not proceed to downstream visualisation — investigate IP / antibody / protocol failure in merip-preprocessing.

## deepTools Genome-Coordinate Metagene

**Goal:** Render a genome-coordinate metagene over scaled gene regions using deepTools, useful when transcript-feature scaling is not needed or when the regions of interest are not standard genes (custom BED).

**Approach:** Build a signal matrix with `computeMatrix scale-regions` from a bigWig (typically IP-over-Input log2 from merip-preprocessing); render as profile plot + heatmap.

```bash
mkdir -p figures

computeMatrix scale-regions \
    --regionsFileName refs/protein_coding.bed \
    --scoreFileName tracks/IP_rep1_over_Input_rep1.bw \
    --regionBodyLength 2000 \
    --upstream 500 \
    --downstream 500 \
    --skipZeros \
    --numberOfProcessors 8 \
    --outFileName figures/m6a_matrix.gz

plotProfile \
    --matrixFile figures/m6a_matrix.gz \
    --outFileName figures/m6a_profile.pdf \
    --plotTitle 'm6A IP over Input metagene' \
    --plotType lines

plotHeatmap \
    --matrixFile figures/m6a_matrix.gz \
    --outFileName figures/m6a_heatmap.pdf \
    --colorMap RdBu_r \
    --plotTitle 'm6A IP over Input heatmap'
```

`scale-regions` is the right mode for gene-body metagene (5'-end-to-3'-end scaled to common length); `reference-point` is for peak-centred plots. For peak-centred, see the next section.

## Peak-Centred Heatmap

**Goal:** Render a peak-centred heatmap of IP-over-Input signal at +/-window around each peak, clustered by condition or by signal pattern, for cross-condition comparison.

**Approach:** Use deepTools `computeMatrix reference-point --referencePoint center` for the matrix; ComplexHeatmap for the clustered render.

```bash
computeMatrix reference-point \
    --regionsFileName exomepeak2_output/m6a_run1/peaks.bed \
    --scoreFileName tracks/IP_rep1_over_Input_rep1.bw tracks/IP_rep2_over_Input_rep2.bw tracks/IP_rep3_over_Input_rep3.bw \
    --referencePoint center \
    --upstream 500 \
    --downstream 500 \
    --binSize 25 \
    --skipZeros \
    --numberOfProcessors 8 \
    --outFileName figures/peak_centred_matrix.gz \
    --outFileNameMatrix figures/peak_centred_matrix.tab

plotHeatmap \
    --matrixFile figures/peak_centred_matrix.gz \
    --outFileName figures/peak_centred_heatmap.pdf \
    --kmeans 3 \
    --colorMap viridis \
    --plotTitle 'm6A signal centred at peaks'
```

For multi-condition heatmap with annotations, parse the matrix into R and use ComplexHeatmap:

```r
library(ComplexHeatmap)
library(circlize)

# deepTools --outFileNameMatrix has a 3-line JSON-style header before per-bin numeric columns.
raw <- read.delim('figures/peak_centred_matrix.tab', skip=3, header=FALSE)
mat <- as.matrix(raw[, -(1:6)])

col_fun <- colorRamp2(c(-2, 0, 2), c('blue', 'white', 'red'))

Heatmap(
    mat,
    name              = 'log2 IP / Input',
    col               = col_fun,
    cluster_columns   = FALSE,
    cluster_rows      = TRUE,
    row_km            = 3,
    show_row_names    = FALSE,
    show_column_names = FALSE,
    column_title      = 'Peak-centred (+/- 500 bp)'
)
```

## IP-vs-Input Paired Browser Tracks via pyGenomeTracks

**Goal:** Render publication-quality genome-browser tracks at a specific locus showing paired IP / Input bigWig tracks, the IP/input log2 ratio, peak calls, and gene annotation; reproducible via INI config.

**Approach:** Build a `tracks.ini` config file listing each track type (bigwig, bed, gtf); invoke `pyGenomeTracks --tracks tracks.ini --region chr:start-end`.

```ini
[x-axis]
where = top
fontsize = 12

[IP rep1]
file = tracks/IP_rep1.bw
title = IP rep1
color = #d62728
height = 2
min_value = 0

[Input rep1]
file = tracks/Input_rep1.bw
title = Input rep1
color = #1f77b4
height = 2
min_value = 0

[IP / Input log2]
file = tracks/IP_rep1_over_Input_rep1.bw
title = log2 IP / Input
color = #2ca02c
height = 2

[spacer]

[m6A peaks]
file = exomepeak2_output/m6a_run1/peaks.bed
title = m6A peaks (exomePeak2)
color = #ff7f0e
height = 1
labels = false

[genes]
file = refs/annotation.gtf
title = GENCODE genes
height = 2
prefered_name = gene_name
merge_transcripts = true
```

```bash
pyGenomeTracks \
    --tracks tracks.ini \
    --region chr19:54,792,000-54,799,000 \
    --outFileName figures/browser_metti3_locus.pdf \
    --width 14 \
    --plotWidth 12
```

## ggcoverage ggplot2-Native Browser Track

**Goal:** Render genome-browser tracks in ggplot2 syntax for combining with other ggplot2 layers (annotations, peak highlights, custom theming).

**Approach:** `LoadTrackFile()` parses a bigWig / bigBed / BAM input into the dataframe ggcoverage expects; chain `ggcoverage()` with `geom_gene()` for transcript annotation; `mark.region` requires columns `start`, `end`, and `label`.

```r
library(ggcoverage)
library(rtracklayer)

peaks <- as.data.frame(import('exomepeak2_output/m6a_run1/peaks.bed'))

track.df <- LoadTrackFile(
    track.file = 'tracks/IP_rep1_over_Input_rep1.bw',
    format     = 'bw',
    region     = 'chr19:54792000-54799000'
)

mark.df <- data.frame(
    start = peaks$start,
    end   = peaks$end,
    label = peaks$name
)

ggcoverage(
    data        = track.df,
    color       = 'auto',
    mark.region = mark.df
) +
    geom_gene(gtf.file = 'refs/annotation.gtf') +
    ggplot2::theme_classic()
```

## DRACH Sequence Logo

**Goal:** Render a sequence logo of peak-centre 5-mers as a sanity check that the called peak set is enriched for the DRACH consensus motif.

**Approach:** Resize peak GRanges to fixed 5-nt centred windows; extract genomic sequences; pass to ggseqlogo with `method='probability'`.

```r
library(Biostrings)
library(BSgenome.Hsapiens.UCSC.hg38)
library(ggseqlogo)
library(rtracklayer)

peaks <- import('exomepeak2_output/m6a_run1/peaks.bed')

peak_centres <- resize(peaks, width=5, fix='center')

genome <- BSgenome.Hsapiens.UCSC.hg38
seqs <- as.character(getSeq(genome, peak_centres))

ggseqlogo(seqs, method='probability') +
    ggplot2::labs(title='Peak-centre 5-mer (DRACH consensus expected)',
                  subtitle='Sanity check on antibody specificity — NOT a per-peak filter')
```

The expected output: a logo showing approximately D-R-A-C-H consensus (D=A/G/U, R=A/G, A=methylated, C, H=A/C/U) with A clearly dominating position 3. If the logo does NOT show DRACH-like enrichment, the IP failed OR the wrong antibody was used.

## 5'UTR / CDS / 3'UTR Stacked Bar

**Goal:** Render the Figure 1 "where do my peaks land?" stacked bar showing the fraction of peaks in 5'UTR vs CDS vs 3'UTR vs intron, paired with the metagene to confirm canonical m6A topology.

**Approach:** Use ChIPseeker `annotatePeak()` with a matched TxDb; aggregate to per-feature counts; render as ggplot2 stacked bar.

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(rtracklayer)
library(ggplot2)
library(dplyr)

txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene
peaks <- import('exomepeak2_output/m6a_run1/peaks.bed')

peak_anno <- annotatePeak(peaks, TxDb=txdb, level='transcript', verbose=FALSE)
anno_df <- as.data.frame(peak_anno@anno)

anno_df$feature <- gsub(' \\(.*\\)', '', anno_df$annotation)

feature_counts <- anno_df %>%
    group_by(feature) %>%
    summarise(n=n()) %>%
    mutate(fraction=n/sum(n)) %>%
    arrange(desc(fraction))

ggplot(feature_counts, aes(x='m6A peaks', y=fraction, fill=feature)) +
    geom_col(width=0.5) +
    scale_y_continuous(labels=scales::percent_format()) +
    labs(x=NULL, y='Fraction of peaks', title='m6A peak distribution across transcript features') +
    theme_minimal()
```

## Per-Method Failure Modes

### Metagene without stop-codon enrichment

**Trigger:** Guitar GuitarPlot of called peaks does NOT show enrichment at and around the stop codon.

**Mechanism:** Canonical m6A topology (Dominissini 2012 / Meyer 2012) shows stop-codon-proximal enrichment. Absence indicates (1) IP failure, (2) wrong antibody, (3) wrong protocol, (4) sample-RNA degradation, OR (5) the assay captured a different modification (m1A is TSS-centred; m5C distribution differs).

**Symptom:** Metagene is flat OR peaks at TSS (m1A signature) OR peaks in introns (unusual).

**Fix:** Do NOT proceed to downstream analysis. Diagnose at the merip-preprocessing layer: plotFingerprint, per-transcript IP/input distribution, antibody-lot QC. Re-do the IP if necessary. The metagene plot is the biological QC anchor; without it, all downstream interpretation is suspect.

### DRACH logo not enriched

**Trigger:** ggseqlogo of peak-centre 5-mers shows no consensus, OR shows a non-DRACH-like motif.

**Mechanism:** Antibody specificity failure OR wrong protocol. Anti-m6A antibodies have ~70% DRACH-context enrichment on real m6A peaks; a failed IP captures random sequences with no consensus.

**Fix:** Re-inspect IP enrichment in merip-preprocessing. If IP is clean but DRACH logo is absent, the assay may have captured a different modification — investigate before claiming m6A.

### Guitar `txdb=` vs `txTxdb=` argument confusion

**Trigger:** `GuitarPlot(stBedFiles=..., txdb=txdb)` rejected with "unused argument" error.

**Mechanism:** Guitar changed the argument name between Bioconductor releases — `txdb=` (older) vs `txTxdb=` (newer).

**Fix:** Try alternative; consult `?GuitarPlot` for installed version. Pin Guitar version in reproducible analyses.

### deepTools genome-coordinate metagene used where transcript-feature is needed

**Trigger:** `computeMatrix scale-regions` over a BED of genes used to show "5'UTR / CDS / 3'UTR enrichment".

**Mechanism:** deepTools scales by genomic length, NOT by transcript-feature length. A gene with long 5'UTR and short CDS will scale 5'UTR more than CDS; the metagene loses 5'UTR / CDS / 3'UTR semantics.

**Fix:** Use Guitar (transcript-feature-aware) for 5'UTR / CDS / 3'UTR semantics. Use deepTools for genome-coordinate metagene over arbitrary BED.

### IGV-only browser figure in published paper

**Trigger:** Figure 4 of paper shows an IGV screenshot of one locus; not reproducible from code.

**Mechanism:** IGV is interactive; the figure cannot be re-generated from a config file. Reviewers cannot reproduce the figure if track files change.

**Fix:** Use pyGenomeTracks (INI config) or ggcoverage (ggplot2 script) for figures intended for publication. IGV is for ad-hoc inspection only.

### bamCompare `--ratio log2` deprecation

**Trigger:** Older deepTools syntax `--ratio log2` used; newer requires `--operation log2`.

**Fix:** Switch to `--operation log2`. Both currently work but `--ratio` is being phased out.

### ggseqlogo "sequences must be equal length"

**Trigger:** Mixed-length peak sequences passed to ggseqlogo.

**Mechanism:** ggseqlogo requires equal-length input strings.

**Fix:** Resize peak ranges to fixed width before extraction: `resize(peaks, width=5, fix='center')`.

### pyGenomeTracks INI typo

**Trigger:** Track section header missing brackets, OR `file =` instead of `file=` (whitespace inconsistency).

**Fix:** Use the documented INI syntax precisely; bracketed section headers; consistent whitespace around `=`. Validate with `pyGenomeTracks --tracks tracks.ini --region 'chr:start-end' --outFileName out.pdf` and iterate on errors.

## Reconciliation: When Plots Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Metagene shows stop-codon enrichment but stacked bar has many 5'UTR peaks | 5'UTR peaks are present but density is concentrated at stop codon | Both plots are correct; report together |
| Guitar metagene and deepTools metagene look very different | Guitar transcript-feature-scaled vs deepTools genome-scaled | Both correct; Guitar for 5'UTR / CDS / 3'UTR semantics; deepTools for genome coordinates |
| Peak-centred heatmap shows two clusters; condition annotation crosses cluster boundary | Biological signal not condition-aligned; OR clustering driven by per-peak coverage variance | Inspect per-cluster fold-change; consider removing low-coverage peaks before re-clustering |
| pyGenomeTracks shows IP track higher than Input but bamCompare bigWig shows log2 near zero | Track signal magnitudes are CPM-normalised; absolute counts and log2 ratios are different summaries | Report log2 ratio as the primary; per-track CPM as supplement |
| DRACH logo enriched but stacked bar shows mostly intronic peaks | Intronic m6A (Louloupi 2018 nascent transcripts) | Genuine biology; report intronic vs exonic separately; consider library prep (poly-A vs ribo-depleted) |
| Volcano plot symmetric but most differential peaks in 3'UTR | Differential is feature-restricted | Cross-check with per-feature differential testing; biological interpretation |

## Quantitative Thresholds

| Quantity | Threshold | Source / rationale |
|----------|-----------|--------------------|
| Guitar metagene -- expected pattern | Stop-codon-proximal enrichment, 3'UTR > CDS > 5'UTR density | Dominissini 2012 *Nature* 485:201; Meyer 2012 *Cell* 149:1635 |
| deepTools metagene scaled-region length | 2000 bp body + 500 bp flanks | Convention; covers typical mammalian gene span |
| Peak-centred heatmap window | +/-500 bp around peak centre | Standard convention; covers MeRIP fragment width |
| Peak-centred heatmap k-means clusters | 3-5 typical | Cluster count informed by condition count + signal heterogeneity |
| ggseqlogo expected DRACH pattern | A dominant at position 3 (the methylated A); C dominant at position 4 | DRACH consensus |
| pyGenomeTracks figure width | 10-14 inches | Standard publication width |
| Browser-track region width | 5-50 kb | Locus-context dependent |
| 5'UTR / CDS / 3'UTR / intron+other expected distribution | ~10% / ~30% / ~50% / ~10% for canonical m6A | Per published m6A atlases |
| DRACH logo "method" parameter | 'probability' for visual; 'bits' for information-theoretic | ggseqlogo convention |
| Per-feature stacked bar minimum peaks | >=100 | Below this, fractions are noisy |
| Cross-replicate metagene divergence | Should be near-identical within condition | If replicates' metagenes diverge, failed-IP suspect in merip-preprocessing |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Guitar `txTxdb` rejected | Older version uses `txdb` | Switch argument name; consult `?GuitarPlot` |
| Guitar PDF blank | BED file empty OR chromosome mismatch with TxDb | Verify peak BED has peaks; reconcile chromosome naming |
| deepTools `computeMatrix` errors with "no regions" | BED file empty OR file path wrong | Verify BED is non-empty and path correct |
| pyGenomeTracks INI parse error | Bracket / whitespace inconsistency | Match documented INI syntax exactly |
| ggcoverage region not displayed | Region beyond bigWig coverage; OR chromosome naming mismatch | Verify bigWig contains region; reconcile chr1 vs 1 |
| ggseqlogo throws "equal length" error | Mixed-length sequences | `resize(peaks, width=5, fix='center')` before extracting |
| ComplexHeatmap clustering hangs | Very large peak set (>100k) | Subset to top N peaks; or use deepTools plotHeatmap k-means |
| bamCompare `--ratio log2` deprecation warning | Newer syntax | Switch to `--operation log2` |
| IGV screenshot not reproducible | Interactive tool | Switch to pyGenomeTracks / ggcoverage |
| ggseqlogo logo blank | Empty `seqs` input OR all sequences are gaps / Ns | Verify peak BED resolves to valid genomic sequences via `getSeq()` |
| Stacked bar shows >100% | Peak annotation overlap counted multiple times | Use `annotatePeak` with explicit hierarchy |
| ComplexHeatmap colour scale wrong | colorRamp2 breaks at outliers | Set scale based on robust quantiles (quantile(x, 0.05), 0, quantile(x, 0.95)) |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Does the MeRIP show the canonical stop-codon enrichment?" | Yes — Guitar metagene plot shows expected stop-codon-proximal enrichment; cited Dominissini 2012 / Meyer 2012 |
| "Why Guitar and not deepTools?" | Guitar is transcript-feature-scaled (5'UTR / CDS / 3'UTR semantics); deepTools is genome-coordinate; both reported when needed |
| "Is the DRACH motif enriched?" | ggseqlogo of peak-centre 5-mers; OR HOMER findMotifsGenome.pl E-value reported |
| "Is the browser figure reproducible?" | Yes — pyGenomeTracks INI config OR ggcoverage R script; not IGV screenshot |
| "How were peaks annotated to features?" | ChIPseeker annotatePeak with matched TxDb; hierarchy explicit |
| "Why these specific clusters in the heatmap?" | k-means with k=3 chosen via elbow / silhouette; clusters reflect signal heterogeneity |
| "Does the metagene differ between conditions?" | Per-condition metagenes plotted alongside; differences quantified at the feature level |
| "Why is the colour scheme red-blue?" | Standard convention for log2 ratios (red = up, blue = down); colour-blind-safe palette via viridis available |
| "Was a cross-check with published m6A-Atlas peaks done?" | Common-core overlap reported; cited m6A-Atlas v2 |
| "Are the browser track signal magnitudes comparable across samples?" | bigWig CPM-normalised in merip-preprocessing; documented |

## References

- Dominissini D, Moshitch-Moshkovitz S, Schwartz S et al (2012) Topology of the human and mouse m6A RNA methylomes revealed by m6A-seq. *Nature* 485(7397):201-206. doi:10.1038/nature11112
- Meyer KD, Saletore Y, Zumbo P, Elemento O, Mason CE, Jaffrey SR (2012) Comprehensive analysis of mRNA methylation reveals enrichment in 3' UTRs and near stop codons. *Cell* 149(7):1635-1646. doi:10.1016/j.cell.2012.05.003
- Cui X, Wei Z, Zhang L et al (2016) Guitar: an R/Bioconductor package for gene annotation guided transcriptomic analysis of RNA-related genomic features. *Biomed Res Int* 2016:8367534. doi:10.1155/2016/8367534
- Olarerin-George AO, Jaffrey SR (2017) MetaPlotR: a Perl/R pipeline for plotting metagenes of nucleotide modifications and other transcriptomic sites. *Bioinformatics* 33(10):1563-1564. doi:10.1093/bioinformatics/btx002
- Ramírez F, Ryan DP, Grüning B et al (2016) deepTools2: a next generation web server for deep-sequencing data analysis. *Nucleic Acids Res* 44(W1):W160-W165. doi:10.1093/nar/gkw257
- Gu Z, Eils R, Schlesner M (2016) Complex heatmaps reveal patterns and correlations in multidimensional genomic data. *Bioinformatics* 32(18):2847-2849. doi:10.1093/bioinformatics/btw313
- Lopez-Delisle L, Rabbani L, Wolff J et al (2021) pyGenomeTracks: reproducible plots for multivariate genomic datasets. *Bioinformatics* 37(3):422-423. doi:10.1093/bioinformatics/btaa692
- Song Y, Wang J (2023) ggcoverage: an R package to visualize and annotate genome coverage for various NGS data. *BMC Bioinformatics* 24(1):309. doi:10.1186/s12859-023-05438-2
- Robinson JT, Thorvaldsdóttir H, Winckler W et al (2011) Integrative genomics viewer. *Nat Biotechnol* 29(1):24-26. doi:10.1038/nbt.1754
- Wagih O (2017) ggseqlogo: a versatile R package for drawing sequence logos. *Bioinformatics* 33(22):3645-3647. doi:10.1093/bioinformatics/btx469
- Yu G, Wang LG, He QY (2015) ChIPseeker: an R/Bioconductor package for ChIP peak annotation, comparison and visualization. *Bioinformatics* 31(14):2382-2383. doi:10.1093/bioinformatics/btv145
- Hahne F, Ivanek R (2016) Visualizing Genomic Data Using Gviz and Bioconductor. *Methods Mol Biol* 1418:335-351. doi:10.1007/978-1-4939-3578-9_16
- Heinz S, Benner C, Spann N et al (2010) Simple combinations of lineage-determining transcription factors prime cis-regulatory elements required for macrophage and B cell identities. *Mol Cell* 38(4):576-589. doi:10.1016/j.molcel.2010.05.004
- Machanick P, Bailey TL (2011) MEME-ChIP: motif analysis of large DNA datasets. *Bioinformatics* 27(12):1696-1697. doi:10.1093/bioinformatics/btr189

## Related Skills

- merip-preprocessing - Generates the bigWig tracks (bamCompare log2 IP/input) used here
- m6a-peak-calling - Generates the peak BED used for metagene + stacked bar + heatmap
- m6a-differential - Differential results visualised via volcano + MA (those plots live in m6a-differential, not duplicated here)
- m6anet-analysis - Per-site DRS modification calls; visualisation analogous via metagene
- data-visualization/ggplot2-fundamentals - General ggplot2 grammar
- data-visualization/multipanel-figures - Combining metagene + heatmap + volcano into figures
- data-visualization/heatmaps-clustering - General heatmap clustering patterns
- data-visualization/volcano-and-ma-plots - General volcano / MA recipes (modification-specific volcano lives in m6a-differential)
- data-visualization/genome-tracks - General genome-track rendering (this skill adds the IP/input pairing specifics)
- data-visualization/sequence-logos - General sequence-logo plotting (this skill adds DRACH-specific context)
- chip-seq/chipseq-visualization - Closest sibling for browser-track + peak-centred heatmap patterns
- pathway-analysis/enrichment-visualization - For visualising downstream pathway results
<!-- END FILE: epitranscriptomics/modification-visualization/SKILL.md -->

<!-- END CATEGORY: epitranscriptomics -->

