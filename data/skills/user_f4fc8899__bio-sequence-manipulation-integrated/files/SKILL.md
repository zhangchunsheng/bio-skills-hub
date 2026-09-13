---
slug: bio-sequence-manipulation-integrated
version: 1.0.0
displayName: "序列操作 / Core sequence operations"
name: bio-sequence-manipulation-integrated
summary: >-
  中文：序列操作综合技能，整合 7 个相关专题，覆盖序列基础操作：反向互补、转录翻译、序列切片、密码子分析、基序搜索、序列性质计算。 English: Integrated Core sequence operations skill covering 7 related topics, including Core sequence operations: reverse complement, transcription/translation, slicing, codon usage analysis, motif search, and sequence properties.
description: >-
  中文：这是一个面向序列操作的综合生物信息学 Skill，整合当前分类下 7 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：序列基础操作：反向互补、转录翻译、序列切片、密码子分析、基序搜索、序列性质计算。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Bio.Seq, Bio.SeqUtils, Bio.SeqUtils.CodonAdaptationIndex。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Core sequence operations, combining 7 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Core sequence operations: reverse complement, transcription/translation, slicing, codon usage analysis, motif search, and sequence properties. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Bio.Seq, Bio.SeqUtils, Bio.SeqUtils.CodonAdaptationIndex. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# sequence-manipulation 分类 Skill 整合版

> 本文件整合同一主分类目录下 7 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: sequence-manipulation -->

## 子目录：sequence-manipulation/codon-usage

<!-- BEGIN FILE: sequence-manipulation/codon-usage/SKILL.md -->
---
name: bio-codon-usage
description: Analyze codon usage and calculate CAI (Codon Adaptation Index), RSCU, and Nc with Biopython, and produce naive max-CAI codon-optimized sequences. Use when scoring a gene's codon bias against a host, optimizing a CDS for heterologous expression, or studying synonymous codon selection.
tool_type: python
primary_tool: Bio.SeqUtils.CodonAdaptationIndex
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Codon Usage

Analyze codon usage patterns, score adaptation to a host, and optimize coding sequences for expression.

**"Analyze codon usage"** -> Count codons in a coding sequence, compute frequencies and bias metrics.
- Python: `Counter` on in-frame triplets + RSCU/Nc helpers (BioPython + standard library)

**"Score this gene against a host"** -> Compute the Codon Adaptation Index from a reference set of highly expressed genes.
- Python: `CodonAdaptationIndex(reference_seqs).calculate(query)` (BioPython)

**"Optimize codons for expression"** -> Replace each codon with the host's single most-preferred synonymous codon.
- Python: `CodonAdaptationIndex(reference_seqs).optimize(seq)` (BioPython)

## The governing principle

CAI is meaningless without an expression-biased reference. The relative-adaptiveness weights (w) must be built from the **highly expressed genes of the TARGET organism** (ribosomal proteins, elongation factors). A CAI computed against a whole-genome average, or against the wrong organism, is a number with no biological meaning. There is no bundled reference index in modern Biopython, so the reference set is always the caller's responsibility.

Two silent traps dominate this skill:
- **Out-of-frame input is silently corrupted.** `calculate` blindly steps `range(0, len, 3)` from position 0; it never checks the reading frame. A frame-shifted CDS returns a plausible CAI computed from garbage codons. Frame correctness is the caller's job (length divisible by 3, starts at the first base of codon 1).
- **Naive max-CAI optimization can REDUCE expression.** `optimize()` is the textbook max-CAI output (single most-frequent codon per amino acid). It is blind to the translation ramp, 5' mRNA structure, GC extremes, cryptic regulatory elements, and codon-pair bias. It is a starting point to screen, never a final design. Failure is silent: correct protein, high CAI, poor expression.

## CRITICAL API migration (Biopython 1.82)

`Bio.SeqUtils.CodonUsage` and `Bio.SeqUtils.CodonUsageIndices` were **removed in Biopython 1.82**. Any code calling `generate_index()`, `set_cai_index()`, `cai_for_gene()`, `print_index()`, or importing `SharpEcoliIndex` raises ImportError on any modern install. The replacement is a redesigned class imported directly from `Bio.SeqUtils`:

```python
from Bio.SeqUtils import CodonAdaptationIndex  # NOT Bio.SeqUtils.CodonUsage (removed)
```

| Removed (<=1.81) | Replacement (>=1.82) |
|------------------|----------------------|
| `CodonAdaptationIndex()` then `generate_index(fasta)` | `CodonAdaptationIndex(reference_seqs, table=...)` constructor |
| `cai.cai_for_gene(seq)` | `cai.calculate(seq)` |
| `cai.set_cai_index(d)` | `cai.update(d)` (it is a dict subclass) |
| `SharpEcoliIndex` (bundled) | none -- build from a supplied reference CDS set |
| `cai.print_index()` | iterate the object: `for codon, w in cai.items()` |

## Required Imports

```python
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqUtils import CodonAdaptationIndex, GC123
from Bio.Data.CodonTable import standard_dna_table
from Bio.Data import CodonTable
from collections import Counter
```

## Codon Adaptation Index (CAI)

**Goal:** Measure how closely a gene's codon usage matches the highly expressed genes of a host organism.

**Approach:** Build a `CodonAdaptationIndex` from a reference set of highly expressed CDS (the constructor computes per-codon relative adaptiveness w), then score query sequences with `calculate` (0-1, higher = better adapted).

```python
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqUtils import CodonAdaptationIndex
from Bio.Data.CodonTable import standard_dna_table

# Reference = highly expressed genes of the TARGET host (ribosomal proteins, EFs).
# Parse a FASTA yourself; there is no bundled index. Pass str/Seq/SeqRecord.
reference_seqs = list(SeqIO.parse('highly_expressed_genes.fasta', 'fasta'))
cai = CodonAdaptationIndex(reference_seqs, table=standard_dna_table)

query = Seq('ATGAAACGTGCTGAAGCTAAATAA')
score = cai.calculate(query)   # 0-1; the query MUST be in-frame (see governing principle)
print(f'CAI: {score:.3f}')
```

`CodonAdaptationIndex` **is a dict subclass** -- the codon->w mapping is the object itself. Inspect or override weights directly:

```python
print(cai['GCT'])         # relative adaptiveness of Ala codon GCT
cai.update({'GCT': 0.9})  # override a weight (replaces the old set_cai_index)
```

Verified behavior (Biopython >=1.82):
- **ATG (Met) and TGG (Trp) are excluded** from CAI -- single-codon families, w is always 1.
- **Stop codons are excluded.**
- **Unobserved codons get w = 0.5** (Sharp & Li), softly down-weighted; no division-by-zero.
- **Case-insensitive** -- both the constructor and `calculate` uppercase internally.
- An illegal codon (non-ACGT) in a reference raises `ValueError`; an illegal or trailing-partial codon in a query raises `TypeError`. Out-of-frame input does NOT raise -- it is silently mis-scored.

## RSCU = w is built from these ratios

CAI weights come from RSCU. w_ij = RSCU_ij / RSCU_jmax = (codon count) / (count of the most-used synonymous codon in that family); CAI = exp((1/L) * sum ln w). RSCU itself = observed count / expected-if-uniform within a synonymous family (=1 no bias, >1 over-used, <1 under-used). RSCU normalizes away amino-acid composition, which is why w is built from RSCU ratios rather than raw frequencies.

**Goal:** Quantify synonymous codon bias to detect translational selection or mutational pressure.

**Approach:** Group codons by amino acid via the codon table, then divide each codon's observed count by the family mean.

```python
from Bio.Data import CodonTable
from collections import Counter

def count_codons(seq):
    s = str(seq).upper()
    return Counter(s[i:i+3] for i in range(0, len(s) - 2, 3))

def calculate_rscu(seq, table_id=1):
    '''RSCU per codon: observed / expected-if-uniform within its synonymous family'''
    table = CodonTable.unambiguous_dna_by_id[table_id]
    counts = count_codons(seq)
    back_table = {}
    for codon, aa in table.forward_table.items():
        back_table.setdefault(aa, []).append(codon)
    rscu = {}
    for aa, codons in back_table.items():
        total = sum(counts.get(c, 0) for c in codons)
        expected = total / len(codons) if codons else 0
        for codon in codons:
            rscu[codon] = counts.get(codon, 0) / expected if expected > 0 else 0
    return rscu
```

## Codon optimization for expression

**Goal:** Generate a host-adapted CDS that preserves the protein.

**Approach:** `optimize()` swaps each amino acid for the host's single most-preferred synonymous codon (max-CAI). Always confirm the protein is unchanged, then screen the design against the tradeoffs below.

```python
opt = cai.optimize(query, seq_type='DNA', strict=True)
assert opt.translate() == query.translate()   # protein must be identical
```

`optimize(sequence, seq_type='DNA'|'RNA'|'protein', strict=True)`: `strict=True` **raises ValueError on a tie** (two equally-preferred codons, e.g. `'TTT and TTC are equally preferred.'`); `strict=False` warns and picks one.

### Why naive max-CAI can HURT expression

`optimize()` is blind to everything except single-codon frequency. Screen the output for:
- **The translation ramp** (Tuller et al. 2010): a conserved profile of slow (rare) codons over the first ~30-50 codons spaces ribosomes; flattening it can lower yield and increase misfolding.
- **5' mRNA secondary structure:** strong folding near the start codon impedes initiation. Minimize 5' free energy, sometimes against CAI.
- **GC extremes:** swaps that push GC very high create stable hairpins; very low GC destabilizes.
- **Cryptic elements created by swaps:** splice sites, internal Shine-Dalgarno/RBS, polyadenylation signals, restriction sites, AU-rich destabilizing elements -- silent in protein, corrupting in expression.
- **Codon-pair bias:** decoding efficiency depends on adjacent codon pairs; CAI scores single codons only.

### tAI -- the supply-side alternative

The tRNA Adaptation Index (dos Reis et al. 2004) weights each codon by **tRNA gene copy number** (a proxy for tRNA abundance) scaled by wobble-pairing efficiency at the third position. Where tRNA copy number is a good abundance proxy, tAI tracks expression and elongation speed better than CAI. tAI is **not in Biopython** -- use the R `tAI` package or reimplement.

## Synonymous bias by other metrics

### Effective Number of Codons (Nc)

A reference-free bias measure (lower = more biased; range ~20 fully biased to 61 unbiased). The helper below is a simplified per-amino-acid approximation: Wright's published estimator averages the homozygosity F WITHIN each degeneracy class (2-, 3-, 4-, 6-fold) before combining as `Nc = 2 + 9/F2 + 1/F3 + 5/F4 + 3/F6`. The endpoints agree, but intermediate values will not match codonW/standard Nc when families in a class have unequal F. For comparable Nc, average F by class per Wright (1990) or use codonW.

```python
import math
from Bio.Data import CodonTable

def effective_nc(seq, table_id=1):
    table = CodonTable.unambiguous_dna_by_id[table_id]
    counts = count_codons(seq)
    aa_groups = {}
    for codon, aa in table.forward_table.items():
        aa_groups.setdefault(aa, []).append(codon)
    nc_sum = 0
    for aa, codons in aa_groups.items():
        n = sum(counts.get(c, 0) for c in codons)
        if n <= 1:
            continue
        pi_sq = sum((counts.get(c, 0) / n) ** 2 for c in codons)
        F = (n * pi_sq - 1) / (n - 1)
        nc_sum += 1 / F if F > 0 else len(codons)
    return nc_sum if nc_sum > 0 else 61
```

### GC at codon positions (GC123)

```python
from Bio.SeqUtils import GC123

gc_total, gc_pos1, gc_pos2, gc_pos3 = GC123(seq)  # four PERCENTAGES (0-100)
print(f'GC3 (wobble): {gc_pos3:.1f}%')             # correlates with genome GC
```

GC123 returns percentages (0-100), unlike `gc_fraction` which returns 0-1. GC3 at the wobble position usually tracks overall genome GC content.

## Codon tables

```python
from Bio.Data import CodonTable

table = CodonTable.unambiguous_dna_by_id[1]   # standard genetic code
print(table.start_codons, table.stop_codons)
print(table.forward_table['ATG'])             # 'M'
```

| ID | Name | Organism |
|----|------|----------|
| 1 | Standard | Most nuclear genomes |
| 2 | Vertebrate Mitochondrial | Human/mouse mito |
| 4 | Mold/Protozoan Mitochondrial | Fungi, protozoa mito |
| 5 | Invertebrate Mitochondrial | Insects, worms mito |
| 11 | Bacterial/Plastid | E. coli, chloroplasts |

Pass the matching `table=` to `CodonAdaptationIndex` when scoring mitochondrial or bacterial genes.

## Metric reference

| Metric | Range | Reference needed | Interpretation |
|--------|-------|------------------|----------------|
| CAI | 0-1 | Highly expressed genes of the host | Higher = better adapted |
| RSCU | 0-N | None (within-sequence) | 1 = no bias, >1 over-used |
| Nc | ~20-61 | None | Lower = more biased |
| GC3 | 0-100% | None | GC at wobble position |
| tAI | 0-1 | tRNA gene copy numbers | Higher = better tRNA supply |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ImportError: cannot import name 'CodonUsage'` | `Bio.SeqUtils.CodonUsage` removed in 1.82 | `from Bio.SeqUtils import CodonAdaptationIndex` |
| `AttributeError: 'CodonAdaptationIndex' object has no attribute 'generate_index'` | Old API on new class | Build in the constructor; score with `calculate` |
| Plausible CAI from a frame-shifted CDS | Out-of-frame input silently mis-scored | Confirm frame: length divisible by 3, starts at codon 1 |
| CAI near 1 for every gene | Reference set is whole-genome, not expression-biased | Use only highly expressed genes of the target host |
| `ValueError: ... equally preferred` | `optimize(strict=True)` hit a tie | Pass `strict=False`, or curate weights with `update` |
| High CAI but poor expression in the lab | Max-CAI ignores ramp / 5' structure / cryptic sites | Screen `optimize()` output; treat it as a draft |

## Related Skills

- transcription-translation - Translate CDS and select the correct codon table
- sequence-properties - GC123 and per-position GC content
- sequence-io/read-sequences - Parse reference CDS from FASTA/GenBank for CAI training
- database-access/entrez-fetch - Fetch highly expressed gene sets from NCBI for CAI references

## References

Sharp PM, Li WH (1987) The codon adaptation index -- a measure of directional synonymous codon usage bias, and its potential applications. Nucleic Acids Res 15(3):1281-1295.

dos Reis M, Savva R, Wernisch L (2004) Solving the riddle of codon usage preferences: a test for translational selection. Nucleic Acids Res 32(17):5036-5044.

Tuller T, Carmi A, Vestsigian K, Navon S, Dorfan Y, Zaborske J, Pan T, Dahan O, Furman I, Pilpel Y (2010) An evolutionarily conserved mechanism for controlling the efficiency of protein translation. Cell 141(2):344-354.

Wright F (1990) The 'effective number of codons' used in a gene. Gene 87(1):23-29.
<!-- END FILE: sequence-manipulation/codon-usage/SKILL.md -->

## 子目录：sequence-manipulation/motif-search

<!-- BEGIN FILE: sequence-manipulation/motif-search/SKILL.md -->
---
name: bio-motif-search
description: Find sequence motifs, degenerate IUPAC patterns, and transcription-factor binding sites in DNA/RNA using Biopython and regex, including position weight matrix (PWM/PSSM) scoring. Use when locating regulatory elements, counting overlapping motif occurrences, scanning for binding-site matches above a significance threshold, or reading motif matrices from JASPAR/MEME/TRANSFAC files. For restriction enzyme sites, use restriction-analysis/restriction-sites.
tool_type: python
primary_tool: Bio.motifs
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Motif Search

**"Search for a sequence motif or binding-site pattern"** -> Scan sequences for a fixed motif, a degenerate IUPAC consensus, or a probabilistic PWM, on one or both strands, and locate transcription-factor binding sites, regulatory elements, or custom patterns.
- Python: `Bio.SeqUtils.nt_search` (IUPAC + overlaps), `re` (regex/lookahead), `Bio.motifs` (PWM/PSSM scoring + matrix file parsing)

## The Governing Principle

Two silent failures dominate motif searching; both return a plausible-but-wrong answer with no error:

1. **Overlapping matches are dropped.** `str.count`, `str.find`, and `re.findall` consume the string left to right, so a motif that overlaps its own next occurrence is undercounted. Target `AAGCGCGCGAA`, motif `GCGC`: `str.count` returns 1, the true answer is 2 (starts at positions 2 and 4). Use a zero-width lookahead `re.finditer(r'(?=(GCGC))', target)` or `Bio.SeqUtils.nt_search`, both of which report overlaps.
2. **A PSSM score is a likelihood in bits, not a probability.** `pssm.calculate` returns log2-odds versus background. A "high-looking" threshold chosen by eye is arbitrary and non-reproducible; derive the threshold from the score distribution at a chosen false-positive rate. And a PSSM scans only the strand it is given, so scoring just the forward strand silently misses roughly half of real sites on double-stranded DNA.

## Which Approach for Which Question

| Question | Tool |
|----------|------|
| Position of first exact hit | `str.find` / `Seq.find` (returns -1 if absent) |
| All exact hits, possibly overlapping | `re.finditer(r'(?=(motif))', seq)` |
| Degenerate IUPAC consensus (e.g. `GATNNTC`), with overlaps | `Bio.SeqUtils.nt_search(seq, motif)` |
| Flexible / repeat / variable-spacer pattern | `re` with explicit character classes and quantifiers |
| Graded match to many aligned sites (binding sites) | `Bio.motifs` PWM -> PSSM, score and threshold |
| Match significance / false-positive control | `pssm.distribution(...).threshold_fpr(fpr)` |
| Restriction enzyme recognition sites | restriction-analysis/restriction-sites |

## IUPAC Degenerate Motifs

A degenerate motif expands each ambiguity code to a regex character class:

| Code | Class | Code | Class | Code | Class |
|------|-------|------|-------|------|-------|
| N | `[ACGT]` | R | `[AG]` | Y | `[CT]` |
| W | `[AT]` | S | `[GC]` | K | `[GT]` |
| M | `[AC]` | B | `[CGT]` | D | `[AGT]` |
| H | `[ACT]` | V | `[ACG]` | | |

B, D, H, V each exclude A, C, G, T respectively (the code preceding the one they drop is a mnemonic).

```python
IUPAC_DNA = {'N': '[ACGT]', 'R': '[AG]', 'Y': '[CT]', 'W': '[AT]', 'S': '[GC]',
             'K': '[GT]', 'M': '[AC]', 'B': '[CGT]', 'D': '[AGT]', 'H': '[ACT]', 'V': '[ACG]'}

def iupac_to_regex(pattern):
    return ''.join(IUPAC_DNA.get(base, base) for base in pattern)

# 'GATNNTC' -> 'GAT[ACGT][ACGT]TC'
```

`Bio.SeqUtils.nt_search` expands IUPAC ambiguity in the query motif automatically and reports overlapping hits, so it is the shortest correct path for a degenerate consensus.

## Overlapping Matches (the count trap)

**Goal:** Report every start position of a motif, including self-overlapping occurrences.

**Approach:** Use a zero-width lookahead so the regex engine never consumes the matched text; recover the match string from the inner capture group. For IUPAC motifs, prefer `nt_search`, which both expands ambiguity and reports overlaps.

**Reference (BioPython 1.83+):**
```python
import re
from Bio.SeqUtils import nt_search

target = 'AAGCGCGCGAA'

starts = [match.start(1) for match in re.finditer(r'(?=(GCGC))', target)]  # [2, 4]
hits = [(match.start(1), match.group(1)) for match in re.finditer(r'(?=([AG]CG[CT]))', target)]

result = nt_search(target, 'GCGC')  # ['GCGC', 2, 4]
pattern, positions = result[0], result[1:]
```

`nt_search` returns a heterogeneous list: `result[0]` is the (expanded) pattern string and `result[1:]` are the 0-based start positions. When there are no hits it returns just `[pattern]` (length 1), so test `len(result) > 1` before indexing rather than truthiness.

## Bio.motifs PWM / PSSM Pipeline

**Goal:** Build a probabilistic model from a set of aligned binding sites and score a target sequence for graded matches.

**Approach:** Create a motif from instances or a matrix file, set pseudocounts and background, read the recomputed PSSM, then scan. The count matrix `m.counts['A', 0]` is indexed `[base, position]`.

**Reference (BioPython 1.83+):**
```python
from Bio import motifs
from Bio.Seq import Seq

m = motifs.create([Seq('TACAA'), Seq('TACGA'), Seq('TACTA'), Seq('TGCAA')])  # alphabet defaults to ACGT

m.pseudocounts = 0.5        # set BEFORE reading m.pssm (see trap below)
m.background = None         # None gives uniform 0.25; or pass a dict of base frequencies

pwm = m.pwm                 # normalized frequencies (property)
pssm = m.pssm               # log2-odds vs background (property; RECOMPUTED on each access)

m.consensus                 # most frequent base per column
m.degenerate_consensus      # IUPAC-degenerate consensus
```

`m.counts.normalize(pseudocounts=0.5)` returns a position weight matrix and `pwm.log_odds()` returns a PSSM; these are equivalent to reading `m.pwm` / `m.pssm` after setting `m.pseudocounts`.

### The Pseudocount / -inf Trap (silent)

A column where some base has count 0 gives that base frequency 0 and a log-odds of negative infinity; any target carrying that base at that position then scores `-inf` and is unmatchable. This is common with short motifs or few instances. Setting `m.pseudocounts` (a flat 0.5, or sqrt(N) with N the number of instances; scalar or per-base dict) makes every cell finite by shrinking toward background.

Critically, `m.pssm` is recomputed from `m.pseudocounts` and `m.background` on every access. Set both BEFORE reading `m.pssm` (or `pwm.log_odds()`), or the matrix is silently wrong.

### Score, Threshold, and P-value

`pssm.calculate(seq)` returns the log2-odds score in bits for each window (a relative likelihood, not a probability). `pssm.search(seq, threshold=...)` yields `(position, score)` pairs at or above the threshold.

To convert a bit score into a false-positive rate, build the null distribution and ask it for a threshold:

```python
dist = pssm.distribution(background=m.background, precision=10**4)
threshold = dist.threshold_fpr(0.01)        # 1% false-positive rate
threshold = dist.threshold_fnr(0.1)         # 10% false-negative rate
threshold = dist.threshold_balanced(1000)   # rate_proportion = FNR:FPR ratio (FNR = FPR x rate_proportion), NOT a sequence length; default 1.0 gives FPR=FNR
```

Choosing a threshold "because it looks high" is the classic non-reproducible error. Higher `precision` gives finer threshold resolution at the cost of memory.

### Both Strands

`pssm.calculate` scans only the strand it is handed. `pssm.search` defaults to `both=True`, scanning both strands in one call; with `both=True` a hit at negative position `p` lies on the reverse strand and its forward-coordinate start is `len(seq) + p`. To handle strands separately, set `both=False` and scan the reverse-complemented PSSM explicitly:

```python
combined = list(pssm.search(seq, threshold=3.0))  # both strands; reverse hits have NEGATIVE positions

rc_pssm = pssm.reverse_complement()
forward = list(pssm.search(seq, threshold=3.0, both=False))
reverse = list(rc_pssm.search(seq, threshold=3.0, both=False))
```

## Reading Motif Matrix Files

`motifs.read(handle, fmt)` reads exactly one motif; `motifs.parse(handle, fmt)` returns an iterator over many. The format string must match the file layout exactly.

| `fmt` string | File type / source |
|--------------|--------------------|
| `jaspar` | multi-motif JASPAR PFM collection (use `parse`) |
| `pfm` | single JASPAR-style PFM (use `read`) |
| `pfm-four-columns` | CIS-BP, HOMER, HOCOMOCO (A C G T as columns) |
| `pfm-four-rows` | ScerTF, YeTFaSCo (A C G T as rows) |
| `sites` | JASPAR sites file (use `read`) |
| `meme` | MEME program output (use `parse`) |
| `minimal` | MEME minimal text format |
| `transfac` | TRANSFAC matrices |
| `mast`, `alignace`, `clusterbuster`, `xms` | respective tool outputs |

`'cisbp'`, `'homer'`, and `'hocomoco'` are NOT valid strings; those databases use `pfm-four-columns`. The four-columns versus four-rows distinction is the most common mix-up: a 4-column matrix read as `pfm-four-rows` parses without error but produces a meaningless transposed motif.

```python
from Bio import motifs

with open('collection.jaspar') as handle:
    for m in motifs.parse(handle, 'jaspar'):
        print(m.matrix_id, m.name, m.consensus)

m.format('jaspar')      # serialize back out
m.format('transfac')
```

## Common Motif Patterns

| Motif | Pattern | Description |
|-------|---------|-------------|
| Start codon | `ATG` | Translation initiation |
| Kozak | `[AG]CCATGG` | Eukaryotic translation initiation |
| TATA box | `TATA[AT]A[AT]` | Core promoter element |
| GC box (Sp1) | `GGGCGG` | Promoter element |
| CAAT box | `CCAAT` | Promoter element |
| Poly-A signal | `AATAAA` | mRNA polyadenylation |
| E-box (bHLH) | `CA[ACGT]{2}TG` | bHLH TF binding |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Count is too low | `str.count`/`re.findall` skip overlaps | `re.finditer(r'(?=(motif))', seq)` or `nt_search` |
| `IndexError` on `nt_search` result | No hits returns `[pattern]` (length 1) | Test `len(result) > 1` before reading `result[1:]` |
| Every target scores `-inf` | Count-0 cell gives -inf log-odds | Set `m.pseudocounts` (0.5 or sqrt(N)) before reading `m.pssm` |
| PSSM scores look wrong | Pseudocounts/background set after reading `m.pssm` | Set them first; `m.pssm` is recomputed on each access |
| Roughly half of sites missed | Only forward strand scanned | Score `pssm.reverse_complement()` or pass `both=True` |
| Threshold not reproducible | Cutoff chosen by eye | `pssm.distribution(...).threshold_fpr(fpr)` |
| `ValueError` parsing matrix | Wrong `fmt` (4-column vs 4-row, `jaspar` vs `pfm`) | Match `fmt` to the actual layout |
| No matches | Case or strand mismatch | `.upper()` both; check reverse complement |

## Related Skills

- seq-objects - Create Seq objects for searching
- reverse-complement - Reverse-complement the target to search the opposite strand
- transcription-translation - ORF and codon-context motifs in coding sequences
- sequence-properties - GC content and per-sequence properties around hits
- restriction-analysis/restriction-sites - Restriction enzyme recognition sites
- chip-seq/motif-analysis - De novo motif discovery and enrichment in peak sets
- database-access/entrez-fetch - Download motif matrices from JASPAR/NCBI
<!-- END FILE: sequence-manipulation/motif-search/SKILL.md -->

## 子目录：sequence-manipulation/reverse-complement

<!-- BEGIN FILE: sequence-manipulation/reverse-complement/SKILL.md -->
---
name: bio-reverse-complement
description: Generate reverse complements and complements of DNA/RNA sequences using Biopython, including IUPAC ambiguity codes, gapped alignments, and minus-strand features. Use when working with the opposite strand, building reverse primers, normalizing strand orientation before alignment, or extracting a coding sequence from a minus-strand feature.
tool_type: python
primary_tool: Bio.Seq
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Reverse Complement

Generate complementary and reverse complementary sequences using Biopython.

**"Get the reverse complement"** -> Produce the 5'-to-3' sequence of the opposite strand.
- Python: `seq.reverse_complement()` (BioPython `Seq`)
- CLI: `samtools faidx ref.fa region --reverse-complement` (extracts and RCs a region)

## The Governing Principle

Never hand-roll the complement table. Biopython's `reverse_complement()` already encodes the full IUPAC mapping correctly, case-insensitively, and on minus-strand features it is applied for the analyst automatically by `SeqFeature.extract()`. Every silent corruption in this domain comes from reimplementing what Biopython already does right: swapping ambiguity codes, forgetting that S/W/N are self-complementary, complementing the wrong molecule type, or reverse-complementing a second time after `extract()` already did it. Reach for the library method; reach for a guard (`molecule_type`) before it; never reach for a custom dictionary.

## Required Import

```python
from Bio.Seq import Seq
```

## Which Method for Which Question

| Question | Method | Output strand/direction |
|----------|--------|-------------------------|
| Opposite strand, conventional 5'->3' | `reverse_complement()` | 5'->3' of the complementary strand (the usual answer) |
| Base-paired sequence, same direction | `complement()` | 3'->5' of the complementary strand |
| Opposite strand of RNA, keep U | `reverse_complement_rna()` | 5'->3', emits U |
| Complement of RNA, keep U | `complement_rna()` | 3'->5', emits U |
| Coding strand from template (or vice versa) | `reverse_complement()` | the other strand, 5'->3' |
| mRNA sequence from the coding strand | `transcribe()` (NOT a complement) | same strand, T->U |

### reverse_complement()

Returns the reverse complement (5'->3' of the opposite strand). This is the most commonly used operation.

```python
seq = Seq('ATGCGATCG')
rc = seq.reverse_complement()  # Returns Seq('CGATCGCAT')
```

### complement()

Returns the complement without reversing. Less common - gives the opposite strand still written in 3'->5' order.

```python
seq = Seq('ATGCGATCG')
comp = seq.complement()  # Returns Seq('TACGCTAGC')
```

### reverse_complement_rna() and complement_rna()

For RNA, the dedicated methods emit U:

```python
rna = Seq('AUGCGAUCG')
rna.reverse_complement_rna()  # Returns Seq('CGAUCGCAU')
rna.complement_rna()          # Returns Seq('UACGCUAGC')
```

## Base Pairing and Ambiguity Codes

`reverse_complement()` complements all 15 IUPAC codes plus X correctly. The mapping is non-obvious for ambiguity codes - this is exactly why hand-rolling corrupts silently.

| Code | Bases | Complement | | Code | Bases | Complement |
|------|-------|------------|-|------|-------|------------|
| A | A | T | | M | A/C | K |
| T | T | A | | B | C/G/T | V |
| G | G | C | | V | A/C/G | B |
| C | C | G | | D | A/G/T | H |
| R | A/G | Y | | H | A/C/T | D |
| Y | C/T | R | | S | G/C | S (self) |
| K | G/T | M | | W | A/T | W (self) |
|   |       |   | | N | any | N (self) |

S, W, N, and X are SELF-complementary. The pairs that get swapped wrong by hand are B<->V and D<->H. The table is built for upper and lower case, so complementation is case-insensitive (`Seq('atRY').reverse_complement()` works).

## DNA vs RNA: the U handling rule

`reverse_complement()` runs in DNA mode: it treats any U as a T and EMITS T (docstring: "Any U in the sequence is treated as a T"). It does not raise and does not leave U.

```python
Seq('ACGU').reverse_complement()      # Returns Seq('ACGT')  -- U mapped to A, emitted as T
Seq('ACGU').reverse_complement_rna()  # Returns Seq('ACGU')  -- stays RNA
```

`transcribe()` does NOT complement. It swaps T->U on the SAME strand. Confusing "complement the template" with "transcribe the coding strand" is silent corruption. True biological transcription from the template strand is `template_dna.reverse_complement().transcribe()`.

## Gaps and Non-Table Characters

`complement` and `reverse_complement` do NOT validate the alphabet (unlike `translate()`). A gap `-` is not a table key, so it passes through unchanged and reversal preserves gap columns - the desired behavior for aligned sequences. Any other non-table character (`?`, `*`) also passes through silently.

```python
Seq('ATG-CGA--TY').reverse_complement()  # Returns Seq('RA--TCG-CAT') -- gaps preserved, Y->R
```

Because there is no alphabet check, garbage in produces garbage out without a warning (see the protein trap below).

## Code Patterns

### Visualize Double-Stranded DNA

```python
def show_dsdna(seq):
    print(f"5'-{seq}-3'")
    print(f"   {'|' * len(seq)}")
    print(f"3'-{seq.complement()}-5'")

show_dsdna(Seq('ATGCGATCG'))
```

### Check if a Sequence is Palindromic (Self-Complementary)

```python
def is_palindrome(seq):
    return seq == seq.reverse_complement()

is_palindrome(Seq('GAATTC'))  # True  -- EcoRI site
is_palindrome(Seq('ATGCGA'))  # False
```

### Reverse Complement a FASTA File

**Goal:** Produce a new FASTA file with all sequences reverse-complemented.

**Approach:** Parse records as a stream, build new SeqRecords from `.reverse_complement()`, write to output.

**Reference (BioPython 1.83+):**

```python
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

def reverse_complement_records(records):
    for record in records:
        yield SeqRecord(record.seq.reverse_complement(), id=record.id + '_rc', description=record.description + ' reverse complement')

records = SeqIO.parse('sequences.fasta', 'fasta')
SeqIO.write(reverse_complement_records(records), 'sequences_rc.fasta', 'fasta')
```

### Extract a Coding Sequence from a Minus-Strand Feature

**Goal:** Get the correct 5'->3' coding sequence for a gene annotated on the minus strand.

**Approach:** Call `feature.extract(parent.seq)`. For `strand == -1`, `extract()` ALREADY reverse-complements the slice and returns the coding sequence. Do NOT reverse-complement again.

**Reference (BioPython 1.83+):**

```python
from Bio.Seq import Seq
from Bio.SeqFeature import SeqFeature, SimpleLocation

parent = Seq('AAATGGGCCCTTTAAA')
feature = SeqFeature(SimpleLocation(3, 12, strand=-1), type='CDS')
cds = feature.extract(parent)  # Already reverse-complemented; this is the coding sequence
# cds.reverse_complement()     # WRONG -- double-RC bug, valid-looking but wrong strand
```

### Search Both Strands for a Motif

**Goal:** Find a motif on both strands and report forward-strand coordinates.

**Approach:** Search the forward sequence, then search its reverse complement, mapping minus-strand hits back to forward coordinates.

**Reference (BioPython 1.83+):**

```python
def search_both_strands(seq, motif):
    motif = Seq(motif)
    results = []
    pos = seq.find(motif)
    while pos != -1:
        results.append(('+', pos))
        pos = seq.find(motif, pos + 1)
    rc = seq.reverse_complement()
    pos = rc.find(motif)
    while pos != -1:
        results.append(('-', len(seq) - pos - len(motif)))
        pos = rc.find(motif, pos + 1)
    return results

search_both_strands(Seq('ATGCGAATTCGATGAATTCGATC'), 'GAATTC')
```

## In-Place Complementation

`inplace` defaults to `False` (standardized in 1.79). On an immutable `Seq`, `inplace=True` raises `TypeError: Sequence is immutable` (a loud, useful error). In-place mutation works only on `MutableSeq`.

```python
from Bio.Seq import MutableSeq
m = MutableSeq('ATGC')
m.reverse_complement(inplace=True)  # m is now MutableSeq('GCAT')
```

## The Protein Trap

Since the 1.78 alphabet removal there is no molecule-type checking. Reverse-complementing a protein produces SILENT GARBAGE with no warning: residues that are also nucleotide codes get complemented (`Seq('MAIVMGR').reverse_complement()` -> `Seq('YCKBITK')`; M->K, V->B), while protein-only letters E, F, I, L, P, Q, Z and `*` pass through unchanged. The old `IUPAC.protein` ValueError guard is gone. Guard on the molecule type, not the Seq:

```python
if record.annotations.get('molecule_type') not in ('DNA', 'RNA'):
    raise ValueError('reverse_complement is only valid for nucleotide sequences')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| U replaced by T in result | `reverse_complement()` runs in DNA mode (U treated as T) | Use `reverse_complement_rna()` to keep RNA |
| Result is meaningless letters, no error | Reverse-complemented a protein (silent since 1.78) | Guard on `molecule_type`, not the Seq |
| Coding sequence is the wrong strand | Called `.reverse_complement()` after `extract()` on a minus-strand feature | `extract()` already RC'd it; do not RC again |
| `TypeError: Sequence is immutable` | `inplace=True` on a `Seq` | Use a `MutableSeq`, or take the returned value |
| Ambiguity codes complement wrongly | Hand-rolled complement table (B/V, D/H swapped; S/W/N not self-complementary) | Use Biopython's `reverse_complement()`; never reinvent the table |
| Same strand returned instead of complement | Used `transcribe()` thinking it complements | `transcribe()` only swaps T->U; use `reverse_complement()` for the other strand |
| `TypeError` on a plain string | Passed a `str` instead of a `Seq` | Wrap input in `Seq()` first |

## References

Cornish-Bowden A (1985) "Nomenclature for incompletely specified bases in nucleic acid sequences: recommendations 1984." Nucleic Acids Res 13(9):3021-3030 (PMID 2582368). Defines the IUPAC ambiguity codes (R, Y, S, W, K, M, B, D, H, V, N) that Biopython's complement table implements.

## Related Skills

- seq-objects - Create and mutate Seq/MutableSeq objects to complement
- transcription-translation - transcribe() vs complement(); six-frame translation uses the reverse complement
- motif-search - Search both strands by reverse-complementing the query or sequence
- sequence-io/read-sequences - Parse FASTA/GenBank records before reverse-complementing
- primer-design/primer-basics - Reverse primers are the reverse complement of the target 3' end
- restriction-analysis/restriction-sites - Restriction sites are often palindromic (self-complementary)
- alignment-files/sam-bam-basics - BAM FLAG indicates read strand; samtools view -f 16 selects reverse reads
<!-- END FILE: sequence-manipulation/reverse-complement/SKILL.md -->

## 子目录：sequence-manipulation/seq-objects

<!-- BEGIN FILE: sequence-manipulation/seq-objects/SKILL.md -->
---
name: bio-seq-objects
description: Create and manipulate Seq, MutableSeq, and SeqRecord objects using Biopython. Use when creating sequences from strings, modifying sequence data in-place, building annotated records for file output, or debugging post-1.78 Bio.Alphabet and immutability errors.
tool_type: python
primary_tool: Bio.Seq
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Seq Objects

Create and manipulate biological sequence objects using Biopython.

**"Create a sequence object"** -> Wrap a raw string in a typed sequence container for biological operations.
- Immutable: `Seq('ATGC')` (BioPython) - string-like, supports complement/translate
- Mutable: `MutableSeq('ATGC')` (BioPython) - supports in-place edits
- Annotated: `SeqRecord(Seq(...), id=...)` (BioPython) - adds metadata for file I/O

## The governing principle: no alphabet, no validation

`Bio.Alphabet` was removed entirely in Biopython 1.78 (2020-09-04). `Seq` and `SeqRecord` lost their `.alphabet` attribute, and any old-style construction fails LOUD: `from Bio.Alphabet import IUPAC` raises ImportError, and `Seq('ACGT', IUPAC.unambiguous_dna)` raises TypeError. Molecule type now lives as a SeqRecord annotation, `record.annotations['molecule_type'] = 'DNA'`, consumed by the GenBank/EMBL writers.

The consequence governs everything downstream: no `Seq` operation validates its alphabet anymore. A protein passed to `reverse_complement()` or `transcribe()` returns silent garbage rather than an error. Sibling skills (transcription-translation, reverse-complement) inherit this - the burden is on the caller to track what kind of molecule a `Seq` holds.

## Required Imports

```python
from Bio.Seq import Seq, MutableSeq
from Bio.SeqRecord import SeqRecord
```

## Core Objects

### Seq - Immutable Sequence

Immutable and behaves like `str` since 1.78: indexing, slicing, `+`, `*`, `.upper()`, `in`, `.count()`, `.find()` all work. In-place edits raise: `seq[0] = 'A'` -> TypeError (LOUD). Use MutableSeq for edits.

```python
seq = Seq('ATGCGATCGATCG')

len(seq)           # length
seq[0]             # first base
seq[0:10]          # slice (returns Seq)
str(seq)           # text form (see bytes note below)
'ATG' in seq       # membership test
seq.count('G')     # count occurrences
seq.find('ATG')    # position (-1 if not found)
seq.upper()        # uppercase (returns Seq)
seq * 3            # repeat
```

Since 1.79 `Seq` is backed by `bytes` (and `MutableSeq` by `bytearray`), NOT a `str` subclass. Use `str(seq)` for text and `bytes(seq)` for bytes. `isinstance(seq, str)` is always False - code that type-checks with `isinstance(x, str)` to detect sequences silently skips every `Seq`; test `isinstance(x, (Seq, MutableSeq))` instead.

### MutableSeq - Mutable Sequence

A `bytearray`-backed sequence for in-place editing; required when an operation needs `inplace=True`.

```python
mut_seq = MutableSeq('ATGCGATCG')
mut_seq[0] = 'C'              # modify single position
mut_seq[0:3] = 'GGG'          # replace slice
mut_seq.append('A')           # add to end
mut_seq.insert(0, 'G')        # insert at position
mut_seq.pop()                 # remove and return last
mut_seq.remove('G')           # remove first occurrence
mut_seq.reverse()             # reverse in place
```

Convert between types (a `MutableSeq` is unhashable and cannot be a dict key or used in `SeqIO.write`, so cast back to `Seq` when done editing):

```python
seq = Seq(mut_seq)            # MutableSeq -> Seq
mut_seq = MutableSeq(seq)     # Seq -> MutableSeq
```

### Undefined and partially-defined sequences

`UndefinedSequenceError` (added 1.79, a subclass of `ValueError`) models a sequence whose length is known but whose content is not - produced by lazy/partial file parsers. A `Seq(None, length=20)` reports `len() == 20` but raises on any attempt to read the bytes.

```python
undef = Seq(None, length=20)
len(undef)            # 20 - fine
str(undef)            # raises UndefinedSequenceError (subclass of ValueError)

partial = Seq({3: 'ACGT'}, length=10)   # only positions 3-6 defined
str(partial[3:7])     # 'ACGT' - defined region reads fine
str(partial)          # raises - undefined positions
```

Note: `complement()`/`reverse_complement()` on an undefined `Seq` return self rather than crash, but any read of the bytes raises. Guard reads of records from lazy parsers with `try`/`except UndefinedSequenceError` only where content access is genuinely optional.

### SeqRecord - Annotated Sequence

Sequence plus metadata for file I/O and analysis.

```python
record = SeqRecord(Seq('ATGCGATCG'), id='gene1', name='example_gene', description='An example gene sequence')

record.seq                 # the Seq object
record.id                  # identifier string
record.name                # name string
record.description         # description string
record.features            # list of SeqFeature objects
record.annotations         # dict (organism, molecule_type, topology, ...)
record.letter_annotations  # per-letter annotations (e.g. phred_quality)
record.dbxrefs             # database cross-references
```

### SeqRecord transformations

**Goal:** Transform whole records (reverse-complement, translate, slice) while keeping metadata coherent.

**Approach:** Use SeqRecord methods that return new records with features remapped to the new coordinate frame; pass `id`/`description` explicitly because they are NOT carried automatically.

```python
rc_record = record.reverse_complement(id=f'{record.id}_rc', description='reverse complement')
protein_record = record.translate(id=f'{record.id}_protein', to_stop=True)
fasta_str = record.format('fasta')      # quick in-memory file-format string
```

Unlike `Seq.translate()`, `SeqRecord.translate()` defaults to `gap=None`, so any gap raises `TranslationError`; pass `gap='-'` to allow full gap codons such as `'---'`, while mixed gap/base codons still raise.

Slicing a SeqRecord remaps features but silently DROPS `annotations`, `dbxrefs`, and any feature that straddles a slice boundary - `subset = record[10:50]` returns a record with empty `annotations`. Re-attach `molecule_type` (and anything else a writer needs) on the slice before writing.

```python
subset = record[10:50]                          # features clipped; annotations dropped
subset.annotations['molecule_type'] = 'DNA'     # restore before GenBank/EMBL write
```

## Code Patterns

### Create Seq from String
```python
dna = Seq('ATGCGATCGATCG')
rna = Seq('AUGCGAUCGAUCG')
protein = Seq('MRCRS')
```

### Create SeqRecord with annotations for GenBank output
```python
record = SeqRecord(Seq('ATGCGATCG'), id='gene1', description='Example')
record.annotations['organism'] = 'Homo sapiens'
record.annotations['molecule_type'] = 'DNA'   # required by GenBank/EMBL writers
```

### Build SeqRecord with a feature
```python
from Bio.SeqFeature import SeqFeature, FeatureLocation

record = SeqRecord(Seq('ATGCGATCGATCG'), id='gene1')
feature = SeqFeature(FeatureLocation(0, 9), type='CDS', qualifiers={'product': ['Example protein']})
record.features.append(feature)
```

### Batch create SeqRecords
```python
sequences = ['ATGC', 'GCTA', 'TTAA']
records = [SeqRecord(Seq(s), id=f'seq_{i}') for i, s in enumerate(sequences)]
```

### Copy a SeqRecord
```python
from copy import deepcopy
new_record = deepcopy(record)   # deep copy; plain assignment shares features/annotations
new_record.id = 'modified_copy'
```

### Join sequences with a linker
```python
combined_seq = seq1 + Seq('NNNN') + seq2
combined_record = SeqRecord(combined_seq, id='combined')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ImportError: No module named 'Bio.Alphabet'` (or `cannot import name 'IUPAC'`) | `Bio.Alphabet` removed in 1.78 | Drop the alphabet argument; set `record.annotations['molecule_type']` instead |
| `TypeError: 'Seq' object does not support item assignment` | Editing an immutable `Seq` in place | Use `MutableSeq`, or rebuild with slicing/concatenation |
| `UndefinedSequenceError` on `str(seq)`/`print(seq)` | Sequence from a lazy/partial parser (`Seq(None, length=n)`) has known length but no content | Avoid reading bytes, or guard with `except UndefinedSequenceError` (subclass of `ValueError`) |
| `isinstance(seq, str)` is False, type-check skips the sequence | Since 1.79 `Seq` is `bytes`-backed, not a `str` subclass | Test `isinstance(x, (Seq, MutableSeq))`; use `str(seq)` for text |
| `ValueError: missing molecule_type` writing GenBank/EMBL | No `molecule_type` annotation (or it was dropped by slicing) | Set `record.annotations['molecule_type'] = 'DNA'` before writing |
| `reverse_complement()`/`transcribe()` returns nonsense, no error | No alphabet validation since 1.78 - a protein/RNA was passed | Track molecule type yourself; only call strand ops on DNA/RNA |

## Decision Tree

```
Need to work with sequence data?
├── Only string-like reads (slice, count, find, translate)?
│   └── Use Seq (immutable)
├── Editing individual positions in place?
│   └── Use MutableSeq, then cast back to Seq to write
├── Need metadata (id, description, features, annotations)?
│   └── Use SeqRecord
└── Writing to GenBank/EMBL?
    └── Use SeqRecord with annotations['molecule_type'] set
```

## Related Skills

- sequence-io/read-sequences - Parse files to get SeqRecord objects
- sequence-io/write-sequences - Write SeqRecord objects to files
- transcription-translation - Transform Seq objects (DNA to protein); inherits the no-alphabet-validation trap
- reverse-complement - Get reverse complement of Seq; silent garbage on non-DNA input
- sequence-slicing - Slice and extract from Seq/SeqRecord; 0-based vs 1-based coordinate trap
- database-access/entrez-fetch - Fetch sequences from NCBI as SeqRecords
<!-- END FILE: sequence-manipulation/seq-objects/SKILL.md -->

## 子目录：sequence-manipulation/sequence-properties

<!-- BEGIN FILE: sequence-manipulation/sequence-properties/SKILL.md -->
---
name: bio-sequence-properties
description: Calculate nucleotide and protein sequence properties (GC content, GC skew, molecular weight, melting temperature, isoelectric point, instability, hydropathy) with Biopython. Use when analyzing sequence composition, computing primer Tm, estimating DNA or protein mass, or profiling protein biophysical properties.
tool_type: python
primary_tool: Bio.SeqUtils
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Sequence Properties

Calculate physical and chemical properties of nucleotide and protein sequences using Biopython.

**"Calculate GC content"** -> Compute the fraction of G+C bases in a nucleotide sequence.
- Python: `gc_fraction(seq)` (Bio.SeqUtils) - returns a FRACTION 0-1, multiply by 100 for percent.

**"Compute a primer melting temperature"** -> Estimate Tm for hybridization or PCR.
- Python: `MeltingTemp.Tm_NN(seq)` (Bio.SeqUtils) - nearest-neighbor, the accurate method for primers.

**"Analyze protein properties"** -> Compute MW, pI, stability, hydrophobicity from an amino-acid sequence.
- Python: `ProteinAnalysis(str_seq)` (Bio.SeqUtils.ProtParam).

## The governing principle

Most of these functions return a plausible number for any input, so the danger is silent wrongness, not crashes. Three defaults bite hardest: `gc_fraction` returns a FRACTION (not the percent the legacy `GC()` returned), `molecular_weight` defaults to a SINGLE strand (~half a duplex), and `Tm_Wallace`/`Tm_GC` are composition-only methods that are wrong for real primers. Pick the function to match the question and verify its units, not just that it ran.

## Required Imports

```python
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction, molecular_weight, GC123, GC_skew, MeltingTemp, nt_search, seq1, seq3
from Bio.SeqUtils.ProtParam import ProteinAnalysis
```

## DNA/RNA Properties

### GC Content

`gc_fraction()` returns a fraction in [0, 1]. The legacy `GC()` returned a percent in [0, 100] and was REMOVED in BioPython 1.82 (`from Bio.SeqUtils import GC` now raises ImportError).

```python
from Bio.SeqUtils import gc_fraction

seq = Seq('ATGCGATCGATCGATCGATCG')
gc = gc_fraction(seq)        # 0.476... (FRACTION, not percent)
gc_percent = gc * 100        # 47.6 - multiply for percent
```

Factor-of-100 trap: porting `GC(seq)` to `gc_fraction(seq)` without `* 100` silently underreports 100x, so downstream filters like "GC > 40" reject everything.

Ambiguity-default trap: the new default `ambiguous='remove'` strips ambiguity codes before computing, but legacy `GC()` counted them in the length only, which equals the new `ambiguous='ignore'`. The faithful drop-in replacement is `gc_fraction(seq, ambiguous='ignore') * 100`. The modes only diverge on sequences that actually contain ambiguity codes (so clean test fixtures hide the difference, real data exposes it).

```python
gc_fraction(seq, ambiguous='remove')    # default: ambiguity codes stripped (neither numerator nor denominator)
gc_fraction(seq, ambiguous='ignore')    # counts ambiguous in denominator only - matches legacy GC()
gc_fraction(seq, ambiguous='weighted')  # each code contributes its mean GC probability (N/X = 0.5)
```

### GC at Codon Positions (GC123)

`GC123()` returns FOUR PERCENTAGES (0-100) - total GC plus GC at codon positions 1, 2, 3 (position 3 is the wobble base, most free to vary under codon bias). Note the unit inconsistency with `gc_fraction`: these are percentages, not fractions. `GC123` does not handle ambiguity codes.

```python
from Bio.SeqUtils import GC123

gc_total, gc_pos1, gc_pos2, gc_pos3 = GC123(Seq('ATGCGATCGATCGATCGATCG'))  # all 0-100
```

### GC Skew

`GC_skew(seq, window=100)` returns `(G-C)/(G+C)` for each non-overlapping window. A window with no G or C returns 0 (the zero-division is guarded), which can be misread as "no skew" rather than "no data".

```python
from Bio.SeqUtils import GC_skew

skew_values = GC_skew(seq, window=1000)  # list of per-window skew values
```

Biology: cumulative GC skew has a global MINIMUM at the replication origin (oriC) and a MAXIMUM at the terminus on circular bacterial chromosomes - the leading strand is G-enriched from strand-asymmetric mutation/repair. This is the basis of in-silico origin prediction. Compute the cumulative skew by taking the running sum of `GC_skew()`.

`xGC_skew()` is a GRAPHICS routine (its docstring literally says "GRAPHICS !!!") that draws on a Tkinter canvas. It raises a loud TclError/ImportError in headless environments. For headless cumulative-skew analysis, sum `GC_skew()` yourself instead.

### Molecular Weight

`molecular_weight(seq, seq_type='DNA', double_stranded=False, circular=False, monoisotopic=False)`.

```python
from Bio.SeqUtils import molecular_weight

dna = Seq('ATGCGATCG')
mw_ss = molecular_weight(dna)                          # single-stranded (DEFAULT)
mw_ds = molecular_weight(dna, double_stranded=True)    # full duplex mass
mw_circ = molecular_weight(dna, circular=True)         # no terminal phosphate adjustment
mw_rna = molecular_weight(Seq('AUGCGAUCG'), seq_type='RNA')
mw_prot = molecular_weight(Seq('MRCRS'), seq_type='protein')
mw_mono = molecular_weight(dna, monoisotopic=True)     # most-abundant isotope, for high-res MS
```

Double-stranded trap (~2x, silent): the default `double_stranded=False` returns a single-strand mass - roughly half a duplex. For genomic dsDNA pass `double_stranded=True`. It is NOT exactly half, because the complementary strand has a different base composition, so a non-self-complementary single-strand number cannot be "fixed later" by doubling. ng-to-molecule, copy-number, and molarity conversions all come out ~2x wrong.

Monoisotopic vs average: the default is average mass (bulk, spectrophotometric). Pass `monoisotopic=True` to match high-resolution mass spec (ESI/MALDI); the wrong choice is a silent systematic offset that grows with mass. Ambiguous letters raise ValueError (loud - good).

### Melting Temperature

**Goal:** Estimate the Tm of an oligo, choosing a method that matches its length and use.

**Approach:** Use `Tm_NN` for any PCR primer (nearest-neighbor, sequence-order aware). Reserve `Tm_Wallace` for very short probes and `Tm_GC` only when a composition-only estimate is acceptable.

```python
from Bio.SeqUtils import MeltingTemp as mt

primer = Seq('ACGGTCAGGTCAGGTACGGT')

tm = mt.Tm_NN(primer, strict=True)                       # accurate primer Tm
tm_salt = mt.Tm_NN(primer, Na=50, dnac1=250, dnac2=250)  # 50 mM Na+, 250 nM each strand
tm_mg = mt.Tm_NN(primer, Mg=1.5, dNTPs=0.2, saltcorr=7)  # Mg/dNTPs ONLY honored at saltcorr 6 or 7
```

| Method | Model | Use when | Caveat |
|--------|-------|----------|--------|
| `Tm_Wallace` | 4(G+C) + 2(A+T) "2+4 rule" | Oligos <=14 nt only | Ignores order/salt; WRONG for primers (off 5-10 C+) |
| `Tm_GC` | GC-content empirical equation | Longer sequences, rough estimate | Composition-only, no nearest-neighbor info |
| `Tm_NN` | Nearest-neighbor thermodynamics | PCR primers, probes, accurate work | Needs realistic salt/strand conc for absolute values |

`Tm_NN` defaults: `nn_table=None` which selects `DNA_NN3` (Allawi & SantaLucia 1997), `saltcorr=5`, strand concentrations `dnac1=dnac2=25` nM. `saltcorr` ranges 1-7, but only 6 (Owczarzy 2004) and 7 (Owczarzy 2008) actually use Mg2+/dNTPs - setting `Mg`/`dNTPs` with `saltcorr<=5` silently ignores them. Keep `strict=True` for primer work: it raises on ambiguous or unsupported nearest-neighbor pairs, whereas `strict=False` silently skips them and underestimates Tm.

### IUPAC-Aware Search (nt_search)

```python
from Bio.SeqUtils import nt_search

result = nt_search('ATGCGATCGATCGATNGATC', 'GATNGATC')  # ['GAT[GATC]GATC', 4] - result[0] is the EXPANDED regex, result[1:] are 0-based starts
```

## Protein Properties

**Goal:** Compute biophysical properties of a protein from its amino-acid sequence.

**Approach:** Create one `ProteinAnalysis` object and call its methods. Non-standard residues (B, Z, X, U, `*`, `-`) are absent from the parameter tables and raise KeyError, so sanitize first.

```python
from Bio.SeqUtils.ProtParam import ProteinAnalysis

clean = 'MAEGEITTFTALTEKFNLPPGNYKKPKLLYCSNG'.replace('*', '').replace('X', '')
protein = ProteinAnalysis(clean)

mw = protein.molecular_weight()              # protein average MW (Daltons)
pi = protein.isoelectric_point()             # pI from linear-sequence pKa tables
charge = protein.charge_at_pH(7.0)           # net charge at a given pH
ii = protein.instability_index()             # Guruprasad: > 40 => predicted unstable
gravy = protein.gravy()                       # mean Kyte-Doolittle hydropathy (neg = hydrophilic)
arom = protein.aromaticity()                 # relative frequency of F + W + Y
helix, turn, sheet = protein.secondary_structure_fraction()
eps_reduced, eps_oxidized = protein.molar_extinction_coefficient()  # 280 nm, (reduced, cystine)
flex = protein.flexibility()                 # per-residue, fixed window of 9
```

Interpretation caveats:
- `isoelectric_point()` and `charge_at_pH()` use fixed pKa tables on the LINEAR sequence - they ignore 3D environment and post-translational modifications, so a measured pI can differ by a full pH unit or more.
- `gravy(scale='KyteDoolitle')` - the default scale literal is MISSPELLED `'KyteDoolitle'` (one 't'). Passing the correctly-spelled `'KyteDoolittle'` raises KeyError. A single whole-protein average also collapses local topology (a TM helix plus hydrophilic loops can average near 0); use a windowed hydropathy profile for membrane topology.
- `secondary_structure_fraction()` is a composition propensity estimate, not a structure prediction.
- `instability_index()` uses Guruprasad's dipeptide method; > 40 predicts an unstable protein.

### Amino-Acid Code Conversion

```python
from Bio.SeqUtils import seq1, seq3

seq1('MetAlaGlyTrp')           # 'MAGW'  (3-letter -> 1-letter)
seq3('MAGW')                   # 'MetAlaGlyTrp'  (1-letter -> 3-letter, no separator)
```

## Code Patterns

### Per-Record GC Across a FASTA

**Goal:** Report length and GC percent for every record in a file.

**Approach:** Stream records with `SeqIO.parse`, compute GC per record, multiply the fraction by 100.

```python
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction

def analyze_fasta(filename):
    return [{'id': r.id, 'length': len(r.seq), 'gc': gc_fraction(r.seq) * 100} for r in SeqIO.parse(filename, 'fasta')]
```

### Cumulative GC Skew (Headless)

**Goal:** Locate a candidate replication origin without the Tkinter graphics routine.

**Approach:** Take per-window skew from `GC_skew`, accumulate it, and read off the minimum (oriC) and maximum (terminus).

```python
from Bio.SeqUtils import GC_skew

def cumulative_skew(seq, window=10000):
    skew = GC_skew(seq, window=window)
    positions, cumulative, total = [], [], 0
    for i, s in enumerate(skew):
        total += s
        positions.append(i * window)
        cumulative.append(total)
    ori = positions[cumulative.index(min(cumulative))]
    return positions, cumulative, ori
```

### Full Protein Report

**Goal:** Summarize the key biophysical metrics of a protein in one pass.

**Approach:** Sanitize non-standard residues, build one `ProteinAnalysis` object, and collect each metric into a dict.

```python
from Bio.SeqUtils.ProtParam import ProteinAnalysis

def protein_report(sequence):
    clean = str(sequence).upper().replace('*', '').replace('X', '')
    protein = ProteinAnalysis(clean)
    helix, turn, sheet = protein.secondary_structure_fraction()
    return {
        'length': len(clean),
        'molecular_weight': protein.molecular_weight(),
        'isoelectric_point': protein.isoelectric_point(),
        'charge_at_pH7': protein.charge_at_pH(7.0),
        'instability_index': protein.instability_index(),
        'gravy': protein.gravy(),
        'aromaticity': protein.aromaticity(),
        'helix_fraction': helix, 'turn_fraction': turn, 'sheet_fraction': sheet,
    }
```

### CpG Observed/Expected Ratio

```python
def cpg_ratio(seq):
    s = str(seq).upper()
    expected = (s.count('C') * s.count('G')) / len(s) if s else 0
    return s.count('CG') / expected if expected > 0 else 0
```

## Property Reference

| Property | Function | Units / Notes |
|----------|----------|---------------|
| GC content | `gc_fraction()` | FRACTION 0-1 (multiply by 100 for percent) |
| GC by codon position | `GC123()` | FOUR PERCENTAGES 0-100 (total + pos 1/2/3) |
| GC skew | `GC_skew()` | (G-C)/(G+C) per window; 0 = no G/C in window |
| Molecular weight | `molecular_weight()` | Daltons; single-strand by DEFAULT |
| Melting temp | `MeltingTemp.Tm_NN()` | Celsius; accurate for primers |
| pI / charge | `isoelectric_point()` / `charge_at_pH()` | Linear pKa only, ignores 3D/PTMs |
| Instability | `instability_index()` | > 40 => predicted unstable |
| Hydropathy | `gravy()` | neg = hydrophilic; default scale misspelled `'KyteDoolitle'` |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| GC values look 100x too small; filters reject all | Used `gc_fraction()` (fraction) where percent expected | Multiply by 100 |
| GC differs from legacy `GC()` on real data | Default `ambiguous='remove'` vs legacy `'ignore'` | Use `gc_fraction(seq, ambiguous='ignore') * 100` for a faithful drop-in |
| `GC_skew` returns 0 across a region | Window had no G or C (guarded division), not true zero skew | Treat 0 as "no data"; widen the window |
| `xGC_skew` raises TclError/ImportError | It is a Tkinter graphics routine, fails headless | Sum `GC_skew()` yourself for cumulative skew |
| Primer Tm off by 5-10 C | Used `Tm_Wallace`/`Tm_GC` (composition-only) | Use `Tm_NN` with realistic salt and strand concentration |
| Mg/dNTPs change nothing in `Tm_NN` | `Mg`/`dNTPs` ignored unless `saltcorr` is 6 or 7 | Set `saltcorr=7` (Owczarzy 2008) for divalent correction |
| MW ~half of expected for genomic dsDNA | `molecular_weight` default `double_stranded=False` | Pass `double_stranded=True` |
| `KeyError` from `ProteinAnalysis` | Non-standard residue (B, Z, X, U, `*`, `-`) | Strip or replace before analysis |
| `KeyError` from `gravy('KyteDoolittle')` | Default scale literal is misspelled `'KyteDoolitle'` (one 't') | Omit the argument or pass `'KyteDoolitle'` |

## References

Lobry JR (1996) Asymmetric substitution patterns in the two DNA strands of bacteria. Mol Biol Evol 13(5):660-665.

Lobry JR, Gautier C (1994) Hydrophobicity, expressivity and aromaticity are the major trends of amino-acid usage in 999 Escherichia coli chromosome-encoded genes. Nucleic Acids Res 22(15):3174-3180.

SantaLucia J Jr (1998) A unified view of polymer, dumbbell, and oligonucleotide DNA nearest-neighbor thermodynamics. PNAS 95(4):1460-1465.

Kyte J, Doolittle RF (1982) A simple method for displaying the hydropathic character of a protein. J Mol Biol 157(1):105-132.

Guruprasad K, Reddy BVB, Pandit MW (1990) Correlation between stability of a protein and its dipeptide composition: a novel approach for predicting in vivo stability of a protein from its primary sequence. Protein Eng 4(2):155-161.

## Related Skills

- seq-objects - Create and modify Seq objects before property calculation
- codon-usage - GC123 and codon-bias indices for coding-sequence analysis
- transcription-translation - Translate a CDS before protein property analysis
- sequence-io/sequence-statistics - File-level statistics (N50, totals, dataset GC)
- primer-design/primer-basics - Design primers where Tm_NN and GC content drive the choices
- restriction-analysis/restriction-sites - Locate enzyme recognition sites in the same sequence
<!-- END FILE: sequence-manipulation/sequence-properties/SKILL.md -->

## 子目录：sequence-manipulation/sequence-slicing

<!-- BEGIN FILE: sequence-manipulation/sequence-slicing/SKILL.md -->
---
name: bio-sequence-slicing
description: Slice, extract, and concatenate biological sequences and annotated records using Biopython. Use when extracting subsequences by position, splicing exons into a transcript, joining sequences, or carrying a sub-region of an annotated record (with quality scores and features) into a new record.
tool_type: python
primary_tool: Bio.Seq
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Sequence Slicing

Extract sub-regions, splice non-contiguous regions, and concatenate sequences and annotated records.

**"Extract a subsequence"** -> Slice a Seq with 0-based half-open coordinates.
- Python: `seq[start:end]` (Bio.Seq)

**"Pull out a sub-region but keep its quality scores and features"** -> Slice the SeqRecord, not the bare Seq.
- Python: `record[start:end]` (Bio.SeqRecord)

**"Splice exons into a transcript"** -> Extract each region and concatenate.
- Python: `sum((seq[s:e] for s, e in coords), Seq(''))` or the `+` operator

## The Governing Principle

Slicing a bare `Seq` is pure string math: `seq[start:end]` returns a new `Seq`, half-open, with no metadata to lose. Slicing a `SeqRecord` carries metadata, and the rule for WHAT survives is the single most error-prone part of this skill:

`record[start:end]` (verified against `Bio/SeqRecord.__getitem__`):
- PRESERVES `id`, `name`, `description`, and `molecule_type`.
- AUTO-SLICES `letter_annotations` (per-letter data such as PHRED `phred_quality`) to match the new coordinates -- this is why a FASTQ slice keeps the right per-base qualities for free.
- KEEPS only features FULLY CONTAINED in `[start:end]`; their locations are recalculated relative to the new start.
- SILENTLY DROPS the `annotations` dict (organism, taxonomy, references, comments), the `dbxrefs` list, and any feature that STRADDLES the slice boundary (dropped whole, never truncated). A non-trivial stride (`record[::2]`) drops features entirely.

Nothing warns when annotations vanish. The GenBank `source` feature spans the whole record, so it straddles almost any slice and disappears along with organism/taxonomy. To carry that metadata across, copy it explicitly:

```python
sub = record[start:end]
sub.annotations = record.annotations.copy()
```

and re-add any boundary-straddling feature manually (with a clamped, recalculated location) if a truncated copy is needed.

## Required Imports

```python
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
```

## Coordinate Systems: the 0-based vs 1-based trap

Python and Biopython slicing is 0-based and half-open: `seq[start:end]` includes `start`, excludes `end`, and returns `end - start` letters. File formats disagree, and mixing them is a SILENT off-by-one (no error, just the wrong bases):

| Source | Convention | Position 1234..5678 means |
|--------|------------|---------------------------|
| Python / Bio.Seq slice | 0-based, half-open | `seq[1234:5678]` |
| GenBank / EMBL / GFF / VCF feature line | 1-based, INCLUSIVE | `seq[1233:5678]` (subtract 1 from start only) |
| BED file | 0-based, half-open | `seq[1234:5678]` (already matches Python) |

The asymmetry is the catch: convert a 1-based inclusive interval by subtracting 1 from the START only; the end already lands correctly because Python's exclusive end cancels the inclusive end. Reading a coordinate straight off a GFF and slicing `seq[start:end]` without the `-1` silently shifts everything one base left.

`Bio.SeqFeature` locations sidestep this entirely: they store a 0-based start and a Python-style end, so `int(feature.location.start):int(feature.location.end)` slices the parent directly, and `feature.extract(record.seq)` does the same automatically (handling strand and compound/joined locations).

```python
def extract_1based(seq, start, end):
    '''Extract a 1-based inclusive interval (GenBank/GFF style).'''
    return seq[start - 1:end]
```

## Slicing a Bare Seq

Slicing returns a `Seq` (not a string); negative indices and strides behave exactly like `str` (Seq has behaved like `str` since BioPython 1.78).

```python
seq = Seq('ATGCGATCGATCG')
seq[0]       # 'A'  single base, 0-indexed -> returns a str
seq[-1]      # 'G'  last base
seq[0:3]     # Seq('ATG')   first 3 bases
seq[-5:]     # Seq('GATCG')  last 5
seq[::2]     # Seq('AGGTGTG')  every 2nd base (stride)
seq[::-1]    # Seq('GCTAGCTAGCGTA')  reversed (not the reverse complement)
```

`str(record.seq)` returns the raw string, but raises `UndefinedSequenceError` when the record's sequence content is undefined (e.g. `Seq(None, length=n)` from a header-only FASTA or a pysam-backed record). Guard with `len()` (always defined) before forcing the content to a string.

## Code Patterns

### Splice Non-Contiguous Regions (Exons -> Transcript)

**Goal:** Join several separated regions of a genomic sequence into one continuous sequence.

**Approach:** Extract each region with half-open coordinates and concatenate. `sum()` needs an explicit `Seq('')` start value because the default `0` cannot be added to a `Seq`.

```python
def extract_regions(seq, regions):
    '''Concatenate multiple [start, end) regions in order.'''
    return sum((seq[start:end] for start, end in regions), Seq(''))

exon_coords = [(0, 50), (100, 150), (200, 250)]
mrna = extract_regions(genomic_seq, exon_coords)
```

For a real annotated transcript, let the feature do the work -- `feature.extract` honors strand and joined exon locations:

```python
for feature in record.features:
    if feature.type == 'mRNA':
        transcript = feature.extract(record.seq)
```

### Carry a Sub-Region into a New Annotated Record

**Goal:** Keep id, per-base quality, and contained features when extracting a window, and decide deliberately what metadata to carry.

**Approach:** Slice the `SeqRecord` (qualities and contained features ride along automatically), then explicitly copy the `annotations` dict, which slicing always drops.

```python
sub = record[100:400]                      # qualities + contained features auto-sliced
sub.annotations = record.annotations.copy()  # organism/taxonomy/refs would be lost otherwise
sub.id = f'{record.id}:101-400'            # 1-based label for humans
```

To build a fresh record from a bare Seq slice instead (no source metadata to carry):

```python
sub = SeqRecord(record.seq[100:400], id=f'{record.id}_sub', description='positions 101-400')
```

### Extract a Feature by Type

```python
for record in SeqIO.parse('sequence.gb', 'genbank'):
    for feature in record.features:
        if feature.type == 'CDS':
            cds = feature.extract(record.seq)      # strand-aware
            gene = feature.qualifiers.get('gene', ['?'])[0]
```

### Concatenate Sequences and Records

```python
seq1 + seq2                      # Seq + Seq -> Seq
seq1 + 'NNNN'                    # Seq + str -> Seq
Seq('NNN').join([s1, s2, s3])   # linker between each -> Seq
```

Adding `SeqRecord` objects works (`rec1 + rec2` concatenates sequences and per-letter annotations), but follows the same rule as slicing: the result keeps `id`/`name`/`description` only when both share them, and the `annotations` dict is reset. Set metadata on the result explicitly.

### Split into Codons or Fixed Chunks

```python
def split_codons(seq):
    '''Whole codons only; trailing 1-2 nt remainder is dropped.'''
    return [seq[i:i + 3] for i in range(0, len(seq) - len(seq) % 3, 3)]

def chunk_sequence(seq, size):
    '''Fixed-size chunks; final chunk may be shorter.'''
    return [seq[i:i + size] for i in range(0, len(seq), size)]
```

### Tile Overlapping Windows

```python
def sliding_windows(seq, window_size, step=1):
    for i in range(0, len(seq) - window_size + 1, step):
        yield i, seq[i:i + window_size]
```

### Flanking Region Around a Position

```python
def get_flanking(seq, position, flank):
    '''Clamp to sequence ends so the slice never runs past the edges.'''
    start = max(0, position - flank)
    end = min(len(seq), position + flank + 1)
    return seq[start:end]
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Organism/taxonomy/references gone from a sub-record | `record[start:end]` silently drops the `annotations` dict and `dbxrefs` | `sub.annotations = record.annotations.copy()` after slicing |
| A feature spanning the cut is missing from the slice | Features straddling the boundary are dropped whole, not truncated | Re-add manually with a clamped, recalculated location |
| All features gone after `record[::2]` | A non-trivial stride drops features entirely | Slice without a stride, or rebuild features by hand |
| Everything shifted one base left | GFF/GenBank 1-based start sliced as if 0-based | Subtract 1 from the START only: `seq[start-1:end]` |
| `UndefinedSequenceError` on `str(record.seq)` | Sequence content undefined (`Seq(None, length=n)`) | Use `len(record)`; do not force undefined content to a string |
| `TypeError` from `sum(slices)` | Default start `0` cannot add to a `Seq` | Pass a start: `sum(slices, Seq(''))` |
| Reversed but wrong strand | `seq[::-1]` reverses only; it does not complement | Use `seq.reverse_complement()` (see reverse-complement) |
| `IndexError` on single-base index | Position past the end | Check `len(seq)` first; slices clamp but `seq[i]` does not |

## Decision Guide

- Bare sequence, no metadata to keep -> slice the `Seq`: `seq[start:end]`.
- Need per-base quality or contained features to ride along -> slice the `SeqRecord`: `record[start:end]`, then copy `annotations`.
- Coordinates came from a GFF/GenBank/EMBL/VCF line -> subtract 1 from the start before slicing.
- Coordinates came from a BED file -> use as-is (already 0-based half-open).
- Strand-aware or joined/compound location -> `feature.extract(record.seq)`, never a manual slice.
- Joining separated regions -> `sum((seq[s:e] for s, e in coords), Seq(''))`.

## Related Skills

- seq-objects - Create Seq/SeqRecord objects and handle undefined sequence content
- reverse-complement - Reverse-complement an extracted region (slicing reverses but does not complement)
- transcription-translation - Translate an extracted CDS or spliced transcript
- sequence-io/read-sequences - Parse GenBank/FASTQ records (with features and qualities) to slice
- genome-intervals/gtf-gff-handling - Read 1-based GFF/GTF feature coordinates before slicing
- alignment-files/sam-bam-basics - Extract sequences from BAM regions with samtools
<!-- END FILE: sequence-manipulation/sequence-slicing/SKILL.md -->

## 子目录：sequence-manipulation/transcription-translation

<!-- BEGIN FILE: sequence-manipulation/transcription-translation/SKILL.md -->
---
name: bio-transcription-translation
description: Transcribe DNA to RNA and translate to protein using Biopython, with NCBI codon-table selection, CDS validation, and six-frame ORF finding. Use when converting a CDS or ORF to its amino-acid sequence, selecting a non-standard (mitochondrial, bacterial, ciliate) genetic code, validating a coding sequence, or scanning all reading frames.
tool_type: python
primary_tool: Bio.Seq
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Transcription and Translation

**"Translate my DNA sequence to protein"** -> Transcribe DNA to RNA and translate to protein, choosing the right genetic code and validating the reading frame.
- Python: `Seq.translate()`, `Seq.transcribe()`, `Bio.Data.CodonTable` (BioPython)

## The Governing Principle

The single most dangerous bug in translation is **silent**: a valid-but-wrong `table=` argument produces a plausible wrong protein with no error. Translating human mitochondrial DNA with the default Standard code (table 1) inserts `*` where UGA actually codes Trp and truncates at AGA/AGG (which are stops in vertebrate mito). The protein looks real and nothing complains. By contrast, an *unknown* table id or name raises `KeyError` (loud). Only valid-but-wrong tables corrupt silently.

The defense: when the input is a complete coding sequence, pass `cds=True`. It converts silent traps into loud `TranslationError` exceptions by validating start, length, and stop. Use it for ORF validation rather than trusting a clean-looking output.

Since the Biopython 1.78 alphabet removal, `transcribe()`, `back_transcribe()`, and `translate()` perform NO type checking. Transcribing a protein or translating the wrong strand returns silent garbage. Confirm the molecule and strand before converting.

## Required Import

```python
from Bio.Seq import Seq
from Bio.Data import CodonTable
```

## Transcription Is a String Operation, Not Biology

`transcribe()` is a pure T->U replacement on the coding (sense) strand; `back_transcribe()` is U->T. Neither performs splicing, intron removal, 5' capping, or poly-A addition. The Biopython tutorial states plainly that all transcribe does is replace T with U.

```python
coding_dna = Seq('ATGCGATCGATCG')
rna = coding_dna.transcribe()        # Seq('AUGCGAUCGAUCG'), T->U only
back = rna.back_transcribe()         # Seq('ATGCGATCGATCG'), U->T only
```

True biological transcription starts from the template strand, so reverse-complement first:

```python
template = Seq('CGATCGATCGCAT')
mrna = template.reverse_complement().transcribe()
```

Translation accepts DNA or RNA directly, so explicit transcription is rarely needed before `translate()`.

## Translation Basics

```python
coding_dna = Seq('ATGTTTGGT')
coding_dna.translate()               # Seq('MFG'), from DNA
Seq('AUGUUUGGU').translate()         # Seq('MFG'), from RNA
```

### Stop-Codon Behavior

`translate()` substitutes `stop_symbol` (default `'*'`) for EVERY in-frame stop, so internal stops appear as `*` mid-protein. `to_stop=True` instead halts at the first in-frame stop and does NOT append the symbol.

```python
seq = Seq('ATGTTTGGTTAAGGG')
seq.translate()                      # Seq('MFG*G'), stop shown, translation continues
seq.translate(to_stop=True)          # Seq('MFG'), halts at first stop
```

## NCBI Codon Tables: Which Code, and the Consequence of the Wrong One

Biopython exposes every NCBI genetic code by integer id or registered name. Selecting the wrong one is the #1 silent bug (see governing principle).

| ID | Name | Key reassignments vs Standard | When it matters |
|----|------|-------------------------------|-----------------|
| 1 | Standard | none (baseline) | Most nuclear genes |
| 2 | Vertebrate Mitochondrial | AGA/AGG -> STOP; AUA -> Met; UGA -> Trp | Human/vertebrate mtDNA (4 stops: UAA, UAG, AGA, AGG) |
| 3 | Yeast Mitochondrial | CUN (all four CU*) -> Thr; AUA -> Met; UGA -> Trp | **CTG -> Thr lives HERE, not table 12** |
| 4 | Mold/Protozoan Mito + Mycoplasma/Spiroplasma | UGA -> Trp (only change) | Fungal/protozoan mito; Mycoplasma |
| 5 | Invertebrate Mitochondrial | AGA/AGG -> Ser; AUA -> Met; UGA -> Trp | Insect/worm mito (AGA/AGG=Ser, not STOP as in table 2) |
| 6 | Ciliate Nuclear | UAA/UAG -> Gln; only UGA stays stop | Tetrahymena, Paramecium (single stop) |
| 11 | Bacterial/Archaeal/Plastid | same coding as Standard; expanded starts | Prokaryotes, plastids (differs from 1 mainly in initiation) |
| 12 | Alternative Yeast Nuclear | CUG -> Ser (from Leu) | *Candida* CUG-Ser clade |

**Explicit correction:** CTG -> Thr is table **3** (Yeast Mitochondrial). Table **12** is CUG -> **Ser**. Do not conflate them.

```python
seq = Seq('ATGGCCTGA')
seq.translate(table=2)                            # by NCBI integer id
seq.translate(table='Vertebrate Mitochondrial')   # by registered name

CodonTable.unambiguous_dna_by_id[2]
CodonTable.unambiguous_dna_by_name['Vertebrate Mitochondrial']
```

## Validating a Coding Sequence with cds=True

**Goal:** Translate a complete ORF and have any structural defect raise a loud error instead of producing a silent wrong protein.

**Approach:** Pass `cds=True`. It enforces four conditions, each raising `Bio.Data.CodonTable.TranslationError` on failure: (1) first codon is a start codon for the chosen table; (2) length is a multiple of 3; (3) sequence ends in a stop; (4) no internal in-frame stop. A valid alternative start (GTG/TTG/ATT) is translated as M, biologically correct for fMet initiation. The terminal stop is stripped from the output.

**Reference (BioPython 1.83+):**

```python
cds = Seq('ATGTTTGGTTAA')
cds.translate(cds=True)              # Seq('MFG'), validated, terminal stop removed

alt_start = Seq('GTGTTTGGTTAA')
alt_start.translate(table=11, cds=True)   # Seq('MFG'), GTG start -> M under bacterial code
```

Start-codon lists differ by table: table 1 = TTG/CTG/ATG; table 2 = ATT/ATC/ATA/ATG/GTG; table 11 = TTG/CTG/ATT/ATC/ATA/ATG/GTG. A start valid under one table fails under another, which is exactly the loud signal `cds=True` provides.

## translate() Parameters and Edge Cases

Signature (the `Seq.translate` METHOD): `translate(table='Standard', stop_symbol='*', to_stop=False, cds=False, gap='-')`. The `Seq` method defaults to `gap='-'`, while both the module-level `Bio.Seq.translate(sequence, ...)` function and `SeqRecord.translate()` default to `gap=None`.

- **Partial codon** (length not a multiple of 3): emits a `BiopythonWarning` and SILENTLY drops the trailing 1-2 bases. Easy to miss in a pipeline. Under `cds=True` the same condition becomes a loud `TranslationError`.
- **Gaps:** because the `Seq` method defaults to `gap='-'`, a full gap codon `'---'` already translates to `'-'` (e.g. `Seq('GTG---GCCATT').translate()` -> `'V-AI'`, no error). A codon mixing gaps and bases (`'TT-'`) raises `TranslationError`. `SeqRecord.translate()` instead defaults to `gap=None`, so even a full `'---'` codon raises unless `gap='-'` is passed; mixed gap/base codons still raise. For alignment-derived CDS, preserve codon and alignment semantics with `alignment/multiple-alignment` or the project's established translation wrapper rather than assuming one gap-normalization policy.
- **Dual-coding stop tables (27 Karyorelict, 28 Condylostoma, 31 Blastocrithidia Nuclear):** these reassign a stop codon so it codes both an amino acid and stop, so `to_stop=True` raises a `ValueError` (no single truncation point).

```python
Seq('ATGTTTGG').translate()          # BiopythonWarning, trailing 'GG' dropped -> Seq('MF')
Seq('ATGTTTGG').translate(cds=True)  # TranslationError: length not a multiple of three
```

## Selenocysteine and Pyrrolysine Are Silently Lost

Selenocysteine (Sec, one-letter U) is encoded by UGA and pyrrolysine (Pyl, one-letter O) by UAG, both normally stop codons. Recoding requires a SECIS (Sec) or PYLIS (Pyl) element that Biopython does NOT detect. No NCBI table maps UGA->U or UAG->O. Naive translation therefore yields `*` mid-protein, and `to_stop=True` SILENTLY truncates the protein at that position. Real selenoproteins (GPX, TXNRD, SELENOP) come out truncated or peppered with `*`. There is no clean Biopython workaround; flag these genes and handle the recoding event manually.

## Six-Frame Translation

**Goal:** Translate a DNA sequence in all six frames (three forward, three reverse) to expose every possible protein product.

**Approach:** For each strand, offset by 0, 1, 2 bases, trim to a multiple of 3, and translate.

**Reference (BioPython 1.83+):**

```python
def six_frame_translation(seq):
    frames = []
    for strand, s in [('+', seq), ('-', seq.reverse_complement())]:
        for frame in range(3):
            length = 3 * ((len(s) - frame) // 3)
            fragment = s[frame:frame + length]
            frames.append((strand, frame, fragment.translate()))
    return frames

seq = Seq('ATGCGATCGATCGATCGATCG')
for strand, frame, protein in six_frame_translation(seq):
    print(f'{strand}{frame}: {protein}')
```

## Find All ORFs (Start to Stop)

**Goal:** Identify all open reading frames (Met to stop) across both strands and all three frames, keeping only those above a minimum length.

**Approach:** Translate each of the six frames, then scan each translation for Met-to-stop segments meeting the threshold.

**Reference (BioPython 1.83+):**

```python
def find_orfs(seq, min_protein_length=30):
    orfs = []
    for strand, s in [('+', seq), ('-', seq.reverse_complement())]:
        for frame in range(3):
            end = frame + 3 * ((len(s) - frame) // 3)
            trans = str(s[frame:end].translate())
            aa_start = 0
            while True:
                start = trans.find('M', aa_start)
                if start == -1:
                    break
                stop = trans.find('*', start)
                if stop == -1:
                    stop = len(trans)
                orf = trans[start:stop]
                if len(orf) >= min_protein_length:
                    orfs.append((strand, frame, start * 3 + frame, orf))
                aa_start = start + 1
    return orfs

seq = Seq('ATGCGATCGATCGATCGATCGTAA')
for strand, frame, pos, orf in find_orfs(seq, min_protein_length=3):
    print(f'{strand} frame {frame} pos {pos}: {orf}')
```

## Inspect a Codon Table

```python
table = CodonTable.unambiguous_dna_by_id[2]
table.start_codons                   # ['ATT', 'ATC', 'ATA', 'ATG', 'GTG']
table.stop_codons                    # ['TAA', 'TAG', 'AGA', 'AGG']
table.forward_table['TGA']           # 'W' under vertebrate mito code
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Plausible protein, wrong residues, no error | Valid-but-wrong `table=` (e.g. mito DNA on table 1) | Select the organism's NCBI table; use `cds=True` to validate |
| `*` mid-protein or premature truncation | Selenoprotein/pyrrolysine UGA/UAG, or wrong table where UGA=Trp | Use correct mito table for UGA=Trp; Sec/Pyl recoding is not automatic |
| `TranslationError: First codon ... is not a start codon` | `cds=True` on a sequence not starting at a valid start for that table | Trim to the true start, or pick the table whose starts include it |
| `TranslationError: ... is not a multiple of three` | `cds=True` on a partial CDS | Trim to a full ORF; without `cds=True` this only warns and drops trailing bases |
| `TranslationError: Extra in frame stop codon found` | Internal stop under `cds=True` | Wrong frame, wrong table, or genuine internal stop; re-check frame/table |
| Garbage protein from a protein input | `transcribe()`/`translate()` on a non-nucleotide Seq (no type checks since 1.78) | Verify molecule type before converting |
| `KeyError` | Unknown table id or name | Use a valid NCBI id (1-6, 9-16, 21-31) or registered name |

## Decision Tree

```
Need to convert a sequence?
├── DNA <-> RNA (string-level T<->U)?
│   ├── coding strand to RNA -> seq.transcribe()
│   ├── RNA back to DNA      -> seq.back_transcribe()
│   └── template strand to mRNA -> seq.reverse_complement().transcribe()
├── DNA/RNA to protein?
│   ├── alignment-derived CDS    -> alignment/multiple-alignment (codon-aware), or project wrapper
│   ├── complete CDS to validate -> translate(cds=True) [loud on defects]
│   ├── stop at first stop only  -> translate(to_stop=True)
│   ├── non-standard organism    -> translate(table=N)  [pick from the table above]
│   └── show internal stops      -> translate()  [* per stop]
└── Unknown coding regions? -> six-frame translation, then scan M...* for ORFs
```

## Related Skills

- seq-objects - Create and inspect Seq objects before translation
- reverse-complement - Strand handling for six-frame translation and template-strand transcription
- codon-usage - Analyze codon bias and adaptation in coding sequences
- sequence-io/read-sequences - Parse GenBank/FASTA records and CDS features for translation

## References

The genetic-code tables and their organism assignments follow the NCBI Taxonomy "The Genetic Codes" page, compiled by Andrzej (Anjay) Elzanowski and Jim Ostell at NCBI (https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi). This is a maintained web resource; cite it as the NCBI page rather than as a journal article.
<!-- END FILE: sequence-manipulation/transcription-translation/SKILL.md -->

<!-- END CATEGORY: sequence-manipulation -->

