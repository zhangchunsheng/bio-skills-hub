---
slug: bio-sequence-io-integrated
version: 1.0.0
displayName: "序列I/O / Read, write, convert, and compress sequence files in FASTA, FASTQ, GenBank, EMBL, and other formats"
name: bio-sequence-io-integrated
summary: >-
  中文：序列I/O综合技能，整合 9 个相关专题，覆盖序列文件的读取、写入、转换与压缩处理，支持FASTA、FASTQ、GenBank、EMBL等格式。 English: Integrated Read, write, convert, and compress sequence files in FASTA, FASTQ, GenBank, EMBL, and other formats skill covering 9 related topics, including Read, write, convert, and compress sequence files in FASTA, FASTQ, GenBank, EMBL, and other formats.
description: >-
  中文：这是一个面向序列I/O的综合生物信息学 Skill，整合当前分类下 9 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：序列文件的读取、写入、转换与压缩处理，支持FASTA、FASTQ、GenBank、EMBL等格式。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Bio.SeqIO, Bio.bgzf。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Read, write, convert, and compress sequence files in FASTA, FASTQ, GenBank, EMBL, and other formats, combining 9 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Read, write, convert, and compress sequence files in FASTA, FASTQ, GenBank, EMBL, and other formats. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Bio.SeqIO, Bio.bgzf. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# sequence-io 分类 Skill 整合版

> 本文件整合同一主分类目录下 9 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: sequence-io -->

## 子目录：sequence-io/batch-processing

<!-- BEGIN FILE: sequence-io/batch-processing/SKILL.md -->
---
name: bio-batch-processing
description: Process many sequence files in batch (count, merge, split, convert, summarize) with memory-safe streaming and on-disk indexing using Biopython, pysam, or pyfastx. Use when iterating over a directory of FASTA/FASTQ files, merging or splitting datasets, building random access across many or huge files, or automating per-file operations without exhausting RAM.
tool_type: python
primary_tool: Bio.SeqIO
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+ (alternatives: pysam 0.22+, pyfastx 2.0+)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Batch Processing

**"Process all my sequence files in a directory"** -> Iterate, merge, split, convert, and summarize across multiple sequence files without loading everything into RAM.
- Python: `SeqIO.parse()` + `Path.glob()` (BioPython, pathlib) for streaming
- Python: `SeqIO.index_db()` (BioPython) for persistent random access across many files
- Python: `pysam.FastxFile` (pysam) or `pyfastx` for fast iteration over huge FASTQ

## The Governing Principle

`list(SeqIO.parse(...))` materializes every `SeqRecord` in RAM at once. On a directory of large files this causes OOM. `SeqIO.parse()` itself returns a generator that holds one record at a time, so streaming is the default for batch work: iterate, never `list()`, unless the file is known-small and needs multiple passes.

For random access across many or huge files, do not load them. `SeqIO.index_db()` builds one on-disk SQLite index over a list of files that persists across sessions. That, not `to_dict()`, is the batch random-access tool.

For tens of millions of reads, `SeqIO` is slow by design: it constructs a full `SeqRecord` (a `Seq`, id/name/description, and a `letter_annotations` dict of per-base qualities) for every read. When the job is plain linear iteration, a thinner reader wins.

## Choosing a Reader

| Reader | Per-record object | Random access | Best for |
|--------|-------------------|---------------|----------|
| `Bio.SeqIO.parse` | full `SeqRecord` (rich API) | no (one-pass generator) | small/medium data needing the Biopython record API |
| `Bio.SeqIO.index_db` | reparsed `SeqRecord` on access | yes, on-disk SQLite, multi-file, persists | batch random access across many/huge files |
| `pysam.FastxFile` | thin entry (`.name/.sequence/.comment/.quality`) | no (linear, gzip sequential) | fast linear iteration over huge FASTQ |
| `pyfastx` | tuple/object via SQLite index | yes, into plain or gzipped FASTA/Q | random access + indexed reuse of gzipped files |

`pysam.FastxFile` exposes `.name`, `.sequence`, `.comment`, `.quality`, and `.get_quality_array()` (offset-removed int Phred, but it always subtracts 33, so it is correct only for Phred+33 data - for legacy Phred+64/Solexa stay on `SeqIO` with the explicit variant string). `pyfastx` builds a persistent `.fxi`/`.fqi` SQLite index and reads random records out of plain or gzipped files without re-bgzipping.

## Required Imports

```python
from pathlib import Path
from Bio import SeqIO
```

## Iterate and Count Across Files

Count by iterating, never by building a list. `len(list(SeqIO.parse(f)))` loads the whole file; `sum(1 for _ in ...)` holds one record at a time.

```python
for fasta_file in Path('data/').glob('*.fasta'):
    count = sum(1 for _ in SeqIO.parse(fasta_file, 'fasta'))
    print(f'{fasta_file.name}: {count} sequences')
```

Recursive search uses `rglob`:

```python
for gb_file in Path('data/').rglob('*.gb'):
    print(f'Found: {gb_file}')
```

For huge FASTQ where only sequence content matters, skip `SeqRecord` construction entirely:

```python
import pysam

with pysam.FastxFile('reads.fastq.gz') as fh:
    count = sum(1 for _ in fh)
```

## Random Access Across Many Files

**Goal:** Look up records by id across a whole directory of files, repeatedly, without holding them in RAM.

**Approach:** Build one persistent on-disk SQLite index over the file list with `index_db`. Reopen later with just the index path; lookups reparse single records from disk on demand.

**Reference (BioPython 1.83+):**

```python
from pathlib import Path
from Bio import SeqIO

files = [str(p) for p in Path('data/').glob('*.fasta')]
records = SeqIO.index_db('combined.idx', files, 'fasta')

print(len(records))            # total across all files
record = records['seq_00042']  # random access by id
records.close()
```

The index file persists. A later session calls `SeqIO.index_db('combined.idx')` with no file list and reopens instantly. Ids must be unique across the merged set: a collision raises `ValueError: Duplicate key`. `index_db` also indexes BGZF-compressed files; plain gzip is not seekable and cannot be indexed.

## Merge Files

**Goal:** Concatenate sequences from many files into one output without loading them all.

**Approach:** Chain per-file generators with `yield from` and stream straight into `SeqIO.write`, which consumes the generator one record at a time.

**Reference (BioPython 1.83+):**

```python
def all_records(directory, pattern, format):
    for filepath in Path(directory).glob(pattern):
        yield from SeqIO.parse(filepath, format)

count = SeqIO.write(all_records('data/', '*.fasta', 'fasta'), 'merged.fasta', 'fasta')
print(f'Merged {count} records')
```

### Merge with Source Tracking

**Goal:** Combine sequences from multiple files, tagging each record with its source filename.

**Approach:** Stream records through a generator that appends source metadata to the description before writing.

**Reference (BioPython 1.83+):**

```python
def records_with_source(directory, pattern, format):
    for filepath in Path(directory).glob(pattern):
        for record in SeqIO.parse(filepath, format):
            record.description = f'{record.description} [source={filepath.name}]'
            yield record

SeqIO.write(records_with_source('data/', '*.fasta', 'fasta'), 'merged_tracked.fasta', 'fasta')
```

When merging files that may share ids, decide upfront: write-then-merge tolerates duplicates (FASTA allows repeated ids), but any later `index_db`/`to_dict` over the merged file raises on the duplicate.

## Split Files

### Split by Number of Records

**Goal:** Divide a large file into chunks of N records each.

**Approach:** Consume the parse generator in fixed-size batches with `islice`, writing each batch to a numbered file. `islice` pulls only N records into memory per chunk, so an arbitrarily large input streams safely.

**Reference (BioPython 1.83+):**

```python
from itertools import islice

def split_file(input_file, format, records_per_file, output_prefix):
    records = SeqIO.parse(input_file, format)
    file_num = 1
    while True:
        batch = list(islice(records, records_per_file))
        if not batch:
            break
        output_file = f'{output_prefix}_{file_num}.{format}'
        SeqIO.write(batch, output_file, format)
        print(f'Wrote {len(batch)} records to {output_file}')
        file_num += 1

split_file('large.fasta', 'fasta', 1000, 'split')
```

On Python 3.12+, `itertools.batched(records, records_per_file)` yields the same fixed-size tuples without the manual `while`/`islice` loop.

### Split by Sequence ID Prefix

**Goal:** Group sequences into separate files by a shared id prefix (sample or chromosome).

**Approach:** Route each record to a per-prefix open output handle while streaming, so no group is fully held in RAM.

**Reference (BioPython 1.83+):**

```python
handles = {}
for record in SeqIO.parse('input.fasta', 'fasta'):
    prefix = record.id.split('_')[0]
    if prefix not in handles:
        handles[prefix] = open(f'{prefix}.fasta', 'w')
    SeqIO.write(record, handles[prefix], 'fasta')

for handle in handles.values():
    handle.close()
```

## Batch Convert

```python
for gb_file in Path('genbank/').glob('*.gb'):
    fasta_file = Path('fasta/') / gb_file.with_suffix('.fasta').name
    count = SeqIO.convert(str(gb_file), 'genbank', str(fasta_file), 'fasta')
    print(f'{gb_file.name} -> {fasta_file.name}: {count} records')
```

`SeqIO.convert` streams internally and never loads the whole file. GenBank-to-FASTA silently drops features, annotations, and qualifiers (FASTA stores only id, description, and sequence); see sequence-io/format-conversion before converting away annotated formats.

## Parallel Processing

For CPU-bound per-file work, distribute whole files across processes. Each worker streams its own file, so peak memory is one file's records per process, not the whole directory.

```python
from multiprocessing import Pool

def process_file(filepath):
    total = 0
    bp = 0
    for record in SeqIO.parse(filepath, 'fasta'):
        total += 1
        bp += len(record.seq)
    return {'file': filepath.name, 'count': total, 'total_bp': bp}

files = list(Path('data/').glob('*.fasta'))
with Pool(4) as pool:
    results = pool.map(process_file, files)
```

Use `concurrent.futures.ThreadPoolExecutor` instead for I/O-bound work (gzip decode, network filesystems); the GIL makes threads pointless for CPU-bound parsing.

## Summary Statistics

**Goal:** Build a per-file CSV of counts and length stats for a directory.

**Approach:** Stream each file once, accumulating count, total, min, and max as integers rather than collecting a length list per file.

**Reference (BioPython 1.83+):**

```python
import csv

summaries = []
for fasta_file in Path('data/').glob('*.fasta'):
    count = total = 0
    min_len = None
    max_len = 0
    for record in SeqIO.parse(fasta_file, 'fasta'):
        n = len(record.seq)
        count += 1
        total += n
        max_len = max(max_len, n)
        min_len = n if min_len is None else min(min_len, n)
    summaries.append({'file': fasta_file.name, 'sequences': count, 'total_bp': total,
                      'min_len': min_len or 0, 'max_len': max_len,
                      'avg_len': total / count if count else 0})

with open('summary.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=summaries[0].keys())
    writer.writeheader()
    writer.writerows(summaries)
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `MemoryError` / process killed on a directory | `list(SeqIO.parse(...))` materializes every record at once | Stream the generator; iterate or `sum(1 for _ in ...)`; never `list()` a large file |
| Counting/merge job runs for minutes on tens of millions of reads | `SeqIO` builds a full `SeqRecord` per read | Use `pysam.FastxFile` for linear iteration, or `pyfastx` for indexed access |
| `ValueError: Duplicate key` from `index_db`/`to_dict` | Same id appears in more than one merged file | Make ids unique (prefix by filename) or supply a `key_function` |
| Second loop over `SeqIO.parse(...)` yields nothing | The generator is one-pass and exhausts silently | Re-create the generator per pass, or use `index_db` for repeated access |
| `index_db` fails on a `.gz` file | Plain gzip is not seekable | Re-compress with `bgzip`; only BGZF is indexable (sequence-io/compressed-files) |
| Annotations missing after batch convert | GenBank-to-FASTA drops all features silently | Keep an annotated format, or extract needed qualifiers first |

## Related Skills

- read-sequences - parse, index, and index_db semantics for each file
- filter-sequences - apply per-record filters while streaming a batch
- sequence-statistics - N50 and length distributions across files
- format-conversion - batch format conversion and its data-loss traps
- compressed-files - BGZF vs plain gzip for indexable batch random access
- paired-end-fastq - keep R1/R2 synchronized when batch-filtering mates
- database-access/entrez-fetch - batch download sequences from NCBI
<!-- END FILE: sequence-io/batch-processing/SKILL.md -->

## 子目录：sequence-io/compressed-files

<!-- BEGIN FILE: sequence-io/compressed-files/SKILL.md -->
---
name: bio-compressed-files
description: Read, write, and index compressed sequence files (gzip, bzip2, xz, BGZF) with Biopython and bgzip/samtools. Use when working with .gz, .bz2, or .bgz sequence files, when random access into a compressed FASTA/FASTQ is needed, or when SeqIO.index/faidx/tabix rejects a plain .gz. Covers the BGZF-vs-gzip seekability asymmetry, the 'rt'-not-'rb' handle trap, virtual offsets, and gzip-to-BGZF conversion.
tool_type: mixed
primary_tool: Bio.bgzf
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, htslib/bgzip 1.19+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Compressed Files

Read, write, and randomly access gzip, bzip2, xz, and BGZF compressed sequence files.

**"Read a compressed sequence file"** -> Open a decompression handle in TEXT mode, then parse with the standard SeqIO interface.
- gzip: `gzip.open(path, 'rt')` (Python stdlib)
- bzip2: `bz2.open(path, 'rt')` (Python stdlib)
- xz/LZMA: `lzma.open(path, 'rt')` (Python stdlib)
- BGZF: `bgzf.open(path, 'rt')` (BioPython) - BGZF input ONLY

**"Make a compressed file randomly accessible"** -> Re-compress as BGZF, then index. Only BGZF supports `SeqIO.index()`, `samtools faidx`, and `tabix` on compressed data.

## The Governing Principle: BGZF vs plain gzip is asymmetric

A BGZF (Blocked GNU Zip) file IS a valid gzip file - `gunzip` and `zcat` read it transparently. The reverse is FALSE: a plain `.gz` is NOT BGZF, so `faidx`/`tabix`/`SeqIO.index` reject it, and `bgzf.open` refuses to read it.

The reason is structural. BGZF is a series of concatenated gzip blocks, each <=64 KiB and independently decodable, so any record can be reached by seeking to its block. Plain gzip is one continuous DEFLATE stream with no block boundaries: reaching byte N means decompressing every byte before it (O(n)). Random access therefore REQUIRES BGZF; on a plain `.gz`, `SeqIO.index()` would re-decompress huge prefixes on every lookup, which is why Biopython forbids it outright (it raises rather than running slowly).

Consequences the agent must respect:
- Reading sequentially: gzip, bzip2, xz, and BGZF all work via the matching `*.open(path, 'rt')` handle.
- Random access / indexing: BGZF only. Convert plain gzip to BGZF first.
- `bgzf.open()` reads BGZF input only. Pointing it at a plain `.gz` raises `ValueError: A BGZF block should start with b'\x1f\x8b\x08\x04'...`. To read plain gzip use `gzip.open()`.
- BAM and tabix-indexed files use BGZF natively; bzip2/xz are archive-only (no seekable index).

## Required Imports

```python
import gzip
import bz2
import lzma
from Bio import SeqIO
from Bio import bgzf
```

## Reading Compressed Files

**Goal:** Parse sequence records from a compressed file without decompressing to disk.

**Approach:** Open a decompression handle in TEXT mode (`'rt'`), then pass the handle to `SeqIO.parse()`. The parser is format-agnostic about the underlying compression.

```python
with gzip.open('reads.fastq.gz', 'rt') as handle:
    for record in SeqIO.parse(handle, 'fastq'):
        print(record.id, len(record.seq))
```

Swap `gzip.open` for `bz2.open` (`.bz2`), `lzma.open` (`.xz`), or `bgzf.open` (`.bgz`) - the parse loop is identical.

### The 'rt' vs 'rb' trap

`SeqIO.parse()` in Python 3 needs a TEXT handle that yields `str`. A binary `'rb'` handle yields `bytes` and raises `TypeError: a bytes-like object is required` (or a decode error). Always use `'rt'` for reading and `'wt'` for writing through `SeqIO`. The low-level `SimpleFastaParser`/`FastqGeneralIterator` also require text handles.

## Writing Compressed Files

**Goal:** Save records straight to a compressed file with no intermediate plain copy.

**Approach:** Open a compression handle in TEXT mode (`'wt'`), then pass it to `SeqIO.write()`.

```python
with gzip.open('output.fasta.gz', 'wt') as handle:
    SeqIO.write(records, handle, 'fasta')
```

For an indexable result write BGZF instead:

```python
with bgzf.open('output.fasta.bgz', 'wt') as handle:
    SeqIO.write(records, handle, 'fasta')
```

`BgzfWriter.close()` (and the `with` block exit) automatically appends the 28-byte empty-block EOF marker that htslib tools check for; let the context manager close the handle.

## Random Access: index a BGZF file

**Goal:** Pull individual records by id from a large compressed file without a linear scan.

**Approach:** Compress as BGZF, then build a Biopython offset index. `SeqIO.index()` keeps virtual offsets in RAM; `SeqIO.index_db()` stores them in an on-disk SQLite index that persists across sessions and spans multiple files.

```python
records = SeqIO.index('sequences.fasta.bgz', 'fasta')
target = records['gene_042'].seq
records.close()

# Persistent, multi-file, scales beyond RAM:
db = SeqIO.index_db('idx.sqlite', ['a.fasta.bgz', 'b.fasta.bgz'], 'fasta')
```

`SeqIO.index()` on a plain `.gz` raises `ValueError: Gzipped files are not suitable for indexing, please use BGZF (blocked gzip format) instead.` Convert first (below).

## Convert plain gzip to BGZF

**"Convert gzip to an indexable format"** -> Decompress the gzip stream and re-compress it as BGZF.

CLI (fastest, htslib-native):

```bash
# Either decompress then bgzip in place...
gzip -d sequences.fasta.gz && bgzip sequences.fasta      # -> sequences.fasta.gz (now BGZF)
# ...or stream without touching disk:
zcat sequences.fasta.gz | bgzip -@ 4 > sequences.fasta.bgz

# Index a BGZF FASTA for region extraction:
samtools faidx sequences.fasta.bgz                        # writes BOTH .fai and .gzi
samtools faidx sequences.fasta.bgz gene_042:1-200
```

`samtools faidx` on a BGZF FASTA writes TWO index files: `.fai` (record offsets in uncompressed coordinates) AND `.gzi` (the compressed-to-uncompressed block map). Deleting `.gzi` breaks region extraction even though `.fai` survives. Note that bgzip keeps the `.gz` extension, so a `.gz` may be EITHER plain gzip or BGZF - check with `bgzip -t file.gz` (tests for a valid BGZF stream) rather than trusting the suffix.

Pure-Python equivalent (no external tools):

```python
import gzip
from Bio import SeqIO, bgzf

with gzip.open('input.fasta.gz', 'rt') as in_handle:
    with bgzf.open('output.fasta.bgz', 'wt') as out_handle:
        SeqIO.write(SeqIO.parse(in_handle, 'fasta'), out_handle, 'fasta')
```

## Bio.bgzf API and virtual offsets

`Bio.bgzf` exports `open`, `BgzfReader`, `BgzfWriter`, `make_virtual_offset`, `split_virtual_offset`.

A virtual offset packs two coordinates into one 64-bit integer: `voffset = coffset << 16 | uoffset`, where `coffset` is the byte position of the block start in the compressed file (top 48 bits) and `uoffset` is the offset within that block's decompressed data (low 16 bits - 16 bits suffices because a block holds at most 64 KiB).

```python
vo = bgzf.make_virtual_offset(100, 7)        # 6553607
coffset, uoffset = bgzf.split_virtual_offset(vo)   # (100, 7)

with bgzf.open('sequences.fasta.bgz', 'rt') as handle:
    handle.readline()
    saved = handle.tell()        # a VIRTUAL offset, not a byte position
    handle.seek(saved)           # jumps back to the same record
```

Critical caveat: virtual offsets may be COMPARED for ordering but NEVER SUBTRACTED to get a byte length - they live in two coordinate spaces (compressed position and within-block position), so `vo2 - vo1` is meaningless. `BgzfReader.tell()` returns a virtual offset; `seek()` consumes one. Text mode forces `latin1` and does no newline translation.

## Compression Format Comparison

| Format | Extension | Random access | Speed | Ratio | Stdlib handle |
|--------|-----------|---------------|-------|-------|---------------|
| gzip | `.gz` | No (O(n) seek) | Fast | Good | `gzip.open` |
| BGZF | `.bgz` / `.gz` | **Yes (block-seekable)** | Fast, threadable | Good | `bgzf.open` (BioPython) |
| bzip2 | `.bz2` | No | Slow | Better | `bz2.open` |
| xz / LZMA | `.xz` | No | Slowest | Best | `lzma.open` |

## When to Use Each Format

| Use case | Format | Why |
|----------|--------|-----|
| Sequential read/write, sharing | gzip | Universal, fast, every tool reads it |
| Need `faidx`/`tabix`/`SeqIO.index` | **BGZF** | Only seekable compressed format |
| BAM, tabix-indexed VCF/GFF/BED | BGZF | Required natively |
| Cold archive, max shrink, no random access | xz then bzip2 | Highest ratios, slowest |
| Random access into an existing plain `.gz` without re-bgzipping | pyfastx | Adds a seek-point index over the gzip stream |

`pyfastx` is the exception that gives random access into a PLAIN gzip FASTA/FASTQ: it builds a seek-point index (via `zran` from indexed_gzip) plus a SQLite `.fxi`/`.fqi` index alongside the file, a different strategy from faidx (which requires the stream itself to be BGZF). Use it when re-compressing a large gzipped genome to BGZF is not an option.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `TypeError: a bytes-like object is required` | Handle opened `'rb'` instead of `'rt'` | Open compressed handles with `'rt'`/`'wt'` for SeqIO |
| `ValueError: Gzipped files are not suitable for indexing, please use BGZF...` | `SeqIO.index()` on a plain `.gz` | Re-compress as BGZF (`zcat ... | bgzip`), then index |
| `ValueError: A BGZF block should start with b'\x1f\x8b\x08\x04'...` | `bgzf.open()` pointed at a plain gzip file | Read plain gzip with `gzip.open()`; reserve `bgzf.open` for BGZF |
| `[bgzf] file ... not BGZF` / `not compressed with bgzip` (htslib) | faidx/tabix given a plain `.gz` | Convert to BGZF first |
| `[faidx] Failed to read ... / could not load .gzi` | `.gzi` deleted next to a BGZF FASTA | Re-run `samtools faidx` to regenerate `.fai` + `.gzi` |
| `gzip.BadGzipFile` / `OSError: Not a gzipped file` | File is not gzip (wrong suffix / corrupt) | Verify with `bgzip -t` or `file`; match handle to real format |
| `UnicodeDecodeError` | Non-UTF8 bytes in a text handle | `gzip.open(path, 'rt', encoding='latin-1')` |

## Related Skills

- read-sequences - parse vs index vs index_db trade-offs for compressed handles
- write-sequences - write records through a compression handle
- batch-processing - stream many compressed files without loading them into RAM
- filter-sequences - keep R1/R2 in sync when filtering gzipped paired reads
- alignment-files/sam-bam-basics - BAM is BGZF natively; samtools manages the compression

## References

- Li H, Handsaker B, Wysoker A, et al. The Sequence Alignment/Map format and SAMtools. Bioinformatics. 2009;25(16):2078-2079. (Defines BGZF in the SAM/BAM specification.)
- Bonfield JK. CRAM 3.1: advances in the CRAM file format. Bioinformatics. 2022;38(6):1497. (Per-column block compression beyond BGZF.)
- Du L, Liu Q, Fan Z, et al. Pyfastx: a robust Python package for fast random access to sequences from plain and gzipped FASTA/Q files. Briefings in Bioinformatics. 2021;22(4):bbaa368.
<!-- END FILE: sequence-io/compressed-files/SKILL.md -->

## 子目录：sequence-io/fastq-quality

<!-- BEGIN FILE: sequence-io/fastq-quality/SKILL.md -->
---
name: bio-fastq-quality
description: Work with FASTQ quality scores using Biopython - access Phred scores, filter and trim by quality, compute per-position profiles, and convert between Sanger/Phred+33, Solexa, and Illumina/Phred+64 encodings. Use when analyzing read quality, filtering or trimming low-quality bases, generating quality reports, or deciding which FASTQ quality encoding a file uses before parsing.
tool_type: python
primary_tool: Bio.SeqIO
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# FASTQ Quality Scores

**"Filter my FASTQ reads by quality score"** -> Access, analyze, and filter per-base quality scores, trim low-quality bases, and generate per-position quality profiles.
- Python: `SeqIO.parse()` with `record.letter_annotations['phred_quality']` (BioPython)
- CLI alternative: `pysam.FastxFile` (`.get_quality_array()` returns offset-removed Phred ints, but ALWAYS subtracts 33 - it cannot read Phred+64/Solexa correctly, so use it only on confirmed Phred+33 data; for legacy encodings stay on `SeqIO` with the explicit variant string)

## The Governing Principle: Never Guess the Offset

A FASTQ file does not record which quality encoding it uses. The same ASCII byte means different Phred scores under different encodings, and the offsets (33 vs 64) differ by exactly 31. Choosing the wrong format string has two failure modes:

- LOUD (safe): a quality character lies outside the chosen parser's legal range -> `ValueError` naming the wrong QualityIO parser. The run stops.
- SILENT (dangerous): every character lies in the ASCII overlap region legal for both encodings -> no error, and every score is off by exactly 31. Reading Phred+33 data as `fastq-illumina` makes all scores 31 too LOW; reading Phred+64 data as `fastq-sanger` makes them 31 too HIGH. QC, filtering, and trimming silently operate on garbage scores.

Auto-detection is provably ambiguous: ASCII >= 64 is legal in every variant, so a high-quality Sanger file (all Q >= 31) and a low-quality Illumina-1.3 file can be byte-identical in their quality lines. There is no reliable way to detect the encoding from content alone (Biopython docs: this "cannot be detected reliably automatically"). Determine the encoding from the sequencing instrument and run metadata, not by guessing. Scanning for the minimum ASCII byte can only RULE OUT encodings (see "Ruling Out Encodings" below), never confirm one.

## The Four FASTQ Encodings

| Variant | Score type | Offset | Format string | ASCII chars | Q range |
|---------|-----------|--------|---------------|-------------|---------|
| Sanger / Phred+33 | Phred | 33 | `'fastq'` / `'fastq-sanger'` | `!`(33)..`~`(126) | 0..93 |
| Solexa / Illumina 1.0 (Solexa+64) | Solexa odds | 64 | `'fastq-solexa'` | `;`(59)..`~`(126) | -5..62 |
| Illumina 1.3+ (Phred+64) | Phred | 64 | `'fastq-illumina'` | `@`(64)..`~`(126) | 0..62 |
| Illumina 1.5-1.7 (Phred+64, B-tail) | Phred | 64 | `'fastq-illumina'` | `B`(66)..`~`(126) | 2..62 |
| Illumina 1.8+ (Phred+33) | Phred | 33 | `'fastq'` / `'fastq-sanger'` | `!`(33)..~`J`(74) | 0..~41 |

Almost all data produced since 2011 is Phred+33 (`'fastq'`). Phred+64 and Solexa appear only in legacy datasets, but the cost of misreading them is silent corruption, so the encoding must be confirmed before parsing legacy files.

`'fastq'` is an alias for `'fastq-sanger'`; both are Phred+33. The wrong choice produces a LOUD `ValueError` only when an out-of-range character appears, and SILENT 31-shifted scores otherwise.

## Phred vs Solexa: Two Different Score Definitions

The Solexa encoding is not just a different offset; it uses a different score formula, which is why it needs a separate parser.

- Phred: Q = -10 * log10(P_error). Always >= 0.
- Solexa: Q = -10 * log10(P/(1 - P)) - an ODDS score. It goes NEGATIVE when P > 0.5 (floor -5), which is why Solexa quality strings include ASCII 59-63.

The two scales are asymptotically equal at high quality (rounded scores above ~Q10-13 are interchangeable) but diverge for poor-quality bases. The round trip Phred -> Solexa -> Phred is LOSSY in that low-quality region: Cock et al. (2010) note that Solexa scores 9 and 10 both map to Phred 10. Do not convert legacy Solexa data to Phred and back if the low-Q values matter.

## Accessing Quality Scores

Quality scores live in `record.letter_annotations['phred_quality']` as a list of ints. The attribute is `letter_annotations` (NOT `per_letter_annotations`, which does not exist). Solexa data parsed with `'fastq-solexa'` stores `record.letter_annotations['solexa_quality']` instead, and those values can be negative.

```python
from Bio import SeqIO

for record in SeqIO.parse('reads.fastq', 'fastq'):
    quals = record.letter_annotations['phred_quality']
    print(record.id, quals[:10])
```

`letter_annotations` is length-locked to `len(record.seq)`: assigning a list of the wrong length raises. To edit sequence and quality together, slice the record (slicing keeps qualities in sync) or build a fresh record.

| Phred Score | Error Probability | Accuracy |
|-------------|-------------------|----------|
| 10 | 1 in 10 | 90% |
| 20 | 1 in 100 | 99% |
| 30 | 1 in 1000 | 99.9% |
| 40 | 1 in 10000 | 99.99% |

## Code Patterns

### Calculate Average Quality per Read
```python
for record in SeqIO.parse('reads.fastq', 'fastq'):
    quals = record.letter_annotations['phred_quality']
    print(f'{record.id}: {sum(quals) / len(quals):.1f}')
```

### Filter Reads by Mean Quality
```python
def high_quality_reads(records, min_avg_qual=20):
    for record in records:
        quals = record.letter_annotations['phred_quality']
        if sum(quals) / len(quals) >= min_avg_qual:
            yield record

records = SeqIO.parse('reads.fastq', 'fastq')
SeqIO.write(high_quality_reads(records, 25), 'filtered.fastq', 'fastq')
```

### Filter by Minimum Quality at Any Position
```python
def all_bases_above(records, min_qual=20):
    for record in records:
        if min(record.letter_annotations['phred_quality']) >= min_qual:
            yield record
```

### Trim Low-Quality 3' End

**Goal:** Drop trailing bases below a quality cutoff while keeping qualities aligned to the trimmed sequence.

**Approach:** Walk inward from the 3' end to the first base that meets the cutoff, then slice the record; slicing a SeqRecord trims `letter_annotations` in step with the sequence.

**Reference (BioPython 1.83+):**
```python
def trim_low_quality(record, min_qual=20):
    quals = record.letter_annotations['phred_quality']
    trim_pos = len(quals)
    for i in range(len(quals) - 1, -1, -1):
        if quals[i] >= min_qual:
            trim_pos = i + 1
            break
    return record[:trim_pos]

records = SeqIO.parse('reads.fastq', 'fastq')
SeqIO.write((trim_low_quality(r) for r in records), 'trimmed.fastq', 'fastq')
```

### Sliding Window Quality Trim

**Goal:** Truncate a read at the first position where average quality in a sliding window drops below a threshold (the Trimmomatic SLIDINGWINDOW model).

**Approach:** Slide a fixed-size window across the quality list; when the window mean falls below the cutoff, slice the record at that position.

**Reference (BioPython 1.83+):**
```python
def sliding_window_trim(record, window_size=5, min_avg_qual=20):
    quals = record.letter_annotations['phred_quality']
    for i in range(len(quals) - window_size + 1):
        if sum(quals[i:i + window_size]) / window_size < min_avg_qual:
            return record[:i] if i > 0 else None
    return record
```

### Per-Position Quality Profile

**Goal:** Compute mean quality at each read position to spot systematic drops (typically 3' degradation).

**Approach:** Accumulate scores by position across reads, then average each position. NovaSeq binning (see below) makes per-position values cluster at a few discrete levels - expected, not a defect.

**Reference (BioPython 1.83+):**
```python
from collections import defaultdict

position_quals = defaultdict(list)
for record in SeqIO.parse('reads.fastq', 'fastq'):
    for i, q in enumerate(record.letter_annotations['phred_quality']):
        position_quals[i].append(q)

for pos in sorted(position_quals)[:20]:
    quals = position_quals[pos]
    print(f'Position {pos}: mean={sum(quals) / len(quals):.1f}')
```

### Count Reads by Quality Threshold
```python
thresholds = [20, 25, 30, 35]
counts = {t: 0 for t in thresholds}
for record in SeqIO.parse('reads.fastq', 'fastq'):
    avg = sum(record.letter_annotations['phred_quality']) / len(record.seq)
    for t in thresholds:
        if avg >= t:
            counts[t] += 1
```

## The Illumina 1.5-1.7 B-Tail

In Illumina 1.5-1.7 (Phred+64) data, Q0 and Q1 are reserved, and ASCII `B` (Q2) at the 3' end is a Read Segment Quality Control Indicator, NOT a real Q2 measurement. A run of trailing `B`s marks a region the instrument deemed unreliable. A trimmer that treats `B` as literal Q2 keeps those junk bases instead of removing them. When trimming legacy Phred+64 data, drop trailing `B`/Q2 runs as flags rather than scores.

## NovaSeq / NextSeq Quality Binning

Modern Illumina instruments quantize quality on-instrument (RTA software, baked into the BCL), so the binned values arrive in the FASTQ - they are not introduced downstream. NovaSeq 6000 (RTA3) emits only four values: Q2, Q12, Q23, Q37. NovaSeq X / X Plus (RTA4, XLEAP-SBS chemistry) uses a different, software-version-dependent bin set whose high bins shifted to roughly Q9/Q24/Q40 (the exact ranges depend on the Control/RTA software version), so its spike values differ from the 6000 - confirm them against the run's instrument and software version rather than assuming the 6000 set. Consequences:

- Per-base quality histograms collapse to spikes at the bin values. This is expected; it is not a data problem.
- Mean quality stays meaningful (each bin approximates the mean of its input range).
- GATK BQSR interacts with binning: with only four input levels, recalibration tables are coarse and corrections are blunter than on unbinned data.

## Converting Between Encodings

`SeqIO.convert` (or parse + write) re-encodes legacy data to standard Phred+33. Specify the SOURCE encoding explicitly; an out-of-range character raises, but overlap-region characters convert silently with the wrong offset if the source is mislabeled.

```python
from Bio import SeqIO

SeqIO.convert('old_illumina.fastq', 'fastq-illumina', 'standard.fastq', 'fastq')
SeqIO.convert('solexa.fastq', 'fastq-solexa', 'standard.fastq', 'fastq')
```

Per-score conversion helpers return floats:

```python
from Bio.SeqIO.QualityIO import phred_quality_from_solexa, solexa_quality_from_phred

phred_quality_from_solexa(10)   # Solexa -> Phred (float)
solexa_quality_from_phred(30)   # Phred -> Solexa (float)
```

Writing `'fastq-solexa'` from a Phred-only record forces a lossy on-the-fly conversion and emits a `BiopythonWarning` when `max(qualities) >= 62.5`. There is no clean Phred-to-Solexa write path that avoids the lossy step, so keep modern data in Phred+33.

## Ruling Out Encodings (Heuristic Only)

The minimum ASCII byte present can EXCLUDE encodings but cannot confirm one: an ASCII >= 64 file is consistent with all four variants. Use this only to narrow candidates, then confirm against instrument metadata.

```python
def candidate_encodings(filepath, sample_size=1000):
    '''Narrow FASTQ encoding candidates from the minimum quality byte. Confirm with run metadata.'''
    min_byte = 126
    count = 0
    with open(filepath) as handle:
        for i, line in enumerate(handle):
            if i % 4 == 3:
                for char in line.strip():
                    min_byte = min(min_byte, ord(char))
                count += 1
                if count >= sample_size:
                    break
    if min_byte < 59:
        return ['fastq']                        # only Phred+33 reaches below ASCII 59
    if min_byte < 64:
        return ['fastq-solexa']                 # ASCII 59-63 unique to Solexa+64
    return ['fastq', 'fastq-solexa', 'fastq-illumina']  # ambiguous - metadata decides
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ValueError: ... not in correct range (...right QualityIO parser?)` | Wrong format string; a char is out of the chosen parser's range | Use the encoding the instrument produced (`'fastq'`, `'fastq-illumina'`, or `'fastq-solexa'`) |
| Scores look uniformly ~31 too high or too low; QC silently off | Overlap-region 31-shift from a mislabeled offset | Confirm encoding from metadata; never guess. Phred+33 read as `fastq-illumina` is 31 low; Phred+64 read as `fastq-sanger` is 31 high |
| `AttributeError`/`KeyError` on `per_letter_annotations` | That attribute does not exist | Use `record.letter_annotations['phred_quality']` (or `['solexa_quality']` for Solexa) |
| `KeyError: 'phred_quality'` on Solexa data | Parsed with `'fastq-solexa'`, which stores `'solexa_quality'` | Read `['solexa_quality']`, or convert to Phred on write |
| Trailing `B`/Q2 bases survive trimming | Illumina 1.5-1.7 B-tail treated as real Q2 | Strip trailing `B` runs as QC flags, not scores |
| Quality histogram shows discrete spikes | NovaSeq 4-level binning (Q2/Q12/Q23/Q37) | Expected on binned instruments; not a data problem |

## References

Cock PJA, Fields CJ, Goto N, Heuer ML, Rice PM (2010). The Sanger FASTQ file format for sequences with quality scores, and the Solexa/Illumina FASTQ variants. Nucleic Acids Research 38(6):1767-1771.

Ewing B, Green P (1998). Base-calling of automated sequencer traces using phred. II. Error probabilities. Genome Research 8(3):186-194.

Ewing B, Hillier L, Wendl MC, Green P (1998). Base-calling of automated sequencer traces using phred. I. Accuracy assessment. Genome Research 8(3):175-185.

## Related Skills

- read-sequences - Parse FASTQ records and choose parse vs index for large files
- filter-sequences - Filter reads by length and content alongside quality
- paired-end-fastq - Keep R1/R2 synchronized when filtering paired reads
- sequence-statistics - Summary statistics across read sets
- read-qc/quality-reports - FastQC-style aggregate quality reports
- alignment-files/sam-bam-basics - Align filtered reads; quality scores carry into BAM
<!-- END FILE: sequence-io/fastq-quality/SKILL.md -->

## 子目录：sequence-io/filter-sequences

<!-- BEGIN FILE: sequence-io/filter-sequences/SKILL.md -->
---
name: bio-filter-sequences
description: Filter and select sequences by criteria (length, ID, GC content, N content, motifs, patterns, description) using Biopython, streaming so large files never load into RAM. Use when subsetting a FASTA/FASTQ file, removing unwanted or low-quality records, or selecting records by specific criteria. Use the paired-end-fastq skill instead whenever the input is paired R1/R2 reads.
tool_type: python
primary_tool: Bio.SeqIO
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Filter Sequences

**"Filter sequences by length, quality, or content"** -> Apply boolean criteria to a stream of sequence records and write survivors to output.
- Python: generator expression with `SeqIO.parse()` + `SeqIO.write()` (BioPython)
- CLI: `seqkit seq -m 200` (SeqKit) or `awk` on FASTA

Filter and select sequences based on length, ID, GC content, N content, motifs, regex patterns, and description.

## The governing principle

Two traps cause silent, downstream-corrupting errors. Neither raises an exception, so the agent must guard against both up front.

1. **Never filter one mate of a paired-end set independently.** Aligners (bwa, bowtie2) read R1 and R2 as two parallel streams and pair the i-th record of each, assuming SAME ORDER and SAME COUNT. Dropping a read from R1 alone DESYNCS the files: best case the aligner crashes on a name mismatch, worst case it silently pairs the wrong R1 with the wrong R2, producing mismapped reads and garbage insert sizes with no error. If the input is paired, route to the paired-end-fastq skill (synchronized filtering that writes matched output plus separate orphan/singleton files). Do NOT apply the single-file patterns below to one mate.
2. **Filter by STREAMING, not by loading.** `SeqIO.parse()` yields one record at a time; a generator expression into `SeqIO.write()` holds a single record in RAM regardless of file size. `list(SeqIO.parse(...))` materializes every record and OOMs on large FASTQ. Only the patterns that genuinely need all records at once (random sampling, splitting into multiple files) load the file; they say so explicitly.

## Required Imports

```python
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction
```

## Core Pattern

Stream records through a generator expression so memory stays flat:

```python
records = SeqIO.parse('input.fasta', 'fasta')
filtered = (rec for rec in records if len(rec.seq) >= 100)
SeqIO.write(filtered, 'output.fasta', 'fasta')
```

`SeqIO.write()` consumes the generator lazily and returns the count written.

## Filter by Length

### Minimum Length
```python
records = SeqIO.parse('input.fasta', 'fasta')
long_seqs = (rec for rec in records if len(rec.seq) >= 500)
SeqIO.write(long_seqs, 'long.fasta', 'fasta')
```

### Length Range
```python
records = SeqIO.parse('input.fasta', 'fasta')
sized = (rec for rec in records if 100 <= len(rec.seq) <= 1000)
SeqIO.write(sized, 'sized.fasta', 'fasta')
```

### Remove Short Sequences
```python
min_length = 200
records = SeqIO.parse('input.fasta', 'fasta')
filtered = (rec for rec in records if len(rec.seq) >= min_length)
count = SeqIO.write(filtered, 'filtered.fasta', 'fasta')
```

`len(rec.seq)` counts every base, including soft-masked lowercase (see Case Sensitivity below).

## Filter by ID

### Select Specific IDs
```python
wanted_ids = {'seq1', 'seq2', 'seq3'}
records = SeqIO.parse('input.fasta', 'fasta')
selected = (rec for rec in records if rec.id in wanted_ids)
SeqIO.write(selected, 'selected.fasta', 'fasta')
```

`rec.id` is the first whitespace-delimited token of the header. For CASAVA 1.8+ paired FASTQ, R1 and R2 share this id (the mate number lives after the space), so an id set matches both mates equally - another reason mate-aware filtering belongs in paired-end-fastq.

### Select from ID File

**Goal:** Extract sequences whose IDs appear in an external list file.

**Approach:** Load IDs into a set for O(1) lookup, then stream-filter and write matches.

**Reference (BioPython 1.83+):**
```python
with open('ids.txt') as f:
    wanted_ids = {line.strip() for line in f}

records = SeqIO.parse('input.fasta', 'fasta')
selected = (rec for rec in records if rec.id in wanted_ids)
SeqIO.write(selected, 'selected.fasta', 'fasta')
```

### Exclude Specific IDs
```python
exclude_ids = {'bad_seq1', 'bad_seq2'}
records = SeqIO.parse('input.fasta', 'fasta')
kept = (rec for rec in records if rec.id not in exclude_ids)
SeqIO.write(kept, 'kept.fasta', 'fasta')
```

### Filter by ID Pattern
```python
import re

pattern = re.compile(r'^chr\d+$')  # matches chr1, chr2, etc.
records = SeqIO.parse('input.fasta', 'fasta')
chromosomes = (rec for rec in records if pattern.match(rec.id))
SeqIO.write(chromosomes, 'chromosomes.fasta', 'fasta')
```

## Filter by GC Content

**Goal:** Keep records whose GC fraction falls in a target band.

**Approach:** Use `gc_fraction()`, which returns a FRACTION (0-1), NOT a percentage - thresholds must be 0.4, not 40. The `ambiguous=` mode decides how N and other IUPAC ambiguity codes are counted, and the same sequence yields a different GC value per mode, so set it explicitly rather than relying on the default.

**Reference (BioPython 1.83+):**
```python
from Bio.SeqUtils import gc_fraction

records = SeqIO.parse('input.fasta', 'fasta')
moderate_gc = (rec for rec in records if 0.4 <= gc_fraction(rec.seq, ambiguous='ignore') <= 0.6)
SeqIO.write(moderate_gc, 'moderate_gc.fasta', 'fasta')
```

### Choosing the ambiguous= mode

`gc_fraction(seq, ambiguous='remove')` is the default. For the same sequence the three modes give different answers - an N-containing read can pass or fail purely because of the mode:

| Mode | Denominator | `gc_fraction('GCGCNNNN')` | When to use |
|------|-------------|---------------------------|-------------|
| `'remove'` (default) | only unambiguous A,T,G,C,S,W,U | 1.0 | GC of the called bases only; ignores how many N's are present |
| `'ignore'` | full `len(seq)` (N's dilute GC) | 0.5 | GC over the whole read; matches a naive `(G+C)/len` |
| `'weighted'` | full length, ambiguous codes add expected GC | 0.75 | each IUPAC code contributes its mean GC (S=1.0, W=0.0, N=0.5, V/B=0.667, H/D=0.333) |

A naive `(G+C)/len` silently equals `'ignore'` mode and under-reports GC whenever N's are present. The default `'remove'` ignores N's entirely, so a heavily-N read can post a misleadingly extreme GC. Pick the mode that matches the intent and pass it explicitly.

### High / Low GC bands
```python
records = SeqIO.parse('input.fasta', 'fasta')
high_gc = (rec for rec in records if gc_fraction(rec.seq, ambiguous='ignore') >= 0.6)
SeqIO.write(high_gc, 'high_gc.fasta', 'fasta')
```

## Case Sensitivity (soft-masking)

`Seq` is CASE-PRESERVING: lowercase soft-masked bases (from RepeatMasker, Ensembl, dustmasker) survive parse and round-trip unchanged. Length, GC, motif, and regex filters are CASE-SENSITIVE - a naive uppercase test silently misses masked bases. Always `.upper()` the sequence before content matching when the masking should not affect the decision:

```python
seq_upper = str(rec.seq).upper()
has_site = 'GAATTC' in seq_upper            # matches gaattc and GAATTC
```

`gc_fraction()` itself is case-insensitive, but a hand-rolled `.count('G')` is not - count on the uppercased string.

## Filter by Sequence Content

### Remove Sequences with N's
```python
records = SeqIO.parse('input.fasta', 'fasta')
clean = (rec for rec in records if 'N' not in str(rec.seq).upper())
SeqIO.write(clean, 'clean.fasta', 'fasta')
```

### Limit N Content
```python
def n_fraction(seq):
    upper = str(seq).upper()
    return upper.count('N') / len(seq)

records = SeqIO.parse('input.fasta', 'fasta')
low_n = (rec for rec in records if n_fraction(rec.seq) < 0.05)  # under 5% ambiguous bases
SeqIO.write(low_n, 'low_n.fasta', 'fasta')
```

### Contains Specific Motif
```python
motif = 'GAATTC'  # EcoRI site
records = SeqIO.parse('input.fasta', 'fasta')
with_motif = (rec for rec in records if motif in str(rec.seq).upper())
SeqIO.write(with_motif, 'with_ecori.fasta', 'fasta')
```

### Regex Pattern in Sequence
```python
import re

pattern = re.compile(r'ATG.{30,100}T(AA|AG|GA)')  # ORF-like pattern
records = SeqIO.parse('input.fasta', 'fasta')
matches = (rec for rec in records if pattern.search(str(rec.seq).upper()))
SeqIO.write(matches, 'orf_like.fasta', 'fasta')
```

## Filter by Description

### Description Contains Keyword
```python
records = SeqIO.parse('input.fasta', 'fasta')
kinases = (rec for rec in records if 'kinase' in rec.description.lower())
SeqIO.write(kinases, 'kinases.fasta', 'fasta')
```

### Multiple Keywords (OR)
```python
keywords = ['kinase', 'phosphatase', 'transferase']
records = SeqIO.parse('input.fasta', 'fasta')
enzymes = (rec for rec in records if any(k in rec.description.lower() for k in keywords))
SeqIO.write(enzymes, 'enzymes.fasta', 'fasta')
```

## Combine Multiple Filters

**Goal:** Remove sequences that fail any of several length/content thresholds.

**Approach:** Define a predicate that checks all criteria against the uppercased sequence once, set the GC `ambiguous=` mode explicitly, apply the predicate as a generator filter, and stream survivors to output.

**Reference (BioPython 1.83+):**
```python
from Bio.SeqUtils import gc_fraction

def passes_filters(record):
    if len(record.seq) < 100:
        return False
    gc = gc_fraction(record.seq, ambiguous='ignore')
    if gc < 0.3 or gc > 0.7:
        return False
    if 'N' in str(record.seq).upper():
        return False
    return True

records = SeqIO.parse('input.fasta', 'fasta')
filtered = (rec for rec in records if passes_filters(rec))
SeqIO.write(filtered, 'filtered.fasta', 'fasta')
```

## Sample Sequences

### Random Sample (requires loading all)
```python
import random

records = list(SeqIO.parse('input.fasta', 'fasta'))  # loads file - needs all records up front
sample = random.sample(records, min(100, len(records)))
SeqIO.write(sample, 'sample.fasta', 'fasta')
```

### First N Sequences (streams)
```python
from itertools import islice

records = SeqIO.parse('input.fasta', 'fasta')
first_100 = islice(records, 100)
SeqIO.write(first_100, 'first100.fasta', 'fasta')
```

### Every Nth Sequence (streams)
```python
records = SeqIO.parse('input.fasta', 'fasta')
every_10th = (rec for i, rec in enumerate(records) if i % 10 == 0)
SeqIO.write(every_10th, 'sampled.fasta', 'fasta')
```

## Split by Criteria

### Split by Length

**Goal:** Partition sequences into separate files based on a length threshold.

**Approach:** Load all records once, partition with list comprehensions, and write each partition. Loading is acceptable here because both partitions are needed in a single pass; for very large files, run two streaming passes instead.

**Reference (BioPython 1.83+):**
```python
records = list(SeqIO.parse('input.fasta', 'fasta'))
short = [r for r in records if len(r.seq) < 500]
long = [r for r in records if len(r.seq) >= 500]
SeqIO.write(short, 'short.fasta', 'fasta')
SeqIO.write(long, 'long.fasta', 'fasta')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Downstream mismapping, wrong insert sizes, no error | Filtered one mate of a paired-end set independently, desyncing R1/R2 | Never filter one mate alone; use paired-end-fastq for synchronized filtering with orphan output |
| GC filter keeps/drops the wrong reads | `gc_fraction` returns a fraction 0-1 but threshold written as a percent (40 instead of 0.4) | Use 0-1 thresholds; multiply by 100 only for display |
| N-containing read unexpectedly passes or fails GC band | Wrong `ambiguous=` mode (default `'remove'` drops N's; `'ignore'` dilutes GC) | Set `ambiguous=` explicitly to match intent |
| Soft-masked read fails a motif/regex/uppercase test | `Seq` is case-preserving; lowercase masked bases do not match an uppercase pattern | `.upper()` the sequence before content matching |
| Generator yields nothing on second use | `SeqIO.parse()` is one-pass and exhausts silently | Re-create the generator, or `list()` it if it must be reused |
| MemoryError on large FASTQ | `list(SeqIO.parse(...))` materialized every record | Use a generator expression; only load for sampling/splitting |
| Empty output file | Filter too strict, or matched against the wrong case/field | Loosen thresholds; confirm id vs description and case |

## Related Skills

- read-sequences - Parse sequences before filtering
- write-sequences - Write filtered sequences to output
- fastq-quality - Filter FASTQ by per-base quality scores and encoding
- paired-end-fastq - Synchronized filtering of R1/R2 with orphan handling
- sequence-manipulation/sequence-properties - Per-sequence GC, length, and composition
- sequence-manipulation/motif-search - Filter by complex motif patterns
- alignment-files/alignment-filtering - Filter aligned reads with samtools view -f/-F
<!-- END FILE: sequence-io/filter-sequences/SKILL.md -->

## 子目录：sequence-io/format-conversion

<!-- BEGIN FILE: sequence-io/format-conversion/SKILL.md -->
---
name: bio-format-conversion
description: Convert between sequence file formats (FASTA, FASTQ, GenBank, EMBL, Stockholm) and re-encode FASTQ quality offsets using Biopython Bio.SeqIO. Use when changing a file format for a downstream tool, fixing FASTQ quality encoding (Phred+33 vs Phred+64 vs Solexa), or when a conversion risks silently dropping annotations or quality scores.
tool_type: python
primary_tool: Bio.SeqIO
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Format Conversion

**"Convert this file to a different format"** -> Read records in one format, optionally add or drop annotations, and write in the target format.
- Python: `SeqIO.convert()` for a streaming one-shot conversion, or `SeqIO.parse()` + `SeqIO.write()` when records need modification (BioPython)
- CLI: `seqkit seq` (SeqKit) for FASTA/FASTQ; `samtools view` for SAM/BAM/CRAM

## The Governing Principle

A conversion is lossy whenever the target format cannot represent the source's information. The conversion still succeeds with no error and no warning. FASTA stores only id + description + sequence, so it is the most lossy common target: converting GenBank, EMBL, or FASTQ to FASTA silently discards everything the richer format carried. Before converting, decide whether the destination can hold what the source contains. If it cannot, treat the conversion as a deliberate downgrade, not a neutral reformat.

## The Canonical Trap: GenBank/EMBL -> FASTA Silently Drops Everything

`SeqIO.convert('in.gb', 'genbank', 'out.fasta', 'fasta')` discards all features, annotations, qualifiers, and dbxrefs. The genes, CDS coordinates, `/product` and `/gene` qualifiers, organism, taxonomy, references, and molecule_type are all gone. There is no error, no warning, and the record count is unchanged, so the loss is invisible unless the output is inspected. FASTA encodes only `record.id`, `record.description`, and `record.seq`; everything in `record.features`, `record.annotations`, and `record.dbxrefs` has nowhere to go.

If the features matter, do not convert to FASTA. Extract feature sequences first (see sequence-manipulation/sequence-slicing) or keep the GenBank file as the source of record and use the FASTA only as a sequence-only derivative for tools that demand FASTA.

## Lossy Conversion Decision Table

| From | To | What is lost (silently) |
|------|-----|-------------------------|
| GenBank / EMBL | FASTA | All features, qualifiers, annotations, dbxrefs; keeps id + description + seq |
| GenBank | EMBL (or reverse) | Usually lossless; both hold features and annotations |
| FASTQ | FASTA | Per-base quality scores (`phred_quality`) |
| FASTQ Phred+64 | FASTQ Phred+33 | Nothing if offsets handled correctly; corruption if the wrong parser is used |
| FASTQ Phred | FASTQ Solexa | Precision at low quality (round-trip lossy below ~Q10); warns when max Solexa exceeded |
| Stockholm | FASTA | Alignment columns (gaps), consensus, per-column annotation; keeps ungapped seqs |
| Any rich format | FASTA | Everything except id + description + seq |

The general pattern: rich -> flat loses the richness. The conversion succeeds regardless.

## Preferred Path: SeqIO.convert() Is a Streaming One-Shot

For a plain conversion with no record modification, use `SeqIO.convert()`. It streams one record at a time from input to output (memory-efficient, never loads the whole file) and is preferred over `parse()` + `write()`, which is only needed when records must be changed en route.

```python
from Bio import SeqIO

count = SeqIO.convert('input.gb', 'genbank', 'output.fasta', 'fasta')
print(f'Converted {count} records')
```

Parameters: `in_file`, `in_format`, `out_file`, `out_format` (filenames or handles; format strings are lowercase). Returns the number of records written. Reach for `parse()` + `write()` only when injecting annotations, transforming sequences, or filtering during the conversion.

## FASTQ Quality Encoding Conversion

FASTQ quality is one ASCII character per base, but the offset and score type differ across instrument generations. Re-encoding between them is a conversion, not a copy: the bytes in the quality line change.

| Format string | For | Offset | Score type |
|---------------|-----|--------|-----------|
| `fastq` (alias of `fastq-sanger`) | Sanger and modern Illumina 1.8+ | 33 | Phred 0-93 |
| `fastq-sanger` | same as above | 33 | Phred 0-93 |
| `fastq-illumina` | Illumina 1.3-1.7 | 64 | Phred 0-62 |
| `fastq-solexa` | pre-1.3 Solexa | 64 | Solexa odds -5..62 |

Re-encode old Illumina 1.3+ (Phred+64) to modern Sanger (Phred+33) by naming both variants. `SeqIO.convert()` reads with the input offset and writes with the output offset:

```python
from Bio import SeqIO

SeqIO.convert('illumina13.fastq', 'fastq-illumina', 'sanger.fastq', 'fastq-sanger')
```

**Never re-encode without a verified source encoding.** Quality encoding cannot be auto-detected in general: ASCII >= 64 is legal in every variant, so a high-quality Sanger file and a low-quality Illumina-1.3 file can be byte-identical in their quality lines. Two failure modes follow from guessing wrong:
- Loud and safe: a character outside the chosen parser's range raises `ValueError` noting the quality string is not in the correct range for the chosen QualityIO parser.
- Silent and dangerous: if every quality char falls in the overlap valid for both encodings, no error fires and every score comes out off by exactly 31 (the 64 - 33 offset gap). QC is then silently garbage.

Confirm the encoding from the sequencing pipeline (or FastQC's inferred encoding) before re-encoding; do not let the agent guess the offset.

**Solexa is doubly lossy.** Solexa uses an odds score, Q = -10 log10(P/(1-P)), not Phred's Q = -10 log10(P), which is why Solexa scores go negative. Phred <-> Solexa conversions round a float to one ASCII char per base, so the round trip is many-to-one and lossy below ~Q10 (for example Solexa 9 and 10 both map to Phred 10). Writing `fastq-solexa` from a Phred-only record forces an on-the-fly lossy conversion and emits a `BiopythonWarning` when `max(qualities) >= 62.5`. There is no clean Phred -> Solexa path that avoids the loss; only re-encode toward Solexa when a legacy tool truly requires it.

## Conversions That Require Adding Data

FASTA has no molecule_type and no quality, so converting FASTA up to a richer format means supplying what FASTA lacked. Stream records through a generator that injects the missing field.

### FASTA to GenBank (requires molecule_type)

**Goal:** Convert FASTA to GenBank, which the writer refuses to produce without `molecule_type`.

**Approach:** Stream records through a generator that sets `record.annotations['molecule_type']`, then write as GenBank.

**Reference (BioPython 1.83+):**
```python
from Bio import SeqIO

def add_molecule_type(records, mol_type='DNA'):
    for record in records:
        record.annotations['molecule_type'] = mol_type
        yield record

records = SeqIO.parse('input.fasta', 'fasta')
SeqIO.write(add_molecule_type(records), 'output.gb', 'genbank')
```

### FASTA to FASTQ (requires quality scores)

**Goal:** Convert FASTA to FASTQ by assigning placeholder per-base quality.

**Approach:** Stream records through a generator that adds a `phred_quality` list of the right length, then write as FASTQ.

**Reference (BioPython 1.83+):**
```python
from Bio import SeqIO

def add_quality(records, quality=40):
    for record in records:
        record.letter_annotations['phred_quality'] = [quality] * len(record.seq)
        yield record

records = SeqIO.parse('input.fasta', 'fasta')
SeqIO.write(add_quality(records), 'output.fastq', 'fastq')
```

Placeholder quality is fabricated, not measured: downstream QC and variant callers will treat it as real. Use it only to satisfy a tool's format requirement, never to imply the bases were measured at that quality. `letter_annotations` is length-locked to the sequence, so the list length must equal `len(record.seq)`.

## Batch Convert a Directory

**Goal:** Convert every file of one format in a directory to another format.

**Approach:** Glob the input files, apply `SeqIO.convert()` to each, and report per-file counts.

**Reference (BioPython 1.83+):**
```python
from pathlib import Path
from Bio import SeqIO

for gb_file in Path('.').glob('*.gb'):
    fasta_file = gb_file.with_suffix('.fasta')
    count = SeqIO.convert(str(gb_file), 'genbank', str(fasta_file), 'fasta')
    print(f'{gb_file.name}: {count} records')
```

## Convert With Sequence Modification

When the conversion must also transform sequences, parse and write explicitly rather than using `convert()`.

```python
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

def uppercase_record(rec):
    return SeqRecord(rec.seq.upper(), id=rec.id, description=rec.description)

records = SeqIO.parse('input.fasta', 'fasta')
SeqIO.write((uppercase_record(rec) for rec in records), 'output.fasta', 'fasta')
```

`Seq` is case-preserving, so lowercase soft-masking survives a plain conversion; call `.upper()` explicitly only when the destination tool requires uppercase.

## Alignment Format Conversion

Sequence formats drop gaps and alignment columns. To convert between alignment formats (Stockholm, PHYLIP, Clustal, FASTA-alignment) keeping the columns, use `AlignIO`, not `SeqIO`.

```python
from Bio import AlignIO

AlignIO.convert('alignment.sto', 'stockholm', 'alignment.phy', 'phylip')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| GenBank features missing after conversion | Target was FASTA, which cannot hold features | Expected and silent; keep the GenBank as source, or extract features before converting |
| `ValueError` about missing molecule_type | Writing GenBank/EMBL from records that lack it (e.g. from FASTA) | Set `record.annotations['molecule_type']` before writing |
| `ValueError` about quality scores | Writing FASTQ from records with no `phred_quality` | Add `phred_quality` to `letter_annotations` (length must equal the sequence) |
| `ValueError` mentioning the QualityIO parser | A quality char is outside the named parser's range (wrong FASTQ variant) | Use the correct variant: `fastq-sanger`, `fastq-illumina`, or `fastq-solexa` |
| FASTQ scores all off by 31 with no error | Read Phred+33 as `fastq-illumina` or Phred+64 as `fastq-sanger` (overlap region) | Confirm the true encoding from the pipeline; re-read with the right variant |
| `BiopythonWarning` "Data loss - max Solexa quality" | Writing `fastq-solexa` from Phred scores above ~62 | Expected lossy conversion; only write Solexa when a legacy tool requires it |
| Alignment columns/gaps lost | Used `SeqIO` on an alignment | Use `AlignIO.convert()` to preserve columns |

## Related Skills

- read-sequences - Parse sequences and choose parse vs index for the input
- write-sequences - Write converted sequences with modifications
- fastq-quality - Phred/Solexa/Illumina encoding details and quality handling
- batch-processing - Convert many files across a directory
- compressed-files - Handle gzip/BGZF input and output during conversion
- sequence-manipulation/sequence-slicing - Extract feature sequences before downgrading to FASTA
- alignment-files/sam-bam-basics - For SAM/BAM/CRAM conversion, use samtools view
<!-- END FILE: sequence-io/format-conversion/SKILL.md -->

## 子目录：sequence-io/paired-end-fastq

<!-- BEGIN FILE: sequence-io/paired-end-fastq/SKILL.md -->
---
name: bio-paired-end-fastq
description: Handle paired-end FASTQ files (R1/R2) using Biopython while keeping mates synchronized. Use when working with Illumina paired reads, synchronizing pairs, filtering both mates together with orphan routing, interleaving/deinterleaving, or matching mates by read name.
tool_type: python
primary_tool: Bio.SeqIO
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Paired-End FASTQ

**"Work with my paired-end FASTQ files"** -> Iterate R1/R2 pairs in sync, filter both mates together (routing orphans out), interleave/deinterleave files, and match mates by read name.
- Python: `SeqIO.parse()` with `zip()` iteration (BioPython)

## The Governing Principle: R1 and R2 Are Parallel Streams

Aligners (bwa mem, bowtie2, STAR) consume R1 and R2 as two parallel streams and pair the i-th record of each file: same order, same count. They assume the k-th read in R1 is the mate of the k-th read in R2.

This makes independent per-mate processing the #1 paired-end correctness trap. Filtering or trimming ONE mate without the other DESYNCS the files:
- Best case: the aligner detects a read-name mismatch and crashes loudly.
- Worst case: it silently pairs the wrong R1 with the wrong R2 -> mismapping, corrupt insert sizes, no error at all.

Governing rule: never filter, trim, sort, or subsample one mate independently. Process both mates as a unit. When a read fails but its mate passes, route the survivor to a separate singleton/orphan file rather than leaving a gap that desyncs the stream. Proper paired trimmers (Trimmomatic PE, fastp, cutadapt `-p`) do exactly this: synchronized paired output plus separate orphan files.

## Required Import

```python
from Bio import SeqIO
```

## Read-Name Conventions: How Mates Are Matched

Two distinct naming layers exist. File naming (which file is R1 vs R2) is separate from read naming (how a tool decides two records are mates).

### File naming patterns
- `sample_R1.fastq` / `sample_R2.fastq`
- `sample_1.fastq` / `sample_2.fastq`
- `sample_R1_001.fastq` / `sample_R2_001.fastq` (Illumina bcl2fastq)
- `sample.R1.fastq.gz` / `sample.R2.fastq.gz`

### Read naming: mate matched by shared ID up to the first whitespace

| Era | Mate marker | Example | How mates match |
|-----|-------------|---------|-----------------|
| Pre-CASAVA 1.8 | SUFFIX `/1`, `/2` on the read name | `@HWUSI-EAS100R:6:73:941:1973#0/1` | Strip the trailing `/1`/`/2`; the rest is the shared ID |
| CASAVA 1.8+ | SECOND field after a SPACE | `@EAS139:136:FC706VJ:2:2104:15343:197393 1:Y:18:ATCACG` | The text before the space is IDENTICAL for both mates; the `1:`/`2:` lives only after the space |

In CASAVA 1.8+ the second field is `<read>:<is_filtered>:<control>:<index>` -> `read`=1 or 2 (mate number), `is_filtered`=Y (failed chastity) or N, `control`=0 normally, `index`=barcode.

Most tools (and Biopython) take the read ID as everything up to the first whitespace. Biopython puts that token in `record.id` and the full header line in `record.description`. So for 1.8+ data, `r1.id == r2.id` directly; the `1:`/`2:` distinction is only visible in `record.description`. For pre-1.8 data, strip the `/1`/`/2` suffix before comparing.

A normalizer that handles both eras:

```python
def mate_key(record):
    return record.id.rsplit('/', 1)[0]
```

`record.id` already excludes anything after the first space, so this single rsplit covers both the space-format (1.8+) and the slash-suffix (pre-1.8) conventions.

## Iterate Pairs Together

### Basic Paired Iteration
```python
r1_records = SeqIO.parse('reads_R1.fastq', 'fastq')
r2_records = SeqIO.parse('reads_R2.fastq', 'fastq')

for r1, r2 in zip(r1_records, r2_records):
    print(f'R1: {r1.id}, R2: {r2.id}')
    print(f'Lengths: {len(r1.seq)}, {len(r2.seq)}')
```

`zip` stops at the shorter iterator. If R1 has 1000 reads and R2 has 998, `zip` silently processes 998 and drops the tail with no warning. Verify counts match (see Paired Statistics) before trusting a `zip` loop on files of unknown provenance.

### Verify Pair Matching
```python
def iterate_pairs(r1_file, r2_file, format='fastq'):
    r1_records = SeqIO.parse(r1_file, format)
    r2_records = SeqIO.parse(r2_file, format)

    for r1, r2 in zip(r1_records, r2_records):
        if mate_key(r1) != mate_key(r2):
            raise ValueError(f'Pair mismatch: {r1.id} vs {r2.id}')
        yield r1, r2

for r1, r2 in iterate_pairs('reads_R1.fastq', 'reads_R2.fastq'):
    process_pair(r1, r2)
```

## Filter Pairs Together (Synchronized, With Orphan Routing)

**Goal:** Quality-filter paired reads so that R1 and R2 stay in lockstep, and reads whose mate was discarded are routed to orphan files instead of silently desyncing the stream.

**Approach:** Stream both files together with `zip`. Evaluate both mates. If both pass, write to the paired outputs. If exactly one passes, write the survivor to its orphan file. This mirrors the four-output behavior of Trimmomatic PE (paired R1, paired R2, orphan R1, orphan R2).

**Reference (BioPython 1.83+):**
```python
def filter_pairs_synced(r1_in, r2_in, r1_out, r2_out, r1_orphan, r2_orphan, min_qual=25):
    '''Keep a pair only if both mates pass; route lone survivors to orphan files.'''
    r1_records = SeqIO.parse(r1_in, 'fastq')
    r2_records = SeqIO.parse(r2_in, 'fastq')

    counts = {'paired': 0, 'r1_orphan': 0, 'r2_orphan': 0}
    with open(r1_out, 'w') as p1, open(r2_out, 'w') as p2, \
         open(r1_orphan, 'w') as o1, open(r2_orphan, 'w') as o2:
        for r1, r2 in zip(r1_records, r2_records):
            r1_ok = sum(r1.letter_annotations['phred_quality']) / len(r1.seq) >= min_qual
            r2_ok = sum(r2.letter_annotations['phred_quality']) / len(r2.seq) >= min_qual
            if r1_ok and r2_ok:
                SeqIO.write(r1, p1, 'fastq')
                SeqIO.write(r2, p2, 'fastq')
                counts['paired'] += 1
            elif r1_ok:
                SeqIO.write(r1, o1, 'fastq')
                counts['r1_orphan'] += 1
            elif r2_ok:
                SeqIO.write(r2, o2, 'fastq')
                counts['r2_orphan'] += 1
    return counts
```

The paired outputs stay synchronized because every pass-both write goes to BOTH files in the same iteration. Mean quality is one criterion; swap the test for a length threshold, adapter check, or any predicate, but always apply it to both mates and route orphans the same way. `min_qual=25` is a common Q-score cutoff (Phred 25 ~= 0.3% error); tune per experiment.

## Interleave Pairs

Interleaved FASTQ holds both mates in one file alternating R1, R2, R1, R2 (record 2k = forward, 2k+1 = reverse). `bwa mem -p` reads this format. The strict alternation IS the pairing, so a single mate-less read shifts every downstream record by one and desyncs everything. Only interleave files that are known to be synchronized, and pull orphans out first.

### Create Interleaved File

**Goal:** Merge synchronized R1/R2 files into one interleaved file.

**Approach:** Zip both iterators and yield alternating records through a generator so nothing is materialized in memory.

**Reference (BioPython 1.83+):**
```python
def interleave_pairs(r1_file, r2_file, output_file, format='fastq'):
    r1_records = SeqIO.parse(r1_file, format)
    r2_records = SeqIO.parse(r2_file, format)

    def interleaved():
        for r1, r2 in zip(r1_records, r2_records):
            yield r1
            yield r2

    count = SeqIO.write(interleaved(), output_file, format)
    return count // 2  # Number of pairs

pairs = interleave_pairs('reads_R1.fastq', 'reads_R2.fastq', 'reads_interleaved.fastq')
```

## Deinterleave

### Split Interleaved to Paired Files

**Goal:** Recover separate R1/R2 files from an interleaved file, streaming to avoid loading everything.

**Approach:** Parse once; route even-indexed records to R1, odd-indexed to R2.

**Reference (BioPython 1.83+):**
```python
def deinterleave_streaming(interleaved_file, r1_file, r2_file, format='fastq'):
    records = SeqIO.parse(interleaved_file, format)

    pairs = 0
    with open(r1_file, 'w') as r1_h, open(r2_file, 'w') as r2_h:
        for i, record in enumerate(records):
            if i % 2 == 0:
                SeqIO.write(record, r1_h, format)
            else:
                SeqIO.write(record, r2_h, format)
                pairs += 1
    return pairs
```

Even/odd splitting only stays correct if the interleaved file has perfect alternation. If an upstream per-read filter left an orphan in the file, every record after it lands in the wrong output. Guard by checking `mate_key` equality between each even/odd pair after splitting, or deinterleave with a name check.

## Paired Statistics

### Count and Verify Pairs
```python
def paired_stats(r1_file, r2_file):
    r1_count = sum(1 for _ in SeqIO.parse(r1_file, 'fastq'))
    r2_count = sum(1 for _ in SeqIO.parse(r2_file, 'fastq'))

    if r1_count != r2_count:
        print(f'WARNING: Unequal counts! R1={r1_count}, R2={r2_count} -> files are desynced')
    else:
        print(f'Pairs: {r1_count}, total reads: {r1_count * 2}')
    return r1_count, r2_count
```

### Paired Quality Summary
```python
def paired_quality_summary(r1_file, r2_file):
    r1_quals, r2_quals = [], []
    for r1, r2 in zip(SeqIO.parse(r1_file, 'fastq'), SeqIO.parse(r2_file, 'fastq')):
        r1_quals.append(sum(r1.letter_annotations['phred_quality']) / len(r1.seq))
        r2_quals.append(sum(r2.letter_annotations['phred_quality']) / len(r2.seq))
    print(f'R1 mean quality: {sum(r1_quals)/len(r1_quals):.1f}')
    print(f'R2 mean quality: {sum(r2_quals)/len(r2_quals):.1f}')
```

R2 commonly shows lower mean quality than R1 (the reverse read is sequenced later in the run); a modest R1/R2 gap is expected, not a defect.

## Find Paired Files

### Auto-Detect R2 from R1
```python
from pathlib import Path

def find_r2(r1_path):
    r1_path = Path(r1_path)
    name = r1_path.name
    patterns = [('_R1', '_R2'), ('_R1_', '_R2_'), ('.R1.', '.R2.'), ('_1', '_2')]

    for p1, p2 in patterns:
        if p1 in name:
            r2_path = r1_path.parent / name.replace(p1, p2, 1)
            if r2_path.exists():
                return r2_path
    return None
```

Order matters: test the specific `_R1` patterns before the bare `_1`, otherwise `sample_R1.fastq` would match `_1` and produce `sample_R2.fastq` only by luck. `replace(..., 1)` replaces the first occurrence only, so a sample named `sample_R1_lane_R1.fastq` swaps just the first token.

## Compressed Paired Files
```python
import gzip

def iterate_gzipped_pairs(r1_gz, r2_gz):
    with gzip.open(r1_gz, 'rt') as r1_h, gzip.open(r2_gz, 'rt') as r2_h:
        for r1, r2 in zip(SeqIO.parse(r1_h, 'fastq'), SeqIO.parse(r2_h, 'fastq')):
            yield r1, r2
```

Use text mode `'rt'`, not `'rb'`, when handing a gzip handle to `SeqIO.parse`; the parser expects decoded text.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Aligner reports "mismatched read names" or "unpaired reads" | R1 and R2 desynced by filtering/trimming one mate independently | Always filter both mates together; route orphans to separate files (see synchronized filter) |
| Silent mismapping, nonsensical insert sizes, no error | A per-mate operation dropped reads from one file -> i-th records no longer mates | Re-pair from source; never trust outputs from independent per-mate filtering |
| Mates never recognized as pairs | Mixing pre-1.8 `/1` `/2` data with 1.8+ space-format ids, or comparing full descriptions instead of the pre-space ID | Match on `mate_key` (ID up to first space, `/1`/`/2` stripped), not the whole header |
| Deinterleave produces shifted/wrong pairs | An orphan in the interleaved file broke the strict R1,R2 alternation | Remove orphans before interleaving; verify each even/odd pair with `mate_key` after splitting |
| `zip` loop processes fewer reads than expected | R1 and R2 have unequal counts; `zip` stops at the shorter and silently drops the tail | Run `paired_stats` first; counts must be equal |
| Memory error on large files | `list(SeqIO.parse(...))` materializes every record | Stream with generators; for random access use `SeqIO.index`/`index_db` |

## Related Skills

- read-sequences - Parse individual FASTQ files and choose parse vs index
- fastq-quality - Phred encoding and quality interpretation before paired filtering
- filter-sequences - Single-file filtering criteria (apply to both mates here)
- compressed-files - gzip vs BGZF handling for paired files
- read-qc/quality-reports - FastQC/MultiQC per-mate quality assessment
- alignment-files/sam-bam-basics - After filtering, align paired reads with bwa mem; proper pairs in BAM
<!-- END FILE: sequence-io/paired-end-fastq/SKILL.md -->

## 子目录：sequence-io/read-sequences

<!-- BEGIN FILE: sequence-io/read-sequences/SKILL.md -->
---
name: bio-read-sequences
description: Read biological sequence files (FASTA, FASTQ, GenBank, EMBL, ABI, SFF) with Biopython Bio.SeqIO, choosing between streaming, in-memory, and on-disk-indexed access. Use when parsing sequence files, iterating multi-record files, randomly accessing records by ID in large files, or maximizing parse throughput.
tool_type: python
primary_tool: Bio.SeqIO
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Read Sequences

Read biological sequence data from files using Biopython's Bio.SeqIO module.

**"Read sequences from a file"** -> Parse a file into SeqRecord objects exposing id, sequence, and annotations.
- Python: `SeqIO.parse()` / `SeqIO.read()` (BioPython)
- R: `readDNAStringSet()` / `readAAStringSet()` (Biostrings)

## The Governing Principle

Stream by default. `SeqIO.parse()` yields one record at a time and never holds the whole file in RAM, so it scales to any size. Reach for an in-memory or indexed structure only when the access pattern demands it: load all records (`to_dict`) only for small files needing random access; build an index (`index` / `index_db`) for random access into large files. Never `list()` a huge file or `to_dict()` it - that defeats streaming and can exhaust memory.

## Which Function to Use

| Method | Returns | Memory model | Random access | Persists | Multi-file |
|--------|---------|--------------|---------------|----------|------------|
| `parse(handle, format)` | generator of SeqRecord | one record at a time | no | no | no |
| `read(handle, format)` | one SeqRecord | one record | n/a | no | no |
| `to_dict(records)` | real `dict` | ALL records in RAM | yes | no | feed combined iterators |
| `index(filename, format)` | dict-like (read-only) | byte offsets only, re-parses on access | yes | no | no |
| `index_db(idx_file, files, format)` | dict-like (read-only) | on-disk SQLite index | yes | yes | yes |

Decision rule: `parse` for streaming; `read` for a known single-record file; `to_dict` when the file is small and random access by ID is needed; `index` for random access into one large file; `index_db` for files larger than RAM, many files indexed together, or an index reused across runs.

Behavioral traps these methods hide:
- `parse()` is a one-pass generator. It is NOT subscriptable (`parse(...)[3]` raises TypeError), and it EXHAUSTS SILENTLY: a second `for` loop over the same generator object yields nothing with no error. Re-call `parse()` for each pass, or `list()` it once if the file is small.
- `read()` fails LOUDLY: zero records raise `ValueError: No records found in handle`; more than one raises `ValueError: More than one record found in handle`. Use it as an assertion that the file holds exactly one sequence.
- `to_dict()`, `index()`, and `index_db()` all raise `ValueError` on a DUPLICATE id (`Duplicate key '...'`). Supply a `key_function` to derive unique keys when ids collide.
- `index()` needs a FILENAME, not a handle (it must seek). It stores only byte offsets and re-parses the record from disk on every access, so it returns a fresh object each time and mutations do not persist. It is read-only (`__setitem__` raises NotImplementedError).
- `index_db()` stores the offset index in an on-disk SQLite file. It PERSISTS across sessions (reopen later with just the index filename), and scales beyond RAM and across multiple files (pass a list of filenames). This is the right answer for data larger than memory.

The `alphabet=` argument still appears in some signatures for back-compatibility but is a no-op since BioPython 1.78; leave it `None`.

## Required Import

```python
from Bio import SeqIO
```

## Reading Records

### SeqIO.parse() - Stream Multiple Records
Returns a one-pass iterator of SeqRecord objects. Always pass the format explicitly as the second argument.

```python
for record in SeqIO.parse('sequences.fasta', 'fasta'):
    print(record.id, len(record.seq))
```

### SeqIO.read() - Exactly One Record
Use when the file must contain a single sequence; raises on zero or multiple records.

```python
record = SeqIO.read('single.fasta', 'fasta')
```

## Random Access

### SeqIO.to_dict() - Small Files
Loads every record into a dictionary keyed by id. Fast random access, but holds all records in RAM.

```python
records = SeqIO.to_dict(SeqIO.parse('sequences.fasta', 'fasta'))
seq = records['sequence_id'].seq
```

### SeqIO.index() - One Large File

**Goal:** Random access by id into a large file without loading every record into memory.

**Approach:** Build an in-memory map of byte offsets keyed by id; each lookup re-parses one record from disk.

**Reference (BioPython 1.83+):**
```python
records = SeqIO.index('large.fasta', 'fasta')
seq = records['sequence_id'].seq
records.close()
```

A `key_function` maps the id STRING to a custom key (note: `to_dict`'s key_function receives the whole record instead):
```python
def get_accession(identifier):
    return identifier.split('.')[0]  # drop the version suffix

records = SeqIO.index('sequences.fasta', 'fasta', key_function=get_accession)
```

### SeqIO.index_db() - Huge / Multiple Files

**Goal:** Random access into data larger than RAM, or across many files, with the index reusable across runs.

**Approach:** Persist the offset index in an on-disk SQLite database; reopen it later without re-parsing.

**Reference (BioPython 1.83+):**
```python
# First call parses the file(s) and builds the SQLite index
records = SeqIO.index_db('index.sqlite', 'large.fasta', 'fasta')
seq = records['sequence_id'].seq
records.close()

# Later sessions reopen instantly with just the index filename
records = SeqIO.index_db('index.sqlite')

# Index multiple files as one database
records = SeqIO.index_db('combined.sqlite', ['file1.fasta', 'file2.fasta'], 'fasta')
```

## High-Performance Parsing

For maximum throughput on large files, low-level parsers (SimpleFastaParser, FastqGeneralIterator) yield raw tuples and skip SeqRecord construction, so they run substantially faster than SeqIO.parse.

### SimpleFastaParser

**Goal:** Parse large FASTA files at maximum speed without SeqRecord overhead.

**Approach:** Iterate `(title, sequence)` string tuples directly from the handle.

**Reference (BioPython 1.83+):**
```python
from Bio.SeqIO.FastaIO import SimpleFastaParser

with open('large.fasta') as handle:
    for title, sequence in SimpleFastaParser(handle):
        if len(sequence) > 1000:
            seq_id = title.split()[0]  # first whitespace token is the id
```

### FastqGeneralIterator

**Goal:** Parse large FASTQ files at maximum speed.

**Approach:** Iterate `(title, sequence, quality_string)` string tuples; decode quality manually if needed.

**Reference (BioPython 1.83+):**
```python
from Bio.SeqIO.QualityIO import FastqGeneralIterator

with open('reads.fastq') as handle:
    for title, sequence, quality in FastqGeneralIterator(handle):
        avg_qual = sum(ord(c) - 33 for c in quality) / len(quality)  # Phred+33
```

## SeqRecord Attributes

After parsing, each record exposes:

```python
record.id          # first whitespace token of the header (string)
record.name        # same first token (for FASTA, name == id)
record.description # the ENTIRE header after '>', including the id token
record.seq         # sequence data (Seq object; case-preserving)
record.features    # list of SeqFeature objects (GenBank/EMBL)
record.annotations # dict of annotations (organism, molecule_type, ...)
record.letter_annotations  # per-letter dict (e.g. 'phred_quality' list)
record.dbxrefs     # database cross-references
```

### id vs name vs description - the first-space split
A FASTA header `>FIRST rest of the line` parses to: `id` = `FIRST` (the first whitespace token), `name` = `FIRST` (same token), `description` = `FIRST rest of the line` (the WHOLE header after `>`, including the id). So `>seq1 some desc` gives id `seq1`, name `seq1`, description `seq1 some desc`. The id is therefore the leading word of the description, not a separate field - relevant when writing records back out.

## Common Formats

| Format | String | Typical Extension | Notes |
|--------|--------|-------------------|-------|
| FASTA | `'fasta'` | .fasta, .fa, .fna, .faa | Most common |
| FASTA 2-line | `'fasta-2line'` | .fasta | One line per sequence (no wrapping) |
| FASTQ | `'fastq'` | .fastq, .fq | Alias of fastq-sanger (Phred+33) |
| FASTQ Solexa | `'fastq-solexa'` | .fastq | Old Solexa (Solexa+64, scores -5..62) |
| FASTQ Illumina | `'fastq-illumina'` | .fastq | Illumina 1.3-1.7 (Phred+64) |
| GenBank | `'genbank'` or `'gb'` | .gb, .gbk | With features/annotations |
| EMBL | `'embl'` | .embl | European format with features |
| Swiss-Prot | `'swiss'` | .dat | UniProt format |

FASTQ quality encoding cannot be auto-detected reliably: the same quality line can be valid Phred+33 and Phred+64. Picking the wrong string can silently shift every score by 31. Confirm the encoding before parsing; see fastq-quality for the full encoding decision.

## Specialized Formats

| Format | String | Use Case |
|--------|--------|----------|
| ABI | `'abi'` | Sanger sequencing trace files (.ab1) |
| ABI Trimmed | `'abi-trim'` | ABI with low-quality ends trimmed |
| SFF | `'sff'` | 454/Ion Torrent flowgram data |
| SFF Trimmed | `'sff-trim'` | SFF with adapter/quality trimming |
| QUAL | `'qual'` | Quality scores file (pairs with FASTA) |
| PDB SEQRES | `'pdb-seqres'` | Protein sequences from PDB SEQRES records |
| PDB ATOM | `'pdb-atom'` | Sequences from ATOM records in PDB |
| SnapGene | `'snapgene'` | SnapGene .dna files |

### Reading ABI Trace Files
```python
record = SeqIO.read('sample.ab1', 'abi')
qualities = record.letter_annotations['phred_quality']
record_trimmed = SeqIO.read('sample.ab1', 'abi-trim')  # low-quality ends removed
```

### Reading 454/Ion Torrent SFF
```python
for record in SeqIO.parse('reads.sff', 'sff'):
    print(record.id, len(record.seq))
```

### Reading PDB Sequences
```python
for record in SeqIO.parse('structure.pdb', 'pdb-seqres'):
    print(record.id, record.seq)
```

## Alignment Formats (Read-Only)

| Format | String | Notes |
|--------|--------|-------|
| PHYLIP | `'phylip'` | Interleaved; `'phylip-relaxed'` allows longer names |
| Clustal | `'clustal'` | ClustalW output |
| Stockholm | `'stockholm'` | Rfam/Pfam alignments |
| NEXUS | `'nexus'` | PAUP/MrBayes format |
| MAF | `'maf'` | Multiple Alignment Format |

## Code Patterns

### Count Records Without Loading All
```python
count = sum(1 for _ in SeqIO.parse('sequences.fasta', 'fasta'))
```

### Read GenBank with Features
```python
for record in SeqIO.parse('sequence.gb', 'genbank'):
    for feature in record.features:
        if feature.type == 'CDS':
            product = feature.qualifiers.get('product', ['Unknown'])[0]
            cds_seq = feature.extract(record.seq)  # spliced feature sequence
```

### Access FASTQ Quality Scores
```python
for record in SeqIO.parse('reads.fastq', 'fastq'):
    qualities = record.letter_annotations['phred_quality']
    avg_quality = sum(qualities) / len(qualities)
```

### Read From a File Handle
```python
with open('sequences.fasta') as handle:
    for record in SeqIO.parse(handle, 'fasta'):
        print(record.id)
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Second loop over a parser yields nothing, no error | `parse()` generator exhausted after the first pass | Re-call `parse()` per pass, or `list()` once for small files |
| `TypeError: 'generator' object is not subscriptable` | Indexed/sliced a `parse()` result | Wrap in `list()`, or use `to_dict`/`index` for keyed access |
| `ValueError: More than one record found in handle` | `read()` on a multi-record file | Use `parse()` |
| `ValueError: No records found in handle` | `read()` on an empty/zero-record file | Check the file and format string; use `parse()` if multi-record |
| `ValueError: Duplicate key '...'` | `to_dict`/`index`/`index_db` hit a repeated id | Pass a `key_function` that derives unique keys |
| Random access by id silently slow / re-reads disk | `index()` re-parses each access; mutations don't persist | Expected; cache needed records, or use `to_dict` for small files |
| MemoryError / process killed on a huge file | `list()` or `to_dict()` loaded everything into RAM | Stream with `parse()`; use `index_db()` for random access |
| `ValueError: unknown format` | Misspelled format string | Use a lowercase string from the format tables |
| `ValueError`/`AssertionError` naming the LOCUS line | GenBank parser reads fixed LOCUS columns (molecule type ~44-54, topology ~55-63); ICE/SnapGene/Ensembl/assembler LOCUS lines violate the spec | Biologically valid content can still fail the strict column parse; fix the LOCUS columns or re-export from a spec-compliant writer |
| FASTQ scores all off by ~31 with no error | Wrong FASTQ variant string (Phred+33 vs +64 overlap) | Confirm encoding; see fastq-quality |
| `AttributeError` referencing `.alphabet` | Code assumes pre-1.78 alphabet API | Drop alphabet usage; molecule type lives in `annotations['molecule_type']` |

## Related Skills

- write-sequences - Write parsed sequences to new files
- filter-sequences - Filter sequences by criteria after reading
- format-conversion - Convert between formats (GenBank->FASTA silently drops annotations)
- compressed-files - Read gzip/bzip2/BGZF compressed files; only BGZF supports indexed random access
- fastq-quality - FASTQ encoding (Phred vs Solexa) and offset selection
- sequence-manipulation/seq-objects - Work with parsed SeqRecord and Seq objects
- database-access/entrez-fetch - Fetch sequences from NCBI instead of local files
- alignment-files/sam-bam-basics - For SAM/BAM/CRAM alignment files, use samtools/pysam
<!-- END FILE: sequence-io/read-sequences/SKILL.md -->

## 子目录：sequence-io/sequence-statistics

<!-- BEGIN FILE: sequence-io/sequence-statistics/SKILL.md -->
---
name: bio-sequence-statistics
description: Calculate assembly and sequence statistics (N50/L50, auN, NG50/NGA50, length distribution, GC content with ambiguity handling, summary reports) using Biopython. Use when analyzing sequence datasets, generating QC reports, or comparing genome assemblies.
tool_type: python
primary_tool: Bio.SeqIO
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Sequence Statistics

**"Calculate N50 and other assembly statistics"** -> Compute sequence count, length distribution, N50/L50, auN, GC content, and nucleotide composition for FASTA datasets.
- Python: `SeqIO.parse()`, `gc_fraction()` (BioPython)

Calculate comprehensive statistics for sequence datasets using Biopython.

## The Governing Principle

N50 measures CONTIGUITY, not correctness. A misassembled scaffold that wrongly joins distant regions can post a large N50 while being biologically wrong; N50 says nothing about base accuracy or join correctness. Treat contiguity metrics as one axis of assembly quality, alongside completeness (BUSCO) and correctness (read-backed validation, reference alignment).

Two further traps shape every reported number:
- N50 is a discontinuous, threshold-based statistic. Near the 50% crossing, contig lengths can differ by megabases, so a tiny change can jump N50 by megabases. Prefer auN (smooth, threshold-free) for robust comparison.
- N50 uses ASSEMBLY size as the denominator, so it is not comparable across assemblies of the same genome. Use NG50 (GENOME size denominator) to compare assemblies on a common baseline.

## Required Imports

```python
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction
import statistics
```

## N50, L50, and Nx Statistics

**Goal:** Report the length at which half the assembled bases reside in equal-or-longer contigs (N50), and how many contigs that takes (L50).

**Approach:** N50 is the minimal length `x` such that contigs of length `>= x` together cover `>= 50%` of total assembly length. Sort lengths DESCENDING, take the cumulative sum, and return the length at which the cumulative sum first reaches or crosses 50%. L50 is the COUNT of contigs at that crossing. Three details silently break naive implementations: the sort must be descending, the crossing test must be `>=` (not strict `>`), and the denominator must be the assembly total (not a genome estimate).

**Reference (BioPython 1.83+):**
```python
def n50_l50(lengths):
    '''Return (N50 length, L50 count) for a list of contig lengths.'''
    sorted_lengths = sorted(lengths, reverse=True)
    half = sum(sorted_lengths) / 2
    cumsum = 0
    for count, length in enumerate(sorted_lengths, start=1):
        cumsum += length
        if cumsum >= half:
            return length, count
    return 0, 0

lengths = [len(r.seq) for r in SeqIO.parse('assembly.fasta', 'fasta')]
n50, l50 = n50_l50(lengths)
print(f'N50: {n50:,} bp  L50: {l50} contigs')
```

### Any Nx Value (N75, N90)

```python
def calculate_nx(lengths, x):
    '''Nx where x is a percentage (50 for N50, 90 for N90).'''
    sorted_lengths = sorted(lengths, reverse=True)
    threshold = sum(sorted_lengths) * (x / 100)
    cumsum = 0
    for length in sorted_lengths:
        cumsum += length
        if cumsum >= threshold:
            return length
    return 0

lengths = [len(r.seq) for r in SeqIO.parse('assembly.fasta', 'fasta')]
print(f'N50: {calculate_nx(lengths, 50):,} bp')
print(f'N90: {calculate_nx(lengths, 90):,} bp')
```

## auN: Robust Contiguity (Preferred for Comparison)

**Goal:** Replace the discontinuous N50 with a smooth, threshold-free contiguity score that responds to every join.

**Approach:** auN (Heng Li, 2020) is the area under the Nx curve, equivalently a length-weighted average length: each contig contributes its own length weighted by the fraction of the assembly it represents. Connecting any two contigs always raises auN, even when N50 stays unchanged (joining two contigs both above, or both below, the N50 contig leaves N50 fixed). No single straddling contig arbitrarily sets the score.

Formula: auN = sum_i(L_i^2) / sum_j(L_j)

**Reference (BioPython 1.83+):**
```python
def calculate_aun(lengths):
    '''auN = sum(L_i^2) / sum(L_j); a length-weighted mean length.'''
    total = sum(lengths)
    return sum(length * length for length in lengths) / total if total else 0

lengths = [len(r.seq) for r in SeqIO.parse('assembly.fasta', 'fasta')]
print(f'auN: {calculate_aun(lengths):,.0f} bp')
```

## NG50, NGx, NA50, NGA50: Cross-Assembly and Misassembly-Aware

NG50/NGx use the GENOME size as the denominator instead of the assembly size, so two assemblies of the same genome share one baseline and become directly comparable. They require a known or estimated genome size (QUAST `--est-ref-size` or a reference). NA50/NGA50 are computed on alignment blocks broken at misassembly breakpoints; NGA50 markedly below NG50 signals misassemblies.

**Reference (BioPython 1.83+):**
```python
def calculate_ngx(lengths, genome_size, x=50):
    '''NGx uses genome_size (not assembly size) as the denominator.'''
    sorted_lengths = sorted(lengths, reverse=True)
    threshold = genome_size * (x / 100)
    cumsum = 0
    for length in sorted_lengths:
        cumsum += length
        if cumsum >= threshold:
            return length
    return 0  # assembly never covers x% of the genome

lengths = [len(r.seq) for r in SeqIO.parse('assembly.fasta', 'fasta')]
print(f'NG50: {calculate_ngx(lengths, genome_size=3_100_000_000):,} bp')
```

## Length Distribution

Median contig length is near-useless for assemblies: it is dominated by the many tiny contigs and sits among fragments, ignoring where the sequence mass lives. N50 and auN are mass-weighted precisely to answer "in contigs of what size does the bulk of the genome reside?" Report median for read-length QC, not for assembly contiguity.

```python
lengths = [len(r.seq) for r in SeqIO.parse('sequences.fasta', 'fasta')]
print(f'Count: {len(lengths)}  Total: {sum(lengths):,} bp')
print(f'Min: {min(lengths):,}  Max: {max(lengths):,}  Mean: {statistics.mean(lengths):,.1f} bp')
```

### Length Histogram Data

```python
from collections import Counter

lengths = [len(r.seq) for r in SeqIO.parse('sequences.fasta', 'fasta')]
bin_size = 100  # 100-bp length bins
histogram = Counter((l // bin_size) * bin_size for l in lengths)
for length_bin in sorted(histogram):
    print(f'{length_bin}-{length_bin + bin_size}: {histogram[length_bin]}')
```

## GC Content: Choose the Ambiguity Mode Explicitly

`gc_fraction(seq, ambiguous=...)` returns a FRACTION 0-1 (the old `Bio.SeqUtils.GC()` returned a PERCENT 0-100 and was REMOVED in 1.82; swapping names without rescaling is a silent 100x error). The `ambiguous=` argument changes the answer, so set it on purpose:

| Mode | Numerator | Denominator | `GCGCNNNN` |
|------|-----------|-------------|------------|
| `remove` (default) | G, C, S | only unambiguous + S/W (N excluded) | 1.0 |
| `ignore` | G, C, S | full length (N dilutes GC) | 0.5 |
| `weighted` | G, C, S + each ambiguous code x its expected GC | full length | 0.75 |

A naive `(G + C) / len` silently equals the `ignore` mode, under-reporting GC whenever N is present. `remove` reports GC among called bases; `ignore` reports GC over the full sequence including gaps/Ns; `weighted` apportions each IUPAC code its expected GC.

```python
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction

seq = Seq('GCGCNNNN')
gc_fraction(seq, ambiguous='remove')    # 1.0  - N dropped from both
gc_fraction(seq, ambiguous='ignore')    # 0.5  - N counted in denominator
gc_fraction(seq, ambiguous='weighted')  # 0.75 - N contributes 0.5 each
```

### Per-Sequence GC Distribution

```python
gc_values = [gc_fraction(r.seq, ambiguous='remove') for r in SeqIO.parse('sequences.fasta', 'fasta')]
print(f'Mean GC: {statistics.mean(gc_values):.1%}')
print(f'Median GC: {statistics.median(gc_values):.1%}')
print(f'Range: {min(gc_values):.1%} - {max(gc_values):.1%}')
```

## Comprehensive Summary Report

**Goal:** Generate a complete QC summary (counts, lengths, N50/L50, auN, GC) for any FASTA file in one pass.

**Approach:** Load all records once, compute length and GC arrays, derive N50/L50 from the cumulative sorted lengths and auN from the squared-length sum, and package into a dictionary.

**Reference (BioPython 1.83+):**
```python
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction
import statistics

def sequence_summary(fasta_file):
    records = list(SeqIO.parse(fasta_file, 'fasta'))
    lengths = [len(r.seq) for r in records]
    gc_values = [gc_fraction(r.seq, ambiguous='remove') for r in records]

    sorted_lengths = sorted(lengths, reverse=True)
    total_bp = sum(lengths)
    half = total_bp / 2

    cumsum, n50, l50 = 0, 0, 0
    for count, length in enumerate(sorted_lengths, start=1):
        cumsum += length
        if cumsum >= half:
            n50, l50 = length, count
            break

    aun = sum(length * length for length in lengths) / total_bp if total_bp else 0

    return {
        'file': fasta_file, 'sequences': len(records), 'total_bp': total_bp,
        'min_length': min(lengths), 'max_length': max(lengths),
        'mean_length': statistics.mean(lengths), 'median_length': statistics.median(lengths),
        'n50': n50, 'l50': l50, 'aun': aun,
        'gc_mean': statistics.mean(gc_values),
        'gc_std': statistics.stdev(gc_values) if len(gc_values) > 1 else 0,
    }

stats = sequence_summary('assembly.fasta')
print(f'Sequences: {stats["sequences"]:,}  Total: {stats["total_bp"]:,} bp')
print(f'N50: {stats["n50"]:,} bp (L50: {stats["l50"]})  auN: {stats["aun"]:,.0f} bp')
print(f'GC: {stats["gc_mean"]:.1%} (+/- {stats["gc_std"]:.1%})')
```

## Compare Multiple Assemblies

**Goal:** Build a side-by-side table of key metrics across assembly files.

**Approach:** Run `sequence_summary` on each file and format the results into an aligned table; auN is the most reliable single column for ranking contiguity.

**Reference (BioPython 1.83+):**
```python
from pathlib import Path

files = sorted(Path('assemblies/').glob('*.fasta'))
print(f'{"File":<30} {"Seqs":>8} {"Total bp":>15} {"N50":>12} {"auN":>12}')
print('-' * 80)
for fasta_file in files:
    s = sequence_summary(str(fasta_file))
    print(f'{fasta_file.name:<30} {s["sequences"]:>8,} {s["total_bp"]:>15,} {s["n50"]:>12,} {s["aun"]:>12,.0f}')
```

## Nucleotide Composition

```python
from collections import Counter

def nucleotide_composition(fasta_file):
    counts = Counter()
    for record in SeqIO.parse(fasta_file, 'fasta'):
        counts.update(str(record.seq).upper())
    total = sum(counts.values())
    return {base: count / total for base, count in counts.items()}

comp = nucleotide_composition('sequences.fasta')
for base in ['A', 'T', 'G', 'C', 'N']:
    if base in comp:
        print(f'{base}: {comp[base]:.2%}')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| N50 looks far too small | Sorted ascending instead of descending | Sort lengths with `reverse=True` before the cumulative sum |
| N50 off by one contig near the crossing | Strict `>` test misses the exact-50% case | Use `>= 50%` (minimal length that reaches/exceeds half) |
| N50 not comparable between assemblies | Used assembly size as denominator | Use NG50 with the genome size for cross-assembly comparison |
| GC values off by 100x | Treated `gc_fraction` (0-1) like old `GC()` (0-100) | Multiply by 100 only for display; never mix the two |
| GC silently low when Ns present | Default `remove` vs naive `(G+C)/len` (= `ignore`) | Pass `ambiguous=` explicitly to match intent |
| Huge N50 on a wrong assembly | N50 measures contiguity, not correctness | Pair with BUSCO completeness and read-backed/reference validation; prefer auN |

## References

- Li H (2020). "auN: a new metric to measure assembly contiguity." Technical blog post, https://lh3.github.io/2020/04/08/a-new-metric-on-assembly-contiguity (auN = area under the Nx curve; smooth, threshold-free contiguity).

## Related Skills

- read-sequences - Parse sequences for statistics calculation
- batch-processing - Calculate stats across multiple files
- fastq-quality - Quality score statistics for FASTQ files
- sequence-manipulation/sequence-properties - Per-sequence GC content and properties
- alignment-files/bam-statistics - samtools stats/flagstat for alignment statistics
<!-- END FILE: sequence-io/sequence-statistics/SKILL.md -->

## 子目录：sequence-io/write-sequences

<!-- BEGIN FILE: sequence-io/write-sequences/SKILL.md -->
---
name: bio-write-sequences
description: Write biological sequences to files (FASTA, FASTQ, GenBank, EMBL) using Biopython Bio.SeqIO. Use when saving sequences, creating new sequence files, or outputting modified records.
tool_type: python
primary_tool: Bio.SeqIO
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Write Sequences

**"Write sequences to a file"** -> Serialize SeqRecord objects into a formatted sequence file.
- Python: `SeqIO.write()` (BioPython)
- R: `writeXStringSet()` (Biostrings)

## Governing Principle

The write is only as complete as the SeqRecord. Each format reads specific record fields and silently ignores the rest, so what survives a write is decided by which fields are populated before the call, not by the format string. FASTA serializes only `id`/`description`+`seq`; FASTQ additionally requires `letter_annotations['phred_quality']`; GenBank/EMBL additionally require `annotations['molecule_type']`. Populate the fields a format needs, or the write either drops data quietly (FASTA) or raises (FASTQ/GenBank).

## Required Import

```python
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
```

## Core Functions

### SeqIO.write() - Write Records to File

```python
SeqIO.write(records, 'output.fasta', 'fasta')
```

- `records` - Single SeqRecord, list, or iterator of SeqRecords
- `handle` - Filename (string) or open file handle
- `format` - Lowercase output format string
- Returns the number of records written (integer)

### record.format() - Get Formatted String

```python
formatted = record.format('fasta')
```

## The FASTA Header Trap (id vs description)

FASTA output is built from `record.description`, NOT `record.id`. The writer compares the first whitespace token of `description` to `id`: if they match it writes `description` as-is; otherwise it prepends `id` + a space. When a record is parsed from FASTA, `description` already leads with the id token, so a round trip is faithful. But when `id` and `description` are set independently, a stale id-like token inside the description gets duplicated, and older BioPython releases dropped the id entirely instead of prepending it.

| record.id | record.description | Header written |
|-----------|--------------------|----------------|
| `seq1` | `seq1 kinase domain` | `>seq1 kinase domain` (clean: description leads with id) |
| `seq1` | `kinase domain` | `>seq1 kinase domain` (id auto-prepended) |
| `seq1` | `` (empty) | `>seq1` (id used as fallback) |
| `seq1` | `gene7 kinase domain` | `>seq1 gene7 kinase domain` (stale id duplicated) |

To control the header exactly and stay robust across versions, make `description` begin with `id` + a space: `description=f'{rec_id} kinase domain'`. The FASTA writer wraps the sequence at 60 characters per line by default.

## Format Field Requirements

| Format | String | Record fields read | Hard requirement |
|--------|--------|--------------------|------------------|
| FASTA | `'fasta'` | id/description, seq | none (header trap above) |
| FASTQ | `'fastq'` | seq, letter_annotations | phred quality scores |
| GenBank | `'genbank'` / `'gb'` | seq, annotations, features | molecule_type |
| EMBL | `'embl'` | seq, annotations, features | molecule_type |
| Tab | `'tab'` | id, seq | none |

## Creating SeqRecord Objects

**Goal:** Construct in-memory records that carry the fields the target format requires.

**Approach:** Build a `SeqRecord` from a `Seq` plus `id`; add `letter_annotations['phred_quality']` for FASTQ and `annotations['molecule_type']` for GenBank/EMBL.

**"Create a sequence record from scratch"** -> Wrap a `Seq` in a `SeqRecord` with metadata.
- Python: `SeqRecord(Seq(...), id=...)` (BioPython)

```python
record = SeqRecord(Seq('ATGCGATCGATCG'), id='seq1', description='seq1 example sequence')
```

## Code Patterns

### Write Single or Multiple Records

```python
records = [SeqRecord(Seq('ATGC'), id='seq1'), SeqRecord(Seq('GCTA'), id='seq2')]
count = SeqIO.write(records, 'output.fasta', 'fasta')
```

### Write to a File Handle (and Append)

```python
with open('output.fasta', 'w') as handle:
    SeqIO.write(records, handle, 'fasta')

with open('output.fasta', 'a') as handle:
    SeqIO.write(new_records, handle, 'fasta')
```

### Write Modified Records via Generator

**Goal:** Transform sequences in memory and write the modified versions to a new file.

**Approach:** Parse input, map a transform over a generator, write the generator. Streaming avoids loading every record into RAM.

**"Modify sequences and save"** -> Parse records, transform each, write with `SeqIO.write()`.

```python
def uppercase_record(rec):
    return SeqRecord(rec.seq.upper(), id=rec.id, description=rec.description)

records = SeqIO.parse('input.fasta', 'fasta')
modified = (uppercase_record(rec) for rec in records)
SeqIO.write(modified, 'output.fasta', 'fasta')
```

### Write FASTQ with Quality Scores

FASTQ requires `letter_annotations['phred_quality']` as a list of ints. `letter_annotations` is length-locked to `len(seq)`: assigning a list whose length differs from the sequence raises. Set the sequence first, then the quality list of matching length.

```python
record = SeqRecord(Seq('ATGCGATCG'), id='read1')
record.letter_annotations['phred_quality'] = [40] * len(record.seq)
SeqIO.write(record, 'output.fastq', 'fastq')
```

### Quality Encoding on Write (Phred vs Solexa)

When both `phred_quality` and `solexa_quality` keys are present, the writer uses Phred. Writing `'fastq-solexa'` from a Phred-only record forces an on-the-fly lossy conversion (the scales diverge in the low-quality region) and emits a `BiopythonWarning` once any score reaches the high end (max quality >= ~62). For modern data, write plain `'fastq'` (Sanger/Phred+33); only use `'fastq-solexa'`/`'fastq-illumina'` when a tool explicitly demands that legacy encoding.

### Write GenBank Format

GenBank and EMBL writing requires `annotations['molecule_type']` (the alphabet that once carried this was removed in BioPython 1.78). Missing it raises on write.

```python
record = SeqRecord(Seq('ATGCGATCGATCG'), id='SEQ001', name='example')
record.annotations['molecule_type'] = 'DNA'
record.annotations['topology'] = 'linear'
record.annotations['organism'] = 'Example organism'
SeqIO.write(record, 'output.gb', 'genbank')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Header has a duplicated or mangled id | FASTA builds the header from `description`; it does not lead with `id` + space | Set `description=f'{rec.id} ...'` or leave description empty to fall back to id |
| `ValueError: No suitable quality scores found in letter_annotations of SeqRecord (id=...)` on FASTQ write | Record has no `letter_annotations['phred_quality']` | Assign `record.letter_annotations['phred_quality'] = [q]*len(seq)` |
| `TypeError: Any per-letter annotation should be a Python sequence ... of the same length` | Quality list length != `len(seq)` (annotations are length-locked) | Set seq first, then a quality list of matching length |
| `ValueError: missing molecule_type ...` on GenBank/EMBL write | No `annotations['molecule_type']` since the 1.78 alphabet removal | Add `record.annotations['molecule_type'] = 'DNA'` (or 'RNA'/'protein') |
| `BiopythonWarning: Data loss - max Solexa quality ...` | Writing `'fastq-solexa'` from a high Phred-only record forces lossy conversion | Write plain `'fastq'` unless a tool requires the Solexa encoding |
| `TypeError` passing a raw `str`/`Seq` to write | `SeqIO.write` expects SeqRecord(s) | Wrap the sequence in a `SeqRecord` first |
| `ValueError: Sequences must all be the same length` | PHYLIP/alignment format with unequal lengths | Align, pad, or trim to equal length first |

## Related Skills

- read-sequences - Read sequences before modifying and writing
- format-conversion - Direct format conversion without intermediate processing
- filter-sequences - Filter sequences before writing a subset
- fastq-quality - Phred/Solexa encodings and quality-score handling
- sequence-manipulation/seq-objects - Create SeqRecord objects to write
- alignment-files/sam-bam-basics - For SAM/BAM output, use samtools/pysam
<!-- END FILE: sequence-io/write-sequences/SKILL.md -->

<!-- END CATEGORY: sequence-io -->

