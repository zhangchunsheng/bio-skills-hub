---
slug: bio-alignment-integrated
version: 1.0.1
displayName: "序列比对 / Multiple sequence alignment (MSA) tools and post-processing"
name: bio-alignment-integrated
summary: "中文：序列比对综合技能，整合 7 个相关专题，覆盖多序列比对(MSA)工具与后处理：MAFFT、MUSCLE5、ClustalOmega、T-Coffee，以及比对质量评估、截短和结构比对。 English: Integrated Multiple sequence alignment (MSA) tools and post-processing skill covering 7 related topics, including Multiple sequence alignment (MSA) tools and post-processing: MAFFT, MUSCLE5, ClustalOmega, T-Coffee, alignment quality assessment, trimming, and structural alignment."
description: "中文：这是一个面向序列比对的综合生物信息学 Skill，整合当前分类下 7 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：多序列比对(MSA)工具与后处理：MAFFT、MUSCLE5、ClustalOmega、T-Coffee，以及比对质量评估、截短和结构比对。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Bio.Align, Bio.AlignIO, ClipKIT。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Multiple sequence alignment (MSA) tools and post-processing, combining 7 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Multiple sequence alignment (MSA) tools and post-processing: MAFFT, MUSCLE5, ClustalOmega, T-Coffee, alignment quality assessment, trimming, and structural alignment. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Bio.Align, Bio.AlignIO, ClipKIT. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# alignment 分类 Skill 整合版

> 本文件整合同一主分类目录下 7 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: alignment -->

## 子目录：alignment/alignment-io

<!-- BEGIN FILE: alignment/alignment-io/SKILL.md -->
---
name: bio-alignment-io
description: Read, write, and convert multiple sequence alignment files using Biopython Bio.AlignIO. Supports Clustal, PHYLIP, Stockholm, FASTA, Nexus, and other alignment formats for phylogenetics and conservation analysis. Use when reading, writing, or converting alignment file formats.
tool_type: python
primary_tool: Bio.AlignIO
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Alignment File I/O

Read, write, and convert multiple sequence alignment files in various formats.

## Required Import

**Goal:** Load modules for reading, writing, and manipulating multiple sequence alignments.

**Approach:** Import AlignIO for file I/O and supporting classes for programmatic alignment construction.

```python
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
```

## Format Coverage Map

Three Python libraries cover the alignment-format space, with overlapping but non-identical support. Pick by what is actually required.

| Format | `Bio.AlignIO` | `Bio.Align` (modern) | `pyhmmer.easel` | Notes |
|--------|---------------|----------------------|-----------------|-------|
| Aligned FASTA | R/W | R/W | R/W | Most portable; loses annotations |
| Clustal | R/W | R/W | R | Clustal conservation marks NOT round-tripped |
| PHYLIP (interleaved/sequential/relaxed) | R/W | R/W | R | Strict 10-char names is silent footgun |
| Stockholm | R/W | R/W | R/W | Only format preserving GS/GR/GC/GF annotations |
| NEXUS | R/W | R/W | -- | MrBayes / PAUP* input |
| MAF (Multiple Alignment Format) | R/W | R/W | -- | UCSC whole-genome alignments |
| A2M / A3M | -- (use `'fasta'` parser then post-process) | -- | R/W | HMMER (a2m), HHsuite/ColabFold (a3m) |
| MSF (GCG) | R | -- | -- | GCG legacy |
| EMBOSS / Mauve XMFA / FASTA-m10 | R | partial | -- | One-way: read-only |

**Formats NOT in BioPython** (use dedicated tools):

| Format | Tool | Why |
|--------|------|-----|
| HAL | progressiveCactus, halTools | HDF5-backed multi-genome alignments at TB scale |
| chain / net | UCSC Kent tools (`liftOver`, `chainNet`) | Pairwise genome alignment |
| AXT | BLASTZ / lastz native | Pairwise alignment blocks |
| PSL | UCSC Kent tools (`pslPretty`, `blat`) | BLAT alignment summary |
| GFA / rGFA | `vg`, `odgi`, `pggb`, gfatools | Pangenome graph |
| GAF | `vg surject`, `vg call` | Graph alignment format (read-to-graph) |

Recommend `Bio.Align` (modern API) over `Bio.AlignIO` (legacy) for new code; it returns `Alignment` objects with built-in `.counts()` and `.substitutions` properties. For multi-gigabyte Stockholm databases such as Pfam-A.full, `pyhmmer.easel.MSAFile` streams record-by-record where `Bio.AlignIO.parse` works but at higher per-record cost.

## Reading Alignments

**"Read an alignment file"** -> Parse an alignment file into an alignment object with sequences and metadata accessible.

**Goal:** Load alignment data from files in various formats (Clustal, PHYLIP, Stockholm, FASTA).

**Approach:** Use `AlignIO.read()` for single-alignment files or `AlignIO.parse()` for files containing multiple alignments.

### Single Alignment File
```python
from Bio import AlignIO

alignment = AlignIO.read('alignment.aln', 'clustal')
print(f'Alignment length: {alignment.get_alignment_length()}')
print(f'Number of sequences: {len(alignment)}')
```

### Multiple Alignments in One File
```python
for alignment in AlignIO.parse('multi_alignment.sto', 'stockholm'):
    print(f'Alignment with {len(alignment)} sequences, length {alignment.get_alignment_length()}')
```

### Read as List
```python
alignments = list(AlignIO.parse('alignments.phy', 'phylip'))
print(f'Read {len(alignments)} alignments')
```

## Writing Alignments

**Goal:** Save alignment data to files in standard formats for downstream tools or archival.

**Approach:** Use `AlignIO.write()` with the target format specifier, supporting single or multiple alignments and file handles.

### Write Single Alignment
```python
AlignIO.write(alignment, 'output.fasta', 'fasta')
```

### Write Multiple Alignments
```python
alignments = [alignment1, alignment2, alignment3]
count = AlignIO.write(alignments, 'output.sto', 'stockholm')
print(f'Wrote {count} alignments')
```

### Write to Handle
```python
with open('output.aln', 'w') as handle:
    AlignIO.write(alignment, handle, 'clustal')
```

## Format Conversion

**"Convert alignment format"** -> Transform an alignment file from one format to another (e.g., Clustal to PHYLIP).

**Goal:** Convert alignment files between formats for compatibility with different analysis tools.

**Approach:** Use `AlignIO.convert()` for direct one-step conversion, or read-modify-write for cases requiring intermediate manipulation.

### Direct Conversion (Most Efficient)
```python
AlignIO.convert('input.aln', 'clustal', 'output.phy', 'phylip')
```

### With Alphabet Specification
```python
AlignIO.convert('input.sto', 'stockholm', 'output.nex', 'nexus', molecule_type='DNA')
```

### Manual Conversion (When Modification Needed)
```python
alignment = AlignIO.read('input.aln', 'clustal')
# ... modify alignment ...
AlignIO.write(alignment, 'output.fasta', 'fasta')
```

## Accessing Alignment Data

**Goal:** Navigate and extract data from alignment objects including sequences, columns, and slices.

**Approach:** Use iteration, indexing, and column slicing on the alignment object.

```python
alignment = AlignIO.read('alignment.aln', 'clustal')

# Iterate over sequences
for record in alignment:
    print(f'{record.id}: {record.seq}')

# Access by index
first_seq = alignment[0]
last_seq = alignment[-1]

# Slice columns
column_slice = alignment[:, 10:20]  # Columns 10-19

# Get specific column
column = alignment[:, 5]  # Column 5 as string
```

## Working with Alignment Objects

### Get Alignment Properties
```python
alignment = AlignIO.read('alignment.aln', 'clustal')

length = alignment.get_alignment_length()
num_seqs = len(alignment)
seq_ids = [record.id for record in alignment]
```

### Slice Alignments
```python
# Get subset of sequences
subset = alignment[0:5]  # First 5 sequences

# Get subset of columns
trimmed = alignment[:, 50:150]  # Columns 50-149

# Combine slicing
region = alignment[0:5, 50:150]  # 5 sequences, columns 50-149
```

## Creating Alignments Programmatically

**Goal:** Build an alignment object from sequences defined in code rather than read from a file.

**Approach:** Construct SeqRecord objects with gap characters and wrap them in a MultipleSeqAlignment.

```python
from Bio.Align import MultipleSeqAlignment
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

records = [
    SeqRecord(Seq('ACTGACTGACTG'), id='seq1'),
    SeqRecord(Seq('ACTGACT-ACTG'), id='seq2'),
    SeqRecord(Seq('ACTG-CTGACTG'), id='seq3'),
]
alignment = MultipleSeqAlignment(records)
AlignIO.write(alignment, 'new_alignment.fasta', 'fasta')
```

## Format Selection for Downstream Tools

Choosing the output format depends on which downstream tool consumes the alignment:

| Downstream Tool | Required Format | BioPython Format String |
|----------------|-----------------|------------------------|
| RAxML-NG, IQ-TREE | PHYLIP (relaxed) | `'phylip-relaxed'` |
| MrBayes | NEXUS | `'nexus'` |
| PAUP* | NEXUS or PHYLIP | `'nexus'` or `'phylip'` |
| HMMER, Infernal | Stockholm | `'stockholm'` |
| Pfam/Rfam databases | Stockholm | `'stockholm'` |
| PAML/codeml | PHYLIP (sequential) | `'phylip-sequential'` |
| Most tools | FASTA | `'fasta'` |

### Annotation Preservation

Not all formats support annotations. Converting between formats can silently discard metadata:

| Format | Sequence Annotations | Column Annotations | Secondary Structure |
|--------|---------------------|-------------------|-------------------|
| Stockholm | Yes (GS/GR lines) | Yes (GC lines) | Yes (SS_cons) |
| NEXUS | Partial (SETS block) | Via CHARSET | No |
| Clustal | No (conservation marks not parsed) | No | No |
| PHYLIP | No | No | No |
| FASTA | No | No | No |

Converting Stockholm to FASTA or PHYLIP discards all annotations, secondary structure markup, and per-residue quality scores. If annotations matter, keep a Stockholm master copy.

## Format-Specific Notes

### PHYLIP Format Pitfalls

PHYLIP has two incompatible variants (interleaved vs sequential) and two name-length modes (strict vs relaxed). Confusing these causes silent data corruption.

**Strict PHYLIP** truncates sequence names to exactly 10 characters. This can silently merge distinct sequences whose names share a 10-character prefix (e.g., `Homo_sapiens_chr1` and `Homo_sapiens_chr2` both become `Homo_sapie`).

```python
# Strict PHYLIP (10-char names, interleaved) -- only for tools requiring it
alignment = AlignIO.read('file.phy', 'phylip')

# Sequential PHYLIP (10-char names, one sequence at a time) -- PAML/codeml
alignment = AlignIO.read('file.phy', 'phylip-sequential')

# Relaxed PHYLIP (no name limit) -- RAxML-NG, IQ-TREE (recommended default)
alignment = AlignIO.read('file.phy', 'phylip-relaxed')

# Always prefer phylip-relaxed for writing unless the downstream tool
# specifically requires strict format
AlignIO.write(alignment, 'output.phy', 'phylip-relaxed')
```

#### PHYLIP-Relaxed Dialect Mismatches Between Tree Tools

Biopython's `'phylip-relaxed'` writes a single space between name and sequence. RAxML-NG and IQ-TREE accept this; PhyML rejects sequence names containing colons or parentheses; PAML's codeml expects sequential format with name-truncation behaviour distinct from interleaved. Common silent failures:

| Symptom | Cause | Fix |
|---------|-------|-----|
| RAxML-NG: `terminating with uncaught exception ... bad alphabet` | Stop codons (`*`) in protein alignment | Replace `*` with `X` before writing |
| IQ-TREE: `not a valid PHYLIP file` | Sequence name contains `:` (NEXUS-tree-style refs) | Sanitize names: `re.sub(r'[():,]', '_', record.id)` |
| PhyML: silently truncated names | Names >100 chars | PhyML truncates without warning at 100 chars in current build |
| codeml: `cannot read sequences` | Used `phylip-relaxed` instead of `phylip-sequential` | codeml requires strict sequential |

Always verify by running the downstream tool's "validate input only" mode (e.g. `iqtree2 -s file.phy --check`) before committing to a long compute.

### MAF Block Coordinate Conventions

UCSC MAF (read via `AlignIO.parse(file, 'maf')`) returns blocks with per-row `annotations`:
- `start` (0-based; converts directly to BED but is off-by-one vs GFF)
- `size` (length on src strand)
- `strand` (`+` or `-`)
- `srcSize` (length of source chromosome)

For minus-strand rows, `start` is measured from the END of the source contig: the corresponding plus-strand start is `srcSize - start - size`. Without this conversion, lifting MAF to genome coordinates places minus-strand blocks at the wrong locus. Reference: UCSC MAF spec at genome.ucsc.edu/FAQ/FAQformat.html#format5.

```python
def maf_to_plus_strand_coords(row_anno):
    if row_anno['strand'] == '-':
        return row_anno['srcSize'] - row_anno['start'] - row_anno['size']
    return row_anno['start']
```

### Stockholm Format Annotations

Stockholm format (used by Pfam, Rfam, HMMER) supports four annotation line types:

| Line Prefix | Scope | Description | Example |
|-------------|-------|-------------|---------|
| `#=GF` | File | Alignment-level metadata (ID, accession, description) | `#=GF AC PF00001` |
| `#=GC` | Column | Per-column annotation (1 char per alignment column) | `#=GC SS_cons ..(((...)))..` |
| `#=GS` | Sequence | Per-sequence free text (organism, description) | `#=GS seq1 OS Homo sapiens` |
| `#=GR` | Residue | Per-residue annotation (1 char per residue) | `#=GR seq1 SS ..HHH..EEE..` |

Common GC annotations: `SS_cons` (consensus secondary structure), `RF` (reference coordinates), `seq_cons` (consensus sequence).

**WUSS notation** in RNA `#=GC SS_cons` lines uses nested bracket pairs (`<>`, `()`, `[]`, `{}`) for paired bases and characters like `_`, `-`, `,`, `:`, `.`, `~` for unpaired regions; pseudoknots use upper/lower-case letter pairs (`Aa`, `Bb`). Consult the Infernal user guide for the full character table before writing or parsing custom SS_cons strings.

```python
alignment = AlignIO.read('pfam.sto', 'stockholm')

for record in alignment:
    print(record.id, record.annotations)
    if 'secondary_structure' in record.letter_annotations:
        print(f'  SS: {record.letter_annotations["secondary_structure"]}')

ss_cons = alignment.column_annotations.get('secondary_structure')
```

**Round-trip caveat:** `AlignIO.write(alignment, 'out.fasta', 'fasta')` discards every Stockholm annotation silently. Re-reading and re-writing as Stockholm preserves GC/GR but dropped/added sequences invalidate the per-residue annotations -- regenerate annotations after edits.

**Pfam-style `name/start-end` identifier convention:** Pfam, Rfam, and Dfam Stockholm IDs (e.g. `Q9Y6Y0/45-198`) encode a 1-based inclusive region. Biopython does not split this; before passing to RAxML or IQ-TREE, parse the suffix into `record.annotations['start']` / `['end']` and strip from `record.id`, then restore it after.

### A2M / A3M Conventions

A2M (HMMER) and A3M (HHsuite, ColabFold) encode match vs insert columns by case (uppercase / `-` = match column, lowercase / `.` = insert column). A2M pads inserts across rows so it loads as a rectangular MSA; A3M does not, so convert with HHsuite `reformat.pl a3m a2m in.a3m out.a2m` (or `pyhmmer.easel.MSAFile(..., format='a2m')`) before parsing as a normal alignment.

**reformat.pl pitfall:** HHsuite's `reformat.pl a3m a2m` uses the FIRST sequence in the A3M as the match-state reference. ColabFold MSAs typically place the query first, which is the desired reference; merged or sorted A3Ms can have a non-query first sequence, producing match-state assignments that mis-align the query. Either (a) verify the first sequence is the query before reformatting, or (b) renormalise with `hhfilter -i in.a3m -o out.a3m -id 100 -qid 0 -cov 0` before running `reformat.pl`. A3M files emitted by `hhblits` always have the query first; A3M files concatenated from MSA databases do not.

```python
alignment = AlignIO.read('hhsearch.a2m', 'fasta')
match_only_seqs = [
    ''.join(c for c in str(r.seq) if c.isupper() or c == '-')
    for r in alignment
]
```

### Streaming Large Stockholm Databases

`Bio.AlignIO.read()` is in-memory; for Pfam-A.full (multi-gigabyte; ~22,000 family alignments in Pfam 37) or BFD (>2 TB), use `pyhmmer.easel.MSAFile` for streaming Stockholm or A3M.

```python
import pyhmmer

with pyhmmer.easel.MSAFile('Pfam-A.full', digital=True) as msa_file:
    for msa in msa_file:
        if msa.nseq < 50:
            continue
        weights = msa.compute_weights(method='pb')
        print(msa.name.decode(), msa.nseq, msa.alen, f'sum_w={sum(weights):.1f}')
```

`msa.compute_weights(method='pb')` computes Henikoff PB weights via the same Easel routine HMMER uses; the weights sum to the number of sequences (not Neff). For an Henikoff-style Neff estimate, see `msa-parsing/examples/neff.py`.

### Clustal Format
```python
# Clustal preserves conservation symbols in file but not when parsed
alignment = AlignIO.read('clustal.aln', 'clustal')
```

## Batch Processing Multiple Files

**Goal:** Convert a directory of alignment files from one format to another in bulk.

**Approach:** Glob for input files and iterate, reading each alignment and writing to the target format.

```python
from pathlib import Path

input_dir = Path('alignments/')
output_dir = Path('converted/')

for input_file in input_dir.glob('*.aln'):
    alignment = AlignIO.read(input_file, 'clustal')
    output_file = output_dir / f'{input_file.stem}.fasta'
    AlignIO.write(alignment, output_file, 'fasta')
```

## Alternative: Bio.Align Module I/O

**Goal:** Use the modern Bio.Align module for alignment I/O with access to newer features like counts and substitutions.

**Approach:** Use `Align.read()`, `Align.parse()`, and `Align.write()` which return `Alignment` objects instead of `MultipleSeqAlignment`.

The newer `Bio.Align` module provides its own I/O functions that return `Alignment` objects (instead of `MultipleSeqAlignment`). These support additional formats and provide access to modern alignment features.

```python
from Bio import Align

# Read single alignment (returns Alignment object)
alignment = Align.read('alignment.aln', 'clustal')

# Parse multiple alignments
for alignment in Align.parse('multi.sto', 'stockholm'):
    print(f'Alignment with {len(alignment)} sequences')

# Write alignment
Align.write(alignment, 'output.fasta', 'fasta')
```

### When to Use Which

| Use Case | Module |
|----------|--------|
| Legacy code, MultipleSeqAlignment needed | `Bio.AlignIO` |
| Modern features (counts, substitutions) | `Bio.Align` |
| Format conversion | Either works |
| Working with pairwise alignments | `Bio.Align` |

## Quick Reference: Common Operations

| Task | Code |
|------|------|
| Read single alignment | `AlignIO.read(file, format)` |
| Read multiple alignments | `AlignIO.parse(file, format)` |
| Write alignment(s) | `AlignIO.write(align, file, format)` |
| Convert format | `AlignIO.convert(in_file, in_fmt, out_file, out_fmt)` |
| Get length | `alignment.get_alignment_length()` |
| Get sequence count | `len(alignment)` |
| Slice columns | `alignment[:, start:end]` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: No records` | Empty file | Check file path and format |
| `ValueError: More than one record` | Multiple alignments with `read()` | Use `parse()` instead |
| `ValueError: Sequences different lengths` | Invalid alignment | Ensure all sequences same length |
| `ValueError: unknown format` | Unsupported format string | Check supported formats list |

## Related Skills

- alignment/multiple-alignment - Run MSA tools (MAFFT, MUSCLE5, ClustalOmega) to generate alignments
- alignment/pairwise-alignment - Create pairwise alignments with PairwiseAligner
- alignment/msa-parsing - Analyze alignment content and annotations
- alignment/msa-statistics - Calculate conservation and identity
- alignment/structural-alignment - Foldseek/TM-align outputs and Foldmason `result_aa.fa` / `result_3di.fa` MSAs (FASTA-loadable; the per-column LDDT report is HTML, not BioPython-parseable)
- alignment/alignment-trimming - Pre-format trimming with column-mapping retention
- sequence-io/format-conversion - Convert sequence (non-alignment) formats

## References

- Nawrocki EP, Eddy SR. 2013. Infernal 1.1: 100-fold faster RNA homology searches. Bioinf 29:2933-2935 (WUSS notation reference; see also the Infernal user guide).
- Larralde M et al. 2023. PyHMMER: a Python library binding to HMMER for efficient sequence analysis. Bioinf 39:btad214.
- Cock PJA et al. 2009. Biopython: freely available Python tools for computational molecular biology and bioinformatics. Bioinf 25:1422-1423.
- Mistry J et al. 2021. Pfam: the protein families database in 2021. NAR 49:D412-D419.
- Steinegger M et al. 2019. HH-suite3 for fast remote homology detection and deep protein annotation. BMC Bioinf 20:473.
- Mirdita M et al. 2022. ColabFold: making protein folding accessible to all. Nat Methods 19:679-682.
- Blanchette M et al. 2004. Aligning multiple genomic sequences with the threaded blockset aligner. Genome Res 14:708-715.
<!-- END FILE: alignment/alignment-io/SKILL.md -->

## 子目录：alignment/alignment-trimming

<!-- BEGIN FILE: alignment/alignment-trimming/SKILL.md -->
---
name: bio-alignment-trimming
description: Trim multiple sequence alignments using ClipKIT, trimAl, BMGE, Divvier, or HMMcleaner with mode selection guidance per downstream goal. Use when removing unreliable columns or contaminating residues before phylogenetic inference, HMM building, or selection analysis.
tool_type: mixed
primary_tool: ClipKIT
---

## Version Compatibility

Reference examples tested with: ClipKIT 2.1+, trimAl 1.4+, BMGE 1.12+, Divvier 1.01+, HMMcleaner (current CPAN release of `Bio::MUST::Apps::HmmCleaner`), BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `clipkit --version`, `trimal --version`, `BMGE --help`, `Divvier --help`
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Alignment Trimming

**"Remove unreliable columns from this MSA"** -> Filter or split columns based on gap fraction, conservation, entropy, or per-residue quality.
- CLI: `clipkit`, `trimal`, `BMGE`, `Divvier`, `HMMcleaner`
- Python: post-process via Bio.AlignIO with custom column masks

**"Make this alignment publication-grade for phylogenetics"** -> Apply ClipKIT's `kpic-smart-gap` mode, or trimAl `-automated1`, then verify via tree-stability comparison before vs after trimming.

Tool choice and aggressiveness matter more than trimming vs not-trimming. Pick a mode by dataset character (table below), and always run a sensitivity check by building trees on trimmed and untrimmed alignments.

### Pick a Trimming Mode by Dataset Character

| Dataset character | Trimming effect | Recommended approach |
|-------------------|-----------------|----------------------|
| Deep-divergence orthologs (>500 Ma), saturated 3rd codons | Aggressive trimming HURTS (Tan-style result) | No trim or `kpic-smart-gap` only; report sensitivity to trimming choice |
| Mid-depth eukaryotic (animal phyla, fungal classes) | ClipKIT `kpic-smart-gap` HELPS | Steenwyk-style result |
| Shallow (within-genus) | All trimmers ~equivalent | Choose for downstream-tool compatibility |
| Concatenated supermatrix with very long alignments (>10 kb) | Trimming reduces phylogenetic noise | `kpic-smart-gap` or BMGE `-h 0.5` |
| Single short genes (<200 bp aligned) | Trimming amplifies stochastic error | Skip column trimming; use sequence-level outlier filtering |

**The 20%/40% rule.** Tan et al 2015 (Syst Biol) and Steenwyk et al 2020 (PLOS Bio) appear to disagree but their conclusions are reconciled by trimming aggressiveness: light trimming (<20% of columns removed) has minimal impact on tree accuracy regardless of method; heavy trimming (>40%) removes phylogenetic signal alongside noise and degrades tree accuracy on most empirical datasets. Steenwyk's ClipKIT `kpic-smart-gap` improves trees because it stays in the light-trim regime; the older Gblocks defaults fail because they over-trim. **Operational rule:** if the trimmer removes >40% of columns, the mode is too aggressive for the dataset; switch to a less aggressive mode or skip trimming.

Always run a sensitivity analysis: build the tree on trimmed AND untrimmed alignments. If topology and support are stable across trimming choices, the conclusion is robust; if unstable, report this and pick the result better supported by independent evidence (gene-tree concordance, biological priors).

## Goal-Driven Tool Selection

| Downstream goal | First-line tool | Rationale |
|----------------|-----------------|-----------|
| Phylogenetic-tree input (concatenated genes) | ClipKIT `kpic-smart-gap` (Steenwyk et al 2020 PLOS Bio) | Retains parsimony-informative + constant sites; consistently produces better trees |
| Phylogenetic-tree input (single gene) | ClipKIT `smart-gap` | Default mode; dynamic threshold determination |
| HMM profile building (HMMER, HHsuite) | trimAl `-gappyout` (Capella-Gutierrez et al 2009 Bioinf) | Aggressive gap removal acceptable; profile quality benefits |
| Selection / dN/dS analysis (PAML, HyPhy) | TCS column masking or GUIDANCE2 (NOT aggressive trimming) | Removing columns causes false-positive selection signals (Fletcher & Yang 2010 MBE) |
| Deep prokaryotic phylogenomics | BMGE (Criscuolo & Gribaldo 2010 BMC Evol Biol) | Entropy-based with BLOSUM62 context; standard in GToTree pipeline |
| Cross-contaminated sequences | HMMcleaner (Di Franco et al 2019 BMC Evol Biol) | Per-residue cleaning; targets contamination not column quality |
| Preserve phylogenetic signal in indels | Divvier (Ali, Bogusz & Whelan 2019 MBE) | Splits ambiguous columns rather than removing them |
| Column-mapping retention for site analysis | trimAl `-colnumbering` | Outputs original-column indices for downstream cross-reference |
| Codon-aware trimming | MACSE `trimAlignment` (Ranwez et al 2018 MBE) | Preserves codon boundaries; pairs with MACSE codon MSA |

## ClipKIT Modes

Pick a `-m` mode by what the downstream task needs the alignment to KEEP. Run `clipkit --help` for the full list of 15 modes.

| Pick this mode | When |
|----------------|------|
| `kpic-smart-gap` | Publication-grade phylogenomics on concatenated supermatrices (recommended default) |
| `smart-gap` | Single-gene tree input or unbalanced datasets where `kpic` over-trims outgroups |
| `gappy` / `gappyout` | Need an explicit gap threshold or trimAl-equivalent behaviour |
| `kpi-smart-gap` | Maximum-parsimony tree input (drops constant sites) |
| `c3` / `cst` / `entropy` / `block-gappy` / `composition-bias` / `heterotachy` | Specialist needs: third-codon stripping, manual masks, entropy thresholding, conserved-block preservation, long-branch mitigation, or heterotachy filtering -- consult `clipkit --help` |

**Goal:** Run ClipKIT on an MSA with the mode appropriate to the downstream goal.

**Approach:** Pick a `-m` mode from the table above, optionally enable `--log` for reproducibility, and write the trimmed alignment in the desired format.

```bash
clipkit input.fasta -m kpic-smart-gap -o trimmed.fasta
clipkit input.fasta -m gappy -g 0.9 -o trimmed.fasta
clipkit input.fasta -m kpic-smart-gap --output-format phylip -o trimmed.phy
clipkit input.fasta -m kpic-smart-gap --log -o trimmed.fasta
```

The `--log` flag produces a per-column kept/removed log -- essential for reproducibility audits. ClipKIT also has a Python API (`clipkit.api.clipkit`) for in-memory trimming.

### ClipKIT kpic Failure Modes

`kpic` defines parsimony-informative as "at least 2 sequences with each of at least 2 different residues". On taxonomically unbalanced datasets (e.g. 95 close relatives + 5 outgroups), columns informative WITHIN the dominant clade look informative GLOBALLY, while columns that distinguish the outgroup from the dominant clade may have a single residue in the outgroup and fail kpic. Result: the trimmed alignment is biased toward the dominant clade's signal. Mitigations:
- Use `kpic-smart-gap` AND verify outgroup branch length is preserved before vs after trimming
- For unbalanced datasets, consider `smart-gap` (no kpic constraint) or sequence-weight-aware trimming (no production tool exists; manual subsampling to balance clades is the practical fix)
- ClipKIT does NOT use Henikoff-style sequence weighting; the count-based informativeness is unweighted (Steenwyk et al 2020 supplement)

For bias-aware trimming, BMGE's entropy thresholding with `-w` window weighting (default 3) is partially weighted but not by clade structure. ClipKIT GitHub issues #71 and #88 document the unbalanced-dataset failure.

## trimAl Modes

Pick a trimAl mode by downstream tool. `-gappyout` for HMM profile builds, `-strictplus` for phylogenetic tree input, `-automated1` only when audit-grade reproducibility is not required (heuristic has changed across point releases).

| Mode | Flag | Description |
|------|------|-------------|
| Automated heuristic | `-automated1` | Picks `gappyout`, `strict`, or `strictplus` based on alignment characteristics |
| Gap-only | `-gappyout` | Automatic gap-fraction threshold from gap distribution |
| Strict | `-strict` | Combined gap + similarity criterion; recommended for phylogenetics |
| Strict-plus | `-strictplus` | Stricter; ~50% more aggressive than `-strict` |
| Manual gap | `-gt 0.5` | Remove columns with > 50% gaps (set fraction explicitly) |
| Manual similarity | `-st 0.5` | Remove columns with similarity below threshold |
| Manual conservation | `-cons 60` | Keep at least 60% of original columns regardless of other criteria |
| Sequence-quality | `-resoverlap 0.8 -seqoverlap 75` | Remove sequences with poor residue/sequence overlap |
| HTML report | `-htmlout report.html` | Visual diff of kept/removed columns |
| Column mapping | `-colnumbering` | Output original column indices preserved |

**Goal:** Trim an MSA with trimAl using a heuristic or manual threshold suited to the downstream tool.

**Approach:** Select an automated mode (`-automated1`, `-gappyout`, `-strictplus`) for typical use, or compose `-gt`, `-st`, `-cons` thresholds for manual control; export an HTML diff or column index mapping when audit-grade reproducibility is required.

```bash
trimal -in input.fasta -out trimmed.fasta -automated1
trimal -in input.fasta -out trimmed.fasta -gappyout
trimal -in input.fasta -out trimmed.fasta -strictplus -htmlout report.html
trimal -in input.fasta -out trimmed.fasta -gt 0.3 -st 0.5 -cons 60 -colnumbering > columns.txt
```

`-gappyout` is the recommended choice for HMM profile building (HMMER `hmmbuild` benefits from aggressive gap removal). `-strictplus` is recommended for phylogenetic tree input. `-automated1` is the safe default when characterising the dataset is impractical.

**Reproducibility note:** `trimAl -automated1` selects between `gappyout`, `strict`, and `strictplus` via internal heuristics that have changed between point releases (1.4 -> 1.4.1 -> 2.0-rc). For audit-grade reproducibility, do NOT use `-automated1`; specify the underlying mode explicitly. Record `trimal --version` in pipeline manifests. trimAl 2.0 (in development) is expected to change defaults; until release, pin to 1.4.1 in production environments.

## BMGE: Block Mapping and Gathering with Entropy

Use BMGE for deep prokaryotic phylogenomics (the GToTree default) or whenever entropy-based, matrix-aware column filtering is preferred over gap-only heuristics.

**Goal:** Filter MSA columns by matrix-aware entropy and gap-rate thresholds, particularly for deep prokaryotic phylogenomics.

**Approach:** Invoke BMGE.jar with `-t` (sequence type) and tune `-h` (entropy) and `-g` (gap rate) against the divergence depth of the dataset; recalibrate `-h` if the substitution matrix is changed via `-m`.

```bash
java -jar BMGE.jar -i input.fasta -t AA -of trimmed.fasta -h 0.5 -g 0.2

java -jar BMGE.jar -i input.fasta -t DNA -of trimmed.fasta -m DNAPAM100:2 -h 0.5
```

| Flag | Default | Meaning |
|------|---------|---------|
| `-h` | 0.5 | Entropy threshold (lower = more aggressive trimming) |
| `-g` | 0.2 | Gap rate threshold |
| `-m` | BLOSUM62 (AA) | Substitution matrix for entropy weighting |
| `-t` | -- | Required: AA, CODON, or DNA |
| `-b` | 5 | Minimum block size |

`-h 0.4` is the recommended setting for deep phylogenomics where conservation is low; `-h 0.6` retains more sites for shallower phylogenies.

**Matrix-aware threshold:** BMGE computes entropy weighted by the chosen substitution-matrix probabilities. The `-h 0.5` and `-h 0.4` thresholds are calibrated for BLOSUM62 (default). Switching to `-m BLOSUM30` (deep phylogenomics) makes the same numeric `-h` more permissive; `-m BLOSUM90` (close orthologs) makes it more aggressive. When using a non-default matrix, recalibrate by running on a known-good benchmark before applying.

## Divvier: Column Splitting Instead of Removal

Use Divvier when phylogenetic signal in indels matters and pure removal would discard block-boundary information; it splits ambiguous columns rather than dropping them.

```bash
# Divvier ships as a compiled binary; invoke as ./divvier or `divvier` if on PATH
./divvier -divvy input.fasta

./divvier -partial -mincol 4 -divvygap input.fasta
```

`-divvy` (default) outputs `input.fasta.divvy.fas` (full divvying); `-partial` only filters individual ambiguous characters. `-mincol N` sets the minimum number of confident characters required to keep a split column (integer count, default 2). `-divvygap` writes gaps instead of asterisks for phylogenetics-tool compatibility. Divvier is particularly useful when input alignments have many short conserved blocks separated by ambiguous regions -- removing the regions discards information about block boundaries that splitting preserves.

Maintenance note: Divvier's last release was 2019 (`simonwhelan/Divvier`); the tool is no longer actively maintained but results remain reproducible with the v2019 binary.

## HMMcleaner: Per-Residue Cleaning

Run HMMcleaner before column trimming when cross-contamination or annotation errors are suspected; it masks suspect residues with `X` rather than removing columns. Apply only to alignments with >= 15 sequences (below that the per-residue pHMM has too little signal and over-flags divergent residues).

```bash
HmmCleaner.pl input.fasta
HmmCleaner.pl input.fasta --no-large-remove
```

Output is `input_hmm.fasta` with low-confidence residues masked. Used in OrthoMaM and Compositional Heterogeneity-aware phylogenomic pipelines where cross-contamination from sequencing or annotation errors is suspected.

**Sample-size sensitivity:** HMMcleaner builds a per-residue HMM from the OTHER sequences at each position, so on small alignments (<15 sequences) the HMM has insufficient signal and over-flags real divergent residues as contamination. Di Franco et al 2019 show two related effects: pHMMs built from few sequences carry less signal, lowering HMMcleaner sensitivity, and its false positives are driven mainly by evolutionary divergence -- specificity falls with gap frequency, evolutionary rate, and the fraction of ambiguously-aligned regions rather than by a fixed sequence count (global specificity ~94% at default settings). OrthoMaM v11 and PhyloHerb pipelines apply HMMcleaner only to alignments with >= 15 sequences. For smaller alignments, manual inspection or BLAST-based contamination screening is more reliable.

## Gblocks: The Legacy Default

Use Gblocks only when matching a legacy pipeline; prefer ClipKIT or trimAl for new work. Default parameters are too aggressive -- always relax with `-b1=50% -b2=85% -b3=10 -b4=5 -b5=h`.

```bash
Gblocks input.fasta -t=p -b1=50% -b2=85% -b3=10 -b4=5 -b5=h
```

## PhyIN: Phylogenetic Incompatibility Trimming

PhyIN (Maddison 2024 PeerJ) is a complementary trimmer that flags neighbouring columns whose split patterns are phylogenetically incompatible (i.e. cannot share a tree). It targets a different failure mode than gap-based or entropy-based trimmers: ClipKIT, trimAl, and BMGE all evaluate columns independently, so a region with consistent gap structure passes their filters even if its character patterns are pairwise tree-incompatible (alignment artefact). PhyIN catches that case.

```bash
phyin input.fasta -o trimmed.fasta -w 5 -t 0.5
```

Use PhyIN as a SECOND-PASS trimmer after ClipKIT/trimAl when alignment artefact is the suspected source of incongruence in a phylogenomic dataset; not a replacement for first-pass column filtering. PhyIN's incompatibility test is signal-direction agnostic, so it does not distinguish "the alignment is wrong here" from "true incongruent locus" (e.g. introgression, ILS); only gene-tree comparison after tree-building can disambiguate. Reference: PeerJ 2024 paper.

## Decision Tree by Downstream Goal

```
What is the next step?
+- Phylogenetic ML tree (RAxML, IQ-TREE)
|  +- Concatenated supermatrix? -> ClipKIT kpic-smart-gap
|  +- Single gene? -> ClipKIT smart-gap or trimAl -automated1
|  +- Deep prokaryotic? -> BMGE -h 0.4 -g 0.2
|  +- Suspected cross-contamination? -> HMMcleaner first, then ClipKIT
|
+- Bayesian inference (MrBayes, BEAST)
|  +- Same as ML; trimming is acceptable but log column mapping
|
+- HMM profile (HMMER hmmbuild, HHsuite)
|  +- trimAl -gappyout (aggressive gap removal helps profile quality)
|
+- Selection analysis (PAML codeml, HyPhy)
|  +- DO NOT aggressively trim
|  +- Use TCS column masking (T-Coffee -evaluate) or GUIDANCE2
|  +- See alignment/multiple-alignment confidence assessment
|
+- Sequence logo / motif scan
   +- Light gap-only trim (trimAl -gt 0.5)
   +- Preserve all variable positions
```

## TCS Column Masking for Selection Analysis

TCS (Chang et al 2014 MBE) scores each column on a 0-9 scale by consistency across a pairwise-alignment library. The recommended dN/dS workflow:

**Goal:** Mask unreliable columns before selection analysis to prevent alignment errors from inflating false-positive dN/dS calls.

**Approach:** Build a library-rich consistency score via M-Coffee, evaluate the alignment against that library to obtain per-column TCS scores, then keep columns at or above a chosen confidence threshold using `seq_reformat`.

```bash
# 1. Generate library-rich consistency scores via M-Coffee (combines libraries from MAFFT, MUSCLE, ClustalW, ProbCons)
t_coffee input.fasta -mode mcoffee -output fasta_aln -outfile aligned.fasta

# 2. Compute per-column TCS scores against the same library
t_coffee -infile aligned.fasta -evaluate -output score_ascii > tcs_scores.ascii

# 3. Filter columns at a chosen threshold via seq_reformat (5-9 = retain columns scoring 5 or higher)
t_coffee -other_pg seq_reformat -in aligned.fasta -struc_in tcs_scores.ascii \
    -struc_in_f number_aln -action +keep '[5-9]' -output fasta_aln > aligned_tcs5.fasta
```

Threshold guidance: TCS >= 5 retains columns confidently aligned by the majority of library methods; TCS >= 7 is a stricter operational convention on the seq_reformat 0-9 display scale. Chang et al 2014 do not prescribe an integer 5/7 cutoff -- on BAliBASE 3 and PREFAB 4 structural benchmarks they keep residues scoring above ~0.6 on the native 0-1 scale and drop columns scoring below 2, with TCS outperforming GUIDANCE and HoT. TCS-from-mcoffee gives substantially better column-confidence ranking than TCS-from-default-tcoffee because the library is more diverse. For the PAML branch-site test, Fletcher & Yang 2010 showed alignment errors inflate false positives dramatically (up to ~0.99 with ClustalW, ~0.13 even with codon-aware PRANK) and that removing gappy columns did not reduce them; confidence-based column masking (TCS, GUIDANCE2) is a common mitigation but was not evaluated in that study, since TCS postdates it (Chang et al 2014).

## MACSE Frameshift Markers Need Post-Processing

MACSE encodes detected frameshifts as `!` (within-codon insertion) and `*` (premature stop) in the nucleotide output. PAML codeml interprets `!` as missing data; HyPhy `BUSTED`/`MEME` interpret `!` as `N` but `*` triggers a parse error mid-sequence. Standard cleanup before downstream analysis:

**Goal:** Convert MACSE frameshift and stop markers into formats that PAML and HyPhy will parse correctly.

**Approach:** Replace `!` with gaps for PAML, and use MACSE's own `exportAlignment` sub-program with `-codonForInternalStop NNN` for HyPhy-safe output.

```bash
# Convert frameshift markers to gaps; replace internal stops with NNN
sed -e 's/!/-/g' aligned_nt.fasta > aligned_paml.fasta
java -jar macse_v2.jar -prog exportAlignment -align aligned_nt.fasta \
    -codonForFinalStop --- -codonForInternalStop NNN \
    -out_NT aligned_hyphy.fasta -out_AA aligned_hyphy_aa.fasta
```

`-codonForInternalStop NNN` replaces internal stops with `NNN` (HyPhy-safe). Without this step, the dN/dS run silently produces results that do not correspond to the alignment shown.

## Aggressiveness Cap

Compute the retained-column fraction and warn if it drops below 0.7. Trimming more than 20-30% of columns rapidly degrades ML tree accuracy on empirical data.

```python
def trimming_fraction(input_alignment, trimmed_alignment):
    return trimmed_alignment.get_alignment_length() / input_alignment.get_alignment_length()
```

If retention drops below 0.7, switch to a less aggressive mode or accept the original alignment unfiltered.

## Column Mapping for Reproducibility

When trimming for phylogenetic input, retain the column-index mapping so downstream site-specific analyses (selection per site, structure-mapped residues, etc.) can be back-traced:

```bash
trimal -in input.fasta -out trimmed.fasta -automated1 -colnumbering > kept_columns.txt

clipkit input.fasta -m kpic-smart-gap --log -o trimmed.fasta
```

These two flags emit different formats. `trimal -colnumbering` writes a comma-separated list of the original column indices that survived (e.g. `0, 1, 2, 4, ...`) on stdout. `clipkit --log` writes a `<output>.log` file with one row per original column reporting `position\tkeep_or_trim\tsite_classification\tgap_proportion`. To compare runs across the two tools, parse each format separately and reconcile to a common "kept-column index list" before applying the index map for site-specific cross-reference.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| ClipKIT empty output | All columns failed `kpic` filter | Switch to `smart-gap` mode (less aggressive); check input for non-amino-acid characters |
| trimAl "all sequences are identical" | Input has duplicates with no variation | Remove duplicate sequences first |
| BMGE Java OutOfMemoryError | Default JVM heap too small | `java -Xmx16g -jar BMGE.jar` |
| Divvier crashes on large input | Memory limits | Run on per-gene alignments rather than concatenated supermatrices |
| HMMcleaner reports "no contamination" | Input alignment too small (< 5 sequences) | Pool more sequences or skip per-residue cleaning |
| Trimming removes 80%+ of columns | Mode too aggressive for divergent input | Switch to `kpic-gappy` or relaxed-parameter Gblocks |

## Related Skills

- alignment/multiple-alignment - Generate the input MSA before trimming; confidence assessment (GUIDANCE2, TCS, MUSCLE5 ensemble) for selection-analysis input
- alignment/msa-parsing - Parse the trimmed alignment; sequence weighting; coordinate mapping
- alignment/msa-statistics - Compute conservation and gap statistics to inform mode selection
- alignment/structural-alignment - Trim structural MSAs the same way as sequence MSAs
- phylogenetics/modern-tree-inference - Build trees from trimmed alignments

## References

- Steenwyk JL, Buida TJ, Li Y, Shen XX, Rokas A. 2020. ClipKIT: a multiple sequence alignment trimming software for accurate phylogenomic inference. PLOS Bio 18:e3001007.
- Capella-Gutierrez S, Silla-Martinez JM, Gabaldon T. 2009. trimAl: a tool for automated alignment trimming in large-scale phylogenetic analyses. Bioinf 25:1972-1973.
- Criscuolo A, Gribaldo S. 2010. BMGE: a new software for selection of phylogenetic informative regions from multiple sequence alignments. BMC Evol Biol 10:210.
- Maddison WP. 2024. PhyIN: trimming alignments by phylogenetic incompatibilities among neighbouring sites. PeerJ 12:e18504.
- Tan G, Muffato M, Ledergerber C, Herrero J, Goldman N, Gil M, Dessimoz C. 2015. Current methods for automated filtering of multiple sequence alignments frequently worsen single-gene phylogenetic inference. Syst Biol 64:778-791.
- Fletcher W, Yang Z. 2010. The effect of insertions, deletions, and alignment errors on the branch-site test of positive selection. MBE 27:2257-2267.
- Chang JM, Di Tommaso P, Notredame C. 2014. TCS: a new multiple sequence alignment reliability measure. MBE 31:1625-1637.
<!-- END FILE: alignment/alignment-trimming/SKILL.md -->

## 子目录：alignment/msa-parsing

<!-- BEGIN FILE: alignment/msa-parsing/SKILL.md -->
---
name: bio-alignment-msa-parsing
description: Parse and analyze multiple sequence alignments using Biopython. Extract sequences, identify conserved regions, analyze gaps, work with annotations, and manipulate alignment data for downstream analysis. Use when parsing or manipulating multiple sequence alignments.
tool_type: python
primary_tool: Bio.AlignIO
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# MSA Parsing and Analysis

Parse multiple sequence alignments to extract information, analyze content, and prepare for downstream analysis.

## Required Import

**Goal:** Load modules for parsing, analyzing, and manipulating multiple sequence alignments.

**Approach:** Import AlignIO for reading, Counter for column analysis, and alignment classes for constructing modified alignments.

```python
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from collections import Counter
import numpy as np
import pandas as pd
```

Optional for streaming and Easel-based weighting:
```python
import pyhmmer
```

## Loading Alignments

**Goal:** Read an MSA file and inspect its dimensions.

**Approach:** Use `AlignIO.read()` specifying the file and format.

```python
from Bio import AlignIO

alignment = AlignIO.read('alignment.fasta', 'fasta')
print(f'{len(alignment)} sequences, {alignment.get_alignment_length()} columns')
```

## Extracting Sequence Information

### Get All Sequence IDs
```python
seq_ids = [record.id for record in alignment]
```

### Get Sequences as Strings
```python
sequences = [str(record.seq) for record in alignment]
```

### Get Sequence by ID
```python
def get_sequence_by_id(alignment, seq_id):
    for record in alignment:
        if record.id == seq_id:
            return record
    return None

target = get_sequence_by_id(alignment, 'species_A')
```

### Access Descriptions and Annotations
```python
for record in alignment:
    print(f'ID: {record.id}')
    print(f'Description: {record.description}')
    print(f'Annotations: {record.annotations}')
```

## Column-wise Analysis

**Goal:** Analyze alignment content column by column to assess composition, conservation, and variability.

**Approach:** Use column indexing (`alignment[:, idx]`) and Counter to examine character frequencies at each position.

### Get Single Column
```python
column_5 = alignment[:, 5]  # Returns string of characters at position 5
print(column_5)  # e.g., 'AAAGA'
```

**API note:** `Bio.AlignIO` returns `MultipleSeqAlignment` objects whose `[:, idx]` returns a plain `str`; `[:, start:end]` returns another `MultipleSeqAlignment`. The newer `Bio.Align.Alignment` (from `Align.read` / `Align.parse`) uses numpy-backed slicing -- verify with `type(alignment[:, 0])` before assuming string methods work. For numpy-array access to the full alignment, use `np.array(alignment)`.

### Iterate and Count Columns
```python
for col_idx in range(alignment.get_alignment_length()):
    column = alignment[:, col_idx]
    counts = Counter(column)
```

### Find Conserved Positions
```python
def find_conserved_positions(alignment, threshold=1.0):
    conserved = []
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        counts = Counter(column)
        most_common_char, most_common_count = counts.most_common(1)[0]
        if most_common_char != '-':
            conservation = most_common_count / len(alignment)
            if conservation >= threshold:
                conserved.append((col_idx, most_common_char))
    return conserved

fully_conserved = find_conserved_positions(alignment, threshold=1.0)
mostly_conserved = find_conserved_positions(alignment, threshold=0.8)
```

## Gap Analysis

**Goal:** Quantify gap distribution across sequences and columns to identify problematic regions or sequences.

**Approach:** Count gap characters per sequence and per column, then identify positions exceeding a gap fraction threshold.

### Count Gaps Per Sequence
```python
gap_counts = [(record.id, str(record.seq).count('-')) for record in alignment]
for seq_id, gaps in gap_counts:
    print(f'{seq_id}: {gaps} gaps')
```

### Count Gaps Per Column
```python
def gaps_per_column(alignment):
    return [alignment[:, i].count('-') for i in range(alignment.get_alignment_length())]

gap_profile = gaps_per_column(alignment)
```

### Find Gappy Columns
```python
def find_gappy_columns(alignment, threshold=0.5):
    gappy = []
    num_seqs = len(alignment)
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        gap_fraction = column.count('-') / num_seqs
        if gap_fraction >= threshold:
            gappy.append(col_idx)
    return gappy

columns_to_remove = find_gappy_columns(alignment, threshold=0.5)
```

### Remove Gappy Columns
```python
def remove_gappy_columns(alignment, threshold=0.5):
    num_seqs = len(alignment)
    keep_columns = []
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        gap_fraction = column.count('-') / num_seqs
        if gap_fraction < threshold:
            keep_columns.append(col_idx)

    new_records = []
    for record in alignment:
        new_seq = ''.join(str(record.seq)[i] for i in keep_columns)
        new_records.append(SeqRecord(Seq(new_seq), id=record.id, description=record.description))
    return MultipleSeqAlignment(new_records)

cleaned = remove_gappy_columns(alignment, threshold=0.5)
```

## Alignment Trimming

Trimming controversy and tool selection (ClipKIT, trimAl, BMGE, Divvier, HMMcleaner, Noisy) is the subject of a dedicated skill. Use this short decision matrix for routing:

| Goal | First-line tool |
|------|-----------------|
| Phylogenetic-tree input | ClipKIT `kpic-smart-gap` (Steenwyk et al 2020 PLOS Bio) |
| HMM profile building | trimAl `-gappyout` (Capella-Gutierrez et al 2009 Bioinf) |
| Selection / dN/dS input | Avoid aggressive trimming; use TCS / GUIDANCE2 column masking |
| Deep prokaryotic phylogenomics | BMGE (Criscuolo & Gribaldo 2010 BMC Evol Biol) |
| Preserve column-mapping for residue-level analysis | trimAl `-colnumbering` |

See alignment/alignment-trimming for full mode comparisons, decision trees, and runnable examples.

## Gap Handling for Phylogenetics

How gaps are treated in downstream phylogenetic analysis significantly affects tree topology:

| Treatment | Method | Tradeoff |
|-----------|--------|----------|
| Missing data (default) | Gaps = unknown character | Most common; can be statistically inconsistent under ML |
| Fifth state | Gap = 5th nucleotide | Biologically problematic (gaps of different lengths treated equally) |
| Simple indel coding | Each unique indel coded as binary character | Most biologically realistic; adds phylogenetic signal |

For slow- to mid-rate datasets where indels are phylogenetically informative, prefer SIC indel coding or fifth-state treatment; for rapidly-evolving datasets (intra-species, ITS regions, retroelement-rich plant genomes), default to missing-data treatment because gap homology is unreliable. Run a sensitivity analysis comparing both treatments before drawing topological conclusions.

## Identifying Unreliable Alignment Regions

Columns exhibiting **both** high gap fraction AND low conservation are the strongest indicators of alignment uncertainty. These often reflect guide tree artifacts rather than true evolutionary events. Before phylogenetic analysis:

1. Flag columns with gap fraction >50%, which may be alignment artifacts
2. Check if gappy regions coincide with insertions in a single divergent sequence (remove that sequence and re-align)
3. For critical analyses, run GUIDANCE2 or MUSCLE5 ensemble to get per-column confidence scores; mask columns below the reliability threshold (default: 0.93 for GUIDANCE2)

## Consensus Sequence

**"Get consensus sequence"** -> Derive a single representative sequence from an MSA based on majority-rule voting at each column.

**Goal:** Generate a consensus sequence from the alignment using a frequency threshold.

**Approach:** At each column, select the most common non-gap character if it exceeds the threshold; otherwise mark as ambiguous.

### Simple Majority Consensus
```python
def consensus_sequence(alignment, threshold=0.5, gap_char='-', ambiguous='N'):
    consensus = []
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        counts = Counter(column)
        most_common_char, most_common_count = counts.most_common(1)[0]
        if most_common_char == gap_char:
            counts.pop(gap_char, None)
            if counts:
                most_common_char, most_common_count = counts.most_common(1)[0]
            else:
                most_common_char = gap_char

        if most_common_count / len(alignment) >= threshold:
            consensus.append(most_common_char)
        else:
            consensus.append(ambiguous)
    return ''.join(consensus)

consensus = consensus_sequence(alignment, threshold=0.5)
```

### Note on Bio.Align.AlignInfo
The `AlignInfo.SummaryInfo` class is deprecated in recent Biopython versions. The custom `consensus_sequence()` function above is the recommended approach. When deprecation warnings appear from `AlignInfo`, callers should switch to the custom implementation.

## Extracting Regions

### Slice by Column Range
```python
region = alignment[:, 100:200]  # Columns 100-199
```

### Slice by Sequence Range
```python
subset = alignment[0:10]  # First 10 sequences
```

### Extract Ungapped Regions from Reference
```python
def extract_ungapped_regions(alignment, ref_idx=0):
    ref_seq = str(alignment[ref_idx].seq)
    ungapped_cols = [i for i, char in enumerate(ref_seq) if char != '-']

    new_records = []
    for record in alignment:
        new_seq = ''.join(str(record.seq)[i] for i in ungapped_cols)
        new_records.append(SeqRecord(Seq(new_seq), id=record.id, description=record.description))
    return MultipleSeqAlignment(new_records)

ungapped = extract_ungapped_regions(alignment, ref_idx=0)
```

## Sequence Filtering

**Goal:** Subset an alignment to retain only sequences matching specific criteria (ID pattern, gap content, uniqueness).

**Approach:** Iterate over alignment records, apply filter conditions, and reconstruct a new MultipleSeqAlignment from matching records.

```python
import re

def filter_by_id(alignment, pattern):
    regex = re.compile(pattern)
    return MultipleSeqAlignment([r for r in alignment if regex.search(r.id)])

def filter_by_gap_content(alignment, max_gap_fraction=0.1):
    return MultipleSeqAlignment(
        [r for r in alignment if str(r.seq).count('-') / len(r.seq) <= max_gap_fraction]
    )

def remove_duplicates(alignment):
    seen = set()
    return MultipleSeqAlignment([r for r in alignment if not (str(r.seq) in seen or seen.add(str(r.seq)))])
```

## Working with Annotations

Stockholm-derived alignments expose secondary-structure markup, per-column GC/GR annotations, and per-sequence metadata via `record.annotations`, `record.letter_annotations`, and `alignment.column_annotations`. See usage-guide.md "Working with Annotations" for the full access pattern.

## Position Mapping

**Goal:** Convert between alignment column coordinates and ungapped sequence coordinates.

**Approach:** For one-off lookups, walk the sequence tracking gap characters. For repeated queries on the same sequence, vectorize with `numpy.cumsum` over a gap-mask -- O(L) preprocessing, O(1) lookups.

### Vectorized Coordinate Mapping (Recommended)

```python
import numpy as np

def coordinate_map(record):
    chars = np.frombuffer(str(record.seq).encode('ascii'), dtype=np.uint8)
    is_residue = chars != ord('-')
    seq_to_aln = np.flatnonzero(is_residue)
    aln_to_seq = np.where(is_residue, np.cumsum(is_residue) - 1, -1)
    return seq_to_aln, aln_to_seq

seq_to_aln, aln_to_seq = coordinate_map(alignment[0])
column_for_residue_42 = seq_to_aln[42]
residue_at_column_100 = aln_to_seq[100]
```

`aln_to_seq[i] == -1` indicates a gap at alignment column `i`. This pattern handles 1 M-site genomic alignments in milliseconds compared to the loop-based version's seconds.

For single lookups without numpy, walk the sequence tracking a counter (`seq_pos += 1` for each non-`-` char). The vectorized form above subsumes both directions.

### Mapping Alignment Columns to PDB Residues

A column-to-PDB mapping requires THREE coordinate systems: alignment column -> SEQRES residue (ungapped FASTA) -> ATOM residue (resolved structure). The SEQRES-to-ATOM map is non-trivial because PDB structures have unmodelled loops, N-terminal tags, engineered mutations, and seleno-substitutions. Conservation scores mapped via the bare alignment-to-SEQRES path will be off-by-many residues whenever the structure has missing density. For SEQRES/ATOM extraction and the authoritative `_pdbx_poly_seq_scheme` mapping, see `structural-biology/structure-navigation`.

## Sequence Weighting and Neff

Compute sequence weights before any column-wise statistic on phylogenetically structured datasets (lots of closely-related sequences plus a few outliers); without weighting, every per-column metric is biased toward the over-represented clades.

### Henikoff Sequence Weights

**Goal:** Give each sequence a weight that reflects its non-redundant contribution.

**Approach:** Each column `c` contributes `1 / (k_c * n_{s,c})` to sequence `s`, where `k_c` is the number of distinct residues at column `c` and `n_{s,c}` is the count of `s`'s residue at that column (Henikoff & Henikoff 1994 JMB).

```python
def henikoff_weights(alignment):
    seq_array = np.array([list(str(r.seq)) for r in alignment])
    weights = np.zeros(len(alignment))
    for col_idx in range(seq_array.shape[1]):
        residues, inverse, counts = np.unique(seq_array[:, col_idx], return_inverse=True, return_counts=True)
        if '-' in residues:
            continue
        weights += 1.0 / (len(residues) * counts[inverse])
    return weights / weights.sum()
```

Full implementation: `examples/henikoff_weights.py`.

**Edge case:** The implementation skips columns containing any gap, so sequences whose non-gap residues fall ONLY in gap-rich columns receive weight zero. This typically affects fragmentary or terminal-truncated sequences. HMMER's `pb` weighting handles this by including gaps as a residue type. For Pfam-style alignments where many columns are gappy, switch to `pyhmmer.easel.MSAFile` + `compute_weights(method='pb')` rather than this implementation, or augment the pure-numpy version with an `ignore_gaps=False` branch.

### Effective Sequence Number (Neff)

**Goal:** Estimate effective non-redundant sequence count after similarity-based clustering.

**Approach:** Cluster sequences at an identity threshold (HMMER and AlphaFold use 0.62 for protein, 0.80 for nucleotide), assign each sequence weight `1 / cluster_size`, and sum. `Neff/L > 0.5` is the rule-of-thumb threshold for direct-coupling-analysis contact prediction. Full implementation: `examples/neff.py`.

The thresholds reflect convention: 0.62 traces back to BLOSUM62 derivation; 0.80 is HHsuite's default for cd-hit-style clustering of the BFD database.

**Neff is estimator-dependent.** Different tools report different "Neff" values for the same MSA, often differing by 2-3x:

| Tool | Method | Typical relationship |
|------|--------|---------------------|
| HMMER, pyhmmer (`method='pb'`) | Henikoff position-based | Baseline |
| HMMER (`method='gsc'`) | Gerstein-Sonnhammer-Chothia | ~0.5-1.5x of `pb` |
| HMMER (`method='blosum'`) | BLOSUM62-similarity clusters | ~0.7-1.2x of `pb` |
| AlphaFold2 / ColabFold | MMseqs2 cluster count at id=0.62 | ~1.5-3x of `pb` (counts unique sequences, not weights) |
| EVcouplings | HHfilter clusters at id=0.80 | ~0.5-1x of `pb` |
| HHsuite `hhmake` | inverse-purity count | Closer to `pb` |

Always report which estimator was used. Threshold rules ("Neff/L > 0.5 for DCA") are calibrated against a specific estimator -- Hopf et al 2017 use HHfilter-80 cluster count; Marks et al 2011 use 70%-identity cluster reweighting. AlphaFold2's MSA-depth gating uses unweighted cluster count at 62% identity.

## Coevolution: Mutual Information with APC

**Goal:** Identify columns whose residue identities co-vary, indicating direct or indirect physical/functional coupling.

**Approach:** Compute pairwise mutual information across column pairs, then subtract the average-product correction (APC) from Dunn, Wahl & Gloor (2008 Bioinf) to remove per-column-entropy and phylogenetic background. This is the foundation of plmDCA and EVcouplings; full DCA needs Potts-model inference but APC-corrected MI runs in pure numpy and is informative on its own.

Skeleton (full implementation: `examples/mi_apc.py`):
```python
def mi_matrix_apc(alignment):
    # Compute pairwise MI across columns -> column_means -> APC = outer(means) / overall_mean
    # Return mi - apc
    ...
```

For production-grade contact prediction, switch to plmDCA (Ekeberg et al 2013 Phys Rev E) or EVcouplings (Hopf et al 2017 Nat Biotechnol). APC-corrected MI scales to a few hundred columns; deeper analyses need approximate likelihood methods.

**APC over-correction on short alignments:** APC subtracts each column-pair's product of column-average MIs. For alignments with <100 columns, the column-averages are noisy estimates dominated by their constituent column-pairs, and APC removes signal proportional to noise. Empirically on Pfam alignments <100 columns, APC-corrected MI underperforms raw MI for contact prediction (Cocco et al 2018 Rep Prog Phys review). Apply APC only when L > 100 and Neff/L > 1; below this, raw MI plus a phylogenetic-distance threshold is more reliable. plmDCA and EVcouplings auto-skip APC when input depth is insufficient.

## A2M / A3M Conventions

A2M (HMMER) and A3M (HHsuite, ColabFold) encode insert vs match columns via case (uppercase = match column residue, lowercase = insert). A3M does not pad inserts across sequences and must be reformatted to A2M before loading as a rectangular MSA. See `alignment/alignment-io` A2M / A3M Conventions section for the full character table, BioPython load pattern, and the `reformat.pl` reference-sequence pitfall.

## Streaming Large Alignments

For Pfam-scale streaming (multi-gigabyte Stockholm or A3M databases that exceed RAM), use `pyhmmer.easel.MSAFile` with `compute_weights(method='pb')` for in-flight Henikoff weighting. See `alignment/alignment-io` Streaming Large Stockholm Databases section for the full code pattern.

## Quick Reference: Common Operations

| Task | Code |
|------|------|
| Get column | `alignment[:, col_idx]` |
| Get sequence | `alignment[seq_idx]` |
| Column count | `alignment.get_alignment_length()` |
| Sequence count | `len(alignment)` |
| Find gaps | `str(record.seq).count('-')` |
| Consensus | Use custom `consensus_sequence()` function |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `IndexError` | Column index out of range | Check `get_alignment_length()` |
| Unequal sequence lengths | Invalid MSA | Ensure all sequences same length |
| Empty Counter | All gaps in column | Handle gap-only columns |

## Related Skills

- alignment/multiple-alignment - Run MSA tools (MAFFT, MUSCLE5, ClustalOmega) to generate alignments
- alignment/alignment-io - Read/write alignment files in various formats
- alignment/pairwise-alignment - Create pairwise alignments
- alignment/msa-statistics - Calculate conservation metrics
- alignment/alignment-trimming - ClipKIT, trimAl, BMGE, Divvier modes and decision trees
- alignment/structural-alignment - Twilight-zone alternative when sequence MSA is unreliable
- phylogenetics/modern-tree-inference - Build trees from processed alignments

## References

- Henikoff S, Henikoff JG. 1994. Position-based sequence weights. JMB 243:574-578.
- Dunn SD, Wahl LM, Gloor GB. 2008. Mutual information without the influence of phylogeny or entropy dramatically improves residue contact prediction. Bioinf 24:333-340.
- Ekeberg M, Lovkvist C, Lan Y, Weigt M, Aurell E. 2013. Improved contact prediction in proteins: using pseudolikelihoods to infer Potts models. Phys Rev E 87:012707.
- Hopf TA, Ingraham JB, Poelwijk FJ, Scharfe CPI, Springer M, Sander C, Marks DS. 2017. Mutation effects predicted from sequence co-variation. Nat Biotechnol 35:128-135.
- Eddy SR. 2011. Accelerated profile HMM searches. PLOS CB 7:e1002195.
- Larralde M et al. 2023. PyHMMER: a Python library binding to HMMER for efficient sequence analysis. Bioinf 39:btad214.
- Cocco S et al. 2018. Inverse statistical physics of protein sequences: a key issues review. Rep Prog Phys 81:032601.
- Marks DS et al. 2011. Protein 3D structure computed from evolutionary sequence variation. PLOS One 6:e28766.
- Jumper J et al. 2021. Highly accurate protein structure prediction with AlphaFold. Nature 596:583-589.
- Simmons MP, Ochoterena H. 2000. Gaps as characters in sequence-based phylogenetic analyses. Syst Biol 49:369-381.
- Mueller K. 2006. Incorporating information from length-mutational events into phylogenetic analysis. Mol Phylogenet Evol 38:667-676.
- Dwivedi B, Gadagkar SR. 2009. Phylogenetic inference under varying proportions of indel-induced alignment gaps. BMC Evol Biol 9:211.
- Velankar S et al. 2013. SIFTS: structure integration with function, taxonomy and sequences resource. NAR 41:D483-D489.
<!-- END FILE: alignment/msa-parsing/SKILL.md -->

## 子目录：alignment/msa-statistics

<!-- BEGIN FILE: alignment/msa-statistics/SKILL.md -->
---
name: bio-alignment-msa-statistics
description: Calculate alignment statistics including sequence identity, conservation scores, substitution matrices, and similarity metrics. Use when comparing alignment quality, measuring sequence divergence, and analyzing evolutionary patterns.
tool_type: python
primary_tool: Bio.Align
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# MSA Statistics

Calculate sequence identity, conservation scores, substitution counts, and other alignment metrics.

## Required Import

**Goal:** Load modules for alignment I/O, substitution scoring, and statistical calculations.

**Approach:** Import AlignIO for reading alignments, Counter for column analysis, numpy for matrix operations, and math for entropy calculations.

```python
from Bio import AlignIO
from Bio.Align import substitution_matrices
from collections import Counter
import numpy as np
import math
```

## Pairwise Identity

**"Calculate percent identity"** -> Compute the fraction of identical aligned residues between sequence pairs.

**Goal:** Measure sequence similarity as percent identity for individual pairs or across all sequences in an alignment.

**Approach:** Count matching non-gap positions divided by total aligned positions; optionally compute a full N-by-N identity matrix.

### Percent Identity Definitions

There are four common denominators, producing **up to 11.5% difference** on the same alignment. Combined with different alignment algorithms, variation reaches 22%. Always report which method was used.

| Method | Denominator | Code |
|--------|-------------|------|
| PID1 | Aligned positions including internal gaps | `sum(a != '-' or b != '-' for a, b in zip(s1, s2))` |
| PID2 | Aligned residue pairs only (no gaps) | `sum(a != '-' and b != '-' for a, b in zip(s1, s2))` |
| PID3 | Shorter sequence length (ungapped) | `min(len(s1.replace('-', '')), len(s2.replace('-', '')))` |
| PID4 | Mean sequence length (ungapped) | `(len(s1.replace('-', '')) + len(s2.replace('-', ''))) / 2` |

PID2 always gives the highest value; PID4 correlates best with structural similarity (Raghava & Barton 2006 BMC Bioinf, r=0.86 with STAMP's Sc score) and is recommended for evolutionary analyses.

**Length-asymmetry pathology:** When sequences differ greatly in length, PID4 and PID2 diverge sharply. Example: 80 matches between a 500-residue protein and a 100-residue domain fragment yields PID2 ~84% (matches over aligned residue pairs) but PID4 ~27% (matches over mean ungapped length). Neither is wrong; they answer different questions:
- PID2 -> "how similar is the aligned region?" (motif/domain detection)
- PID4 -> "how similar are the full sequences?" (structural similarity benchmarks)

For ortholog identification at the protein level (full-length, similar size), PID4 is recommended. For domain detection or fragment-vs-genome alignment, PID2 with explicit length annotation is more interpretable. Always report alignment length alongside any percent identity to disambiguate.

### Calculate Identity Between Two Sequences
```python
def pairwise_identity(seq1, seq2, method='pid1'):
    matches = sum(a == b and a != '-' for a, b in zip(seq1, seq2))
    if method == 'pid1':
        denom = sum(a != '-' or b != '-' for a, b in zip(seq1, seq2))
    elif method == 'pid2':
        denom = sum(a != '-' and b != '-' for a, b in zip(seq1, seq2))
    elif method == 'pid3':
        denom = min(len(seq1.replace('-', '')), len(seq2.replace('-', '')))
    elif method == 'pid4':
        denom = (len(seq1.replace('-', '')) + len(seq2.replace('-', ''))) / 2
    return matches / denom if denom > 0 else 0

alignment = AlignIO.read('alignment.fasta', 'fasta')
seq1, seq2 = str(alignment[0].seq), str(alignment[1].seq)
for method in ['pid1', 'pid2', 'pid3', 'pid4']:
    print(f'{method}: {pairwise_identity(seq1, seq2, method) * 100:.1f}%')
```

### Identity Matrix for All Sequences

The double-loop is O(N^2 * L) and fine for hundreds of sequences; for thousands, vectorize via numpy broadcasting:

```python
def identity_matrix_vectorized(alignment):
    # Build N x L character array; for each row, broadcast equality and validity masks against all rows
    ...
```

Full implementation: `examples/identity_matrix.py`. For very large alignments (>10k sequences), switch to k-mer-based distance estimation (e.g. mash) -- exact pairwise identity becomes prohibitive.

## Conservation Scoring Methods

Pick a conservation score by what the downstream task needs:

| Pick this | When |
|-----------|------|
| Majority fraction or Shannon entropy | Quick screening; DNA/RNA logos; coarse column QC |
| Capra-Singh JSD (modern default) | Catalytic-residue / functional-site prediction on protein MSAs |
| ConSurf rate4site | PDB surface mapping when a phylogenetic tree is available |

## Conservation Score

**Goal:** Quantify per-column and overall alignment conservation to identify conserved and variable regions.

**Approach:** Calculate the fraction of the most common residue at each column, optionally ignoring gaps, and smooth with a sliding window.

### Per-Column Conservation
```python
def column_conservation(alignment, col_idx, ignore_gaps=True):
    column = alignment[:, col_idx]
    if ignore_gaps:
        column = column.replace('-', '')
    if not column:
        return 0.0
    counts = Counter(column)
    most_common_count = counts.most_common(1)[0][1]
    return most_common_count / len(column)

alignment = AlignIO.read('alignment.fasta', 'fasta')
for i in range(min(20, alignment.get_alignment_length())):
    cons = column_conservation(alignment, i)
    print(f'Column {i}: {cons*100:.0f}% conserved')
```

### Average Conservation Across Alignment
```python
def average_conservation(alignment, ignore_gaps=True):
    scores = []
    for col_idx in range(alignment.get_alignment_length()):
        scores.append(column_conservation(alignment, col_idx, ignore_gaps))
    return sum(scores) / len(scores)

avg_cons = average_conservation(alignment)
print(f'Average conservation: {avg_cons*100:.1f}%')
```

### Conservation Profile
```python
def conservation_profile(alignment, window=10):
    profile = []
    for i in range(alignment.get_alignment_length()):
        start = max(0, i - window // 2)
        end = min(alignment.get_alignment_length(), i + window // 2)
        scores = [column_conservation(alignment, j) for j in range(start, end)]
        profile.append(sum(scores) / len(scores))
    return profile

profile = conservation_profile(alignment, window=10)
```

### Capra-Singh Jensen-Shannon Divergence

**Goal:** Score columns by divergence from a residue-frequency background, with a window-smoothed neighbour penalty for catalytic residue prediction.

**Approach:** Compute JSD between the column distribution and a residue-frequency background (Capra & Singh 2007 Bioinf used BLOSUM62-derived; the example uses Robinson & Robinson 1991 PNAS, which gives effectively-equivalent column ranking), then mix with the windowed-neighbour mean. Defaults `window=3`, `lambda_window=0.5` track catalytic-residue annotation in the Catalytic Site Atlas. Full implementation: `examples/capra_singh_jsd.py`.

```python
def capra_singh_score(alignment, background=None, window=3, lambda_window=0.5):
    # raw[i] = JSD(column_i, background) * (1 - gap_fraction_i)   # gap-penalty per Capra-Singh reference impl
    # smoothed[i] = (1 - lambda) * raw[i] + lambda * mean(raw[i-window:i+window+1] excluding i)
    ...
```

**Threshold for catalytic-residue prediction:** Capra & Singh 2007 (Bioinf 23:1875) report AUC ~0.94 and Top-30 score ~0.75 on the Catalytic Site Atlas using JSD with neighbor mixing (window=3, lambda=0.5); the paper does not prescribe a single threshold. Choose by ROC tradeoff for the specific use case. ConSurf-derived rate4site (rate-of-evolution) is competitive but requires a phylogenetic tree; Capra-Singh JSD is the alignment-only equivalent.

## Substitution Counts

**Goal:** Tabulate observed substitution frequencies from the alignment for evolutionary analysis or custom scoring matrices.

**Approach:** Enumerate all pairwise non-gap character comparisons at each column and tally substitution pairs.

### Count Substitutions from Alignment

```python
def substitution_counts(alignment):
    # Tally pairwise non-gap residue mismatches across all column-pair comparisons
    ...
```

Full implementation: `examples/substitution_counts.py`. The script also reports Ti/Tv ratio for DNA alignments.

### Built-in Pairwise Substitutions

For pairwise alignments created with `PairwiseAligner`, use the `.substitutions` property:

```python
from Bio.Align import PairwiseAligner
aligner = PairwiseAligner(mode='global', match_score=1, mismatch_score=-1)
print(aligner.align(seq1, seq2)[0].substitutions)
```

### BLOSUM62 Lambda Is Not a Single Number

Different tools calibrate Karlin-Altschul lambda differently (NCBI BLAST tabulates 0.3176; FASTA/SSEARCH recomputes per query; HMMER `phmmer` derives it via Forward calibration; Bio.Align does not implement Karlin-Altschul). Expect ~2% bit-score variation across tools on the same alignment. Always record tool and version when citing bit scores; for borderline (~30 bit) hits this matters.

## Information Content

**Goal:** Measure column variability using Shannon entropy and derive information content for identifying functionally important positions.

**Approach:** Compute Shannon entropy from character frequencies per column; information content is max entropy minus observed entropy.

### Shannon Entropy Per Column
```python
import math

def shannon_entropy(column, ignore_gaps=True):
    if ignore_gaps:
        column = column.replace('-', '')
    if not column:
        return 0.0
    counts = Counter(column)
    total = len(column)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

alignment = AlignIO.read('alignment.fasta', 'fasta')
for i in range(min(20, alignment.get_alignment_length())):
    column = alignment[:, i]
    ent = shannon_entropy(column)
    print(f'Column {i}: entropy = {ent:.2f} bits')
```

### Information Content (Kullback-Leibler Divergence)

The classic uniform-background formulation `IC = log2(alphabet_size) - H` (Schneider & Stephens 1990 NAR) is only valid when the genomic background is uniform. This is approximately true for random DNA but emphatically wrong for protein, where amino acid frequencies range from 1.4% (Trp) to 9.4% (Leu). For amino acids, use Kullback-Leibler divergence `IC = sum_i p_i * log2(p_i / b_i)` against the Robinson & Robinson 1991 PNAS empirical background. Full implementation: `examples/entropy_analysis.py`.

```python
ROBINSON_BACKGROUND = {
    'A': 0.0780, 'R': 0.0512, 'N': 0.0427, 'D': 0.0530, 'C': 0.0193,
    'Q': 0.0419, 'E': 0.0629, 'G': 0.0738, 'H': 0.0224, 'I': 0.0526,
    'L': 0.0922, 'K': 0.0596, 'M': 0.0224, 'F': 0.0399, 'P': 0.0508,
    'S': 0.0712, 'T': 0.0584, 'W': 0.0133, 'Y': 0.0327, 'V': 0.0653,
}
DNA_UNIFORM = {'A': 0.25, 'C': 0.25, 'G': 0.25, 'T': 0.25}

def information_content(column, background, ignore_gaps=True):
    if ignore_gaps:
        column = column.replace('-', '')
    if not column:
        return 0.0
    counts = Counter(column)
    total = len(column)
    return sum((c / total) * math.log2((c / total) / background.get(r, 1e-9))
               for r, c in counts.items() if c > 0)
```

For sequence-logo letter heights, use the Schneider-Stephens form (`letter_height = p_i * (log2(alphabet) - H_observed)`, uniform background) when the comparison is "informative vs random"; use the KL form (against an empirical background such as Robinson-Robinson 1991) for protein logos where amino-acid frequencies are non-uniform or when the comparison is "informative vs the proteome". When the background is unknown, default to the empirical alignment composition rather than uniform.

## Gap Statistics

**Goal:** Summarize gap distribution across the alignment to assess alignment quality and identify problematic regions.

**Approach:** Calculate gap fractions per column and aggregate statistics including total gaps, gap-free columns, and gappiest sequence/column.

### Gap Fraction Per Column
```python
def gap_profile(alignment):
    profile = []
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        gap_fraction = column.count('-') / len(alignment)
        profile.append(gap_fraction)
    return profile

gaps = gap_profile(alignment)
avg_gaps = sum(gaps) / len(gaps)
print(f'Average gap fraction: {avg_gaps*100:.1f}%')
```

### Gap Statistics Summary

```python
def gap_statistics(alignment):
    # total gaps, gap fraction, gappiest sequence and column indices, gap-free column count
    ...
```

Full implementation: `examples/gap_statistics.py`.

## Alignment Quality Metrics

**Goal:** Score alignment quality using sum-of-pairs or simple match/mismatch/gap scoring across all columns.

**Approach:** For each column, score all pairwise residue comparisons and sum across the alignment.

### Overall Alignment Score
```python
def alignment_score(alignment, match=1, mismatch=-1, gap=-2):
    total_score = 0
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        for i, c1 in enumerate(column):
            for c2 in column[i+1:]:
                if c1 == '-' or c2 == '-':
                    total_score += gap
                elif c1 == c2:
                    total_score += match
                else:
                    total_score += mismatch
    return total_score

score = alignment_score(alignment)
print(f'Alignment score: {score}')
```

### Sum of Pairs Score

Biopython's `substitution_matrices.load('BLOSUM62')` returns a `Bio.Align.substitution_matrices.Array` object (a numpy-backed 2D array indexed by residue characters), NOT a dict. The correct accessor is `matrix[c1, c2]`; calling `.get((c1, c2), 0)` on an Array silently always returns 0. Standard BLOSUM62 includes `B`, `Z`, `X`, and `*`; pairs containing residues outside the matrix alphabet (e.g. `U` selenocysteine, `J` Leu/Ile) raise `IndexError` and should be skipped or scored zero.

```python
def sum_of_pairs(alignment, substitution_matrix=None):
    if substitution_matrix is None:
        substitution_matrix = substitution_matrices.load('BLOSUM62')

    total = 0.0
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        for i, c1 in enumerate(column):
            for c2 in column[i+1:]:
                if c1 == '-' or c2 == '-':
                    continue
                try:
                    total += substitution_matrix[c1, c2]
                except (KeyError, IndexError):
                    continue
    return total
```

**SP-score is biased on unbalanced datasets.** The above implementation gives equal weight to every sequence pair. On phylogenetically structured datasets (e.g. 95 mammals + 5 outgroups), 99% of pairs are mammal-mammal and the SP score reports only mammal-internal alignment quality. MUSCLE and T-Coffee internally compute weighted SP using sequence weights (Henikoff or position-based) so pair contributions are downweighted by cluster redundancy. For SP-as-quality-score on real data, multiply each pair contribution by `weight[i] * weight[j]` from the Henikoff weights in `alignment/msa-parsing` (`examples/henikoff_weights.py`).

## Position-Specific Score Matrix (PSSM)

**Goal:** Build a position-specific scoring matrix from the alignment for motif analysis or sequence scoring.

**Approach:** Raw counts give frequencies; without pseudocounts, log-odds against background diverge to negative infinity at any column missing a residue. Henikoff JG & Henikoff S 1996 (Bioinf 12:135-143) introduced data-dependent pseudocount weighting; a simple Laplace add-one is the minimal correct approach for production use. Full implementation: `examples/pssm.py`.

```python
def pssm_with_pseudocounts(alignment, background, pseudocount=1.0):
    # log2((counts[r] + pc * background[r]) / (n + pc) / background[r]) per column
    ...
```

`pseudocount=1.0` is the Laplace prior; HMMER uses Dirichlet mixtures for sophisticated smoothing. For motif scanning, score a candidate site by summing per-position log-odds; sites above a calibrated threshold are predicted hits. Use `ROBINSON_BACKGROUND` (defined in the IC section above) for protein.

## Effective Sequence Number (Neff)

**Goal:** Estimate non-redundant sequence count for MSA-depth metrics.

**Approach:** Cluster at an identity threshold (0.62 protein, 0.80 nucleotide) and weight by inverse cluster size; reference implementation lives in `msa-parsing` (`examples/neff.py`). `Neff/L > 0.5` is the rule-of-thumb for direct-coupling-analysis contact prediction; AlphaFold's MSA-depth scoring uses a closely related metric.

## Mutual Information with APC

**Goal:** Detect coevolving column pairs as a coupling/contact signal.

**Approach:** Pairwise MI minus average-product correction (Dunn, Wahl, Gloor 2008 Bioinf). Reference implementation lives in `msa-parsing` (`examples/mi_apc.py`). For production-grade contact prediction beyond a few hundred columns, switch to plmDCA (Ekeberg et al 2013) or EVcouplings (Hopf et al 2017).

## Distance Correction Models

For publication-grade pairwise distances, do NOT pick a model by rule of thumb. Run ModelTest-NG to select the best-fit substitution model by AIC/BIC, then apply that correction via IQ-TREE2 (`.mldist` output) or EMBOSS `distmat`. Hand-coded JC69 / K80 / blosum62 corrections via `Bio.Phylo.TreeConstruction.DistanceCalculator` are appropriate only for exploratory work.

```bash
modeltest-ng -i alignment.fasta -d nt -t ml
modeltest-ng -i alignment.fasta -d aa -t ml -p 4
```

```python
from Bio.Phylo.TreeConstruction import DistanceCalculator

calculator = DistanceCalculator('blosum62')
distance_matrix = calculator.get_distance(alignment)
```

For substitution-model selection in the context of full phylogenetic inference, see `phylogenetics/modern-tree-inference`.

## Alignment Quality Assessment

### When to Worry About Alignment Quality

| Warning Sign | Implication | Action |
|-------------|-------------|--------|
| Average pairwise identity <25% (protein) | Twilight zone; alignment may be unreliable | Use GUIDANCE2 to assess; consider structural alignment |
| >30% of columns have >50% gaps | Possible non-homologous sequences or misalignment | Remove outlier sequences and re-align |
| Identity varies dramatically across regions | Domain architecture mismatch | Align domains separately |
| Conservation pattern absent in expected functional regions | Alignment error or non-homology | Verify with BLAST that sequences are truly homologous |

### Quantifying Alignment Uncertainty

Alignment uncertainty propagates directly into evolutionary inference; for selection analysis (dN/dS), misaligned codons create artificial nonsynonymous differences and false positive signals. For column-confidence quantification (GUIDANCE2, MUSCLE5 ensemble, T-Coffee TCS), see the Confidence Assessment section in `alignment/multiple-alignment`.

## Note on Bio.Align.AlignInfo

The `AlignInfo.SummaryInfo` class is **deprecated** in recent Biopython versions. Use the custom functions in this skill instead:
- For PSSM: use `pssm_with_pseudocounts()` above
- For information content: use `information_content()` function earlier in this skill
- For consensus: see msa-parsing skill

## Quick Reference: Metrics

| Metric | Description | Range |
|--------|-------------|-------|
| Identity | Fraction of identical residues | 0-1 |
| Conservation | Most common residue frequency | 0-1 |
| Shannon Entropy | Variability measure | 0 to log2(alphabet) |
| Information Content | Max entropy - observed entropy | 0 to log2(alphabet) |
| Gap Fraction | Proportion of gaps | 0-1 |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ZeroDivisionError` | Empty column after gap removal | Check for gap-only columns |
| `KeyError` | Character not in substitution matrix | Handle gaps separately |
| Negative IC | Wrong alphabet size | Use 4 for DNA, 20 for protein |

## Related Skills

- alignment/multiple-alignment - Run MSA tools and quantify alignment confidence with ensembles
- alignment/msa-parsing - Parse, filter, trim, and assess alignment quality (Henikoff weights, Neff, MI-APC live there)
- alignment/alignment-io - Read/write alignment files
- alignment/pairwise-alignment - Create and score pairwise alignments
- alignment/alignment-trimming - Column trimming before downstream statistics
- alignment/structural-alignment - Twilight-zone alternative when sequence MSA is unreliable
- phylogenetics/distance-calculations - Distance models and tree building from corrected distances
- sequence-manipulation/sequence-properties - Sequence-level statistics

## References

- Schneider TD, Stephens RM. 1990. Sequence logos: a new way to display consensus sequences. NAR 18:6097-6100.
- Robinson AB, Robinson LR. 1991. Distribution of glutamine and asparagine residues and their near neighbors in peptides and proteins. PNAS 88:8880-8884.
- Capra JA, Singh M. 2007. Predicting functionally important residues from sequence conservation. Bioinf 23:1875-1882.
- Henikoff JG, Henikoff S. 1996. Using substitution probabilities to improve position-specific scoring matrices. Bioinf 12:135-143.
- Pei J, Grishin NV. 2001. AL2CO: calculation of positional conservation in a protein sequence alignment. Bioinf 17:700-712.
- Mayrose I, Graur D, Ben-Tal N, Pupko T. 2004. Comparison of site-specific rate-inference methods for protein sequences: empirical Bayesian methods are superior. MBE 21:1781-1791.
- Valdar WSJ. 2002. Scoring residue conservation. Proteins 48:227-241.
- Raghava GPS, Barton GJ. 2006. Quantification of the variation in percentage identity for protein sequence alignments. BMC Bioinf 7:415.
- Dunn SD, Wahl LM, Gloor GB. 2008. Mutual information without the influence of phylogeny or entropy dramatically improves residue contact prediction. Bioinf 24:333-340.
- Altschul SF et al. 1997. Gapped BLAST and PSI-BLAST: a new generation of protein database search programs. NAR 25:3389-3402.
- Pearson WR. 2013. An introduction to sequence similarity ("homology") searching. Curr Protoc Bioinf 3.1.
- Eddy SR. 2008. A probabilistic model of local sequence alignment that simplifies statistical significance estimation. PLOS CB 4:e1000069.
- Edgar RC. 2004. MUSCLE: multiple sequence alignment with high accuracy and high throughput. NAR 32:1792-1797.
- Darriba D et al. 2020. ModelTest-NG: a new and scalable tool for the selection of DNA and protein evolutionary models. MBE 37:291-294.
<!-- END FILE: alignment/msa-statistics/SKILL.md -->

## 子目录：alignment/multiple-alignment

<!-- BEGIN FILE: alignment/multiple-alignment/SKILL.md -->
---
name: bio-alignment-multiple
description: Perform multiple sequence alignment using MAFFT, MUSCLE5, ClustalOmega, or T-Coffee. Guides tool and algorithm selection based on dataset size, sequence divergence, and downstream application. Use when aligning three or more homologous sequences for phylogenetics, conservation analysis, or evolutionary studies.
tool_type: mixed
primary_tool: MAFFT
---

## Version Compatibility

Reference examples tested with: MAFFT 7.520+, MUSCLE 5.1+, ClustalOmega 1.2.4+, T-Coffee 13+, PAL2NAL 14+, BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `mafft --version`, `muscle -version`, `clustalo --version`
- Python: `pip show biopython` then `help(module.function)` to check signatures

If code throws errors, introspect the installed tool and adapt the example to match the actual CLI flags rather than retrying.

# Multiple Sequence Alignment

**"Align multiple sequences"** -> Compute an optimal alignment of three or more homologous sequences using progressive, iterative, or consistency-based methods.
- CLI: `mafft` (most versatile), `muscle` (highest accuracy), `clustalo` (scales well), `t_coffee` (consistency-based)
- Python: `subprocess.run()` wrapping CLI tools; BioPython `Bio.Align.Applications` was removed in BioPython 1.86 (verify with `pip show biopython`); use `subprocess` directly

## MSA Algorithm Taxonomy

When a tool is failing on a dataset, switch to a tool from a different algorithmic family rather than tuning flags. The six families and their characteristic failure modes:

| Family | Representative tools | Best at | Fails when |
|--------|---------------------|---------|-----------|
| Progressive | ClustalW, MAFFT FFT-NS-2 | Fast, large datasets, similar lengths | Early-stage gap errors propagate; no recovery |
| Iterative refinement | MAFFT L-INS-i, MUSCLE3, PRRN | Recovers from progressive errors at <2000 seqs | Slow on >2000; still guide-tree dependent |
| Consistency-based | T-Coffee, ProbCons | Highest accuracy <100 seqs; integrates evidence | O(N^2 to N^4) scaling; heavy compute |
| HMM-based | HMMER hmmalign, ClustalOmega (HHalign), UPP, WITCH | Adding sequences to a curated profile; fragmentary input | Needs an existing high-quality profile or backbone |
| Divide-and-conquer | PASTA, MAGUS, MUSCLE5 super5 | Heterogeneous large datasets (>10k seqs) | Sub-alignment merges can introduce artefacts |
| Structure or pLM-informed | Foldmason, PROMALS3D, vcMSA, 3D-Coffee | Dark proteome, <15% identity, dataset has structures | Requires structures or a working pLM |

## Tool Selection

Pick by dataset size and divergence; the default recommendations follow the table.

| Tool | Best For | Max Sequences | Accuracy | Speed |
|------|----------|---------------|----------|-------|
| MAFFT L-INS-i | Highest accuracy, <200 seqs | ~200 | Highest | Slow |
| MAFFT FFT-NS-2 | Large datasets, good balance | ~50,000 | Good | Fast |
| MAFFT E-INS-i | Sequences with long unalignable internal regions | ~200 | High | Slow |
| MUSCLE5 (PPP `-align`) | Benchmarked highest accuracy on Balifam-10000 | ~1000 | Highest | Medium |
| MUSCLE5 (`-super5`) | Large datasets via mBed clustering | ~100,000+ | Good | Medium |
| ClustalOmega | Very large datasets, HMM-based profiles | ~190,000 in published benchmark (Sievers et al 2011 Mol Syst Biol) | Good | Fast |
| T-Coffee (default) | Small datasets needing maximum accuracy | ~200 | Highest | Slowest |

**Default recommendation**: MAFFT L-INS-i for <200 sequences; MAFFT FFT-NS-2 or MUSCLE5 super5 for thousands; MUSCLE5 ensemble (`-stratified`) when alignment confidence estimates are needed.

### Cross-Aligner Sensitivity Check

When downstream analysis depends on a specific column (a candidate selection site, a contact-prediction position), run BOTH MAFFT L-INS-i and MUSCLE5 `-align` and verify that column is stable across the two outputs. If unstable, flag as low-confidence regardless of GUIDANCE2/TCS scores. The MUSCLE5 ensemble (`-stratified`/`-diversified`) accomplishes the same check directly within one tool and is preferred when ensemble output is acceptable downstream.

### Beyond MAFFT and MUSCLE: Scale and Domain

Some workloads exceed what the four main tools handle gracefully. Use the scale-and-domain table below to escape default-tool blind spots.

| Scenario | Recommended tool | Why |
|----------|------------------|-----|
| 100k - millions of sequences (UniRef cluster reps) | FAMSA v2 (Deorowicz et al 2016 SREP, v2 2024) | Million-scale MSA in hours with Pareto-optimal accuracy |
| Heterogeneous large dataset (variable length, divergence) | PASTA (Mirarab et al 2015 J Comp Biol) or MAGUS (Smirnov & Warnow 2021 Bioinf) | Divide-and-conquer plus iterative re-alignment |
| Fragmentary input (metagenomics, eDNA, ancient DNA) | UPP (Nguyen et al 2015 Genome Biol) or WITCH (Shen et al 2022 J Comp Biol) | HMM backbone tolerates partial sequences |
| Dark proteome / <15% identity | vcMSA (McWhite, Armour-Garb & Singh 2023 Genome Res; alpha-stage tool per its repo README; last release Oct 2023; test on representative inputs before pipeline use) or Foldmason (Gilchrist et al 2024) | pLM-embedding or structural alignment where sequence fails |
| RNA with secondary structure | Infernal `cmalign` (Nawrocki & Eddy 2013), R-Coffee, MAFFT-Q-INS-i | Sequence + base-pair consistency |
| Strand-unknown (Sanger, Nanopore raw) | `mafft --adjustdirection --globalpair` | Auto-detects and reverse-complements as needed |
| Adding many sequences to a curated profile | HMMER `hmmalign` (Eddy 2011 PLOS CB) | Profile-driven; better than `mafft --add` for Pfam-style use |

**vcMSA limitation:** Pre-filter input to within ~2x mean length; vcMSA degrades sharply on mixed full-length/fragment input because ProtT5 embeddings encode positional context. For mixed-length sets, segment long sequences via HHsearch domain decomposition before alignment, or use Foldmason on predicted structures.

## Critical Concepts

### Mitigate Guide-Tree Dependency

All major MSA tools build a guide tree, then align progressively along it; once a gap is inserted in the progressive phase, it is never removed, so early errors propagate. To mitigate: prefer iterative-refinement modes (MAFFT `-i`, MUSCLE5), use consistency scoring (T-Coffee) for small datasets, and quantify uncertainty with GUIDANCE2 bootstrapping or the MUSCLE5 ensemble before publishing column-specific conclusions.

### Joint MSA-Phylogeny Co-estimation (Small Datasets Only)

The theoretically correct answer to guide-tree dependency is to estimate the alignment and tree jointly under a statistical evolutionary model rather than treating MSA as a fixed input to phylogenetic inference. BAli-Phy version 3 (Redelings 2021 Bioinf 37:3032) does this via MCMC, producing a posterior distribution over alignments and trees with insertion/deletion rates as model parameters. Version 3 is O(n) instead of O(n^2) per likelihood evaluation, but the practical ceiling remains ~70-200 sequences before runtime becomes prohibitive (weeks for >100 sequences). When the dataset fits the cap, BAli-Phy gives the most defensible alignment+tree pair for publication; when it does not, the practical alternative is MUSCLE5 ensemble + IQ-TREE per-replicate (Edgar 2022) to approximate posterior alignment uncertainty without joint estimation.

| Dataset size | Recommended approach |
|--------------|----------------------|
| < 70 sequences | BAli-Phy v3 joint MSA+tree posterior; gold standard |
| 70 - 200 sequences | BAli-Phy v3 if compute allows (weeks); else MUSCLE5 ensemble + IQ-TREE per replicate |
| > 200 sequences | MUSCLE5 ensemble (`-stratified`) + IQ-TREE per replicate; BAli-Phy not feasible |
| > 1000 sequences | Single MAFFT/MUSCLE5 + standard bootstrap; ensemble methods become intractable |

### Sequence Divergence Thresholds

| Protein Identity | Signal Level | Recommendation |
|-----------------|--------------|----------------|
| >40% | Strong | Any MSA tool produces reliable alignment |
| 25-40% | Moderate (twilight zone begins) | Use iterative methods (L-INS-i, MUSCLE5); validate with GUIDANCE2 |
| 20-25% | Weak | Profile-profile methods (HHpred); consider structural alignment |
| <15-20% (length-dependent twilight) | Noise dominates signal | Sequence MSA is unreliable; switch to structural alignment (Foldseek, TM-align) or pLM aligners -- see `alignment/structural-alignment` |

## Running MAFFT

### Algorithm Selection

MAFFT offers multiple algorithms with explicit accuracy/speed tradeoffs. Selecting the right mode is critical; the difference between L-INS-i and FFT-NS-1 can be the difference between a correct and incorrect downstream phylogeny.

| Algorithm | Flag | Strategy | Best For |
|-----------|------|----------|----------|
| FFT-NS-1 | `--retree 1` | Progressive only | Quick look, >10,000 seqs |
| FFT-NS-2 | `--retree 2` | Progressive + guide tree rebuild | Default balance, 200-10,000 seqs |
| FFT-NS-i | `--maxiterate 1000` | Iterative refinement | Moderate improvement, 200-2,000 seqs |
| G-INS-i | `--globalpair --maxiterate 1000` | Global pairwise + iterative | Sequences alignable over full length, <200 |
| L-INS-i | `--localpair --maxiterate 1000` | Local pairwise + iterative | Single alignable domain amid divergent flanks, <200 |
| E-INS-i | `--genafpair --maxiterate 1000` | Local with generalized affine gaps | Multiple conserved motifs separated by unalignable regions, <200 |
| Auto | `--auto` | Auto-selects based on dataset size | When unsure |

**Decision guide**: If sequences share a single conserved domain (most common case), use L-INS-i. If sequences are globally similar (e.g., ortholog set of similar length), use G-INS-i. If sequences have multiple conserved blocks separated by highly variable linker regions (e.g., multi-domain proteins with variable interdomain regions), use E-INS-i.

**G-INS-i failure mode:** When sequences have long divergent N/C-terminal extensions (signal peptides, intrinsically-disordered regions, isoform-specific tails), the global pairwise distance G-INS-i uses for guide-tree construction is dominated by the extension's mismatch content. The guide tree then mis-clusters sequences by extension similarity rather than core homology. Symptom: the resulting alignment has core conserved domains poorly aligned despite high-identity flanks. Switch to L-INS-i (local pairwise; tolerant of divergent flanks) or pre-process to remove signal peptides/disordered regions before alignment.

### What `--auto` Picks (and Why to Specify Explicitly)

`mafft --auto` silently downgrades the algorithm based on dataset size. The decision tree is roughly:

| Sequences | `--auto` selects | Equivalent flags |
|-----------|------------------|------------------|
| < 200 | L-INS-i | `--localpair --maxiterate 1000` |
| 200 - 500 | FFT-NS-i | `--retree 2 --maxiterate 2` |
| 500 - 2000 | FFT-NS-2 | `--retree 2 --maxiterate 0` |
| 2000 - 50000 | FFT-NS-2 (one-pass) | `--retree 1 --maxiterate 0` |
| > 50000 | PartTree | `--parttree --retree 1 --maxiterate 0` |

The transition at 200 sequences flips the alignment from "iterative-refined accurate" to "single-pass progressive". Note that `--auto` invokes FFT-NS-i with only `--maxiterate 2` in the 200-500 range (a truncated form of the full FFT-NS-i which uses `--maxiterate 1000`); for best accuracy in this range, specify `--retree 2 --maxiterate 1000` explicitly. For publication-quality phylogenetics, specify the algorithm explicitly so reproducibility audits do not rely on internal threshold heuristics.

### Basic Usage

**Goal:** Run MAFFT on a FASTA file with appropriate algorithm selection.

**Approach:** Invoke MAFFT via command line or subprocess, selecting the algorithm based on dataset characteristics.

```bash
# Highest accuracy for <200 sequences (local pairwise iterative)
mafft --localpair --maxiterate 1000 input.fasta > aligned.fasta

# Good balance for medium datasets
mafft --retree 2 input.fasta > aligned.fasta

# Auto-select algorithm based on dataset size
mafft --auto input.fasta > aligned.fasta

# Protein alignment with specific matrix (default BLOSUM62)
mafft --amino --localpair --maxiterate 1000 input.fasta > aligned.fasta

# DNA alignment (auto-detected, but can be explicit)
mafft --nuc --localpair --maxiterate 1000 input.fasta > aligned.fasta

# Adjust gap penalties (op=gap open, ep=gap extension)
mafft --op 1.53 --ep 0.123 --localpair --maxiterate 1000 input.fasta > aligned.fasta

# Multithreaded
mafft --thread 8 --localpair --maxiterate 1000 input.fasta > aligned.fasta
```

```python
import subprocess

def run_mafft(input_fasta, output_fasta, algorithm='linsi', threads=4):
    algo_flags = {
        'linsi': ['--localpair', '--maxiterate', '1000'],
        'ginsi': ['--globalpair', '--maxiterate', '1000'],
        'einsi': ['--genafpair', '--maxiterate', '1000'],
        'fftns2': ['--retree', '2'],
        'auto': ['--auto'],
    }
    cmd = ['mafft', '--thread', str(threads)] + algo_flags[algorithm] + [input_fasta]
    with open(output_fasta, 'w') as out:
        result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f'MAFFT failed (exit {result.returncode}):\n{result.stderr}')

run_mafft('sequences.fasta', 'aligned.fasta', algorithm='linsi')
```

MAFFT writes its progress log and errors to stderr, not stdout. Capturing stderr and surfacing the failure message is essential when MAFFT exits non-zero (e.g. encountering ambiguous characters, oversized input, missing libraries) -- otherwise `check=True` raises a CalledProcessError without showing the actionable message.

### Adding Sequences to an Existing Alignment

**Goal:** Add new sequences to an existing MSA without realigning the entire dataset.

**Approach:** Use MAFFT's `--add` for full-length sequences, `--addfragments` for partial / surveillance / metagenomic reads. The two flags are NOT interchangeable.

| Flag | Use when | Behaviour |
|------|----------|-----------|
| `--add` | New sequences are full-length homologues | Each new sequence is profile-aligned end-to-end |
| `--addfragments` | New sequences are partial (reads, contigs, surveillance amplicons) | Free terminal gaps; new sequences may align to a sub-region of the profile |
| `--addprofile` | Adding an entire pre-aligned profile | Profile-profile alignment |
| `--keeplength` | Output must have the same column count as input MSA | Insertions in new sequences are dropped (key for HMMER/Pfam-style use) |

```bash
# Full-length additions; may extend alignment with new columns
mafft --add new_seqs.fasta existing_alignment.fasta > updated.fasta

# Partial reads or fragments; common for SARS-CoV-2 surveillance
mafft --addfragments new_reads.fasta --keeplength reference_msa.fasta > updated.fasta

# Profile-profile merge
mafft --addprofile second_msa.fasta first_msa.fasta > merged.fasta
```

For HMM-curated families (Pfam, Rfam), `hmmalign --trim --outformat afa profile.hmm new_seqs.fa > out.fasta` is the canonical alternative; it constrains insertions to lowercase columns rather than introducing new alignment columns and is the format expected by downstream HMMER/HHsuite tooling.

## Running MUSCLE5

Pick `-align` (PPP) for peak-accuracy runs up to ~1000 sequences, or `-super5` (mBed clustering + chunked alignment) for thousands to millions. `-super5` is not a "lower quality" mode; both share the same HMM-perturbation ensemble machinery.

| Command | Algorithm | Designed for | Output |
|---------|-----------|--------------|--------|
| `-align` (PPP) | Posterior probability progressive (HMM) | <= ~1000 seqs, peak accuracy | Single MSA or .efa ensemble |
| `-super5` | mBed-clustering + chunked alignment | Thousands to millions of seqs | Single MSA or .efa ensemble |

### Basic Usage

```bash
# Peak accuracy PPP algorithm, <1000 sequences
muscle -align input.fasta -output aligned.fasta -threads 8

# super5 divide-and-conquer for thousands of sequences
muscle -super5 input.fasta -output aligned.fasta -threads 8
```

### Ensemble Mode for Alignment Confidence

**Goal:** Quantify alignment uncertainty by generating multiple HMM-perturbed alignments and measuring column consistency.

**Approach:** MUSCLE5 (Edgar 2022 Nat Comm) ships two ensemble modes: `-stratified` (16 replicates by default: the `-replicates` flag defaults to 4 HMM-perturbation seeds x 4 guide-tree permutations) and `-diversified` (100 replicates by default). Both write an Ensemble FASTA (.efa) file containing all replicates; column-level confidence is the fraction of replicates that place a given residue pair in the same column. `-perturb SEED` is a separate flag that sets the HMM-perturbation random seed, not an ensemble selector.

```bash
# Stratified ensemble: 16 replicates (4 HMM-perturbation seeds x 4 guide-tree permutations)
muscle -super5 input.fasta -stratified -output ensemble.efa

# Diversified ensemble: 100 replicates exploring guide-tree and HMM space
muscle -super5 input.fasta -diversified -output ensemble.efa

# Optional: change replicate count and HMM-perturbation seed
muscle -super5 input.fasta -stratified -replicates 8 -perturb 42 -output ensemble.efa
```

The .efa output is consumed downstream to derive confidence-weighted bootstrap support: each replicate is fed to a tree builder and the resulting trees combined (Edgar 2022 supplement). Columns consistently aligned across replicates are reliable; high-divergence regions diverge between replicates and should be flagged before phylogenetic inference.

## Running ClustalOmega

Use ClustalOmega when datasets reach hundreds of thousands of sequences (the mBed guide tree scales O(N log N)) or for HMM-profile-driven alignment. Prefer MAFFT or MUSCLE5 below that scale.

```bash
# Basic alignment
clustalo -i input.fasta -o aligned.fasta --auto

# Force overwrite output
clustalo -i input.fasta -o aligned.fasta --force

# Specify output format
clustalo -i input.fasta -o aligned.phy --outfmt=phylip

# Use more iterations for better accuracy
clustalo -i input.fasta -o aligned.fasta --iter=5

# Profile-profile alignment (align two existing MSAs)
clustalo --p1 profile1.fasta --p2 profile2.fasta -o merged.fasta

# Add sequences to existing alignment
clustalo -i new_seqs.fasta --profile1 existing.fasta -o updated.fasta

# Multithreaded
clustalo -i input.fasta -o aligned.fasta --threads=8
```

## Running T-Coffee

Use T-Coffee for small datasets (<50 sequences) where maximum accuracy matters or where structural templates exist (Expresso, 3D-Coffee). It is slower than progressive aligners but integrates diverse evidence via consistency-based library scoring.

| Mode | Flag | What it does |
|------|------|-------------|
| Default | (none) | T-Coffee + Lalign pairwise library |
| M-Coffee | `-mode mcoffee` | Combines libraries from MAFFT, MUSCLE, ClustalW, ProbCons, T-Coffee, etc. |
| Expresso | `-mode expresso` | PSI-BLAST searches PDB for structural templates, runs SAP structural alignment (requires internet for PSI-BLAST and PDB lookups; offline alternative: 3D-Coffee with user-supplied templates) |
| 3D-Coffee | `-mode 3dcoffee -template_file templates.txt` | User-supplied PDB templates; SAP / TM-align pairwise structural library |
| R-Coffee | `-mode rcoffee` | RNA: combines sequence alignment with consensus secondary structure (RNAplfold) |
| Pro-Coffee | `-mode procoffee` | Promoter regions: enforces position-specific TF binding-site alignment |
| Reliability | `-evaluate -output score_ascii` | TCS column reliability score for an existing alignment |

```bash
t_coffee input.fasta -output fasta_aln -outfile aligned.fasta

t_coffee input.fasta -mode mcoffee -output fasta_aln -outfile aligned.fasta

t_coffee input.fasta -mode expresso -output fasta_aln -outfile aligned.fasta

t_coffee -infile aligned.fasta -evaluate -output score_ascii > tcs_scores.ascii
```

**When to use T-Coffee**: Small datasets (<50 sequences) where maximum accuracy matters, especially when structural information (PDB templates) is available. Expresso (Armougom et al 2006 NAR) and 3D-Coffee modes (Poirot et al 2004; O'Sullivan et al 2004 JMB) substantially improve correct-column rate over sequence-only T-Coffee when structures exist; verify the latest benchmark numbers in the project documentation. Expresso requires internet access for PSI-BLAST + PDB lookups. The TCS reliability score (Chang et al 2014 MBE) flags individual columns as reliable/unreliable for downstream filtering before phylogenetics.

## Codon-Aware Alignment

### When Codon Alignment Is Required

Coding sequences destined for selection analysis (dN/dS with PAML/codeml, HyPhy BUSTED/MEME/aBSREL) **must** be aligned respecting codon boundaries. Standard nucleotide MSA tools do not preserve reading frames and produce systematically incorrect dN/dS estimates -- Fletcher & Yang (2010 MBE) showed conventional aligners cause false-positive signals in the branch-site test of positive selection even on clean simulated data.

### Codon-Alignment Tool Decision Tree

| Input cleanliness | Recommended tool | Notes |
|------------------|------------------|-------|
| Clean orthologs (no frameshifts, no internal stops) | MAFFT-protein + PAL2NAL (Suyama, Torrents & Bork 2006 NAR) | Fastest; standard PAML pipeline input |
| Recently duplicated paralogs (indel-rich) | PRANK +F codon (Loytynoja & Goldman 2008 Science) | Phylogeny-aware indel model; fewest false-positive selection calls (Fletcher & Yang 2010) |
| Frameshifts, pseudogenes, error-prone assemblies | MACSE v2 `alignSequences -fs <cost>` (Ranwez et al 2018 MBE) | Frameshift-tolerant; preserves reading frame across sequencing errors |
| Mixed dataset with some bad genes | OMM_MACSE pipeline (Scornavacca, Belkhir, Lopez et al 2019; Ranwez group) | MACSE non-homologous-fragment trimming + MAFFT prealignment + MACSE frameshift refinement + HMMcleaner |
| HyPhy-grade quality (BUSTED, MEME, aBSREL input) | HyPhy `pre-msa.bf` / `post-msa.bf` (Pond lab; Kosakovsky Pond et al) | Strips stop codons, runs MSA at protein level, threads back, validates frames |

### PAL2NAL: Protein-Guided Codon Alignment

**Goal:** Thread a nucleotide coding sequence alignment onto a protein alignment to preserve reading frame.

**Approach:** Align protein sequences first (higher sensitivity), then use PAL2NAL to map the protein alignment back to codons. Suyama et al 2006 NAR; standard codeml input pipeline.

```bash
mafft --localpair --maxiterate 1000 proteins.fasta > proteins_aligned.fasta
pal2nal.pl proteins_aligned.fasta codons.fasta -output fasta > codons_aligned.fasta
pal2nal.pl proteins_aligned.fasta codons.fasta -output paml > codons_aligned.phy
```

**Non-standard genetic codes:** PAL2NAL by default uses the standard code (NCBI table 1). For mitochondrial (vertebrate=2, yeast=3, invertebrate=5), ciliate macronuclear (=6, UAA/UAG=Gln), or other non-standard codes, the protein-to-codon mapping mismatches and PAL2NAL silently produces wrong codon assignments. Specify explicitly with `-codontable N`:

```bash
pal2nal.pl proteins_aligned.fasta codons.fasta -output paml -codontable 2 > codons_mt.phy
```

For datasets mixing genetic codes (e.g. nuclear + mitochondrial CDS in one tree), translate each lineage with its own code BEFORE protein alignment, never apply a single code globally. See NCBI Translation Tables for the full numbering.

### PRANK +F Codon Mode

**Goal:** Align coding sequences under a phylogeny-aware indel model that does not over-collapse insertions.

**Approach:** PRANK +F (Loytynoja & Goldman 2008 Science) treats indels as evolutionary events on a tree, distinguishing insertions from deletions. Slower than MAFFT but recommended for selection-analysis prep.

```bash
prank -d=codons.fasta -o=prank_aligned -codon -F
```

The `+F` flag enforces "fewer false insertions"; without it PRANK behaves more like a conventional aligner. For dN/dS analysis under PAML M2a/M8, PRANK +F is the most conservative input choice.

### MACSE v2: Frameshift-Tolerant Codon Alignment

**Goal:** Align coding sequences directly at the codon level while tolerating frameshifts and internal stops.

**Approach:** MACSE scores based on amino acid translation while operating on DNA. The v2 toolbox (Ranwez et al 2018 MBE) ships a sub-program selector via `-prog`; the eight most-used sub-programs are listed below (run `macse -help` for the full set in the installed release):

| Sub-program | Purpose |
|-------------|---------|
| `alignSequences` | Align coding sequences (`-fs <cost>` sets frameshift penalty) |
| `enrichAlignment` | Add new sequences to existing codon alignment |
| `refineAlignment` | Refine an alignment with MACSE scoring |
| `splitAlignment` | Split into sub-alignments (e.g. by guide tree clades) |
| `exportAlignment` | Convert between MACSE-internal and standard formats |
| `trimAlignment` | Position-aware trimming preserving codon structure |
| `trimNonHomologousFragments` | Detect and remove non-homologous regions per sequence |
| `reportGapsAA2NT` | Map protein-level gap removals back to nucleotide alignment |

```bash
java -jar macse_v2.jar -prog alignSequences -seq coding_seqs.fasta \
    -out_NT aligned_nt.fasta -out_AA aligned_aa.fasta -fs 30

java -jar macse_v2.jar -prog enrichAlignment -align existing.fasta \
    -seq new_seqs.fasta -out_NT updated.fasta
```

### OMM_MACSE: Recommended Pipeline Wrapper

OMM_MACSE (Ranwez group, used in OrthoMaM v10+) chains: MACSE `trimNonHomologousFragments` to remove non-homologous fragments (annotation errors, retained introns/UTRs), MAFFT pre-alignment for guide-tree, MACSE v2 frameshift-aware refinement, then soft HMMcleaner cleaning. This is the recommended pipeline for genome-scale ortholog datasets where some genes will contain frameshifts.

```bash
OMM_MACSE_v12.02.sif --in_seq_file orthogroup.fasta --out_dir omm_out --out_file_prefix orthogroup --genetic_code_number 1
```

### HyPhy pre-msa.bf / post-msa.bf

For HyPhy-grade dN/dS analyses (BUSTED, MEME, aBSREL, RELAX), Pond lab's standard workflow is:

```bash
hyphy pre-msa.bf --input cds.fasta
mafft --auto cds.fasta_protein.fas > cds.fasta_protein.msa
hyphy post-msa.bf --protein-msa cds.fasta_protein.msa --nucleotide-sequences cds.fasta_nuc.fas --output cds.codon.msa
```

`pre-msa.bf` strips internal stop codons and translates; `post-msa.bf` validates that all sequences remain in-frame after threading. Without this validation step, a single mis-aligned codon can cascade into a spurious episodic-selection call.

### Confidence Assessment

For publication-grade phylogenetics or selection analysis, alignment uncertainty must be quantified per column and unreliable columns excluded BEFORE downstream inference -- not after.

| Method | Tool | Output |
|--------|------|--------|
| Guide-tree perturbation | GUIDANCE2 (Sela et al 2015 NAR) | Per-column and per-residue reliability score (0-1); default cutoff 0.93. No GUIDANCE3 has been released; deep-learning successors are exploratory only. |
| Library-consistency | T-Coffee TCS (Chang et al 2014 MBE) | Per-column reliability score via `-evaluate -output score_ascii` |
| HMM ensemble | MUSCLE5 `-stratified` / `-diversified` | EFA file; column confidence = fraction of replicates supporting it |
| Co-optimal alignments | HoT (Landan & Graur 2007 MBE) | Heads-or-tails alternate optimal alignment for each column |

Mask columns below the reliability threshold before phylogenetic inference. Trees built from filtered alignments are markedly more stable to method choice.

**GUIDANCE2 thresholds are tool-specific.** The 0.93 default cutoff is calibrated against MAFFT-LINSI in Sela et al 2015. Running GUIDANCE2 on top of MUSCLE5 or PRANK uses different perturbation distributions and produces scores on a slightly different scale. For non-MAFFT base aligners, calibrate the threshold empirically using a benchmark with known-correct columns or use the tool-native ensemble scoring (MUSCLE5 `-stratified`) instead.

## Post-Alignment Validation Checklist

Before proceeding to downstream analysis, verify alignment quality:

1. **Visual inspection**: Scan for columns of mostly gaps with scattered residues (hallmark of misalignment)
2. **Gap distribution**: High gap fraction (>50% of columns with gaps) suggests problematic regions or inclusion of non-homologous sequences
3. **Sequence identity**: If average pairwise identity is <25% for proteins, alignment reliability is questionable
4. **Outlier sequences**: Sequences with excessive gaps relative to others may be non-homologous or fragments; consider removing and re-aligning
5. **Conservation pattern**: Functional domains should show clear conservation; absence of expected conserved motifs suggests alignment error or non-homology
6. **Run GUIDANCE2 or MUSCLE5 ensemble**: Quantify alignment confidence per column before phylogenetic inference

## When NOT to Run MSA

- **Non-homologous sequences**: MSA tools always produce an alignment, even for unrelated sequences; verify homology first (e.g., BLAST E-value < 1e-5)
- **Sequences below the twilight zone**: Below ~20% protein identity, sequence signal is lost in noise; structural alignment is needed
- **Different domain architectures**: Globally aligning multi-domain proteins with different domain orders produces meaningless results; align individual domains separately
- **Very different lengths without shared homology**: Aligning a 50-residue fragment against 1000-residue proteins globally forces biologically meaningless gaps; use local alignment or fragment-aware modes (E-INS-i)
- **Highly repetitive sequences**: Tandem repeats cause alignment ambiguity; specialized tools (e.g., TRUST for tandem repeats) may be needed

## Quick Reference

| Task | Command |
|------|---------|
| Best accuracy (<200 seqs) | `mafft --localpair --maxiterate 1000 in.fa > out.fa` |
| Large dataset | `mafft --retree 2 in.fa > out.fa` or `clustalo -i in.fa -o out.fa` |
| Uncertainty estimation | `muscle -super5 in.fa -stratified -output out.efa` |
| Codon-aware | Align protein first, then `pal2nal.pl prot.fa cds.fa -output fasta` |
| Add to existing MSA | `mafft --add new.fa existing.fa > updated.fa` |
| Profile merge | `clustalo --p1 msa1.fa --p2 msa2.fa -o merged.fa` |
| With structure info | `t_coffee in.fa -mode expresso` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| MAFFT runs out of memory | L-INS-i on too many sequences | Switch to FFT-NS-2 or auto mode |
| Alignment has many all-gap columns | Non-homologous sequences included | Filter input by BLAST hits first |
| ClustalOmega crashes on large input | Memory limits | Increase `--MAC` RAM or use MAFFT |
| PAL2NAL "length mismatch" | Protein/DNA sequences not from same genes | Verify correspondence with sequence IDs |
| MUSCLE5 slow on large datasets | Default algorithm not designed for >10K seqs | Use `-super5` mode |
| Poor alignment despite high identity | Wrong sequence type detection | Explicitly specify `--amino` or `--nuc` |

## Related Skills

- alignment/pairwise-alignment - Compare two sequences using PairwiseAligner
- alignment/alignment-io - Read/write MSA files in various formats
- alignment/msa-parsing - Parse, filter, trim, and assess MSA quality
- alignment/msa-statistics - Calculate identity, conservation, entropy metrics
- alignment/structural-alignment - Foldseek, TM-align, Foldmason for the dark proteome
- alignment/alignment-trimming - ClipKIT, trimAl, BMGE post-MSA column filtering
- phylogenetics/modern-tree-inference - Build phylogenetic trees from MSAs
- sequence-io/read-sequences - Read input sequences for alignment

## References

- Edgar RC. 2022. Muscle5: high-accuracy alignment ensembles enable unbiased assessments of sequence homology and phylogeny. Nat Comm 13:6968.
- Katoh K, Standley DM. 2013. MAFFT multiple sequence alignment software version 7. MBE 30:772-780.
- Sievers F et al. 2011. Fast, scalable generation of high-quality protein multiple sequence alignments using Clustal Omega. Mol Syst Biol 7:539.
- Notredame C, Higgins DG, Heringa J. 2000. T-Coffee: a novel method for fast and accurate multiple sequence alignment. JMB 302:205-217.
- Loytynoja A, Goldman N. 2008. Phylogeny-aware gap placement prevents errors in sequence alignment and evolutionary analysis. Science 320:1632-1635.
- Ranwez V, Douzery EJP, Cambon C, Chantret N, Delsuc F. 2018. MACSE v2: toolkit for the alignment of coding sequences accounting for frameshifts and stop codons. MBE 35:2582-2584.
- Suyama M, Torrents D, Bork P. 2006. PAL2NAL: robust conversion of protein sequence alignments into the corresponding codon alignments. NAR 34:W609-W612.
- Sela I, Ashkenazy H, Katoh K, Pupko T. 2015. GUIDANCE2: accurate detection of unreliable alignment regions accounting for the uncertainty of multiple parameters. NAR 43:W7-W14.
- Chang JM, Di Tommaso P, Notredame C. 2014. TCS: a new multiple sequence alignment reliability measure to estimate alignment accuracy and improve phylogenetic tree reconstruction. MBE 31:1625-1637.
- Fletcher W, Yang Z. 2010. The effect of insertions, deletions, and alignment errors on the branch-site test of positive selection. MBE 27:2257-2267.
- Armougom F, Moretti S, Poirot O, Audic S, Dumas P, Schaeli B, Keduas V, Notredame C. 2006. Expresso: automatic incorporation of structural information in multiple sequence alignments using 3D-Coffee. NAR 34:W604-W608.
- McWhite CD, Armour-Garb I, Singh M. 2023. Leveraging protein language models for accurate multiple sequence alignments. Genome Res 33:1145-1153.
- Redelings BD. 2021. BAli-Phy version 3: model-based co-estimation of alignment and phylogeny. Bioinf 37:3032-3034.
<!-- END FILE: alignment/multiple-alignment/SKILL.md -->

## 子目录：alignment/pairwise-alignment

<!-- BEGIN FILE: alignment/pairwise-alignment/SKILL.md -->
---
name: bio-alignment-pairwise
description: Perform pairwise sequence alignment using Biopython Bio.Align.PairwiseAligner. Use when comparing two sequences, finding optimal alignments, scoring similarity, and identifying local or global matches between DNA, RNA, or protein sequences.
tool_type: python
primary_tool: Bio.Align
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Pairwise Sequence Alignment

**"Align two sequences"** -> Compute an optimal alignment between a pair of sequences using dynamic programming.
- Python: `PairwiseAligner()` (BioPython Bio.Align)
- CLI: `needle` (global) or `water` (local) from EMBOSS
- R: `pairwiseAlignment()` (Biostrings)

Align two sequences using dynamic programming algorithms (Needleman-Wunsch for global, Smith-Waterman for local).

## Required Import

**Goal:** Load modules needed for pairwise alignment operations.

**Approach:** Import the PairwiseAligner class along with sequence and I/O utilities from Biopython.

```python
from Bio.Align import PairwiseAligner
from Bio.Seq import Seq
from Bio import SeqIO
```

## Pairwise Library Selection

`Bio.Align.PairwiseAligner` is the right default for interactive use, scripting, and pair sizes up to a few thousand residues, but it is not the fastest or most scalable option. For high-throughput screens, very long sequences, or production pipelines, switch to a SIMD-accelerated or specialised library.

| Library | Speed vs Bio.Align | Alphabet | Scoring | Vectorization | When to use |
|---------|-------------------|----------|---------|---------------|-------------|
| `Bio.Align.PairwiseAligner` (BioPython) | 1x baseline | DNA / RNA / protein | Matrix + affine | C-backed Gotoh | Default, <10 kb pairs, interactive use |
| `parasail` (Daily 2016 BMC Bioinf) | 10-100x | DNA / protein | Matrix + affine | SSE / AVX SIMD | High-throughput SW or NW; benchmark loops |
| `edlib` (Sosic & Sikic 2017 Bioinf) | 100-1000x | DNA only | Edit distance only | Bit-parallel Myers | Read mapping, k-mer search, primer placement |
| `pywfa` / WFA2 (Marco-Sola 2021 Bioinformatics 37:456; BiWFA: Marco-Sola 2023 Bioinformatics 39:btad074) | Best for low-divergence | DNA | Matrix + affine | Wavefront, O(s) memory | Long, near-identical sequences (>10 kb, <5% diverged) |
| `mappy` / minimap2 (Li 2018 Bioinf) | Production reads-to-genome | DNA | Chain + base-level | k-mer chain | Long-read mapping, splice-aware DNA |
| `Bio.pairwise2` | DEPRECATED | -- | -- | -- | Migrate to `PairwiseAligner` (deprecated in BioPython 1.80; not yet removed; migrate proactively) |
| EMBOSS `needle` / `water` | ~Bio.Align | DNA / protein | Matrix + affine | None | Reproducibility, audit trails (fixed, documented default parameters) |

Speed numbers in the table are rough; benchmark on representative inputs before committing. Critical caveats:
- **WFA / BiWFA**: 10-100x faster than Gotoh below 5% divergence; above ~10% it converges to Gotoh complexity. Right tool for PacBio HiFi self-similarity or assembly-vs-reference; not for distant homologs.
- **edlib**: 100-1000x faster than Gotoh at low divergence (<5% errors); above ~50% divergence the effective speedup drops to ~64x. For high-divergence DNA (<70% nucleotide identity), prefer parasail's SIMD score-only mode.
- **parasail**: SIMD only realises its advantage on long sequences in amortised batch loops.

When uncertain which algorithm Biopython's aligner selected internally, inspect `aligner.algorithm` after configuration -- it returns the resolved variant ("Needleman-Wunsch", "Smith-Waterman", "Gotoh global alignment algorithm", "Gotoh local alignment algorithm", "Waterman-Smith-Beyer global alignment algorithm", "Waterman-Smith-Beyer local alignment algorithm") for deterministic auditing.

## Core Concepts

| Mode | Algorithm | Use Case |
|------|-----------|----------|
| `global` | Needleman-Wunsch | Full-length alignment, similar-length sequences |
| `local` | Smith-Waterman | Find best matching regions, different-length sequences |
| `global` + free end gaps | Semi-global | Overlap detection, fragment-to-reference alignment |

### Choosing the Right Mode

- **Global**: Both sequences are expected to be homologous over their full length (e.g., two orthologs of similar size). Forces end-to-end alignment.
- **Local**: Conserved domains or motifs within otherwise dissimilar sequences. BLAST uses local alignment internally. Preferred when protein termini are highly divergent (termini accumulate mutations faster than core regions).
- **Semi-global**: One sequence is a fragment or subsequence of the other (e.g., primer to template, read to reference, detecting overlap between shotgun reads). Free end gaps prevent penalizing unaligned flanking regions.

**Common mistake**: Global alignment of sequences with very different lengths forces biologically meaningless terminal gaps. If sequences differ substantially in length, use local or semi-global instead.

### DNA vs Protein Alignment

| Scenario | Align As | Rationale |
|----------|----------|-----------|
| Nucleotide identity >70% | DNA | Sufficient signal at nucleotide level |
| Nucleotide identity <70% | Protein | Codon degeneracy masks signal at DNA level; protein alignment is ~3x more sensitive |
| Noncoding sequences (UTRs, intergenic) | DNA | No protein translation possible |
| Coding sequences for dN/dS analysis | Protein first, then back-translate codons (PAL2NAL) | Preserves reading frame for selection analysis |

When in doubt, align at the protein level. It captures functional constraint better because 20 amino acids provide richer signal than 4 nucleotides.

## Creating an Aligner

**Goal:** Configure a PairwiseAligner with appropriate scoring for the sequence type.

**Approach:** Instantiate PairwiseAligner with mode, scoring parameters, or a substitution matrix depending on DNA vs protein input.

```python
# Basic aligner with defaults
aligner = PairwiseAligner()

# Configure mode and scoring
aligner = PairwiseAligner(mode='global', match_score=2, mismatch_score=-1, open_gap_score=-10, extend_gap_score=-0.5)

# For protein alignment with substitution matrix
from Bio.Align import substitution_matrices
aligner = PairwiseAligner(mode='global', substitution_matrix=substitution_matrices.load('BLOSUM62'))
```

## Performing Alignments

**"Align two sequences"** -> Compute optimal alignment(s) between a pair of sequences, returning alignment objects or a score.

**Goal:** Align two sequences and retrieve the optimal alignment(s) or score.

**Approach:** Call `aligner.align()` for full alignment objects or `aligner.score()` for score-only (faster for large sequences).

```python
seq1 = Seq('ACCGGTAACGTAG')
seq2 = Seq('ACCGTTAACGAAG')

# Get all optimal alignments
alignments = aligner.align(seq1, seq2)
print(f'Found {len(alignments)} optimal alignments')
print(alignments[0])  # Print first alignment

# Get score only (faster for large sequences)
score = aligner.score(seq1, seq2)
```

## Alignment Output Format

```
target            0 ACCGGTAACGTAG 13
                  0 |||||.||||.|| 13
query             0 ACCGTTAACGAAG 13
```

## Accessing Alignment Data

**Goal:** Extract alignment properties including score, shape, aligned sequences, and coordinate mappings.

**Approach:** Access alignment object attributes and indexing to retrieve per-sequence aligned strings and coordinate arrays.

```python
alignment = alignments[0]

# Basic properties
print(alignment.score)                    # Alignment score
print(alignment.shape)                    # (num_seqs, alignment_length)
print(len(alignment))                     # Alignment length

# Get aligned sequences with gaps
target_aligned = alignment[0, :]          # First sequence (target) with gaps
query_aligned = alignment[1, :]           # Second sequence (query) with gaps

# Get coordinate mapping
print(alignment.aligned)                  # Array of aligned segment coordinates
print(alignment.coordinates)              # Full coordinate array
```

## Alignment Counts (Identities, Mismatches, Gaps)

**Goal:** Quantify identities, mismatches, and gaps in an alignment to calculate percent identity.

**Approach:** Use the `.counts()` method on the alignment object and derive percent identity from identity and mismatch totals.

```python
alignment = alignments[0]
counts = alignment.counts()

print(f'Identities: {counts.identities}')
print(f'Mismatches: {counts.mismatches}')
print(f'Gaps: {counts.gaps}')

# Calculate percent identity
total_aligned = counts.identities + counts.mismatches
percent_identity = counts.identities / total_aligned * 100
print(f'Percent identity: {percent_identity:.1f}%')
```

## Common Scoring Configurations

### PairwiseAligner Default Gap Penalties Are 0

`PairwiseAligner()` with no arguments uses match_score=1, mismatch_score=0, open_gap_score=0, extend_gap_score=0. Combined with a positive-scoring substitution matrix (BLOSUM62), this produces alignments with arbitrarily many short gaps -- gaps cost nothing while matches pay positive score. **Always specify gap penalties explicitly when using a substitution matrix.** BLASTP defaults: open=-11, extend=-1 with BLOSUM62; Smith-Waterman EMBOSS `water` defaults: open=-10, extend=-0.5. Inspect with `print(aligner)` after configuration to verify the resolved parameter set.

### DNA/RNA Alignment
```python
aligner = PairwiseAligner(mode='global', match_score=2, mismatch_score=-1, open_gap_score=-10, extend_gap_score=-0.5)
```

### Protein Alignment
```python
from Bio.Align import substitution_matrices
blosum62 = substitution_matrices.load('BLOSUM62')
aligner = PairwiseAligner(mode='global', substitution_matrix=blosum62, open_gap_score=-11, extend_gap_score=-1)
```

### Local Alignment (Find Best Region)
```python
aligner = PairwiseAligner(mode='local', match_score=2, mismatch_score=-1, open_gap_score=-10, extend_gap_score=-0.5)
```

### Semiglobal (Overlap/Fragment Alignment)
```python
# Free end gaps on query -- for aligning a fragment against a full-length reference
# or detecting overlap between reads
aligner = PairwiseAligner(mode='global')
aligner.query_left_open_gap_score = 0
aligner.query_left_extend_gap_score = 0
aligner.query_right_open_gap_score = 0
aligner.query_right_extend_gap_score = 0

# Free end gaps on BOTH sequences -- for overlap detection between two reads
aligner = PairwiseAligner(mode='global')
aligner.end_gap_score = 0.0
```

## Substitution Matrix Selection

**Goal:** Select the appropriate substitution matrix based on expected sequence divergence.

**Approach:** Match matrix to divergence level. BLOSUM and PAM number in **opposite directions**: higher BLOSUM = closer sequences; higher PAM = more distant sequences.

| Divergence Level | BLOSUM | PAM | When To Use |
|-----------------|--------|-----|-------------|
| Very close (<20% divergence) | BLOSUM80, BLOSUM90 | PAM30 | Recently duplicated genes, strain comparison |
| Moderate | BLOSUM62 (default) | PAM120 | General-purpose, most analyses |
| Distant (>50% divergence) | BLOSUM45, BLOSUM50 | PAM250 | Remote homology detection |

**BLOSUM62 is the universal default** (used by BLAST, most alignment tools). When in doubt, use BLOSUM62. Switch to BLOSUM80 for very similar proteins or BLOSUM45 for distant homologs.

**DNA matrices**: `NUC.4.4` (match=+5, mismatch=-4) handles IUPAC ambiguity codes. `HOXD70` is tuned for human-mouse whole-genome alignment from noncoding regions.

```python
from Bio.Align import substitution_matrices
print(substitution_matrices.load())  # List all 30 available matrices

blosum62 = substitution_matrices.load('BLOSUM62')  # General protein (default)
blosum80 = substitution_matrices.load('BLOSUM80')  # Close homologs
blosum45 = substitution_matrices.load('BLOSUM45')  # Distant homologs
nuc44 = substitution_matrices.load('NUC.4.4')      # DNA with IUPAC support
```

### Affine Gap Penalties: Biological Rationale

Gap penalties control how gaps (insertions/deletions) are scored. The **affine model** (`penalty = open + extend * (L-1)`) is almost always preferred over linear because it reflects indel biology: a DNA break introduces the first gap (costly), but extending an existing gap is mechanistically easier (less costly). This models the observation that indels in real sequences tend to occur as single contiguous events.

Typical values with BLOSUM62: gap open = -11, gap extend = -1 (BLASTP defaults). Setting gap open equal to gap extend (linear model) over-penalizes long indels and under-penalizes scattered single-residue gaps, producing biologically unrealistic alignments.

## Working with SeqRecord Objects

**Goal:** Align sequences loaded from FASTA files rather than hardcoded strings.

**Approach:** Parse SeqRecord objects from a FASTA file and pass their `.seq` attributes to the aligner.

```python
from Bio import SeqIO

records = list(SeqIO.parse('sequences.fasta', 'fasta'))
seq1, seq2 = records[0].seq, records[1].seq

aligner = PairwiseAligner(mode='global', match_score=1, mismatch_score=-1)
alignments = aligner.align(seq1, seq2)
```

## Iterating Over Multiple Alignments

```python
# Limit number of alignments returned (memory efficient)
aligner.max_alignments = 100

for i, alignment in enumerate(alignments):
    print(f'Alignment {i+1}: score={alignment.score}')
    if i >= 4:
        break
```

## Substitution Matrix from Alignment

**Goal:** Extract observed substitution frequencies from a completed alignment.

**Approach:** Access the `.substitutions` property to get a matrix of observed base/residue substitution counts.

```python
alignment = alignments[0]
substitutions = alignment.substitutions

# View as array (rows=target, cols=query)
print(substitutions)

# Access specific substitution counts
# substitutions['A', 'T'] gives count of A aligned to T
```

## Export Alignment to Different Formats

**Goal:** Convert an alignment to standard bioinformatics file formats for downstream tools.

**Approach:** Use Python's `format()` function with format specifiers (fasta, clustal, psl, sam) on the alignment object.

```python
alignment = alignments[0]

# Various output formats
print(format(alignment, 'fasta'))     # FASTA format
print(format(alignment, 'clustal'))   # Clustal format
print(format(alignment, 'psl'))       # PSL format (BLAT)
print(format(alignment, 'sam'))       # SAM format
```

## Quick Reference: Scoring Parameters

| Parameter | Description | Typical DNA | Typical Protein |
|-----------|-------------|-------------|-----------------|
| `match_score` | Score for identical bases | 1-2 | Use matrix |
| `mismatch_score` | Penalty for mismatches | -1 to -3 | Use matrix |
| `open_gap_score` | Cost to start a gap | -5 to -15 | -10 to -12 |
| `extend_gap_score` | Cost per gap extension | -0.5 to -2 | -0.5 to -1 |
| `substitution_matrix` | Scoring matrix | N/A | BLOSUM62 |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `OverflowError` | Too many optimal alignments | Set `aligner.max_alignments` |
| Low scores | Wrong scoring scheme | Use substitution matrix for proteins |
| No alignments in local mode | Scores all negative | Ensure `match_score` > 0 |

## Percent Identity: Definitions Matter

There are four common ways to calculate percent identity from the same alignment, producing different values:

| Method | Denominator | Best For |
|--------|-------------|----------|
| PID1 | Aligned positions + internal gaps | Gap-aware, conservative |
| PID2 | Aligned residue pairs (excluding gaps) | Always highest value |
| PID3 | Shorter sequence length | Length-normalized |
| PID4 | Mean sequence length | Best correlation with structural similarity |

**Practical impact**: Up to 11.5% difference between methods on a single alignment. Combined with different alignment algorithms, variation reaches 22%. Always report which method was used. The `counts()` method above uses aligned non-gap positions (similar to PID2).

## Statistical Significance: Karlin-Altschul

Use bit score (database-size-independent) and E-value (expected chance hits) to interpret raw alignment scores; never compare raw scores across scoring schemes. For non-default gap penalties or non-protein/DNA alphabets, generate empirical p-values via sequence shuffling instead of trusting the formula (`examples/empirical_pvalue.py`; for DNA, use the dinucleotide shuffle of Altschul & Erickson 1985 via `ushuffle`).

| Bit score | E-value (typical 1e6 db) | Interpretation |
|-----------|--------------------------|----------------|
| > 200 | < 1e-50 | Essentially certain homology |
| 50-200 | 1e-5 to 1e-50 | Likely homology |
| 30-50 | 0.01 to 1e-5 | Possible homology; verify with profile methods |
| < 30 | > 0.01 | Suspect; not significant |

Karlin-Altschul lambda/K are calibrated empirically per (matrix, gap-open, gap-extend) tuple; switching gap penalties without recalibrating produces wrong E-values.

**Mask compositional bias before scoring.** Low-complexity regions (poly-Q, proline-rich, leucine-rich TM helices) inflate raw scores. Pre-filter with SEG for protein or DUST for DNA, then run BLAST with `-comp_based_stats 2` (modern default; Yu & Altschul 2005 Bioinf, conditional) or `-comp_based_stats 3` for repeat-rich queries (Yu & Altschul 2005 unconditional; Schaffer et al 2001 NAR introduced the original level-1 statistics). SEG pre-filtering is complementary to `-comp_based_stats`, not redundant.

## When Alignment Is NOT Appropriate

Pick the alignment method by protein identity; below 15% identity DP alignments are statistically indistinguishable from random pairings, so escape to structure or pLM tools.

| Identity (protein) | Recommended approach |
|-------------------|---------------------|
| >= 40% | Any DP aligner; Bio.Align or BLAST is sufficient |
| 25-40% | Use sensitive iterative methods (MMseqs2 iterative, BLASTP with composition-based statistics) |
| 15-25% | Profile-profile (HHsearch, HMMER `phmmer`/`jackhmmer`) |
| < 15% | Structural alignment (Foldseek, TM-align, US-align) or pLM embeddings (TM-Vec, ESM-2 + cosine) -- see structural-alignment |

Length amplifies the signal: 30% identity over 200 residues is far more reliable than 30% over 50.

**When pairwise becomes the wrong tool.** A single DP pairwise alignment is correct for two sequences. For one query against thousands to millions of targets (genome-scale homology search) or for many-vs-many all-by-all (clustering, ortholog detection), the right tool is profile- or k-mer-indexed search, not iterated DP:
- BLASTP / DIAMOND -- standard query-vs-database baseline
- MMseqs2 (Steinegger & Soding 2017 Nat Biotech) -- ~400x faster than PSI-BLAST at higher sensitivity; iterative profile mode `--num-iterations 3` matches PSI-BLAST and approaches `jackhmmer`
- MMseqs2-GPU (Kallenborn et al 2025 Nat Methods 22:2024; Mirdita co-author) -- GPU-accelerated; ~177x faster than `jackhmmer` for single queries on one NVIDIA L40S; use when GPU is available and the dataset is sensitivity-bound
- jackhmmer (HMMER) -- gold standard for distant homology when run to convergence; slow but the most sensitive non-structural method
- Foldseek -- escape to structural search when both query and database have predicted structures (see `alignment/structural-alignment`)

Other failure modes:
- **Non-homologous sequences**: All DP aligners return an alignment regardless of homology. E-value or bit score is the homology gate, not the existence of an alignment.
- **Repetitive sequences**: Tandem repeats produce ambiguous, artifactually high-scoring alignments; mask first.
- **NUC.4.4 IUPAC partial matches**: Biopython's NUC.4.4 matrix scores partial-match IUPAC codes (e.g. `R` vs `A`) as +1 rather than +5; verify behaviour with `print(substitution_matrices.load('NUC.4.4'))` before relying on ambiguity-aware scoring.

## Related Skills

- alignment/multiple-alignment - Align three or more sequences with MAFFT, MUSCLE5, ClustalOmega
- alignment/alignment-io - Save alignments to files in various formats
- alignment/msa-parsing - Work with multiple sequence alignments
- alignment/msa-statistics - Calculate identity, similarity metrics
- alignment/structural-alignment - Twilight-zone alternative when sequence signal fails (Foldseek, TM-align, pLM aligners)
- alignment/alignment-trimming - Remove unreliable columns post-alignment
- sequence-manipulation/motif-search - Pattern matching in sequences

## References

- Karlin S, Altschul SF. 1990. Methods for assessing the statistical significance of molecular sequence features. PNAS 87:2264-2268.
- Schaffer AA et al. 2001. Improving the accuracy of PSI-BLAST protein database searches with composition-based statistics. NAR 29:2994-3005.
- Rost B. 1999. Twilight zone of protein sequence alignments. Prot Eng 12:85-94.
- Steinegger M, Soding J. 2017. MMseqs2 enables sensitive protein sequence searching for the analysis of massive data sets. Nat Biotech 35:1026-1028.
- Kallenborn F, Chacon A, Hundt C, Sirelkhatim H, Didi K, Cha S, Dallago C, Mirdita M, Schmidt B, Steinegger M. 2025. GPU-accelerated homology search with MMseqs2. Nat Methods 22(10):2024-2027.
- Sosic M, Sikic M. 2017. Edlib: a C/C++ library for fast, exact sequence alignment. Bioinf 33:1394-1395.
- Daily J. 2016. Parasail: SIMD C library for global, semi-global, and local pairwise sequence alignments. BMC Bioinf 17:81.
- Marco-Sola S et al. 2021. Fast gap-affine pairwise alignment using the wavefront algorithm. Bioinf 37:456-463.
- Marco-Sola S et al. 2023. Optimal gap-affine alignment in O(s) space. Bioinformatics 39(2):btad074.
- Yu YK, Altschul SF. 2005. The construction of amino acid substitution matrices for the comparison of proteins with non-standard compositions. Bioinf 21:902-911.
- Altschul SF, Erickson BW. 1985. Significance of nucleotide sequence alignments: a method for random sequence permutation that preserves dinucleotide and codon usage. MBE 2:526-538.
<!-- END FILE: alignment/pairwise-alignment/SKILL.md -->

## 子目录：alignment/structural-alignment

<!-- BEGIN FILE: alignment/structural-alignment/SKILL.md -->
---
name: bio-alignment-structural
description: Align protein structures using Foldseek 3Di, TM-align, US-align, DALI, or Foldmason for structural MSA. Predict, score, and superpose backbone coordinates when sequence identity is below the twilight zone or remote-homology detection is required. Use when sequence MSA fails (<25% identity), when the dark proteome is the target, when AlphaFoldDB / ESM Atlas search is needed, or when structural superposition is the goal.
tool_type: mixed
primary_tool: Foldseek
---

## Version Compatibility

Reference examples tested with: Foldseek 8+, TM-align 20220412+, US-align 20231222+, Foldmason 1+, BioPython 1.83+, pymol-open-source 3.0+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `foldseek --version`, `TMalign`, `USalign`, `foldmason --version`
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Structural Alignment

**"Align two protein structures"** -> Compute backbone-aware superposition and a fold-similarity score (TM-score, RMSD, or LDDT).
- CLI pairwise: `TMalign A.pdb B.pdb`, `USalign A.pdb B.pdb`
- CLI search at scale: `foldseek easy-search query/ AFDB result.m8 tmp/`
- CLI structural MSA: `foldmason easy-msa structures/*.pdb out tmp/`
- Python pairwise: `Bio.PDB.Superimposer`, or `subprocess` wrapping `TMalign` / `USalign` (see `examples/tm_align_pairwise.py`)
- GUI / scripted molecular-graphics superposition: ChimeraX `matchmaker`, PyMOL `super`/`cealign`

**"Find structural homologs of an AlphaFold model"** -> Search a structure database by 3Di-encoded structural alphabet (Foldseek) or by full TM-align rotation (DALI, US-align).

## When to Use Structural Alignment

| Sequence identity | Recommended approach |
|-------------------|---------------------|
| >= 40% | Sequence DP (Bio.Align, BLASTP) is sufficient |
| 25-40% | Sensitive sequence (MMseqs2, jackhmmer, profile-profile HHsearch) |
| 15-25% | Profile-profile (HHsearch) OR Foldseek if structures available |
| < 15% (dark proteome / twilight zone) | Foldseek (3Di), TM-align, US-align, pLM aligners |

Sequence alignment below 15% identity is statistically indistinguishable from random pairings. The exact twilight-zone cutoff is length-dependent: Rost 1999 (Prot Eng) showed the curve drops to 25% at length 80, 20% at length 250 -- short alignments need higher identity for the same statistical signal, so a 15-25% rule of thumb is shorthand for "twilight zone for proteins of typical domain size (~150-300 residues)". If reasonable structural models exist (PDB, AlphaFoldDB, ESMFold), structural alignment is far more reliable in this regime.

### Twilight-Zone Threshold Exceptions

For families with strong functional or structural constraint (ribosomal proteins, class I aminoacyl-tRNA synthetases with HIGH/KMSKS motifs, histone fold, cytochrome c with CXXCH, or any long alignment with well-distributed conservation), sequence MSA may remain reliable down to ~12-15% identity. Verify with a profile-profile method (HHsearch) before committing to structural alignment.

## Pairwise Structural Alignment Tool Selection

| Tool | Reference | Score | Best for |
|------|-----------|-------|----------|
| TM-align | Zhang & Skolnick 2005 NAR | TM-score | Single-chain pairwise; standard fold-similarity benchmark |
| US-align | Zhang et al 2022 Nat Methods | TM-score | Multi-chain protein, RNA, DNA, complexes; original successor to TM-align |
| Foldseek-Multimer | Kim et al 2025 Nat Methods | TM-score | Database-scale multi-chain complex search; 10-100x faster than US-align in pairwise mode, 1000-10000x in DB search; preferred at AFDB-multimer scale |
| FATCAT | Ye & Godzik 2003 Bioinf | FATCAT score | Flexible alignment with allowed twists/breaks |
| CE | Shindyalov & Bourne 1998 Prot Eng | CE score | Combinatorial extension of fragments; PDB legacy |
| DALI | Holm 2022 NAR | Z-score | Distance-matrix alignment; superior at TM 0.3-0.5 (twilight fold); operates on AFDB at scale |
| Bio.PDB.Superimposer | Cock et al 2009 Bioinf | RMSD | Pure-Python superposition with known atom correspondence |

TM-align and US-align report two TM-scores by default: one normalised by chain 1 length and one by chain 2 length. The standard fold-similarity metric for asymmetric reporting is the larger of the two (effectively normalising by the shorter chain), since TM-score is length-asymmetric. The `-a T` flag adds a third score normalised by the average of the two chain lengths (useful for symmetric clustering). **TM > 0.5** indicates the same fold; **TM > 0.8** indicates equivalent topology / close structural relationship; **TM < 0.2** indicates random structural similarity. RMSD alone is misleading: RMSD scales with length, depends on outliers, and an "optimization RMSD" (used to fit) is not the same as an "evaluation RMSD" (used to compare). Always report TM-score alongside RMSD and the alignment length.

| Metric | Threshold | Source / Interpretation |
|--------|-----------|-------------------------|
| TM-score | > 0.5 | Same fold (Zhang & Skolnick 2004 Proteins; reported by TM-align, US-align, Foldseek, DALI) |
| TM-score | > 0.8 | Equivalent topology (homologous) |
| TM-score | < 0.2 | Random structural similarity |
| DALI Z-score | > 20 | Definitely homologous (Holm 2020 Methods Mol Biol) |
| DALI Z-score | 8 - 19 | Probable homology |
| DALI Z-score | 2 - 8 | Candidate; verify with TM-score or biology |
| DALI Z-score | < 2 | Not significant (random) |
| GDT-TS | > 50 | Correct fold (CASP/LGA scoring; reported by LGA, MaxCluster, OpenStructure -- not by TM-align/Foldseek) |
| LDDT | > 0.6 | Conventional cutoff for "correctly modelled" residue (Mariani et al 2013 Bioinf shows the score is fold-architecture-dependent and does not define a universal hard threshold; >= 0.6 is widely used in CAMEO and Foldseek output as a working cutoff) |
| RMSD | < 2 A over >100 residues | Strong superposition; below 1.5 A is excellent |

### Foldseek vs DALI: Modern Comparison

Both target structural homolog search, but with different strengths:

| Question | Foldseek | DALI |
|----------|----------|------|
| Find any same-fold homolog quickly | YES (3Di indexed; 1000-1M seq/s) | Slow (full distance matrix) |
| Sensitivity at TM > 0.5 (same-fold) | Comparable to TM-align | Slightly higher recall |
| Sensitivity at TM 0.3-0.5 (twilight fold) | Recall drops sharply | DALI Z-score retains signal (Holm 2022) |
| Alignment quality for indel-rich pairs | Local 3Di+AA; can miss large indels | Distance-matrix optimal handles indels well |
| AFDB-scale all-vs-all | Tractable | Now tractable post-2022 (Holm DALI server update) |

Practical workflow for remote homology: (1) Foldseek `easy-search` to retrieve same-fold candidates fast, (2) for hits with TM < 0.5 or with structural-indel rich alignments, re-align with DALI for higher-quality residue equivalences. The two tools are complementary; Foldseek-only misses some twilight-fold relationships, DALI-only misses the AFDB-scale opportunity.

### TM-score Threshold Caveats

Apply the 0.5 same-fold rule only to globular domains of ~100-300 residues; for chains <60 residues TM > 0.5 occurs by chance ~3-5%, so use Xu & Zhang 2010's length-aware Gumbel p-value instead. Always report both length-normalised TM-scores (or use `-a T` for the symmetrised average) and pair RMSD with the atom count (`(RMSD, n_atoms_used)`); raw RMSD without length normalisation is misleading.

### TM-align Pairwise Run

**Goal:** Compute TM-score and RMSD between two structures and write a superposed PDB.

**Approach:** Invoke TMalign or USalign with output flags; parse the structured output for downstream filtering.

```bash
TMalign chainA.pdb chainB.pdb -o superposed.sup
TMalign chainA.pdb chainB.pdb -outfmt 2

USalign chainA.pdb chainB.pdb -mol prot -outfmt 2
USalign complex_A.pdb complex_B.pdb -mm 1 -ter 0
```

`-outfmt 2` returns tabular output (one line per pair). For multi-chain complexes, US-align with `-mm 1 -ter 0` aligns full assemblies; TM-align is single-chain only.

**US-align multi-chain score interpretation.** US-align `-mm 1 -ter 0` produces multiple TM-scores per complex: normalised by query length, normalised by template length, and (for symmetric homo-oligomers) the best-matching chain permutation. For different stoichiometries (query hetero-A2B2 vs template hetero-A4B4), use `-mm 4` and `-byresi 0`. The "best-of" TM-score is the appropriate cross-complex homology metric; per-chain TM-scores serve as a sanity check (low per-chain + high complex TM = topology match without local fold conservation, suggests promiscuous interaction not deep homology). See Zhang et al 2022 Nat Methods for the full mode taxonomy.

### Foldseek-Multimer for Database-Scale Complex Search

For multi-chain complex search at AFDB-multimer scale (~214k entries) or against PDB complexes, US-align is too slow; Foldseek-Multimer (Kim et al 2025 Nat Methods) is the modern default. Two modes share the chain-pairing prefilter:

| Mode | Algorithm | Use when |
|------|-----------|----------|
| `Foldseek-MM` (default) | 3Di+AA Gotoh per chain pair | Fast database search; default speed-sensitivity tradeoff |
| `Foldseek-MM-TM` | TM-align per chain pair after prefilter | Top-hit refinement with full TM-score |

```bash
foldseek easy-multimersearch query_complex.pdb afdb_multimer result tmp/
foldseek easy-multimersearch query_complex.pdb afdb_multimer result tmp/ --multimer-tm-threshold 0.5

foldseek easy-multimercluster *.pdb cluster_result tmp/ --multimer-tm-threshold 0.65
```

Decision guide: pairwise complex pair on a few hundred targets -> US-align with `-mm 1 -ter 0`. Database search across thousands to millions of complex entries -> Foldseek-Multimer. For AFDB-Multimer or PDB100-Multimer scale, US-align is computationally infeasible; Foldseek-Multimer matches US-align chain-pairing in >99% of cases at 10-100x speedup pairwise and 10^3-10^4x in database mode (Kim et al 2025 benchmark).

**Reporting convention:** Always quote BOTH the multimer TM-score (whole-complex) AND the worst per-chain TM-score; high multimer TM with one low per-chain score signals topology-matched but locally divergent chains (often promiscuous binders or paralog swaps), which is biologically distinct from a uniformly-conserved complex.

### Bio.PDB.Superimposer

**Goal:** Superpose a known atom correspondence and compute RMSD without running an external aligner.

**Approach:** Use when residue equivalence is already established (e.g. same sequence, different conformations). For unknown correspondence, prefer TM-align / US-align.

```python
from Bio.PDB import PDBParser, Superimposer

parser = PDBParser(QUIET=True)
mobile_atoms = list(parser.get_structure('mobile', 'mobile.pdb').get_atoms())
reference_atoms = list(parser.get_structure('ref', 'reference.pdb').get_atoms())

ca_mobile = [a for a in mobile_atoms if a.get_id() == 'CA']
ca_reference = [a for a in reference_atoms if a.get_id() == 'CA']
n = min(len(ca_mobile), len(ca_reference))

sup = Superimposer()
sup.set_atoms(ca_reference[:n], ca_mobile[:n])
sup.apply(mobile_atoms)
print(f'RMSD: {sup.rms:.3f} A over {n} CA atoms')
```

## Structural Search at Scale: Foldseek

Run Foldseek for AlphaFoldDB-scale structural search; it indexes a 20-letter 3Di alphabet for thousand- to million-fold speedup over TM-align at comparable same-fold sensitivity.

```bash
# Search query structures against AFDB (default: --alignment-type 2)
foldseek easy-search query.pdb afdb_database result.m8 tmp/

# Refine top hits with full TM-align rotation (slower but global TM-score)
foldseek easy-search query.pdb afdb_database result.m8 tmp/ --alignment-type 1

# All-versus-all clustering at TM > 0.5
foldseek easy-cluster structures/*.pdb cluster_result tmp/ --tmscore-threshold 0.5

# Custom output columns
foldseek easy-search query.pdb afdb_database result.m8 tmp/ \
    --format-output query,target,evalue,alntmscore,qtmscore,ttmscore,lddt,bits
```

| Foldseek `--alignment-type` | Algorithm | Use when |
|-----------------------------|-----------|----------|
| 0 | 3Di Gotoh-Smith-Waterman (local) | Not recommended; 3Di alone, no amino-acid signal |
| 1 | TMalign (global) | Refine top hits with full TM-score; slow |
| 2 | 3Di+AA Gotoh-Smith-Waterman (local) | Default; best speed-sensitivity tradeoff |

### pLDDT-Filtering AlphaFold Structures Before Foldseek

Mask residues with pLDDT < 70 before Foldseek indexing or search; their backbone coordinates encode as random 3Di letters and contaminate hits below TM ~ 0.4. AFDB clusters from Barrio-Hernandez et al 2023 are pre-filtered; ESMFold predictions need the same step.

```bash
# Mask low-pLDDT residues during database creation (B-factor column stores pLDDT)
# The *.pdb glob requires shell expansion; for Python subprocess calls use glob.glob()
# to expand the file list before passing as argv.
foldseek createdb --mask-bfactor-threshold 70.0 *.pdb afdb_masked
```

## Structural Multiple Sequence Alignment

| Tool | Reference | Best for |
|------|-----------|----------|
| Foldmason | Gilchrist et al 2026 Science 391:485 | Billion-protein-scale structural MSA on AFDB; the structural counterpart to MAFFT |
| 3D-Coffee / Expresso | Notredame group | <100 chains with mixed PDB and sequence input |
| mTM-align | Dong et al 2018 Bioinf | Multiple structure alignment; output suitable for tree building. Server: `yanglab.qd.sdu.edu.cn/mTM-align/` (Yang Lab moved from Nankai to Shandong University in 2021; verify URL before use) |
| PROMALS3D | Pei, Kim & Grishin 2008 NAR | Hybrid sequence-structure profile MSA; uses PSI-BLAST + DALI/SAP templates |
| MUSTANG | Konagurthu et al 2006 Proteins | Pure structural MSA via residue-residue equivalences |

### Foldmason easy-msa

```bash
foldmason easy-msa structures/*.pdb result tmp/ \
    --refine-iters 100 \
    --report-mode 1

# Outputs: result_aa.fa (amino-acid MSA), result_3di.fa (3Di MSA), result.nw (guide tree), result.html (LDDT report)
```

`--refine-iters` controls iterative MSA refinement; `--report-mode 1` produces an HTML report with per-column LDDT confidence. The 3Di MSA can be used directly for evolutionary analyses where structure rather than sequence is the appropriate signal.

**Per-column LDDT extraction:** Run with `--report-mode 2` to produce machine-readable JSON output:

```bash
foldmason easy-msa structures/*.pdb result tmp/ --report-mode 2
# Produces result.json with per-column LDDT in machine-readable form
```

```python
import json
with open('result.json') as f:
    report = json.load(f)
lddt_per_column = report.get('per_column_lddt')
```

Verify the exact JSON schema with `foldmason easy-msa --help` and inspect a sample `result.json`; the field name may evolve across releases.

## Hybrid Sequence-Structure Approaches

When a small dataset has known structures or templates, hybrid tools dramatically improve MSA accuracy:

- **T-Coffee Expresso** (Notredame et al) -- PSI-BLAST searches PDB for templates, runs SAP or TM-align pairwise structural library, then T-Coffee consistency over the resulting library. Reported in Notredame-group benchmarks to substantially improve correct-column rate over sequence-only T-Coffee. Requires internet access for PSI-BLAST and PDB template fetching; for offline / reproducible runs use 3D-Coffee with locally curated templates.
- **3D-Coffee** -- user-supplied PDB templates with `-template_file templates.txt`; uses SAP or TM-align as the structural method.
- **PROMALS3D** (Pei, Kim & Grishin 2008 NAR) -- PSI-BLAST profiles + secondary-structure prediction + DALI/SAP templates; used heavily in the Grishin lab's superfamily annotations. PROMALS3D server availability has been intermittent; if unreachable, T-Coffee Expresso (mode `expresso`) is a current alternative for structure-informed sequence MSA.

```bash
t_coffee input.fasta -mode expresso -output fasta_aln -outfile aligned.fasta

t_coffee input.fasta -template_file templates.txt -mode 3dcoffee
```

## AlphaFold Integration

The "predict-then-align" workflow has become standard for remote-homology problems:

1. Search sequence with MMseqs2 / jackhmmer to seed an MSA.
2. Predict structure with AlphaFold2 (ColabFold), ESMFold, or AlphaFold3 -- see `structural-biology/modern-structure-prediction` for prediction workflows.
3. Search the predicted structure against AFDB or PDB with Foldseek.
4. Use Foldmason or PROMALS3D to derive a structure-aware MSA from the hits.
5. Refine sequence MSA using the structure-derived column equivalences.

Search AFDB clusters (~2.3 M Foldseek-derived clusters from Barrio-Hernandez et al 2023) as the canonical remote-homology entry point; supplement with the ESM Atlas (~600 M ESMFold metagenomic structures) when AFDB recall is insufficient. For pLDDT semantics and curated AlphaFoldDB entry handling, see `structural-biology/alphafold-predictions`.

## pLM-Based Sequence Aligners

Run a pLM aligner (TM-Vec, vcMSA, DEDAL, pLM-BLAST) when no structure is available but identity is in the twilight zone (<15-25%). They recover signal that DP aligners miss but do NOT replace TM-align / US-align when structures exist; use them as a complementary first pass.

| Tool | Reference | Embedding source |
|------|-----------|------------------|
| vcMSA | McWhite, Armour-Garb & Singh 2023 Genome Res | ProtT5 vector clustering for MSA (alpha-stage tool per its repo README; last release Oct 2023; test on representative inputs before pipeline use) |
| DEDAL | Llinares-Lopez et al 2023 Nat Methods | Differentiable end-to-end alignment with pLM features |
| TM-Vec | Hamamsy et al 2024 Nat Biotech | TM-score prediction from ProtT5 embeddings (active fork: `valentynbez/tmvec`; original `tymor22/tm-vec` is in limited maintenance) |
| pLM-BLAST | Kaminski et al 2023 Bioinf | BLAST-style hits via pLM cosine similarity |

These run on raw sequence (no structure required) and recover signal at <15% identity that DP aligners miss entirely. They do NOT replace structural alignment when structures exist; treat them as complementary.

**pLM aligner accuracy ceiling.** TM-Vec, vcMSA, and DEDAL predict alignment-equivalent quantities (TM-score, alignment columns) from sequence-only embeddings. Hamamsy et al 2024 report TM-Vec TM-score prediction RMSE ~0.07 on SCOP -- sufficient for coarse filtering ("is this hit at all structurally similar?") but NOT for fine-grained ranking (e.g. choosing among hits with TM 0.5-0.7). For final structural-similarity scoring, run TM-align or US-align on predicted structures (ColabFold + USalign) rather than relying on the pLM-predicted score.

## Visualisation and Inspection

Structural alignments are read by viewing the superposed structures, not the sequence text:

```bash
# PyMOL headless: -cq runs without GUI/quietly; -d passes commands directly
pymol -cq -d "load reference.pdb; load mobile.pdb; super mobile, reference; ray 800,600; png fig.png"

# ChimeraX (modern, replaces Chimera): MatchMaker uses Needleman-Wunsch + iterative refinement
ChimeraX --cmd "open reference.pdb mobile.pdb; matchmaker #2 to #1; save fig.png"
```

PyMOL `super` performs cycle-fitting for distantly related structures (better than `align` when sequence identity is low); `cealign` runs CE; `tmalign` (PyMOL plugin) wraps TM-align. ChimeraX MatchMaker is the modern replacement and uses Needleman-Wunsch + iterative refinement with the option to invoke external tools.

## Decision Tree by Goal

| Goal | First-line tool |
|------|-----------------|
| Two structures, known correspondence | `Bio.PDB.Superimposer` |
| Two structures, unknown correspondence | TMalign or USalign |
| Multi-chain complex, pairwise | USalign with `-mm 1 -ter 0` |
| Multi-chain complex, database search | `foldseek easy-multimersearch` (Foldseek-Multimer) |
| Twilight-fold homology (TM 0.3-0.5) | DALI (Z-score ranks low-similarity hits better than Foldseek) |
| Structural homolog search at AFDB scale (single chain) | `foldseek easy-search` |
| All-vs-all clustering of structures | `foldseek easy-cluster --tmscore-threshold 0.5` |
| Multiple structure alignment, < 100 chains | T-Coffee Expresso or mTM-align |
| Multiple structure alignment, > 1000 chains | Foldmason `easy-msa` |
| Hybrid sequence-structure MSA | PROMALS3D or T-Coffee Expresso |
| pLM aligner for dark proteome | TM-Vec, vcMSA, DEDAL |
| Distant homology with no structures | Predict with ColabFold/ESMFold first, then Foldseek |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| TM-align "atoms not enough" | Single-residue chains or ligand-only PDB | Filter to canonical amino acids before running |
| Foldseek "no hits" | Wrong database format | Run `foldseek databases` to confirm AFDB / PDB100 download |
| Bio.PDB Superimposer "different number of atoms" | Atom selection mismatch | Filter both lists to common atom names (CA only, or N/CA/C/O) |
| TM-score normalised by length 1 | Used `-L 1` | Drop `-L` flag; default normalisation is correct |
| Foldmason output empty | Input structures not in same chain ID | Renumber and rename chains uniformly before running |

## Related Skills

- alignment/multiple-alignment - Sequence MSA when identity > 25%; complementary for hybrid tools
- alignment/pairwise-alignment - Sequence pairwise; use first to filter before structural alignment
- alignment/msa-parsing - Parse and analyze structural MSA output for downstream metrics
- alignment/msa-statistics - Apply per-column conservation to structurally-derived MSAs
- alignment/alignment-io - Read and convert structural MSA files for downstream tools
- alignment/alignment-trimming - Trim structural MSAs the same way as sequence MSAs
- structural-biology/modern-structure-prediction - Predict structures (AlphaFold2/3, ESMFold) used as input
- structural-biology/alphafold-predictions - Curated AFDB / pLDDT handling
- structural-biology/structure-navigation - Map alignment columns to PDB residues
- phylogenetics/modern-tree-inference - Trees from structural MSAs (Foldmason output works directly)

## References

- van Kempen M et al. 2024. Fast and accurate protein structure search with Foldseek. Nat Biotech 42:243-246.
- Kim W, Mirdita M, Levy Karin E, Gilchrist CLM, Schweke H, Soding J, Levy E, Steinegger M. 2025. Rapid and sensitive protein complex alignment with Foldseek-Multimer. Nat Methods 22:469-472.
- Zhang Y, Skolnick J. 2005. TM-align: a protein structure alignment algorithm based on the TM-score. NAR 33:2302-2309.
- Zhang C, Shine M, Pyle AM, Zhang Y. 2022. US-align: universal structure alignments of proteins, nucleic acids, and macromolecular complexes. Nat Methods 19:1109-1115.
- Holm L. 2020. Using Dali for protein structure comparison. Methods Mol Biol 2112:29-42 (Z-score interpretation thresholds).
- Holm L. 2022. Dali server: structural unification of protein families. NAR 50:W210-W215.
- Gilchrist CLM et al. 2026. Foldmason: multiple protein structure alignment at scale with 3Di. Science 391(6784):485-488.
- Barrio-Hernandez I et al. 2023. Clustering predicted structures at the scale of the known protein universe. Nature 622:637-645.
- Hamamsy T et al. 2024. Protein remote homology detection and structural alignment using deep learning. Nat Biotech 42:975-985.
- Xu J, Zhang Y. 2010. How significant is a protein structure similarity with TM-score = 0.5? Bioinf 26:889-895.
<!-- END FILE: alignment/structural-alignment/SKILL.md -->

<!-- END CATEGORY: alignment -->

