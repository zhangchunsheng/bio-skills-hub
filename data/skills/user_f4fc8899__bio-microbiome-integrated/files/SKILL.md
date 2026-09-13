---
slug: bio-microbiome-integrated
version: 1.0.1
displayName: "微生物组 / Microbiome analysis"
name: bio-microbiome-integrated
summary: "中文：微生物组综合技能，整合 6 个相关专题，覆盖微生物组分析：16S/ITS amplicon ASV推断、分类、多样性、差异丰度、PICRUSt2功能预测。 English: Integrated Microbiome analysis skill covering 6 related topics, including Microbiome analysis: 16S/ITS amplicon ASV inference, taxonomy, diversity, differential abundance, PICRUSt2 functional prediction."
description: "中文：这是一个面向微生物组的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：微生物组分析：16S/ITS amplicon ASV推断、分类、多样性、差异丰度、PICRUSt2功能预测。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：ALDEx2, DADA2, PICRUSt2。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Microbiome analysis, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Microbiome analysis: 16S/ITS amplicon ASV inference, taxonomy, diversity, differential abundance, PICRUSt2 functional prediction. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: ALDEx2, DADA2, PICRUSt2. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# microbiome 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: microbiome -->

## 子目录：microbiome/amplicon-processing

<!-- BEGIN FILE: microbiome/amplicon-processing/SKILL.md -->
---
name: bio-microbiome-amplicon-processing
description: Infers exact amplicon sequence variants (ASVs) from demultiplexed 16S rRNA or ITS amplicon FASTQ with DADA2 - removing primers with cutadapt (--discard-untrimmed), learning a per-run error model (filterAndTrim -> learnErrors -> dada -> mergePairs), merging run-level tables with mergeSequenceTables, then one removeBimeraDenovo. Covers why primers come OFF before truncation, why the error model is per-run, truncLen as a merge-overlap detection budget (V4 vs V3-V4), DADA2 vs Deblur and q2-dada2 (denoise-paired/single/pyro/ccs), ASV vs OTU, NovaSeq binned-quality error-fit breakage, ITSxpress for variable-length ITS, and decontam removal of reagent/kit contaminants. Use when turning demultiplexed amplicon reads into an ASV/feature table, choosing truncation lengths, handling multi-run studies, or ITS. For shotgun reads see metagenomics/kraken-classification; for QIIME2 CLI mechanics see qiime2-workflow; for primer trimming theory see read-qc/adapter-trimming.
tool_type: mixed
primary_tool: DADA2
---

## Version Compatibility

Reference examples tested with: DADA2 1.30+, cutadapt 4.6+, ITSxpress 2.0+, QIIME2 2024.2+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The error model is a PER-RUN artifact, not a version: `learnErrors` is fit to one sequencing run (flowcell/chemistry/instrument). Multi-run studies run the per-run inference separately, then `mergeSequenceTables`, then a single chimera removal - never pool FASTQs across runs before `learnErrors`. DADA2 `dada()` defaults (`OMEGA_A` 1e-40, `mergePairs` `minOverlap` 12) and QIIME2 plugin flag spellings drift between releases; confirm with `?dada` and `qiime dada2 --help`.

# Amplicon Processing with DADA2

**"Process my 16S amplicon data to get ASVs"** -> Strip primers, learn a per-run error model, denoise into exact amplicon sequence variants, merge pairs, and remove chimeras - because an ASV is a model-inferred sequence conditioned on one run, not a clustered consensus or an organism.
- R: `dada(filtFs, err=learnErrors(filtFs, multithread=TRUE), multithread=TRUE)`
- CLI: `cutadapt -g FWD -G REV --discard-untrimmed ...` then DADA2, or `qiime dada2 denoise-paired`

Scope: demultiplexed amplicon reads -> chimera-free ASV/feature table + representative sequences. Shotgun reads -> metagenomics/kraken-classification. Taxonomy of the ASVs -> taxonomy-assignment. Diversity/DA of the table -> diversity-analysis, differential-abundance. Compositional/normalization theory (shared) -> metagenomics/abundance-estimation. QIIME2 artifact/provenance/demux mechanics -> qiime2-workflow. Primer-trimming theory -> read-qc/adapter-trimming.

## The Single Most Important Modern Insight -- An ASV Is a Denoiser's Output on One Run, Not a Ground-Truth Organism

The feature table is not an observation of the community; it is the residue of modeling decisions made BEFORE any result exists - which primers were stripped, where reads were truncated, what error model the run's quality scores supported, what was called a chimera. Turn the knobs differently and the table changes. Three corollaries each common misuse violates:

1. **Primers and truncLen decide what is detectable, silently.** Leftover primers corrupt the error model (mismatches read as sequencing error) and masquerade as chimeras; truncating reads below the merge-overlap budget erases taxa by arithmetic, not biology. These knobs are set before the answer exists - declare them.
2. **The error model is fit PER RUN.** Illumina error rates are run-specific. Concatenating runs before `learnErrors` fits one model to a mixture of error structures and denoises wrong. Infer each run separately, then `mergeSequenceTables` (the exact-sequence string is the join key), then one chimera removal.
3. **An ASV is an exact sequence, not a cell, genome, or species.** One genome carries multiple, often divergent 16S copies, so one organism becomes several ASVs and inflates richness (Schloss 2021). Reads are not cells (16S copy number varies); a species-level 16S call is usually overconfident.

Organize the work around declaring and defending these knobs - not around running `dada()` and calling the columns "species."

## ASV vs OTU -- the Methodological Fork

An ASV (DADA2/Deblur) is an exact inferred sequence at single-nucleotide resolution; a 97% OTU is a centroid of a 3%-identity cluster. Both sides are live (present both, do not declare a winner):

- **ASVs replace OTUs** (Callahan 2017 *ISME J* 11:2639): the sequence IS the identity, so ASVs are portable across studies without re-clustering, higher-resolution, and reproducible (no clustering-order/abundance dependence). This is the field default.
- **ASVs over-split genomes** (Schloss 2021 *mSphere* 6:e00191-21; Pan 2023 *Appl Environ Microbiol* 89:e02108-22): intragenomic 16S copy heterogeneity (in ~60% of prokaryotes; *E. coli* K-12 has 7 copies in ~5 sequence types) makes one organism appear as several ASVs, inflating richness; 97% OTUs lump those copies back. Defensible practice: use ASVs, but treat ASV count as an upper bound on richness and collapse to a taxonomic rank (taxonomy-assignment) before richness claims.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| DADA2 | Callahan 2016 *Nat Methods* 13:581 | per-run parametric error model, abundance-partition denoising, merge, chimera | the default; variable length, ITS, singleton sensitivity via pseudo-pooling |
| q2-dada2 | (DADA2 engine; Bolyen 2019 *Nat Biotechnol* 37:852) | QIIME2 wrapper: `denoise-paired`/`single`/`pyro`/`ccs` | DADA2 inside a QIIME2 artifact/provenance workflow -> qiime2-workflow |
| Deblur | Amir 2017 *mSystems* 2:e00191-16 | static upper-bound Illumina error profile (positive filter), one fixed length | fast, per-sample-independent, trivially combinable runs; 16S only |
| cutadapt | Martin 2011 *EMBnet J* 17:10 | primer/adapter trimming (`-g`/`-G`, linked adapters) | MUST run before filterAndTrim; primer removal -> read-qc/adapter-trimming |
| ITSxpress | Rivers 2018 *F1000Research* 7:1418 | HMM-trims the variable-length ITS spacer, keeping quality scores | ITS only; ITS has no valid fixed truncLen |
| VSEARCH | Rognes 2016 *PeerJ* 4:e2584 | open-source 97% OTU clustering, dereplication, chimera | the OTU path, if a 97% clustering is required (legacy) |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| 16S V4 (~253 bp), 2x250 | DADA2 paired, truncLen with comfortable overlap | huge merge slack; truncate to quality freely |
| 16S V3-V4 (~460 bp), 2x250 | DADA2 paired, protect overlap; loosen `maxEE` R | only ~28 bp slack - the merge budget dominates quality |
| ITS (variable length) | cutadapt + ITSxpress + DADA2 `truncLen=0` | fixed truncation slices real biology and breaks merging |
| Full-length 16S (PacBio HiFi/CCS) | DADA2 / `qiime dada2 denoise-ccs` | resolves to species/strain; single-end CCS, not paired |
| Multiple sequencing runs | per-run inference -> `mergeSequenceTables` -> one chimera removal | error model is per-run; never pool FASTQs first |
| Want speed, fixed length, many runs, 16S only | Deblur (`denoise-16S`) | static positive filter; per-sample independent |
| Need singleton/rare-ASV sensitivity | DADA2 `dada(..., pool='pseudo')` | pseudo-pooling approximates full pooling in linear time |
| NovaSeq/NextSeq/iSeq (binned Q) | inspect `plotErrors`; enforce monotonic error fit | ~4 quality bins starve the loess fit -> wrong denoising |
| Shotgun (random WGS) reads, not amplicon | -> metagenomics/kraken-classification | no primers/per-run denoising; different category |

## Remove Primers First (cutadapt)

**Goal:** Strip synthetic, often-degenerate primer sequence before any quality/error step.

**Approach:** Match the forward primer as a 5' adapter on R1 and the reverse primer on R2, discarding pairs where the primer is absent. The order primers -> filter -> learn-errors is non-negotiable: leftover primers corrupt the error model, shift the truncLen frame, and inflate chimeras.

```bash
# -g = 515F forward primer (5' adapter on R1); -G = 806R reverse primer (5' adapter on R2);
# --discard-untrimmed drops pairs lacking the primer (a primerless read is suspect).
cutadapt \
    -g GTGYCAGCMGCCGCGGTAA \
    -G GGACTACNVGGGTWTCTAAT \
    --discard-untrimmed \
    -o trimmed_R1.fastq.gz -p trimmed_R2.fastq.gz \
    sample_R1.fastq.gz sample_R2.fastq.gz
```

The QIIME2 equivalent is `qiime cutadapt trim-paired --p-front-f FWD --p-front-r REV --p-discard-untrimmed`.

## The Per-Run DADA2 Pipeline

**Goal:** Turn one run's primer-trimmed FASTQs into a denoised, merged sequence table.

**Approach:** Filter on expected errors and truncate within the merge budget, learn the run's error model, denoise each read set against it, merge pairs, then tabulate. Run this block once PER sequencing run.

```r
library(dada2)

out <- filterAndTrim(fnFs, filtFs, fnRs, filtRs,
                     truncLen=c(240, 160),     # region/read-length specific; subject to the merge budget below
                     maxEE=c(2, 2), truncQ=2, maxN=0, rm.phix=TRUE,
                     compress=TRUE, multithread=TRUE)
errF <- learnErrors(filtFs, multithread=TRUE)  # fit THIS run only
errR <- learnErrors(filtRs, multithread=TRUE)
plotErrors(errF, nominalQ=TRUE)                # observed points must track the fitted line and fall with Q
dadaFs <- dada(filtFs, err=errF, multithread=TRUE)   # pool='pseudo' for rare-ASV sensitivity
dadaRs <- dada(filtRs, err=errR, multithread=TRUE)
mergers <- mergePairs(dadaFs, filtFs, dadaRs, filtRs, verbose=TRUE)
seqtab_run <- makeSequenceTable(mergers)
```

### truncLen Is a Detection Budget, Not a Quality Setting

Paired-end merging needs `truncLen_F + truncLen_R >= amplicon_length + ~12` (DADA2 `minOverlap` default is 12). truncLen is jointly constrained by quality (cut where median Q drops below ~Q30 on `plotQualityProfile`) AND this overlap budget; the two fight, and for long amplicons the budget wins.

- **V4 (515F/806R, ~253 bp), 2x250:** 250+250 vs 253+12 leaves huge slack - truncate to quality freely (e.g. `c(240, 200)`).
- **V3-V4 (341F/805R, ~460 bp), 2x250:** 250+250 vs 460+12 leaves only ~28 bp slack. Aggressive truncation of both reads kills the overlap and the merge rate collapses to near zero. Preserve length: barely truncate the reverse and loosen `maxEE` to `c(2, 5)` to keep low-Q reverse reads.

A merge cliff in the read-tracking table is a budget problem, not bad data - the taxa were erased by arithmetic.

## Combine Runs, Then Remove Chimeras

**Goal:** Merge per-run sequence tables into one study table and remove PCR chimeras once.

**Approach:** Join run-level tables by exact sequence string, then detect bimeras (an ASV reconstructable from two more-abundant parents) across the combined table.

```r
st_all <- mergeSequenceTables(seqtab_run1, seqtab_run2)   # exact-sequence string is the join key
seqtab_nochim <- removeBimeraDenovo(st_all, method='consensus', multithread=TRUE, verbose=TRUE)
sum(seqtab_nochim) / sum(st_all)   # chimeras = many ASVs but few READS (~0.8-0.99 retained)
```

Carry "run" forward as a batch covariate into differential abundance. A large READ fraction removed as chimeric is a leftover-primer smell (degenerate bases look chimeric), not a real chimera storm.

## Decontamination and Controls (low-biomass)

**Goal:** Identify and remove reagent/kit ("kitome") contaminant ASVs before any downstream analysis - decisive for low-biomass samples, where contaminants can outnumber real signal.

**Approach:** Sequence negative controls (extraction blanks, no-template PCR) and a positive mock community alongside the samples, then classify contaminant ASVs with decontam (Davis 2018): the prevalence method when only controls are available, the frequency method when per-sample DNA concentration was measured, combined when both.

```r
library(decontam)
# seqtab_nochim is samples (rows) x ASVs (cols) - decontam's expected orientation.
# is_control: logical, TRUE for negative-control samples; dna_conc: per-sample DNA concentration (qPCR/Qubit).
# prevalence-only threshold 0.1 default; 0.5 = aggressive (ASV more prevalent in controls than samples = contaminant).
contam <- isContaminant(seqtab_nochim, neg = meta$is_control, conc = meta$dna_conc, method = 'combined', threshold = 0.1)
seqtab_clean <- seqtab_nochim[, !contam$contaminant]
```

Low-biomass samples (skin, biopsy, BAL, sterile-site swabs) can be dominated by the kitome, so a "community" there may be mostly contamination - never interpret a low-biomass result without controls. The shotgun analogue is metagenomics/contamination-controls.

## ITS: Never Fixed-Truncate

**Goal:** Isolate the biologically variable-length ITS spacer without slicing real sequence.

**Approach:** Strip primers with cutadapt, then HMM-trim the conserved SSU/5.8S/LSU flanks with ITSxpress (preserving quality scores), then denoise with `truncLen=0`, filtering on `maxEE`/`minLen` only.

```bash
itsxpress --fastq r1.fastq.gz --fastq2 r2.fastq.gz \
    --region ITS2 --taxa Fungi \   # ITS1/ITS2/ALL; --taxa selects the HMM model
    --outfile trimmed.fastq.gz --threads 4
```

```r
out_its <- filterAndTrim(trimmed, filtered, truncLen=0,   # NEVER fix-truncate ITS (variable length)
                         maxEE=2, minLen=50, maxN=0, rm.phix=TRUE, multithread=TRUE)
```

## QIIME2 and Deblur Equivalents

DADA2 inside QIIME2: `qiime dada2 denoise-paired --p-trunc-len-f --p-trunc-len-r` (also `denoise-single`, `denoise-pyro` for 454/Ion Torrent, `denoise-ccs` with `--p-front`/`--p-adapter`/`--p-min-len`/`--p-max-len` for PacBio CCS). Deblur (static positive filter, one fixed length, 16S only):

```bash
qiime deblur denoise-16S --i-demultiplexed-seqs qc.qza \
    --p-trim-length 250 --p-sample-stats \   # ONE fixed length; Deblur cannot handle variable length
    --o-representative-sequences rep-seqs.qza --o-table table.qza --o-stats stats.qza
```

Do not merge a DADA2 ASV table with a Deblur sOTU table - different feature definitions.

## Per-Method Failure Modes

### Primers left on before truncation
**Trigger:** running filterAndTrim/learnErrors on reads that still carry primers. **Mechanism:** synthetic, often-degenerate primer bases are read as sequencing error and create spurious split points. **Symptom:** wrong error fit, a huge READ fraction removed as chimeric, inflated ASV count. **Fix:** cutadapt `--discard-untrimmed` first; order is primers -> filter -> learnErrors.

### Pooling runs before learnErrors
**Trigger:** concatenating multiple runs' FASTQs into one pipeline. **Mechanism:** one error model is fit to a mixture of run-specific error structures. **Symptom:** distorted denoising; ASVs that vanish or appear when runs are split. **Fix:** per-run inference, then `mergeSequenceTables`, then one chimera removal; carry run as a batch covariate.

### Merge cliff from over-truncation
**Trigger:** truncLen_F + truncLen_R below amplicon length + 12. **Mechanism:** denoised pairs no longer overlap enough to merge. **Symptom:** near-zero `merged` column in read tracking; misread as "low diversity"/"bad data". **Fix:** compute the budget from amplicon and read length first; for long amplicons keep length and loosen `maxEE` R.

### Fixed-truncating ITS
**Trigger:** any `truncLen` on ITS. **Mechanism:** ITS length is biological (ITS1 ~200-600 bp), so a fixed cut slices real sequence off long variants and merge-fails short ones. **Symptom:** lost long fungal taxa, poor merging. **Fix:** cutadapt + ITSxpress, then `truncLen=0`, filter on `maxEE`/`minLen`.

### NovaSeq/NextSeq binned-quality error fit
**Trigger:** default `learnErrors` on ~4-bin quality data. **Mechanism:** the loess error-vs-Q fit is starved and can become non-monotonic (error rising at high Q). **Symptom:** in `plotErrors` the fitted line diverges from observed points. **Fix:** enforce monotonicity in the error matrix (nf-core/ampliseq `--illumina_novaseq`, or set sub-max-Q entries to the max-Q error); never trust the default fit on binned Q.

### ASV count read as species richness
**Trigger:** reporting ASV count as richness or each ASV as one organism. **Mechanism:** intragenomic 16S copy divergence splits one genome into several ASVs (Schloss 2021); reads are not cells (copy number 1-15+). **Symptom:** inflated richness, "species" that are copies of one organism. **Fix:** collapse to genus/species (taxonomy-assignment) before richness claims; treat ASV count as an upper bound.

### Low-biomass contamination ignored (no controls / no decontam)
**Trigger:** analysing low-biomass samples (skin, biopsy, BAL, sterile site) without sequencing controls or running decontam. **Mechanism:** reagent/kit DNA (the kitome) is amplified alongside scarce template and can dominate the reads. **Symptom:** a plausible "community" in a near-sterile sample; reagent-associated genera prominent; results track DNA yield. **Fix:** sequence extraction-blank + no-template-PCR negatives (and a positive mock), run decontam (prevalence or combined), report what was removed (Davis 2018; metagenomics/contamination-controls).

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `maxEE` c(2,2) (loosen R to 5 for long amplicons) | Callahan 2016 *Nat Methods* 13:581 | expected-errors filter beats a hard Q cutoff; computed on the TRUNCATED read, so it interacts with truncLen |
| truncLen budget: truncLen_F + truncLen_R >= amplicon_len + 12 | DADA2 `mergePairs` `minOverlap` default | below this, denoised pairs cannot merge; the merge cliff is arithmetic, not data |
| truncLen cut where median Q < ~25-30 | DADA2 docs | quality target, secondary to the merge budget for long amplicons |
| `maxN` = 0 | DADA2 docs | DADA2 cannot model ambiguous bases; mandatory |
| chimera retained-read fraction ~0.8-0.99 | DADA2 docs | chimeras are many ASVs but few reads; a large read loss flags leftover primers |
| `pool='pseudo'` for rare ASVs | DADA2 docs | approximates full pooling (quadratic) in linear time; default FALSE misses cross-sample singletons |
| Deblur `--p-trim-length` one fixed value | Amir 2017 *mSystems* 2:e00191-16 | the positive filter requires a single read length |
| 16S copy-number correction: report, do not assume | Louca 2018 *Microbiome* 6:41 | predictable only near reference genomes; correction can ADD error ("unsolved problem") |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Near-zero merge rate | truncLen below the overlap budget | recompute budget; keep length, loosen `maxEE` R |
| Large read fraction "chimeric" | primers not trimmed (degenerate bases) | cutadapt `--discard-untrimmed` before filtering |
| `plotErrors` fitted line diverges from points | binned quality (NovaSeq/NextSeq) | enforce monotonic error matrix; nf-core/ampliseq `--illumina_novaseq` |
| ASVs vanish/appear when runs split | one error model fit across runs | per-run `learnErrors`, then `mergeSequenceTables` |
| Few reads pass filter | `maxEE` too strict or truncLen too long (low-Q tail) | loosen `maxEE`, shorten truncLen within the budget |
| ITS taxa lost / poor merging | fixed `truncLen` on ITS | cutadapt + ITSxpress, then `truncLen=0` |

## References

- Callahan BJ, McMurdie PJ, Rosen MJ, Han AW, Johnson AJA, Holmes SP. 2016. DADA2: high-resolution sample inference from Illumina amplicon data. *Nat Methods* 13:581-583.
- Callahan BJ, McMurdie PJ, Holmes SP. 2017. Exact sequence variants should replace operational taxonomic units in marker-gene data analysis. *ISME J* 11:2639-2643.
- Callahan BJ, Wong J, Heiner C, Oh S, Theriot CM, Gulati AS, McGill SK, Dougherty MK. 2019. High-throughput amplicon sequencing of the full-length 16S rRNA gene with single-nucleotide resolution. *Nucleic Acids Res* 47:e103.
- Amir A, McDonald D, Navas-Molina JA, Kopylova E, Morton JT, Zech Xu Z, Kightley EP, Thompson LR, Hyde ER, Gonzalez A, Knight R. 2017. Deblur rapidly resolves single-nucleotide community sequence patterns. *mSystems* 2:e00191-16.
- Martin M. 2011. Cutadapt removes adapter sequences from high-throughput sequencing reads. *EMBnet J* 17:10-12.
- Rivers AR, Weber KC, Gardner TG, Liu S, Armstrong SD. 2018. ITSxpress: software to rapidly trim internally transcribed spacer sequences with quality scores for marker gene analysis. *F1000Research* 7:1418.
- Rognes T, Flouri T, Nichols B, Quince C, Mahe F. 2016. VSEARCH: a versatile open source tool for metagenomics. *PeerJ* 4:e2584.
- Bolyen E, Rideout JR, Dillon MR, et al. 2019. Reproducible, interactive, scalable and extensible microbiome data science using QIIME 2. *Nat Biotechnol* 37:852-857.
- Schloss PD. 2021. Amplicon sequence variants artificially split bacterial genomes into separate clusters. *mSphere* 6:e00191-21.
- Pan P, et al. 2023. Microbial diversity biased estimation caused by intragenomic heterogeneity and interspecific conservation of 16S rRNA genes. *Appl Environ Microbiol* 89:e02108-22.
- Louca S, Doebeli M, Parfrey LW. 2018. Correcting for 16S rRNA gene copy numbers in microbiome surveys remains an unsolved problem. *Microbiome* 6:41.
- Davis NM, Proctor DM, Holmes SP, Relman DA, Callahan BJ. 2018. Simple statistical identification and removal of contaminant sequences in marker-gene and metagenomics data. *Microbiome* 6:226.

## Related Skills

- taxonomy-assignment - Assign taxonomy to the ASVs produced here
- diversity-analysis - Alpha/beta diversity of the resulting community table
- differential-abundance - Compositional DA on the ASV/feature table
- qiime2-workflow - The QIIME2 CLI equivalent of this R workflow
- read-qc/adapter-trimming - cutadapt primer removal before DADA2
- metagenomics/kraken-classification - Shotgun (not amplicon) read classification
- metagenomics/abundance-estimation - Shared compositional/normalization theory
- metagenomics/contamination-controls - Negative/positive controls and decontam for low-biomass (shotgun analogue)
- phylogenetics/tree-io - Phylogenetic tree for UniFrac / Faith PD
- workflows/microbiome-pipeline - End-to-end amplicon pipeline
<!-- END FILE: microbiome/amplicon-processing/SKILL.md -->

## 子目录：microbiome/differential-abundance

<!-- BEGIN FILE: microbiome/differential-abundance/SKILL.md -->
---
name: bio-microbiome-differential-abundance
description: Tests which individual taxa differ between groups on an amplicon ASV/feature table (phyloseq) using compositionally-aware methods - ALDEx2 (Dirichlet-MC CLR, conservative), ANCOM-BC2/ANCOMBC (sampling-fraction bias correction, structural zeros, passed_ss, default p_adj_method=holm), MaAsLin2/MaAsLin3 (multivariable GLM, random effects, prevalence/abundance split), LinDA (CLR mixed-model regression), ZicoSeq (permutation FDR), LEfSe, and q2-composition ancombc. Covers why the hit list depends more on the DA tool than the biology (Nearing benchmark) so the deliverable is a CONSENSUS of >=2 tools, why a relative change is not absolute without a load anchor, the prevalence-filter knob, BH/FDR plus an effect-size floor, and why DESeq2/edgeR misfire here. Use when finding differentially abundant taxa, handling covariates or longitudinal designs, or choosing a method. Whole-community diversity -> diversity-analysis; shotgun DA -> metagenomics/metagenome-visualization; CoDA theory -> metagenomics/abundance-estimation
tool_type: r
primary_tool: ALDEx2
---

## Version Compatibility

Reference examples tested with: ALDEx2 1.34+, ANCOMBC 2.4+, Maaslin2 1.16+, MicrobiomeStat 1.2+ (LinDA), GUniFrac 1.8+ (ZicoSeq), phyloseq 1.46+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

ANCOM-BC2 changed argument names between `ancombc()` and `ancombc2()`, and its default `p_adj_method` is `holm`, not `BH` - confirm both against the installed version. The MaAsLin3 `maaslin3()` API differs from MaAsLin2's `Maaslin2()`.

# Differential Abundance Testing

**"Find which taxa differ between my groups"** -> Run two or more compositionally-aware DA tools and report their consensus - because the significant-taxa list is a property of the tool as much as of the sample, and a relative-abundance change is not an absolute change.
- R: `ALDEx2::aldex(counts, conds, test='t', effect=TRUE, denom='all')` then a second tool (`ANCOMBC::ancombc2()` or `MicrobiomeStat::linda()`)

Scope: per-taxon DA on an amplicon feature table. Whole-community alpha/beta/PERMANOVA -> diversity-analysis. Shotgun profiler-table DA -> metagenomics/metagenome-visualization. Shared compositional/closure/CLR/zero theory -> metagenomics/abundance-estimation. Collapse ASVs to genus/species first -> taxonomy-assignment. QIIME2 CLI route -> qiime2-workflow.

## The Single Most Important Modern Insight -- Which Taxa Are "Significant" Depends More on the Tool Than on the Biology

Run ALDEx2, ANCOM-BC2, MaAsLin2, and LinDA on the same ASV table and the four significant-taxa lists overlap but disagree (Nearing 2022 *Nat Commun* 13:342, across 38 datasets). So the deliverable is NOT "the differential taxa" - it is the CONSENSUS of >=2 compositionally-aware tools, every tool NAMED: the intersection is high-confidence, the union is exploratory, and a single-tool hit is tentative. Picking the tool with the prettiest volcano is p-hacking by software (uncorrected multiplicity hidden in the method menu). Three corollaries:

1. **A relative-abundance increase is not an absolute increase.** Microbiome counts are compositional - the sequencer fixes the total, so one taxon blooming forces every other taxon's proportion down (the blooming-taxon illusion). "Taxon X increased" is a statement about its SHARE unless an external load anchor (spike-in / flow cytometry / qPCR, see metagenomics/abundance-estimation) or MaAsLin3's absolute-abundance mode licenses an absolute claim.
2. **Uncorrected Wilcoxon/t-test on raw relative abundances is wrong twice in one line** - closure (reference-frame) AND multiple testing. But a BH-corrected simple test, honestly labelled as relative, can replicate BETTER than a sophisticated model (Pelto 2025): the forbidden thing is the uncorrected, closure-blind form, not simple tests per se.
3. **There is no settled best tool.** The benchmarks optimize different criteria, so they rank tools differently. Consensus-of-tools is the only stance that survives all of them.

## The Benchmark Landscape (no settled winner)

| Benchmark | Optimized for | Verdict |
|-----------|---------------|---------|
| Nearing 2022 *Nat Commun* 13:342 | cross-method consistency | ALDEx2 + ANCOM-II most consistent and most conservative; LEfSe/edgeR flag far more, agree less |
| Yang & Chen 2022 *Microbiome* 10:130 | FDR-power balance | ZicoSeq / LinDA / ANCOM-BC-family best |
| Yang & Chen 2023 *Brief Bioinform* 24:bbac607 | correlated (repeated-measures) designs | use a mixed-model-capable tool (LinDA, MaAsLin2, ANCOM-BC2) |
| Pelto 2025 *Brief Bioinform* 26(2):bbaf130 | cross-study replicability | elementary BH-corrected methods most replicable; ANCOM-BC2 worst |

Report the disagreement AS the result; verify current best practice against the latest tool docs rather than hard-coding one method.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| ALDEx2 | Fernandes 2014 *Microbiome* 2:15 | Dirichlet Monte-Carlo posterior + CLR; tests each draw; reports expected effect + BH-adjusted p | conservative two-group anchor; small-to-moderate n |
| ANCOM-BC2 | Lin & Peddada 2024 *Nat Methods* 21:83 | estimates per-sample sampling fraction and bias-corrects; structural zeros; pseudo-count sensitivity (`passed_ss`) | interpretable LFC + CI; covariates; multi-group |
| MaAsLin2 | Mallick 2021 *PLoS Comput Biol* 17:e1009442 | general (mixed) linear model on transformed abundance | multivariable / longitudinal / metadata-rich |
| MaAsLin3 | Nickols 2026 *Nat Methods* 23:554 | splits abundance (level when present) from prevalence (present/absent); absolute-abundance mode | prevalence-vs-abundance separation; load data available |
| LinDA | Zhou 2022 *Genome Biol* 23:95 | CLR regression with mode-based bias correction; asymptotic FDR | large cohorts; fast; native mixed model |
| ZicoSeq | Yang & Chen 2022 *Microbiome* 10:130 | reference-taxa normalization + permutation FDR; winsorization | covariates; non-parametric permutation p; strong FP control |
| LEfSe | Segata 2011 *Genome Biol* 12:R60 | Kruskal-Wallis + LDA effect size | exploratory biomarker discovery; NOT a formal FDR-controlled test |
| DESeq2 | Love 2014 *Genome Biol* 15:550 | RNA-seq median-of-ratios size factor | caveat only; geometric-mean reference dies on sparse zero-heavy tables |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Two groups, want a trustworthy conservative anchor | ALDEx2 | Dirichlet-MC + CLR; most reproducible/conservative (Nearing); gate on effect size |
| Need interpretable LFC + CI, structural zeros, multi-group | ANCOM-BC2 | models and corrects per-sample sampling fraction; global/pairwise/Dunnett/trend; `passed_ss` |
| Large cohort, covariates, speed, mixed model | LinDA | CLR regression + bias mode; asymptotic FDR; fast; random effects in the formula |
| Covariates + permutation-grounded non-parametric p | ZicoSeq | reference-taxa frame + permutation FDR |
| Longitudinal / many covariates / flexible GLM | MaAsLin2 | `fixed_effects` + `random_effects`; normalization/transform menu |
| Prevalence-vs-abundance separation or absolute abundance | MaAsLin3 | logistic prevalence model + abundance model; load-data hook |
| Inside a QIIME2 CLI pipeline | qiime composition ancombc + tabulate/da-barplot | native artifact flow (v1 ANCOM-BC; go to R for v2 `passed_ss`/multi-group) -> qiime2-workflow |
| Repeated / paired samples | any tool above WITH a random effect | ignoring subject structure is pseudo-replication |
| ALWAYS | run >=2 of the above, report the consensus | tool choice drives the hit list more than biology (Nearing 2022) |
| Shotgun species table, not amplicon | -> metagenomics/metagenome-visualization | same CoDA theory; different upstream pipeline |
| Uncorrected t-test/Wilcoxon on TSS proportions | DO NOT | closure biases the test and there is no FDR control |

## Filter Before Testing (a modeling knob, not housekeeping)

**Goal:** Drop rare features before testing so the BH denominator is not crushed and log/CLR transforms are well-behaved.

**Approach:** Keep features present in at least 10-25% of samples (and optionally a mean-abundance floor); declare the threshold and confirm the headline result is not knife-edge-sensitive to it. Every tool exposes this (`prv_cut`, `min_prevalence`, `prev.filter`).

```r
library(phyloseq)
ps <- readRDS('phyloseq_object.rds')
# prv_cut 0.10: a feature must appear in >= 10% of samples; raising to 0.25 removes more tests
# (smaller BH correction, more power on survivors) but discards rare-but-real taxa - a declared choice
keep <- filter_taxa(ps, function(x) sum(x > 0) >= 0.10 * nsamples(ps), TRUE)
```

## ALDEx2: The Conservative Floor of the Consensus

**Goal:** Identify taxa that differ between two groups while propagating the sampling uncertainty of low-count features.

**Approach:** Draw `mc.samples` Monte-Carlo instances from a Dirichlet posterior of the counts (this IS the zero handling - no explicit pseudocount), CLR-transform each instance against the geometric mean of all features (`denom='all'`), run the test on every draw, and report the EXPECTED effect size and BH-adjusted p over the draws.

```r
library(ALDEx2)
counts <- as.matrix(otu_table(ps))            # integer counts, taxa in ROWS
if (!taxa_are_rows(ps)) counts <- t(counts)
groups <- as.character(sample_data(ps)$Group)

# mc.samples 128: standard Monte-Carlo draws; 256+ for publication (more stable expected p)
res <- aldex(counts, groups, mc.samples = 128, test = 't', effect = TRUE, denom = 'all')
# we.eBH = Welch expected BH-adjusted p (report this, NOT we.ep); wi.eBH = Wilcoxon equivalent
# effect = median standardized effect = median(diff.btw / max(diff.win)); the primary decision variable
hits <- res[res$we.eBH < 0.05 & abs(res$effect) > 1, ]   # q AND effect floor (Gloor: gate on effect, not p alone)
```

Gate on effect size AND q, not p alone: with large n trivially small CLR differences become "significant," and Gloor's own guidance is that `|effect| > 1` is a strong ~2-SD signal. For >2 groups use `aldex.kw()`; for covariates the `aldex.glm()` + model.matrix route works but ALDEx2 is weakest here - prefer ANCOM-BC2/LinDA/MaAsLin2 for serious covariate or random-effect modeling.

## ANCOM-BC2: Bias-Corrected LFC With a Sensitivity Safeguard

**Goal:** Estimate an interpretable bias-corrected log-fold-change per taxon, with covariate adjustment, structural-zero handling, and a flag for hits that are hostage to the pseudo-count.

**Approach:** Model log(observed count) as a function of covariates, estimate each sample's log sampling fraction as an offset and subtract it, then refit across a range of pseudo-counts and record how often each q-value flips (`passed_ss`).

```r
library(ANCOMBC)
out <- ancombc2(data = ps, fix_formula = 'Group + Age + Sex',
                rand_formula = NULL,        # '(1 | SubjectID)' for repeated measures - see Failure Modes
                p_adj_method = 'BH',        # DEFAULT is 'holm'; set 'BH' deliberately for FDR
                prv_cut = 0.10, lib_cut = 1000,
                group = 'Group', struc_zero = TRUE, pseudo_sens = TRUE,
                global = FALSE, pairwise = FALSE, n_cl = 2)
res <- out$res
# a confident hit is BOTH significant AND robust to the pseudo-count. ANCOM-BC2 suffixes the
# diff_/passed_ss_ columns with the literal model-matrix coefficient (variable + factor level,
# verbatim case, e.g. 'Grouptreated') - match it by pattern rather than hard-coding the case.
dcol <- grep('^diff_Group', names(res), value = TRUE)[1]
robust <- res[res[[dcol]] & res[[sub('^diff_', 'passed_ss_', dcol)]], ]
```

`passed_ss` is the most valuable ANCOM-BC2-specific feature: a CLR/log model on sparse data is hostage to the zero-replacement constant, and `passed_ss` quantifies that per taxon. A hit with `passed_ss == FALSE` depends on the arbitrary pseudo-count - do not report it as confident. For >2 groups set `global=TRUE` (omnibus), `pairwise=TRUE` (mdFDR-controlled pairs), `dunnet=TRUE`, or `trend=TRUE`; results land in `out$res_global`/`res_pair`/`res_dunn`/`res_trend`.

## LinDA: Fast CLR Regression With Native Mixed Models

**Goal:** Get FDR-controlled log2-fold-changes on a large cohort, including repeated-measures designs, without Monte-Carlo or EM cost.

**Approach:** Fit ordinary linear regression on the CLR-transformed table covariate by covariate, estimate the compositional bias as the mode of the per-feature coefficients and subtract it; a random effect in the formula makes it a linear mixed model.

```r
library(MicrobiomeStat)
otu <- as.data.frame(otu_table(ps)); if (!taxa_are_rows(ps)) otu <- t(otu)
meta <- as.data.frame(sample_data(ps))
fit <- linda(feature.dat = otu, meta.dat = meta,
             formula = '~ Group + Age + (1 | SubjectID)',   # random effect -> mixed model
             feature.dat.type = 'count', prev.filter = 0.10, alpha = 0.05)
fit$output[[1]]   # names(fit$output) are the model-matrix coefficient columns (e.g. 'Grouptreated' - the factor level keeps its case); per-feature: log2FoldChange, lfcSE, stat, pvalue, padj, reject
```

LinDA is the natural fast modern entry in a consensus panel and the cleanest route to mixed models. Yang & Chen rate it among the best FDR-power trade-offs.

## MaAsLin2 / MaAsLin3 and ZicoSeq (the rest of the panel)

**Goal:** Fit covariate-rich or longitudinal differential-abundance models, or add a permutation-based panel member, when ALDEx2/ANCOM-BC2/LinDA do not cover the design.

**Approach:** Use MaAsLin2/3 for multivariable GLMs with random effects, or ZicoSeq for a non-parametric permutation-FDR test against empirically selected reference taxa.

MaAsLin2 fits a flexible per-feature GLM; its package DEFAULT is TSS + LOG + LM (not CLR), and `random_effects` is the canonical route for longitudinal designs. NOTE the orientation gotcha: it expects features in COLUMNS, samples in rows.

```r
library(Maaslin2)
fit <- Maaslin2(input_data = as.data.frame(t(otu)), input_metadata = meta,
                output = 'maaslin2_out', fixed_effects = c('Group', 'Age'),
                random_effects = c('SubjectID'),
                normalization = 'TSS', transform = 'LOG', analysis_method = 'LM',
                min_prevalence = 0.10, max_significance = 0.05)
# writes all_results.tsv / significant_results.tsv with columns feature, metadata, coef, pval, qval
```

MaAsLin3 (`maaslin3()`) splits each feature into an abundance model (level when present) and a logistic prevalence model (present/absent) tested jointly, and can ingest total-load measurements for absolute-abundance inference. ZicoSeq (`GUniFrac::ZicoSeq()`) winsorizes, posterior-samples, normalizes against empirically selected reference taxa, and returns permutation FDR (`zc$p.adj.fdr`) - a non-parametric panel member that accepts covariates via `adj.name`.

## Consensus: Intersect the Tools

**Goal:** Convert two or more per-tool hit sets into a confidence-graded result instead of one tool's answer.

**Approach:** Collect the significant feature SETS (BH within each tool), then report the intersection as high-confidence, the union as exploratory, and tabulate, per taxon, how many of N tools agree and which ones. Never pool p-values across tools.

```r
sig_aldex <- rownames(res)[res$we.eBH < 0.05 & abs(res$effect) > 1]
sig_linda <- rownames(fit$output[[1]])[fit$output[[1]]$reject]   # [[1]] = the group coefficient (named 'Grouptreated')
confident  <- intersect(sig_aldex, sig_linda)   # high-confidence
exploratory <- union(sig_aldex, sig_linda)       # report with the tool that found each
```

## Per-Method Failure Modes

### Cherry-picking the tool with the prettiest result
**Trigger:** running several tools and reporting only the one(s) that flag the favored taxon. **Mechanism:** that is uncorrected multiplicity hidden in the method menu (p-hacking by software). **Symptom:** "the recommended method found X" with no mention of the tools that disagreed. **Fix:** decide the panel a priori, report ALL tools, intersect for confident hits, disclose disagreement.

### Uncorrected Wilcoxon/t-test on relative abundances
**Trigger:** a per-taxon Wilcoxon/t-test on TSS proportions with no FDR correction. **Mechanism:** closure makes a naive test call every taxon "decreased" when one blooms, and hundreds of uncorrected tests inflate false positives. **Symptom:** dozens of "significant" taxa, all in the same direction, no q-values. **Fix:** use a CoDA/reference-frame tool; if a simple test is used, BH-correct it and label the comparison as relative (Pelto 2025).

### Pseudo-replication of repeated measures
**Trigger:** longitudinal/paired samples treated as independent rows. **Mechanism:** fewer independent units than rows inflates significance. **Symptom:** implausibly small p-values on a small subject count. **Fix:** a random effect - ANCOM-BC2 `rand_formula='(1|SubjectID)'`, MaAsLin2 `random_effects='SubjectID'`, LinDA `(1|SubjectID)` in the formula. Cross-check ANCOM-BC2 mixed-model output against LinDA/MaAsLin2 (GitHub issue #111 reported `rand_formula` correctness problems in some versions).

### Prevalence filter set blindly
**Trigger:** an undeclared prevalence cut, or none at all. **Mechanism:** the cut decides which taxa are even tested and thus the BH landscape - it is a modeling choice. **Symptom:** the hit list changes materially between `prv_cut=0.1` and `0.25`. **Fix:** declare and justify the threshold; confirm the headline result survives moving it.

### Relative change reported as absolute
**Trigger:** "taxon X doubled" from a closed table with no load data. **Mechanism:** one taxon blooming compresses every other proportion. **Symptom:** whole-community "depletion" that is really one taxon rising. **Fix:** anchor to load (spike-in/flow/qPCR) or MaAsLin3 absolute mode; otherwise state the claim is relative.

### DESeq2/edgeR on a sparse 16S table
**Trigger:** RNA-seq median-of-ratios / TMM on a zero-heavy ASV table. **Mechanism:** the geometric-mean size-factor reference collapses on zeros and the "most features unchanged" assumption is violated. **Symptom:** degenerate size factors, errors, or inflated hit counts that disagree with CoDA tools (Nearing). **Fix:** use a compositional tool; if DESeq2 is unavoidable, the `poscounts` estimator is the minimum mitigation - present as a caveat, not a recipe.

### ANCOM-BC2 hit held hostage by the pseudo-count
**Trigger:** reporting `diff_* == TRUE` without checking `passed_ss_*`. **Mechanism:** significance depends on the arbitrary zero-replacement constant. **Symptom:** a hit that vanishes when the pseudo-count changes. **Fix:** require `diff_* & passed_ss_*` for a confident call.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Prevalence cut 10-25% (`prv_cut`/`min_prevalence`/`prev.filter`) | Nearing 2022; tool defaults (0.10) | rare features carry little information and crush the BH denominator; declare the value and test sensitivity |
| BH q <= 0.05 across taxa, within each tool | Benjamini-Hochberg 1995 *JRSS B* 57:289 | hundreds-thousands of features make uncorrected p meaningless; do not pool p across tools |
| ALDEx2 `|effect| > 1` (with q <= 0.05) | Gloor 2016 *J Comput Graph Stat* 25:971 | effect is a standardized median-ratio; ~2 SD is a strong signal; large n makes trivial diffs "significant" |
| ALDEx2 `mc.samples` = 128 (256+ for publication) | Fernandes 2014 *Microbiome* 2:15 | Monte-Carlo draws; more draws stabilize the expected p |
| ANCOM-BC2 `passed_ss == TRUE` required | Lin & Peddada 2024 *Nat Methods* 21:83 | flags hits whose significance is hostage to the pseudo-count |
| Consensus of >=2 compositionally-aware tools | Nearing 2022 *Nat Commun* 13:342 | tool choice drives the hit list more than biology; intersection = confident |
| ZicoSeq permutations `perm.no` >= 99 | Yang & Chen 2022 *Microbiome* 10:130 | permutation FDR resolution; raise for finer tail p |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| ALDEx2 returns NA effects / errors | proportions or non-integer matrix passed | feed integer COUNTS with taxa in rows |
| `passed_ss` column missing | `pseudo_sens = FALSE` | set `pseudo_sens = TRUE` (the default) |
| Far fewer hits than expected | ANCOM-BC2 `p_adj_method` left at `holm` | set `p_adj_method = 'BH'` deliberately if FDR is wanted |
| MaAsLin2 finds nothing / orientation error | features in rows, not columns | transpose so samples are rows, features columns |
| Mixed-model hits disagree across tools | `rand_formula` correctness varies by version | cross-check ANCOM-BC2 against LinDA/MaAsLin2 |
| Tools disagree on the hit list | normal - tool choice drives results | report the consensus and the disagreement, do not cherry-pick |
| Many "depleted" taxa in a host/plant sample | host mitochondria/chloroplast 16S inflates the table | filter Mitochondria/Chloroplast features (see taxonomy-assignment) before DA |
| Contaminant ASVs among the hits (low-biomass) | reagent kitome not removed before DA | run decontam upstream with negative controls (amplicon-processing; metagenomics/contamination-controls) |

## References

- Fernandes AD, Reid JNS, Macklaim JM, McMurrough TA, Edgell DR, Gloor GB. 2014. Unifying the analysis of high-throughput sequencing datasets: characterizing RNA-seq, 16S rRNA gene sequencing and selective growth experiments by compositional data analysis. *Microbiome* 2:15.
- Gloor GB, Macklaim JM, Fernandes AD. 2016. Displaying variation in large datasets: plotting a visual summary of effect sizes. *J Comput Graph Stat* 25:971-979.
- Lin H, Peddada SD. 2020. Analysis of compositions of microbiomes with bias correction (ANCOM-BC). *Nat Commun* 11:3514.
- Lin H, Peddada SD. 2024. Multigroup analysis of compositions of microbiomes with covariate adjustments and repeated measures (ANCOM-BC2). *Nat Methods* 21:83-91.
- Mallick H, Rahnavard A, McIver LJ, et al. 2021. Multivariable association discovery in population-scale meta-omics studies. *PLoS Comput Biol* 17:e1009442.
- Nickols WA, Kuntz T, Shen J, et al. 2026. MaAsLin 3: refining and extending generalized multivariable linear models for meta-omic association discovery. *Nat Methods* 23:554-564.
- Zhou H, He K, Chen J, Zhang X. 2022. LinDA: linear models for differential abundance analysis of microbiome compositional data. *Genome Biol* 23:95.
- Yang L, Chen J. 2022. A comprehensive evaluation of microbial differential abundance analysis methods: current status and potential solutions. *Microbiome* 10:130.
- Yang L, Chen J. 2023. Benchmarking differential abundance analysis methods for correlated microbiome sequencing data. *Brief Bioinform* 24:bbac607.
- Pelto J, Auranen K, Kujala JV, Lahti L. 2025. Elementary methods provide more replicable results in microbial differential abundance analysis. *Brief Bioinform* 26(2):bbaf130.
- Nearing JT, Douglas GM, Hayes MG, et al. 2022. Microbiome differential abundance methods produce different results across 38 datasets. *Nat Commun* 13:342.
- Segata N, Izard J, Waldron L, et al. 2011. Metagenomic biomarker discovery and explanation. *Genome Biol* 12:R60.
- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biol* 15:550.
- Benjamini Y, Hochberg Y. 1995. Controlling the false discovery rate: a practical and powerful approach to multiple testing. *J R Stat Soc Series B* 57:289-300.

## Related Skills

- diversity-analysis - Whole-community alpha/beta/PERMANOVA; answer "do the communities differ" before "which taxa differ"
- taxonomy-assignment - Collapse ASVs to genus/species before per-taxon testing
- amplicon-processing - Produces the ASV feature table tested here
- qiime2-workflow - The qiime composition ancombc CLI route
- metagenomics/abundance-estimation - Shared compositional/closure/CLR/zero/load-anchor theory
- metagenomics/metagenome-visualization - The same DA mechanics on shotgun profiler tables
- experimental-design/multiple-testing - FDR control and multiplicity across taxa
<!-- END FILE: microbiome/differential-abundance/SKILL.md -->

## 子目录：microbiome/diversity-analysis

<!-- BEGIN FILE: microbiome/diversity-analysis/SKILL.md -->
---
name: bio-microbiome-diversity-analysis
description: Alpha and beta diversity of an amplicon (16S/ITS) ASV/OTU community table - observed features, Shannon, Pielou evenness, Faith PD, Bray-Curtis, Jaccard, weighted/unweighted/generalized UniFrac, Aitchison/RPCA - via QIIME2 core-metrics-phylogenetic, phyloseq/vegan, and scikit-bio. Covers the three knobs that set the answer before it is seen (rarefaction sampling depth, the tree, the metric), why core-metrics silently deletes samples below the sampling depth, why de novo trees lose to SEPP fragment-insertion and Greengenes2, why unweighted and weighted UniFrac can flip the story, why observed features is an ASV count not a species count, the QIIME2-log2 vs R-ln Shannon mismatch, and pairing PERMANOVA (adonis2) with betadisper. Use when summarizing whole-community richness/evenness or testing group differences in community structure. Per-taxon testing -> differential-abundance. Shotgun tables -> metagenomics/metagenome-visualization. Shared CoDA/rarefaction theory -> metagenomics/abundance-estimation.
tool_type: mixed
primary_tool: phyloseq
---

## Version Compatibility

Reference examples tested with: phyloseq 1.46+, vegan 2.6+, picante 1.8+, GUniFrac 1.8+, scikit-bio 0.6+, QIIME2 2024.2+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `qiime <plugin> <action> --help` to confirm flags
- Python: `pip show scikit-bio` then `help(skbio.diversity.beta_diversity)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

scikit-bio 0.6.0 renamed OTU to taxon across the API and drifted metric kwargs (`otu_ids=` vs newer forms) - discover names with `skbio.diversity.get_beta_diversity_metrics()` before hard-coding. UniFrac/Faith PD results inherit the tree (de novo vs SEPP vs Greengenes2 reference build) AND the chosen sampling depth - record both alongside the QIIME2 release that produced the `.qza` artifacts.

# Diversity Analysis

**"Compare microbial diversity across my samples"** -> Summarize within-sample richness/evenness (alpha) and between-sample dissimilarity (beta) - but only after declaring the rarefaction depth, the tree, and the metric, because each is a knob that sets the answer before it is seen.
- CLI: `qiime diversity core-metrics-phylogenetic --i-phylogeny rooted-tree.qza --i-table table.qza --p-sampling-depth N --m-metadata-file md.tsv --output-dir cm/`
- R: `estimate_richness(ps_rare)` for alpha; `UniFrac(ps_rare, weighted=)` / `vegdist()` then `adonis2()` + `betadisper()` for beta

Scope: whole-community summary (a number or ordination per sample) of an amplicon ASV/OTU table plus a tree. Per-taxon between-group testing -> differential-abundance. Shotgun profiler tables (MetaPhlAn/Bracken) -> metagenomics/metagenome-visualization. The shared CoDA and rarefaction-debate theory lives in metagenomics/abundance-estimation; the Hill-number and PERMANOVA-dispersion theory in metagenomics/metagenome-visualization - cross-referenced here, not re-derived. Tree handling -> phylogenetics/tree-io.

## The Single Most Important Modern Insight -- A Diversity Number Is the Output of Three Knobs Turned Before the Answer Appears

An alpha or beta diversity value is not a measurement of the community; it is the output of three choices made before the number appears - the rarefaction DEPTH, the TREE, and the METRIC. Turn them differently and the conclusion can change. The job is to declare all three and show the result survives a second reasonable choice, not to run `core-metrics-phylogenetic` and read the p-value. The quietest and most dangerous knob is the depth:

1. **`--p-sampling-depth` is a sample-deletion knob in a normalization costume.** core-metrics rarefies every sample to the depth and, per the QIIME2 docs, silently drops every sample whose total count is below it - no warning, just fewer points in the PCoA. The dropped samples are the lowest-yield ones (the lowest-biomass swab, the sickest patient, the failed extraction), so the loss is almost never random. Pick the depth from the feature-table summary plus the alpha-rarefaction plateau, report the depth AND the dropped samples, and confirm the conclusion at a nearby depth. Rarefying to `min(sample_sums)` is the worst of both worlds - one tiny library drags everyone to noise.
2. **UniFrac and Faith PD are only as real as the tree, and the tree is a model not a property of the data.** A de novo MAFFT+FastTree tree from ~250 bp reads is poorly resolved and arbitrarily midpoint-rooted (Janssen 2018); SEPP fragment-insertion into a full-length reference, or Greengenes2 placement, gives stable topology and correct associations - and SEPP/GG2 align 16S with shotgun (McDonald 2024). SEPP also drops fragments that fail to insert, a second silent table-shrink.
3. **Rarefy for diversity, never for differential abundance.** Rarefaction-to-even-depth is defensible for alpha/beta (Schloss 2024); for DA it discards count information a compositional model needs (McMurdie 2014). Keep the raw counts; rarefy only into the diversity branch; route DA to differential-abundance on the unrarefied table.

## Tool / Metric Taxonomy

| Metric / tool | Citation | What it measures / does | When |
|---------------|----------|-------------------------|------|
| Observed features | - | ASV richness (Hill q=0); most depth-sensitive; an ASV count, not species | richness, but report denoising params; prefer Hill q1/q2 |
| Shannon | - | entropy = richness+evenness (Hill q=1 = exp(H')); QIIME2 log2/bits, R ln/nats | balanced diversity; report exp(H') to dodge the base |
| Pielou evenness | Pielou 1966 *J Theor Biol* 13:131 | H'/ln(S); 0-1; isolates evenness from richness | when evenness is the question |
| Faith PD | Faith 1992 *Biol Conserv* 61:1 | sum of branch lengths spanning observed taxa; phylogenetic q=0 | amplicon-native richness; needs a tree |
| Jaccard | - | presence/absence dissimilarity; no tree | membership turnover; depth/rare-ASV sensitive |
| Bray-Curtis | - | abundance dissimilarity; no tree; compositionally incoherent | abundance default; intuitive, label the caveat |
| Unweighted UniFrac | Lozupone 2005 *Appl Environ Microbiol* 71:8228 | branch length unique to one community (presence/absence) | rare/divergent lineages + topology; needs a tree |
| Weighted UniFrac | Lozupone 2007 *Appl Environ Microbiol* 73:1576 | branch length weighted by abundance difference | abundant-lineage shifts; needs a tree |
| Generalized UniFrac | Chen 2012 *Bioinformatics* 28:2106 | alpha in [0,1] interpolating unweighted-weighted | alpha=0.5 compromise; powerful for moderately abundant lineages |
| Aitchison / RPCA | Martino 2019 *mSystems* 4:e00016-19 | CLR + matrix completion; ordination with feature loadings | compositionally coherent; sparse data; no pseudocount |
| SEPP insertion | Janssen 2018 *mSystems* 3:e00021-18 | places ASVs into a full-length reference tree | the preferred tree for short reads |
| Greengenes2 | McDonald 2024 *Nat Biotechnol* 42:715 | unified genome+16S reference tree | makes 16S UniFrac comparable to shotgun |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Need a phylogenetic metric (UniFrac, Faith PD) | SEPP-into-reference or Greengenes2 tree | de novo from short reads is unstable (Janssen 2018) |
| De novo tree is the only option | treat unweighted UniFrac with suspicion | topology noise on ~250 bp reads dominates it |
| Change is in rare/low-abundance lineages | unweighted UniFrac, observed features | presence/absence + topology see rare taxa |
| Change is a bloom of dominant taxa | weighted UniFrac, Bray-Curtis | abundance-weighted metrics see dominant shifts |
| Do not want to metric-shop | generalized UniFrac alpha=0.5 + report both un/weighted | Chen 2012 compromise; single-metric hit is tentative |
| Richness vs evenness question | observed/Faith (q0) AND Shannon-exp (q1) / InvSimpson (q2) | span the richness-evenness spectrum |
| Compositional, want axis-driving taxa | RPCA (DEICODE/gemelli) | CLR ordination with interpretable loadings |
| Picking a rarefaction depth | feature-table summarize + alpha-rarefaction plateau | depth must retain samples AND saturate richness |
| Per-taxon "which bug changed" | -> differential-abundance | diversity is whole-community; DA is per-feature |
| Shotgun profiler table, not amplicon | -> metagenomics/metagenome-visualization | no per-feature tree; different idiom |

## Choosing the Sampling Depth (the biggest lever)

**Goal:** Pick a rarefaction depth that saturates richness while retaining an acceptable fraction of samples, and know exactly which samples were dropped.

**Approach:** Read the per-sample frequency distribution from the feature-table summary, find where the alpha-rarefaction curve plateaus, set the depth there, then declare the depth and the dropped-sample list.

```bash
qiime feature-table summarize --i-table table.qza --o-visualization table.qzv   # per-sample frequencies; the depth lives here

qiime diversity alpha-rarefaction \
    --i-table table.qza --i-phylogeny rooted-tree.qza \
    --p-max-depth 20000 \   # set near the median sample depth; the curve panel shows survivors per depth
    --m-metadata-file metadata.tsv --o-visualization alpha-rarefaction.qzv

qiime diversity core-metrics-phylogenetic \
    --i-phylogeny rooted-tree.qza --i-table table.qza \
    --p-sampling-depth 10000 \   # on the observed-features plateau; SILENTLY DROPS samples below this
    --m-metadata-file metadata.tsv --output-dir core-metrics-results
```

core-metrics-phylogenetic rarefies the table, computes the four alpha vectors (`faith_pd_vector`, `observed_features_vector`, `shannon_vector`, `evenness_vector`) and four beta matrices (`unweighted_unifrac_`, `weighted_unifrac_`, `jaccard_`, `bray_curtis_distance_matrix`), and produces a PCoA + Emperor plot for each beta metric. The non-phylogenetic twin `qiime diversity core-metrics` drops Faith PD and both UniFracs and needs no tree.

## Building the Tree (a modeling choice, not a fixed step)

**Goal:** Obtain a phylogeny over the ASVs that does not inject topology noise into UniFrac/Faith PD.

**Approach:** Prefer SEPP fragment-insertion into a full-length reference (or Greengenes2 placement) over a de novo build from short reads; for de novo, mask the alignment and accept that unweighted UniFrac will be shaky.

```bash
qiime fragment-insertion sepp \
    --i-representative-sequences rep-seqs.qza \
    --i-reference-database sepp-refs-gg-13-8.qza \
    --p-threads 4 \
    --o-tree insertion-tree.qza --o-placements insertion-placements.qza

qiime fragment-insertion filter-features \
    --i-table table.qza --i-tree insertion-tree.qza \
    --o-filtered-table table-sepp.qza --o-removed-table removed-table.qza   # fragments that failed to insert are DROPPED
```

De novo is `qiime phylogeny align-to-tree-mafft-fasttree` (MAFFT align -> mask -> FastTree2 -> midpoint root) - acceptable only when no reference package fits the marker/region, and unweighted UniFrac on it must be treated as suspect.

## Alpha Diversity in R (counts on the rarefied table)

**Goal:** Compute richness and evenness per sample and test for a group difference without confounding by sequencing depth.

**Approach:** Rarefy to a chosen depth, estimate Hill-spanning metrics, test with a non-parametric test (escalate to a linear/mixed model for covariates), and report effective species exp(H').

```r
library(phyloseq); library(vegan)

ps_rare <- rarefy_even_depth(ps, sample.size = chosen_depth, rngseed = 42, replace = FALSE)
alpha <- estimate_richness(ps_rare, measures = c('Observed', 'Shannon', 'InvSimpson'))   # q0, exp gives q1, q2
alpha$Group <- sample_data(ps_rare)$Group
alpha$Shannon_eff <- exp(alpha$Shannon)   # effective species; base-invariant in interpretation (Hill q=1)

kruskal.test(Shannon ~ Group, data = alpha)   # non-parametric; escalate to lme4/nlme for covariates or repeated measures
```

Faith PD in R uses `picante::pd(otu_matrix, tree, include.root = TRUE)`. The Shannon from `estimate_richness` is in natural log (nats); QIIME2 reports log2 (bits) - report `exp(Shannon)` to compare across the two.

## Beta Diversity in R (report weighted AND unweighted)

**Goal:** Quantify between-sample dissimilarity with phylogenetic and abundance-weighted views, then test the group effect while ruling out a dispersion artifact.

**Approach:** Compute both UniFrac variants (and generalized UniFrac alpha=0.5), ordinate by PCoA, run adonis2 for location, and ALWAYS pair it with betadisper for spread.

```r
wu  <- UniFrac(ps_rare, weighted = TRUE)    # abundant-lineage view
uwu <- UniFrac(ps_rare, weighted = FALSE)   # rare-lineage + topology view
# generalized UniFrac alpha=0.5 (Chen 2012 compromise):
gu  <- as.dist(GUniFrac::GUniFrac(t(as(otu_table(ps_rare), 'matrix')), phy_tree(ps_rare), alpha = 0.5)$unifracs[, , 'd_0.5'])

meta <- data.frame(sample_data(ps_rare))
adonis2(wu ~ Group, data = meta, permutations = 999)   # >=999 permutations; significance = LOCATION
permutest(betadisper(wu, meta$Group))                  # MANDATORY: is it dispersion, not location?
```

If betadisper is significant the adonis2 result is ambiguous (location vs spread) - state it. The PERMANOVA-dispersion theory is shared; see metagenomics/metagenome-visualization. For a compositionally coherent ordination with feature loadings use RPCA (DEICODE `qiime deicode rpca` / gemelli). The Python engine is scikit-bio (`skbio.diversity.beta_diversity`, `skbio.stats.ordination.pcoa`, `skbio.stats.distance.permanova`).

## Per-Method Failure Modes

### Sampling-depth sample-massacre
**Trigger:** a `--p-sampling-depth` higher than some samples' totals. **Mechanism:** core-metrics drops every sample below the depth with no warning. **Symptom:** fewer points in the PCoA than samples in the metadata; the lost ones skew low-biomass. **Fix:** pick the depth from the rarefaction plateau, report the dropped-sample list, confirm at a nearby depth.

### De novo tree noise
**Trigger:** UniFrac/Faith PD on a MAFFT+FastTree tree from short reads. **Mechanism:** ~250 bp reads give an unstable topology and arbitrary midpoint root. **Symptom:** unweighted-UniFrac separation that vanishes under SEPP insertion or weighted UniFrac. **Fix:** use SEPP-into-reference or Greengenes2; treat de novo unweighted UniFrac as suspect.

### Unweighted-vs-weighted flip
**Trigger:** reporting only the UniFrac variant that gives p<0.05. **Mechanism:** unweighted listens to rare/short branches, weighted to abundant lineages. **Symptom:** the two disagree and the chosen one is the significant one. **Fix:** report both plus generalized alpha=0.5; state which lineage axis each implicates.

### Rarefy-then-reuse-for-DA
**Trigger:** feeding the rarefied table to a differential-abundance tool. **Mechanism:** rarefaction discards count information the DA model needs. **Symptom:** underpowered or distorted DA. **Fix:** keep raw counts; rarefy only into the diversity branch; route DA to differential-abundance.

### Observed-features-as-species
**Trigger:** comparing raw ASV counts across runs/studies as "richness". **Mechanism:** ASV count tracks DADA2 truncation/maxEE/pooling and intragenomic 16S copy variants, not just biology. **Symptom:** richness shifts with denoising settings. **Fix:** prefer Hill q1/q2; report observed features with the denoising parameters stated.

### Shannon base mismatch
**Trigger:** comparing a QIIME2 Shannon to an R Shannon. **Mechanism:** QIIME2 uses log2 (bits), R `diversity`/`estimate_richness` natural log (nats). **Symptom:** numbers differ by a constant factor and look like a real effect. **Fix:** state the base, convert, or report `exp(H')`.

### PERMANOVA dispersion
**Trigger:** a significant adonis2 read as a composition shift. **Mechanism:** pseudo-F responds to within-group spread, not only centroid location (shared theory; metagenomics/metagenome-visualization). **Symptom:** significant adonis2 with significant betadisper. **Fix:** always run betadisper/permutest alongside; report both.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Sampling depth on the observed-features plateau | Janssen 2018; QIIME2 docs | depth must saturate richness while retaining samples; report dropped list |
| Do NOT use `min(sample_sums)` as the depth | McMurdie 2014 | one tiny library drags every sample to under-saturated noise |
| Generalized UniFrac alpha = 0.5 | Chen 2012 *Bioinformatics* 28:2106 | most powerful for moderately abundant lineages; beats running un/weighted jointly |
| Report Hill q = 0, 1, 2 together | (shared; metagenomics/metagenome-visualization) | spans richness (q0) -> evenness-weighted (q2) |
| PERMANOVA permutations >= 999 | vegan docs | resolution floor for p ~ 0.001; use 9999 for publication |
| Pair adonis2 with betadisper | Anderson & Walsh 2013 (shared) | distinguishes a location shift from a dispersion difference |
| Rarefy for diversity, not for DA | McMurdie 2014; Schloss 2024 | per-analysis decision, not a global switch |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| PCoA has fewer points than samples | `--p-sampling-depth` dropped low-count samples | lower the depth or report the loss; never assume zero drops |
| `UniFrac` errors / Faith PD missing | no `phy_tree` slot in the phyloseq object | attach a SEPP/GG2 (preferred) or de novo tree |
| Unweighted UniFrac significant, weighted not | change is in rare lineages, or de novo tree noise | report both; verify the tree; treat single-metric hit as tentative |
| R and QIIME2 Shannon disagree | log base differs (nats vs bits) | report `exp(H')`; convert by `log2(e)` |
| adonis2 p<0.001 but groups visually overlap | dispersion difference, not location | run betadisper; report it |
| scikit-bio `otu_ids=` deprecation warning | 0.6 renamed OTU to taxon; `otu_ids=` kept as a deprecated alias | `get_beta_diversity_metrics()` and `help()` to find current kwargs |
| Diversity tracks host/plant content | host mitochondria/chloroplast 16S not removed | filter Mitochondria/Chloroplast features (see taxonomy-assignment) before computing diversity |
| "Community" in a near-sterile/low-biomass sample | reagent kitome not removed | sequence controls + run decontam upstream (amplicon-processing; metagenomics/contamination-controls) |

## References

- Faith DP. 1992. Conservation evaluation and phylogenetic diversity. *Biol Conserv* 61:1-10.
- Pielou EC. 1966. The measurement of diversity in different types of biological collections. *J Theor Biol* 13:131-144.
- Lozupone C, Knight R. 2005. UniFrac: a new phylogenetic method for comparing microbial communities. *Appl Environ Microbiol* 71:8228-8235.
- Lozupone CA, Hamady M, Kelley ST, Knight R. 2007. Quantitative and qualitative beta diversity measures lead to different insights into factors that structure microbial communities. *Appl Environ Microbiol* 73:1576-1585.
- Chen J, Bittinger K, Charlson ES, Hoffmann C, Lewis J, Wu GD, Collman RG, Bushman FD, Li H. 2012. Associating microbiome composition with environmental covariates using generalized UniFrac distances. *Bioinformatics* 28:2106-2113.
- Janssen S, McDonald D, Gonzalez A, et al. 2018. Phylogenetic placement of exact amplicon sequences improves associations with clinical information. *mSystems* 3:e00021-18.
- Mirarab S, Nguyen N, Warnow T. 2012. SEPP: SATe-enabled phylogenetic placement. *Pac Symp Biocomput* 2012:247-258.
- McDonald D, Jiang Y, Balaban M, et al. 2024. Greengenes2 unifies microbial data in a single reference tree. *Nat Biotechnol* 42:715-718.
- Martino C, Morton JT, Marotz CA, Thompson LR, Tripathi A, Knight R, Zengler K. 2019. A novel sparse compositional technique reveals microbial perturbations. *mSystems* 4:e00016-19.
- McDonald D, Vazquez-Baeza Y, Koslicki D, et al. 2018. Striped UniFrac: enabling microbiome analysis at unprecedented scale. *Nat Methods* 15:847-848.
- McMurdie PJ, Holmes S. 2014. Waste not, want not: why rarefying microbiome data is inadmissible. *PLoS Comput Biol* 10:e1003531.
- Schloss PD. 2024. Rarefaction is currently the best approach to control for uneven sequencing effort in amplicon sequence analyses. *mSphere* 9:e00354-23.
- McMurdie PJ, Holmes S. 2013. phyloseq: an R package for reproducible interactive analysis and graphics of microbiome census data. *PLoS One* 8:e61217.

## Related Skills

- amplicon-processing - Generate the ASV table and representative sequences upstream
- taxonomy-assignment - Label the ASVs summarized here
- differential-abundance - Per-taxon between-group testing on the unrarefied counts
- qiime2-workflow - The QIIME2 CLI home for core-metrics and tree building
- phylogenetics/tree-io - Read, write, and root the UniFrac/Faith PD tree
- metagenomics/abundance-estimation - Shared CoDA and rarefaction-debate theory
- metagenomics/metagenome-visualization - Shared Hill-number and PERMANOVA-dispersion theory; diversity/ordination on shotgun profiler tables
- data-visualization/ggplot2-fundamentals - Custom ordination and diversity plots
<!-- END FILE: microbiome/diversity-analysis/SKILL.md -->

## 子目录：microbiome/functional-prediction

<!-- BEGIN FILE: microbiome/functional-prediction/SKILL.md -->
---
name: bio-microbiome-functional-prediction
description: Predicts community functional POTENTIAL from 16S/ITS amplicon ASVs with PICRUSt2 (or q2-picrust2) by phylogenetic interpolation of reference-genome gene content - EPA-ng placement, gappa, castor hidden-state prediction of KO/EC/Pfam copy number, 16S copy-number normalization, and MinPath MetaCyc/KEGG pathways - gated by the NSTI quality index. Covers why predicted function is taxonomy re-encoded (never measured gene content and never activity), the mandatory NSTI report (--max_nsti 2 silently drops novel ASVs), why accuracy IS reference coverage (gut Spearman ~0.8, soil/marine collapse), the circularity trap, and Tax4Fun2/FAPROTAX/BugBase alternatives. Use when inferring KO/EC/MetaCyc potential from an ASV table, gating on NSTI, or choosing a prediction method. For MEASURED shotgun function see metagenomics/functional-profiling; for enrichment of KO lists see pathway-analysis/go-enrichment; for DA of predicted tables see differential-abundance.
tool_type: cli
primary_tool: PICRUSt2
---

## Version Compatibility

Reference examples tested with: PICRUSt2 2.5+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The bundled REFERENCE is the version that matters. PICRUSt2 ships its own reference tree, alignment, and per-genome trait tables (16S/KO/EC/Pfam/COG/TIGRFAM) for ~20,000 genomes - there is no separate multi-GB download as in HUMAnN. That fixed reference is the entire ceiling on accuracy, and NSTI is computed against THAT reference. The reference is versioned with the PICRUSt2 release; record the release so a prediction is reproducible.

# Functional Prediction with PICRUSt2

**"Predict the functional pathways from my 16S data"** -> Place ASVs on a reference genome tree and report the gene content of their nearest sequenced relatives - because PICRUSt2 never sees a functional gene from the sample, it infers POTENTIAL from who-is-there.
- CLI: `picrust2_pipeline.py -s asv_seqs.fna -i asv_table.biom -o picrust2_out -p 8 --max_nsti 2`

Scope: PREDICTED gene-content potential from amplicon ASVs. MEASURED shotgun function (HUMAnN) -> metagenomics/functional-profiling. ASV table + rep-seqs come from amplicon-processing + taxonomy-assignment. The QIIME2 q2-picrust2 path -> qiime2-workflow. DA of predicted tables -> differential-abundance (compositional, same theory as metagenomics/abundance-estimation). Reading KO/pathway lists -> pathway-analysis/go-enrichment.

## The Single Most Important Modern Insight -- Predicted Function Is Taxonomy Re-Encoded, Not a Measurement

PICRUSt2 never sequences a functional gene from the sample. It places each ASV on a tree of ~20,000 reference genomes, asks "what genes do this ASV's nearest sequenced relatives carry?", and reports that guess as the community's function. Every output number is the gene content of OTHER organisms, weighted by how much of the 16S resembles them. Three corollaries each common misuse violates:

1. **Potential, never activity.** The honest claim is "increased butyrate-production capacity," never "increased butyrate production / upregulated / more active." The inference chain is 16S abundance -> who-is-there -> relatives' genomes -> predicted gene presence -> predicted copy number -> potential. Transcription and flux are further measurement layers away.
2. **Accuracy IS reference coverage.** Predicted-vs-shotgun Spearman tops out around 0.8 in the densely-referenced human gut (Douglas 2020); in soil, marine, sediment, and novel environments the references are sparse, NSTI rises, and the prediction collapses toward a restatement of taxonomy.
3. **Circularity.** Predicted function is a DETERMINISTIC function of the ASV table - same input, same KO table, every time. So a "functional difference" between groups is the TAXONOMIC difference projected through a fixed lookup, not independent corroboration. Predicted-function analysis is hypothesis-generating; a functional conclusion needs shotgun or metatranscriptomics.

Organize the analysis around defending these three (report NSTI, forbid activity verbs, do not double-count taxonomy as a second finding), not around listing flags.

## The Predicted < Measured Ladder

State this explicitly when reporting. Each rung is a real measurement layer above the one below:

predicted potential (PICRUSt2, this skill) < measured gene carriage (HUMAnN / shotgun, metagenomics/functional-profiling) < measured transcription (metatranscriptomics) < measured flux (fluxomics/metabolomics).

PICRUSt2 is the bottom rung. A PICRUSt2 `path_abun_unstrat` table looks identical to a HUMAnN `pathabundance` table - same MetaCyc IDs, same shape, same MinPath logic - but HUMAnN counts reads that actually aligned to genes in the sample, while PICRUSt2 reports relatives' genomes. Never merge or compare the two as interchangeable.

## How PICRUSt2 Builds the Table (the five-stage interpolation)

Every stage is an inference layered on the previous, so error compounds (Douglas 2020 *Nat Biotechnol* 38:685; original Langille 2013 *Nat Biotechnol* 31:814). PICRUSt2's headline advance over PICRUSt1 is that it places arbitrary de-novo ASVs (not closed-reference Greengenes OTUs):

1. **Placement.** Align ASVs to the reference alignment (hmmalign), place into the reference tree with EPA-ng (Barbera 2019 *Syst Biol* 68:365), resolve placements with gappa (Czech 2020 *Bioinformatics* 36:3263). Default `--placement_tool epa-ng` (alternative `sepp`).
2. **Hidden-state prediction (HSP).** For each placed ASV - whose genome was never sequenced - interpolate the copy number of every gene family from neighboring reference genomes using castor (Louca & Doebeli 2018 *Bioinformatics* 34:1053). Default `--hsp_method mp` (maximum parsimony; `pic` is faster but `mp` is the recommended default).
3. **16S copy-number normalization.** Divide each ASV's abundance by its PREDICTED 16S copy number (a genome with seven 16S copies is over-counted 7x in an amplicon survey). The correction is itself an HSP output, not a measurement.
4. **Metagenome inference.** Per-sample gene abundance = sum over ASVs of (ASV abundance / 16S copies) x (predicted gene copy number). Emits KO/EC/Pfam tables.
5. **Pathway inference.** Map genes to MetaCyc reactions and call pathways with MinPath (Ye & Doak 2009 *PLoS Comput Biol* 5:e1000465). Pathway COVERAGE (`--coverage`, presence confidence) and pathway ABUNDANCE are different questions - do not conflate.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| PICRUSt2 | Douglas 2020 *Nat Biotechnol* 38:685 | EPA-ng placement + castor HSP into ~20k-genome tree -> KO/EC/Pfam, MetaCyc | de-novo ASVs, broad function; strongest in human gut; the default |
| Tax4Fun2 | Wemheuer 2020 *Environ Microbiome* 15:11 | nearest-BLAST to reference 16S + habitat-specific reference + functional-redundancy index | habitat-specific reference available; want a functional-redundancy metric |
| FAPROTAX | Louca 2016 *Science* 353:1272 | curated literature lookup: taxon -> biogeochemical group (nitrification, methanogenesis, sulfate reduction) | ENVIRONMENTAL/biogeochemistry, cultured-taxon-dominated marine/soil; NOT gene-content prediction |
| BugBase | Ward 2017 *bioRxiv* 133462 | organism-level PHENOTYPE prediction (PICRUSt-style gene content) | coarse community phenotypes (aerobic/anaerobic, Gram, oxidative stress); PREPRINT-only, never journal-published |
| PanFP | Jun 2015 *BMC Res Notes* 8:479 | per-lineage pangenome profile weighted by OTU abundance | lineage-level functional summary; no de-novo placement |
| Piphillin | Iwai 2016 *PLoS ONE* 11:e0166104 | direct nearest-neighbor BLAST of ASVs to genome DB (no tree, no HSP) | avoids the phylogenetic-interpolation assumption |

FAPROTAX is conceptually different: a curated taxon-to-function lookup answering "is this community nitrifying?", saying nothing about uncharacterized taxa (they map to nothing). Use FAPROTAX for biogeochemical-cycle questions, PICRUSt2 for a predicted KO/pathway profile - different questions.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Human gut / well-referenced host, broad KO/pathway profile | PICRUSt2 + report NSTI | dense references -> low NSTI -> Spearman ~0.8 vs shotgun; credible broad strokes |
| Soil / marine / sediment / novel environment, biogeochemical question | FAPROTAX (broad groups) | reference tree is gut/host-biased; high NSTI makes PICRUSt2 KOs mostly extrapolation |
| Need REAL (measured) functional gene content | -> metagenomics/functional-profiling | only shotgun reads measure genes; PICRUSt2 predicts, HUMAnN measures |
| Coarse community phenotype (aerobe/anaerobe, Gram, pathogenic potential) | BugBase (flag: preprint-only) | organism-level phenotype, not pathways; cite its unpublished status |
| Already in QIIME2 with .qza artifacts | -> qiime2-workflow (q2-picrust2 plugin) | same engine; FeatureTable in, FeatureTable out, into qiime diversity/composition |
| DA between groups on predicted table | -> differential-abundance, run >=2 CoDA tools | compositional + prediction error; frame as hypothesis-generating (circularity) |
| Reading the resulting KO/pathway list for biology | -> pathway-analysis/go-enrichment | predicted abundance is summed gene content, not an over-representation test |

## Run the Pipeline

```bash
# Full pipeline: place -> HSP -> 16S-normalize -> metagenome -> MetaCyc pathways
picrust2_pipeline.py \
    -s asv_seqs.fna \              # representative ASV sequences (FASTA)
    -i asv_table.biom \            # ASV abundance table (BIOM or TSV; samples as columns)
    -o picrust2_out \
    -p 8 \
    --hsp_method mp \              # maximum parsimony (recommended default); pic is faster but not recommended
    --max_nsti 2 \                 # ASVs ABOVE 2 are DROPPED before inference; report how many (see below)
    --verbose
# Key outputs (gzipped):
#   KO_metagenome_out/pred_metagenome_unstrat.tsv.gz   KEGG ortholog abundances
#   EC_metagenome_out/pred_metagenome_unstrat.tsv.gz   EC-number abundances
#   pathways_out/path_abun_unstrat.tsv.gz              MetaCyc pathway abundances
#   marker_predicted_and_nsti.tsv.gz                   per-ASV 16S copies + metadata_NSTI (the quality file)
```

`--stratified` additionally emits per-ASV contribution tables (large, much slower); `--per_sequence_contrib` is only meaningful with it. `--coverage` adds pathway coverage (a different question from abundance). The unrolled per-step scripts are `place_seqs.py` -> `hsp.py -i {16S,KO,EC} -m mp [-n]` -> `metagenome_pipeline.py --max_nsti 2` -> `pathway_pipeline.py`; `--max_nsti` filtering and 16S normalization happen in `metagenome_pipeline.py`. `add_descriptions.py -m METACYC` attaches human-readable names.

## Report NSTI (mandatory)

**Goal:** Quantify how much of the prediction is extrapolation and how much of the sampled community the NSTI gate discarded, so the result is interpretable.

**Approach:** Read `marker_predicted_and_nsti.tsv.gz`, summarize the `metadata_NSTI` distribution, and report the number of ASVs AND the fraction of READS dropped at `--max_nsti 2` (a study that loses 40% of reads predicted function for a different community than it sampled).

```python
import pandas as pd

nsti = pd.read_csv('picrust2_out/marker_predicted_and_nsti.tsv.gz', sep='\t')   # cols: sequence, metadata_NSTI
asv_counts = pd.read_csv('asv_table.tsv', sep='\t', index_col=0)                # ASVs x samples
nsti = nsti.set_index('sequence')
reads_per_asv = asv_counts.sum(axis=1)

max_nsti = 2.0   # PICRUSt2 default; ASVs above this are dropped before metagenome inference
dropped = nsti.index[nsti['metadata_NSTI'] > max_nsti]
reads_dropped_frac = reads_per_asv.reindex(dropped).sum() / reads_per_asv.sum()
print(f'mean NSTI {nsti.metadata_NSTI.mean():.3f}  median {nsti.metadata_NSTI.median():.3f}')
print(f'ASVs dropped at NSTI>{max_nsti}: {len(dropped)}/{len(nsti)}  reads dropped: {reads_dropped_frac:.1%}')
```

## Per-Method Failure Modes

### Claiming activity or expression
**Trigger:** reporting "increased butyrate production" / "upregulated" / "more metabolically active." **Mechanism:** PICRUSt2 measured no genes and no transcripts - only inferred gene presence from relatives' genomes. **Symptom:** a results sentence with an activity verb on a predicted pathway. **Fix:** restrict every claim to "potential" / "predicted capacity"; for activity, cite metatranscriptomics, not this skill.

### NSTI ignored or under-reported
**Trigger:** accepting the default `--max_nsti 2` filter without reporting the distribution or the dropped fraction. **Mechanism:** the filter silently deletes the most novel/under-referenced ASVs - exactly the organisms an environmental study cares about. **Symptom:** a predicted-function result with no NSTI numbers in the methods. **Fix:** report mean/median NSTI, the distribution, and the ASV AND read fraction dropped (the helper above); treat high mean NSTI as a red flag that the result is mostly extrapolation.

### Wrong environment (reference coverage too sparse)
**Trigger:** running PICRUSt2 on soil/marine/sediment/plant/novel hosts and reporting fine-grained KO differences. **Mechanism:** the ~20k-genome reference tree is gut/host-biased; sparse references mean high NSTI and predictions interpolated from distant relatives. **Symptom:** high mean NSTI yet confident KO/pathway tables. **Fix:** report the environment and NSTI; prefer FAPROTAX for the broad biogeochemical question, or do real shotgun. "Relatively better than other predictors" (per the paper) is not "trustworthy in absolute terms."

### Predicted treated as measured
**Trigger:** describing `path_abun_unstrat` as "the pathways present in the community" or merging it with a HUMAnN table. **Mechanism:** the two tables share IDs and shape but PICRUSt2 reports relatives' genomes, HUMAnN reports reads that aligned to genes in the sample. **Symptom:** predicted and measured tables combined or compared as one. **Fix:** label predictions as potential; never merge with shotgun; keep coverage and abundance as separate questions.

### Circularity (taxonomy double-counted as a second finding)
**Trigger:** reporting "groups differed taxonomically AND functionally" as two lines of evidence. **Mechanism:** predicted function is a deterministic function of the ASV table, so the functional difference IS the taxonomic difference re-encoded. **Symptom:** a predicted-function DA result presented as orthogonal corroboration of a taxonomic result. **Fix:** present predicted function as a hypothesis-generating summary of the taxonomic signal; for orthogonal functional evidence use shotgun/metatranscriptomics.

### DA without compositional correction
**Trigger:** uncorrected Wilcoxon/t-test on relative abundances of the predicted table. **Mechanism:** the table is compositional, depth-confounded, and zero-inflated, on top of prediction error. **Symptom:** a long list of "significant" pathways that do not replicate across methods. **Fix:** use >=2 CoDA tools (ALDEx2, ANCOM-BC2, MaAsLin2, LinDA) and report the intersection (Nearing 2022 *Nat Commun* 13:342); ALDEx2 wants count-like features-as-rows, NOT relab-normalized output - see differential-abundance.

### Strain-level function invisible
**Trigger:** inferring strain-specific function (toxin, resistance, pathogenicity island) from a 16S-based prediction. **Mechanism:** 16S resolves to roughly genus/species; accessory genome, HGT, plasmids, and prophage-borne genes vary within a species and are assigned the reference neighbors' core content. **Symptom:** a strain-level functional claim from amplicon data. **Fix:** state that the species core is the ceiling regardless of NSTI; strain function needs isolate genomes or shotgun.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `--max_nsti` 2.0 (default) | Douglas 2020 *Nat Biotechnol* 38:685 | ASVs whose nearest sequenced genome is >2 substitutions/site away are too extrapolated to trust; dropped before inference - always report the dropped read fraction |
| `--hsp_method mp` (default) | PICRUSt2 manual | maximum parsimony is the recommended HSP method; `pic` is faster but not recommended (the legacy skill wrongly defaulted to `pic`) |
| `--placement_tool epa-ng` (default) | Barbera 2019 *Syst Biol* 68:365 | EPA-ng + gappa is the default placement path; `sepp` is the alternative |
| `--min_align` 0.8 (default) | PICRUSt2 manual | an ASV must align over >=80% of its length to be placed; poorly aligning ASVs are excluded |
| Predicted-vs-shotgun Spearman ~0.79-0.88 (gut) | Douglas 2020 *Nat Biotechnol* 38:685 | the empirical ceiling in the BEST case (dense human-gut references); lower elsewhere - the anchor for every accuracy caveat |
| NSTI ~0.5 / ~0.5-1 / ->2 (heuristic bands) | community practice | rough well-characterized / moderate / weak guide; no NSTI value converts predicted potential into measured function |
| DA: >=2 CoDA tools, report intersection | Nearing 2022 *Nat Commun* 13:342 | tool choice changes the predicted-pathway hit list; consensus beats any single tool |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `metadata_NSTI` / NSTI file not found | reading `marker_nsti_predicted.tsv` (does not exist) | the real file is `marker_predicted_and_nsti.tsv.gz`; the column is `metadata_NSTI` |
| Near-empty output / most ASVs dropped | high NSTI (wrong environment) | check the NSTI distribution; consider FAPROTAX or shotgun; do not just lower `--max_nsti` to keep them |
| ALDEx2 gives implausible results on predicted table | fed relab-normalized output, features-as-columns | pass raw (count-like) predicted abundances with features as rows - see differential-abundance |
| Predicted and shotgun pathway tables disagree | comparing PICRUSt2 to HUMAnN as if interchangeable | they are different objects (predicted vs measured); do not merge |
| `--per_sequence_contrib` produces nothing | used without `--stratified` | it is only meaningful with `--stratified` |
| Pathway "presence" and "abundance" conflated | reading `path_abun` as coverage | abundance and `--coverage` are different questions |

## References

- Douglas GM, Maffei VJ, Zaneveld JR, Yurgel SN, Brown JR, Taylor CM, Huttenhower C, Langille MGI. 2020. PICRUSt2 for prediction of metagenome functions. *Nat Biotechnol* 38:685-688.
- Langille MGI, Zaneveld J, Caporaso JG, et al. 2013. Predictive functional profiling of microbial communities using 16S rRNA marker gene sequences. *Nat Biotechnol* 31:814-821.
- Barbera P, Kozlov AM, Czech L, Morel B, Darriba D, Flouris T, Stamatakis A. 2019. EPA-ng: massively parallel evolutionary placement of genetic sequences. *Syst Biol* 68:365-369.
- Czech L, Barbera P, Stamatakis A. 2020. Genesis and Gappa: processing, analyzing and visualizing phylogenetic (placement) data. *Bioinformatics* 36:3263-3265.
- Louca S, Doebeli M. 2018. Efficient comparative phylogenetics on large trees. *Bioinformatics* 34:1053-1055.
- Ye Y, Doak TG. 2009. A parsimony approach to biological pathway reconstruction/inference for genomes and metagenomes. *PLoS Comput Biol* 5:e1000465.
- Wemheuer F, Taylor JA, Daniel R, Johnston E, Meinicke P, Thomas T, Wemheuer B. 2020. Tax4Fun2: prediction of habitat-specific functional profiles and functional redundancy based on 16S rRNA gene sequences. *Environ Microbiome* 15:11.
- Louca S, Parfrey LW, Doebeli M. 2016. Decoupling function and taxonomy in the global ocean microbiome. *Science* 353:1272-1277.
- Ward T, Larson J, Meulemans J, et al. 2017. BugBase predicts organism-level microbiome phenotypes. *bioRxiv* 133462 (preprint; not peer-reviewed).
- Jun SR, Robeson MS, Hauser LJ, Schadt CW, Gorin AA. 2015. PanFP: pangenome-based functional profiles for microbial communities. *BMC Res Notes* 8:479.
- Iwai S, Weinmaier T, Schmidt BL, et al. 2016. Piphillin: improved prediction of metagenomic content by direct inference from human microbiomes. *PLoS ONE* 11:e0166104.
- Nearing JT, Douglas GM, Hayes MG, et al. 2022. Microbiome differential abundance methods produce different results across 38 datasets. *Nat Commun* 13:342.

## Related Skills

- amplicon-processing - Generate the ASV table and representative sequences consumed here
- taxonomy-assignment - Taxonomic labels for the same ASVs (predicted function tracks these)
- differential-abundance - Compositional DA of the predicted KO/pathway table
- qiime2-workflow - The q2-picrust2 plugin path inside QIIME2
- metagenomics/functional-profiling - MEASURED shotgun function (HUMAnN); the predicted-vs-measured wall
- pathway-analysis/go-enrichment - Reading/enriching the predicted KO/MetaCyc lists
- workflows/microbiome-pipeline - End-to-end amplicon pipeline
<!-- END FILE: microbiome/functional-prediction/SKILL.md -->

## 子目录：microbiome/qiime2-workflow

<!-- BEGIN FILE: microbiome/qiime2-workflow/SKILL.md -->
---
name: bio-microbiome-qiime2-workflow
description: Operates the QIIME2 framework as the glue for an amplicon analysis - the .qza/.qzv artifact model, semantic types (FeatureTable[Frequency], SampleData[PairedEndSequencesWithQuality], Phylogeny[Rooted], FeatureData[Taxonomy]), embedded provenance plus provenance replay, import (Casava/manifest/EMP/BIOM), export, the Metadata object, and the q2cli vs Artifact API interfaces. Covers why a .qza is data-plus-executable-history not a file, why export drops provenance, why a .qzv is terminal, why classifier .qza are version-pinned, and the 2026 distribution/rachis rename. Use when importing reads, choosing a manifest/Casava/EMP/BIOM path, reading or replaying provenance, exporting to BIOM/phyloseq, fixing semantic-type or Phred or sklearn-version errors, or orchestrating the pipeline. Denoising -> amplicon-processing; classifier/DB -> taxonomy-assignment; diversity metric/depth -> diversity-analysis; DA tool -> differential-abundance; PICRUSt2 -> functional-prediction; shotgun moshpit -> metagenomics.
tool_type: cli
primary_tool: QIIME2
---

## Version Compatibility

Reference examples tested with: QIIME2 2026.1+ (amplicon distribution; framework now `rachis`), provenance-lib 2024.10+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `qiime --version`, `qiime info`, then `qiime <plugin> <action> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The QIIME2 release tag (calendar-versioned `YYYY.RELEASE`, e.g. `2026.1`) defines the plugin API AND the `.qza` artifact format; an sklearn taxonomy classifier `.qza` trained under one release may need retraining under another (the classifier is pinned to its scikit-learn version). The conda env name encodes the release and distribution (`qiime2-amplicon-2026.1`; renamed toward `rachis-qiime2-<release>` in 2026.4). Names and the install YAML URL are moving targets - verify the current release and distribution names against the live install page before pinning anything.

# QIIME2 Amplicon Workflow

**"Run my amplicon study through QIIME2"** -> Move data through the framework as typed, provenance-carrying artifacts and defer every scientific choice to the owning skill - because a `.qza` is not a file, it is data plus its entire executable history, and that history is the deliverable.
- CLI: `qiime tools import`, `qiime <plugin> <action> --i-* --p-* --m-* --o-*`, `qiime tools peek/export`

Scope: the artifact/provenance/type machinery and the import/export/metadata/interface mechanics - this is the GLUE skill. Denoising params (trunc/trim/maxEE, DADA2 vs Deblur) -> amplicon-processing. Classifier/DB choice + training -> taxonomy-assignment. Diversity metric/sampling-depth/rarefaction + PERMANOVA-vs-dispersion -> diversity-analysis. DA tool choice/consensus -> differential-abundance. PICRUSt2 -> functional-prediction. Shotgun reads (moshpit distribution, Kraken2/MetaPhlAn/HUMAnN) -> metagenomics. This skill shows each scientific action and routes the decision out; it does not re-teach the method.

## The Single Most Important Modern Insight -- A .qza Is Data Plus Its Executable History, Not a File Format

A `.qza` carries the data AND the complete computational graph that produced it. The semantic-type system plus the embedded provenance ARE the reproducibility guarantee - the whole reason to work inside the framework instead of passing loose BIOM/FASTA/Newick files. The cost is exact and unavoidable: there is no `cat`-ing the data. Three corollaries each common misuse violates:

1. **Working THROUGH the framework keeps the chain; exporting breaks it.** `qiime tools export` writes native data and silently drops the QIIME2 wrapper AND the provenance. Export early and go ad-hoc, and the final figure has no history back to the raw reads - the framework overhead was paid and the deliverable thrown away. Export at the LAST step, or use `qiime2R::qza_to_phyloseq` so the chain survives as far as possible.
2. **Semantic types are a type system for biology.** `core-metrics-phylogenetic` refuses a `FeatureData[Taxonomy]` where a `FeatureTable[Frequency]` belongs, BEFORE running. A type error is the guard WORKING - fix the upstream action that made the wrong type, do not launder it by re-importing.
3. **A `.qzv` is terminal and a classifier is version-pinned.** A Visualizer's output can never be another action's input (keep the `.qza` it was made from). An sklearn classifier `.qza` trained under 2024.x raises a version-mismatch under 2026.x - the training version is part of the method.

Organize the analysis around protecting the provenance chain and the type contract, not around listing flags.

## What Is Inside a .qza

A `.qza` (QIIME Zipped Artifact) and `.qzv` (Visualization) are ZIP archives keyed at top level by a UUID. Every artifact carries four things:

1. **UUID** - identifies THIS computation (provenance references inputs/outputs by UUID), not just a file.
2. **Semantic TYPE** - what the data MEANS: `FeatureTable[Frequency]`, `SampleData[PairedEndSequencesWithQuality]`, `Phylogeny[Rooted]`, `FeatureData[Taxonomy]`, `FeatureData[Sequence]`, `DistanceMatrix`, `SampleData[AlphaDiversity]`. Types can carry Properties (`SampleData[AlphaDiversity] % Properties('phylogenetic')`).
3. **FORMAT** - the on-disk layout the bytes live in (e.g. `BIOMV210DirFmt`, a Newick file). Type is the meaning; format is the bytes.
4. **PROVENANCE** - in a `provenance/` subtree: for every upstream action the plugin/action name, every parameter value, input/output UUIDs, plugin + framework versions, execution environment, timestamp, and BibTeX citations. The references form a DAG of the whole analysis.

```bash
qiime tools peek table.qza                    # UUID + Type + Format, without unzipping
qiime tools validate table.qza --level max    # archive integrity + payload conforms to its format
qiime tools extract --input-path table.qza --output-path extracted/   # FULL archive incl provenance (read by hand)
qiime tools export  --input-path table.qza --output-path exported/     # ONLY the native data - DROPS provenance
```

`qiime tools extract` keeps the QIIME2 structure (data + `provenance/`); `qiime tools export` is the one-way door out. A plain `unzip table.qza` works too (it is a standard ZIP).

## Tool / Interface Taxonomy

| Interface / tool | Role | When |
|------------------|------|------|
| q2cli (`qiime ...`) | the command-line interface; `--i-*` inputs, `--p-*` params, `--m-*` metadata, `--o-*`/`--output-dir` outputs | default, most-documented, scriptable; what tutorials/forum answers use |
| Artifact API (`from qiime2 import Artifact, Metadata`) | the Python 3 interface; `Artifact.load`/`.save`/`.view`, actions importable as functions returning `Results` | notebooks, embedding QIIME2 in a larger Python pipeline (no temp files) |
| view.qiime2.org | renders any `.qzv` viz AND the `.qza`/`.qzv` provenance DAG client-side, NO install | sharing results and inspecting provenance without QIIME2 installed |
| provenance-lib (`qiime tools replay-provenance`) | parses an artifact's provenance DAG and regenerates executable code (Keefe 2023) | recovering the commands that made an artifact; reproducing a shared `.qza` |

Neither q2cli nor the Artifact API is "more reproducible" - provenance is identical; pick by host environment. An Action is a Method (Artifacts in -> Artifacts out), a Visualizer (-> exactly one terminal `.qzv`), or a Pipeline (-> many Artifacts and/or Visualizations, e.g. `core-metrics-phylogenetic`). The Method/Visualizer distinction is WHY a `.qzv` is a dead end. The legacy `q2studio` desktop GUI is dead (last release 2022.8); the no-CLI answers are Galaxy + view.qiime2.org.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Demultiplexed per-sample FASTQ, filenames are Casava 1.8 | `--type SampleData[PairedEndSequencesWithQuality] --input-format CasavaOneEightSingleLanePerSampleDirFmt` | sample IDs parsed from filenames; no manifest needed |
| Demultiplexed FASTQ, arbitrary paths | V2 manifest (`PairedEndFastqManifestPhred33V2`) | TSV of absolute paths; the most general/explicit on-ramp |
| Still multiplexed (one big FASTQ + barcodes) | import `EMPPairedEndSequences`, then `qiime demux emp-paired` | demultiplexing is a QIIME2 step, not the import |
| A feature table built elsewhere | `--input-format BIOMV210Format --type FeatureTable[Frequency]` | BIOM v2.1 (HDF5); attach metadata separately |
| Scripting a notebook / larger Python pipeline | Artifact API | returns Artifacts directly, no temp files; same provenance |
| Need to share a result with no-QIIME2 collaborators | upload `.qzv` to view.qiime2.org | renders viz + provenance client-side |
| Handed a single `.qza`, need the commands that made it | `qiime tools replay-provenance` | regenerates executable code from the provenance DAG |
| One-off custom R analysis, fighting the framework | `qiime2R::qza_to_phyloseq` / export, own the provenance loss | the overhead is not worth it; be honest about the exit point |
| Shotgun / WGS reads | -> metagenomics (moshpit distribution) | different distribution and toolchain; cross-link, do not merge |

## Import

**Goal:** Turn raw demultiplexed reads into a typed, provenance-rooted artifact with the correct Phred offset.

**Approach:** Write a V2 manifest (TSV, absolute paths), declare the semantic type and the format whose name encodes the Phred offset, then immediately summarize to confirm the reads decoded sanely.

```bash
# manifest.tsv (TAB-separated, V2; absolute paths):
#   sample-id<TAB>forward-absolute-filepath<TAB>reverse-absolute-filepath
qiime tools import \
    --type 'SampleData[PairedEndSequencesWithQuality]' \
    --input-path manifest.tsv \
    --input-format PairedEndFastqManifestPhred33V2 \
    --output-path demux.qza
# Phred offset is BAKED INTO the format name: Phred33V2 (modern Illumina) vs Phred64V2 (legacy).
# V1 was CSV with a `direction` column; V2 is TSV with separate forward/reverse columns - prefer V2.

qiime demux summarize --i-data demux.qza --o-visualization demux.qzv   # per-base quality (drives trunc choices)
```

For EMP-multiplexed data: import `--type 'EMPPairedEndSequences'`, then `qiime demux emp-paired --i-seqs emp.qza --m-barcodes-file metadata.tsv --m-barcodes-column barcode-sequence --o-per-sample-sequences demux.qza --o-error-correction-details ec.qza`. The per-base quality plot in `demux.qzv` is read by amplicon-processing to pick truncation - not here.

## The Orchestration Skeleton (each science step DEFERS)

The pipeline shape, with every method choice routed to its owning skill:

```bash
# Denoise -> ASV table + rep-seqs.  PARAM CHOICE (trunc/trim/maxEE, DADA2 vs Deblur) -> amplicon-processing
qiime dada2 denoise-paired --i-demultiplexed-seqs demux.qza \
    --p-trunc-len-f 0 --p-trunc-len-r 0 \
    --o-table table.qza --o-representative-sequences rep-seqs.qza --o-denoising-stats stats.qza

qiime tools peek table.qza    # confirm Type is FeatureTable[Frequency] before wiring downstream

# Taxonomy.  CLASSIFIER + DB choice and training -> taxonomy-assignment
# Use a classifier .qza trained for THIS release (data.qiime2.org/<release>/common/...); old ones break.
qiime feature-classifier classify-sklearn \
    --i-classifier classifier.qza --i-reads rep-seqs.qza --o-classification taxonomy.qza

# Phylogeny (Pipeline) -> rooted tree for UniFrac/Faith PD
qiime phylogeny align-to-tree-mafft-fasttree --i-sequences rep-seqs.qza \
    --o-alignment aln.qza --o-masked-alignment masked-aln.qza \
    --o-tree unrooted-tree.qza --o-rooted-tree rooted-tree.qza

# Diversity (Pipeline).  SAMPLING DEPTH + metric + rarefy-or-not -> diversity-analysis (pick depth from alpha-rarefaction)
qiime diversity core-metrics-phylogenetic --i-phylogeny rooted-tree.qza --i-table table.qza \
    --p-sampling-depth 10000 --m-metadata-file metadata.tsv --output-dir core-metrics/
# PERMANOVA via diversity beta-group-significance; the location-vs-dispersion (betadisper) confound -> diversity-analysis

# Differential abundance - MODERN q2-composition (NOT add-pseudocount+ancom).  Tool choice/consensus -> differential-abundance
qiime composition ancombc --i-table table.qza --m-metadata-file metadata.tsv \
    --p-formula 'group' --o-differentials ancombc.qza
qiime composition da-barplot --i-data ancombc.qza --o-visualization ancombc-barplot.qzv
```

`core-metrics-phylogenetic` and `align-to-tree-mafft-fasttree` are Pipelines (one call, a directory of artifacts + Emperor `.qzv`s out). `--p-formula` takes column names from the Metadata; annotate integer ID/batch columns `categorical` (below) or they enter the model as continuous covariates.

## Metadata

The Metadata TSV is the spine - the same `--m-metadata-file` drives demux barcodes, group-significance, taxa barplots, ANCOM-BC grouping, and Emperor coloring. First column header is the ID column (`sample-id`, `id`, `#SampleID`, ...). An optional second row `#q2:types` overrides type inference per column (`categorical` / `numeric`):

```
sample-id	subject	group
#q2:types	categorical	categorical
s1	101	treatment
s2	102	control
```

Without the `#q2:types` row, a column of only integers is inferred **numeric** - so a subject/batch/timepoint ID silently becomes a continuous covariate. Annotate ID-like integer columns `categorical`. Validate the sheet with Keemei (Rideout 2016 *GigaScience* 5:27) before running - a malformed metadata file is a top cause of cryptic action failures. `qiime metadata tabulate --m-input-file metadata.tsv --o-visualization metadata.qzv` renders any metadata (including an artifact viewed as metadata, e.g. taxonomy or denoising stats) as a table.

## Provenance Replay

**Goal:** Recover the executable commands that produced an artifact, from the artifact alone.

**Approach:** Parse the embedded provenance DAG and regenerate a q2cli (or Artifact-API) script plus a citations BibTeX.

```bash
qiime tools replay-provenance --in-fp core-metrics/ --out-fp replay.sh --usage-driver cli
qiime tools replay-citations  --in-fp core-metrics/ --out-fp citations.bib
# --usage-driver selects cli vs python3/artifact-api output. Verify flag spelling with
# `qiime tools replay-provenance --help` on the installed build (the interface is still maturing).
```

Replay recovers the commands; it is not a guaranteed bit-identical rerun across very different releases (plugin versions are part of the record). The aggregated DAG citations are how a methods section's references come straight from provenance, also via the `.qzv` Citations tab on view.qiime2.org.

## Export (the one-way door)

**Goal:** Hand the data to R/Python when the analysis is no longer expressible in QIIME2 - while losing as little provenance as possible.

**Approach:** Stay in artifacts as long as the work is QIIME2-expressible; export (or read into phyloseq) only at the last step, and keep the upstream `.qza`s so the chain survives up to the exit.

```bash
qiime tools export --input-path table.qza --output-path exported/      # -> exported/feature-table.biom
biom convert -i exported/feature-table.biom -o feature-table.tsv --to-tsv
# FeatureData[Sequence] -> dna-sequences.fasta; FeatureData[Taxonomy] -> taxonomy.tsv; Phylogeny[Rooted] -> tree.nwk
```

Export DROPS the QIIME2 wrapper and the provenance - the exported TSV has no history back to the reads. For R, prefer `qiime2R::qza_to_phyloseq('table.qza', 'taxonomy.qza', 'rooted-tree.qza', 'metadata.tsv')` (Bisanz), which reads artifacts directly and assembles a phyloseq object without manual export. Record where the chain ends.

## Per-Method Failure Modes

### Export-early-loses-provenance
**Trigger:** `qiime tools export` to TSV at step three, then everything else in a notebook. **Mechanism:** export writes native data only and drops the `provenance/` subtree. **Symptom:** the final figure has no provenance back to the raw reads - the framework overhead bought nothing. **Fix:** export at the LAST step; save upstream `.qza`s; or use `qiime2R::qza_to_phyloseq` so the chain survives to the exit.

### Semantic-type mismatch treated as a bug
**Trigger:** feeding a `Phylogeny[Unrooted]` or a `FeatureData[Taxonomy]` where a `FeatureTable[Frequency]` is required. **Mechanism:** the type system refuses incompatible inputs at the interface boundary before running. **Symptom:** "expected an artifact of type ..." error. **Fix:** this is the guard WORKING; `qiime tools peek` to read the actual Type, then fix the UPSTREAM action that produced the wrong type - do not re-import to coerce it.

### Classifier / artifact version break across releases
**Trigger:** a `silva-138-99-nb-classifier.qza` from 2024.x used under 2026.x. **Mechanism:** the sklearn naive-Bayes classifier is pinned to its scikit-learn version; provenance replay assumes recorded plugin versions. **Symptom:** scikit-learn version-mismatch warning/error, or refusal to load. **Fix:** download/train the classifier for YOUR release (the `data.qiime2.org/<release>/common/...` URLs are release-namespaced); retrain or pin the whole env if reusing an old one.

### Manifest Phred / format error on import
**Trigger:** `Phred64V2` on modern Illumina, V1-vs-V2 manifest confusion, relative paths, or `SampleData[...]` for still-multiplexed EMP data. **Mechanism:** the Phred offset is baked into the format name and is applied without checking. **Symptom:** silently mis-decoded quality scores, or an import that "works" but `demux summarize` shows garbage qualities. **Fix:** modern Illumina = Phred33; V2 TSV manifests with absolute paths; `qiime demux summarize` immediately after import; EMP data needs `EMPPairedEndSequences` + `qiime demux`.

### A .qzv treated as data
**Trigger:** trying to feed a `.qzv` into the next action. **Mechanism:** a Visualizer's output is terminal by the framework's type contract. **Symptom:** the action will not accept it as an input. **Fix:** keep and feed the `.qza` the Visualizer was MADE from; a `.qzv` is for viewing only (browser or view.qiime2.org).

### Metadata numeric cast
**Trigger:** an integer subject/batch/timepoint column with no `#q2:types` row. **Mechanism:** inference casts an all-integer column to numeric. **Symptom:** an ID enters a model as a continuous covariate; nonsensical group results. **Fix:** add a `#q2:types` row annotating ID-like columns `categorical`; validate with Keemei.

### Mixing distributions
**Trigger:** expecting amplicon plugins in `moshpit`, or shotgun assembly in `amplicon`. **Mechanism:** distributions are curated, partially-disjoint plugin sets. **Symptom:** "plugin not found." **Fix:** amplicon/marker-gene -> `amplicon` distribution (renamed `qiime2` in 2026.4); shotgun -> `moshpit` (and -> metagenomics); pin both distribution and release.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `--sampling-depth` (rarefaction depth) | -> diversity-analysis | required by `core-metrics`; pick from `alpha-rarefaction`, not a default - the 10000 in examples is a placeholder |
| `--p-formula` integer columns annotated `categorical` | use.qiime2.org metadata reference | otherwise inferred numeric and used as a continuous covariate |
| Phred offset = 33 (modern Illumina) | Illumina format history | Phred64 only for pre-2011 pipelines; wrong choice silently mis-decodes quality |
| Classifier release-match | Bokulich 2018 *Microbiome* 6:90 | the classifier is pinned to its scikit-learn version; cross-release reuse breaks |
| denoise / taxonomy / DA tuning | -> the owning sibling skill | this skill owns no scientific thresholds by design |

Most scientific magic numbers live in the five sibling skills, not here - this skill owns the machinery.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "The scikit-learn version ... could not be found" / classifier won't load | classifier `.qza` trained under a different release | use the release-namespaced classifier or retrain under the current release |
| "Argument ... is not a subtype of ..." / type error | wrong semantic type wired into an action | `qiime tools peek`; fix the upstream action, do not re-import |
| `demux summarize` shows nonsense quality scores | wrong Phred offset in the import format name | re-import with `...Phred33V2`; modern Illumina is Phred33 |
| Import fails on the manifest | V1/V2 confusion, relative paths, wrong delimiter | V2 TSV, absolute paths, tab-separated header `sample-id` |
| A `.qzv` rejected as an action input | Visualizations are terminal | feed the `.qza` it was made from |
| Action treats an ID column as continuous | no `#q2:types` row | annotate the column `categorical`; validate with Keemei |
| Plugin not found | wrong distribution installed | install the `amplicon` (a.k.a. `qiime2` in 2026.4) distribution |

## References

- Bolyen E, Rideout JR, Dillon MR, Bokulich NA, ..., Caporaso JG. 2019. Reproducible, interactive, scalable and extensible microbiome data science using QIIME 2. *Nat Biotechnol* 37:852-857.
- Keefe CR, Dillon MR, Gehret E, Herman C, Jewell M, Wood CV, Bolyen E, Caporaso JG. 2023. Facilitating bioinformatics reproducibility with QIIME 2 Provenance Replay. *PLoS Comput Biol* 19(11):e1011676.
- Lin H, Peddada SD. 2020. Analysis of compositions of microbiomes with bias correction. *Nat Commun* 11:3514.
- Rideout JR, Chase JH, Bolyen E, Ackermann G, Gonzalez A, Knight R, Caporaso JG. 2016. Keemei: cloud-based validation of tabular bioinformatics file formats in Google Sheets. *GigaScience* 5:27.
- Bokulich NA, Kaehler BD, Rideout JR, Dillon M, Bolyen E, Knight R, Huttley GA, Caporaso JG. 2018. Optimizing taxonomic classification of marker-gene amplicon sequences with QIIME 2's q2-feature-classifier plugin. *Microbiome* 6:90.

## Related Skills

- amplicon-processing - DADA2 denoising parameters this skill defers (trunc/trim/maxEE, DADA2 vs Deblur)
- taxonomy-assignment - Classifier and reference-database choice and training behind classify-sklearn
- diversity-analysis - Sampling depth, diversity metric, rarefaction, and the PERMANOVA-vs-dispersion confound
- differential-abundance - DA tool choice and consensus behind composition ancombc
- functional-prediction - PICRUSt2 functional prediction from the feature table
- metagenomics/kraken-classification - Shotgun (moshpit distribution) read classification, not amplicon
- phylogenetics/tree-io - Phylogenetic tree I/O for UniFrac / Faith PD
- read-qc/adapter-trimming - cutadapt primer removal before import/denoising
- workflows/microbiome-pipeline - End-to-end amplicon pipeline
<!-- END FILE: microbiome/qiime2-workflow/SKILL.md -->

## 子目录：microbiome/taxonomy-assignment

<!-- BEGIN FILE: microbiome/taxonomy-assignment/SKILL.md -->
---
name: bio-microbiome-taxonomy-assignment
description: Assigns taxonomy to amplicon ASVs/OTUs (16S, ITS, 18S) with a classifier conditioned on a reference database and primer region - DADA2 assignTaxonomy + addSpecies (RDP naive Bayes), DECIPHER IDTAXA, and QIIME2 q2-feature-classifier (classify-sklearn naive Bayes, classify-consensus-vsearch alignment-consensus). Covers region-specific training (extract-reads, fit-classifier-naive-bayes), why a full-length classifier fabricates calls on a V4 read, the scikit-learn version-pinning trap on pre-trained .qza classifiers, confidence thresholds (classify-sklearn 0.7, assignTaxonomy minBoot 50), and choosing SILVA/GTDB/Greengenes2/UNITE/PR2/RDP. Use when classifying ASVs after DADA2, picking a reference database, training a region-matched classifier, setting a confidence threshold, or deciding whether a 16S species call is defensible (usually not - genus at best). For shotgun read classification see metagenomics/kraken-classification and metagenomics/metaphlan-profiling.
tool_type: mixed
primary_tool: DADA2
---

## Version Compatibility

Reference examples tested with: DADA2 1.30+, DECIPHER 2.30+, QIIME2 2024.10+ (q2-feature-classifier), vsearch 2.22+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The REFERENCE DATABASE and the CLASSIFIER TRAINING REGION are the versions that matter most. Results track the database release and format - SILVA 138.1/138.2, GTDB r220, Greengenes2 2024.09, UNITE (its own release scheme for ITS), PR2 5.x. A DADA2-formatted training FASTA, a DECIPHER trainingSet `.RData`, and a QIIME2 pre-trained classifier `.qza` are NOT interchangeable: each must match the marker and the primer region. A pre-trained naive-Bayes `.qza` is a pickled scikit-learn model tied to the QIIME2 release that built it (see the version-pinning failure mode). Record the database release AND the training region (full-length vs 515-806/V4) for every label.

# Taxonomy Assignment

**"What is this ASV?"** -> Return the most probable lineage in a reference database at a stated confidence - because a label is a classifier + database + primer-region-conditioned hypothesis, not an identification, and a short 16S read licenses genus at best.
- R: `assignTaxonomy(seqs, refFasta, minBoot=50, multithread=TRUE)` then `addSpecies(taxa, speciesFasta)` (exact match only)
- CLI: `qiime feature-classifier classify-sklearn --i-classifier region-matched.qza --i-reads rep-seqs.qza --o-classification taxonomy.qza`

Scope: classification of per-feature amplicon sequences (ASVs/OTUs) from 16S/ITS/18S. ASV inference is upstream -> amplicon-processing. Diversity/DA on the classified table -> diversity-analysis, differential-abundance. Shotgun read classification (raw reads, not ASVs) -> metagenomics/kraken-classification (k-mer LCA), metagenomics/metaphlan-profiling (clade markers). Primer removal before assignment -> read-qc/adapter-trimming.

## The Single Most Important Modern Insight -- A Taxonomic Label Is a Classifier + Database + Region-Conditioned Hypothesis, Not an Identification

A classifier never identifies an organism; it returns the most probable lineage in THIS database, under a model that assumes the true source taxon is represented. The label is a function of three choices made before seeing the answer - the classifier, the reference database (and its naming authority), and the primer region the reference was trimmed to. Change any one and the genus or species call can change. Three corollaries each common misuse violates:

1. **Confidence is certainty WITHIN the database, not proof the answer is in it.** A bootstrap of 95 means the model is sure GIVEN the taxon is in the reference. If the true organism is absent, the classifier confidently returns the nearest WRONG relative. The score cannot detect absence.
2. **Assigning a label and the label being correct are different events.** A ~250 bp single hypervariable region (V4) is identical across many species and often across genera - the discriminating substitutions are elsewhere in the gene. The tool will still EMIT a species name (over-classification); that name is not licensed by the data. Report the rank the data supports - genus at best for many bacteria, family for poorly resolved clades.
3. **The reference must match the primer region.** A full-length-trained classifier applied to a V4 read mismatches k-mer composition and both fabricates and erases calls (Werner 2012; Bokulich 2018). Use a region-matched (515-806) classifier or extract-reads -> fit-classifier-naive-bayes.

ITS (the fungal barcode) is the exception: it resolves to species far more reliably than 16S. 18S (eukaryotes) resolves coarsely, like 16S.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| classify-sklearn (q2-feature-classifier) | Bokulich 2018 *Microbiome* 6:90 | multinomial naive Bayes over 7-mers; pre-trained pickled model | QIIME2 default; train once, classify many; fast |
| classify-consensus-vsearch | Bokulich 2018 *Microbiome* 6:90 | global alignment, consensus over top hits; no trained model | immune to sklearn pinning; transparent hits; slower |
| assignTaxonomy + addSpecies (DADA2) | Wang 2007 *Appl Environ Microbiol* 73:5261 | RDP 8-mer naive Bayes + bootstrap; addSpecies = exact 100% match | R workflow; genus via NB, species via exact match only |
| IDTAXA (DECIPHER) | Murali 2018 *Microbiome* 6:140 | tree-descent with learned per-node confidence; refuses to over-descend | conservative; minimizes over-classification; novelty-aware |
| weighted/clawback classifier | Kaehler 2019 *Nat Commun* 10:4643 | naive Bayes with habitat-specific abundance prior | known habitat (gut, soil); raises species accuracy |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| 16S V4 (515F/806R), standard | SILVA region-matched (515-806) pre-trained NB classifier OR DADA2 assignTaxonomy on SILVA | region-matched, fast, well-benchmarked |
| Have primers but no pre-trained artifact for them | extract-reads -> fit-classifier-naive-bayes (RESCRIPt) | builds the matched reference; full-length underperforms |
| Known habitat, best species accuracy | weighted/clawback classifier | habitat prior cuts species error (Kaehler 2019) |
| scikit-learn version error / no retraining wanted | classify-consensus-vsearch | stores no pickled model; immune to version pinning |
| Conservative, novelty-aware, minimize over-calls | IDTAXA (DECIPHER) | learned per-node refusal to over-descend |
| Unify 16S with shotgun on one tree | Greengenes2 (q2-greengenes2) | single genome-backbone tree, GTDB-harmonized; closed-reference |
| Environmental / under-named bacteria | GTDB SSU reference (via RESCRIPt) | genome-based, rank-normalized, polyphyly-pruned |
| Fungal ITS | UNITE (species hypotheses) + NB or vsearch | formal fungal barcode; species-resolved; never position-trim ITS |
| Protist / eukaryote 18S | PR2 (or SILVA 18S) | curated microeukaryote SSU |
| Species name from one 16S region | DO NOT (or addSpecies exact-match only) | region lacks the information; report genus |
| Raw shotgun reads, not ASVs | -> metagenomics/kraken-classification, metaphlan-profiling | different input artifact and output semantics |

Method choice is contested (see References). Bokulich 2018 found naive Bayes and vsearch-consensus broadly comparable and both top-tier; verify current best practice against the latest q2-feature-classifier docs rather than hard-coding one classifier.

## DADA2 assignTaxonomy + addSpecies

**Goal:** Assign each ASV to the deepest rank the data and reference support, reporting NA below the confidence floor rather than forcing a label.

**Approach:** Run the RDP naive Bayes (8-mer, 100 bootstraps) against a DADA2-formatted reference to a genus-level call, leaving ranks NA below `minBoot`; then attempt species ONLY by exact match against a species reference - never inferring species from the noisy read.

```r
library(dada2)
seqtab_nochim <- readRDS('seqtab_nochim.rds')

# minBoot 50 = the DADA2 default and the RDP recommendation for reads <=250 nt; tutorials
# often use 80 (a stricter CHOICE, not the default). Raising it truncates to shallower but
# more reliable ranks; ranks below the threshold are returned as NA, not guessed.
taxa <- assignTaxonomy(seqtab_nochim, 'silva_nr99_v138.1_train_set.fa.gz', minBoot = 50, tryRC = TRUE, multithread = TRUE)

# addSpecies assigns species by EXACT (100%) match against a species reference. It does NOT
# license a species name from a noisy read - it reports a species only when the ASV is
# identical to a reference over the amplicon, else leaves it NA. This is the honest 16S path.
taxa <- addSpecies(taxa, 'silva_species_assignment_v138.1.fa.gz')
```

The reference FASTA must be DADA2-formatted (rank-labelled headers) AND ideally trimmed to the amplicon region; a full-length SILVA training set on V4 reads is the Trap-1 failure mode below. For ITS, use a UNITE DADA2 reference and do NOT trim ITS to a fixed length (it is variable-length).

## DECIPHER IDTAXA

**Goal:** Get a conservative, novelty-aware classification that refuses to descend into a clade the query likely does not belong to.

**Approach:** Convert ASV sequences to a DNAStringSet, classify with a pre-trained DECIPHER trainingSet, then flatten the per-rank output to a matrix, mapping IDTAXA's "unclassified_" placeholders to NA.

```r
library(DECIPHER)
load('SILVA_SSU_r138_2019.RData')  # provides the trainingSet object
dna <- DNAStringSet(getSequences(seqtab_nochim))

# threshold 60 = DECIPHER default confidence cutoff; raise for stricter calls. IDTAXA's
# tree-descent stops (leaves the rank unclassified) when the query likely belongs to a taxon
# absent from the reference - this is the intended anti-over-classification behaviour.
ids <- IdTaxa(dna, trainingSet, strand = 'both', threshold = 60, processors = NULL)

ranks <- c('domain', 'phylum', 'class', 'order', 'family', 'genus', 'species')
taxa_idtaxa <- t(sapply(ids, function(x) {
    out <- x$taxon[match(ranks, x$rank)]
    out[startsWith(replace(out, is.na(out), ''), 'unclassified_')] <- NA
    out
}))
colnames(taxa_idtaxa) <- ranks
```

## QIIME2 classify-sklearn + Region-Specific Training

**Goal:** Classify ASVs with a naive-Bayes classifier whose reference is trimmed to the EXACT primer region, avoiding the full-length-on-V4 accuracy loss.

**Approach:** In-silico PCR the reference to the primer-bounded region with extract-reads, train a naive-Bayes classifier on the extracted reads, then classify at the default confidence (0.7), which truncates each lineage to the deepest rank clearing the threshold.

```bash
# 1. Extract the V4 (515F/806R) region from a full-length reference (matched k-mer composition)
qiime feature-classifier extract-reads \
    --i-sequences silva-138-99-seqs.qza \
    --p-f-primer GTGYCAGCMGCCGCGGTAA --p-r-primer GGACTACNVGGGTWTCTAAT \
    --p-min-length 50 --p-max-length 0 \
    --o-reads ref-seqs-515-806.qza

# 2. Train the naive-Bayes classifier on the EXTRACTED region (or download the region-matched
#    pre-trained .qza built for THIS QIIME2 release - never a different release, see below)
qiime feature-classifier fit-classifier-naive-bayes \
    --i-reference-reads ref-seqs-515-806.qza \
    --i-reference-taxonomy silva-138-99-tax.qza \
    --o-classifier silva-138-99-515-806-nb-classifier.qza

# 3. Classify. --p-confidence default 0.7: below it the lineage is truncated to a shallower,
#    more confident rank. 0 = compute but never truncate (deepest always); 'disable' = skip.
qiime feature-classifier classify-sklearn \
    --i-classifier silva-138-99-515-806-nb-classifier.qza \
    --i-reads rep-seqs.qza \
    --p-confidence 0.7 --p-read-orientation auto --p-n-jobs 1 \
    --o-classification taxonomy.qza
```

`--p-n-jobs >1` multiplies memory (each job holds a copy of the classifier); a full-length SILVA classifier is multi-GB, so reduce `--p-n-jobs` / `--p-reads-per-batch` if OOM-killed, or use the smaller region-extracted classifier.

## QIIME2 classify-consensus-vsearch (no pickled model)

**Goal:** Classify without a trained, sklearn-pinned model - by aligning each query to the reference and taking a consensus taxonomy across top hits.

**Approach:** VSEARCH global alignment keeps the top `maxaccepts` hits above `perc-identity`; a rank is reported only if at least `min-consensus` of those hits agree on it, else it is dropped.

```bash
qiime feature-classifier classify-consensus-vsearch \
    --i-query rep-seqs.qza \
    --i-reference-reads silva-138-99-seqs.qza \
    --i-reference-taxonomy silva-138-99-tax.qza \
    --p-maxaccepts 10 --p-perc-identity 0.8 --p-min-consensus 0.51 \
    --p-threads 8 \
    --o-classification taxonomy-vsearch.qza --o-search-results vsearch-hits.qza
```

## Filtering Host Organelle and Off-Target Features

**Goal:** Remove host mitochondrial 16S, chloroplast/plastid 16S, and domain-unassigned features BEFORE diversity and differential abundance - universal 16S primers amplify host organelle rRNA, and leaving it in inflates the feature table and deflates every real taxon by compositional closure.

**Approach:** Use the taxonomy just assigned to exclude the Mitochondria and Chloroplast lineages (the labels enable the filter), then carry the filtered table and sequences forward.

```bash
# QIIME2: exclude mitochondria + chloroplast (case-insensitive substring match on the lineage)
qiime taxa filter-table --i-table table.qza --i-taxonomy taxonomy.qza \
    --p-exclude mitochondria,chloroplast \
    --o-filtered-table table-no-organelle.qza
qiime taxa filter-seqs --i-data rep-seqs.qza --i-taxonomy taxonomy.qza \
    --p-exclude mitochondria,chloroplast \
    --o-filtered-data rep-seqs-no-organelle.qza
```

```r
# phyloseq (SILVA ranks: Order 'Chloroplast', Family 'Mitochondria'); the is.na guard keeps unranked taxa
ps <- subset_taxa(ps, is.na(Order)  | Order  != 'Chloroplast')
ps <- subset_taxa(ps, is.na(Family) | Family != 'Mitochondria')
```

Organelle contamination is heaviest in plant, rhizosphere, and host-tissue/biopsy samples (often the majority of reads); inspect per-sample read retention after filtering. Exception: in phototroph-focused, aquatic, or microbial-mat communities, Chloroplast-binned 16S can be the signal of interest (cyanobacterial vs algal-plastid 16S are hard to separate) - inspect what falls in the Chloroplast bin before excluding it. The phyloseq rank-equality form is SILVA-138-specific (Chloroplast at Order, Mitochondria at Family); for GTDB/Greengenes2/RDP verify the rank (`get_taxa_unique(ps, 'Order')`) or use the QIIME2 substring exclude, which is reference-robust.

## Per-Method Failure Modes

### Full-length classifier on a sub-region
**Trigger:** classifying V4 (~250 bp) ASVs with a classifier trained on full-length (~1500 bp) 16S "because it was the one downloaded." **Mechanism:** conserved-region k-mers dominate the model; the discriminating signal is outside the amplified window, so k-mer composition mismatches the query. **Symptom:** systematically shallower or wrong genus/species calls vs a region-matched run. **Fix:** use the 515-806 (or primer-matched) classifier, or extract-reads -> fit-classifier-naive-bayes (Werner 2012; Bokulich 2018).

### Over-reading species from 16S
**Trigger:** reporting a species name (e.g. from naive Bayes descending past the region's resolution) as an identification. **Mechanism:** one hypervariable region is identical across many species/genera; the read lacks the information regardless of classifier quality. **Symptom:** confident species labels that an exact-match (addSpecies) call would leave NA. **Fix:** report genus; use addSpecies (exact match) or IDTAXA's conservative descent for any species claim; treat 16S species as a hypothesis. ITS may legitimately reach species.

### Mixed or mismatched database
**Trigger:** comparing a SILVA genus to a GTDB genus, merging two tables built on different references, or using a database whose scope excludes the marker (GTDB has no Eukarya -> cannot classify 18S/ITS). **Mechanism:** NCBI/SILVA/GTDB assign different names, and GTDB normalizes ranks; labels are not comparable across authorities. **Symptom:** spurious genus mismatches across cohorts; empty/garbled ITS calls against a bacteria-only DB. **Fix:** pick one database matched to the marker (16S->SILVA/GTDB/GG2; ITS->UNITE; 18S->PR2/SILVA), state its release, never merge labels across authorities without a crosswalk.

### scikit-learn version break on a pre-trained classifier
**Trigger:** loading a pre-trained NB `.qza` built for a different QIIME2 release. **Mechanism:** the classifier is a pickled scikit-learn model; QIIME2 records the sklearn version and refuses to run under a different one. **Symptom:** the error "The scikit-learn version (X) used to generate this artifact does not match the current version of scikit-learn installed (Y). Please retrain..." **Fix:** download the classifier built for the exact installed QIIME2 release, OR retrain locally with fit-classifier-naive-bayes, OR use classify-consensus-vsearch (no pickled model). Pinning to a hard-coded classifier URL is exactly this brittleness.

### Confidence default left unexamined
**Trigger:** running classify-sklearn at 0.7 or assignTaxonomy at the default, then reporting whatever rank comes out without stating the threshold. **Mechanism:** the threshold trades sensitivity for specificity - lowering it over-classifies (deeper but wronger), raising it truncates to shallower-but-reliable ranks. **Symptom:** either an over-deep label list or silently dropped/force-filled Unassigned features. **Fix:** state the threshold, tune to region/DB, and keep the truncated ("unassigned at rank X") output honestly - do not drop or force-fill it.

### Host organelle reads not filtered
**Trigger:** running diversity/DA on a host-associated or plant sample without removing Mitochondria/Chloroplast features. **Mechanism:** universal 16S primers amplify host mitochondrial and plastid 16S; classifiers label them `f__Mitochondria`/`o__Chloroplast`, and compositional closure then deflates every real taxon. **Symptom:** a large read fraction labelled Mitochondria/Chloroplast; diversity/DA tracks host content. **Fix:** filter them (the Filtering section above) after assignment, before diversity/DA.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| classify-sklearn `--p-confidence` 0.7 | Bokulich 2018 *Microbiome* 6:90 | benchmarked default for 16S/ITS; below it the lineage is truncated to a more confident rank |
| assignTaxonomy `minBoot` 50 (default); 80 common | Wang 2007 *Appl Environ Microbiol* 73:5261 | RDP recommended 50 for reads <=250 nt, 80 generally; below the floor the rank is NA |
| IDTAXA `threshold` 60 (default) | Murali 2018 *Microbiome* 6:140 | per-node confidence cutoff; raise for stricter, novelty-conservative calls |
| classify-consensus-vsearch `--p-min-consensus` 0.51 | QIIME2 docs | a rank is reported only if a majority of accepted hits agree on it |
| classify-consensus-vsearch `--p-perc-identity` 0.8 | QIIME2 docs | minimum query-reference identity for an accepted hit |
| classify-consensus-vsearch `--p-maxaccepts` 10 | QIIME2 docs | top hits kept per query for the consensus vote |
| addSpecies match 100% (exact) | DADA2 docs | species licensed only by an exact amplicon match; high precision, low recall |
| extract-reads `--p-min-length` 50 | QIIME2 docs | drops too-short in-silico amplicons that would mistrain the classifier |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "scikit-learn version ... does not match" | pre-trained `.qza` built under a different QIIME2/sklearn release | retrain locally, download the release-matched classifier, or use classify-consensus-vsearch |
| Mostly genus/family, few species | correct behaviour for short 16S | report the supported rank; use addSpecies/IDTAXA for species; do not lower confidence to force species |
| OOM kill during classify-sklearn | large classifier x `--p-n-jobs` | lower `--p-n-jobs`/`--p-reads-per-batch`; use a region-extracted (smaller) classifier |
| Empty or garbage ITS taxonomy | bacteria-only DB (GTDB) or position-trimmed ITS | use UNITE; remove ITS primers but never fixed-length-trim ITS |
| All Unassigned at domain level | off-target ASVs (host, chimera, primer artifact) or wrong-orientation reads | filter off-target; leave read-orientation on `auto`; document, do not force-fill |
| Large read fraction labelled Mitochondria/Chloroplast | host organelle 16S amplified by universal primers | `qiime taxa filter-table --p-exclude mitochondria,chloroplast` (or phyloseq subset_taxa) before diversity/DA |
| Genus mismatch across cohorts | labels from different databases (SILVA vs GTDB) | use one database+release for all samples |

## References

- Bokulich NA, Kaehler BD, Rideout JR, Dillon M, Bolyen E, Knight R, Huttley GA, Caporaso JG. 2018. Optimizing taxonomic classification of marker-gene amplicon sequences with QIIME 2's q2-feature-classifier plugin. *Microbiome* 6:90.
- Kaehler BD, Bokulich NA, McDonald D, Knight R, Caporaso JG, Huttley GA. 2019. Species abundance information improves sequence taxonomy classification accuracy. *Nat Commun* 10:4643.
- Werner JJ, Koren O, Hugenholtz P, DeSantis TZ, Walters WA, Caporaso JG, Angenent LT, Knight R, Ley RE. 2012. Impact of training sets on classification of high-throughput bacterial 16S rRNA gene surveys. *ISME J* 6:94-103.
- Wang Q, Garrity GM, Tiedje JM, Cole JR. 2007. Naive Bayesian classifier for rapid assignment of rRNA sequences into the new bacterial taxonomy. *Appl Environ Microbiol* 73:5261-5267.
- Murali A, Bhargava A, Wright ES. 2018. IDTAXA: a novel approach for accurate taxonomic classification of microbiome sequences. *Microbiome* 6:140.
- Quast C, Pruesse E, Yilmaz P, Gerken J, Schweer T, Yarza P, Peplies J, Glockner FO. 2013. The SILVA ribosomal RNA gene database project: improved data processing and web-based tools. *Nucleic Acids Res* 41:D590-D596.
- Parks DH, Chuvochina M, Waite DW, Rinke C, Skarshewski A, Chaumeil PA, Hugenholtz P. 2018. A standardized bacterial taxonomy based on genome phylogeny substantially revises the tree of life. *Nat Biotechnol* 36:996-1004.
- McDonald D, Jiang Y, Balaban M, et al. 2024. Greengenes2 unifies microbial data in a single reference tree. *Nat Biotechnol* 42:715-718.
- Nilsson RH, Larsson KH, Taylor AFS, et al. 2019. The UNITE database for molecular identification of fungi: handling dark taxa and parallel taxonomic classifications. *Nucleic Acids Res* 47:D259-D264.
- Guillou L, Bachar D, Audic S, et al. 2013. The Protist Ribosomal Reference database (PR2): a catalog of unicellular eukaryote Small Sub-Unit rRNA sequences with curated taxonomy. *Nucleic Acids Res* 41:D597-D604.
- Robeson MS 2nd, O'Rourke DR, Kaehler BD, Ziemski M, Dillon MR, Foster JT, Bokulich NA. 2021. RESCRIPt: Reproducible sequence taxonomy reference database management. *PLoS Comput Biol* 17:e1009581.

## Related Skills

- amplicon-processing - Generate the ASV table that is classified here
- diversity-analysis - Alpha/beta diversity of the classified community table
- differential-abundance - Compositional DA on the classified feature table
- qiime2-workflow - The QIIME2 CLI workflow this classification step plugs into
- read-qc/adapter-trimming - cutadapt primer removal before ASV inference and assignment
- metagenomics/kraken-classification - Shotgun (raw-read, not ASV) k-mer classification
- metagenomics/metaphlan-profiling - Shotgun marker-gene profiling; a different input artifact
- phylogenetics/tree-io - Phylogenetic tree for UniFrac / Faith PD on the classified table
- workflows/microbiome-pipeline - End-to-end amplicon pipeline
<!-- END FILE: microbiome/taxonomy-assignment/SKILL.md -->

<!-- END CATEGORY: microbiome -->

