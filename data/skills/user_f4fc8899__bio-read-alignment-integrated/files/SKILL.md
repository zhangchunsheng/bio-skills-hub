---
slug: bio-read-alignment-integrated
version: 1.0.0
displayName: "读段比对 / Short-read alignment"
name: bio-read-alignment-integrated
summary: >-
  中文：读段比对综合技能，整合 4 个相关专题，覆盖短读段比对：BWA-MEM2、Bowtie2、STAR、HISAT2的算法选择与参数调优。 English: Integrated Short-read alignment skill covering 4 related topics, including Short-read alignment: algorithm selection and parameter tuning for BWA-MEM2, Bowtie2, STAR, HISAT2.
description: >-
  中文：这是一个面向读段比对的综合生物信息学 Skill，整合当前分类下 4 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：短读段比对：BWA-MEM2、Bowtie2、STAR、HISAT2的算法选择与参数调优。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：HISAT2, STAR, bowtie2。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Short-read alignment, combining 4 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Short-read alignment: algorithm selection and parameter tuning for BWA-MEM2, Bowtie2, STAR, HISAT2. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: HISAT2, STAR, bowtie2. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# read-alignment 分类 Skill 整合版

> 本文件整合同一主分类目录下 4 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: read-alignment -->

## 子目录：read-alignment/bowtie2-alignment

<!-- BEGIN FILE: read-alignment/bowtie2-alignment/SKILL.md -->
---
name: bio-read-alignment-bowtie2-alignment
description: Aligns DNA short reads to a reference with Bowtie2, choosing end-to-end (whole read must align) vs local (soft-clip read ends) mode and a sensitivity preset; the de-facto aligner for ChIP-seq, ATAC-seq, and CUT&RUN, where fragment-geometry flags (--no-mixed, --no-discordant, --dovetail, -X) and a tool-appropriate MAPQ filter feed the peak caller. Use when aligning ChIP/ATAC/CUT&RUN reads, when read ends are adapter-contaminated and need soft-clipping, or when a tunable sensitivity/speed preset is wanted. DNA variant calling prefers bwa-alignment; RNA spliced alignment is star-alignment/hisat2-alignment; the QC gate and cross-tool MAPQ scale are alignment-files; peak calling is chip-seq/atac-seq; bisulfite uses methylation-analysis/bismark-alignment.
tool_type: cli
primary_tool: bowtie2
---

## Version Compatibility

Reference examples tested with: bowtie2 2.5+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Bowtie2 Alignment -- End-to-End vs Local and the Fragment-Geometry Flags Are the Whole Decision

**"Align my ChIP-seq / ATAC-seq reads"** -> Map short reads with Bowtie2, choosing whether the entire read must align (end-to-end) or read ends may be soft-clipped (local), and which fragment-geometry flags to set -- because for peak assays the mode, the preset, and the --no-mixed/--dovetail/-X flags determine the fragment coordinates the peak caller actually sees.
- CLI: `bowtie2 -p 8 -x index -1 R1.fq.gz -2 R2.fq.gz | samtools sort -o aligned.bam -`

Scope: DNA short-read mapping with Bowtie2 and the mode/preset/geometry choices that matter for ChIP/ATAC/CUT&RUN. Contig naming, the QC gate, and the cross-tool MAPQ scale -> alignment-files (bam-statistics / sam-bam-basics). Peak calling and the ATAC Tn5 cut-site shift -> chip-seq, atac-seq. BAM sort/dedup/stats -> alignment-files. Read trimming -> read-qc. OUT OF SCOPE: DNA variant calling (prefer bwa-alignment), RNA (star-alignment/hisat2-alignment), bisulfite (methylation-analysis/bismark-alignment -- Bismark wraps Bowtie2 internally, do not call Bowtie2 directly for WGBS).

## The Single Most Important Modern Insight

1. **End-to-end (default) vs --local is a biology decision about whether the full read must align.** End-to-end forces the entire read to match (best score 0, no soft-clipping) -- correct for clean genomic DNA. `--local` soft-clips untrustworthy read ends to maximize score (positive match bonus) -- correct when read ends are junk: adapter read-through, the short fragments and frequent adapter contamination of ATAC-seq, or amplicon primer ends. Using end-to-end on adapter-contaminated reads mis-penalizes the good core and depresses the alignment rate; the fix is to trim first or use `--local`.
2. **Bowtie2 MAPQ is a different scale from BWA and caps low.** It is AS/XS-driven and discrete, capping at 42 in end-to-end mode and 44 in local mode -- it never reaches BWA's 60. A `MAPQ >= 30` filter (the ENCODE ChIP/ATAC convention to drop multimappers) is fine, but a BWA-style `MAPQ >= 60` "uniquely mapped" filter copied from a DNA-variant pipeline discards every Bowtie2 read. Always tune the MAPQ threshold to the aligner -- see alignment-files/sam-bam-basics for the full cross-tool table.
3. **For peak assays, the fragment-geometry flags set the coordinates the peak caller consumes.** ChIP/ATAC interpret signal at the fragment level (summits, fragment midpoints, nucleosome spacing), so a singleton ("mixed") or geometrically inconsistent (discordant) alignment injects a fragment with undefined length/position. `--no-mixed --no-discordant` restrict to concordant proper pairs; `-X 2000` widens the allowed fragment length for ATAC's nucleosome-spanning fragments; `--dovetail` lets short-fragment pairs whose mates extend past each other still count as concordant (by default such pairs are not concordant and are dropped once `--no-mixed`/`--no-discordant` are set). These flags, not the core alignment, are what make the downstream peak set correct.

## Tool Taxonomy

| Mode / tool | Citation | Mechanism / role | When |
|-------------|----------|------------------|------|
| Bowtie2 `--end-to-end` (default) | Langmead & Salzberg 2012 Nat Methods 9:357 | whole read must align; no soft-clipping; scores <= 0 | clean genomic DNA, ChIP-seq on trimmed reads |
| Bowtie2 `--local` | Langmead & Salzberg 2012 | soft-clips read ends; positive match bonus | adapter read-through, ATAC-seq, amplicon ends |
| Sensitivity presets | Langmead & Salzberg 2012 | preset expansions of -D/-R/-N/-L/-i | trade speed vs sensitivity predictably |
| bwa-mem2 | Vasimuddin 2019 IEEE IPDPS | seed-and-extend; ALT/decoy-aware | DNA variant calling instead (route OUT) -> bwa-alignment |
| Bismark (wraps Bowtie2) | Krueger & Andrews 2011 Bioinformatics 27:1571 | 3-letter C->T-aware mapping engine | bisulfite/WGBS (route OUT) -> methylation-analysis/bismark-alignment |
| STAR / HISAT2 | -- | splice-aware (route OUT) | any RNA library -> star-alignment, hisat2-alignment |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| ChIP-seq, trimmed reads | `--very-sensitive --no-mixed --no-discordant`, end-to-end, then `-q 30` | clean reads align fully; drop singletons/discordants and multimappers for peak calling |
| CUT&RUN / CUT&Tag | `--very-sensitive --local --dovetail --no-mixed --no-discordant -I 10 -X 700` | sub-nucleosomal short fragments (like ATAC); the E. coli carry-over reads are the spike-in normalizer, so align them (do not discard as contamination) -> chip-seq |
| ATAC-seq | `--very-sensitive --local --dovetail -X 2000 --no-mixed --no-discordant` | soft-clip adapter read-through; admit nucleosome-spanning and dovetailed short fragments |
| Reads with adapter read-through (untrimmed) | `--local` (or trim first) | end-to-end mis-penalizes contaminated ends |
| Need maximum sensitivity on divergent data | `--very-sensitive` (or `-N 1`) | more seed-extension attempts / a seed mismatch allowed |
| Multi-mapping analysis | `-k <N>` or `-a` | report multiple/all alignments (MAPQ unreliable in -k mode) |
| DNA variant calling | route OUT to bwa-alignment | bwa-mem2 is the variant-calling community default |
| RNA-seq | route OUT to star-alignment / hisat2-alignment | spliced reads need an N-CIGAR aligner |

Default when uncertain: `--very-sensitive` end-to-end with `--no-mixed --no-discordant` for ChIP; switch to `--local --dovetail -X 2000` for ATAC; filter `-q 30` to drop multimappers.

## Build Index

```bash
bowtie2-build --threads 8 reference.fa reference_index
# emits reference_index.{1,2,3,4}.bt2 and .rev.{1,2}.bt2. Pass the BASENAME (reference_index) to -x, NOT a file.
```

## Basic Alignment

```bash
# Paired-end, streamed to a sorted BAM. Bowtie2 prints the alignment summary to stderr.
bowtie2 -p 8 -x reference_index -1 reads_1.fq.gz -2 reads_2.fq.gz 2> align.log | \
    samtools sort -@ 4 -o aligned.sorted.bam -
samtools index aligned.sorted.bam
# single-end: -U reads.fq.gz instead of -1/-2.
```

## ChIP-seq

```bash
bowtie2 -p 8 --very-sensitive --no-mixed --no-discordant \
    --rg-id sample1 --rg SM:sample1 --rg PL:ILLUMINA --rg LB:lib1 \
    -x reference_index -1 chip_1.fq.gz -2 chip_2.fq.gz 2> chip.log | \
    samtools view -bS -q 30 -F 1804 - | \
    samtools sort -@ 4 -o chip.bam -
# -q 30 drops multimappers (Bowtie2 scale: max 42 e2e); -F 1804 removes unmapped/secondary/dup/QC-fail.
```

## ATAC-seq

```bash
# Local mode + dovetail + wide -X for adapter read-through and nucleosome-spanning short fragments.
bowtie2 -p 8 --very-sensitive --local --dovetail -X 2000 --no-mixed --no-discordant \
    -x reference_index -1 atac_1.fq.gz -2 atac_2.fq.gz 2> atac.log | \
    samtools view -bS -q 30 -F 1804 - | \
    samtools sort -@ 4 -o atac.bam -
# The Tn5 +4/-5 cut-site shift is a DOWNSTREAM signal-track transform, not done here -> atac-seq.
```

## Sensitivity Presets (end-to-end; the preset IS the speed/sensitivity decision)

```bash
bowtie2 --very-fast       -x index -1 r1.fq -2 r2.fq    # -D 5  -R 1 -N 0 -L 22 -i S,0,2.50
bowtie2 --sensitive       -x index -1 r1.fq -2 r2.fq    # -D 15 -R 2 -N 0 -L 22 -i S,1,1.15  (DEFAULT)
bowtie2 --very-sensitive  -x index -1 r1.fq -2 r2.fq    # -D 20 -R 3 -N 0 -L 20 -i S,1,0.50
# Append -local for the local-mode presets (e.g. --very-sensitive-local). Higher -D/-R/shorter -L = more sensitive, slower.
```

## Multi-mapping and Unmapped Output

```bash
bowtie2 -k 5  -x index -1 r1.fq -2 r2.fq -S out.sam     # up to 5 alignments/read (MAPQ unreliable in -k)
bowtie2 -a    -x index -1 r1.fq -2 r2.fq -S out.sam     # ALL alignments (slow on repetitive genomes)
bowtie2 --un-conc-gz unmapped_%.fq.gz -x index -1 r1.fq.gz -2 r2.fq.gz -S out.sam  # save unaligned pairs
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| -x | -- | index BASENAME (not a filename) |
| -1 / -2 / -U | -- | paired / single-end reads |
| --end-to-end / --local | end-to-end | whole-read vs soft-clipped alignment |
| -I / -X | 0 / 500 | min / max fragment length for a concordant pair |
| --no-mixed / --no-discordant | off | suppress singleton / discordant alignments |
| --dovetail | off | treat mate-overrun pairs as concordant (short-fragment ATAC) |
| -N | 0 | mismatches allowed in a seed (0 or 1; 1 is slower, more sensitive) |
| -L | 22 (e2e) / 20 (local) | seed length |
| -k / -a | off | report up to k / all alignments |
| --rg-id / --rg | -- | read-group id / fields |

## Per-Method Failure Modes

### End-to-end on adapter-contaminated reads
**Trigger:** untrimmed reads with adapter read-through aligned in default end-to-end mode. **Mechanism:** the contaminated 3' end forces mismatches the whole-read alignment cannot escape. **Symptom:** depressed alignment rate, lost reads at fragment ends. **Fix:** trim first (-> read-qc) or use `--local` to soft-clip the junk ends.

### MAPQ filter copied from a BWA pipeline
**Trigger:** a `MAPQ >= 60` "uniquely mapped" filter applied to Bowtie2 output. **Mechanism:** Bowtie2 caps at 42 (e2e) / 44 (local). **Symptom:** an empty BAM. **Fix:** use a tool-appropriate threshold (`-q 30` drops multimappers) -> alignment-files/sam-bam-basics.

### ATAC pairs flagged discordant
**Trigger:** ATAC alignment without `--dovetail` (and a too-tight `-X`). **Mechanism:** very short fragments produce mates that extend past each other, which default Bowtie2 does not count as concordant. **Symptom:** many real short-fragment pairs dropped by a `--no-mixed`/`--no-discordant` filter. **Fix:** add `--dovetail` and widen `-X 2000`.

### -x given a filename
**Trigger:** `-x reference_index.1.bt2` (a file) instead of the basename. **Mechanism:** `-x` expects the index basename. **Symptom:** "Could not locate a Bowtie index" error. **Fix:** pass the basename (`-x reference_index`).

### Calling Bowtie2 directly for bisulfite data
**Trigger:** aligning WGBS reads with plain Bowtie2. **Mechanism:** bisulfite converts C->T, breaking 4-letter matching. **Symptom:** very low alignment rate, strand-biased mismatches. **Fix:** use Bismark, which wraps Bowtie2 with C->T-aware mapping -> methylation-analysis/bismark-alignment.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| MAPQ cap 42 (end-to-end) / 44 (local) | Bowtie2 source (unique.h) | the scale never reaches BWA's 60; tune filters per aligner |
| `-q 30` for ChIP/ATAC | ENCODE peak-assay convention | drops multimappers from repeats before peak calling |
| -X 500 default, -X 2000 for ATAC | Bowtie2 manual | ATAC fragments span nucleosomes; the default cap flags them discordant |
| default preset `--sensitive` (-D15 -R2 -N0 -L22) | Bowtie2 manual | balanced speed/sensitivity; `--very-sensitive` for divergent/peak data |
| -F 1804 in ChIP filtering | ENCODE convention | removes unmapped + mate-unmapped + secondary + duplicate + QC-fail |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "Could not locate a Bowtie index" | `-x` given a file, not the basename | pass the index basename to `-x` |
| Empty BAM after MAPQ filter | BWA-style `-q 60` on a 42/44-capped scale | use `-q 30` (Bowtie2 scale) -> alignment-files/sam-bam-basics |
| Low alignment rate | adapter read-through, wrong reference, contamination | trim (-> read-qc) or `--local`; verify the reference; confirm species -> read-qc/contamination-screening |
| Many ATAC pairs dropped as discordant | missing `--dovetail`, too-tight `-X` | add `--dovetail -X 2000` |
| Very low rate on bisulfite reads | plain Bowtie2 on WGBS | use Bismark -> methylation-analysis/bismark-alignment |

## References

- Langmead B, Salzberg SL. 2012. Fast gapped-read alignment with Bowtie 2. *Nat Methods* 9:357-359.
- Langmead B, Trapnell C, Pop M, Salzberg SL. 2009. Ultrafast and memory-efficient alignment of short DNA sequences to the human genome. *Genome Biol* 10:R25.
- Krueger F, Andrews SR. 2011. Bismark: a flexible aligner and methylation caller for Bisulfite-Seq applications. *Bioinformatics* 27:1571-1572.
- Vasimuddin M, Misra S, Li H, Aluru S. 2019. Efficient architecture-aware acceleration of BWA-MEM for multicore systems. *IEEE IPDPS* 2019:314-324.

## Related Skills

- bwa-alignment - DNA variant-calling alignment with bwa-mem2 (ALT/decoy-aware)
- star-alignment - RNA splice-aware alignment (when reads cross junctions)
- read-qc/fastp-workflow - Trim adapters before end-to-end alignment
- alignment-files/duplicate-handling - Mark/remove duplicates after alignment
- alignment-files/sam-bam-basics - The cross-tool MAPQ scale, SAM flags, CIGAR
- alignment-files/bam-statistics - flagstat/idxstats QC gate; what a high mapping rate hides
- chip-seq/peak-calling - Call peaks from ChIP/CUT&RUN BAMs
- atac-seq/atac-peak-calling - ATAC peak calling and the Tn5 cut-site shift
- methylation-analysis/bismark-alignment - Bisulfite alignment (wraps Bowtie2)
<!-- END FILE: read-alignment/bowtie2-alignment/SKILL.md -->

## 子目录：read-alignment/bwa-alignment

<!-- BEGIN FILE: read-alignment/bwa-alignment/SKILL.md -->
---
name: bio-read-alignment-bwa-alignment
description: Aligns DNA short reads (paired- or single-end) to a reference genome with bwa-mem2, the maintained successor to BWA-MEM, for WGS/WES and germline/somatic variant-calling pipelines; covers index build, read-group injection, the collate/fixmate/sort/markdup ordering, soft-clipping for SV split reads, ALT/decoy-aware mapping on GRCh38, -K determinism, and streaming straight to a sorted BAM. Use when mapping DNA short reads to a reference for variant calling, coverage, ChIP/ATAC (alongside bowtie2-alignment), or SV detection. RNA-seq spliced alignment is star-alignment/hisat2-alignment; BAM sort/dedup/stats, the QC gate, and the cross-tool MAPQ scale are alignment-files; read trimming is read-qc; counting reads over features is rna-quantification.
tool_type: cli
primary_tool: bwa-mem2
---

## Version Compatibility

Reference examples tested with: bwa-mem2 2.2.1+, bwa 0.7.17+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# BWA-MEM2 Alignment -- Read Groups, the Reference, and the Output Contract Decide Downstream Truth

**"Align my DNA reads"** -> Map reads to a reference with seed-and-extend, inject read groups, and stream to a sorted BAM -- because the aligner is the easy part: the reference analysis set, the @RG metadata, the -M/-Y output flags, and the dedup ordering are the decisions that silently determine whether variant calling works.
- CLI: `bwa-mem2 mem -t 8 -R '@RG\tID:s1\tSM:s1\tPL:ILLUMINA\tLB:lib1' ref.fa R1.fq.gz R2.fq.gz | samtools sort -@4 -o aligned.bam -`

Scope: DNA short-read mapping with bwa-mem2 (and original BWA-MEM / bwa-aln), the GRCh38 analysis-set choice (below), and the output contract it must satisfy for GATK/DeepVariant/SV callers. BAM sort/dedup/index/stats, the QC gate (flagstat/idxstats interpretation), and contig-naming reconciliation -> alignment-files. The cross-tool MAPQ scale -> alignment-files/sam-bam-basics. Read trimming/QC -> read-qc. Variant calling -> variant-calling. Structural-variant calling consumes the split reads produced here -> variant-calling/structural-variant-calling. OUT OF SCOPE: RNA (use star-alignment/hisat2-alignment), long reads (long-read-sequencing/long-read-alignment), bisulfite (methylation-analysis/bismark-alignment).

## The Single Most Important Modern Insight

1. **Read groups are a hard contract, not metadata decoration.** GATK (HaplotypeCaller/Mutect2/BQSR) and Picard refuse to run or behave wrongly without `@RG`. SM names the sample callers group by; ID is the BQSR error-model unit; PL sets the error model; LB is the unit MarkDuplicates dedups within (two reads at the same coordinate from different libraries are NOT duplicates). Inject them at mapping time with `-R`; adding them later (Picard AddOrReplaceReadGroups) is a full BAM rewrite. The catastrophic error is a clean-looking BAM that GATK rejects or mis-merges because SM/LB are missing.
2. **On GRCh38, ALT/decoy handling is a correctness decision and a blind +ALT mapping is actively worse than no ALT.** ALT contigs are alternate haplotypes of hyperpolymorphic loci (MHC/HLA); a read matches the primary copy AND the ALT copy, becomes a multimapper, and MAPQ collapses to 0 -- so variant callers drop it and HLA variants vanish. bwa-mem rescues this only if the `<idxbase>.alt` file is present (it then scores non-ALT hits against non-ALT hits only); adding ALT contigs to the FASTA WITHOUT the `.alt` imports the ambiguity and discards the fix. Use a decoy (hs38d1) always -- it absorbs reads from sequence missing from the primary assembly that would otherwise mismap and make recurrent false SNPs. The analysis-set layering is below.
3. **The -M/-Y flags and the dedup ordering are downstream contracts that fail silently.** `-M` marks split (chimeric) pieces as secondary (0x100) for legacy Picard -- but modern tools read supplementary (0x800) natively, and `-M` hides the split-read evidence SV callers need, so do NOT use it for SV work; use `-Y` (soft-clip supplementary) so every split piece keeps its full sequence. Duplicate marking has a strict order: `collate (name) -> fixmate -m -> sort (coordinate) -> markdup`; the `-m` adds the mate-score/MC tags markdup requires, fixmate needs mates adjacent, markdup needs coordinate order. Any other order silently produces wrong duplicate flags.

## What MAPQ Means Here (and what it does not)

bwa-mem MAPQ runs 0-60 and is an ordinal confidence rank derived from the gap between the best and second-best alignment score and the seed coverage -- it is NOT a calibrated `-10*log10 P(wrong)`. It clusters bimodally at 0 (a competing locus scores as well -> multimapper) and 60 (no competitor, good seed support); the middle is sparse. It models only repeat ambiguity, not contamination or heuristic error, so MAPQ 60 means "no competing locus found," not "P(wrong)=1e-6". A `-q 20` pre-filter drops most multimappers; rely on the caller's own MAPQ handling (GATK ignores MAPQ-0 and duplicates) rather than double-filtering aggressively. This scale is bwa-specific -- a `-q 60` "unique" filter empties a Bowtie2 (cap 42/44) or STAR (255=unique) BAM; see alignment-files/sam-bam-basics for the cross-tool scale.

## Tool Taxonomy

| Tool / subcommand | Citation | Mechanism / role | When |
|-------------------|----------|------------------|------|
| `bwa-mem2 mem` | Vasimuddin 2019 IEEE IPDPS 314-324 | architecture-aware reimplementation of BWA-MEM; near-identical output, ~1.5-3x faster, ~2x RAM, different index | the default DNA aligner today |
| `bwa mem` | Li 2013 arXiv:1303.3997 | SMEM seed + chain + banded affine SW; the reference implementation defining "correct" | when bwa-mem2 is unavailable or to match a legacy pipeline |
| `bwa aln` + `samse`/`sampe` | Li & Durbin 2009 Bioinformatics 25:1754 | bounded backtracking, no exact-seed requirement | ancient DNA / very short (<70 bp) damaged reads where the 19-mer seed fails |
| `bwa bwasw` | Li & Durbin 2010 Bioinformatics 26:589 | SW over BWT for long/divergent queries | legacy, superseded by mem; rarely used |
| DRAGEN / Parabricks fq2bam | -- | hardware-accelerated BWA-MEM (FPGA/GPU); concordant, not bit-identical | high-throughput production where a validated pipeline accepts the small delta |
| STAR / HISAT2 | -- | splice-aware (route OUT) | any RNA library -> star-alignment, hisat2-alignment |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Human WGS/WES germline or somatic | `bwa-mem2 mem` + GRCh38 + decoy (+ALT/postalt if HLA matters); add `-Y` | seed-and-extend standard; GATK/DeepVariant expect its soft-clipped, ALT-aware output |
| SV / split-read detection | `bwa-mem2 mem -Y` (no `-M`) | supplementary alignments with full soft-clipped sequence are the split-read signal |
| Reproducible / functional-equivalence pipeline | add `-K 100000000` (and `-Y`) | pins per-batch insert-size estimation so output is thread-count-invariant |
| ChIP-seq / CUT&RUN | bwa-mem2 or bowtie2 | both work; bowtie2 is the ENCODE peak-assay default -> bowtie2-alignment |
| ATAC-seq | bowtie2 (local/dovetail) | adapter read-through + short fragments favor local mode -> bowtie2-alignment |
| Ancient / very short damaged DNA | `bwa aln -l 1024 -n ~0.01-0.03 -o 2` + samse/sampe | mem's mandatory 19-mer seed fails on short damaged reads, biasing toward reference |
| Allele-specific (ASE / allelic binding) | bwa-mem2 then WASP-filter | reads carrying the alt allele align worse -> reference bias at het sites |
| RNA-seq | route OUT to star-alignment / hisat2-alignment | spliced reads need an N-CIGAR-capable aligner |

Default when uncertain: `bwa-mem2 mem` with read groups, streamed to a coordinate-sorted BAM, on a decoy-containing GRCh38 analysis set; add `-Y` for any pipeline that calls SVs.

## Build Index

```bash
bwa-mem2 index reference.fa
# emits reference.fa.0123 .amb .ann .bwt.2bit.64 .pac  (NOT interchangeable with `bwa index`'s .bwt/.sa)
```

For human DNA, obtain the decoy/ALT analysis set rather than a bare GRCh38: bwakit's `run-gen-ref hs38DH` downloads `hs38DH.fa` (primary + ALT + hs38d1 decoy + HLA) AND the `hs38DH.fa.alt` lift file, which must sit next to the index basename for ALT-aware mapping; the GATK/Broad resource bundle ships an equivalent decoy reference. Pick the layer by what the downstream caller can handle: no-alt + decoy (hs38) when the caller is not ALT-aware (the safe minimum), or full + decoy (hs38DH) with ALT-aware mapping plus `bwa-postalt.js` when MHC/HLA accuracy matters -- mismatching mapper-awareness to the analysis set silently degrades MHC/segdup accuracy. Use GRCh38 over GRCh37, and never mix builds across a cohort.

## Align with Read Groups, Stream to a Sorted BAM

```bash
bwa-mem2 mem -t 8 \
    -R '@RG\tID:sample1\tSM:sample1\tPL:ILLUMINA\tLB:lib1' \
    reference.fa reads_1.fq.gz reads_2.fq.gz | \
    samtools sort -@ 4 -o aligned.sorted.bam -
samtools index aligned.sorted.bam
# single-end: drop reads_2.fq.gz. The literal \t in -R must survive the shell (single quotes do this).
```

## Mark Duplicates (the strict ordering)

```bash
# collate -> fixmate -m -> sort -> markdup. -m adds the ms/MC tags markdup requires.
bwa-mem2 mem -t 8 -R '@RG\tID:s1\tSM:s1\tPL:ILLUMINA\tLB:lib1' reference.fa R1.fq.gz R2.fq.gz | \
    samtools collate -@ 4 -O -u - | \
    samtools fixmate -m -@ 4 -u - - | \
    samtools sort -@ 4 -u - | \
    samtools markdup -@ 4 - aligned.markdup.bam
samtools index aligned.markdup.bam
# NEVER run this on amplicon/multiplex-PCR data: identical primer-defined ends are by design, so
# markdup deletes almost all real coverage. Use UMIs (fgbio/UMI-tools) for PCR-dup removal there.
```

## SV / Split-Read Mapping

```bash
# -Y soft-clips supplementary alignments so every split piece keeps its full sequence (SA-tag chain).
# Do NOT add -M (it demotes split pieces to secondary and hides the SV evidence).
bwa-mem2 mem -t 8 -Y -R '@RG\tID:s1\tSM:s1\tPL:ILLUMINA' reference.fa R1.fq.gz R2.fq.gz | \
    samtools sort -@ 4 -o aligned.sv.bam -
```

## Reproducible Output Across Thread Counts

```bash
# Per-batch insert-size estimation makes default multithreaded output vary; -K pins the batch size.
bwa-mem2 mem -t 8 -K 100000000 -Y \
    -R '@RG\tID:s1\tSM:s1\tPL:ILLUMINA\tLB:lib1' \
    reference.fa R1.fq.gz R2.fq.gz | samtools sort -@ 4 -o aligned.bam -
```

## Ancient / Very Short Damaged DNA

```bash
# mem's 19-mer seed fails on short deaminated reads; bwa aln backtracks with no exact-seed requirement.
bwa index reference.fa
bwa aln -l 1024 -n 0.02 -o 2 -t 8 reference.fa reads.fq.gz > reads.sai
bwa samse reference.fa reads.sai reads.fq.gz | samtools sort -o ancient.bam -
# -l 1024 disables the seed (seed longer than the read); -n relaxes edit distance; -o 2 allows gaps.
# The -n value is benchmark-dependent (commonly ~0.01-0.03); treat as a tunable starting point.
```

## Key Parameters (verified against bwa/bwa-mem2 source defaults)

| Flag | Default | Effect |
|------|---------|--------|
| -t | 1 | threads |
| -k | 19 | min seed (SMEM) length; lower = more sensitive on short/divergent reads, slower; the reason aDNA defeats mem |
| -r | 1.5 | re-seed a MEM longer than k*1.5; lower = more sensitive, slower |
| -c | 500 | discard a seed occurring > N times (NOT 10000; the old sourceforge page is stale) |
| -A / -B / -O / -E | 1 / 4 / 6 / 1 | match / mismatch / gap-open / gap-extend; lower -B for divergent data, lower -O/-E to permit longer indels |
| -L | 5 | clip penalty; higher discourages soft-clipping (toward end-to-end) |
| -T | 30 | min alignment score to OUTPUT (below it the read is reported unmapped) |
| -M | off | mark split hits secondary (legacy Picard); harmful for SV -- prefer -Y |
| -Y | off | soft-clip supplementary alignments (keep full sequence for SV callers) |
| -K | auto | input bases per batch; fix it (e.g. 100000000) for thread-count-invariant output |
| -R | -- | the @RG header line (literal \t) |

## Per-Method Failure Modes

### Missing read groups
**Trigger:** mapping without `-R '@RG...'`. **Mechanism:** GATK groups reads by SM and models error by ID/LB. **Symptom:** GATK errors ("no read group"), or MarkDuplicates/BQSR misbehave; samples cannot be told apart. **Fix:** inject SM/ID/PL/LB at mapping time; Picard AddOrReplaceReadGroups is a rewrite if missed.

### GRCh38 + ALT without the .alt file
**Trigger:** ALT contigs in the FASTA but no `<idxbase>.alt`. **Mechanism:** ALT copies become ordinary contigs, so every MHC/HLA read multimaps and MAPQ collapses to 0. **Symptom:** a MAPQ-0 spike and missing variants in MHC/HLA. **Fix:** supply the `.alt` (alt-aware mapping) + `bwa-postalt.js`, or use a no-alt + decoy analysis set if not ALT-aware (see Build Index above).

### -M used in an SV pipeline
**Trigger:** `bwa-mem2 mem -M ...` then split-read SV calling. **Mechanism:** `-M` marks split pieces secondary (0x100), which SV callers and MarkDuplicates skip. **Symptom:** SV caller finds little split-read support. **Fix:** drop `-M`, add `-Y`, then dedup, then call -> variant-calling/structural-variant-calling.

### fixmate without -m, or wrong dedup order
**Trigger:** `samtools markdup` on a name-sorted BAM, or `fixmate` without `-m`. **Mechanism:** markdup needs coordinate order plus the ms/MC tags `-m` writes. **Symptom:** silently wrong duplicate flags; over- or under-marking. **Fix:** `collate -> fixmate -m -> sort -> markdup` -> alignment-files/duplicate-handling.

### Index built with the wrong tool
**Trigger:** pointing bwa-mem2 at a `bwa index` directory or vice versa. **Mechanism:** bwa-mem2 uses `.bwt.2bit.64`; bwa uses `.bwt`/`.sa`. **Symptom:** "fail to locate the index" / format error. **Fix:** rebuild with the matching tool (`bwa-mem2 index`).

### Reference bias at heterozygous sites
**Trigger:** allele-specific analysis (ASE, allelic ChIP/ATAC, low-VAF somatic) off a raw BAM. **Mechanism:** the alt-allele read carries an extra mismatch, sometimes failing the 19-mer seed -> reference allele over-counted. **Symptom:** false allelic imbalance toward reference; depressed alt-allele VAF. **Fix:** WASP-filter (re-map allele-swapped reads, keep only if placement is unchanged), N-mask, a personalized reference, or a SNP-graph/pangenome.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| min seed -k 19 | bwamem.c::mem_opt_init | sets the sensitivity floor; the reason short damaged aDNA reads fail mem |
| seed cap -c 500 | bwamem.c::mem_opt_init | above this a seed is uninformative and explodes extension; verified default (not 10000) |
| scoring -A1 -B4 -O6 -E1 | bwamem.c::mem_opt_init | the substitution-rate the scheme tolerates is ~0.75*exp(-log(4)*B/A) |
| min output score -T 30 | bwamem.c::mem_opt_init | reads scoring below 30 are reported unmapped |
| -K 100000000 for reproducibility | CCDG / functional-equivalence pipelines | pins per-batch insert-size estimation independent of thread count |
| bwa-mem2 human index/runtime RAM ~10 GB | bwa-mem2 README (approximate) | ~2x original bwa; plan node memory accordingly |
| GRCh38 + hs38d1 decoy for human WGS | GATK/CCDG guidance | decoy absorbs missing-assembly reads that otherwise make recurrent false variants |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "fail to locate the index" | bwa vs bwa-mem2 index mismatch | rebuild with the matching tool (`bwa-mem2 index`) |
| GATK "no read group" | missing `-R '@RG...'` | inject SM/ID/PL/LB at mapping time |
| Low mapping rate | wrong reference/species, un-trimmed adapter, contamination | confirm species with read-qc/contamination-screening; check the reference build; trim first -> read-qc; interpret stats -> alignment-files/bam-statistics |
| MAPQ-0 spike, missing HLA variants | GRCh38+ALT without `.alt`, or no decoy | use decoy + ALT-aware mapping/postalt, or no-alt+decoy (see Build Index) |
| Wrong/unstable BAM across runs | default per-batch insert estimation with multithreading | add `-K 100000000` and fix input order |
| Almost all reads marked duplicate | MarkDuplicates run on amplicon/PCR data | do not dedup amplicon; use UMIs -> read-qc/umi-processing, alignment-files/duplicate-handling |
| markdup mis-marks duplicates | name-sorted input or fixmate without `-m` | `collate -> fixmate -m -> sort -> markdup` |

## References

- Li H. 2013. Aligning sequence reads, clone sequences and assembly contigs with BWA-MEM. arXiv:1303.3997.
- Li H, Durbin R. 2009. Fast and accurate short read alignment with Burrows-Wheeler transform. *Bioinformatics* 25:1754-1760.
- Li H, Durbin R. 2010. Fast and accurate long-read alignment with Burrows-Wheeler transform. *Bioinformatics* 26:589-595.
- Vasimuddin M, Misra S, Li H, Aluru S. 2019. Efficient architecture-aware acceleration of BWA-MEM for multicore systems. *IEEE IPDPS* 2019:314-324.
- Li H, Handsaker B, Wysoker A, et al. 2009. The Sequence Alignment/Map format and SAMtools. *Bioinformatics* 25:2078-2079.
- van de Geijn B, McVicker G, Gilad Y, Pritchard JK. 2015. WASP: allele-specific software for robust molecular quantitative trait locus discovery. *Nat Methods* 12:1061-1063.

## Related Skills

- bowtie2-alignment - ChIP/ATAC DNA mapping with end-to-end vs local modes
- star-alignment - RNA splice-aware alignment (when reads cross junctions)
- read-qc/fastp-workflow - Trim and QC reads before alignment
- read-qc/umi-processing - UMI extraction/dedup for amplicon and low-input libraries (do not coordinate-dedup amplicon)
- alignment-files/duplicate-handling - Mark/remove duplicates; UMI-aware dedup
- alignment-files/sam-bam-basics - SAM flags, CIGAR, the cross-tool MAPQ scale, SA tags
- alignment-files/bam-statistics - flagstat/idxstats/stats QC gate; what a high mapping rate hides
- variant-calling/variant-calling - Call variants from the aligned BAM
- variant-calling/structural-variant-calling - SV calling from split/discordant reads (needs -Y)
<!-- END FILE: read-alignment/bwa-alignment/SKILL.md -->

## 子目录：read-alignment/hisat2-alignment

<!-- BEGIN FILE: read-alignment/hisat2-alignment/SKILL.md -->
---
name: bio-read-alignment-hisat2-alignment
description: Aligns RNA-seq reads to a genome with HISAT2, the splice-aware aligner whose hierarchical graph FM-index runs at roughly a quarter of STAR's memory (~7 GB for human), whose SNP/haplotype graph index reduces reference bias in the index itself, and whose MAPQ is GATK-friendly (60 for unique, no 255 problem). Use when RNA alignment must fit a memory-constrained machine, when feeding StringTie/Cufflinks transcript assembly via --dta, or when a SNP-aware graph index is wanted for allele-robust mapping. Feature-rich/high-RAM RNA alignment and fusion detection are star-alignment; DE on known transcripts only should skip alignment for rna-quantification/alignment-free-quant; the QC gate and contig-naming reconciliation are alignment-files; counting is rna-quantification.
tool_type: cli
primary_tool: HISAT2
---

## Version Compatibility

Reference examples tested with: hisat2 2.2+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# HISAT2 Alignment -- Graph-Indexed Spliced Mapping at a Quarter of STAR's Memory

**"Align my RNA-seq reads with low memory"** -> Map reads across exon-exon junctions with a hierarchical graph FM-index that fits a small machine -- because HISAT2 buys splice-aware alignment at ~7 GB instead of STAR's ~30 GB, its MAPQ is GATK-friendly, and its SNP-graph index can remove reference bias before a single read is mapped.
- CLI: `hisat2 -p 8 -x index -1 R1.fq.gz -2 R2.fq.gz | samtools sort -@4 -o aligned.bam -`

Scope: low-memory RNA splice-aware mapping with HISAT2 -- index building (plain / annotation-aware / SNP-graph), strandedness, the --dta transcript-assembly mode, and manual two-pass. Contig naming and the QC gate -> alignment-files. Feature-rich/high-RAM RNA alignment, native gene counts, and fusion detection -> star-alignment. Counting reads over genes -> rna-quantification. DE without a BAM -> rna-quantification/alignment-free-quant. OUT OF SCOPE: DNA (bwa-alignment/bowtie2-alignment), long reads (long-read-sequencing/long-read-alignment), HLA typing (HISAT-genotype, a separate tool).

## The Single Most Important Modern Insight

1. **The hierarchical graph FM-index is why HISAT2 exists: near-STAR spliced alignment at ~1/4 the RAM.** HISAT2 uses one global FM-index to anchor a read plus ~55,000 small local graph FM-indexes (each ~56 kb), and extends a spliced read within the relevant local index rather than stitching genome-wide as STAR does. Most introns fit inside one local window, so spliced extension is a cheap local operation -- the resident human index is ~4-7 GB vs STAR's ~30 GB. That memory win is the reason to choose HISAT2; the cost is slightly lower novel-junction sensitivity than STAR two-pass and no native gene counts or fusion output.
2. **The SNP/haplotype graph index removes reference bias in the index, and the MAPQ is GATK-friendly.** A `hisat2-build --snp --haplotype` (or the prebuilt `grch38_snp` index) encodes millions of known variants as alternate graph nodes, so a read carrying a known alt allele traverses the alt node with no mismatch penalty -- the bias that over-counts the reference allele is removed structurally, for all those sites at once, without a per-sample personalized reference. (Private/novel variants still cause bias, so rigorous ASE still needs WASP or a personalized reference.) HISAT2 also assigns unique reads MAPQ 60 (not STAR's 255), so its output goes into GATK without the reassignment STAR needs.
3. **--dta is for transcript assembly only, and using it for plain counting throws away reads.** `--dta` raises the minimum anchor length required to report a de-novo spliced alignment, deliberately suppressing short-anchor junction reads -- because StringTie/Cufflinks cannot reliably assemble a transcript from a 3-5 bp anchor and such reads produce spurious isoforms. That trades junction sensitivity for assembly cleanliness, so `--dta` belongs only in a transcript-assembly pipeline; for plain gene counting it just discards usable junction reads. Strandedness (`--rna-strandness RF` for the common dUTP/TruSeq case) must also be set, or sense reads land in "no feature" and counts roughly halve.

## How HISAT2 Splices (the mechanism in brief)

A read is seeded by the global FM-index, then the relevant ~56 kb local FM-index is selected and the read is extended across the junction within it: the unaligned remainder is anchored in the local index and extended by repeated FM-index extension. Because the spliced extension is a narrow, local operation rather than a genome-wide seed-cluster-stitch, HISAT2 needs far less RAM than STAR -- and evaluates a narrower set of candidate splice configurations, which is the source of both its speed/memory advantage and its slightly lower novel-junction sensitivity.

## Tool Taxonomy

| Mode / index | Citation | Mechanism / role | When |
|--------------|----------|------------------|------|
| `hisat2-build` (plain) | Kim 2019 Nat Biotechnol 37:907 | genome-only HGFM | quick index; junctions supplied at align time |
| `hisat2-build --ss --exon` | Kim 2019 | annotation-aware HGFM (better short-anchor placement) | when build RAM allows; or use prebuilt `*_tran` indexes |
| `hisat2-build --snp --haplotype` | Kim 2019 | SNP/haplotype graph (reference-bias reduction) | allele-robust mapping; the `grch38_snp` index |
| `hisat2` alignReads | Kim 2019 | spliced alignment via local FM-index extension | the default RNA-to-genome mapping |
| `--dta` / `--dta-cufflinks` | HISAT2 manual | longer-anchor reporting for assemblers | StringTie / Cufflinks transcript assembly ONLY |
| manual two-pass (`--novel-splicesite-*`) | HISAT2 manual | discover then reuse novel junctions | novel-junction sensitivity (cohort: merge across samples) |
| STAR | Dobin 2013 Bioinformatics 29:15 | higher RAM, native counts, fusions, 2-pass | feature-rich RNA (route OUT) -> star-alignment |
| Salmon / kallisto | Patro 2017 Nat Methods 14:417 | alignment-free quantification | DE on known transcripts only (route OUT) -> rna-quantification/alignment-free-quant |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| RNA-seq on a memory-constrained machine (<32 GB) | HISAT2 | ~7 GB graph index vs STAR's ~30 GB |
| StringTie/Cufflinks transcript assembly | HISAT2 `--dta` | longer-anchor reporting the assemblers need |
| Allele-robust mapping / known-variant-aware | HISAT2 SNP-graph index (`grch38_snp`) | alt-allele reads traverse graph nodes without penalty |
| RNA variant calling | HISAT2 (MAPQ 60) then GATK SplitNCigarReads | GATK-friendly MAPQ, no 255 reassignment |
| Need native gene counts, fusions, or top novel-junction sensitivity | route OUT to star-alignment | HISAT2 has no GeneCounts/chimeric output |
| DE on known transcripts only | route OUT to rna-quantification/alignment-free-quant | Salmon/kallisto are faster and model multimapping |
| Plain gene-level counting | HISAT2 without `--dta` | `--dta` discards short-anchor junction reads |

Default when uncertain: HISAT2 with `--rna-strandness RF` (verify the strand), streamed to a coordinate-sorted BAM; add `--dta` only for transcript assembly.

## Build Index

```bash
# Plain genome-only index (cheap; supply junctions at align time with --known-splicesite-infile).
hisat2-build -p 8 reference.fa hisat2_index

# Annotation-aware (better short-anchor placement). NOTE: a full human --ss --exon build needs a LOT of RAM;
# prefer the prebuilt grch38_tran / grch38_snp_tran indexes, or pass junctions at align time instead.
hisat2_extract_splice_sites.py annotation.gtf > splice_sites.txt
hisat2_extract_exons.py        annotation.gtf > exons.txt
hisat2-build -p 8 --ss splice_sites.txt --exon exons.txt reference.fa hisat2_index
```

## Basic Alignment with Strandedness

```bash
# RF = reverse-stranded (dUTP / Illumina TruSeq Stranded mRNA -- the common case). Verify, do not assume.
hisat2 -p 8 -x hisat2_index --rna-strandness RF \
    --rg-id sample1 --rg SM:sample1 --rg PL:ILLUMINA \
    -1 reads_1.fq.gz -2 reads_2.fq.gz \
    --new-summary --summary-file sample.summary.txt | \
    samtools sort -@ 4 -o aligned.sorted.bam -
samtools index aligned.sorted.bam
# Single-end stranded: --rna-strandness R (reverse) or F (forward). Unstranded: omit the flag.
```

## For StringTie / Cufflinks (transcript assembly)

```bash
# --dta reports longer anchors the assemblers need; use ONLY for assembly, not for plain counting.
hisat2 -p 8 -x hisat2_index --rna-strandness RF --dta \
    -1 r1.fq.gz -2 r2.fq.gz | samtools sort -@ 4 -o aligned.bam -
```

## Manual Two-Pass (cohort novel-junction discovery)

```bash
# Pass 1: discover novel junctions per sample.
for r1 in *_R1.fq.gz; do
    base=$(basename "$r1" _R1.fq.gz); r2=${r1/_R1/_R2}
    hisat2 -p 8 -x hisat2_index --novel-splicesite-outfile "${base}.novel.txt" \
        -1 "$r1" -2 "$r2" -S /dev/null
done
# Merge across the cohort so every sample sees the same junction set (avoids a per-sample junction batch effect).
cat *.novel.txt | sort -u > cohort.novel.txt
# Pass 2: re-align every sample with the shared novel-junction set.
for r1 in *_R1.fq.gz; do
    base=$(basename "$r1" _R1.fq.gz); r2=${r1/_R1/_R2}
    hisat2 -p 8 -x hisat2_index --rna-strandness RF --novel-splicesite-infile cohort.novel.txt \
        -1 "$r1" -2 "$r2" | samtools sort -@ 4 -o "${base}.bam" -
done
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| -x | -- | index BASENAME |
| -1 / -2 / -U | -- | paired / single-end reads |
| --rna-strandness | unstranded | FR / RF / F / R (dUTP/TruSeq = RF / R) |
| --dta / --dta-cufflinks | off | longer anchors for StringTie / Cufflinks (assembly only) |
| --known-splicesite-infile | -- | supply junctions at align time (cheap-index alternative to --ss build) |
| --novel-splicesite-outfile / -infile | -- | manual two-pass |
| --max-intronlen | 500000 | shorter than STAR's effective ~1 Mb; raise for long-intron genes |
| -k | 5 (HFM) / 10 (HGFM) | max alignments reported per read |
| --no-softclip / --no-spliced-alignment | off | force end-to-end / disable splicing (DNA mode) |

## Per-Method Failure Modes

### --dta used for plain counting
**Trigger:** `--dta` on a run whose downstream is featureCounts/htseq, not StringTie. **Mechanism:** `--dta` suppresses short-anchor junction reads. **Symptom:** lower junction-read recovery and counts than a non-dta run. **Fix:** drop `--dta` for counting; keep it only for transcript assembly.

### Wrong strandedness
**Trigger:** omitting or mis-setting `--rna-strandness`. **Mechanism:** the XS strand tag is mislabeled and sense reads are assigned to "no feature." **Symptom:** counts ~halved; StringTie builds transcripts on the wrong strand. **Fix:** infer strand (RSeQC infer_experiment.py, or STAR GeneCounts) and set RF for dUTP/TruSeq.

### --ss --exon human build runs out of RAM
**Trigger:** a full human annotation-aware build on a small machine. **Mechanism:** building the annotation-aware HGFM needs far more RAM than a plain build. **Symptom:** the build is killed (OOM). **Fix:** use a prebuilt `grch38_tran`/`grch38_snp_tran` index, or build plain and pass junctions at align time via `--known-splicesite-infile`.

### max-intronlen too small for long-intron genes
**Trigger:** the default `--max-intronlen 500000` on genes with introns near or above ~1 Mb. **Mechanism:** junctions longer than the cap are not formed. **Symptom:** long-gene junction reads soft-clipped or mismapped. **Fix:** raise `--max-intronlen` for organisms/genes with very long introns.

### Genome/GTF contig-naming mismatch
**Trigger:** the BAM uses `chr1`/`chrM` but the counting GTF uses `1`/`MT`. **Mechanism:** no overlapping features. **Symptom:** zero counts despite a high alignment rate. **Fix:** reconcile naming (same source/release) -> alignment-files.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| HISAT2 human graph index RAM ~4.3 GB plain / ~6.7 GB SNP | Kim 2019 (approximate) | the ~1/4-of-STAR footprint that motivates choosing HISAT2 |
| --max-intronlen 500000 default | HISAT2 manual | shorter than STAR's ~1 Mb; raise for long-intron genes |
| --rna-strandness RF for dUTP/TruSeq | library-prep chemistry | the overwhelmingly common stranded protocol |
| unique-read MAPQ 60 (since v2.0.4) | HISAT2 manual / changelog | GATK-friendly; no 255 reassignment needed |
| -k 5 (HFM) / 10 (HGFM) | HISAT2 manual | max reported alignments differs by index type |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Counts ~halved, wrong-strand transcripts | missing/incorrect `--rna-strandness` | infer strand; set RF for dUTP/TruSeq |
| Lower counts than expected | `--dta` used for plain counting | drop `--dta` unless assembling transcripts |
| `--ss --exon` build killed (OOM) | full human annotation-aware build | use a prebuilt index or `--known-splicesite-infile` at align time |
| Long-gene junction reads clipped | `--max-intronlen` too small | raise it for long-intron genes |
| 0 counts despite high alignment rate | genome/GTF contig-naming mismatch | reconcile `chr1` vs `1` (same source/release) -> alignment-files |
| "Could not locate a HISAT2 index" | `-x` given a `.ht2` file | pass the index basename |
| htseq-count miscounts HISAT2 output | htseq wants name-sorted input | pipe to `samtools sort -n` for htseq; featureCounts accepts coordinate order |

## References

- Kim D, Paggi JM, Park C, Bennett C, Salzberg SL. 2019. Graph-based genome alignment and genotyping with HISAT2 and HISAT-genotype. *Nat Biotechnol* 37:907-915.
- Kim D, Langmead B, Salzberg SL. 2015. HISAT: a fast spliced aligner with low memory requirements. *Nat Methods* 12:357-360.
- Dobin A, Davis CA, Schlesinger F, et al. 2013. STAR: ultrafast universal RNA-seq aligner. *Bioinformatics* 29:15-21.
- Patro R, Duggal G, Love MI, Irizarry RA, Kingsford C. 2017. Salmon provides fast and bias-aware quantification of transcript expression. *Nat Methods* 14:417-419.

## Related Skills

- star-alignment - Feature-rich, higher-RAM splice-aware alternative (native counts, fusions)
- bwa-alignment - DNA short-read mapping (when reads do not cross junctions)
- read-qc/rnaseq-qc - RNA destination metrics: rRNA, gene-body coverage, strandedness
- read-qc/fastp-workflow - Trim adapters/poly-A before alignment
- alignment-files/bam-statistics - flagstat/idxstats QC gate; what a high mapping rate hides; contig naming
- rna-quantification/featurecounts-counting - Count aligned reads over genes
- rna-quantification/alignment-free-quant - Salmon/kallisto when only known-transcript DE is needed
- differential-expression/deseq2-basics - Downstream DE from the count matrix
<!-- END FILE: read-alignment/hisat2-alignment/SKILL.md -->

## 子目录：read-alignment/star-alignment

<!-- BEGIN FILE: read-alignment/star-alignment/SKILL.md -->
---
name: bio-read-alignment-star-alignment
description: Aligns RNA-seq reads to a genome with STAR, the fast splice-aware aligner whose splice-junction database (built from a GTF at sjdbOverhang = readlength-1) and two-pass mode set junction sensitivity, whose 255-for-unique MAPQ breaks GATK, and whose GeneCounts output reveals library strandedness. Use when RNA reads must be placed on the genome for novel-isoform discovery, fusion detection, RNA variant calling, coverage tracks, splicing QC, or single-cell (STARsolo). Memory-constrained RNA alignment is hisat2-alignment; DE on known transcripts only should skip alignment for rna-quantification/alignment-free-quant; the QC gate and contig-naming reconciliation are alignment-files; counting is rna-quantification; DNA is bwa-alignment/bowtie2-alignment.
tool_type: cli
primary_tool: STAR
---

## Version Compatibility

Reference examples tested with: STAR 2.7.11+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# STAR RNA-seq Alignment -- The Junction Database, the 255 MAPQ, and the Strand Column Decide the Result

**"Align my RNA-seq reads"** -> Map reads across exon-exon junctions to the genome, building or reusing a splice-aware index from a GTF -- because an RNA read spans introns the genome does not contain, so the junction database (and its sjdbOverhang), the two-pass choice, the 255-unique MAPQ, and the strand column STAR reports are what actually determine the downstream counts and variant calls.
- CLI: `STAR --runMode alignReads --genomeDir idx/ --readFilesIn R1.fq.gz R2.fq.gz --readFilesCommand zcat --outSAMtype BAM SortedByCoordinate`

Scope: RNA splice-aware mapping with STAR -- index generation, two-pass, GeneCounts, chimeric/fusion output, and the MAPQ/strandedness traps. Contig-naming reconciliation and the QC gate -> alignment-files. Low-memory RNA alignment -> hisat2-alignment. Counting reads over genes/transcripts -> rna-quantification. Single-cell droplet/plate counting (STARsolo) -> single-cell. DE on known transcripts without a BAM -> rna-quantification/alignment-free-quant. OUT OF SCOPE: DNA (bwa-alignment/bowtie2-alignment), long reads (long-read-sequencing/long-read-alignment).

## The Single Most Important Modern Insight

1. **The splice-junction database is part of the index/run config, and a wrong sjdbOverhang or per-sample two-pass silently changes the answer.** STAR builds short artificial junction-flank sequences from the GTF so reads with a short overhang on one exon can still be placed; `--sjdbOverhang` sets the flank length and should equal `max(readlength) - 1` (default 100 is fine near 100 bp reads but degrades junction sensitivity for very short reads). Two-pass (`--twopassMode Basic`) discovers novel junctions and re-aligns, raising novel-junction sensitivity -- but it is PER-SAMPLE: each sample is re-aligned against its own augmented index, so a junction found only in the deep/disease sample is rescued asymmetrically, a batch effect that confounds junction/splicing/sQTL comparisons. The cohort-correct recipe is to pool every sample's pass-1 `SJ.out.tab`, filter, and feed one common `--sjdbFileChrStartEnd` to a uniform second pass. Per-sample two-pass is fine for plain gene-level DE; it bites splicing analyses.
2. **STAR's MAPQ is 255-for-unique and a multiplicity code, so it breaks GATK and a copied MAPQ filter deletes every multimapper.** Unique reads get MAPQ 255 -- the SAM "mapping quality unavailable" value -- which GATK treats as missing and drops, the classic silently-empty RNA VCF; fix it at align time with `--outSAMmapqUnique 60`. Multimappers get 3 / 1 / 0 for 2 / 3-4 / >=5 loci (pure locus count, no score information), so a generic `samtools view -q 10` or `featureCounts -Q 10` copied from a DNA pipeline DELETES every multimapper while keeping every unique -- a directional "discard paralog/gene-family/rRNA/pseudogene reads" filter that biases against recently-duplicated gene families. A hard MAPQ filter is almost never what an RNA analysis wants.
3. **STAR reports library strandedness for free in GeneCounts, and getting strand wrong roughly halves counts.** `--quantMode GeneCounts` emits a 4-column `ReadsPerGene.out.tab`: gene, unstranded, forward, reverse. Summing columns 3 and 4 reveals the protocol -- roughly equal is unstranded (use col 2), col 3 dominant is forward, col 4 dominant is reverse (the common dUTP/TruSeq case, use col 4). Never assume the strand: feeding the wrong column (or the wrong `-s` to a counter) sends sense reads to "no feature" and roughly halves the counts, distorting DE.

## How STAR Places a Splice (the mechanism in brief)

STAR seeds with Maximal Mappable Prefix search on an uncompressed suffix array: it finds the longest exact prefix, and when that prefix ends (at a junction, mismatch, or read end) it restarts from the next base -- so a junction-spanning read naturally decomposes into seeds on two exons that STAR then stitches across the intron with an `N` (skipped-region) CIGAR. The stitch is scored with splice priors that penalize non-canonical motifs (`--scoreGapNoncan -8`), long introns (`--scoreGenomicLengthLog2scale -0.25`), and reward annotated junctions (`--sjdbScore 2`), plus a hard anchor floor (`--alignSJoverhangMin`): a novel junction on a tiny anchor carries almost no information, so it must clear both the soft score prior and the hard overhang minimum. This is why annotation (the sjdb) and two-pass matter for short-overhang and novel junctions.

## Tool Taxonomy

| Mode / output | Citation | Mechanism / role | When |
|---------------|----------|------------------|------|
| `STAR --runMode alignReads` | Dobin 2013 Bioinformatics 29:15 | MMP seed + stitch; spliced genomic BAM | the default RNA-to-genome alignment |
| `--twopassMode Basic` | Dobin 2013 (STAR manual) | discover novel junctions, re-align | novel-isoform / variant / splicing work (per-sample); pool for cohorts |
| `--quantMode GeneCounts` | STAR manual | per-gene counts + the strand-detection 3 columns | quick counts and strandedness inference |
| `--quantMode TranscriptomeSAM` | STAR manual | transcriptome-coord BAM for RSEM / Salmon-aln | isoform-level EM quantification -> rna-quantification |
| `--chimSegmentMin` -> Chimeric.out.junction | STAR manual | split-across-loci reads for fusion calling | STAR-Fusion / Arriba fusion detection |
| STARsolo (`--soloType`) | STAR manual | cell-barcode + UMI single-cell counting | scRNA-seq (route OUT) -> single-cell |
| HISAT2 | Kim 2019 Nat Biotechnol 37:907 | graph FM-index, ~1/4 the RAM | memory-constrained RNA (route OUT) -> hisat2-alignment |
| Salmon / kallisto | Patro 2017 Nat Methods 14:417 | alignment-free transcript quantification | DE on known transcripts only (route OUT) -> rna-quantification/alignment-free-quant |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| RNA-seq, ample RAM (>=32 GB), need a genomic BAM | STAR | fastest splice-aware aligner; native counts, fusions, 2-pass |
| RNA variant calling | STAR 2-pass + `--outSAMmapqUnique 60` then GATK SplitNCigarReads | 2-pass splices novel junctions; 60 avoids the 255 drop |
| Novel-isoform / splicing / sQTL across a cohort | cohort 2-pass (pool SJ.out.tab -> common `--sjdbFileChrStartEnd`) | per-sample 2-pass is a junction batch effect |
| Fusion detection | `--chimSegmentMin 12 --chimOutType ...` -> STAR-Fusion / Arriba | chimeric junctions are the fusion signal |
| Single-cell RNA | STARsolo (route OUT) | barcode+UMI counting -> single-cell |
| Memory-constrained (<32 GB) | route OUT to hisat2-alignment | STAR needs ~30 GB for human |
| DE on known transcripts only | route OUT to rna-quantification/alignment-free-quant | Salmon/kallisto are faster and model multimapping better |
| Small genome (bacterial/viral/plasmid) | STAR with reduced `--genomeSAindexNbases` | the default 14 silently builds a bad index / segfaults |

Default when uncertain: STAR with `--outSAMtype BAM SortedByCoordinate`, `--quantMode GeneCounts` (to also read strandedness), and `--twopassMode Basic` for per-sample novel-junction work; set `--outSAMmapqUnique 60` for any STAR -> GATK path.

## Generate the Genome Index

```bash
# sjdbOverhang = max(readlength) - 1 (149 for 2x150 reads). Default 100 degrades junctions for short reads.
STAR --runMode genomeGenerate --runThreadN 8 \
    --genomeDir star_index/ \
    --genomeFastaFiles genome.fa \
    --sjdbGTFfile annotation.gtf \
    --sjdbOverhang 149
# Small genome (e.g. 5 Mb): add --genomeSAindexNbases <= min(14, log2(GenomeLength)/2 - 1), or STAR segfaults.
```

## Basic Alignment

```bash
STAR --runThreadN 8 \
    --genomeDir star_index/ \
    --readFilesIn reads_1.fq.gz reads_2.fq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix sample_ \
    --outSAMtype BAM SortedByCoordinate
samtools index sample_Aligned.sortedByCoord.out.bam
# STAR already coordinate-sorts -- a subsequent `samtools sort` is redundant. Single-end: one file in --readFilesIn.
```

## Two-Pass + Gene Counts + Strandedness

```bash
STAR --runThreadN 8 --genomeDir star_index/ \
    --readFilesIn r1.fq.gz r2.fq.gz --readFilesCommand zcat \
    --outFileNamePrefix sample_ \
    --outSAMtype BAM SortedByCoordinate \
    --twopassMode Basic \
    --quantMode GeneCounts \
    --outSAMattrRGline ID:sample1 SM:sample1 PL:ILLUMINA LB:lib1 \
    --outSAMmapqUnique 60        # so a downstream GATK RNA-variant step does not drop the 255 uniques
# STAR read groups use --outSAMattrRGline (SPACE-separated tags), NOT bwa's tab-delimited -R '@RG\t...'.
# GATK requires read groups; comma-with-spaces separates groups for multiple --readFilesIn files.

# Detect strandedness from ReadsPerGene.out.tab (skip the 4 N_* summary rows, sum cols 3 vs 4):
awk 'NR>4 {f+=$3; r+=$4} END {printf "fwd(col3)=%d  rev(col4)=%d -> use col %s\n", f, r, (f>2*r?"3 fwd": r>2*f?"4 rev":"2 unstranded")}' sample_ReadsPerGene.out.tab
```

## ENCODE Long-RNA-seq Parameter Set

```bash
STAR --runThreadN 8 --genomeDir star_index/ --readFilesIn r1.fq.gz r2.fq.gz --readFilesCommand zcat \
    --outFileNamePrefix sample_ --outSAMtype BAM SortedByCoordinate \
    --outFilterType BySJout \
    --outFilterMultimapNmax 20 \
    --outFilterMismatchNmax 999 --outFilterMismatchNoverReadLmax 0.04 \
    --alignIntronMin 20 --alignIntronMax 1000000 --alignMatesGapMax 1000000 \
    --alignSJoverhangMin 8 --alignSJDBoverhangMin 1 \
    --sjdbScore 1 --outSAMattributes NH HI AS NM MD
# BySJout keeps only reads whose junctions passed the dataset-wide collapse; multimapNmax 20 retains real
# multi-locus genes; the 0.04 mismatch ratio scales with read length; intron caps at ~1 Mb cover human genes.
```

## Fusion Detection

```bash
# Chimeric junctions for STAR-Fusion (params per the STAR-Fusion wiki).
STAR --runThreadN 8 --genomeDir star_index/ --readFilesIn r1.fq.gz r2.fq.gz --readFilesCommand zcat \
    --outFileNamePrefix sample_ --outSAMtype BAM SortedByCoordinate \
    --chimSegmentMin 12 --chimJunctionOverhangMin 12 --chimOutJunctionFormat 1 \
    --chimOutType Junctions
# Arriba instead reads chimeric alignments from the BAM: --chimSegmentMin 10 --chimOutType WithinBAM SoftClip.
```

## Key Parameters (STAR defaults unless noted)

| Parameter | Default | Description |
|-----------|---------|-------------|
| --sjdbOverhang | 100 | junction-flank length at index build; set to readlength-1 |
| --twopassMode | None | `Basic` for per-sample novel-junction discovery |
| --outSAMmapqUnique | 255 | MAPQ for unique reads; set 60 for GATK |
| --outFilterMultimapNmax | 10 | max loci to report (ENCODE uses 20 for RNA) |
| --alignIntronMin / Max | 21 / 0 (auto) | gap < min is a deletion; cap Max ~1 Mb for human |
| --alignSJoverhangMin / SJDBoverhangMin | 5 / 3 | novel / annotated junction anchor floor (ENCODE 8 / 1) |
| --quantMode | -- | `GeneCounts` and/or `TranscriptomeSAM` |
| --chimSegmentMin | 0 (off) | turn on chimeric/fusion detection |
| --genomeSAindexNbases | 14 | reduce to min(14, log2(L)/2-1) for small genomes |
| --genomeLoad / --limitBAMsortRAM | NoSharedMemory / -- | shared-memory reuse; explicit sort RAM |

## Per-Method Failure Modes

### STAR 255 MAPQ into GATK
**Trigger:** STAR BAM (uniques at 255) fed to GATK RNA variant calling. **Mechanism:** GATK reads 255 as "MAPQ unavailable" and drops the read. **Symptom:** a silently empty or near-empty RNA VCF. **Fix:** `--outSAMmapqUnique 60` at align time (then SplitNCigarReads in the GATK RNA workflow).

### MAPQ filter deletes every multimapper
**Trigger:** a `-q 10` / `-Q 10` MAPQ filter (copied from DNA) on STAR output. **Mechanism:** STAR multimappers are MAPQ <= 3, uniques 255, so the filter keeps only uniques. **Symptom:** systematic under-counting of paralog/gene-family/rRNA/pseudogene loci; DE driven by multimapper fraction. **Fix:** do not MAPQ-filter RNA for counting; handle multimappers in the counter (NH-aware) or via EM -> rna-quantification/featurecounts-counting.

### Per-sample two-pass as a batch effect
**Trigger:** `--twopassMode Basic` per sample for a splicing/junction comparison. **Mechanism:** each sample is aligned against its own novel-junction-augmented index. **Symptom:** junction recovery correlates with depth/condition, confounding sQTL/differential splicing. **Fix:** pool pass-1 SJ.out.tab across the cohort, filter, feed one `--sjdbFileChrStartEnd` to a uniform second pass.

### sjdbOverhang mismatched to read length
**Trigger:** index built with default 100 for 36-50 bp reads, or a mismatch between index build and align values. **Mechanism:** junction flanks far longer than the reads degrade short-overhang sensitivity; a mismatch errors at align time. **Symptom:** reduced novel-junction-spanning sensitivity, or "present sjdbOverhang not equal to genome generation step." **Fix:** rebuild with `sjdbOverhang = max(readlength)-1`.

### Small genome with default SAindexNbases
**Trigger:** indexing a bacterial/viral/plasmid genome with `--genomeSAindexNbases 14`. **Mechanism:** the SA pre-index string is too long for the genome. **Symptom:** STAR silently builds a bad index or segfaults at align time. **Fix:** set `--genomeSAindexNbases min(14, log2(GenomeLength)/2 - 1)` (1 Mb -> 9, 100 kb -> 7).

### Index built with a different STAR version
**Trigger:** an index built months ago loaded by a bumped STAR module. **Mechanism:** STAR refuses an index whose versionGenome differs. **Symptom:** "Genome version is INCOMPATIBLE with running STAR version," or a subtly different version that loads and behaves differently across a cohort. **Fix:** rebuild the index with the exact aligning STAR version; pin the version for the whole cohort.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| sjdbOverhang = max(readlength) - 1 | STAR manual | sets the junction-flank length for short-overhang reads |
| --outSAMmapqUnique 60 for GATK | STAR manual / GATK RNA best practice | 255 is "unavailable" and is dropped by GATK |
| --outFilterMultimapNmax 20, --outFilterMismatchNoverReadLmax 0.04 | ENCODE long-RNA-seq pipeline | retains real multi-locus genes; mismatch budget scales with read length |
| --genomeSAindexNbases <= min(14, log2(L)/2 - 1) | STAR manual | the default 14 corrupts/segfaults small-genome indexes |
| STAR human-genome index RAM ~30 GB | STAR docs (approximate) | the reason to route memory-constrained jobs to HISAT2 |
| --chimSegmentMin 12 (STAR-Fusion) | STAR-Fusion wiki | minimum chimeric-segment length for fusion calling |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Empty / tiny RNA VCF after GATK | STAR 255 MAPQ dropped as "unavailable" | `--outSAMmapqUnique 60` (and SplitNCigarReads) |
| GATK "no read group" on a STAR BAM | STAR omits @RG unless asked | add `--outSAMattrRGline ID:.. SM:.. PL:ILLUMINA LB:..` (space-separated, not bwa's `-R`) |
| htseq-count silently miscounts STAR output | htseq wants name-sorted (or `-r pos`) input; STAR coordinate-sorts | emit `--outSAMtype BAM Unsorted` for htseq, or `samtools sort -n`; featureCounts accepts either |
| Counts ~halved, antisense artifacts | wrong strandedness column / `-s` | infer from GeneCounts cols 3 vs 4 (or RSeQC); TruSeq/dUTP = reverse |
| Paralog/gene-family genes under-counted | a `-q 10` MAPQ filter deleted multimappers | drop the MAPQ filter; handle NH>1 in the counter -> rna-quantification |
| "not enough memory for BAM sorting" | `--limitBAMsortRAM` too small | set it explicitly (e.g. 10000000000) |
| Segfault / bad index on a small genome | `--genomeSAindexNbases 14` | reduce per min(14, log2(L)/2 - 1) |
| "Genome version INCOMPATIBLE" | index built with another STAR version | rebuild with the running version; pin it |
| 0 counts despite high mapping rate | genome/GTF contig-naming mismatch | reconcile `chr1` vs `1`, `chrM` vs `MT` (same source/release) -> alignment-files |
| STAR reads `.gz` FASTQ as garbage / fails | STAR does not auto-detect gzip | add `--readFilesCommand zcat` (bwa/bowtie2/HISAT2 auto-detect gzip) |

## References

- Dobin A, Davis CA, Schlesinger F, et al. 2013. STAR: ultrafast universal RNA-seq aligner. *Bioinformatics* 29:15-21.
- Kim D, Paggi JM, Park C, Bennett C, Salzberg SL. 2019. Graph-based genome alignment and genotyping with HISAT2 and HISAT-genotype. *Nat Biotechnol* 37:907-915.
- Patro R, Duggal G, Love MI, Irizarry RA, Kingsford C. 2017. Salmon provides fast and bias-aware quantification of transcript expression. *Nat Methods* 14:417-419.
- Burset M, Seledtsov IA, Solovyev VV. 2000. Analysis of canonical and non-canonical splice sites in mammalian genomes. *Nucleic Acids Res* 28:4364-4375.

## Related Skills

- hisat2-alignment - Low-memory splice-aware alternative to STAR
- bwa-alignment - DNA short-read mapping (when reads do not cross junctions)
- read-qc/rnaseq-qc - RNA destination metrics: rRNA, gene-body coverage, strandedness
- read-qc/fastp-workflow - Trim adapters/poly-A before alignment
- alignment-files/bam-statistics - flagstat/idxstats QC gate; what a high mapping rate hides; contig naming
- rna-quantification/featurecounts-counting - Count aligned reads over genes (NH-aware multimapper handling)
- rna-quantification/alignment-free-quant - Salmon/kallisto when only known-transcript DE is needed
- differential-expression/deseq2-basics - Downstream DE from the count matrix
- single-cell/data-io - STARsolo single-cell counts into a single-cell workflow
<!-- END FILE: read-alignment/star-alignment/SKILL.md -->

<!-- END CATEGORY: read-alignment -->

