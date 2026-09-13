---
slug: bio-rna-quantification-integrated
version: 1.0.0
displayName: "RNA定量 / RNA quantification"
name: bio-rna-quantification-integrated
summary: >-
  中文：RNA定量综合技能，整合 4 个相关专题，覆盖RNA定量：featureCounts基因计数、Salmon/kallisto无比对定量、tximport转录本汇总。 English: Integrated RNA quantification skill covering 4 related topics, including RNA quantification: featureCounts gene counting, Salmon/kallisto alignment-free quantification, tximport transcript summarization.
description: >-
  中文：这是一个面向RNA定量的综合生物信息学 Skill，整合当前分类下 4 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：RNA定量：featureCounts基因计数、Salmon/kallisto无比对定量、tximport转录本汇总。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：DESeq2, featureCounts, salmon。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for RNA quantification, combining 4 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers RNA quantification: featureCounts gene counting, Salmon/kallisto alignment-free quantification, tximport transcript summarization. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: DESeq2, featureCounts, salmon. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# rna-quantification 分类 Skill 整合版

> 本文件整合同一主分类目录下 4 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: rna-quantification -->

## 子目录：rna-quantification/alignment-free-quant

<!-- BEGIN FILE: rna-quantification/alignment-free-quant/SKILL.md -->
---
name: bio-rna-quantification-alignment-free-quant
description: Quantify transcript expression from FASTQ with Salmon (selective alignment) or kallisto (pseudoalignment), bypassing genome mapping. Use when quantifying RNA-seq without alignment, deciding whether a decoy-aware index is required, detecting and verifying library strandedness, enabling GC and sequence bias correction, or choosing whether to generate inferential replicates (bootstraps/Gibbs) for transcript-level downstream testing.
tool_type: cli
primary_tool: salmon
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: Salmon 1.10+, kallisto 0.50+, fastp 0.23+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Alignment-Free Quantification

**"Quantify gene expression without aligning to the genome"** -> Estimate transcript abundances directly from FASTQ reads by mapping to a transcriptome, then resolving multi-mapping reads (paralogs, shared isoform sequence) with an EM/variational model.
- CLI: `salmon quant -i index -l A -1 R1.fq.gz -2 R2.fq.gz -o quant/`, `kallisto quant -i index -o out R1.fq.gz R2.fq.gz`

These tools do not just count reads; they run probabilistic inference. Most fragments are compatible with several transcripts, so the abundance of each transcript is a latent quantity estimated by EM (Salmon offline phase, RSEM) or variational Bayes (Salmon default). The two load-bearing decisions that determine whether the numbers are trustworthy are the index (decoy-aware or not) and the library type. Get either wrong and the run completes silently with biased output.

## Decision 1: the decoy-aware index is not optional

A transcriptome-only index has no target for reads that originate from introns, unannotated transcription, or intergenic DNA. Those reads do not vanish; they are force-fit onto whatever transcript shares enough sequence, inflating its count. Adding the genome as a set of decoy sequences fixes this: if a fragment aligns better to a decoy than to any transcript, all of its mappings are discarded rather than misassigned. Always build the decoy-aware index when the genome is available (Srivastava et al. 2020).

```bash
# Decoy names = every genome sequence header
grep "^>" genome.fa | cut -d " " -f 1 | sed 's/>//g' > decoys.txt

# gentrome = transcripts FIRST, then genome
cat transcripts.fa genome.fa > gentrome.fa

# Build (k=31 is right for reads >=75 bp; lower to ~23-25 for ~50 bp reads)
salmon index -t gentrome.fa -d decoys.txt -i salmon_index -k 31 -p 8
```

`--validateMappings` is deprecated and has no effect: selective alignment has been the default since Salmon 1.0.0. Do not pass it. This is the accuracy difference from pure pseudoalignment (kallisto): pseudoalignment commits a read to its compatible transcript set without scoring base-level mismatches, so it over-assigns intron-, pseudogene-, and error-derived reads, whereas selective alignment computes an actual alignment score around each candidate and drops low-scoring spurious mappings. kallisto has no equivalent decoy index; its closest analog is `--d-list genome.fa` (a distinguishing-k-mer filter, different mechanism) to partially compensate.

## Decision 2: library type drives strandedness

```bash
# Salmon: auto-detect, then VERIFY
salmon quant -i salmon_index -l A \
    -1 sample_R1.fastq.gz -2 sample_R2.fastq.gz \
    -o sample_quant --gcBias --seqBias -p 8

# Single-end
salmon quant -i salmon_index -l A -r sample.fastq.gz -o sample_quant -p 8
```

`-l A` auto-detects the type and writes the inferred format to `lib_format_counts.json`. Inspect it: a library with weak strand signal can be miscalled, and the wrong type makes correctly oriented fragments incompatible, collapsing or randomizing abundances. The dominant modern chemistry (dUTP / Illumina TruSeq Stranded / NEBNext Directional) is `ISR` for Salmon and maps to `featureCounts -s 2` (reverse). Map: unstranded `IU` <-> `-s 0`; forward `ISF`/`SF` <-> `-s 1`; reverse `ISR`/`SR` <-> `-s 2`. 3'-tag protocols carry their own strandedness (Lexogen QuantSeq FWD is forward, `SF`/`-s 1`; QuantSeq REV is reverse), so rely on `-l A` and `lib_format_counts.json` rather than assuming reverse.

## Bias correction

`--gcBias` and `--seqBias` learn sample-specific fragment-GC and random-hexamer-priming biases and reweight the read-to-transcript probabilities. They cost little and protect against the case that produces false positives: when library-prep batch is confounded with the biological condition, an uncorrected GC bias becomes a condition effect. Enable both as a near-default; reserve `--posBias` for degraded or visibly 3'-biased libraries.

## Inferential replicates: only when transcript-level uncertainty matters

Transcripts that share sequence are not individually identifiable, so their point estimates carry inferential (quantification) uncertainty on top of biological variance. This uncertainty cancels when isoforms are summed to the gene, so gene-level DESeq2/edgeR via tximport needs no replicates. It does not cancel at the transcript level: differential transcript expression (DTE) and usage (DTU) require propagating it.

```bash
# Generate inferential replicates ONLY for transcript-level downstream testing
salmon quant -i salmon_index -l A --gcBias --seqBias \
    --numGibbsSamples 20 \
    -1 R1.fq.gz -2 R2.fq.gz -o sample_quant -p 8

# kallisto bootstraps (for sleuth)
kallisto quant -i kallisto_index -o sample_quant -b 100 R1.fq.gz R2.fq.gz
```

Use `--numGibbsSamples 20` (or `--numBootstraps 30`) for Salmon; ~100 bootstraps for kallisto. Downstream consumers: swish (alternative-splicing/isoform-switching), sleuth (expression-matrix/counts-ingest), edgeR catchSalmon (differential-expression/edger-basics). Do not pay this cost for gene-level work.

## kallisto Workflow

```bash
kallisto index -i kallisto_index transcripts.fa

# Paired-end learns the fragment-length distribution from mate distances
kallisto quant -i kallisto_index -o sample_quant R1.fastq.gz R2.fastq.gz

# Single-end CANNOT observe fragment length -> must supply mean (-l) and sd (-s),
# which set effective lengths and therefore TPM; wrong values bias every TPM
kallisto quant -i kallisto_index -o sample_quant --single -l 200 -s 20 sample.fastq.gz
```

## Output

`quant.sf` (Salmon) columns: `Name`, `Length`, `EffectiveLength`, `TPM`, `NumReads`. kallisto `abundance.tsv`: `target_id`, `length`, `eff_length`, `est_counts`, `tpm`; `abundance.h5` holds bootstraps. EffectiveLength is the transcript length convolved with the fragment-length distribution; a transcript shorter than the mean fragment length has a tiny, unstable effective length, so its TPM is hypersensitive to small count changes. Treat short-transcript TPMs with suspicion and filter low-count features before testing.

Import the estimated counts (`NumReads`/`est_counts`), not TPM, into DESeq2/edgeR via tximport, which adds the length offset (rna-quantification/tximport-workflow). TPM is a within-sample proportion and is invalid for cross-sample differential expression.

## Salmon vs kallisto vs RSEM

| Tool | Speed | Accuracy | Best when |
|------|-------|----------|-----------|
| Salmon (selective alignment + decoy) | Fast | Highest among lightweight | Default for bulk RNA-seq; decoy absorbs intron/pseudogene reads |
| kallisto | Fastest | Excellent | Speed-critical or sleuth-based DTE; add `--d-list` to mitigate intron over-assignment |
| RSEM | Slowest (needs a separate aligner) | Reference standard | Defensible benchmark accuracy; runs on a transcriptome BAM (STAR `--quantMode TranscriptomeSAM`) |

Methodology evolves; confirm current defaults against the Salmon and kallisto docs before relying on a flag.

## Combine TPM / counts for inspection

```python
import pandas as pd
from pathlib import Path

samples = ['sample1', 'sample2', 'sample3']
tpm, counts = {}, {}
for s in samples:
    df = pd.read_csv(Path(f'{s}_quant/quant.sf'), sep='\t', index_col=0)  # kallisto: abundance.tsv
    tpm[s], counts[s] = df['TPM'], df['NumReads']                          # kallisto: tpm, est_counts
pd.DataFrame(tpm).to_csv('tpm_matrix.csv')
pd.DataFrame(counts).to_csv('counts_matrix.csv')
```

## Quality Checks

```bash
grep "Mapping rate" sample_quant/logs/salmon_quant.log   # expect > ~70% for a matched reference
cat sample_quant/lib_format_counts.json                  # confirm one consistent library type
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Low mapping rate (<50%) | Wrong/old transcriptome version, contamination, or no decoy | First confirm a decoy-aware index and a transcriptome matching the GTF release; then run FastQ Screen for contamination |
| One gene/transcript implausibly high | Intron or pseudogene reads forced onto it (transcriptome-only index) | Rebuild with genome decoys |
| Counts halve or look random for stranded data | Library type miscalled by `-l A` | Read `lib_format_counts.json`; for dUTP/TruSeq it should be `ISR` |
| Inconsistent library types across samples | Mixed library preps or a sample swap | Verify metadata; quantify suspect samples separately and compare |
| `swish: no inferential replicates found` downstream | Salmon/kallisto run without Gibbs/bootstraps | Re-run with `--numGibbsSamples 20` (or kallisto `-b 100`) |

## Related Skills

- rna-quantification/tximport-workflow - Import counts with the length offset for DESeq2/edgeR
- rna-quantification/featurecounts-counting - Alignment-based counting alternative
- read-qc/fastp-workflow - Upstream adapter/quality trimming
- alternative-splicing/isoform-switching - swish DTE/DTU using Salmon Gibbs samples
- expression-matrix/counts-ingest - sleuth on kallisto bootstraps
- differential-expression/edger-basics - catchSalmon transcript-level DTE
- differential-expression/deseq2-basics - Gene-level downstream analysis

## References

- Patro R, Duggal G, Love MI, Irizarry RA, Kingsford C. 2017. Salmon provides fast and bias-aware quantification of transcript expression. Nat Methods 14(4):417-419. doi:10.1038/nmeth.4197
- Bray NL, Pimentel H, Melsted P, Pachter L. 2016. Near-optimal probabilistic RNA-seq quantification. Nat Biotechnol 34(5):525-527. doi:10.1038/nbt.3519
- Srivastava A, Malik L, Sarkar H, et al. 2020. Alignment and mapping methodology influence transcript abundance estimation. Genome Biol 21:239. doi:10.1186/s13059-020-02151-8
- Love MI, Hogenesch JB, Irizarry RA. 2016. Modeling of RNA-seq fragment sequence bias reduces systematic errors in transcript abundance estimation. Nat Biotechnol 34(12):1287-1291. doi:10.1038/nbt.3682
<!-- END FILE: rna-quantification/alignment-free-quant/SKILL.md -->

## 子目录：rna-quantification/count-matrix-qc

<!-- BEGIN FILE: rna-quantification/count-matrix-qc/SKILL.md -->
---
name: bio-rna-quantification-count-matrix-qc
description: Quality control and exploration of RNA-seq count matrices before differential expression. Use when checking library sizes and composition, choosing VST vs rlog for visualization, running PCA and sample correlation, detecting outliers with Cook's distance, deciding how to handle known vs unknown batch effects, screening for sample swaps, or judging whether a sample or design is too compromised to test.
tool_type: mixed
primary_tool: DESeq2
---

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, edgeR 4.0+, ggplot2 3.5+, pheatmap 1.0+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scikit-learn 1.4+, scipy 1.12+, seaborn 0.13+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Count Matrix QC

**"Check my count matrix for outliers and batch effects"** -> Assess depth, composition, sample relationships, and outliers on appropriately transformed data, then decide what (if anything) to remove or model before differential expression.
- R: `DESeq2::vst()` -> `plotPCA()`, sample-distance heatmap, Cook's distance
- Python: `sklearn.decomposition.PCA`, `seaborn.clustermap` (with the low-count caveat below)

Two principles govern this whole skill. First, DE testing runs on raw counts with a size-factor offset; the transformed matrices here are for QC and visualization only, never fed back into the count model. Second, raw counts confound depth, composition, and biology, so QC must look at the right scale: a variance-stabilized matrix for clustering/PCA, and the size factors and Cook's distances from the count model for normalization and outliers.

## Load and Inspect

**Goal:** Get counts into a model object and read off depth and detection per sample.

**Approach:** Build a DESeqDataSet (from tximport or a matrix), then summarize library size and genes detected.

```r
library(DESeq2)
counts <- read.csv('count_matrix.csv', row.names = 1)
coldata <- data.frame(condition = factor(c('ctrl', 'ctrl', 'treat', 'treat')),
                      row.names = colnames(counts))
dds <- DESeqDataSetFromMatrix(countData = counts, colData = coldata, design = ~ condition)

colSums(counts(dds))        # library size per sample
colSums(counts(dds) > 0)    # genes detected per sample
```

```python
import pandas as pd, numpy as np
counts = pd.read_csv('count_matrix.csv', index_col=0)
metadata = pd.read_csv('sample_info.csv', index_col=0)
print(counts.sum()); print((counts > 0).sum())
```

## Filtering: the principled cut

**Goal:** Drop genes with too little signal to test, in a depth- and design-aware way.

**Approach:** Prefer edgeR `filterByExpr` (keeps genes with enough counts in at least the smallest group's worth of samples) over an arbitrary `CPM > 1` rule.

```r
library(edgeR)
keep <- filterByExpr(counts(dds), group = dds$condition)
dds <- dds[keep, ]
```

```python
min_counts, min_samples = 10, 3   # 10 reads in >=3 samples; ~smallest group size
counts_filt = counts[(counts >= min_counts).sum(axis=1) >= min_samples]
```

In DESeq2, pre-filtering is mainly for speed and to drop all-zero rows; the inferential filter is independent filtering done automatically inside `results()` (it picks a mean-count threshold maximizing discoveries at the chosen alpha). Keep pre-filtering light. For edgeR/limma-voom, `filterByExpr` is the filter.

## Normalization and transformation

Composition bias is the reason depth scaling is not enough: if a few genes dominate a library, every other gene looks depressed at unchanged absolute output. DESeq2 median-of-ratios and edgeR TMM each estimate one size factor per sample assuming most genes are not DE, then apply it as an offset on the raw counts. CPM and TPM do NOT correct composition (they rescale by a within-sample total) -- the same reason TPM is invalid for cross-sample comparison upstream -- so they are for visualization, not DE normalization. For matrices with many structural zeros (single-cell, metagenomics), use the `poscounts` size-factor estimator.

For QC visualization the matrix must be homoskedastic. `log2(CPM + 1)` is not: at low counts the log amplifies sampling noise, so PCA on it is driven by noisy near-zero genes. Use a variance-stabilizing transform instead.

| Transform | Speed | Use when |
|-----------|-------|----------|
| `vst()` | Fast | Default, especially medium-to-large n (>30) |
| `rlog()` | Slow | Small n (roughly < 30) and heterogeneous designs; but can over-shrink when size factors span a very wide range (then prefer vst) |

```r
vsd <- vst(dds, blind = TRUE)    # blind=TRUE for unsupervised QC; FALSE only after DESeq() for plotting
mat <- assay(vsd)
```

## PCA and sample relationships

**Goal:** See whether replicates cluster and whether PC1 is biology or a technical artifact.

**Approach:** PCA on the VST matrix (top variable genes), then read PC1 against depth and batch.

```r
plotPCA(vsd, intgroup = 'condition')                     # uses top 500 most-variable genes
sampleDists <- dist(t(assay(vsd)))
pheatmap::pheatmap(as.matrix(sampleDists))
```

```python
from sklearn.decomposition import PCA
# log-CPM PCA is a quick look only: low-count heteroskedasticity can drive the PCs.
# For publication QC, compute VST in R and bring the matrix into Python.
cpm = counts_filt * 1e6 / counts_filt.sum()
log_cpm = np.log2(cpm + 1)
pcs = PCA(n_components=2).fit_transform(log_cpm.T)
```

If PC1 correlates with library size or detected-gene count rather than condition, it is a depth artifact (color the PCA by `log10` library size to confirm). A common pattern is PC1 = batch, PC2 = condition, which is a design problem, not a normalization fix.

## Outlier detection with Cook's distance

**Goal:** Distinguish a single bad count in one gene from a globally bad sample.

**Approach:** Read per-gene-per-sample Cook's distances from the fitted model; treat single-gene outliers and whole-sample outliers differently.

```r
dds <- DESeq(dds)
cooks <- assays(dds)[['cooks']]          # per gene x sample; NOT results(dds)$cooksd
boxplot(log10(cooks), las = 2, main = "Cook's distance")
# results() flags a gene whose max Cook's exceeds qf(0.99, p, m-p) by setting its p-value to NA.
# With >= 7 replicates per group (minReplicatesForReplace) DESeq2 replaces the outlier count instead.
```

A single-gene-in-one-sample outlier is exactly what Cook's filtering and `replaceOutliers` are for; let DESeq2 handle it. A whole-sample outlier (many flagged genes in one sample, that sample far on the VST-PCA, low correlation to its replicates, an anomalous size factor) is not rescuable by `replaceOutliers`. Investigate, and remove only with a documented technical cause, since post-hoc cherry-picking inflates false positives.

## Batch effects

Known batch goes in the design; the engine estimates and removes it on raw counts while propagating uncertainty:

```r
design(dds) <- ~ batch + condition       # condition last = contrast of interest
```

Do NOT run `removeBatchEffect()` or ComBat and feed the adjusted matrix into DESeq2/edgeR; those engines model batch internally, and pre-adjusting double-corrects and breaks the count model. `limma::removeBatchEffect(assay(vsd), batch = vsd$batch)` is for visualization only. For unknown/unmeasured structure, estimate surrogate variables (`sva`/`svaseq`) or factors of unwanted variation (`RUVSeq`: RUVg control genes, RUVs replicate samples, RUVr residuals) and add them to the design.

The fatal case: if batch is correlated with condition, regressing it out removes biology too; a perfect confound (all treated in batch 1, all control in batch 2) is statistically unfixable. Cross-tabulate batch against condition before fitting.

## Library-level QC and sample swaps

```r
sf <- sizeFactors(estimateSizeFactors(dds))   # a size factor far from 1 (< ~0.3 or > ~3) is a red flag
```

Do not deduplicate standard RNA-seq: high duplication is expected from highly expressed genes, and position-based dedup discards real signal (deduplicate only with UMIs). Screen for sample swaps cheaply with sex-linked genes (XIST high in XX; RPS4Y1/UTY/DDX3Y high in XY) against recorded sex, and confirm identity with genotype concordance tools (VerifyBamID, somalier) when available.

## Red flags that should halt a DE analysis

1. A sample clusters away from its group on the VST-PCA (and concentrates Cook's-flagged genes).
2. A size factor far from 1, or a library an order of magnitude off the cohort.
3. Near-zero correlation of a sample to its replicates.
4. Condition (near-)perfectly confounded with batch, lane, or run.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `results(dds)$cooksd` is NULL | Cook's distance is not a results column | Read `assays(dds)[['cooks']]` |
| PCA driven by a few noisy genes | PCA run on `log2(CPM+1)` or raw counts | Use VST/rlog; restrict to top-variable genes |
| Batch effect persists after correction | `removeBatchEffect` output fed to DESeq2 | Put batch in the design instead; keep correction for plots only |
| Every gene significant, or none | Sample swap / confounded batch / wrong normalization | Check metadata, batch x condition table, and size factors first |
| One transform behaves oddly with wide size factors | rlog over-shrinks | Switch to vst |

## Related Skills

- rna-quantification/featurecounts-counting - Generate the count matrix
- rna-quantification/tximport-workflow - Import transcript counts with the length offset
- differential-expression/deseq2-basics - DE testing after QC
- differential-expression/de-visualization - Downstream result visualization
- read-qc/rnaseq-qc - Upstream read-level QC (rRNA, degradation, contamination)

## References

- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. Genome Biol 15(12):550. doi:10.1186/s13059-014-0550-8
- Robinson MD, Oshlack A. 2010. A scaling normalization method for differential expression analysis of RNA-seq data. Genome Biol 11(3):R25. doi:10.1186/gb-2010-11-3-r25
- Risso D, Ngai J, Speed TP, Dudoit S. 2014. Normalization of RNA-seq data using factor analysis of control genes or samples. Nat Biotechnol 32(9):896-902. doi:10.1038/nbt.2931
<!-- END FILE: rna-quantification/count-matrix-qc/SKILL.md -->

## 子目录：rna-quantification/featurecounts-counting

<!-- BEGIN FILE: rna-quantification/featurecounts-counting/SKILL.md -->
---
name: bio-rna-quantification-featurecounts-counting
description: Count reads per gene from aligned BAM files using Subread featureCounts. Use when turning STAR/HISAT2 BAMs into a gene-level count matrix for DESeq2/edgeR, deciding library strandedness, handling paired-end fragment counting, choosing how to treat multi-mapping and multi-overlapping reads, or diagnosing a low assignment rate from the summary file.
tool_type: cli
primary_tool: featureCounts
---

## Version Compatibility

Reference examples tested with: Subread 2.0+, STAR 2.7.11+, HISAT2 2.2.1+, DESeq2 1.42+, edgeR 4.0+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# featureCounts Counting

**"Count reads per gene from my BAM files"** -> Assign each aligned read to at most one gene by overlap with a GTF, discarding ambiguous reads, to produce an integer gene-by-sample matrix for differential expression.
- CLI: `featureCounts -a genes.gtf -o counts.txt sample1.bam sample2.bam`

featureCounts is bookkeeping, not inference: it tallies reads to genes and discards anything ambiguous. That is correct for gene-level DE, where almost every read's gene of origin is unambiguous even when its isoform is not. The two settings that silently corrupt the matrix if wrong are strandedness (`-s`) and, for paired-end data, fragment counting (`--countReadPairs`).

## Basic Usage

```bash
# Multiple samples in one run -> a single aligned matrix (recommended)
featureCounts -a annotation.gtf -o counts.txt sample1.bam sample2.bam sample3.bam

# Defaults: -t exon -g gene_id (count reads over exons, aggregate by gene)
```

## Decision 1: strandedness (`-s`) is the load-bearing setting

| `-s` | Meaning | Read 1 |
|------|---------|--------|
| 0 | Unstranded | strand ignored |
| 1 | Forward stranded | read 1 is sense |
| 2 | Reverse stranded | read 1 is antisense; read 2 is sense |

The dominant chemistry, dUTP / Illumina TruSeq Stranded / NEBNext Directional, is reverse, `-s 2`. Setting the wrong strand does not error; it silently destroys the matrix. For a truly stranded library, the correct `-s` assigns ~80-90% of reads while the opposite setting collapses to ~5-20% (counting only antisense background). Do not trust the kit name; determine it empirically:

```bash
# Method A: RSeQC reports the strand pattern fractions
infer_experiment.py -r genes.bed -i sample.bam

# Method B: run all three and pick the one that maximizes Assigned in the .summary
for s in 0 1 2; do featureCounts -s $s -a annotation.gtf -o counts_s$s.txt sample.bam; done
```

If `-s 1` and `-s 2` give wildly different Assigned fractions, the data are stranded (use the higher); if both are roughly equal and about half of `-s 0`, the data are unstranded. STAR `--quantMode GeneCounts` provides a free cross-check (see below).

## Decision 2: paired-end fragment counting

```bash
# Subread >= 2.0.2: -p only declares paired input; --countReadPairs is REQUIRED to count fragments
featureCounts -p --countReadPairs -a annotation.gtf -o counts.txt *.bam

# Stricter: require both ends mapped, exclude chimeric/discordant pairs
featureCounts -p --countReadPairs -B -C -a annotation.gtf -o counts.txt *.bam
```

Omitting `--countReadPairs` on paired-end data counts each mate separately, roughly doubling counts and breaking the count model. `-B` requires both ends aligned; `-C` excludes pairs mapping across chromosomes or in the wrong orientation.

## Decision 3: multi-mapping and multi-overlap reads

```bash
# Default (recommended for gene-level DE): discard both -> uniquely, unambiguously assigned reads only
featureCounts -a annotation.gtf -o counts.txt *.bam

# Count multimappers fractionally (1/N) or fully (1 each) -- NOT recommended for DE
featureCounts -M --fraction -a annotation.gtf -o counts.txt *.bam
featureCounts -M -a annotation.gtf -o counts.txt *.bam

# Count reads overlapping >1 gene in all of them
featureCounts -O -a annotation.gtf -o counts.txt *.bam
```

Discarding multimappers is the right default for gene-level DE. `-M --fraction` looks principled but biases exactly the genes where resolution matters: a read truly from gene A that also maps to paralog A' is split 0.5/0.5, diluting both. This is the regime where alignment-free EM quantifiers (rna-quantification/alignment-free-quant) outperform featureCounts, because they reassign by full likelihood rather than a flat split.

## Quality and feature options

```bash
featureCounts -Q 10 -a annotation.gtf -o counts.txt *.bam      # min MAPQ (aligner-specific scale)
featureCounts --primary -a annotation.gtf -o counts.txt *.bam  # primary alignments only
featureCounts -t CDS -g gene_id -a annotation.gtf -o counts.txt *.bam  # count CDS instead of exon
```

`-Q` thresholds mapping quality, but MAPQ conventions are aligner-specific (STAR assigns 255 to unique reads, low values to multimappers), so confirm the scheme before choosing a cutoff. Do NOT add `--ignoreDup` for standard RNA-seq: high duplication is expected from highly expressed genes, and position-based deduplication discards real signal. Deduplicate only with UMIs. For exon-level usage testing (DEXSeq), use a flattened annotation rather than gene-level counting (alternative-splicing/isoform-switching).

## Output

```
counts.txt:           Geneid Chr Start End Strand Length sample1.bam sample2.bam ...
counts.txt.summary:   Status              sample1.bam  sample2.bam
                      Assigned            1523456      1678234
                      Unassigned_NoFeatures 234567     245678
```

Reading the `.summary` is the primary QC step. A good poly-A library assigns ~70-90% of mapped reads (rRNA-depletion libraries run lower).

| Dominant unassigned category | Likely cause | Action |
|------------------------------|--------------|--------|
| Unassigned_NoFeatures high | GTF/genome mismatch (chr naming `1` vs `chr1`, wrong release), DNA contamination | Match GTF release and chromosome naming to the BAM |
| Unassigned_MultiMapping high | rRNA carryover or repetitive content | Check rRNA depletion; inspect with FastQ Screen |
| Unassigned_Ambiguity high | Overlapping/nested gene models or wrong feature level | Expected in gene-dense regions; reconsider `-O`/feature type |
| Assigned low, others spread thin | Wrong strandedness | Re-test `-s` (see Decision 1) |

## STAR cross-check

If aligned with STAR `--quantMode GeneCounts`, `ReadsPerGene.out.tab` gives a free independent count: column 2 = unstranded (≈ `-s 0`), column 3 = forward (≈ `-s 1`), column 4 = reverse (≈ `-s 2`). The larger of columns 3 vs 4 reveals the strand directly, and the per-gene counts should track featureCounts at the matching `-s`.

## Extract the matrix

```bash
cut -f1,7- counts.txt | tail -n +2 > count_matrix.txt   # drop the 6 annotation columns
```

```python
import pandas as pd
counts = pd.read_csv('counts.txt', sep='\t', comment='#')
mat = counts.set_index('Geneid').iloc[:, 5:]
mat.columns = [c.replace('.bam', '') for c in mat.columns]
mat.to_csv('count_matrix.csv')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Assigned ~half of expected, no error | Wrong `-s`, or paired-end without `--countReadPairs` (double-counting) | Determine strand empirically; add `--countReadPairs` for paired-end |
| Near-zero counts for known genes | `gene_id` attribute or feature type mismatch with the GTF | Confirm `-t`/`-g` match the annotation; check the GTF attribute names |
| Counts much higher than read count | Paired-end mates counted separately | Add `-p --countReadPairs` |
| Inflated correlated paralog counts | `-M`/`-O` fractional counting enabled | Drop `-M`/`-O` for DE; use alignment-free EM for paralog-heavy genes |
| Low Assigned across all `-s` values | GTF does not match the aligned genome | Use the GTF release and contig names matching the alignment reference |

## Related Skills

- alignment-files/sam-bam-basics - Input BAM handling and filtering
- read-alignment/star-alignment - Producing BAMs and ReadsPerGene.out.tab strand cross-check
- genome-intervals/gtf-gff-handling - GTF/GFF annotation files
- rna-quantification/alignment-free-quant - EM-based alternative; better for multimappers/paralogs
- rna-quantification/count-matrix-qc - QC the resulting matrix before DE
- differential-expression/deseq2-basics - Gene-level DE from these counts

## References

- Liao Y, Smyth GK, Shi W. 2014. featureCounts: an efficient general purpose program for assigning sequence reads to genomic features. Bioinformatics 30(7):923-930. doi:10.1093/bioinformatics/btt656
- Liao Y, Smyth GK, Shi W. 2013. The Subread aligner: fast, accurate and scalable read mapping by seed-and-vote. Nucleic Acids Res 41(10):e108. doi:10.1093/nar/gkt214
<!-- END FILE: rna-quantification/featurecounts-counting/SKILL.md -->

## 子目录：rna-quantification/tximport-workflow

<!-- BEGIN FILE: rna-quantification/tximport-workflow/SKILL.md -->
---
name: bio-rna-quantification-tximport-workflow
description: Import transcript-level quantifications from Salmon/kallisto/RSEM into R for gene-level analysis with DESeq2/edgeR using tximport or tximeta. Use when summarizing transcript abundances to gene counts with the correct length offset, choosing a countsFromAbundance mode (full-length vs 3'-tag vs DTU), resolving transcript-ID version mismatches, or handing off to DESeq2/edgeR without double-applying the offset.
tool_type: r
primary_tool: tximport
---

## Version Compatibility

Reference examples tested with: tximport 1.30+, tximeta 1.20+, DESeq2 1.42+, edgeR 4.0+, txdbmaker 1.0+, Salmon 1.10+, kallisto 0.50+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# tximport Workflow

**"Import Salmon/kallisto results into DESeq2"** -> Summarize transcript-level abundance estimates to gene-level counts AND compute a per-gene, per-sample length offset that the DE model consumes.
- R: `tximport::tximport(files, type='salmon', tx2gene=tx2gene)`

## Why this is not just a sum

tximport does not merely add transcript counts to a gene total. The fragment count a gene produces depends on the average length of the isoforms expressed in that sample, because longer molecules yield more fragments (more start positions). When isoform usage shifts between conditions (differential transcript usage), the gene's average effective length changes, so a naive summed count is length-biased in a condition-correlated way and masquerades as differential expression. tximport corrects this by returning a per-gene, per-sample average-length matrix (`txi$length`) and passing it as a normalization offset to DESeq2/edgeR. A single per-gene length cannot capture this because the bias is sample-specific (Soneson, Love, Robinson 2015).

## Basic tximport

**Goal:** Import transcript-level quantifications into R as gene-level counts plus the length offset for DESeq2 or edgeR.

**Approach:** Build a transcript-to-gene map, then run tximport over the quant files; the returned `txi$counts`/`txi$length` carry both the gene counts and the offset.

```r
library(tximport)

files <- c(sample1 = 'sample1_quant/quant.sf',
           sample2 = 'sample2_quant/quant.sf',
           sample3 = 'sample3_quant/quant.sf')

tx2gene <- read.csv('tx2gene.csv')                 # column order: TXNAME, then GENEID
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene)
```

`txi` is a list: `$abundance` (TPM), `$counts` (estimated counts), `$length` (the average-length offset source), `$countsFromAbundance`.

## Decision: countsFromAbundance mode

This argument silently determines correctness; nothing errors when it is wrong.

| Mode | What it returns | Use when |
|------|-----------------|----------|
| `'no'` (default) | Estimated counts + separate length offset | Full-length library -> DESeq2/edgeR (they consume the offset). The cleanest path. |
| `'lengthScaledTPM'` | Counts with the length correction baked in, no separate offset | A tool that cannot take an offset (e.g. limma-voom) |
| `'scaledTPM'` | TPM scaled to library size, no length scaling | Transcript-level DTU with `txOut=TRUE` (DRIMSeq/DEXSeq); the established Love et al. workflow input |
| `'dtuScaledTPM'` | Scaled by median isoform length | DTU alternative (tximport >= 1.10), needs `tx2gene`; helps when isoform lengths within a gene differ widely |

For DTU, `scaledTPM` is the established default; `dtuScaledTPM` is the newer purpose-built mode, preferable when a gene's isoforms span very different lengths.

The 3'-tag exception: for 3'-end protocols (10x, QuantSeq, Lexogen) a read count does not scale with transcript length, so there is no length bias to correct, and length-correcting injects one. Do not use the length-scaled modes (`lengthScaledTPM`/`dtuScaledTPM`) for tag-seq. Import with the default, but build the DESeqDataSet from the plain counts so the length offset is NOT auto-applied:

```r
# 3'-tag: bypass the length offset that DESeqDataSetFromTximport would otherwise apply
dds <- DESeqDataSetFromMatrix(round(txi$counts), colData = coldata, design = ~ condition)
```

```r
# Full-length, DESeq2/edgeR (default): keep the offset path
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene)

# Transcript-level for DTU (hand off to alternative-splicing/isoform-switching)
txi_tx <- tximport(files, type = 'salmon', txOut = TRUE,
                   countsFromAbundance = 'scaledTPM')
```

## Creating tx2gene

The map is a two-column data frame; column ORDER is load-bearing (TXNAME first, GENEID second), names do not matter.

**Goal:** Map every quantified transcript ID to its gene, with IDs that exactly match the quant files.

**Approach:** Derive from the annotation that built the index (GTF, ensembldb, biomaRt, or the index t2g); strip version suffixes to match.

```r
# From a GTF: makeTxDbFromGFF moved to txdbmaker in Bioconductor >= 3.19
# (defunct in GenomicFeatures >= 1.61.1; on older Bioconductor use GenomicFeatures::makeTxDbFromGFF)
library(txdbmaker)
txdb <- makeTxDbFromGFF('annotation.gtf')
k <- keys(txdb, keytype = 'TXNAME')
tx2gene <- AnnotationDbi::select(txdb, keys = k, keytype = 'TXNAME',
                                 columns = c('TXNAME', 'GENEID'))

# From biomaRt (useEnsembl; useMart is deprecated)
library(biomaRt)
mart <- useEnsembl(biomart = 'genes', dataset = 'hsapiens_gene_ensembl')
tx2gene <- getBM(attributes = c('ensembl_transcript_id', 'ensembl_gene_id'), mart = mart)
```

## The #1 silent failure: transcript-ID version mismatch

If `quant.sf` IDs carry version suffixes (`ENST00000456328.4`) but `tx2gene` does not (or vice versa), the IDs do not match. Total non-overlap raises an error; partial mismatch silently drops the non-matching transcripts and prints a summary, deflating affected genes toward zero. Fix by stripping versions consistently or with `ignoreTxVersion`:

```r
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene,
                ignoreTxVersion = TRUE, ignoreAfterBar = TRUE)
```

## Handoff to DESeq2 (offset applied automatically)

**Goal:** Build a DESeqDataSet that uses the tximport length offset without any manual step.

**Approach:** `DESeqDataSetFromTximport` stores `txi$length` as the `avgTxLength` assay and converts it to per-gene normalization factors inside `DESeq()`.

```r
library(DESeq2)
coldata <- data.frame(condition = factor(c('control', 'control', 'treated', 'treated')),
                      row.names = names(files))
dds <- DESeqDataSetFromTximport(txi, colData = coldata, design = ~ condition)
dds <- dds[rowSums(counts(dds)) >= 10, ]   # light pre-filter (speed); results() does the inferential filter
dds <- DESeq(dds)
res <- results(dds)
```

Passing a `countsFromAbundance='no'` txi prints "using counts and average transcript lengths from tximport"; a length-scaled txi prints "using just counts" and applies no offset. Both are handled correctly by the function.

## Handoff to edgeR (manual offset)

**Goal:** Carry the length offset into an edgeR DGEList.

**Approach:** Geometric-mean-center the length matrix, fold in composition-corrected library sizes, log it, attach via `scaleOffset`.

```r
library(edgeR)
cts <- txi$counts
normMat <- txi$length / exp(rowMeans(log(txi$length)))   # center each gene on its geometric mean
normCts <- cts / normMat
eff.lib <- calcNormFactors(normCts) * colSums(normCts)
normMat <- sweep(normMat, 2, eff.lib, '*')
y <- scaleOffset(DGEList(cts), log(normMat))
y <- y[filterByExpr(y, group = coldata$condition), , keep.lib.sizes = FALSE]   # group-aware filter
```

Do not double-apply the offset: if `countsFromAbundance='lengthScaledTPM'` already baked the correction into the counts, do not also attach a length offset. Use `'no'` for the offset path, the scaled modes for the no-offset path, never both.

## Transcript-level uncertainty (DTE/DTU)

Gene-level estimates are robust because per-isoform assignment uncertainty cancels on summation. Transcript-level testing must propagate it: edgeR `catchSalmon` deflates counts by per-transcript overdispersion (differential-expression/edger-basics), swish/fishpond tests across Salmon Gibbs samples (alternative-splicing/isoform-switching), and sleuth uses kallisto bootstraps (expression-matrix/counts-ingest). Generate the replicates at quantification time (rna-quantification/alignment-free-quant).

## tximeta: provenance by checksum

tximeta hashes the index's reference sequences and looks the digest up against known GENCODE/Ensembl/RefSeq releases, attaching transcript ranges and release metadata automatically, so the exact reference becomes a verified property of the object rather than lab lore.

```r
library(tximeta)
makeLinkedTxome(indexDir = 'salmon_index', source = 'Ensembl', organism = 'Homo sapiens',
                release = '110', genome = 'GRCh38', fasta = 'transcripts.fa', gtf = 'annotation.gtf')
coldata <- data.frame(names = names(files), files = files,
                      condition = c('control', 'control', 'treated', 'treated'))
se <- tximeta(coldata)
gse <- summarizeToGene(se)
dds <- DESeqDataSet(gse, design = ~ condition)
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Many genes import as zero or deflated | Transcript-ID version mismatch (partial drop) | `ignoreTxVersion = TRUE`; or strip `\.\d+$` from both sides |
| Error: none of the transcripts present in tx2gene | Total ID mismatch (versions or wrong annotation) | Rebuild tx2gene from the annotation that built the index |
| Summarized at the wrong level, no error | tx2gene columns reversed (GENEID first) | Order as TXNAME, then GENEID |
| Length bias appears in 3'-tag data | DESeqDataSetFromTximport auto-applied the length offset | Build via `DESeqDataSetFromMatrix(round(txi$counts), ...)` so no offset is applied |
| Fold changes inflated near isoform switches with manual edgeR | Offset double-applied or omitted | One path only: `'no'`+offset, or scaled mode without offset |

## Related Skills

- rna-quantification/alignment-free-quant - Upstream Salmon/kallisto and inferential replicates
- differential-expression/deseq2-basics - Gene-level DE from a DESeqDataSet
- differential-expression/edger-basics - edgeR DE and catchSalmon transcript DTE
- alternative-splicing/isoform-switching - DTU and swish from transcript-level import
- expression-matrix/counts-ingest - sleuth and other quantifier ingestion paths
- genome-intervals/gtf-gff-handling - Building tx2gene from a GTF

## References

- Soneson C, Love MI, Robinson MD. 2015. Differential analyses for RNA-seq: transcript-level estimates improve gene-level inferences. F1000Research 4:1521. doi:10.12688/f1000research.7563
- Love MI, Soneson C, Hickey PF, et al. 2020. Tximeta: Reference sequence checksums for provenance identification in RNA-seq. PLoS Comput Biol 16(2):e1007664. doi:10.1371/journal.pcbi.1007664
<!-- END FILE: rna-quantification/tximport-workflow/SKILL.md -->

<!-- END CATEGORY: rna-quantification -->

