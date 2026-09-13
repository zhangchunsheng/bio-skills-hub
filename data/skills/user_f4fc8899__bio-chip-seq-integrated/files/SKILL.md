---
slug: bio-chip-seq-integrated
version: 1.0.1
displayName: "ChIP-seq分析 / ChIP-seq analysis"
name: bio-chip-seq-integrated
summary: "中文：ChIP-seq分析综合技能，整合 12 个相关专题，覆盖ChIP-seq分析：峰调用、峰注释、差异结合、motifs分析、超增强子、染色质状态分割。 English: Integrated ChIP-seq analysis skill covering 12 related topics, including ChIP-seq analysis: peak calling, peak annotation, differential binding, motif analysis, super-enhancers, chromatin state segmentation."
description: "中文：这是一个面向ChIP-seq分析的综合生物信息学 Skill，整合当前分类下 12 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：ChIP-seq分析：峰调用、峰注释、差异结合、motifs分析、超增强子、染色质状态分割。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：ChIPseeker, ChromHMM, DiffBind。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for ChIP-seq analysis, combining 12 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers ChIP-seq analysis: peak calling, peak annotation, differential binding, motif analysis, super-enhancers, chromatin state segmentation. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: ChIPseeker, ChromHMM, DiffBind. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# chip-seq 分类 Skill 整合版

> 本文件整合同一主分类目录下 12 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: chip-seq -->

## 子目录：chip-seq/allele-specific-binding

<!-- BEGIN FILE: chip-seq/allele-specific-binding/SKILL.md -->
---
name: bio-chipseq-allele-specific-binding
description: Detects allele-specific transcription factor or histone modification binding from heterozygous-variant ChIP-seq using WASP (reference-bias filter; mandatory upstream), RASQUAL (joint QTL + bias-corrected testing), BaalChIP (Bayesian beta-binomial with copy-number-aware overdispersion), and AlleleSeq (personalized diploid genome). Handles imprinted-locus awareness, X-inactivation artifacts, cancer copy-number imbalance, and integration with downstream caQTL / bQTL mapping. Use when identifying variants with allelic effects on TF binding, fine-mapping causal regulatory variants, validating deep-learning variant predictions, or characterizing cis-acting regulatory effects.
tool_type: mixed
primary_tool: WASP
---

## Version Compatibility

Reference examples tested with: WASP 0.3.4+, RASQUAL 1.1+, BaalChIP 1.30+ (Bioconductor), AlleleSeq 2.0+, samtools 1.19+, bcftools 1.19+, GATK 4.5+, pysam 0.22+.

# Allele-Specific Binding (ASB)

**"Identify variants that affect transcription factor or histone modification binding in cis"** -> Compare ChIP-seq read counts at the reference and alternate alleles of heterozygous variants in a single sample. Differential read counts (ALT vs REF at hetSNPs in peaks) reveal allele-specific binding.

- CLI (mandatory bias filter): WASP `mapping pipeline` to remove reference-allele mapping bias
- CLI (joint association): RASQUAL for cis-QTL + ASB (genotype VCF piped in via tabix)
- R (Bayesian beta-binomial): BaalChIP with copy-number-aware overdispersion
- CLI (personalized genome): AlleleSeq with phased diploid genome
- Statistical test: beta-binomial likelihood ratio or chi-squared on count tables

ASB analysis has three universal pitfalls: reference-allele mapping bias (universal across short-read aligners), imprinted loci (constitutively allele-skewed by biology), and copy-number variation (changes effective allele dose). All three must be addressed or results are unreliable.

## Method Taxonomy

| Method | Year | Approach | Strength | Fails when |
|--------|------|----------|----------|------------|
| **WASP** (van de Geijn 2015) | 2015 | Map reads, swap alleles, re-map, drop discordant | Universal first step; aligner-agnostic; mandatory preprocessing | Drops 22-31% of reads; reduces power; not an analysis method itself |
| **RASQUAL** (Kumasaka 2016) | 2016 | Joint genotype-phenotype association with per-feature `phi` bias parameter | Improves QTL mapping; integrates bias correction; works for ChIP/ATAC/RNA-seq | Computationally intensive; assumes binomial bias structure |
| **BaalChIP** (de Santiago 2017) | 2017 | Bayesian beta-binomial; copy-number-aware overdispersion | Cancer genomes (copy-number imbalance); rigorous inference | Slower; assumes copy-number known |
| **AlleleSeq** (Rozowsky 2011) | 2011 | Personalized diploid genome alignment | Avoids reference bias completely; conceptually cleanest | Requires phased genotype + diploid genome construction; computational cost |
| **MBASED** (Mayba 2014) | 2014 | Meta-analysis-based ASE; gene-level | RNA-seq oriented; adapted for ChIP gene-body binning | Gene-level not peak-level; less precise for narrow TF peaks |
| **AllelicImbalance** (R package) | — | Bioconductor multi-method | Easy R workflow | Requires variants and BAM; less rigorous than BaalChIP |
| **deepSEA / chromBPNet variant effects** | 2015 / 2024 | Deep-learning predictions | Sequence-only; no chromatin sample needed | Predictive not measurement; see chip-deep-learning |

## Universal First Step: WASP Reference-Bias Filter

**Goal:** Remove reads that show reference-allele mapping bias before any ASB testing.

**Approach:** Align reads, identify those overlapping heterozygous SNPs, swap alleles and re-align; reads that don't map consistently to the same position with both alleles are discarded. The output is a bias-corrected BAM at the cost of 22-31% read loss.

Reference-allele mapping bias is systematic: reads with the reference allele align more readily because the reference is the alignment target. This inflates REF allele frequency by 1-5% genome-wide. WASP fixes this:

```bash
# WASP mapping pipeline
# 1. Initial alignment
bowtie2 -x hg38 -1 R1.fq -2 R2.fq -S step1.sam
samtools view -bS step1.sam | samtools sort -o step1.bam
samtools index step1.bam

# 2. Identify reads overlapping hetSNPs; swap alleles; re-map
python /path/to/WASP/mapping/find_intersecting_snps.py \
    --is_paired_end \
    --is_sorted \
    --output_dir wasp_out/ \
    --snp_tab snps_tab.h5 \
    --snp_index snps_index.h5 \
    --haplotype haplotypes.h5 \
    --samples sample_list.txt \
    step1.bam

# 3. Re-map swapped reads
bowtie2 -x hg38 -1 wasp_out/step1.remap.fq.gz -S step2.sam
# (process step2.sam similarly)

# 4. Filter reads that don't map back consistently
python /path/to/WASP/mapping/filter_remapped_reads.py \
    step1.to.remap.bam step2.bam step1.keep.bam

# 5. Final WASP-filtered BAM (use this for all downstream ASB analysis)
samtools sort -o step1.wasp.bam step1.keep.bam
samtools index step1.wasp.bam
```

**WASP always drops 22-31% of reads.** This is the cost of bias correction; downstream power is reduced but ASB calls are trustworthy.

**Alternative to WASP filter:** RASQUAL's `phi` parameter models bias within the test rather than filtering reads. More sophisticated but assumes binomial bias structure.

## Workflow: BaalChIP (Recommended for Cancer / Copy-Number-Imbalanced Samples)

```r
library(BaalChIP)
library(BSgenome.Hsapiens.UCSC.hg38)

# Sample metadata
samples <- data.frame(
    SampleID = c('HCC1395_FOXA1_rep1', 'HCC1395_FOXA1_rep2'),
    Tissue = 'TNBC',
    Target = 'FOXA1',
    BAM = c('rep1.wasp.bam', 'rep2.wasp.bam'),
    Peaks = c('rep1_peaks.bed', 'rep2_peaks.bed'),
    Group = 'HCC1395'
)

# hetSNP file: VCF or BED with chrom, pos, ref, alt, allele frequencies
hetSNPs <- 'het_snps.bed'

# CNV file for copy-number-aware overdispersion (critical for cancer)
cnvs <- 'cnvs.bed'

# Initialize BaalChIP object
res <- BaalChIP(samplesheet = samples, hets = hetSNPs)

# Run filters and Bayesian test
res <- alleleCounts(res, min_base_quality = 10, min_mapq = 15)
res <- QCfilter(res, RegionsToFilter = list(blacklist = rtracklayer::import('blacklist_v2.bed')))
res <- mergePerGroup(res)
res <- filter1allele(res)
res <- getASB(res, Iter = 5000, conf_level = 0.95)
# Verify parameter names against the installed BaalChIP version (`?getASB`); some releases
# use `nIter` instead of `Iter`.

# Results
asb_table <- BaalChIP.report(res)
head(asb_table)
```

BaalChIP outputs per-hetSNP: allelic ratio (AR), bias-corrected ratio (Corrected.AR), a Bayesian credible interval (Bayes_lower/Bayes_upper), and the ASB call (isASB).

## Workflow: RASQUAL (Joint cis-QTL + ASB)

```bash
# Prepare input
# - BAM filtered by WASP
# - Genotype VCF (phased)
# - Peak BED

# Run RASQUAL. The genotype VCF is piped in from tabix (there is NO --vcf flag);
# options are single-dash. Inputs -y/-k/-x are BINARY files built by RASQUAL's
# txt2bin utilities (not .txt). One run per feature: -j selects the feature row,
# -l = number of test (cis) SNPs, -m = number of feature SNPs in the window.
tabix genotypes.vcf.gz chr:start-end | \
  rasqual -y Y.bin -k K.bin -x X.bin \
    -n N_samples -j FEATURE_INDEX -l N_TEST_SNPS -m N_FEATURE_SNPS \
    -s EXON_STARTS -e EXON_ENDS -f PEAK_ID \
    > rasqual_results.txt

# Output columns: chrom, peak_id, n_RSNPs, n_FSNPs, n_imputed, summarized_phi,
#                 summarized_overdispersion, summarized_pi, beta, log10_BF, ...
```

RASQUAL's `phi` parameter is the per-feature bias estimate; `pi` is the allelic ratio.

## Workflow: AlleleSeq (Personalized Diploid Genome)

```bash
# Build personalized diploid genome from phased VCF
java -jar vcf2diploid.jar -id SAMPLE -chr hg38.fa -vcf SAMPLE.phased.vcf   # per-haplotype FASTAs written to CWD (no -outDir option)

# Align reads to both maternal and paternal copies
bowtie2-build personalized/maternal.fa maternal_index
bowtie2-build personalized/paternal.fa paternal_index
bowtie2 -x maternal_index -1 R1.fq -2 R2.fq -S maternal.sam
bowtie2 -x paternal_index -1 R1.fq -2 R2.fq -S paternal.sam

# AlleleSeq2 pipeline (Makefile-based; there is no AlleleSeq2.pl entry point)
make -f PIPELINE.mk PGENOME_DIR=personalized/ REFGENOME_VERSION=GRCh38 ALIGNMENT_MODE=ASB NTHR=8

# Output: per-hetSNP allelic counts and binomial test
```

Personalized genome avoids reference bias by construction. Cost: per-sample diploid genome generation and indexing.

## Three Universal Pitfalls

### Pitfall 1: Imprinted Loci Are Constitutively Skewed

Imprinted loci (H19, IGF2, MEG3, MEG8, KCNQ1OT1, etc.) show extreme allele bias by biology, not from differential binding.

```bash
# Filter imprinted loci before ASB analysis
# Imprinted-gene coordinates are derived from a catalog (geneimprint.com or the
# Otago Imprinted Gene Catalogue, igc.otago.ac.nz) mapped to hg38; there is no
# canonical hosted hg38 BED. Given imprinted_loci_hg38.bed:
bedtools intersect -v -a hetSNPs.bed -b imprinted_loci_hg38.bed > hetSNPs.non_imprinted.bed
```

### Pitfall 2: X-Inactivation in Females

In female samples, X-linked genes show extreme allele skew because each cell silences one X chromosome. This appears as ASB at every X-linked hetSNP.

```bash
# Filter chrX in female samples
awk '$1 != "chrX"' hetSNPs.bed > hetSNPs.autosomal.bed
# Or analyze chrX separately with imprinting-aware methods
```

### Pitfall 3: Copy-Number Imbalance (Cancer Genomes)

In cancer cells, copy-number gain of one allele alters effective allele dose; raw allelic ratios mix dose and binding effects. BaalChIP's copy-number-aware overdispersion handles this; other methods require pre-filtering CN-altered regions.

```bash
# Use ASCAT / Sequenza / FACETS to call allele-specific CNVs
# Exclude CN-altered regions from ASB analysis OR use BaalChIP
```

## Per-Tool Failure Modes

### WASP -- Reference panel mismatch

**Trigger:** Using a WASP SNP file from a different population than the sample.

**Mechanism:** WASP swaps alleles at known hetSNPs; if the variant isn't in the SNP file, no swap happens; reads retain reference bias.

**Symptom:** Sample-specific hetSNPs (not in 1KG) still show reference bias after WASP.

**Fix:** Build WASP SNP file from the sample's own genotype VCF, not a population panel; OR use RASQUAL which handles novel hetSNPs.

### WASP -- Excessive read loss

**Trigger:** WASP filter removes >40% of reads.

**Mechanism:** Many reads span multiple hetSNPs; each must re-map consistently after every allele swap; combinatorial loss.

**Fix:** Accept the loss (genuine bias correction) OR switch to AlleleSeq (personalized genome avoids the swap-and-remap step) OR RASQUAL (no read filtering).

### RASQUAL -- Convergence failure

**Trigger:** Sparse data (few hetSNPs per peak); strong copy-number imbalance.

**Mechanism:** EM convergence requires enough hetSNPs per feature; sparse data underspecifies the model.

**Fix:** Require well-imputed SNPs (`--imputation-quality-fsnp`); combine replicates; or switch to BaalChIP for sparse-data robustness.

### BaalChIP -- CN file mismatch

**Trigger:** CN BED uses different naming convention (chrX vs X) than BAMs.

**Mechanism:** BaalChIP silently doesn't apply CN-aware overdispersion if CN positions don't match BAM chromosomes.

**Symptom:** ASB calls at CN-altered regions look bimodal (one allele appears 100% bound).

**Fix:** Verify chromosome naming matches across CN file, BAM, hetSNP VCF.

### AlleleSeq -- Insufficient phasing

**Trigger:** Using unphased VCF for diploid genome construction.

**Mechanism:** AlleleSeq requires phased genotypes; without phasing, maternal and paternal genomes are randomly assigned.

**Fix:** Use trio or read-based phasing (HapCUT2, WhatsHap) before AlleleSeq.

### Imprinted loci not filtered

**Trigger:** Reporting ASB at H19 or IGF2.

**Mechanism:** These loci are biologically allele-skewed; the "ASB" call is correct but uninformative.

**Fix:** Always filter imprinted loci before reporting / interpreting ASB.

### Female chrX ASB artifacts

**Trigger:** Reporting ASB at chrX in female samples without X-inactivation correction.

**Mechanism:** Random X-inactivation silences one X per cell; population of cells shows extreme allele bias at any X-linked variant.

**Fix:** Filter chrX in female samples OR use methods that model X-inactivation (rare in standard ASB pipelines).

### Reference allele bias not corrected

**Trigger:** Running BaalChIP / chi-squared test directly without WASP or RASQUAL bias handling.

**Mechanism:** 1-5% genome-wide REF allele over-representation produces false-positive REF-favoring ASB calls.

**Symptom:** ASB calls skewed toward REF allele.

**Fix:** Always apply WASP (or RASQUAL's phi parameter) before testing.

## Reconciliation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| WASP filter applied; still REF-biased | Sample-specific hetSNPs not in WASP SNP file | Use sample's own genotype VCF for WASP |
| BaalChIP and RASQUAL disagree at sparse hetSNPs | Different sparse-data behavior | BaalChIP Bayesian more conservative for sparse; check posterior |
| ASB call at imprinted locus | Biology, not differential binding | Filter imprinted loci |
| ASB at chrX in female | X-inactivation | Filter chrX |
| ASB call where copy-number altered | Cancer dose effect | Use BaalChIP with CN file OR exclude CN-altered regions |
| chromBPNet predicts strong variant effect; ASB doesn't | Sample has low coverage at variant; chromBPNet predicts in counterfactual | Increase depth; ASB requires actual chromatin sample |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| WASP `find_intersecting_snps.py` fails | h5 SNP table format wrong | Build SNP tables from VCF via `snp2h5` (HDF5) or `extract_vcf_snps.sh` (text SNP dir) |
| BaalChIP "no overlap with peaks" | hetSNP and peak chrom naming mismatch | Standardize chrom prefixes |
| RASQUAL OOM | cis-window too large; too many features | Narrow the cis-window (tabix region and `-l`/`-m`); chunk feature list |
| AlleleSeq "diploid genome too large" | Many SVs in genome | Use small-variant only VCF; exclude SV-rich regions |
| ASB calls cluster at REF allele | WASP not applied OR insufficient | Re-run WASP with sample-specific SNP file |
| Many ASB at chrX in female | X-inactivation | Filter chrX |
| All "ASB" calls are at imprinted loci | Imprinting not filtered | Apply imprinted-loci BED |

## References

- Rozowsky J et al 2011 Mol Syst Biol 7:522 (AlleleSeq)
- van de Geijn B et al 2015 Nat Methods 12:1061 (WASP)
- Kumasaka N et al 2016 Nat Genet 48:206 (RASQUAL)
- de Santiago I et al 2017 Genome Biol 18:39 (BaalChIP)
- Mayba O et al 2014 Genome Biol 15:405 (MBASED)
- Chen J et al 2016 Nat Commun 7:11101 (1000 Genomes ASB / ASE survey)

## Related Skills

- chip-seq/peak-calling - Peak calling upstream
- chip-seq/chipseq-qc - QC before ASB analysis
- chip-seq/chip-deep-learning - Validate DL variant predictions against ASB
- chip-seq/peak-annotation - Annotate ASB variants to genes / cCREs
- atac-seq/allele-specific-accessibility - Parallel ATAC ASB workflow
- causal-genomics/fine-mapping - ASB as fine-mapping orthogonal evidence
- variant-calling/variant-annotation - Annotate hetSNPs before ASB
- phasing-imputation/haplotype-phasing - Required for AlleleSeq
<!-- END FILE: chip-seq/allele-specific-binding/SKILL.md -->

## 子目录：chip-seq/chip-deep-learning

<!-- BEGIN FILE: chip-seq/chip-deep-learning/SKILL.md -->
---
name: bio-chipseq-chip-deep-learning
description: Trains and applies base-resolution deep learning models on ChIP-seq / ChIP-nexus / CUT&RUN data. Uses BPNet (Avsec 2021 Nat Genet 53:354; soft motif syntax from ChIP-nexus), chromBPNet (Pampari A et al 2024 bioRxiv; bias-factorized base-resolution profiles), EnFormer (Avsec 2021 Nat Methods 18:1196; 196 kb input, ~100 kb effective receptive field), DeepSEA (Zhou 2015; multi-task CNN), and JASPAR 2026 deep-learning collection (1259 BPNet ChIP models). Performs in silico mutagenesis for variant-effect prediction, DeepLIFT/Grad attribution, and TF-MoDISco motif discovery from attribution scores. Use when predicting variant effects on TF binding, discovering soft motif syntax / cooperativity, integrating ChIP-seq with sequence-only predictions, or applying precomputed JASPAR Deep Learning models to new variants.
tool_type: python
primary_tool: chrombpnet
---

## Version Compatibility

Reference examples tested with: chrombpnet 0.1.7+, BPNet 0.0.23+, TF-MoDISco-lite 2.0+, EnFormer (Avsec lab Colab + DeepMind release), tensorflow 2.13+, pytorch 2.0+, JASPAR 2026 deep-learning collection (released 2025).

# Deep Learning for ChIP-seq

**"Predict TF binding from sequence and quantify variant effects on binding"** -> Train base-resolution convolutional / transformer models on ChIP-seq / ChIP-nexus / CUT&RUN profiles; predict reference and alternate-allele binding profiles for variants; extract motif syntax via TF-MoDISco from sequence-attribution scores.

- Python (modern): chrombpnet (bias-factorized; ATAC/DNase/ChIP)
- Python (canonical TF ChIP): BPNet (originally for ChIP-nexus; soft motif syntax)
- Python (long-range): EnFormer (Avsec 2021 Nat Methods 18:1196; 196 kb input window, ~100 kb effective receptive field; tissue-aggregated training)
- Python (multi-task): DeepSEA (Zhou 2015; older but still used)
- Precomputed: JASPAR 2026 Deep Learning collection (1259 BPNet ChIP models from ENCODE; 240 TFs)

Deep-learning ChIP-seq models predict signal from sequence; their power is in counterfactual variant prediction (effect on binding from a SNP) and discovery of soft motif syntax that PWMs miss (cooperativity, spacing).

## Model Taxonomy

| Model | Year | Architecture | Receptive field | Best for |
|-------|------|--------------|------------------|----------|
| **BPNet** (Avsec 2021 Nat Genet 53:354) | 2021 | CNN with dilated convolutions | ~1 kb | TF ChIP-nexus / ChIP-exo; base-resolution profile prediction; soft motif syntax |
| **chromBPNet** (Pampari A et al 2024 bioRxiv) | 2024 | Bias-factorized CNN | ~1-2 kb | ATAC/DNase + ChIP base-resolution; bias-corrected variant effects |
| **EnFormer** (Avsec 2021 Nat Methods 18:1196) | 2021 | Transformer | ~100 kb effective receptive field (input window 196 kb) | Long-range regulatory predictions; cross-tissue; variant effects spanning enhancer-gene |
| **DeepSEA** (Zhou 2015) | 2015 | CNN multi-task | 1 kb | Predicts presence/absence across many chromatin features simultaneously |
| **DeepBind** (Alipanahi 2015) | 2015 | CNN binary classifier | ~50-200 bp | TF binding presence (older, less precise than BPNet) |
| **Basset** (Kelley 2016) | 2016 | CNN | ~600 bp | DNase / ATAC accessibility prediction |
| **JASPAR 2026 Deep Learning collection** | 2025 | Precomputed BPNet | ~1 kb | 1259 ENCODE TF ChIP-seq models; 240 TFs; ready-to-use |

## Decision Tree: Which Model

| Goal | Model | Why |
|------|-------|-----|
| Predict variant effect on TF binding (cis-pQTL fine-mapping) | chromBPNet or EnFormer | Both predict ref/alt counterfactuals; chromBPNet base-resolution, EnFormer long-range |
| Discover motif syntax / TF cooperativity from existing ChIP | BPNet (ChIP-nexus data) or chromBPNet (regular ChIP) + TF-MoDISco | Attribution-based motif discovery captures soft syntax PWMs miss |
| Use precomputed model on new variant | JASPAR 2026 deep-learning collection | 1259 BPNet ChIP models ready; no training needed |
| Predict ChIP signal from sequence in a new cell type | EnFormer (cross-tissue training) | Long-range receptive field; multi-tissue training |
| Integrate ATAC + ChIP into single model | chromBPNet | Bias-factorized handles both assays |
| TF binding presence/absence multi-task | DeepSEA | Older but simple multi-output |

## In Silico Mutagenesis Workflow

**Goal:** Predict whether a single-nucleotide variant changes transcription factor or histone modification binding.

**Approach:** Encode reference and alternate-allele sequences in the model's expected window (2114 bp for chromBPNet, centered on variant), predict per-base profile + total counts for each, compute log2 fold change in counts as the variant-effect score. Apply ensemble of 5-10 models for uncertainty.

The most clinically/translationally useful application: predict whether a variant changes TF binding.

```python
import chrombpnet
import numpy as np
import tensorflow as tf

# Load trained chromBPNet model
model = tf.keras.models.load_model('chrombpnet_model.h5', compile=False)

# Reference and alternate-allele sequence around variant (2114 bp window typical)
ref_seq = encode_dna_one_hot('NNN...CCATGNNN...')   # 2114 bp; variant position central
alt_seq = encode_dna_one_hot('NNN...CCAAGNNN...')   # G->A at central position

# Predict base-resolution profiles
ref_profile, ref_counts = model.predict(ref_seq[None, ...])
alt_profile, alt_counts = model.predict(alt_seq[None, ...])

# Variant effect: log2 fold change in predicted total counts
log2_fc = np.log2(alt_counts / ref_counts)
print(f'Variant effect: log2_fc = {log2_fc}')

# |log2_fc| > 1 indicates strong-effect SNP per chromBPNet 2024 paper
# Concordance with EnFormer increases confidence for clinical interpretation
```

**Variant effect interpretation:**
- |log2_fc| > 1: strong effect; binding likely affected
- 0.3 < |log2_fc| < 1: moderate effect; investigate further
- |log2_fc| < 0.3: weak / no effect predicted
- Concordance between chromBPNet and EnFormer increases confidence

## TF-MoDISco for Soft Motif Syntax

Standard PWM-based motif discovery misses:
- Cooperative motif interactions (TF dimers, ETS-RUNX, GATA-TAL)
- Soft motif syntax (variable spacing, weak co-binding)
- Long-range dependencies

TF-MoDISco extracts motifs from deep-learning attribution scores:

```python
import numpy as np
import shap

# Compute DeepLIFT / DeepSHAP attribution scores
explainer = shap.DeepExplainer(model, background_seqs)
attribution_scores = explainer.shap_values(test_seqs)

# Save one-hot sequences + attributions for tfmodisco-lite
np.savez('ohe.npz', test_seqs)
np.savez('shap.npz', attribution_scores)
```

```bash
# tfmodisco-lite runs via its `modisco` CLI: -n max seqlets/metacluster, -w window (default 400)
modisco motifs -s ohe.npz -a shap.npz -n 2000 -w 400 -o modisco_results.h5
modisco report -i modisco_results.h5 -o report/ -m motifs.meme
# Output: motif patterns discovered from attribution (not from PWM matching)
# Often more interpretable than PWM motifs for cooperative TF binding
```

## Training chromBPNet from Scratch

```bash
# Install
pip install chrombpnet

# Train bias model (control regions without TF binding).
# In the bias pipeline, -b is the bias_threshold_factor (float; ~0.5 ATAC, ~0.8 DNase)
# and -o is the required output directory.
chrombpnet bias pipeline \
    -ibam input.bam -d DNASE \
    -g hg38.fa -c chrom.sizes -p peaks.bed \
    -n nonpeaks.bed -fl fold_0.json \
    -b 0.8 -o bias_model_dir/

# Train main chromBPNet model. chromBPNet assay types are ATAC or DNASE only
# (there is no -d ChIP); use the DNASE bias model for point-source ChIP.
# In the main pipeline, -b is the path to the trained bias model .h5.
chrombpnet pipeline \
    -ibam chip.bam -d DNASE \
    -g hg38.fa -c chrom.sizes -p peaks.bed -n nonpeaks.bed \
    -fl fold_0.json \
    -b bias_model_dir/models/bias.h5 \
    -o output_dir/

# Output: trained model + per-locus base-resolution predictions
```

Training cost: 1-3 GPU days for a single chromBPNet model; multiple GPUs for EnFormer.

## EnFormer Application

```python
from enformer_pytorch import from_pretrained

model = from_pretrained('EleutherAI/enformer-official-rough')

# 196 kb input window
seq = torch.tensor(one_hot_encode(reference_seq))[None, ...]
predictions = model(seq)
# Predictions: per-bin signal across 5,313 ENCODE tracks
# Each variant effect = difference in target track prediction

# Variant effect at SNP
ref_pred = model(encode(ref_seq))[..., :, target_track_idx]
alt_pred = model(encode(alt_seq))[..., :, target_track_idx]
variant_effect = (alt_pred - ref_pred).mean()
```

EnFormer's 196 kb input (~100 kb effective receptive field) captures distal regulatory effects; useful when variant is far from TSS.

## Using JASPAR 2026 Deep Learning Models (Precomputed)

JASPAR 2026 (released 2025) added 1259 BPNet models trained on ENCODE TF ChIP-seq:

```python
from pyjaspar import jaspardb

jdb = jaspardb(release='JASPAR2026')

# pyjaspar returns PWM/motif objects (Bio.motifs.jaspar.Motif), e.g. CORE PWMs:
core_pwms = jdb.fetch_motifs(collection=['CORE'])

# The JASPAR 2026 BPNet deep-learning models (per-TF, ENCODE ChIP) are distributed
# as model files on the JASPAR website, NOT via pyjaspar; download them there and
# load (Keras H5 / PyTorch) for in silico mutagenesis on new variants.
```

This is the lowest-effort path for variant-effect prediction on canonical TFs (no training required).

## Per-Tool Failure Modes

### chromBPNet -- Bias model trained on wrong assay

**Trigger:** Using ATAC bias model on ChIP data.

**Mechanism:** ATAC bias model captures Tn5 sequence preferences; ChIP has different bias structure (sonication, fragmentation, antibody-driven).

**Symptom:** Variant effect predictions noisy; attribution scores dominated by Tn5 sequence preferences.

**Fix:** Train bias model on ChIP non-peak regions, not ATAC; or use chromBPNet's ChIP-specific bias correction.

### BPNet -- Trained on insufficient peaks

**Trigger:** Training BPNet on a TF with <5000 high-confidence peaks.

**Mechanism:** Base-resolution profile prediction needs many examples per motif context.

**Symptom:** Model accuracy <0.6 Spearman correlation between predicted and observed profiles.

**Fix:** Combine replicates; use more permissive peak threshold; or fall back to PWM-based motif analysis.

### TF-MoDISco -- Background sequences not representative

**Trigger:** Using random genomic sequences as background for attribution.

**Mechanism:** Genomic sequences include other TF binding sites; attribution conflates target TF with background TFs.

**Fix:** Use shuffled-input sequences as background (preserves dinucleotide); OR use peaks from a control ChIP (e.g., IgG) as background.

### In silico mutagenesis -- Variant outside training distribution

**Trigger:** Predicting effect of a variant in a sequence context the model never saw (e.g., new TF site arrangement).

**Mechanism:** Deep-learning models extrapolate poorly; counterfactual prediction for novel contexts is unreliable.

**Symptom:** Variant effect estimate has huge variance across model replicates.

**Fix:** Train ensemble of 5-10 models; use disagreement as uncertainty estimate; for high-stakes claims, validate experimentally.

### EnFormer -- Tissue-aggregated predictions

**Trigger:** Predicting variant effect for a specific cell line that has its own ChIP-seq.

**Mechanism:** EnFormer was trained on tissue-aggregated tracks; cell-line-specific resolution is limited.

**Fix:** For cell-line-specific predictions, fine-tune EnFormer on cell-line ChIP-seq OR use chromBPNet trained on cell-line data.

### Memory / GPU requirements

**Trigger:** Training chromBPNet or EnFormer on a single GPU with insufficient memory.

**Mechanism:** chromBPNet (~10 GB GPU memory), EnFormer (~16-24 GB), batch sizes / sequence lengths affect memory.

**Fix:** Reduce batch size; use gradient checkpointing; for EnFormer, use the smaller 5x architecture variant.

## Reconciliation with PWM-Based Analysis

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| TF-MoDISco motif matches JASPAR PWM | DL model recovered canonical motif | Confidence in DL model |
| TF-MoDISco motif doesn't match any PWM | Novel motif syntax OR DL model overfit | Validate with TOMTOM against larger DBs; check model ensemble agreement |
| chromBPNet predicts strong variant effect, JASPAR PWM scan does not | Soft syntax / cooperativity; DL captures more than PWM | DL prediction often more accurate; experimental validation ideal |
| EnFormer and chromBPNet disagree on variant effect | Different receptive fields capture different biology | Trust EnFormer for distal effects, chromBPNet for local |
| Variant effect ensemble disagrees within model | Training instability OR variant in extrapolation regime | Treat as low-confidence; do not publish without validation |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `chrombpnet` import fails | TensorFlow / Keras version mismatch | Use chrombpnet conda env with pinned tf 2.13 |
| `cuda out of memory` | Batch size too large | Reduce batch_size in training config |
| Predictions all zero | Bias model corrupted or wrong assay | Re-train bias on matched assay |
| TF-MoDISco produces empty motif list | FDR too strict or attribution noisy | Lower `target_seqlet_fdr` to 0.10; increase model training depth |
| EnFormer "shape mismatch" | Sequence not exactly 196608 bp (default) | Pad or truncate to expected length |
| Variant effect for nucleotide outside ACGT | Model only handles ACGT | Skip variants with N or ambiguous nucleotides |

## References

- Avsec Ž et al 2021 Nat Genet 53:354 (BPNet; ChIP-nexus base-resolution model)
- Pampari A et al 2024 bioRxiv 2024.12.25.630221 (chromBPNet; bias-factorized base-resolution models of chromatin accessibility)
- Avsec Ž et al 2021 Nat Methods 18:1196-1203 (EnFormer; ~100 kb effective receptive field, 196 kb input window)
- Zhou J & Troyanskaya OG 2015 Nat Methods 12:931 (DeepSEA)
- Alipanahi B et al 2015 Nat Biotechnol 33:831 (DeepBind)
- Kelley DR et al 2016 Genome Res 26:990 (Basset)
- Shrikumar A et al 2018 (rev. 2020) arXiv:1811.00416 (TF-MoDISco)
- Shrikumar A et al 2017 ICML (DeepLIFT)
- Lundberg SM & Lee SI 2017 NeurIPS (SHAP)
- JASPAR Project 2026 (deep-learning collection)
- Karbalayghareh A et al 2022 Genome Res 32:930 (GraphReg; chromatin-interaction-aware regulatory modeling, cross-cell-type generalization)

## Related Skills

- chip-seq/peak-calling - Source peaks for training DL models
- chip-seq/motif-analysis - PWM-based analysis (complementary to DL)
- chip-seq/allele-specific-binding - Validate DL variant predictions against ASB data
- atac-seq/deep-learning-atac - ATAC-specific chromBPNet workflow
- atac-seq/footprinting - TOBIAS footprints as comparison
- causal-genomics/fine-mapping - Variant-level functional annotation
- machine-learning/biomarker-discovery - DL variant scores as features
- machine-learning/model-validation - Ensemble agreement, cross-validation
<!-- END FILE: chip-seq/chip-deep-learning/SKILL.md -->

## 子目录：chip-seq/chipseq-qc

<!-- BEGIN FILE: chip-seq/chipseq-qc/SKILL.md -->
---
name: bio-chipseq-qc
description: Assesses ChIP-seq quality across antibody specificity, fragmentation, enrichment, replicate concordance, and library complexity. Computes FRiP, NSC/RSC (phantompeakqualtools), library complexity (NRF/PBC1/PBC2), deepTools plotFingerprint (JS distance, AUC, synthetic JS), ChIPQC, IDR with ENCODE Nself/Nt rules, and detects hyper-ChIPable artifacts. Use when validating an antibody, diagnosing failed peak calls, deciding whether to proceed with downstream analysis, grading against ENCODE thresholds, or auditing replicate concordance.
tool_type: mixed
primary_tool: deepTools
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: deepTools 3.5+, phantompeakqualtools 1.2.2+, ChIPQC 1.42+, IDR 2.0.4+, samtools 1.19+, bedtools 2.31+, pysam 0.22+, pybedtools 0.9+, MACS2 2.2.9+, MACS3 3.0.4+.

Verify versions before relying on numerical thresholds — phantompeakqualtools has known R-version compatibility issues with R ≥ 4.0 (use kundajelab fork or pin to R 3.6).

# ChIP-seq Quality Control

**"Should I trust this ChIP-seq experiment?"** -> Validate antibody, fragmentation, enrichment, replicate concordance, library complexity, and absence of hyper-ChIPable artifacts before committing to downstream peak calling and differential analysis.

- CLI: `Rscript run_spp.R -c=chip.bam -out=cc.txt` (NSC/RSC), `plotFingerprint -b chip.bam input.bam` (enrichment shape), `idr --samples rep1.np rep2.np` (replicate IDR)
- R: ChIPQC package (Carroll & Stark; computes the full ENCODE metric battery)
- Python: pysam + pybedtools for custom FRiP and library-complexity metrics

ChIP-seq fails for many independent reasons. The QC metrics below probe distinct failure modes — passing one metric does not rescue another. Antibody failure cannot be fixed by sequencing more.

## The Antibody Problem is the Real Problem

Every downstream metric is conditional on antibody specificity. "ChIP-grade" on a vendor datasheet is marketing, not validation. Run the cascade:

| Step | What | Why |
|------|------|-----|
| 1. Western blot | Expected MW + KO/KD negative | Confirms the antibody hits a band of the right size and loses signal in KO |
| 2. IP-Western | Pulls down the protein | Confirms IP recovery, not just recognition |
| 3. ChIP-qPCR | Known positive + known negative loci | First chromatin-context test; cheap |
| 4. ChIP-seq biological replicate | Two independent biological replicates | Reproducibility check |
| 5. KO/KD orthogonal | ChIP in KO/KD cells | Gold-standard: signal should drop to background |
| 6. Peptide array (histones) | Epicypher SNAP-ChIP or equivalent | Tests modification-state specificity |

Histone modification cross-reactivity is universal: H3K9me2 vs H3K9me3, H3K27me2 vs H3K27me3, and H3K4me1 vs H3K4me2 antibodies routinely show 10-30% cross-reactivity. Polyclonals vary lot-to-lot. CRISPR-knockout-validated lots from CST and Epicypher are the modern standard. Always record antibody catalog number + lot in methods.

## Fragment-Size Distribution is a Free Diagnostic

The fragment-size distribution from a properly prepared ChIP BAM is itself a quality readout:

| Distribution shape | Interpretation |
|--------------------|----------------|
| Sharp peak at ~50-100 bp (sub-nucleosomal) | Direct TF binding; expected for well-fragmented TF ChIP |
| Sharp peak at ~150 bp + secondary at ~300 bp | Mono- + di-nucleosomal; expected for histone ChIP |
| Bimodal at 150 + 300, no sub-nucleosomal | Histone-only signal; in TF ChIP, suggests trapping / hyper-ChIPable |
| Broad continuum 100-1000 bp | Over-sonication; biology lost; cannot be rescued |
| No peak structure, flat | Severe over-sonication or library prep failure |

```bash
# Quick diagnostic — count fragment sizes from properly-paired reads
samtools view -f 0x2 sample.bam | awk '{print $9}' | awk '$1>0' \
    | sort -n | uniq -c | awk '{print $2, $1}' > fragment_sizes.tsv
```

For CUT&Tag: 25-75 bp characteristic; fragments < 25 bp are Tn5 self-tagmentation noise (see cut-and-run-tag).

## QC Metric Battery with ENCODE Thresholds

| Metric | Tool | TF threshold | Histone threshold | Source / rationale |
|--------|------|--------------|-------------------|---------------------|
| **FRiP** (Fraction of Reads in Peaks) | bedtools / pysam / featureCounts | ≥ 0.01 minimum, > 0.05 ideal | ≥ 0.05, > 0.20 ideal; > 0.15 for H3K4me3 | Landt 2012; ENCODE flags experiments with FRiP < 1% |
| **NSC** (Normalized Strand Cross-correlation) | phantompeakqualtools | > 1.05 marginal, > 1.10 ideal | > 1.05 | Landt 2012; min = 1 (no enrichment); ratio of fragment-length CC to background |
| **RSC** (Relative Strand Cross-correlation) | phantompeakqualtools | > 0.8 marginal, > 1.0 ideal | > 0.8 | Landt 2012; ratio of (fragment - background) / (phantom - background) |
| **QualityTag** | phantompeakqualtools | ≥ 0 acceptable, 1-2 ideal | ≥ 0 | Composite based on NSC/RSC; -2 to 2 scale |
| **NRF** (Non-Redundant Fraction) | unique_pos / total | > 0.8 | > 0.8 | ENCODE; < 0.5 severe PCR bottleneck |
| **PBC1** (M1 / Mdistinct) | bedtools / pysam | > 0.8 | > 0.8 | ENCODE; fraction of singly-occupied positions |
| **PBC2** (M1 / M2) | bedtools / pysam | > 3 | > 3 | ENCODE; ratio of singletons to doubletons |
| **JS distance** (plotFingerprint) | deepTools | > 0.3 | > 0.05 (broad) to > 0.3 (narrow) | Distance between cumulative signal curves IP vs Input |
| **AUC** (plotFingerprint) | deepTools | < 0.6 | 0.6-0.9 | Input = ~0.5; lower AUC = more enrichment concentrated |
| **Synthetic JS** (plotFingerprint) | deepTools | Should ≈ measured JS | — | Sanity check vs simulated null |
| **Replicate Spearman correlation** | deepTools multiBamSummary / plotCorrelation | > 0.8 (true reps) | > 0.8 (true reps), > 0.6 (broad) | Replicates should correlate more than cross-condition |
| **Read count per replicate** | samtools flagstat | ≥ 20M unique mapped | 20M (narrow histone), 40-60M (broad histone) | ENCODE 2012 |

**Practical operational rule:** Compute the full battery. Reject any sample failing FRiP OR antibody validation OR fragment-size sanity check, regardless of other metrics. Failing one of NSC/RSC alone with strong FRiP can sometimes be rescued for narrow-peak biology; broad histones are more forgiving on NSC.

## Hyper-ChIPable Region Detection

Teytelman 2013 (PNAS): untagged GFP, no antibody, or non-existent targets all produce "binding" signal at highly-transcribed loci (rRNA, tRNA, histone gene clusters, snoRNA hosts, mtDNA, abundant housekeeping genes). ENCODE blacklist v2 (Amemiya 2019) catches repeat-driven artifacts but NOT these hyper-ChIPable transcribed regions.

**Detection:**

```bash
# Top 1% input signal as cell-type-specific custom blacklist
multiBigwigSummary BED-file -b input.bw -o input_signal.npz \
    --BED genes.bed --outRawCounts input_per_gene.tsv
awk 'NR > 1' input_per_gene.tsv | sort -k4,4nr | head -n $(($(wc -l < input_per_gene.tsv) / 100)) \
    > hyper_chipable.bed

# Intersect peaks against this list; flag peaks falling in hyper-ChIPable regions
bedtools intersect -a peaks.narrowPeak -b hyper_chipable.bed -u > suspicious_peaks.bed
```

**Disprove a suspicious peak:** Required for any claim at rRNA loci, tRNA clusters, HIST1/2 clusters, mitochondrial DNA:
1. Motif enrichment at peak (artifact has no enrichment)
2. KO/KD signal loss at peak (artifact persists)
3. Untagged-protein control ChIP shows no signal at this locus

Many "novel binding" claims at the rDNA repeat, mtDNA, and HIST1 cluster are spurious artifacts.

## Computing the Battery

### FRiP

```bash
total_reads=$(samtools view -c -F 260 chip.bam)
reads_in_peaks=$(bedtools intersect -a chip.bam -b peaks.narrowPeak -u | samtools view -c -)
frip=$(echo "scale=4; $reads_in_peaks / $total_reads" | bc)
```

### NSC / RSC / fragment length (phantompeakqualtools)

```bash
Rscript run_spp.R -c=chip.bam -savp=qc/chip_cc.pdf -out=qc/chip_cc.txt
# Output columns: filename | numReads | estFragLen | corr_estFragLen |
#                 phantomPeak | corr_phantomPeak | argmin_corr | min_corr |
#                 NSC | RSC | QualityTag
```

### Library complexity

```bash
# NRF
total=$(samtools view -c -F 260 chip.bam)
unique=$(samtools view -F 260 chip.bam | awk '{print $1, $3, $4}' | sort -u | wc -l)
nrf=$(echo "scale=4; $unique / $total" | bc)

# PBC1, PBC2 (singletons vs distinct positions vs doubletons)
samtools view -F 260 chip.bam | awk '{print $3":"$4}' | sort | uniq -c \
    | awk '{
        if ($1 == 1) m1++;
        if ($1 == 2) m2++;
        mdist++;
      } END {
        print "M1:", m1; print "M2:", m2; print "Mdistinct:", mdist;
        print "PBC1:", m1/mdist; print "PBC2:", m1/m2
      }'
```

### deepTools plotFingerprint

```bash
plotFingerprint \
    -b chip.bam input.bam \
    --labels ChIP Input \
    -o qc/fingerprint.pdf \
    --outRawCounts qc/fingerprint_counts.tab \
    --outQualityMetrics qc/fingerprint_qc.txt
# Inspect qc/fingerprint_qc.txt: AUC, JS distance, synthetic JS, X-intercept
# Good ChIP: AUC < 0.6 (TF), JS > 0.3 (TF); Input near diagonal (AUC ~ 0.5)
```

### Replicate Spearman correlation

```bash
multiBamSummary bins -b rep1.bam rep2.bam rep3.bam input.bam \
    --binSize 10000 -o results.npz
plotCorrelation -in results.npz --corMethod spearman \
    --whatToPlot heatmap --plotNumbers -o corr.pdf \
    --outFileCorMatrix corr_matrix.tab
# Replicates: > 0.8 (narrow), > 0.6 (broad)
# Cross-condition reps should correlate less than within-condition
```

### ChIPQC R package

```r
library(ChIPQC)
samples <- read.csv('samples.csv')
qc <- ChIPQC(samples, annotation = 'hg38')
ChIPQCreport(qc, reportFolder = 'ChIPQCreport')
# Generates the full ENCODE battery report per sample in one call
```

ChIPQC remains Bioconductor-maintained but mature; phantompeakqualtools is the canonical NSC/RSC source.

## IDR and Replicate Consistency Rules

For TFs: signal-ranked IDR with Nself/Nt consistency check; see chip-seq/peak-calling for full ENCODE workflow. Key thresholds:

- True replicate IDR threshold: 0.05
- Pseudoreplicate IDR threshold: 0.10 (per-rep self-consistency)
- **Nself/Nt rule:** `max(N1self, N2self) / min(N1self, N2self) ≤ 2` AND `max(Nt, max(Nself)) / min(Nt, min(Nself)) ≤ 2`. Failing both ratios rejects the library.

For histones: naive overlap with ≥ 40% reciprocal overlap (ENCODE default; commonly misquoted as 50%). IDR is too conservative for histone signal dynamic range.

## ENCODE 3 vs ENCODE 4 Thresholds (unchanged for most QC)

| Metric | ENCODE 3 | ENCODE 4 |
|--------|----------|----------|
| FRiP minimum | 1% | 1% (unchanged) |
| NSC threshold | > 1.05 | > 1.05 (unchanged) |
| RSC threshold | > 0.8 | > 0.8 (unchanged) |
| NRF threshold | > 0.8 | > 0.8 (unchanged) |
| Blacklist | v1 | v2 (Amemiya 2019) |
| Read depth (TF) | ≥ 20M unique mapped | ≥ 20M unchanged |
| Read depth (broad histone) | ≥ 40M | 40-60M recommended |

Most QC thresholds are stable across ENCODE versions; blacklist update is the main practical change.

## Per-Tool Failure Modes

### phantompeakqualtools / SPP -- R version incompatibility

**Trigger:** Running with R ≥ 4.0.

**Mechanism:** spp R package has unmaintained Boost / Rcpp dependencies; some shifts produce NaN cross-correlation values.

**Symptom:** NSC = NaN, RSC = NaN, or fragment length = 0 in output.

**Fix:** Pin to R 3.6 + spp 1.16 via conda env; OR use the kundajelab/phantompeakqualtools fork (current); OR substitute deepTools plotFingerprint for enrichment QC and `macs3 predictd` for fragment length.

### deepTools plotFingerprint -- Wrong baseline assumption for broad marks

**Trigger:** Interpreting JS distance with TF threshold (> 0.3) on broad histone mark.

**Mechanism:** Broad marks have less concentrated signal; JS distance is naturally lower (0.05-0.15 for H3K27me3) without indicating bad ChIP.

**Symptom:** Reports "failed JS distance" for high-quality broad-mark ChIP.

**Fix:** Use mark-specific thresholds: > 0.3 for TFs and sharp histones; > 0.05 for broad histones; check AUC instead (0.6-0.9 for broad; < 0.6 for TF/sharp).

### FRiP -- Computed before vs after blacklist filtering

**Trigger:** Calling FRiP from peak file pre- vs post-blacklist.

**Mechanism:** Hyper-ChIPable regions inflate "reads in peaks" because most reads at those loci are artifacts.

**Symptom:** FRiP looks great (>15%) but most of it is rRNA / mtDNA reads.

**Fix:** Apply blacklist + custom hyper-ChIPable filter BEFORE computing FRiP; or report both raw and filtered FRiP.

### NRF / PBC -- Computed after deduplication

**Trigger:** Running NRF on a MarkDuplicates-filtered BAM.

**Mechanism:** Library complexity metrics measure PCR redundancy; if duplicates are already removed, NRF = 1.0 by construction (uninformative).

**Symptom:** NRF reports 0.99-1.0; metric is meaningless.

**Fix:** Compute NRF / PBC1 / PBC2 on the PRE-deduplication BAM. ENCODE-compliant pipeline: filter -> MarkDuplicates (don't remove) -> compute NRF -> filter out duplicates -> call peaks.

### IDR -- Wrong rank column

**Trigger:** Sorting narrowPeak by signalValue (column 7) for IDR.

**Mechanism:** MACS signalValue scales with pile-up intensity which differs between libraries of different depth; rank correlation breaks.

**Symptom:** IDR returns 0 reproducible peaks despite good replicate Spearman correlation.

**Fix:** Sort by p-value (`-k8,8nr`), pass `--rank p.value` to IDR. ENCODE convention.

### ChIPQC -- Default annotation mismatch

**Trigger:** Using `annotation = 'hg19'` on hg38-aligned data.

**Mechanism:** ChIPQC computes feature-context enrichment from the specified annotation; mismatch silently corrupts enrichment metrics.

**Symptom:** Promoter / 5'UTR / 3'UTR enrichments look wrong; replicate report metrics drift.

**Fix:** Match `annotation` to the genome the BAMs were aligned to; for custom genomes pass a TxDb object explicitly.

## Reconciliation: When Metrics Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Good FRiP, bad NSC | High background but real enrichment | Acceptable for broad marks; for TFs, check phantompeakqualtools fragment length is reasonable |
| Good NSC, bad FRiP | Strong cross-correlation signal but few peaks pass q-value | Library shallow OR peak caller threshold too strict; try `-p 1e-2` |
| Good FRiP and NSC, bad replicate correlation | Real biology + replicate-specific batch effect | Check sample swap; check sequencing batch; consider PCA |
| Good Rep1, bad Rep2 | One replicate failed | Drop Rep2 + repeat; do NOT average metrics |
| All metrics fail | Antibody or fragmentation failure | Re-validate antibody (KO/KD); inspect fragment-size distribution; do not proceed |
| FRiP excellent at rRNA/mtDNA | Hyper-ChIPable artifact dominance | Build custom blacklist; recompute |

**Operational rule for proceeding with downstream analysis:** Require (1) antibody validated, (2) fragment-size distribution sane, (3) FRiP, NSC, RSC pass ENCODE thresholds, (4) Nself/Nt rule satisfied for TFs OR naive overlap concordance for histones, (5) hyper-ChIPable artifacts identified and either filtered or flagged.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `Sequence chrM not found` (multi-tool) | chrM removed from BAM but kept in genome FASTA | Match chromosome naming convention; consistently include or exclude chrM |
| phantompeakqualtools hangs / OOM | Default tag chunking on deep libraries | Subsample to 15-25M reads (`samtools view -s`) before running |
| plotFingerprint blank or near-diagonal | Input control mislabeled as ChIP | Verify sample labels; AUC ~ 0.5 = Input-like signal |
| IDR runs but Nself ratio always > 2 | One pseudoreplicate dominates due to seed | Use sufficiently different seeds (`-s 1.5` and `-s 2.5`) |
| ChIPQC report missing peaks | samples.csv path columns wrong | Verify bamReads / Peaks paths; ChIPQC fails silently on missing files |
| Replicate Spearman > 0.95 | Technical (not biological) replicates | Treat as one sample; do not report as biological replicates |

## References

- Landt SG et al 2012 Genome Res 22:1813 (ENCODE/modENCODE QC guidelines, IDR Nself rule)
- Kharchenko PV et al 2008 Nat Biotechnol 26:1351 (SPP, NSC/RSC framework)
- Li Q et al 2011 Ann Appl Stat 5:1752 (IDR)
- Marinov GK et al 2014 G3 4:209 (large-scale ChIP-seq QC comparison)
- Teytelman L et al 2013 PNAS 110:18602 (hyper-ChIPable regions)
- Amemiya HM et al 2019 Sci Rep 9:9354 (ENCODE blacklist v2)
- Ramírez F et al 2016 Nucleic Acids Res 44:W160 (deepTools)
- Carroll TS et al 2014 Front Genet 5:75 (ChIPQC framework)
- Diaz A et al 2012 Stat Appl Genet Mol Biol 11:Article 9 (SES normalization / fingerprint-style QC)
- Park PJ 2009 Nat Rev Genet 10:669 (foundational review)
- Rothbart SB et al 2015 Mol Cell 59:502 (histone antibody specificity database)

## Related Skills

- chip-seq/peak-calling - Use QC metrics to decide whether to proceed with peak calling
- chip-seq/cut-and-run-tag - CUT&RUN/CUT&Tag QC differs (spike-in % aligned, fragment-size signatures)
- chip-seq/spike-in-normalization - QC for spike-in carryover and Drosophila read depth
- chip-seq/differential-binding - Replicate concordance required before differential testing
- atac-seq/atac-qc - Parallel QC for ATAC-seq (no input control, different thresholds)
- alignment-files/bam-statistics - General BAM-level QC
- alignment-files/duplicate-handling - MarkDuplicates before NRF computation
<!-- END FILE: chip-seq/chipseq-qc/SKILL.md -->

## 子目录：chip-seq/chipseq-visualization

<!-- BEGIN FILE: chip-seq/chipseq-visualization/SKILL.md -->
---
name: bio-chipseq-visualization
description: Visualizes ChIP-seq data using deepTools (computeMatrix, plotHeatmap, plotProfile, bamCoverage, bamCompare), pyGenomeTracks (modern INI-driven track plots), Gviz (R browser-style), EnrichedHeatmap (ComplexHeatmap-based), ChIPseeker tag heatmaps, and IGV batch screenshots. Handles bigWig normalization choices (CPM, BPM, RPGC, spike-in scaled), bamCompare operations (log2 ratio, subtract) with SES scaling, k-means clustering of heatmaps for biological subgrouping, and spike-in-scaled tracks for global-shift experiments. Use when generating publication-quality ChIP-seq signal heatmaps, profile plots, genome-browser tracks, or comparing samples visually.
tool_type: mixed
primary_tool: deepTools
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: deepTools 3.5+, pyGenomeTracks 3.9+, Gviz 1.46+, EnrichedHeatmap 1.32+, ChIPseeker 1.38+, IGV 2.17+, samtools 1.19+, bedtools 2.31+.

# ChIP-seq Visualization

**"Visualize ChIP-seq signal around features of interest"** -> Generate normalized signal tracks (bigWig), heatmaps centered on TSS/peaks, average profile plots, and genome-browser views — with normalization that supports the biological claim (within-sample vs cross-sample vs spike-in scaled).

- CLI (production): deepTools `bamCoverage` -> `computeMatrix` -> `plotHeatmap` / `plotProfile`
- CLI (config-driven tracks): pyGenomeTracks (replaces Gviz for many use cases)
- R (publication): Gviz, EnrichedHeatmap, ChIPseeker tag heatmaps
- GUI: IGV with batch scripts for reproducible screenshots

The single most consequential choice is **bigWig normalization** — it determines whether visual comparison reflects biology. Get this right before generating any heatmap or browser view.

## bigWig Normalization Decision Tree

| Goal | Method | When to use |
|------|--------|------------|
| Within-sample profile of a single ChIP | `--normalizeUsing CPM` | Standard; reads per million; comparable within one library |
| Within-sample, length-aware | `--normalizeUsing BPM` | TPM-analog; useful for variable-width regions; less common for ChIP-seq |
| Cross-sample with equal effective depth | `--normalizeUsing RPGC --effectiveGenomeSize <N>` | "1x genome coverage" — assumes equal sequencing genome-wide; ENCODE convention |
| Cross-condition with global signal change | `--scaleFactor <spike_in_derived>` (skip `--normalizeUsing`) | HDACi / BETi / EZH2i; see chip-seq/spike-in-normalization |
| ChIP vs input ratio | `bamCompare --operation log2` | Visualize enrichment over input |
| ChIP vs input control-subtracted | `bamCompare --operation subtract` | Absolute signal above background |
| ChIP vs input SES-corrected | `bamCompare --scaleFactorsMethod SES --operation log2` | More robust to library size; uses signal-extraction-scaling |

**ENCODE convention:** RPGC with read-length-matched effective genome size. For visual comparison of treatment vs control on a fold-change biology, log2 bamCompare against shared input.

**Spike-in scaled tracks (the right way):**

```bash
# Compute scale factor from spike-in reads (ChIP-Rx Drosophila or CUT&RUN E. coli)
SCALE=$(echo "scale=6; 1.0 / $SPIKE_IN_READS_M" | bc)  # 1 per million spike reads
bamCoverage -b chip.bam -o chip.bw --scaleFactor $SCALE --binSize 10
# DO NOT also pass --normalizeUsing; deepTools multiplies the two factors, reintroducing depth normalization
```

## deepTools Workflow

### bigWig generation

```bash
# Standard within-sample (CPM)
bamCoverage -b chip.bam -o chip.bw \
    --normalizeUsing CPM --binSize 10 \
    --extendReads 200 --numberOfProcessors 8

# Cross-sample at 1x genome coverage (ENCODE)
bamCoverage -b chip.bam -o chip.bw \
    --normalizeUsing RPGC --effectiveGenomeSize 2701495761 \
    --binSize 10 --extendReads 200

# ChIP vs Input log2 ratio (visualization of enrichment)
bamCompare -b1 chip.bam -b2 input.bam -o chip_vs_input.bw \
    --operation log2 --binSize 50 --extendReads 200 \
    --pseudocount 1 --skipZeroOverZero
```

### Signal matrix and heatmap (reference-point: TSS / peak summit)

```bash
# Compute matrix centered on TSS
computeMatrix reference-point \
    --referencePoint TSS \
    -b 3000 -a 3000 \
    -R genes.bed \
    -S chip.bw input.bw \
    -o matrix.gz \
    --outFileSortedRegions sorted_regions.bed \
    --numberOfProcessors 8 \
    --skipZeros

# Heatmap with k-means clustering (biology emerges from clusters)
plotHeatmap -m matrix.gz \
    -o heatmap.pdf \
    --kmeans 3 \
    --colorMap RdBu_r \
    --zMin -3 --zMax 3 \
    --refPointLabel TSS \
    --heatmapHeight 12 \
    --whatToShow 'heatmap and colorbar'

# Profile plot (average signal across regions)
plotProfile -m matrix.gz \
    -o profile.pdf \
    --perGroup \
    --plotTitle 'H3K4me3 around TSS'
```

### Scale-regions (gene-body scaled to common length)

```bash
computeMatrix scale-regions \
    -R genes.bed \
    -S chip.bw \
    -b 3000 -a 3000 \
    -m 5000 \
    -o matrix_genebody.gz \
    --numberOfProcessors 8

plotProfile -m matrix_genebody.gz -o genebody_profile.pdf --perGroup
```

### Sample correlation

```bash
multiBamSummary bins -b sample1.bam sample2.bam sample3.bam \
    --binSize 10000 -o results.npz \
    --numberOfProcessors 8

plotCorrelation -in results.npz \
    --corMethod spearman \
    --whatToPlot heatmap \
    --plotNumbers -o correlation.pdf \
    --outFileCorMatrix correlation.tab
# Replicates should correlate > 0.8 (narrow), > 0.6 (broad)
```

## pyGenomeTracks (Modern Browser-Style Plotting)

INI-driven, config-as-code; better than Gviz for complex layouts or pipeline integration.

```ini
# tracks.ini
[x-axis]

[chip-h3k27ac]
file = h3k27ac.bw
color = darkblue
height = 3
title = H3K27ac

[chip-h3k4me3]
file = h3k4me3.bw
color = darkred
height = 3
title = H3K4me3

[peaks-narrowpeak]
file = peaks.narrowPeak
file_type = narrow_peak
color = black
height = 0.5
title = MACS peaks

[se-bed]
file = super_enhancers.bed
color = orange
height = 0.5
title = Super-enhancers

[genes]
file = genes.gtf
color = darkgreen
prefered_name = gene_name
height = 4
```

```bash
pyGenomeTracks --tracks tracks.ini --region chr1:1000000-1500000 -o region.pdf
```

For pipeline-driven figure generation across multiple regions, pyGenomeTracks is easier to script than Gviz. For one-off publication figures with complex annotation, Gviz remains useful.

## R: Gviz and EnrichedHeatmap

```r
library(Gviz)
library(GenomicRanges)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

chr <- 'chr1'; start <- 1e6; end <- 1.1e6
itrack <- IdeogramTrack(genome = 'hg38', chromosome = chr)
gtrack <- GenomeAxisTrack()
dtrack <- DataTrack(range = 'sample.bw', genome = 'hg38',
                     type = 'histogram', name = 'ChIP', col.histogram = 'darkblue')
grtrack <- GeneRegionTrack(TxDb.Hsapiens.UCSC.hg38.knownGene,
                            genome = 'hg38', chromosome = chr, name = 'Genes')
plotTracks(list(itrack, gtrack, dtrack, grtrack), from = start, to = end, chromosome = chr)
```

```r
library(EnrichedHeatmap)
library(rtracklayer)

# Normalize bigWig signal to a matrix around target sites
signal <- import('sample.bw')
tss <- promoters(txdb, upstream = 0, downstream = 1)
mat <- normalizeToMatrix(signal, tss, extend = 3000, mean_mode = 'w0', w = 50)

# Heatmap with customization
EnrichedHeatmap(mat, name = 'Signal', col = c('white', 'red'),
                top_annotation = HeatmapAnnotation(lines = anno_enriched()))
```

## ChIPseeker Tag Heatmap (R)

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

peaks <- readPeakFile('peaks.narrowPeak')
promoter <- getPromoters(TxDb = TxDb.Hsapiens.UCSC.hg38.knownGene,
                          upstream = 3000, downstream = 3000)
tagMatrix <- getTagMatrix(peaks, windows = promoter)

# Tag heatmap and average profile
# tagHeatmap in ChIPseeker >= 1.36 takes palette (RColorBrewer name), not xlim/color;
# xlim is read from the tagMatrix window. plotAvgProf still uses xlim/conf.
tagHeatmap(tagMatrix, palette = 'Reds')
plotAvgProf(tagMatrix, xlim = c(-3000, 3000), conf = 0.95,
             xlab = 'Distance from TSS (bp)', ylab = 'Peak density')
```

## IGV Batch Scripts

```bash
# IGV batch script for reproducible screenshots
cat > igv.batch << 'EOF'
new
genome hg38
load chip.bw
load peaks.bed
load super_enhancers.bed
goto chr1:1000000-1100000
snapshot region1.png
goto chr2:50000000-51000000
snapshot region2.png
exit
EOF

igv.sh -b igv.batch
```

## Per-Tool Failure Modes

### bamCoverage -- `--normalizeUsing` and `--scaleFactor` conflict

**Trigger:** Passing both `--normalizeUsing CPM` and `--scaleFactor X`.

**Mechanism:** deepTools multiplies the `--scaleFactor` value by the factor computed from `--normalizeUsing`, so passing both compounds them and reintroduces library-depth normalization on top of the spike-in factor.

**Symptom:** Spike-in scaling appears to have no effect; tracks look like CPM.

**Fix:** Use ONE — `--scaleFactor` alone for spike-in; `--normalizeUsing` alone otherwise. Never both.

### bamCompare -- log2 with zeros produces -Inf

**Trigger:** `bamCompare --operation log2` without pseudocount; many bins have zero reads.

**Mechanism:** log2(0/x) = -Inf; downstream tools (plotHeatmap) may color these as NaN or fail.

**Fix:** Add `--pseudocount 1` to both samples; or use `--skipZeroOverZero` to skip bins with zero in both samples.

### computeMatrix -- Stranded bigWig vs unstranded reference points

**Trigger:** Using stranded bigWigs (separate plus/minus) with `reference-point` mode on a BED without strand info.

**Mechanism:** computeMatrix doesn't auto-detect strand; signal is plotted in genomic-strand orientation, breaking TSS-centered plots.

**Fix:** Use unstranded merged bigWig OR ensure BED has strand column 6.

### plotHeatmap `--kmeans` -- Order depends on first sample only

**Trigger:** Using k-means with multiple samples and expecting consistent clustering.

**Mechanism:** k-means clusters by signal in the first `-S` bigWig only; other samples are plotted in the same row order.

**Fix:** Order samples in `-S` so the most-discriminating one is first; for combined clustering across samples, use `--hclust` or run k-means externally on combined matrix.

### Spike-in scaled bigWig -- Wrong scale factor direction

**Trigger:** Computing `scale_factor = spike_reads / 1e6` and passing to `--scaleFactor`.

**Mechanism:** deepTools multiplies signal by scaleFactor; the INVERSE is correct (sample with fewer spike reads gets larger scale factor to compensate).

**Symptom:** Treatment samples appear lower than control even when biology says higher.

**Fix:** `scale_factor = MIN(spike_reads_all_samples) / spike_reads_this_sample`. Always verify against known internal-control regions (blacklist should show no signal change post-scaling).

### Gviz / EnrichedHeatmap -- Memory failure on whole-genome bigWigs

**Trigger:** Loading a 3 GB bigWig into R as a GRanges.

**Mechanism:** Gviz loads the entire bigWig into memory for genome-wide views.

**Fix:** Use `chromosome` parameter to restrict; use `import.bw(con, which = GRanges(...))` to subset; consider pyGenomeTracks for whole-chromosome views.

### pyGenomeTracks -- INI parsing strict

**Trigger:** Custom INI keys not recognized; or section names with spaces.

**Mechanism:** pyGenomeTracks expects exact key names; case-sensitive section labels.

**Fix:** Run `make_tracks_file --trackFiles sample.bw -o tracks.ini` to generate a template; modify from there.

## Reconciliation: When Visualizations Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Heatmap shows enrichment; profile plot doesn't | Signal concentrated at few regions; profile averages them out | Both correct; heatmap shows distribution, profile shows central tendency |
| Replicate heatmaps differ at peak edges | Different normalization or stranded vs unstranded bigWigs | Verify bigWig parameters identical; use same `--normalizeUsing` |
| Spike-in scaled tracks show opposite trend from CPM | Global shift; CPM forces median to control levels | Spike-in is correct; CPM is fooled by composition |
| ChIPseeker tag heatmap differs from deepTools heatmap | ChIPseeker uses peak density; deepTools uses signal coverage | Different metrics; pick one per analysis |
| Profile plot loose-replicate band wide | Genuine biological variability OR one replicate failed | Check per-replicate metrics (chipseq-qc); don't average across failing rep |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| bigWig has all zeros | Wrong chromosome naming (chr vs no chr) | `samtools view -H bam | head` to check; convert if needed |
| computeMatrix "all regions skipped" | BED chromosome naming mismatches bigWig | Match seqlevels |
| plotHeatmap colors compressed | `--zMin/--zMax` not set; outliers dominate | Set `--zMin -3 --zMax 3` or use percentile-based |
| IGV batch hangs | `exit` command missing; IGV waits for input | Always end batch script with `exit` |
| pyGenomeTracks region out of range | Region exceeds chromosome length | Verify region from `samtools view -H bam` |
| Spike-in scaled track has artifact stripes | Scale factor too extreme (>10x) | Verify spike-in reads adequate (>100k); check titration |

## References

- Ramírez F et al 2016 Nucleic Acids Res 44:W160 (deepTools)
- Lopez-Delisle L et al 2021 Bioinformatics 37:422 (pyGenomeTracks)
- Hahne F & Ivanek R 2016 Methods Mol Biol 1418:335 (Gviz)
- Gu Z et al 2018 BMC Genomics 19:234 (EnrichedHeatmap)
- Yu G et al 2015 Bioinformatics 31:2382 (ChIPseeker)
- Thorvaldsdóttir H et al 2013 Brief Bioinform 14:178 (IGV)
- ENCODE 2012 quality metrics (NSC/RSC; for cross-correlation context)

## Related Skills

- chip-seq/peak-calling - Peak files for heatmap reference regions
- chip-seq/chipseq-qc - QC plots (fingerprint, correlation) complement visualization
- chip-seq/spike-in-normalization - Spike-in-scaled bigWig generation
- chip-seq/differential-binding - Visualize differential peak signal
- chip-seq/super-enhancers - SE region visualization in tracks
- data-visualization/genome-tracks - General genome track patterns + IGV batch + pyGenomeTracks
- data-visualization/heatmaps-clustering - General heatmap conventions
<!-- END FILE: chip-seq/chipseq-visualization/SKILL.md -->

## 子目录：chip-seq/chromatin-state-segmentation

<!-- BEGIN FILE: chip-seq/chromatin-state-segmentation/SKILL.md -->
---
name: bio-chipseq-chromatin-state-segmentation
description: Segments the genome into chromatin states from combinatorial histone modification and chromatin factor ChIP-seq data. Uses ChromHMM (multivariate HMM on binarized signal, v1.27), Segway (Dynamic Bayesian Network on continuous signal), EpiSegMix (flexible-distribution HMM with duration modeling, 2024), EpiLogos (multi-biosample visualization), IDEAS (cell-type-aware joint), and full-stack ChromHMM (Vu Ernst 2022) for cross-cell-type segmentations. Handles state-count selection (15 vs 18 vs 25 states), binarization choice, OverlapEnrichment / NeighborhoodEnrichment downstream analysis, and cross-biosample integration. Use when learning chromatin states from a histone mark panel, characterizing learned states by genomic feature enrichment, or comparing chromatin landscapes across cell types.
tool_type: cli
primary_tool: ChromHMM
---

## Version Compatibility

Reference examples tested with: ChromHMM 1.27+, Segway 3.0+, EpiSegMix 1.0+, EpiLogos (Meuleman lab), IDEAS 1.20+, samtools 1.19+, bedtools 2.31+. ChromHMM requires Java 8+; runs as `java -mx<MEMORY> -jar ChromHMM.jar <command>`.

# Chromatin State Segmentation

**"Integrate multiple histone modification ChIP-seq tracks into chromatin states"** -> Learn a small set of recurring combinatorial patterns of histone marks (active promoter, active enhancer, poised enhancer, polycomb-repressed, heterochromatic, transcribed, etc.) and segment the genome by which state each region belongs to. Output: per-state genomic intervals, state-by-mark emission matrix, and state-state transition matrix.

- CLI (canonical): ChromHMM `BinarizeBam` -> `LearnModel` -> `OverlapEnrichment` / `NeighborhoodEnrichment`
- CLI (continuous signal): Segway `train` -> `posterior` -> `annotate`
- CLI (flexible distributions): EpiSegMix (2024)
- Visualization across biosamples: EpiLogos (Meuleman lab)
- Cell-type-aware joint: IDEAS

Chromatin state segmentation requires a panel of histone marks; minimum 4-5 marks (e.g., H3K4me3, H3K27ac, H3K4me1, H3K36me3, H3K27me3) for meaningful states. With fewer marks, simpler peak-based annotation (chipseq/peak-annotation) is more appropriate.

## Tool Taxonomy

| Tool | Method | Strength | Fails when |
|------|--------|----------|------------|
| **ChromHMM** (Ernst & Kellis 2012; v1.27 current) | Multivariate HMM on binarized 200 bp bins | Canonical; widely used; integrated with Roadmap Epigenomics 15-state model; mature toolchain | Binarization throws away signal quantitation; default 200 bp bins may be too coarse for sharp boundaries |
| **Segway** (Hoffman 2012) | Dynamic Bayesian Network on continuous signal | Higher resolution; uses signal magnitudes not binarized | More complex setup; slower; less standardized output |
| **EpiSegMix** (Schmitz, Aggarwal, Laufer, Walter, Salhab, Rahmann 2024 Bioinformatics 40:btae178) | HMM with flexible read-count distributions + duration modeling | Modern; handles both narrow and broad mark distributions in one model | Newer; smaller user base |
| **EpiLogos** (Meuleman lab) | Multi-biosample visualization tool | Built on top of ChromHMM/Segway segmentations; compare ChromHMM states across 100s of biosamples | Visualization tool, not a segmentation method itself |
| **IDEAS** (Zhang 2016) | Cell-type-aware joint inference | Across-cell-type segmentation respecting cell-type identity | Slower; complex parameter tuning |
| **EpiCSeg** (Mammana 2015) | Negative binomial mixture | Read-count-based; doesn't need binarization | Less standardized output |
| **GenoSTAN** | HMM with various emission distributions | Flexible | Less actively developed |
| **Roadmap 25-state model** (Kundaje 2015) | ChromHMM 25-state precomputed model | Reference for cross-cell-type interpretation | Requires the Roadmap imputed 12-mark panel |
| **Full-stack ChromHMM** (Vu Ernst 2022) | 100-state segmentation across 1032 datasets / 127 reference epigenomes | Comprehensive cross-tissue annotation | Computationally intensive to retrain |

## ChromHMM Workflow

ChromHMM is the de facto standard. The workflow has 4 stages:

### Step 1: Binarize ChIP-seq signal

```bash
# Build cellMarkFileTable: cell_type<TAB>mark<TAB>file<TAB>(optional control)
cat > cellMarkFileTable.txt << EOF
GM12878	H3K4me3	gm12878_h3k4me3.bam	gm12878_input.bam
GM12878	H3K27me3	gm12878_h3k27me3.bam	gm12878_input.bam
GM12878	H3K27ac	gm12878_h3k27ac.bam	gm12878_input.bam
GM12878	H3K4me1	gm12878_h3k4me1.bam	gm12878_input.bam
GM12878	H3K36me3	gm12878_h3k36me3.bam	gm12878_input.bam
EOF

# Binarize BAMs into 200 bp bins; emission = whether mark exceeds Poisson threshold
java -mx16G -jar ChromHMM.jar BinarizeBam \
    -b 200 \
    chromsizes_hg38.txt \
    bam_dir/ \
    cellMarkFileTable.txt \
    binarized_output/
```

Output: per-chromosome `_binary.txt` files, one row per 200 bp bin, columns = marks, values 0/1.

### Step 2: Learn model

```bash
# Train HMM with N states; common choices: 15, 18, 25
# 15 states: Ernst & Kellis 2011 model; canonical
# 18 states: extends with additional regulatory states
# 25 states: Roadmap Epigenomics extended model
java -mx16G -jar ChromHMM.jar LearnModel \
    -p 8 \
    binarized_output/ \
    model_15state/ \
    15 \
    hg38

# Output: model_15state.txt (emission + transition matrices),
# emissions_15.png (visualization), transitions_15.png,
# per-chromosome _segments.bed (state assignments)
# AND automatically runs OverlapEnrichment + NeighborhoodEnrichment
```

### Step 3: Interpret states from emission matrix

| Roadmap 15-state assignments (canonical) |
|-------------------------------------------|
| 1_TssA — Active TSS (high H3K4me3, H3K27ac) |
| 2_TssAFlnk — Flanking TSS (H3K4me3, H3K27ac, lower) |
| 3_TxFlnk — Transcript flanking |
| 4_Tx — Strong transcription (H3K36me3, H3K79me2 if available) |
| 5_TxWk — Weak transcription |
| 6_EnhG — Enhancer in gene body (H3K4me1, H3K27ac) |
| 7_Enh — Generic enhancer (H3K4me1, H3K27ac) |
| 8_ZNF/Rpts — Zinc-finger / repeats |
| 9_Het — Heterochromatin (H3K9me3) |
| 10_TssBiv — Bivalent TSS (H3K4me3 + H3K27me3) |
| 11_BivFlnk — Bivalent flanking |
| 12_EnhBiv — Bivalent enhancer (H3K4me1 + H3K27me3) |
| 13_ReprPC — Polycomb-repressed (H3K27me3) |
| 14_ReprPCWk — Weak Polycomb |
| 15_Quies — Quiescent (no signal) |

### Step 4: Functional enrichment of states

```bash
# OverlapEnrichment: enrichment of each state for external feature sets.
# Options (e.g. -labels) MUST precede the three positional args.
java -mx16G -jar ChromHMM.jar OverlapEnrichment \
    -labels \
    model_15state/GM12878_15_segments.bed \
    /path/to/anchor_files/ \
    enrichment_output/GM12878

# NeighborhoodEnrichment: enrichment relative to anchor positions (e.g., TSS)
java -mx16G -jar ChromHMM.jar NeighborhoodEnrichment \
    -labels \
    model_15state/GM12878_15_segments.bed \
    /path/to/tss_anchors.txt \
    enrichment_output/GM12878_TSS
```

Anchor files: BED files of features (CGIs, repeats, conserved elements, etc.) for OverlapEnrichment; position files for NeighborhoodEnrichment.

## Choosing State Count

| States | Use case | Mark panel size |
|--------|----------|-----------------|
| 8-10 | Initial exploration; small mark panel (3-4 marks) | 3-5 marks |
| 15 | Roadmap Epigenomics canonical | 5 core (H3K4me3, H3K4me1, H3K36me3, H3K27me3, H3K9me3) |
| 18 | Roadmap extended (adds H3K27ac -> fine enhancer subtypes) | 6 marks (core 5 + H3K27ac) |
| 25 | Roadmap Epigenomics extended; cross-cell-type compatibility | 12 imputed marks |
| 50+ | Full-stack model (Vu Ernst 2022) | Many marks across many cell types |

**Practical workflow:** Train at N=15, 18, 25; compare emission matrices; choose the smallest N where biology is interpretable. Higher N risks over-segmentation (state splitting random variation).

## Segway Workflow

```bash
# Segway reads only the Genomedata format, so first pack the signal tracks
# (one track per bigWig) plus the genome sequence into an archive.
genomedata-load \
    -s hg38.fa \
    -t h3k4me3=h3k4me3.bw \
    -t h3k27ac=h3k27ac.bw \
    -t h3k4me1=h3k4me1.bw \
    -t h3k36me3=h3k36me3.bw \
    -t h3k27me3=h3k27me3.bw \
    signal.genomedata

# Train Segway model; GENOMEDATA and TRAINDIR are positional
segway train \
    --num-labels=25 \
    --num-instances=3 \
    --resolution=100 \
    signal.genomedata traindir/

# Posterior probabilities + hard-call annotation (GENOMEDATA TRAINDIR OUTDIR, positional)
segway posterior signal.genomedata traindir/ posteriordir/
segway annotate signal.genomedata traindir/ identifydir/

# Output: identifydir/segway.bed.gz (state assignments)
```

Segway uses continuous signal (from the genomedata archive) vs ChromHMM's binarized bins. Trade-off: more information per region (continuous) but more complex training.

## EpiLogos Visualization

EpiLogos doesn't perform segmentation; it visualizes existing ChromHMM/Segway segmentations across many biosamples (epilogos.org).

```bash
# Use precomputed ChromHMM segmentations across multiple cell types
# Web interface: https://epilogos.altius.org/
# Local: github.com/meuleman/epilogos
```

Useful for: cross-cell-type comparison; identifying tissue-specific regulatory states; cohort-level chromatin landscape summaries.

## Full-Stack ChromHMM (Vu Ernst 2022)

The full-stack model trained on 1032 datasets / 127 reference epigenomes:

```bash
# Use precomputed model from Ernst lab
# github.com/ernstlab/full_stack_ChromHMM_annotations
# Annotate new sample by applying model to binarized data
java -mx16G -jar ChromHMM.jar MakeSegmentation \
    full_stack_model_100states.txt \
    binarized_sample/ \
    full_stack_output/
```

Useful for: applying a comprehensive cross-tissue annotation to a new sample; comparing to canonical Roadmap states.

## Per-Tool Failure Modes

### ChromHMM -- Bin size 200 bp too coarse for sharp boundaries

**Trigger:** Studying TF binding boundaries or sharp enhancer transitions at 200 bp resolution.

**Mechanism:** ChromHMM default 200 bp bins; biology may shift within a bin.

**Fix:** Reduce to `-b 100` or `-b 50` (smaller bin); increases memory and compute time but improves boundary resolution. Re-train model at finer resolution.

### ChromHMM -- Binarization throws away signal quantitation

**Trigger:** Distinguishing low- from high-signal regions of the same state.

**Mechanism:** ChromHMM binarizes each 200 bp bin to 0/1 per mark; state assignment uses combinatorial pattern, not magnitude.

**Fix:** Use Segway (continuous signal) or EpiSegMix (flexible distributions) for magnitude-aware segmentation.

### ChromHMM / Segway -- Wrong state count

**Trigger:** Training with N=50 states on a 4-mark panel; or N=10 on a 7-mark panel.

**Mechanism:** Excess states fragment biology; insufficient states force unrelated regions into the same state.

**Symptom:** Emission matrix shows redundant states (multiple states with same emission profile) at high N; or biologically distinct regions lumped together at low N.

**Fix:** Train at N=15, 18, 25; inspect emission matrix similarity; choose the smallest N where states are interpretable as distinct biology.

### Mark panel mismatch with model

**Trigger:** Applying Roadmap 25-state model to a sample with different mark panel.

**Mechanism:** Model was trained on specific marks; emission probabilities are mark-specific. Applying to different mark panel produces nonsensical state assignments.

**Fix:** Either train a new model on the available mark panel; OR ensure the exact same marks (and ordering) as used in the model.

### IgG control instead of input

**Trigger:** Using IgG controls in `BinarizeBam` for histone marks.

**Mechanism:** ChromHMM's binarization compares mark signal to control; histone mark biology assumes input (sonicated chromatin) as background, not IgG.

**Fix:** Use sonicated input as control for histone mark ChIP. IgG is not appropriate for ChromHMM binarization of histone marks.

### Cross-cell-type state mapping

**Trigger:** Training separate models per cell type and trying to compare state assignments.

**Mechanism:** State 5 in cell type A may not correspond to state 5 in cell type B if trained independently.

**Fix:** Train one model on concatenated data from all cell types (joint segmentation); or apply a single precomputed model (Roadmap 15-state, full-stack) to all samples for consistent state labels.

## Reconciliation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| ChromHMM and Segway segments differ | Different bin sizes / binarization vs continuous | Both can be valid; inspect emission matrices; pick the tool matching the resolution needs |
| State assignment varies wildly between replicates | Insufficient marks; over-binned | Increase mark panel; reduce state count |
| Active TSS state overlaps polycomb state at promoters | Bivalent biology (Bernstein 2006) | Expected for ESC-like cells; not an error; consider bivalent-specific state in N=18 model |
| Roadmap 25-state model annotates unknown cell type | Cross-cell-type generalization | Use cautiously; verify against tissue-specific tracks |
| Heterochromatin (H3K9me3) state has too many bins | H3K9me3 covers large fraction of genome | Expected; heterochromatin is genome-wide |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `java.lang.OutOfMemoryError` | Insufficient JVM heap | `java -mx32G -jar ChromHMM.jar ...` |
| `BinarizeBam` very slow | Large BAMs without index | `samtools index` all BAMs first |
| All states have similar emissions | Mark panel too small | Need at least 5 marks for canonical 15-state model |
| Segments file empty for some chromosomes | Chromosome not in chromsizes file | Add or use `-chrom` flag to restrict |
| State labels don't match Roadmap | Trained model independently | Use Roadmap precomputed model OR map states by emission similarity |
| ChromHMM "no signal in marks" | All bins binarized to 0 | Check signal quality; verify control normalization |

## References

- Ernst J & Kellis M 2012 Nat Methods 9:215 (ChromHMM v1)
- Ernst J & Kellis M 2017 Nat Protoc 12:2478 (ChromHMM protocol)
- Hoffman MM et al 2012 Nat Methods 9:473 (Segway)
- Schmitz JE, Aggarwal N, Laufer L, Walter J, Salhab A, Rahmann S 2024 Bioinformatics 40:btae178 (EpiSegMix)
- Meuleman W et al 2020 Nature 584:244 (EpiLogos / DHS index)
- Zhang Y & Hardison 2016 Nucleic Acids Res 44:6721 (IDEAS)
- Mammana A & Chung HR 2015 Genome Biol 16:151 (EpiCSeg)
- Roadmap Epigenomics Consortium 2015 Nature 518:317 (Roadmap 25-state model)
- Vu H & Ernst J 2022 Genome Biol 23:9 (full-stack ChromHMM)
- Kundaje A et al 2015 Nature 518:317 (Roadmap integrative analysis)

## Related Skills

- chip-seq/peak-calling - Peak calling per mark before segmentation
- chip-seq/chipseq-qc - Replicate concordance per mark; QC before integration
- chip-seq/peak-annotation - cCRE classification (PLS/pELS/dELS) complementary to chromatin states
- chip-seq/spike-in-normalization - Spike-in normalize per-mark BAMs before binarization for cross-condition state comparison
- atac-seq/single-cell-atac - scATAC + ChIP integration via multimodal methods
- machine-learning/model-validation - Model selection (state count); cross-validation
- data-visualization/genome-tracks - Visualize state segmentations
- gene-regulatory-networks/coexpression-networks - Cross-reference chromatin states with co-expression modules
<!-- END FILE: chip-seq/chromatin-state-segmentation/SKILL.md -->

## 子目录：chip-seq/cut-and-run-tag

<!-- BEGIN FILE: chip-seq/cut-and-run-tag/SKILL.md -->
---
name: bio-chipseq-cut-and-run-tag
description: Analyzes CUT&RUN (Skene Henikoff 2017) and CUT&Tag (Kaya-Okur 2019) chromatin profiling data. Handles SEACR vs MACS2 peak calling (with the btaf375 2025 benchmark guidance), pA-MNase vs pA-Tn5 vs pAG-Tn5 chimera differences, E. coli spike-in carryover normalization, IgG-only control logic (no input), characteristic fragment-size signatures (25-75 bp for CUT&Tag), and lower depth requirements (5M reads typical vs 25M for ChIP). Use when calling peaks from CUT&RUN/CUT&Tag, scaling by E. coli spike-in carryover, choosing SEACR norm mode, or comparing CUT&RUN/Tag results to traditional ChIP.
tool_type: mixed
primary_tool: SEACR
---

## Version Compatibility

Reference examples tested with: SEACR 1.3+, MACS2 2.2.9+, MACS3 3.0.4+, samtools 1.19+, bowtie2 2.5+, bedtools 2.31+, deepTools 3.5+, GoPeaks 1.0+, LanceOtron (pip).

# CUT&RUN / CUT&Tag

**"Analyze CUT&RUN or CUT&Tag chromatin profiling data"** -> Use the lower-background, lower-input alternatives to traditional ChIP. CUT&RUN tethers MNase to an antibody via Protein A; CUT&Tag tethers Tn5 via Protein A/G. Both bypass cross-linking, fragmentation, and IP washes — producing 10-100× lower background, allowing 100-1000× lower cell input, and shifting the peak-calling problem from "find signal in noise" to "find signal in near-zero background."

- Aligner: bowtie2 (CUT&RUN/Tag standard) or bwa-mem; chromap optional
- Peak calling (CUT&RUN/Tag): SEACR (Meers 2019), MACS2 with `-f BAMPE --keep-dup all`, or both for consensus
- Spike-in: E. coli carryover from bacterially-produced pA-MNase/Tn5 (automatic, variable)
- Control: IgG-only (no input control; native chromatin has no meaningful "input")

CUT&RUN/CUT&Tag has different QC thresholds, different peak calling defaults, different spike-in protocols, and different antibody requirements than traditional ChIP. Treating it as ChIP fails silently.

## Protocol Variant Taxonomy

| Variant | Chimera | Year | Use case | Failure mode |
|---------|---------|------|----------|--------------|
| **CUT&RUN** (Skene Henikoff) | pA-MNase | 2017 | Native chromatin profiling; broad antibody compatibility | Native (no fixation) — gentler; MNase digest needs careful Ca²⁺ control |
| **CUT&Tag** (Kaya-Okur Henikoff) | pA-Tn5 (rabbit only) | 2019 | Lower cell input (~5000); faster; library-ready output | Rabbit-only antibody; PCR cycles can over-amplify |
| **CUT&Tag-IT** (Active Motif) | pA-Tn5 commercial | 2020 | Standardized lots; reproducible | Cost; vendor-locked |
| **pAG-Tn5 CUT&Tag** | pAG-Tn5 | 2020 | Binds both rabbit AND mouse IgG | More versatile; identical performance otherwise |
| **AutoCut&Tag** | pAG-Tn5 plate-based | 2021 | High-throughput (96-well) | Throughput at the cost of per-sample optimization |
| **CUTAC** (CUT&Tag-then-ATAC) | pAG-Tn5 + protocol modification | 2020 | Chromatin accessibility variant of CUT&Tag | Less common; not standard CUT&Tag |
| **scCUT&Tag** | pAG-Tn5 in droplets | 2021 | Single-cell histone mark profiling | Very sparse (~1000-5000 reads/cell) |

## Algorithmic Taxonomy

| Tool | Model | Strength | Fails when |
|------|-------|----------|------------|
| **SEACR** (Meers 2019) | Empirical threshold on signal block totals; IgG-aware "stringent" mode | Designed for sparse CUT&RUN data; "stringent + norm + IgG" is the recommended default | Wrong mode (top-X% without IgG; "non" mode if no upstream spike-in normalization); broad mark with very flat signal landscape |
| **MACS2 `-f BAMPE --keep-dup all`** | Local Poisson | Familiar; integrates well with downstream tools (DiffBind) | Default `-q 0.05` may be too lenient for low-background CUT&Tag; consider `-q 0.01` |
| **GoPeaks** (Yashar 2022) | Sliding-window thresholding | Broad-mark-oriented; faster than SEACR on broad data | Newer; smaller user base |
| **LanceOtron** (Hentges 2022) | CNN trained on ENCODE peaks | Parameter-free; handles both narrow and broad | Less validated for CUT&RUN/Tag specifically; web-only or pip |
| **MACS2 + SEACR consensus** | Intersection | Highest confidence; conservative two-caller intersection | Most conservative; may miss true peaks at marginal regions |

**2025 benchmark (Bioinformatics 41:btaf375, Nooranikhojasteh et al):** benchmarked MACS2, SEACR, GoPeaks and LanceOtron on CUT&RUN.
- MACS2 better for sharp peaks (H3K4me3, TFs)
- SEACR gave the highest signal-to-noise across marks
- No single caller is universally optimal; the study favors careful parameter tuning or ensemble/consensus approaches over any single tool

## SEACR Workflow (Canonical CUT&RUN/Tag Caller)

**Goal:** Call CUT&RUN/CUT&Tag peaks from aligned BAMs using SEACR with IgG-aware threshold.

**Approach:** Align with Henikoff parameters, convert BAM to fragment bedGraph via bamtobed-bedpe, then invoke SEACR with `norm stringent` mode and IgG control.

```bash
# 1. Align with bowtie2 (Henikoff lab standard parameters)
bowtie2 --local --very-sensitive --no-mixed --no-discordant \
    --phred33 -I 10 -X 700 \
    -x hg38 -1 reads_R1.fq -2 reads_R2.fq \
    -S aln.sam

# 2. Convert SAM to BAM, sort, index
samtools view -bS aln.sam | samtools sort -o aln.bam
samtools index aln.bam

# 3. Generate bedGraph for SEACR (paired-end fragments)
samtools view -bS -F 0x04 aln.bam | bedtools bamtobed -bedpe -i - > aln.bedpe
awk '$1==$4 && $6-$2 < 1000 {print $0}' aln.bedpe > aln.clean.bedpe
cut -f 1,2,6 aln.clean.bedpe | sort -k1,1 -k2,2n -k3,3n > aln.fragments.bed
bedtools genomecov -bg -i aln.fragments.bed -g hg38.chrom.sizes > aln.bedgraph

# 4. Same for IgG control
# (... produce igg.bedgraph similarly ...)

# 5. SEACR with stringent + norm + IgG control (recommended default).
# Final argument is the OUTPUT PREFIX; SEACR appends ".stringent.bed" / ".relaxed.bed".
bash SEACR_1.3.sh aln.bedgraph igg.bedgraph norm stringent target_peaks
# Output file: target_peaks.stringent.bed

# Alternative: no IgG control, use top 1% of peaks
# bash SEACR_1.3.sh aln.bedgraph 0.01 non stringent target_peaks
```

**SEACR mode selection:**
- `norm` (recommended): scales target to IgG distribution
- `non`: use ONLY if upstream spike-in normalization was applied; otherwise use `norm`
- `stringent`: top-half of signal blocks (recommended default)
- `relaxed`: full distribution (use only for very sparse signal)
- IgG control: `bash SEACR_1.3.sh target.bg igg.bg norm stringent out_prefix` -> writes `out_prefix.stringent.bed`
- Top-X% without IgG: `bash SEACR_1.3.sh target.bg 0.01 non stringent out_prefix` -> writes `out_prefix.stringent.bed`

## E. coli Spike-In Carryover (Automatic Spike-In)

CUT&RUN/CUT&Tag spike-in is "free" because the pA-MNase or pA-Tn5 carries E. coli DNA from bacterial production. Carryover is variable across batches but stable within a batch.

```bash
# Align reads to combined hg38 + E. coli genome (or sequential)
bowtie2 -x hg38_ecoli_combined -1 R1.fq -2 R2.fq -S aln.sam

# Count E. coli reads per sample
ECOLI_READS=$(samtools view -c -F 4 aln.bam ecoli_chr1)

# Scaling factor: smallest E. coli read count / per-sample E. coli reads
# Apply BEFORE peak calling for cross-condition comparison
```

**Expected E. coli alignment fractions:**
- Target ChIP samples: 0.5-2% of total reads
- IgG control: 2-5% (higher because no target chromatin to dilute)
- Below 0.1% E. coli: spike-in carryover lost; cross-condition normalization unreliable
- Above 10%: target ChIP failed (mostly E. coli)

The carryover is variable between batches of bacterial production; single-experiment carryover spike-in is noisier than deliberate Drosophila spike-in (ChIP-Rx). For high-stakes cross-condition claims, add deliberate Drosophila spike-in despite the E. coli carryover. See chip-seq/spike-in-normalization.

## QC Differences from Traditional ChIP

| Metric | Traditional ChIP | CUT&RUN/CUT&Tag |
|--------|------------------|------------------|
| FRiP (TF) | > 0.05 | > 0.10 (often > 0.25) |
| FRiP (histone) | > 0.10 | > 0.25 |
| Library size requirement | 20-50M | 3-10M (often sufficient) |
| Input control | Required | IgG only (no input meaningful) |
| Fragment size (CUT&Tag) | Sub-nucleosomal or mono-nucleosomal | Sharp peak at 25-75 bp (Tn5 staggered cuts) |
| Fragment size (CUT&RUN) | Variable | Mono- + di-nucleosomal pattern |
| Duplicates | Remove (MarkDuplicates) | **Keep for CUT&Tag** (low PCR cycles, dups have biology) |
| Spike-in alignment | Deliberate (Drosophila); 0.5-5% | Automatic E. coli; 0.5-5% |
| Cell input | 1-10M | 5,000-100,000 |

**Critical: `--keep-dup all` in MACS for CUT&Tag.** PCR cycles are 12-15 (vs 5-8 for ChIP); duplicates at high-coverage TF binding sites contain biology. The MACS default `--keep-dup 1` (keeps one read per position) will over-deduplicate CUT&Tag data.

## Fragment Size as Diagnostic (Critical for CUT&Tag)

```bash
samtools view -f 0x2 sample.bam | awk '{print $9}' | awk '$1>0' \
    | sort -n | uniq -c | awk '{print $2, $1}' > frag_sizes.tsv
```

Expected for CUT&Tag:
- Sharp peak at 25-75 bp (Tn5 staggered insertion = ~9 bp + protein-DNA-protein interaction)
- Secondary peak at ~150-200 bp (mono-nucleosomal CUT&Tag from H3K4me3 etc)
- < 25 bp: Tn5 self-tagmentation noise; high abundance indicates over-tagmentation
- Flat distribution above 200 bp: poor enzyme activity or over-amplification

Expected for CUT&RUN:
- Mono-nucleosomal (~150 bp) for histone marks
- Sub-nucleosomal (~50-100 bp) for TFs (rare; CUT&RUN better for histones)
- Di-nucleosomal (~300 bp) secondary peak common

## Per-Tool Failure Modes

### SEACR -- Wrong mode for context

**Trigger:** Using `non` mode without prior spike-in normalization; using `relaxed` mode on standard CUT&Tag.

**Mechanism:** `non` assumes target is already scaled to IgG (typical for ChIP-Rx-style spike-in); on raw counts, it inflates false positives. `relaxed` includes the full distribution; appropriate only for sparse signal.

**Fix:** Default to `norm stringent` with IgG control. Use `non` only when upstream spike-in scaling has been applied.

### CUT&Tag MACS2 -- Default `--keep-dup 1` removes biology

**Trigger:** Using MACS2 default dedup settings on CUT&Tag.

**Mechanism:** Low PCR cycles (12-15) in CUT&Tag mean PCR duplicates contain real biology at high-coverage sites; auto-dedup over-filters.

**Symptom:** Peak counts much lower than published for same antibody / cell line.

**Fix:** `macs2 callpeak --keep-dup all -f BAMPE` for CUT&Tag. For CUT&RUN, dedup behavior depends on PCR cycles — verify with library complexity (NRF).

### pA-Tn5 vs pAG-Tn5 -- Antibody species mismatch

**Trigger:** Using pA-Tn5 (Henikoff original) with mouse primary antibody.

**Mechanism:** Protein A binds rabbit IgG much better than mouse IgG; mouse antibodies give weak signal with pA-Tn5.

**Fix:** Use pAG-Tn5 (binds both); or switch to a rabbit primary antibody for the same target.

### Digitonin permeabilization -- Wrong concentration

**Trigger:** Default 0.05% digitonin on all cell lines.

**Mechanism:** Optimal digitonin varies by cell type (some need 0.02%, some 0.1%); over-permeabilization releases chromatin into supernatant; under-permeabilization prevents antibody access.

**Symptom:** Inconsistent signal across cell lines; high IgG signal (under-permeabilized) or low target signal (over-permeabilized).

**Fix:** Titrate digitonin per cell line using a known-positive H3K4me3 antibody as control.

### ConA bead vs sepharose -- Volume / sample mismatch

**Trigger:** Switching bead type between protocols without adjusting volume.

**Mechanism:** ConA magnetic beads (e.g., Bangs) and sepharose ConA have different binding capacities; protocols designed for one give wrong cell loading for the other.

**Fix:** Follow Henikoff lab protocol exactly for the chosen bead; or titrate cell number per bead volume.

### Adapter readthrough in short fragments

**Trigger:** 100-150 bp reads on 25-75 bp CUT&Tag fragments.

**Mechanism:** Reads longer than fragments read through both adapters; downstream alignment loses the fragment.

**Symptom:** Many reads with adapter sequence at 3' end; alignment rate drops.

**Fix:** Aggressive adapter trimming with cutadapt: `-e 0.1 -O 5 --minimum-length 25`. Use 50 bp paired-end sequencing for CUT&Tag instead of 150 bp.

### MACS2 fragment-size modeling failure on CUT&Tag

**Trigger:** Running MACS2 without `-f BAMPE` on CUT&Tag PE data.

**Mechanism:** MACS2 in `-f BAM` mode tries to model fragment size from cross-correlation; CUT&Tag fragments are 25-75 bp, not the 200 bp ChIP expects; modeling fails or produces wrong estimate.

**Fix:** Always use `-f BAMPE` for CUT&Tag; MACS uses actual fragment spans from mate pairs.

## Reconciliation: When CUT&RUN/Tag Disagrees with ChIP

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Peak count much lower in CUT&Tag vs ChIP | Lower background reveals signal vs noise; CUT&Tag often has FEWER but cleaner peaks | Both correct; CUT&Tag specificity > sensitivity |
| Peak count much higher in CUT&Tag vs ChIP | `--keep-dup all` retained PCR duplicates as peaks | Verify NRF; if low, consider deduplicating with caution |
| Same antibody, different signal | Native chromatin vs cross-linked accessibility differs | Native CUT&RUN may miss DSG-dependent cofactors (BRD4); add brief fixation |
| FRiP very high (>50%) | Likely real for CUT&Tag (low background); confirm with motif enrichment | Verify motif enrichment at peaks; if missing, suspect technical artifact |
| H3K4me3 CUT&Tag peak count differs from ChIP | Expected; CUT&Tag has higher specificity | Trust CUT&Tag for sharp marks |
| H3K27me3 CUT&RUN/Tag misses regions | Broad domains require deeper sequencing; CUT&Tag was designed for sharp marks | Use CUT&RUN or traditional ChIP for very broad marks |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| SEACR "input file not bedgraph" | Wrong file format | Use `bedtools genomecov -bg`; not `bedGraphToBigWig` output |
| MACS2 modeling fails on CUT&Tag | Default `-f BAM` on PE | `-f BAMPE` |
| Peak count for mouse antibody | Used pA-Tn5 not pAG-Tn5 | Switch to pAG-Tn5 OR use rabbit primary |
| Very high adapter content in FASTQ | Read length > fragment length | Trim aggressively; consider 50 bp PE for CUT&Tag |
| Sample-to-sample carryover variability >5x | E. coli carryover variable between bacterial production batches | Add deliberate Drosophila spike-in for cross-condition |
| IgG signal as strong as target | Failed antibody / over-permeabilization | Validate antibody on positive control; titrate digitonin |

## References

- Skene PJ & Henikoff S 2017 eLife 6:e21856 (CUT&RUN)
- Skene PJ Henikoff JG & Henikoff S 2018 Nat Protoc 13:1006 (CUT&RUN protocol)
- Kaya-Okur HS et al 2019 Nat Commun 10:1930 (CUT&Tag)
- Kaya-Okur HS et al 2020 Nat Protoc 15:3264 (CUT&Tag protocol)
- Meers MP et al 2019 Epigenetics Chromatin 12:42 (SEACR)
- Nooranikhojasteh A et al 2025 Bioinformatics 41:btaf375 (CUT&RUN peak-caller benchmark)
- Yashar WM et al 2022 Genome Biol 23:144 (GoPeaks)
- Hentges LD et al 2022 Bioinformatics 38:4255 (LanceOtron)
- Bartosovic M Kabbe M & Castelo-Branco G 2021 Nat Biotechnol 39:825 (scCUT&Tag)
- Janssens DH et al 2021 Nat Genet 53:1586 (AutoCUT&Tag)
- Li Q et al 2024 Nat Methods 21:2044 (scNanoSeq-CUT&Tag, long-read single-cell CUT&Tag)

## Related Skills

- chip-seq/peak-calling - Traditional ChIP peak calling (MACS3 + IDR vs naive overlap)
- chip-seq/chipseq-qc - QC battery (different thresholds for CUT&RUN/Tag)
- chip-seq/spike-in-normalization - Deliberate Drosophila spike-in beyond E. coli carryover
- chip-seq/differential-binding - DiffBind / csaw differential on CUT&RUN/Tag
- chip-seq/peak-annotation - Annotate CUT&RUN/Tag peaks (same tools as ChIP)
- chip-seq/super-enhancers - SE calling on CUT&Tag H3K27ac
- alignment-files/sam-bam-basics - BAM preparation
- read-qc/adapter-trimming - Aggressive trimming for short fragments
<!-- END FILE: chip-seq/cut-and-run-tag/SKILL.md -->

## 子目录：chip-seq/differential-binding

<!-- BEGIN FILE: chip-seq/differential-binding/SKILL.md -->
---
name: bio-chipseq-differential-binding
description: Identifies differentially bound ChIP-seq regions between conditions using DiffBind, csaw (sliding windows), DESeq2/edgeR/PyDESeq2 on count matrices, NormR (control-aware), or MAnorm2. Distinguishes three distinct normalization problems (composition bias, trended bias, global shifts) and matches each to its appropriate fix including spike-in scaling. Use when comparing ChIP-seq binding between experimental conditions, choosing normalization for global vs local changes, integrating spike-in data, or reconciling DiffBind/DESeq2 disagreement.
tool_type: mixed
primary_tool: DiffBind
---

## Version Compatibility

Reference examples tested with: DiffBind 3.20+, DESeq2 1.42+, edgeR 4.0+, csaw 1.36+, PyDESeq2 0.5+, NormR 1.28+, MAnorm2 1.2+, ChIPseqSpikeInFree 1.6+.

DiffBind 3.0+ changed defaults: `summits=200` (was FALSE), `dba.normalize()` now required, blacklist filtering on by default, full library size normalization replaces reads-in-peaks. Always run `packageVersion('DiffBind')` and inspect `dba.normalize(obj, bRetrieve=TRUE)` to confirm what was applied.

# Differential ChIP-seq Binding

**"Compare protein-DNA binding between experimental conditions"** -> Identify regions where IP signal changes significantly, accounting for sequencing depth, composition bias, trended biases, and global shifts that confound naive normalization.

- R (BAM + peaks): `DiffBind::dba()` -> `dba.count()` -> `dba.normalize()` -> `dba.analyze()`
- R (count matrix): `DESeq2::DESeq()` or `edgeR::glmQLFTest()` on a peaks-by-samples matrix
- R (windows-based, global-shift-robust): `csaw::windowCounts()` -> `csaw::normFactors()` -> `edgeR::glmQLFTest()`
- R (control-aware): `normr::diffR(chip1.bam, chip2.bam, genome)` joint binomial mixture
- Python (count matrix): `pydeseq2.DeseqDataSet()`

Choice of normalization matters more than choice of test statistic (RLE vs TMM vs csaw bin-TMM on the same reference reads produce nearly identical results). Choose by which of the three normalization problems applies.

## The Three Distinct Normalization Problems

| Problem | Symptom on MA plot | Cause | Fix |
|---------|--------------------|-------|-----|
| **Composition bias** | Loess shifts off y=0 systematically | Few high-signal peaks dominate read counts; small fold changes look large or inverted | TMM on background 10 kb bins (csaw / DiffBind `background=TRUE`); NOT reads-in-peaks |
| **Trended bias (intensity-dependent)** | Loess curve sweeps from + to - across abundance | Library-prep efficiency varies with fragment abundance | Non-linear loess offsets (csaw `normOffsets`); use cautiously — can over-normalize biology |
| **Global shift (treatment changes most peaks)** | Loess entirely shifted off y=0; mean log2FC ≠ 0 | Drug/perturbation changes the genome-wide level of binding (HDACi, BETi, EZH2i, target KD) | Spike-in scaling (ChIP-Rx); no algorithmic fix works |

**Why this matters:** Most published ChIP-seq differential analyses default to RLE/TMM on reads-in-peaks, which assumes "most peaks are unchanged." For HDAC inhibitors, BET inhibitors, EZH2 inhibitors, or any large dosage / target-knockdown experiment, this assumption is violated. The algorithm forces the median log2FC to zero, hides the real effect, and amplifies noise around the new "zero." The result can have the wrong sign.

**Diagnostic:** Plot MA loess on differential results. A loess curve that sweeps abundance indicates trended bias. A uniformly shifted loess indicates a global shift. Both patterns together indicate normalization is failing in two ways simultaneously.

## Algorithmic Taxonomy

| Tool | Treats | Statistical model | Strength | Fails when |
|------|--------|-------------------|----------|------------|
| **DiffBind 3.20+** | Consensus peaks summit ± 200 bp (default) | DESeq2 or edgeR backend | Mature; integrated counting/normalization; spike-in support; blacklist filter on | Default `summits=200` recenters peaks (wrong for broad marks); `DBA_NORM_LIB` is conservative but misses global shifts unless `background=TRUE` |
| **DESeq2 (direct)** | Predefined peaks | NB GLM | Familiar; transparent | RLE on reads-in-peaks fails for global shifts |
| **edgeR (direct)** | Predefined peaks | NB GLM with TMM; quasi-likelihood F-test | Cleaner small-sample inference; QL-F controls type-I error | TMM on peak counts unstable if peaks globally shifting |
| **csaw** (Lun & Smyth 2016) | Sliding windows (typically 150 bp width, 50 bp shift) | edgeR QL-F | Gold-standard for global shifts; bin-TMM composition bias; loess for trended biases | Slower; requires BAMs not count matrix; window-merge step adds complexity |
| **NormR** (Helmuth 2016) | Genomic bins | Binomial mixture (background + enriched) | Control-aware; identifies enrichment/depletion/background simultaneously | Bin-level not peak-level; older codebase; less integration with downstream tools |
| **MAnorm2** (Tu 2021) | Peaks | Hierarchical model with mean-variance trend | Designed for cross-condition with replicates | Less widely adopted; sparse maintenance |
| **SpikChIP** (Blanco 2021) | Peaks | Spike-in-aware | Multi-sample spike-in comparison | Niche; specific spike-in protocol assumed |
| **SpikeFlow** (2024) | End-to-end | Snakemake pipeline: MACS2/EPIC2/EDD peaks + DESeq2 with spike-in size factors | Automated; multiple normalization options (RPM/RRPM/Rx-Input/downsampling) | Inherits experimental-design errors upstream |
| **ChIPComp** (Chen 2015) | Peaks | Joint Poisson with input | Control-aware | Older; less maintained |
| **ChIPseqSpikeInFree** (Jin 2020) | Peaks (post-hoc) | Distribution-shape inference | Detects global shift WITHOUT spike-in | Post-hoc heuristic only; not definitive; sanity check |

## Decision Tree: Choosing Normalization

| Scenario | Recommended | Tool / parameter |
|----------|-------------|------------------|
| Standard TF ChIP, local changes expected, balanced gain/loss | RLE on reads-in-peaks | DESeq2 default; DiffBind `DBA_NORM_RLE` |
| Histone marks, broad domains, local changes | TMM on background 10 kb bins | csaw `normFactors`; DiffBind `background=TRUE` |
| HDAC / BET / EZH2 inhibitor (global change) | Spike-in scaling | DiffBind `spikein=TRUE`; SpikeFlow; manual `sizeFactors()` from spike reads |
| Dosage titration, cell-cycle synchronization | Spike-in scaling | Same |
| ChIP target knockdown / degron | Spike-in or matched-input control subtraction | Spike-in preferred; bamCompare log2 ratio next |
| CUT&RUN/CUT&Tag standard | E. coli spike-in (carryover) | DiffBind custom scaling; see cut-and-run-tag |
| No spike-in available; suspect global shift | ChIPseqSpikeInFree | Post-hoc distribution-shape inference |
| Suspected trended (abundance-dependent) bias | Non-linear loess | csaw `normOffsets` |
| Genome-wide enrichment/depletion analysis | NormR | Binomial mixture |
| Many conditions, large peak set | edgeR QL-F or DiffBind+edgeR | Better type-I control than DESeq2 Wald |

## Spike-In Scaling Factor Calculation

ChIP-Rx (Orlando 2014) uses Drosophila chromatin spike-in added at fixed concentration BEFORE IP. Egan 2016 adds a fixed MASS of Drosophila S2 chromatin (matched to target chromatin by the ~27:1 human:fly genome-size ratio), not a fixed cell count.

**RRPM (reference-adjusted reads per million):**

```
scale_factor_i = min(N_spike_sample) / N_spike_sample_i
```

Apply to read counts pre-test, OR pass as `sizeFactors()` to DESeq2 / `normFactors()` to edgeR / a numeric library-size vector to DiffBind's `dba.normalize(..., library=...)`:

```r
spike_in_reads <- c(120000, 145000, 110000, 95000)  # per-sample Drosophila read count
sample_names <- c('ctrl_1', 'ctrl_2', 'treat_1', 'treat_2')
scale_factors <- min(spike_in_reads) / spike_in_reads
names(scale_factors) <- sample_names

# DESeq2 with spike-in size factors
sizeFactors(dds) <- 1 / scale_factors  # DESeq2 expects inverse convention

# Or directly via DiffBind 3.x (spikein = TRUE forces library = DBA_LIBSIZE_BACKGROUND internally)
dba_obj <- dba.normalize(dba_obj, spikein = TRUE,
                          normalize = DBA_NORM_LIB)
```

**Rx-Input variant** (Fursova 2019): additionally scale by input spike-in to correct IP efficiency variation.

**Internal-control sanity check:** After spike-in normalization, blacklist regions and constitutive housekeeping sites (U6 promoter, rRNA processing factors that are stable) should show no signal change. If they do, the normalization is broken — common causes:
- Spike-in scaling applied to peak counts instead of read counts
- Spike-in reads not deduplicated before scaling
- Spike-in genome not filtered for high-mapq before scaling
- Spike-in saturated (always 100k+ reads); check titration linearity

Per the Patel et al 2024 *Nat Biotechnol* survey, improper spike-in normalization is common: of 53 datasets examined, only 27 (~51%) had adequate matched input controls across conditions.

## DiffBind Workflow (BAMs + Peaks)

**Goal:** Run DiffBind from a sample sheet to consensus peaks, normalized counts, and tested differential binding.

**Approach:** Build sample sheet, count reads in consensus peaks (summit-centered for narrow marks, full peak width for broad), choose normalization based on the three-problem framework above, then test with DESeq2 or edgeR backend.

```r
library(DiffBind)

# Sample sheet: SampleID, Condition, Replicate, bamReads, bamControl, Peaks, PeakCaller
dba_obj <- dba(sampleSheet = 'samples.csv')

# Counting: summits=250 (narrow); FALSE for broad histones (use full peak width)
dba_obj <- dba.count(dba_obj, summits = 250, minOverlap = 2, bParallel = TRUE)

# Normalization — choose per the three-problem framework
dba_obj <- dba.normalize(dba_obj,                      # default: full library size
                          method = DBA_DESEQ2,
                          normalize = DBA_NORM_LIB,
                          library = DBA_LIBSIZE_FULL)

# Background bin TMM for composition bias / broad marks
# dba_obj <- dba.normalize(dba_obj, background = TRUE)

# Spike-in scaling for global shifts
# dba_obj <- dba.normalize(dba_obj, spikein = TRUE)

dba_obj <- dba.contrast(dba_obj, design = '~ Condition')
dba_obj <- dba.analyze(dba_obj, method = DBA_DESEQ2)

# Always inspect what was actually applied
dba.normalize(dba_obj, bRetrieve = TRUE)
```

DiffBind 3.20+ defaults (verified via `bRetrieve`):
- `summits = 200` — narrow recentering (set `FALSE` for broad histones)
- `library = DBA_LIBSIZE_FULL` — full library, conservative
- `normalize = DBA_NORM_LIB` — library size only, not reads-in-peaks RLE
- Blacklist filtering on
- `background = FALSE` — set `TRUE` for composition bias

## csaw Workflow (Windows-Based)

**Goal:** Detect differential binding from sliding windows without committing to predefined peaks; robust to composition bias via background bin TMM.

**Approach:** Count reads in overlapping windows, normalize on 10 kb bins (composition bias) and/or loess (trended bias), test with edgeR QL-F, then merge significant windows into regions.

```r
library(csaw)
library(edgeR)

bam_files <- c('ctrl_1.bam', 'ctrl_2.bam', 'treat_1.bam', 'treat_2.bam')
condition <- factor(c('ctrl', 'ctrl', 'treat', 'treat'))

# Window counts: 150 bp window, 50 bp spacing (sharp marks); 1-2 kb for broad
param <- readParam(minq = 30, pe = 'both', dedup = TRUE,
                    discard = import('hg38-blacklist.v2.bed'))
windows <- windowCounts(bam_files, width = 150, ext = 200, param = param)

# Composition bias via 10 kb bins (always applied for ChIP-seq)
bg_bins <- windowCounts(bam_files, bin = TRUE, width = 10000, param = param)
windows <- normFactors(bg_bins, se.out = windows)

# Optional: trended bias via non-linear loess (use cautiously)
# windows <- normOffsets(windows, se.out = TRUE)

# edgeR QL-F test
y <- asDGEList(windows)
design <- model.matrix(~condition)
y <- estimateDisp(y, design)
fit <- glmQLFit(y, design, robust = TRUE)
results <- glmQLFTest(fit, coef = 2)

# Merge significant windows within 1 kb into regions
merged <- mergeResults(windows, results$table, tol = 1000, merge.args = list(max.width = 5000))
```

For broad marks, increase window width to 1-2 kb and merge tolerance to 5 kb. For TFs, 150 bp window + 50 bp spacing is standard.

## DESeq2 from Count Matrix

```r
library(DESeq2)

counts <- read.delim('counts.tsv', row.names = 1, check.names = FALSE)
coldata <- data.frame(
    condition = factor(c('ctrl', 'ctrl', 'ctrl', 'treat', 'treat', 'treat')),
    row.names = colnames(counts)
)

dds <- DESeqDataSetFromMatrix(countData = counts, colData = coldata, design = ~ condition)

# Pre-filtering for ChIP-seq is LESS aggressive than RNA-seq (peaks already enriched)
keep <- rowSums(counts(dds)) >= 1  # remove only all-zero
dds <- dds[keep, ]
dds$condition <- relevel(dds$condition, ref = 'ctrl')

dds <- DESeq(dds)
res <- results(dds, alpha = 0.05)  # match independent-filtering optimization

# Optional: LFC shrinkage for ranking/visualization only — does NOT change padj
library(apeglm)
resLFC <- lfcShrink(dds, coef = 'condition_treat_vs_ctrl', type = 'apeglm')
```

For spike-in normalization, set `sizeFactors(dds)` from scaling factors before `DESeq(dds)`. For background-bin TMM (composition bias) use csaw to compute size factors, then transfer.

## Per-Tool Failure Modes

### DiffBind -- `summits=200` default destroys broad marks

**Trigger:** Default DiffBind 3.x call with histone broad marks (H3K27me3, H3K9me3).

**Mechanism:** `summits=200` re-centers peaks to summit ± 200 bp, throwing away most of a 10-100 kb broad domain.

**Symptom:** Differential count for broad marks much lower than expected; signal concentrated at narrow centers of broad regions.

**Fix:** `dba.count(obj, summits = FALSE, ...)` for broad marks; OR use full-width consensus peaks; OR switch to csaw with 1-2 kb windows.

### DiffBind -- `DBA_NORM_RLE` reads-in-peaks default reverses global shifts

**Trigger:** Default (legacy DiffBind < 3.0) OR explicitly setting `normalize = DBA_NORM_RLE` on a global-shift experiment.

**Mechanism:** RLE on reads-in-peaks assumes most peaks unchanged. If 80% of peaks lose signal (e.g., EZH2 inhibitor on H3K27me3), the size factors compensate by inflating the "lost" peaks' normalized values toward control levels.

**Symptom:** Differential results show fewer peaks changed than visually obvious; or signs are wrong (gain reported where loss occurred).

**Fix:** Switch to `background = TRUE` (bin TMM); for definitive analysis use `spikein = TRUE` with ChIP-Rx.

### DESeq2 -- Pre-filtering removes condition-specific peaks

**Trigger:** Applying RNA-seq-style filter `rowSums(counts) >= 10` to ChIP-seq counts.

**Mechanism:** A peak present in treatment but absent in control has near-zero control counts. Aggressive filtering removes truly differential peaks.

**Symptom:** Significantly differential gains-of-binding peaks missing from results.

**Fix:** `rowSums(counts) >= 1` only (remove all-zero rows); accept the loss of statistical power vs. recovering true differential peaks.

### csaw -- Trended bias loess over-normalizes biology

**Trigger:** Applying `normOffsets()` (loess) when the abundance-dependent shift IS the biology.

**Mechanism:** Loess fits a smooth curve to the MA-plot trend; if treatment uniformly increases binding at low-signal peaks (which is biology), loess interprets it as a technical trend and removes it.

**Symptom:** No differential peaks detected despite obvious treatment effect.

**Fix:** Use bin-TMM only (composition bias); apply loess only after confirming the trend is technical (e.g., it appears in IgG-only samples).

### Spike-in normalization -- Scaling factor applied to wrong layer

**Trigger:** Multiplying peak counts by spike-in scaling factor.

**Mechanism:** Spike-in factors are for read-level normalization; applied to peak counts they double-correct (peak counts already reflect mapped reads).

**Symptom:** Effect sizes shifted by 2-10× from expected biology; internal-control regions show artifactual signal change.

**Fix:** Apply spike-in via `sizeFactors(dds)` (DESeq2) or `normFactors` (edgeR) BEFORE the test; or via `bamCoverage --scaleFactor` for browser tracks. Never multiply peak-level counts.

### IDR-passing peaks not used as differential input

**Trigger:** Using per-replicate MACS calls (loose `-p 1e-2`) as DiffBind peak input.

**Mechanism:** Loose ENCODE-pattern peaks include many low-confidence calls; DiffBind's `minOverlap = 2` may not filter aggressively enough.

**Symptom:** Differential results dominated by noise at marginal peaks; high false-positive rate.

**Fix:** Pre-filter peak input to IDR-passing peaks (TF) or naive-overlap-passing peaks (histone) before DiffBind ingestion.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| DiffBind + DESeq2 directly differ wildly | Different normalization (DiffBind default = library size; DESeq2 default = RLE) | Force same normalization; differences should shrink to <5% |
| csaw windows + DiffBind peaks disagree | csaw catches sub-peak local maxima or wider regions DiffBind missed | Inspect IGV; csaw windows-based often more sensitive to broad/diffuse changes |
| Spike-in scaled + non-scaled give opposite signs | Global shift present | Spike-in is correct; non-scaled is fooled by composition bias |
| DiffBind run twice gives different results | Different `summits` or `minOverlap` settings | Verify via `dba.normalize(obj, bRetrieve=TRUE)`; pin parameters in script |
| Few replicates, large fold changes, low padj | DESeq2 dispersion estimate unstable with n=2 | Switch to edgeR QL-F or DiffBind with edgeR backend |
| Different fold changes in DiffBind 3.x vs 2.x | Default normalization changed | Match settings explicitly; document version in methods |

**Operational rule for publication-grade:** Run on ENCODE-pattern peaks (IDR or naive overlap-passing), normalize with both reads-in-peaks AND background-bin AND spike-in if available; require concordance across at least two methods. For global-shift experiments, spike-in is mandatory.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `Error: dba.normalize() must be called before dba.analyze()` | DiffBind 3.x change; not in older docs | Add `dba.normalize(obj)` step |
| DiffBind very slow on many samples | Sequential counting | `dba.count(obj, bParallel = TRUE)` |
| `Error in DESeq()` with few replicates | Dispersion estimation unstable | Use `DESeq(dds, fitType = 'parametric', sfType = 'poscounts')` or switch to edgeR |
| Spike-in size factors mostly NA | Spike-in reads not in sample sheet or wrong BAM path | Verify spike-in BAM exists; load via DiffBind `spikein` field |
| All padj = NA | Independent filtering too aggressive | Lower `alpha` in `results()` to match intended threshold |
| Volcano plot inverted (down peaks on right) | Contrast direction reversed | `contrast = c('condition', 'treat', 'ctrl')` for positive log2FC = up in treat |

## References

- Stark R & Brown G 2011 Bioconductor (DiffBind)
- Lun ATL & Smyth GK 2016 Nucleic Acids Res 44:e45 (csaw)
- Love MI et al 2014 Genome Biol 15:550 (DESeq2)
- Robinson MD et al 2010 Bioinformatics 26:139 (edgeR; TMM)
- Helmuth J et al 2016 bioRxiv (NormR)
- Tu S et al 2021 Genome Res 31:131 (MAnorm2)
- Orlando DA et al 2014 Cell Rep 9:1163 (ChIP-Rx framework)
- Egan B et al 2016 PLoS One 11:e0166438 (ChIP-Rx protocol)
- Fursova NA et al 2019 Mol Cell 74:1020 (Rx-Input scaling)
- Jin H et al 2020 Bioinformatics 36:1270 (ChIPseqSpikeInFree)
- Blanco E et al 2021 NAR Genom Bioinform 3:lqab064 (SpikChIP)
- Patel L, Cao Y, Mendenhall EM, Benner C, Goren A 2024 Nat Biotechnol 42:1343 (review of spike-in normalization failure modes; PMC12266361)
- Bressan D et al 2024 NAR Genom Bioinform 6:lqae118 (SpikeFlow Snakemake pipeline)

## Related Skills

- chip-seq/peak-calling - Upstream peak calling for DiffBind input
- chip-seq/chipseq-qc - Replicate concordance required before differential
- chip-seq/spike-in-normalization - Detailed spike-in workflow and scaling factor calculation
- chip-seq/cut-and-run-tag - CUT&RUN/CUT&Tag uses E. coli spike-in (different from Drosophila ChIP-Rx)
- chip-seq/peak-annotation - Annotate differential peaks to genes/cCREs
- differential-expression/deseq2-basics - DESeq2 fundamentals
- differential-expression/edger-basics - edgeR quasi-likelihood framework
- atac-seq/differential-accessibility - Parallel ATAC differential workflow
<!-- END FILE: chip-seq/differential-binding/SKILL.md -->

## 子目录：chip-seq/motif-analysis

<!-- BEGIN FILE: chip-seq/motif-analysis/SKILL.md -->
---
name: bio-chipseq-motif-analysis
description: Discovers de novo motifs and tests known motif enrichment in ChIP-seq, ATAC-seq, or other peak sequences using HOMER, MEME-ChIP (STREME, CentriMo, TOMTOM, FIMO), monaLisa, and AME. Handles background selection (GC-matched, dinucleotide-shuffled, Markov order-2, peak-flanks), motif databases (JASPAR 2024 CORE PWMs, JASPAR 2026 deep-learning collection, HOCOMOCO v12, HOMER built-in), centrally-enriched motif testing, and differential motif analysis. Use when identifying TF binding motifs in peaks, testing for known TF enrichment, scanning for motif instances, comparing motif content between conditions, or interpreting motifs from deep learning models.
tool_type: cli
primary_tool: HOMER
---

## Version Compatibility

Reference examples tested with: HOMER 4.11+, MEME suite 5.5+ (STREME replaces DREME from 5.4+), monaLisa 1.10+, JASPAR 2024 CORE, HOCOMOCO v12, BioPython 1.83+, bedtools 2.31+.

DREME was removed from MEME suite 5.4+; use STREME instead. Some tutorials still reference DREME — verify the installed version via `meme --version`. JASPAR 2026 (released late 2025) integrates 1259 BPNet ChIP models in a Deep Learning collection; the CORE collection remains the standard PWM source.

# Motif Analysis on ChIP-seq Peaks

**"Find enriched DNA binding motifs in my ChIP-seq peaks"** -> Discover de novo motif patterns and test for known TF motif enrichment in peak sequences, with appropriate background to control for compositional and positional biases.

- CLI (HOMER, fast): `findMotifsGenome.pl peaks.bed hg38 outdir/ -size 200 -p 8`
- CLI (MEME-ChIP, comprehensive): `meme-chip -db JASPAR.meme peaks.fa`
- R (regression-based, selective enrichment): `monaLisa::calcBinnedMotifEnrR(seqs, bins, pwms)`
- CLI (deep-learning-derived motifs): TF-MoDISco on BPNet attribution scores (see chip-deep-learning)

Motif discovery is sensitive to background choice and peak quality. Hyper-ChIPable artifacts at rRNA / housekeeping loci often produce false-positive motifs (GC-rich or A-T-rich biases of those regions). Filter peaks against blacklists and inspect peak distribution before running motif discovery.

## Tool Taxonomy

| Tool | Discovery type | Background handling | Strength | Fails when |
|------|----------------|---------------------|----------|------------|
| **HOMER findMotifsGenome.pl** | De novo + known | GC-matched genomic regions (auto) | Fast (multi-core); integrated vertebrate/insect/plant DBs; one-command full report | Background can include unmasked repeats producing motif artifacts; `-size given` slow; auto background may include peaks themselves |
| **MEME-ChIP** | De novo (STREME, MEME) + central enrichment (CentriMo) + DB comparison (TOMTOM) + scanning (FIMO) | Markov order-2 from input; shuffled (preserves dinucleotide) | Comprehensive single command; rigorous statistics; HTML report | Slower; sequences must be 100-500 bp; central enrichment requires summit-centered peaks |
| **STREME** (MEME 5.4+) | De novo (replaced DREME) | Markov order-2 | Bailey 2021 benchmark: more accurate than DREME/HOMER/MEME/Peak-motifs; handles 3-30 bp; scales to 100k+ sequences | Memory-hungry for very long sequences (>1 kb) |
| **MEME** (classical) | De novo (long, gapped) | Markov | Long motifs; gapped motifs | Slow (no parallel); replaced by STREME for short motifs |
| **DREME** | De novo (short) | Shuffled | Historical; small fast | Removed from MEME 5.4+; use STREME |
| **monaLisa** (Stadler lab) | Binned enrichment regression | Native (binned scoring) | Modern; regression-based; selectivity (TF-specific in differential peaks) | R-only; less integrated with browsers |
| **AME** (MEME suite) | Known motif differential | Matched background set required | Designed for two-set comparison (e.g., peaks vs. control regions) | Requires user-provided background set |
| **CentriMo** | Known motif central enrichment | Auto from input | Tests positional enrichment relative to peak center | Requires summit-centered peaks (200-500 bp) |
| **FIMO** | Motif scanning | Markov model | Genome-wide scanning at user-set p-value | Many false positives at p ≤ 1e-4; tighten to 1e-5 for whole-genome |
| **HOMER scanMotifGenomeWide.pl** | Motif scanning | None | Genome-wide scanning at fixed score threshold | Less calibrated than FIMO; HOMER's PWM format |
| **RSAT peak-motifs** | De novo + known | k-mer comparison | Web-server; multi-tool ensemble | Web limits; less reproducible from CLI |
| **TF-MoDISco** | DL attribution-based | Implicit in model | Motifs from BPNet/chromBPNet attribution scores; captures soft motif syntax | Requires trained DL model; see chip-deep-learning |

## Background Selection — The Biggest Source of Error

Motif enrichment p-values are conditional on the background distribution. Wrong background produces wrong motifs.

| Background | What it preserves | Use case | Limitation |
|------------|-------------------|----------|------------|
| **GC-matched genomic regions** | Mononucleotide composition; chromatin context | TF motifs; avoid GC-bias artifacts | Doesn't preserve dinucleotide (CpG, TpA) |
| **Dinucleotide-shuffled** | CpG and TpA frequencies | Short motifs; avoiding repeat-derived artifacts | Doesn't capture genomic position context |
| **Markov order-2 (trinucleotide)** | Trinucleotide context | Compositional control; STREME/MEME default | Doesn't capture chromatin context |
| **Peak-flanking sequences** (±500 bp upstream/downstream of peak) | Local genomic context | When peak GC differs from genome | May contain shared regulatory motifs if peaks cluster |
| **Repeat-masked input** | Sequence with repeats replaced by N | Avoid TE-derived motif artifacts | Loses motifs in evolved-from-repeat regulatory elements |
| **Input control peaks** | Open-chromatin / artifact regions | TF discrimination from generic chromatin | Hard to obtain; controversial |
| **Differential set** (AME) | Treatment-condition-specific peaks vs ctrl peaks | Differential motif enrichment | Requires a control peak set |

**Practical default:** STREME / MEME-ChIP with Markov order-2 (built-in default); HOMER with `-mask` flag (mask repeats); always inspect for repeat-derived motifs (e.g., Alu-derived AluY consensus, LINE motifs).

## Window Around Summit Matters

Motif enrichment improves dramatically when sequences are summit-centered:

| Window | When |
|--------|------|
| ±100 bp (200 bp total) | Sharp TFs (CTCF, p53); summit reliably reflects motif position |
| ±150-250 bp (300-500 bp) | Most TFs and sharp histones; balance of motif coverage and noise |
| Full peak width (`-size given`) | Variable-width broad marks; computationally expensive |
| Whole gene body (>1 kb) | Almost always wrong; dilutes motif signal |

**For ChIP-seq broad histone marks (H3K27me3, H3K9me3) motif analysis is generally NOT informative** — these marks reflect Polycomb / heterochromatin domains without sequence-specific binding. Motif analysis applies to TFs and to histone marks deposited by sequence-specific cofactors (H3K27ac partial, since BRD4 reads acetyl).

## HOMER Workflow

```bash
# De novo + known motif discovery, repeat-masked, GC-matched background
findMotifsGenome.pl peaks.narrowPeak hg38 homer_out/ \
    -size 200 \
    -mask \
    -p 8

# With user-supplied background (e.g., control peaks or random genomic)
findMotifsGenome.pl peaks.narrowPeak hg38 homer_out/ \
    -size 200 -mask -p 8 \
    -bg background_peaks.bed

# Known motifs only (skip de novo; faster)
findMotifsGenome.pl peaks.narrowPeak hg38 homer_known_only/ \
    -size 200 -mask -nomotif

# Differential motif analysis: peaks gained in condition A vs condition B
findMotifsGenome.pl gained_in_A.bed hg38 differential_motifs/ \
    -size 200 -mask -bg gained_in_B.bed
```

HOMER output files:
- `homerResults.html` — de novo motifs ranked by significance
- `knownResults.html` — known motif enrichment
- `homerMotifs.all.motifs` — all de novo motifs (PWM format)
- `knownResults.txt` — tab-separated known motif stats

## MEME-ChIP Workflow

```bash
# Center peaks to ±100 bp around summit (column 10 in narrowPeak)
awk 'BEGIN{OFS="\t"} {summit = $2 + $10; print $1, summit - 100, summit + 100, $4, $5, $6}' \
    peaks.narrowPeak > peaks_centered.bed
bedtools getfasta -fi hg38.fa -bed peaks_centered.bed -fo peaks_centered.fa

# Full MEME-ChIP analysis
meme-chip \
    -oc meme_chip_out/ \
    -db JASPAR2024_CORE_vertebrates_non-redundant_pfms_meme.txt \
    -meme-nmotifs 5 \
    -streme-nmotifs 10 \
    -minw 6 -maxw 20 \
    peaks_centered.fa

# MEME-ChIP runs: STREME (replaces DREME) + MEME + CentriMo + TOMTOM + FIMO
# CentriMo tests known motifs for central enrichment — strongest signal of
# direct binding vs. tethered/indirect binding
```

## monaLisa Workflow (R, Regression-Based)

**Goal:** Test which TF motifs are enriched in specific bins of peaks (e.g., bins of differential log2FC, or bins of accessibility).

**Approach:** monaLisa builds a per-motif regression of peak signal on motif occurrence, controlling for GC content. Selective for TFs that discriminate between bins.

```r
library(monaLisa)
library(JASPAR2024)
library(TFBSTools)
library(Biostrings)
library(BSgenome.Hsapiens.UCSC.hg38)

# Load peaks and split into bins (e.g., quintiles of log2FC)
peaks <- rtracklayer::import('peaks.bed')
peaks$log2FC <- ...  # from differential analysis
bins <- bin(peaks$log2FC, binmode = 'equalN', nElements = 200)

# Get sequences around peak centers
seqs <- getSeq(BSgenome.Hsapiens.UCSC.hg38, resize(peaks, width = 500, fix = 'center'))

# Load JASPAR PWMs
pwms <- getMatrixSet(RSQLite::dbConnect(RSQLite::SQLite(), db(JASPAR2024())), list(species = 9606, collection = 'CORE'))

# Compute binned motif enrichment with GC control
res <- calcBinnedMotifEnrR(seqs = seqs, bins = bins, pwmL = pwms, BPPARAM = MulticoreParam(8))

# Plot heatmap of motif enrichment vs bins
plotMotifHeatmaps(x = res, which.plots = c('log2enr', 'negLog10P'),
                   width = 1.8, maxEnr = 2, maxSig = 10)
```

## Per-Tool Failure Modes

### HOMER -- Background includes peaks themselves

**Trigger:** Running `findMotifsGenome.pl` without `-bg` on a large peak set covering >5% of genome.

**Mechanism:** HOMER auto-samples GC-matched genomic regions for background, which can overlap the peak set itself.

**Symptom:** Even known TF motif p-values are weak (>1e-3); de novo motifs less enriched than expected.

**Fix:** Supply explicit `-bg` background (e.g., random genomic intervals matching peak count and width) OR use MEME-ChIP with internal shuffled background.

### HOMER / MEME -- Repeat-derived false-positive motifs

**Trigger:** Running on unmasked peaks; peaks cover transposable elements (Alu, LINE, LTR).

**Mechanism:** TEs contain over-represented k-mers that motif algorithms mistake for biology.

**Symptom:** Top de novo motif matches AluY consensus (~280 bp), LINE/L1, or LTR families.

**Fix:** Use `-mask` (HOMER) or pre-mask peak sequences with RepeatMasker; verify TOMTOM matches against legitimate TF databases.

### STREME -- Memory failure on long sequences

**Trigger:** Running STREME on full-peak sequences (>1 kb each) with > 50k peaks.

**Mechanism:** STREME holds suffix structures in memory; long sequences explode RAM.

**Fix:** Resize peaks to ±100-250 bp summit-centered before STREME; or downsample peak count.

### CentriMo -- No central enrichment due to wrong centering

**Trigger:** Using full peak coordinates (BED `start, end`) without recentering on summit.

**Mechanism:** Peak start coordinate is the left edge, not the summit; motif may be enriched near the summit but appears unenriched relative to the start.

**Symptom:** Known TF motifs show no central enrichment despite being clearly enriched overall.

**Fix:** Recenter sequences on summit: `summit = start + summit_offset` (narrowPeak column 10) before extracting FASTA.

### FIMO -- Massive false positives at default p ≤ 1e-4

**Trigger:** Genome-wide scanning at FIMO default p-value threshold.

**Mechanism:** At p ≤ 1e-4, expect ~3M random matches in a 3 Gb genome; most are false positives.

**Symptom:** FIMO output has millions of motif "hits"; can't distinguish real binding.

**Fix:** Tighten to `--thresh 1e-5` or stricter for genome-wide scans; or restrict scan to peaks: `fimo --bgfile motif_bg motif.meme peaks.fa`.

### monaLisa -- GC bins not respected

**Trigger:** Running `calcBinnedMotifEnrR` without GC binning when peaks have systematic GC differences (e.g., promoters vs distal enhancers).

**Mechanism:** GC-rich motifs are over-enriched in GC-rich bins simply by chance.

**Symptom:** Top motifs are CpG-rich families (e.g., E2F, NRF1) regardless of biology.

**Fix:** Use `background = 'genome'` with GC-matched genomic background; or `background = 'otherBins'` with stratified GC.

### Motif analysis on hyper-ChIPable regions

**Trigger:** Running motifs on peaks dominated by hyper-ChIPable artifacts (rRNA, tRNA, housekeeping).

**Mechanism:** These regions have systematic compositional biases (GC-rich, A-T-rich, repeat-derived); motifs from artifact peaks reflect compositional biology, not TF binding.

**Symptom:** Top de novo motif matches no known TF; high-GC or low-complexity consensus.

**Fix:** Apply blacklist + custom hyper-ChIPable filter (top-1% input signal) before motif analysis. See chipseq-qc.

## Reconciliation: When Motif Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| HOMER finds motif X; MEME-ChIP misses | Different background; HOMER may have permissive background | Run MEME-ChIP with explicit GC-matched background; check |
| MEME finds long gapped motif; STREME doesn't | MEME captures variable-length structure; STREME limited to 30 bp | Both are correct; report MEME for long motifs |
| Top de novo motif doesn't match TOMTOM databases | Novel motif OR repeat artifact OR compositional artifact | Inspect peaks for repeats; check input control; could be genuine novel TF |
| Known motif enriched but no de novo recovery | Insufficient enrichment for de novo; or motif is degenerate | Trust known motif enrichment; de novo needs strong signal |
| Differential motif gained in treatment but TF expression unchanged | TF post-translational regulation (binding mode change without expression change) | Check ChIP signal at known TF target genes; not a contradiction |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| HOMER "configureHomer.pl genome not installed" | Genome not configured | `perl configureHomer.pl -install hg38` (one-time) |
| MEME "sequence too short" | Peaks < motif min width | Resize peaks to ≥ 200 bp |
| MEME-ChIP "out of memory" | Too many long sequences | Resize peaks to ±100-250 bp; downsample |
| No enriched motifs | Peak quality / hyper-ChIPable / wrong background | Check FRiP, filter blacklist, supply explicit background |
| Top motif is GC-rich consensus | GC-bias in peaks not matched by background | GC-matched background (HOMER `-bg` or MEME shuffled with order-2) |
| FIMO produces millions of hits | p-value threshold too loose | `--thresh 1e-5` for whole-genome; restrict to peaks for finer p |
| TOMTOM matches always say "no match" | Motif database species mismatch | Use vertebrates / insects / plants DB matching organism |

## References

- Heinz S et al 2010 Mol Cell 38:576 (HOMER)
- Bailey TL & Elkan C 1994 Proc ISMB (MEME)
- Bailey TL 2021 Bioinformatics 37:2834 (STREME)
- Machanick P & Bailey TL 2011 Bioinformatics 27:1696 (MEME-ChIP)
- Bailey TL et al 2015 Nucleic Acids Res 43:W39 (MEME suite update)
- Grant CE et al 2011 Bioinformatics 27:1017 (FIMO)
- Bailey TL & Machanick P 2012 Nucleic Acids Res 40:e128 (CentriMo)
- McLeay RC & Bailey TL 2010 BMC Bioinformatics 11:165 (AME)
- Machlab D et al 2022 Bioinformatics 38:2624 (monaLisa)
- Castro-Mondragon JA et al 2022 Nucleic Acids Res 50:D165 (JASPAR 2022; CORE collection)
- Avsec Ž et al 2021 Nat Genet 53:354 (BPNet; soft motif syntax)
- Shrikumar A et al 2018 (rev. 2020) arXiv:1811.00416 (TF-MoDISco)

## Related Skills

- chip-seq/peak-calling - Upstream peak calling; recenter on summit for motif input
- chip-seq/chipseq-qc - Filter hyper-ChIPable artifacts before motif discovery
- chip-seq/chip-deep-learning - BPNet/chromBPNet for sequence-attribution motif discovery (TF-MoDISco)
- chip-seq/peak-annotation - Annotate peaks before motif discovery to filter promoters vs enhancers
- atac-seq/motif-deviation - chromVAR per-cell motif activity (ATAC-specific)
- atac-seq/footprinting - TOBIAS footprint analysis (ATAC; complementary to motif enrichment)
- sequence-manipulation/motif-search - General sequence motif scanning
- genome-intervals/proximity-operations - bedtools getfasta to extract peak sequences
<!-- END FILE: chip-seq/motif-analysis/SKILL.md -->

## 子目录：chip-seq/peak-annotation

<!-- BEGIN FILE: chip-seq/peak-annotation/SKILL.md -->
---
name: bio-chipseq-peak-annotation
description: Annotates ChIP-seq peaks to genomic features, nearest genes, ENCODE candidate cis-regulatory elements (cCREs), and regulatory domains. Uses ChIPseeker (R), HOMER annotatePeaks.pl (CLI), pyranges (Python), GREAT/rGREAT (regulatory domain gene-set enrichment), ChIP-Enrich (locus-length-adjusted), ENCODE SCREEN cCRE classification (PLS/pELS/dELS/CA-CTCF/CA-H3K4me3), and ENCODE-rE2G for cell-type-specific enhancer-gene linking. Handles nearest-TSS vs host-gene ambiguity, promoter window definition, and feature priority. Use when assigning genomic context to peaks, linking enhancer peaks to target genes, classifying peaks against ENCODE cCRE registry, or running gene-set enrichment on peak-associated genes.
tool_type: mixed
primary_tool: ChIPseeker
---

## Version Compatibility

Reference examples tested with: ChIPseeker 1.38+, GenomicFeatures 1.54+, rtracklayer 1.62+, HOMER 4.11+, rGREAT 2.4+, chipenrich 2.26+, pyranges 0.0.129+, pandas 2.2+.

ENCODE cCRE registry expanded to 2.37M human and 967k mouse elements (Moore JE et al 2026 Nature). SCREEN web app at screen.encodeproject.org provides browser access; ENCODE provides bed files for batch annotation.

# Peak Annotation

**"What genes and regulatory elements do my peaks correspond to?"** -> Assign each peak to a genomic feature (promoter, exon, intron, intergenic), its target gene (via nearest-TSS or host-gene), and where applicable an ENCODE cCRE class (PLS/pELS/dELS/CA-CTCF/CA-H3K4me3).

- R (gene-feature): `ChIPseeker::annotatePeak(peaks, TxDb=txdb)`
- CLI (gene-feature): `annotatePeaks.pl peaks.bed hg38 -gtf annotation.gtf`
- Python (custom): pyranges + pandas
- R (cCRE classification): intersect peaks with ENCODE cCRE BED from SCREEN
- R (gene-set enrichment): `rGREAT::great()` or `chipenrich::chipenrich()`

The single biggest source of misinterpretation is the **nearest-TSS vs host-gene** distinction (see below). For enhancer-driven biology, ENCODE-rE2G or ABC (in atac-seq/enhancer-gene-linking) is more accurate than nearest-TSS.

## Choosing an Annotation Approach

| Context | Recommended | Why |
|---------|-------------|-----|
| Standard genome, pre-built annotations available | ChIPseeker with TxDb package | Simplest; automatic gene symbol mapping via annoDb |
| Custom or project-specific GTF | ChIPseeker + makeTxDbFromGFF, HOMER -gtf, or pyranges | All three handle custom annotations |
| HOMER already in pipeline | HOMER annotatePeaks.pl | Reuses tag directory; combined with motif workflow |
| Fine-grained control | pyranges (Python) | Full control over priority rules, distance calculation |
| Enhancer peaks (distal regulatory) | GREAT / rGREAT | Regulatory domain assignment (basal + extension), not just nearest |
| Cell-type-specific enhancer-gene linking | ENCODE-rE2G | Modern (2024); ABC-trained logistic regression with chromatin context |
| Gene-set enrichment with locus-length adjustment | chipenrich / Broad-Enrich | Corrects for systematic gene-length bias in peak assignment |
| Compare against ENCODE cCRE atlas | SCREEN cCRE BED intersect | Cross-reference standard regulatory registry |
| Promoter-coverage decomposition | bedtools intersect with TSS windows | Quick stats per peak set |

**Critical:** Use the same annotation source as the alignment (UCSC knownGene TxDb with GENCODE GTF alignment causes mismatches). When a specific GTF is provided, use it directly via `makeTxDbFromGFF` rather than a mismatched pre-built TxDb package.

## Nearest-TSS vs Host-Gene Convention

Peak annotation involves two decisions that should be coupled but often aren't:
1. Which gene to assign (target gene)
2. What feature the peak overlaps (promoter / exon / intron / intergenic)

Default tools decouple these, producing internally inconsistent annotations.

| Convention | Gene from | Feature from | Tools |
|------------|-----------|---------------|-------|
| Nearest-TSS (default) | Gene with closest TSS | Physical overlap at peak center | ChIPseeker `overlap='TSS'` (default), HOMER |
| Host-gene priority | Gene whose body contains the peak | Same gene's features | ChIPseeker `overlap='all'` |

**Example failure:** Peak inside gene A's intron, near gene B's TSS. Default tools report `nearest_gene=B, feature=intron` — but the intron belongs to gene A, not gene B. The annotation is internally inconsistent.

### Choosing per Biology

| Context | Convention | Rationale |
|---------|-----------|-----------|
| Distal TF binding (enhancers) | Nearest-TSS, but prefer ENCODE-rE2G / ABC | Enhancers can regulate gene A despite sitting in gene B's intron |
| Histone marks in gene bodies (H3K36me3, H3K27me3) | Host-gene | Mark reflects host transcriptional state |
| Promoter-associated marks (H3K4me3, H3K27ac at promoters) | Either | Most peaks at promoters where conventions agree |
| Custom annotation against project GTF | Host-gene | Internal consistency |
| Reproducing published HOMER results | Nearest-TSS | Matches HOMER default |

When a task says "nearest gene," clarify which definition. For most annotation purposes where gene + feature should be consistent, use host-gene; for distal enhancer biology, use a proper enhancer-gene linker (ENCODE-rE2G, ABC).

## Coordinate Systems and TSS

BED uses 0-based half-open `[start, end)`. GTF uses 1-based closed `[start, end]`. Mixing without conversion shifts annotations by one base.

**Peak center (BED):** `(start + end) // 2`

**TSS from GTF (1-based to 0-based):**
- Plus-strand: `tss_0based = start - 1`
- Minus-strand: `tss_0based = end`

**Signed distance** (negative = upstream of TSS):
- Plus-strand: `distance = peak_center - tss`
- Minus-strand: `distance = -(peak_center - tss)`

## ChIPseeker (R)

**Goal:** Assign each ChIP-seq peak to a gene and a feature category using a transcript database.

**Approach:** Load the TxDb (pre-built or custom-built from GTF), pass peaks to `annotatePeak()` with the desired `tssRegion` window and `overlap` convention (host-gene vs nearest-TSS), then export the annotated data frame with gene symbols mapped from `annoDb` or the original GTF.

**Standard genome:**

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(org.Hs.eg.db)

peaks <- readPeakFile('peaks.narrowPeak')
peak_anno <- annotatePeak(peaks,
                           TxDb = TxDb.Hsapiens.UCSC.hg38.knownGene,
                           tssRegion = c(-2000, 2000),
                           annoDb = 'org.Hs.eg.db',
                           overlap = 'all')   # host-gene convention
anno_df <- as.data.frame(peak_anno)
```

**Custom GTF** (use makeTxDbFromGFF; map symbols from original GTF since custom TxDb objects lack annoDb mappings):

```r
library(GenomicFeatures)
library(rtracklayer)

txdb <- makeTxDbFromGFF('genes.gtf.gz', format = 'gtf')
peaks <- readPeakFile('peaks.bed')
peak_anno <- annotatePeak(peaks, TxDb = txdb, tssRegion = c(-2000, 2000),
                           overlap = 'all')

gtf <- import('genes.gtf.gz')
gene_map <- unique(data.frame(
    gene_id = sub('\\..*', '', gtf$gene_id),
    symbol = gtf$gene_name, stringsAsFactors = FALSE))
gene_map <- gene_map[!is.na(gene_map$symbol), ]
anno_df <- as.data.frame(peak_anno)
anno_df$gene_id_base <- sub('\\..*', '', anno_df$geneId)
anno_df$SYMBOL <- gene_map$symbol[match(anno_df$gene_id_base, gene_map$gene_id)]
```

GENCODE gene IDs have version suffixes (`ENSG00000142192.25`); strip before joining.

**Promoter window:** `tssRegion = c(-2000, 2000)` is common; `c(-3000, 3000)` is ChIPseeker default. Match to analysis requirements.

**Feature priority:** Default `Promoter > 5'UTR > 3'UTR > Exon > Intron > Downstream > Intergenic`. A peak in both a promoter (gene A) and an intron (gene B) receives "Promoter (gene A)" by default.

## HOMER annotatePeaks.pl (CLI)

```bash
# Standard genome (HOMER's installed annotation)
annotatePeaks.pl peaks.bed hg38 > annotated.txt

# Custom GTF (overrides HOMER's default)
annotatePeaks.pl peaks.bed hg38 -gtf genes.gtf > annotated.txt

# Without installed genome, GTF only
annotatePeaks.pl peaks.bed none -gtf genes.gtf > annotated.txt

# Generate annotation statistics
annotatePeaks.pl peaks.bed hg38 -gtf genes.gtf -annStats stats.txt > annotated.txt
```

HOMER's 19-column output: columns 8 (Annotation), 10 (Distance to TSS), 16 (Gene Name) are the primary annotation columns.

**HOMER promoter window is fixed at -1kb / +100bp** — not configurable via flags. For custom windows, reclassify using the Distance to TSS column post-hoc.

## ENCODE cCRE Classification

The ENCODE Registry of candidate cis-Regulatory Elements (cCREs) provides 2.37M human + 967k mouse elements. Registry V4 uses an 8-class scheme (the older V3 "CTCF-only" and "DNase-H3K4me3" were renamed CA-CTCF and CA-H3K4me3):

| Class | Definition | Marker pattern |
|-------|------------|-----------------|
| **PLS** (Promoter-Like Signature) | ≤ 200 bp of annotated TSS; high DNase + high H3K4me3 | DNase + H3K4me3 |
| **pELS** (Proximal Enhancer-Like Signature) | ≤ 2 kb of TSS; enhancer-like (DNase + H3K27ac, low H3K4me3) | DNase + H3K27ac |
| **dELS** (Distal Enhancer-Like Signature) | > 2 kb of TSS; enhancer-like | DNase + H3K27ac |
| **CA-H3K4me3** | Chromatin-accessible + H3K4me3, not TSS-proximal | DNase + H3K4me3 |
| **CA-CTCF** | Chromatin-accessible + CTCF (potential boundary) | DNase + CTCF |
| **CA-TF** | Chromatin-accessible + TF binding | DNase + TF |
| **CA** | Chromatin-accessible only | DNase |
| **TF** | TF-bound, not highly accessible | TF |

```bash
# Download ENCODE cCRE BED from SCREEN (GRCh38, expanded Registry-V4, uncompressed)
wget https://downloads.wenglab.org/Registry-V4/GRCh38-cCREs.bed

# Intersect peaks with cCRE; -wa preserves peak coords, -wb adds cCRE class
bedtools intersect -a peaks.narrowPeak -b GRCh38-cCREs.bed -wa -wb \
    > peaks_ccre.tsv
```

Cross-referencing peaks against cCREs:
- Indicates whether peaks overlap canonical regulatory elements
- Provides the cCRE class (PLS / pELS / dELS / CA-CTCF / CA-H3K4me3)
- Cell-type-specific activity profiles available via SCREEN web app

## GREAT / rGREAT (Regulatory Domain Gene-Set Enrichment)

GREAT (McLean 2010) addresses two problems with standard gene-set enrichment on peaks:
1. Peak-to-gene assignment via regulatory domains (not nearest TSS)
2. Statistical correction for region-locus length bias

**Regulatory domain rules** (default):
- Basal domain: -5 kb / +1 kb of TSS
- Extension: up to 1 Mb in each direction, OR until reaching neighbor's basal domain
- Each peak is assigned to ALL genes whose regulatory domain it overlaps (not just nearest)

```r
library(rGREAT)

# Submit peaks for regulatory-domain gene-set enrichment
res <- great(gr = peaks, gene_sets = 'GO:BP', tss_source = 'TxDb.Hsapiens.UCSC.hg38.knownGene',
              biomart_dataset = 'hsapiens_gene_ensembl')

# Top enriched gene sets
table_results <- getEnrichmentTable(res)
head(table_results)

# Visualization (local great() returns a GreatObject -> plotRegionGeneAssociations)
plotVolcano(res)
plotRegionGeneAssociations(res)
```

GREAT is most appropriate for distal regulatory elements (enhancer ChIP, ATAC). For promoter-focused marks (H3K4me3), ChIP-Enrich is more standard.

## ChIP-Enrich (Locus-Length-Adjusted Gene-Set Enrichment)

Welch 2014: standard gene-set enrichment on peak-associated genes systematically over-counts long genes. ChIP-Enrich models locus length as a covariate.

```r
library(chipenrich)

res <- chipenrich(peaks = 'peaks.bed', genome = 'hg38',
                   genesets = 'GOBP', locusdef = 'nearest_tss',
                   out_name = 'chipenrich_out', n_cores = 4)
# Locus definitions: nearest_tss, nearest_gene, exon, intron, 1kb, 5kb, 10kb
# method= accepts chipenrich (default) or fet; broadenrich() and polyenrich() are separate functions
```

For broad marks (H3K27me3, H3K9me3): use the separate `broadenrich(peaks = 'peaks.bed', genome = 'hg38', genesets = 'GOBP', locusdef = 'nearest_tss')` function, which accounts for region width.

## ENCODE-rE2G (Modern Enhancer-Gene Linking)

ENCODE-rE2G (2024) replaces ABC for cell types with ENCODE data. Cell-type-specific logistic-regression weights map distal enhancer peaks to target genes with higher accuracy than nearest-TSS or basal+extension.

See atac-seq/enhancer-gene-linking for full workflow; the same model applies to ChIP-seq enhancer marks (H3K27ac, H3K4me1, H3K4me2).

## Per-Tool Failure Modes

### ChIPseeker -- TxDb / annoDb genome mismatch

**Trigger:** Using hg19 TxDb on hg38-aligned BAMs / peaks.

**Mechanism:** Silent; ChIPseeker doesn't verify genome assembly.

**Symptom:** Annotated gene symbols look reasonable but distance-to-TSS is wrong; promoter / intron classifications drift.

**Fix:** Match TxDb to BAM alignment genome explicitly; verify with `seqlevels(peaks) == seqlevels(txdb)`.

### ChIPseeker -- Default `overlap='TSS'` decouples gene from feature

**Trigger:** Default annotation call on peaks in gene bodies.

**Mechanism:** `overlap='TSS'` assigns nearest gene by TSS; feature classification is independent of that gene.

**Symptom:** Annotation reports `nearest_gene=X, feature=intron` where the intron belongs to a different gene.

**Fix:** Pass `overlap='all'` for host-gene-consistent annotation; or accept TSS-only convention and clarify in methods.

### ChIPseeker -- Custom TxDb has no annoDb

**Trigger:** Building TxDb from GTF and passing `annoDb='org.Hs.eg.db'`.

**Mechanism:** Custom TxDb lacks the gene_id-to-symbol mapping that org.Hs.eg.db provides; ChIPseeker silently returns NA for symbols.

**Fix:** Map symbols separately from the original GTF after annotation; strip Ensembl version suffixes before joining.

### HOMER -- Hard-coded promoter window

**Trigger:** Needing a 2 kb or 5 kb promoter window with HOMER.

**Mechanism:** HOMER's promoter classification is hard-coded to -1 kb / +100 bp; not configurable.

**Fix:** Post-hoc reclassify using `Distance to TSS` column:
```bash
awk -F'\t' 'NR>1 { dist = ($10 < 0) ? -$10 : $10; \
    feat = (dist <= 2000) ? "promoter_custom" : $8; \
    print $2, $3, $4, $16, $10, feat }' OFS='\t' annotated.txt
```

### GREAT -- Default regulatory domain inappropriate for some species / cell types

**Trigger:** Using default basal+extension on insect or compact-genome data.

**Mechanism:** 1 Mb maximum extension assumes vertebrate-scale enhancer-target distances; not appropriate for organisms with shorter regulatory ranges.

**Fix:** Adjust `extension` parameter; for non-default species, configure regulatory domain explicitly.

### GREAT -- Hyper-ChIPable peaks inflate enrichment

**Trigger:** Including unfiltered peaks at rRNA / housekeeping / mtDNA in GREAT analysis.

**Mechanism:** Hyper-ChIPable artifacts are enriched at highly-transcribed loci; GREAT assigns them to associated genes, inflating GO terms for "translation" and "ribosomal" categories.

**Symptom:** Top enriched GO terms always include "ribosomal", "translation", "mitochondrion" regardless of biology.

**Fix:** Blacklist filter + custom hyper-ChIPable filter (top-1% input signal) before GREAT.

### ENCODE cCRE -- Cell-type-agnostic vs specific

**Trigger:** Using the master cCRE BED (cell-type-agnostic) to claim cell-type-specific regulatory activity.

**Mechanism:** Master cCRE BED is the union across all cell types. Specific activity profile per cell type is a separate dataset.

**Fix:** Use SCREEN web app or per-cell-type activity profiles for cell-type-specific claims.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| ChIPseeker nearest-TSS gene ≠ HOMER nearest gene | Different TSS reference; HOMER uses RefSeq | Verify both use same TxDb / RefSeq + UCSC knownGene |
| GREAT enrichment ≠ ChIP-Enrich enrichment | GREAT uses regulatory domain; ChIP-Enrich uses locus length adjustment | Both are valid; use GREAT for distal regulatory, ChIP-Enrich for promoter-focused |
| Peak overlaps cCRE but classified differently than expected | Cell-type-specific activity profile not used | Check SCREEN per-cell-type profile |
| Enhancer peak's nearest gene differs from ENCODE-rE2G target | ENCODE-rE2G uses cell-type chromatin context | Use ENCODE-rE2G for cell-type-specific enhancer-gene claims |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `seqlevels` mismatch in ChIPseeker | chr vs no-chr naming | `seqlevelsStyle(peaks) <- 'UCSC'` |
| Gene symbols all NA in ChIPseeker | Custom TxDb without annoDb | Map symbols from original GTF |
| HOMER reports "no annotation" | Genome not installed | `perl configureHomer.pl -install hg38` |
| rGREAT timeout | Large peak set + slow biomart | Use pre-computed gene sets; lower peak count |
| chipenrich slow | Default locusdef computed on-the-fly | Use built-in locusdef shortcuts (`nearest_tss`, `1kb`) |
| pyranges feature-overlap result missing strand | pyranges 0.x conversion drops strand by default | Pass `strandedness='same'` to overlap operations |

## References

- Yu G et al 2015 Bioinformatics 31:2382 (ChIPseeker)
- Heinz S et al 2010 Mol Cell 38:576 (HOMER annotatePeaks)
- McLean CY et al 2010 Nat Biotechnol 28:495 (GREAT)
- Gu Z 2023 Bioinformatics 39:btac745 (rGREAT)
- Welch RP et al 2014 Nucleic Acids Res 42:e105 (ChIP-Enrich)
- Cavalcante RG, Lee C, Welch RP, ... Sartor MA 2014 Bioinformatics 30:i393-i400 (Broad-Enrich)
- ENCODE Project Consortium 2020 Nature 583:699 (cCRE registry v1)
- Moore JE et al 2026 Nature (expanded cCRE registry, 2.37M human + 967k mouse elements)
- Fulco CP et al 2019 Nat Genet 51:1664 (ABC model precursor to ENCODE-rE2G)
- Kundaje lab / ENCODE 2024 (ENCODE-rE2G)
- SCREEN: screen.encodeproject.org

## Related Skills

- chip-seq/peak-calling - Generate peaks for annotation
- chip-seq/chipseq-qc - Filter hyper-ChIPable peaks before GREAT / chipenrich
- chip-seq/super-enhancers - Annotate SE-associated genes
- chip-seq/differential-binding - Annotate differential peaks
- atac-seq/enhancer-gene-linking - ENCODE-rE2G workflow for cell-type-specific E-G linking
- pathway-analysis/go-enrichment - Standard GO enrichment on peak-associated genes
- pathway-analysis/reactome-pathways - Reactome pathway enrichment
- genome-intervals/gtf-gff-handling - Parse and convert GTF/GFF
- genome-intervals/proximity-operations - bedtools closest and window operations
<!-- END FILE: chip-seq/peak-annotation/SKILL.md -->

## 子目录：chip-seq/peak-calling

<!-- BEGIN FILE: chip-seq/peak-calling/SKILL.md -->
---
name: bio-chipseq-peak-calling
description: Calls ChIP-seq peaks with MACS3, MACS2, HOMER, or SPP across narrow (TF) and broad (histone) modes. Handles input control matching, fragment-size modeling vs --nomodel, effective genome size, ENCODE-style IDR vs naive overlap, hyper-ChIPable artifacts, and aligner-specific shifts. Use when calling peaks from ChIP-seq alignments, choosing between narrow vs broad mode for a histone mark, deciding model vs nomodel for low-depth data, applying ENCODE pseudoreplicate IDR, or reconciling MACS vs HOMER vs SPP results.
tool_type: cli
primary_tool: macs3
---

## Version Compatibility

Reference examples tested with: MACS3 3.0.4+, MACS2 2.2.9+, HOMER 4.11+, SPP 1.16+, samtools 1.19+, bedtools 2.31+, IDR 2.0.4+.

Before running, verify versions: `<tool> --version` and `<tool> --help` to confirm flags. If a flag is missing, check the changelog — MACS2->MACS3 is API-compatible for `callpeak` but `predictd`, `bdgpeakcall`, and `hmmratac` differ.

# ChIP-seq Peak Calling

**"Identify protein-DNA binding sites from ChIP-seq alignments"** -> Detect statistically enriched genomic regions by comparing IP signal to input control (or genomic background), with peak shape (narrow/broad) determined by target biology (TF vs histone mark).

- CLI (ENCODE TF default): `macs2 callpeak -t chip.bam -c input.bam -f BAM -g hs -n sample --keep-dup all -p 1e-2`
- CLI (ENCODE histone default): same with `--broad --broad-cutoff 0.1` for H3K27me3, H3K9me3, H3K36me3
- CLI (alternative): `macs3 callpeak ...` (API-identical, active development), HOMER `findPeaks tags/ -style histone -i input_tags/`, SPP via phantompeakqualtools wrapper

ENCODE TF pipeline still uses **SPP for peak ranking + IDR**, with MACS2 producing the signal tracks. Histone pipeline uses **MACS2 + naive overlap** (IDR is too conservative for histone signal dynamic range). MACS3 is the actively maintained successor; MACS2 receives only bug fixes.

## Critical Pre-Call Validation

Before any peak calling, three things must be true or the output is unreliable:

1. **Antibody validated** — KO/KD orthogonal control, peptide-array specificity for histone modifications, or vendor-provided CRISPR-validated lot (Epicypher, CST). "ChIP-grade" marketing is not validation. See chipseq-qc.
2. **Fragment-size distribution is sane** — TF ChIP should show sub-nucleosomal (~50-100 bp) enrichment; histone ChIP should show clean mono- (~150) and di-nucleosomal (~300) peaks. Flat distribution = over-sonication; rescue is impossible. Check via `samtools view -f 0x2 sample.bam | awk '{print $9}' | sort | uniq -c`.
3. **Input control matches** — Sonicated input is biased toward open chromatin; MNase input toward nucleosomes. Input from a different library prep batch or fragmentation method introduces bias that subtraction cannot fix.

## Algorithmic Taxonomy

| Tool | Model | Treats fragments as | Strength | Fails when |
|------|-------|---------------------|----------|------------|
| MACS3/MACS2 callpeak | Dynamic local Poisson (max of genome-wide, 1kb, 5kb, 10kb lambda) + BH-FDR | Single-end shifts; PE fragments via BAMPE | Mature, fast, ENCODE-default, narrow + broad modes, integrated signal tracks | Confounds NFR with broad accessible domains; default narrow mode segments broad enrichment; assumes most genome NOT enriched (breaks for genome-wide marks) |
| SPP (Kharchenko 2008) | Strand cross-correlation peak detection + Poisson fold-enrichment | Single-end with cross-corr-derived shift | ENCODE TF caller; integrated NSC/RSC QC; robust for sharp TF peaks | Underperforms for broad marks; older R codebase; phantompeakqualtools wrapper has R-version compatibility issues |
| HOMER `-style factor` | Fixed-width peaks + three sequential filters (control / local / clonal) | Tag positions; auto-estimated width | Fast on tag directories; clonal filter `-C` removes PCR-artifact peaks | Less calibrated p-values; fixed width clips variable-width factor binding |
| HOMER `-style histone` | Variable-width region stitching (500 bp blocks, 1000 bp gap merging); L=0 (no local enrichment) | Tag positions | Captures variable-width histone enrichment; Omnipeak benchmark (Shpynov & Artyomov 2026): outperforms `-style factor` for histone marks including H3K4me3 | Less sensitive than MACS for very sharp TF binding |
| Genrich `-y` (ChIP mode) | q-value on log-transformed p-value, joint replicate model | Whole fragments (PE intervals) | Joint replicate analysis; chrM exclusion via `-e chrM`; auto blacklist via `-E` | Less peer-reviewed than MACS/SPP; thin literature; control handling less mature |
| MACS3 hmmratac | 3-state HMM on fragment-size signal | Fragment-size classes | Best for ATAC, not ChIP | Wrong tool for ChIP; ChIP fragment-size distribution doesn't drive useful HMM states |
| SEACR (Meers 2019) | Empirical threshold on signal block totals | Bedgraph signal blocks | Designed for sparse CUT&RUN/CUT&Tag data; "stringent" mode with IgG strongly preferred | Not for traditional ChIP-seq (assumes near-zero background); see cut-and-run-tag |
| LanceOtron (Hentges 2022) | CNN trained on ENCODE peaks | bigWig signal | Competitive for both narrow and broad without parameter tuning | Newer; less validated; web-only or pip install |

For CUT&RUN / CUT&Tag specifically, see chip-seq/cut-and-run-tag — protocol differences (lower depth, IgG-only control, E. coli spike-in carryover) drive different caller choice (MACS2 + SEACR consensus, not MACS3 alone).

## Decision: Narrow vs Broad

Driven by target biology, not preference. Calling broad mode does not make a sharp signal broad; it changes how MACS stitches adjacent enrichment.

| Target | Mode | Why |
|--------|------|-----|
| Transcription factors (CTCF, p53, GATA1, FOXA1) | Narrow (default) | Discrete motif binding produces sharp peaks |
| H3K4me3, H3K27ac at promoters/enhancers | Narrow | Localized at regulatory elements |
| H3K4me1 at enhancers | Narrow or broad-cutoff 0.1 | Variable; check published data for the cell type |
| H3K36me3, H3K79me2 (elongation) | Broad | Deposited across active gene bodies (5-50 kb domains) |
| H3K27me3, H3K9me3 (repressive) | Broad | Spread across 10-100+ kb domains |
| H4K20me3 (constitutive het) | Broad | Heterochromatin domains |
| Pol II (RNAPII) | Narrow at promoter + broad option for elongation profile | Two separate analyses if doing elongation biology |

For HOMER: use `-style histone` for ALL histone marks (Omnipeak benchmark, Shpynov & Artyomov 2026 NAR 54:gkaf1454); `-style factor` ONLY for transcription factors.

## Decision: Model vs --nomodel

MACS2/3 fragment-size modeling needs ≥100 paired plus/minus enrichment regions within `--mfold` (default `[5, 50]`). Silent failure produces wrong fragment size and warped peaks — always inspect `_model.r` output.

| Condition | Model? | Fallback |
|-----------|--------|----------|
| Whole-genome, ≥1M treatment reads, narrow TF | Yes | `--mfold 3 50` if fails |
| Paired-end with `-f BAMPE` | N/A | Fragment size from mate pairs |
| Single chromosome or targeted capture | No | `--nomodel --extsize <data-derived or mark default>` |
| Low read count (<500k) | No | Same |
| Broad histone mark | Either | Mark-type default if no estimate available |

When `--nomodel` is required, choose `--extsize` in priority order: (1) cross-correlation estimate from phantompeakqualtools (ENCODE standard, gives NSC/RSC simultaneously); (2) `macs3 predictd -i chip.bam -g hs` and read stderr; (3) mark-type fallback (147 for nucleosome-proximal marks, 200 for broader marks).

## Effective Genome Size — Often Wrong, Always Matters

`-g hs` (2.7e9) and `-g mm` (1.87e9) are decade-old approximations. Modern read-length-matched values (deepTools `effectiveGenomeSize` table):

| Genome | Read length | Effective size |
|--------|-------------|----------------|
| hg38 | 50 bp | 2.701e9 |
| hg38 | 75 bp | 2.748e9 |
| hg38 | 100 bp | 2.806e9 |
| hg38 | 150 bp | 2.862e9 |
| mm10 | 50 bp | 2.308e9 |
| mm10 | 100 bp | 2.467e9 |

Wrong size shifts every q-value but rarely peak ranks. For subset data (single chromosome, targeted), provide numeric `-g <bp>`; the shorthand inflates lambda_BG by 60× and produces false positives at low-signal regions.

## Hyper-ChIPable Regions Are a Persistent Artifact

Teytelman 2013 (PNAS) and Park 2013 (PLoS One) demonstrated that highly-transcribed genes (rRNA, tRNA, histone gene cluster, snoRNA hosts, mitochondrial-encoded genes, abundant housekeeping loci) appear "bound" in ChIP-seq with untagged GFP, no antibody, or non-existent targets. ENCODE blacklist v2 catches repeat-driven artifacts but NOT these hyper-ChIPable transcribed regions.

Always interpret peaks at rRNA loci, tRNA clusters, replication-dependent histone genes (HIST1/2 clusters), mitochondrial DNA, and the top-1% input-signal regions with skepticism. For rigorous claims: (1) require motif enrichment at the peak (artifact has no motif); (2) require KO/KD signal loss; (3) build a cell-type-specific blacklist from the top 1% of input signal and intersect-out.

## Pipeline Reference: ENCODE TF vs Histone

**TF pipeline (uses SPP for peak ranking):**

```bash
# Per-replicate (loose) — IDR tightens downstream
macs2 callpeak -t rep1.tagAlign.gz -c input.tagAlign.gz \
    -f BED -g hs -n rep1 \
    --nomodel --shift 0 --extsize {fraglen_from_xcor} \
    --keep-dup all -B --SPMR -p 1e-2

# Repeat for rep2, pooled, and pseudoreplicates (split each rep into halves)
# Score peaks by signalValue, sort, run IDR (see Replicate Handling below)
```

**Histone pipeline (uses MACS2 broad / narrow + naive overlap):**

```bash
# Broad marks: H3K27me3, H3K9me3, H3K36me3
macs2 callpeak -t rep1.tagAlign.gz -c input.tagAlign.gz \
    -f BED -g hs -n rep1 \
    --broad --broad-cutoff 0.1 \
    --nomodel --shift 0 --extsize {fraglen} \
    --keep-dup all -B --SPMR -p 1e-2

# Naive overlap: a peak passes if it appears in ≥2 of N replicates
# with ≥40% reciprocal overlap (ENCODE default, often misquoted as 50%)
bedtools intersect -a rep1.broadPeak -b rep2.broadPeak -f 0.40 -r -u > naive_overlap.bed
```

`--keep-dup all` is intentional in the ENCODE pattern: duplicates were already filtered upstream by MarkDuplicates + `samtools view -F 1804 -q 30`. `-p 1e-2` is permissive because IDR (TF) or overlap (histone) tightens downstream.

## Replicate Handling: IDR vs Naive Overlap

ENCODE rules (Landt 2012 *Genome Res*):

**TFs use IDR.** Run on signal-ranked peaks (sort by `-k8,8nr` p-value; `-k7,7nr` signal works for SPP but breaks for MACS pile-up if libraries differ).

```bash
sort -k8,8nr rep1.narrowPeak > rep1.sorted
sort -k8,8nr rep2.narrowPeak > rep2.sorted

idr --samples rep1.sorted rep2.sorted \
    --input-file-type narrowPeak --rank p.value \
    --idr-threshold 0.05 --output-file true_reps.idr --plot
```

**ENCODE Nself/Nt consistency rule** (often misremembered):
- Nt = IDR-passing peaks across true biological replicates (threshold 0.05)
- Nself (per rep) = IDR-passing peaks across pseudoreplicates of one library (threshold 0.10)
- Library passes if `max(N1self, N2self) / min(N1self, N2self) ≤ 2` AND `max(Nt, max(Nself)) / min(Nt, min(Nself)) ≤ 2`
- Both ratios > 2: library rejected

**Histones use naive overlap.** IDR's high-vs-low-rank assumption breaks for histone dynamic range. Naive overlap: pool peaks, require each to appear in ≥2 replicates with ≥40% reciprocal overlap.

## ENCODE 3 vs ENCODE 4 Differences

| Feature | ENCODE 3 | ENCODE 4 |
|---------|----------|----------|
| TF peak ranker | SPP | SPP (unchanged) |
| Histone caller | MACS2 | MACS2 (MACS3 not yet adopted) |
| Aligner | bwa-mem | bwa-mem (chromap evaluated; not yet swapped) |
| Blacklist | v1 (ENCODE DAC, unpublished resource) | v2 (Amemiya 2019) |
| TF significance | `-p 1e-2` + IDR @ 0.05 | Same |
| Histone significance | `-p 1e-2` + naive overlap | Same |
| Effective genome size | `hs`/`mm` shorthand | deepTools read-length-tabulated |
| Pseudoreplicate IDR threshold | 0.10 self-consistency | 0.10 self-consistency |

ENCODE 4 outputs are NOT numerically comparable to ENCODE 3 on the same BAM (blacklist change + genome size update shift peak counts ~3-10%).

## Per-Tool Failure Modes

### MACS2/3 -- Silent fragment-size model failure

**Trigger:** Sparse signal, low replicate depth, or saturated samples; `_model.r` plot never inspected.

**Mechanism:** Model needs ≥100 paired plus/minus enriched regions in `--mfold` range. Below threshold, MACS picks an arbitrary fragment size (often 50 or 1000 bp), producing miscentered or oversized peaks. Stderr shows a warning that gets ignored.

**Symptom:** Peak summits shifted relative to known motif positions by hundreds of bp; visual inspection in IGV shows peaks displaced from pile-up centers.

**Fix:** Inspect `<sample>_model.r` — if peaks look reasonable, accept; if degenerate, widen with `--mfold 3 50` or switch to `--nomodel --extsize <data-derived>`. For consistency across samples in a study, always use `--nomodel --extsize {fraglen}` with cross-correlation-derived fraglen (ENCODE pattern).

### MACS2/3 -- Confounded narrow vs broad on intermediate marks

**Trigger:** Marks of intermediate breadth (H3K4me1, H3K9ac) called with default narrow mode.

**Mechanism:** Default narrow mode fragments wide enrichment into multiple sub-peaks; `--broad` over-stitches.

**Symptom:** Peak count 3-5× higher than published for same cell type; mean peak width < 200 bp at known enhancer regions.

**Fix:** For H3K4me1, try `--broad --broad-cutoff 0.1` and compare; for H3K9ac, narrow mode typically OK. Always cross-reference published peak counts for the cell type and antibody lot.

### MACS2/3 -- `--call-summits` double-counts

**Trigger:** Narrow mode + `--call-summits` flag.

**Mechanism:** MACS adds sub-peak summits at multi-mode pile-ups; broad-shouldered peaks get split into 2-3 entries.

**Symptom:** Peak count inflated; same genomic region appears as 2-3 adjacent peaks in narrowPeak output.

**Fix:** Drop `--call-summits` unless deliberately analyzing multi-mode binding (rare); merge `bedtools merge -d 200` if needed post-hoc.

### HOMER -- Wrong style for histones

**Trigger:** `-style factor` used for histone marks.

**Mechanism:** Factor mode uses fixed-width peaks with local enrichment filter `-L 4` that eliminates broad signal.

**Symptom:** Far fewer peaks than expected for H3K4me3/H3K27ac/H3K27me3; missed enrichment at known regions.

**Fix:** Use `-style histone` for ALL histone marks (Omnipeak benchmark, Shpynov & Artyomov 2026); reserve `-style factor` for TFs only.

### SPP / phantompeakqualtools -- R version incompatibility

**Trigger:** Running phantompeakqualtools wrapper script with R ≥ 4.0.

**Mechanism:** spp R package has unmaintained dependencies; some functions silently fail or return NaN for NSC/RSC.

**Fix:** Use conda env pinned to R 3.6 + spp 1.16; or use kundajelab/phantompeakqualtools fork (current); or substitute deepTools plotFingerprint for QC and MACS-derived fragment length.

### chromap aligner -- Pre-applied shift double-counts

**Trigger:** Using chromap (fast aligner) output as MACS input with `--shift -75 --extsize 150`.

**Mechanism:** chromap pre-applies a Tn5/cut-site shift before fragment output (designed for ATAC); ChIP cut-site reasoning doesn't apply but the shift still happens silently.

**Symptom:** Peaks shifted ~5-10 bp from bwa-mem output at the same locus.

**Fix:** When using chromap, drop downstream shift OR use chromap's `--no-correction`. For ChIP, bwa-mem or bowtie2 are safer defaults until ENCODE switches.

## Reconciliation: When Callers Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| MACS finds peak; HOMER misses | HOMER local-enrichment filter (`-L 4`) removed it at low-signal regions; or `-style factor` clipped a histone peak | Re-run HOMER with `-style histone -L 0` for histones; if persists, trust MACS |
| HOMER finds peak; MACS misses | Clonal filter `-C 2` retained PCR artifact peaks; or HOMER's auto-width captured something MACS narrow mode segmented | Check if MACS broad mode rescues; check IGV for visual confirmation |
| SPP and MACS narrow peaks differ by 10-50 bp summit | Different fragment-size estimates (SPP uses cross-corr; MACS models from data) | Use same fragment size for both: ENCODE pattern `--nomodel --extsize {xcor_fraglen}` |
| MACS narrow + MACS broad on same data: 10× peak count difference | Expected — broad mode stitches subpeaks within 1 kb gap | Use narrow for differential analysis (consistent units); broad for domain annotation |
| Per-rep MACS calls peak; pooled MACS does not | One replicate dominates; pooling smooths local lambda | Trust pooled + IDR over per-replicate counts |
| Replicate count differs >2× | One replicate failed | Check FRiP, NSC, library complexity per replicate; do NOT average — drop the failing replicate or repeat |

**Operational rule for publication-grade:** TFs require IDR ≤ 0.05 on true reps AND Nt/Nself ratios ≤ 2. Histones require naive overlap ≥2 reps with ≥40% reciprocal overlap. Both require FRiP, NSC, RSC, and library complexity thresholds met. See chipseq-qc.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| 0 peaks called | Wrong genome size on subset data; wrong `-f` for input format; swapped treatment/control | Provide numeric `-g`; match `-f` to file type (BAM/BAMPE/BED); verify `-t` is enriched sample |
| Peak count >> 500k | Did not deduplicate; chrM not removed; `-q` too loose; hyper-ChIPable artifacts dominate | Filter `samtools view -F 1804 -q 30`; remove chrM; tighten to `-q 0.01`; blacklist top-1% input regions |
| Peaks shifted from motif by ~75 bp | `--shift` not set for `-f BAM`; or fragment-size model wrong | Add `--shift 0 --extsize {fraglen}`; or check `_model.r` |
| `--shift/--extsize ignored` warning | Used `-f BAMPE` with these flags | Switch to `-f BAM` for ENCODE pattern, or accept that BAMPE uses true fragment spans |
| IDR returns 0 reproducible peaks | Sorted by wrong column; ranks effectively random | `sort -k8,8nr` (p-value descending) on each peakset |
| Naive overlap returns few peaks | Set `-f 0.5 -r` (50% reciprocal) — too strict | Use `-f 0.40 -r` (ENCODE default) |
| FRiP < 1% | Bad ChIP (antibody, fragmentation, depth); peaks called on noise | Re-validate antibody with KO/KD; check fragment-size distribution; do not proceed |

## References

- Park PJ 2009 Nat Rev Genet 10:669 (foundational review)
- Landt SG et al 2012 Genome Res 22:1813 (ENCODE/modENCODE guidelines, IDR Nself rule)
- Zhang Y et al 2008 Genome Biol 9:R137 (MACS)
- Kharchenko PV et al 2008 Nat Biotechnol 26:1351 (SPP)
- Heinz S et al 2010 Mol Cell 38:576 (HOMER)
- Li Q et al 2011 Ann Appl Stat 5:1752 (IDR framework)
- Teytelman L et al 2013 PNAS 110:18602 (hyper-ChIPable regions)
- Park D et al 2013 PLoS One 8:e83506 (independent hyper-ChIPable confirmation)
- Amemiya HM et al 2019 Sci Rep 9:9354 (ENCODE blacklist v2)
- ENCODE ChIP-seq pipeline v2.1.6 (github.com/ENCODE-DCC/chip-seq-pipeline)
- Shpynov O & Artyomov MN 2026 Nucleic Acids Res 54:gkaf1454 (Omnipeak; benchmarks HOMER -style histone vs factor for histone marks)

## Related Skills

- chip-seq/chipseq-qc - Fragment-size diagnostic, FRiP, NSC/RSC, antibody validation
- chip-seq/cut-and-run-tag - SEACR + MACS for CUT&RUN/CUT&Tag (different QC, lower depth)
- chip-seq/spike-in-normalization - When global signal shifts expected (HDACi, BETi, EZH2i)
- chip-seq/differential-binding - DiffBind/csaw downstream of peak calling
- chip-seq/peak-annotation - Annotate peaks to genes and cCREs
- chip-seq/motif-analysis - Discover and scan binding motifs in peaks
- chip-seq/super-enhancers - Stitch H3K27ac peaks into super-enhancer calls
- atac-seq/atac-peak-calling - ATAC-specific shift/extend; no input control
- alignment-files/sam-bam-basics - Pre-call BAM filtering and deduplication
- genome-intervals/interval-arithmetic - Peak intersection and overlap
<!-- END FILE: chip-seq/peak-calling/SKILL.md -->

## 子目录：chip-seq/spike-in-normalization

<!-- BEGIN FILE: chip-seq/spike-in-normalization/SKILL.md -->
---
name: bio-chipseq-spike-in-normalization
description: Normalizes ChIP-seq data using exogenous spike-in (ChIP-Rx with Drosophila chromatin per Orlando 2014 / Egan 2016; E. coli carryover for CUT&RUN/CUT&Tag). Distinguishes RRPM from Rx-Input scaling, integrates with DiffBind / DESeq2 / edgeR / csaw via sizeFactors and DiffBind library-size vectors, applies the Patel et al 2024 *Nat Biotechnol* failure-mode framework, and validates that normalization is applied at the read level (not peak counts). Use when global signal shifts are expected (HDACi, BETi, EZH2i, dosage, target knockdown), when ChIPseqSpikeInFree detects post-hoc shifts, or when validating internal-control regions before publication.
tool_type: mixed
primary_tool: DiffBind
---

## Version Compatibility

Reference examples tested with: DiffBind 3.20+, DESeq2 1.42+, edgeR 4.0+, csaw 1.36+, ChIPseqSpikeInFree 1.6+, SpikChIP 1.0+, SpikeFlow (NAR Genom Bioinform 2024), samtools 1.19+, bowtie2 2.5+.

# ChIP-seq Spike-In Normalization

**"Account for global signal changes that defeat standard normalization"** -> Add exogenous reference chromatin (Drosophila for human/mouse ChIP-Rx; E. coli carryover for CUT&RUN/CUT&Tag) at fixed concentration BEFORE IP, derive scaling factors from spike-in read counts, and apply at the read or size-factor level (never to peak counts) to enable quantitative cross-condition comparison.

- CLI: align reads to combined target + spike genome; count spike reads via `samtools view -c`
- R (DiffBind integration): `dba.normalize(obj, spikein = TRUE)`
- R (DESeq2 / edgeR): `sizeFactors(dds) <- 1 / scale_factors` (note inverse)
- CLI (deepTools tracks): `bamCoverage --scaleFactor <derived>` (use alone; `--normalizeUsing` compounds with it)
- Wrapper: SpikeFlow (Snakemake; 2024) automates end-to-end
- Post-hoc detection: ChIPseqSpikeInFree (when no spike-in was added)

The fundamental rule: spike-in scaling is applied at the READ level (via size factors or `--scaleFactor`), never multiplied into peak counts. This is a common implementation error in published spike-in ChIP.

## When Spike-In Is Required

| Experimental design | Spike-in needed? |
|---------------------|------------------|
| HDAC inhibitor -> global H3K27ac increase | Yes |
| BET inhibitor (JQ1, OTX015) -> global BRD4 / H3K27ac decrease | Yes |
| EZH2 inhibitor -> global H3K27me3 loss | Yes |
| DNMT inhibitor -> global 5mC loss; downstream histone mark shifts | Yes |
| Target factor knockdown / degron | Yes (or matched-input subtraction) |
| Cell-cycle synchronization / arrest | Yes |
| Dosage titration | Yes |
| Standard TF perturbation, local rebinding expected | No (reads-in-peaks RLE works) |
| Histone mark cross-cell-type comparison | Recommended |
| CUT&RUN/CUT&Tag standard | E. coli carryover (automatic); deliberate Drosophila for high-stakes |
| Replicate-only experiment, no condition comparison | No |

**Why this is necessary:** Standard normalization (RLE on reads-in-peaks, TMM on bins) assumes most regions don't change. When the perturbation IS the change-everything-globally biology, these methods force the median log2FC to zero, hiding the real effect.

## Spike-In Protocol Taxonomy

| Protocol | Spike organism | Added when | Notes |
|----------|----------------|------------|-------|
| **ChIP-Rx** (Orlando 2014) | Drosophila S2 nuclei | After lysis, before IP | fixed Drosophila chromatin mass, ~27:1 human:Drosophila genome-copy ratio (Egan 2016) |
| **ChIP-Rx variant** (Bonhoure 2014) | Drosophila chromatin | After fragmentation, before IP | Different normalization layer |
| **CUT&RUN/Tag E. coli** | E. coli (carryover) | Automatic from bacterial pA-MNase/Tn5 | Free; variable across enzyme batches |
| **Heterologous spike-in** | Defined yeast / E. coli chromatin | Added at lysis | Less common; defined concentration |
| **xenoChIP** | Species swap (mouse cells + human chromatin spike) | Before IP | Niche; specific cancer xenograft contexts |

**The dominant standard for human/mouse ChIP is Drosophila (ChIP-Rx).** Drosophila is genetically distinct enough that mapping is unambiguous, and the genome size (~140 Mb) gives adequate read depth at small chromatin input.

## Scaling Factor Calculation

**RRPM (Orlando 2014):** reference-adjusted reads per million.

```
scale_factor_i = min(N_spike) / N_spike_i
```

Apply at the read level. The sample with the fewest spike reads gets scale_factor = 1 (the maximum); others get < 1 (scaled down because they recovered more spike chromatin).

**Rx-Input (Fursova 2019):** additionally scales by input spike-in to correct IP efficiency variation.

```
RxInput_i = (N_spike_chip_i / N_total_chip_i) / (N_spike_input_i / N_total_input_i)
```

This is more rigorous when input controls are available; required for some inhibitor experiments where IP efficiency itself changes.

## Workflow: Drosophila ChIP-Rx Spike-In

**Goal:** Compute per-sample scaling factors from Drosophila spike-in reads and apply at the read level (not peak counts) to enable quantitative cross-condition ChIP-seq comparison.

**Approach:** Align reads to combined target + Drosophila genome, count spike reads at high mapq after deduplication, derive RRPM scaling factors (min/each), then apply via DESeq2 sizeFactors, DiffBind spike-in flag, or bamCoverage scaleFactor. Validate against internal-control regions (blacklist).

### Step 1: Alignment to combined genome

```bash
# Build combined index (target + Drosophila)
cat hg38.fa dm6.fa > hg38_dm6.fa
bowtie2-build hg38_dm6.fa hg38_dm6

# Align reads
bowtie2 -x hg38_dm6 -1 R1.fq -2 R2.fq -S aln.sam --very-sensitive --no-mixed
samtools view -bS aln.sam | samtools sort -o aln.bam
samtools index aln.bam
```

### Step 2: Filter, deduplicate, count spike reads

```bash
# Apply ENCODE filter (-F 1804 -q 30) BEFORE counting spike reads
samtools view -F 1804 -q 30 -b aln.bam > aln.filt.bam
samtools index aln.filt.bam

# Count Drosophila reads (NOT total reads)
DROSO_READS=$(samtools view -c aln.filt.bam chr2L chr2R chr3L chr3R chr4 chrX chrY)
echo "$SAMPLE: Drosophila reads = $DROSO_READS"

# Separate into target-only BAM for peak calling
samtools view -b aln.filt.bam chr1 chr2 chr3 chr4 chr5 chr6 chr7 chr8 chr9 chr10 \
    chr11 chr12 chr13 chr14 chr15 chr16 chr17 chr18 chr19 chr20 chr21 chr22 chrX chrY \
    > aln.filt.hg38.bam
samtools index aln.filt.hg38.bam
```

### Step 3: Compute scaling factors

```bash
# Per-sample Drosophila counts (assume saved in droso_counts.tsv)
# sample_id, droso_reads
# ctrl_1, 145000
# ctrl_2, 132000
# treat_1, 98000
# treat_2, 85000

awk 'BEGIN{min=1e10} NR>1{if($2<min) min=$2} END{print "min:", min}' droso_counts.tsv
# Use min as numerator: scale_factor_i = min / droso_reads_i
```

### Step 4: Apply scaling — three layers

**Layer 1: bigWig tracks**

```bash
SCALE=$(echo "scale=6; $MIN_DROSO / $SAMPLE_DROSO" | bc)
bamCoverage -b sample.bam -o sample.scaled.bw \
    --scaleFactor $SCALE --binSize 10 --extendReads 200
# DO NOT also pass --normalizeUsing; deepTools multiplies the two factors together, reintroducing depth normalization
```

**Layer 2: DiffBind**

```r
library(DiffBind)
dba_obj <- dba(sampleSheet = 'samples.csv')   # spike-in BAM in sample sheet
dba_obj <- dba.count(dba_obj, summits = 250, bParallel = TRUE)

# Spike-in normalization (spikein = TRUE forces library = DBA_LIBSIZE_BACKGROUND internally)
dba_obj <- dba.normalize(dba_obj, spikein = TRUE,
                          normalize = DBA_NORM_LIB)

# Verify what was applied
dba.normalize(dba_obj, bRetrieve = TRUE)
```

**Layer 3: DESeq2 / edgeR direct**

```r
library(DESeq2)
# Read spike-in counts into a vector aligned with sample order
spike_reads <- c(ctrl_1 = 145000, ctrl_2 = 132000, treat_1 = 98000, treat_2 = 85000)
scale_factors <- min(spike_reads) / spike_reads

dds <- DESeqDataSetFromMatrix(counts, coldata, design = ~ condition)
# DESeq2 expects sizeFactors in INVERSE convention (sample with smallest factor gets largest sizeFactor)
sizeFactors(dds) <- 1 / scale_factors
dds <- DESeq(dds, fitType = 'parametric')
```

## Workflow: E. coli Spike-In (CUT&RUN/CUT&Tag Automatic)

E. coli DNA from bacterial pA-MNase/pA-Tn5 production is automatic spike-in carryover.

```bash
# Combined index
cat hg38.fa ecoli_k12.fa > hg38_ecoli.fa
bowtie2-build hg38_ecoli.fa hg38_ecoli

# Align as in ChIP-Rx; count E. coli reads
ECOLI_READS=$(samtools view -c aln.filt.bam ecoli_chr1)
TOTAL_READS=$(samtools view -c aln.filt.bam)
echo "E. coli fraction: $(echo "scale=4; $ECOLI_READS / $TOTAL_READS" | bc)"
# Target: 0.005-0.02 (0.5-2%); IgG: 0.02-0.05 (2-5%)

# Scale factor same as ChIP-Rx: min(ecoli) / per_sample_ecoli
# Apply at read or sizeFactors level
```

**E. coli carryover is variable** between enzyme production batches. For publication-grade cross-condition claims, supplement with deliberate Drosophila spike-in OR use a single enzyme lot across all experiments.

## ChIPseqSpikeInFree: Post-Hoc Detection

When no spike-in was added, ChIPseqSpikeInFree (Jin 2020) attempts post-hoc detection of global shifts by analyzing signal-distribution shape changes.

```r
library(ChIPseqSpikeInFree)

samples <- data.frame(
    ID = c('ctrl_1', 'ctrl_2', 'treat_1', 'treat_2'),
    BAM = c('ctrl_1.bam', 'ctrl_2.bam', 'treat_1.bam', 'treat_2.bam'),
    ANTIBODY = rep('H3K27me3', 4),
    GROUP = c('Control', 'Control', 'Treatment', 'Treatment')
)

res <- ChIPseqSpikeInFree(bamFiles = samples$BAM, chromFile = 'hg38.chrom.sizes',
                          metaFile = 'metadata.txt', prefix = 'spikein_free_out')
# Output: per-sample scaling factor + global-shift detection
```

**Limitations:** Heuristic; not a substitute for true spike-in. Use as:
1. Sanity check when spike-in was forgotten
2. Initial diagnosis before deciding whether spike-in is needed in next experiment
3. NOT for publication-grade claims

## Internal-Control Sanity Check (Mandatory)

After applying spike-in scaling, internal-control regions should show NO signal change:

| Region type | Source | Expected behavior post-spike-in |
|-------------|--------|----------------------------------|
| ENCODE blacklist v2 | Amemiya 2019 | No change (artifact regions) |
| Constitutive housekeeping promoters | Eisenberg 2013 list (HK genes); U6 snRNA promoter | Minor change only |
| Custom hyper-ChIPable regions | Top-1% input signal | Stable signal at artifact regions |
| Untouched chromosome (e.g., chrY in cell types without expression) | Genome | No signal change |

```bash
# Compute mean signal at blacklist regions per condition; should be stable
bedtools multicov -bams ctrl_1.bam ctrl_2.bam treat_1.bam treat_2.bam \
    -bed hg38-blacklist.v2.bed > blacklist_signal.tsv
# Apply scaling factors to per-sample counts; verify no shift across conditions
```

If internal controls shift after scaling, the normalization is broken. Common causes:
1. Scaling applied to peak counts instead of read counts
2. Spike-in reads not deduplicated before scaling
3. Spike-in genome not mapq-filtered (low-quality alignments inflated counts)
4. Spike-in saturated (>1M reads); titration not linear

## Per-Tool Failure Modes

### Scaling factor applied to peak counts instead of read counts

**Trigger:** Multiplying peak-by-sample count matrix entries by spike-in factor.

**Mechanism:** Peak counts already integrate over read counts; multiplying them double-corrects.

**Symptom:** Effect sizes 2-10× larger than expected biology; internal control regions also "shift" artifactually.

**Fix:** Apply via `sizeFactors(dds)` (DESeq2), `normFactors` (edgeR), or DiffBind's `dba.normalize(..., library=<numeric vector>, normalize=DBA_NORM_LIB)` to supply spike-in-derived library sizes, OR `--scaleFactor` (bamCoverage for tracks). Never multiply peak-level counts.

### Spike-in reads not deduplicated before scaling

**Trigger:** Counting all aligned reads to spike genome including duplicates.

**Mechanism:** PCR duplicates of spike-in reads vary independently of input chromatin amount.

**Symptom:** Scaling factors poorly correlated with library prep batch; high inter-replicate variability.

**Fix:** Deduplicate with MarkDuplicates; apply ENCODE filter `-F 1804 -q 30` before counting spike reads.

### Spike-in mapq filter too loose

**Trigger:** Counting all reads aligning to spike genome.

**Mechanism:** Low-mapq reads at low-complexity regions (E. coli rRNA, Drosophila satellite) are often misaligned from host genome.

**Fix:** Apply `-q 30` (high mapq) before counting spike reads.

### Inverse convention errors with DESeq2 / edgeR

**Trigger:** Passing `scale_factors` directly to `sizeFactors(dds)` without inversion.

**Mechanism:** DESeq2 / edgeR DIVIDE counts by `sizeFactors` (normalized = counts / sizeFactor); a read-level spike-in scale factor multiplies reads, so it must be applied as its inverse. Convention difference.

**Symptom:** Effect sizes inverted (treatment shifted in wrong direction).

**Fix:** `sizeFactors(dds) <- 1 / scale_factors` (inverse). Verify with internal-control sanity check.

### `--normalizeUsing` and `--scaleFactor` conflict in bamCoverage

**Trigger:** Passing both for spike-in scaled bigWig.

**Mechanism:** deepTools multiplies the `--scaleFactor` value by the factor computed from `--normalizeUsing`; adding `--normalizeUsing` therefore reintroduces library-depth normalization on top of the spike-in factor. The default `--normalizeUsing None` leaves `--scaleFactor` acting alone.

**Fix:** Use ONE: `--scaleFactor` alone for spike-in; `--normalizeUsing` alone otherwise. Verify via `bamCoverage --help`.

### E. coli carryover inconsistent across enzyme batches

**Trigger:** Comparing CUT&Tag samples processed with different pA-Tn5 lots.

**Mechanism:** E. coli carryover varies between bacterial production batches; cross-batch comparison adds artificial variability.

**Fix:** Use single enzyme lot for cross-condition comparison; OR supplement E. coli with deliberate Drosophila spike-in.

### ChIPseqSpikeInFree applied as primary normalization

**Trigger:** No spike-in was added; ChIPseqSpikeInFree used for publication-grade scaling.

**Mechanism:** ChIPseqSpikeInFree infers global shift from signal-distribution shape; this is a heuristic, not a measurement.

**Fix:** Use only as diagnostic. For publication, re-do experiment with deliberate spike-in.

### Spike-in titration not verified linear

**Trigger:** Spike-in concentration too high (>5% of total reads) OR too low (<0.1%).

**Mechanism:** Outside linear range, scaling factor doesn't reflect actual ratio of input chromatin.

**Symptom:** Replicate-to-replicate scaling factor variability >2×.

**Fix:** Verify titration linearity by varying spike-in concentration on a single sample; only use spike-in counts in linear range (typically 0.5-5% of total reads).

## Reconciliation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Spike-in scaled vs CPM give opposite signs | Global shift; CPM forced to median; spike-in revealed it | Spike-in is correct; CPM is fooled |
| Scaling factor varies wildly between reps | Spike-in saturated / not in linear range | Verify titration; subsample if needed |
| Internal-control signal shifts after scaling | Scaling applied wrong layer; reads not dedup'd; mapq too loose | Apply pre-test diagnostic; recompute |
| ChIPseqSpikeInFree predicts shift but spike-in says no | Both interpretations possible; trust spike-in when available | Spike-in measurement > distribution heuristic |
| DiffBind spike-in vs manual sizeFactors differ | DiffBind applies inverse convention internally | Verify via `dba.normalize(obj, bRetrieve=TRUE)` |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Spike-in BAM column missing in DiffBind sample sheet | `bamSpikeIn` (DiffBind 3.x) vs older `spikein` field | Use `spikein = TRUE` in `dba.normalize()` with appropriate column |
| Drosophila reads on chromosome X include host chrX | Combined genome chromosome naming collision | Prefix Drosophila chroms with `dm_` before combining |
| Scaling factors all close to 1 | Spike-in not added at fixed amount | Verify Egan 2016 protocol; titrate the spike-in chromatin mass |
| Cross-condition results sign-flipped after scaling | Inverse convention bug | `sizeFactors(dds) <- 1 / scale_factors` |
| Blacklist signal shifts post-scaling | Normalization broken | Investigate spike-in scaling failure modes (peak-count vs read-level, dedup, mapq) |

## References

- Orlando DA et al 2014 Cell Rep 9:1163 (ChIP-Rx framework)
- Egan B et al 2016 PLoS One 11:e0166438 (ChIP-Rx protocol; fixed Drosophila chromatin mass)
- Bonhoure N et al 2014 Genome Res 24:1157 (alternative Drosophila spike-in)
- Fursova NA et al 2019 Mol Cell 74:1020 (Rx-Input scaling)
- Jin H et al 2020 Bioinformatics 36:1270 (ChIPseqSpikeInFree)
- Blanco E et al 2021 NAR Genom Bioinform 3:lqab064 (SpikChIP)
- 2024 NAR Genom Bioinform 6:lqae118 (SpikeFlow)
- Patel L, Cao Y, Mendenhall EM, Benner C, Goren A 2024 Nat Biotechnol 42:1343 (spike-in normalization review; common failure modes; PMC12266361)
- Stark R & Brown G 2011 Bioconductor (DiffBind with spikein parameter)

## Related Skills

- chip-seq/peak-calling - Upstream peak calling
- chip-seq/chipseq-qc - Spike-in fraction QC
- chip-seq/differential-binding - Apply spike-in via DiffBind / DESeq2 / csaw
- chip-seq/cut-and-run-tag - E. coli spike-in carryover specifics
- chip-seq/super-enhancers - SE calling requires spike-in for cross-condition
- chip-seq/chipseq-visualization - Spike-in-scaled bigWig generation
- alignment-files/sam-bam-basics - Multi-genome alignment and chromosome filtering
- differential-expression/deseq2-basics - DESeq2 sizeFactors conventions
<!-- END FILE: chip-seq/spike-in-normalization/SKILL.md -->

## 子目录：chip-seq/super-enhancers

<!-- BEGIN FILE: chip-seq/super-enhancers/SKILL.md -->
---
name: bio-chipseq-super-enhancers
description: Identifies super-enhancers from H3K27ac, MED1, or BRD4 ChIP-seq using ROSE, ROSE2, LILY, HOMER -style super, and ENCODE dELS cross-referencing. Handles peak stitching parameters, ranking choices, hockey-stick inflection, marker choice (H3K27ac vs MED1/BRD4), and cross-condition comparison with spike-in normalization. Constructs core regulatory circuitry (Saint-Andre 2016) from SE-encoded TFs. Use when identifying cell-identity / cancer-associated regulatory domains, comparing super-enhancers between conditions, identifying master transcription factor networks, or predicting BET-inhibitor responsiveness.
tool_type: mixed
primary_tool: ROSE
---

## Version Compatibility

Reference examples tested with: ROSE (stjude/ROSE, 2018+), ROSE2 (linlabbcm/rose2, 2021+), LILY (BoevaLab/LILY, 2020+), HOMER 4.11+, samtools 1.19+, bedtools 2.31+, GenomicRanges 1.54+.

The original Young-lab ROSE is Python 2; ROSE2 (linlabbcm/rose2) and the stjude/ROSE fork are the Python-3 implementations with the same algorithm. For hg38 data use stjude/ROSE (`python ROSE_main.py`, whose genomeDict includes HG38); rose2's released genomeDict covers only HG18/HG19/MM8/MM9/MM10/RN4/RN6, so `rose2 -g HG38` fails. LILY (Boeva 2017) is a refactored implementation with input-control background subtraction for low-quality H3K27ac data.

# Super-Enhancer Calling

**"Identify super-enhancers driving cell identity / cancer biology"** -> Stitch nearby active enhancer peaks (H3K27ac, MED1, or BRD4) within a stitching window, exclude proximal-promoter signal, rank by total signal, find the hockey-stick inflection point where signal sharply increases, and classify all stitched regions above the inflection as super-enhancers.

- CLI (stjude/ROSE, Python 3): `python ROSE_main.py -g HG38 -i peaks.gff -r h3k27ac.bam -c input.bam -s 12500 -t 2500 -o rose_out/`
- CLI (HOMER): `findPeaks tag_dir/ -style super -i input_tag_dir/`
- CLI (LILY): variant with input-control background subtraction
- R (custom hockey-stick): rank enhancers by signal, find tangent-line inflection

The SE concept (Whyte 2013) is a thresholding heuristic on a continuous signal distribution (Pott & Lieb 2015 *Nat Genet*), not a categorical biological category. Genetic dissection of super-enhancers (Hay 2016; Moorthy 2017) shows constituent elements contribute unequally and many are individually dispensable/redundant; the "SE" label is a useful operational definition for BET-inhibitor responsiveness and cell-identity gene regulation, not an absolute biological property.

## Marker Choice: H3K27ac vs MED1 vs BRD4

| Marker | Captures | When to prefer |
|--------|----------|----------------|
| **H3K27ac** | Active regulatory elements broadly | Most widely available; standard for SE definition since Whyte 2013 |
| **MED1** | Mediator complex accumulation (the defining biology) | Direct readout of SE; less common antibody; lower signal-to-noise |
| **BRD4** | BET cofactor accumulation | Most predictive of BET-inhibitor responsiveness; clinical relevance |
| **H3K27ac + MED1 intersection** | High-confidence SE | Gold standard if both available |
| **dELS from ENCODE cCREs** | Cell-type-agnostic distal enhancer registry | Cross-reference; not SE-specific by itself |

**Operational rule:** H3K27ac for discovery; MED1 or BRD4 ChIP for functional / therapeutic claims. SE called on H3K27ac alone may not respond to BET inhibitors; SE called on BRD4 will.

## Algorithmic Taxonomy

| Tool | Method | Strength | Fails when |
|------|--------|----------|------------|
| **ROSE** (Whyte 2013) | Stitch within 12.5 kb, exclude ±2.5 kb of TSS, rank by signal, hockey-stick inflection | Original; widely cited; canonical reference | Original Young-lab code is Python 2; run the stjude/ROSE Py3 fork instead |
| **ROSE2** (linlabbcm/rose2) | Same algorithm, Python 3 port | Maintained; pip-installable `rose2` console command | Released genomeDict has no HG38 (HG18/HG19/MM8/MM9/MM10/RN4/RN6 only) -> use stjude/ROSE for hg38 |
| **LILY** (Boeva 2017) | ROSE-like with input-control background subtraction | Works on lower-quality H3K27ac data; subtracts input | Adds complexity; less validated; specific to neuroblastoma/glioma in original paper |
| **HOMER `-style super`** | Native ROSE-like in HOMER framework; stitching without TSS exclusion | Integrated with HOMER workflow | Different stitching defaults; not directly comparable to ROSE counts |
| **Custom hockey-stick (R)** | Generic rank-by-signal + tangent inflection | Flexible; works on any signal definition | Reinvents algorithm; verify against ROSE on known dataset |

**Most papers use ROSE/ROSE2 with default stitching (12.5 kb) and TSS exclusion (2.5 kb).** This is the de facto standard for cross-paper comparison. HOMER's `-style super` produces different counts and is not directly comparable.

## Decision Tree: SE Calling Workflow

| Scenario | Recommended pipeline |
|----------|----------------------|
| Standard SE discovery, H3K27ac available | ROSE2 with default `-s 12500 -t 2500`; input control for subtraction |
| Predict BET-inhibitor response | BRD4 ChIP -> ROSE2 (or H3K27ac SE intersected with BRD4 peaks) |
| Compare SE between conditions (drug treatment) | ROSE2 per condition + spike-in normalization (HDACi/BETi/EZH2i need ChIP-Rx) |
| Build core regulatory circuitry | ROSE2 + Saint-Andre 2016 algorithm: identify TFs encoded by SE that bind own SE + cross-bind other SE-encoded TFs |
| Low-quality H3K27ac (low FRiP) | LILY with input subtraction |
| Compare with ENCODE dELS atlas | ROSE2 + intersect with ENCODE cCRE dELS BED |
| Differential SE between conditions | ROSE2 per condition + signal-quantitative differential (DiffBind on SE regions) |

## ROSE / ROSE2 Workflow

**Goal:** Identify super-enhancers by stitching nearby active enhancer peaks within a stitching distance and ranking by total signal.

**Approach:** Convert peaks to GFF, exclude promoter-proximal peaks via `-t` (TSS exclusion window), stitch enhancers within `-s` (default 12.5 kb), rank by total H3K27ac (or MED1/BRD4) signal, find the hockey-stick inflection point, classify regions above as super-enhancers.

```bash
# Install ROSE2 (Python 3 port; unmaintained ROSE Py2 not recommended)
git clone https://github.com/linlabbcm/rose2.git
pip install ./rose2

# Convert peaks BED to GFF (ROSE requires GFF input)
awk 'BEGIN{OFS="\t"} {print $1,"peaks","enhancer",$2,$3,".",$6,".","ID="NR}' \
    peaks.narrowPeak > peaks.gff

# Filter promoter peaks before SE calling (within 2.5 kb of TSS)
# ROSE handles this via -t flag; preferable to pre-filter for clarity
bedtools intersect -a peaks.narrowPeak -b promoters_2kb.bed -v > enhancer_peaks.bed

# Run stjude/ROSE with input control (Python-3 fork; genomeDict includes HG38)
python ROSE_main.py -g HG38 -i peaks.gff \
    -r h3k27ac.bam -c input.bam \
    -o rose_output/ \
    -s 12500 \
    -t 2500
```

ROSE outputs:
- `*_AllEnhancers.table.txt` — all stitched enhancer regions ranked by signal
- `*_SuperEnhancers.table.txt` — SE only (above hockey-stick inflection)
- `*_Enhancers_withSuper.bed` — BED with SE / TE classification
- `*_Plot_points.png` — hockey-stick plot

## Cross-Condition SE Comparison

This is the analysis most often done wrong. SE calling thresholds depend on absolute signal, so any global shift (HDACi, BETi, EZH2i) confounds direct SE-count comparison.

**Wrong approach:** Call ROSE2 on condition A and condition B separately, intersect SE BEDs, report "gained/lost SE."

**Right approach:**
1. Spike-in normalize signal between conditions (see chip-seq/spike-in-normalization)
2. Build a union SE set from both conditions
3. Quantify signal at union SE regions per condition (DiffBind on the union)
4. Apply differential testing with appropriate normalization (background-bin TMM or spike-in)

```r
library(DiffBind)
# Union of SE BED files from condition A and B
union_se <- rtracklayer::import('union_SE.bed')
# Run DiffBind quantification on this region set with spike-in normalization
```

For BET-inhibitor experiments: the biology IS that all SE decrease globally; spike-in is mandatory.

## Core Regulatory Circuitry (Saint-André 2016)

The CRC algorithm identifies master TF networks from SE annotations:

1. List all TFs encoded by SE-associated genes
2. For each such TF, check if its motif appears in its own SE (auto-regulation)
3. Build a graph where TFs encoded by SE-A bind to motifs in SE-B
4. Identify highly-interconnected sub-networks (CRC)

```bash
# Install CRC pipeline (console command is `crc`; -g is the genome BUILD, not a GTF)
pip install git+https://github.com/linlabcode/CRC.git

# Requires: SE enhancer table, subpeak BED, chromosome-FASTA dir
crc -e SE_table.txt -g HG38 -s subpeaks.bed -c chroms/ -o crc_out/ -n SAMPLE
```

CRC outputs the connected components of the regulatory network. Master TFs typically appear in the largest component with high out-degree.

## ENCODE dELS Cross-Reference

ENCODE distal Enhancer-Like Signatures (dELS) are the cell-type-agnostic regulatory atlas (see chip-seq/peak-annotation). Cross-referencing SE against dELS:

- Validates SE constituents are at canonical regulatory elements
- Identifies SE constituents NOT in the dELS registry (potentially cell-type-specific)
- Provides chromatin-state context (DNase + H3K27ac signatures)

```bash
wget https://downloads.wenglab.org/Registry-V4/GRCh38-cCREs.bed
awk -F'\t' '$NF == "dELS"' GRCh38-cCREs.bed > dels.bed

# Fraction of SE constituents overlapping dELS
bedtools intersect -a SuperEnhancers.bed -b dels.bed -u | wc -l
bedtools intersect -a SuperEnhancers.bed -b dels.bed -wa -wb > se_with_dels.tsv
```

## Per-Tool Failure Modes

### ROSE -- Python 2 dependency

**Trigger:** Running the original Young-lab `ROSE_main.py` (Python 2 code) on a modern system.

**Mechanism:** The original ROSE is Python 2 code; `print` statements without parens, `dict.iteritems()`, etc.

**Symptom:** SyntaxError on first import.

**Fix:** Use the stjude/ROSE fork (`python ROSE_main.py`, Python 3, genomeDict includes HG38) or ROSE2 (`rose2`, Python 3, but its released genomeDict has no HG38 -- HG18/HG19/MM8/MM9/MM10/RN4/RN6 only); identical algorithm and output format.

### ROSE / ROSE2 -- Stitching distance default not appropriate for all biology

**Trigger:** Using default `-s 12500` (12.5 kb) on small genomes or compact gene structures.

**Mechanism:** Default was set on human/mouse vertebrate genomes; Drosophila / yeast / plants have different regulatory architecture.

**Fix:** For non-vertebrate genomes, reduce stitching distance proportionally (e.g., -s 2500 for Drosophila, -s 500 for yeast).

### ROSE / ROSE2 -- TSS exclusion can remove promoter-associated enhancers

**Trigger:** Default `-t 2500` (exclude peaks within 2.5 kb of TSS) on promoter-proximal enhancers (e.g., pELS class).

**Mechanism:** TSS-proximal enhancers are filtered out; SE definition becomes distal-only.

**Symptom:** Lower SE counts than expected for cell types with promoter-enhancer architecture (e.g., human ES cells).

**Fix:** Reduce TSS exclusion to `-t 500` or `-t 0` if including promoter-proximal regulatory regions; document the decision.

### H3K27ac SE vs BRD4 SE -- BET-inhibitor mismatch

**Trigger:** Calling SE on H3K27ac and claiming BET-inhibitor responsiveness.

**Mechanism:** H3K27ac marks active enhancers broadly; not all H3K27ac-positive SE have BRD4 accumulation.

**Symptom:** Predicted BET-sensitive genes don't respond to BET inhibitors in cell-based assays.

**Fix:** For BET-inhibitor claims, use BRD4 ChIP for SE calling, or intersect H3K27ac SE with BRD4 peaks.

### Cross-condition SE counting -- Wrong normalization

**Trigger:** Comparing SE counts in HDACi-treated vs DMSO without spike-in normalization.

**Mechanism:** SE calling thresholds depend on absolute signal; HDACi globally increases H3K27ac, raising every region's signal and shifting the hockey-stick inflection.

**Symptom:** Reports "1000 SE in HDACi vs 500 in DMSO" when biology is just global H3K27ac increase.

**Fix:** Spike-in normalize BAMs (ChIP-Rx with Drosophila chromatin), call SE on scaled signal; OR quantify signal at a union peak set rather than calling SE per condition.

### LILY -- Input subtraction artifacts

**Trigger:** Running LILY without high-quality matched input control.

**Mechanism:** LILY subtracts background based on input signal; mismatched input introduces artifactual negative signal.

**Fix:** Use LILY only when input quality is good (same library prep, same depth, same fragmentation); otherwise use ROSE2 with standard input handling.

### Hockey-stick inflection -- Sensitive to peak count

**Trigger:** Calling SE on a small peak set (< 5000 enhancers).

**Mechanism:** Hockey-stick inflection depends on having a long "tail" of typical enhancers; few peaks distort the inflection.

**Symptom:** SE count is unreasonably high (50%+ of all peaks called SE) or unreasonably low (< 50 SE).

**Fix:** Require ≥ 5000 enhancer peaks input to ROSE2; if fewer, use absolute signal cutoff (e.g., top 5% by signal density) rather than hockey-stick.

## Reconciliation: When SE Calls Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| ROSE2 vs HOMER -style super differ | Different stitching distance / TSS handling | Use ROSE2 standard for cross-paper comparison; HOMER for HOMER-integrated workflows |
| H3K27ac SE ≠ MED1 SE at same locus | H3K27ac is broad; MED1 marks subset of active SE | MED1 SE is the more functional definition; H3K27ac includes inactive-but-acetylated regions |
| SE called in DMSO but not in BETi (or vice versa) | Global signal shift confounds threshold | Spike-in normalize; compare quantitatively at union SE set |
| SE shifts location between replicates | Marginal calls below inflection; hockey-stick inflection noisy | Use top N SE by rank for robustness; or require SE in ≥ 2/3 replicates |
| LILY and ROSE2 disagree on SE count | LILY's input subtraction differs | Trust ROSE2 unless input quality is poor (low FRiP) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `SyntaxError: invalid syntax` in ROSE | Python 2 codebase | Use ROSE2 (linlabbcm) Python 3 port |
| GFF format error | Wrong column ordering | Use awk template: `chr<TAB>peaks<TAB>enhancer<TAB>start<TAB>end<TAB>.<TAB>strand<TAB>.<TAB>ID=N` |
| ROSE2 reports 0 SE | Hockey-stick inflection failed; too few enhancers | Inspect `_Plot_points.png`; ≥ 5000 peaks input recommended |
| Genome flag error in ROSE2 | Genome not pre-configured | Genome flag must be one of HG18, HG19, HG38, MM8, MM9, MM10 |
| All SE at promoters | TSS exclusion too narrow OR data dominated by promoter signal | Verify `-t 2500`; check input is H3K27ac at enhancers not full chromatin |
| Cross-condition SE gain/loss not reproducible | No spike-in normalization | Spike-in (ChIP-Rx) or quantitative differential on union SE |

## References

- Whyte WA et al 2013 Cell 153:307 (super-enhancers, ROSE)
- Lovén J et al 2013 Cell 153:320 (SE characterization, BET sensitivity)
- Hnisz D et al 2013 Cell 155:934 (SE in cell identity)
- Pott S & Lieb JD 2015 Nat Genet 47:8 (SE as continuum critique)
- Lin CY et al 2016 Nature 530:57-62 (medulloblastoma super-enhancers)
- Saint-André V et al 2016 Genome Res 26:385 (core regulatory circuitry)
- Boeva V et al 2017 Nat Genet 49:1408 (LILY; neuroblastoma SE)
- Hnisz D et al 2017 Cell 169:13 (phase-separation model of transcriptional control)
- Hay D et al 2016 Nat Genet 48:895 (genetic dissection of the alpha-globin super-enhancer)
- Moorthy S et al 2017 Genome Res 27:246 (SE constituents have equivalent/redundant regulatory roles in ESCs)
- Sengupta S & George RE 2017 Trends Cancer 3:269 (SE function review)

## Related Skills

- chip-seq/peak-calling - Generate H3K27ac / MED1 / BRD4 peaks for SE input
- chip-seq/chipseq-qc - Filter hyper-ChIPable peaks before SE calling
- chip-seq/spike-in-normalization - Mandatory for cross-condition SE comparison
- chip-seq/differential-binding - Quantitative differential testing on union SE set
- chip-seq/peak-annotation - Annotate SE-associated genes; cross-reference dELS
- chip-seq/cut-and-run-tag - SE calling on CUT&RUN/CUT&Tag H3K27ac (different spike-in)
- atac-seq/enhancer-gene-linking - ENCODE-rE2G for SE-target gene assignment
- data-visualization/genome-tracks - SE region visualization
<!-- END FILE: chip-seq/super-enhancers/SKILL.md -->

<!-- END CATEGORY: chip-seq -->

