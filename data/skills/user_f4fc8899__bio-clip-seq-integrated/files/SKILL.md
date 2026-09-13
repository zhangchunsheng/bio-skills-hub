---
slug: bio-clip-seq-integrated
version: 1.0.1
displayName: "CLIP-seq分析 / CLIP-seq analysis"
name: bio-clip-seq-integrated
summary: "中文：CLIP-seq分析综合技能，整合 12 个相关专题，覆盖CLIP-seq分析：eCLIP/iCLIP/PAR-CLIP预处理、peak调用、crosslink位点检测、motif分析。 English: Integrated CLIP-seq analysis skill covering 12 related topics, including CLIP-seq analysis: eCLIP/iCLIP/PAR-CLIP preprocessing, peak calling, crosslink site detection, motif analysis."
description: "中文：这是一个面向CLIP-seq分析的综合生物信息学 Skill，整合当前分类下 12 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：CLIP-seq分析：eCLIP/iCLIP/PAR-CLIP预处理、peak调用、crosslink位点检测、motif分析。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：CLIPper, ChIPseeker, DEWSeq。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for CLIP-seq analysis, combining 12 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers CLIP-seq analysis: eCLIP/iCLIP/PAR-CLIP preprocessing, peak calling, crosslink site detection, motif analysis. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: CLIPper, ChIPseeker, DEWSeq. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# clip-seq 分类 Skill 整合版

> 本文件整合同一主分类目录下 12 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: clip-seq -->

## 子目录：clip-seq/ago-clip-mirna-targets

<!-- BEGIN FILE: clip-seq/ago-clip-mirna-targets/SKILL.md -->
---
name: bio-clip-seq-ago-clip-mirna-targets
description: Identify direct miRNA-target interactions from AGO HITS-CLIP, AGO-CLEAR-CLIP (chimeric reads), HEAP (Halo-Ago2 mouse), chimeric eCLIP / miR-eCLIP (deep miRNA-target profiling), or CLASH using chimeric-read processing pipelines, seed-pairing analysis, and 3' auxiliary pairing rules. Use when distinguishing direct miRNA targets from indirect, integrating CLIP-derived target maps with TargetScan / miRDB / DIANA predictions, applying canonical 7mer-8mer seed matching with 3' UTR context, or recovering miRNA-mRNA chimeras at scale.
tool_type: mixed
primary_tool: chimeric-eCLIP
---

## Version Compatibility

Reference examples tested with: eCLIP pipeline (Yeo lab), chimeric eCLIP analysis scripts (Yeo lab), HEAP pipeline (Li 2020), Hyb pipeline (Travis 2014), TargetScanHuman 8.0, miRDB 6.0, samtools 1.19+, bedtools 2.31+, pyHyb 0.4+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed package and adapt the example to match the actual API rather than retrying.

# AGO-CLIP and miRNA Target Identification

**"Identify direct miRNA-target interactions experimentally"** -> Use Argonaute (AGO1-4) CLIP-seq variants to map miRNA-binding sites on mRNAs, then resolve which miRNA pairs with each site. Three approaches: (a) standard AGO-CLIP recovers AGO-bound sites but cannot say which miRNA; (b) chimeric methods (CLEAR-CLIP, chimeric eCLIP / miR-eCLIP) ligate the miRNA to its target during library prep, producing miRNA-mRNA chimeric reads that unambiguously assign miRNA-target pairs; (c) HEAP uses HaloTag-Ago2 for in vivo profiling. The chimeric methods are the gold standard for direct miRNA-target identification; standard AGO-CLIP must be combined with computational seed-matching (TargetScan, miRDB) to infer miRNA pairing. Resolution: chimeric reads pinpoint single miRNA-target pairs; AGO-only CLIP identifies "AGO-binding sites" of which a subset are miRNA targets.

- CLI (chimeric eCLIP / miR-eCLIP processing): custom pipeline starting from eCLIP-style preprocessing + chimeric-read identification + miRNA-mRNA junction extraction
- CLI (CLEAR-CLIP custom Moore 2015 pipeline): Hyb (Travis 2014) for chimera analysis
- CLI (Hyb pipeline): `hyb run_hyb peaks.bam mature_miRNA.fa human.tab.gz` to find miRNA-mRNA chimeras
- CLI (HEAP analysis): standard HITS-CLIP processing pipeline + Halo-Ago2 capture details
- Python (seed-pairing analysis on AGO CLIP peaks): scan peaks for canonical 7mer-m8, 7mer-1A, 8mer, 6mer seeds + 3' UTR position + miRNA expression filter

The Yeo lab miR-eCLIP / chimeric eCLIP is the modern depth-improved version of chimeric AGO-CLIP, enriching for chimeras of specific miRNAs of interest via PCR or on-bead probe capture. For comprehensive miRNA-target mapping, miR-eCLIP combined with eCLIP-seq-style normalization is the state-of-the-art.

## Methods Taxonomy

| Method | Year | miRNA-target pairing | Chimera enrichment | Strength | Fails when |
|--------|------|---------------------|--------------------|----------|------------|
| HITS-CLIP for AGO | 2009 (Chi) | Indirect (computational seed) | None | Original; widely cited | Cannot assign miRNA without computational prediction |
| PAR-CLIP for AGO | 2010 (Hafner) | Indirect | None | T->C signature at CL position | Restricted to 4SU-permissive cells |
| AGO-CLEAR-CLIP (Moore 2015) | 2015 | Direct (chimera) | None (incidental) | First direct miRNA-target chimera method | Chimeric reads only 1-5% of library; deep sequencing needed |
| CLASH (Helwak 2013) | 2013 | Direct (chimera) | None | First general chimera method; pan-Argonaute | Lower chimera rate than CLEAR-CLIP |
| HEAP (Li 2020) | 2020 | Indirect (with chimeric step) | None | HaloTag-Ago2 in vivo mouse strain | Mouse only; requires transgenic model |
| chimeric eCLIP / miR-eCLIP | 2022 | Direct (chimera) | Probe/PCR enriched | Deepest miRNA-target chimera profiling | Specialized library prep |
| AGO-IP-microarray (Karginov 2007) | 2007 | Indirect | None | Earliest; predecessor of CLIP for AGO | No crosslinking; misses transient targets |

Methodology evolves; verify the current chimeric eCLIP / miR-eCLIP literature for best practice. As of 2024, miR-eCLIP is the canonical approach for deep miRNA-target profiling.

## Critical Choice: Chimeric vs Computational miRNA-Target Pairing

Two fundamentally different strategies:

**Chimeric methods (CLEAR-CLIP, chimeric eCLIP / miR-eCLIP, CLASH):** During library prep, a ligation step covalently joins the miRNA to its target mRNA, producing chimeric reads (miRNA at 5' + target mRNA at 3'). The miRNA-target pair is read directly from the sequence. Pro: direct evidence of binding interaction; no inference. Con: chimera rate is 1-5% of library by default (substantially enriched with miR-eCLIP probe capture for specific miRNAs); deep sequencing or enrichment needed.

**Computational pairing (HITS-CLIP / PAR-CLIP + seed-matching):** Standard AGO CLIP identifies AGO-bound peaks; downstream computational scanning matches each peak against canonical miRNA seeds (7mer-m8, 7mer-1A, 8mer) from TargetScan, miRDB, or DIANA databases. Pro: any AGO CLIP data can be analyzed; no special library prep. Con: indirect; assigns miRNAs based on canonical seed rules, missing non-canonical interactions (3' compensatory, central pairing).

The CLEAR-CLIP analysis (Darnell lab, Moore 2015) revealed substantial 3' auxiliary pairing beyond canonical seeds: many miRNA-target interactions have weak or non-canonical seed matching but strong 3' supplementary pairing. Chimeric methods recover these; computational seed-only inference misses them.

| Goal | Method |
|------|--------|
| Direct miRNA-target pair identification | Chimeric eCLIP / miR-eCLIP |
| Specific miRNA's targets (deep) | miR-eCLIP with probe-capture enrichment |
| All AGO-binding sites (any miRNA) | Standard AGO eCLIP / HITS-CLIP |
| In vivo mouse tissue | HEAP (Halo-Ago2 mouse) |
| Pan-Argonaute interactome | CLASH or chimeric eCLIP |
| Initial discovery / cost-conscious | AGO HITS-CLIP + TargetScan |
| Non-canonical / 3'-compensatory miRNA pairing | Chimeric methods (CLEAR-CLIP) |
| Comparison across species | TargetScan + AGO HITS-CLIP (computational) |
| Validate specific miRNA-target prediction | miR-eCLIP with that miRNA's probe |

## miRNA-Target Pairing Rules

Computational seed-matching against TargetScan / miRDB requires understanding the canonical miRNA-target pairing rules:

| Seed type | Pairing positions (miRNA nt) | Position 1 | Pro / Con |
|-----------|-------------------------------|------------|-----------|
| 8mer | 2-7 + position 8 + A at position 1 | A required | Strongest; most conserved targets |
| 7mer-m8 | 2-7 + position 8 (no A1 requirement) | Any | Strong; common |
| 7mer-A1 | 2-7 (no position 8) + A at position 1 | A required | Moderate; common |
| 6mer | 2-7 | Any | Weak; very common (many false positives) |
| 6mer-A1 | 2-6 + A at position 1 | A required | Weak |
| 3'-compensatory | Weak 6mer + strong 3' UTR pairing 12-17 | Any | Discovered via CLEAR-CLIP; misses in seed-only methods |
| Central pairing | Positions 4-15 with no seed | Any | Rare; cleavage rather than translational repression |

For TargetScan integration: download the TargetScanHuman 8.0 conserved-site predictions; filter for 7mer-8mer (drop 6mer if too noisy); cross-reference with the CLIP peak BED of the analysis.

## Chimeric eCLIP / miR-eCLIP Workflow

**Goal:** Recover miRNA-mRNA chimeras from AGO chimeric eCLIP / miR-eCLIP libraries and produce a per-miRNA target list suitable for direct biological interpretation.

**Approach:** Apply eCLIP-style preprocessing, then run Hyb in chimera (`type=mim`) mode with bowtie2 alignment (required for short 21-23 nt miRNA sequences), filter chimeras to human mRNA targets, intersect with miRNA-expression atlas (filter > 100 TPM in matched cell type), and validate top targets against TargetScan conserved 7mer-m8 / 8mer predictions.

```bash
# Step 1: eCLIP-style preprocessing (see clip-seq/clip-preprocessing)
umi_tools extract --bc-pattern=NNNNNNNNNN \
    --stdin=R1.fq.gz --read2-in=R2.fq.gz \
    --stdout=R1.umi.fq.gz --read2-out=R2.umi.fq.gz

cutadapt -a AGATCGGAAGAGCACACGTCT -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT \
    -q 6 -m 18 -o R1.trim.fq.gz -p R2.trim.fq.gz \
    R1.umi.fq.gz R2.umi.fq.gz

# Step 2: Chimera-specific alignment
# Chimeric reads have miRNA sequence (21-23 nt) at 5' followed by target mRNA
# Step 2a: Trim 5' for miRNA portion + align miRNA part
# Step 2b: Trim 3' for target mRNA portion + align target part
# Use custom chimeric-eCLIP pipeline OR Hyb (Travis 2014)

# Hyb pipeline approach (CLEAR-CLIP and chimeric methods)
hyb \
    in=R1.trim.fq.gz \
    db=miRNA_and_human_mRNA.fa \
    align=blastall \
    type=mim   # multimer (miRNA-target) chimera mode

# Output: .blast and .hyb files with miRNA-mRNA chimera coordinates

# Step 3: Filter chimeras by miRNA + target alignment quality
# Hyb reports each chimera as: miRNA_id  target_id  miRNA_alignment  target_alignment
# Filter for:
#   - miRNA portion 18-25 nt
#   - Target portion 18-50 nt
#   - miRNA-target seed match (7mer-m8 / 7mer-A1 / 8mer)
#   - Target alignment unique
awk '$5 == "human_mRNA"' chimeras.hyb > chimeras_human_mRNA.tsv

# Step 4: Aggregate chimeras into per-miRNA target list
# Each miRNA -> targets (with read counts as binding affinity proxy)
awk '{print $3, $4}' chimeras_human_mRNA.tsv | sort | uniq -c | sort -rn > mirna_target_counts.tsv
```

## CLEAR-CLIP (Moore 2015) Analysis

CLEAR-CLIP was the first method to recover ~130k miRNA-target chimeras from mouse brain (Moore 2015). The analytical insight: AGO-CLIP reads ligated together during library prep produce chimeric reads at low rates that contain unambiguous miRNA-target pairs.

```bash
# CLEAR-CLIP analysis uses the Hyb pipeline (Travis 2014)
# Pre-requisite: AGO HITS-CLIP / PAR-CLIP BAM

# Extract candidate chimeric reads (reads that don't fully align to human mRNA)
samtools view -h dedup.bam | awk '$6 ~ /S/' | wc -l   # soft-clipped reads candidate chimeras

# Run Hyb in chimera mode
hyb \
    in=R1.trim.fq.gz \
    db=mature_miRNA_plus_human_mRNA.fa \
    align=blastall \
    type=mim

# Filter for canonical seed match
python analyze_chimeras.py \
    --chimeras chimeras.hyb \
    --mirna_db mature_human_miRNA.fa \
    --seed_types 7mer-m8 7mer-A1 8mer \
    --output validated_chimeras.tsv
```

## miR-eCLIP Probe Enrichment

To recover deep coverage of one or a few miRNAs' targets, miR-eCLIP uses probe-based or PCR-based enrichment to amplify chimeras containing specific miRNAs.

```bash
# After chimera identification, filter for specific miRNA
# Example: enrich for hsa-miR-21 targets
grep "hsa-miR-21" chimeras_human_mRNA.tsv > mir21_targets.tsv

# Count unique target sites per miRNA
awk '{print $3}' mir21_targets.tsv | sort -u | wc -l

# Cross-reference with TargetScan conserved predictions for validation
bedtools intersect -wa -wb \
    -a mir21_targets_3utr_coords.bed \
    -b targetscan_mir21_conserved_targets.bed > mir21_validated_targets.bed
```

## Per-Method Failure Modes

### Standard AGO-CLIP -- Cannot assign miRNA

**Trigger:** Standard AGO eCLIP / HITS-CLIP run; user wants per-miRNA target list.

**Mechanism:** Standard AGO-CLIP enriches for AGO-bound RNAs but does not retain miRNA identity. Computational seed-matching infers which miRNAs are likely bound but each peak gets matched to dozens of candidate miRNAs.

**Symptom:** Peak BED has 100k peaks; seed-matching assigns 10-50 candidate miRNAs per peak.

**Fix:** Switch to chimeric method for direct pairing, OR filter computational predictions by miRNA expression in the same cell type (only consider miRNAs > 100 TPM in matched small-RNA-seq).

### Chimeric methods -- Low chimera rate

**Trigger:** Standard chimeric eCLIP without probe enrichment; expecting deep per-miRNA targets.

**Mechanism:** Chimeras are 1-5% of total reads in standard chimeric eCLIP. For a 30M-read library, only 300k-1.5M chimeras; distributed across 200+ miRNAs gives only ~5000-15000 per miRNA.

**Symptom:** Per-miRNA target count is sparse; rare miRNAs have < 100 chimeras.

**Fix:** Use miR-eCLIP with probe enrichment for specific miRNAs of interest (substantial boost). Or sequence ultra-deep (200M+ reads) for global chimera profiling.

### Hyb -- BLAST sensitivity vs miRNA length

**Trigger:** miRNA sequences (21-23 nt) too short for BLAST default sensitivity.

**Mechanism:** BLAST defaults need >= 100 nt for reliable alignment. miRNA 21-23 nt hits below threshold; many true chimeras lost.

**Symptom:** Hyb returns few chimeras; rerun with `align=bowtie2` gives more.

**Fix:** Use bowtie2 mode for miRNA alignment (`hyb align=bowtie2 type=mim`); short-read aligners are designed for short sequences.

### Computational seed matching -- High false positive

**Trigger:** TargetScan predictions used as ground truth without CLIP validation.

**Mechanism:** TargetScan reports all potential 7mer-m8 / 8mer matches in 3' UTRs; many sites are not functional miRNA targets (no AGO binding observed).

**Symptom:** TargetScan predicts thousands of targets per miRNA; only a fraction are validated by CLIP.

**Fix:** Use CLIP overlap as the validation: TargetScan prediction AND AGO-CLIP peak = high-confidence target. Sites in TargetScan but not in CLIP = unfunctional predictions.

### Non-canonical miRNA-target pairing missed

**Trigger:** Seed-matching only; 3' compensatory pairing missed.

**Mechanism:** A substantial fraction of miRNA-target interactions have weak seeds but strong 3' UTR pairing (positions 12-17). Seed-only matching loses these.

**Symptom:** Chimeric methods find targets that TargetScan misses; these have weak seeds.

**Fix:** Accept chimeric method's targets even with weak seeds (the chimera IS the evidence). Or use TargetScan + RNAhybrid (full miRNA-target duplex prediction) for non-canonical sites.

### HEAP -- Mouse-only

**Trigger:** Want HEAP-style in vivo AGO profiling in human tissue.

**Mechanism:** HEAP uses a transgenic mouse with Halo-Ago2 allele; not available in human or other species.

**Symptom:** Cannot replicate HEAP results in human.

**Fix:** Use eCLIP / chimeric eCLIP on human samples; HEAP is specifically for mouse tissue studies.

### miRNA expression filter forgotten

**Trigger:** Computational miRNA-target assignment without filtering by miRNA expression.

**Mechanism:** Many miRNA databases include rare or developmental-specific miRNAs. If the miRNA is not expressed in the cell type, it cannot bind anything.

**Symptom:** Per-miRNA target lists include miRNAs at < 1 TPM expression - implausible binding.

**Fix:** Cross-reference with matched small-RNA-seq from the same cell type; filter for miRNAs > 100 TPM. ENCODE-validated cell types have published miRNA atlases.

## Decision Tree by Use Case

| Scenario | Method | Why |
|----------|--------|-----|
| Direct miRNA-target identification, modern | chimeric eCLIP / miR-eCLIP | Direct chimeras; deep enrichment available |
| Specific miRNA's deep target list | miR-eCLIP with probe for that miRNA | probe-based enrichment |
| Discover novel miRNA-target interactions | CLEAR-CLIP or chimeric eCLIP | Direct chimera, no seed prior |
| In vivo mouse tissue | HEAP (Halo-Ago2 mouse) | Mouse only |
| Initial AGO-binding site discovery | AGO HITS-CLIP / eCLIP | Cost-effective; no chimera |
| Compare miRNA targets across species | TargetScan + AGO HITS-CLIP each species | Computational + experimental |
| 3' compensatory / non-canonical | CLEAR-CLIP / chimeric eCLIP | Direct chimera captures non-canonical |
| miRNA-perturbation effects | KD/KO + AGO-CLIP + differential | See clip-seq/differential-clip |
| Cross-tissue miRNA profiling | AGO eCLIP each tissue | Tissue-specific cell-type |
| Validate single miRNA prediction | miR-eCLIP with that miRNA's probe | Direct experimental confirmation |

## Reconciliation: AGO-CLIP vs TargetScan vs Chimeric

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Chimera method finds targets TargetScan does not | Non-canonical / 3'-compensatory pairing | Trust chimera; novel target |
| TargetScan predicts; AGO eCLIP peak present; no chimera | Functional target without chimera in library | Likely real target; chimera capture stochastic |
| TargetScan predicts; no AGO eCLIP peak | Computational false positive | Not a functional target |
| AGO eCLIP peak; no TargetScan match | Non-canonical or rare miRNA seed | Investigate; may be 3' compensatory |
| Per-miRNA target counts vary 100x across miRNAs | miRNA expression varies | Filter by matched small-RNA-seq |
| Hyb chimeras 1% of library | Standard rate | Enrich with miR-eCLIP if needed |
| Different chimera tools give different counts | Algorithm sensitivity differs | Hyb is the most-cited; use it for canonical |
| HEAP and eCLIP discordant | Mouse vs human; in vivo vs cell line | Both correct in their context |
| miR-eCLIP enriched chimera count not 30x baseline | Probe inefficient | Verify probe design; use multiple probes per miRNA |

**Operational rule:** For publication-grade miRNA-target list: (a) chimeric eCLIP / miR-eCLIP for direct pairing; (b) cross-reference with TargetScan conserved predictions; (c) filter by miRNA expression > 100 TPM in matched small-RNA-seq; (d) validate top targets with reporter assay (luciferase / GFP fusion with target 3' UTR).

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Hyb returns few chimeras | BLAST too stringent for short miRNAs | Use bowtie2 mode (`hyb align=bowtie2`) |
| Per-miRNA target list sparse | Low chimera rate without enrichment | Use miR-eCLIP probe enrichment |
| TargetScan predicts thousands per miRNA | No CLIP filter | Require CLIP peak overlap for high-confidence |
| miRNA assignments dominate by unexpressed miRNAs | No expression filter | Filter by matched small-RNA-seq > 100 TPM |
| Non-canonical sites missed | Seed-only matching | Use chimeric methods; or RNAhybrid full duplex |
| HEAP results don't replicate in human | Mouse-specific transgenic | Use eCLIP / chimeric eCLIP in human |
| 6mer matches dominate target list | Most weak seeds | Restrict to 7mer-m8 / 8mer; report 6mer separately |
| miRNA target chimeras unstrand-resolved | Strand information lost | Check BED column 6 throughout pipeline |
| Cross-tissue comparison naive | Tissue-specific miRNA expression | Match tissue-specific miRNA atlases |
| miR-eCLIP enrichment fails | Probe non-specific or low-affinity | Design multiple probes per miRNA; validate enrichment |

## References

- Chi SW et al 2009 Nature 460:479 (AGO HITS-CLIP)
- Hafner M et al 2010 Cell 141:129 (PAR-CLIP for AGO)
- Helwak A et al 2013 Cell 153:654 (CLASH; chimera method)
- Travis AJ et al 2014 Methods 65:263 (Hyb pipeline)
- Moore MJ et al 2015 Nat Commun 6:8864 (CLEAR-CLIP, 130k chimeras mouse brain)
- Li X et al 2020 Mol Cell 79:167 (HEAP, Halo-Ago2 in vivo mouse)
- Agarwal V et al 2015 eLife 4:e05005 (TargetScan 7.0)
- Lewis BP et al 2003 Cell 115:787 (original 7mer/8mer seed rules)
- Bartel DP 2018 Cell 173:20 (miRNA target principles)
- McGeary SE et al 2019 Science 366:eaav1741 (TargetScan 8.0 / quantitative target prediction).

## Related Skills

- clip-seq/clip-peak-calling - AGO CLIP peak calls
- clip-seq/binding-site-annotation - 3' UTR annotation
- clip-seq/clip-motif-analysis - Seed motif scan
- clip-seq/differential-clip - miRNA perturbation experiments
- clip-seq/m6a-clip - DART-seq uses similar APOBEC1 fusion
- small-rna-seq/target-prediction - TargetScan / miRDB / DIANA
- small-rna-seq/differential-mirna - miRNA expression
- small-rna-seq/mirdeep2-analysis - miRNA discovery
<!-- END FILE: clip-seq/ago-clip-mirna-targets/SKILL.md -->

## 子目录：clip-seq/binding-site-annotation

<!-- BEGIN FILE: clip-seq/binding-site-annotation/SKILL.md -->
---
name: bio-clip-seq-binding-site-annotation
description: Annotate CLIP-seq peaks or crosslink sites to RNA features (5'UTR, CDS, 3'UTR, intron, splice junction, snoRNA, tRNA, ncRNA, repeat elements) with ChIPseeker, RCAS, RBP-Maps (Yeo splicing regulatory maps), and bedtools, applying feature-priority hierarchies, transcript-context resolution, and metagene aggregation. Use when characterizing where in transcripts an RBP binds, comparing peak distribution across regions, generating splicing-regulatory maps relative to alternative-splicing events, or distinguishing exonic vs intronic vs UTR binding.
tool_type: mixed
primary_tool: ChIPseeker
---

## Version Compatibility

Reference examples tested with: ChIPseeker 1.40+, RCAS 1.30+, GenomicFeatures 1.56+, GenomicRanges 1.56+, rbp-maps (Yeo github), bedtools 2.31+, pybedtools 0.10+, pyranges 0.0.129+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed package and adapt the example to match the actual API rather than retrying. ChIPseeker 1.40+ changed the priority defaults; verify the priority vector before pipelining.

# Binding Site Annotation

**"Annotate where in transcripts my RBP binds"** -> Map CLIP peaks or single-nucleotide crosslink sites to RNA features and report the per-feature distribution. The interpretation is RBP-class-specific: splicing factors (PTBP1, U2AF2, RBFOX) bind intron-exon junctions; mRNA-stability regulators (HuR, PUM2) bind 3' UTRs; translation factors (EIF3J, RPS19) bind 5' UTRs and CDS; and small-ncRNA-binding RBPs (NSUN2 tRNAs, LARP7 7SK, TROVE2 Y-RNAs) bind specific non-coding transcripts. A correct annotation pipeline (a) resolves overlapping features by priority, (b) preserves transcript-isoform context, (c) generates metagene distributions, and (d) flags repeat-element overlap separately.

- R (peak-level, fast): `ChIPseeker::annotatePeak(peaks, TxDb=txdb, level='gene', tssRegion=c(-100,100))` then `plotAnnoPie(anno)`
- R (transcript-level with RNA-specific regions): RCAS `runReport(queryRegions=peaks, gffData=gencode_gtf, genomeVersion='hg38')`
- CLI (regions only): `bedtools intersect -s -wa -wb -a peaks.bed -b features.bed` (manual hierarchy)
- R (splicing-regulatory map for splice factors): RBP-Maps (`yeolab/rbp-maps`) generates the 1400 nt vectorized cassette-exon map used in Yeo lab ENCODE papers
- CLI (metagene aggregation): `deepTools computeMatrix` or RSeQC `geneBody_coverage.py` for read profiles

The Yeo lab convention for ENCODE eCLIP: ChIPseeker for global region distribution + RBP-Maps for position-resolved splicing context + custom analysis for repeat-element overlap. ChIPseeker alone over-counts intronic binding because TSS-region default extends too far for RNA features.

## Algorithmic Taxonomy

| Tool | Input | Annotation level | Feature priority | Output | Strength | Fails when |
|------|-------|------------------|------------------|--------|----------|------------|
| ChIPseeker (R) | Peak BED + TxDb | Gene-level or transcript-level | Promoter > 5' UTR > 3' UTR > Exon > Intron > Intergenic | Per-peak annotation + pie chart + distance-to-TSS | Mature, widely used, fast | TSS-region default `c(-3000, 3000)` over-extends; promoter category meaningless for RNA |
| RCAS (R) | Peak BED + GFF | Transcript-level | Customizable | HTML report + per-region table | RNA-specific design; ncRNA-aware | Slow; HTML-heavy; less actively maintained |
| RBP-Maps (Yeo) | eCLIP BAM + alternative splicing event tables | Splice junction-level | NA (positional metagene) | Splicing regulatory map (1400nt vector around cassette exon) | The standard for splicing-factor CLIP analysis | Splicing-only; not for 3' UTR or ncRNA binders |
| HOMER annotatePeaks.pl | Peak BED | Gene-level | Promoter > UTR > Exon > Intron > Intergenic | Annotation TSV | Familiar from ChIP-seq | Same TSS issue as ChIPseeker; less RNA-aware |
| bedtools intersect | Peak BED + feature BED | User-defined | User-defined | Per-feature overlap | Most flexible | Manual hierarchy logic must be written |
| pyranges (Python) | Peak BED + GTF | Customizable | User-defined | DataFrame | Fast, pythonic, scriptable | Hand-written priority logic |
| pybedtools | Peak BED + GTF | Customizable | User-defined | iterators | Flexible, scripted | Same as pyranges |
| Peakhood (Uhl 2022) | Peak BED + transcripts | Transcript context | NA | Per-peak transcript context | Resolves transcript-isoform ambiguity | Specialized; not a global region tool |

Methodology evolves; verify the GTF source (GENCODE preferred over Ensembl for human; both have feature differences) and the priority hierarchy against published RBP literature.

## Critical Choice: Annotation Hierarchy

RNA features are nested and overlapping. A 3' UTR peak is ALSO in an exon; an intronic peak near a splice site is ALSO in a transcribed-but-spliced region. Without a priority hierarchy the same peak gets counted multiple times.

**Standard CLIP hierarchy (most-specific first):**

1. **3' UTR** (specific to mature mRNA biology)
2. **5' UTR**
3. **CDS** (coding sequence)
4. **Exon** (catch-all for non-UTR exonic)
5. **Splice site** (within 50 nt of donor/acceptor; key for splicing factors)
6. **Intron**
7. **Promoter** (within 1 kb of TSS; usually not relevant for RNA-binding)
8. **5' flanking** / **3' flanking** (within 1 kb of gene)
9. **ncRNA** (lncRNA, snoRNA, snRNA, miRNA host)
10. **Repeat element** (Alu, LINE, LTR, SINE) - separate axis from above
11. **Intergenic**

ChIPseeker's default `level='gene'` reports the FIRST hit by priority. For CLIP, set `level='transcript'` and explicitly customize `tssRegion=c(-100, 100)` (default `c(-3000, 3000)` is for ChIP).

**Why CLIP needs the tight TSS window:** ChIPseeker was designed for ChIP-seq where the "Promoter" category captures transcription-factor binding within 3 kb upstream of a gene. For CLIP-seq, the binding substrate is RNA - the RBP cannot bind upstream of the TSS because there is no RNA upstream of the TSS. A 6 kb TSS window catches 5'-UTR peaks and unrelated upstream sequence, mislabeling 30-50% of CLIP peaks as "Promoter (2-3kb)" - implausible for an RNA-binding study. Tightening to `c(-100, 100)` constrains the "Promoter" category to the mRNA 5' end immediate vicinity and pushes deeper-5'-UTR peaks into the "5UTR" category where they belong.

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene

peaks <- readPeakFile('peaks.stringent.bed')

# CLIP-appropriate annotation
anno <- annotatePeak(
    peaks,
    TxDb = txdb,
    level = 'transcript',     # RNA-isoform-aware
    tssRegion = c(-100, 100), # tight; not a meaningful promoter for RNA binding
    genomicAnnotationPriority = c(
        'Promoter', '5UTR', '3UTR', 'Exon',
        'Intron', 'Downstream', 'Intergenic'
    )
)

print(anno)
plotAnnoPie(anno)
plotAnnoBar(anno)
plotDistToTSS(anno)  # CLIP-specific: dist to TSS is dist to mRNA 5' end
```

## RBP Class -> Expected Annotation

| RBP class | Expected dominant region | RBP examples |
|-----------|--------------------------|--------------|
| Splicing factors | Intron (within 500 nt of splice junction) | PTBP1, U2AF2, RBFOX1/2, SRSF1-9, HNRNPC, MBNL1 |
| 3' UTR mRNA stability/decay | 3' UTR | HuR (ELAVL1), PUM2, AUF1, ZFP36, TIA1, NUDT21 |
| 5' UTR translation regulation | 5' UTR, CDS start | EIF4A3, EIF3J, eIF2 subunits, LARP1, PCBP1/2 |
| Ribosome-associated | CDS | RPL/RPS proteins, RACK1 |
| Nuclear export | CDS, 3' UTR | NXF1, ALYREF, SRSF3 |
| m6A reader | 3' UTR, stop codon region | YTHDF1/2/3, IGF2BP1/2/3 |
| miRNA effector | 3' UTR (seed-matched sites) | AGO1/2/3/4, DICER1, TNRC6A/B/C |
| snoRNA-targeting RBP | snoRNA, rRNA | DKC1, FBL, NOP56, NHP2 |
| ncRNA-binding | Specific ncRNA target | TROVE2 (Y RNA), LARP7 (7SK), SSB (vault) |
| Mitochondrial | chrM (mt-mRNA + 12S/16S rRNA) | FASTKD2, LRPPRC, TFAM, MTPAP |
| Histone mRNA | Histone 3' end stem-loop | SLBP |
| Repeat-binding (TE) | Alu, LINE-1, LTR, SINE | MATR3, ZFP36, HNRNPK, HNRNPA2B1, FUS (LINE-1) |
| LCD/IDR / phase separation | Diverse (Alu, intron, 3' UTR) | FUS, TDP-43, EWSR1, TAF15 |

Mismatch between observed and expected suggests: (a) failed IP (cross-reactive antibody binding wrong RBP), (b) artifact (high-expression contamination), (c) genuinely new biology - investigate.

## RBP-Maps: Splicing Regulatory Maps

For splicing factors (PTBP1, U2AF2, RBFOX, SRSF1, etc.), the Yeo lab RBP-Maps tool aggregates eCLIP signal in a 350 nt window flanking the upstream, cassette, and downstream exons, producing a 1400 nt vectorized regulatory map. This map shows the position-dependent enrichment of RBP binding relative to alternative splicing events and is THE standard for splicing-CLIP analysis.

```bash
# Yeo lab rbp-maps Snakemake workflow
git clone https://github.com/YeoLab/rbp-maps
cd rbp-maps

# Inputs:
#   1. eCLIP BAM (rep1 + rep2)
#   2. Cassette exon BED (from RNA-seq KD experiment; see clip-seq/differential-clip)
#   3. Background "native" exons (constitutively spliced)

python rbpmaps/RBPMaps.py \
    --ip rep1.bam rep2.bam \
    --input sminput.bam \
    --positive cassette_inc.bed \
    --negative cassette_exc.bed \
    --background native_constitutive.bed \
    --output rbpmaps_out/ \
    --normalization input_normalization
```

Output: 1400 nt vector with eCLIP signal at every base, plotted as a metagene for cassette inclusion vs exclusion vs constitutive. A peak in the upstream-intron region (right of the cassette exon's 5' splice site) indicates intronic regulation; a peak in the cassette exon body indicates exonic regulation.

## Per-Tool Failure Modes

### ChIPseeker -- TSS-region default over-extends

**Trigger:** Used ChIPseeker default `tssRegion=c(-3000, 3000)` for CLIP peaks.

**Mechanism:** The 6 kb TSS window catches CLIP peaks deep in the 5' UTR or upstream introns and labels them "Promoter (2-3kb)". For RNA biology, the "promoter" category is meaningless - the RBP cannot bind pre-mRNA upstream of the TSS.

**Symptom:** 30-50% of peaks labeled "Promoter (2-3kb)" - implausible for an RNA-binding study.

**Fix:** Set `tssRegion=c(-100, 100)` or `c(-50, 50)`. Remove the "Promoter" category from the priority vector entirely if it gives 0 hits.

### ChIPseeker -- Gene-level loses isoform context

**Trigger:** Used `level='gene'` (default) on peaks that should be transcript-specific.

**Mechanism:** Gene-level annotation picks the canonical/longest transcript and assigns the peak to that transcript's features. A peak in an alternatively-spliced exon may be labeled "intron" because the gene-level reference picks an isoform where the exon is skipped.

**Symptom:** Splicing factor peaks heavily "intronic" when they should be exonic at alternative-cassette exons.

**Fix:** Use `level='transcript'`. Match isoforms to RBP-Maps cassette-exon coordinates for splicing factors.

### RCAS -- Slow on large peak sets

**Trigger:** RCAS report on > 100k peaks.

**Mechanism:** RCAS generates an HTML report with many plots; rendering is slow.

**Symptom:** Run time > 1 h; out-of-memory; HTML failing to render.

**Fix:** Sub-sample peaks to top 10k; or use ChIPseeker for the global view and reserve RCAS for per-region deep dives.

### RBP-Maps -- Requires SE event table

**Trigger:** Splicing-factor CLIP with no companion RNA-seq KD or no SE event BED.

**Mechanism:** RBP-Maps's regulatory metagene only makes sense relative to cassette exons differentially regulated by the RBP. Without the SE event table, the tool falls back to plotting at all native exons (no differential signal).

**Symptom:** Flat metagene; no position-dependent enrichment.

**Fix:** Generate the cassette-exon table from companion RNA-seq KD experiments (rMATS / MAJIQ / LeafCutter; see alternative-splicing skills) OR use a published table from ENCODE shRNA RNA-seq.

### bedtools -- Manual hierarchy errors

**Trigger:** Hand-written `bedtools intersect` chain for region annotation.

**Mechanism:** Forgetting to enforce priority leads to double-counting: a 3' UTR peak intersects 3UTR.bed AND exon.bed.

**Symptom:** Per-region counts sum to > total peak count by 20-50%.

**Fix:** Process in priority order; remove already-annotated peaks from the remaining set with `-v` before next intersect. Or use ChIPseeker / RCAS which encode the hierarchy internally.

### Repeat-element overlap missed

**Trigger:** Repeat-binding RBP (MATR3, HNRNPK) annotated without RepeatMasker BED.

**Mechanism:** Genomic feature BEDs (UTR/CDS/intron) do not flag repeat instances within them. An MATR3 peak in an intronic LINE-1 is labeled "intron" when "LINE-1 within intron" is the biology.

**Symptom:** Repeat-binding RBP looks like an intronic binder; functional analysis (GO terms) returns generic "RNA processing".

**Fix:** Pass RepeatMasker BED (UCSC) as a separate axis; annotate each peak with BOTH region AND repeat-class. Cross-check repeat-class fraction against literature: > 15% Alu / LINE / LTR overlap indicates a repeat binder.

### Mitochondrial peaks excluded by default

**Trigger:** Standard TxDb annotation drops chrM transcripts; FASTKD2 / LRPPRC peaks all "intergenic".

**Mechanism:** Some TxDb objects (older releases) exclude mitochondrial chromosome; ChIPseeker reports those peaks as having no annotation.

**Symptom:** chrM peaks labeled "Distal Intergenic" or simply missing from the annotation table.

**Fix:** Verify TxDb includes chrM (`genes(txdb, filter=list(tx_chrom='chrM'))`); add custom mt-mRNA + mt-rRNA + mt-tRNA BED if missing.

### Strand information ignored

**Trigger:** `bedtools intersect -wa -wb` without `-s` flag.

**Mechanism:** CLIP is strand-specific. Without `-s`, peaks on one strand can be annotated to features on the other strand - especially for overlapping transcripts (sense/antisense pairs).

**Symptom:** Antisense transcript peaks contaminate the sense annotation; per-region distribution shifted.

**Fix:** Always pass `-s` to bedtools intersect for CLIP. ChIPseeker handles strand automatically when peaks have BED column 6.

## Metagene Analysis

Metagene = aggregated profile of CLIP signal at each base of a normalized feature (e.g., 5' UTR, CDS, 3' UTR scaled to common length). Reveals position-dependent binding.

**Goal:** Generate a position-resolved CLIP-signal profile aggregated across all 3' UTRs (or other features) to identify position-dependent binding modes (e.g., stop-codon-proximal m6A readers, polyA-proximal CPEB).

**Approach:** Convert dedup BAM to strand-stranded bigWig, then use deepTools `computeMatrix scale-regions` to align signal across feature instances of variable length, and `plotProfile` / `plotHeatmap` for visualization.

```bash
# deepTools computeMatrix for metagene
# Step 1: peaks BED -> bedgraph
bedtools genomecov -bg -strand + -ibam dedup.bam > clip_plus.bg
bedtools genomecov -bg -strand - -ibam dedup.bam > clip_minus.bg
# combine to bigwig
bedGraphToBigWig clip_plus.bg chrom.sizes clip_plus.bw

# Step 2: metagene over 3' UTRs
computeMatrix scale-regions \
    -S clip_plus.bw clip_minus.bw \
    -R three_prime_UTRs.bed \
    --regionBodyLength 500 \
    --beforeRegionStartLength 100 \
    --afterRegionStartLength 100 \
    -o matrix.gz

plotProfile -m matrix.gz -o metagene.png --perGroup
plotHeatmap -m matrix.gz -o metagene_heatmap.png
```

| Metagene shape | Biology |
|----------------|---------|
| Peak at stop codon region | m6A reader (YTHDF1/2/3); IGF2BP1; some 3' UTR factors |
| Peak in proximal 3' UTR (within 200 nt of stop) | PUM2, IGF2BP, miRNA effectors |
| Peak in distal 3' UTR (within 200 nt of poly-A) | NUDT21, CPEB1, polyadenylation regulators |
| Peak at 5' splice site flanking intron | RBFOX, MBNL, HNRNPC |
| Peak at 3' splice site / branch point | U2AF2, PTBP1 |
| Peak at 5' UTR (within 50 nt of TSS) | EIF3, EIF4A3, LARP1 |
| Flat across CDS | Cytoplasmic ribosome-associated; less position-specific |

## Decision Tree by Scenario

| Scenario | Tool + parameters | Why |
|----------|-------------------|-----|
| Global region distribution (3' UTR / CDS / intron) | ChIPseeker `tssRegion=c(-100,100) level='transcript'` | Mature, fast, ENCODE-comparable |
| Splicing factor regulatory map | RBP-Maps (Yeo) with RNA-seq KD cassette table | The standard for splicing-CLIP |
| RNA-feature aware (snoRNA, lncRNA-specific) | RCAS or custom GTF + bedtools | RCAS handles ncRNA features |
| Transcript-isoform context resolved | Peakhood + ChIPseeker level='transcript' | Resolves which isoform the peak supports |
| Metagene 3' UTR / 5' UTR | deepTools computeMatrix + plotProfile | Standard metagene visualization |
| Repeat-element overlap (MATR3, HNRNPK) | bedtools intersect with RepeatMasker | Repeat axis is independent of region axis |
| Mitochondrial RBP (FASTKD2) | Custom chrM-aware annotation | Standard TxDb may drop chrM |
| Bulk RBP overview | ChIPseeker plotAnnoPie + plotDistToTSS | Quick orienting plots |
| Compare two RBPs' region distributions | ChIPseeker annotatePeakList + side-by-side bar | Direct comparability |
| miRNA target site (AGO-CLIP) | bedtools intersect with 3' UTR + TargetScan seed scan | miRNA biology specific |
| m6A reader (YTHDF, IGF2BP) | ChIPseeker + custom stop-codon-distance plot | m6A biology stops-codon-proximal |

## Reconciliation: When Annotations Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| ChIPseeker "Promoter" >> 5' UTR for CLIP | TSS region too wide | Tighten `tssRegion=c(-100,100)` |
| ChIPseeker gene-level intronic; RBP-Maps shows exonic at cassettes | Gene-level picks canonical isoform; RBP-Maps uses cassettes | Trust RBP-Maps for splicing factors |
| Many peaks "intergenic" near a known gene | TxDb missing the transcript | Verify GENCODE vs Ensembl GTF; add lincRNA / unannotated transcripts |
| chrM peaks missing | TxDb excluded chrM | Add custom mt-mRNA BED |
| Sum of per-region counts > total peaks | Hierarchy not enforced | Use ChIPseeker; or `bedtools intersect -v` chain |
| Repeat-binding RBP looks "intronic" | RepeatMasker axis not added | Annotate peaks with RepMask intersect separately |
| Metagene flat for known position-specific RBP | Wrong feature BED (e.g., gene-body instead of transcript-isoform) | Use isoform-aware feature BED |
| RBP-Maps signal flat at cassette exons | No RNA-seq KD reference table | Generate cassettes from companion KD; use ENCODE shRNA tables |

**Operational rule:** Report (a) ChIPseeker global region pie, (b) RBP-Maps metagene for splicing factors, (c) repeat-element fraction separately, (d) transcript-isoform context with Peakhood if ambiguous. Three views together prevent misinterpretation.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "Promoter" >> 30% of peaks in CLIP | TSS region default too wide | `tssRegion=c(-100,100)` |
| Strand-mixing artifacts | Bedtools intersect without `-s` | Always pass `-s` for CLIP |
| 3' UTR fraction < 10% for HuR | Wrong txdb version (UTR poorly annotated) | Use GENCODE v38+ TxDb |
| chrM peaks lost | TxDb excludes mitochondrial | Add mt-transcript BED |
| RBP-Maps flat metagene | No cassette exon BED | Generate from RNA-seq KD; or use ENCODE table |
| Repeat fraction over-counted | Same repeat instance counted multiple times | `bedtools merge` repeat BED first |
| ChIPseeker `level='gene'` collapses isoforms | Default level=gene | Set `level='transcript'` |
| Annotation runs slow for large peak set | RCAS HTML generation | Use ChIPseeker for global; RCAS for top-K |
| GO enrichment yields generic terms | Repeat-binding RBP annotated as intronic | Re-annotate with RepeatMasker axis |
| Peak in unannotated lincRNA labeled intergenic | Older GENCODE missing the lincRNA | Update GENCODE; add manual transcript BED |

## References

- Yu G et al 2015 Bioinformatics 31:2382 (ChIPseeker)
- Uyar B, Yusuf D et al 2017 Nucleic Acids Res 45:e91 (RCAS)
- Yee BA et al 2019 RNA 25:193 (RBP-Maps splicing regulatory maps)
- Van Nostrand EL et al 2020 Nature 583:711 (ENCODE 150 RBP eCLIP, region distribution analysis)
- Quinlan AR & Hall IM 2010 Bioinformatics 26:841 (bedtools)
- Hentze MW et al 2018 Nat Rev Mol Cell Biol 19:327 (RBP function review)
- Uhl M et al 2022 Bioinformatics 38:1139 (Peakhood transcript-context)
- ENCODE eCLIP standards (encodeproject.org/eclip) - region distribution conventions

## Related Skills

- clip-seq/clip-peak-calling - Upstream peak calls
- clip-seq/crosslink-site-detection - Single-nt CL sites for fine-grained metagene
- clip-seq/clip-motif-analysis - Motif discovery within annotated regions
- clip-seq/differential-clip - Cross-condition annotated peaks for regulatory maps
- clip-seq/ago-clip-mirna-targets - 3' UTR seed-matched site annotation
- clip-seq/m6a-clip - Stop-codon-proximal m6A annotation
- genome-intervals/gtf-gff-handling - GTF preparation for annotation
- genome-intervals/interval-arithmetic - bedtools intersect patterns
- alternative-splicing/differential-splicing - Cassette exon tables for RBP-Maps
- chip-seq/peak-annotation - DNA-protein annotation analogue
<!-- END FILE: clip-seq/binding-site-annotation/SKILL.md -->

## 子目录：clip-seq/clip-alignment

<!-- BEGIN FILE: clip-seq/clip-alignment/SKILL.md -->
---
name: bio-clip-seq-clip-alignment
description: Align preprocessed CLIP-seq reads (eCLIP, iCLIP, iCLIP2, PAR-CLIP) to genome with STAR or bowtie2 using crosslink-preserving parameters, choosing between unique-mapper-only and multi-mapper-aware alignment for repeat-binding RBPs, deciding STAR vs HISAT2 memory trade-offs, and applying ENCODE-compatible filters. Use when turning preprocessed CLIP FASTQ into a deduplicated, MAPQ-filtered BAM ready for peak calling or crosslink-site detection.
tool_type: cli
primary_tool: STAR
---

## Version Compatibility

Reference examples tested with: STAR 2.7.11b+, bowtie2 2.5.3+, HISAT2 2.2.1+, samtools 1.19+, CLAM 1.2+, umi_tools 1.1.5+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed binary (`<tool> -h`) and adapt the example to match the actual CLI rather than retrying.

# CLIP-seq Alignment

**"Align preprocessed CLIP reads to genome with crosslink-preserving parameters"** -> Map UMI-extracted, adapter-trimmed reads to the genome (NOT transcriptome) with end-to-end alignment, strict mismatch ceiling, and unique-mapper-only filtering by default. The 5' end of the read (R2 5' in paired-end eCLIP; R1 5' in iCLIP) carries the reverse-transcriptase truncation = crosslink site -1; any soft-clipping or 5' trimming during alignment destroys nucleotide resolution.

- CLI (eCLIP / iCLIP / iCLIP2, ENCODE pattern): `STAR --runMode alignReads --genomeDir STAR_index --readFilesIn R1.trim.fq.gz R2.trim.fq.gz --readFilesCommand zcat --outFilterType BySJout --outFilterMultimapNmax 1 --alignEndsType EndToEnd --outFilterMismatchNoverReadLmax 0.04 --outSAMtype BAM SortedByCoordinate --outSAMattributes All --outFileNamePrefix sample_`
- CLI (PAR-CLIP, mismatch ceiling raised for T->C signal): same as above but `--outFilterMismatchNoverReadLmax 0.07`
- CLI (low memory, no splicing): `bowtie2 -x genome_index -U R1.trim.fq.gz --very-sensitive -p 8 | samtools view -bS - | samtools sort -o aligned.bam`
- CLI (repeat-binding RBP, multi-mapper rescue): `STAR ... --outFilterMultimapNmax 100 --outSAMmultNmax -1` then process with `CLAM` (see repeat-element section)

End-to-end alignment is non-negotiable. `--alignEndsType Local` (STAR default for some pipelines) soft-clips low-quality 5' bases and discards exactly the truncation signal. Mismatch ceiling 0.04 (4% of read length) excludes most sequencing-error reads; 0.07 is the PAR-CLIP override to retain T->C reads.

## Algorithmic Taxonomy

| Aligner | Splice-aware | Memory (human) | CLIP-suitable | Strength | Fails when |
|---------|--------------|----------------|---------------|----------|------------|
| STAR | Yes | ~30 GB peak (sjdbOverhang 100) | Yes (ENCODE eCLIP standard) | Splice-aware, fast on deep libraries, excellent multi-mapper logs | RAM hungry; small clusters or laptops cannot run human genome index |
| HISAT2 | Yes | ~8 GB | Yes (good alternative when STAR memory infeasible) | Low memory; comparable splice accuracy | Slightly lower multi-mapper precision; smaller community adoption for CLIP |
| bowtie2 | No (no splice) | ~3 GB | Limited (loses intronic and read-through reads at splice junctions) | Fast, low memory, mature | Misses spliced reads; not suitable for mRNA-binding RBPs (PTBP1, U2AF2) |
| bwa-mem2 | No | ~30 GB index | Not recommended | Fast for DNA; no splice support | Same splicing issue as bowtie2; no CLIP-specific advantage |
| chromap | No | ~5 GB | Not recommended for CLIP | Very fast for ATAC/ChIP | No splice support; pre-applies fragment shift inappropriate for CLIP |
| novoalign | Yes (splice with -X) | ~10 GB | Acceptable | Old standard; some labs still use | Commercial; community moved to STAR/HISAT2 |
| Salmon (transcriptome) | N/A | low | Not suitable | Pseudo-alignment | Discards intronic and unannotated reads, both common in CLIP |

Methodology evolves; verify the current ENCODE eCLIP pipeline (encodeproject.org/eclip) before locking parameters. The ENCODE eCLIP SOP v2.2 pins STAR 2.5.2b (the earlier v1 SOP used 2.4.0i); modern reanalyses use STAR 2.7.x with the same parameter set.

## Critical Choice: Unique-Mapper-Only vs Multi-Mapper Rescue

Two valid alignment strategies depend on the RBP biology:

**Strategy A -- Unique-mapper-only (default, ENCODE standard):** `--outFilterMultimapNmax 1` discards every read that maps to more than one genomic location. Loses 5-15% of reads but produces unambiguous positions for downstream peak calling and crosslink-site detection.

**Strategy B -- Multi-mapper rescue (for repeat-binding RBPs):** `--outFilterMultimapNmax 100 --outSAMmultNmax -1` retains up to 100 alignments per read; downstream EM-based assignment (CLAM, Xinglab) probabilistically allocates them. Required for RBPs that bind Alu, LINE-1, LTR, or other repetitive elements (e.g., MATR3, ILF3, FUS at LINE-1, HNRNPK at SINEs, PUM2 in some repeat contexts).

| RBP class | Strategy | Why |
|-----------|----------|-----|
| Splicing factors (PTBP1, U2AF2, RBFOX, SRSF1) | A (unique) | Bind defined intronic/exonic motifs, not repeats |
| 3' UTR stability (HuR, PUM2, AUF1) | A (unique) | Binding sites are usually in unique 3' UTR sequence |
| Ribosomal proteins (RPS19, RPL35A) | A (unique) | Bind mRNA bodies and snoRNAs in unique sequence |
| Translation initiation (EIF3J, EIF2S2) | A (unique) | Bind 5' UTRs and snoRNAs |
| Repeat / TE binders (MATR3, ZFP36 isoforms, HNRNPK, LINE-1 ORFs) | B (multi-mapper) | Genuine biology is in repeat regions |
| Y-RNA / 7SK / vault RNAs (TROVE2, LARP7) | A (unique) but with `--outFilterMultimapNmax 50` for the ncRNA itself | These small RNAs have a few unique copies; pure unique discards them |
| Mitochondrial RBPs (FASTKD2, LRPPRC, TFAM) | A (unique) with chrM retained | chrM has unique sequence but must not be excluded by blacklists |
| Histone mRNA (SLBP) | A (unique) but DO NOT pre-filter rRNA index that includes histone | Replication-dependent histone genes are repetitive in some indices |

## Per-Aligner Failure Modes

### STAR -- Local alignment soft-clips the truncation site

**Trigger:** Pipeline copied from RNA-seq tutorial uses `--alignEndsType Local` (or omits the flag, letting STAR default).

**Mechanism:** Local alignment soft-clips up to 12% of the read end if scoring improves. In CLIP, the 5' read end is the truncation = CL site -1 base; if it carries even one mismatched base from RT errors, STAR soft-clips it.

**Symptom:** Crosslink-site density looks "smoothed"; PureCLIP / CTK CITS detect 5-30% fewer single-nt sites than expected; peak boundaries look fuzzy.

**Fix:** Always pass `--alignEndsType EndToEnd`. To confirm: `samtools view dedup.bam | awk '{ if ($6 ~ /S/) print }' | wc -l` should report < 1% of reads with soft-clip CIGAR operations.

### STAR -- Mismatch ceiling discards PAR-CLIP signal

**Trigger:** PAR-CLIP library aligned with `--outFilterMismatchNoverReadLmax 0.04` (the iCLIP/eCLIP default).

**Mechanism:** PAR-CLIP T->C conversion rate is 20-50% of T positions in crosslinked reads. For a 30 nt read with 8 Ts and 50% conversion, ~4 T->C mismatches occur (13% of read length). The 4% mismatch ceiling drops these reads.

**Symptom:** 40-70% read loss at alignment for PAR-CLIP; downstream PARalyzer / wavClusteR find few clusters.

**Fix:** For PAR-CLIP only, set `--outFilterMismatchNoverReadLmax 0.07` (7%). Verify post-alignment: `samtools view dedup.bam | awk '{ for(i=12;i<=NF;i++) if($i ~ /^MD:/) print $i }' | head` should show many T->C-indicating MD tags.

### STAR -- Multi-mappers silently discarded when needed

**Trigger:** Repeat-binding RBP (MATR3, LINE-1 binders) aligned with default `--outFilterMultimapNmax 1`.

**Mechanism:** Reads mapping to more than one Alu/LINE/LTR instance are removed; 10-30% of true binding sites are lost.

**Symptom:** Compared to published RBP literature for repeat binders, the analysis peak count is 3-10x lower; repeat-overlap fraction is < 5% when literature suggests 15-30%.

**Fix:** Raise `--outFilterMultimapNmax` to 50-100; emit all alignments with `--outSAMmultNmax -1`; downstream use CLAM (Xinglab) to probabilistically assign multi-mappers to a single best location via expectation-maximization. Or restrict to a non-repeat analysis and note the limitation.

### bowtie2 -- Splice junctions missed silently

**Trigger:** Used `bowtie2` instead of STAR for an mRNA-binding RBP (typical of PTBP1, U2AF2 intronic binding studies); BAM looks normal but introns/exons map poorly.

**Mechanism:** bowtie2 has no splice model; reads spanning exon-intron junctions soft-clip 5-20 nt or fail to align entirely.

**Symptom:** Lower read recovery (~70-80% vs STAR ~90-95%); peaks at splice sites under-called; intronic peaks over-represented (reads that would have aligned across an exon now align fully in the intron upstream).

**Fix:** Use STAR or HISAT2 for any RBP that binds mRNA, pre-mRNA, or splice signals. Reserve bowtie2 for non-coding RNA targets (snoRNA, 7SK, Y RNA) where short reads do not span junctions.

### STAR -- Memory exhausted on small machine

**Trigger:** Human genome index loaded into < 32 GB RAM machine.

**Mechanism:** STAR's suffix-array index requires ~30 GB RAM for human/mouse. Smaller machines crash or swap.

**Symptom:** "STAR EXITED" with bus error; or alignment takes > 24h on a single sample.

**Fix:** Switch to HISAT2 (~8 GB peak); or build a STAR index with `--genomeSAsparseD 2` (halves RAM at the cost of ~30% alignment slowdown); or use a public cluster with > 64 GB. Do NOT use bowtie2 as a memory workaround for splice-aware needs.

### Read-2 5' end trimmed inadvertently

**Trigger:** A `--clip5pNbases` flag carried over from RNA-seq quality trimming; or a `fastp --trim_front2 5` step in preprocessing.

**Mechanism:** Removes the eCLIP truncation base on R2 5'.

**Symptom:** Crosslink sites called from R2 5' positions cluster artificially at uniform offsets across genome; motif enrichment around crosslink sites collapses.

**Fix:** Verify the BAM with `samtools view dedup.bam | awk '$2 ~ /83|163/ { print $4 }'` (R2 5' positions on minus and plus strand) and confirm they map to the EXPECTED truncation sites, not shifted by 5 nt.

## ENCODE 4 eCLIP STAR Parameters (Reference)

```bash
STAR --runMode alignReads \
    --runThreadN 16 \
    --genomeDir /path/to/STAR_hg38_index \
    --genomeLoad NoSharedMemory \
    --readFilesIn R1.trim.fq.gz R2.trim.fq.gz \
    --readFilesCommand zcat \
    --outFilterType BySJout \
    --outFilterMultimapNmax 1 \
    --alignEndsType EndToEnd \
    --outFilterMismatchNoverReadLmax 0.04 \
    --outSAMtype BAM SortedByCoordinate \
    --outSAMattributes All \
    --outFileNamePrefix sample_ \
    --outFilterScoreMinOverLread 0.66 \
    --outFilterMatchNminOverLread 0.66
```

The `--outFilterScoreMinOverLread 0.66` / `--outFilterMatchNminOverLread 0.66` (matched score / matched bases >= 66% of read length) are ENCODE-specific stringency added on top of the mismatch ceiling. These two flags are why ENCODE eCLIP BAMs are smaller than naive STAR output.

## Post-Alignment Filtering

```bash
# Sort and index
samtools index sample_Aligned.sortedByCoord.out.bam

# MAPQ filter (255 in STAR = unique; bowtie2 uses different scheme)
samtools view -b -q 10 sample_Aligned.sortedByCoord.out.bam > sample_q10.bam
samtools index sample_q10.bam

# UMI deduplication (see clip-preprocessing for `--method=unique` rationale)
umi_tools dedup \
    --stdin=sample_q10.bam \
    --stdout=sample_dedup.bam \
    --method=unique \
    --paired \
    --log=sample_dedup.log
samtools index sample_dedup.bam
```

**MAPQ thresholds differ by aligner:**
- STAR: 255 = uniquely mapped (== `--outFilterMultimapNmax 1` already filtered); lower MAPQ values mean multi-mappers
- bowtie2: 42 = unique; 0-1 = multi-mapper; intermediate = ambiguous
- HISAT2: 60 = unique; similar to bowtie2 scheme but tool-specific

For STAR `-q 10` is conventional but redundant if `--outFilterMultimapNmax 1` was already set. For bowtie2/HISAT2, `-q 30` is a stricter unique-mapper proxy.

## Multi-Mapper Rescue with CLAM (Repeat-Binding RBPs)

```bash
# 1. Re-align permitting multi-mappers
STAR --runMode alignReads \
    --genomeDir STAR_index --readFilesIn R1.fq.gz R2.fq.gz \
    --readFilesCommand zcat --outFilterMultimapNmax 100 \
    --outSAMmultNmax -1 --alignEndsType EndToEnd \
    --outSAMtype BAM SortedByCoordinate --outFileNamePrefix mm_

samtools index mm_Aligned.sortedByCoord.out.bam

# 2. CLAM preprocessing splits unique vs multi-mapper reads
CLAM preprocessor -i mm_Aligned.sortedByCoord.out.bam -o clam_out/ --read-tagger-method median

# 3. EM-based multi-mapper realignment
CLAM realigner -i clam_out/unique.sorted.bam -o clam_out/ --winsize 50 --max-tags 0

# 4. Downstream peakcaller (CLAM peakcaller is a wrapper for Piranha+EM)
CLAM peakcaller -i clam_out/unique.sorted.bam clam_out/realigned.sorted.bam \
    -o clam_peaks.bed -p 8 --gtf gencode.v38.annotation.gtf
```

CLAM (Zhang & Xing 2017) rescues additional peaks in repeat regions (operationally ~10-30% more, dataset-dependent). It is the only EM-based multi-mapper solution actively maintained for CLIP as of 2025.

## HISAT2 Low-Memory Alternative

```bash
hisat2 --rna-strandness FR --no-softclip \
    -p 8 -x hisat2_grch38_index \
    -1 R1.trim.fq.gz -2 R2.trim.fq.gz \
    --no-unal \
    --score-min L,0,-0.2 \
    -S sample.sam 2> hisat2.log

samtools view -bS sample.sam | samtools sort -o sample.bam -
samtools index sample.bam
```

`--no-softclip` is the HISAT2 equivalent of STAR's `--alignEndsType EndToEnd`. `--score-min L,0,-0.2` is roughly equivalent to STAR's `--outFilterMismatchNoverReadLmax 0.04` (penalty scales linearly with read length, with -0.2 per mismatch slope).

## Decision Tree by Use Case

| Scenario | Recommended aligner + parameters | Why |
|----------|----------------------------------|-----|
| eCLIP, ENCODE-comparable, 32+ GB RAM | STAR ENCODE pattern (above) | Reproducible against ENCODE peak calls |
| iCLIP / iCLIP2, single-end | STAR same params, `--readFilesIn R1.fq.gz` | Single-end variant of ENCODE block |
| PAR-CLIP | STAR with `--outFilterMismatchNoverReadLmax 0.07` | T->C is signal, not error |
| Repeat-binding RBP (MATR3, LINE-1 binders) | STAR `--outFilterMultimapNmax 100 --outSAMmultNmax -1` + CLAM | EM rescue of multi-mappers |
| Low memory (< 16 GB) | HISAT2 with `--no-softclip` | STAR index unloadable |
| Bacterial / yeast (small genome, no splicing) | bowtie2 `--very-sensitive` | Splice-awareness wasted |
| snoRNA-only / 7SK-only analysis | bowtie2 with custom index | Avoid genome-scale splicing tangle |
| Allele-specific CLIP | STAR ENCODE + WASP filter (`--waspOutputMode SAMtag`) | Reference-allele mapping bias must be removed |
| Long-read CLIP (dirCLIP, nanopore) | minimap2 `-ax splice -uf -k14` | STAR cannot align long reads |

## Allele-Specific Alignment with WASP

CLIP-seq inherits reference-allele mapping bias from RNA-seq. For allele-specific binding analyses (BEAPR, ASPRIN), STAR's WASP integration removes reads where the alternative-allele version of the read would not have aligned at the same position.

```bash
# STAR with WASP filter; --varVCFfile is the heterozygous SNP VCF
STAR --runMode alignReads \
    --genomeDir STAR_index --readFilesIn R1.fq.gz R2.fq.gz --readFilesCommand zcat \
    --alignEndsType EndToEnd --outFilterMultimapNmax 1 --outFilterMismatchNoverReadLmax 0.04 \
    --outSAMtype BAM SortedByCoordinate \
    --varVCFfile sample.het.vcf.gz \
    --waspOutputMode SAMtag \
    --outSAMattributes vA vG vW \
    --outFileNamePrefix wasp_

samtools view -b -e '[vW]==1' wasp_Aligned.sortedByCoord.out.bam > wasp_pass.bam
```

WASP filtering is MANDATORY for allele-specific binding analyses; reference-allele bias inflates REF allele frequency 1-5% in unfiltered CLIP data.

## Reconciliation: When Alignment Outputs Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| STAR retains more reads than bowtie2 | STAR handles splice junctions; bowtie2 fails on spliced reads | Trust STAR for mRNA-binding RBPs |
| Read count after STAR < expected | `--outFilterMultimapNmax 1` discarding multi-mappers | If RBP binds repeats, switch to multi-mapper mode + CLAM |
| Crosslink-site density looks smoothed | Soft-clip ON (alignEndsType Local) | Re-align with `--alignEndsType EndToEnd` |
| 40-70% read loss in PAR-CLIP | T->C mismatches exceed 4% ceiling | Raise `--outFilterMismatchNoverReadLmax` to 0.07 |
| HISAT2 calls peaks STAR misses | HISAT2 lower-stringency soft-clip behaviour | Re-run HISAT2 with `--no-softclip`; differences should narrow to < 5% |
| Two STAR versions (2.4 vs 2.7) give different BAMs | Index sjdb format changed; parameter defaults drift | Pin STAR version for cross-study comparison; document |

**Operational rule:** For ENCODE-comparable analysis, use STAR 2.5.2b (ENCODE eCLIP SOP v2.2) or 2.7.x with the ENCODE eCLIP parameter block; use `--alignEndsType EndToEnd`; use `--outFilterMultimapNmax 1` unless the biology requires multi-mappers (then add CLAM); UMI-dedupe with `umi_tools dedup --method=unique`. Document any deviation in methods.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `STAR ERROR ... Could not allocate memory` | Index too large for RAM | Switch to HISAT2; or rebuild STAR index with `--genomeSAsparseD 2` |
| `samtools sort: not enough memory` after STAR | sort -m default 768M too small | `samtools sort -m 4G -@ 8` |
| Crosslink density at uniform 5 nt offsets across genome | R2 5' trimmed by mistake | Recheck preprocessing; cutadapt `-g` and fastp `--trim_front2` are banned for CLIP |
| 90% of reads MAPQ < 10 | Genome index built for different species | Verify with `samtools view -h sample.bam \| head` against expected chromosome names |
| HISAT2 splice junctions miss-detected | Used `--no-splice` (HISAT2 splice OFF) | Remove `--no-splice` for mRNA studies |
| umi_tools dedup OOM | Too many UMIs at one position; deep library | Switch to `--method=unique` (less RAM than directional) |
| Multi-mapper count after STAR `--outFilterMultimapNmax 100` = 0 | `--outSAMmultNmax` not set | Add `--outSAMmultNmax -1` to emit all alignments |
| Reads MAPQ 0 dominate after bowtie2 | `--very-sensitive` ON but multi-mappers retained | Add `samtools view -q 30` post-filter |
| CLAM EM never converges | Background regions empty; sparse coverage | Lower `--max-tags` to 5; provide gene model GTF; verify multi-mapper BAM exists |

## References

- Van Nostrand EL et al 2016 Nat Methods 13:508 (eCLIP / ENCODE alignment parameter block)
- Konig J et al 2010 Nat Struct Mol Biol 17:909 (iCLIP truncation-as-CL principle)
- Dobin A et al 2013 Bioinformatics 29:15 (STAR aligner)
- Kim D et al 2019 Nat Biotechnol 37:907 (HISAT2)
- Langmead B & Salzberg SL 2012 Nat Methods 9:357 (bowtie2)
- Zhang Z & Xing Y 2017 Nucleic Acids Res 45:9260 (CLAM multi-mapper assignment)
- van de Geijn B et al 2015 Nat Methods 12:1061 (WASP allele-specific alignment)
- Hafner M et al 2010 Cell 141:129 (PAR-CLIP T->C mismatch tolerance need)
- West C et al 2023 Wellcome Open Res 8:286 (nf-core/clipseq alignment defaults)

## Related Skills

- clip-seq/clip-preprocessing - UMI extraction and adapter trimming before alignment
- clip-seq/clip-qc - Post-alignment QC (library complexity, read distribution, FRiP)
- clip-seq/crosslink-site-detection - Why the 5' end must be preserved
- clip-seq/clip-peak-calling - Downstream peak calling on the dedup BAM
- read-alignment/star-alignment - General STAR usage and indexing
- read-alignment/bowtie2-alignment - General bowtie2 usage
- alignment-files/duplicate-handling - Picard MarkDuplicates as UMI-less fallback
- single-cell/scatac-analysis - Cross-reference for single-cell variants
<!-- END FILE: clip-seq/clip-alignment/SKILL.md -->

## 子目录：clip-seq/clip-deep-learning

<!-- BEGIN FILE: clip-seq/clip-deep-learning/SKILL.md -->
---
name: bio-clip-seq-clip-deep-learning
description: Predict RBP binding from RNA sequence using deep learning models (RBPNet sequence-to-signal, RNAProt RNN, GraphProt2 GCN with structure, DeepCLIP, DeepRiPe multi-modal CNN) for variant-effect prediction, in silico binding-site discovery, model interpretation, and transfer learning from CLIP and RBNS datasets. Use when computational prediction of RBP binding from sequence is needed, evaluating variant effects on binding without further wet-lab experiments, comparing model performance, or training a custom model on ENCODE eCLIP data.
tool_type: python
primary_tool: RBPNet
---

## Version Compatibility

Reference examples tested with: RBPNet (Horlacher et al 2023 github), RNAProt 0.5+, GraphProt2 (Uhl et al 2021 github), DeepCLIP 1.0+ (Gronning 2020), DeepRiPe (Ohler lab), pytorch 2.2+, tensorflow 2.15+, scikit-learn 1.4+, biopython 1.83+, transformers 4.40+ (for RNA foundation models).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- Frameworks: check pytorch / tensorflow versions; reproducibility depends on framework version

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# CLIP-seq Deep Learning

**"Predict RBP binding from RNA sequence using deep learning"** -> Train or apply neural networks that learn the sequence (and optionally structure) preference of an RBP from CLIP-seq peaks or single-nucleotide crosslink sites. The output is per-base or per-site binding probability for any input sequence, enabling: (a) variant-effect prediction at heterozygous SNPs; (b) in silico binding-site discovery on transcripts not covered by CLIP; (c) systematic comparison across RBPs via shared model architectures; (d) interpretation via attribution / saliency to recover RBP-specific motifs and structural preferences. Modern models (RBPNet 2023) predict per-nucleotide crosslink count distributions rather than binary peak/non-peak, providing single-nt resolution outputs.

- Python (RBPNet sequence-to-CL signal): `import rbpnet; model = rbpnet.load_pretrained('RBP_name'); predictions = model.predict(sequence)` produces per-base CL count distribution
- Python (RNAProt RNN classifier): `RNAProt train -i peaks.bed -t background.bed -g genome.fa -o model/` then `RNAProt predict -m model/ -i query_sequences.fa -o predictions.tsv`
- Python (GraphProt2 GCN with structure): `graphprot2 train -i peaks.bed -bg shuffled.bed -g genome.fa --structure -o model/`
- Python (DeepCLIP for binding probability): `deepclip --train --train_data train.fa --validation_data val.fa --predict --predict_data test.fa --output_dir output/`
- Python (DeepRiPe multi-modal CNN): `from deepripe import DeepRiPe; model.train(X_train, y_train); predictions = model.predict(X_test)`

The benchmarks (RNAProt paper, 2021): RNAProt AUC 87-89%; DeepCLIP 84-87%; GraphProt 82-84%. RBPNet (2023) is the modern sequence-to-signal model that predicts per-nt CL distributions at single-nucleotide resolution rather than binary site classification.

## Models Taxonomy

| Model | Architecture | Input | Output | Resolution | Strength | Fails when |
|-------|--------------|-------|--------|------------|----------|------------|
| RBPNet (Horlacher et al 2023) | Sequence-to-signal CNN | Sequence | Per-nt CL count distribution | Single-nt | Modern single-nt resolution; predicts CL distribution not binary | New (2023); fewer pretrained RBPs |
| RNAProt (Uhl 2021) | GRU RNN | Sequence | Binary binding probability | Site/peak | Highest AUC in benchmark (87-89%); feature-rich (RNAplfold structure) | Single-prediction; not per-base profile |
| GraphProt (Maticzka 2014) | Graph kernel + SVM | Sequence + structure | Binary | Site/peak | Original structure-aware; well-validated | Older; superseded by GraphProt2 |
| GraphProt2 (Uhl 2021) | Graph Convolutional Network (GCN) | Variable-length sequence + structure | Nucleotide-wise binding profile | Per-nt | Variable-length input; structure-aware | Slow to train; needs GPU |
| DeepCLIP (Gronning 2020) | CNN + BiLSTM | Sequence | Binary | Site | Fast; good benchmarks | Sequence-only; no structure |
| DeepRiPe (Ghanbari 2020) | Multi-modal CNN | Sequence + region type | Binary | Site | Multi-input; good ENCODE benchmark | Sequence/region must be pre-extracted |
| iDeep / iDeepE (Pan 2018) | CNN ensemble | Sequence | Binary | Site | Ensemble approach | Older; few pretrained models |
| Pysster (Budach 2018) | CNN-LSTM | Sequence | Binary | Site | Generic framework | Less RBP-specific |
| DeepBind (Alipanahi 2015) | CNN | Sequence | Binary | Site | First deep-learning RBP model | Outdated; superseded |
| Basenji-style multi-task CNN | Multi-task CNN | Sequence | Per-task profile | Per-nt | Joint learning across RBPs | Computational overhead; no dedicated CLIP tool |
| RNA foundation models (RNAErnie, RNA-FM) | Transformer pretrained on RNA | Sequence | Embeddings (downstream task) | Embedding | Transfer learning across RBPs | Foundation model trained at depth; fine-tuning needed |

Methodology evolves; verify the latest publication on RBP deep learning (RBPNet 2023 is the current state-of-the-art per-nt resolution model). RNA foundation models (RNA-FM, RNAErnie) are emerging in 2024 as transfer-learning backbones; fine-tuning on CLIP data for specific RBPs is the next-generation approach.

## Critical Choice: Binary Classification vs Sequence-to-Signal

**Binary classification (RNAProt, DeepCLIP, DeepRiPe, GraphProt2):** Train on labeled site vs background; predict probability of binding for an input sequence. Output: per-sequence score. Pro: simple framework; mature benchmarks. Con: discards single-nt CL distribution information; binary decision boundary.

**Sequence-to-signal (RBPNet):** Train on per-nt CL count distributions from PureCLIP or CTK CITS output; predict per-base CL count for input sequence. Output: per-nt profile. Pro: single-nt resolution; preserves CL count information; matches biology (CL is a sharp signal, not a region). Con: newer (2023); fewer pretrained models; harder to interpret with classical motif tools.

| Goal | Model |
|------|-------|
| Predict RBP binding probability for an input sequence | RNAProt or DeepRiPe |
| Predict per-base CL distribution | RBPNet |
| Variant-effect at heterozygous SNP | RBPNet or DeepRiPe (per-base output) |
| Compare RBP preferences across ENCODE | Multi-task model (Basenji-style) |
| Transfer learning across RBPs | RNA foundation model + fine-tune |
| In silico screening of variants | RBPNet (per-base) for genome-wide |
| Motif interpretation via attribution | DeepRiPe or GraphProt2 (interpretable) |
| Custom training on new CLIP data | RNAProt (easiest pipeline) |
| Production-grade per-base prediction | RBPNet 2023 |

## Variant-Effect Prediction Workflow

Apply a pretrained or custom-trained model to predict the change in binding upon a sequence variant.

```python
import torch
from rbpnet import RBPNet  # hypothetical API; verify per-package documentation

# Load pretrained model for specific RBP
model = RBPNet.load_pretrained('TARDBP_HEK293T')

# Reference and alternative sequences around a variant
ref_seq = 'CTGTACTGCAGTAGCATGCTAGCATGCTAGCAT'  # 32 nt window centered on variant
alt_seq = 'CTGTACTGCAGTAGCATGCTAGCATGCTAGCAA'  # Variant: T -> A at position 32

# Predict per-base CL distribution for both
ref_pred = model.predict(ref_seq)   # shape: (32, 1) - per-base CL probability
alt_pred = model.predict(alt_seq)

# Variant effect: log2 fold change in summed binding signal
import numpy as np
effect = np.log2((alt_pred.sum() + 1e-9) / (ref_pred.sum() + 1e-9))
print(f'Variant effect (log2 FC): {effect:.4f}')

# Strong-effect variant: |log2 FC| > 1.0
# Mid-effect: 0.5 - 1.0
# Weak: < 0.5
```

For genome-wide variant scoring: apply this in batch to all GWAS variants overlapping the RBP's binding regions. The output is a per-variant log2 FC; downstream Mendelian randomization or fine-mapping integrates with phenotype-association statistics.

## Training a Custom Model (RNAProt Example)

RNAProt is the most accessible training framework. It accepts peak BED + background BED + genome FASTA.

**Goal:** Train a chromosome-split RNN classifier from CLIP peaks to predict RBP binding probability on arbitrary input sequences, with held-out evaluation on a chromosome-distinct test set.

**Approach:** Generate a GC-matched 3' UTR background, split peaks and background by chromosome (train chr1-20, test chr21-22) to prevent gene-neighbor leakage, train RNAProt for 50 epochs at batch size 64, and evaluate held-out AUC against the ENCODE benchmark target of 0.85-0.89.

```bash
# Step 1: Prepare data
# Foreground: positive peaks from CLIPper / Skipper stringent set
# Background: GC-matched random regions from expressed transcripts
bedtools getfasta -fi genome.fa -bed peaks.stringent.bed -s -fo peaks.fa
bedtools shuffle -i peaks.stringent.bed -g chrom.sizes -incl expressed.bed -seed 42 > bg.bed
bedtools getfasta -fi genome.fa -bed bg.bed -s -fo background.fa

# Step 2: Train RNAProt
RNAProt train \
    --in peaks.fa \
    --neg background.fa \
    --out model_dir \
    --epochs 50 \
    --batch-size 64 \
    --learning-rate 0.001 \
    --validation-split 0.2

# Step 3: Apply to query sequences
RNAProt predict \
    --model model_dir \
    --in query.fa \
    --out predictions.tsv

# Output: per-sequence binding probability
```

## RBPNet Sequence-to-Signal Workflow

```python
# Hypothetical RBPNet API - verify against current package
import rbpnet

# Training: needs per-nt crosslink count for each example
# Inputs: sequence windows (256 nt) around peaks
# Targets: per-base CL count vector from PureCLIP or CTK CITS

# Prepare data
X_train, y_train = rbpnet.load_clip_data(
    peaks_bed='peaks.bed',
    crosslinks_bed='pureclip_sites.bed',
    genome_fa='genome.fa',
    window_size=256
)

# Train
model = rbpnet.RBPNet(
    seq_length=256,
    out_length=256,
    conv_layers=4,
    filters=128
)
model.train(X_train, y_train, epochs=50, batch_size=32, val_split=0.2)

# Predict per-base CL distribution
predictions = model.predict(novel_sequences)
```

## Per-Tool Failure Modes

### Training data imbalance

**Trigger:** Peak set 10k positive vs 100k negative background.

**Mechanism:** Class imbalance biases model toward negative class; specificity high but sensitivity low.

**Symptom:** AUC reported at 0.95 but precision-recall at peak threshold poor; few sites recovered.

**Fix:** Balanced sampling (1:1 positive:negative) or class weights. RNAProt does this automatically; DeepCLIP / DeepRiPe require manual balancing.

### Background mismatch

**Trigger:** Random shuffled background not matched to peak transcript context (e.g., peaks from 3' UTRs, background from CDS).

**Mechanism:** Model learns transcript-region differences (AU-content of 3' UTR vs CDS), not RBP specificity.

**Symptom:** Top predicted sites all in 3' UTRs regardless of test sequence; motif analysis shows AU-rich without RBP motif.

**Fix:** Match background to same region as foreground (3' UTR peaks -> 3' UTR background). Use the GC-content matched shuffle.

### Test on training data leak

**Trigger:** Splitting train/test by random shuffle.

**Mechanism:** Adjacent peaks in genome share evolutionary context; random split leaks training peaks near test peaks.

**Symptom:** Held-out AUC > 0.95 in benchmark but fails on truly novel sequences.

**Fix:** Split by chromosome (e.g., train chr1-20, test chr21-22). Or split by gene (no two peaks in same gene across splits).

### GPU requirement underestimated

**Trigger:** RNAProt / RBPNet training on CPU only.

**Mechanism:** Modern RBP DL models have 1-10M parameters; training requires GPU (or 100x slower on CPU).

**Symptom:** Training time > 24 h on CPU; convergence unstable.

**Fix:** Use Google Colab GPU; AWS EC2 GPU instance; or restricted-architecture model for CPU.

### Variant-effect prediction window size

**Trigger:** Variant-effect prediction with too narrow window around the variant.

**Mechanism:** RBP context extends 50-200 nt; window < 100 nt misses long-range context.

**Symptom:** Variant effect estimates noisy; same model gives different effects on different windows.

**Fix:** Use the model's native window size (256 nt for RBPNet); for shorter windows, average across multiple shifted predictions.

### Pretrained models lack the target RBP

**Trigger:** Looking for pretrained DeepRiPe / RBPNet for an uncommon RBP.

**Mechanism:** Only ~150 ENCODE-tested RBPs have pretrained models; thousands of RBPs are not.

**Symptom:** No pretrained available for the protein of interest.

**Fix:** Train custom model on new CLIP data using RNAProt or DeepCLIP. Or use transfer learning from a related RBP (closest paralog).

### Structure prediction integration

**Trigger:** GraphProt2 with `--structure` flag without RNA-Fold structure ensemble.

**Mechanism:** GraphProt2 needs structure ensemble (RNAfold output) as input; without it the GCN cannot leverage structure.

**Symptom:** GraphProt2 performance no better than sequence-only models.

**Fix:** Pre-compute RNAfold ensemble for each training sequence; pass to GraphProt2 input. Or use sequence-only DeepCLIP if structure is not needed.

### Model interpretation via saliency

**Trigger:** Want to recover RBP motif from trained model.

**Mechanism:** Saliency / integrated gradients on trained model produces per-base importance scores; sum across many positive examples gives a motif.

**Symptom:** Saliency results noisy; no clean motif emerges.

**Fix:** Use TF-MoDISco (Shrikumar et al 2018) for cleaner motif extraction from saliency maps. Or use DeepLIFT scores instead of vanilla saliency.

## Decision Tree by Use Case

| Scenario | Model | Why |
|----------|-------|-----|
| Variant-effect prediction (genome-wide GWAS variants) | RBPNet (per-base) | Single-nt resolution; predicts CL distribution |
| Binary "is this sequence bound" | RNAProt | Best AUC in benchmark (87-89%) |
| Structure-aware prediction | GraphProt2 | Structure ensemble integration |
| Custom training on new CLIP data | RNAProt (easiest CLI) | Fast training; CLI tool |
| Single RBP, no pretrained | Train custom RNAProt | Most accessible framework |
| Multi-task across RBPs | Basenji-style | Joint learning |
| Transfer learning from foundation model | RNA-FM + fine-tune | New approach; not yet in production |
| Production scoring of many sequences | DeepCLIP (fast inference) | Throughput |
| Motif interpretation | DeepRiPe + TF-MoDISco | Interpretable architectures |
| Comparing in silico to RBNS | RBPNet or DeepRiPe + RBNS Kd correlation | Calibration |
| Variant effect at heterozygous SNP | RBPNet | Per-base output |

## Reconciliation: Model Predictions vs CLIP / RBNS

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Model predicts site; CLIP misses | Model false positive; or transient binding not captured by CLIP | Check RBNS prediction; in vitro Kd |
| Model predicts low; CLIP has strong peak | Model false negative; or non-canonical / context-dependent | Investigate training data; structure-dependent? |
| Model AUC 0.95 in test; fails on novel sequences | Train/test leakage; chromosome split needed | Re-train with proper split |
| Variant effect log2 FC inconsistent across windows | Window-size sensitivity | Use model native window; average across shifts |
| Pretrained for related RBP works on target | Cross-RBP transfer | Transfer learning may work for paralogs |
| GraphProt2 underperforms sequence-only | Structure ensemble not provided | Fix structure input |
| Saliency motif noisy | Vanilla gradient method | Use DeepLIFT or TF-MoDISco |
| Train/test split by random outperforms chromosome split | Leakage from gene-neighbor sequences | Trust chromosome-split AUC |

**Operational rule for high-confidence variant-effect:** (a) Use RBPNet per-base output; (b) compute log2 FC at variant position summed over 50 nt window; (c) cross-validate with another model (DeepRiPe); (d) cross-reference with overlapping eCLIP peak if available; (e) report |log2 FC| > 1 as strong effect.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| AUC 0.5 on test | Train data leak or random shuffle | Verify chromosome split |
| Model trained on 1 epoch | Default optimizer state | Train 30-50 epochs with validation |
| GPU OOM | Batch size too large | Reduce batch size to 32 |
| Variant effect log2 FC very large (> 10) | Reference sequence not in training distribution | Verify input sequence reasonable |
| Pretrained model not found | RBP not in pretrained list | Train custom; or use closest paralog |
| Structure flag without input | GraphProt2 misuse | Pre-compute RNAfold structure |
| Saliency map flat | Model architecture too shallow | Use DeepRiPe / RBPNet (deeper) |
| Per-class accuracy uneven | Class imbalance | Use balanced sampling or class weights |
| Cross-RBP transfer fails | RBPs unrelated | Limit transfer to paralogs or use foundation model |
| Custom training crashes | RAM / GPU exhausted | Smaller batch; cache embeddings |

## References

- Alipanahi B et al 2015 Nat Biotechnol 33:831 (DeepBind, first DL RBP model)
- Maticzka D et al 2014 Genome Biol 15:R17 (GraphProt with structure)
- Uhl M et al 2021 bioRxiv 850024 (GraphProt2 with GCN; preprint)
- Gronning AGB et al 2020 Nucleic Acids Res 48:7099 (DeepCLIP)
- Ghanbari M, Ohler U 2020 Genome Res 30:214 (DeepRiPe multi-modal)
- Pan X, Shen HB 2018 Bioinformatics 34:3427 (iDeepE)
- Budach S, Marsico A 2018 Bioinformatics 34:3035 (Pysster)
- Uhl M et al 2021 GigaScience 10:giab054 (RNAProt RNN)
- Horlacher M, Wagner N, Moyon L et al 2023 Genome Biol 24:180 (RBPNet sequence-to-signal at single-nt)
- Shrikumar A et al 2018 arXiv (TF-MoDISco interpretation)
- Chen J et al 2022 arXiv:2204.00300 (RNA-FM foundation model, preprint)
- Wang N et al 2024 Nat Mach Intell 6:548 (RNAErnie)

## Related Skills

- clip-seq/clip-motif-analysis - Motif analysis is the classical alternative
- clip-seq/crosslink-site-detection - Single-nt CL sites for sequence-to-signal models
- clip-seq/clip-peak-calling - Peak BEDs for binary classification training
- causal-genomics/mendelian-randomization - Variant-effect predictions feed MR
- causal-genomics/fine-mapping - Variant prioritization with model scores
- machine-learning/model-validation - Train/test split methodology
- machine-learning/prediction-explanation - Saliency / attribution methods
- machine-learning/biomarker-discovery - Generic ML framework
<!-- END FILE: clip-seq/clip-deep-learning/SKILL.md -->

## 子目录：clip-seq/clip-motif-analysis

<!-- BEGIN FILE: clip-seq/clip-motif-analysis/SKILL.md -->
---
name: bio-clip-seq-clip-motif-analysis
description: Discover RBP binding motifs from CLIP-seq peaks or single-nucleotide crosslink sites using HOMER, MEME/STREME, kpLogo, mCross (CL-position-registered motifs), PEKA (positional k-mer enrichment), RBPamp (affinity), and RNA Bind-n-Seq (RBNS) cross-validation. Use when characterizing RBP sequence specificity, registering motifs to crosslink positions, validating in vivo CLIP motifs against in vitro RBNS Kd, reconciling motif disagreements across tools, or correcting for the uracil crosslinking bias that contaminates raw CLIP motif logos.
tool_type: mixed
primary_tool: HOMER
---

## Version Compatibility

Reference examples tested with: HOMER 4.11+, MEME Suite 5.5+ (STREME, MEME-ChIP, FIMO), bedtools 2.31+, kpLogo 1.1+, mCross v1+, PEKA v1+, RBPamp 0.9+, ggseqlogo 0.1+, biopython 1.83+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws unexpected errors, introspect the installed tool and adapt the example to match the actual API rather than retrying.

# CLIP-seq Motif Analysis

**"Find enriched RNA motifs at my RBP binding sites"** -> Discover the in vivo sequence preference of an RNA-binding protein from CLIP-seq peaks or single-nucleotide crosslink sites. The fundamental confound is the uracil bias of UV254 crosslinking: U is the most-crosslinked base, so naive motif logos centered on CL positions are U-enriched even for non-U-binding RBPs. Modern tools (mCross, PEKA) register motifs relative to the CL position and correct for this bias; legacy tools (HOMER, MEME) need careful background selection.

- CLI (de novo, peak-based, HOMER RNA mode): `findMotifs.pl peaks.fa fasta motif_out -rna -len 5,6,7,8 -p 4`
- CLI (de novo, peak-based, MEME-ChIP / STREME): `streme --rna --oc streme_out -p peaks.fa -n background.fa --minw 5 --maxw 10`
- CLI (positional, single-nt CL-registered, mCross): `mCross -i crosslinks.bed -g genome.fa -k 7 -o mcross_out` (jointly models motif + CL position)
- CLI (positional k-mer, no input control needed, PEKA): `peka --peak_file_name peaks.bed --crosslinks_file_name crosslinks.bed --genome_file_name genome.fa --regions_file_name regions.bed --kmer_length 5 --percentile 30 --outpath peka_out` (the short flags `-i/-x/-g/-r/-k/-p` shown in earlier docs are not all stable; use the long forms or check `peka --help`)
- CLI (affinity-weighted, RBPamp): `rbpamp run -i peaks.fa -k 7 -o rbpamp_out` (joint affinity + motif model)
- CLI (positional logo, kpLogo): `kpLogo crosslinks_with_kmer_scores.txt -o kplogo_out` (position-specific significance)

ENCODE eCLIP motif convention: extract sequences from peaks (CLIPper + SMInput stringent), use shuffled or expression-matched background, run HOMER `-rna -len 5,6,7,8`. The Yeo lab eCLIP papers typically report the top 1-3 HOMER hits per RBP and validate with mCross for CL-registered position. For ASB and variant-effect work, mCross is mandatory.

## Algorithmic Taxonomy

| Tool | Input | Background | CL-position aware | Output | Strength | Fails when |
|------|-------|------------|-------------------|--------|----------|------------|
| HOMER findMotifs.pl | Peak FASTA | Auto-shuffled or user-provided | No | PWM + de novo + known scan | Mature, fast, RNA mode (U instead of T) | Background generation is heuristic; uracil bias inflates U-content motifs |
| MEME (MEME Suite) | Peak FASTA | Optional Markov model | No | PWM | Statistically rigorous; broadly cited | Slow on large peak sets (> 1000 sequences); single-motif default |
| STREME (MEME Suite) | Peak FASTA | Shuffled or user-provided | No | PWM | Fast successor to MEME-ChIP; tolerant of large sets | Same uracil bias issue as HOMER |
| MEME-ChIP | Peak FASTA | Markov order 1-3 | No | Multiple motifs | Wrapper for MEME + CentriMo + Tomtom comparison | Designed for ChIP; for CLIP use STREME directly |
| kpLogo | k-mer scores with positions | NA (significance from kpLogo internals) | Yes (positional) | Position-specific logo | Visualizes position-specific signal; complements PWM | Requires k-mer-score input file; not a peak-to-motif tool by itself |
| mCross (Feng 2019) | Single-nucleotide CL sites + genome | Generated internally | Yes (jointly models motif + CL position) | Registered PWM + CL offset | The standard for in vivo RBP motif registration; SRSF1 example showed clustered GGA half-sites | Requires high-quality single-nt CL sites (PureCLIP or CTK CITS) |
| PEKA (Kuret 2022) | Peaks + crosslink BED | Low-count crosslinks within same dataset | Yes (positional k-mer) | Position-enriched k-mers with significance | No external input required; cross-validates with mCross | Less granular than mCross's jointly-modeled PWM |
| RBPamp (Jens 2022) | Peak FASTA or CL sites | Joint affinity model | No (affinity-based) | Affinity-weighted motif + Kd estimate | Provides Kd; compatible with RBNS calibration | Slow; small community; needs validation |
| RCAS | Peak BED + GTF | Auto | No | Motif + region annotation | One-stop for motif + region distribution | Less granular than per-tool dedicated runs |
| MEME FIMO (motif scan) | PWM + FASTA | Markov bg | No | Match locations and scores | Scan known motifs across genome | Not a de novo tool; complements HOMER known scan |
| RBPNet (Horlacher et al 2023) | Raw sequence | Trained model | Yes (sequence-to-signal at single nt) | Predicted CL count distribution | Deep learning; predicts per-base affinity profile | See clip-seq/clip-deep-learning |

Methodology evolves; verify motif comparison databases (CISBP-RNA, ATtRACT, oRNAment, mCrossBase, RBPDB) for known motif validation. RBNS in vitro Kd values (Lambert 2014; Dominguez 2018 for 78 RBPs) are the most reliable orthogonal reference for in vivo CLIP motifs.

## Critical Choice: Peak-Based vs Crosslink-Site-Based Motif Discovery

**Peak-based (HOMER, MEME/STREME, RBPamp):** Extract sequences from peak BED, find enriched k-mers / PWMs. Produces classical motif logos. Fast and intuitive. Captures broad binding zones.

**Crosslink-site-based (mCross, PEKA, kpLogo):** Use single-nucleotide CL positions; analyze sequence in a window around each CL position. Produces motif logos REGISTERED to the CL site. Required for understanding the structural relationship between motif and crosslink.

The fundamental difference: peak-based logos show "what sequence is enriched near binding"; CL-registered logos show "what sequence the RBP contacts at the crosslink position." For most RBPs they agree on the core motif but diverge on flanking context.

## Uracil Crosslinking Bias

UV254 crosslinking is U-biased: single-nt CL events are strongly enriched at U residues (Konig 2010; Sugimoto 2012). Consequence: motif logos centered on raw CL positions are U-enriched at the center even for non-U-binding RBPs (e.g., PUM2 binds UGUANAUA but peak-center is shifted; HNRNPK binds C-rich tracts but centers can show spurious U).

**Mitigations:**
- Use peak boundaries, not single-nt CL, for HOMER/MEME (peak-level averaging dilutes the U bias).
- Use mCross or PEKA, which explicitly model the CL position offset from the motif center.
- Shuffle background should preserve mononucleotide composition (HOMER default does; MEME with `--markov-order 1` does).
- For PAR-CLIP, the bias is at U residues but T->C marks the EXACT CL position; mCross / PEKA register more cleanly than for iCLIP/eCLIP.

For naive HOMER/MEME output, examine the central column of the PWM: if it is U-skewed, suspect CL bias rather than true U preference. Cross-check against published RBNS Kd if available.

## Per-Tool Failure Modes

### HOMER -- Background mismatch inflates GC-biased motifs

**Trigger:** HOMER auto-generates a shuffled background that preserves only nucleotide frequency, not GC distribution per region; CLIP peaks come disproportionately from 3' UTRs which are AU-rich.

**Mechanism:** AU-rich foreground vs GC-shuffled background produces "AU-rich motif" as the top hit for any 3' UTR-binding RBP, regardless of biology.

**Symptom:** Top HOMER motif looks like the 3' UTR mean composition (AU-rich, no clear specificity); known motif scan (`-known`) finds the RBP's canonical motif at lower rank than the spurious "AU" motif.

**Fix:** Provide a GC-matched background: extract sequences from random 3' UTR regions of expressed transcripts matched by length distribution. Use `-bg matched_bg.fa` flag. Or use STREME with `-n matched_bg.fa`.

### MEME -- Slow on large peak sets

**Trigger:** MEME run on > 1000 peak sequences.

**Mechanism:** MEME is O(N^2) in sequence count; classical OOPS/ZOOPS/ANR models do not scale.

**Symptom:** Runtime > 12h; out-of-memory on large machines.

**Fix:** Use STREME (MEME Suite >= 5.0); it is the modern fast successor (sub-quadratic). Or restrict to top-1000 peaks by score.

### mCross -- Requires single-nt CL sites

**Trigger:** mCross run on a peak BED instead of crosslink BED.

**Mechanism:** mCross's model is `motif_PWM x CL_position_offset_PMF`. Without single-nt CL positions there is no offset axis; the model degenerates.

**Symptom:** mCross output looks identical to a peak-centered logo; the diagnostic CL-offset histogram is flat.

**Fix:** Provide CL sites from PureCLIP, CTK CITS, or PARalyzer. The Yeo lab and Zhang lab use the convention of PureCLIP CL sites as mCross input.

### PEKA -- Background from same dataset

**Trigger:** Concerned that PEKA's "low-count crosslinks within same dataset" background is biased.

**Mechanism:** PEKA does NOT need external input. It uses low-count crosslinks (below a quantile threshold) as the background and high-count crosslinks (above) as the foreground. This is by design (Kuret 2022) and cross-validated against mCross.

**Symptom:** False positive concern; user wants to verify.

**Fix:** Run BOTH PEKA and mCross; cross-validate. The PEKA paper reports high concordance with mCross for ENCODE RBPs; treat them as orthogonal confirmation.

### RBPamp -- Slow convergence

**Trigger:** Large peak set (> 5000); RBPamp jointly optimizes affinity + motif iteratively.

**Mechanism:** Joint optimization is slow; some RBPs have multimodal binding (multiple motifs) that confuse single-PWM RBPamp.

**Symptom:** Runtime > 24h; output PWM disagrees with HOMER top motif.

**Fix:** Down-sample to top-2000 peaks; or run HOMER for initial PWM and use it as RBPamp seed.

### RBNS comparison -- in vitro vs in vivo divergence

**Trigger:** Comparing CLIP-derived motif to RBNS Kd-ranked motif (Dominguez 2018) and finding divergence (e.g., CLIP top motif rank 3 in RBNS; RBNS top motif weakly enriched in CLIP).

**Mechanism:** In vivo binding is shaped by structure accessibility (RNA secondary structure), cooperativity, and competing factors. RBNS measures intrinsic affinity in vitro. They diverge for:
- Structurally regulated RBPs (PUM2, RBFOX2 favor accessible loops)
- Cooperative binders (FUS, TDP-43, SR proteins)
- Co-factor-dependent (SRSF1 paralogs)

**Symptom:** CLIP motif logo plausible but rank-3 in RBNS; or RBNS top motif missing from CLIP peaks.

**Fix:** Accept the divergence as informative. Cite both. Use SHAPE-eCLIP or icSHAPE-MaP to test structural-accessibility hypothesis. For variant-effect studies, prefer RBNS-derived PWM (RBPamp Kd) over CLIP motif for absolute affinity prediction.

### Known motif scan -- FIMO threshold too lenient

**Trigger:** Used FIMO with default `-thresh 1e-4` and got matches everywhere.

**Mechanism:** Default threshold is too lenient for in vivo binding; CLIP background sequences contain many low-affinity matches.

**Symptom:** FIMO match rate > 50% of peaks AND > 20% of random background; no enrichment signal.

**Fix:** Use `-thresh 1e-5` or `-thresh 1e-6`; or use CentriMo for local enrichment around peak center (testing positional enrichment, not threshold).

## Decision Tree by Scenario

| Scenario | Tool | Why |
|----------|------|-----|
| Quick de novo motif from CLIPper peaks, ENCODE-comparable | HOMER `-rna -len 5,6,7,8` with GC-matched bg | Fast, mature, ENCODE convention |
| Motif registered to crosslink position (for variant effect) | mCross on PureCLIP single-nt sites | The 2019 Feng paper is the canonical reference |
| Confirm mCross result with independent method | PEKA on same peaks + crosslinks | Cross-validation; PEKA does not need input control |
| Affinity-weighted motif with Kd estimate | RBPamp | Provides quantitative Kd; integrates with RBNS comparison |
| Compare to in vitro RBNS Kd | RBPamp + Dominguez 2018 / Lambert 2014 tables | RBNS is the orthogonal in vitro standard |
| RBP with known motif - validation scan | FIMO -thresh 1e-5 against CISBP-RNA / ATtRACT PWM | Lower-confidence motifs need tight threshold |
| Multiple binding modes (SRSF1 GGA clusters) | mCross + manual inspection of CL-offset histogram | mCross reveals the multimodal structure |
| Position-specific logo (5' vs 3' of CL) | kpLogo with k-mer scores | Position-specific significance visualization |
| AU-rich 3' UTR binders (HuR, AUF1) - validate U bias is real | Compare HOMER motif center vs PUM2-style register | RBP-specific tradition |
| Allele-specific motif (variant effect) | mCross PWM + DeepRiPe/RBPNet for variant scoring | See clip-seq/clip-deep-learning |
| snoRNA / structural RNA - sequence motif less meaningful | Skip motif analysis; emphasize structural context (icSHAPE) | snoRNA binders read structure, not linear sequence |

## Reconciliation: When Motif Tools Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| HOMER and STREME agree; mCross disagrees on flanking | mCross's CL-offset registers a flanking base that's identical in peak; HOMER sees both flanking bases as motif | Trust mCross for CL-registered position; HOMER is "what's nearby" |
| Top HOMER motif AU-rich; RBP knows to bind structure | GC-matched background not used | Re-run HOMER with `-bg matched_bg.fa` |
| HOMER finds canonical motif at rank 1; RBNS Kd ranks at rank 3 | In vitro vs in vivo specificity divergence | Both valid; cite RBNS for absolute affinity, CLIP for in vivo prevalence |
| mCross PWM has multiple CL-position peaks | Multiple binding modes (SRSF1 GGA half-sites; PTBP1 multimer) | Treat as biologically meaningful; report both |
| Skipper window-level motifs differ from CLIPper peak-level | Window size dilutes signal; peak boundaries sharpen | Both valid; report at the level of the downstream analysis |
| PAR-CLIP motifs cleaner than iCLIP for same RBP | PAR-CLIP T->C registers exactly; iCLIP truncates -1 from CL | Both correct; PAR-CLIP is the sharper single-nt method when 4SU labeling tolerated |
| HOMER finds different motif on top vs bottom strand | Strand information lost in upstream BED | Verify BED column 6 (strand) is preserved; HOMER respects strand |

**Operational rule for high-confidence motif reporting:** Report (a) HOMER top de novo motif with GC-matched background, (b) mCross PWM with CL-position offset histogram, (c) PEKA k-mer enrichment for orthogonal confirmation, (d) FIMO scan against published RBP PWM (CISBP-RNA / ATtRACT) for known-motif validation, (e) RBNS Kd ranking from Dominguez 2018 if available. Three independent methods agreeing on the core motif is the bar.

## Workflow: De Novo + Known + CL-Registered

**Goal:** Produce a publication-grade motif report combining peak-based de novo discovery, CL-position-registered motif (mCross), and known-motif validation.

**Approach:** Extract sequences with strand preservation, build a GC-matched 3' UTR background, run HOMER + STREME for de novo, mCross for CL-registered, FIMO scan against CISBP-RNA, and report all three views with information-content QC.

```bash
# Step 1: Extract peak sequences (use stringent peak set: log2 FC >= 3, -log10 p >= 3)
bedtools getfasta -fi genome.fa -bed peaks.stringent.bed -s -fo peaks.fa

# Step 2: GC-matched background (random regions from expressed transcripts)
# expressed.bed = transcripts with TPM >= 1 in the same cell type
shuffleBed -i peaks.stringent.bed -g chrom.sizes -incl expressed.bed -seed 42 > shuffled.bed
bedtools getfasta -fi genome.fa -bed shuffled.bed -s -fo background.fa

# Step 3: HOMER de novo + known
findMotifs.pl peaks.fa fasta homer_out \
    -rna -len 5,6,7,8 -p 8 \
    -fasta background.fa

# Step 4: STREME for cross-validation
streme --rna --oc streme_out -p peaks.fa -n background.fa --minw 5 --maxw 10

# Step 5: mCross requires single-nt CL sites (PureCLIP output)
# crosslinks.bed = PureCLIP -o sites.bed (single-nt CL positions, see clip-seq/crosslink-site-detection)
mCross \
    -i crosslinks.bed -g genome.fa -k 7 -n 5 -o mcross_out

# Step 6: PEKA orthogonal positional k-mer
peka --peak_file_name peaks.stringent.bed --crosslinks_file_name crosslinks.bed --genome_file_name genome.fa --regions_file_name regions.bed --kmer_length 5 --percentile 30 --outpath peka_out

# Step 7: Compare to RBNS in vitro Kd (Dominguez 2018 supplementary)
# Manual cross-reference to RBNS Kd-ranked top-5 motifs for the target RBP
```

## Quality Checks

```python
import numpy as np
import pandas as pd
from Bio import motifs

def parse_homer_motif(motif_file):
    '''Parse HOMER motif PWM and return information content'''
    pwm = []
    with open(motif_file) as f:
        for line in f:
            if line.startswith('>'):
                continue
            pwm.append([float(x) for x in line.strip().split()])
    pwm = np.array(pwm)
    # Information content per position (bits)
    epsilon = 1e-10
    ic = np.sum(pwm * np.log2(pwm / 0.25 + epsilon), axis=1)
    return {
        'length': pwm.shape[0],
        'mean_IC_per_position': np.mean(ic),
        'max_IC': np.max(ic),
        'min_IC': np.min(ic),
        'is_low_complexity': np.mean(ic) < 0.5
    }

# A high-quality CLIP motif has mean IC per position > 1.0 bit
# Mean IC < 0.5 suggests no real motif - check for background mismatch
```

| Metric | Good | Investigate |
|--------|------|-------------|
| Mean IC per position (HOMER PWM) | > 1.0 bit | < 0.5 = no real motif or background mismatch |
| Motif center U content | matches RBP biology | > 80% U in central position = U-CL bias suspect |
| FIMO scan rate in peaks vs background | peaks 3-10x bg | < 2x = motif too weak; > 50x = motif too narrow |
| mCross CL-offset histogram | single mode at offset N | flat = mCross unable to register |
| RBNS rank of CLIP top motif | top 3 | > 10 = strong in vivo / in vitro divergence; investigate |
| Replicate motif overlap | top motif identical in 2/2 reps | discordance = under-powered or one rep failed |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| HOMER top motif is "ATCC" or similar TruSeq-adapter-like | Adapter trim incomplete in preprocessing | Re-run cutadapt with correct adapter; verify trimming completed before peak calling |
| mCross "no crosslinks found" or output identical to peak-centered logo | Passed peak BED instead of single-nt crosslink-site BED | mCross requires PureCLIP or CTK CITS single-nt site BED; not a CLIPper peak BED. See clip-seq/crosslink-site-detection |
| mCross CL-offset histogram is flat | Strand information missing OR alignment soft-clipped 5' base | Verify BED column 6 (strand); confirm upstream `--alignEndsType EndToEnd` |
| All HOMER motifs are AU-rich, no specificity | Default shuffled background AU-rich for 3' UTR peaks | Provide GC-matched background from expressed 3' UTRs |
| mCross input "no crosslinks found" | Provided peak BED instead of single-nt CL BED | Pass PureCLIP / CTK CITS single-nt BED instead |
| MEME "out of memory" or > 12h runtime | Peak set too large | Switch to STREME; or down-sample to top-1000 peaks |
| FIMO match in nearly every peak | Threshold too lenient | Tighten to 1e-5 or 1e-6 |
| Motif width > 10 nt looks chimeric | HOMER reported overlapping co-motifs as one | Re-run with `-len 5,6,7,8` (force narrower); inspect rank 2-5 motifs |
| PWM info content < 0.5 bits | Background mismatch or peaks have no specificity | Verify peak set is stringent (log2 FC >= 3); regenerate background |
| Strand-specific motif different on +/- | BED column 6 missing or wrong | Verify strand encoding; re-extract with `bedtools getfasta -s` |
| Multiple distinct motifs per RBP | Biological (multimodal RBPs) OR contaminating multi-RBP CLIP | Validate with mCross multimode + compare to literature |

## References

- Heinz S et al 2010 Mol Cell 38:576 (HOMER motif discovery)
- Bailey TL et al 2015 Nucleic Acids Res 43:W39 (MEME Suite)
- Bailey TL 2021 Bioinformatics 37:2834 (STREME, MEME's fast successor)
- Wu X & Bartel DP 2017 Nucleic Acids Res 45:W534 (kpLogo positional logo)
- Feng H et al 2019 Mol Cell 74:1189 (mCross, jointly modeling motif + CL position)
- Kuret K, Amalietti AG, Jones DM, Capitanchik C, Ule J 2022 Genome Biol 23:191 (PEKA, positional k-mer no input)
- Jens M et al 2022 bioRxiv 2022.11.08.515616 (RBPamp, affinity-weighted motif; preprint)
- Lambert N et al 2014 Mol Cell 54:887 (RNA Bind-n-Seq)
- Dominguez D et al 2018 Mol Cell 70:854 (78-RBP RBNS atlas)
- Sugimoto Y et al 2012 Genome Biol 13:R67 (CLIP/iCLIP analysis; uridine crosslink preference)
- Van Nostrand EL et al 2020 Nature 583:711 (ENCODE 150 RBP eCLIP + motifs)
- Konig J et al 2010 Nat Struct Mol Biol 17:909 (iCLIP, U bias origin)

## Related Skills

- clip-seq/clip-peak-calling - Upstream peak calls feed motif discovery
- clip-seq/crosslink-site-detection - Single-nt CL sites required for mCross / PEKA
- clip-seq/binding-site-annotation - Region-level context for motifs
- clip-seq/clip-deep-learning - Sequence-to-binding deep models (RBPNet, DeepRiPe)
- clip-seq/ago-clip-mirna-targets - miRNA seed motifs from CLEAR-CLIP chimeras
- chip-seq/motif-analysis - DNA-protein motif analogue
- pathway-analysis/go-enrichment - Functional context of motif-bearing genes
<!-- END FILE: clip-seq/clip-motif-analysis/SKILL.md -->

## 子目录：clip-seq/clip-peak-calling

<!-- BEGIN FILE: clip-seq/clip-peak-calling/SKILL.md -->
---
name: bio-clip-seq-clip-peak-calling
description: Call protein-RNA binding sites from CLIP-seq BAM with CLIPper, PureCLIP, Skipper, Piranha, omniCLIP, CTK, CLAM, or Paraclu. Use when choosing between coverage-based, HMM-based, beta-binomial window-based, and crosslink-site-based peak callers; applying ENCODE eCLIP thresholds (log2 IP/SMInput >= 3, -log10 p >= 3); deciding when SMInput is mandatory; or reconciling peak-set discordance between callers for the same RBP.
tool_type: cli
primary_tool: CLIPper
---

## Version Compatibility

Reference examples tested with: CLIPper 2.0+, PureCLIP 1.3.1+, Piranha 1.2.1+, omniCLIP 0.2.0+, CTK 1.1.4+, CLAM 1.2+, Paraclu 9+, Skipper (commit 2023.05+), MACS3 3.0+, bedtools 2.31+, samtools 1.19+, idr 2.0.4+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed binary and adapt the example to match the actual CLI rather than retrying. PureCLIP 2.x changed several flag names; Skipper is distributed as a Snakemake workflow with frequently-evolving paths.

# CLIP-seq Peak Calling

**"Call protein-RNA binding sites from my deduplicated CLIP BAM"** -> Identify regions where read pile-up (and, for iCLIP/eCLIP, single-nucleotide truncations) exceed background from a size-matched input (SMInput) control. The choice of peak caller depends on (a) the CLIP variant (HITS-CLIP, iCLIP, eCLIP, PAR-CLIP), (b) whether SMInput is available, (c) the RBP binding mode (narrow motif vs broad zones vs repeat-binding), and (d) the goal (publication-comparable ENCODE peaks vs single-nucleotide crosslink sites vs high-recall site lists).

- CLI (ENCODE eCLIP canonical): `clipper -b dedup.bam -s hg38 -o peaks.bed --save-pickle --FDR-alpha 0.05 --superlocal` then `eclip-norm peaks.bed -i sminput.bam` for log2 fold-change against SMInput (`--FDR-alpha` is the CLIPper flag for the FDR cutoff; older docs sometimes shorten to `--FDR`)
- CLI (single-nucleotide crosslink sites, iCLIP/eCLIP): `pureclip -i dedup.bam -bai dedup.bam.bai -g genome.fa -ibam sminput.bam -ibai sminput.bam.bai -o sites.bed -or regions.bed -nt 8 -dm 8`
- CLI (high-recall, beta-binomial windowed; needs SMInput): `Skipper` Snakemake workflow with config matching cell type and SMInput BAM
- CLI (no SMInput, no truncation): `Piranha -b 50 -p 0.01 -d ZeroTruncatedNegativeBinomial -s -o peaks.bed dedup.bam` (Piranha takes the BAM as a positional argument, not via `-s`)
- CLI (CIMS/CITS single-nt from CTK): `tag2cluster.pl dedup.bed cluster.bed --multi-tag-method coverage`; then `bedExtractCIMS.pl cluster.bed cims.bed`
- CLI (multi-mapper rescue for repeat-binding RBPs): `CLAM peakcaller -i unique.bam multimap.bam -o clam_out_dir/ --gtf gencode.gtf` (CLAM peakcaller writes peaks into an OUTPUT DIRECTORY, not a single file)

The ENCODE eCLIP gold standard for "stringent" peaks is: log2(IP / SMInput) >= 3 AND -log10(p-value) >= 3. "Lenient" peaks use log2 >= 1 AND -log10 >= 2. Both filters operate on CLIPper peak output normalized against SMInput. Without SMInput, neither stringency level can be reproduced - the algorithm has no background term.

## Algorithmic Taxonomy

| Caller | Model | Resolution | SMInput required | Strength | Fails when |
|--------|-------|------------|------------------|----------|------------|
| CLIPper (Yeo) | Poisson with 500 bp local lambda, cubic-spline interpolation | Peak (10-500 nt) | Not for calling; required for ENCODE normalization | ENCODE eCLIP standard; reproducible against published ENCODE peak sets | Assumes most reads not from binding; fails when IP signal dominates a gene; sensitive to highly expressed transcripts |
| PureCLIP (Krakau 2017) | Non-homogeneous HMM jointly modeling enrichment + truncation + sequence biases | Single-nucleotide CL + broad region | Optional via -ibam; recommended | Single-nt resolution; only caller that explicitly models the iCLIP truncation pattern | Misses broad binding zones; very focal (low recall on broad-binding RBPs in the Boyle 2023 benchmark) |
| Skipper (Boyle 2023) | GC-stratified beta-binomial, 100 bp feature-respecting windows | Window (~100 nt) | Mandatory | 210-320% more sites than CLIPper; 8x faster; properly normalizes against input | Loses single-nt resolution; relatively new (2023); fewer published peak sets to compare |
| Piranha (Smith lab) | Zero-truncated negative binomial regression with optional covariates | Bin (50-200 nt) | Optional; pass as covariate | Mature, widely cited, handles count overdispersion | Biased toward high-expression transcripts; convergence fails with large covariate values (use `-l` log-space) |
| omniCLIP (Drewe-Boss 2018) | Non-homogeneous HMM with Dirichlet-multinomial of variants | Peak | Required | Models replicate variance; integrates background; can call peaks on any CLIP variant | Slow on deep libraries; blind to mitochondrial transcripts (misses chrM windows for FASTKD2) |
| CTK CIMS/CITS (Shah 2017) | Empirical FDR on crosslink-induced mutations or truncations | Single-nucleotide | No (uses background mutation rate from non-bound transcripts) | Single-nt resolution; works on HITS-CLIP deletions, PAR-CLIP T->C, iCLIP truncations | Empirical FDR less principled than HMM/beta-binomial; perl-based pipeline harder to integrate |
| CLAM peakcaller (Zhang & Xing 2017) | EM-assigned multi-mapper count + Piranha-like negative binomial | Peak | Optional | Only solution for repeat-binding RBPs; 10-30% additional sites in repeats | Inherits Piranha limitations on coverage-based stats; slower than Piranha |
| Paraclu (Frith) | Parametric clustering with min-density and max-density thresholds | Variable | No | Simple, parameter-tunable, works on bedgraph | Heuristic; no statistical significance; cluster boundaries sensitive to thresholds |
| PIPE-CLIP | Online CLIP pipeline with custom peak caller | Peak | Optional | Web interface; integrated end-to-end | Slow on cloud; less customizable; community has moved on |
| CLIPick (Park 2018) | Expression-deconvolved peak caller | Peak | No (RNA-seq used instead) | Models RNA-seq abundance as background | RNA-seq cannot capture nonspecific binding; less popular post-Skipper |
| Flipper (Flanagan 2026) | Negative-binomial differential test downstream of Skipper | Window | Yes | Companion differential tool to Skipper | Only meaningful in differential context; see clip-seq/differential-clip |
| MACS3 callpeak | Local Poisson | Peak | Optional (treats SMInput as ChIP-seq input) | Familiar, fast | Not designed for CLIP; misses truncation signal; produces wider-than-typical peaks |

Methodology evolves; verify the current ENCODE eCLIP standard operating procedure (encodeproject.org/eclip) and the nf-core/clipseq pipeline configuration before locking on a single caller. The 2023 Skipper benchmark (Boyle Cell Genomics) is the most recent comprehensive comparison and is the rationale for many recent eCLIP reanalyses.

## Critical Choice: Coverage-Based vs Crosslink-Site-Based vs Window-Based

Three fundamentally different statistical frameworks:

**Coverage-based (CLIPper, Piranha, MACS3, Paraclu):** Tally reads in a window; significance from local Poisson or negative binomial. Produces multi-nt peaks. Best when binding zones are broader than the read footprint (PUM2 3' UTR, HuR ARE elements).

**Crosslink-site-based (PureCLIP, CTK CIMS/CITS, PARalyzer):** Identify single nucleotides enriched in truncations (iCLIP/eCLIP) or specific mutations (PAR-CLIP T->C, HITS-CLIP deletions). Produces single-nt sites that can be aggregated into footprints. Best when single-nt resolution is essential (motif registration with mCross; allele-specific binding).

**Window-based (Skipper):** Tile transcriptome a priori into fixed-size feature-respecting windows; test each window's IP/IN ratio with beta-binomial. Produces window-level calls. Best when SMInput is available and the goal is high-recall, comparable-across-RBPs site sets.

| Goal | Recommended caller | Why |
|------|-------------------|-----|
| Reproduce ENCODE published peaks | CLIPper + IP/SMInput normalization | The Yeo lab pipeline is the canonical reference |
| Maximum sensitivity, modern statistics, SMInput available | Skipper | 210-320% more sites; explicit input normalization |
| Single-nucleotide crosslink-site map (motif registration, ASB) | PureCLIP (HMM) or CTK CITS (empirical) | True single-nt resolution |
| Repeat-binding RBP (Alu, LINE, LTR) | STAR multi-mapper + CLAM peakcaller | Only solution that uses multi-mappers |
| No SMInput control | Piranha or PureCLIP with no -ibam | Both work without input but lose specificity |
| PAR-CLIP T->C signature | PARalyzer or CTK CIMS (-substitution) | Designed for the T->C signal |
| HITS-CLIP deletion signature | CTK CIMS (-deletion) | Designed for the deletion signal |
| Custom statistical model needed | omniCLIP | Most flexible HMM among the options |
| Online interactive analysis | Galaxy CLIP-Explorer or PIPE-CLIP | Web interface |

## ENCODE eCLIP Stringency Thresholds

The Van Nostrand et al. ENCODE eCLIP standards define two stringency levels for CLIPper peaks normalized against SMInput:

| Stringency | log2(IP / SMInput) | -log10(p-value) | Use case |
|------------|--------------------|-----------------|----------|
| Stringent (publication) | >= 3 | >= 3 | High-confidence binding sites; differential analysis; motif discovery |
| Lenient (discovery) | >= 1 | >= 2 | Catalogue of all enriched windows; sensitive analyses |

Both thresholds are applied to the IDR-passing reproducible peak set. ENCODE requires:
- >= 2 biological replicates
- >= 1M unique fragments per replicate (or saturated peak detection)
- IDR rescue ratio and self-consistency ratio both < 2
- Narrow-binding RBPs: FRiP >= 0.005 (atypical-binding RBPs exempt)

```bash
# CLIPper -> SMInput normalization -> ENCODE thresholds
clipper -b dedup.bam -s hg38 -o peaks.bed --save-pickle --FDR-alpha 0.05 --superlocal

# Normalize against SMInput; eclip-norm is the Yeo lab tool
python overlap_peakfi_with_bam_PE.py peaks.bed dedup.bam sminput.bam dedup.bam.readnum.txt sminput.bam.readnum.txt peaks.normed.bed
python compress_l2foldenrpeakfi_for_replicate_overlapping_bedformat.py peaks.normed.bed peaks.compressed.bed

# Stringent filter: log2 FC >= 3, -log10 p >= 3
awk 'BEGIN{FS=OFS="\t"} $4 >= 3 && $5 >= 3' peaks.compressed.bed > peaks.stringent.bed

# Lenient
awk 'BEGIN{FS=OFS="\t"} $4 >= 1 && $5 >= 2' peaks.compressed.bed > peaks.lenient.bed
```

The Yeo lab scripts (`overlap_peakfi_with_bam_PE.py`, `compress_l2foldenrpeakfi_for_replicate_overlapping_bedformat.py`) live in the eclip-pipeline repository; they implement the exact log2 fold-change computation used for ENCODE data downloads.

## Per-Caller Failure Modes

### CLIPper -- High-expression transcript bias

**Trigger:** RBP that binds rare transcripts (snoRNAs, tRNAs, mitochondrial mRNAs) such as TROVE2 (Y RNA), NSUN2 (tRNA), or FASTKD2 (chrM).

**Mechanism:** CLIPper's Poisson local-lambda model assumes only a minority of reads come from binding. For rare-transcript binders, the IP reads ARE the majority signal on that transcript; the model treats them as background.

**Symptom:** Per-transcript peak count plummets compared to qualitatively-visible IP signal; chrM peaks called by Skipper but missed by CLIPper for FASTKD2.

**Fix:** Use Skipper for rare-transcript binders (beta-binomial against SMInput respects the actual IP/IN ratio independently of local lambda). Or pre-restrict CLIPper to the target transcript with `--gene custom.bed`.

### CLIPper -- Requires SMInput downstream

**Trigger:** Submitting CLIPper output as "peaks" without IP/SMInput log2 normalization.

**Mechanism:** CLIPper's own p-value is uncorrected for SMInput background. ENCODE peak BED files distributed on the portal are CLIPper + SMInput log2 normalization combined.

**Symptom:** Peak count from the analysis is 5-10x higher than ENCODE values for the same RBP; the peak set includes obvious housekeeping-gene noise.

**Fix:** Always normalize CLIPper output against SMInput. The Yeo lab scripts (`overlap_peakfi_with_bam_PE.py` + `compress_l2foldenrpeakfi_for_replicate_overlapping_bedformat.py`) produce the canonical ENCODE-style peak.

### PureCLIP -- Too focal; misses broad binding zones

**Trigger:** RBP with broad binding mode (PUM2 in 3' UTR clusters; SR proteins across exonic enhancer regions); using PureCLIP and disappointed.

**Mechanism:** PureCLIP's HMM emits single-nt crosslink-site state at high stringency. In the Boyle 2023 Skipper benchmark, PureCLIP was highly focal with low recall on broad-binding RBPs (few true-positive windows).

**Symptom:** Site count 100x lower than expected; sites cluster within known binding regions but vast majority of region is "background" in PureCLIP output.

**Fix:** Use PureCLIP for single-nt CL maps (motif registration, ASB) but pair with CLIPper or Skipper for the broader binding-site list. PureCLIP's `-or` regions file gives broader output but is still focal compared to CLIPper.

### Piranha -- Top-expression-decile bias

**Trigger:** Highly expressed transcript (GAPDH, ACTB, rRNA-flanking) appears in most-significant Piranha peaks even when RBP biology is elsewhere.

**Mechanism:** ZTNB regression weights peak significance by absolute count, not relative enrichment. Genes with 10x baseline expression dominate the top of the peak list.

**Symptom:** Top-100 Piranha peaks include housekeeping genes; motif enrichment in top peaks is weak; functional GO term analysis of peak-bearing genes returns generic "cellular metabolism."

**Fix:** Use Piranha with SMInput as a covariate (`-c sminput_counts.bed -l`) so the regression accounts for input pile-up. Or switch to Skipper for principled input normalization.

### Piranha -- Convergence failure with covariates

**Trigger:** `-c rna_seq.bed` for expression normalization; large per-bin RNA-seq counts (> 10000).

**Mechanism:** ZTNB optimization fails on extreme covariate values; the iterative algorithm diverges.

**Symptom:** "Maximum iterations reached" or "Singularity in regression" error; or output BED file empty.

**Fix:** Pass `-l` to convert covariates to log-space; or pre-filter covariate BED to remove top-1% outlier bins; or switch to Skipper which handles input normalization internally.

### omniCLIP -- Mitochondrial transcript blind spot

**Trigger:** Mitochondrial RBP (FASTKD2, LRPPRC) submitted to omniCLIP.

**Mechanism:** omniCLIP's HMM is trained on autosomal/X transcripts; chrM has different background statistics that the model treats as outlier (or excludes if blacklisted).

**Symptom:** chrM peaks return 0; FASTKD2 peak file has no peaks at all.

**Fix:** Use Skipper for chrM-binding RBPs (GC-stratified beta-binomial is per-bin and indifferent to chromosome). Or call peaks on chrM separately with PureCLIP.

### CTK CIMS -- HITS-CLIP only; iCLIP/eCLIP misuse

**Trigger:** CTK CIMS (`-mutation` flag) applied to iCLIP/eCLIP data.

**Mechanism:** iCLIP/eCLIP use truncation (RT stops at adduct), not mutations. CIMS expects deletions/substitutions inside the read; CITS is the truncation-based companion.

**Symptom:** CIMS returns very few sites (mutation rate of CL is ~3-7% for HITS-CLIP, but only ~1-2% for iCLIP since most reads truncate before reaching the adduct).

**Fix:** For iCLIP/eCLIP, use CTK CITS (`tag2cluster.pl ... -cs5 5` truncation-mode). For HITS-CLIP and PAR-CLIP, CIMS is correct (HITS deletions, PAR T->C).

### CLAM peakcaller -- Multi-mapper BAM absent

**Trigger:** Ran STAR with `--outFilterMultimapNmax 1` then tried CLAM; CLAM fails or returns identical output to Piranha.

**Mechanism:** CLAM's EM rescue requires the multi-mapper BAM from STAR (`--outFilterMultimapNmax 100 --outSAMmultNmax -1`). Without it, CLAM falls back to unique-only Piranha-style peak calling.

**Symptom:** CLAM output looks identical to Piranha; repeat peaks not rescued.

**Fix:** Re-align with multi-mapper-aware STAR parameters (see clip-seq/clip-alignment). Verify the multi-mapper BAM has alignments at non-unique positions before running CLAM.

### MACS3 callpeak -- Wide peaks miss footprint

**Trigger:** MACS3 used because the user is familiar from ATAC/ChIP work.

**Mechanism:** MACS3 model is for DNA-protein binding at ~100-500 nt scale; CLIP-seq RBP footprints are 8-30 nt. MACS3 wide peaks (300+ nt) merge multiple distinct binding sites.

**Symptom:** MACS3 peak count is much lower than CLIPper/Skipper; mean peak width >> 100 nt; multiple known motif instances inside one MACS peak.

**Fix:** Use CLIP-specific callers. If MACS3 is forced (institutional pipeline), pass `--nomodel --shift -1 --extsize 50` for narrower peaks and accept the limitation.

## IDR for CLIP-seq

IDR (Li 2011) measures reproducibility of peak rankings across biological replicates. ENCODE eCLIP convention is per-rep + pooled + pseudoreplicates, identical to the ChIP-seq IDR pattern. The CLIP-specific consideration: rank by `signalValue` (column 7) NOT by `score` (column 5), because CLIPper's score is sparse and tied across many peaks.

```bash
# Per-replicate CLIPper + SMInput normalization yields .compressed.bed files
sort -k7,7nr rep1_peaks.compressed.bed > rep1.sorted
sort -k7,7nr rep2_peaks.compressed.bed > rep2.sorted

idr --samples rep1.sorted rep2.sorted \
    --input-file-type bed --rank 7 \
    --output-file idr.out --idr-threshold 0.05 \
    --plot --log-output-file idr.log
```

ENCODE IDR rules for eCLIP:
- Nt (true replicates) and Nself (pseudoreplicates): max(Nt, Nself) / min(Nt, Nself) <= 2 -> pass
- Both ratios > 2 -> library rejected
- IDR threshold 0.05 for true reps; 0.10 for pseudoreplicates

## Decision Tree by Scenario

| Scenario | Caller + parameters | Why |
|----------|---------------------|-----|
| Standard eCLIP with SMInput, ENCODE-comparable | CLIPper + SMInput log2 norm + IDR | Reproducible against ENCODE peak files |
| Standard eCLIP with SMInput, maximum sensitivity | Skipper Snakemake workflow | 210-320% more sites, beta-binomial input-norm |
| iCLIP/iCLIP2, want single-nt CL map | PureCLIP + SMInput (or empty bam if no SMI) | HMM jointly models enrichment + truncation |
| HITS-CLIP, want CIMS deletions | CTK `parseAlignment.pl` + `tag2cluster.pl` + `bedExtractCIMS.pl` | Empirical FDR on deletion-induced mutations |
| PAR-CLIP, T->C signal | PARalyzer or CTK CIMS `-substitution T C` | Designed for the T->C signature |
| Repeat-binding RBP (MATR3, LINE-1) | CLAM peakcaller on multi-mapper BAM | Only solution that recovers repeat peaks |
| No SMInput, mostly hopeless | Piranha `-d ZeroTruncatedNegativeBinomial` or PureCLIP w/o -ibam | Lose ENCODE comparability but get a peak set |
| Mitochondrial RBP (FASTKD2) | Skipper (window-based, chrM-friendly) | omniCLIP/CLIPper miss chrM |
| Highly multiplexed (SPIDR) | Custom Snakemake; no single-tool solution | Each barcode's reads are deep enough for CLIPper |
| Long-read CLIP (dirCLIP) | Custom analysis from BAM; long-read tools not yet mature | Isoform-resolved binding-site calls |
| Need maximum precision for motif analysis | PureCLIP (single-nt) + mCross downstream | mCross requires registered CL positions |
| Replicates with unequal library complexity (>2x diff in unique fragments) | Skipper (more robust to depth imbalance) OR `samtools view -s` down-sample to common depth then CLIPper + IDR | Skipper's GC-stratified beta-binomial handles per-sample depth; CLIPper without down-sampling lets the deeper replicate dominate joint analysis |

## Reconciliation: When Callers Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Skipper >> CLIPper site count | Skipper better recovers low-abundance and rare-transcript binders | Trust Skipper for rare transcripts; trust CLIPper for ENCODE-comparable counts |
| PureCLIP << CLIPper | PureCLIP is single-nt focal; CLIPper is broad peak | Both correct; report at the resolution the downstream analysis needs |
| Piranha top peaks dominated by housekeeping | No input normalization | Add SMInput as `-c` covariate or switch to Skipper |
| CLAM > Piranha by 10-30% | CLAM rescued multi-mappers in repeats | Trust CLAM if RBP biologically binds repeats |
| omniCLIP wider peaks than CLIPper | HMM smoothes binding state across nearby positions | Both correct; choose by downstream analysis needs |
| Per-rep CLIPper calls peak; pooled does not | Replicates inconsistent; one rep dominates | Inspect with IGV; trust IDR-passing peaks only |
| MACS3 < CLIPper peak count | MACS3 wide peaks merge multiple CLIP sites | Use CLIP-specific caller |
| FASTKD2 chrM peaks: Skipper finds; CLIPper / omniCLIP find none | Coverage-based callers blind to chrM lambda | Trust Skipper for organelle-binding RBPs |
| chimeric eCLIP peaks for snoRNA: standard tools find few | snoRNA-targeting eCLIP needs custom processing | Use VanNostrandLab/snoRNA-chimeric pipeline |

**Operational rule for high-confidence reporting:** Require a peak to pass (a) IDR <= 0.05 on true replicates, (b) log2(IP/SMInput) >= 3 AND -log10 p >= 3 (ENCODE stringent), (c) overlap with at least one independent caller within 100 nt. For motif analysis, additionally require PureCLIP single-nt sites within the peak. For ASB, require WASP-filtered alignment + PureCLIP CL sites overlapping heterozygous SNPs.

## Strand-Specific Peak Calling

CLIP libraries are strand-specific by design. Most callers handle strands correctly when the BAM is stranded (read flags 99/147/83/163 for paired). If a caller bug or unstranded library forces manual split:

```bash
# Plus strand reads (F flag NOT 0x10)
samtools view -h -b -F 16 dedup.bam > plus.bam
samtools index plus.bam
# Minus strand reads (F flag 0x10)
samtools view -h -b -f 16 dedup.bam > minus.bam
samtools index minus.bam

# Call peaks on each strand independently, then merge
clipper -b plus.bam -s hg38 -o peaks_plus.bed
clipper -b minus.bam -s hg38 -o peaks_minus.bed
cat peaks_plus.bed peaks_minus.bed | sort -k1,1 -k2,2n > peaks_stranded.bed
```

For paired-end CLIP, mate orientation determines strand: RF (R1 reverse) means R2 5' is the truncation = CL site -1 on plus-strand transcripts. ENCODE eCLIP convention: read 2 of pair is the truncation-bearing read.

## Multi-Mapper Rescue with CLAM (Repeat Binders)

```bash
# Assume STAR was run with --outFilterMultimapNmax 100 --outSAMmultNmax -1
samtools sort -o multimap.bam aligned_multimap.bam
samtools index multimap.bam

# Split unique vs multi
CLAM preprocessor -i multimap.bam -o clam_out/ --read-tagger-method median

# EM-based reassignment
CLAM realigner -i clam_out/unique.sorted.bam -o clam_out/ --winsize 50 --max-tags 0

# Peak calling with reassigned multi-mappers
CLAM peakcaller -i clam_out/unique.sorted.bam clam_out/realigned.sorted.bam \
    -o clam_peaks.bed -p 8 --gtf gencode.v38.annotation.gtf
```

CLAM rescues 10-30% additional peaks in repeat-rich regions. The trade-off: peak coordinates in repeat instances are probabilistic (single best from EM), so motif analysis on CLAM repeat peaks requires careful interpretation.

## Quality Metrics for Peak Sets

```python
import pandas as pd

def peak_qc(peaks_bed):
    peaks = pd.read_csv(peaks_bed, sep='\t', header=None,
                        names=['chrom','start','end','name','score','strand'])
    peaks['width'] = peaks['end'] - peaks['start']
    return {
        'n_peaks': len(peaks),
        'mean_width': peaks['width'].mean(),
        'median_width': peaks['width'].median(),
        'width_5p_95p': (peaks['width'].quantile(0.05), peaks['width'].quantile(0.95)),
        'chroms_with_peaks': peaks['chrom'].nunique(),
        'peaks_chrM': (peaks['chrom'] == 'chrM').sum()
    }
```

| Metric | Expected | Interpretation |
|--------|----------|----------------|
| n_peaks (CLIPper stringent) | 5k - 100k | <5k = under-IP or stringency too high; >>100k = noisy library |
| Mean peak width (CLIPper) | 40-200 nt | Wider = caller over-merging; narrower = under-coverage |
| Peak width 5-95% range | 20-500 nt | Tight range = consistent peaks; wide = mixed sharp + broad |
| FRiP (fraction reads in peaks) | >= 0.005 | ENCODE narrow-binding RBP minimum; many RBPs higher |
| chrM peaks | 0 unless mt-RBP | FASTKD2, LRPPRC expected to have chrM enrichment |
| TPM-rank distribution | Spread across deciles | Concentrated in top decile = caller has expression bias (Piranha symptom) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| CLIPper "no peaks found" | BAM not sorted/indexed; gene annotation missing | `samtools sort && index`; verify `-s hg38` (or `--gene custom.bed`) |
| CLIPper out-of-memory on 50M BAM | `--save-pickle` keeps intermediates in RAM | Remove `--save-pickle`; or use machine with > 64 GB |
| PureCLIP slow (>24h) | `-iv` interval file missing | Restrict to one chromosome with `-iv chr1` for testing; provide GTF |
| Piranha returns no peaks | ZTNB convergence failed silently | Add `-l`; or reduce `-b` bin size; or switch to Skipper |
| omniCLIP segmentation fault | Replicate BAMs differ in chromosome order | Re-sort all BAMs with identical reference dictionary |
| CTK CITS finds nothing on PAR-CLIP | Used CITS (truncation) for substitution data | Use CIMS `-substitution T C` for PAR-CLIP |
| Multi-mapper rescue returns 0 extra peaks | STAR was run unique-only; no multi-mapper BAM | Re-align with `--outFilterMultimapNmax 100 --outSAMmultNmax -1` |
| ENCODE stringent peak count = 0 | Forgot SMInput normalization step | Run Yeo lab `overlap_peakfi_with_bam_PE.py` first; thresholds apply to normalized peaks |
| Strand information lost | `samtools view -F 16` filter applied to merged BAM | Strand is encoded in BAM flags; do not pre-split |
| IDR returns no reproducible peaks | Wrong ranking column | Sort by signalValue / log2FC, not score; for narrowPeak format use `--rank p.value` |

## References

- Van Nostrand EL et al 2016 Nat Methods 13:508 (eCLIP, SMInput, ENCODE pipeline)
- Lovci MT et al 2013 Nat Struct Mol Biol 20:1434 (CLIPper algorithm)
- Krakau S et al 2017 Genome Biol 18:240 (PureCLIP HMM)
- Boyle EA et al 2023 Cell Genomics 3:100317 (Skipper, GC-stratified beta-binomial)
- Uren PJ et al 2012 Bioinformatics 28:3013 (Piranha, ZTNB)
- Drewe-Boss P et al 2018 Genome Biol 19:183 (omniCLIP)
- Shah A et al 2017 Bioinformatics 33:566 (CTK / CIMS / CITS)
- Zhang Z & Xing Y 2017 Nucleic Acids Res 45:9260 (CLAM multi-mapper)
- Frith MC et al 2008 Genome Res 18:1-12 (paraclu)
- Li Q et al 2011 Ann Appl Stat 5:1752 (IDR framework)
- Van Nostrand EL et al 2020 Nature 583:711 (A large-scale binding and functional map of human RNA-binding proteins)
- ENCODE eCLIP Standards (encodeproject.org/eclip) - canonical thresholds

## Related Skills

- clip-seq/clip-preprocessing - Upstream preprocessing producing dedup BAM
- clip-seq/clip-alignment - Upstream alignment with crosslink-preserving parameters
- clip-seq/clip-qc - FRiP, library complexity, IDR before/after peak calling
- clip-seq/crosslink-site-detection - PureCLIP / CTK CITS / PARalyzer for single-nt CL sites
- clip-seq/differential-clip - DEWSeq / Flipper for cross-condition differential binding
- clip-seq/binding-site-annotation - Annotate called peaks to 5' UTR / CDS / 3' UTR / intron
- clip-seq/clip-motif-analysis - Motif discovery on called peaks
- clip-seq/ago-clip-mirna-targets - Chimeric eCLIP peak calling
- clip-seq/m6a-clip - miCLIP2-specific peak calling
- chip-seq/peak-calling - DNA-protein peak calling for comparison
<!-- END FILE: clip-seq/clip-peak-calling/SKILL.md -->

## 子目录：clip-seq/clip-preprocessing

<!-- BEGIN FILE: clip-seq/clip-preprocessing/SKILL.md -->
---
name: bio-clip-seq-clip-preprocessing
description: Preprocess CLIP-seq reads (eCLIP, iCLIP, iCLIP2, iCLIP3, irCLIP, PAR-CLIP, FLASH) with protocol-specific UMI extraction, adapter trimming, length filtering, and post-alignment PCR-duplicate collapse. Use when raw CLIP FASTQ must be turned into deduplicated, crosslink-preserving BAM input for peak calling; choosing between two-pass and single-pass adapter trimming; deciding minimum read length; or mapping UMI patterns to specific eCLIP/iCLIP/iCLIP2/iCLIP3 library preps.
tool_type: cli
primary_tool: umi_tools
---

## Version Compatibility

Reference examples tested with: umi_tools 1.1.5+, cutadapt 4.6+, fastp 0.23.4+, samtools 1.19+, pysam 0.22+, picard 3.1+, preseq 3.2+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# CLIP-seq Preprocessing

**"Preprocess raw CLIP reads into UMI-deduplicated, alignable FASTQ"** -> Extract random barcodes, trim adapters without disturbing the 5' truncation site, length-filter to remove unmappable shorts, and (post-alignment) collapse PCR duplicates by UMI + position. The 5' end of the read carries the iCLIP/eCLIP truncation signature one base downstream of the protein-RNA crosslink; preserving this base is the single most important constraint of CLIP preprocessing.

- CLI (eCLIP, paired-end): `umi_tools extract --bc-pattern=NNNNNNNNNN --stdin R1.fq.gz --read2-in R2.fq.gz --stdout R1_umi.fq.gz --read2-out R2_umi.fq.gz`
- CLI (iCLIP/iCLIP2, single-end): `umi_tools extract --bc-pattern=NNNXXXXNN --extract-method=string --stdin R1.fq.gz --stdout R1_umi.fq.gz` (3+2 random Ns flanking a 4 nt library barcode; demultiplex by the X positions first if multiplexed)
- CLI (PAR-CLIP): `umi_tools extract --bc-pattern=NNNN ...` (most protocols use 4 nt random barcodes; verify the lab's exact prep)
- CLI (3' trim only, eCLIP convention): `cutadapt -a AGATCGGAAGAGCACACGTCT -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT --quality-base 33 --quality-cutoff 6 -m 18 -o R1.trim.fq.gz -p R2.trim.fq.gz R1_umi.fq.gz R2_umi.fq.gz`

The eCLIP convention is: trim quality and adapter from the 3' end ONLY. The 5' end of read 2 (in paired-end eCLIP) is the truncation site of the RT enzyme at the protein-RNA adduct, located one nucleotide downstream of the crosslink. Trimming the 5' end discards that exact base. `cutadapt -g`, `fastp --trim_front1`, and aggressive quality trimming of the 5' end are all banned for CLIP unless a documented protocol-specific reason exists.

## Read Structure by Protocol

| Protocol | UMI length and location | Truncation-site read | Adapter set | Notes |
|----------|-------------------------|----------------------|-------------|-------|
| eCLIP (Van Nostrand 2016 / ENCODE) | 10 nt at R1 5' end (random nucleotides preceding insert) | R2 5' end (after R1 UMI is stripped) = crosslink -1 | Illumina TruSeq R1 + R2 + inline X1A/X1B inverted adapter for two-pass | ENCODE pipeline normative |
| seCLIP (single-end eCLIP) | 10 nt at R1 5' end | R1 5' end | TruSeq R1 only | ENCODE accepts both eCLIP and seCLIP |
| iCLIP (Konig 2010) | 5 nt random (NNNXXXXNN: 3 N + 4 X library barcode + 2 N), single-end | R1 5' end after barcode strip | L3 adapter at 3' | Multiplexed - demultiplex by the 4 X bases |
| iCLIP2 (Buchbender 2020) | 5 or 9 nt random (NNNXXXXNN or longer), single-end | R1 5' end | L3 adapter at 3' | Increased complexity vs iCLIP; same UMI pattern |
| iCLIP3 (Despic et al, bioRxiv 2026.03.01.708747) | 10 nt random + dual sample index, single-end | R1 5' end | TruSeq | Silica-column RNA isolation; non-radioactive; streamlined low-input protocol. Preprint - verify final published version before pinning a pipeline. |
| irCLIP (Zarnegar 2016) | 5 nt random + barcode (similar to iCLIP) | R1 5' end | IR700 adapter + standard TruSeq sequencing adapter | Infrared replaces 32P; otherwise iCLIP-like |
| PAR-CLIP (Hafner 2010) | 0-4 nt depending on prep | T->C transitions within reads (NOT a truncation method) | TruSeq R1 | UMI optional; rely on T->C signature for CL |
| FLASH (Ilik 2020) | Sample barcode + UMI in custom adapter | R1 5' | Custom L3 design | 1.5 day protocol; adapter design proprietary to MPI |
| miCLIP / miCLIP2 (Linder 2015 / Kortel 2021) | iCLIP-style barcodes | R1 5' = m6A -1 (truncation OR C-to-T) | iCLIP L3 | m6A-specific |
| STAMP (Brannan 2021) | NA (no UV) | NA (C-to-U editing) | 10x or bulk RNA-seq adapters | Antibody-free editing-based; preprocess as RNA-seq |

If the read structure differs from the lab's documentation, run `seqkit head -n 1000 R1.fq.gz | seqkit stats -a` and inspect the first 12 bases of 100 random reads. Random-barcode positions show ~25% base composition per position; library/sample barcodes will be fixed across reads.

## Critical Choice: One Adapter Pass vs Two

**One pass (single-end iCLIP, PAR-CLIP):** Single 3' adapter; cutadapt with `-a <L3>` and `-m 18` is sufficient.

**Two passes (eCLIP, paired-end):** The eCLIP library design ligates an inverted X1A/X1B inline adapter that can appear at either end of a short fragment due to read-through. The ENCODE pipeline does pass 1 with the standard 3' adapter, then pass 2 trims a residual 5' adapter that read-through events leave on read 2. Trimming a 5' adapter from R2 is a special case: cutadapt's `-G <ADAPTER>` (uppercase) anchored at R2's 5' end is the right invocation. Do NOT use `-g` (lowercase) for R1 5' trimming - that destroys the truncation site.

**Cutadapt full eCLIP-style invocation:**

```bash
# Pass 1 - 3' adapter (both reads)
cutadapt \
    -a AGATCGGAAGAGCACACGTCT \
    -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT \
    --quality-base 33 -q 6 \
    -m 18 \
    -o R1.p1.fq.gz -p R2.p1.fq.gz \
    R1.umi.fq.gz R2.umi.fq.gz

# Pass 2 - read-through 5' adapter on R2 only (ENCODE eCLIP)
cutadapt \
    -G GATCGTCGGACTGTAGAACTCTGAAC \
    --quality-base 33 -q 6 \
    -m 18 \
    -o R1.p2.fq.gz -p R2.p2.fq.gz \
    R1.p1.fq.gz R2.p1.fq.gz
```

The `-q 6` is intentionally permissive. Aggressive `-q 20` quality trimming chews back the 5' end of R2 and breaks truncation-based crosslink-site detection. The `-m 18` minimum-length cutoff is non-negotiable: reads shorter than 18 nt are functionally unmappable (multi-map prevalence > 50%, see CIMS analysis discussions in the CLIP review literature) and must be discarded before alignment.

## Per-Protocol Failure Modes

### eCLIP -- 5' end trimmed by mistake

**Trigger:** Pipeline written for generic RNA-seq applied to eCLIP; `fastp` defaults trim both ends; `cutadapt -g` invoked on R2.

**Mechanism:** The 5' end of R2 in eCLIP is the truncation site = crosslink -1. Quality-trim from 5' or untargeted 5' adapter trim discards that exact base.

**Symptom:** Downstream PureCLIP / iCount / CTK CITS analysis fails to call crosslink sites; peak calling still works but the peaks lose nucleotide precision.

**Fix:** Use `-q 6` (3' only by default in cutadapt) and never `--trim_front2` in fastp. Validate by inspecting BAM read 2 5' positions: 60-90% of unique R2 5' positions should map within 100 nt windows around known RBP binding motifs, not be uniformly distributed.

### iCLIP / iCLIP2 -- Demultiplex confusion with UMI

**Trigger:** Multiplexed iCLIP library; user runs `umi_tools extract` with `NNNNNNNNN` (9 N) when the actual prep is `NNNXXXXNN` (5 random + 4 sample barcode).

**Mechanism:** umi_tools treats the entire 9-base prefix as UMI, losing the sample identity in the middle 4 bases. Reads from different samples are merged.

**Symptom:** Library complexity inflated artificially; per-sample read counts seem high but binding profiles look averaged across samples; sample-specific motifs absent.

**Fix:** Demultiplex BEFORE UMI extraction. Use `umi_tools extract --bc-pattern=NNNXXXXNN --extract-method=string --filter-cell-barcode` with a whitelist of the 4 X-base barcodes; or split the FASTQ with `je demultiplex` against the library barcode table first, then `umi_tools extract --bc-pattern=NNNNN` (the 5 surviving random Ns).

### PAR-CLIP -- T->C mistaken for sequencing error

**Trigger:** Standard variant-calling pipeline applied to PAR-CLIP without recognizing the T->C signature.

**Mechanism:** PAR-CLIP's diagnostic mutation is T->C (4SU adduct pairs with G during RT). Upon crosslinking the per-position T->C rate jumps from ~0.5% baseline to 20-50% (see PAR-CLIP literature; Hafner 2010, Spitzer 2014). Pipelines that filter "high-error" reads or apply STAR `--outFilterMismatchNoverLmax 0.04` (4% mismatch ceiling) discard the very reads carrying the signal.

**Symptom:** Loss of 40-70% of PAR-CLIP reads; downstream T->C site calling (PARalyzer, wavClusteR) finds almost nothing.

**Fix:** For PAR-CLIP only, raise the STAR mismatch ceiling to `--outFilterMismatchNoverLmax 0.07` (downstream in clip-alignment); also raise quality-trim tolerance in cutadapt to `-q 6` (already the CLIP default but worth re-confirming for PAR-CLIP). Track T->C rate per nucleotide position with `samtools mpileup` to confirm the signature is preserved post-alignment. **Critical exception summary:** iCLIP/eCLIP/iCLIP2 keep 0.04; PAR-CLIP only raises to 0.07. See clip-seq/clip-alignment for the alignment-stage override.

### Quality trimming too aggressive

**Trigger:** Inherited fastp/Trimmomatic pipeline with `-q 20` or `MINLEN 36`.

**Mechanism:** CLIP fragments are short (20-75 nt insert) and the 3' end carries adapter. Aggressive quality trimming and length filtering destroy 30-60% of usable reads.

**Symptom:** Per-replicate unique-mapped read count < 500k from a ~30M raw library; library complexity calculation crashes from too few reads.

**Fix:** Use `-q 6 -m 18` (cutadapt) or `--qualified_quality_phred 6 --length_required 18` (fastp). Compare retained fraction: a properly preprocessed CLIP library retains ~70-85% of raw reads through trimming.

### Library complexity below threshold

**Trigger:** PCR duplication rate >> 50%; deduplicated unique fragment count < 1M.

**Mechanism:** Low input cells (< 5M), over-amplification (> 25 PCR cycles), or failed IP all produce libraries dominated by a small number of PCR-amplified molecules.

**Symptom:** `preseq lc_extrap` predicts plateau well below 5M unique reads at infinite sequencing depth; `picard CollectLibraryComplexity` reports `ESTIMATED_LIBRARY_SIZE` < 1M; UMI families have median size > 8.

**Fix:** No analytic rescue. Re-prep the library with more input cells and fewer PCR cycles (target 14-18 cycles for eCLIP, 16-20 for iCLIP2). If the dataset must be salvaged, downsample to the unique-fragment fraction and acknowledge the loss of statistical power in differential analyses.

## UMI Deduplication Decision

After alignment, collapse PCR duplicates by `(UMI, position, strand)`. The choice between `unique` and `directional` methods is a precision/recall tradeoff:

| Method | Match rule | Behaviour | When to use |
|--------|-----------|-----------|-------------|
| `--method=unique` | Exact UMI match | Strictest; two UMIs differing by 1 base treated as independent molecules | ENCODE convention; reproducibility against published peaks |
| `--method=directional` | Network of UMIs differing by hamming-1; pick most-abundant | Collapses UMI sequencing errors; slightly fewer unique fragments reported | Highest precision; preferred when UMI sequencing error rate > 1% |
| `--method=cluster` | Connected components within edit distance | Most aggressive collapse | Default umi_tools behaviour pre-2017; not recommended for CLIP |
| `--method=adjacency` | Adjacency clustering | Between unique and directional | Rarely used for CLIP |

For eCLIP and iCLIP, the **ENCODE convention is `--method=unique`** (Van Nostrand 2016); the Yeo lab pipeline uses this exclusively. Directional adds 5-15 minutes runtime for human eCLIP at typical depth and is more conservative on rare UMI sequencing errors but produces slightly different absolute counts.

```bash
samtools index aligned.bam
umi_tools dedup \
    --stdin=aligned.bam \
    --stdout=dedup.bam \
    --method=unique \
    --paired \
    --log=dedup.log
samtools index dedup.bam
```

Without UMIs (e.g., older eCLIP with only sample barcodes, some custom protocols), fall back to `picard MarkDuplicates --REMOVE_DUPLICATES true`. The trade-off: position-only dedup over-collapses (genuinely independent fragments that share start positions are lost) at ~5-15% in deep CLIP libraries; UMI dedup recovers them.

## Pre-Mapping rRNA Filter (Optional but Standard)

eCLIP libraries are 5-30% rRNA reads even after polyA depletion. ENCODE's pipeline pre-maps to a rRNA + RepeatMasked repeat index with bowtie2, then aligns unmapped reads to the genome. This is purely a performance optimization (avoiding STAR's multi-mapper tangle on rRNA) and does not change which reads survive deduplication; it only reorders the alignment stages.

```bash
# Pre-map to rRNA + repeats
bowtie2 -x repbase_repeats -U R1.trim.fq.gz \
    --un-gz R1.norep.fq.gz \
    -p 8 -S /dev/null
# Then align unmapped reads to genome with STAR
```

For non-eCLIP protocols (iCLIP, PAR-CLIP) the rRNA pre-map is optional; the alternative is to filter rRNA-overlapping reads after STAR alignment with `bedtools intersect -v -a aligned.bam -b rRNA.bed`.

## Library Complexity Assessment

```bash
# preseq lc_extrap predicts unique fragments at deeper sequencing
preseq lc_extrap -B -P aligned.bam -o complexity.txt
# Output: TOTAL_READS, EXPECTED_DISTINCT, LOWER_0.95CI, UPPER_0.95CI
# At 100M reads, EXPECTED_DISTINCT >= 10M = good complexity; < 3M = library failed

# picard direct estimate
picard EstimateLibraryComplexity \
    I=aligned.bam \
    O=picard_complexity.txt
# ESTIMATED_LIBRARY_SIZE > 5M = healthy
```

ENCODE eCLIP requires >= 1M unique fragments per replicate (after UMI dedup). Anything below 500k is functionally unusable for genome-wide peak calling. Between 500k and 1M, restrict analysis to high-expression transcripts.

## QC Checkpoints After Preprocessing

| Metric | Target | If below target |
|--------|--------|-----------------|
| Adapter trim retention | >= 70% reads | Adapter pattern wrong; recheck library prep docs |
| Mean read length post-trim | >= 25 nt | RNA fragmentation too aggressive in IP step |
| % reads >= 18 nt | >= 80% | Drop the prep; libraries with > 30% < 18 nt indicate degraded RNA |
| UMI-extract success rate | >= 95% | UMI pattern wrong; reads do not start with random Ns |
| PCR duplication rate | 30-70% (CLIP normal) | < 30% means under-sequenced; > 90% means over-amplified |
| Library complexity (preseq) | >= 1M unique at sequenced depth | Library failed; cannot rescue analytically |

CLIP libraries have HIGH duplication rates (40-70%) by design - the IP enriches a small pool of molecules. This is NOT a problem if UMIs collapse duplicates correctly. A "30% duplication rate" CLIP library typically means either (a) the IP failed (no enrichment, so library looks like RNA-seq) or (b) the library was undersequenced and unique molecules dominate.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| umi_tools extract: "Read does not match pattern" for > 10% of reads | UMI pattern wrong (5 vs 9 vs 10 nt) | Inspect first 12 bases of 100 reads; rerun extract with correct `--bc-pattern` |
| cutadapt: 95% reads "Too short, filtered" | Adapter sequence wrong; reads are adapter-only after trim | Verify adapter sequence in library prep documentation; check both R1 and R2 adapters |
| All reads aligning to chrM after preprocessing | Pre-map to rRNA skipped; rRNA reads dominate | Add bowtie2 rRNA pre-map OR `samtools view -F 4 -L exclude_chrM_rRNA.bed` post-align |
| umi_tools dedup very slow (> 4h on 30M BAM) | Default `--method=directional` on dense libraries | Switch to `--method=unique` (ENCODE convention) |
| eCLIP truncation positions look uniform across genome | 5' adapter trim destroyed R2 5' end | Re-preprocess; `-g` should never touch R2 5' in eCLIP |
| 30% T->C mismatches in PAR-CLIP fail mapping | STAR mismatch ceiling 0.04 too strict | Raise to `--outFilterMismatchNoverLmax 0.07` for PAR-CLIP only |
| iCLIP2 reads after dedup << expected unique | Demultiplex done with whole UMI; samples merged | Demultiplex by 4 X bases of NNNXXXXNN first, then extract UMI |

## Reconciliation: Preprocessing Tools

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| fastp gives more reads than cutadapt | fastp default polyG trimming kept short reads; cutadapt min-length filtered them | Both correct; pick one and document |
| umi_tools and je-suite give different dedup counts | Different UMI distance metric (unique vs hamming-1 vs network) | Use ENCODE convention `umi_tools --method=unique` for cross-study comparability |
| Library complexity (preseq) vs (picard) disagree | preseq extrapolates non-linearly; picard estimates at sequenced depth only | Trust preseq at sequenced depth, picard for absolute library size |
| Read count after Yeo lab pipeline >> nf-core/clipseq | Yeo includes rRNA reads; nf-core pre-filters | Both correct; downstream peak callers handle this differently |

**Operational rule:** For ENCODE comparability, follow the Yeo lab eCLIP pipeline exactly: `umi_tools extract` (10 N R1) -> `cutadapt -q 6 -m 18` (two-pass) -> `bowtie2 pre-map rRNA` (unmapped to genome) -> `STAR --alignEndsType EndToEnd --outFilterMultimapNmax 1` -> `umi_tools dedup --method=unique`. For iCLIP/iCLIP2, follow the iCount preprocessing tutorial. Document any deviation in methods.

## References

- Van Nostrand EL et al 2016 Nat Methods 13:508 (eCLIP protocol, ENCODE standard)
- Konig J et al 2010 Nat Struct Mol Biol 17:909 (original iCLIP, truncation principle)
- Buchbender A et al 2020 Methods 178:33 (iCLIP2 protocol, library complexity gain)
- Lee FCY et al 2021 bioRxiv 2021.08.27.457890 (iiCLIP / improved iCLIP, motif specificity)
- Hafner M et al 2010 Cell 141:129 (PAR-CLIP, 4SU labeling, T->C signature)
- Zarnegar BJ et al 2016 Nat Methods 13:489 (irCLIP, non-radioactive)
- Ilik IA et al 2020 Nucleic Acids Res 48:e15 (FLASH, fast protocol)
- Smith T et al 2017 Genome Res 27:491 (UMI-tools, network-based dedup)
- Daley T & Smith AD 2013 Nat Methods 10:325 (preseq library complexity)
- West C et al 2023 Wellcome Open Res 8:286 (nf-core/clipseq pipeline)

## Related Skills

- clip-seq/clip-alignment - Downstream STAR/bowtie2 alignment with ENCODE parameters
- clip-seq/clip-qc - Library complexity, FRiP, IDR, read-distribution QC after preprocessing
- clip-seq/crosslink-site-detection - Why preserving the 5' R2 base is critical
- clip-seq/clip-peak-calling - Downstream peak callers consume the dedup BAM
- clip-seq/stamp-antibody-free - STAMP/DART-seq use RNA-seq preprocessing instead of UMI-based CLIP preprocessing
- read-qc/umi-processing - General UMI handling concepts
- read-qc/adapter-trimming - General adapter trimming
- alignment-files/duplicate-handling - Picard MarkDuplicates fallback when UMIs unavailable
<!-- END FILE: clip-seq/clip-preprocessing/SKILL.md -->

## 子目录：clip-seq/clip-qc

<!-- BEGIN FILE: clip-seq/clip-qc/SKILL.md -->
---
name: bio-clip-seq-clip-qc
description: Comprehensive quality control for CLIP-seq libraries (eCLIP, iCLIP, iCLIP2, PAR-CLIP) covering library complexity (preseq), FRiP, IDR replicate reproducibility, read-distribution metagene, SMInput vs IgG control rationale, rRNA / snoRNA contamination, fragment-length distribution, and ENCODE-compliance thresholds. Use when assessing whether a CLIP library passed, deciding lenient vs stringent peak thresholds, comparing replicates with IDR rescue and self-consistency ratios, or distinguishing failed IP from over-amplified library.
tool_type: mixed
primary_tool: preseq
---

## Version Compatibility

Reference examples tested with: preseq 3.2+, picard 3.1+, samtools 1.19+, bedtools 2.31+, deeptools 3.5+, idr 2.0.4+, MultiQC 1.21+, RSeQC 5.0+, pysam 0.22+, fastp 0.23+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed binary and adapt the example to match the actual CLI rather than retrying.

# CLIP-seq Quality Control

**"Did my CLIP library pass?"** -> Assess preprocessing retention, alignment rate, library complexity, replicate reproducibility (IDR), fraction reads in peaks (FRiP), read-distribution metagene, rRNA/snoRNA contamination, fragment-length distribution, and SMInput vs IP enrichment. ENCODE eCLIP compliance is the canonical bar: >= 1M unique fragments per replicate, IDR rescue and self-consistency ratios both < 2, FRiP >= 0.005 (narrow-binding), library complexity rising linearly with depth on preseq lc_extrap. A library can fail at any of these stages, and the failure mode determines whether the data is salvageable.

- CLI (library complexity, primary QC): `preseq lc_extrap -B -P aligned.bam -o complexity.txt`
- CLI (FRiP after peak calling): `bedtools intersect -c -s -a peaks.bed -b dedup.bam | awk '{s+=$NF} END{print s}'` then divide by total reads
- CLI (IDR, ENCODE convention): `idr --samples rep1.sorted.bed rep2.sorted.bed --input-file-type bed --rank 5 --output-file idr.out --idr-threshold 0.05 --plot`
- CLI (read distribution / metagene): `RSeQC read_distribution.py -i dedup.bam -r gencode.v38.bed` + `geneBody_coverage.py -i dedup.bam -r housekeeping.bed -o gb`
- CLI (rRNA contamination check): `samtools idxstats dedup.bam | awk '$1 ~ /rRNA|45S|18S|28S/ { sum+=$3 } END {print sum}'`
- CLI (consolidated report): `multiqc <run_dir>` aggregates FastQC + cutadapt + STAR + umi_tools + preseq + samtools stats

The ENCODE eCLIP standards (encodeproject.org/eclip) define: >= 2 biological replicates with >= 1M unique fragments each (or saturated peak detection); IDR rescue and self-consistency ratios both < 2; narrow-binding RBPs FRiP >= 0.005. CLIP libraries should have 40-70% PCR duplication BY DESIGN - the IP enriches a small molecule pool, so high pre-dedup duplication is normal; low duplication suggests failed IP.

## QC Stage Hierarchy

CLIP QC progresses through five gates; failure at an earlier gate makes later gates meaningless.

| Gate | Metric | Tool | ENCODE threshold | Failure interpretation |
|------|--------|------|------------------|------------------------|
| 1. Preprocessing retention | % reads retained after UMI + adapter trim | cutadapt log | >= 70% | Adapter pattern wrong; degraded RNA |
| 2. Alignment rate | % reads aligned to genome (unique) | STAR Log.final.out | >= 60% for eCLIP, 70% for iCLIP/PAR-CLIP | Wrong genome; rRNA pre-map missing |
| 3. Library complexity | Predicted unique fragments at sequenced depth | preseq lc_extrap | >= 1M unique | Over-amplified or under-input library |
| 4. IP enrichment | log2(IP/SMInput) at expected sites; FRiP | bedtools + idr | FRiP >= 0.005; log2 >= 3 at top peaks | Failed antibody / antibody not IP-grade |
| 5. Reproducibility | IDR rescue + self-consistency ratios | idr | both < 2 | Biological variation too high; or low complexity |

A library failing at Gate 3 (complexity) cannot be rescued analytically; gates 4-5 fail downstream of complexity by construction.

## Library Complexity with preseq

**Goal:** Determine whether the CLIP library captured enough independent molecules to support genome-wide peak calling (ENCODE: >= 1M unique fragments per replicate).

**Approach:** Run `preseq lc_extrap` on the PRE-dedup BAM (preseq counts PCR duplicates to extrapolate); also compute picard ESTIMATED_LIBRARY_SIZE at sequenced depth. Flag any library predicted to plateau below 3M unique fragments at infinite depth.

```bash
# After alignment, BEFORE UMI dedup (preseq counts PCR duplicates)
preseq lc_extrap \
    -B -P \
    -o sample_complexity.txt \
    sample_aligned.bam

# Output columns:
# TOTAL_READS  EXPECTED_DISTINCT  LOWER_0.95CI  UPPER_0.95CI
# At 100M reads, EXPECTED_DISTINCT:
#   >= 10M  = excellent complexity
#   3-10M   = acceptable; restrict to high-expression transcripts
#   < 3M    = library failed; cannot rescue analytically

# picard direct estimate at current depth
picard EstimateLibraryComplexity \
    I=sample_aligned.bam \
    O=picard_complexity.txt
# ESTIMATED_LIBRARY_SIZE > 5M = healthy CLIP library
```

A linear plateau on preseq's curve at low depth indicates over-amplification; a curve still climbing at sequenced depth means more sequencing would yield more unique fragments.

## FRiP (Fraction Reads in Peaks)

FRiP measures how much of the IP signal falls into the called peak set. ENCODE eCLIP narrow-binding RBP minimum: FRiP >= 0.005. Atypical-binding RBPs (rare-transcript binders like TROVE2 on Y RNAs) are exempt.

```bash
# Reads in peaks (use stringent peaks: log2 FC >= 3, -log10 p >= 3)
reads_in_peaks=$(bedtools intersect -c -s -a peaks.stringent.bed -b dedup.bam | awk '{s+=$NF} END {print s}')
total_reads=$(samtools view -c -F 4 dedup.bam)
frip=$(echo "scale=4; $reads_in_peaks / $total_reads" | bc)
echo "FRiP: $frip"

# Per-region FRiP breakdown
for region in three_utr exon intron; do
    rip=$(bedtools intersect -c -s -a peaks_${region}.bed -b dedup.bam | awk '{s+=$NF} END {print s}')
    echo "${region}: $(echo "scale=4; $rip / $total_reads" | bc)"
done
```

| RBP class | Expected FRiP (ENCODE eCLIP) |
|-----------|------------------------------|
| Splicing factors (PTBP1, U2AF2) | 0.01 - 0.10 |
| 3' UTR mRNA stability (HuR, PUM2) | 0.02 - 0.20 |
| Translation factors (EIF3J) | 0.01 - 0.05 |
| Repeat binders (MATR3) | 0.05 - 0.30 (high; concentrated in repeats) |
| Mitochondrial (FASTKD2) | 0.05 - 0.40 (very high; chrM is small) |
| snoRNA binders (DKC1) | 0.10 - 0.50 (high; snoRNA is rare) |
| Failed IP (any RBP) | < 0.005 |

## IDR for CLIP Reproducibility

IDR (Li et al 2011) measures peak-rank reproducibility across replicates. ENCODE eCLIP convention applies IDR identically to ChIP-seq, using CLIPper + SMInput log2 FC + -log10 p as the ranking signal. The CLIP-specific consideration: rank by signalValue (log2 FC) or p-value, NOT by score column (CLIPper score is sparse and tied).

```bash
# Sort each replicate's peaks by signal
sort -k5,5gr rep1.compressed.bed > rep1.sorted
sort -k5,5gr rep2.compressed.bed > rep2.sorted

# True-replicates IDR (threshold 0.05)
idr --samples rep1.sorted rep2.sorted \
    --input-file-type bed --rank 5 \
    --output-file idr_true.out \
    --idr-threshold 0.05 \
    --plot --log-output-file idr.log

# Pseudo-replicates from each individual replicate (split BAM in half)
samtools view -b -h -s 1.5 rep1.dedup.bam > rep1.psr1.bam   # seed 1, fraction 0.5
samtools view -b -h -s 2.5 rep1.dedup.bam > rep1.psr2.bam   # seed 2 (different)
# Re-run peak calling on each pseudoreplicate, then IDR at threshold 0.10
```

**ENCODE consistency rules for eCLIP:**
- Nt = peaks passing IDR on true replicates
- Nself = peaks passing IDR on pseudo-replicates of each rep
- Library passes if: max(Nt, Nself) / min(Nt, Nself) <= 2
- If both ratios > 2: library rejected

## SMInput vs IgG Control: Which?

The eCLIP design uses a size-matched input (SMInput) from the SAME lysate, treated identically (UV, IP buffer, RNase, ligation, IP, but with NO antibody addition - just bead-only control or a non-specific control IP). This is fundamentally different from IgG controls and from RNA-seq.

| Control | What it measures | Pros | Cons |
|---------|------------------|------|------|
| SMInput | Background from non-specific binding + ligation/RT/gel biases at same size | Captures all CLIP-specific biases; ENCODE standard | Requires same-day prep; cannot use a previous IgG library |
| IgG-IP | Non-specific antibody binding to the same RBP-naive lysate | Direct nonspecificity measure | Yields very low (~3-10x less reads); high PCR dup; hard to normalize |
| Empty beads (mock) | Bead surface non-specificity only | Cleanest baseline | Misses real CLIP background (IP buffer + ligation step bias) |
| RNA-seq (matched cell type) | Transcript abundance | Easy to obtain | Misses CLIP-specific biases entirely; not a real CLIP control |
| Total RNA / nuclear RNA | Cellular RNA distribution | Easy | Same as RNA-seq above |

**Consensus (ENCODE / Hentze / Yeo):** SMInput. The bead-only IgG/mock alternatives are ill-suited for quantification because their library yields are 5-10x lower, dominated by PCR duplicates, and produce sparse read-density tracks. RNA-seq cannot replace SMInput because it does not capture the non-specific binding that occurs during IP.

```bash
# SMInput preparation - same as IP except no antibody added during incubation
# Same UV dose, same lysate aliquot, same RNase, same library prep
# Critical: same SDS-PAGE size cut from membrane as the IP

# Check SMInput vs IP enrichment. A ratio of whole-library totals only measures relative sequencing
# depth; normalize the in-peak fraction in each library instead:
#   log2( (IP_in_peaks/IP_total) / (SMI_in_peaks/SMI_total) )
# > 0.5 indicates the IP concentrates reads into peaks beyond SMInput (good)
# ~ 0 indicates failed IP (SMInput == IP)
```

## Read Distribution Metagene

```bash
# RSeQC read_distribution.py shows fractional read placement
read_distribution.py -i dedup.bam -r gencode.v38.bed > read_dist.txt

# Output reports:
#   CDS_Exons, 5'UTR_Exons, 3'UTR_Exons, Introns, TES_down_10kb, TES_down_1kb,
#   TSS_up_10kb, TSS_up_1kb, Intergenic_region
# CLIP-seq biology-specific patterns:
#   Splicing factor: > 60% Introns + 5' UTR exons (containing 5' splice sites)
#   3' UTR factor: > 50% 3'UTR_Exons
#   m6A reader: 3'UTR_Exons + Stop_codon region
#   Failed IP: matches RNA-seq distribution (no enrichment)

# GeneBody coverage for 5' vs 3' bias
geneBody_coverage.py \
    -i dedup.bam \
    -r housekeeping.bed \
    -o sample_gb
# Flat curve = no positional bias (normal for most RBPs)
# 3' end bias = polyA-dependent enrichment (suspect)
# 5' end bias = nascent / TSS-proximal (only sensible for some RBPs)
```

## Fragment-Length Distribution (Paired-End)

```bash
# Paired-end fragment-length distribution
samtools view -f 2 dedup.bam | awk '$9 > 0 && $9 < 500 {print $9}' | sort -n | uniq -c > fragment_lengths.txt

# CLIP normal range: 20-75 nt insert (rises from short trimmed reads to ~75 nt)
# Wider range (20-200) seen in high-RNase / long-fragment protocols
# Narrow peak at one length (e.g., all reads at 30 nt) = over-trimmed
# Bimodal at 30 nt and 150 nt = library preparation artifact
```

## Pre-Map rRNA / snoRNA Contamination Check

```bash
# rRNA reads as fraction of total
total=$(samtools view -c -F 4 dedup.bam)
rRNA=$(samtools idxstats dedup.bam | awk '$1 ~ /rRNA|45S|18S|28S|5_8S/ { sum+=$3 } END {print sum}')
rrna_frac=$(echo "scale=4; $rRNA / $total" | bc)
echo "rRNA fraction: $rrna_frac"

# eCLIP without pre-map: rRNA 5-30% normal
# After pre-map: < 2% expected
# > 30% indicates rRNA dominance - IP captured ribosomes preferentially
# Some RBPs (RPL/RPS) expected to bind ribosomes; verify against RBP biology
```

## Antibody Validation Sanity Check

The antibody is the single most common point of failure in CLIP. Even commercial "IP-grade" antibodies fail at 30-50% rates in practice. Cross-check IP enrichment against expected biology:

```python
import pandas as pd

# Load peak file
peaks = pd.read_csv('peaks.stringent.bed', sep='\t', header=None,
                    names=['chr','start','end','name','log2fc','strand'])

# Filter top 100 peaks
top_peaks = peaks.nlargest(100, 'log2fc')

# Check enrichment in expected biology
# 1. If RBP is splicing factor: top peaks should be intronic or splice-site flanking
# 2. If RBP is HuR: > 70% top peaks should be 3' UTR
# 3. If RBP is FASTKD2: top peaks should be chrM
# 4. If RBP is FUS: GUGGU motif should appear in top motif enrichment

# Quick check
chrom_dist = top_peaks['chr'].value_counts(normalize=True)
print(chrom_dist.head(10))
# Healthy RBP: chromosomes represented in proportion to expression
# Failed IP: top chromosome chrM (mt artifact) or chr21/22 (housekeeping bias) > 20%
```

GO term sanity: top-peak genes should enrich for the expected biology (e.g., HuR -> immune / inflammation / mRNA stability terms; PTBP1 -> RNA splicing terms). If the top GO term is "cellular metabolism" or "translation" for a splicing factor, the IP failed.

## Per-Stage Failure Modes

### Gate 1: Preprocessing retention < 70%

**Trigger:** cutadapt log shows > 30% reads filtered (too short or no adapter).

**Mechanism:** Adapter pattern wrong; or RNA was degraded before fragmentation (all reads adapter-only).

**Symptom:** Catastrophic loss at the adapter trim step.

**Fix:** Verify adapter sequence in library prep documentation; check library quality control (Bioanalyzer / TapeStation) for RIN value; re-prep if RIN < 7.

### Gate 2: Alignment rate < 60%

**Trigger:** STAR Log.final.out reports `Uniquely mapped reads %` < 60% for eCLIP, < 70% for iCLIP.

**Mechanism:** rRNA contamination dominating (no pre-map); wrong species genome; or chimeric library (contamination).

**Symptom:** Low alignment rate; samtools idxstats shows most reads as rRNA-aligned.

**Fix:** Run bowtie2 pre-map to rRNA + repeats index; verify genome species; check for sample swap with `samtools view -h sample.bam | grep '^@SQ'`.

### Gate 3: Library complexity < 1M unique

**Trigger:** preseq lc_extrap predicts plateau < 1M unique at sequenced depth; or picard reports ESTIMATED_LIBRARY_SIZE < 1M.

**Mechanism:** Over-amplification (> 25 PCR cycles); low input (< 5M cells); failed IP capturing only a few molecules.

**Symptom:** preseq curve flattens early; UMI clusters have median size > 8.

**Fix:** No analytic rescue. Re-prep with more input cells (10-20M for eCLIP), fewer PCR cycles (14-18 for eCLIP, 16-20 for iCLIP2). If forced to use this library, restrict downstream analysis to high-expression transcripts and acknowledge the limitation.

### Gate 4: FRiP < 0.005 for narrow-binding RBP

**Trigger:** FRiP value below ENCODE threshold for the RBP class.

**Mechanism:** IP failed to enrich specific binding sites; antibody cross-reactive or not IP-grade.

**Symptom:** Top peaks dominated by abundant transcripts (GAPDH, ACTB); GO enrichment generic; motif analysis returns AU-rich background.

**Fix:** Re-test antibody on a knockdown lysate (siRNA against the RBP) - if WB signal does not decrease, antibody is non-specific; switch antibody. ENCODE-validated antibodies are at encodeproject.org/biosamples.

### Gate 4 variant: IP/SMInput global log2 ~ 0

**Trigger:** Whole-genome log2(IP/SMInput) is near 0 instead of positive.

**Mechanism:** IP and SMInput are equivalent - the antibody is not enriching any RBP-bound RNA.

**Symptom:** Per-peak log2 FC scaled around 0; no obvious enrichment at known motif sites.

**Fix:** Same as above - antibody failure. Consider tagged-RBP system (Halo-CLIP, GoldCLIP, or knock-in endogenous tag).

### Gate 5: IDR fails - rescue/self-consistency > 2

**Trigger:** ENCODE IDR test reports rescue ratio > 2 OR self-consistency > 2.

**Mechanism:** Replicates inconsistent. Biological variation high; OR one replicate has lower library complexity; OR one replicate failed IP.

**Symptom:** Per-replicate peak counts differ > 2x; IDR plot shows the two replicates have very different peak rank distributions.

**Fix:** Run preseq and FRiP on each replicate independently; identify the failing one; re-sequence to higher depth or re-prep. ENCODE-style: down-sample both replicates to common depth, re-test IDR.

### High PCR duplication confused with low complexity

**Trigger:** Saw 60% PCR duplication and panicked.

**Mechanism:** CLIP libraries have 40-70% PCR duplication BY DESIGN - the IP enriches a small pool. UMI dedup recovers the unique molecules underneath.

**Symptom:** "60% duplication" headline. Actual unique count is what matters.

**Fix:** Confirm UMI dedup has been applied and unique fragment count >= 1M. The duplication rate metric is meaningless without UMI context for CLIP.

## Decision Tree by Failure

| Symptom | Likely failure | Action |
|---------|----------------|--------|
| > 50% reads "too short" in cutadapt | Adapter wrong or RNA degraded | Verify adapter; check RIN |
| Most reads align to rRNA | No pre-map; or IP captured ribosomes | bowtie2 pre-map; or accept if RBP is ribosomal |
| Unique frag count < 1M | Over-amplified or under-input | No rescue; re-prep |
| FRiP < 0.005 (narrow RBP) | Failed IP | Switch antibody |
| IP/SMInput global log2 ~ 0 | Antibody non-specific | Switch antibody or use tagged-RBP |
| IDR rescue > 2 | Replicate inconsistency | Identify failing replicate; re-sequence |
| Top GO terms generic | Failed IP or contamination | Check antibody on KD lysate WB |
| chrM peaks abundant for non-mt-RBP | Mitochondrial contamination | Filter chrM or accept if mt-RBP |
| Fragment length all 30 nt | Over-trimmed | Loosen quality trim from -q 20 to -q 6 |
| Strand-specific peaks lost | bedtools without -s | Add `-s` strand flag |

## Standard QC Report (MultiQC)

```bash
# Aggregate all QC tools into a single report
multiqc \
    fastqc_output/ \
    cutadapt_logs/ \
    star_logs/ \
    umi_tools_logs/ \
    preseq_output/ \
    samtools_stats/ \
    -o multiqc_report/
```

MultiQC reads logs from FastQC, cutadapt, STAR, umi_tools, preseq, samtools stats, picard, and others, and produces a single HTML report. For CLIP-seq, additionally run RSeQC `read_distribution.py` and document FRiP / IDR results manually.

## ENCODE-Style Comprehensive QC Table

| Metric | Threshold | Source |
|--------|-----------|--------|
| Biological replicates | >= 2 | ENCODE eCLIP |
| Read length | >= 50 nt (PE) | ENCODE |
| Unique fragments per replicate | >= 1M (or saturated) | ENCODE |
| Preprocessing retention | >= 70% | Practitioner consensus |
| Genome alignment rate (unique) | >= 60% eCLIP, 70% iCLIP | Practitioner consensus |
| Library complexity (preseq) | >= 10M expected unique at 100M | ENCODE |
| FRiP (narrow-binding RBP) | >= 0.005 | ENCODE |
| FRiP (atypical-binding RBP) | Exempt | ENCODE |
| log2(IP/SMInput) at stringent peaks | >= 3 | ENCODE |
| -log10 p at stringent peaks | >= 3 | ENCODE |
| IDR rescue ratio | < 2 | ENCODE |
| IDR self-consistency ratio | < 2 | ENCODE |
| rRNA fraction post pre-map | < 2% | Practitioner consensus |
| Read distribution match to RBP class | Y | Sanity check |
| Top motif consistent with literature | Y | Sanity check |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| preseq "all reads have duplicates" | Pre-deduplicated BAM passed to preseq | Re-run on PRE-dedup BAM |
| FRiP value > 1.0 | Peak set overlaps reads counted twice | Use unique-reads BAM; verify peak BED is non-redundant |
| IDR plot empty | Ranking column wrong; all peaks tied at same value | Rank by `--rank 5` (log2 FC); sort BED first |
| MultiQC missing modules | Logs not in expected directory structure | Verify log paths; rerun multiqc with explicit `-d` |
| Read distribution: > 50% intergenic for mRNA RBP | TxDb missing transcripts; rRNA contamination | Update GENCODE; pre-map rRNA |
| GeneBody coverage 3' biased | polyA-selected library; not CLIP | Verify library prep was random hexamer |
| Fragment-length distribution narrow at 30 nt | Adapter aggressively trimmed at 5' | Loosen trim parameters |
| Antibody KD WB shows no decrease | Antibody non-specific | Switch antibody; use ENCODE-validated |

## References

- Van Nostrand EL et al 2016 Nat Methods 13:508 (eCLIP, ENCODE QC standards)
- Li Q et al 2011 Ann Appl Stat 5:1752 (IDR framework)
- Landt SG et al 2012 Genome Res 22:1813 (ChIP/CLIP QC guidelines, IDR Nself rule)
- Daley T & Smith AD 2013 Nat Methods 10:325 (preseq library complexity)
- Wang L et al 2012 Bioinformatics 28:2184 (RSeQC)
- Ewels P et al 2016 Bioinformatics 32:3047 (MultiQC)
- Smith T et al 2017 Genome Res 27:491 (UMI-tools)
- ENCODE eCLIP Data Standards (encodeproject.org/eclip) - canonical thresholds
- Van Nostrand EL et al 2020 Nature 583:711 (ENCODE 150 RBP QC patterns)

## Related Skills

- clip-seq/clip-preprocessing - Gate 1 preprocessing logs
- clip-seq/clip-alignment - Gate 2 alignment metrics
- clip-seq/clip-peak-calling - Gates 4-5 peak QC + FRiP
- clip-seq/differential-clip - QC for differential analyses
- read-qc/quality-reports - General FastQC / MultiQC
- read-qc/contamination-screening - Cross-species contamination
- chip-seq/chipseq-qc - DNA-protein QC analogue
<!-- END FILE: clip-seq/clip-qc/SKILL.md -->

## 子目录：clip-seq/crosslink-site-detection

<!-- BEGIN FILE: clip-seq/crosslink-site-detection/SKILL.md -->
---
name: bio-clip-seq-crosslink-site-detection
description: Detect single-nucleotide crosslink (CL) sites in CLIP-seq data using truncation patterns (iCLIP/eCLIP CITS), crosslink-induced mutations (HITS-CLIP CIMS deletions, PAR-CLIP T-to-C), or HMM/kernel-density methods (PureCLIP, PARalyzer, CTK). Use when single-nucleotide resolution is required for motif registration (mCross), allele-specific binding (BEAPR), variant-effect prediction, or comparing crosslink chemistry across CLIP variants.
tool_type: cli
primary_tool: PureCLIP
---

## Version Compatibility

Reference examples tested with: PureCLIP 1.3.1+, CTK 1.1.4+, PARalyzer 1.5+, wavClusteR 2.34+, pyCRAC 1.5+, samtools 1.19+, bedtools 2.31+, pysam 0.22+, R 4.3+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws unexpected errors, introspect the installed tool and adapt the example to match the actual CLI rather than retrying.

# CLIP-seq Crosslink-Site Detection

**"Detect single-nucleotide crosslink sites in my CLIP data"** -> Identify the exact base where the protein-RNA UV adduct caused the reverse transcriptase to stop (truncation, in iCLIP/eCLIP), to read through with a mutation (deletion in HITS-CLIP, T->C in PAR-CLIP), or to leave a multi-base signature (PARalyzer kernel density for PAR-CLIP). Single-nucleotide resolution is the foundation of motif registration (mCross), allele-specific binding (BEAPR/ASPRIN), variant-effect prediction, and the most rigorous comparisons across CLIP variants. The detection chemistry differs by CLIP type: iCLIP/eCLIP read 5' end is one nucleotide downstream of the crosslink (CITS); PAR-CLIP reads contain T->C transitions at the crosslink (CIMS substitution); HITS-CLIP reads contain deletions at the crosslink (CIMS deletion).

- CLI (HMM, all CLIP variants): `pureclip -i dedup.bam -bai dedup.bam.bai -g genome.fa -ibam sminput.bam -ibai sminput.bam.bai -o crosslinks.bed -or regions.bed -nt 8 -dm 8`
- CLI (CTK CITS truncations, iCLIP/eCLIP): `parseAlignment.pl --map-qual 1 --min-len 18 --mutation-file mut.txt dedup.bam dedup.bed` then `tag2cluster.pl ... -cs5 5 -m 1` for truncation-cluster
- CLI (CTK CIMS deletions, HITS-CLIP): `getMutationType.pl dedup.bed mut.txt -type del` then `CIMS.pl dedup.bed mut.txt -big -c -p 0.01 cims.bed`
- CLI (CTK CIMS T->C, PAR-CLIP): `getMutationType.pl dedup.bed mut.txt -type sub -nuc t -mut c` then `CIMS.pl dedup.bed t2c.mut -p 0.001 t2c_cims.bed`
- CLI (PAR-CLIP kernel density): `PARalyzer params.ini` (parameters file defines read length, min reads per cluster, mutation rate threshold)
- CLI (PAR-CLIP wavClusteR R): `wavClusteR::filterClusters(cl, snps=NULL, filterFC=FALSE)` after wavelet clustering

Single-nt CL sites are the input to mCross motif registration (see clip-seq/clip-motif-analysis), to BEAPR/ASPRIN allele-specific binding analyses, and to RBPNet/DeepRiPe deep-learning models (see clip-seq/clip-deep-learning). They are NOT a replacement for broad peak calls; the two outputs are complementary. A common downstream error is passing a CLIPper peak BED to mCross instead of a PureCLIP single-nt BED - mCross requires the single-nt resolution to register motif position relative to the crosslink offset.

## Crosslink Chemistry by CLIP Variant

The detection method must match the underlying chemistry of how the reverse transcriptase encountered the protein-RNA adduct:

| CLIP variant | RT behavior at CL | Detection signature | Sensitivity (CL captured per read) | Sequence bias |
|--------------|-------------------|---------------------|-------------------------------------|---------------|
| iCLIP / iCLIP2 / iCLIP3 / eCLIP / irCLIP / FLASH | Truncates at adduct | 5' end of cDNA = CL site - 1 | ~80% of reads truncate; the minority read through | Strong U bias at CL sites |
| HITS-CLIP | Reads through with deletion (~8-20% of tags) | Single-base deletion in read | ~8-20% of tags contain a deletion at the CL site | U bias plus sequence-specific deletion rate |
| PAR-CLIP (4SU) | Reads through with T->C (20-50% of T positions in crosslinked reads) | T->C transition (or G->A on reverse strand) | Per-T rate 20-50%; per-read 1-5 conversions | Restricted to T positions; depends on 4SU incorporation rate |
| PAR-CLIP (6SG) | Reads through with G->A | G->A transition | Lower rate than 4SU T->C | Restricted to G positions |
| miCLIP / miCLIP2 (m6A) | Primarily truncation at the m6A site (RT stops at antibody-trapped m6A); secondary C->T transition observed in a subset of reads at m6A | 5' end (CL -1); C->T rate is a feature used by m6Aboost ML in addition to truncation, not a stand-alone primary signal | Mixed; m6Aboost ML integrates truncation + sequence context to score | DRACH motif context required |
| STAMP | C->T editing on target (not crosslink) | C->T editing in mRNA reads | NA (editing-based; not crosslink-based) | N/A |
| TRIBE | A->I editing on target | A->G in cDNA (I read as G) | NA | Adjacent to ADAR consensus |

## Algorithmic Taxonomy

| Tool | CLIP variant | Detection signal | Statistical model | Output resolution | Strength | Fails when |
|------|--------------|------------------|-------------------|-------------------|----------|------------|
| PureCLIP (Krakau 2017) | iCLIP/eCLIP/PAR-CLIP | Truncation + enrichment + CL motif | Non-homogeneous HMM | Single-nucleotide | The most comprehensive HMM model | Lowest F1 among callers benchmarked in Boyle 2023 on broad-binding RBPs (highly focal) |
| CTK CITS (Shah 2017) | iCLIP/eCLIP | Truncation only | Empirical FDR vs background | Single-nucleotide | Simple, well-validated for iCLIP | Less granular than PureCLIP; no HMM smoothing |
| CTK CIMS deletion (Shah 2017) | HITS-CLIP | Single-base deletions | Empirical FDR | Single-nucleotide | Standard for HITS-CLIP | Requires deletion-tolerant aligner (BWA -e) |
| CTK CIMS T->C (Shah 2017) | PAR-CLIP | T->C substitutions | Empirical FDR | Single-nucleotide | Alternative to PARalyzer | Less popular than PARalyzer |
| PARalyzer (Corcoran 2011) | PAR-CLIP | T->C transitions, kernel density | Kernel density estimation | Cluster (10-50 nt) | Field standard for PAR-CLIP | Cluster-level, not single-nt; needs careful parameter tuning |
| wavClusteR (Comoglio 2015) | PAR-CLIP | T->C with wavelet smoothing | Wavelet transform + clustering | Cluster | Robust to sequencing depth variability | Less single-nt; legacy R package |
| pyCRAC / kPLogo | CRAC (yeast) | Read truncation + deletion | Empirical | Single-nucleotide | Original CLIP analytics tool | Yeast-focused; perl/python legacy |
| Piranha bins | Any | Coverage in bins | ZTNB | Bin-level (50-200 nt) | Not crosslink-specific | Bin width too coarse for single-nt |
| HOMER tag2pos | Any | 5' end position | None | Read-end positions only | Quick truncation site dump | No statistical filtering |
| omniCLIP | Any | Coverage + variant pattern | Dirichlet-multinomial HMM | Region | Not focal | Too broad for single-nt |
| iCount (paths) | iCLIP | Crosslink site cluster | Empirical | Cluster | Used in nf-core/clipseq | Less single-nt than PureCLIP |

Methodology evolves; PureCLIP 2.0 and CTK 1.2 have minor flag changes; PARalyzer parameters need careful tuning per-RBP. Cross-validate single-nt sites with at least two tools when high-confidence reporting is required.

## Critical Choice: Truncation vs Mutation vs HMM

Three orthogonal approaches:

**Truncation-based (CITS, PureCLIP)** -- Find positions enriched in cDNA 5' ends. The RT enzyme stops at the adduct; the 5' end of the read maps to CL site - 1. Used for iCLIP/eCLIP. Pro: high yield (~80% of reads truncate). Con: U bias of crosslinking inflates U positions.

**Mutation-based (CIMS for deletions/substitutions; PARalyzer for T->C)** -- Find positions with crosslink-induced mutations. RT reads through the adduct with high mutation rate at the CL position. Used for HITS-CLIP (deletions, ~8-20%) and PAR-CLIP (T->C, 20-50%). Pro: less U bias; PAR-CLIP signal is restricted to T positions. Con: lower yield (only mutated reads count).

**HMM-based (PureCLIP, omniCLIP)** -- Joint model of enrichment + CL signature + sequence context. State the most-likely posterior probability of CL state per nucleotide. Used across CLIP variants. Pro: integrates multiple signals; explicit input normalization. Con: F1 ~0.2 on bulk RBPs (very focal); single-nt resolution at the cost of breadth.

| Goal | Method | Tool |
|------|--------|------|
| Single-nt CL map for motif registration (mCross) | HMM | PureCLIP |
| Truncation-based ENCODE-compatible iCLIP | Truncation | CTK CITS |
| PAR-CLIP T->C signal | Mutation | PARalyzer (cluster) or CTK CIMS sub T->C (single-nt) |
| HITS-CLIP deletion signal | Mutation | CTK CIMS deletion |
| Cross-CLIP-variant comparable single-nt | HMM | PureCLIP (all variants) |
| Allele-specific CLIP (BEAPR) | Truncation + ASB | PureCLIP CL sites + WASP-filtered BAM |
| Variant effect (computational from CL) | HMM | PureCLIP + downstream DeepRiPe (see clip-deep-learning) |
| Yeast / CRAC | Truncation + deletion | pyCRAC |

## Per-Tool Failure Modes

### PureCLIP -- HMM convergence on sparse coverage

**Trigger:** RBP with low IP enrichment; SMInput depth uneven; PureCLIP run on full genome without -iv interval.

**Mechanism:** PureCLIP HMM convergence is sensitive to coverage depth. On regions with < 5 reads/100 bp the HMM defaults to background state; if half the genome is sparse, the state distributions become bimodal and the entire run takes > 24 h or runs out of memory.

**Symptom:** PureCLIP "Convergence not reached" warning; or output has 0 CL sites; or runtime > 24 h on standard server.

**Fix:** Restrict analysis to expressed transcripts: `-iv expressed_tx.bed`. Or filter the BAM to high-coverage regions first. Test on chr22 first to verify parameters before genome-wide run.

### PureCLIP -- Misses broad binding zones

**Trigger:** RBP with broad binding (PUM2 3' UTRs, SR proteins exonic enhancers); using PureCLIP exclusively.

**Mechanism:** PureCLIP HMM emits the CL state at very high stringency. The Boyle 2023 Skipper benchmark reports PureCLIP as the most focal caller with low recall on broad-binding RBPs.

**Symptom:** PureCLIP CL site count is 100x lower than CLIPper / Skipper peak count.

**Fix:** Use PureCLIP for single-nt CL maps AND CLIPper/Skipper for broad-zone peak calls. They are complementary, not substitutes. PureCLIP `-or` regions output is broader than `-o` sites but still focal.

### CITS truncation -- Misapplied to PAR-CLIP

**Trigger:** CTK CITS run on PAR-CLIP data.

**Mechanism:** PAR-CLIP RT reads through the adduct (T->C mutation), not truncates. The 5' end of PAR-CLIP reads is at the fragment 5' end, not the CL site.

**Symptom:** CITS returns few sites; the sites that ARE returned do not align with the T->C mutation positions.

**Fix:** For PAR-CLIP use PARalyzer or CTK CIMS substitution mode (`-type sub -nuc t -mut c`). CITS is iCLIP/eCLIP only.

### CIMS deletion -- Misapplied to iCLIP

**Trigger:** CTK CIMS run with `-type del` on iCLIP data.

**Mechanism:** iCLIP RT truncates, doesn't delete. The deletion rate is < 1% in iCLIP (background level), so CIMS finds nothing significant.

**Symptom:** CIMS output BED has < 100 sites genome-wide.

**Fix:** Use CTK CITS for iCLIP (truncation-based) or PureCLIP. CIMS deletion is HITS-CLIP / older PAR-CLIP only.

### PARalyzer -- Parameter sensitivity

**Trigger:** PARalyzer default parameters on a new RBP; cluster count unexpected.

**Mechanism:** PARalyzer's kernel-density approach has 5+ parameters: minimum read depth, minimum mutation read count, mutation rate threshold, bandwidth, kernel type. Different combinations produce 5-100x different cluster counts.

**Symptom:** PARalyzer cluster count 5-100x off from literature reports for the same RBP.

**Fix:** Use the PARalyzer default parameters (Corcoran 2011), tuned for that RBP class. Validate on a known-binding region with a reference dataset before publication.

### Aligner deletion-tolerance for HITS-CLIP

**Trigger:** HITS-CLIP aligned with STAR or bowtie2 in standard mode; CIMS finds few deletion sites.

**Mechanism:** Standard STAR/bowtie2 are aggressive about handling deletions; CIMS expects the deletions to be visible as CIGAR D operations in BAM. STAR/bowtie2 may soft-clip or fail to align deletion-bearing reads.

**Symptom:** Few CIGAR D operations in BAM (`samtools view dedup.bam | awk '$6 ~ /D/' | wc -l`); CIMS deletion site count low.

**Fix:** Re-align HITS-CLIP with BWA-aln (Zhang lab / CTK convention) or STAR `--scoreDelOpen -1 --scoreDelBase -1 --scoreInsOpen -1 --scoreInsBase -1` to permit deletions. Or use Novoalign which is more deletion-tolerant.

### PAR-CLIP T->C mismatch ceiling

**Trigger:** PAR-CLIP aligned with STAR `--outFilterMismatchNoverReadLmax 0.04`; T->C reads discarded.

**Mechanism:** PAR-CLIP per-T conversion rate 20-50% means a 30 nt read with 8 Ts may have 4 T->C events = 13% mismatch rate, exceeding the 4% ceiling.

**Symptom:** 40-70% read loss at alignment for PAR-CLIP; downstream T->C site detection finds nothing.

**Fix:** Raise to 0.07 for PAR-CLIP only (see clip-seq/clip-alignment).

### Strand mis-assignment for truncation site

**Trigger:** Single-end CLIP; using read 5' end as CL site without strand consideration.

**Mechanism:** For plus-strand RNA, the cDNA 5' end is downstream of the CL position. For minus-strand RNA, it is upstream. Without strand-aware coordinate conversion, half of CL sites are mis-positioned by ~1 nt.

**Symptom:** mCross / motif analysis shows the motif positioned 1 nt off from expected.

**Fix:** Verify the BED output handles strand correctly. CTK CITS, PureCLIP, and most modern tools do this automatically; custom scripts must add `if strand == '-': cl_position = read_end_5p + 1`.

## Decision Tree by Use Case

| Scenario | Tool | Parameters |
|----------|------|-----------|
| Single-nt CL map for mCross motif registration | PureCLIP | `-i dedup.bam -ibam sminput.bam -dm 8` |
| iCLIP/eCLIP CITS truncation sites | CTK CITS | `tag2cluster.pl -cs5 5 -m 1` |
| HITS-CLIP deletion CIMS | CTK CIMS | `CIMS.pl -big -c -p 0.01` |
| PAR-CLIP T->C clusters | PARalyzer | Per-RBP params tuned from Corcoran 2011 defaults |
| PAR-CLIP T->C single-nt | CTK CIMS substitution | `CIMS.pl -type sub -nuc t -mut c -p 0.001` |
| Yeast CRAC | pyCRAC | `pyCRAC.py` with HTP-tagged protein |
| Variant effect at CL sites | PureCLIP + DeepRiPe | See clip-seq/clip-deep-learning |
| Allele-specific binding | WASP-filtered BAM + PureCLIP | See clip-seq/clip-alignment for WASP |
| Cross-CLIP comparison | PureCLIP (consistent across variants) | Same parameters |
| m6A miCLIP2 sites | miCLIP2-specific (m6Aboost) | See clip-seq/m6a-clip |
| STAMP edit sites | Not crosslink-based | See clip-seq/stamp-antibody-free |

## Reconciliation: When Detection Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| PureCLIP << CTK CITS site count | PureCLIP HMM very focal; CITS empirical broader | Both correct; report which threshold |
| PARalyzer clusters << CIMS T->C sites for PAR-CLIP | PARalyzer is cluster-level; CIMS is single-nt | Aggregate CIMS to clusters for comparison |
| PureCLIP CL sites at unexpected positions | Strand mis-assignment OR aligner soft-clip | Check BED strand column; verify `--alignEndsType EndToEnd` |
| HITS-CLIP CIMS empty | Aligner not deletion-tolerant | Re-align with BWA-aln or STAR with adjusted scoring |
| PAR-CLIP CIMS << expected | Reads lost at mismatch ceiling | Raise STAR `--outFilterMismatchNoverReadLmax` to 0.07 |
| eCLIP CITS positions shifted by 1 nt | Strand handling off-by-one | Verify R2 5' end position handling |
| Multiple CITS sites within 5 nt | RT stops near each other; same CL event | Cluster within 10 nt window post-detection |
| Motif registers 5 nt off in mCross | CL positions wrong by RT-stop offset | Confirm tool reports "CL - 1" position consistently |

**Operational rule:** For motif registration and ASB, run PureCLIP with SMInput. For ENCODE-comparable truncation-based output, also run CTK CITS. Cross-validate by checking that mCross motif PWM is the same when fed PureCLIP sites vs CTK CITS sites. If they diverge by > 2 nt in motif position, suspect strand or off-by-one issue.

## Workflow: PureCLIP -> mCross -> ASB

```bash
# Step 1: PureCLIP single-nt sites
pureclip \
    -i sample.dedup.bam -bai sample.dedup.bam.bai \
    -g genome.fa \
    -ibam sminput.dedup.bam -ibai sminput.dedup.bam.bai \
    -o sample.crosslinks.bed \
    -or sample.regions.bed \
    -nt 8 -dm 8 -iv expressed_tx.bed

# Step 2: mCross motif registration
mCross -i sample.crosslinks.bed -g genome.fa -k 7 -n 5 -o mcross_out

# Step 3: Intersect with heterozygous SNPs for allele-specific binding
bedtools intersect -wa -wb -s -a sample.crosslinks.bed -b het_snps.vcf > cl_at_hets.bed

# Step 4: Test allele bias with BEAPR or ASPRIN
# (see allele-specific CLIP literature; not in this skill)
```

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| PureCLIP "Convergence not reached" | HMM didn't converge on sparse coverage | Restrict to expressed transcripts with `-iv expressed.bed` |
| PureCLIP > 24h runtime | Full genome on large library | Test on chr22 first; add `-iv` filter |
| CTK CIMS empty for HITS-CLIP | Aligner not deletion-tolerant | Re-align with BWA-aln |
| CITS truncation sites not single-nt | CIGAR S operations from soft-clip | Verify `--alignEndsType EndToEnd` upstream |
| PAR-CLIP CIMS empty | Reads lost at mismatch ceiling | Raise STAR mismatch tolerance |
| Off-by-one motif position | Strand handling differs | Verify tool documents whether output is CL or CL-1 |
| Single-nt motif lost in HOMER on PureCLIP sites | Site BED too narrow; need flanking | Extend `bedtools slop -b 15` before motif analysis |
| mCross "no crosslinks found" | Passed peak BED instead of CL BED | Use single-nt site output |
| PureCLIP output looks like uniform distribution | R2 5' end trimmed in preprocessing | Re-preprocess; -g and --trim_front2 banned for CLIP |
| Strand-specific motif inverted | BED column 6 wrong | Verify strand encoding; PureCLIP preserves correctly |

## References

- Konig J et al 2010 Nat Struct Mol Biol 17:909 (iCLIP truncation principle)
- Hafner M et al 2010 Cell 141:129 (PAR-CLIP T->C signature)
- Granneman S et al 2009 PNAS 106:9613 (CRAC, single-nt CL detection)
- Corcoran DL et al 2011 Genome Biol 12:R79 (PARalyzer)
- Comoglio F et al 2015 BMC Bioinformatics 16:32 (wavClusteR)
- Shah A et al 2017 Bioinformatics 33:566 (CTK / CIMS / CITS)
- Krakau S et al 2017 Genome Biol 18:240 (PureCLIP HMM)
- Boyle EA et al 2023 Cell Genomics 3:100317 (Skipper; PureCLIP focality/F1 benchmark)
- Sugimoto Y et al 2012 Genome Biol 13:R67 (CLIP/iCLIP analysis; uridine crosslink preference)
- Feng H et al 2019 Mol Cell 74:1189 (mCross requires CL sites)
- Yang EW et al 2019 Nat Commun 10:1338 (BEAPR allele-specific protein-RNA binding)
- Van Nostrand EL et al 2020 Nature 583:711 (ENCODE eCLIP single-nt analyses)

## Related Skills

- clip-seq/clip-preprocessing - 5' base preservation critical for truncation detection
- clip-seq/clip-alignment - End-to-end alignment for crosslink-preserving BAM
- clip-seq/clip-peak-calling - Peak vs CL site is a complementary distinction
- clip-seq/clip-motif-analysis - mCross consumes CL sites
- clip-seq/clip-deep-learning - RBPNet trained on CL count distributions
- clip-seq/m6a-clip - miCLIP2 has its own CL detection
- clip-seq/stamp-antibody-free - STAMP uses C->U editing, not crosslink
- alignment-files/sam-bam-basics - CIGAR string semantics for D operations
<!-- END FILE: clip-seq/crosslink-site-detection/SKILL.md -->

## 子目录：clip-seq/differential-clip

<!-- BEGIN FILE: clip-seq/differential-clip/SKILL.md -->
---
name: bio-clip-seq-differential-clip
description: Identify differentially bound regions across CLIP-seq conditions (knockdown vs control, treatment vs vehicle, disease vs healthy) using DEWSeq (sliding-window DESeq2), Flipper (Skipper-downstream), ASpeak, edgeR, or limma-voom. Use when computing condition-level changes in RBP binding intensity, choosing peak-level vs window-level vs crosslink-level testing, designing replicate experiments, or distinguishing biological binding shifts from technical confounders.
tool_type: r
primary_tool: DEWSeq
---

## Version Compatibility

Reference examples tested with: DEWSeq 1.18+, htseq-clip 2.0+, DESeq2 1.44+, edgeR 4.2+, limma 3.60+, Flipper (commit 2024.04+), Skipper (commit 2023.05+), pybedtools 0.10+, pyranges 0.0.129+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Differential CLIP-seq Analysis

**"Identify regions with changed RBP binding across conditions"** -> Test for condition-level differences in IP enrichment relative to SMInput, accounting for replicate variance and (where available) sequencing depth normalization. Three statistical scales are possible: peak-level (test each peak as a unit), window-level (test fixed transcriptome windows; DEWSeq, Flipper), or crosslink-site level (test single-nt positions). The choice depends on the biology (narrow regulatory shift vs broad binding-mode change) and on which upstream peak caller was used (CLIPper -> peak-level; Skipper -> window-level; PureCLIP -> CL-level).

- R (window-level, DEWSeq + htseq-clip): `library(DEWSeq); dds <- DESeqDataSetFromSlidingWindows(counts, colData, design=~condition); dds <- DESeq(dds); res <- results(dds)`
- R (Skipper downstream, Flipper): `flipper differential -i skipper_out/ --design design.tsv --contrast treatment vs control -o flipper_out/`
- R (peak-level, edgeR): `dge <- DGEList(counts=peak_counts, group=condition); dge <- calcNormFactors(dge); design <- model.matrix(~condition); dge <- estimateDisp(dge, design); fit <- glmQLFit(dge, design); res <- glmQLFTest(fit)`
- R (peak-level, limma-voom): `v <- voom(dge, design); fit <- lmFit(v, design); fit <- eBayes(fit); res <- topTable(fit, coef=2, number=Inf)`
- CLI (htseq-clip preprocessing): `htseq-clip extract -i annotation.gff -o annotation_windows.bed -w 50 -s 20 && htseq-clip count -i sample.bam -w annotation_windows.bed -o sample.counts.txt`

DEWSeq is the EMBL/Hentze-group windowed-NB approach for CLIP binding-site discovery, commonly adapted for differential testing via the interaction design. Flipper is the Skipper-companion tool (Flanagan 2026) for the modern Skipper workflow. Peak-level edgeR/limma-voom work when the upstream peak caller produced a comparable peak BED across conditions (e.g., consensus peaks from CLIPper).

## Algorithmic Taxonomy

| Tool | Scale | Statistical model | Replicate requirement | Strength | Fails when |
|------|-------|-------------------|----------------------|----------|------------|
| DEWSeq (Schwarzl 2024) | 50-100 nt sliding window | Negative binomial GLM (DESeq2 internals) | >= 2 reps per condition | Designed specifically for CLIP; integrates SMInput | Slow on dense libraries; output window-resolution |
| Flipper (Flanagan 2026) | Skipper window (100 nt) | Negative binomial; designed for Skipper output | >= 2 reps per condition | Modern; pairs with Skipper peak caller | Only useful if upstream is Skipper |
| ASpeak | Peak | Negative binomial | >= 2 reps | Peak-level for CLIPper output | Less popular; legacy |
| edgeR (general) | Peak or window | Quasi-likelihood F-test on NB | >= 2 reps | Mature, widely cited | Generic; not CLIP-aware; needs careful normalization |
| limma-voom | Peak or window | Linear model with mean-variance trend | >= 2 reps | Fast; well-validated; handles small samples | Generic; treats counts as continuous after voom |
| DESeq2 (direct) | Peak or window | Negative binomial GLM | >= 2 reps | Mature; same engine as DEWSeq | Same as edgeR caveats |
| Single-cell CLIP (specialized) | Cell-resolved (scCLIP) | Cell-mixture / pseudobulk | Cells | Single-cell CLIP differential | Nascent; few published tools |
| diffbind (CLIP adaptation) | Peak | DESeq2 or edgeR backend | >= 2 reps | Familiar from ChIP/ATAC | Designed for ChIP; needs CLIP-specific normalization |
| MAnorm2 | Peak | Hierarchical empirical Bayes | >= 2 reps | Tested on ChIP; less on CLIP | Less CLIP-specific |

Methodology evolves; verify DEWSeq vignette and Flipper paper for current best practice. The DEWSeq + htseq-clip pipeline (Schwarzl 2024) is the most-published CLIP-specific differential framework; Flipper (Flanagan 2026) is the modern Skipper-coupled alternative.

## Critical Decision: The Interaction-Term Design

**Use `~ type + condition + type:condition` and test the interaction-term coefficient.** This is the single most consequential statistical choice in differential CLIP.

- `type` = `ip` vs `sminput` (whether the library is IP or size-matched input)
- `condition` = `treated` vs `untreated` (or KD vs control)
- `type:condition` interaction = "Does the IP-vs-input ratio shift across conditions?"

A naive `~ condition` design tests whether read counts differ regardless of whether they come from IP or SMInput - this confounds binding changes with expression changes. The interaction term explicitly tests for **differential binding** (the biologically meaningful signal) rather than differential expression at peak loci.

When testing, extract the interaction-term coefficient: `results(dds, name = 'typeip.conditiontreat')`. The log2FoldChange returned is the change in IP/input ratio in `treated` vs `untreated` - this is what "differential binding" means.

## Critical Choice: Peak-Level vs Window-Level vs Crosslink-Level

Three scales differ in resolution and statistical power:

**Peak-level (edgeR, limma-voom, DESeq2 on CLIPper peaks):** Test each consensus peak's IP/SMInput log2 FC across conditions. Pro: peak boundaries are biologically meaningful; output interpretable. Con: peak set changes across conditions (a new peak in treatment but missing in control complicates testing); SMInput normalization must be applied consistently.

**Window-level (DEWSeq, Flipper):** Tile transcriptome into fixed 50-100 nt windows; test each window. Pro: comparable across conditions (windows are pre-defined); handles binding-mode shifts within a peak; high statistical power. Con: window-resolution; multiple-testing burden (millions of windows); biological meaning of a window needs translation.

**Crosslink-level (custom):** Test each single-nt CL position. Pro: nucleotide resolution; captures motif-level shifts. Con: very low coverage per position; massive multiple-testing burden; rarely used in published differential CLIP.

| Goal | Scale | Tool |
|------|-------|------|
| ENCODE-style peak-level differential (CLIPper upstream) | Peak | DESeq2 / edgeR / limma-voom on CLIPper consensus peaks |
| Maximum sensitivity windowed differential | Window | DEWSeq (with htseq-clip) or Flipper (with Skipper) |
| Modern Skipper-coupled workflow | Window | Flipper |
| Single-cell scCLIP differential | Cell | Specialized single-cell CLIP methods (few published tools) |
| Compare binding-mode shifts within a peak | Window | DEWSeq |
| Allele-specific differential | CL site | BEAPR + custom logistic |
| RBP-KD effect on binding profile | Peak/window | DEWSeq (handles KD-effect on RBP itself) |

## DEWSeq Workflow (Window-Level Differential)

DEWSeq is the EMBL/Hentze-group windowed-NB framework for CLIP binding-site discovery, adapted here for differential testing via the interaction design. The pipeline is:

**Goal:** Identify transcriptome windows where the IP-vs-SMInput ratio shifts across conditions, accounting for replicate variance with the negative-binomial GLM.

**Approach:** Use htseq-clip to extract sliding 50 nt windows across annotated features, count reads per window per sample, build a DESeqDataSetFromSlidingWindows object with the `~ type + condition + type:condition` interaction design, extract the `typeip.conditiontreat` interaction coefficient as the differential-binding effect size, and aggregate adjacent significant windows with `bedtools merge -d 100`.

```bash
# Step 1: htseq-clip generates sliding-window count matrices
htseq-clip extract \
    -i gencode.v38.annotation.gff \
    -o annotation_windows.bed \
    --window-size 50 \
    --window-step 20 \
    --feature-type CDS,UTR

# Step 2: count IP and SMInput reads per window per sample
for sample in ip_rep1 ip_rep2 sminput_rep1 sminput_rep2; do
    htseq-clip count \
        -i ${sample}.dedup.bam \
        -a annotation_windows.bed \
        -o ${sample}.counts.txt \
        --mate 2
done
# (For eCLIP, --mate 2 because R2 5' is the truncation site; for iCLIP single-end use --mate 1)

# Step 3: DEWSeq differential testing
htseq-clip mergeCounts \
    -i ip_rep1.counts.txt ip_rep2.counts.txt sminput_rep1.counts.txt sminput_rep2.counts.txt \
    -o merged_counts.tsv
```

```r
library(DEWSeq)

counts <- read.table('merged_counts.tsv', sep='\t', header=TRUE, row.names=1)
colData <- data.frame(
    sample = c('ip_rep1','ip_rep2','sminput_rep1','sminput_rep2'),
    type = c('ip','ip','sminput','sminput'),
    condition = c('treated','treated','untreated','untreated')
)

dds <- DESeqDataSetFromSlidingWindows(
    countData = counts,
    colData = colData,
    annotObj = 'annotation_windows.bed',
    design = ~ type + condition
)

dds <- DESeq(dds)
# In a model with `~ type + condition`, the IP-vs-input contrast is the simple condition
# main effect; to test the differential CLIP signal between conditions use the interaction
# term name from the design matrix (matches the skill's interaction-term guidance below):
res <- results(dds, name='typeip.conditiontreated')

# Window-level FDR adjustment
res_filtered <- res[!is.na(res$padj) & res$padj < 0.05 & abs(res$log2FoldChange) > 1, ]

# Aggregate adjacent significant windows into differential regions
sig_windows <- as.data.frame(res_filtered)
sig_windows$chr <- gsub('_.*', '', rownames(sig_windows))
# Custom reduce: combine adjacent windows within 100 nt
```

## Flipper Workflow (Skipper-Coupled)

Flipper (Flanagan 2026) is the differential companion to Skipper, operating on the same 100 nt feature-respecting windows with a negative-binomial (DESeq2-based) differential test.

```bash
# Assume Skipper has been run on all samples; Skipper output is at skipper_out/
flipper differential \
    -i skipper_out/ \
    --design design.tsv \
    --contrast treatment vs control \
    -o flipper_out/

# design.tsv format:
# sample_id   condition   replicate   ip_or_input
# ip_treat_r1 treatment   1           ip
# ip_treat_r2 treatment   2           ip
# in_treat_r1 treatment   1           input
# ...
```

Output: differential window BED with log2 FC, p, padj per window.

## Peak-Level Differential (CLIPper Upstream)

```r
library(DESeq2)
library(GenomicRanges)
library(Rsubread)

# Step 1: union of CLIPper peaks across conditions
# (See bedtools merge upstream)
peaks <- read.table('consensus_peaks.bed', sep='\t', col.names=c('chr','start','end','name','score','strand'))

# Step 2: count reads per peak per sample with featureCounts
saf <- data.frame(
    GeneID = peaks$name,
    Chr = peaks$chr,
    Start = peaks$start + 1,  # 1-based for featureCounts
    End = peaks$end,
    Strand = peaks$strand
)
counts_ip <- featureCounts(
    files = c('ip_treat_r1.bam','ip_treat_r2.bam','ip_ctrl_r1.bam','ip_ctrl_r2.bam'),
    annot.ext = saf,
    isGTFAnnotationFile = FALSE,
    strandSpecific = 1,
    isPairedEnd = TRUE
)$counts

counts_in <- featureCounts(
    files = c('in_treat_r1.bam','in_treat_r2.bam','in_ctrl_r1.bam','in_ctrl_r2.bam'),
    annot.ext = saf,
    isGTFAnnotationFile = FALSE,
    strandSpecific = 1,
    isPairedEnd = TRUE
)$counts

# Step 3: DESeq2 with IP vs SMInput interaction
all_counts <- cbind(counts_ip, counts_in)
colData <- data.frame(
    type = rep(c('ip','input'), each=4),
    condition = rep(c('treat','treat','ctrl','ctrl'), 2),
    replicate = rep(c('r1','r2','r1','r2'), 2)
)

dds <- DESeqDataSetFromMatrix(countData = all_counts, colData = colData,
                               design = ~ type + condition + type:condition)
dds <- DESeq(dds)

# The interaction term `typeip.conditiontreat` tests:
# does the IP/input ratio differ in treatment vs control?
res <- results(dds, name = 'typeip.conditiontreat')

# Filter
res_sig <- res[!is.na(res$padj) & res$padj < 0.05 & abs(res$log2FoldChange) > 1, ]
```

The interaction-term design (`type:condition`) is the correct statistical model for differential CLIP: it tests whether the IP-vs-input ratio differs across conditions, which is what "differential binding" means. Naive testing of just `condition` (ignoring SMInput) confounds binding changes with expression changes.

## RBP Knockdown Experiment Design

The canonical differential CLIP design is to knock down the RBP and observe what binding sites are lost. Caveats:

| Issue | Implication | Mitigation |
|-------|-------------|------------|
| RBP KD also depletes the RBP protein in cells | siRNA/shRNA reduces RBP -> reduces IP yield -> reduces unique fragments | Normalize against SMInput WITHIN each condition; the relative IP/SMInput captures binding, not protein level |
| RBP KD changes transcript abundance | mRNA stability regulators (HuR, PUM2) when knocked down change target abundance | Both IP and SMInput see the change; ratio still works |
| Off-target effects of siRNA | Multiple binding profiles change | Use multiple independent siRNAs; require concordance |
| KD efficiency varies | Lower KD -> smaller binding-loss signal | Validate KD by WB on the same IP lysate; > 70% protein loss target |
| Rescue requires re-introducing RBP | siRNA-resistant RBP cDNA for rescue | The standard differential validation experiment |

## Per-Tool Failure Modes

### DEWSeq -- Slow on dense libraries

**Trigger:** Whole-genome window tiling at 20 nt step; dense library (50M unique fragments); 4+ samples.

**Mechanism:** DEWSeq runs DESeq2 internals on millions of windows; the dispersion fit on this many features is slow.

**Symptom:** Runtime > 6 h; out-of-memory; "size of object exceeds vector limit".

**Fix:** Increase window step size to 50 nt; pre-filter windows with low counts; or restrict to expressed transcripts only. DEWSeq vignette suggests `keep <- rowSums(counts(dds)) >= 30; dds <- dds[keep,]` before testing.

### DEWSeq -- Custom adjacency aggregation needed

**Trigger:** Windows are 50 nt; biological binding sites are 50-500 nt; user expects DEWSeq to output continuous "differential regions" but gets individual windows.

**Mechanism:** DEWSeq outputs per-window results; aggregating adjacent significant windows into regions is a separate step.

**Symptom:** Output has 10,000 individual windows; user expects 1,000 biological regions.

**Fix:** Use the DEWSeq utility `resultsDEWSeq()` then `bedtools merge -d 100` on the significant-window BED. Or use the `top_hits_to_bed.R` script from DEWSeq examples.

### Peak-level differential -- Peak set differs between conditions

**Trigger:** CLIPper called peaks separately per condition; treatment has peaks at sites missing in control (and vice versa).

**Mechanism:** Peak unification requires a consensus peakset; testing on a "treatment-only" peak underestimates evidence in control (zero reads) and produces spurious DE.

**Symptom:** "Treatment-specific" peaks dominate DE results; biologically implausible.

**Fix:** Generate consensus peakset across all conditions (bedtools merge of all per-condition peak BEDs); count reads per consensus peak across all samples; THEN run differential. The Yeo lab convention is consensus peakset across all samples.

### Interaction term forgotten

**Trigger:** DESeq2 design `~ condition` instead of `~ type + condition + type:condition`.

**Mechanism:** Simple `~ condition` tests whether read counts differ between treatment and control regardless of whether reads are from IP or SMInput. A condition-driven expression change in SMInput is detected as DE binding.

**Symptom:** DE results dominated by transcripts with global expression changes (housekeeping shifts).

**Fix:** Always use the interaction-term design. The biologically meaningful test is the interaction `type:condition` p-value.

### Normalization assumptions

**Trigger:** edgeR `calcNormFactors(method='TMM')` on CLIP-seq data.

**Mechanism:** TMM assumes most features (genes) are not differentially expressed. CLIP-seq peak counts can be globally shifted if the RBP itself is knocked down; TMM normalization would force the shift to be invisible.

**Symptom:** Knockdown experiment shows ~0 DE peaks; expected hundreds.

**Fix:** Use SMInput as the control library; spike-in normalization if available; or skip TMM and use library-size normalization only. Some CLIP-specific tools (DEWSeq, Flipper) handle this internally.

### Flipper requires Skipper upstream

**Trigger:** Flipper called on CLIPper output.

**Mechanism:** Flipper expects Skipper's window-level output format with beta-binomial estimates.

**Symptom:** Flipper crashes or produces nonsense.

**Fix:** Use DEWSeq with htseq-clip for CLIPper-upstream workflows; use Flipper only with Skipper.

## Decision Tree by Scenario

| Scenario | Tool + design | Why |
|----------|---------------|-----|
| KD vs control eCLIP, CLIPper upstream | DEWSeq + htseq-clip | CLIP-specific NB GLM with interaction term |
| KD vs control eCLIP, Skipper upstream | Flipper | Skipper companion; matches windowing |
| Treatment vs vehicle (small effect) | DEWSeq (window-level higher power) | Sliding windows capture small shifts |
| Multiple time points | DEWSeq with time as covariate | Continuous design with time vector |
| Allele-specific differential | BEAPR per-allele + custom logistic | See clip-seq/clip-alignment for WASP |
| Single-cell CLIP differential | Specialized single-cell CLIP methods | Nascent; few published tools |
| Differential motif occupancy | Window-level + DEWSeq + motif overlap | Combine differential windows with motif BED |
| RBP overexpression vs control | Same as KD reversed | Same statistical framework |
| Compare two RBPs | NOT differential CLIP; use SPIDR or separate CLIPs | Different RBPs need separate IPs |
| Spike-in normalization needed | DEWSeq + spike-in size factors | For global occupancy shifts |
| chimeric eCLIP differential miRNA targets | Custom; treat each miRNA-target chimera as feature | Specialized; see clip-seq/ago-clip-mirna-targets |

## Reconciliation: When Differential Tools Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| DEWSeq finds many DE windows; edgeR peak-level finds few | Window-level higher power for narrow shifts | Aggregate DEWSeq windows; cross-check |
| edgeR many DE; DEWSeq few | edgeR not accounting for SMInput | Re-run edgeR with interaction term |
| DE peaks dominated by expression changes | No interaction term | Use `~ type + condition + type:condition` |
| KD experiment shows ~0 DE | TMM over-corrects global shift | Switch to library-size norm only; use SMInput |
| siRNA replicates discordant | Off-target effects vary | Use multiple independent siRNAs; require concordance |
| Treatment-only peaks dominate DE | No consensus peakset | Generate consensus first; then test on unified set |
| Significant windows scattered | Window aggregation step skipped | `bedtools merge -d 100` on significant-window BED |
| Same gene appears in many DE windows | Multiple binding sites per gene differential | Report at gene-level too; not just window-level |
| Flipper fails with non-Skipper input | Upstream mismatch | Use DEWSeq for non-Skipper workflows |
| DESeq2 dispersion fit fails | Too few replicates (n=2 per condition); too few features after filtering | Increase replicates; or relax filtering |

**Operational rule for high-confidence differential reporting:** (a) Use SMInput-aware design (`~ type + condition + type:condition`); (b) generate consensus peakset across conditions; (c) require padj < 0.05 AND |log2FC| > 1; (d) require concordance with at least one orthogonal method (e.g., DEWSeq + edgeR peak-level on same data); (e) for KD experiments, validate KD efficiency by WB and require multiple independent siRNAs.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| DESeq2 `~ condition` finds many DE | No interaction with type | Use `~ type + condition + type:condition` and test interaction |
| DEWSeq output is gene-level not window-level | `keep <- ...` filter too aggressive | Loosen pre-filter |
| Adjacent significant windows not aggregated | Forgot bedtools merge | `bedtools merge -d 100` on sig windows |
| edgeR TMM fits all libraries to one value | Most-features-not-DE assumption violated | Use library-size norm; or DEWSeq for CLIP-specific |
| Flipper crashes on CLIPper input | Tool mismatch | Switch to DEWSeq |
| Few replicates -> unstable estimates | n=2 not enough for dispersion | Increase n; or use limma-voom (more tolerant) |
| Peaks differ across conditions | Per-condition peak calls | Unify with consensus peakset |
| KD experiment yields 0 DE | Normalization over-corrected; OR KD efficiency too low | Validate KD WB; check normalization |
| Global shift in IP relative to SMInput | RBP itself knocked down so IP yield lower | Normalize WITHIN each condition |
| Lots of "treatment-only" peaks | Caller stringency higher in one condition | Use consensus peakset for fairness |

## References

- Schwarzl T et al 2024 Nucleic Acids Res 52:e1 (DEWSeq, windowed NB binding-site discovery; DESeq2-based, adaptable to differential designs)
- Sahadevan S et al 2022 Methods Mol Biol 2404:189 (DEWSeq + htseq-clip pipeline)
- Flanagan K, Xu S, Yeo GW 2026 bioRxiv 2026.03.13.711628 (Flipper, Skipper-companion differential; preprint)
- Boyle EA et al 2023 Cell Genomics 3:100317 (Skipper, parent of Flipper)
- Love MI et al 2014 Genome Biol 15:550 (DESeq2)
- McCarthy DJ et al 2012 Nucleic Acids Res 40:4288 (edgeR)
- Ritchie ME et al 2015 Nucleic Acids Res 43:e47 (limma)
- Yang EW et al 2019 Nat Commun 10:1338 (BEAPR allele-specific protein-RNA binding)
- Van Nostrand EL et al 2020 Nature 583:711 (ENCODE 150 RBP shRNA + eCLIP comparison)

## Related Skills

- clip-seq/clip-peak-calling - CLIPper / Skipper outputs feed differential
- clip-seq/clip-qc - Replicate QC required for valid differential
- clip-seq/binding-site-annotation - Annotate differential regions
- clip-seq/clip-motif-analysis - Motif analysis on differential windows
- clip-seq/ago-clip-mirna-targets - Differential miRNA targeting from chimeric eCLIP
- differential-expression/deseq2-basics - Underlying NB GLM model
- differential-expression/de-results - DE results interpretation
- differential-expression/edger-basics - edgeR for peak counts
- chip-seq/differential-binding - DNA-protein analogue
<!-- END FILE: clip-seq/differential-clip/SKILL.md -->

## 子目录：clip-seq/m6a-clip

<!-- BEGIN FILE: clip-seq/m6a-clip/SKILL.md -->
---
name: bio-clip-seq-m6a-clip
description: Map N6-methyladenosine (m6A) RNA modifications at single-nucleotide resolution using miCLIP (Linder 2015), miCLIP2 + m6Aboost machine learning (Kortel 2021), GLORI (Liu 2023, antibody-free chemical conversion), DART-seq (Meyer 2019, APOBEC1-YTH fusion), m6Anet (nanopore direct RNA), or MeRIP-seq with calibration. Use when distinguishing antibody-based from antibody-free m6A detection methods, applying the DRACH motif constraint, reconciling cross-method disagreements (DART 44% in DRACH vs GLORI), or detecting m6Am at the cap.
tool_type: mixed
primary_tool: miCLIP2
---

## Version Compatibility

Reference examples tested with: miCLIP2 pipeline (Kortel 2021), m6Aboost 1.0+, GLORI-tools (Liu 2023), Bullseye 1.0+, m6Anet 2.1+, EpiNano 1.2+, MeRIPSeq tools (exomePeak2 1.16+), nanocompore 1.0+, samtools 1.19+, bedtools 2.31+, R 4.3+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed package and adapt the example to match the actual API rather than retrying.

# m6A CLIP (N6-Methyladenosine Profiling)

**"Map m6A modifications at single-nucleotide resolution"** -> Profile m6A on RNA using one of three orthogonal approaches: antibody-based UV-CL (miCLIP/miCLIP2), antibody-free chemical conversion (GLORI), or enzyme-fusion editing (DART-seq with APOBEC1-YTH). Nanopore direct RNA (m6Anet, nanocompore, EpiNano) provides a fourth modality. The DRACH consensus motif (D=A/G/U, R=A/G, A=m6A, C=C, H=A/C/U) constrains plausible sites but is not exclusive - only a fraction of DRACH instances are methylated; some m6A sites occur outside DRACH. Cross-method discordance is real: only ~44% of DART-seq C->U mutations fall within DRACH motifs (Guo 2025 reanalysis of the DART-seq data), suggesting many DART sites are not consensus m6A. GLORI is the new (2023) gold standard for stoichiometric single-base m6A.

- CLI (miCLIP2 antibody-based): `iCount` or custom pipeline through truncation + C->T mutation analysis; then m6Aboost ML scoring
- CLI (GLORI antibody-free): `GLORI-tools` Python pipeline; output is per-A m6A fraction (stoichiometric)
- CLI (DART-seq editing): `Bullseye` or `SAILOR` pipeline; identify C->U editing sites; filter by DRACH; cross-check against APOBEC1-only control
- CLI (m6Anet nanopore): `m6anet inference` on nanopolish eventalign output; per-site probability of m6A
- CLI (MeRIP-seq peak calling): `exomePeak2` in R for peak-level m6A from IP+input MeRIP libraries

The m6A field is rapidly evolving (2022-2026); single-base methods (GLORI, m6Anet) have largely replaced antibody-based miCLIP for new studies, but miCLIP2 remains the most common because of its eCLIP-like processing pipeline. Cross-method discordance means high-confidence m6A reporting should require concordance across at least two orthogonal methods.

## Methods Taxonomy

| Method | Detection chemistry | Resolution | Antibody | Stoichiometry | Strength | Fails when |
|--------|---------------------|------------|----------|---------------|----------|------------|
| MeRIP-seq (Dominissini 2012, Meyer 2012) | Anti-m6A IP + RNA-seq | Peak (50-300 nt) | Yes | No | Original m6A method; widely used | Low resolution; cannot distinguish m6A from m6Am |
| miCLIP (Linder 2015) | Anti-m6A + UV-CL + RT mutation | Single-nucleotide (some) | Yes | No | Single-nt subset of m6A peaks | Low yield of single-nt; high false-positive rate |
| miCLIP2 (Kortel 2021) | Anti-m6A + UV-CL + improved library | Single-nucleotide | Yes | No | Higher complexity; ML-classified (m6Aboost) | Antibody specificity remains issue |
| GLORI (Liu 2023) | Glyoxal + nitrite deamination of unmodified A to inosine (reads as G) | Single-nucleotide | No (chemical) | Yes (stoichiometric) | Stoichiometric m6A fraction per site | New; less validated; harsh conversion may damage rare RNAs |
| DART-seq (Meyer 2019) | APOBEC1-YTH fusion edits C adjacent to m6A | Single-nucleotide (offset) | No | No | Antibody-free; in vivo | Only 44% of edits in DRACH motifs; high false positive |
| m6A-CLIP (Ke 2015) | Anti-m6A + UV-CL | Peak | Yes | No | Original UV-CL approach | Predecessor to miCLIP |
| m6Anet (Hendra 2022) | Nanopore direct RNA + neural net | Single-nucleotide (DRACH constraint) | No | Probability | Direct RNA; preserves isoform context | Restricted to DRACH; needs high coverage per site |
| EpiNano (Liu 2019) | Nanopore + SVM on signal features | Single-nucleotide | No | No | Pioneer nanopore m6A | Lower accuracy than m6Anet on benchmark |
| nanocompore (Leger 2021) | Nanopore + statistical test wt vs Mettl3-KO | Single-nucleotide | No | No | Comparative; high specificity | Requires KO control sample |
| DENA (Qin 2022) | Nanopore + neural network | Single-nucleotide | No | No | Single-sample tool | Newer; less validation |
| FTO/ALKBH5-aware methods | Eraser perturbation | Site | No | Indirect | Validates m6A regulation | Indirect |
| MAZTER-seq (Garcia-Campos 2019) | MazF (RNase) cleavage at unmodified ACA | Site (within ACA) | No | No | Antibody-free | Restricted to ACA context (subset of DRACH) |
| REF-seq (Zhang 2019) | MazF endonuclease-cleavage | Site | No | No | Antibody-free | Restricted context |
| m6ACali (Ye 2024) | Calibrates MeRIP | Site | NA | Yes (calibration) | Cross-method calibration | Postprocessing only |

Methodology evolves; verify the latest benchmark publications and reviews. The field is moving toward GLORI as the new gold standard but miCLIP2 remains the most-cited method because of its eCLIP-pipeline compatibility.

## Critical Choice: Antibody-Based vs Antibody-Free

**Antibody-based (MeRIP-seq, miCLIP, miCLIP2, m6A-CLIP):** Anti-m6A antibody (Abcam/Synaptic Systems) immunoprecipitates m6A-bearing RNA. The antibody is the only limitation - false positives from non-specific binding to long structured RNAs (especially poly-A) and false negatives at sites with low m6A stoichiometry. Mettl3 knockout calibration is recommended.

**Antibody-free chemical (GLORI):** Glyoxal + nitrite converts unmodified A to a nucleotide that reads as G; m6A is protected and reads as A. Sites are detected as A->G discrepancies post-conversion. Stoichiometric (the fraction of reads showing A vs G at a position = m6A fraction). Most rigorous but chemistry is harsh - degrades very long RNAs.

**Antibody-free enzymatic (DART-seq, APOBEC1-YTH):** APOBEC1 cytidine deaminase fused to YTH-domain (m6A reader) edits C residues adjacent to m6A. Editing pattern (C->U) marks m6A nearby but not exactly. 44% of DART edits in DRACH; many edits are off-target.

**Antibody-free nanopore (m6Anet, nanocompore, EpiNano):** Direct RNA sequencing detects m6A via current signal perturbation. Preserves isoform context. m6Anet has high AUC on HEK293T and outperforms EpiNano and Tombo on the Hendra 2022 benchmark.

| Goal | Method |
|------|--------|
| Stoichiometric m6A fraction per site | GLORI |
| eCLIP-compatible processing pipeline | miCLIP2 + m6Aboost |
| Isoform-resolved m6A | m6Anet (nanopore) |
| Cell-line comparison (KO available) | nanocompore vs Mettl3-KO |
| High-throughput screening | DART-seq (in vivo, no UV) |
| Initial discovery (low cost) | MeRIP-seq (with calibration) |
| Variants in m6A context | GLORI + variant-effect analysis |
| Combined m6A + 5'-cap m6Am | miCLIP2 (detects both with separate motifs) |

## DRACH Motif Constraint

The DRACH consensus (D=A/G/U, R=A/G, A=m6A, C=C, H=A/C/U) is the dominant motif at m6A sites - 70-90% of high-confidence sites fall in DRACH context. But:
- Some m6A sites occur outside DRACH (~10-20% in calibrated datasets)
- Many DRACH instances are NOT methylated (only a subset)
- Filtering for DRACH-only loses 10-20% of sites; not-filtering inflates false positives

**miCLIP2 + m6Aboost (Kortel 2021)** trained on Mettl3 knockout calibration data to score sites without DRACH filtering. The m6Aboost ML model is the recommended approach when DRACH-blind detection is needed.

**GLORI** does not filter by DRACH; the per-A m6A fraction is reported regardless of context. The non-DRACH GLORI sites (10-20%) include genuine m6A in non-canonical context.

## Cross-Method Discordance

| Comparison | Concordance | Source |
|------------|-------------|--------|
| miCLIP vs miCLIP2 | ~70% | Kortel 2021 |
| miCLIP2 vs GLORI | ~60% (miCLIP2 calls in GLORI) | Liu 2023 |
| GLORI vs MeRIP-seq peaks | ~50% sites in MeRIP peaks | Liu 2023 |
| DART-seq vs GLORI | ~44% of DART edits within DRACH | Guo 2025 |
| m6Anet vs miCLIP2 | ~75% concordance at high-coverage sites | Hendra 2022 |
| Antibody-based methods | High discordance between antibody lots | Practitioner reports |

**Reconciliation strategy:** Use GLORI as the new gold standard (2023+); cross-reference with m6Anet for nanopore isoform context; treat miCLIP2 + m6Aboost as a complementary in vivo perspective; treat DART-seq as a hypothesis-generating method. Three orthogonal methods agreeing on a site = high confidence.

## miCLIP2 Workflow

miCLIP2 (Kortel 2021) is the eCLIP-pipeline-compatible m6A method. It uses anti-m6A antibody + UV-CL + improved library prep that yields substantially higher-complexity libraries from less input than miCLIP.

**Goal:** Produce a high-confidence single-nucleotide m6A site BED from anti-m6A miCLIP2 reads with antibody-false-positive suppression via m6Aboost machine learning.

**Approach:** Run the eCLIP-style preprocessing + STAR + UMI-dedup pipeline, call single-nt CL sites with PureCLIP using SMInput control, then apply m6Aboost (trained on Mettl3-KO calibration data) to discriminate genuine m6A sites from antibody false positives without requiring strict DRACH motif filtering.

```bash
# Step 1: Preprocessing (eCLIP-style - see clip-seq/clip-preprocessing)
umi_tools extract --bc-pattern=NNNNNNNNNN \
    --stdin=R1.fq.gz --read2-in=R2.fq.gz \
    --stdout=R1.umi.fq.gz --read2-out=R2.umi.fq.gz

cutadapt -a AGATCGGAAGAGCACACGTCT -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT \
    -q 6 -m 18 \
    -o R1.trim.fq.gz -p R2.trim.fq.gz \
    R1.umi.fq.gz R2.umi.fq.gz

# Step 2: Alignment (eCLIP-style)
STAR --runMode alignReads --genomeDir STAR_index \
    --readFilesIn R1.trim.fq.gz R2.trim.fq.gz --readFilesCommand zcat \
    --alignEndsType EndToEnd --outFilterMultimapNmax 1 --outFilterMismatchNoverReadLmax 0.04 \
    --outSAMtype BAM SortedByCoordinate

umi_tools dedup --method=unique --paired -I aligned.bam -S dedup.bam

# Step 3: Single-nt CL site detection - PureCLIP or custom
pureclip -i dedup.bam -bai dedup.bam.bai -g genome.fa \
    -ibam sminput.bam -ibai sminput.bam.bai \
    -o miCLIP2_sites.bed -or miCLIP2_regions.bed -nt 8

# Step 4: m6Aboost ML scoring (Kortel 2021)
# Requires: site BED + features (sequence context, C->T rate, truncation position)
# Trained on Mettl3 KO calibration data
# Output: m6A probability score per site
python m6aboost.py \
    --sites miCLIP2_sites.bed \
    --bam dedup.bam \
    --genome genome.fa \
    --output m6Aboost_predictions.bed

# Step 5: Filter at m6Aboost score >= 0.5 (default; tune per study)
awk '$5 >= 0.5' m6Aboost_predictions.bed > m6a_high_confidence.bed
```

## GLORI Workflow (Antibody-Free Stoichiometric)

GLORI (Liu 2023) is the new (2023) gold-standard for stoichiometric m6A. Chemistry: glyoxal + nitrite converts unmodified A; m6A is protected.

```bash
# GLORI-tools pipeline (Liu lab, github). GLORI-tools is a multi-step Python pipeline
# (`run_GLORI.py` is the typical orchestrator); the conceptual flow below is illustrative --
# verify the exact CLI against the GLORI-tools repo before scripting.
# 1. Pre-conversion sequencing (control)
# 2. Post-conversion sequencing (treated)
# 3. GLORI-tools computes per-A m6A fraction

python run_GLORI.py \
    --input pre_conversion.bam \
    --treated post_conversion.bam \
    --reference genome.fa \
    --output glori_sites.tsv

# Output columns: chr, pos, strand, m6A_fraction, coverage, p_value
# m6A_fraction: 0.0 = unmodified; 1.0 = fully methylated
# Filter at coverage >= 20 and m6A_fraction >= 0.1
awk 'NR>1 && $5 >= 20 && $4 >= 0.1' glori_sites.tsv > glori_high_confidence.tsv
```

## DART-seq Workflow (Editing-Based)

DART-seq (Meyer 2019) expresses APOBEC1-YTH fusion in cells; the YTH domain binds m6A, APOBEC1 edits nearby Cs.

```bash
# Bullseye pipeline (Meyer lab github)
# Requires APOBEC1-only (no YTH) control to subtract off-target editing
Bullseye \
    --ip dart_sample.bam \
    --control apobec1_only.bam \
    --reference genome.fa \
    --output dart_sites.bed

# Filter for DRACH motif overlap (44% of DART sites are in DRACH)
# Sites outside DRACH may be off-target editing
bedtools intersect -wa -u -s -a dart_sites.bed -b drach_motifs.bed > dart_drach_sites.bed
```

## m6Anet Workflow (Nanopore)

m6Anet (Hendra 2022) is the leading nanopore direct-RNA m6A detector. Uses signal-level features in a multiple-instance learning framework.

```bash
# Step 1: nanopolish eventalign on raw nanopore signal
# (assumes basecalled FASTQ, aligned BAM, raw FAST5/POD5)
nanopolish eventalign \
    --reads basecalled.fastq \
    --bam aligned.bam \
    --genome transcriptome.fa \
    --scale-events --signal-index --samples \
    > eventalign.tsv

# Step 2: m6Anet feature extraction
m6anet dataprep \
    --eventalign eventalign.tsv \
    --out_dir m6anet_features \
    --n_processes 8

# Step 3: m6Anet inference
m6anet inference \
    --input_dir m6anet_features \
    --out_dir m6anet_out \
    --pretrained_model HEK293T_RNA002

# Output: per-site probability of m6A
# Filter at probability_modified >= 0.9 (high confidence)
awk -F'\t' 'NR>1 && $5 >= 0.9' m6anet_out/data.indiv_proba.csv > m6Anet_high.tsv
```

## Per-Method Failure Modes

### miCLIP / miCLIP2 -- Antibody specificity

**Trigger:** Antibody lot variation; off-target binding to structured non-methylated RNAs.

**Mechanism:** Anti-m6A antibody (Abcam, Synaptic Systems) has variable specificity. Long structured RNAs (especially poly-A regions, snRNAs) capture non-specifically. False-positive rate without Mettl3-KO calibration is 30-50%.

**Symptom:** miCLIP sites overlap with snRNAs and long ncRNAs at unexpected rates; m6Aboost predicts < 30% of sites are true m6A.

**Fix:** Always include Mettl3-KO calibration (m6Aboost was trained on this). Apply m6Aboost ML; do not just filter by DRACH. Or switch to antibody-free GLORI.

### GLORI -- RNA degradation

**Trigger:** GLORI on long RNAs (> 5 kb); high glyoxal+nitrite concentration.

**Mechanism:** Harsh chemistry damages long RNAs; coverage at long transcripts drops 50-80% post-conversion.

**Symptom:** Long transcripts (e.g., Titin) have poor coverage post-GLORI; m6A sites in coding regions of long mRNAs under-called.

**Fix:** Use shorter conversion times for long-RNA studies (4 h vs 24 h); accept reduced power on long transcripts; cross-reference with miCLIP2 for long-RNA m6A.

### DART-seq -- Off-target editing

**Trigger:** APOBEC1-YTH expressed in cells; no APOBEC1-only control.

**Mechanism:** APOBEC1 has intrinsic C->U editing activity independent of YTH-m6A binding. Without APOBEC1-only control, 30-50% of edits are off-target.

**Symptom:** Many DART edits in non-DRACH context (~44% in DRACH); GO term enrichment of edited genes is non-specific.

**Fix:** Always run APOBEC1-only control in parallel; subtract its edits. Filter for DRACH motif overlap when reporting. Cross-validate with miCLIP2 or GLORI.

### m6Anet -- Coverage requirement

**Trigger:** Nanopore direct RNA on a low-input sample; per-site coverage < 20 reads.

**Mechanism:** m6Anet's multiple-instance learning needs >= 20 reads per DRACH position for stable probability estimate.

**Symptom:** Many "not enough coverage" sites in m6Anet output; gene-level coverage uneven.

**Fix:** Increase nanopore flowcell yield; pool replicates; restrict analysis to high-expression transcripts (TPM >= 5).

### MeRIP-seq -- Peak-level resolution

**Trigger:** MeRIP-seq on antibody-based platforms; peak width 100-300 nt.

**Mechanism:** MeRIP fragments are 100-300 nt; the peak captures a region containing m6A but cannot pinpoint the exact A.

**Symptom:** Peak BED width > 100 nt; downstream single-nt analysis impossible.

**Fix:** Combine MeRIP-seq with single-nt method (GLORI, miCLIP2). Or use m6ACali (Ye 2024) for cross-method calibration.

### DRACH-only filter -- Misses non-canonical m6A

**Trigger:** Filtered miCLIP2 / DART sites to DRACH-only.

**Mechanism:** 10-20% of validated m6A sites are outside DRACH context.

**Symptom:** Lost some validated sites; published m6A list shorter than expected.

**Fix:** Use m6Aboost (DRACH-blind ML) or GLORI (DRACH-blind chemical). Report both DRACH-filtered and unfiltered sets.

### Cross-method discordance frustration

**Trigger:** Three methods produce three different m6A site lists; user wants ONE truth.

**Mechanism:** Methods have different chemistries, sensitivities, and biases. They are not interchangeable. Discordance is real biology + technical.

**Symptom:** Two papers on the same RNA report different m6A sites.

**Fix:** Triangulate. Report (a) high-confidence sites from any single rigorous method (GLORI preferred); (b) consensus sites across 2+ methods. Acknowledge method limitations.

## Decision Tree by Use Case

| Scenario | Method | Why |
|----------|--------|-----|
| New 2024+ study, gold-standard single-base | GLORI | Stoichiometric, antibody-free |
| eCLIP-pipeline-compatible processing | miCLIP2 + m6Aboost | Uses eCLIP infrastructure |
| Isoform-resolved m6A | m6Anet (nanopore) | Long reads preserve isoforms |
| Mettl3 KO calibration available | miCLIP2 + m6Aboost; OR nanocompore | KO is the m6A negative control |
| In vivo, no UV | DART-seq | No UV CL needed |
| Initial discovery (low cost) | MeRIP-seq + exomePeak2 + m6ACali | Cheapest |
| Long RNAs (> 5 kb) | miCLIP2 or m6Anet (not GLORI) | GLORI degrades long RNAs |
| Variant in m6A context | GLORI single-base + variant-effect | Stoichiometric reveals dosage |
| m6Am at 5' cap | miCLIP2 (distinguishes via context) | The 5'-cap-adjacent A |
| Bacterial m6A | Custom methods | Mammalian DRACH irrelevant |
| Time-course m6A dynamics | GLORI per time point | Stoichiometric quantitation |
| Cross-species m6A | Use method validated in that species | Generalization not assumed |

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| miCLIP2 calls site; GLORI does not | Antibody false positive; or m6A fraction low | Trust GLORI for stoichiometry; flag miCLIP2 site for re-validation |
| GLORI calls site; miCLIP2 does not | Antibody false negative (saturation); or non-DRACH | Trust GLORI; check DRACH context of miCLIP2 site |
| DART edits not in DRACH | Off-target APOBEC1 editing | Subtract APOBEC1-only control; filter for DRACH |
| m6Anet calls site; miCLIP2 does not | Nanopore signal-specific detection; complementary | Cross-validate with GLORI; nanopore is orthogonal |
| MeRIP peak but no single-base call within | Peak captures multiple low-stoichiometry sites OR antibody non-specific | Use single-base method for confirmation |
| Discordance between antibody lots | Specificity variation | Use ENCODE-validated antibody; document lot |
| Cross-species method comparison | Method validated only in HEK293 / mouse | Re-validate before applying |
| Time-course shows decrease, methods disagree on magnitude | Stoichiometric (GLORI) vs fraction-based (miCLIP) | GLORI is quantitative; miCLIP is binary call |

**Operational rule for high-confidence m6A reporting:** (a) Use GLORI for stoichiometric single-base sites where chemistry permits; (b) Use miCLIP2 + m6Aboost where eCLIP-pipeline compatibility is required; (c) Use m6Anet for isoform-resolved or long RNAs; (d) Require concordance across at least two orthogonal methods for any m6A site claimed in publication.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| miCLIP2 sites > 100k - more than realistic m6A count | No m6Aboost ML scoring | Apply m6Aboost; expect 10-50k high-confidence |
| GLORI coverage uneven across transcripts | Glyoxal harshness on long RNAs | Shorter conversion; or use other methods for long RNAs |
| DART edits everywhere | No APOBEC1-only subtraction | Add APOBEC1-only control |
| m6Anet returns "no sites" | Coverage < 20 per DRACH | Pool replicates; restrict to high-expression transcripts |
| 10-20% sites outside DRACH | Real biology + some false positives | Report DRACH and non-DRACH separately |
| MeRIP peaks > 200 nt wide | Method resolution | Use single-base method for single-nt sites |
| Different methods give different sites | Method-specific biases | Triangulate; cross-validate |
| Antibody lot variation in miCLIP | Specificity drift | Document lot; use Mettl3-KO calibration |
| m6Am detection failing in miCLIP2 | Failed at 5'-cap | Check 5'-cap adjacent context filter |
| Cross-method calibration confusing | m6ACali heuristic | Apply pre-publication; verify with m6Aboost |

## References

- Dominissini D et al 2012 Nature 485:201 (MeRIP-seq)
- Meyer KD et al 2012 Cell 149:1635 (MeRIP-seq concurrent)
- Linder B et al 2015 Nat Methods 12:767 (miCLIP)
- Ke S et al 2015 Genes Dev 29:2037 (m6A-CLIP)
- Kortel N et al 2021 Nucleic Acids Res 49:e92 (miCLIP2 + m6Aboost)
- Liu C et al 2023 Nat Biotechnol 41:355 (GLORI)
- Meyer KD 2019 Nat Methods 16:1275 (DART-seq)
- Guo W et al 2025 Mol Cell 85:1233 (single-molecule m6A; DART-seq DRACH reanalysis, 44% within DRACH)
- Hendra C et al 2022 Nat Methods 19:1590 (m6Anet)
- Liu H et al 2019 Nat Commun 10:4079 (EpiNano)
- Leger A et al 2021 Nat Commun 12:7198 (nanocompore)
- Garcia-Campos MA et al 2019 Cell 178:731 (MAZTER-seq)
- Qin H et al 2022 Genome Biol 23:25 (DENA)
- Zhang Z et al 2019 Sci Adv 5:eaax0250 (m6A-REF-seq)
- Ye H et al 2024 Nucleic Acids Res 52:4830 (m6ACali, MeRIP-seq calibration)

## Related Skills

- clip-seq/clip-preprocessing - miCLIP2 uses eCLIP-style preprocessing
- clip-seq/clip-alignment - miCLIP2 uses eCLIP-style alignment
- clip-seq/crosslink-site-detection - miCLIP2 single-nt CL detection
- clip-seq/clip-peak-calling - MeRIP-seq exomePeak2 peak calling
- clip-seq/stamp-antibody-free - STAMP / DART-seq antibody-free approach
- long-read-sequencing/nanopore-methylation - Native nanopore m6A
- long-read-sequencing/basecalling - dRNA-seq basecalling
- epitranscriptomics/m6a-peak-calling - MeRIP-specific peak calling
- epitranscriptomics/m6a-differential - Differential m6A
- epitranscriptomics/m6anet-analysis - Nanopore m6Anet workflow
<!-- END FILE: clip-seq/m6a-clip/SKILL.md -->

## 子目录：clip-seq/stamp-antibody-free

<!-- BEGIN FILE: clip-seq/stamp-antibody-free/SKILL.md -->
---
name: bio-clip-seq-stamp-antibody-free
description: Profiles RNA-binding protein targets without antibody or UV crosslinking using STAMP (APOBEC1-RBP fusion, C-to-U editing), scSTAMP (single-cell), TRIBE/HyperTRIBE (ADAR-RBP, A-to-I editing), DART-seq (APOBEC1-YTH for m6A), or Bullseye/SAILOR edit-site detection pipelines. Use when antibody is unavailable or specificity is doubtful, when single-cell RBP profiling is needed (scSTAMP), or when in vivo RBP profiling without UV is preferred.
tool_type: mixed
primary_tool: STAMP
---

## Version Compatibility

Reference examples tested with: STAMP / scSTAMP (Brannan 2021 Yeo lab github), Bullseye 1.0+, SAILOR 1.1+, samtools 1.19+, REDItools2 1.3+, JACUSA2 2.0+, scanpy 1.10+, anndata 0.10+, pysam 0.22+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws unexpected errors, introspect the installed package and adapt the example to match the actual CLI rather than retrying.

# STAMP / Antibody-Free RBP Profiling

**"Profile RBP-RNA targets without UV crosslinking or immunoprecipitation"** -> Express a fusion of the RBP-of-interest with a deaminase (APOBEC1 for STAMP, ADAR for TRIBE) in cells; the deaminase edits RNA nucleotides adjacent to where the RBP binds, producing a C-to-U (STAMP) or A-to-I (TRIBE, read as A-to-G) editing signature in standard RNA-seq. The targets are recovered computationally from the editing pattern. Three properties make this approach valuable: (a) no UV crosslinking required (works in tissue/in vivo); (b) no IP step (no antibody needed - the RBP itself targets the deaminase); (c) compatible with single-cell readout because the editing signal exists in standard scRNA-seq (scSTAMP, scTRIBE). Trade-off: editing is offset from the binding site (typically 0-50 nt away); resolution is approximate; off-target editing from deaminase alone must be subtracted.

- CLI (STAMP, bulk): standard RNA-seq pipeline + Bullseye or SAILOR for C-to-U edit detection vs APOBEC1-only control
- CLI (TRIBE, bulk): standard RNA-seq + REDItools2 or JACUSA2 for A-to-I edit detection vs ADAR-only control
- CLI (DART-seq for m6A): same as STAMP, with APOBEC1-YTH fusion (YTH is the m6A reader)
- Python (scSTAMP single-cell): 10x Genomics or Smart-seq2 pipeline + custom editing-rate quantification per cell + per-cell binding-target inference
- CLI (general edit-site detection): `JACUSA2 call-2 -r ref.fa -p 8 -F 1024 -A,B treated.bam,control.bam -t pileup.tsv` then filter for C-to-U or A-to-I

STAMP (Brannan 2021) is the canonical antibody-free RBP profiling method. TRIBE (McMahon 2016) and HyperTRIBE (Xu 2018) are earlier ADAR-based variants. DART-seq (Meyer 2019) is the m6A-specific application using YTH-fused APOBEC1. scSTAMP (single-cell readout) is part of the same Brannan 2021 method.

## Methods Taxonomy

| Method | Deaminase | Edit signature | Cells supported | Single-cell | Strength | Fails when |
|--------|-----------|----------------|-----------------|-------------|----------|------------|
| STAMP (Brannan 2021) | APOBEC1 | C->U in mRNA (reads as C->T) | Any | Yes (scSTAMP) | Antibody-free; no UV; in vivo | APOBEC1 also edits ssDNA off-target; saturated edits at high APOBEC1 expression |
| scSTAMP (Brannan 2021) | APOBEC1 | C->U per cell | Single cell (10x or Smart-seq2) | Yes (native) | Per-cell RBP profiling | Coverage per cell limits sensitivity; ~25% of cytosines accessible per transcript |
| TRIBE (McMahon 2016) | ADAR catalytic domain | A->I (reads as A->G in cDNA) | Drosophila standard; mammalian works | Yes (scTRIBE) | First antibody-free | Edits restricted to certain ADAR consensus; lower edit rate than HyperTRIBE |
| HyperTRIBE (Xu 2018) | ADAR E488Q hyperactive mutant | A->I in much wider context | Drosophila / mammalian | Yes | Higher edit rate than original TRIBE | Hyperactive may edit off-target; needs ADAR-only control |
| DART-seq (Meyer 2019) | APOBEC1-YTH | C->U near m6A | Any | Yes (scDART) | m6A reader profiling | Indirect (edits near m6A, not at RBP binding sites) |
| Bullseye | NA (analysis tool) | NA | Any | Yes | STAMP / DART analysis | Just an analysis pipeline |
| SAILOR | NA (analysis tool) | NA | Any | Yes | RNA editing analysis | Just an analysis pipeline |
| REDItools2 | NA (analysis tool) | NA | Any | NA | Generic RNA editing | Generic; not RBP-specific |
| JACUSA2 (Piechotta 2022 Genome Biol 23:115) | NA (analysis tool) | NA | Any | NA | Multi-sample edit-site detection | Generic; not RBP-specific |
| ADAR-CLIP | NA - this is regular ADAR CLIP | NA | NA | NA | CLIP for ADAR | Not an antibody-free method; just a different CLIP target |

Methodology evolves; the Brannan lab / Yeo lab 2021 paper is canonical. Verify deaminase fusion expression level (low expression for specificity; saturation degrades specificity).

## STAMP vs m6A-Specific Methods

For m6A profiling specifically, antibody-free choices include:
- **DART-seq (APOBEC1-YTH fusion):** This skill covers the methodology, but for m6A detection see clip-seq/m6a-clip. Only ~44% of DART edits fall within DRACH motifs (Guo 2025); strong off-target component.
- **GLORI (Liu 2023):** Antibody-free, chemical, stoichiometric single-base m6A; this is the new (2023) gold standard for m6A. See clip-seq/m6a-clip.
- **m6Anet (Hendra 2022):** Nanopore direct RNA m6A; high AUC on HEK293T.

If the use case is m6A profiling, the m6a-clip skill is the canonical reference; this skill (stamp-antibody-free) focuses on the broader RBP-editing-fusion paradigm where the target is not m6A but the RBP's RNA targets.

## Critical Choice: STAMP (APOBEC1) vs TRIBE (ADAR)

| Property | STAMP | TRIBE |
|----------|-------|-------|
| Deaminase | APOBEC1 (cytidine -> uridine) | ADAR (adenosine -> inosine) |
| Edit signature | C->U (reads as C->T) | A->I (reads as A->G) |
| ssRNA preference | Yes (APOBEC1 acts on ssRNA + ssDNA) | No (ADAR acts on dsRNA stems by default; ADAR2cd in TRIBE relaxes this) |
| Edit clusters per target | 10-1000 | ~5-50 (lower; HyperTRIBE higher) |
| Off-target | APOBEC1 alone has detectable C->U on ssDNA + RNA | ADAR has weak intrinsic A->I |
| Spatial offset from RBP binding | 0-50 nt | 0-30 nt |
| Cell line tested | HEK293, K562, mouse tissue | Drosophila (original), mouse, human |
| Single-cell | scSTAMP (Brannan 2021) | scTRIBE |
| Compatible methods | C->U is rare in mRNA; signal is clean | A->I is common at ALU repeats; baseline ADAR editing competes |
| Cytosine accessibility | ~25-35% of mRNA bases are C; APOBEC1 needs ssRNA | All A residues are potential ADAR targets |

Both work; STAMP has more clusters per target (advantage for low-coverage scenarios) and cleaner background (C->U is rare in mRNA). TRIBE has more flexibility (ADAR variants tunable) and lower off-target. Practical choice often comes down to lab familiarity.

## scSTAMP / scTRIBE Single-Cell Workflow

The defining advantage of antibody-free RBP profiling is compatibility with single-cell readout. scSTAMP processes 10x Genomics or Smart-seq2 libraries.

```bash
# Standard 10x cellranger pipeline produces BAM with per-cell barcodes
cellranger count \
    --id=scstamp_sample \
    --transcriptome=refdata-gex-GRCh38 \
    --fastqs=fastq_dir \
    --localcores=16 --localmem=64

# scSTAMP analysis (Yeo lab github)
# Quantify per-cell C->U editing
python scstamp_analysis.py \
    --bam scstamp_sample/outs/possorted_genome_bam.bam \
    --barcodes scstamp_sample/outs/filtered_feature_bc_matrix/barcodes.tsv.gz \
    --control apobec1_only_sample/outs/possorted_genome_bam.bam \
    --output per_cell_edits.h5
```

Per-cell edit-rate matrix can be integrated with standard scRNA-seq clustering. The per-cell binding profile is reconstructed from cells with sufficient coverage (>= 10000 unique reads typically).

## Editing-Site Detection Pipelines

**Goal:** Recover specific (not background) RBP-fusion-induced editing sites from RNA-seq libraries by subtracting the deaminase-only control.

**Approach:** Process fusion-sample BAM and deaminase-only-control BAM in parallel; use Bullseye (STAMP/DART), SAILOR (Yeo), or JACUSA2 (general) to call C-to-U (STAMP/DART) or A-to-I (TRIBE/HyperTRIBE) edit sites at edit rate >= 0.1 and coverage >= 10, requiring fusion-vs-control edit ratio > 3 as the specificity threshold.

**Bullseye** (Meyer lab DART-seq pipeline) is a multi-script Perl pipeline (`parseBAM.pl`, `summarize_sites.pl`, `find_edit_site.pl`) rather than a single binary -- the conceptual flow is shown below; consult the Bullseye repo for the exact per-script invocations.

```bash
# Bullseye -- conceptual STAMP workflow (multi-step Perl scripts; verify against repo)
perl parseBAM.pl --input stamp_sample.bam --output stamp.parsed.tsv
perl parseBAM.pl --input apobec1_only.bam --output control.parsed.tsv
perl summarize_sites.pl --in stamp.parsed.tsv > stamp.summary.tsv
perl summarize_sites.pl --in control.parsed.tsv > control.summary.tsv
perl find_edit_site.pl --ip stamp.summary.tsv --ctrl control.summary.tsv \
    --edit_type c2t --threshold 0.1 --min_coverage 10 --out stamp_edits.bed
```

**SAILOR** (Yeo lab) is a Snakemake-based pipeline, not a single CLI binary -- launch via the SAILOR Snakefile after editing the config (`config.yaml`) for input BAMs, background BAM, and reference FASTA.

```bash
# SAILOR -- conceptual; SAILOR ships as a Snakemake workflow.
# Configure inputs in the SAILOR Snakemake config.yaml, then run:
snakemake -s SAILOR.smk --configfile config.yaml --cores 8
```

**JACUSA2** is a general-purpose RNA editing pipeline, distributed as a Java jar.

```bash
# JACUSA2 multi-sample edit-site detection (BAM inputs are POSITIONAL; -r is output, -R is reference)
java -jar JACUSA2.jar call-2 \
    -R genome.fa \
    -p 8 \
    -F 1024 \
    -r jacusa_edits.tsv \
    stamp1.bam,stamp2.bam control1.bam,control2.bam

# Post-filter for C->U (STAMP) at edit rate >= 0.1
awk '$5 == "C" && $9 ~ /U/ && $11 >= 0.1' jacusa_edits.tsv > stamp_edits_filtered.tsv
```

## Per-Method Failure Modes

### STAMP -- APOBEC1 over-expression saturation

**Trigger:** Strong APOBEC1-RBP expression (>>10x endogenous).

**Mechanism:** At high APOBEC1 expression, the deaminase saturates editing - every accessible C in mRNA is edited, regardless of RBP binding.

**Symptom:** Edit count per gene >> expected; non-specific editing across mRNAs; APOBEC1-only control has nearly as many edits as the fusion.

**Fix:** Titrate fusion expression with inducible promoter; aim for low-to-moderate expression giving clean fusion-specific edits. Yeo lab convention: doxycycline-inducible with mid-range dox dose. Compare edits in fusion vs APOBEC1-only; require fusion edits / APOBEC1-only edits > 3.

### STAMP -- APOBEC1 off-target on ssDNA

**Trigger:** APOBEC1 expressed in DNA-replicating cells.

**Mechanism:** APOBEC1 has intrinsic ssDNA editing activity; some "C->U" calls are actually genomic ssDNA edits read through transcription.

**Symptom:** Edits cluster at replication-fork regions or LINE-1 elements; non-specific genome-wide.

**Fix:** Bullseye filters genomic SNVs vs RNA edits via strand information; verify mismatch is C->U on the transcribed strand, not the genomic C->T.

### TRIBE -- Editing at ALU repeats

**Trigger:** TRIBE in mammalian cells; many edits at ALU sequences.

**Mechanism:** ADAR has baseline activity at ALU dsRNA structures; this is NOT TRIBE-specific signal. ALU edits dominate the apparent target list.

**Symptom:** Top edited regions are all ALU repeats; target list looks generic.

**Fix:** Subtract ADAR-only control or wild-type ADAR baseline; filter out ALU-overlapping edits unless RBP is known to bind repeats.

### DART-seq -- Spatial offset from m6A

**Trigger:** DART-seq applied with expectation of single-base m6A resolution.

**Mechanism:** APOBEC1-YTH edits Cs 0-50 nt from the YTH-bound m6A site. The exact m6A position is not the edit position.

**Symptom:** DART edits scattered around DRACH motifs; only ~44% of edits within DRACH.

**Fix:** Treat DART edits as "near m6A"; cross-reference with single-base m6A methods (GLORI, miCLIP2). DART is hypothesis-generating, not precise localization.

### scSTAMP -- Coverage limitation per cell

**Trigger:** scSTAMP on 10x library; per-cell coverage limits target detection.

**Mechanism:** Single cells have ~5000-50000 mRNA molecules; editing-rate quantification at any single position needs >= 10 reads. Most positions have 0-3 reads per cell.

**Symptom:** Per-cell binding-target list is sparse; many cells have 0 detected targets.

**Fix:** Aggregate cells into pseudo-bulk by cluster/cell-type; quantify editing at pseudobulk level; or use ultra-deep Smart-seq2 (~1M reads/cell) instead of 10x for higher per-cell coverage.

### No control subtraction

**Trigger:** STAMP/DART/TRIBE run without deaminase-only control.

**Mechanism:** Deaminases have intrinsic baseline editing (APOBEC1 ~3-5% C->U; ADAR ~5-10% A->I at ALUs). Without control, all edits look like signal.

**Symptom:** Edit count enormous; target list non-specific.

**Fix:** Always run deaminase-only (APOBEC1 or ADAR catalytic domain) control in parallel. Bullseye / SAILOR / JACUSA all support control subtraction.

### Strand-specific edit interpretation

**Trigger:** Generic variant caller used instead of edit-aware tool.

**Mechanism:** Variant callers report any C->T mismatch; without strand information it is not possible to distinguish C->U (STAMP signal on transcribed strand) from G->A (the reverse complement of C->T on the genome strand from anti-sense reads).

**Symptom:** Edit count inflated 2x; signal not stranded.

**Fix:** Use editing-specific tool (Bullseye, SAILOR, JACUSA2) that respects strand. Or filter for proper strand: C->U on +sense and G->A on -sense.

## Decision Tree by Use Case

| Scenario | Method | Why |
|----------|--------|-----|
| Antibody for RBP doesn't exist | STAMP or TRIBE | The original use case |
| RBP in tissue / in vivo (no UV possible) | STAMP / TRIBE | No CL needed |
| Single-cell RBP profiling | scSTAMP or scTRIBE | The only practical option |
| m6A reader profiling (YTHDF) | DART-seq (APOBEC1-YTH) | Specific reader fusion |
| Drosophila RBP | TRIBE (original development) | Most validated in Drosophila |
| Mammalian RBP | STAMP (more validated in mammalian) | Yeo lab benchmarks |
| Need precise binding site | Use CLIP / eCLIP not STAMP/TRIBE | Editing is offset from binding |
| Repeat-binding RBP | CLIP + CLAM, not TRIBE | ADAR baseline at ALUs swamps TRIBE |
| Comparison across methods | STAMP + classic eCLIP both | Triangulation increases confidence |
| Low input cell numbers (< 50k) | scSTAMP | Compatible with sparse libraries |
| Time-course binding dynamics | STAMP with inducible expression | Live-cell editing accumulates |
| Cross-link sensitive RBP | STAMP / TRIBE (no UV) | Some RBPs degrade with UV |

## Reconciliation: STAMP vs CLIP

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| STAMP finds targets eCLIP missed | Targets that crosslink poorly; or low-abundance | Validate orthogonally; STAMP often more sensitive for low-abundance targets |
| eCLIP finds targets STAMP missed | RBP-RNA contact too far from accessible C; or APOBEC1 saturated | Check fusion expression level; ssRNA accessibility |
| STAMP edits clustered; eCLIP peaks broader | Spatial offset of editing from binding | Both correct; report at appropriate resolution |
| STAMP top targets generic mRNAs | Saturated APOBEC1; or no control subtraction | Titrate fusion expression; verify APOBEC1-only control |
| TRIBE editing dominated by ALUs | ADAR baseline activity | Subtract ADAR-only; filter ALU repeats |
| Discordant target lists across labs for same RBP | Fusion expression varies; control differs | Standardize protocols; cross-validate |
| scSTAMP pseudobulk = bulk STAMP | Cell aggregation correct | Trust both for low-coverage targets |
| scSTAMP per-cell sparse | Coverage limitation | Pseudobulk by cluster; or use Smart-seq2 |

**Operational rule:** STAMP/TRIBE for hypothesis-generation, antibody-free profiling, or single-cell. CLIP/eCLIP for high-resolution validation. Best paper figure: STAMP + eCLIP concordance for top targets.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Edit count enormous | No control subtraction | Add APOBEC1-only / ADAR-only control |
| Edits in DNA / off-target | APOBEC1 ssDNA activity | Filter genomic SNVs; trust strand-specific RNA edits |
| Saturated editing on every gene | High fusion expression | Titrate down; use inducible promoter |
| TRIBE all edits at ALUs | ADAR baseline | Subtract ADAR-only; filter ALU |
| DART edits not at m6A | Spatial offset (0-50 nt) | Expected; cross-reference single-base m6A |
| scSTAMP per-cell sparse | 10x coverage limit | Pseudobulk by cluster; Smart-seq2 alternative |
| Generic variant caller | No strand awareness | Use Bullseye / SAILOR / JACUSA |
| Edits in non-edited strand | Anti-sense transcription | Filter by strand-specific mate |
| Same target list as RNA-seq abundance | Saturated APOBEC1 | Reduce fusion expression |
| Reproducibility issue across labs | Fusion construct differs | Standardize promoter, tag position, deaminase variant |

## References

- Brannan KW et al 2021 Nat Methods 18:507 (STAMP + scSTAMP single-cell, APOBEC1-RBP fusion)
- McMahon AC et al 2016 Cell 165:742 (TRIBE original, Drosophila)
- Xu W, Rahman R, Rosbash M 2018 RNA 24:173 (HyperTRIBE)
- Meyer KD 2019 Nat Methods 16:1275 (DART-seq, APOBEC1-YTH)
- Guo W et al 2025 Mol Cell 85:1233 (DART-seq DRACH reanalysis, 44% within DRACH)
- (SAILOR: pipeline by Yeo lab; documented at github.com/YeoLab/SAILOR -- specific peer-reviewed citation has not been confirmed; consult current literature.)
- Piechotta M et al 2017 BMC Bioinformatics 18:7 (JACUSA1).
- Piechotta M et al 2022 Genome Biol 23:115 (JACUSA2 -- the multi-sample call-2 mode used above).
- Picardi E & Pesole G 2013 Bioinformatics 29:1813 (REDItools)
- Tegowski M et al 2022 Mol Cell 82:868 (scDART single-cell DART-seq)

## Related Skills

- clip-seq/m6a-clip - DART-seq is part of the m6A toolkit
- clip-seq/clip-deep-learning - Computational target prediction
- clip-seq/ago-clip-mirna-targets - AGO-CLIP for comparison
- single-cell/preprocessing - scSTAMP downstream
- single-cell/clustering - scSTAMP per-cluster pseudobulk
- single-cell/markers-annotation - Cell-type-specific targets
- methylation-analysis/methylation-calling - Editing as related to methylation
- epitranscriptomics/m6anet-analysis - Nanopore m6A alternative to DART
<!-- END FILE: clip-seq/stamp-antibody-free/SKILL.md -->

<!-- END CATEGORY: clip-seq -->

