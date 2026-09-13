---
slug: bio-database-access-integrated
version: 1.0.1
displayName: "数据库访问 / Public database querying"
name: bio-database-access-integrated
summary: "中文：数据库访问综合技能，整合 15 个相关专题，覆盖公共数据库查询：NCBI Entrez/BLAST/SRA、Ensembl REST、UniProt、BioMart、STRING。 English: Integrated Public database querying skill covering 15 related topics, including Public database querying: NCBI Entrez/BLAST/SRA, Ensembl REST, UniProt, BioMart, STRING."
description: "中文：这是一个面向数据库访问的综合生物信息学 Skill，整合当前分类下 15 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：公共数据库查询：NCBI Entrez/BLAST/SRA、Ensembl REST、UniProt、BioMart、STRING。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：BLAST+, Bio.Blast.NCBIWWW, Bio.Entrez。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Public database querying, combining 15 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Public database querying: NCBI Entrez/BLAST/SRA, Ensembl REST, UniProt, BioMart, STRING. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: BLAST+, Bio.Blast.NCBIWWW, Bio.Entrez. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# database-access 分类 Skill 整合版

> 本文件整合同一主分类目录下 15 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: database-access -->

## 子目录：database-access/batch-downloads

<!-- BEGIN FILE: database-access/batch-downloads/SKILL.md -->
---
name: bio-batch-downloads
description: Download large datasets from NCBI efficiently using EPost, history server, batching, rate limiting, and retry logic. Use when bulk-fetching tens of thousands of sequences, pulling all results of a large ESearch, designing reproducible pipelines, comparing E-utilities to NCBI Datasets v2 CLI, or implementing checksum-validated downloads. Encodes WebEnv TTL (~8h), EPost 200-ID limit, retmax caps, parallelization design, and integrity verification.
tool_type: python
primary_tool: Bio.Entrez
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, NCBI Datasets CLI 16.0+, Entrez Direct 21.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(Bio.Entrez.efetch)` to check signatures
- CLI: `datasets --version` and `efetch -version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Batch Downloads

**"Download N thousand records from NCBI without getting blocked"** -> The right answer is rarely "parallelize requests". For >5000 records the answer is the **history server**: search once, fetch in chunks server-side. For >100,000 records or whole genomes, the modern answer is **NCBI Datasets v2 CLI** -- the E-utilities are not optimized for bulk genome/gene data anymore.

This skill encodes (a) when to use each retrieval strategy, (b) the precise rate-limit math, (c) WebEnv lifecycle for long-running jobs, (d) how to design retry/resume, and (e) when to defect to Datasets CLI instead.

- Python: `Entrez.esearch(usehistory='y')` + chunked `Entrez.efetch()` (BioPython)
- CLI: `datasets download genome accession ...` (NCBI Datasets v2 -- preferred for genome/gene bulk)
- CLI: `epost | efetch -mode webenv` (Entrez Direct)

## Required Setup

```python
from Bio import Entrez
import time
Entrez.email = 'researcher@institution.edu'
Entrez.api_key = 'YOUR_KEY'  # 3 -> 10 req/sec; mandatory for bulk
Entrez.tool = 'project-name'
```

## Decision matrix: which retrieval strategy?

| Record count | Source | Strategy | Why |
|---|---|---|---|
| < 200 known IDs | Any db | EFetch with comma-joined `id=` | Single round-trip; trivial |
| 200-5,000 known IDs | Any db | EPost (chunked at 200) -> history -> chunked EFetch | URL length limit + chunked retrieval |
| 5,000-100,000 from a query | Any db | ESearch with `usehistory='y'` -> chunked EFetch | Push to server once; pull in batches |
| > 100,000 sequences | nucleotide/protein | Consider FTP mirror or Datasets CLI; chunk if E-utils still | NCBI throttles bulk; offline mirror is faster |
| Whole genome assemblies | Assembly/Datasets | `datasets download genome accession ...` | Datasets v2 is the modern bulk endpoint |
| All RefSeq for a species | Datasets | `datasets download genome taxon ...` | Replaces assembly_summary.txt scraping |
| All gene records for a list | Datasets | `datasets download gene gene-id ...` | Cleaner output than EFetch gene XML |
| Raw sequencing reads | SRA | `prefetch` + `fasterq-dump` (or ENA mirror) | See `sra-data` skill |

The Datasets CLI is the right answer for any genome- or gene-centric bulk workflow as of 2023+. The E-utilities remain right for PubMed, ESummary metadata, custom queries, and anything not in the Datasets API. See `ncbi-datasets-cli` skill.

## Rate-limit math (precise)

| Auth | req/sec | Sleep between calls | Bulk-friendly notes |
|---|---|---|---|
| Email only | 3 | 0.34 s | Single-threaded only; parallelism violates ToS |
| Email + API key | 10 | 0.10 s | Modest parallelism (max ~4 workers) safe |
| Institutional bulk | Negotiated | Email `eutilities@ncbi.nlm.nih.gov` | For >100K queries; courtesy expected |

NCBI's terms ask that heavy automated downloads run **outside US weekday business hours (9 AM-5 PM ET)**. Cron the job for nights/weekends; pipelines that ignore this get IP-throttled.

**Critical**: parallelizing API calls is the WRONG bulk strategy. One stream with history server + larger batches is faster AND more polite than N parallel streams. The bottleneck is rarely NCBI's throughput at small N -- it's the round-trip count.

## History server lifecycle (the long-running-job trap)

| Property | Value | Failure mode |
|---|---|---|
| TTL | 8 hours absolute (per NCBI E-utils help) | Job started Friday evening dies Saturday morning |
| Idle eviction | ~15 min empirically under load | A worker that stalls loses its WebEnv |
| Per-session isolation | One WebEnv string per session | Don't share across processes if isolation matters |
| Expired session behavior | HTTP 200 with `<ERROR>WebEnv not found</ERROR>` | Won't surface as HTTP error -- must parse body |
| Recovery | Re-run ESearch; resume at `retstart` | Need to checkpoint progress to disk |

Production pattern: checkpoint the `retstart` cursor after each successful chunk to disk; on restart, re-run ESearch (cheap), pick up `retstart` from checkpoint, continue.

## EPost specifics

EPost pushes a list of UIDs to the history server so downstream EFetch can pull by WebEnv/QueryKey instead of by ID. Two constraints:
- **200 IDs per EPost call** is the hard limit.
- **Chained posts share a WebEnv**: pass the WebEnv from the first call into subsequent calls to accumulate IDs under one session; a new QueryKey is issued per call.

To intersect: `term=#{key1} AND #{key2}` against the WebEnv produces a new key.

## Batch size guidelines per rettype

| Database | rettype | Optimal batch | Per-record payload |
|---|---|---|---|
| nucleotide | fasta | 500-1000 | ~1 KB |
| nucleotide | gb | 100-200 | ~10-50 KB |
| protein | fasta | 500-1000 | ~0.5 KB |
| protein | gp | 100-200 | ~5-30 KB |
| pubmed | medline | 1000-2000 | ~2 KB |
| pubmed | xml | 200-500 | ~10-30 KB |
| any | esummary (docsum) | 500 per call | ~1 KB |

Smaller batches for GenBank/XML because per-record payload is larger; larger batches for FASTA because the per-call HTTP overhead dominates.

## Code patterns

### Production batch fetch (history server + retry + checkpoint)

**Goal:** Download all records matching a query, robust to mid-job failures and session expiry.

**Approach:** ESearch with history; checkpoint cursor to disk; on error, retry the chunk; on session expiry, re-run ESearch and resume from checkpoint.

**Reference (BioPython 1.83+):**
```python
import json
import time
from pathlib import Path
from urllib.error import HTTPError
from Bio import Entrez


def checkpointed_batch_download(db, term, out_path, ckpt_path, rettype='fasta',
                                 retmode='text', batch_size=500, max_retries=3):
    '''Download all matching records with disk checkpoint for resumability.'''
    delay = 0.1 if Entrez.api_key else 0.34
    ckpt = Path(ckpt_path)
    start = json.loads(ckpt.read_text())['start'] if ckpt.exists() else 0

    h = Entrez.esearch(db=db, term=term, usehistory='y', retmax=0)
    s = Entrez.read(h); h.close()
    webenv, query_key, total = s['WebEnv'], s['QueryKey'], int(s['Count'])
    print(f'{total:,} records matched; resuming at {start:,}')

    mode = 'a' if start else 'w'
    with open(out_path, mode) as out:
        while start < total:
            for attempt in range(max_retries):
                try:
                    h = Entrez.efetch(db=db, rettype=rettype, retmode=retmode,
                                      retstart=start, retmax=batch_size,
                                      webenv=webenv, query_key=query_key)
                    body = h.read(); h.close()
                    if isinstance(body, bytes):
                        body = body.decode('utf-8', errors='replace')
                    if '<ERROR>' in body[:500]:
                        raise RuntimeError(f'Server error in body: {body[:200]}')
                    out.write(body)
                    break
                except HTTPError as e:
                    if e.code == 429:
                        wait = 10 * (attempt + 1)
                        print(f'  Rate-limited; sleeping {wait}s')
                        time.sleep(wait)
                    elif attempt == max_retries - 1:
                        raise
                    else:
                        time.sleep(5 * (attempt + 1))
                except RuntimeError as e:
                    # Likely WebEnv expired; re-run ESearch
                    print(f'  {e}; refreshing WebEnv')
                    h = Entrez.esearch(db=db, term=term, usehistory='y', retmax=0)
                    s = Entrez.read(h); h.close()
                    webenv, query_key = s['WebEnv'], s['QueryKey']

            start += batch_size
            ckpt.write_text(json.dumps({'start': start, 'total': total}))
            time.sleep(delay)
            print(f'  {min(start, total):,}/{total:,}')
    ckpt.unlink(missing_ok=True)
```

### EPost large ID list, then EFetch

**Goal:** Download by a known list of 5,000 accessions without 414 URI errors.

**Approach:** EPost in 200-ID chunks; reuse WebEnv across chunks; final fetch reads from history.

**Reference (BioPython 1.83+):**
```python
def epost_and_fetch(db, ids, out_path, rettype='fasta', retmode='text', batch_size=500):
    delay = 0.1 if Entrez.api_key else 0.34
    webenv = None
    posted_keys = []  # (query_key, n_ids) so we iterate each key's actual size
    for i in range(0, len(ids), 200):
        chunk = ids[i:i+200]
        kwargs = {'db': db, 'id': ','.join(chunk)}
        if webenv:
            kwargs['WebEnv'] = webenv
        h = Entrez.epost(**kwargs)
        r = Entrez.read(h); h.close()
        webenv = r['WebEnv']
        posted_keys.append((r['QueryKey'], len(chunk)))
        time.sleep(delay)

    with open(out_path, 'w') as out:
        for qk, n in posted_keys:
            for start in range(0, n, batch_size):
                h = Entrez.efetch(db=db, rettype=rettype, retmode=retmode,
                                  retstart=start, retmax=min(batch_size, n - start),
                                  webenv=webenv, query_key=qk)
                out.write(h.read()); h.close()
                time.sleep(delay)
```

### Integrity check after download

**Goal:** Confirm downloaded FASTA has the expected record count and no truncation.

**Approach:** Count expected (from ESearch Count) vs observed (from SeqIO.parse).

```python
from Bio import SeqIO

def verify_fasta_count(path, expected):
    observed = sum(1 for _ in SeqIO.parse(path, 'fasta'))
    assert observed == expected, f'Expected {expected:,} records, found {observed:,}'
    return True
```

For genome assemblies and known-checksum files, NCBI provides MD5 manifests (e.g. `md5checksums.txt` in FTP genome directories). NCBI Datasets CLI verifies checksums automatically; the FTP-direct route needs explicit `md5sum -c`.

### Compare E-utils to Datasets CLI cost

```python
def estimate_efetch_calls(total, batch_size):
    return -(-total // batch_size)  # ceiling division
```

For 100,000 nucleotide records at 500/batch with API key: 200 calls * 0.1s = 20s minimum. For the same workflow via `datasets download gene gene-id 100000`: one CLI invocation, parallel download, automatic checksum. For genome-scale bulk, Datasets wins by an order of magnitude.

### Parallelization design (modest)

**Goal:** Pull from two independent queries concurrently without violating rate limits.

**Approach:** Async with a global semaphore that enforces the API-key-permitted rate. Max 4 concurrent workers is the polite cap.

```python
import asyncio
from asyncio import Semaphore

# Pseudo-pattern; real impl needs aiohttp + Bio.Entrez async wrappers
async def fetch_with_semaphore(sem, db, id_, rettype):
    async with sem:
        # call EFetch
        await asyncio.sleep(0.1)  # rate gate
        # ... actual call

sem = Semaphore(4)
```

Never exceed 4 concurrent workers with an API key, or 1 without. Above that NCBI throttles by IP and the whole pipeline grinds.

## Failure modes

### Session expires mid-pipeline
- **Trigger:** Job runs >8h or worker idles >15 min.
- **Mechanism:** WebEnv evicted; EFetch returns HTTP 200 with `<ERROR>WebEnv not found</ERROR>` body.
- **Symptom:** Silently truncated output mid-file; downstream parsing fails on empty chunks.
- **Fix:** Parse body for `<ERROR>`; re-run ESearch and resume at checkpointed `retstart`.

### URL too long on >200 IDs
- **Trigger:** Comma-joined `id=` to EFetch with 250+ IDs.
- **Mechanism:** GET URL exceeds NCBI's ~2000 char limit.
- **Symptom:** HTTP 414 URI Too Long, or silent truncation.
- **Fix:** EPost in chunks of 200 first, then EFetch by WebEnv/QueryKey.

### Rate-limit cascade
- **Trigger:** Parallelizing without API key; or >10 req/s with key.
- **Mechanism:** NCBI returns 429; aggressive retry triggers IP-level throttle.
- **Symptom:** Pipeline gets slower and eventually stops.
- **Fix:** Add jittered exponential backoff; reduce concurrency; reach out for institutional access if bulk is the norm.

### Datasets / E-utils confusion
- **Trigger:** Building a custom assembly_summary.txt scraper instead of using Datasets.
- **Mechanism:** Datasets API is the official, supported bulk endpoint for genome/gene data; E-utils is not optimized for it.
- **Symptom:** Slow downloads, stale snapshots, missing fields.
- **Fix:** Use `datasets download genome ...` for genomes; `datasets download gene ...` for gene records. See `ncbi-datasets-cli`.

### Silent retmax cap
- **Trigger:** ESearch without `usehistory='y'`; Count > 9999.
- **Mechanism:** Legacy esearch enforces 9999 cap; the rest of the result set is silently dropped.
- **Symptom:** Batch loop terminates early; missing thousands of records.
- **Fix:** Always set `usehistory='y'` for any query expected to return >5000.

### Checkpoint corruption / partial chunk
- **Trigger:** Job crashes mid-chunk; checkpoint hasn't been written.
- **Mechanism:** Output file has half a record at the end.
- **Symptom:** SeqIO.parse fails on the partial record.
- **Fix:** Write checkpoint AFTER successful chunk write + file flush; on resume, truncate the output file at the last newline before continuing.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| HTTPError 429 | Rate limit | Sleep with backoff; get API key |
| HTTPError 414 | URL too long | EPost first |
| `<ERROR>WebEnv not found</ERROR>` (HTTP 200) | Session expired | Re-run ESearch; resume at checkpoint |
| Output file ends mid-record | Crash mid-chunk | Truncate-to-newline on resume |
| Slow despite API key | Too few records per call | Increase batch_size to 500+ for FASTA |
| Datasets CLI faster than EFetch | Workflow is genome/gene bulk | Switch to `ncbi-datasets-cli` |

## References

- Sayers EW et al. (2024) Database resources of the National Center for Biotechnology Information in 2024. *Nucleic Acids Res* 52:D33-D43.
- Kans J. (2024) Entrez Direct: E-utilities on the Unix Command Line. NCBI Bookshelf NBK179288.
- NCBI. EPost help and Usage Guidelines. NBK25499.
- NCBI Datasets documentation: https://www.ncbi.nlm.nih.gov/datasets/docs/v2/

## Related Skills

- entrez-search - Build the query that batch-downloads will fetch
- entrez-fetch - Single-record EFetch and ESummary
- entrez-link - Chain ELink with neighbor_history for cross-db bulk
- ncbi-datasets-cli - Modern bulk endpoint for genome/gene data; preferred over E-utils for that scope
- sra-data - Raw read downloads via SRA toolkit (not via E-utilities)
- geo-data - GEO supplementary file downloads
<!-- END FILE: database-access/batch-downloads/SKILL.md -->

## 子目录：database-access/biomart-queries

<!-- BEGIN FILE: database-access/biomart-queries/SKILL.md -->
---
name: bio-biomart-queries
description: Bulk-query Ensembl BioMart (and other BioMart instances) for cross-database ID mapping, gene/transcript/exon coordinates, and ortholog tables. Use when batch-converting Ensembl IDs to other namespaces (HGNC, RefSeq, UniProt, Entrez), pulling gene coordinate tables for thousands of genes, building ortholog wide-tables across species, or replacing slow Ensembl REST loops with one-shot bulk export. Encodes BioMart's XML query format, R biomaRt vs Python pybiomart trade-off, mart-vs-dataset hierarchy, and the URL endpoint that's BioMart-specific (separate from rest.ensembl.org).
tool_type: mixed
primary_tool: pybiomart
---

## Version Compatibility

Reference examples tested with: pybiomart 0.9+, R biomaRt 2.58+ (Bioconductor); Ensembl BioMart (release 110+)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show pybiomart`
- R: `packageVersion('biomaRt')`

The BioMart XML query format is stable across Ensembl releases; the underlying mart names and attribute IDs can change between Ensembl releases. For published work, pin the Ensembl release via `useEnsembl(version=110)`.

# BioMart Queries

**"Bulk-convert IDs / pull coordinate tables / extract ortholog wide tables"** -> BioMart is the right answer for any Ensembl-rooted query producing >5,000 rows. It is a separate service from the Ensembl REST API, with separate rate behavior and a different query model (XML-based, batch-oriented). For one-off lookups (<100 records), Ensembl REST is more convenient; for bulk anything, BioMart wins.

The single most important fact: **BioMart returns a flat table from a single query**. There is no per-record loop, no rate-limit cascade, no async polling. One XML query in; one TSV out.

- Python: `pybiomart` (https://github.com/jrderuiter/pybiomart) is the lightest client
- R: `biomaRt` Bioconductor (Durinck et al. 2009 *Nat Protoc* 4:1184) is the canonical client
- CLI: `curl` against the XML endpoint works but is rarely used directly
- Web: `https://www.ensembl.org/biomart/martview` for interactive query design

## Installation

```bash
pip install pybiomart pandas
# R:
# BiocManager::install('biomaRt')
```

## BioMart hierarchy

| Level | Examples |
|---|---|
| Mart | `ENSEMBL_MART_ENSEMBL` (genes), `ENSEMBL_MART_SNP` (variants), `ENSEMBL_MART_MOUSE` (mouse-specific) |
| Dataset | `hsapiens_gene_ensembl`, `mmusculus_gene_ensembl`, etc. (per species) |
| Attribute | Fields to return: `ensembl_gene_id`, `external_gene_name`, `chromosome_name`, etc. |
| Filter | Constraints on the query: `chromosome_name = 17`, `biotype = protein_coding`, etc. |

A query is: pick a mart, pick a dataset, list attributes to return, list filters to constrain. BioMart returns a single TSV.

Discovery:
```python
from pybiomart import Server
server = Server(host='http://www.ensembl.org')
print(server.marts)                                          # list marts
mart = server['ENSEMBL_MART_ENSEMBL']
print(mart.datasets)                                         # list datasets (species)
ds = mart['hsapiens_gene_ensembl']
print(ds.attributes)                                         # list attributes
print(ds.filters)                                            # list filters
```

## Decision matrix: BioMart vs Ensembl REST

| Question | BioMart | Ensembl REST |
|---|---|---|
| Bulk ID mapping (>5000 IDs) | yes (1 query) | rate-limited cascade |
| Single-gene lookup | overkill | yes |
| Coordinate tables for thousands of genes | yes | rate-limited |
| Ortholog wide-table across species | yes (multi-species mart) | per-gene loop |
| VEP variant annotation | no | yes (or local VEP) |
| Sequence retrieval | partial | yes |
| Real-time | no (batch) | yes (per-record) |
| Reproducibility (version pin) | `useEnsembl(version=110)` | archive URL `e110.rest.ensembl.org` |

For >5K rows, BioMart is the right tool. For real-time per-record lookups, REST.

## Common attribute selectors

| Attribute | Returns |
|---|---|
| `ensembl_gene_id` | Stable Ensembl Gene ID |
| `ensembl_gene_id_version` | With `.N` version suffix |
| `external_gene_name` | HGNC symbol (or species-equivalent) |
| `hgnc_id`, `hgnc_symbol` | HGNC permanent ID and symbol |
| `entrezgene_id` | NCBI Gene ID |
| `refseq_mrna`, `refseq_peptide` | RefSeq accessions |
| `uniprotswissprot`, `uniprotsptrembl` | UniProt accessions |
| `chromosome_name`, `start_position`, `end_position`, `strand` | Gene coordinates |
| `transcript_count`, `exon_count` | Counts |
| `biotype` | protein_coding, lncRNA, miRNA, etc. |
| `description` | Free-text gene description |
| `go_id`, `name_1006`, `namespace_1003` | GO term ID, name, namespace |

## Common filter selectors

| Filter | Constraint |
|---|---|
| `ensembl_gene_id` | List of Gene IDs |
| `external_gene_name` | List of symbols |
| `entrezgene_id` | List of NCBI Gene IDs |
| `chromosome_name` | One or more chromosomes |
| `start` / `end` | Coordinate range |
| `biotype` | One or more biotypes |
| `with_<source>` | Boolean: has cross-ref to `<source>` (e.g. `with_hpa` = has Human Protein Atlas) |

## Code patterns

### Bulk ID mapping: Ensembl Gene -> HGNC + RefSeq + UniProt

**Goal:** Convert 5,000 Ensembl Gene IDs to HGNC symbols, RefSeq mRNA accessions, and UniProt accessions in one query.

**Approach:** pybiomart query with three attributes; ID list as a filter; returns one TSV.

**Reference (pybiomart 0.9+, Ensembl release 110+):**
```python
from pybiomart import Server
import pandas as pd

server = Server(host='http://www.ensembl.org')
mart = server['ENSEMBL_MART_ENSEMBL']
ds = mart['hsapiens_gene_ensembl']

ensembl_ids = ['ENSG00000139618', 'ENSG00000141510', 'ENSG00000171862']  # ...up to 5K+

df = ds.query(
    attributes=['ensembl_gene_id', 'external_gene_name', 'hgnc_id',
                'refseq_mrna', 'uniprotswissprot'],
    filters={'ensembl_gene_id': ensembl_ids},
)
print(df.head())
# One row per (gene, cross-ref) pair; genes with multiple RefSeq mRNAs get multiple rows.
```

### Pull gene coordinate table for a chromosome

```python
df = ds.query(
    attributes=['ensembl_gene_id', 'external_gene_name', 'chromosome_name',
                'start_position', 'end_position', 'strand', 'biotype'],
    filters={'chromosome_name': '17', 'biotype': 'protein_coding'},
)
print(f'{len(df)} protein-coding genes on chr17')
```

### Bulk ortholog wide-table (human <-> mouse <-> zebrafish)

**Goal:** One TSV with human Ensembl ID, mouse ortholog Ensembl ID, zebrafish ortholog Ensembl ID per row.

**Approach:** Ortholog attributes from the human mart query both species' orthologs.

```python
df = ds.query(
    attributes=['ensembl_gene_id', 'external_gene_name',
                'mmusculus_homolog_ensembl_gene', 'mmusculus_homolog_orthology_type',
                'drerio_homolog_ensembl_gene', 'drerio_homolog_orthology_type'],
    filters={'chromosome_name': '17'},
)
# pybiomart columns use the mart display names, which can vary across releases.
# Resolve column names defensively rather than hardcoding strings:
mouse_type_col = next(c for c in df.columns if 'Mouse' in c and 'type' in c)
zebra_type_col = next(c for c in df.columns if 'Zebrafish' in c and 'type' in c)
df_one2one = df[(df[mouse_type_col] == 'ortholog_one2one') &
                (df[zebra_type_col] == 'ortholog_one2one')]
print(f'{len(df_one2one)} 1:1 orthologs across all three species on chr17')
```

### GO term annotation for a gene set

```python
df = ds.query(
    attributes=['ensembl_gene_id', 'external_gene_name',
                'go_id', 'name_1006', 'namespace_1003'],
    filters={'external_gene_name': ['TP53', 'BRCA1', 'MYC', 'EGFR']},
)
# Long format: one row per (gene, GO term) pair
```

### Version-pinned query (R biomaRt)

```r
# Reference: Bioconductor biomaRt 2.58+ | Verify API if version differs
library(biomaRt)

# Pin to release 110 for reproducibility
ensembl <- useEnsembl(biomart='genes', dataset='hsapiens_gene_ensembl', version=110)

# Or via host URL (for older or specific assemblies)
# ensembl <- useMart('ENSEMBL_MART_ENSEMBL',
#                     dataset='hsapiens_gene_ensembl',
#                     host='https://nov2020.archive.ensembl.org')

df <- getBM(
    attributes = c('ensembl_gene_id', 'external_gene_name', 'entrezgene_id',
                   'uniprotswissprot', 'refseq_mrna'),
    filters = 'ensembl_gene_id',
    values = c('ENSG00000139618', 'ENSG00000141510'),
    mart = ensembl
)
head(df)
```

### Discover attributes / filters programmatically

```python
# What attributes are available?
attrs = ds.attributes
ortho_attrs = [a for a in attrs if 'homolog' in a]
print(f'{len(ortho_attrs)} ortholog attributes; first 5: {ortho_attrs[:5]}')

# What filters?
filts = ds.filters
chrom_filts = [f for f in filts if 'chrom' in f]
```

## Failure modes

### Trying to pull >100K rows in one query
- **Trigger:** Query without any filter (e.g. all attributes for the whole human genome).
- **Mechanism:** BioMart times out or truncates on very large queries.
- **Symptom:** Empty or partial result.
- **Fix:** Chunk by chromosome; combine results client-side.

### No version pinning
- **Trigger:** `useMart('ensembl', ...)` without `version=`.
- **Mechanism:** Defaults to current release; gene model versions change quarterly.
- **Symptom:** Re-running a year later produces different rows.
- **Fix:** Pin with `useEnsembl(version=110)` or archive host URL.

### Multiple cross-refs balloon row count
- **Trigger:** Query for `ensembl_gene_id, refseq_mrna`; a gene with 10 RefSeq mRNAs produces 10 rows.
- **Mechanism:** BioMart joins on cross-refs; many-to-many produces row multiplication.
- **Symptom:** "Why do I have 50K rows for 5K input IDs?"
- **Fix:** Filter to one isoform per gene downstream; or use `ensembl_canonical` filter where available.

### Symbol-based filter misses HGNC renames
- **Trigger:** `filters={'external_gene_name': ['MARCH1']}` post-2020.
- **Mechanism:** HGNC renamed to MARCHF1; BioMart mirrors the new symbol.
- **Symptom:** Empty result for that gene.
- **Fix:** Filter by `ensembl_gene_id` or `hgnc_id`; these are stable.

### Multi-species mart query slow
- **Trigger:** Querying `mmusculus_homolog_ensembl_gene` for 30K human genes.
- **Mechanism:** Ortholog attributes are heavy; large queries take minutes.
- **Symptom:** Timeout or slow.
- **Fix:** Chunk by chromosome; or use Ensembl Compara REST for targeted lookups.

### REST loops where BioMart belongs
- **Trigger:** Loop of 5,000 Ensembl REST `/lookup/symbol` calls.
- **Mechanism:** Rate-limit cascade; 5,000 * 0.07s = 6 minutes just for the rate gate, plus HTTP overhead.
- **Symptom:** Slow; 429 errors.
- **Fix:** Switch to one BioMart query.

### Wrong mart for the question
- **Trigger:** Querying gene info from `ENSEMBL_MART_SNP`.
- **Mechanism:** SNP mart has variant attributes, not gene attributes.
- **Symptom:** Empty result or wrong fields.
- **Fix:** Discover marts with `server.marts`; pick `ENSEMBL_MART_ENSEMBL` for genes.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| Empty result | Wrong attribute / filter name | List with `ds.attributes` and `ds.filters` |
| Timeout on big query | No filter, too many rows | Chunk by chromosome |
| Drift between re-runs | No version pinning | `useEnsembl(version=110)` |
| Row count > expected | Many-to-many cross-ref joins | Filter to canonical isoform |
| Symbol filter returns nothing | HGNC rename | Filter by Ensembl ID or HGNC ID |
| Slow on ortholog wide-table | Multi-species join expensive | Chunk by chromosome |

## References

- Durinck S, Spellman PT, Birney E, Huber W. (2009) Mapping identifiers for the integration of genomic datasets with the R/Bioconductor package biomaRt. *Nat Protoc* 4:1184-1191.
- Kinsella RJ, Kahari A, Haider S, et al. (2011) Ensembl BioMarts: a hub for data retrieval across taxonomic space. *Database* 2011:bar030.
- Smedley D, Haider S, Durinck S, et al. (2015) The BioMart community portal: an innovative alternative to large, centralized data repositories. *Nucleic Acids Res* 43:W589-W598.
- pybiomart documentation: https://github.com/jrderuiter/pybiomart

## Related Skills

- ensembl-rest - Per-record Ensembl queries (BioMart's complement)
- ortholog-inference - Compara ortholog calls with confidence semantics
- uniprot-access - UniProt ID mapping (preferred for UniProt-rooted lookups and obsolete-accession resolution; BioMart is preferred for Ensembl-rooted batches >5K)
- ncbi-datasets-cli - NCBI-side bulk path for genome / gene data
- entrez-search - NCBI alternative for non-Ensembl queries
<!-- END FILE: database-access/biomart-queries/SKILL.md -->

## 子目录：database-access/blast-searches

<!-- BEGIN FILE: database-access/blast-searches/SKILL.md -->
---
name: bio-blast-searches
description: Run remote BLAST searches against NCBI servers using Biopython Bio.Blast.NCBIWWW. Use when identifying unknown sequences, finding homologs, picking the correct BLAST program (blastn/blastp/blastx/tblastn/tblastx/psiblast/megablast/dc-megablast), interpreting Karlin-Altschul E-values, avoiding the max_target_seqs trap (Shah 2019), choosing composition-based statistics, or limiting searches by organism. Covers RID lifecycle, database choice (nt/nr/refseq_select/swissprot), word-size and CBS taxonomy.
tool_type: python
primary_tool: Bio.Blast.NCBIWWW
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, NCBI BLAST+ 2.15+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(Bio.Blast.NCBIWWW.qblast)` to check signatures
- CLI: `blastn -version` then `blastn -help`

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# BLAST Searches (Remote)

**"Find similar sequences in NCBI's database"** -> Submit a query to NCBI's remote BLAST servers; receive a Request ID (RID); poll for completion; parse the XML hit table. Best for one-off identification of a few sequences. For >50 sequences, switch to `local-blast` or DIAMOND/MMseqs2 in `remote-homology`.

The two most consequential decisions: **which program** (defines query+target molecule types and word-size defaults) and **which database** (defines the search space and therefore E-value baselines). The third most important: do NOT misuse `max_target_seqs` -- it is an early-termination heuristic, not a "give me the top N hits" filter (Shah et al. 2019).

- Python: `NCBIWWW.qblast(program, db, sequence)` + `NCBIXML.read(handle)` (BioPython)
- CLI: `blastn -remote -db nt -query seq.fa -out hits.xml -outfmt 5` (BLAST+)
- Web: https://blast.ncbi.nlm.nih.gov/Blast.cgi (RID lookup)

## Required Setup

```python
from Bio.Blast import NCBIWWW, NCBIXML
from Bio import SeqIO
```

No API key needed for remote BLAST itself, but NCBI's general rate-limit ethic still applies -- one search at a time, polite waiting, no parallelism.

## Program decision (query vs database molecule)

| Program | Query | Target | Word size default | Use case |
|---|---|---|---|---|
| `blastn` | DNA | DNA | 11 | General DNA similarity |
| `megablast` | DNA | DNA | 28 | High-identity DNA (>=95%) -- PCR primer hits, contamination |
| `dc-megablast` | DNA | DNA | 11 (discontiguous) | Cross-species mRNA (sensitive, gapped) |
| `blastp` | Protein | Protein | 3 (6 also valid) | General protein homology |
| `blastx` | DNA | Protein | 3 | Translated DNA query vs protein DB; ORF discovery |
| `tblastn` | Protein | DNA | 3 | Protein query vs translated DB; find unannotated CDS |
| `tblastx` | DNA | DNA | 3 (both translated) | Most expensive; deep cross-species coding similarity |
| `psiblast` | Protein | Protein | 3 | Iterative PSSM-based remote homology -- see `remote-homology` |

**The misuse to avoid:** using default `blastn` (word=11) for cross-species DNA where `dc-megablast` is the right tool. Or using `megablast` (word=28) for cross-species homology where it will miss every divergent hit. The most-misused BLAST parameter according to literature.

## Database decision (search space)

| Database (`db=`) | Content | Size (2026 approx) | Stable for reproducibility? |
|---|---|---|---|
| `nt` | Non-redundant nucleotide (all GenBank+EMBL+DDBJ) | ~250 GB | NO -- changes daily |
| `nr` | Non-redundant protein | ~300 GB | NO -- changes daily |
| `refseq_select` | One curated rep per species (RNA + protein) | small | YES -- versioned releases |
| `refseq_rna` | RefSeq mRNA | ~10 GB | YES |
| `refseq_protein` | RefSeq protein | small | YES |
| `swissprot` | UniProt Swiss-Prot (reviewed) | small | YES -- monthly releases |
| `pdb` | Protein structures | small | YES |
| `refseq_genomic` | RefSeq genomic | huge | YES |
| `env_nr` / `env_nt` | Environmental (metagenomic) | huge | YES |

**For publication reproducibility, never search `nt` or `nr`** without recording the snapshot date and ideally archiving a frozen copy. Default to `refseq_select` for any cross-species homology question; switch to `nt`/`nr` only when curated coverage is insufficient.

## E-value interpretation (Karlin-Altschul)

E-value = K * m * n * exp(-lambda * S), where m = effective query length, n = effective database size, lambda and K are scoring-matrix-dependent constants (Karlin & Altschul 1990 PNAS 87:2264).

| E-value | Bit-score (BLOSUM62, protein) | Interpretation |
|---|---|---|
| < 1e-50 | > 200 | Strong; almost certainly homologous |
| 1e-50 to 1e-10 | 100-200 | Significant; likely homolog |
| 1e-10 to 1e-3 | 50-100 | Marginal; check identity + coverage |
| 0.01 to 10 | 30-50 | Possible remote homolog; needs profile method |
| > 10 | < 30 | Random; not meaningful |

**Key implication of E = K * m * n * exp(-lambda * S):** the same alignment against a 100x larger database has a 100x larger E-value. Cross-database E-value comparison is meaningless. Bit-score is database-size normalized and is the right cross-database metric.

For protein remote homology where E is marginal (10^-3 to 10^-1), reach for profile methods: PSI-BLAST, jackhmmer, HHblits, or Foldseek -- see `remote-homology` skill.

## Composition-Based Statistics (CBS)

Compositional bias inflates significance for low-complexity proteins. The CBS modes (Yu et al. 2006 *Nucleic Acids Res* 34:5966):

| `composition_based_statistics` | Mode | Use when |
|---|---|---|
| 0 | Off | Almost never |
| 1 | F&S 2002 score adjustment | Legacy compatibility |
| 2 | Yu&Altschul 2005 conditional score adjustment | **Default since BLAST+ 2.2.17** -- correct for most cases |
| 3 | Universal statistics | Short queries (< 30 aa) where mode 2 over-corrects |

For protein queries under 30 aa, switch to CBS=3. For protein with known compositional bias (e.g. coiled-coil regions, signal peptides), CBS=2 is appropriate but consider hard-masking with SEG.

## The `max_target_seqs` trap

**The misuse**: `max_target_seqs=10` is interpreted as "return the 10 most significant hits". It is not. The flag is an **early termination** parameter that affects which hits the search ever considers, not which it ultimately reports (Shah N, Nute MG, Warnow T, Pop M. (2019) Misunderstood parameter of NCBI BLAST impacts the correctness of bioinformatics workflows. *Bioinformatics* 35:1613-1614).

**Consequences:**
- Setting `max_target_seqs=10` can return entirely different hits than `max_target_seqs=500` then filtering to top 10 by E-value.
- The "top 10" by E-value as reported may not be the actual top 10.

**Correct pattern:** set `hitlist_size` (Bio.Blast parameter name) large (1000+), then post-filter to the top N by E-value or bit-score in Python.

## Word size, gap costs, and matrix

| Search | Word size | Matrix (protein) | Gap (open, extend) |
|---|---|---|---|
| megablast (high identity DNA) | 28 | n/a | 0, 0 (linear) |
| blastn (sensitive DNA) | 11 | n/a | 5, 2 |
| blastp default | 3 | BLOSUM62 | 11, 1 |
| blastp distant | 2 | BLOSUM45 | 14, 2 |
| Short peptides (<30 aa) | 2 | PAM30 or BLOSUM45 | 9, 1 |

For very short query proteins (e.g. proteomics-identified peptides), BLOSUM45 + word=2 + PAM30 substitution matrix is more sensitive than the default. Use `matrix='PAM30'` for searches against `swissprot`.

## RID lifecycle

| Phase | Server state | Client action |
|---|---|---|
| Submit | RID created, queued | NCBIWWW.qblast() returns handle |
| Running | Queue + compute | Poll status |
| Done | RID + results retained | Fetch XML |
| Expired | RID purged | 24-36h after completion |

`NCBIWWW.qblast()` handles polling internally with a fixed retry interval. For long-running searches (>5 min) or batches, submit and capture the RID, then poll independently to avoid blocking. The RID is visible at `https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Get&RID=...` for 24-36 hours.

## Code patterns

### Standard remote BLASTN with reproducible parameters

**Goal:** Run BLASTN with explicit, paper-quality parameters.

**Approach:** Specify program, database (refseq_select for stability), word size, expect, and a large hitlist_size to dodge the max_target_seqs trap.

**Reference (BioPython 1.83+):**
```python
from Bio.Blast import NCBIWWW, NCBIXML

handle = NCBIWWW.qblast(
    program='blastn',
    database='refseq_select_rna',
    sequence=query_seq,
    expect=1e-10,
    word_size=11,
    hitlist_size=500,  # large; filter top-N downstream
    format_type='XML',
)
record = NCBIXML.read(handle); handle.close()
top10 = sorted(record.alignments, key=lambda a: a.hsps[0].expect)[:10]
```

### Protein search with organism restriction

**Goal:** Find mammalian homologs of a query protein in Swiss-Prot.

**Approach:** `entrez_query` filters the BLAST search space pre-execution; faster and more meaningful E-values than post-filtering.

**Reference (BioPython 1.83+):**
```python
handle = NCBIWWW.qblast(
    program='blastp',
    database='swissprot',
    sequence=protein_seq,
    entrez_query='Mammalia[Organism]',
    expect=1e-5,
    composition_based_statistics=2,
    hitlist_size=200,
)
record = NCBIXML.read(handle); handle.close()
```

### Short peptide search

```python
handle = NCBIWWW.qblast(
    program='blastp',
    database='swissprot',
    sequence=peptide_seq,  # < 30 aa
    matrix_name='PAM30',
    word_size=2,
    expect=1000,  # short queries need permissive cutoff
    composition_based_statistics=3,
    hitlist_size=100,
)
```

### Save XML for re-parsing

```python
handle = NCBIWWW.qblast('blastn', 'refseq_select_rna', query)
with open('blast.xml', 'w') as f:
    f.write(handle.read())
handle.close()

with open('blast.xml') as f:
    record = NCBIXML.read(f)
```

### Hit extraction with identity + coverage filtering

**Goal:** Return structured top hits with biological metrics, not just E-values.

**Approach:** Walk alignments + first HSP; compute identity and query coverage as fractions; sort by bit-score (database-size invariant) not E-value.

**Reference (BioPython 1.83+):**
```python
def top_hits(record, min_identity=0.5, min_coverage=0.7, top_n=10):
    qlen = record.query_length
    hits = []
    for aln in record.alignments:
        hsp = aln.hsps[0]
        ident = hsp.identities / hsp.align_length
        cov = hsp.align_length / qlen
        if ident >= min_identity and cov >= min_coverage:
            hits.append({
                'accession': aln.accession,
                'title': aln.title,
                'evalue': hsp.expect,
                'bits': hsp.bits,
                'identity': ident,
                'coverage': cov,
            })
    return sorted(hits, key=lambda h: -h['bits'])[:top_n]
```

### Programmatic RID polling for long jobs

```python
import time

handle = NCBIWWW.qblast('tblastn', 'nr', query, hitlist_size=500, format_type='XML')
# Bio.Blast handles polling internally; for explicit control use the REST API directly
# or save and re-parse the RID URL
```

## Failure modes

### `max_target_seqs` misinterpretation
- **Trigger:** Setting `hitlist_size=10` and assuming top 10 by E-value.
- **Mechanism:** It's an early-termination param; can miss legitimate top hits.
- **Symptom:** Different "top 10" between hitlist=10 and hitlist=500 filtered.
- **Fix:** Always set `hitlist_size=500+` and post-filter; cite Shah 2019.

### Cross-database E-value comparison
- **Trigger:** Comparing E from a `nt` search against E from a `swissprot` search.
- **Mechanism:** E scales linearly with database size; comparison is meaningless.
- **Symptom:** Misleading rankings between two analyses.
- **Fix:** Compare bit-scores instead, or set the same database for both.

### Megablast for cross-species
- **Trigger:** Default `megablast` (word=28) on a cross-species DNA query.
- **Mechanism:** Word size 28 requires 28-nt exact match to seed; cross-species mRNA has too much divergence.
- **Symptom:** Zero hits or only hits to the same species.
- **Fix:** Use `dc-megablast` (discontiguous) or `blastn` with word=11.

### Reproducibility loss against `nt`/`nr`
- **Trigger:** Manuscript says "BLASTed against nt"; reviewer re-runs 3 weeks later.
- **Mechanism:** Databases change daily; new genomes deposited.
- **Symptom:** Different hit set, different paper conclusions.
- **Fix:** Use `refseq_select` for reproducibility, or record snapshot date + archive subset.

### Server timeout on large queries
- **Trigger:** Multi-megabase query or batch submission.
- **Mechanism:** Remote BLAST has a per-query compute budget.
- **Symptom:** Job stuck in queue, eventually fails.
- **Fix:** Split into smaller queries; or switch to `local-blast` / DIAMOND / MMseqs2.

### Compositional bias inflates E
- **Trigger:** Protein query with low-complexity region (coiled-coil, signal peptide).
- **Mechanism:** Default CBS=2 handles most cases, but extreme bias still inflates scores.
- **Symptom:** Many "significant" hits to unrelated low-complexity proteins.
- **Fix:** Confirm CBS=2 is on; consider hard-masking with `filter='S'` (SEG).

### Empty FASTA defline submitted
- **Trigger:** Sending `sequence` as a raw string without `>id\n`.
- **Mechanism:** BLAST treats as anonymous query; some downstream parsers misbehave.
- **Symptom:** Hits returned but `record.query` is None.
- **Fix:** Always pass FASTA with a defline; or pass a `SeqRecord`.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| Stuck > 5 min | Large query or busy queue | Submit RID, poll separately; or use local |
| URLError / timeout | Network or NCBI maintenance | Retry with backoff; status at status.ncbi.nlm.nih.gov |
| No hits | Wrong program / database type | Verify query and DB molecule types match |
| Empty XML | RID expired | Re-submit; RIDs purge after 24-36h |
| 1000s of low-complexity hits | CBS disabled or extreme bias | CBS=2; consider SEG filter |
| Cross-DB E mismatch | Comparing E across DBs | Use bit-score instead |

## References

- Altschul SF, Gish W, Miller W, Myers EW, Lipman DJ. (1990) Basic local alignment search tool. *J Mol Biol* 215:403-410.
- Karlin S, Altschul SF. (1990) Methods for assessing the statistical significance of molecular sequence features by using general scoring schemes. *Proc Natl Acad Sci USA* 87:2264-2268.
- Altschul SF, Madden TL, Schaffer AA, Zhang J, Zhang Z, Miller W, Lipman DJ. (1997) Gapped BLAST and PSI-BLAST: a new generation of protein database search programs. *Nucleic Acids Res* 25:3389-3402.
- Yu YK, Gertz EM, Agarwala R, Schaffer AA, Altschul SF. (2006) Retrieval accuracy, statistical significance and compositional similarity in protein sequence database searches. *Nucleic Acids Res* 34:5966-5973.
- Shah N, Nute MG, Warnow T, Pop M. (2019) Misunderstood parameter of NCBI BLAST impacts the correctness of bioinformatics workflows. *Bioinformatics* 35:1613-1614.
- Camacho C, Coulouris G, Avagyan V, Ma N, Papadopoulos J, Bealer K, Madden TL. (2009) BLAST+: architecture and applications. *BMC Bioinformatics* 10:421.

## Related Skills

- local-blast - Faster, unlimited local BLAST+ pipelines and database build
- remote-homology - PSI-BLAST, jackhmmer, HHblits, MMseqs2, DIAMOND, Foldseek for distant homology
- ortholog-inference - Reciprocal best hit, OrthoFinder, OMA for orthology
- sequence-io/read-sequences - Load query sequences from FASTA
- entrez-fetch - Fetch full records for BLAST hits
<!-- END FILE: database-access/blast-searches/SKILL.md -->

## 子目录：database-access/ensembl-rest

<!-- BEGIN FILE: database-access/ensembl-rest/SKILL.md -->
---
name: bio-ensembl-rest
description: Query the Ensembl REST API for gene/transcript/protein lookup, sequence retrieval, comparative genomics (Compara), variant effect prediction (VEP), regulatory features, and cross-species ortholog/paralog calls. Use when pulling Ensembl-native data (Ensembl Gene IDs, version-pinned releases, archive endpoints for reproducibility), gene/transcript/exon structure with stable IDs, or VEP for variant annotation. Encodes the 15 req/sec rate limit, archive (e110.rest.ensembl.org) for reproducibility, Ensembl divisions (vertebrates / plants / fungi / metazoa / bacteria), and the symbol-vs-ID stability problem.
tool_type: python
primary_tool: requests
---

## Version Compatibility

Reference examples tested with: requests 2.31+, Ensembl REST API (release 110+); Ensembl release schedule is roughly quarterly

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show requests`
- API surface: check release notes at https://rest.ensembl.org

Each Ensembl release has an archive REST endpoint (e.g. `https://e110.rest.ensembl.org`) for reproducibility.

# Ensembl REST

**"Pull Ensembl-native gene / transcript / variant data programmatically"** -> Ensembl REST is distinct from NCBI Entrez and BioMart. It is the right answer for: stable Ensembl IDs, transcript / exon structure, VEP (Variant Effect Predictor) annotation, Compara orthologs at vertebrate scale, regulatory feature annotation, and any workflow rooted in Ensembl's coordinate system.

Two facts dominate Ensembl REST work: (1) the **15 req/sec / 55,000 req/hour rate limit** — high enough for hundreds of queries, low enough that bulk work (>5,000) belongs in BioMart instead; (2) **versioned archive endpoints** — `https://e110.rest.ensembl.org` pins to release 110 for reproducibility, while `https://rest.ensembl.org` follows the current release.

- Python: `requests.get('https://rest.ensembl.org/...')`
- Web: https://rest.ensembl.org (interactive doc with try-it-now)
- R: `biomaRt` for bulk (see `biomart-queries`); REST via `httr`

## Required Setup

```python
import requests
import time

BASE = 'https://rest.ensembl.org'
HEADERS = {'Accept': 'application/json'}
SLEEP = 0.07   # 15 req/sec ceiling
```

No API key required. Respect `Retry-After` header on 429.

## Ensembl divisions

Ensembl is divided by clade. Different REST hosts:

| Division | Host | Scope |
|---|---|---|
| Vertebrates | https://rest.ensembl.org | Human, mouse, fish, etc. (the "main" Ensembl) |
| Plants | https://rest.ensembl.org (plants division also accessible) | Arabidopsis, rice, etc. via Ensembl Genomes |
| Fungi | https://rest.ensemblgenomes.org | Yeasts, Aspergillus, etc. |
| Metazoa | https://rest.ensemblgenomes.org | Insects, nematodes, etc. |
| Bacteria | https://rest.ensemblgenomes.org | Limited (most bacteria in NCBI) |

For non-vertebrate work, check `ensemblgenomes.org` mirrors. As of 2024, Ensembl Genomes was being consolidated; check current host.

## Version pinning

| URL | Behavior |
|---|---|
| `https://rest.ensembl.org` | Current release (rolling) |
| `https://e110.rest.ensembl.org` | Pinned to release 110 |
| `https://e111.rest.ensembl.org` | Pinned to release 111 |
| `https://grch37.rest.ensembl.org` | Pinned to GRCh37 (legacy assembly) |

For any published analysis, pin the release. Ensembl releases change gene model versions, exon coordinates, and transcript annotations — re-running a pipeline a year later against the live endpoint may produce different results.

## Major endpoint groups

| Group | Example | Purpose |
|---|---|---|
| Lookup | `/lookup/symbol/human/BRCA1` | Resolve symbol or ID to stable record |
| Sequence | `/sequence/id/{id}` | DNA/protein sequence for ID |
| Cross References | `/xrefs/symbol/human/BRCA1` | Cross-refs to other DBs |
| Homology / Compara | `/homology/symbol/human/BRCA1` | Orthologs and paralogs |
| Gene Tree | `/genetree/id/{tree_id}` | Compara gene tree |
| VEP | `/vep/human/region/{region}/{allele}` | Variant effect prediction |
| Overlap | `/overlap/id/{id}` or `/overlap/region/{region}` | Genes/regulatory in interval |
| Regulatory | `/regulatory/species/{species}/feature/{id}` | Regulatory features |
| Variant | `/variation/{species}/{id}` | dbSNP / 1000G / ClinVar via Ensembl |
| LD | `/ld/{species}/pairwise/{var1}/{var2}` | LD between variants |
| GA4GH | `/ga4gh/...` | GA4GH-compliant subset |

Full reference: https://rest.ensembl.org (interactive).

## The symbol-vs-ID stability problem

Gene symbols are unstable (MARCH1 -> MARCHF1 in 2020 due to Excel autocorrect; SEPT* family also renamed). Ensembl Gene IDs (ENSG...) are stable across releases when the gene model is preserved.

**Best practice:**
1. Resolve symbol -> Ensembl ID once at pipeline start: `/lookup/symbol/{species}/{symbol}`.
2. Persist the Ensembl ID.
3. Run downstream queries by ID, not symbol.

Symbol-based endpoints are convenient for interactive use; ID-based endpoints are for reproducible pipelines.

## Rate-limit math

| Limit | Value |
|---|---|
| Burst | 15 req/sec |
| Hourly | 55,000 req/hour |
| Concurrent | Not enforced; courtesy 1-2 |

Respect `Retry-After` header on HTTP 429. For >5,000 queries, switch to BioMart bulk export (see `biomart-queries`) — BioMart has separate, more permissive limits.

## VEP (Variant Effect Predictor)

VEP via REST is the right call for ad hoc variant annotation. For batch variant annotation (>1000 variants), download VEP and run locally (`variant-calling/variant-annotation` skill).

REST modes:
- `/vep/{species}/region/{region}/{allele}` — single variant by coordinate
- `/vep/{species}/id/{variant_id}` — by dbSNP / Ensembl variant ID
- `/vep/{species}/hgvs/{hgvs_notation}` — by HGVS notation

VEP returns rich annotation: consequence (missense, synonymous, intron), SIFT/PolyPhen scores, gnomAD frequencies (if available), ClinVar significance.

## Compara homology

Compara orthology calls via Ensembl REST are covered in detail in `ortholog-inference` (database-access view). The relevant endpoint:

- `/homology/symbol/{species}/{symbol}` — all orthologs across Ensembl species
- `/homology/id/{ensembl_id}` — same, by ID
- `?target_species=` to restrict to one target
- `?type=orthologues` or `paralogues` to filter

## Code patterns

### Symbol -> stable Ensembl Gene ID

**Goal:** Resolve a gene symbol to its current Ensembl Gene ID once, then use the ID for all downstream queries.

**Approach:** `/lookup/symbol/{species}/{symbol}` returns the canonical record.

**Reference (requests 2.31+):**
```python
import requests
import time

BASE = 'https://rest.ensembl.org'
HEADERS = {'Accept': 'application/json'}


def get_with_retry(url, params=None, max_retries=3):
    for attempt in range(max_retries):
        r = requests.get(url, params=params, headers=HEADERS)
        if r.status_code == 429:
            time.sleep(int(r.headers.get('Retry-After', '5')))
            continue
        r.raise_for_status()
        return r
    raise RuntimeError(f'Failed after {max_retries} retries')


def symbol_to_ensembl(species, symbol):
    r = get_with_retry(f'{BASE}/lookup/symbol/{species}/{symbol}')
    return r.json()


info = symbol_to_ensembl('human', 'BRCA1')
print(f'  Ensembl Gene ID: {info["id"]}')
print(f'  Biotype:         {info["biotype"]}')
print(f'  Chromosome:      {info["seq_region_name"]}:{info["start"]}-{info["end"]}')
print(f'  Strand:          {info["strand"]}')
```

### Sequence retrieval by Ensembl ID

```python
def get_sequence(ensembl_id, seq_type='cdna'):
    '''seq_type: cdna, cds, protein, genomic'''
    r = get_with_retry(f'{BASE}/sequence/id/{ensembl_id}',
                       params={'type': seq_type, 'content-type': 'application/json'})
    return r.json()


prot = get_sequence('ENSG00000139618', seq_type='protein')
print(f'  Length: {len(prot["seq"])} aa')
```

### Overlap: what genes are in this region

```python
def genes_in_region(species, region):
    '''region as "chr:start-end" e.g. "17:43000000-44000000".'''
    r = get_with_retry(f'{BASE}/overlap/region/{species}/{region}',
                       params={'feature': 'gene'})
    return r.json()


for g in genes_in_region('human', '17:43000000-43200000'):
    print(f'  {g["external_name"]:<12} {g["id"]} {g["biotype"]:<20} {g["start"]}-{g["end"]}')
```

### VEP for a single variant

**Goal:** Get full annotation for a variant by coordinate.

**Approach:** `/vep/{species}/region/{region}/{allele}` returns transcript consequences, SIFT/PolyPhen, frequencies.

**Reference (Ensembl REST release 110+):**
```python
def vep_region(species, region, allele):
    r = get_with_retry(f'{BASE}/vep/{species}/region/{region}/{allele}')
    return r.json()


# BRCA1 missense variant in GRCh38 coordinates (rest.ensembl.org defaults to GRCh38);
# for GRCh37 coords use https://grch37.rest.ensembl.org instead.
results = vep_region('human', '17:43044295-43044295:1', 'A')
if results:
    for tc in results[0].get('transcript_consequences', [])[:5]:
        print(f'  {tc["gene_symbol"]:<8} {tc["consequence_terms"]}')
        if 'sift_prediction' in tc:
            print(f'    SIFT: {tc["sift_prediction"]} ({tc.get("sift_score", "?")})')
```

### Compara orthologs (Compara via REST)

```python
def orthologs(species, symbol, target_species=None):
    params = {'type': 'orthologues'}
    if target_species:
        params['target_species'] = target_species
    r = get_with_retry(f'{BASE}/homology/symbol/{species}/{symbol}', params=params)
    return r.json()['data'][0]['homologies']


for o in orthologs('human', 'BRCA1', target_species='mouse'):
    print(f'  {o["target"]["species"]:<15} {o["target"]["id"]}  type={o["type"]}  confidence={o.get("confidence")}')
```

### Batch lookup with rate-limit handling

```python
def batch_symbols(species, symbols):
    out = {}
    for sym in symbols:
        try:
            out[sym] = symbol_to_ensembl(species, sym)
        except requests.HTTPError as e:
            out[sym] = {'error': str(e)}
        time.sleep(0.07)  # 15 req/sec ceiling
    return out
```

### Archive endpoint for reproducibility

```python
# Pin to release 110
ARCHIVE = 'https://e110.rest.ensembl.org'
r = requests.get(f'{ARCHIVE}/lookup/symbol/human/BRCA1', headers={'Accept': 'application/json'})
print(r.json()['id'])
# Re-runs against e110 in 2030 will return the same Gene ID even if the live release has moved on.
```

### LD between two variants

```python
def ld_pairwise(species, var1, var2, population='1000GENOMES:phase_3:CEU'):
    r = get_with_retry(f'{BASE}/ld/{species}/pairwise/{var1}/{var2}',
                       params={'population_name': population})
    return r.json()
```

## Failure modes

### Symbol-based pipeline breaks on HGNC rename
- **Trigger:** `/lookup/symbol/human/MARCH1` after the 2020 rename.
- **Mechanism:** HGNC renamed Excel-autocorrect-affected genes; Ensembl mirrors the rename.
- **Symptom:** 404 or wrong gene returned.
- **Fix:** Resolve symbol to Ensembl Gene ID once at pipeline start; use ID downstream.

### No version pinning, results drift
- **Trigger:** Re-running a pipeline against `https://rest.ensembl.org` a year later.
- **Mechanism:** Live endpoint follows current release; gene models update quarterly.
- **Symptom:** Different transcript coordinates, exon counts, sometimes Gene ID changes.
- **Fix:** Pin to an archive endpoint (`https://e110.rest.ensembl.org`) for reproducibility.

### Rate-limit cascade
- **Trigger:** Loop of 5,000 REST calls without sleep.
- **Mechanism:** 15 req/sec ceiling; 429 with Retry-After.
- **Symptom:** Pipeline stalls; cascade of failures.
- **Fix:** Sleep 0.07s between calls; honor Retry-After; for >5K queries use BioMart bulk export.

### VEP for bulk variants
- **Trigger:** VEP REST for 100K variants.
- **Mechanism:** REST is per-variant; rate-limit makes this infeasible.
- **Symptom:** Days-long runtime; many 429s.
- **Fix:** Download VEP and run locally (`variant-calling/variant-annotation` skill); reserve REST for ad hoc <1K variants.

### Wrong species name
- **Trigger:** Using `Homo_sapiens` instead of `human`, or arbitrary capitalization.
- **Mechanism:** Ensembl species names are lowercase with underscores or common names; case matters.
- **Symptom:** 404 or empty result.
- **Fix:** Use `https://rest.ensembl.org/info/species` to enumerate valid names.

### Non-vertebrate species not in vertebrate host
- **Trigger:** Querying Arabidopsis on `rest.ensembl.org`.
- **Mechanism:** Plants live in Ensembl Genomes (`rest.ensemblgenomes.org`) as of 2024 (consolidation ongoing).
- **Symptom:** 404 or species not recognized.
- **Fix:** Check the right division host; use the lookup endpoint `info/divisions` to confirm.

### Archive endpoint TLS / connectivity
- **Trigger:** Older archive endpoints (e80, e90) gradually decommissioned.
- **Mechanism:** Very old archives are retired ~5 years after release.
- **Symptom:** DNS failure or 503.
- **Fix:** Check the current archive list at https://www.ensembl.org/info/website/archives/index.html.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `404` on symbol lookup | HGNC rename or wrong species | Resolve to Ensembl ID; check species code |
| HTTP 429 | Rate limit | Sleep per Retry-After; cap to 15 req/sec |
| Different results 6 months later | No version pinning | Use archive endpoint (`eXX.rest.ensembl.org`) |
| `404` on non-vertebrate | Wrong host division | Switch to `rest.ensemblgenomes.org` |
| VEP infeasible bulk | REST is per-variant | Local VEP for bulk |
| Old archive 503 | Decommissioned | Use a current archive release |

## References

- Yates AD, Allen J, Amode RM, et al. (2022) Ensembl Genomes 2022: an expanding genome resource for non-vertebrates. *Nucleic Acids Res* 50:D996-D1003.
- Martin FJ, Amode MR, Aneja A, et al. (2023) Ensembl 2023. *Nucleic Acids Res* 51:D933-D941.
- McLaren W, Gil L, Hunt SE, et al. (2016) The Ensembl Variant Effect Predictor. *Genome Biol* 17:122.
- Yates A, Beal K, Keenan S, et al. (2015) The Ensembl REST API: Ensembl data for any language. *Bioinformatics* 31:143-145.

## Related Skills

- biomart-queries - Ensembl BioMart for bulk (>5K) ID mapping
- ortholog-inference - Compara orthologs via Ensembl REST and other resources
- uniprot-access - Cross-reference Ensembl IDs in UniProt entries
- variant-calling/variant-annotation - Local VEP for bulk variant annotation
- ncbi-datasets-cli - NCBI alternative for genome / gene data
- entrez-search - NCBI alternative for non-Ensembl queries
<!-- END FILE: database-access/ensembl-rest/SKILL.md -->

## 子目录：database-access/entrez-fetch

<!-- BEGIN FILE: database-access/entrez-fetch/SKILL.md -->
---
name: bio-entrez-fetch
description: Retrieve records from NCBI databases using Biopython Bio.Entrez (EFetch, ESummary). Use when downloading sequences, fetching GenBank/GenPept records, getting document summaries, parsing nested XML, navigating GI deprecation, choosing between rettype+retmode combinations, and parsing into Biopython SeqRecord/SwissProt objects. Covers nucleotide, protein, gene, pubmed, sra, gds, taxonomy, snp, clinvar.
tool_type: python
primary_tool: Bio.Entrez
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, Entrez Direct 21.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(Bio.Entrez.efetch)` to check signatures
- CLI: `efetch -version` then `efetch -help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Entrez Fetch

**"Download a record by accession from NCBI"** -> EFetch returns the full record content in a chosen format (FASTA, GenBank, XML, MEDLINE, etc.). ESummary returns a lightweight "docsum" object — much faster when only metadata is needed.

The agent's first decision is always: does this workflow need the full record, or just metadata? ESummary is 5-10x cheaper than EFetch for the equivalent record set. For "tell me the organism, length, and definition line for 10,000 accessions", ESummary wins by an order of magnitude.

- Python: `Entrez.efetch(db=..., id=..., rettype=..., retmode=...)` (BioPython)
- CLI: `efetch -db nucleotide -id NM_007294 -format gb` (Entrez Direct, NBK179288)
- R: `entrez_fetch(db=..., id=..., rettype=...)` (rentrez)

## Required Setup

```python
from Bio import Entrez, SeqIO
Entrez.email = 'researcher@institution.edu'
Entrez.api_key = 'optional_api_key'  # raises rate to 10 req/sec
```

## Decision matrix: rettype + retmode per database

The combinations are not orthogonal — each (db, rettype, retmode) triple is enabled or disabled by NCBI server-side. Wrong combinations return either silent empty responses or HTTP 400. The triples below are the safe, current set.

### nucleotide / protein

| rettype | retmode | Returns | Use when |
|---|---|---|---|
| `fasta` | `text` | FASTA | Just need sequence + defline |
| `gb` (nuc) / `gp` (prot) | `text` | Full flat file | Need annotations, features, references |
| `gbwithparts` | `text` | GB with CONTIG sequences inlined | Whole-genome shotgun assemblies; default `gb` returns CONTIG records requiring a chase to resolve |
| `fasta_cds_na` | `text` | CDS-only nucleotide | Extract coding regions from annotated GB |
| `fasta_cds_aa` | `text` | CDS-translated AA | Get translated proteins from GB record in one call |
| `xml` (== gb XML) | `xml` | INSDSeq XML | Programmatic parsing; the schema is unversioned and shifts |
| `acc` | `text` | Accession.version per line | Just resolve UID -> accession |
| `seqid` | `text` | Internal seq-id | Rarely needed |

### pubmed

| rettype | retmode | Returns | Use when |
|---|---|---|---|
| `abstract` | `text` | Title + authors + abstract | Reading abstracts |
| `medline` | `text` | MEDLINE flat | Parsing with `Bio.Medline` |
| `xml` | `xml` | Full PubMed XML | Programmatic — get MeSH, grants, PMC link |
| (omitted) | (omitted) | Defaults to XML | EFetch default for pubmed is XML — pass `retmode='xml'` explicitly for clarity |

### gene

| rettype | retmode | Returns | Use when |
|---|---|---|---|
| `gene_table` | `text` | Tabular per-transcript layout | Exon coordinates |
| `xml` | `xml` | Full Entrez Gene XML | Everything else — name, synonyms, GeneRIFs, locus |

### sra

| rettype | retmode | Returns | Use when |
|---|---|---|---|
| `runinfo` | `text` | CSV of run metadata | Convert SRA UID -> SRR accession + Run metrics |
| `xml` | `xml` | Full SRA XML hierarchy | Need BioSample/BioProject linkage in one call |

### taxonomy

| rettype | retmode | Returns | Use when |
|---|---|---|---|
| `xml` | `xml` (default) | TaxNode XML | Lineage, parent, common name |

### gds (GEO)

| rettype | retmode | Returns | Use when |
|---|---|---|---|
| (default — no rettype) | `text` | Plaintext SOFT-style summary | Quick metadata; for full series matrix go to FTP |

EFetch for GDS records is intentionally minimal — full GEO downloads go via the FTP mirror or `GEOparse`. See `geo-data` skill.

## GI deprecation (still bites in 2026)

NCBI stopped issuing new GI numbers for major nucleotide/protein submissions starting 2017. Records submitted after the cutoff have only `accession.version` identifiers. Many older scripts assume `id=<numeric_gi>`; passing a modern accession string also works, but mixing the two in one comma-separated id list is the bug.

**Rules:**
- For modern code, always pass `accession.version` strings.
- A bare accession without `.version` resolves to the latest version — fine for exploratory work, dangerous for reproducibility.
- Old `id=12345` GI lookups still work for records issued before 2017, but a search returning a UID that looks like a GI may actually be the legacy GI for an old record — assume UID is an opaque identifier.
- EFetch accepts comma-separated IDs of mixed types but the URL has a ~2000 char practical limit; chunk large ID lists into batches.

## ESummary vs EFetch triage

| Need | ESummary | EFetch (text) | EFetch (xml) |
|---|---|---|---|
| Title, organism, length | yes | overkill | overkill |
| Authors of a PubMed article | yes | yes | yes |
| Full abstract text | no | `rettype=abstract` | better — structured |
| MeSH terms, grant info, PMC ID | no | no | yes |
| Sequence | no | `rettype=fasta` | overkill |
| Sequence features (CDS, exons) | no | `rettype=gb` | yes |
| Cross-references (xref) | partial | yes (in GB) | yes |
| Bulk metadata for 10K records | best (1 call per ~500) | slow | slow |

ESummary's documented hard limit is 10,000 docsums per call, but the practical sweet spot is ~500 (keeps the URL under length limits when IDs are comma-joined; for >500 use EPost to push IDs server-side first). Per-record payload is much smaller than EFetch. Use ESummary as the default for any metadata-only workflow.

## XML schema brittleness

`Entrez.read()` parses INSDSeq XML, PubmedArticle XML, Gene XML, etc. The schemas are NOT versioned; NCBI adds and renames fields without notice. Real-world consequence: a parser that worked in 2022 may KeyError in 2026 because a nested field moved.

Defensive patterns:
- Use `.get(key, default)` not `[key]` for every nested field
- For sequence content, prefer `SeqIO.read()` over `Entrez.read()` — the SeqIO parsers are versioned with BioPython
- Pin BioPython version in production code; expect to update the parser when NCBI changes the XML
- For PubMed, `Bio.Medline.parse(handle)` (against `rettype='medline'`) is more stable than the XML route

## Code patterns

### Single sequence by accession

**Goal:** Fetch one nucleotide record as a SeqRecord with features.

**Approach:** EFetch with `rettype='gb', retmode='text'`; parse with `SeqIO.read()`.

**Reference (BioPython 1.83+):**
```python
def fetch_genbank(accession):
    h = Entrez.efetch(db='nucleotide', id=accession, rettype='gb', retmode='text')
    record = SeqIO.read(h, 'genbank'); h.close()
    return record

gb = fetch_genbank('NM_007294.4')
for feat in gb.features:
    if feat.type == 'CDS':
        print(feat.location, feat.qualifiers.get('product', ['?'])[0])
```

### Bulk metadata via ESummary

**Goal:** Get organism + length + title for 1,000 UIDs without downloading sequences.

**Approach:** ESummary on a comma-joined ID batch (max 500 per call by convention; supports 10K hard limit).

**Reference (BioPython 1.83+):**
```python
def bulk_summaries(db, ids, chunk=500):
    out = []
    for i in range(0, len(ids), chunk):
        h = Entrez.esummary(db=db, id=','.join(ids[i:i+chunk]))
        out.extend(Entrez.read(h)); h.close()
        time.sleep(0.1 if Entrez.api_key else 0.34)
    return out

records = bulk_summaries('nucleotide', uid_list)
```

### Extract CDS in one round-trip

**Goal:** Download the CDS-only translated protein sequences from a GenBank record without manually walking features.

**Approach:** Use `rettype='fasta_cds_aa'` — NCBI server-side extracts and translates every CDS in the record.

**Reference (BioPython 1.83+):**
```python
def cds_proteins(accession):
    h = Entrez.efetch(db='nucleotide', id=accession, rettype='fasta_cds_aa', retmode='text')
    return list(SeqIO.parse(h, 'fasta'))

proteins = cds_proteins('NC_000913.3')  # E. coli K-12 genome
print(f'{len(proteins)} CDS-translated proteins')
```

### Pull PubMed with structured MeSH

**Goal:** Get MeSH terms and grant information that aren't in the abstract format.

**Approach:** `rettype='xml'` and walk the PubmedArticle structure defensively.

**Reference (BioPython 1.83+):**
```python
def pubmed_full(pmid):
    h = Entrez.efetch(db='pubmed', id=pmid, retmode='xml')
    records = Entrez.read(h); h.close()
    article = records['PubmedArticle'][0]
    citation = article['MedlineCitation']
    mesh = [m['DescriptorName'] for m in citation.get('MeshHeadingList', [])]
    title = citation['Article']['ArticleTitle']
    return {'pmid': pmid, 'title': title, 'mesh': mesh}
```

### History-server fetch (post-ESearch)

**Goal:** Pull a 50,000-record result set without re-sending UIDs.

**Approach:** ESearch with `usehistory='y'`; iterate EFetch with `webenv`/`query_key` and `retstart`. See `batch-downloads` for the production pattern.

```python
h = Entrez.esearch(db='nucleotide', term='Homo sapiens[ORGN] AND srcdb_refseq[PROP] AND biomol_mrna[PROP]',
                   usehistory='y', retmax=0)
r = Entrez.read(h); h.close()
total = int(r['Count'])

with open('out.fasta', 'w') as out:
    for start in range(0, total, 500):
        h = Entrez.efetch(db='nucleotide', rettype='fasta', retmode='text',
                          retstart=start, retmax=500,
                          webenv=r['WebEnv'], query_key=r['QueryKey'])
        out.write(h.read()); h.close()
        time.sleep(0.1 if Entrez.api_key else 0.34)
```

### SRA UID -> SRR accession + run metrics

**Goal:** Convert an opaque SRA UID into the SRR run accession plus Bases/Spots metrics, in one EFetch.

**Approach:** `rettype='runinfo'` returns a CSV row per run.

```python
def sra_runinfo(uids):
    h = Entrez.efetch(db='sra', id=','.join(uids), rettype='runinfo', retmode='text')
    text = h.read(); h.close()
    lines = text.strip().split('\n')
    header = lines[0].split(',')
    return [dict(zip(header, row.split(','))) for row in lines[1:]]
```

### Taxonomy lineage by TXID

```python
def lineage(txid):
    h = Entrez.efetch(db='taxonomy', id=str(txid), retmode='xml')
    record = Entrez.read(h)[0]; h.close()
    return record['Lineage'], record['ScientificName']
```

## Failure modes

### Mixed-format batch silently truncates
- **Trigger:** Mixing modern accessions and legacy GIs in one comma-separated `id=`.
- **Mechanism:** EFetch parses left-to-right; on type-mismatch it may return only the prefix that succeeded.
- **Symptom:** Batch of 100 returns 47 records with no error.
- **Fix:** Validate that all IDs in a batch are the same type before sending.

### `gb` returns CONTIG instead of sequence
- **Trigger:** Fetching a whole-genome shotgun (WGS) assembly with `rettype='gb'`.
- **Mechanism:** Default GB output skips the contig sequence for assemblies, returning only the join() statement.
- **Symptom:** `len(record.seq) == 0` despite the record showing a length in metadata.
- **Fix:** Use `rettype='gbwithparts'` for assemblies; or for FASTA use `rettype='fasta'` directly.

### XML parse fails on schema drift
- **Trigger:** Code that was last touched in 2022 hits a new NCBI XML field layout.
- **Mechanism:** `Entrez.read()` uses cached DTDs that may not match current responses.
- **Symptom:** KeyError or ValidationError on a field that "always worked".
- **Fix:** Run `Entrez.read._XMLParser._DTDs.clear()` to force re-fetch of DTDs; upgrade BioPython; or switch to text format (`rettype='medline'` for pubmed) which is more stable.

### Silent empty response on bad rettype
- **Trigger:** Asking for `rettype='abstract'` on the nucleotide db (only valid for pubmed).
- **Mechanism:** EFetch returns empty text — no HTTP error.
- **Symptom:** `handle.read()` returns `''` or whitespace.
- **Fix:** Check the decision matrix above before sending unfamiliar combinations.

### Accession without `.version` returns wrong record later
- **Trigger:** Storing `'NM_007294'` (no version) for reproducibility years later.
- **Mechanism:** NCBI returns the current version, which may have changed annotation.
- **Symptom:** Re-run produces different CDS coordinates than the original analysis.
- **Fix:** Always pin `accession.version` (e.g. `NM_007294.4`); the version is in the GB LOCUS line.

### EFetch returns HTML error page
- **Trigger:** Invalid UID, mid-maintenance window, or expired WebEnv.
- **Mechanism:** Failure surfaces in HTML body, HTTP status is 200.
- **Symptom:** SeqIO chokes parsing HTML as GenBank.
- **Fix:** Sniff the first line of the response — `LOCUS` for GB, `>` for FASTA — and raise on mismatch.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `HTTPError 400` | Invalid id/db/rettype combo | Verify against decision matrix; check accession exists |
| `HTTPError 429` | Rate limit exceeded | Add `time.sleep(0.34)` or use API key |
| Empty `SeqRecord.seq` | WGS record with `rettype='gb'` | Use `rettype='gbwithparts'` |
| `ValueError: Sequence too short` | Wrong format declared to SeqIO | Match rettype to `SeqIO` format string |
| `ExpatError` | Got HTML where XML expected | Sniff response start; retry |
| KeyError on nested XML field | Schema drift | Use `.get()` defensively; pin BioPython |

## References

- Sayers EW et al. (2024) Database resources of the National Center for Biotechnology Information in 2024. *Nucleic Acids Res* 52:D33-D43.
- Kans J. (2024) Entrez Direct: E-utilities on the Unix Command Line. NCBI Bookshelf NBK179288.
- NCBI. EFetch help. NBK25499.
- Cock PJ et al. (2009) Biopython: freely available Python tools for computational molecular biology and bioinformatics. *Bioinformatics* 25:1422-1423.

## Related Skills

- entrez-search - Find UIDs before fetching
- entrez-link - Cross-database navigation via ELink
- batch-downloads - History-server pipelines for large fetches
- ncbi-datasets-cli - Modern CLI for genome / gene metadata; often faster than EFetch
- sequence-io/read-sequences - Parse downloaded FASTA/GenBank with SeqIO
<!-- END FILE: database-access/entrez-fetch/SKILL.md -->

## 子目录：database-access/entrez-link

<!-- BEGIN FILE: database-access/entrez-link/SKILL.md -->
---
name: bio-entrez-link
description: Find cross-database references between NCBI databases using Biopython Bio.Entrez (ELink). Use when navigating gene to protein/structure, sequence to publication, PubMed to GEO, BioProject to SRA runs, or discovering all link relationships for a record. Covers linkname semantics, cmd= variants, asymmetric link warnings, neighbor_history for >200 input IDs, and per-database link tables.
tool_type: python
primary_tool: Bio.Entrez
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, Entrez Direct 21.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(Bio.Entrez.elink)` to check signatures
- CLI: `elink -version` then `elink -help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Entrez Link

**"Find records linked to this record in another NCBI database"** -> ELink walks the curated, weekly-maintained link tables between Entrez databases. A link is an asserted relationship (e.g. "this PubMed article describes this nucleotide sequence"), not a similarity hit.

ELink is the navigation layer of Entrez. The decision that matters most is **which `linkname` to use** — not which databases. A single (`dbfrom`, `db`) pair can have a dozen `linkname` variants distinguishing curation level, evidence type, and direction. Picking the wrong one is the difference between 5 high-confidence matches and 500 noisy automated assertions.

- Python: `Entrez.elink(dbfrom=..., db=..., id=..., linkname=...)` (BioPython)
- CLI: `elink -db pubmed -target gene -name pubmed_gene_rif` (Entrez Direct)
- R: `entrez_link(dbfrom=..., db=..., id=...)` (rentrez)

## Required Setup

```python
from Bio import Entrez
Entrez.email = 'researcher@institution.edu'
Entrez.api_key = 'optional_api_key'  # raises rate to 10 req/sec
```

## The `linkname` decision (most important)

For most (`dbfrom`, `db`) pairs NCBI exposes multiple link tables. The qualifiers in the name encode the curation level and the evidence source. Choose deliberately.

### gene -> protein (representative example)

| linkname | Returns | When to use |
|---|---|---|
| `gene_protein` | All linked proteins (curated + automated) | Exploration; expect 10-1000x more hits |
| `gene_protein_refseq` | RefSeq proteins only | Reference-quality analyses; orthology |
| `gene_protein_swissprot` | Reviewed UniProt entries with NCBI cross-ref | Functional annotation; literature support |

### pubmed -> gene

| linkname | Returns |
|---|---|
| `pubmed_gene` | Genes mentioned in this paper (text-mined + curated) |
| `pubmed_gene_rif` | Genes with a Reference Into Function (curated, high-quality) |
| `pubmed_gene_pubmed` | Other PubMed records sharing gene linkage (rare use) |

### nucleotide -> protein

| linkname | Returns |
|---|---|
| `nuccore_protein` | All proteins encoded by this nucleotide record (CDS-linked) |
| `nuccore_protein_refseq` | RefSeq proteins only |

### Discover what link names exist for a pair

```python
h = Entrez.elink(dbfrom='gene', db='protein', id='672', cmd='acheck')
record = Entrez.read(h); h.close()
for ls in record[0]['IdCheckList']['IdLinkSet'][0]['LinkInfo']:
    print(f'{ls["Name"]}  -> {ls["DbTo"]} | {ls["MenuTag"]} ({ls["HtmlTag"]})')
```

`cmd='acheck'` is the only authoritative way to enumerate available linknames — they change with each NCBI release.

## Decision table: which `cmd` for which goal

| Goal | cmd | Returns |
|---|---|---|
| Get linked records | `neighbor` (default) | Linked IDs in target db |
| Get linked + relevance scores | `neighbor_score` | IDs with similarity scores (mostly `pubmed_pubmed`) |
| Get >200 source IDs in one go | `neighbor_history` | WebEnv + QueryKey for downstream EFetch |
| Enumerate available links | `acheck` | List of all linknames for source IDs |
| Check if any link exists | `ncheck` | Boolean per source ID |
| Check specific link exists | `lcheck` | Boolean per source ID + linkname |
| Get NCBI HTML link URLs | `llinks` | URLs to Entrez record pages |
| Get external provider links | `prlinks` | URLs to journal sites, etc. |

The `neighbor_history` cmd is essential when source `id` count exceeds ~200 — past that, the URL-length limit makes the comma-joined form fail. With `neighbor_history` ELink puts results on the history server and returns WebEnv/QueryKey for downstream pickup.

## Asymmetric link warning

ELink relationships are **not guaranteed symmetric**. `pubmed_gene` and `gene_pubmed` may return different sets because:
- Direction-dependent curation: gene-to-PubMed is curated by NCBI staff (GeneRIF); PubMed-to-gene includes text-mining.
- Cutoffs: some link tables truncate at N best links in one direction but not the other.
- Index lag asymmetry: when one db updates faster than the other.

If round-trip consistency matters (e.g. "every gene mentioned in this paper, then every paper mentioning each gene"), expect the round-trip set to be larger than the input — and never assume `A -> B -> A` returns the original ID alone.

## Per-database link catalog (curated subset)

### gene

| Target | Common linknames | Notes |
|---|---|---|
| protein | `gene_protein`, `gene_protein_refseq`, `gene_protein_swissprot` | RefSeq is the safe default |
| nuccore | `gene_nuccore`, `gene_nuccore_refseqrna`, `gene_nuccore_refseqgene` | `refseqrna` for mRNA, `refseqgene` for the curated gene region |
| pubmed | `gene_pubmed`, `gene_pubmed_rif` | RIF is curated and high-quality |
| homologene | `gene_homologene` | Deprecated 2014 but data still queryable |
| snp | `gene_snp` | dbSNP entries in gene region |
| clinvar | `gene_clinvar` | Clinical variants |
| omim | `gene_omim` | Disease associations |

### nuccore / nucleotide

| Target | Common linknames |
|---|---|
| protein | `nuccore_protein`, `nuccore_protein_refseq` |
| gene | `nuccore_gene` |
| taxonomy | `nuccore_taxonomy` |
| biosample | `nuccore_biosample` |
| sra | `nuccore_sra` |
| pubmed | `nuccore_pubmed`, `nuccore_pubmed_refseq` |

### protein

| Target | Common linknames |
|---|---|
| nuccore | `protein_nuccore`, `protein_nuccore_cds`, `protein_nuccore_mrna` |
| gene | `protein_gene` |
| structure | `protein_structure` |
| cdd | `protein_cdd` (conserved domains) |
| pubmed | `protein_pubmed` |

### pubmed

| Target | Common linknames |
|---|---|
| pubmed | `pubmed_pubmed`, `pubmed_pubmed_citedin`, `pubmed_pubmed_refs` |
| gene | `pubmed_gene`, `pubmed_gene_rif` |
| protein | `pubmed_protein` |
| nuccore | `pubmed_nuccore` |
| gds | `pubmed_gds` (GEO datasets cited in paper) |
| sra | `pubmed_sra` |

### bioproject

| Target | Common linknames |
|---|---|
| biosample | `bioproject_biosample` |
| sra | `bioproject_sra` |
| pubmed | `bioproject_pubmed` |

## Code patterns

### Single source -> single target

**Goal:** Get RefSeq proteins for a single gene.

**Approach:** ELink with explicit `linkname` to restrict to curated set.

**Reference (BioPython 1.83+):**
```python
def gene_to_refseq_proteins(gene_id):
    h = Entrez.elink(dbfrom='gene', db='protein', id=gene_id, linkname='gene_protein_refseq')
    r = Entrez.read(h); h.close()
    if not r[0]['LinkSetDb']:
        return []
    return [link['Id'] for link in r[0]['LinkSetDb'][0]['Link']]

print(gene_to_refseq_proteins('672'))  # BRCA1
```

### Batch source -> target (small batch)

**Goal:** Get linked proteins for a list of <200 gene IDs in one call.

**Approach:** Comma-join IDs; one linkset per input in the response.

**Reference (BioPython 1.83+):**
```python
def batch_gene_protein(gene_ids):
    h = Entrez.elink(dbfrom='gene', db='protein', id=','.join(gene_ids), linkname='gene_protein_refseq')
    r = Entrez.read(h); h.close()
    out = {}
    for linkset in r:
        src = linkset['IdList'][0]
        out[src] = [link['Id'] for link in linkset['LinkSetDb'][0]['Link']] if linkset['LinkSetDb'] else []
    return out
```

### Large batch via history server

**Goal:** Link 5,000 gene IDs to proteins without hitting URL-length limits.

**Approach:** EPost the IDs first (chunked at 200), then ELink with `cmd='neighbor_history'` referencing the WebEnv. Downstream EFetch picks up linked IDs from the history server.

**Reference (BioPython 1.83+):**
```python
def post_then_link(gene_ids, target='protein', linkname='gene_protein_refseq'):
    # EPost in chunks of 200
    webenv = None
    for i in range(0, len(gene_ids), 200):
        chunk = gene_ids[i:i+200]
        kwargs = {'db': 'gene', 'id': ','.join(chunk)}
        if webenv:
            kwargs['WebEnv'] = webenv
        h = Entrez.epost(**kwargs)
        r = Entrez.read(h); h.close()
        webenv = r['WebEnv']
        query_key = r['QueryKey']
        time.sleep(0.1 if Entrez.api_key else 0.34)

    # Link with neighbor_history
    h = Entrez.elink(dbfrom='gene', db=target, linkname=linkname,
                     cmd='neighbor_history', WebEnv=webenv, query_key=query_key)
    r = Entrez.read(h); h.close()
    # WebEnv is at the top level of the response; QueryKey is per-LinkSetDbHistory entry.
    return r[0]['WebEnv'], r[0]['LinkSetDbHistory'][0]['QueryKey']

we, qk = post_then_link(['672', '675', '7157'] * 1000)
# Downstream: Entrez.efetch(db='protein', WebEnv=we, query_key=qk, retstart=..., retmax=500)
```

### Discover all available links

**Goal:** Before writing a pipeline, enumerate what link tables NCBI exposes for a (dbfrom, source-id) pair.

**Approach:** `cmd='acheck'` returns the full LinkInfo list per source.

**Reference (BioPython 1.83+):**
```python
def list_link_names(dbfrom, id):
    h = Entrez.elink(dbfrom=dbfrom, id=id, cmd='acheck')
    r = Entrez.read(h); h.close()
    info = r[0]['IdCheckList']['IdLinkSet'][0]['LinkInfo']
    return [(i['Name'], i['DbTo'], i['MenuTag']) for i in info]

for name, target, label in list_link_names('gene', '672'):
    print(f'{name:<40} -> {target:<15} ({label})')
```

### Chain links (gene -> protein -> structure)

```python
def gene_to_structures(gene_id):
    h = Entrez.elink(dbfrom='gene', db='protein', id=gene_id, linkname='gene_protein_refseq')
    r = Entrez.read(h); h.close()
    if not r[0]['LinkSetDb']:
        return []
    prot_ids = [l['Id'] for l in r[0]['LinkSetDb'][0]['Link'][:10]]
    time.sleep(0.1 if Entrez.api_key else 0.34)
    h = Entrez.elink(dbfrom='protein', db='structure', id=','.join(prot_ids))
    r = Entrez.read(h); h.close()
    out = []
    for ls in r:
        if ls['LinkSetDb']:
            out.extend(l['Id'] for l in ls['LinkSetDb'][0]['Link'])
    return out
```

### Get neighbor_score for related PubMed articles

```python
def related_pubmed(pmid, top=10):
    h = Entrez.elink(dbfrom='pubmed', db='pubmed', id=pmid,
                     linkname='pubmed_pubmed', cmd='neighbor_score')
    r = Entrez.read(h); h.close()
    if not r[0]['LinkSetDb']:
        return []
    return [(l['Id'], int(l['Score'])) for l in r[0]['LinkSetDb'][0]['Link'][:top]]
```

### BioProject -> SRA runs

For SRA discovery, `pysradb.SRAweb().sra_metadata(prjna, detailed=True)` (see `sra-data`) is the higher-fidelity path — returns SRR accessions directly with run-level metadata in one call. Use ELink only when staying inside Bio.Entrez:

```python
def bioproject_to_sra(prjna):
    # Convert PRJNA to UID first
    h = Entrez.esearch(db='bioproject', term=f'{prjna}[BioProject]')
    r = Entrez.read(h); h.close()
    if not r['IdList']:
        return []
    bp_uid = r['IdList'][0]
    time.sleep(0.1 if Entrez.api_key else 0.34)
    # Link to SRA
    h = Entrez.elink(dbfrom='bioproject', db='sra', id=bp_uid)
    r = Entrez.read(h); h.close()
    return [l['Id'] for l in r[0]['LinkSetDb'][0]['Link']] if r[0]['LinkSetDb'] else []
```

## Failure modes

### Wrong linkname gives wrong order of magnitude
- **Trigger:** Using `gene_protein` when `gene_protein_refseq` was intended.
- **Mechanism:** `gene_protein` includes all automated and predicted entries (XP_* RefSeq plus all GenBank submissions).
- **Symptom:** 500 proteins returned per gene instead of the expected 1-5 canonical isoforms.
- **Fix:** Pick the curated linkname; verify counts on a known gene.

### Empty LinkSetDb on valid input
- **Trigger:** Gene with no linked records in the requested target.
- **Mechanism:** `record[0]['LinkSetDb']` is an empty list, not raising an error.
- **Symptom:** `KeyError` if code assumes `record[0]['LinkSetDb'][0]` always exists.
- **Fix:** Always guard `if not record[0]['LinkSetDb']: return []`.

### Asymmetric round-trip
- **Trigger:** Pipeline does `genes_for_paper(pmid) -> papers_for_each_gene -> set of PMIDs`.
- **Mechanism:** `pubmed_gene` (text-mined + curated) is larger than `gene_pubmed` (curated only); the round-trip set is not closed.
- **Symptom:** Original PMID may not appear in the round-trip set; new PMIDs do.
- **Fix:** Document the directional asymmetry; use the more-curated linkname (`*_rif` variants) when fidelity matters.

### URL length limit on large batches
- **Trigger:** Comma-joined `id=` with 200+ IDs.
- **Mechanism:** HTTP GET URL exceeds NCBI's parsing limit (~2000 chars).
- **Symptom:** HTTP 414 URI Too Long, or silent truncation.
- **Fix:** EPost the IDs first, then ELink with `cmd='neighbor_history'`.

### One linkset per input ID, indexing confusion
- **Trigger:** Sending 5 IDs, then accessing `record[0]['LinkSetDb'][0]['Link']` expecting the union.
- **Mechanism:** ELink returns one `LinkSet` per input UID, indexed by position.
- **Symptom:** Only the first input's links are processed; rest are dropped.
- **Fix:** Iterate `for linkset in record:` and map by `linkset['IdList'][0]`.

### Mismatched dbfrom and id namespace
- **Trigger:** Passing a PMID into `dbfrom='nucleotide'`.
- **Mechanism:** ELink returns no error — it just looks up the PMID as a nucleotide UID, finds nothing.
- **Symptom:** Empty LinkSetDb on a "valid" ID.
- **Fix:** Validate that the ID matches the source db namespace (PMIDs are db=pubmed, GeneIDs are db=gene).

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `KeyError: 'LinkSetDb'` | Empty result not guarded | `if not record[0]['LinkSetDb']: return []` |
| `HTTPError 414` | Comma-joined id too long | Use EPost + `neighbor_history` |
| `HTTPError 400` | Invalid linkname or wrong db namespace | Use `cmd='acheck'` to enumerate valid links |
| 500 hits instead of 5 | Wrong linkname (e.g. `gene_protein` vs `_refseq`) | Pick curated variant |
| Round-trip set differs from input | Asymmetric link tables | Document; use curated variants |

## References

- Sayers EW et al. (2024) Database resources of the National Center for Biotechnology Information in 2024. *Nucleic Acids Res* 52:D33-D43.
- Kans J. (2024) Entrez Direct: E-utilities on the Unix Command Line. NCBI Bookshelf NBK179288.
- NCBI. ELink help. NBK25499.

## Related Skills

- entrez-search - Resolve UIDs before linking
- entrez-fetch - Retrieve linked records' content
- batch-downloads - History-server retrieval after ELink with `neighbor_history`
- geo-data - Specialized gds <-> pubmed/bioproject links (gds->sra ELink unreliable; use pysradb)
- ncbi-datasets-cli - Modern alternative for gene/genome cross-reference queries
<!-- END FILE: database-access/entrez-link/SKILL.md -->

## 子目录：database-access/entrez-search

<!-- BEGIN FILE: database-access/entrez-search/SKILL.md -->
---
name: bio-entrez-search
description: Search NCBI databases using Biopython Bio.Entrez (ESearch, EInfo, EGQuery, ESpell). Use when finding records by keyword, building reproducible field-qualified queries, navigating the Entrez Query Translator, exploiting the history server for large result sets, handling retmax caps, or interpreting weekly index lag. Covers PubMed, Nucleotide, Protein, Gene, SRA, GEO, Assembly, Taxonomy, ClinVar, dbSNP.
tool_type: python
primary_tool: Bio.Entrez
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, Entrez Direct 21.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(Bio.Entrez.esearch)` to check signatures
- CLI: `esearch -version` then `esearch -help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Entrez Search

**"Find NCBI records matching a query"** -> ESearch returns matching record UIDs (not full records) from one NCBI database; EGQuery returns counts across all databases; EInfo describes a database's searchable fields and update timestamp.

The single most important fact: ESearch returns *UIDs* (PMIDs, GI numbers, gene IDs, etc.), not records. To get content the agent must call EFetch or ESummary. Forgetting this is the most common Entrez mistake.

- Python: `Entrez.esearch(db=..., term=...)` (BioPython)
- CLI: `esearch -db pubmed -query 'CRISPR[Title]'` (Entrez Direct, NBK179288)
- R: `entrez_search(db=..., term=...)` (rentrez)

## Required Setup

```python
from Bio import Entrez
import time

Entrez.email = 'researcher@institution.edu'  # NCBI requires; sets User-Agent
Entrez.api_key = 'YOUR_KEY'                  # 3 -> 10 req/sec; get at ncbi.nlm.nih.gov/account/settings/
Entrez.tool = 'project-name'                 # appears in NCBI usage logs; helps if rate-throttled
```

## What ESearch actually does

ESearch sends the query string through the **Entrez Query Translator (EQT)**, which rewrites unqualified terms into the canonical `term[field]` form, then runs the rewritten query against the per-database index. The result is a list of UIDs plus a `QueryTranslation` string showing exactly what was searched. Reproducible work always inspects `QueryTranslation` and builds queries that are translation-stable from the start.

```python
handle = Entrez.esearch(db='nucleotide', term='human BRCA1')
record = Entrez.read(handle)
handle.close()
print(record['QueryTranslation'])
# '("homo sapiens"[Organism] OR human[All Fields]) AND (BRCA1[Gene Name] OR BRCA1[All Fields])'
```

The translator may expand `human` to the full taxonomy subtree, or coerce a gene symbol to `[All Fields]` if the symbol isn't unambiguous. Use field-qualified terms (`Homo sapiens[ORGN] AND BRCA1[Gene Name]`) for any query that will be re-run later.

## Decision table: which utility for which question

| Question | Utility | Returns | Cost |
|---|---|---|---|
| "How many records match X in PubMed?" | ESearch with `retmax=0` | Count + WebEnv | 1 call |
| "Give me 20 matching UIDs" | ESearch | UIDs | 1 call |
| "Give me ALL matching UIDs (>10K)" | ESearch + `usehistory='y'` | WebEnv/QueryKey | 1 call (then EFetch chunks server-side) |
| "Does record X exist in db Y?" | ESearch with `term='X[Accn]'` | UIDs | 1 call |
| "Which NCBI databases mention X at all?" | EGQuery | Counts across every db | 1 call |
| "What searchable fields does db Y have?" | EInfo with `db=Y` | FieldList | 1 call |
| "Last update timestamp for db Y?" | EInfo with `db=Y` | `LastUpdate` | 1 call |
| "Did the user misspell X?" | ESpell | Spelling suggestion | 1 call |

EGQuery has been semi-deprecated since the 2022 site refactor — it still works but counts can lag the per-database indexes by 1-2 days. For authoritative cross-database counts, loop ESearch over a curated db list instead.

## retmax silent caps

| Endpoint behavior | Cap | Workaround |
|---|---|---|
| Default `retmax` | 20 | Set explicitly |
| Legacy esearch.fcgi (no `usehistory`) | **9,999** silent cap | Use history server |
| `usehistory='y'` + ESearch | 100,000 per page | Page with `retstart` against the WebEnv |
| EPost (to push IDs server-side) | 200 IDs per call | Chunk to multiple EPost calls; union with QueryKey |

The 9,999 cap is the bug that has shipped in countless lab pipelines: query returns "Count: 78,432" but `IdList` has 9,999 entries and there is no error. Always set `retmax` explicitly and either page or move to `usehistory='y'` whenever `Count > retmax`.

## History server (WebEnv/QueryKey) semantics

| Property | Value |
|---|---|
| TTL | 8 hours absolute (per NCBI E-utils help, 2024) |
| Idle eviction | Empirically ~15 min under load; can be shorter |
| Chaining | Run another ESearch against `WebEnv` with `term='#1 AND #2'` to intersect prior QueryKeys |
| Persistence | Session is per WebEnv string; do NOT share across processes when isolation matters |
| Failure mode | Expired session returns HTTP 200 with `<ERROR>WebEnv not found</ERROR>` — must parse body, not status |

Chaining example:
```python
h1 = Entrez.esearch(db='pubmed', term='CRISPR[Title]', usehistory='y')
r1 = Entrez.read(h1); h1.close()
webenv = r1['WebEnv']

h2 = Entrez.esearch(db='pubmed', term='2024[PDAT]', usehistory='y', WebEnv=webenv)
r2 = Entrez.read(h2); h2.close()

# Intersect QueryKey #1 (CRISPR) AND #2 (2024) into a new key
h3 = Entrez.esearch(db='pubmed', term=f'#{r1["QueryKey"]} AND #{r2["QueryKey"]}',
                    usehistory='y', WebEnv=webenv)
r3 = Entrez.read(h3); h3.close()
print(f'CRISPR & 2024: {r3["Count"]}')
```

## Index lag

NCBI's Entrez indexer runs nightly (US Eastern). Records submitted Monday morning typically appear in ESearch results Wednesday at earliest. PubMed has additional MEDLINE indexing lag (1-3 weeks for full MeSH terms). For freshly-deposited data the more reliable check is EFetch on the known accession or NCBI Datasets API for genomes.

## Field-qualified query patterns (per database)

| Database | Common fields | Notes |
|---|---|---|
| pubmed | `[Title]`, `[TIAB]` (title+abstract), `[MeSH]`, `[Author]`, `[Journal]`, `[PDAT]`, `[DCOM]`, `[PMC]` | `[TIAB]` is more permissive than `[Title]`; `[MeSH]` requires the term to be indexed (lags) |
| nucleotide | `[Organism]`, `[Gene Name]`, `[Accn]`, `[SLEN]`, `[Filter]`, `[PROP]` | `srcdb_refseq[PROP]` restricts to RefSeq; `biomol_genomic[PROP]` filters molecule type |
| protein | `[Organism]`, `[Gene Name]`, `[Accn]`, `[MOLWT]`, `[PROP]` | `swissprot[Filter]` restricts to reviewed |
| gene | `[Gene/Locus]`, `[Organism]`, `[Chromosome]`, `[Gene Type]` | `[Gene Type]` includes `protein-coding`, `pseudo`, `ncRNA` |
| sra | `[Organism]`, `[Platform]`, `[Strategy]`, `[Library Source]`, `[BioProject]` | `[Strategy]` accepts `RNA-Seq`, `WGS`, `ChIP-Seq`, etc. |
| gds (GEO) | `[Organism]`, `[Entry Type]`, `[GDS Type]`, `[Platform]` | `gse[Entry Type]` for Series, `gds[Entry Type]` for curated DataSets |
| taxonomy | `[Scientific Name]`, `[Common Name]`, `[Rank]`, `[TXID]` | TXID is the numeric taxonomy ID |
| clinvar | `[Gene Name]`, `[Clinical Significance]`, `[Variation Type]` | `pathogenic[CLIN]` for pathogenic only |

### Filter properties that newcomers miss

```python
# Curated RefSeq mRNA only, human, between 500 and 5000 nt
term = 'Homo sapiens[ORGN] AND srcdb_refseq[PROP] AND biomol_mrna[PROP] AND 500:5000[SLEN]'

# Reviewed SwissProt human kinases
term = 'Homo sapiens[ORGN] AND swissprot[Filter] AND kinase[Protein Name]'

# PubMed: human studies in last 30 days, full-text in PMC
term = 'CRISPR[Title] AND humans[MeSH Terms] AND last 30 days[EDAT] AND pubmed pmc[sb]'
```

### Organism field gotcha

`[Organism]` (and the alias `[ORGN]`) is **taxonomy-walked**: searching `mammalia[ORGN]` returns records from every species in Mammalia. To get records tagged at exactly that node use `[Organism:exp]` (no taxonomic expansion). Most workflows want the default walk, but multi-species queries that "blow up" by 100x are almost always a missing `:exp`.

## Code patterns

### Single search with explicit retmax

**Goal:** Get matching UIDs for a focused query without hitting silent caps.

**Approach:** Set `retmax` explicitly to the maximum the caller wants; if `Count > retmax` either page or switch to history server.

**Reference (BioPython 1.83+):**
```python
def search_ncbi(db, term, max_results=100):
    handle = Entrez.esearch(db=db, term=term, retmax=max_results)
    record = Entrez.read(handle); handle.close()
    count = int(record['Count'])
    if count > max_results:
        print(f'WARNING: {count} matched, returning first {max_results}; use history server for full set')
    return record['IdList'], count, record['QueryTranslation']
```

### Paged retrieval (only when enumeration without fetching is required)

**Goal:** Stream all matching UIDs to a file when downstream work can't use the history server.

**Approach:** Page through `retstart` increments; respect rate limit; stop at total.

```python
def stream_all_ids(db, term, batch_size=10000):
    h = Entrez.esearch(db=db, term=term, retmax=0)
    total = int(Entrez.read(h)['Count']); h.close()
    delay = 0.1 if Entrez.api_key else 0.34
    for start in range(0, total, batch_size):
        h = Entrez.esearch(db=db, term=term, retstart=start, retmax=batch_size)
        r = Entrez.read(h); h.close()
        for uid in r['IdList']:
            yield uid
        time.sleep(delay)
```

For any download workflow, history-server retrieval is strictly better — see `batch-downloads` skill.

### History server for downstream EFetch

**Goal:** Push a large result set to NCBI servers so EFetch can pull it in batches without re-sending IDs.

**Approach:** ESearch with `usehistory='y'`; capture WebEnv and QueryKey; pass to EFetch.

**Reference (BioPython 1.83+):**
```python
h = Entrez.esearch(db='nucleotide',
                   term='Homo sapiens[ORGN] AND srcdb_refseq[PROP] AND biomol_mrna[PROP]',
                   usehistory='y', retmax=0)
r = Entrez.read(h); h.close()
webenv, query_key, count = r['WebEnv'], r['QueryKey'], int(r['Count'])
print(f'{count} mRNAs queued on history server; use webenv/query_key with efetch')
```

### Inspect the translation before trusting a query

**Goal:** Catch translator misinterpretation before producing publication results.

**Approach:** Always print `QueryTranslation` for new queries and lock the rewritten string into the codebase as the canonical query.

```python
h = Entrez.esearch(db='pubmed', term='covid vaccine efficacy 2024', retmax=0)
r = Entrez.read(h); h.close()
print(r['QueryTranslation'])
# '("covid 19 vaccines"[MeSH Terms] OR ("covid 19"[All Fields] AND ...
# Now use this rewritten string explicitly to guarantee reproducibility.
```

### Discover fields for a database

```python
def list_fields(db):
    h = Entrez.einfo(db=db); r = Entrez.read(h); h.close()
    return [(f['Name'], f['FullName'], f['Description']) for f in r['DbInfo']['FieldList']]
```

### Spell-check before searching (catches typo-driven empty results)

```python
h = Entrez.espell(db='pubmed', term='breast canser')
r = Entrez.read(h); h.close()
print(r['CorrectedQuery'])  # 'breast cancer'
```

## Failure modes

### Silent retmax cap
- **Trigger:** `Count > 9999` with no `usehistory='y'`; `IdList` capped at 9999.
- **Mechanism:** Legacy esearch.fcgi enforces a 9999 cap for non-history responses.
- **Symptom:** Pipeline returns "the first 9999" with no error; downstream stats are wrong.
- **Fix:** Always check `int(record['Count']) <= len(record['IdList'])`; switch to history server above ~5000.

### Query translation mismatch
- **Trigger:** Unqualified ambiguous term (e.g. `MARCH1` — Excel-renamed gene vs month abbreviation).
- **Mechanism:** EQT falls back to `[All Fields]` when no unambiguous mapping is found.
- **Symptom:** Either zero hits (gene symbol not in `[All Fields]`) or huge non-specific hits.
- **Fix:** Use field-qualified terms; for gene symbols, use HGNC ID via `gene` db lookup first.

### WebEnv expiration mid-pipeline
- **Trigger:** Long-running batch job; session > 8 hours or idle > 15 min.
- **Mechanism:** Server evicts WebEnv; subsequent EFetch returns `<ERROR>` body with HTTP 200.
- **Symptom:** Silent empty results halfway through a download.
- **Fix:** Parse error bodies (not just status codes); re-run ESearch and resume from `retstart`.

### Index lag for fresh deposits
- **Trigger:** Querying a record submitted < 48h ago.
- **Mechanism:** Indexer is batch (Tue/Fri primary); record exists but not searchable.
- **Symptom:** ESearch by accession returns empty; direct EFetch by accession succeeds.
- **Fix:** If the accession is known, use EFetch directly; only use ESearch for content-based discovery.

### Organism over-expansion
- **Trigger:** `[ORGN]` query on a higher taxon (e.g. `Vertebrata[ORGN]`).
- **Mechanism:** Default behavior walks the entire taxonomy subtree.
- **Symptom:** 1000x more hits than intended.
- **Fix:** Use `[Organism:exp]` to disable the walk, or constrain to a specific species/genus.

### Empty IdList with no error
- **Trigger:** Misspelled field name (`[gene]` works; `[gene_name]` returns nothing).
- **Mechanism:** Unknown field is silently coerced to `[All Fields]` — but combined with `AND` of a real field, the AND prunes everything.
- **Symptom:** Query that "should" match gets 0 results.
- **Fix:** Run EInfo on the db first to confirm field names; check `QueryTranslation`.

## Rate-limit math

| Auth | req/sec allowed | Sleep between calls | Bulk-friendly? |
|---|---|---|---|
| Email only | 3 | 0.34 s | Use history server, not parallel calls |
| Email + API key | 10 | 0.10 s | Modest parallelism (4 workers) is safe |
| Institutional bulk | Email `eutilities@ncbi.nlm.nih.gov` | Negotiated | For >100K queries; courtesy expected |

NCBI's terms of use ask that heavy automated queries run outside US weekday business hours (9 AM-5 PM ET). For genuinely bulk work, prefer the history server over parallel API calls — chunking against one session is faster and friendlier than scaling out.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `HTTPError 429` | Rate limit exceeded | Add `time.sleep(0.34)` or use API key |
| `HTTPError 400` | Field name or bracket malformed | Inspect EInfo field list; check brackets |
| `RuntimeError: ... email` | Missing `Entrez.email` | Set globally before any call |
| Empty `IdList`, large `Count` | Hit retmax cap | Set `retmax` explicitly or use history |
| `<ERROR>WebEnv not found</ERROR>` (HTTP 200) | Session expired | Re-run ESearch; parse XML body for errors |
| Query gives wildly wrong count | EQT misinterpretation | Print `QueryTranslation`; use field-qualified terms |

## References

- Sayers EW et al. (2024) Database resources of the National Center for Biotechnology Information in 2024. *Nucleic Acids Res* 52:D33-D43.
- Kans J. (2024) Entrez Direct: E-utilities on the Unix Command Line. NCBI Bookshelf NBK179288.
- NCBI. E-utilities In-Depth: Parameters, Syntax and More. NBK25499 (online manual; check current revision).
- Cock PJ et al. (2009) Biopython: freely available Python tools for computational molecular biology and bioinformatics. *Bioinformatics* 25:1422-1423.

## Related Skills

- entrez-fetch - Retrieve actual records once UIDs are in hand
- entrez-link - Cross-database navigation via ELink
- batch-downloads - History-server batch retrieval pipelines
- ncbi-datasets-cli - Modern alternative for genome/gene metadata (Datasets v2 CLI)
- geo-data - Specialized search semantics for the gds database
- sra-data - SRA metadata search before downloading runs
- ensembl-rest - Ensembl REST as alternative for Ensembl-native queries
<!-- END FILE: database-access/entrez-search/SKILL.md -->

## 子目录：database-access/geo-data

<!-- BEGIN FILE: database-access/geo-data/SKILL.md -->
---
name: bio-geo-data
description: Query and download from NCBI Gene Expression Omnibus (GEO) and EMBL-EBI's BioStudies/ArrayExpress mirror. Use when finding expression datasets, navigating SuperSeries vs SubSeries, choosing between series-matrix (submitter-normalized) and raw supplementary files, downloading via GEOparse (Python) or GEOquery (R/Bioconductor), linking GEO to SRA for raw reads, or distinguishing GSE/GSM/GPL/GDS record types. Encodes the SuperSeries trap, the series-matrix normalization-trust caveat, GEOmetadb deprecation, ArrayExpress migration to BioStudies, and processed-vs-raw decision matrix.
tool_type: mixed
primary_tool: Bio.Entrez
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, GEOparse 2.0+, R Bioconductor GEOquery 2.70+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython geoparse` then introspect signatures
- R: `packageVersion('GEOquery')`

If the GSE structure doesn't match expectations (missing fields, malformed series matrix), re-fetch from FTP directly and inspect the SOFT or MINiML file as source of truth.

# GEO Data

**"Pull expression data from GEO accession GSE..."** -> GEO stores Series (GSE), Samples (GSM), Platforms (GPL), and curated DataSets (GDS, frozen 2018). The single most consequential decision is **processed (series matrix) vs raw (supplementary files / linked SRA)** — the answer turns on how much trust the submitter's normalization deserves.

The single most-missed gotcha: **SuperSeries**. A GSE may be a meta-container (`!Series_relation = SuperSeries of: GSExxxxx`) holding multiple sub-studies on different platforms. Naively pulling samples from a SuperSeries gives mixed Affymetrix + Illumina + RNA-seq, mis-batched.

- Python: `Entrez.esearch(db='gds')`, GEOparse for full series download
- R: `GEOquery::getGEO()` (Bioconductor; more mature than GEOparse)
- CLI: `wget` from `ftp.ncbi.nlm.nih.gov/geo/series/...`

## Required Setup

```bash
pip install biopython GEOparse pandas
# OR for R-side:
# R: BiocManager::install('GEOquery')
```

```python
from Bio import Entrez
Entrez.email = 'researcher@institution.edu'
Entrez.api_key = 'optional'
```

## GEO record taxonomy

| Prefix | Type | Granularity | What's in it |
|---|---|---|---|
| GSE | Series | One study | Title, summary, design, links to GSMs, supplementary files |
| GSM | Sample | One biological/technical sample | Submitter metadata, per-sample processed data, link to raw SRA |
| GPL | Platform | One array / sequencer | Probe annotations or sequencer model |
| GDS | DataSet | Curated, normalized subset of one GSE | Re-normalized expression matrix (frozen 2018; new GDS no longer created) |
| GSEXXX SuperSeries | Series meta-container | Wraps multiple SubSeries | `!Series_relation = SuperSeries of: ...` |

**`GDS` is dead-as-format**: NCBI stopped creating new GDS records in 2018. Existing GDS still queryable but use GSE for anything current.

## The SuperSeries trap

A SuperSeries (GSE) wraps multiple SubSeries, often with different platforms. Detection:

```python
# Read the !Series_relation field from SOFT format
from Bio import Entrez
h = Entrez.esummary(db='gds', id='200122288')   # example
r = Entrez.read(h)[0]; h.close()
print(r.get('summary'))   # may or may not flag SuperSeries
# Definitive check: download SOFT and grep:
#   curl ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE122nnn/GSE122288/soft/GSE122288_family.soft.gz | zgrep Series_relation
```

A `SuperSeries of: GSE12345` line means the SuperSeries' samples are the union of all SubSeries — almost certainly mixed-platform / mixed-batch. Process each SubSeries independently.

Symmetric trap: a paper may cite a SubSeries (`SubSeries of: GSEsuper`) where the wider context is essential — check both directions.

## Decision matrix: processed vs raw vs SRA

| Question | Source | Trust level |
|---|---|---|
| "I want expression values; submitter normalization is fine" | Series matrix (`GSE_series_matrix.txt.gz`) | Trust submitter's normalization |
| "I want raw Affymetrix CEL files and to do my own RMA" | Supplementary files (`suppl/`) | Re-normalize locally |
| "I want raw RNA-seq FASTQ" | pysradb `gse_to_srp -> srp_to_srr` (Entrez gds->sra ELink unreliable) | Always raw; processed at submitter is rarely re-usable |
| "I want submitter-provided counts (RNA-seq)" | Supplementary files (usually a `*_counts.txt.gz`) | Trust at risk; submitter pipelines vary |
| "I want a curated subset across many studies" | Use ArchS4 (https://archs4.org) or recount3 | Curated re-processing |

**Default to raw whenever possible.** For Affymetrix: CEL + locally-run RMA is far more reliable than the submitter's "normalized" matrix. For RNA-seq: SRA FASTQ + locally-run alignment/quantification is the only reproducible path; submitter counts often use a private pipeline.

## Series matrix files

A series matrix (`GSE12345_series_matrix.txt.gz`) is a header (sample metadata as `!Sample_*` lines) plus a sample-by-feature expression table. The format is fragile and the values' provenance is whatever the submitter chose. Critical caveats:

- For Affymetrix: the matrix is usually RMA-normalized but submitters sometimes apply additional transforms (log2, scaling, batch correction).
- For RNA-seq: the matrix is sometimes log-CPM, sometimes raw counts, sometimes VST/rlog — read `!Series_overall_design` and `!Sample_data_processing` to know.
- The header has `!Sample_characteristics_ch1` rows that hold the metadata of interest — these are submitter-formatted strings, often inconsistent within one series.

## SOFT vs MINiML

| Format | Content | Parser support |
|---|---|---|
| **SOFT** (`*_family.soft.gz`) | Plain-text, key=value style | GEOparse (Python), GEOquery (R), Entrez Direct |
| **MINiML** (`*_family.xml.tgz`) | XML-structured | GEOparse, GEOquery, custom XML |

Both contain the same content. SOFT is the legacy, MINiML the XML successor. GEOparse handles SOFT well; for very large series (1000+ samples) MINiML's XML structure is slower to parse.

## GEOparse vs GEOquery

| Aspect | GEOparse (Python) | GEOquery (R/Bioconductor) |
|---|---|---|
| Maturity | OK; some known supplementary-file fetch issues since ~2022 | Mature; Bioconductor-supported |
| Output | `GEOparse.GSE` object with `gsms`, `gpls`, `metadata` dicts | `ExpressionSet` or list per platform |
| Supplementary files | `gse.download_supplementary_files()` (sometimes flakey) | `getGEOSuppFiles(gse)` (more reliable) |
| Integration | Pandas DataFrames | Bioconductor ecosystem |
| When | Python-first pipelines | R-first / use ExpressionSet downstream |

For production GEO workflows in R, GEOquery is the stable choice. For Python, GEOparse is the only option but verify file counts after download.

## GEOmetadb status

GEOmetadb (Zhu 2008) was a SQLite mirror of GEO metadata enabling fast SQL queries. **Unmaintained since 2020**; downloads still work but data is stale. Modern replacement: pysradb (`pysradb gse_to_srp`, `pysradb metadata`) covers most of the GEO->SRA mapping; for full GEO queries fall back to Entrez gds.

## ArrayExpress -> BioStudies migration (2020)

ArrayExpress (EMBL-EBI's microarray archive, mirroring GEO) was migrated into BioStudies in 2020. Old `E-MTAB-####` accessions still resolve but the API moved:

| Old (pre-2020) | New (BioStudies) |
|---|---|
| `https://www.ebi.ac.uk/arrayexpress/...` | `https://www.ebi.ac.uk/biostudies/...` |
| ArrayExpress REST | BioStudies REST: `https://www.ebi.ac.uk/biostudies/api/v1/...` |

For new workflows, use BioStudies. For legacy ArrayExpress URLs in old papers, redirect via BioStudies.

## Code patterns

### Search GEO for studies matching a query

**Goal:** Find GSE accessions matching keywords + organism + study type.

**Approach:** ESearch on `gds` db with field-qualified terms; filter to `gse[Entry Type]`; summarize with ESummary.

**Reference (BioPython 1.83+):**
```python
from Bio import Entrez
import time

Entrez.email = 'researcher@institution.edu'


def search_geo(term, study_type='gse', organism=None, max_results=50):
    full_term = f'{term} AND {study_type}[Entry Type]'
    if organism:
        full_term += f' AND {organism}[Organism]'
    h = Entrez.esearch(db='gds', term=full_term, retmax=max_results)
    s = Entrez.read(h); h.close()
    if not s['IdList']:
        return []
    h = Entrez.esummary(db='gds', id=','.join(s['IdList']))
    summaries = Entrez.read(h); h.close()
    return summaries


for s in search_geo('breast cancer RNA-seq', organism='Homo sapiens', max_results=10):
    # Surface SuperSeries
    relation = s.get('summary', '')
    is_super = 'SuperSeries' in str(relation)
    print(f"  {s['Accession']:12} {s['n_samples']:>4} samples  {'[SuperSeries]' if is_super else '':12}  {s['title'][:60]}")
```

### Detect SuperSeries before pulling data

**Goal:** Avoid mixing platforms by detecting SuperSeries structure first.

**Approach:** Download SOFT family file and read `!Series_relation` keys.

```python
import gzip
import urllib.request


def check_super_or_sub_series(gse):
    prefix = gse[:-3] + 'nnn'
    url = f'https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}/{gse}/soft/{gse}_family.soft.gz'
    urllib.request.urlretrieve(url, f'{gse}.soft.gz')
    super_of = []
    sub_of = None
    with gzip.open(f'{gse}.soft.gz', 'rt') as f:
        for line in f:
            if line.startswith('!Series_relation'):
                if 'SuperSeries of' in line:
                    super_of.append(line.split('SuperSeries of: ')[1].strip())
                elif 'SubSeries of' in line:
                    sub_of = line.split('SubSeries of: ')[1].strip()
            if line.startswith('^SAMPLE'):
                break   # Speed: don't read past header
    return {'super_of': super_of, 'sub_of': sub_of}


print(check_super_or_sub_series('GSE122288'))
# {'super_of': ['GSExxxxx', 'GSEyyyyy'], 'sub_of': None}  -> SuperSeries; process subseries separately
```

### Download series matrix with submitter caveat

```python
import gzip
import pandas as pd


def download_series_matrix(gse):
    prefix = gse[:-3] + 'nnn'
    url = f'https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}/{gse}/matrix/{gse}_series_matrix.txt.gz'
    urllib.request.urlretrieve(url, f'{gse}_matrix.txt.gz')
    return f'{gse}_matrix.txt.gz'


def parse_series_matrix(path):
    metadata = {}
    with gzip.open(path, 'rt') as f:
        for line in f:
            if line.startswith('!series_matrix_table_begin'):
                break
            if line.startswith('!'):
                key, *vals = line.rstrip('\n').split('\t')
                metadata[key] = [v.strip('"') for v in vals]
        expr = pd.read_csv(f, sep='\t', index_col=0, comment='!')
    # Series matrix values are whatever submitter chose -- check metadata['!Sample_data_processing']
    return metadata, expr


meta, expr = parse_series_matrix(download_series_matrix('GSE123456'))
print('Sample-level data processing notes:')
for note in set(meta.get('!Sample_data_processing', [])):
    print(f'  - {note}')
```

### Link GEO Series to SRA runs (preferred path: pysradb)

```python
from pysradb import SRAweb


def gse_to_srr(gse):
    db = SRAweb()
    srp_df = db.gse_to_srp(gse)
    if srp_df.empty:
        return []
    srp = srp_df['study_accession'].iloc[0]
    srr_df = db.srp_to_srr(srp)
    return srr_df['run_accession'].tolist()


srrs = gse_to_srr('GSE123456')
print(f'GSE123456 -> {len(srrs)} SRR runs')
```

### GEOparse: full Series download

```python
import GEOparse


def get_gse(gse_id, dest='./geo_cache'):
    gse = GEOparse.get_GEO(geo=gse_id, destdir=dest)
    print(f'{gse_id}: {len(gse.gsms)} samples, {len(gse.gpls)} platforms')
    for gsm_name, gsm in list(gse.gsms.items())[:3]:
        print(f'  {gsm_name}: {gsm.metadata.get("title", ["?"])[0]}')
    return gse


# Supplementary files (raw data) -- verify file count manually after
gse = get_gse('GSE123456')
gse.download_supplementary_files(directory='./geo_cache')
```

### R: GEOquery (more reliable supplementary download)

```r
# Reference: Bioconductor GEOquery 2.70+ | Verify API if version differs
library(GEOquery)

gse <- getGEO('GSE123456', GSEMatrix = TRUE)
length(gse)             # one ExpressionSet per platform
head(pData(gse[[1]]))   # sample metadata
head(exprs(gse[[1]]))   # expression matrix (submitter-normalized -- verify processing notes)

# Raw / supplementary files
supp_dir <- getGEOSuppFiles('GSE123456', baseDir = './geo_cache')
list.files(rownames(supp_dir))
```

### Find datasets by PubMed citation

```python
def geo_from_pubmed(pmid):
    h = Entrez.elink(dbfrom='pubmed', db='gds', id=pmid)
    r = Entrez.read(h); h.close()
    if not r[0]['LinkSetDb']:
        return []
    gds_ids = [l['Id'] for l in r[0]['LinkSetDb'][0]['Link']]
    h = Entrez.esummary(db='gds', id=','.join(gds_ids))
    summaries = Entrez.read(h); h.close()
    return summaries
```

## Failure modes

### SuperSeries pulled as one experiment
- **Trigger:** GSE accession from a paper; turns out to be a SuperSeries wrapping multiple platforms.
- **Mechanism:** Default download merges all samples without flagging the structure.
- **Symptom:** Downstream batch correction can't recover the mixed-platform structure; spurious "batch" effects.
- **Fix:** Always check `!Series_relation` in SOFT before pulling; process SubSeries independently.

### Series matrix is not what it appears to be
- **Trigger:** Series matrix downloaded; treated as RMA-normalized when submitter applied additional transforms.
- **Mechanism:** Series matrix contents are at submitter's discretion.
- **Symptom:** Re-analysis gives different answers than the published paper.
- **Fix:** Read `!Sample_data_processing` to know what's in the matrix; re-normalize from raw if in doubt.

### Submitter-provided RNA-seq counts mis-trusted
- **Trigger:** Using a `*_counts.txt.gz` supplementary file as the count matrix.
- **Mechanism:** Submitter's pipeline (aligner, GTF version, counting strategy) is rarely documented.
- **Symptom:** Counts don't agree with re-quantification from SRA FASTQ.
- **Fix:** Pull SRA FASTQ + re-quantify with a known pipeline (Salmon, kallisto, STAR + featureCounts).

### Platform GPL mismatch
- **Trigger:** One GSE with multiple platforms; series matrix split across multiple files.
- **Mechanism:** `GSE_series_matrix.txt.gz` is the merged one; per-platform are `GSE-GPLxxx_series_matrix.txt.gz`.
- **Symptom:** "Missing samples" or NaN-heavy expression matrix.
- **Fix:** Download per-platform matrix files; check `!Series_platform_id` count.

### GEOparse supplementary files flakey
- **Trigger:** `gse.download_supplementary_files()` silently misses files.
- **Mechanism:** Known issue with the GEOparse FTP enumeration since ~2022.
- **Symptom:** Local cache missing CEL or counts files.
- **Fix:** Use R GEOquery or direct FTP `wget -r` on the suppl/ subdirectory.

### ArrayExpress URL rot
- **Trigger:** Old paper links `https://www.ebi.ac.uk/arrayexpress/experiments/E-MTAB-1234/`.
- **Mechanism:** ArrayExpress migrated to BioStudies in 2020.
- **Symptom:** 404 or redirect.
- **Fix:** Use `https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-1234`.

### GEOmetadb stale
- **Trigger:** Old pipeline downloads `GEOmetadb.sqlite` for fast queries.
- **Mechanism:** GEOmetadb unmaintained since 2020.
- **Symptom:** Missing recent series; outdated annotations.
- **Fix:** Switch to pysradb for SRA-linked queries; Entrez gds for full GEO.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| Empty IdList for `gse[entry_type]` | Wrong field name | Use `gse[Entry Type]` (case-sensitive) |
| Matrix file has no expression data | SuperSeries with no aggregate matrix | Pull per-SubSeries matrices |
| Submitter "normalized" matrix gives different result than paper | Hidden submitter transforms | Re-process from raw |
| 404 on ArrayExpress URL | Migrated to BioStudies | Use new BioStudies URL |
| GEOparse missing CEL files | Known flake | Use R GEOquery or direct FTP |
| GEOmetadb-based pipeline missing recent series | DB unmaintained | Switch to pysradb / Entrez |

## References

- Edgar R, Domrachev M, Lash AE. (2002) Gene Expression Omnibus: NCBI gene expression and hybridization array data repository. *Nucleic Acids Res* 30:207-210.
- Barrett T, Wilhite SE, Ledoux P, et al. (2013) NCBI GEO: archive for functional genomics data sets - update. *Nucleic Acids Res* 41:D991-D995.
- Davis S, Meltzer PS. (2007) GEOquery: a bridge between the Gene Expression Omnibus (GEO) and BioConductor. *Bioinformatics* 23:1846-1847.
- Gumienny R. GEOparse: Python library to parse GEO databases. https://github.com/guma44/GEOparse (no journal publication).
- Sarkans U, Gostev M, Athar A, et al. (2018) The BioStudies database--one stop shop for all data supporting a life sciences study. *Nucleic Acids Res* 46:D1266-D1270.
- Lachmann A, Torre D, Keenan AB, et al. (2018) Massive mining of publicly available RNA-seq data from human and mouse. *Nat Commun* 9:1366. (ARCHS4)
- Wilks C, Zheng SC, Chen FY, et al. (2021) recount3: summaries and queries for large-scale RNA-seq expression and splicing. *Genome Biol* 22:323.

## Related Skills

- entrez-search - General gds search
- entrez-link - gds <-> pubmed, bioproject links (gds->sra ELink is unreliable; use pysradb)
- sra-data - Download raw FASTQ from GEO-linked SRA runs
- expression-matrix/normalization - Re-normalize raw expression data
- rna-quantification/alignment-free-quant - Salmon/kallisto re-quantification of GEO/SRA data
- ensembl-rest - Cross-reference Ensembl IDs in series-matrix files
<!-- END FILE: database-access/geo-data/SKILL.md -->

## 子目录：database-access/interaction-databases

<!-- BEGIN FILE: database-access/interaction-databases/SKILL.md -->
---
name: bio-interaction-databases
description: Query protein-protein and gene interaction databases (STRING, BioGRID, IntAct, SIGNOR, Reactome, HuRI, HuMAP, OmniPath, ConsensusPathDB, DIP). Use when building PPI networks, choosing between physical vs functional vs genetic interactions, signed/directed vs undirected, high-throughput vs curated, picking confidence thresholds, aggregating across resources, or navigating license constraints. Encodes the database decision matrix, STRING v12 channel semantics, OmniPath as meta-database, SIGNOR for signed signaling, and per-resource rate limits.
tool_type: python
primary_tool: requests
---

## Version Compatibility

Reference examples tested with: requests 2.31+, pandas 2.2+, networkx 3.2+; STRING v12.0, BioGRID 4.4+, IntAct (live), SIGNOR 3.0+, OmniPath (live)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show requests pandas networkx`
- API surface: confirm endpoint URLs match each resource's current docs

STRING URL is version-pinned (`version-12-0` as of 2024); older URLs (`version-11-5`) were deprecated 2023. The Cytoscape/Cytoscape.js ecosystem uses different version semantics; check the docs for the targeted version.

# Interaction Databases

**"Get protein-protein interactions for these genes"** -> The choice of database matters more than the choice of API. Different resources index different evidence (physical binding, functional association, genetic interaction, signed signaling), with different curation pipelines (manually curated vs high-throughput vs text-mined), different species coverage, and different licenses.

The decision matrix below is the postdoc-grade view: **what question is being asked, and which resource answers it best?**

- Python: `requests.get()` against REST endpoints; `pandas` for parsing; `networkx` for graphs
- R: `STRINGdb`, `OmnipathR` (mature Bioconductor clients)
- Web: STRING, BioGRID, IntAct, SIGNOR, OmniPath, ConsensusPathDB browsers

## Required Setup

```python
import requests
import pandas as pd
import networkx as nx
from io import StringIO

CALLER = 'bioskills-2026'  # STRING + OmniPath accept caller_identity for usage attribution
```

API key requirements:
- **BioGRID**: free key required (`https://webservice.thebiogrid.org/`)
- **STRING, IntAct, SIGNOR, OmniPath, Reactome**: no key

## Decision matrix: which resource for which question?

| Question | Best resource | Why |
|---|---|---|
| "Build a network around 10 genes" | STRING (medium confidence ~400) | Comprehensive; channels combinable; good viz integration |
| "Only physically interacting proteins" | IntAct or BioGRID physical | Curated physical interactions; PSI-MI standard |
| "Signed/directed signaling (phospho, ubiq, etc.)" | **SIGNOR** | Only major DB with mechanism types and direction |
| "Functional enrichment based on co-mentioned genes" | STRING functional (default) | Includes textmining channel |
| "Genetic interactions (synthetic lethality)" | BioGRID genetic | Largest curated genetic interaction set |
| "High-throughput Y2H interactome" | **HuRI** | Reference yeast-2-hybrid map of human |
| "Mass-spec-derived protein complexes" | **HuMAP v2** or BioPlex | AP-MS complex maps |
| "Curated pathways with interactions" | Reactome | Pathway-organized; gold standard for signaling |
| "Meta-database aggregating 100+ sources" | **OmniPath** | The modern "one-stop"; pre-aggregated |
| "Cross-species or non-human" | STRING | Species coverage broadest |
| "Bacterial interactome" | STRING bacterial | Limited curated alternatives |
| "Phosphorylation site-specific" | PhosphoSitePlus (commercial license) or SIGNOR | PSP has best PTM coverage but requires license |

**OmniPath** (Türei et al. 2021 *Mol Sys Biol* 17:e9923) deserves special mention: it aggregates >100 sources into a unified API with provenance tracking. For "give me all available interactions for X" workflows, OmniPath is the modern default.

## STRING (v12, channels, confidence)

STRING (Szklarczyk et al. 2023 *Nucleic Acids Res* 51:D638) aggregates evidence into a combined confidence score. The seven evidence **channels**:

| Channel | What it captures |
|---|---|
| `experiments` | Direct experimental evidence (BioGRID, IntAct, etc.) |
| `database` | Curated database (Reactome, KEGG) |
| `textmining` | Co-mention in PubMed |
| `coexpression` | Co-expression across conditions |
| `neighborhood` | Genomic neighborhood (prokaryotes mainly) |
| `fusion` | Gene fusion across species |
| `cooccurrence` | Phylogenetic profile co-occurrence |

The default `score` is the combined-evidence score (0-1000). Confidence tiers:

| Threshold | Tier | Use when |
|---|---|---|
| 150 | Low | Exploration; includes weak textmining |
| 400 | Medium | Default; balanced sensitivity/specificity |
| 700 | High | Publication-quality networks |
| 900 | Highest | Experimentally validated core only |

**Version pinning**: STRING URL is `https://version-12-0.string-db.org/api/...` as of 2024. Older `version-11-5` URLs were deprecated 2023 — code using them silently fails. Use the unversioned `https://string-db.org/api/...` to follow the current release, or pin to a specific version for reproducibility.

**`caller_identity`**: STRING requests all programmatic users pass `caller_identity=<app-name>` for usage attribution. The parameter helps STRING identify and contact heavy automated callers.

## BioGRID (physical + genetic, curated + HT)

BioGRID (Oughtred et al. 2021 *Protein Sci* 30:187) covers physical and genetic interactions across the broadest organism set of any major resource. Requires a **free API key** (`https://webservice.thebiogrid.org/`).

Key concepts:
- `EXPERIMENTAL_SYSTEM`: e.g. "Two-hybrid", "Affinity Capture-MS", "Synthetic Growth Defect"
- `THROUGHPUT`: "Low Throughput" vs "High Throughput" — the most important quality flag
- `EVIDENCE_TYPE`: physical vs genetic

For high-confidence physical interactions, filter to physical systems + Low Throughput:

```python
PHYSICAL_LT_SYSTEMS = {
    'Affinity Capture-MS', 'Affinity Capture-Western', 'Affinity Capture-RNA',
    'Co-fractionation', 'Co-purification', 'Reconstituted Complex',
    'Co-crystal Structure', 'Two-hybrid', 'Far Western', 'FRET', 'PCA',
}
```

## IntAct (PSI-MI curated physical)

IntAct (Del Toro et al. 2022 *Nucleic Acids Res* 50:D648) is the IMEx consortium reference for curated physical interactions in PSI-MI standard format. MINT was folded in ~2014; queries to MINT URLs now redirect to IntAct.

Direct REST API has changed multiple times; the most stable access is via OmniPath (which wraps IntAct) or via the PSICQUIC web services.

## SIGNOR (signed signaling)

SIGNOR (Lo Surdo et al. 2023 *Nucleic Acids Res* 51:D631) is **the only major curated database with signed, directed, mechanism-typed interactions**. Each edge has:

- `direction`: A->B
- `effect`: `up-regulates`, `down-regulates`, `unknown`
- `mechanism`: `phosphorylation`, `dephosphorylation`, `ubiquitination`, `binding`, etc.

Essential for any signaling pathway analysis or dynamic modeling. Coverage smaller than STRING/BioGRID but quality is high.

## Reactome (curated pathways)

Reactome (Milacic et al. 2024 *Nucleic Acids Res* 52:D672) is gold-standard for human pathway curation with full interaction reactions. Species-specific (human is by far the most complete).

Reactome ContentService REST: `https://reactome.org/ContentService/`.

## HuRI / HuMAP (human-specific interactomes)

- **HuRI** (Luck et al. 2020 *Nature* 580:402): yeast-2-hybrid interactome of human; ~53K binary interactions; biased toward binary high-confidence.
- **HuMAP v2** (Drew et al. 2021 *Mol Syst Biol* 17:e10016): AP-MS-derived complex map; integrates >15,000 proteomic experiments.

Both available for download; HuRI also has a web portal (`http://www.interactome-atlas.org/`).

## OmniPath (meta-database)

OmniPath (Türei et al. 2021 *Mol Syst Biol* 17:e9923) aggregates 100+ sources with provenance. Key endpoints:

| Endpoint | Content |
|---|---|
| `/interactions` | Signaling interactions (directed); the most useful for cross-DB consensus |
| `/enzsub` | Enzyme-substrate (kinase-substrate, etc.) |
| `/complexes` | Protein complexes |
| `/annotations` | Functional annotations |
| `/intercell` | Intercellular communication |

Each interaction includes `sources` (list of contributing databases) and `references` (PMIDs). For "give me everything anyone has said about A-B", OmniPath is the answer.

R users: `OmnipathR` (Bioconductor) is more ergonomic than raw HTTP.

## License gotchas (critical for commercial use)

| Resource | License | Notes |
|---|---|---|
| STRING | Free for all use | Permissive |
| BioGRID | Free, but registration required for bulk | Academic and commercial |
| IntAct | CC-BY (PSI-MI) | Permissive |
| SIGNOR | CC-BY-SA | Share-alike |
| Reactome | CC-BY | Permissive |
| HuRI / HuMAP | CC-BY | Permissive |
| OmniPath | Per-source (mostly permissive) | Check individual sources for commercial use |
| ConsensusPathDB | **Academic only** | Cannot use commercially |
| PhosphoSitePlus | **Commercial license required** | Best PTM coverage but costly |
| Pathway Commons | Per-source | Check sources |

For commercial pipelines, **stick to STRING + BioGRID + IntAct + SIGNOR + Reactome + HuRI/HuMAP + OmniPath** with appropriate source attribution. Avoid ConsensusPathDB and PhosphoSitePlus without legal review.

## Code patterns

### STRING network with confidence threshold and channel inspection

**Goal:** Build a network of interactions among a gene list at a stated confidence; surface which channels contribute.

**Approach:** REST `/network` endpoint; parse channel-specific scores from response columns.

**Reference (STRING v12.0):**
```python
import requests
import pandas as pd
from io import StringIO

STRING = 'https://version-12-0.string-db.org/api'


def get_string_network(genes, species=9606, threshold=700):
    '''threshold: 150 (low), 400 (medium), 700 (high), 900 (highest).'''
    url = f'{STRING}/tsv/network'
    params = {
        'identifiers': '%0d'.join(genes),
        'species': species,
        'required_score': threshold,
        'caller_identity': 'bioskills-2026',
    }
    r = requests.get(url, params=params); r.raise_for_status()
    df = pd.read_csv(StringIO(r.text), sep='\t')
    # Columns: stringId_A, stringId_B, preferredName_A, preferredName_B, ncbiTaxonId,
    # score, nscore (neighborhood), fscore (fusion), pscore (cooccurrence),
    # ascore (coexpression), escore (experiments), dscore (database), tscore (textmining)
    return df


genes = ['TP53', 'BRCA1', 'MDM2', 'ATM', 'CHEK2', 'CDK2']
df = get_string_network(genes, threshold=700)
print(f'{len(df)} interactions at score >= 700')
print('Channel composition for first 5 edges:')
print(df[['preferredName_A', 'preferredName_B', 'score',
          'escore', 'dscore', 'tscore', 'ascore']].head())
```

### BioGRID physical interactions, low-throughput only

**Reference (BioGRID 4.4+):**
```python
BIOGRID = 'https://webservice.thebiogrid.org/interactions/'

# Use the PHYSICAL_LT_SYSTEMS set defined above (the full curated set).
# Importing or re-defining is equivalent; using the same constant keeps the filter consistent.


def biogrid_lt_physical(gene, api_key, taxon=9606):
    params = {
        'accesskey': api_key,
        'format': 'json',
        'searchNames': True,
        'geneList': gene,
        'taxId': taxon,
        'includeInteractors': True,
        'max': 10000,
    }
    r = requests.get(BIOGRID, params=params); r.raise_for_status()
    data = r.json()
    rows = []
    for v in data.values():
        if v['THROUGHPUT'] == 'Low Throughput' and v['EXPERIMENTAL_SYSTEM'] in PHYSICAL_LT_SYSTEMS:
            rows.append({
                'gene_a': v['OFFICIAL_SYMBOL_A'],
                'gene_b': v['OFFICIAL_SYMBOL_B'],
                'system': v['EXPERIMENTAL_SYSTEM'],
                'pmid': v['PUBMED_ID'],
            })
    return pd.DataFrame(rows)
```

### SIGNOR signed signaling

```python
SIGNOR = 'https://signor.uniroma2.it/getData.php'


def signor_for_gene(gene_symbol):
    '''Return signed, directed signaling interactions involving the gene.'''
    params = {'organism': 'human', 'entity': gene_symbol}
    r = requests.get(SIGNOR, params=params); r.raise_for_status()
    rows = []
    for line in r.text.strip().split('\n')[1:]:
        cols = line.split('\t')
        if len(cols) >= 8:
            rows.append({
                'source': cols[0], 'target': cols[1], 'effect': cols[2],
                'mechanism': cols[3], 'pmid': cols[7],
            })
    return pd.DataFrame(rows)
```

### OmniPath interactions (meta-database)

```python
OMNI = 'https://omnipathdb.org'


def omnipath_interactions(genes, types='post_translational'):
    '''types: post_translational, transcriptional, mirna_target, lncrna_target.'''
    params = {
        'genesymbols': 1,
        'fields': 'sources,references,curation_effort,n_resources',
        'partners': ','.join(genes),
        'types': types,
        'license': 'academic',  # or 'commercial' for permissive-only sources
    }
    r = requests.get(f'{OMNI}/interactions', params=params); r.raise_for_status()
    df = pd.read_csv(StringIO(r.text), sep='\t')
    return df


df = omnipath_interactions(['TP53', 'MDM2', 'BRCA1'])
# Rich metadata: directionality, sign, sources, references, curation effort
print(df[['source_genesymbol', 'target_genesymbol', 'is_directed', 'is_stimulation',
          'is_inhibition', 'n_resources', 'n_references']].head())
```

### Multi-resource aggregation

**Goal:** Build a union network of interactions from multiple resources; track provenance per edge.

**Approach:** Query each resource; normalize gene symbols; merge into a networkx Graph with `sources` attribute per edge.

**Reference (requests 2.31+, networkx 3.2+):**
```python
import networkx as nx


def aggregate_networks(genes, biogrid_key=None):
    g = nx.Graph()

    # STRING (high confidence)
    string_df = get_string_network(genes, threshold=700)
    for _, row in string_df.iterrows():
        a, b = sorted([row['preferredName_A'], row['preferredName_B']])
        edge = g.get_edge_data(a, b, default={'sources': set(), 'max_score': 0})
        edge['sources'].add('STRING')
        edge['max_score'] = max(edge['max_score'], row['score'] / 1000.0)
        g.add_edge(a, b, **edge)

    # OmniPath
    omni_df = omnipath_interactions(genes)
    for _, row in omni_df.iterrows():
        a, b = sorted([row['source_genesymbol'], row['target_genesymbol']])
        edge = g.get_edge_data(a, b, default={'sources': set(), 'max_score': 0})
        edge['sources'].add('OmniPath')
        g.add_edge(a, b, **edge)

    # BioGRID (if key available)
    if biogrid_key:
        for gene in genes:
            biogrid_df = biogrid_lt_physical(gene, biogrid_key)
            for _, row in biogrid_df.iterrows():
                a, b = sorted([row['gene_a'], row['gene_b']])
                edge = g.get_edge_data(a, b, default={'sources': set(), 'max_score': 0})
                edge['sources'].add('BioGRID-LT-physical')
                g.add_edge(a, b, **edge)

    return g
```

### Network statistics

```python
def summary(g):
    return {
        'nodes': g.number_of_nodes(),
        'edges': g.number_of_edges(),
        'density': nx.density(g),
        'components': nx.number_connected_components(g),
        'mean_degree': sum(dict(g.degree()).values()) / max(g.number_of_nodes(), 1),
    }


# Edges supported by multiple resources are higher-confidence
high_conf = [(a, b, d) for a, b, d in g.edges(data=True) if len(d['sources']) >= 2]
print(f'Multi-source edges: {len(high_conf)}/{g.number_of_edges()}')
```

## Failure modes

### Confusing functional with physical interactions
- **Trigger:** Treating STRING's combined score as "physically interact".
- **Mechanism:** STRING aggregates seven channels; textmining and coexpression are functional, not physical.
- **Symptom:** Network includes co-mentioned but non-interacting proteins.
- **Fix:** Filter STRING to `experiments` channel only (`escore > threshold`); or use BioGRID/IntAct for strictly physical.

### Wrong confidence tier for the use case
- **Trigger:** Default STRING threshold 400 for a publication network.
- **Mechanism:** Includes weak textmining hits.
- **Symptom:** Network has many low-quality edges; downstream stats inflated.
- **Fix:** Use threshold 700 (high) for publication; 900 for experimentally-validated-core.

### High-throughput interactions trusted as low-throughput
- **Trigger:** Treating Y2H or AP-MS bulk screens like curated low-throughput evidence.
- **Mechanism:** HT screens have higher false-positive rates.
- **Symptom:** Spurious interactions; network overfit to specific screens.
- **Fix:** Filter `THROUGHPUT = 'Low Throughput'` in BioGRID; or use IntAct with curated MI scores.

### Symbol drift
- **Trigger:** Using `MARCH1` for a query; renamed to `MARCHF1` in 2020.
- **Mechanism:** HGNC renamed Excel-autocorrect-affected genes; some resources updated, some didn't.
- **Symptom:** Empty results; or matches to wrong gene.
- **Fix:** Resolve symbols to HGNC IDs first via UniProt or Ensembl; query by ID when possible.

### STRING version drift
- **Trigger:** Code using `version-11-5.string-db.org`.
- **Mechanism:** Deprecated 2023; v12 is the current release.
- **Symptom:** 404 or silent return of stale data.
- **Fix:** Use `version-12-0` (pinned for reproducibility) or `string-db.org` (live).

### License surprise
- **Trigger:** Building a commercial product using ConsensusPathDB.
- **Mechanism:** ConsensusPathDB is academic-only.
- **Symptom:** License violation downstream.
- **Fix:** Audit each resource's license before commercial use; OmniPath has a `license=commercial` parameter that filters to commercially-permissive sources.

### Asymmetric / directional confusion
- **Trigger:** Treating SIGNOR or OmniPath directional edges as undirected.
- **Mechanism:** Signaling edges carry direction and sign; collapsing loses information.
- **Symptom:** Wrong network topology in pathway analysis.
- **Fix:** Use DiGraph (nx.DiGraph) for directed resources; preserve `effect` and `mechanism` attributes.

### Rate limit on bulk STRING queries
- **Trigger:** Looping STRING /network for 1000 gene sets.
- **Mechanism:** STRING asks for one request at a time per `caller_identity`.
- **Symptom:** Connection errors; throttling.
- **Fix:** Sleep 1-2 seconds between calls; respect `caller_identity` rules; for very large batches, use the bulk download.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| STRING 404 | Deprecated `version-11-5` URL | Use `version-12-0` or unversioned |
| BioGRID empty result | Missing API key or wrong taxId | Get key; use NCBI taxon ID |
| Symbol mismatch | HGNC renaming | Resolve via UniProt/Ensembl ID |
| HT interactions inflate network | No throughput filter | Filter `THROUGHPUT = 'Low Throughput'` |
| Functional vs physical confusion | Mixed STRING channels | Filter to `escore` for physical |
| Directional edges collapsed | Used Graph for directed source | Use DiGraph for SIGNOR/OmniPath |
| License violation in commercial pipeline | ConsensusPathDB or PhosphoSitePlus | Switch to permissive sources |
| OmniPath returns nothing | `license=commercial` filter too strict | Drop the filter for academic use |

## References

- Szklarczyk D, Kirsch R, Koutrouli M, et al. (2023) The STRING database in 2023: protein-protein association networks and functional enrichment analyses for any sequenced genome of interest. *Nucleic Acids Res* 51:D638-D646.
- Oughtred R, Rust J, Chang C, et al. (2021) The BioGRID database: A comprehensive biomedical resource of curated protein, genetic, and chemical interactions. *Protein Sci* 30:187-200.
- Del Toro N, Shrivastava A, Ragueneau E, et al. (2022) The IntAct database: efficient access to fine-grained molecular interaction data. *Nucleic Acids Res* 50:D648-D653.
- Lo Surdo P, Iannuccelli M, Contino S, et al. (2023) SIGNOR 3.0, the SIGnaling network open resource 3.0: 2022 update. *Nucleic Acids Res* 51:D631-D637.
- Milacic M, Beavers D, Conley P, et al. (2024) The Reactome Pathway Knowledgebase 2024. *Nucleic Acids Res* 52:D672-D678.
- Luck K, Kim DK, Lambourne L, et al. (2020) A reference map of the human binary protein interactome. *Nature* 580:402-408.
- Drew K, Wallingford JB, Marcotte EM. (2021) hu.MAP 2.0: integration of over 15,000 proteomic experiments builds a global compendium of human multiprotein assemblies. *Mol Syst Biol* 17:e10016.
- Türei D, Valdeolivas A, Gül L, et al. (2021) Integrated intra- and intercellular signaling knowledge for multicellular omics analysis. *Mol Syst Biol* 17:e9923.

## Related Skills

- uniprot-access - Resolve symbols to UniProt accessions
- ensembl-rest - Cross-reference Ensembl IDs in network nodes
- gene-regulatory-networks/coexpression-networks - Co-expression as a complement to PPI
- pathway-analysis/go-enrichment - Functional enrichment of network genes
- pathway-analysis/reactome-pathways - Use Reactome pathways alongside Reactome interactions
- data-visualization/network-visualization - Visualize the resulting networks
<!-- END FILE: database-access/interaction-databases/SKILL.md -->

## 子目录：database-access/local-blast

<!-- BEGIN FILE: database-access/local-blast/SKILL.md -->
---
name: bio-local-blast
description: Build local BLAST databases and run searches using NCBI BLAST+ command-line tools. Use when running >50 queries, building custom databases with -parse_seqids and -taxid, downloading prebuilt NCBI databases via update_blastdb.pl, choosing -task variants (megablast/dc-megablast/blastn/blastn-short), tuning soft/hard masking, scaling threads, or extracting hits with blastdbcmd. Encodes BLAST v5 vs v4 database format, taxonomy filtering, makeblastdb pitfalls.
tool_type: cli
primary_tool: BLAST+
---

## Version Compatibility

Reference examples tested with: NCBI BLAST+ 2.15+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `blastn -version` then `blastn -help` to confirm flags
- CLI: `makeblastdb -help` to confirm database build options

If a flag is unrecognized or behavior changes, introspect with `-help` and adapt the example to match the installed version rather than retrying.

# Local BLAST

**"Run BLAST locally for speed and control"** -> Build or download a BLAST+ database, run the appropriate program with carefully chosen `-task`, masking, and thread settings, parse tabular output. Local BLAST is the right tool when remote is rate-limited or when the database must be reproducible (frozen).

The biggest mistakes are (a) using `nt`/`nr` without realizing they're >250 GB and grow weekly, (b) not building with `-parse_seqids` and then being unable to extract hit sequences with `blastdbcmd`, (c) using default `blastn` for cross-species when `dc-megablast` is correct, and (d) thinking `-num_threads 32` will scale -- past ~16 threads BLAST is I/O bound.

- CLI: `makeblastdb`, `blastn`/`blastp`, `blastdbcmd`, `update_blastdb.pl` (NCBI BLAST+)
- Python: `subprocess` wrapper (preferred); `Bio.Blast.Applications` was deprecated and removed -- do not use

## Installation

```bash
# conda (preferred)
conda install -c bioconda blast

# macOS
brew install blast

# Ubuntu
sudo apt install ncbi-blast+

# Verify
blastn -version    # NCBI BLAST+ 2.15+ expected
update_blastdb.pl --showall pretty | head
```

## Database format: v5 vs v4

NCBI introduced BLAST database v5 in BLAST+ 2.10 (2020). v5 includes taxonomy indexing directly in the database files, enabling `-taxids` and `-taxidlist` filtering without a companion file. v4 databases require `taxonomy4blast.sqlite3` to be present and discoverable.

| Feature | v4 | v5 |
|---|---|---|
| Default for prebuilt NCBI dbs | No (legacy) | Yes (since 2020) |
| `-taxids`, `-taxidlist` support | No | Yes |
| `blastdbcmd -taxids` | No | Yes |
| New `-info` output fields | No | Yes |

`update_blastdb.pl` downloads v5 by default. When building a database manually with `makeblastdb`, v5 format requires `-blastdb_version 5`. **Always pass `-blastdb_version 5` and `-parse_seqids` when building from scratch.**

## `makeblastdb` flag taxonomy

| Flag | Effect | When |
|---|---|---|
| `-dbtype nucl` or `-dbtype prot` | Required | Always |
| `-parse_seqids` | Indexes accessions so `blastdbcmd -entry <acc>` works | Almost always (downstream extraction) |
| `-hash_index` | Speeds up extraction by accession | Large dbs |
| `-blastdb_version 5` | Use v5 format | Always |
| `-taxid 9606` | Single taxid for all seqs | Single-species DB |
| `-taxid_map file.tsv` | Per-sequence taxid mapping (seqid<TAB>taxid) | Multi-species DB |
| `-mask_data masking.asnb` | Apply precomputed soft-masking | Production pipelines |
| `-title "..."` | Free-text label | Cosmetic |
| `-out path/prefix` | DB file path prefix | Always |

```bash
makeblastdb -in reference.fasta -dbtype nucl \
            -blastdb_version 5 \
            -parse_seqids \
            -hash_index \
            -title "Custom reference 2026-05" \
            -out custom_db
```

## `-task` taxonomy (the most-misused BLAST setting)

For `blastn`, the `-task` flag picks among heuristics with different word sizes and gap parameters.

| `-task` | Word | Gapped | Use case | Mistake to avoid |
|---|---|---|---|---|
| `megablast` (default) | 28 | linear | >=95% identity, intra-species, primer hits, contamination check | Used for cross-species and misses everything |
| `dc-megablast` | 11 (discontiguous) | yes | Cross-species mRNA homology | Underused -- this is what `blastn` "should" be for cross-species |
| `blastn` | 11 | yes | General sensitive DNA | Slower than dc-megablast for same job |
| `blastn-short` | 7 | yes | Queries <50 nt (primers, small RNAs) | Default megablast can't seed at length 7 |
| `rmblastn` | 11 | yes | Repeat masking; bundled with RepeatModeler | Specialized |

For `blastp`:

| `-task` | Word | Use case |
|---|---|---|
| `blastp` (default) | 3 | General protein similarity |
| `blastp-fast` | 6 | Faster, less sensitive |
| `blastp-short` | 2 | Peptides <30 aa, with PAM30 + word_size=2 typical |

## Soft vs hard masking

| Setting | Effect on seed | Effect on extension | Effect on score |
|---|---|---|---|
| `-soft_masking true` (default for several tasks) | Skip masked positions when seeding | Allow extension through masked | Score includes masked positions |
| `-soft_masking false` + `-dust yes` / `-seg yes` | Skip masked positions when seeding | Skip masked positions in extension | Score excludes masked positions |
| Hard-mask in input FASTA (N or X) | Hard exclusion everywhere | Hard exclusion | Treated as mismatches |

Soft masking is correct for almost all cases. Hard masking creates artificial mismatches at masked boundaries and can split true alignments. The exception: searching against a database of repeats explicitly, where hard masking on the query is the right choice.

## Thread scaling

BLAST+ parallelizes per-query (with `-num_threads`) but is I/O bound past ~16 threads on most hardware. For >100,000 query batches the better answer is splitting the input FASTA into N chunks and running N parallel `blastn` invocations -- this saturates CPUs better than `-num_threads 64`.

| Threads | Typical speedup vs single | Notes |
|---|---|---|
| 1-8 | Near-linear | Default sweet spot |
| 8-16 | Sub-linear (1.5-2x over 8) | Useful on big SMP boxes |
| 16-32 | Diminishing returns | I/O bound for most DBs |
| 32+ | Often slower | Cache thrash + I/O contention |

For massive workflows, prefer **DIAMOND** (Buchfink et al. 2021 *Nat Methods* 18:366) or **MMseqs2** (Steinegger & Soding 2017 *Nat Biotechnol* 35:1026) -- 100-10,000x faster than BLASTP at comparable sensitivity. See `remote-homology` skill.

## Output format reference (`-outfmt`)

| `-outfmt` | Description | Use |
|---|---|---|
| 0 | Pairwise (default; human-readable) | Debugging, inspection |
| 5 | XML | Programmatic parsing (Bio.SearchIO) |
| 6 | Tabular (no header) | Most pipelines |
| 7 | Tabular with comment headers | Self-documenting |
| 11 | ASN.1 binary | Re-parse with later versions |

Custom tabular fields:
```bash
blastn -query q.fa -db db -outfmt "6 qseqid sseqid pident length qcovs qcovhsp evalue bitscore staxids sscinames stitle"
```

Field key fields for analysis:
- `pident` = percent identity over the HSP (NOT the query); for query-level, use `qcovhsp`
- `qcovs` = total query coverage by all HSPs of this subject (the "coverage" most users want)
- `qcovhsp` = query coverage by best HSP alone (use when there's only one HSP per hit)
- `staxids` = taxonomy IDs (v5 only); critical for any "what species" workflow

## Prebuilt NCBI databases via `update_blastdb.pl`

```bash
# List available
update_blastdb.pl --showall pretty | grep -E 'refseq|swissprot|nt|nr'

# Download (with decompress)
update_blastdb.pl --decompress refseq_select_rna

# Download specific volume of split database
update_blastdb.pl --decompress refseq_protein

# Download with parallelism
update_blastdb.pl --decompress --num_threads 4 refseq_select_rna
```

Sizes (approximate, 2026):
- `refseq_select_rna`: ~5 GB
- `refseq_protein`: ~30 GB
- `swissprot`: <1 GB
- `nt`: ~250 GB
- `nr`: ~300 GB

For most use cases, `refseq_select_*` is the right starting point. `nt`/`nr` are storage-heavy and reproducibility-hostile.

## Code patterns

### Build and search a custom protein database

**Goal:** Build a BLAST+ protein database from a custom FASTA and search against it.

**Approach:** `makeblastdb` with v5 + parse_seqids + hash_index; `blastp` with explicit outfmt.

**Reference (NCBI BLAST+ 2.15+):**
```bash
#!/bin/bash
# Reference: NCBI BLAST+ 2.15+ | Verify API if version differs

REF=reference_proteins.fasta
DB=ref_prot_db
QUERY=query.fasta
OUT=hits.tsv

makeblastdb -in "$REF" -dbtype prot \
            -blastdb_version 5 -parse_seqids -hash_index \
            -title "$REF $(date +%Y-%m-%d)" \
            -out "$DB"

blastp -query "$QUERY" -db "$DB" \
       -evalue 1e-10 \
       -num_threads 8 \
       -max_target_seqs 500 \
       -outfmt "6 qseqid sseqid pident length qcovs evalue bitscore stitle" \
       -out "$OUT"

# Top hit per query by bit-score (column 7)
sort -k1,1 -k7,7gr "$OUT" | awk '!seen[$1]++' > top_hit_per_query.tsv
```

### Cross-species DNA with dc-megablast

```bash
blastn -query mouse_cdna.fa -db human_refseq_rna \
       -task dc-megablast \
       -word_size 11 \
       -evalue 1e-10 \
       -outfmt "6 qseqid sseqid pident length qcovs evalue bitscore" \
       -num_threads 8 \
       -out cross_species.tsv
```

### Short primer search

```bash
blastn -query primers.fa -db genome_db \
       -task blastn-short \
       -word_size 7 \
       -evalue 1000 \
       -outfmt 6 \
       -out primer_hits.tsv
```

### Taxonomy-filtered search (BLAST v5 only)

```bash
# Restrict to specific taxids
blastp -query query.fa -db nr \
       -taxids 9606,10090,10116 \
       -outfmt "6 qseqid sseqid staxids sscinames evalue bitscore" \
       -out mammalian_hits.tsv

# Or to a taxid subtree (NCBI BLAST+ 2.13+)
echo 9606 > human_only.txt
blastp -query query.fa -db nr -taxidlist human_only.txt -outfmt 6 -out human_hits.tsv
```

### Extract subject sequences for top hits

```bash
# Requires database built with -parse_seqids
cut -f2 top_hit_per_query.tsv | sort -u > hit_accessions.txt
blastdbcmd -db ref_prot_db -entry_batch hit_accessions.txt -out hits.fasta

# Pull a range of a sequence
blastdbcmd -db genome_db -entry NC_000001.11 -range 1000000-1001000 -out region.fa
```

### Reciprocal best hit (RBH) for ortholog candidates

See `ortholog-inference` skill for the principled treatment. Quick version:

```bash
blastp -query A.fa -db B_db -outfmt 6 -evalue 1e-5 -num_threads 8 \
       -max_target_seqs 5 -out A_vs_B.tsv
blastp -query B.fa -db A_db -outfmt 6 -evalue 1e-5 -num_threads 8 \
       -max_target_seqs 5 -out B_vs_A.tsv

# Best forward + reverse, intersect
awk '!seen[$1]++ {print $1"\t"$2}' A_vs_B.tsv | sort > A_best
awk '!seen[$1]++ {print $1"\t"$2}' B_vs_A.tsv | sort > B_best
awk 'NR==FNR{a[$1]=$2; next} a[$2]==$1' A_best B_best > rbh.tsv
```

This works but does NOT handle paralog mis-pairs from gene duplication; for that use OrthoFinder or OMA (in `ortholog-inference`).

### Python wrapper with version pinning

```python
import subprocess
import shutil


def require_tool(name, min_version=None):
    if not shutil.which(name):
        raise RuntimeError(f'{name} not on PATH')
    out = subprocess.run([name, '-version'], capture_output=True, text=True)
    print(f'  {out.stdout.strip().splitlines()[0]}')


def run_blast(query, db, out, program='blastp', evalue=1e-10, threads=8, hitlist=500):
    require_tool(program)
    cmd = [program, '-query', query, '-db', db, '-out', out,
           '-evalue', str(evalue),
           '-num_threads', str(threads),
           '-max_target_seqs', str(hitlist),
           '-outfmt', '6 qseqid sseqid pident length qcovs qcovhsp evalue bitscore stitle']
    subprocess.run(cmd, check=True)


def parse_tabular(path):
    cols = ['qseqid', 'sseqid', 'pident', 'length', 'qcovs', 'qcovhsp', 'evalue', 'bitscore', 'stitle']
    rows = []
    with open(path) as f:
        for line in f:
            vals = line.rstrip('\n').split('\t')
            d = dict(zip(cols, vals))
            for k in ('pident', 'qcovs', 'qcovhsp', 'evalue', 'bitscore'):
                d[k] = float(d[k])
            d['length'] = int(d['length'])
            rows.append(d)
    return rows
```

## Failure modes

### `nt`/`nr` size shock
- **Trigger:** `update_blastdb.pl --decompress nt` without realizing the size.
- **Mechanism:** `nt` is ~250 GB compressed, ~1 TB indexed.
- **Symptom:** Disk fills mid-download; partial DB unusable.
- **Fix:** Use `refseq_select` for most workflows; only pull `nt`/`nr` with intent and >1 TB free.

### Missing `-parse_seqids`
- **Trigger:** Built DB without `-parse_seqids`; later try `blastdbcmd -entry`.
- **Mechanism:** Without the parsed index, `blastdbcmd` can't look up by accession.
- **Symptom:** `Error: ... not found in database`.
- **Fix:** Rebuild with `-parse_seqids` (cheap if FASTA still on disk).

### Wrong `-task` for the question
- **Trigger:** Default `blastn` for cross-species mRNA (word=11 but ungapped seeding).
- **Mechanism:** Discontiguous seed (`dc-megablast`) is much more sensitive across species.
- **Symptom:** Far fewer hits than the question warrants.
- **Fix:** Use `-task dc-megablast` for cross-species; `-task megablast` only for >=95% identity.

### Thread saturation
- **Trigger:** `-num_threads 64` on a 32-core box.
- **Mechanism:** I/O bound past ~16 threads; cache thrash hurts past CPU count.
- **Symptom:** No speedup or slowdown.
- **Fix:** Cap at 8-16; split FASTA and run parallel processes instead for very large batches.

### v4 database, expecting v5 features
- **Trigger:** Old prebuilt DB; `-taxids` flag returns "Taxonomy database not available".
- **Mechanism:** v4 needs `taxonomy4blast.sqlite3` companion; v5 has taxonomy indexed in DB.
- **Symptom:** Taxonomy filtering silently no-ops or errors.
- **Fix:** Re-download with `update_blastdb.pl --decompress` (gets v5); or use v5 explicitly when building.

### Soft-masking confusion
- **Trigger:** Hard-masking input (replacing repeats with N or X) instead of using `-dust`/`-seg`.
- **Mechanism:** Hard-mask creates artificial mismatches at boundaries.
- **Symptom:** True alignments split into multiple short HSPs.
- **Fix:** Pass unmasked FASTA + soft-mask via `-soft_masking true` + `-dust yes`/`-seg yes`.

### `max_target_seqs` truncation
- **Trigger:** `-max_target_seqs 10` (Shah et al. 2019 *Bioinformatics* 35:1613).
- **Mechanism:** Early termination, not top-N filter.
- **Symptom:** Different top-10 than `-max_target_seqs 500` + post-filter.
- **Fix:** Set `-max_target_seqs` large (500+); filter top N in awk/Python.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `BLAST Database error` | DB path wrong, or alias missing | `blastdbcmd -db <db> -info` to confirm |
| `Error: entry not found` | Built without `-parse_seqids` | Rebuild |
| Taxonomy filter no-op | v4 DB | Upgrade to v5 |
| Threads >16 not faster | I/O bound | Split input + parallel invocations |
| `nt` download fills disk | Database is huge | Use refseq_select |
| `Sequence too short` | Query < word_size | Use `-task blastn-short` (word=7) |
| Out of memory | Single large query | Reduce `-num_threads`, split query |

## References

- Camacho C, Coulouris G, Avagyan V, Ma N, Papadopoulos J, Bealer K, Madden TL. (2009) BLAST+: architecture and applications. *BMC Bioinformatics* 10:421.
- Altschul SF, Madden TL, Schaffer AA, Zhang J, Zhang Z, Miller W, Lipman DJ. (1997) Gapped BLAST and PSI-BLAST: a new generation of protein database search programs. *Nucleic Acids Res* 25:3389-3402.
- Shah N, Nute MG, Warnow T, Pop M. (2019) Misunderstood parameter of NCBI BLAST impacts the correctness of bioinformatics workflows. *Bioinformatics* 35:1613-1614.
- Boratyn GM, Camacho C, Cooper PS, et al. (2013) BLAST: a more efficient report with usability improvements. *Nucleic Acids Res* 41:W29-W33.

## Related Skills

- blast-searches - Remote BLAST against NCBI servers
- remote-homology - PSI-BLAST, jackhmmer, HHblits, MMseqs2, DIAMOND, Foldseek for distant homology
- ortholog-inference - Reciprocal best hit, OrthoFinder, OMA for ortholog calls
- sequence-io/read-sequences - Load query/reference FASTA files
- batch-downloads - Download large reference FASTA sets before makeblastdb
<!-- END FILE: database-access/local-blast/SKILL.md -->

## 子目录：database-access/ncbi-datasets-cli

<!-- BEGIN FILE: database-access/ncbi-datasets-cli/SKILL.md -->
---
name: bio-ncbi-datasets-cli
description: Download genome assemblies, gene records, and ortholog data from NCBI using the modern Datasets v2 CLI (replaces assembly_summary.txt scraping and many EFetch workflows). Use when bulk-pulling genome assemblies, gene metadata across species, ortholog sets, or BLAST databases; when E-utilities are too slow for genome-scale work; or when automatic checksum verification, parallel download, and clean accession-driven retrieval are required. Encodes the JSON-lines output format, dataformat conversion, --dehydrated for cloud workflows, and when Datasets is/isn't the right tool.
tool_type: cli
primary_tool: NCBI Datasets CLI
---

## Version Compatibility

Reference examples tested with: NCBI Datasets CLI 16.0+ (2024), dataformat 16.0+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `datasets --version`, `dataformat --version`
- Subcommand help: `datasets <subcommand> --help`

If a subcommand or flag is unrecognized, run `datasets --help` and adapt. The CLI is under active development; major releases (v15 -> v16) added subcommands and renamed flags.

# NCBI Datasets CLI

**"Pull genome / gene / ortholog data from NCBI in 2026"** -> The Datasets v2 CLI (launched 2023) is the official, supported bulk endpoint for genome and gene-centric data. It replaces the prior best-practice of scraping `assembly_summary.txt` + parallel FTP + manual checksum verification. For genome-scale data, it is strictly better than E-utilities (EFetch).

The CLI is not the right answer for everything. PubMed, SRA reads, and custom Entrez queries still belong to E-utilities. The defection rule: **if the question is about genome assemblies, gene records, or pre-computed orthologs, use Datasets; otherwise stay with E-utilities**.

- CLI: `datasets download genome accession GCF_...`
- CLI: `datasets summary gene symbol BRCA1 --taxon human`
- Python: `subprocess` wrapper; Python client `ncbi-datasets-pylib` (experimental as of 2024)

## Installation

```bash
# conda
conda install -c conda-forge ncbi-datasets-cli

# Or direct download (Linux, macOS, Windows binaries)
curl -O https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets

datasets --version    # 16.0+ expected
dataformat --version  # bundled companion tool
```

## What's in scope (use Datasets) vs out of scope (use E-utilities or other tools)

| Question | Datasets | Use instead |
|---|---|---|
| Genome assembly download | yes | — |
| All reference genomes for a taxon | yes | — |
| Gene record metadata (multi-species) | yes | — |
| Ortholog data for a gene | yes (`datasets summary gene ... --ortholog`) | OrthoDB / Compara for tree-aware orthology |
| Virus data (assemblies, metadata) | yes (`datasets download virus`) | — |
| Annotation files (GFF3, GTF) for a genome | yes | — |
| Protein records (curated, with cross-refs) | partial | UniProt REST for richer annotation |
| PubMed | no | `entrez-search` / `entrez-fetch` |
| SRA reads | no | `sra-data` |
| BLAST | no | `blast-searches` / `local-blast` |
| Custom Entrez queries | no | `entrez-search` |
| Pre-computed alignments (Compara) | no | `ensembl-rest` |

## Subcommand taxonomy

| Subcommand | Purpose | Example |
|---|---|---|
| `datasets summary genome` | Metadata only; JSON output | `datasets summary genome accession GCF_000001405.40` |
| `datasets download genome` | Download data files | `datasets download genome accession GCF_...` |
| `datasets summary gene` | Gene record metadata | `datasets summary gene symbol BRCA1 --taxon human` |
| `datasets download gene` | Download gene products | `datasets download gene symbol BRCA1 --taxon human` |
| `datasets summary taxonomy` | Taxonomy info | `datasets summary taxonomy taxon human` |
| `datasets download virus` | Virus assemblies/proteins | `datasets download virus genome taxon SARS-CoV-2` |
| `dataformat tsv` / `dataformat excel` | Convert JSON-lines to tabular | `dataformat tsv gene-summary` |

`datasets summary` always returns JSON-lines on stdout (one object per record). `datasets download` produces a `.zip` (default) or a "dehydrated" stub for cloud workflows.

## Key parameters (download)

| Flag | Effect |
|---|---|
| `--filename out.zip` | Where to write the archive |
| `--include genome,gff3,gtf,protein,cds,rna,seq-report` | Which file types to include |
| `--reference` | Restrict to reference assemblies only (one per species) |
| `--annotated` | Restrict to annotated assemblies |
| `--assembly-source RefSeq` / `GenBank` / `all` | Database source |
| `--assembly-level chromosome,complete` | Assembly quality level |
| `--released-after 2024-01-01` | Date filter |
| `--dehydrated` | Skip data; download just stubs + URL list (for parallel pull) |
| `--api-key XXX` | Optional API key (raises rate limit) |
| `--no-progressbar` | For non-interactive use |

For very large pulls (1000+ genomes), `--dehydrated` is the right choice: download the metadata stubs first, then run `datasets rehydrate` later or pull URLs in parallel from the manifest.

## JSON-lines output + dataformat

`datasets summary` returns JSON-lines (one JSON object per line) on stdout. Pipe through `dataformat tsv` for tabular:

```bash
datasets summary genome taxon "Escherichia coli" --reference --as-json-lines \
  | dataformat tsv genome --fields accession,organism-name,assembly-level,scaffold-n50 \
  > ecoli_refs.tsv
```

`dataformat` subcommands match summary types: `genome`, `gene`, `virus-genome`, etc. The `--fields` list is documented per type via `dataformat tsv <type> --help`.

## When to use --dehydrated for cloud workflows

The "dehydrated" mode separates data discovery from data transfer:

1. **Discover**: `datasets download genome taxon human --reference --dehydrated --filename human.zip` (fast; ~MB).
2. **Inspect**: `unzip -p human.zip ncbi_dataset/fetch.txt` -- a TSV of all URLs to pull.
3. **Pull**: either `datasets rehydrate --directory ./human/` or use `aria2c --input-file=fetch.txt` for parallel pull.

This is essential for HPC / cloud pipelines where inspection of the pending transfer is needed before committing the I/O.

## Checksum verification (automatic)

`datasets` verifies MD5 checksums for every downloaded file automatically. Rehydrate workflows also verify. If a file fails checksum, Datasets retries up to 3 times then errors. This replaces the `md5sum -c` step that was required with assembly_summary.txt-based scraping.

## Code patterns

### Download a single reference genome

**Goal:** Get human reference assembly with genome + GTF + protein + CDS.

**Approach:** `datasets download genome accession ... --include ...`.

**Reference (NCBI Datasets CLI 16.0+):**
```bash
#!/bin/bash
# Reference: NCBI Datasets CLI 16.0+ | Verify API if version differs

datasets download genome accession GCF_000001405.40 \
    --include genome,gff3,gtf,protein,cds,seq-report \
    --filename human_grch38.zip

unzip -q human_grch38.zip -d human_grch38/
ls -lh human_grch38/ncbi_dataset/data/GCF_000001405.40/
```

### Bulk download all reference bacterial genomes

**Goal:** Pull every RefSeq reference bacterial assembly with annotation.

**Approach:** `--dehydrated` first for inspection; rehydrate with parallel pull.

**Reference (NCBI Datasets CLI 16.0+):**
```bash
#!/bin/bash
# Step 1: dehydrated discovery
datasets download genome taxon Bacteria \
    --reference --annotated --assembly-source RefSeq \
    --include genome,gff3,protein \
    --dehydrated --filename bact_refs.zip

unzip -q bact_refs.zip -d bact_refs/
wc -l bact_refs/ncbi_dataset/fetch.txt   # how many files will be pulled

# Step 2: parallel pull via aria2 (or datasets rehydrate)
aria2c --input-file=bact_refs/ncbi_dataset/fetch.txt \
       --dir=bact_refs/ncbi_dataset/data/ \
       --max-concurrent-downloads=8 \
       --retry-wait=5
```

### Gene metadata across species

```bash
datasets summary gene symbol BRCA1 \
    --taxon Mammalia \
    --as-json-lines \
  | dataformat tsv gene --fields gene-id,symbol,taxname,description,nomenclature-authority,chromosomes \
  > brca1_mammals.tsv

head brca1_mammals.tsv
```

### Find orthologs for a gene

```bash
datasets summary gene symbol BRCA1 --taxon human --ortholog --as-json-lines \
  | dataformat tsv gene --fields gene-id,symbol,taxname,description \
  > brca1_orthologs.tsv
```

`--ortholog` returns NCBI's ortholog set (a single representative per species; tree-aware orthology with multiple co-orthologs is in `ortholog-inference` / Compara / OMA).

### Filter assemblies by quality and date

```bash
datasets summary genome taxon "Salmonella enterica" \
    --assembly-level chromosome,complete \
    --released-after 2024-01-01 \
    --as-json-lines \
  | dataformat tsv genome --fields accession,organism-name,assembly-level,scaffold-n50,submission-date \
  > sal_2024.tsv
```

### Python wrapper with checksum + retry awareness

**Reference (NCBI Datasets CLI 16.0+):**
```python
import subprocess
import json
from pathlib import Path


def datasets_summary(subcommand, *args):
    '''Run `datasets summary` and parse JSON-lines stdout.'''
    cmd = ['datasets', 'summary', subcommand, *args, '--as-json-lines']
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return [json.loads(line) for line in out.stdout.strip().split('\n') if line]


def datasets_download(subcommand, *args, out='dataset.zip', include=None):
    cmd = ['datasets', 'download', subcommand, *args, '--filename', out]
    if include:
        cmd += ['--include', ','.join(include)]
    subprocess.run(cmd, check=True)
    return Path(out)


genomes = datasets_summary('genome', 'taxon', 'Escherichia coli', '--reference')
print(f'{len(genomes)} reference E. coli assemblies')
for g in genomes[:3]:
    acc = g.get('accession')
    n50 = g.get('assemblyStats', {}).get('contigN50')
    print(f'  {acc}  N50={n50}')

datasets_download('genome', 'accession', 'GCF_000005845.2',
                  out='ecoli_k12.zip',
                  include=['genome', 'gff3', 'protein'])
```

### Comparison vs E-utilities

```python
# E-utilities path: ESearch in assembly db -> ESummary -> manual FTP pull
#   ~30 API calls + manual md5 + serial download
# Datasets path:
#   datasets download genome accession GCF_...  # one command, automatic md5, parallel inside
```

For genome workflows, Datasets is 5-50x faster than the equivalent E-utilities pipeline and far more reliable.

## Failure modes

### Choosing Datasets for the wrong question
- **Trigger:** Trying to pull raw SRA reads via Datasets.
- **Mechanism:** Datasets covers genome/gene/ortholog, not raw reads.
- **Symptom:** Subcommand not found or empty result.
- **Fix:** Use `sra-data` skill (prefetch/fasterq-dump) for raw reads.

### `--reference` filter loses too much
- **Trigger:** Bulk pull of "all assemblies for a species"; `--reference` returns one per species.
- **Mechanism:** Reference subset is the canonical single representative.
- **Symptom:** Far fewer assemblies than expected for a species with hundreds of submissions.
- **Fix:** Drop `--reference` for full set; add `--assembly-level chromosome,complete` for quality filter instead.

### Dehydrated workflow forgotten
- **Trigger:** 1000-genome pull without `--dehydrated`.
- **Mechanism:** Datasets downloads serially within one ZIP; can take hours.
- **Symptom:** Slow; no parallelism; one giant ZIP.
- **Fix:** Use `--dehydrated` + aria2c with `--max-concurrent-downloads`.

### dataformat field name guessing
- **Trigger:** `dataformat tsv genome --fields foo,bar` with invented field names.
- **Mechanism:** Field names are constrained per summary type.
- **Symptom:** "Unknown field" error.
- **Fix:** `dataformat tsv genome --help` lists valid field names; pull JSON-lines and inspect with `jq` to discover fields.

### Old assembly_summary.txt-based scripts still in use
- **Trigger:** Legacy pipeline scraping `https://ftp.ncbi.nlm.nih.gov/genomes/all/refseq/...`.
- **Mechanism:** Pre-2023 best practice; FTP listing parsing is fragile.
- **Symptom:** Slow; brittle; no checksums; broken when NCBI restructures FTP.
- **Fix:** Switch to Datasets CLI; the FTP path still works but Datasets is the supported modern path.

### API key not used for high-volume
- **Trigger:** 1000+ summary calls in a loop without `--api-key`.
- **Mechanism:** NCBI rate-limits unauthenticated bulk traffic.
- **Symptom:** Throttling; slow downloads.
- **Fix:** Pass `--api-key YOUR_KEY` to bulk commands; obtain from `https://www.ncbi.nlm.nih.gov/account/settings/`.

### CLI version drift
- **Trigger:** Using Datasets v14 with v16 docs.
- **Mechanism:** Subcommands and flags renamed between major versions.
- **Symptom:** "Unknown flag" or different output structure.
- **Fix:** Pin to v16+; `conda update ncbi-datasets-cli`.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| "command not found: datasets" | Not installed | `conda install -c conda-forge ncbi-datasets-cli` |
| Subcommand not found | Old version | Upgrade to v16+ |
| Slow 1000-genome pull | Serial download | Use `--dehydrated` + aria2c |
| "Unknown field" in dataformat | Wrong field name | Check `dataformat <type> --help` |
| Throttled bulk pull | No API key | Pass `--api-key` |
| `--reference` returns 1 per species | By design | Drop the flag or use `--assembly-level` |
| MD5 mismatch retried | Network issue | Datasets retries automatically; persistent failure -> investigate network |

## References

- O'Leary NA, Cox E, Holmes JB, et al. (2024) Exploring and retrieving sequence and metadata for species across the tree of life with NCBI Datasets. *Sci Data* 11:732.
- NCBI Datasets documentation: https://www.ncbi.nlm.nih.gov/datasets/docs/v2/
- NCBI. Datasets CLI usage. https://www.ncbi.nlm.nih.gov/datasets/docs/v2/reference-docs/command-line/datasets/

## Related Skills

- entrez-search - For PubMed, custom queries, and non-genome data
- entrez-fetch - For single-record fetches outside genome/gene scope
- batch-downloads - Bulk E-utilities (when not genome-scale)
- sra-data - Raw sequencing reads (NOT covered by Datasets)
- ensembl-rest - Ensembl REST as alternative for Ensembl-native species
- ortholog-inference - Compara/OMA/OrthoDB for tree-aware orthology
<!-- END FILE: database-access/ncbi-datasets-cli/SKILL.md -->

## 子目录：database-access/ortholog-inference

<!-- BEGIN FILE: database-access/ortholog-inference/SKILL.md -->
---
name: bio-ortholog-inference
description: Pull pre-computed ortholog calls from public databases (OrthoDB, Ensembl Compara, OMA browser, eggNOG, PANTHER, KEGG Orthology, HomoloGene) via their REST APIs. Use when orthologs are already curated upstream, when the question is "what is the X ortholog of Y" rather than "how to infer orthology de novo", when batch-mapping gene IDs across species, or when comparing the resources for consensus calls. Encodes confidence-level semantics, 1:1 vs 1:many vs many:many, HomoloGene deprecation, and when to defect to de novo computation.
tool_type: python
primary_tool: requests
---

## Version Compatibility

Reference examples tested with: requests 2.31+, pandas 2.2+; OrthoDB v12 API, Ensembl REST (Ensembl release 112+), OMA REST API, eggNOG 6.0+, PANTHER v18+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show requests pandas`
- API surface: confirm endpoint URLs and JSON schema match the current API docs

If endpoints return 404 or unexpected JSON, check release notes for the resource; schema migrations happen with each major version (Ensembl release is the biggest moving target).

# Ortholog Inference (Database Access)

**"What is the X ortholog of gene Y?"** -> Many ortholog resources have already done the inference at scale. Pulling their answers is faster and often more reliable than re-computing. This skill is the **database-access** view: how to query the major orthology resources programmatically, what their confidence semantics mean, and when their disagreements matter.

For **de novo orthology inference** (running OrthoFinder, SonicParanoid, OMA standalone on local proteomes), see `comparative-genomics/ortholog-inference` — that's a much deeper treatment of the computational side.

This skill is about pulling answers from:
- **OrthoDB v12** — broadest coverage (1700+ species), levels from species-specific to deep
- **Ensembl Compara** — vertebrate-focused, tree-reconciled, confidence scores
- **OMA browser** — high precision, HOG (Hierarchical Orthologous Group) framework
- **eggNOG 6.0** — pre-computed functional groups, deepest functional annotation
- **PANTHER** — protein family + ortholog calls with experimentally validated curation
- **KEGG Orthology (KO)** — pathway-centric orthologous functional units
- **HomoloGene** — deprecated since 2014, but data still queryable for legacy comparison

- Python: `requests.get()` against REST endpoints; `pandas` for parsing
- CLI: `curl` against the same endpoints; OrthoDB also has bulk downloads

## Required Setup

```python
import requests
import pandas as pd
import time
```

No API keys required for any of these resources (as of 2026), but rate limits apply — see per-resource notes below.

## Decision matrix: which resource for which question?

| Question | Resource | Why |
|---|---|---|
| Ortholog of human gene X in mouse | Ensembl Compara | Best-curated for vertebrates; confidence score per call |
| Ortholog of gene X across all 1700+ species | OrthoDB | Broadest taxonomic coverage |
| Single-copy orthologs for phylogenomics | OrthoDB at species-tree level | Pre-computed; large taxonomic groups |
| Functional annotation transfer | eggNOG-mapper or eggNOG API | OG-based functional categories |
| Pathway-centric orthology (KEGG pathways) | KEGG Orthology (KO) | KO IDs link directly to pathway maps |
| Curated function-aware orthologs | PANTHER | Smaller scope; manually curated; experiment-supported |
| Compare resource consensus | All of them + intersect | Disagreement is itself a signal |
| Plant orthology (Ensembl Plants) | Ensembl Compara (plant division) | Better than Ensembl vertebrate for plants |
| Bacterial orthology | OrthoDB or eggNOG bactNOG | Ensembl Bacteria has limited Compara coverage |
| Custom proteomes not in any database | **De novo computation** | See `comparative-genomics/ortholog-inference` |

## Per-resource API reference

### OrthoDB v12

Base URL: `https://data.orthodb.org/v12/`

Key endpoints (all GET, JSON returned):
- `/search?query=<symbol>&species=<NCBI_taxid>` — find ortholog groups by gene symbol
- `/orthologs?id=<og_id>&species=<taxid>` — get orthologs of a group at a specific level
- `/group?id=<og_id>` — full group info (sequences, evidence)
- `/tab?query=<og_id>` — tab-separated bulk dump

Levels are NCBI taxonomy IDs (e.g. 9606 = human, 40674 = Mammalia, 7742 = Vertebrata).

```python
def orthodb_search(symbol, species_taxid=9606):
    r = requests.get('https://data.orthodb.org/v12/search',
                     params={'query': symbol, 'species': species_taxid})
    r.raise_for_status()
    return r.json()['data']  # list of orthogroup IDs
```

### Ensembl Compara (via Ensembl REST)

Base URL: `https://rest.ensembl.org/`. JSON: `Accept: application/json`. Rate limit: 15 req/sec, 55,000 req/hour. Respect `Retry-After` on 429.

Key endpoints:
- `/homology/symbol/<species>/<symbol>` — orthologs of a gene by symbol
- `/homology/id/<ensembl_gene_id>` — orthologs of a gene by Ensembl ID
- `/lookup/symbol/<species>/<symbol>` — resolve symbol to Ensembl ID first
- Add `?type=orthologues` to filter to orthologs only (drop paralogs)
- Add `?target_species=<species>` to filter to one target species

```python
def ensembl_orthologs(symbol, species='human', target=None):
    url = f'https://rest.ensembl.org/homology/symbol/{species}/{symbol}'
    params = {'type': 'orthologues'}
    if target:
        params['target_species'] = target
    r = requests.get(url, params=params, headers={'Accept': 'application/json'})
    r.raise_for_status()
    homologies = r.json()['data'][0]['homologies']
    return [{
        'target_species': h['target']['species'],
        'target_id': h['target']['id'],
        'type': h['type'],  # ortholog_one2one / one2many / many2many / within_species_paralog
        'confidence': h.get('confidence'),  # 0/1; some calls lack this field
        'identity_target': h['target'].get('perc_id'),
        'identity_query': h['source'].get('perc_id'),
    } for h in homologies]
```

### OMA REST API

Base URL: `https://omabrowser.org/api/`. JSON returned. No rate-limit doc but be polite.

Key endpoints:
- `/protein/<id>/orthologs/` — orthologs of a protein (UniProt or OMA ID)
- `/hog/<hog_id>/` — Hierarchical Orthologous Group info
- `/genome/<species_code>/` — list all genomes; species codes are 5-letter (e.g. HUMAN, MOUSE)

```python
def oma_orthologs(uniprot_acc):
    r = requests.get(f'https://omabrowser.org/api/protein/{uniprot_acc}/orthologs/')
    r.raise_for_status()
    return r.json()  # list of ortholog dicts with omaid, canonicalid, taxonId
```

### eggNOG (5/6)

Base URL: `http://eggnog6.embl.de/api/` (web API; lighter than running eggNOG-mapper). Most heavy lifting still uses **eggNOG-mapper** locally (Cantalapiedra et al. 2021 *Mol Biol Evol* 38:5825) — for batch protein-set annotation, mapper > API.

For ad hoc lookup: search the eggNOG web interface for an orthogroup ID, then download the member set.

### KEGG Orthology (KO)

Base URL: `https://rest.kegg.jp/`. Returns plain text TSV by default (NOT JSON).

```python
def kegg_ko_for_gene(species_code, gene):
    '''KEGG species codes: hsa=human, mmu=mouse, dme=fly, etc.'''
    r = requests.get(f'https://rest.kegg.jp/link/ko/{species_code}:{gene}')
    r.raise_for_status()
    return [line.split('\t')[1].replace('ko:', '') for line in r.text.strip().split('\n') if line]


def kegg_orthologs(ko_id):
    r = requests.get(f'https://rest.kegg.jp/link/genes/{ko_id}')
    return [line.split('\t')[1] for line in r.text.strip().split('\n') if line]
```

KEGG license: commercial use requires a paid license; academic use is free for web/API.

### PANTHER

Base URL: `http://pantherdb.org/services/oai/pantherdb/` (note the unusual base). Has a curated, smaller scope than OrthoDB but with experimental evidence.

### HomoloGene (deprecated)

`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=homologene&id=<id>&rettype=xml` — still works; data frozen since 2014. Useful only for backward-compatibility with old pipelines.

## Confidence-level semantics

Each resource defines "confidence" differently. They are NOT directly comparable.

| Resource | Confidence field | Semantics |
|---|---|---|
| Ensembl Compara | `confidence` 0/1 | Binary; 1 = high confidence based on gene-tree topology |
| OrthoDB | `evolutionary_rate` (not a confidence per se) | Inverse proxy; lower = more conserved |
| OMA | Internal QC; not exposed as a per-call score | All calls passed precision filter |
| eggNOG | Tax-level coverage | Member counts per taxonomic level |
| PANTHER | `evidence` codes | Experimentally validated vs predicted |

**Don't average or compare confidence across resources.** Use within-resource cutoffs; for cross-resource comparison, intersect call sets.

## The orthology conjecture (and why resources disagree)

The orthology conjecture (Tatusov 1997; rigorously evaluated by Studer & Robinson-Rechavi 2009 *Trends Genet* 25:210; Altenhoff et al. 2012 *PLoS Comput Biol* 8:e1002514) — orthologs are more likely than paralogs to share function — is supported but weakly. Sub- and neo-functionalization mean a paralog can become the functional equivalent.

This is also why resources disagree. Different algorithms emphasize different evidence:
- **OMA** is strict (RBH + verification + HOG inference) — higher precision, lower recall.
- **Ensembl Compara** is tree-reconciled — best for vertebrates with deep Compara curation.
- **OrthoDB** uses broader hierarchical clustering — broader coverage, more ambiguous calls.
- **eggNOG** uses pre-computed orthogroups at fixed taxonomic levels — fast but coarser.

For high-stakes calls (publication, drug target choice), **intersect at least two resources** and inspect disagreements.

## Code patterns

### Get the human ortholog of a mouse gene (Ensembl Compara, 1:1 only)

**Goal:** Pull Compara's high-confidence 1:1 ortholog of a single mouse gene in human.

**Approach:** REST query with type filter; assert 1:1; record confidence.

**Reference (Ensembl REST, release 112+):**
```python
import requests
import time


def compara_one2one(symbol, source='mouse', target='human'):
    url = f'https://rest.ensembl.org/homology/symbol/{source}/{symbol}'
    r = requests.get(url, params={'type': 'orthologues', 'target_species': target},
                     headers={'Accept': 'application/json'})
    if r.status_code == 429:
        time.sleep(int(r.headers.get('Retry-After', '5')))
        return compara_one2one(symbol, source, target)
    r.raise_for_status()
    hits = r.json()['data'][0]['homologies']
    one2one = [h for h in hits if h['type'] == 'ortholog_one2one']
    if not one2one:
        return None
    h = one2one[0]
    return {
        'source_id': h['source']['id'],
        'target_id': h['target']['id'],
        'confidence': h.get('confidence'),
        'pid_target': h['target'].get('perc_id'),
    }
```

### Cross-resource agreement (Ensembl + OMA + OrthoDB)

**Goal:** Find orthologs agreed on by multiple resources to flag high-confidence calls.

**Approach:** Query each resource; intersect target IDs after normalizing to a common namespace (UniProt or NCBI Gene).

```python
def cross_resource_orthologs(symbol):
    '''Return target-species ortholog calls from multiple resources for cross-validation.'''
    ensembl = ensembl_orthologs(symbol, species='human')
    # (OMA/OrthoDB lookups omitted for brevity -- need namespace conversion via UniProt ID Mapping)
    return {'ensembl': ensembl}
```

### Batch ortholog table for >100 genes

**Goal:** Build a wide table of orthologs across N species for a gene list.

**Approach:** Loop with rate limit; cache responses; respect `Retry-After`.

**Reference (requests 2.31+):**
```python
def batch_ensembl_orthologs(symbols, source='human', target_species=None, sleep=0.07):
    '''sleep=0.07 keeps under the 15-req/sec ceiling with margin.'''
    rows = []
    for sym in symbols:
        try:
            orthologs = ensembl_orthologs(sym, species=source, target=target_species)
            for o in orthologs:
                rows.append({'source_symbol': sym, **o})
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                wait = int(e.response.headers.get('Retry-After', '10'))
                time.sleep(wait)
            else:
                rows.append({'source_symbol': sym, 'error': str(e)})
        time.sleep(sleep)
    return pd.DataFrame(rows)


df = batch_ensembl_orthologs(['BRCA1', 'TP53', 'MYC'], target_species='mouse')
print(df[df['type'] == 'ortholog_one2one'][['source_symbol', 'target_id', 'confidence']])
```

### Pull all human-mouse 1:1 orthologs as a bulk table

For thousands of genes, prefer Ensembl BioMart bulk export — see `biomart-queries`. The REST API is fine for hundreds; BioMart wins at thousands.

### OMA HOG navigation

```python
def oma_hog_for_protein(oma_or_uniprot_id):
    r = requests.get(f'https://omabrowser.org/api/protein/{oma_or_uniprot_id}/')
    r.raise_for_status()
    return r.json().get('oma_hog_id')


def oma_hog_members(hog_id, level=None):
    url = f'https://omabrowser.org/api/hog/{hog_id}/'
    params = {'level': level} if level else {}
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()
```

### KEGG ortholog lookup

```python
ko_ids = kegg_ko_for_gene('hsa', '7157')  # human TP53
for ko in ko_ids:
    orthologs = kegg_orthologs(ko)
    print(f'{ko}: {len(orthologs)} orthologs across all KEGG species')
```

## Failure modes

### Resource disagreement on 1:1
- **Trigger:** Ensembl Compara says 1:1; OrthoDB says 1:many; OMA says no call.
- **Mechanism:** Different algorithmic emphases; different species coverage.
- **Symptom:** Inconsistent ortholog tables across pipeline stages.
- **Fix:** Define the authoritative resource per project; or take intersection; document the choice.

### Stale resource snapshot
- **Trigger:** Using a 2-year-old OrthoDB download or HomoloGene (frozen 2014).
- **Mechanism:** Species coverage and algorithms have improved; gene model updates.
- **Symptom:** Missing orthologs that the live database has; calling defunct ortholog IDs.
- **Fix:** Pin to a release version with date; refresh annually; for HomoloGene, treat as legacy and verify against a current resource.

### Symbol-based lookup ambiguity
- **Trigger:** `compara_one2one('MARCH1', 'human', 'mouse')` -- but MARCH1 was renamed to MARCHF1 in 2020.
- **Mechanism:** HGNC symbol renames break symbol-based lookups; APIs may return empty or wrong gene.
- **Symptom:** No orthologs found; or orthologs of the wrong gene.
- **Fix:** Resolve symbol to canonical Ensembl/HGNC ID first; use the ID-based endpoint.

### Compara confidence missing
- **Trigger:** Some Compara calls lack `confidence` (older calls; certain species pairs).
- **Mechanism:** Field is not populated for all calls.
- **Symptom:** `KeyError`; or filter drops calls that should pass.
- **Fix:** Use `.get('confidence', None)` and treat missing as unknown (not as low-confidence).

### Rate-limit cascade on bulk queries
- **Trigger:** Loop of 5000 Ensembl REST calls.
- **Mechanism:** 15 req/sec ceiling, 55K/hour; hit gives 429 with Retry-After.
- **Symptom:** Cascading retries; pipeline stalls.
- **Fix:** Sleep 0.07s between calls; check Retry-After on 429; for >5K queries use BioMart bulk export instead.

### Custom proteome not in any DB
- **Trigger:** Querying a newly sequenced species absent from all resources.
- **Mechanism:** All ortholog databases require the species to be in their pre-computed set.
- **Symptom:** No ortholog calls.
- **Fix:** Run de novo (OrthoFinder or SonicParanoid) -- see `comparative-genomics/ortholog-inference`.

### KEGG license confusion
- **Trigger:** Building a commercial product on KEGG REST.
- **Mechanism:** KEGG academic-free, commercial-paid.
- **Symptom:** License violation in a commercial pipeline.
- **Fix:** Confirm license for the use case; eggNOG and OrthoDB have more permissive licenses.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `HTTPError 429` (Ensembl) | Rate limit | Sleep per Retry-After; cap at 15 req/sec |
| Empty homologies | Symbol misspelled or stale | Resolve to Ensembl ID first |
| Missing confidence field | Older calls | `.get()` with default |
| OMA `404` | Wrong namespace (used UniProt where OMA needed OMA ID) | Use the protein lookup endpoint to resolve first |
| KEGG returns HTML | Endpoint wrong (use `rest.kegg.jp`) | Check URL; KEGG is text TSV not JSON |
| Resource disagreement | Different algorithms / coverage | Intersect; document choice |

## References

- Tatusov RL, Koonin EV, Lipman DJ. (1997) A genomic perspective on protein families. *Science* 278:631-637.
- Altenhoff AM, Studer RA, Robinson-Rechavi M, Dessimoz C. (2012) Resolving the ortholog conjecture: orthologs tend to be weakly, but significantly, more similar in function than paralogs. *PLoS Comput Biol* 8:e1002514.
- Studer RA, Robinson-Rechavi M. (2009) How confident can we be that orthologs are similar, but paralogs differ? *Trends Genet* 25:210-216.
- Kuznetsov D, Tegenfeldt F, Manni M, Seppey M, Berkeley M, Kriventseva EV, Zdobnov EM. (2023) OrthoDB v11: annotation of orthologs in the widest sampling of organismal diversity. *Nucleic Acids Res* 51:D445-D451.
- Herrero J, Muffato M, Beal K, et al. (2016) Ensembl comparative genomics resources. *Database* 2016:baw053.
- Altenhoff AM, Vesztrocy AW, Bernard C, et al. (2024) OMA orthology in 2024. *Nucleic Acids Res* 52:D513-D521.
- Hernandez-Plaza A, Szklarczyk D, Botas J, et al. (2023) eggNOG 6.0: enabling comparative genomics across 12,535 organisms. *Nucleic Acids Res* 51:D389-D394.
- Cantalapiedra CP, Hernandez-Plaza A, Letunic I, Bork P, Huerta-Cepas J. (2021) eggNOG-mapper v2: functional annotation, orthology assignments, and domain prediction at the metagenomic scale. *Mol Biol Evol* 38:5825-5829.
- Thomas PD, Ebert D, Muruganujan A, Mushayahama T, Albou LP, Mi H. (2022) PANTHER: making genome-scale phylogenetics accessible to all. *Protein Sci* 31:8-22.

## Related Skills

- comparative-genomics/ortholog-inference - De novo orthology computation (OrthoFinder, OMA standalone, SonicParanoid)
- ensembl-rest - Broader Ensembl REST workflows beyond Compara
- biomart-queries - Bulk ortholog table export via Ensembl BioMart
- uniprot-access - Resolve UniProt accessions used by OMA
- pathway-analysis/kegg-pathways - KEGG Orthology and pathway mapping
<!-- END FILE: database-access/ortholog-inference/SKILL.md -->

## 子目录：database-access/remote-homology

<!-- BEGIN FILE: database-access/remote-homology/SKILL.md -->
---
name: bio-remote-homology
description: Detect distant homologs using profile and structure-aware methods that go beyond standard BLAST. Use when sequence identity falls into the twilight zone (<35% pairwise), when BLAST fails to find homologs that should exist, when working at metagenomic scale (DIAMOND, MMseqs2), or when structure beats sequence (Foldseek). Covers PSI-BLAST (iterative PSSM), jackhmmer (iterative HMM), HHblits/HHsearch (profile-profile), DIAMOND, MMseqs2, and Foldseek (3Di structural alphabet, van Kempen 2024).
tool_type: mixed
primary_tool: HMMER
---

## Version Compatibility

Reference examples tested with: NCBI BLAST+ 2.15+, HMMER 3.4+, MMseqs2 15+, DIAMOND 2.1+, HH-suite3 3.3+, Foldseek 9+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then introspect signatures

If a flag is unrecognized or behavior changes, introspect with `--help` and adapt the example to match the installed version rather than retrying.

# Remote Homology

**"Find homologs my BLAST missed"** -> Standard BLAST detects similarity reliably down to ~35% pairwise identity (the "twilight zone", Rost 1999 *Protein Eng* 12:85). Below that, profile methods (PSSMs, HMMs) and structure-aware methods (Foldseek) recover homologs that pairwise alignment misses.

This skill covers the decision: which method, when, against what database. The competition has shifted substantially since 2015: PSI-BLAST is no longer the de-facto standard; MMseqs2 and DIAMOND have replaced BLAST in most large-scale workflows; Foldseek (van Kempen et al. 2024 *Nat Biotechnol* 42:243) detects homologs no sequence method can reach by searching with a 3Di structural alphabet derived from AlphaFold/ESMFold predictions.

- CLI: `psiblast`, `jackhmmer`, `hmmsearch`, `hhblits`, `mmseqs`, `diamond`, `foldseek`
- Python: `Bio.SearchIO` for output parsing; tool-specific clients exist but subprocess is preferred
- Web: HHpred (HHblits webserver), Foldseek webserver, ColabFold for paired structure search

## Required Setup

```bash
# Install via conda
conda install -c bioconda hmmer mmseqs2 diamond hhsuite foldseek
# BLAST+ (separate)
conda install -c bioconda blast

# Verify
hmmsearch -h | head -3       # HMMER 3.4+
mmseqs version               # MMseqs2 15+
diamond --version            # DIAMOND 2.1+
hhblits -h | head -3         # HH-suite3 3.3+
foldseek --version           # Foldseek 9+
```

## Decision matrix: which method when

| Question | Best tool | Why | Sensitivity / Speed |
|---|---|---|---|
| Quick all-vs-all proteome | MMseqs2 or DIAMOND | 100-10,000x faster than BLAST at comparable sensitivity | Highest throughput, near-BLAST sensitivity |
| Identify distant protein homolog (single query) | jackhmmer | Iterative HMM; usually beats PSI-BLAST | Higher sensitivity than PSI-BLAST |
| Distant homology where structure available | Foldseek | 3Di alphabet finds homologs sequence misses | Finds hits PSI-BLAST/HMMER cannot |
| Profile-profile comparison (PDB70 / Pfam) | HHblits + HHsearch | Profile vs profile is most sensitive when target also has profile | Best sensitivity for very-deep homology |
| Domain assignment | hmmscan against Pfam-A | Curated, calibrated thresholds | Standard practice |
| Metagenomic protein clustering | MMseqs2 `easy-cluster` | Scales to >1B sequences | Production-grade |
| ORF search vs metagenome | DIAMOND `blastx --frameshift` | Frameshift-aware; long reads | Best for noisy long reads |
| Structure-aware homology (no AF2 prediction available) | Foldseek + ProstT5 | Predicts 3Di alphabet from sequence via PLM | Skip the AF2 step |

## Foldseek: the 2024 revolution

Foldseek (van Kempen, Kim, Tumescheit et al. 2024 *Nat Biotechnol* 42:243) searches protein structures by representing each residue's local geometry as a 21-letter "3Di" alphabet, then running BLAST-style alignment in this alphabet. Two consequences:
- **4-5 orders of magnitude faster than DALI** (the previous gold-standard structure aligner).
- **Finds homologs that sequence methods cannot**: when sequence has diverged past detection but structure is preserved, Foldseek recovers the homology. Reported sensitivity vs traditional structure search is comparable; sensitivity vs sequence methods is dramatically higher at low identity.

Two access modes:
1. **Have a structure** (PDB or AlphaFold): `foldseek easy-search query.pdb db_dir result.m8 tmp_dir`
2. **Sequence only, no structure**: use **ProstT5** (Heinzinger et al. 2024) to embed sequence to 3Di alphabet directly, skipping AF2 entirely: `foldseek databases ProstT5 prostt5_db tmp` then `foldseek easy-search seq.fa db result.m8 tmp --prostt5-model prostt5_db`

The major prebuilt Foldseek databases (AlphaFoldDB, PDB100, ESMAtlas) are downloadable via `foldseek databases`.

## PSI-BLAST: still useful, but watch the drift

PSI-BLAST (Altschul et al. 1997 *Nucleic Acids Res* 25:3389) builds a PSSM iteratively: each iteration includes hits below `-inclusion_ethresh` (default 0.005) in the next PSSM. Convergence is when no new hits cross the threshold. **Stopping at convergence is often the wrong call** -- iterations 2-3 are usually optimal; iterations 4+ frequently drift into paralog inclusion, contaminating the PSSM.

| Parameter | Default | Postdoc tuning |
|---|---|---|
| `-num_iterations` | 1 | 3 for most workflows; >3 risks drift |
| `-inclusion_ethresh` | 0.005 | 0.002 if specificity matters (Altschul 1997 recommendation) |
| `-evalue` | 10 | 0.01 for reporting cutoff |
| `-num_threads` | 1 | 8 for large DBs |

PSI-BLAST is also **non-deterministic** in detail: different input order or DB version can produce different PSSMs. For reproducibility, save the PSSM (`-out_pssm pssm.asn`) and re-use with `-in_pssm`.

## HMMER 3 (hmmsearch, jackhmmer)

HMMER 3 (Eddy 2011 *PLoS Comput Biol* 7:e1002195) is profile HMM search. Two main workflows:
- **`hmmsearch profile.hmm seqdb`**: search a database with a known HMM (Pfam, custom).
- **`jackhmmer query.fa seqdb`**: iterative search like PSI-BLAST but with full HMM math. Typically higher sensitivity than PSI-BLAST at the same number of iterations.

For domain assignment, `hmmscan query.fa Pfam-A.hmm` is the canonical pipeline. Pfam HMMs come with calibrated gathering thresholds (`-gathering`) -- use them instead of arbitrary E-value cutoffs.

```bash
# Build domain database once
wget https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz
gunzip Pfam-A.hmm.gz
hmmpress Pfam-A.hmm

# Annotate query against Pfam-A with gathering threshold (calibrated cutoff)
hmmscan --cut_ga --domtblout query.domtbl Pfam-A.hmm query.fa
```

## HHblits / HHsearch (HH-suite3)

HHblits (Remmert et al. 2012 *Nat Methods* 9:173; HH-suite3: Steinegger et al. 2019 *BMC Bioinformatics* 20:473) is profile-profile alignment. The most sensitive method when both query and target have an HMM representation. Standard pipeline:
1. Build query MSA with `hhblits` against UniRef30 (or HHblits' default DB).
2. Convert MSA to query HMM.
3. Search against a profile DB (PDB70 for structure, Pfam-A for domains) with `hhsearch`.

Output is in HHM format. For very deep homology (the structural twilight zone), HHsearch vs PDB70 is still the gold standard.

## MMseqs2 (the modern protein search workhorse)

MMseqs2 (Steinegger & Soding 2017 *Nat Biotechnol* 35:1026) replaces BLAST in nearly all large-scale workflows.

Key advantages:
- **Speed**: 400-10,000x faster than blastp at similar sensitivity.
- **Sensitivity**: At `-s 7.5`, matches HMMER sensitivity (but on raw sequence, not profiles).
- **Iterative profile search**: `mmseqs search --num-iterations 3` matches PSI-BLAST behavior at much higher speed.

```bash
# Build target DB
mmseqs createdb target.fasta targetDB
mmseqs createindex targetDB tmp

# Sensitive search
mmseqs easy-search query.fa targetDB results.m8 tmp -s 7.5 --num-iterations 3

# All-vs-all clustering at 50% sequence identity
mmseqs easy-cluster all_proteins.fa cluster tmp --min-seq-id 0.5 -c 0.8
```

The `-s` parameter trades sensitivity for speed: 1.0 (fast), 4.0 (default), 7.5 (HMMER-like sensitivity).

## DIAMOND (the modern blastp replacement)

DIAMOND (Buchfink et al. 2015 *Nat Methods* 12:59; v2: Buchfink et al. 2021 *Nat Methods* 18:366) is the de-facto replacement for blastp on large-scale workflows.

| Feature | DIAMOND v2 | blastp |
|---|---|---|
| Speed | 100-10,000x faster | baseline |
| Sensitivity (default) | ~95% of blastp | baseline |
| `--ultra-sensitive` | >99% of blastp | baseline |
| Frameshift-aware (long reads) | Yes (`--frameshift 15`) | No |
| GPU support | No (CPU-only) | No |

```bash
# Build DIAMOND DB
diamond makedb --in nr.fa -d nr

# Sensitive search
diamond blastp -d nr -q query.fa -o results.tsv \
        --more-sensitive -e 1e-10 -p 16 \
        --outfmt 6 qseqid sseqid pident length qcovhsp evalue bitscore stitle

# Long-read frameshift-aware (for nanopore/PacBio metagenomics)
diamond blastx -d nr -q longreads.fa --frameshift 15 -o reads.tsv --outfmt 6
```

For protein remote homology in 2026, DIAMOND `--ultra-sensitive` or MMseqs2 `-s 7.5` should be the default before reaching for BLAST.

## Iterative HMMER (jackhmmer)

```bash
# 3 iterations, save checkpoint HMM at each iteration
jackhmmer -N 3 --chkhmm iter.hmm --tblout hits.tbl query.fa uniref90.fa

# After convergence (no new hits below threshold) use the final HMM for downstream searches
hmmsearch iter-3.hmm target.fa > hits.txt
```

## Code patterns

### Foldseek search against AlphaFoldDB

**Goal:** Find structural homologs of a protein structure (or sequence via ProstT5) in AlphaFold's predicted structure database.

**Approach:** Download AlphaFoldDB structure DB (or ProstT5 for sequence-only); search with foldseek `easy-search`; parse m8 tabular output.

**Reference (Foldseek 9+):**
```bash
#!/bin/bash
# Reference: foldseek 9+ | Verify API if version differs

mkdir -p foldseek_dbs tmp
# Download the AlphaFoldDB Swiss-Prot subset (~few GB; full AFDB is much larger)
foldseek databases Alphafold/Swiss-Prot afdb_sp foldseek_dbs/tmp

# Structure-vs-structure search
foldseek easy-search query.pdb foldseek_dbs/afdb_sp results.m8 tmp \
         --format-output query,target,fident,alnlen,evalue,bits,prob,qtmscore,ttmscore

head -5 results.m8
# qtmscore/ttmscore are TM-score equivalents from local Foldseek alignment.
# Hits with prob > 0.9 are confidently structurally homologous.
```

### Sequence-only Foldseek via ProstT5

```bash
foldseek databases ProstT5 prostt5_model tmp
foldseek easy-search query.fa foldseek_dbs/afdb_sp seq_results.m8 tmp \
         --prostt5-model prostt5_model --threads 8
```

This is the path to take when only a protein sequence is available -- ProstT5 (a protein language model) predicts the 3Di alphabet directly from sequence.

### PSI-BLAST with saved PSSM

**Goal:** Build a position-specific scoring matrix iteratively, then re-use it for downstream searches.

**Approach:** 3 iterations against UniRef90 (or nr); save ASN.1 + ASCII PSSM; subsequent searches use `-in_pssm`.

**Reference (NCBI BLAST+ 2.15+):**
```bash
psiblast -query distant_protein.fa -db uniref90 \
         -num_iterations 3 \
         -inclusion_ethresh 0.002 \
         -evalue 0.01 \
         -num_threads 8 \
         -out_pssm distant.pssm.asn \
         -out_ascii_pssm distant.pssm.txt \
         -out psiblast_results.txt

# Reuse saved PSSM in subsequent searches against a different DB
psiblast -in_pssm distant.pssm.asn -db swissprot \
         -out swissprot_via_pssm.txt
```

### MMseqs2 sensitive iterative search

**Goal:** PSI-BLAST-equivalent iterative profile search, but 100x faster.

**Approach:** `mmseqs search --num-iterations 3 -s 7.5`.

**Reference (MMseqs2 15+):**
```bash
mmseqs createdb query.fa queryDB
mmseqs createdb uniref90.fa uniref90DB
mmseqs createindex uniref90DB tmp

mmseqs search queryDB uniref90DB resultDB tmp \
       --num-iterations 3 \
       -s 7.5 \
       -e 1e-5 \
       --threads 16

mmseqs convertalis queryDB uniref90DB resultDB results.m8 \
       --format-output query,target,fident,alnlen,evalue,bits
```

### Pfam domain annotation (canonical)

```bash
# One-time prep
hmmpress Pfam-A.hmm

# Annotate
hmmscan --cut_ga --domtblout query.domtbl --cpu 8 Pfam-A.hmm query.fa

# Filter: gathering threshold passes are already significance-validated
awk '!/^#/ {print $1, $2, $4, $5, $7, $8, $13}' query.domtbl | head
# columns: target_name, accession, query_name, accession, full_evalue, full_score, i_evalue
```

### HHsearch against PDB70 (deepest homology to PDB)

```bash
# Build query MSA via HHblits vs UniRef30
hhblits -i query.fa -d uniref30 -oa3m query.a3m -n 3 -cpu 8

# Search PDB70 with the query profile
hhsearch -i query.a3m -d pdb70 -o query.hhr -cpu 8

head -30 query.hhr   # Top hits with probability + alignment statistics
```

### DIAMOND ultra-sensitive on a metagenome

```bash
diamond makedb --in uniref90.fa -d uniref90
diamond blastp -d uniref90 -q metagenome_proteins.fa -o hits.tsv \
        --ultra-sensitive -e 1e-5 -p 32 \
        --outfmt 6 qseqid sseqid pident length qcovhsp evalue bitscore stitle
```

## Failure modes

### PSI-BLAST profile drift
- **Trigger:** Iterating to convergence (5+ iterations).
- **Mechanism:** Each iteration includes hits below threshold; eventually paralogs and divergent family members contaminate the PSSM.
- **Symptom:** Later iterations return many implausible hits; functional inference goes wrong.
- **Fix:** Cap at 3 iterations; inspect the saved PSSM and the included sequence set; use stricter `-inclusion_ethresh 0.001`.

### Foldseek "structure but no homology" hits
- **Trigger:** Searching small fragments or highly conserved folds (TIM barrels, Rossmann folds).
- **Mechanism:** Structural fold is preserved across deep divergence; superfamily hits exist without true homology.
- **Symptom:** High structural similarity to functionally unrelated proteins.
- **Fix:** Combine Foldseek hits with sequence-based evidence; check shared catalytic residues; consider that fold-level similarity is necessary but not sufficient for homology.

### MMseqs2 default sensitivity
- **Trigger:** `mmseqs easy-search` without `-s`.
- **Mechanism:** Default `-s 4.0` is fast but misses remote homologs.
- **Symptom:** Equivalent to a fast BLAST; misses what HMMER would find.
- **Fix:** Set `-s 7.5` for distant homology; `-s 5.7` is a middle ground.

### DIAMOND default mode lossy
- **Trigger:** `diamond blastp` without `--more-sensitive` or `--ultra-sensitive`.
- **Mechanism:** Default mode trades ~5% sensitivity for speed vs blastp.
- **Symptom:** Hits BLAST would find are missing.
- **Fix:** Use `--more-sensitive` for general work, `--ultra-sensitive` for remote homology.

### Profile method on a low-complexity query
- **Trigger:** Query has signal peptide, coiled-coil, or repeat region.
- **Mechanism:** Profile is dominated by low-complexity columns; false hits to other low-complexity proteins.
- **Symptom:** Many high-scoring hits to unrelated low-complexity proteins.
- **Fix:** Mask the low-complexity region (SEG: `segmasker -infmt fasta -in query.fa`) before building the profile.

### HHblits database version drift
- **Trigger:** Using a UniRef30 database from a different release than the PDB70 search DB.
- **Mechanism:** Profile statistics depend on the DB's amino acid distribution.
- **Symptom:** Hit probabilities are miscalibrated.
- **Fix:** Use UniRef30 and PDB70 from the same MMseqs2 / HH-suite release.

### Foldseek without ProstT5 for sequence-only query
- **Trigger:** No structure available; tried to predict with AF2 first (slow).
- **Mechanism:** ProstT5 predicts 3Di alphabet directly from sequence, skipping AF2.
- **Symptom:** Days-long AF2 prediction step for a query that could be Foldseek'd in seconds.
- **Fix:** Use `foldseek databases ProstT5 ...` and `--prostt5-model`.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| PSI-BLAST returns implausible hits | Profile drift (too many iterations) | Cap at 3 iterations; tighter `-inclusion_ethresh` |
| MMseqs2 hits all unrelated | Default sensitivity too low | `-s 7.5` |
| DIAMOND misses BLAST hits | Default mode lossy | `--more-sensitive` |
| Foldseek hits structurally unrelated proteins | Common fold, no homology | Cross-check with sequence and functional residues |
| HHblits prefilter no hits | Query MSA too sparse | Add `-n 4` iterations; check input |
| jackhmmer ConvergenceError | Loop bug pre-v3.4 | Upgrade HMMER |

## References

- Altschul SF, Madden TL, Schaffer AA, Zhang J, Zhang Z, Miller W, Lipman DJ. (1997) Gapped BLAST and PSI-BLAST: a new generation of protein database search programs. *Nucleic Acids Res* 25:3389-3402.
- Rost B. (1999) Twilight zone of protein sequence alignments. *Protein Eng* 12:85-94.
- Eddy SR. (2011) Accelerated profile HMM searches. *PLoS Comput Biol* 7:e1002195.
- Remmert M, Biegert A, Hauser A, Soding J. (2012) HHblits: lightning-fast iterative protein sequence searching by HMM-HMM alignment. *Nat Methods* 9:173-175.
- Buchfink B, Xie C, Huson DH. (2015) Fast and sensitive protein alignment using DIAMOND. *Nat Methods* 12:59-60.
- Steinegger M, Soding J. (2017) MMseqs2 enables sensitive protein sequence searching for the analysis of massive data sets. *Nat Biotechnol* 35:1026-1028.
- Steinegger M, Meier M, Mirdita M, Vohringer H, Haunsberger SJ, Soding J. (2019) HH-suite3 for fast remote homology detection and deep protein annotation. *BMC Bioinformatics* 20:473.
- Buchfink B, Reuter K, Drost HG. (2021) Sensitive protein alignments at tree-of-life scale using DIAMOND. *Nat Methods* 18:366-368.
- van Kempen M, Kim SS, Tumescheit C, Mirdita M, Lee J, Gilchrist CLM, Soding J, Steinegger M. (2024) Fast and accurate protein structure search with Foldseek. *Nat Biotechnol* 42:243-246.
- Heinzinger M, Weissenow K, Sanchez JG, Henkel A, Mirdita M, Steinegger M, Rost B. (2024) Bilingual language model for protein sequence and structure. *NAR Genom Bioinform* 6:lqae150.

## Related Skills

- blast-searches - Remote BLAST against NCBI; baseline for closer homologs
- local-blast - Local BLAST+ for moderate-scale workflows
- ortholog-inference - Orthology calls (RBH, OrthoFinder, OMA, Compara)
- alignment/multiple-alignment - Build MSAs for HMM profiles
- structural-biology/alphafold-predictions - Predict structures for Foldseek input
- structural-biology/modern-structure-prediction - ESMFold, ColabFold pipelines
<!-- END FILE: database-access/remote-homology/SKILL.md -->

## 子目录：database-access/sra-data

<!-- BEGIN FILE: database-access/sra-data/SKILL.md -->
---
name: bio-sra-data
description: Download raw sequencing reads from NCBI SRA using sra-tools (prefetch, fasterq-dump, vdb-validate) or the ENA mirror. Use when pulling FASTQ for SRR/ERR/DRR accessions, deciding between SRA-direct, ENA mirror, or AWS/GCP cloud mirror (STRIDES), handling --include-technical for 10x and other single-cell records, validating with MD5/vdb-validate, navigating SRR/SRX/SRS/SRP/PRJNA hierarchy, or finding accessions via pysradb. Encodes SRA cloud-egress economics, the fasterq-dump uncompressed-scratch trap, and the --max-size default that silently truncates large prefetches.
tool_type: cli
primary_tool: sra-tools
---

## Version Compatibility

Reference examples tested with: sra-tools 3.0+ (fasterq-dump, prefetch, vdb-validate, vdb-config), pysradb 2.2+, ENA portal API 2.0+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `fasterq-dump --version`, `prefetch --version`
- Python: `pip show pysradb`

If a flag is unrecognized or behavior changes, run `<tool> --help` and adapt.

# SRA Data

**"Download FASTQ from this SRA accession"** -> Two paths exist in 2026: the **SRA toolkit** (NCBI's official, with prefetch + fasterq-dump) and the **ENA mirror** (EMBL-EBI's mirror with direct FASTQ download, often faster). For >1 TB workflows, a third path: **AWS Open Data** (STRIDES program) where same-region EC2 pulls SRA data with zero egress cost.

The single most impactful decision is **where to pull from**. SRA-direct is the default but ENA is faster more often than not, and AWS Open Data is the right answer for cloud-native analysis pipelines.

- CLI: `prefetch SRR...`, `fasterq-dump SRR...`, `vdb-validate SRR...` (sra-tools)
- CLI: `curl https://ftp.sra.ebi.ac.uk/...` (ENA mirror; direct FASTQ)
- CLI: `aws s3 cp s3://sra-pub-run-odp/sra/SRR.../SRR... ./SRR....sra ...` (STRIDES; object is unsuffixed; same-region free)
- Python: `pysradb` for metadata; `subprocess` for download

## Required Setup

```bash
# sra-tools (toolkit)
conda install -c bioconda sra-tools           # 3.0+
fasterq-dump --version                        # confirm

# Configure cache location (default ~/ncbi/ -- often too small)
vdb-config --cfg                              # show current config
vdb-config --set /repository/user/main/public/root=/data/sra_cache

# Optional: pysradb for metadata
pip install pysradb
```

For STRIDES cloud:
```bash
# AWS CLI (no NCBI auth needed for public buckets)
aws s3 ls s3://sra-pub-run-odp/sra/SRR12345678/ --no-sign-request
```

## Decision matrix: where to pull from

| Source | When best | Speed | Cost |
|---|---|---|---|
| **ENA mirror** (FTP/Aspera) | Default for most workflows | Often fastest; direct FASTQ (no SRA->FASTQ conversion needed) | Free; no rate limit observed |
| **SRA toolkit + AWS STRIDES** | Same-region EC2/EKS | Fastest within AWS us-east-1 | Free egress within region; small storage cost |
| **SRA toolkit + GCP STRIDES** | Same-region GCP Compute Engine | Fastest within GCP us-central1 | Free egress within region |
| **SRA-direct (prefetch + fasterq-dump)** | On-prem; small downloads; need SRA-format access | Variable; can be slow off-peak fails | Free; NCBI throttles by IP |
| **Aspera (`ascp`)** | Institutional accounts only | Faster than HTTPS on long links | NCBI public Aspera retired 2019; ENA public Aspera retired ~2023; institutional use still possible |

**Default recommendation**: **ENA mirror** for off-cloud, **STRIDES (AWS/GCP)** for in-cloud analysis. SRA-direct only when neither is available or when SRA format itself is needed (e.g. for re-extraction of technical reads).

## SRA accession hierarchy

| Prefix | Type | Granularity |
|---|---|---|
| SRR / ERR / DRR | Run | One sequencing run (file-level) |
| SRX / ERX / DRX | Experiment | Library prep + sequencing strategy |
| SRS / ERS / DRS | Sample | Biological sample |
| SRP / ERP / DRP | Study | Project (deprecated; superseded by BioProject) |
| PRJNA / PRJEB / PRJDB | BioProject | Top-level project ID |
| SAMN / SAMEA / SAMD | BioSample | Biological sample (cross-archive) |

Conversion is via SRA metadata: `pysradb metadata <ID>` or `efetch -db sra -id <UID> -rettype runinfo`.

The actual download unit is SRR/ERR/DRR (runs). The BioProject (PRJNA...) is the convenient top-level handle for "pull all data for paper X".

## fasterq-dump vs fastq-dump

`fasterq-dump` (sra-tools 2.10+) is the multi-threaded successor. **Always prefer it**, with two exceptions noted below.

| Aspect | fasterq-dump | fastq-dump |
|---|---|---|
| Threads | Multi (`-e N`) | Single |
| Speed | ~5-10x faster | Baseline |
| Disk overhead | Writes uncompressed FASTQ to scratch (~3x final size) | In-place; lower scratch |
| Compression | NOT built-in (post-process with pigz) | `--gzip` flag built-in |
| Single-cell technical reads | `--include-technical` works | Some 10x records need fastq-dump for full extraction |
| 10x split semantics | Sometimes incomplete | Sometimes the only way to get all reads |

The **uncompressed-scratch trap**: `fasterq-dump` writes uncompressed FASTQ first, then leaves it uncompressed. A 100 GB compressed FASTQ needs ~300 GB of scratch space + 300 GB of final output. Either compress post-hoc with `pigz` or use `--mem` to control RAM/disk tradeoff.

## prefetch and the `--max-size` trap

`prefetch` downloads `.sra` files to the configured cache before extraction. Default `--max-size 20G` silently skips runs larger than 20 GB.

```bash
# Wrong: silently skips runs >20 GB
prefetch SRR12345678

# Right: set max-size explicitly to your largest expected size
prefetch SRR12345678 --max-size 100G -p
```

For unknown-size queues, set max-size to a generous upper bound (e.g. `--max-size 200G`) or query metadata first with `pysradb metadata`.

## ENA mirror: direct FASTQ URLs

ENA stores FASTQ files directly (no SRA-format intermediate). Discover URLs via the ENA portal API:

```bash
curl 'https://www.ebi.ac.uk/ena/portal/api/filereport?accession=SRR12345678&result=read_run&fields=fastq_ftp,fastq_md5,read_count&format=tsv'
```

Returns TSV with semicolon-separated paired-end URLs and md5 checksums.

Direct download:
```bash
curl -O 'https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR123/078/SRR12345678/SRR12345678_1.fastq.gz'
```

ENA's mirror is typically faster than SRA's because (a) it's hosted on Aspera-aware servers, (b) the FASTQ is pre-compressed (no SRA->FASTQ conversion needed), (c) EMBL-EBI's bandwidth is generous. For most downloads in 2026, ENA is the right default.

## Single-cell / 10x quirks

10x Genomics records include "technical reads" (cell barcodes, UMIs) interleaved with biological reads. Default `fasterq-dump` (or `fastq-dump`) skips them. To get all reads:

```bash
# fasterq-dump with technical reads
fasterq-dump SRR12345678 --include-technical --split-files -p -O ./fastq/

# Some 10x records require fastq-dump -- check sra-stat first
sra-stat --xml SRR12345678 | grep -E '(spotCount|baseCount|tag)'
```

For 10x v3, expect 3 files per run: R1 (barcode+UMI), R2 (cDNA), I1 (index). For 10x v2: R1 (barcode), R2 (UMI+cDNA), I1.

## MD5 / vdb-validate

Always verify downloads.

```bash
# vdb-validate for SRA-format files (toolkit path)
vdb-validate SRR12345678

# md5sum for ENA FASTQ files
md5sum -c <(echo "<expected_md5>  SRR12345678_1.fastq.gz")
```

ENA provides md5 in the portal API response. SRA-toolkit's `vdb-validate` is the equivalent for `.sra` files (different file format).

## Cloud (STRIDES) access

NCBI's STRIDES initiative mirrored SRA data to AWS Open Data (us-east-1) and GCP (us-central1). Same-region pulls have zero egress cost.

```bash
# List SRA cloud-hosted files (no NCBI auth needed)
aws s3 ls s3://sra-pub-run-odp/sra/SRR12345678/ --no-sign-request

# Direct copy to EC2 in us-east-1. The STRIDES object is named without a `.sra`
# suffix (just SRR12345678); rename on copy to keep fasterq-dump happy.
aws s3 cp s3://sra-pub-run-odp/sra/SRR12345678/SRR12345678 ./SRR12345678.sra --no-sign-request

# Then fasterq-dump locally
fasterq-dump ./SRR12345678.sra -p -e 8
```

For cloud-native analysis pipelines (Nextflow on AWS Batch, Cromwell, etc.), STRIDES is the right path.

## Code patterns

### Single SRR via ENA mirror (preferred default)

**Goal:** Download paired-end FASTQ for one SRR; verify md5; minimal dependencies.

**Approach:** Query ENA portal API for FASTQ URLs and md5; download with curl; verify with md5sum.

**Reference (ENA portal API 2.0+, curl):**
```bash
#!/bin/bash
SRR="${1:-SRR12345678}"
OUT="${2:-./fastq}"
mkdir -p "${OUT}"

# Get FASTQ URLs + md5 from ENA portal API
META=$(curl -s "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=${SRR}&result=read_run&fields=fastq_ftp,fastq_md5&format=tsv" | tail -1)
URLS=$(echo "${META}" | cut -f1 | tr ';' '\n')
MD5S=$(echo "${META}" | cut -f2 | tr ';' '\n')

i=0
while read url; do
    fname="${OUT}/$(basename ${url})"
    expected_md5=$(echo "${MD5S}" | sed -n "$((i+1))p")
    echo "Downloading ${fname}"
    curl -sL -o "${fname}" "https://${url}"
    actual_md5=$(md5sum "${fname}" | awk '{print $1}')
    if [ "${actual_md5}" != "${expected_md5}" ]; then
        echo "MD5 MISMATCH ${fname}: expected ${expected_md5}, got ${actual_md5}"
        exit 1
    fi
    echo "  md5 OK"
    i=$((i+1))
done <<< "${URLS}"
```

### prefetch + fasterq-dump (SRA toolkit, classic)

```bash
#!/bin/bash
SRR="${1:-SRR12345678}"
OUT="${2:-./fastq}"
THREADS="${3:-8}"
mkdir -p "${OUT}"

# prefetch with explicit max-size (default 20G silently skips larger)
prefetch "${SRR}" --max-size 100G -p

# Validate SRA file
vdb-validate "${SRR}" || { echo "Validation FAILED"; exit 1; }

# Extract FASTQ (multi-threaded; uncompressed scratch ~3x final size)
fasterq-dump "${SRR}" -O "${OUT}" -e "${THREADS}" -p --split-files

# Compress post-hoc (fasterq-dump does NOT compress)
pigz -p "${THREADS}" "${OUT}/${SRR}"_*.fastq

# Cleanup SRA cache if you don't need it
# rm -rf ~/ncbi/sra/${SRR}.sra
```

### Batch via pysradb metadata

**Goal:** Convert a list of GSE / BioProject / SRX IDs to SRR run accessions.

**Approach:** pysradb metadata returns a full hierarchy table; pull SRR column.

**Reference (pysradb 2.2+):**
```python
from pysradb import SRAweb
import pandas as pd


def gse_to_srr(gse):
    db = SRAweb()
    df = db.gse_to_srp(gse)
    if df.empty:
        return []
    srp = df['study_accession'].iloc[0]
    runs = db.srp_to_srr(srp)
    return runs['run_accession'].tolist()


def bioproject_to_runs(prjna):
    db = SRAweb()
    return db.sra_metadata(prjna, detailed=True)


def batch_resolve(ids):
    db = SRAweb()
    rows = []
    for id in ids:
        try:
            meta = db.sra_metadata(id, detailed=True)
            rows.append(meta)
        except Exception as e:
            print(f'{id}: {e}')
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


# Resolve a GSE to all its SRRs
srrs = gse_to_srr('GSE123456')
print(f'GSE123456 -> {len(srrs)} SRRs')
```

### Cloud (STRIDES) via AWS

```bash
#!/bin/bash
# Run from EC2 in us-east-1 for zero egress
SRR="${1:-SRR12345678}"

# Check if available on AWS Open Data
aws s3 ls "s3://sra-pub-run-odp/sra/${SRR}/" --no-sign-request

# Download .sra (then extract locally)
aws s3 cp "s3://sra-pub-run-odp/sra/${SRR}/${SRR}" "./${SRR}.sra" --no-sign-request

fasterq-dump "./${SRR}.sra" -p -e 8 --split-files
pigz -p 8 "${SRR}"_*.fastq
```

### 10x single-cell with technical reads

```bash
#!/bin/bash
SRR="${1:-SRR_10x_run}"
OUT="${2:-./fastq_10x}"
mkdir -p "${OUT}"

# Get all reads including technical (barcode/UMI/index)
fasterq-dump "${SRR}" --include-technical --split-files -p -O "${OUT}" -e 8

# 10x v3 expects: R1 (28-bp barcode+UMI), R2 (cDNA), I1 (sample index)
ls -la "${OUT}/${SRR}"_*.fastq
pigz -p 8 "${OUT}/${SRR}"_*.fastq
```

## Failure modes

### prefetch --max-size silent skip
- **Trigger:** Default 20 GB limit; run is 50 GB.
- **Mechanism:** prefetch returns success but downloads nothing.
- **Symptom:** vdb-validate or fasterq-dump fails because no file exists.
- **Fix:** Always set `--max-size` explicitly to a generous upper bound (e.g. 200G).

### fasterq-dump scratch space exhaustion
- **Trigger:** Run is 100 GB compressed; scratch dir has 200 GB free.
- **Mechanism:** fasterq-dump writes ~300 GB uncompressed, fills disk.
- **Symptom:** "out of disk space" mid-extraction.
- **Fix:** Use a scratch dir with 4-5x the compressed size; or use `--mem` to trade memory for disk; or stick with `fastq-dump --gzip` (slower but lower scratch).

### 10x technical reads missing
- **Trigger:** Default `fasterq-dump` on a 10x record.
- **Mechanism:** Technical reads (barcodes, UMIs) are skipped by default.
- **Symptom:** Only the cDNA file (R2) appears; CellRanger / STARsolo errors.
- **Fix:** Add `--include-technical`; verify with `sra-stat --xml` first.

### SRA-direct slowness during US business hours
- **Trigger:** Downloading from NCBI 9 AM-5 PM ET weekdays.
- **Mechanism:** NCBI bandwidth contention; institutional users have priority.
- **Symptom:** kbps-level download speeds.
- **Fix:** Switch to ENA mirror or AWS STRIDES; run outside US business hours.

### Aspera deprecation
- **Trigger:** Old script using `ascp` against `anonftp@ftp.ncbi.nlm.nih.gov`.
- **Mechanism:** NCBI retired public Aspera in 2019; ENA followed ~2023; only institutional accounts retain support.
- **Symptom:** Connection refused or auth fails.
- **Fix:** Switch to HTTPS (slower but works); for fastest cloud transfer use STRIDES (AWS/GCP).

### Cloud egress costs surprise
- **Trigger:** STRIDES pull from EC2 in us-west-2 against bucket in us-east-1.
- **Mechanism:** Cross-region egress is charged.
- **Symptom:** Unexpected AWS bill.
- **Fix:** Match compute region to bucket region (us-east-1 for AWS, us-central1 for GCP).

### vdb-config not persisted across containers
- **Trigger:** Docker container without persisted `~/.ncbi/user-settings.mkfg`.
- **Mechanism:** Cache config is per-user, per-home; container rebuild loses it.
- **Symptom:** Cache fills container's small layer; download fails.
- **Fix:** Mount a host volume at `~/.ncbi/` and persist user-settings.mkfg; or set `--temp` and `-O` explicitly in commands.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| "item not found" | Invalid accession or not in current SRA | Verify; check ENA mirror |
| Scratch disk full mid-extraction | fasterq-dump uncompressed write | Use larger scratch or fastq-dump --gzip |
| Slow SRA-direct download | Business-hours contention | ENA or STRIDES |
| 10x reads missing | --include-technical not set | Add the flag |
| Container loses cache config | vdb-config not persisted | Mount ~/.ncbi as volume |
| prefetch returns "success" but no file | --max-size silent skip | Set --max-size explicitly |
| AWS bill on STRIDES | Cross-region pull | Match compute region |

## References

- NCBI. SRA Toolkit documentation. https://github.com/ncbi/sra-tools/wiki
- NCBI. STRIDES program. https://datascience.nih.gov/strides
- Leinonen R, Sugawara H, Shumway M; International Nucleotide Sequence Database Collaboration. (2011) The sequence read archive. *Nucleic Acids Res* 39:D19-D21.
- Cochrane G, Karsch-Mizrachi I, Takagi T; International Nucleotide Sequence Database Collaboration. (2016) The International Nucleotide Sequence Database Collaboration. *Nucleic Acids Res* 44:D48-D50.
- Choudhary S. (2019) pysradb: A Python package to query next-generation sequencing metadata and data from NCBI Sequence Read Archive. *F1000Research* 8:532.

## Related Skills

- entrez-search - Search the SRA db for accessions before downloading
- geo-data - GEO Series often link to SRA; gds -> sra ELink
- read-qc/quality-reports - QC the downloaded FASTQ
- read-qc/fastp-workflow - Adapter trim downloaded FASTQ
- ncbi-datasets-cli - Modern bulk path for genome data (NOT for SRA reads)
<!-- END FILE: database-access/sra-data/SKILL.md -->

## 子目录：database-access/uniprot-access

<!-- BEGIN FILE: database-access/uniprot-access/SKILL.md -->
---
name: bio-uniprot-access
description: Query UniProt's REST API (post-2022 endpoint at rest.uniprot.org) for protein sequences, annotations, GO terms, cross-references, ID mappings, and proteomes. Use when fetching UniProtKB entries, navigating the JSON schema, choosing between UniProtKB/UniRef/UniParc/Proteomes resources, deciding stream vs search endpoint for batch retrieval, running ID-mapping jobs with the async pattern, handling isoform suffixes, or filtering reviewed Swiss-Prot vs auto-annotated TrEMBL. Encodes the legacy URL migration (2022), the new JSON schema layout, and bulk-pull patterns.
tool_type: python
primary_tool: requests
---

## Version Compatibility

Reference examples tested with: requests 2.31+, pandas 2.2+; UniProt REST API as of 2024_06 release

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show requests pandas`
- API surface: confirm endpoint URLs match https://www.uniprot.org/help/api

The REST API JSON schema is stable within a release; major schema changes are documented at https://www.uniprot.org/release-notes. The 2022 migration broke the legacy `https://www.uniprot.org/uniprot/...` endpoints.

# UniProt Access

**"Get protein information from UniProt"** -> Two facts dominate every UniProt workflow in 2026: (1) **the API endpoint migrated in 2022** from `https://www.uniprot.org/uniprot/...` to `https://rest.uniprot.org/uniprotkb/...` with a substantially different JSON schema; pre-2022 code does not work as-is. (2) **`?fields=`** is essential — default JSON returns the full entry (~20-30 KB each); for bulk pulls, request only the fields actually needed.

The major databases under the UniProt umbrella have different scopes:

- **UniProtKB**: the curated knowledgebase — Swiss-Prot (manually reviewed, ~570K entries as of 2024) + TrEMBL (auto-annotated, ~250M). Always specify `reviewed:true` for high-quality reference work.
- **UniRef**: clustered sequences at 100%, 90%, 50% identity. UniRef50 is the standard for redundancy reduction.
- **UniParc**: archival "every unique sequence ever seen" — for provenance and historical lookup.
- **Proteomes**: organism-level groupings; reference proteomes (one per species) are the canonical subset.

- Python: `requests.get('https://rest.uniprot.org/uniprotkb/...')` (REST API)
- Python: `Bio.ExPASy.get_sprot_raw()` (BioPython; legacy SwissProt format)
- CLI: `curl https://rest.uniprot.org/uniprotkb/P04637.json`

## Required Setup

```python
import requests
import pandas as pd
import time
```

No API key required. Rate limit is generous (~200 req/sec tolerated empirically); ID-mapping has its own job queue.

## Endpoint reference

Base: `https://rest.uniprot.org/`

| Resource | Endpoint | Use |
|---|---|---|
| Single entry | `/uniprotkb/{accession}` | One protein record |
| Search | `/uniprotkb/search` | Query with up to 500 results per page |
| Stream | `/uniprotkb/stream` | No 500-result limit; for bulk |
| Batch by accession | `/uniprotkb/accessions` | Multiple specific accessions |
| ID Mapping (run) | `/idmapping/run` | Submit conversion job |
| ID Mapping (status) | `/idmapping/status/{jobId}` | Poll |
| ID Mapping (results) | `/idmapping/results/{jobId}` | Retrieve |
| UniRef entry | `/uniref/{cluster_id}` | One cluster |
| UniRef search | `/uniref/search` | UniRef cluster queries |
| Proteome | `/proteomes/{upid}` | Organism proteome |
| Proteome FASTA | `/proteomes/{upid}.fasta.gz` | Download whole proteome |
| Taxonomy | `/taxonomy/{taxid}` | Taxonomy info |

Append `.json`, `.fasta`, `.tsv`, `.xml`, `.txt`, or `.gff` to single-entry URLs to control format.

## Search query syntax

UniProt search queries use a Lucene-like syntax distinct from Entrez:

| Query | Means |
|---|---|
| `gene:TP53` | Gene name TP53 |
| `gene_exact:TP53` | Exact gene name (no wildcard match) |
| `organism_id:9606` | Human (NCBI taxonomy ID) |
| `organism_name:"Homo sapiens"` | By name (slower than taxid) |
| `reviewed:true` | Swiss-Prot only |
| `reviewed:false` | TrEMBL only |
| `length:[100 TO 500]` | Sequence length range |
| `go:0006915` | GO term (apoptosis) |
| `keyword:KW-0067` | UniProt keyword |
| `ec:2.7.1.1` | Enzyme classification |
| `database:pdb` | Has PDB cross-ref |
| `xref:pdb` | Same as above |
| `existence:1` | Evidence at protein level (1 = strongest) |

Combine: `organism_id:9606 AND reviewed:true AND keyword:KW-0067 AND xref:pdb`.

## `?fields=` for bulk pulls

Default JSON entry is ~20-30 KB. For batch work, restrict fields:

```python
fields = 'accession,id,gene_names,protein_name,length,sequence,xref_pdb,xref_alphafolddb'
url = 'https://rest.uniprot.org/uniprotkb/search'
params = {'query': 'organism_id:9606 AND reviewed:true', 'fields': fields, 'format': 'tsv', 'size': 500}
```

Common field selectors:
| Field | Returns |
|---|---|
| `accession`, `id` | Primary accession (P04637), entry name (P53_HUMAN) |
| `gene_names` | All gene names |
| `gene_primary` | Primary gene name only |
| `protein_name` | Recommended name |
| `organism_name`, `organism_id` | Species |
| `length`, `mass` | Sequence stats |
| `sequence` | The actual sequence |
| `cc_function`, `cc_subcellular_location` | Function and localization comments |
| `ft_domain`, `ft_binding`, `ft_active_site` | Domain/site features |
| `go_p`, `go_c`, `go_f` | GO biological process / cellular component / molecular function |
| `xref_pdb`, `xref_alphafolddb`, `xref_ensembl`, `xref_refseq` | Cross-references |
| `keyword` | UniProt keywords |
| `ec` | Enzyme classification |
| `reviewed` | Swiss-Prot vs TrEMBL flag |
| `cc_alternative_products` | Isoforms |

## Stream vs search vs accessions

| Endpoint | When | Limit |
|---|---|---|
| `/uniprotkb/{acc}` | One accession | 1 entry |
| `/uniprotkb/accessions?accessions=...` | Several known accessions | Up to ~100 per call |
| `/uniprotkb/search?query=...` | Query-driven; need pagination | 500 results per page; `cursor=` for paging |
| `/uniprotkb/stream?query=...` | Bulk query (>500) | No hard limit; one HTTP stream |

For 1000+ results, `/stream` is the right endpoint. Stream returns one HTTP response; iterate over the stream to avoid memory blowup.

## JSON schema navigation (the post-2022 layout)

The new schema is deeply nested. Common access patterns:

```python
entry = requests.get('https://rest.uniprot.org/uniprotkb/P04637.json').json()

acc = entry['primaryAccession']                                                # 'P04637'
entry_name = entry['uniProtkbId']                                              # 'P53_HUMAN'
sequence = entry['sequence']['value']                                          # actual AA sequence
length = entry['sequence']['length']

# Names (nested; defensive .get() because some fields are optional)
recommended = entry.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value')
primary_gene = entry.get('genes', [{}])[0].get('geneName', {}).get('value')

# Cross-references
xrefs_by_db = {}
for xref in entry.get('uniProtKBCrossReferences', []):
    xrefs_by_db.setdefault(xref['database'], []).append(xref['id'])

# Features (domains, binding sites)
domains = [f for f in entry.get('features', []) if f['type'] == 'Domain']
binding = [f for f in entry.get('features', []) if f['type'] == 'Binding site']

# Isoforms
isoforms = []
for comment in entry.get('comments', []):
    if comment.get('commentType') == 'ALTERNATIVE PRODUCTS':
        isoforms = [iso['name']['value'] for iso in comment.get('isoforms', [])]
```

## Isoform handling

Canonical sequence is returned for the bare accession (e.g. `P04637`). Isoforms have `-2`, `-3`, etc. suffixes (`P04637-2`). To fetch a specific isoform:

```python
iso = requests.get('https://rest.uniprot.org/uniprotkb/P04637-2.fasta').text
```

The canonical entry's `comments[type=ALTERNATIVE PRODUCTS]` lists all isoforms with their differences. For workflows needing all isoforms, iterate the list and fetch separately.

## ID Mapping API (async)

Convert between identifier systems (Ensembl Gene -> UniProt; PDB -> UniProt; UniProt -> RefSeq; etc.). The job pattern:

1. **Submit**: `POST /idmapping/run` with `ids`, `from`, `to`.
2. **Poll**: `GET /idmapping/status/{jobId}` — returns `{'jobStatus': 'RUNNING'}` or `{'results': [...]}`.
3. **Fetch**: `GET /idmapping/results/{jobId}` once status is complete.

Job typically completes in 30s; larger batches take 5-10 min. **Always set a poll timeout** — the API doesn't fail-soft on stuck jobs.

| From | To | Notes |
|---|---|---|
| `UniProtKB_AC-ID` | `UniProtKB` | Resolve obsolete to current accessions |
| `Gene_Name` | `UniProtKB` | Symbol -> accession (lossy; check matches) |
| `Ensembl` | `UniProtKB` | Ensembl Gene/Transcript/Protein |
| `EMBL-GenBank-DDBJ` | `UniProtKB` | INSDC nucleotide accessions |
| `RefSeq_Protein` | `UniProtKB` | NP_/XP_ accessions |
| `PDB` | `UniProtKB` | PDB chain to protein |
| `UniProtKB` | `EMBL-GenBank-DDBJ` | Reverse direction |

Full from/to list at https://rest.uniprot.org/configure/idmapping/fields.

## Code patterns

### Single entry with defensive JSON parsing

**Goal:** Fetch one UniProt entry as JSON and extract canonical name, gene, sequence, PDB cross-refs without KeyErrors.

**Approach:** GET `/uniprotkb/{acc}.json`; navigate with `.get()` chains; handle missing fields gracefully.

**Reference (UniProt REST as of 2024_06):**
```python
import requests


def fetch_uniprot_entry(accession):
    r = requests.get(f'https://rest.uniprot.org/uniprotkb/{accession}.json')
    r.raise_for_status()
    e = r.json()
    return {
        'accession': e['primaryAccession'],
        'entry_name': e.get('uniProtkbId'),
        'reviewed': e.get('entryType') == 'UniProtKB reviewed (Swiss-Prot)',
        'protein_name': e.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value'),
        'gene_primary': (e.get('genes') or [{}])[0].get('geneName', {}).get('value'),
        'sequence': e['sequence']['value'],
        'length': e['sequence']['length'],
        'pdb_ids': [x['id'] for x in e.get('uniProtKBCrossReferences', []) if x['database'] == 'PDB'],
        'alphafold_id': next((x['id'] for x in e.get('uniProtKBCrossReferences', []) if x['database'] == 'AlphaFoldDB'), None),
    }


print(fetch_uniprot_entry('P04637'))
```

### Search via TSV with `fields=` (bulk-friendly)

**Goal:** Get a DataFrame of human reviewed kinases with their PDB and AlphaFold IDs.

**Approach:** /search with format=tsv and explicit fields; paginate via `cursor` if results exceed 500.

**Reference (requests 2.31+):**
```python
import pandas as pd
from io import StringIO


def search_uniprot_tsv(query, fields, size=500):
    url = 'https://rest.uniprot.org/uniprotkb/search'
    params = {'query': query, 'fields': ','.join(fields), 'format': 'tsv', 'size': size}
    r = requests.get(url, params=params)
    r.raise_for_status()
    return pd.read_csv(StringIO(r.text), sep='\t')


df = search_uniprot_tsv(
    'organism_id:9606 AND reviewed:true AND keyword:"Kinase"',
    fields=['accession', 'gene_primary', 'protein_name', 'length', 'xref_pdb', 'xref_alphafolddb'],
)
print(f'{len(df)} reviewed human kinases')
print(df.head())
```

### Stream endpoint for >500 results

```python
import requests
import pandas as pd
from io import StringIO


def stream_uniprot(query, fields):
    url = 'https://rest.uniprot.org/uniprotkb/stream'
    params = {'query': query, 'fields': ','.join(fields), 'format': 'tsv'}
    r = requests.get(url, params=params, stream=True)
    r.raise_for_status()
    return pd.read_csv(StringIO(r.text), sep='\t')


# All human reviewed proteins (~20K)
df = stream_uniprot(
    'organism_id:9606 AND reviewed:true',
    fields=['accession', 'gene_primary', 'protein_name', 'length'],
)
print(f'All human Swiss-Prot: {len(df)}')
```

### ID mapping with proper async polling

**Goal:** Convert Ensembl Gene IDs to UniProt accessions.

**Approach:** Submit job; poll with timeout; retrieve results.

**Reference (UniProt REST 2024_06):**
```python
import time


def map_ids(ids, from_db='Ensembl', to_db='UniProtKB', timeout=600, poll_interval=3):
    submit = requests.post('https://rest.uniprot.org/idmapping/run',
                           data={'ids': ','.join(ids), 'from': from_db, 'to': to_db})
    submit.raise_for_status()
    job_id = submit.json()['jobId']
    print(f'Submitted job {job_id}')

    elapsed = 0
    while elapsed < timeout:
        status = requests.get(f'https://rest.uniprot.org/idmapping/status/{job_id}')
        status.raise_for_status()
        js = status.json()
        if 'jobStatus' in js and js['jobStatus'] == 'RUNNING':
            time.sleep(poll_interval)
            elapsed += poll_interval
            continue
        # Completed (results in status response) or has results endpoint
        break
    else:
        raise TimeoutError(f'ID mapping job {job_id} did not complete in {timeout}s')

    results = requests.get(f'https://rest.uniprot.org/idmapping/results/{job_id}')
    results.raise_for_status()
    return results.json()


mapping = map_ids(['ENSG00000141510', 'ENSG00000171862', 'ENSG00000139618'])
for r in mapping.get('results', []):
    print(f"  {r['from']:<20} -> {r['to']}")
for failed in mapping.get('failedIds', []):
    print(f"  {failed:<20} -> NOT MAPPED")
```

### Resolve obsolete accessions

```python
def resolve_obsolete(accessions):
    '''Use ID mapping to update obsolete accessions to current primary IDs.'''
    return map_ids(accessions, from_db='UniProtKB_AC-ID', to_db='UniProtKB')
```

### Download a reference proteome

```python
import gzip


def download_proteome(upid, out_path):
    '''upid: UniProt Proteome ID, e.g. UP000005640 (human reference).'''
    url = f'https://rest.uniprot.org/proteomes/{upid}.fasta.gz'
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(out_path, 'wb') as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    return out_path


download_proteome('UP000005640', 'human.fasta.gz')  # human reference proteome
```

### UniRef cluster lookup

```python
def uniref_cluster(uniref_id):
    '''e.g. UniRef50_P04637 -- the UniRef50 cluster centered on P04637.'''
    r = requests.get(f'https://rest.uniprot.org/uniref/{uniref_id}.json')
    r.raise_for_status()
    j = r.json()
    return {
        'id': j['id'],
        'representative': j['representativeMember']['memberId'],
        'member_count': j['memberCount'],
        'identity': j.get('entryType'),
    }
```

## Failure modes

### Legacy URL still in code (post-2022)
- **Trigger:** Old code using `https://www.uniprot.org/uniprot/{acc}.json`.
- **Mechanism:** 2022 migration; old URLs redirect but JSON schema is the new one — old parsers break.
- **Symptom:** Either 404 or `KeyError` from old field paths.
- **Fix:** Use `https://rest.uniprot.org/uniprotkb/{acc}.json`; update field navigation to the new nested layout.

### `?fields=` not specified
- **Trigger:** Bulk pull (1000 accessions) returning full JSON entries.
- **Mechanism:** Default returns ~20-30 KB per entry; 1000 entries = 20-30 MB.
- **Symptom:** Slow; memory blowup; rate-limit triggers.
- **Fix:** Always specify `fields=` for bulk; request only the fields actually needed.

### Search hit 500-record cap
- **Trigger:** Query matches 800 records; iterate first page only.
- **Mechanism:** /search returns 500 per page; need `cursor` for next.
- **Symptom:** Silently dropped tail.
- **Fix:** Use `/stream` for >500 results; or paginate /search with `cursor`.

### ID mapping job poll infinite loop
- **Trigger:** Network glitch during job; status forever "RUNNING".
- **Mechanism:** API doesn't time-out stuck jobs.
- **Symptom:** Pipeline hangs.
- **Fix:** Always set `timeout=` on polling; surface TimeoutError.

### Isoform suffix mishandled
- **Trigger:** Storing `P04637` and assuming that's the only sequence.
- **Mechanism:** TP53 has multiple isoforms; default fetch returns canonical only.
- **Symptom:** Missing alternative-product sequences.
- **Fix:** Read `comments[type=ALTERNATIVE PRODUCTS]`; fetch each isoform with `-N` suffix.

### Swiss-Prot vs TrEMBL confusion
- **Trigger:** Search without `reviewed:true` returning millions of TrEMBL hits.
- **Mechanism:** TrEMBL is automatically annotated, often low-quality.
- **Symptom:** "Why does my analysis include 200M proteins?"
- **Fix:** For reference-quality work, always filter `reviewed:true`.

### Obsolete accessions silently fail
- **Trigger:** Old paper-derived accession that has been merged or demerged.
- **Mechanism:** Direct fetch returns 404 or 301.
- **Symptom:** Missing entries in a batch.
- **Fix:** Use ID mapping (UniProtKB_AC-ID -> UniProtKB) to resolve to current accessions first.

### Gene-symbol disambiguation
- **Trigger:** Search `gene:TP53` returns multiple species or duplicates.
- **Mechanism:** Symbol is shared across species; UniProt indexes all.
- **Symptom:** Mixed-species hits.
- **Fix:** Combine with `organism_id:9606` (or specific taxon); use `gene_exact:` to avoid wildcard matches.

## Common errors

| Error / symptom | Cause | Solution |
|---|---|---|
| 404 on legacy URL | Pre-2022 endpoint | Use rest.uniprot.org/uniprotkb/ |
| `KeyError` on old field path | Schema migration 2022 | Update to new nested layout; use `.get()` |
| Bulk fetch very slow | Default JSON entry size | Specify `fields=` for TSV bulk |
| Mid-pagination data missing | 500-record cap | Use /stream or paginate with cursor |
| ID mapping job hangs | API doesn't fail stuck jobs | Set `timeout=` on poll loop |
| Mixed-species search results | Symbol shared across species | Add `organism_id:` filter |
| Million-row search returning TrEMBL | No reviewed filter | Add `reviewed:true` |
| Missing isoform | Default returns canonical only | Fetch with `-N` suffix per isoform |

## References

- The UniProt Consortium. (2024) UniProt: the Universal Protein Knowledgebase in 2025. *Nucleic Acids Res* 53:D609-D617.
- Bursteinas B, Britto R, Bely B, et al. (2016) Minimizing proteome redundancy in the UniProt Knowledgebase. *Database* 2016:baw139.
- UniProt help: https://www.uniprot.org/help/api
- UniProt REST: https://rest.uniprot.org

## Related Skills

- entrez-fetch - NCBI protein records (RefSeq, GenPept) alternative
- biomart-queries - Alternative ID-mapping path via BioMart (preferred for Ensembl-rooted batches >5K; UniProt /idmapping/run is preferred for obsolete-accession resolution and any UniProt-rooted mapping)
- ortholog-inference - Resolve UniProt accessions used by OMA orthology queries
- structural-biology/structure-io - Download PDB structures referenced from UniProt
- structural-biology/alphafold-predictions - AlphaFoldDB entries cross-referenced in UniProt
- pathway-analysis/go-enrichment - Use GO annotations pulled from UniProt
<!-- END FILE: database-access/uniprot-access/SKILL.md -->

<!-- END CATEGORY: database-access -->

