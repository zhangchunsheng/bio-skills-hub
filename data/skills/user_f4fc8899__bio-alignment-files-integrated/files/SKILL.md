---
slug: bio-alignment-files-integrated
version: 1.0.1
displayName: "比对文件处理 / SAM/BAM/CRAM alignment file operations"
name: bio-alignment-files-integrated
summary: "中文：比对文件处理综合技能，整合 10 个相关专题，覆盖SAM/BAM/CRAM比对文件操作：查看、排序、过滤、索引、统计、去重、amplicon修剪与质量验证。 English: Integrated SAM/BAM/CRAM alignment file operations skill covering 10 related topics, including SAM/BAM/CRAM alignment file operations: view, sort, filter, index, statistics, deduplication, amplicon clipping, and quality validation."
description: "中文：这是一个面向比对文件处理的综合生物信息学 Skill，整合当前分类下 10 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：SAM/BAM/CRAM比对文件操作：查看、排序、过滤、索引、统计、去重、amplicon修剪与质量验证。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：samtools。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for SAM/BAM/CRAM alignment file operations, combining 10 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers SAM/BAM/CRAM alignment file operations: view, sort, filter, index, statistics, deduplication, amplicon clipping, and quality validation. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: samtools. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# alignment-files 分类 Skill 整合版

> 本文件整合同一主分类目录下 10 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: alignment-files -->

## 子目录：alignment-files/alignment-amplicon-clipping

<!-- BEGIN FILE: alignment-files/alignment-amplicon-clipping/SKILL.md -->
---
name: bio-alignment-amplicon-clipping
description: Trim PCR primers from aligned reads in amplicon-panel BAMs using samtools ampliconclip. Use when processing SARS-CoV-2 ARTIC, hereditary cancer panels, ctDNA hot-spot panels, or any amplicon assay where primer-derived bases would falsely confirm reference at primer footprints.
tool_type: cli
primary_tool: samtools
---

## Version Compatibility

Reference examples tested with: samtools 1.19+, pysam 0.22+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Alignment Amplicon Clipping

**"Trim primer-derived bases from amplicon BAM"** -> Soft- or hard-clip the 5' primer footprint after alignment using a primer BED, then repair fixmate/MD/NM tags.
- CLI: `samtools ampliconclip -b primers.bed input.bam -o clipped.bam` (since samtools 1.11)
- Alternative: `iVar trim`, `BAMClipper`, `fgbio ClipBam`

## Why Primer Trimming After Alignment

Amplicon panels (SARS-CoV-2 ARTIC, hereditary cancer panels, ctDNA hot-spot panels, fusion panels, 16S rRNA) use designed PCR primers for enrichment. Primer-derived bases at read 5' ends do NOT reflect biological sequence -- they reflect the primer template. Without trimming:
- False reference confirmation at primer footprint positions.
- Variant allele frequency suppressed at variants under primers (the primer sequence cannot capture the variant base).
- Strand bias artifacts (primers are typically one-strand).

Standard amplicon BAMs should NEVER be processed by `samtools markdup` -- by design every read at a primer location is a "duplicate" by coordinate. See duplicate-handling for the assay-aware decision.

## Tool Selection

| Tool | When | Notes |
|------|------|-------|
| `samtools ampliconclip` | Default for amplicon panels (since 1.11) | Soft- or hard-clip from BED; modifies CIGAR; invalidates MD/NM |
| `iVar trim` | Illumina SARS-CoV-2 / PrimalSeq route (Andersen lab) | Coordinates by primer name/position; soft-clips only + quality sliding-window |
| `BAMClipper` | Capture / hybrid panels with primer overlap | 5'-end clipping with overlap handling |
| `fgbio ClipBam` | When read-pair coordination matters | Soft/hard-clip with mate-aware end adjustment |
| `cutadapt` (pre-alignment) | Legacy / when alignment is downstream | Trims at FASTQ stage; less precise for amplicon |

## Soft-Clip vs Hard-Clip

**Goal:** Decide whether trimmed bases are kept in the BAM (reversible) or discarded (irreversible).

**Approach:** Soft-clip is the safe default; hard-clip only when archiving and disk is constrained.

| Mode | Flag | What it does | Reversible? |
|------|------|--------------|-------------|
| Soft-clip | (default) / `--soft-clip` | Bases kept in SEQ; CIGAR uses `S`; bases not aligned | Yes (CIGAR can be re-extended) |
| Hard-clip | `--hard-clip` | Bases removed from SEQ; CIGAR uses `H` | **No** (bases lost) |

Soft-clip is the recommended default. Hard-clip is irreversible -- once applied, the trimmed bases cannot be recovered for re-analysis with different primer coordinates.

## Basic ampliconclip Workflow

**Goal:** Trim primers from a coordinate-sorted, indexed amplicon BAM and produce a downstream-ready BAM.

**Approach:** Run `ampliconclip` with primer BED, choosing either `--strand` (5' strand-aware) or `--both-ends` (read-through amplicons; note `--both-ends` overrides `--strand`), then re-fixmate (CIGAR changed) and re-calmd (MD/NM tags invalidated by clip).

```bash
# 1. Soft-clip primers (default; reversible). --strand clips only the designed strand.
samtools ampliconclip --strand --soft-clip \
    -b primers.bed input.bam -o clipped.bam

# 2. Re-pair tags (CIGARs changed -- mate info needs refresh)
samtools sort -n clipped.bam | \
    samtools fixmate -m - - | \
    samtools sort -o sorted.bam -

# 3. Repair MD/NM tags (invalidated by clip; required by mpileup BAQ and IGV)
samtools calmd -b sorted.bam reference.fa > clipped_final.bam
samtools index clipped_final.bam
```

### Strand-Aware Clipping

`--strand` clips primer bases only on the strand the primer is designed for. Without `--strand`, both strands are clipped at the primer site, removing valid biological sequence on the off-strand.

### Both-End Clipping

`--both-ends` allows clipping at both 5' and 3' positions of the read (some primers can appear at either end after alignment). Necessary for amplicon designs where reads can read through the entire amplicon. When `--both-ends` is set, `--strand` is ignored -- primer sites at both ends are clipped regardless of the BED strand column:

```bash
samtools ampliconclip --both-ends --soft-clip -b primers.bed input.bam -o clipped.bam
```

## Primer BED Format

```
# tab-separated, 0-based half-open like all BED
chr1   100   125   primer_1_F    +
chr1   500   525   primer_1_R    -
chr1   600   625   primer_2_F    +
chr1   1000  1025  primer_2_R    -
```

Tools that consume the BED: column 1-3 (region), column 6 (strand) is required for `--strand`. ARTIC primer schemes ship pre-built BEDs (e.g., `primer.bed` from artic-network/primer-schemes).

## SARS-CoV-2 ARTIC Comparison

| Tool | Approach | When |
|------|----------|------|
| `samtools ampliconclip` | Soft-clip from BED, post-alignment | General amplicon panels; modern ARTIC workflows |
| `iVar trim` | Soft-clip with primer-position parsing + quality trim | nf-core/viralrecon; Illumina PrimalSeq route (Andersen lab) |

Note: the ARTIC network's own nanopore field-bioinformatics pipeline (`artic minion`) trims primers with its `align_trim` tool, not iVar; iVar (Grubaugh et al. 2019, Genome Biol 20:8) is the Illumina/PrimalSeq route. Modern viral consensus pipelines tend to use ampliconclip then `samtools consensus --config hiseq --ambig` (Illumina preset) for IUPAC heterozygote handling. See reference-operations for consensus generation.

## After Clipping: Required Re-Processing

Clipping invalidates several tags and CIGAR-derived fields:

| Field | Impact | Repair |
|-------|--------|--------|
| CIGAR | New `S` or `H` operations added | Automatic from ampliconclip |
| MD:Z | Mismatch positions now wrong | `samtools calmd -b in.bam ref.fa` |
| NM:i | Edit distance recomputed | `samtools calmd` |
| TLEN | Template length changes when both mates clipped | `samtools fixmate -m` |
| ms, MC:Z | Mate score (lowercase per SAMtags) / mate CIGAR | `samtools fixmate -m` |

A clipped BAM that bypasses fixmate + calmd causes silent failures in `bcftools mpileup` BAQ (which depends on MD), IGV mismatch coloring, and any tool using NM for filtering.

## Why Not Markdup

Amplicon reads at primer locations are by design coordinate-degenerate -- every read mapped to the same amplicon shares the same start/end coordinates because they all come from the same primer pair. `samtools markdup` would mark essentially every read as a duplicate and erase the dataset. For amplicon panels:

- WITHOUT UMIs: skip dedup entirely; rely on coverage uniformity from amplicon design.
- WITH UMIs (deep panels): use `fgbio GroupReadsByUmi` -> `CallMolecularConsensusReads` instead of markdup. See duplicate-handling.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `MD tag mismatch` after clipping | calmd not run | Run `samtools calmd -b clipped.bam ref.fa` |
| Variant calls with strand bias at every amplicon end | Forgot `--strand` | Re-run with strand-aware clipping |
| Markdup output shows ~100% duplicates | Amplicon BAM was processed with markdup | Restart from raw alignment; use ampliconclip; skip markdup |
| Unexpected reference confirmation at primer-overlapping variants | ampliconclip not run | Run before variant calling |

## Quick Reference

| Task | Command |
|------|---------|
| Soft-clip primers (strand-aware) | `samtools ampliconclip --strand -b primers.bed in.bam -o clipped.bam` |
| Soft-clip primers (read-through amplicons) | `samtools ampliconclip --both-ends -b primers.bed in.bam -o clipped.bam` |
| Hard-clip (irreversible) | `samtools ampliconclip --strand --hard-clip -b primers.bed in.bam -o clipped.bam` |
| Repair MD/NM after clip | `samtools calmd -b clipped.bam ref.fa > final.bam` |
| Repair mate info | `samtools sort -n - \| samtools fixmate -m - - \| samtools sort -o out.bam -` |

## Related Skills

- duplicate-handling - Why amplicon BAMs should not be markdup'd; UMI-aware alternatives
- alignment-filtering - Post-clip filtering for amplicon variant calling
- alignment-sorting - Re-sort after fixmate
- pileup-generation - mpileup flags for amplicon (`-aa -A -d 600000 -B`)
- reference-operations - Consensus generation from amplicon BAMs (samtools consensus)
- read-qc/quality-reports - Pre-alignment adapter/quality trimming
<!-- END FILE: alignment-files/alignment-amplicon-clipping/SKILL.md -->

## 子目录：alignment-files/alignment-filtering

<!-- BEGIN FILE: alignment-files/alignment-filtering/SKILL.md -->
---
name: bio-alignment-filtering
description: Filter alignments by flags, mapping quality, and regions using samtools view and pysam. Use when extracting specific reads, removing low-quality alignments, or subsetting to target regions.
tool_type: cli
primary_tool: samtools
---

## Version Compatibility

Reference examples tested with: pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Alignment Filtering

**"Filter my BAM file to keep only high-quality reads"** -> Select reads by FLAG bits, mapping quality, and genomic regions using samtools view or pysam.
- CLI: `samtools view` with `-F`/`-f`/`-q`/`-L` flags (samtools)
- Python: `pysam.AlignmentFile` iteration with attribute filters (pysam)

Filter alignments by flags, quality, and regions using samtools and pysam.

## Filter Flags

| Option | Description |
|--------|-------------|
| `-f FLAG` | Include reads with ALL bits set |
| `-F FLAG` | Exclude reads with ANY bits set |
| `-G FLAG` | Exclude reads with ALL bits set |
| `-q MAPQ` | Minimum mapping quality |
| `-L BED` | Include reads overlapping regions |

## Common FLAG Values

| Flag | Hex | Meaning |
|------|-----|---------|
| 1 | 0x1 | Paired |
| 2 | 0x2 | Proper pair |
| 4 | 0x4 | Unmapped |
| 8 | 0x8 | Mate unmapped |
| 16 | 0x10 | Reverse strand |
| 32 | 0x20 | Mate reverse strand |
| 64 | 0x40 | First in pair (read1) |
| 128 | 0x80 | Second in pair (read2) |
| 256 | 0x100 | Secondary alignment |
| 512 | 0x200 | Failed QC |
| 1024 | 0x400 | Duplicate |
| 2048 | 0x800 | Supplementary |

## Filter by FLAG

### Keep Only Mapped Reads
```bash
samtools view -F 4 -o mapped.bam input.bam
```

### Keep Only Unmapped Reads
```bash
samtools view -f 4 -o unmapped.bam input.bam
```

### Keep Only Properly Paired
```bash
samtools view -f 2 -o proper.bam input.bam
```

### Remove Duplicates
```bash
samtools view -F 1024 -o nodup.bam input.bam
```

### Remove Secondary and Supplementary
```bash
samtools view -F 2304 -o primary.bam input.bam
```

### Keep Only Primary Alignments
```bash
samtools view -F 256 -F 2048 -o primary.bam input.bam
# Or combined: -F 2304
```

### Keep Read1 Only
```bash
samtools view -f 64 -o read1.bam input.bam
```

### Keep Read2 Only
```bash
samtools view -f 128 -o read2.bam input.bam
```

### Forward Strand Only
```bash
samtools view -F 16 -o forward.bam input.bam
```

### Reverse Strand Only
```bash
samtools view -f 16 -o reverse.bam input.bam
```

## Filter by Mapping Quality

### Minimum MAPQ
```bash
samtools view -q 30 -o highqual.bam input.bam
```

### MAPQ and Mapped
```bash
samtools view -F 4 -q 30 -o filtered.bam input.bam
```

### Aligner-Aware MAPQ Thresholds

MAPQ scales differ by aligner; the same `-q 30` filter does different things. See sam-bam-basics for the full MAPQ-by-aligner table. Filtering recommendations:

| Aligner | "Drop ambiguous" | "High confidence" |
|---------|------------------|-------------------|
| BWA-MEM / BWA-MEM2 | `-q 1` | `-q 30` (or `-q 60` for unique only) |
| Bowtie2 | `-q 1` | `-q 23` (Bowtie2 MAPQ maxes at 42 end-to-end; 23 is a community "uniquely mapped" convention derived from analysis of Bowtie2's MAPQ scoring, not stated in the official manual) |
| **STAR** | `-q 255` | `-q 255` (STAR emits only MAPQ 0/1/3/255, 255 = unique; `-q 60` is therefore equivalent to `-q 255` -- there are no values between 3 and 255) |
| HISAT2 | `-q 1` | `-q 60` |
| minimap2 (DNA, long-read) | `-q 1` | `-q 60` |
| pbmm2 (PacBio) | `-q 1` | `-q 60` |

For Phred-scaled aligners (BWA, minimap2), MAPQ Q maps to ~10^(-Q/10) probability of wrong mapping. For STAR, the only emitted values are 0/1/3/255 (sentinels, not probabilities).

### Drop Ambiguous Across Aligners (Universal)
```bash
samtools view -q 1 in.bam   # exclude MAPQ=0; works for all aligners
```

## Filter by Region

### Single Region
```bash
samtools view -o region.bam input.bam chr1:1000000-2000000
```

### Multiple Regions
```bash
samtools view -o regions.bam input.bam chr1:1000-2000 chr2:3000-4000
```

### Regions from BED File
```bash
samtools view -L targets.bed -o targets.bam input.bam
```

### Combine Region and Quality
```bash
samtools view -q 30 -L targets.bed -o filtered.bam input.bam
```

## Combined Filters

### Standard Quality Filter

**Goal:** Produce a clean BAM containing only primary, mapped, non-duplicate reads with high mapping confidence.

**Approach:** Combine FLAG exclusion (-F for unmapped + secondary + duplicate + supplementary) with a MAPQ threshold.

**Reference (samtools 1.19+):**
```bash
samtools view -F 3332 -q 30 -o filtered.bam input.bam
# 3332 = 4 (unmapped) + 256 (secondary) + 1024 (duplicate) + 2048 (supplementary)
```

### Variant Calling Prep -- Assay-Aware

**Goal:** Choose a filter that matches what the downstream caller expects. Stripping supplementary alignments breaks SV callers; requiring proper-pair drops valid spliced RNA-seq reads.

| Assay / caller | Recommended filter | Why |
|----------------|-------------------|-----|
| Germline WGS short-variant (HaplotypeCaller, DeepVariant) | `-f 2 -F 3328 -q 20` | Primary, no dup, proper pair, MAPQ>=20 |
| Somatic short-variant (Mutect2, Strelka2) | `-F 3328 -q 1` | Drop only MAPQ=0; somatic callers handle low MAPQ; chimeric reads at SVs may carry real somatic SNVs |
| Long-read short-variant (clair3, DeepVariant ONT) | `-F 3328 -q 5` | Long-read MAPQ scale is lower |
| Long-read SV (Sniffles, cuteSV) | `-F 1024` only | **Keep supplementary** -- SA tag is the SV signal |
| Short-read SV (Manta, GRIDSS, Delly, SvABA) | `-F 1024` only | Same -- supplementary required |
| ChIP-seq peak calling | `-F 1804 -q 30` | Drop dup + secondary + unmapped + mate-unmapped + QC-fail (supplementary reads are kept -- 1804 has no 2048 bit) |
| ATAC-seq | `-F 1804 -q 30 -f 2` | Same plus proper pair |
| RNA-seq quantification (STAR) | `-q 255` | Unique only (STAR sentinel) |
| RNA-seq quantification (HISAT2) | `-F 256 -q 60` | Different aligner semantics |
| RNA-seq variant (after `SplitNCigarReads`) | `-F 3328 -q 20` | Standard germline after split-N-trim |
| Panel / amplicon | After `samtools ampliconclip`; `-F 1024 -q 20` | Primer overlap makes proper-pair unreliable |
| ctDNA / cfDNA (UMI) | After fgbio consensus; do not pre-filter raw | |

**Reference (samtools 1.19+):**
```bash
# Short-variant germline
samtools view -f 2 -F 3328 -q 20 -o clean.bam input.bam
# 3328 = 256 (secondary) + 1024 (duplicate) + 2048 (supplementary)

# SV calling: KEEP supplementary
samtools view -F 1024 -o sv_input.bam input.bam   # NOT -F 2304 or -F 3328

# ChIP-seq / ATAC-seq common filter
samtools view -F 1804 -q 30 -o filtered.bam input.bam
# 1804 = 4 + 8 + 256 + 512 + 1024 = unmapped + mate-unmapped + secondary + QC-fail + duplicate
```

**Cost of getting this wrong:** filtering `-F 2304` or `-F 3328` before SV calling produces zero SV calls -- a single-flag mistake that silently invalidates the analysis.

## Subsample Reads (Deterministic, Pair-Consistent)

`samtools view -s SEED.FRAC` -- integer is the hash seed; fractional is the keep fraction. The hash is on QNAME, so:
1. Mate consistency: read1 and read2 are kept or dropped together.
2. Reproducibility: same seed + same fraction returns the same reads.
3. **Sequential downsampling requires different seeds.** With the same seed the keep-sets are nested, so `-s 1.5` then `-s 1.25` keeps a nested 1/4 (25%) of the original, not 12.5%. Use different integer seeds for independent samples.

```bash
# 10% with seed 42 (always the same reads; pair-consistent)
samtools view -s 42.1 -b -o subset.bam input.bam

# Sequential cuts with INDEPENDENT seeds
samtools view -s 1.5 -b in.bam > half1.bam
samtools view -s 2.25 -b half1.bam > quarter.bam   # 12.5% of original

# Coverage-matching to a target read count
total=$(samtools view -c -F 2304 input.bam)
target=10000000
frac=$(awk -v t=$target -v n=$total 'BEGIN{printf "%.6f", t/n}')
samtools view -s "1.${frac#*.}" -b -o matched.bam input.bam

# Tumor-normal coverage matching (pull tumor down to normal)
normal_reads=$(samtools view -c -F 2308 normal.bam)
tumor_reads=$(samtools view -c -F 2308 tumor.bam)
if [ "$tumor_reads" -gt "$normal_reads" ]; then
    frac=$(awk -v n=$normal_reads -v t=$tumor_reads 'BEGIN{printf "%.6f", n/t}')
    samtools view -s "1.${frac#*.}" -b -o tumor_matched.bam tumor.bam
fi
```

A subsampled BAM without an integer seed (`-s 0.1`) is non-reproducible -- production pipelines should reject it.

## Expression Filtering

`samtools view -e EXPR` (or `--expr`, since samtools 1.12; the `sclen` helper used below and improved null-tag handling arrived in 1.16) supports arbitrary expression filtering on tags, FLAG, MAPQ, RNAME, CIGAR, etc. Powerful for filtering by `NM`, `AS`, `NH`, `cs`, etc. that the FLAG-based filters cannot reach:
```bash
# Reads with >=2 mismatches (NM tag)
samtools view -e '[NM] >= 2' in.bam

# Soft clip on the left, on chr1
samtools view -e 'cigar=~"^[0-9]+S" && rname=="chr1"' in.bam

# Combine with FLAG and MAPQ
samtools view -F 2308 -q 30 -e '[NM] <= 5 && [AS] >= 100' in.bam

# Drop reads with low mapped fraction (samtools-internal helpers)
samtools view -e 'sclen / qlen < 0.2' in.bam
```

Note: in samtools 1.16+, `![NM]` is true only if NM is missing (was buggy in earlier versions); NULL values from missing tags propagate through arithmetic.

## Filter by Read Group
```bash
samtools view -r library_A in.bam              # single read group
samtools view -R rg_list.txt in.bam            # multiple via file (one ID per line)
```

## pysam Python Alternative

### Basic Filtering
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('filtered.bam', 'wb', header=infile.header) as outfile:
        for read in infile:
            if read.is_unmapped:
                continue
            if read.mapping_quality < 30:
                continue
            if read.is_duplicate:
                continue
            outfile.write(read)
```

### Filter with Function

**Goal:** Apply a multi-criteria quality filter to produce clean alignments for downstream analysis.

**Approach:** Define a predicate checking mapped status, primary alignment, duplicate flag, and MAPQ; stream reads through it.

**Reference (pysam 0.22+):**
```python
import pysam

def passes_filter(read):
    if read.is_unmapped:
        return False
    if read.is_secondary or read.is_supplementary:
        return False
    if read.is_duplicate:
        return False
    if read.mapping_quality < 30:
        return False
    return True

with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('filtered.bam', 'wb', header=infile.header) as outfile:
        for read in infile:
            if passes_filter(read):
                outfile.write(read)
```

### Filter by Region
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('region.bam', 'wb', header=infile.header) as outfile:
        for read in infile.fetch('chr1', 1000000, 2000000):
            outfile.write(read)
```

### Filter from BED File

**Goal:** Extract only reads overlapping target regions defined in a BED file.

**Approach:** Parse BED into a list of (chrom, start, end) tuples, then fetch reads from each region and write to output.

**Reference (pysam 0.22+):**
```python
import pysam

def read_bed(bed_path):
    regions = []
    with open(bed_path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            regions.append((parts[0], int(parts[1]), int(parts[2])))
    return regions

regions = read_bed('targets.bed')

with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('targets.bam', 'wb', header=infile.header) as outfile:
        for chrom, start, end in regions:
            for read in infile.fetch(chrom, start, end):
                outfile.write(read)
```

### Subsample (Pair-Consistent)

Hash on QNAME so mates stay together (a fresh `random.random()` per read drops mates inconsistently and breaks paired-end tools):
```python
import pysam
import zlib

fraction = 0.1
seed = 42
threshold = int(0xffffffff * fraction)

def template_hash(qname, seed):
    return zlib.crc32(qname.encode()) ^ seed

with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('subset.bam', 'wb', header=infile.header) as outfile:
        for read in infile:
            if template_hash(read.query_name, seed) <= threshold:
                outfile.write(read)
```

## Quick Reference

| Task | samtools command |
|------|------------------|
| Mapped only | `view -F 4` |
| Unmapped only | `view -f 4` |
| Properly paired | `view -f 2` |
| Primary only | `view -F 2304` |
| No duplicates | `view -F 1024` |
| High MAPQ | `view -q 30` |
| Region | `view file.bam chr1:1-1000` |
| BED regions | `view -L file.bed` |
| Subsample 10% (reproducible) | `view -s 42.1` |
| Standard filter | `view -F 3332 -q 30` |

## Common Filter Combinations

| Purpose | Flags |
|---------|-------|
| Clean reads | `-F 3332 -q 30` (mapped, primary, no dups, high qual) |
| Variant calling | `-f 2 -F 3328 -q 20` (proper pair, primary, no dups) |
| Coverage analysis | `-F 1284 -q 1` (mapped, no secondary, no dups; supplementary retained) |
| Count unique | `-F 2304` (primary only) |

Flag breakdowns:
- 2304 = 256 + 2048 (secondary + supplementary)
- 3328 = 256 + 1024 + 2048 (secondary + duplicate + supplementary)
- 3332 = 4 + 256 + 1024 + 2048 (unmapped + secondary + duplicate + supplementary)
- 1284 = 4 + 256 + 1024 (unmapped + secondary + duplicate)

## Related Skills

- sam-bam-basics - FLAG semantics, MAPQ-by-aligner, secondary vs supplementary
- alignment-sorting - Sort before/after filtering
- alignment-indexing - Required for region filtering
- alignment-amplicon-clipping - Primer clipping for amplicon panels
- duplicate-handling - Mark duplicates before filtering
- bam-statistics - Check filter effects
<!-- END FILE: alignment-files/alignment-filtering/SKILL.md -->

## 子目录：alignment-files/alignment-indexing

<!-- BEGIN FILE: alignment-files/alignment-indexing/SKILL.md -->
---
name: bio-alignment-indexing
description: Create and use BAI/CSI indices for BAM/CRAM files using samtools and pysam. Use when enabling random access to alignment files or fetching specific genomic regions.
tool_type: cli
primary_tool: samtools
---

## Version Compatibility

Reference examples tested with: pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Alignment Indexing

Create indices for random access to alignment files using samtools and pysam.

**"Index a BAM file"** -> Create a .bai/.csi index enabling random access to genomic regions.
- CLI: `samtools index file.bam`
- Python: `pysam.index('file.bam')`

## Index Types

| Index | Extension | Max contig | Bin shift | When required |
|-------|-----------|-----------|-----------|---------------|
| BAI | `.bai` / `.bam.bai` | 2^29 bp ≈ 537 Mbp | fixed (16 kb) | Default for human, mouse, fly, fish |
| CSI | `.csi` / `.bam.csi` | 2^(min_shift + depth*3) | configurable via `-m` | **Required** for any contig >537 Mbp |
| CRAI | `.crai` / `.cram.crai` | chunk-based | n/a | CRAM only |
| TBI | `.tbi` | 2^29-1 | fixed | tabix VCF/BED -- same limit as BAI |

### Which Index for Which Genome

| Genome | Largest contig | Index |
|--------|---------------|-------|
| GRCh38 / GRCh37 (human) | 248 Mbp | BAI |
| GRCm39 (mouse) | 195 Mbp | BAI |
| GRCz11 (zebrafish), TAIR10 (Arabidopsis) | 78 Mbp / 30 Mbp | BAI |
| Wheat IWGSC (Triticum aestivum) | ~830 Mbp (chr3B) | **CSI** |
| Pine, fir, axolotl, sugar pine | multi-Gbp | **CSI with larger `-m`** |
| Long-read assembly with very large contigs | varies | check `cut -f2 ref.fa.fai \| sort -nr \| head -1` |

For polyploid plants and salamander-scale genomes, increase the bin shift:
```bash
# Default CSI matches BAI bin layout: 2^(14 + 5*3) = 2^29 bp ≈ 537 Mbp per contig
samtools index -c file.bam

# Larger min_shift for contigs >537 Mbp (wheat, axolotl, sugar pine)
samtools index -c -m 18 file.bam   # 2^(18+15) = 2^33 = ~8.5 Gbp per contig
```

**Index file precedence:** htslib (and therefore the samtools CLI) tries `.csi` before `.bai` on auto-load, so when both exist the `.csi` is used -- a stale `.bai` left over after re-indexing to CSI is generally ignored. (Note: htsjdk/Java prefers `.bai`, the opposite order.) Removing the obsolete `.bai` still avoids confusion.

## samtools index

### Create BAI Index
```bash
samtools index input.bam
# Creates input.bam.bai
```

### Create CSI Index
```bash
samtools index -c input.bam
# Creates input.bam.csi
```

### Specify Output Name
```bash
samtools index input.bam output.bai
```

### Multi-threaded Indexing
```bash
samtools index -@ 4 input.bam
```

### Index CRAM
```bash
samtools index input.cram
# Creates input.cram.crai
```

## Index Requirements

Indexing requires coordinate-sorted files:
```bash
# Check sort order
samtools view -H input.bam | grep "^@HD"
# Should show SO:coordinate

# Sort if needed, then index
samtools sort -o sorted.bam input.bam
samtools index sorted.bam
```

## Using Indices for Region Access

**Goal:** Extract reads overlapping specific genomic coordinates from an indexed BAM.

**Approach:** With the index present, `samtools view` or `pysam.fetch()` can jump directly to the relevant file offset instead of scanning the entire file.

### samtools view with Region
```bash
# Requires index file present
samtools view input.bam chr1:1000000-2000000
```

### Multiple Regions
```bash
samtools view input.bam chr1:1000-2000 chr2:3000-4000
```

### Regions from BED File
```bash
samtools view -L regions.bed input.bam
```

## pysam Python Alternative

### Create Index
```python
import pysam

pysam.index('input.bam')
# Creates input.bam.bai
```

### Create CSI Index
```python
# pysam.index passes through to samtools index; pass the -c flag for CSI.
pysam.index('-c', 'input.bam')
# Produces input.bam.csi.
```

### Fetch with Index
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    # fetch() requires index
    for read in bam.fetch('chr1', 1000000, 2000000):
        print(read.query_name)
```

### Check if Indexed
```python
import pysam
from pathlib import Path

def is_indexed(bam_path):
    bam_path = Path(bam_path)
    return (bam_path.with_suffix('.bam.bai').exists() or
            Path(str(bam_path) + '.bai').exists() or
            bam_path.with_suffix('.bam.csi').exists())

if not is_indexed('input.bam'):
    pysam.index('input.bam')
```

### Fetch Multiple Regions
```python
regions = [('chr1', 1000, 2000), ('chr1', 5000, 6000), ('chr2', 1000, 2000)]

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for chrom, start, end in regions:
        count = sum(1 for _ in bam.fetch(chrom, start, end))
        print(f'{chrom}:{start}-{end}: {count} reads')
```

### Count Reads in Region
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    count = bam.count('chr1', 1000000, 2000000)
    print(f'Reads in region: {count}')
```

### Get Reads Covering Position
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for read in bam.fetch('chr1', 1000000, 1000001):
        if read.reference_start <= 1000000 < read.reference_end:
            print(f'{read.query_name} covers position 1000000')
```

## Index File Locations

samtools looks for indices in two locations:
```
input.bam.bai   # Standard location
input.bai       # Alternative location
```

For CRAM:
```
input.cram.crai
```

## idxstats - Index Statistics

### Get Per-Chromosome Counts
```bash
samtools idxstats input.bam
```

Output format:
```
chr1    248956422    5000000    0
chr2    242193529    4500000    0
*       0            0          10000
```

Columns: reference name, length, mapped reads, unmapped reads.

### What "mapped" Actually Counts (Caveat)

The mapped column counts **every alignment record with that RNAME, including secondary AND supplementary**. For long-read minimap2 output, where a single read can produce many supplementary chimeric alignments, idxstats overcounts input reads -- typically 1.5-3x.

For unique read counts, use primary-only:
```bash
samtools view -c -F 2304 input.bam chr1   # primary only
```

Cross-check unmapped consistency (a senior sanity check):
```bash
samtools idxstats file.bam | awk '{sum+=$4} END {print sum}'   # idxstats unmapped (sum across all rows; PE orphans get a contig RNAME)
samtools view -c -f 4 -F 2304 file.bam                         # primary unmapped (should match)
```

### Sum Total Mapped Reads
```bash
samtools idxstats input.bam | awk '{sum += $3} END {print sum}'
```

### pysam idxstats
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for stat in bam.get_index_statistics():
        print(f'{stat.contig}: {stat.mapped} mapped, {stat.unmapped} unmapped')
```

## FASTA Index (faidx)

Related but different - index reference FASTA for random access:

```bash
samtools faidx reference.fa
# Creates reference.fa.fai

# Fetch region from indexed FASTA
samtools faidx reference.fa chr1:1000-2000
```

### pysam FastaFile
```python
with pysam.FastaFile('reference.fa') as ref:
    seq = ref.fetch('chr1', 1000, 2000)
    print(seq)
```

## Quick Reference

| Task | samtools | pysam |
|------|----------|-------|
| Create BAI | `samtools index file.bam` | `pysam.index('file.bam')` |
| Create CSI | `samtools index -c file.bam` | `pysam.index('-c', 'file.bam')` |
| Fetch region | `samtools view file.bam chr1:1-1000` | `bam.fetch('chr1', 0, 1000)` |
| Count in region | `samtools view -c file.bam chr1:1-1000` | `bam.count('chr1', 0, 1000)` |
| Index stats | `samtools idxstats file.bam` | `bam.get_index_statistics()` |
| Index FASTA | `samtools faidx ref.fa` | Automatic with FastaFile |

## Index Staleness

If the BAM was modified after indexing, the index points to wrong file offsets and region queries return wrong (or zero) reads. Quick check:
```bash
if [ input.bam -nt input.bam.bai ]; then
    echo "Index older than BAM; re-indexing"
    samtools index input.bam
fi
```

## Contig-Naming Sanity Check

A leading cause of "my variant calling produced empty VCFs" tickets: querying `chrM` against a BAM that uses `MT` (or `chr1` vs `1`). Always inspect contig conventions before region queries:
```bash
samtools view -H input.bam | grep '^@SQ' | head -3
# Compare with reference dict:
samtools dict ref.fa | head -3
```

UCSC convention uses `chr1`/`chrM`; Ensembl/NCBI uses `1`/`MT`. The two are not interchangeable; tools fail with "contig not found" or silently return zero reads.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `random alignment retrieval only works for indexed BAM` | Missing index | Run `samtools index file.bam` |
| `file is not sorted` | Unsorted BAM | Sort first with `samtools sort` |
| `chromosome not found` | Wrong chromosome name | Check names with `samtools view -H` |
| Region query returns zero reads on a known-populated locus | Stale BAI / `chr` vs no-`chr` mismatch | Re-index; verify naming convention |
| BAI silently truncates reads on contigs >537 Mbp | Plant / amphibian / amplified genome | Use CSI: `samtools index -c file.bam` |

## Related Skills

- sam-bam-basics - View and convert alignment files
- alignment-sorting - Sort BAM files (required before indexing)
- alignment-filtering - Filter by regions using index
- bam-statistics - Use idxstats for quick counts
- sequence-io/read-sequences - Index FASTA with SeqIO.index_db()
<!-- END FILE: alignment-files/alignment-indexing/SKILL.md -->

## 子目录：alignment-files/alignment-sorting

<!-- BEGIN FILE: alignment-files/alignment-sorting/SKILL.md -->
---
name: bio-alignment-sorting
description: Sort alignment files by coordinate or read name using samtools and pysam. Use when preparing BAM files for indexing, variant calling, or paired-end analysis.
tool_type: cli
primary_tool: samtools
---

## Version Compatibility

Reference examples tested with: pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Alignment Sorting

Sort alignment files by coordinate or read name using samtools and pysam.

**"Sort a BAM file"** -> Reorder reads by genomic coordinate (for indexing/variant calling) or by name (for paired-end processing).
- CLI: `samtools sort -o sorted.bam input.bam`
- Python: `pysam.sort('-o', 'sorted.bam', 'input.bam')`

## Sort Orders

| Order | Flag | Use Case |
|-------|------|----------|
| Coordinate | default | Indexing, visualization, variant calling |
| Name | `-n` | Paired-end processing, fixmate, markdup |
| Tag | `-t TAG` | Sort by specific tag value |

## samtools sort

### Sort by Coordinate (Default)
```bash
samtools sort -o sorted.bam input.bam
```

### Sort by Read Name
```bash
samtools sort -n -o namesorted.bam input.bam
```

### Multi-threaded Sorting
```bash
samtools sort -@ 8 -o sorted.bam input.bam
```

### Control Memory Usage
```bash
samtools sort -m 4G -@ 4 -o sorted.bam input.bam
```

### Set Temporary Directory
```bash
samtools sort -T /tmp/sort_tmp -o sorted.bam input.bam
```

### Specify Output Format
```bash
# Output as BAM (default)
samtools sort -O bam -o sorted.bam input.bam

# Output as CRAM
samtools sort -O cram --reference ref.fa -o sorted.cram input.bam
```

### Sort by Tag
```bash
# Sort by cell barcode (10x Genomics)
samtools sort -t CB -o sorted_by_barcode.bam input.bam
```

### Pipe from Aligner
```bash
bwa mem ref.fa reads.fq | samtools sort -o aligned.bam
```

## samtools collate vs sort -n

| Tool | Algorithm | Speed | Memory | Output guarantee |
|------|-----------|-------|--------|------------------|
| `sort -n` | Full lexicographic sort by QNAME | Slowest | Spills to `-T` | Strict total order by name |
| `collate` | Hash-bucket grouping | ~3-10x faster | Bounded | Mates adjacent; between-mate order undefined |

Use `collate` when extracting paired FASTQ, re-aligning, or streaming through markdup. Use `sort -n` only when a tool requires true lexicographic name order (e.g. RSEM, Salmon alignment-mode).

```bash
# Fast paired FASTQ extraction
samtools collate -O -u in.bam tmp_prefix | \
    samtools fastq -1 R1.fq.gz -2 R2.fq.gz -0 /dev/null -s /dev/null -n -

# Markdup pre-processing (collate beats sort -n here)
samtools collate -O -u in.bam tmp_prefix | \
    samtools fixmate -m -u - - | \
    samtools sort -u - | \
    samtools markdup - out.bam
```

### Sort Order Required by Downstream Tool

| Operation | Required sort |
|-----------|---------------|
| `samtools index` | coordinate (hard requirement) |
| `samtools fixmate -m` | name (or collate; needs mates adjacent) |
| `samtools markdup` | coordinate (after fixmate) |
| GATK MarkDuplicatesSpark | coordinate or queryname |
| `samtools mpileup` / `bcftools mpileup` | coordinate |
| GATK HaplotypeCaller, Mutect2 | coordinate |
| featureCounts / HTSeq | coordinate or name (`-p` for paired) |
| umi_tools dedup | coordinate (with index) |
| fgbio GroupReadsByUmi | any order accepted (template-coordinate recommended to avoid an internal re-sort) |
| fgbio CallMolecularConsensusReads | grouped by MI tag (consumes GroupReadsByUmi output) |
| Sniffles, cuteSV, Manta, Delly | coordinate (need SA tags) |
| Salmon alignment-mode | name |
| RSEM (with STAR `--quantMode TranscriptomeSAM`) | name (hard requirement) |

## Check Sort Order

### From Header
```bash
samtools view -H input.bam | grep "^@HD"
# SO:coordinate = coordinate sorted
# SO:queryname = name sorted
# SO:unsorted = not sorted
```

### Verify Sorted
```bash
# Check if coordinate sorted (returns 0 if sorted). Reset the position tracker
# on each new contig, else the POS reset at every chromosome boundary of a
# correctly sorted multi-contig BAM would falsely report "unsorted".
samtools view input.bam | awk '$3!=c {c=$3; prev=0} $4<prev {exit 1} {prev=$4}'
# Simpler and authoritative: trust the @HD SO: header shown above.
```

## pysam Python Alternative

### Sort with pysam
```python
import pysam

pysam.sort('-o', 'sorted.bam', 'input.bam')
```

### Sort by Name
```python
pysam.sort('-n', '-o', 'namesorted.bam', 'input.bam')
```

### Sort with Options
```python
pysam.sort('-@', '4', '-m', '2G', '-o', 'sorted.bam', 'input.bam')
```

### Avoid In-Python Sorting

Do not load BAM records into a list and call `sorted()`. `pysam.sort()` calls samtools' external-merge sort which spills to disk; loading reads into memory blows up around ~30M reads (~10 GB human BAM). Always delegate to `pysam.sort()`:
```python
import pysam

pysam.sort('-@', '4', '-m', '2G', '-T', '/tmp/sortpfx',
           '-o', 'sorted.bam', 'input.bam')
```

### Check Sort Order in pysam
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    hd = bam.header.get('HD', {})
    sort_order = hd.get('SO', 'unknown')
    print(f'Sort order: {sort_order}')
```

### Stream Sort from Aligner
For streaming from aligners, use shell pipes (simpler and more reliable):
```python
import subprocess

subprocess.run(
    'bwa mem ref.fa reads.fq | samtools sort -o aligned.bam',
    shell=True, check=True
)
```

## samtools merge

Combine multiple BAM files into one. `samtools merge` does NOT validate sort-order consistency across inputs; mismatched inputs silently produce a malformed output.

### Verify Sort Order Consistency First
```bash
for f in *.bam; do samtools view -H "$f" | head -1; done | sort -u
# Should print exactly ONE line, e.g. "@HD VN:1.6 SO:coordinate"
```

### Safe Merge (dedup @RG and @PG)
```bash
# -c deduplicates @RG records; -p deduplicates @PG records (samtools-merge(1))
samtools merge -c -p -@ 8 merged.bam sample1.bam sample2.bam sample3.bam
```

When merging BAMs from different lanes / machines / aligners, RG IDs may collide. `-c` and `-p` deduplicate header records, but RG IDs that genuinely refer to different lane-level read groups must be made unique upstream (`samtools addreplacerg`) before merge -- otherwise GATK BQSR (which keys models by RGID/PU) silently produces wrong recalibration.

### Merge with Threads / from File List
```bash
samtools merge -@ 4 merged.bam sample1.bam sample2.bam sample3.bam
samtools merge -b files.txt merged.bam   # one BAM path per line
```

### Force Overwrite
```bash
samtools merge -f merged.bam sample1.bam sample2.bam
```

### Merge Specific Region
```bash
samtools merge -R chr1:1000000-2000000 merged_region.bam sample1.bam sample2.bam
```

### pysam Merge
```python
import pysam

pysam.merge('-c', '-p', '-f', 'merged.bam', 'sample1.bam', 'sample2.bam', 'sample3.bam')
```

## Common Workflows

**Goal:** Combine sorting with other alignment processing steps into efficient pipelines.

**Approach:** Pipe aligner output directly into `samtools sort` to avoid writing unsorted intermediates, then index for downstream access.

### Align and Sort
```bash
bwa mem -t 8 ref.fa R1.fq R2.fq | samtools sort -@ 4 -o aligned.bam
samtools index aligned.bam
```

### Re-sort by Name for Duplicate Marking
```bash
# Full workflow: sort by name, fixmate, sort by coord, markdup
samtools sort -n -o namesorted.bam input.bam
samtools fixmate -m namesorted.bam fixmate.bam
samtools sort -o sorted.bam fixmate.bam
samtools markdup sorted.bam marked.bam
```

### Convert Name-sorted to Coordinate-sorted
```bash
samtools sort -o coord_sorted.bam name_sorted.bam
samtools index coord_sorted.bam
```

### Extract FASTQ from Sorted BAM
```bash
# Collate first to group pairs
samtools collate -u -O input.bam /tmp/collate | \
    samtools fastq -1 R1.fq -2 R2.fq -0 /dev/null -s /dev/null -
```

## Performance Tips

| Parameter | Effect |
|-----------|--------|
| `-@ N` | Use N additional threads |
| `-m SIZE` | Memory per thread (e.g., 4G) |
| `-T PREFIX` | Temp file location (use fast SSD scratch) |
| `-l LEVEL` | Compression level (1-9, default 6) |

### Compression Level Decision

| Level | Use | Wall-time vs default | Size vs default |
|-------|-----|----------------------|------------------|
| `-l 0` / `-u` | Pipe between samtools tools | 0% (skips BGZF) | +200-400% |
| `-l 1` | Final output if disk is cheap | ~+10% | ~+30% |
| `-l 6` | Default | baseline | baseline |
| `-l 9` | Archival, write-once | ~+50-100% | ~-2-5% |

```bash
# WRONG -- pipe re-compresses then decompresses every step
samtools fixmate -m in.bam - | samtools sort -o out.bam

# RIGHT -- uncompressed (-u) between piped samtools commands
samtools fixmate -m -u in.bam - | samtools sort -o out.bam
```

### Optimal Settings for Large Files
```bash
# 8 threads, 2GB per thread, low compression for output written to fast disk
samtools sort -@ 8 -m 2G -l 1 -T /scratch/sortpfx -o sorted.bam input.bam
```

## Quick Reference

| Task | Command |
|------|---------|
| Sort by coordinate | `samtools sort -o out.bam in.bam` |
| Sort by name | `samtools sort -n -o out.bam in.bam` |
| Sort with threads | `samtools sort -@ 8 -o out.bam in.bam` |
| Collate pairs | `samtools collate -o out.bam in.bam` |
| Merge BAMs | `samtools merge out.bam in1.bam in2.bam` |
| Check sort order | `samtools view -H in.bam \| grep "^@HD"` |
| Sort + index | `samtools sort -o out.bam in.bam && samtools index out.bam` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `out of memory` | Insufficient RAM | Use `-m` to limit per-thread memory |
| `disk full` | Temp files filling disk | Use `-T` to specify different location |
| `truncated file` | Interrupted sort | Re-run sort from original |

## Related Skills

- sam-bam-basics - View and convert alignment files
- alignment-indexing - Index after coordinate sorting
- duplicate-handling - Requires name-sorted input for fixmate
- alignment-filtering - Filter before or after sorting
<!-- END FILE: alignment-files/alignment-sorting/SKILL.md -->

## 子目录：alignment-files/alignment-validation

<!-- BEGIN FILE: alignment-files/alignment-validation/SKILL.md -->
---
name: bio-alignment-validation
description: Validate alignment quality with insert size distribution, proper pairing rates, GC bias, strand balance, and other post-alignment metrics. Use when verifying alignment data quality before variant calling or quantification.
tool_type: mixed
primary_tool: samtools
---

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, picard 3.1+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Alignment Validation

Post-alignment quality control to verify alignment quality and identify issues.

**"Check alignment quality"** -> Compute post-alignment QC metrics (mapping rate, pairing, insert size, strand balance) to identify issues before downstream analysis.
- CLI: `samtools flagstat`, `samtools stats`, Picard `CollectAlignmentSummaryMetrics`
- Python: `pysam.AlignmentFile` iteration with metric calculations

## Two Different Validations

| Concern | Tools | What it catches |
|---------|-------|-----------------|
| **File integrity** | `samtools quickcheck`, `picard ValidateSamFile` | Truncation, missing EOF, malformed records, wrong CIGAR, MAPQ out of range |
| **Sequence dictionary identity** | `samtools dict` + M5 diff | BAM aligned to wrong reference flavor / different decoy / chr vs no-chr |
| **QC metrics** | `samtools stats`, `flagstat`, `mosdepth`, Picard `CollectMultipleMetrics` / `CollectHsMetrics` / `CollectWgsMetrics` | Are the data biologically reasonable for the assay? |
| **Contamination / sample swap** | `verifybamid2`, `somalier`, Picard `CrosscheckFingerprints` | Cross-sample contamination, tumor-normal swap, mislabeled sample |

A file can pass `quickcheck` and still be malformed in ways that crash GATK three hours into HaplotypeCaller. Conversely, a QC-poor BAM can be structurally valid.

### File Integrity
```bash
# Fast: header + EOF block check (misses mid-file truncation, invalid CIGAR)
samtools quickcheck -v in.bam || echo "QUICKCHECK FAILED"
samtools quickcheck -v *.bam > bad_bams.fofn   # one fail-line per bad file

# Slow but thorough: structural validation
picard ValidateSamFile I=in.bam MODE=SUMMARY R=ref.fa

# Production: ignore expected-but-noisy
picard ValidateSamFile I=in.bam MODE=SUMMARY R=ref.fa \
    IGNORE=INVALID_MAPPING_QUALITY \
    IGNORE=MISMATCH_FLAG_MATE_NEG_STRAND
```

CI-safe one-liner:
```bash
test -s in.bam \
  && samtools quickcheck -v in.bam \
  && [ $(samtools view -c -F 2304 in.bam) -gt 1000 ] \
  || { echo "BAM failed integrity"; exit 1; }
```

### Sequence Dictionary Cross-Validation (M5)
```bash
# Compare per-contig MD5 between BAM and reference
diff \
    <(samtools view -H in.bam | grep '^@SQ' | tr '\t' '\n' | grep '^M5:' | sort) \
    <(samtools dict ref.fa | grep '^@SQ' | tr '\t' '\n' | grep '^M5:' | sort)
```

If M5s differ, the BAM was aligned to a different sequence than the current reference (even if contig names match). Concrete failure modes: GRCh38 vs GRCh38.p13 vs GRCh38_no_alt (alt contigs differ); UCSC `chr1` vs Ensembl `1` (names differ, M5s match -- pure renaming); soft-masked vs unmasked (M5 matches -- case is normalized to uppercase before hashing, so lowercase soft-masking is invisible to M5). Note hard-masking is different: it replaces bases with `N`, changing the sequence, so its M5 does NOT match the unmasked reference. The M5 tag is the only definitive identity check.

### Contamination and Sample Swap

No alignment QC is complete without these in production:
```bash
# Cross-sample contamination
verifybamid2 --SVDPrefix /resources/1000g.b38.vcf.gz.SVD \
    --Reference ref.fa --BamFile sample.bam --Output sample.contam
# FREEMIX > 0.03 is the commonly used contamination-concern threshold; values escalate from there.

# Relatedness, sex check, sample swap detection
somalier extract -d extracted/ -s /resources/sites.GRCh38.vcf.gz \
    -f ref.fa sample.bam
somalier relate --infer extracted/*.somalier

# Tumor/normal pairing verification
picard CrosscheckFingerprints I=tumor.bam I=normal.bam \
    HAPLOTYPE_MAP=Homo_sapiens_assembly38.haplotype_database.txt
# LOD > 5 = same individual; < -5 = different
```

Sample-swap rates of 0.5-1% in production cohorts are typical. Without `somalier` or `CrosscheckFingerprints`, swaps are detected only when a downstream finding contradicts clinical expectation.

## Insert Size Distribution

**Goal:** Verify that the fragment length distribution matches the library preparation protocol.

**Approach:** Extract template_length from properly paired reads and compare the distribution to expected values for the library type.

### samtools stats

```bash
samtools stats input.bam > stats.txt
grep "^IS" stats.txt | cut -f2,3 > insert_sizes.txt
```

### Picard CollectInsertSizeMetrics

```bash
java -jar picard.jar CollectInsertSizeMetrics \
    I=input.bam \
    O=insert_metrics.txt \
    H=insert_histogram.pdf
```

### Expected Insert Sizes by Library

| Library | Mean insert | Distribution shape | Diagnostic |
|---------|-------------|-------------------|-----------|
| TruSeq DNA PCR-free WGS | 400-500 bp | Roughly Gaussian, tight/sharp | Sharpest, most symmetric peak (no PCR bias); bimodality = degraded sample |
| TruSeq DNA Nano (PCR) WGS | 300-400 bp | Gaussian, broadened by PCR amplification bias | |
| Twist / IDT exome capture | 250-350 bp | Gaussian | |
| TruSeq Stranded mRNA | 200-300 bp | Right-skewed (transcript distribution) | Long tail = poor size selection |
| Ribo-Zero rRNA-depleted | 250-400 bp | Right-skewed | |
| Smart-seq2 / Smart-seq3 | 200-700 bp | Broad | |
| 10x Chromium (3') | n/a -- not informative | n/a | |
| TruSeq ChIP | 200-400 bp | Sharp | |
| ATAC-seq (Buenrostro / Omni-ATAC) | Multimodal | Peaks at ~50, ~180, ~370 bp | **Missing multimodal pattern = bad library**; missing ~180 bp mononucleosome peak = over-transposition (Tn5 over-titrated) or degraded DNA |
| Hi-C / Micro-C | Multimodal | Peak at ligation-junction size | |
| cfDNA / ctDNA | 160-180 bp | Multimodal; ~167 bp mononucleosomal + ~340 dinuc | Tumor-derived shorter (~145 bp); shape itself is a biomarker |
| FFPE | 100-250 bp | Right-skewed, broad | |
| aDNA | 30-80 bp | Sharp left-skewed | |
| ONT (native) | 1-30 kb | n/a | |
| PacBio HiFi | 10-25 kb | Sharp peak | |

For ATAC, the multimodal pattern *is* the QC. If the mononucleosomal peak (~180 bp) is absent, Tn5 was over-titrated, under-titrated, or DNA was degraded. Use ATACseqQC `fragSizeDist()` for the standard ATAC fragment-size diagnostic.

### Python Insert Size Analysis

```python
import pysam
import numpy as np
import matplotlib.pyplot as plt

def get_insert_sizes(bam_file, max_reads=100000):
    sizes = []
    bam = pysam.AlignmentFile(bam_file, 'rb')
    for i, read in enumerate(bam.fetch()):
        if i >= max_reads:
            break
        if read.is_proper_pair and not read.is_secondary and read.template_length > 0:
            sizes.append(read.template_length)
    bam.close()
    return sizes

sizes = get_insert_sizes('sample.bam')
print(f'Median insert size: {np.median(sizes):.0f}')
print(f'Mean insert size: {np.mean(sizes):.0f}')
print(f'Std dev: {np.std(sizes):.0f}')

plt.hist(sizes, bins=100, range=(0, 1000))
plt.xlabel('Insert Size')
plt.ylabel('Count')
plt.savefig('insert_size_dist.pdf')
```

## Proper Pairing Rate

Percentage of reads correctly paired.

### samtools flagstat

```bash
samtools flagstat input.bam

samtools flagstat input.bam | grep "properly paired"
```

### Calculate Pairing Rate

```bash
proper=$(samtools view -c -f 2 input.bam)
mapped=$(samtools view -c -F 4 input.bam)
rate=$(echo "scale=4; $proper / $mapped * 100" | bc)
echo "Proper pairing rate: ${rate}%"
```

### Expected Rates

| Metric | Good | Marginal | Poor |
|--------|------|----------|------|
| Proper pair | > 90% | 80-90% | < 80% |
| Mapped | > 95% | 90-95% | < 90% |
| Singletons | < 5% | 5-10% | > 10% |

## GC Bias

GC content correlation with coverage.

### Picard CollectGcBiasMetrics

```bash
java -jar picard.jar CollectGcBiasMetrics \
    I=input.bam \
    O=gc_bias_metrics.txt \
    CHART=gc_bias_chart.pdf \
    S=gc_summary.txt \
    R=reference.fa
```

### deepTools computeGCBias

```bash
computeGCBias \
    -b input.bam \
    --effectiveGenomeSize 2913022398 \
    -g hg38.2bit \
    -o gc_bias.txt \
    --biasPlot gc_bias.pdf
```

### Interpret GC Bias

| Issue | Symptom |
|-------|---------|
| Under-representation | Low GC coverage drops |
| Over-representation | High GC coverage elevated |
| PCR bias | Strong correlation |

## Strand Balance

A balanced 0.48-0.52 forward/reverse ratio applies to WGS / WES / generic DNA-seq on autosomes. Expected to deviate for: stranded RNA-seq (deliberately strand-asymmetric -- verify with RSeQC `infer_experiment.py`), bisulfite (CT vs GA), small-RNA / strand-specific RNA-seq, and chrY/chrM regions. Per-chromosome strand imbalance >5% on autosomes is a field-convention rule of thumb (no single primary citation) — it picks up aligner artifacts; on chrX/chrY it suggests sex-mismatch.

### Calculate Strand Ratio

```bash
forward=$(samtools view -c -F 16 input.bam)
reverse=$(samtools view -c -f 16 input.bam)
echo "Forward: $forward"
echo "Reverse: $reverse"
ratio=$(echo "scale=4; $forward / $reverse" | bc)
echo "F/R ratio: $ratio"
```

### Check Strand Bias per Chromosome

```bash
for chr in chr1 chr2 chr3; do
    fwd=$(samtools view -c -F 16 input.bam $chr)
    rev=$(samtools view -c -f 16 input.bam $chr)
    echo "$chr: F=$fwd R=$rev ratio=$(echo "scale=2; $fwd/$rev" | bc)"
done
```

## Mapping Quality Distribution

### Extract MAPQ Distribution

```bash
samtools view input.bam | cut -f5 | sort -n | uniq -c | sort -k2 -n
```

### Calculate Mean MAPQ

```bash
samtools view input.bam | awk '{sum+=$5; count++} END {print "Mean MAPQ:", sum/count}'
```

### MAPQ Distribution Is Bimodal and Aligner-Specific

Mean MAPQ is misleading; distributions are bimodal (0 and aligner-max). For aligner-specific scales and "unique mapping" sentinels, see sam-bam-basics. The fraction of primary mapped reads at MAPQ >= 30 is a more informative summary than the mean.

## Chromosome Coverage Balance

### Calculate Per-Chromosome Coverage

```bash
samtools idxstats input.bam | awk '{print $1, $3/$2}' | head -25
```

### Check for Aneuploidy / Sex Chromosome Imbalance

Median-normalized per-autosome coverage (1.0 = expected diploid; 0.5 = monosomy/sex; 1.5 = trisomy):
```bash
samtools idxstats in.bam | awk '$2>0 && $1!~/^chr[XYM]|^GL|^KI|^chrUn|^chrEBV/ {
    cov[$1] = $3 / $2
}
END {
    n = asort(cov, sorted)
    med = sorted[int(n/2)+1]
    for (c in cov) printf "%s\t%.3f\n", c, cov[c]/med
}'
```

For full ancestry / contamination / relatedness checking, use `verifybamid2`, `somalier`, or `peddy` -- they account for population AFs, not just per-contig depth.

## Mismatch Rate

### Picard CollectAlignmentSummaryMetrics

```bash
java -jar picard.jar CollectAlignmentSummaryMetrics \
    I=input.bam \
    R=reference.fa \
    O=alignment_summary.txt
```

### Key Metrics

| Metric | Description | Good Value |
|--------|-------------|------------|
| PCT_PF_READS_ALIGNED | Mapped % | > 95% |
| PF_MISMATCH_RATE | Mismatches | < 1% |
| PF_INDEL_RATE | Indels | < 0.1% |
| STRAND_BALANCE | Strand ratio | ~0.5 |

## Comprehensive Validation Script

**Goal:** Run all key alignment QC checks in a single pass and generate a summary report.

**Approach:** Combine samtools flagstat, stats, idxstats, and strand counts into one script that outputs pass/warn/fail calls.

```bash
#!/bin/bash
BAM=$1
REF=$2
NAME=$(basename $BAM .bam)
OUTDIR=${3:-qc}

mkdir -p $OUTDIR

echo "=== Alignment Validation: $NAME ===" | tee $OUTDIR/report.txt

echo -e "\n--- Flagstat ---" | tee -a $OUTDIR/report.txt
samtools flagstat $BAM | tee -a $OUTDIR/report.txt

echo -e "\n--- Mapping Rate ---" | tee -a $OUTDIR/report.txt
mapped=$(samtools view -c -F 4 $BAM)
total=$(samtools view -c $BAM)
rate=$(echo "scale=2; $mapped / $total * 100" | bc)
echo "Mapping rate: ${rate}%" | tee -a $OUTDIR/report.txt

echo -e "\n--- Proper Pairing ---" | tee -a $OUTDIR/report.txt
proper=$(samtools view -c -f 2 $BAM)
pair_rate=$(echo "scale=2; $proper / $mapped * 100" | bc)
echo "Proper pairing: ${pair_rate}%" | tee -a $OUTDIR/report.txt

echo -e "\n--- Insert Size ---" | tee -a $OUTDIR/report.txt
samtools stats $BAM | grep "insert size average" | tee -a $OUTDIR/report.txt

echo -e "\n--- Strand Balance ---" | tee -a $OUTDIR/report.txt
fwd=$(samtools view -c -F 16 $BAM)
rev=$(samtools view -c -f 16 $BAM)
strand_ratio=$(echo "scale=3; $fwd / $rev" | bc)
echo "Forward: $fwd, Reverse: $rev, Ratio: $strand_ratio" | tee -a $OUTDIR/report.txt

echo -e "\n--- Chromosome Coverage ---" | tee -a $OUTDIR/report.txt
samtools idxstats $BAM | head -25 | tee -a $OUTDIR/report.txt

echo -e "\nReport: $OUTDIR/report.txt"
```

## Python Validation Module

A skeleton; full implementation is in `examples/validate_alignment.py`:
```python
import pysam

class AlignmentValidator:
    def __init__(self, bam_file):
        self.bam = pysam.AlignmentFile(bam_file, 'rb')

    def report(self, sample_size=100000):
        # Sample reads, compute mapping rate, proper-pair rate, MAPQ dist, strand balance
        # See examples/validate_alignment.py for full implementation
        ...
```

The first-N-reads sampling pattern is biased toward chr1 (different GC content and complexity than chrM/chrX/chrY/alt contigs). For unbiased per-chromosome statistics, use `samtools view -s 42.01 input.bam` (the `INT.FRAC` form uses `INT` as the seed; specify an explicit nonzero seed so the subsample is documented and consistent across paired runs) instead of head-of-file iteration.

## Quality Thresholds Summary

| Metric | Good | Warning | Fail |
|--------|------|---------|------|
| Mapping rate | > 95% | 90-95% | < 90% |
| Proper pairing | > 90% | 80-90% | < 80% |
| Duplicate rate (assay-specific) | see bam-statistics decision table | -- | -- |
| Strand balance | 0.48-0.52 | 0.45-0.55 | Outside |
| Mean MAPQ | > 40 | 30-40 | < 30 |
| GC bias | < 1.2x | 1.2-1.5x | > 1.5x (field-convention bands; Picard CollectGcBiasMetrics does not prescribe specific cutoffs) |

## Related Skills

- bam-statistics - Per-assay metric thresholds, depth/coverage tools, mosdepth
- alignment-filtering - Aligner-specific MAPQ thresholds (canonical home)
- duplicate-handling - Library-aware dedup decisions
- sam-bam-basics - MAPQ-by-aligner table
- chip-seq/chipseq-qc - ChIP-specific QC (FRiP, NSC, RSC)
<!-- END FILE: alignment-files/alignment-validation/SKILL.md -->

## 子目录：alignment-files/bam-statistics

<!-- BEGIN FILE: alignment-files/bam-statistics/SKILL.md -->
---
name: bio-bam-statistics
description: Generate alignment statistics using samtools flagstat, stats, depth, coverage, and mosdepth. Use when assessing alignment quality, calculating coverage, or generating QC reports.
tool_type: cli
primary_tool: samtools
---

## Version Compatibility

Reference examples tested with: pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# BAM Statistics

**"Get alignment statistics and coverage from my BAM file"** -> Generate read counts, mapping rates, per-chromosome statistics, depth profiles, and coverage summaries.
- CLI: `samtools flagstat`, `samtools stats`, `samtools depth`, `samtools coverage` (samtools)
- Python: `pysam.AlignmentFile` with `pileup()` and `get_index_statistics()` (pysam)

Generate alignment statistics using samtools and pysam.

## Quick Summary Commands

| Question | Best tool | Why |
|----------|-----------|-----|
| Quick read counts by FLAG category | `samtools flagstat` | Fast; counts secondary+supp in totals |
| Per-chromosome counts | `samtools idxstats` | Fast (needs index); **counts secondary+supp** |
| Insert size, MAPQ, error, GC | `samtools stats -r ref.fa` | Comprehensive; feeds MultiQC |
| Per-position depth (small region) | `samtools depth` or pysam pileup | Slow on full genome |
| Per-position depth (genome-wide) | **`mosdepth`** | 3-10x faster than `samtools depth` |
| Per-region coverage (BED) | `mosdepth --by regions.bed` | Production default |
| Coverage histogram / cumulative | `mosdepth -t 4 --no-per-base` | Single-pass histogram |
| Breadth at depth thresholds | `mosdepth --thresholds 1,10,30,100` | Standard exome QC |
| Targeted enrichment QC | `picard CollectHsMetrics` | PCT_OFF_BAIT, FOLD_80_BASE_PENALTY, AT/GC dropout |
| Cross-sample contamination | `verifybamid2`, `somalier` | FREEMIX < 0.01 expected |

### What Each Tool Counts (and Doesn't)

| Counting category | flagstat | stats | idxstats |
|-------------------|----------|-------|----------|
| Primary alignments | `in total` minus supp | `raw total sequences` | mapped column |
| Secondary | `secondary` line | filtered out | counted in mapped |
| Supplementary | `supplementary` line | filtered out | counted in mapped |
| Mapping rate denominator | total *including* supp | primary only | mapped+unmapped |

For long-read data where one read produces many supplementary alignments, the senior cross-check:
```
input_read_count = flagstat_total - secondary - supplementary
                 = stats_raw_total_sequences
```
Reports of "the file has 1.2M reads" where the input was actually 800k with 400k supplementary chimeric splits trace to flagstat misinterpretation.

## samtools flagstat

Fast summary of alignment flags.

```bash
samtools flagstat input.bam
```

Output:
```
10000000 + 0 in total (QC-passed reads + QC-failed reads)
9950000 + 0 primary
0 + 0 secondary
50000 + 0 supplementary
0 + 0 duplicates
0 + 0 primary duplicates
9800000 + 0 mapped (98.00% : N/A)
9750000 + 0 primary mapped (97.99% : N/A)
9950000 + 0 paired in sequencing
4975000 + 0 read1
4975000 + 0 read2
9700000 + 0 properly paired (97.49% : N/A)
9720000 + 0 with itself and mate mapped
30000 + 0 singletons (0.30% : N/A)
15000 + 0 with mate mapped to a different chr
10000 + 0 with mate mapped to a different chr (mapQ>=5)
```
(samtools 1.13+ adds the `primary`, `primary duplicates`, and `primary mapped` lines shown above.)

### Multi-threaded
```bash
samtools flagstat -@ 4 input.bam
```

### Output to File
```bash
samtools flagstat input.bam > flagstat.txt
```

## samtools idxstats

Per-chromosome read counts (requires index).

```bash
samtools idxstats input.bam
```

Output format: `chrom length mapped unmapped`
```
chr1    248956422    5000000    1000
chr2    242193529    4800000    800
chrM    16569        50000      100
*       0            0          150000
```

### Parse idxstats
```bash
# Total mapped reads
samtools idxstats input.bam | awk '{sum += $3} END {print sum}'

# Mitochondrial percentage
samtools idxstats input.bam | awk '
    /^chrM/ {mt = $3}
    {total += $3}
    END {print mt/total*100 "% mitochondrial"}'
```

## samtools stats

Comprehensive statistics including insert size, base quality, and more.

```bash
samtools stats input.bam > stats.txt
```

### View Summary Numbers
```bash
samtools stats input.bam | grep "^SN"
```

Key summary fields:
- `raw total sequences` - Total reads
- `reads mapped` - Mapped reads
- `reads mapped and paired` - Properly paired
- `insert size average` - Mean insert size
- `insert size standard deviation` - Insert size spread
- `average length` - Mean read length
- `error rate` - Mismatch rate

### Generate Plots (with plot-bamstats)
```bash
samtools stats input.bam > stats.txt
plot-bamstats -p plots/ stats.txt
```

### Stats for Specific Region
```bash
samtools stats input.bam chr1:1000000-2000000 > region_stats.txt
```

## samtools depth

Per-position read depth.

### Basic Depth
```bash
samtools depth input.bam > depth.txt
```

Output: `chrom position depth`

### Depth at Specific Positions
```bash
samtools depth -r chr1:1000-2000 input.bam
```

### Include Zero-Depth Positions
```bash
samtools depth -a input.bam > depth_with_zeros.txt
```

### Maximum Depth Cap (Critical Trap)
```bash
# samtools mpileup historically capped depth at 8000 per position -- the cap was in mpileup, not depth.
# samtools depth -d/--max-depth is deprecated in 1.13+ (silently ignored).
# For mpileup, raise the cap explicitly when working with deep targeted/amplicon data:
samtools mpileup -d 1000000 -f ref.fa input.bam
```

Pipelines that historically break the 8000 mpileup cap: targeted oncology hotspots (5000-50000x), mitochondrial DNA (small genome, large read share), amplicon viral (ARTIC: 1000-100000x per amplicon), UMI-deduped capture (14000-17000x post-collapse), highly expressed transcripts (rRNA, mt-RNA).

### Overlapping Pair Correction
```bash
# When fragment length < 2 * read_length, R1 and R2 overlap.
# Default samtools depth double-counts overlap; -s deducts:
samtools depth -s input.bam
```
Without `-s`, doubled support inflates somatic VAFs at sites covered by overlapping pairs (especially in fragmented samples: FFPE, cfDNA). `mosdepth` does not double-count overlap. `samtools mpileup` and `bcftools mpileup` both enable overlap detection by default; pass `-x` to disable (long form `--disable-overlap-removal` in samtools, `--ignore-overlaps` in bcftools).

### mosdepth (Modern Default)
```bash
mosdepth -t 4 sample input.bam                                                       # genome-wide per-base
mosdepth -t 4 --by exome.bed --thresholds 1,10,20,30,100 --no-per-base sample input.bam   # exome QC
mosdepth -t 4 --quantize 0:1:10:100: sample input.bam                                # CNV-style bands
mosdepth -t 4 -f ref.fa sample input.cram                                            # CRAM with reference
```
`mosdepth` excludes unmapped, secondary, QC-fail, and duplicate reads by default (`--flag 1796`); supplementary reads are NOT excluded (use `--flag 3844` to drop them too). Configurable via `--flag`. Memory ~ 4 bytes x longest chrom (1 GB for human chr1, 12+ GB for axolotl). Does not honor base quality; use `samtools depth -q INT` if needed.

### Depth from BED Regions
```bash
samtools depth -b regions.bed input.bam
```

### Calculate Mean Depth
```bash
samtools depth input.bam | awk '{sum += $3; n++} END {print sum/n}'
```

## samtools coverage

Per-chromosome or per-region coverage statistics (faster than depth).

```bash
samtools coverage input.bam
```

Output columns:
- `#rname` - Reference name
- `startpos` - Start position
- `endpos` - End position
- `numreads` - Number of reads
- `covbases` - Bases with coverage
- `coverage` - Percentage of bases covered
- `meandepth` - Mean depth
- `meanbaseq` - Mean base quality
- `meanmapq` - Mean mapping quality

### Coverage for Specific Region
```bash
samtools coverage -r chr1:1000000-2000000 input.bam
```

### Coverage from BED
```bash
samtools coverage -b regions.bed input.bam
```

### Histogram Output
```bash
samtools coverage -m input.bam
```

## pysam Python Alternative

### Count Reads
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    total = mapped = paired = proper = 0
    for read in bam:
        total += 1
        if not read.is_unmapped:
            mapped += 1
        if read.is_paired:
            paired += 1
        if read.is_proper_pair:
            proper += 1

    print(f'Total: {total}')
    print(f'Mapped: {mapped} ({mapped/total*100:.1f}%)')
    print(f'Properly paired: {proper} ({proper/paired*100:.1f}%)')
```

### Per-Chromosome Counts
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for stat in bam.get_index_statistics():
        print(f'{stat.contig}: {stat.mapped} mapped, {stat.unmapped} unmapped')
```

### Calculate Depth at Position
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for pileup in bam.pileup('chr1', 1000000, 1000001):
        print(f'Position {pileup.pos}: depth {pileup.n}')
```

### Mean Depth in Region
```python
import pysam

def mean_depth(bam_path, chrom, start, end):
    depths = []
    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for pileup in bam.pileup(chrom, start, end, truncate=True):
            depths.append(pileup.n)

    if depths:
        return sum(depths) / len(depths)
    return 0

depth = mean_depth('input.bam', 'chr1', 1000000, 2000000)
print(f'Mean depth: {depth:.1f}x')
```

### Coverage Statistics

**Goal:** Compute coverage breadth and depth for a genomic region from a BAM file.

**Approach:** Iterate pileup columns in the region, count covered positions and accumulate depth, then derive percentages and means.

**Reference (pysam 0.22+):**
```python
import pysam

def coverage_stats(bam_path, chrom, start, end):
    covered = 0
    total_depth = 0

    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for pileup in bam.pileup(chrom, start, end, truncate=True):
            covered += 1
            total_depth += pileup.n

    length = end - start
    pct_covered = covered / length * 100
    mean_depth = total_depth / length if length > 0 else 0

    return {
        'length': length,
        'covered_bases': covered,
        'pct_covered': pct_covered,
        'mean_depth': mean_depth
    }

stats = coverage_stats('input.bam', 'chr1', 1000000, 2000000)
print(f'Coverage: {stats["pct_covered"]:.1f}%')
print(f'Mean depth: {stats["mean_depth"]:.1f}x')
```

### Insert Size Distribution

**Goal:** Compute the insert size distribution to assess library preparation quality.

**Approach:** Iterate properly paired read1 records, accumulate template lengths into a Counter, then compute summary statistics.

**Reference (pysam 0.22+):**
```python
import pysam
from collections import Counter

insert_sizes = Counter()

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for read in bam:
        if read.is_proper_pair and read.is_read1 and read.template_length > 0:
            insert_sizes[read.template_length] += 1

sizes = list(insert_sizes.keys())
mean_insert = sum(s * c for s, c in insert_sizes.items()) / sum(insert_sizes.values())
print(f'Mean insert size: {mean_insert:.0f}')
print(f'Min: {min(sizes)}, Max: {max(sizes)}')
```

## Quick Reference

| Task | Command |
|------|---------|
| Quick counts | `samtools flagstat input.bam` |
| Per-chrom counts | `samtools idxstats input.bam` |
| Full stats | `samtools stats input.bam` |
| Coverage summary | `samtools coverage input.bam` |
| Per-position depth | `samtools depth input.bam` |
| Mean depth | `samtools depth input.bam \| awk '{sum+=$3;n++}END{print sum/n}'` |

## QC Thresholds Are Assay-Specific

A single "mapping rate > 95%" rule rejects valid ATAC, ChIP, RNA-seq, metagenomics, and aDNA samples. The threshold question is "is this rate normal for this assay?" not "is this rate above 95%?"

| Metric | WGS PCR-free | WGS PCR | WES | Targeted panel | Deep panel (UMI) | RNA-seq | scRNA (10x) | ATAC | ChIP | Long-read | aDNA |
|--------|--------------|---------|-----|----------------|------------------|---------|-------------|------|------|-----------|------|
| Mapping rate | >99% | >98% | >95% | >95% | >95% | >90% | >70% | >50% | >60% | >95% | 1-50% |
| Duplicate rate | <5% | 5-15% | 20-50% | 20-50% | 50-90% pre-consensus | (skip) | (use UMI) | 10-30% | 5-30% | n/a | 20-60% |
| Proper pair rate | >95% | >95% | >85% | >80% | >80% | >70% | n/a | >50% | >70% | n/a | >60% |
| Mean MAPQ | bimodal at 0/60 | bimodal | bimodal | bimodal | bimodal | bimodal incl 255 (STAR) | 0/1/3/255 | 30-55 | 30-55 | 30-50 | 20-40 |
| Mt fraction | 0.1-2% | 0.1-2% | <1% | <0.1% | <0.1% | varies | varies | **<10% (Omni-ATAC goal; original Buenrostro-2013 libraries were often majority-mito)** | <2% | n/a | varies |

Mean MAPQ is misleading; the distribution is bimodal (0 and aligner-max). The fraction at MAPQ >= 30 is more informative:
```bash
samtools view -c -F 2308 -q 30 in.bam   # primary, mapped, MAPQ>=30
samtools view -c -F 2308 in.bam          # primary, mapped (denominator)
# For STAR/STARsolo, use -q 255 instead of -q 30 (255 is the unique-mapping sentinel)
```

## What Flagstat Does Not Reveal

A 99% flagstat mapping rate does NOT mean the data is usable. Common false-positive scenarios:

1. **Adapter readthrough**: short fragments (insert < 2 * read_length) sequence into adapter; aligners soft-clip the adapter portion and flag the read as MAPPED. Detect:
   ```bash
   samtools stats input.bam | grep "bases soft-clipped"   # >5% suggests adapter contamination
   ```
2. **Off-target enrichment** (capture/WES): detect via `picard CollectHsMetrics` PCT_OFF_BAIT or PCT_SELECTED_BASES.
3. **Low-complexity pile-up**: telomere/centromere reads mass at MAPQ-0; counted as mapped but useless. Detect via MAPQ distribution.
4. **Cross-sample contamination**: detect via `verifybamid2` or `somalier` (FREEMIX > 1% degrades somatic calling; > 5% breaks germline calling).
5. **Wrong reference build**: a BAM aligned to GRCh37 viewed against GRCh38 looks fine to flagstat but produces nonsense pileups. Compare `@SQ M5:` from BAM header with `samtools dict ref.fa` -- see alignment-validation.

## Insert Size Caveats

`samtools stats` reports the IS section only for FR-oriented properly paired reads. So:
- Mate-pair libraries (RF orientation): IS section *empty* -- proper-pair flag not set for RF
- ATAC-seq: bimodal/multimodal expected (nucleosome ladder ~50/~180/~370 bp). Unimodal suggests poor transposition.
- RNA-seq: TLEN includes intron span -- mean meaningless
- Bisulfite (PBAT): orientation reversed; samtools may not flag proper pair

## Related Skills

- sam-bam-basics - View alignment files; aligner-aware MAPQ semantics
- alignment-indexing - idxstats requires index; secondary+supp counted
- alignment-validation - Insert size by library, contamination, sample-swap detection
- duplicate-handling - Library-aware duplicate rate expectations
- alignment-filtering - Filter before stats
- sequence-io/sequence-statistics - FASTA/FASTQ statistics
<!-- END FILE: alignment-files/bam-statistics/SKILL.md -->

## 子目录：alignment-files/duplicate-handling

<!-- BEGIN FILE: alignment-files/duplicate-handling/SKILL.md -->
---
name: bio-duplicate-handling
description: Mark and remove PCR/optical duplicates using samtools fixmate and markdup. Use when preparing alignments for variant calling or when duplicate reads would bias analysis.
tool_type: cli
primary_tool: samtools
---

## Version Compatibility

Reference examples tested with: picard 3.1+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Duplicate Handling

**"Remove PCR duplicates from my BAM file"** -> Mark or remove duplicate reads using the fixmate-sort-markdup pipeline to prevent duplicate bias in variant calling.
- CLI: `samtools fixmate`, `samtools markdup` (samtools)
- Python: `pysam.fixmate()`, `pysam.markdup()` (pysam)

Mark and remove PCR/optical duplicates using samtools.

## Why Remove Duplicates?

PCR duplicates are identical copies of the same original molecule, created during library preparation. They inflate coverage, bias allele frequencies, and create false positive variant calls. Optical duplicates are flowcell-proximity artifacts: on unpatterned flowcells they arise when the imaging software splits one cluster into two adjacent calls; on patterned flowcells (NovaSeq, NovaSeq X, NextSeq 1000/2000, HiSeq X/4000) the dominant source is ExAmp (exclusion-amplification) "pad-hopping", where a library molecule re-seeds a nearby nanowell.

## When to Mark Duplicates -- and When NOT To

Standard `samtools markdup` is the right tool for some assays and actively harmful for others. The decision is assay-driven:

| Assay | Standard markdup? | Recommended approach |
|-------|------------------|----------------------|
| Germline WGS / WES (PCR or PCR-free) | YES | `samtools markdup` (PCR-free still has ~0.5% optical duplicates on patterned flowcells) |
| Somatic tumor/normal (no UMI) | YES | Same |
| Exome / target capture | YES (20-50% expected) | `samtools markdup` |
| ChIP-seq | **MARK, do not remove** | Then use peak caller's auto-dup logic (`macs3 --keep-dup auto`) |
| CUT&RUN / CUT&Tag | MARK, do not remove | Same |
| ATAC-seq | YES, BEFORE Tn5 +4/-5 shift | Then shift coords for footprinting |
| Bulk RNA-seq (no UMIs) | **NO** | Duplicates are biological at highly-expressed loci; removing them biases DE proportional to expression |
| Bulk RNA-seq (with UMIs) | NO | umi_tools dedup |
| scRNA (10x, STARsolo, drop-seq) | **NO** | umi_tools dedup with CB+UB tags, or rely on Cell Ranger UMI counts |
| ctDNA / liquid biopsy / deep panel (UMI) | NO | fgbio GroupReadsByUmi -> CallDuplexConsensusReads |
| Twist / IDT / Roche UMI capture | NO | fgbio or Picard UmiAwareMarkDuplicatesWithMateCigar |
| Amplicon / hotspot panel (no UMI) | **NO** | Every read is a "duplicate" by coordinate; markdup erases the dataset. Use `samtools ampliconclip` instead -- see alignment-amplicon-clipping. |
| Amplicon / hotspot panel (UMI) | NO | fgbio consensus |
| Long-read native (ONT, PacBio HiFi unamplified) | NO | No PCR step; markdup is meaningless |
| PacBio HiFi amplicon | YES (rare) | `pbmarkdup` |
| Ancient DNA (aDNA) | YES + mapDamage | Run markdup, then mapDamage `--rescale` before variant calling |
| Microbiome 16S/ITS | NO | Read counts encode community structure |

If the BAM came from 10x Cell Ranger / STARsolo and `samtools markdup` produces a 50-95% duplicate rate, it is the wrong tool, not a bug.

## Tool Selection: markdup vs Picard vs UMI-aware

| Tool | Speed | Threading | Optical | UMI | Notes |
|------|-------|-----------|---------|-----|-------|
| `samtools markdup` | Fast | Yes | Yes (`-d`) | Limited (`--barcode-tag` exact-match) | Fast production choice (nf-core/sarek defaults to GATK MarkDuplicates) |
| `picard MarkDuplicates` | Slow | No | Yes | UmiAware variant (BETA, transcriptome bug) | GATK Best Practices reference |
| `biobambam2 bammarkduplicates2` | Fastest | Yes | Yes | No | Sanger / 1KGP pipelines |
| `samblaster` | Streaming, fast | No | Optional | No | Pipe directly from aligner; no name sort |
| `sambamba markdup` | Fast | Yes | Yes | No | Less actively maintained |
| `fgbio GroupReadsByUmi` + `CallMolecularConsensusReads` | Fast | Yes | n/a | **Best UMI tool** | Graph-based; supports duplex |
| `umi_tools dedup` | Slow | No | n/a | Yes (mature) | Reference for scRNA / bulk UMI |
| `pbmarkdup` | Fast | Yes | n/a | n/a | PacBio HiFi amplicons only |

Picard `UmiAwareMarkDuplicatesWithMateCigar` is BETA and has known bugs on transcriptome-aligned BAMs (silently keeps duplicates). Avoid for RNA-seq UMIs.

## Optical Distance Is Platform-Specific

`samtools markdup` default is `-d 0`, meaning **optical-duplicate detection is disabled by default**. Set explicitly per platform:

| Platform | `-d` value | Rationale |
|----------|-----------|-----------|
| HiSeq 2000/2500 (random) | 100 | Picard historic default |
| HiSeq 3000/4000/X (patterned) | 2500 | Patterned tile size larger |
| NovaSeq 6000 (patterned) | 2500 | Same as HiSeq X |
| NovaSeq X (10B) | 2500 | Patterned; same starting point as NovaSeq 6000 |
| NextSeq 1000/2000 (patterned) | 2500 | ExAmp duplicates span larger pixel distances |
| MiSeq, NextSeq 500/550 | 100 | Smaller / unpatterned |
| Element AVITI, MGI / DNBseq | Custom regex | Different read-name format -- supply via `--read-coords` |

```bash
samtools markdup -d 2500 -f stats.txt input.bam marked.bam

# Count optical (SQ) vs library/PCR (LB) duplicates. The dt:Z:SQ/LB tag is
# emitted automatically because -d is set (it is not produced by -t, which
# instead adds a 'do' tag carrying the original read's name).
samtools view -f 1024 marked.bam | grep -o 'dt:Z:[A-Z][A-Z]' | sort | uniq -c
```

Setting `-d 2500` on a HiSeq run does no harm. Forgetting `-d 2500` on NovaSeq systematically under-marks optical duplicates and overestimates library complexity.

## Multi-Library Pooled Marking

Without `--use-read-groups`, multi-library BAMs systematically over-mark: independent molecules from different libraries with the same coordinates get wrongly flagged as PCR duplicates. With `--use-read-groups`, RG tags must also match for two reads to be a duplicate (verify availability with `samtools markdup --help`):
```bash
samtools markdup --use-read-groups -d 2500 in.bam out.bam
```

samtools `--use-read-groups` keys on RG ID; Picard's library-aware behavior keys on the LB tag (allowing dedup across multiple lanes of the same library). For multi-lane single-library BAMs, Picard MarkDuplicates with `READ_NAME_REGEX` is closer to canonical.

## Duplicate Marking Workflow

**Goal:** Mark PCR/optical duplicates so they can be excluded from downstream variant calling and coverage analysis.

**Approach:** Name-sort, add mate tags with fixmate, coordinate-sort, then run markdup. The pipeline version avoids intermediate files.

**Reference (samtools 1.19+):**
```bash
# 1. Sort by name (required for fixmate)
samtools sort -n -o namesort.bam input.bam

# 2. Add mate information with fixmate
samtools fixmate -m namesort.bam fixmate.bam

# 3. Sort by coordinate (required for markdup)
samtools sort -o coordsort.bam fixmate.bam

# 4. Mark duplicates
samtools markdup coordsort.bam marked.bam

# 5. Index result
samtools index marked.bam
```

### Pipeline Version (Optimized)
```bash
# collate is faster than sort -n; -u/-O between piped tools skips BGZF round-trips
samtools collate -O -u input.bam tmpdir/collate | \
    samtools fixmate -m -u - - | \
    samtools sort -u -@ 4 -T tmpdir/sort - | \
    samtools markdup -@ 4 -d 2500 --use-read-groups \
        -f markdup_stats.txt - marked.bam

samtools index marked.bam
```

This is ~30% faster than `sort -n | fixmate | sort | markdup` on typical 30x WGS.

**Critical pitfall:** `samtools markdup` requires `ms` (mate score, lowercase) and `MC` (mate CIGAR) tags from `fixmate -m`. A re-sort that loses aux tags via Python round-trip silently produces a markdup output that marks almost nothing. If duplicate counts look implausibly low, verify `MC:Z:` is present in the input to markdup.

## samtools fixmate

Adds mate information required by markdup. Must be run on name-sorted BAM.

### Basic Usage
```bash
samtools fixmate namesorted.bam fixmate.bam
```

### Add Mate Score Tag (-m)
```bash
# Required for markdup to work correctly
samtools fixmate -m namesorted.bam fixmate.bam
```

### Multi-threaded
```bash
samtools fixmate -m -@ 4 namesorted.bam fixmate.bam
```

### Remove Secondary/Unmapped
```bash
samtools fixmate -r -m namesorted.bam fixmate.bam
```

## samtools markdup

Marks or removes duplicate alignments. Requires coordinate-sorted BAM with mate tags from fixmate.

### Mark Duplicates (Keep in File)
```bash
samtools markdup input.bam marked.bam
```

### Remove Duplicates
```bash
samtools markdup -r input.bam deduped.bam
```

### Output Statistics
```bash
samtools markdup -s input.bam marked.bam 2> markdup_stats.txt
```

### Optical Duplicate Distance
```bash
# Default -d 0 disables optical detection. Set per platform; see decision table above.
samtools markdup -d 2500 input.bam marked.bam   # NovaSeq / patterned
samtools markdup -d 100 input.bam marked.bam    # HiSeq / random
```

### Multi-threaded
```bash
samtools markdup -@ 4 input.bam marked.bam
```

### Write Stats to File
```bash
samtools markdup -f stats.txt input.bam marked.bam
```

## Duplicate Statistics

### Check Duplicate Rate
```bash
samtools flagstat marked.bam
# Look for "duplicates" line
```

### Count Duplicates
```bash
# Count reads with duplicate flag
samtools view -c -f 1024 marked.bam
```

### Percentage Duplicates
```bash
total=$(samtools view -c marked.bam)
dups=$(samtools view -c -f 1024 marked.bam)
echo "scale=2; $dups * 100 / $total" | bc
```

## pysam Python Alternative

### Full Pipeline
```python
import pysam

# Sort by name
pysam.sort('-n', '-o', 'namesort.bam', 'input.bam')

# Fixmate
pysam.fixmate('-m', 'namesort.bam', 'fixmate.bam')

# Sort by coordinate
pysam.sort('-o', 'coordsort.bam', 'fixmate.bam')

# Mark duplicates
pysam.markdup('coordsort.bam', 'marked.bam')

# Index
pysam.index('marked.bam')
```

### Check Duplicate Flag
```python
import pysam

with pysam.AlignmentFile('marked.bam', 'rb') as bam:
    total = 0
    duplicates = 0
    for read in bam:
        total += 1
        if read.is_duplicate:
            duplicates += 1

    print(f'Total: {total}')
    print(f'Duplicates: {duplicates}')
    print(f'Rate: {duplicates/total*100:.2f}%')
```

### Filter Out Duplicates
```python
import pysam

with pysam.AlignmentFile('marked.bam', 'rb') as infile:
    with pysam.AlignmentFile('nodup.bam', 'wb', header=infile.header) as outfile:
        for read in infile:
            if not read.is_duplicate:
                outfile.write(read)
```

### Production Tools, Not Hand-Rolled

For real BAMs, always use a production marker. A naive Python implementation keyed on (chrom, pos, strand) ignores 5' position correction for soft clips, ignores library/RG, treats optical = PCR, and mis-handles supplementary alignments. The result is silently wrong duplicate marks. Use `samtools markdup`, Picard, or fgbio depending on assay (see decision tables above).

## Alternative: From Aligner

Some aligners can mark duplicates directly during streaming:

### BWA-MEM2 with samblaster
```bash
bwa-mem2 mem ref.fa R1.fq R2.fq | \
    samblaster | \
    samtools sort -o marked.bam
```

### Picard MarkDuplicates
```bash
java -jar picard.jar MarkDuplicates \
    I=input.bam \
    O=marked.bam \
    M=metrics.txt \
    OPTICAL_DUPLICATE_PIXEL_DISTANCE=2500
```

## UMI-Aware Deduplication

For UMI libraries (10x scRNA, ctDNA panels, Twist/IDT/Roche UMI capture), naive markdup destroys information. Use UMI-aware tools:

```bash
# 10x / scRNA -- group by cell barcode + UMI
umi_tools dedup --stdin=cellranger_possorted.bam --stdout=dedup.bam \
    --extract-umi-method=tag --umi-tag=UB --cell-tag=CB \
    --per-cell --method=directional

# Bulk UMI / ctDNA -- consensus calling (best practice for low-VAF detection)
fgbio AnnotateBamWithUmis -i raw.bam -f umi.fastq -o annotated.bam
fgbio GroupReadsByUmi -i annotated.bam -o grouped.bam --strategy=adjacency --edits=1
fgbio CallMolecularConsensusReads -i grouped.bam -o consensus.bam --min-reads=1
# Or for duplex (xGen-Prism, NEBNext duplex):
fgbio CallDuplexConsensusReads -i grouped.bam -o duplex.bam --min-reads 1 1 0
```

`--method=directional` is the default and correct -- do not use `--method=unique`, which treats single-base UMI errors as different molecules. `samtools markdup --barcode-tag RX` (UMI/barcode handling added in samtools 1.16) does exact-match UMI grouping; adequate for IDT xGen Duplex but insufficient for single-UMI applications where 1-edit errors are common.

## Quick Reference

| Task | Command |
|------|---------|
| Full workflow | `sort -n \| fixmate -m \| sort \| markdup` |
| Mark duplicates | `samtools markdup in.bam out.bam` |
| Remove duplicates | `samtools markdup -r in.bam out.bam` |
| Count duplicates | `samtools view -c -f 1024 marked.bam` |
| View non-duplicates | `samtools view -F 1024 marked.bam` |
| Get stats | `samtools markdup -s in.bam out.bam` |

## Duplicate FLAG

| Flag | Value | Meaning |
|------|-------|---------|
| 0x400 | 1024 | PCR or optical duplicate |

### Filter Commands
```bash
# View only duplicates
samtools view -f 1024 marked.bam

# View non-duplicates only
samtools view -F 1024 marked.bam

# Count non-duplicates
samtools view -c -F 1024 marked.bam
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `mate not found` | Input not name-sorted | Run `samtools sort -n` first |
| `no MC tag` | fixmate not run with -m | Re-run fixmate with `-m` flag |
| `not coordinate sorted` | Input to markdup not sorted | Run `samtools sort` after fixmate |

## Lossy Operations

`samtools markdup -r` (remove duplicates) is irreversible -- the records are dropped. Default to marking, not removing; downstream tools can filter on FLAG 1024. Removing pre-emptively destroys data needed for re-running QC, library complexity estimation, or switching dedup strategies.

## Related Skills

- alignment-sorting - Sort by name/coordinate; collate vs sort -n decision
- alignment-filtering - Filter duplicates from output
- alignment-amplicon-clipping - Use ampliconclip instead of markdup for amplicon panels
- bam-statistics - Check duplicate rates with flagstat / mosdepth
- variant-calling/variant-calling - Standard variant calling expects deduped BAMs
- read-qc/quality-reports - Pre-alignment QC including UMI extraction
<!-- END FILE: alignment-files/duplicate-handling/SKILL.md -->

## 子目录：alignment-files/pileup-generation

<!-- BEGIN FILE: alignment-files/pileup-generation/SKILL.md -->
---
name: bio-pileup-generation
description: Generate pileup data for variant calling using samtools mpileup and pysam. Use when preparing data for variant calling, analyzing per-position read data, or calculating allele frequencies.
tool_type: cli
primary_tool: samtools
---

## Version Compatibility

Reference examples tested with: bcftools 1.19+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Pileup Generation

Generate pileup data for variant calling and position-level analysis.

**"Generate pileup from BAM"** -> Produce per-position read summaries showing depth, bases, and qualities.
- CLI: `samtools mpileup -f ref.fa input.bam`
- Python: `bam.pileup(chrom, start, end)` (pysam)

**"Count alleles at a position"** -> Extract per-base read support at a specific genomic coordinate.
- Python: iterate `pileup_column.pileups` and count bases (pysam)

## What is Pileup?

Pileup shows all reads covering each position in the reference, used for:
- Variant calling (with bcftools)
- Coverage analysis
- Allele frequency calculation
- SNP/indel detection

## samtools mpileup vs bcftools mpileup (Deprecation)

`samtools mpileup -g/-u` (BCF output for variant calling) was **deprecated in samtools 1.9 and removed in 1.15** (the option no longer exists; the usage/manpage directs users to `bcftools mpileup`) -- the genotype-likelihood code now lives in `bcftools mpileup`, which keeps mpileup logic versioned alongside `bcftools call` and avoids version-skew bugs.

| Use case | Recommended tool |
|----------|------------------|
| Quick allele counts at known sites | `samtools mpileup` or pysam pileup |
| Germline variant calling (small genomes, simple cohorts) | `bcftools mpileup` -> `bcftools call` |
| Germline WGS / WES production | DeepVariant or HaplotypeCaller (not mpileup) |
| Somatic SNV/indel | Mutect2 / VarDict / VarScan2 (direct from BAM) |
| Long-read small variants | clair3 / DeepVariant ONT (direct from BAM) |
| Long-read SV | Sniffles / cuteSV (direct from BAM) |
| Ultra-low-frequency (ctDNA / MRD) | fgbio consensus -> `bcftools call` or hot-spot Mutect2 |
| Per-position allele counts (custom) | pysam pileup |

`samtools mpileup` (without `-g`) is still the standard tool for human-readable per-position read summaries.

### Basic Pileup
```bash
samtools mpileup -f reference.fa input.bam > pileup.txt
```

### Pileup Specific Region
```bash
samtools mpileup -f reference.fa -r chr1:1000000-2000000 input.bam
```

### Regions from BED
```bash
samtools mpileup -f reference.fa -l targets.bed input.bam
```

### Multiple BAM Files
```bash
samtools mpileup -f reference.fa sample1.bam sample2.bam sample3.bam > pileup.txt
```

## Output Format

Text pileup format (6 columns per sample):
```
chr1    1000    A    15    ...............    FFFFFFFFFFF
chr1    1001    T    12    ............      FFFFFFFFFFFF
```

| Column | Description |
|--------|-------------|
| 1 | Chromosome |
| 2 | Position (1-based) |
| 3 | Reference base |
| 4 | Read depth |
| 5 | Read bases |
| 6 | Base qualities |

### Read Bases Encoding

| Symbol | Meaning |
|--------|---------|
| `.` | Match on forward strand |
| `,` | Match on reverse strand |
| `ACGT` | Mismatch (uppercase = forward) |
| `acgt` | Mismatch (lowercase = reverse) |
| `^Q` | Start of read (Q = MAPQ as ASCII) |
| `$` | End of read |
| `+NNN` | Insertion of N bases |
| `-NNN` | Deletion of N bases |
| `*` | Deleted base |
| `>` / `<` | Reference skip (intron) |

## Quality Filtering Options

### Minimum Mapping Quality
```bash
samtools mpileup -f reference.fa -q 20 input.bam
```

### Minimum Base Quality
```bash
samtools mpileup -f reference.fa -Q 20 input.bam
```

### Combined Quality Filters
```bash
samtools mpileup -f reference.fa -q 20 -Q 20 input.bam
```

### Maximum Depth (Critical Trap)
```bash
# samtools mpileup default -d 8000 silently truncates targeted / mt-DNA / amplicon / UMI-deduped data
# bcftools mpileup default -d 250 is far lower; both must be set explicitly when piping
samtools mpileup -f reference.fa -d 0 input.bam        # no cap
samtools mpileup -f reference.fa -d 1000000 input.bam  # explicit high cap

# WRONG -- samtools 8000 cap, then bcftools 250 cap re-applied
samtools mpileup -f ref.fa in.bam | bcftools call -mv

# RIGHT -- single tool, explicit -d
bcftools mpileup -d 1000000 -f ref.fa in.bam | bcftools call -mv
```

## BAQ: Base Alignment Quality (Critical Default)

When `-f ref.fa` is passed, BAQ is enabled by default. BAQ Phred-scales the probability that a base is misaligned (HMM realignment over a small window) and reduces base quality near indels. Tradeoffs: ~30% slower; suppresses FP SNVs near indels; hurts indel detection sensitivity.

| Flag | Behavior |
|------|----------|
| (default with `-f`) | BAQ on (computed from CIGAR if MD missing) |
| `-B` / `--no-BAQ` | Disable BAQ -- raw qualities |
| `-E` / `--redo-BAQ` | Force recompute (after BQSR; if MD stale) |

**BAQ ON for:** short-read germline SNV (BWA, Bowtie2, HISAT2), short-read somatic SNV.

**BAQ OFF (`-B`) for:** long-read variant calling (ONT, PacBio HiFi), SV calling, RNA-seq near splice junctions, viral / amplicon, ultra-deep ctDNA from consensus reads (consensus quality already inflated), aDNA (qualities pre-rescaled by mapDamage).

`-A` (count anomalous read pairs / orphans) is required for amplicon -- amplicon reads are by design not properly paired.

`-aa` (output all positions, including zero-coverage) is required for ARTIC SARS-CoV-2 consensus generation.

### Library-Typed Flags Cheat Sheet

| Library | Flags |
|---------|-------|
| Short-read germline WGS (BWA) | `-q 20 -Q 20 -d 0` (BAQ on default) |
| Short-read tumor WGS | `-q 1 -Q 13 -d 0 -B` (low MAPQ kept; BAQ off) |
| Amplicon viral (ARTIC) | `-aa -A -d 600000 -B -Q 20` |
| Capture / exome | `-q 20 -Q 20 -d 250` |
| Long-read ONT R10.4+ | `-q 30 -Q 0 -B -d 0`; for `bcftools mpileup` add `--max-BQ 30` (its `ont` preset value) |
| PacBio HiFi | `-q 20 -Q 0 -B -d 0` |
| RNA-seq variants | `-q 20 -Q 20 -B -d 0` |
| Forensic / aDNA | `-q 0 -Q 0 -A -d 0 -B` |

## Variant Calling Pipeline (Modern: bcftools mpileup)

**Goal:** Call variants from alignment data using the pileup-based approach.

**Approach:** Use `bcftools mpileup` (not `samtools mpileup -g`) so genotype-likelihood code is co-versioned with `bcftools call`. Apply quality and depth caps explicitly; annotate FORMAT fields needed for downstream filtering.

### Modern Germline Calling
```bash
bcftools mpileup -f reference.fa -d 1000000 -q 20 -Q 20 \
    --annotate FORMAT/AD,FORMAT/DP,FORMAT/SP,INFO/AD \
    input.bam | \
  bcftools call -mv -Oz -o variants.vcf.gz
bcftools index -t variants.vcf.gz
```

### Multi-Sample Joint Calling
```bash
bcftools mpileup -f reference.fa --threads 4 -d 250 -q 20 -Q 20 \
    -a FORMAT/AD,FORMAT/DP s1.bam s2.bam s3.bam | \
  bcftools call -mv --threads 4 -Oz -o joint.vcf.gz
```

For somatic / low-VAF, prefer Mutect2 / Strelka2 / DeepVariant -- materially better than mpileup-based callers.

### Overlap Detection Defaults

When fragment length < 2 * read_length, R1 and R2 overlap. Both `samtools mpileup` and `bcftools mpileup` enable overlap detection by default (per samtools-mpileup(1)) and count overlapping bases once; pass `-x` to disable (long form is `--disable-overlap-removal` in samtools since 1.16, but `--ignore-overlaps` in bcftools). Disabling overlap correction can inflate somatic VAFs at sites covered by overlapping pairs (especially in cfDNA / FFPE).

## pysam Python Alternative

### Basic Pileup
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for pileup_column in bam.pileup('chr1', 1000000, 1001000):
        print(f'{pileup_column.reference_name}:{pileup_column.pos} depth={pileup_column.n}')
```

### Access Reads at Position
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for pileup_column in bam.pileup('chr1', 1000000, 1000001, truncate=True):
        print(f'Position: {pileup_column.pos}')
        print(f'Depth: {pileup_column.n}')

        for pileup_read in pileup_column.pileups:
            if pileup_read.is_del:
                print('  Deletion')
            elif pileup_read.is_refskip:
                print('  Reference skip')
            else:
                qpos = pileup_read.query_position
                base = pileup_read.alignment.query_sequence[qpos]
                qual = pileup_read.alignment.query_qualities[qpos]
                print(f'  {base} (Q{qual})')
```

### Count Alleles at Position
```python
import pysam
from collections import Counter

def allele_counts(bam_path, chrom, pos):
    counts = Counter()

    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for pileup_column in bam.pileup(chrom, pos, pos + 1, truncate=True):
            if pileup_column.pos != pos:
                continue

            for pileup_read in pileup_column.pileups:
                if pileup_read.is_del:
                    counts['DEL'] += 1
                elif pileup_read.is_refskip:
                    continue
                else:
                    qpos = pileup_read.query_position
                    base = pileup_read.alignment.query_sequence[qpos]
                    counts[base.upper()] += 1

    return dict(counts)

counts = allele_counts('input.bam', 'chr1', 1000000)
print(counts)  # {'A': 45, 'G': 5}
```

### Calculate Allele Frequency
```python
import pysam
from collections import Counter

def allele_frequency(bam_path, chrom, pos, min_qual=20):
    counts = Counter()

    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for pileup_column in bam.pileup(chrom, pos, pos + 1, truncate=True,
                                         min_base_quality=min_qual):
            if pileup_column.pos != pos:
                continue

            for pileup_read in pileup_column.pileups:
                if pileup_read.is_del or pileup_read.is_refskip:
                    continue
                qpos = pileup_read.query_position
                base = pileup_read.alignment.query_sequence[qpos]
                counts[base.upper()] += 1

    total = sum(counts.values())
    if total == 0:
        return {}

    return {base: count / total for base, count in counts.items()}

freq = allele_frequency('input.bam', 'chr1', 1000000)
for base, f in sorted(freq.items(), key=lambda x: -x[1]):
    print(f'{base}: {f:.1%}')
```

### Pileup with Quality Filtering
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for pileup_column in bam.pileup('chr1', 1000000, 1001000,
                                     truncate=True,
                                     min_mapping_quality=20,
                                     min_base_quality=20):
        print(f'{pileup_column.pos}: {pileup_column.n}')
```

### Generate Pileup Text
```python
import pysam

def pileup_text(bam_path, ref_path, chrom, start, end):
    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        with pysam.FastaFile(ref_path) as ref:
            for pileup_column in bam.pileup(chrom, start, end, truncate=True):
                pos = pileup_column.pos
                ref_base = ref.fetch(chrom, pos, pos + 1)
                depth = pileup_column.n

                bases = []
                for pileup_read in pileup_column.pileups:
                    if pileup_read.is_del:
                        bases.append('*')
                    elif pileup_read.is_refskip:
                        bases.append('>')
                    else:
                        qpos = pileup_read.query_position
                        base = pileup_read.alignment.query_sequence[qpos]
                        if base.upper() == ref_base.upper():
                            bases.append('.' if not pileup_read.alignment.is_reverse else ',')
                        else:
                            bases.append(base.upper() if not pileup_read.alignment.is_reverse else base.lower())

                print(f'{chrom}\t{pos+1}\t{ref_base}\t{depth}\t{"".join(bases)}')

pileup_text('input.bam', 'reference.fa', 'chr1', 1000000, 1000100)
```

## Pileup Options Summary

| Option | Description | Common pitfall |
|--------|-------------|----------------|
| `-f FILE` | Reference FASTA | Triggers BAQ ON by default |
| `-r REGION` | Restrict to region | |
| `-l FILE` | BED file of regions | |
| `-q INT` | Min mapping quality | Aligner-dependent semantics |
| `-Q INT` | Min base quality | `-Q 0` with default overlap detection has subtle behavior |
| `-d INT` | Max depth | **Default 8000 silently truncates**; bcftools mpileup default is 250 |
| `-B` | Disable BAQ | Often correct for long reads, SV, viral, consensus |
| `-A` | Count anomalous pairs | Required for amplicon |
| `-aa` | Output all positions | Required for consensus generation |
| `-x` (`--disable-overlap-removal`; bcftools: `--ignore-overlaps`) | Disable mate-overlap correction | Rarely correct |
| `--max-BQ INT` (`bcftools mpileup` only) | Cap baseQ/BAQ (default 60) | Not a `samtools mpileup` option; useful for ONT/HiFi (Q values inflated) |
| `-g` (REMOVED in 1.15) | Old BCF output | Use `bcftools mpileup` instead |

## Quick Reference

| Task | Command |
|------|---------|
| Basic pileup | `samtools mpileup -f ref.fa in.bam` |
| Quality filter | `samtools mpileup -f ref.fa -q 20 -Q 20 in.bam` |
| Region | `samtools mpileup -f ref.fa -r chr1:1-1000 in.bam` |
| To bcftools | `bcftools mpileup -f ref.fa -d 1000000 in.bam \| bcftools call -mv` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `No FASTA reference` | Missing -f option | Add `-f reference.fa` |
| `Reference mismatch` | Wrong reference | Use same reference as alignment |
| Out of memory | High coverage region | Use `-d` to cap depth |

## Related Skills

- alignment-filtering - Filter BAM before pileup
- reference-operations - Index reference for pileup; M5 cross-check
- bam-statistics - mosdepth, depth tool selection
- variant-calling/variant-calling - Full variant calling workflows
- variant-calling/vcf-basics - VCF/BCF I/O
- variant-calling/joint-calling - Multi-sample joint calling
<!-- END FILE: alignment-files/pileup-generation/SKILL.md -->

## 子目录：alignment-files/reference-operations

<!-- BEGIN FILE: alignment-files/reference-operations/SKILL.md -->
---
name: bio-reference-operations
description: Generate consensus sequences and manage reference files using samtools. Use when creating consensus from alignments, indexing references, or creating sequence dictionaries.
tool_type: cli
primary_tool: samtools
---

## Version Compatibility

Reference examples tested with: GATK 4.5+, bcftools 1.19+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Reference Operations

Generate consensus sequences and manage reference files using samtools.

**"Prepare a reference genome"** -> Index the FASTA and create a sequence dictionary for downstream tools.
- CLI: `samtools faidx ref.fa` + `samtools dict ref.fa -o ref.dict`
- Python: `pysam.FastaFile('ref.fa')` (auto-uses .fai index)

**"Build a consensus from BAM"** -> Derive the most-supported base at each position from aligned reads.
- CLI: `samtools consensus input.bam -o consensus.fa`
- Python: iterate pileup columns and take majority base (pysam)

## samtools faidx - Index Reference FASTA

Create index for random access to reference sequences.

### Create Index
```bash
samtools faidx reference.fa
# Creates reference.fa.fai
```

### Fetch Region from Reference
```bash
samtools faidx reference.fa chr1:1000-2000
```

### Fetch Multiple Regions
```bash
samtools faidx reference.fa chr1:1000-2000 chr2:3000-4000
```

### Fetch Entire Chromosome
```bash
samtools faidx reference.fa chr1
```

### Output to File
```bash
samtools faidx reference.fa chr1:1000-2000 > region.fa
```

### Reverse Complement
```bash
samtools faidx -i reference.fa chr1:1000-2000
```

### FAI File Format
```
chr1    248956422    6    60    61
chr2    242193529    253105708    60    61
```
Columns: name, length, offset, line bases, line width

## samtools dict - Create Sequence Dictionary

Create SAM header dictionary for reference (used by GATK, Picard).

### Create Dictionary
```bash
samtools dict reference.fa -o reference.dict
```

### With Assembly Info
```bash
samtools dict -a GRCh38 -s "Homo sapiens" reference.fa -o reference.dict
```

### Dictionary Format
```
@HD VN:1.0 SO:unsorted
@SQ SN:chr1 LN:248956422 M5:6aef897c3d6ff0c78aff06ac189178dd UR:file:reference.fa
@SQ SN:chr2 LN:242193529 M5:f98db672eb0993dcfdabafe2a882905c UR:file:reference.fa
```

The `M5:` (MD5) tag is the only definitive reference-identity check -- two references named "GRCh38" with different decoy/alt content have different M5s. CRAM enforces M5 match on read-back. See alignment-validation for BAM-vs-reference M5 cross-check.

### GRCh38 Is Not One Reference

| Reference flavor | ALT | Decoy | EBV | HLA | Use case |
|------------------|-----|-------|-----|-----|----------|
| GRCh38 no-alt | no | no | no | no | Conservative analyses |
| GRCh38 + decoy + EBV (1000G analysis set) | no | yes | yes | no | Cohort projects |
| GRCh38 ALT + decoy + EBV + HLA (Broad / hs38DH) | yes | yes | yes | yes | GATK Best Practices |
| T2T-CHM13 v2.0 | n/a | n/a | n/a | n/a | Distinct coordinates -- NOT interchangeable |

Mixing no-alt and ALT-aware BAMs in one cohort produces inconsistent multi-mapping behavior at HLA, KIR, and segmental-duplication regions. Standardize before joint calling.

### Contig Naming: The Silent Killer

| Convention | Source | chr1 | mitochondrion |
|-----------|--------|------|---------------|
| UCSC (hg19, hg38) | UCSC Genome Browser | chr1 | chrM |
| Ensembl (GRCh37, GRCh38) | Ensembl, ENA | 1 | MT |
| NCBI RefSeq (recent) | NCBI | chr1 | chrM |
| 1000G analysis sets | 1000G GRCh38 analysis set | chr1 | chrM |

A BAM with `@SQ SN:chr1` cannot be analyzed against a `1`-named reference (and vice versa). Detect:
```bash
samtools view -H sample.bam | grep '^@SQ' | head -3
samtools dict ref.fa | head -3
```

Convert: `bcftools annotate --rename-chrs` for VCF; for BAM there is no clean conversion -- re-align.

## samtools consensus - Generate Consensus

Create consensus sequence from alignments.

### Basic Consensus
```bash
samtools consensus input.bam -o consensus.fa
```

### From Specific Region
```bash
samtools consensus -r chr1:1000-2000 input.bam -o region_consensus.fa
```

### Output Formats
```bash
# FASTA (default)
samtools consensus -f fasta input.bam -o consensus.fa

# FASTQ (includes quality)
samtools consensus -f fastq input.bam -o consensus.fq
```

### Quality Options
```bash
# Minimum depth to call base
samtools consensus -d 5 input.bam -o consensus.fa

# Call all positions (including low coverage)
samtools consensus -a input.bam -o consensus.fa
```

### IUPAC Ambiguity for Heterozygotes
```bash
# Emit IUPAC codes (R, Y, S, W, K, M, B, D, H, V, N) for heterozygous columns
# --ambig is REQUIRED -- without it, output is restricted to A,C,G,T,N,*
samtools consensus --ambig --het-fract 0.2 --call-fract 0.5 input.bam -o consensus.fa
```

`--het-fract` controls the fraction of the second-most-common base relative to the most common required to call a heterozygote (verify the default for the installed version with `samtools consensus --help`; the manpage documents none). Without `--ambig`, columns where the second base passes `--het-fract` resolve to `N` rather than the IUPAC code. `--show-ins` / `--show-del` control insertion / deletion display, not ambiguity.

### Platform-Aware Consensus
```bash
# Default: Bayesian algorithm (no --config needed)
samtools consensus -f fasta input.bam -o consensus.fa

# Platform-specific profiles (samtools 1.17+; verify via samtools consensus --help for installed version)
samtools consensus --config hifi       input.bam -o consensus.fa   # PacBio HiFi
samtools consensus --config r10.4_sup  input.bam -o consensus.fa   # ONT R10.4+ (r10.4_dup for duplex)
samtools consensus --config ultima     input.bam -o consensus.fa   # Ultima Genomics
samtools consensus --config hiseq      input.bam -o consensus.fa   # Illumina

# Report ref base where consensus unavailable (low coverage; -T added in samtools 1.22)
samtools consensus -T ref.fa input.bam -o consensus.fa
```

### samtools consensus vs bcftools consensus

Different operations -- conflating them produces nonsense:

| Tool | Input | Output | Use case |
|------|-------|--------|----------|
| `samtools consensus` | BAM | Consensus FASTA derived from reads (Bayesian) | Viral, de novo / amplicon, low-coverage species |
| `bcftools consensus` | reference + VCF | Reference with VCF variants applied | Apply called variants (haplotype reconstruction, custom ref for re-mapping) |

For viral consensus from BAM:
```bash
# Modern: samtools consensus
samtools consensus --config hiseq -d 10 --het-fract 0.5 \
    --show-ins yes --show-del yes input.bam -o consensus.fa

# Apply called variants to reference (different question)
bcftools consensus -f reference.fa variants.vcf.gz -o sample_consensus.fa
bcftools consensus -f reference.fa -H 1 phased.vcf.gz -o haplotype1.fa   # phased haplotype 1
```

For bacterial / phage assembly polishing, prefer Pilon (short-read) or medaka (ONT); `samtools consensus` is not iterative.

## pysam Python Alternative

### Fetch from Indexed FASTA
```python
import pysam

with pysam.FastaFile('reference.fa') as ref:
    seq = ref.fetch('chr1', 999, 2000)  # 0-based
    print(seq)
```

### Get Reference Lengths
```python
with pysam.FastaFile('reference.fa') as ref:
    for name in ref.references:
        length = ref.get_reference_length(name)
        print(f'{name}: {length:,} bp')
```

### Fetch All Chromosomes
```python
with pysam.FastaFile('reference.fa') as ref:
    for chrom in ref.references:
        seq = ref.fetch(chrom)
        print(f'>{chrom}')
        print(seq[:100] + '...')
```

### Generate Simple Consensus
```python
import pysam
from collections import Counter

def consensus_at_position(bam, chrom, pos):
    bases = Counter()
    for pileup in bam.pileup(chrom, pos, pos + 1, truncate=True):
        if pileup.pos == pos:
            for read in pileup.pileups:
                if not read.is_del and not read.is_refskip:
                    bases[read.alignment.query_sequence[read.query_position]] += 1
    if bases:
        return bases.most_common(1)[0][0]
    return 'N'

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    consensus = consensus_at_position(bam, 'chr1', 1000000)
    print(f'Consensus at chr1:1000000 = {consensus}')
```

### Build Consensus Sequence (Pedagogical Only)

The Python majority-vote consensus below is illustrative, NOT production. `samtools consensus` is Bayesian, quality-aware, and platform-aware; majority vote ignores base qualities and produces wrong calls on low-coverage / low-quality regions. Use for teaching pileup iteration mechanics; use `samtools consensus` for any real consensus.

```python
import pysam
from collections import Counter

def build_consensus(bam_path, chrom, start, end, min_depth=3):
    consensus = []

    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for pileup in bam.pileup(chrom, start, end, truncate=True):
            bases = Counter()
            for read in pileup.pileups:
                if not read.is_del and not read.is_refskip:
                    base = read.alignment.query_sequence[read.query_position]
                    bases[base] += 1

            if sum(bases.values()) >= min_depth:
                consensus.append(bases.most_common(1)[0][0])
            else:
                consensus.append('N')

    return ''.join(consensus)
```

### Create Dictionary Header
```python
import pysam

def create_dict_header(fasta_path):
    header = {'HD': {'VN': '1.6', 'SO': 'unsorted'}, 'SQ': []}

    with pysam.FastaFile(fasta_path) as ref:
        for name in ref.references:
            length = ref.get_reference_length(name)
            header['SQ'].append({'SN': name, 'LN': length})

    return header

header = create_dict_header('reference.fa')
for sq in header['SQ'][:5]:
    print(f'{sq["SN"]}: {sq["LN"]:,} bp')
```

## Reference Preparation Workflow

**Goal:** Set up a reference genome with all indices needed by common analysis tools.

**Approach:** Create FASTA index (.fai), sequence dictionary (.dict), and aligner-specific indices in sequence.

### Prepare Reference for Analysis
```bash
# 1. Index FASTA for samtools/pysam
samtools faidx reference.fa

# 2. Create sequence dictionary for GATK/Picard
samtools dict reference.fa -o reference.dict

# 3. Pre-populate CRAM REF_CACHE (for offline HPC nodes)
seq_cache_populate.pl -root $REF_CACHE_DIR reference.fa
```

For aligner-specific indices (BWA, Bowtie2, STAR, minimap2, Salmon), see read-alignment.

### Check Reference Setup
```bash
# Verify FAI exists
ls -la reference.fa.fai

# Verify dict exists
head reference.dict

# Test fetch
samtools faidx reference.fa chr1:1-100
```

## Common Operations

### Extract Chromosome
```bash
samtools faidx reference.fa chr1 > chr1.fa
samtools faidx chr1.fa  # Index the subset
```

### Get Chromosome Sizes
```bash
cut -f1,2 reference.fa.fai > chrom.sizes
```

### Subset Reference
```bash
samtools faidx reference.fa chr1 chr2 chr3 > subset.fa
samtools faidx subset.fa
```

### Compare Consensus to Reference
```bash
# Generate consensus
samtools consensus input.bam -o consensus.fa

# Align consensus back to reference
minimap2 -a reference.fa consensus.fa > comparison.sam
```

## Quick Reference

| Task | Command |
|------|---------|
| Index FASTA | `samtools faidx ref.fa` |
| Fetch region | `samtools faidx ref.fa chr1:1-1000` |
| Create dict | `samtools dict ref.fa -o ref.dict` |
| Build consensus | `samtools consensus in.bam -o out.fa` |
| Chrom sizes | `cut -f1,2 ref.fa.fai` |

## Related Skills

- sam-bam-basics - CRAM reference resolution (REF_PATH, REF_CACHE)
- alignment-indexing - faidx for reference access
- alignment-validation - BAM-vs-reference M5 cross-validation
- pileup-generation - Pileup for consensus building
- variant-calling/vcf-basics - VCF I/O for `bcftools consensus`
- variant-calling/consensus-sequences - Consensus from VCF (different operation)
- read-alignment/bwa-alignment - BWA index preparation
- sequence-io/read-sequences - Parse FASTA with Biopython
<!-- END FILE: alignment-files/reference-operations/SKILL.md -->

## 子目录：alignment-files/sam-bam-basics

<!-- BEGIN FILE: alignment-files/sam-bam-basics/SKILL.md -->
---
name: bio-sam-bam-basics
description: View, convert, and understand SAM/BAM/CRAM alignment files using samtools and pysam. Use when inspecting alignments, converting between formats, or understanding alignment file structure.
tool_type: cli
primary_tool: samtools
---

## Version Compatibility

Reference examples tested with: pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# SAM/BAM/CRAM Basics

**"Read a BAM file"** -> Open a binary alignment file and iterate over aligned reads with their mapping coordinates, flags, and quality scores.
- Python: `pysam.AlignmentFile()` (pysam)
- CLI: `samtools view` (samtools)
- R: `scanBam()` (Rsamtools)

View and convert alignment files using samtools and pysam.

## Format Overview

| Format | Description | Use Case |
|--------|-------------|----------|
| SAM | Text format, human-readable | Debugging, small files |
| BAM | Binary compressed SAM | Standard storage format |
| CRAM | Reference-based compression | Long-term archival, smaller than BAM |

## SAM Format Structure

```
@HD VN:1.6 SO:coordinate
@SQ SN:chr1 LN:248956422
@RG ID:sample1 SM:sample1
@PG ID:bwa PN:bwa VN:0.7.17
read1  0   chr1  100  60  50M  *  0  0  ACGT...  FFFF...  NM:i:0
```

Header lines start with `@`:
- `@HD` - Header metadata (version, sort order)
- `@SQ` - Reference sequence dictionary
- `@RG` - Read group information
- `@PG` - Program used to create file

Alignment fields (tab-separated):
1. QNAME - Read name
2. FLAG - Bitwise flag
3. RNAME - Reference name
4. POS - 1-based position
5. MAPQ - Mapping quality
6. CIGAR - Alignment description
7. RNEXT - Mate reference
8. PNEXT - Mate position
9. TLEN - Template length
10. SEQ - Read sequence
11. QUAL - Base qualities
12. Optional tags (NM:i:0, MD:Z:50, etc.)

## samtools view

### View BAM as SAM
```bash
samtools view input.bam | head
```

### View with Header
```bash
samtools view -h input.bam | head -100
```

### View Header Only
```bash
samtools view -H input.bam
```

### View Specific Region
```bash
samtools view input.bam chr1:1000-2000
```

### Count Alignments
```bash
samtools view -c input.bam
```

## Format Conversion

**Goal:** Convert between SAM (text), BAM (binary), and CRAM (reference-compressed) alignment formats.

**Approach:** Use `samtools view` with format flags (`-b` for BAM, `-C` for CRAM, `-h` for SAM with header). CRAM requires a reference FASTA with `-T`.

### BAM to SAM
```bash
samtools view -h -o output.sam input.bam
```

### SAM to BAM
```bash
samtools view -b -o output.bam input.sam
```

### BAM to CRAM
```bash
samtools view -C -T reference.fa -o output.cram input.bam
```

### CRAM to BAM
```bash
samtools view -b -T reference.fa -o output.bam input.cram
```

### Pipe Conversion
```bash
samtools view -b input.sam > output.bam
```

## Common Flags

| Flag | Decimal | Meaning |
|------|---------|---------|
| 0x1 | 1 | Paired |
| 0x2 | 2 | Proper pair |
| 0x4 | 4 | Unmapped |
| 0x8 | 8 | Mate unmapped |
| 0x10 | 16 | Reverse strand |
| 0x20 | 32 | Mate reverse strand |
| 0x40 | 64 | First in pair |
| 0x80 | 128 | Second in pair |
| 0x100 | 256 | Secondary alignment |
| 0x200 | 512 | Failed QC |
| 0x400 | 1024 | PCR duplicate |
| 0x800 | 2048 | Supplementary |

### Decode Flags (Bidirectional)
```bash
# Number to mnemonics
samtools flags 147
# 0x93 147 PAIRED,PROPER_PAIR,REVERSE,READ2

# Mnemonics to number
samtools flags PAIRED,PROPER_PAIR,REVERSE,READ2   # 147
```

### Secondary vs Supplementary (Different Semantics)

Two different concepts that are routinely conflated:

| Bit | Name | Meaning | Filter implication |
|-----|------|---------|--------------------|
| 0x100 (256) | Secondary | An alternative candidate alignment for the same read; not the primary location | `-F 256` is correct for SNV/indel calling on short reads |
| 0x800 (2048) | Supplementary | A piece of a chimeric/split alignment (the read is split across loci) | Carries SA:Z tag; **required** by SV callers (Manta, Sniffles, cuteSV, GRIDSS, Delly) |

`-F 2304` removes both. Strip supplementary only when downstream is small-variant calling; keep supplementary for SV calling, fusion detection, or any analysis that follows split-reads.

## MAPQ Is Not Portable Across Aligners

`samtools view -q 30` does different things depending on what produced the BAM. MAPQ is an aligner-specific scale, not a universal probability:

| Aligner | MAPQ scale | "Unique" sentinel | Common gotcha |
|---------|-----------|-------------------|----------------|
| BWA-MEM / BWA-MEM2 | 0-60 | 60 | `-q 30` is sensible "high confidence" |
| minimap2 (DNA / pbmm2) | 0-60 | 60 | Spec-compliant |
| HISAT2 | 0-60 | 60 | Spec-compliant |
| Bowtie2 | 0-42 | 42 (rare) | `-q 60` drops everything; `-q 23` is a common "uniquely mapped" convention (not a probabilistic 99% threshold) |
| STAR | 0, 1, 3, 255 | **255 = uniquely mapped (sentinel, not a quality)** | `-q 255` for "unique only"; `-q 30` accidentally keeps unique only too |
| DRAGEN | 0 to `--mapq-max` (default 60) | varies | `-q 30` still meaningful; distribution shape differs |
| Cell Ranger / STARsolo | inherits STAR | 255 | Same trap as STAR |

Verify the actual scale of any unfamiliar BAM:
```bash
samtools view input.bam | awk '{print $5}' | sort -un | head
samtools view -H input.bam | grep '^@PG' | head -1   # which aligner produced this BAM
```

## 0-Based vs 1-Based Coordinates (Footgun)

| Context | Coordinate system |
|---------|-------------------|
| SAM text POS | 1-based, inclusive |
| `samtools view chr1:100-200` | 1-based, closed interval |
| `samtools faidx chr1:100-200` | 1-based, closed interval |
| BAM binary internal | 0-based, half-open |
| `pysam read.reference_start` | 0-based |
| `bam.fetch('chr1', 100, 200)` | 0-based, half-open |
| BED files | 0-based, half-open |
| VCF | 1-based |
| GFF/GTF | 1-based, inclusive |

`samtools view bam chr1:100-200` and `bam.fetch('chr1', 100, 200)` return different read sets at boundaries.

## CIGAR Operations

| Op | Description |
|----|-------------|
| M | Alignment match (can be mismatch) |
| I | Insertion to reference |
| D | Deletion from reference |
| N | Skipped region (introns in RNA-seq; do NOT count as covered bases) |
| S | Soft clipping (sequence in SEQ but not aligned) |
| H | Hard clipping (sequence not in SEQ) |
| = | Sequence match (explicit) |
| X | Sequence mismatch (explicit) |
| P | Padding (rare; multiple-sequence-alignment context) |

Example: `50M2I30M` = 50 bases match, 2 base insertion, 30 bases match

CIGAR `M` is overloaded -- it is the union of `=` and `X`. Some aligners emit `=`/`X` directly (e.g. minimap2 with `--eqx`); bcftools / Picard often need `M` and rebuild MD/NM with `samtools calmd`. `N` operations break naive coverage calculations: a 1000 bp RNA-seq read with one 50 kb intron does not cover 50 kb. Distinguish soft-clip (`S`, bases retained) from hard-clip (`H`, bases discarded -- irreversible).

## Context-Specific Tags

Beyond the standard fields, downstream tools depend on optional tags whose presence depends on aligner and assay. Inspect with `samtools view input.bam | head -1 | tr '\t' '\n'` or pysam `read.get_tag('XX')`.

| Tag | Set by | Meaning | Required by |
|-----|--------|---------|-------------|
| NM:i | bwa, samtools calmd | Edit distance to reference | mapDamage, many filters |
| MD:Z | bwa, samtools calmd | Mismatch positions (text) | bcftools mpileup BAQ, IGV mismatch coloring |
| MC:Z | samtools fixmate -m | Mate CIGAR | samtools markdup |
| ms:i | samtools fixmate -m | Mate score (lowercase per SAMtags) | samtools markdup |
| RG:Z | aligner from -R | Read group ID | GATK BQSR, MarkDuplicates LB lookup |
| SA:Z | All split-read aligners | Comma-list of supplementary coords | Sniffles, Manta, cuteSV, GRIDSS, Delly |
| NH:i | STAR, HISAT2 | Number of reported hits | featureCounts multimapper handling, Salmon |
| HI:i | STAR | Hit index among NH (1-based by default; `--outSAMattrIHstart 0` for 0-based) | RSEM |
| XS:A | STAR (`--outSAMstrandField intronMotif`), HISAT2 | Strand inferred from splice motif | StringTie, Cufflinks |
| ts:A | minimap2 `-ax splice` | Transcript strand from splice motif | StringTie |
| CB:Z | Cell Ranger, STARsolo | Corrected cell barcode | scRNA quantification |
| UB:Z | Cell Ranger, STARsolo | Corrected UMI | UMI-aware dedup |
| RX:Z | fgbio AnnotateBamWithUmis | Raw UMI (bulk) | fgbio GroupReadsByUmi |
| MI:Z | fgbio GroupReadsByUmi | Molecular identifier (UMI group) | CallMolecularConsensusReads, duplex calling |
| cs:Z | minimap2 --cs | Compact CIGAR-with-bases | paftools, SV tools |

Missing tags fail in two modes: silently wrong (featureCounts ignoring multimappers without NH; markdup marking nothing without MC/MS) or loudly (consensus tools rejecting input without MD).

## Provenance: @PG Chain

The `@PG` lines record every tool that touched the BAM, linked through `PP` (previous program) tags. This is the audit trail.

```bash
samtools view -H input.bam | grep '^@PG'
```

A clean germline pipeline:
```
@PG ID:bwa-mem PN:bwa VN:0.7.17
@PG ID:samtools.1 PN:samtools VN:1.20 PP:bwa-mem CL:samtools sort
@PG ID:samtools.2 PN:samtools VN:1.20 PP:samtools.1 CL:samtools fixmate
@PG ID:samtools.3 PN:samtools VN:1.20 PP:samtools.2 CL:samtools markdup
```

A broken/missing chain (no PP, unknown tools, gaps) means the BAM cannot be reliably reproduced. Production pipelines often reject inputs without a complete chain.

## CRAM Reference Resolution (Critical)

CRAM stores reads relative to a reference; without it, the file is unreadable. htslib resolves the reference in this order:

1. Command-line `-T ref.fa` / `--reference`
2. `REF_CACHE` env var (local MD5-named cache; searched *before* `REF_PATH`)
3. `REF_PATH` env var (colon-separated; each element matched by the `@SQ M5:` MD5). A remote server such as EBI ENA is consulted only if its URL is present here -- it was the built-in default through htslib 1.21, but that default was **removed in 1.22** to reduce EBI load, so modern htslib does no network lookup unless that URL is added explicitly.
4. Local file named in the `@SQ UR:` header tag (local / `file://` paths only; `http`/`ftp` URIs in `UR:` are ignored)

On HPC nodes without internet, populate a local cache once:
```bash
mkdir -p $HOME/cram_cache
seq_cache_populate.pl -root $HOME/cram_cache reference.fa
export REF_CACHE=$HOME/cram_cache/%2s/%2s/%s
export REF_PATH=$REF_CACHE   # local only; no network/ENA lookup

samtools quickcheck -v file.cram   # header + EOF only
samtools view -c file.cram          # forces full decode; proves reference reachable
```

CRAM can be made irreversibly lossy, but the `archive` profile is NOT how: `--output-fmt-option archive` is a *lossless* maximum-compression preset (fqzcomp quality codec, name tokenization, larger slices) that does not alter bases or qualities. Irreversible loss comes instead from explicit quality **binning** (e.g. Illumina 8-bin), which must be applied deliberately and is harmful for low-coverage / somatic / forensic / archival data. Convert against the *exact* reference the BAM was aligned to (matched by `@SQ M5:`); a different reference silently corrupts bases on read-back.

## pysam Python Alternative

**Goal:** Read and manipulate alignment data programmatically in Python.

**Approach:** Use `pysam.AlignmentFile` to open BAM/CRAM files, iterate over reads, and access properties like coordinates, flags, CIGAR, and tags.

### Open and Iterate
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for read in bam:
        print(f'{read.query_name}\t{read.reference_name}:{read.reference_start}')
```

### Access Header
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for sq in bam.header['SQ']:
        print(f'{sq["SN"]}: {sq["LN"]} bp')
```

### Read Alignment Properties
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for read in bam:
        print(f'Name: {read.query_name}')
        print(f'Flag: {read.flag}')
        print(f'Chrom: {read.reference_name}')
        print(f'Pos: {read.reference_start}')  # 0-based
        print(f'MAPQ: {read.mapping_quality}')
        print(f'CIGAR: {read.cigarstring}')
        print(f'Seq: {read.query_sequence}')
        print(f'Qual: {read.query_qualities}')
        break
```

### Check Flag Properties
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for read in bam:
        if read.is_paired and read.is_proper_pair:
            if read.is_reverse:
                strand = '-'
            else:
                strand = '+'
            print(f'{read.query_name} on {strand} strand')
```

### Fetch Region
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for read in bam.fetch('chr1', 1000, 2000):
        print(read.query_name)
```

### Convert BAM to SAM
```python
with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('output.sam', 'w', header=infile.header) as outfile:
        for read in infile:
            outfile.write(read)
```

### Convert to CRAM
```python
with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('output.cram', 'wc', reference_filename='reference.fa', header=infile.header) as outfile:
        for read in infile:
            outfile.write(read)
```

## Quick Reference

| Task | samtools | pysam |
|------|----------|-------|
| View BAM | `samtools view file.bam` | `AlignmentFile('file.bam', 'rb')` |
| View header | `samtools view -H file.bam` | `bam.header` |
| Count reads | `samtools view -c file.bam` | `sum(1 for _ in bam)` |
| Get region | `samtools view file.bam chr1:1-1000` | `bam.fetch('chr1', 0, 1000)` |
| BAM to SAM | `samtools view -h -o out.sam in.bam` | Open with 'w' mode |
| SAM to BAM | `samtools view -b -o out.bam in.sam` | Open with 'wb' mode |
| BAM to CRAM | `samtools view -C -T ref.fa -o out.cram in.bam` | Open with 'wc' mode |

## Related Skills

- alignment-indexing - Create indices for random access (required for fetch/region queries)
- alignment-sorting - Sort alignments by coordinate or name
- alignment-filtering - Filter alignments by flags, quality, regions
- alignment-validation - Sequence dictionary cross-validation (M5 checksums)
- bam-statistics - Generate statistics from alignment files
- reference-operations - REF_PATH/REF_CACHE setup for CRAM
- sequence-io/read-sequences - Parse FASTA/FASTQ input files
<!-- END FILE: alignment-files/sam-bam-basics/SKILL.md -->

<!-- END CATEGORY: alignment-files -->

