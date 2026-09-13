---
slug: bio-small-rna-seq-integrated
version: 1.0.0
displayName: "小RNA测序 / Small RNA-seq"
name: bio-small-rna-seq-integrated
summary: >-
  中文：小RNA测序综合技能，整合 6 个相关专题，覆盖小RNA测序：miRNA/isomiR/tRF/piRNA分析、miRDeep2新miRNA发现、miRge3定量。 English: Integrated Small RNA-seq skill covering 6 related topics, including Small RNA-seq: miRNA/isomiR/tRF/piRNA analysis, miRDeep2 novel miRNA discovery, miRge3 quantification.
description: >-
  中文：这是一个面向小RNA测序的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：小RNA测序：miRNA/isomiR/tRF/piRNA分析、miRDeep2新miRNA发现、miRge3定量。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：DESeq2, MINTmap, cutadapt。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Small RNA-seq, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Small RNA-seq: miRNA/isomiR/tRF/piRNA analysis, miRDeep2 novel miRNA discovery, miRge3 quantification. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: DESeq2, MINTmap, cutadapt. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# small-rna-seq 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: small-rna-seq -->

## 子目录：small-rna-seq/differential-mirna

<!-- BEGIN FILE: small-rna-seq/differential-mirna/SKILL.md -->
---
name: bio-small-rna-seq-differential-mirna
description: Tests miRNAs for differential expression with DESeq2 or edgeR using small-RNA-aware normalization and filtering. Use when deciding which normalization survives a library dominated by a few hyper-abundant miRNAs (compositional fragility); choosing DESeq2 vs edgeR vs a compositional method; setting a lower prefilter than mRNA; handling biofluid data with no endogenous normalizer; or remembering that RPM is for display and TDMD can make a miRNA drop without transcriptional repression.
tool_type: r
primary_tool: DESeq2
---

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, edgeR 4.0+, apeglm 1.24+, EnhancedVolcano 1.20+, pheatmap 1.0.12+, ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Differential miRNA Expression

**"Find differentially expressed miRNAs between my conditions"** -> Test a raw miRNA count matrix for expression changes, accounting for the compositional fragility that makes miRNA normalization harder than mRNA.
- R: `DESeq2::DESeq()` or `edgeR::glmQLFTest()` on RAW miRNA counts

## The governing principle: a few miRNAs dominate the library, so normalization is the dominant decision

A miRNA library is not a gently varying pool of thousands of features like an mRNA library. A handful of tissue-dominant miRNAs can be more than half of all reads, and the expressed repertoire is only hundreds to low-thousands of miRNAs. Two consequences follow, and they matter more than the choice of DE engine. First, global-scaling normalizers (DESeq2 median-of-ratios, edgeR TMM) assume most features are not differentially expressed and the count distribution is roughly symmetric; when one dominant miRNA shifts between conditions it absorbs the size factor and distorts every other miRNA's normalized value, manufacturing phantom changes. The normalization choice genuinely changes which miRNAs are called DE (Garmire 2012; Tam 2015) - so filter low-count noise FIRST, inspect whether a few miRNAs dominate, and report the normalizer. Second, empirical-Bayes dispersion shrinkage borrows strength across features, so with only hundreds of miRNAs the prior is estimated from a small, noisy population and is weaker than on ~20k genes; apeglm LFC shrinkage matters more for the many low-count miRNAs.

Two reframes prevent classic mistakes. RPM is for display and cross-sample viewing, never for testing - hand RAW counts to DESeq2/edgeR, which model the count distribution themselves. And a miRNA going DOWN does not necessarily mean transcriptional repression: target-directed miRNA degradation (TDMD, via ZSWIM8) lets a highly complementary target trigger decay of the miRNA itself (Han 2020; Shi 2020), so interpret a drop as a change in steady-state level, not automatically as reduced biogenesis.

A third decision is the level of testing. Mature-miRNA-level DE answers "which miRNAs changed" with good power; isomiR-level DE is sparser (more features and zeros, weaker per-feature power, heavier multiplicity), and 5' isomiRs shift the seed and can move OPPOSITE to the canonical mature form - so never silently sum 5' isomiRs into the mature count. Collapse to mature for the standard question; test at isomiR resolution only when isomiR identity is the biology.

## Decision: which normalization / method

| Method | Normalization assumption | Best when | Fails when |
|--------|--------------------------|-----------|------------|
| DESeq2 (median-of-ratios) | most features stable; symmetric | balanced designs, no single runaway miRNA | one miRNA dominates and shifts (compositional) |
| edgeR TMM (glmQLF) | most features stable; trimmed mean | similar to DESeq2; flexible GLM | strong composition shift; default 30%/5% trim built for thousands of mRNAs |
| upper-quartile / quantile / Lowess | rank/quantile-based | skewed miRNA distributions (often better-behaved per Garmire) | when the global shape itself is the biology |
| spike-in (cel-miR-39) | external technical scale | biofluids with no endogenous reference; controls extraction | does not correct ligation bias or biological composition |
| RUVg (RUVSeq) | unwanted variation from control miRNAs | hidden batch/technical structure global scaling misses | controls poorly chosen |
| CLR + ALDEx2 (compositional) | treat counts as compositional | as a sensitivity analysis when a few miRNAs dominate | still blind to a global pool shift; more conservative |

When a perturbation moves the WHOLE pool (e.g. Dicer/Drosha loss), every internal normalizer - including CLR - forces the average change to zero and is blind to it; only external spike-ins or cell-number normalization detect a global shift (Lovén 2012).

## Load the count matrix

**Goal:** Read raw miRNA counts and build sample metadata for testing.

**Approach:** Load the miRge3/miRDeep2 count CSV (raw, not RPM) and define the condition factor.

```r
library(DESeq2)

counts <- read.csv('miR.Counts.csv', row.names = 1)   # RAW counts, not RPM
coldata <- data.frame(
    condition = factor(c('control', 'control', 'treated', 'treated')),
    row.names = colnames(counts))
```

## DESeq2 analysis

**Goal:** Identify miRNAs that change between conditions with small-RNA-aware filtering and shrinkage.

**Approach:** Build a DESeqDataSet from rounded raw counts, prefilter at a lower threshold than mRNA, run DESeq2, then shrink LFCs with apeglm for the many low-count miRNAs.

```r
dds <- DESeqDataSetFromMatrix(
    countData = round(counts),     # DESeq2 needs integers
    colData = coldata,
    design = ~ condition)

# Lower prefilter than mRNA: miRNA libraries have fewer total counts, and most
# miRBase entries are near-zero noise. Justify the threshold; do not test everything.
keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep, ]

dds <- DESeq(dds)

# Inspect for compositional risk: a size factor far from 1, or one miRNA that is a
# large fraction of reads, is a warning that median-of-ratios may be distorted.
sizeFactors(dds)

res <- results(dds, contrast = c('condition', 'treated', 'control'))
# apeglm shrinks via a named coef; for an arbitrary/multi-level contrast not expressible
# as one coef, use type = 'ashr' instead.
res_shrunk <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')
res_shrunk <- res_shrunk[order(res_shrunk$padj), ]
```

## edgeR alternative

**Goal:** Test the same data with edgeR's quasi-likelihood GLM as a cross-check.

**Approach:** Build a DGEList, filter with filterByExpr, TMM-normalize, estimate dispersion, and run the QL F-test.

```r
library(edgeR)

dge <- DGEList(counts = round(counts), group = coldata$condition)
keep <- filterByExpr(dge, group = coldata$condition)   # pass group or it treats all samples as one
dge <- dge[keep, , keep.lib.sizes = FALSE]
dge <- calcNormFactors(dge)                            # TMM

design <- model.matrix(~ condition, data = coldata)
dge <- estimateDisp(dge, design)
fit <- glmQLFit(dge, design)
qlf <- glmQLFTest(fit, coef = 2)
res_edger <- topTags(qlf, n = Inf)$table               # edgeR uses $FDR, not $padj
```

## Report effect size and expression level, not just FDR

**Goal:** Avoid calling low-count miRNAs DE on the strength of unstable fold-changes.

**Approach:** Filter on shrunk LFC and FDR, but always inspect base mean / CPM, because a significant LFC on a ~5-count miRNA is almost always noise.

```r
sig <- subset(as.data.frame(res_shrunk), padj < 0.05 & abs(log2FoldChange) > 1)
sig$baseMean <- res_shrunk[rownames(sig), 'baseMean']  # keep expression level visible
sig <- sig[order(sig$padj), ]
```

## Visualize

**Goal:** Show the result with a volcano plot and a heatmap of significant miRNAs.

**Approach:** Use EnhancedVolcano on the shrunk results and a variance-stabilized, row-scaled pheatmap.

```r
library(EnhancedVolcano); library(pheatmap)

EnhancedVolcano(res_shrunk, lab = rownames(res_shrunk),
    x = 'log2FoldChange', y = 'padj', pCutoff = 0.05, FCcutoff = 1,
    title = 'Differential miRNA expression')

# vst() subsets 1000 genes to fit the dispersion trend and ERRORS on miRNA-sized data
# (hundreds of features) - use the full varianceStabilizingTransformation instead.
vsd <- varianceStabilizingTransformation(dds, blind = FALSE)
mat <- assay(vsd)[rownames(sig), , drop = FALSE]
pheatmap(t(scale(t(mat))), annotation_col = coldata['condition'],
    show_rownames = nrow(mat) < 50)
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Everything looks DE in one direction | One dominant miRNA shifted and distorted the size factors | Filter first; inspect sizeFactors; try upper-quartile/quantile or remove the runaway from size-factor estimation |
| Inflated significance on tiny miRNAs | RPM (or unfiltered low counts) fed to the test | Use RAW counts and a lower prefilter; report baseMean for every call |
| `filterByExpr` warns "all samples one group" | group/design not passed | `filterByExpr(dge, group = coldata$condition)` |
| edgeR results have no `padj` column | edgeR names the FDR column `FDR` | Use `topTags(...)$table$FDR`, not `$padj` |
| Biofluid DE driven by a few samples | hemolysis/batch confound; no endogenous normalizer | Add cel-miR-39 spike-in normalization; flag hemolysis (miR-451a:miR-23a-3p); model batch |
| A known miRNA "down" but its gene is unchanged | TDMD (target-driven degradation), not transcription | Interpret as steady-state change; check pri/pre-miRNA or ZSWIM8 context before claiming repression |
| `vst()` errors "less than 'nsub' rows" | vst() subsets 1000 genes; miRNA datasets have only hundreds | Use `varianceStabilizingTransformation(dds, blind=FALSE)` (full VST) instead of `vst()` |

## Related Skills

- mirge3-analysis - Produces the raw count matrix
- mirdeep2-analysis - Alternative quantification
- target-prediction - Predict and validate targets of DE miRNAs
- differential-expression/deseq2-basics - General DESeq2 mechanics
- differential-expression/edger-basics - General edgeR mechanics

## References

- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biol* 15:550. doi:10.1186/s13059-014-0550-8
- Robinson MD, McCarthy DJ, Smyth GK. 2010. edgeR: a Bioconductor package for differential expression analysis of digital gene expression data. *Bioinformatics* 26:139-140. doi:10.1093/bioinformatics/btp616
- Zhu A, Ibrahim JG, Love MI. 2019. Heavy-tailed prior distributions for sequence count data: removing the noise and preserving large differences. *Bioinformatics* 35:2084-2092. doi:10.1093/bioinformatics/bty895
- Garmire LX, Subramaniam S. 2012. Evaluation of normalization methods in mammalian microRNA-Seq data. *RNA* 18:1279-1288. doi:10.1261/rna.030916.111
- Tam S, Tsao MS, McPherson JD. 2015. Optimization of miRNA-seq data preprocessing. *Brief Bioinform* 16:950-963. doi:10.1093/bib/bbv019
- Han J, LaVigne CA, Jones BT, et al. 2020. A ubiquitin ligase mediates target-directed microRNA decay independently of tailing and trimming. *Science* 370:eabc9546. doi:10.1126/science.abc9546
- Shi CY, Kingston ER, Kleaveland B, et al. 2020. The ZSWIM8 ubiquitin ligase mediates target-directed microRNA degradation. *Science* 370:eabc9359. doi:10.1126/science.abc9359
- Lovén J, Orlando DA, Sigova AA, et al. 2012. Revisiting global gene expression analysis. *Cell* 151:476-482. doi:10.1016/j.cell.2012.10.012
<!-- END FILE: small-rna-seq/differential-mirna/SKILL.md -->

## 子目录：small-rna-seq/mirdeep2-analysis

<!-- BEGIN FILE: small-rna-seq/mirdeep2-analysis/SKILL.md -->
---
name: bio-small-rna-seq-mirdeep2-analysis
description: Discovers novel miRNAs and quantifies known miRNAs with miRDeep2 by scoring genome-mapped read stacks against the Dicer/Drosha biogenesis signature. Use when deciding whether a study needs de novo discovery at all versus known-miRNA quantification; choosing the species and related-species miRBase references; reading the miRDeep2 score as a signal-to-noise hypothesis rather than a fixed cutoff; or filtering novel candidates against tRNA/rRNA loci to reject the classic false positives.
tool_type: cli
primary_tool: miRDeep2
---

## Version Compatibility

Reference examples tested with: miRDeep2 2.0.1.3+, bowtie 1.3+ (NOT bowtie2), ViennaRNA 2.5+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# miRDeep2 Analysis

**"Discover novel miRNAs from my small RNA-seq data"** -> Map collapsed reads to the genome, excise candidate hairpins, fold them, and score how well the observed read stacks match the Dicer/Drosha processing signature.
- CLI: `mapper.pl` (map to genome, emit ARF) -> `miRDeep2.pl` (discover + quantify) -> `quantifier.pl` (known-only quantification)

## The governing principle: a miRDeep2 score is a biogenesis hypothesis, not a validated miRNA

miRDeep2 does not detect miRNAs by sequence; it asks whether the reads piled on a genomic hairpin look like the product of Dicer/Drosha processing: a sharp, abundant MATURE arm, a lower-abundance STAR (passenger) arm with the correct ~2-nt 3' overhang geometry, a depleted loop, and a thermodynamically stable fold whose minimum free energy is lower than shuffled controls (the randfold p-value). A log-odds model converts that fit into a score (Friedländer 2012). The decisive consequence is that any locus producing a stacked, hairpin-foldable read pile can mimic the signature, so novel discovery is intrinsically high false-positive. The textbook failure is contaminating tRNA and rRNA fragments: tRNAs fold into stable cloverleaf arms and throw sharp, abundant read stacks that score as "novel miRNAs." A high score is a structural and expression hypothesis that demands orthogonal validation, never a finding.

There is no universal score cutoff. `survey.pl` sweeps cutoffs and reports, at each, the estimated true positives, false positives, signal-to-noise ratio, and an estimated FDR derived from permuted controls; Friedländer 2012 chose, per analysis, the lowest cutoff giving signal-to-noise >= 5. Asserting "score > 10 = high confidence" as a fixed rule is folklore: read the survey output, pick a cutoff for an acceptable estimated FDR, and report it.

## Decision: is miRDeep2 the right tool?

| Goal | Use | Why |
|------|-----|-----|
| Discover NOVEL miRNAs in an animal genome | miRDeep2 (full discovery) | The dedicated probabilistic biogenesis model; genome-anchored |
| Quantify KNOWN miRNAs + isomiRs + tRFs on a supported species | mirge3-analysis | Faster, isomiR-aware; discovery machinery is expensive and high-FP |
| Quantify KNOWN miRNAs only, no discovery | `quantifier.pl` (miRDeep2) or mirge3 | Skip the discovery engine when discovery is not needed |
| Profile tRFs / piRNAs (not miRNAs) | trf-pirna-profiling | tRF/rRF stacks are miRDeep2 false positives, not the target |
| Plant small RNAs | ShortStack (see trf-pirna-profiling) | Plant hairpins and 24-nt siRNA biology break the animal model |
| Animal with NO genome assembly (non-model, single-cell) | Mirnovo (genome-free ML) | miRDeep2 is genome-anchored and cannot run without an assembly |

miRDeep2 requires a reference GENOME and bowtie 1 (not bowtie2). The species and related-species miRBase references are load-bearing: the same-species mature/hairpin define "known," and the other-species mature provides conservation evidence that raises confidence in novel calls.

## Workflow overview

```
collapsed reads (FASTA, _xN counts)
    |
    v   mapper.pl  --> bowtie align to genome, emit ARF
    v
miRDeep2.pl  --> excise hairpins, fold (RNAfold), randfold, score read stacks
    |
    v   quantifier.pl  --> known-miRNA counts (run alone if no discovery needed)
```

## Step 1: Build the genome index (bowtie 1)

```bash
# miRDeep2 uses bowtie 1, NOT bowtie2
bowtie-build genome.fa genome_index
```

## Step 2: Map reads with mapper.pl

```bash
mapper.pl reads.fastq \
    -e -h -i -j \
    -k TGGAATTCTCGGGTGCCAAGG \
    -l 18 -m \
    -p genome_index \
    -s reads_collapsed.fa \
    -t reads_vs_genome.arf \
    -v

# -e: input is FASTQ   -h: parse to FASTA   -i: convert RNA to DNA
# -j: remove reads with non-ACGTN   -k: clip 3' adapter   -l 18: discard < 18 nt
# -m: collapse identical reads   -p: bowtie index   -s/-t: collapsed FASTA + ARF
```

## Step 3: Prepare miRBase references

```bash
# miRBase distributes RNA (U) sequences; miRDeep2 needs DNA and no whitespace.
# Pin the miRBase version - accessions and sequences change between releases.
wget https://www.mirbase.org/download/mature.fa
wget https://www.mirbase.org/download/hairpin.fa

# Same-species mature + hairpin (here human, hsa) and a related species for conservation
grep -A1 '>hsa-' mature.fa | grep -v '^--$' > mature_hsa.fa
grep -A1 '>hsa-' hairpin.fa | grep -v '^--$' > hairpin_hsa.fa
grep -A1 '>mmu-' mature.fa | grep -v '^--$' > mature_mmu.fa
# Convert U->T and strip spaces if the tool's extract_miRNAs.pl is not used:
# sed '/^>/!s/U/T/g; /^>/!s/u/t/g' in.fa
```

## Step 4: Run discovery with miRDeep2.pl

```bash
miRDeep2.pl \
    reads_collapsed.fa \
    genome.fa \
    reads_vs_genome.arf \
    mature_hsa.fa \
    mature_mmu.fa \
    hairpin_hsa.fa \
    -t Human \
    2> report.log

# Positional args (ORDER is fixed): collapsed reads, genome, ARF,
#   same-species mature, other-species mature (or 'none'), same-species hairpin
# -t: species for miRBase labelling
```

## Step 5: Known-miRNA quantification only (skip discovery)

```bash
quantifier.pl \
    -p hairpin_hsa.fa \
    -m mature_hsa.fa \
    -r reads_collapsed.fa \
    -t hsa
# Output: miRNAs_expressed_all_samples_*.csv
# Note: quantifier.pl and miRDeep2.pl counts can differ (different mapping logic)
```

## Output files

| File | Description |
|------|-------------|
| result_*.csv | Ranked candidates: miRDeep2 score, randfold p, mature/star, miRBase match, estimated probability TP |
| result_*.html | Interactive report with read-stack and structure plots |
| miRNAs_expressed_all_samples_*.csv | Known-miRNA expression matrix |
| mirdeep_runs/, expression_analyses/, pdfs_*/ | Intermediate read-stack alignments (.mrd) and structures |

## Reading and filtering results

```python
import pandas as pd

def parse_mirdeep2_results(csv_path, score_cutoff):
    # score_cutoff is NOT universal: choose it from survey.pl signal-to-noise / FDR,
    # then report the value. There is no fixed 'score > 10' rule.
    df = pd.read_csv(csv_path, sep='\t', skiprows=1)
    return df[df['miRDeep2 score'] >= score_cutoff]

def reject_structured_rna_false_positives(candidates, trna_rrna_bed):
    # The classic miRDeep2 false positive is a tRNA/rRNA fragment hairpin.
    # Require: (a) no overlap with tRNA/rRNA/snoRNA loci, (b) some star-arm read
    # support, (c) reproducibility across replicates, before trusting a novel call.
    return candidates  # intersect coordinates against trna_rrna_bed with bedtools upstream
```

## Calling a novel miRNA real: the community criteria

A miRDeep2 score is a prefilter, not a verdict. A genuine novel miRNA must satisfy the community annotation criteria (Ambros 2003; MirGeneDB), and the deliverable should be a per-candidate criteria table, not a score-ranked list:
- CONSISTENT 5' processing of BOTH the mature and star arms across reads - this 5'-end homogeneity is the single most discriminating signal (a precise 5' end is what defines the seed; degradation gives smeared ends).
- A mature/star duplex with the ~2-nt 3' overhang geometry of Dicer cleavage.
- Star-arm read support (real miRNAs usually show some passenger reads).
- A ~22-nt mature length and a hairpin without large internal loops/bulges.
- Conservation or Dicer/Drosha-dependence (loss of signal on knockdown), and reproducibility across replicates.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| "novel miRNAs" cluster at tRNA/rRNA loci | Structured-RNA fragments fold into scoring hairpins | Intersect candidates against GtRNAdb/rRNA annotations and discard overlaps |
| mapper.pl fails or maps almost nothing | bowtie2 index supplied, or genome not indexed with bowtie 1 | Rebuild with `bowtie-build` (bowtie 1); confirm reads were adapter-trimmed |
| miRDeep2.pl errors on the reference FASTA | miRBase U-containing or whitespace-laden sequences | Convert U->T and strip header whitespace, or use the bundled extraction script |
| Treating score > 10 as truth | No universal cutoff exists | Use survey.pl signal-to-noise/FDR to set and report a cutoff |
| Very few known miRNAs detected | Wrong species `-t`, or reads not collapsed (`_xN`) | Set the correct species code; collapse reads in mapper.pl (`-m`) |
| Novel call has no star-arm reads | Real miRNAs usually show some passenger reads | Down-weight single-arm candidates; require duplex evidence |

## Related Skills

- smrna-preprocessing - Adapter trimming and read collapsing before mapping
- mirge3-analysis - Faster known-miRNA + isomiR quantification when discovery is not needed
- differential-mirna - Differential expression of the resulting count matrix
- trf-pirna-profiling - For tRF/piRNA biology, which would otherwise appear as miRDeep2 false positives
- genome-annotation/ncrna-annotation - Annotating tRNA/rRNA/snoRNA loci to filter false positives

## References

- Friedländer MR, Mackowiak SD, Li N, Chen W, Rajewsky N. 2012. miRDeep2 accurately identifies known and hundreds of novel microRNA genes in seven animal clades. *Nucleic Acids Res* 40:37-52. doi:10.1093/nar/gkr688
- Friedländer MR, Chen W, Adamidi C, et al. 2008. Discovering microRNAs from deep sequencing data using miRDeep. *Nat Biotechnol* 26:407-415. doi:10.1038/nbt1394
- Bonnet E, Wuyts J, Rouzé P, Van de Peer Y. 2004. Evidence that microRNA precursors, unlike other non-coding RNAs, have lower folding free energies than random sequences. *Bioinformatics* 20:2911-2917. doi:10.1093/bioinformatics/bth374
- Kozomara A, Birgaoanu M, Griffiths-Jones S. 2019. miRBase: from microRNA sequences to function. *Nucleic Acids Res* 47:D155-D162. doi:10.1093/nar/gky1141
- Fromm B, Domanska D, Høye E, et al. 2020. MirGeneDB 2.0: the metazoan microRNA complement. *Nucleic Acids Res* 48:D1172-D1180. doi:10.1093/nar/gkz885
- Ambros V, Bartel B, Bartel DP, et al. 2003. A uniform system for microRNA annotation. *RNA* 9:277-279. doi:10.1261/rna.2183803
<!-- END FILE: small-rna-seq/mirdeep2-analysis/SKILL.md -->

## 子目录：small-rna-seq/mirge3-analysis

<!-- BEGIN FILE: small-rna-seq/mirge3-analysis/SKILL.md -->
---
name: bio-small-rna-seq-mirge3-analysis
description: Quantifies known miRNAs, isomiRs, tRFs, and A-to-I editing fast with miRge3.0 by aligning collapsed reads to curated miRBase or MirGeneDB libraries. Use when choosing miRBase versus MirGeneDB as the reference; deciding whether to collapse isomiRs to the parent miRNA or keep 5'-isomiRs separate (they shift the seed and retarget); confirming the organism is among the six supported species; or remembering that RPM output is for display only and raw counts go to DESeq2/edgeR.
tool_type: python
primary_tool: miRge3
---

## Version Compatibility

Reference examples tested with: miRge3.0 0.1.4+, numpy 1.26+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `miRge3.0 annotate --help` to confirm flag names (they have drifted across versions)
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# miRge3 Analysis

**"Quantify my miRNAs and isomiRs fast"** -> Align collapsed reads to a hierarchy of curated small-RNA libraries and tabulate per-miRNA counts, isomiR variants, tRFs, and A-to-I editing.
- CLI: `miRge3.0 annotate -s sample.fastq.gz -lib LIBS -on human -db miRBase -a illumina -gff -ai -cpu 8 -o out/`

## The governing principle: miRge3 quantifies what is already known, fast, and isomiRs are biology

miRge3.0 does not do genome-wide de novo discovery as its main job; it Bowtie-aligns collapsed reads against small curated libraries (mature miRBase or MirGeneDB, hairpin, tRNA, rRNA, snoRNA, mRNA, spike-ins) hierarchically and assigns each read to the first matching class. That is why it is fast, and why it is the default for a routine differential-expression study on a supported species - and why it cannot help on an unsupported organism (it ships pre-built libraries for only six species: human, mouse, rat, zebrafish, nematode, fruitfly). For serious NOVEL discovery prefer miRDeep2; miRge3's optional `-nmir` SVM module is a convenience, not its strength.

Two judgments carry the analysis. First, isomiRs are real biology, not noise: a 5' isomiR shifts the seed (positions 2-7) and therefore the target set, so collapsing all isomiRs to the canonical miRNA can hide function - keep 5' isomiRs separate when isomiR identity is the question, and collapse to the parent only for a standard "which miRNAs changed" analysis. But the precision floor cuts the other way: low-count 3' and internal isomiRs are frequently sequencing/ligation artifacts (per-base error ~0.1-1% plus ligation bias), so filter them aggressively and demand replicate or UMI support, and trust 5' isomiRs more. A germline seed SNP (a polymiR) masquerades as an isomiR or edit; with genotypes available, fold them into the reference (e.g. OptimiR) rather than calling them isomiRs. Second, miRge3 emits both raw counts and RPM, but RPM is for display and cross-sample viewing only; differential testing takes RAW counts into DESeq2/edgeR, which model the count distribution themselves.

## Decision: miRBase vs MirGeneDB reference (`-db`)

| Reference | Size | Character | Choose when |
|-----------|------|-----------|-------------|
| miRBase (v22) | large (~1900 human miRNAs) | permissive; includes many dubious entries (mis-annotated tRFs/fragments) | maximizing recall / comparability with legacy studies |
| MirGeneDB | small (~550 human genes) | conservatively curated; every entry passes the biogenesis signature | conservative, high-confidence claims; cleaner DE feature set |

The reference choice changes results: counting against miRBase yields more "miRNA" rows, some of which are not bona fide miRNAs; against MirGeneDB the rows are fewer and defensible. miRge3 can emit both side by side - report which one a result came from, and pin the version.

## Library installation (no built-in download command)

```bash
# miRge3.0 has NO '--download-library' subcommand. Fetch the pre-built libraries from
# SourceForge and extract them, then point -lib at the extracted directory.
wget https://sourceforge.net/projects/mirge3/files/miRge3_Lib/human.tar.gz
tar -xzf human.tar.gz          # creates a 'human' library tree
# For an unsupported organism, build a custom library with the separate miRge3_build tool.
```

## Quantify known miRNAs (+ isomiRs, A-to-I)

**Goal:** Produce a per-miRNA count matrix with isomiR and editing detail for one or more samples.

**Approach:** Run `miRge3.0 annotate` with the curated library, organism, database, and adapter, switching on mirGFF3 isomiR output and A-to-I detection.

```bash
miRge3.0 annotate \
    -s sample1.fastq.gz,sample2.fastq.gz \
    -lib /path/to/miRge3_Lib \
    -on human \
    -db miRBase \
    -a illumina \
    -gff \
    -ai \
    -cpu 8 \
    -o output_dir

# -s: comma-separated FASTQs (raw or already adapter-known)
# -on: organism (human|mouse|rat|zebrafish|nematode|fruitfly)
# -db: miRBase or MirGeneDB
# -a: adapter as a name ('illumina') OR a raw sequence (e.g. TGGAATTCTCGGGTGCCAAGG)
# -gff: emit isomiR results in mirGFF3 (the community-standard isomiR format)
# -ai: A-to-I editing. A seed A->I edit RETARGETS the miRNA (inosine reads as G), and
#      mismatch-permissive alignment silently merges edited reads into the canonical
#      count - keep -ai on and treat seed edits as distinct species, not noise.
# -cpu: threads
```

## UMI and novel-miRNA options

```bash
# QIAseq UMI library: -qumi removes Qiagen PCR duplicates; -umi gives the 5',3' trim lengths
miRge3.0 annotate -s qiaseq.fastq.gz -lib LIBS -on human -db miRBase \
    -a AACTGTAGGCACCATCAAT -umi 0,12 -qumi -o out_umi

# Optional novel-miRNA prediction (SVM); needs the genome; prefer miRDeep2 for real discovery
miRge3.0 annotate -s sample.fastq.gz -lib LIBS -on human -db miRBase -a illumina -nmir -o out_novel
```

## Output files

| File | Description |
|------|-------------|
| miR.Counts.csv | Raw read counts per miRNA (this feeds DESeq2/edgeR) |
| miR.RPM.csv | RPM-normalized counts (display only, NOT for DE testing) |
| *.gff3 | isomiR variants in mirGFF3 (with `-gff`) |
| annotation.report.html / .csv | RNA-class composition and QC report |
| a2i / editing report | A-to-I editing sites and frequencies (with `-ai`) |

## Run from Python via subprocess

**Goal:** Orchestrate miRge3 from a Python pipeline and load its outputs.

**Approach:** miRge3.0 is a command-line tool with no documented Python API, so invoke it with subprocess, then read the CSV outputs with pandas.

```python
import subprocess

def run_mirge3(samples, lib_path, out_dir, organism='human', db='miRBase', adapter='illumina', threads=8):
    cmd = ['miRge3.0', 'annotate',
           '-s', ','.join(samples),
           '-lib', lib_path,
           '-on', organism,
           '-db', db,
           '-a', adapter,
           '-gff', '-ai',
           '-cpu', str(threads),
           '-o', out_dir]
    subprocess.run(cmd, check=True)
```

## Load and filter counts

**Goal:** Read the miRge3 count matrix and remove near-zero noise before downstream analysis.

**Approach:** Load `miR.Counts.csv`, then filter to miRNAs with a minimum total count (most miRBase entries are near-zero noise).

```python
import pandas as pd

def load_mirge3_counts(output_dir):
    return pd.read_csv(f'{output_dir}/miR.Counts.csv', index_col=0)

def filter_low_counts(counts, min_total=10):
    # Lower than an mRNA threshold because miRNA libraries have fewer total counts;
    # hand the SURVIVING RAW counts (not RPM) to DESeq2/edgeR for testing.
    return counts[counts.sum(axis=1) >= min_total]
```

## Aggregate isomiRs deliberately

**Goal:** Decide whether to collapse isomiRs to the parent miRNA or keep seed-shifting 5' variants separate.

**Approach:** Parse the mirGFF3 isomiR table, classify each variant by 5' vs 3' change, and aggregate to the parent only for variants that preserve the seed.

```python
def summarize_isomirs(isomir_counts):
    # 5' isomiRs shift the seed and retarget -> keep separate when isomiR identity is
    # the biology; 3' isomiRs mostly tune stability -> safe to collapse to the parent.
    # KEEP the -5p/-3p arm in the parent key: the two arms have different seeds and
    # targets and must never be merged (the dominant arm also switches across tissues).
    # .values assigns positionally - index.str.extract returns a fresh RangeIndex that
    # would otherwise misalign to all-NaN against the string index.
    isomir_counts['miRNA'] = isomir_counts.index.str.extract(r'(hsa-\w+-\d+[a-z]*(?:-[35]p)?)')[0].values
    summary = isomir_counts.groupby('miRNA').agg(
        total_reads=('count', 'sum'),
        n_isomirs=('count', 'count'),
        dominant_isomir=('count', lambda x: x.idxmax()))
    return summary
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `unrecognized arguments: --isomir` | Flag does not exist | isomiR counts are produced by default; use `-gff` for mirGFF3 output |
| `unrecognized arguments: --download-library` | No such subcommand | Download libraries from SourceForge and `tar -xzf`; point `-lib` at the tree |
| `ModuleNotFoundError: mirge3.annotate` | No documented Python API | Call the CLI with `subprocess.run([...])` |
| Empty or tiny count matrix | Wrong `-on`, wrong `-db` case, or wrong adapter | Confirm a supported species; `-db miRBase`/`MirGeneDB`; check the adapter name/sequence |
| Organism not supported | Only six species ship libraries | Build a custom library with miRge3_build, or use miRDeep2/sRNAbench |
| Inflated DE significance on tiny miRNAs | RPM fed to the DE test | Feed RAW `miR.Counts.csv`, not `miR.RPM.csv`, to DESeq2/edgeR |

## Related Skills

- smrna-preprocessing - Adapter and UMI handling; miRge3 can also trim internally
- mirdeep2-analysis - Use when de novo novel-miRNA discovery is the goal
- differential-mirna - Differential expression from the raw count matrix
- trf-pirna-profiling - Deeper tRF/piRNA analysis beyond miRge3's tRF module

## References

- Patil AH, Halushka MK. 2021. miRge3.0: a comprehensive microRNA and tRF sequencing analysis pipeline. *NAR Genom Bioinform* 3:lqab068. doi:10.1093/nargab/lqab068
- Desvignes T, Loher P, Eilbeck K, et al. 2020. Unification of miRNA and isomiR research: the mirGFF3 format and the mirtop API. *Bioinformatics* 36:698-703. doi:10.1093/bioinformatics/btz675
- Kozomara A, Birgaoanu M, Griffiths-Jones S. 2019. miRBase: from microRNA sequences to function. *Nucleic Acids Res* 47:D155-D162. doi:10.1093/nar/gky1141
- Fromm B, Domanska D, Høye E, et al. 2020. MirGeneDB 2.0: the metazoan microRNA complement. *Nucleic Acids Res* 48:D1172-D1180. doi:10.1093/nar/gkz885
- Tan GC, Chan E, Molnar A, et al. 2014. 5' isomiR variation is of functional and evolutionary importance. *Nucleic Acids Res* 42:9424-9435. doi:10.1093/nar/gku656
<!-- END FILE: small-rna-seq/mirge3-analysis/SKILL.md -->

## 子目录：small-rna-seq/smrna-preprocessing

<!-- BEGIN FILE: small-rna-seq/smrna-preprocessing/SKILL.md -->
---
name: bio-small-rna-seq-smrna-preprocessing
description: Trims kit-specific 3' adapters, strips UMIs or 4N degenerate ends, size-selects, and collapses small RNA-seq reads (miRNA, piRNA, tRF) with cutadapt or fastp. Use when choosing the kit's 3' adapter; setting the size window (18-26 nt miRNA vs 24-32 nt piRNA); deciding whether a library carries a true UMI (QIAseq) versus a 4N debiasing spacer (NEXTflex); reading the read-length histogram to judge library quality; or deciding whether to collapse identical reads before mapping.
tool_type: cli
primary_tool: cutadapt
---

## Version Compatibility

Reference examples tested with: cutadapt 4.4+, fastp 0.23+, seqkit 2.6+, umi_tools 1.1+, matplotlib 3.8+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Small RNA Preprocessing

**"Preprocess my small RNA-seq reads"** -> Remove the 3' adapter, remove any UMI or 4N degenerate bases, size-select to the target class window, and collapse identical reads to a counted FASTA before quantification or discovery.
- CLI: `cutadapt -a ADAPTER -m 18 -M 30 --discard-untrimmed` then class-specific UMI/4N handling and `seqkit rmdup -s`

## The governing principle: the insert IS its ends, so adapter handling decides everything

In small RNA-seq the molecule is shorter than the read (insert ~18-32 nt, read 50-75 nt), so the 3' adapter is sequenced through on EVERY real insert. A read with no adapter is therefore not a complete small RNA (the insert was too long, or it is an adapter dimer or junk), which inverts the genomic-DNA intuition: here `--discard-untrimmed` is the correct default, not an aggressive one. Because the insert is defined by its exact 5' and 3' ends, ligation bias never averages out the way fragmentation does in mRNA-seq: T4 RNA ligase captures some miRNA ends 10-100x more efficiently than others, so absolute, cross-miRNA abundance WITHIN a sample is not trustworthy (only the same miRNA compared ACROSS samples, where the per-sequence bias cancels, is reliable; Giraldez 2018). Preprocessing cannot fix ligation bias, but mishandling adapters, UMIs, or size windows manufactures artifacts on top of it.

The read-length histogram after trimming is the primary QC readout, not an afterthought: a sharp peak at 21-23 nt is a healthy miRNA library; a 26-32 nt peak is piRNA (expected in germline, suspicious in soma/plasma); a broad 30+ nt smear with no 22 nt peak is degradation or tRNA/rRNA-fragment contamination or failed size selection; a spike near insert length 0 is adapter dimer eating flowcell capacity. Read the histogram before trusting any downstream count. This degradation heuristic assumes a standard ligation library: for T4-PNK / PANDORA-seq / phospho-RNA-seq preps (which deliberately capture 5'-OH and cyclic-phosphate tRFs and rRFs) the heuristic INVERTS - broad ~18-35 nt tRF/rRF peaks are the expected signal, not contamination.

## Decision: how to handle the 3' end depends on the kit

| Kit | 3' adapter | Degenerate / UMI design | Preprocessing consequence |
|-----|-----------|--------------------------|----------------------------|
| Illumina TruSeq | TGGAATTCTCGGGTGCCAAGG | invariant ends (high ligation bias) | trim adapter only; do NOT PCR-dedup |
| NEBNext | AGATCGGAAGAGCACACGTCT | invariant ends | trim adapter only; do NOT PCR-dedup |
| NEXTflex (Bioo/PerkinElmer) | TGGAATTCTCGGGTGCCAAGG | 4 random nt on each adapter end (debiasing spacer) | trim adapter, then STRIP 4 nt from each insert end (`-u 4 -u -4`); the 4N is NOT a UMI, discard it |
| QIAseq miRNA | AACTGTAGGCACCATCAAT | true 12-nt UMI 3' of the adapter | EXTRACT the UMI (keep it), align, then UMI-dedup; never position-dedup |
| SMARTer / CATS (template-switching) | no ligation adapter | adds a 3' poly-A/tail, not a 4N or UMI | trim the 3' poly-tail, NOT a ligation adapter; different bias profile; ultra-low input |
| RealSeq (circularization) | single adapter, one ligation | sidesteps the two-junction ligation bias | low-input; one-ligation chemistry, not two |

The single most damaging error in this table is conflating the NEXTflex 4N debiasing spacer (only 4^4=256 combinations, must be DISCARDED) with the QIAseq 12-nt UMI (must be KEPT and used to separate PCR duplicates from biological duplicates). Using the 4N as a pseudo-UMI saturates instantly and undercounts abundant miRNAs.

## Adapter trimming with cutadapt

```bash
# Standard ligation-based small-RNA library (TruSeq adapter shown)
cutadapt \
    -a TGGAATTCTCGGGTGCCAAGG \
    -m 18 \
    -M 30 \
    -q 20 \
    --discard-untrimmed \
    -j 8 \
    -o trimmed.fastq.gz \
    input.fastq.gz

# -a: 3' adapter (cutadapt finds it even when only a prefix is sequenced)
# -m 18 / -M 30: keep the small-RNA window; -m drops adapter dimers (trim to ~0)
# -q 20: light 3' quality trim, applied BEFORE adapter removal (cutadapt orders it internally)
# --discard-untrimmed: a read with no adapter is not a complete small RNA
```

## Class-specific size windows

```bash
# miRNA-focused window (mature miRNAs cluster at 21-23 nt)
cutadapt -a TGGAATTCTCGGGTGCCAAGG -m 18 -M 26 --discard-untrimmed -o mirna.fastq.gz input.fastq.gz

# piRNA / tRNA-half window (widen -M; do not clip the very class of interest)
cutadapt -a TGGAATTCTCGGGTGCCAAGG -m 24 -M 35 --discard-untrimmed -o pirna.fastq.gz input.fastq.gz
```

## Removing 4N degenerate bases (NEXTflex / high-definition adapters)

```bash
# ORDER MATTERS: trim the adapter FIRST, then strip the 4 random nt from each insert end.
# Stripping a fixed 4 nt before adapter removal would corrupt the adapter search.
cutadapt -a TGGAATTCTCGGGTGCCAAGG -m 18 -M 30 --discard-untrimmed -o adapter_trimmed.fastq.gz input.fastq.gz
cutadapt -u 4 -u -4 -o final.fastq.gz adapter_trimmed.fastq.gz

# -u 4: remove 4 nt from the 5' end; -u -4: remove 4 nt from the 3' end (negative = 3')
```

## Extracting and using a true UMI (QIAseq)

```bash
# The 12-nt UMI sits immediately 3' of the QIAGEN adapter. Capture it into the read name,
# align, then collapse reads sharing sequence+position+UMI (PCR duplicates) but keep reads
# that differ in UMI (distinct biological molecules). Position-only dedup is WRONG for small RNA.
umi_tools extract --extract-method=regex \
    --bc-pattern='.+(?P<discard_1>AACTGTAGGCACCATCAAT)(?P<umi_1>.{12}).*' \
    -I input.fastq.gz -S umi_extracted.fastq.gz
# ... adapter-trim, map ...
umi_tools dedup --method=directional -I aligned.bam -S deduped.bam
# directional models 1-edit UMI sequencing errors; raw unique-UMI counting overcounts
```

## Using fastp as an alternative

```bash
fastp \
    --in1 input.fastq.gz \
    --out1 trimmed.fastq.gz \
    --adapter_sequence TGGAATTCTCGGGTGCCAAGG \
    --length_required 18 \
    --length_limit 30 \
    --json report.json --html report.html

# --length_limit caps the small-RNA window; do NOT use fastp --dedup on small RNA
# (it is sequence-based and deletes real biological duplicates)
```

## Collapse identical reads to a counted FASTA

```bash
# seqkit rmdup -s only DEDUPLICATES identical sequences; it does NOT append the _xN
# count that miRDeep2 needs. Use it to shrink the file, but generate the counted FASTA
# with the awk/Python helper below. For a UMI library, collapse on sequence+UMI (or skip
# collapsing) so the UMI survives dedup.
seqkit rmdup -s trimmed.fastq.gz -o dedup.fasta
```

```python
import gzip
from collections import Counter

def collapse_reads(fastq_path, lo=18, hi=30):
    counts = Counter()
    with gzip.open(fastq_path, 'rt') as f:
        while True:
            header = f.readline()
            if not header:
                break
            seq = f.readline().strip()
            f.readline()
            f.readline()
            if lo <= len(seq) <= hi:
                counts[seq] += 1
    return counts

def write_collapsed_fasta(counts, output_path):
    # miRDeep2 reads the _xN suffix as the read count; preserve it
    with open(output_path, 'w') as f:
        for i, (seq, count) in enumerate(counts.most_common()):
            f.write(f'>seq_{i}_x{count}\n{seq}\n')
```

## QC and contamination gate with miRTrace

```bash
# Run miRTrace BEFORE quantifying. Beyond length/complexity, it reports the RNA-class
# composition (miRNA vs rRNA/tRNA/artifact) AND fingerprints clade-specific miRNAs to
# detect cross-species / reagent / sample-swap contamination (found in >7% of public
# datasets) that a good genome mapping rate hides. It has kit presets via --protocol.
mirtrace qc --species hsa --protocol illumina -o mirtrace_out *.fastq.gz
# Read: a miRNA-dominant composition is healthy; rRNA/tRNA-dominant means poor size
# selection, degraded input, or low real miRNA; a foreign-clade signal flags contamination.
```

For plasma/serum specifically, hemolysis is the dominant QC: red blood cells are loaded with miR-451a, so even slight hemolysis floods the sample with erythroid miRNAs and corrupts the circulating profile. Flag it with the miR-451a (RBC-enriched, rises with hemolysis) vs miR-23a-3p (hemolysis-insensitive) relationship - an elevated miR-451a fraction (or delta-Cq(miR-23a-3p - miR-451a) > ~7 by qPCR) marks a hemolyzed sample. Exclude or model hemolyzed samples before differential analysis (see differential-mirna). Use exogenous spike-ins (cel-miR-39) for low-biomass technical normalization.

## Read the length distribution as QC

```python
import gzip
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot_length_distribution(fastq_path, out_png):
    lengths = Counter()
    with gzip.open(fastq_path, 'rt') as f:
        for i, line in enumerate(f):
            if i % 4 == 1:
                lengths[len(line.strip())] += 1
    xs = sorted(lengths)
    plt.bar(xs, [lengths[x] for x in xs])
    plt.axvspan(21, 23, color='green', alpha=0.15)  # healthy miRNA peak
    plt.xlabel('read length (nt)')
    plt.ylabel('count')
    plt.savefig(out_png)
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Almost nothing maps; reads ~50-75 nt | 3' adapter never removed (wrong sequence or step skipped) | Set the kit's exact adapter; reads must shrink to ~18-30 nt after trimming |
| Length histogram peaks at ~8 random nt over the real peak | 4N spacer not stripped after adapter removal | Add `cutadapt -u 4 -u -4` as a second pass |
| Abundant miRNAs look flat / undercounted | Position-based PCR dedup on non-UMI data, or 4N used as a UMI | Do not dedup without a real UMI; for QIAseq use `umi_tools dedup` |
| Broad 30+ nt smear, no 22 nt peak | Degraded input / tRNA-rRNA fragments / failed size selection | Inspect RNA quality (DV200, not RIN); rerun size selection; expect mostly non-miRNA classes |
| Huge spike at insert length ~0 | Adapter dimers (no-insert ligation), common at low input | `-m 18` discards them; report the dimer fraction as a library-quality flag |
| Cross-sample counts incomparable | Libraries built with different kits/protocols (bias is protocol-specific) | Never merge or compare counts across kits; rebuild with one protocol |
| High mapping rate but odd composition / foreign reads | Cross-species or reagent contamination that mapping rate hides | Run miRTrace clade fingerprinting; exclude or investigate contaminated samples |
| Good phospho/PANDORA library flagged as "degraded" | Standard length-histogram heuristic applied to a 5'-OH/cP-capture prep | Expect broad ~18-35 nt tRF/rRF peaks for these preps; the heuristic inverts |
| Plasma profile dominated by a few miRNAs across all samples | Hemolysis: red-cell miR-451a contamination | Flag with miR-451a:miR-23a-3p; exclude/model hemolyzed samples; spike-in normalize |

## Related Skills

- mirdeep2-analysis - Novel miRNA discovery; consumes collapsed reads
- mirge3-analysis - Fast known-miRNA + isomiR quantification; has its own trimming
- trf-pirna-profiling - tRF and piRNA profiling, where wider size windows and 5'-OH/cP end chemistry matter
- read-qc/adapter-trimming - General adapter trimming concepts and tool behavior
- read-qc/umi-processing - UMI extraction and deduplication mechanics

## References

- Martin M. 2011. Cutadapt removes adapter sequences from high-throughput sequencing reads. *EMBnet.journal* 17:10-12. doi:10.14806/ej.17.1.200
- Chen S, Zhou Y, Chen Y, Gu J. 2018. fastp: an ultra-fast all-in-one FASTQ preprocessor. *Bioinformatics* 34:i884-i890. doi:10.1093/bioinformatics/bty560
- Giraldez MD, Spengler RM, Etheridge A, et al. 2018. Comprehensive multi-center assessment of small RNA-seq methods for quantitative miRNA profiling. *Nat Biotechnol* 36:746-757. doi:10.1038/nbt.4183
- Smith T, Heger A, Sudbery I. 2017. UMI-tools: modeling sequencing errors in Unique Molecular Identifiers to improve quantification accuracy. *Genome Res* 27:491-499. doi:10.1101/gr.209601.116
- Sorefan K, Pais H, Hall AE, et al. 2012. Reducing ligation bias of small RNAs in libraries for next generation sequencing. *Silence* 3:4. doi:10.1186/1758-907X-3-4
- Kang W, Eldfjell Y, Fromm B, et al. 2018. miRTrace reveals the organismal origins of microRNA sequencing data. *Genome Biol* 19:213. doi:10.1186/s13059-018-1588-9
- Shi J, Zhang Y, Tan D, et al. 2021. PANDORA-seq expands the repertoire of regulatory small RNAs by overcoming RNA modifications. *Nat Cell Biol* 23:424-436. doi:10.1038/s41556-021-00652-7
<!-- END FILE: small-rna-seq/smrna-preprocessing/SKILL.md -->

## 子目录：small-rna-seq/target-prediction

<!-- BEGIN FILE: small-rna-seq/target-prediction/SKILL.md -->
---
name: bio-small-rna-seq-target-prediction
description: Predicts and prioritizes miRNA target genes with seed-based tools (miRanda, TargetScan, miRDB) and experimentally validated databases (miRTarBase, multiMiR). Use when deciding that a predicted target is a hypothesis not a finding; ranking by the right score (weighted context++, mirSVR, miRDB); raising confidence by intersecting predictions with inversely-correlated mRNA DE; weighing validated (CLIP/reporter) over predicted evidence; or avoiding the circular enrichment of unfiltered target lists.
tool_type: mixed
primary_tool: miRanda
---

## Version Compatibility

Reference examples tested with: miRanda 3.3a+, BioPython 1.83+, pandas 2.2+, gseapy 1.1+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# miRNA Target Prediction

**"Predict target genes for my miRNAs"** -> Generate candidate mRNA targets by seed complementarity and thermodynamics, then raise confidence with conservation, validated databases, and matched expression.
- CLI: `miranda miRNA.fa UTR.fa -sc 140 -en -20 -strict` for de novo prediction
- Python: query TargetScan/miRDB downloads and miRTarBase for validated interactions

## The governing principle: a predicted target is a hypothesis, not a finding

Seed-based prediction has a false-positive rate near 50% even for conserved sites (Pinzon 2017), because a 6mer seed match occurs by chance roughly once per 4 kb of sequence, so a multi-kb 3' UTR carries many spurious matches. It also has a RECALL problem in the opposite direction: AGO-CLIP and CLASH show that roughly 60% of real interactions are noncanonical, and the bulged, seedless, and 3'-compensatory sites among them are missed entirely by seed-only tools (3'-supplementary sites keep a canonical seed and are still found), so a clean seed list is incomplete, not just imprecise (Helwak 2013). Worse, a single miRNA represses most of its real targets only modestly - typically less than two-fold at the protein level (Baek 2008; Selbach 2008) - so miRNAs are rheostats, not switches, and large single-target claims should be distrusted. The decisive move is therefore not running more predictors (five seed-based tools agreeing is pseudo-replication, not independent evidence) but climbing an evidence ladder and, above all, intersecting predictions with INVERSELY-correlated differentially expressed mRNA or protein from the SAME samples. Prediction proposes; expression disposes.

| Evidence tier (low to high) | What it means |
|------------------------------|----------------|
| seed match alone | weakest; common by chance |
| + conservation (TargetScan PCT) | precision up, recall down (misses species-specific targets) |
| + multiple independent tools / ML (miRDB) | modestly higher precision |
| + AGO-CLIP footprint | the miRNA's complex bound there (but CLIP is cell-type/state-specific - a peak from another tissue is weak evidence) |
| + CLASH/CLEAR-CLIP chimera | direct miRNA-target duplex |
| + anti-correlated matched miRNA/mRNA(protein) DE | functional in YOUR system |
| + reporter / seed-mutation rescue (miRTarBase "strong") | causal, gold standard |

## Decision: which predictor, and how it scores

| Tool | Scoring philosophy | Use for | Caveat |
|------|--------------------|---------|--------|
| TargetScan (context++) | conservation + 14-feature regression of repression | conserved-site prioritization | v7 = context++; v8 = a different Kd/biochemical model |
| miRanda + mirSVR | thermodynamic alignment + expression-trained regression | non-conserved / non-canonical sites | permissive; tune thresholds |
| miRDB / MirTarget | ML (SVM) on CLIP + overexpression data | data-driven ranking (score 0-100) | score >= 80 is the conventional high-confidence cut |
| RNAhybrid | pure MFE hybridization, no seed constraint | exploratory, no-seed sites | most false positives without filters |
| miRTarBase / TarBase (ENCORI) | experimentally validated interactions | the gold tier; anchor claims here | "less strong" CLIP/NGS entries are not individually validated |
| multiMiR | unifies predicted + validated sources | one-call aggregation | inherits each source DB's errors |

## De novo prediction with miRanda

**Goal:** Predict miRNA-mRNA target sites by complementarity and duplex energy.

**Approach:** Align miRNA sequences against 3' UTRs with a minimum score and a maximum (negative) energy, requiring strict seed pairing.

```bash
miranda miRNA.fa UTRs.fa -sc 140 -en -20 -strict -out predictions.txt

# -sc 140: minimum alignment score (keep alignments with score >= 140; default 140)
# -en -20: maximum free energy in kcal/mol (keep energies <= -20; value is negative)
# -strict: require canonical seed pairing at positions 2-8 (no gaps/wobble in seed)
# Tunable: many use -sc 150 / -en -7 (looser) up to -sc 155 / -en -20 (stringent)
```

## Parse miRanda output

**Goal:** Extract interaction records into a DataFrame.

**Approach:** Read the lines miRanda prefixes with '>' (per-hit summary) and pull miRNA, target, score, and energy.

```python
import pandas as pd

def parse_miranda(output_file):
    rows = []
    with open(output_file) as f:
        for line in f:
            if line.startswith('>') and not line.startswith('>>'):
                p = line.strip().split('\t')
                if len(p) >= 5:
                    rows.append({'mirna': p[0].lstrip('>'), 'target': p[1],
                                 'score': float(p[2]), 'energy': float(p[3])})
    return pd.DataFrame(rows)
```

## TargetScan context-scores lookup

**Goal:** Retrieve conserved-site predictions and rank a miRNA's targets.

**Approach:** Read the downloadable per-site context-scores file and rank by the weighted context++ score (more negative = stronger predicted repression across the whole UTR).

```python
import pandas as pd

def query_targetscan(mirbase_id, ts_file='Predicted_Targets_Context_Scores.default_predictions.txt'):
    # Verified column names: the miRNA column is 'Mirbase ID' (NOT 'miRNA family'),
    # the gene column is 'Gene ID', and 'weighted context++ score' aggregates a UTR's sites.
    df = pd.read_csv(ts_file, sep='\t')
    hits = df[df['Mirbase ID'] == mirbase_id]
    return hits.sort_values('weighted context++ score')   # ascending: most negative first
```

## miRDB (machine-learning) lookup

**Goal:** Retrieve ML-based target predictions above the conventional confidence cut.

**Approach:** Read the miRDB prediction download and keep targets with score >= 80.

```python
def query_mirdb(mirna_id, mirdb_file='miRDB_v6.0_prediction_result.txt'):
    df = pd.read_csv(mirdb_file, sep='\t', header=None, names=['mirna', 'refseq', 'score'])
    hits = df[df['mirna'] == mirna_id]
    return hits[hits['score'] >= 80].sort_values('score', ascending=False)
```

## Validated targets and unified lookup

**Goal:** Anchor target claims in experimental evidence rather than prediction.

**Approach:** Query miRTarBase for validated interactions and weight by evidence type; use multiMiR (R) to unify predicted and validated sources in one call.

```python
def get_validated_targets(mirna, mirtarbase_file='miRTarBase_MTI.xlsx'):
    df = pd.read_excel(mirtarbase_file)
    hits = df[df['miRNA'] == mirna]
    # 'Support Type' separates strong (reporter/western/qPCR) from less-strong (CLIP/NGS)
    return hits[['Target Gene', 'Experiments', 'Support Type']]
```

## The confidence move: intersect with anti-correlated mRNA DE

**Goal:** Keep only targets that behave functionally in the actual experiment.

**Approach:** Intersect predicted (or CLIP-supported) targets of UP miRNAs with DOWN mRNAs from matched samples; note the blind spot that translation-only targets may not move at the mRNA level.

```python
def functional_targets(predicted_targets, mrna_de, mirna_direction):
    # mrna_de: DataFrame with index = gene, column 'log2FC' from matched mRNA-seq.
    # Anti-correlation: an UP miRNA should repress -> targets DOWN (and vice versa).
    # Blind spot: miRNAs also act translationally, so some real targets stay flat at
    # the mRNA level (need ribosome profiling / proteomics to see those).
    want_down = mirna_direction == 'up'
    moved = mrna_de[(mrna_de['log2FC'] < 0) == want_down].index
    return [g for g in predicted_targets if g in set(moved)]
```

## Seed match analysis and site types

**Goal:** Locate seed matches in a UTR and classify site strength.

**Approach:** The seed is miRNA positions 2-7; a site is the reverse complement of the seed in the 3' UTR. Canonical sites by decreasing efficacy: 8mer > 7mer-m8 > 7mer-A1 > 6mer.

```python
from Bio.Seq import Seq

def find_seed_matches(mirna_seq, utr_seq):
    # 7mer-m8 site = reverse complement of miRNA positions 2-8 found in the UTR
    seed = str(Seq(mirna_seq)[1:8])
    site = str(Seq(seed).reverse_complement())
    matches, start = [], 0
    while True:
        pos = utr_seq.find(site, start)
        if pos == -1:
            break
        matches.append(pos)
        start = pos + 1
    return matches
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `KeyError: 'miRNA family'` on TargetScan file | Wrong column name for the context-scores file | The miRNA column is `Mirbase ID`; rank by `weighted context++ score` |
| Hundreds of "targets", almost none real | Treating seed prediction as truth | Intersect with anti-correlated mRNA DE; anchor in miRTarBase strong evidence |
| Every miRNA "regulates cancer pathways" | Enrichment on an unfiltered predicted target list (circular) | Build the list from validated/CLIP or expression-filtered targets before enrichment |
| Five tools "agree" so a target is trusted | All five use the seed (pseudo-replication) | Require an orthogonal evidence tier (CLIP/validated/expression), not more seed tools |
| A strong single-target claim | miRNAs repress most targets < 2-fold | Treat large single-target effects skeptically; demand validation |
| ceRNA/sponge mechanism asserted | Stoichiometry usually too low to matter (Denzler) | Require absolute abundance (miRNA copies vs added sites) before accepting it |

## Related Skills

- differential-mirna - Source of the DE miRNAs to predict targets for
- pathway-analysis/go-enrichment - Enrich a target list (only after evidence-filtering)
- database-access/entrez-fetch - Fetch UTR/gene sequences and identifiers
- clip-seq/ago-clip-mirna-targets - AGO-CLIP / CLASH direct target evidence

## References

- Agarwal V, Bell GW, Nam JW, Bartel DP. 2015. Predicting effective microRNA target sites in mammalian mRNAs. *eLife* 4:e05005. doi:10.7554/eLife.05005
- Betel D, Koppal A, Agius P, Sander C, Leslie C. 2010. Comprehensive modeling of microRNA targets predicts functional non-conserved and non-canonical sites. *Genome Biol* 11:R90. doi:10.1186/gb-2010-11-8-r90
- Chen Y, Wang X. 2020. miRDB: an online database for prediction of functional microRNA targets. *Nucleic Acids Res* 48:D127-D131. doi:10.1093/nar/gkz757
- Huang HY, Lin YC, Cui S, et al. 2022. miRTarBase update 2022: an informative resource for experimentally validated miRNA-target interactions. *Nucleic Acids Res* 50:D222-D230. doi:10.1093/nar/gkab1079
- Ru Y, Kechris KJ, Tabakoff B, et al. 2014. The multiMiR R package and database: integration of microRNA-target interactions. *Nucleic Acids Res* 42:e133. doi:10.1093/nar/gku631
- Pinzón N, Li B, Martinez L, et al. 2017. microRNA target prediction programs predict many false positives. *Genome Res* 27:234-245. doi:10.1101/gr.205146.116
- Baek D, Villén J, Shin C, et al. 2008. The impact of microRNAs on protein output. *Nature* 455:64-71. doi:10.1038/nature07242
- Selbach M, Schwanhäusser B, Thierfelder N, et al. 2008. Widespread changes in protein synthesis induced by microRNAs. *Nature* 455:58-63. doi:10.1038/nature07228
- Helwak A, Kudla G, Dudnakova T, Tollervey D. 2013. Mapping the human miRNA interactome by CLASH reveals frequent noncanonical binding. *Cell* 153:654-665. doi:10.1016/j.cell.2013.03.043
- Denzler R, Agarwal V, Stefano J, Bartel DP, Stoffel M. 2014. Assessing the ceRNA hypothesis with quantitative measurements of miRNA and target abundance. *Mol Cell* 54:766-776. doi:10.1016/j.molcel.2014.03.045
<!-- END FILE: small-rna-seq/target-prediction/SKILL.md -->

## 子目录：small-rna-seq/trf-pirna-profiling

<!-- BEGIN FILE: small-rna-seq/trf-pirna-profiling/SKILL.md -->
---
name: bio-small-rna-seq-trf-pirna-profiling
description: Profiles non-miRNA small RNAs - tRNA-derived fragments (tRFs/tsRNAs), piRNAs, and rRNA/snoRNA-derived species - with MINTmap, unitas, SPORTS, and proTRAC. Use when annotating all small-RNA classes in a library; quantifying tRFs at locus resolution where tRNA loci are redundant (exclusive vs ambiguous); testing the piRNA ping-pong signature; deciding whether a species is a processed functional RNA or a degradation fragment; or judging whether the prep could even capture 5'-OH/cyclic-phosphate classes.
tool_type: mixed
primary_tool: MINTmap
---

## Version Compatibility

Reference examples tested with: MINTmap 2.0+, unitas 1.7+, SPORTS1.0, proTRAC 2.4+, Python 3.10+ (numpy 1.26+, pandas 2.2+)

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# tRF and piRNA Profiling

**"Profile the tRFs and piRNAs in my small RNA-seq"** -> Annotate every small-RNA class, quantify tRNA-derived fragments at locus resolution, and test whether a piRNA population is real and active.
- CLI: `MINTmap` (tRFs), `unitas` / `SPORTS1.0` (all classes), `proTRAC` (piRNA clusters)

## The governing principle: small RNA-seq is a size cut over 8+ classes, and the kit decides what is captured

A small-RNA library is a ~18-40 nt size selection that pools miRNAs, piRNAs, endo-siRNAs, tRNA-derived fragments, rRNA-derived fragments, snoRNA-derived RNAs, and Y-RNA fragments - treating the output as "a miRNA dataset" is the field's most common error. Two facts dominate the analysis. First, end chemistry decides capture: standard TruSeq-style ligation requires a 5'-monophosphate and a 3'-OH, so 5'-OH and 2',3'-cyclic-phosphate species (angiogenin-cleaved tRNA halves, many tRFs and rRFs) are SILENTLY ABSENT, not lowly expressed - their absence in a TruSeq library is an assay artifact until proven otherwise, and capturing them needs T4 PNK pre-treatment (cP-RNA-seq / PANDORA-seq). Second, detection is not function: any abundant structured RNA sheds breakdown products into the 18-40 nt window, so high read count proves nothing. Functionality must be EARNED by precise reproducible ends, strand bias, phasing, the piRNA ping-pong signature, or AGO/PIWI loading - and database membership (piRBase, MINTbase) is annotation, not proof.

Multimapping is the other defining hazard: tRNA and piRNA loci are highly redundant (many genomic copies), so a read often cannot be assigned to one locus. This is why tRF tools report EXCLUSIVE versus AMBIGUOUS counts, and why piRNAs are quantified at the cluster/family level rather than per sequence.

Two end-chemistry and biogenesis facts change piRNA conclusions specifically. piRNAs (and plant miRNAs) carry a 3' 2'-O-methyl (HENMT1) that suppresses standard 3'-adapter ligation, so they are systematically UNDER-counted - low piRNA yield can be a 3'-end-chemistry artifact, not low abundance. And the ping-pong signature evidences the SECONDARY (slicer-driven, transposon) pathway only: primary piRNAs are PHASED (1U, Zucchini-dependent trail biogenesis), not ping-pong, and adult mammalian testis is >95% pachytene piRNAs that are repeat-depleted and largely non-transposon. A flat ping-pong z-score therefore does NOT mean "no piRNAs" - test phasing as well.

## Decision: which tool for which class

| Goal | Tool | Why |
|------|------|-----|
| tRFs/tsRNAs at locus resolution | MINTmap | deterministic, mapping-free; separates exclusive vs ambiguous tRF reads; MINTplate license-plate IDs |
| All small-RNA classes annotated hierarchically | unitas or sRNAbench | universal annotation (miRNA/piRNA/tRF/rRF/snoRNA) across ~800 species |
| tRF + rRF-centric biology (sperm/stress/aging) | SPORTS1.0 | finer tRF/rRF classification than miRNA-centric tools |
| piRNA clusters and ping-pong | proTRAC (+ a ping-pong test) | probabilistic cluster detection from mapped reads |
| Plant small RNAs (24-nt siRNA, phasiRNA) | ShortStack | DicerCall, phasing/PHAS-locus detection; animal tools misperform on plants |
| Known miRNAs only | mirge3-analysis | wrong tool for tRFs/piRNAs; miRNA-specific |

## tRF quantification with MINTmap

```bash
# MINTmap maps trimmed reads against a tRNA-space lookup and emits two tables:
# EXCLUSIVE tRFs (reads that map only within tRNA space) and AMBIGUOUS tRFs.
# Trust exclusive counts; ambiguous reads are shared with non-tRNA loci.
MINTmap -f trimmed.fastq -p sample_out
# Outputs: sample_out-MINTmap_v2-exclusive-tRFs.expression.txt
#          sample_out-MINTmap_v2-ambiguous-tRFs.expression.txt
# tRF type (tRF-5/tRF-3/tRF-1/i-tRF/tRNA-half) and the source tRNA are reported per row.
```

The tRF subtype carries a biogenesis tell: tRF-1 comes from the pre-tRNA 3' trailer (RNase Z/ELAC2, ending at the Pol III terminator), tRF-3 includes the post-transcriptional CCA (a marker of mature-tRNA origin), and tRNA halves are angiogenin-cleaved and stress-induced. Mitochondrially-encoded tRFs (mse-tRFs) are lost or misassigned if reads are mapped only to the nuclear genome.

## All-class annotation with unitas

```bash
# Hierarchical annotation: each read assigned to the first matching class.
# Reading the class composition is the first interpretation step.
unitas -input trimmed.fastq -species human
# Output: a UNITAS folder with per-class read fractions (miRNA / piRNA / tRF / rRF / snoRNA / ...)
```

## piRNA cluster detection with proTRAC

```bash
# Map reads (e.g. with sRNAmapper/bowtie), then call clusters probabilistically.
proTRAC_2.4.4.pl -genome genome.fa -map reads.map -format SAM
# A real primary-piRNA cluster shows strand asymmetry, 1U bias, and phased 3' ends.
```

## Test the ping-pong signature (is this an active piRNA pathway?)

**Goal:** Decide whether a putative piRNA population shows the slicer-driven ping-pong amplification signature.

**Approach:** For sense/antisense read pairs, count 5'-5' overlaps; an active pathway shows a sharp excess at exactly 10 nt (with 1U on primary and 10A on secondary piRNAs).

```python
import numpy as np
from collections import defaultdict

def ping_pong_zscore(plus_5p, minus_5p, max_overlap=30):
    # plus_5p / minus_5p: dict mapping genomic 5' coordinate -> read count, per strand.
    # A sense read at position i and an antisense read whose 5' end sits at i+overlap-1
    # overlap by 'overlap' nt at their 5' ends. Score the overlap histogram; a 10-nt
    # spike (z >> 0) is the ping-pong signature, evidence of an active piRNA pathway.
    hist = np.zeros(max_overlap + 1)
    for pos, n in plus_5p.items():
        for overlap in range(1, max_overlap + 1):
            partner = pos + overlap - 1
            if partner in minus_5p:
                hist[overlap] += n * minus_5p[partner]
    others = np.concatenate([hist[1:10], hist[11:]])
    z10 = (hist[10] - others.mean()) / (others.std() + 1e-9)
    return hist, z10


def phasing_zscore(same_strand_5p, period=27, max_dist=60):
    # Primary piRNAs are produced head-to-tail, so adjacent SAME-strand 5' ends are
    # spaced ~one piRNA length apart. Score the 5'-to-5' distance histogram: a peak at
    # the modal piRNA length (~26-28 nt) is the phasing signal (the primary-pathway
    # complement to ping-pong; proTRAC reports it natively). Test BOTH, not just ping-pong.
    pos = sorted(same_strand_5p)
    hist = np.zeros(max_dist + 1)
    for a in pos:
        for d in range(1, max_dist + 1):
            if (a + d) in same_strand_5p:
                hist[d] += same_strand_5p[a] * same_strand_5p[a + d]
    others = np.delete(hist[1:], period - 1)
    zp = (hist[period] - others.mean()) / (others.std() + 1e-9)
    return hist, zp
```

## Separate functional species from degradation

**Goal:** Avoid reporting random tRNA/rRNA breakdown as regulatory small RNAs.

**Approach:** Require end precision (a sharp, reproducible 5' terminus across replicates), strand bias, and class-appropriate length modality before trusting a non-miRNA species; rRFs are the hardest case because rRNA is so abundant that even tiny decay yields huge counts.

```python
def end_precision(read_5p_positions):
    # read_5p_positions: list of 5' coordinates for reads at a candidate locus.
    # A processed species has a dominant 5' end; random decay gives a smeared
    # distribution. Fraction of reads at the modal 5' end is a cheap discriminator.
    from collections import Counter
    c = Counter(read_5p_positions)
    return max(c.values()) / sum(c.values())   # near 1.0 = precise; low = decay-like
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| "No tRNA halves / no tRFs" from a TruSeq library | 5'-OH / 2',3'-cyclic-phosphate ends are not ligatable | Absence is an assay artifact; use T4 PNK prep (cP-RNA-seq/PANDORA-seq) to capture them |
| tRF counts unstable across samples | Counting ambiguous (multimapped) tRF reads | Use MINTmap EXCLUSIVE counts; report ambiguous separately |
| Abundant "piRNAs" in a somatic/plasma sample | piRBase match by chance (often tRFs or Y-RNA fragments) | piRNAs are scarce in soma; require ping-pong/phasing, not database membership |
| Huge rsRNA counts called a discovery | rRNA is so abundant that minor decay dominates | Demand end precision and reproducibility before treating an rRF as a species |
| Plant data gives few "miRNAs" | Animal tools misread 24-nt siRNA / phasiRNA biology | Use ShortStack with DicerCall and phasing |
| Ping-pong test is flat | No active SECONDARY pathway, or primary/pachytene piRNAs (which are phased, not ping-pong) | Test phasing too; flat ping-pong does not mean no piRNAs (testis is >95% pachytene/phased) |
| Low piRNA yield despite a capable prep | 3' 2'-O-methyl blocks standard adapter ligation | Treat low piRNA counts as a possible end-chemistry artifact; use periodate/2'-OMe-tolerant chemistry |

## Related Skills

- smrna-preprocessing - Wider size windows and end chemistry that determine class capture
- mirdeep2-analysis - tRF/rRF stacks are miRDeep2 false positives; this skill targets them instead
- mirge3-analysis - Known miRNAs (and a basic tRF module)
- differential-mirna - The same count-based DE framework applies to tRF/piRNA matrices
- genome-annotation/ncrna-annotation - tRNA/rRNA/snoRNA locus annotation underlying these tools

## References

- Loher P, Telonis AG, Rigoutsos I. 2017. MINTmap: fast and exhaustive profiling of nuclear and mitochondrial tRNA fragments from short RNA-seq data. *Sci Rep* 7:41184. doi:10.1038/srep41184
- Pliatsika V, Loher P, Magee R, et al. 2018. MINTbase v2.0: a comprehensive database for tRNA-derived fragments. *Nucleic Acids Res* 46:D152-D159. doi:10.1093/nar/gkx1075
- Gebert D, Hewel C, Rosenkranz D. 2017. unitas: the universal tool for annotation of small RNAs. *BMC Genomics* 18:644. doi:10.1186/s12864-017-4031-9
- Shi J, Ko EA, Sanders KM, Chen Q, Zhou T. 2018. SPORTS1.0: a tool for annotating and profiling non-coding RNAs optimized for rRNA- and tRNA-derived small RNAs. *Genomics Proteomics Bioinformatics* 16:144-151. doi:10.1016/j.gpb.2018.04.004
- Rosenkranz D, Zischler H. 2012. proTRAC - a software for probabilistic piRNA cluster detection, visualization and analysis. *BMC Bioinformatics* 13:5. doi:10.1186/1471-2105-13-5
- Brennecke J, Aravin AA, Stark A, et al. 2007. Discrete small RNA-generating loci as master regulators of transposon activity in Drosophila. *Cell* 128:1089-1103. doi:10.1016/j.cell.2007.01.043
- Shi J, Zhang Y, Tan D, et al. 2021. PANDORA-seq expands the repertoire of regulatory small RNAs by overcoming RNA modifications. *Nat Cell Biol* 23:424-436. doi:10.1038/s41556-021-00652-7
<!-- END FILE: small-rna-seq/trf-pirna-profiling/SKILL.md -->

<!-- END CATEGORY: small-rna-seq -->

