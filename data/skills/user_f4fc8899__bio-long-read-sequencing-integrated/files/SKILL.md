---
slug: bio-long-read-sequencing-integrated
version: 1.0.1
displayName: "长读长测序 / Long-read sequencing analysis"
name: bio-long-read-sequencing-integrated
summary: "中文：长读长测序综合技能，整合 9 个相关专题，覆盖长读长测序分析：Dorado碱基识别、minimap2比对、Clair3变异检测、SV调用、甲基化分析、Iso-Seq。 English: Integrated Long-read sequencing analysis skill covering 9 related topics, including Long-read sequencing analysis: Dorado basecalling, minimap2 alignment, Clair3 variant calling, SV detection, methylation analysis, Iso-Seq."
description: "中文：这是一个面向长读长测序的综合生物信息学 Skill，整合当前分类下 9 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：长读长测序分析：Dorado碱基识别、minimap2比对、Clair3变异检测、SV调用、甲基化分析、Iso-Seq。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Clair3, SQANTI3, dorado。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Long-read sequencing analysis, combining 9 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Long-read sequencing analysis: Dorado basecalling, minimap2 alignment, Clair3 variant calling, SV detection, methylation analysis, Iso-Seq. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Clair3, SQANTI3, dorado. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# long-read-sequencing 分类 Skill 整合版

> 本文件整合同一主分类目录下 9 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: long-read-sequencing -->

## 子目录：long-read-sequencing/basecalling

<!-- BEGIN FILE: long-read-sequencing/basecalling/SKILL.md -->
---
name: bio-long-read-sequencing-basecalling
description: Basecalls raw Oxford Nanopore signal (POD5/FAST5) into reads with Dorado, choosing the chemistry-matched model and accuracy tier (fast/hac/sup), requesting modified bases (5mCG_5hmCG, 6mA, m6A) at basecall time, and handling duplex, demultiplexing, trimming, and HERRO read correction. Covers why the model+version is an irreversible analysis decision, why methylation cannot be recovered later, and why downstream polish/variant models must match the basecaller. Use when converting POD5/FAST5 to reads, picking a Dorado model for R9/R10 or RNA004, enabling methylation calling, basecalling duplex, demultiplexing barcoded runs, or correcting reads for assembly.
tool_type: cli
primary_tool: dorado
---

## Version Compatibility

Reference examples tested with: Dorado 1.0+, pod5 0.3+, samtools 1.19+, chopper 0.7+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Results depend on inputs that outlive the binary version - record them:
- The basecaller MODEL string (e.g. `dna_r10.4.1_e8.2_400bps_sup@v5.2.0`) sets the entire error profile and must be propagated to every downstream tool. Pin it.
- Modified-base models carry a SECOND version (`..._sup@v5.0.0_5mCG_5hmCG@v3`); the mod version can lag the simplex version - check `dorado download --list`.
- R9.4.1 and RNA002 models were removed from Dorado v1.0 defaults; legacy data needs an archived model path.

If code throws an error, introspect the installed tool (`dorado --help`, `dorado basecaller --help`) and adapt the example to the actual API rather than retrying.

# Nanopore Basecalling

**"Basecall my Nanopore data"** -> Convert raw signal (POD5) into reads with Dorado using the chemistry-matched model, deciding the accuracy tier and whether to call modifications now - because the model choice is baked irreversibly into the output.
- CLI: `dorado basecaller sup pod5s/ > calls.bam` (simplex), `dorado basecaller sup,5mCG_5hmCG pod5s/ > calls.bam` (with methylation), `dorado duplex sup pod5s/ > duplex.bam` (duplex)

PacBio note: PacBio "basecalling" (CCS -> HiFi reads) runs on-instrument/in SMRT Link; users receive HiFi BAMs already at Q20-Q30+. This skill is Oxford Nanopore / Dorado. HiFi assembly lives in genome-assembly/hifi-assembly.

## The Single Most Important Modern Insight -- There Is No "The Reads," Only "The Reads As Called By This Model"

Basecalling is not fixed preprocessing that yields a neutral FASTQ. The model and version chosen are an analysis decision written permanently into the BAM, with three consequences a naive user misses:

1. **Methylation is a basecalling decision, not a later analysis step.** Modified bases are inferred from raw signal at basecall time by Remora models and emitted as MM/ML tags. A plain BAM/FASTQ with no MM/ML tags has thrown the signal away - mods CANNOT be recovered without re-basecalling from POD5. If methylation might ever matter, request it now (`sup,5mCG_5hmCG`) and KEEP the POD5. See nanopore-methylation.
2. **Downstream polish/variant models must match the basecaller model+version.** medaka and Clair3 ship per-model weights (Clair3 `r1041_e82_400bps_sup_v500`; medaka the dotted `r1041_e82_400bps_sup_v5.2.0`). A mismatched model silently degrades accuracy with no error. Propagate the basecaller model name to every downstream step.
3. **Mixing model versions across a cohort is a batch effect.** Different model versions have different identity and homopolymer-indel error profiles. Re-basecall the WHOLE cohort with ONE current model before joint or differential analysis.

## Dorado Subcommand Taxonomy

Dorado (one GPU-first executable) replaced Guppy, which is end-of-life. Bonito is ONT's research/training basecaller (not production); Rerio hosts research-release models (niche mods, bacterial methylation).

| Subcommand | Purpose | Canonical invocation |
|------------|---------|----------------------|
| `basecaller` | simplex basecalling | `dorado basecaller hac pod5s/ > calls.bam` |
| `duplex` | template+complement duplex | `dorado duplex sup pod5s/ > duplex.bam` |
| `demux` | barcode classification/split | `dorado demux --kit-name SQK-NBD114-24 --output-dir out/ calls.bam` |
| `trim` | standalone adapter/primer trim | `dorado trim reads.bam > trimmed.bam` |
| `aligner` | minimap2 alignment (carries MM/ML) | `dorado aligner ref.mmi reads.bam > aln.bam` |
| `correct` | HERRO single-read correction | `dorado correct reads.fastq > corrected.fasta` |
| `summary` | sequencing-summary TSV from BAM | `dorado summary calls.bam > summary.tsv` |
| `download` | model management | `dorado download --model <name>` / `--list` |

## Model Naming Scheme (load-bearing)

Format `{analyte}_{pore}_{chemistry}_{speed}@v{ver}` + optional mod suffix, e.g. `dna_r10.4.1_e8.2_400bps_sup@v5.2.0_5mCG_5hmCG@v3`.

| Token | Meaning | Examples |
|-------|---------|----------|
| analyte | molecule | `dna`, `rna004` |
| pore | flow-cell generation | `r10.4.1` (current), `r9.4.1` (legacy) |
| chemistry | kit chemistry | `e8.2` (Kit 14) |
| speed | translocation speed -> sampling rate | `400bps` (5 kHz DNA), `130bps` (RNA004, 4 kHz) |
| tier | model size/accuracy | `fast`, `hac`, `sup` |
| version | model version | `@v4.3.0`, `@v5.2.0`, `@v6.0.0` |

Passing the bare tier (`sup`) lets Dorado auto-detect chemistry from POD5 metadata and fetch the matching latest model; pin a version (`sup@v5.2.0`) or a full path for reproducibility. Append mods comma-separated (`sup,5mCG_5hmCG,6mA`); only one mod model per canonical base may be active.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Any analysis (variant/assembly/methylation) | `sup` + matched model, pinned version | `fast`/`hac` error profile leaks into calls |
| Live run / adaptive sampling / quick QC only | `fast` | speed; never for downstream analysis |
| Routine work, compute-limited | `hac` | strong accuracy/compute balance (v5.2 closed much of the gap to sup) |
| Methylation wanted now or maybe later | `sup,5mCG_5hmCG` (DNA), keep POD5 | mods are unrecoverable from a plain BAM -> nanopore-methylation |
| Per-molecule accuracy, low input, phasing | `dorado duplex sup` | ~Q30 reads, but expect <10% duplex yield |
| Diploid/phased T2T assembly from simplex | `dorado correct` (HERRO) before assembler | haplotype-aware Q22->Q40 -> genome-assembly/long-read-assembly |
| Barcoded multiplexed run | basecall `--no-trim`, then `dorado demux` | trimming first strips barcodes before demux sees them |
| Legacy R9.4.1 / RNA002 data | explicit archived model path | removed from Dorado v1.0 default downloads |
| PacBio data | already HiFi; no Dorado step | CCS runs on-instrument -> genome-assembly/hifi-assembly |

## Core Commands

```bash
# Simplex, super-accuracy, auto-detected chemistry-matched model (BAM is the default output)
dorado basecaller sup pod5s/ > calls.bam

# Pin the model version for reproducibility
dorado basecaller dna_r10.4.1_e8.2_400bps_sup@v5.2.0 pod5s/ > calls.bam

# Call methylation AT basecall time (CpG 5mC + 5hmC); KEEP pod5s/ - mods are unrecoverable later
dorado basecaller sup,5mCG_5hmCG pod5s/ > calls.bam
dorado basecaller sup,6mA pod5s/ > calls.bam               # all-context 6mA
# RNA004 direct RNA (cDNA CANNOT call mods - PCR erases the signal):
dorado basecaller rna004_130bps_sup@v5.1.0,m6A_DRACH pod5s/ > rna_mods.bam

# FASTQ output and a per-read quality floor (relative filter, not a calibrated accuracy)
dorado basecaller sup pod5s/ --emit-fastq --min-qscore 10 > calls.fastq

# Duplex (needs raw POD5; cannot be recovered from simplex FASTQ); dx tag marks read types
dorado duplex sup pod5s/ > duplex.bam

# Demultiplex: basecall WITHOUT trimming, then demux (demux trims barcodes itself)
dorado basecaller sup pod5s/ --no-trim > calls.bam
dorado demux --kit-name SQK-NBD114-24 --output-dir demux/ calls.bam
dorado demux --kit-name SQK-NBD114-24 --barcode-both-ends --output-dir demux/ calls.bam  # stringent

# HERRO read correction for diploid/phased assembly (input FASTQ of HAC/SUP R10 reads >=10kb -> FASTA)
dorado download --model herro-v1
dorado correct reads.fastq > corrected.fasta
```

POD5 is ONT's default raw format (faster random access than FAST5). Convert FAST5 first:

```bash
pod5 convert fast5 raw/*.fast5 --output pod5s/    # FAST5 is legacy; basecalling it directly is slow
pod5 view pod5s/                                   # summary table (replaces deprecated `pod5 inspect reads`)
pod5 merge pod5s/*.pod5 --output merged.pod5
```

## Per-Method Failure Modes

### Methylation gone forever
**Trigger:** basecalling without a mod model, then wanting 5mC later. **Mechanism:** Remora infers mods from raw signal at basecall time; a plain BAM has only bases. **Symptom:** no MM/ML tags; modkit pileup returns nothing. **Fix:** re-basecall from POD5 with `sup,5mCG_5hmCG`; keep POD5 archives.

### Barcodes land in unclassified
**Trigger:** default `--trim all` basecall, then a separate `dorado demux`. **Mechanism:** trimming removes the barcode before demux can read it. **Symptom:** most reads in `unclassified.bam`, low classification rate. **Fix:** basecall `--no-trim`, then demux (it trims barcodes itself).

### Silent accuracy loss downstream
**Trigger:** polishing/calling with a medaka/Clair3 model that doesn't match the basecaller model+version. **Mechanism:** per-model neural weights expect a specific error profile. **Symptom:** no error, just quietly worse consensus/calls. **Fix:** propagate the basecaller model name; use `medaka tools resolve_model --auto_model`; pick the matching Clair3 model dir.

### Duplex double-counting
**Trigger:** treating every read in a duplex BAM as an independent molecule. **Mechanism:** a simplex parent and its duplex offspring both appear. **Symptom:** inflated coverage/allele counts. **Fix:** the `dx:i:-1` tag marks simplex parents of duplex reads - filter them when counting molecules (`dx:i:1` = duplex, `dx:i:0` = simplex-only).

### Cohort batch effect
**Trigger:** runs basecalled with different model versions joined for analysis. **Mechanism:** version-specific identity/indel error profiles confound a technical batch with biology. **Symptom:** spurious between-run differences. **Fix:** re-basecall the whole cohort with one model version.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `sup` for any analysis | ONT model guidance | `fast`/`hac` error profiles contaminate variant/assembly/methylation calls |
| R10.4.1 SUP modal accuracy ~Q20 (99%) | Sereika 2022 | dual-reader head fixes homopolymers; enables nanopore-only near-finished genomes |
| Duplex read ~Q30; yield typically <10% of reads | community benchmarks | duplex is library-prep/loading-limited, not free accuracy |
| A "Q20" base errs at ~Q12.5 empirically | Delahaye 2021 | nanopore qscores >Q10 are overconfident posteriors; use for relative filtering only |
| HERRO input reads >=10 kbp, HAC/SUP R10 | Dorado correct docs | HERRO operates on 4096-bp chunks; shorter reads dropped |
| `--min-qscore 10` as a permissive QC floor | convention | Q10 ~ 90% nominal; a starting filter, not a hard rule |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "Failed to determine sequencing chemistry from data" | R9/RNA002 or non-standard kit; bare tier can't auto-resolve | pass an explicit model path; for legacy chemistry use an archived model |
| No MM/ML tags in BAM | basecalled without a mod model | re-basecall from POD5 with `sup,5mCG_5hmCG` |
| Most reads `unclassified` after demux | trimmed before demux | basecall `--no-trim`, then demux |
| `--model sup` errors | model is the positional arg, not a flag | `dorado basecaller sup pod5s/` |
| `dorado correct reads.bam` fails | input is FASTQ(.gz), output FASTA | `dorado correct reads.fastq > corrected.fasta` |
| Out of GPU memory | batch too large for VRAM (sup is heaviest) | lower `--batchsize`; or drop to `hac` |
| cDNA m6A calling returns nothing | PCR erased native modifications | use direct RNA (RNA004), not cDNA |

## References

- Sereika M, Kirkegaard RH, Karst SM, et al. 2022. Oxford Nanopore R10.4 long-read sequencing enables the generation of near-finished bacterial genomes from pure cultures and metagenomes without short-read or reference polishing. *Nat Methods* 19:823-826.
- Stanojević D, Lin D, Nurk S, Florez de Sessions P, Šikić M. 2026. Telomere-to-telomere assembly using HERRO-corrected Nanopore simplex reads. *Nature* (online ahead of print). DOI 10.1038/s41586-026-10563-y.
- Wick RR, Judd LM, Holt KE. 2019. Performance of neural network basecalling tools for Oxford Nanopore sequencing. *Genome Biol* 20:129.
- Pagès-Gallego M, de Ridder J. 2023. Comprehensive benchmark and architectural analysis of deep learning models for nanopore sequencing basecalling. *Genome Biol* 24:71.
- Delahaye C, Nicolas J. 2021. Sequencing DNA with nanopores: troubles and biases. *PLoS ONE* 16(10):e0257521.
- Gamaarachchi H, Samarakoon H, et al. 2025. The enduring advantages of the SLOW5 file format for raw nanopore sequencing data. *GigaScience* giaf118.

## Related Skills

- long-read-qc - Assess read length/quality and run health after basecalling
- nanopore-methylation - Pile up the MM/ML tags this skill must request at basecall time
- long-read-alignment - Map the reads; use `-y` to carry MM/ML tags through alignment
- medaka-polishing - Consensus model that must match this basecaller model+version
- clair3-variants - Variant model that must match this basecaller model+version
- genome-assembly/long-read-assembly - Assemble the reads (HERRO-corrected for diploid/T2T)
- genome-assembly/hifi-assembly - PacBio HiFi (basecalled on-instrument, not here)
- epitranscriptomics/m6anet-analysis - ONT direct-RNA m6A from signal
- workflows/longread-sv-pipeline - End-to-end basecall -> align -> SV call
<!-- END FILE: long-read-sequencing/basecalling/SKILL.md -->

## 子目录：long-read-sequencing/clair3-variants

<!-- BEGIN FILE: long-read-sequencing/clair3-variants/SKILL.md -->
---
name: bio-long-read-sequencing-clair3-variants
description: Calls germline small variants (SNPs and indels) from Oxford Nanopore and PacBio HiFi long reads with Clair3, a two-stage (pileup + full-alignment) deep-learning caller, selecting the chemistry- and basecaller-version-matched model, enabling read-based phasing, and benchmarking against GIAB with stratification. Covers why the model string is the experiment (no auto-detection, silent degradation on mismatch), why ONT homopolymer/STR indels are the residual error whole-genome F1 hides, and the somatic/trio/RNA boundary to the ClairS/Clair3-Trio family. Use when calling germline SNVs/indels from ONT or HiFi BAMs, choosing a Clair3 model, phasing variants, or benchmarking long-read calls.
tool_type: cli
primary_tool: Clair3
---

## Version Compatibility

Reference examples tested with: Clair3 2.0+, whatshap 2.0+, bcftools 1.19+, hap.py 0.3.15+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Results depend on inputs that outlive the binary version - record them:
- The Clair3 MODEL must match the platform + chemistry + basecaller tier + basecaller version (e.g. `r1041_e82_400bps_sup_v500`). There is NO auto-detection; `--model_path` is mandatory and a mismatch silently degrades calls.
- Clair3 v2 moved TensorFlow -> PyTorch; models are `pileup.pt`/`full_alignment.pt`. v1 TensorFlow models do NOT load in v2.
- The full ONT model set (every version, hac/fast, `_with_mv` signal-aware) lives in the rerio `clair3_models/` repo; only a subset is bundled.

If code throws an error, introspect the installed tool (`run_clair3.sh --help`) and adapt the example to the actual API rather than retrying.

# Clair3 Variant Calling

**"Call variants from my long reads"** -> Run Clair3 with the model that matches how the reads were basecalled, phase, and benchmark with stratification - because the model string, not the command, determines accuracy.
- CLI: `run_clair3.sh --bam_fn=aln.bam --ref_fn=ref.fa --output=out/ --threads=16 --platform=ont --model_path=/models/r1041_e82_400bps_sup_v500`

Scope: germline diploid SNPs + small indels. NOT structural variants (-> structural-variants), NOT somatic/mosaic (-> ClairS/ClairS-TO), NOT RNA (-> Clair3-RNA).

## The Single Most Important Modern Insight -- The Model String Is the Experiment, and ONT Indels Hide in the Strata

Clair3's accuracy is gated by two facts a naive user misses:

1. **The model is hand-picked and a mismatch fails silently.** There is no auto-detection - the user must point `--model_path` at a specific model folder. Three axes must ALL match: chemistry (`r941` vs `r1041`), basecaller tier (`fast`/`hac`/`sup`), and basecaller version (`g5014`/`v430`/`v500`/`v520`), plus the optional `_with_mv` signal-aware axis if the BAM has Dorado `mv` tags. Wrong model = no crash, no warning, measurably worse calls (indels most). Derive the model from the basecaller string in the run metadata; pick the model version closest to but not above the basecaller version.
2. **ONT indels in homopolymers/STRs are the residual error whole-genome F1 conceals.** Even on R10.4.1 sup, insertions/deletions in homopolymer runs and short tandem repeats are the weak point (G/C homopolymers worst), because the pore cannot reliably count identical consecutive bases. A genome-wide indel F1 of ~99.5% hides much lower performance inside LowComplexity/homopolymer strata - exactly the medically relevant loci. HiFi largely solves this; do not transfer ONT-indel pessimism to HiFi. Always benchmark with GIAB stratification, never a single global number.

## Two-Stage Architecture

Clair3 "symphonizes" two networks: a fast **pileup model** (summarized per-position statistics) that calls the large majority of sites, and a slow **full-alignment model** (haplotype-resolved read tensor) that re-evaluates only the uncertain subset. Internally Clair3 phases the top het-SNP pileup calls with WhatsHap, haplotags the BAM, and feeds the haplotagged reads to the full-alignment model - which is why read-based phasing buys ~6% indel F1, not cosmetics. Output: `merge_output.vcf.gz` (final).

## Model Selection

Model name anatomy (`r1041_e82_400bps_sup_v500`): pore (`r1041`=R10.4.1), flowcell (`e82`), speed (`400bps`), basecaller tier (`sup`/`hac`/`fast`), basecaller version (`v500`=Dorado 5.0.0, `g5014`=Guppy 5.0.14). The `_with_mv` suffix uses Dorado move-table tags for best accuracy when present.

| Data | `--platform` | Model |
|------|--------------|-------|
| ONT R10.4.1 sup, Dorado v5.x, mv tags present | ont | `r1041_e82_400bps_sup_v520_with_mv` |
| ONT R10.4.1 sup, Dorado v5.0.0 | ont | `r1041_e82_400bps_sup_v500` |
| ONT R10.4.1 hac | ont | `r1041_e82_400bps_hac_v500`/`_v520` |
| ONT R9.4.1 (any tier) | ont | `r941_prom_sup_g5014` |
| PacBio HiFi Revio | hifi | `hifi_revio` |
| PacBio HiFi Sequel II | hifi | `hifi_sequel2` |
| Illumina (supported) | ilmn | `ilmn` |
| PacBio CLR | - | not supported -> PEPPER-Margin-DeepVariant |

## Decision Tree by Scenario

| Scenario | Tool | Why |
|----------|------|-----|
| Germline SNV/indel, single sample | Clair3 | this skill |
| Somatic, paired tumor-normal | ClairS | VAF-aware; Clair3 germline priors cannot find low-VAF somatic |
| Somatic, tumor-only | ClairS-TO | tumor-only ensemble |
| De novo / Mendelian trio | Clair3-Nova / Clair3-Trio | family-aware |
| Long-read RNA variants | Clair3-RNA | RNA model |
| ONT R10.4.1, also considering DeepVariant | either | neck-and-neck on R10 sup; native-ONT DeepVariant (Kolesnikov 2024) superseded PEPPER-Margin |
| Non-human / draft / bacterial reference | Clair3 + `--include_all_ctgs` | default calls only chr1-22,X,Y -> empty output otherwise |
| Cohort joint genotyping | Clair3 gVCF -> GLnexus | `bcftools merge` on gVCFs is NOT joint genotyping |

## Core Commands

```bash
# Germline ONT calling (model MUST match the basecaller)
run_clair3.sh \
  --bam_fn=aln.bam --ref_fn=ref.fa --output=clair3_out/ \
  --threads=16 --platform=ont \
  --model_path=/opt/models/r1041_e82_400bps_sup_v500
# final VCF: clair3_out/merge_output.vcf.gz

# Phase the final output VCF (WhatsHap); --longphase_for_phasing swaps only the INTERNAL
# phaser to LongPhase (faster, SV-aware). For a LongPhase-phased final VCF use
# --use_longphase_for_final_output_phasing instead of --enable_phasing.
run_clair3.sh ... --enable_phasing --longphase_for_phasing
# Phased calls go to clair3_out/phased_merge_output.vcf.gz; merge_output.vcf.gz stays UNPHASED.

# Non-human / draft assembly reference - call ALL contigs
run_clair3.sh ... --include_all_ctgs

# Targeted / amplicon panel
run_clair3.sh ... --bed_fn=panel.bed --gvcf

# Benchmark against GIAB with stratification (the step that reveals ONT indel errors)
hap.py giab_truth.vcf.gz clair3_out/merge_output.vcf.gz \
  -f giab_confident.bed -r ref.fa --engine=vcfeval \
  --stratification giab_stratifications.tsv -o bench/hg002
```

## Per-Method Failure Modes

### Silent model mismatch
**Trigger:** `--model_path` pointing at a model that does not match the basecaller chemistry/tier/version. **Mechanism:** no auto-detection; the wrong network runs. **Symptom:** no error, lower F1 (indels most). **Fix:** derive the model from the basecaller string; verify the folder exists (rerio for the full set); for v2 ensure `.pt` models.

### Clair3 found nothing on a non-human reference
**Trigger:** bacterial genome or draft assembly without chr1-22,X,Y names. **Mechanism:** Clair3 calls only standard human contigs by default. **Symptom:** near-empty VCF. **Fix:** `--include_all_ctgs`.

### Global F1 looks great, clinical genes are wrong
**Trigger:** reporting only whole-genome F1. **Mechanism:** ONT indel errors concentrate in homopolymer/STR/low-complexity strata. **Symptom:** ~99.5% global indel F1 but much lower in LowComplexity. **Fix:** stratify with GIAB BEDs (Dwarshuis 2024); use CMRG for medically relevant genes.

### Treating Clair3 as a somatic caller
**Trigger:** lowering `--snp_min_af`/`--indel_min_af` to catch low-VAF variants. **Mechanism:** germline model expects ~0.5/1.0 allele fractions, is not VAF-aware. **Symptom:** germline-model false positives at low AF, missed true somatic. **Fix:** ClairS (paired) / ClairS-TO (tumor-only).

### v1 model with v2 Clair3
**Trigger:** an old TensorFlow model dir with Clair3 v2. **Mechanism:** v2 needs PyTorch `.pt` models. **Symptom:** model load failure. **Fix:** use `pileup.pt`/`full_alignment.pt` models (Converted Rerio).

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Recommended depth ~20-60x | Clair3 guidance | sensitivity (hets, indels) falls off below ~20x; `--min_coverage` default 2 is a floor, not a recommendation |
| Phasing buys ~6% indel F1 | Zheng 2022 | haplotagged reads disambiguate indel alleles in repeats |
| ONT R10.4.1 sup: SNP F1 ~99.99%, indel F1 ~99.5% | GIAB benchmarks | indel residual lives in homopolymer/STR strata |
| `--var_pct_full` 0.3 (default) | Clair3 README | fraction of low-quality pileup calls re-run by full-alignment; raise for recall, slower |
| Stratify with GIAB / CMRG | Dwarshuis 2024 | global F1 hides the ONT indel problem |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Empty/near-empty VCF on non-human ref | default calls only chr1-22,X,Y | `--include_all_ctgs` |
| Model fails to load | v1 TF model with v2 Clair3 | use `.pt` (PyTorch) models |
| `--model_path .../models/ont` not found | no generic `ont`/`hifi` model | point at a specific model subfolder |
| Worse-than-expected indels | wrong-version or wrong-tier model | match the basecaller model exactly |
| "joint genotyping" gave odd merges | `bcftools merge` on gVCFs is not joint calling | use GLnexus |
| Looking for somatic/low-VAF variants | germline caller | use ClairS / ClairS-TO |

## References

- Zheng Z, Li S, Su J, Leung AWS, Lam TW, Luo R. 2022. Symphonizing pileup and full-alignment for deep learning-based long-read variant calling (Clair3). *Nat Comput Sci* 2:797-803.
- Zheng Z, He M, Yu X, et al. 2026. Accelerated long-read variant calling with Clair3 for whole-genome sequencing. *Bioinformatics* (advance access) btag181.
- Kolesnikov A, Cook D, Nattestad M, et al. 2024. Local read haplotagging enables accurate long-read small variant calling. *Nat Commun* 15:5907.
- Dwarshuis N, Kalra D, McDaniel J, et al. 2024. The GIAB genomic stratifications resource for human reference genomes. *Nat Commun* 15:9029.
- Lin JH, Chen LC, Yu SC, Huang YT. 2022. LongPhase: an ultra-fast chromosome-scale phasing algorithm for small and large variants. *Bioinformatics* 38(7):1816-1822.
- Chen L, Zheng Z, Su J, et al. 2025. ClairS-TO: a deep-learning method for long-read tumor-only somatic small variant calling. *Nat Commun* 16:9630.

## Related Skills

- basecalling - The basecaller model+version the Clair3 model must match
- long-read-alignment - Produces the BAM (keep `--MD`; use minimap2 >=2.28)
- haplotype-phasing - whatshap/longphase phasing and haplotagging Clair3 uses internally
- medaka-polishing - ONT consensus; medaka diploid variant calling is deprecated in favor of Clair3
- structural-variants - SVs are out of Clair3's scope (Sniffles2/cuteSV)
- variant-calling/deepvariant - DeepVariant native ONT/HiFi models (neck-and-neck on R10)
- variant-calling/vcf-statistics - Summarize/filter the VCF Clair3 emits
- clinical-databases/variant-prioritization - Prioritize the called variants
<!-- END FILE: long-read-sequencing/clair3-variants/SKILL.md -->

## 子目录：long-read-sequencing/haplotype-phasing

<!-- BEGIN FILE: long-read-sequencing/haplotype-phasing/SKILL.md -->
---
name: bio-long-read-sequencing-haplotype-phasing
description: Phases small variants, SVs, and methylation from Oxford Nanopore and PacBio long reads (read-backed/physical phasing) with WhatsHap, LongPhase, or HiPhase, and haplotags the BAM (HP/PS tags) for allele-resolved downstream analysis. Covers why phase blocks break at het-sparse gaps (read length x heterozygosity), why phasing the VCF is useless until the BAM is haplotagged, the GT-pipe/PS and read HP/PS tag spec, reporting block N50 with switch error, the diploid-assumption/CNV/haploid-region traps, trio phasing as the gold standard, and the boundary to statistical panel phasing. Use when phasing long-read variants, haplotagging reads for allele-specific methylation/expression or phased SVs, choosing WhatsHap vs LongPhase vs HiPhase, trio phasing, or assessing phasing quality.
tool_type: cli
primary_tool: whatshap
---

## Version Compatibility

Reference examples tested with: whatshap 2.3+, longphase 1.7+, samtools 1.19+, tabix/htslib 1.19+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Behavior to record:
- `whatshap phase --reference` enables realignment mode (rescues indel phasing on error-prone long reads); omitting it falls back to lower-quality genotype-only phasing.
- Phasing the VCF and haplotagging the BAM are SEPARATE steps; downstream read-level tools need the BAM HP tag.
- `--max-coverage 15` (WhatsHap) is a runtime downsampling cap, not a minimum-depth requirement.

If code throws an error, introspect the installed tool (`whatshap phase --help`, `longphase --help`) and adapt the example to the actual API rather than retrying.

# Read-Backed Haplotype Phasing

**"Phase my long-read variants"** -> Reconstruct haplotypes directly from reads that span heterozygous sites, then haplotag the BAM so downstream tools can see the phase.
- CLI: `whatshap phase -o phased.vcf.gz --reference ref.fa --indels variants.vcf.gz aln.bam` then `whatshap haplotag -o haplotagged.bam --reference ref.fa phased.vcf.gz aln.bam`

This is read-backed (physical, panel-free) phasing of a single sample. Statistical/reference-panel phasing for imputation lives in phasing-imputation/haplotype-phasing; building phased haplotype contigs lives in genome-assembly/hifi-assembly.

## The Single Most Important Modern Insight -- Phasing the VCF Is Useless Until the BAM Is Haplotagged, and Blocks Break Where No Read Spans Two Hets

Read-backed phasing is sample-intrinsic and panel-free (the haplotypes are exactly what this individual's reads physically witness), with two load-bearing consequences:

1. **`phase` writes the VCF; `haplotag` writes the BAM - they are different products.** `whatshap phase` / `longphase phase` set GT pipe (`0|1`) and a PS phase-set in the VCF; they do NOT touch the BAM. Every read-level downstream tool (modkit `--partition-tag HP` for allele-specific methylation, pb-CpG-tools `--hap-tag HP`, Severus for phased SVs, IGV color-by-HP, `whatshap split`) keys on the per-read `HP` tag that ONLY `haplotag` writes. A user who runs `phase` and stops has a phased VCF and an un-haplotagged BAM, and the downstream step silently produces only an ungrouped partition. Triage: `samtools view haplotagged.bam | grep -m1 'HP:i:'`.
2. **Phase blocks break wherever no single read spans two adjacent hets.** Block length is capped by read length x heterozygosity: a long homozygous run (or a coverage/mapping dropout) ends a block no matter how long the reads are. A genome is phased into MANY blocks, not one haplotype per chromosome, and between-block phase is arbitrary until a long-range method (trio, Hi-C) stitches them. So "the genome is phased" is meaningless without block N50 AND switch error together.

## Tool Decision Tree

Switch-error accuracy is comparable across read-based tools (~0.1-0.4% on long reads); choose on speed, SV/mod co-phasing, platform, and pedigree.

| Scenario | Tool | Why |
|----------|------|-----|
| Careful default; indel phasing | WhatsHap (`--reference --indels`) | realignment mode rescues indels; widest downstream familiarity |
| Parents/pedigree sequenced | WhatsHap `--ped` (PedMEC) | the gold standard - chromosome-scale, lowest switch error |
| Whole-genome ONT speed | LongPhase (`--ont`) | ~10x faster; 30x human in ~1 min |
| Co-phase SVs / methylation into long blocks | LongPhase (`--sv-file`/`--mod-file`) | a phased SV bridges het-sparse gaps; block N50 ~25 Mbp |
| PacBio HiFi, joint small+SV+STR | HiPhase | PacBio-native one-pass phasing |
| Multi-tech (Hi-C / 10x) | HapCUT2 | models Hi-C/linked-read error |
| Inside PEPPER-Margin-DeepVariant | margin | legacy embedded haplotagger |

Clair3 uses WhatsHap (or LongPhase) internally to phase its het SNPs and haplotag the BAM feeding its full-alignment model - this skill owns that phase->haplotag mechanism (see clair3-variants).

## The Tags (the central distinction)

| Layer | Tag | Meaning |
|-------|-----|---------|
| VCF (per variant) | `GT` with `|` vs `/` | `0|1` phased (order = which haplotype carries ALT); `0/1` unphased |
| VCF (per variant) | `FORMAT/PS` (Integer) | phase-set / block id; variants sharing a PS are phased relative to each other (conventionally the first variant's position) |
| BAM (per read) | `HP:i:1` / `HP:i:2` | the haplotype this read was assigned to (written by `haplotag`) |
| BAM (per read) | `PS:i:<int>` | the phase set the read's assignment belongs to (matches the VCF PS) |

Unassigned reads carry NO HP tag (not `HP:i:0`). Do not confuse the VCF `HP` FORMAT tag (GATK style) with the BAM `HP` read tag.

## Phasing Quality - Report Block N50 AND Switch Error

| Metric | Tool | Trap |
|--------|------|------|
| phase-block N50/NG50 | `whatshap stats` | contiguity, not correctness; gameable by over-joining blocks (which raises switch errors) |
| phased fraction | `whatshap stats` | a tool can phase fewer easy sites to look better |
| switch error rate | `whatshap compare` | the primary accuracy number |
| switch vs flip decomposition | `whatshap compare` | a long switch propagates (damaging); a flip/short switch self-corrects (one wrong variant) - quote the decomposition |
| Hamming distance | `whatshap compare` | hypersensitive to switch position (a switch near a block start flips half the block) |

Long blocks with a high switch rate are worse, not better, than honest short blocks. Benchmark against a trio-/strand-seq-phased GIAB truth.

## Core Commands

```bash
# WhatsHap: phase (VCF), then haplotag (BAM). --reference enables realignment for indels.
whatshap phase -o phased.vcf.gz --reference ref.fa --indels variants.vcf.gz aln.bam
tabix -p vcf phased.vcf.gz
whatshap haplotag -o haplotagged.bam --reference ref.fa \
    --output-haplotag-list htlist.tsv.gz phased.vcf.gz aln.bam
samtools index haplotagged.bam

# Quality
whatshap stats --gtf blocks.gtf phased.vcf.gz                       # block N50, count, fraction
whatshap compare --names truth,mine truth.vcf.gz phased.vcf.gz      # switch error, flip decomposition

# Trio (gold standard) - --ped takes a PED file, not mother/father/child args
whatshap phase -o trio.vcf.gz --reference ref.fa --ped family.ped joint.vcf.gz mother.bam father.bam child.bam

# LongPhase: faster whole-genome, co-phase SNP+indel+SV(+5mC) into long blocks
longphase phase -s snps.vcf --indels --sv-file svs.vcf -b aln.bam -r ref.fa -o phased -t 16 --ont
longphase haplotag -s phased.vcf --sv-file phased_SV.vcf -b aln.bam -r ref.fa -o haplotagged -t 16

# Downstream consumer example: allele-specific methylation
modkit pileup haplotagged.bam asm/ --ref ref.fa --cpg --combine-strands --partition-tag HP
```

## Per-Method Failure Modes

### Phased VCF but no HP tags downstream
**Trigger:** running `phase` and pointing a read-level tool at the original BAM. **Mechanism:** `phase` writes the VCF only; the BAM HP tag comes from `haplotag`. **Symptom:** modkit returns only an ungrouped partition; IGV shows one color; Severus reports no phased SVs - all with no error. **Fix:** run `haplotag`; verify `samtools view ... | grep HP:i:`.

### Short blocks blamed on the tool
**Trigger:** a homozygosity-rich or inbred sample phasing into many short blocks. **Mechanism:** no intervening hets to link across a long homozygous run - intrinsic, not tool failure. **Symptom:** low block N50 despite good reads. **Fix:** expect it; use ultra-long reads or co-phase SVs (LongPhase) to bridge sparse-het gaps; only trio/Hi-C makes it chromosome-scale.

### Indels phased poorly
**Trigger:** `whatshap phase` without `--reference`. **Mechanism:** without realignment, allele support for indels in error-prone reads is noisy. **Symptom:** low indel phasing / errors. **Fix:** always pass `--reference ref.fa` (and `--indels`) on long reads.

### Confident phasing of a haploid/CNV region
**Trigger:** phasing chrX/Y/MT in an XY sample, or inside a CNV/segdup. **Mechanism:** the two-haplotype model is false there (hemizygous, >2 or 1 haplotype, or collapsed paralogs). **Symptom:** spurious micro-blocks, HP counts far from 50/50. **Fix:** treat phasing there as unreliable; do not interpret it as biology.

### Quoting N50 alone
**Trigger:** comparing phasers on block N50. **Mechanism:** N50 is inflated by over-joining, which raises switch errors. **Symptom:** "longer blocks" that are actually worse. **Fix:** report block N50 AND switch error together; use the flip decomposition.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Total depth ~15-20x for confident phasing | phasing practice | per-haplotype depth is ~half; below ~10x blocks fragment |
| `--max-coverage 15` is a runtime cap | WhatsHap | wMEC is exponential in per-site coverage; >15x is redundant, not required |
| long-read switch error ~0.1-0.4% | benchmarks vs trio truth | the achievable accuracy band |
| LongPhase SNP+SV block N50 ~25 Mbp | Lin 2022 | co-phasing SVs bridges het-sparse gaps (vs ~10-15 Mbp SNP-only) |
| ASM wants ~20x total | methylation practice | each haplotype must clear the ~10x per-site floor |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `modkit --partition-tag HP` has only an ungrouped partition | BAM never haplotagged | run `whatshap haplotag` / `longphase haplotag` |
| `--trio` flag not recognized | the flag is `--ped` | pass a PED file: `--ped family.ped` |
| Poor indel phasing | `--reference` omitted | add `--reference ref.fa --indels` |
| 0 reads usable in phase | BAM @RG sample != VCF sample | `--ignore-read-groups` (or fix sample names) |
| `longphase --platform ont` errors | platform is a bare flag | use `--ont` or `--pb` |
| Spurious phasing on chrX/CNV | diploid assumption violated | treat as unreliable; exclude haploid/CNV regions |

## References

- Patterson M, Marschall T, Pisanti N, et al. 2015. WhatsHap: weighted haplotype assembly for future-generation sequencing reads. *J Comput Biol* 22(6):498-509.
- Martin M, Patterson M, Garg S, et al. 2016. WhatsHap: fast and accurate read-based phasing. *bioRxiv* 085050.
- Garg S, Martin M, Marschall T. 2016. Read-based phasing of related individuals (PedMEC). *Bioinformatics* 32(12):i234-i242.
- Lin JH, Chen LC, Yu SC, Huang YT. 2022. LongPhase: an ultra-fast chromosome-scale phasing algorithm for small and large variants. *Bioinformatics* 38(7):1816-1822.
- Holt JM, Saunders CT, Rowell WJ, et al. 2024. HiPhase: jointly phasing small, structural, and tandem repeat variants from HiFi sequencing. *Bioinformatics* 40(2):btae042.
- Edge P, Bafna V, Bansal V. 2017. HapCUT2: robust and accurate haplotype assembly for diverse sequencing technologies. *Genome Res* 27(5):801-812.

## Related Skills

- clair3-variants - Produces the het VCF; Clair3 phases+haplotags internally via this mechanism
- long-read-alignment - Produces the BAM (keep `-Y` so supplementaries are taggable)
- nanopore-methylation - Allele-specific methylation via `modkit --partition-tag HP`
- structural-variants - Severus consumes a haplotagged BAM for phased/somatic SVs
- basecalling - LongPhase can co-phase 5mC from a modBAM
- phasing-imputation/haplotype-phasing - Statistical/reference-panel phasing for imputation
- genome-assembly/hifi-assembly - Phased de novo haplotype contigs (trio/Hi-C)
- hi-c-analysis/contact-pairs - Hi-C long-range phasing (orthogonal)
<!-- END FILE: long-read-sequencing/haplotype-phasing/SKILL.md -->

## 子目录：long-read-sequencing/isoseq-analysis

<!-- BEGIN FILE: long-read-sequencing/isoseq-analysis/SKILL.md -->
---
name: bio-long-read-sequencing-isoseq-analysis
description: Discovers, classifies, filters, and quantifies full-length transcript isoforms from PacBio Iso-Seq/Kinnex (HiFi) and Oxford Nanopore (cDNA/direct-RNA) long reads, using the isoseq+pigeon pipeline, SQANTI3, and ONT tools (IsoQuant, FLAIR, Bambu, StringTie2). Covers why a novel isoform is an artifact until proven otherwise (RT template-switching, intra-priming, and 5' degradation manufacture junctions and truncations), the SQANTI3 structural categories and their trust order, the Kinnex skera-split step, orthogonal CAGE/poly-A/short-read-junction validation, and why long-read isoform quantification needs EM. Use when building a full-length isoform catalog, classifying/filtering long-read transcripts, running Iso-Seq or ONT cDNA/dRNA analysis, or judging novel-isoform reliability.
tool_type: mixed
primary_tool: SQANTI3
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: isoseq 4.3+, pigeon 1.2+, SQANTI3 5.2+, pbmm2 1.13+, minimap2 2.28+, IsoQuant 3.4+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python/R: `pip show <pkg>` / `packageVersion('<pkg>')` for SQANTI3/IsoQuant/Bambu

Results depend on inputs that outlive the binary version - record them:
- The reference annotation + genome version drive SQANTI3/pigeon classification; record them.
- Orthogonal support files (CAGE refTSS BED, poly-A motif/atlas, short-read STAR SJ.out) determine which novels survive; record their provenance.
- The Iso-Seq binary was renamed `isoseq3` -> `isoseq` in v4; the classifier `pigeon` is a separate binary.

If code throws an error, introspect the installed tool (`isoseq --help`, `pigeon --help`, `sqanti3_qc.py --help`) and adapt the example to the actual API rather than retrying.

# Full-Length Isoform Analysis

**"Find the isoforms in my long-read RNA data"** -> Build a full-length isoform catalog, then classify and filter it against the reference with orthogonal end/junction support - because discovery without curation is a catalog of artifacts.
- CLI: `isoseq refine ... && isoseq collapse ... && pigeon classify ... && pigeon filter ...` (PacBio), `IsoQuant`/`FLAIR`/`Bambu` (ONT)

## The Single Most Important Modern Insight -- A Novel Isoform Is an Artifact Until Proven Otherwise

RT template-switching, intra-priming on genomic poly-A, and 5' RNA degradation actively MANUFACTURE novel junctions and truncated isoforms. So the classification + filter + orthogonal validation IS the analysis, not a QC postscript. Invert the posture from "I discovered N novel isoforms" to "I curated N novel isoforms that survived artifact filtering." Three consequences:

1. **A high novel-isoform fraction is a RED FLAG, not a success** - it usually means an under-powered filter or degraded RNA, not unusually rich biology.
2. **ISM (incomplete-splice-match) is the RNA-degradation thermometer, not a discovery.** ISMs are 5'-truncated FSMs; a high ISM fraction signals bad RNA integrity. Do not report ISMs as novel isoforms without CAGE 5' support.
3. **The orthogonal validation triad is mandatory:** CAGE peaks for the 5' TSS (catches 5' degradation), poly-A atlas/motif for the 3' TES (catches intra-priming), and short-read STAR junctions for splice sites (catches RT-switch/NNC junk).

## SQANTI3 Structural Categories (trust order)

Reference comparison is junction-chain based. NIC > NNC in trust, always; ISM is a diagnostic, not a discovery.

| Category (field value) | Meaning | Trust |
|------------------------|---------|-------|
| FSM (`full-splice_match`) | every internal junction matches a reference transcript; ends may differ | highest (known); ends still need CAGE/polyA |
| ISM (`incomplete-splice_match`) | junction subset of a reference (fewer 5' exons) | low - the 5'-degradation/RT-dropoff signature; trust only with CAGE |
| NIC (`novel_in_catalog`) | novel combination of KNOWN splice sites | high among novels - RT-switching cannot fake a NIC |
| NNC (`novel_not_in_catalog`) | >=1 genuinely novel splice site | lower - where junction artifacts concentrate; needs canonical/short-read support |
| genic / genic_intron | overlaps introns/exons; within an intron | low - pre-mRNA / gDNA carryover |
| fusion | spans >=2 genes | RT-chimera until proven by short-read split reads |
| intergenic / antisense | no gene overlap / antisense | novel-gene candidate or artifact; needs ORF/CAGE/conservation |

Mono-exon transcripts have no junctions to validate and are the false-discovery sink (intra-priming + gDNA run unchecked) - require ORF + CAGE + polyA + conservation before belief.

## Platform / Tool Decision Tree

| Data / goal | Tool | Why |
|-------------|------|-----|
| PacBio Iso-Seq/Kinnex, turnkey | isoseq + pigeon | native PacBio collapse + SQANTI-style classify/filter, SMRT Link integrated |
| Any long-read transcriptome, full curation | SQANTI3 | structural classification + ~50 QC descriptors + rules/ML filter + rescue; PacBio and ONT |
| ONT bulk discovery + quantification | IsoQuant | intron-graph; lowest novel FP rate among ONT tools |
| ONT, want built-in differential splicing | FLAIR | align -> correct junctions -> collapse -> diffSplice |
| Quantification with a precision knob | Bambu | NDR (novel discovery rate) calibrates precision; R/Bioconductor |
| Genome-guided assembly / hybrid short+long | StringTie2 `-L` (`--mix`) | fast long-read transcript assembly |
| ONT single-cell long-read isoforms | FLAMES | single-cell/spatial full-length isoforms |
| Differential isoform usage (DTU/DTE) | -> alternative-splicing | this skill yields the filtered set + counts and hands off |

## cDNA vs Direct-RNA and Spliced Alignment

PacBio Iso-Seq and ONT cDNA sequence reverse-transcribed cDNA (modifications erased; strand from primers); ONT direct-RNA sequences native RNA (true strand, poly-A length, modifications preserved, lower accuracy). Match the minimap2 preset to the chemistry:

```bash
minimap2 -ax splice ref.fa ont_cdna.fq        # ONT cDNA (orient first with pychopper)
minimap2 -ax splice -uf -k14 ref.fa drna.fq   # ONT direct RNA (stranded -> -uf, small k)
minimap2 -ax splice:hq -uf ref.fa hifi.fa     # PacBio HiFi (or pbmm2 --preset ISOSEQ)
```

`-uf` forces the forward transcript strand - correct for stranded dRNA/Iso-Seq, wrong for unoriented ONT PCR-cDNA (orient with pychopper first).

## PacBio Iso-Seq / Kinnex Pipeline

```bash
# 0. Kinnex (MAS-seq) ONLY: deconcatenate the array into segmented reads FIRST
skera split movie.hifi_reads.bam mas_adapters.fasta movie.segmented.bam   # skip for classic Iso-Seq

# 1. Remove cDNA primers; 2. produce FLNC (full-length non-chimeric)
lima movie.segmented.bam primers.fasta movie.fl.bam --isoseq --peek-guess
isoseq refine movie.fl.5p--3p.bam primers.fasta movie.flnc.bam --require-polya

# 3. cluster (reference-free) or skip and align FLNC directly; 4. map; 5. collapse to isoforms
isoseq cluster2 movie.flnc.bam clustered.bam                              # cluster2 scales to large sets
pbmm2 align --preset ISOSEQ --sort ref.fa clustered.bam mapped.bam
isoseq collapse --do-not-collapse-extra-5exons mapped.bam movie.flnc.bam collapsed.gff
#   collapsed.flnc_count.txt = FLNC molecules per isoform = the real DEPTH metric

# 6. classify + filter with pigeon (needs the collapsed.sorted.gff after prepare, NOT a BAM)
pigeon prepare collapsed.gff            # sorts the transcript GFF
pigeon prepare annotation.gtf ref.fa    # sorts the annotation -> annotation.sorted.gtf, indexes genome
pigeon classify collapsed.sorted.gff annotation.sorted.gtf ref.fa \
    --fl collapsed.flnc_count.txt --cage-peak cage.refTSS.bed --poly-a polyA.motif.list
pigeon filter collapsed_classification.txt --isoforms collapsed.sorted.gff
pigeon report --exclude-singletons collapsed_classification.filtered_lite_classification.txt saturation.txt
```

pigeon is PacBio's productized SQANTI3 (classify/filter, NOT a quantifier). Substitute SQANTI3 itself for the full descriptor set, ML filter, rescue module, and ONT support:

```bash
sqanti3_qc.py collapsed.gff annotation.gtf ref.fa --CAGE_peak cage.bed --polyA_motif_list polyA.txt \
    --short_reads short_reads_fofn.txt    # isoforms positional defaults to GTF/GFF; add --fasta for FASTA input
sqanti3_filter.py rules collapsed_classification.txt   # or: sqanti3_filter.py ml ...
```

## Per-Method Failure Modes

### Counting ISMs as novel isoforms
**Trigger:** reporting incomplete-splice-match transcripts as discoveries. **Mechanism:** 5' RNA degradation truncates FSMs into ISMs. **Symptom:** inflated novel/ISM fraction tracking RNA quality, not biology. **Fix:** treat ISM fraction as an integrity QC; keep ISMs only with CAGE 5' support.

### Intra-priming false 3' ends
**Trigger:** trusting 3' ends without poly-A validation. **Mechanism:** oligo-dT primes on a genomic internal A-stretch. **Symptom:** spurious short/mono-exon transcripts; `perc_A_downstream_TTS` >59%. **Fix:** SQANTI3/pigeon filter on downstream genomic A-content and poly-A motif; `--require-polya` alone does NOT catch this.

### Believing NNC novels without scrutiny
**Trigger:** treating NNC like NIC. **Mechanism:** novel splice sites are where RT template-switching and mapping artifacts land. **Symptom:** novel junctions absent from short-read data. **Fix:** require canonical junctions or short-read SJ coverage; prefer NIC.

### Feeding pigeon a BAM
**Trigger:** `pigeon classify mapped.bam ...`. **Mechanism:** pigeon classifies the collapsed.sorted.gff after `pigeon prepare`, not an alignment. **Symptom:** wrong-input error. **Fix:** `isoseq collapse` -> `pigeon prepare` -> `pigeon classify`.

### Comparing isoform counts across libraries of different depth
**Trigger:** raw isoform counts as abundance. **Mechanism:** discovery is depth-unsaturated; truncated reads are multi-isoform-compatible. **Symptom:** deeper libraries "have more isoforms"; double-counted abundance. **Fix:** rarefaction curve (`--exclude-singletons`); EM quantification (Bambu/IsoQuant/NanoCount), not raw FLNC counts.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `perc_A_downstream_TTS` > 59-60% = intra-priming | SQANTI (Tardaguila 2018) | genomic A-rich window means the poly-A was internal, not the real tail |
| novel junction trusted if canonical OR short-read cov >= 3 | SQANTI3 rules filter | a single criterion for RT-switch/NNC artifacts |
| ML filter needs >= 250 Reference-Match FSM | SQANTI3 | enough true-positive labels to train; else falls back to rules |
| exclude singletons (1-FLNC) for saturation | pigeon report | singletons are the dominant unreliable novel bucket |
| FLNC count = depth metric | isoseq collapse | independently sequenced full-length molecules, before clustering/dedup |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `isoseq3: command not found` | renamed in v4 | use `isoseq` (subcommands unchanged) |
| pigeon classify wrong input | fed a BAM | give the collapsed.sorted.gff after `pigeon prepare` |
| Huge novel-isoform count | filter skipped/underpowered | run pigeon/SQANTI3 filter with CAGE/polyA/short-read support |
| Many mono-exon novels | intra-priming / gDNA carryover | filter on poly-A; require ORF/CAGE for mono-exon |
| Wrong-strand spliced alignment | `-uf` on unoriented cDNA | orient with pychopper, or drop `-uf` for cDNA |
| Isoform counts not comparable across samples | depth-unsaturated discovery | EM quantification + rarefaction curve |

## References

- Tardaguila M, de la Fuente L, Marti C, et al. 2018. SQANTI: extensive characterization of long-read transcript sequences for quality control in full-length transcriptome identification and quantification. *Genome Res* 28(3):396-411.
- Pardo-Palacios FJ, Arzalluz-Luque A, Kondratova L, et al. 2024. SQANTI3: curation of long-read transcriptomes for accurate identification of known and novel isoforms. *Nat Methods* 21(5):793-797.
- Prjibelski AD, Mikheenko A, Joglekar A, et al. 2023. Accurate isoform discovery with IsoQuant using long reads. *Nat Biotechnol* 41(7):915-918.
- Tang AD, Soulette CM, van Baren MJ, et al. 2020. Full-length transcript characterization of SF3B1 mutation in chronic lymphocytic leukemia (FLAIR). *Nat Commun* 11:1438.
- Chen Y, Sim A, Wan YK, et al. 2023. Context-aware transcript quantification from long-read RNA-seq data with Bambu. *Nat Methods* 20(8):1187-1195.
- Al'Khafaji AM, Smith JT, Garimella KV, et al. 2024. High-throughput RNA isoform sequencing using programmed cDNA concatenation (MAS-ISO-seq/Kinnex). *Nat Biotechnol* 42(4):582-586.

## Related Skills

- long-read-alignment - Spliced alignment of cDNA/direct-RNA (splice/splice:hq, `-uf`)
- basecalling - Direct-RNA (RNA004) basecalling; cDNA vs direct-RNA chemistry
- nanopore-methylation - Direct-RNA modifications are separate from isoform structure
- alternative-splicing/long-read-splicing - Long-read splicing analysis (define the boundary)
- alternative-splicing/isoform-switching - Differential isoform usage (DTU) downstream
- alternative-splicing/differential-splicing - Differential splicing downstream
- rna-quantification/tximport-workflow - Transcript-level quantification downstream
- genome-annotation/eukaryotic-gene-prediction - Long-read isoforms as annotation evidence
<!-- END FILE: long-read-sequencing/isoseq-analysis/SKILL.md -->

## 子目录：long-read-sequencing/long-read-alignment

<!-- BEGIN FILE: long-read-sequencing/long-read-alignment/SKILL.md -->
---
name: bio-long-read-sequencing-long-read-alignment
description: Aligns Oxford Nanopore and PacBio long reads (and assemblies) to a reference with minimap2 using the error-rate-matched preset (map-ont, lr:hq, map-hifi, map-pb, splice/splice:hq, asm5/10/20, ava), producing a sorted/indexed BAM for variant, SV, methylation, or isoform analysis. Covers why the preset rewrites the scoring/chaining model, why SV calling rides on supplementary not secondary alignments, carrying MM/ML methylation tags through with -y, the multi-part-index MAPQ trap, and when to swap in Winnowmap/VACmap/lra/pbmm2. Use when mapping ONT or PacBio reads, choosing a minimap2 preset by platform/chemistry, preparing input for Clair3/medaka/Sniffles/modkit, aligning into repeats/centromeres, or spliced-aligning cDNA/Iso-Seq.
tool_type: cli
primary_tool: minimap2
---

## Version Compatibility

Reference examples tested with: minimap2 2.28+, samtools 1.19+, winnowmap 2.03+, pbmm2 1.13+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Version-driven behavior to record:
- `lr:hq` and `map-iclr` were added in minimap2 2.27; `lr:hqae` in 2.28. Use >=2.28.
- `--MD` was broken by the 2.27 `--ds` addition and fixed in 2.28; use >=2.28 for any MD-dependent caller.
- A prebuilt `.mmi` index bakes in k/w/H/I - it must be built with the same preset used for alignment.

If code throws an error, introspect the installed tool (`minimap2 --help`, man page) and adapt the example to the actual API rather than retrying.

# Long-Read Alignment with minimap2

**"Align my long reads to the reference"** -> Map with the preset that matches the reads' ERROR RATE (not just platform), keeping the supplementary alignments and tags that downstream callers need.
- CLI: `minimap2 -ax lr:hq --MD -Y ref.fa reads.fq | samtools sort -o aln.bam` (accurate ONT/R10), `minimap2 -ax map-ont` (noisy R9 ONT), `minimap2 -ax map-hifi` (PacBio HiFi)

## The Single Most Important Modern Insight -- The Preset Rewrites the Scoring Model, So the Wrong One Fabricates or Erases Variants

`-x <preset>` is not a label. The man page defines each preset as a literal bundle that rewrites k-mer/window AND the entire scoring model (match `-A`, mismatch `-B`, gap-open `-O`, gap-extend `-E`), Z-drop `-z`, and chaining bandwidth `-r`. So the wrong preset does not merely "align worse" - it changes which gaps the chainer will span, and thereby fabricates or erases the exact insertions, deletions, introns, and SV breakpoints the downstream caller is built to find. Three corollaries an expert holds:

1. **Preset = read error rate, not platform.** "ONT" is no longer one regime: noisy R9/fast/hac = `map-ont`; accurate Q20+/duplex/R10-sup = `lr:hq` (2.27+, ~4x fewer CPU-hours, equal/better accuracy). `map-hifi` is literally `lr:hq` + HiFi scoring.
2. **Supplementary alignments ARE the SV signal.** SV callers read the split-read pattern (primary + supplementary chimeric pieces), not the tidy primary. Feeding them secondaries, or hard-clipping supplementaries, silently degrades SV sensitivity.
3. **A tag absent at alignment time is unrecoverable.** MM/ML, MD, cs - if minimap2 did not write them, no downstream tool can reconstruct them; the pipeline succeeds and produces empty/wrong results.

## Preset Taxonomy

| Preset | Read type / when correct | Notes |
|--------|--------------------------|-------|
| `map-ont` | ONT noisy genomic (R9, fast/hac) | the historic default; ~10% error scoring |
| `lr:hq` | accurate long reads <1% err (ONT Q20+/duplex/R10 sup) | 2.27+; the modern accurate-ONT default |
| `map-hifi` | PacBio HiFi/CCS genomic | = `lr:hq` + HiFi scoring (2.27+) |
| `map-pb` | PacBio CLR (legacy, ~15% err) | homopolymer-compressed minimizers; NEVER for HiFi |
| `splice` | noisy long RNA (ONT cDNA/direct RNA) | add `-uf` for stranded direct RNA |
| `splice:hq` | accurate long RNA (PacBio Iso-Seq, R10 cDNA) | |
| `asm5` / `asm10` / `asm20` | assembly-to-ref at ~0.1% / ~1% / ~5% divergence | PAF output; `--cs` for paftools call |
| `ava-ont` / `ava-pb` | all-vs-all read overlap (miniasm) | overlaps only, no base alignment |
| `lr:hqae` | accurate reads back to THEIR OWN assembly | 2.28+; fixes centromere self-mapping mismaps |

## Aligner Decision Tree

| Situation | Aligner | Why |
|-----------|---------|-----|
| Standard ONT/HiFi to a normal reference (SNV/SV/general) | minimap2 | the de-facto standard; default for Sniffles2, cuteSV, Clair3 |
| Accurate ONT (Q20+/duplex/R10 sup) | minimap2 `-x lr:hq` | ~4x faster than map-ont, equal/better |
| Centromeres / satellite arrays / segmental dups / T2T reference | Winnowmap2 | minimap2 minimizer-masking mismaps long tandem repeats; Winnowmap down-weights via meryl repetitive k-mers |
| Complex/nested SVs, inversions, tandem dups | VACmap (or lra) | variant-aware nonlinear chaining resolves CSVs minimap2 splits |
| Accurate reads -> a diploid assembly built from them | minimap2 `-x lr:hqae` (2.28+) | avoids self-assembly centromere mismaps |
| PacBio-native (.bam/.xml, want sorted+indexed in one call) | pbmm2 | minimap2 + PacBio plumbing; presets SUBREAD/CCS/HIFI/ISOSEQ |
| Legacy Sniffles1 reproduction | NGMLR | the 2018 standard, now superseded by minimap2+Sniffles2 |

## Tag Requirements by Downstream Tool

A missing tag is a silent failure. Add the tag at alignment time.

| Tag / flag | What it does | Needed for |
|------------|--------------|-----------|
| `--MD` | mismatch positions vs ref | many small-variant callers, IGV mismatch coloring (use minimap2 >=2.28) |
| `-Y` | soft-clip supplementary (default hard-clips) | SV callers: keeps breakpoint/insertion SEQ on the split read |
| `-y` | copy MM/ML (and other) tags from the input | methylation: carries Dorado MM/ML through alignment |
| `--cs` | minimap2 difference string | `paftools.js call` (assembly/long-read variant calling) requires it |
| `--eqx` | `=`/`X` CIGAR instead of `M` | tools that read match/mismatch from CIGAR |
| `-L` | move >65535-op CIGAR to CG:B tag | ultra-long ONT reads (else unrepresentable in BAM) |

Supplementary (flag 0x800) = split piece of one read across loci = the SV substrate, controlled by chaining + `-Y`. Secondary (flag 0x100) = multi-mapping alternative, controlled by `--secondary`/`-N`/`-p`. SV work keeps primary+supplementary and is fine with `--secondary=no`.

## Core Commands

```bash
# Accurate ONT (Q20+/R10 sup) -> genome, SV+variant ready, sorted+indexed
minimap2 -ax lr:hq -t 16 --MD -Y -R '@RG\tID:s1\tSM:s1' ref.fa reads.fq.gz \
  | samtools sort -@4 -o aln.bam && samtools index aln.bam

# Noisy ONT (R9 / fast / hac)
minimap2 -ax map-ont -t 16 --MD -Y ref.fa r9.fq.gz | samtools sort -o ont.bam

# PacBio HiFi (minimap2, or pbmm2 in one sorted+indexed call)
minimap2 -ax map-hifi -t 16 --MD -Y ref.fa hifi.fq.gz | samtools sort -o hifi.bam
pbmm2 align --preset HIFI --sort -j 16 ref.fa hifi.bam hifi.aligned.bam

# Methylation passthrough: carry Dorado MM/ML through alignment (the -y trap). -Y soft-clips
# supplementary records so hard-clipping does not break the MM per-base skip counting.
samtools fastq -T MM,ML dorado.mod.bam \
  | minimap2 -ax lr:hq -y -Y --MD ref.fa - \
  | samtools sort -o meth.bam        # then modkit pileup meth.bam ...

# Direct RNA (ONT): stranded forward-only, small k for terminal-exon sensitivity
minimap2 -ax splice -uf -k14 -G500k ref.fa dRNA.fq.gz | samtools sort -o drna.bam
#   -G500k raises max-intron above the 200k default only for genes with long introns

# Assembly-to-reference: PAF is correct here; --cs enables paftools variant calling
minimap2 -cx asm5 --cs ref.fa asm.fa > asm.paf
paftools.js call asm.paf > asm.var.vcf

# Repeats / centromeres / T2T: Winnowmap (precompute repetitive k-mers)
meryl count k=15 output merylDB ref.fa
meryl print greater-than distinct=0.9998 merylDB > repetitive_k15.txt
winnowmap -W repetitive_k15.txt -ax map-ont ref.fa reads.fq.gz | samtools sort -o wm.bam

# Prebuild index - bake the SAME preset's k/w in (else the preset's k/w is ignored)
minimap2 -x lr:hq -d ref.lrhq.mmi ref.fa
```

## Per-Method Failure Modes

### Hard-clipped supplementaries break SV insertion calls
**Trigger:** mapping for SV calling without `-Y`. **Mechanism:** minimap2 hard-clips supplementary records, discarding the breakpoint-spanning bases. **Symptom:** imprecise/missing insertions and translocations. **Fix:** add `-Y` (soft-clip) so split reads keep full SEQ.

### Methylation tags silently dropped
**Trigger:** aligning a Dorado mod BAM without preserving tags. **Mechanism:** `samtools fastq` strips MM/ML unless `-T MM,ML`; minimap2 ignores them unless `-y`. **Symptom:** aligned BAM has no MM/ML; modkit produces empty bedMethyl, no error. **Fix:** `samtools fastq -T MM,ML | minimap2 -y -Y`, or use `dorado aligner`.

### Multi-part index destroys MAPQ
**Trigger:** reference larger than `-I` (default 8G) - large plant/polyploid or concatenated refs. **Mechanism:** minimap2 builds a multi-part index and scores batches independently, so cross-batch best hits are invisible and MAPQ is wrong. **Symptom:** "no @SQ lines ... use --split-prefix"; spurious MAPQ. **Fix:** `-I <bigger-than-ref>` or `--split-prefix`.

### Wrong preset on accurate reads
**Trigger:** `map-ont` on Q20/R10/duplex, or `map-pb` on HiFi. **Mechanism:** noisy-read scoring on accurate reads (or CLR scoring on HiFi). **Symptom:** ~4x slower for no gain (map-ont case), or spurious clips/indels (map-pb-on-HiFi). **Fix:** `lr:hq` for accurate ONT, `map-hifi` for HiFi.

### Direct-RNA junctions on the wrong strand
**Trigger:** `-ax splice` on direct RNA without `-uf`. **Mechanism:** splice defaults to `-ub` (GT-AG on both strands), but dRNA is stranded. **Symptom:** invented/misplaced introns. **Fix:** add `-uf` (and usually `-k14`).

### Centromere/SD mismapping looks fine in flagstat
**Trigger:** plain minimap2 into long tandem repeats. **Mechanism:** minimizer masking collapses minimizer density, so reads map to the wrong paralog/copy. **Symptom:** reads still "map" (flagstat clean) but produce false SVs/heterozygosity in repeats. **Fix:** Winnowmap2 with a meryl repetitive-k-mer set.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `lr:hq` for reads <1% error | minimap2 2.27 NEWS / Li | accurate-read preset; ~4x fewer CPU-hours than map-ont |
| `-I 8G` default index batch | minimap2 man page | refs above it split into a MAPQ-breaking multi-part index |
| `distinct=0.9998` meryl k-mer cutoff | Winnowmap2 (Jain 2022) | flags the most-frequent k-mers to down-weight in repeats |
| `-G 200k` default max intron (splice) | minimap2 man page | raise only to the real longest intron; excess slows and invents alignments |
| minimap2 >= 2.28 | minimap2 NEWS | `lr:hq`/`lr:hqae` present and the 2.27 `--MD` regression fixed |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| SV insertions imprecise/missing | supplementaries hard-clipped | add `-Y` |
| modkit bedMethyl empty after alignment | MM/ML dropped | `samtools fastq -T MM,ML | minimap2 -y -Y` |
| "no @SQ lines ... use --split-prefix" | ref exceeds `-I`, multi-part index | `-I <bigger>` or `--split-prefix` |
| Preset k/w seems ignored | `.mmi` built with a different preset | rebuild index with the same `-x` preset |
| `paftools.js call` fails on PAF | missing base CIGAR / cs | `minimap2 -cx asm5 --cs` |
| Reads mismap in centromeres/SDs | minimizer masking | Winnowmap2 with meryl repetitive k-mers |
| Spurious wrong-strand introns (direct RNA) | `splice` default `-ub` | add `-uf` |

## References

- Li H. 2018. Minimap2: pairwise alignment for nucleotide sequences. *Bioinformatics* 34(18):3094-3100.
- Li H. 2021. New strategies to improve minimap2 alignment accuracy. *Bioinformatics* 37(23):4572-4574.
- Jain C, Rhie A, Hansen NF, et al. 2022. Long-read mapping to repetitive reference sequences using Winnowmap2. *Nat Methods* 19:705-710.
- Ren J, Chaisson MJP. 2021. lra: a long read aligner for sequences and contigs. *PLoS Comput Biol* 17(6):e1009078.
- Ding H, et al. 2026. VACmap: an accurate long-read aligner for unraveling complex genomic rearrangements. *Nat Commun* 16:11198.
- Sedlazeck FJ, et al. 2018. Accurate detection of complex structural variations using single-molecule sequencing (NGMLR/Sniffles). *Nat Methods* 15:461-468.

## Related Skills

- basecalling - The basecaller chemistry/error rate that picks the preset; carries MM/ML to pass with `-y`
- long-read-qc - Read length/quality before mapping; % identity from the aligned BAM
- structural-variants - Consumes the supplementary (split-read) signal this preserves with `-Y`
- clair3-variants - Small-variant calling on this BAM (needs the matched basecaller model)
- nanopore-methylation - Pileup of the MM/ML tags carried through with `-y`
- isoseq-analysis - Spliced alignment of full-length cDNA/Iso-Seq
- alignment-files/sam-bam-basics - Sort/index/inspect the BAM this produces
- alignment-files/alignment-filtering - Filter by MAPQ and secondary/supplementary flags
- genome-assembly/long-read-assembly - Assemble the reads instead of reference-mapping
<!-- END FILE: long-read-sequencing/long-read-alignment/SKILL.md -->

## 子目录：long-read-sequencing/long-read-qc

<!-- BEGIN FILE: long-read-sequencing/long-read-qc/SKILL.md -->
---
name: bio-long-read-sequencing-long-read-qc
description: Assesses Oxford Nanopore and PacBio long-read quality with NanoPlot, cramino, NanoComp, pycoQC/toulligQC, and seqkit, and filters reads with chopper/Filtlong for the downstream goal. Covers why read-only Qscore is an uncalibrated posterior (real accuracy needs a reference BAM), why the sequencing_summary.txt is required for run-health metrics, intent-conditioned filtering (preserve long reads and small replicons for assembly, filter almost nothing for variant calling), the chimera/internal-adapter trap that fabricates SVs, and PacBio rq-based HiFi QC. Use when judging a long-read run, computing read N50 or percent identity, filtering reads before assembly or variant calling, comparing barcodes/runs, or reading run-health red flags.
tool_type: cli
primary_tool: nanoplot
---

## Version Compatibility

Reference examples tested with: NanoPlot 1.42+ (NanoPack2), cramino 0.14+, chopper 0.7+, Filtlong 0.2+, seqkit 2.5+, pycoQC 2.5+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags (chopper/cramino are fast-moving Rust tools)

Inputs that determine what QC is even possible - record them:
- `sequencing_summary.txt` is produced by the basecaller (Dorado/Guppy), not the FASTQ. pycoQC/toulligQC REQUIRE it for pore activity, yield-over-time, and translocation speed. FASTQ-only hand-off permanently loses the run-health layer.
- Percent identity requires a reference BAM (NanoPlot `--bam` / cramino); it cannot come from FASTQ.

If code throws an error, introspect the installed tool (`NanoPlot --help`, `cramino --help`) and adapt the example to the actual API rather than retrying.

# Long-Read QC

**"Is my long-read run any good?"** -> Read length N50 and yield from FASTQ, real percent identity from a reference BAM, run-health from the sequencing_summary, then filter for the downstream goal.
- CLI: `NanoPlot --fastq reads.fq.gz -o qc/` (overview), `cramino aln.bam` (fast BAM stats + identity), `pycoQC -f sequencing_summary.txt -o run.html` (run health)

## The Single Most Important Modern Insight -- Read-Only Qscore Is a Self-Graded Posterior; Real Accuracy and the Failures That Sink a Run Are Only Visible Against a BAM and the Summary

Three corrections a naive long-read QC misses:

1. **Per-read Qscore is an uncalibrated basecaller posterior, not an empirical error rate.** It is the Phred of the mean per-base error probability (NOT the arithmetic mean of Q values), assigned by the basecaller to its own output. ONT's own data: bases labeled Q20 are empirically ~Q12.5 on older chemistries; R10 sup and HiFi are better calibrated but read-only Q still overstates accuracy. Real accuracy is gap-compressed identity from a reference BAM (cramino, NanoPlot `--bam`). Treat Q thresholds as relative knobs, not accuracy guarantees.
2. **The sequencing_summary.txt is the run-health layer, and it is not in the FASTQ.** Pore/channel activity, yield-over-time, translocation speed, and barcode breakdown come from the basecaller's summary TSV. Hand a collaborator only FASTQ and that layer is gone (re-basecalling from POD5 can regenerate it; FASTQ cannot).
3. **The right filter depends on intent, not a fixed cutoff.** Assembly wants the long reads (which are the lowest-Q) and small replicons preserved - subsample by quality, never hard-length-cut. Variant calling wants depth - filter almost nothing and let the caller model per-base Q. HiFi is already Q20+ - do not Phred-filter it like noisy CLR.

## Tool Roles

| Tool | Input | Reports |
|------|-------|---------|
| NanoPlot | FASTQ / BAM / summary | length dist, length-vs-quality, yield; `--bam` adds percent identity |
| cramino | BAM/CRAM | fast N50, yield, gap-compressed identity, `--phased` block N50, `--karyotype` |
| NanoComp | multiple FASTQ/BAM/summaries | compare runs/barcodes (length, quality, identity) |
| pycoQC / toulligQC | sequencing_summary.txt | run health: pore activity, mux map, yield/speed over time, barcodes |
| seqkit stats -a | FASTA/FASTQ | N50, quartiles, total bases, GC |
| chopper | FASTQ (stdin) | filter/trim by mean Q and length |
| Filtlong | FASTQ | keep best reads by length x identity; subsample to a target depth |

Read N50 = the length where 50% of total bases are in reads at least that long (length-weighted, far above the median); it predicts assembly contiguity. NanoFilt and the rrwick Porechop are deprecated/unmaintained (use chopper and Porechop_ABI).

## Intent-Conditioned Filtering Decision Tree

| Goal | Filter | Why |
|------|--------|-----|
| Bacterial / small-genome assembly | light Q/length, then subsample by quality to ~50-100x (`filtlong --target_bases`) | a hard 10 kb length cut erases small plasmids; quality-subsampling beats length filtering |
| Eukaryotic / large-genome assembly | minimal; keep the long tail | the longest (lowest-Q) reads span repeats; over-filtering loses N50 |
| SV calling | light Q only; trim chimeras | chimeras fabricate SVs; trimming matters more than Q filtering |
| SNV / small-variant calling | almost nothing (`chopper -q 10`) | callers model per-base Q and want depth |
| PacBio HiFi | `rq >= 0.99` only | already Q20+; Phred filtering adds nothing |
| cDNA / direct RNA | orient/trim (pychopper), no hard length cut | transcript length is biology; a length cut biases the expression matrix |

## Core Commands

```bash
# Overview from FASTQ (length + posterior quality only - not real accuracy)
NanoPlot --fastq reads.fq.gz -o qc_fastq/ --N50
seqkit stats -a reads.fq.gz                     # N50 + quartiles, fast

# Real accuracy: fast BAM stats incl. gap-compressed identity (needs a reference BAM)
cramino aln.bam
NanoPlot --bam aln.bam -o qc_bam/               # percent identity scatter

# Run health (requires the basecaller's summary)
pycoQC -f sequencing_summary.txt -o run_qc.html

# Compare barcodes / runs
NanoComp --bam s1.bam s2.bam s3.bam --names s1 s2 s3 -o compare/

# Filter for VARIANT calling: light quality only
chopper -q 10 -i reads.fq.gz | gzip > q10.fq.gz

# Subsample for ASSEMBLY: by quality to ~100x of a 5 Mb genome (never a hard length cut)
filtlong --target_bases 500000000 reads.fq.gz | gzip > subsampled.fq.gz
```

## Per-Method Failure Modes

### Trusting FASTQ Qscore as accuracy
**Trigger:** judging a run from `NanoStat --fastq` mean Q. **Mechanism:** Q is an uncalibrated posterior. **Symptom:** "Q20 reads" that are ~94% accurate. **Fix:** align and read gap-compressed identity (cramino / NanoPlot `--bam`).

### QC without the summary
**Trigger:** only FASTQ/BAM at hand-off. **Mechanism:** run-health metrics live in sequencing_summary.txt. **Symptom:** cannot see pore death, mux map, or yield-over-time. **Fix:** obtain the summary (or re-basecall from POD5 to regenerate it).

### Over-filtering erases assembly value
**Trigger:** a blunt `-q 15` or hard 10 kb length cut before assembly. **Mechanism:** the longest reads are the lowest-Q; small plasmids fall under a length floor. **Symptom:** worse N50; missing plasmids. **Fix:** subsample by quality (Filtlong `--target_bases`), keep the long tail, never length-floor above the smallest replicon.

### Chimeras masquerade as SVs
**Trigger:** undetected internal adapters (two molecules ligated as one read). **Mechanism:** the read's halves map to different loci. **Symptom:** phantom translocations/insertions in the SV VCF. **Fix:** check whether Dorado already trimmed/split; use Porechop_ABI for unknown adapters; suspect a biologically implausible long-read spike.

### Re-filtering HiFi like CLR
**Trigger:** Phred-quality-filtering PacBio HiFi. **Mechanism:** HiFi is Q20+ consensus already. **Symptom:** wasted reads, no accuracy gain. **Fix:** filter on `rq >= 0.99` only.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Q20-labeled bases ~Q12.5 empirically | ONT EPI2ME | read-only Q overstates accuracy; verify by alignment |
| Subsample assembly data to ~50-100x | Wick 2026 | >100x slows assemblers and can propagate systematic errors |
| Pore occupancy <~70% in hour 1 rarely recovers | ONT guidance | run-health red flag for early pore death |
| Translocation ~400 b/s (R10 DNA) | ONT chemistry | drift off target correlates with falling basecall Q |
| HiFi `rq >= 0.99` (Q20); `>= 0.999` for Q30 | PacBio CCS | the canonical HiFi accuracy filter |
| `-q 10` as a light QC floor | convention | a relative knob, not a 90%-accuracy guarantee |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| NanoPlot gives no percent identity | run on FASTQ | use `--bam` (identity needs alignment) |
| pycoQC errors / empty | no sequencing_summary.txt | supply the basecaller summary |
| cramino fails on FASTQ | cramino is BAM/CRAM only | give it the aligned BAM |
| Assembly N50 dropped after filtering | hard length/quality cut removed long reads | subsample by quality instead |
| Missing small plasmids | length floor above the replicon size | lower/remove the length floor |
| Phantom SVs in the VCF | chimeric reads | trim/split internal adapters |

## References

- De Coster W, D'Hert S, Schultz DT, Cruts M, Van Broeckhoven C. 2018. NanoPack: visualizing and processing long-read sequencing data. *Bioinformatics* 34(15):2666-2669.
- De Coster W, Rademakers R. 2023. NanoPack2: population-scale evaluation of long-read sequencing data (cramino, chopper). *Bioinformatics* 39(5):btad311.
- Leger A, Leonardi T. 2019. pycoQC, interactive quality control for Oxford Nanopore Sequencing. *J Open Source Softw* 4(34):1236.
- Steinig E, Coin L. 2022. Nanoq: ultra-fast quality control for nanopore reads. *J Open Source Softw* 7(69):2991.
- Bonenfant Q, Noé L, Touzet H. 2023. Porechop_ABI: discovering unknown adapters in Oxford Nanopore sequencing reads. *Bioinform Adv* 3(1):vbac085.
- Shen W, Le S, Li Y, Hu F. 2016. SeqKit: a cross-platform and ultrafast toolkit for FASTA/Q file manipulation. *PLoS ONE* 11(10):e0163962.

## Related Skills

- basecalling - Produces the reads and the sequencing_summary.txt this QC needs
- long-read-alignment - Produces the BAM required for real percent identity
- structural-variants - Chimeras flagged here fabricate SVs there
- medaka-polishing - QC/subsample reads before polishing
- genome-assembly/long-read-assembly - Subsample by quality before assembling
- genome-assembly/genome-profiling - K-mer ploidy/size estimate alongside read QC
- read-qc/quality-reports - General (short-read-oriented) read QC
- sequence-io/sequence-statistics - FASTA/FASTQ summary statistics
<!-- END FILE: long-read-sequencing/long-read-qc/SKILL.md -->

## 子目录：long-read-sequencing/medaka-polishing

<!-- BEGIN FILE: long-read-sequencing/medaka-polishing/SKILL.md -->
---
name: bio-long-read-sequencing-medaka-polishing
description: Polishes Oxford Nanopore draft assemblies to higher consensus accuracy with medaka, a basecaller-model-specific neural consensus net, produces haploid variant calls (VCF) for microbial, mitochondrial, or viral samples, and generates amplicon/viral consensus sequences. Covers the model-matching footgun that silently degrades output, why Racon-first is obsolete and medaka runs directly on Flye output as a single pass, why HiFi must never be fed to medaka, the v1->v2 subcommand renames, and the precise medaka_variant deprecation. Use when polishing an ONT-only assembly, generating an amplicon/viral consensus, calling a haploid ONT consensus, or deciding whether medaka, dorado polish, or Clair3 is the right tool.
tool_type: cli
primary_tool: medaka
---

## Version Compatibility

Reference examples tested with: medaka 2.2+, minimap2 2.28+, samtools 1.19+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Results depend on inputs that outlive the binary version - record them:
- The medaka MODEL must match the basecaller (pore + chemistry + speed + mode + version), e.g. `r1041_e82_400bps_sup_v5.2.0`. A mismatch silently degrades output. Prefer auto-detection from the BAM; verify with `medaka tools list_models`.
- Default models advance with each release (consensus `..._sup_v5.2.0`, variant `..._sup_variant_v5.0.0` at time of writing); confirm with `medaka tools list_models`.
- medaka v2 renamed subcommands (`consensus`->`inference`, `stitch`->`sequence`, `variant`->`vcf`) and moved the backend to PyTorch; v1 tutorials fail.

If code throws an error, introspect the installed tool (`medaka --help`, `medaka_consensus --help`) and adapt the example to the actual API rather than retrying.

# Medaka Polishing

**"Polish my Nanopore assembly"** -> Run one medaka consensus pass directly on the assembler output, with the model that matches the basecaller - because a mismatched model silently makes the consensus worse.
- CLI: `medaka_consensus -i reads.fq -d draft.fa -o out/ -t 8` (model auto-detected from the basecaller annotation)

medaka is an Oxford Nanopore tool. For PacBio (HiFi/CLR) it is the wrong tool entirely - route to genome-assembly/assembly-polishing.

## The Single Most Important Modern Insight -- A Mismatched Model Silently Degrades; HiFi Must Never Be Fed to Medaka; Prove It on Held-Out Data

medaka is a basecaller-model-specific neural consensus net trained on one exact stack (pore + motor enzyme + speed + basecaller mode + basecaller version). Three consequences:

1. **The model must match the basecaller, and a mismatch fails silently.** Fed reads from a different stack, medaka applies corrections calibrated for an error fingerprint that is not there and misses the real one - the consensus gets WORSE, but medaka exits 0, writes a FASTA, and prints no warning. This is the #1 ONT-polishing footgun, sprung by ordinary acts (re-basecalling with newer Dorado, copying a 2020 model name, polishing a public assembly with the default). Prefer auto-detection (`medaka tools resolve_model --auto_model consensus reads.bam`); treat a stale model name as a reason to re-basecall, not to proceed.
2. **HiFi (and CLR) must never be fed to medaka.** It has no PacBio models; an ONT error-model net "corrects" HiFi toward errors HiFi does not make, and HiFi is already QV40+. If the reads are PacBio, medaka is simply wrong -> genome-assembly/assembly-polishing.
3. **Success is only real on held-out data.** medaka maximizes agreement between the consensus and its input pileup, so grading it on those same reads is circular and always looks good. medaka's "N changes" is a risk signal, not a success signal. Measure with reference-free Merqury QV before vs after on held-out / different-platform k-mers (design deferred to genome-assembly/assembly-polishing).

## What medaka Is For (three modes, same model rule)

| Mode | Input | medaka's role |
|------|-------|---------------|
| Assembly polishing | Flye/Canu draft + ONT reads | raise per-base QV (homopolymer-indel cleanup is the dominant win) |
| Haploid variant calling | ONT reads + reference (microbial, mito, viral) | `medaka_variant` wrapper -> haploid VCF (apply with `bcftools consensus` for a FASTA) |
| Amplicon / viral consensus | tiling-amplicon ONT reads | the non-signal consensus arm of ARTIC fieldbioinformatics / EPI2ME wf-artic |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| ONT-only Flye/Canu assembly | `medaka_consensus`, ONE pass, auto-detected model | model-matched consensus; racon pre-step is obsolete |
| Native bacterial isolate (modified DNA) | `medaka_consensus --bacteria` | bacterial-methylation model fixes methylation-motif errors |
| ONT small-variant (diploid/germline) calling | -> clair3-variants | medaka diploid calling deprecated in v2 (Clair3 surpassed it) |
| Haploid microbial/mito/viral VCF | `medaka_variant` (the renamed haploid wrapper) | still supported in v2 |
| Read-level / human polishing | `dorado polish` | ONT's emerging successor; identical bacterial weights to medaka today |
| PacBio HiFi/CLR | -> genome-assembly/assembly-polishing | medaka has no PacBio models; never ONT-polish HiFi |
| Unsure which basecaller model produced the reads | re-basecall, then auto-detect | a guessed model silently degrades the consensus |

## medaka_consensus Mechanics

The wrapper runs three steps: align (`mini_align`, a thin veil over `minimap2 -x map-ont`), infer (`medaka inference`, the neural net over the pileup), and stitch (`medaka sequence`, regions -> consensus FASTA).

```bash
# Canonical modern usage - model auto-detected from the basecaller annotation in the reads
medaka_consensus -i reads.fastq -d draft.fa -o medaka_out/ -t 8
# medaka_out/consensus.fasta is the polished assembly

# Native bacterial isolate: use the methylation-aware bacterial model
medaka_consensus -i reads.fastq -d draft.fa -o medaka_out/ -t 8 --bacteria

# Resolve / list models (do this when auto-detection cannot pick)
medaka tools resolve_model --auto_model consensus reads.bam
medaka tools list_models
```

medaka runs directly on the assembler (Flye) output as a SINGLE pass - do NOT pre-run Racon (contemporary models are trained on raw assembler output; v2 removed the bundled racon wrapper) and do NOT run medaka twice (iteration was racon's role; a second pass risks flipping correct bases).

### Haploid variant calling (v2 names)

medaka_variant emits a VCF only (no consensus FASTA); apply it to the reference with `bcftools consensus` to get a haploid consensus sequence.

```bash
# Wrapper form (renamed from medaka_haploid_variant in v2) - haploid samples only
medaka_variant -i reads.fastq -r reference.fa -o variant_out/

# Manual form - note v2 subcommand names and the hdf -> ref -> out argument order
minimap2 -ax map-ont reference.fa reads.fq | samtools sort -o aln.bam && samtools index aln.bam
medaka inference aln.bam probs.hdf --model r1041_e82_400bps_sup_variant_v5.0.0
medaka vcf probs.hdf reference.fa variants.vcf

# Optional: turn the VCF into a haploid consensus FASTA
bgzip variants.vcf && tabix -p vcf variants.vcf.gz
bcftools consensus -f reference.fa variants.vcf.gz > consensus.fasta
```

## Per-Method Failure Modes

### Silent model mismatch
**Trigger:** running medaka with a model that does not match the basecaller chemistry/version. **Mechanism:** the net corrects toward the wrong error fingerprint. **Symptom:** lower held-out QV; medaka exits 0 with no warning. **Fix:** auto-detect from the BAM; if forced to pick, derive from the actual basecaller and confirm in `list_models`; treat a stale name as a reason to re-basecall.

### HiFi fed to medaka
**Trigger:** polishing a PacBio assembly with medaka. **Mechanism:** ONT-only error model, no PacBio support, on already-QV40+ data. **Symptom:** degraded/homogenized consensus. **Fix:** do not; route to genome-assembly/assembly-polishing.

### Racon-first off-distribution
**Trigger:** running Racon before medaka out of habit. **Mechanism:** contemporary models are trained on raw assembler output; racon-polished input is off the training distribution. **Symptom:** no gain or mild harm. **Fix:** run medaka directly on the Flye output; one pass.

### Missing plasmid poisons the chromosome
**Trigger:** an assembly missing a small replicon (~80% identical to a chromosomal region). **Mechanism:** the absent plasmid's reads misalign onto the chromosome, and medaka "corrects" toward that spurious evidence. **Symptom:** clustered changes that introduce real errors. **Fix:** make the assembly structurally complete first; inspect medaka's changes for clustering (clustered = mapping artifact, not scattered homopolymer fixes).

### Validating on the polishing reads
**Trigger:** judging the polish by medaka's change count or by re-mapping the same reads. **Mechanism:** medaka optimizes agreement with its input pileup. **Symptom:** "improvement" that is circular. **Fix:** reference-free Merqury QV before vs after on held-out / different-platform k-mers.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| 1 medaka pass | medaka README | a single trained-model pass; iteration was racon's role, extra passes flip correct bases |
| model must match basecaller version | medaka model design | mismatch silently degrades; the #1 ONT-polishing error |
| inference threads ~2 | medaka inference behavior | the net is GPU-bound and scales poorly past ~2 CPU threads |
| HiFi QV40+ already | EBP/HiFi baseline | nothing for an ONT consensus net to gain; only harm |
| measure with held-out Merqury QV | Rhie 2020 | the only honest, reference-free before/after instrument |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `medaka consensus` not found / wrong args | v1 subcommand renamed | use `medaka inference` (or the `medaka_consensus` wrapper) |
| `medaka stitch` / `medaka variant` fail | v1 names | `medaka sequence` / `medaka vcf` |
| Polished assembly worse than draft | model mismatch | auto-detect the model; re-basecall if the model is stale |
| medaka errors on PacBio reads | no PacBio models | route to genome-assembly/assembly-polishing |
| Clustered, suspicious changes | missing/mis-structured contig in the draft | complete the assembly first; filter to high-identity alignments |
| Looking for diploid SNP calling | deprecated in v2 | use clair3-variants |

## References

- medaka. Oxford Nanopore Technologies. https://github.com/nanoporetech/medaka (no journal paper; cite the repository).
- Zheng Z, Li S, Su J, Leung AW, Lam TW, Luo R. 2022. Symphonizing pileup and full-alignment for deep learning-based long-read variant calling (Clair3). *Nat Comput Sci* 2:797-803.
- Vaser R, Sović I, Nagarajan N, Šikić M. 2017. Fast and accurate de novo genome assembly from long uncorrected reads (Racon). *Genome Res* 27:737-746.
- Wick RR, Judd LM, Holt KE. 2023. Assembling the perfect bacterial genome using Oxford Nanopore and Illumina sequencing. *PLoS Comput Biol* 19(3):e1010905.
- Rhie A, Walenz BP, Koren S, Phillippy AM. 2020. Merqury: reference-free quality, completeness, and phasing assessment for genome assemblies. *Genome Biol* 21:245.
- Wick RR. 2024. Medaka v2: progress and potential pitfalls. https://rrwick.github.io/2024/10/17/medaka-v2.html (blog; source of the missing-plasmid footgun).

## Related Skills

- basecalling - The basecaller model+version medaka's model must match
- clair3-variants - ONT small-variant (diploid/germline) calling; medaka diploid is deprecated
- long-read-alignment - minimap2 map-ont, the alignment medaka's mini_align wraps
- genome-assembly/assembly-polishing - Polishing strategy authority (HiFi doctrine, hybrid tiers, Merqury QV design)
- genome-assembly/long-read-assembly - Produces the Flye draft medaka polishes
- genome-assembly/assembly-qc - Merqury QV / BUSCO before-vs-after measurement
<!-- END FILE: long-read-sequencing/medaka-polishing/SKILL.md -->

## 子目录：long-read-sequencing/nanopore-methylation

<!-- BEGIN FILE: long-read-sequencing/nanopore-methylation/SKILL.md -->
---
name: bio-long-read-sequencing-nanopore-methylation
description: Calls DNA base modifications (5mC, 5hmC, 6mA, 4mC) directly from Oxford Nanopore and PacBio HiFi long reads encoded as MM/ML SAM tags, piles them into per-site bedMethyl with modkit (or pb-CpG-tools for PacBio), and produces phased allele-specific methylation. Covers why methylation is a basecalling decision that cannot be recovered later, the MM/ML tag-drop failure that silently zeroes methylation through alignment, the MM ? vs . no-call semantics, 5mC/5hmC resolution vs bisulfite, modkit's 10th-percentile auto-threshold, and the haplotagged ASM workflow. Use when calling 5mC/5hmC/6mA from a modBAM, generating bedMethyl, preserving methylation tags through alignment, doing allele-specific or differential methylation, or QC-ing a modification BAM.
tool_type: cli
primary_tool: modkit
---

## Version Compatibility

Reference examples tested with: modkit 0.3+, dorado 1.0+, minimap2 2.28+, samtools 1.19+, pb-CpG-tools 2.3+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Inputs that determine what is even possible - record them:
- The basecaller MODIFICATION model (e.g. `5mCG_5hmCG`) fixes which mods can ever be piled up; it must be requested at basecall time and cannot be added later.
- The MM/ML tags must survive every fastq/alignment step or methylation is silently lost.
- modkit auto-estimates the pass threshold from the data (per run); fix it for cross-sample comparisons.

If code throws an error, introspect the installed tool (`modkit pileup --help`, `modkit --help`) and adapt the example to the actual API rather than retrying.

# Nanopore Methylation

**"Call methylation from my long reads"** -> First confirm the MM/ML tags exist and survived alignment, then pile them into per-site bedMethyl - because methylation is a basecalling decision, not something that can be added now.
- CLI: `modkit pileup aligned.bam out.bed --ref ref.fa --cpg --combine-strands`

## The Single Most Important Modern Insight -- Methylation Is a Basecalling Decision, and the Tags Silently Die in Alignment

Two facts gate the entire skill:

1. **If the reads were not basecalled with a modification model, the signal is already gone.** Mods are inferred from raw signal at basecall time (ONT Remora model in Dorado; PacBio kinetics model in jasmine) and written into the unaligned BAM as MM/ML tags. A plain BAM or a FASTQ cannot yield methylation - there is no post-hoc tool. The only fix is re-basecalling from POD5 (`dorado basecaller sup,5mCG_5hmCG pod5/`). The agent's FIRST move is to check the tags exist: `samtools view in.bam | head | grep -o 'MM:Z:[^\t]*'`.
2. **The MM/ML tags silently die in a normal alignment workflow.** `samtools fastq` drops auxiliary tags unless given `-T MM,ML`; minimap2 ignores them unless given `-y`; hard-clipping breaks MM's per-base skip counting unless `-Y` is set. Miss any one and the aligned BAM still sorts, indexes, and looks fine, but `modkit pileup` returns an empty/all-canonical bedMethyl with no error. Use `dorado aligner` (carries tags natively) or `samtools fastq -T MM,ML | minimap2 -y -Y`, and re-grep for MM:Z AFTER alignment.

## End-to-End modBAM Pipeline

```bash
# 1. MODS-BASECALL (from POD5; the only step that can ever produce methylation)
dorado basecaller sup,5mCG_5hmCG pod5/ > calls.bam      # unaligned BAM, has MM/ML

# 2. TAG-PRESERVING ALIGN (route a is simplest)
dorado aligner ref.mmi calls.bam > aligned.bam                                  # a) native
samtools fastq -T MM,ML calls.bam | minimap2 -y -Y -ax lr:hq ref.fa - \
  | samtools sort -o aligned.bam && samtools index aligned.bam                  # b) manual
samtools view aligned.bam | head | grep -q 'MM:Z' && echo 'tags survived'       # verify!

# 3. PILEUP -> bedMethyl (auto-thresholds at the 10th percentile of ML; NOT 0.5)
modkit pileup aligned.bam out.bed --ref ref.fa --cpg --combine-strands
bgzip out.bed && tabix -p bed out.bed.gz

# 4. (optional) DIFFERENTIAL methylation, long-read native
modkit dmr pair -a A.bed.gz -b B.bed.gz --ref ref.fa --regions cpgislands.bed -o dmr.tsv
```

## MM / ML Tag Spec (what the numbers mean)

- `MM:Z` encodes modification positions: `<canonical base><strand><mod code><. or ?>,<skip counts>;`. Mod codes: `m`=5mC, `h`=5hmC, `a`=6mA, `c`=4mC. The `.`/`?` modifier is load-bearing: `.` = skipped bases are implicitly canonical (count toward the unmodified denominator); `?` = skipped bases are no-call/unknown (land in Nnocall, outside the denominator). Misreading `?` as `.` inflates the canonical denominator and deflates methylation.
- `ML:B:C` is a uint8 per call: value N means probability in `[N/256, (N+1)/256)`, so 255 is ~0.998, never exactly 1.0. Do not threshold `== 1.0`.

## bedMethyl Columns (modkit, 18 columns)

Cols 1-9 are tab-delimited BED9; cols 10-18 are space-delimited (a parsing gotcha). The ones that matter:

| Col | Name | Meaning |
|-----|------|---------|
| 10 | Nvalid_cov | Nmod + Ncanonical + Nother_mod (the denominator; this is "coverage" for QC) |
| 11 | percent_modified | (Nmod / Nvalid_cov) * 100 (a percent, 0-100) |
| 12 | Nmod | passing calls of this modification |
| 13 | Ncanonical | passing calls of the canonical base |
| 14 | Nother_mod | passing calls of a different mod on the same base (5hmC in a 5mC row) |
| 16 | Nfail | calls below the pass threshold (excluded from Nvalid_cov) |
| 18 | Nnocall | aligned canonical base with no mod call (e.g. `?`-skipped) |

For count-based DMR (DSS/methylKit) hand over Nmod and Nvalid_cov, never percent_modified.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| ONT 5mC for mammals | `dorado ...sup,5mCG_5hmCG` -> `modkit pileup --cpg --combine-strands` | mammalian 5mC is overwhelmingly CpG |
| Compare ONT to WGBS/array | `modkit pileup --combine-mods` (or `--preset traditional`) | WGBS conflates 5mC+5hmC; combine to match |
| Study 5hmC biology | keep 5mC and 5hmC split; ideally add oxBS/TAB-seq | bisulfite cannot separate them |
| Plants (CHG/CHH) or bacterial 6mA/4mC | all-context model + `--motif` (not `--cpg`) | methylation is not CpG-restricted there |
| Allele-specific methylation / imprinting | phase + haplotag -> `modkit pileup --partition-tag HP` | one read carries SNV phase AND methylation |
| PacBio HiFi 5mC | `ccs --hifi-kinetics` -> `jasmine` -> pb-CpG-tools (or modkit) | primrose is deprecated; Revio does 5mC on-instrument |
| Differential methylation statistics | `modkit dmr` (native) or export to -> methylation-analysis | DSS/methylKit for dispersion modeling |
| RNA modifications (m6A etc.) | -> epitranscriptomics | direct-RNA mods are out of scope here |

## Phased Allele-Specific Methylation

```bash
# Order is strict: align (tags preserved) -> phase+haplotag -> pileup partitioned by HP
# 1-2. Clair3/DeepVariant -> whatshap/longphase phase + haplotag (adds HP:i:1/2) -> haplotype-phasing
modkit pileup aligned.haplotagged.bam asm_out/ --ref ref.fa --cpg --combine-strands --partition-tag HP
# --partition-tag writes one UNCOMPRESSED bedMethyl per HP value into asm_out/, named by the tag
# value (e.g. 1.bed, 2.bed). bgzip + tabix each before dmr, which requires indexed inputs:
bgzip asm_out/1.bed && tabix -p bed asm_out/1.bed.gz
bgzip asm_out/2.bed && tabix -p bed asm_out/2.bed.gz
modkit dmr pair -a asm_out/1.bed.gz -b asm_out/2.bed.gz --ref ref.fa -o asm.tsv
```

Each haplotype gets ~half the coverage, so the per-site 10x floor effectively wants ~20x total. Imprinted loci (one haplotype ~fully methylated) are the canonical positive control.

## Per-Method Failure Modes

### No methylation in a plain BAM
**Trigger:** BAM basecalled without a mods model. **Mechanism:** mods are a basecall-time decision. **Symptom:** no MM:Z tags; modkit returns nothing. **Fix:** re-basecall from POD5 with a mods model; there is no post-hoc tool.

### Tags died in alignment (the #1 silent killer)
**Trigger:** `samtools fastq | minimap2` without `-T MM,ML`/`-y`. **Mechanism:** fastq export and minimap2 drop the tags. **Symptom:** valid aligned BAM, empty bedMethyl, no error. **Fix:** `dorado aligner`, or `samtools fastq -T MM,ML | minimap2 -y -Y`; verify MM:Z after alignment.

### Methylation fraction looks too low
**Trigger:** misreading `?` (no-call) as `.` (canonical). **Mechanism:** unscored bases counted as unmethylated. **Symptom:** deflated percent_modified; large Nnocall. **Fix:** check the MM modifier and Nnocall; `modkit update-tags` to convert styles if needed.

### 5mC understated vs WGBS
**Trigger:** comparing ONT-5mC-only to bisulfite. **Mechanism:** WGBS reads 5mC+5hmC together. **Symptom:** ONT looks lower by the 5hmC fraction. **Fix:** `--combine-mods`/`--preset traditional` to combine before comparing.

### Cross-sample thresholds not comparable
**Trigger:** relying on modkit's auto-threshold per sample. **Mechanism:** the 10th-percentile cut is data-dependent. **Symptom:** sample-specific thresholds confound a DMR. **Fix:** fix a common `--filter-threshold`/`--mod-thresholds` across samples.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Nvalid_cov >= 10 per CpG | field standard | below it, single-site fractions are noisy (~20x total for phased) |
| modkit pass = 10th percentile of ML | modkit docs | discards the lowest-confidence ~10%; improves WGBS concordance |
| R10 ONT vs WGBS r ~ 0.84-0.95 | benchmarks | adequate-depth site-level concordance (R10 > R9) |
| ML 255 ~ 0.998 (not 1.0) | SAM spec | uint8 bin [255/256, 1.0); never test == 1.0 |
| no `--min-coverage` flag on pileup | modkit API | filter bedMethyl on Nvalid_cov post-hoc instead |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Empty bedMethyl / Nvalid_cov 0 | tags dropped or never present | grep MM:Z; re-basecall or re-align preserving tags |
| `modkit pileup --min-coverage` unknown flag | no such flag | filter on Nvalid_cov (col 10) after pileup |
| `modkit extract in.bam out.tsv` errors | needs a subcommand | `modkit extract full` / `modkit extract calls` |
| `modkit dmr` fails on raw .bed | inputs must be indexed | `bgzip` + `tabix -p bed` first |
| Sparse bedMethyl with `--combine-strands` | records lack MN tags (old basecaller or hard-clipped) | basecall with current Dorado and align with `-Y` (no hard-clip) |
| Methylation lower than expected | `?` read as `.`; or 5hmC excluded vs WGBS | check Nnocall; `--combine-mods` to match WGBS |
| primrose not found (PacBio) | deprecated/archived | use `jasmine` (or Revio on-instrument 5mC) |

## References

- Simpson JT, Workman RE, Zuzarte PC, et al. 2017. Detecting DNA cytosine methylation using nanopore sequencing. *Nat Methods* 14:407-410.
- Yuen ZW-S, Srivastava A, Daniel R, et al. 2021. Systematic benchmarking of tools for CpG methylation detection from nanopore sequencing (METEORE). *Nat Commun* 12:3438.
- Tse OYO, Jiang P, Cheng SH, et al. 2021. Genome-wide detection of cytosine methylation by single molecule real-time sequencing. *PNAS* 118(5):e2019768118.
- Cheetham SW, Kindlova M, Ewing AD. 2022. Methylartist: tools for visualizing modified bases from nanopore sequence data. *Bioinformatics* 38(11):3109-3112.
- SAM Optional Fields Specification (SAMtags): MM/ML base-modification tags. samtools/hts-specs.

## Related Skills

- basecalling - The upstream gate: methylation must be requested at basecall time
- long-read-alignment - Carry MM/ML through with `-y -Y` (or use dorado aligner)
- haplotype-phasing - Phase + haplotag the BAM for allele-specific methylation
- clair3-variants - SNVs to phase before allele-specific methylation
- methylation-analysis/dmr-detection - DMR statistics downstream of bedMethyl
- methylation-analysis/methylkit-analysis - methylKit differential methylation
- epitranscriptomics/m6anet-analysis - Direct-RNA m6A (out of scope here)
- workflows/methylation-pipeline - End-to-end methylation pipeline
<!-- END FILE: long-read-sequencing/nanopore-methylation/SKILL.md -->

## 子目录：long-read-sequencing/structural-variants

<!-- BEGIN FILE: long-read-sequencing/structural-variants/SKILL.md -->
---
name: bio-long-read-sequencing-structural-variants
description: Detects structural variants (deletions, insertions, inversions, duplications, translocations) from Oxford Nanopore and PacBio long-read alignments with Sniffles2, cuteSV, SVIM, and assembly-based callers, joint-genotypes cohorts via the Sniffles2 .snf workflow, and benchmarks with Truvari against GIAB. Covers why an SV call is a representation artifact (the tandem-repeat BED, aligner, and Truvari params set precision/recall as much as the caller), the cuteSV per-platform parameter trap, soft-clipped supplementary alignments as the SV substrate, and the somatic/mosaic boundary to Severus/nanomonsv. Use when calling germline or somatic SVs from ONT/HiFi reads, joint-genotyping a cohort, choosing or tuning an SV caller, or benchmarking SV calls.
tool_type: cli
primary_tool: sniffles
---

## Version Compatibility

Reference examples tested with: Sniffles 2.2+, cuteSV 2.1+, minimap2 2.28+, samtools 1.19+, truvari 4.0+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Results depend on inputs that outlive the binary version - record them:
- The reference-matched tandem-repeat BED supplied to the caller (Sniffles `--tandem-repeats`) drives the FP rate in repeats more than any other setting. Record which TR BED was used.
- Benchmark numbers depend on the region set + TR handling + Truvari params; record all three.
- cuteSV parameters are platform-specific (ONT vs HiFi vs CLR); the defaults are not platform-appropriate.

If code throws an error, introspect the installed tool (`sniffles --help`, `cuteSV --help`) and adapt the example to the actual API rather than retrying.

# Long-Read Structural Variants

**"Find structural variants in my long reads"** -> Map with the SV-ready preset (soft-clipped supplementaries), call with a TR-aware caller, and benchmark stating the region set and Truvari params.
- CLI: `sniffles --input aln.bam --vcf svs.vcf --reference ref.fa --tandem-repeats TR.bed`

Long reads are the killer app for SVs: a single read spans the breakpoint (within-read CIGAR or split alignment) and resolves repeats short reads cannot. By convention SV = >=50 bp; the 30-100 bp range is a VNTR-dominated gray zone where callers disagree most.

## The Single Most Important Modern Insight -- An SV Call Is a Representation Artifact as Much as a Biological Fact

In tandem repeats and segmental duplications, the same biological event has many valid VCF encodings - a deletion can be written as the reciprocal insertion on the other allele, and a VNTR expansion's breakpoints slide freely across repeat units. Consequently:

1. **The tandem-repeat BED, the aligner, and the Truvari parameters decide precision/recall as much as the caller does.** A claim like "caller X has F1 0.95" is meaningless without also stating the region set, the TR BED supplied to the caller, and the Truvari params - change any one and the number moves more than the gap between callers.
2. **Without a TR BED, one event fragments into several false-positive calls** with inconsistent breakpoints. `--tandem-repeats` makes clustering repeat-aware (widening the merge window inside annotated TRs) - the single biggest FP-reduction lever, not a nicety.
3. **`truvari refine` exists precisely to re-harmonize representations** within TR regions; benchmarking TR-dense regions without it systematically understates recall.

## Caller Taxonomy

| Tool | Regime | Best for | Citation |
|------|--------|----------|----------|
| Sniffles2 | germline + population + mosaic | the default germline workhorse; cohort joint genotyping; .snf merge | Smolka 2024 *Nat Biotechnol* 42:1571 |
| cuteSV | germline | high sensitivity, speed; per-platform tuning required | Jiang 2020 *Genome Biol* 21:189 |
| SVIM | germline | scores (not hard-filters) SVs; good INS detection | Heller 2019 *Bioinformatics* 35:2907 |
| pbsv | germline (PacBio) | two-step discover->call; official PacBio tool | PacBio (no journal paper) |
| NanoVar | germline, low-depth | 4-8x ONT clinical | Tham 2020 *Genome Biol* 21:56 |
| dipcall / SVIM-asm / PAV | assembly-based germline | most accurate single sample with phased HiFi; truth-set generation | Li 2018; Heller 2021; Ebert 2021 |
| Severus | somatic (tumor-normal) | cancer T/N, complex/subclonal | Keskus 2026 *Nat Biotechnol* |
| nanomonsv | somatic (tumor-normal) | precise somatic breakpoints, MEI | Shiraishi 2023 *NAR* 51:e74 |
| SVision-pro | de novo + somatic, complex | resolving nested CSVs | Wang 2025 *Nat Biotechnol* 43:181 |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Single ONT/HiFi germline sample | Sniffles2 + `--tandem-repeats` | TR-aware, auto support, fast |
| Cohort germline | Sniffles2 per-sample `.snf` -> merge | re-genotypes from raw signal; true joint genotypes |
| Maximum sensitivity / speed | cuteSV with the platform-matched param set | per-platform tuning is mandatory |
| Phased HiFi, want best per-sample accuracy | assembly-based (dipcall/SVIM-asm) -> hifi-assembly | resolves the alt haplotype directly |
| Tumor-normal somatic SVs | Severus or nanomonsv | paired callers; Sniffles `--mosaic` is single-sample only |
| Low-VAF mosaic in one sample | Sniffles2 `--mosaic` | lowers support, reports VAF (not a T/N caller) |
| Low coverage (4-8x) | NanoVar | designed for low-depth clinical |
| Benchmarking | Truvari (+`refine`) vs GIAB Tier1/CMRG | the field standard; state region + params |

## Alignment for SV Calling

Map with minimap2 (the modern default; NGMLR is a higher-precision/slower legacy niche for Sniffles). Use the platform preset and keep soft-clipped supplementary alignments - split-read callers reconstruct breakpoints from the clipped sequence on those records.

```bash
minimap2 -ax map-ont --MD -Y ref.fa ont.fq.gz | samtools sort -o aln.bam && samtools index aln.bam
#   -Y keeps SEQ on supplementaries (the SV substrate); --MD for cuteSV; map-hifi/map-pb for PacBio
```

## Sniffles2 - germline and the .snf population workflow

```bash
# Single sample (always supply --reference for INS sequence and --tandem-repeats for repeats)
sniffles --input aln.bam --vcf svs.vcf --reference ref.fa --tandem-repeats human_GRCh38_TR.bed

# Cohort: per-sample .snf signature index, then merge + joint-genotype
sniffles --input s1.bam --snf s1.snf --reference ref.fa --tandem-repeats TR.bed
sniffles --input s2.bam --snf s2.snf --reference ref.fa --tandem-repeats TR.bed
sniffles --input s1.snf s2.snf --vcf cohort.vcf --reference ref.fa

# Force-call / regenotype a known SV set in a new sample
sniffles --input new.bam --genotype-vcf known_svs.vcf --vcf genotyped.vcf

# Single-sample low-VAF / mosaic (NOT a tumor-normal caller)
sniffles --input tumor.bam --vcf mosaic.vcf --mosaic
```

The `.snf` is a binary signature index (NOT a VCF - never bcftools it); it retains sub-threshold signatures so the merge re-genotypes an SV even in a sample that did not independently pass support.

## cuteSV - the per-platform parameter trap

cuteSV's defaults are not platform-appropriate; the README gives distinct sets by error rate. `--genotype` is OFF by default. Positional args: `cuteSV <bam> <ref> <out.vcf> <work_dir>`. Force-calling moved to the separate cuteFC tool.

| Platform | --max_cluster_bias_INS | --diff_ratio_merging_INS | --max_cluster_bias_DEL | --diff_ratio_merging_DEL |
|----------|------------------------|--------------------------|------------------------|--------------------------|
| ONT | 100 | 0.3 | 100 | 0.3 |
| PacBio HiFi/CCS | 1000 | 0.9 | 1000 | 0.5 |
| PacBio CLR | 100 | 0.3 | 200 | 0.5 |

```bash
mkdir cutesv_work
cuteSV aln.bam ref.fa cutesv.vcf cutesv_work --genotype \
  --max_cluster_bias_INS 100 --diff_ratio_merging_INS 0.3 \
  --max_cluster_bias_DEL 100 --diff_ratio_merging_DEL 0.3   # ONT set
```

## Benchmarking with Truvari

```bash
truvari bench --base giab_tier1.vcf.gz --comp calls.vcf.gz \
  --includebed tier1_regions.bed --pctseq 0.7 --refdist 500 --passonly -o bench/
truvari refine bench/        # re-harmonize TR-region representations for a fair comparison
```

`--pctseq` (default 0.7) compares the actual inserted/deleted sequence, not just coordinates - set 0 for depth-based callers lacking alt sequence, keep 0.7 for long-read callers. Region set dominates the headline: Tier1 (resolvable INS/DEL >=50 bp) overstates whole-genome performance; CMRG reflects hard clinical loci. Tier1 v0.6 is INS/DEL only - do not report INV recall against it.

## Per-Method Failure Modes

### One VNTR fragments into many false positives
**Trigger:** calling in tandem repeats without a TR BED. **Mechanism:** the breakpoint slides across repeat units, scattering signatures. **Symptom:** several calls with inconsistent breakpoints where one event exists. **Fix:** supply `--tandem-repeats` to the caller; `truvari refine` when benchmarking.

### cuteSV defaults inflate or fragment calls
**Trigger:** running cuteSV with one parameter set across platforms. **Mechanism:** HiFi settings over-merge ONT noise; ONT settings fragment clean HiFi signatures. **Symptom:** FP inflation or split calls. **Fix:** use the platform-matched set; remember `--genotype` is off by default.

### Missing insertion sequence / breakpoints
**Trigger:** Sniffles without `--reference`, or alignment without `-Y`. **Mechanism:** no reference -> no ALT sequence; hard-clipped supplementaries -> lost breakpoint sequence. **Symptom:** INS lack sequence; imprecise breakpoints. **Fix:** add `--reference` and align with `-Y`.

### Treating Sniffles --mosaic as a cancer caller
**Trigger:** somatic SV calling with single-sample `--mosaic`. **Mechanism:** mosaic mode lowers support in one sample; it has no normal to subtract. **Symptom:** germline SVs reported as somatic; FP at low VAF. **Fix:** Severus or nanomonsv (paired tumor-normal).

### Comparing F1 across studies that handled repeats differently
**Trigger:** quoting F1 without region + TR BED + Truvari params. **Mechanism:** representation handling moves the number more than the caller. **Symptom:** apples-to-oranges comparisons. **Fix:** fix the region set, TR BED, and Truvari params; run `truvari refine`.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| SV >= 50 bp | GIAB convention | 30-100 bp is a VNTR gray zone where callers disagree |
| Sniffles `--minsvlen` 35, `--mapq` 25, `--minsupport auto` | Sniffles2 manpage | the actual defaults (support is coverage-derived, not a fixed 3) |
| Coverage ~20-30x germline; >30-60x mosaic/somatic | SV practice | large SVs callable from 5-10x; low-VAF needs depth |
| Truvari `--pctseq 0.7`, `--refdist 500` | English 2022 | sequence-aware INS matching; loosen refdist to 1000 only for fuzzy callers |
| cuteSV params per platform | cuteSV README | error rate sets cluster bias / merge ratio |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Many FP calls in repeats | no TR BED | supply `--tandem-repeats` |
| cuteSV VCF has no GT | `--genotype` off by default | add `--genotype` |
| Cannot bcftools the `.snf` | `.snf` is a binary signature index | use it as Sniffles input, not a VCF |
| INS records lack sequence | `--reference` not supplied | add `--reference ref.fa` |
| Imprecise/missing breakpoints | supplementaries hard-clipped | align with minimap2 `-Y` |
| Looking for cuteSV force-calling flag | moved to cuteFC | use the cuteFC tool |
| Somatic SVs from a single sample | germline/mosaic caller | Severus / nanomonsv (paired) |

## References

- Smolka M, Paulin LF, Grochowski CM, et al. 2024. Detection of mosaic and population-level structural variants with Sniffles2. *Nat Biotechnol* 42:1571-1580.
- Jiang T, Liu Y, Jiang Y, et al. 2020. Long-read-based human genomic structural variation detection with cuteSV. *Genome Biol* 21:189.
- Heller D, Vingron M. 2019. SVIM: structural variant identification using mapped long reads. *Bioinformatics* 35:2907-2915.
- English AC, Menon VK, Gibbs RA, Metcalf GA, Sedlazeck FJ. 2022. Truvari: refined structural variant comparison preserves allelic diversity. *Genome Biol* 23:271.
- Zook JM, Hansen NF, Olson ND, et al. 2020. A robust benchmark for detection of germline large deletions and insertions. *Nat Biotechnol* 38:1347-1355.
- Wagner J, Olson ND, Harris L, et al. 2022. Curated variation benchmarks for challenging medically relevant autosomal genes (CMRG). *Nat Biotechnol* 40:672-680.
- Keskus AG, Bryant A, Ahmad T, et al. 2026. Severus detects somatic structural variation and complex rearrangements in cancer genomes using long-read sequencing. *Nat Biotechnol* 44:247-257.

## Related Skills

- long-read-alignment - SV-ready mapping (`-Y` soft-clip, platform preset)
- basecalling - Read accuracy/length that gates breakpoint precision
- clair3-variants - Small variants (<50 bp) are Clair3's job, not an SV caller's
- haplotype-phasing - Haplotag the BAM for haplotype-specific / phased SVs
- genome-assembly/hifi-assembly - Phased assembly for assembly-based SV calling
- variant-calling/structural-variant-calling - The variant-calling-side SV view
- variant-calling/vcf-manipulation - Filter/merge the SV VCFs
- genome-intervals/gtf-gff-handling - Annotate SVs against gene models
<!-- END FILE: long-read-sequencing/structural-variants/SKILL.md -->

<!-- END CATEGORY: long-read-sequencing -->

