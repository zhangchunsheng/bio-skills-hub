---
slug: bio-atac-seq-integrated
version: 1.0.1
displayName: "ATAC-seq分析 / ATAC-seq analysis"
name: bio-atac-seq-integrated
summary: "中文：ATAC-seq分析综合技能，整合 12 个相关专题，覆盖ATAC-seq分析：峰调用、consensus peakset、差异可及性、footprinting、motif偏差、scATAC-seq。 English: Integrated ATAC-seq analysis skill covering 12 related topics, including ATAC-seq analysis: peak calling, consensus peakset, differential accessibility, footprinting, motif deviation, scATAC-seq."
description: "中文：这是一个面向ATAC-seq分析的综合生物信息学 Skill，整合当前分类下 12 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：ATAC-seq分析：峰调用、consensus peakset、差异可及性、footprinting、motif偏差、scATAC-seq。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：ABC-Enhancer-Gene-Prediction, DiffBind, NucleoATAC。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for ATAC-seq analysis, combining 12 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers ATAC-seq analysis: peak calling, consensus peakset, differential accessibility, footprinting, motif deviation, scATAC-seq. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: ABC-Enhancer-Gene-Prediction, DiffBind, NucleoATAC. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# atac-seq 分类 Skill 整合版

> 本文件整合同一主分类目录下 12 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: atac-seq -->

## 子目录：atac-seq/allele-specific-accessibility

<!-- BEGIN FILE: atac-seq/allele-specific-accessibility/SKILL.md -->
---
name: bio-atac-seq-allele-specific-accessibility
description: Detect allele-specific chromatin accessibility from ATAC-seq using WASP, GATK ASEReadCounter, or RASQUAL. Use when mapping cis-regulatory genetic variants from heterozygous SNPs, separating cis from trans regulation, building chromatin QTL (caQTL) maps, validating GWAS variant function with allelic imbalance, or detecting reference allele mapping bias before downstream analysis.
tool_type: mixed
primary_tool: WASP
---

## Version Compatibility

Reference examples tested with: WASP 0.3.4+, GATK 4.4+, RASQUAL 1.1+, samtools 1.19+, bcftools 1.19+, vcftools 0.1.16+, plink 2.00+, MatrixEQTL 2.3+, QuASAR 0.1+, bowtie2 2.5+, bwa-mem2 2.2.1+, scipy 1.11+ (false_discovery_control), pandas 2+, pybedtools 0.10+.

Verify before use:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws unexpected errors, introspect the installed package and adapt rather than retrying.

# Allele-Specific Accessibility

**"Does this heterozygous SNP affect chromatin accessibility on its allele?"** -> Count ATAC reads supporting reference vs alternative allele at heterozygous sites in the same individual; significant deviation from 50:50 indicates cis-regulatory effect. Requires careful handling of reference-allele mapping bias (WASP filtering) and within-individual binomial testing.

- CLI: `WASP` (Geijn 2015) for de-biased reference mapping
- CLI: `gatk ASEReadCounter` for allele-specific count tables
- CLI: `RASQUAL` (Kumasaka 2016) for joint cis-mapping with allelic counts
- R: `QuASAR` (Harvey 2015) for genotype + ASE inference simultaneously

ASE/ASB analysis is fundamentally different from cohort-level differential. Statistical framework is binomial within-individual; sample size is the count of heterozygous SNPs in accessible regions, not the number of individuals.

## Algorithmic Taxonomy

| Tool | Method | Input | Strength | Fails when |
|------|--------|-------|----------|------------|
| WASP (Geijn 2015) | Realign reads where alt allele swap could change mapping; filter mapping-bias affected sites | BAM + VCF + reference | Mandatory for any ASE/ASB analysis; controls reference-allele bias | Slow on deep coverage; requires re-alignment step |
| GATK ASEReadCounter | Count REF and ALT reads at known heterozygous sites | BAM + VCF | Mature; integrates with GATK ecosystem; standard counter | Doesn't fix mapping bias (needs WASP first); single-sample |
| RASQUAL (Kumasaka 2016) | Joint cis-eQTL/caQTL model: total counts + allelic imbalance | BAM + VCF + peak counts | Best statistical power for caQTL when sample size is moderate (N=20-100); models genotype uncertainty | Complex setup; per-feature regression (slow); requires LD computation |
| QuASAR (Harvey 2015) | Genotype + ASE inference from RNA-seq or ATAC alone | BAM (no VCF needed) | Useful when genotypes are limited; integrates phasing | Less accurate than WASP+GATK when genotypes are known |
| MatrixEQTL on per-feature counts | Linear model fit on accessibility per peak | Genotypes + peak counts | Standard cohort-level caQTL; well-supported | No allelic imbalance information; needs sample size N >= 50 |
| Allelic Imbalance from Bayesian models (MAJIQ-style) | Bayesian beta-binomial | BAM + VCF | Models overdispersion appropriately | Niche; less mature than WASP+GATK |

Methodology evolves; verify against current Geijn 2015, Kumasaka 2016, Buchkovich 2015 before locking pipelines. Modern caQTL studies typically combine WASP + RASQUAL at modest N or WASP + GATK + linear caQTL at large N.

## Reference Allele Mapping Bias (The Single Most Important Issue)

When aligning reads to the reference genome, reads carrying the reference allele align with 0 mismatches; reads carrying the alternative allele have 1 mismatch and may fail to align (especially with `bwa-mem` -k or `bowtie2 --very-sensitive` thresholds). This **inflates the apparent reference-allele frequency** at every SNP and confounds ASE.

**Trigger:** Always (mapping bias is universal at heterozygous SNPs).

**Mechanism:** Aligners are mismatch-penalized. Without correction, ALT reads systematically under-align. Effect size: 1-5% bias toward reference at typical mismatch penalties.

**Symptom:** Per-SNP REF allele fraction skews above 50% even at sites without true allelic imbalance.

**Fix:** WASP. Pseudo-alleles every read at heterozygous sites; re-aligns swapped reads; keeps only reads that map identically to both haplotypes. Mandatory for any ASE/ASB analysis.

**Goal:** Remove reference-allele mapping bias before counting allele-specific ATAC reads.

**Approach:** Identify reads overlapping heterozygous SNPs, re-align allele-swapped versions, keep only reads consistent across both haplotypes, then count REF/ALT with GATK ASEReadCounter.

```bash
# WASP read-correction pipeline (Geijn 2015)
WASP_DIR=/path/to/WASP
PEAKS=peaks.bed                                  # ATAC peaks for filtering
SAMPLE=sample1
OUT=$SAMPLE.wasp_filtered.bam

# 1. Find reads at SNP sites
python $WASP_DIR/mapping/find_intersecting_snps.py \
    --is_paired_end \
    --is_sorted \
    --output_dir wasp_out/ \
    --snp_tab snp_h5/snp_tab.h5 \
    --snp_index snp_h5/snp_index.h5 \
    --haplotype snp_h5/haps.h5 \
    --samples $SAMPLE \
    $SAMPLE.bam

# 2. Re-align flipped-allele reads
bowtie2 -x hg38_idx -1 wasp_out/$SAMPLE.remap.fq1.gz \
                   -2 wasp_out/$SAMPLE.remap.fq2.gz \
                   -S wasp_out/$SAMPLE.remap.sam
samtools view -bS wasp_out/$SAMPLE.remap.sam | samtools sort -o wasp_out/$SAMPLE.remap.bam
samtools index wasp_out/$SAMPLE.remap.bam

# 3. Keep only consistently-mapped reads
python $WASP_DIR/mapping/filter_remapped_reads.py \
    wasp_out/$SAMPLE.to.remap.bam \
    wasp_out/$SAMPLE.remap.bam \
    wasp_out/$SAMPLE.kept.bam

# 4. Merge kept reads with non-overlapping reads
samtools merge $OUT \
    wasp_out/$SAMPLE.kept.bam \
    wasp_out/$SAMPLE.keep.bam

# After WASP filtering, GATK ASEReadCounter is safe
gatk ASEReadCounter \
    -I $OUT \
    -V heterozygous_snps.vcf \
    -R hg38.fa \
    -O $SAMPLE.ase_counts.tsv
```

## Per-Tool Failure Modes

### GATK ASEReadCounter without WASP -- Reference bias

**Trigger:** Running ASEReadCounter directly on a standard ATAC BAM without WASP filtering.

**Mechanism:** Reference allele over-counts due to alignment bias.

**Symptom:** Per-SNP reference fraction systematically > 0.5; aggregate plots show ~0.51-0.55 instead of 0.5.

**Fix:** WASP filter first, ALWAYS. There are no exceptions.

### Sample size for ASE per SNP

**Trigger:** Single-individual ATAC; per-SNP heterozygous coverage typically 10-100 reads.

**Mechanism:** Per-SNP binomial test has limited power; 10 reads at p=0.5 has 95% CI from 0.18 to 0.82 -- effectively no power for moderate effects.

**Fix:** Aggregate across many SNPs in the same peak (within-peak ASE); aggregate across replicates at same SNP; combine with cis-caQTL across cohort.

### RASQUAL -- LD computation requirement

**Trigger:** RASQUAL exits or returns NA for a feature.

**Mechanism:** RASQUAL estimates genotype/allelic correlation internally from the tabix-streamed VCF (no external LD matrix is needed or accepted). Failures instead come from the `-l` (testing SNP) and `-m` (feature SNP) counts not matching the SNPs actually present in the cis-window, or a feature with zero fSNPs.

**Fix:** Compute `-l`/`-m` from the actual VCF window rather than a fixed guess, and skip features with no feature SNPs; there is no LD-precompute step.

### WASP -- Phased vs unphased genotypes

**Trigger:** Using unphased genotypes for ASE.

**Mechanism:** ASE requires knowing which allele is on which haplotype to assign reads. Unphased het sites ambiguously assign reads.

**Fix:** Phase genotypes with SHAPEIT5, BEAGLE 5.4, or whatshap (read-based) before running WASP/ASE counter.

### Cohort-level caQTL without allelic info

**Trigger:** MatrixEQTL on peak counts without ASE.

**Mechanism:** MatrixEQTL maps cohort-level associations; misses cis-mode that ASE captures within individual.

**Symptom:** Power to detect caQTL is low (typical N=50-100 cohort gives ~hundreds of caQTLs vs ASE-augmented can give thousands).

**Fix:** Use RASQUAL (joint total + ASE) when N <= 100; or combine MatrixEQTL with separate ASE per individual.

### Read-deep peak coverage required

**Trigger:** Per-peak coverage < 30 reads at SNP site.

**Mechanism:** Binomial test power at p=0.5, n=30 yields detectable shifts only at |delta_p| >= 0.2.

**Fix:** Pool replicates if available; or restrict to peaks with sufficient coverage; or aggregate to per-individual peak-level ASE rather than per-SNP.

## Decision Tree by Setting

| Setting | Recommended pipeline |
|---------|---------------------|
| Single individual, ATAC + genotypes | WASP + GATK ASEReadCounter -> per-SNP and per-peak ASE; within-peak aggregation |
| Cohort N >= 100, want caQTL | WASP + GATK + MatrixEQTL on peak counts; supplement with ASE for cis-effects |
| Cohort N = 20-100 | WASP + RASQUAL (joint total + ASE) for max power |
| Cohort with no genotypes | QuASAR (infers genotypes from data) |
| Validating GWAS variant function | Look up het samples in cohort; aggregate ASE at the variant; ASB ratio |
| Trios or quartets | Per-trio phasing then ASE per individual |
| iPSC line genotype validation | Single-individual ASE at known SNPs |

## Cohort caQTL Pipeline

**Goal:** Build cohort-level chromatin QTLs by combining WASP-corrected per-sample counts with cis-genotype association.

**Approach:** WASP-correct each BAM, build consensus peakset, count reads in peaks per sample, then test cis-genotype association via MatrixEQTL (cohort) or RASQUAL (joint total + allelic).

```bash
# 1. WASP-correct each individual's BAM
for sample in $(cat samples.txt); do
    bash wasp_pipeline.sh $sample.bam $sample.vcf
done

# 2. Build consensus peakset (atac-seq/consensus-peakset)
# 3. Count reads in peaks per sample (featureCounts)
featureCounts -F SAF -a consensus.saf -o counts.tsv -p --countReadPairs *.wasp.bam

# 4. Cohort-level caQTL via MatrixEQTL
# (see R script in examples/)

# 5. Per-individual ASE (RASQUAL alternative)
# Parallel: gatk ASEReadCounter per sample, then merge for QuASAR meta-analysis
```

## Within-Peak ASE Aggregation

**Goal:** Boost per-SNP ASE power by pooling allele counts across heterozygous SNPs in the same peak.

**Approach:** Map each het SNP to its containing peak, sum REF and ALT counts per peak, run pooled binomial test against 50:50, apply BH FDR, and threshold on effect size.

```python
import pandas as pd, numpy as np
from scipy import stats

# Per-SNP allele counts at heterozygous sites
ase = pd.read_csv('sample.ase_counts.tsv', sep='\t')
ase = ase.rename(columns={'refCount': 'REF', 'altCount': 'ALT'})
ase['totalCount'] = ase['REF'] + ase['ALT']

# Map each SNP to its containing peak
ase['peak'] = map_snps_to_peaks(ase, 'consensus_peaks.bed')

# Aggregate within peak: pooled binomial test
def peak_ase(group):
    ref = group['REF'].sum()
    total = group['totalCount'].sum()
    if total < 30: return pd.Series({'ref_frac': np.nan, 'p_value': np.nan})
    p = stats.binomtest(ref, total, p=0.5).pvalue
    return pd.Series({'ref_frac': ref / total, 'p_value': p, 'snp_count': len(group)})

peak_ase_df = ase.groupby('peak').apply(peak_ase)
peak_ase_df['adj_p'] = stats.false_discovery_control(peak_ase_df['p_value'].fillna(1.0))
sig_ase = peak_ase_df[(peak_ase_df['adj_p'] < 0.05) & (abs(peak_ase_df['ref_frac'] - 0.5) >= 0.2)]
```

|ref_frac - 0.5| >= 0.2 is a 30:70 effect; smaller imbalances are detectable but biologically minor. Per-peak SNP count >= 2 strengthens the call.

## RASQUAL Joint Modeling

RASQUAL uses a non-standard CLI: it reads the VCF from stdin via tabix and uses single-letter flags. The canonical invocation pattern is:

**Goal:** Combine total accessibility counts and allele-specific counts into one joint cis-caQTL test per peak.

**Approach:** Pre-build binary count and offset files via rasqualTools, then iterate per-feature, streaming the cis-window VCF through tabix into RASQUAL with feature coordinates and SNP counts.

```bash
# 1. Pre-compute genotype offsets and binary count files (rasqualTools R package)
# (see rasqualTools::saveRasqualMatrices; produces .bin files for -y, -k)

# 2. Per-feature (peak) RASQUAL call: pipe tabix VCF in via stdin
# Per-line meaning: feature name, chromosome, start, end, n_testing_SNPs (cis-window rSNP candidates), n_feature_SNPs (fSNPs in the peak)
while IFS=$'\t' read -r name chr start end n_testing n_feature; do
    tabix cohort.vcf.gz $chr:$((start-500000))-$((end+500000)) | \
        rasqual -y counts.bin \
                -k offsets.bin \
                -n $N_SAMPLES \
                -j $FEATURE_INDEX \
                -l $n_testing -m $n_feature \
                -s $start -e $end \
                -f $name \
                > $name.rasqual.txt
done < features.tsv
```

`-y` is the binary count file; `-k` is the binary size-factor / offset file (both produced by `rasqualTools::saveRasqualMatrices` from R); `-j` is the row index of the feature; `-l` is the number of testing SNPs (cis-window rSNP candidates) and `-m` the number of feature SNPs (fSNPs overlapping the peak). RASQUAL does NOT use `--features`, `--counts`, `--vcf` flags; those are common in newer caQTL wrappers but not in stock RASQUAL.

For modern usage, the `rasqualTools` R wrapper (Kumasaka GitHub) handles this orchestration. Verify against `rasqual --help` because the flag set is unusual.

RASQUAL output includes joint p-values, total-only and ASE-only sub-tests; the joint test typically gains 1.5-3x power vs MatrixEQTL alone.

## Reconciliation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| GATK ASE shows REF > ALT systematically | WASP not run | Re-run with WASP filter; bias fixed |
| RASQUAL joint p << ASE-only p | Cis effect dominated by allelic component | Confirms cis-regulatory mechanism |
| ASE detected at SNP not in peak | Possible coding splice or 3' UTR effect | Check annotation; may not be regulatory |
| Cohort caQTL doesn't replicate per-individual ASE | Trans effect or technical artifact | Consider trans-effect; or single-individual outliers |

**Operational rule for high-confidence reporting:** A cis-regulatory variant must show (a) WASP-filtered allelic imbalance with adjusted p < 0.05 and effect size >= 0.2, AND (b) cohort-level caQTL p < 1e-5 (or RASQUAL joint p < 1e-5), AND (c) accessibility peak overlap. Validation against MPRA or CRISPRi-FlowFISH increases confidence.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Reference allele systematically over-represented | WASP not run | Mandatory WASP filter |
| ASE per-SNP coverage too low | Sparse coverage; rare alleles | Aggregate across SNPs in peak; or filter SNPs with allele freq 0.1-0.9 |
| RASQUAL crashes/NA on small features | Feature has no fSNPs, or `-l`/`-m` counts mismatch the VCF window | Skip features with 0 feature-SNPs; compute `-l`/`-m` from the actual window |
| caQTL replication low | Cohort-effect vs cis-effect confusion | Use RASQUAL joint or replicate ASE separately |
| Phased vs unphased confusion | Different software expectations | Phase with SHAPEIT5/BEAGLE before any ASE |
| GATK ASEReadCounter fails on multiallelic sites | Multi-allelic complications | Pre-filter VCF to biallelic only with bcftools |
| WASP runs slow | Re-alignment step is dominant | Parallelize per-chromosome; or use samtools faidx + region-based parallelism |

## References

- van de Geijn B et al 2015 Nat Methods 12:1061 (WASP; reference allele bias correction)
- Castel SE et al 2015 Genome Biol 16:195 (GATK ASEReadCounter; ASE framework)
- Kumasaka N et al 2016 Nat Genet 48:206 (RASQUAL; joint total + ASE caQTL)
- Harvey CT et al 2015 Bioinformatics 31:1235 (QuASAR)
- Buchkovich ML et al 2015 BMC Med Genomics 8:43 (reference mapping-bias correction with limited/no genotype data; AA-ALIGNER)
- Browning SR & Browning BL 2007 Am J Hum Genet 81:1084 (BEAGLE phasing)
- Patterson M et al 2015 J Comput Biol 22:498 (whatshap; read-based phasing)

## Related Skills

- atac-seq/atac-peak-calling - Generate peaks for ASE within-peak aggregation
- atac-seq/consensus-peakset - Cohort consensus peakset
- atac-seq/differential-accessibility - Cohort-level (cis + trans) differential
- atac-seq/deep-learning-atac - Predicted variant effects vs observed allelic imbalance
- atac-seq/enhancer-gene-linking - Map ASE-supported variants to target genes
- variant-calling/vcf-basics - VCF input
- variant-calling/joint-calling - Cohort genotype inputs
- phasing-imputation/haplotype-phasing - Phasing before WASP
- causal-genomics/fine-mapping - Use caQTL for fine-mapping
- population-genetics/association-testing - GWAS context
<!-- END FILE: atac-seq/allele-specific-accessibility/SKILL.md -->

## 子目录：atac-seq/atac-peak-calling

<!-- BEGIN FILE: atac-seq/atac-peak-calling/SKILL.md -->
---
name: bio-atac-seq-atac-peak-calling
description: Call accessible chromatin regions from ATAC-seq BAM files using MACS3, MACS2, Genrich, or HMMRATAC. Use when identifying open chromatin from aligned ATAC-seq, choosing between point-source vs HMM peak callers, applying ENCODE-style pseudoreplicate IDR, removing blacklist regions, or fixing 501bp consensus peaks for downstream differential analysis.
tool_type: cli
primary_tool: macs3
---

## Version Compatibility

Reference examples tested with: MACS3 3.0.2+, MACS2 2.2.9+, Genrich 0.6.1+, HMMRATAC 1.2+ (now bundled in MACS3 as `macs3 hmmratac`), samtools 1.19+, bedtools 2.31+, IDR 2.0.4+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed binary (`<tool> -h`) and adapt the example to match the actual CLI rather than retrying.

# ATAC-seq Peak Calling

**"Call accessible regions from my ATAC-seq BAM"** -> Identify Tn5-hypersensitive open chromatin, treating fragments as point insertion events (not protein-bound regions as in ChIP-seq) and accounting for the lack of input control.

- CLI (canonical, ENCODE 4): `macs2 callpeak -t atac.bam -f BAM -g hs -n sample --nomodel --shift -75 --extsize 150 --keep-dup all -B --SPMR -p 0.01` (use `-f BAM`, not `-f BAMPE` -- BAMPE reads true fragment ends and ignores `--shift`/`--extsize`)
- CLI (HMM-based, single sample): `macs3 hmmratac -i atac.bam -n sample --outdir hmm_out`
- CLI (joint replicates): `Genrich -j -t rep1.bam,rep2.bam -o peaks.narrowPeak -e chrM -E blacklist.bed`

The `-p 0.01` (loose) plus IDR is the ENCODE pattern: low stringency increases peak overlap between replicates, and IDR rescues the reproducible set. Single-sample workflows usually swap to `-q 0.05` instead.

## Algorithmic Taxonomy

| Tool | Model | Treats fragments as | Min reps | Strength | Fails when |
|------|-------|---------------------|----------|----------|------------|
| MACS3/MACS2 | Local Poisson lambda + FDR | Point-source insertions (+/- shift) | 1 | Mature, ENCODE-default, fast, narrow + broad modes | Confounds NFR with broad accessible domains; no input means lambda from local genome only |
| Genrich (ATAC mode -j) | q-value on log-transformed p-value, joint replicate model | Whole fragments (paired-end intervals) | 1 (multi-rep optional) | Treats reps jointly; can exclude chrM via `-e chrM`; auto blacklist via `-E`; PCR-dup removal via `-r` | Less peer-reviewed than MACS; thin literature; slow on deep libraries |
| MACS3 hmmratac (was HMMRATAC) | 3-state HMM (open / nucleosomal / background) on fragment-size signal | Fragment-size classes | 1 | Models nucleosome periodicity directly; differentiates NFR and flanking nucleosomes | Needs >= 30M de-duplicated nuclear reads; memory-hungry; slow; flat fragment distribution -> garbage HMM |
| HOMER `findPeaks -style dnase` | Fixed window + fold-change cutoff | Tag positions | 1 | Convenient for downstream HOMER motif analysis | Less calibrated p-values than MACS; window-size sensitive |
| nf-core/atacseq | Wrapper (MACS2 by default) | Same as MACS2 | 1 | Reproducible Nextflow pipeline with QC built in | Only as good as the underlying caller |

Methodology evolves; verify the current ENCODE ATAC-seq Standards (encodeproject.org pipelines/atac-seq) before locking parameters. ENCODE 4 still defaults to MACS2 (not MACS3) at time of writing; `macs3 callpeak` is API-compatible for ATAC parameters but not yet the official ENCODE binary.

## Shift-Extend vs BAMPE: The Critical Choice

Two valid ways to feed paired-end ATAC into MACS:

**Pattern A (ENCODE / "single-end-ified"):** `-f BAMPE` actually IGNORES `--shift/--extsize`. To activate them, use `-f BAM` and treat each end independently. ENCODE's pipeline uses `-f BAM --shift -75 --extsize 150` to model each Tn5 cut as a 150 bp window centered on the insertion site, ignoring fragment lengths.

**Pattern B (paired-fragment):** `-f BAMPE` uses the full paired-end fragment span as the signal interval. Best when fragment lengths are biologically meaningful (e.g., NFR-only peak calling at 38/75 bp). In BAMPE mode, do NOT set `--shift/--extsize` (silently ignored, but confusing).

For most bulk ATAC, Pattern A matches ENCODE convention and is reproducible against published peak sets. Pattern B can be more sensitive at narrow regulatory elements but does not match ENCODE outputs.

## Effective Genome Size

`-g hs` and `-g mm` are MACS shorthands for old defaults. Modern values:

| Genome | MACS shorthand | Actual mappable size | Source |
|--------|---------------|----------------------|--------|
| hg38 | `-g hs` (2.7e9) | 2.701e9 (50bp), 2.748e9 (75bp), 2.806e9 (100bp), 2.862e9 (150bp) | deepTools `effectiveGenomeSize` |
| hg19 | `-g hs` (2.7e9) | 2.686e9 (50bp), 2.777e9 (100bp) | deepTools |
| mm10 | `-g mm` (1.87e9) | 2.308e9 (50bp), 2.408e9 (75bp), 2.467e9 (100bp) | deepTools |
| mm39 | none | 2.310e9 (50bp), 2.468e9 (100bp) | deepTools |

Wrong size shifts every q-value but rarely changes peak ranks. Use `unique-kmers.py` (khmer) or the deepTools tabulated values for exact sizes; the shorthand is a decade-old approximation.

## Effective Genome Size: When It Matters

**Trigger:** Comparing peaks across genome builds or species; reproducing published q-value cutoffs; hi-resolution lambda estimation.

**Mechanism:** MACS estimates genome-wide lambda as `total_reads / effective_size`. Wrong size -> wrong null -> shifted q-values, especially at the marginal cutoff.

**Symptom:** Peak counts diverge ~10-20% from published numbers when re-running an old dataset.

**Fix:** Pull the read-length-matched value from deepTools `effectiveGenomeSize` table. For pipelines, parameterize this; never inline the shorthand for cross-study comparisons.

## Per-Tool Failure Modes

### MACS2/MACS3 -- Confounded NFR + broad accessibility

**Trigger:** Cell type with extended open domains (e.g., active super-enhancers, MYOD1 regulons, locus-control regions).

**Mechanism:** Default narrow-peak mode segments wide accessible domains into multiple smaller peaks at local lambda spikes; `--broad --broad-cutoff 0.1` merges them but inflates total length and breaks IDR comparability.

**Symptom:** Peak count >> 200k for human bulk ATAC at ENCODE depth; mean peak width < 200 bp; visual inspection in IGV shows 3-5 calls under one continuous accessibility block.

**Fix:** Run both narrow and broad; use narrow for differential analysis, broad for domain-level enrichment (e.g., super-enhancer overlap). Do NOT use `--call-summits` for broad mode.

### Genrich -- Replicate weighting and chrM exclusion

**Trigger:** Replicates with very different library sizes; high-mitochondrial samples not pre-filtered.

**Mechanism:** Genrich's joint mode combines the per-replicate p-values at each position via Fisher's method. Library-size imbalance dominates the joint p-value; chrM reads inflate background unless `-e chrM` is set.

**Symptom:** Most-significant peaks cluster on chrM or on the largest-library replicate's high-coverage regions.

**Fix:** Always pass `-e chrM` (Genrich 0.6+) and `-E blacklist.bed`. Down-sample BAMs to common depth (`samtools view -s`) before joint calling if libraries differ >2x. Add `-r` to remove PCR duplicates inside Genrich, OR pre-deduplicate (do not do both).

### MACS3 hmmratac (HMMRATAC) -- Depth and fragment-size dependence

**Trigger:** Library < 25M nuclear reads, or libraries with degraded chromatin and flat fragment-size distribution.

**Mechanism:** The 3-state HMM is trained from fragment-size classes (NFR ~50 bp, mono ~200 bp, di ~400 bp peaks). Without periodicity the emission distributions collapse and the HMM cannot separate states.

**Symptom:** Output BED is empty, or all peaks are tiny (~150 bp) with no nucleosome flanks called; runtime explodes (>24h) on shallow data.

**Fix:** Verify fragment-size periodicity in QC first (atac-qc skill). If flat, fall back to MACS3 callpeak. HMMRATAC needs deep coverage (a practical minimum around 30M deduplicated nuclear reads).

### HOMER findPeaks -- Window-size sensitivity

**Trigger:** Default `-style dnase` uses 75 bp peaks; ATAC peaks are 250-500 bp typically.

**Mechanism:** HOMER's window-based caller does not auto-fit width to ATAC.

**Fix:** Use `-style factor -size 150` for narrow ATAC peaks, or skip HOMER for peak calling and use it only for downstream motif analysis on MACS peaks.

### Aligner choice -- chromap vs bwa-mem2 vs bowtie2 affects peak shape

**Trigger:** Switching aligners between datasets and expecting reproducible peaks.

**Mechanism:** chromap (Zhang 2021) applies its own ATAC-specific 4 bp / -5 bp Tn5 shift before fragment output; bwa-mem2 and bowtie2 do not. Downstream `--shift -75 --extsize 150` parameters are calibrated for unshifted bwa/bowtie BAMs; applying them to chromap output double-shifts the signal.

**Symptom:** Peaks called from chromap output are shifted by ~5-10 bp relative to bwa output at the same locus.

**Fix:** When using chromap, drop `--shift` and `--extsize` (chromap's pre-shift is sufficient) OR omit chromap's `--Tn5-shift` (the shift is opt-in, applied only when that flag or an ATAC preset is set) so it is not double-applied, then proceed with standard MACS parameters. Document the aligner version and any shift choices in methods. Within a project, pin the aligner.

### Single-sample (no replicate) -- Rotation / circular-shift permutation

**Trigger:** Single biological sample without any replicate for IDR.

**Mechanism:** IDR requires two replicates by construction. For n=1, statistical confidence per peak comes from local background (Poisson p-value) but reproducibility cannot be assessed.

**Fix:** Apply a stricter `-q 0.01` (vs ENCODE `-p 0.01` + IDR pattern) and additionally apply rotation/circular-shift permutation: shift the BAM cuts by a random distance modulo each chromosome and re-call peaks; the per-peak persistence rate across rotations is a non-parametric reproducibility proxy. Document this is a single-sample heuristic, not ENCODE-compliant.

## ENCODE 3 vs ENCODE 4 Differences

| Feature | ENCODE 3 (legacy) | ENCODE 4 (current) |
|---------|-------------------|---------------------|
| Per-rep significance threshold | `-q 0.05` directly | `-p 0.01` (loose) + IDR |
| Pseudoreplicate IDR cutoff | Not formalized | `--idr-threshold 0.10` self-consistency |
| TSS enrichment threshold | >= 6 (older) | >= 7 (hg38, GENCODE v29) |
| Mt fraction expectation | < 25% | < 20% (Omni-ATAC < 5%) |
| Blacklist | v1 | v2 (Amemiya 2019) |
| Default genome size | hardcoded `hs`/`mm` | encouraged: deepTools effectiveGenomeSize |

To reproduce a published ENCODE 3 dataset, pin the original pipeline and threshold exactly. ENCODE 4 results are not directly numerically comparable to ENCODE 3 even on the same input BAM.

## Super-Enhancer Detection

For active super-enhancer (SE) annotation alongside narrow-peak workflow, ROSE (Whyte 2013) and LILY (Boeva 2017) stitch ATAC or H3K27ac peaks separated by < 12.5 kb and rank by signal:

```bash
# ROSE expects H3K27ac BAM but works on ATAC narrowPeak with care
ROSE_main.py -g hg38 -i atac_peaks.gff -r atac.bam -o rose_out/ -t 2500
```

ROSE-style stitching is complementary to MACS3 narrow peaks: narrow peaks for differential analysis; SE annotation for biology interpretation. SE calls require H3K27ac input for definitive annotation; ATAC alone produces "stretch enhancers" that overlap but are not identical to H3K27ac SE.

## ENCODE 4 ATAC-seq Pipeline (Reference Implementation)

The exact ENCODE pattern produces the most-comparable peak sets:

```bash
# Per-replicate peak calling (loose threshold)
macs2 callpeak \
    -t rep1.filt.dedup.bam \
    -f BAM -g hs \
    -n rep1 --outdir peaks/rep1/ \
    --nomodel --shift -75 --extsize 150 \
    --keep-dup all \
    -B --SPMR \
    -p 0.01

# Pooled (all replicates)
macs2 callpeak \
    -t rep1.filt.dedup.bam rep2.filt.dedup.bam \
    -f BAM -g hs -n pooled --outdir peaks/pooled/ \
    --nomodel --shift -75 --extsize 150 --keep-dup all -B --SPMR -p 0.01

# Pseudoreplicates (two independent 50% subsamples; approximate, not a disjoint partition)
samtools view -b -h -s 1.5 rep1.filt.dedup.bam > rep1.psr1.bam   # seed.fraction
samtools view -b -h -s 2.5 rep1.filt.dedup.bam > rep1.psr2.bam   # different seed
# (call peaks on each pseudoreplicate the same way)
```

`--SPMR` writes signal as Signal Per Million Reads (normalized bedGraph). `-p 0.01` is intentionally loose; IDR will tighten to a reproducible set.

## IDR for Reproducible Peaks

**Goal:** Find peaks reproducible across biological replicates at controlled IDR.

**Approach:** Score paired peak lists by signalValue, fit IDR's two-component mixture (reproducible + noise), threshold at IDR <= 0.05 (true reps) or 0.10 (pseudoreplicates).

```bash
# Sort peaks by p-value (column 8) so IDR scores by significance
sort -k8,8nr rep1_peaks.narrowPeak > rep1.sorted.narrowPeak
sort -k8,8nr rep2_peaks.narrowPeak > rep2.sorted.narrowPeak

# True replicates -- threshold IDR <= 0.05
idr --samples rep1.sorted.narrowPeak rep2.sorted.narrowPeak \
    --input-file-type narrowPeak --rank p.value \
    --output-file true_reps.idr \
    --idr-threshold 0.05 --plot --log-output-file idr.log

# Pseudoreplicates -- threshold IDR <= 0.10 (looser, ENCODE Nself <= 2 rule)
idr --samples psr1_peaks.narrowPeak psr2_peaks.narrowPeak \
    --input-file-type narrowPeak --rank p.value \
    --output-file psr.idr --idr-threshold 0.10 --plot
```

**ENCODE consistency rules:** Nt = peaks passing IDR on true reps; Nself = peaks passing IDR on pseudoreps. Library passes if `max(Nt, Nself) / min(Nt, Nself) <= 2`. If both ratios > 2, the library is rejected.

**IDR fails when:** Ranking column choice matters. `--rank p.value` (column 8) is robust; `--rank signal.value` (column 7) breaks if MACS pile-up scaling differs between replicates.

## Decision Tree by Experimental Scenario

| Scenario | Recommended caller | Why |
|----------|-------------------|-----|
| Bulk ATAC, 2-3 reps, depth >= 25M | MACS2 ENCODE pipeline + IDR | Reproducible, comparable to published peaksets |
| Bulk ATAC, 1 sample (no rep) | MACS3 callpeak with `-q 0.05`; do not run IDR | IDR is meaningless without reps; tighter q-value substitutes |
| Bulk ATAC, depth >= 30M, want NFR + flanking nuc structure | MACS3 hmmratac | HMM separates NFR from nucleosome flanks |
| Multi-replicate joint analysis where rep weighting is symmetric | Genrich `-j` ATAC mode | Joint p-value across reps; built-in chrM and blacklist |
| Cell type with broad super-enhancer accessibility | MACS3 `--broad --broad-cutoff 0.1` for SE; narrow for differential | Domain-level inference vs site-level |
| FFPE / degraded chromatin (flat fragment dist) | MACS3 callpeak with stringent `-q 0.01`; never HMMRATAC | HMM needs fragment periodicity |
| scATAC pseudobulk per cluster | MACS3 callpeak per cluster + iterative overlap | See atac-seq/single-cell-atac |
| Want fixed-width consensus peaks for differential | Call broadly, then re-center to summits +/- 250 bp | See atac-seq/consensus-peakset |
| Plant / non-model organism | MACS3 with `-g <effective_size>`; verify size empirically | Default `-g hs/mm` invalid; compute via khmer |

## Reconciliation: When Callers Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| MACS narrow peaks much fewer than Genrich | Genrich q-cutoff different default (`-q 0.05` log-scale, MACS `-q 0.05` linear) | Re-run with `-q 0.01` (Genrich) for parity |
| HMMRATAC misses peaks MACS finds | Library too shallow OR fragment-size periodicity weak | Trust MACS; HMMRATAC is depth-sensitive |
| HMMRATAC calls peaks MACS misses | HMM is sensitive to mid-strength accessibility flanked by phased nucleosomes | Inspect; often genuine but unconfirmed by short-fragment signal |
| Same peak called by all but width 2x different | Broad mode vs narrow mode mismatch | Standardize: re-center to summit +/- 250 bp for differential |
| Per-rep MACS calls peak; pooled MACS does not | One rep dominates; lambda smoothes it out in pooled | Trust pooled + IDR over per-rep counts |

**Operational rule for high-confidence reporting:** Require a peak to pass IDR <= 0.05 on true replicates AND survive blacklist/greylist filtering AND have mean signalValue >= 5 across reps. Two callers from different families (MACS + Genrich) agreeing within 250 bp is acceptable evidence when IDR is unavailable.

## Blacklist and Greylist

```bash
# ENCODE blacklist (Amemiya 2019) -- always remove
wget https://github.com/Boyle-Lab/Blacklist/raw/master/lists/hg38-blacklist.v2.bed.gz
gunzip hg38-blacklist.v2.bed.gz
bedtools intersect -v -a peaks.narrowPeak -b hg38-blacklist.v2.bed > peaks.no_blacklist.narrowPeak

# Sample-specific greylist (input-derived high-signal regions; rarely available for ATAC)
# For ATAC, ENCODE recommends pooling all samples' top-percentile signal and removing
# regions exceeding 100x median coverage as a "soft greylist"
```

Blacklist is mandatory; greylist is optional and most useful when the same library prep produces consistent artifact regions across samples.

## NFR-Only Peak Calling

**Goal:** Call peaks using only sub-nucleosomal fragments (<100 bp) for sharper TF-binding-relevant accessibility.

**Approach:** Pre-filter BAM to short fragments, then call peaks with parameters scaled to the smaller fragment length.

```bash
samtools view -h sample.dedup.bam | \
    awk 'substr($0,1,1)=="@" || ($9 > 0 && $9 < 100) || ($9 < 0 && $9 > -100)' | \
    samtools view -b > nfr.bam
samtools index nfr.bam

macs2 callpeak -t nfr.bam -f BAM -g hs -n sample_nfr \
    --nomodel --shift -37 --extsize 75 \
    --keep-dup all -p 0.01
```

`--shift -37 --extsize 75` halves both parameters to match shorter fragments; this is a fragment-scaled convention for NFR-focused input, not a TOBIAS-specified setting (TOBIAS instead applies the +4/-5 Tn5 correction to the full BAM via ATACorrect).

## Output Files (narrowPeak)

| Column | Field | Notes |
|--------|-------|-------|
| 1-3 | chrom, start, end | 0-based, half-open |
| 4 | name | MACS auto-numbers |
| 5 | score | Min(int(-10*log10(qvalue)), 1000) |
| 6 | strand | `.` for ATAC |
| 7 | signalValue | Fold enrichment over local lambda |
| 8 | pValue | -log10 p |
| 9 | qValue | -log10 q (BH-FDR) |
| 10 | summit_offset | Peak summit relative to start |

Convert to bigWig for browsers: `sort -k1,1 -k2,2n sample_treat_pileup.bdg > sample.sorted.bdg && bedGraphToBigWig sample.sorted.bdg chrom.sizes sample.bw` (bedGraphToBigWig is multi-pass and cannot read from a pipe/stdin, so sort to a file first).

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `--shift/--extsize ignored` warning | Used `-f BAMPE` with these flags | Switch to `-f BAM` or remove the flags |
| 0 peaks called | Forgot `--nomodel`; MACS tries to build a shifting model and fails | Add `--nomodel --shift -75 --extsize 150` |
| Peak count >> 500k | Did not deduplicate; or did not remove chrM; or `-q` too loose | Pre-filter (samtools view -F 1804 -q 30; samtools idxstats); use `-q 0.01` |
| `Sequence chrM not found` (Genrich) | Wrong chromosome name in `-e` flag (chrM vs MT) | Match BAM header naming convention |
| HMMRATAC out of memory | Deep library / large genome; the current tool is `macs3 hmmratac` (Python, not Java) | Increase available RAM and use a scratch `--outdir`; the `-Xmx`/`HMMRATAC.jar` heap flags apply only to the deprecated standalone Java HMMRATAC |
| Peaks shifted by 75 bp from expected positions | Forgot `--shift -75` (cuts at one end of read) | Add the shift; positions are now centered on Tn5 cut site |
| IDR returns 0 reproducible peaks | Sorted by wrong column; ranks are random | Sort each peakset by `-k8,8nr` (p-value descending) |

## References

- Buenrostro JD et al 2013 Nat Methods 10:1213 (ATAC-seq protocol)
- Corces MR et al 2017 Nat Methods 14:959 (Omni-ATAC protocol)
- Corces MR et al 2018 Science 362:eaav1898 (iterative-overlap fixed-width 501 bp consensus peaks)
- Tarbell ED & Liu T 2019 Nucleic Acids Res 47:e91 (HMMRATAC)
- Gaspar JM, Genrich: detecting sites of genomic enrichment (github.com/jsh58/Genrich; no published paper)
- Li Q et al 2011 Ann Appl Stat 5:1752 (IDR framework)
- Landt SG et al 2012 Genome Res 22:1813 (ENCODE/modENCODE peak calling guidelines, IDR Nself rule)
- Amemiya HM et al 2019 Sci Rep 9:9354 (ENCODE blacklist v2)
- ENCODE ATAC-seq Standards (encodeproject.org/atac-seq) -- canonical pipeline parameters

## Related Skills

- atac-seq/atac-qc - Verify TSS enrichment, FRiP, and fragment periodicity before calling
- atac-seq/consensus-peakset - Combine per-sample peaks into a fixed-width differential-ready set
- atac-seq/single-cell-atac - Pseudobulk peak calling per cluster
- atac-seq/differential-accessibility - Downstream DiffBind/csaw/DESeq2 testing
- atac-seq/deep-learning-atac - chromBPNet bias-corrected per-base profiles as alternative input
- read-alignment/bowtie2-alignment - Upstream ATAC alignment
- alignment-files/duplicate-handling - Pre-call dedup with Picard MarkDuplicates
- chip-seq/peak-calling - ChIP-seq comparison (uses input control)
- chip-seq/super-enhancers - ROSE / LILY for super-enhancer annotation
- genome-intervals/bed-file-basics - Peak file manipulation
<!-- END FILE: atac-seq/atac-peak-calling/SKILL.md -->

## 子目录：atac-seq/atac-qc

<!-- BEGIN FILE: atac-seq/atac-qc/SKILL.md -->
---
name: bio-atac-seq-atac-qc
description: ATAC-seq library quality control -- TSS enrichment, FRiP, fragment-size periodicity, library complexity (NRF/PBC1/PBC2), mitochondrial fraction, and ENCODE 4 thresholds. Use when assessing whether an ATAC-seq library passes ENCODE acceptance criteria, diagnosing transposition artefacts, comparing Omni-ATAC vs standard prep quality, or selecting which replicates to drop before peak calling.
tool_type: mixed
primary_tool: deeptools
---

## Version Compatibility

Reference examples tested with: deepTools 3.5+, Picard 3.1+, samtools 1.19+, bedtools 2.31+, ATACseqQC 1.26+, pysam 0.22+, pyBigWig 0.3+, numpy 1.26+, pandas 2.2+, MultiQC 1.21+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt.

# ATAC-seq Quality Control

**"Does my ATAC library pass ENCODE quality criteria?"** -> Compute the seven canonical metrics (depth, alignment rate, mitochondrial fraction, library complexity, fragment-size periodicity, TSS enrichment, FRiP) and compare against ENCODE 4 thresholds, then diagnose failures.

- CLI: `picard CollectInsertSizeMetrics`, `samtools flagstat`, `samtools idxstats`
- CLI: `deeptools plotFingerprint`, `computeMatrix reference-point` + `plotProfile`
- R: `ATACseqQC::TSSEscore`, `ATACseqQC::fragSizeDist`, `ATACseqQC::PTscore`
- Python: custom NRF/PBC from coordinate hash; pyBigWig for TSS enrichment

## ENCODE 4 ATAC-seq Acceptance Thresholds

| Metric | Definition | Ideal | Acceptable | Reject | Source |
|--------|-----------|-------|------------|--------|--------|
| Nuclear reads (after dedup, no chrM) | Mapped, MAPQ >= 30, non-chrM, deduped | >= 50M | 25-50M | < 25M | ENCODE 4 ATAC-seq Standards |
| Alignment rate | Mapped / total reads | >= 95% | 80-95% | < 80% | ENCODE 4 |
| Mitochondrial fraction | chrM / total mapped | < 5% (Omni-ATAC), < 20% (standard) | 20-50% | > 50% | Corces 2017 (Omni-ATAC) |
| NRF (Non-Redundant Fraction) | Distinct positions / total reads | >= 0.9 | 0.7-0.9 | < 0.7 | Landt 2012 |
| PBC1 (PCR Bottlenecking Coefficient 1) | Positions w/ 1 read / Positions w/ >= 1 read | >= 0.9 | 0.7-0.9 | < 0.7 | Landt 2012 |
| PBC2 | Positions w/ 1 read / Positions w/ 2 reads | >= 3.0 | 1.0-3.0 | < 1.0 | Landt 2012 |
| TSS enrichment (hg38, GENCODE v29) | Avg signal at TSS / avg flanking | >= 7 | 5-7 | < 5 | ENCODE 4 |
| FRiP (Fraction Reads in Peaks) | Reads in MACS peaks / total | >= 0.3 | 0.2-0.3 | < 0.2 | ENCODE 4, Landt 2012 |
| Insert-size periodicity | NFR + mono-nuc + di-nuc peaks visible | Clear 3+ peaks | NFR + mono only | Flat / single peak | Buenrostro 2013 |

ENCODE thresholds are organism-specific. Mouse (mm10, GENCODE M21) TSS enrichment >= 5 is acceptable; non-model organisms have no published threshold (use cohort percentile rank instead). Methodology evolves; verify against the current ENCODE ATAC-seq Standards before reporting.

## TSS Enrichment: ENCODE Method vs ATACseqQC Method

The two most common implementations DO NOT produce identical scores.

| Method | Numerator | Denominator | Scaling |
|--------|-----------|-------------|---------|
| ENCODE pyTSSe / Kundaje gtsse | Mean signal in 100 bp window centered at TSS | Mean signal in 100 bp window at +/- 1900 to +/- 2000 bp (flanks) | Per-base normalization to flanks; reported as fold-enrichment |
| ATACseqQC TSSEscore | Sum signal in TSS +/- 100 bp | Sum signal at +/- 1000 bp flanking windows | Different window sizes; ratios are larger |
| deeptools plotProfile | Visual; numeric ratio not standardized | Reference-point matrix | No standard score; for visualization only |

**Trigger:** Comparing a TSS score across studies.

**Mechanism:** Different normalization windows shift the absolute number; ATACseqQC's TSSEscore is typically 2-3x ENCODE's because of the wider flank.

**Symptom:** Reported score 21 vs ENCODE-ideal 7 mismatch. Likely the calculator was ATACseqQC; the equivalent ENCODE score might be 8.

**Fix:** State which implementation was used. For ENCODE comparisons, use `pyTSSe` (Kundaje lab) or implement the ENCODE recipe directly.

```python
import numpy as np
import pyBigWig

def encode_tss_enrichment(bw_path, tss_bed, flank=2000):
    """ENCODE-style TSS enrichment: signal at TSS center / signal at flanks."""
    bw = pyBigWig.open(bw_path)
    profiles = []
    for line in open(tss_bed):
        chrom, start, end, *rest = line.strip().split('\t')
        tss = int(start)
        strand = rest[2] if len(rest) > 2 else '+'
        try:
            vals = bw.values(chrom, tss - flank, tss + flank)
            if vals is None or len(vals) != 2 * flank: continue
            if strand == '-': vals = vals[::-1]
            profiles.append(np.nan_to_num(vals))
        except RuntimeError:
            continue
    avg = np.nanmean(profiles, axis=0)
    flank_signal = np.mean(np.concatenate([avg[:100], avg[-100:]]))
    center_signal = np.mean(avg[flank - 50: flank + 50])
    return center_signal / flank_signal if flank_signal > 0 else 0.0
```

## Fragment-Size Periodicity Patterns

| Pattern | Visual signature | Interpretation | Action |
|---------|-----------------|----------------|--------|
| Strong tri-modal | NFR (~50bp) >> mono (~200bp) > di (~400bp) > tri (~600bp) peaks | Excellent transposition; well-positioned chromatin | Pass |
| Clear bi-modal | NFR + mono only, di and tri faint | Acceptable; common in Omni-ATAC | Pass |
| Single broad peak | Flat after NFR or no NFR | Over-transposition (too much Tn5) OR degraded chromatin | Reject; cannot distinguish nucleosomes |
| Inverted (mono >> NFR) | Mono peak dominant, NFR weak | Under-transposition OR chromatin condensation | Caution; peak counts will be low |
| Sharp 147 bp spike with no flanks | Tight peak at 147 bp | ChIP-seq input contamination (MNase-like) | Reject; not ATAC-grade |
| 10.4 bp helical periodicity overlay | Sub-peaks at 50, 60, 70, 80 bp on NFR | Excellent chromatin structure resolution; helical phasing visible | Pass; high-quality |

The 10.4 bp helical periodicity is a Buenrostro 2013 hallmark: it reflects the helical pitch of B-form DNA, with Tn5 preferring outward-facing minor grooves on nucleosomal DNA. Its presence is a positive QC indicator but not required.

## Per-Metric Failure Modes

### Mitochondrial fraction > 50%

**Trigger:** Standard ATAC-seq protocol on intact cells (no nuclear isolation), or insufficient detergent in lysis.

**Mechanism:** Mitochondrial DNA is naked (no histones), so Tn5 hyperactively cuts it. Without nuclear-isolation steps (Omni-ATAC pre-spin, OR digitonin lysis with mt removal), chrM dominates the library.

**Symptom:** `samtools idxstats sample.bam | awk '$1=="chrM"'` shows >50% of mapped reads on chrM.

**Fix:** Re-prep with Omni-ATAC (Corces 2017) or fast-ATAC. Re-running QC on chrM-stripped BAM hides the underlying problem; the wasted sequencing remains. If chrM fraction is 30-50%, the library may still be salvageable via chrM removal but yield is reduced.

### NRF / PBC1 / PBC2 below threshold

**Trigger:** Over-amplified library; low input cell count combined with high PCR cycles.

**Mechanism:** Each PCR cycle doubles starting fragments. With low complexity input (<5000 cells) and >12 cycles, distinct fragments saturate and reads pile up at identical positions. NRF measures unique fragments / total; PBC2 specifically detects multi-copy duplication.

**Symptom:** NRF < 0.7; PBC2 < 1.0; massive duplicate-removal loss in `samtools markdup`.

**Fix:** No fix post-hoc. Re-prep with more starting cells and fewer PCR cycles. Note: ATAC has *legitimate* duplicates at hyperaccessible sites (Tn5 cuts identically there), so NRF < 0.9 is not by itself fatal. The combined PBC1 < 0.7 + PBC2 < 1.0 + visual coverage pile-ups confirm true bottlenecking.

### TSS enrichment < 5

**Trigger:** Generic chromatin opening throughout the genome (over-transposition), OR genome build mismatch between TSS BED and BAM, OR strand-flip in TSS file.

**Mechanism:** TSS enrichment requires that signal at TSSs is >> signal in genomic flanks. Over-transposition flattens the signal landscape. Strand-flipped TSSs subtract real signal because TSSs on - strand are calculated from the wrong direction.

**Symptom:** TSS profile is flat or shows a slight dip at TSS center. Genome browser shows accessibility everywhere, not concentrated at promoters.

**Fix:** Verify genome build (mm10 vs mm39 differ in TSS positions); verify GTF strand column; confirm signal track was generated post-deduplication. If TSS profile is genuinely flat, library is over-transposed and not recoverable; lower transposition time / Tn5 concentration in next prep.

### FRiP < 0.2

**Trigger:** Signal too diffuse to call peaks (over-transposition), low TSS enrichment, OR peak set is too narrow / restrictive.

**Mechanism:** FRiP correlates with TSS enrichment because both measure how concentrated the signal is. A diffuse library will have low FRiP regardless of peak count.

**Symptom:** Peak count looks normal but FRiP < 0.15.

**Fix:** Check TSS enrichment first. If TSS is also low, the library is over-transposed. If TSS is OK but FRiP is low, the peak caller may be undercalling -- try `-p 0.01` (looser) and recalculate FRiP.

### Replicate correlation < 0.85

**Trigger:** Batch effect, technical artefact, or cell-state drift between replicate biological collections.

**Mechanism:** Pearson correlation on log-scaled binned counts (deepTools `multiBamSummary bins -bs 10000`) tracks coverage similarity. Below 0.85 indicates non-trivial divergence; ENCODE wants >= 0.9 for biological reps.

**Fix:** Check PCA; if reps cluster apart from condition, drop the outlier or rerun. If the divergence aligns with batch, add batch as a covariate downstream (DiffBind `~Batch + Condition`). Do not silently merge with bad correlation.

## Library Complexity (NRF, PBC1, PBC2)

**Goal:** Detect over-amplification or low-input bottlenecks.

**Approach:** Hash mapped read positions (or fragment 5' coordinates), tally how many positions have 1, 2, or more reads, and compute the three metrics.

```python
import pysam
from collections import Counter

def library_complexity(bam):
    pos_counts = Counter()
    total = 0
    with pysam.AlignmentFile(bam, 'rb') as bf:
        for r in bf.fetch():
            if r.is_unmapped or r.is_secondary or r.is_supplementary:
                continue
            if r.is_duplicate:                          # Mark, not skip; PBC counts pre-dedup
                pass
            total += 1
            key = (r.reference_name, r.reference_start, r.is_reverse)
            pos_counts[key] += 1
    distinct = len(pos_counts)
    histogram = Counter(pos_counts.values())            # {1: N1, 2: N2, ...}
    n1 = histogram.get(1, 0)
    n2 = histogram.get(2, 0)
    nrf = distinct / total if total else 0.0
    pbc1 = n1 / distinct if distinct else 0.0
    pbc2 = n1 / n2 if n2 else float('inf')
    return {'NRF': nrf, 'PBC1': pbc1, 'PBC2': pbc2, 'total': total, 'distinct': distinct}
```

`r.is_duplicate` is informational only here; ENCODE NRF/PBC are computed pre-deduplication on the raw mapped BAM.

## Cross-Replicate QC

```bash
# Spearman correlation (more robust than Pearson for ATAC)
multiBamSummary bins -bs 10000 -p 8 \
    --bamfiles rep1.bam rep2.bam rep3.bam \
    -o multi.npz

plotCorrelation -in multi.npz \
    --corMethod spearman --whatToPlot heatmap --skipZeros \
    -o spearman_heatmap.png

# Fingerprint (per-bin signal cumulative -- diagonal = no enrichment, sharp curve = good)
plotFingerprint -p 8 -b rep1.bam rep2.bam rep3.bam \
    --labels rep1 rep2 rep3 \
    --skipZeros --numberOfSamples 50000 \
    -o fingerprint.png \
    --outQualityMetrics fingerprint_metrics.txt
```

deepTools fingerprint quality metrics report a synthetic JS distance without a reference; the (non-synthetic) Jensen-Shannon distance column is only computed when a reference sample is supplied via `--JSDsample`. Larger values indicate stronger enrichment.

## Library Complexity Extrapolation (preseq)

**Goal:** Predict whether re-sequencing would rescue a low-NRF library, separating "library is bottlenecked" from "we just sequenced too shallow."

**Approach:** Fit preseq's rational-function (Pade) approximation of the Good-Toulmin power-series estimator on observed BAM read positions; extrapolate distinct-fragment yield as a function of additional sequencing depth.

```bash
# c_curve: observed complexity at current depth
preseq c_curve -B sample.bam -o sample.ccurve.tsv -s 1e6

# lc_extrap: predicted complexity at higher depth (extrapolation -e here 200M; preseq default -e is 1e10, step -s default 1M)
preseq lc_extrap -B sample.bam -o sample.lcextrap.tsv -e 200000000 -s 5000000
```

Interpretation: if `lc_extrap` shows distinct-fragment count flattening before 100M reads, the library is bottlenecked (re-sequencing won't help; re-prep needed). If it continues to climb, re-sequencing will recover more unique reads. Use alongside NRF/PBC1/PBC2 to decide library re-prep vs deeper sequencing.

## Sex-Chromosome QC

**Trigger:** Clinical-grade ATAC; biobank-scale studies; sample-mix-up detection.

**Mechanism:** chrY has minimal coverage in female samples; XIST locus (chrX) is highly accessible only in female cells (X-inactivation). Sample-swap or sex-misassignment detectable from these two loci.

```bash
# chrY read fraction
samtools idxstats sample.bam | awk '$1=="chrY"{print $3 / $2}'   # reads per bp

# XIST locus accessibility (chrX:73820651-73852753 in hg38)
samtools view -c sample.bam chrX:73820651-73852753
```

Female: chrY reads/bp ~0; XIST count high. Male: chrY reads/bp ~male coverage; XIST count low. Discrepancy with sample metadata flags swap.

## Cell-Cycle Effect on Accessibility

**Trigger:** Proliferating cell lines (K562, HEK293, HeLa); samples with high S/G2M signature.

**Mechanism:** Replication-associated chromatin opening adds 5-15% global accessibility shift in proliferating cells; without correction, condition-specific cell-cycle differences confound differential analysis.

**Detection:** Score cells/samples for S-phase signature (Macosko 2015 cell cycle gene set adapted for chromatin: regulated origin loci, replication-stress-response genes); for bulk ATAC, compute per-sample peak intersection with replication-origin atlas (Repli-seq peaks).

**Fix for differential:** Add S-phase score as covariate in DESeq2 design (`~Sphase + Condition`); for scATAC, regress on TF-IDF residuals analogous to Seurat CellCycleScoring.

## Spike-in QC (Drosophila or E. coli Chromatin)

**Trigger:** Studies where global accessibility shift is biological (HDAC inhibitor, DNMT inhibitor, differentiation).

**Mechanism:** Per-library normalization (RPM, CPM) erases global accessibility shifts because total reads are nominally constant. Exogenous chromatin spike-in (Drosophila S2 or E. coli Tn5-naive chromatin added pre-Tn5) provides an external scaling reference.

**Pipeline:** Align reads to a concatenated human + Drosophila reference; count spike-in reads per sample; normalize by spike-in (not by total reads). Reske 2020 Epigenetics Chromatin shows that normalization-method choice materially changes differential-accessibility results when a global accessibility shift is expected (ARID1A/PIK3CA endometrial-epithelium case study), motivating an external reference such as a chromatin spike-in.

**QC threshold:** spike-in fraction 0.5-5% of total reads is the workable range. Below 0.1% spike-in is unreliable; above 10% suggests too much spike-in (loss of cellular reads).

## Comprehensive QC Aggregation

**Goal:** Produce a per-sample report card with PASS/FAIL flags against ENCODE thresholds.

**Approach:** Compute each metric independently, compare to thresholds, write a tab-delimited report consumable by MultiQC.

```python
import json, subprocess, sys
from pathlib import Path

ENCODE_THRESHOLDS = {
    'nuclear_reads_M': (25, 50),                      # (min acceptable, ideal)
    'mt_fraction': (0.5, 0.05),                       # (max acceptable, ideal); inverted
    'NRF': (0.7, 0.9), 'PBC1': (0.7, 0.9), 'PBC2': (1.0, 3.0),
    'TSS_enrichment': (5.0, 7.0), 'FRiP': (0.2, 0.3),
}

def grade(value, thr_acceptable, thr_ideal, inverted=False):
    if inverted:
        return 'FAIL' if value > thr_acceptable else ('PASS' if value <= thr_ideal else 'WARN')
    return 'FAIL' if value < thr_acceptable else ('PASS' if value >= thr_ideal else 'WARN')

def report(metrics, out_tsv):
    rows = []
    for k, (acc, ideal) in ENCODE_THRESHOLDS.items():
        if k not in metrics: continue
        inverted = (k == 'mt_fraction')
        flag = grade(metrics[k], acc, ideal, inverted=inverted)
        rows.append((k, metrics[k], acc, ideal, flag))
    with open(out_tsv, 'w') as f:
        f.write('metric\tvalue\tacceptable\tideal\tflag\n')
        for r in rows: f.write('\t'.join(map(str, r)) + '\n')
```

## MultiQC Aggregation

```bash
# Run after generating per-sample QC outputs
multiqc \
    fastqc/ \
    picard/ \
    samtools_stats/ \
    macs2/ \
    deeptools/ \
    -o multiqc_report
```

MultiQC ingests Picard CollectInsertSizeMetrics, samtools flagstat, deepTools plotFingerprint output, and MACS peaks tables. It does NOT compute TSS enrichment or NRF; pipe a custom `_mqc.tsv` for those.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| TSS enrichment off by 3x from expected | Wrong implementation (ENCODE vs ATACseqQC) | State the formula; convert by recomputing |
| NRF = 1.0 exactly | BAM was already deduplicated -> all positions distinct | Compute NRF on raw mapped BAM (pre-dedup) |
| PBC2 = inf | No positions with 2 reads | Library is too sparse; PBC2 unreliable below ~5M reads |
| Mt fraction reported but BAM has no `chrM` | Mitochondrial chromosome named `MT`, `Mt`, or `chromosome:MT` | Match `samtools idxstats` chromosome name to the filter |
| Insert size distribution flat after Picard | Sample is single-end | Insert size only valid for paired-end; switch to deeptools fragmentSize |
| Replicates correlate poorly but PCA looks fine | High background dominates correlation | Use `--skipZeros`; or compute correlation on peak counts only |
| FRiP differs by 2x between identical pipeline runs | Peak set differs (q-value cutoff drift) | Pin caller version + cutoff; FRiP is peak-set-dependent |
| TSS enrichment lower than expected on Omni-ATAC | Used standard TSS BED on FFPE-prepped sample | FFPE TSSs are degraded; use peak-based metric instead |

## References

- Buenrostro JD et al 2013 Nat Methods 10:1213 (ATAC-seq protocol; fragment-size periodicity)
- Corces MR et al 2017 Nat Methods 14:959 (Omni-ATAC; mt fraction reduction protocol)
- Landt SG et al 2012 Genome Res 22:1813 (ENCODE/modENCODE QC framework, NRF/PBC definitions; the PBC1/PBC2 split is a later ENCODE-pipeline refinement)
- ENCODE 4 ATAC-seq Data Standards (encodeproject.org/atac-seq) -- canonical thresholds
- Ou J et al 2018 BMC Genomics 19:169 (ATACseqQC R package; TSSEscore implementation)
- Ramirez F et al 2016 Nucleic Acids Res 44:W160 (deepTools, plotFingerprint JSD)
- Daley T & Smith AD 2013 Nat Methods 10:325 (preseq library-complexity extrapolation model; the lc_extrap re-sequencing decision)

## Related Skills

- atac-seq/atac-peak-calling - FRiP requires peaks; QC drives accept/reject before calling
- atac-seq/nucleosome-positioning - Fragment-size analysis
- atac-seq/single-cell-atac - per-cell QC has different thresholds
- read-qc/quality-reports - upstream FastQC
- alignment-files/bam-statistics - samtools flagstat / idxstats
- alignment-files/duplicate-handling - dedup before NRF/PBC computation
<!-- END FILE: atac-seq/atac-qc/SKILL.md -->

## 子目录：atac-seq/co-accessibility

<!-- BEGIN FILE: atac-seq/co-accessibility/SKILL.md -->
---
name: bio-atac-seq-co-accessibility
description: Infer cis-regulatory connections (peak-to-peak co-accessibility) from scATAC-seq using Cicero, ArchR getCoAccessibility, or SCENIC+. Use when linking enhancer accessibility to promoter accessibility, identifying enhancer-gene pairs from chromatin alone (without paired RNA), running gene-regulatory inference combining ATAC + RNA, or comparing predicted regulatory contacts against Hi-C/Micro-C ground truth.
tool_type: r
primary_tool: cicero
---

## Version Compatibility

Reference examples tested with: Cicero 1.20+, monocle3 1.3+, ArchR 1.0.2+, SCENIC+ 1.0+, pycisTopic 1.0+, Signac 1.13+, GenomicRanges 1.54+, GenomicInteractions 1.36+, BSgenome.Hsapiens.UCSC.hg38 1.4+.

Verify before use:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws unexpected errors, introspect the installed package and adapt rather than retrying.

# Co-accessibility (cis-Regulatory Linkage)

**"Which enhancers connect to which promoters in my scATAC data?"** -> Use cell-to-cell variability in joint accessibility of nearby peaks to infer cis-regulatory connections without explicit RNA expression. Output is a peak-pair graph with co-accessibility scores; thresholding produces enhancer-gene candidate pairs.

- R: `cicero::run_cicero(input_cds, genomic_coords)` -> peak-pair connection scores
- R: `ArchR::addCoAccessibility(proj)` -> ArchR-internal Cicero wrapper
- Python: `pycisTopic` + `SCENIC+` for network-level inference combining ATAC + RNA + motifs

Co-accessibility is NOT 3D contact; it's a statistical association based on cell-to-cell co-variation. Strong co-accessibility correlates with Hi-C/Micro-C contacts (~30-50% concordance) but is not equivalent.

## What Co-accessibility Captures vs What It Doesn't

| Captures | Misses |
|----------|--------|
| Peak pairs that vary together across cell states | 3D physical contacts that don't vary in accessibility |
| Cis-regulatory grammar within a cell type | Trans-chromosomal interactions |
| Active enhancer-promoter pairs | Constitutive structural contacts |
| Lineage-specific regulation | Developmental contacts that opened before scATAC sample |
| Distance-decay biology of enhancer-promoter | Hub enhancers that contact many distal targets |

For physical contact, use Hi-C, Micro-C, or PCHi-C. Co-accessibility is the chromatin-only proxy.

## Algorithmic Taxonomy

| Tool | Method | Input | Output | Strength | Fails when |
|------|--------|-------|--------|----------|------------|
| Cicero (Pliner 2018) | Graphical lasso on aggregated cell metacells | scATAC peak-cell matrix + cell trajectory | Peak-pair connection score (0-1) | Original, well-validated; integrates with Monocle3 | Slow on >50K cells; sensitive to alpha tuning |
| ArchR getCoAccessibility | Cicero-based; uses ArchR's metacell aggregation | ArchR project | Same as Cicero | Built-in to ArchR pipeline; faster on large datasets | Tied to ArchR; same biology as Cicero |
| SCENIC+ (Bravo 2023) | Multi-step: co-accessibility + motif scoring + RNA correlation | Multiome (ATAC + RNA) or paired | TF-driven enhancer-gene networks | Most comprehensive; multi-modal | Multiome data required; computationally heavy |
| LinkPeaks (Signac) | Pearson correlation of accessibility with paired gene expression | Multiome | Peak-gene linkage score | Direct enhancer-gene from RNA correlation | Multiome-only; not pure ATAC |
| GeneHancer / FANTOM5 / EpiMap | Bulk-derived enhancer-gene reference | None (database lookup) | Pre-computed enhancer-gene pairs | Comprehensive; published references | Cell-type-agnostic; may not match the biology of interest |

Methodology evolves; verify against Pliner 2018 (Cicero), Bravo 2023 (SCENIC+), Nasser 2021 (ABC model alternative for enhancer-gene), and current Hi-C concordance benchmarks.

## How Cicero Works (Conceptually)

Cell-to-cell variability is too sparse for direct correlation. Cicero solves this via metacells:

1. Reduce dimensionality (UMAP from input).
2. Build k-NN graph of cells.
3. Aggregate k cells into metacells (default k = 50).
4. Compute correlation in accessibility across metacells, restricted to peak pairs within `genomic_distance_max` (default 500 kb cis).
5. Apply graphical lasso with regularization `alpha` to sparsify the correlation matrix.
6. Output: per-pair connection score; positive = co-variation, negative = anti-co-variation.

Connection thresholds typically 0.05-0.5; > 0.25 is high-confidence.

## Per-Tool Failure Modes

### Cicero -- alpha tuning shifts results

**Trigger:** Default alpha (sometimes computed automatically from data); custom alpha < 0.5 or > 5.

**Mechanism:** Alpha controls graphical lasso regularization. Too low: dense graph with many spurious connections; too high: sparse with biology missing.

**Symptom:** Connection count varies 10-100x across alpha sweeps.

**Fix:** Use Cicero's `estimate_distance_parameter()` to get data-driven alpha; verify connection count is biologically plausible (~10-50% of peaks have at least one strong connection).

### Cicero -- metacell aggregation hides cell-type-specific connections

**Trigger:** Running Cicero on heterogeneous dataset spanning multiple cell types.

**Mechanism:** Metacells aggregate across cell types; connections that exist only in one cell type get diluted.

**Fix:** Run Cicero per-cluster separately; combine results with cluster annotations. Cell-type-specific connections often differ.

### Cicero -- distance assumption

**Trigger:** Default `genomic_distance_max=500000` (500 kb cis only).

**Mechanism:** Distal connections beyond 500 kb cis are excluded; trans-chromosomal entirely missed.

**Fix:** For specific use cases (e.g., gene desertless TADs), increase `genomic_distance_max` to 1 Mb or more. Trans connections require Hi-C, not co-accessibility.

### SCENIC+ -- RNA scaling

**Trigger:** RNA-side dropouts in Multiome data.

**Mechanism:** SCENIC+ requires reasonable RNA quantification per cell. Sparse Multiome RNA with many zero genes causes correlation degradation.

**Fix:** Filter cells with insufficient RNA; aggregate cells if necessary. Multiome RNA should look comparable to standalone scRNA-seq.

### LinkPeaks (Signac) -- Distance default

**Trigger:** Default `LinkPeaks(..., distance=5e+05)`.

**Mechanism:** Same as Cicero; 500 kb cis only by default.

**Fix:** Same; widen if needed but trans not supported.

## Decision Tree by Goal

| Goal | Tool |
|------|------|
| ATAC-only enhancer-promoter inference | Cicero |
| ATAC-only inside ArchR ecosystem | ArchR getCoAccessibility |
| Multiome (RNA + ATAC) enhancer-gene inference | LinkPeaks (Signac) for direct correlation; SCENIC+ for TF network |
| TF-driven regulatory networks | SCENIC+ (requires Multiome) |
| Comparison against Hi-C / Micro-C | Cicero output -> overlap with HiCCUPS loops |
| Published reference enhancer-gene pairs | GeneHancer, FANTOM5, EpiMap (pre-computed lookup) |
| Gene desertless distal regulation | Cicero with widened distance; or H3K27ac HiChIP |

## Cicero Standard Workflow

**Goal:** Infer cis-regulatory peak-peak connections from a scATAC peak-cell matrix.

**Approach:** Build a Monocle3 CellDataSet, reduce dimensions via LSI + UMAP, aggregate cells into metacells, then run Cicero's graphical-lasso correlation across the cis window and threshold on connection score.

```r
library(cicero); library(monocle3); library(GenomicRanges)

# Input: peak-cell binary matrix from Signac/ArchR (rows = peaks, cols = cells)
# Convert peaks to "chrN_start_end" format
peak_names <- paste0(seqnames(peaks), '_', start(peaks), '_', end(peaks))
input_cds <- new_cell_data_set(peak_matrix, cell_metadata=metadata,
                               gene_metadata=peak_metadata)

# Reduce dimensionality (UMAP from input)
input_cds <- detect_genes(input_cds)
input_cds <- estimate_size_factors(input_cds)
input_cds <- preprocess_cds(input_cds, method='LSI')
input_cds <- reduce_dimension(input_cds, reduction_method='UMAP',
                              preprocess_method='LSI')

# Build metacell-aggregated CDS
umap_coords <- reducedDims(input_cds)$UMAP
cicero_cds <- make_cicero_cds(input_cds, reduced_coordinates=umap_coords, k=50)

# Run Cicero with hg38 chrom sizes
genome_df <- data.frame(chr=seqnames(seqinfo(BSgenome.Hsapiens.UCSC.hg38)),
                        length=seqlengths(seqinfo(BSgenome.Hsapiens.UCSC.hg38)))
conns <- run_cicero(cicero_cds, genomic_coords=genome_df,
                    window=500000, sample_num=100)

# Filter to high-confidence connections.
# Threshold 0.25 is a Cicero-documentation working default; the optimal cutoff
# is dataset-dependent and is best calibrated against orthogonal Hi-C / HiChIP.
strong <- conns[conns$coaccess > 0.25, ]
cat(sprintf('Total conns: %d; strong (>0.25): %d\n', nrow(conns), nrow(strong)))
```

## ArchR getCoAccessibility

```r
library(ArchR)
proj <- loadArchRProject('ArchR_out')
proj <- addCoAccessibility(proj, reducedDims='IterativeLSI',
                          k=100, knnIteration=500,
                          maxDist=250000)               # 250 kb cis (wider than the 100 kb default)
co_acc <- getCoAccessibility(proj, corCutOff=0.5,       # Default 0.5 in ArchR; lower for more (calibrate against Hi-C/HiChIP)
                             returnLoops=TRUE)           # TRUE (default) -> GRanges loops object; FALSE -> DataFrame of peak-pair correlations
```

With `returnLoops=TRUE` (the default) ArchR returns the connections as a GRanges loops object compatible with `GenomicInteractions` for direct overlap with Hi-C loops; `returnLoops=FALSE` instead returns a DataFrame of peak-pair correlations.

## Visualizing Connections

```r
# As arc plot at a locus of interest
library(Gviz); library(GenomicInteractions)
# Cicero Peak1/Peak2 are chr_start_end strings; convert to chr:start-end for GRanges()
gi <- GenomicInteractions(anchor1=GRanges(sub('_(\\d+)_(\\d+)$', ':\\1-\\2', strong$Peak1)),
                          anchor2=GRanges(sub('_(\\d+)_(\\d+)$', ':\\1-\\2', strong$Peak2)),
                          counts=as.integer(strong$coaccess * 100))
track <- InteractionTrack(gi, name='co-accessibility')
plotTracks(track)
```

For genome-browser visualization with ArchR: `plotPeak2GeneHeatmap()` shows the peak-gene linkage matrix; `plotBrowserTrack()` overlays connections on tracks.

## SCENIC+ TF-Driven Networks

SCENIC+ 1.0 runs as a Snakemake pipeline (CLI), not a single monolithic Python call. Prepare the inputs first (a pycisTopic cisTopic object, motif-enrichment results, and paired RNA AnnData), then scaffold and run the workflow:

```bash
# Scaffold the pipeline, then edit its config.yaml to point at the cisTopic object,
# motif-enrichment results, and GEX AnnData
scenicplus init_snakemake --out_dir scplus_pipeline/
snakemake --cores 16 --snakefile scplus_pipeline/Snakemake/workflow/Snakefile
# eRegulons (TF + target genes + linked enhancers) are written to the output MuData (scplusmdata.h5mu)
```

SCENIC+ is significantly more complex than Cicero; budget 1-2 days for setup. The benefit is that outputs are TF -> enhancer -> gene triples, not just peak-peak co-accessibility.

## Cicero Alpha Mathematics

**Trigger:** Tuning Cicero's regularization parameter for the graphical lasso step.

**Mechanism:** `estimate_distance_parameter()` searches for the smallest distance-penalty scaling (Cicero's `distance_parameter`, called "alpha" here) such that, across random genomic windows, no more than ~5% of peak pairs beyond `distance_constraint` retain non-zero graphical-lasso entries and fewer than 80% of all entries are non-zero. This penalizes long-range co-accessibility so the graph sparsifies at biologically appropriate distance scales -- it is not a correlation-vs-distance regression slope.

**Implementation:** Cicero calls `estimate_distance_parameter(cicero_cds, window=window, maxit=100, sample_num=100, genomic_coords=genome_df)` over `sample_num` random windows and returns one `distance_parameter` per window; take the mean and pass it to `generate_cicero_models(cicero_cds, distance_parameter=mean(...))`. Supply `genomic_coords` explicitly -- its default is `cicero::human.hg19.genome`, wrong for an hg38 analysis.

**When manual tuning helps:** Very dense peaksets (>200k peaks) may need a higher `distance_parameter` to control false positives; very sparse (<10k peaks) may need a lower one to recover signal. Verify by running on a permutation / cell-label-shuffle negative control -- the expected outcome is ~0 strong connections (technical replicates should instead reproduce connections).

## ABC Model Cross-Reference

For enhancer-to-gene linking with paired Hi-C/Micro-C, the canonical method is the ABC model (Fulco 2019, Nasser 2021), not Cicero. ABC computes ABC = (Activity_E * Contact_E,G) / sum_e(Activity_e * Contact_e,G); standardizes on combined ATAC + H3K27ac activity and Hi-C contact frequencies. ENCODE-rE2G (Gschwind et al 2023, bioRxiv) is the modern logistic-regression enhancer-gene link predictor.

See atac-seq/enhancer-gene-linking for full ABC and ENCODE-rE2G coverage. Cicero is the ATAC-only fallback when no Hi-C is available.

## HiChIP H3K27ac as Orthogonal Anchor

| Decision | Action |
|----------|--------|
| Have Hi-C / Micro-C | Use ABC (atac-seq/enhancer-gene-linking) primary; Cicero as ATAC-only sanity check |
| Have HiChIP H3K27ac | FitHiChIP loops (FDR < 0.05, count >= 5) primary; ABC + HiChIP intersection is high-confidence |
| Have ATAC + H3K27ac, no 3D | ABC with average HiC fallback (Fulco 2019); document degraded performance |
| Have only ATAC | Cicero (this skill); known concordance with Hi-C ~30-50% |

Cicero is appropriate when no 3D data exists; do not use Cicero in lieu of ABC when Hi-C/Micro-C are available.

## Hi-C / Micro-C Concordance

| Hi-C concordance | Action |
|-----------------|--------|
| > 50% of strong Cicero connections overlap Hi-C loops | High-confidence; Cicero captures real 3D structure |
| 30-50% | Standard; some 3D contacts don't vary in accessibility |
| < 20% | Co-accessibility may not reflect contacts; lineage-specific contacts may be missing |

**Goal:** Quantify what fraction of strong Cicero connections are supported by Hi-C loop calls.

**Approach:** Import HiCCUPS loops as GenomicInteractions, build a parallel object from Cicero connections, then count anchor-anchor overlaps and report the percentage.

```r
# Compare Cicero against published Hi-C loops
library(GenomicInteractions)
hic_loops <- makeGenomicInteractionsFromFile('hiccups_loops.bedpe', type='bedpe',
                                             experiment_name='hiccups', description='HiCCUPS loops')
ci <- GenomicInteractions(anchor1=GRanges(sub('_(\\d+)_(\\d+)$', ':\\1-\\2', strong$Peak1)),
                          anchor2=GRanges(sub('_(\\d+)_(\\d+)$', ':\\1-\\2', strong$Peak2)))
overlap <- countOverlaps(ci, hic_loops) > 0   # anchor-anchor 'any' overlap; 'equal' is too stringent at loop bin resolution
cat(sprintf('Cicero connections overlapping HiCCUPS loops: %.1f%%\n',
            100 * mean(overlap)))
```

## Reconciliation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Cicero many weak connections; ArchR few strong | Different alpha or aggregation | Standardize parameters |
| LinkPeaks (Multiome) finds connections Cicero misses | LinkPeaks uses RNA expression as the anchor; Cicero is ATAC-only | Both valid; report intersection as high-confidence |
| Co-accessibility doesn't match Hi-C in heterochromatin | Heterochromatic contacts are constitutive; co-accessibility needs variation | Expected; co-accessibility complements Hi-C |
| SCENIC+ network has ENCODE-validated TFs but missing some | Motif database limited or RNA imputation missed | Expand motif database; integrate paired ChIP-seq if available |

**Operational rule:** Co-accessibility is a hypothesis generator. Validate with Hi-C, ChIP-seq, or experimental enhancer-promoter interaction (CRISPRi-FlowFISH).

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Cicero `make_cicero_cds` slow / crashes | k too high or cell count too large | Reduce k or subsample cells |
| All connections near zero | alpha set too high | Use `estimate_distance_parameter()` |
| Connection score > 1 reported | Bug in older Cicero versions | Update; check `as.numeric(coaccess)` for outliers |
| ArchR getCoAccessibility "TileMatrix" error | Need PeakMatrix not TileMatrix | `addPeakMatrix()` first |
| SCENIC+ install fails | Many heavy dependencies | Use the published Docker image |
| Connection count varies wildly per run | Stochastic metacell aggregation | Set seed; or aggregate at higher k for stability |
| LinkPeaks all NaN | RNA expression has too many zeros | Re-filter cells with sufficient RNA |
| Peak names not matching | format mismatch (chr_start_end vs chr:start-end) | Standardize naming convention |

## References

- Pliner HA et al 2018 Mol Cell 71:858 (Cicero)
- Granja JM et al 2021 Nat Genet 53:403 (ArchR getCoAccessibility)
- Bravo Gonzalez-Blas C et al 2023 Nat Methods 20:1355 (SCENIC+)
- Stuart T et al 2021 Nat Methods 18:1333 (Signac LinkPeaks)
- Nasser J et al 2021 Nature 593:238 (ABC model; alternative enhancer-gene)
- Fulco CP et al 2019 Nat Genet 51:1664 (CRISPRi-FlowFISH; gold-standard validation)
- Mumbach MR et al 2017 Nat Genet 49:1602 (HiChIP H3K27ac for enhancer-promoter)
- Boix CA et al 2021 Nature 590:300 (EpiMap; bulk enhancer-gene reference)

## Related Skills

- atac-seq/single-cell-atac - scATAC preprocessing (input)
- atac-seq/consensus-peakset - Peak set used for connection inference
- atac-seq/motif-deviation - chromVAR for TF activity (complement)
- atac-seq/enhancer-gene-linking - ABC, ENCODE-rE2G, CRISPRi-FlowFISH validation when Hi-C is available
- atac-seq/deep-learning-atac - chromBPNet variant effect at predicted enhancers
- gene-regulatory-networks/scenic-regulons - Standalone SCENIC for TF networks
- hi-c-analysis/loop-calling - Physical contacts from Hi-C
- hi-c-analysis/contact-pairs - Hi-C / Micro-C contact pairs
- single-cell/multimodal-integration - Multiome integration
- chip-seq/peak-annotation - Cross-validate with TF ChIP
- pathway-analysis/gsea - Downstream gene-level enrichment
<!-- END FILE: atac-seq/co-accessibility/SKILL.md -->

## 子目录：atac-seq/consensus-peakset

<!-- BEGIN FILE: atac-seq/consensus-peakset/SKILL.md -->
---
name: bio-atac-seq-consensus-peakset
description: Build a differential-ready consensus peakset from per-replicate ATAC-seq peaks using iterative overlap removal, fixed-width re-centering, and majority-rule overlap. Use when generating a stable peak coordinate system for downstream differential accessibility, ML feature engineering, cross-sample comparison, or fixed-width peak counts; covers Corces 2018 iterative overlap (501 bp), DiffBind summit re-centering, and ENCODE consistency rules.
tool_type: mixed
primary_tool: bedtools
---

## Version Compatibility

Reference examples tested with: bedtools 2.31+, samtools 1.19+, BEDOPS 2.4.41+, GenomicRanges 1.54+, DiffBind 3.12+, Subread 2.0.2+ (featureCounts; `--countReadPairs` requires >= 2.0.2), pybedtools 0.10+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed package and adapt rather than retrying.

# Consensus Peakset Construction

**"Build a single peakset to count reads against for all my samples"** -> Combine per-replicate or per-condition peak calls into a non-redundant, fixed-width set of regions. The strategy chosen drives FDR calibration, peak-width fairness, and reproducibility downstream.

- CLI: `bedtools merge` (simple union) and `bedtools multiinter` (per-sample membership columns emitted by default)
- CLI: Corces 2018 iterative overlap removal (custom shell)
- R: `DiffBind::dba.count(summits=250)` (built-in fixed-width)
- Python: `pybedtools` for programmatic merging

The peakset choice is rarely default-correct. Wrong width or wrong overlap rule propagates to every downstream analysis (differential, motif, footprint, ML).

## Why a Consensus Peakset Matters

ATAC peaks vary in width across replicates: same regulatory element might be called 200 bp in rep1 and 800 bp in rep2 because of stochastic Tn5 cuts at edges. Counting reads in different-width intervals confounds peak width with biological signal. A fixed-width consensus avoids this.

For ENCODE-style differential analysis: ALL samples must be counted against the SAME peak coordinates; otherwise the count matrix is non-rectangular and statistical models are misspecified.

## Strategy Taxonomy

| Strategy | Implementation | Width | When to use | Fails when |
|----------|---------------|-------|-------------|------------|
| Naive union | `bedtools merge` of all peaks | Variable, tends wide | Quick exploratory; never for differential | Width inflation drives spurious differential |
| Naive intersection | `bedtools multiinter` requiring all samples | Variable | High-stringency reproducibility | Loses real condition-specific peaks |
| Majority-rule overlap | `multiinter` requiring >= n/2 samples | Variable | Balance; DiffBind default with `minOverlap` | Width still varies; counts are width-biased |
| Iterative overlap removal (Corces 2018) | Sort by significance, greedily keep non-overlapping at fixed width | 501 bp fixed | ML features; cross-study comparison; modern ATAC standard | Loses sub-501bp resolution; overweights high-significance peaks |
| Summit-centered fixed width (DiffBind) | `dba.count(summits=250)` re-centers all peaks on summit +/- 250 bp | 501 bp fixed | Matches the Corces 501 bp convention (note: `dba.count` default is `summits=200` -> 401 bp); integrates with replicate counts | Requires summit info (MACS narrowPeak); broad peaks lose width info |
| IDR-filtered union | Union of IDR-passed peaks across rep pairs | Variable | ENCODE pipeline-compliant; reproducibility-aware | Requires running IDR per pair; computationally heavier |
| Per-condition union, then global union | Each group consensus separately, then merge | Variable | Different cell types / strong condition shift | Same width issues as naive union |
| Width-controlled extension | Extend each peak to median width centered on midpoint | User-set | Quick fixed-width without summit info | Midpoint != summit; can shift biology |

Methodology evolves; verify against current ENCODE 4 ATAC standards (encodeproject.org/atac-seq) and the Corces 2018 iterative overlap algorithm before locking pipelines.

## Iterative Overlap Removal (Corces 2018)

This is the modern standard for fixed-width consensus peaksets used in cross-study comparison and machine-learning feature matrices.

**Algorithm:**
1. Pool all peaks from all samples; re-center each on its summit; extend +/- 250 bp -> 501 bp fixed-width peaks.
2. Sort by significance (narrowPeak column 7, signalValue, descending).
3. Walk down the sorted list. Keep each peak if it does not overlap any previously kept peak. Drop if overlap.
4. Output the kept peaks as the consensus.

**Goal:** Produce a non-overlapping, fixed-width peakset weighted toward strongest evidence.

**Approach:** Greedy non-overlap on summit-centered fixed-width peaks ranked by signalValue.

```bash
#!/bin/bash
# Corces 2018 iterative overlap removal
PEAKS_DIR=peaks/per_sample
GENOME_SIZES=hg38.chrom.sizes
WIDTH_HALF=250                                       # 501 bp total width

# 1. Pool all peaks, re-center on summit, extend
awk -v w=$WIDTH_HALF 'BEGIN{OFS="\t"}
    {summit=$2+$10; print $1, summit-w, summit+w+1, $4, $7, $6}' \
    $PEAKS_DIR/*.narrowPeak | \
    awk '$2 >= 0' | \
    bedtools slop -i - -g $GENOME_SIZES -b 0 | \
    sort -k1,1 -k2,2n > pooled_recentered.bed

# 2. Sort by signalValue descending (column 5 in our BED -- which was column 7 of narrowPeak)
sort -k5,5gr pooled_recentered.bed > pooled_by_sig.bed

# 3. Iterative greedy non-overlap (process in significance order)
python3 - <<'EOF'
import sys
kept = []
with open('pooled_by_sig.bed') as f:
    for line in f:
        chrom, start, end, name, sig, strand = line.strip().split('\t')[:6]
        start, end = int(start), int(end)
        overlap = any(c == chrom and not (end <= s or start >= e) for c, s, e in kept)
        if not overlap:
            kept.append((chrom, start, end))

with open('consensus_iterative.bed', 'w') as f:
    for c, s, e in sorted(kept):
        f.write(f'{c}\t{s}\t{e}\n')
EOF

sort -k1,1 -k2,2n consensus_iterative.bed > consensus_final.bed
echo "Consensus peakset: $(wc -l < consensus_final.bed) fixed-width 501bp peaks"
```

For a faster approximation at scale, `bedtools cluster` + per-cluster top-significance selection is tempting, but it is NOT equivalent to greedy iterative overlap: `cluster` groups transitively-overlapping peaks (a chain can span well beyond 501 bp), so keeping one peak per cluster discards non-overlapping peaks the greedy algorithm would retain. Use it only as an approximation.

## Per-Strategy Failure Modes

### Naive union -- Width-driven differential

**Trigger:** Using `bedtools merge` of all per-rep peaks; counting reads in merged intervals.

**Mechanism:** A peak appearing as 200 bp in one rep but 800 bp in another merges to 800 bp in the union. Read count in 800 bp interval is biased high; differential analysis flags it as condition-specific even when it's just width difference.

**Symptom:** Top differential peaks track peak width (mean width different by 100+ bp between conditions).

**Fix:** Use fixed-width strategy (Corces iterative or DiffBind `summits=250`). Never use merged variable-width peaks for differential.

### Intersection (peak in all reps) -- Loses condition-specific biology

**Trigger:** Using `bedtools multiinter -i ...` (which emits per-sample membership columns by default) and requiring all samples.

**Mechanism:** Peaks present only in one condition fail intersection requirement and are excluded from the consensus, even though they are the biology of interest.

**Symptom:** Differential analysis returns near-zero significant peaks; the condition-specific peaks were filtered out before testing.

**Fix:** Use per-condition consensus, then union of consensus. Or majority rule with per-condition minOverlap.

### Majority rule (DiffBind default-ish) -- Borderline peaks dropped

**Trigger:** `dba.count(minOverlap=ceiling(N/2))` where N = total replicates and one condition has fewer reps.

**Mechanism:** A peak in 2/2 reps of cond1 but 0/3 reps of cond2 is in 2/5 = 40% < 50% -> dropped.

**Fix:** Compute consensus per condition first (e.g. peak in >= 2/3 reps), then union across conditions. This preserves condition-specific peaks.

### Width-controlled extension -- Shifts off summit

**Trigger:** Extending peak to fixed width using midpoint (`(start+end)/2`).

**Mechanism:** Midpoint of the called peak is rarely at the actual summit; particularly for asymmetric peaks (TSS-flanking) or wide broadPeaks.

**Fix:** Use summit position from narrowPeak column 10 (`start + summit_offset`). If summit unavailable (broadPeak), use peak start + half median width as approximation.

### IDR-filtered union -- Computational cost; threshold mismatch

**Trigger:** Running IDR for each rep pair, then unioning IDR-passed peaks.

**Mechanism:** IDR thresholds differ (true reps 0.05; pseudoreps 0.10). Mixing both into a union biases the consensus toward looser pseudorep peaks unless filtering carefully.

**Fix:** Decide upfront -- use only true-rep IDR (stricter, fewer peaks) OR pseudorep IDR (looser, more peaks). Don't mix.

## Decision Tree by Goal

| Goal | Strategy |
|------|----------|
| Standard 2-3 rep DA analysis with DiffBind | DiffBind `summits=250, minOverlap=2` |
| Modern ATAC publication / ML features | Corces 2018 iterative overlap (501 bp fixed) |
| ENCODE-compliant differential | IDR-passed per-rep-pair union (true-rep threshold 0.05) |
| Multi-condition with strong biology shift | Per-condition consensus then union |
| Single-cell ATAC pseudobulk | MACS3 per cluster -> iterative overlap across clusters |
| Cross-study peak comparison | Iterative overlap on shared genome build; lift over if needed |
| Quick exploratory | `bedtools merge` (acknowledge width bias; not for stats) |

## Reconciliation Across Methods

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Iterative overlap peakset much smaller than DiffBind summits=250 | Iterative removes overlapping summits within 500 bp; DiffBind keeps them | Both valid; iterative is sparser, DiffBind preserves resolution |
| Per-condition union then merged peak count >> within-condition consensus | Strong condition-specific peaks; biology is real | Use this strategy; do NOT collapse to global majority rule |
| IDR-pass peaks much fewer than majority-rule | IDR is stricter (reproducibility-aware) than overlap counting | Use IDR for high-confidence reporting; majority for exploratory |
| Same biology gives different peak counts on different genome builds | Lift-over noise; build-specific blacklist differences | Match builds; use ENCODE blacklist v2 specific to build |

**Operational rule:** Document the strategy explicitly in methods. The strategy choice can shift downstream results by 30-50% in peak count and FDR. Reproducibility requires explicit specification.

## Width-Re-centering Patterns

```python
# pybedtools: re-center on summit and fix width to 501 bp
import pybedtools as pbt

def fix_width_recenter(narrowpeak_path, half_width=250, out_path='consensus.bed'):
    """Re-center each narrowPeak on its summit and fix width to 2 * half_width + 1 bp."""
    rows = []
    for line in open(narrowpeak_path):
        f = line.strip().split('\t')
        chrom = f[0]; start = int(f[1]); summit_off = int(f[9])
        signal = float(f[6])
        summit = start + summit_off
        rows.append((chrom, max(0, summit - half_width), summit + half_width + 1,
                     f[3], signal, f[5]))
    rows.sort(key=lambda r: -r[4])               # Sort by signalValue desc
    bt = pbt.BedTool([list(map(str, r)) for r in rows])
    return bt.saveas(out_path)
```

## Per-Condition Consensus Then Union

```bash
# For each condition, build a within-condition consensus first
for cond in cond1 cond2; do
    bedtools multiinter -i <(sort -k1,1 -k2,2n ${cond}_rep1.narrowPeak) \
                            <(sort -k1,1 -k2,2n ${cond}_rep2.narrowPeak) \
                            <(sort -k1,1 -k2,2n ${cond}_rep3.narrowPeak) \
        -names rep1 rep2 rep3 | \
        awk '$4 >= 2 {print $1"\t"$2"\t"$3}' > ${cond}_consensus.bed
done

# Union across condition consensuses (preserves condition-specific peaks)
cat cond1_consensus.bed cond2_consensus.bed | \
    sort -k1,1 -k2,2n | \
    bedtools merge -i - > all_conditions_consensus.bed
```

This is the right pattern when conditions differ enough that a global majority-rule would discard condition-specific peaks.

## R-native Fixed-Width Re-centering (GenomicRanges)

For Bioconductor pipelines that avoid intermediate BED files. The iterative-overlap step requires a loop; `!duplicated(findOverlaps(...))` does NOT implement greedy non-overlap (every peak self-overlaps).

```r
library(GenomicRanges); library(rtracklayer)

peaks <- import('peaks.narrowPeak')                    # GRanges
# trim() below only clamps ranges when seqlengths are set, so attach them from the genome index
chrom_sizes <- read.table('hg38.chrom.sizes', col.names=c('chrom', 'len'))
seqlengths(peaks) <- setNames(chrom_sizes$len, chrom_sizes$chrom)[seqlevels(peaks)]
peaks_summit <- peaks                                  # column 10 of narrowPeak is summit offset
start(peaks_summit) <- start(peaks) + peaks$peak       # move start to the summit position
end(peaks_summit) <- start(peaks_summit)               # collapse to 1 bp at the summit before centering
peaks_fixed <- resize(peaks_summit, width=501, fix='center')
peaks_fixed <- trim(peaks_fixed)                       # clamp to chromosome bounds (requires seqlengths, set above)

# Sort by signalValue (column 7) descending; greedy iterative non-overlap
peaks_sorted <- peaks_fixed[order(-peaks_fixed$signalValue)]
kept <- logical(length(peaks_sorted))
already_used <- GRanges()
for (i in seq_along(peaks_sorted)) {
    if (!any(overlapsAny(peaks_sorted[i], already_used))) {
        kept[i] <- TRUE
        already_used <- c(already_used, peaks_sorted[i])
    }
}
consensus <- peaks_sorted[kept]
export(consensus, 'consensus_iterative.bed')
```

For very large peaksets (>500k), use `bedtools` shell pipeline (faster) or precompute the per-rank reduce in chunks. The greedy loop is the canonical Corces 2018 algorithm; approximations via `reduce()` or `disjoin()` are NOT equivalent.

## Cross-Organism / Cross-Build Consensus

When merging peaks across genome builds (hg19 -> hg38; human -> mouse for cross-species analysis):

```bash
# Lift over hg19 peaks to hg38
liftOver published_peaks.hg19.bed hg19ToHg38.over.chain.gz \
    published_peaks.hg38.bed published_peaks.unmapped.bed

# Then merge with current hg38 peaks
cat published_peaks.hg38.bed my_peaks.hg38.bed | \
    sort -k1,1 -k2,2n | \
    bedtools merge -i - > merged_consensus.bed
```

**Trigger:** Cross-cohort meta-analysis or comparing to published datasets on older builds.

**Mechanism:** Genome assemblies differ in coordinates, gap regions, alt-haplotypes; chain files (UCSC) provide the position translation but ~3-5% of regions fail liftover (especially complex regions, sex chromosomes, MHC).

**Fix:** Always document liftOver chain version; report unmapped fraction; for high-stakes cross-build comparisons, re-align rather than liftover.

For human -> mouse comparison, use synteny-based mapping (`bnMapper` or `halLiftover`) rather than chain liftOver because conservation is non-trivial.

## Peak-Width Adaptive (When ATAC + Broad Histone Marks Co-analyzed)

**Trigger:** Combined ATAC narrow peaks + H3K27ac (broadPeak) or H3K4me1 in the same workflow.

**Mechanism:** Fixed 501 bp from ATAC under-counts H3K27ac which spreads across 2-5 kb domains. Counting H3K27ac reads in 501 bp windows misses most signal.

**Fix:** Build a dual-resolution consensus: 501 bp for ATAC narrow peaks; broadPeak union (2-5 kb) for H3K27ac. Run differential separately on each resolution. Or use a unified per-feature width derived from the broader signal.

## ENCODE-rE2G Candidate Element Lists

**Alternative to iterative-overlap:** ENCODE-rE2G (atac-seq/enhancer-gene-linking) predicts scored enhancer-gene regulatory links for ENCODE cell types, prioritizing elements by predicted regulatory function rather than just ATAC signal strength (the genome-wide cCRE registry itself is a distinct product, SCREEN/ENCODE cCREs). Its predicted regulatory elements serve as an alternative consensus peakset for ML feature engineering. Trade-off: limited to ENCODE cell types; cell-type-specific elements may not align with the actual peakset of any specific dataset.

## Counting Reads in Consensus Peaks

```bash
# Convert BED to SAF for featureCounts (BED start is 0-based half-open; SAF Start is 1-based inclusive, so +1)
awk 'BEGIN{OFS="\t"; print "GeneID","Chr","Start","End","Strand"}
     {print $1"_"$2"_"$3, $1, $2+1, $3, "+"}' consensus.bed > consensus.saf

featureCounts -F SAF -a consensus.saf \
    -o consensus_counts.tsv \
    -p --countReadPairs \
    -T 8 \
    sample1.bam sample2.bam sample3.bam
```

`-p --countReadPairs` is required for paired-end ATAC; `-T 8` parallelizes across 8 threads. Output is the count matrix consumed by DESeq2 / edgeR / DiffBind.

## Blacklist Filtering

Blacklist filtering belongs after consensus construction, before or alongside differential testing.

```bash
# ENCODE blacklist v2 (Amemiya 2019)
bedtools intersect -v -a consensus_final.bed -b hg38-blacklist.v2.bed.gz \
    > consensus_no_blacklist.bed
echo "After blacklist: $(wc -l < consensus_no_blacklist.bed) peaks"
```

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Differential analysis flags hundreds of peaks; biology is implausible | Variable-width consensus driving width effects | Switch to fixed-width (iterative or summits=250) |
| `Negative coordinates` in fixed-width output | Peak summit too close to chromosome start | Clip with `awk '$2 >= 0'` or `bedtools slop -g chrom.sizes` |
| featureCounts SAF complaint about non-unique GeneID | Duplicate peak names in SAF | Use chr_start_end as GeneID; ensure peakset is non-redundant |
| Iterative overlap output much smaller than expected | Too many peaks within 500 bp; strict non-overlap | Try smaller half-width (e.g. 100) for higher resolution |
| `multiinter` output empty | Peak files not sorted; or wrong chromosome naming | Sort all inputs first; confirm chr name consistency |
| Per-condition union has 2x peaks of any per-condition | Strong condition-specific biology -- expected | Confirm with browser tracks; use this consensus |
| DiffBind takes hours on consensus | All-by-all counting is N samples x M peaks | Use `bParallel=TRUE` (default `DBA$config$RunParallel`); limit cores via `DBA$config$cores` |

## References

- Corces MR et al 2018 Science 362:eaav1898 (Iterative overlap, fixed-width 501 bp consensus standard)
- Stark R & Brown G 2011 DiffBind (Bioconductor; canonical reference; `summits=250` parameter)
- Quinlan AR & Hall IM 2010 Bioinformatics 26:841 (bedtools)
- Liao Y et al 2014 Bioinformatics 30:923 (featureCounts)
- Amemiya HM et al 2019 Sci Rep 9:9354 (ENCODE blacklist v2)
- Li Q et al 2011 Ann Appl Stat 5:1752 (IDR framework)
- ENCODE 4 ATAC-seq Standards (encodeproject.org/atac-seq)

## Related Skills

- atac-seq/atac-peak-calling - Generate per-replicate peaks
- atac-seq/differential-accessibility - Use consensus for DA testing
- atac-seq/atac-qc - Filter samples before consensus construction
- atac-seq/single-cell-atac - Per-cluster consensus for pseudobulk DA
- genome-intervals/bed-file-basics - bedtools operations on the consensus
- genome-intervals/interval-arithmetic - merge / intersect / subtract patterns
- chip-seq/peak-calling - Same consensus strategy applies to ChIP-seq
<!-- END FILE: atac-seq/consensus-peakset/SKILL.md -->

## 子目录：atac-seq/deep-learning-atac

<!-- BEGIN FILE: atac-seq/deep-learning-atac/SKILL.md -->
---
name: bio-atac-seq-deep-learning-atac
description: Sequence-based deep learning for ATAC-seq using chromBPNet, BPNet, scBasset, or Enformer. Use when correcting Tn5 bias with neural networks beyond k-mer models, predicting per-base accessibility profiles, scoring in silico variant effects at GWAS or rare-variant SNPs, discovering motifs via DeepLIFT/TF-MoDISco from a trained model, or generating cell-type-specific accessibility predictions for unobserved cell states.
tool_type: python
primary_tool: chrombpnet
---

## Version Compatibility

Reference examples tested with: chrombpnet 0.1.7+, bpnet-lite 0.6+ (github.com/jmschrei/bpnet-lite), scBasset 0.1.0+ (basenji2 fork), tangermeme 0.1+, tfmodisco-lite 2.2+, DeepLIFT 0.6+, captum 0.7+, tensorflow 2.13+, pytorch 2.1+, kipoi 0.8+.

Verify before use:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed package and adapt rather than retrying. Deep-learning tooling evolves rapidly; method papers post 2023 may have superseded reference implementations.

# Sequence-Based Deep Learning for ATAC-seq

**"Score the effect of a GWAS SNP on chromatin accessibility"** -> Train (or use pre-trained) sequence-to-accessibility CNNs that take 1-5 kb DNA windows and predict per-base Tn5 cleavage profiles. Outputs include: bias-corrected accessibility, single-base mutation effect predictions, and DeepLIFT contribution scores convertible to motifs via TF-MoDISco.

- CLI: `chrombpnet pipeline --bigwig signal.bw --bigwig-bias bias.bw ...`
- Python: `bpnet-lite` for custom architectures; `tangermeme` for fast scoring
- Python (single-cell): `scBasset` for per-cell sequence-based predictions
- Python (long-context): Enformer pre-trained models via Kipoi

Sequence models are NOT a replacement for MACS+TOBIAS at every step. They excel at three specific tasks where classical pipelines struggle: (1) Tn5 bias correction in low-complexity sequence contexts, (2) variant effect prediction in non-genic regions, (3) cell-type-specific motif discovery beyond what JASPAR provides.

## Algorithmic Taxonomy

| Tool | Architecture | Training | Output | Strength | Fails when |
|------|-------------|----------|--------|----------|------------|
| chromBPNet (Pampari 2024 bioRxiv) | Two-track CNN: bias model + accessibility model; bias trained on naked-DNA control or k-mer baseline, accessibility trained on chromatin signal | Per-cell-type, paired bias track | Bias-corrected per-base profile + total counts | Strongest bias correction of the compared tools; established in Kundaje lab pipelines | Requires GPU, ~24h training per cell type; needs >= 50M reads |
| BPNet (Avsec 2021 Nat Genet 53:354) | Original counts + profile dual-head CNN | TF ChIP-seq or ATAC | Per-base profile prediction | Foundational; widely cited; bpnet-lite reimpl maintained | Less polished than chromBPNet for ATAC; bias correction needs separate model |
| scBasset (Yuan & Kelley 2022) | Basenji2-derived CNN, per-cell projection layer | Single-cell ATAC | Per-cell sequence-derived peak score | First sequence model that predicts per-cell accessibility; outperforms chromVAR for cluster discrimination | Fixed architecture, hard to extend; benchmarks evolving |
| Enformer (Avsec 2021 Nat Methods 18:1196) | Long-context Transformer (196 kb input) | Reference epigenome (DNase + histones + CAGE) | Per-bin epigenome prediction | Best for distal regulation modeling; pre-trained available | Pre-trained models cell-line specific; finetuning on custom data is expensive |
| Borzoi (Linder 2025 Nat Genet) | Enformer extension trained on RNA + ATAC | Multi-tissue paired data | Sequence -> RNA + chromatin | Current best benchmark for variant effect on RNA via ATAC linkage | Newer; benchmarks still emerging |
| DeepATAC / Basset (legacy) | Earlier CNN architectures | -- | Binary peak prediction | Historical context; cited in older literature | Superseded by chromBPNet + Enformer; do not use for new work |
| tangermeme | Inference-only fast wrapper | Use any saved model | Marginal scoring of variants | Speeds up variant effect prediction 100x; works with chromBPNet/BPNet outputs | Inference only; cannot train |

Methodology evolves; verify against current Kundaje lab pipelines (chrombpnet GitHub), Greenleaf lab (scBasset), and Avsec / Linder publications before locking pipelines.

## When Deep Learning Helps vs When Classical Pipelines Suffice

| Task | Classical | Deep Learning |
|------|-----------|---------------|
| Peak calling | MACS3 / Genrich (sufficient) | chromBPNet (overkill unless variant downstream) |
| Tn5 bias correction at TF motifs | TOBIAS ATACorrect (good) | chromBPNet (better at hard cases: low-complexity flanks, deep TF footprints) |
| Differential accessibility | DiffBind / DESeq2 (sufficient) | -- (no clear DL advantage) |
| GWAS variant effect prediction at causal SNPs | Limited (overlap heuristics) | chromBPNet / Enformer (essential) |
| Motif discovery from de novo data | MEME / HOMER (good) | chromBPNet + TF-MoDISco (better; finds composite + cooperative motifs) |
| Per-cell TF activity | chromVAR (sufficient at the cluster level) | scBasset (better at fine-grained cell states) |
| Cross-cell-type accessibility prediction | -- | Enformer / Borzoi (only option) |
| Predicting cell-type-specific enhancer activity from sequence | -- | chromBPNet / Enformer (essential) |

For most standard ATAC analysis, classical pipelines remain primary. Deep learning enters when (a) variant interpretation is the goal, (b) cell-type prediction is needed beyond observed data, or (c) bias correction quality is paramount (low-input, FFPE, transcription factors with weak motifs).

## Per-Tool Failure Modes

### chromBPNet -- Bias model mismatch

**Trigger:** Training the bias model on a dataset different from the accessibility dataset (e.g. K562 bias model used on primary T cells).

**Mechanism:** chromBPNet's bias model captures sequence-specific Tn5 preference, which is mostly cell-type-invariant BUT contributions of chromatin context at cuts can vary. Cross-celltype bias models work but with degraded performance.

**Symptom:** Predicted footprints look correct at known TFs (CTCF) but fail on cell-type-specific regulators.

**Fix:** Train a per-cell-type bias model from naked-DNA control if available, OR use the chromBPNet authors' pre-trained k562 / GM12878 / HepG2 bias as a fallback (acknowledged degradation).

### chromBPNet -- Insufficient training data

**Trigger:** Training on < 50M deduplicated nuclear reads, or < 30k peaks.

**Mechanism:** CNN training needs enough peaks for stable gradient updates and enough background regions for the dual-task loss.

**Fix:** Pool replicates before training; reduce model capacity (`--num-filters`); use pre-trained model on closest cell type and skip retraining.

### BPNet / chromBPNet -- DeepLIFT vs Integrated Gradients confusion

**Trigger:** Computing per-base contributions for motif discovery.

**Mechanism:** DeepLIFT (RevealCancel rule) and Integrated Gradients (50 baseline samples) give different attribution patterns. DeepLIFT preserves additivity; IG is stochastic.

**Fix:** Use DeepLIFT rescale-rule (chromBPNet default) for TF-MoDISco. IG only when DeepLIFT fails on saturating activations. Document the choice.

### scBasset -- Cell projection layer instability

**Trigger:** Few cells per cluster; sparse training data.

**Mechanism:** scBasset learns a per-cell projection vector; with < 100 cells per cluster the projection is noisy.

**Fix:** Aggregate cells to clusters before training, OR use chromBPNet trained on pseudobulks per cluster instead.

### Enformer -- Pre-trained models lack target cell type

**Trigger:** Using Enformer for variant effects in a cell type not in its training set (e.g. GTEx tissues are covered; novel primary cell types are not).

**Mechanism:** Enformer's outputs are per-track predictions; if the target cell type wasn't trained, the agent can use a similar track as proxy but accuracy degrades.

**Fix:** Use a similar tissue track as proxy (HepG2 for liver biology; GM12878 for B-cell-like) OR fine-tune Enformer on custom data (expensive). Document the proxy.

### tangermeme -- Marginal vs in silico mutagenesis confusion

**Trigger:** Asking for a "variant effect score" without specifying the formula.

**Mechanism:** Marginal effects = ref vs alt at the SNP only. ISM = saturation across all positions in the window (every base mutated). Different magnitudes; different questions.

**Fix:** Define which calculation. For GWAS variant prediction, use marginal at the SNP (matches phenotype-genotype coupling). For motif discovery, use ISM.

## Decision Tree by Goal

| Goal | Recommended approach |
|------|---------------------|
| Score 100 GWAS SNPs for chromatin effects | Pre-trained chromBPNet model on closest cell type; tangermeme for fast scoring |
| Score 1 lead SNP at high resolution | chromBPNet + tangermeme + ISM saturation map |
| Identify TF binding motifs from a new cell type's ATAC | chromBPNet train + DeepLIFT contributions + TF-MoDISco-lite |
| Predict accessibility in a cell type not in training | Enformer pre-trained (best for ENCODE cell types) or scBasset for sc state interpolation |
| Bias-correct a low-input ATAC library before footprinting | chromBPNet bias model output as `--bias` to TOBIAS or directly use chromBPNet corrected track |
| Cell-type-specific enhancer prediction | chromBPNet trained on each cell type; per-cell-type ISM at candidate loci |
| Replace TOBIAS bias correction | chromBPNet corrected bigWig as input to TOBIAS ScoreBigwig; skip ATACorrect |

## chromBPNet Standard Pipeline

**Goal:** Train a bias-corrected CNN that predicts per-base accessibility from sequence, then score variants with it.

**Approach:** Generate train/valid/test chromosome splits, train the Tn5 bias model on background regions, train the accessibility model with bias correction, then run the standalone variant-scorer repo to predict ref-vs-alt effects at SNPs.

```bash
# 1. Generate train / valid / test chromosome splits (output is a JSON file with chrom assignments)
chrombpnet prep splits \
    -c hg38.chrom.sizes \
    -tcr chr1 chr3 chr6 \
    -vcr chr8 chr20 \
    -op splits/fold_0
# Train chromosomes are auto-inferred (whatever is not in -tcr/-vcr). The `-tecr` flag does NOT exist.

# 2. Train bias model from background regions
chrombpnet bias pipeline \
    -ibam atac.bam \
    -d ATAC \
    -g hg38.fa \
    -c hg38.chrom.sizes \
    -p peaks.narrowPeak \
    -n nonpeaks.bed \
    -fl splits/fold_0.json \
    -b 0.5 \
    -o bias_model/

# 3. Train accessibility model with bias correction
chrombpnet pipeline \
    -ibam atac.bam \
    -d ATAC \
    -g hg38.fa \
    -c hg38.chrom.sizes \
    -p peaks.narrowPeak \
    -n nonpeaks.bed \
    -fl splits/fold_0.json \
    -b bias_model/models/bias.h5 \
    -o output/

# 4. Variant effect prediction at GWAS SNPs uses the SEPARATE kundajelab/variant-scorer repo
# (the `chrombpnet snp_score` subcommand is commented out in current chrombpnet/parsers.py)
git clone https://github.com/kundajelab/variant-scorer
python variant-scorer/src/variant_scoring.py \
    --model output/models/chrombpnet_nobias.h5 \
    --list variants.tsv \
    --genome hg38.fa \
    --chrom_sizes hg38.chrom.sizes \
    --out_prefix variants_predicted
# Output: variants_predicted.variant_scores.tsv with per-SNP log2FC magnitudes
```

`-b 0.5` is the bias threshold factor (`--bias-threshold-factor`); chromBPNet docs recommend a start value of 0.5 for ATAC (0.8 for DNase). For variant scoring, use the standalone `kundajelab/variant-scorer` companion repo, NOT a chrombpnet subcommand. Verify exact flag names with `python variant_scoring.py --help` because the API evolves.

## DeepLIFT + TF-MoDISco for Motif Discovery

The maintained version is `tfmodisco-lite` (jmschrei/tfmodisco-lite, `pip install modisco-lite`), which exposes a CLI rather than the deprecated v1 `TfModiscoWorkflow` Python API. The original `kundajelab/tfmodisco` package (with `tfmodisco.tfmodisco_workflow.workflow.TfModiscoWorkflow`) is unmaintained and incompatible with `modisco-lite`.

**Goal:** Discover de novo motifs from a trained chromBPNet model using per-base contribution scores.

**Approach:** Extract one-hot sequences and DeepLIFT/SHAP contributions from chromBPNet, run modisco-lite to cluster seqlets into motif patterns, then generate an annotated HTML report matched against a known motif database.

```bash
# Generate one-hot sequence and SHAP / DeepLIFT contribution score arrays from chromBPNet
# (chromBPNet `chrombpnet contribs_bw` writes hypothetical contributions; convert to numpy via shap_to_modisco)

# Run TF-MoDISco-lite via its CLI
modisco motifs \
    -s ohe.npz \
    -a shap.npz \
    -n 2000 \
    -w 500 \
    -o modisco_results.h5

# Generate HTML report with discovered motifs matched to known databases
modisco report \
    -i modisco_results.h5 \
    -o modisco_report/ \
    -m motifs_meme.txt \
    -s modisco_report/
```

`-n 2000` caps seqlets per metacluster; `-w 500` is the window around each peak center considered for motif discovery (default 400; the seqlet-core sliding-window size is a separate flag, `-z`/`--size`, default 20). `motifs_meme.txt` (e.g. JASPAR or HOCOMOCO MEME-format) lets `modisco report` annotate clusters against known motifs.

## In Silico Variant Effect Prediction

**Goal:** Score the effect of SNPs on predicted accessibility using a trained chromBPNet model.

**Approach:** Load the bias-free chromBPNet model, build ref and alt one-hot windows centered on each SNP, run tangermeme's substitution_effect to get paired predictions, then compute log2(alt/ref) per variant.

```python
import numpy as np

# tangermeme's variant-effect API: substitution_effect for SNPs, marginalize for motif insertions
from tangermeme.variant_effect import substitution_effect
from tangermeme.predict import predict

# Load pre-trained chromBPNet model (saved as Keras .h5 or PyTorch state_dict).
# chromBPNet wraps Keras; load with tensorflow.keras.models.load_model and wrap for tangermeme.
# `load_chrombpnet_model` below is pseudocode -- substitute the actual loader for the installed version
# (e.g. tf.keras.models.load_model + tangermeme.io.adapter, or torch.load for PyTorch checkpoints).
model = load_chrombpnet_model('output/models/chrombpnet_nobias.h5')

# substitution_effect: per-SNP ref vs alt prediction across a sequence window
# X shape (N, 4, L); substitutions is a sparse-COO tensor of shape (-1, 3) where each row is
# [example_idx, position, new_base_idx] (new_base_idx 0-3 for ACGT)
y_ref, y_alt = substitution_effect(model, X, substitutions)
log2fc = np.log2(y_alt.sum(axis=-1) / y_ref.sum(axis=-1))
```

For motif marginalization (testing a candidate motif's effect by inserting it into background sequences), use `tangermeme.marginalize.marginalize(model, X, motif)`. The `motif` argument is a one-hot tensor of shape `(-1, 4, motif_length)`; convert string motifs via `tangermeme.utils.one_hot_encode`. Verify the exact signatures with `help(tangermeme.marginalize.marginalize)` because tangermeme is actively developed; `marginal_predict` is NOT a real function name.

`log2fc` magnitudes are unitless; |log2fc| > 1 typical for strong-effect SNPs in regulatory regions.

## Reconciliation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| chromBPNet predicts strong effect; MACS does not call peak | Sequence model captures latent regulatory potential | Trust chromBPNet for variant effect; not for peak calling |
| Enformer prediction differs from chromBPNet at same locus | Different context windows (196 kb vs 1-2 kb); different cell types | Both can be correct at different scales; report both with their context size |
| TF-MoDISco motifs differ from JASPAR | Different methodology (sequence-based vs ChIP-validated) | TF-MoDISco can find composites and cooperative; check JASPAR for confirmation |
| chromBPNet bias correction differs from TOBIAS ATACorrect | Different bias models (CNN vs k-mer) | chromBPNet is more accurate but slower; TOBIAS still publishable for standard use |

**Operational rule:** For high-confidence variant prediction, agree across two approaches: chromBPNet + Enformer (or Borzoi). Single-tool calls should be reported as exploratory. For motif discovery, validate TF-MoDISco hits against JASPAR/HOCOMOCO before publication.

## GPU and Compute Considerations

| Task | Hardware | Wall time |
|------|---------|-----------|
| chromBPNet training (per cell type) | 1 A100 GPU, 80 GB RAM | ~24 h |
| chromBPNet inference at 1M variants | 1 A100 | ~4 h |
| Enformer pre-trained inference | 1 V100+ | ~30 min for 100k variants |
| Borzoi training | 1 A100, ~250 GB RAM | ~7 days |
| scBasset training (10k cells) | 1 V100, 32 GB RAM | ~12 h |
| TF-MoDISco on 1M peaks | CPU 32 cores | ~6 h |

For most labs without sustained GPU access: use pre-trained chromBPNet/Enformer models for inference; only train custom models when the cell type is not in the public model zoo (encodeproject.org/atac-seq pre-trained chromBPNet).

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| chromBPNet `bias.h5` missing | Bias model training failed silently | Re-run `chrombpnet bias pipeline` with verbose; check input BAM size |
| Out of memory during training | Default batch size too large for GPU | `--batch-size 64` or smaller; reduce `--num-filters` |
| Predicted profile is constant | Model collapsed (training too short) | Increase epochs; verify input peaks are non-empty |
| TF-MoDISco produces too many small clusters | `target_seqlet_fdr` too loose | Tighten to 0.01; or increase `flank_size` |
| Enformer prediction has wrong shape | Pre-trained model expects 196 kb input | Pad input to exactly 196,608 bp |
| Variant effect predictions cluster near zero | SNP outside model's effective window | Predict on window-centered sequences (variant at the center) |
| chromBPNet model not converging | Peaks file contains chrM or blacklist | Pre-filter; chromBPNet does not auto-filter |
| scBasset training crashes on Apple Silicon | TensorFlow Metal incompatible with operations | Use CPU mode or run on Linux GPU |

## References

- Pampari A et al 2024 bioRxiv 2024.12.25.630221 (chromBPNet; Tn5 bias correction with deep learning; preprint)
- Avsec Z et al 2021 Nat Genet 53:354-366 (BPNet; foundational sequence-to-profile)
- Avsec Z et al 2021 Nat Methods 18:1196-1203 (Enformer; long-context Transformer)
- Linder J et al 2025 Nat Genet (Borzoi; multi-tissue sequence-to-RNA+chromatin; consult current publication for exact volume/pages)
- Yuan H & Kelley DR 2022 Nat Methods 19:1088 (scBasset)
- Shrikumar A et al 2017 ICML (DeepLIFT)
- Schreiber J 2025 bioRxiv 2025.08.08.669296 (tangermeme; fast inference utilities)
- Shrikumar A et al 2018 arXiv:1811.00416 (TF-MoDISco)
- Kelley DR 2020 PLoS Comput Biol 16:e1008050 (Basenji2; cross-species precursor)

## Related Skills

- atac-seq/atac-peak-calling - Classical peak calling input
- atac-seq/footprinting - Use chromBPNet bias correction as TOBIAS alternative
- atac-seq/motif-deviation - chromVAR vs scBasset for per-cell motif activity
- atac-seq/single-cell-atac - scBasset integration with sc workflow
- atac-seq/enhancer-gene-linking - Variant effect feeds enhancer scoring
- atac-seq/allele-specific-accessibility - DL-predicted variant effects vs observed allelic imbalance
- causal-genomics/fine-mapping - Downstream use of variant effect scores
- machine-learning/biomarker-discovery - General ML patterns
- gene-regulatory-networks/scenic-regulons - Combine motif discovery with TF networks
<!-- END FILE: atac-seq/deep-learning-atac/SKILL.md -->

## 子目录：atac-seq/differential-accessibility

<!-- BEGIN FILE: atac-seq/differential-accessibility/SKILL.md -->
---
name: bio-atac-seq-differential-accessibility
description: Identify differentially accessible chromatin regions across conditions using DiffBind, csaw, DESeq2, or edgeR. Use when comparing ATAC-seq accessibility between treatment groups, choosing between consensus-peak vs sliding-window approaches, picking the correct normalization (full library vs reads-in-peaks), correcting batch with SVA/RUVseq, or interpreting log2FC and FDR thresholds in a chromatin context.
tool_type: r
primary_tool: DiffBind
---

## Version Compatibility

Reference examples tested with: DiffBind 3.12+, DESeq2 1.42+, edgeR 4.0+, csaw 1.36+, limma 3.58+, GenomicRanges 1.54+, ChIPseeker 1.38+, Subread 2.0+ (featureCounts), sva 3.50+, RUVSeq 1.36+.

Before using code patterns, verify installed versions match:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws unexpected errors, introspect the installed package and adapt rather than retrying.

# Differential Accessibility

**"Find chromatin regions that change accessibility between my conditions"** -> Build a sample-by-region count matrix, normalize for library size and chromatin compaction, fit a generalized linear model (negative-binomial), and extract regions with significant accessibility change.

- R (consensus-peak workflow): `DiffBind` -> count -> normalize -> contrast -> analyze
- R (window-based, no peak set): `csaw::windowCounts` + `filterWindowsGlobal` + edgeR QL F-test
- R (existing peak-count matrix): `DESeq2` or `edgeR` directly on `featureCounts` output

DiffBind is a wrapper around DESeq2 / edgeR with ATAC-aware defaults. csaw is the only peak-free option; it tests fixed-width sliding windows. The choice depends on whether peaks are stable across conditions (use DiffBind) or whether some condition has dramatically different peak structure (use csaw or rebuild consensus peaks).

## Algorithmic Taxonomy

| Tool | Model | Input | Min reps | Strength | Fails when |
|------|-------|-------|----------|----------|------------|
| DiffBind 3.x (default DESeq2) | NB GLM via DESeq2 on consensus peaks | BAM + peak files | 2-3 per group | ATAC-aware defaults; built-in QC; blocking factors. Default in 3.x is `normalize=DBA_NORM_LIB` with `library=DBA_LIBSIZE_FULL` (full library size, background-included) | Peaks differ dramatically between conditions (closed -> open shifts width); fewer than 2 reps per group |
| DiffBind with edgeR backend | NB GLM via edgeR-QL on consensus peaks | Same | 2-3 per group | Robust at low replicates (n=2 OK); QL test calibrates dispersion better than DESeq2 at small n | When global accessibility shifts dominate, switch to spike-in or full-library (library=DBA_LIBSIZE_FULL), never reads-in-peaks |
| DESeq2 directly on peak counts | NB GLM with shrinkage | featureCounts SAF | 3+ | Maximum control; integrates with apeglm shrinkage; modern interface | Need to manually build consensus peakset; per-region pre-filter required (low counts inflate dispersion) |
| edgeR QL F-test on peak counts | NB QL (quasi-likelihood) | featureCounts | 2 | Calibrated FDR at low n (n=2 viable); robust to outlier reps | Manual consensus peakset; small library bias unless normalization explicit |
| csaw (windows) | edgeR-QL on sliding windows | BAM only | 2 | No peak set required; detects diffuse changes peaks miss; merges adjacent windows | Computationally heavy; window size choice biases results; harder to annotate downstream |
| limma-voom | linear model with mean-variance trend | log2(CPM+offset) | 3 | Fast; good calibration at moderate count | Mis-calibrated at very low counts (atac peaks often have dropouts); needs explicit voom normalization |

Methodology evolves; verify the current consensus practice (Gontarz 2020 DA-strategy benchmark; Reske 2020 normalization comparison) before locking pipelines.

## Decision Tree by Experimental Scenario

| Scenario | Recommended workflow | Why |
|----------|---------------------|-----|
| 3+ reps, similar peak structure across conditions | DiffBind (DESeq2 backend), `summits=250`, `normalize=DBA_NORM_NATIVE` | Standard pattern; peak-level inference is interpretable |
| 2 reps per condition | DiffBind with edgeR backend OR raw edgeR QL | DESeq2 underpowered at n=2; QL is robust |
| Peak structure differs dramatically (e.g., differentiation, KO of pioneer TF) | csaw windows OR rebuild consensus peakset post-hoc per condition then take union | Stable consensus peakset is invalid when chromatin landscape shifts |
| Multi-factor design (batch, sex, time) | DiffBind with `dba.contrast(..., design='~Batch + Condition')` | Standard linear model adjustment |
| Hidden batch / unknown variance | DESeq2 + SVA OR RUVseq before fitting | Empirical surrogate variables capture unknown nuisance |
| Long timecourse (5+ time points) | DESeq2 LRT (likelihood ratio test) on `~time + condition + time:condition` | Captures temporal interaction; use `differential-expression/timeseries-de` patterns |
| Diffuse / broad accessibility change (super-enhancers) | csaw with merged windows OR call broad peaks first | Narrow peaks fragment broad domains -> inflated peak count, deflated effect |
| Single-cell ATAC pseudobulk | DESeq2 on aggregated counts OR Signac::FindMarkers | See atac-seq/single-cell-atac |
| Allele-specific accessibility | csaw on heterozygous SNPs OR HOMER tagDir | Peak-level invalid because alleles share peaks |
| Plant / non-model organism | DiffBind works; just provide custom `genome` and disable annotation | Annotation step assumes UCSC TxDb; bypass if absent |

## Consensus Peak Set Strategy

The consensus peakset choice drives FDR calibration. DiffBind defaults rarely match what a chromatin biologist wants.

| Strategy | Implementation | When to use |
|----------|---------------|-------------|
| Intersection (peak in all reps) | `dba.count(minOverlap=N)` with N = total reps | Strict; for high-confidence reproducible analysis (matches IDR philosophy) |
| Union (peak in any rep) | `minOverlap=1` | Maximum sensitivity; risks single-rep artefact peaks |
| Majority rule (peak in >= half reps) | `minOverlap=ceiling(N/2)` | DiffBind default-ish; balance |
| Per-condition union, then union of unions | Compute consensus per group, then merge | Best when conditions have very different peak counts |
| Iterative overlap removal (Corces 2018) | Sort peaks by significance; greedily keep non-overlapping; fixed-width 501 bp | Standard for fixed-width consensus; required for peak-count matrices used in machine learning |

Refer to atac-seq/consensus-peakset for full coverage of fixed-width re-centering and the iterative overlap algorithm. For DiffBind, the key parameter is `summits=250` (re-center peaks on summit +/- 250 bp = 501 bp fixed width).

## Normalization: The ATAC-Specific Choice

DiffBind 3.x conflates two orthogonal choices: the normalization method (`normalize=`) and the library-size definition (`library=`). The defaults are `normalize=DBA_NORM_LIB` with `library=DBA_LIBSIZE_FULL` (full mapped-read total).

| Choice | DiffBind argument | What it does | When to use |
|--------|-------------------|--------------|-------------|
| Normalize by library size only | `normalize=DBA_NORM_LIB` (default) | Scale counts by the chosen library size | Standard; pairs with full or RiP library |
| Reads-in-peaks library size | `library=DBA_LIBSIZE_PEAKREADS` | Library size = reads in consensus peaks (RiP) | When background varies independently of biology (protects against background drift) |
| Full mapped library size | `library=DBA_LIBSIZE_FULL` (default) | Library size = total mapped reads | When global accessibility shifts must remain visible (e.g., chromatin compaction) |
| Native per-tool default | `normalize=DBA_NORM_NATIVE` | DESeq2 RLE or edgeR TMM, depending on backend | Use DESeq2/edgeR conventions directly |
| TMM (edgeR) | `normalize=DBA_NORM_TMM` | Trimmed mean of M-values | Robust to a few highly-DA peaks dominating |
| RLE (DESeq2) | `normalize=DBA_NORM_RLE` | DESeq2 geometric-mean size factors | DESeq2-conventional analysis |
| Spike-in / external | not built-in; pre-scale counts | Exogenous reference (e.g., spike-in chromatin) | Required when global scaling is biological |

**Trigger:** Treatment causes global chromatin compaction (e.g., HDAC inhibitor, DNMT inhibitor).

**Mechanism:** Full library-size normalization is robust to background but the default still scales background reads in; under uniform global compaction the magnitudes can collapse. RiP scaling (`library=DBA_LIBSIZE_PEAKREADS`) makes the opposite assumption (peak signal is stable, background absorbs the shift) and so erases the very biology of interest.

**Symptom:** Volcano plot is symmetric about zero; PCA shows treatment effect that vanishes after normalization.

**Fix:** Use spike-in normalization (add exogenous chromatin pre-Tn5; scale by spike-in reads), or keep the default `library=DBA_LIBSIZE_FULL` but interpret with the global shift in mind. Reske 2020 documented that the normalization choice materially changes which peaks are called differential under such a global shift.

## Per-Tool Failure Modes

### DiffBind -- Library-size choice confounds global change

**Trigger:** Treatment causes whole-genome accessibility shift; cell-cycle synchronized samples; differentiation timecourse.

**Mechanism:** Setting `library=DBA_LIBSIZE_PEAKREADS` (RiP-based) assumes total reads-in-peaks is comparable across samples. Global accessibility shifts break this assumption.

**Symptom:** Conditions clearly differ in PCA before normalization; after normalization PC1 is nearly noise.

**Fix:** Keep the default `library=DBA_LIBSIZE_FULL` (or use spike-in scaling) and re-run `dba.contrast` and `dba.analyze`. Re-inspect PCA; if treatment now drives PC1, the global-shift biology is preserved.

### DiffBind summits parameter -- Width-driven differential

**Trigger:** Per-rep peaks have very different widths; consensus uses union.

**Mechanism:** Without `summits=250`, DiffBind counts reads in the original peak intervals. A peak called as 200 bp in one rep and 800 bp in another inflates the count for the wider rep.

**Symptom:** Top differential peaks track peak width, not signal intensity.

**Fix:** Always set `summits=250` (or 100, depending on resolution). This re-centers all peaks on the summit and uses identical 501 (or 201) bp windows.

### csaw -- Window size and filter choice dominates results

**Trigger:** Default `width=spacing=50` bp windows; default `filter=10` count cutoff.

**Mechanism:** Narrow windows have very low counts and inflated dispersion; the global background filter discards too many windows. Results are extremely sensitive to these.

**Symptom:** Number of significant windows ranges from 200 to 200,000 across reasonable parameter sweeps.

**Fix:** Use `width=150` for ATAC (matches typical NFR fragment); threshold with `filterWindowsGlobal(data, background)$filter > log2(3)` to discard low-signal windows. Validate by running on technical replicates -- ~0 differential windows is the expected outcome.

### DESeq2 -- Apeglm shrinkage with too few reps

**Trigger:** n=2 per condition; using `lfcShrink(type='apeglm')`.

**Mechanism:** Apeglm shrinks log2FC toward zero based on dispersion estimate; at n=2 dispersion is unreliable, shrinkage is over-aggressive, and biology is masked.

**Symptom:** All log2FC values cluster near zero post-shrinkage; FDR list has high p-values across the board.

**Fix:** Skip shrinkage at n=2 OR switch to edgeR QL test. If n=2 is unavoidable, report unshrunken log2FC alongside FDR; do not use shrunken FCs as the effect size.

### edgeR QL -- Filter must be aggressive enough

**Trigger:** Including peaks with mean count < 5 across all samples.

**Mechanism:** The QL F-test calibrates dispersion across all features. Including very-low-count peaks pulls dispersion estimates and inflates FDR.

**Fix:** `filterByExpr(y, group=group)` removes low-count peaks; restore peaks one at a time only if they are biologically critical and supported by at least one rep at depth.

## Reconciliation: When Tools Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| DiffBind + DESeq2 differ wildly | Different normalization (DiffBind default = full library `DBA_NORM_LIB`/`DBA_LIBSIZE_FULL`, DESeq2 default = RLE) | Force same normalization; differences should shrink |
| DiffBind + csaw differ | csaw catches diffuse changes peaks miss; DiffBind catches narrow peaks csaw smooths | Both can be correct; report intersection as high-confidence |
| Top hits in DiffBind have FDR > 0.5 in DESeq2 | DiffBind's blacklist filter or width re-centering changes the per-region count | Re-run DESeq2 on the exact DiffBind consensus matrix (`dba.peakset` extract) |
| Effect-size ranking differs across reps | One rep is an outlier -- check PCA | Drop or block as covariate; never silently include |
| No significant peaks despite obvious browser-track differences | Library-size normalization eaten the global shift | Switch to spike-in or full-library normalization |

**Operational rule:** For high-confidence reporting, require concordant detection in two methods from different families (DiffBind/DESeq2-style on consensus peaks AND csaw-style sliding windows agreeing within +/- 500 bp). Report the intersection as primary; the union as exploratory.

## Effect Size and Threshold Selection

| Question | Threshold | Rationale |
|----------|-----------|-----------|
| Statistical significance | FDR < 0.05 | Standard BH FDR (DESeq2 / edgeR / DiffBind default) |
| Stringent biological change | abs(log2FC) >= 1 (= 2-fold) | Within-noise effects below 2-fold are unreliable in chromatin |
| Conservative reporting | FDR < 0.01 AND abs(log2FC) >= 1 | Per ENCODE differential reporting guidance |
| Exploratory / discovery | FDR < 0.1 OR shrunken log2FC >= 0.585 (1.5x) | For follow-up validation, not final claim |
| Proper effect-size reporting | Use shrunken log2FC (apeglm or DESeq2 lfcShrink) when n >= 3 | Raw log2FC at low counts is volatile |

abs(log2FC) >= 1 is *not* universal. ATAC effects in primary cells (immune subsets, neurons) often max at 1.5-fold; require log2FC >= 0.585 with FDR < 0.05 for those settings.

## Hidden Batch with SVA / RUVseq

**Goal:** Recover differential accessibility signal when unknown batch effects swamp the contrast.

**Approach:** Estimate surrogate variables on normalized counts via svaseq, append them to the DESeq2 design, refit the model, and extract the contrast.

```r
library(DESeq2); library(sva)

dds <- DESeqDataSetFromMatrix(countData=counts, colData=coldata, design=~condition)
dds <- estimateSizeFactors(dds)
dat <- counts(dds, normalized=TRUE)
dat <- dat[rowMeans(dat) > 1, ]

mod  <- model.matrix(~condition, colData(dds))
mod0 <- model.matrix(~1, colData(dds))
svobj <- svaseq(dat, mod, mod0, n.sv=2)

dds$SV1 <- svobj$sv[, 1]; dds$SV2 <- svobj$sv[, 2]
design(dds) <- ~SV1 + SV2 + condition
dds <- DESeq(dds)
res <- results(dds, contrast=c('condition', 'treated', 'control'))
```

RUVseq is the alternative when negative-control regions (ChrM peaks NOT changing) or technical replicates are available. SVA is preferred when no controls exist.

## Spike-in Normalization

**Trigger:** Treatment causes whole-genome accessibility shift (HDAC inhibitor, DNMT inhibitor); RPM/CPM/RiP normalization erases the global biology.

**Mechanism:** Exogenous chromatin spike-in (Drosophila S2 nuclei) is added at constant cell number ratio pre-Tn5; reads aligning to dm6 quantify the constant exogenous baseline. Sample-level scaling factor = inverse of dm6 reads per sample, applied to human-aligned counts.

**Goal:** Preserve global accessibility shifts that RiP / library-size normalization would erase.

**Approach:** Compute per-sample size factors from inverse spike-in read counts, override DESeq2's default size factors, then run the standard DESeq2 fit and contrast.

```r
library(DESeq2)

# spike_counts: per-sample dm6 read counts (one column per sample)
sf_spike <- 1 / spike_counts
sf_spike <- sf_spike / mean(sf_spike)                 # Geometric mean = 1 for stability

dds <- DESeqDataSetFromMatrix(countData=counts, colData=coldata, design=~condition)
sizeFactors(dds) <- sf_spike                          # Override library-size factors
dds <- DESeq(dds)
res <- results(dds, contrast=c('condition', 'treated', 'control'))
```

After spike-in normalization, log2FC reflects absolute accessibility change (not just relative redistribution). Spike-in is the most direct control for global-shift biology.

## Permutation Testing for Low Replicate Designs

**Trigger:** n=2 per condition; parametric NB tests give over-confident p-values.

**Mechanism:** csaw provides a permutation framework: the null is generated by shuffling sample labels; test statistic is the count-difference per window; per-region p is the rank under permutation.

**Goal:** Generate empirical per-region p-values when parametric NB tests are over-confident at low replicate counts.

**Approach:** Fit the observed edgeR QL F statistic, repeatedly shuffle group labels and refit, then compute per-region p as the rank of the observed F under the shuffled null.

```r
library(csaw); library(edgeR)

# Standard csaw counts (windows or peaks)
counts <- regionCounts(bam_files, regions, ext=200)

# Standard NB fit
y <- DGEList(counts=assay(counts), group=condition)
y <- calcNormFactors(y, method='TMM')
design <- model.matrix(~condition)
y <- estimateDisp(y, design)
fit <- glmQLFit(y, design)

# Permutation: shuffle group labels n_perms times; track per-region rank statistic
n_perms <- 1000
perm_p <- replicate(n_perms, {
    shuffled <- sample(condition)
    design_p <- model.matrix(~shuffled)
    fit_p <- glmQLFit(estimateDisp(y, design_p), design_p)
    glmQLFTest(fit_p, coef=2)$table$F
})
observed_F <- glmQLFTest(fit, coef=2)$table$F
permp <- rowMeans(perm_p >= observed_F)
```

Permutation requires ~1000 shuffles for stable per-region p; computationally expensive but essential when parametric tests cannot be trusted.

## DESeq2 Likelihood Ratio Test for Time-Courses

**Goal:** Identify peaks whose accessibility trajectory differs between conditions across a timecourse.

**Approach:** Fit a DESeq2 LRT comparing a full model with a spline-by-condition interaction against a reduced model lacking the interaction; significant peaks have time-dependent condition response.

```r
library(DESeq2); library(splines)

# Spline-modeled time course (5+ time points)
dds <- DESeqDataSetFromMatrix(countData=counts, colData=coldata,
                              design=~ns(timepoint, df=3) + condition + ns(timepoint, df=3):condition)
dds_full <- DESeq(dds, test='LRT', reduced=~ns(timepoint, df=3) + condition)
res <- results(dds_full)
```

The LRT compares the full model (with time:condition interaction) to a reduced model without; significant peaks have time-dependent condition response. Use `df=3` natural splines for typical 5-7 timepoints; df=4-5 for >= 8.

## Hi-C-Loop-Anchored Differential

**Trigger:** Combined ATAC-seq + Hi-C/HiChIP datasets; want to test enhancer-promoter pair-level differential.

**Mechanism:** Aggregate peak-level differential signal at HiCCUPS loop anchors (or ABC-predicted enhancer-gene pairs). Combined enhancer + promoter accessibility change has more statistical power than either alone.

**Goal:** Test enhancer-promoter pair-level differential accessibility by aggregating peak-level signal at loop anchors.

**Approach:** Import HiCCUPS loops, map consensus peaks to anchor positions, then aggregate per-peak log2FC across both anchors of each loop to get loop-level effect sizes.

```r
# Pseudo-pattern: per loop, sum DESeq2 log2FC at both anchors
loops <- makeGenomicInteractionsFromFile('hiccups_loops.bedpe', type='bedpe',
                                         experiment_name='hiccups', description='HiCCUPS loops')
peak_to_loop <- findOverlaps(consensus_peaks, c(anchorOne(loops), anchorTwo(loops)))

loop_lfc <- aggregate(res$log2FoldChange[queryHits(peak_to_loop)],
                      by=list(loop=ceiling(subjectHits(peak_to_loop) / 2)),
                      FUN=function(x) sum(x, na.rm=TRUE))
```

For implementation, use the `InteractionSet` Bioconductor package which preserves loop-pair structure during testing. Reference: Mumbach 2017 Nat Genet (HiChIP enhancer connectome).

## Annotate Differential Peaks

**Goal:** Assign each differentially accessible peak to its nearest gene and feature class for downstream interpretation.

**Approach:** Pull DiffBind / DESeq2 results as GRanges, annotate via ChIPseeker against a TxDb with a custom promoter window, then plot annotation distribution and extract gene IDs for enrichment.

```r
library(ChIPseeker); library(TxDb.Hsapiens.UCSC.hg38.knownGene)

diff_peaks <- dba.report(dba)
peakAnno <- annotatePeak(diff_peaks, TxDb=TxDb.Hsapiens.UCSC.hg38.knownGene,
                         tssRegion=c(-2000, 500), level='gene')
plotAnnoPie(peakAnno); plotDistToTSS(peakAnno)
genes <- as.data.frame(peakAnno)$geneId          # for GO enrichment via pathway-analysis/go-enrichment
```

`tssRegion=c(-2000, 500)` defines promoter as TSS-2kb to TSS+500bp; ChIPseeker default (`-3000, 3000`) over-counts promoter assignments. Adjust per cell type / organism.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| DiffBind very slow | Counting all peaks across all BAMs sequentially | `dba.count(..., bParallel=TRUE)` and provide `BPPARAM` |
| `unable to use the provided design matrix` (DESeq2) | Confounded design (e.g., batch perfectly aligns with condition) | Replicate in a way that breaks the confound, or drop the batch term |
| FDR list empty despite obvious differences | RiP scaling (`library=DBA_LIBSIZE_PEAKREADS`) removed global biology | Use spike-in or keep default `library=DBA_LIBSIZE_FULL`; verify with browser tracks |
| Top peaks all on chrM | chrM not removed from BAM before counting | Always strip chrM upstream |
| dispersion estimate failure (DESeq2) | Too few peaks pass filter; too few reps | `filterByExpr` less aggressively; check rep count |
| `Error in if (any(out))`(csaw) | Window count below threshold | Reduce `bin.size`; check BAM is paired-end |
| ChIPseeker error on non-human TxDb | Wrong organism db loaded | Use `make_org_db` from biomartr or AnnotationDbi for non-model |
| Volcano plot symmetric about zero with no significant peaks | Hidden batch swamping signal | Run SVA/RUVseq |

## References

- Stark R & Brown G 2011 DiffBind (Bioconductor; canonical reference)
- Lun ATL & Smyth GK 2014 NAR 42:e95 (csaw windowed differential method)
- Love MI et al 2014 Genome Biol 15:550 (DESeq2)
- Robinson MD et al 2010 Bioinformatics 26:139 (edgeR)
- Chen Y et al 2016 F1000Res 5:1438 (edgeR-QL framework)
- Leek JT 2014 NAR 42:e161 (svaseq for hidden batch)
- Risso D et al 2014 Nat Biotechnol 32:896 (RUVseq)
- Reske JJ et al 2020 Epigenetics Chromatin 13:22 (ATAC normalization-method comparison; ARID1A/PIK3CA global-shift case study)
- Gontarz P et al 2020 Sci Rep 10:10150 (comparison of differential-accessibility analysis strategies for ATAC-seq)
- Corces MR et al 2018 Science 362:eaav1898 (iterative overlap, fixed-width 501 bp consensus)
- Yu G et al 2015 Bioinformatics 31:2382 (ChIPseeker)

## Related Skills

- atac-seq/atac-peak-calling - Generate per-replicate peaks
- atac-seq/consensus-peakset - Build the differential-ready consensus peakset
- atac-seq/atac-qc - Pre-screen and drop failing replicates
- atac-seq/single-cell-atac - Pseudobulk-level differential per cluster
- atac-seq/co-accessibility - Identify cis-regulatory connections among DA peaks
- differential-expression/deseq2-basics - Underlying DESeq2 patterns
- differential-expression/de-results - Effect-size reporting and shrinkage
- chip-seq/differential-binding - Same DiffBind workflow, ChIP context
- pathway-analysis/go-enrichment - Downstream gene-level enrichment of DA-associated genes
<!-- END FILE: atac-seq/differential-accessibility/SKILL.md -->

## 子目录：atac-seq/enhancer-gene-linking

<!-- BEGIN FILE: atac-seq/enhancer-gene-linking/SKILL.md -->
---
name: bio-atac-seq-enhancer-gene-linking
description: Predict enhancer-gene regulatory connections from ATAC-seq using ABC, ENCODE-rE2G, HiChIP, or Cicero. Use when linking distal enhancers to target genes, choosing between contact-aware (ABC, ENCODE-rE2G), accessibility-only (Cicero), and orthogonal (HiChIP H3K27ac, EpiMap) approaches, validating predictions against CRISPRi-FlowFISH gold-standard, or building cell-type-specific regulatory maps for fine-mapping or therapeutic target discovery.
tool_type: mixed
primary_tool: ABC-Enhancer-Gene-Prediction
---

## Version Compatibility

Reference examples tested with: ABC-Enhancer-Gene-Prediction 0.2.2+ (Engreitz lab), ENCODE-rE2G v1.0+ (EngreitzLab), Cicero 1.20+, GenomicInteractions 1.36+, FitHiChIP 9.1+, HiC-Pro 3.1+, FAN-C 0.9+, MACS3 3.0+, samtools 1.19+, bedtools 2.31+.

Verify before use:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws unexpected errors, introspect the installed package and adapt rather than retrying.

# Enhancer-Gene Linking

**"Which gene does this distal accessible region regulate?"** -> Predict the enhancer's target gene using a model that combines accessibility activity, 3D contact frequency, and (optionally) sequence-based chromatin predictions. Output is a per-(enhancer, gene) score that can be thresholded for high-confidence calls.

- CLI: ABC pipeline (`run.neighborhoods.py`, `predict.py` from Engreitz lab)
- CLI: ENCODE-rE2G (Snakemake-based; ENCODE 4 enhancer-gene standard)
- R: Cicero (ATAC-only; covered in atac-seq/co-accessibility)
- CLI: FitHiChIP / hichipper for HiChIP H3K27ac loops
- Database: EpiMap (Boix 2021), GeneHancer, FANTOM5 (pre-computed reference)

ABC and ENCODE-rE2G are the canonical predictors when Hi-C/Micro-C data is available. Cicero is the ATAC-only fallback. CRISPRi-FlowFISH (Fulco 2019) is the gold-standard experimental validation.

## Algorithmic Taxonomy

| Method | Inputs | Mathematics | Strength | Fails when |
|--------|--------|-------------|----------|------------|
| ABC (Fulco 2019, Nasser 2021) | ATAC + H3K27ac + Hi-C/Micro-C | ABC = (Activity_E x Contact_E,G) / sum_e(Activity_e x Contact_e,G); threshold typically >= 0.02 | Mechanistically grounded; published gold-standard for human cell lines | Requires matched Hi-C / Micro-C; cell-type-specific; default contact uses average across 10 ENCODE cell types if Hi-C not available |
| ENCODE-rE2G (Gschwind 2023) | ATAC + H3K27ac + (Hi-C optional) | Logistic regression trained on CRISPRi-FlowFISH ground truth; uses ABC features + sequence features + distance | ENCODE 4 standard; pre-trained models for many cell types | Pre-trained models only available for ENCODE cell types; retraining requires CRISPRi data |
| Cicero (Pliner 2018) | scATAC peak-cell matrix | Graphical lasso on metacell co-accessibility | ATAC-only; works without Hi-C | Less concordant with Hi-C than ABC; cis-distance-limited; alpha-sensitive |
| HiChIP H3K27ac + FitHiChIP | H3K27ac HiChIP | Statistically significant loops at FDR < 0.05 | Direct experimental loop measurement; cell-type-specific; orthogonal to ATAC | Requires HiChIP wet-lab; only captures loops within HiChIP resolution (~10 kb) |
| Hi-C + HiCCUPS | Bulk Hi-C | Fold-enrichment loop calling | Most-validated 3D contact method | Resolution typically 5-25 kb; misses sub-loop fine structure |
| Capture Hi-C / PCHi-C (CHiCAGO) | Promoter Capture Hi-C | Asymptotic CHiCAGO score | High-resolution promoter-anchored | Wet-lab cost; promoter capture only |
| EpiMap (Boix 2021) reference | None (pre-computed lookup) | Bulk-derived enhancer-gene predictions in 833 epigenomes | Fast, comprehensive | Cell-type-agnostic for tissues outside the reference set |
| GeneHancer / FANTOM5 (legacy) | None (pre-computed lookup) | Pre-computed; varied methods per database | Comprehensive lookup; widely cited | Older; less reliable than ABC for cell-type-specific |

Methodology evolves; verify against current Engreitz lab releases (ABC), ENCODE 4 publications (ENCODE-rE2G), and Mumbach 2017 (HiChIP) before locking pipelines.

## ABC Mathematics

For each candidate (enhancer E, gene G) pair within the cis window (default 5 Mb):

```
ABC(E -> G) = Activity_E * Contact_E,G / sum_{all e in window}(Activity_e * Contact_e,G)
```

- **Activity_E** = ATAC reads at E * H3K27ac reads at E (geometric mean of normalized signals; reflects "enhancer strength")
- **Contact_E,G** = Hi-C/Micro-C contact frequency from E to G's TSS (after distance-correction)
- **Window** = +/- 5 Mb cis (default; ENCODE-rE2G uses 1 Mb)

Threshold typical: ABC >= 0.02 for high-confidence; >= 0.01 for exploratory.

When Hi-C is unavailable, ABC uses an "average contact" averaged across 10 ENCODE Hi-C cell types as proxy (Nasser 2021); it performs comparably to cell-type-matched Hi-C. The alternative powerlaw approximation of contact-vs-distance is the Fulco 2019 fallback.

## ENCODE-rE2G Differences from ABC

ENCODE-rE2G (Gschwind et al 2023, bioRxiv) is a reformulation:

- **Logistic regression** trained on CRISPRi-FlowFISH ground truth (~10 cell types)
- **Features:** ABC score components + 3D contact + distance + activity ratios
- **Multiple feature configurations:** "abc-features", "no-hic-features" for cells without 3D data
- **Output:** Per-pair probability of regulatory connection
- **Pre-trained models** for ENCODE cell lines; logistic params vary by cell type

ENCODE-rE2G generally outperforms ABC at CRISPRi recall, especially at modest distances (50-500 kb). For ENCODE cell types, prefer ENCODE-rE2G; for novel cell types, ABC remains the default.

## Per-Tool Failure Modes

### ABC -- Wrong cell-type-matched Hi-C

**Trigger:** Using K562 Hi-C contact when actual cell type is GM12878.

**Mechanism:** Contact frequencies differ across cell types at compartment and TAD boundaries; using mismatched Hi-C produces wrong ABC scores.

**Symptom:** ABC predictions concentrate at known K562-specific loci even when ATAC data is from GM12878.

**Fix:** Use cell-type-matched Hi-C or Micro-C. If unavailable, ABC's "average HiC" (10-cell-type pooled) is the documented fallback with acknowledged degradation. Document the proxy in methods.

### ABC -- H3K27ac normalization

**Trigger:** H3K27ac ChIP-seq with different sequencing depth than ATAC.

**Mechanism:** ABC's "Activity" is the geometric mean of accessibility and H3K27ac signals; both must be normalized to the same scale.

**Symptom:** Activity scores skewed; some peaks have very high activity from H3K27ac alone, others from ATAC alone.

**Fix:** Normalize both signals to reads-per-million in peaks (RPM-IP) before combining. Use ABC's `--qnorm` flag with a quantile-normalization reference file (e.g. `--qnorm reference/EnhancersQNormRef.K562.txt` from the ABC repo).

### ENCODE-rE2G -- Cell type not in pre-trained set

**Trigger:** Running pre-trained model on a primary cell type not in CRISPRi training.

**Mechanism:** Logistic regression coefficients learned from ENCODE cell types may not transfer to primary tissues.

**Fix:** Use the closest ENCODE cell type (myeloid lineage -> K562; lymphoid -> GM12878; hepatic -> HepG2). Document the proxy. For high-stakes use, custom retraining requires CRISPRi-FlowFISH data.

### Cicero -- No Hi-C concordance benchmark

**Trigger:** Reporting Cicero connections as enhancer-gene calls without external validation.

**Mechanism:** Cicero is statistical co-accessibility; correlation with Hi-C 3D contacts is ~30-50%. Many strong Cicero connections are NOT Hi-C-validated.

**Fix:** When Hi-C is available, cross-validate; report both. When only ATAC, use Cicero with the explicit caveat that connections are co-accessibility hypotheses, not contact predictions.

### HiChIP -- Loop calling threshold

**Trigger:** Default FitHiChIP at FDR < 0.05.

**Mechanism:** HiChIP loops are abundant (10k-100k per dataset); FDR alone produces a long tail of weak loops.

**Fix:** Threshold at FDR < 0.05 AND number of contacts per loop >= 5; or use the top N most significant where N = expected number of loops based on cell type.

### EpiMap / GeneHancer -- Cell-type-agnostic limitation

**Trigger:** Using EpiMap or GeneHancer pre-computed pairs for a specific cell type.

**Mechanism:** These references aggregate across many tissues / experiments; cell-type-specific connections are diluted.

**Fix:** Use as a baseline / sanity check, not as the primary call. ABC or ENCODE-rE2G in the actual cell type is preferred.

## Decision Tree by Available Data

| Available data | Recommended method |
|---------------|--------------------|
| ATAC + H3K27ac + matched Hi-C/Micro-C | ABC or ENCODE-rE2G (with cell-type-matched contact) |
| ATAC + H3K27ac, no Hi-C | ABC with average HiC fallback; or ENCODE-rE2G `no-hic` model |
| ATAC only, no H3K27ac | Cicero (atac-seq/co-accessibility); ABC with synthetic activity |
| ATAC + H3K27ac HiChIP | FitHiChIP loops + ABC; intersect for high confidence |
| Multiome (ATAC + RNA same cell) | LinkPeaks (Signac) for direct correlation; SCENIC+ for TF networks |
| ENCODE cell type | Pre-computed ENCODE-rE2G predictions (download) |
| Tissue with limited public data | ABC + acknowledge proxy; do not rely on EpiMap |
| Multi-cell-type scATAC | scBasset (atac-seq/deep-learning-atac) for sequence-based per-cell |
| Want experimental validation | CRISPRi-FlowFISH design; use predictions as targeted hypotheses |

## ABC Standard Pipeline

**Goal:** Compute per-(enhancer, gene) ABC scores combining ATAC accessibility, H3K27ac activity, and Hi-C contact.

**Approach:** Define non-promoter candidate enhancers from ATAC peaks, run ABC neighborhoods (which counts reads directly from the ATAC/H3K27ac BAMs) to compute per-candidate activity, then run ABC predict against a Hi-C contact matrix and threshold the per-pair ABC score.

```bash
# 1. (Optional, browser tracks only) ATAC/H3K27ac bigWigs -- ABC neighborhoods below reads the BAMs directly, not bigWigs
bamCoverage --bam atac.bam --outFileName atac.bw --binSize 50 --normalizeUsing RPGC \
    --effectiveGenomeSize 2701495711 --numberOfProcessors 8

# 2. Define enhancer candidates (typically MACS narrowPeak from ATAC)
# Filter to non-promoter regions
bedtools intersect -v -a atac_peaks.narrowPeak -b promoter_regions.bed > candidate_enhancers.bed

# 3. Run ABC neighborhoods (compute Activity per candidate)
# Script path: legacy ABC = src/run.neighborhoods.py; Snakemake-based modern = workflow/scripts/run.neighborhoods.py
python /path/ABC-Enhancer-Gene-Prediction/workflow/scripts/run.neighborhoods.py \
    --candidate_enhancer_regions candidate_enhancers.bed \
    --genes refseq_protein_coding.bed \
    --H3K27ac h3k27ac.bam \
    --DHS atac.bam \
    --chrom_sizes hg38.chrom.sizes \
    --chrom_sizes_bed hg38.chrom.sizes.bed \
    --ubiquitously_expressed_genes Genes.ubiquitously_expressed.txt \
    --cellType MyCellType \
    --outdir abc_out/

# 4. Run ABC predictions (Activity * Contact) -- generates ALL unthresholded links
python /path/ABC-Enhancer-Gene-Prediction/workflow/scripts/predict.py \
    --enhancers abc_out/EnhancerList.txt \
    --genes abc_out/GeneList.txt \
    --hic_file hic_data/ \
    --hic_type avg \
    `# --hic_type choices: hic | juicebox | bedpe | avg -- must match the Hi-C input format` \
    --hic_resolution 5000 \
    --hic_pseudocount_distance 5000 \
    `# --hic_pseudocount_distance (required): powerlaw fit at this distance is added as a pseudocount (config default 5000)` \
    --chrom_sizes hg38.chrom.sizes \
    --score_column ABC.Score \
    --cellType MyCellType \
    --outdir abc_out/Predictions/

# predict.py writes EnhancerPredictionsAllPutative.tsv.gz (all unthresholded E-G links).
# 5. Threshold at ABC.Score >= 0.02. The ABC Snakemake pipeline runs filter_predictions.py with its
# full set of --output_* arguments; for a standalone cut, select by the ABC.Score column (by header):
zcat abc_out/Predictions/EnhancerPredictionsAllPutative.tsv.gz | \
    awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)if($i=="ABC.Score")c=i; print; next} $c>=0.02' \
    > abc_out/Predictions/EnhancerPredictions_thresholded.tsv
```

ABC.Score >= 0.02 is the standard threshold validated in Fulco 2019 against CRISPRi-FlowFISH; >= 0.04 is a stricter cut sometimes used in the ABC pipeline documentation for higher precision (no separate primary-paper calibration).

## ENCODE-rE2G

```bash
# Snakemake-based; clone the ENCODE-rE2G repo
git clone https://github.com/EngreitzLab/ENCODE_rE2G
cd ENCODE_rE2G

# Inputs are supplied through config/config.yaml, whose ABC_BIOSAMPLES field points to
# an ABC biosamples TSV carrying the cell type and the ATAC / H3K27ac / Hi-C paths --
# there is no cell_type=/atac_bw= --config override interface.
snakemake -j1 --use-conda

# Output: encode_e2g_predictions.tsv.gz with per-pair ENCODE-rE2G.Score and thresholded predictions
```

Pre-trained models are at https://github.com/EngreitzLab/ENCODE_rE2G/tree/main/models. Choose by tissue similarity if exact cell type not present.

## CRISPRi-FlowFISH Validation Framework

CRISPRi-FlowFISH (Fulco 2019) is the experimental gold-standard:
1. Design sgRNAs tiling each candidate enhancer
2. Transduce CRISPRi-expressing cells; FACS by gene expression (FlowFISH for endogenous; reporter for ectopic)
3. Sequence sgRNAs in low- vs high-expression bins; compute log2 enrichment per sgRNA
4. Significance: meta-test across sgRNAs in same enhancer

A 2-fold expression decrease (p < 0.05) confirms the enhancer regulates the gene.

For predictions to be publication-grade, ENCODE 4 expects:
- **Test set sensitivity / specificity** against published CRISPR enhancer-screen catalogs (Fulco 2019: K562 FlowFISH; Gasperini 2019: K562; Schraivogel 2020: K562 TAP-seq)
- **Effect-size correlation** between predicted score and observed expression effect
- **Distance bias check** (predictors over-rank close-distance pairs)

## Reconciling Methods

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| ABC and ENCODE-rE2G disagree | Different feature weighting; different training distributions | Both valid; report intersection as high-confidence |
| ABC strong, Cicero weak | Co-accessibility sparse for that cell type | Trust ABC if Hi-C is matched |
| HiChIP loop with no ABC prediction | Loop is below ABC threshold; or peak set too narrow | Lower threshold or expand candidate enhancers |
| ENCODE-rE2G high probability, no CRISPRi support | Could be context-dependent biology or false positive | Prioritize for follow-up; not a publishable claim alone |
| EpiMap pair not in ABC | Pre-computed reference is cell-type-aggregated | Use ABC for cell-type-specific |

**Operational rule for high-confidence reporting:** Predictions used for therapeutic target nomination must be (a) above ABC >= 0.02 OR ENCODE-rE2G >= 0.5, AND (b) consistent across two methods (ABC + ENCODE-rE2G or ABC + HiChIP), AND (c) validated experimentally (CRISPRi-FlowFISH preferred). Single-method high-score predictions are exploratory hypotheses.

## Combining Multiple Predictions

**Goal:** Build a high-confidence enhancer-gene set by intersecting ABC, ENCODE-rE2G, and HiChIP evidence.

**Approach:** Load each method's output, merge ABC and ENCODE-rE2G on enhancer-gene pair above per-method thresholds, then flag pairs with HiChIP loop support for triple-method evidence.

```python
import pandas as pd
abc = pd.read_csv('abc_predictions.tsv', sep='\t')
re2g = pd.read_csv('encode_re2g.tsv.gz', sep='\t')
hichip = pd.read_csv('fithichip_loops.bedpe', sep='\t', header=None,
                     names=['chr1','s1','e1','chr2','s2','e2','name','score'])

# High-confidence intersection
high_conf = abc[abc['ABC.Score'] >= 0.02].merge(
    re2g[re2g['ENCODE-rE2G.Score'] >= 0.5],
    on=['enhancer_id', 'gene'])

# Add HiChIP support flag
hichip_anchors = ...    # extract enhancer/gene pairs from HiChIP loops
high_conf['hichip_support'] = high_conf['enhancer_id'].isin(hichip_anchors)
```

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| ABC predictions concentrate at TSSs | Did not exclude promoter regions from candidates | Pre-filter `bedtools intersect -v` against promoters |
| Activity scores all very small | H3K27ac or ATAC bigWig in wrong scale | Use RPGC normalization |
| ENCODE-rE2G model not converging | Pre-trained model loaded for wrong cell type | Match training cell type via `cell_type` config |
| Cicero connections used as enhancer-gene calls | Method confusion (co-accessibility vs contact) | Switch to ABC if Hi-C available; or document as co-accessibility hypothesis |
| Hi-C resolution too coarse | Default 25 kb resolution masks fine ABC structure | Use 5 kb or 10 kb if Micro-C available |
| FitHiChIP many loops, low specificity | Default FDR alone | Add contact count threshold; or use ENCODE-rE2G HiChIP-trained model |
| GeneHancer / FANTOM5 used as primary call | Cell-type-agnostic limitation | Use as baseline only |

## References

- Fulco CP et al 2019 Nat Genet 51:1664 (ABC; CRISPRi-FlowFISH validation)
- Nasser J et al 2021 Nature 593:238 (ABC genome-wide application)
- Gschwind AR et al 2023 bioRxiv 2023.11.09.563812 (ENCODE-rE2G; encyclopedia of enhancer-gene regulatory interactions; preprint)
- Mumbach MR et al 2017 Nat Genet 49:1602 (HiChIP H3K27ac)
- Bhattacharyya S et al 2019 Nature Communications 10:4221 (FitHiChIP)
- Boix CA et al 2021 Nature 590:300 (EpiMap reference)
- Gasperini M et al 2019 Cell 176:377 (CRISPRi at scale)
- Schraivogel D et al 2020 Nat Methods 17:629 (TAP-seq targeted Perturb-seq enhancer screen, K562; scRNA-seq readout)
- Pliner HA et al 2018 Mol Cell 71:858 (Cicero co-accessibility)

## Related Skills

- atac-seq/co-accessibility - Cicero (ATAC-only enhancer-promoter inference)
- atac-seq/atac-peak-calling - Generate enhancer candidates
- atac-seq/consensus-peakset - Fixed-width enhancer regions
- atac-seq/deep-learning-atac - chromBPNet variant effect at predicted enhancers
- atac-seq/single-cell-atac - Per-cell-type scATAC inputs
- hi-c-analysis/loop-calling - Hi-C / Micro-C contact prediction
- hi-c-analysis/contact-pairs - Hi-C / Micro-C input
- chip-seq/peak-calling - H3K27ac peaks
- gene-regulatory-networks/scenic-regulons - Downstream TF -> target inference
<!-- END FILE: atac-seq/enhancer-gene-linking/SKILL.md -->

## 子目录：atac-seq/footprinting

<!-- BEGIN FILE: atac-seq/footprinting/SKILL.md -->
---
name: bio-atac-seq-footprinting
description: Detect transcription factor binding footprints in ATAC-seq using TOBIAS, HINT-ATAC, Wellington, or scprinter. Use when identifying bound TF sites within accessible regions, correcting Tn5 insertion bias before footprinting, choosing between cleavage-based and aggregate-based footprinters, or comparing differential TF activity between conditions.
tool_type: cli
primary_tool: tobias
---

## Version Compatibility

Reference examples tested with: TOBIAS 0.16+, RGT HINT-ATAC 1.0.2+, Wellington (pyDNase) 0.3+, scprinter 0.1+, samtools 1.19+, bedtools 2.31+, pyBigWig 0.3+, MEME suite 5.5+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed package and adapt rather than retrying.

# TF Footprinting

**"Identify TF binding footprints in my ATAC-seq data"** -> Detect short DNA stretches (typically 6-20 bp) of reduced Tn5 cleavage within accessible regions, where a bound TF physically protects DNA. Requires (1) Tn5 sequence-bias correction, (2) per-base footprint scoring, (3) motif-anchored detection.

- CLI: `TOBIAS ATACorrect` -> `TOBIAS ScoreBigwig` (formerly `FootprintScores`) -> `TOBIAS BINDetect`
- CLI: `rgt-hint footprinting --atac-seq` (HINT-ATAC, single-step)
- CLI: `wellington_footprints.py` (legacy DNase, adapted for ATAC)
- Python: `scprinter` (multi-scale, single-cell aware; Hu 2025 Nature)

Tn5 has a strong sequence preference (Karabacak Calviello 2019), reading approximately +/- 4 bp around the insertion site. Without bias correction, "footprints" reflect Tn5 sequence preference rather than TF binding. This is the single most important step.

## Algorithmic Taxonomy

| Tool | Bias model | Scoring | Min depth | Strength | Fails when |
|------|-----------|---------|-----------|----------|------------|
| TOBIAS (BINDetect) | +/-12 bp k-mer window (`--k_flank` 12), dinucleotide weight matrix (DWM) | Two-step: continuous footprint score then motif-anchored bound/unbound classification | >= 50M nuclear reads | Mature, peer-reviewed (Bentsen 2020), differential support, modular pipeline | Below 50M reads; sequencing errors near motif inflate background |
| HINT-ATAC | Hidden-Markov + dinucleotide bias correction | HMM emits open/footprint/closed states; calls ranked footprints | >= 50M | Single-step; integrates motif matching; handles DNase too | Less control over individual stages; HMM occasionally over-segments |
| Wellington (pyDNase) | DNase-developed; ATAC adaptation by post-shift | Cleavage-rate Poisson Z-score | >= 50M (DNase >= 80M) | Original footprinting framework; well-validated for DNase | Designed for DNase II; ATAC-specific bias not corrected as carefully |
| PIQ | Bayesian latent variable on cut sites | Genome-wide PWM scan + cleavage profile | >= 30M (lower because of model) | Per-TF posterior probabilities; works on lower depth | Outdated; not actively maintained; harder to install |
| scprinter | Multi-scale CNN-based footprint and TF activity | Resolves footprints at multiple TF size scales (CTCF vs nuclear receptors) | >= 1M cells (sc) or 50M (bulk) | Modern ML approach; single-cell; multi-scale resolves problematic TF families | Newer tool; benchmarks evolving; GPU recommended |
| TOBIAS + scprinter combination | TOBIAS bias correction + scprinter scoring | Two-step bridging | >= 50M | Combines the best bias model with multi-scale scoring | Manual pipeline, no single CLI |

Methodology evolves; verify against the current Bentsen 2020, Karabacak Calviello 2019, and scPrinter (Hu 2025) benchmarks. ATAC footprinting power saturates above 100M nuclear reads; below 50M, weak-binding TFs (transient occupancy) cannot be reliably called.

## Tn5 Bias and Why Correction Matters

**Trigger:** Tn5 inserts preferentially at certain k-mers (Karabacak Calviello 2019 measured the protocol-specific 6-mer insertion-bias model used for bias correction). The preference is reproducible and biologically uninteresting.

**Mechanism:** Without correction, every "TF footprint" near a high-bias k-mer reads as occupancy. Conversely, regions with low-bias flanks but real binding may show no footprint dip relative to corrected expectation.

**Symptom:** Aggregate footprint at random GC-rich motifs shows V-shape; aggregate at AT-rich motifs shows inverse-V (peak instead of dip).

**Fix:** Apply ATACorrect (TOBIAS), seqOutBias (Martins 2018), or HINT's dinucleotide model. Bias correction subtracts the Tn5-expected per-base profile from observed cleavage. After correction, V-shape is preserved only at TF-bound sites.

**Goal:** Subtract Tn5 sequence-bias from the per-base cleavage signal so residual footprints reflect TF binding rather than enzyme preference.

**Approach:** Run TOBIAS ATACorrect over the deduplicated BAM with the reference genome, consensus peaks, and ENCODE blacklist; it emits per-condition uncorrected, bias, expected, and corrected bigWigs for downstream scoring.

```bash
# TOBIAS ATACorrect: produces uncorrected, bias, expected, and corrected bigWigs
TOBIAS ATACorrect \
    --bam sample.dedup.bam \
    --genome hg38.fa \
    --peaks consensus_peaks.bed \
    --blacklist hg38-blacklist.v2.bed \
    --outdir corrected/ \
    --cores 8
# Output: sample_uncorrected.bw, sample_bias.bw, sample_expected.bw, sample_corrected.bw
```

## Tn5 Cut Geometry: +4 / -5 Dual-Cut

Tn5 dimers cut both strands of DNA but with a 9 bp staggered offset. The cleavage event creates two free 5' ends: one shifted +4 bp from the binding center on the forward strand and -5 bp on the reverse strand. Footprinting tools must apply this shift before per-base counting:

| Strand | Read 5' end correction |
|--------|------------------------|
| + strand | shift +4 bp downstream |
| - strand | shift -5 bp upstream |

**Trigger:** Computing per-base Tn5 cut signal manually.

**Symptom:** Footprint aggregates show ~9 bp asymmetry (apex shifted from motif center).

**Fix:** Apply +4/-5 shift before counting; TOBIAS, HINT-ATAC, and scprinter handle this internally. Custom analyses must apply explicitly. deepTools provides this via `alignmentSieve --ATACshift` (which applies the canonical +4 / -5 shift in one step).

## Bias Correction Alternatives

| Method | Approach | When to use |
|--------|---------|-------------|
| TOBIAS ATACorrect | +/-12 bp k-mer window, dinucleotide weight matrix (DWM) | Default for most ATAC; fast |
| chromBPNet bias model (Pampari 2024) | CNN trained on naked-DNA control or k-mer baseline | Best when sequence context complex; handles low-complexity flanks |
| seqOutBias (Martins 2018) | Genome-wide k-mer frequency scaling (observed vs expected cut counts) | Independent of footprinting tool; works upstream |
| HINT-ATAC dinucleotide | HMM-integrated dinucleotide bias | Built into HINT pipeline; less control |
| Naked-DNA empirical | Sequence Tn5 on protein-free DNA | Gold standard for non-model organisms; expensive wet-lab |

For non-model organisms (no published Tn5 bias model), naked-DNA control is required. chromBPNet's bias model is the modern standard for human/mouse and outperforms TOBIAS at low-complexity sequence contexts (Pampari 2024). See atac-seq/deep-learning-atac.

## In Silico Variant Effect at Footprinted TF Motifs

**Trigger:** A GWAS-fine-mapped or rare variant falls inside a TOBIAS-bound motif site.

**Mechanism:** Sequence-based DL models (chromBPNet, Enformer) predict per-base accessibility at ref vs alt allele; combined with footprint evidence (TOBIAS bound site overlap), this produces a mechanistic hypothesis: "variant disrupts binding of TF X at enhancer Y."

**Workflow:** Run TOBIAS BINDetect to identify bound motif sites; for variants in bound sites, score with chromBPNet (atac-seq/deep-learning-atac) for ref/alt log2FC; |log2FC| > 1 supports functional disruption. Cross-reference with allele-specific accessibility (atac-seq/allele-specific-accessibility) for observed evidence.

## Per-TF Footprinting Failure Modes

Different TF families produce different footprint signatures. The same tool can report a clean V-shape for one family and noise for another.

### CTCF -- The gold standard

**Trigger:** Footprinting CTCF.

**Mechanism:** CTCF has high ChIP-seq concordance, deep V-shaped footprint (~19-20 bp protected), strong sequence specificity. ChIP-seq overlap is typically >70%.

**Symptom:** Aggregate corrected footprint shows clean ~20 bp dip with bilateral cleavage shoulders.

**Verification:** Always validate footprinting output by checking CTCF first; if CTCF footprint is shallow, the bias correction or depth is the problem, not the biology.

### Nuclear receptors (ER, AR, GR) -- Transient binding

**Trigger:** Glucocorticoid response, hormone-stimulated systems.

**Mechanism:** Steroid receptors bind transiently (residence time minutes vs hours for CTCF); average ATAC sample captures binding probability < 30% per allele.

**Symptom:** Aggregate footprint is shallow or absent despite ChIP-seq peaks at the same sites.

**Fix:** Use scprinter's multi-scale model OR limit to ChIP-validated sites OR pool replicates for higher effective depth. Do not interpret absence of footprint as absence of binding.

### Pioneer TFs (FOXA1, GATA, OCT4) -- Half-site footprint

**Trigger:** Pioneer-factor binding to nucleosomal DNA.

**Mechanism:** Pioneer factors bind one DNA face; the back face is on the histone octamer. Footprint is asymmetric (one side protected, other side accessible).

**Symptom:** Aggregate plot shows asymmetric V; one shoulder is taller than the other.

**Fix:** Use single-stranded scoring; HINT-ATAC has stranded mode. Treat asymmetric footprints as biologically meaningful, not artefactual.

### AP-1 family (FOS, JUN) -- Heterodimer composite footprint

**Trigger:** AP-1 enrichment; the JASPAR motif is composite of multiple heterodimer combinations.

**Mechanism:** Different AP-1 dimers (FOS+JUN, FOS+JUNB, JUNB+JUNB) bind slightly different motifs. JASPAR entries are degenerate; scoring averages over all.

**Fix:** Use specific HOCOMOCO motifs per heterodimer when distinguishing matters. Otherwise accept the composite call.

### ZBTB family / BTB-zinc finger -- Dynamic / unfootprintable

**Trigger:** Footprinting ZBTB16, BCL6, others.

**Mechanism:** Dynamic binding kinetics + cofactor-mediated stabilization mean steady-state occupancy is highly variable. Some ZBTBs simply do not produce reliable ATAC footprints despite genuine ChIP-seq binding.

**Fix:** Document the failure; use ChIP-seq for these TFs. Footprinting cannot rescue everything.

### Forkhead / homeobox (FOX, HOX) -- Short footprint < 8 bp

**Trigger:** Short-motif TFs.

**Mechanism:** Footprint extent matches motif length; <8 bp footprints are at the resolution limit of Tn5 (which has ~4 bp positional uncertainty).

**Fix:** Multi-scale scoring (scprinter); aggregate over thousands of sites; do not rely on per-site calls for short motifs.

## Decision Tree by Goal

| Goal | Recommended pipeline |
|------|---------------------|
| Identify all TFs differentially bound between two conditions | TOBIAS ATACorrect (per condition) -> ScoreBigwig -> BINDetect with `--cond_names` |
| Find the strongest single-TF binding (e.g., CTCF) | TOBIAS PlotAggregate over JASPAR CTCF motif sites; verify V-shape |
| Per-cell footprinting (scATAC) | scprinter (single-cell mode); avoid TOBIAS unless pseudobulking by cluster |
| Multi-scale TF activity (handle short and long simultaneously) | scprinter or TOBIAS + custom multi-scale | 
| Differential nuclear-receptor binding | TOBIAS pooled-replicate footprints + ChIP cross-validation; raw ATAC alone often misses transient binding |
| Plant / non-model organism | TOBIAS or HINT-ATAC with custom motifs; bias model retrained from genomic background |

## TOBIAS Three-Step Pipeline

**Goal:** Call bound/unbound TF motif sites per condition and detect differential occupancy across two conditions.

**Approach:** Run ATACorrect to subtract Tn5 bias from cleavage counts, ScoreBigwig to compute a continuous per-base footprint score, then BINDetect to anchor footprints to motif positions and produce per-TF differential bound calls with p-values.

```bash
# Step 1: Bias correction
TOBIAS ATACorrect \
    --bam cond1.bam --genome hg38.fa \
    --peaks consensus.bed --blacklist hg38-blacklist.v2.bed \
    --outdir cond1_corrected/ --cores 16

# Step 2: Per-base footprint scoring (continuous)
TOBIAS ScoreBigwig \
    --signal cond1_corrected/cond1_corrected.bw \
    --regions consensus.bed \
    --output cond1_footprints.bw \
    --cores 16

# Step 3: Motif-anchored bound/unbound calls + differential
TOBIAS BINDetect \
    --motifs JASPAR2024_CORE_vertebrates.pfm \
    --signals cond1_footprints.bw cond2_footprints.bw \
    --genome hg38.fa --peaks consensus.bed \
    --outdir bindetect/ \
    --cond_names cond1 cond2 \
    --cores 16
```

BINDetect output columns: `output_prefix`, motif info, condition counts (`cond1_bound`, `cond2_bound`), `cond1_mean_score`, `cond2_mean_score`, `cond1_cond2_change` (differential), `cond1_cond2_pvalue` (one-sided per direction).

## Differential Reading

| BINDetect output | Interpretation |
|------------------|----------------|
| `cond1_cond2_change` > 0, low pvalue | TF more bound in cond1 |
| `cond1_cond2_change` < 0, low pvalue | TF more bound in cond2 |
| Both `cond1_bound` and `cond2_bound` near 0 | Motif present but no footprint either condition; TF likely not active |
| `cond1_bound` >> `cond2_bound` but change small | High dynamic range; differential per-site rather than aggregate |

The differential score is the difference in mean footprint score across motif sites, not a fold-change. Magnitudes around 0.1-0.5 are typical for biologically relevant changes (TOBIAS BINDetect tutorials / Bentsen 2020 examples; no formally published cutoff -- calibrate against positive controls in the current dataset).

## Reconciling TOBIAS vs HINT-ATAC

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| TOBIAS calls binding, HINT does not | TOBIAS more sensitive; HINT's HMM filters edge calls | Trust if motif is canonical; suspect for novel/weak motifs |
| HINT calls binding, TOBIAS does not | HINT's HMM occasionally over-segments and reports spurious | Verify by aggregate footprint at the called sites |
| Both call same TF as differential but opposite directions | Different bias correction model; different bound/unbound thresholds | Re-check ATACorrect output; one bias model may be miscalibrated |
| Both flat | Library too shallow; chromatin too closed at motif sites | Pool replicates; consider scprinter multi-scale |

**Operational rule:** For high-confidence reporting, require two-tool concordance (TOBIAS + HINT-ATAC OR TOBIAS + ChIP-seq overlap > 50%). Single-tool calls should be reported as exploratory.

## NFR-Filtering Before Footprinting

**Goal:** Restrict footprinting input to nucleosome-free (sub-100 bp) fragments where TF binding signal lives.

**Approach:** Stream the BAM through awk, keep header lines and fragments whose insert size is between -100 and 100 bp, then re-index.

```bash
# Filter to fragments < 100 bp (NFR) -- TF binding lives here, not on nucleosomes
samtools view -h sample.bam | \
    awk 'substr($0,1,1)=="@" || ($9 > 0 && $9 < 100) || ($9 < 0 && $9 > -100)' | \
    samtools view -b > sample.nfr.bam
samtools index sample.nfr.bam
# Use this NFR BAM as input to TOBIAS ATACorrect
```

Filtering NFR strengthens footprint signal but discards di-nucleosome-borne information. Keep the unfiltered BAM for nucleosome-positioning analysis.

## Motif Database Choice

| Database | Coverage | Format | Notes |
|----------|---------|--------|-------|
| JASPAR 2024 CORE vertebrates | ~880 vertebrate non-redundant motifs (curated, experimentally derived) | JASPAR PFM, MEME, etc. | Default for vertebrate ATAC |
| HOCOMOCO v12 | ~1443 curated motifs (v12 CORE) | JASPAR PFM | Best for resolving paralogues; provides secondary motif subtypes per TF |
| CIS-BP 2.0 | ~80,000 motifs across 1000+ species | PWM, .meme | Broadest coverage including non-model species |
| MEME-CHIP / homer | Custom from peaks | .meme, .motif | When de novo motif needed |

JASPAR motifs are conservatively curated; HOCOMOCO is comprehensive for human/mouse with quality scores per motif (A/B/C/D); CIS-BP excels for non-model organisms.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Aggregate footprint inverted (peak instead of dip) | No bias correction; or wrong genome FASTA | Run ATACorrect; verify FASTA matches BAM build |
| BINDetect reports zero bound sites | Default cutoff too stringent; or peakset too narrow | Raise `--bound-pvalue` (default 0.001) and inspect; verify peaks include where binding expected |
| TOBIAS ATACorrect out of memory | Genome FASTA huge or many cores | Reduce `--cores`; use `samtools faidx` to confirm FASTA index exists |
| Differential score noisy / random | Per-condition bias correction inconsistent | Re-run ATACorrect with identical peakset and blacklist for each |
| Empty motif file warning | JASPAR PFM format mismatch | Use `MEME suite` to convert; TOBIAS expects JASPAR format |
| HINT-ATAC reports many tiny footprints | Default HMM over-segments | Use `--organism` flag explicitly; check `--region-file` is consensus, not raw peaks |
| Wellington crashes on paired-end ATAC | Wellington was DNase-targeted, single-end model | Use TOBIAS instead, or convert paired-end to cuts-only BED |
| Per-site footprint is V-shape but aggregate is flat | Mixing strands; some motifs on - strand | Aggregate function should handle strand; verify input motif strand column |

## References

- Buenrostro JD et al 2013 Nat Methods 10:1213 (ATAC-seq protocol)
- Karabacak Calviello A et al 2019 Genome Biol 20:42 (protocol-specific Tn5/DNase bias modeling for footprinting)
- Bentsen M et al 2020 Nat Commun 11:4267 (TOBIAS framework, benchmark)
- Li Z et al 2019 Genome Biol 20:45 (HINT-ATAC)
- Piper J et al 2013 NAR 41:e201 (Wellington / pyDNase)
- Sherwood RI et al 2014 Nat Biotechnol 32:171 (PIQ)
- Hu Y et al 2025 Nature 638:779 (scPrinter/PRINT; multi-scale single-cell footprinting)
- Martins AL et al 2018 NAR 46:e9 (seqOutBias bias correction alternative)
- Castro-Mondragon JA et al 2022 NAR 50:D165 (JASPAR 2022, recently 2024)
- Vorontsov IE et al 2024 NAR 52:D154 (HOCOMOCO v12)

## Related Skills

- atac-seq/atac-peak-calling - Generate input peakset (NFR-only optional)
- atac-seq/atac-qc - Confirm depth >= 50M before footprinting
- atac-seq/single-cell-atac - scprinter for single-cell footprinting
- atac-seq/motif-deviation - Complementary chromVAR for accessibility variability
- atac-seq/deep-learning-atac - chromBPNet bias correction alternative; in silico variant effect at footprints
- atac-seq/allele-specific-accessibility - Observed allelic imbalance at TF-bound sites
- chip-seq/peak-annotation - Cross-validate footprints with ChIP peaks
- sequence-manipulation/motif-search - Underlying motif scanning patterns
- gene-regulatory-networks/scenic-regulons - Downstream regulatory network inference
<!-- END FILE: atac-seq/footprinting/SKILL.md -->

## 子目录：atac-seq/motif-deviation

<!-- BEGIN FILE: atac-seq/motif-deviation/SKILL.md -->
---
name: bio-atac-seq-motif-deviation
description: Analyze TF motif accessibility variability across samples or single cells using chromVAR. Use when identifying TF motifs whose accessibility correlates with conditions, computing per-sample motif z-scores after matched background correction, comparing to ArchR / Signac equivalents, or distinguishing motif-accessibility signal from per-site footprinting.
tool_type: r
primary_tool: chromVAR
---

## Version Compatibility

Reference examples tested with: chromVAR 1.24+, motifmatchr 1.24+, JASPAR2024 0.99+, TFBSTools 1.40+, BSgenome.Hsapiens.UCSC.hg38 1.4+, SummarizedExperiment 1.32+, limma 3.58+, ggplot2 3.5+, Matrix 1.6+, ArchR 1.0.2+, Signac 1.13+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws unexpected errors, introspect the installed package and adapt rather than retrying.

# Motif Deviation (chromVAR)

**"Which TF motifs explain accessibility variation across my samples or cells?"** -> Compute per-sample (or per-cell) deviation z-scores: how many standard deviations above expectation each TF motif's accessibility falls, controlling for GC content and overall accessibility via matched background peak sets.

- R: `chromVAR::computeDeviations(counts, motifs)` -> per-sample z-scores
- R: `chromVAR::computeVariability(dev)` -> per-motif variance ranking
- Single-cell alternative: `Signac::RunChromVAR()` (wrapper with matched defaults) or `ArchR::addDeviationsMatrix()`

chromVAR answers a different question than footprinting: footprinting asks "is this specific motif site bound?", chromVAR asks "do peaks containing this motif have systematically more or less accessibility than expected?" The two are complementary.

## What chromVAR Computes

For each (motif, sample) pair:
- **Raw deviation** = Sum of accessibility at peaks containing the motif - expected from a matched-GC, matched-accessibility background.
- **Bias-corrected deviation** = Raw deviation / SD of background deviations.
- **Z-score** = (corrected deviation - mean across cells) / SD across cells. Reported as the principal output.

Z-scores are signed: positive = motif more accessible in this sample than population average; negative = less. Magnitudes 2-5 are typical for biologically interesting motifs; >5 indicates strong covariation with sample state.

## Algorithmic Taxonomy

| Tool | Input | Background | Output | Best for | Fails when |
|------|-------|------------|--------|----------|------------|
| chromVAR | Peak count matrix + motif annotations | Matched GC + accessibility (50 peaks per match by default) | Per-sample motif z-score | Bulk + single-cell (sparse-aware); cross-sample variability | < 1500 reads/sample (bulk) or < 500 cells/cluster (sc); too few peaks (< 5000) |
| Signac::RunChromVAR | Seurat single-cell ATAC object | Same as chromVAR (delegated) | Motif assay in Seurat object | Standard single-cell workflows in Seurat ecosystem | Same as chromVAR; needs Seurat object setup |
| ArchR::addDeviationsMatrix | ArrowFile + tile/peak matrix | ArchR's getBgdPeaks (matched on GC + log accessibility) | Per-cell deviation matrix in ArchR project | ArchR ecosystem; faster on large scATAC | ArchR-specific format; not portable to chromVAR objects |
| Signac::FindMarkers (with motifs as features) | Motif accessibility matrix from RunChromVAR | Per-cell-cluster | Differential motifs per cluster | Cluster-level differential | Differential test must be on z-scores; raw counts will mislead |
| TF activity inference (DecoupleR / SCENIC+) | Gene expression + motif activity | Multi-modal | TF activity score | Multi-omics integration | Requires paired RNA-seq; chromVAR alone is insufficient |

Methodology evolves; verify against current chromVAR (Schep 2017), ArchR (Granja 2021), and Signac (Stuart 2021) benchmarks before locking pipelines.

## chromVAR vs Footprinting -- Different Questions

| Question | Tool |
|----------|------|
| Does the bulk pattern of motif-containing peaks vary with condition? | chromVAR |
| Is THIS specific motif site bound by a TF? | TOBIAS / HINT-ATAC |
| Per-cell TF activity in scATAC | chromVAR (via Signac/ArchR) |
| Per-cell TF binding at specific sites | scprinter |
| TF activity correlated with gene expression | chromVAR + co-expression OR SCENIC+ |
| Which TF families distinguish my cell clusters? | chromVAR per-cluster z-scores |
| Differential bound vs unbound between conditions | TOBIAS BINDetect |

chromVAR is fundamentally a *summary statistic* over many motif sites. Footprinting is per-site classification. Use chromVAR when motif site count >> 100; use footprinting when specific sites matter.

## Per-Tool Failure Modes

### chromVAR -- Too few peaks or too few reads

**Trigger:** ATAC peakset < 5000 peaks; per-sample read depth < 1500 in peaks.

**Mechanism:** chromVAR's background sampling requires enough peaks to find matched GC + accessibility partners. Sparse sampling at low peak count creates correlated null distributions, inflating both positive and negative z-scores.

**Symptom:** Variability scores all > 5 (suspiciously high); top variable motifs are dominated by AT-rich or GC-rich sequences regardless of biology.

**Fix:** Verify peakset is at full ATAC scale (typically 50k-200k peaks). For sc ATAC, aggregate cells to clusters of >= 500 cells before running.

### chromVAR background peaks -- Default is good, custom requires care

**Trigger:** Calling `getBackgroundPeaks()` with non-default `niterations` or `bias`.

**Mechanism:** Default `niterations=50` yields 50 matched background peaks per foreground peak. Reducing `niterations` increases noise; increasing slows linearly without much accuracy gain.

**Symptom:** Custom backgrounds inflate variability when niterations < 30.

**Fix:** Stick to defaults unless benchmarking. If running on huge cell counts, test on subsample first.

### chromVAR on broadly accessible cell types -- Z-scores compressed

**Trigger:** Multiple cell types in dataset have very different overall accessibility magnitudes.

**Mechanism:** chromVAR's correction normalizes for total accessibility; cell types with high background accessibility have compressed z-scores even if their motif-specific signal is strong.

**Symptom:** PCA on z-scores does not separate cell types as cleanly as raw counts.

**Fix:** Run chromVAR per-cell-type-cluster (separate runs) when global accessibility differs by > 5x. Alternatively use ArchR's per-cluster background.

### chromVAR on bulk samples without enough variation -- All z-scores near zero

**Trigger:** All bulk samples are technical replicates or very similar.

**Mechanism:** Z-scores normalize across the sample population; if there is no across-sample variability, all z-scores collapse to zero.

**Symptom:** Variability ranking is unstable across runs; top motifs change.

**Fix:** chromVAR is designed for variability; if the dataset has only one biological condition replicated, use footprinting or differential accessibility instead. chromVAR needs 6+ samples with biological variation to be informative.

### Signac::RunChromVAR -- Motif matching mismatch

**Trigger:** Motif assay added before peak set finalized; peak coordinates change.

**Mechanism:** RunChromVAR matches motifs to peaks at the time it's called; if peaks change downstream (e.g., after merge), the motif annotations become stale.

**Symptom:** Some peaks have NA motif annotations; deviation matrix has missing entries.

**Fix:** Run `AddMotifs()` -> `RunChromVAR()` AFTER finalizing peakset. Re-run if peaks change.

### ArchR::addDeviationsMatrix -- TileMatrix vs PeakMatrix

**Trigger:** Calling on tile matrix when peak matrix is more appropriate.

**Mechanism:** ArchR can compute deviations on either tiles (regular bins) or peaks. Peaks are biologically meaningful; tiles add noise from intergenic background.

**Fix:** Use `matrixName='PeakMatrix'` after addReproduciblePeakSet. Tile-based deviations are mainly for embedding, not biology.

## Decision Tree by Setting

| Setting | Workflow |
|---------|---------|
| Bulk, 6+ samples, condition contrast | chromVAR + limma differential on z-scores; rank by FDR |
| Bulk, 3-5 samples | chromVAR; report variability ranking; differential underpowered |
| scATAC, Signac ecosystem | Signac AddMotifs + RunChromVAR; FindMarkers on motif assay |
| scATAC, ArchR ecosystem | ArchR addPeakMatrix + addDeviationsMatrix + getMarkerFeatures |
| Multimodal scATAC + scRNA | chromVAR + paired DE; consider SCENIC+ for TF -> target inference |
| Plant / non-model organism | chromVAR with custom motif PFM (from CIS-BP); custom BSgenome |
| Time-course bulk (5+ time points) | chromVAR z-scores -> spline regression on time; identify motifs with non-monotone trajectories |

## chromVAR Workflow (Bulk)

**Goal:** Compute per-sample TF-motif accessibility z-scores corrected for GC bias and total signal.

**Approach:** Build a SummarizedExperiment from peak counts, add GC bias, filter sparse samples and peaks, match JASPAR motifs to peaks, sample matched background peaks, then compute deviations and per-motif variability.

```r
library(chromVAR); library(motifmatchr); library(BSgenome.Hsapiens.UCSC.hg38)
library(JASPAR2024); library(TFBSTools); library(SummarizedExperiment)

peaks <- rtracklayer::import('consensus_peaks.bed')           # GRanges
counts <- as.matrix(read.delim('peak_counts.tsv', row.names=1))    # rows = peaks, cols = samples
se <- SummarizedExperiment(assays=list(counts=counts), rowRanges=peaks)
se <- addGCBias(se, genome=BSgenome.Hsapiens.UCSC.hg38)

# Filter: depth >= 1500 reads/sample, FRiP >= 0.15; drop peaks with < 10 total fragments
se <- filterSamples(se, min_depth=1500, min_in_peaks=0.15, shiny=FALSE)
se <- filterPeaks(se, non_overlapping=TRUE, min_fragments_per_peak=10)

# Motifs: JASPAR vertebrate CORE (default for human/mouse)
# JASPAR2024 + TFBSTools incompatibility (TFBSTools issue #39): getMatrixSet does not dispatch on the
# JASPAR2024 object directly. Open the SQLite handle and pass that to getMatrixSet instead.
library(RSQLite)
jaspar2024 <- JASPAR2024::JASPAR2024()
sq <- dbConnect(SQLite(), db(jaspar2024))
pfm <- getMatrixSet(sq, opts=list(collection='CORE', tax_group='vertebrates'))
# JASPAR2020 (older) accepts the package object directly: getMatrixSet(JASPAR2020, opts=...)
motif_ix <- matchMotifs(pfm, se, genome=BSgenome.Hsapiens.UCSC.hg38, p.cutoff=5e-05)

# Background peaks: matched GC + accessibility (default 50 iterations is fine)
bg <- getBackgroundPeaks(object=se, niterations=50)

# Compute deviations
dev <- computeDeviations(object=se, annotations=motif_ix, background_peaks=bg)
zscores <- deviationScores(dev)         # motif x sample matrix of z-scores (deviations() returns raw bias-corrected deviations)
variability <- computeVariability(dev) # per-motif variability ranking
```

## Differential Motif Activity (limma on z-scores)

**Goal:** Identify TF motifs whose chromVAR z-scores differ significantly between conditions.

**Approach:** Build a contrast design matrix, fit limma's linear model on the motif-x-sample z-score matrix with empirical Bayes moderation, and pull motifs at adjusted p < 0.05.

```r
library(limma)
groups <- factor(colData(se)$condition, levels=c('control', 'treated'))
design <- model.matrix(~groups)
fit <- lmFit(zscores, design); fit <- eBayes(fit)
diff_motifs <- topTable(fit, coef=2, number=Inf, p.value=0.05)   # adj.P.Val column
```

Use `adj.P.Val` (limma's BH FDR), not `FDR` (which limma does not return). `logFC` is the difference in z-scores between groups; magnitudes 0.5-2 typical.

## chromVAR for Single-Cell ATAC (Signac)

**Goal:** Compute per-cell TF-motif z-scores in a Seurat scATAC workflow and call cluster-marker motifs.

**Approach:** Open the JASPAR2024 SQLite handle, attach motifs to the Seurat object via AddMotifs, run RunChromVAR to build the chromvar assay, then call FindAllMarkers with mean.fxn=rowMeans for z-score-appropriate differential.

```r
library(Signac); library(Seurat); library(JASPAR2024); library(TFBSTools)
library(BSgenome.Hsapiens.UCSC.hg38); library(RSQLite)

# Assume `seurat_obj` has an ATAC assay with consensus peaks
# JASPAR2024 + TFBSTools workaround (see TFBSTools issue #39):
jaspar2024 <- JASPAR2024::JASPAR2024()
sq <- dbConnect(SQLite(), db(jaspar2024))
pfm <- getMatrixSet(sq, opts=list(collection='CORE', tax_group='vertebrates'))
seurat_obj <- AddMotifs(seurat_obj, genome=BSgenome.Hsapiens.UCSC.hg38, pfm=pfm)
seurat_obj <- RunChromVAR(seurat_obj,
                          genome=BSgenome.Hsapiens.UCSC.hg38,
                          new.assay.name='chromvar')
DefaultAssay(seurat_obj) <- 'chromvar'

# Per-cluster differential motifs.
# `mean.fxn` is the standard FindAllMarkers/FindMarkers control for the per-feature summary.
# `fc.name` controls the output column name and is accepted by Seurat 4.x/5.x; if it errors,
# fall back to renaming the output column post-hoc.
markers <- FindAllMarkers(seurat_obj, only.pos=TRUE, mean.fxn=rowMeans, fc.name='avg_diff')
```

`mean.fxn=rowMeans` is required for z-score-style data; the default fold-change function (designed for log-counts) makes no sense on chromVAR z-scores.

## chromVAR for Single-Cell ATAC (ArchR)

**Goal:** Compute per-cell TF-motif deviations and per-cluster marker motifs within the ArchR ecosystem.

**Approach:** Build the reproducible peakset, attach motif annotations from CIS-BP, sample matched background peaks, run addDeviationsMatrix to score motif z-scores, and call getMarkerFeatures on the MotifMatrix per cluster.

```r
library(ArchR)
proj <- addReproduciblePeakSet(proj, groupBy='Clusters', pathToMacs2='/path/macs2')
proj <- addPeakMatrix(proj)
proj <- addMotifAnnotations(proj, motifSet='cisbp', name='Motif')
proj <- addBgdPeaks(proj)
proj <- addDeviationsMatrix(proj, peakAnnotation='Motif')

# Per-cluster deviation summary
markersMotifs <- getMarkerFeatures(proj, useMatrix='MotifMatrix',
                                   groupBy='Clusters', useSeqnames='z')
```

ArchR uses `cisbp` by default (CIS-BP database, ~5000 motifs); switch to `JASPAR2020` for fewer, more curated motifs.

## Reconciling chromVAR vs ArchR vs Signac

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Top variable motifs disagree | Different motif databases (JASPAR vs CIS-BP) | Re-run with matched motif set |
| Z-scores correlate but magnitudes differ | Different background sampling | Inspect per-tool background; defaults are similar but not identical |
| Signac chromvar assay has NA values | Motifs added after peakset finalized | Re-run AddMotifs + RunChromVAR after peaks are stable |
| ArchR per-cluster signature differs from Signac | Different clustering; different cell membership | Standardize clustering before comparison |

**Operational rule:** chromVAR z-scores are tool-specific. For cross-study comparison, recompute on the same peakset with the same motif database; do not use stored z-scores from heterogeneous sources directly.

## Variability Score Interpretation

| Variability | Z-score range typical | Interpretation |
|-------------|----------------------|----------------|
| < 1 | -1 to +1 | Motif activity ~constant; not biologically variable |
| 1-2 | -2 to +2 | Modest variation; condition-driven possible |
| 2-5 | -3 to +5 | Strong cross-sample / cross-cluster variability; biologically interesting |
| > 5 | -5 to +10 | Major driver of cell-state differences; flagship hits |

Variability is the across-sample variance of z-scores; it ranks motifs without requiring condition labels. For unsupervised TF discovery (e.g., trajectory analysis) variability is the primary metric.

## Background Peak Matching Mathematics

**Trigger:** Tuning chromVAR's `getBackgroundPeaks` parameters; benchmarking against published results.

**Mechanism:** chromVAR matches each foreground peak to background peaks by GC content + total accessibility, using a bin size `bs` (default 50). For each foreground peak, the algorithm samples `niterations` (default 50) replacement peaks from the matching bins. Variance across these matched samples becomes the null reference.

**Threshold tuning:**
- **bs=50** (default): the GC/accessibility bin granularity; works for typical peaksets. For very small peaksets (< 2,000 peaks), lower `bs` to avoid empty bins.
- **niterations=50** (default): 50 matched background peaks per foreground peak. Reducing below 30 inflates noise; increasing above 100 yields diminishing returns.

For non-canonical genomes (mouse mm10 with different GC distribution), consider rebuilding bins manually with `quantile()` to ensure equal-sized bins.

## chromVAR vs scBasset for Single-Cell

| Tool | Approach | Best for | Limitation |
|------|---------|----------|------------|
| chromVAR | Matched-background z-score per motif | Standard sc workflow; integrated in Signac/ArchR | Linear; no sequence context beyond motif PWM |
| scBasset (Yuan & Kelley 2022) | Sequence CNN with per-cell projection | Higher cluster-discrimination accuracy than chromVAR; predicts cell states from sequence | Newer; ecosystem smaller; needs >= 100 cells per cluster for stable projection |
| Enformer-derived TF activity | Long-context Transformer | Cross-cell-type TF activity prediction; distal regulation | Pre-trained models cell-type-specific |
| DecoupleR ULM/MLM (Badia-i-Mompel 2022) | Multi-method consensus TF activity scoring | Multi-omics integration; aggregation across motif databases | Requires careful cell-x-motif input matrix |

For high-stakes per-cell TF activity, run chromVAR + scBasset and report the intersection. See atac-seq/deep-learning-atac for scBasset details.

## DecoupleR Multi-Method TF Activity

```python
import decoupler as dc   # 1.x API shown (pip install 'decoupler<2'); decoupler 2.x renamed these to dc.mt.ulm / dc.mt.mlm / dc.mt.consensus
# adata: AnnData with motif_x_cell deviation matrix as input
acts_ulm = dc.run_ulm(mat=adata.obsm['chromvar'], net=collectri_net,
                      source='source', target='target')
acts_mlm = dc.run_mlm(mat=adata.obsm['chromvar'], net=collectri_net,
                      source='source', target='target')
acts_consensus = dc.run_consensus(mat=adata.obsm['chromvar'], net=collectri_net)
```

DecoupleR aggregates multiple TF-activity inference methods (ULM, MLM, viper, GSVA, etc.). The consensus output is more robust than any single method to motif database biases.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `Error in addGCBias`: missing `seqlengths` | GRanges object lacks chrom sizes | Use `seqlengths(peaks) <- seqlengths(genome)` first |
| All z-scores near zero | Too few samples or too little variation | chromVAR requires biological variation; use footprinting or differential instead |
| `getBackgroundPeaks` slow | Default niterations and large peakset | Default is fine; do not reduce iterations below 30 |
| Differential motifs all significant | FDR not applied; or compared identical samples | Apply BH correction; verify groups are correct |
| Signac chromvar assay all zero | RunChromVAR called before peakset | Re-run after AddMotifs and peakset stability |
| FindAllMarkers reports `avg_log2FC` for chromvar | Default fc method incorrect for z-scores | Use `mean.fxn=rowMeans` and `fc.name='avg_diff'` |
| z-score interpretation flipped | Sign of contrast reversed | Verify factor level order; first level is reference |
| ArchR `cisbp` vs `JASPAR2020` results differ | Different motif databases | Choose one and report the choice |

## References

- Schep AN et al 2017 Nat Methods 14:975 (chromVAR)
- Granja JM et al 2021 Nat Genet 53:403 (ArchR)
- Stuart T et al 2021 Nat Methods 18:1333 (Signac)
- Aibar S et al 2017 Nat Methods 14:1083 (SCENIC; downstream TF target inference)
- Bravo Gonzalez-Blas C et al 2023 Nat Methods 20:1355 (SCENIC+)
- Castro-Mondragon JA et al 2022 NAR 50:D165 (JASPAR 2022)
- Rauluseviciute I et al 2024 NAR 52:D174 (JASPAR 2024)
- Weirauch MT et al 2014 Cell 158:1431 (CIS-BP)
- Vorontsov IE et al 2024 NAR 52:D154 (HOCOMOCO v12)

## Related Skills

- atac-seq/footprinting - Per-site TF binding (different question)
- atac-seq/differential-accessibility - Peak-level DA (alternative approach)
- atac-seq/single-cell-atac - sc workflow integration with Signac/ArchR
- atac-seq/co-accessibility - Cis-regulatory connections
- atac-seq/deep-learning-atac - scBasset / Enformer alternative
- gene-regulatory-networks/scenic-regulons - Downstream TF -> target inference
- chip-seq/motif-analysis - Alternative motif-enrichment approaches
- single-cell/clustering - Inputs for per-cluster motif activity
<!-- END FILE: atac-seq/motif-deviation/SKILL.md -->

## 子目录：atac-seq/nucleosome-positioning

<!-- BEGIN FILE: atac-seq/nucleosome-positioning/SKILL.md -->
---
name: bio-atac-seq-nucleosome-positioning
description: Map nucleosome center positions, occupancy, and fuzziness from ATAC-seq fragment-size patterns using NucleoATAC, ATACseqQC, DANPOS3, or scprinter. Use when characterizing nucleosome organization at promoters and enhancers, calling +1/-1 nucleosomes flanking NFRs, generating V-plots for chromatin structure visualization, or comparing nucleosome positioning between conditions.
tool_type: mixed
primary_tool: NucleoATAC
---

## Version Compatibility

Reference examples tested with: NucleoATAC 0.3.4+, ATACseqQC 1.26+, DANPOS 3.1+, samtools 1.19+, pysam 0.22+, pyBigWig 0.3+, BSgenome.Hsapiens.UCSC.hg38 1.4+, TxDb.Hsapiens.UCSC.hg38.knownGene 3.18+.

NucleoATAC is unmaintained since 2018 but remains the canonical ATAC-specific nucleosome caller; ATACseqQC, DANPOS3, and scprinter are actively developed alternatives. Verify versions before use:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed package and adapt rather than retrying.

# Nucleosome Positioning

**"Where are the nucleosomes in my ATAC-seq data?"** -> Use fragment-size classes (Tn5 cuts twice through naked DNA generating short fragments; once on each side of a single nucleosome generating ~147+linker fragments) to call nucleosome centers, occupancy scores, and the spacing pattern around regulatory elements.

- CLI: `nucleoatac run --bed regions.bed --bam sample.bam --fasta genome.fa`
- R: `ATACseqQC::splitGAlignmentsByCut()` -> fragment classes; `factorFootprints()` -> per-TF flanking nuc analysis
- CLI: `python danpos.py dpos sample.bam` (alternative; supports MNase, ATAC, DNase)
- Python: `scprinter` for multi-scale nucleosome inference

## Nucleosome Physics for ATAC

A nucleosome wraps ~147 bp DNA in 1.65 turns. Adjacent nucleosomes are separated by 20-50 bp linker; mean **nucleosome repeat length (NRL)** is species-dependent:

| Cell type / organism | NRL | Notes |
|----------------------|-----|-------|
| Yeast S. cerevisiae | 165 bp | Tightly packed; less linker |
| Drosophila S2 | 175-185 bp | |
| Mouse ES cells | 188-196 bp | |
| Human HEK293 / K562 | 196-200 bp | Standard somatic |
| Human cortical neurons | 211 bp | Longer linker |
| Sperm chromatin | 240-250 bp | Tight packaging via protamines |
| Active gene bodies | -10 bp shorter than genome avg | Active transcription disrupts |

NRL determines fragment-size peak positions. ATAC mono-nucleosome peak is at NRL (NOT 147 bp -- that's the protected length; ATAC fragments span the full nucleosome+linker). Di-nuc is at 2x NRL minus a small overlap.

## Fragment-Size Classes (Buenrostro 2013, refined)

| Class | Fragment range | Origin | Use |
|-------|---------------|--------|-----|
| Sub-nucleosomal / NFR | < 100 bp | Two Tn5 cuts in naked accessible DNA | TF binding, footprinting |
| Mono-nucleosomal | 180-247 bp | Tn5 cuts on each side of one nucleosome | Nucleosome positioning |
| Di-nucleosomal | 315-473 bp | Tn5 cuts span two nucleosomes | Phasing, NRL estimation |
| Tri-nucleosomal | 558-615 bp | Three nucleosomes | Heterochromatin / phasing |
| > 700 bp | Rare | Often artefact (chimeric); discard | -- |

Mono-nucleosome window 180-247 bp is the Buenrostro 2013 convention; ATACseqQC uses 180-250. Adjust for the target organism's NRL.

## V-Plot Interpretation

V-plots (fragment-size vs position) are diagnostic. X-axis is position relative to a feature (TSS, motif center); Y-axis is fragment size. Aggregate density forms characteristic patterns:

| Pattern | Visual | Meaning |
|---------|--------|---------|
| V (apex at center, low size at center, increasing flanks) | Classic V | TF or NFR at center, flanking nucleosomes |
| W (two V's flanking center) | W-shape | NFR at center plus +1 / -1 nucleosomes |
| Inverted V (peak at center) | Mountain | Fragment fully enclosed at feature; e.g. nucleosome-bound TF | 
| Flat band at 200 bp | Horizontal line | Constitutive nucleosome (no positioning relative to feature) |
| 10.4 bp helical phasing on V | Sub-peaks at 50, 60, 70, 80 bp size | Tn5 helical preference visible; high-quality library |

V-plots are the primary diagnostic for whether nucleosome-positioning analysis will succeed. Flat-band patterns mean no positioning information; classic V/W patterns mean positioning is recoverable.

## Algorithmic Taxonomy

| Tool | Method | Resolution | Strength | Fails when |
|------|--------|-----------|----------|------------|
| NucleoATAC | Cross-correlation with idealized V-plot template; per-base occupancy + nucleosome calls | Single-bp | ATAC-specific; provides occupancy + fuzziness | Unmaintained since 2018; pegs Python 2/3.6; struggles on chromatin without clear NRL |
| ATACseqQC | Fragment-size split + Tn5-shifted GAlignments + V-plot from BAM | Region-level | R/Bioconductor; integrates with TxDb / motif analysis | No per-base nucleosome calls; visualization-focused |
| DANPOS3 | Smoothing + peak call on cleavage signal; tested on MNase, ATAC, DNase | ~50 bp | Robust differential mode (`dpos`); MNase legacy; broadly maintained | Designed for MNase-Seq; ATAC adaptation needs careful parameter tuning |
| scprinter | CNN multi-scale; resolves co-occurring TF + nucleosome footprints | Single-bp | Modern; single-cell aware; multi-scale | Newer; benchmarks evolving; GPU recommended |
| custom (pysam V-plot) | Fragment counting + 2D density | Region-level | Maximally flexible; reproducible | Requires manual calling logic; slow |

Methodology evolves; verify against current Schep 2015 (NucleoATAC), Chen 2013 (DANPOS), Hu 2025 (scPrinter) before locking pipelines.

## +1 Nucleosome Calling

The +1 nucleosome (first nucleosome downstream of TSS, immediately bordering the NFR) is the most-studied positioning feature. Its position relative to TSS determines transcription initiation kinetics.

**Canonical +1 position:** +50 to +60 bp from TSS in metazoa; -100 to -120 bp from TATA in yeast; varies by gene type (Pol II vs Pol III, housekeeping vs developmental).

**Calling strategy:**

**Goal:** Identify each gene's +1 nucleosome, the first nucleosome downstream of the TSS that flanks the NFR.

**Approach:** Build gene-body intervals slopped around TSSs, run NucleoATAC over them to call per-base nucleosome positions, then pick the most-downstream-of-TSS nucleosome per gene.

```bash
# 1. Define gene-body intervals
bedtools slop -i genes.bed -g chrom.sizes -l 200 -r 1000 > gene_bodies.bed

# 2. Run NucleoATAC
nucleoatac run --bed gene_bodies.bed --bam sample.dedup.bam --fasta genome.fa \
    --out tss_nuc/ --cores 8

# 3. The first nucleosome downstream of each TSS in nucpos.bed is +1
```

A failure to detect a clear +1 peak in aggregate V-plot suggests TSS annotation is wrong or library is over-transposed.

## Per-Tool Failure Modes

### NucleoATAC -- Region size and depth dependence

**Trigger:** Short region BED (< 1 kb per region); shallow library (< 25M nuclear reads).

**Mechanism:** NucleoATAC fits an idealized V-plot template per region. Short regions provide too few fragments for stable correlation; shallow data provides noisy templates.

**Symptom:** No nucleosome calls in shallow regions; "occupancy" track is flat at zero.

**Fix:** Use regions >= 500 bp; merge adjacent peaks via bedtools to ensure region size; require >= 30M nuclear reads.

### NucleoATAC -- Maintenance status

**Trigger:** Installing NucleoATAC in 2025+.

**Mechanism:** Last release 2018; pegs Python 3.6 in some installs; depends on outdated NumPy API.

**Fix:** Use a dedicated conda env (`conda create -n nucleoatac python=3.7 numpy=1.18 scipy=1.5 pysam`); accept it works but is no longer updated. Consider scprinter or DANPOS3 alternatives for new projects.

### ATACseqQC factorFootprints -- Asymmetric nucleosome flanks

**Trigger:** Pioneer-factor binding sites where one face is on a nucleosome.

**Mechanism:** factorFootprints assumes symmetric flanking nucleosomes. Pioneer TFs (FOXA1, GATA) only have nucleosome on one side -> asymmetric output.

**Symptom:** Single shoulder in flanking signal; unbalanced V-plot.

**Fix:** Treat asymmetry as biological signal, not artefact. For pioneers, use stranded analysis.

### DANPOS dpos with default parameters -- ATAC mismatch

**Trigger:** Running `python danpos.py dpos` with MNase defaults on ATAC.

**Mechanism:** DANPOS3's smoothing window and peak-calling defaults are tuned for MNase signal (smoother coverage). ATAC's sharper signal requires `--smooth_width 80 --width 145` or similar; otherwise calls are over-smoothed.

**Fix:** Use ATAC-tuned parameters. See DANPOS docs for ATAC-specific recipe; or use NucleoATAC instead.

### Mono-nucleosome filter window mis-set

**Trigger:** Using strict 147 bp filter for mono-nuc fraction; using 100-180 bp instead of 180-247.

**Mechanism:** Mono-nuc fragments are 180-247 bp because they span the nucleosome AND a linker. Filtering tighter excludes the legitimate signal.

**Symptom:** Mono-nuc count is much lower than expected (< 30% of NFR count).

**Fix:** Use Buenrostro 2013 windows: NFR < 100, mono 180-247, di 315-473.

## Decision Tree by Goal

| Goal | Recommended workflow |
|------|---------------------|
| Per-base nucleosome occupancy track | NucleoATAC (with caveat about maintenance); or scprinter |
| V-plot at TSS or motif center | ATACseqQC vPlot |
| Differential nucleosome positioning between conditions | DANPOS3 dpos |
| +1 nucleosome calling at all genes | NucleoATAC + post-process to first nuc downstream of TSS |
| Single-cell nucleosome positioning | scprinter |
| Quick fragment-size QC plot | ATACseqQC fragSizeDist |
| NRL estimation | Custom Fourier / autocorrelation on fragment-end coverage |
| Nucleosome-aware peak calling | MACS3 hmmratac (peak-calling skill) |

## Estimating NRL from Fragment-Size Distribution

**Goal:** Estimate the nucleosome repeat length from ATAC fragment-size periodicity.

**Approach:** Collect proper-pair fragment lengths from the BAM, build a histogram, find density peaks via scipy find_peaks, and read off the mono-nucleosome peak position within the 150-250 bp window.

```python
import numpy as np, pysam
from scipy.signal import find_peaks

bam = pysam.AlignmentFile('sample.bam', 'rb')
frag_lengths = [abs(r.template_length) for r in bam.fetch()
                if r.is_proper_pair and r.is_read1 and 0 < abs(r.template_length) < 1500]
hist, edges = np.histogram(frag_lengths, bins=300, range=(0, 1500))
peaks, _ = find_peaks(hist, distance=50, prominence=hist.max() * 0.05)
peak_positions = edges[peaks] + (edges[1] - edges[0]) / 2
# Mono peak should be ~NRL; di peak ~2*NRL
mono = peak_positions[(peak_positions > 150) & (peak_positions < 250)][0]
print(f'Estimated NRL: {mono:.0f} bp')
```

NRL inferred this way is approximate; for precision use autocorrelation on cumulative cleavage coverage instead.

## V-Plot in Python

**Goal:** Build a fragment-size-by-position density plot to diagnose nucleosome positioning around a feature.

**Approach:** Iterate proper-pair fragments in a flank window around each feature center, accumulate counts into a (fragment_size x position) grid, and render the 2D density.

```python
import numpy as np, pysam, matplotlib.pyplot as plt

def vplot(bam_path, regions_bed, max_size=600, flank=1000):
    bam = pysam.AlignmentFile(bam_path, 'rb')
    grid = np.zeros((max_size, 2 * flank))
    for line in open(regions_bed):
        chrom, start, *_ = line.strip().split('\t')
        center = int(start)
        for r in bam.fetch(chrom, max(0, center - flank), center + flank):
            if not r.is_proper_pair or not r.is_read1: continue
            size = abs(r.template_length)
            if size <= 0 or size >= max_size: continue
            frag_center = r.reference_start + size // 2
            x = frag_center - center + flank
            if 0 <= x < 2 * flank:
                grid[size, x] += 1
    return grid

g = vplot('sample.bam', 'tss.bed')
plt.imshow(g, aspect='auto', origin='lower', cmap='magma',
           extent=[-1000, 1000, 0, 600])
plt.xlabel('Distance from feature (bp)')
plt.ylabel('Fragment size (bp)')
plt.savefig('vplot.png', dpi=200, bbox_inches='tight')
```

V-plot quality is the most useful diagnostic before nucleosome calling. Classic V at TSS = positioning info recoverable; flat band = not.

## Differential Nucleosome Positioning (DANPOS3 dpos)

```bash
# Compare control vs treatment nucleosome positions.
# The sample pair is the POSITIONAL argument (a:b means a minus b); -b is for background/input to
# subtract, and -c specifies a read-count to normalize to (an integer, NOT a control BAM path).
python danpos.py dpos condition2.bam:condition1.bam \
    -o danpos_diff/ \
    --paired 1 \
    --smooth_width 80
```

DANPOS reports four event types: shifted nucleosomes, gained, lost, fuzziness change. ENCODE has no official threshold; require >= 30 bp shift and FDR < 0.05 for nucleosome shift calls.

**Full ATAC-tuned DANPOS3 recipe:**
```bash
# --width 145: summit-scan window (DANPOS -jw/--width; default 40)
# --smooth_width 80: smoothing kernel width (DANPOS -z; default 20, widened for ATAC)
# -jd 145: min distance between adjacent nuc calls (single-dash short flag)
# --pheight 1e-5: occupancy P-value cutoff (DANPOS -p; dpos default 0). -q/--height is the separate density cutoff
# --frsz 200: fragment size used (mono-nuc)
python danpos.py dpos sample.bam \
    --paired 1 \
    --width 145 \
    --smooth_width 80 \
    -jd 145 \
    --pheight 1e-5 \
    --frsz 200 \
    --out danpos_out/
```

Verify exact flags with `python danpos.py dpos --help`; DANPOS3 (github.com/sklasfeld/DANPOS3) is invoked as `python danpos.py`, not a `danpos3` executable, and installs from GitHub (the bioconda `danpos` package is DANPOS2). Its documentation has been spotty and flag names can drift across releases.

Adapted from DANPOS3 docs for ATAC; `--smooth_width 80` widens the smoothing kernel to match ATAC's sharper signal vs MNase's broader cleavage. `-jd 145` (single-dash short, alternative `--distance 145`) enforces nucleosome spacing >= 145 bp (one nucleosome footprint).

## Histone Variant Detection from Fragment Size

**Trigger:** Suspected H2A.Z- or H3.3-containing nucleosomes; differential nucleosome composition between conditions.

**Mechanism:** H2A.Z replacement of H2A produces nucleosomes with weaker DNA-histone interaction (lower thermal stability); the H2A.Z population tends toward shorter fragment sizes than canonical H2A nucleosomes. H3.3 replacement is more subtle, but H3.3-H2A.Z double-variant nucleosomes are particularly destabilized at active promoters (Jin 2009 *Nat Genet* 41:941-945).

**Detection:** Aggregate fragment-size distribution at H2A.Z ChIP-seq peaks vs H3K4me3-only peaks; the H2A.Z population shows mean fragment size ~10 bp shorter. ATAC alone CANNOT definitively call H2A.Z; H2A.Z ChIP-seq is needed for ground truth. ATAC fragment-size analysis is a hypothesis generator.

```python
# Per-region fragment-size mean as H2A.Z indicator
def region_frag_size(bam, region):
    sizes = [abs(r.template_length) for r in bam.fetch(*region)
             if r.is_proper_pair and r.is_read1 and 100 < abs(r.template_length) < 300]
    return np.mean(sizes) if sizes else np.nan

# Compare H2A.Z-positive vs H2A.Z-negative TSSs
```

## Long-Read Single-Molecule Chromatin (Fiber-seq, NanoNOMe)

**Alternative to short-read ATAC for nucleosome positioning:**

| Method | Tech | Resolution | Strength |
|--------|------|-----------|----------|
| Fiber-seq (Stergachis 2020) | PacBio HiFi + DNA methylation footprinting | Per-molecule single-bp | Reads continuous chromatin fiber up to 20 kb; resolves haplotype-specific positioning |
| NanoNOMe (Lee 2020 *Nat Methods* 17:1191-1199) | Nanopore + GpC methyltransferase | Per-molecule single-bp | Same single-molecule but cheaper than PacBio |

Fiber-seq can detect nucleosome occupancy directly per single chromatin molecule (no aggregation needed). Resolves cell-cycle-dependent and stochastic positioning that bulk ATAC averages out. Preferred for fine-structure analysis of regulatory elements.

For most labs, short-read ATAC + NucleoATAC remains primary; Fiber-seq is special-purpose when single-molecule resolution is essential.

## Nucleosome Fuzziness

Fuzziness measures how sharply positioned a nucleosome is across cells. Defined as the standard deviation of per-cell nucleosome center positions.

| Fuzziness range | Interpretation |
|-----------------|----------------|
| < 20 bp | Sharply positioned (rare in metazoa; common at +1 in yeast) |
| 20-50 bp | Standard well-positioned |
| 50-100 bp | Fuzzy; constitutive but non-stable |
| > 100 bp | Effectively unpositioned |

These ranges are field-convention bands (drawn from NucleoATAC / DANPOS practice); no single primary paper prescribes them -- verify against tool-specific documentation when reporting.

NucleoATAC reports per-nucleosome fuzziness in the fuzziness column (column 13) of `.nucpos.bed` -- a measure of how wide the signal peak is; well-positioned nucleosomes show low fuzziness (~20-50 bp), consistent with the table above.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `nucleoatac run` ImportError on numpy | Python 3.6 incompatibility | Use dedicated conda env with pinned versions |
| Empty .nucpos.bed output | Region BED too short or library too shallow | Verify region size >= 500 bp; depth >= 30M |
| V-plot shows horizontal band, no V | No positioning info; library over-transposed or wrong feature center | Check feature BED; verify TSS positions are correct |
| Mono-nuc count very low | Wrong fragment-size window (used 100-180 instead of 180-247) | Use Buenrostro windows |
| factorFootprints asymmetric | Pioneer TF; this is biological | Treat as signal, not artefact |
| DANPOS calls many shifts | MNase parameters used on ATAC | Tune `--smooth_width 80 --width 145` for ATAC |
| splitGAlignmentsByCut error in ATACseqQC | BAM is single-end | Mono-nuc analysis requires paired-end |
| +1 nucleosome not visible at TSS aggregate | TSS list mixes coding + non-coding strands; or wrong genome build | Restrict to protein-coding TSSs in matched build |

## References

- Schep AN et al 2015 Genome Res 25:1757 (NucleoATAC)
- Chen K et al 2013 Genome Res 23:341 (DANPOS)
- Buenrostro JD et al 2013 Nat Methods 10:1213 (ATAC fragment-size classes)
- Ou J et al 2018 BMC Genomics 19:169 (ATACseqQC)
- Hu Y et al 2025 Nature 638:779 (scPrinter/PRINT; multiscale footprints)
- Mavrich TN et al 2008 Nature 453:358 (+1 nucleosome positioning)
- Voong LN et al 2016 Cell 167:1555-1570 (high-resolution chemical nucleosome mapping)
- Jin C et al 2009 Nat Genet 41:941 (H3.3/H2A.Z double-variant nucleosome instability at active regions)
- Teif VB et al 2012 Nat Struct Mol Biol 19:1185 (NRL variation across cell types)

## Related Skills

- atac-seq/atac-qc - Fragment-size periodicity QC
- atac-seq/atac-peak-calling - Nucleosome-aware MACS3 hmmratac
- atac-seq/footprinting - Per-TF flanking nucleosome analysis
- atac-seq/single-cell-atac - scprinter for sc nucleosome positioning
- chip-seq/peak-annotation - Annotate nucleosome positions to genes
- alignment-files/bam-statistics - Insert-size statistics upstream
<!-- END FILE: atac-seq/nucleosome-positioning/SKILL.md -->

## 子目录：atac-seq/single-cell-atac

<!-- BEGIN FILE: atac-seq/single-cell-atac/SKILL.md -->
---
name: bio-atac-seq-single-cell-atac
description: Process and analyze single-cell ATAC-seq data with Signac, ArchR, SnapATAC2, or Cell Ranger ATAC. Use when handling 10X scATAC or 10X Multiome (paired RNA+ATAC) data, performing per-cell QC, choosing between ArchR/Signac/SnapATAC2 ecosystems, building per-cluster consensus peaksets, integrating with paired scRNA-seq, doublet detection (AMULET vs ArchR vs scDblFinder), or running pseudobulk differential accessibility per cluster.
tool_type: mixed
primary_tool: Signac
---

## Version Compatibility

Reference examples tested with: Cell Ranger ATAC 2.1+, Signac 1.13+, Seurat 5.0+, ArchR 1.0.2+, SnapATAC2 2.8+, AMULET 1.1+, scDblFinder 1.16+, scater 1.30+, scvi-tools 1.1+, GenomicRanges 1.54+, JASPAR2024 0.99+, BSgenome.Hsapiens.UCSC.hg38 1.4+, EnsDb.Hsapiens.v86 2.99+, MACS3 3.0+. SnapATAC2 2.8+ uses `pp.import_fragments`; older 2.5-2.7 used `pp.import_data` (renamed/removed in 2.9).

Verify before use:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed package and adapt rather than retrying.

# Single-Cell ATAC-seq

**"Process my 10X scATAC data from cellranger output"** -> Build a per-cell fragment matrix, compute per-cell QC, dimensionality reduction (TF-IDF + LSI / spectral / autoencoder), cluster, call cluster-level pseudobulk peaks, annotate cell types via gene-activity scores, and integrate with paired scRNA-seq if Multiome.

- R: `Signac::CreateChromatinAssay()` -> `Seurat` workflow (TF-IDF + SVD + UMAP + Leiden)
- R: `ArchR::createArrowFiles()` -> ArchR project (TileMatrix + LSI + UMAP)
- Python: `snapatac2.pp.import_fragments()` -> SnapATAC2 (spectral / diffusion-map clustering)
- CLI (preprocessing): `cellranger-atac count` (10X) or `chromap` (alignment-only fragment files)

## Ecosystem Choice (The Most Important Decision)

| Ecosystem | Language | Strength | Fails when | Best for |
|-----------|---------|---------|------------|----------|
| Signac (Stuart 2021) | R, Seurat-based | Tightest scRNA-seq integration; Seurat ecosystem mature | Memory hungry on >100K cells; slower than ArchR | Multiome RNA+ATAC; small-to-medium datasets; Seurat user |
| ArchR (Granja 2021) | R, Arrow/HDF5 | Memory-efficient (Arrow files); fast on 100K-1M cells; built-in trajectory + doublet | Less RNA-seq integration; ArchR-specific format | Large bulk-cohort scATAC; trajectory analysis; ATAC-only |
| SnapATAC2 (Zhang 2024) | Python, AnnData | Memory-efficient; modern Python ecosystem; spectral clustering performant | Newer; benchmarks evolving; ecosystem smaller than R | Python-first labs; very large datasets (>1M cells) |
| Cell Ranger ATAC | CLI (10X-specific) | 10X official preprocessing | Closed; fixed pipeline | Only as preprocessing step; analysis happens elsewhere |
| scATAC-pro | CLI-based pipeline | Alternative preprocessing | Less maintained | Legacy; not recommended for new projects |

Methodology evolves; verify against Granja 2021 (ArchR), Stuart 2021 (Signac), Zhang 2024 (SnapATAC2), Heumos 2023 (best practices) before locking pipelines.

## 10X Multiome Caveat (Paired RNA + ATAC)

10X Multiome chemistry profiles RNA AND ATAC from the same cell. Outputs are joined by a shared barcode. Multiome workflows use Signac for ATAC and Seurat for RNA, integrated through the same Seurat object via WNN (Weighted Nearest Neighbor; Hao 2021).

Single-modality 10X scATAC (chemistry v1, v2) does NOT produce paired RNA. Verify the chemistry on the cellranger summary before assuming Multiome.

## Per-Cell QC Thresholds

| Metric | Definition | Pass | Caution | Reject | Source |
|--------|-----------|------|---------|--------|--------|
| Fragment count per cell | n_fragments after dedup | 3000-50000 | 1000-3000 | < 1000 or > 80000 | 10X recommendation; high = doublet |
| TSS enrichment per cell | Signal at TSS / flanks (per cell) | >= 4 | 2-4 | < 2 | ArchR / Signac default; lower than bulk because per-cell |
| Nucleosome signal | Mono / NFR fragment ratio | <= 4 | 4-10 | > 10 | Signac default; high = poor library |
| % reads in peaks (per cell) | FRiP per cell at consensus | >= 0.15 | 0.10-0.15 | < 0.05 | ArchR / Signac defaults |
| Mitochondrial fraction (per cell) | chrM / total per cell | < 0.05 | 0.05-0.15 | > 0.20 | Lower than bulk; per-cell more sensitive |
| Doublet score | AMULET / ArchR doublet | < 0.5 | 0.5-0.7 | > 0.7 | Tool-dependent threshold |
| Blacklist ratio | Reads in ENCODE blacklist / total | < 0.05 | 0.05-0.10 | > 0.10 | Standard |

Per-cell thresholds are looser than bulk because individual cells have orders of magnitude less signal; the population aggregate is what matters.

## Doublet Detection: Three Approaches

| Tool | Method | Strength | Fails when |
|------|--------|---------|------------|
| AMULET (Thibodeau 2021) | Collision-based: detects cells with too many fragments at same position (mathematically impossible from single cell because of 2-allele limit) | Specific to ATAC biology; orthogonal to clustering | Requires high depth; recall drops sharply below ~15-16K valid read pairs/cell (peaks ~90% near ~25K) |
| ArchR addDoubletScores | Synthetic doublet simulation + projection into LSI | Built into ArchR; auto-thresholds | Tied to ArchR's LSI; not portable |
| scDblFinder (Germain 2021) | Synthetic doublets + classifier | Works on Signac and SCE objects; well-benchmarked | RNA-developed; ATAC adaptation requires careful settings |

**Operational rule:** Run AMULET as the primary ATAC-specific check; verify with ArchR or scDblFinder as orthogonal evidence. Double-flagged cells are high-confidence doublets.

## Per-Tool Failure Modes

### Signac TF-IDF + SVD -- First component is depth

**Trigger:** Running `RunTFIDF` -> `RunSVD` and using all components for clustering.

**Mechanism:** Component 1 of LSI is highly correlated with sequencing depth per cell, not biology. Including it pulls clusters along depth axis.

**Symptom:** UMAP shows linear cell-density gradient that tracks fragment count.

**Fix:** Skip component 1 in downstream UMAP and clustering: `RunUMAP(object, dims=2:30)`, `FindNeighbors(object, dims=2:30)`. ArchR and SnapATAC2 do this automatically.

### ArchR -- TileMatrix vs PeakMatrix confusion

**Trigger:** Using TileMatrix for differential testing or motif analysis.

**Mechanism:** TileMatrix is regular fixed bins (default 500 bp) covering the whole genome; useful for clustering but not for biology because ATAC signal is at peaks, not arbitrary bins.

**Fix:** Use TileMatrix for embedding/clustering (it's faster); use PeakMatrix (after `addReproduciblePeakSet`) for differential, motif, and gene-activity analysis.

### SnapATAC2 -- Memory layout assumes integer counts

**Trigger:** Loading non-integer or negative-valued matrices.

**Fix:** SnapATAC2 expects raw fragment counts (Int32). Convert from float matrices before loading.

### Cell Ranger ATAC -- Empty droplet detection

**Trigger:** Default cellranger-atac calls cells based on UMI count but ATAC has no UMIs; uses fragment-based heuristic. Sometimes calls < 1000-fragment cells as real.

**Fix:** Re-filter cellranger output to require fragment count >= 1000 AND TSS enrichment >= 4 BEFORE downstream analysis.

### Multiome WNN -- ATAC weighting

**Trigger:** Default WNN equally weights RNA and ATAC modalities.

**Mechanism:** ATAC's per-cell signal is much sparser than RNA; equal weighting can swamp the joint embedding with ATAC noise.

**Fix:** Inspect per-modality weights with `IntegrateLayers`; if ATAC weights dominate noise, manually adjust or use `FindMultiModalNeighbors` carefully.

### Per-cluster pseudobulk peak calling -- Empty clusters

**Trigger:** Calling MACS3 per cluster when one cluster has < 200 cells.

**Mechanism:** MACS3 needs >= 1M reads in pseudobulk to call peaks reliably; small clusters do not produce enough reads.

**Fix:** Aggregate small clusters into a "rare" group OR drop them from per-cluster calling. Use the union of larger-cluster peaks as a fallback for rare-cell-type analysis.

## Decision Tree by Goal

| Goal | Recommended pipeline |
|------|---------------------|
| Standard 10X scATAC analysis (R user) | Signac: CreateChromatinAssay -> RunTFIDF -> RunSVD -> RunUMAP (dims 2:30) -> FindClusters |
| Standard 10X scATAC analysis (Python user) | SnapATAC2: pp.import_fragments -> add_tile_matrix -> spectral -> UMAP -> leiden |
| Large dataset (> 100K cells) | ArchR (memory-efficient Arrow files) |
| 10X Multiome (paired RNA + ATAC) | Signac + Seurat: per-modality embedding then WNN integration |
| Trajectory / pseudotime | ArchR getTrajectory; or Signac + Cicero |
| Differential accessibility per cluster | Pseudobulk per cluster -> consensus peakset -> DESeq2 |
| Cell-type annotation | Gene-activity scores via ArchR or Signac; then run `single-cell/markers-annotation` |
| Multimodal trajectories (RNA + ATAC) | MOFA+, ArchR + scRNA integration, or SCENIC+ |
| Plant / non-model | Signac with custom EnsDb / TxDb; ArchR with custom annotations |

## Standard Signac Workflow

**Goal:** Process 10X scATAC output into a clustered, annotated Seurat object with per-cell QC, embedding, and gene-activity scores.

**Approach:** Load fragments and peak counts into a ChromatinAssay, compute per-cell QC (TSS enrichment, nucleosome signal, FRiP, blacklist), subset to passing cells, run TF-IDF + SVD + UMAP skipping LSI component 1, then derive a gene-activity assay for marker-based annotation.

```r
library(Signac); library(Seurat); library(EnsDb.Hsapiens.v86)
library(BSgenome.Hsapiens.UCSC.hg38)

# 1. Load 10X output
counts <- Read10X_h5('outs/filtered_peak_bc_matrix.h5')
metadata <- read.csv('outs/singlecell.csv', row.names=1)

chrom_assay <- CreateChromatinAssay(
    counts=counts,
    sep=c(':', '-'),
    fragments='outs/fragments.tsv.gz',
    annotation=GetGRangesFromEnsDb(EnsDb.Hsapiens.v86),
    genome='hg38')

obj <- CreateSeuratObject(counts=chrom_assay, assay='ATAC', meta.data=metadata)

# 2. Per-cell QC
obj <- NucleosomeSignal(obj)              # Mono/NFR ratio
obj <- TSSEnrichment(obj, fast=FALSE)
obj$pct_reads_in_peaks <- obj$peak_region_fragments / obj$passed_filters * 100
obj$blacklist_ratio <- obj$blacklist_region_fragments / obj$peak_region_fragments

# 3. QC filter (looser per-cell thresholds)
obj <- subset(obj,
    subset = peak_region_fragments > 1000 & peak_region_fragments < 20000 &
             pct_reads_in_peaks > 15 & blacklist_ratio < 0.05 &
             nucleosome_signal < 4 & TSS.enrichment > 4)

# 4. Dimensionality reduction (skip component 1 - it's depth)
obj <- RunTFIDF(obj)
obj <- FindTopFeatures(obj, min.cutoff='q0')
obj <- RunSVD(obj)
obj <- RunUMAP(obj, reduction='lsi', dims=2:30)
obj <- FindNeighbors(obj, reduction='lsi', dims=2:30)
obj <- FindClusters(obj, algorithm=4, resolution=0.5)    # Leiden

# 5. Gene-activity for annotation
gene.activities <- GeneActivity(obj)
obj[['ACT']] <- CreateAssayObject(counts=gene.activities)
DefaultAssay(obj) <- 'ACT'
obj <- NormalizeData(obj, normalization.method='LogNormalize',
                     scale.factor=median(obj$nCount_ACT))
```

## Per-Cluster Pseudobulk Peak Calling

```r
# Signac wrapper around MACS3
peaks <- CallPeaks(obj, group.by='seurat_clusters',
                   macs2.path='/path/to/macs3', cleanup=FALSE,
                   format='BED', shift=-75, extsize=150,   # Tn5 cut-site recipe; shift only applies to format='BED'
                   additional.args='-p 0.01')
# Then iterative-overlap consensus across clusters (atac-seq/consensus-peakset)
```

## ArchR Workflow

**Goal:** Build an ArchR project from fragment files, filter doublets, cluster, and call per-cluster reproducible peaks.

**Approach:** Create Arrow files with minimum TSS and fragment thresholds, score doublets and filter, run iterative LSI + UMAP + clustering on the TileMatrix, then build per-cluster group coverages and a reproducible peakset via MACS3.

```r
library(ArchR)
addArchRGenome('hg38')

# 1. Create Arrow files from fragment files
ArrowFiles <- createArrowFiles(
    inputFiles=c('fragments_rep1.tsv.gz', 'fragments_rep2.tsv.gz'),
    sampleNames=c('rep1', 'rep2'),
    minTSS=4, minFrags=1000,
    addTileMat=TRUE, addGeneScoreMat=TRUE)

# 2. Doublet detection (built-in)
doubletScores <- addDoubletScores(input=ArrowFiles, k=10, knnMethod='UMAP')

# 3. Project + filter
proj <- ArchRProject(ArrowFiles=ArrowFiles, outputDirectory='ArchR_out')
proj <- filterDoublets(proj)

# 4. LSI + UMAP + clustering
proj <- addIterativeLSI(proj, useMatrix='TileMatrix', name='IterativeLSI')
proj <- addClusters(proj, reducedDims='IterativeLSI', method='Seurat', resolution=0.5)
proj <- addUMAP(proj, reducedDims='IterativeLSI')

# 5. Reproducible peakset (per cluster)
proj <- addGroupCoverages(proj, groupBy='Clusters')
proj <- addReproduciblePeakSet(proj, groupBy='Clusters', pathToMacs2='/path/macs3')
proj <- addPeakMatrix(proj)
```

## SnapATAC2 Workflow (Python)

**Goal:** Run a Python-native scATAC pipeline from fragments through clusters, per-cluster peaks, and gene activity.

**Approach:** Import fragments to a backed AnnData, compute per-cell TSS enrichment and fragment-size metrics, filter cells, build a tile matrix, run spectral embedding + UMAP + Leiden, call per-cluster peaks via MACS3, and derive a gene-activity matrix.

```python
import snapatac2 as snap

# 1. Load 10X fragments. SnapATAC2 uses snap.pp.import_fragments (NOT snap.read_10x, which doesn't exist).
data = snap.pp.import_fragments(
    fragment_file='outs/fragments.tsv.gz',
    chrom_sizes=snap.genome.hg38,
    file='out.h5ad',                        # backed AnnData; backend handled by file path
    sorted_by_barcode=False)
data.obs['sample_id'] = 'rep1'

# 2. Per-cell QC
snap.metrics.tsse(data, gene_anno=snap.genome.hg38)
snap.metrics.frag_size_distr(data)
snap.pp.filter_cells(data, min_counts=1000, min_tsse=4)

# 3. Tile matrix + spectral
snap.pp.add_tile_matrix(data, bin_size=500)
snap.pp.select_features(data, n_features=250000)
snap.tl.spectral(data)
snap.tl.umap(data)
snap.tl.leiden(data)

# 4. Per-cluster peak calling (uses MACS3)
snap.tl.macs3(data, groupby='leiden')

# 5. Gene activity (gene score) for annotation
gene_mat = snap.pp.make_gene_matrix(data, gene_anno=snap.genome.hg38)
```

## Reconciliation Across Tools

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Signac UMAP shows tight clusters; ArchR UMAP shows loose | Different LSI implementation; ArchR uses iterative LSI by default | Both valid; biology should match in cluster labels |
| Different tools call different doublet rates | Different algorithms (collision vs simulation) | Use intersection (cells flagged by 2+ tools) as high-confidence doublets |
| Cluster boundaries differ | Different clustering algorithm or resolution | Standardize on Leiden algorithm 4 with same resolution |
| Per-cluster peak count differs | Different peak callers or pseudobulk depth | Ensure same MACS3 parameters; pool small clusters |

**Operational rule:** For high-confidence cell-type annotation, agree across two ecosystems (e.g., Signac + ArchR clusters) and report agreement metrics.

## cellranger-atac vs cellranger-arc

| Pipeline | Use for | Output |
|----------|---------|--------|
| cellranger-atac | Single-modality 10X scATAC (chemistry v1, v2) | per-cell ATAC barcodes; fragments.tsv.gz; per-barcode metadata |
| cellranger-arc | 10X Multiome (paired RNA + ATAC same cell, "Multiome chemistry") | joint barcodes for RNA + ATAC; separate fragment / count files; one barcode whitelist |

**Trigger:** Loading 10X output without checking which pipeline produced it.

**Mechanism:** cellranger-atac and cellranger-arc produce different output structures. cellranger-arc fragments.tsv has barcodes paired with the RNA matrix; cellranger-atac fragments are ATAC-only with their own barcode universe.

**Fix:** Verify the chemistry on the cellranger summary (look for "Multiome" in the run config). Use `Read10X_h5` for cellranger-arc Multiome RNA output; use `CreateChromatinAssay` with the matched fragments for the ATAC. Mixing barcodes across pipelines fails silently.

## Cell-Cycle Correction for scATAC

**Trigger:** Proliferating cell types in the dataset; cells distributed across cell cycle phases.

**Mechanism:** Replication-associated chromatin opening adds 5-10% global accessibility per cell as it moves G1 -> S -> G2/M; this confounds clustering and DA.

**Detection:** Score cells with a chromatin-adapted S-phase signature (regulated origin loci, replication-stress-response gene accessibility) analogous to Seurat's CellCycleScoring on RNA. Or compute a Repli-seq peak overlap score.

**Fix:** Regress S-phase score on the TF-IDF residuals before downstream LSI: `ScaleData(obj, vars.to.regress='S.score')` analogous to RNA workflow. For DA between cell-cycle-mismatched conditions, add S-phase as covariate in pseudobulk DESeq2.

## Sex-Chromosome QC for scATAC

**Trigger:** Mixed-sex donors in the dataset; sample-swap detection.

**Mechanism:** XIST locus accessibility is high in female cells (X-inactivation); chrY peak count is essentially zero in females. Per-cell or per-sample, the XIST/chrY ratio identifies sex unambiguously.

**Detection:** In a per-cell counts matrix, compute fraction of fragments at XIST locus (chrX:73820651-73852753 hg38) and chrY peak count; classify cells; flag cells/samples where assignment disagrees with metadata.

**XCI escapees:** Genes that escape X-inactivation (KDM6A, DDX3X, EIF1AX) are biallelically accessible in female cells but not male; can be used as additional sex confirmation if XIST is ambiguous.

## scArches Reference Mapping

**Trigger:** Projecting query scATAC onto a reference atlas; cross-study integration without batch effects.

**Mechanism:** scArches (Lotfollahi 2022) provides transfer-learning to project a new dataset onto an existing reference's latent space without retraining the reference. For ATAC, the relevant model is PEAKVI (Ashuach 2022). PEAKVI lives in `scvi-tools` (`scvi.model.PEAKVI`); the `load_query_data` classmethod implements the scArches algorithm directly, so an explicit `import scarches` is not required.

```python
import scvi

# Pre-trained reference model (e.g. PBMC scATAC atlas)
query_model = scvi.model.PEAKVI.load_query_data(adata_query, reference_path)
query_model.train(max_epochs=200)
adata_query.obsm['X_emb'] = query_model.get_latent_representation()
```

Reference atlases for ATAC are still emerging; the most-developed are PBMC (Granja 2021) and brain (BRAIN Initiative).

## chromBPNet Per-Cluster Pseudobulk

**Trigger:** Cell-type-specific variant effect prediction; per-cluster bias-corrected calling.

**Mechanism:** Train chromBPNet (atac-seq/deep-learning-atac) per pseudobulk cluster; outputs are bias-corrected per-base profiles + variant effect predictions specific to that cell type.

**Workflow:** Aggregate fragments per cluster into pseudobulk BAMs; run chromBPNet pipeline per cluster (~24h GPU per cluster); use the resulting model for in silico variant scoring at GWAS / rare-variant SNPs in that cell type.

For most studies, this is reserved for top 5-10 priority clusters; running chromBPNet per cluster on >20 cell types is computationally heavy.

## AMULET Depth Threshold

AMULET reaches maximum recall (~90%) near ~25,000 valid read pairs (~fragments) per cell and degrades sharply below ~15,000-16,000, where the collision-based detection has insufficient power: the expected number of collisions per cell is too small for the binomial test to distinguish doublet from singleton. For lower-depth libraries, use synthetic-doublet methods (ArchR addDoubletScores, scDblFinder) instead.

## Multiome WNN Integration (Signac)

**Goal:** Build a joint RNA + ATAC embedding from a 10X Multiome dataset using Weighted Nearest Neighbors.

**Approach:** Run per-modality embeddings (PCA on RNA, TF-IDF + SVD on ATAC skipping LSI-1), then use FindMultiModalNeighbors to learn per-cell modality weights and project a joint UMAP.

```r
# Assume `obj` has both 'RNA' and 'ATAC' assays from same Multiome experiment
DefaultAssay(obj) <- 'RNA'
obj <- NormalizeData(obj) %>% FindVariableFeatures() %>% ScaleData() %>% RunPCA()

DefaultAssay(obj) <- 'ATAC'
obj <- RunTFIDF(obj) %>% FindTopFeatures(min.cutoff='q0') %>% RunSVD()

# Joint embedding
obj <- FindMultiModalNeighbors(obj, reduction.list=list('pca', 'lsi'),
                               dims.list=list(1:30, 2:30))
obj <- RunUMAP(obj, nn.name='weighted.nn', reduction.name='wnn.umap')
```

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| UMAP shows depth gradient | LSI component 1 included in clustering | `dims=2:30` instead of `1:30` |
| Cell Ranger output has many low-quality cells | cellranger ATAC uses lenient cell calling | Re-filter at fragment count >= 1000 + TSS enrichment >= 4 |
| ArchR "TileMatrix not found" | Forgot `addTileMat=TRUE` in createArrowFiles | Re-create Arrow files with the flag |
| Signac CreateChromatinAssay fails on missing fragments file | Path to fragments.tsv.gz incorrect; or missing tabix index | Provide full path; run `tabix -p bed fragments.tsv.gz` |
| MACS3 fails on tiny pseudobulk | Cluster too small | Use cluster aggregation; require >= 200 cells per cluster |
| AMULET reports 100% doublets | Threshold mis-set or input is technical replicates | Check fragment-count distribution; AMULET needs high depth (recall peaks near ~25K valid read pairs/cell) |
| Multiome WNN clusters dominated by ATAC noise | Equal modality weighting | Inspect modality weights; manually adjust if needed |
| chromVAR / motif assay all NA | Run before peakset finalized | Re-run AddMotifs / RunChromVAR after peaks stable |
| EnsDb / BSgenome version mismatch | hg38 BSgenome with wrong-build EnsDb | Match builds; `EnsDb.Hsapiens.v86` is GRCh38 (Ensembl v86); use `EnsDb.Hsapiens.v75` for hg19. Newer hg38 EnsDb releases (v98+) reflect newer GENCODE annotations |

## References

- Stuart T et al 2021 Nat Methods 18:1333 (Signac)
- Granja JM et al 2021 Nat Genet 53:403 (ArchR)
- Zhang K et al 2024 Nat Methods 21:217 (SnapATAC2)
- Hao Y et al 2021 Cell 184:3573 (Seurat WNN)
- Thibodeau A et al 2021 Genome Biol 22:252 (AMULET doublet detection)
- Germain PL et al 2021 F1000Res 10:979 (scDblFinder)
- Cusanovich DA et al 2015 Science 348:910 (sciATAC; LSI for sc data)
- Chen H et al 2019 Genome Biol 20:241 (scATAC analysis benchmark)
- Heumos L et al 2023 Nat Rev Genet 24:550 (Best practices for single-cell)
- 10X Genomics Cell Ranger ATAC documentation

## Related Skills

- atac-seq/atac-qc - Bulk QC patterns adapted for per-cell
- atac-seq/atac-peak-calling - Pseudobulk peak calling per cluster
- atac-seq/consensus-peakset - Across-cluster consensus
- atac-seq/differential-accessibility - Pseudobulk DA per cluster
- atac-seq/motif-deviation - chromVAR for per-cell TF activity
- atac-seq/footprinting - scprinter for sc footprinting
- atac-seq/co-accessibility - Cicero for cis-regulatory connections
- atac-seq/deep-learning-atac - chromBPNet / scBasset for per-cluster bias correction and variant effects
- atac-seq/enhancer-gene-linking - Per-cell-type enhancer-gene maps
- atac-seq/allele-specific-accessibility - sc allelic imbalance for cis-effects
- single-cell/preprocessing - General sc QC patterns
- single-cell/clustering - Cluster definition
- single-cell/cell-annotation - Automated reference-based label transfer
- single-cell/multimodal-integration - Multiome RNA+ATAC integration
- single-cell/scatac-analysis - Cross-reference single-cell ATAC-specific patterns
- single-cell/batch-integration - scArches reference mapping; Harmony
<!-- END FILE: atac-seq/single-cell-atac/SKILL.md -->

<!-- END CATEGORY: atac-seq -->

