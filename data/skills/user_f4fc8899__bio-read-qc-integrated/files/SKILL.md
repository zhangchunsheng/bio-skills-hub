---
slug: bio-read-qc-integrated
version: 1.0.0
displayName: "读取质量控制 / Sequencing data QC"
name: bio-read-qc-integrated
summary: >-
  中文：读取质量控制综合技能，整合 7 个相关专题，覆盖测序数据质量控制：FastQC/MultiQC报告、adapter修剪、质量过滤、UMI处理、污染筛查。 English: Integrated Sequencing data QC skill covering 7 related topics, including Sequencing data QC: FastQC/MultiQC reports, adapter trimming, quality filtering, UMI processing, contamination screening.
description: >-
  中文：这是一个面向读取质量控制的综合生物信息学 Skill，整合当前分类下 7 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：测序数据质量控制：FastQC/MultiQC报告、adapter修剪、质量过滤、UMI处理、污染筛查。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：RSeQC, cutadapt, fastp。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Sequencing data QC, combining 7 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Sequencing data QC: FastQC/MultiQC reports, adapter trimming, quality filtering, UMI processing, contamination screening. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: RSeQC, cutadapt, fastp. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# read-qc 分类 Skill 整合版

> 本文件整合同一主分类目录下 7 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: read-qc -->

## 子目录：read-qc/adapter-trimming

<!-- BEGIN FILE: read-qc/adapter-trimming/SKILL.md -->
---
name: bio-read-qc-adapter-trimming
description: Removes sequencing adapters from FASTQ reads with Cutadapt and Trimmomatic, including paired-end read-through, small-RNA 3' adapters, amplicon primers, and anchored/linked adapters. Use when FastQC shows adapter content climbing toward the 3' end, when inserts are shorter than the read length (small-RNA, cfDNA, FFPE), or before assembly/k-mer analysis. For all-in-one trimming use fastp-workflow; for quality/length filtering use quality-filtering.
tool_type: cli
primary_tool: cutadapt
---

## Version Compatibility

Reference examples tested with: Cutadapt 4.4+, Trimmomatic 0.39+, fastp 0.23+, FastQC 0.12+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Adapter Trimming -- adapter content IS the insert-size distribution

Remove adapter sequence that the polymerase read INTO once it ran off the end of a short insert, using Cutadapt (precise, the correctness reference) or Trimmomatic (palindrome mode for paired read-through).

**"Trim adapters from my reads"** -> Detect and remove 3' adapter introduced by read-through, then length-filter the survivors.
- CLI: `cutadapt -a AGATCGGAAGAGC -A AGATCGGAAGAGC -m 20 -o R1.fq -p R2.fq in_R1.fq in_R2.fq`
- All-in-one alternative: `fastp` (PE overlap analysis needs no adapter sequence) -> read-qc/fastp-workflow

Scope: this skill OWNS adapter/primer removal. Quality and length filtering -> read-qc/quality-filtering. Single-pass trim+QC -> read-qc/fastp-workflow. Contaminant/PhiX k-mer removal -> read-qc/contamination-screening. OUT OF SCOPE: quality-score trimming as a standalone goal (usually unnecessary before soft-clipping aligners; see insight 2).

## The Single Most Important Modern Insight

1. **Adapter appears only when the insert is shorter than the read, so adapter content is a direct readout of the insert-size distribution -- and adapter trimming is 3'-only for standard Illumina.** The library is `[P5]-[insert]-[P7]`; a read primes at the insert boundary and reads 5'->3' into the insert, running into the 3'/P7-side adapter only if it runs out of insert. Short-insert libraries (small-RNA ~22 nt, cfDNA ~167 bp, FFPE, degraded RNA, ancient DNA) are read-through-dominated; long-insert WGS may show almost none. The FastQC adapter-content curve climbing toward the 3' end IS that insert-size signal.

2. **Adapter trimming is the one near-universal preprocessing step; quality trimming usually is not.** Local aligners (BWA-MEM, STAR, Bowtie2 local, HISAT2) SOFT-CLIP low-quality tails, so quality trimming is redundant or harmful for alignment-based DNA/RNA (MacManes 2014, Williams 2016; GATK discourages it before BQSR). But aligners do NOT reliably remove ADAPTER -- adapter is foreign sequence with genuine base quality, so the aligner may try to align it and anchor a wrong placement. Trim adapter; leave quality trimming to the cases that need it (assembly, k-mer/pseudo-alignment, small-RNA, amplicon, no-BQSR variant calling).

3. **Small-RNA inverts the logic: the adapter is on EVERY read, so DISCARD reads with no adapter.** A ~22 nt miRNA insert is far shorter than a 50-75 nt read, so read-through is universal; a read with no detectable adapter is an adapter dimer, a too-long contaminant, or junk. Use `--discard-untrimmed` plus a tight length gate (`-m 18 -M 30`). This is the OPPOSITE of genomic DNA, where the no-adapter reads are the good full-length inserts.

Two-color trap: on NextSeq/NovaSeq, a high-quality poly-G tail is NOT adapter and is not removed by adapter trimming -- it needs a chemistry-aware poly-G trim (`cutadapt --nextseq-trim=20`, or fastp's auto poly-G). See read-qc/quality-reports and read-qc/fastp-workflow.

## Verified Adapter Sequences

| Kit | Read | Sequence |
|-----|------|----------|
| Illumina TruSeq | R1 3' | AGATCGGAAGAGCACACGTCTGAACTCCAGTCA |
| Illumina TruSeq | R2 3' | AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT |
| TruSeq (shared stem -- catches both) | -- | AGATCGGAAGAGC |
| Nextera / Tn5 | transposase | CTGTCTCTTATACACATCT |
| TruSeq small-RNA | 3' | TGGAATTCTCGGGTGCCAAGG |

The R1 3' adapter is the reverse complement of the R2-side region; trimming the shared 13 bp stem `AGATCGGAAGAGC` on both mates catches TruSeq read-through.

## Tool Taxonomy

| Tool | Mechanism | When it wins |
|------|-----------|--------------|
| Cutadapt | Error-tolerant semiglobal alignment of a supplied adapter | PRECISION: small-RNA 3' adapter, amplicon/16S primers, anchored/linked adapters, demultiplexing. The correctness reference. |
| Trimmomatic | ILLUMINACLIP simple + palindrome modes; ordered step pipeline | Legacy/reproducibility pipelines; palindrome PE read-through detection |
| fastp | PE overlap analysis (no adapter sequence needed) + auto poly-G | DEFAULT general-purpose trim; one fast pass (route OUT -> fastp-workflow) |
| Trim Galore | Cutadapt + FastQC wrapper with adapter auto-detect | Bisulfite/RRBS (`--rrbs`), Bismark pipelines |
| BBDuk | k-mer match against an adapter/contaminant reference | Contaminant/PhiX removal in the same pass (route OUT -> contamination-screening) |

## Decision Tree by Scenario

| Scenario | Use | Why |
|----------|-----|-----|
| General Illumina PE WGS/WES/RNA | fastp, or cutadapt with the TruSeq stem | Overlap analysis needs no sequence; cutadapt for explicit control |
| Small-RNA / miRNA | cutadapt `-a TGGAATTCTCGGGTGCCAAGG -m 18 -M 30 --discard-untrimmed` | Adapter on every read; gate length and drop no-adapter reads |
| Amplicon / 16S primers | cutadapt linked/anchored adapters | Primers are at fixed positions; needs precise placement |
| PE read-through, no adapter sequence known | fastp overlap, or Trimmomatic palindrome | Both detect read-through from the R1/R2 overlap |
| Bisulfite / RRBS | Trim Galore `--rrbs` | Handles MspI fill-in and Bismark conventions |
| NextSeq/NovaSeq with poly-G tails | fastp (auto) or cutadapt `--nextseq-trim` | Poly-G is high-Q; quality trim alone misses it |

Default when uncertain: fastp for bulk PE, cutadapt with the TruSeq stem for explicit single-tool control.

## Cutadapt

The algorithm is semiglobal (overlap) alignment, so a partial 3' adapter at the read end is detected. Two defaults drive behavior: `-e` (error rate, default 0.1) is computed against the LENGTH OF THE MATCHED REGION, not the whole adapter (an 8 bp match with 1 error is rate 0.125 and is rejected at the default); `-O` (minimum overlap, default 3) costs only ~0.07 bases lost per read by chance.

```bash
# Single-end 3' adapter
cutadapt -a AGATCGGAAGAGC -m 20 -o trimmed.fq.gz in.fq.gz

# Paired-end TruSeq (shared stem on both mates); both reads of a pair are discarded together
cutadapt -a AGATCGGAAGAGC -A AGATCGGAAGAGC -m 20:20 \
         -o R1.fq.gz -p R2.fq.gz in_R1.fq.gz in_R2.fq.gz

# Small-RNA: adapter on every read -> discard untrimmed, gate length
cutadapt -a TGGAATTCTCGGGTGCCAAGG -m 18 -M 30 --discard-untrimmed -j 8 \
         -o mirna.fq.gz raw.fq.gz

# Amplicon: linked 5'...3' primers (anchor with ^ to require the 5' primer)
cutadapt -g ^FWDPRIMER...REVPRIMER -o trimmed.fq.gz in.fq.gz

# 2-color poly-G aware (treats G as low quality so high-Q poly-G is trimmed)
cutadapt --nextseq-trim=20 -a AGATCGGAAGAGC -m 20 -o out.fq.gz in.fq.gz

# Higher error tolerance / longer required overlap when matches are missed / spurious
cutadapt -a ADAPTER -e 0.15 -O 5 -m 20 -o out.fq.gz in.fq.gz
```

Key flags: `-a/-g/-b` (3'/5'/anywhere, R1), `-A/-G/-B` (R2), `-q` (quality trim, BWA running-sum, runs BEFORE adapter removal), `--pair-filter {any,both,first}` (default any), `--max-n`, `--action {trim,mask,lowercase,none}`. When a filtering option discards reads in PE mode, both files MUST be processed together or they fall out of sync.

## Trimmomatic

`ILLUMINACLIP:<adapters.fa>:<seedMismatches>:<palindromeClip>:<simpleClip>:<minAdapterLen>:<keepBothReads>`

- seedMismatches: mismatches tolerated in the initial seed (commonly 2).
- palindromeClip (~30): log-odds threshold for the PE palindrome alignment; ~30 needs ~50 matched bases.
- simpleClip (~10): log-odds threshold for an adapter-vs-read match; ~10 needs ~16 bases.
- keepBothReads: DEFAULT False -- after palindrome detects read-through, R2 is redundant (reverse complement of R1) and is DROPPED; set True if a downstream tool needs both mates.

SIMPLE mode tests each adapter against each read. PALINDROME mode (PE-only) aligns R1+adapter against the reverse complement of R2+adapter, so it detects read-through even when only a few adapter bases remain or the adapter is entirely past the read end. Steps run in COMMAND-LINE ORDER; put ILLUMINACLIP first and MINLEN last so the length check reflects all prior trimming.

```bash
# Paired-end, palindrome-capable adapter file, MINLEN last
trimmomatic PE -phred33 -threads 8 \
    in_R1.fq.gz in_R2.fq.gz \
    R1_paired.fq.gz R1_unpaired.fq.gz R2_paired.fq.gz R2_unpaired.fq.gz \
    ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads MINLEN:36

# Built-in adapter files ship with the install
ls $CONDA_PREFIX/share/trimmomatic-*/adapters/
```

PE mode emits FOUR files: paired (both mates survived) and unpaired/orphan (mate dropped). Feed the paired files to the aligner; the orphans stay synchronized out of the way.

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| FastQC still shows adapter after trimming | Wrong adapter, too-low `-e`, or only partial stem used | Use the shared stem AGATCGGAAGAGC; raise `-e` to 0.15; BLAST the overrepresented sequence |
| Reads truncated / many lose a few bp | `-O` too low -> random 3-mer matches | Raise `-O` (e.g. 5); the default loses ~0.07 bp/read by chance |
| Aligner reports R1/R2 out of sync | Mates trimmed/filtered independently | Process pairs together (cutadapt `-p`; Trimmomatic paired outputs) |
| Small-RNA yields huge "reads" | Forgot `--discard-untrimmed` / length gate | Add `--discard-untrimmed -m 18 -M 30` |
| 3' G-content rise persists after trimming | 2-color poly-G is high-quality, not adapter | `cutadapt --nextseq-trim` or fastp auto poly-G |
| Half of R2 disappears in Trimmomatic | keepBothReads default False drops redundant R2 | Add `keepBothReads` (True) if both mates are needed downstream |

## References

Martin M. 2011. Cutadapt removes adapter sequences from high-throughput sequencing reads. EMBnet.journal 17(1):10-12.
Bolger AM, Lohse M, Usadel B. 2014. Trimmomatic: a flexible trimmer for Illumina sequence data. Bioinformatics 30(15):2114-2120.
MacManes MD. 2014. On the optimal trimming of high-throughput mRNA sequence data. Frontiers in Genetics 5:13.
Williams CR, Baccarella A, Parrish JZ, Kim CC. 2016. Trimming of sequence reads alters RNA-Seq gene expression estimates. BMC Bioinformatics 17:103.
Chen S, Zhou Y, Chen Y, Gu J. 2018. fastp: an ultra-fast all-in-one FASTQ preprocessor. Bioinformatics 34(17):i884-i890.

## Related Skills

read-qc/quality-reports - Read the adapter-content panel that triggers trimming
read-qc/quality-filtering - Quality and length filtering after adapter removal
read-qc/fastp-workflow - All-in-one adapter + quality trim with auto poly-G
read-qc/contamination-screening - k-mer removal of PhiX/vector/contaminant sequence
small-rna-seq/smrna-preprocessing - Full small-RNA adapter + length workflow
read-alignment/bwa-alignment - Soft-clipping aligner that handles low-quality tails without trimming
<!-- END FILE: read-qc/adapter-trimming/SKILL.md -->

## 子目录：read-qc/contamination-screening

<!-- BEGIN FILE: read-qc/contamination-screening/SKILL.md -->
---
name: bio-read-qc-contamination-screening
description: Detects contamination in sequencing reads - cross-species (FastQ Screen, Kraken2), vector/PhiX/adapter, rRNA, and same-species cross-sample/index-hopping and sample swaps (SNP fingerprints via verifyBamID2/NGSCheckMate/somalier). Use when suspecting cross-contamination, PDX host reads, microbial carry-over, or sample swaps, and to decide whether to report, filter, or align to a combined reference. For deep taxonomic profiling use metagenomics/kraken-classification.
tool_type: cli
primary_tool: fastq_screen
---

## Version Compatibility

Reference examples tested with: FastQ Screen 0.15+, Bowtie2 2.5+, Kraken2 2.1+, BBTools 39.0+, MultiQC 1.21+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Contamination Screening -- a species screen cannot see a same-species swap

Screen reads against a genome panel (FastQ Screen / Kraken2) for foreign ORGANISMS, and against SNP fingerprints for foreign or wrong INDIVIDUALS.

**"Check my reads for contamination"** -> Map a subsample against multiple references and/or fingerprint sample identity to find foreign DNA and mislabels.
- CLI: `fastq_screen --conf fastq_screen.conf sample.fastq.gz` (cross-species)
- CLI: `verifyBamID2 --SVDPrefix resource --BamFile sample.bam` (same-species contamination)

Scope: this skill OWNS contamination detection and the report-vs-filter decision. Deep taxonomic profiling/abundance -> metagenomics/kraken-classification, metagenomics/metaphlan-profiling. rRNA depletion as an RNA prep metric -> read-qc/rnaseq-qc. OUT OF SCOPE: adapter removal (read-qc/adapter-trimming).

## The Single Most Important Modern Insight

1. **A SPECIES screen answers "what ORGANISMS are here?"; a SNP FINGERPRINT answers "WHOSE DNA is this, and is it a mixture?" -- and these are orthogonal.** A species screen is structurally BLIND to same-species cross-sample contamination and sample swaps: a human-A + human-B mixture, or a mislabeled human file, produces a perfectly clean single-species profile. Most pipelines run only a species screen and declare the data clean. Any human or single-species-cohort pipeline needs BOTH a taxonomic screen AND a SNP-fingerprint identity/contamination check (verifyBamID2, NGSCheckMate, somalier, conpair).

2. **Index hopping is the same-species contamination that lives inside one run, and unique dual indexing (UDI) is the only clean fix.** On patterned flowcells (HiSeq X/4000, NovaSeq) ExAmp chemistry lets a free index adapter tag a fragment from another sample, spreading ~0.1-2% of reads into incorrect samples. Irrelevant for germline common variants, CATASTROPHIC for low-VAF work (ctDNA, single-cell, somatic) where hopped reads look like phantom low-frequency variants. Combinatorial indexing cannot detect it; UDI (a unique i7 AND i5 per sample) lets the demultiplexer drop impossible index pairs. UDI is effectively mandatory for ctDNA/plasma, single-cell, and low-input somatic.

3. **Default to SCREEN-AND-REPORT, not filter -- removing reads biases composition.** A species screen is a QC gate; if a contaminant is low, aligning to the correct reference simply will not place the foreign reads. Filter only a specific, named contaminant (PhiX before assembly, adapters before alignment) with a precise k-mer remover (BBDuk `ref=phix`), never "remove anything that hits the screen" (that also discards conserved rRNA/mito reads that belong to the sample). For PDX, align to a COMBINED human+mouse reference and keep human-assigned reads, OR use a dedicated post-alignment classifier (XenofilteR benchmarks above Xenome for variant false-positive rate); both beat hard pre-filtering on one genome, which mis-assigns conserved-region reads.

Deeper trap: reference-genome contamination corrupts the screen itself. A "human" hit can be bacterial sequence mis-deposited inside the human assembly (Conterminator found >2M contaminated GenBank entries). No `--confidence` setting fixes a wrong database; trust a deconned/curated DB and treat surprising single-source hits as DB artifacts until ruled out.

## The Contamination Taxonomy -- five classes, five fixes

| Class | What it is | Detect with | Fix |
|-------|-----------|-------------|-----|
| Cross-species | Mouse in human PDX; bacteria in culture | FastQ Screen, Kraken2/Bracken, sourmash, Xenome/XenofilteR | Combined-reference alignment; k-mer bin (report, do not blindly remove) |
| Cross-sample / index hopping | Same-species reads on the wrong sample (INVISIBLE to species screens) | verifyBamID2, NGSCheckMate, somalier, conpair | UDI at prep; drop impossible index pairs at demux |
| Vector / PhiX / adapter | Spike-in, cloning vector, linkers | UniVec/VecScreen; FastQ Screen adapter DB; BBDuk `ref=phix`/`ref=adapters` | k-mer trim/filter; upstream library QC |
| rRNA over-representation | Library-prep failure, not contamination | SortMeRNA, ribodetector | Re-prep / better depletion; filter only to recover depth |
| Cell-line: mycoplasma / misID | Mollicutes infection; HeLa cross-contamination | Kraken2 for Mollicutes; STR profiling for line identity | Clear culture or discard; STR-authenticate |

A pipeline that runs FastQ Screen and stops has checked exactly one of five boxes.

## Tool Taxonomy

| Tool | Mechanism | When |
|------|-----------|------|
| FastQ Screen | Map a subsample to a genome panel; classify hit categories | Cross-species QC gate; the workhorse screen |
| Kraken2 + Bracken | Exact-k-mer minimizer LCA classification; Bracken re-estimates abundance | Read-level taxonomy; many possible contaminants |
| BBSplit / BBDuk | k-mer binning / named-contaminant k-mer removal | Decontamination of a NAMED contaminant (PhiX, adapters) |
| Xenome / XenofilteR | Classify reads human vs mouse (k-mer / dual-alignment) | PDX host-graft disambiguation |
| sourmash | MinHash/FracMinHash containment sketches | Fast low-memory "what is in here?" screen |
| verifyBamID2 | Per-sample within-species contamination from population SNP AFs | Same-species contamination level (FREEMIX) |
| NGSCheckMate / somalier | SNP-fingerprint identity / relatedness | Sample swaps, tumor-normal pairing, longitudinal identity |
| conpair | Tumor-normal concordance + independent contamination | Matched T/N pairs |

## Decision Tree by Scenario

| Question | Use | Why |
|----------|-----|-----|
| Is a foreign ORGANISM present? | FastQ Screen or Kraken2 | Maps reads to species references |
| Is this the right INDIVIDUAL / one person? | NGSCheckMate / somalier | SNP fingerprint, species-screen-blind |
| What is the contamination LEVEL (human)? | verifyBamID2 (FREEMIX) | Estimates mixture fraction from SNP AFs |
| Tumor-normal pair: matched and clean? | conpair | Concordance + per-sample contamination |
| PDX host vs graft | Combined reference or a benchmarked classifier | XenofilteR > Xenome for SNV FP rate; both beat hard pre-filtering |
| Remove a NAMED contaminant | BBDuk `ref=...` | Precise k-mer removal, not "hits the screen" |
| Strip HUMAN reads before public deposition (non-human library) | hostile / NCBI sra-human-scrubber (HRRT) | Deposition compliance, not a QC gate; a masked T2T reference avoids stripping conserved microbial regions |

Default when uncertain: FastQ Screen as the QC gate for organisms, PLUS a SNP-fingerprint check (somalier/NGSCheckMate) for any human cohort.

## FastQ Screen

Maps a SUBSAMPLE (`--subset`, default 100000) with bowtie2 reporting >1 alignment, then classifies each read across the panel. Read the bar chart, not just "% mapped": contamination concentrates in `One_hit_one_genome` of an UNEXPECTED genome; homology (rRNA, mito, conserved loci) spreads into the `*_multiple_genomes` categories; high `Hit_no_genomes` means adapter dimer, a missing reference, or a novel organism (a diagnostic, not a verdict).

```bash
# Config: aligner binary + DATABASE lines (bowtie2 index prefixes)
cat > fastq_screen.conf <<'EOF'
BOWTIE2  /usr/local/bin/bowtie2
THREADS  8
DATABASE  Human  /refs/GRCh38_bt2/GRCh38
DATABASE  Mouse  /refs/GRCm39_bt2/GRCm39
DATABASE  Ecoli  /refs/Ecoli_bt2/Ecoli
DATABASE  PhiX   /refs/phix_bt2/phix
DATABASE  rRNA   /refs/rRNA_bt2/rRNA
EOF

fastq_screen --conf fastq_screen.conf --threads 8 --outdir screen/ *.fastq.gz
multiqc screen/                      # MultiQC parses *_screen.txt across samples

# Tag every read with a per-genome status, then extract a subset by pattern
fastq_screen --conf fastq_screen.conf --tag --filter 10000 sample.fastq.gz   # maps only to genome 1
fastq_screen --conf fastq_screen.conf --nohits sample.fastq.gz               # reads hitting nothing
```

`--filter` digits (one per genome, config order): 0=no map, 1=unique, 2=multi, 3=maps, 4=pass 0 or 1, 5=pass 0 or 2, -=ignore. `--subset 0` screens the whole file; `--bisulfite` uses Bismark.

## Kraken2 + Bracken (read-level taxonomy)

Default `--confidence 0.0` over-reports a long tail of spurious low-abundance species (a few shared k-mers suffice); raise to 0.05-0.1 and keep `--minimum-hit-groups 2` (or 3 for custom DBs). Kraken2 gives CLASSIFICATION; Bracken redistributes higher-rank reads to species for ABUNDANCE.

```bash
kraken2 --db /db/k2_standard --threads 8 --confidence 0.1 --paired \
        --report sample.kreport --use-names R1.fq.gz R2.fq.gz > sample.kraken
bracken -d /db/k2_standard -i sample.kreport -o sample.bracken -r 150 -l S
```

## Same-species: SNP fingerprints and index hopping

```bash
# verifyBamID2: FREEMIX = contamination fraction (action threshold ~0.02);
# FREEMIX~0 with CHIPMIX~1 indicates a SWAP, not contamination.
# --SVDPrefix points to the panel resource that ships with verifyBamID2 (resource/1000g.phase3...).
verifyBamID2 --SVDPrefix /res/1000g.phase3.100k.b38.vcf.gz.dat --BamFile sample.bam --Reference ref.fa

# somalier: extract genome sketches, then relate to find swaps / identity across a cohort.
# --sites = somalier's released sites.<build>.vcf.gz (github releases), not a custom panel.
somalier extract -d sites/ --sites sites.hg38.vcf.gz -f ref.fa sample.bam
somalier relate sites/*.somalier            # off-diagonal identity flags swaps

# conpair (tumor-normal): concordance + independent per-sample contamination
```

Index hopping is mitigated at demultiplexing with UDI (drop impossible i7,i5 pairs); residual contamination is then quantified by the SNP-fingerprint tools above.

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| "Single species, data is clean" but a swap is suspected | Species screen is blind to same-species swaps | Run somalier / NGSCheckMate on SNP fingerprints |
| Phantom low-VAF variants in ctDNA/single-cell | Index hopping on patterned flowcell | Use UDI; quantify residual with verifyBamID2/conpair |
| Kraken2 reports dozens of trace species | Default confidence 0.0 over-reports | Raise `--confidence` to 0.05-0.1; raise hit-groups |
| A "human" Kraken hit on a microbial isolate | Reference/DB contamination | Use a deconned DB; treat as artifact until confirmed |
| Filtering "contaminant" reads skews composition | Removed conserved rRNA/mito too | Remove a NAMED contaminant with BBDuk, not "hits the screen" |
| PDX human counts look biased | Hard pre-filtering of ambiguous reads | Align to combined human+mouse reference instead |

## References

Wingett SW, Andrews S. 2018. FastQ Screen: a tool for multi-genome mapping and quality control. F1000Research 7:1338.
Wood DE, Lu J, Langmead B. 2019. Improved metagenomic analysis with Kraken 2. Genome Biology 20:257.
Lu J, Breitwieser FP, Thielen P, Salzberg SL. 2017. Bracken: estimating species abundance in metagenomics data. PeerJ Computer Science 3:e104.
Steinegger M, Salzberg SL. 2020. Terminating contamination: large-scale search identifies more than 2,000,000 contaminated entries in GenBank. Genome Biology 21:115.
Conway T, Wazny J, Bromage A, et al. 2012. Xenome - a tool for classifying reads from xenograft samples. Bioinformatics 28(12):i172-i178.
Costello M, Fleharty M, Abreu J, et al. 2018. Characterization and remediation of sample index swaps by non-redundant dual indexing. BMC Genomics 19:332.
Zhang F, Flickinger M, Taliun SAG, et al. 2020. Ancestry-agnostic estimation of DNA sample contamination from sequence reads. Genome Research 30(2):185-194.
Lee S, Lee S, Ouellette S, Park WY, Lee EA, Park PJ. 2017. NGSCheckMate: software for validating sample identity in next-generation sequencing studies within and across data types. Nucleic Acids Research 45(11):e103.
Pedersen BS, Bhetariya PJ, Brown J, et al. 2020. Somalier: rapid relatedness estimation for cancer and germline studies using efficient genome sketches. Genome Medicine 12:62.

## Related Skills

read-qc/quality-reports - Bimodal GC and overrepresented sequences flag contamination
read-qc/adapter-trimming - Remove adapter contamination
read-qc/rnaseq-qc - rRNA fraction as a prep-efficiency metric
metagenomics/kraken-classification - Deeper taxonomic classification and profiling
variant-calling/joint-calling - Where SNP-fingerprint sample swaps do the most damage
<!-- END FILE: read-qc/contamination-screening/SKILL.md -->

## 子目录：read-qc/fastp-workflow

<!-- BEGIN FILE: read-qc/fastp-workflow/SKILL.md -->
---
name: bio-read-qc-fastp-workflow
description: Runs all-in-one FASTQ preprocessing with fastp in a single pass - adapter trimming via paired-end overlap analysis, quality/length filtering, 2-color poly-G removal, base correction, optional dedup/UMI/merge, and HTML/JSON reports. Use when preprocessing bulk Illumina data and wanting one fast tool instead of separate Cutadapt, Trimmomatic, and FastQC steps. For precise small-RNA/amplicon adapters use adapter-trimming; for molecule-accurate UMI dedup use umi-processing.
tool_type: cli
primary_tool: fastp
---

## Version Compatibility

Reference examples tested with: fastp 0.23+, FastQC 0.12+, MultiQC 1.21+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# fastp Workflow -- one C++ pass for adapter, quality, poly-G, and QC

Run adapter trimming, quality/length filtering, poly-G removal, and reporting in a single fast pass.

**"Preprocess my reads with fastp"** -> Trim adapters from the read overlap, filter low-quality reads, remove 2-color poly-G, and emit an HTML/JSON report.
- CLI: `fastp -i R1.fq.gz -I R2.fq.gz -o c_R1.fq.gz -O c_R2.fq.gz -h report.html -j report.json`

Scope: this skill OWNS general-purpose single-pass Illumina preprocessing. Precise small-RNA/amplicon/anchored adapters -> read-qc/adapter-trimming. Molecule-accurate UMI dedup/consensus -> read-qc/umi-processing. DNA coordinate dedup -> alignment-files/duplicate-handling. OUT OF SCOPE: transcriptome QC (read-qc/rnaseq-qc).

## The Single Most Important Modern Insight

1. **fastp trims paired-end adapters by OVERLAP ANALYSIS, needing no adapter sequence at all.** It aligns R1 against the reverse complement of R2, finds the insert-derived overlap, and trims whatever extends past it (the read-through region) -- so it can trim adapter down to a SINGLE trailing base, where sequence-matching tools need at least 3. The same overlap drives `--correction` (`-c`): where the mates disagree and one base is high-quality and the other very low, fastp overwrites the low-quality base with the high-quality call. This overlap machinery is why fastp is the default bulk PE preprocessor and why it needs no `--adapter_sequence` for standard libraries.

2. **`--dedup` is SEQUENCE-identity deduplication at the FASTQ level -- no coordinates, no UMI -- so it removes BIOLOGICAL duplicates too.** It cannot tell a PCR duplicate from a highly expressed transcript's fragment or a targeted amplicon. NEVER use `--dedup` for RNA-seq quantification, amplicon, or any assay where identical reads are genuine signal. For molecule-accurate removal use UMIs (read-qc/umi-processing); for DNA variant calling use coordinate-based dedup AFTER alignment (alignment-files/duplicate-handling). fastp `--dedup` is for the narrow case of removing exact-duplicate reads from a non-UMI library where that is known to be safe.

3. **Poly-G trimming auto-enables for 2-color instruments (NextSeq/NovaSeq) from the machine ID, because G is the no-signal call.** Leave it on; a high-quality poly-G tail is invisible to the quality filter. One fast pass does adapter + quality + poly-G + filtering + QC report, and the JSON feeds MultiQC -- but fastp does NOT replace cutadapt's precision for small-RNA 3' adapters, amplicon primers, or anchored/linked adapters.

## Tool Positioning

| Need | Use fastp? | Alternative |
|------|-----------|-------------|
| Bulk PE WGS/WES/RNA/cfDNA preprocessing | Yes (default) | -- |
| One pass: trim + filter + poly-G + QC report | Yes | -- |
| Small-RNA 3' adapter + tight length gate | No | cutadapt (read-qc/adapter-trimming) |
| Amplicon / anchored / linked primers | No | cutadapt |
| Molecule counting / ctDNA consensus | Extract only | umi_tools / fgbio (read-qc/umi-processing) |
| RNA-seq molecule dedup | No (`--dedup` is wrong) | UMIs, or do not dedup |

## Core Operations

```bash
# Single-end and paired-end basics
fastp -i in.fq.gz -o out.fq.gz
fastp -i R1.fq.gz -I R2.fq.gz -o c_R1.fq.gz -O c_R2.fq.gz

# Adapter: PE overlap is automatic; --detect_adapter_for_pe ADDS sequence-based detection on top
fastp -i R1.fq.gz -I R2.fq.gz -o c_R1.fq.gz -O c_R2.fq.gz --detect_adapter_for_pe
# Manual adapter sequences (SE auto-detects from data by default)
fastp -i in.fq.gz -o out.fq.gz --adapter_sequence AGATCGGAAGAGCACACGTCTGAACTCCAGTCA

# Quality FILTER (per-read): base <Q20 unqualified; drop if >40% unqualified or >5 Ns
fastp -i in.fq.gz -o out.fq.gz -q 20 -u 40 -n 5
# Quality TRIM (sliding window from 3', SLIDINGWINDOW analogue) + length gate
fastp -i in.fq.gz -o out.fq.gz --cut_right --cut_window_size 4 --cut_mean_quality 20 -l 36

# 2-color poly-G (auto for NextSeq/NovaSeq); poly-X for 3' poly-A etc.
fastp -i in.fq.gz -o out.fq.gz --trim_poly_g          # --poly_g_min_len 10 default
fastp -i in.fq.gz -o out.fq.gz --trim_poly_x

# Overlap base correction (PE only; high-Q mate fixes low-Q base)
fastp -i R1.fq.gz -I R2.fq.gz -o c_R1.fq.gz -O c_R2.fq.gz --correction

# Merge overlapping pairs (short inserts: cfDNA, small-RNA, aDNA). Produces THREE streams:
# the merged file is single-end (full insert) and un_R1/un_R2 stay paired -- align them separately
# (merged as SE, un_R1/un_R2 as PE) and combine the BAMs.
fastp -i R1.fq.gz -I R2.fq.gz --merge --merged_out merged.fq.gz -o un_R1.fq.gz -O un_R2.fq.gz

# UMI extraction: fastp moves the inline UMI out of the read before trimming; molecule-accurate
# dedup/consensus still happens AFTER alignment (umi_tools/fgbio), not in fastp
fastp -i R1.fq.gz -I R2.fq.gz -o c_R1.fq.gz -O c_R2.fq.gz --umi --umi_loc read1 --umi_len 8
```

Key flags: `-q` qualified quality (default 15), `-u` unqualified percent limit (40), `-n` N limit (5), `-e` average-quality filter (0=off), `-l` length required (15), `--length_limit` (0=off), `--cut_right/--cut_front/--cut_tail` window cut modes (off by default), `--cut_window_size` (4), `--cut_mean_quality` (Q20), `--thread/-w` (default 3), `-h/-j` HTML/JSON report.

## Complete Workflows

```bash
# Standard Illumina PE (4-color: HiSeq/MiSeq)
fastp -i raw_R1.fq.gz -I raw_R2.fq.gz -o clean_R1.fq.gz -O clean_R2.fq.gz \
      --detect_adapter_for_pe --cut_right --cut_window_size 4 --cut_mean_quality 20 \
      -q 20 -l 36 -w 8 -h sample.html -j sample.json

# NovaSeq / NextSeq (2-color): add poly-G (auto, but explicit for clarity)
fastp -i raw_R1.fq.gz -I raw_R2.fq.gz -o clean_R1.fq.gz -O clean_R2.fq.gz \
      --detect_adapter_for_pe --trim_poly_g \
      --cut_right --cut_window_size 4 --cut_mean_quality 20 -q 20 -l 36 -w 8 \
      -h sample.html -j sample.json

# RNA-seq: light trim only (aligner soft-clips; do NOT --dedup), longer min length
fastp -i raw_R1.fq.gz -I raw_R2.fq.gz -o clean_R1.fq.gz -O clean_R2.fq.gz \
      --detect_adapter_for_pe -q 20 -l 50 -w 8 -h sample.html -j sample.json
```

## Parsing the JSON report

```python
import json

with open('sample.json') as f:
    report = json.load(f)

after = report['summary']['after_filtering']
print(f"reads kept: {after['total_reads']}, Q30: {after['q30_rate']:.2%}")
print(f"duplication: {report['duplication']['rate']:.2%}")    # diagnostic only -- do not auto-dedup
```

MultiQC parses fastp JSON directly: `multiqc .` over a directory of `*.json` builds the cohort report (read-qc/quality-reports).

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| RNA-seq counts deflated after fastp | Used `--dedup` (sequence dedup removes biological dups) | Drop `--dedup` for RNA-seq; never sequence-dedup expression data |
| Adapter not trimmed (SE) | SE has no overlap; relies on data auto-detect | Pass `--adapter_sequence` explicitly for SE |
| Poly-G remains | 4-color run, or auto-detect missed the instrument | Add `--trim_poly_g` explicitly |
| Small-RNA results poor | fastp overlap is not precise enough for ~22 nt inserts | Use cutadapt with `--discard-untrimmed` (read-qc/adapter-trimming) |
| Over-trimmed RNA-seq | Aggressive `--cut_right` quality | Light trim only; aligner soft-clips (read-qc/quality-filtering) |
| UMI dedup expected but none happened | `--umi` only EXTRACTS; dedup is post-alignment | Extract here, dedup with umi_tools/fgbio after mapping (read-qc/umi-processing) |

## References

Chen S, Zhou Y, Chen Y, Gu J. 2018. fastp: an ultra-fast all-in-one FASTQ preprocessor. Bioinformatics 34(17):i884-i890.
Chen S. 2023. Ultrafast one-pass FASTQ data preprocessing, quality control, and deduplication using fastp. iMeta 2(2):e107.
Ewels P, Magnusson M, Lundin S, Kaller M. 2016. MultiQC: summarize analysis results for multiple tools and samples in a single report. Bioinformatics 32(19):3047-3048.

## Related Skills

read-qc/adapter-trimming - Precise adapter/primer control for small-RNA and amplicon
read-qc/quality-filtering - Detailed quality/length filtering options and the trim-light evidence base
read-qc/quality-reports - Aggregate fastp JSON across samples with MultiQC
read-qc/umi-processing - Molecule-accurate UMI dedup and consensus after alignment
alignment-files/duplicate-handling - Coordinate-based duplicate marking for DNA variant calling
<!-- END FILE: read-qc/fastp-workflow/SKILL.md -->

## 子目录：read-qc/quality-filtering

<!-- BEGIN FILE: read-qc/quality-filtering/SKILL.md -->
---
name: bio-read-qc-quality-filtering
description: Filters reads by quality, length, N content, and complexity with Trimmomatic, fastp, and Cutadapt, including sliding-window trimming, per-read unqualified-base filtering, and 2-color poly-G removal. Use when reads have poor-quality tails, when an assembly or k-mer workflow needs clean input, or when a junk read subpopulation must be dropped. For adapter removal use adapter-trimming; for all-in-one preprocessing use fastp-workflow.
tool_type: cli
primary_tool: trimmomatic
---

## Version Compatibility

Reference examples tested with: Trimmomatic 0.39+, fastp 0.23+, Cutadapt 4.4+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Quality Filtering -- trim lightly or not at all, and never without a length filter

Trim low-quality bases and drop low-quality reads with Trimmomatic (sliding window / MAXINFO), fastp (per-read filter + window cut), or Cutadapt (BWA-style quality trim).

**"Filter reads by quality"** -> Remove low-quality bases and/or discard reads below quality/length thresholds.
- CLI: `fastp -i in.fq -o out.fq --cut_right -q 20 -l 36` (window trim + per-read filter + length gate)
- CLI: `trimmomatic SE in.fq out.fq SLIDINGWINDOW:4:20 MINLEN:36`

Scope: this skill OWNS quality/length/N/complexity filtering. Adapter removal -> read-qc/adapter-trimming. Single-pass trim+QC -> read-qc/fastp-workflow. Reading the quality plots -> read-qc/quality-reports. OUT OF SCOPE: contamination removal (read-qc/contamination-screening).

## The Single Most Important Modern Insight

1. **Modern local aligners SOFT-CLIP low-quality tails, so quality trimming is usually unnecessary -- and AGGRESSIVE quality trimming actively harms downstream results.** Williams 2016 showed aggressive trimming changed expression estimates for >10% of genes; Del Fabbro 2013 showed stringent Q>30 DEGRADES de novo assembly; MacManes 2014 found gentle trimming (remove only Phred<2-5) optimal for RNA-seq; GATK discourages quality trimming because BQSR recalibrates qualities itself. Trim ADAPTER always (read-qc/adapter-trimming); quality-trim lightly or not at all before a soft-clipping aligner. The workflows that genuinely need quality trimming are assembly, k-mer/pseudo-alignment, small-RNA, amplicon, and variant calling WITHOUT BQSR.

2. **Quality FILTERING (drop whole reads) and quality TRIMMING (cut bases within a read) are different operations with different tools.** fastp's `-q/-u/-n` filters whole reads by the fraction of unqualified bases; `--cut_right` / Trimmomatic `SLIDINGWINDOW` trims bases from a window scan. Filtering removes a junk subpopulation (a low-Q hump in the per-sequence-quality plot); trimming shortens reads with decayed tails. Choose by whether the problem is some bad reads or bad ends.

3. **A short post-trim read mis-maps, so quality trimming MUST be paired with a minimum-length filter.** Williams 2016 showed that adding a post-trim min-length filter mitigates most of the expression distortion that trimming introduces, because over-trimmed fragments that would map spuriously are dropped instead. `MINLEN` (Trimmomatic, always last), `-l` (fastp), `-m` (cutadapt) are not optional add-ons; they are the safety mechanism that makes trimming safe.

Two-color note: on NextSeq/NovaSeq the quality scores are binned to four values (RTA3: 2, 12, 23, 37), so a sliding-window threshold like 4:15 partitions between the 12 and 23 bins rather than acting on a smooth gradient -- thresholds tuned on HiSeq-era 0-40 qualities behave differently. And poly-G tails are HIGH quality, so a quality filter does not remove them (use poly-G trimming).

## Tool Taxonomy

| Tool | Mechanism | When it wins |
|------|-----------|--------------|
| fastp | Per-read unqualified-base filter (`-q/-u/-n`) + window cut (`--cut_right`) + auto poly-G | DEFAULT; one fast pass, filtering and trimming together |
| Trimmomatic | `SLIDINGWINDOW` / `MAXINFO` window trim; ordered step pipeline; orphan handling | Legacy/reproducibility pipelines; MAXINFO length-vs-quality balance |
| Cutadapt | `-q` BWA running-sum quality trim (combined with adapter removal) | When already running cutadapt for adapters; precise per-end control |

## Decision Tree by Scenario

| Workflow | Quality trimming | Why |
|----------|------------------|-----|
| Alignment-based DNA/RNA (BWA-MEM, STAR, Bowtie2 local, HISAT2) | Light or none | Aligner soft-clips tails; aggressive trim distorts expression |
| GATK variant calling with BQSR | None | BQSR recalibrates; trimming interferes |
| De novo assembly | Moderate (~Q20) + min-length | Low-Q errors corrupt the de Bruijn graph; stringent Q>30 over-trims |
| k-mer / pseudo-alignment (kallisto/salmon) | Light + adapter | Errors create phantom k-mers |
| A junk read subpopulation (bimodal per-seq quality) | FILTER whole reads (`-e`/AVGQUAL) | Trimming cannot fix a globally bad read |
| Variant calling WITHOUT BQSR | Moderate + min-length | No recalibration safety net |

Default when uncertain: trim adapter, apply a light window trim plus a minimum-length filter, then confirm with FastQC.

## Trimmomatic

Steps run in COMMAND-LINE ORDER; put quality steps before MINLEN so the length check reflects all trimming.

```bash
# Single-end: light leading/trailing + window, length-gated
trimmomatic SE -phred33 in.fq.gz out.fq.gz \
    LEADING:3 TRAILING:3 SLIDINGWINDOW:4:20 MINLEN:36

# Paired-end (four outputs: paired + orphan)
trimmomatic PE -phred33 -threads 8 \
    R1.fq.gz R2.fq.gz \
    R1_paired.fq.gz R1_unpaired.fq.gz R2_paired.fq.gz R2_unpaired.fq.gz \
    SLIDINGWINDOW:4:20 MINLEN:36

# MAXINFO: adaptive length-vs-quality balance (strictness <0.2 favors length, >0.8 favors correctness)
trimmomatic SE in.fq.gz out.fq.gz MAXINFO:40:0.5 MINLEN:36
```

| Step | Meaning |
|------|---------|
| SLIDINGWINDOW:W:Q | scan 5'->3'; cut from the point where the W-bp window mean drops below Q |
| MAXINFO:L:S | adaptive trim balancing target length L against error rate; strictness S in 0-1 |
| LEADING:Q / TRAILING:Q | cut 5'/3' bases below Q (also removes N) |
| MINLEN:L / AVGQUAL:Q | DROP read if shorter than L / if mean quality below Q |
| CROP:L / HEADCROP:N | cap length / remove first N bases (do NOT HEADCROP random-hexamer bias -- see below) |

Do NOT HEADCROP the first ~12 bp of RNA-seq to "fix" the wavy per-base-content plot: that pattern is random-hexamer priming bias (Hansen 2010), not adapter, and trimming it just discards real data without removing the underlying bias.

## fastp

fastp separates per-read FILTERING from window TRIMMING. Quality filtering is on by default (-q 15).

```bash
# Per-read quality filter: base < Q20 is 'unqualified'; drop read if >40% unqualified or >5 Ns
fastp -i in.fq.gz -o out.fq.gz -q 20 -u 40 -n 5 -l 36

# Window trim from the 3' (Trimmomatic SLIDINGWINDOW analogue) + length gate
fastp -i R1.fq.gz -I R2.fq.gz -o R1.fq.gz -O R2.fq.gz \
      --cut_right --cut_window_size 4 --cut_mean_quality 20 -l 36

# Drop globally low-quality reads by mean quality (filter, not trim)
fastp -i in.fq.gz -o out.fq.gz -e 25

# 2-color poly-G (auto-enabled for NextSeq/NovaSeq from the instrument ID)
fastp -i in.fq.gz -o out.fq.gz --trim_poly_g

# Low-complexity filter (e.g. poly-A / homopolymer-rich reads)
fastp -i in.fq.gz -o out.fq.gz --low_complexity_filter --complexity_threshold 30
```

fastp flags: `-q` qualified quality (default 15), `-u` unqualified percent limit (default 40), `-n` N base limit (default 5), `-e` average-quality filter (default 0 = off), `-l` length required (default 15), `--length_limit` max length (long form only), `--cut_front/--cut_tail/--cut_right` window cut modes (off by default), `--cut_window_size` (4), `--cut_mean_quality` (Q20).

## Cutadapt

`-q` uses the BWA running-partial-sum algorithm, not a fixed cutoff, so a single high-Q base inside a low-Q run does not stop trimming. Quality trimming runs BEFORE adapter removal.

```bash
# 3'-only quality trim with a length gate (5',3' form: -q 15,20)
cutadapt -q 20 -m 36 -o out.fq.gz in.fq.gz

# Combined adapter + light quality trim, paired
cutadapt -a AGATCGGAAGAGC -A AGATCGGAAGAGC -q 20 -m 36 \
         -o R1.fq.gz -p R2.fq.gz R1.fq.gz R2.fq.gz
```

## Quantitative Thresholds

| Parameter | Typical | Rationale |
|-----------|---------|-----------|
| Window quality | Q20 (4:20) | 1% error; light. Aggressive (Q25-30) distorts expression/assembly (Williams 2016, Del Fabbro 2013) |
| fastp -q / -u | Q15 / 40% | fastp defaults; a base under Q15 is unqualified, read dropped if >40% unqualified |
| MINLEN / -l / -m | 36 (150 bp reads) | Mandatory after trimming; short reads mis-map. Scale up for longer inserts |
| complexity_threshold | 30 (30%) | fastp default for low-complexity filtering |
| MAXINFO strictness | 0.2-0.8 | <0.2 favors length, >0.8 favors correctness |

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| Expression estimates shift for many genes | Aggressive quality trimming | Trim lightly; always add a min-length filter (Williams 2016) |
| Variant calling worse after trimming | Trimmed before/around BQSR | Do not quality-trim for GATK BQSR workflows |
| Window threshold behaves oddly on NovaSeq | Binned quality (4 values) makes windows coarse | Expect step-like behavior; do not port HiSeq thresholds blindly |
| Reads mis-map after trimming | No min-length filter, over-trimmed fragments | Add MINLEN / -l / -m |
| Poly-G tails survive quality filtering | Poly-G is high quality on 2-color | Use `--trim_poly_g` / cutadapt `--nextseq-trim` |
| R1/R2 out of sync | Independent SE trimming of mates | Use Trimmomatic paired outputs or fastp/cutadapt paired mode |

## References

Bolger AM, Lohse M, Usadel B. 2014. Trimmomatic: a flexible trimmer for Illumina sequence data. Bioinformatics 30(15):2114-2120.
Chen S, Zhou Y, Chen Y, Gu J. 2018. fastp: an ultra-fast all-in-one FASTQ preprocessor. Bioinformatics 34(17):i884-i890.
MacManes MD. 2014. On the optimal trimming of high-throughput mRNA sequence data. Frontiers in Genetics 5:13.
Del Fabbro C, Scalabrin S, Morgante M, Giorgi FM. 2013. An extensive evaluation of read trimming effects on Illumina NGS data analysis. PLoS ONE 8(12):e85024.
Williams CR, Baccarella A, Parrish JZ, Kim CC. 2016. Trimming of sequence reads alters RNA-Seq gene expression estimates. BMC Bioinformatics 17:103.
Hansen KD, Brenner SE, Dudoit S. 2010. Biases in Illumina transcriptome sequencing caused by random hexamer priming. Nucleic Acids Research 38(12):e131.

## Related Skills

read-qc/adapter-trimming - Remove adapter before quality filtering
read-qc/quality-reports - Read the quality plots that motivate filtering
read-qc/fastp-workflow - All-in-one preprocessing in a single pass
read-alignment/bwa-alignment - Soft-clipping aligner that absorbs low-quality tails
read-alignment/star-alignment - Soft-clipping RNA aligner (light trimming preferred)
<!-- END FILE: read-qc/quality-filtering/SKILL.md -->

## 子目录：read-qc/quality-reports

<!-- BEGIN FILE: read-qc/quality-reports/SKILL.md -->
---
name: bio-read-qc-quality-reports
description: Generates and interprets per-file and cross-sample QC reports from FASTQ data with FastQC, falco, and MultiQC, covering Phred quality, per-base composition, GC, duplication, overrepresented sequences, and adapter content. Use when performing initial QC on raw sequencing reads, validating preprocessing, or judging a multi-sample cohort for outliers and batch effects. For long reads use NanoPlot; for adapter/quality remediation route to adapter-trimming, quality-filtering, or fastp-workflow.
tool_type: cli
primary_tool: fastqc
---

## Version Compatibility

Reference examples tested with: FastQC 0.12+, MultiQC 1.21+, falco 1.2+, seqkit 2.5+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Quality Reports -- the traffic light is a hypothesis about WGS DNA, not a verdict

Generate per-file QC with FastQC/falco and aggregate the cohort with MultiQC, then READ THE PLOTS against the assay rather than trusting pass/warn/fail.

**"Run quality control on FASTQ files"** -> Compute per-base quality, composition, GC, duplication, and adapter profiles per file, then aggregate across samples to find outliers.
- CLI: `fastqc -t 8 *.fastq.gz` then `multiqc .`
- Long reads: `NanoPlot --fastq reads.fastq.gz` (FastQC assumes fixed-length short reads)

Scope: this skill OWNS raw-FASTQ QC reporting and interpretation, and carries the cross-cutting quality-score / chemistry / duplication concepts the rest of read-qc depends on. Remediation lives elsewhere -> read-qc/adapter-trimming, read-qc/quality-filtering, read-qc/fastp-workflow. Contamination -> read-qc/contamination-screening. Transcriptome QC on the BAM -> read-qc/rnaseq-qc. OUT OF SCOPE: any modification of the reads.

## The Single Most Important Modern Insight

1. **FastQC pass/warn/fail are heuristics calibrated to random whole-genome DNA, so they FALSE-FAIL on every other assay.** RNA-seq fails per-base content (random-hexamer bias) and duplication (high-expression molecules); amplicon fails duplication and GC by design; bisulfite fails base content (C->T conversion); small-RNA fails length distribution; single-cell R1 fails everything (it is barcode+UMI, not biology). A red light is a HYPOTHESIS about a WGS library. For any other protocol, first ask "is this module expected to deviate for this chemistry?" before treating the red as a defect. Read the plot shape; the traffic light is calibration noise.

2. **On 2-color chemistry (NextSeq, NovaSeq, MiniSeq) G is the ABSENCE of signal, so poly-G tails are called at HIGH quality and the quality plot will NOT flag them.** When a cluster runs out of template, dark cycles read as a run of Gs with high confidence. Quality trimming alone does not remove them. They surface as a 3'-end RISE in G content (per-base sequence content) and a spurious high-GC spike, and they mis-map or manufacture false somatic variants if left in. The fix is a chemistry-aware poly-G trim (fastp auto-enables it from the instrument ID; cutadapt `--nextseq-trim`), not a quality cutoff. Read the per-base CONTENT plot on any 2-color run, not just the quality plot.

3. **The duplication percentage is read-level and complexity-blind: it cannot tell a PCR jackpot from genuine high abundance.** Identical reads from a highly expressed transcript, a targeted amplicon, or a ChIP/ATAC peak are counted as duplicates even though they are independent biological molecules. Duplication % is a function of BOTH library complexity AND sequencing depth (a good library sequenced deeply shows high duplication). It is a PROMPT to reason about library complexity (preseq), never an automatic "remove duplicates" -- and removing duplicates in non-UMI RNA-seq is actively wrong (read-qc/umi-processing, read-qc/rnaseq-qc).

Bonus trap: NovaSeq/NextSeq emit BINNED quality scores (RTA3 uses four values: 2, 12, 23, 37), so FastQC box plots look blocky/quantized. This is the instrument's quality table, NOT bad data and NOT something to fix. The bin edges are RTA-version-specific (NovaSeq X / RTA4 differs) -- never hard-code one bin set.

## Tool Taxonomy

| Tool | Role | Mechanism / when |
|------|------|------------------|
| FastQC | Per-file short-read QC (HTML + zip) | Java; the module set below; duplication/overrep from the first 100k distinct reads. The de-facto standard per-file report. |
| falco | Drop-in FastQC re-implementation (C++) | ~3x faster, lower memory, same module names and MultiQC-compatible output. Use when FastQC throughput bottlenecks a large cohort. |
| MultiQC | Cross-sample aggregator (SCRAPER, not a re-analyzer) | Walks directories, regex-matches each tool's log/report, parses the numbers, builds one cohort report. The unit of review for multi-sample studies. |
| seqkit stats | Instant tabular FASTA/FASTQ numbers | `seqkit stats -a`: N50, Q20%, Q30%, GC%, length quartiles. For quick numbers and assembly/long-read contexts where FastQC is the wrong shape. |
| NanoPlot / NanoComp | Long-read (ONT/PacBio) QC | Read-length and quality distributions, yield, N50, length-vs-quality. The correct first pass for long reads; FastQC's fixed-length assumptions break there. |

## Decision Tree by Scenario

| Scenario | Use | Why |
|----------|-----|-----|
| Per-file Illumina short-read QC | FastQC (or falco) | Module-level diagnostics; read the plots by assay |
| Many samples / a study cohort | FastQC/falco then MultiQC | Outlier and batch detection is RELATIVE; only visible overlaid |
| Long reads (ONT/PacBio) | NanoPlot / NanoComp | FastQC is built for fixed-length short reads |
| Instant numbers, assembly input | seqkit stats -a | N50/Q20/Q30/GC in one line; no HTML overhead |
| Large cohort, FastQC too slow | falco then MultiQC | Same output, ~3x faster |

Default when uncertain: FastQC on each file, then MultiQC over the run directory, and judge each sample against the cohort.

## FastQC Modules -- thresholds and the expert read

Thresholds are FastQC's `limits.txt` defaults (calibrated to random WGS DNA). The expert read is what to conclude BEYOND the traffic light.

| Module | Default warn / fail | Expert read |
|--------|--------------------|-------------|
| Per base sequence quality | warn LQ<10 or median<25; fail LQ<5 or median<20 | 3' decay is normal; blocky boxes on NovaSeq are binning; this plot will NOT reveal poly-G on 2-color |
| Per tile sequence quality | spatial deviation (no numeric) | A hot tile band across cycles = a localized flowcell problem (bubble, debris, edge); reason no MultiQC table replaces raw FastQC |
| Per sequence quality scores | distribution of per-read mean Q | A low-Q hump = a junk subpopulation to FILTER (not trim) |
| Per base sequence content | warn dev>10%; fail dev>20% | First ~12 bp skew = random-hexamer priming (Hansen 2010), expected for RNA-seq, do NOT trim it. A 3'-end skew is poly-G / adapter -- act on that |
| Per sequence GC content | warn dev>15%; fail dev>30% | SHAPE matters: bimodal/secondary peak = contamination; sharp spike = adapter dimer / overrepresented; a shifted single peak = wrong-GC reference assumption |
| Per base N content | warn N>5%; fail N>20% | Ns at a fixed position = a failed cycle; rising 3' Ns = dying clusters |
| Sequence length distribution | warn if lengths differ; fail if any length 0 | WARNs trivially after trimming and on long reads -- ignore for those |
| Sequence duplication levels | warn if <70% would remain; fail if <50% | Read-level, complexity-blind (see insight 3); high = think complexity, not dedup |
| Overrepresented sequences | warn >0.1%; fail >1% | Most diagnostic module: it prints the sequence -- BLAST it (adapter dimer, rRNA, primer, poly-G) |
| Adapter content | warn k-mer>5%; fail >10% | A curve climbing toward 3' = read-through from short inserts; this panel IS an insert-size readout (route to adapter-trimming) |
| K-mer content | (deprecated, off by default) | Only appears in old reports; do not build guidance on it |

Algorithm note (why duplication/overrep are estimates): FastQC tracks only the first 100,000 DISTINCT sequences, keys on the first 50 bp for reads >75 bp (so 3' errors do not fragment a duplicate family), counts by exact identity, and extrapolates the "% remaining if deduplicated" headline. It is a sample-based estimate, not a full-library dedup.

## Duplication Taxonomy -- four causes, four actions

| Class | Mechanism | Detected by | Action |
|-------|-----------|-------------|--------|
| Optical | One real cluster mis-segmented (non-patterned flowcell) | Same tile, pixel distance (Picard default 100) | Removable; spatially local artifact |
| ExAmp / patterned | One molecule seeds two nanowells (HiSeq X/4000, NovaSeq) | Spatially clustered, larger radius (Picard 2500 for patterned) | Removable; the reason patterned flowcells need the bigger pixel distance |
| PCR | Same fragment amplified and sequenced twice | Identical 5' coordinates post-alignment (+UMI if present) | Mark/remove for variant calling; NEVER coordinate-dedup amplicon (use UMIs) |
| Natural / biological | Independent identical molecules (high coverage, expressed genes, amplicon start) | Indistinguishable from PCR at read level without UMIs | KEEP -- removing biases quantification (do not dedup non-UMI RNA-seq) |

The read-level duplication % FastQC reports cannot separate these. Use preseq (Daley & Smith 2013) to model the complexity curve and ask "how many NEW molecules would more sequencing buy?" -- that curve, not a single %, judges whether a library is exhausted or just deeply sequenced.

## Quality scores and encoding

Phred Q = -10*log10(P_error): Q20 = 1% error, Q30 = 0.1%, Q40 = 0.01%. Q30 is the routine Illumina target; bulk Q40+ is uncommon on legacy chemistry (phasing, signal decay) and is a tell for re-binned or synthetic data on old runs, though XLEAP-SBS (NovaSeq X, NextSeq 2000) genuinely reaches Q40+. Modern data is universally Phred+33; any Phred+64 file (Illumina 1.3-1.7) feeds 31-too-high scores to a +33-assuming tool and passes garbage silently -- convert it (`seqtk seq -Q64 -V`). A quality byte below ASCII 64 (digits/punctuation) proves +33; detection tools sample reads to break ties.

## MultiQC -- the cohort is the unit of review

MultiQC does NOT re-analyze data; it scrapes tool logs/reports (`search_patterns.yaml`), parses the numbers, and tabulates them per sample. Consequences: it is only as good as the files left on disk and the sample-name parsing (name collisions merge samples -- check `multiqc_data/multiqc_sources.txt`), and it reports whatever the upstream tool wrote (a wrong reference or wrong strandedness shows as a coherent-but-wrong table, not an error). Read the General Statistics table FIRST -- outliers jump out as a column anomaly -- then overlay per-base-quality / GC / duplication and ask whether the low-quality set maps to one lane / prep batch / operator. The batch effect caught here at QC is the one not chased for a month in the DE results.

```bash
# Per-file QC, then aggregate the run
fastqc -t 8 -o qc/raw/ raw_data/*.fastq.gz
multiqc qc/raw/ -o qc/multiqc/ -f

# Compare before vs after trimming in one report
fastqc -t 8 -o qc/trimmed/ trimmed/*.fastq.gz
multiqc qc/ -o qc/compare/ -f          # picks up both raw/ and trimmed/

# Long reads do not go through FastQC
NanoPlot --fastq ont_reads.fastq.gz -o qc/nanoplot/
```

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| Every RNA-seq sample fails per-base content | Random-hexamer 5' bias (Hansen 2010) | Expected; do not trim the first bases |
| High-Q reads but a 3' G-content rise on NovaSeq | 2-color poly-G (dark cycles = G) | Chemistry-aware poly-G trim (fastp / cutadapt --nextseq-trim), not -q |
| FastQC quality boxes look quantized/blocky | NovaSeq/NextSeq binned qualities (RTA3) | Expected; not a defect, do not "fix" |
| MultiQC merges two samples into one row | Over-aggressive name cleaning / collision | Check multiqc_sources.txt; use `--fn_as_s_name` or fix names |
| Duplication 60%, urge to dedup RNA-seq | Read-level dup is complexity-blind | Do not dedup non-UMI RNA-seq; assess complexity (preseq) |
| FastQC crashes / huge plot on long reads | Fixed-length short-read assumptions | Use NanoPlot / seqkit stats instead |
| FastQC module missing in MultiQC | The fastqc_data.txt was not on disk / wrong dir | Point MultiQC at the directory holding the zip/data files |

## References

de Sena Brandine G, Smith AD. 2019. Falco: high-speed FastQC emulation for quality control of sequencing data. F1000Research 8:1874.
Ewing B, Hillier L, Wendl MC, Green P. 1998. Base-calling of automated sequencer traces using phred. I. Accuracy assessment. Genome Research 8(3):175-185.
Ewing B, Green P. 1998. Base-calling of automated sequencer traces using phred. II. Error probabilities. Genome Research 8(3):186-194.
Hansen KD, Brenner SE, Dudoit S. 2010. Biases in Illumina transcriptome sequencing caused by random hexamer priming. Nucleic Acids Research 38(12):e131.
Daley T, Smith AD. 2013. Predicting the molecular complexity of sequencing libraries. Nature Methods 10(4):325-327.
Ewels P, Magnusson M, Lundin S, Kaller M. 2016. MultiQC: summarize analysis results for multiple tools and samples in a single report. Bioinformatics 32(19):3047-3048.
Shen W, Le S, Li Y, Hu F. 2016. SeqKit: a cross-platform and ultrafast toolkit for FASTA/Q file manipulation. PLoS ONE 11(10):e0163962.
De Coster W, D'Hert S, Schultz DT, Cruts M, Van Broeckhoven C. 2018. NanoPack: visualizing and processing long-read sequencing data. Bioinformatics 34(15):2666-2669.

## Related Skills

read-qc/adapter-trimming - Remove read-through adapter flagged by the adapter-content panel
read-qc/quality-filtering - Drop low-quality reads and trim ends
read-qc/fastp-workflow - All-in-one QC + trim, including 2-color poly-G
read-qc/contamination-screening - Resolve a bimodal-GC or unexpected overrepresented-sequence signal
read-qc/rnaseq-qc - Transcriptome QC (strandedness, gene-body coverage) on the aligned BAM
sequence-io/sequence-statistics - Programmatic per-file sequence summaries
<!-- END FILE: read-qc/quality-reports/SKILL.md -->

## 子目录：read-qc/rnaseq-qc

<!-- BEGIN FILE: read-qc/rnaseq-qc/SKILL.md -->
---
name: bio-read-qc-rnaseq-qc
description: Runs RNA-seq-specific post-alignment QC - strandedness inference, gene-body 5'-3' coverage, read distribution (exonic/intronic/intergenic), rRNA/globin/mitochondrial rate, transcript integrity (TIN), and saturation - with RSeQC, Qualimap, RNA-SeQC, and Picard. Use when validating RNA-seq libraries before quantification or differential expression, diagnosing degradation or gDNA contamination, or determining library strandedness. For raw-FASTQ QC use quality-reports; for UMI dedup use umi-processing.
tool_type: mixed
primary_tool: RSeQC
---

## Version Compatibility

Reference examples tested with: RSeQC 5.0+, Qualimap 2.3+, RNA-SeQC 2.4+, Picard 3.1+, salmon 1.10+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# RNA-seq QC -- post-alignment metrics that have no DNA analogue

Assess strandedness, integrity, feature distribution, and enrichment on the ALIGNED BAM, using RSeQC / Qualimap / RNA-SeQC / Picard against a gene model.

**"Run RNA-seq QC"** -> Infer strandedness, gene-body coverage, exonic/intronic/intergenic distribution, rRNA rate, and TIN from the BAM.
- CLI: `infer_experiment.py -i aligned.bam -r genes.bed12` (strandedness)
- CLI: `picard CollectRnaSeqMetrics` / `qualimap rnaseq` / `rnaseqc collapsed.gtf in.bam out/`

Scope: this skill OWNS transcriptome QC on the aligned BAM. Raw-FASTQ QC (adapters, base quality) -> read-qc/quality-reports. UMI dedup -> read-qc/umi-processing. Quantification -> rna-quantification/featurecounts-counting. OUT OF SCOPE: differential expression (differential-expression/deseq2-basics).

## The Single Most Important Modern Insight

1. **These are POST-ALIGNMENT QC: every metric needs an aligned BAM AND a gene model (BED12 / GTF / refFlat / collapsed-GTF), which is the line that separates them from FastQC.** FastQC answers "is the sequencer output clean?"; RNA-seq QC answers "did I sequence the transcriptome I think I sequenced, in the orientation I think, with the integrity I think?" The metrics below (strand, exonic rate, rRNA rate, 5'-3' bias) have no DNA analogue because DNA has no exons, no strand of transcription, and no rRNA fraction. The most common setup error is feeding the wrong gene-model format (RSeQC wants BED12; Qualimap a GTF; RNA-SeQC a COLLAPSED GTF; Picard a refFlat + ribosomal_intervals).

2. **Getting strandedness wrong SILENTLY HALVES OR ZEROS the counts -- no error is thrown.** dUTP (TruSeq Stranded mRNA, most rRNA-depletion kits) is fr-firststrand = REVERSE = featureCounts `-s 2` = htseq `reverse` = salmon `ISR` = STAR ReadsPerGene column 4. Run it as "forward" and reads land on the antisense gene: counts collapse toward zero and the antisense neighbor inflates (running stranded data as UNSTRANDED, by contrast, roughly doubles counts). The tell is a huge "assigned to no feature" fraction or counts ~2x below the unstranded run. ALWAYS infer strandedness empirically (`infer_experiment.py`, salmon `-l A`, or how_are_we_stranded_here) before quantifying -- never assume from the kit name.

3. **In standard bulk RNA-seq WITHOUT UMIs, do NOT mark or remove duplicates.** A highly expressed gene legitimately produces many fragments sharing identical coordinates; at the read level a PCR duplicate and a natural duplicate are INDISTINGUISHABLE. Coordinate dedup (Picard MarkDuplicates) preferentially deletes reads from the most abundant and shortest transcripts, introducing an expression- and length-dependent bias. This is the OPPOSITE of DNA-seq. Duplication rate is a DIAGNOSTIC ("low complexity / over-sequenced / low input"), never a remove step. The only correct way to remove RNA PCR duplicates is UMIs (read-qc/umi-processing); UMI-protocol RNA-seq (QuantSeq, 10x) inverts the rule.

Integrity bonus: RIN is an electrophoresis estimate measured BEFORE library prep; gene-body coverage and TIN are the post-hoc TRUTH measured from the aligned reads. Use DV200 (% fragments >200 nt), not RIN, for FFPE/archival. In a cohort with variable quality, regress medTIN out as a covariate rather than discarding samples.

## Tool Taxonomy

| Tool | Gene model | Role |
|------|-----------|------|
| RSeQC | BED12 | The script suite: infer_experiment, geneBody_coverage, read_distribution, tin, junction_saturation, read_duplication |
| Qualimap 2 | GTF | `qualimap rnaseq`: feature distribution + transcript 5'-3' profile + junctions in one HTML (bamqc is the generic, non-RNA mode) |
| RNA-SeQC 2 | COLLAPSED GTF | GTEx/TOPMed tool; scales to tens of thousands of samples; exonic/intronic/intergenic + rRNA rate + TPM |
| Picard CollectRnaSeqMetrics | refFlat + ribosomal_intervals | PCT_CODING/UTR/INTRONIC/INTERGENIC/RIBOSOMAL, MEDIAN_5PRIME_TO_3PRIME_BIAS (cannot compute rRNA without the intervals) |
| SortMeRNA | rRNA database | Filter/quantify rRNA reads directly |

QC-gate order: (1) FastQC on raw FASTQ -> (2) align (STAR/HISAT2) -> (3) post-alignment QC: strandedness FIRST (it gates correct quantification), then read distribution, gene-body + TIN, rRNA/globin/MT, duplication + saturation -> (4) aggregate with MultiQC and judge each sample against the cohort.

## Strandedness -- infer, then set every tool to match

```bash
infer_experiment.py -i aligned.bam -r genes.bed12     # samples reads, reports the two fractions
salmon quant -i index -l A -r sample.fq.gz -o quant/  # -l A auto-detects; see lib_format_counts.json
```

| Protocol | infer_experiment dominant fraction | salmon -l (PE/SE) | featureCounts -s | htseq | STAR ReadsPerGene col |
|----------|------------------------------------|-------------------|------------------|-------|-----------------------|
| Unstranded | both ~0.5 | IU / U | 0 | no | 2 |
| fr-secondstrand (forward) | "1++,1--,2+-,2-+" | ISF / SF | 1 | yes | 3 |
| fr-firststrand (reverse, dUTP -- common) | "1+-,1-+,2++,2--" | ISR / SR | 2 | reverse | 4 |

Single-end infer_experiment drops the read-number prefix: forward = "++,--", reverse = "+-,-+". A STAR sanity check: the ReadsPerGene column with the most counts and fewest N_noFeature is the correct strand (the wrong column makes N_noFeature blow up). Picard STRAND_SPECIFICITY is a notorious inversion: NONE / FIRST_READ_TRANSCRIPTION_STRAND (= forward/fr-secondstrand) / SECOND_READ_TRANSCRIPTION_STRAND (= dUTP/reverse/fr-firststrand, the common case).

## Gene-body coverage and integrity

```bash
geneBody_coverage.py -i aligned.bam -r genes.bed12 -o coverage   # 5'->3' uniformity curve
tin.py -i aligned.bam -r genes.bed12 > tin.txt                   # per-transcript integrity; medTIN = sample score
```

3' bias (coverage piling at the 3' end) = RNA degradation OR oligo-dT priming of degraded/FFPE RNA -- which is why poly-A protocols fail on FFPE and rRNA-depletion + random priming is preferred there. 5' bias is rarer (5'-capture protocols / artifacts). Flat = intact RNA. RIN/DV200/TIN: RIN (1-10, pre-prep, electrophoresis) predicts degradation; DV200 (% >200 nt) is the FFPE metric because fragmented RNA has no rRNA peaks for RIN; TIN is measured from the data and can be used as a DE covariate.

## Read distribution and enrichment

```bash
read_distribution.py -i aligned.bam -r genes.bed12 > distribution.txt
```

- High INTRONIC = pre-mRNA / nuclear RNA or gDNA contamination (in snRNA-seq it is SIGNAL, not a fail).
- High INTERGENIC = gDNA contamination or annotation gaps. gDNA drives intronic AND intergenic up together; an annotation gap drives only intergenic.
- rRNA rate = the readout of poly-A-selection / rRNA-depletion efficiency (high = wasted reads, failed depletion).
- Globin (HBA/HBB) crowds whole-blood PAXgene libraries -- deplete (GLOBINclear); globin% is the readout.
- Mitochondrial %: high = degradation (bulk) or dying cells / ambient contamination (single-cell; in snRNA-seq it should be LOW).

## Duplication and saturation -- diagnostic, not a remove step

```bash
# Duplication as a DIAGNOSTIC only -- do NOT remove duplicates in non-UMI bulk RNA-seq
read_duplication.py -i aligned.bam -o dup                         # sequence- and mapping-based curves
junction_saturation.py -i aligned.bam -r genes.bed12 -o junc_sat  # enough depth for splicing?
```

## Complete QC pipeline

**Goal:** Produce a per-sample RNA-seq QC summary covering strandedness, distribution, integrity, and Picard metrics.

**Approach:** Infer strandedness first, run the RSeQC suite, then Picard with STRAND_SPECIFICITY set to the inferred protocol, and append to one report (do NOT dedup).

```bash
#!/bin/bash
set -euo pipefail
SAMPLE=$1; BAM=$2; BED12=$3; REFFLAT=$4; RRNA_INTERVALS=$5
STRAND=${6:-SECOND_READ_TRANSCRIPTION_STRAND}   # SECOND = dUTP/reverse (common); FIRST = forward; NONE = unstranded

REPORT="${SAMPLE}_rnaseq_qc.txt"
echo "=== RNA-seq QC: $SAMPLE ===" > "$REPORT"

echo "--- Strandedness (set downstream tools to match) ---" >> "$REPORT"
infer_experiment.py -i "$BAM" -r "$BED12" >> "$REPORT"

echo "--- Read distribution ---" >> "$REPORT"
read_distribution.py -i "$BAM" -r "$BED12" >> "$REPORT"

geneBody_coverage.py -i "$BAM" -r "$BED12" -o "${SAMPLE}_genebody"
tin.py -i "$BAM" -r "$BED12"                       # writes <bam>.summary.txt (mean/median TIN) + <bam>.tin.xls
echo "--- TIN (medTIN = median column of the summary) ---" >> "$REPORT"
cat *.summary.txt >> "$REPORT" 2>/dev/null

echo "--- Picard RNA-seq metrics (STRAND=$STRAND) ---" >> "$REPORT"
picard CollectRnaSeqMetrics I="$BAM" O="${SAMPLE}_picard.txt" \
    REF_FLAT="$REFFLAT" STRAND_SPECIFICITY="$STRAND" RIBOSOMAL_INTERVALS="$RRNA_INTERVALS"

cat "$REPORT"
```

## The collapsed gene model

A standard GTF lists many overlapping isoforms per gene, so a read that is exonic in isoform A but intronic in B is ambiguous and overlapping isoforms double-count the same base. RNA-SeQC 2 REQUIRES a COLLAPSED model (one flattened transcript per gene, inter-gene overlaps excluded), built with GTEx `collapse_annotation.py`. Mismatched or un-collapsed models are a leading cause of "my exonic rate looks wrong". Picard `PCT_*` metrics are FRACTIONS (0-1), not percentages, despite the name.

## Quantitative Thresholds

| Metric | Anchor | Source / rationale |
|--------|--------|--------------------|
| Mapping rate | > 0.2 exclude below (GTEx); > 85% typical | GTEx v8 RNA-SeQC gate |
| Intergenic rate | < 0.3 | GTEx; above = gDNA / annotation |
| rRNA rate | < 0.3 (GTEx); <5% polyA, <10% depleted in practice | depletion efficiency |
| Uniquely mapped reads | >= 30M (ENCODE human) | ENCODE long-RNA standard |
| medTIN | > 70 good, 50-70 moderate, < 50 poor | RSeQC TIN |
| 5'-to-3' bias | near 1 flat; > 2 strong degradation | Picard MEDIAN_5PRIME_TO_3PRIME_BIAS |

Thresholds are protocol-specific: an intronic rate that fails a poly-A bulk sample is normal/required for snRNA-seq (nuclei are >50% intronic); a 3' bias that condemns fresh poly-A is expected for FFPE. Apply cohort-relative outlier logic on top.

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| Counts ~halved / huge "no feature" fraction | Wrong strandedness | Infer first; set featureCounts/htseq/salmon/Picard to match |
| RNA-seq DE has odd length bias | Marked duplicates on non-UMI bulk RNA-seq | Do not dedup; report duplication as a diagnostic |
| Exonic rate looks wrong in RNA-SeQC | Un-collapsed multi-isoform GTF | Use a collapsed GTF (GTEx collapse_annotation.py) |
| Picard rRNA metric is 0/blank | No ribosomal_intervals supplied | Build the interval list from rRNA features + BAM dict |
| snRNA-seq "fails" high intronic rate | Bulk gate applied to nuclear RNA | Intronic reads are signal in snRNA; use an intron-inclusive reference |
| Picard percentages look 100x too small | PCT_* are fractions (0-1) | Multiply by 100 for display |

## References

Wang L, Wang S, Li W. 2012. RSeQC: quality control of RNA-seq experiments. Bioinformatics 28(16):2184-2185.
Okonechnikov K, Conesa A, Garcia-Alcalde F. 2016. Qualimap 2: advanced multi-sample quality control for high-throughput sequencing data. Bioinformatics 32(2):292-294.
Graubert A, Aguet F, Ravi A, Ardlie KG, Getz G. 2021. RNA-SeQC 2: efficient RNA-seq quality control and quantification for large cohorts. Bioinformatics 37(18):3048-3050.
Schroeder A, Mueller O, Stocker S, et al. 2006. The RIN: an RNA integrity number for assigning integrity values to RNA measurements. BMC Molecular Biology 7:3.
Wang L, Nie J, Sicotte H, et al. 2016. Measure transcript integrity using RNA-seq data. BMC Bioinformatics 17:58.
Smith T, Heger A, Sudbery I. 2017. UMI-tools: modeling sequencing errors in Unique Molecular Identifiers to improve quantification accuracy. Genome Research 27(3):491-499.

## Related Skills

read-qc/quality-reports - Raw-FASTQ QC before alignment
read-qc/umi-processing - Molecule-accurate dedup for UMI RNA-seq
read-qc/contamination-screening - rRNA and cross-species contamination
read-alignment/star-alignment - Aligner that emits ReadsPerGene strandedness columns
rna-quantification/featurecounts-counting - Strand-aware quantification after QC
differential-expression/deseq2-basics - Use medTIN as a covariate in the design
<!-- END FILE: read-qc/rnaseq-qc/SKILL.md -->

## 子目录：read-qc/umi-processing

<!-- BEGIN FILE: read-qc/umi-processing/SKILL.md -->
---
name: bio-read-qc-umi-processing
description: Extracts UMIs and collapses reads to original molecules with umi_tools (directional dedup) or builds error-corrected single-strand/duplex consensus reads with fgbio. Use when the library has UMIs and accurate molecule counting or below-sequencer-floor error correction is needed - single-cell, low-input RNA-seq, targeted panels, and ctDNA/liquid-biopsy rare-variant detection. For UMI extraction during QC use fastp-workflow; do not dedup non-UMI bulk RNA-seq.
tool_type: cli
primary_tool: umi_tools
---

## Version Compatibility

Reference examples tested with: umi_tools 1.1+, fgbio 2.1+, samtools 1.19+, STAR 2.7+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# UMI Processing -- count original molecules, or build a consensus below the error floor

Collapse PCR/optical duplicates by (coordinate + UMI) with umi_tools, or call error-corrected consensus reads with fgbio.

**"Deduplicate reads using UMIs"** -> Extract the UMI before alignment, then group reads by UMI + mapping position after alignment to count original molecules.
- CLI: `umi_tools extract` -> align -> `umi_tools dedup` (molecule counting)
- CLI: `fgbio GroupReadsByUmi` -> `fgbio CallMolecularConsensusReads`/`CallDuplexConsensusReads` (error correction)

Scope: this skill OWNS UMI extraction, dedup, and consensus calling. UMI extraction during QC -> read-qc/fastp-workflow. Single-cell matrices -> single-cell/preprocessing. Non-UMI DNA coordinate dedup -> alignment-files/duplicate-handling. OUT OF SCOPE: non-UMI bulk RNA-seq (do NOT dedup it -- read-qc/rnaseq-qc).

## The Single Most Important Modern Insight

1. **UMIs resolve the PCR-vs-biological duplicate confound that coordinates alone cannot, by collapsing on (coordinate + UMI) instead of coordinate -- and this forces a hard pipeline order: extract UMI on the FASTQ, align, THEN dedup.** Two reads at the same coordinate are the same molecule only if they also share a UMI; two independent molecules at one coordinate carry different UMIs. The confound dominates at high coverage, high expression, amplicon (every molecule shares the same primer-defined ends), and low input. Dedup cannot run before alignment because duplicate identity needs mapping COORDINATES; and `extract` must run before alignment so the aligner does not try to map the UMI bases as genomic sequence (extract moves the UMI into the read name / RX tag).

2. **umi_tools' DIRECTIONAL method (default) folds UMI errors back into their parent via a count-gradient rule; naive exact-UMI collapse OVER-counts.** Sequencing/PCR errors inside the UMI mutate a true UMI into a 1-off neighbor that looks like a new molecule. Directional builds a directed graph where an edge a->b exists when they are within edit distance 1 AND n_a >= 2*n_b - 1 (the parent is at least ~twice the error child, because errors are rarer than originals), then collapses each network to one molecule. This is why directional beats `cluster` (single-linkage over-merges, under-counts) and `unique` (no error model, over-counts).

3. **UMI-tools COUNTS molecules; fgbio builds a CONSENSUS read to push the error rate BELOW the sequencer floor -- and only DUPLEX consensus reaches the ctDNA/MRD floor.** Single-strand consensus (CallMolecularConsensusReads) votes within one strand's family and roughly halves errors, but cannot catch a lesion fixed into the molecule before the first copy (oxidative 8-oxo-G, C>T deamination). Duplex consensus (CallDuplexConsensusReads) keeps a base only where BOTH original strands agree -- a real mutation is on both strands, an artifact almost never -- reaching <1e-7 error for sub-0.1% VAF detection, at the cost of ~2x raw reads (families missing one strand are discarded).

Bridges: do NOT dedup non-UMI bulk RNA-seq (high-expression genes make genuine duplicate coordinates; read-qc/rnaseq-qc). CellRanger/STARsolo ALREADY UMI-collapse and emit a final matrix -- do not re-dedup their output. Deep amplicon needs LONGER UMIs because every molecule shares coordinates, so the UMI alone must separate them (4^L space; collisions under-count).

## Tool Taxonomy

| Tool / command | Role | When |
|----------------|------|------|
| umi_tools extract | Move UMI from read into the header (FASTQ stage) | Inline UMIs before alignment |
| umi_tools dedup | Collapse to one read per (coord + UMI) via directional | Molecule counting (bulk, targeted) |
| umi_tools count | Emit a gene x cell molecule matrix | Single-cell from a tagged raw BAM |
| umi_tools group | Tag reads with UG (group id) + BX (representative UMI), no dedup | Inspect grouping / feed consensus |
| fgbio GroupReadsByUmi | Group reads into source-molecule families (MI tag) | First step of consensus calling |
| fgbio CallMolecularConsensusReads | Single-strand consensus | Moderate-VAF error correction |
| fgbio CallDuplexConsensusReads | Duplex consensus (both strands agree) | ctDNA / MRD sub-0.1% VAF |
| fgbio FilterConsensusReads | Filter/mask untrustworthy consensus bases | Mandatory after consensus calling |
| fastp --umi | Extract only (no dedup) | UMI extraction folded into QC (route OUT) |

## Decision Tree by Scenario

| Goal | Use | Why |
|------|-----|-----|
| Count molecules (bulk/targeted RNA or DNA) | umi_tools dedup --method directional | Models UMI errors; the standard |
| Single-cell molecule matrix | umi_tools count (tagged raw BAM) or the aligner's own collapse | per-cell + per-gene |
| Already have a CellRanger/STARsolo matrix | nothing | It is already UMI-deduplicated |
| Moderate-VAF somatic error correction | fgbio single-strand consensus | Halves errors |
| ctDNA / MRD sub-0.1% VAF | fgbio duplex consensus + FilterConsensusReads | Below the single-strand floor |
| Non-UMI bulk RNA-seq | do NOT dedup | Duplicate coordinates are biological |

Default when uncertain: umi_tools directional dedup for counting; fgbio duplex for ctDNA.

## Extraction (FASTQ stage, before alignment)

`--bc-pattern` alphabet (string method): N = UMI base (extracted to the read name), C = cell barcode (extracted), X = a fixed/known base REATTACHED to the read (not discarded). True discard uses the regex method's `(?P<discard_N>...)` group, shown below.

```bash
# Inline 8 nt UMI at the start of R1
umi_tools extract --stdin=R1.fq.gz --read2-in=R2.fq.gz \
    --stdout=R1_umi.fq.gz --read2-out=R2_umi.fq.gz --bc-pattern=NNNNNNNN

# 10x 3' v3: 16 nt cell barcode + 12 nt UMI on R1
umi_tools extract --stdin=R1.fq.gz --read2-in=R2.fq.gz \
    --stdout=R1_umi.fq.gz --read2-out=R2_umi.fq.gz \
    --bc-pattern=CCCCCCCCCCCCCCCCNNNNNNNNNNNN

# Variable-position UMI with an anchor (regex method)
umi_tools extract --extract-method=regex --stdin=R1.fq.gz --stdout=R1_umi.fq.gz \
    --bc-pattern='(?P<umi_1>.{8})ATGC(?P<discard_1>.{4})'

# fgbio reads structure (M=UMI, T=template, C=cell, B=sample barcode, S=skip)
fgbio FastqToBam --input R1.fq.gz R2.fq.gz --read-structures 8M+T +T \
    --sample S1 --library L1 --output unmapped.bam      # UMI -> RX tag
```

## umi_tools dedup (molecule counting)

```bash
samtools sort -o sorted.bam aligned.bam && samtools index sorted.bam

# Directional (default), paired, with the diagnostic edit-distance stats
umi_tools dedup -I sorted.bam -S dedup.bam --paired --output-stats=stats

# Single-cell from a RAW aligned BAM whose CB/UB are in tags (NOT a CellRanger BAM)
umi_tools count -I tagged.bam -S counts.tsv \
    --per-gene --gene-tag=XT --per-cell --cell-tag=CB \
    --umi-tag=UB --extract-umi-method=tag
```

| Method | Behavior | Verdict |
|--------|----------|---------|
| directional (default) | Count-gradient graph (n_a >= 2n_b-1); folds UMI errors into parent | Best; the default |
| adjacency | Resolve each component by abundance, one edge out | Reasonable |
| cluster | One molecule per connected component (single-linkage) | Over-merges, under-counts |
| unique | Exact UMI only, no error model | Over-counts; only PCR-free/high-diversity |
| percentile | Drop UMIs below 1% of mean count | Crude denoiser |

`--edit-distance-threshold` default 1; `--output-stats` writes the edit-distance file (observed-vs-null confirms UMI errors were collapsed); `umi_tools group --output-bam` writes UG + BX tags without deduplicating.

## fgbio consensus (error correction)

```bash
# Group reads into source-molecule families (writes MI tag from raw RX)
fgbio GroupReadsByUmi --input mapped.bam --output grouped.bam --strategy adjacency --edits 1

# Single-strand consensus (--min-reads required; raise to >=2-3 when error correction matters)
fgbio CallMolecularConsensusReads --input grouped.bam --output consensus.bam --min-reads 3

# Duplex consensus for ctDNA: group with the paired strategy, then call duplex
fgbio GroupReadsByUmi --input mapped.bam --output grouped.bam --strategy paired --edits 1
fgbio CallDuplexConsensusReads --input grouped.bam --output duplex.bam --min-reads 2 1 1

# Mandatory final step: filter/mask untrustworthy consensus bases
fgbio FilterConsensusReads --input duplex.bam --output filtered.bam --ref ref.fa \
    --min-reads 2 1 1 --max-base-error-rate 0.1 --min-base-quality 40 --max-no-calls 0.2
```

GroupReadsByUmi `--strategy`: identity (exact), edit (cluster by edits), adjacency (umi_tools directional port), paired (DUPLEX -- a read with UMI A-B is the opposite strand of one with B-A, tagged MI .../A and .../B). The consensus pipeline aligns, groups, calls consensus, then RE-aligns the consensus reads (the sequence changed). RX = raw UMI, MI = molecular id (SAM tags).

## Saturation and collision

A fully-random L-mer UMI has 4^L sequences (L=8 -> 65,536; L=12 -> ~16.8M). When the molecules at a locus approach the usable space, independent molecules COLLIDE on the same UMI and are under-counted. For bulk/RNA the key is coordinate+UMI, so the space is 4^L per coordinate and collisions are rare; for AMPLICON every molecule shares coordinates, so the UMI alone separates them and deep panels need longer UMIs (AmpUMI sizes this). UMIs do NOT fix capture/ligation bias upstream of tagging, errors before UMI attachment (only duplex does), or low library complexity.

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| Re-running dedup on CellRanger output | CellRanger/STARsolo already UMI-collapse | Use their matrix as-is; do not re-dedup |
| Deduped a non-UMI bulk RNA-seq BAM | Coordinate dups are biological there | Do not dedup; report duplication as a diagnostic |
| Molecule count too high | `--method unique` (no UMI error model) | Use directional (default) |
| Aligner soft-clips/mismaps the UMI | Dedup attempted before extract, or UMI left in read | extract first; UMI must leave the aligned sequence |
| Amplicon molecules under-counted | UMI too short -> collisions at shared coordinates | Use a longer UMI; size with AmpUMI |
| Duplex yields few consensus reads | Many families missing one strand | Expected; duplex needs ~2x raw reads |
| Consensus BAM still noisy | Skipped FilterConsensusReads | Always filter/mask after calling consensus |

## References

Smith T, Heger A, Sudbery I. 2017. UMI-tools: modeling sequencing errors in Unique Molecular Identifiers to improve quantification accuracy. Genome Research 27(3):491-499.
Liu D. 2019. Algorithms for efficiently collapsing reads with Unique Molecular Identifiers. PeerJ 7:e8275.
Islam S, Zeisel A, Joost S, et al. 2014. Quantitative single-cell RNA-seq with unique molecular identifiers. Nature Methods 11(2):163-166.
Schmitt MW, Kennedy SR, Salk JJ, et al. 2012. Detection of ultra-rare mutations by next-generation sequencing. PNAS 109(36):14508-14513.
Kennedy SR, Schmitt MW, Fox EJ, et al. 2014. Detecting ultralow-frequency mutations by Duplex Sequencing. Nature Protocols 9(11):2586-2606.
Clement K, Farouni R, Bauer DE, Pinello L. 2018. AmpUMI: design and analysis of unique molecular identifiers for deep amplicon sequencing. Bioinformatics 34(13):i202-i210.

## Related Skills

read-qc/fastp-workflow - UMI extraction folded into preprocessing
read-qc/rnaseq-qc - Why non-UMI bulk RNA-seq must NOT be deduplicated
alignment-files/duplicate-handling - Coordinate dedup for non-UMI DNA
single-cell/preprocessing - scRNA-seq UMI matrices and downstream
liquid-biopsy/ctdna-mutation-detection - Duplex consensus for rare-variant detection
<!-- END FILE: read-qc/umi-processing/SKILL.md -->

<!-- END CATEGORY: read-qc -->

