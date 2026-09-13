---
slug: bio-expression-matrix-integrated
version: 1.0.1
displayName: "表达矩阵处理 / Expression matrix handling"
name: bio-expression-matrix-integrated
summary: "中文：表达矩阵处理综合技能，整合 5 个相关专题，覆盖表达矩阵处理：计数矩阵导入、标准化、基因ID映射、稀疏矩阵操作。 English: Integrated Expression matrix handling skill covering 5 related topics, including Expression matrix handling: count matrix import, normalization, gene ID mapping, sparse matrix operations."
description: "中文：这是一个面向表达矩阵处理的综合生物信息学 Skill，整合当前分类下 5 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：表达矩阵处理：计数矩阵导入、标准化、基因ID映射、稀疏矩阵操作。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：DESeq2, biomaRt, pandas。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Expression matrix handling, combining 5 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Expression matrix handling: count matrix import, normalization, gene ID mapping, sparse matrix operations. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: DESeq2, biomaRt, pandas. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# expression-matrix 分类 Skill 整合版

> 本文件整合同一主分类目录下 5 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: expression-matrix -->

## 子目录：expression-matrix/counts-ingest

<!-- BEGIN FILE: expression-matrix/counts-ingest/SKILL.md -->
---
name: bio-expression-matrix-counts-ingest
description: Imports gene expression count matrices from featureCounts, HTSeq, STAR ReadsPerGene, Salmon/kallisto via tximport or tximeta, RSEM, 10X Genomics MTX/H5, AnnData H5AD, and RDS. Handles silent-miscounting traps (featureCounts -p v2.0.2 API break, STAR strandedness column choice, salmon NumReads-sum without tximport, RSEM non-integer expected_count, GENCODE _PAR_Y suffix, zero-length-transcript TPM divide-by-zero), and encodes the tximport countsFromAbundance decision tree with the "lengthScaledTPM is not TPM" warning. Use when assembling a gene-by-sample count matrix from aligner or quantifier output, importing salmon/kallisto for DESeq2 vs limma-voom, choosing strandedness column for STAR, debugging zero-count panics, or building tx2gene mapping.
tool_type: mixed
primary_tool: tximport
---

## Version Compatibility

Reference examples tested with: pandas 2.2+, numpy 1.26+, scanpy 1.10+, anndata 0.10+, tximport 1.30+, tximeta 1.20+, GenomicFeatures 1.54+, Subread/featureCounts 2.0.6+ (post-v2.0.2 API), STAR 2.7.10+, Salmon 1.10+, kallisto 0.48+, RSEM 1.3.3+, HTSeq 2.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Count Matrix Ingestion

**"Load my featureCounts / Salmon / STAR output into a count matrix"** -> Parse the per-sample quantification, strip metadata, choose the correct strandedness or NumReads column, optionally apply length-bias correction via tximport, and return a gene-by-sample matrix appropriate for the downstream DE tool.

## The Single Most Important Modern Insight -- `lengthScaledTPM` is NOT TPM; the naming has fooled many

`tximport(..., countsFromAbundance='lengthScaledTPM')` returns a **count-scale matrix** (sum to library size) with the gene-length bias removed, intended as input to DE tools that cannot accept offsets (limma-voom). The word "TPM" in the option name has misled users into reporting these values as normalized abundance -- they are not.

The decision tree for `countsFromAbundance` (Soneson, Love, Robinson 2015 *F1000Res* 4:1521):

| Option | Returns | Use with |
|--------|---------|----------|
| `'no'` (default) | Raw NumReads; length matrix passed as DESeq2/edgeR offset | DESeq2 via `DESeqDataSetFromTximport`, edgeR via `DGEList` -- the correct path for DGE |
| `'scaledTPM'` | TPM scaled to library size | DGE when downstream tool cannot accept offsets (rare) |
| `'lengthScaledTPM'` | TPM scaled by avg transcript length AND library size | limma-voom for DGE; recommended modern default when offsets unavailable |
| `'dtuScaledTPM'` | Per-transcript scaling by median isoform length | Differential Transcript Usage (DRIMSeq, DEXSeq) ONLY; requires `txOut=TRUE` |

Two adjacent traps with the same flavor of silent miscount:

1. **featureCounts `-p` since v2.0.2 (March 2021) needs `--countReadPairs`**. Pre-v2.0.2, `-p` flagged paired-end AND counted pairs as fragments. Post-v2.0.2, `-p` only flags paired-end -- pairs are NOT counted as one fragment unless `--countReadPairs` is added. Old scripts run on new installs produce ~2x the expected counts (one count per mate). No warning. Always pass `-p --countReadPairs` together for paired-end.

2. **STAR `ReadsPerGene.out.tab` column choice depends on library protocol**. Column 2 is unstranded; column 3 is forward-stranded; column 4 is reverse-stranded. Illumina TruSeq Stranded (the dominant kit, dUTP-based) is reverse-stranded -- column 4. Reading column 3 for TruSeq throws away ~95% of reads. Reading column 2 conflates antisense expression. Verify with RSeQC `infer_experiment.py` on a few BAMs before assembling the matrix.

## Algorithmic Taxonomy

| Source | Output structure | Read into | Caveats |
|--------|------------------|-----------|---------|
| featureCounts (Liao 2014) | TSV with 6 metadata cols + N sample cols | `read.delim` (R), `pd.read_csv(comment='#')` (Python) | -p/--countReadPairs v2.0.2 break; -O double-counts; -s strandedness |
| HTSeq-count (Anders 2015) | Per-sample 2-col TSV with `__` summary lines | Per-sample read, drop `__` rows, concat | `--mode` matters (union vs intersection-strict vs intersection-nonempty); `-s` strandedness |
| STAR `--quantMode GeneCounts` | Per-sample 4-col `ReadsPerGene.out.tab` | Skip first 4 summary rows; pick column by strandedness | Column 4 = TruSeq Stranded |
| Salmon `quant.sf` | Per-sample 5-col TSV (Name, Length, EffectiveLength, TPM, NumReads) | tximport (recommended) or manual NumReads sum (length-biased) | Selective alignment is the default since Salmon 1.0.0 (Srivastava 2020); the `--validateMappings` flag is now a no-op |
| kallisto `abundance.tsv` / `.h5` | Per-sample 5-col TSV; bootstraps in `.h5` | tximport (gene-level) or sleuth (transcript-level with bootstrap variance) | `kallisto quant -b 100` for sleuth |
| RSEM `*.genes.results` / `*.isoforms.results` | Per-sample TSV; expected_count is non-integer | tximport (`type='rsem'`) with `round()` via DESeq2; or manual | Zero-length transcripts cause `lengths > 0 is not TRUE` |
| 10X Genomics CellRanger | filtered_feature_bc_matrix/ MTX dir OR `.h5` | scanpy `read_10x_mtx` / `read_10x_h5`; Seurat `Read10X` | Single-cell convention: cells in rows |
| AnnData `.h5ad` | scverse single-file binary | scanpy `read_h5ad`; in R via zellkonverter | `.X` vs `.layers['counts']` vs `.raw.X` semantics |
| RDS (from R) | R-serialized object | `pyreadr` (Python); base R `readRDS` | For Seurat objects, convert first |

## Decision Tree by Scenario

| Scenario | Recommended approach |
|----------|---------------------|
| Bulk RNA-seq with featureCounts paired-end | `featureCounts -p --countReadPairs -s 2 -t exon -g gene_id` (TruSeq Stranded) |
| Bulk RNA-seq with STAR | `--quantMode GeneCounts`; read column 4 for TruSeq Stranded |
| Salmon/kallisto -> gene-level DGE with DESeq2 | `tximport(type='salmon', tx2gene)` + `DESeqDataSetFromTximport()` -- offsets handled |
| Salmon -> gene-level DGE with limma-voom | `tximport(..., countsFromAbundance='lengthScaledTPM')` -- no offset |
| Salmon/kallisto -> DTE (differential transcript expression) | `tximport(..., txOut=TRUE, countsFromAbundance='dtuScaledTPM')` for DRIMSeq/DEXSeq; OR `edgeR::catchSalmon()` for the Baldoni 2024 framework |
| kallisto with bootstraps -> sleuth (uncertainty-aware DE) | `sleuth_prep()` directly; do not go through tximport |
| RSEM -> DESeq2 | `tximport(files, type='rsem', txIn=FALSE)` + `DESeqDataSetFromTximport()` |
| Want automatic annotation provenance | `tximeta` (Love 2020 *PLoS Comp Biol* 16:e1007664) |
| 3'-tagged library (10x bulk, QuantSeq) | `countsFromAbundance='no'` WITHOUT length offset -- length bias negligible |
| 10X single-cell | `sc.read_10x_h5()` or `Read10X_h5()` |
| Strandedness unknown | RSeQC `infer_experiment.py` on 1-2 BAMs BEFORE re-running quantification |

## featureCounts -- The `-p` and `-O` Traps

**Goal:** Run featureCounts correctly on paired-end stranded RNA-seq, then read the output without inheriting the metadata columns.

**Approach:** CLI invocation with `-p --countReadPairs -s <strandedness>`, plus optional `-O --fraction` for overlapping-gene handling; parse with pandas/read.delim stripping the 6 metadata columns.

```bash
featureCounts -T 8 -p --countReadPairs -s 2 \
    -t exon -g gene_id \
    -a annotation.gtf \
    -o featurecounts.txt \
    sample1.bam sample2.bam sample3.bam
```

```python
import pandas as pd

fc = pd.read_csv('featurecounts.txt', sep='\t', comment='#')
counts = fc.set_index('Geneid').iloc[:, 5:]
counts.columns = [c.replace('.bam', '').split('/')[-1] for c in counts.columns]
```

```r
fc <- read.delim('featurecounts.txt', comment.char = '#', row.names = 1)
counts <- fc[, 6:ncol(fc)]
colnames(counts) <- gsub('.*/|\\.bam$', '', colnames(counts))
```

| Flag | Meaning | Default | When to flip |
|------|---------|---------|--------------|
| `-p` | Input is paired-end | off | Always for paired-end -- AND add `--countReadPairs` |
| `--countReadPairs` | Count fragment (pair) as one | off in v2.0.2+ | Always for paired-end (post-v2.0.2 API change) |
| `-s 0|1|2` | Strandedness | 0 (unstranded) | `-s 2` for TruSeq Stranded; `-s 1` for forward kits |
| `-O` | Allow multi-overlap | off | Off for typical DGE; on creates double-counts in overlapping genes |
| `-M` | Count multi-mappers | off | Off for DGE; on with `--fraction` for fractional counting |
| `-t` | Feature type | `exon` | Almost always `exon` |
| `-g` | Group attribute | `gene_id` | `gene_id` for gene-level; `transcript_id` is wrong (use Salmon for transcript-level) |

## STAR `--quantMode GeneCounts`

**Goal:** Build a count matrix from STAR's per-sample 4-column output, choosing the correct strandedness column.

**Approach:** Skip the first 4 summary rows; index column 0 (gene ID); pick column for strandedness; concat across samples.

```python
import pandas as pd
from pathlib import Path

def load_star_genecounts(filepaths, strandedness='reverse'):
    '''Load STAR ReadsPerGene.out.tab files.
    File columns (1-indexed): 1=gene_id, 2=unstranded, 3=forward, 4=reverse.
    After read_csv with index_col=0, the three remaining columns are 0=unstranded, 1=forward, 2=reverse.
    Illumina TruSeq Stranded is 'reverse'.
    '''
    col_map = {'unstranded': 0, 'forward': 1, 'reverse': 2}
    col_idx = col_map[strandedness]
    dfs = {}
    for fp in filepaths:
        sample = Path(fp).name.replace('_ReadsPerGene.out.tab', '')
        df = pd.read_csv(fp, sep='\t', header=None, index_col=0)
        dfs[sample] = df.iloc[4:, col_idx]
    return pd.DataFrame(dfs)
```

Strandedness verification: for a stranded library, the "wrong" strand column total should be <5% of the "right" strand column total. If comparable, the library was unstranded or there was a kit / config mix-up.

```bash
infer_experiment.py -r annotation.bed -i sample.bam
```

## Salmon / kallisto via tximport

**Goal:** Import transcript-level Salmon or kallisto quantifications to gene-level counts with length-bias correction.

**Approach:** Build a `tx2gene` mapping; call `tximport()` with the right `type` and `countsFromAbundance`; hand the result to DESeq2 or limma-voom.

```r
library(tximport)
library(DESeq2)

tx2gene <- read.csv('tx2gene.csv')

files <- file.path('salmon_out', samples$id, 'quant.sf')
names(files) <- samples$id

txi <- tximport(files, type = 'salmon', tx2gene = tx2gene)

dds <- DESeqDataSetFromTximport(txi, colData = samples, design = ~ condition)
```

The naive alternative -- summing NumReads to gene level -- is wrong when isoform usage varies across samples. NumReads is normalized against EffectiveLength per transcript; sum-then-DE introduces a length-by-condition bias indistinguishable from differential expression. tximport handles this by carrying the per-sample average transcript length matrix as a DESeq2/edgeR offset.

For limma-voom (no offset mechanism):

```r
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene,
                countsFromAbundance = 'lengthScaledTPM')
y <- DGEList(counts = txi$counts)
v <- voom(y, design, plot = TRUE)
```

For DTU (DRIMSeq, DEXSeq), use `dtuScaledTPM` with `txOut=TRUE`.

For 3'-tagged libraries (10x Chromium 3', QuantSeq), length bias is negligible; use `countsFromAbundance='no'` WITHOUT the length offset (`tximeta`'s argument or manual disable).

## tximeta -- Automatic Provenance

**Goal:** Import Salmon/kallisto with automatic linkage to the exact annotation release used in the index.

**Approach:** `tximeta` (Love, Soneson, Hickey et al. 2020 *PLoS Comp Biol* 16:e1007664) inspects the Salmon index hash and pulls matching annotation and metadata; the resulting `SummarizedExperiment` carries the provenance.

```r
library(tximeta)

coldata <- data.frame(
    names = samples$id,
    files = file.path('salmon_out', samples$id, 'quant.sf'),
    condition = samples$condition
)

se <- tximeta(coldata)
gse <- summarizeToGene(se)

library(DESeq2)
dds <- DESeqDataSet(gse, design = ~ condition)
```

For new projects, `tximeta` is the modern preference over hand-managed `tx2gene` -- it eliminates a class of "wrong annotation" bugs.

## HTSeq-count

```python
import pandas as pd
from pathlib import Path

def load_htseq_counts(filepaths):
    '''Load HTSeq count files, dropping the __no_feature etc. summary rows.'''
    dfs = {}
    for fp in filepaths:
        sample = Path(fp).stem.replace('_counts', '')
        df = pd.read_csv(fp, sep='\t', header=None, index_col=0,
                         names=['gene', 'count'])
        df = df[~df.index.str.startswith('__')]
        dfs[sample] = df['count']
    return pd.DataFrame(dfs)
```

HTSeq overlap modes (Anders, Pyl, Huber 2015 *Bioinformatics* 31:166):

| Mode | Behavior |
|------|----------|
| `union` (default) | Read assigned to union of overlapping features; >1 gene -> `__ambiguous` |
| `intersection-strict` | Every base of read must overlap the same single feature |
| `intersection-nonempty` | Intersection across positions; nonempty -> that gene wins |

`-s yes|no|reverse`: TruSeq Stranded is `reverse`. The `--mode` and `-s` flags must match the library; mismatches are silent miscounts.

The `__no_feature` and `__ambiguous` totals are QC signals. If `__no_feature` > 30%: annotation incomplete, wrong reference, or strandedness misspecified. If `__ambiguous` > 10%: many overlapping gene annotations (common with comprehensive GTFs); consider `intersection-nonempty`.

## RSEM expected_count

```r
library(tximport)
library(DESeq2)

files <- file.path('rsem_out', paste0(samples$id, '.genes.results'))
names(files) <- samples$id
txi <- tximport(files, type = 'rsem', txIn = FALSE, txOut = FALSE)

txi$length[txi$length == 0] <- 1

dds <- DESeqDataSetFromTximport(txi, colData = samples, design = ~ condition)
```

RSEM `expected_count` is non-integer (EM-derived). DESeq2 requires integers, but `DESeqDataSetFromTximport` rounds appropriately. The `txi$length == 0` substitution handles the "Error: all(lengths > 0) is not TRUE" panic from rRNA-filtered or zero-length transcripts.

Avoid `round()` + `DESeqDataSetFromMatrix` -- that path loses the length correction.

## kallisto + sleuth (Uncertainty-Aware DE)

```bash
kallisto quant -i index -o sample1_out -b 100 -t 8 read1_1.fq.gz read1_2.fq.gz
```

```r
library(sleuth)

s2c <- data.frame(sample = samples$id,
                  condition = samples$condition,
                  path = file.path('kallisto_out', samples$id))

so <- sleuth_prep(s2c, ~ condition,
                  target_mapping = tx2gene,
                  aggregation_column = 'gene_id',
                  gene_mode = TRUE)
so <- sleuth_fit(so, ~ condition, 'full')
so <- sleuth_fit(so, ~ 1, 'reduced')
so <- sleuth_lrt(so, 'reduced', 'full')
results <- sleuth_results(so, 'reduced:full')
```

Sleuth (Pimentel et al. 2017 *Nat Methods* 14:687) uses the 100 bootstrap replicates from kallisto to decouple BIOLOGICAL variance (between-replicate) from INFERENTIAL variance (within-replicate, from EM uncertainty). For transcript-level analyses where quantification uncertainty matters (similar isoforms, low coverage), sleuth's response error linear model is more conservative than DESeq2 on plain counts. For well-quantified gene-level DGE, sleuth and DESeq2-via-tximport converge.

## Salmon Selective Alignment

Selective alignment (Srivastava 2020 *Genome Biol* 21:239) -- which combines fast pseudo-mapping with traditional alignment of seed extensions to improve quantification accuracy for transcripts with sequence similarity -- has been the **default** since Salmon 1.0.0. The historical `--validateMappings` flag that explicitly requested it is now a deprecated no-op; passing it does nothing.

```bash
salmon quant -i index -l A \
    -1 read_1.fq.gz -2 read_2.fq.gz \
    --gcBias --seqBias \
    -p 8 -o sample_out
```

`--gcBias` corrects fragment GC bias; `--seqBias` corrects random hexamer priming bias. Both are recommended for any Salmon run from RNA-seq with biological condition variation. They affect EffectiveLength estimates and propagate through tximport.

## 10X Genomics

```python
import scanpy as sc

adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')
adata = sc.read_10x_h5('filtered_feature_bc_matrix.h5')
```

```r
library(Seurat)
mat <- Read10X(data.dir = 'filtered_feature_bc_matrix/')
mat <- Read10X_h5('filtered_feature_bc_matrix.h5')
```

10X convention: cells in rows (AnnData) or cells in columns (Seurat after Read10X). The R/Python convention differs by transpose.

## Annotation Pre-Filtering -- rRNA, Mt-rRNA, Pseudogenes

**Goal:** Drop biotypes that distort downstream normalization or are irrelevant to the question.

**Approach:** Filter on `gene_biotype` from the GTF (Ensembl) or `gene_type` (GENCODE).

```r
library(rtracklayer)
gtf <- import('Homo_sapiens.GRCh38.110.gtf.gz')
gene_info <- as.data.frame(gtf[gtf$type == 'gene',
                                c('gene_id', 'gene_name', 'gene_biotype')])

keep_biotypes <- c('protein_coding', 'lncRNA',
                   'IG_C_gene', 'IG_D_gene', 'IG_J_gene', 'IG_V_gene',
                   'TR_C_gene', 'TR_D_gene', 'TR_J_gene', 'TR_V_gene')
keep_genes <- gene_info$gene_id[gene_info$gene_biotype %in% keep_biotypes]
counts_filt <- counts[rownames(counts) %in% keep_genes, ]
```

Mt-encoded protein-coding genes (MT-CO1, MT-ND1, ...) are a judgment call: include for tissue-specific work (heart, muscle); drop when mitochondrial fraction varies with cell stress and could confound normalization.

In single-cell, mitochondrial percentage is a STANDARD QC metric (cells with high %mito are stressed/dying); see `single-cell/preprocessing`.

## GENCODE vs Ensembl -- What Differs at the File Level

| Difference | Ensembl | GENCODE |
|------------|---------|---------|
| chromosome naming | `1`, `2`, ..., `MT` | `chr1`, `chr2`, ..., `chrM` |
| PAR gene encoding (releases 25-43) | Once on chrX | Both chrX and chrY with `_PAR_Y` suffix on chrY copies |
| PAR gene encoding (releases 44+ / Ensembl 110+) | Once on chrX | chrY copies get their own ENSG accessions; `_PAR_Y` retired |
| Subset releases | Single release | `basic` (high-confidence subset) and `comprehensive` (everything) |

CRITICAL: code that strips Ensembl version suffixes via `sub('\\..*', '', x)` ALSO strips the `_PAR_Y` tag in GENCODE 25-43, collapsing the chrY duplicate onto the chrX gene -- silently introducing duplicate row indices. Use `sub('\\.[0-9]+(_PAR_Y)?$', '\\1', x)` to preserve.

BAM files aligned to GENCODE (`chr1`) cannot be quantified against Ensembl GTF (`1`) without rename. Mismatched naming causes `__no_feature` to dominate.

## Filter Low-Count Genes

```r
library(edgeR)

y <- DGEList(counts = counts, group = group)
keep <- filterByExpr(y, design = model.matrix(~ condition, coldata))
y <- y[keep, , keep.lib.sizes = FALSE]
```

```python
min_counts, min_samples = 10, 3
expressed = (counts >= min_counts).sum(axis=1) >= min_samples
counts_filt = counts.loc[expressed]
```

See `differential-expression/edger-basics` for `filterByExpr` semantics. DESeq2 has automatic independent filtering at `results()` time; manual pre-filter is speed-only.

## Per-Method Failure Modes

### featureCounts paired-end double-counted

**Trigger:** Pipeline written against featureCounts pre-v2.0.2 used `-p` only; rerun on Subread 2.0.6 produces counts ~2x expected.

**Mechanism:** Post-v2.0.2 `-p` flags paired-end but does NOT count pairs as fragments. Each mate is counted separately.

**Symptom:** Library sizes ~2x what RNA-seq QC reports; downstream CPM compressed; "more reads than expected" panic.

**Fix:** Add `--countReadPairs`. Re-run featureCounts.

### STAR wrong strandedness column

**Trigger:** TruSeq Stranded library quantified via STAR; user reads column 3 (forward); ~95% of reads dropped.

**Mechanism:** TruSeq Stranded is reverse-stranded (column 4). Column 3 is forward-stranded; for a reverse library, almost no reads align in the forward orientation.

**Symptom:** Library sizes ~5% of expected; almost no DE detectable; very low gene detection rate.

**Fix:** Read column 4. Verify with `infer_experiment.py`.

### Salmon NumReads summed naively -> length-by-condition bias

**Trigger:** Salmon output read without tximport; per-transcript NumReads summed to gene level via groupby.

**Mechanism:** NumReads is normalized against per-transcript EffectiveLength. Summing ignores that. If treatment shifts isoform usage from short to long, the gene appears upregulated even with constant total mRNA.

**Symptom:** DE genes overlap with known isoform-switching genes (e.g., during development); fold changes don't replicate at the protein level.

**Fix:** Use `tximport` (or `catchSalmon` in edgeR) to carry the length matrix as a DE offset.

### RSEM zero-length transcript breaks tximport

**Trigger:** `tximport(files, type='rsem')` errors out with "all(lengths > 0) is not TRUE".

**Mechanism:** RSEM reports `effective_length = 0` for certain very-short or filtered transcripts.

**Symptom:** Pipeline halts at import.

**Fix:** `txi$length[txi$length == 0] <- 1` after `tximport`; or filter `tx2gene` to exclude affected transcripts.

### `_PAR_Y` stripped, chrY duplicates lost

**Trigger:** GENCODE v40 quantification; `rownames(counts) <- sub('\\..*', '', rownames(counts))`; duplicate row indices.

**Mechanism:** Default regex strips `_PAR_Y` along with the version suffix; chrY PAR copies collapse onto chrX gene IDs.

**Symptom:** Duplicate row warnings; sample-specific counts double for affected genes; downstream `aggregate(... ~ rownames)` adds them.

**Fix:** Use the regex that preserves `_PAR_Y`: `sub('\\.[0-9]+(_PAR_Y)?$', '\\1', x)`. Or upgrade to GENCODE 44+ where the issue is gone.

### HTSeq mode mismatched to library

**Trigger:** Mouse RNA-seq with `--mode intersection-strict`; many overlapping-gene reads dropped; library size 30% lower than featureCounts on the same data.

**Mechanism:** `intersection-strict` requires every base to overlap the same feature; reads crossing exon-intron boundaries or overlapping gene boundaries get dropped.

**Symptom:** Lower count totals than other quantifiers; `__no_feature` and `__ambiguous` high.

**Fix:** `--mode union` (default) or `--mode intersection-nonempty` for richer recovery.

## Common errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `Error: all(lengths > 0) is not TRUE` | RSEM zero-length transcripts | `txi$length[txi$length == 0] <- 1` |
| Duplicate row indices after version strip | `_PAR_Y` collapsed | Use the preserving regex |
| `__no_feature` >30% | Wrong reference; wrong strandedness; chrN naming mismatch | Verify reference + strandedness; check chr vs N naming |
| `counts matrix should be integers` | Salmon/RSEM raw counts to DESeq2 | Use `DESeqDataSetFromTximport`; or round (loses length correction) |
| Library sizes ~2x expected for paired-end | featureCounts v2.0.2 `-p` without `--countReadPairs` | Add `--countReadPairs` |
| TPM column has Inf values | Zero-length features | Filter `Length > 0` before TPM computation |
| Salmon TPM doesn't sum to 1e6 | Pre-summed across samples or filtered subset | Recompute TPM after filter; or use original abundance column |

## References

- Liao Y, Smyth GK, Shi W. 2014. featureCounts: an efficient general purpose program for assigning sequence reads to genomic features. *Bioinformatics* 30(7):923-930. doi:10.1093/bioinformatics/btt656
- Anders S, Pyl PT, Huber W. 2015. HTSeq -- a Python framework to work with high-throughput sequencing data. *Bioinformatics* 31(2):166-169. doi:10.1093/bioinformatics/btu638
- Dobin A et al. 2013. STAR: ultrafast universal RNA-seq aligner. *Bioinformatics* 29(1):15-21. doi:10.1093/bioinformatics/bts635
- Patro R, Duggal G, Love MI, Irizarry RA, Kingsford C. 2017. Salmon provides fast and bias-aware quantification of transcript expression. *Nat Methods* 14(4):417-419. doi:10.1038/nmeth.4197
- Srivastava A, Malik L, Sarkar H, Zakeri M, Almodaresi F, Soneson C, Love MI, Kingsford C, Patro R. 2020. Alignment and mapping methodology influence transcript abundance estimation. *Genome Biol* 21:239. doi:10.1186/s13059-020-02151-8
- Bray NL, Pimentel H, Melsted P, Pachter L. 2016. Near-optimal probabilistic RNA-seq quantification. *Nat Biotechnol* 34(5):525-527. doi:10.1038/nbt.3519
- Pimentel H, Bray NL, Puente S, Melsted P, Pachter L. 2017. Differential analysis of RNA-seq incorporating quantification uncertainty. *Nat Methods* 14(7):687-690. doi:10.1038/nmeth.4324
- Soneson C, Love MI, Robinson MD. 2015. Differential analyses for RNA-seq: transcript-level estimates improve gene-level inferences. *F1000Res* 4:1521. doi:10.12688/f1000research.7563.2
- Love MI, Soneson C, Hickey PF, Johnson LK, Pierce NT, Shepherd L, Morgan M, Patro R. 2020. Tximeta: Reference sequence checksums for provenance identification in RNA-seq. *PLoS Comput Biol* 16(2):e1007664. doi:10.1371/journal.pcbi.1007664
- Frankish A et al. 2021. GENCODE 2021. *Nucleic Acids Res* 49(D1):D916-D923. doi:10.1093/nar/gkaa1087

## Related Skills

- gene-id-mapping - Building tx2gene; Ensembl version stripping with PAR_Y preservation
- normalization - Composition bias, TMM/RLE, the "biotype filter before normalize" rationale
- metadata-joins - Sample name reconciliation across counts and metadata
- sparse-handling - Single-cell sparse matrix formats
- differential-expression/deseq2-basics - tximport -> DESeqDataSetFromTximport workflow
- differential-expression/edger-basics - catchSalmon for transcript-level DTE
- differential-expression/batch-correction - Batch covariate vs subtraction
- rna-quantification/featurecounts-counting - Detailed featureCounts run patterns
- rna-quantification/alignment-free-quant - Salmon/kallisto invocation details
- rna-quantification/tximport-workflow - Detailed tximport workflow
- read-alignment/star-alignment - STAR upstream of GeneCounts
- read-qc/quality-reports - RIN, DV200 inputs to consider
<!-- END FILE: expression-matrix/counts-ingest/SKILL.md -->

## 子目录：expression-matrix/gene-id-mapping

<!-- BEGIN FILE: expression-matrix/gene-id-mapping/SKILL.md -->
---
name: bio-expression-matrix-gene-id-mapping
description: Maps between gene identifier systems (Ensembl, Entrez, HGNC symbol, UniProt, RefSeq, MANE) using AnnotationDbi, biomaRt, mygene, pyensembl, and Ensembl REST. Encodes Ensembl version stripping with GENCODE _PAR_Y preservation, the Ziemann 2016 Excel autocorrect debacle and Bruford 2020 HGNC renames (SEPT*->SEPTIN*, MARCH*->MARCHF*, MARC*->MTARC*, DEC1->DELEC1), OCT4/POU5F1 alias resolution, biomaRt archive endpoints for release pinning, the `filters` (plural) gotcha, MANE Select for clinical reporting, cross-species orthology via Ensembl Compara / OMA / OrthoDB, and tx2gene construction for tximport. Use when converting gene IDs across systems, handling renamed symbols, building tx2gene, pinning to a specific Ensembl release for reproducibility, or mapping cross-species orthologs.
tool_type: mixed
primary_tool: biomaRt
---

## Version Compatibility

Reference examples tested with: biomaRt 2.58+, AnnotationDbi 1.66+, org.Hs.eg.db 3.18+, org.Mm.eg.db 3.18+, GenomicFeatures 1.54+, mygene 1.38+ (Python), pyensembl 2.3+, pandas 2.2+, rtracklayer 1.62+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Gene ID Mapping

**"Convert gene IDs from X to Y"** -> Query the appropriate annotation source (local org.db for speed, biomaRt for Ensembl-specific attributes, mygene for cross-database aliases, Ensembl REST for low-level access), with version pinning for reproducibility and explicit handling of one-to-many mappings, withdrawn symbols, and species-specific naming.

## The Single Most Important Modern Insight -- Excel autocorrect renamed real genes

Ziemann, Eren, El-Osta 2016 *Genome Biol* 17:177 scanned 18 leading genomics journals and found ~20% of papers with Excel-attached supplementary gene lists had silently mangled symbols (`SEPT2` -> `2-Sep`, `MARCH1` -> `1-Mar`, ...). Five years later the problem persisted. HGNC's response (Bruford, Braschi, Denny, Jones, Seal, Tweedie 2020 *Nat Genet* 52:754) was to rename the affected genes:

| Old | New | Affected |
|-----|-----|----------|
| `SEPT#` | `SEPTIN#` | SEPT1 - SEPT14 -> SEPTIN1 - SEPTIN14 |
| `MARCH#` | `MARCHF#` | MARCH1 - MARCH11 -> MARCHF1 - MARCHF11 |
| `MARC#` | `MTARC#` | MARC1, MARC2 -> MTARC1, MTARC2 |
| `DEC1` | `DELEC1` | DEC1 -> DELEC1 |

Code that hard-codes old symbols silently drops these genes when joined against post-2020 annotations. Detection on import: if a gene column contains `^\d{1,2}-(Jan|Feb|Mar|...|Dec)$` patterns, the file was Excel-corrupted. Always `read.csv(colClasses=c(gene='character'))` (R) or `pd.read_csv(dtype={'gene': str})` (Python) -- but the damage is at Excel-save time, not import time.

Two related insights that determine half the practical work:

1. **Ensembl version suffixes matter sometimes and not others.** `ENSG00000123456.7` is release-specific; the unversioned `ENSG00000123456` is the stable cross-release ID. STRIP for cross-release joins, MSigDB lookups, gene-set databases. KEEP for intra-release reproducibility and clinical reports. CRITICAL: the naive `sub('\\..*', '', x)` regex ALSO strips the GENCODE `_PAR_Y` suffix in releases 25-43, collapsing chrY PAR duplicates onto their chrX counterparts. Use `sub('\\.[0-9]+(_PAR_Y)?$', '\\1', x)`.

2. **Never use HGNC symbols as the primary computational key.** Symbols change. Use Ensembl or Entrez as keys; carry symbols only as display labels in the final results table.

## Algorithmic Taxonomy

| Tool | Source | Speed | Strength | Use for |
|------|--------|-------|----------|---------|
| AnnotationDbi + `org.Hs.eg.db` / `org.Mm.eg.db` | NCBI Gene snapshot, pinned at Bioc install | Fast, local | Stable, version-pinned | Default for Ensembl <-> Entrez <-> Symbol within Bioconductor |
| biomaRt | Ensembl BioMart over HTTP | Slow for >5k queries; timeouts | Ensembl-specific attributes (biotype, transcript versions, paralogs, orthologs) | Need Ensembl-specific fields; archive endpoints for release pinning |
| mygene.info / mygene (Python) | REST API to a curated meta-database | Server-side batching of 1000 IDs | Best for symbol/alias/prev_symbol resolution | Cross-database; HGNC withdrawn symbol resolution; non-R environments |
| Ensembl REST | Direct REST API to Ensembl | Rate-limited (15 req/sec) | Low-level access to variant consequence, sequence, etc. | Specialized queries not covered by biomaRt |
| pyensembl | Local Ensembl database (Python) | Fast, local, version-pinned | Reproducible offline; gene objects with transcript and exon access | Python pipelines needing rich annotation |
| HGNC API direct | https://rest.genenames.org | REST | Authoritative source for HGNC | Symbol provenance, prev/alias detection |

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| R Bioconductor pipeline, Ensembl <-> Entrez <-> Symbol | `AnnotationDbi::mapIds(org.Hs.eg.db, ...)` | Fastest, version-pinned, stable |
| Need Ensembl-only attributes (biotype, paralog, ortholog) | `biomaRt::useEnsembl(version=N)` | Only biomaRt exposes these |
| Cross-database with alias and withdrawn-symbol fallback | mygene `querymany(scopes='symbol,alias,prev_symbol')` | Designed for this case |
| Python pipeline, reproducible | `pyensembl` with pinned release | Offline, version-locked |
| Clinical report needing canonical transcript per gene | MANE Select (Morales 2022 *Nature* 604:310) | Cross-database consensus (RefSeq + Ensembl) |
| Cross-species mouse <-> human | Ensembl Compara `getLDS` filtered to `one2one` | Compara has best coverage; one2one most defensible |
| Building tx2gene for tximport | `GenomicFeatures::makeTxDbFromGFF` on the SAME GTF used in quantification | Annotation pinning matters |
| Need to reproduce a 2023 analysis exactly | `useEnsembl(version=109)` (or whichever release was used) | Without `version=`, biomaRt floats to current release |
| GRCh37 (legacy clinical) | `useEnsembl(GRCh=37)` dedicated permanent endpoint | GRCh37 -> GRCh38 mappings are not 1:1 |

## AnnotationDbi + org.db

**Goal:** Map Ensembl gene IDs to symbols, Entrez IDs, or descriptions using a local Bioconductor annotation package.

**Approach:** `mapIds()` with the source keytype and target column; handle one-to-many via `multiVals`.

```r
library(org.Hs.eg.db)
library(AnnotationDbi)

ensembl_ids <- sub('\\.[0-9]+(_PAR_Y)?$', '\\1', rownames(counts))

symbols  <- mapIds(org.Hs.eg.db, keys = ensembl_ids,
                    keytype = 'ENSEMBL', column = 'SYMBOL',
                    multiVals = 'first')
entrez   <- mapIds(org.Hs.eg.db, keys = ensembl_ids,
                    keytype = 'ENSEMBL', column = 'ENTREZID',
                    multiVals = 'first')
descrips <- mapIds(org.Hs.eg.db, keys = ensembl_ids,
                    keytype = 'ENSEMBL', column = 'GENENAME',
                    multiVals = 'first')

keytypes(org.Hs.eg.db)
```

`multiVals` options: `'first'` (silent), `'asNA'` (NA for ambiguous), `'list'` (preserve all). For DE results tables, `'first'` is typical but the mapping rate should be reported.

For mouse: `org.Mm.eg.db`. For other organisms: check Bioconductor `AnnotationData -> OrgDb` list.

## biomaRt with Version Pinning

**Goal:** Query Ensembl BioMart with the EXACT release version, for reproducibility.

**Approach:** `useEnsembl(version=N)` pins; `listEnsemblArchives()` lists available archives.

```r
library(biomaRt)

ensembl <- useEnsembl(biomart = 'genes',
                       dataset = 'hsapiens_gene_ensembl',
                       version = 110)

ensembl_grch37 <- useEnsembl(biomart = 'genes',
                              dataset = 'hsapiens_gene_ensembl',
                              GRCh = 37)

mapping <- getBM(
    attributes = c('ensembl_gene_id', 'hgnc_symbol', 'entrezgene_id',
                   'gene_biotype', 'description'),
    filters    = 'ensembl_gene_id',
    values     = ensembl_ids,
    mart       = ensembl
)
```

The `filters=` argument is PLURAL. The singular `filter=` may work via R's partial matching but breaks unpredictably if another argument starts with `f`. Always spell `filters=` and `values=` fully.

Multiple filters:

```r
genes_in_region <- getBM(
    attributes = c('ensembl_gene_id', 'hgnc_symbol'),
    filters    = c('chromosome_name', 'start', 'end'),
    values     = list('16', 1100000, 1250000),
    mart       = ensembl
)
```

Without `version=`, biomaRt floats to the current release -- a script written in 2023 against Ensembl 109 produces different mappings in 2026 against Ensembl 113. ALWAYS pin for any published analysis. Cache the mapping table alongside the analysis for reproducibility.

`listEnsemblArchives()` shows the available historical releases.

## mygene (Python)

**Goal:** Map between any identifier systems using the curated MyGene.info meta-database with alias fallback.

**Approach:** `MyGeneInfo().querymany(ids, scopes, fields, species)`; auto-batches at 1000 IDs server-side.

```python
import mygene

mg = mygene.MyGeneInfo()

results = mg.querymany(['ENSG00000141510', 'ENSG00000012048', 'ENSG00000141736'],
                        scopes='ensembl.gene', fields='symbol,entrezgene,uniprot',
                        species='human')

mapping = {r['query']: r.get('symbol', None) for r in results}

results = mg.querymany(['SEPT1', 'MARCH1', 'OCT4'],
                        scopes='symbol,alias,prev_symbol',
                        fields='symbol,entrezgene,ensembl.gene',
                        species='human')
```

For paper-derived gene lists where symbols may be old or aliases (OCT4 vs POU5F1, MARCH1 vs MARCHF1, SEPT2 vs SEPTIN2), `scopes='symbol,alias,prev_symbol'` handles the resolution. The MyGene database aggregates HGNC's prev/alias columns.

OCT4 is the common usage; POU5F1 is the official HGNC symbol; in MSigDB the gene is POU5F1; in a Western blot legend it's "Oct4". For mapping a stem-cell paper to an Ensembl-quantified matrix, scope to aliases.

## pyensembl

```python
from pyensembl import EnsemblRelease

ensembl = EnsemblRelease(110, species='human')

gene = ensembl.gene_by_id('ENSG00000141510')
gene.gene_name

gene = ensembl.genes_by_name('TP53')[0]
gene.gene_id

mapping = {}
for eid in ensembl_ids:
    try:
        gene = ensembl.gene_by_id(eid.split('.')[0])
        mapping[eid] = gene.gene_name
    except ValueError:
        mapping[eid] = None
```

pyensembl downloads and caches the release database on first use; thereafter offline and version-locked.

## Apply Mapping to Count Matrix -- Handling One-to-Many

**Goal:** Convert the gene index of a count matrix to a different ID type, summing reads from multiple source IDs that map to the same target.

**Approach:** Look up mapping, replace index, aggregate duplicates by SUM (not mean -- counts add).

```python
import pandas as pd
import mygene

def map_count_matrix_ids(counts, from_type='ensembl.gene', to_type='symbol',
                         species='human'):
    '''Map gene IDs in count matrix index, summing reads when multiple source map to one target.'''
    mg = mygene.MyGeneInfo()
    clean = [g.split('.')[0] for g in counts.index]
    results = mg.querymany(clean, scopes=from_type, fields=to_type, species=species)
    mapping = {r['query']: r[to_type] for r in results if to_type in r}
    new_index = [mapping.get(g.split('.')[0], g) for g in counts.index]
    counts_mapped = counts.copy()
    counts_mapped.index = new_index
    counts_mapped = counts_mapped.groupby(counts_mapped.index).sum()
    return counts_mapped

mapped = map_count_matrix_ids(counts, 'ensembl.gene', 'symbol')
```

Counts ADD when collapsing multiple source genes to one target. Means or medians would be wrong (they understate library size for the merged target).

```r
library(biomaRt)

ensembl <- useEnsembl(biomart = 'genes', dataset = 'hsapiens_gene_ensembl', version = 110)

clean <- sub('\\.[0-9]+(_PAR_Y)?$', '\\1', rownames(counts))

mapping <- getBM(
    attributes = c('ensembl_gene_id', 'hgnc_symbol'),
    filters    = 'ensembl_gene_id',
    values     = clean,
    mart       = ensembl
)

counts_df <- as.data.frame(counts)
counts_df$ensembl <- clean
merged <- merge(counts_df, mapping, by.x = 'ensembl', by.y = 'ensembl_gene_id')
counts_by_symbol <- aggregate(. ~ hgnc_symbol,
                              data = merged[, setdiff(colnames(merged), 'ensembl')],
                              FUN = sum)
rownames(counts_by_symbol) <- counts_by_symbol$hgnc_symbol
counts_by_symbol$hgnc_symbol <- NULL
```

## Handle Unmapped IDs

```python
def robust_id_mapping(gene_ids, from_type, to_type, species='human'):
    import mygene
    mg = mygene.MyGeneInfo()
    clean = [g.split('.')[0] for g in gene_ids]
    results = mg.querymany(clean, scopes=from_type, fields=to_type, species=species)
    mapping, unmapped = {}, []
    for r in results:
        original = gene_ids[clean.index(r['query'])]
        if to_type in r:
            mapping[original] = r[to_type]
        else:
            mapping[original] = original
            unmapped.append(original)
    print(f'Mapped: {len(gene_ids) - len(unmapped)}/{len(gene_ids)}')
    return mapping, unmapped
```

Unmapped fraction is a QC signal:
- <5% unmapped: normal (rare genes, recent deprecations)
- 5-20% unmapped: check Ensembl release alignment; check for HGNC renames
- >20% unmapped: wrong annotation release, wrong species, or wrong source ID type

## MANE Select for Clinical Reporting

**Goal:** Use the single representative transcript per gene with identical exon/CDS in RefSeq AND Ensembl for clinical variant reporting.

**Approach:** Download the MANE TSV; join on `Ensembl_Gene` -> `Ensembl_nuc` (transcript) and `RefSeq_nuc`.

Morales J, Pujar S, Loveland JE et al. 2022 *Nature* 604:310-315 established MANE Select. ~19,000+ protein-coding genes have a single agreed transcript with matched coordinates across RefSeq (NM_xxxxxx) and Ensembl/GENCODE (ENST00000xxxxxxx). MANE Plus Clinical adds extra transcripts at loci where Select misses clinical variants.

For clinical reports with HGVS notation like `NM_000546.6:c.215C>G`, use the MANE Select RefSeq accession. The MANE TSV (downloadable from NCBI) provides the Ensembl crosswalk.

## Cross-Species Orthologs

**Goal:** Map mouse <-> human (or any pair) for cross-species integration or pathway transfer.

**Approach:** Ensembl Compara via biomaRt `getLDS`; filter to orthology type appropriate to use.

```r
library(biomaRt)

human <- useEnsembl(biomart = 'genes', dataset = 'hsapiens_gene_ensembl', version = 110)
mouse <- useEnsembl(biomart = 'genes', dataset = 'mmusculus_gene_ensembl', version = 110)

orthologs <- getLDS(
    attributes  = c('hgnc_symbol', 'ensembl_gene_id'),
    filters     = 'ensembl_gene_id',
    values      = human_gene_ids,
    mart        = human,
    attributesL = c('mgi_symbol', 'ensembl_gene_id', 'mmusculus_homolog_orthology_type'),
    martL       = mouse
)
```

| Strategy | When | Trade-off |
|----------|------|-----------|
| `one2one` orthologs only | Cross-species scRNA-seq integration; conservative DE comparison | Loses genes with paralog expansions; lower coverage |
| Include `one2many` | Broader gene coverage needed | Must select within group (highest confidence; highest expression) |
| Include `many2many` | Maximum inclusivity | Introduces ambiguity; use with caution |

The "homology threshold" problem: no automatic threshold reliably separates true orthologs from paralogs across all gene families. For pathway transfer (mouse signature -> human), filter to one2one and accept the coverage loss.

Alternative sources: OMA (Hierarchical Orthologous Groups, cleaner one2one when present, smaller coverage); OrthoDB (hierarchical at multiple taxonomic levels). OrthoFinder for custom genomes.

## PAR Gene Complications

Pseudo-autosomal region (PAR) genes exist on both X and Y with identical sequences. In GENCODE 25-43, the chrY copy has a `_PAR_Y` suffix. In GENCODE 44+ (Ensembl 110+), chrY PAR genes get their own ENSG accessions.

```python
par_genes_human = ['SHOX', 'IL3RA', 'SLC25A6', 'P2RY8', 'AKAP17A', 'ASMT', 'DHRSX']
dup_ids = counts.index[counts.index.duplicated()].unique()
if len(dup_ids) > 0:
    print(f'Duplicate gene entries: {len(dup_ids)}')
    counts = counts.groupby(counts.index).sum()
```

Reads from PAR regions cannot be unambiguously assigned to X or Y. Some references mask the Y-chromosome PAR to avoid double-counting; verify what the alignment reference does before building the matrix.

## Build tx2gene for tximport

**Goal:** Create the transcript-to-gene mapping needed by tximport for gene-level summarization.

**Approach:** Build from the SAME GTF used to construct the Salmon/kallisto index, OR pull from biomaRt with version pinning.

```r
library(GenomicFeatures)

txdb <- makeTxDbFromGFF('annotation.gtf.gz')
k <- keys(txdb, keytype = 'TXNAME')
tx2gene <- AnnotationDbi::select(txdb, k, 'GENEID', 'TXNAME')
```

```r
library(biomaRt)

mart <- useEnsembl(biomart = 'genes', dataset = 'hsapiens_gene_ensembl', version = 110)
tx2gene <- getBM(
    attributes = c('ensembl_transcript_id_version', 'ensembl_gene_id_version'),
    mart       = mart
)
colnames(tx2gene) <- c('TXNAME', 'GENEID')
```

```python
import pandas as pd

def tx2gene_from_gtf(gtf_path):
    records = []
    with open(gtf_path) as f:
        for line in f:
            if line.startswith('#') or '\ttranscript\t' not in line:
                continue
            attrs = line.strip().split('\t')[8]
            gene_id = [a.split('"')[1] for a in attrs.split(';') if 'gene_id' in a][0]
            tx_id   = [a.split('"')[1] for a in attrs.split(';') if 'transcript_id' in a][0]
            records.append({'TXNAME': tx_id, 'GENEID': gene_id})
    return pd.DataFrame(records).drop_duplicates()
```

CRITICAL: the tx2gene MUST use the same versioning convention as the Salmon/kallisto index. If the index used `ENST00000269305.9` and tx2gene has `ENST00000269305` (unversioned), tximport drops the transcripts. Mismatched versions silently lose data.

## ID Type Reference

| Type | Example | Stability | Use case |
|------|---------|-----------|----------|
| Ensembl Gene | ENSG00000141510 | Stable across releases; versioned | RNA-seq, GTFs, primary computational key |
| Ensembl Transcript | ENST00000269305 | Stable; versioned | Transcript-level analysis |
| Entrez Gene | 7157 | Stable; never reused | NCBI databases, KEGG pathways |
| HGNC Symbol | TP53 | Changes (see SEPT/MARCH renames) | Display labels only |
| UniProt | P04637 | Stable; versioned releases | Protein databases |
| RefSeq mRNA | NM_000546 | Stable; versioned | Clinical reports, HGVS notation |
| MANE Select | NM_000546.6 / ENST00000269305.9 | Stable consensus | Clinical variant reporting |

## Per-Method Failure Modes

### `_PAR_Y` stripped, chrY duplicates collapsed

**Trigger:** GENCODE v40 count matrix; `rownames(counts) <- sub('\\..*', '', rownames(counts))`; duplicate row indices and inflated chrY PAR gene counts.

**Mechanism:** Default regex strips `_PAR_Y` along with the version suffix. Two distinct rows (chrX and chrY copies) become the same ENSG ID; `aggregate` sums them.

**Symptom:** Counts for PAR genes double; sex check shows females expressing chrY genes; downstream `rowGroupBy` returns warnings.

**Fix:** Use the preserving regex: `sub('\\.[0-9]+(_PAR_Y)?$', '\\1', x)`. Or upgrade quantification to GENCODE 44+ where `_PAR_Y` is retired.

### `biomaRt` returned 0 rows without warning

**Trigger:** `getBM(attributes=..., filter='ensembl_gene_id', values=ids, mart=mart)` -- note singular `filter`.

**Mechanism:** R's partial matching usually resolves `filter` -> `filters`, but in some package versions or with conflicting argument names, the call silently passes nothing.

**Symptom:** Empty result data frame; no error.

**Fix:** Always spell `filters=` and `values=` fully.

### HGNC SEPT/MARCH symbols silently dropped

**Trigger:** Code copies a pre-2020 list of septin genes (`SEPT1`, `SEPT2`, ...); current org.db / biomaRt returns no matches.

**Mechanism:** HGNC renamed all `SEPT#` to `SEPTIN#` in 2020.

**Symptom:** 0% mapping rate for septin genes; functional analyses missing septin pathways.

**Fix:** Use mygene `scopes='symbol,alias,prev_symbol'`; or update the input list to current symbols.

### biomaRt drift between runs

**Trigger:** A 2023 analysis used `useEnsembl()` without `version=`; rerun in 2026 produces 200 fewer significant genes.

**Mechanism:** Without `version=`, biomaRt floats to the current release. Symbols, biotypes, and gene boundaries change between releases.

**Symptom:** Non-reproducible results across runs of the same script.

**Fix:** Pin `useEnsembl(version=N)` where N is the release used in the original analysis. Cache the mapping table.

### tx2gene version mismatch with Salmon index

**Trigger:** `tximport(files, type='salmon', tx2gene)` runs but the gene-level counts have far fewer genes than expected.

**Mechanism:** Salmon index built with versioned transcript IDs (`ENST00000269305.9`) but tx2gene has unversioned IDs (`ENST00000269305`). Transcripts silently drop during the mapping step.

**Symptom:** Lower-than-expected gene count; warning from tximport about missing transcript IDs.

**Fix:** Match versioning convention: rebuild tx2gene with the same versioning as the index. `GenomicFeatures::makeTxDbFromGFF` on the same GTF as the index is the safest path.

### Cross-species mapping reports many2many, user picks one arbitrarily

**Trigger:** Mouse-to-human mapping returns 1.3 mouse genes per human gene on average; user takes the first row of each duplicate.

**Mechanism:** Many2many orthology is genuinely ambiguous; "first row" is unprincipled and irreproducible across biomaRt API versions.

**Symptom:** Different mappings on rerun; conflicting downstream gene sets.

**Fix:** Either filter to `mmusculus_homolog_orthology_type == 'ortholog_one2one'` (conservative) or aggregate via highest homology confidence score (`mmusculus_homolog_perc_id_r1`).

## Common errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `filters` returns empty | Singular `filter=` partial-matched against another argument | Spell `filters=` fully |
| `1-Mar` in gene column | Excel autocorrected `MARCH1` | Re-import with explicit string type; map back to MARCHF1 |
| pyensembl `ValueError: gene not found` | ID not in pinned release; or unversioned ID against versioned database | Strip version before lookup; verify release |
| Duplicate rownames after aggregate | Collapsed multiple source IDs to one target; OR `_PAR_Y` stripped | Sum-collapse expected; for PAR_Y use preserving regex |
| biomaRt timeout for >5k IDs | Query too large | Chunk into batches of 1000 |
| Wrong species mapping | Default `species='human'` in mygene; mouse query returns nothing | Pass `species='mouse'` explicitly |
| `ENSEMBL` keytype not available | Older org.db package or non-human/mouse | `keytypes(orgdb)` to verify |

## References

- Ziemann M, Eren Y, El-Osta A. 2016. Gene name errors are widespread in the scientific literature. *Genome Biol* 17:177. doi:10.1186/s13059-016-1044-7
- Bruford EA, Braschi B, Denny P, Jones TEM, Seal RL, Tweedie S. 2020. Guidelines for human gene nomenclature. *Nat Genet* 52:754-758. doi:10.1038/s41588-020-0669-3
- Morales J, Pujar S, Loveland JE, et al. 2022. A joint NCBI and EMBL-EBI transcript set for clinical genomics and research. *Nature* 604:310-315. doi:10.1038/s41586-022-04558-8
- Durinck S, Spellman PT, Birney E, Huber W. 2009. Mapping identifiers for the integration of genomic datasets with the R/Bioconductor package biomaRt. *Nat Protoc* 4(8):1184-1191. doi:10.1038/nprot.2009.97
- Carlson M, Falcon S, Pages H, Li N. 2019. org.Hs.eg.db: Genome wide annotation for Human. R package. Bioconductor.
- Wu C et al. 2013. BioGPS and MyGene.info: organizing online, gene-centric information. *Nucleic Acids Res* 41(D1):D561-D565. doi:10.1093/nar/gks1114
- Frankish A et al. 2021. GENCODE 2021. *Nucleic Acids Res* 49(D1):D916-D923. doi:10.1093/nar/gkaa1087
- Howe KL et al. 2021. Ensembl 2021. *Nucleic Acids Res* 49(D1):D884-D891. doi:10.1093/nar/gkaa942
- Soneson C, Love MI, Robinson MD. 2015. Differential analyses for RNA-seq: transcript-level estimates improve gene-level inferences. *F1000Res* 4:1521. doi:10.12688/f1000research.7563.2

## Related Skills

- counts-ingest - Building count matrices and tx2gene
- metadata-joins - Joining annotation with sample tables
- normalization - Biotype filtering before normalization
- sparse-handling - Single-cell row metadata in AnnData
- differential-expression/de-results - Annotating DE results; gene-symbol display
- rna-quantification/tximport-workflow - Detailed tximport + tx2gene workflow
- pathway-analysis/go-enrichment - Entrez IDs required
- pathway-analysis/kegg-pathways - Entrez IDs; strain-specific organism codes
- database-access/biomart-queries - General biomaRt patterns
- database-access/uniprot-access - UniProt mapping details
- database-access/ortholog-inference - De novo ortholog inference for custom genomes
<!-- END FILE: expression-matrix/gene-id-mapping/SKILL.md -->

## 子目录：expression-matrix/metadata-joins

<!-- BEGIN FILE: expression-matrix/metadata-joins/SKILL.md -->
---
name: bio-expression-matrix-metadata-joins
description: Aligns sample metadata with count matrices and constructs design matrices for downstream DE, handling the alphabetical-reference-level trap (relevel BEFORE DESeq), LRT reduced-model rules, the interaction-term resultsNames trap, continuous-covariate scaling and splines, repeated measures via duplicateCorrelation or dream, high-cardinality categorical pseudo-singular designs, sample swap detection via XIST/RPS4Y1 expression and somalier/NGSCheckMate genotypes, SABV (sex-as-biological-variable) mandate, Simpson's-paradox collapsing of technical replicates, and the `~ 0 + group` parameterization for clean contrasts. Use when building a design matrix, troubleshooting reversed fold-change direction, encoding paired or repeated-measures designs, detecting sample swaps, deciding sex-as-covariate, or aggregating technical replicates.
tool_type: mixed
primary_tool: pandas
---

## Version Compatibility

Reference examples tested with: pandas 2.2+, DESeq2 1.42+, edgeR 4.0+, limma 3.58+, variancePartition / dream 1.32+, somalier 0.2.18+ (CLI), pyensembl 2.3+, anndata 0.10+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metadata Joins

**"Align my sample metadata with my count matrix and build a design"** -> Reconcile sample identifiers, validate the join, set factor levels explicitly to control fold-change direction, encode the experimental structure (paired, repeated measures, interaction) in the design formula, and detect swaps before downstream DE.

## The Single Most Important Modern Insight -- Alphabetical reference levels invert fold changes silently

DESeq2 picks the reference level alphabetically if not told otherwise. With `condition = c('Treated', 'Untreated')`, `T < U`, so `Treated` becomes the reference. The reported `log2FoldChange` is then `Untreated vs Treated` -- **the opposite of what the methods section says**. No error; the volcano plot looks plausible; the gene list is correct but with reversed sign.

```r
dds$condition <- relevel(dds$condition, ref = 'Untreated')
coldata$condition <- factor(coldata$condition, levels = c('Untreated', 'Treated'))
```

Set BEFORE `DESeq()`; relevel-then-DESeq again to take effect.

A second insight: in interaction designs `~ genotype * treatment`, `results(dds, name='treatment_drug_vs_vehicle')` returns the drug effect IN THE WT REFERENCE only, not the marginal/average effect. The interaction coefficient `genotypeKO.treatmentdrug` is the DIFFERENCE in drug effect between KO and WT (the difference of differences), NOT the drug effect in KO. The cleanest fix is to use `~ 0 + group` with `group = paste(genotype, treatment, sep='_')` so every comparison of interest is a single contrast.

## Algorithmic Taxonomy

| Pattern | Encoding | Tests | Caveat |
|---------|----------|-------|--------|
| Simple two-group | `~ condition` | `results(name='condition_treated_vs_control')` | Set reference level explicitly |
| With known batch | `~ batch + condition` | `results(name='condition_...')` | Variable of interest LAST is the convention; not required |
| Paired (pre/post per subject) | `~ subject + condition` | `results(name='condition_...')` | Pairing FIRST; subject absorbs baseline variability |
| Repeated measures (>2 time per subject) | DREAM `~ condition + (1|subject)` | `topTable(coef='condition')` | Mixed model; uses voom + lmer |
| Interaction (2x2) | `~ A * B` (expands to A + B + A:B) | `results(name='A.B')` for diff-in-diff; combined factor for cleaner contrasts | resultsNames trap |
| Multi-group all pairwise | `~ 0 + group` + `makeContrasts` | Contrasts named directly | DESeq2 needs intercept; works for edgeR/limma |
| Multi-level "any change" | LRT `reduced = ~ 1` | `results(dds)` from LRT fit | padj is omnibus; LFC is one specific level |

## Decision Tree by Scenario

| Scenario | Recommended approach |
|----------|---------------------|
| Tumor / normal paired by patient | `~ patient + tissue`; pairing FIRST -- absorbs subject variability |
| Pre / post drug, same patient (2 time points) | `~ subject + condition` |
| Longitudinal, 4+ time points per subject | DREAM mixed model with `(1 \| subject)` random effect |
| Known batch (sequencing run, library prep date) | `~ batch + condition`; do NOT subtract |
| Many batches (>10 levels, n=20-40) | `~ condition + (1 \| batch)` via DREAM; or aggregate batches |
| Continuous covariate (age, RIN) | Center first; include linearly OR via `ns(x, df=3)` if non-linear |
| Mixed-sex cohort | Include sex unless sex-specific; report sex-stratified sensitivity |
| Multi-group, want pairwise contrasts | `~ 0 + group` + `makeContrasts` |
| Interaction question (does effect of A differ across B?) | Either `~ A * B` (handle resultsNames trap) or combined factor `~ 0 + group` |
| Many technical reps within bio reps | `duplicateCorrelation` (limma) OR aggregate via `collapseReplicates` (DESeq2) |
| Cohort >=20 samples | Run somalier or NGSCheckMate genotype check at the matrix-build step |

## Basic Join

**Goal:** Align count matrix columns with metadata rows; remove samples present in only one source; verify alignment before downstream use.

**Approach:** Intersect sample identifiers; reorder both data sources; assert match.

```python
import pandas as pd

counts = pd.read_csv('counts.tsv', sep='\t', index_col=0)
metadata = pd.read_csv('metadata.csv', index_col=0)

common = counts.columns.intersection(metadata.index)
only_counts = set(counts.columns) - set(metadata.index)
only_meta = set(metadata.index) - set(counts.columns)
if only_counts: print(f'In counts not metadata: {only_counts}')
if only_meta: print(f'In metadata not counts: {only_meta}')

counts = counts[common]
metadata = metadata.loc[common]
assert all(counts.columns == metadata.index)
```

```r
common <- intersect(colnames(counts), rownames(coldata))
counts <- counts[, common]
coldata <- coldata[common, , drop = FALSE]
stopifnot(all(colnames(counts) == rownames(coldata)))
```

When sample names differ by formatting (underscore vs dash, BAM suffix, case), try systematic transformations -- replace `_` <-> `-`, strip `.bam`, lower-case, take prefix before `_` -- before giving up.

## Reference Level (Critical -- Set Before DESeq)

**Goal:** Pick the baseline against which fold changes are reported, controlling sign direction.

**Approach:** `relevel()` or construct the factor with explicit `levels=`. Set BEFORE `DESeq()` runs.

```r
coldata$condition <- factor(coldata$condition, levels = c('control', 'treated'))

coldata$condition <- relevel(coldata$condition, ref = 'control')
```

```python
metadata['condition'] = pd.Categorical(metadata['condition'],
                                        categories=['control', 'treated'],
                                        ordered=True)
```

With factor levels explicit, the LFC reads `treated / control` -- treated up means LFC > 0.

A reminder for edgeR / limma users: `makeContrasts(Treated - Control)` is explicit and immune to the reference-level trap. Same caution applies less because the user names the contrast.

## Paired Designs

```r
design = ~ patient + tissue
```

Pairing variable FIRST (convention). Patient absorbs inter-subject baseline variability, dramatically increasing power for the tissue effect.

For DESeq2:
```r
dds <- DESeqDataSetFromMatrix(counts, coldata, design = ~ patient + tissue)
dds <- DESeq(dds)
res <- results(dds, name = 'tissue_tumor_vs_normal')
```

For edgeR:
```r
design <- model.matrix(~ patient + tissue, coldata)
y <- estimateDisp(y, design, robust = TRUE)
fit <- glmQLFit(y, design, robust = TRUE)
qlf <- glmQLFTest(fit, coef = 'tissuetumor')
```

Common mistake: writing `~ tissue + patient`. Numerically the model is the same; the convention of pairing-first improves readability and matches the natural mental model.

## Interaction Terms -- the resultsNames Trap

```r
design = ~ genotype + treatment + genotype:treatment
dds <- DESeqDataSetFromMatrix(counts, coldata, design = design)
dds <- DESeq(dds)
resultsNames(dds)
```

Output names (after relevel):
```
"Intercept"
"genotype_KO_vs_WT"
"treatment_drug_vs_vehicle"
"genotypeKO.treatmentdrug"
```

| Question | Wrong answer | Right answer |
|----------|--------------|--------------|
| Drug effect averaged over genotypes | `results(name='treatment_drug_vs_vehicle')` -- this is drug effect in WT only | Combined factor `~ 0 + group`; or contrast that explicitly averages |
| Is drug effect different between genotypes? | n/a | `results(name='genotypeKO.treatmentdrug')` -- the interaction coefficient IS the difference of differences |
| Drug effect in KO | `results(name='treatment_drug_vs_vehicle')` -- WRONG, this is drug in WT | `results(contrast=list(c('treatment_drug_vs_vehicle', 'genotypeKO.treatmentdrug')))` (sum of main + interaction) |

The cleaner alternative for designs with many contrasts of interest:

```r
coldata$group <- factor(paste(coldata$genotype, coldata$treatment, sep = '_'))
dds <- DESeqDataSetFromMatrix(counts, coldata, design = ~ 0 + group)
dds <- DESeq(dds)

res_drug_in_ko <- results(dds, contrast = c('group', 'KO_drug', 'KO_vehicle'))
res_drug_in_wt <- results(dds, contrast = c('group', 'WT_drug', 'WT_vehicle'))
res_diff       <- results(dds, contrast = list(c('groupKO_drug', 'groupWT_vehicle'),
                                                c('groupKO_vehicle', 'groupWT_drug')))
```

`~ 0 + group` parameterization is the long-standing edgeR / limma recommendation (Smyth and Robinson User's Guides) for any design with multiple pairwise contrasts of interest.

## LRT and the Reduced Model

```r
dds <- DESeq(dds, test = 'LRT', reduced = ~ batch)
```

Reduced model drops the term being tested. With `design = ~ batch + condition` and `reduced = ~ batch`, the LRT tests condition. With interaction designs:

```r
dds <- DESeq(dds, test = 'LRT', reduced = ~ genotype + treatment)
```

(Tests the interaction.)

The reduced model must be NESTED in the full model (every term in reduced must appear in full).

## Continuous Covariates

| Encoding | Assumption | When |
|----------|------------|------|
| Linear (`+ age`) | log-expression linear in age | Limited range, biologically linear |
| Centered linear (`+ I(age - mean(age))`) | As linear, interpretable intercept | Standard for age-RIN-day covariates |
| Natural spline (`+ ns(age, df=3)`) | Smooth nonlinear | Wide age range with non-monotonic effects |
| Polynomial (`+ poly(age, 2)`) | Quadratic; orthogonal polynomials | Limited use; splines usually better |

```r
coldata$age_c <- coldata$age - mean(coldata$age)
design = ~ age_c + RIN + condition

library(splines)
design = ~ ns(age, df = 3) + condition
```

DO NOT include library size as a covariate -- it is handled by size factors / normalization factors internally.

## Repeated Measures -- duplicateCorrelation vs dream

**Goal:** Correctly model within-subject correlation when the same subject contributes multiple samples.

**Approach:** For technical reps within bio reps OR paired pre/post: `duplicateCorrelation` (limma) is adequate. For >2 time points per subject or random slopes: DREAM (`variancePartition`).

```r
library(limma)
library(edgeR)

v <- voom(y, design)
corfit <- duplicateCorrelation(v, design, block = coldata$donor)
v <- voom(y, design, block = coldata$donor, correlation = corfit$consensus)
corfit <- duplicateCorrelation(v, design, block = coldata$donor)
fit <- lmFit(v, design, block = coldata$donor, correlation = corfit$consensus)
fit <- eBayes(fit, robust = TRUE)
```

The double pass is intentional: estimate correlation, re-voom with correlation, re-estimate, fit. Limma's `duplicateCorrelation` assumes ONE within-subject correlation across all genes -- approximation.

For proper per-gene mixed models:

```r
library(variancePartition)

form <- ~ condition + (1 | donor)
vobj <- voomWithDreamWeights(y, form, coldata)
fitmm <- dream(vobj, form, coldata)
fitmm <- eBayes(fitmm)
tt <- topTable(fitmm, coef = 'condition')
```

See `differential-expression/timeseries-de` for full longitudinal designs.

Before committing to a design, `variancePartition::fitExtractVarPartModel(vobj, form, coldata)` quantifies the fraction of expression variance explained by each covariate, gene-by-gene. If a candidate "nuisance" covariate explains <1% of variance across most genes, it can usually be dropped; if a known biological factor explains <5% and isn't of direct interest, model it as a random effect rather than fixed.

## Sample Swap Detection (Mandatory for Cohort >= 20)

### Sex check via XIST and chrY expression

**Goal:** Detect mislabeled samples by checking that gene-expression sex matches reported sex.

**Approach:** Compare XIST expression (high in XX, low/absent in XY) against chrY-gene expression (DDX3Y, RPS4Y1, UTY, KDM5D, EIF1AY -- high in XY, absent in XX).

```python
import pandas as pd

def sex_check(counts, metadata, sex_column='sex'):
    y_genes = ['DDX3Y', 'RPS4Y1', 'UTY', 'KDM5D', 'EIF1AY']
    y_avail = [g for g in y_genes if g in counts.index]
    if 'XIST' not in counts.index or not y_avail:
        return None
    predicted = pd.Series('unknown', index=counts.columns)
    predicted[counts.loc[y_avail].sum() > counts.loc['XIST']] = 'M'
    predicted[counts.loc['XIST'] > counts.loc[y_avail].sum()] = 'F'
    if sex_column in metadata.columns:
        mis = predicted != metadata[sex_column]
        if mis.any():
            print(f'SEX MISMATCHES: {list(metadata.index[mis])}')
    return predicted
```

```r
sex_check <- function(counts, coldata, sex_col = 'sex') {
    y_genes <- c('DDX3Y', 'RPS4Y1', 'UTY', 'KDM5D', 'EIF1AY')
    y_expr <- colSums(counts[intersect(y_genes, rownames(counts)), , drop = FALSE])
    predicted <- ifelse(y_expr > counts['XIST', ], 'M', 'F')
    mis <- predicted != coldata[[sex_col]]
    if (any(mis)) cat('Sex mismatches:', colnames(counts)[mis], '\n')
    predicted
}
```

CAVEAT: tumors with X loss, sex chromosome aneuploidies, HeLa (XXX with mixed inactivation) muddy this. Genotype-based methods are more robust.

### Genotype-based: somalier and NGSCheckMate

```bash
somalier extract -d extracted/ --sites sites.GRCh38.vcf.gz \
    -f reference.fa sample.bam
somalier relate --infer extracted/*.somalier
```

```bash
ncm_fastq.py -l fastq_list.txt -O outdir -bed common_sites.bed
```

Somalier (Pedersen et al. 2020 *Genome Med* 12:62) extracts a few thousand SNP sketches per sample (sub-second per sample) and computes pairwise relatedness from BAM/CRAM/VCF. NGSCheckMate (Lee et al. 2017 *NAR* 45:e103) computes VAF correlation across a common-SNP panel; works on FASTQ/BAM/VCF including RNA-seq.

For any cohort >=20 samples, run one of these at the matrix-build step. Catching a swap in raw data is cheap; finding it after DE is expensive.

## SABV -- Sex as Biological Variable

NIH 2016+ requires sex consideration in vertebrate animal and human studies. Mauvais-Jarvis F et al. 2020 *Lancet* 396:565 reviews effect-size differences across diseases.

Practical implication:
- Always include sex in the metadata, even when not in the model.
- For sex-balanced cohorts, `~ sex + condition` rarely hurts and captures real biology.
- For sex-confounded cohorts (all-male disease cohort vs mixed-sex control), can't rescue but documents the limitation.
- For chrX/chrY analyses, sex MUST be in the model OR the analysis is uninterpretable.
- Report DE counts overall AND sex-stratified.

## Simpson's Paradox -- Collapsing Technical Replicates

**Goal:** Aggregate technical replicates from the same subject correctly; never treat them as independent biological replicates.

**Approach:** Sum (not average) technical replicates of the same subject BEFORE downstream DE.

```r
library(DESeq2)
dds_collapsed <- collapseReplicates(dds, groupby = dds$subject)
```

```python
counts_per_subject = counts.T.groupby(metadata['subject']).sum().T
metadata_per_subject = metadata.drop_duplicates(subset='subject').set_index('subject')
```

Why sum and not average? Reads add. Two technical replicates yielding 1M reads each are equivalent to one library yielding 2M reads. Averaging would understate the effective library size.

Treating technical replicates as independent biological samples is the cardinal sin: it inflates the apparent sample size and deflates standard errors. With 4 patients x 3 tech reps = 12 samples, naive DE assumes 12 independent observations; the truth is closer to 4. p-values are compressed ~3x.

## High-Cardinality Categorical Covariates

**Goal:** Handle batch / lane / well covariates with many levels without making the design matrix singular.

**Approach:** Aggregate to fewer levels, model as random effect via DREAM, or drop if confounded.

```r
ct <- table(coldata$condition, coldata$batch)
ct

ad <- alias(model.matrix(~ batch + condition, coldata))
ad$Complete
```

For a batch with 30 levels in n=40 samples: 30 batch coefficients + condition + intercept = 32 parameters for 40 observations. Symptoms: `Matrix not positive definite` (DESeq2), degenerate p-values (limma).

Fixes:
- Aggregate batches (sequencing run, sequencing pool, library prep date as proxy).
- Random effect: `~ condition + (1 | batch)` via DREAM borrows information across batch levels via shrinkage.
- Drop the covariate if confounded with condition (`alias()` reveals collinearity).

## ~ 0 + group Parameterization

```r
design_default <- model.matrix(~ group, coldata)
# columns: (Intercept), groupB, groupC  -- A is reference

design_nointercept <- model.matrix(~ 0 + group, coldata)
# columns: groupA, groupB, groupC  -- each column is mean of that group
```

With `~ 0 + group`, every contrast reads as `B - A`:

```r
library(limma)

con <- makeContrasts(BvsA = groupB - groupA,
                     CvsA = groupC - groupA,
                     BvsC = groupB - groupC,
                     levels = design_nointercept)
fit <- glmQLFit(y, design_nointercept, robust = TRUE)
qlf <- glmQLFTest(fit, contrast = con[, 'BvsA'])
```

DESeq2 needs an intercept internally, so `~ 0 + group` works directly with edgeR/limma but DESeq2 uses `contrast=` to achieve the same effect.

## Create DESeq2 / edgeR / AnnData Containers

```r
dds <- DESeqDataSetFromMatrix(as.matrix(counts), coldata, design = ~ batch + condition)

y <- DGEList(counts = as.matrix(counts), group = coldata$condition)
y$samples <- cbind(y$samples, coldata)

adata <- ad.AnnData(X = t(as.matrix(counts)), obs = coldata, var = data.frame(row.names = rownames(counts)))
```

AnnData convention is cells (samples) in rows -- transpose from the typical R genes-in-rows convention.

## Per-Method Failure Modes

### Fold-change direction reversed

**Trigger:** Methods says "treated vs control"; published volcano shows expected up-genes on the LEFT.

**Mechanism:** Factor levels left at alphabetical default; `c('Treated','Untreated')` -> `T < U` -> Treated is reference -> LFC is Untreated/Treated.

**Symptom:** Known up-regulated genes appear down; reviewer questions direction.

**Fix:** `relevel(coldata$condition, ref = 'Untreated')` BEFORE `DESeq()`. Re-run.

### Interaction coefficient mistaken for main effect

**Trigger:** `~ A * B` design; `results(name='B_drug_vs_vehicle')` reported as "drug effect"; reviewer asks about genotype-specific effect.

**Mechanism:** With interaction, `B_drug_vs_vehicle` is drug effect IN THE A REFERENCE LEVEL only, not averaged across A.

**Symptom:** Drug effect doesn't match the marginal estimate from a separate `~ B`-only fit.

**Fix:** Use `~ 0 + group` with combined factor; OR extract per-stratum results explicitly using contrasts that sum main + interaction.

### Pseudoreplication -- 12 samples, only 3 subjects

**Trigger:** 3 subjects x 4 conditions = 12 samples; vanilla DESeq2 with `~ condition`; many DE genes.

**Mechanism:** Same subject contributes multiple observations; not independent. Effective sample size for testing condition is ~3, not 12.

**Symptom:** p-value histogram anti-conservative; replication low.

**Fix:** Include subject in design (`~ subject + condition`) OR use DREAM with random subject.

### Sample swap caught in DE results, not metadata

**Trigger:** PCA shows "control" sample clustering with treated; investigation reveals it was mislabeled at thaw.

**Mechanism:** Manual sample tracking is error-prone; cohort >=20 inevitably has swaps.

**Symptom:** One sample dramatically off its group cluster; DE gene list dominated by sample-specific effects.

**Fix:** Run somalier or NGSCheckMate at the matrix-build step, BEFORE DE. Catching a swap early is cheap; finding it post-DE is expensive.

### Sex confounded, chrY genes dominate top hits

**Trigger:** Mixed-sex cohort; sex not in design; PCA shows clear sex split on PC1.

**Mechanism:** Sex distribution differs between groups; "treatment effect" partially captures sex.

**Symptom:** Top DE genes are DDX3Y, RPS4Y1, UTY (chrY) and XIST -- not biology of interest.

**Fix:** Add sex to design (`~ sex + condition`). For sex-specific analyses, stratify and report each separately.

### duplicateCorrelation single-pass

**Trigger:** limma user wrote a one-pass `duplicateCorrelation` + lmFit; QC reviewer asks why no re-voom.

**Mechanism:** The proper pattern is: voom -> dupCor -> re-voom WITH correlation -> dupCor again -> lmFit. The first voom doesn't know about block structure; re-voom with correlation gets better weights.

**Symptom:** Slightly inflated DE counts vs the two-pass pattern.

**Fix:** Implement the two-pass pattern per the limma User's Guide (section 9.7).

## Common errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| Sample names don't match between counts and metadata | Underscore/dash inconsistency, BAM suffix, case | `fuzzy_match_samples()` or manual normalization; report what failed |
| DESeq2 design not full rank | Confounded covariates | `alias(design)$Complete` to identify; aggregate or drop |
| `Matrix not positive definite` | High-cardinality batch with few samples | Aggregate batches or use random effect via DREAM |
| LFC direction reversed | Alphabetical reference level | `relevel()` before `DESeq()` |
| `results(name='...')` returns drug effect in WT only | Interaction design and naming trap | Use combined factor `~ 0 + group`; or contrast summing main + interaction |
| Inflated DE list with 12 samples from 3 subjects | Pseudoreplication | Include subject; or use DREAM |
| Sex effect appears as treatment effect | Sex not in design | Add `~ sex + condition` |
| Sample distance heatmap shows mixing groups | Likely swap | Run somalier or NGSCheckMate |

## References

- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biol* 15(12):550. doi:10.1186/s13059-014-0550-8
- Robinson MD, McCarthy DJ, Smyth GK. 2010. edgeR: a Bioconductor package for differential expression analysis of digital gene expression data. *Bioinformatics* 26(1):139-140. doi:10.1093/bioinformatics/btp616
- Ritchie ME et al. 2015. limma powers differential expression analyses for RNA-sequencing and microarray studies. *Nucleic Acids Res* 43(7):e47. doi:10.1093/nar/gkv007
- Smyth GK, Michaud J, Scott HS. 2005. Use of within-array replicate spots for assessing differential expression in microarray experiments. *Bioinformatics* 21(9):2067-2075. doi:10.1093/bioinformatics/bti270
- Hoffman GE, Roussos P. 2021. dream: powerful differential expression analysis for repeated measures designs. *Bioinformatics* 37(2):192-201. doi:10.1093/bioinformatics/btaa687
- Hoffman GE, Schadt EE. 2016. variancePartition: interpreting drivers of variation in complex gene expression studies. *BMC Bioinformatics* 17:483. doi:10.1186/s12859-016-1323-z
- Pedersen BS, Bhetariya PJ, Brown J, Kravitz SN, Marth GT, Jensen RL, Bronner MP, Underhill HR, Quinlan AR. 2020. Somalier: rapid relatedness estimation for cancer and germline studies using efficient genome sketches. *Genome Medicine* 12:62. doi:10.1186/s13073-020-00761-2
- Lee S, Lee S, Ouellette S, Park W-Y, Lee EA, Park PJ. 2017. NGSCheckMate: software for validating sample identity in next-generation sequencing studies within and across data types. *Nucleic Acids Res* 45(11):e103. doi:10.1093/nar/gkx193
- Mauvais-Jarvis F, Bairey Merz N, Barnes PJ et al. 2020. Sex and gender: modifiers of health, disease, and medicine. *Lancet* 396(10250):565-582. doi:10.1016/S0140-6736(20)31561-0

## Related Skills

- counts-ingest - Building count matrices before metadata join
- gene-id-mapping - Annotating result tables with symbols
- normalization - Reference for downstream normalization choice
- sparse-handling - AnnData obs metadata convention
- differential-expression/deseq2-basics - Where the design formula matters; relevel; interactions
- differential-expression/edger-basics - edgeR design matrix conventions
- differential-expression/batch-correction - Design-inclusion vs subtraction; confounding
- differential-expression/timeseries-de - Repeated measures; DREAM mixed model details
- single-cell/preprocessing - scRNA-seq sample metadata handling
<!-- END FILE: expression-matrix/metadata-joins/SKILL.md -->

## 子目录：expression-matrix/normalization

<!-- BEGIN FILE: expression-matrix/normalization/SKILL.md -->
---
name: bio-expression-matrix-normalization
description: Normalizes and transforms RNA-seq count matrices for DE, visualization, clustering, and ML. Covers between-sample (TMM, TMMwsp, RLE/median-of-ratios, upper quartile), within-sample (TPM, FPKM/RPKM), variance-stabilizing (VST, rlog, log-CPM), GC-content correction (cqn, EDASeq), and single-cell (scran deconvolution, scanpy normalize_total). Encodes the composition-bias rationale, the "most genes not DE" assumption and its catastrophic failure modes (MYC amplification, apoptosis, viral host shutoff, prokaryotic stress), the "lengthScaledTPM is not TPM" naming trap, the "TPM is not for DE" rule, the blind=TRUE vs FALSE decision, ERCC spike-in normalization (SBN), and the single-cell zero-inflation breakdown of TMM/RLE. Use when choosing or applying normalization, debugging shifted-MA-plot diagnostics, handling zero-heavy single-cell data, or correcting GC bias.
tool_type: mixed
primary_tool: DESeq2
---

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, edgeR 4.0+, limma 3.58+, pandas 2.2+, numpy 1.26+, scanpy 1.10+, scran 1.30+, scater 1.30+, EDASeq 2.36+, cqn 1.48+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Expression Matrix Normalization

**"Normalize my counts for X"** -> Pick a method that matches the downstream task (raw counts for DE; TMM/RLE-scaled CPM for cross-sample comparison; VST/rlog for visualization/ML; scran for single-cell) and the data structure (bulk vs single-cell, zero-heavy or not, length-biased or not).

## The Single Most Important Modern Insight -- TMM/RLE assume most genes are NOT DE; that assumption is wrong in MYC, apoptosis, viral host shutoff, and prokaryotic stress

TMM (Robinson & Oshlack 2010 *Genome Biol* 11:R25) and RLE/median-of-ratios (Anders & Huber 2010 *Genome Biol* 11:R106) both rely on the assumption that the MAJORITY of genes are unchanged between samples. The scaling factor is computed from a trimmed reference. When that assumption holds (most bulk RNA-seq), both methods are excellent.

When the assumption fails catastrophically:

| Biology | Mechanism | Symptom |
|---------|-----------|---------|
| MYC amplification | MYC drives global 2-3x transcriptional amplification | Scaling factors absorb the global shift; reported LFCs muted |
| Apoptosis / cell death | Massive transcriptional shutdown | Surviving (often mitochondrial) transcripts appear up-regulated |
| Viral host shutoff (HSV-1, vaccinia) | Host mRNA degraded by viral nucleases | Apparent up-regulation of non-degraded host genes |
| Transcription / splicing inhibitors (DRB, flavopiridol) | Pol II elongation blocked | Similar global shutdown signature |
| Cell-cycle synchronization | G1 vs S vs M differ in total RNA per cell | Per-cell RNA shifts; library-size-only normalization mis-corrects |
| Prokaryotic stress | Bacteria rewire large fractions of transcriptome | >50% of genes truly DE; trimmed mean is no longer "background" |

Detection: MA plot shows the bulk cloud clearly shifted off zero; reported fold changes don't match qPCR or Western for known-DE genes.

Fix: ERCC spike-in normalization (Jiang 2011 *Genome Res* 21:1543) -- 96 synthetic RNAs spiked proportional to cell number; use spike-in counts as the size factor. Or: `controlGenes=` with a curated stable housekeeping set. The "most genes not DE" assumption is checkable; check it on every dataset that might violate it.

A second insight: **`lengthScaledTPM` from tximport is NOT TPM**. It is a count-scale matrix (sums to library size) with length-bias removed, designed as input to limma-voom (which cannot accept offsets). The "TPM" in the option name has misled many users into reporting these values as normalized abundance. See `expression-matrix/counts-ingest` for the full `countsFromAbundance` decision tree.

A third insight: **VST/rlog values are NEVER input to DE**. They are for PCA, heatmaps, clustering, ML features. DE tools model the count distribution directly; passing VST/rlog values silently violates their assumptions.

## Normalization Decision Table

| Task | Method | Tool | Input |
|------|--------|------|-------|
| DE testing (DESeq2) | RLE / median-of-ratios | `DESeq()` internally | Raw integer counts |
| DE testing (edgeR) | TMM / TMMwsp | `normLibSizes()` internally | Raw integer counts |
| DE testing (limma-voom) | TMM + voom precision weights | `normLibSizes()` then `voom()` | Raw integer counts |
| PCA, heatmaps, clustering (n > 30) | VST | `vst(dds, blind = FALSE)` | DESeqDataSet |
| PCA, heatmaps, clustering (n < 30, library sizes vary >4x) | rlog | `rlog(dds, blind = FALSE)` | DESeqDataSet |
| PCA, heatmaps (edgeR/limma) | log-CPM | `cpm(y, log=TRUE, prior.count=2)` | DGEList |
| WGCNA | VST or log-CPM | `vst(blind=FALSE)` | DESeqDataSet |
| GSVA / ssGSEA | log2(TPM+1) or VST | precomputed | TPM or DESeqDataSet |
| ML biomarker model | VST | `vst(blind=FALSE)` | DESeqDataSet |
| Cross-sample expression reporting | DESeq2 normalized counts | `counts(dds, normalized=TRUE)` | DESeqDataSet |
| Within-sample gene ranking | TPM | quantification tool output | -- |
| Single-cell normalization | scran deconvolution | `computeSumFactors` + `logNormCounts` | SingleCellExperiment |
| Single-cell, simple/exploratory | log1p(CPM-like) | `sc.pp.normalize_total + sc.pp.log1p` | AnnData |
| Cross-sample but composition-shifted (majority-DE biology) | Spike-in (ERCC) or `controlGenes=` | DESeq2/edgeR with offset | Raw counts + controls |
| GC-content bias (cross-platform integration) | cqn or EDASeq | `cqn()` returns offset | Counts + per-gene GC + length |

## Between-Sample Normalization

### RLE / Median of Ratios (DESeq2)

**Goal:** Estimate per-sample size factors that correct for library size and composition bias.

**Approach:** Geometric mean per gene across samples forms a pseudo-reference; per-sample size factor is the median ratio of (sample count / reference count). Median is robust to a minority of DE genes.

```r
library(DESeq2)

dds <- DESeqDataSetFromMatrix(counts, coldata, design = ~ condition)
dds <- estimateSizeFactors(dds)
sizeFactors(dds)

norm_counts <- counts(dds, normalized = TRUE)
```

Size factor interpretation: 1.2 means the sample has 20% more sequencing depth (after composition adjustment) than the reference.

The geometric mean is undefined for any gene with a zero in any sample, so RLE `type='ratio'` (default) silently EXCLUDES genes with any zero from the reference. For single-cell or zero-heavy data, use:

```r
dds <- estimateSizeFactors(dds, type = 'poscounts')
```

`poscounts` uses only positive entries per gene, salvaging the geometric mean.

| Scenario | Use |
|----------|-----|
| Standard bulk RNA-seq | Default `type='ratio'` |
| Zero-heavy (single-cell, sparse) | `type='poscounts'` |
| Very small libraries | `type='iterate'` |
| Known stable reference genes | `controlGenes=stable_idx` |
| Majority-DE biology (stress, MYC, viral) | `controlGenes=` or spike-in SBN |

### TMM / TMMwsp (edgeR)

**Goal:** Compute normalization factors that account for composition bias via trimmed mean of M-values.

**Approach:** Select reference; compute gene-wise log-ratios (M-values) and average expression (A-values); trim extremes; weighted mean scaling factor.

```r
library(edgeR)

y <- DGEList(counts = counts, group = coldata$condition)
y <- normLibSizes(y)
y$samples$norm.factors
```

`normLibSizes()` is the v4 canonical name (was `calcNormFactors()` in v3; same function). `method='TMM'` remains the documented default; `method='TMMwsp'` (TMM with singleton pairing) is an alternative for samples with many zeros and is the preferred choice for sparse / single-cell-pseudobulk data. Pass `method=` explicitly for reproducibility. Both old name and method still work.

TMM defaults: `logratioTrim = 0.3` (trim top 30% and bottom 30% of M values), `sumTrim = 0.05`. The factor enters the GLM as part of the offset; counts are NOT divided.

For visualization:

```r
log_cpm <- cpm(y, log = TRUE, prior.count = 2)
cpm_vis <- cpm(y, normalized.lib.sizes = TRUE)
```

`prior.count = 2` is the modern edgeR default for `log=TRUE`. Smaller priors (0.25) leave low-count log values noisy; larger priors (5-10) shrink them further toward zero. limma-trend assumes the log-CPM uses cpm log=TRUE.

### Upper Quartile

```r
y <- normLibSizes(y, method = 'upperquartile')
```

Per-sample 75th percentile of non-zero counts (Bullard et al. 2010 *BMC Bioinformatics* 11:94). Robust to the "most genes unchanged" assumption -- useful when TMM/RLE fail. Less common in modern practice; usable for microRNA-seq or targeted panels where TMM doesn't have enough genes to trim.

### Spike-In Normalization (ERCC)

```r
ercc_idx <- grep('^ERCC-', rownames(counts))
y <- DGEList(counts = counts[-ercc_idx, ], group = coldata$condition)
ercc_lib <- colSums(counts[ercc_idx, ])
y$samples$norm.factors <- ercc_lib / mean(ercc_lib)
```

Spike-in based normalization (SBN) uses ERCC counts as the per-sample size factor proxy, decoupling normalization from endogenous transcript composition. Required for MYC, viral, or other majority-DE biology. Caveat: spike-ins have technical variance; the spike-in:endogenous ratio depends on input cell number being accurately measured (often violated).

## Within-Sample Normalization (TPM, FPKM)

| Unit | Definition | Within-sample comparable | Between-sample comparable | Use for DE |
|------|------------|-------------------------|--------------------------|------------|
| Raw counts | reads per gene | No | No | YES (via DE tools) |
| CPM | reads / library_size * 1e6 | No (no length correction) | Only with TMM/RLE factors | No |
| RPKM/FPKM (Mortazavi 2008) | reads / (length_kb * lib_size_in_M) | Yes | No (composition bias) | No |
| TPM (Wagner 2012) | (reads/length) / sum(reads/length) * 1e6 | Yes | Partially (same composition caveat) | No |
| Normalized counts | DESeq2 / edgeR scaled | No | Yes | Via DE tool |
| VST/rlog | DESeq2 stabilized | No | Yes | NO (visualization only) |

```python
import pandas as pd

def counts_to_tpm(counts, gene_lengths):
    '''Convert raw counts to TPM. gene_lengths in bp.'''
    rate = counts.div(gene_lengths / 1000, axis=0)
    tpm = rate.div(rate.sum(axis=0), axis=1) * 1e6
    return tpm
```

```r
counts_to_tpm <- function(counts, gene_lengths) {
    rate <- counts / (gene_lengths / 1000)
    t(t(rate) / colSums(rate)) * 1e6
}
```

TPM's sum-to-1e6-per-sample makes cross-sample comparisons dimensionally coherent but does NOT fix composition shifts -- TPM remains a COMPOSITIONAL value. Under massive global changes, TPM destroys the absolute-scale signal.

Wagner GP, Kin K, Lynch VJ 2012 *Theory Biosci* 131:281 is the canonical "why TPM > RPKM" reference. Their headline: "average FPKM varies between samples even for the same genome."

CRITICAL: do NOT use TPM as input to DESeq2 / edgeR / limma-voom. They model the count distribution directly. TPM is for: within-sample ranking, gene-set comparison within sample, deconvolution (CIBERSORT, EPIC, MCP-counter all require TPM), and reporting expression levels.

## Variance-Stabilizing Transformations (VST, rlog)

**Goal:** Transform counts so variance is approximately constant across the mean, suitable for PCA, heatmaps, clustering, ML features.

**Approach:** Fit dispersion-mean trend and apply variance-stabilizing function.

```r
library(DESeq2)

vsd <- vst(dds, blind = FALSE)
rld <- rlog(dds, blind = FALSE)

vst_matrix <- assay(vsd)
```

| Criterion | VST | rlog |
|-----------|-----|------|
| Speed | Fast (1 sec for thousands of samples) | Slow (30+ sec for 100 samples) |
| n > 30 | Recommended | Impractical |
| Unequal library sizes (>4x) | Adequate | Better (more shrinkage) |
| Low-count genes | May be noisy | Better shrinkage |
| Default choice | YES | Only when n<30 AND lib sizes vary >4x |

`blind=TRUE` (vst default) re-estimates dispersions IGNORING the design -- appropriate for unbiased QC ("are samples consistent independent of design?"). `blind=FALSE` uses fitted dispersions -- appropriate for downstream visualization after the design is settled. Modern DESeq2 vignette recommends `blind=FALSE` for any plot AFTER the model is fit.

`vst()` uses 1000 most-variable genes by default to fit the dispersion trend. With <1000 genes after filtering, set `nsub` lower.

CRITICAL: VST/rlog values are for visualization only. NEVER pass them to `DESeq()` or `glmQLFit()`. DE tools require raw counts.

### log-CPM (edgeR / limma)

```r
log_cpm <- cpm(y, log = TRUE, prior.count = 2)
```

```python
import numpy as np
def log_cpm(counts, prior_count=2):
    lib_sizes = counts.sum(axis=0)
    cpm_vals = (counts + prior_count) / (lib_sizes + 2 * prior_count) * 1e6
    return np.log2(cpm_vals)
```

`prior.count = 2` (edgeR modern default) shrinks low-count log values toward zero, reducing visual artifacts from low-expression noise. For statistical use (limma-trend), this default is appropriate; for heatmaps and PCA, larger priors (3-5) further dampen noise.

voom uses 0.5 added per cell with `(lib.size + 1)` denominator -- not strictly equivalent to `cpm(log=TRUE, prior.count=0.5)`. Its mean-variance trend handles low-count noise via per-observation weights. Do not confuse voom's internal pre-log handling with `cpm(log=TRUE)`.

## GC Content and Length Bias (cqn, EDASeq)

Standard TMM/RLE do NOT correct sample-specific GC content bias or gene length bias. These biases arise from library preparation (fragmentation, PCR) and create systematic differences in read coverage correlated with gene properties.

Most affected: GSEA. Sample-specific gene-length bias causes recurrent false positives.

EDASeq (Risso, Schwartz, Sherlock, Dudoit 2011 *BMC Bioinformatics* 12:480) applies within-lane GC normalization then between-lane normalization:

```r
library(EDASeq)

fd <- data.frame(gc = gene_gc, length = gene_lengths, row.names = rownames(counts))
data <- newSeqExpressionSet(as.matrix(counts), featureData = fd, phenoData = coldata)

data_norm <- withinLaneNormalization(data, 'gc', which = 'full')
data_norm <- betweenLaneNormalization(data_norm, which = 'full')
normalized_counts <- counts(data_norm)
```

cqn (Hansen, Irizarry, Wu 2012 *Biostatistics* 13:204) fits a smooth conditional-quantile model on log2 expression as a function of GC and length; the offset enters the GLM directly:

```r
library(cqn)
cqn_res <- cqn(counts, x = gene_gc, lengths = gene_lengths)
y$offset <- cqn_res$glm.offset
```

Use when comparing samples sequenced on different platforms or with different library prep chemistries. Run BEFORE TMM/RLE (or supply the cqn offset to edgeR/DESeq2 directly).

## Single-Cell Normalization

### scran Deconvolution

**Goal:** Per-cell size factors that handle the high zero-inflation of single-cell data without violating TMM/RLE assumptions.

**Approach:** Pool cells in overlapping windows; compute pool-level size factors; deconvolve back to individual cells. Pre-cluster to avoid mixing cell types with very different transcriptome sizes.

```r
library(scran)
library(scater)

clusters <- quickCluster(sce)
sce <- computeSumFactors(sce, clusters = clusters)
sce <- logNormCounts(sce)
```

`quickCluster` provides a rough partition; without it, mixing a cell with 200 detected genes (resting T cell) and 5000 detected genes (activated macrophage) produces wrong size factors.

### scanpy normalize_total

```python
import scanpy as sc

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
```

Simpler than scran (CPM-like with target_sum=1e4) but less robust to composition bias. Adequate for exploratory analysis; for rigorous DE (especially pseudobulk), use scran-style or aggregate to bulk and use DESeq2.

Standard bulk TMM/RLE FAIL on single-cell data because many genes have zero counts due to dropout, violating "most genes detected in most samples." Use scran or `poscounts`.

## Pre-Filtering Before Normalization

```r
library(edgeR)
keep <- filterByExpr(y, design = model.matrix(~ condition, coldata))
y <- y[keep, , keep.lib.sizes = FALSE]
```

`filterByExpr` is design-aware: requires CPM above threshold in at least n samples, where n is the smallest group size from the design. See `differential-expression/edger-basics` for internals.

DESeq2 performs automatic independent filtering at `results()` time. Manual pre-filtering for DESeq2 is for SPEED only -- it does not affect statistical results.

```r
keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep, ]
```

Key distinction: edgeR REQUIRES explicit `filterByExpr` (no automatic independent filtering); DESeq2 does both. Forgetting `filterByExpr` in edgeR inflates the multiple-testing burden -- the single biggest reason an edgeR analysis underperforms a comparable DESeq2 analysis.

## Per-Method Failure Modes

### TMM/RLE fail under MYC amplification

**Trigger:** Cancer vs normal with MYC amplification; MA plot shows the bulk cloud clearly above zero; reported fold changes 30-50% smaller than qPCR or Western.

**Mechanism:** MYC drives global ~2x mRNA increase. TMM/RLE assume most genes unchanged -- the assumption is wrong; trimmed reference is dominated by genuinely up-regulated genes; size factors absorb the global shift.

**Symptom:** Known up-regulated genes show muted LFC; spike-in or qPCR shows the real magnitude.

**Fix:** Use ERCC spike-ins for SBN; or supply curated stable housekeeping genes via `controlGenes=` or as `y$offset`.

### Used VST/rlog values as DE input

**Trigger:** PCA looked good on VST; user passed VST matrix to limma `lmFit`; many DE genes.

**Mechanism:** DE tools require raw counts. VST/rlog values are log-scale and homoskedastic by design -- the count-distribution assumptions are violated.

**Symptom:** P-value histogram non-uniform; gene lists don't replicate.

**Fix:** Always use raw counts as input to DE tools. VST/rlog is for visualization, clustering, ML -- not testing.

### Single-cell with TMM -- zero-inflation breaks it

**Trigger:** scRNA-seq data passed through `normLibSizes(y, method='TMM')`; many cells have NA size factors or extreme values.

**Mechanism:** TMM trims top and bottom 30% of M-values. With many zeros, the M-value distribution is dominated by undefined values.

**Symptom:** Size factor estimation fails or produces extreme outliers.

**Fix:** scran deconvolution (with `quickCluster` pre-clustering). For DESeq2 on pseudobulk, `type='poscounts'`.

### TPM used for DE

**Trigger:** Pipeline computed TPM in Python; user wrote `DESeqDataSetFromMatrix(round(tpm), coldata, ...)`.

**Mechanism:** TPM is compositional within sample; cross-sample comparisons are fractions, not abundances. DESeq2 models the count distribution; rounded TPM is neither raw counts nor a meaningful transformation.

**Symptom:** Bizarre dispersion estimates; DE list dominated by housekeeping shifts.

**Fix:** Always use raw counts as input. For Salmon/kallisto output, use tximport.

### blind=TRUE for downstream visualization

**Trigger:** `vst(dds, blind = TRUE)` for the results-figure PCA; clusters look weaker than expected.

**Mechanism:** `blind=TRUE` ignores the design when fitting dispersions, treating biological signal as noise -- appropriate for QC, suboptimal for results figures.

**Symptom:** PCA shows less separation than `blind=FALSE` would.

**Fix:** Use `blind=FALSE` for downstream visualization AFTER the design is settled.

### Quantile normalization across RNA-seq samples with global shift

**Trigger:** Multi-platform integration; user applied quantile normalization to harmonize; downstream DE shows fewer hits than expected.

**Mechanism:** Quantile normalization forces every sample's distribution to be identical by rank-replacing. Assumes the true expression distribution is the same across samples (valid for microarrays with bounded dynamic range; often false for RNA-seq with global shifts).

**Symptom:** Real biological signal erased; especially harmful when biological condition truly shifts the distribution.

**Fix:** TMM/RLE for between-sample composition correction; quantile only for cross-platform integration where dynamic range mismatch dominates.

## Common errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| Size factors all NA | Zero-heavy data with default `type='ratio'` | `type='poscounts'` |
| MA plot bulk cloud shifted off zero | TMM/RLE assumption violated | Spike-in normalization; `controlGenes=` |
| `lengthScaledTPM` reported as TPM in methods | Misleading option name | Clarify: count-scale matrix with length bias removed; NOT TPM |
| DE list reproducibly different across normalization methods | Marginal cases sensitive to normalization choice | Report results using two methods; flag genes that change rank |
| `cpm(y, log=TRUE)` very noisy at low counts | Default `prior.count` too small | `prior.count = 2` (modern edgeR default) |
| VST produces NA matrix | Too few genes after filtering | Set `nsub` lower in `vst(dds, nsub=...)` |
| Quantile-normalized RNA-seq missing known DE | Quantile erases the global biological shift | Use TMM/RLE; reserve quantile for cross-platform integration |

## References

- Anders S, Huber W. 2010. Differential expression analysis for sequence count data. *Genome Biol* 11(10):R106. doi:10.1186/gb-2010-11-10-r106
- Robinson MD, Oshlack A. 2010. A scaling normalization method for differential expression analysis of RNA-seq data. *Genome Biol* 11(3):R25. doi:10.1186/gb-2010-11-3-r25
- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biol* 15(12):550. doi:10.1186/s13059-014-0550-8
- Bullard JH, Purdom E, Hansen KD, Dudoit S. 2010. Evaluation of statistical methods for normalization and differential expression in mRNA-Seq experiments. *BMC Bioinformatics* 11:94. doi:10.1186/1471-2105-11-94
- Wagner GP, Kin K, Lynch VJ. 2012. Measurement of mRNA abundance using RNA-seq data: RPKM measure is inconsistent among samples. *Theory Biosci* 131(4):281-285. doi:10.1007/s12064-012-0162-3
- Mortazavi A, Williams BA, McCue K, Schaeffer L, Wold B. 2008. Mapping and quantifying mammalian transcriptomes by RNA-Seq. *Nat Methods* 5(7):621-628. doi:10.1038/nmeth.1226
- Bolstad BM, Irizarry RA, Astrand M, Speed TP. 2003. A comparison of normalization methods for high density oligonucleotide array data based on variance and bias. *Bioinformatics* 19(2):185-193. doi:10.1093/bioinformatics/19.2.185
- Smid M et al. 2018. Gene length corrected trimmed mean of M-values (GeTMM) processing of RNA-seq data performs similarly in intersample analyses while improving intrasample comparisons. *BMC Bioinformatics* 19:236. doi:10.1186/s12859-018-2246-7
- Lun ATL, Bach K, Marioni JC. 2016. Pooling across cells to normalize single-cell RNA sequencing data with many zero counts. *Genome Biol* 17:75. doi:10.1186/s13059-016-0947-7
- Jiang L et al. 2011. Synthetic spike-in standards for RNA-seq experiments. *Genome Res* 21(9):1543-1551. doi:10.1101/gr.121095.111
- Risso D, Schwartz K, Sherlock G, Dudoit S. 2011. GC-content normalization for RNA-Seq data. *BMC Bioinformatics* 12:480. doi:10.1186/1471-2105-12-480
- Hansen KD, Irizarry RA, Wu Z. 2012. Removing technical variability in RNA-seq data using conditional quantile normalization. *Biostatistics* 13(2):204-216. doi:10.1093/biostatistics/kxr054
- Chen Y et al. 2025. edgeR v4: powerful differential analysis of sequencing data with expanded functionality and improved support for small counts and larger datasets. *Nucleic Acids Res* 53(2):gkaf018. doi:10.1093/nar/gkaf018

## Related Skills

- counts-ingest - tximport offsets vs scaledTPM vs lengthScaledTPM; biotype pre-filtering before normalize
- gene-id-mapping - Filtering rRNA/Mt biotypes affects normalization
- metadata-joins - Sample alignment before normalization
- sparse-handling - Single-cell sparse matrix normalization patterns
- differential-expression/deseq2-basics - DESeq2 RLE / median-of-ratios internals
- differential-expression/edger-basics - edgeR TMM / TMMwsp internals
- differential-expression/batch-correction - Normalization vs batch correction distinction
- differential-expression/de-visualization - VST/rlog blind choice; log-CPM prior count
- single-cell/preprocessing - Single-cell normalization workflows
- rna-quantification/count-matrix-qc - QC before normalization
<!-- END FILE: expression-matrix/normalization/SKILL.md -->

## 子目录：expression-matrix/sparse-handling

<!-- BEGIN FILE: expression-matrix/sparse-handling/SKILL.md -->
---
name: bio-expression-matrix-sparse-handling
description: Stores and operates on sparse expression matrices for single-cell and large bulk RNA-seq, covering dgCMatrix/dgRMatrix/dgTMatrix when-each-is-fast, the dgCMatrix (CSC, R) <-> CSR (Python) implicit transpose, AnnData (cells-rows) <-> SingleCellExperiment (cells-cols) orientation flip, HDF5/h5ad vs Zarr cloud-native shift, HDF5SummarizedExperiment + DelayedArray for out-of-memory bulk, scanpy backed mode for large h5ad, the ~10-15% density crossover where dense beats sparse, 10X format proliferation (MTX vs CellRanger H5 vs h5ad), the dense-conversion memory blow-up, and Dask + Zarr for consortium-scale matrices. Use when choosing sparse format, working with single-cell-sized matrices, importing/exporting 10X, debugging R/Python interop transposes, processing matrices too large for RAM, or building cloud-native pipelines.
tool_type: python
primary_tool: scipy.sparse
---

## Version Compatibility

Reference examples tested with: numpy 1.26+, scipy 1.12+, pandas 2.2+, anndata 0.10+, scanpy 1.10+, Matrix R package 1.6+, HDF5Array 1.30+ (Bioconductor), DelayedArray 0.28+, zellkonverter 1.12+, zarr-python 2.18+, dask 2024.1+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Sparse Matrix Handling

**"Store / compute on a single-cell matrix without blowing up memory"** -> Pick the sparse format that matches the access pattern (CSC for column ops, CSR for row ops), respect the R/Python convention difference (Bioconductor stores cells in columns; AnnData stores cells in rows), and use HDF5/Zarr backed mode for matrices too large for RAM.

## The Single Most Important Modern Insight -- The R/Python interop transpose is silent and catastrophic

R Bioconductor (Seurat, SingleCellExperiment) stores cells in COLUMNS and uses dgCMatrix (Column-Compressed Sparse). Python scverse (AnnData, scanpy) stores cells in ROWS and defaults to CSR (Compressed Sparse Row). Round-tripping with `anndata2ri`, `zellkonverter`, or `rpy2` triggers a TRANSPOSE under the hood -- once per direction. Two flips silently cancel. A debugging session that converts back and forth multiple times can end up with mysteriously transposed data and no error.

| Conversion | Implicit transpose |
|------------|-------------------|
| Python CSR -> R dgCMatrix | YES (rows <-> cols) |
| AnnData `.X` (cells x genes) -> SingleCellExperiment counts (genes x cells) | YES |
| Seurat `@assays$RNA@counts` (genes x cells) -> AnnData `.X` (cells x genes) | YES |
| `scipy.sparse.csr_matrix(dense)` | None (just format conversion) |
| `csr.tocsc()` / `csc.tocsr()` | None (semantically same matrix, different layout) |

The safe pattern for one-shot conversions: file-based intermediate. `adata.write('file.h5ad')` then `zellkonverter::readH5AD('file.h5ad')` -- avoids the in-memory rpy2/reticulate gymnastics, and the file roundtrip makes orientation explicit.

For a 1M-cell single-cell matrix, the implicit transpose is non-trivial -- minutes of wall time and a temporary memory peak roughly equal to nnz x 12 bytes (CSC) or x 16 bytes (CSR with int64). Avoid unnecessary transposes by aligning the format to the consumer.

Two adjacent insights:

1. **Sparse becomes inefficient above ~10-15% density.** Sparse iteration has cache-unfriendly indirection; dense iteration is sequential. Above ~10-15% nonzero, dense is often faster for most operations even though it uses more memory.
2. **AnnData backed mode quietly differs from in-memory in important ways.** `sc.read_h5ad('file.h5ad', backed='r')` returns an AnnData where `.X` is a wrapped HDF5 dataset, read-only. Many scanpy functions silently load to memory; some functions error or hang on backed mode.

## Algorithmic Taxonomy

| Format | Layout | Fast for | Slow for |
|--------|--------|----------|----------|
| dgCMatrix (CSC, R) | i (row indices), p (col pointers), x (values) | Column slicing; per-cell ops in single-cell (cells in cols); matrix-vector with col vector | Row slicing |
| dgRMatrix (CSR, R) | j (col indices), p (row pointers), x (values) | Row slicing; per-gene ops when genes in rows | Column slicing |
| dgTMatrix (COO, R triplet) | i, j, x | Random insertion when building; reading MTX | Most operations -- convert to dgCMatrix after build |
| scipy `csc_matrix` | Same as dgCMatrix | Column ops in Python | Row ops |
| scipy `csr_matrix` | Same as dgRMatrix | Row ops (NumPy convention); matmul; sklearn defaults | Column ops |
| scipy `coo_matrix` | Triplet (i, j, data) | Construction; MTX I/O | Most ops -- convert after build |
| HDF5 (h5ad, h5) | Single-file binary chunked | Random access via chunks; compression; widely supported | Cloud / parallel writes |
| Zarr | Chunked array, per-chunk file (or S3 object) | Cloud-native; parallel writes; Dask integration | Single-file simplicity |
| DelayedArray + HDF5Array | Bioc lazy evaluation over HDF5 | Out-of-memory bulk ops in R | Speed of in-memory |

## Decision Tree by Scenario

| Scenario | Recommended approach |
|----------|---------------------|
| Single-cell (>10k cells), per-cell ops | dgCMatrix in R (Bioconductor); CSR `adata.X` in Python (scanpy) |
| Bulk RNA-seq (60-80% density) | Dense -- sparse overhead exceeds benefit |
| Single-cell pseudobulk (after donor aggregation) | Dense -- now 60-80% density typically |
| 1M+ cells, can't fit in RAM | scanpy backed mode OR HDF5SummarizedExperiment + DelayedArray |
| TCGA + GTEx + recount3 scale (100k+ samples) | HDF5Array / Zarr + Dask |
| 10X CellRanger 3.0+ output | `sc.read_10x_h5()` or `Read10X_h5()` -- the .h5 is faster than the .mtx triplet |
| Cloud-native (anndata on S3, dask compute) | Zarr |
| Local workstation, single-machine | HDF5 -- faster, more widely supported |
| Building sparse matrix incrementally | COO (dgTMatrix / coo_matrix); convert to CSC/CSR after |
| R <-> Python conversion | File-based intermediate (`adata.write` then `zellkonverter::readH5AD`); aware of the transpose |

## Check Sparsity

**Goal:** Decide whether sparse is the right format given the actual data density.

**Approach:** Compute nonzero fraction; rule of thumb is sparse > ~85% (single-cell). Below that, dense often wins.

```python
import numpy as np
import scipy.sparse as sp

def sparsity(m):
    if sp.issparse(m):
        return 1 - m.nnz / (m.shape[0] * m.shape[1])
    return (m == 0).mean()

s = sparsity(adata.X)
print(f'{s:.1%} sparse')
```

Memory math:

| Data | Format | Bytes |
|------|--------|-------|
| 30k x 100k single-cell matrix, 5% density | dgCMatrix | (5% * 3e9) * 12 bytes ~= 1.8 GB |
| Same | Dense double | 24 GB |
| 60k x 100k bulk, 70% density | dgCMatrix | 50 GB (worse than dense!) |
| Same | Dense double | 48 GB |

For single-cell (typically 90-95% sparse), sparse is essential. For bulk RNA-seq (typically 60-80% density), dense is faster and not appreciably larger.

## dgCMatrix / scipy CSC / CSR

**Goal:** Construct, query, and convert sparse matrices in the format matching the consumer's expected layout.

**Approach:** `Matrix::sparseMatrix(i, j, x, dims=...)` (R) or `scipy.sparse.csr_matrix((data, (i, j)))` (Python); preserve row/column names; convert layout (CSC <-> CSR) without changing semantics.

```python
import scipy.sparse as sp
import pandas as pd

dense_df = pd.read_csv('counts.csv', index_col=0)
sparse_csr = sp.csr_matrix(dense_df.values)
sparse_csc = sp.csc_matrix(dense_df.values)

gene_names = dense_df.index.tolist()
sample_names = dense_df.columns.tolist()

sparse_csr.tocsc()
sparse_csc.tocsr()
```

```r
library(Matrix)

dense_mat <- as.matrix(read.csv('counts.csv', row.names = 1))
sparse_dgc <- as(dense_mat, 'CsparseMatrix')

class(sparse_dgc)
rownames(sparse_dgc) <- rownames(dense_mat)
colnames(sparse_dgc) <- colnames(dense_mat)
```

dgTMatrix is best for building matrices incrementally (reading MTX, parsing per-row); convert to dgCMatrix for downstream ops:

```r
mat_t <- as(triplet_data, 'TsparseMatrix')
mat_c <- as(mat_t, 'CsparseMatrix')
```

## HDF5 vs Zarr -- The Cloud-Native Shift

HDF5 (Hierarchical Data Format 5): hierarchical, single-file binary. Random access via chunks; supports compression (gzip, blosc, lz4). On-disk format for AnnData `.h5ad`, MuData `.h5mu`, 10x Genomics `.h5`, HDF5SummarizedExperiment.

Zarr: cloud-native, chunked array storage. Each chunk is a separate file (or S3 object). Parallel-write friendly; splittable by Dask. Format used by recent AnnData (`anndata.write_zarr`), SpatialData, and large-cohort consortia.

| Criterion | HDF5 | Zarr |
|-----------|------|------|
| File structure | Single binary file | Directory of chunk files |
| Parallel writes | Limited (process-level locks) | Native |
| S3 / cloud object storage | Workarounds (h5cloud); often slow | Native; first-class |
| Compression options | gzip, blosc, lz4, szip | gzip, blosc, lz4, zstd, custom |
| Local workstation speed | Faster | Slightly slower (many small files) |
| Wide ecosystem support | Yes (mature) | Growing; modern scverse |

For local workstation work, HDF5 is faster and more widely supported. For cloud-mounted analysis (anndata on S3 with dask-distributed compute), Zarr wins because of object-storage friendliness.

## HDF5SummarizedExperiment + DelayedArray (Bioconductor)

**Goal:** Work with bulk SummarizedExperiment objects too large to fit in RAM by keeping the matrix on disk.

**Approach:** `HDF5Array` wraps an HDF5 dataset as a `DelayedArray`. Subsetting builds a delayed operation tree -- no I/O until realization. `DelayedMatrixStats` provides delayed-friendly stat functions.

```r
library(HDF5Array)
library(SummarizedExperiment)
library(DelayedMatrixStats)

se <- loadHDF5SummarizedExperiment('saved_se_dir')

s <- se[1:1000, 1:50]
row_means <- rowMeans2(assay(se))

saveHDF5SummarizedExperiment(se, 'saved_se_dir', replace = TRUE)
```

The `assay(se)` returns a DelayedMatrix backed by HDF5. DESeq2, edgeR, limma have varying levels of DelayedArray support; consult package docs before assuming all ops work in delayed mode.

For TCGA + GTEx + recount3 scale (100k+ samples, 60k genes), a dense matrix is ~48 GB (double); dgCMatrix at 70% density is ~50 GB (sparse loses). HDF5Array + chunk-aware ops keeps memory at whatever-fits-in-RAM.

## scanpy Backed Mode

**Goal:** Work with h5ad files too large for memory by loading only accessed slices on demand.

**Approach:** `sc.read_h5ad(..., backed='r')` returns an AnnData with `.X` as a wrapped HDF5 dataset. Subset operations are lazy; `.to_memory()` realizes.

```python
import scanpy as sc

adata = sc.read_h5ad('large_dataset.h5ad', backed='r')
print(f'Shape: {adata.shape}, X type: {type(adata.X)}')

t_cells = adata[adata.obs['cell_type'] == 'T_cell', :].to_memory()
```

Limitations:
- `.X` is read-only in `backed='r'`. Use `backed='r+'` for in-place updates, but only `.X` updates supported.
- `.obs` and `.var` are fully loaded -- only `.X` supports backed access.
- Very large sparse h5ad (>35 GB) can still cause memory issues even in backed mode (anndata library overhead).
- Many scanpy functions internally load to memory; check `?function` docs for backed compatibility.
- Functions like `sc.tl.pca`, `sc.pp.neighbors` typically require in-memory; subset first with `.to_memory()`.

For datasets too large for backed mode, process in chunks:

```python
import anndata as ad

def process_in_chunks(h5ad_path, chunk_size=10000, func=None):
    adata = sc.read_h5ad(h5ad_path, backed='r')
    n_cells = adata.shape[0]
    results = []
    for start in range(0, n_cells, chunk_size):
        end = min(start + chunk_size, n_cells)
        chunk = adata[start:end].to_memory()
        if func:
            chunk = func(chunk)
        results.append(chunk)
    return ad.concat(results)
```

## 10X Genomics Format Proliferation

| Format | Files | Notes |
|--------|-------|-------|
| MTX (pre-CellRanger 3.0) | `matrix.mtx` + `barcodes.tsv` + `features.tsv` (or `genes.tsv`) | Triplet format; slow to read for large matrices |
| H5 (CellRanger 3.0+) | `filtered_feature_bc_matrix.h5` | HDF5 with `/matrix/data`, `/matrix/indices`, `/matrix/indptr`, `/matrix/shape`; single file, fast |
| H5AD | `data.h5ad` | AnnData; convert on import |
| kallisto|bustools output | `output.bus` + barcode and gene mappings | `BUSpaRse` / `kb-python` |

```python
import scanpy as sc

adata = sc.read_10x_h5('filtered_feature_bc_matrix.h5')
adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')
```

```r
library(Seurat)
mat <- Read10X_h5('filtered_feature_bc_matrix.h5')
mat <- Read10X(data.dir = 'filtered_feature_bc_matrix/')

library(DropletUtils)
sce <- read10xCounts('filtered_feature_bc_matrix/')
```

For 10X output, prefer the `.h5` over the MTX triplet -- typically 5-10x faster for large matrices.

## Dense Conversion -- The Memory Blow-Up

`adata.X.toarray()` (Python) or `as.matrix(seurat_obj@assays$RNA@counts)` (R) on a 30k x 100k single-cell matrix instantiates a ~24 GB dense double array. Common triggers:

- Passing sparse to a function that internally calls `as.matrix()` (older R `cor()` implementations).
- Heatmap functions (`pheatmap`, `ComplexHeatmap`) that require dense.
- ML libraries with no sparse support (some sklearn models; XGBoost requires specific sparse API).
- Plotting functions (`plot()`, `ggplot2`) called on the full matrix.

Defensive pattern: subset to a manageable gene/cell set BEFORE dense conversion.

For per-cell PCA-style ops, use sparse-aware solvers:

```python
from scipy.sparse.linalg import svds
U, s, Vt = svds(adata.X, k=50)
```

```r
library(irlba)
svd_res <- irlba(sparse_mat, nv = 50)
```

`irlba` (R) and `scipy.sparse.linalg.svds` (Python) compute truncated SVD without densifying.

## SCE vs AnnData vs MuData -- Where Bulk Fits

| Container | Library | Cells/samples | Multi-modal | Bulk fit |
|-----------|---------|---------------|-------------|----------|
| SummarizedExperiment / RangedSummarizedExperiment | Bioconductor | n/a; bulk | No | YES -- standard for DESeq2/edgeR/limma bulk |
| SingleCellExperiment (Amezquita 2020) | Bioconductor | cells in cols | Via `altExps` | scRNA-seq with spike-ins, ADT |
| AnnData | scverse/Python | cells in rows | Via layers | scRNA-seq; bulk is unusual |
| MuData | scverse/Python | cells in rows | Yes, multiple AnnData | Multi-modal scRNA + ATAC + protein |
| MultiAssayExperiment | Bioconductor | samples | Yes | R-side multi-modal analog |

Bulk RNA-seq rarely uses AnnData -- it shines on the single-cell dimensionality reduction / neighbors / clustering machinery. For bulk in R, use SummarizedExperiment. For bulk in Python, a tidy DataFrame + numpy array is usually sufficient.

## Dask + Zarr for Consortium-Scale Matrices

For TCGA + GTEx + recount3 (Wilks 2021 *Genome Biol* 22:323) or pancancer assemblies:

```python
import zarr
import dask.array as da

z = zarr.open('counts.zarr', mode='r')
da_arr = da.from_zarr(z)

col_sums = da_arr.sum(axis=0).compute()
filtered = da_arr[da_arr.sum(axis=1) > 100, :]
```

```python
import anndata as ad
adata_disk = ad.read_zarr('large_data.zarr')
```

For R: `HDF5Array` + `DelayedArray` is the equivalent, but R doesn't have a true Dask analog. BiocParallel can parallelize chunks, but lazy planning is more manual.

## Sparse Operations

```python
import numpy as np
import scipy.sparse as sp

row_sums = np.array(sparse_matrix.sum(axis=1)).flatten()
col_sums = np.array(sparse_matrix.sum(axis=0)).flatten()

keep_rows = row_sums > 10
sparse_filt = sparse_matrix[keep_rows, :]

sparse_log = sparse_matrix.copy()
sparse_log.data = np.log1p(sparse_log.data)
```

Subsetting: select genes (rows) or samples (cols) by index:

```python
gene_idx = [gene_names.index(g) for g in ['TP53', 'BRCA1', 'MYC'] if g in gene_names]
subset = sparse_matrix[gene_idx, :]
```

## CPM Normalization on Sparse

**Goal:** Apply CPM normalization without densifying.

**Approach:** Compute library sizes from column sums; broadcast scaling factors with sparse multiply for CPM; transform only the nonzero data array in-place with log1p.

```python
import numpy as np
import scipy.sparse as sp

def normalize_sparse_cpm(sparse_matrix):
    lib_sizes = np.array(sparse_matrix.sum(axis=0)).flatten()
    scaling = 1e6 / lib_sizes
    return sparse_matrix.multiply(scaling)

def log1p_inplace(sparse_matrix):
    out = sparse_matrix.copy()
    out.data = np.log1p(out.data)
    return out

cpm = normalize_sparse_cpm(adata.X)
log_cpm = log1p_inplace(cpm)
```

After log-transformation, sparsity is PRESERVED (log1p(0) = 0). After CPM with pseudocount, zeros become nonzero -- check sparsity and convert to dense if density drops below ~15%.

## Save / Load Sparse Matrices

```python
import scipy.sparse as sp
import numpy as np

sp.save_npz('counts_sparse.npz', sparse_matrix)
loaded = sp.load_npz('counts_sparse.npz')

np.savez('counts_with_meta.npz',
    data    = sparse_matrix.data,
    indices = sparse_matrix.indices,
    indptr  = sparse_matrix.indptr,
    shape   = sparse_matrix.shape,
    genes   = np.array(gene_names),
    samples = np.array(sample_names))
```

For interop and durable storage, prefer h5ad or zarr:

```python
adata.write_h5ad('counts.h5ad')
adata.write_zarr('counts.zarr')
```

## Per-Method Failure Modes

### Implicit transpose in R/Python conversion

**Trigger:** AnnData with cells in rows passed to a SingleCellExperiment workflow that expects cells in cols; downstream `colSums` returns gene-level totals.

**Mechanism:** AnnData stores cells in rows; SCE in cols. The conversion auto-transposes ONCE per direction; two roundtrips silently restore.

**Symptom:** Per-cell stats look like per-gene stats; QC plots have wrong axes.

**Fix:** Use file-based intermediate (`adata.write('file.h5ad')`; `zellkonverter::readH5AD('file.h5ad')`). Always verify dimensions and orientation after conversion.

### Dense conversion blew up memory

**Trigger:** `as.matrix(seurat_obj@assays$RNA@counts)` on a 100k-cell dataset; R session crashes with OOM.

**Mechanism:** 100k cells x 30k genes = 3e9 entries; double precision = 24 GB.

**Symptom:** R session killed; "cannot allocate vector of size N GB".

**Fix:** Don't densify the full matrix. Subset to genes/cells of interest first. For dimensionality reduction, use `irlba::irlba()` (sparse SVD).

### scanpy backed mode silently loaded to memory

**Trigger:** `adata = sc.read_h5ad(path, backed='r')` then `sc.tl.pca(adata)`; memory spikes to dense-equivalent.

**Mechanism:** Many scanpy functions internally call `.to_memory()` because they cannot operate on backed mode. `sc.tl.pca`, `sc.pp.neighbors`, `sc.tl.umap` all materialize.

**Symptom:** OOM despite backed mode.

**Fix:** Subset first (`adata[mask].to_memory()`), then operate. Or use a streaming-aware alternative (Dask + Zarr).

### Sparse stored where dense would be faster

**Trigger:** Bulk RNA-seq with 70% density stored as dgCMatrix; per-gene `rowVars` is slow.

**Mechanism:** Sparse iteration has cache-unfriendly indirection; above ~10-15% density, dense wins.

**Symptom:** Operations notably slower than expected; profiler shows time in sparse indexing.

**Fix:** Convert to dense for the hot path: `as.matrix(sparse_mat)` (R) or `sparse_matrix.toarray()` (Python). Memory may go up but speed improves substantially.

### 10X MTX read is slow

**Trigger:** Reading a 100k-cell 10X dataset via the MTX three-file format; takes 10+ minutes.

**Mechanism:** MTX is a text format; parsing is slow for large matrices.

**Symptom:** Long load times; user kills the process before completion.

**Fix:** Use the CellRanger H5 (`.h5`) instead -- typically 5-10x faster.

## Common errors

| Error / symptom | Cause | Fix |
|-----------------|-------|-----|
| `cannot allocate vector of size N GB` | Implicit dense conversion | Subset first; use sparse-aware solver (irlba) |
| Sparse-dense arithmetic returns `numpy.matrix` | Deprecated NumPy type from sparse+dense | `np.asarray(sparse + dense)` to force ndarray |
| `KeyError: '_index'` reading h5ad | anndata version mismatch | Update anndata; or `sc.read_h5ad(..., backed=None)` |
| Empty rows/cols after sparse subset | Subset removed all data | Verify the index list; cross-check sample/gene names |
| Backed mode AnnData crash on `sc.tl.umap` | Function not backed-compatible | `.to_memory()` on the subset first |
| Per-cell totals look wrong after R<->Python conversion | Implicit transpose | Verify dimensions; use file-based intermediate |
| CSR (Python) <-> dgCMatrix (R) treated as same | Convention difference | They're transposes of each other; verify shape and a known cell-gene pair |

## References

- Amezquita RA, Lun ATL, Becht E et al. 2020. Orchestrating single-cell analysis with Bioconductor. *Nat Methods* 17:137-145. doi:10.1038/s41592-019-0654-x
- Wolf FA, Angerer P, Theis FJ. 2018. SCANPY: large-scale single-cell gene expression data analysis. *Genome Biol* 19:15. doi:10.1186/s13059-017-1382-0
- Wilks C et al. 2021. recount3: summaries and queries for large-scale RNA-seq expression and splicing. *Genome Biol* 22:323. doi:10.1186/s13059-021-02533-6
- Bates D, Maechler M. 2023. Matrix: Sparse and Dense Matrix Classes and Methods. R package version 1.6-x.
- Pages H et al. 2020. HDF5Array: HDF5 backend for DelayedArray objects. Bioconductor package.
- Miles A et al. 2020. zarr-python. Python package documentation.
- Rocklin M. 2015. Dask: Parallel Computation with Blocked algorithms and Task Scheduling. *Proc Python Sci Conf.* (canonical Dask reference)
- Lachmann A et al. 2018. Massive mining of publicly available RNA-seq data from human and mouse. *Nat Commun* 9:1366. doi:10.1038/s41467-018-03751-6

## Related Skills

- counts-ingest - Reading 10X formats; building sparse matrices from quantification output
- gene-id-mapping - Var (gene) metadata in AnnData
- metadata-joins - Obs (sample) metadata in AnnData
- normalization - log1p and CPM patterns on sparse
- differential-expression/deseq2-basics - Pseudobulk aggregation makes dense
- single-cell/data-io - Single-cell file format ecosystem
- single-cell/preprocessing - Standard single-cell sparse pipeline
<!-- END FILE: expression-matrix/sparse-handling/SKILL.md -->

<!-- END CATEGORY: expression-matrix -->

