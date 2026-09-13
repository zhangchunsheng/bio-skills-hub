---
slug: bio-metagenomics-integrated
version: 1.0.1
displayName: "宏基因组学 / Metagenomics analysis"
name: bio-metagenomics-integrated
summary: "中文：宏基因组学综合技能，整合 8 个相关专题，覆盖宏基因组分析：Kraken2/MetaPhlAn分类、HUMAnN功能分析、耐药基因检测、菌株追踪。 English: Integrated Metagenomics analysis skill covering 8 related topics, including Metagenomics analysis: Kraken2/MetaPhlAn classification, HUMAnN functional profiling, AMR gene detection, strain tracking."
description: "中文：这是一个面向宏基因组学的综合生物信息学 Skill，整合当前分类下 8 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：宏基因组分析：Kraken2/MetaPhlAn分类、HUMAnN功能分析、耐药基因检测、菌株追踪。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：AMRFinderPlus, Bracken, HUMAnN。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Metagenomics analysis, combining 8 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Metagenomics analysis: Kraken2/MetaPhlAn classification, HUMAnN functional profiling, AMR gene detection, strain tracking. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: AMRFinderPlus, Bracken, HUMAnN. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# metagenomics 分类 Skill 整合版

> 本文件整合同一主分类目录下 8 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: metagenomics -->

## 子目录：metagenomics/abundance-estimation

<!-- BEGIN FILE: metagenomics/abundance-estimation/SKILL.md -->
---
name: bio-metagenomics-abundance
description: Turns shotgun classifier output into a defensible abundance table with Bracken Bayesian re-estimation, then compositional treatment (CLR, zero handling), library-size normalization, reference-frame differential abundance, and optional absolute quantification. Covers why a relative-abundance change is not a change, why Bracken read fractions and MetaPhlAn percentages are different physical quantities, the silent -r read-length bias, the genome-size confound no library-size method fixes, and the rarefaction debate. Use when estimating species abundance from a Kraken2 report, normalizing a community count table, choosing a compositional transform, or converting relative to absolute load. For classification see kraken-classification; for diversity/ordination/DA mechanics see metagenome-visualization.
tool_type: mixed
primary_tool: Bracken
---

## Version Compatibility

Reference examples tested with: Bracken 2.9+, Kraken2 2.1.3+, pandas 2.2+, scikit-bio 0.6+, R zCompositions 1.5+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `bracken -h`, `bracken-build -h` to confirm flags and defaults
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('zCompositions')` then `?cmultRepl` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The Bracken `databaseRLENmers.kmer_distrib` is built per database at a fixed read length and MUST match both the Kraken2 database and the actual (post-trim) read length; `-r` is not auto-detected and a mismatch silently biases every species fraction. Bracken needs the default Kraken2 report format, not mpa-style.

# Abundance Estimation

**"How much of each taxon is in my sample?"** -> Re-estimate species reads with Bracken, then treat the table as a composition - because the sequencer fixed the total, so the numbers are relative and a change in one forces apparent changes in the rest.
- CLI: `bracken -d DB -i kraken.kreport -o out.bracken -w out.bracken.kreport -r 150 -l S -t 10`

Scope: Bracken mechanics plus what happens to the numbers afterward - estimand choice, compositional transforms, normalization, reference-frame DA logic, absolute conversion. Read classification -> kraken-classification, metaphlan-profiling. Diversity/ordination/DA tool mechanics -> metagenome-visualization. Generic 16S diversity -> the microbiome category.

## The Single Most Important Modern Insight -- A Relative-Abundance Change Is Not a Change

A shotgun abundance table is a composition: the sequencer fixes the total number of reads, not the sample's microbial load. So every number is relative to every other, and "taxon X went up 2-fold" is undefined without a reference frame or an external load anchor. Without one, a single blooming taxon makes every other taxon look depleted (the blooming-taxon illusion), and a Pearson correlation of two taxa's proportions is biased negative by arithmetic, not biology. Bracken is step one of about six: classify -> re-estimate -> compositional transform -> normalize -> reference-frame test -> (optional) absolute conversion. Two corollaries:

1. **Bracken percent and MetaPhlAn percent are different physical quantities.** Bracken is a fraction of READS (large-genome biased, approximately fraction of DNA); MetaPhlAn is a genome-size-normalized marker abundance (approximately fraction of cells). They legitimately disagree 2-3x for the same sample. Picking one chooses an estimand (DNA vs cells), not the "more accurate tool."
2. **No library-size normalizer fixes the genome-size confound.** TSS/CSS/TMM/GMPR all operate on the count table and inherit the large-genome bias; only a coverage-based estimand (CoverM) or a genome-normalized profiler (MetaPhlAn) removes it.

## What Quantity Is Being Estimated?

| Estimand | Definition | Bias / use |
|----------|------------|-----------|
| Read count | raw reads to a taxon | library-size and genome-size dependent; never compare raw across samples |
| Relative abundance | read count / total | compositional (sums to 1); still genome-size biased |
| Coverage abundance | reads x readlen / genome size | removes large-genome bias; ~ fraction of genomes/cells (CoverM) |
| Cell fraction | fraction of organisms | needs coverage + an assumption of one genome per cell; polyploidy/growth bias it |
| Absolute load | composition x external total | the only basis for "increased/decreased" (flow/qPCR/spike-in) |

## Bracken: Step One, Not the Finish Line

Bracken redistributes reads stranded at the genus/family node (where shared k-mers stopped Kraken) down to species, using a database-derived expectation of where length-L reads classify. It does not classify and it does not add precision.

```bash
bracken-build -d "$KRAKEN_DB" -t 8 -k 35 -l 150   # one-time; -k MUST equal the Kraken2 build k (35)
bracken -d "$KRAKEN_DB" -i kraken.kreport -o out.bracken -w out.bracken.kreport \
    -r 150 \   # MUST equal the bracken-build -l AND the actual post-trim read length (not auto-detected)
    -l S -t 10 # species level; -t drops taxa with fewer than 10 clade-level reads (strict <) before redistribution
```

Output columns: `name, taxonomy_id, taxonomy_lvl, kraken_assigned_reads, added_reads, new_est_reads, fraction_total_reads`. `fraction_total_reads` is a fraction of classified-and-retained reads, not of all input - so two samples with different unclassified (e.g. host) fractions have non-comparable denominators. `combine_bracken_outputs.py --files *.bracken -o matrix.tsv` builds a taxa-by-sample matrix.

### Bracken's defining failure mode
Bracken can only redistribute among species already in the database. A true organism absent from the database has its reads parked by Kraken at the shared genus node, and Bracken hands them to the database-present congeners - confidently fabricating or inflating those species. Distrust any species with high `added_reads` but tiny `kraken_assigned_reads`; gate presence on upstream unique-minimizer evidence (kraken-classification) and a coverage breadth check.

## Treat the Table as a Composition

**Goal:** Make the abundance table valid for multivariate stats and correlation by removing closure with a centered log-ratio, after handling zeros (log of zero is undefined).

**Approach:** Impute count zeros with Bayesian-multiplicative replacement (preserves ratios), then CLR-transform; use Aitchison distance (Euclidean on CLR) downstream, never raw-proportion Pearson or Bray-Curtis for correlation.

```python
import pandas as pd
import numpy as np
from skbio.stats.composition import clr, multi_replace   # multiplicative_replacement was renamed multi_replace in skbio 0.6

counts = pd.read_csv('matrix.tsv', sep='\t', index_col=0)   # taxa x samples (new_est_reads)
mat = counts.T.values.astype(float)                          # samples x taxa for transform
mat_nozero = multi_replace(mat / mat.sum(axis=1, keepdims=True))
clr_mat = clr(mat_nozero)                                    # closure removed; rows are CLR coordinates
clr_df = pd.DataFrame(clr_mat, index=counts.columns, columns=counts.index)
```

For sparse tables prefer R `zCompositions::cmultRepl()` (Bayesian-multiplicative, posterior-imputed) over a fixed +1 pseudocount, which is arbitrary, distorts ratios, and re-opens closure. Structural zeros (taxon genuinely absent) and sampling zeros (present below detection) are usually indistinguishable from the table - disclose the assumption rather than pretend otherwise.

## Library-Size Normalization

| Method | What it does | Shotgun applicability |
|--------|--------------|-----------------------|
| TSS (proportions) | divide by library size | IS the compositional closure; fine for viz, biased for DA/correlation |
| Rarefaction | subsample to common depth | discards data; defensible for diversity, contested for DA (see below) |
| CSS (metagenomeSeq) | scale by a cumulative-sum quantile | robust to dominant taxa; designed for marker surveys, usable on counts |
| TMM (edgeR) | trimmed mean of M-values | "most features unchanged" often violated in microbiome; use with caution |
| RLE (DESeq median-of-ratios) | geometric-mean reference | breaks on zeros (geometric mean -> 0); needs poscounts workaround |
| GMPR | pairwise median ratios then geometric-mean | purpose-built for zero-inflated counts; good default size factor |

None of these fixes the genome-size confound - that needs a coverage estimand or a genome-normalized profiler.

### The rarefaction debate (do not take a side; decide per analysis)
McMurdie & Holmes 2014 (*PLoS Comput Biol* 10:e1003531) showed rarefying for DIFFERENTIAL ABUNDANCE is statistically wasteful versus modeling library size. Schloss 2024 (*mSphere* 9:e00354-23 and the companion e00355-23) argues rarefaction is currently the best control of uneven effort for RICHNESS and COMMUNITY-DISTANCE analyses, where scaling alone does not remove the depth effect. They concern different downstream analyses: for DA do not rarefy (use a CoDA/reference-frame method or a modeled size factor); for alpha/beta diversity rarefaction is defensible. Treating "rarefy: yes/no" as one global switch is the mistake.

## Reference-Frame Differential Abundance (logic here; mechanics in metagenome-visualization)

"Taxon X increased" needs a reference frame because the total is fixed. Methods differ chiefly by their implicit frame: total-sum (naive, wrong), the geometric mean of all taxa (CLR / ALDEx2), or an estimated per-sample sampling fraction (ANCOM-BC). ALDEx2 (Fernandes 2014 *Microbiome* 2:15) Monte-Carlo samples a Dirichlet posterior, CLR-transforms, and tests each draw; ANCOM-BC (Lin & Peddada 2020 *Nat Commun* 11:3514) estimates and corrects each sample's sampling fraction. Do not run naive t-tests or Wilcoxon on TSS proportions. Run the tools and read their output in metagenome-visualization.

## Absolute Quantification: the Only Basis for "Increased/Decreased"

Relative methods recover the composition; absolute load = composition x an external total. Anchors: flow-cytometry cell counts (QMP, Vandeputte 2017 *Nature* 551:507, which showed apparent Crohn's "increases" were a microbial-load artifact - the absolute trajectory was opposite); per-taxon flow density (Props 2017 *ISME J* 11:584); a known spike-in organism added before extraction (SCML, Stammler 2016 *Microbiome* 4:28; a cellular spike also captures extraction bias a DNA spike misses); or total 16S qPCR copies (cheap, copy-number biased). Any "X increased" claim without an anchor or a reference-frame method is unsupported.

## Per-Method Failure Modes

### Bracken `-r` read-length mismatch
**Trigger:** `-r 150` on trimmed ~120 bp reads, or a database built only for a different length. **Mechanism:** the redistribution prior is fragment-length specific and not auto-detected. **Symptom:** biased species fractions with no error if the `.kmer_distrib` exists, hard crash if not. **Fix:** `-r` = actual post-trim read length and a matching built distribution.

### Pearson/Bray-Curtis on proportions
**Trigger:** correlating two taxa's relative abundances, or Bray-Curtis distance for a "who-co-occurs" claim. **Mechanism:** closure biases proportion correlations negative and makes Euclidean/Bray-Curtis sub-compositionally incoherent. **Symptom:** spurious negative interactions; unstable clustering. **Fix:** CLR + Aitchison distance, or SparCC/proportionality for co-occurrence.

### Relative fold-change reported as absolute
**Trigger:** "taxon X doubled" from a relative table. **Mechanism:** one bloom deflates every other proportion. **Symptom:** whole-community "depletion" that is really one taxon rising. **Fix:** anchor to load (flow/qPCR/spike-in) or use ANCOM-BC; state which frame.

### RLE/DESeq on a sparse table
**Trigger:** DESeq2/edgeR median-of-ratios on a species count table. **Mechanism:** the geometric-mean reference collapses to 0 when any feature has a zero. **Symptom:** degenerate size factors, errors, or nonsense fold-changes. **Fix:** GMPR or CSS; or DESeq2 with a poscounts estimator.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Bracken `-k` = 35 | Lu 2017 *PeerJ Comput Sci* 3:e104 | must equal the Kraken2 database k-mer length |
| Bracken `-r` = post-trim read length | Bracken docs | redistribution prior is fragment-length specific; silent bias otherwise |
| Bracken `-t` 10 default | Bracken docs | redistribution floor; raise to suppress noise, too high deletes real rare taxa |
| Multiplicative/Bayesian zero replacement over +1 | Martin-Fernandez 2015 *Stat Modelling* 15:134 | preserves ratios; fixed pseudocount distorts them and re-opens closure |
| Rarefy for diversity, not for DA | McMurdie 2014; Schloss 2024 *mSphere* 9:e00354-23 | decision is per-analysis, not global |
| Coverage breadth (`covered_fraction`) presence gate | Aroney 2025 *Bioinformatics* 41:btaf147 | high mean coverage over a few % of a genome is a conserved-region artifact |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "kmer_distrib not found" | `-r` has no matching built distribution | `bracken-build -l <readlen>` or pick a DB shipping it |
| Bracken rejects input | mpa-style or per-read file passed to `-i` | give the default Kraken2 `--report` |
| Species with huge added_reads, tiny assigned | redistribution into a DB-present relative of an absent taxon | gate presence on unique minimizers + coverage breadth |
| CLR returns -inf / NaN | zeros not replaced before log-ratio | multiplicative or `cmultRepl` replacement first |
| Cross-sample fractions not comparable | differing unclassified (host) fractions in the denominator | track classified fraction as a covariate; host-deplete upstream |
| MetaPhlAn and Bracken disagree | different estimands (cells vs reads) | do not merge; pick one estimand and state it |

## References

- Lu J, Breitwieser FP, Thielen P, Salzberg SL. 2017. Bracken: estimating species abundance in metagenomics data. *PeerJ Comput Sci* 3:e104.
- Gloor GB, Macklaim JM, Pawlowsky-Glahn V, Egozcue JJ. 2017. Microbiome datasets are compositional: and this is not optional. *Front Microbiol* 8:2224.
- Quinn TP, Erb I, Richardson MF, Crowley TM. 2018. Understanding sequencing data as compositions: an outlook and review. *Bioinformatics* 34:2870-2878.
- Fernandes AD, Reid JN, Macklaim JM, et al. 2014. Unifying the analysis of high-throughput sequencing datasets. *Microbiome* 2:15.
- Lin H, Peddada SD. 2020. Analysis of compositions of microbiomes with bias correction. *Nat Commun* 11:3514.
- Martin-Fernandez JA, Hron K, Templ M, Filzmoser P, Palarea-Albaladejo J. 2015. Bayesian-multiplicative treatment of count zeros in compositional data sets. *Stat Modelling* 15:134-158.
- McMurdie PJ, Holmes S. 2014. Waste not, want not: why rarefying microbiome data is inadmissible. *PLoS Comput Biol* 10:e1003531.
- Schloss PD. 2024. Rarefaction is currently the best approach to control for uneven sequencing effort in amplicon sequence analyses. *mSphere* 9:e00354-23.
- Weiss S, Xu ZZ, Peddada S, et al. 2017. Normalization and microbial differential abundance strategies depend upon data characteristics. *Microbiome* 5:27.
- Chen L, Reeve J, Zhang L, et al. 2018. GMPR: a robust normalization method for zero-inflated count data. *PeerJ* 6:e4600.
- Vandeputte D, Kathagen G, D'hoe K, et al. 2017. Quantitative microbiome profiling links gut community variation to microbial load. *Nature* 551:507-511.
- Stammler F, Glasner J, Hiergeist A, et al. 2016. Adjusting microbiome profiles for differences in microbial load by spike-in bacteria. *Microbiome* 4:28.
- Aroney STN, Newell RJP, Nissen JN, Camargo AP, Tyson GW, Woodcroft BJ. 2025. CoverM: read alignment statistics for metagenomics. *Bioinformatics* 41:btaf147.

## Related Skills

- kraken-classification - Generates the Kraken2 report and owns the read-count-is-not-abundance reframe
- metaphlan-profiling - Genome-size-normalized cell-fraction abundance; a different estimand
- metagenome-visualization - Diversity, ordination, and differential-abundance tool mechanics
- contamination-controls - Host-fraction and blank handling that affect the denominator
- genome-assembly/metagenome-assembly - Coverage-based MAG abundance via read mapping
- workflows/metagenomics-pipeline - End-to-end profiling and abundance
<!-- END FILE: metagenomics/abundance-estimation/SKILL.md -->

## 子目录：metagenomics/amr-detection

<!-- BEGIN FILE: metagenomics/amr-detection/SKILL.md -->
---
name: bio-metagenomics-amr-detection
description: Profiles the antimicrobial-resistance gene content (resistome) of shotgun metagenomes - read-based quantification with RGI bwt, AMR++/MEGARes, ARGs-OAP/SARG, deepARG, or GROOT, and presence calling with AMRFinderPlus/ABRicate on assembled contigs or MAGs. Covers why an ARG hit is a sequence match not a phenotype, why a metagenomic ARG has no host and no genomic context until assembly (and assembly breaks at ARGs), per-gene curated thresholds vs a flat 80/80, gene-fraction false-positive control, and cross-study normalization pitfalls. Use when quantifying a community resistome, normalizing ARG abundance, or calling ARGs from metagenome contigs. For pure-culture isolate AMR, point mutations, and phenotype/MIC prediction see epidemiological-genomics/amr-surveillance.
tool_type: cli
primary_tool: AMRFinderPlus
---

## Version Compatibility

Reference examples tested with: AMRFinderPlus 3.12+, RGI 6+ (CARD 3.2+), ABRicate 1.0+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `amrfinder -V` (reports software AND database version), `rgi main --version`, `abricate --list` to confirm DB snapshots
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The AMR reference DATABASE is versioned and updated roughly monthly; `amrfinder -V` reports both software and database version, and ABRicate ships pinned database snapshots so two labs on different versions get different calls. Record the tool version, the database version, and (for read-based work) the normalization unit and sequencing depth - none are recoverable later.

# AMR Detection (Community Resistome)

**"What resistance genes are in my community, and how abundant?"** -> Match reads or contigs to a curated ARG database - reporting that ARG sequences are present at some relative abundance, never that the sample is resistant, because a metagenomic hit has no host and no expression.
- CLI (reads): `rgi bwt -1 R1.fq.gz -2 R2.fq.gz -a kma -n 16 -o sample --local`
- CLI (contigs/MAGs): `amrfinder -n contigs.fasta --plus -o amr.tsv`

Scope: community/metagenomic resistome - read-based quantification and contig/MAG presence calling. Pure-culture isolate AMR, point-mutation resistance, in-silico antibiogram, MLST/clone/outbreak context, and GLASS reporting -> epidemiological-genomics/amr-surveillance. Assembly/binning and ARG-host linkage mechanics -> genome-assembly/metagenome-assembly. General gene-family/pathway abundance -> functional-profiling.

## The Single Most Important Modern Insight -- An ARG Hit Is a Sequence Match, Not a Phenotype

An ARG hit is a match against a reference database, not a measured resistance phenotype - and in a metagenome it is a match with no host and no genomic context until assembly. Three inferences a naive pipeline silently makes, all wrong:

1. **match -> gene** - defeated by partial hits (a 30 bp conserved-domain hit to a 1 kb ARG is not a gene); guarded by gene-fraction / breadth-of-coverage.
2. **gene -> resistance** - defeated by expression and regulation: silent sul2 below ECOFF, ampC/blaOXA driven only when an IS lands in the promoter, efflux that needs overexpression, truncations that still score a partial hit, point mutations where only the SNP matters.
3. **gene -> who carries it / is it mobile** - defeated by read shortness: a short read cannot see its neighbors, so host and plasmid context need assembly, long reads, or Hi-C.

The honest deliverable is "these ARG sequences are present at this relative abundance in this community," never "this sample is resistant to drug X." The moment a report says resistant, it has smuggled in a host, an expression assumption, and a clinical breakpoint the data never contained. On a pure culture the organism can be grown and an MIC measured - that is a different skill (epidemiological-genomics/amr-surveillance).

## Read-Based vs Assembly-Based: the Core Metagenomic Tradeoff

| Axis | Read-based (RGI bwt, AMR++, ARGs-OAP, deepARG, GROOT) | Assembly-based (AMRFinderPlus/RGI main/ABRicate on contigs/MAGs) |
|------|---------------------------------|----------------------------|
| Low-abundance sensitivity | high - every read counts, below assembly coverage | low - ARGs at low coverage do not assemble |
| Quantification | yes - abundance + normalization | presence/absence per contig |
| Host / MGE context | none without binning | possible via contig taxonomy / MAG |
| Point-mutation resistance | weak/unreliable (RGI bwt cannot screen the SNP) | yes, with organism/model |
| False positives | partial hits unless gene-fraction filtered | chimeric contigs, but vettable |

The assembly paradox: metagenomic assemblies preferentially break exactly at ARG/MGE boundaries, recovering only a small fraction of true ARG genomic contexts and underestimating the resistome (Abramova 2024 *BMC Genomics* 25:959). So "assemble to get host" is necessary but not sufficient - long reads (Nanopore/PacBio) and Hi-C metagenomics are the real remedy for ARG-host/MGE linkage.

## Tool Taxonomy

| Tool | Citation | Role | When |
|------|----------|------|------|
| AMRFinderPlus | Feldgarden 2021 *Sci Rep* 11:12728 | NCBI Reference Gene Catalog; per-gene curated cutoffs + HMMs | contig/MAG presence calling; the default contig caller |
| RGI bwt | Alcock 2023 *Nucleic Acids Res* 51:D690 | CARD homolog-model read mapping (KMA/bowtie2/bwa) | read-based resistome with coverage/depth per allele |
| AMR++ / MEGARes 3.0 | Bonin & Doster 2023 *Nucleic Acids Res* 51:D744 | BWA-MEM + gene-fraction filter + rarefaction | quantitative resistome with built-in partial-hit control |
| ARGs-OAP / SARG | Yin 2023 *Engineering* 27:234 | two-stage read annotation + 16S/cell normalization | copies-ARG-per-16S / per-cell units |
| deepARG | Arango-Argoty 2018 *Microbiome* 6:23 | deep-NN over dissimilarity features | catches divergent ARGs best-hit BLAST misses |
| GROOT | Rowe & Winn 2018 *Bioinformatics* 34:3601 | variation-graph alignment | types SNP-bearing alleles that flat references conflate |
| ABRicate | Seemann (no paper) | flat 80/80 BLASTn, bundled DB snapshots | quick contig screen; acquired genes only, no point mutations |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Quantitative resistome from reads | RGI bwt or AMR++ or ARGs-OAP | abundance + normalization; no host/context |
| Divergent / novel ARGs from reads | deepARG (confirm surprising calls) | dissimilarity features beat top-hit BLAST |
| Type a specific high-similarity allele | GROOT | graph carries SNP-bearing variants |
| Presence per contig / MAG | AMRFinderPlus (`--plus`) on contigs | curated per-gene cutoffs; possible host via binning |
| Quick multi-DB contig screen | ABRicate | fast; but flat 80/80, no point mutations |
| Is the ARG mobile / in a pathogen? | assemble+bin, long read, or Hi-C | short reads cannot link ARG to host |
| Pure culture / phenotype / MIC | -> epidemiological-genomics/amr-surveillance | isolate AMR is a different skill |
| Cross-study abundance comparison | within-study only, same DB+normalization+depth | "total ARG abundance" is rarely comparable |

## Read-Based Resistome Quantification

```bash
# CARD read mapping (homolog models). RGI bwt CANNOT screen point-mutation SNPs, so this is for
# acquired/homolog ARGs only - never report a gyrA read hit as fluoroquinolone resistance.
rgi bwt -1 reads_R1.fq.gz -2 reads_R2.fq.gz \
    -a kma -n 16 \
    -o sample_resistome --local
# Outputs *.gene_mapping_data.txt with percent coverage and depth per gene.

# AMR++/MEGARes applies the gene-fraction filter (default 80%): the minimum proportion of a
# reference covered by >=1 read for "present" - the read-based analog of breadth-of-coverage.
```

ARGs-OAP/SARG normalizes to copies-of-ARG-per-16S or per-cell; report the unit. Gene fraction (breadth) is the single most important false-positive guard - without it a conserved-domain fragment counts as a present gene.

## Contig / MAG Presence Calling

```bash
amrfinder -n contigs.fasta \
    --plus \                  # also report biocide/metal (STRESS) and virulence elements
    --threads 8 -o amr.tsv
# --ident_min default -1 = use the per-gene CURATED cutoffs; overriding with a global value is usually a mistake.
# Point mutations require --organism (a single known species) - inappropriate for a mixed community;
# use it only on a taxonomically resolved MAG, and defer isolate point-mutation work to amr-surveillance.
```

AMRFinderPlus uses manually curated per-gene BLAST cutoffs (plus HMM cutoffs with protein), not a flat 80/80 - catching divergent real variants while rejecting partial housekeeping homologs. ABRicate, by contrast, is flat 80/80 and acquired-genes-only; it will never report a point mutation.

## Per-Method Failure Modes

### ARG presence reported as resistance
**Trigger:** an output column or summary that says "resistant." **Mechanism:** presence is not expression and not a host-linked MIC. **Symptom:** a sewage metagenome described as "resistant to carbapenems." **Fix:** report "ARG detected at abundance X"; reserve phenotype claims for isolates (amr-surveillance).

### `--organism` on a mixed community
**Trigger:** `amrfinder --organism Escherichia` on community contigs. **Mechanism:** organism mode assumes a single known species and calls organism-specific point mutations/intrinsic genes. **Symptom:** spurious point-mutation calls; filtered "intrinsic" genes wrong for the community. **Fix:** run organism mode only on a taxonomically resolved MAG; otherwise omit it.

### Partial hit counted as a gene
**Trigger:** read mapping or BLAST with no breadth filter. **Mechanism:** a short conserved-domain match to a long ARG passes an identity threshold. **Symptom:** inflated ARG counts dominated by fragments. **Fix:** require gene-fraction / breadth-of-coverage (AMR++ default 80%); inspect coverage, not just identity.

### Cross-study abundance comparison
**Trigger:** comparing "total ARG abundance" across papers. **Mechanism:** different databases (CARD/MEGARes/SARG/ResFinder), normalization units, aligners, and depth all change the number. **Symptom:** apparent resistome differences that are pipeline artifacts. **Fix:** compare only within a study with one pipeline; report DB version, tool version, normalization unit, and depth; hAMRonization harmonizes format, not the metric.

### Loose/Discovery hits reported as ARGs
**Trigger:** CARD-RGI `--include_loose` in a surveillance report. **Mechanism:** Loose is below the curated bit-score cutoff - discovery only. **Symptom:** a flood of low-similarity false positives. **Fix:** report Perfect/Strict; reserve Loose for novel-variant discovery with manual curation.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| AMRFinderPlus `--ident_min` -1 (use curated) | Feldgarden 2021 *Sci Rep* 11:12728 | per-gene curated cutoffs beat a global 80/80; overriding is usually wrong |
| AMRFinderPlus `--coverage_min` 0.5 | AMRFinderPlus docs | minimum reference coverage for a call |
| AMR++ gene fraction 80% | Bonin & Doster 2023 *Nucleic Acids Res* 51:D744 | breadth guard against partial-hit false positives |
| ResFinder acquired 0.80 id / 0.60 cov | Bortolaia 2020 *J Antimicrob Chemother* 75:3491 | the documented default (not 0.90) |
| deepARG `--min-prob` 0.8 | Arango-Argoty 2018 *Microbiome* 6:23 | category probability cutoff; confirm surprising calls |
| CARD Loose tier = discovery only | Alcock 2023 *Nucleic Acids Res* 51:D690 | below curated bit-score; not for surveillance |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| No point mutations reported | ABRicate or read-based homolog mapper used | those cannot call SNPs; use AMRFinderPlus `--organism` on a MAG / defer to amr-surveillance |
| AMRFinderPlus calls changed silently | stale reference database | `amrfinder -u`; record `amrfinder -V` software + DB version |
| ABRicate results differ between labs | pinned DB snapshot version differs | record `abricate --list` versions; update with abricate-get_db |
| Inflated ARG abundance | no gene-fraction/breadth filter | apply breadth-of-coverage; inspect coverage |
| gyrA "hit" from read-based RGI | `--include_other_models` reports the gene, not the SNP | do not call resistance; SNP screening needs an isolate/organism |

## References

- Feldgarden M, Brover V, Gonzalez-Escalona N, et al. 2021. AMRFinderPlus and the Reference Gene Catalog facilitate examination of the genomic links among antimicrobial resistance, stress response, and virulence. *Sci Rep* 11:12728.
- Alcock BP, Huynh W, Chalil R, et al. 2023. CARD 2023: expanded curation, support for machine learning, and resistome prediction at the Comprehensive Antibiotic Resistance Database. *Nucleic Acids Res* 51:D690-D699.
- Bortolaia V, Kaas RS, Ruppe E, et al. 2020. ResFinder 4.0 for predictions of phenotypes from genotypes. *J Antimicrob Chemother* 75:3491-3500.
- Bonin N, Doster E, Worley H, et al. 2023. MEGARes and AMR++, v3.0: an updated comprehensive database of antimicrobial resistance determinants and an improved software pipeline. *Nucleic Acids Res* 51:D744-D752.
- Yin X, Zheng X, Li L, et al. 2023. ARGs-OAP v3.0: antibiotic-resistance gene database curation and analysis pipeline optimization. *Engineering* 27:234-241.
- Arango-Argoty G, Garner E, Pruden A, et al. 2018. DeepARG: a deep learning approach for predicting antibiotic resistance genes from metagenomic data. *Microbiome* 6:23.
- Rowe WPM, Winn MD. 2018. Indexed variation graphs for efficient and accurate resistome profiling. *Bioinformatics* 34:3601-3608.
- Abramova A, Karkman A, Bengtsson-Palme J. 2024. Metagenomic assemblies tend to break around antibiotic resistance genes. *BMC Genomics* 25:959.

## Related Skills

- epidemiological-genomics/amr-surveillance - Isolate AMR, point mutations, phenotype/MIC, typing, GLASS
- functional-profiling - General gene-family/pathway abundance (HUMAnN can surface ARG families)
- kraken-classification - Taxonomic context for the community
- genome-assembly/metagenome-assembly - Assembly/binning and ARG-host linkage
- contamination-controls - Host depletion before resistome profiling
- workflows/metagenomics-pipeline - End-to-end shotgun analysis
<!-- END FILE: metagenomics/amr-detection/SKILL.md -->

## 子目录：metagenomics/contamination-controls

<!-- BEGIN FILE: metagenomics/contamination-controls/SKILL.md -->
---
name: bio-metagenomics-contamination-controls
description: Cleans a shotgun metagenome of everything that is not the target community before profiling - host-read depletion (Hostile, bowtie2/T2T-CHM13), reagent/kitome contamination control with blanks and decontam, mock-community validation, and depth-adequacy checks (Nonpareil). Covers why a metagenomic result is a position in a choice-chain rather than a direct observation, why extraction is the experiment, why a low-biomass community can be entirely kitome, why absence means not-detectable-by-this-chain, and why a confident classifier call can still be wrong when the reference is contaminated. Use when designing controls, removing host reads, identifying reagent contaminants, validating with mocks, or judging whether a low-biomass result is real. For adapter/quality trimming see read-qc; for MAG-level decontamination see genome-assembly/metagenome-assembly.
tool_type: mixed
primary_tool: decontam
---

## Version Compatibility

Reference examples tested with: decontam 1.22+, Hostile 1.1+, Bowtie2 2.5+, Nonpareil 3.4+, pandas 2.2+, R 4.3+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('decontam')` then `?isContaminant` to verify parameters
- CLI: `hostile --version`, `nonpareil -h` to confirm flags and indexes
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The controls define the result: an extraction blank defines the kitome for its batch/lot, a mock community defines the limit of detection and the extraction-lysis bias, and the host reference (prefer T2T-CHM13 over GRCh38) defines what host is removed. Record the extraction kit and lot, the host index, the blanks, the mock version (whole-cell vs DNA), and the reads removed at each step.

# Contamination Controls

**"Is this signal real, or did my pipeline create it?"** -> Remove host reads, define the kitome with blanks, validate with a mock, and confirm depth - because a low-biomass community can be entirely reagent contamination.
- R: `decontam::isContaminant(seqtab, conc=, neg=, method='combined')` on the classifier output table
- CLI: `hostile clean --fastq1 R1.fq.gz --fastq2 R2.fq.gz --index human-t2t-hla`

Scope: sample-level pre-analysis cleanup and controls - host depletion, kitome/blank/mock controls, decontam, depth adequacy. Adapter/quality trimming mechanics -> read-qc/adapter-trimming, read-qc/quality-filtering. MAG-level decontamination (CheckM2/GUNC chimerism, FCS-GX foreign sequence) -> genome-assembly/metagenome-assembly - a different, genome-level problem. Classification -> kraken-classification, metaphlan-profiling.

## The Single Most Important Modern Insight -- A Metagenomic Result Is a Position in a Choice-Chain

A metagenomic profile is the product of a chain of choices - extraction, host/contaminant depletion, depth, read-vs-assembly, classifier, database, normalization - and each link silently sets what is observable. The community is never observed directly; the report is the community as refracted by this pipeline. Three consequences a newcomer misses:

1. **There is no raw truth to recover.** Even the input DNA is already a biased sample of the cells (lysis bias). Cleaning the data does not get closer to the community; it changes which lens dominates. The honest framing is relative-within-a-consistent-pipeline.
2. **Absence means not-detectable-by-this-chain.** A zero is below the depth detection limit, OR not in the database, OR lost in extraction, OR removed by depletion - almost never simple biological absence. Force the question "which link is responsible?" before interpreting absence.
3. **The pipeline can manufacture the result.** In low biomass the entire community can BE the kitome; with the wrong database the profile is the database's bias; over-aggressive depletion deletes real taxa. Controls plus a consistent chain plus explicit reporting are what convert an uninterpretable number into a defensible measurement.

## Extraction Is the Experiment

Lysis efficiency is taxon-dependent: tough-walled Gram-positives (Firmicutes, *Staphylococcus*, *Enterococcus*), endospores (*Bacillus*, *Clostridium*), acid-fast *Mycobacterium*, and fungi/archaea resist lysis and are under-represented unless bead-beating is used. Gentle/enzymatic kits inflate easy-to-lyse Gram-negatives - so a Firmicutes:Bacteroidetes shift can be an extraction artifact. Extraction had the largest effect on observed composition across 21 protocols (Costea 2017 *Nat Biotechnol* 35:1069). Use bead-beating, hold one method constant across a study, validate lysis with a whole-cell mock, and report kit and lot. Note the tradeoff: aggressive bead-beating shears DNA and hurts long-read assembly, so the best extraction depends on the read-vs-assembly choice.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Host-associated sample (gut, oral, skin, tissue) | host-deplete first (Hostile, T2T-CHM13) | host reads waste depth and leak false calls; also a data-sharing/ethics requirement |
| Low-biomass sample (skin, BAL, CSF, tissue, blood) | blanks + DNA quantification + decontam mandatory | the lower the biomass, the larger the kitome fraction |
| Novel taxa claimed in low biomass | treat as kitome until proven (canonical genera) | placenta/tumor "microbiomes" were largely kitome |
| Need limit of detection / lysis check | run a mock (ZymoBIOMICS whole-cell) | the only sample with a known answer |
| Is my depth enough for this question? | Nonpareil coverage curve | depth sets the detection limit; host depletion halves usable depth |
| Confident classifier call, odd taxon | suspect a contaminated reference | confidence is not correctness if the reference is mislabeled |
| Adapter/quality trimming | -> read-qc | this skill owns metagenomics-specific cleanup, not generic trimming |
| MAG chimerism / foreign sequence in a bin | -> genome-assembly/metagenome-assembly | genome-level decontamination is a different problem |

## Host-Read Depletion

```bash
# Hostile removes >99.5% of human reads while discarding far fewer microbial reads than naive mapping.
# Prefer the T2T-CHM13-based index over GRCh38; high-sensitivity Bowtie2 drives removal more than the reference.
hostile clean --fastq1 sample_R1.fq.gz --fastq2 sample_R2.fq.gz \
    --index human-t2t-hla --aligner bowtie2
# Report the reads removed - it is a QC metric, not a footnote. For long reads use --aligner minimap2.
```

Remove host for two reasons: analytical (depth, false positives, runtime) and ethical (raw human-associated reads carry identifiable host genotype; depleting before deposit is increasingly required). Wet-lab depletion (saponin/DNase, methyl-CpG capture) saves sequencing but adds its own bias - a genuine tradeoff.

## Identify Reagent Contaminants with decontam

**Goal:** Separate real low-abundance taxa from the kitome using blanks and DNA concentration.

**Approach:** Run decontam on the classifier output table (taxa x samples) using the frequency signal (contaminants scale inversely with input DNA) and the prevalence signal (contaminants are enriched in blanks); raise the prevalence threshold for low biomass.

```r
library(decontam)
# seqtab: samples x taxa from the Bracken/MetaPhlAn table; conc: per-sample DNA concentration; neg: TRUE for blanks.
contam <- isContaminant(seqtab, conc = dna_conc, neg = is_blank, method = 'combined', threshold = 0.1)
# Low-biomass studies: use the prevalence method at the more aggressive threshold 0.5, and inspect the calls.
contam_lowbio <- isContaminant(seqtab, neg = is_blank, method = 'prevalence', threshold = 0.5, batch = batch_id)
seqtab_clean <- seqtab[, !contam$contaminant]
```

decontam runs per batch (`batch=`) because the kitome differs by lot/run. Always inspect the called contaminants against the canonical kitome genera (*Bradyrhizobium*, *Ralstonia*, *Burkholderia*, *Pseudomonas*, *Acinetobacter*, *Sphingomonas*, *Methylobacterium*, *Stenotrophomonas*) rather than applying blindly - over-aggressive removal deletes real taxa.

## Depth Adequacy

```bash
# Nonpareil estimates how much of the community's sequence space you have sampled, without assembly or a DB.
nonpareil -s reads.fasta -T kmer -f fasta -b sample_np
# Plot the coverage-vs-effort curve in R (Nonpareil.curve); a non-detection below the implied limit is meaningless.
```

Depth is set by the question: dominant taxa need a few million reads, rare-pathogen detection sets a limit of detection, and strain SNVs need high per-genome coverage. Host depletion can silently halve usable depth - budget for it.

## Per-Method Failure Modes

### Extraction bias reported as biology
**Trigger:** a Firmicutes:Bacteroidetes shift or "low Gram-positive" community from a gentle-lysis kit. **Mechanism:** taxon-dependent lysis under-represents tough-walled organisms. **Symptom:** composition differences tracking the kit, not the sample. **Fix:** bead-beating, one method held constant, a whole-cell mock to prove hard taxa are lysed.

### Kitome called as novel taxa in low biomass
**Trigger:** reporting novel low-abundance taxa from skin/BAL/tissue/blood without blanks. **Mechanism:** reagent DNA is a fixed dose; at low biomass it dominates the signal. **Symptom:** canonical kitome genera presented as discovery. **Fix:** extraction blanks through the full workflow, DNA quantification, decontam (prevalence + frequency), skepticism toward the kitome genera.

### Absence read as biological absence
**Trigger:** "taxon/function not present" or "low diversity." **Mechanism:** detection is bounded by depth, database, extraction, and depletion. **Symptom:** a negative interpreted as biology. **Fix:** report the classified fraction and the limit of detection; state which link is responsible before interpreting absence.

### Confident call from a contaminated reference
**Trigger:** trusting a high-confidence classifier assignment. **Mechanism:** >2 million GenBank/RefSeq entries carry mislabeled or chimeric sequence (Steinegger & Salzberg 2020 *Genome Biol* 21:115). **Symptom:** a confident, systematic wrong assignment (the classic stray human/vector in a microbial genome). **Fix:** treat confidence as not equal to correctness; cross-check surprising calls against a cleaner database.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| decontam threshold 0.1 default; 0.5 prevalence for low biomass | Davis 2018 *Microbiome* 6:226 | aggressive prevalence call needed when the kitome dominates |
| >= 1 extraction blank per batch | Salter 2014 *BMC Biol* 12:87 | blanks define the kitome for that lot; more for very low biomass |
| Hostile removes > 99.5% host | Constantinides 2023 *Bioinformatics* 39:btad728 | high host removal with low microbial loss |
| Prefer T2T-CHM13 over GRCh38 + mask rDNA | host-removal practice | GRCh38 gaps let host reads escape; rDNA masking spares microbial reads |
| Whole-cell vs DNA mock | mock-standard practice | whole-cell tests extraction/lysis; DNA tests classifier/library only |
| Nonpareil coverage before interpreting absence | Rodriguez-R 2018 *mSystems* 3:e00039-18 | a non-detection below the limit of detection is uninformative |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| decontam finds nothing useful | no blanks or DNA concentration supplied | add blanks (`neg=`) and/or DNA quant (`conc=`); run per batch |
| Host removal leaves human reads | GRCh38 with gaps, low-sensitivity aligner | use a T2T-CHM13 index and high-sensitivity Bowtie2 |
| Real microbes deleted in host removal | rDNA / conserved regions not masked | mask host rDNA; check microbial reads removed |
| Low-biomass "novel taxon" not reproducible | kitome | blanks + decontam; check canonical kitome genera |
| Cross-study profiles disagree | different extraction/depth/DB chains | hold the chain constant; do not meta-analyze across links |

## References

- Salter SJ, Cox MJ, Turek EM, et al. 2014. Reagent and laboratory contamination can critically impact sequence-based microbiome analyses. *BMC Biol* 12:87.
- Davis NM, Proctor DM, Holmes SP, Relman DA, Callahan BJ. 2018. Simple statistical identification and removal of contaminant sequences in marker-gene and metagenomics data. *Microbiome* 6:226.
- Costea PI, Zeller G, Sunagawa S, et al. 2017. Towards standards for human fecal sample processing in metagenomic studies. *Nat Biotechnol* 35:1069-1076.
- Steinegger M, Salzberg SL. 2020. Terminating contamination: large-scale search identifies more than 2,000,000 contaminated entries in GenBank. *Genome Biol* 21:115.
- Constantinides B, Hunt M, Crook DW. 2023. Hostile: accurate decontamination of microbial host sequences. *Bioinformatics* 39:btad728.
- Rodriguez-R LM, Gunturu S, Tiedje JM, Cole JR, Konstantinidis KT. 2018. Nonpareil 3: fast estimation of metagenomic coverage and sequence diversity. *mSystems* 3:e00039-18.

## Related Skills

- kraken-classification - Classification after host removal; database bias and contaminated references
- metaphlan-profiling - Marker-gene profiling after cleanup
- abundance-estimation - decontam runs on the classifier output abundance table
- metagenome-visualization - Plot blanks alongside samples; depth-adequacy curves
- read-qc/adapter-trimming - Generic adapter/quality trimming before this step
- genome-assembly/metagenome-assembly - MAG-level decontamination (a different, genome-level problem)
- workflows/metagenomics-pipeline - End-to-end pipeline with a controls/depletion stage up front
<!-- END FILE: metagenomics/contamination-controls/SKILL.md -->

## 子目录：metagenomics/functional-profiling

<!-- BEGIN FILE: metagenomics/functional-profiling/SKILL.md -->
---
name: bio-metagenomics-functional-profiling
description: Profiles the functional potential of shotgun metagenomes with HUMAnN 3's tiered search (MetaPhlAn prescreen, Bowtie2 pangenome, translated DIAMOND vs UniRef), giving gene-family (RPK) and MetaCyc pathway abundances stratified by species. Covers why a metagenome measures potential not activity, why dropping UNMAPPED/UNINTEGRATED biases everything, why stratification is an estimate, coverage-vs-abundance and MinPath/gap-fill, UniRef90-vs-50 and biome database bias, and the assembly/eggNOG/dbCAN/antiSMASH alternatives. Use when obtaining pathway or gene-family abundances, regrouping to KO/EC/GO, normalizing functional tables, or choosing read-based vs assembly-based functional profiling. For AMR genes see amr-detection; for host-gene enrichment see pathway-analysis.
tool_type: cli
primary_tool: HUMAnN
---

## Version Compatibility

Reference examples tested with: HUMAnN 3.6+, MetaPhlAn 4.1+, DIAMOND 2.1+, pandas 2.2+, scipy 1.12+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `humann --version` then `humann --help` to confirm flags and defaults
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Output is driven by the reference databases: the ChocoPhlAn nucleotide pangenome, the UniRef90/50 protein database, and the MetaPhlAn database version HUMAnN calls. Record all three. Match the MetaPhlAn database version to the HUMAnN version when supplying `--taxonomic-profile` (MetaPhlAn 3 and 4 databases differ), and pin UniRef90 vs UniRef50, which changes both sensitivity and the UNMAPPED fraction.

# Functional Profiling

**"What can my community do?"** -> Quantify gene families and pathways with a tiered search that only translates the reads the fast steps could not place - measuring functional POTENTIAL the community encodes, never what it is expressing.
- CLI: `humann --input reads.fastq.gz --output out/ --taxonomic-profile sample_metaphlan.tsv --threads 8`

Scope: read-based community function (HUMAnN) and the assembly/specialized-database alternatives. Read classification -> kraken-classification, metaphlan-profiling. AMR gene quantification -> amr-detection. Host-gene over-representation (GO/KEGG/GSEA) -> the pathway-analysis category. Assembly/ORF mechanics -> genome-assembly/metagenome-assembly. Host depletion and trimming -> contamination-controls, read-qc.

## The Single Most Important Modern Insight -- A Metagenome Measures Potential, Not Activity

A gene family or a "complete pathway" in HUMAnN output is a CAPABILITY the community encodes - never a rate, a flux, or proof of expression. The DNA says the cell could ferment pyruvate; only RNA (metatranscriptome), protein, or metabolite data says it is. RNA functional profiles decouple from gene carriage (Franzosa 2014 *PNAS* 111:E2329), so narrating a pathabundance table as "the disease microbiome upregulates X" is the cardinal sin - it carries the gene more abundantly, nothing more. If the question is about activity, pair with metatranscriptomics: run the same HUMAnN on RNA and divide RNA-CPM by matched DNA-CPM per feature to get expression per gene copy. Memorable form: HUMAnN reports what the community CAN do, never what it IS doing. And every cell of the table is a model-dependent artifact of a reference database plus a tiered search at chosen thresholds - a hypothesis conditioned on the reference, not a measurement.

## The Tiered Search Is the Algorithm

HUMAnN does not brute-force-translate every read. Three tiers each filter the input to the next, so the slow translated step only sees what the fast steps could not place:

1. **Taxonomic prescreen (MetaPhlAn).** Detect species, then build a sample-specific ChocoPhlAn pangenome from only species above `--prescreen-threshold` (default 0.01%). Reuse via `--taxonomic-profile` to skip re-running MetaPhlAn.
2. **Nucleotide pangenome search (Bowtie2).** Reads mapping to that pangenome get a UniRef90 family WITH a high-confidence species label - this is where confident stratification comes from.
3. **Translated protein search (DIAMOND).** Reads that failed tier 2 are 6-frame translated and aligned to full UniRef90/50; they get a family but the species is INFERRED or `|unclassified` - lower-confidence stratification. Reads matching nothing become UNMAPPED.

This model is why `--bypass-*` flags and `--prescreen-threshold` change results, and why a stratified contribution from the translated tier is an estimate, not a measurement.

## Tool Taxonomy

| Tool | Citation | Role | When |
|------|----------|------|------|
| HUMAnN 3 | Beghini 2021 *eLife* 10:e65088 | tiered read-based gene-family + MetaCyc pathway abundance | quantitative community function across samples |
| eggNOG-mapper v2 | Cantalapiedra 2021 *Mol Biol Evol* 38:5825 | orthology annotation (KO/GO/EC/CAZy/COG) of predicted ORFs | assembly route; flat functional catalogue |
| DIAMOND | Buchfink 2021 *Nat Methods* 18:366 | fast sensitive protein search (blastx) | custom read-vs-protein-DB profiling; backend of many tools |
| dbCAN3 | Zheng 2023 *Nucleic Acids Res* 51:W115 | CAZyme family/subfamily + substrate | carbohydrate-active enzymes (UniRef under-resolves these) |
| antiSMASH 7 | Blin 2023 *Nucleic Acids Res* 51:W46 | biosynthetic gene cluster detection | secondary-metabolite BGCs; CONTIGS only |
| MinPath | Ye & Doak 2009 *PLoS Comput Biol* 5:e1000465 | parsimony pathway calling inside HUMAnN | suppresses naive any-gene-implies-pathway over-calling |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Quantitative community function across samples | HUMAnN 3 (read-based) | counts every read; comprehensive; DB-bounded |
| Gut/host-associated, fine resolution | HUMAnN + UniRef90 | well-covered biome; specific families |
| Soil/marine/novel, big UNMAPPED | HUMAnN + UniRef50, or assembly route | UniRef90 cannot map divergent homologs |
| Need gene-to-organism/operon context or novel function | assembly + Prodigal + eggNOG-mapper | genomic context; accept loss of the unassembled majority |
| Carbohydrate-active enzymes | dbCAN3 | CAZy families/substrate beat generic UniRef |
| Biosynthetic gene clusters | antiSMASH (-> assembly first) | clusters span kb; require contigs |
| Activity, not capability | metatranscriptome (HUMAnN RNA mode) / RNA-DNA ratio | DNA cannot report expression |
| AMR gene quantification | -> amr-detection | dedicated ARG databases are the standard |
| Host-gene pathway enrichment | -> pathway-analysis | community pathway abundance is not GSEA |

## Run HUMAnN and Build a Functional Table

```bash
# Pre-QC first: adapter/quality trim AND host-deplete (e.g. KneadData). Host reads inflate UNMAPPED
# and waste DIAMOND time. Paired-end has no native pairing - concatenate R1+R2 into one file.
cat sample_R1.fq.gz sample_R2.fq.gz > sample.fq.gz
humann --input sample.fq.gz --output out/ \
    --taxonomic-profile sample_metaphlan.tsv \   # reuse the MetaPhlAn profile; do NOT --remove-temp-output and lose it
    --threads 8                                   # defaults: prescreen 0.01, translated-id 80 (uniref90), gap-fill on, minpath on

# Normalize PER SAMPLE before cross-sample stats (RPK is depth-dependent), then join and split.
humann_renorm_table -i out/sample_genefamilies.tsv -o out/sample_cpm.tsv -u cpm   # cpm preferred for models
humann_join_tables -i out -o merged_pathabundance.tsv --file_name pathabundance
humann_regroup_table -i merged_pathabundance.tsv -g uniref90_ko -o merged_ko.tsv  # adds an UNGROUPED row - keep it
humann_split_stratified_table -i merged_pathabundance.tsv -o .                     # run stats on the UNSTRATIFIED file
```

## Differential Abundance Without Biasing the Denominator

**Goal:** Test pathways between conditions without inventing abundance by discarding the unmapped fraction.

**Approach:** Keep UNMAPPED/UNINTEGRATED through normalization, check they do not differ by group (they often track the phenotype), then test the unstratified community totals with a compositional method (MaAsLin2/ANCOM-BC), not a bare Mann-Whitney on proportions.

```python
import pandas as pd

df = pd.read_csv('merged_pathabundance_unstratified.tsv', sep='\t', index_col=0)
meta = pd.read_csv('metadata.tsv', sep='\t', index_col=0)
unmapped = df.loc[['UNMAPPED', 'UNINTEGRATED']]            # the denominator - inspect, do not drop
g1 = meta.index[meta['condition'] == 'healthy']
g2 = meta.index[meta['condition'] == 'disease']
# If UNMAPPED differs by group, an assigned-feature comparison is confounded - report it.
unmapped_shift = unmapped[g2].mean(axis=1) - unmapped[g1].mean(axis=1)
print('UNMAPPED/UNINTEGRATED shift (disease - healthy):')
print(unmapped_shift.round(1))
# Then hand the unstratified table (UNMAPPED retained) to MaAsLin2/ANCOM-BC, which model
# compositionality and zero-inflation - not a raw t-test/Mann-Whitney on relative abundance.
```

## Per-Method Failure Modes

### Dropping UNMAPPED/UNINTEGRATED then renormalizing
**Trigger:** `.drop(['UNMAPPED','UNINTEGRATED'])` before relab. **Mechanism:** rescales assigned features to sum to 1, inventing abundance and erasing the database-coverage signal. **Symptom:** two samples with 20% vs 60% UNMAPPED look identical; a hit appears or vanishes. **Fix:** keep them through normalization; report them; if comparing assigned features only, confirm UNMAPPED does not differ by group.

### Stratification read as ground truth
**Trigger:** "species X contributes Y% of pathway Z." **Mechanism:** tier-2 species labels are confident, tier-3 (translated) are inferred or `|unclassified`. **Symptom:** over-confident organism-of-origin claims; ignored unclassified mass. **Fix:** treat contributions as estimates; flag the unclassified fraction; for confident gene-to-organism linkage use the assembly+binning route.

### Gut-centric QC thresholds applied to other biomes
**Trigger:** flagging a soil run as failed because UNMAPPED > 50%. **Mechanism:** UniRef is biased toward well-studied microbes; environmental biomes have large genuine dark function. **Symptom:** healthy environmental runs labeled failures. **Fix:** in novel biomes a big UNMAPPED is the environment, not a failure - drop to UniRef50 for sensitivity or switch to the assembly route.

### Coverage vs abundance confusion; gap-fill/MinPath artifacts
**Trigger:** reading `pathcoverage` as abundance or trusting a "complete" pathway. **Mechanism:** gap-fill (default on) scores pathways with missing reactions; MinPath parsimony prunes redundant pathways so absence is not biological absence; coverage is de-emphasized in recent docs. **Symptom:** fabricated completeness or missing real-but-redundant pathways. **Fix:** use abundance for stats; treat coverage as a soft presence prior; know gap-fill and MinPath are on by default.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `--prescreen-threshold` 0.01% | HUMAnN docs | species below this are excluded from the tier-2 pangenome |
| `--translated-identity-threshold` 80 (UniRef90) / 50 (UniRef50) | HUMAnN docs | the sensitivity knob; divergent homologs fail the 80% cutoff |
| nucleotide/translated coverage 90/50 | HUMAnN docs | query 90%, subject 50% coverage filters |
| `--evalue` 1.0 | HUMAnN docs | permissive DIAMOND e-value; tier design controls specificity |
| gap-fill on, MinPath on | HUMAnN docs | sensitivity/parsimony defaults that shape pathway presence |
| Normalize RPK -> CPM per sample before stats | HUMAnN docs | RPK is depth-dependent; CPM preferred for linear/log models |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Huge UNMAPPED on a gut sample | host reads not removed | host-deplete + trim before HUMAnN |
| MetaPhlAn profile gone after run | `--remove-temp-output` deleted `_humann_temp/` | omit it; keep the profile for reuse and taxonomy |
| `--taxonomic-profile` rejected | MetaPhlAn DB version mismatch with HUMAnN | match the MetaPhlAn database to the HUMAnN version |
| Pathways look over-called | MinPath off / naive any-gene mapping | keep MinPath on (default) |
| Stratified DA is all zeros/noise | bare t-test on zero-inflated strata | run stats on the unstratified table with MaAsLin2/ANCOM-BC |
| CAZymes under-annotated by UniRef | generic database under-resolves CAZy | use dbCAN3 on predicted ORFs |

## References

- Beghini F, McIver LJ, Blanco-Miguez A, et al. 2021. Integrating taxonomic, functional, and strain-level profiling of diverse microbial communities with bioBakery 3. *eLife* 10:e65088.
- Franzosa EA, Morgan XC, Segata N, et al. 2014. Relating the metatranscriptome and metagenome of the human gut. *PNAS* 111:E2329-E2338.
- Ye Y, Doak TG. 2009. A parsimony approach to biological pathway reconstruction/inference for genomes and metagenomes. *PLoS Comput Biol* 5:e1000465.
- Buchfink B, Reuter K, Drost HG. 2021. Sensitive protein alignments at tree-of-life scale using DIAMOND. *Nat Methods* 18:366-368.
- Cantalapiedra CP, Hernandez-Plaza A, Letunic I, Bork P, Huerta-Cepas J. 2021. eggNOG-mapper v2: functional annotation, orthology assignments, and domain prediction at the metagenomic scale. *Mol Biol Evol* 38:5825-5829.
- Hyatt D, Chen GL, LoCascio PF, et al. 2010. Prodigal: prokaryotic gene recognition and translation initiation site identification. *BMC Bioinformatics* 11:119.
- Zheng J, Hu B, Zhang X, et al. 2023. dbCAN3: automated carbohydrate-active enzyme and substrate annotation. *Nucleic Acids Res* 51:W115-W121.
- Blin K, Shaw S, Augustijn HE, et al. 2023. antiSMASH 7.0: new and improved predictions. *Nucleic Acids Res* 51:W46-W50.

## Related Skills

- metaphlan-profiling - The taxonomic prescreen HUMAnN reuses via --taxonomic-profile
- kraken-classification - Alternative taxonomic input
- abundance-estimation - Compositional normalization shared with functional tables
- amr-detection - Dedicated ARG quantification (HUMAnN can surface AMR families but is not standard)
- metagenome-visualization - Plot and test functional tables
- contamination-controls - Host depletion before HUMAnN
- genome-assembly/metagenome-assembly - Assembly route for contextualized/novel function
- pathway-analysis/kegg-pathways - Organism-centric pathway interpretation (not community abundance)
<!-- END FILE: metagenomics/functional-profiling/SKILL.md -->

## 子目录：metagenomics/kraken-classification

<!-- BEGIN FILE: metagenomics/kraken-classification/SKILL.md -->
---
name: bio-metagenomics-kraken
description: Classifies shotgun metagenomic reads to taxa with Kraken2's minimizer/LCA matching against a chosen reference database, then hands off to Bracken for abundance re-estimation. Covers why the database (not the algorithm) decides what can be detected, the --confidence and --minimum-hit-groups precision levers, unique-minimizer false-positive control, host-read removal, and why raw Kraken2 read counts are not abundances. Use when profiling who-is-there from shotgun reads, choosing a Kraken2 database, setting a confidence threshold, controlling false positives, or feeding reports to Bracken. For marker-gene profiling see metaphlan-profiling; for abundance mechanics see abundance-estimation; for assembly/MAG recovery see genome-assembly/metagenome-assembly.
tool_type: cli
primary_tool: Kraken2
---

## Version Compatibility

Reference examples tested with: Kraken2 2.1.3+, Bracken 2.9+, KrakenTools 1.2+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `kraken2 --version`, `bracken -h`, `kraken2 --help` to confirm flags and defaults
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The DATABASE is the version that matters most. A taxon absent from the database is invisible no matter how the binary is configured. Record the Kraken2 database build (Standard / PlusPF / PlusPFP / nt / GTDB, and whether capped to 8/16 GB) and the Bracken `databaseRLENmers.kmer_distrib` read length, which must match both the Kraken2 database and the actual read length. `--minimum-hit-groups` enforcement varied across older 2.x point releases; confirm defaults with `kraken2 --help` on the installed build.

# Kraken Classification

**"What's in my metagenome?"** -> Match each read's k-mers to a reference database by lowest-common-ancestor, then re-estimate abundance with Bracken - because the database, not the algorithm, decides what can be found.
- CLI: `kraken2 --db DB --paired R1.fq.gz R2.fq.gz --report out.kreport --confidence 0.1 --output out.kraken`

Scope: read-based, assembly-free taxonomic classification of shotgun reads, plus the Bracken handoff. Marker-gene profiling -> metaphlan-profiling. Bracken command mechanics -> abundance-estimation. Genome/MAG recovery -> genome-assembly/metagenome-assembly. Host removal and read QC -> read-qc/contamination-screening, contamination-controls. Amplicon/16S -> the microbiome category.

## The Single Most Important Modern Insight -- A Kraken Report Is a Database-Conditioned Similarity Ledger, Not a Sample Inventory

Kraken reports what each read most resembles in THIS database - never what is truly present, and never how much. Every number is hostage to three choices made before the run: the database, the confidence threshold, and the assumption that read count means abundance. Three corollaries each common misuse violates:

1. **Classification is not presence.** At `--confidence 0` with the LCA rule, one shared k-mer labels a read with its nearest database relative even when the true organism is absent. Absence-from-database becomes a confident wrong species.
2. **Read count is not abundance.** Counts scale with genome length and copy number, so the report percentage is a fragment fraction, not a cell fraction. Bracken fixes the wrong-rank problem; it does not fix this.
3. **A taxon at the bottom of the report is a hypothesis, not a finding.** Single-region hits, hash collisions, and contaminated references populate the long tail. Unique-minimizer coverage separates a real low-abundance organism from a phantom.

Organize the analysis around defending against these three, not around listing flags. Kraken2 at defaults over-classifies; Kraken2 tuned (right database + confidence + hit-groups + a unique-k-mer floor + host removal) is competitive with any classifier.

## Why "Exact K-mer" Is Wrong for Kraken2

Kraken1 (Wood & Salzberg 2014 *Genome Biol* 15:R46) stored every exact k-mer. Kraken2 (Wood 2019 *Genome Biol* 20:257) replaced that with three ideas that make it fast and lean but PROBABILISTIC: (a) minimizers collapse each k-mer (default k=35) to the smallest hashed l=31-mer in its window; (b) a spaced seed (s=7 masked positions) tolerates errors at "don't care" positions; (c) a compact hash table stores only high bits of each key. The compact hash can return a wrong or spurious LCA on collision - which is exactly why the precision levers below exist. Calling Kraken2 "exact k-mer" hides where false positives come from.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| Kraken2 | Wood 2019 *Genome Biol* 20:257 | minimizer + spaced-seed + compact-hash LCA | fast read classification; database-bound; the default choice |
| Bracken | Lu 2017 *PeerJ Comput Sci* 3:e104 | Bayesian redistribution of reads stranded at higher ranks | always run after Kraken2 for species/genus estimates |
| KrakenUniq | Breitwieser 2018 *Genome Biol* 19:198 | HyperLogLog count of unique k-mers per taxon | false-positive control on hits of interest |
| KMCP | Shen 2023 *Bioinformatics* 39:btac845 | genome-coverage pseudo-mapping | low-depth/clinical/viral where conserved-region FPs hurt |
| sourmash gather | Pierce 2019 *F1000Res* 8:1006 | FracMinHash containment, min-set-cover | "which genomes are present" with calibrated containment |
| MetaPhlAn 4 | Blanco-Miguez 2023 *Nat Biotechnol* 41:1633 | clade-specific marker genes | -> metaphlan-profiling; FP-conservative, abundance directly |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Who-is-there, fast, custom database possible | Kraken2 + Bracken | k-mer LCA; Bracken fixes count->rank, not count->cells |
| Need species relative abundance with no database build | -> metaphlan-profiling | marker-based; abundance-conservative; no FP tail |
| Low-biomass / clinical pathogen ID | Kraken2 (high confidence + hit-groups) + KrakenUniq unique-k-mer floor | the FP tail is the enemy; one unique-k-mer filter cuts phantoms |
| Reads not host-depleted / unQC'd | -> contamination-controls, read-qc/contamination-screening first | host reads swamp the profile; references carry human fragments |
| Want abundance comparable across studies | state the database + confidence; do not merge with MetaPhlAn percentages | read fraction != cell fraction; different tools = different quantities |
| Recover genomes / novel taxa / MAGs | -> genome-assembly/metagenome-assembly | classification is assembly-free and database-bound |
| 16S amplicon reads | -> microbiome category | Kraken-on-16S works but amplicon analysis lives there |

## Basic Classification

```bash
# Paired-end, with the precision levers that defaults omit
kraken2 --db "$KRAKEN_DB" \
    --paired --gzip-compressed --threads 8 \
    --confidence 0.1 \            # raise from default 0 to suppress single-k-mer false positives
    --minimum-hit-groups 2 \      # require >=2 distinct hit regions (default 2; raise to 3 for clinical)
    --report out.kreport \
    --output out.kraken \
    R1.fq.gz R2.fq.gz
```

`--paired` joins mates with a k-mer-breaking `N` and classifies the pair as one fragment, raising specificity. The per-read `--output` (large) can be dropped to `/dev/null` once the `.kreport` is what feeds Bracken. `--memory-mapping` runs without loading the database into RAM (slower; for low-memory hosts).

## False-Positive Control: Unique Minimizers

**Goal:** Separate a real low-abundance organism from a single-region phantom before believing any tail taxon.

**Approach:** Enable `--report-minimizer-data` so the report carries distinct-minimizer counts; a taxon with many reads but few distinct minimizers is hitting one conserved region and is a red flag. KrakenUniq's HyperLogLog unique-k-mer count is the heavier-weight version of the same signal.

```bash
kraken2 --db "$KRAKEN_DB" --paired --confidence 0.1 \
    --report-minimizer-data \    # inserts 2 columns: total + DISTINCT minimizers (shifts later columns)
    --report out.kreport --output /dev/null \
    R1.fq.gz R2.fq.gz
# A species with high reads but low distinct-minimizers = false positive (one region lit up repeatedly).
```

Calibrate a unique-k-mer floor against negative controls rather than hard-coding one; the clinical ">=1024 unique k-mers" cutoff is dataset/database-specific folklore, not a constant.

## Build a Custom Database

**Goal:** Build a database whose contents define exactly the detectable universe (and include human for host capture).

**Approach:** Download taxonomy, add the libraries the question needs (including `human`), build the minimizer index, then build the matching Bracken distributions at the actual read length.

```bash
kraken2-build --download-taxonomy --db custom_db
for lib in bacteria archaea viral human UniVec_Core; do
    kraken2-build --download-library "$lib" --db custom_db
done
kraken2-build --build --db custom_db --threads 16    # writes hash.k2d, opts.k2d, taxo.k2d
kraken2-build --clean --db custom_db                 # drop library/ + taxonomy/ to shrink
bracken-build -d custom_db -t 16 -k 35 -l 150        # -k MUST equal the Kraken2 k (35); -l = read length
```

`kraken2-build --special gtdb` builds a GTDB-taxonomy database (curated; the greengenes/silva/rdp special downloads have rotted). `--max-db-size` randomly downsamples k-mers to fit a cap - this is how the prebuilt 8gb/16gb databases are made, and the reason confidence collapses classification on them.

## Hand Off to Bracken

Kraken strands reads at the shared genus when species share k-mers; Bracken redistributes them down using genome-derived priors. It fixes the wrong-rank problem only - never genome-size bias, and never false positives (it can amplify or even invent a species by reassigning an absent organism's reads to its nearest congener). Run FP control first. Command mechanics live in abundance-estimation:

```bash
bracken -d "$KRAKEN_DB" -i out.kreport -o out.bracken -w out.bracken.kreport \
    -r 150 \   # MUST match a built databaseRLENmers.kmer_distrib AND the actual read length
    -l S -t 10 # species level; -t is a redistribution floor (drops taxa with fewer than 10 clade-level reads, strict <), not a confidence
```

## Per-Method Failure Modes

### Over-classification at default confidence
**Trigger:** running `--confidence 0` and reporting the species list. **Mechanism:** one shared k-mer can classify a read; the LCA labels it with its nearest database relative. **Symptom:** hundreds of low-abundance species, many biologically implausible. **Fix:** `--confidence 0.1-0.4` (database-dependent) plus `--minimum-hit-groups >=2`; verify the tail with unique minimizers.

### Counts read as abundance
**Trigger:** using the `.kreport` percentage column as relative abundance. **Mechanism:** read count is proportional to abundance x genome length x copy number. **Symptom:** large-genome taxa overstated; downstream diversity/ordination on a non-cell-fraction. **Fix:** run Bracken for the rank problem; treat even Bracken `fraction_total_reads` as a read fraction and hand off genome-size/copy-number caveats to abundance-estimation.

### Bracken read-length mismatch
**Trigger:** `-r 100` on 150 bp reads, or a database built only for a different length. **Mechanism:** the redistribution model is fragment-length specific. **Symptom:** biased abundances with no error (silent) if the `.kmer_distrib` exists, hard crash if it does not. **Fix:** `-r` = actual read length AND a matching `databaseRLENmers.kmer_distrib` must exist (build it or pick a prebuilt database shipping that length).

### Capped database plus high confidence
**Trigger:** a Standard-8/16 database with confidence cranked up. **Mechanism:** capped databases are random k-mer subsamples; few reads can clear a high threshold. **Symptom:** classification collapses toward zero; "my sample is mostly novel." **Fix:** use a full/large database for high confidence, or lower confidence on a capped database and accept lower precision.

### Host reads and contaminated references
**Trigger:** classifying without host depletion, then trusting human and low-level hits. **Mechanism:** host reads dominate low-biomass samples, and >2 million GenBank entries carry mislabeled human/vector sequence (Steinegger & Salzberg 2020 *Genome Biol* 21:115). **Symptom:** confident `Homo sapiens` plus a long artifactual tail. **Fix:** include `human` in the database and/or host-deplete upstream; scrutinize any taxon co-varying with host load; consider Recentrifuge negative-control subtraction.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `--confidence` 0.0 default; use 0.2-0.4 on a comprehensive DB | Liu 2024 *aBIOTECH* 5:465; Lu 2022 *Nat Protoc* 17:2815 | species precision rose from ~0.16 to ~0.76 at CS 0.2; default over-classifies |
| `--minimum-hit-groups` 2 (raise to 3 for clinical) | Kraken2 manual | a single lucky minimizer/collision cannot make a call |
| Bracken `-k` = 35 | Lu 2017 *PeerJ Comput Sci* 3:e104 | must equal the Kraken2 database k-mer length |
| Bracken `-r` = actual read length | Bracken docs | redistribution priors are fragment-length specific |
| Bracken `-t` 10 default | Bracken docs | redistribution floor; too high deletes real rare taxa, not a confidence |
| Classification rate 30-70% (environmental) | community | low rate = novel taxa OR host contamination OR wrong database - diagnose which |
| Build k/l/s = 35/31/7 (nuc); 15/12/0 (prot) | Kraken2 manual | build-time only; cannot change k at classify time |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Hundreds of implausible species | `--confidence 0`, no hit-group floor | raise confidence; `--minimum-hit-groups >=2`; unique-k-mer filter |
| Bracken: "kmer_distrib file not found" | `-r` has no matching built distribution | run `bracken-build -l <readlen>` or use a prebuilt DB shipping that length |
| Report parsing columns misaligned | `--report-minimizer-data` inserted 2 columns | parse 8-column layout when the flag is on |
| Near-zero classification on a small DB | capped (downsampled) DB + high confidence | larger DB, or lower confidence on the capped DB |
| Confident human + odd tail | host reads + contaminated references | host-deplete first; treat human/tail as suspect |
| Bash example silently truncates flags | inline `# comment` after a `\` line continuation | put comments on their own line |

## References

- Wood DE, Lu J, Langmead B. 2019. Improved metagenomic analysis with Kraken 2. *Genome Biol* 20:257.
- Wood DE, Salzberg SL. 2014. Kraken: ultrafast metagenomic sequence classification using exact alignments. *Genome Biol* 15:R46.
- Lu J, Breitwieser FP, Thielen P, Salzberg SL. 2017. Bracken: estimating species abundance in metagenomics data. *PeerJ Comput Sci* 3:e104.
- Breitwieser FP, Baker DN, Salzberg SL. 2018. KrakenUniq: confident and fast metagenomics classification using unique k-mer counts. *Genome Biol* 19:198.
- Lu J, Rincon N, Wood DE, Breitwieser FP, Pockrandt C, Langmead B, Salzberg SL, Steinegger M. 2022. Metagenome analysis using the Kraken software suite. *Nat Protoc* 17:2815-2839.
- Liu Y, Ghaffari MH, Ma T, Tu Y. 2024. Impact of database choice and confidence score on the performance of taxonomic classification using Kraken2. *aBIOTECH* 5:465-475.
- Steinegger M, Salzberg SL. 2020. Terminating contamination: large-scale search identifies more than 2,000,000 contaminated entries in GenBank. *Genome Biol* 21:115.
- Shen W, Xiang H, Huang T, et al. 2023. KMCP: accurate metagenomic profiling of both prokaryotic and viral populations by pseudo-mapping. *Bioinformatics* 39:btac845.

## Related Skills

- abundance-estimation - Bracken command mechanics and read-count-to-abundance conversion
- metaphlan-profiling - Marker-gene alternative; FP-conservative, abundance reported directly
- metagenome-visualization - Plot and run community stats on the resulting profiles
- contamination-controls - Host depletion, blanks, and decontam before classification
- genome-assembly/metagenome-assembly - Assembly/MAG recovery; this category is read-based
- read-qc/contamination-screening - Host/vector read screening before classification
- workflows/metagenomics-pipeline - End-to-end shotgun profiling
<!-- END FILE: metagenomics/kraken-classification/SKILL.md -->

## 子目录：metagenomics/metagenome-visualization

<!-- BEGIN FILE: metagenomics/metagenome-visualization/SKILL.md -->
---
name: bio-metagenomics-visualization
description: Turns a shotgun profiler table (MetaPhlAn relative abundance, Bracken counts, HUMAnN function tables) into honest figures and defensible community statistics with phyloseq, vegan, microViz, and Python. Covers why an ordination/bar/diversity number is a modeling choice that can manufacture a result, the MetaPhlAn-percent-vs-Bracken-counts fork that decides everything, CLR/Aitchison vs Bray-Curtis, Hill numbers and why shotgun richness is a database readout, pairing PERMANOVA with betadisper, and the multi-tool differential-abundance consensus. Use when plotting taxonomic/functional profiles, computing alpha/beta diversity, running ordination/PERMANOVA, or testing differential abundance. For amplicon/QIIME2 stats see the microbiome category; for compositional theory see abundance-estimation.
tool_type: mixed
primary_tool: phyloseq
---

## Version Compatibility

Reference examples tested with: phyloseq 1.46+, vegan 2.6+, microViz 0.12+, ALDEx2 1.34+, pandas 2.2+, scikit-bio 0.6+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `ktImportTaxonomy` (no args) to confirm Krona column flags on the installed build

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The input profiler decides the toolchain: MetaPhlAn gives relative abundance (cannot rarefy; ships an SGB tree so UniFrac is available); Bracken gives counts (rarefaction and count models valid; no tree); HUMAnN gives gene-family/pathway features. Record the profiler, its filtering (Kraken `--confidence`, Bracken threshold, MetaPhlAn `--stat_q`), and every modeling choice below - they are not recoverable from the figure.

# Metagenome Visualization

**"Show me how my communities differ."** -> Choose a transform, a distance, and a test - each a modeling choice that can create or erase the difference - then declare them and show the conclusion survives them.
- R: phyloseq + vegan + microViz on a parsed profiler table
- Python: pandas + scikit-bio + matplotlib (plotting and wrangling; R is primary for community stats)

Scope: visualizing and testing a shotgun profiler table. Input generation -> kraken-classification, metaphlan-profiling, abundance-estimation, functional-profiling. Compositional theory and absolute load -> abundance-estimation. Amplicon/QIIME2 stats -> the microbiome category. Generic plotting primitives -> data-visualization.

## The Single Most Important Modern Insight -- A Figure Is a Modeling Choice, Not an Observation

The distance metric, the transform, the rarefaction depth, the confidence filter, and the top-N cutoff are knobs turned before the answer is seen; turning them differently gives a different paper. A shotgun table is a compositional, depth-confounded, false-positive-laden estimate, and the figure inherits all of it. The job is to declare the modeling choices and show they did not fabricate the conclusion. Memory hooks:

- A stacked bar of relative abundance hides absolute load and visually inflates whatever is already dominant - it shows the relative race, not whether the community bloomed or collapsed.
- Bray-Curtis on relative abundance is the field default and is compositionally incoherent; Aitchison (Euclidean on CLR) is correct and almost nobody runs it.
- Shotgun richness is a readout of the database and the confidence threshold, not biology.
- A significant PERMANOVA may be a difference in variability, not composition.
- The differentially abundant taxa reported depend more on which DA tool was run than on biology.

The fork that decides everything downstream: **MetaPhlAn = percent, Bracken = counts.** Rarefaction is only meaningful for counts; CLR needs a pseudocount on percentages; richness estimators (Chao1/Observed) require integer counts and are meaningless on MetaPhlAn relative abundances.

## Honest Composition Plots

Krona gives the full drillable hierarchy - often the honest answer to "what is in it," versus a bar that pre-collapses to the top 10:

```bash
kreport2krona.py -r kraken.kreport -o krona.txt && ktImportText krona.txt -o krona.html
# Confirm ktImportTaxonomy column flags with no-arg usage; they drift across versions.
```

For a stacked bar: collapse rare taxa to "Other" but label how many taxa and what percent that hides; state n per group (never stack one representative sample); use a colorblind-safe palette of <=12 colors; show absolute load alongside if total-biomass data exist. microViz `comp_barplot()` handles Other and palettes.

## Alpha Diversity: Hill Numbers and Richness Honesty

**Goal:** Report within-sample diversity in interpretable units without letting shotgun richness masquerade as biology.

**Approach:** Use Hill numbers (effective species) at q=0/1/2; prefer evenness-weighted q=1/q=2 for shotgun because richness (q=0) is dominated by database size and false positives; only compute richness estimators on integer counts.

```r
library(phyloseq); library(vegan)
# estimate_richness Observed/Chao1 assume INTEGER COUNTS - valid for Bracken, meaningless on MetaPhlAn %.
alpha <- estimate_richness(ps_counts, measures = c('Shannon', 'InvSimpson'))
hill_q1 <- exp(alpha$Shannon)        # effective species (q=1), interpretable units
hill_q2 <- alpha$InvSimpson          # q=2, dominance-weighted; robust to rare-taxon noise
```

Richness moves drastically with the classifier's confidence/threshold and 25-70% of shotgun species can be false positives - report the filtering, show a rarefaction or coverage curve, and gate richness behind unique-k-mer evidence (KrakenUniq). The rarefaction debate is unresolved: McMurdie & Holmes 2014 (*PLoS Comput Biol* 10:e1003531) call rarefying inadmissible for differential abundance; Schloss 2024 (*mSphere* 9:e00355-23) defends it for diversity. Decide per analysis - rarefy/coverage-standardize for diversity, model-based for DA - and show the curve either way.

## Beta Diversity and Ordination

| Distance | Compositionally coherent | Needs tree | When |
|----------|--------------------------|------------|------|
| Bray-Curtis | no | no | field default, intuitive; label it incoherent |
| Aitchison (Euclidean on CLR) | yes | no | the compositional-correct choice; needs zero handling |
| Robust Aitchison / RPCA (DEICODE) | yes | no | handles sparsity without a pseudocount |
| Weighted/unweighted UniFrac | partial | yes | only if a tree exists (MetaPhlAn SGB tree; not Bracken/HUMAnN) |

PCoA decomposes any distance; PCA on CLR is the compositional-coherent ordination and gives taxon loadings (which taxa drive an axis) that PCoA cannot; NMDS reports stress (not variance); UMAP does not preserve global distances and is for spotting clusters, not measuring dissimilarity. Pick the geometry for a stated reason and show the conclusion survives at least one alternative.

```r
library(vegan)
dist_bc <- vegdist(otu_matrix, method = 'bray')   # samples as rows
pm <- adonis2(dist_bc ~ group, permutations = 999, by = 'terms')
# ALWAYS pair PERMANOVA with a dispersion test - a significant adonis2 can be a spread difference,
# not a location shift (Anderson & Walsh 2013), especially for unbalanced designs.
bd <- betadisper(dist_bc, group); permutest(bd, permutations = 999)
```

If betadisper is significant, the PERMANOVA is ambiguous - report both.

## Differential Abundance: Consensus, Not a Single Tool

DA methods disagree wildly across datasets (Nearing 2022 *Nat Commun* 13:342); the taxa called significant depend more on the tool than on biology. Run at least two compositionally aware methods, report the intersect as high-confidence and the union as exploratory, and name every tool. ALDEx2 and ANCOM-II were the most conservative/consistent in Nearing; LinDA and ANCOM-BC were well FDR-controlled in Yang & Chen 2022. Prevalence-filter first and BH-correct across taxa.

| Tool | Model | Citation |
|------|-------|----------|
| ALDEx2 | Dirichlet Monte-Carlo -> CLR | Fernandes 2014 *Microbiome* 2:15 |
| ANCOM-BC | log-linear + sampling-fraction bias correction | Lin & Peddada 2020 *Nat Commun* 11:3514 |
| MaAsLin2 | general linear model + covariates | Mallick 2021 *PLoS Comput Biol* 17:e1009442 |
| LinDA | linear model on CLR + bias correction | Zhou 2022 *Genome Biol* 23:95 |

The anti-pattern to forbid: an uncorrected Wilcoxon or t-test on raw relative abundances - wrong on compositionality and on multiple testing in one line. Most tools want counts (Bracken); for MetaPhlAn percentages use methods that accept proportions (MaAsLin2/LinDA) or convert to pseudo-counts.

## Compositional Ordination in Python

**Goal:** Produce a compositionally coherent ordination in Python instead of the incoherent StandardScaler-then-PCA on raw relative abundance.

**Approach:** Replace zeros, CLR-transform, then PCA on the CLR coordinates (this is Aitchison-PCA); the loadings are interpretable as taxa.

```python
import pandas as pd
from skbio.stats.composition import clr, multi_replace   # renamed from multiplicative_replacement in skbio 0.6
from sklearn.decomposition import PCA

ab = pd.read_csv('merged_abundance.txt', sep='\t', index_col=0)
ab = ab[ab.index.str.contains(r'\|s__') & ~ab.index.str.contains(r'\|t__')]  # species rows only
proportions = (ab.T.values / ab.T.values.sum(axis=1, keepdims=True))
clr_mat = clr(multi_replace(proportions))                # zeros replaced, then CLR (NOT StandardScaler on relab)
pca = PCA(n_components=2).fit(clr_mat)
coords = pca.transform(clr_mat)
```

## Per-Method Failure Modes

### The transform/metric/rarefaction triad manufactures the result
**Trigger:** defaulting to Bray-Curtis PCoA and presenting it as "the" answer. **Mechanism:** metric, transform, and rarefaction each change the geometry. **Symptom:** separation that vanishes under Aitchison/RPCA, or appears only at one rarefaction depth. **Fix:** state the choice; show the conclusion survives a second reasonable choice; report % variance / stress.

### PERMANOVA dispersion confound
**Trigger:** "communities differed (adonis2 p<0.001)" with no dispersion check. **Mechanism:** pseudo-F responds to within-group spread, not only centroid location (unbalanced designs especially). **Symptom:** a "difference" that is really higher variability in one group. **Fix:** pair every adonis2 with betadisper + permutest; report both.

### Single-tool differential abundance
**Trigger:** reporting the DA tool that gives the prettiest story. **Mechanism:** tools disagree (Nearing 2022). **Symptom:** findings that do not replicate. **Fix:** consensus of >=2 compositional tools; intersect = confident; name them; BH-correct.

### Richness as biology
**Trigger:** plotting Observed/Chao1 from a k-mer classifier as diversity. **Mechanism:** richness tracks database size and false positives; estimators assume integer counts. **Symptom:** "richness" differences driven by depth/filtering; meaningless Chao1 on MetaPhlAn percentages. **Fix:** prefer Hill q=1/q=2; gate richness behind confidence filtering and unique-k-mer evidence.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Prevalence filter (e.g. present in >=10% of samples) | DA best practice | reduces multiple-testing and unstable zero-dominated taxa |
| BH FDR across taxa | standard | many taxa = many tests; report q-values |
| NMDS stress < 0.2 usable, < 0.1 good | Clarke 1993 *Aust J Ecol* 18:117 | above 0.2 the configuration is suspect |
| Hill q=0,1,2 reported together | Jost 2007; Chao 2014 | characterize the richness-evenness spectrum, not richness alone |
| Pair adonis2 with betadisper | Anderson & Walsh 2013 *Ecol Monogr* 83:557 | dispersion can masquerade as a location difference |
| Consensus of >=2 DA tools | Nearing 2022 *Nat Commun* 13:342 | single-tool hits do not replicate |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Chao1/Observed nonsensical | run on MetaPhlAn relative abundances | compute richness on Bracken counts only |
| PCA shows no compositional structure | StandardScaler on raw relab | CLR-transform first, then PCA (Aitchison-PCA) |
| "Significant" PERMANOVA challenged in review | no dispersion test | add betadisper + permutest |
| DA hits do not replicate | single tool, uncorrected test | >=2 compositional tools, BH correction |
| UniFrac errors on Bracken data | no phylogeny for NCBI taxonomy | UniFrac needs a tree (MetaPhlAn SGB tree only) |
| Krona flags rejected | version-fragile column flags | run `ktImportTaxonomy` with no args to confirm |

## References

- McMurdie PJ, Holmes S. 2013. phyloseq: an R package for reproducible interactive analysis and graphics of microbiome census data. *PLoS One* 8:e61217.
- Ondov BD, Bergman NH, Phillippy AM. 2011. Interactive metagenomic visualization in a web browser. *BMC Bioinformatics* 12:385.
- Gloor GB, Macklaim JM, Pawlowsky-Glahn V, Egozcue JJ. 2017. Microbiome datasets are compositional: and this is not optional. *Front Microbiol* 8:2224.
- Nearing JT, Douglas GM, Hayes MG, et al. 2022. Microbiome differential abundance methods produce different results across 38 datasets. *Nat Commun* 13:342.
- Anderson MJ, Walsh DCI. 2013. PERMANOVA, ANOSIM, and the Mantel test in the face of heterogeneous dispersions. *Ecol Monogr* 83:557-574.
- McMurdie PJ, Holmes S. 2014. Waste not, want not: why rarefying microbiome data is inadmissible. *PLoS Comput Biol* 10:e1003531.
- Schloss PD. 2024. Waste not, want not: revisiting the analysis that called into question the practice of rarefaction. *mSphere* 9:e00355-23.
- Fernandes AD, Reid JN, Macklaim JM, et al. 2014. Unifying the analysis of high-throughput sequencing datasets. *Microbiome* 2:15.
- Lin H, Peddada SD. 2020. Analysis of compositions of microbiomes with bias correction. *Nat Commun* 11:3514.
- Mallick H, Rahnavard A, McIver LJ, et al. 2021. Multivariable association discovery in population-scale meta-omics studies. *PLoS Comput Biol* 17:e1009442.
- Barnett DJM, Arts ICW, Penders J. 2021. microViz: an R package for microbiome data visualization and statistics. *J Open Source Softw* 6:3201.

## Related Skills

- metaphlan-profiling - Generates the relative-abundance table (with the SGB tree)
- kraken-classification - Generates Kraken/Bracken count input
- abundance-estimation - Compositional theory, normalization, and absolute load
- functional-profiling - HUMAnN function tables tested with the same DA logic
- microbiome/diversity-analysis - Amplicon/QIIME2 diversity and differential abundance for ASV input
- data-visualization/ggplot2-fundamentals - Generic plotting primitives
- workflows/metagenomics-pipeline - End-to-end shotgun analysis
<!-- END FILE: metagenomics/metagenome-visualization/SKILL.md -->

## 子目录：metagenomics/metaphlan-profiling

<!-- BEGIN FILE: metagenomics/metaphlan-profiling/SKILL.md -->
---
name: bio-metagenomics-metaphlan
description: Profiles shotgun metagenomes to species/SGB relative abundance with MetaPhlAn 4's clade-specific marker genes (bowtie2 short reads, minimap2 long reads). Covers why a MetaPhlAn percentage is a cell fraction (genome-size-normalized taxonomic abundance) and must never be merged with Kraken/Bracken read fractions, kSGB vs uSGB units for quantifying database-absent taxa, the unknown-fraction rescaling and its version-default flip, --index pinning as a batch variable, and when mOTUs3 or sourmash gather beat marker profiling. Use when profiling who-is-there with high precision, needing HMP-comparable species abundances, quantifying novel taxa, or deciding marker-gene vs k-mer profiling. For k-mer classification see kraken-classification; for strains see strain-tracking; for 16S amplicon see the microbiome category.
tool_type: cli
primary_tool: MetaPhlAn
---

## Version Compatibility

Reference examples tested with: MetaPhlAn 4.1+, Bowtie2 2.5.3+, minimap2 2.26+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `metaphlan --version` then `metaphlan --help` to confirm flag names and defaults
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The marker DATABASE version is the experimental variable. Results track the index (e.g. `mpa_vJun23_CHOCOPhlAnSGB_202403` vs the live `vJan25` build); MetaPhlAn 3 and MetaPhlAn 4 databases are not interchangeable. Pin `--index` and report it like a reagent lot. Two flags were renamed in 4.2: `--bowtie2out` -> `--mapout` and `--bowtie2db` -> `--db_dir` (the `--input_type` value `bowtie2out` likewise becomes `mapout`); unknown-fraction estimation flipped from opt-in (`--unclassified_estimation`) to on-by-default (`--skip_unclassified_estimation` to disable). Confirm against `metaphlan --help`.

# MetaPhlAn Profiling

**"Who is in my metagenome, by cell fraction?"** -> Detect which clades' private marker genes are present, average their per-marker coverage, and normalize to a genome-size-aware relative abundance - so the percentage is a fraction of cells, not of reads.
- CLI: `metaphlan reads_1.fq.gz,reads_2.fq.gz --input_type fastq --index mpa_vJun23_CHOCOPhlAnSGB_202403 -o profile.txt --mapout sample.bz2`

Scope: marker-gene species/SGB profiling and its alternatives (mOTUs3, sourmash gather). K-mer read classification -> kraken-classification. Strain-resolved SNV haplotypes -> strain-tracking. Functional profiling -> functional-profiling. Compositional stats and plotting -> metagenome-visualization. 16S amplicon -> the microbiome category.

## The Single Most Important Modern Insight -- A MetaPhlAn Percentage Is a Cell Fraction, Not a Read Fraction

A MetaPhlAn percentage estimates what fraction of the CELLS in the community belong to a clade - a genome-size-normalized taxonomic abundance. A Kraken/Bracken percentage estimates what fraction of the READS came from a clade - a sequence abundance. There is no sample-independent conversion between them, because sequence abundance under-estimates small-genome microbes and over-estimates large-genome ones by a factor that depends on the whole community's genome-size distribution (Sun 2021 *Nat Methods* 18:618). Therefore:

- Never merge MetaPhlAn percentages with Kraken/Bracken percentages into one table, correlate them, or benchmark one against the other. Disagreement between them is expected even when both are correct.
- Marker profiling is not "classify every read." It detects which clades' PRIVATE markers are present (default presence gate: reads cover roughly 20% of a clade's markers) and averages their per-marker coverage. Most reads are never assigned - by design, not failure.

Mnemonic: markers measure WHO is there (cells); k-mers measure HOW MUCH DNA is there (reads).

## SGBs: the Unit Is Species-Level, and uSGBs Quantify the Unnamed

MetaPhlAn 4's atomic taxon is the SGB (species-level genome bin, a ~95% ANI cluster), not an NCBI species. A kSGB contains a cultured reference genome and gets a Latin name; a uSGB is defined only from MAGs (>=5 required) and is reported with a placeholder ID and no name. Quantifying uSGBs - taxa with no reference genome - is MetaPhlAn 4's headline advance over MetaPhlAn 3 and explains ~20% more gut reads, >40% more in under-characterized environments (Blanco-Miguez 2023 *Nat Biotechnol* 41:1633). Consequences: an unnamed `t__SGB...` row is a real quantified taxon - do not drop it; one named species can split into several SGBs; MetaPhlAn 3 species profiles and MetaPhlAn 4 SGB profiles are not row-compatible (use `sgb_to_gtdb_profile.py` for GTDB names). The `t__` tier is the SGB, NOT a strain - strain resolution is StrainPhlAn (-> strain-tracking).

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| MetaPhlAn 4 | Blanco-Miguez 2023 *Nat Biotechnol* 41:1633 | ~189 clade-specific markers/SGB; robust coverage average | high-precision species/SGB %, HMP-comparable, characterized communities |
| mOTUs3 | Ruscheweyh 2022 *Microbiome* 10:212 | 10 universal single-copy marker genes | higher recall of novel/divergent taxa; transparent marker-hit confidence |
| sourmash gather | Pierce 2019 *F1000Res* 8:1006 | FracMinHash containment, minimum metagenome cover | genome-resolved hits vs all of GTDB + an honest unknown fraction |
| Kraken2 + Bracken | Wood 2019 *Genome Biol* 20:257 | k-mer LCA + Bayesian reestimation | -> kraken-classification; max recall, willing to filter false positives |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Human gut species %, low false positives, HMP-comparable | MetaPhlAn 4 | curated SGB markers; high precision; huge corpus |
| Quantify novel / database-absent taxa | MetaPhlAn 4 uSGBs OR mOTUs3 ext-mOTUs | reference-independent units |
| Maximize recall in under-characterized environments | mOTUs3 or sourmash gather | universal markers / containment vs everything |
| Genome-resolved + explicit unknown fraction | sourmash gather | minimum metagenome cover reports what is unexplained |
| Max recall of every read, speed | -> kraken-classification | k-mer LCA; filter the false-positive tail |
| Need cell fraction, not read fraction | MetaPhlAn / mOTUs | k-mer tools report read fraction |
| Strain-level resolution | -> strain-tracking | per-SNV haplotypes, not species profiling |
| Composition stats next | -> metagenome-visualization (CLR/ANCOM-BC) | output is closed; naive stats on percentages are invalid |

## Basic Profiling

```bash
# Paired-end reads are passed as ONE comma-separated argument (MetaPhlAn treats them as two
# single-end files - it does not use insert/pairing info). Pin the index for reproducibility.
metaphlan reads_R1.fastq.gz,reads_R2.fastq.gz \
    --input_type fastq \
    --index mpa_vJun23_CHOCOPhlAnSGB_202403 \   # pin it; DB version is a batch variable
    --nproc 8 \
    --mapout sample.map.bz2 \                    # cache the read->marker mapping (pre-4.2: --bowtie2out)
    --output_file profile.txt
```

## Re-Profile from the Mapping Cache (the real operational lever)

**Goal:** Try different analysis types, levels, or estimator settings without realigning.

**Approach:** Save the mapping once with `--mapout`, then re-run from it with `--input_type mapout` (pre-4.2: `bowtie2out`). Realignment is the expensive step; everything downstream is free.

```bash
metaphlan sample.map.bz2 --input_type mapout \
    --tax_lev s \           # k,p,c,o,f,g,s,t (t = SGB tier)
    --stat_q 0.2 \          # quantile-truncated robust mean of per-marker coverages: drop top/bottom 20%, average the middle 60%
    --output_file profile_species.txt
```

`--stat_q` down-weights markers in HGT/mobile and conserved cross-clade regions; the default 0.2 is a sensible robust mean. Changing it changes the reported abundances - report it if it is changed. Long reads (4.1+) route to minimap2 with `--long_reads`.

## The Unknown Fraction Rescales Everything

Relative abundance sums to 100% only over DETECTED clades. With unknown estimation OFF (pre-4.2 default), known taxa absorb 100% and the database-absent community is invisible - overstating every known taxon. With it ON (4.2 default), an `UNCLASSIFIED` row appears and every known abundance shrinks proportionally. In soil/marine/rumen the unknown fraction can be the largest "taxon" in the sample.

```bash
# 4.2 default includes the UNCLASSIFIED row. To force it on pre-4.2: --unclassified_estimation
# For SAM input, pass --nreads <total> or the unknown fraction is wrong.
metaphlan reads.fastq.gz --input_type fastq -o profile.txt   # 4.2: UNCLASSIFIED row present by default
```

Pre-4.2-default and 4.2-default outputs are not comparable abundances - mixing them is a hidden batch effect.

## Merge and Convert

```bash
# All inputs MUST come from the SAME database index or rows mismatch silently.
merge_metaphlan_tables.py profiles/*_profile.txt > merged_abundance.txt
sgb_to_gtdb_profile.py -i merged_abundance.txt -o merged_gtdb.txt   # recover GTDB names for SGBs
```

## Per-Method Failure Modes

### MetaPhlAn percentages merged with Kraken percentages
**Trigger:** putting MetaPhlAn and Bracken abundances in one matrix or correlating them. **Mechanism:** cell fraction vs read fraction - different quantities (Sun 2021). **Symptom:** "tools disagree," spurious scatter, broken ML/differential-abundance features. **Fix:** keep them separate; if harmonizing, convert via genome length (Bracken counts / genome length, renormalize) and accept it is approximate.

### Unknown-fraction default mismatch across samples
**Trigger:** profiles built with different MetaPhlAn versions or `--unclassified_estimation` settings. **Mechanism:** the UNCLASSIFIED row rescales all known abundances. **Symptom:** a batch effect aligned to processing date, not biology. **Fix:** pin one version and one unknown-estimation setting across the whole study; for environmental samples always include the unknown fraction.

### Treating a low mapping rate as a QC failure
**Trigger:** alarm at <1% of reads mapping. **Mechanism:** only clade-specific markers are targeted; low mapping is expected. **Symptom:** unnecessary re-runs. **Fix:** low mapping is normal; a large unknown fraction means database-absent community (consider mOTUs3/sourmash), and a very low rate plus low microbial yield suggests host contamination -> contamination-controls.

### Recall ceiling in under-characterized environments
**Trigger:** profiling soil/marine and reporting only named taxa. **Mechanism:** a marker tool is structurally blind to clades whose markers are not in the database (high precision, low recall; CAMI2 Meyer 2022). **Symptom:** most of the community missing; lowering thresholds does not recover it. **Fix:** use mOTUs3 (universal markers) or sourmash gather (containment vs all of GTDB), or accept Kraken false positives and filter - do not just lower MetaPhlAn thresholds and call it sensitivity.

### Index mismatch on merge
**Trigger:** merging profiles built on different `--index` builds. **Mechanism:** SGB IDs and marker sets differ between releases. **Symptom:** rows silently fail to align; abundances look implausible. **Fix:** rebuild all samples on one pinned index before merging.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Presence gate ~20% of an SGB's markers | Blanco-Miguez 2023 *Nat Biotechnol* 41:1633 | enough markers covered to call a clade present (precision mechanism) |
| `--stat_q` 0.2 default | MetaPhlAn docs | truncated mean drops top/bottom 20% of marker coverages; robust to HGT/conserved outliers |
| uSGB requires >=5 MAGs | Blanco-Miguez 2023 *Nat Biotechnol* 41:1633 | false-positive control for unnamed taxa |
| Pin `--index` | MetaPhlAn docs | DB version changes profiles for identical reads; report like a reagent lot |
| `--min_cu_len` 2000 | MetaPhlAn docs | minimum cumulative marker length to report a clade (low-evidence filter) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "No database found" | DB not installed | `metaphlan --install` (optionally `--index <ver> --db_dir DIR`) |
| Output all zeros | wrong `--input_type` or empty/host-only input | match `--input_type` to the file; check microbial yield |
| `--bowtie2out` not recognized | running MetaPhlAn 4.2+ | use `--mapout` / `--input_type mapout` (4.2 rename) |
| Rows mismatch after merge | profiles from different indices | rebuild on one pinned `--index` |
| SAM input unknown fraction wrong | `--nreads` not supplied | pass total read count with `--nreads` |
| Viral calls look unreliable | `--add_viruses` calls are low-confidence | treat vSGB calls cautiously (CAMI2) |

## References

- Blanco-Miguez A, Beghini F, Cumbo F, et al. 2023. Extending and improving metagenomic taxonomic profiling with uncharacterized species using MetaPhlAn 4. *Nat Biotechnol* 41:1633-1644.
- Beghini F, McIver LJ, Blanco-Miguez A, et al. 2021. Integrating taxonomic, functional, and strain-level profiling of diverse microbial communities with bioBakery 3. *eLife* 10:e65088.
- Sun Z, Huang S, Zhang M, et al. 2021. Challenges in benchmarking metagenomic profilers. *Nat Methods* 18:618-626.
- Meyer F, Fritz A, Deng ZL, et al. 2022. Critical Assessment of Metagenome Interpretation: the second round of challenges. *Nat Methods* 19:429-440.
- Ruscheweyh HJ, Milanese A, Paoli L, et al. 2022. Cultivation-independent genomes greatly expand taxonomic-profiling capabilities of mOTUs across various environments. *Microbiome* 10:212.
- Sunagawa S, Mende DR, Zeller G, et al. 2013. Metagenomic species profiling using universal phylogenetic marker genes. *Nat Methods* 10:1196-1199.
- Pierce NT, Irber L, Reiter T, Brooks P, Brown CT. 2019. Large-scale sequence comparisons with sourmash. *F1000Res* 8:1006.

## Related Skills

- kraken-classification - K-mer read classification; reports read fraction, not cell fraction
- abundance-estimation - Compositional handling and cross-tool abundance comparison
- strain-tracking - StrainPhlAn strain resolution below the SGB level
- functional-profiling - HUMAnN reuses a MetaPhlAn profile for its taxonomic prescreen
- metagenome-visualization - Compositional stats and plotting of profiles
- genome-assembly/metagenome-assembly - Recover the MAGs that define uSGBs; this category is read-based
- workflows/metagenomics-pipeline - End-to-end shotgun profiling
<!-- END FILE: metagenomics/metaphlan-profiling/SKILL.md -->

## 子目录：metagenomics/strain-tracking

<!-- BEGIN FILE: metagenomics/strain-tracking/SKILL.md -->
---
name: bio-metagenomics-strain-tracking
description: Resolves and compares bacterial strains below the species level from shotgun metagenomes with inStrain (popANI/conANI microdiversity), StrainPhlAn (marker-SNV consensus phylogeny and nGD), MIDAS2, metaSNV, and StrainGE, plus genome-vs-genome ANI (skani/fastANI/MASH) for isolate/MAG comparison. Covers why a strain is a threshold not a thing, why ANI answers same-genome while popANI/nGD answer same-population-in-situ, the 99.999% popANI and per-species nGD definitions, the coverage detection limit (absence is not absence), why sharing is not transmission direction, and mapping to the dataset's own dRep MAGs. Use when detecting shared strains, tracking transmission, resolving within-host strain dynamics, or deconvoluting co-occurring strains. For pure-culture isolate outbreak SNP trees see epidemiological-genomics; for MAG assembly see genome-assembly/metagenome-assembly.
tool_type: mixed
primary_tool: inStrain
---

## Version Compatibility

Reference examples tested with: inStrain 1.8+, StrainPhlAn/MetaPhlAn 4.1+, dRep 3.4+, skani 0.2+, Bowtie2 2.5+, samtools 1.19+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `inStrain profile -h`, `strainphlan -h`, `skani dist -h` to confirm flags and defaults
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The mapping REFERENCE defines the answer. Map to genomes present in the sample set (dRep-dereplicated MAGs from this dataset), not generic database genomes - a distant reference inflates apparent SNVs and corrupts popANI. Record the reference set, the popANI/nGD threshold, the minimum coverage and breadth, and the co-detection rate; the "strain" is defined by these, not by nature.

# Strain Tracking

**"Is the same strain in samples A and B?"** -> Compare per-position SNV populations (not consensus genomes) at adequate depth - because a strain is defined by the chosen threshold, and ANI cannot resolve the difference that matters.
- CLI: `inStrain profile sample.bam reps.fasta -o sample.IS -s reps.stb -p 8` then `inStrain compare`

Scope: in-situ strain resolution, sharing, and deconvolution from a community. Pure-culture isolate outbreak SNP/cgMLST trees -> epidemiological-genomics. MAG assembly/binning -> genome-assembly/metagenome-assembly. Species presence/abundance -> kraken-classification, metaphlan-profiling.

## The Single Most Important Modern Insight -- A Strain Is a Threshold, Not a Thing

There is no universal definition of a metagenomic strain. A strain is an operational construct fixed by the reference mapped to, the genome fraction comparable at adequate depth, and the cutoff drawn. inStrain's popANI >= 99.999% over >= 50% of the genome IS the strain definition; Valles-Colomer's per-species nGD threshold IS the strain definition. Changing the cutoff changes how many strains exist. Two corollaries:

1. **ANI answers "same genome?"; popANI/nGD answer "same population, in situ?"** Genome-to-genome ANI (MASH/skani/fastANI) saturates - two genuinely distinct, separately transmissible strains routinely share >99.9% ANI, and ANI's resolution floor sits above the difference that matters. Strain sharing cannot be done with an ANI number; it needs microdiversity-aware, position-level concordance.
2. **Detecting a shared strain is a narrow statement:** across the genome fraction both samples covered at >= 5x, their SNV populations were >= 99.999% concordant. That is not proof an organism was transmitted between two people - the threshold certifies genomic identity within a coverage window, nothing more.

## The Three Tasks (Do Not Conflate)

| Task | Question | Tools |
|------|----------|-------|
| Identification | which known reference strain is present? | StrainGST, sourmash gather, MIDAS |
| Tracking / sharing | is the SAME strain in samples A and B? | inStrain compare, StrainPhlAn, MIDAS2, metaSNV, SameStr |
| Deconvolution | how many strains coexist in ONE sample, what are their haplotypes? | DESMAN, Strainberry, strainFlye, Strainy |

Genome-to-genome ANI (MASH/skani/fastANI) is a fourth, orthogonal task - "are these two assembled genomes the same?" - isolate/MAG comparison and dereplication, NOT in-situ strain resolution.

## Tool Taxonomy

| Tool | Citation | Mechanism / role | When |
|------|----------|------------------|------|
| inStrain | Olm 2021 *Nat Biotechnol* 39:727 | popANI/conANI microdiversity from reads mapped to MAGs | the reference standard for shared-strain detection |
| StrainPhlAn | Truong 2017 *Genome Res* 27:626 | marker-SNV consensus -> phylogeny -> nGD | large cross-sample marker surveys, no assembly needed |
| MIDAS2 | Zhao 2023 *Bioinformatics* 39:btac713 | UHGG pan-genome SNV + gene CNV | accessory-genome strain signal at scale |
| StrainGE | van Dijk 2022 *Genome Biol* 23:74 | k-mer search + low-coverage variant calling | low-abundance strains down to 0.5x coverage |
| metaSNV v2 | Van Rossum 2022 *Bioinformatics* 38:1162 | SNV distances + subspecies clustering | subspecies structure across samples |
| skani | Shaw 2023 *Nat Methods* 20:1661 | sparse-chaining ANI | genome-vs-genome ANI; robust on fragmented MAGs (prefer over fastANI) |
| Strainberry / strainFlye | Vicedomini 2021 *Nat Commun* 12:4485; Fedarko 2022 *Genome Res* 32:2119 | long-read haplotype separation | deconvolute co-occurring strains (-> genome-assembly) |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Is a strain shared between two metagenomes? | inStrain compare (popANI) | microdiversity-aware; the field standard |
| Cross-sample transmission survey, many samples | StrainPhlAn (per-species nGD) | marker-based, scalable, no assembly |
| Low-abundance pathogen (< 1% / < 5x) | StrainGE | detects/compares down to 0.5x |
| Accessory-genome / pan-genome strain signal | MIDAS2 | adds gene-content axis SNV tools miss |
| Separate co-occurring strains into haplotypes | DESMAN (many samples) or long-read Strainberry/strainFlye | SNV tools do not partition a mixture |
| Compare two assembled genomes / dereplicate | skani (or fastANI) | genome-vs-genome ANI, not in-situ strains |
| Pure-culture isolate outbreak tree | -> epidemiological-genomics | cgMLST/SNP-distance on one genome per sample |

## inStrain: popANI vs conANI

**Goal:** Decide whether two metagenomes share a strain without being fooled by which allele happens to be the majority.

**Approach:** dRep the dataset's MAGs into representative genomes, map reads to the concatenated references, profile each sample, then compare on popANI (microdiversity-aware) over the co-covered genome fraction.

```bash
# 1. dRep -> representative genomes (97-99% ANI); concatenate; build scaffold-to-bin (.stb).
# 2. Map reads to the concatenated reps - your OWN MAGs, not database genomes.
bowtie2 -x reps -1 r1.fq.gz -2 r2.fq.gz | samtools sort -o sampleA.bam
inStrain profile sampleA.bam reps.fasta -o sampleA.IS -s reps.stb -g genes.fna -p 8
inStrain profile sampleB.bam reps.fasta -o sampleB.IS -s reps.stb -g genes.fna -p 8
inStrain compare -i sampleA.IS sampleB.IS -o compare.out -s reps.stb -p 8
```

conANI calls a difference whenever the consensus base differs - confounded by within-sample microdiversity (a minor-allele flip fakes a difference). popANI calls a difference only if the two samples share NO alleles at all, including minor ones, so popANI >= conANI always and is what detects shared strains consensus tools miss. Read genome-level calls from `genomeWide_compare.tsv` (breadth column `percent_compared`); the per-scaffold `comparisonsTable.tsv` uses `percent_genome_compared`.

## StrainPhlAn: Marker SNVs and nGD

```bash
metaphlan sample.fq.gz --input_type fastq -s sample.sam.bz2 --bowtie2out sample.bz2 -o profile.tsv  # need the SAM (-s)
sample2markers.py -i sams/*.sam.bz2 -o consensus_markers -n 8
extract_markers.py -c t__SGB1877 -o clade_markers/
strainphlan -s consensus_markers/*.json -m clade_markers/t__SGB1877.fna \
    -r reference_genomes/*.fna.bz2 -o output -c t__SGB1877 \
    --marker_in_n_samples_perc 80 --sample_with_n_markers 20 --nproc 8  # 4.0 named this --marker_in_n_samples
```

The output tree gives a pairwise nGD (normalized genetic distance). There is no universal nGD strain cutoff - derive a per-species threshold from the data (same-individual-different-timepoint pairs fall below it, unrelated pairs above), as in Valles-Colomer 2023. Low coverage means too few markers pass the filters and the sample is dropped from the species tree silently - so a missing shared-strain call is not evidence of no shared strain.

## Genome-vs-Genome ANI (Isolate/MAG Comparison, NOT In-Situ Strains)

```bash
skani dist genomeA.fasta genomeB.fasta   # prefer skani over fastANI: robust on fragmented MAGs
```

~95% ANI is the species boundary (Jain 2018 *Nat Commun* 9:5114). ANI saturates above that and cannot resolve same-vs-different strain - use it to compare isolates/MAGs and to dereplicate, never to call transmission.

## Per-Method Failure Modes

### ANI distance reported as strain resolution
**Trigger:** "MASH distance < 0.001 = same strain" or "fastANI > 99% = same strain." **Mechanism:** ANI operates on consensus genomes, saturates above 99.9%, and ignores microdiversity. **Symptom:** distinct transmissible strains called identical; transmission inferred from an ANI number. **Fix:** use ANI for isolate/MAG comparison; use inStrain popANI / StrainPhlAn nGD for strain sharing.

### Coverage detection limit (absence is not absence)
**Trigger:** concluding "no transmission" or "strain turnover." **Mechanism:** a shared strain can only be called for a species detected at adequate depth in BOTH samples (inStrain >= 5x and >= 50% breadth; StrainPhlAn enough markers). **Symptom:** a coverage dropout misread as biological absence; sharing rates biased to abundant taxa. **Fix:** report co-detection rates alongside sharing rates; use StrainGE for low-abundance targets.

### Sharing read as transmission direction
**Trigger:** narrating "A infected B." **Mechanism:** a shared strain is an undirected edge. **Symptom:** directionality claimed from one cross-sectional comparison. **Fix:** direction comes from timepoints, contact metadata, or a known index case - the published landscapes infer it from study design, not the genomic comparison.

### Wrong reference genome
**Trigger:** mapping to a generic database genome. **Mechanism:** a distant reference inflates apparent SNVs. **Symptom:** corrupted popANI; spurious differences. **Fix:** map to dRep-dereplicated MAGs from the sample set.

### Asking a SNV tool to deconvolute a mixture
**Trigger:** "what are the two strains here?" from inStrain. **Mechanism:** SNV/marker tools characterize population diversity; they do not partition it into haplotypes. **Symptom:** a category error. **Fix:** use DESMAN (many samples) or long-read Strainberry/strainFlye/Strainy for haplotype separation.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| popANI >= 99.999% same strain | Olm 2021 *Nat Biotechnol* 39:727 | empirical shared-strain cutoff; IS the operational definition |
| percent_compared >= 50% (genome-level breadth) | Olm 2021 *Nat Biotechnol* 39:727 | a genome below 50% breadth is not confidently present |
| min_cov 5x | Olm 2021 *Nat Biotechnol* 39:727 | lowest coverage at which sub-50% minor alleles are reliable |
| StrainGE detection ~0.5x | van Dijk 2022 *Genome Biol* 23:74 | tracks low-abundance strains below the inStrain floor |
| Per-species nGD threshold (derive it) | Valles-Colomer 2023 *Nature* 614:125 | no universal cutoff; separate within-host timepoints from unrelated |
| ~95% ANI species boundary | Jain 2018 *Nat Commun* 9:5114 | ANI saturates above this; cannot resolve strains |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Everything looks like one strain | ANI/MASH used for strain calls | switch to inStrain popANI / StrainPhlAn nGD |
| Sample missing from the StrainPhlAn tree | too few markers passed filters at low coverage | report co-detection; do not read absence as no-sharing |
| popANI implausibly low across the board | mapped to a distant database reference | map to dRep MAGs from the dataset |
| inStrain compare gives no genomes | < 50% breadth or < 5x in one sample | deepen sequencing or use StrainGE for that taxon |
| "Who infected whom" asked of one timepoint | sharing is undirected | need longitudinal/epi design for direction |

## References

- Olm MR, Crits-Christoph A, Bouma-Gregson K, et al. 2021. inStrain profiles population microdiversity from metagenomic data and sensitively detects shared microbial strains. *Nat Biotechnol* 39:727-736.
- Truong DT, Tett A, Pasolli E, Huttenhower C, Segata N. 2017. Microbial strain-level population structure and genetic diversity from metagenomes. *Genome Res* 27:626-638.
- Zhao C, Dimitrov B, Goldman M, Nayfach S, Pollard KS. 2023. MIDAS2: Metagenomic Intra-species Diversity Analysis System. *Bioinformatics* 39:btac713.
- Van Rossum T, Costea PI, Paoli L, et al. 2022. metaSNV v2: detection of SNVs and subspecies in prokaryotic metagenomes. *Bioinformatics* 38:1162-1164.
- van Dijk LR, Walker BJ, Straub TJ, et al. 2022. StrainGE: a toolkit to track and characterize low-abundance strains in complex microbial communities. *Genome Biol* 23:74.
- Vicedomini R, Quince C, Darling AE, Chikhi R. 2021. Strainberry: automated strain separation in low-complexity metagenomes using long reads. *Nat Commun* 12:4485.
- Valles-Colomer M, Blanco-Miguez A, Manghi P, et al. 2023. The person-to-person transmission landscape of the gut and oral microbiomes. *Nature* 614:125-135.
- Shaw J, Yu YW. 2023. Fast and robust metagenomic sequence comparison through sparse chaining with skani. *Nat Methods* 20:1661-1665.
- Jain C, Rodriguez-R LM, Phillippy AM, Konstantinidis KT, Aluru S. 2018. High throughput ANI analysis of 90K prokaryotic genomes reveals clear species boundaries. *Nat Commun* 9:5114.

## Related Skills

- metaphlan-profiling - StrainPhlAn builds on MetaPhlAn markers; profile species first
- kraken-classification - Species presence before strain resolution
- genome-assembly/metagenome-assembly - dRep MAGs to map against; long-read deconvolution
- epidemiological-genomics/amr-surveillance - Isolate outbreak SNP/cgMLST trees from pure cultures
- workflows/metagenomics-pipeline - End-to-end shotgun analysis
<!-- END FILE: metagenomics/strain-tracking/SKILL.md -->

<!-- END CATEGORY: metagenomics -->

