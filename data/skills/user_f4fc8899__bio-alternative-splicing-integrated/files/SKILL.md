---
slug: bio-alternative-splicing-integrated
version: 1.0.1
displayName: "可变剪接 / Alternative splicing analysis"
name: bio-alternative-splicing-integrated
summary: "中文：可变剪接综合技能，整合 9 个相关专题，覆盖可变剪接分析：rMATS/leafcutter/MAJIQ/SUPPA2事件检测、isoform切换、SpliceAI变异预测、FRASER2异常剪接检测。 English: Integrated Alternative splicing analysis skill covering 9 related topics, including Alternative splicing analysis: rMATS/leafcutter/MAJIQ/SUPPA2 event detection, isoform switching, SpliceAI variant prediction, FRASER2 outlier detection."
description: "中文：这是一个面向可变剪接的综合生物信息学 Skill，整合当前分类下 9 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：可变剪接分析：rMATS/leafcutter/MAJIQ/SUPPA2事件检测、isoform切换、SpliceAI变异预测、FRASER2异常剪接检测。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：FLAIR, FRASER, IsoformSwitchAnalyzeR。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Alternative splicing analysis, combining 9 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Alternative splicing analysis: rMATS/leafcutter/MAJIQ/SUPPA2 event detection, isoform switching, SpliceAI variant prediction, FRASER2 outlier detection. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: FLAIR, FRASER, IsoformSwitchAnalyzeR. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# alternative-splicing 分类 Skill 整合版

> 本文件整合同一主分类目录下 9 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: alternative-splicing -->

## 子目录：alternative-splicing/differential-splicing

<!-- BEGIN FILE: alternative-splicing/differential-splicing/SKILL.md -->
---
name: bio-differential-splicing
description: Detects differential alternative splicing between conditions using rMATS-turbo (binomial LRT on junction counts), leafcutter (Dirichlet-multinomial GLM on intron clusters), MAJIQ V3 deltapsi/HET (Bayesian posterior on LSVs), SUPPA2 (empirical-null on TPM-derived PSI), or Shiba (junction-imbalance-corrected, 2025 SOTA at low coverage). Reports FDR-corrected significance and delta PSI effect sizes. Tools differ in statistical model, annotation dependence, calibration regime, and replicate-count requirements. Use when comparing splicing patterns between treatment groups, tissues, or disease states.
tool_type: mixed
primary_tool: rMATS-turbo
---

## Version Compatibility

Reference examples tested with: rMATS-turbo 4.3+, SUPPA2 2.4+, leafcutter 0.2.9+, MAJIQ 3.0+, Shiba 0.5+, STAR 2.7.11+, regtools 1.0+, pandas 2.2+, R 4.4+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Differential Splicing

Detect splicing changes between conditions. Tool choice is a decision about **statistical model**, **annotation dependence**, and **calibration regime** under the specific experimental design — not a preference. Wrong tool for the design produces uncalibrated FDR or systematic effect-size bias.

## Statistical Model Taxonomy

| Tool | Model | Test statistic | Min reps per group | Calibration regime | Fails when |
|------|-------|-----------------|---------------------|---------------------|------------|
| rMATS-turbo | Binomial counts with hierarchical PSI variance | LRT on \|ΔPSI\| > `cutoff` (default 0.0001) | n>=3 | Well-calibrated at n>=3 with adequate junction reads | Junction read imbalance; very low coverage; uncorrected for confounders |
| leafcutter | Dirichlet-multinomial GLM at cluster level | LRT on group factor | n>=2 (n>=3 preferred) | Strong at n>=3; novel-junction-friendly | Undersampled clusters (DM dispersion unstable); cluster topology arbitrariness |
| MAJIQ deltapsi | Beta-binomial bootstrap -> posterior over PSI per LSV | P(\|ΔPSI\| > T) threshold (T=0.2) | n>=3 | Replicate-structured n=3 vs n=3 | Cohorts where between-sample variability dominates between-group |
| MAJIQ HET | Same model, heterogeneity-aware | Per-LSV permutation-based test | n>=10 | n>=10 vs n>=10 cohort designs | Tightly-controlled small replicate experiments |
| SUPPA2 (empirical) | Empirical null from between-replicate ΔPSI | ECDF on \|ΔPSI\| conditioned on TPM | n>=4 | n>=4 vs n>=4 with paired-end deep sequencing | n<=3 vs n<=3 (sparse null collapses) |
| SUPPA2 (classical) | Wilcoxon rank-sum on PSI distributions | Wilcoxon p-value | n>=2 | Small samples; non-parametric backup | Cassette events with tight PSI distributions |
| Shiba (2025) | Beta-binomial with explicit junction-imbalance correction | LRT | n>=2 | n=2-3 vs n=2-3 | Established benchmarks limited (new tool) |
| LeafcutterMD | Dirichlet-multinomial outlier mode | Per-sample p-value | n=1 vs cohort >=20 | Single-patient vs cohort | Too few controls (<20) |
| FRASER 2.0 | Beta-binomial autoencoder on Intron Jaccard Index | Per-sample p-value with delta cutoff | n=1 vs cohort >=20 | n>=20 control cohort, single-patient query | See `outlier-splicing-detection` for this regime |

The first decision is which **regime** the design falls into: between-group with replicates, heterogeneous cohort, or single-sample-vs-cohort. Within each regime, tool choice is much smaller (1-2 options).

Comprehensive 2023-2026 benchmarks: Olofsson 2023 *Biochem Biophys Res Commun*; Tran 2025 *WIREs RNA*; Kubota 2025 *NAR*. Methodology evolves — verify benchmarks and tool docs before reporting. Default 2026 recommendation: run **two complementary tools** (rMATS + leafcutter) and require concordance for high-confidence calls.

## Decision Tree by Experimental Design

| Scenario | Recommended tool | Why | Threshold |
|----------|------------------|-----|-----------|
| Standard n=3 vs n=3, GENCODE-annotated | rMATS-turbo + leafcutter (concordance) | Two algorithmic families; concordant hits = high-confidence | FDR<0.05, \|ΔPSI\|>0.10 |
| n=2 vs n=2 small pilot | Shiba | Junction-imbalance correction matters most at low coverage | FDR<0.10, \|ΔPSI\|>0.10 |
| n=10+ vs n=10+ heterogeneous (clinical, GTEx-style) | MAJIQ V3 HET | HET designed for between-sample heterogeneity | P(\|ΔPSI\|>0.2)>0.95 |
| Single rare-disease patient vs panel of n>=20 | FRASER 2.0 (see outlier-splicing-detection) | Outlier detection statistical model is fundamentally different | padj<0.05, \|delta-jaccard\|>=0.1 |
| Time-course / multi-condition design | Custom DEXSeq or limma on PSI matrix | rMATS/leafcutter primarily 2-group | FDR<0.05 on time:group interaction |
| Paired tumor-normal | rMATS with `--paired-stats` | Paired test reduces inter-patient variance | FDR<0.05, paired \|ΔPSI\|>0.10 |
| Cancer with spliceosomal mutation (SF3B1, U2AF1) | leafcutter or MAJIQ denovo | Cryptic events not in annotation | FDR<0.05; check 3'ss shifts in IGV |
| TDP-43 loss / ALS post-mortem | leafcutter denovo | Cryptic exons not in annotation | FDR<0.05; expect UNC13A, STMN2 |
| Non-model organism without GENCODE-grade annotation | leafcutter | Annotation-free | FDR<0.05, \|ΔPSI\|>0.10 |
| Long-read available | rMATS-long, FLAIR diffSplice | See long-read-splicing | Tool-specific |

## rMATS-turbo Differential Analysis

**Goal:** Detect statistically significant differential splicing between two groups from BAMs.

**Approach:** Run rMATS-turbo without `--statoff`, then filter by FDR + ΔPSI + per-replicate coverage.

```bash
rmats.py \
    --b1 condition1_bams.txt \
    --b2 condition2_bams.txt \
    --gtf annotation.gtf \
    -t paired \
    --readLength 150 \
    --variable-read-length \
    --libType fr-firststrand \
    --nthread 8 \
    --od rmats_output \
    --tmp rmats_tmp \
    --novelSS \
    --cstat 0.05
```

`--cstat 0.05` tests `|ΔPSI| > 0.05`; raise to 0.10 for stricter discovery. `--novelSS` enables novel-junction discovery (recommended with STAR 2-pass). For paired designs, add `--paired-stats`.

```python
import pandas as pd
import numpy as np

se = pd.read_csv('rmats_output/SE.MATS.JC.txt', sep='\t')

def min_per_rep(s):
    return s.str.split(',').apply(lambda x: min(int(v) for v in x))

se['min_inc'] = min_per_rep(se['IJC_SAMPLE_1']).combine(min_per_rep(se['IJC_SAMPLE_2']), min)
se['min_skip'] = min_per_rep(se['SJC_SAMPLE_1']).combine(min_per_rep(se['SJC_SAMPLE_2']), min)

significant = se[
    (se['FDR'] < 0.05) &
    (se['IncLevelDifference'].abs() > 0.10) &
    ((se['min_inc'] + se['min_skip']) >= 10)
].copy()

significant['score'] = -np.log10(significant['FDR']) * significant['IncLevelDifference'].abs()
top = significant.nlargest(50, 'score')
```

## leafcutter Differential Intron Usage

**Goal:** Detect differential intron-cluster usage annotation-free, capturing novel junctions and complex multi-junction events.

**Approach:** Extract junctions with regtools, cluster introns by shared splice sites, run cluster-level Dirichlet-multinomial test.

```bash
for bam in *.bam; do
    regtools junctions extract -a 8 -m 50 -s XS "$bam" -o "${bam%.bam}.junc"
done
ls *.junc > juncfiles.txt

python leafcutter_cluster_regtools.py \
    -j juncfiles.txt \
    -o leafcutter \
    -m 50 \
    -l 500000
```

```r
library(leafcutter)

groups <- data.frame(
    sample = c('s1', 's2', 's3', 's4', 's5', 's6'),
    group = c('control', 'control', 'control', 'treatment', 'treatment', 'treatment')
)
write.table(groups, 'groups.txt', sep = '\t', quote = FALSE, row.names = FALSE, col.names = FALSE)

system('leafcutter_ds.R --num_threads 4 --exon_file gencode_exons.txt.gz \
    leafcutter_perind_numers.counts.gz groups.txt -o ds_results')

cluster_sig <- read.table('ds_results_cluster_significance.txt', header = TRUE, sep = '\t')
intron_effects <- read.table('ds_results_effect_sizes.txt', header = TRUE, sep = '\t')

sig_clusters <- subset(cluster_sig, p.adjust < 0.05)
```

**LeafCutter2** (Buen Abad Najar 2025 *bioRxiv*) extends leafcutter with NMD-aware classification of unproductive splicing — useful when AS-NMD coupling is the question.

## MAJIQ V3 Differential Analysis

**Goal:** Detect differential LSVs with full posterior distributions over ΔPSI; ideal for complex multi-junction events and heterogeneous cohorts.

**Approach:** Build splice graph -> compute coverage per group -> run deltapsi (replicate-structured) or heterogen (cohort-style).

```bash
majiq build annotation.gff3 -c settings.ini -j 8 -o build_output

majiq deltapsi \
    -grp1 build_output/ctrl1.majiq build_output/ctrl2.majiq build_output/ctrl3.majiq \
    -grp2 build_output/trt1.majiq build_output/trt2.majiq build_output/trt3.majiq \
    -n control treatment \
    -o deltapsi_output \
    --minreads 10 --minpos 3 \
    -j 8

majiq heterogen \
    -grp1 build_output/het_ctrl{1..20}.majiq \
    -grp2 build_output/het_trt{1..20}.majiq \
    -n control treatment \
    -o heterogen_output \
    -j 8

voila view -p 5000 -j 8 build_output/splicegraph.zarr deltapsi_output/control_treatment.deltapsi.voila -o voila_html
```

MAJIQ V3 (Aicher, Slaff, Jewell, Barash *bioRxiv* 2024; public release 2025) uses Zarr storage (`splicegraph.zarr`); V2's SQLite splicegraph is deprecated. MAJIQ reports posterior probability `P(|ΔPSI| > 0.2)`; thresholds are interpreted differently from FDR. Use HET for n>=10 vs n>=10 cohort designs (clinical, GTEx-style); deltapsi for tightly controlled n=3 vs n=3.

## SUPPA2 Differential Analysis

**Goal:** Quick differential splicing from existing transcript quantifications, useful as a sanity check or pilot.

**Approach:** Generate per-condition PSI files from Salmon TPM, then run `diffSplice` with empirical or classical p-values.

```bash
suppa.py generateEvents -i annotation.gtf -o events -f ioe -e SE SS MX RI

for ev in SE A5 A3 MX RI; do
    suppa.py psiPerEvent -i events_${ev}_strict.ioe -e ctrl_tpm.tsv -o ctrl_${ev}
    suppa.py psiPerEvent -i events_${ev}_strict.ioe -e trt_tpm.tsv -o trt_${ev}

    suppa.py diffSplice \
        -m empirical \
        -gc \
        -i events_${ev}_strict.ioe \
        -p ctrl_${ev}.psi trt_${ev}.psi \
        -e ctrl_tpm.tsv trt_tpm.tsv \
        -o diff_${ev}
done
```

For n<=3 designs, switch `-m classical` (Wilcoxon). Empirical null requires sufficient between-replicate observations to construct.

## Shiba for Low-Coverage / Few-Replicate Designs

**Goal:** Detect differential splicing with explicit junction-imbalance correction — addresses a known false-positive source for rMATS-style methods.

**Approach:** Shiba is a Snakemake-based pipeline configured via YAML. Install via bioconda, write a config file describing groups + BAMs, then run with snakemake.

```bash
conda install -c bioconda shiba

# Edit config.yaml with reference GTF, BAM groups, output dir, thresholds
# Then run the Snakemake workflow:
snakemake -s snakeshiba.smk \
    --configfile config.yaml \
    --cores 8 \
    --use-singularity \
    --singularity-args "--bind $HOME:$HOME"
```

Shiba (Kubota 2025 *NAR*) reportedly outperforms rMATS at n=2 vs n=2 by correcting differential mappability between inclusion and skipping junctions; community calibration still emerging. See https://sika-zheng-lab.github.io/Shiba/ for the full config.yaml schema.

## Per-Tool Failure Modes

### rMATS: Confounder-Blind LRT

**Trigger:** Sequencing batch, RIN, library prep date, or sex correlates with the comparison of interest.

**Mechanism:** rMATS' default LRT does not natively accept covariates the way DESeq2 does; the `--paired-stats` flag handles paired designs but not arbitrary covariates.

**Symptom:** Many "significant" hits driven by batch rather than biological condition; PCA on PSI matrix shows samples clustering by batch rather than group.

**Fix:** Either (a) include batch as a stratification (run rMATS within each batch), (b) regress PSI matrix against batch in R, then test residuals, or (c) switch to leafcutter which accepts a `confounders` argument in `differential_splicing`.

### leafcutter: Cluster Mis-Topology

**Trigger:** A cluster spans a complex topology (cassette + alternative donor in same cluster).

**Mechanism:** Cluster-level p-value reports "something in this cluster differs" but doesn't indicate which intron drove the change; downstream analysis needs per-intron effect sizes.

**Symptom:** Significant cluster, multiple introns with different ΔPSI directions, ambiguous biological interpretation.

**Fix:** Inspect cluster in leafviz; report per-intron effect sizes from `ds_results_effect_sizes.txt`; map cluster topology to canonical SE/A5SS/A3SS via flanking exon coordinates manually.

### MAJIQ HET: Power vs Type-1 Tradeoff

**Trigger:** HET module on n=5-10 cohorts (between regimes).

**Mechanism:** HET assumes between-sample variability dominates; for moderate-replicate designs (n=5-10), HET is conservative and deltapsi is more powerful.

**Symptom:** HET reports few hits in n=5-10 designs; deltapsi on the same data reports many.

**Fix:** Use deltapsi for n=3-5; reserve HET for n>=10 with explicit cohort heterogeneity.

### SUPPA2 Empirical: Sparse Null at Low Replicate

**Trigger:** n<=3 vs n<=3 with `--method empirical`.

**Mechanism:** Empirical null is ECDF of |ΔPSI| from between-replicate comparisons within each group, binned by transcript expression. Few replicates -> few null observations -> wide confidence on null distribution.

**Symptom:** Inflated FDR (15-30%); "significant" hits don't replicate or validate.

**Fix:** Use `-m classical` (Wilcoxon) for n<=3 vs n<=3; or switch tool entirely (leafcutter, Shiba).

## Reconciliation: When Tools Disagree

The two most common short-read tools answer slightly different questions: rMATS classifies on annotated event templates; leafcutter classifies on observed cluster usage. Disagreement is informative.

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| rMATS sig, leafcutter not sig | rMATS junction imbalance OR rMATS event hits annotation that leafcutter clustered differently | Inspect locus in IGV; check Shiba on the same locus |
| leafcutter sig, rMATS not sig | Novel junction not in rMATS annotation; rMATS `--novelSS` may have missed it | Verify `--novelSS` was on; rerun if not |
| Both sig, opposite ΔPSI direction | Event class mismatch (rMATS calls SE positive, leafcutter sees A5SS shift in same cluster) | Manually map cluster topology to event class |
| Both sig, same direction | High-confidence call | Report; cross-validate with sashimi-plot |
| All tools null but biology suggests change | Underpowered design or wrong regime | Increase replicates; check whether outlier-splicing-detection regime applies |

**Operational rule:** for high-confidence reporting, require concordant detection in two tools from different algorithmic families (event-based + cluster-based, or LSV + isoform-based). Document both calls and any explainable disagreements.

## rMATS Output Columns Reference

| Column | Meaning |
|--------|---------|
| IJC_SAMPLE_1 / SJC_SAMPLE_1 | Comma-delimited inclusion / skipping junction counts per replicate, group 1 |
| IJC_SAMPLE_2 / SJC_SAMPLE_2 | Same for group 2 |
| IncFormLen / SkipFormLen | Effective lengths normalizing PSI for differential mapping opportunity |
| upstreamES/EE, downstreamES/EE | Flanking exon coordinates (genomic order; strand-agnostic in column meaning) |
| exonStart_0base / exonEnd | Cassette exon coordinates (0-based half-open) |
| PValue | LRT p-value of \|ΔPSI\| > cutoff |
| FDR | BH-adjusted PValue within event class |
| IncLevel1, IncLevel2 | Comma-delimited per-replicate PSI values |
| IncLevelDifference | mean(IncLevel1) - mean(IncLevel2); sign matches --b1 - --b2 order |

## Replicate Count and Power

| Design | Recommended tools | Expected power for ΔPSI=0.2 |
|--------|-------------------|------------------------------|
| n=2 vs n=2 | leafcutter or Shiba; **avoid SUPPA2** | Marginal; many real effects missed |
| n=3 vs n=3 | rMATS-turbo + leafcutter | Adequate at moderate coverage; standard |
| n=5 vs n=5 | rMATS or leafcutter, MAJIQ deltapsi | Good; recommended for publication |
| n=10+ vs n=10+ heterogeneous | MAJIQ-HET | Designed for this scale |
| Single patient vs n=20+ controls | leafcutterMD or FRASER2 | Outlier regime; see outlier-splicing-detection |

For an effect-size of |ΔPSI|=0.10 (typical biological signal), power generally requires n>=4 and >=20 junction reads per replicate. Below this, expect to miss most real changes.

## Significance and Effect-Size Thresholds

| Stringency | \|ΔPSI\| | FDR | Use case |
|------------|----------|-----|----------|
| Lenient | > 0.05 | < 0.10 | Discovery, exploratory, hypothesis generation |
| Standard | > 0.10 | < 0.05 | Publication; default reporting threshold |
| Stringent | > 0.20 | < 0.01 | Validation cohort, follow-up targets |

For MAJIQ: posterior probability `P(|ΔPSI| > 0.2) >= 0.95` is roughly equivalent to standard stringency. Always document tool, threshold, and rationale.

**Biologically meaningful ΔPSI varies by context:**
- A poison exon shift of |ΔPSI|=0.10 can halve functional protein (huge biology, modest number).
- A stoichiometric isoform shift of |ΔPSI|=0.10 may be physiologically silent.
- Therapeutic ASO target: SMA nusinersen aims for ΔPSI~+0.30 in SMN2 exon 7.

## Confounder Handling

**rMATS** does not natively accept arbitrary covariates. Workarounds:
1. **Stratification**: run rMATS within each batch separately and meta-analyze.
2. **PSI residuals (logit-transformed)**: PSI is bounded [0,1]; raw linear regression near the boundaries is biased. Logit-transform first, regress on confounders, then test residuals.
3. **Switch to leafcutter** (R function accepts `confounders` matrix; CLI accepts confounders as additional columns in the groups file).

```python
import numpy as np
import statsmodels.formula.api as smf

# logit-transform PSI before residualization (PSI is bounded [0,1])
eps = 1e-3
psi['logit_psi'] = np.log((psi['psi'].clip(eps, 1 - eps)) / (1 - psi['psi'].clip(eps, 1 - eps)))
psi['psi_resid'] = smf.ols('logit_psi ~ batch + RIN', data=psi).fit().resid
# then test psi_resid by group via Wilcoxon
```

**leafcutter** accepts confounders two ways:
- **R function**: `differential_splicing(counts, x, confounders=numeric_matrix)` accepts a numeric covariate matrix
- **CLI script**: `leafcutter_ds.R` reads confounders from **additional columns in the groups file** (3rd, 4th, ... columns), NOT from a `--confounders` flag

**MAJIQ** does not accept arbitrary confounders; use stratification or switch tool.

**Always check confounding before reporting:** PCA on PSI matrix; if PC1 separates by batch rather than group, the comparison is confounded.

## Multi-Group / Multi-Factor Designs

| Design | Approach |
|--------|----------|
| 3 groups (e.g. drug A, drug B, control) | Pairwise rMATS or leafcutter; OR limma/DESeq2 on logit-PSI matrix |
| Time-course (e.g. 0h, 6h, 24h) | DEXSeq on event counts with time as factor; or limma::lmFit on PSI matrix |
| 2x2 factorial (genotype × treatment) | DEXSeq with interaction term; rMATS pairwise on interaction subsets |
| Continuous covariate (dose, age) | limma::lmFit on logit-PSI ~ covariate |

For complex designs, custom regression on the PSI matrix is more flexible than rMATS/leafcutter pairwise.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `rMATS: numpy.AxisError` | rMATS version mismatch with numpy >=2.0 | Pin numpy<2.0 or update rMATS-turbo to >=4.3 |
| `leafcutter: zero variance in cluster` | Cluster has all-zero counts in a group | Pre-filter with `--min_samples_per_intron 5 --min_samples_per_group 3` |
| `MAJIQ: out of memory` | Default settings on >50-sample cohort | Use `--mem-profile` flag; chunk samples; consider HET for large cohorts |
| `SUPPA2: no events with sufficient coverage` | Salmon/kallisto TPM filter too strict upstream | Lower upstream TPM threshold; verify event annotations |
| `voila: missing splicegraph.zarr` (V3) or `splicegraph.sql` (V2; deprecated) | Forgot to keep build output directory | Re-run `majiq build`; output must persist for VOILA |
| `regtools: too many open files` | Many BAMs in one batch | `ulimit -n 4096` or batch in groups |

## Result Prioritization

**Goal:** Rank events by combined statistical and biological significance for follow-up.

**Approach:** Composite score combining FDR and effect size, then enrich for biology (RBP binding, NMD sensitivity, conservation, disease relevance).

```python
import pandas as pd
import numpy as np

sig['score'] = -np.log10(sig['FDR']) * sig['IncLevelDifference'].abs()
sig['exon_length'] = sig['exonEnd'] - sig['exonStart_0base']
sig['nmd_likely'] = (sig['exon_length'] % 3 != 0)
top_events = sig.nlargest(50, 'score')
```

Cross-reference top hits with:
- **eCLIP/ENCODE RBP target databases** (POSTAR3, oRNAment, RBP2GO) -> candidate trans-regulators
- **Disease-specific signatures**: SF3B1 cryptic 3'ss for MDS/CLL/UM; TDP-43 cryptic exons (UNC13A, STMN2) for ALS/FTD
- **Conservation**: VastDB cross-species PSI for evolutionary support
- **Splice-site predictions**: SpliceAI scores for the involved sites (see splice-variant-prediction)

## Common Pitfalls

- **Junction read imbalance** (cassette exon flanks have unequal mapping opportunity) inflates rMATS false positives; Shiba explicitly corrects this.
- **Comparing tool outputs naively** — MAJIQ posteriors and rMATS FDR are different scales; use threshold equivalents (P>0.95 ~ FDR<0.05 in many regimes) but confirm with simulation when reporting.
- **Forgetting NMD direction** — increased PSI of a poison exon decreases protein. Always check whether the alternative form is PTC-introducing using ORF-aware annotation.
- **Cryptic splicing in TDP-43 loss / SF3B1-mutant samples** — annotation-bound tools (rMATS, SUPPA2) miss these; need leafcutter or MAJIQ with denovo mode.
- **Forgetting strand** — wrong `--libType` halves usable junctions. Confirm with RSeQC `infer_experiment.py`.
- **Reporting one tool's call as ground truth** — discordance between rMATS and leafcutter is informative, not a problem to hide.
- **Skipping confounder check** — always run PCA on PSI matrix before final reporting.
- **Using empirical SUPPA2 at n<=3** — calibration collapses; use classical mode or different tool.

## Related Skills

- splicing-quantification - PSI estimation per event; foundational
- splicing-qc - Run BEFORE differential to verify library, depth, strandedness; avoid downstream surprises
- isoform-switching - DTU framework with NMD/ORF/domain consequences; complementary to event-level
- sashimi-plots - Visualize differential events for QC and reporting
- outlier-splicing-detection - Single-sample-vs-cohort regime (FRASER2/DROP); use when not 2-group
- splice-variant-prediction - SpliceAI / Pangolin for variant-driven mechanistic explanation of differential events
- long-read-splicing - Differential analysis from full-length isoforms; use when short-read insufficient
- read-alignment/star-alignment - STAR 2-pass cohort-style required upstream

## References

- Shen et al 2014 *PNAS* - rMATS original
- Wang et al 2024 *Nat Protoc* - rMATS-turbo
- Li et al 2018 *Nat Genet* - leafcutter (Dirichlet-multinomial GLM)
- Buen Abad Najar et al 2025 *bioRxiv* - LeafCutter2 (NMD-aware unproductive splicing)
- Vaquero-Garcia et al 2016 *eLife* - MAJIQ LSV framework
- Vaquero-Garcia et al 2023 *Nat Commun* - MAJIQ-HET heterogeneity module
- Aicher, Slaff, Jewell, Barash 2024 *bioRxiv* - MAJIQ V3
- Trincado et al 2018 *Genome Biol* - SUPPA2
- Kubota et al 2025 *NAR* - Shiba (junction-imbalance correction)
- Olofsson et al 2023 *Biochem Biophys Res Commun* 653:31-37 - benchmark across tools
- Tran et al 2025 *WIREs RNA* - methodology review
- Brown et al 2022 *Nature* - UNC13A cryptic exon (TDP-43 / ALS)
- Klim et al 2019 *Nat Neurosci* - STMN2 cryptic splicing (ALS)
- Darman et al 2015 *Cell Rep* - SF3B1 cryptic 3'ss
<!-- END FILE: alternative-splicing/differential-splicing/SKILL.md -->

## 子目录：alternative-splicing/isoform-switching

<!-- BEGIN FILE: alternative-splicing/isoform-switching/SKILL.md -->
---
name: bio-isoform-switching
description: Analyzes differential transcript usage (DTU) and isoform switches with functional consequence prediction (NMD via 50nt rule, ORF disruption, protein domain loss/gain, signal peptide changes, IDR alterations, coding-potential shifts). Tools include IsoformSwitchAnalyzeR v2 (auto-selects satuRn for >5 reps else DEXSeq), the manual DRIMSeq -> DEXSeq/satuRn -> stageR DTU pipeline, and fishpond/swish for inferential-uncertainty-aware DTE. Distinguishes DTU from DGE and DTE; integrates external annotators (CPC2, Pfam, SignalP, IUPred2A or DeepTMHMM). Use when investigating how splicing differences alter protein function or trigger NMD-mediated degradation.
tool_type: r
primary_tool: IsoformSwitchAnalyzeR
---

## Version Compatibility

Reference examples tested with: IsoformSwitchAnalyzeR 2.11+, DRIMSeq 1.34+, DEXSeq 1.52+, satuRn 1.14+, stageR 1.28+, fishpond 2.14+, tximport 1.34+, tximeta 1.24+, Salmon 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Isoform Switching and Differential Transcript Usage

Identify shifts in *which* transcript a gene predominantly uses between conditions, and predict functional consequences. Statistically distinct from DGE and DTE; biologically distinct because the same gene-level expression can hide a complete isoform switch with major protein-level consequences.

## DGE vs DTE vs DTU: Which Question Is Being Asked?

| Question | Statistic | Tool | Example claim |
|----------|-----------|------|----------------|
| **DGE** Does the gene total change? | Sum of transcript counts | DESeq2, edgeR, limma-voom | "Gene X is upregulated 2-fold" |
| **DTE** Does this transcript change in absolute abundance? | Per-transcript count | swish (fishpond), DESeq2 on transcripts, sleuth | "Transcript X-201 is upregulated 2-fold" |
| **DTU** Do proportions of transcripts within the gene shift? | Vector of per-transcript proportions | DRIMSeq, DEXSeq, satuRn (+ stageR) | "Gene X switches from isoform 201 (50% -> 10%) to 202 (50% -> 90%)" |

DTU is statistically harder than DGE because:
1. The null is **compositional** (proportions sum to 1; one transcript up means another down).
2. **Multi-stage testing** is required: gene-level "any DTU" + transcript-level "which transcript" -> stageR formalizes this.
3. **Quantification uncertainty propagates** when transcripts are similar (Salmon EM ambiguity).

DTU and event-level differential splicing answer related but distinct questions: rMATS' `IncLevelDifference` is essentially a 1-D projection of a DTU shift onto a single event coordinate. The pragmatic 2026 default: run both an event-level tool (rMATS or leafcutter) and a DTU pipeline; reconcile.

## Tool Selection for DTU

| Tool | Model | When to use | Fails when |
|------|-------|-------------|------------|
| IsoformSwitchAnalyzeR v2 | Wraps DEXSeq or satuRn + functional consequence annotation | Standard interpretation workflow with NMD/domain output | Manual DTU control needed; very large cohorts (>200) |
| DRIMSeq | Dirichlet-multinomial on transcript counts; gene-level DTU | Pre-filter step before DEXSeq/satuRn | Cannot annotate functional consequences alone |
| DEXSeq | Negative-binomial GLM on exon-bin or transcript counts | Classic DTU; conservative; <=5 replicates per condition | Slow at scale; uses bins not transcripts in default mode |
| satuRn | Quasi-binomial GLM with empirical-Bayes shrinkage | DTU at scale (single-cell, large bulk cohorts) | Newer; less battle-tested than DEXSeq |
| swish (fishpond) | Non-parametric SAMseq across Salmon Gibbs samples | DTE/DGE incorporating quantification uncertainty | Requires Gibbs samples; not strictly DTU |
| stageR | Two-stage testing framework | Required for proper OFDR control on top of DRIMSeq/DEXSeq/satuRn | Standalone — wraps another tool's output |
| sleuth | Bootstrap-based DTE on kallisto | When committed to kallisto pipeline | Less active development; superseded by fishpond+swish |

The IsoformSwitchAnalyzeR v2 default rule is: **satuRn if any condition has >5 replicates; else DEXSeq.** For exactly 5 replicates per condition (boundary), explicitly choose; results may differ.

## Decision Tree by Research Question

| Question | Recommended approach |
|----------|----------------------|
| Functional consequences of switches (domains, NMD, signal peptide) | IsoformSwitchAnalyzeR v2 with full external annotator pipeline |
| Pure statistical DTU (gene-level + transcript-level OFDR) | DRIMSeq (filter) -> DEXSeq -> stageR; or -> satuRn -> stageR for n>5 |
| DTU with proper quantification uncertainty | Salmon `--numGibbsSamples 20` -> tximeta -> swish for DTE; concurrent DTU |
| Single-cell DTU | satuRn (DEXSeq doesn't scale to scRNA-seq) |
| Long-read DTU (PacBio Iso-Seq, ONT) | IsoformSwitchAnalyzeR v2 long-read input mode (no Salmon EM uncertainty) |
| Time-course DTU | DEXSeq with time as factor + interaction; or limma::lmFit on logit-prop matrix |
| Cancer / disease — switch hits -> mechanism | Standard pipeline + cross-reference with eCLIP, ClinVar, COSMIC |
| Therapeutic ASO target identification | Standard pipeline + sashimi visualization + SpliceAI design |

## IsoformSwitchAnalyzeR v2 Workflow

**Goal:** Identify isoform switches with functional consequences in one integrated workflow.

**Approach:** Import Salmon, pre-filter, run statistical test (satuRn auto-selected if any condition has >5 replicates, else DEXSeq), annotate switches with external tools (CPC2, Pfam, SignalP, IUPred2A or DeepTMHMM), then summarize consequences.

```r
library(IsoformSwitchAnalyzeR)

salmonQuant <- importIsoformExpression(
    parentDir = 'salmon_quant/',
    addIsofomIdAsColumn = TRUE
)

design <- data.frame(
    sampleID = colnames(salmonQuant$counts)[-1],
    condition = c('control', 'control', 'control', 'treatment', 'treatment', 'treatment')
)

aSwitchList <- importRdata(
    isoformCountMatrix = salmonQuant$counts,
    isoformRepExpression = salmonQuant$abundance,
    designMatrix = design,
    isoformExonAnnoation = 'annotation.gtf',
    isoformNtFasta = 'transcripts.fa',
    showProgress = TRUE
)

aSwitchList <- preFilter(
    aSwitchList,
    geneExpressionCutoff = 1,
    isoformExpressionCutoff = 0,
    IFcutoff = 0.01,
    removeSingleIsoformGenes = TRUE,
    keepIsoformInAllConditions = TRUE
)

aSwitchList <- isoformSwitchTestSatuRn(
    aSwitchList,
    reduceToSwitchingGenes = TRUE,
    alpha = 0.05,
    dIFcutoff = 0.1
)
```

`preFilter` parameters:
- `geneExpressionCutoff = 1` — minimum TPM for gene to be tested (raise for stricter)
- `isoformExpressionCutoff = 0` — minimum TPM per isoform (set to 1 for stricter)
- `IFcutoff = 0.01` — minimum isoform fraction; below = noise
- `removeSingleIsoformGenes = TRUE` — drop genes with only one detectable isoform (cannot have DTU)
- `keepIsoformInAllConditions = TRUE` — require expression across all conditions

For long-read input, use `importRdata` with long-read transcript counts directly — bypasses Salmon EM uncertainty entirely.

## Functional Consequence Annotation

**Goal:** Predict how each switch alters protein structure, function, and stability.

**Approach:** Extract sequences, run external annotators outside R, then re-import results into the switchAnalyzeRlist.

```r
aSwitchList <- extractSequence(
    aSwitchList,
    pathToOutput = 'sequences/',
    writeToFile = TRUE
)

# Run external tools on sequences/isoformSwitchAnalyzeR_isoform_*.fasta
# Then import:

# IMPORTANT: ORF analysis must run BEFORE analyzeSwitchConsequences for NMD_status,
# ORF_seq_similarity, and coding_potential consequences to be computed.
aSwitchList <- analyzeORF(aSwitchList, orfMethod = 'longest', genomeObject = NULL)

aSwitchList <- analyzeCPC2(aSwitchList, pathToCPC2resultFile = 'cpc2_results.txt', removeNoncodinORFs = TRUE)
aSwitchList <- analyzePFAM(aSwitchList, pathToPFAMresultFile = 'pfam_results.txt')
aSwitchList <- analyzeSignalP(aSwitchList, pathToSignalPresultFile = 'signalp_results.txt')
aSwitchList <- analyzeIUPred2A(aSwitchList, pathToIUPred2AresultFile = 'iupred2_results.txt')
aSwitchList <- analyzeAlternativeSplicing(aSwitchList, onlySwitchingGenes = TRUE)

aSwitchList <- analyzeSwitchConsequences(
    aSwitchList,
    consequencesToAnalyze = c(
        'intron_retention',
        'coding_potential',
        'ORF_seq_similarity',
        'NMD_status',
        'domains_identified',
        'IDR_identified',
        'IDR_type',
        'signal_peptide_identified'
    ),
    dIFcutoff = 0.1
)
```

| External tool | Purpose | Required for |
|----------------|---------|--------------|
| CPC2 (Coding Potential Calculator 2) | Coding vs non-coding classification | `coding_potential` consequence |
| Pfam (HMMER hmmscan against Pfam-A) | Protein domain identification | `domains_identified` |
| SignalP 6.0+ | Signal peptide prediction | `signal_peptide_identified` |
| IUPred2A or DeepTMHMM | Intrinsic disorder regions / TM domains | `IDR_identified`, `IDR_type` |
| NetSurfP-3 | Surface accessibility (optional) | Extended IDR analysis |

The external tools must be run *outside* R; IsoformSwitchAnalyzeR provides FASTA outputs and re-imports the parsed results. Plan for ~30-60 minutes of external compute on typical mammalian transcriptomes.

## NMD Prediction (The 50-nt Rule)

A transcript is predicted NMD-sensitive if its premature termination codon (PTC) lies **>50-55 nt upstream of the last exon-exon junction** (Maquat 2004 *Nat Rev Mol Cell Biol*; Lykke-Andersen & Jensen 2015 *Nat Rev Mol Cell Biol*).

**Mechanism:** Spliceosome deposits the Exon Junction Complex (EJC) ~20-24 nt upstream of every exon-exon junction. During the pioneer round of translation, ribosome reading through removes EJCs upstream of the stop codon. If a stop codon precedes the last EJC by >50 nt, the EJC remains, recruits UPF1 -> SMG1 phosphorylation -> SMG6/SMG7 -> mRNA decay.

**Caveats and exceptions:**
- **Last-exon PTCs escape NMD** — can be dominant-negative or gain-of-function (e.g. MYH7 truncating variants).
- **3'UTR length matters**: very long 3' UTRs (>1 kb past stop) trigger NMD via UPF1 binding even without EJCs (faux-3'UTR rule).
- **Tissue-specific NMD**: SMG6 vs SMG5/7 ratios vary; UPF1 stress conditions modulate.
- **PTC distance must be measured on the spliced transcript**, not the genomic distance.
- **~10-20% of "predicted NMD" transcripts escape NMD per orthogonal RNA-seq** (Lindeboom 2016 *Nat Genet*; ~22% of canonical PTC-bearing transcripts escape in some tissues). Treat NMD prediction as probabilistic, not certain.

IsoformSwitchAnalyzeR's `analyzeSwitchConsequences` with `'NMD_status'` evaluates this from the predicted ORF + transcript model.

## AS-NMD as a Regulatory Layer

A large class of conserved alternative splicing events is **deliberately PTC-introducing** to titrate functional protein levels:

- **All major SR proteins** (SRSF1-12) autoregulate via poison exons (Lareau 2007 *Nature*; Ni 2007 *Genes Dev*)
- **All major hnRNPs** likewise
- **Ribosomal protein genes** use AS-NMD autoregulation (e.g. rpL3, rpL12; Cuccurese 2005 *NAR*)
- **SCN1A** poison exon -> Stoke STK-001 ASO in Phase 1/2 for Dravet syndrome (Han 2020 *Sci Transl Med*)

**Functional implication:** an *increase* in PSI of a poison exon *decreases* functional protein. Sign-of-effect in DTU output is opposite from intuition for these genes. Always check whether the alternative form is PTC-bearing before interpreting direction.

**Disease examples:**
- TDP-43 cryptic exons (UNC13A, STMN2) introduce PTCs -> NMD on disease-relevant transcript (Brown 2022 *Nature*)
- Last-exon truncating variants in TTN (and MYH7): escape NMD -> stable poison/dominant-negative protein

## Manual DTU Pipeline (DRIMSeq + DEXSeq + stageR)

The canonical reference is the *F1000Research* "Swimming downstream" workflow (Love, Soneson, Patro 2018; Bioconductor `rnaseqDTU`).

```r
library(tximeta); library(DRIMSeq); library(DEXSeq); library(stageR)

se <- tximeta(coldata)
counts <- assays(se)$counts

samples <- data.frame(
    sample_id = colnames(counts),
    condition = c('control', 'control', 'control', 'treatment', 'treatment', 'treatment')
)

txdf <- data.frame(
    gene_id = rowData(se)$gene_id,
    feature_id = rowData(se)$tx_id,
    counts
)

d <- dmDSdata(counts = txdf, samples = samples)
d <- dmFilter(d, min_samps_feature_expr = 3, min_feature_expr = 10,
              min_samps_feature_prop = 3, min_feature_prop = 0.1,
              min_samps_gene_expr = 6, min_gene_expr = 10)

design_full <- model.matrix(~ condition, data = samples(d))

dxd <- DEXSeqDataSet(
    countData = round(as.matrix(counts(d)[, -c(1, 2)])),
    sampleData = samples(d),
    design = ~ sample + exon + condition:exon,
    featureID = counts(d)$feature_id,
    groupID = counts(d)$gene_id
)
dxd <- estimateSizeFactors(dxd)
dxd <- estimateDispersions(dxd, quiet = TRUE)
dxd <- testForDEU(dxd, reducedModel = ~ sample + exon)
qval <- perGeneQValue(DEXSeqResults(dxd))

dxr <- DEXSeqResults(dxd, independentFiltering = FALSE)
pConfirmation <- matrix(dxr$pvalue, ncol = 1)
rownames(pConfirmation) <- dxr$featureID
tx2gene <- as.data.frame(dxr[, c('featureID', 'groupID')])

stageRObj <- stageRTx(
    pScreen = qval,
    pConfirmation = pConfirmation,
    pScreenAdjusted = TRUE,
    tx2gene = tx2gene
)
stageRObj <- stageWiseAdjustment(stageRObj, method = 'dtu', alpha = 0.05)

results <- getAdjustedPValues(stageRObj, order = FALSE, onlySignificantGenes = FALSE)
```

**stageR semantics:**
- **Stage 1 (screening)**: gene-level p-value (`perGeneQValue` from DEXSeq, or DRIMSeq's gene-level p) is filtered at the desired Overall FDR.
- **Stage 2 (confirmation)**: only within significant genes, individual transcripts are tested at a within-gene FWER computed to maintain global OFDR.
- **Net effect**: gene-level FDR is properly controlled, AND the transcript that drove the call is known.
- Without stageR: naive transcript-level BH overcounts because the gene-level multiple-testing burden is ignored.

## fishpond/swish for Inferential-Uncertainty-Aware Testing

**Goal:** Test DTE while propagating quantification uncertainty from Salmon's Gibbs samples.

**Approach:** Run Salmon with `--numGibbsSamples 20`, import with tximeta, then use swish to average a non-parametric SAMseq-style test across inferential replicates.

```r
library(fishpond); library(tximeta)

se <- tximeta(coldata)
y <- scaleInfReps(se)
y <- labelKeep(y)
y <- y[mcols(y)$keep, ]

set.seed(1)
y <- swish(y, x = 'condition')

dte_results <- as.data.frame(mcols(y))
sig <- subset(dte_results, qvalue < 0.05)
```

**`infRV`** (inferential relative variance) is a per-feature uncertainty diagnostic; high-infRV transcripts are unreliable and can be filtered before testing. Critical for genes with many similar isoforms (TTN, MAPT, NEFM) where Salmon's EM is uncertain.

## Per-Tool Failure Modes

### DEXSeq: Slowness at Scale

**Trigger:** Bulk cohort with >50 samples or single-cell DTU.

**Mechanism:** DEXSeq fits a NB GLM per exon-bin per gene; computational cost scales linearly with samples × bins.

**Symptom:** `estimateDispersions` takes hours; `testForDEU` exhausts memory.

**Fix:** Switch to satuRn (designed for scale, including scRNA-seq); run with parallelization (`BPPARAM = MulticoreParam(8)`).

### DRIMSeq: Filtering Sensitivity

**Trigger:** Default `dmFilter` parameters too strict for low-expression cohort.

**Mechanism:** `min_samps_feature_expr = 3, min_feature_expr = 10` drops transcripts seen in <=2 samples or with <10 counts.

**Symptom:** Most candidate genes filtered out; few testable genes.

**Fix:** Tune to dataset: lower thresholds for low-coverage data, raise for high-coverage. Document choice.

### satuRn: Empirical-Bayes Shrinkage Limits

**Trigger:** Very small cohort (n=2 vs n=2) or very heterogeneous.

**Mechanism:** Empirical-Bayes shrinkage assumes shared dispersion across genes; collapses with too-few or too-heterogeneous samples.

**Symptom:** Inflated p-values; few discoveries despite real effects.

**Fix:** Aggregate replicates (pseudobulk), or switch to DEXSeq for small cohorts; use larger cohorts when possible.

### swish: Salmon Gibbs Requirements

**Trigger:** Running swish on Salmon output without Gibbs samples.

**Mechanism:** swish averages over inferential replicates from Salmon's Gibbs sampler; requires `--numGibbsSamples 20` (or bootstrap with `--numBootstraps`) at Salmon time.

**Symptom:** `scaleInfReps` errors about missing inferential replicates.

**Fix:** Re-run Salmon with `--numGibbsSamples 20`; this triples Salmon runtime but enables uncertainty-aware testing.

### IsoformSwitchAnalyzeR: External-Annotator Failure

**Trigger:** Forgetting to run all 4 external annotators (CPC2, Pfam, SignalP, IUPred2A).

**Mechanism:** `analyzeSwitchConsequences` silently drops consequence types for which annotation wasn't imported.

**Symptom:** `extractConsequenceSummary` shows fewer types than requested; specific consequence reports missing.

**Fix:** Verify all 4 result files exist before `analyzeSwitchConsequences`; check `aSwitchList$AlternativeSplicingAnalysis` slot for completeness.

## Reconciliation: When DTU and Event-Level Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Significant DTU, no rMATS hit | DTU shift across many transcripts; no single canonical event captures it | Examine isoform structure in switchPlot; report at gene level |
| rMATS sig, no significant DTU | Single event in single isoform; not a gene-level DTU | Report as event-level result; DTU not the right framing |
| Both sig, same gene, different "main" isoforms | Annotation differs (rMATS uses GENCODE basic; ISA uses comprehensive) | Standardize annotation; re-run |
| DTU shows poison-exon switch, gene-level DGE shows decrease | NMD-coupled regulation: AS-NMD reducing protein on top of transcription | Mechanism: AS-NMD; report direction carefully |

For high-confidence reporting: concordant DTU + event-level + sashimi visualization.

## Single-Cell DTU

For scRNA-seq, **satuRn** scales where DEXSeq does not. IsoformSwitchAnalyzeR v2 supports single-cell input via `importRdata` with single-cell count matrices, and the underlying satuRn test has explicit single-cell calibration (Gilis 2022 *F1000Research*).

**Strong recommendation:** pseudobulk by cell type first; per-cell DTU is rarely powered with droplet 3' chemistry. See `single-cell-splicing` for chemistry-specific limitations.

## Visualization

```r
extractTopSwitches(
    aSwitchList,
    filterForConsequences = TRUE,
    n = 25,
    sortByQvals = TRUE
)

switchPlot(
    aSwitchList,
    gene = 'TARGET_GENE',
    condition1 = 'control',
    condition2 = 'treatment',
    localTheme = theme_bw(base_size = 12)
)

extractConsequenceSummary(aSwitchList, consequencesToAnalyze = 'all', plotGenes = FALSE)
extractConsequenceEnrichment(aSwitchList, consequencesToAnalyze = 'all')
extractSplicingSummary(aSwitchList, asFractionTotal = FALSE)
```

## Significance Thresholds

| Parameter | Default | Notes |
|-----------|---------|-------|
| isoform_switch_q_value | < 0.05 | Switch significance |
| dIF (delta isoform fraction) | > 0.1 | Minimum biological effect |
| Consequence q-value | < 0.05 | Significance per consequence type |
| Gene-level OFDR (stageR) | < 0.05 | Gene-level screening FDR |
| satuRn alpha | 0.05 | Empirical-Bayes alpha |
| swish qvalue | < 0.05 | Local FDR from qvalue package |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Error in importRdata: ... transcript_ids do not match` | Salmon index built from different annotation than provided GTF | Rebuild Salmon index with matching transcripts.fa |
| `analyzeSwitchConsequences: not enough switching genes` | preFilter too strict; few candidate switches | Lower `geneExpressionCutoff`, `dIFcutoff` in test step |
| `dmFilter: empty result` | Filter parameters too strict | Reduce `min_feature_expr`, `min_samps_feature_expr` |
| `satuRn: rank-deficient design matrix` | Confounder perfectly correlated with condition | Drop the confounder or stratify analysis |
| `swish: no inferential replicates found` | Salmon run without `--numGibbsSamples` | Re-run Salmon with `--numGibbsSamples 20` |
| `analyzeIUPred2A: file not found` | External annotator output missing or wrong path | Verify CPC2/Pfam/SignalP/IUPred2A all completed and paths match |

## Common Pitfalls

- **Skipping stageR** -> inflated transcript-level FDR; gene-level multiple-testing burden ignored.
- **Forgetting NMD direction** -> sign-of-effect on protein opposite to sign-of-effect on transcript when alternative form is a PTC-bearer. Always check.
- **Treating short-read-derived isoform calls as ground truth** -> Salmon EM is uncertain; use Gibbs samples + swish if quantification uncertainty matters.
- **Comparing across annotations** -> GENCODE basic vs comprehensive, RefSeq, Ensembl all have different transcript catalogs; switches "appear" or "disappear" with annotation choice. Document version.
- **Not running long-read where possible** -> Iso-Seq / ONT removes ambiguity for genes with many similar isoforms (TTN, MAPT, NEFM, DSCAM).
- **Choosing satuRn or DEXSeq blindly at the n=5 boundary** -> IsoformSwitchAnalyzeR v2 auto-selects based on >5 vs <=5; results may differ. Document choice.
- **Reporting a "switch" without a sashimi plot** -> reviewers will demand it; do it upfront.
- **Forgetting stageR also corrects gene-level p when starting from DRIMSeq** -> DRIMSeq's `gene_p` should be passed as `pScreen`, not raw transcript p-values.

## Related Skills

- differential-splicing - Event-level (rMATS, leafcutter, MAJIQ) complementary to DTU
- splicing-quantification - PSI is a 1D projection of DTU shifts
- splicing-qc - Verify upstream library, depth, alignment before DTU
- sashimi-plots - Required visualization for switch validation and reporting
- splice-variant-prediction - Connects SpliceAI variant predictions to specific isoforms
- long-read-splicing - Full-isoform DTU bypasses transcript-quant uncertainty; preferred for many-isoform genes
- pathway-analysis/go-enrichment - Pathway enrichment of switching genes
- rna-quantification/alignment-free-quant - Salmon with `--numGibbsSamples` is upstream

## References

- Han et al 2025 *bioRxiv* 10.64898/2025.12.08.693027 - IsoformSwitchAnalyzeR v2
- Vitting-Seerup & Sandelin 2019 *Bioinformatics* 35:4469-4471 - IsoformSwitchAnalyzeR original
- Anders et al 2012 *Genome Res* - DEXSeq
- Nowicka & Robinson 2016 *F1000Research* - DRIMSeq
- Gilis et al 2022 *F1000Research* - satuRn
- Zhu et al 2019 *NAR* - swish / fishpond
- Van den Berge et al 2017 *Genome Biol* - stageR
- Love, Soneson, Patro 2018 *F1000Research* - Swimming downstream DTU workflow
- Maquat 2004 *Nat Rev Mol Cell Biol* - NMD review
- Lykke-Andersen & Jensen 2015 *Nat Rev Mol Cell Biol* - NMD update
- Lindeboom et al 2016 *Nat Genet* - NMD escape rates from RNA-seq
- Lareau et al 2007 *Nature* - SR protein AS-NMD autoregulation
- Ni et al 2007 *Genes Dev* - ultraconserved-element AS-NMD in splicing regulators
- Cuccurese et al 2005 *NAR* 33:5965-5977 - ribosomal protein AS-NMD autoregulation
- Brown et al 2022 *Nature* - UNC13A cryptic exon (TDP-43)
- Han et al 2020 *Sci Transl Med* - SCN1A poison exon ASO
<!-- END FILE: alternative-splicing/isoform-switching/SKILL.md -->

## 子目录：alternative-splicing/long-read-splicing

<!-- BEGIN FILE: alternative-splicing/long-read-splicing/SKILL.md -->
---
name: bio-long-read-splicing
description: Analyzes alternative splicing from PacBio Iso-Seq (HiFi, Kinnex/MAS-Iso-seq) and Oxford Nanopore (direct cDNA, direct RNA, R10.4.1+) long-read RNA-seq with full-isoform resolution. Tools include FLAIR (correct/collapse/quantify/diffSplice for PacBio + ONT), IsoQuant (de-novo or annotation-guided isoform discovery 2024 SOTA), Bambu (annotation-aware Bayesian discovery + quantification with Novel Discovery Rate), SQANTI3 (isoform classification: FSM/ISM/NIC/NNC + artifact flags), rMATS-long (event calling on long-read isoforms), and minimap2 (-ax splice:hq for HiFi; -ax splice -k14 for ONT cDNA; add -uf only for direct RNA or stranded cDNA preps). Solves microexon detection, recursive splicing, complex multi-exon isoforms, and DTU without transcript-quantification uncertainty. Use when short-read AS limitations (anchor length, complex isoforms, microexons, recursive splicing, transcript ambiguity) demand full-isoform resolution.
tool_type: mixed
primary_tool: FLAIR
---

## Version Compatibility

Reference examples tested with: FLAIR 2.0+, IsoQuant 3.5+, Bambu 3.4+, SQANTI3 5.4+, minimap2 2.26+, samtools 1.19+, rMATS-long 0.2+, IsoSeq3 4.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Long-Read Splicing Analysis

Full-length long-read sequencing solves problems that short-read AS cannot: anchor-length-limited microexon detection, complex multi-exon isoform deconvolution, recursive splicing in long introns, and transcript-quantification uncertainty in DTU. The 2024-2026 transition: long-read is becoming the splicing default for high-resolution analysis.

## When Long-Read Wins

| Question | Why long-read wins |
|----------|---------------------|
| Microexon detection (3-27 nt) | Reads span the microexon entirely; no aligner anchor problem |
| Long-intron recursive splicing | Can detect ratchet point usage (Sibley 2015 *Nature*) |
| Complex isoform deconvolution (TTN, MAPT, NEFM) | Single read per isoform avoids EM ambiguity |
| DTU without quantification uncertainty | Transcript identity is read-level, not inferred |
| Novel transcript discovery | No annotation dependence |
| Phasing splicing with SNVs | Allele-resolved isoforms |
| Single-cell full-length isoforms | MAS-Iso-seq + 10X 5' is the practical SOTA |
| Cryptic splicing in TDP-43 ALS | Full-length reads confirm cryptic exon inclusion in target transcripts |

## Platform Selection Matrix

| Platform | Throughput | Accuracy (modal) | Best for | Fails when |
|----------|------------|------------------|----------|------------|
| PacBio Revio HiFi (Iso-Seq) | ~25M reads / SMRT cell | Q30+ (CCS) | Bulk transcript discovery; gold standard | Cost prohibitive for very large cohorts |
| PacBio Kinnex / MAS-Iso-seq | ~16x Iso-Seq via concatemer | Q30+ | High-throughput single-cell long-read | Kinnex de-array (skera) is an extra step |
| ONT direct cDNA (R10.4.1, PCS-114) | Millions / flowcell | ~98% simplex, ~99% duplex | Cost-effective; throughput | Minor higher error than HiFi |
| ONT direct RNA (RNA004, 2024+) | ~30M reads | ~96-98% | Native modifications (m6A, pseudo-U); no RT bias | Lower throughput; higher input |
| ONT pre-R10 (R9.4.1) | Same as R10 | ~85-90% | Legacy data | Pre-R10 not recommended for splicing analysis (false novel junctions) |

**Read length:** PacBio HiFi cdna typically 1-10 kb; ONT cdna 0.5-50+ kb (long-tailed). Both span typical mammalian transcripts. Direct RNA on ONT preserves true 5'/3' termini and modifications.

## Decision Tree by Use Case

| Use case | Recommended tools |
|----------|--------------------|
| Bulk Iso-Seq transcript discovery in well-annotated organism | minimap2 -ax splice:hq -> IsoQuant or Bambu -> SQANTI3 |
| Bulk ONT cDNA in well-annotated organism | minimap2 -ax splice -uf -k14 -> IsoQuant or FLAIR -> SQANTI3 |
| End-to-end pipeline for differential analysis | FLAIR (correct -> collapse -> quantify -> diffSplice) |
| Joint discovery + quantification with calibrated novel rate | Bambu in R |
| De novo discovery for non-model organism | IsoQuant with --genedb omitted |
| Event-level differential splicing on long reads | rMATS-long |
| DTU on long-read transcript counts | DRIMSeq -> DEXSeq/satuRn -> stageR (no Salmon Gibbs needed) |
| Hybrid short+long for cohort | StringTie2 hybrid + FLAIR / IsoQuant |
| Single-cell full-length isoforms | MAS-Iso-seq + 10X 5' -> FLAMES or scNanoGPS |
| Cryptic exon validation in ALS | minimap2 -> FLAIR collapse -> manual inspection of UNC13A, STMN2 |
| ASO design with full-isoform context | minimap2 -> IsoQuant -> SQANTI3 -> ASO design (see splice-variant-prediction) |

## Splice-Aware Alignment

```bash
# PacBio HiFi (Iso-Seq) -> minimap2 splice:hq preset
minimap2 -ax splice:hq -uf --secondary=no \
    -t 16 \
    reference.fa \
    isoseq.fastq.gz | \
    samtools sort -@ 8 -o isoseq_aligned.bam
samtools index isoseq_aligned.bam

# ONT direct cDNA (PCS-114, PCB-114): unstranded by default; omit -uf
minimap2 -ax splice -k14 \
    -t 16 \
    reference.fa \
    ont_cdna.fastq.gz | \
    samtools sort -@ 8 -o ont_cdna_aligned.bam
samtools index ont_cdna_aligned.bam

# ONT direct RNA (RNA004): truly stranded (RNA molecule preserves direction); -uf is correct
minimap2 -ax splice -uf -k14 \
    -t 16 \
    reference.fa \
    ont_rna.fastq.gz | \
    samtools sort -@ 8 -o ont_rna_aligned.bam
samtools index ont_rna_aligned.bam
```

`-uf` forces all reads to the forward transcript strand — correct for direct RNA (single-stranded) and stranded cDNA library preps; **omit for unstranded cDNA** (default ONT PCS/PCB kits) or ~half the reads are lost. `--secondary=no` discards secondary alignments. For genomes with poorly-annotated splice sites, supplement with `--junc-bed gencode_junctions.bed`. uLTRA (Sahlin & Mäkinen 2021 *Bioinformatics*) and deSALT (Liu 2019 *Genome Biol*) are alternatives with higher precision on small/cryptic exons.

**Critical:** `splice:hq` is the preset for HiFi (Q30+ reads); plain `splice` is for ONT regardless of cDNA vs direct RNA. Using `splice` on HiFi data underuses the high quality; using `splice:hq` on ONT misses true junctions due to error-tolerance mismatch.

## FLAIR Workflow (correct -> collapse -> quantify -> diffSplice)

**Goal:** Identify, quantify, and test full-length isoforms from long-read RNA-seq across conditions.

**Approach:** Correct splice junctions against short-read or annotation evidence, collapse isoforms, quantify per-sample expression, run diffSplice for differential isoform usage.

```bash
flair correct \
    --query aligned.bed \
    --genome reference.fa \
    --gtf gencode.v45.annotation.gtf \
    --shortread short_read_junctions.bed \
    --output flair_corrected \
    --threads 16

flair collapse \
    --query flair_corrected_all_corrected.bed \
    --reads sample.fastq.gz \
    --genome reference.fa \
    --gtf gencode.v45.annotation.gtf \
    --output flair_collapsed \
    --threads 16

flair quantify \
    --reads_manifest reads_manifest.tsv \
    --isoforms flair_collapsed.isoforms.fa \
    --output flair_quantified \
    --threads 16

flair diffSplice \
    --isoforms flair_collapsed.isoforms.bed \
    --counts_matrix flair_quantified.counts.tsv \
    --out_dir flair_diffsplice \
    --test \
    --threads 16
```

FLAIR (Tang 2020 *Nat Commun*) handles ONT and PacBio with the same workflow. Output includes per-event PSI, FDR, and visual sashimi-like plots. The `--shortread` flag for `flair correct` is **strongly recommended** when short-read RNA-seq is available — it dramatically improves splice junction precision.

## IsoQuant for Discovery + Quantification

**Goal:** De novo or annotation-guided isoform discovery and quantification with high precision.

**Approach:** Run `isoquant.py` with reference + reads + data type; output is GTF + counts.

```bash
isoquant.py \
    --reference reference.fa \
    --genedb gencode.v45.annotation.gtf \
    --fastq sample1.fastq.gz sample2.fastq.gz \
    --data_type pacbio_ccs \
    --output isoquant_output \
    --threads 16 \
    --model_construction_strategy default_pacbio
```

`--data_type` accepts `pacbio_ccs` (HiFi), `nanopore` (ONT), or `assembly`. As of v3.0+, `--genedb` is optional for de novo discovery. IsoQuant (Prjibelski 2023 *Nat Biotech*) is current SOTA for novel transcript reconstruction; pairs well with SQANTI3 for downstream classification.

Memory requirement: >=64 GB for atlas-scale runs.

## Bambu for Annotation-Aware Discovery + Quantification

**Goal:** Joint discovery and quantification with statistical filtering of novel isoforms.

**Approach:** R Bioconductor package; takes BAM + reference annotation + genome; outputs ranged SE objects of known + novel transcripts.

```r
library(bambu)

bam_files <- c('sample1.bam', 'sample2.bam', 'sample3.bam')
genome <- 'reference.fa'
gtf <- 'gencode.v45.annotation.gtf'

bambuAnnotations <- prepareAnnotations(gtf)

se <- bambu(
    reads = bam_files,
    annotations = bambuAnnotations,
    genome = genome,
    NDR = 0.1,
    ncore = 8
)

writeBambuOutput(se, path = 'bambu_output/')

tx_counts <- as.data.frame(assays(se)$counts)
gene_counts <- transcriptToGeneExpression(se)
```

Bambu (Chen 2023 *Nat Methods* 20:1187-1195) uses **NDR** (Novel Discovery Rate) as a single, calibrated parameter replacing per-sample heuristics:

| NDR | Interpretation |
|-----|----------------|
| 0.05 | Stringent; few novel transcripts; highest precision |
| 0.1 | Balanced (default) |
| 0.2-0.3 | Permissive; more novel discoveries; recall over precision |

Excellent for combined discovery + quantification when statistical filtering matters.

## SQANTI3 Classification

**Goal:** Classify discovered isoforms relative to reference; flag artifacts (intra-priming, RT-switching).

**Approach:** Run `sqanti3_qc.py` on the isoform GTF; review classification (FSM/ISM/NIC/NNC/antisense/genic/intergenic/fusion) and quality flags.

```bash
sqanti3_qc.py \
    --isoforms isoforms.gtf \
    --refGTF gencode.v45.annotation.gtf \
    --refFasta reference.fa \
    --output sqanti3_qc \
    --aligner_choice minimap2 \
    --CAGE_peak refTSS_v3.3_human_coordinate.hg38.bed \
    --polyA_motif_list mouse_and_human.polyA_motif.txt \
    --cpus 8

sqanti3_filter.py rules \
    --sqanti_class sqanti3_qc_classification.txt \
    --filter_isoforms isoforms.fa \
    --filter_gtf isoforms.gtf \
    --output sqanti3_filtered
```

| SQANTI category | Meaning |
|-----------------|---------|
| FSM (Full Splice Match) | All junctions match reference |
| ISM (Incomplete Splice Match) | Subset of reference junctions |
| NIC (Novel In Catalog) | Novel combination of known junctions |
| NNC (Novel Not in Catalog) | Contains novel junction |
| Antisense | Overlaps gene on opposite strand |
| Genic | Within gene but no junction match |
| Intergenic | Between genes |
| Fusion | Spans multiple genes |

SQANTI3 (Pardo-Palacios 2024 *Nat Methods* 21:793-797) is the long-read isoform-curation/QC tool, with structural categories and QC tailored to ONT/PacBio error patterns. **Filter intra-priming and RT-switching** flags before reporting.

## rMATS-long for Differential Isoform Analysis on Long-Read Data

**Goal:** Apply differential isoform analysis to long-read transcript abundance with classification and visualization.

**Approach:** rMATS-long is a multi-script Python pipeline distributed via bioconda; entry point is `rmats-long` followed by the script name. It supports two modes: **abundance-based** (using ESPRESSO-style abundance estimates) and **ASM-based** (Alternative Splicing Modules — sets of isoforms sharing exon-junction structure). Run preprocessing scripts in order before `rmats_long.py`.

```bash
conda install -c conda-forge -c bioconda rmats-long

# Preprocessing pipeline (ASM mode); per-script flag names verified vs Xinglab/rmats-long
rmats-long organize_gene_info_by_chr.py --gtf annotation.gtf --out-dir gene_info_by_chr/

# simplify_alignment_info processes one BAM at a time -> one TSV
for bam in *.bam; do
    rmats-long simplify_alignment_info.py --in-file "$bam" --out-tsv "alignment_info/${bam%.bam}.tsv"
done

# organize_alignment_info_by_gene_and_chr requires a samples-tsv (sample_id<TAB>tsv_path)
rmats-long organize_alignment_info_by_gene_and_chr.py \
    --gtf-dir gene_info_by_chr/ \
    --out-dir organized/ \
    --samples-tsv samples.tsv

rmats-long detect_splicing_events.py --align-dir organized/ --gtf-dir gene_info_by_chr/ --out-dir events/
rmats-long create_gtf_from_asm_definitions.py --event-dir events/ --out-gtf asm.gtf
rmats-long count_reads_for_asms.py --align-dir organized/ --event-dir events/ --gtf-dir gene_info_by_chr/ --out-dir asm_counts/

# Main differential analysis (ASM mode)
# --group-1 / --group-2 each take the PATH to a file whose single line is a
# comma-separated list of sample IDs (matching the BAM basenames in --align-dir).
echo 'ctrl1,ctrl2,ctrl3' > group1.txt
echo 'trt1,trt2,trt3' > group2.txt
rmats-long rmats_long.py \
    --group-1 group1.txt \
    --group-2 group2.txt \
    --event-dir events/ \
    --asm-counts-dir asm_counts/ \
    --align-dir organized/ \
    --gtf-dir gene_info_by_chr/ \
    --out-dir rmats_long_output/ \
    --adj-pvalue 0.05 \
    --delta-proportion 0.05 \
    --average-reads-per-group 10

# Alternative: abundance-based mode (when you already have ESPRESSO-style estimates)
rmats-long rmats_long.py \
    --abundance abundance.esp \
    --updated-gtf updated.gtf \
    --group-1 group1.txt \
    --group-2 group2.txt \
    --out-dir rmats_long_output/ \
    --no-splice-graph-plot
```

Key flags: `--adj-pvalue` (default 0.05), `--delta-proportion` (default 0.05), `--average-reads-per-group` (default 10), `--no-splice-graph-plot` (skip expensive splice-graph rendering).

rMATS-long is a separate tool from short-read rMATS-turbo. The predecessor `lr2rmats` used long reads only to *augment* the short-read rMATS GTF. The ASM framework treats AS as a set-of-isoforms problem, more natural for long-read data than rMATS-turbo's pre-defined event categories.

## DTU on Long-Read Counts

**Goal:** Apply DRIMSeq + DEXSeq + stageR DTU pipeline to long-read transcript counts (no quantification uncertainty).

**Approach:** Use FLAIR or Bambu transcript counts as input; long-read counts are read-level identities, so no Salmon Gibbs samples needed.

```r
library(DRIMSeq); library(DEXSeq); library(stageR)

counts <- read.table('flair_quantified_counts.tsv', header=TRUE, sep='\t')

samples <- data.frame(
    sample_id = c('s1', 's2', 's3', 's4', 's5', 's6'),
    condition = c('ctrl', 'ctrl', 'ctrl', 'trt', 'trt', 'trt')
)

d <- dmDSdata(counts = counts, samples = samples)
d <- dmFilter(
    d,
    min_samps_feature_expr = 3, min_feature_expr = 5,
    min_samps_feature_prop = 3, min_feature_prop = 0.1,
    min_samps_gene_expr = 6, min_gene_expr = 10
)
```

Then proceed with the standard DEXSeq + stageR DTU pipeline (see `isoform-switching` skill). IsoformSwitchAnalyzeR v2 has explicit long-read input support.

## Single-Cell Long-Read for Splicing

**Goal:** Combine cell typing (10X 5' short read) with full-length isoform structure (Kinnex / MAS-Iso-seq).

**Approach:** Split 10X library; sequence half short-read for cell typing, half PacBio Kinnex for isoforms; recover cell barcodes from long reads via FLAMES or skera (Kinnex de-array).

```bash
# Demultiplex MAS-Iso-seq reads
skera split \
    raw_kinnex.bam \
    mas12_primers.fasta \
    demuxed.bam

# Then proceed with lima -> isoseq3 refine -> isoseq3 cluster pipeline
# For barcode rescue from FLAMES:
match_cell_barcode \
    --bam demuxed.bam \
    --barcodes 10x_barcodes.tsv \
    --output flames_demuxed.bam
```

Joglekar et al 2024 (*Nat Neurosci* 27:1051-1063) used this approach to map single-cell isoforms across developing and adult mouse and human brain. See `single-cell-splicing` for tools that work on the demultiplexed data.

## Per-Tool Failure Modes

### minimap2: Wrong Preset

**Trigger:** Using `-ax splice` for PacBio HiFi (instead of `-ax splice:hq`) or `-ax splice:hq` for ONT.

**Mechanism:** Presets configure k-mer size, error tolerance, and indel scoring; mismatched preset is sub-optimal.

**Symptom:** Lower alignment rate; missed junctions on HiFi, false novel junctions on ONT.

**Fix:** `splice:hq` for HiFi; `splice -k14` for ONT cDNA (unstranded); add `-uf` only for ONT direct RNA or stranded cDNA preps.

### IsoQuant: Memory Pressure

**Trigger:** Atlas-scale cohort or low-RAM environment.

**Mechanism:** IsoQuant builds graph structures across all reads simultaneously.

**Symptom:** OOM kill; very slow runtime.

**Fix:** Increase RAM to >=64 GB; or batch by chromosome.

### Bambu: NDR Mistuning

**Trigger:** NDR=0.5+ or NDR=0.01.

**Mechanism:** NDR controls the precision-recall tradeoff for novel transcripts.

**Symptom:** Too many spurious novel transcripts (high NDR) or missing real novel transcripts (low NDR).

**Fix:** Default NDR=0.1 is balanced; adjust based on validation expectations.

### SQANTI3: RT-Switching Flags

**Trigger:** PacBio/ONT cDNA libraries with template switching artifacts.

**Mechanism:** RT-switching produces chimeric reads spanning two unrelated transcripts; SQANTI3 flags these.

**Symptom:** Many "fusion" transcripts in non-cancer samples; biologically implausible.

**Fix:** Filter out RT-switching flags via `sqanti3_filter.py`; investigate library prep if rate >5%.

### FLAIR: Short-Read Augmentation Missing

**Trigger:** Running `flair correct` without `--shortread`.

**Mechanism:** FLAIR uses short-read junctions to correct long-read junction calls; without them, long-read errors persist as junction calls.

**Symptom:** Many false novel junctions; junction precision low.

**Fix:** Always include `--shortread short_read_junctions.bed` when short-read RNA-seq is available; generate with regtools junctions.

### rMATS-long: GTF-Only Input

**Trigger:** Trying to give rMATS-long raw long-read BAMs.

**Mechanism:** rMATS-long expects per-sample isoform GTFs (from FLAIR/IsoQuant collapse), not raw alignments.

**Symptom:** Confusing parsing errors.

**Fix:** Run FLAIR/IsoQuant per sample first; pass the resulting GTFs.

## Reconciliation: When Long-Read Tools Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| FLAIR has more isoforms than IsoQuant | FLAIR collapse less stringent; or IsoQuant filtered more aggressively | Both tools have valid pipelines; report based on use case |
| Bambu calls fewer novel than IsoQuant | Bambu NDR=0.1 is more conservative | Adjust NDR or trust Bambu's calibration |
| SQANTI3 classifies as NNC, FLAIR thinks FSM | GENCODE version mismatch | Verify both tools use same annotation |
| Long-read isoform calls don't match short-read events | Short-read EM ambiguity; or long-read coverage gap | Trust long-read for unambiguous; trust short-read for high-coverage events |

## Quality Control for Long-Read Splicing

| Metric | PacBio HiFi | ONT cDNA R10.4.1 |
|--------|-------------|-------------------|
| Read accuracy (modal) | Q30+ (>=99.9%) | ~98% simplex / ~99% duplex |
| Splice junction concordance to short-read truth | ~98% | 95-98% |
| Median read length (transcripts) | 1-4 kb | 0.5-3 kb |
| Throughput per run | ~25M HiFi reads | Tens of millions |
| Library input | 100-500 ng total RNA | 100-500 ng |
| Read direction | TSO + dT primed | TSO or random hexamer |

Pre-R10 ONT (R9.4.1) had ~85-90% junction concordance and is no longer recommended for splicing.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `minimap2: too many anchors` | Repeat-rich genome region | Use `-N 50` to limit secondary alignments |
| `IsoQuant: ssw-py not found` | Missing dependency | `pip install ssw-py` |
| `Bambu: prepareAnnotations failed` | GTF malformed | Validate GTF with `gffread -E` |
| `SQANTI3: kallisto not found` | sqanti3 expects kallisto for short-read overlap | `conda install -c bioconda kallisto` |
| `FLAIR: flair correct slow` | Genome FASTA not indexed | `samtools faidx reference.fa` |
| `skera: too many mismatches in adapter` | MAS primer mismatch | Verify primer fasta matches kit version |

## Quality Thresholds

| Metric | Recommendation | Source |
|--------|----------------|--------|
| Full-length non-chimeric (FLNC) % | >=80% (PacBio Iso-Seq) | PacBio convention |
| FSM% | >=50% in well-annotated genome (field-convention rule of thumb; not specified in the SQANTI paper) | SQANTI3 documentation; Tardaguila 2018 *Genome Res* 28:396 |
| NNC% | <=30% (>30% suggests artifacts unless biologically interesting) | SQANTI3 convention |
| Junction support | >=2 reads (or >=3 with strict filtering) | Conservative |
| Bambu NDR | 0.1 default; 0.05 stringent | Chen 2023 *Nat Methods* 20:1187 |
| SQANTI3 RT-switching flag | filter out unless validated | SQANTI3 convention |
| SQANTI3 intra-priming flag | filter out | SQANTI3 convention |
| ONT R-version | R10.4.1+ for splicing | Splice junction concordance >=95% only with R10+ |
| HiFi CCS passes | >=3 | PacBio convention for Q30+ |

## Common Pitfalls

- **Ignoring reference annotation completeness** — SQANTI3 NNC categorization differs by GENCODE version; report version with results.
- **Not running isoseq3 refine** — concatemers and polyA artifacts inflate isoform counts.
- **Confusing FLAIR's 'collapse' with 'cluster'** — collapse merges similar isoforms post-alignment; cluster (in isoseq3) merges raw reads pre-alignment.
- **Treating ONT R9.x splice calls as reliable** — pre-R10.4.1 error patterns generate false novel junctions.
- **Skipping CAGE / polyA validation in SQANTI3** — TSS / TTS hallucination is common in long-read isoforms.
- **DTU on too few replicates** — long-read is expensive; n=2 vs n=2 is common but underpowered.
- **PacBio HiFi alignment with `-ax splice` (not `splice:hq`)** — use the HQ preset for HiFi data; default `splice` is for ONT.
- **Skipping `--shortread` in FLAIR correct** — long-read junction precision is much higher with short-read augmentation.

## Related Skills

- splicing-quantification - Short-read PSI for cross-validation
- isoform-switching - DTU framework on long-read counts
- single-cell-splicing - MAS-Iso-seq + 10X integration
- long-read-sequencing/isoseq-analysis - PacBio Iso-Seq general pipeline (CCS, lima, refine, cluster)
- long-read-sequencing/long-read-alignment - minimap2 splice:hq details
- long-read-sequencing/long-read-qc - QC for long-read data
- splice-variant-prediction - Cross-reference variant predictions with full isoforms

## References

- Tang et al 2020 *Nat Commun* - FLAIR
- Prjibelski et al 2023 *Nat Biotech* - IsoQuant
- Chen et al 2023 *Nat Methods* 20:1187-1195 - Bambu
- Tardaguila et al 2018 *Genome Res* - SQANTI (original)
- Pardo-Palacios et al 2024 *Nat Methods* 21:793-797 - SQANTI3
- Pardo-Palacios et al 2024 *Nat Methods* 21:1349-1363 - LRGASP benchmark
- Wyman et al 2020 *bioRxiv* - TALON (note: not formally peer-reviewed)
- Li 2018 / 2021 *Bioinformatics* - minimap2
- Sahlin & Makinen 2021 *Bioinformatics* - uLTRA
- Sibley et al 2015 *Nature* - recursive splicing
- Al'Khafaji et al 2024 *Nat Biotech* - MAS-Iso-seq / Kinnex
- Joglekar et al 2024 *Nat Neurosci* 27:1051-1063 - scISOr-Seq2 single-cell brain isoform mapping
- Tian et al 2021 *Genome Biology* 22:310 - FLAMES
- Brown et al 2022 *Nature* - UNC13A cryptic exon (TDP-43)
- Klim et al 2019 *Nat Neurosci* - STMN2 cryptic splicing
<!-- END FILE: alternative-splicing/long-read-splicing/SKILL.md -->

## 子目录：alternative-splicing/outlier-splicing-detection

<!-- BEGIN FILE: alternative-splicing/outlier-splicing-detection/SKILL.md -->
---
name: bio-outlier-splicing-detection
description: Detects aberrant splicing in single rare-disease patients vs a control panel using FRASER 2.0 (Bioconductor; Beta-binomial autoencoder on Intron Jaccard Index, default delta cutoff 0.1, q hyperparameter), OUTRIDER (gene-level outlier expression via autoencoder denoising), LeafcutterMD (Dirichlet-multinomial outlier mode of LeafCutter for annotation-free junctions), and DROP (Snakemake pipeline integrating FRASER2 + OUTRIDER + monoallelic expression for clinical diagnostics). The statistical model is fundamentally different from differential splicing — single-sample-vs-cohort outlier detection rather than two-group comparison. Standard tool in EU rare-disease (Solve-RD) and NIH UDN programs. Use when applying RNA-seq to undiagnosed Mendelian disease, validating predicted splice variants in clinical samples, or detecting cryptic splicing in disease tissue.
tool_type: r
primary_tool: FRASER
---

## Version Compatibility

Reference examples tested with: FRASER 2.0 (>=1.99.0), OUTRIDER 1.20+, LeafcutterMD via leafcutter 0.2.9+, DROP 1.4+, R 4.4+, BiocManager 1.30+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Outlier Splicing Detection

For clinical RNA-seq diagnostics in rare disease, the question is not "what differs between groups?" but "what is aberrant in this single patient relative to a panel of unaffected samples?". The statistical framework is **single-sample-vs-cohort outlier detection**, fundamentally different from two-group differential splicing. Tools in this space are designed for clinical Mendelian diagnostic settings.

## Tool Taxonomy

| Tool | Statistic | Test target | Fails when |
|------|-----------|-------------|------------|
| FRASER 2.0 | Beta-binomial autoencoder on Intron Jaccard Index | Splicing outliers (per-sample, per-junction) | Cohort <20 samples; tissue mismatch |
| OUTRIDER | Autoencoder-denoised expression Z-score | Gene-level expression outliers (LoF, monoallelic) | Cohort <20 samples |
| LeafcutterMD | Dirichlet-multinomial outlier mode | Annotation-free intron usage | Beta-binomial fits poorly OR few controls |
| DROP | Snakemake pipeline | All of above + monoallelic expression | Pipeline complexity for small projects |

Core reference: **FRASER 2.0** for splicing outliers, **OUTRIDER** for expression outliers, **DROP** to combine. Standard tool in EU rare-disease programs (Solve-RD) and NIH UDN.

## Decision Tree by Diagnostic Scenario

| Scenario | Recommended approach |
|----------|----------------------|
| Single rare-disease patient + panel of n>=50 controls | FRASER 2.0 (Intron Jaccard Index) |
| Single patient + small panel (n=20-50) | FRASER 2.0 with auxiliary GTEx controls; tune q carefully |
| Patient + cohort <20 | Insufficient for outlier detection; consider differential or recruit more samples |
| Outlier expression suspected (loss of function, monoallelic) | OUTRIDER on same cohort |
| Annotation-free outlier (cryptic exon, novel junction) | LeafcutterMD |
| Integrated diagnostic pipeline (splicing + expression + MAE) | DROP |
| TDP-43 ALS post-mortem brain (cryptic exons) | FRASER 2.0; expect UNC13A, STMN2, ATG4B |
| SF3B1-mutant cancer sample | FRASER 2.0 with cohort-matched RNA-seq; expect cryptic 3'ss |
| Familial dysautonomia (ELP1) | FRASER 2.0 in fibroblast/iPSC; CNS tissue gives strongest signal |
| Stargardt deep-intronic ABCA4 | FRASER 2.0 in retina-relevant tissue |
| Solid tumor splicing biomarker | Differential splicing (n>=10 vs cohort) — see differential-splicing skill |
| RNA validation of SpliceAI hit | FRASER 2.0 + cross-reference with predicted variant location |

## When to Use Outlier vs Differential

**Outlier regime** (this skill):
- Single patient or small case series vs control panel
- Question: "What is aberrant in this patient?"
- Statistical model: single-sample p-value vs cohort distribution

**Differential regime** (differential-splicing skill):
- Two well-defined groups, n>=3 each
- Question: "What differs between groups?"
- Statistical model: two-group LRT or related

If n>=10 patients with a shared phenotype are available, prefer **differential** (more power); if single patient or heterogeneous case series, use **outlier**.

## FRASER 2.0 Workflow

**Goal:** Detect aberrant splicing in patient samples vs cohort using the Intron Jaccard Index.

**Approach:** Count split reads per junction, compute Intron Jaccard Index per intron, fit a Beta-binomial autoencoder to estimate expected values, then flag outliers by p-value and delta.

```r
library(FRASER); library(BiocParallel)

bam_files <- list.files('bams/', pattern='.bam$', full.names=TRUE)
sample_table <- data.frame(
    sampleID = gsub('.bam', '', basename(bam_files)),
    bamFile = bam_files,
    pairedEnd = TRUE
)

settings <- FraserDataSet(
    colData = sample_table,
    workingDir = 'fraser_workdir',
    name = 'rare_disease_cohort'
)

settings <- countRNAData(settings, BPPARAM = MulticoreParam(8))
fds <- calculatePSIValues(settings)

fds <- filterExpressionAndVariability(
    fds,
    minDeltaPsi = 0.0,
    minExpressionInOneSample = 20,
    quantile = 0.05,
    quantileMinExpression = 1
)

fitMetrics(fds) <- 'jaccard'
currentType(fds) <- 'jaccard'  # canonical setter for active metric in FRASER 2.0
fds <- FRASER(
    fds,
    q = c(jaccard = 10),
    BPPARAM = MulticoreParam(8)
)

results <- results(
    fds,
    psiType = 'jaccard',
    padjCutoff = 0.05,
    deltaPsiCutoff = 0.1
)

patient_results <- results[results$sampleID == 'PATIENT_001', ]
patient_results <- patient_results[order(patient_results$padjust), ]
```

**FRASER 2.0 changes vs FRASER 1.x:**
- Default `psiType` changed from three metrics (psi5, psi3, theta) to single **Intron Jaccard Index**
- Default `deltaPsiCutoff` dropped from 0.3 to **0.1**
- Pseudocount and filtering parameter optimization
- Bioconductor package version >=1.99.0 == FRASER 2.0

`q = 10` is the autoencoder dimension hyperparameter. **Tune via `estimateBestQ(fds, type='jaccard')` for cohort-specific optimum** — too low: confounders not removed; too high: real signal absorbed.

## OUTRIDER for Gene-Level Outlier Expression

**Goal:** Detect genes with aberrantly high or low expression in patient samples.

**Approach:** Autoencoder denoising of expression matrix; outliers identified by Z-score and adjusted p-value.

```r
library(OUTRIDER); library(BiocParallel)

countTable <- read.table('counts.tsv', header=TRUE, row.names=1)
ods <- OutriderDataSet(countData = countTable)

ods <- filterExpression(ods, minCounts=TRUE, filterGenes=TRUE)
# OUTRIDER's estimateBestQ returns a scalar q (unlike FRASER's, which returns the object)
q_best <- estimateBestQ(ods)
ods <- OUTRIDER(ods, q = q_best, BPPARAM = MulticoreParam(8))

res <- results(ods, padjCutoff = 0.05, zScoreCutoff = 0)
patient_outliers <- res[res$sampleID == 'PATIENT_001', ]
```

OUTRIDER (Brechtmann 2018 *Am J Hum Genet*) catches loss-of-function alleles producing transcript collapse, monoallelic effects, and tissue-inappropriate expression — complements splice outlier detection.

## LeafcutterMD for Annotation-Free Outlier Intron Usage

**Goal:** Detect outlier intron usage relative to a control panel without annotation dependence.

**Approach:** Run LeafcutterMD (LeafCutter's Dirichlet-multinomial outlier mode for Mendelian disease) against the control panel.

```bash
for bam in *.bam; do
    regtools junctions extract -a 8 -m 50 -s XS "$bam" -o "${bam%.bam}.junc"
done

ls *.junc > juncfiles.txt
python leafcutter_cluster_regtools.py -j juncfiles.txt -o leafcutter -m 50 -l 500000

leafcutterMD.R \
    --num_threads 4 \
    --output_prefix patient_outlier \
    leafcutter_perind_numers.counts.gz
```

LeafcutterMD (Jenkinson 2020 *Bioinformatics*) reports per-sample p-values per intron-cluster; useful when FRASER's Beta-binomial model fits poorly or when novel-junction sensitivity matters.

## DROP Pipeline (Integrated Workflow)

**Goal:** Run FRASER2 + OUTRIDER + monoallelic expression in a unified Snakemake pipeline for clinical diagnostics.

**Approach:** DROP is distributed via **bioconda** (not PyPI). Install in a dedicated environment, then configure with patient + control sample sheets; pipeline handles QC, alignment, counting, autoencoding, and reporting.

```bash
# Install via bioconda (DROP is not on PyPI)
mamba create -n drop_env -c conda-forge -c bioconda drop --override-channels
conda activate drop_env

drop init my_diagnostic_run
cd my_diagnostic_run

# Edit config.yaml:
#  - sample_table: samples.tsv (patient + controls)
#  - aberrantSplicing: enabled
#  - aberrantExpression: enabled
#  - mae: enabled (monoallelic expression)

snakemake --cores 16 --use-conda
```

DROP (Yepez 2021 *Nat Protocols*) is the standard tool in EU rare-disease genome+RNA-seq programs (Solve-RD) and the NIH UDN. v1.4+ uses FRASER 2.0. The **MAE module** uses a custom z-score test on heterozygous SNPs from RNA-seq (allele-specific expression) — useful for catching dominant-negative or monoallelic LoF that splicing/expression outliers miss. Cohort >=30 samples recommended for confident outlier detection.

## Variant + Outlier Integration

**Goal:** Connect a candidate splice-altering DNA variant to RNA-level confirmation.

**Approach:** Cross-reference SpliceAI hits with FRASER2 outliers in the same sample.

```r
library(dplyr)

variants <- read.table('spliceai_hits.tsv', header=TRUE, sep='\t')
fraser_hits <- read.table('fraser_results.tsv', header=TRUE, sep='\t')

confirmed <- variants %>%
    filter(delta_max >= 0.2) %>%
    inner_join(
        fraser_hits %>% filter(sampleID == 'PATIENT_001', padjust < 0.05),
        by = c('chrom' = 'seqnames'),
        relationship = 'many-to-many'
    ) %>%
    filter(abs(pos - start) < 1000 | abs(pos - end) < 1000)
```

A SpliceAI hit + concordant FRASER2 outlier in the patient = strong PS3 functional evidence in the ACMG framework. This integration is the highest-value clinical pipeline step — converts a computational PP3 to functional PS3.

## Cohort Size and Power

| Cohort size | Power | Comment |
|-------------|-------|---------|
| n < 20 | Marginal | High FDR; consider GTEx tissue-matched controls as auxiliary |
| n = 20-50 | Acceptable | FRASER autoencoder can fit; tune q carefully |
| n >= 50 | Recommended | Standard clinical diagnostic cohort size |
| n >= 100 | Optimal | Tissue-matched and batch-matched gives best calibration |

GTEx-derived tissue-matched controls can supplement small in-house cohorts but introduce batch effects; use only when in-house n < 30 and document the pooling strategy.

## Tissue Choice for Mendelian RNA-seq

| Tissue | Pros | Cons | Genes captured |
|--------|------|------|----------------|
| Whole blood (PAXgene) | Easy, standard | Globin contamination; many disease genes silent | ~70-80% of clinical genes |
| Fibroblast (skin biopsy) | Reasonable expression | Requires culture; senescence variability | ~75-85% |
| Muscle biopsy | Best for muscular dystrophy | Invasive | ~85-90% for muscle disorders |
| iPSC-derived neuron / cardiomyocyte | Disease-relevant tissue | Cost, variability | ~95% if differentiation works |
| Urine sediment | Non-invasive | Low yield | ~50-60% |

For UDN-style cases: blood first, then fibroblast if blood lacks expression of candidate gene. Critical: **a negative blood RNA-seq doesn't rule out a candidate gene that's silent in blood** — verify gene expression with GTEx tissue panel before committing to the tissue.

## Hyperparameter Tuning

```r
# useOHT=FALSE runs the injection-based q grid so plotEncDimSearch has a curve to show;
# useOHT=TRUE (default) is the fast deterministic OHT estimate but produces no search table to plot.
fds <- estimateBestQ(fds, type='jaccard', useOHT=FALSE, q_param=c(2, 5, 10, 15, 20))
plotEncDimSearch(fds, type='jaccard')
```

The encoding dimension `q` should be where the loss curve plateaus. Too low: confounders not removed; too high: real signal absorbed.

For typical 50-100 sample cohorts, q=8-15 is the usual operating range (DROP / FRASER workflow convention; no single primary citation — verify with `plotEncDimSearch` on the actual cohort). For very small cohorts (n=20-30), q=5-8 is typical.

## Per-Tool Failure Modes

### FRASER 2.0: Q Hyperparameter Mistuning

**Trigger:** Default q=10 used without tuning; or wrong q for cohort size.

**Mechanism:** Q is the autoencoder bottleneck dimension; too small -> confounders leak into outlier signal; too large -> real biological signal absorbed by autoencoder.

**Symptom:** Either no significant outliers (q too high) or many spurious calls clustering by batch (q too low).

**Fix:** Run `estimateBestQ(fds, type='jaccard', useOHT=TRUE)` (Optimal Hard Thresholding default; very fast); use the returned `bestQ(fds)` value. For exhaustive search, pass `useOHT=FALSE, q_param=c(2, 5, 10, 15)` and inspect `plotEncDimSearch` for the plateau.

### FRASER 2.0: Tissue Mismatch

**Trigger:** Patient sample from different tissue than majority of controls.

**Mechanism:** FRASER autoencoder learns tissue-specific expression patterns; tissue-mismatched patient appears as global outlier.

**Symptom:** Hundreds of "significant" outliers in patient; not biologically interpretable.

**Fix:** Strict tissue matching; if controls are mixed-tissue, use only controls from patient's tissue.

### OUTRIDER: Few Controls

**Trigger:** Cohort <20 samples.

**Mechanism:** Autoencoder needs sufficient samples to learn expression covariance; fails to fit at very small cohort sizes.

**Symptom:** Convergence warnings; uncalibrated p-values.

**Fix:** Pool with GTEx auxiliary controls; or use simpler outlier methods (z-score on log-CPM).

### LeafcutterMD: Cluster Count Limits

**Trigger:** Very few clusters in patient sample (low coverage or filtered out).

**Mechanism:** LeafcutterMD fits a Dirichlet-multinomial (Beta-binomial per-intron) model over cluster counts; few observations -> unstable fit -> unreliable p-values.

**Symptom:** Inflated or deflated p-values; few significant calls.

**Fix:** Increase coverage; relax filtering (`-m 10` instead of 50); or switch to FRASER2.

### DROP: Snakemake Pipeline Failures

**Trigger:** Missing dependencies or incompatible R/Bioconductor versions.

**Mechanism:** DROP orchestrates many tools; version mismatches cascade through pipeline.

**Symptom:** Snakemake step fails partway through; cryptic R errors.

**Fix:** Use `--use-conda` flag for environment isolation; pin versions in environment yamls.

## Reconciliation: When Outlier Tools Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| FRASER2 sig, OUTRIDER not | Splicing change without expression collapse | Standard splicing outlier; report |
| OUTRIDER sig, FRASER2 not | Expression LoF without splicing change | Likely promoter / regulatory; not splicing |
| Both sig at same gene | LoF allele triggering NMD on splicing-disrupted transcript | Strong combined evidence; expect downstream |
| LeafcutterMD sig, FRASER2 not | Novel cryptic event not in annotation | High-priority novel finding; investigate |
| All tools null but biology suggests change | Underpowered cohort or wrong tissue | Verify gene expression in tissue; recruit larger cohort |

## Disease-Specific Expectations

| Condition | Expected outlier signature | Tissue |
|-----------|----------------------------|--------|
| ALS / FTD (TDP-43 loss) | Cryptic exons in UNC13A, STMN2, ATG4B | Post-mortem brain ONLY |
| SF3B1-mutant MDS / CLL / uveal melanoma | Aberrant 3'ss ~10-30nt upstream of canonical | Bone marrow / tumor tissue |
| Spinal muscular atrophy (untreated SMN2) | SMN exon 7 skipping | Fibroblast / iPSC-MN |
| Familial dysautonomia (ELP1 c.2204+6T>C) | ELP1 exon 20 skipping (>=99% in CNS, partial elsewhere) | iPSC-neuron > fibroblast > blood |
| Deep-intronic CFTR / USH2A / CEP290 | Pseudoexon inclusion | Cognate disease tissue (lung / retina) |
| Duchenne muscular dystrophy (DMD) | Out-of-frame exon skipping pattern | Muscle biopsy |
| Stargardt (ABCA4) deep-intronic | Pseudoexon in retina | Retinal organoid / iPSC-RPE |

For each, the gene must be expressed in the queried tissue. Verify with GTEx before assuming negative result rules out the gene.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `FRASER: cohort too small` | n<10 | Pool with auxiliary controls; or recruit more patients |
| `FRASER: countRNAData failed on chromosome X` | BAM index missing or corrupted | Re-index BAMs; check `samtools idxstats` |
| `estimateBestQ: convergence not reached` | Default q range insufficient | Expand `q_param=c(2,5,10,15,20)`; or use `useOHT=TRUE` for the fast deterministic alternative |
| `OUTRIDER: encoding-dim search slow` | `findEncodingDim` grids many q values | Use `estimateBestQ(ods)` for a fast single-q estimate |
| `DROP: snakemake job failed at FRASER` | DROP-FRASER version mismatch | Update DROP to latest; verify FRASER 2.0 compatibility |
| `LeafcutterMD: insufficient clusters` | Cluster filter too strict | Lower `-m` minimum cluster reads |
| `Variant integration: chrom format mismatch` | VCF uses 1, FRASER uses chr1 (or vice versa) | Standardize with `bcftools annotate --rename-chrs` |

## Common Pitfalls

- **Using bulk differential-splicing tools for n=1 vs cohort** — rMATS, leafcutter (regular), SUPPA2 are not designed for this. Use FRASER2 / LeafcutterMD.
- **Ignoring tissue choice** — clinical gene expression varies dramatically across blood / fibroblast / muscle. A negative blood RNA-seq doesn't rule out a candidate gene that's silent in blood.
- **Forgetting batch effects** — combining in-house and external (GTEx) controls introduces sequencing batch confounding; use ComBat or include batch as covariate.
- **Skipping the variant + outlier integration** — RNA-only outlier without DNA variant suggests cellular state or technical artifact; DNA-only prediction without RNA confirmation is supporting only (PP3, not PS3).
- **Treating all FRASER2 outliers as pathogenic** — many are benign tissue-specific variation. Filter against gnomAD splice constraint and disease gene panels.
- **Q hyperparameter not tuned** — default `q=10` works for ~50-100 sample cohorts; tune for outliers.
- **Wrong default delta cutoff for FRASER 1.x vs 2.0** — 1.x default 0.3, 2.0 default 0.1; document which version.

## Quality Thresholds

| Metric | Recommendation | Source |
|--------|----------------|--------|
| Cohort size | n>=50 (ideal); n>=20 (minimum) | Solve-RD / UDN convention |
| FRASER 2.0 padj | < 0.05 | Standard |
| FRASER 2.0 delta Jaccard | >= 0.1 (default in v2.0) | Scheller 2023 *AJHG* |
| OUTRIDER padj | < 0.05 | Brechtmann 2018 *AJHG* |
| OUTRIDER zScore | abs >= 2 | Conservative |
| Sequencing depth | >=50M PE reads/sample | Standard for AS analysis |
| Tissue match between patient and controls | Required | Critical for FRASER2 calibration |
| Batch match | Strongly recommended | Reduces autoencoder confounding |

## Related Skills

- splice-variant-prediction - SpliceAI / Pangolin for in-silico prediction; integration target
- differential-splicing - When testing multiple patients vs controls (>=10 vs cohort)
- splicing-qc - Library / depth / tissue prerequisites
- variant-calling/clinical-interpretation - ACMG/AMP framework integration
- workflows/clinical-trial-pipeline - Trial-grade RNA-seq diagnostics

## References

- Mertes et al 2021 *Nat Commun* - FRASER 1.x
- Scheller et al 2023 *Am J Hum Genet* - FRASER 2.0 (Intron Jaccard Index)
- Brechtmann et al 2018 *Am J Hum Genet* - OUTRIDER
- Jenkinson et al 2020 *Bioinformatics* - LeafcutterMD
- Yepez et al 2021 *Nat Protocols* - DROP pipeline
- Cummings et al 2017 *Sci Transl Med* - RNA-seq for muscular dystrophy diagnostics
- Kremer et al 2017 *Nat Commun* - RNA-seq for mitochondrial disease
- Brown et al 2022 *Nature* - UNC13A cryptic exon (TDP-43 / ALS)
- Klim et al 2019 *Nat Neurosci* - STMN2 cryptic splicing (ALS)
- Darman et al 2015 *Cell Rep* - SF3B1 cryptic 3'ss
- Walker et al 2023 *Am J Hum Genet* - ClinGen SVI splicing recommendations
<!-- END FILE: alternative-splicing/outlier-splicing-detection/SKILL.md -->

## 子目录：alternative-splicing/sashimi-plots

<!-- BEGIN FILE: alternative-splicing/sashimi-plots/SKILL.md -->
---
name: bio-sashimi-plots
description: Creates sashimi-style plots showing RNA-seq read coverage and splice junction counts using ggsashimi (general-purpose, condition-grouped overlays), rmats2sashimiplot (rMATS-output-aware), MAJIQ-VOILA (LSV posteriors interactive HTML), leafviz (leafcutter clusters Shiny), Jutils (tool-agnostic heatmaps and sashimi for rMATS/leafcutter/MntJULiP/MAJIQ output), or pyGenomeTracks (multi-track publication figures). Tool choice depends on the upstream differential-splicing tool's output format and the publication vs interactive use case. Use when visualizing specific splicing events, validating differential splicing calls, or producing publication-quality figures.
tool_type: python
primary_tool: ggsashimi
---

## Version Compatibility

Reference examples tested with: ggsashimi 1.1+, rmats2sashimiplot 3.0+, MAJIQ 3.0+, leafcutter 0.2.9+, pyGenomeTracks 3.8+, ggplot2 3.5+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Sashimi Plot Visualization

Visualize RNA-seq coverage tracks with splice junction arcs labeled by read count. Sashimi plots originated with MISO (Katz 2010 *Nat Methods*); modern tools differ in input handling, group aggregation logic, and customization. Tool choice is not interchangeable — some tools work only with specific upstream output formats.

## Tool Selection Matrix

| Tool | Best for | Input | Strengths | Fails when |
|------|----------|-------|-----------|------------|
| ggsashimi | Publication-quality grouped overlays from any BAM | BAMs + region | `--overlay` aggregates samples within a group; clean PDFs | No native rMATS/MAJIQ integration; need to extract coords manually |
| rmats2sashimiplot | One-line plot from rMATS output | rMATS event file + BAMs | No manual coord extraction | rMATS-specific; doesn't handle leafcutter or MAJIQ |
| MAJIQ-VOILA | Interactive LSV browsing with posterior PSI distributions | MAJIQ build + psi/deltapsi | Splice-graph topology; LSV-aware; posterior violins | Static figures; non-academic license |
| leafviz | Cluster-level interactive browsing with NMD annotation | leafcutter differential output | Filter table + sashimi-like plots; NMD-aware | leafcutter-specific |
| Jutils | Unified output across rMATS, leafcutter, MntJULiP, MAJIQ | Tool-specific differential output | Heatmaps, Venn, sashimi tool-agnostically | Output less polished than ggsashimi |
| pyGenomeTracks | Multi-track publication figures (RNA-seq + ChIP/ATAC) | BigWig + BED + GTF | Combine RNA with chromatin tracks | Not splicing-specific; configure tracks manually |
| IGV (interactive) | Quick ad-hoc inspection | BAM + region | Scrollable, instant | Not for publication figures |
| MISO sashimi | Historical | MISO output | Original sashimi format | MISO unmaintained; no longer recommended |

## Decision Tree by Goal

| Goal | Recommended tool |
|------|-------------------|
| Validate a specific rMATS hit | rmats2sashimiplot (one-line) or ggsashimi (custom) |
| Validate a leafcutter cluster | leafviz (interactive) or ggsashimi with cluster coordinates |
| Validate a MAJIQ LSV (complex topology) | MAJIQ-VOILA (only tool that shows full LSV graph) |
| Publication-quality two-condition comparison | ggsashimi `-O 3 -A mean_j` for grouped overlay |
| Multi-track figure (RNA-seq + H3K4me3 + ATAC) | pyGenomeTracks |
| Quick ad-hoc browsing during development | IGV sashimi |
| Tool-agnostic batch heatmap of significant events | Jutils |
| Interactive cohort-level filtering of leafcutter results | leafviz Shiny |

## ggsashimi for Publication Overlays

**Goal:** Generate publication-quality sashimi plot for a region with samples grouped by condition and per-sample tracks aggregated.

**Approach:** Define samples + groups + colors in a TSV (no header), then call ggsashimi with coordinates, GTF, and visual flags.

```python
import subprocess
import pandas as pd

# ggsashimi input: col1 = sample id, col2 = BAM path, col3 = group (for -O/-C overlay/color)
groups = pd.DataFrame({
    'sample_id': ['ctrl1', 'ctrl2', 'ctrl3', 'trt1', 'trt2', 'trt3'],
    'bam': ['ctrl1.bam', 'ctrl2.bam', 'ctrl3.bam', 'trt1.bam', 'trt2.bam', 'trt3.bam'],
    'group': ['Control', 'Control', 'Control', 'Treatment', 'Treatment', 'Treatment']
})
groups.to_csv('sashimi_groups.tsv', sep='\t', index=False, header=False)

subprocess.run([
    'ggsashimi.py',
    '-b', 'sashimi_groups.tsv',
    '-c', 'chr17:43094000-43125000',
    '-o', 'BRCA1_sashimi',
    '-M', '10',
    '--alpha', '0.25',
    '--height', '3',
    '--width', '10',
    '--shrink',
    '--fix-y-scale',
    '--ann-height', '4',
    '-g', 'gencode_v45.gtf',
    '--base-size', '14',
    '-O', '3',
    '-A', 'mean_j',
    '-F', 'pdf'
], check=True)
```

Key ggsashimi flags (Garrido-Martin 2018 *PLoS Comput Biol*):
- `--overlay 3` (or `-O 3`): aggregate multiple samples within a group into a single overlay track with summary statistics — its signature feature
- `-A mean_j`: junction aggregation method (`mean`, `median`, `mean_j` accounts for sample-wise normalization); use `mean_j` for biological replicates
- `--shrink`: rescale long introns (>2x flanking exons) for compact display
- `--fix-y-scale`: identical y-axis across groups (essential for visual comparison)
- `--alpha 0.25`: transparency for per-sample coverage in overlay mode
- `-M 10`: minimum junction reads to display (lower = noisier; 5-10 typical; raise to 20+ for crowded plots)
- `--ann-height`: gene annotation track height
- `-F pdf`: output format (pdf, png, svg, eps)

## Batch Plotting from rMATS Hits

**Goal:** Auto-generate sashimi plots for all significant rMATS differential events.

**Approach:** Parse SE.MATS.JC.txt, expand coordinates to flanking exons + 500nt context, iterate ggsashimi.

```python
import subprocess
import pandas as pd
from pathlib import Path

diff = pd.read_csv('rmats_output/SE.MATS.JC.txt', sep='\t')
sig = diff[(diff['FDR'] < 0.05) & (diff['IncLevelDifference'].abs() > 0.10)]

Path('sashimi_plots').mkdir(exist_ok=True)
for idx, ev in sig.head(25).iterrows():
    region = f'{ev["chr"]}:{ev["upstreamES"] - 500}-{ev["downstreamEE"] + 500}'
    safe_name = f'{ev["geneSymbol"]}_{ev["chr"]}_{ev["upstreamES"]}'
    subprocess.run([
        'ggsashimi.py',
        '-b', 'sashimi_groups.tsv',
        '-c', region,
        '-o', f'sashimi_plots/{safe_name}',
        '-M', '5',
        '--shrink',
        '--fix-y-scale',
        '-O', '3',
        '-A', 'mean_j',
        '-g', 'annotation.gtf',
        '-F', 'pdf'
    ], check=True)
```

For MXE events, plot from upstreamES of exon 1 to downstreamEE of exon 2 to show both alternative exons in the same figure.

## rmats2sashimiplot

**Goal:** Plot directly from rMATS event coordinates without manual region calculation.

**Approach:** Pass rMATS event file + BAM lists + event type; rmats2sashimiplot extracts coordinates and produces per-event PDFs.

```bash
rmats2sashimiplot \
    --b1 ctrl1.bam,ctrl2.bam,ctrl3.bam \
    --b2 trt1.bam,trt2.bam,trt3.bam \
    -t SE \
    -e rmats_output/SE.MATS.JC.txt \
    --l1 Control \
    --l2 Treatment \
    -o sashimi_rmats \
    --exon_s 1 \
    --intron_s 5 \
    --color '#1f77b4,#ff7f0e' \
    --group-info group_def.txt
```

`--exon_s 1 --intron_s 5` shrinks intron-to-exon visual ratio 5:1 (introns drawn 1/5 their actual length). The `--group-info` flag (newer versions) allows custom replicate groupings.

## MAJIQ-VOILA Interactive HTML

**Goal:** Browse LSV posterior PSI distributions interactively with splice-graph topology.

**Approach:** Run `voila` on MAJIQ output to generate self-contained HTML.

```bash
# MAJIQ V3 (June 2025+) uses Zarr-format splicegraph (V2's .sql is deprecated)
voila view -p 5000 -j 8 build/splicegraph.zarr psi_output/sample.psi.voila -o voila_psi_html

voila view -p 5000 -j 8 build/splicegraph.zarr deltapsi_output/group1_group2.deltapsi.voila -o voila_dpsi_html
```

VOILA shows:
- Complete LSV graphs (single source / single target nodes)
- Per-junction posterior PSI violin plots
- ΔPSI distributions across all conditions
- Confidence by junction within an LSV

**The only tool that visualizes complex multi-junction LSVs intuitively.** For events that don't fit canonical SE/A5SS/A3SS, VOILA is the visualization of choice.

## leafviz Shiny App

**Goal:** Browse leafcutter clusters with intron-level effects, sashimi-like plots, and NMD annotation.

**Approach:** Prepare leafviz input from leafcutter differential output, then launch Shiny.

```bash
prepare_results.R \
    -o leafviz \
    -m groups.txt \
    leafcutter_perind_numers.counts.gz \
    ds_results_cluster_significance.txt \
    ds_results_effect_sizes.txt \
    annotation_codes
```

```r
library(leafviz)
run_leafviz('leafviz.RData')
```

Standalone alternative: `jackhump/leafviz` GitHub repo for the lightweight installable subset. Useful for cohort-level interactive filtering.

## Jutils for Tool-Agnostic Output

**Goal:** Visualize differential splicing output uniformly across rMATS, leafcutter, MntJULiP, and MAJIQ.

**Approach:** Convert tool output to Jutils' standard format, then plot.

```bash
python3 jutils.py convert-results --rmats-dir rmats_output/ --out-dir jutils_out/
python3 jutils.py heatmap --tsv-file jutils_out/rmats.tsv --meta-file meta.tsv --q-value 0.05
python3 jutils.py sashimi --tsv-file jutils_out/rmats.tsv --meta-file meta.tsv \
    --gtf annotation.gtf --coordinate chr1:1000-2000 --bam-list bam_list.tsv
python3 jutils.py venn-diagram --tsv-file-list jutils_out/rmats.tsv,jutils_out/leafcutter.tsv
```

(Yang 2021 *Bioinformatics*) Useful when comparing multiple tools' outputs across publications or doing meta-analysis.

## pyGenomeTracks for Multi-Track Figures

**Goal:** Combine splicing with chromatin or coverage tracks for publication figures.

**Approach:** Define tracks in an INI file (genes, BAM, BigWig, BED), then run `pyGenomeTracks --tracks tracks.ini --region ... -o figure.pdf`.

```ini
[gene_models]
file = annotation.gtf
height = 3
title = GENCODE v45
fontsize = 10
file_type = gtf

[ctrl_coverage]
file = ctrl_merged.bw
title = Control
color = #1f77b4
height = 3
file_type = bigwig

[trt_coverage]
file = trt_merged.bw
title = Treatment
color = #ff7f0e
height = 3
file_type = bigwig

[junctions]
file = junctions.bedpe
title = Junctions
height = 2
file_type = links
links_type = arcs
```

The `junctions.bedpe` file must be in **BEDPE format** (6 columns: chr1 start1 end1 chr2 start2 end2 [+ optional score]). Convert from regtools .bed12 junctions:

```bash
# Convert regtools junctions BED12 to BEDPE for pyGenomeTracks.
# regtools BED12 column 11 is blockSizes (anchor_left, anchor_right);
# column 12 is blockStarts (0, intron_length + anchor_left).
# Intron start = chromStart + anchor_left = $2 + a[1]
# Intron end   = chromStart + blockStarts[2] = $2 + b[2]
awk 'BEGIN{OFS="\t"} {split($11,a,","); split($12,b,","); s=$2+a[1]; e=$2+b[2]; print $1, s, s+1, $1, e-1, e, $5}' \
    regtools_junctions.bed > junctions.bedpe
```

```bash
pyGenomeTracks --tracks tracks.ini --region chr17:43094000-43125000 -o figure.pdf
```

## Reading Sashimi Plots (Interpretation Guide)

| Visual element | What it represents |
|----------------|--------------------|
| Filled coverage track | Read coverage at each genomic position (depth-normalized in `-A` mode) |
| Arc / curve between exons | Junction-spanning reads; arc connects donor to acceptor |
| Number on arc | Count of junction-spanning reads (raw, not normalized, unless `-A` set) |
| Arc thickness | Often proportional to read count (tool-dependent) |
| Gene model below | Exons (boxes) and introns (lines) from GTF |
| Multiple parallel tracks | Per-sample (default) or per-group (with `-O`) |

**Junction count interpretation:** the number on an arc is the absolute count of reads whose CIGAR string contained an `N` operation matching that intron coordinate. Higher = more usage. Compare counts on inclusion vs skipping arcs to estimate PSI visually.

**Color convention:** by convention, control = blue (`#1f77b4`), treatment = orange (`#ff7f0e`); always document. Use ColorBrewer or matplotlib defaults for >2 groups.

## Per-Tool Failure Modes

### ggsashimi: Off-Strand Junction Artifacts

**Trigger:** Stranded RNA-seq library plotted without strand specification.

**Mechanism:** ggsashimi reads BAM strand from CIGAR + flag; without strand info, antisense junctions appear as artifacts.

**Symptom:** Implausible junctions in regions with overlapping antisense genes; "noise" arcs at unexpected locations.

**Fix:** Set library strandedness with `-s MATE2_SENSE` (dUTP/TruSeq reverse-stranded PE; use `-s MATE1_SENSE` for forward, `-s SENSE`/`ANTISENSE` for single-end); verify orientation with RSeQC `infer_experiment.py`. Alternatively, pre-filter BAM by strand with `samtools view -f 16` / `-F 16`.

### rmats2sashimiplot: Wrong Coordinate Convention

**Trigger:** Older versions or non-default rMATS output.

**Mechanism:** rmats2sashimiplot expects 1-based coordinates from rMATS' .MATS.JC.txt; rMATS outputs 0-based half-open in some columns.

**Symptom:** Plot region shifted by 1 nt; arcs misaligned with gene model.

**Fix:** Verify rmats2sashimiplot version matches rMATS-turbo output convention; use ggsashimi for cleaner control.

### MAJIQ-VOILA: Browser Memory

**Trigger:** Loading large VOILA HTML in browser (cohort with hundreds of LSVs).

**Mechanism:** VOILA HTML embeds all LSV data; large cohorts produce >100 MB HTMLs.

**Symptom:** Browser unresponsive on opening; "page unresponsive" warnings.

**Fix:** Filter LSVs in MAJIQ before voila step (`--changing-pvalue-threshold 0.95` and `--changing-between-group-dpsi-threshold 0.2`); split into per-gene HTMLs.

### leafviz: Annotation Codes Mismatch

**Trigger:** Using leafviz with annotation_codes from different GENCODE version than leafcutter clusters.

**Mechanism:** annotation_codes encodes intron-to-event-class mapping per GTF version.

**Symptom:** Many clusters show as "unannotated" despite being in canonical GTF.

**Fix:** Generate annotation_codes from the same GENCODE version used in differential analysis.

## Customization Reference

| Visual goal | ggsashimi flag |
|-------------|-----------------|
| Reduce intron whitespace | `--shrink` |
| Identical y-axis across groups | `--fix-y-scale` |
| Per-group overlay aggregation | `-O 3 -A mean_j` |
| Larger figure | `--width 12 --height 4` |
| Bigger fonts | `--base-size 16` |
| Vector output | `-F pdf` or `-F svg` |
| Custom palette | Edit colors in groups TSV |
| Filter junction noise | `-M 10` (raise to 20+) |
| Transparency | `--alpha 0.25` |
| Restrict to protein-coding | pre-filter the GTF (`awk '$0 ~ /protein_coding/'`); ggsashimi has no feature-filter flag |

## Best Practices

| Tip | Rationale |
|-----|-----------|
| Use `--shrink` for genes with large introns | Keeps exons visible (TTN, brain genes with multi-kb introns) |
| `--fix-y-scale` for cross-group comparisons | Otherwise auto-rescaling visually exaggerates differences |
| Aggregate replicates with `-O 3 -A mean_j` | Reduces clutter; per-sample variance still shown via alpha |
| Limit to 3-4 groups per figure | More becomes hard to read |
| Include 200-500 nt flanking exons | Show full splicing context |
| For MXE events, plot both alternative exons | Otherwise only half of the event is visible |
| Check accessibility colors | Use ColorBrewer-safe palettes for color-blind readers |
| Always include a legend | Sashimi figures without legends are uninformative for non-experts |
| Specify output format explicitly | PDF for publication; PNG for slides; SVG for editing |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ggsashimi: 'samtools' not found` | samtools not in PATH | Install via conda; `which samtools` to verify |
| `ggsashimi: empty plot` | Region has no reads or wrong chromosome name | Check BAM with `samtools view sample.bam chr1:100-200`; chrom name match (chr1 vs 1) |
| `rmats2sashimiplot: KeyError 'IJC_SAMPLE_1'` | Old rmats2sashimiplot with new rMATS output | Update both to matching versions |
| `voila: out of memory` | Large LSV cohort | Filter by deltapsi threshold before voila |
| `pyGenomeTracks: ini parse error` | Missing closing bracket or invalid track type | Validate INI syntax; check `pyGenomeTracks --listTracks` for supported types |
| `leafviz: missing exon file` | annotation_codes path wrong | Re-run `prepare_results.R` with correct paths |

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| No junctions shown | Default `-M 10` too strict | Lower to `-M 3` or `-M 5` |
| Plot too crowded | Many samples without aggregation | Use `-O 3` to overlay groups |
| Annotation missing or wrong gene | GTF lacks gene_name attribute or wrong build | Verify GTF version vs BAM reference; pre-filter the GTF to the relevant features |
| Memory issues on large regions | >100 kb regions with many samples | Plot smaller windows or pre-extract reads with samtools view |
| Y-axis dominated by one peak | Outlier sample | Use `-A mean_j` to aggregate; or filter outlier |

## Related Skills

- differential-splicing - Identify events to plot; sashimi plots are validation
- splicing-quantification - Context for PSI values; sashimi provides visual confirmation
- data-visualization/genome-tracks - Multi-track figure design (pyGenomeTracks, Gviz)
- data-visualization/ggplot2-fundamentals - ggsashimi customization (extends ggplot2)
- data-visualization/color-palettes - Accessible color choices
- data-visualization/volcano-and-ma-plots - Volcano complement to sashimi
- data-visualization/heatmaps-clustering - Heatmap complement to sashimi

## References

- Katz et al 2010 *Nat Methods* - MISO sashimi plot original
- Garrido-Martin et al 2018 *PLoS Comput Biol* - ggsashimi
- Yang et al 2021 *Bioinformatics* - Jutils
- Vaquero-Garcia et al 2016 *eLife* - MAJIQ / VOILA
- Li et al 2018 *Nat Genet* - leafcutter / leafviz
- Ramirez et al 2018 *Nat Commun* - pyGenomeTracks
<!-- END FILE: alternative-splicing/sashimi-plots/SKILL.md -->

## 子目录：alternative-splicing/single-cell-splicing

<!-- BEGIN FILE: alternative-splicing/single-cell-splicing/SKILL.md -->
---
name: bio-single-cell-splicing
description: Analyzes alternative splicing at single-cell resolution. The first decision is library chemistry — 10X 3' is fundamentally limited (RT primes from poly-A, R2 falls in 3' UTR, <0.1 junction read per cell per AS event). Plate-based full-length methods (Smart-seq3, FLASH-seq, VASA-seq, STORM-seq) and single-cell long-read (MAS-Iso-seq, scISOr-Seq2) are the chemistries that give per-cell isoform structure. Tools include MARVEL (R, Smart-seq integrated), BRIE2 (Bayesian PSI with regulatory features and ELBO_gain test), scQuint (junction-cluster, plate-based; not for 10X), SpliZ (annotation-free Z-score), Psix (graph-smoothness regulated AS), and Sierra (alternative polyadenylation, often confused with AS). Use when analyzing isoform usage in scRNA-seq, identifying cell-type-specific splicing, or determining whether scRNA-seq chemistry supports splicing analysis at all.
tool_type: python
primary_tool: MARVEL
---

## Version Compatibility

Reference examples tested with: MARVEL 2.0+, BRIE2 0.2.4+, scQuint 0.1+, SpliZ 0.0.1+, Sierra 1.0+, Psix 0.1+, anndata 0.10+, scanpy 1.10+, pandas 2.2+, scipy 1.13+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Single-Cell Splicing Analysis

The fundamental decision is **chemistry**, not tool. Most droplet 3' scRNA-seq cannot support transcriptome-wide splicing inference because reverse transcription primes from the poly(A) tail and most reads land in the 3' UTR — far from CDS-region splicing events. Plate-based full-length methods and single-cell long-read sequencing are the chemistries that give per-cell isoform structure across the gene body.

## The 10X 3' Problem (Quantified)

Three compounding mechanisms make 10X Chromium 3' (v3.1, GEM-X, v4) hostile to splicing:

1. **3' enrichment**: median fragment <1 kb from poly(A); >70% of unique reads fall within 3' UTR.
2. **Short R2 (~91 nt)**: each read straddles at most one junction; usually none, because R2 lands in 3' UTR.
3. **PCR concatemers and TSO artifacts**: pollute junction detection; UMI collapse is gene-level, not isoform-level.

**Quantitative estimate:** Only a small fraction of cassette exons sit close enough to the polyA site to be sampled by 3' chemistry (empirical estimates from APA/3'-end atlases — see Tian & Manley 2017 *Nat Rev Mol Cell Biol* for the 3' UTR isoform landscape). Effective junction read yield from 10X 3' is **<0.1 per cell per AS event** — vs the 5-10 needed for stable per-cell PSI. Most splicing analyses on 10X 3' data report artifacts.

**The 5' kit (10X 5' GEX) does not solve this** — it shifts capture from 3' UTR to 5' UTR / TSS-proximal regions. Marginal improvement; not a transcriptome-wide solution. Note that V(D)J recovery requires the **10X Chromium Single Cell Immune Profiling kit** (with TCR/BCR-specific enrichment), not 5' GEX alone — postdocs designing immune-repertoire experiments must use the dedicated V(D)J kit.

## Decision: Does the Chemistry Support Splicing Analysis?

| Chemistry | Splicing analysis viable? | Best alternative if no |
|-----------|----------------------------|--------------------------|
| 10X 3' (Chromium v3, GEM-X, v4, Flex) | No (transcriptome-wide); maybe near-3'-end events | Sierra for APA |
| 10X 5' GEX | Limited; near-5'-end events only | Sierra for alternative TSS; switch to MAS-Iso-seq |
| Smart-seq2 | Yes (full transcript) | MARVEL or BRIE2 |
| Smart-seq3 / Smart-seq3xpress | Yes + UMI molecule counting | MARVEL or BRIE2 |
| FLASH-seq | Yes (faster, cheaper Smart-seq3) | MARVEL or BRIE2 |
| VASA-seq | Yes + total RNA (incl. nascent, IR) | MARVEL with IR analysis |
| STORM-seq | Yes + total RNA + ribodepletion | MARVEL with IR analysis |
| MAS-Iso-seq + 10X 5' (PacBio Kinnex) | Yes — full isoforms per cell | FLAMES, scNanoGPS, IsoQuant, see long-read-splicing |
| scISOr-Seq2 (PacBio + 10X) | Yes — full isoforms with cell-typing | FLAMES, IsoQuant |
| ONT direct cDNA scRNA | Yes | FLAMES |
| ONT direct RNA scRNA | Yes + native modifications | FLAMES |

## Tool Selection Matrix

| Tool | Best for | Input | Strengths | Fails when |
|------|----------|-------|-----------|------------|
| MARVEL | Smart-seq plate-based and (v2+) 10X droplet unified workflow | Plate or droplet BAMs + Seurat | SE/A5SS/A3SS/MXE/RI/AFE/ALE; modality classification; native Seurat integration; v2 droplet support | R-only |
| BRIE2 | Plate-based with regulatory feature prior | Plate BAM + GFF3 events | Bayesian variational PSI + ELBO_gain test; principled uncertainty; CLI-driven (`brie-count`, `brie-quant`) | TensorFlow dependency; slow at scale |
| scQuint | Plate-based annotation-free junction-cluster quantification (validated on Smart-seq2) | STAR junctions across cells | Cluster-level junction usage; latent Dirichlet | Authors recommend AGAINST use on 10X 3'/5' data (3'-bias confounds); plate-based only |
| SpliZ | Annotation-free discovery of cell-state-associated splicing | STAR-aligned BAMs | Per-gene Z-score; no event database needed | Annotation-free = power tradeoff |
| Psix | Regulated AS along trajectories | PSI matrix + kNN graph | Tests graph smoothness; robust to dropout | Needs cell-state graph upstream |
| Sierra | APA in 10X 3' (NOT splicing) | 10X BAM + GTF | Peak-calling 3' ends; DEXSeq DTU on UTR isoforms | APA only; not for cassette exons |
| pseudobulk leafcutter / rMATS | Between-cell-type differential splicing | Aggregated BAMs | Bulk-level statistical power | Loses within-cluster heterogeneity |
| MAS-Iso-seq + FLAMES | Full-length single-cell isoforms | 10X 5' + PacBio Kinnex | Full isoforms per cell at scale | Cost; complex pipeline |

## Decision Tree by Goal

| Goal | Recommended approach |
|------|----------------------|
| "Will my 10X 3' data support splicing?" | No transcriptome-wide; consider Sierra for APA. Note: scQuint authors recommend against use on 10X data |
| Cassette exon analysis in cell types from Smart-seq2 | MARVEL with `ComputePSI` + `AssignModality` + `CompareValues` |
| Discover cell-state-associated splicing without an event database | SpliZ |
| Test regulated AS along developmental pseudotime | Psix |
| Per-cell PSI with uncertainty in low-coverage cells | BRIE2 |
| Differential splicing between two well-defined cell types | Pseudobulk leafcutter or rMATS on aggregated BAMs |
| APA (alternative polyadenylation, often confused with AS) | Sierra |
| Full-length single-cell isoforms at scale | MAS-Iso-seq + FLAMES (long-read) |
| Microexons (3-27 nt) | Long-read or aligner with low overhang (uLTRA, deSALT) |
| snRNA-seq (nuclei) — IR question | Library captures nuclear RNA enriched for incomplete splicing — interpret IR cautiously |

## MARVEL Plate-Based Workflow

**Goal:** Run a unified workflow from STAR junctions to cell-type-specific splicing calls.

**Approach:** Build a wide splice-junction count matrix (rows = junctions keyed by `coord.intron`, columns = cells), assemble per-event feature tables, then construct MARVEL object with named slots (`SpliceJunction`, `SplicePheno`, `SpliceFeature`, `IntronCounts`, `GeneFeature`, `Exp`, `GTF`). Quantify PSI per event class, classify modality, test differential splicing.

```r
library(MARVEL); library(Seurat); library(data.table)

seurat_obj <- readRDS('cells.rds')

# Build wide SJ matrix: first column 'coord.intron' (e.g. 'chr1:100007082:100022621'),
# subsequent columns are per-cell sample IDs with junction counts as values.
# This is constructed from STAR SJ.out.tab files (one per cell) merged on intron coord.
sj_files <- list.files('star_pass2/', pattern='SJ.out.tab$', full.names=TRUE)
sj_long <- rbindlist(lapply(sj_files, function(f) {
    d <- fread(f, sep='\t', header=FALSE,
               col.names=c('chr','start','end','strand','motif','annot','unique','multi','overhang'))
    d$coord.intron <- paste(d$chr, d$start, d$end, sep=':')
    d$sample <- gsub('_SJ.out.tab$', '', basename(f))
    d[, .(coord.intron, sample, unique)]
}))
sj <- dcast(sj_long, coord.intron ~ sample, value.var='unique', fill=0)

# SpliceFeature is a NAMED LIST keyed by event class
df.feature.list <- list(
    SE   = read.table('events_SE.txt',   header=TRUE, sep='\t'),
    A5SS = read.table('events_A5SS.txt', header=TRUE, sep='\t'),
    A3SS = read.table('events_A3SS.txt', header=TRUE, sep='\t'),
    MXE  = read.table('events_MXE.txt',  header=TRUE, sep='\t'),
    RI   = read.table('events_RI.txt',   header=TRUE, sep='\t')
)

# SplicePheno: per-cell metadata; sample.id column maps to SpliceJunction column names
df.pheno <- seurat_obj@meta.data
df.pheno$sample.id <- rownames(df.pheno)

marvel <- CreateMarvelObject(
    SpliceJunction = sj,
    SplicePheno    = df.pheno,
    SpliceFeature  = df.feature.list,
    GeneFeature    = read.table('gene_features.tsv', header=TRUE, sep='\t'),
    Exp            = read.table('tpm.tsv', header=TRUE, sep='\t', row.names=1),
    GTF            = rtracklayer::import('annotation.gtf')
)

marvel <- ComputePSI(marvel, CoverageThreshold=10, EventType='SE')
marvel <- AssignModality(marvel, EventType='SE')
marvel <- CompareValues(
    marvel,
    cell.group.g1 = neurons, cell.group.g2 = glia,
    method = 'wilcox', n.cells = 25, psi.delta = 0.1
)
```

For 10X droplet data, MARVEL v2+ provides `CreateMarvelObject.10x()` and `AnnotateSJ.10x()` constructors. Verify the exact API via `?CreateMarvelObject.10x` in installed MARVEL.

MARVEL classifies events into modalities (Song 2017 *Mol Cell*): included (PSI~1), excluded (PSI~0), bimodal (mixture at 0/1), middle (peaked ~0.5), multimodal. Bimodality usually reflects mixed cell states or stochastic monoallelic-like bursting. Mid-modality (peaked at 0.5) can be technical (mixed cells in a droplet) — confirm with full-length data.

## BRIE2 Bayesian PSI

**Goal:** Estimate per-cell PSI with informative regulatory-feature prior; test cell-state association via likelihood-ratio testing on covariate effects.

**Approach:** BRIE2 is a CLI-driven workflow (`brie-count` for read counting, `brie-quant` for variational inference + LRT). Prepare a GFF3 of splicing events, count cell-barcoded junction reads, then fit the model with covariate testing.

```bash
# 1. Count splicing events per cell
brie-count \
    -a splicing_events.gff3 \
    -S sample_list.tsv \
    -o brie_counts/ \
    -p 16

# 2. Fit BRIE2 with LRT against the cell-type covariate
brie-quant \
    -i brie_counts/brie_count.h5ad \
    -c cell_metadata.tsv \
    -o brie_quant.h5ad \
    --interceptMode gene \
    --LRTindex All \
    --testBase null \
    --MCsize 3 \
    --batchSize 1000000 \
    -p 16
```

`--interceptMode gene` fits a gene-specific intercept (recommended); `--LRTindex All` tests all covariates; `--testBase null` uses the null model as the LRT reference. Verify exact flag set via `brie-quant -h` in installed BRIE2.

```python
import scanpy as sc

adata_splice = sc.read_h5ad('brie_quant.h5ad')
# Per-event covariate effects, ELBO values, and LRT statistics live in
# adata_splice.varm and adata_splice.var; column names depend on BRIE2 version.
# Inspect with: print(adata_splice); print(adata_splice.varm.keys())
# Per-event significance is typically derived from LRT delta-ELBO.
```

BRIE2 (Huang & Sanguinetti 2021 *Genome Biol*) uses a sequence-derived feature prior (exon length, GC content, splice site strength, motif counts) to regularize PSI estimates in low-coverage cells. The LRT-based covariate test answers "is this event associated with cell state?" without requiring per-cell PSI accuracy. Threshold the delta-ELBO at ~3 (analogous to log-Bayes-factor); confirm against version-specific output keys via the brie-tutorials repo.

## SpliZ for Annotation-Free Discovery

**Goal:** Identify splicing-defined cell populations without an event database.

**Approach:** Compute per-gene splicing Z-score across cells; test for cell-state association via permutation.

```bash
# SpliZ is a Nextflow pipeline (not a standalone CLI). Configure inputs in a .config
# file (dataname, input_file, libraryType, grouping_level_1/2) - either SICILIAN
# output (SICILIAN=true) or BAMs via a samplesheet CSV + metadata + GTF (SICILIAN=false).
nextflow run salzmanlab/spliz -r main -latest -c spliz.config
```

SpliZ (Olivieri 2022 *Nat Methods*) is robust to dropout because it pools junction information across the gene; particularly useful for discovering splicing diversity in heterogeneous tumor samples.

## Psix for Regulated AS Along Trajectories

**Goal:** Detect AS that varies coherently with cell state along a developmental trajectory, robust to dropout.

**Approach:** Score whether observed PSI is smooth on the cell-cell kNN graph from expression-space embedding.

```python
import psix
import scanpy as sc

adata = sc.read_h5ad('cells.h5ad')
sc.pp.neighbors(adata, n_neighbors=30, use_rep='X_pca')

psix_obj = psix.Psix(adata, psi_matrix_path='psi_matrix.tsv')
psix_obj.run_psix()

regulated = psix_obj.psix_results.query('psix_score > 1.5 and pvalue < 0.05')
```

Psix (Buen Abad Najar 2022 *Genome Res* 32:1385) is the principled alternative to imputing PSI: do not impute (it obliterates heterogeneity); test for graph smoothness instead.

## Sierra for APA (Not Splicing)

**Goal:** Detect alternative polyadenylation in 10X 3' data — frequently confounded with AS.

**Approach:** Peak-call read pile-ups at 3' ends, then DEXSeq-style DTU on 3' UTR isoforms.

```r
library(Sierra)

peak_file <- FindPeaks(
    output.file = 'peaks.txt',
    gtf.file = 'annotation.gtf',
    bam.file = 'possorted_genome_bam.bam'
)

counts <- CountPeaks(
    peak.sites.file = 'peaks.txt',
    gtf.file = 'annotation.gtf',
    bamfile = 'possorted_genome_bam.bam',
    whitelist.file = 'barcodes.tsv'
)

# CountPeaks returns a peak x cell matrix; annotate it and build a peak Seurat
# object before differential-usage testing.
peak.annotations <- AnnotatePeaksFromGTF(
    peak.sites.file = 'peaks.txt',
    gtf.file = 'annotation.gtf',
    output.file = 'peak_annotations.txt'
)

peaks.seurat <- NewPeakSeurat(
    peak.data = counts,
    annot.info = peak.annotations,
    cell.idents = cell_identities
)

apa_results <- DUTest(peaks.seurat, population.1 = ctrl_cells, population.2 = trt_cells)
```

If only 10X 3' data is available, this is often what is actually wanted. Distinct UTRs change miRNA targeting, RBP binding, and stability — biologically meaningful but not splicing.

## Pseudobulk for Statistical Power

**Goal:** Recover bulk-level statistical power for differential splicing between cell types.

**Approach:** Sum junction counts across cells of the same cluster, then run leafcutter / rMATS on aggregated counts.

```python
import pandas as pd
import numpy as np

def pseudobulk_junctions(junction_counts, cell_metadata, groupby='cell_type'):
    out = {}
    for group, cells in cell_metadata.groupby(groupby).groups.items():
        mask = junction_counts.columns.isin(cells)
        out[group] = junction_counts.loc[:, mask].sum(axis=1)
    return pd.DataFrame(out)
```

Use pseudobulk for differential splicing **between** well-defined cell types; use per-cell methods for **within-population heterogeneity** (graded splicing along pseudotime, bimodal cell-state mixtures).

## Single-Cell Long-Read = Future of Single-Cell Splicing

In 2024-2026, full-length single-cell long-read sequencing has become practical and is the recommended chemistry for splicing-focused single-cell experiments:

- **MAS-Iso-seq / PacBio Kinnex**: concatenated full-length cDNA arrays, ~16x throughput vs plain Iso-Seq, compatible with 10X 5' libraries (Al'Khafaji 2024 *Nat Biotech*)
- **scISOr-Seq2**: hybrid 10X + PacBio for cell typing + isoform structure (Joglekar et al 2024 *Nat Neurosci* 27:1051-1063, single-cell long-read brain isoform mapping)
- **ONT direct cDNA + 10X**: lower cost, similar information content
- **FLAMES**: barcode demultiplexing + isoform quantification + SNV calling for ONT scRNA (Tian 2021 *Genome Biol* 22:310)

For splicing-specific full-length single-cell analysis, see `long-read-splicing` skill.

## Per-Tool Failure Modes

### MARVEL: SpliceJunction Matrix Format

**Trigger:** Building the SpliceJunction matrix from STAR SJ.out.tab incorrectly (e.g. long-format instead of wide).

**Mechanism:** MARVEL plate-based `CreateMarvelObject(SpliceJunction = ...)` expects a **wide matrix** with first column `coord.intron` (formatted `chr:start:end`) and subsequent columns being per-cell sample IDs with integer junction counts. Long-format data.frames or missing `coord.intron` column cause runtime errors.

**Symptom:** "no `coord.intron` column found" errors; or empty PSI tables despite junction reads being present.

**Fix:** Verify wide-matrix structure; ensure SJ.out.tabs are merged on the `chr:start:end` key with cells as columns. Use `data.table::dcast` for the long->wide reshape.

### BRIE2: TensorFlow Memory

**Trigger:** Large cohort (>10k cells) with deep coverage.

**Mechanism:** Variational inference loads full count matrix; TensorFlow allocates GPU memory aggressively.

**Symptom:** OOM kills; training stalls.

**Fix:** Reduce `--batchSize` from default (500000) to 100000 or 50000; train per-chromosome batch; use CPU mode for very small cohorts. Note flag is camelCase `--batchSize`, not `--batch_size`.

### scQuint: 3' Data Sparsity

**Trigger:** Running scQuint on 10X 3' v3 data hoping for splicing signal.

**Mechanism:** scQuint's latent Dirichlet model needs junction counts; 10X 3' yields too few junction reads to fit the model robustly.

**Symptom:** All cells assign to one cluster; no informative splicing signal.

**Fix:** Pivot to APA analysis with Sierra; or upgrade chemistry to MAS-Iso-seq.

### Psix: Missing kNN Graph

**Trigger:** Running Psix without precomputed cell-cell graph.

**Mechanism:** Psix tests PSI smoothness on a pre-existing cell-cell graph; without one, no smoothness statistic.

**Symptom:** Empty results or error about missing `connectivities`.

**Fix:** Run `sc.pp.neighbors(adata)` before Psix; ensure `connectivities` is in `adata.obsp`.

### Sierra: Annotation Gaps

**Trigger:** GTF missing 3'UTR annotations.

**Mechanism:** Sierra peak-calls within annotated 3'UTRs; missing annotations mean missed peaks.

**Symptom:** Few peaks detected; gene-level coverage but no APA calls.

**Fix:** Use comprehensive GENCODE annotation; or run de-novo peak calling first.

## Reconciliation: When Single-Cell Tools Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| MARVEL sig, BRIE2 not | Per-cell PSI noise (BRIE2 conservative); MARVEL pseudobulk-like | Trust MARVEL for cell-type comparisons; BRIE2 for within-cluster |
| BRIE2 sig, MARVEL not | Cell-state effect smoother than cell-type boundary | Test along trajectory with Psix |
| SpliZ sig, MARVEL not | Annotation-free SpliZ catches novel events | Investigate junction structure manually |
| Sierra sig, MARVEL not | Sierra is APA, MARVEL is splicing — different biology | Distinguish in interpretation |
| Pseudobulk sig, per-cell not | Power issue; effect averaged out per-cell | Report at cluster level, not per-cell |

## Quantitative Concepts Unique to Single-Cell

**Per-cell PSI vs pseudobulk PSI:**
- Per-cell PSI: meaningful only when junction coverage exceeds ~10-20 reads per cell per event (plate-based or long-read).
- Pseudobulk PSI: aggregate, recovers bulk-level statistical power, discards within-cluster heterogeneity.

**Modality detection in PSI distributions** (Song 2017 *Mol Cell*):
| Modality | PSI distribution | Biology |
|----------|------------------|---------|
| Included | Peaked at 1 | Constitutive inclusion |
| Excluded | Peaked at 0 | Constitutive skipping |
| Bimodal | Mixture at 0 and 1 | Mixed cell states or monoallelic-like bursting |
| Middle | Peaked ~0.5 | Often technical (well-contamination, doublets, or low-coverage shrinkage to prior); confirm with full-length |
| Multimodal | Multiple peaks | Complex regulation; deserves follow-up |

**Beta-binomial vs binomial models:** with sparse counts, binomial PSI is overdispersed. Beta-binomial models (BRIE2; leafcutter2 as Dirichlet-multinomial cluster-level) handle this. For very sparse droplet data, even beta-binomial fits poorly per cell — collapse to pseudobulk.

**Imputation pitfalls:** naive imputation (MAGIC, scImpute, ALRA) of expression matrices is **not** appropriate for PSI: imputing missing junction counts averages over neighboring cells and obliterates the very heterogeneity under study. Psix's approach — testing smoothness of observed PSI on the kNN graph — is the principled alternative.

## Cell-Type-Specific Splicing Biology

| System | Event | Regulator |
|--------|-------|-----------|
| Neural microexons | 3-27 nt exons enriched in brain | SRRM4/nSR100 (Irimia 2014 *Cell*); SRRM3 in retina/photoreceptors (Ciampi 2022 *PNAS*) |
| Neural differentiation | PTBP1 -> PTBP2 switch | miR-124 represses PTBP1; derepresses neural exons (Boutz 2007 *Genes Dev*) |
| T-cell activation | CD45 RA -> RO | hnRNP-L, ESRP-mediated |
| Erythropoiesis | EPB41 exon 16 | Splicing factor switching during maturation |
| Cardiac development | TTN N2BA -> N2B | MBNL1/CELF1 antagonism |
| EMT | FGFR2 IIIb -> IIIc, ENAH exon 11a | ESRP1/2 loss in mesenchymal state (Warzecha 2009 *Mol Cell*) |
| Activated T cell | CD45 isoform shift | Multiple SR/hnRNP regulators |

## Quality Thresholds

| Metric | Recommendation |
|--------|----------------|
| Cells per event with reads | >=50 (per-cell PSI); >=200 cells per cluster (pseudobulk) |
| Junction reads per event per cell | >=5 with coverage; <=1 = unreliable |
| PSI variance for cell-type call | <0.1 within cluster, >0.2 between clusters |
| Library | full-length plate or long-read for transcriptome-wide; 3' for APA only |
| Doublet filtering | Required before splicing analysis (DoubletFinder, Scrublet) |
| Cells per cluster (pseudobulk) | >=100 ideal; >=50 minimum |
| nuclear vs whole-cell | snRNA-seq enriches IR; treat with caution |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `MARVEL: ComputePSI returns empty` | STAR SJ.out.tab missing strand info | Re-run STAR with `--outSJtype Standard` |
| `brie.tl.fit: NaN loss` | Insufficient junction reads per cell | Filter cells with `min_reads=20`; raise threshold |
| `scQuint: convergence not reached` | LDA model fit on too-few junctions | Aggregate by chromosome; or switch chemistry |
| `Psix: missing connectivities` | Neighbors graph not computed | Run `sc.pp.neighbors(adata)` first |
| `Sierra: no peaks called` | GTF missing 3'UTR annotations | Use comprehensive GENCODE; or de-novo peak-call |
| `MARVEL: ggplot error` | Seurat version mismatch | Match MARVEL and Seurat versions |
| `FLAMES: barcode rescue failed` | Short-read 10X output not in expected directory | Verify cellranger output structure |

## Common Pitfalls

- **Treating 10X 3' splicing analysis as legitimate** — the chemistry doesn't support it. Use Sierra for APA or upgrade to MAS-Iso-seq.
- **Imputing PSI matrices** — destroys the heterogeneity to be detected. Use Psix or BRIE2 instead.
- **Per-cell PSI on droplet data** — typically too sparse for stable estimates. Use pseudobulk first, then drill down to per-cell.
- **Confusing APA with splicing** — Sierra results look like AS but are 3' UTR isoforms. Different machinery, different biology.
- **snRNA-seq IR signal misinterpreted as splicing dysregulation** — nuclear RNA is enriched for incompletely spliced transcripts; baseline IR is high.
- **Trusting per-cell PSI from BRIE2 without ELBO_gain test** — BRIE2's per-cell point estimates are noisy; the principled output is the ELBO_gain cell-state-association statistic.
- **Microexon analysis with default short-read aligners** — anchors >=20 nt miss most microexons; use VAST-TOOLS, MicroExonator, or long-read.
- **Skipping doublet filtering before splicing** — doublets create artificial PSI mid-modality.

## Related Skills

- single-cell/preprocessing - QC and normalization (must run before splicing)
- single-cell/clustering - Cell type annotation prerequisite
- single-cell/doublet-detection - Doublet filtering critical for splicing
- single-cell/data-io - h5ad / Seurat I/O
- splicing-quantification - Bulk RNA-seq comparison context
- long-read-splicing - Full-isoform analysis from MAS-Iso-seq, scISOr-Seq2; future of single-cell splicing

## References

- Huang & Sanguinetti 2021 *Genome Biol* - BRIE2
- Wen et al 2023 *Nucleic Acids Research* 51:e29 - MARVEL
- Benegas, Fischer & Song 2022 *eLife* - scQuint (annotation-free single-cell splicing analysis, validated on Smart-seq2)
- Olivieri et al 2022 *Nat Methods* - SpliZ
- Buen Abad Najar et al 2022 *Genome Research* 32:1385 - Psix
- Patrick et al 2020 *Genome Biol* - Sierra
- Song et al 2017 *Mol Cell* - splicing modality classification
- Picelli et al 2014 *Nat Protoc* - Smart-seq2
- Hagemann-Jensen et al 2020 *Nat Biotech* - Smart-seq3
- Hagemann-Jensen et al 2022 *Nat Biotech* - Smart-seq3xpress
- Hahaut et al 2022 *Nat Biotech* - FLASH-seq
- Salmen et al 2022 *Nat Biotech* - VASA-seq
- Johnson et al 2022 *bioRxiv* 10.1101/2022.03.14.484332 - STORM-seq (preprint)
- Al'Khafaji et al 2024 *Nat Biotech* - MAS-Iso-seq / Kinnex
- Tian et al 2021 *Genome Biology* 22:310 - FLAMES
- Joglekar et al 2024 *Nat Neurosci* 27:1051-1063 - scISOr-Seq2 single-cell brain isoform mapping
- Irimia et al 2014 *Cell* - neural microexons / SRRM4
- Ciampi et al 2022 *PNAS* 119:e2117090119 - SRRM3-dependent photoreceptor microexons
- Boutz et al 2007 *Genes Dev* - PTBP1/PTBP2 neural switch
- Tian & Manley 2017 *Nat Rev Mol Cell Biol* - alternative polyadenylation and 3' UTR isoforms
<!-- END FILE: alternative-splicing/single-cell-splicing/SKILL.md -->

## 子目录：alternative-splicing/splice-variant-prediction

<!-- BEGIN FILE: alternative-splicing/splice-variant-prediction/SKILL.md -->
---
name: bio-splice-variant-prediction
description: Predicts whether a DNA variant alters mRNA splicing using sequence-based deep-learning tools — SpliceAI (10kb context dilated CNN, clinical default), Pangolin (multi-tissue), MMSplice (modular per-region CNN with calibrated ΔPSI), SpliceTransformer/TrASPr (tissue-aware transformers), SpliceVault (empirical 300K-RNA lookup of likely mis-splicing outcomes), CADD-Splice (composite score). Applies the ClinGen SVI 2023 framework for ACMG/AMP variant interpretation (PVS1, PP3, BP4 evidence codes), HGVS splicing nomenclature (c.123+1G>A, c.123-3T>G, r.spl?), extended-window scoring for deep-intronic pseudoexons, tissue-specific predictions, branchpoint variant detection (BPHunter, LaBranchoR), and splice-switching ASO design. Use when interpreting splice impact of clinical variants, prioritizing VUS, identifying deep-intronic pathogenic variants, or designing ASOs.
tool_type: python
primary_tool: SpliceAI
---

## Version Compatibility

Reference examples tested with: SpliceAI 1.3+, Pangolin 1.0+, MMSplice 2.4+, pyensembl 2.3+, pysam 0.22+, pandas 2.2+, gffutils 0.13+, tensorflow 2.15+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Splice Variant Prediction

Predict whether a DNA variant alters mRNA splicing. **Distinct from "variant pathogenicity" generally**: a variant can be a strong splice disruptor without being pathogenic for the gene's standard mechanism, or pathogenic for reasons orthogonal to splicing. Splice prediction asks specifically: does this variant change splice-site usage?

## Predictor Taxonomy

| Family | Architecture | Output | Fails when |
|--------|--------------|--------|------------|
| Context-aware CNN | 10 kb dilated ResNet | Per-position donor/acceptor probability | Long-range (>5 kb) regulatory effects; tissue-specific events |
| Tissue-aware CNN/transformer | Same arch + multi-tissue training | Per-tissue ΔPSI | Tissue not in training set; novel cell types |
| Modular per-region CNN | Separate sub-models for 5'ss/3'ss/exon/intron | Calibrated quantitative ΔPSI | Atypical events; complex multi-junction effects |
| Foundation transformer | Pretrained on broad genomic context | Splice probability or ΔPSI | New tools; less battle-tested |
| Empirical lookup | Public RNA-seq event database | Top-N most likely mis-splicing outcomes | Variant types not represented in training cohorts |
| Composite score | Blend of multiple predictors | Single scaled score | When component predictors disagree internally |

## Tool Selection Matrix

| Tool | Best for | Output | When to use | Fails when |
|------|----------|--------|-------------|------------|
| SpliceAI | Clinical screening; canonical splice site disruption | Delta score 0-1 | Default for ACMG variant classification | Tissue-specific events; deep-intronic with default 50nt window |
| Pangolin | Tissue-aware predictions | Per-tissue ΔPSI | When disease tissue is known (brain, heart, liver, testis) | Tissue not in 4-tissue training set |
| MMSplice | Quantitative ΔPSI | Δlogit_psi | Research where calibrated effect-size matters | Atypical events outside cassette-exon model |
| SpliceTransformer | 2024+ benchmark improvements | Tissue-specific ΔPSI | When transformer foundation models outperform CNN on benchmark variant sets | New (2024); limited clinical adoption |
| TrASPr | Multi-transformer, 2024-2025 | Tissue-specific PSI/ΔPSI | Strong on tissue-specific test sets | New; verify before clinical use |
| SpliceVault | Empirical mis-splicing outcome | Top-N events at the affected splice site | Predicting consequence (skip vs cryptic) of canonical-disrupting variants | Variants not represented in 300K-RNA training |
| CADD-Splice | Single composite score | Scaled C-score | Clinical pipelines wanting one number | When knowing which sub-component drove the score is needed |

Methodology evolves; verify benchmarks (Smith & Kitzman 2023 *Genome Biol* 24:294; You et al 2024 *Nat Commun*) and ClinGen SVI splicing recommendations before reporting clinical interpretations. Concordance across SpliceAI + Pangolin + MMSplice is gold-standard evidence; discordance flags need RNA validation.

## Decision Tree by Use Case

| Use case | Recommended approach |
|----------|----------------------|
| Clinical variant report (single variant, ACMG classification) | SpliceAI default 50nt + ClinGen SVI 2023 thresholds |
| Tissue-specific clinical question (brain disease, cardiomyopathy) | SpliceAI + Pangolin (tissue-matched) |
| Unsolved Mendelian case (suspect deep-intronic) | SpliceAI extended window (-D 500-2000) + SpliceVault |
| VUS panel screening | SpliceAI + Pangolin + MMSplice concordance scoring |
| Predict consequence of canonical-disrupting variant | SpliceVault top-N empirical events |
| Branchpoint variant suspected | BPHunter (branchpoint screen) — SpliceAI is weak here |
| Splice-switching ASO design (target ESE/ESS occlusion) | SpliceAI on masked sequence + RNAfold accessibility |
| Validate predicted splice change in patient | RNA-seq + FRASER2 (see outlier-splicing-detection) |
| Pseudoexon prediction in deep intron | SpliceAI extended window + CI-SpliceAI; require RNA validation |

## ClinGen SVI 2023 Framework

The ClinGen Sequence Variant Interpretation (SVI) splicing subgroup (Walker 2023 *Am J Hum Genet*) extended the ACMG/AMP 2015 framework with explicit splice-prediction rules.

| Evidence code | Threshold | Notes |
|----------------|-----------|-------|
| **PP3** (supporting pathogenic) | SpliceAI delta >= 0.20 | ClinGen SVI: apply at **supporting** weight (not standalone) |
| **BP4** (supporting benign) | SpliceAI delta <= 0.10 | ClinGen SVI: apply at **supporting** weight |
| **PVS1** (very strong null) | Canonical +/-1, +/-2 site disruption with predicted LoF + NMD | Requires gene where LoF is established mechanism (Abou Tayoun 2018 *Hum Mutat* PVS1 decision tree) |
| **PS3 / BS3** (functional) | RNA evidence (RT-PCR, RNA-seq, minigene) | Supersedes computational evidence |

**Operational rules:** Computational evidence (PP3/BP4) is *supporting*, not standalone. ClinGen SVI 2023 recommends applying predictive splice PP3/BP4 at **supporting** weight only; higher SpliceAI cutoffs (0.5, 0.8) increase precision but are the tool's own tiers (Jaganathan 2019), NOT ClinGen-endorsed evidence-strength upgrades — reaching moderate/strong requires functional/RNA evidence (PS3/BS3), not a higher SpliceAI score alone. Splicing variants benefit from concordance across SpliceAI + Pangolin + MMSplice. RNA validation supersedes prediction. Always log SpliceAI version, distance window, and reference transcript. SpliceAI alone is **not sufficient** for PVS1; canonical site disruption requires gene-level LoF context.

## SpliceAI Workflow

**Goal:** Annotate VCF variants with per-variant delta scores for splice-site change.

**Approach:** Run `spliceai` CLI with reference genome and annotation; parse INFO field for delta scores. **SpliceAI is human-only** (`-A grch37` or `-A grch38`); the model was trained on GENCODE human and does not directly transfer to mouse, fly, or other species. For mouse, retrained variants exist (e.g. mouseSpliceAI); for other species, use Pangolin (4 species: human, mouse, rat, rhesus macaque) or accept that prediction will be unreliable.

```bash
spliceai \
    -I input.vcf \
    -O output.vcf \
    -R GRCh38.primary_assembly.genome.fa \
    -A grch38 \
    -D 50 \
    -M 0
```

`-D 50` = distance window in nt around variant (default 50). For deep-intronic variants suspected of creating pseudoexons, raise to **500-2000**:

```bash
spliceai -I input.vcf -O output_extended.vcf -R genome.fa -A grch38 -D 500 -M 1
```

`-M 0` (default) returns raw scores; `-M 1` masks splice gains at annotated sites and losses at unannotated sites (cleaner for clinical use). Output INFO format: `SpliceAI=ALLELE|SYMBOL|DS_AG|DS_AL|DS_DG|DS_DL|DP_AG|DP_AL|DP_DG|DP_DL`. Delta score = max(DS_AG, DS_AL, DS_DG, DS_DL).

```python
import pandas as pd
import re

def parse_spliceai_vcf(vcf_path):
    rows = []
    with open(vcf_path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            fields = line.strip().split('\t')
            info = fields[7]
            m = re.search(r'SpliceAI=([^;]+)', info)
            if not m:
                continue
            for ann in m.group(1).split(','):
                parts = ann.split('|')
                allele, symbol = parts[0], parts[1]
                ds = [float(p) if p != '.' else 0 for p in parts[2:6]]
                dp = parts[6:10]
                rows.append({
                    'chrom': fields[0], 'pos': int(fields[1]),
                    'ref': fields[3], 'alt': allele,
                    'gene': symbol,
                    'DS_AG': ds[0], 'DS_AL': ds[1],
                    'DS_DG': ds[2], 'DS_DL': ds[3],
                    'delta_max': max(ds),
                })
    return pd.DataFrame(rows)

df = parse_spliceai_vcf('output.vcf')
df['acmg_evidence'] = pd.cut(
    df['delta_max'],
    bins=[-0.01, 0.10, 0.20, 0.50, 0.80, 1.01],
    # ClinGen SVI applies splice PP3/BP4 at supporting weight; 0.5/0.8 are SpliceAI
    # precision tiers (Jaganathan 2019), NOT ACMG evidence-strength upgrades
    labels=['BP4', 'inconclusive', 'PP3_supporting', 'PP3_supporting_prec0.5', 'PP3_supporting_prec0.8']
)
```

DS labels: AG = acceptor gain, AL = acceptor loss, DG = donor gain, DL = donor loss.

## Pangolin for Tissue-Specific Prediction

**Goal:** Get tissue-specific splice impact predictions when disease tissue is known.

**Approach:** Run Pangolin CLI with VCF + reference + gffutils annotation database.

```bash
python -c "import gffutils; gffutils.create_db('gencode.v45.annotation.gff3', 'gencode.db', force=True)"

pangolin \
    input.vcf \
    GRCh38.primary_assembly.genome.fa \
    gencode.db \
    pangolin_output \
    -d 500 \
    -m True \
    -s 0.2
```

`-m True` masks splice gains at annotated sites and losses at unannotated sites (recommended for clinical use). `-s 0.2` outputs all sites with predicted change >= cutoff.

Pangolin output is a VCF with per-tissue predictions across the **4 tissues used at training: brain, heart, liver, testis** (Zeng & Li 2022 *Genome Biol*). The model outputs per-species per-tissue predictions but extrapolates poorly to tissues outside this set. Use the tissue closest to disease-relevant context. **For tissues not in the 4-tissue training set, fall back to SpliceAI** — Pangolin extrapolates poorly to unseen tissues.

## SpliceVault for Empirical Mis-Splicing Outcomes

**Goal:** Predict the *type* of mis-splicing (exon skipping vs cryptic site activation) given a canonical-disrupting variant.

**Approach:** Query SpliceVault's database of empirical mis-splicing events from public RNA-seq.

```python
import requests

# Web API: https://kidsneuro.shinyapps.io/splicevault/
# Or use the R/Python package at github.com/kidsneuro-lab/SpliceVault

# Example: NM_000546.6:c.673-2A>G (TP53)
# Returns top-N most likely mis-splicing events: exon skipping, cryptic 3'ss usage, etc.
```

SpliceVault (Dawes 2023 *Nat Genet*) showed that the **Top-4 events** at any splice site predict variant-associated mis-splicing with ~92% sensitivity overall (96% of exon-skipping and 86% of cryptic-activation events) — a striking regularity that makes consequence prediction tractable. Use SpliceVault when the question is not "will splicing change?" but "what specific aberrant splicing will occur?".

## MMSplice for Calibrated ΔPSI

**Goal:** Predict quantitative ΔPSI (not just probability of disruption) for cassette exons.

**Approach:** Score variant impact on each splicing region (5'ss, 3'ss, exon, intron-3'/5') and combine.

```python
from mmsplice.vcf_dataloader import SplicingVCFDataloader
from mmsplice import MMSplice, predict_save

dl = SplicingVCFDataloader(
    gtf='gencode.v45.basic.gtf',
    fasta_file='GRCh38.fa',
    vcf_file='input.vcf'
)

model = MMSplice()
predict_save(model, dl, 'mmsplice_predictions.csv', pathogenicity=True)
```

MMSplice (Cheng 2019 *Genome Biol*) reports Δlogit_psi per variant. Useful when calibrated effect sizes matter (research) more than probability of disruption (clinical screening). Companion **MTSplice** (Cheng 2021 *Genome Biol*) adds tissue-specific Δψ predictions.

## HGVS Splicing Nomenclature

Following den Dunnen 2016 *Hum Mutat*:

| Notation | Meaning |
|----------|---------|
| `c.123+1G>A` | +1 of intron downstream of exon ending at cDNA position 123 (canonical 5'ss G) |
| `c.123+5G>A` | +5 position of donor (consensus region) |
| `c.124-1G>A` | -1 of acceptor (canonical AG) |
| `c.124-3T>G` | -3 of acceptor (Py-tract / BPS region) |
| `c.124-50A>G` | Deep-intronic; may activate cryptic site |
| `r.123_456del` | RNA-level deletion (predicted exon skipping) |
| `r.spl?` | Unknown splice consequence |
| `r.0?` | No detectable RNA |
| `p.0?` | Unknown protein consequence |
| `p.(=)` | No predicted protein change (silent) |

Validation tools: VariantValidator (Freeman 2018 *Hum Mutat*), Mutalyzer 2 (Lefter et al 2021 *Bioinformatics* 37:2811-2817).

## Extended-Window Scoring for Deep-Intronic Variants

SpliceAI's default precomputed scores use a **50-nt window**, missing variants that create pseudoexons in deep intronic regions. For unsolved Mendelian cases:

```bash
# Recompute with extended window
spliceai -I input.vcf -O output_2kb.vcf -R genome.fa -A grch38 -D 2000

# Or use CI-SpliceAI (Strauch 2022 PLoS One), SpliceAI retrained on curated GENCODE splice sites
```

| Window | Tradeoff |
|--------|----------|
| -D 50 (default) | Fast; captures canonical-site disruption; misses deep-intronic |
| -D 500 | Captures most pseudoexon-creating deep-intronic variants |
| -D 2000 | Maximum sensitivity; some false positives at large distances |

Pseudoexon creation in deep introns explains a substantial fraction of unsolved Mendelian disease alleles in current cohorts (estimates 5-15% across studies; specific quantitative range will vary by cohort and panel — verify against current literature). Disease examples: CFTR 3849+10kbC>T, USH2A c.7595-2144A>G, CEP290 c.2991+1655A>G (LCA10).

## Concordance Across Predictors

```python
import pandas as pd

merged = (spliceai_df
    .merge(pangolin_df, on=['chrom', 'pos', 'alt'], suffixes=('_sai', '_pang'))
    .merge(mmsplice_df, on=['chrom', 'pos', 'alt'])
)

merged['concordance'] = (
    (merged['delta_max_sai'] >= 0.2).astype(int) +
    (merged['pangolin_score'].abs() >= 0.2).astype(int) +
    (merged['delta_logit_psi'].abs() >= 1.0).astype(int)
)

merged['interpretation'] = merged['concordance'].map({
    0: 'concordant_benign',
    1: 'discordant_low_evidence',
    2: 'concordant_evidence',
    3: 'high_concordance_pathogenic'
})
```

| Concordance | Interpretation | Action |
|-------------|----------------|--------|
| 3/3 above threshold | High confidence | PP3 (supporting); strong candidate for RNA validation (PS3) |
| 2/3 above | Concordant evidence | PP3 (supporting) |
| 1/3 above | Discordant | Report inconclusive; flag for RNA validation |
| 0/3 above | Concordant benign | BP4 (supporting) |

Discordance is the most informative pattern — variants where one model sees impact and others don't are high priority for RNA validation.

## Branchpoint Variant Detection

All current tools are **weak at branchpoint variants** because the BPS motif (yUnAy) has low information content. Specific branchpoint tools:

| Tool | Method | Notes |
|------|--------|-------|
| BPP | Mixture model (BP motif + polypyrimidine tract) | Zhang 2017 *Bioinformatics* 33:3166 |
| LaBranchoR | Bidirectional LSTM | Paggi & Bejerano 2018 *RNA* 24:1647 |
| SVM-BPfinder | SVM on conservation+sequence | Corvelo 2010 *PLoS Comput Biol* |
| BPHunter | Genome-wide branchpoint screen against an aggregated experimental (lariat/RNA-seq) + computational BP database | Zhang 2022 *PNAS* |

Branchpoint variants are under-recognized in clinical pipelines; SpliceAI captures only some because branchpoint motifs have low information content. **Recommendation:** when SpliceAI delta is borderline (0.1-0.3) for a variant in the BPS region (-18 to -40 from 3'ss), run BPHunter as supplement.

## Splice-Switching ASO Design

**Goal:** Design antisense oligonucleotides to modulate splicing therapeutically (e.g. SMA ISS-N1, DMD exon skipping).

**Approach:** Use SpliceAI to predict impact of binding-site occlusion; check accessibility (RNAfold); avoid SR/hnRNP off-target motifs.

```python
# Conceptual workflow - actual design uses ASO synthesis platforms
# 1. Identify target ESE/ESS/ISE/ISS region from MaxEntScan + SpliceAI scan
# 2. Design candidate 18-22 nt ASOs spanning the regulatory element
# 3. For each ASO, simulate splice-site occlusion impact via SpliceAI on the masked sequence
# 4. Filter for RNA accessibility (avoid stable hairpins) using RNAfold
# 5. Whole-transcriptome SpliceAI scan for off-target binding (>=17/20 nt match)
# 6. Avoid TLR9 immunostimulatory CpG motifs

# Chemistry choices:
# - 2'-MOE-PS: nusinersen-like (CNS, intrathecal)
# - PMO: DMD ASOs (systemic IV)
# - GalNAc-conjugated: hepatic targeting
```

Approved precedents: **nusinersen** (SMA ISS-N1 occlusion, exon 7 inclusion); **risdiplam** (small-molecule SMN2 splicing modulator); **eteplirsen/golodirsen/casimersen/viltolarsen** (DMD exon skipping). Design references: Hua 2008 *AJHG*; Roberts et al 2023 *Nat Rev Drug Discov* 22:917 (DMD therapeutic approaches).

## Per-Tool Failure Modes

### SpliceAI: 50nt Window Limitation

**Trigger:** Variant deep in an intron (>50 nt from canonical splice site).

**Mechanism:** Default precomputed scores use ±50 nt window; the model is trained on this context but pre-stored scores limit lookups.

**Symptom:** Known pathogenic deep-intronic variant scores low (<0.2); no pseudoexon detected.

**Fix:** Re-run with `-D 500` or `-D 2000`; or try CI-SpliceAI (SpliceAI retrained on curated GENCODE splice sites) as a second predictor.

### SpliceAI: Tissue Agnosticism

**Trigger:** Variant in a tissue-specific gene (NEFM in neurons, MAPT brain, DMD muscle isoforms).

**Mechanism:** SpliceAI is trained on aggregate GENCODE annotation; tissue-specific events with weak constitutive use score low.

**Symptom:** Tissue-specific pathogenic variant has low SpliceAI delta; functional impact still observed in target tissue.

**Fix:** Use Pangolin for tissue-aware prediction; or SpliceTransformer; require RNA validation in disease-relevant tissue.

### Pangolin: Out-of-Training Tissue

**Trigger:** Disease tissue not represented in Pangolin's 4-species, 4-tissue (Cardoso-Moreira 2019 developmental) training set.

**Mechanism:** Pangolin extrapolates poorly to tissues outside training distribution.

**Symptom:** Pangolin score uncalibrated for queried tissue; doesn't agree with patient RNA-seq from that tissue.

**Fix:** Fall back to SpliceAI for tissues not in Pangolin training; or run patient RNA-seq directly.

### MMSplice: Atypical Events

**Trigger:** Variant affecting a non-cassette event (MXE, complex multi-junction, AFE/ALE).

**Mechanism:** MMSplice modular model is trained primarily on cassette exon events.

**Symptom:** MMSplice ΔPSI doesn't match other predictors or empirical data for non-cassette events.

**Fix:** Use SpliceAI for non-cassette events; restrict MMSplice to cassette exon contexts.

### CADD-Splice: Loss of Component Information

**Trigger:** Wanting to know which sub-component drove a high CADD-Splice score.

**Mechanism:** CADD-Splice combines SpliceAI + MMSplice + CADD into a single C-score; sub-component contributions are abstracted.

**Symptom:** "High CADD-Splice score but unclear why."

**Fix:** Run SpliceAI and MMSplice separately to see which contributed.

### Branchpoint Variants: Low Information Motif

**Trigger:** Variant in the BPS region (-18 to -40 from 3'ss).

**Mechanism:** BPS motif (yUnAy) has low information content; CNNs struggle to learn the consensus.

**Symptom:** Confirmed BPS variant scores SpliceAI delta <0.2 despite functional disruption.

**Fix:** Use BPHunter (Zhang 2022 *PNAS*) for genome-wide branchpoint screening; require RNA validation.

## Population Database Lookup

| Database | Use for |
|----------|---------|
| gnomAD v4 | Allele frequency; SpliceAI annotations integrated |
| ClinVar | Existing classifications; SpliceAI integrated since 2020 |
| SpliceVarDB | Curated splice variants with experimental RNA validation |
| dbNSFP4 | Pre-computed splice scores aggregated |
| Recount3 | Tissue-specific PSI lookups from public RNA-seq |
| GTEx sQTL v8 | Tissue-specific splicing QTLs across 49 tissues |
| MaveDB | Splice MAVE results (e.g. BRCA1 saturation; Findlay 2018 *Nature*) |

Always check ClinVar first for existing classifications; cross-reference with gnomAD for population frequency before committing to PP3/PP4.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `spliceai: tensorflow not found` | TensorFlow not installed | `pip install tensorflow>=2.0` separately |
| `spliceai: chrom not in reference` | VCF chrom name mismatch (chr1 vs 1) | `bcftools annotate --rename-chrs chr_map.txt` |
| `pangolin: no annotations found for variant` | gffutils db doesn't contain queried gene | Rebuild gffutils db with comprehensive GENCODE GFF3 |
| `mmsplice: variant outside any cassette event` | MMSplice model assumes cassette context | Use SpliceAI for non-cassette events |
| `SpliceVault: variant not found` | Variant outside common splice sites in 300K-RNA database | Use SpliceAI for prediction (no empirical baseline available) |
| `VariantValidator: invalid HGVS` | Wrong reference transcript or build | Specify NM_*.* version explicitly |

## Common Pitfalls

- **Using SpliceAI score alone for clinical reporting** — must combine with concordant predictors and ideally RNA validation; ClinGen SVI requires this for non-canonical positions.
- **50nt window for deep intronic variants** — pseudoexon-creating variants 100-2000 nt deep are systematically missed.
- **Tissue-agnostic prediction for tissue-specific genes** — use Pangolin or SpliceTransformer when tissue context matters (NEFM, MAPT, DMD isoforms).
- **Branchpoint variants** — all current predictors are weak here. Use BPHunter for branchpoint screening.
- **Forgetting NMD direction** — confirmed splice disruption needs NMD-status check. Last-exon PTCs escape NMD and can be dominant-negative or gain-of-function.
- **In-silico-only PVS1 application** — PVS1 for non-canonical positions requires functional or strong computational evidence; SpliceAI alone is supporting (PP3), not very strong.
- **Trusting LLMs for variant interpretation** — use as orchestrators on top of SpliceAI/VariantValidator/ClinVar; all clinical-grade calls require human expert sign-off.
- **Skipping HGVS validation** — invalid HGVS leads to silent reference-transcript mismatches; always run VariantValidator first.

## Quality Thresholds

| Metric | Recommendation | Source |
|--------|----------------|--------|
| Default SpliceAI window | -D 50 (clinical screening) | Jaganathan 2019 |
| Deep-intronic SpliceAI window | -D 500-2000 (unsolved Mendelian) | Convention (verify current literature) |
| ACMG PP3 (supporting) | SpliceAI delta >= 0.2 | Walker 2023 *AJHG* (apply at supporting weight) |
| ACMG BP4 (supporting) | SpliceAI delta <= 0.1 | Walker 2023 *AJHG* |
| SpliceAI higher-precision cutoffs | 0.5 / 0.8 raise precision, NOT ACMG strength | Jaganathan 2019 (not ClinGen graded tiers) |
| Off-target ASO match | <=16/20 nt to any non-target transcript | Design convention |
| Concordance for high-confidence | 2/3 predictors above PP3 threshold | Pragmatic |

## Related Skills

- splicing-qc - MaxEntScan + library QC for confirming predicted impact
- splicing-quantification - Empirical PSI from RNA-seq to validate predictions
- outlier-splicing-detection - FRASER2/DROP for RNA-seq confirmation in clinical samples
- variant-calling/clinical-interpretation - Broader ACMG/AMP variant interpretation framework
- variant-calling/variant-annotation - VEP plugin integration for SpliceAI

## References

- Jaganathan et al 2019 *Cell* - SpliceAI
- Zeng & Li 2022 *Genome Biol* - Pangolin
- Cheng et al 2019 *Genome Biol* - MMSplice
- Cheng et al 2021 *Genome Biol* - MTSplice (tissue MMSplice)
- You et al 2024 *Nat Commun* 15:9129 - SpliceTransformer
- Strauch et al 2022 *PLoS One* 17:e0269159 - CI-SpliceAI extended window
- Smith & Kitzman 2023 *Genome Biol* 24:294 - SpliceAI/Pangolin MPSA benchmark
- Rentzsch et al 2021 *Genome Med* - CADD-Splice
- Dawes et al 2023 *Nat Genet* - SpliceVault
- Walker et al 2023 *Am J Hum Genet* - ClinGen SVI splicing recommendations
- Riepe et al 2021 *Hum Mutat* 42:799 - SpliceAI in clinical pipelines (Riepe TV et al)
- Abou Tayoun et al 2018 *Hum Mutat* - PVS1 decision tree
- Richards et al 2015 *Genet Med* - ACMG/AMP framework
- den Dunnen et al 2016 *Hum Mutat* - HGVS standard
- Zhang et al 2022 *PNAS* (PMID 36306325) - BPHunter for branchpoints
- Hua et al 2008 *AJHG* - ISS-N1 / nusinersen mechanism
- Roberts et al 2023 *Nat Rev Drug Discov* 22:917-934 - DMD therapeutic approaches (exon-skipping ASOs)
- Findlay et al 2018 *Nature* - BRCA1 saturation genome editing (MAVE)
<!-- END FILE: alternative-splicing/splice-variant-prediction/SKILL.md -->

## 子目录：alternative-splicing/splicing-qc

<!-- BEGIN FILE: alternative-splicing/splicing-qc/SKILL.md -->
---
name: bio-splicing-qc
description: Assesses RNA-seq data quality specifically for alternative splicing analysis. QC layers include experimental design audit (library prep, read length, depth, replicates), STAR 2-pass cohort-style alignment, junction saturation curves and discovery plateau detection, novel-vs-known junction ratio diagnostics, junction-overhang distribution, splice-site strength scoring (MaxEntScan intrinsic + SpliceAI context-aware), strandedness verification, GENCODE basic vs comprehensive choice, and rRNA contamination screening. Splicing analysis is more demanding than DGE on read length, depth, library prep, alignment strategy, and annotation choice — failures silently bias PSI estimates and inflate novel-junction false positives. Use when evaluating data suitability for splicing analysis, troubleshooting low event detection, or designing sequencing experiments where AS is a primary endpoint.
tool_type: python
primary_tool: RSeQC
---

## Version Compatibility

Reference examples tested with: RSeQC 5.0+, STAR 2.7.11+, samtools 1.19+, pysam 0.22+, regtools 1.0+, maxentpy 0.0.1+, spliceai 1.3+, matplotlib 3.8+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Splicing-Specific Quality Control

Splicing analysis is more demanding than DGE on read length, depth, library prep, alignment strategy, and annotation choice. Failures in any of these silently bias PSI estimates and inflate novel-junction false positives. The decision sequence is: experimental design -> library prep -> alignment strategy -> annotation -> diagnostic metrics. Each layer's failure mode is distinct.

## QC Layer Taxonomy

| Layer | Target | Tool | Fails when |
|-------|--------|------|------------|
| Experimental design | Read length, depth, replicates, library type | Pre-sequencing review | <PE 75nt; n<3 vs n<3; <30M reads/sample |
| Library prep | poly(A) vs rRNA depletion | Pre-sequencing review | poly(A) library used for IR analysis |
| Alignment | STAR 2-pass cohort-style | STAR | 1-pass loses 14% novel junctions; per-sample 2-pass introduces inconsistency |
| Junction discovery | Saturation, novelty | RSeQC `junction_saturation`, `junction_annotation` | Curve still rising = under-sequenced; novel% >40% suggests biology or artifact |
| Strand specificity | Library protocol consistency | RSeQC `infer_experiment` | Wrong `--libType` halves usable junctions |
| Splice site strength | Cryptic vs canonical | MaxEntScan, SpliceAI | Weak splice sites (MaxEnt<5) may indicate cryptic, regulated, or annotation error |
| Junction overhang | Read-junction support quality | pysam CIGAR parsing | Overhang <8nt = high false-positive rate |
| Contamination | rRNA, adapters | fastq_screen | >20% rRNA in "depleted" library = failed depletion |
| Annotation | GENCODE basic vs comprehensive | Annotation choice | Basic for canonical events; comprehensive for DTU |

## Decision Tree by Question

| Question | Recommended QC |
|----------|-----------------|
| Will my planned RNA-seq design support AS analysis? | Pre-sequencing audit: library type, read length, depth, replicates |
| Is my data suitable for cassette exon analysis? | Junction saturation + known/novel ratio + read length |
| Why does my AS analysis call so few events? | Saturation curve, depth, library type, alignment 2-pass |
| Why does my AS analysis call so many novel junctions? | Annotation completeness + novel% + biology check (TDP-43, SF3B1) |
| Are my SpliceAI predictions calibrated for my tissue? | MaxEntScan + SpliceAI concordance for known sites |
| Did STAR 2-pass actually run cohort-style? | Verify SJ.out.tab merging across samples |
| Is intron retention detectable in my data? | Library type (must be rRNA-depleted); strand-specific |
| Are my microexons detectable? | Read length >=100; aligner anchor settings; consider VAST-TOOLS |

## Experimental Design Audit (Before Sequencing)

| Decision | For splicing analysis | Rationale |
|----------|------------------------|-----------|
| **Library prep** | rRNA depletion (Ribo-Zero, RiboCop) | poly(A) selection loses pre-mRNA, nascent transcripts, and detained introns; for IR analysis rRNA depletion is mandatory (convention) |
| **Read length** | PE 100-150 nt (PE 150 strongly preferred) | Junction-spanning reads need >=8 nt overhang on each exon; shorter single-end reads bias junction detection toward shorter exons (convention) |
| **Pairing** | Paired-end | Single-end loses fragment-level disambiguation of junctions |
| **Depth** | 50-100M reads/sample | DGE-grade 30M misses low-PSI events; 100M for low-abundance event discovery |
| **Strandedness** | Stranded library (Illumina TruSeq stranded) | Distinguishes overlapping antisense; some tools double-count unstranded junctions |
| **Replicates** | n>=3 per condition | n=2 vs n=2 has poor calibration in most tools (especially SUPPA2) |
| **Annotation** | GENCODE basic for canonical, comprehensive for DTU/discovery | basic = high-confidence; comprehensive includes putative — affects FDR control |
| **Microexons** | PE 100+ with `--alignSJoverhangMin 8`; VAST-TOOLS | Default aligners miss 3-27nt exons |
| **Long-intron genes (TTN, brain)** | Increased `--alignIntronMax` | Default 1Mb may miss >1Mb introns |

## STAR 2-Pass Alignment

**Goal:** Maximize novel-junction sensitivity for downstream AS analysis.

**Approach:** Run STAR once per sample to discover novel junctions (pass 1), merge novel junctions across cohort, then re-align with the augmented junction set (pass 2). Cohort-style 2-pass beats per-sample basic 2-pass for differential splicing because all samples use the same junction reference.

```bash
# Pass 1: per-sample
STAR --runMode alignReads \
    --runThreadN 8 \
    --genomeDir genome_index \
    --sjdbGTFfile gencode.v45.basic.gtf \
    --sjdbOverhang 149 \
    --readFilesIn sample_R1.fq.gz sample_R2.fq.gz \
    --readFilesCommand zcat \
    --outSAMtype BAM SortedByCoordinate \
    --outFileNamePrefix pass1_${sample}_ \
    --outSJtype Standard \
    --outFilterMultimapNmax 20 \
    --alignSJoverhangMin 8 \
    --alignSJDBoverhangMin 1
```

```bash
# Cohort-style 2-pass: collect all SJ.out.tab from pass 1
cat pass1_*_SJ.out.tab | awk '$5 > 0 && $7 >= 3' | sort -u > cohort_novel_SJ.tab

# Pass 2: re-align with augmented junctions
STAR --runMode alignReads \
    --runThreadN 8 \
    --genomeDir genome_index \
    --sjdbGTFfile gencode.v45.basic.gtf \
    --sjdbFileChrStartEnd cohort_novel_SJ.tab \
    --sjdbOverhang 149 \
    --readFilesIn sample_R1.fq.gz sample_R2.fq.gz \
    --readFilesCommand zcat \
    --outSAMtype BAM SortedByCoordinate \
    --outFileNamePrefix pass2_${sample}_ \
    --outSJtype Standard \
    --twopassMode None \
    --quantMode GeneCounts \
    --alignSJoverhangMin 8 \
    --alignSJDBoverhangMin 3
```

| Approach | Novel-junction recovery | Cohort consistency |
|----------|-------------------------|--------------------|
| 1-pass with annotation | ~80-86% (depends on GENCODE completeness) | High (annotation-based) |
| Per-sample basic 2-pass (`--twopassMode Basic`) | >=94% | Variable (each sample has its own junction set) |
| Cohort-style 2-pass (manual merge) | >=94% | High (shared junction reference) |

Per-sample 2-pass (`--twopassMode Basic`) is simpler but produces inconsistent junction sets across samples; for differential splicing the **cohort-style** version is preferred (Veeneman 2016 *Bioinformatics*).

The pass-1 filter `awk '$5 > 0 && $7 >= 3'` keeps junctions with strand info AND >=3 unique reads — adjust threshold to balance discovery vs noise.

## Junction Saturation

**Goal:** Determine whether sequencing depth is sufficient for comprehensive splicing detection.

**Approach:** Run RSeQC junction saturation; check whether the discovery curve plateaus.

```bash
junction_saturation.py \
    -i sample.bam \
    -r gencode_v45.bed \
    -o sample_junc_sat \
    -m 50
```

```python
import subprocess
import pandas as pd

samples = ['s1.bam', 's2.bam', 's3.bam']
for sample in samples:
    subprocess.run([
        'junction_saturation.py',
        '-i', sample,
        '-r', 'gencode_v45.bed',
        '-o', sample.replace('.bam', '_junc_sat')
    ], check=True)
```

The output `*.junctionSaturation_plot.r` plots known + novel junctions vs subsampled reads.

**Plateau detection rule:** if from 80% to 100% of reads, the junction count rises by <2%, consider it plateaued. Still rising means more sequencing would yield more junctions.

For AS analysis, **plateau on the known junction curve** is the requirement; novel-junction curves often don't plateau even at deep coverage (which is biologically informative — novel junctions are inherently rarer events).

## Novel-vs-Known Junction Ratio

**Goal:** Detect annotation/mapping issues or biologically interesting cryptic splicing.

**Approach:** Classify junctions with RSeQC and compute the novel:known ratio.

```bash
junction_annotation.py -i sample.bam -r gencode_v45.bed -o sample_junc_annot
```

```python
import pandas as pd

# RSeQC .junction.xls has a header: chrom, intron_st(0-based), intron_end(1-based), read_count, annotation
junc = pd.read_csv('sample_junc_annot.junction.xls', sep='\t')
total = junc['read_count'].sum()

by_class = junc.groupby('annotation')['read_count'].sum()
known_frac = by_class.get('annotated', 0) / total
novel_frac = (by_class.get('partial_novel', 0) + by_class.get('complete_novel', 0)) / total

print(f'known: {known_frac:.1%}, novel: {novel_frac:.1%}')
```

| Known fraction | Status | Interpretation |
|----------------|--------|----------------|
| >=80% | Healthy | Comprehensive annotation, good alignment |
| 60-80% | Acceptable | Check annotation completeness or organism |
| <60% | Suspect or interesting | Mapping artifacts, contamination, OR biologically informative |

**High novel-junction rate may be biology, not artifact:**
- **TDP-43 loss** (ALS/FTD post-mortem brain): cryptic exon de-repression in UNC13A, STMN2, ATG4B (Brown 2022 *Nature*; Klim 2019 *Nat Neurosci*)
- **SF3B1-mutant** cancer (MDS, CLL, uveal melanoma): cryptic 3'ss ~10-30nt upstream of canonical (Darman 2015 *Cell Rep*)
- **Non-model organism**: GENCODE-grade annotation unavailable; novel junctions reflect annotation gaps not biology
- **Microbial / viral contamination**: reads aligning to host but with unusual junctions

If novel% >40%, drill down: check organism, check spliceosomal mutation status, check known disease signatures.

## Junction Read Overhang and Coverage

**Goal:** Profile per-junction read counts and overhang distribution to identify weakly-supported events.

**Approach:** Parse CIGAR for N (intron) operations; tally per-junction reads and minimum exon overhangs.

```python
import pysam
from collections import defaultdict

def junction_stats(bam_path):
    bam = pysam.AlignmentFile(bam_path, 'rb')
    counts = defaultdict(int)
    min_overhang = defaultdict(lambda: float('inf'))

    for read in bam.fetch():
        if read.is_unmapped or read.is_secondary:
            continue
        ref_pos = read.reference_start
        cumulative_query = 0
        cigar = read.cigartuples
        for i, (op, length) in enumerate(cigar):
            if op == 3:
                left_match = sum(l for o, l in cigar[:i] if o in (0, 7, 8))
                right_match = sum(l for o, l in cigar[i+1:] if o in (0, 7, 8))
                overhang = min(left_match, right_match)
                key = (read.reference_name, ref_pos, ref_pos + length)
                counts[key] += 1
                min_overhang[key] = min(min_overhang[key], overhang)
            if op in (0, 2, 3, 7, 8):
                ref_pos += length

    bam.close()
    return counts, dict(min_overhang)

counts, overhang = junction_stats('sample.bam')
print(f'total junctions: {len(counts)}')
print(f'>= 10 reads: {sum(1 for c in counts.values() if c >= 10)}')
print(f'overhang >= 8 nt: {sum(1 for k, c in counts.items() if overhang[k] >= 8)}')
```

Junction reads with overhang <8 nt are common false positives, especially for novel sites. Most callers default to >=8 nt anchor for this reason. Microexon-aware aligners use overhang as low as 6 nt with explicit configuration.

## Splice Site Strength (MaxEntScan and SpliceAI)

**Goal:** Score donor and acceptor splice sites to flag weak / cryptic sites and to predict variant impact on splicing.

**Approach:** Use MaxEntScan (sequence information content) and SpliceAI (context-aware deep-learning) — they answer different questions.

```python
from maxentpy.maxent import score5, score3

donor = 'CAGGTAAGT'
acceptor = 'TTTTTTTTTTTTTTTTTTTTCAG'
print(f"5'ss MaxEnt: {score5(donor):.2f}")
print(f"3'ss MaxEnt: {score3(acceptor):.2f}")
```

| Score | Interpretation | Source |
|-------|----------------|--------|
| 5'ss MaxEnt > 8 | Strong donor | Yeo & Burge 2004 *J Comput Biol* |
| 5'ss MaxEnt 5-8 | Moderate | |
| 5'ss MaxEnt < 5 | Weak / cryptic | |
| 3'ss MaxEnt > 8 | Strong acceptor | |
| 3'ss MaxEnt < 5 | Weak / cryptic | |
| SpliceAI delta >= 0.2 | PP3 (applied at supporting weight); BP4 at <= 0.1 | Walker 2023 *AJHG* (ClinGen SVI 2023) |
| SpliceAI delta 0.5 / 0.8 | Higher-precision cutoffs (SpliceAI recommended/high-precision tiers) | Jaganathan 2019 *Cell* — NOT ClinGen graded evidence-strength upgrades |

**MaxEntScan vs SpliceAI:**
- **MaxEntScan** scores sequence information content (intrinsic strength). Captures position-wise dependencies at the consensus.
- **SpliceAI** predicts in-vivo usage probability given full pre-mRNA context (10 kb window).
- A position with **high MaxEnt but low SpliceAI** is intrinsically strong but contextually silenced (chromatin, trans factors).
- A position with **low MaxEnt but high SpliceAI** is intrinsically weak but contextually used (enhancer-driven, e.g. weak donors stabilized by ESEs).
- Report both for variant interpretation; for variant impact see `splice-variant-prediction`.

## Picard CollectRnaSeqMetrics and Gene-Body Coverage

**Goal:** Get integrated RNA-seq QC including intronic / exonic / intergenic mapping rates and gene-body coverage uniformity.

**Approach:** Run picard CollectRnaSeqMetrics for mapping distribution; RSeQC `geneBody_coverage.py` for 5'-3' bias.

```bash
picard CollectRnaSeqMetrics \
    I=sample.bam \
    O=sample.rna_metrics.txt \
    REF_FLAT=refFlat.txt \
    STRAND_SPECIFICITY=SECOND_READ_TRANSCRIPTION_STRAND \
    RIBOSOMAL_INTERVALS=rRNA_intervals.interval_list

# Strandedness conversion (foot-gun):
# Reverse-stranded (Illumina TruSeq Stranded; NEB Ultra II Directional — both dUTP):
#   rMATS  --libType fr-firststrand
#   featureCounts -s 2
#   Picard STRAND_SPECIFICITY=SECOND_READ_TRANSCRIPTION_STRAND
# Forward-stranded (Lexogen QuantSeq FWD, certain ligation-based kits):
#   rMATS  --libType fr-secondstrand
#   featureCounts -s 1
#   Picard STRAND_SPECIFICITY=FIRST_READ_TRANSCRIPTION_STRAND
# STAR has no library-strand flag; pass --outSAMstrandField intronMotif
# (works for any library) so downstream tools can read XS tags.

geneBody_coverage.py \
    -i sample.bam \
    -r gencode_v45.bed \
    -o sample_geneBody
```

| Metric | Healthy | Concerning |
|--------|---------|------------|
| PCT_CODING_BASES | >=50% | <30% (suggests degradation or mis-priming) |
| PCT_UTR_BASES | 20-40% | >>50% (3' bias) |
| PCT_INTRONIC_BASES | <30% (poly(A)); <60% (rRNA-depleted) | >50% (poly(A)) suggests pre-mRNA contamination |
| PCT_INTERGENIC_BASES | <10% | >20% (genomic DNA contamination) |
| MEDIAN_5PRIME_TO_3PRIME_BIAS | 0.7-1.3 | >2 or <0.5 (severe degradation) |
| Gene body coverage curve | Flat | Strong 3' skew = RIN low or library mis-prep |

3' bias (degraded RNA) directly reduces splicing-event detection because junction reads scatter across the gene body; with 3' bias they concentrate near the 3' end and miss CDS junctions.

## Strandedness Verification

```bash
infer_experiment.py -i sample.bam -r gencode_v45.bed -s 200000
```

Output reports the fraction of reads consistent with each library type:

| Output pattern | Library type | rMATS `--libType` |
|----------------|---------------|---------------------|
| ~50% / ~50% | Unstranded | `fr-unstranded` |
| >=90% "++ , --" | Forward-stranded | `fr-secondstrand` |
| >=90% "+- , -+" | Reverse-stranded (Illumina TruSeq stranded) | `fr-firststrand` |

**Wrong strand setting halves usable junction reads** — always verify before quantification. RSeQC `infer_experiment.py` is fast and authoritative.

## Annotation Choice

| GENCODE level | Contents | Use for |
|---------------|----------|---------|
| Basic | High-confidence canonical isoforms | Standard rMATS, leafcutter, SUPPA2 |
| Comprehensive | All transcripts including putative/predicted | DTU pipelines (DRIMSeq+DEXSeq, satuRn), isoform discovery |
| RefSeq | NCBI curated | Less complete than GENCODE; legacy use |
| Ensembl | Same content as GENCODE in vertebrates | Different attribute conventions |

Comprehensive captures more biology but inflates DTU multiple-testing burden and includes annotation noise. For event-level (rMATS) AS, basic is usually adequate; for transcript-level DTU (DRIMSeq, satuRn), comprehensive may be necessary to capture rare isoforms.

## rRNA Contamination Check

```bash
fastq_screen --conf fastq_screen.conf --threads 8 sample_R1.fq.gz
```

Or post-alignment:

```bash
samtools view -c sample.bam | awk '{print "total:",$0}'
samtools view -c -L rRNA_intervals.bed sample.bam | awk '{print "rRNA:",$0}'
```

| rRNA fraction | Library type | Status |
|----------------|---------------|--------|
| >=20% | "depleted" | Failed depletion; redo |
| 5-20% | "depleted" | Acceptable; some rRNA leakage |
| <5% | poly(A) | Healthy |
| <5% | "depleted" | Excellent depletion |
| 1-3% | poly(A) | Suggests RNA degradation |

>5% rRNA in a poly(A) library suggests degraded RNA; >20% in a "depleted" library indicates failed depletion.

## Per-Tool Failure Modes

### RSeQC `junction_saturation`: Subsampling Behavior

**Trigger:** Running on extremely deep BAM (>200M reads).

**Mechanism:** RSeQC subsamples at 5%, 10%, ..., 100%; with very deep BAMs, the early subsamples are still tens of millions of reads, masking saturation behavior.

**Symptom:** Curve appears flat throughout; uninformative.

**Fix:** Subsample BAM with `samtools view -s 0.1` before running junction_saturation; or use `-s` flag to set custom step intervals.

### STAR 2-Pass: Per-Sample Inconsistency

**Trigger:** Using `--twopassMode Basic` on differential splicing cohorts.

**Mechanism:** Per-sample 2-pass means each sample has its own SJ.out.tab; samples may differ in which novel junctions they re-align against.

**Symptom:** Inconsistent novel junction calls across replicates; rMATS `--novelSS` differential calls don't replicate.

**Fix:** Switch to cohort-style 2-pass (collect all pass-1 SJ.out.tabs, merge, re-align all samples with merged set).

### MaxEntScan: Out-of-Range Sequences

**Trigger:** Sequences with N bases or wrong length.

**Mechanism:** `score5` expects exactly 9 nt (3 exon + 6 intron); `score3` expects 23 nt (20 intron + 3 exon).

**Symptom:** ValueError or silently incorrect score.

**Fix:** Pre-validate sequence length and N-content; use a wrapper that returns NaN for invalid inputs.

### SpliceAI: TensorFlow Memory

**Trigger:** Running spliceai on large VCF without GPU.

**Mechanism:** TensorFlow CPU mode is slow; default batch size may exceed memory.

**Symptom:** OOM kill; very slow runtime (hours per chromosome).

**Fix:** Use `-D 50` for screening (fastest); split VCF by chromosome; use GPU when available.

### `infer_experiment.py`: Sample Size

**Trigger:** Running on very low-coverage region or small subsample (-s).

**Mechanism:** Default sample size is 200,000 reads; with low coverage, this isn't met.

**Symptom:** "0 of 200000 reads" output; cannot infer strand.

**Fix:** Lower `-s` to actual available reads; or use `-q 30` to filter by quality.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `STAR: SJDBoverhang differs from genome` | Index built with different overhang than current run | Rebuild index with `--sjdbOverhang` matching read length - 1 |
| `RSeQC: BED format error` | Annotation BED has wrong column order | Convert with `awk` or `bedtools` |
| `MaxEntScan: invalid sequence character N` | N in input | Filter or replace; document |
| `samtools view: missing index` | BAM not indexed | `samtools index sample.bam` |
| `STAR: too many SJs in cohort merge` | Cohort SJ.out.tab too large after merge | Filter to junctions in >=3 samples or with >=3 unique reads |
| `regtools: invalid CIGAR` | Non-spec read in BAM | Filter with `samtools view -h -F 0x100 -F 0x800` |

## Quality Thresholds

| Metric | Good | Acceptable | Poor | Source |
|--------|------|------------|------|--------|
| Read length (PE) | 150 nt | 100 nt | <75 nt | convention |
| Sequencing depth | >=100M | 50-100M | <30M | DGE-grade insufficient |
| Junction saturation | Plateau (<2% growth in last 20%) | Near plateau | Still rising | RSeQC convention |
| Known-junction fraction | >=80% | 60-80% | <60% (suspect or interesting) | RSeQC convention |
| Junctions >=10 reads | >=50% | 30-50% | <30% | rMATS reliability cutoff |
| 5'ss / 3'ss MaxEnt | >8 | 5-8 | <5 | Yeo & Burge 2004 |
| Strandedness | >90% one direction | 70-90% | <70% | RSeQC convention |
| rRNA in depleted library | <5% | 5-20% | >20% | convention |
| 2-pass STAR | Cohort-style | Per-sample basic | 1-pass only | Veeneman 2016 *Bioinformatics* |

## Troubleshooting Low Event Detection

| Issue | Possible causes | Solutions |
|-------|-----------------|-----------|
| Few events called | Low depth; short reads; SE; wrong strand | Increase depth; use PE150; verify libType |
| High novel junctions | Annotation gaps; mapping artifacts; biology (TDP-43, SF3B1) | Update annotation; check 2-pass; consider biology |
| Low IR detection | poly(A) library | Use rRNA depletion |
| Microexons missing | Default aligner anchors too long | VAST-TOOLS, MicroExonator, or long-read |
| Many weak splice sites | Cryptic splicing | Validate with MaxEnt + SpliceAI; consider RNA-seq from secondary tissue |
| FDR uncalibrated at low n | n=2 vs n=2 | Use leafcutter or Shiba; avoid SUPPA2 alone |
| PSI variance high across replicates | Library prep / RIN inconsistency | Check RIN; consider RNA degradation |
| Sashimi plot mismatch with PSI | Junction-imbalance bias in rMATS | Run Shiba; or filter by overhang distribution |

## Common Pitfalls

- **Skipping STAR 2-pass** — loses ~14% of novel junctions; matters for any non-canonical organism or condition.
- **Per-sample 2-pass instead of cohort-style** — produces inconsistent junction sets; differential splicing calls don't replicate.
- **poly(A) library for IR analysis** — biases toward mature transcripts; depletes pre-mRNA / nascent / detained intron signal.
- **PE 50nt single-end** — junction-spanning reads need >=8nt overhang on both sides; biases toward shorter exons.
- **Wrong `--libType`** — halves usable junctions; always verify with `infer_experiment.py`.
- **Using basic GENCODE for DTU** — basic excludes putative/rare isoforms; DTU pipelines may underdetect.
- **Using MaxEntScan alone for variant interpretation** — misses context-dependent regulation; pair with SpliceAI.
- **Treating high novel% as artifact reflexively** — could be biology (TDP-43, SF3B1, non-model organism); investigate.

## Related Skills

- splicing-quantification - PSI estimation after QC passes
- read-alignment/star-alignment - STAR 2-pass detail and parameter tuning
- read-qc/quality-reports - General sequencing QC (FastQC, MultiQC)
- read-qc/contamination-screening - rRNA / adapter / cross-species contamination
- splice-variant-prediction - SpliceAI / Pangolin for variant impact
- long-read-splicing - When short-read QC is fundamentally limiting (microexons, complex isoforms)
- differential-splicing - Downstream tool that requires QC pass

## References

- Yeo & Burge 2004 *J Comput Biol* - MaxEntScan
- Jaganathan et al 2019 *Cell* - SpliceAI
- Walker et al 2023 *Am J Hum Genet* - ClinGen SVI splicing thresholds
- Veeneman et al 2016 *Bioinformatics* - STAR 2-pass benchmark
- Brown et al 2022 *Nature* - cryptic exons in TDP-43 loss
- Klim et al 2019 *Nat Neurosci* - STMN2 cryptic splicing in ALS
- Darman et al 2015 *Cell Rep* - SF3B1 cryptic 3'ss
- Wang et al 2024 *Nat Protoc* - rMATS-turbo
- Dobin et al 2013 *Bioinformatics* - STAR aligner
<!-- END FILE: alternative-splicing/splicing-qc/SKILL.md -->

## 子目录：alternative-splicing/splicing-quantification

<!-- BEGIN FILE: alternative-splicing/splicing-quantification/SKILL.md -->
---
name: bio-splicing-quantification
description: Quantifies alternative splicing as PSI (percent spliced in) from RNA-seq using rMATS-turbo (BAM-based event), SUPPA2 (TPM-based event), MAJIQ V3 (LSV-based Bayesian), leafcutter (annotation-free intron clusters), VAST-TOOLS (cross-species with microexon support), Shiba (junction-imbalance-corrected, 2025 SOTA at low coverage), or IRFinder-S (intron retention coverage-aware). Distinguishes the five canonical event classes (SE, A5SS, A3SS, MXE, RI), special classes (microexons, exitrons, AFE/ALE), intron retention subtypes (canonical RI vs detained introns), and applies effective-length normalization. Use when measuring splice-site usage or isoform inclusion ratios from short-read RNA-seq.
tool_type: mixed
primary_tool: rMATS-turbo
---

## Version Compatibility

Reference examples tested with: rMATS-turbo 4.3+, SUPPA2 2.4+, leafcutter 0.2.9+, MAJIQ 3.0+, IRFinder-S 2.0+, kallisto 0.50+, Salmon 1.10+, pandas 2.2+, STAR 2.7.11+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Splicing Quantification

Quantify alternative splicing events as PSI (percent spliced in) from RNA-seq. PSI = inclusion read evidence / (inclusion + skipping read evidence), normalized for differential mapping opportunity between isoforms. The choice of *quantification unit* (event, intron cluster, LSV, transcript) determines which biological questions can be answered and which failure modes apply.

## Algorithmic Taxonomy

| Family | Unit | Reference tools | Fails when |
|--------|------|-----------------|------------|
| Event-based | Pre-defined SE/A5SS/A3SS/MXE/RI events from annotation | rMATS-turbo, SUPPA2, VAST-TOOLS | Event isn't in annotation; complex multi-junction events split arbitrarily; AFE/ALE confounded with splicing |
| LSV-based | Local Splice Variations at single source/target nodes | MAJIQ V3 | Memory-constrained environments; cohorts smaller than ~3 reps; non-academic users (license) |
| Junction-cluster | Annotation-free intron clusters by shared splice sites | leafcutter, leafcutter2 | Undersampled clusters lose power; topology biologically uninterpretable for novel events |
| Splice-graph | Graph nodes (non-overlapping exonic regions) | Whippet, Shiba | Whippet maintenance status uncertain since ~2022; complex multi-exon graphs |
| Coverage-aware (IR) | Intron body coverage + flanking junctions | IRFinder-S, S-IRFindeR, iREAD | Confounded by overlapping exons, repeats, low mappability regions |
| Isoform-based | Transcript abundance via EM | Salmon/kallisto + tximport | Salmon EM uncertainty propagates; many similar isoforms (TTN, MAPT) become indistinguishable |

The agent's first decision is **which family** the question requires, not which tool. Switching family is the response to a tool failing within a family — switching tool within a family rarely fixes systematic blind spots.

## Event Taxonomy (Beyond Standard SE/A5SS/A3SS/MXE/RI)

| Class | Code | Biology | Detection caveat |
|-------|------|---------|-------------------|
| Skipped exon (cassette) | SE | Default cassette-exon AS | Most common; well-handled by all tools |
| Alternative 5' splice site | A5SS | Alternative donor; intron 5' end varies | Sign convention tool-specific (see below) |
| Alternative 3' splice site | A3SS | Alternative acceptor; intron 3' end varies | Sensitive to BPS cancer mutations (SF3B1) — cryptic 3'ss ~10-30nt upstream |
| Mutually exclusive exons | MXE | Two exons paired, one included | Tool implementations vary; verify which "form 1" is yours |
| Retained intron | RI | Whole intron retained in mature mRNA | Junction-only quant systematically underdetects; needs IRFinder-S |
| **Microexon** | (sub-SE) | 3-27 nt; neural-enriched, SRRM4-regulated | Missed by default aligner anchor lengths (>=20-30 nt); needs VAST-TOOLS, MicroExonator, or long-read |
| **Exitron** | n/a | Intronic region within an annotated CDS exon | Mis-classified as A5SS/A3SS by most tools; use ExitronFinder, ScanExitron |
| **Alternative first exon (AFE)** | AFE | Alternative TSS / promoter use | Promoter-driven, NOT spliceosomal; confirm with FANTOM CAGE before reporting as splicing |
| **Alternative last exon (ALE)** | ALE | Alternative cleavage/polyadenylation | APA-driven, NOT spliceosomal; confirm with 3'-end-seq |
| **Detained intron (DI)** | (RI subtype) | Nuclear-retained on mature mRNA, regulated by Clk kinases | Distinct from cytoplasmic NMD-targeted RI (Boutz 2015 *Genes Dev*); requires fractionation to confirm |
| **Recursive splicing** | (intron subtype) | Long introns >50kb spliced via internal ratchet points | Sibley 2015 *Nature*; only detectable with long-read or nascent RNA-seq |

Tool-agnostic taxonomy reference: Wang 2008 *Nature*; Vaquero-Garcia 2016 *eLife* (LSV); Tapial 2017 *Genome Res* (VastDB).

## Tool Selection Matrix

| Tool | Best for | Input | Strengths | Fails when |
|------|----------|-------|-----------|------------|
| rMATS-turbo | Standard SE/A5SS/A3SS/MXE/RI in annotated organism, n>=3 | BAM + GTF | Fast, well-calibrated at n>=3, novel SS support | Junction read imbalance; novel multi-junction events; underdetects RI and microexons |
| SUPPA2 | Quick PSI from existing TPM, pilot analysis | Salmon/kallisto TPM + GTF | No alignment; fastest | Annotation-bound; high FDR (15-30%) at n<=2 vs n<=2 |
| MAJIQ V3 | Complex events, heterogeneous cohorts (HET) | BAM + GFF3 | Bayesian posterior PSI, complete LSV semantics | High memory (~50+ GB on cohorts); academic license; complex LSV interpretation needs care |
| leafcutter | Novel junction discovery, sQTL, low-memory environments | BAM (regtools junctions) | Annotation-free; ~400 MB memory; SOTA for unannotated organisms | Sensitive to read depth; cluster topology arbitrary for complex multi-junction events |
| Shiba (2025) | Low-coverage / few-replicate designs; junction imbalance correction | BAM + GTF | Best calibration in own benchmark at n=2 vs n=2 | New (2025); limited community calibration |
| VAST-TOOLS | Cross-species comparative AS, microexons | FASTQ | VastDB orthology, ExOrthist co-tool | Limited to species in VastDB |
| Whippet | Laptop-scale exploratory | FASTQ | Fast splice-graph-based PSI | Reduced active development since ~2022; underperforms on complex topologies |
| IRFinder-S | Intron retention specifically | FASTQ | Coverage + junction integration; CNN-based artifact filtering | IR-only; not for cassette events |
| S-IRFindeR | Replicate-stable IR ratio | BAM | Stable IR ratio metric | IR-only; less integrated than IRFinder-S |

Methodology evolves; verify benchmarks (Olofsson 2023 *Biochem Biophys Res Commun*; Kubota 2025 *NAR*; Tran 2025 *WIREs RNA*) and tool docs before committing. Default 2026 recommendation: run rMATS-turbo + leafcutter and reconcile; add MAJIQ V3 for complex events / heterogeneous cohorts; switch to Shiba for n=2 vs n=2.

## PSI Definition and Effective Length Normalization

For a cassette exon, naive PSI ignores that the inclusion isoform contains more positions where a junction read can map than the skipping isoform. rMATS reports `IncFormLen` (= 2*(read_length - anchor) for the two flanking junctions, plus exon body bases) and `SkipFormLen` (= read_length - anchor) and computes:

```
PSI = (IJC / IncFormLen) / (IJC / IncFormLen + SJC / SkipFormLen)
```

where IJC = inclusion junction counts, SJC = skipping junction counts. **Skipping this normalization biases PSI by ~10-30% depending on read length and exon size.** SUPPA2 derives PSI from transcript TPMs, which the upstream Salmon/kallisto already accounts for. leafcutter operates on intron usage proportions within a cluster (a different statistic).

For long-read data, every read carries full isoform identity — effective-length normalization becomes unnecessary because each read counts as one isoform.

## Sign Conventions for Alternative Splice Sites

| Tool | A5SS interpretation | A3SS interpretation | "Inclusion" direction |
|------|----------------------|----------------------|------------------------|
| rMATS | "long" form = donor downstream of alternative donor | "long" form = acceptor upstream of alternative acceptor | PSI > 0 = more long form |
| SUPPA2 | Same as rMATS (long = inclusion of additional exon body) | Same | PSI > 0 = more long form |
| VAST-TOOLS | Encoded in event ID (`_D1` vs `_D2`) | Encoded in event ID (`_A1` vs `_A2`) | Document the chosen reference |
| MAJIQ | Per-junction within LSV; explicit donor/acceptor naming in VOILA | Same | PSI per junction in the LSV |

Always record which alternative form ΔPSI > 0 corresponds to in publication-grade reporting. Confusion is the most common reviewer comment for AS papers.

## rMATS-turbo Workflow

**Goal:** Quantify SE/A5SS/A3SS/MXE/RI events from BAMs aligned with STAR 2-pass.

**Approach:** Group BAMs by condition, run rMATS with `--statoff` for quantification only, then parse JC.txt files for per-replicate PSI.

```bash
rmats.py \
    --b1 condition1_bams.txt \
    --b2 condition2_bams.txt \
    --gtf annotation.gtf \
    -t paired \
    --readLength 150 \
    --variable-read-length \
    --libType fr-firststrand \
    --nthread 8 \
    --od rmats_output \
    --tmp rmats_tmp \
    --novelSS \
    --statoff
```

Key flags: `--novelSS` discovers junctions absent from the GTF (recommended with STAR 2-pass output). `--variable-read-length` allows mixed read lengths in the cohort. `--libType fr-firststrand` matches Illumina TruSeq stranded; verify with RSeQC `infer_experiment.py`. `--statoff` is for quantification-only runs; omit for differential testing.

```python
import pandas as pd

se_jc = pd.read_csv('rmats_output/SE.MATS.JC.txt', sep='\t')

inc_cols = [c for c in se_jc.columns if c.startswith('IncLevel')]
se_jc['mean_PSI'] = se_jc[inc_cols].mean(axis=1)

per_rep_inc = se_jc['IJC_SAMPLE_1'].str.split(',').apply(lambda x: list(map(int, x)))
per_rep_skip = se_jc['SJC_SAMPLE_1'].str.split(',').apply(lambda x: list(map(int, x)))
min_inc = per_rep_inc.apply(min)
min_skip = per_rep_skip.apply(min)

reliable = se_jc[(min_inc + min_skip) >= 20]
```

### JC vs JCEC files

`SE.MATS.JC.txt` uses **only junction-spanning reads**. `SE.MATS.JCEC.txt` adds **reads contained within the alternative exon body** as inclusion evidence.

- Prefer **JC** for clean cassette-exon analysis when reads spanning junctions are sufficient.
- Use **JCEC** when alternative exons are short (<50nt) and junction-spanning reads are scarce.
- Avoid **JCEC** when intron retention overlaps the alternative exon body — exon-body reads may come from retained introns, not inclusion isoform.

## SUPPA2 Workflow

**Goal:** Compute event PSI from transcript TPM without alignment; useful when Salmon/kallisto TPMs already exist.

**Approach:** Generate IOE event definitions from GTF, then aggregate TPMs of transcripts including/excluding each event.

```bash
suppa.py generateEvents -i annotation.gtf -o events -f ioe -e SE SS MX RI FL

# -e takes {SE,SS,MX,RI,FL}; SS emits A5+A3 files, FL emits AF+AL files
for ev in SE A5 A3 MX RI AF AL; do
    suppa.py psiPerEvent -i events_${ev}_strict.ioe -e transcript_tpm.tsv -o psi_${ev}
done
```

SUPPA2 is annotation-bound: events absent from the GTF cannot be quantified. Whether an event is detected depends entirely on which transcripts the upstream Salmon/kallisto index contains. Use GENCODE comprehensive over basic when SUPPA2 detection sensitivity matters.

## MAJIQ V3 Workflow

**Goal:** Quantify LSVs with Bayesian posterior PSI distributions; ideal for complex multi-junction events that don't fit canonical event types.

**Approach:** Build a splice graph from BAMs + GFF3, compute per-junction coverage with bootstrap, then run `majiq psi` for posterior PSI per LSV.

```bash
majiq build annotation.gff3 -c settings.ini -j 8 -o build_output
majiq psi build_output/sample1.majiq build_output/sample2.majiq -j 4 -o psi_output -n condition_psi
voila view -p 5000 -j 8 build_output/splicegraph.zarr psi_output/condition_psi.psi.voila -o voila_output
```

MAJIQ V3 (Aicher, Slaff, Jewell, Barash *bioRxiv* 2024; public release 2025) replaced V2's SQLite splicegraph (`splicegraph.sql`) with **Zarr storage** (`splicegraph.zarr`); the `.sql` is deprecated. V3 is substantially faster than V2 via a rewritten xarray/zarr implementation with parallelized coverage calculations. LSV output includes posterior mean PSI plus the full posterior distribution; this enables threshold-based testing (e.g. P(|ΔPSI| > 0.2)) rather than frequentist p-values.

## leafcutter Junction Quantification

**Goal:** Detect junctions and intron clusters annotation-free for downstream cluster-level usage.

**Approach:** Extract junctions per BAM with regtools, write filenames into a list, then cluster introns sharing splice sites.

```bash
for bam in *.bam; do
    regtools junctions extract -a 8 -m 50 -s XS "$bam" -o "${bam%.bam}.junc"
done
ls *.junc > juncfiles.txt

python leafcutter_cluster_regtools.py \
    -j juncfiles.txt \
    -o leafcutter \
    -m 50 \
    -l 500000
```

`-a 8` = 8nt anchor minimum (raise to 12 for stricter; lower to 6 for microexon-friendly). `-m 50` = minimum junction reads per cluster. `-l 500000` = max intron length (relevant for long brain-gene introns; raise for genes like DSCAM, ROBO2, ANK3).

## Per-Tool Failure Modes

### rMATS-turbo: Junction Read Imbalance

**Trigger:** A cassette exon's flanking exons have unequal read mapping opportunity (very short upstream exon, repeat-overlapping flanks, or low-mappability regions).

**Mechanism:** rMATS' binomial model treats inclusion vs skipping junctions as having equal mappability. When mappability differs between the two junction types, the PSI estimate is biased.

**Symptom:** "Significant" rMATS calls with no concordant change in leafcutter or MAJIQ at the same locus; ΔPSI direction inconsistent with sashimi-plot intuition.

**Fix:** Run Shiba (Kubota 2025 *NAR*) which corrects junction-imbalance, or filter rMATS hits requiring concordant detection in leafcutter.

### SUPPA2: Sparse Empirical Null at Low Replicate Count

**Trigger:** n=2 vs n=2 (or n=3 vs n=2) design with `--method empirical`.

**Mechanism:** SUPPA2's empirical null is constructed from between-replicate ΔPSI distributions binned by transcript expression. With few replicates, the binned null is sparse and conservative-looking but actually under-calibrated.

**Symptom:** Inflated FDR (15-30% in benchmarks); many "significant" hits don't replicate or validate.

**Fix:** Switch to leafcutter or Shiba for n<=3 designs; or use `--method classical` (Wilcoxon) for very low replicate count; reconcile against orthogonal tool.

### MAJIQ V3: Complex LSV Interpretation

**Trigger:** A gene with 4+ alternative splice sites at one node (e.g. one source, multiple acceptors).

**Mechanism:** A complete LSV at a single node lists all observed junctions; PSI is per-junction within the LSV, not "PSI of one event."

**Symptom:** Reporting "PSI of the gene" doesn't make sense; per-junction PSIs sum to 1 across the LSV but no single number represents the gene.

**Fix:** Use VOILA to visualize the LSV graph and identify which junction(s) shifted; for cassette-style reporting, derive equivalent PSI from sum of inclusion-junctions / total junctions in the LSV.

### leafcutter: Cluster Topology Arbitrariness

**Trigger:** A cluster has 4+ introns sharing splice sites with non-canonical topology (e.g. mixed cassette + alternative donor + IR).

**Mechanism:** leafcutter clusters introns by shared splice sites; complex topologies don't map onto SE/A5SS/A3SS taxonomy and cluster-level "ΔPSI" hides which intron drove the change.

**Symptom:** Significant cluster-level p-value but multiple introns showing different effect-size directions.

**Fix:** Inspect the cluster in leafviz; report per-intron effect sizes (`effect_sizes.txt`); for canonical event reporting, map to SE/A5SS/A3SS via flanking exon coordinates manually.

## Reconciliation: When rMATS and leafcutter Disagree

The two most common short-read tools answer slightly different questions: rMATS classifies on annotated event templates; leafcutter classifies on observed cluster usage. Disagreement is informative.

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| rMATS sig, leafcutter not sig | rMATS junction read imbalance OR rMATS event hits an annotation that leafcutter clustered differently | Inspect locus in IGV; check Shiba |
| leafcutter sig, rMATS not sig | Novel junction not in rMATS annotation; rMATS `--novelSS` may have missed it | Check `--novelSS` was on; rerun if not |
| Both sig, opposite ΔPSI direction | Event class mismatch (e.g. rMATS calls SE positive but leafcutter sees A5SS shift in same cluster) | Manually map cluster topology to event class |
| Both sig, same direction | High-confidence call | Report; cross-validate with sashimi-plot |

**Operational rule:** for high-confidence reporting, require concordant detection in two tools from different algorithmic families (event-based + cluster-based, or LSV + isoform-based).

## Intron Retention: Canonical vs Detained vs Co-Transcriptional Unspliced

Three biologically distinct states all called "IR" by generic tools:

1. **Canonical RI (cytoplasmic, NMD-substrate often)**: mature polyadenylated mRNA carries the intron; usually PTC-bearing and NMD-targeted, sometimes encoding an alternative protein.
2. **Detained intron (DI)** (Boutz 2015 *Genes Dev*): nuclear-localized, mature transcripts retaining a specific intron; a regulated reservoir released into translation upon signaling.
3. **Co-transcriptional unspliced**: nascent pre-mRNA captured before splicing complete; not a regulated state.

**Library prep determines which state(s) are visible:**
- Poly(A) selection: enriches (1), depletes (2)/(3)
- rRNA depletion (cytoplasmic): captures (1)
- rRNA depletion (whole cell or nuclear): captures all three

**To distinguish DI from canonical RI:** subcellular fractionation (nuclear vs cytoplasmic RNA-seq), or NMD inhibitor (cycloheximide, NMDi-14) treatment — canonical RI mRNA increases under NMD inhibition; DI does not.

```bash
IRFinder FastQ -r REF/ -d ir_output sample.fastq
```

IRFinder-S (Lorenzi 2021 *Genome Biol*) uses CNN-based filtering of true IR vs noise; current SOTA for IR analysis. iREAD and S-IRFindeR (Broseus & Ritchie 2020 *bioRxiv*) are alternatives.

## Microexon Detection

Microexons (3-27 nt, neural-enriched, SRRM4-regulated; Irimia 2014 *Cell*) are missed by default short-read aligners requiring 20-30 nt anchors. Options:

| Approach | Tool | Notes |
|----------|------|-------|
| Curated database lookup | VAST-TOOLS + VastDB | Cross-species, microexon-aware (Tapial 2017 *Genome Res*) |
| De novo discovery | MicroExonator (Parada 2021 *Genome Biol*) | Snakemake pipeline |
| Tune the upstream aligner | `STAR --alignSJoverhangMin 6 --alignSJDBoverhangMin 1 --outFilterMismatchNoverReadLmax 0.04` | rMATS itself cannot recover microexons that STAR didn't pass through; lower DB-junction overhang to 1 (trusts annotated microexon coords) and combine with strict mismatch filter. Typical AS pipelines use STAR 8/3 which is too strict for microexons |
| Long-read sequencing | PacBio Iso-Seq, ONT | Solves the problem entirely; reads span microexons fully |

For brain / neural tissue or autism-spectrum studies, **microexon analysis must be explicit** — default short-read pipelines underdetect them by ~70%.

## Quality Thresholds

| Metric | Threshold | Source / Rationale |
|--------|-----------|---------------------|
| Junction reads per replicate | >=10-20 (per-replicate minimum) | Empirical PSI variance becomes <0.05 above this; below, PSI becomes a coin flip |
| PSI dynamic range | mean PSI 0.05-0.95 | Outside is near-constitutive; rMATS, SUPPA2 default filters drop these |
| Missing values | <50% of samples | Higher missingness indicates low expression — re-test with subset |
| Read length | >=75nt PE preferred; >=100nt for microexons | Shorter single-end reads bias junction detection toward shorter exons (convention) |
| Library | rRNA depletion for IR analysis; poly(A) acceptable for cassette | poly(A) selection loses pre-mRNA/intronic signal (convention) |
| STAR 2-pass | Cohort-style preferred over per-sample basic | Veeneman 2016 *Bioinformatics*: >=94% novel junction recovery |
| MAJIQ minreads / minpos | --minreads 10 --minpos 3 | Default; lower for low-coverage |
| leafcutter -m | 50 reads per cluster | Higher for rare events; lower for sQTL discovery |
| Anchor length | >=8 nt for short-read | Below this, false-positive junctions dominate (CIGAR-N noise) |

## Decision Tree by Scenario

| Scenario | Recommended tool(s) | Why |
|----------|----------------------|-----|
| Standard cassette analysis, n>=3, GENCODE-annotated | rMATS-turbo + leafcutter (concordance) | Default workflow; complementary algorithmic families |
| Non-model organism, no GENCODE-grade annotation | leafcutter + de novo discovery | Annotation-free |
| Heterogeneous cohort, n>=10 vs n>=10 (clinical, GTEx-style) | MAJIQ V3 with HET module | HET designed for between-sample variability dominance |
| Low coverage / few replicates (n=2 vs n=2) | Shiba | Junction-imbalance correction; SOTA at low coverage in 2025 benchmarks |
| Cross-species comparative (vertebrate panel) | VAST-TOOLS + VastDB | Orthology-aware events; ExOrthist co-tool |
| TPM-only available (no BAMs) | SUPPA2 | Annotation-bound but fast |
| Microexon focus (neural / ASD) | VAST-TOOLS or MicroExonator | Default tools systematically miss microexons |
| Intron retention focus | IRFinder-S (rRNA-depleted library) | Coverage-aware; CNN artifact filter |
| Detained introns specifically | IRFinder-S + nuclear/cytoplasmic fractionation | Required to separate DI from cytoplasmic RI |
| Long reads available | rMATS-long, FLAIR, IsoQuant | Full-isoform resolution; see long-read-splicing |
| Single-cell (full-length plate) | MARVEL, BRIE2 | See single-cell-splicing |
| Single-cell (10X 3') | Likely don't attempt; consider Sierra for APA | 10X 3' chemistry insufficient for AS |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `error: GTF gene_id parsing` (rMATS) | rMATS expects GENCODE-style gene_id; some Ensembl GTFs use different attribute order | `gffread input.gff3 -T -o standardized.gtf` |
| `KeyError: 'IJC_SAMPLE_1'` (rMATS parsing) | Output column missing; sometimes occurs when --statoff combined with novel events on older versions | Update rMATS-turbo to >=4.3.x; re-run |
| `MAJIQ: too few reads at junction` | Default `--minreads 10 --minpos 3` filters out the locus | Lower thresholds for low-coverage data; document filtering |
| `leafcutter: dispersion estimation failed` | Cluster has all-zero counts in one group | Pre-filter with leafcutter_ds.R `--min_samples_per_group 3 --min_samples_per_intron 5` |
| `SUPPA2: empirical p computed on N=4 nulls` | Insufficient replicates for empirical mode | Switch `--method classical` (Wilcoxon) for very low replicate count |
| `regtools: invalid CIGAR` | Non-BAM-spec read in input | Filter with `samtools view -h -F 0x100 -F 0x800` (drop secondary/supplementary) |
| `STAR: too many SJs` (in pass 2) | Cohort SJ.out.tab too large | Filter to junctions seen in >=3 samples or with >=3 unique reads before merging |

## Output Interpretation

PSI ranges 0 to 1: 1 = always included, 0 = always skipped, 0.5 = balanced. Sign of `IncLevelDifference` matches `--b1 minus --b2` group order — always document which is which in publications.

**NMD direction matters:** an increase in PSI of a poison exon (PTC-introducing) **decreases** functional protein due to NMD. Always check whether the alternative form is PTC-bearing using ORF-aware annotation (IsoformSwitchAnalyzeR consequences, or manual stop-codon distance check vs last exon-exon junction).

**Disease signatures:**
- **SF3B1** mutations (MDS, CLL, uveal melanoma): cryptic 3'ss ~10-30 nt upstream of canonical (Darman 2015 *Cell Rep*). Look for clustered A3SS hits.
- **U2AF1** mutations (lung adeno, MDS): altered preferences at 3'ss -3 position; cassette-exon shifts.
- **TDP-43 loss** (ALS/FTD): de novo cryptic exons in UNC13A, STMN2, ATG4B (Brown 2022 *Nature*; Klim 2019 *Nat Neurosci*) — annotation-free tools required (leafcutter denovo).

## Common Pitfalls

- Treating AFE/ALE as splicing — these are typically promoter-driven (AFE) or APA-driven (ALE), not spliceosomal. Confirm with FANTOM CAGE or 3'-end-seq.
- Confusing detained introns with NMD-targeted RI — both call as "IR" but have opposite biological fates.
- Using poly(A) libraries for IR analysis — biases toward mature transcripts, depletes pre-mRNA.
- Single-end short reads — junction-spanning reads need >=8nt overhang on both sides; biases toward shorter exons.
- Quoting "PSI of the gene" from MAJIQ LSV output — only per-junction PSI within an LSV is meaningful.
- Skipping STAR 2-pass — loses ~14% of novel junctions; matters for any non-canonical organism or condition.
- Trusting rMATS calls without `--novelSS` when STAR 2-pass found new junctions — rMATS will only quantify pre-annotated events.

## Related Skills

- differential-splicing - Compare PSI between conditions; use the same upstream alignment but switch to with-stat tools
- splicing-qc - Run BEFORE quantification to verify library, depth, strandedness, alignment quality
- isoform-switching - DTU framework with NMD/ORF/domain consequences; complementary to event-level PSI
- sashimi-plots - Visualize specific events for QC and reporting; concordance check across tools
- splice-variant-prediction - SpliceAI/Pangolin for variant impact predictions to test against PSI changes
- long-read-splicing - Full-isoform PSI without anchor-length limits; preferred for microexons and complex isoforms
- read-alignment/star-alignment - STAR 2-pass cohort-style alignment is required upstream
- rna-quantification/alignment-free-quant - Salmon/kallisto TPM is required for SUPPA2

## References

- Wang et al 2008 *Nature* - AS event taxonomy
- Vaquero-Garcia et al 2016 *eLife* - MAJIQ LSV framework
- Trincado et al 2018 *Genome Biol* - SUPPA2
- Li et al 2018 *Nat Genet* - leafcutter
- Tapial et al 2017 *Genome Res* - VAST-TOOLS / VastDB
- Wang et al 2024 *Nat Protoc* - rMATS-turbo
- Aicher, Slaff, Jewell, Barash 2024 *bioRxiv* - MAJIQ V3
- Kubota et al 2025 *NAR* - Shiba
- Lorenzi et al 2021 *Genome Biol* - IRFinder-S
- Boutz et al 2015 *Genes Dev* - detained introns
- Irimia et al 2014 *Cell* - SRRM4 microexons
- Darman et al 2015 *Cell Rep* - SF3B1 cryptic 3'ss
- Olofsson et al 2023 *Biochem Biophys Res Commun* 653:31-37 - benchmark
- Tran et al 2025 *WIREs RNA* - methodology review
- Brown et al 2022 *Nature* - UNC13A cryptic exon (TDP-43)
- Klim et al 2019 *Nat Neurosci* - STMN2 cryptic splicing
- Veeneman et al 2016 *Bioinformatics* - STAR 2-pass benchmark
<!-- END FILE: alternative-splicing/splicing-quantification/SKILL.md -->

<!-- END CATEGORY: alternative-splicing -->

