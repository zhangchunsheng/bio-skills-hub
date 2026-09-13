---
slug: bio-genome-intervals-integrated
version: 1.0.1
displayName: "基因组区间操作 / Genomic interval operations"
name: bio-genome-intervals-integrated
summary: "中文：基因组区间操作综合技能，整合 8 个相关专题，覆盖基因组区间操作：BED/BEDGraph/bigWig、坐标系统、区间算术、重叠显著性、coverage分析。 English: Integrated Genomic interval operations skill covering 8 related topics, including Genomic interval operations: BED/BEDGraph/bigWig, coordinate systems, interval arithmetic, overlap significance, coverage analysis."
description: "中文：这是一个面向基因组区间操作的综合生物信息学 Skill，整合当前分类下 8 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：基因组区间操作：BED/BEDGraph/bigWig、坐标系统、区间算术、重叠显著性、coverage分析。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：bedtools, deeptools, gffutils。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Genomic interval operations, combining 8 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Genomic interval operations: BED/BEDGraph/bigWig, coordinate systems, interval arithmetic, overlap significance, coverage analysis. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: bedtools, deeptools, gffutils. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# genome-intervals 分类 Skill 整合版

> 本文件整合同一主分类目录下 8 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: genome-intervals -->

## 子目录：genome-intervals/bed-file-basics

<!-- BEGIN FILE: genome-intervals/bed-file-basics/SKILL.md -->
---
name: bio-genome-intervals-bed-file-basics
description: Handles BED-format genomic intervals (BED3 through BED12, narrowPeak/broadPeak) and the coordinate-system substrate the whole interval category rests on, with bedtools (CLI) and pybedtools/pyranges/pandas (Python). Covers the 0-based half-open vs 1-based-closed convention boundary and the start-1/end-unchanged conversion, the silent failures (chrom-name mismatch, CRLF, lexicographic-vs-version sort under -sorted), genome/chrom.sizes generation, sorting contracts, BED12 block invariants, validation, makewindows, cross-assembly liftover (liftOver/CrossMap), and BED<->VCF/BAM/FASTA conversion. Use when reading, creating, validating, sorting, lifting between genome builds, or converting interval files, preparing inputs for bedtools/tabix/bigBed, or debugging an off-by-one or empty-overlap result.
tool_type: mixed
primary_tool: bedtools
---

## Version Compatibility

Reference examples tested with: bedtools 2.31+, pybedtools 0.10+, pyranges 0.x (the `pyranges1` rewrite ships as a separate package), samtools 1.19+, pandas 2.2+, UCSC liftOver / CrossMap 0.7+ (the bare `CrossMap` entry point replaced `CrossMap.py` at 0.7.0).

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

pyranges has a major-version API split: pyranges 0.x and the `pyranges1` rewrite differ in method names and DataFrame access; both keep `Chromosome/Start/End` columns and 0-based half-open coordinates. Check `import pyranges; pyranges.__version__` before chaining methods. Operations that need chromosome lengths (`slop`, `complement`, `shuffle`, `makewindows -g`, `-sorted` ordering) require a genome/chrom.sizes file. If code throws an error, introspect the installed tool and adapt rather than retrying.

# BED File Basics

**"Work with this interval file without shifting everything by one base"** -> Establish the coordinate convention from the format, read/create/validate/sort the intervals, and convert across format boundaries with the correct base shift.
- CLI: `bedtools sort -i in.bed`, `bedtools getfasta`, `bedtools makewindows -g genome.txt -w 10000`, `sort -k1,1 -k2,2n`
- Python: `pybedtools.BedTool('in.bed')`, `pr.read_bed('in.bed')` (pyranges), `pd.read_csv(sep='\t', comment='#')`

## The Single Most Important Modern Insight -- A Coordinate Is a Bare Integer With No Self-Describing Convention

A `start` column is just an `int`. Nothing in the file says whether it is 0-based or 1-based, so the convention lives in the analyst's head, keyed off the **format**, not the data. BED is 0-based half-open `[start, end)`; GTF/GFF, SAM, VCF, and wiggle are 1-based fully-closed `[start, end]`. Three load-bearing consequences:

1. **The conversion is `start - 1, end unchanged` -- and it throws no error if wrong.** A botched convention shift still parses, still runs, and silently shifts every answer by one base: gene bodies 1 bp short, boundary SNPs flipping in/out, exact-edge intersections toggling. The end is numerically identical between BED-half-open and GFF-closed because GFF's last *included* base and BED's first *excluded* position are the same boundary. The symmetry instinct (subtract 1 from both) is the classic bug. The reflex: convert `start_bed = start_1based - 1` (end unchanged) and **test the round-trip on a 1 bp feature** -- BED `chr1 5 6` == GFF `chr1 6 6`, both one base. Length is `end - start` in BED (no `+1`); `end - start + 1` in GTF.

2. **The two truly silent file failures.** (a) **Chrom-name mismatch** (`chr1` vs `1`, `chrM` vs `MT`): intersecting a `chr`-prefixed file against a bare-numeral one yields a perfectly valid **empty** result -- "no overlap" looks like biology, not a bug. Confirm shared naming (`cut -f1 a.bed | sort -u`) before any cross-file op. (b) **CRLF line endings** from Excel/Windows glue `\r` onto the last field (`end` becomes `"100\r"`); the tell is "works for some tools, breaks for others." `cat -A` shows `^M$`; fix with `dos2unix`. Never open a BED in Excel -- it date-mangles `SEPT9`->`9-Sep` and float-truncates large coordinates.

3. **bedtools `-sorted` assumes both inputs share the SAME chromosome order.** With a lexicographic (`chr1, chr10, chr2`) vs version (`chr1, chr2, chr10`) sort mismatch, modern bedtools (>=~2.25) detects the inconsistency and **errors out** (exit 1, `chromomsome sort ordering ... is inconsistent`); older versions silently swept past and **dropped chr10-chr22**. Either sort both files with the identical command, or pass `-g genome.txt` (derived from the same reference FASTA) to pin the expected order. For one-off work, omit `-sorted` (the in-memory path tolerates any order). The mismatch that stays SILENT on every version is a chromosome-NAME difference (`chr1` vs `1`), which returns an empty result with no error.

## Tool Taxonomy

| Tool | Role | Mechanism | When |
|------|------|-----------|------|
| bedtools | CLI interval algebra (Quinlan 2010 *Bioinformatics* 26:841) | streaming, sorted-input reference implementation | shell pipelines, large files, reproducible one-liners |
| pybedtools | Python wrapper over bedtools (Dale 2011 *Bioinformatics* 27:3423) | shells out per op; BedTool objects + iterators | inside a Python analysis; chaining with pandas |
| pyranges | pure-Python interval engine (Stovner 2020 *Bioinformatics* 36:918) | vectorized PyRanges/pandas, no bedtools binary | large in-memory joins, dataframe-native workflows |
| pandas | flat tabular read | `read_csv(sep='\t')`; knows NO coordinate semantics | quick filter/inspect; the analyst enforces 0-based + sort manually |
| UCSC bedToBigBed / tabix | indexed/compressed BED for random access | requires `sort -k1,1 -k2,2n`, no track lines | browser tracks, region queries on huge files |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Quick create/sort/filter on the command line | bedtools + coreutils `sort -k1,1 -k2,2n` | no Python overhead; reproducible |
| Inside a pandas/Python pipeline | pybedtools or pyranges | stays in-process; pyranges if no bedtools binary |
| Convert VCF/GTF/SAM positions to BED | subtract 1 from start, end unchanged | the convention boundary; test on a 1 bp feature |
| Empty intersect / "no overlap found" | check chrom naming (`chr1` vs `1`) FIRST | the most common silent null result |
| Using `-sorted` for speed/RAM | sort both files identically, or pass `-g genome.txt` | modern bedtools errors on a lexicographic-vs-version mismatch; old versions dropped chroms silently |
| Need chromosome lengths (slop/complement/windows) | generate genome.txt from the SAME FASTA | a stale/generic chrom.sizes rots slop/complement |
| Set operations on these intervals | -> interval-arithmetic | this skill is the format/coordinate substrate |
| Parse a GTF/GFF gene model | -> gtf-gff-handling | 1-based, parent/child hierarchy, not a flat BED |
| Peaks not yet called | -> chip-seq/peak-calling or atac-seq/atac-peak-calling | this category operates on existing intervals |
| Convert between assemblies (hg19<->hg38) | liftOver/CrossMap, report unmapped | a different problem from convention shifts |

## BED Columns (BED3 -> BED12)

The first 3 fields are required; the rest are optional but **positional** (cannot supply field N without 1..N-1), and the field count must be identical on every line.

```
BED3   chrom  start  end
BED4   + name
BED5   + score (int 0-1000; '.' allowed)
BED6   + strand (+/-/.)            # the common stranded-interval form
BED12  + thickStart thickEnd itemRgb blockCount blockSizes blockStarts   # transcript/exon models
```

narrowPeak is **BED6+4** (`signalValue pValue qValue peak`); broadPeak is **BED6+3** (drops `peak`). The `peak` column is a **0-based offset from chromStart** (absolute summit = `chromStart + peak`), `-1` if none; `pValue`/`qValue` are `-log10` scaled with `-1` meaning "not assigned", NOT p=0.1.

## Create and Read BED Files

```python
import pybedtools
import pandas as pd

intervals = [('chr1', 100, 200, 'peak1', 100, '+'), ('chr1', 300, 400, 'peak2', 200, '-')]
bed = pybedtools.BedTool(intervals)                                       # from list of tuples
bed = pybedtools.BedTool.from_dataframe(pd.read_csv('peaks.tsv', sep='\t'))  # from a DataFrame
bed.saveas('peaks.bed')

for iv in pybedtools.BedTool('peaks.bed'):
    print(iv.chrom, iv.start, iv.end, len(iv))   # start/end are ints; len(iv) == end - start
df = pybedtools.BedTool('peaks.bed').to_dataframe(names=['chrom', 'start', 'end', 'name', 'score', 'strand'])
```

pandas reads BED as a flat table but knows nothing about coordinates: `pd.read_csv('in.bed', sep='\t', header=None, comment='#')` -- the analyst enforces 0-based and sorts manually.

## Generate the Genome / chrom.sizes File

**Goal:** Produce the authoritative chromosome-length file that `slop`, `complement`, `shuffle`, `makewindows -g`, and `-sorted` ordering depend on.

**Approach:** Index the exact reference FASTA the rest of the pipeline used and take its first two columns -- never download a generic `hg38.chrom.sizes` and hope it matches the assembly the BAM was aligned to.

```bash
samtools faidx ref.fa
cut -f1,2 ref.fa.fai > genome.txt   # chrom<TAB>size; bedtools reads only the first 2 cols, accepts the .fai directly
```

## Convert Across Format Boundaries

**Goal:** Move positions between BED and VCF/SAM/GTF/BAM without an off-by-one.

**Approach:** Subtract 1 from the 1-based start (end unchanged) going TO BED; for BAM, let bedtools do the conversion; verify a known single-base landmark afterwards.

```bash
grep -v '^#' in.vcf | awk 'BEGIN{OFS="\t"} {print $1, $2-1, $2}' > variants.bed   # VCF POS (1-based) -> BED; start-1
bedtools bamtobed -i in.bam > alignments.bed                                       # bedtools handles the convention
bedtools bamtobed -i in.bam -split > spliced.bed                                   # split spliced reads into blocks
bedtools getfasta -fi ref.fa -bed in.bed -name -fo out.fa                          # extract sequence (uses the .fai)
```

## Sort, Validate, and Make Windows

```bash
bedtools sort -i in.bed > sorted.bed                 # lexicographic, == sort -k1,1 -k2,2n
bedtools sort -i in.bed -faidx names.txt > sorted.bed  # reorder to an arbitrary reference contig order
awk -F'\t' '{print NF}' in.bed | sort -u             # field count consistent? (one value expected)
awk -F'\t' '$2 < 0 || $2 >= $3' in.bed               # negative or inverted intervals (bedtools also errors on these)
cut -f1 in.bed | sort -u                             # chromosome names (compare against the partner file)
bedtools makewindows -g genome.txt -w 10000 -s 5000 -i winnum > windows.bed   # 10 kb sliding windows, step 5 kb, numbered
```

## Cross-Assembly Liftover (a different problem from convention conversion)

**Goal:** Move coordinates between genome builds (hg19<->hg38, mm10<->mm39) - which is remapping to a different reference, NOT the 0-based/1-based convention shift above.

**Approach:** Map intervals through a chain file with UCSC `liftOver` (BED) or CrossMap (BED/VCF/GFF/BAM/bigWig), and ALWAYS inspect the unmapped file - regions that fail to map (assembly gaps, rearrangements, split/merged contigs) are dropped, and silently ignoring them biases everything downstream.

```bash
liftOver in.hg19.bed hg19ToHg38.over.chain.gz out.hg38.bed unmapped.bed   # UCSC; chain from UCSC goldenPath
wc -l unmapped.bed                                                         # NEVER skip: dropped regions are not random
CrossMap bed GRCh37_to_GRCh38.chain.gz in.bed > out.bed                    # CrossMap also does vcf/gff/bam/bigwig
```

A coordinate is meaningless without its assembly just as it is meaningless without its convention - record the build (and the chain provenance) alongside the file. Liftover is many-to-one and one-to-none in places; never assume a 1:1 round-trip.

## BED12 Block Invariants

BED12 is a referentially-integral structure, not a flat table. `blockStarts` are **offsets from chromStart**, not absolute coordinates; the **first blockStart must be 0**; `blockStarts[last] + blockSizes[last]` must equal `chromEnd - chromStart`; blocks are ascending and non-overlapping. `thickStart/thickEnd` (the CDS) are absolute and independent of the blocks -- a non-coding feature sets both to `chromStart`. Validate by reconstructing absolute exon coordinates (`chromStart + blockStarts[i]`) and confirming they fall inside `[chromStart, chromEnd]`; `bedtools bed12tobed6` explodes a model into per-exon BED6 as a quick sanity reconstruction.

## Per-Method Failure Modes

### Off-by-one at a convention boundary
**Trigger:** treating a GTF/VCF 1-based `start` as a BED `chromStart`. **Mechanism:** the convention is not stored in the data. **Symptom:** every feature 1 bp short; boundary intersections flip; no error. **Fix:** `start - 1, end unchanged`; test the round-trip on a 1 bp feature.

### Chrom-name mismatch
**Trigger:** intersecting `chr`-prefixed against bare-numeral files. **Mechanism:** chrom strings never match. **Symptom:** valid empty/zero result presented as biology. **Fix:** harmonize naming across all files and genome.txt before any cross-file op.

### Lexicographic-vs-version sort under `-sorted`
**Trigger:** two inputs sorted in different chromosome orders. **Mechanism:** sweep-line assumes one shared order and concludes chroms passed each other. **Symptom:** modern bedtools errors out (`chromomsome sort ordering ... is inconsistent`, exit 1); pre-2.25 silently dropped chr10-chr22 and favored low chroms. **Fix:** sort both identically or pass `-g genome.txt`; omit `-sorted` for one-off work.

### CRLF line endings
**Trigger:** file authored/round-tripped through Windows/Excel. **Mechanism:** `\r` glues onto the last field. **Symptom:** "not an integer" or cryptic last-column errors; works in some tools. **Fix:** `dos2unix` or `sed 's/\r$//'`; never edit BED in Excel.

### Stale / generic genome file
**Trigger:** a downloaded chrom.sizes that does not match the aligned FASTA. **Mechanism:** missing contigs or wrong lengths. **Symptom:** `slop`/`complement` run off real ends or drop contigs; `-sorted` order breaks. **Fix:** regenerate from the exact reference FASTA.

### pyranges 0.x idioms on pyranges1
**Trigger:** running 0.x method/attribute names against the `pyranges1` rewrite. **Mechanism:** the rewrite renamed methods and changed DataFrame access. **Symptom:** AttributeError. **Fix:** check `pyranges.__version__` and use the matching API.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Required minimum 3 columns (BED3) | UCSC/hts-specs BEDv1 | chrom/start/end; field count identical on every line |
| BED `score` integer 0-1000 | UCSC spec | maps to browser gray shade; analysis tools tolerate out-of-range, browser clamps |
| narrowPeak/broadPeak `-1` in pValue/qValue/peak | ENCODE narrowPeak.as | means "not assigned", NOT a real value (e.g. p=0.1 or summit at offset 0) |
| Convention shift: start - 1, end unchanged | BED 0-based vs GFF/VCF 1-based | only the start moves; ends coincide at the shared boundary |
| makewindows window/step (e.g. -w 10000 -s 5000) | analysis choice | resolution vs file size; state the size used, do not default silently |
| tabix BED needs `-p bed` (or `-0`) | tabix default is 1-based | `-p bed` sets chrom/start/end cols and 0-based interpretation |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Empty intersect / "no overlap" | chrom naming mismatch (`chr1` vs `1`, `chrM` vs `MT`) | harmonize naming across all files + genome.txt |
| Every feature 1 bp short | converted 1-based->BED without the start-1 (or subtracted from both) | `start - 1, end unchanged`; verify on a 1 bp feature |
| Every coordinate shifted one column right | UCSC MySQL/`SELECT *` table dump prepends a `bin` column (hierarchical binning index, Kent 2002) | drop field 1 before feeding bedtools: `cut -f2-` |
| `-sorted` errors or (old bedtools) favors low chroms | lexicographic vs version sort mismatch | sort both identically or pass `-g genome.txt`; or drop `-sorted` |
| "not an integer" on the last column | CRLF line endings | `dos2unix` / `sed 's/\r$//'` |
| Negative start / past-chrom-end after slop | missing or stale genome file | regenerate genome.txt from the aligned FASTA |
| `bedToBigBed`/`tabix` errors | unsorted input or track lines present | `sort -k1,1 -k2,2n`; strip `track`/`browser`/`#` lines |
| pyranges AttributeError | 0.x vs pyranges1 API mismatch | check `pyranges.__version__`, use matching method names |

## References

- Quinlan AR, Hall IM. 2010. BEDTools: a flexible suite of utilities for comparing genomic features. *Bioinformatics* 26:841-842.
- Dale RK, Pedersen BS, Quinlan AR. 2011. Pybedtools: a flexible Python library for manipulating genomic datasets and annotations. *Bioinformatics* 27:3423-3424.
- Stovner EB, Sætrom P. 2020. PyRanges: efficient comparison of genomic intervals in Python. *Bioinformatics* 36:918-919.
- Kent WJ, Sugnet CW, Furey TS, et al. 2002. The Human Genome Browser at UCSC. *Genome Res* 12:996-1006.
- The Browser Extensible Data (BED) format, hts-specs BEDv1. samtools.github.io/hts-specs/BEDv1.pdf.
- UCSC Genome Browser FAQ: Data File Formats. genome.ucsc.edu/FAQ/FAQformat.html.

## Related Skills

- interval-arithmetic - Set operations (intersect/merge/subtract) on the intervals defined here
- gtf-gff-handling - 1-based annotation parsing and the parent/child gene-model hierarchy
- coverage-analysis - Per-base depth that becomes bedGraph intervals
- alignment-files/sam-bam-basics - BAM-to-BED conversion and the SAM-1-based vs BAM-0-based distinction
- variant-calling/vcf-basics - VCF POS (1-based) to BED conversion and indel left-anchoring
<!-- END FILE: genome-intervals/bed-file-basics/SKILL.md -->

## 子目录：genome-intervals/bedgraph-handling

<!-- BEGIN FILE: genome-intervals/bedgraph-handling/SKILL.md -->
---
name: bio-genome-intervals-bedgraph-handling
description: Generates, normalizes, and converts bedGraph signal tracks (4-column chrom/start/end/value, 0-based half-open) with bedtools genomecov, deepTools bamCoverage/bamCompare/bigwigCompare, bedtools unionbedg, and UCSC bedGraphToBigWig. Covers why a raw coverage bedGraph is not comparable across samples until normalized, the CPM/RPKM/BPM/RPGC normalization menu and the conserved-total assumption that makes them wrong under a global perturbation, the strict sorted-non-overlapping-chrom.sizes bedGraphToBigWig contract that silently corrupts a bigWig, effective-genome-size selection, and bin-size aliasing. Use when building or normalizing a coverage/signal track from a BAM, comparing tracks across samples or conditions, converting bedGraph to a browser-ready bigWig, or diagnosing a track that looks plausible but reports wrong heights.
tool_type: mixed
primary_tool: deeptools
---

## Version Compatibility

Reference examples tested with: deeptools 3.5+, bedtools 2.31+, ucsc-bedgraphtobigwig 445+, pyBigWig 0.3.22+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

bedGraphToBigWig has a hard, under-advertised input contract: the bedGraph must be `LC_COLLATE=C`-sorted by chrom then start, contain non-overlapping intervals, and ship with a chrom.sizes derived from the exact assembly the reads were aligned to. deepTools effective-genome-size tables are occasionally updated between releases - re-check the installed version's table. If code throws an error, introspect the installed tool and adapt the example to match the actual API rather than retrying.

# bedGraph Handling

**"Make me a coverage/signal track I can compare across samples and load in a browser"** -> Generate a per-bin signal track, normalize it onto a common scale (or decide a spike-in is required), then convert the text bedGraph to an indexed bigWig under the strict sort/overlap/chrom.sizes contract.
- CLI: `bamCoverage -b s.bam -o s.bw --normalizeUsing RPGC --effectiveGenomeSize <N>`; `bedtools genomecov -ibam s.bam -bga`; `LC_COLLATE=C sort -k1,1 -k2,2n in.bdg | bedGraphToBigWig /dev/stdin chrom.sizes out.bw`
- Python: `pyBigWig.open('s.bw')` to read/extract; `bw.intervals(chrom, start, end)` returns the bedGraph rows

## The Single Most Important Modern Insight -- A Raw Coverage bedGraph Is a Library-Size Artifact, and the Wrong Normalization Is Worse Than None

Column 4 of a raw coverage bedGraph is not biology - it is sequencing depth. Two libraries of *identical* biology sequenced to different depths produce different heights, so any cross-sample statement ("more signal at this promoter in treatment") on un-normalized tracks is a category error. The modern path skips the text intermediate entirely: **deepTools bamCoverage takes BAM -> normalized bigWig in one step**, because bigWig is indexed, binary, random-access and bedGraph is flat text. Three load-bearing moves:

1. **Every library-size normalization (CPM/RPKM/BPM/RPGC=1x) assumes total signal is conserved across samples.** They all just rescale each library to a common total (per-million reads, or to 1x genome coverage). That model is correct when signal only *redistributes* locally - the usual case - and **actively wrong** when the perturbation changes *global* levels (histone-mark KD, BET-bromodomain inhibitor, global pol-II collapse). A genuine 3-fold global increase becomes, after CPM/RPGC, *no change* - the extra signal is spread thin and rescaled away. The model is unfalsifiable from the normalized data: forcing both libraries to the same total defines away any global difference. **Library-size normalization assumes the very thing under measurement does not happen.**
2. **There is no computational rescue for a global change after the fact.** The only fix is an external ruler decided AT THE BENCH - a spike-in of fixed foreign chromatin per cell (ChIP-Rx, Orlando 2014; defined reference epigenome, Bonhoure 2014) - scaled by the spike-in reads, not the sample reads. The wet-lab decision had to be made before sequencing; with no spike-in, the global scale is unrecoverable. The mechanics live in chip-seq/spike-in-normalization; the *decision* (could this perturbation change global levels?) belongs here, up front.
3. **bedGraph is scratch; bigWig is the artifact.** The text bedGraph is the last human-readable checkpoint - `awk '$4 > 1000'` to find blacklist pileups, confirm the sort/overlap invariants - before opaque binary. Inspect it, then ship bigWig. Never distribute a bedGraph as a final product: it is unindexed, so a browser reads the whole file to render any region.

## Normalization Taxonomy

| Method | What it assumes | When to use | When WRONG |
|--------|-----------------|-------------|------------|
| None | nothing (raw counts) | single-sample inspection only | any cross-sample comparison - depth confounds it |
| CPM | total mapped reads is the right denominator; total signal conserved | depth-only normalization; quick cross-sample on a common assay | a few high-coverage bins dominate (composition skew); global change |
| RPKM | as CPM plus bin length matters; total signal conserved | legacy default; depth + bin-length normalized | composition skew; global change; superseded by BPM for tracks |
| BPM (TPM-analog) | sum over all bins fixed at 1e6; total signal conserved | composition-aware cross-sample default; robust to a few dominant bins | global change (still a conserved-total rescale) |
| RPGC (1x) | mean genome-wide coverage = 1x; correct effective-genome-size; total signal conserved | field-standard ChIP/ATAC browser viewing; most interpretable height | wrong effective-genome-size (linear scaling error); global change |
| spike-in (external) | spike-in amount is constant per cell (a ruler that does not move) | global-level change plausible or under test | nothing computational - requires a bench step before sequencing |

All five library-size methods share one axiom: **total signal is conserved**. The decision is not which library-size method, it is whether library-size normalization is legitimate at all (see Decision Tree).

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| One BAM -> browser track, local redistribution | `bamCoverage --normalizeUsing RPGC --effectiveGenomeSize <N>` | one-step BAM->normalized bigWig; RPGC is the interpretable ChIP/ATAC standard |
| Cross-sample, composition skew likely | `bamCoverage --normalizeUsing BPM` | bins-per-million fixes the per-bin sum; robust to dominant bins |
| Global-level change plausible (KD/KO of a chromatin modifier, BET inhibitor) | spike-in -> chip-seq/spike-in-normalization | library-size normalization erases the global change by construction |
| RNA-seq coverage track | `bamCoverage --filterRNAstrand` or `genomecov -bga -split` | `-split`/strand handling so spliced reads do not paint introns |
| ChIP/ATAC track | add `--extendReads` (and `--centerReads` for footprints) | a read is a fragment END; raw read-end coverage is double-humped and wrong |
| Treatment vs input from raw BAMs | `bamCompare -b1 chip.bam -b2 input.bam --operation log2` | normalizes depth THEN does the arithmetic |
| Two already-normalized bigWigs | `bigwigCompare --operation log2` | arithmetic only - feeding un-normalized tracks manufactures a fake change |
| Stack N samples into a value matrix | `bedtools unionbedg -header -names ...` | union interval partition; feed the matrix to R/Python for testing |
| Sample-relatedness QC | `multiBigwigSummary bins` -> `plotCorrelation`/`plotPCA` | genome-wide value matrix for correlation/PCA |
| Need exact per-base arithmetic (not a browser) | keep bedGraph (`genomecov -bga`) | bedGraph is exact text; bigWig is binned/lossy |
| Convert finished bedGraph -> bigWig | `LC_COLLATE=C sort` then `bedGraphToBigWig` + matched chrom.sizes | the strict contract; inspect the text first |

## Generate a Normalized Track with bamCoverage (the modern default)

**Goal:** Turn one BAM into a normalized, browser-ready bigWig in a single command.

**Approach:** Let bamCoverage bin, normalize, and write bigWig directly; pick the normalization from the taxonomy, supply the effective-genome-size for RPGC, extend reads for ChIP/ATAC, and exclude chrX/chrM (and any spike-in contigs) from the scale-factor calculation.

```bash
BIN_SIZE=25                  # bp; smaller = finer + noisier + bigger. Match to feature width (sharp TF/ATAC 10-25; broad marks 50-200)
EFFGENOME=2913022398         # GRCh38 non-N length (faCount); use ONLY if multimappers were kept (see Effective Genome Size)

bamCoverage -b sample.bam -o sample.bw \
  --binSize $BIN_SIZE --normalizeUsing RPGC --effectiveGenomeSize $EFFGENOME \
  --extendReads --ignoreForNormalization chrX chrM -p 8
```

Defaults to verify: `--binSize 50`, `--normalizeUsing None`, `--scaleFactor 1.0`, `--extendReads` off, `--centerReads` off. For single-end ChIP supply the fragment length (`--extendReads 200`); paired-end infers it. `--scaleFactor` with `--scaleFactorsMethod None` is the hook for a bench-derived spike-in factor. `--outFileFormat bedgraph` writes the text form when the raw numbers are needed.

## Generate with bedtools genomecov (text, flexible, no normalization)

`-bg` collapses equal-coverage runs but **omits zero-coverage regions**; `-bga` additionally tiles zeros (use when downstream tools need explicit 0s). `-split` is mandatory for RNA-seq so spliced reads do not paint introns. `-scale 1000000/<nreads>` is a crude manual RPM; deepTools is preferred for real normalization.

```bash
bedtools genomecov -ibam sample.bam -bga -split > sample.bedgraph
```

## Convert bedGraph -> bigWig (the silent-corruption trap)

**Goal:** Produce a valid bigWig from a finished bedGraph without shipping a file that loads but lies.

**Approach:** C-locale-sort, guarantee non-overlapping intervals, derive chrom.sizes from the exact aligned-to FASTA, inspect the text, then convert.

```bash
samtools faidx ref.fa && cut -f1,2 ref.fa.fai > chrom.sizes   # chrom.sizes from the SAME FASTA the reads aligned to
LC_COLLATE=C sort -k1,1 -k2,2n sample.bedgraph > sample.sorted.bedgraph   # C locale: locale-aware sort triggers "is not case-sensitive sorted"
bedGraphToBigWig sample.sorted.bedgraph chrom.sizes sample.bw
```

If concatenation/merging introduced overlaps, collapse with an explicit aggregation BEFORE converting - and note `max` vs `mean` vs `sum` are different signals, there is no safe default:

```bash
bedtools merge -i sample.sorted.bedgraph -d 0 -c 4 -o max > sample.nonoverlap.bedgraph
```

bigWig round-trips losslessly: `bigWigToBedGraph sample.bw out.bedgraph` (optionally `-chrom=chr1 -start=1000 -end=2000`).

## Multi-Sample Arithmetic

**Goal:** Compare two tracks (treatment/input, two conditions) without letting a depth difference masquerade as biology.

**Approach:** From raw BAMs use bamCompare, which normalizes depth THEN applies the operation; only use bigwigCompare on bigWigs that are *already* on a common scale.

```bash
bamCompare -b1 chip.bam -b2 input.bam -o log2ratio.bw \
  --operation log2 --pseudocount 1 --binSize 25 --scaleFactorsMethod readCount
```

`--operation` (NOT `--ratio`) chooses log2/ratio/subtract/add/mean/reciprocal_ratio/first/second; default `log2`. `--scaleFactorsMethod readCount` (the default) scales by library size; `--scaleFactorsMethod SES` (signal-extraction scaling, Diaz 2012) instead estimates the factor from the shared background bins and is more robust than readCount for SHARP/punctate marks and TF ChIP where enrichment is a small genomic fraction; it DEGRADES for broad marks (H3K27me3/H3K9me3) where the diffuse enrichment cannot be cleanly separated from background, so use readCount (or spike-in) there. `--pseudocount` (default 1) prevents divide-by-zero in log2/ratio but pulls low-coverage bins toward 0 - a log2 track's apparent dynamic range is partly a pseudocount+bin-size artifact, do not read fold-changes off a browser track as measured. `bigwigCompare --skipZeroOverZero` drops bins that are 0 in both rather than flooding the output with `log2(1)=0`. Stack many samples and QC relatedness:

```bash
bedtools unionbedg -i s1.bdg s2.bdg s3.bdg -header -names s1 s2 s3 > matrix.txt   # inputs must be coordinate-sorted
multiBigwigSummary bins -b s1.bw s2.bw s3.bw -o scores.npz && plotCorrelation -in scores.npz --corMethod spearman --whatToPlot heatmap -o corr.png
```

## Read/Extract Signal with pyBigWig

```python
import pyBigWig

bw = pyBigWig.open('sample.bw')
mean_over_region = bw.stats('chr1', 1_000_000, 1_010_000, type='mean')[0]   # binned summary, not per-base
rows = bw.intervals('chr1', 1_000_000, 1_010_000)   # the underlying bedGraph rows: (start, end, value)
bw.close()
```

`bw.stats()`/`bw.values()` return what the bin resolution preserved, not a faithful per-base record - coarse bins silently change the values read back.

## Effective Genome Size (the two-table trap)

`--effectiveGenomeSize` feeds the RPGC scale factor and depends on the read-filtering regime. deepTools ships two tables that answer different questions:

| Build | Non-N length (faCount; multimappers KEPT) |
|-------|--------------------------------------------|
| GRCh38 | 2,913,022,398 |
| GRCh37 | 2,864,785,220 |
| GRCm38 (mm10) | 2,652,783,500 |
| dm6 | 142,573,017 |
| WBcel235 (C. elegans) | 100,286,401 |

When reads were instead **filtered to unique alignments / a MAPQ filter applied** (the common ChIP/ATAC case), use the read-length-dependent unique-k-mer value: GRCh38 is 2,701,495,711 (50 bp), 2,805,636,231 (100 bp), 2,862,010,428 (150 bp). The two GRCh38 numbers differ ~7% at short read length. RPGC scales linearly in this value, so the error cancels for *within-study* ratios but surfaces as a spurious constant fold-difference on cross-study integration (a public track, a collaborator's bigWig, a track made last year at a different read length). For non-model organisms there is no table - estimate it (`faCount` for non-N length, or unique-k-mers on the assembly).

## Per-Method Failure Modes

### Comparing un-normalized tracks across samples
**Trigger:** browser-comparing or quantifying raw coverage bedGraphs/bigWigs. **Mechanism:** column 4 scales with library size. **Symptom:** the deeper library looks like it has "more signal" everywhere. **Fix:** normalize during bamCoverage; never compare `--normalizeUsing None` tracks.

### Conserved-total assumption under a global change
**Trigger:** CPM/RPKM/BPM/RPGC on a perturbation that shifts global levels (chromatin-modifier KD/KO, BET inhibitor). **Mechanism:** every library-size method forces total signal to a constant. **Symptom:** a real global increase reads as no change; tracks look identical. **Fix:** spike-in decided at the bench -> chip-seq/spike-in-normalization. No computational rescue exists.

### Unsorted / overlapping input -> corrupt bigWig
**Trigger:** `bedGraphToBigWig` on non-C-sorted or overlapping input, or chrom.sizes from the wrong assembly. **Mechanism:** the contract is enforced inconsistently - some violations error, others build a bigWig that loads and shows wrong heights or silently drops chromosomes. **Symptom:** `is not case-sensitive sorted`, `overlapping regions`, `end coordinate bigger than`, or a silently wrong/incomplete track. **Fix:** `LC_COLLATE=C sort`; `bedtools merge -c 4 -o max/mean/sum`; chrom.sizes from the exact aligned-to FASTA; harmonize `chr1` vs `1`.

### Effective-genome-size drift
**Trigger:** grabbing the round 2.9e9 GRCh38 value regardless of multimapper filtering, or reusing a value across read lengths/assemblies. **Mechanism:** RPGC scales linearly in the value; the two tables differ ~7%. **Symptom:** invisible within a study; a spurious constant fold-difference on cross-study integration. **Fix:** match the value to the read length AND filtering regime; estimate it for non-model organisms.

### Bin-size aliasing
**Trigger:** a bin wider than ~half the feature, or comparing tracks built at different binSizes. **Mechanism:** binSize is a low-pass filter chosen once; a feature narrower than ~2 bins is averaged down or straddles a boundary (a phase artifact - replicates disagree by bin alignment). **Symptom:** sharp peaks shrink or split; bin-for-bin ratios meaningless at boundaries. **Fix:** match binSize to feature width (sharp TF/ATAC 10-25 bp, broad marks 50-200 bp); compared tracks MUST share binSize. `--smoothLength` is cosmetic, it cannot recover discarded information.

### ChIP/ATAC track without extendReads
**Trigger:** bamCoverage/genomecov on ChIP/ATAC without `--extendReads`. **Mechanism:** a read marks a fragment END, not the fragment. **Symptom:** double-humped peaks with a central dip; biased boundaries and quantification. **Fix:** `--extendReads` (paired-end infers; single-end supply the fragment length). RNA-seq mirror trap: without `-split` spliced reads paint introns.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| binSize default 50 bp; sharp TF/ATAC 10-25 bp, broad marks 50-200 bp | deepTools default + feature-width matching | binSize is a low-pass filter; finer is noisier/bigger, coarser aliases sharp features |
| GRCh38 effGenome 2,913,022,398 (multimappers kept) | deepTools faCount table | non-N genome length for the RPGC denominator |
| GRCh38 effGenome 2.70-2.86e9 by read length (unique alignments) | deepTools unique-k-mer table | ~7% below the non-N value; use when MAPQ/uniqueness-filtered |
| pseudocount default 1 (log2/ratio) | deepTools default | prevents divide-by-zero; biases low-coverage bins toward 0 |
| single-end fragment length ~200 bp (`--extendReads 200`) | typical sonicated ChIP fragment | wrong value distorts peak width; paired-end infers it |
| compared tracks must share binSize | signal-processing constraint | different grids make bin-for-bin ratios meaningless |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `is not case-sensitive sorted` | locale-aware sort | `LC_COLLATE=C sort -k1,1 -k2,2n` (works on a login node, fails in the scheduler when `$LC_*` differ) |
| `overlapping regions in bedGraph file` | concatenated/merged tracks | `bedtools merge -c 4 -o max/mean/sum` (choose the aggregation deliberately) |
| `end coordinate N bigger than ...` | chrom.sizes from a different assembly/patch | derive chrom.sizes from the exact aligned-to FASTA (`samtools faidx` + `cut -f1,2`) |
| Whole chromosomes missing from the bigWig, no error | `chr1` vs `1` / `MT` vs `chrM` naming mismatch | harmonize naming across bedGraph and chrom.sizes |
| Track line breaks sort/conversion | `track type=bedGraph ...` header row | remove the track line before sort/bedGraphToBigWig |
| RPGC normalization fails | `--effectiveGenomeSize` not supplied | pass the correct value for the build, read length, and filtering |
| Spliced reads paint introns | no `-split` (genomecov) / wrong RNA mode | `genomecov -bga -split` or bamCoverage `--filterRNAstrand` |

## References

- Ramírez F, Ryan DP, Grüning B, et al. 2016. deepTools2: a next generation web server for deep-sequencing data analysis. *Nucleic Acids Res* 44:W160-W165.
- Kent WJ, Zweig AS, Barber G, Hinrichs AS, Karolchik D. 2010. BigWig and BigBed: enabling browsing of large distributed datasets. *Bioinformatics* 26:2204-2207.
- Quinlan AR, Hall IM. 2010. BEDTools: a flexible suite of utilities for comparing genomic features. *Bioinformatics* 26:841-842.
- Orlando DA, Chen MW, Brown VE, et al. 2014. Quantitative ChIP-Seq normalization reveals global modulation of the epigenome. *Cell Reports* 9:1163-1170.
- Bonhoure N, Bounova G, Bernasconi D, et al. 2014. Quantifying ChIP-seq data: a spiking method providing an internal reference for sample-to-sample normalization. *Genome Res* 24:1157-1168.
- Diaz A, Park K, Lim DA, Song JS. 2012. Normalization, bias correction, and peak calling for ChIP-seq. *Stat Appl Genet Mol Biol* 11:Article 9.

## Related Skills

- coverage-analysis - Per-base depth generation and distribution-vs-mean diagnostics feeding bedGraph tracks
- bigwig-tracks - Reading, extracting, and writing the bigWig deliverable this skill produces
- chip-seq/spike-in-normalization - The bench-decided external-reference scaling when a global change makes library-size normalization wrong
- chip-seq/chipseq-visualization - Render the normalized signal tracks built here
- atac-seq/footprinting - Consumes high-resolution coverage/bigWig signal over motif sites
- data-visualization/genome-tracks - Render the bedGraph/bigWig tracks for figures
<!-- END FILE: genome-intervals/bedgraph-handling/SKILL.md -->

## 子目录：genome-intervals/bigwig-tracks

<!-- BEGIN FILE: genome-intervals/bigwig-tracks/SKILL.md -->
---
name: bio-genome-intervals-bigwig-tracks
description: Reads, queries, and writes bigWig indexed binary signal tracks (coverage, fold-change, conservation, methylation-rate) with pyBigWig (Python) and the UCSC Kent tools (bedGraphToBigWig, bigWigToBedGraph, bigWigInfo, bigWigSummary, bigWigAverageOverBed) and deepTools (multiBigwigSummary, computeMatrix, bigwigCompare). Covers the central trap that a wide query returns a precomputed zoom-level summary (by default the mean, which annihilates narrow peaks) not per-base data, when exact=True/values() is mandatory, the NaN-not-zero gap-handling fork, choosing mean vs max vs sum vs coverage by biological question, and the sorted-bedGraph plus chrom.sizes build requirement. Use when extracting signal at regions, computing mean signal per gene/peak, building a browser track from bedGraph, comparing tracks, or building TSS/gene-body metaprofiles.
tool_type: mixed
primary_tool: pyBigWig
---

## Version Compatibility

Reference examples tested with: pyBigWig 0.3.22+, numpy 1.26+, ucsc-bedgraphtobigwig/ucsc-tools 469+, deeptools 3.5+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` (or `bigWigInfo` with no args for usage) then `<tool> --help` to confirm flags
- Python: `pip show pyBigWig` then `help(pyBigWig.bigWigFile.stats)` to check signatures

Building any bigWig needs a chrom.sizes file (`name<TAB>length`) and a coordinate-sorted bedGraph; pyBigWig's numpy return path requires numpy present at compile time. If code throws an error, introspect the installed tool and adapt rather than retrying.

# BigWig Tracks

**"Get the signal from my bigWig over these regions / build a browser track."** -> Query an indexed binary signal track, choosing the summary statistic and exactness that match the biological question, or build one from a sorted bedGraph + chrom.sizes.
- CLI: `bigWigAverageOverBed in.bw regions.bed out.tab`, `bigWigSummary in.bw chr s e N -type=max`, `bedGraphToBigWig in.sorted.bedGraph chrom.sizes out.bw`, `bigWigInfo in.bw`
- Python: `bw=pyBigWig.open('x.bw')`, `bw.stats(chr,s,e,type='max',exact=True)`, `bw.values(chr,s,e,numpy=True)`, `bw.intervals(chr,s,e)` (pyBigWig)

## The Single Most Important Modern Insight -- A Wide Query Returns a Zoom-Level Summary, Not the Underlying Data

bigWig is fast (Kent 2010) because it stores, alongside base-resolution values, a ladder of precomputed zoom levels holding per-bin sum/sumSquared/min/max/nBasesCovered. A B+ tree resolves the chromosome, an R-tree (cirTree) finds the data blocks in O(log n), per-block zlib keeps it ~10x smaller than bedGraph, and **the zoom ladder answers a wide region in near-constant time by reading a precomputed summary instead of the base data.** That speed is bought with two stacked approximations, both ON by default, and a third trap at the moment the signal is reduced to a single number:

1. **WHICH statistic.** Over one wide bin `mean` (the default) dilutes a narrow tall feature toward background: a 200 bp ChIP summit of 500 in a 1 Mb sea of 1 averages to ~1.1 -- indistinguishable from background, while `type='max'` returns 500. **Same file, same coordinates, opposite conclusions, decided by the named statistic.** `mean` is faithful for broad features (domains, gene-body coverage) and a lie for narrow ones. `max`=peak height, `sum`=total amount (scales with width), `coverage`=fraction of bases with any data (ignores magnitude), `std`=variability.
2. **WHERE the number comes from.** `exact=False` (the pyBigWig default, and what `bigWigSummary` and every zoomed-out browser do) computes from the nearest zoom level, not base data. Fine for exploration and broad features; **`exact=True` (or `values()`) is mandatory whenever a number enters a result** -- a per-region average in a table, a threshold call, anything a reviewer recomputes. Plausible-but-zoom-approximated is the worst failure: it does not error, it rounds the biology.
3. **NaN is NOT zero.** Uncovered positions are no-data, surfaced as `NaN` in `values()` and as gaps between `intervals()` runs -- never 0. On a region 30% covered at signal 10: `np.mean` -> **NaN** (poisons), `np.nanmean` -> **10** (covered-only, = `bigWigAverageOverBed` `mean` column), gaps-as-zero (`np.nan_to_num().mean()`, deepTools `--missingDataAsZero`, the `mean0` column) -> **3.0**. A >3x swing in the headline number, and which is correct is **biological**: coverage/read-depth tracks -> gaps are zero (`mean0`); rate/ratio tracks (methylation %, log2FC, conservation) -> gaps are undefined (`mean`/`nanmean`).

Name the biological question first; the statistic, the `exact` flag, and the gap-handling then follow deterministically. Left on default, all three conspire to hand back a fast, confident, wrong answer.

## Tool Taxonomy

| Tool | Role | Mechanism | When |
|------|------|-----------|------|
| pyBigWig | Python read/write | C-extension over libBigWig; `stats`/`values`/`intervals`/`addEntries` | inside a Python pipeline; custom per-region extraction; writing a bigWig |
| bigWigAverageOverBed | mean signal per BED region | one row per feature; `name,size,covered,sum,mean0,mean` | the right tool for "average signal per gene/peak"; gives both mean0 and mean |
| bigWigSummary | region -> N equal bins | reads zoom levels (like `exact=False`); `-type=mean/min/max/std/coverage` | quick binned profile at the command line |
| bigWigInfo | header/stats sanity check | version, zoom-level count, basesCovered, min/max/mean without parsing data | first thing to run on an unfamiliar file |
| bedGraphToBigWig / wigToBigWig | build bigWig | needs sorted input + chrom.sizes | converting a coverage bedGraph/WIG to a track |
| bigWigToBedGraph / bigWigToWig | bigWig -> text | `-chrom/-start/-end` for a sub-region | exact arithmetic; inspecting values as text |
| multiBigwigSummary | score matrix across many bigWigs | mean per bin over genome `bins` or a `BED-file` | track correlation/PCA (-> `plotCorrelation`/`plotPCA`) |
| computeMatrix | signal across many regions | `reference-point` (TSS/peak center) or `scale-regions` (gene body) | metaprofiles/heatmaps (-> `plotHeatmap`/`plotProfile`) |
| bigwigCompare | combine two bigWigs bin-by-bin | `--operation log2/ratio/subtract/...` `--pseudocount` | a log2(IP/input) or (treat-control) track |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Mean signal per gene/peak (one number per BED row) | `bigWigAverageOverBed` | purpose-built; pick `mean` (covered-only) vs `mean0` (gaps as zero) deliberately |
| Peak height / "is there a binding event here?" | `stats(type='max')` or `bigWigSummary -type=max` | `mean` dilutes a narrow peak to background |
| Total signal over an exon/gene (an amount) | `stats(type='sum')` or the `sum` column | extensive quantity; do not use `mean` for a total |
| A number going into a table/threshold | `stats(..., exact=True)` or `values()` | the default `exact=False` reads zoom levels, not base data |
| Per-base values for plotting/analysis | `values(numpy=True)` | one number per base; `nan` for gaps -> `np.nanmean`, never `np.mean` |
| "Is this region even assayed/mappable?" | `stats(type='coverage')` | fraction with data; a different axis from magnitude |
| Compare many tracks (correlation/PCA) | `multiBigwigSummary` -> `plotCorrelation`/`plotPCA` | mean per bin; bin size matters |
| Metaprofile/heatmap over TSS or gene bodies | `computeMatrix reference-point`/`scale-regions` -> `plotHeatmap`/`plotProfile` | match anchored-point vs whole-body mode |
| A ratio/difference track | `bigwigCompare --operation log2 --pseudocount` | pseudocount only meaningful for log2/ratio |
| Build a normalized coverage track from a BAM | -> chip-seq/chipseq-visualization or atac-seq/footprinting (deepTools `bamCoverage`) | generation is upstream; library-size normalization lives there |
| Render the track in a browser figure | -> data-visualization/genome-tracks | pyGenomeTracks/IGV; zoom-out IS the summary trap made visual |
| Discrete features (peaks/genes), not signal | bigBed, not bigWig | continuous-vs-interval; one interval per base defeats the format |

## Inspect a File Before Trusting It

```bash
bigWigInfo coverage.bw                  # version, # zoom levels, basesCovered, min/max/mean/std
bigWigInfo -chroms coverage.bw          # chrom names + lengths (the file carries its own chrom list)
```

A zero or low zoom-level count means a zoomed-out browser will read base data slowly (or, with `maxZooms=0`, IGV breaks). `basesCovered` far below the genome size means most positions are no-data (NaN), which makes the `mean`-vs-`mean0` choice below load-bearing.

## Mean Signal per Region (the most common task)

**Goal:** Compute one signal number per gene/peak, choosing covered-only vs gaps-as-zero by the track's biology.

**Approach:** Use the purpose-built `bigWigAverageOverBed` (BED needs a unique name column) and read the right output column -- `mean` (covered bases only) for rate/ratio tracks, `mean0` (uncovered counted as zero) for coverage/depth tracks.

```bash
# BED4+ with a UNIQUE name in column 4; output columns: name size covered sum mean0 mean
bigWigAverageOverBed coverage.bw genes.bed signal_per_gene.tab
# -> read $6 (mean, covered-only) for methylation/log2FC; $5 (mean0, gaps=0) for read depth
```

The pyBigWig equivalent, when the extraction is inside a Python pipeline -- note `exact=True` because these numbers enter a result, and an explicit gap decision:

```python
import pyBigWig
import numpy as np

bw = pyBigWig.open('coverage.bw')
GAPS_ARE_ZERO = False   # True for read-depth/coverage tracks; False for rate/ratio (methylation, log2FC)

def region_signal(chrom, start, end):
    v = bw.values(chrom, start, end, numpy=True)                         # per-base, nan for gaps
    if GAPS_ARE_ZERO:
        return float(np.nan_to_num(v).mean())                           # mean0: gaps counted as 0 (= bigWigAverageOverBed mean0)
    return np.nanmean(v) if not np.all(np.isnan(v)) else float('nan')    # covered-only (= bigWigAverageOverBed mean); stats(type='mean') is also covered-only, NOT mean0
```

## Peak Height vs Total vs Coverage (statistic = question)

```python
import pyBigWig
bw = pyBigWig.open('chip.bw')
region = ('chr1', 1_000_000, 2_000_000)

peak  = bw.stats(*region, type='max', exact=True)[0]        # binding-event height; mean would dilute it
total = bw.stats(*region, type='sum', exact=True)[0]        # total signal (amount; scales with width)
assayed = bw.stats(*region, type='coverage', exact=True)[0] # FRACTION of bases with any data (0..1), ignores magnitude
profile = bw.stats(*region, type='max', nBins=1000)         # 1000-bin max profile; nBins keeps narrow features visible
```

`stats()` returns a list of length `nBins` (default 1). `type` is one of `mean`(default)/`max`/`min`/`coverage`/`std`/`sum`. Use `max` with `nBins>1` to see narrow features across a wide window; a single-bin `mean` over a megabase buries every peak.

## Per-Base Values (NaN is not zero)

```python
import pyBigWig
import numpy as np
bw = pyBigWig.open('coverage.bw')

v = bw.values('chr1', 1_000_000, 1_001_000, numpy=True)   # list by default; numpy=True -> ndarray, nan for gaps
covered_mean = np.nanmean(v)                               # ignores gaps (= bigWigAverageOverBed mean)
depth_mean = np.nan_to_num(v).mean()                       # gaps counted as zero (= mean0); only for depth tracks
raw = bw.intervals('chr1', 1_000_000, 1_001_000)          # [(start,end,value),...] the unresampled stored runs
bw.close()
```

## Build a Valid bigWig

**Goal:** Turn a coverage bedGraph into an indexed, browser-ready bigWig.

**Approach:** Coordinate-sort the bedGraph, supply a chrom.sizes whose names and lengths match the bedGraph exactly, and run `bedGraphToBigWig` (which builds the index + zoom levels).

```bash
sort -k1,1 -k2,2n coverage.bedGraph > coverage.sorted.bedGraph   # bedGraphToBigWig REQUIRES sorted, non-overlapping input
cut -f1,2 reference.fa.fai > chrom.sizes                          # or fetchChromSizes hg38 > chrom.sizes
bedGraphToBigWig coverage.sorted.bedGraph chrom.sizes coverage.bw
```

Writing directly with pyBigWig -- `addHeader` (ordered chrom list) MUST precede `addEntries`, and entries must be added in sorted (chrom, start) order matching the header:

```python
import pyBigWig
bw = pyBigWig.open('out.bw', 'w')
bw.addHeader([('chr1', 248956422)])   # ordered (name,length); maxZooms default 10; maxZooms=0 disables zoom and breaks IGV
bw.addEntries(['chr1'], [0], ends=[100], values=[1.5])           # mode (a) variable intervals
# mode (b) variableStep: bw.addEntries('chr1', [0,100], values=[1.5,2.3], span=20)
# mode (c) fixedStep:    bw.addEntries('chr1', 0, values=[1.5,2.3], span=20, step=30)
bw.close()                            # close() builds the R-tree index + zoom ladder
```

## Compare and Profile Tracks (deepTools)

```bash
bigwigCompare -b1 treat.bw -b2 control.bw -o log2ratio.bw --operation log2 --pseudocount 1   # NOT --ratio (older flag name)
multiBigwigSummary BED-file -b a.bw b.bw -o scores.npz --BED regions.bed                      # then plotCorrelation/plotPCA
computeMatrix reference-point -S signal.bw -R tss.bed -b 2000 -a 2000 -o matrix.gz            # anchored on TSS
plotHeatmap -m matrix.gz -o heatmap.png
```

Both `bigwigCompare` and `multiBigwigSummary` use mean-per-bin, so the zoom-level dilution caveat above applies; `computeMatrix --missingDataAsZero` is the same NaN-vs-zero fork inside deepTools.

## Per-Method Failure Modes

### Wide mean read as the peak
**Trigger:** `bw.stats(chrom, start, end)` (default `type='mean'`) over a region wide relative to the feature. **Mechanism:** the mean dilutes a narrow tall peak toward background. **Symptom:** "no signal here" that a browser zoom-in contradicts. **Fix:** use `type='max'` (or `nBins>1`, or `values()`) for narrow features.

### exact=False leaks zoom approximations into a result
**Trigger:** shipping default-`exact` `stats()` numbers into a table/threshold. **Mechanism:** the value is computed from the nearest zoom level, not base data, at up to 16x coarser granularity. **Symptom:** plausible numbers a reviewer cannot reproduce. **Fix:** pass `exact=True` (or use `values()`/`bigWigAverageOverBed`) whenever a number enters a result.

### Averaging NaN as zero (or poisoning to NaN)
**Trigger:** `np.mean(bw.values(...))` over a track with gaps, or `mean0` on a rate track. **Mechanism:** `np.mean` poisons to NaN; `nan_to_num`/`mean0`/`--missingDataAsZero` averages real gaps as zeros. **Symptom:** a >3x swing or a NaN where a number was expected. **Fix:** decide biologically -- coverage track -> `mean0`/zero; rate/ratio track -> `mean`/`np.nanmean`.

### addEntries before addHeader (or out of order)
**Trigger:** writing entries before the header, or in non-sorted order. **Mechanism:** the chrom list and offsets must exist and be ordered before data is appended. **Symptom:** runtime error or a corrupt file. **Fix:** `addHeader([(chrom,length),...])` first, add entries in (chrom, start) order matching the header; `close()` to finalize.

### chrom.sizes / naming mismatch on build
**Trigger:** `bedGraphToBigWig` with a chrom.sizes from a different assembly or naming (`chr1` vs `1`). **Mechanism:** the builder validates intervals against chrom lengths. **Symptom:** `chromosome not found`, or silently dropped/truncated intervals. **Fix:** derive chrom.sizes from the same reference (`cut -f1,2 ref.fa.fai`); harmonize naming; sort first.

### Forcing peaks into a bigWig (or dense signal into bigBed)
**Trigger:** storing called peaks as a bigWig. **Mechanism:** bigWig is continuous signal; discrete features with per-feature metadata belong in bigBed. **Symptom:** lost boundaries/names, or an enormous one-interval-per-base file. **Fix:** signal -> bigWig; intervals/features -> bigBed.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `exact=True` when a number enters a result | pyBigWig design | default `exact=False` reads zoom levels (up to ~16x coarser than data); fine for exploration only |
| Zoom ladder: smallest bin ~16x mean interval size, each level 4x the previous | Kent 2010 convention | the resolution at which a wide query is answered; `bigWigInfo -zooms` shows the actual levels |
| Index < ~1% of data; ~10x smaller than bedGraph | Kent 2010 | order-of-magnitude; exact ratio is data-dependent (sparse vs dense) |
| bedGraph must be sorted `-k1,1 -k2,2n`, non-overlapping | bedGraphToBigWig requirement | signal is a function (one value per base); unsorted/overlapping input errors out |
| computeMatrix flank `-b/-a` 2000-3000 bp at TSS | metaprofile convention | captures promoter-proximal signal; widen for distal features; state the value used |
| bin size (e.g. 10-50 bp) | resolution vs file size | finer bins preserve narrow features but enlarge the file; state the bin when reading values back |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Region reads flat but browser shows a peak | wide `mean` query diluted the peak | use `type='max'`, more bins, or zoom to feature resolution |
| Per-region numbers a reviewer cannot reproduce | `exact=False` zoom approximation | re-extract with `exact=True` / `bigWigAverageOverBed` |
| `np.mean` returns NaN | gaps in the track (NaN, not 0) | `np.nanmean`, or `np.nan_to_num` if gaps are biologically zero |
| `mean` and `mean0` differ a lot in `bigWigAverageOverBed` | track is sparsely covered | pick the column by biology (depth -> mean0; rate -> mean) |
| `bedGraphToBigWig` errors / drops intervals | unsorted input or chrom-name/length mismatch | `sort -k1,1 -k2,2n`; match chrom.sizes to the reference |
| IGV will not render zoom-out | bigWig built with `maxZooms=0` | rebuild with zoom levels (default 10) |
| `bigwigCompare` rejects `--ratio` | flag renamed | use `--operation log2` |

## References

- Kent WJ, Zweig AS, Barber G, Hinrichs AS, Karolchik D. 2010. BigWig and BigBed: enabling browsing of large distributed datasets. *Bioinformatics* 26:2204-2207.
- Ramirez F, Ryan DP, Gruning B, Bhardwaj V, Kilpert F, Richter AS, Heyne S, Dundar F, Manke T. 2016. deepTools2: a next generation web server for deep-sequencing data analysis. *Nucleic Acids Res* 44:W160-W165.
- pyBigWig (Devon Ryan / deepTools project) - C-extension wrapping libBigWig; no journal paper, see https://github.com/deeptools/pyBigWig
- UCSC Kent utilities (bedGraphToBigWig, bigWigInfo, bigWigSummary, bigWigAverageOverBed) - https://github.com/ucscGenomeBrowser/kent; cite Kent 2010 for the format.

## Related Skills

- bedgraph-handling - The text bedGraph this skill converts to/from, and exact-arithmetic alternative
- coverage-analysis - Generates the per-base depth/bedGraph that becomes a bigWig
- bed-file-basics - The region BED files passed to bigWigAverageOverBed/computeMatrix
- chip-seq/chipseq-visualization - Generates normalized tracks (bamCoverage) and renders computeMatrix metaprofiles
- atac-seq/footprinting - Consumes bigWig signal over motif sites
- data-visualization/genome-tracks - Renders the bigWig in a browser figure (where zoom-out is the summary trap made visual)
<!-- END FILE: genome-intervals/bigwig-tracks/SKILL.md -->

## 子目录：genome-intervals/coverage-analysis

<!-- BEGIN FILE: genome-intervals/coverage-analysis/SKILL.md -->
---
name: bio-genome-intervals-coverage-analysis
description: Computes and interprets sequencing read depth and coverage over a genome, windows, or target regions with mosdepth (windowed depth, cumulative distribution, --quantize callable BEDs), bedtools genomecov/coverage (bedGraph tracks, per-target stats), samtools depth/coverage (per-base depth, per-contig depth+breadth). Covers the breadth-vs-mean distinction, the cumulative-coverage curve, evenness (CV/Fano/fold-80/Gini), what each tool silently counts (duplicates, secondary/supplementary, MAPQ, read span vs fragment, mate-overlap), the samtools-depth 8000-cap version trap, and the bedtools coverage -a/-b orientation flip. Use when assessing sequencing adequacy, building coverage tracks, computing breadth at a depth threshold, defining callable regions, or QCing target-capture uniformity.
tool_type: mixed
primary_tool: bedtools
---

## Version Compatibility

Reference examples tested with: bedtools 2.31+, mosdepth 0.3+, samtools 1.19+, pybedtools 0.10+, numpy 1.26+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

`samtools depth` behaviour changed across versions: pre-1.13 capped depth at 8000 and truncated silently (`-d 0` = unlimited); 1.13+ rewrote the subcommand with NO cap and `-d/-m` deprecated/ignored. Always check `samtools --version` before trusting a max-depth number. If code throws an error, introspect the installed tool and adapt rather than retrying.

# Coverage Analysis

**"Is my sequencing deep enough to answer the question?"** -> Measure depth as a distribution over positions, then report median, breadth at a depth threshold, and an evenness number -- never the mean alone.
- CLI: `mosdepth --by 500 prefix in.bam` (windowed depth + cumulative dist), `samtools coverage in.bam` (per-contig depth+breadth), `bedtools genomecov -ibam in.bam -bga` (bedGraph track)
- Python: `pybedtools.BedTool('in.bam').genome_coverage(bga=True)` (pybedtools); parse `prefix.mosdepth.global.dist.txt` for the breadth curve

## The Single Most Important Modern Insight -- Mean Depth Is a Budget, Not a Result; Report Breadth Off a Cumulative Curve

"30x WGS" describes what was paid for, not what was achieved. Coverage is a **distribution over positions**, and the mean is its worst summary: it is dragged **up** by a fat right tail (repeats, rDNA, mitochondria, PCR pileups, segmental dups) while staying **blind** to a hard left wall of zeros and near-zeros (GC-extreme exons, poorly-mappable regions, capture dropout). Two libraries with identical mean 30x can differ completely -- one even and callable everywhere, one spiky with 20% of the target uncallable. The mean hides both failures. Four load-bearing moves:

1. **Report MEDIAN, not mean.** The median is robust to the right tail. When mean/median exceeds ~1.1-1.2 the distribution is skewed and the mean is overstating typical depth -- that gap is a free evenness diagnostic.
2. **Report a BREADTH / cumulative-coverage curve.** "% of target >= 1x, >= 10x, >= 20x, >= 30x" is the honest summary, because adequacy is a breadth statement: a base that was not covered deeply enough is uncallable no matter how deep the rest of the genome is. mosdepth's `*.mosdepth.global.dist.txt` IS this curve. The killer question for any "mean = 30x" claim is "breadth at 20x?".
3. **Quantify EVENNESS** (CV, Fano factor, Picard fold-80, or Gini) -- an even 30x and a spiky 30x are different experiments, and a spiky library cannot be rescued by sequencing deeper (extra reads follow the same biased distribution; the holes stay holes). Fix the library (PCR-free, better capture, UMIs), not the lane count.
4. **Say WHAT WAS COUNTED.** A depth number is meaningless until the recipe is stated: duplicates dropped (only if MARKED first)? secondary/supplementary included? MAPQ filter? read span or fragment? mate-overlap corrected? per-base or per-region? The tools disagree on every one of these by default.

## Tool Taxonomy

| Tool | Counts what (defaults) | Per-base or region | When |
|------|------------------------|--------------------|------|
| mosdepth | corrects mate-overlap by default (off under `--fast-mode`/`-x`); `-Q` MAPQ filter; emits cumulative dist + summary | windowed (`--by`), per-region, or callable bins (`--quantize`) | the modern fast default for WGS/WES/targeted; gives the breadth curve directly |
| samtools coverage | per-reference summary (added 1.10); `coverage` column = breadth %, `meandepth` = depth | per-contig | quick "is this contig actually covered?" -- spots high-mean/low-breadth pileups |
| samtools depth | drops UNMAP/SECONDARY/QCFAIL/DUP by default; `-Q`/`-q` filters; `-s` de-double-counts overlap; CRAM needs `--reference` | per-base | exact per-base depth over small regions; watch the 8000-cap version trap |
| bedtools genomecov | counts READ coverage by default (double-counts mate overlap); `-pc` = fragment; `-split` for spliced | per-base / bedGraph / histogram | bedGraph tracks, genome-wide depth histogram |
| bedtools coverage | per-A-interval stats from B reads; `-a`/`-b` flipped at v2.24.0 | per-region (or `-d` per-base) | per-target counts/breadth/mean over a BED |
| Picard CollectHsMetrics | capture-kit QC | per-target panel | exome/panel uniformity: on-target %, fold-80, PCT_TARGET_BASES_20X |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| WGS / WES breadth + adequacy | `mosdepth --by` then parse `*.global.dist.txt` | emits the cumulative curve + median directly; fast |
| Quick per-contig depth & breadth glance | `samtools coverage` | one line/contig; `coverage` col = breadth, `meandepth` = depth |
| Exact per-base depth, small region | `samtools depth -a -r chr:from-to` | per-base; add `-s` for short-insert; check version for 8000 cap |
| bedGraph coverage TRACK for a browser | `bedtools genomecov -ibam -bga` (or `-bg`) | `-bga` marks zero-coverage gaps; convert to bigWig -> bigwig-tracks |
| Per-target counts/breadth/mean over a BED | `bedtools coverage -a targets.bed -b in.bam` | A = targets, B = reads (post-v2.24.0); `-mean` for mean depth |
| Callable-region BED (NO/LOW/CALLABLE/HIGH) | `mosdepth --quantize 0:1:4:150:` | lightweight CallableLoci replacement at scale |
| Target-capture uniformity QC | -> Picard CollectHsMetrics (fold-80, on-target %) | the capture-QC standard; off-target loss + bait unevenness |
| Spliced/RNA-seq depth | add `-split` (genomecov/coverage) | without it an intron (N CIGAR) is counted as covered |
| Short-insert VAF (amplicon/cfDNA) | correct mate-overlap: `samtools depth -s` / `genomecov -pc` / mosdepth default | naive per-base double-counts the overlap, corrupting VAFs |
| Normalized cross-sample track | -> chip-seq/chipseq-visualization (deepTools bamCoverage) | library-size correction (RPGC/CPM/BPM) for comparison |
| Pileup/variant evidence from BAM | -> alignment-files/pileup-generation | depth is upstream of per-call DP/AD |

## mosdepth -- The Modern Default

**Goal:** Get the median depth and the full breadth curve for a BAM in one fast pass.

**Approach:** Run mosdepth windowed (or whole-genome), then read the cumulative distribution file -- it already holds breadth at every depth threshold; no histogram integration needed.

```bash
mosdepth --by 500 -Q 20 sample in.bam     # --by 500 = 500 bp windows; -Q 20 = drop MAPQ<20 (repeat coverage collapses, intentionally)
# Outputs: sample.mosdepth.summary.txt (mean/min/max per chrom + total)
#          sample.mosdepth.global.dist.txt (cumulative: chrom, depth, proportion >= depth)
#          sample.regions.bed.gz (per-window mean depth)
```

The `*.global.dist.txt` rows are `chrom  depth  proportion_of_bases_at_least_this_depth` -- the breadth curve directly. Read median as the depth where proportion crosses 0.5. `--fast-mode`/`-x` is ~2x faster but SILENTLY disables mate-overlap correction -- fine for a rough WGS glance, wrong for VAF-sensitive short-insert data.

**Goal:** Emit a callable-region BED (NO_COVERAGE / LOW / CALLABLE / HIGH) without GATK3.

**Approach:** Use `--quantize` to bin depth and merge adjacent equal-bin runs into a compact BED.

```bash
mosdepth --quantize 0:1:4:150: callable in.bam   # bins: [0,1)=NO_COVERAGE, [1,4)=LOW, [4,150)=CALLABLE, [150,inf)=HIGH
# 4 = min callable depth (tune to caller); 150 = excessive-depth ceiling (flags rDNA/artifact pileups)
zcat callable.quantized.bed.gz | head
```

## bedtools genomecov -- Tracks and the Histogram Default

```bash
bedtools genomecov -ibam in.bam -bga > cov.bedGraph   # -bga = bedGraph INCLUDING zero-coverage runs; -bg omits zeros
bedtools genomecov -ibam in.bam -pc -bg > frag.bedGraph # -pc = FRAGMENT coverage (mate overlap counted once); default counts reads (double-counts overlap)
bedtools genomecov -ibam in.bam -split -bg > rna.bedGraph # -split = skip N-CIGAR gaps (introns); MANDATORY for spliced RNA-seq
bedtools genomecov -ibam in.bam > hist.txt            # NO output flag = a 5-col HISTOGRAM, not a track
```

The bare default is a **histogram**, not a bedGraph -- 5 columns: `chrom  depth  bases_at_that_depth  chrom_size  fraction_of_chrom`, with a final `genome` block for the whole genome. Breadth/mean must be integrated from it yourself (sum `fraction` over `depth >= threshold`) -- which is exactly why mosdepth's ready-made dist file is preferred.

## bedtools coverage -- Per-Target Stats (mind the orientation)

```bash
bedtools coverage -a targets.bed -b in.bam > per_target.bed   # stats reported FOR each A interval
bedtools coverage -a targets.bed -b in.bam -mean > mean.bed   # -mean = mean depth per A interval
```

As of bedtools **v2.24.0** coverage is computed for the **`-a`** file (it was `-b` before) -- A = the regions stats are wanted for (targets), B = the reads. The default appends 4 columns to each A interval: (1) count of B features overlapping, (2) bases in A covered >=1x, (3) length of A, (4) fraction of A covered (col2/col3 = per-interval breadth). `-d` = per-base depth within each interval; `-hist` = depth histogram per interval plus an `all` summary; `-counts` = just the overlap count (faster).

## samtools depth / coverage

```bash
samtools coverage in.bam                          # per-contig: rname..numreads covbases coverage(=breadth%) meandepth meanbaseq meanmapq
samtools depth -a -Q 20 -r chr1:1-100000 in.bam   # -a = report zero-depth positions; -Q = min MAPQ; -r = region
samtools depth -s in.bam                          # -s = count overlapping mate pair only ONCE (short-insert de-double-count)
samtools depth -a --reference ref.fa in.cram      # CRAM REQUIRES --reference
```

In `samtools coverage` the column literally named `coverage` is **breadth** (% bases >=1x), and `meandepth` is depth -- a contig with `coverage=9.7` and `meandepth=3.5` is 3.5x over only 9.7% of the contig (a localized pileup), NOT "9.7x coverage". `samtools depth` drops UNMAP/SECONDARY/QCFAIL/DUP by default (so duplicates are excluded -- but only if they were MARKED first). Without `-a`/`-aa`, zero-depth positions are omitted, so a naive `sum/lines` mean over-counts by dropping the zeros.

## Per-Method Failure Modes

### Reporting mean depth as the result
**Trigger:** citing "mean = 30x" as adequacy. **Mechanism:** mean is inflated by the repeat/rDNA tail and blind to GC/mappability holes. **Symptom:** a genome with large uncallable gaps looks fine. **Fix:** report median + breadth at the caller's threshold (mosdepth dist).

### samtools depth silent 8000 cap
**Trigger:** pre-1.13 samtools on high-depth loci (rDNA, mito, amplicon, ctDNA). **Mechanism:** old default `-d/-m` capped depth at 8000 and truncated with no warning. **Symptom:** depth plateaus near 8000. **Fix:** `samtools --version`; on old builds add `-d 0`; 1.13+ has no cap (flag ignored). Note `mpileup` has its own separate 8000 default.

### Mate-overlap double-counting
**Trigger:** naive per-base depth on short-insert libraries (amplicon, cfDNA, FFPE). **Mechanism:** the two mates of a short fragment both cover the overlap, counted twice but not independent. **Symptom:** locally doubled depth, corrupted/inflated VAFs. **Fix:** `samtools depth -s`, `genomecov -pc` (fragment), or mosdepth default -- and do NOT use mosdepth `--fast-mode`/`-x`, which turns the correction off.

### Coverage off an un-deduped BAM
**Trigger:** depth on a BAM whose duplicates were never marked. **Mechanism:** dedup-aware tools drop the DUP flag, but nothing was flagged. **Symptom:** inflated depth at amplified (often GC-extreme) loci, fatter right tail. **Fix:** Picard MarkDuplicates / `samtools markdup` FIRST, then measure.

### MAPQ filtering and repeat coverage
**Trigger:** choosing a MAPQ threshold without considering repeats. **Mechanism:** repeats give low MAPQ; `-Q 20+` makes repeat coverage vanish, MAPQ 0 lets multimappers pile up or smear. **Symptom:** repeats read as either empty or noisy -- no neutral choice. **Fix:** mask repeats (ENCODE blacklist / mappability) and report breadth over the MAPPABLE genome, not the whole genome.

### bedtools coverage -a/-b backwards
**Trigger:** pre-v2.24.0 muscle memory / old tutorials. **Mechanism:** semantics flipped to report stats for `-a` at v2.24.0. **Symptom:** well-formed output describing per-read instead of per-target stats. **Fix:** A = targets, B = reads; sanity-check the row count equals the target count.

### genomecov default misread / no -split on RNA-seq
**Trigger:** expecting a bedGraph from bare `genomecov`, or omitting `-split` on spliced reads. **Mechanism:** bare default is a histogram; without `-split` an N-CIGAR intron is counted as covered. **Symptom:** misparsed histogram, or every spliced gene appears fully covered across introns. **Fix:** add `-bg`/`-bga` for a track; always `-split` for spliced data.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| WGS germline ~30x mean -> ~95% of genome >= 20x | field convention (approx) | het-SNP sensitivity plateaus ~30x; frame as breadth, not mean |
| WES germline ~100x on-target -> ~90-95% target >= 10-20x | field convention (approx; ACMG-style, lab-dependent) | capture unevenness + off-target loss eat the raw mean |
| Somatic bulk tumor ~60-100x+ | field convention (approx) | low-VAF subclones need depth ~ 1/VAF; impure tumors need more |
| ctDNA/UMI panels 1000s-50000x raw | field convention (approx) | raw depth != usable depth after UMI collapse; report effective depth |
| Long-read WGS ~20-30x (HiFi ~30x, ONT SV ~20x+) | moving convention (approx) | flatter GC bias + better repeat mappability reach more genome per x |
| mean/median > ~1.1-1.2 = skewed | distribution diagnostic | the tail is inflating the mean; investigate dups/repeats/rDNA |
| Fano factor = 1 (Poisson ideal); real >> 1 | Lander & Waterman 1988 | overdispersion = evenness problem; deeper sequencing won't fill holes |
| Picard fold-80 ~1.3-2 good, >3 poor | practitioner heuristic (Picard defines only the metric) | fold extra sequencing to lift 80% of targets to the mean |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Depth plateaus at ~8000 | pre-1.13 samtools default cap | `samtools --version`; add `-d 0`; upgrade to 1.13+ |
| Inflated VAFs in amplicon/cfDNA | mate-overlap double-counting | `samtools depth -s` / `genomecov -pc` / mosdepth (not `--fast-mode`) |
| "30x" but variants missing in some genes | GC-shallow / uncallable holes hidden by mean | report breadth at threshold; mask blacklist; check fold-80 |
| `samtools coverage` "coverage" looks tiny | it is breadth %, not depth | read `meandepth` for depth; `coverage` = % bases >=1x |
| genomecov gives a histogram not a track | no `-bg`/`-bga` flag | add `-bga` (with zeros) or `-bg` |
| Every spliced gene fully covered | missing `-split` on RNA-seq | add `-split` to genomecov/coverage |
| bedtools coverage stats look per-read | `-a`/`-b` backwards (pre-2.24 habit) | A = targets, B = reads |
| CRAM depth errors / empty | missing reference | `samtools depth --reference ref.fa` |

## References

- Quinlan AR, Hall IM. 2010. BEDTools: a flexible suite of utilities for comparing genomic features. *Bioinformatics* 26:841-842.
- Pedersen BS, Quinlan AR. 2018. Mosdepth: quick coverage calculation for genomes and exomes. *Bioinformatics* 34:867-868.
- Danecek P, Bonfield JK, Liddle J, et al. 2021. Twelve years of SAMtools and BCFtools. *GigaScience* 10:giab008.
- Aird D, Ross MG, Chen WS, et al. 2011. Analyzing and minimizing PCR amplification bias in Illumina sequencing libraries. *Genome Biol* 12:R18.
- Benjamini Y, Speed TP. 2012. Summarizing and correcting the GC content bias in high-throughput sequencing. *Nucleic Acids Res* 40:e72.
- Amemiya HM, Kundaje A, Boyle AP. 2019. The ENCODE blacklist: identification of problematic regions of the genome. *Sci Rep* 9:9354.
- Lander ES, Waterman MS. 1988. Genomic mapping by fingerprinting random clones: a mathematical analysis. *Genomics* 2:231-239.

## Related Skills

- bedgraph-handling - bedGraph tracks this skill emits, and their normalization
- bigwig-tracks - Convert the coverage bedGraph to an indexed bigWig for browsers
- interval-arithmetic - Intersect coverage/callable BEDs with target regions
- alignment-files/pileup-generation - Per-base pileup upstream of depth and per-call DP
- alignment-files/bam-statistics - flagstat/idxstats and dup rate that explain coverage confounders
- chip-seq/chipseq-visualization - deepTools normalized coverage tracks for cross-sample comparison
- data-visualization/genome-tracks - Render the coverage tracks built here
<!-- END FILE: genome-intervals/coverage-analysis/SKILL.md -->

## 子目录：genome-intervals/gtf-gff-handling

<!-- BEGIN FILE: genome-intervals/gtf-gff-handling/SKILL.md -->
---
name: bio-genome-intervals-gtf-gff-handling
description: Parses, queries, converts, and extracts from GTF and GFF3 gene-model annotation files - walking the gene/transcript/exon/CDS hierarchy with gffutils (queryable SQLite DB), converting formats and extracting transcript/CDS/protein FASTA with gffread, slurping to dataframes with gtfparse/pyranges, and sanitizing malformed files with AGAT. Covers the 1-based-inclusive vs 0-based BED coordinate conversion (start-1 only), deriving implicit features (introns/UTRs/TSS), phase-not-frame, the stop-codon-in-or-out-of-CDS convention, and the chr1-vs-1 seqid and gene-ID-version mismatches that silently produce all-zero count matrices and dropped joins. Use when extracting features or sequences from an annotation, converting GTF<->GFF3 or GTF->BED, traversing the gene tree, or diagnosing a coordinate/provenance mismatch upstream of counting or DE.
tool_type: mixed
primary_tool: gffutils
---

## Version Compatibility

Reference examples tested with: gffutils 0.13+, gffread 0.12+, gtfparse 2.x, pyranges 0.1+ (or 1.0+ - see note), AGAT 1.4+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

Two version landmines specific to this skill: (1) **gtfparse changed its return type** - older releases returned a pandas DataFrame, gtfparse >=2.x returns a **polars** DataFrame by default; pass `result_type='pandas'` before chaining pandas idioms (`.copy()`, boolean masks). (2) **pyranges has a major-version API split** - pyranges 0.x and the 1.0 rewrite differ in method names and attribute access; check `import pyranges; pyranges.__version__` before pasting code. gffutils stores **1-based** coordinates while pyranges stores **0-based** - their `start` fields differ by one by design. If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt rather than retrying.

# GTF/GFF Handling

**"Pull these features (or their sequences) out of my annotation, convert it, or find out why my counts are wrong."** -> Treat the file as a serialized gene-model tree: walk gene->transcript->exon/CDS, derive implicit features, and reconcile coordinate and namespace conventions before trusting any number.
- CLI: `gffread in.gtf -T -o out.gtf` (convert), `gffread -w tx.fa -g genome.fa in.gtf` (FASTA), `agat_convert_sp_gxf2gxf.pl` (sanitize)
- Python: `gffutils.create_db(...)` then `db.children(gene, featuretype='exon')` (tree query); `gtfparse.read_gtf(..., result_type='pandas')` / `pyranges.read_gtf(...)` (dataframe)

## The Single Most Important Modern Insight -- A GTF/GFF3 Is a Serialized Gene-Model Tree, Not a Table of Intervals

Almost every painful bug here comes from the file looking like a CSV while behaving like a tree, or from a coordinate/provenance mismatch the tools never warn about - and **every one of these failures is silent**: nothing throws, the wrong answer just propagates. Three load-bearing facts the tutorials skip:

1. **The coordinate conversion is asymmetric.** GTF/GFF3 are 1-based fully inclusive `[start, end]`; BED (and pyranges-internal) are 0-based half-open `[start-1, end)`. Convert to BED by **subtracting 1 from the start only - the end is unchanged** (the inclusive 1-based end and the exclusive 0-based end are the same integer). Doing `start-1` AND `end-1` shifts the feature one base left and is the classic over-correction: invisible in coverage/overlap, catastrophic in CDS translation (a one-base frameshift garbles the protein). gffutils keeps 1-based, pyranges stores 0-based, so their `start` fields differ by one *correctly* - never "fix" that discrepancy.

2. **The all-zero count matrix.** featureCounts/htseq-count match a read to a feature by **string equality on the chromosome name**, so `chr1` != `1` != `NC_000001.11` produces a perfectly well-formed matrix of **zeros with no error or warning** - the only signal is `~0%` assigned in the summary. Same bug one altitude up: gene-ID version suffixes (`ENSG00000223972.5` vs `ENSG00000223972`) silently drop rows on an annotation join. Audit every cross-file key (chromosomes between BAM/GTF/FASTA, gene IDs between GTF/count-matrix/annotation) by **set intersection, never by eye**, before any count or join.

3. **phase is not frame, and the stop codon is a 3-bp ghost.** Phase (column 8) is the strand-aware count of bases to trim from the segment's transcriptional 5' end to reach the next codon (0/1/2) - **recompute it on any CDS edit** (AGAT/gffread do; hand-editing coordinates without fixing phase frameshifts the translation). GTF (Ensembl/GENCODE) **excludes** the stop codon from CDS; GenBank/GFF3 often **include** it - so a CDS length off by exactly 3 nt (or a protein +/-1 stop) between two sources is a convention mismatch, not a bug.

## Tool Taxonomy

| Tool | Role | Mechanism | When |
|------|------|-----------|------|
| gffutils | Queryable gene-tree DB (Python) | builds a SQLite DB; `children`/`parents`/`region` traverse the hierarchy; keeps 1-based coords | walk gene->transcript->exon/CDS, derive introns, query by ID/coordinate |
| gffread | Converter + sequence extractor (CLI) | fast C++, genome-aware; one binary | GTF<->GFF3, extract transcript/CDS/protein FASTA, region filter |
| pyranges | Vectorized interval engine (Python) | PyRanges/pandas-like; stores 0-based half-open | overlap joins, set ops, dataframe-native interval work |
| gtfparse | GTF -> dataframe (Python) | one call explodes column 9 into attribute columns | quick column/filter work; NOT hierarchy-aware (flat table) |
| AGAT | GFF/GTF sanitizer (Perl CLI) | reconstructs the full tree; adds missing features, fixes IDs/phase, deflates attributes | a malformed/non-standard file - run FIRST, before parsing |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Walk the gene/transcript/exon hierarchy, derive introns | gffutils `create_db` + `children`/`parents` | the hierarchy is the point; flat parsers lose it |
| Convert GTF<->GFF3 or extract transcript/CDS/protein FASTA | gffread (`-T`, `-w`/`-x`/`-y -g`) | genome-aware, knows the stop-codon convention |
| Quick column/filter on a clean modern GTF | gtfparse (`result_type='pandas'`) | one-call dataframe; verify return type first |
| Overlap/set ops, large in-memory interval joins | pyranges | vectorized; route arithmetic -> interval-arithmetic |
| File malformed: no `##gff-version`, missing gene/exon lines, dup IDs, mixed conventions | AGAT `agat_convert_sp_gxf2gxf.pl` first | sanitize once vs writing a brittle parser around it |
| GTF -> BED for bedtools | `start-1`, end unchanged (-> bed-file-basics) | the off-by-one boundary is where it bites |
| Counts came out all-zero or DE join dropped rows | intersect seqid / gene-ID namespaces | string-equality match; no error is emitted |
| Counting reads per gene/feature | -> rna-quantification/featurecounts-counting | the seqid/strand landmines live there; set `-s` from chemistry |
| Judge whether the annotation itself is sound | -> genome-annotation/annotation-qc | this skill operates on the file, not its quality |

## Walk the Gene Tree and Derive Introns (gffutils)

**Goal:** Traverse gene -> transcript -> exon and reconstruct features (introns) that the file does not store explicitly.

**Approach:** Build a SQLite DB once (disabling gene/transcript inference when those lines already exist, for a ~100x speedup), then query children ordered by position and synthesize introns from the exon gaps.

```python
import gffutils

# disable_infer_* is GTF-only and applies when gene/transcript lines ALREADY exist (modern GENCODE/Ensembl) -> ~100x faster
db = gffutils.create_db('annotation.gtf', 'annotation.db', force=True,
                        disable_infer_genes=True, disable_infer_transcripts=True,
                        merge_strategy='create_unique')

gene = db['ENSG00000141510']                                    # gffutils returns 1-based coords (raw record)
for tx in db.children(gene, featuretype=['mRNA', 'transcript'], order_by='start'):
    exons = list(db.children(tx, featuretype='exon', order_by='start'))
    introns = list(db.interfeatures(exons, new_featuretype='intron'))   # introns are not stored - derived from exon gaps
    print(tx.id, len(exons), 'exons', len(introns), 'introns')
```

A modern GTF without `disable_infer_*` triggers the slow inference/merge machinery; an *older* minimal GTF lacking gene/transcript lines needs inference ON so gffutils reconstructs the envelopes. Match the flag to the file. introns, UTRs (`exon - CDS`), and TSS are derived, not stored - never infer biological absence from a missing feature line.

## Convert Formats and Extract Sequences (gffread)

gffread is genome-aware and respects the stop-codon convention, so it is the safe path for sequence extraction (naive coordinate math is not).

```bash
gffread annotation.gff3 -T -o annotation.gtf            # GFF3 -> GTF2 (default output is GFF3)
gffread -w transcripts.fa -g genome.fa annotation.gtf   # spliced exon (mature transcript) FASTA
gffread -x cds.fa         -g genome.fa annotation.gtf   # spliced CDS nucleotide FASTA
gffread -y proteins.fa    -g genome.fa annotation.gtf   # translated-CDS protein FASTA
gffread annotation.gtf -C -o coding.gtf                 # keep only coding transcripts
```

`-g` needs the genome FASTA (gffread auto-creates the `.fai`). `-w`/`-x`/`-y` splice the segments per transcript, so they handle multi-exon models correctly - do not concatenate exon FASTAs by hand.

## Convert GTF to BED with the Right Coordinate Shift

**Goal:** Emit a BED of a chosen feature type for bedtools, without the off-by-one frameshift.

**Approach:** Parse to a pandas frame, filter to the feature type, subtract 1 from the start *only*, leave the end untouched.

```python
import gtfparse

df = gtfparse.read_gtf('annotation.gtf', result_type='pandas')   # gtfparse >=2.x defaults to POLARS - force pandas
genes = df[df['feature'] == 'gene'].copy()
genes['start'] = genes['start'] - 1                              # 1-based inclusive -> 0-based half-open: START ONLY
bed = genes[['seqname', 'start', 'end', 'gene_id', 'score', 'strand']]
bed.to_csv('genes.bed', sep='\t', header=False, index=False)
```

For TSS/promoter derivation (strand-aware: `+` strand TSS = start, `-` strand TSS = end), route to proximity-operations - the promoter window is an imposed definition, not an annotated feature.

## Sanitize a Malformed File First (AGAT)

When a file lacks `##gff-version 3`, has non-Sequence-Ontology types, is missing `gene`/`exon`/UTR lines, has duplicate IDs, or mixes conventions, sanitize it once rather than coding around it:

```bash
agat_convert_sp_gxf2gxf.pl -g messy.gff3 -o clean.gff3   # adds missing ID/Parent + features, fixes dup IDs, recomputes phase, sorts
agat_convert_sp_gff2gtf.pl -g clean.gff3 -o clean.gtf    # GFF3 -> GTF (collapses level1->gene, level2->transcript)
```

AGAT *makes decisions* (which convention to standardize to, how to derive missing features) - usually a feature, but when a source's exact encoding must be preserved (e.g. auditing a submission), inspect what it changed rather than trusting blindly.

## Per-Method Failure Modes

### Over-correcting the coordinate conversion
**Trigger:** subtracting 1 from both start and end when converting to BED. **Mechanism:** only the start representation differs; the inclusive 1-based end equals the exclusive 0-based end. **Symptom:** every feature shifted one base left; invisible in coverage, frameshifts CDS translation. **Fix:** `start-1`, end unchanged.

### Comparing coordinates across gffutils and pyranges
**Trigger:** asserting equality on `start` fields from both libraries in one script. **Mechanism:** gffutils keeps 1-based, pyranges stores 0-based. **Symptom:** an off-by-one that looks like a bug; "fixing" it introduces a real error. **Fix:** confirm each library's convention; expect the difference.

### All-zero count matrix (seqid mismatch)
**Trigger:** BAM aligned to `chr1`, GTF annotated with `1`. **Mechanism:** counters match reads to features by chromosome-name string equality. **Symptom:** well-formed matrix of zeros, no error; `~0%` assigned in the summary. **Fix:** intersect the BAM `@SQ`/idxstats chromosome set with the GTF column-1 set programmatically; remap one namespace, re-confirm.

### Dropped rows on a gene-ID join
**Trigger:** count matrix keyed `ENSG...` joined to annotation keyed `ENSG....5`. **Mechanism:** exact string match on a versioned vs unversioned ID. **Symptom:** join returns a dataframe but rows vanish / annotation is NA. **Fix:** strip `.\d+$` on both sides for matching; keep the version in the stored annotation for provenance.

### CDS length off by exactly 3
**Trigger:** comparing CDS/protein length across two sources, or translating after a convention-flipping conversion. **Mechanism:** GTF excludes the stop codon from CDS; GenBank/GFF3 often include it. **Symptom:** length differs by 3 nt / 1 aa; protein does/does not end in `*`. **Fix:** suspect the convention before debugging code; extract CDS with gffread/AGAT, which know it.

### Editing CDS coordinates without recomputing phase
**Trigger:** trimming/merging/lifting CDS coordinates, leaving column 8 as-is. **Mechanism:** phase is a static integer; the chain of per-segment phases depends on cumulative coding length. **Symptom:** downstream translation (gffread `-y`, table2asn, EMBL) frameshifts or rejects. **Fix:** treat a CDS edit + phase recompute as one atomic operation; let AGAT/gffread recompute.

### gffutils pathologically slow on a modern GTF
**Trigger:** `create_db` on a GENCODE/Ensembl GTF without the infer flags. **Mechanism:** gffutils infers gene/transcript envelopes and runs the merge machinery. **Symptom:** create_db hangs for many minutes. **Fix:** `disable_infer_genes=True, disable_infer_transcripts=True` when those lines already exist (~100x faster).

## Quantitative Thresholds

| Convention / threshold | Source | Rationale |
|------------------------|--------|-----------|
| GTF/GFF3 1-based inclusive; convert to BED with start-1, end unchanged | UCSC/SO format specs | the inclusive 1-based end == the exclusive 0-based end; over-correcting both ends frameshifts CDS |
| CDS length differs by exactly 3 nt between sources | GTF vs GenBank/GFF3 stop-codon convention | GTF (Ensembl/GENCODE) excludes the stop from CDS; GenBank/GFF3 often include it |
| `disable_infer_*` -> ~100x create_db speedup | gffutils docs | inference/merge machinery is skipped when gene/transcript lines already exist |
| seqid intersection required before counting | featureCounts/htseq string-equality match | non-overlapping chromosome names -> all-zero matrix with no error |
| Strip `.\d+$` from gene IDs on both sides before a join | Ensembl/GENCODE/RefSeq versioned accessions | version suffix tracks model revision; mismatch drops rows silently |
| featureCounts default `-s 0` (unstranded) vs htseq-count `-s yes` (stranded) | tool defaults (Liao 2014; Anders 2015) | switching tools changes the counting model; set `-s` from library chemistry, not the default |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| All genes count zero | seqid mismatch (`chr1` vs `1` vs `NC_...`) | intersect BAM and GTF chromosome sets; remap one namespace |
| Counts low and flip when `-s` changes | wrong strandedness (featureCounts vs htseq defaults differ) | set `-s` from the library prep chemistry; verify assignment rate |
| Join drops rows / NA annotation | gene-ID version suffix (`ENSG....5` vs `ENSG...`) | strip `.\d+$` on both sides for matching |
| Biotype filter returns empty | attribute key differs by source: GENCODE uses `gene_type`, Ensembl/RefSeq use `gene_biotype` | check the actual key (it travels with the `chr1`-vs-`1` provenance split); query the present key |
| Translated protein is garbage | over-corrected coordinate (`start-1` AND `end-1`) | subtract 1 from start only |
| CDS/protein off by 3 nt / 1 aa | stop-codon-in-or-out-of-CDS convention | extract with gffread/AGAT; do not debug coordinate math |
| gtfparse pandas idioms raise AttributeError | gtfparse >=2.x returns polars | pass `result_type='pandas'` |
| pyranges AttributeError | 0.x vs 1.0 API mismatch | check `pyranges.__version__`; use matching method names |
| gffutils create_db hangs | infer machinery on a modern GTF | set `disable_infer_genes=True, disable_infer_transcripts=True` |
| `gffread -w/-x/-y` errors | missing or unindexed genome FASTA | pass `-g genome.fa` (gffread creates the `.fai`) |

## References

- Pertea G, Pertea M. 2020. GFF Utilities: GffRead and GffCompare. *F1000Research* 9:304.
- Stovner EB, Saetrom P. 2020. PyRanges: efficient comparison of genomic intervals in Python. *Bioinformatics* 36:918-919.
- Dale R. gffutils: GFF and GTF file manipulation and interconversion. Software, https://github.com/daler/gffutils (no journal publication).
- Dainat J. AGAT: Another Gff Analysis Toolkit to handle annotations in any GTF/GFF format. Zenodo. doi:10.5281/zenodo.3552717.
- Rubinsteyn A, et al. gtfparse: parsing tools for GTF (gene transfer format) files. Software, https://github.com/openvax/gtfparse (no journal publication).
- Liao Y, Smyth GK, Shi W. 2014. featureCounts: an efficient general purpose program for assigning sequence reads to genomic features. *Bioinformatics* 30:923-930.
- Anders S, Pyl PT, Huber W. 2015. HTSeq - a Python framework to work with high-throughput sequencing data. *Bioinformatics* 31:166-169.

## Related Skills

- bed-file-basics - BED format and the coordinate conversion this skill feeds into
- interval-arithmetic - Set operations on the features extracted here
- proximity-operations - Strand-aware TSS/promoter derivation from extracted features
- rna-quantification/featurecounts-counting - Consumes the GTF/GFF features; the seqid/strand landmines live there
- genome-annotation/functional-annotation - Downstream of feature/sequence extraction from the annotation
- genome-annotation/annotation-qc - Judges whether the annotation this skill parses is sound
- differential-expression/de-results - Map gene coordinates back to DE results
<!-- END FILE: genome-intervals/gtf-gff-handling/SKILL.md -->

## 子目录：genome-intervals/interval-arithmetic

<!-- BEGIN FILE: genome-intervals/interval-arithmetic/SKILL.md -->
---
name: bio-genome-intervals-interval-arithmetic
description: Performs set operations on genomic intervals - intersect (-wa/-wb/-wo/-wao/-loj/-c/-v/-u), subtract (-A), merge (-d, -c/-o), complement, cluster, multiinter, unionbedg, map, and groupby - with bedtools (CLI) and pybedtools/pyranges/bioframe (Python). Covers the sorted-input contract and the -sorted chromosome-order footgun, reciprocal/fractional overlap (-f/-F/-r/-e) and the A-vs-B asymmetry, -split for spliced/BED12/BAM features, and jaccard/fisher as mechanics only. Use when finding overlapping or unique regions between BED/peak/feature files, building consensus peaksets, removing blacklisted regions, transferring annotation values onto intervals, or computing interval-set similarity; route overlap-significance testing to overlap-significance.
tool_type: mixed
primary_tool: bedtools
---

## Version Compatibility

Reference examples tested with: bedtools 2.31+, pybedtools 0.10+, pyranges 0.1+ (or 1.0+ - see note), bioframe 0.7+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `bedtools --version` then `bedtools <subcommand> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

pyranges has a major-version API split: pyranges 0.x and the 1.0 rewrite (package `pyranges1`) differ in method names and return shapes. Verify with `import pyranges; pyranges.__version__` before pasting v0 idioms. If code throws an error, introspect the installed package and adapt rather than retrying.

# Interval Arithmetic

**"Which of my peaks overlap promoters, and how do I combine/subtract/annotate interval sets?"** -> Apply exact, deterministic set operations to sorted interval files, guarding the preconditions (prior `sort`, the `-sorted` chromosome-order contract, `-split`) that otherwise corrupt the answer.
- CLI: `bedtools intersect -a a.bed -b b.bed -u`, `bedtools merge`, `bedtools subtract`, `bedtools map -c 4 -o mean`
- Python: `a.intersect(b, u=True)`, `a.merge()` (pybedtools); `pr_a.overlap(pr_b)` (pyranges); `bf.overlap(df1, df2)` (bioframe)

## The Single Most Important Modern Insight -- The Arithmetic Is Exact; the Danger Is the Silent Preconditions

The set operations themselves are exact and deterministic - bedtools, pyranges, and bioframe compute identical geometry on the same 0-based half-open intervals. The bugs are never in the arithmetic; they hide in four preconditions that fail quietly, returning a plausible wrong answer with exit code 0:

1. **`merge`, `map`, `closest`, `groupby` require prior `sort`.** `merge` only collapses records that are adjacent *in file order* - on unsorted input, overlapping intervals survive un-merged and downstream counts are wrong, with no warning.
2. **`-sorted` requires sorted input in a shared chromosome order.** It swaps `intersect`'s in-memory interval tree for a low-memory chromosome sweep. Modern bedtools (>=~2.25) detects unsorted or differently-ordered `-sorted` input and errors out (exit 1: `... is not sorted` / `chromomsome sort ordering ... is inconsistent`); older versions silently swept past overlaps and under-reported. Pass `-g genome.txt` to pin the expected chromosome order (reproducible, and it catches the subtler missing-chromosome cases). The mismatch that stays SILENT on every version is a chromosome-NAME difference (`chr1` vs `1`), which returns an empty result with no error.
3. **`-split` changes whether the count is exons or the spanning envelope.** A BED12 record or spliced BAM read (CIGAR `N`) spans introns; without `-split` bedtools intersects the whole intron-spanning envelope, silently inflating RNA-seq overlaps. With `-split` it intersects only the blocks (exons).
4. **A raw overlap count is not association.** Long features, clustered features, and uneven coverage all inflate it; the number means nothing without a null. bedtools `fisher` is a weak analytic screen, not the answer - route rigorous significance to overlap-significance.

## Tool Taxonomy

| Tool | Role | Mechanism | When |
|------|------|-----------|------|
| bedtools | CLI interval algebra (reference implementation) | streaming sweep on sorted input; in-memory tree otherwise | shell pipelines, large files, reproducible one-liners |
| pybedtools | Python wrapper over bedtools | shells out to the bedtools binary; BedTool objects, flags as kwargs | inside a Python script; need exact bedtools parity; chaining with pandas |
| pyranges | pure-Python vectorized engine | native NumPy/pandas PyRanges; no bedtools dependency | large in-memory joins, no bedtools install, dataframe-native; mind the v0/v1 split |
| bioframe | functions on a plain pandas DataFrame | vectorized pandas merges; columns `chrom/start/end` | data already in pandas / the cooler-Hi-C ecosystem |

All three Python engines compute the same overlaps; the porting bugs are about default strand handling and return shape (pyranges `overlap` vs `join` vs `intersect`; bioframe `overlap` with `how=`), not geometry.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Quick overlap on the command line | `bedtools intersect -u` | no Python overhead; reproducible one-liner |
| Inside a pandas/Python pipeline | pybedtools or pyranges/bioframe | stays in-process; pyranges/bioframe need no bedtools binary |
| Whole-genome-scale intersect | `intersect -sorted -g genome.txt` | low-memory sweep; modern bedtools errors on a sort/order mismatch, `-g` pins the expected chromosome order |
| Spliced reads / BED12 vs exons | add `-split` | otherwise the intron-spanning envelope is intersected (RNA-seq inflation) |
| Are two SV/CNV calls the same event? | `-f 0.5 -r` (50% reciprocal) | one-sided fractions let a giant interval swallow a tiny one |
| Transfer/aggregate B values onto A | `bedtools map -c COL -o OP` | columnar alternative to `intersect -wo \| groupby` |
| Build consensus peakset from replicates | `cat \| sort \| merge -d N` | collapses replicate peaks within N bp |
| Multi-sample shared-region map | `multiinter` / `unionbedg` | presence/absence (intervals) or stacked signal matrix |
| Is the overlap more than chance? | -> overlap-significance | raw count is length/coverage-confounded; needs a permutation null |
| Peaks not yet called | -> chip-seq/peak-calling or atac-seq/atac-peak-calling | this category operates on existing intervals |

## Intersect - the Workhorse

The output-mode flags do not change *what overlaps*; they change *what gets printed* (the #1 source of confusion). Full flag semantics are in usage-guide.md.

```bash
bedtools intersect -a peaks.bed -b genes.bed -u            # whole A, once, if it overlaps >=1 B
bedtools intersect -a peaks.bed -b genes.bed -v            # A features with NO overlap (set difference)
bedtools intersect -a peaks.bed -b genes.bed -c            # per-A count of B hits (0 if none)
bedtools intersect -a peaks.bed -b genes.bed -wa -wb       # whole A + whole B, one line per pair ("join")
bedtools intersect -a peaks.bed -b genes.bed -loj          # left outer join: every A, NULL B if none
bedtools intersect -a peaks.bed -b genes.bed -wo           # A+B+bp-of-overlap, only A with overlap
bedtools intersect -a peaks.bed -b genes.bed -wao          # like -wo but A-with-no-overlap kept (B=., overlap=0)
```

```python
import pybedtools

a = pybedtools.BedTool('peaks.bed')
b = pybedtools.BedTool('genes.bed')
a.intersect(b, u=True)            # flags become kwargs
a.intersect(b, wa=True, wb=True)
a.intersect(b, c=True)
```

## Subtract, Merge, Complement, Cluster

```bash
bedtools subtract -a a.bed -b b.bed             # clip the overlapping portions out of A (A can fragment)
bedtools subtract -a a.bed -b b.bed -A          # drop the ENTIRE A feature if any part overlaps B
bedtools sort -i a.bed | bedtools merge -d 0    # collapse overlapping + book-ended; -d 0 is the default
bedtools sort -i a.bed | bedtools merge -c 4,5 -o distinct,sum   # summarize columns while merging
bedtools complement -i a.bed -g genome.txt      # the gaps: genome NOT covered by A (genome file required)
bedtools sort -i a.bed | bedtools cluster -d 0  # assign a cluster id to overlapping/adjacent features
```

Valid `-o` operations: `sum, min, max, absmin, absmax, mean, median, mode, antimode, stdev, sstdev, collapse, distinct, count, count_distinct, first, last`. `merge -d 0` merges overlapping and book-ended (touching) features but NOT a 1 bp gap; `-d 1` does.

## Map - Transfer Values, and Groupby - Aggregate

**Goal:** Summarize a column of overlapping B features onto each A interval (e.g. mean signal per gene).

**Approach:** For each sorted A interval, `map` collects overlapping B features and applies an aggregation `-o` to a B column `-c`; `groupby` is the single-file SQL-style aggregator after an `intersect -wo`.

```bash
bedtools map -a genes.bed -b scores.bedgraph -c 4 -o mean      # both inputs MUST be sorted
bedtools intersect -a genes.bed -b peaks.bed -wo \
  | bedtools groupby -g 1,2,3,4 -c 13 -o sum                   # group on A cols, sum the overlap-bp col
```

```python
import pybedtools

genes = pybedtools.BedTool('genes.bed').sort()
scores = pybedtools.BedTool('scores.bedgraph').sort()
genes.map(scores, c=4, o='mean')
```

## Multi-Sample: Multiinter and Unionbedg

```bash
bedtools multiinter -header -names s1 s2 s3 -i s1.bed s2.bed s3.bed   # which files cover each sub-interval
bedtools unionbedg -header -names s1 s2 s3 -i s1.bg s2.bg s3.bg       # stack bedGraph signal into a matrix
```

`multiinter` is the interval presence/absence map (build a consensus by filtering its `num`/`list` columns); `unionbedg` is its signal-track analog.

## Jaccard and Fisher - Mechanics Only

`jaccard` is a single similarity scalar `|A n B| / |A u B|` in [0,1], useful for all-vs-all dataset clustering - it is NOT a significance test (no p-value). `fisher` builds a 2x2 table and returns a Fisher p, but it estimates the in-neither cell from a mean-interval-size/genome-size heuristic, ignores genome structure, and is prone to inflation - treat it as a fast triage screen only.

```bash
bedtools jaccard -a a.bed -b b.bed -g genome.txt        # both sorted; reports jaccard + n_intersections
bedtools fisher  -a a.bed -b b.bed -g genome.txt         # weak analytic null; validate any low p by simulation
```

For a defensible enrichment p-value (size-preserving permutation in an accessible workspace, GAT/regioneR/LOLA/GREAT), route to overlap-significance.

## Per-Method Failure Modes

### Merge without sorting first
**Trigger:** `bedtools merge` (or `cluster`/`map`/`groupby`) on unsorted input. **Mechanism:** merge only collapses records adjacent in file order. **Symptom:** overlapping intervals survive un-merged; counts wrong, no error. **Fix:** `bedtools sort -i in.bed | bedtools merge`.

### `-sorted` on unsorted or differently-ordered input
**Trigger:** `intersect -sorted` on unsorted input or files in different chromosome orders. **Mechanism:** the sweep walks both files in lockstep assuming a shared order. **Symptom:** modern bedtools (>=~2.25) errors out (`... is not sorted` / `chromomsome sort ordering ... is inconsistent`, exit 1); pre-2.25 returned a silently smaller set. **Fix:** sort every input identically and pass `-g genome.txt` to pin the order; on an old bedtools, suspect this when a result is surprisingly small.

### Missing `-split` on spliced features
**Trigger:** intersecting BED12 / spliced BAM without `-split`. **Mechanism:** the intron-spanning envelope is treated as solid. **Symptom:** intronic positions "overlap" exons; RNA-seq overlap inflated/smeared. **Fix:** add `-split` whenever an operand is BED12 or a spliced alignment and exon-level truth is required.

### `-f` vs `-F` swapped, or default 1 bp overlap
**Trigger:** thresholding the wrong set, or no `-f` at all. **Mechanism:** `-f` is a fraction of A, `-F` a fraction of B (default `-f 1e-9` = any 1 bp); A and B play asymmetric roles. **Symptom:** a tiny peak "inside" a 2 Mb gene by one base; swapping `-a`/`-b` changes counts. **Fix:** threshold the *small* set; use `-r` for "same event" concordance.

### complement/shuffle without a genome file
**Trigger:** `complement` (or `closest`/`map` order assumptions) without `-g`. **Mechanism:** bedtools cannot know where chromosomes end. **Symptom:** error, or gaps/coordinates that run past chromosome ends. **Fix:** pass a correct `-g genome.txt` built from the same assembly.

### chrom-naming mismatch (`chr1` vs `1`)
**Trigger:** BED uses `chr1`, genome/other file uses `1`. **Mechanism:** chromosomes never match. **Symptom:** empty/zero output, no error. **Fix:** harmonize naming across all inputs and the genome file.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Overlap fraction `-f` (state explicitly) | analysis choice | default `-f 1e-9` (1 bp) is rarely the biological question; threshold the small set |
| 50% reciprocal overlap (`-f 0.5 -r`) | SV/CNV field convention | "are these the same event"; one-sided lets a big interval swallow a small one |
| Merge `-d` (e.g. 100 bp for replicate consensus) | replicate-merge convention | collapses near-coincident replicate peaks; tune per assay/resolution |
| `merge -d 0` (default) | bedtools default | merges overlapping + book-ended, NOT a 1 bp gap (use `-d 1` for that) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Empty intersect output | chrom naming mismatch (`chr1` vs `1`) | harmonize naming across files + genome.txt |
| `merge` left overlaps behind | input not sorted | `sort` before `merge`/`cluster`/`map`/`groupby` |
| `-sorted` errors or (old bedtools) returns too few | unsorted or mismatched chromosome order | sort all inputs identically; add `-g genome.txt` to pin order |
| RNA-seq overlap looks inflated | missing `-split` on BED12/spliced BAM | add `-split` |
| Negative start / past-chromosome-end | wrong/missing `-g genome.txt` | pass a correct chrom-sizes file |
| pyranges AttributeError | 0.x vs 1.0 API mismatch | check `pyranges.__version__`; use matching method names |

## References

- Quinlan AR, Hall IM. 2010. BEDTools: a flexible suite of utilities for comparing genomic features. *Bioinformatics* 26:841-842.
- Dale RK, Pedersen BS, Quinlan AR. 2011. Pybedtools: a flexible Python library for manipulating genomic datasets and annotations. *Bioinformatics* 27:3423-3424.
- Stovner EB, Sætrom P. 2020. PyRanges: efficient comparison of genomic intervals in Python. *Bioinformatics* 36:918-919.
- Open2C, Abdennur N, Fudenberg G, Flyamer IM, Galitsyna AA, Goloborodko A, Imakaev M, Venev SV. 2024. Bioframe: operations on genomic intervals in pandas dataframes. *Bioinformatics* 40:btae088.

## Related Skills

- bed-file-basics - BED format, coordinate systems, and the conversions this skill depends on
- overlap-significance - Whether an overlap count exceeds a matched null (permutation, GAT/regioneR/LOLA/GREAT)
- proximity-operations - closest, window, flank, slop for adjacency rather than membership
- coverage-analysis - per-base depth and bedGraph signal feeding map/unionbedg
- gtf-gff-handling - exon/feature models whose `-split` behavior this skill depends on
- chip-seq/peak-calling - source of the peak BED files these operations consume
- atac-seq/consensus-peakset - replicate merge via merge/multiinter
<!-- END FILE: genome-intervals/interval-arithmetic/SKILL.md -->

## 子目录：genome-intervals/overlap-significance

<!-- BEGIN FILE: genome-intervals/overlap-significance/SKILL.md -->
---
name: bio-genome-intervals-overlap-significance
description: Tests whether two genomic interval sets overlap (colocalize) more than expected by chance using a permutation test against a structured-genome null model. Covers bedtools fisher (analytic 2x2 screen), bedtools shuffle + jaccard permutation, GAT (isochore/GC-conditioned simulation with FDR), regioneR (flexible permutation, randomizeRegions vs circularRandomizeRegions, localZScore), LOLA (universe-relative Fisher against a region database), and GREAT/rGREAT (regulatory-domain binomial + hypergeometric for ontology-from-regions). Stresses the universe/background choice, matched background, blacklist exclusion, and multiple-testing control. Use when asking whether peaks/regions are enriched at enhancers/TFBS/features, scoring region-set colocalization or region-set enrichment, comparing CNV/SV concordance, or turning an overlap count into a defensible p-value.
tool_type: mixed
primary_tool: regioneR
---

## Version Compatibility

Reference examples tested with: bedtools 2.31+, pybedtools 0.10+, regioneR 1.36+ (Bioconductor 3.18+), GAT 1.3+, LOLA 1.30+, rGREAT 2.4+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('regioneR')` then `?permTest` to verify parameters

Bioconductor packages (regioneR, LOLA, rGREAT) are version-pinned to the Bioconductor release, not just the package version - record the Bioconductor release with results. rGREAT 2.x runs GREAT locally with general background handling; rGREAT 1.x only proxied the (whole-genome-default) web server. If code throws an error, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Overlap Significance

**"My peaks overlap enhancers a lot - is that more than chance?"** -> Compare the observed overlap to a null distribution from a structured-genome model, not to a uniform-random expectation, and report a permutation p-value/z-score, not a raw count.
- CLI: `bedtools fisher -a A -b B -g genome.txt` (fast screen); `gat-run.py --segments=A --annotations=B --workspace=accessible.bed --isochores=gc.bed --num-samples=10000`
- Python: `BedTool(A).shuffle(g='genome.txt', excl='blacklist.bed').jaccard(B)` looped for a null (pybedtools)
- R: `permTest(A=peaks, B=enhancers, randomize.function=circularRandomizeRegions, evaluate.function=numOverlaps, genome='hg38', mask=blacklist, ntimes=1000)` (regioneR)

## The Single Most Important Modern Insight -- A Raw Overlap Count Is an Observation in Search of a Null, and the Universe Choice Dominates

"847 of 1,000 peaks overlap enhancers" means nothing until the analysis can say what that number would have been *by chance* - and "by chance" is almost never "place the regions uniformly at random on the genome." The genome is structured: genes cluster, GC varies in megabase isochores, mappability is uneven, half the genome is repeat/gap, and query regions are drawn from a *biased universe* (open chromatin, callable space, exons). Two tracks that share nothing but a gene-rich, high-GC, high-mappability habitat overlap far more than uniform-random expectation, and a naive test returns p < 1e-300. The co-localization is real; the *interpretation* ("functional association") is false. Three load-bearing moves:

1. **The universe/background is the lever that moves the whole answer - bigger than the test choice.** Across LOLA (`userUniverse`), GREAT (background regions), GAT (`--workspace`), and regioneR (the `mask`/`resampleRegions` universe), the most consequential choice is *the set of regions the query could have come from*. ATAC/ChIP peaks can only be called in accessible chromatin; their honest universe is "all accessible regions," not the genome. Testing against the whole genome merely rediscovers that open chromatin is gene-rich - every gene-associated annotation lights up, none of it specific. The difference between LOLA/GAT/regioneR on the *same correct universe* is second-order; the difference between a correct universe and a whole-genome universe on the *same tool* is often p~1 vs p~1e-200. Care belongs on the background, not on tool selection.

2. **A correct null preserves three things, or it manufactures significance:** (a) the regions' **size distribution** (a 50 kb domain hits anything; a 200 bp peak rarely does - relocate intervals of the observed sizes, do not sprinkle points); (b) an **accessible workspace** excluding assembly gaps, centromeres, the ENCODE blacklist (Amemiya 2019), and unmappable bins; (c) **local structure** - GC/isochore, gene density, and clustering (GAT `--isochores`; regioneR `circularRandomizeRegions` for autocorrelated regions). The "right" answer is usually *less* significant than the naive test - that deflation is the methodology working.

3. **One ten-minute sanity move catches most false claims:** shuffle the query within the same workspace and re-run the same overlap pipeline. If shuffled regions also overlap the annotation a lot, the "enrichment" is workspace geography, not biology.

## Method Taxonomy

| Tool | Citation | Null model | When |
|------|----------|-----------|------|
| bedtools fisher | Quinlan 2010 *Bioinformatics* | analytic 2x2; estimates the unobserved "in-neither" cell from mean interval size + genome size; ignores genome structure | fast triage screen only - never the reported result |
| bedtools shuffle + jaccard/numOverlaps | Quinlan 2010 *Bioinformatics* | DIY size-preserving permutation; `-incl`/`-excl` make it matched | entry-level permutation in a shell/Python pipeline; full control, more code |
| GAT | Heger 2013 *Bioinformatics* | per-isochore size-preserving simulation in a workspace; GC/composition conditioned; built-in FDR across annotations | composition-aware enrichment vs many tracks with multiple-testing control |
| regioneR | Gel 2016 *Bioinformatics* | flexible permutation; `randomizeRegions` (mask) vs `circularRandomizeRegions` (preserves clustering) vs `resampleRegions` (real universe); any evaluator; `localZScore` | publication-grade, R-native, autocorrelated regions, where-in-the-region probing |
| LOLA | Sheffield & Bock 2016 *Bioinformatics* | NOT a shuffle - Fisher's exact of query vs a region database, relative to a `userUniverse` | ranking enrichment of a peak set against ENCODE/Roadmap region collections |
| GREAT / rGREAT | McLean 2010 *Nat Biotechnol*; Gu & Hubschmann 2023 *Bioinformatics* | gene regulatory-domain (basal 5 kb up/1 kb down, extend to 1 Mb); binomial-over-regions AND hypergeometric-over-genes | GO/ontology enrichment *from regions* (cis-regulatory), not from a gene list |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Quick "is this even worth permuting?" | `bedtools fisher` | one command, analytic; p~1 means stop; low means permute |
| Publication-grade colocalization of two region sets | regioneR `permTest` with a `mask` | flexible, reports p + z-score; circular randomization for clustered regions |
| Need GC/isochore/composition control + FDR over many tracks | GAT with `--workspace` + `--isochores` | per-isochore sampling removes the GC confounder; built-in qvalue |
| Enrich a peak set against a region database (TFBS/chromatin) | LOLA `runLOLA` with a correct `userUniverse` | universe-relative Fisher; ranked odds ratios + q-values |
| GO/ontology terms FROM regions (cis-regulatory) | rGREAT with a real background | regulatory-domain model; require binomial AND hypergeometric |
| GWAS/eQTL statistical colocalization (shared causal variant) | -> causal-genomics/colocalization-analysis | DISTINCT problem: coloc/SuSiE on summary stats, not interval overlap |
| Gene-list (not region) ontology enrichment | -> pathway-analysis/go-enrichment | start from genes; GREAT is the region-based analog |
| Query regions are autocorrelated/clustered | regioneR `circularRandomizeRegions` | rotating the set preserves inter-region spacing; uniform randomization inflates significance |
| CNV/SV concordance between call sets | `bedtools intersect -f 0.5 -r` (50% reciprocal) | "same event" convention; one-sided fractions let a giant call swallow a tiny one |
| Peaks not yet called | -> chip-seq/peak-calling, atac-seq/atac-peak-calling | this skill operates on existing interval sets |

## bedtools fisher - The Analytic Screen (weakest null)

```bash
bedtools fisher -a peaks.bed -b enhancers.bed -g genome.txt   # both inputs sorted; genome file required
```

`fisher` builds a 2x2 table (in-A/not x in-B/not) and runs Fisher's exact test. The trap: it cannot observe the "in-neither" cell (there is no negative class of intervals that do not exist), so it **estimates the table totals from a heuristic on mean interval size and genome size**, assuming intervals are independent points uniformly placeable across the genome - exactly the assumption a structured genome violates. The bedtools docs warn it is prone to **inflation** and advise validating any low p-value by simulation. Treat it as triage: p~1 -> stop; p~1e-50 -> run GAT or regioneR, because the structure-corrected p could be anywhere from 1e-30 to 0.3.

## Permutation Null with bedtools shuffle (entry-level)

**Goal:** Decide whether two interval sets overlap more than chance, controlling for feature size and the accessible workspace.

**Approach:** Compute the observed overlap (jaccard or count), then shuffle one set N times within an include-list / outside a blacklist, recompute each time, and locate the observed value in the resulting null distribution.

```python
import pybedtools

N_PERMUTATIONS = 1000   # >=1000 gives a stable empirical p down to ~0.001; fewer cannot resolve small p
a = pybedtools.BedTool('peaks.bed')
b = pybedtools.BedTool('enhancers.bed').sort()
observed = a.sort().jaccard(b)['jaccard']
null = [a.shuffle(g='genome.txt', incl='accessible.bed', excl='blacklist.bed', chrom=True).sort().jaccard(b)['jaccard'] for _ in range(N_PERMUTATIONS)]
p = (sum(x >= observed for x in null) + 1) / (N_PERMUTATIONS + 1)   # +1 avoids a p of exactly 0 (Phipson & Smyth 2010)
```

`-incl` restricts placement to the accessible workspace (the universe); `-excl` avoids gaps/blacklist; `-chrom` keeps each region on its own chromosome (preserves per-chromosome density). Without `-incl`/`-excl` this collapses to a uniform-random null - the wrong one.

## GAT - Isochore/GC-Conditioned Simulation

**Goal:** Test enrichment against one or many annotation tracks while conditioning on GC/composition and controlling FDR.

**Approach:** Provide the query segments, the annotations, an accessible workspace, and an isochore segmentation; GAT samples size-matched segments *per isochore* and compares observed to sampled overlap, reporting fold, empirical p, and FDR-adjusted q across annotations.

```bash
gat-run.py \
  --segments=peaks.bed \
  --annotations=features.bed \
  --workspace=accessible.bed \
  --isochores=gc_bins.bed \
  --num-samples=10000 \
  --counter=nucleotide-overlap \
  --log=gat.log > gat_results.tsv
```

`--isochores` subdivides the workspace (GC bins, chromatin state, or mappability) so sampling happens *per isochore*, preserving GC/composition confounding rather than averaging it away - GAT's signature over a plain shuffle. Set `--num-samples` (>=10000 for stable small q) and `--counter` explicitly; do not rely on defaults.

## regioneR - Flexible Permutation in R

**Goal:** Get a publication-grade colocalization p-value and z-score, with a null that preserves the structure the query trivially has.

**Approach:** Mask the genome to the workspace, choose a randomizer that concedes the right structure (uniform vs clustering-preserving vs real-universe), permute N times scoring overlaps, then probe *where* the association lives with localZScore.

```r
# Reference: regioneR 1.36+ (Bioconductor 3.18+) | Verify API if version differs
library(regioneR)

N_TIMES <- 1000   # permutation count; >=1000 for a stable empirical p (Gel 2016)
peaks <- toGRanges('peaks.bed')
enhancers <- toGRanges('enhancers.bed')
gam <- getGenomeAndMask(genome = 'hg38', mask = toGRanges('blacklist.bed'))

pt <- permTest(A = peaks, B = enhancers,
               randomize.function = circularRandomizeRegions,   # preserves clustering; use randomizeRegions for non-autocorrelated query
               evaluate.function = numOverlaps,
               genome = gam$genome, mask = gam$mask,
               ntimes = N_TIMES, count.once = TRUE)
pt$numOverlaps$pval; pt$numOverlaps$zscore

lz <- localZScore(A = peaks, B = enhancers, pt = pt, window = 10000, step = 500)   # sharp vs diffuse positional association
```

`circularRandomizeRegions` rotates the whole set around the genome, preserving inter-region spacing/clustering - the honest null when the query is autocorrelated (CpG islands, TAD-restricted peaks); plain `randomizeRegions` breaks clustering and inflates significance. `resampleRegions` draws from a supplied real universe. The `mask` is the workspace control.

## LOLA - Universe-Relative Region-Set Enrichment

```r
# Reference: LOLA 1.30+ | Verify API if version differs
library(LOLA)
regionDB <- loadRegionDB('LOLACore/hg38')
userSets <- readBed('peaks.bed')
userUniverse <- readBed('all_called_regions.bed')   # the candidate pool the query was drawn from - NOT the whole genome
res <- runLOLA(userSets, userUniverse, regionDB, cores = 4)   # odds ratio + p + q per reference set, rankable
```

LOLA is not a shuffle: it tests the query against many reference region sets (ENCODE TFBS, Roadmap chromatin) with a Fisher's exact test **relative to `userUniverse`**. The universe is everything - the LOLA vignette recommends either the *union of all query sets across the experiment* ("regions that were in play") or the assay's full candidate pool (e.g. all tested DHS/called peaks); pick the one that honestly bounds where the query could have come from. A whole-genome universe inflates every enrichment.

## rGREAT - Ontology Enrichment From Regions

```r
# Reference: rGREAT 2.4+ | Verify API if version differs
library(rGREAT)
res <- great(toGRanges('peaks.bed'), gene_sets = 'GO:BP', tss_source = 'txdb:hg38',
             background = toGRanges('accessible.bed'))   # supply a real background, not the whole-genome default
tb <- getEnrichmentTable(res)   # has Binom + Hyper p/adjp columns
```

GREAT assigns each gene a regulatory domain (basal 5 kb upstream / 1 kb downstream, extended up to 1 Mb to the next gene's basal domain), maps regions to those domains, then runs a **binomial-over-regions** test AND a **hypergeometric-over-genes** test - by design, with opposite biases. **Trust a term only if both fire:** a single gene with a huge regulatory domain attracts regions by target size and lights up the binomial; the hypergeometric (counting that gene once) calls the bluff. Supply a real background - the binomial assumes regions are independent and uniformly placeable, which clustered ChIP/ATAC peaks violate (Fulcher 2021 demonstrates orders-of-magnitude false-positive inflation from spatial autocorrelation in genomic enrichment analysis - a transferable critique of region-to-gene-category tests).

## Per-Method Failure Modes

### Whole-genome universe for a biased query
**Trigger:** testing ATAC/ChIP peaks (or DMRs, or capture-panel regions) against the whole genome. **Mechanism:** the query could only have come from accessible/assayed space, which is gene-rich; the genome universe credits that geography as enrichment. **Symptom:** every gene-associated annotation is "significant," none specific, p absurdly small. **Fix:** set the universe to the callable/candidate pool (LOLA `userUniverse`, GAT `--workspace`, regioneR `mask`/`resampleRegions`).

### bedtools fisher reported as the result
**Trigger:** putting a `bedtools fisher` p-value in a figure or reviewer reply. **Mechanism:** its analytic 2x2 estimates the unobserved cell from a uniform-placement heuristic, ignoring genome structure; prone to inflation. **Symptom:** spuriously tiny p that evaporates under a competent permutation null. **Fix:** use fisher only to triage; validate any low p with GAT/regioneR.

### Uniform null on clustered query regions
**Trigger:** `randomizeRegions` / plain `shuffle` on autocorrelated regions (CpG islands, tandem families, TAD-restricted peaks). **Mechanism:** uniform placement destroys the clustering the observed data has, so permuted overlap is too low. **Symptom:** inflated significance vs a structure-preserving null. **Fix:** `circularRandomizeRegions` (regioneR) or per-chromosome/per-class shuffling.

### No blacklist / no workspace exclusion
**Trigger:** shuffling across the full genome including gaps, centromeres, and the ENCODE blacklist. **Mechanism:** the null places regions where reads/peaks could never occur, lowering expected overlap. **Symptom:** enrichment that is really mappability artifact. **Fix:** exclude the ENCODE blacklist (Amemiya 2019) and assembly gaps via `-excl`/`mask` before any test.

### Ignoring multiple testing across tracks/terms
**Trigger:** testing a query against many annotation tracks or many GO terms and reading raw p-values. **Mechanism:** dozens-to-thousands of tests inflate the family-wise false-positive rate. **Symptom:** a long list of "significant" hits dominated by chance. **Fix:** use GAT's built-in FDR, FDR-adjust LOLA ranks, and read GREAT's binomial+hypergeometric q-values; require both GREAT tests.

### GREAT term significant by only one test
**Trigger:** reporting a GO term significant by binomial OR hypergeometric alone. **Mechanism:** the two tests have opposite biases (domain size vs gene count). **Symptom:** a term driven by one large-domain gene, or by gene-counting alone. **Fix:** require significance by both; distrust single-test hits.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Permutation N >= 1000 | empirical p resolution (Gel 2016; Phipson & Smyth 2010) | stable empirical p down to ~0.001; the `(hits+1)/(N+1)` estimator avoids p=0 |
| GAT --num-samples >= 10000 | GAT practice | needed for stable small q across many annotations |
| 50% reciprocal overlap (`-f 0.5 -r`) for CNV/SV concordance | field convention | "same event"; one-sided fractions let a giant call swallow a tiny one |
| Universe = candidate/callable pool, not the genome | LOLA/GAT/regioneR design | the dominant lever; whole-genome universe inflates every enrichment |
| GREAT basal 5 kb up / 1 kb down, extend to 1 Mb | McLean 2010 default | regulatory-domain model; user-configurable, report the values used |
| ENCODE blacklist excluded before any test | Amemiya 2019 | high-signal artifact regions otherwise manufacture overlap |
| FDR control across tracks/terms | multiple-testing | many-track / many-term tests inflate false positives |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Every annotation "significant," p absurdly small | whole-genome universe for a biased query | set the universe to the callable/accessible pool |
| `bedtools fisher` error | inputs not sorted, or missing genome file | `sort -k1,1 -k2,2n`; pass `-g genome.txt` |
| Empty/zero overlap in shuffle null | chrom naming mismatch (`chr1` vs `1`) across query/genome/blacklist | harmonize chromosome naming across all files |
| permTest much more significant than expected | uniform randomizer on clustered regions | use `circularRandomizeRegions` |
| GAT reports no GC effect | no `--isochores` supplied | pass an isochore/GC segmentation of the workspace |
| GREAT term looks real but is fragile | significant by only one of the two tests | require binomial AND hypergeometric |
| regioneR `toGRanges`/`getGenomeAndMask` error | genome name not recognized / mask chrom mismatch | use a supported genome id or supply explicit GRanges; match chrom naming |

## References

- Quinlan AR, Hall IM. 2010. BEDTools: a flexible suite of utilities for comparing genomic features. *Bioinformatics* 26:841-842.
- Heger A, Webber C, Goodson M, Ponting CP, Lunter G. 2013. GAT: a simulation framework for testing the association of genomic intervals. *Bioinformatics* 29:2046-2048.
- Gel B, Diez-Villanueva A, Serra E, Buschbeck M, Peinado MA, Malinverni R. 2016. regioneR: an R/Bioconductor package for the association analysis of genomic regions based on permutation tests. *Bioinformatics* 32:289-291.
- Sheffield NC, Bock C. 2016. LOLA: enrichment analysis for genomic region sets and regulatory elements in R and Bioconductor. *Bioinformatics* 32:587-589.
- McLean CY, Bristor D, Hiller M, Clarke SL, Schaar BT, Lowe CB, Wenger AM, Bejerano G. 2010. GREAT improves functional interpretation of cis-regulatory regions. *Nat Biotechnol* 28:495-501.
- Gu Z, Hubschmann D. 2023. rGREAT: an R/Bioconductor package for functional enrichment on genomic regions. *Bioinformatics* 39:btac745.
- Amemiya HM, Kundaje A, Boyle AP. 2019. The ENCODE blacklist: identification of problematic regions of the genome. *Sci Rep* 9:9354.
- Fulcher BD, Arnatkeviciute A, Fornito A. 2021. Overcoming false-positive gene-category enrichment in the analysis of spatially resolved transcriptomic brain atlas data. *Nat Commun* 12:2669.
- Phipson B, Smyth GK. 2010. Permutation P-values should never be zero: calculating exact P-values when permutations are randomly drawn. *Stat Appl Genet Mol Biol* 9:Article 39.

## Related Skills

- interval-arithmetic - The intersect/shuffle/jaccard/fisher mechanics this skill turns into a test
- bed-file-basics - BED format, coordinate systems, and sorting the inputs every test requires
- proximity-operations - Nearest-feature assignment when the question is distance, not overlap enrichment
- chip-seq/peak-calling - Source of the peak query sets tested for enrichment
- chip-seq/peak-annotation - Assign enriched peaks to genes/features
- atac-seq/atac-peak-calling - Source of ATAC peak sets and the accessible-region universe
- pathway-analysis/go-enrichment - Gene-list ontology enrichment; GREAT is the region-based analog
- causal-genomics/colocalization-analysis - GWAS/eQTL statistical colocalization (shared causal variant) - a distinct problem from interval overlap
- data-visualization/genome-tracks - Render the query and annotation tracks behind an enrichment claim
<!-- END FILE: genome-intervals/overlap-significance/SKILL.md -->

## 子目录：genome-intervals/proximity-operations

<!-- BEGIN FILE: genome-intervals/proximity-operations/SKILL.md -->
---
name: bio-genome-intervals-proximity-operations
description: Performs proximity operations on genomic intervals with bedtools (closest, window, flank, slop) and pybedtools - nearest-feature queries with signed/strand-aware distance, fixed-radius window searches, strand-aware promoter construction, and interval extension. Covers the closest -d/-D a/b/ref/-t/-k/-io/-iu/-id flags, the -D ref strand sign-flip, silent chromosome-end clipping in slop/flank, -t all tie double-counting, and the critical distinction between a geometry answer (nearest TSS) and a biology answer (which gene an element regulates). Use when assigning peaks or variants to genes, defining promoters from a gene model, building distance-to-TSS distributions, finding features within a window, or extending intervals - and when deciding whether nearest-gene is a fair prior (GWAS locus) or a trap (distal enhancer).
tool_type: mixed
primary_tool: bedtools
---

## Version Compatibility

Reference examples tested with: bedtools 2.31+, pybedtools 0.10+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `bedtools --version` then `bedtools <subcommand> --help` to confirm flags
- Python: `pip show pybedtools` then `help(pybedtools.BedTool.closest)` to check signatures

`flank` and `slop` REQUIRE a chrom-sizes (`genome.txt`, two columns: chrom<TAB>length) file via `-g`; `closest` requires both inputs coordinate-sorted (`sort -k1,1 -k2,2n`). If code throws an error, introspect the installed tool and adapt rather than retrying.

# Proximity Operations

**"Which gene is nearest to each peak, and is that the gene it regulates?"** -> Compute interval geometry (nearest feature, signed distance, window membership, strand-aware promoters) with bedtools, then decide honestly whether geometry answers the biological question.
- CLI: `bedtools closest -D b -t first -a peaks.bed -b genes.bed`, `bedtools window -w 50000`, `bedtools slop -s -l 2000 -r 200 -g genome.txt`
- Python: `peaks.closest(genes.sort(), D='b', t='first')`, `peaks.window(genes, w=50000)`, `tss.slop(g='genome.txt', s=True, l=2000, r=200)` (pybedtools)

## The Single Most Important Modern Insight -- closest Answers a GEOMETRY Question Misread as a BIOLOGY Question

`bedtools closest` answers "what is the nearest annotated TSS?" - a coordinate fact. The user almost always wants "which gene does this element regulate?" - a biology claim. For distal regulatory elements these disagree the **majority of the time**. In the CRISPRi-FlowFISH gold standard (Fulco 2019 *Nat Genet* 51:1664), assigning each tested distal element to the **closest expressed gene gave only ~47% precision and ~37% recall** - the nearest gene was the wrong target most of the time, and the method missed nearly two-thirds of real links. Enhancers routinely skip intervening genes: the canonical case is the obesity-associated *FTO* intron regulating **IRX3 ~500 kb away**, not *FTO* (Smemo 2014 *Nature* 507:371). Do the bedtools arithmetic flawlessly here, then route real enhancer->gene linking to activity/contact/QTL methods (ABC: Fulco 2019, Nasser 2021; PCHi-C; eQTL-coloc) at atac-seq/enhancer-gene-linking - never present "nearest gene" as a regulatory call for a distal element.

The deeper twist - **two regimes, opposite advice, identical command:**
- **Enhancer -> target (closest is a TRAP).** Distal ATAC/H3K27ac peaks, enhancer GWAS variants: nearest gene is wrong most of the time. Use as a candidate generator, validate with ABC/PCHi-C/eQTL.
- **GWAS locus -> gene (closest is a fair PRIOR).** For a fine-mapped, colocalized credible-set SNP, the nearest **protein-coding** gene is right ~50-65% of the time - a strong, hard-to-beat baseline for which gene a locus implicates. Route to causal-genomics for the rigorous version, but nearest-coding-gene is a defensible first pass.

Conflating the two regimes is the real error. The discriminator: is the question the *target of an enhancer* (distrust nearest) or *the gene under a GWAS peak* (nearest is a fine first pass)?

## Operation Taxonomy

| Operation | What it computes | Strand-aware? | Needs genome file? |
|-----------|------------------|---------------|--------------------|
| closest | For each A, the nearest B (+ optional signed distance) | optional (`-s`/`-S`, `-D a`/`-D b`) | no |
| window | For each A, all B within +-W bp (fuzzy intersect) | optional (`-sw`/`-sm`/`-Sm`) | no |
| slop | Grow each interval by N bp, keeping it one feature | optional (`-s`) | yes (`-g`) |
| flank | Emit the regions BESIDE each interval, dropping the body | optional (`-s`) | yes (`-g`) |

`closest`/`window` are queries (A vs B); `slop`/`flank` are transforms (A only, + genome file). The slop-vs-flank distinction trips people: `slop -b 1000` makes a peak 2 kb wider (one feature); `flank -b 1000` returns only the left/right neighboring 1 kb regions and discards the peak itself (two features). `window -w 0` is approximately `intersect`.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Nearest gene to a promoter-proximal mark (H3K4me3, Pol II, CAGE) | `closest -D b -io -t first` | the peak really is at the gene it marks; closest is honest here |
| Distal enhancer / ATAC peak -> which gene? | `closest`/`window` as candidates, then -> atac-seq/enhancer-gene-linking | nearest is wrong the majority of the time (ABC/PCHi-C/eQTL link it) |
| GWAS credible-set SNP -> implicated gene | `closest` to nearest **protein-coding** gene, then -> causal-genomics/colocalization-analysis | nearest-coding-gene is a ~50-65% prior; a fair first pass |
| All candidate genes near an element | `window -w 50000` (or TAD-scale) | honest "candidate set", not a single call |
| Build promoters from a gene model | collapse to TSS, then `slop -s -l UP -r DOWN -g` | a promoter is an imposed definition, strand-aware, from the TSS |
| Distance-to-TSS distribution | `closest -D b -d` then plot signed distance | a distribution beats a binary "promoter vs distal" threshold |
| Upstream-only / downstream-only nearest | `closest -D b -iu` / `-id` | direction must be strand-relative (`-D b`), never `-D ref` |
| Peak-set GO enrichment from proximity | -> GREAT/rGREAT (regulatory-domain model) | avoids the `-t all` double-counting and distal mis-assignment |
| Regions flanking a feature (splice/boundary context) | `flank -s -b N -g` | the regions outside the feature, strand-aware |
| Peaks not yet called | -> chip-seq/peak-calling, atac-seq/atac-peak-calling | this skill operates on existing intervals |

## closest - Nearest Feature with Signed, Strand-Aware Distance

Default: for each A, report the single nearest B; **on ties, report ALL tied B** (`-t all` is the default - the double-counting trap below). Both inputs must be sorted. When A's chromosome has no B feature, bedtools prints `none` for B columns and **`-1`** for distance - filter this sentinel before any numeric summary.

```bash
# Nearest gene, signed distance by the GENE's strand, ignore overlaps, one row per peak
bedtools sort -i peaks.bed > peaks.sorted.bed
bedtools sort -i genes.bed  > genes.sorted.bed
bedtools closest -a peaks.sorted.bed -b genes.sorted.bed -D b -io -t first > nearest.bed
#                                                         ^^^^ sign by gene strand (biology, not coordinates)
#                                                              ^^^ closest non-overlapping gene
#                                                                  ^^^^^^^^ resolve ties deterministically (document this)

# k=3 nearest with unsigned distance (k>1 intentionally multiplies rows)
bedtools closest -a peaks.sorted.bed -b genes.sorted.bed -k 3 -d > top3.bed
```

```python
import pybedtools

peaks = pybedtools.BedTool('peaks.bed').sort()
genes = pybedtools.BedTool('genes.bed').sort()
near = peaks.closest(genes, D='b', io=True, t='first')      # -D b -io -t first
near = near.filter(lambda x: int(x.fields[-1]) != -1)        # drop the no-feature sentinel
near.saveas('nearest.bed')
```

Key flags: `-d` unsigned distance (overlaps = 0); `-D ref` signed by coordinate only (strand-agnostic - see Failure Modes); `-D a`/`-D b` signed by A's / B's strand; `-t all|first|last`; `-k N` k-nearest; `-io` ignore overlapping B; `-iu`/`-id` ignore upstream/downstream (require `-D`); `-fu`/`-fd` first upstream/downstream; `-s`/`-S` same/opposite strand; `-N` require different names; `-mdb each|all` and `-names`/`-filenames` for multiple `-b` files.

## window - Features Within a Search Radius

`window` reports all B within a window around each A (default 1000 bp each side). Use it for the honest "candidate genes near this element" framing.

```bash
# All genes within 50 kb of each peak, counted per peak
bedtools window -a peaks.bed -b genes.bed -w 50000 -c > peak_gene_counts.bed
```

Flags: `-w N` symmetric (default 1000); `-l N`/`-r N` asymmetric (coordinate left/right); `-sw` define `-l`/`-r` BY STRAND; `-sm`/`-Sm` keep only same/opposite-strand B; `-u` boolean (A once if any B); `-c` count of B per A; `-v` A with no B in window. `-sw` controls *where the window is*; `-sm`/`-Sm` control *which B count* - distinct concerns.

## slop / flank - Extend or Find Adjacent Regions (genome file REQUIRED)

Both need `-g genome.txt` precisely so they can clip at chromosome boundaries - extension past coordinate 0 or past chrom length is **silently truncated** (start floored at 0, end capped). Flags: `-b N` both sides; `-l N`/`-r N` per side (coordinate unless `-s`); `-s` strand-aware (on a `-`-strand feature `-l` adds to the END, so `-l` always means "upstream of the feature"); `-pct` treat N as a fraction of feature length; `-header` echo input header.

### Build Strand-Aware Promoters from a Gene Model

**Goal:** Produce a promoter BED (TSS -2000 / +200 bp, strand-aware) that is correct for both strands - the right way to define "promoter", which is a choice imposed on a TSS, not an annotated feature.

**Approach:** Collapse genes to their TSS first (start for `+`, end-1 for `-`), THEN `slop -s` so "upstream" tracks strand. Running `slop -b 2000` on a gene BODY is the wrong promoter (it grows the whole gene, ignores strand).

```bash
# 1) TSS BED from a BED6 gene model (strand-aware single base)
awk -v OFS='\t' '{ if ($6=="+") print $1,$2,$2+1,$4,$5,$6; else print $1,$3-1,$3,$4,$5,$6 }' genes.bed > tss.bed

# 2) Promoter = TSS -2000 / +200, strand-aware (-l is always the upstream side under -s)
bedtools slop -i tss.bed -g genome.txt -s -l 2000 -r 200 > promoters.bed
```

```python
import pybedtools

UP = 2000   # bp upstream of TSS; common core-promoter convention, NOT a fact -- report it and tune per assay
DOWN = 200  # bp downstream of TSS; asymmetric on purpose (+1 nucleosome / 5'UTR sit downstream)

genes = pybedtools.BedTool('genes.bed')
tss = genes.each(lambda f: pybedtools.create_interval_from_list([f[0], str(f.start) if f.strand == '+' else str(f.end - 1), str(f.start + 1) if f.strand == '+' else str(f.end), f.name, f.score, f.strand])).saveas()
promoters = tss.slop(g='genome.txt', s=True, l=UP, r=DOWN).saveas('promoters.bed')
```

`flank` shares the flag vocabulary but emits the regions BESIDE each feature and drops the original (two intervals per input, used for splice/boundary context):

```bash
bedtools flank -i exons.bed -g genome.txt -s -b 1000 > exon_flanks.bed   # 1 kb each side, strand-aware
```

## Per-Method Failure Modes

### -D ref silently mis-signs minus-strand genes
**Trigger:** using `closest -D ref` and interpreting the sign as upstream/downstream. **Mechanism:** `-D ref` signs by genomic coordinate only (lower = negative); for a `-`-strand gene the TSS is at the HIGHER coordinate, so "upstream" runs to higher coordinates and the coordinate sign is inverted relative to biology. **Symptom:** half the genes (the `-`-strand ones) are folded the wrong way; symmetric QC (TSS-enrichment plot) still looks fine, but any "enhancers preferentially upstream" claim washes out or inverts. **Fix:** use `-D b` (sign by the gene's strand) for any upstream/downstream biology; reserve `-D ref` for pure left/right genomic distance.

### slop on a gene body is not a promoter
**Trigger:** `slop -b 2000` (or `-l 2000 -r 0` without `-s`) on a gene-body BED, called "the promoter". **Mechanism:** it grows the window around the whole gene, not the TSS, and without `-s` adds the "upstream" side to the wrong (3') end on `-`-strand genes. **Symptom:** a 100 kb gene becomes a 104 kb "promoter"; every `-`-strand promoter is shifted into the gene body. **Fix:** collapse to TSS first, then `slop -s -l UP -r DOWN`.

### slop/flank clip silently at chromosome ends
**Trigger:** fixed-width windows near contig starts / telomeres. **Mechanism:** slop/flank truncate at 0 and chrom length with no warning. **Symptom:** a TSS 800 bp from a contig start yields a 1000-bp (not 2000-bp) upstream window - quietly asymmetric, biasing per-window normalization (reads/kb, motif density); flank can drop a region entirely, breaking a 2:1 feature->flank assumption. **Fix:** after slop verify `end-start == requested width`; after flank verify the per-feature flank count; treat chrom-end features as edge cases.

### -t all double-counts ties into inflated enrichment
**Trigger:** letting default `-t all` rows flow into a per-gene tally, `wc -l` peak count, or GO/hypergeometric enrichment. **Mechanism:** a peak equidistant to two TSSs emits two rows; ties concentrate NON-randomly at bidirectional (head-to-head) promoters and gene-dense regions. **Symptom:** association counts inflated exactly where biology is most interesting; broken independence inflates significance. **Fix:** `-t first` (deterministic but arbitrary - document it) OR `-t all` then aggregate counting distinct PEAKS not rows; for enrichment prefer GREAT/rGREAT, whose regulatory-domain model exists to avoid this artifact.

### closest on unsorted input
**Trigger:** `closest` on a BED that was filtered/edited and not re-sorted. **Mechanism:** closest assumes coordinate-sorted input. **Symptom:** wrong nearest feature or an error. **Fix:** `bedtools sort` (or `.sort()` in pybedtools) both A and B first.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Promoter TSS -2000 / +200 bp (strand-aware) | common convention | a CHOICE, not a fact; asymmetric because core-promoter elements sit upstream and the +1 nucleosome / 5'UTR downstream. Report it; "% promoter-proximal" is sensitive to it |
| GREAT basal domain 5 kb up / 1 kb down, extension <=1 Mb | McLean 2010 *Nat Biotechnol* 28:495 | the principled "proximity++": asymmetric basal domain + extension to the neighbor, a far better proximity heuristic than raw closest |
| ChIPseeker default promoter +-3 kb | tool default | shows the convention spans an order of magnitude (+-500 bp to +-10 kb across tools) |
| ABC candidate window 5 Mb | Fulco 2019 | activity-by-contact scores all elements within 5 Mb of a gene's promoter - "distal" is tens of kb to megabases |
| Nearest gene precision/recall ~47% / ~37% (enhancers) | Fulco 2019 CRISPRi-FlowFISH | the empirical ceiling on nearest-gene for distal-enhancer targeting |
| Nearest protein-coding gene ~50-65% right (GWAS loci) | fine-mapping/coloc literature | the GWAS-regime baseline; strong, hard to beat, but imperfect |
| Distal flag |dist| > ~50-100 kb | field convention | beyond promoter scale; flag for ABC/PCHi-C/eQTL validation rather than trusting nearest |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Nearest-gene call wrong for an enhancer | geometry != regulation for distal elements | treat as candidate; route to atac-seq/enhancer-gene-linking (ABC/PCHi-C/eQTL) |
| Upstream/downstream asymmetry washes out or inverts | `-D ref` mis-signs `-`-strand genes | use `-D b` |
| Promoter window includes the whole gene | `slop -b` on a gene body, not the TSS | collapse to TSS, then `slop -s -l UP -r DOWN` |
| Per-gene counts inflated near bidirectional promoters | `-t all` rows counted as peaks | `-t first` or aggregate by distinct peak; or use GREAT |
| Asymmetric "fixed-width" windows near contig ends | silent slop/flank clipping | verify `end-start`; treat chrom-end features as edge cases |
| `none` / `-1` rows poison a mean distance | no B feature on that chromosome | filter the `-1` sentinel before summarizing |
| Wrong nearest feature, or closest errors | unsorted input | `bedtools sort` both A and B |
| Empty output | `chr1` vs `1` naming mismatch between A, B, genome file | harmonize chromosome naming across all files |

## References

- Quinlan AR, Hall IM. 2010. BEDTools: a flexible suite of utilities for comparing genomic features. *Bioinformatics* 26:841-842.
- Dale RK, Pedersen BS, Quinlan AR. 2011. Pybedtools: a flexible Python library for manipulating genomic datasets and annotations. *Bioinformatics* 27:3423-3424.
- Fulco CP, Nasser J, Jones TR, et al. 2019. Activity-by-contact model of enhancer-promoter regulation from thousands of CRISPR perturbations. *Nat Genet* 51:1664-1669.
- Nasser J, Bergman DT, Fulco CP, et al. 2021. Genome-wide enhancer maps link risk variants to disease genes. *Nature* 593:238-243.
- Smemo S, Tena JJ, Kim KH, et al. 2014. Obesity-associated variants within FTO form long-range functional connections with IRX3. *Nature* 507:371-375.
- McLean CY, Bristor D, Hiller M, et al. 2010. GREAT improves functional interpretation of cis-regulatory regions. *Nat Biotechnol* 28:495-501.

## Related Skills

- bed-file-basics - BED coordinate systems and the sort/conversion this skill depends on
- gtf-gff-handling - Extract TSS and gene models from GTF/GFF for promoter construction
- interval-arithmetic - intersect/merge/subtract; window -w 0 is approximately intersect
- chip-seq/peak-annotation - Assigns peaks to genes via the same closest-TSS logic and caveats
- atac-seq/enhancer-gene-linking - The real enhancer->gene science (ABC, contact, peak-gene correlation) this skill routes distal calls to
- atac-seq/footprinting - Uses strand-aware windows over motif/TSS sites
- data-visualization/genome-tracks - Render the promoter/proximity intervals built here
<!-- END FILE: genome-intervals/proximity-operations/SKILL.md -->

<!-- END CATEGORY: genome-intervals -->

